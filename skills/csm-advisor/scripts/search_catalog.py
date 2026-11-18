"""Search the live Microsoft Learn catalog API (the deployed scm-advisor service) for modules and
learning paths. Falls back automatically to the bundled snapshot (ms-learn-catalog.json) if the live
service cannot be reached.

Usage:
  python scripts/search_catalog.py "copilot readiness" "prompt engineering" [--product microsoft-365-copilot]
         [--role administrator] [--level beginner] [--type module|path|all] [--limit 8]
  python scripts/search_catalog.py --facets                 # list product / role / level / subject ids
  python scripts/search_catalog.py --item <uid> [--expand]  # one record; --expand adds its modules/paths

Prints JSON only. Every result carries the catalog link, level and duration; a learning path's "modules"
field lists the uids of the modules it covers. The "debug" object records what was searched (filters,
query tokens, how many results were available, warnings) so each step can be logged. Set CATALOG_API_URL
to point at a different deployment (defaults to https://scm-advisor.azurewebsites.net), and CATALOG_API_KEY
if the deployment requires the x-api-key header.

Instructor-led classes, courses, certifications, exams and applied skills are out of scope for this
skill, so searches and facets are restricted to modules and learning paths only.
"""
import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

API_URL = os.environ.get("CATALOG_API_URL", "https://scm-advisor.azurewebsites.net").rstrip("/")
API_KEY = os.environ.get("CATALOG_API_KEY", "")
TIMEOUT = 20
CATALOG = Path(__file__).resolve().parent.parent / "ms-learn-catalog.json"  # offline fallback snapshot
STOP = {"a", "an", "and", "the", "of", "to", "for", "in", "on", "with", "how", "use", "using", "microsoft"}
TYPE_MAP = {"module": ["module"], "path": ["learningPath"], "all": ["module", "learningPath"]}


def tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in STOP and len(t) > 1]


def clean(s, n=300):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()[:n]


def strength(coverage):
    """Heuristic label only: still check the title and summary against the skill before using a match."""
    return "strong" if coverage >= 0.999 else "possible" if coverage >= 0.5 else "weak"


def bundled_strength(s):
    """Heuristic label for the bundled snapshot's magnitude-based score (different scale from the live API)."""
    return "strong" if s >= 15 else "possible" if s >= 6 else "weak"


# ---------------------------------------------------------------- Live API (primary source)
class ServiceUnreachable(Exception):
    pass


def api_get(path, params=None):
    url = API_URL + path
    if params:
        clean_params = {k: v for k, v in params.items() if v not in (None, [], "")}
        if clean_params:
            url += "?" + urllib.parse.urlencode(clean_params, doseq=True)
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code >= 500:
            raise ServiceUnreachable(f"{API_URL}{path} returned HTTP {e.code}") from e
        raise  # 4xx is a real error (bad query, missing API key, ...), not an outage
    except (urllib.error.URLError, TimeoutError) as e:
        raise ServiceUnreachable(f"could not reach {API_URL}{path}: {e}") from e


def live_view(result, qtokens):
    item = result["item"]
    matched = set(result.get("matched_terms") or [])
    coverage = len(matched & qtokens) / len(qtokens) if qtokens else 0.0
    v = {"type": result["type"], "uid": result["uid"], "title": item.get("title"),
         "url": result.get("link") or item.get("url"), "levels": item.get("levels"),
         "roles": item.get("roles"), "products": item.get("products"),
         "minutes": item.get("duration_in_minutes"), "summary": clean(item.get("summary")),
         "score": result.get("score"), "matched_terms": sorted(matched), "strength": strength(coverage)}
    if result["type"] == "learningPath":
        v["modules"] = item.get("modules", [])
    return v


def live_search(queries, args):
    types = TYPE_MAP[args.type]
    limit = max(1, min(args.limit, 100))
    results, debug_queries = [], []
    for q in queries:
        params = {"q": q, "types": types, "match": "any", "sort": "relevance", "limit": limit,
                  "roles": args.role, "levels": args.level, "products": args.product}
        data = api_get("/search", params)
        qtokens = set(tokens(q))
        matches = [live_view(r, qtokens) for r in data.get("results", [])]
        results.append({"query": q, "matches": matches})
        debug_queries.append({"query": q, "tokens": sorted(qtokens), "items_available": data.get("total"),
                               "returned": len(matches), "warnings": data.get("warnings"),
                               "strong_matches": sum(1 for m in matches if m["strength"] == "strong")})
    meta = api_get("/meta")
    return {
        "source": "live", "service": API_URL, "generated_at": meta.get("file_modified"),
        "note": "Live Microsoft Learn catalog, served by the deployed scm-advisor service",
        "debug": {"filters": {"product": args.product, "role": args.role, "level": args.level,
                               "type": args.type, "limit": limit}, "queries": debug_queries},
        "results": results,
    }


def live_facets():
    taxonomies = api_get("/taxonomies")
    meta = api_get("/meta")
    out = {"source": "live", "service": API_URL, "generated_at": meta.get("file_modified"),
           "counts": meta.get("collections")}
    for field in ("products", "roles", "levels", "subjects"):
        out[field] = [t["id"] for t in taxonomies.get(field, [])]
    return out


def live_item(uid, expand):
    params = {"expand": "true"} if expand else None
    data = api_get(f"/items/{urllib.parse.quote(uid, safe='')}", params)
    return {"source": "live", "service": API_URL, **data}


# ---------------------------------------------------------------- Bundled snapshot (fallback only)
def load_bundled():
    if not CATALOG.exists():
        return None
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def bundled_item_tokens(item):
    return (set(tokens(item["title"])), set(tokens(item.get("summary"))),
            set(tokens(" ".join(item.get("products", []) + item.get("subjects", []) + item.get("roles", [])))))


