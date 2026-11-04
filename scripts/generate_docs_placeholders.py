"""Regenerate placeholder screenshots + site logo for the GitHub Pages docs site.

Run with: python scripts/generate_docs_placeholders.py
Requires: Pillow (pip install Pillow)
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
SCREENSHOTS = ASSETS / "screenshots"
ACCENT = (0x2B, 0x57, 0x9A)
LIGHT_BG = (0xF2, 0xF4, 0xF8)
BORDER = (0xC7, 0xD0, 0xDE)


def make_placeholder(path: Path, label: str, size=(960, 540)):
    img = Image.new("RGB", size, LIGHT_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, size[0] - 5, size[1] - 5], outline=BORDER, width=4)
    text = f"Screenshot placeholder:\n{label}\n\n(replace with a real screenshot)"
    lines = text.split("\n")
    y = size[1] / 2 - (len(lines) * 24) / 2
    for line in lines:
        w = draw.textlength(line)
        draw.text((size[0] / 2 - w / 2, y), line, fill=ACCENT)
        y += 28
    img.save(path)


if __name__ == "__main__":
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    make_placeholder(SCREENSHOTS / "plugins-list.png", "Cowork > Customize > Plugins (installed list)")
    make_placeholder(SCREENSHOTS / "add-plugin-dialog.png", "Cowork Add Plugin dialog")
    make_placeholder(SCREENSHOTS / "combined-summary-output.png", "Combined summary output in chat")

    logo_src = ROOT / "color.png"
    if logo_src.exists():
        Image.open(logo_src).save(ASSETS / "logo.png")
    print("Wrote docs/assets placeholders")
