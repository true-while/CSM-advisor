"""Update the "latest published version" marker block in INSTALL.md.

Run with: python scripts/update_install_version.py <version> <owner/repo>
Invoked automatically by .github/workflows/release.yml right after a new release is published, so
INSTALL.md always names the newest version and links to its release notes without manual edits.
"""
import datetime
import re
import sys
from pathlib import Path

MARKER_START = "<!-- latest-version:start -->"
MARKER_END = "<!-- latest-version:end -->"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: update_install_version.py <version> <owner/repo>")
    version, repo = sys.argv[1], sys.argv[2]

    path = Path(__file__).resolve().parent.parent / "INSTALL.md"
    text = path.read_text(encoding="utf-8")

    date = datetime.date.today().isoformat()
    block = (
        f"{MARKER_START}\n"
        f"Latest published version: **v{version}** (released {date}) - "
        f"[release notes](https://github.com/{repo}/releases/tag/v{version})\n"
        f"{MARKER_END}"
    )

    pattern = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"Could not find {MARKER_START} ... {MARKER_END} markers in INSTALL.md")

    new_text = pattern.sub(block, text, count=1)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print("INSTALL.md updated")
    else:
        print("INSTALL.md already up to date")


if __name__ == "__main__":
    main()
