"""The Catalogue Photo of an Impossible Gadget (make.fun bounty).

Draws one studio catalogue photograph with PIL: a chrome toaster, the
TOAST-AIR 3000, whose slice of toast has just popped up and now floats
down gently under a small red-and-white parachute. The toast never lands
hard and never burns: it parachutes down. The parachute is the gadget's
one accessory; nothing else is in frame.

Standard library + PIL only, no network, fully deterministic.
Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   -> out/entry.png
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))

W = H = 1024
HERE = Path(__file__).resolve().parent


def load_label_font(size=30):
    """Label font that cannot die on a missing system font file.

    The grader runs in a slim pinned image that may not ship DejaVu, so
    try, in order: the vendored font.ttf next to this file, the system
    DejaVu path, then PIL's built-in default at the requested size.
    """
    for path in (HERE / "font.ttf",
                 Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")):
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            continue
    return ImageFont.load_default(size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, top, bottom):
    """Vertical gradient image."""
    w, h = size
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for y in range(h):
        px[0, y] = lerp(top, bottom, y / max(1, h - 1))
    return strip.resize((w, h))


def soft_ellipse(base, box, fill, blur):
    """Draw a blurred ellipse on a layer and composite it."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=fill)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def main():
    img = Image.new("RGB", (W, H))
    # --- studio backdrop: warm grey, lighter at top ---
    bg = vgrad((W, H), (242, 239, 233), (216, 210, 201))
    img.paste(bg, (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # floor: slightly darker band with a soft horizon line
    floor = vgrad((W, H - 780), (210, 204, 194), (196, 189, 178))
    img.paste(floor, (0, 780))
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(0, 780), (W, 780)], fill=(188, 181, 170, 255), width=2)

    # soft radial glow behind the product (focus)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([180, 60, 844, 900], fill=(255, 255, 255, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # --- contact shadow under the toaster ---
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([300, 792, 724, 838], fill=(60, 52, 44, 110))
    layer = layer.filter(ImageFilter.GaussianBlur(14))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ================= parachute canopy =================
    # canopy: upper half of an ellipse, 6 alternating red/white gores
    cx, cy, rx, ry = 512, 268, 268, 150
    canopy = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(canopy)
    panels = 6
    for i in range(panels):
        a0 = 180 + 180 * i / panels
        a1 = 180 + 180 * (i + 1) / panels
        color = (198, 38, 38, 255) if i % 2 == 0 else (245, 243, 238, 255)
        cd.pieslice([cx - rx, cy - ry, cx + rx, cy + ry], start=a0, end=a1, fill=color)
    # chord closing the canopy bottom
    cd.polygon([(cx - rx, cy), (cx + rx, cy), (cx + rx, cy + 6), (cx - rx, cy + 6)],
               fill=(198, 38, 38, 255))
    # gore seams + outline (PIL angles run clockwise from 3 o'clock,
    # y down: rim point at angle a is (cx + rx*cos a, cy + ry*sin a))
    for i in range(panels + 1):
        a = 180 + 180 * i / panels
        import math
        x = cx + rx * math.cos(math.radians(a))
        y = cy + ry * math.sin(math.radians(a))
        cd.line([(cx, cy), (x, y)], fill=(120, 20, 20, 160), width=2)
    cd.arc([cx - rx, cy - ry, cx + rx, cy + ry], start=180, end=360,
           fill=(120, 20, 20, 255), width=4)
    img.paste(Image.alpha_composite(img.convert("RGBA"), canopy).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ================= toast (floating, mid-air) =================
    # shroud lines: left rim points to the left toast corner,
    # right rim points to the right toast corner (no crossing)
    toast_top = 470
    toast_cx = 512
    left_rim = [(cx - rx + 30, cy + 2), (cx - rx // 2, cy - 55)]
    right_rim = [(cx + rx // 2, cy - 55), (cx + rx - 30, cy + 2)]
    for (x, y) in left_rim:
        d.line([(x, y), (toast_cx - 62, toast_top + 6)], fill=(90, 70, 55, 220), width=2)
    for (x, y) in right_rim:
        d.line([(x, y), (toast_cx + 62, toast_top + 6)], fill=(90, 70, 55, 220), width=2)

    # toast slice: crust edge + golden face, slight tilt
    toast = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(toast)
    td.rounded_rectangle([toast_cx - 78, toast_top, toast_cx + 78, toast_top + 118],
                         radius=26, fill=(176, 118, 40, 255))
    td.rounded_rectangle([toast_cx - 66, toast_top + 10, toast_cx + 66, toast_top + 106],
                         radius=20, fill=(232, 182, 76, 255))
    # a few deterministic brown speckles
    for (sx, sy, r) in [(468, 500, 4), (540, 516, 5), (512, 540, 4),
                        (486, 552, 3), (556, 548, 4), (500, 505, 3)]:
        td.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(190, 138, 52, 255))
    # soft shadow of the toast on the toaster top (it hovers just above)
    img.paste(Image.alpha_composite(img.convert("RGBA"), toast).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ================= chrome toaster =================
    tx0, ty0, tx1, ty1 = 312, 600, 712, 800
    # body: vertical chrome gradient
    body = vgrad((tx1 - tx0, ty1 - ty0), (233, 235, 238), (148, 152, 158))
    mask = Image.new("L", (tx1 - tx0, ty1 - ty0), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, tx1 - tx0, ty1 - ty0], radius=28, fill=255)
    img.paste(body, (tx0, ty0), mask)
    d = ImageDraw.Draw(img, "RGBA")
    # brushed highlight streaks
    for (sx, alpha) in [(352, 90), (392, 60), (640, 70)]:
        d.rectangle([sx, ty0 + 8, sx + 14, ty1 - 8], fill=(255, 255, 255, alpha))
    # bottom shade + outline
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=28, outline=(105, 108, 114, 255), width=3)
    d.rounded_rectangle([tx0, ty1 - 26, tx1, ty1], radius=12, fill=(120, 124, 130, 90))

    # top slot (dark)
    d.rounded_rectangle([372, 606, 652, 632], radius=10, fill=(38, 40, 44, 255))
    d.rounded_rectangle([382, 610, 642, 622], radius=6, fill=(18, 19, 22, 255))

    # lever on the right side, up
    d.rounded_rectangle([712, 648, 736, 664], radius=6, fill=(70, 72, 78, 255))
    d.rounded_rectangle([726, 636, 752, 676], radius=8, fill=(198, 38, 38, 255))
    d.rounded_rectangle([726, 636, 752, 676], radius=8, outline=(140, 22, 22, 255), width=2)

    # dial (browning control) bottom-left
    d.ellipse([352, 726, 396, 770], fill=(228, 230, 233, 255),
              outline=(105, 108, 114, 255), width=2)
    d.line([(374, 748), (386, 736)], fill=(60, 62, 66, 255), width=3)
    for ang in (-60, -20, 20, 60):
        import math
        x0 = 374 + 20 * math.cos(math.radians(ang - 90))
        y0 = 748 + 20 * math.sin(math.radians(ang - 90))
        x1 = 374 + 26 * math.cos(math.radians(ang - 90))
        y1 = 748 + 26 * math.sin(math.radians(ang - 90))
        d.line([(x0, y0), (x1, y1)], fill=(90, 92, 96, 255), width=2)

    # product label ON the toaster only
    font = load_label_font(30)
    label = "TOAST-AIR 3000"
    tw = d.textlength(label, font=font)
    d.text((512 - tw / 2, 688), label, font=font, fill=(58, 60, 64, 255))

    # feet
    d.rounded_rectangle([340, 800, 380, 810], radius=4, fill=(50, 52, 56, 255))
    d.rounded_rectangle([644, 800, 684, 810], radius=4, fill=(50, 52, 56, 255))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {img.size} {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
