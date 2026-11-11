"""Download the Microsoft Learn catalog and write a slim copy into the skill folder.

Run: python scripts/build_learn_catalog.py
Output: skills/csm-advisor/ms-learn-catalog.json (bundled in the plugin ZIP, not committed to git)

The full catalog is ~13 MB, but Cowork allows at most 5 MB per companion file, so only the fields
the agent needs are kept. The build fails instead of shipping an empty or truncated catalog.
"""
import datetime
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

URL = "https://learn.microsoft.com/api/catalog/?locale=en-us&type=modules,learningPaths"
OUT = Path(__file__).resolve().parent.parent / "skills" / "csm-advisor" / "ms-learn-catalog.json"
MAX_BYTES = 4_500_000
MIN_MODULES, MIN_PATHS = 1000, 100


def fetch() -> dict:
    last = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(URL, timeout=180) as r:
                return json.load(r)
        except Exception as e:  # retry transient failures
            last = e
            time.sleep(5 * attempt)
    raise SystemExit(f"catalog download failed: {last}")


def clean(s, n=200):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()[:n]


def bare(url):
    return url.split("?")[0]


def build(raw: dict, summary_len: int = 200) -> dict:
    modules = [
        {"uid": m["uid"], "title": m["title"], "url": bare(m["url"]),
         "levels": m.get("levels", []), "roles": m.get("roles", []),
         "products": m.get("products", []), "subjects": m.get("subjects", []),
         "minutes": m.get("duration_in_minutes"), "summary": clean(m.get("summary"), summary_len)}
        for m in raw.get("modules", [])
    ]
    paths = [
        {"uid": p["uid"], "title": p["title"], "url": bare(p["url"]),
         "levels": p.get("levels", []), "roles": p.get("roles", []),
         "products": p.get("products", []), "subjects": p.get("subjects", []),
         "minutes": p.get("duration_in_minutes"), "summary": clean(p.get("summary"), summary_len),
         "modules": p.get("modules", [])}
        for p in raw.get("learningPaths", [])
    ]
    if len(modules) < MIN_MODULES or len(paths) < MIN_PATHS:
        raise SystemExit(
            f"catalog looks incomplete: {len(modules)} modules, {len(paths)} paths")
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": "https://learn.microsoft.com/api/catalog/",
        "counts": {"modules": len(modules), "paths": len(paths)},
        "modules": modules, "paths": paths,
    }


def main() -> None:
    raw = fetch()
    out = build(raw)
    text = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
    size = len(text.encode("utf-8"))
    if size > MAX_BYTES:
        # Retry with shorter summaries before giving up.
        out = build(raw, summary_len=80)
        text = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
        size = len(text.encode("utf-8"))
    if size > MAX_BYTES:
        raise SystemExit(f"slim catalog is {size / 1e6:.1f} MB, over the {MAX_BYTES / 1e6:.1f} MB limit")
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({size / 1e6:.2f} MB): {out['counts']}")


if __name__ == "__main__":
    main()
