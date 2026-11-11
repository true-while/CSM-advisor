"""Search the bundled Microsoft Learn catalog (ms-learn-catalog.json).

Usage:
  python scripts/search_catalog.py "copilot readiness" "prompt engineering" [--product microsoft-365-copilot]
         [--role administrator] [--level beginner] [--type module|path|course|all] [--limit 8]
  python scripts/search_catalog.py --facets      # list the product / role / level / subject values in the catalog

Prints JSON only. Each result keeps the catalog link, level, duration, and (for modules and paths) the
related learning paths and instructor-led courses. The catalog is a snapshot: report generated_at.
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
    ap.add_argument("--type", default="all", choices=["module", "path", "course", "all"])
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--facets", action="store_true")
    args = ap.parse_args()

    if not CATALOG.exists():
        sys.exit(json.dumps({"error": "ms-learn-catalog.json not found; use web search on learn.microsoft.com instead"}))
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))

    if args.facets:
        out = {"generated_at": cat["generated_at"], "counts": cat["counts"]}
        for field in ("products", "roles", "levels", "subjects"):
            c = Counter(v for kind in ("modules", "paths", "courses") for i in cat[kind] for v in i.get(field, []))
            out[field] = [k for k, _ in c.most_common(60)]
        print(json.dumps(out, indent=1))
        return

    modules = {m["uid"]: m for m in cat["modules"]}
    paths = {p["uid"]: p for p in cat["paths"]}
    courses_by_path = {}
    for c in cat["courses"]:
        for p in c["paths"]:
            courses_by_path.setdefault(p, []).append(c)
    paths_by_module = {}
    for p in cat["paths"]:
        for m in p["modules"]:
            paths_by_module.setdefault(m, []).append(p)

    def course_ref(c):
        return {"code": c["code"], "title": c["title"], "url": c["url"], "hours": c["hours"]}

    def view(kind, item):
        if kind == "course":
            return {"type": "course", "code": item["code"], "title": item["title"], "url": item["url"],
                    "hours": item["hours"], "levels": item["levels"], "roles": item["roles"],
                    "products": item["products"], "summary": item["summary"],
                    "paths": [{"title": paths[p]["title"], "url": paths[p]["url"]} for p in item["paths"] if p in paths]}
        v = {"type": kind, "title": item["title"], "url": item["url"], "levels": item.get("levels"),
             "roles": item.get("roles"), "products": item.get("products"),
             "minutes": item.get("minutes"), "summary": item.get("summary")}
        if kind == "path":
            v["modules"] = [{"title": modules[m]["title"], "url": modules[m]["url"]} for m in item["modules"] if m in modules]
            v["courses"] = [course_ref(c) for c in courses_by_path.get(item["uid"], [])]
        else:
            parents = paths_by_module.get(item["uid"], [])
            v["in_paths"] = [{"title": p["title"], "url": p["url"]} for p in parents[:3]]
            seen = {}
            for p in parents:
                for c in courses_by_path.get(p["uid"], []):
                    seen[c["uid"]] = c
            v["courses"] = [course_ref(c) for c in list(seen.values())[:3]]
        return v

    pools = {"module": cat["modules"], "path": cat["paths"], "course": cat["courses"]}
    idf = build_idf([i for pool in pools.values() for i in pool])
    kinds = list(pools) if args.type == "all" else [args.type]
    results = []
    for q in args.queries:
        qt = tokens(q)
        scored = []
        for kind in kinds:
            for item in pools[kind]:
                if not matches_filters(item, args):
                    continue
                s = score(item, qt, idf)
                if s > 0:
                    scored.append((s + (0.5 if kind == "path" else 0), kind, item))
        scored.sort(key=lambda x: -x[0])
        results.append({"query": q, "matches": [dict(view(k, i), score=round(s, 1)) for s, k, i in scored[: args.limit]]})

    print(json.dumps({"generated_at": cat["generated_at"], "note": "Snapshot of Microsoft Learn; verify links before sending",
                      "results": results}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
