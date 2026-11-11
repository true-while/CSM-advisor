"""Search the bundled Microsoft Learn catalog (ms-learn-catalog.json) for modules and learning paths.

Usage:
  python scripts/search_catalog.py "copilot readiness" "prompt engineering" [--product microsoft-365-copilot]
         [--role administrator] [--level beginner] [--type module|path|all] [--limit 8]
  python scripts/search_catalog.py --facets      # list the product / role / level / subject values in the catalog

Prints JSON only. Every result carries the catalog link, level and duration; paths list their modules and
modules list the learning paths they belong to. The "debug" object records what was searched (catalog
snapshot date and size, filters, query tokens, candidate counts, top scores) so each step can be logged.
The catalog is a snapshot: always report generated_at.
"""
import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "ms-learn-catalog.json"
STOP = {"a", "an", "and", "the", "of", "to", "for", "in", "on", "with", "how", "use", "using", "microsoft"}


def tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in STOP and len(t) > 1]


def item_tokens(item):
    return (set(tokens(item["title"])), set(tokens(item.get("summary"))),
            set(tokens(" ".join(item.get("products", []) + item.get("subjects", []) + item.get("roles", [])))))


def build_idf(items):
    df = Counter()
    for item in items:
        for group in item_tokens(item):
            df.update(group)
    n = len(items)
    return {t: math.log(1 + n / c) for t, c in df.items()}


def score(item, qtokens, idf):
    title, summary, tags = item_tokens(item)
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
    # reward items that match more of the distinct query words
    return s * (hit / max(1, len(set(qtokens)))) ** 2 if hit else 0.0


def strength(s):
    """Heuristic label only: still check the title and summary against the skill before using a match."""
    return "strong" if s >= 15 else "possible" if s >= 6 else "weak"


def matches_filters(item, args):
    for field, wanted in (("products", args.product), ("roles", args.role), ("levels", args.level)):
        if wanted and not set(wanted) & set(item.get(field, [])):
            return False
    return True


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
    args = ap.parse_args()

    if not CATALOG.exists():
        sys.exit(json.dumps({"error": "ms-learn-catalog.json not found; use web search on learn.microsoft.com instead"}))
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))

    if args.facets:
        out = {"generated_at": cat["generated_at"], "counts": cat["counts"]}
        for field in ("products", "roles", "levels", "subjects"):
            c = Counter(v for kind in ("modules", "paths") for i in cat[kind] for v in i.get(field, []))
            out[field] = [k for k, _ in c.most_common(60)]
        print(json.dumps(out, indent=1))
        return

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
            v["modules"] = [{"title": modules[m]["title"], "url": modules[m]["url"]} for m in item["modules"] if m in modules]
        else:
            v["in_paths"] = [{"title": p["title"], "url": p["url"]} for p in paths_by_module.get(item["uid"], [])[:3]]
        return v

    pools = {"module": cat["modules"], "path": cat["paths"]}
    idf = build_idf([i for pool in pools.values() for i in pool])
    kinds = list(pools) if args.type == "all" else [args.type]
    results, debug_queries = [], []
    for q in args.queries:
        qt = tokens(q)
        scored, considered = [], 0
        for kind in kinds:
            for item in pools[kind]:
                if not matches_filters(item, args):
                    continue
                considered += 1
                s = score(item, qt, idf)
                if s > 0:
                    scored.append((s + (0.5 if kind == "path" else 0), kind, item))
        scored.sort(key=lambda x: -x[0])
        top = scored[: args.limit]
        results.append({"query": q, "matches": [dict(view(k, i), score=round(s, 1), strength=strength(s)) for s, k, i in top]})
        debug_queries.append({"query": q, "tokens": qt, "items_considered": considered, "items_matched": len(scored),
                              "returned": len(top), "top_score": round(top[0][0], 1) if top else None,
                              "strong_matches": sum(1 for s, _, _ in top if strength(s) == "strong")})

    print(json.dumps({
        "generated_at": cat["generated_at"],
        "note": "Snapshot of Microsoft Learn; links come from the catalog",
        "debug": {"catalog_counts": cat["counts"],
                  "filters": {"product": args.product, "role": args.role, "level": args.level,
                              "type": args.type, "limit": args.limit},
                  "queries": debug_queries},
        "results": results}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
