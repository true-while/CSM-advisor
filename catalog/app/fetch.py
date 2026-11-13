"""Download the full Microsoft Learn catalog to a file.

Run: python -m app.fetch [output-path]
Used by the Dockerfile, so the catalog is baked into the image at build time and the running
service makes no outbound calls. The build fails if the download is incomplete.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

URL = os.environ.get("CATALOG_URL", "https://learn.microsoft.com/api/catalog/?locale=en-us")
MINIMUMS = {"modules": 1000, "units": 5000, "learningPaths": 100, "courses": 50}
TAXONOMIES = ("levels", "products", "roles", "subjects")


def download(url: str, attempts: int = 3) -> bytes:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "csm-advisor-catalog/1.0"})
            with urllib.request.urlopen(request, timeout=300) as response:
                return response.read()
        except Exception as exc:  # retry transient failures
            last = exc
            print(f"download attempt {attempt}/{attempts} failed: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise SystemExit(f"catalog download failed: {last}")


def validate(raw: dict) -> None:
    problems = [f"{name}: {len(raw.get(name, []))} < {minimum}" for name, minimum in MINIMUMS.items()
                if len(raw.get(name, [])) < minimum]
    problems += [f"{name}: missing" for name in TAXONOMIES if not raw.get(name)]
    if problems:
        raise SystemExit("catalog looks incomplete: " + "; ".join(problems))


def main(argv: list[str]) -> int:
    out = Path(argv[0] if argv else Path(__file__).resolve().parent.parent / "data" / "ms-learn-api.json")
    body = download(URL)
    validate(json.loads(body))
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_bytes(body)
    tmp.replace(out)
    print(f"wrote {out} ({len(body) / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
