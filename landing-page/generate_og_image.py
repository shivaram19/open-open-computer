#!/usr/bin/env python3
"""Generate a 1200x630 Open Graph image for the Sukha landing page."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

WIDTH, HEIGHT = 1200, 630

# Sukha design tokens (light mode)
BG = "#faf6f1"
TEXT_PRIMARY = "#0f0e0d"
TEXT_SECONDARY = "#3d3a36"
ACCENT = "#0d7377"
WARM = "#b45309"

FONT_DIR = Path("/usr/share/fonts/truetype")


def find_font(name: str, style: str = "") -> Path:
    """Best-effort font lookup."""
    candidates = []
    if "DejaVu" in name:
        candidates = [
            FONT_DIR / "dejavu" / f"DejaVuSans-{style}.ttf" if style else FONT_DIR / "dejavu" / "DejaVuSans.ttf",
            FONT_DIR / "dejavu" / "DejaVuSans-Bold.ttf",
        ]
    elif "Liberation" in name:
        suffix = style if style else "Regular"
        candidates = [FONT_DIR / "liberation" / f"LiberationSans-{suffix}.ttf"]
    else:
        candidates = [
            FONT_DIR / "dejavu" / "DejaVuSans-Bold.ttf",
            FONT_DIR / "liberation" / "LiberationSans-Bold.ttf",
        ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # Fallback to any ttf
    return next(FONT_DIR.rglob("*.ttf"), None)


def main() -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_bold = ImageFont.truetype(str(find_font("DejaVu", "Bold")), 120)
    font_body = ImageFont.truetype(str(find_font("DejaVu", "")), 48)
    font_small = ImageFont.truetype(str(find_font("DejaVu", "")), 28)
    font_url = ImageFont.truetype(str(find_font("DejaVu", "Bold")), 24)

    # Decorative leaf mark (top-left) — drawn, not emoji, for font independence
    leaf_center = (100, 100)
    leaf_size = 28
    # Simple leaf shape using ellipse + stem
    draw.ellipse(
        [leaf_center[0] - leaf_size, leaf_center[1] - leaf_size * 1.4,
         leaf_center[0] + leaf_size, leaf_center[1] + leaf_size * 1.4],
        fill=ACCENT,
    )
    draw.line(
        [(leaf_center[0], leaf_center[1] + leaf_size * 1.2),
         (leaf_center[0], leaf_center[1] + leaf_size * 2.0)],
        fill=ACCENT,
        width=6,
    )

    # Brand name
    draw.text((70, 170), "Sukha", font=font_bold, fill=TEXT_PRIMARY)

    # Tagline
    draw.text((70, 330), "AI that doesn't give you anxiety", font=font_body, fill=TEXT_SECONDARY)

    # Relief-focused sub-line
    draw.text((70, 410), "Open-source cognitive infrastructure for calm systems", font=font_small, fill=TEXT_SECONDARY)

    # URL at bottom
    draw.text((70, 540), "shivaram19.github.io/open-open-computer", font=font_url, fill=ACCENT)

    # Subtle accent underline
    draw.rounded_rectangle([70, 310, 300, 318], radius=4, fill=ACCENT)

    out_path = Path(__file__).parent / "og-image.png"
    img.save(out_path, "PNG")
    print(f"Saved OG image: {out_path}")


if __name__ == "__main__":
    main()
