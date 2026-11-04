"""Regenerate the plugin's color.png and outline.png icons.

Run with: python scripts/generate_icons.py
Requires: Pillow (pip install Pillow)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ACCENT = (0x2B, 0x57, 0x9A)  # matches manifest.json "accentColor": "#2B579A"


def draw_book_glyph(draw: ImageDraw.ImageDraw, box, fill):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    spine_x = x0 + w / 2
    # left and right pages as two rounded trapezoids meeting at the spine
    draw.polygon(
        [(x0, y0 + h * 0.08), (spine_x, y0 + h * 0.18), (spine_x, y1 - h * 0.08), (x0, y1 - h * 0.18)],
        fill=fill,
    )
    draw.polygon(
        [(x1, y0 + h * 0.08), (spine_x, y0 + h * 0.18), (spine_x, y1 - h * 0.08), (x1, y1 - h * 0.18)],
        fill=fill,
    )


def make_color_icon(path: Path, size: int = 192):
    img = Image.new("RGBA", (size, size), ACCENT + (255,))
    draw = ImageDraw.Draw(img)
    margin = size * 0.22
    draw_book_glyph(draw, (margin, margin, size - margin, size - margin), fill=(255, 255, 255, 255))
    img.save(path)


def make_outline_icon(path: Path, size: int = 32):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = size * 0.12
    draw_book_glyph(draw, (margin, margin, size - margin, size - margin), fill=(255, 255, 255, 255))
    img.save(path)


if __name__ == "__main__":
    make_color_icon(ROOT / "color.png")
    make_outline_icon(ROOT / "outline.png")
    print("Wrote color.png and outline.png")
