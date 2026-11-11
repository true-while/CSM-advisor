"""Compute the next plugin version and write it into manifest.json and SKILL.md.

Run with: python scripts/next_version.py
Invoked by .github/workflows/release.yml on every push to main, so each push produces a new release.

Rules:
- If the version in manifest.json has no release tag (v<version>) yet, it is used as-is. This lets
  you start a new major/minor line by editing manifest.json (e.g. 1.2.0).
- Otherwise the patch number is incremented past the highest existing v<major>.<minor>.* tag.

Prints the resulting version on stdout (and nothing else).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def existing_tags() -> set[str]:
    out = subprocess.run(
        ["git", "tag", "--list", "v*"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def next_version(current: str, tags: set[str]) -> str:
    match = SEMVER.match(current)
    if not match:
        raise SystemExit(f"manifest.json version '{current}' is not MAJOR.MINOR.PATCH")
    if f"v{current}" not in tags:
        return current
    major, minor = match.group(1), match.group(2)
    prefix = re.compile(rf"^v{major}\.{minor}\.(\d+)$")
    highest = max(int(m.group(1)) for t in tags if (m := prefix.match(t)))
    return f"{major}.{minor}.{highest + 1}"


def write_manifest(version: str) -> Path:
    path = ROOT / "manifest.json"
    text = path.read_text(encoding="utf-8")
    new_text, count = re.subn(r'("version"\s*:\s*")[^"]+(")', rf"\g<1>{version}\g<2>", text, count=1)
    if count != 1:
        raise SystemExit("could not update version in manifest.json")
    path.write_text(new_text, encoding="utf-8", newline="")
    return path


def write_skill_files(version: str) -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    for skill in manifest.get("agentSkills", []):
        skill_md = ROOT / skill["folder"] / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        text = re.sub(r'(metadata:\s*\{[^}]*?version:\s*")[^"]+(")', rf"\g<1>{version}\g<2>", text, count=1)
        text = re.sub(r"(\*\*Current version:\*\*\s*`)[^`]+(`)", rf"\g<1>{version}\g<2>", text, count=1)
        skill_md.write_text(text, encoding="utf-8", newline="")


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    version = next_version(manifest["version"], existing_tags())
    write_manifest(version)
    write_skill_files(version)
    sys.stdout.write(version)


if __name__ == "__main__":
    main()
