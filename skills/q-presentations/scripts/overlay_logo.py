"""Overlay Dr. Q logo onto slide PNGs with configurable placement and auto-invert."""
import sys
import os
import glob
import argparse
from pathlib import Path
from PIL import Image, ImageOps

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "Logo_Q.png")

# Dark background hex values for known styles (luminance < 128)
DARK_STYLES = {"technical", "storytelling", "chalkboard", "blueprint", "neon", "pixel-art", "sketchnotes"}


def hex_luminance(hex_color: str) -> float:
    """Calculate perceived luminance from hex color string."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return 128.0
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def should_invert(style: str = "", bg_hex: str = "") -> bool:
    """Auto-detect whether logo needs inversion based on style or background color."""
    if style.lower() in DARK_STYLES:
        return True
    if bg_hex:
        return hex_luminance(bg_hex) < 128
    return False


def overlay_logo(slide_dir: str, position: str = "top-right", invert: bool = False,
                 size_pct: float = 0.06, style: str = "", bg_hex: str = ""):
    pngs = sorted(glob.glob(os.path.join(slide_dir, "*.png")))
    if not pngs:
        print(f"No slide images found in {slide_dir}")
        return

    # Auto-detect inversion if not explicitly set
    if not invert and (style or bg_hex):
        invert = should_invert(style, bg_hex)

    logo_path = LOGO_PATH if os.path.exists(LOGO_PATH) else None
    if not logo_path:
        # Fallback: resolve from script directory
        fallback = str(Path(__file__).parent.parent / "assets" / "Logo_Q.png")
        if os.path.exists(fallback):
            logo_path = fallback
    if not logo_path or not os.path.exists(logo_path):
        print(f"Logo not found at {logo_path}")
        return

    for png_path in pngs:
        slide = Image.open(png_path).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")

        if invert:
            r, g, b, a = logo.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.invert(rgb)
            logo = Image.merge("RGBA", (*rgb.split(), a))

        # Resize logo
        target_width = int(slide.width * size_pct)
        scale = target_width / logo.width
        target_height = int(logo.height * scale)
        logo = logo.resize((target_width, target_height), Image.LANCZOS)

        # Padding offsets for logo's internal whitespace
        pad_offset_x = int(target_width * 0.33)
        pad_offset_y = int(target_height * 0.33)
        margin_x = int(slide.width * 0.005)
        margin_y = int(slide.height * 0.005)

        # Calculate position
        if position == "top-right":
            logo_left = slide.width - target_width + pad_offset_x - margin_x
            logo_top = margin_y - pad_offset_y
        elif position == "bottom-right":
            logo_left = slide.width - target_width + pad_offset_x - margin_x
            logo_top = slide.height - target_height + pad_offset_y - margin_y
        elif position == "top-left":
            logo_left = margin_x - pad_offset_x
            logo_top = margin_y - pad_offset_y
        elif position == "bottom-left":
            logo_left = margin_x - pad_offset_x
            logo_top = slide.height - target_height + pad_offset_y - margin_y
        else:
            logo_left = slide.width - target_width + pad_offset_x - margin_x
            logo_top = margin_y - pad_offset_y

        slide.paste(logo, (logo_left, logo_top), logo)
        slide.save(png_path, "PNG")
        print(f"Logo added ({position}): {Path(png_path).name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Overlay Dr. Q logo on slide PNGs")
    parser.add_argument("slide_dir", help="Directory containing slide PNGs")
    parser.add_argument(
        "--position", default="top-right",
        choices=["top-right", "bottom-right", "top-left", "bottom-left"],
        help="Logo placement position (default: top-right)",
    )
    parser.add_argument(
        "--invert", action="store_true",
        help="Invert logo colors for dark backgrounds",
    )
    parser.add_argument(
        "--style", default="",
        help="Style name for auto-invert detection",
    )
    parser.add_argument(
        "--bg-hex", default="",
        help="Background hex color for auto-invert detection (e.g., #1A1A2E)",
    )
    parser.add_argument(
        "--size", type=float, default=0.06,
        help="Logo size as fraction of slide width (default: 0.06)",
    )
    parser.add_argument(
        "--skip", action="store_true",
        help="Skip logo overlay entirely",
    )
    args = parser.parse_args()

    if not args.skip:
        overlay_logo(args.slide_dir, args.position, args.invert,
                     args.size, args.style, args.bg_hex)
    else:
        print("Logo overlay skipped")