def bundled_build_idf(items):
    df = Counter()
    for item in items:
        for group in bundled_item_tokens(item):
            df.update(group)
    n = len(items)
    return {t: math.log(1 + n / c) for t, c in df.items()}


def bundled_score(item, qtokens, idf):
    title, summary, tags = bundled_item_tokens(item)
    s, hit = 0.0, 0
    for t in set(qtokens):
        w = idf.get(t, 1.0)
        m = 0.0
        if t in title:
            m += 3 * w
        if t in tags:
            m += 1.5 * w
        if t in summary:
            m += 1 * w
        if m:
            hit += 1
        s += m
    return s * (hit / max(1, len(set(qtokens)))) ** 2 if hit else 0.0


def bundled_matches_filters(item, args):
    for field, wanted in (("products", args.product), ("roles", args.role), ("levels", args.level)):
        if wanted and not set(wanted) & set(item.get(field, [])):
            return False
    return True


def bundled_search(queries, args, cat):
    modules = {m["uid"]: m for m in cat["modules"]}
    paths_by_module = {}
    for p in cat["paths"]:
        for m in p["modules"]:
            paths_by_module.setdefault(m, []).append(p)

    def view(kind, item):
        v = {"type": kind, "title": item["title"], "url": item["url"], "levels": item.get("levels"),
             "roles": item.get("roles"), "products": item.get("products"),
             "minutes": item.get("minutes"), "summary": item.get("summary")}
        if kind == "path":
            v["modules"] = item["modules"]
        else:
            v["in_paths"] = [{"title": p["title"], "url": p["url"]} for p in paths_by_module.get(item["uid"], [])[:3]]
        return v

    pools = {"module": cat["modules"], "path": cat["paths"]}
    idf = bundled_build_idf([i for pool in pools.values() for i in pool])
    kinds = ["module"] if args.type == "module" else ["path"] if args.type == "path" else ["module", "path"]
    results, debug_queries = [], []
    for q in queries:
        qt = tokens(q)
        scored, considered = [], 0
        for kind in kinds:
            for item in pools[kind]:
                if not bundled_matches_filters(item, args):
                    continue
                considered += 1
                s = bundled_score(item, qt, idf)
                if s > 0:
                    scored.append((s + (0.5 if kind == "path" else 0), kind, item))
        scored.sort(key=lambda x: -x[0])
        top = scored[: args.limit]
        results.append({"query": q, "matches": [dict(view(k, i), score=round(s, 1), strength=bundled_strength(s)) for s, k, i in top]})
        debug_queries.append({"query": q, "tokens": qt, "items_considered": considered, "items_matched": len(scored),
                              "returned": len(top), "top_score": round(top[0][0], 1) if top else None})

    return {
        "source": "bundled-snapshot", "generated_at": cat["generated_at"],
        "note": "Live catalog service unreachable; used the bundled snapshot instead",
        "debug": {"catalog_counts": cat["counts"],
                  "filters": {"product": args.product, "role": args.role, "level": args.level,
                              "type": args.type, "limit": args.limit},
                  "queries": debug_queries},
        "results": results,
    }


def bundled_facets(cat):
    out = {"source": "bundled-snapshot", "generated_at": cat["generated_at"], "counts": cat["counts"]}
    for field in ("products", "roles", "levels", "subjects"):
        c = Counter(v for kind in ("modules", "paths") for i in cat[kind] for v in i.get(field, []))
        out[field] = [k for k, _ in c.most_common(60)]
    return out


def bundled_item(uid, expand, cat):
    modules = {m["uid"]: m for m in cat["modules"]}
    paths = {p["uid"]: p for p in cat["paths"]}
    if uid in modules:
        item, kind = modules[uid], "module"
    elif uid in paths:
        item, kind = paths[uid], "path"
    else:
        return {"source": "bundled-snapshot", "error": f"'{uid}' not found in the bundled snapshot"}
    out = {"source": "bundled-snapshot", "generated_at": cat["generated_at"], "type": kind, **item}
    if expand and kind == "path":
        out["modules_expanded"] = [{"uid": m, "title": modules[m]["title"], "url": modules[m]["url"]}
                                    for m in item["modules"] if m in modules]
    if expand and kind == "module":
        out["in_paths"] = [{"uid": p["uid"], "title": p["title"], "url": p["url"]}
                            for p in paths.values() if uid in p.get("modules", [])]
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="*", help="skill phrases to look up")
    ap.add_argument("--product", action="append")
    ap.add_argument("--role", action="append")
    ap.add_argument("--level", action="append")
    ap.add_argument("--type", default="all", choices=["module", "path", "all"])
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--facets", action="store_true")
    ap.add_argument("--item", help="look up one record by its uid instead of searching")
    ap.add_argument("--expand", action="store_true", help="with --item, also list its modules or the paths it belongs to")
    args = ap.parse_args()

    try:
        if args.item:
            out = live_item(args.item, args.expand)
        elif args.facets:
            out = live_facets()
        else:
            out = live_search(args.queries, args)
    except ServiceUnreachable as e:
        cat = load_bundled()
        if cat is None:
            sys.exit(json.dumps({"error": f"live catalog service unreachable ({e}) and ms-learn-catalog.json "
                                           "not found; use web search on learn.microsoft.com instead"}))
        if args.item:
            out = bundled_item(args.item, args.expand, cat)
        elif args.facets:
            out = bundled_facets(cat)
        else:
            out = bundled_search(args.queries, args, cat)
        out["unreachable"] = str(e)

    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
