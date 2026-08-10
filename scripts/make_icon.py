"""Draw the Nightreign Helper application icon.

Original artwork. Nothing here comes from the game: the wordmark on the
title screen is hand-lettered bitmap art with no alphabet behind it, so
there is no letter set to borrow even if it were ours to borrow. The
letterforms are Cinzel Black, a Trajan-derived display serif under the SIL
Open Font License.

Writes a layered PNG and a multi-resolution ICO next to the package data.

    python scripts/make_icon.py
"""

from __future__ import annotations

import math
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "nrplanner" / "data"

SIZE = 1024

# A dark ground so the gold reads at 16 px, warmed slightly towards the
# centre rather than a flat black.
GROUND_CENTRE = (44, 37, 26)
GROUND_EDGE = (9, 9, 12)

# Top-to-bottom gold. The pale top and the deep bottom are what make it
# look struck rather than filled.
GOLD_STOPS = [
    (0.00, (250, 238, 200)),
    (0.34, (226, 187, 96)),
    (0.58, (183, 133, 43)),
    (0.78, (140, 96, 27)),
    (1.00, (196, 152, 60)),
]

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\Cinzel-Black.ttf",
    r"C:\Windows\Fonts\CENTAUR.TTF",
    r"C:\Windows\Fonts\timesbd.ttf",
]

ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit("no serif font found; install Cinzel or Times New Roman")


def _lerp(a: tuple[int, ...], b: tuple[int, ...], t: float) -> tuple[int, ...]:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def _gold_gradient(size: tuple[int, int]) -> Image.Image:
    """A vertical gold ramp the size of a text box, used as a fill."""
    width, height = size
    strip = Image.new("RGB", (1, height))
    pixels = strip.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        for i in range(len(GOLD_STOPS) - 1):
            t0, c0 = GOLD_STOPS[i]
            t1, c1 = GOLD_STOPS[i + 1]
            if t0 <= t <= t1:
                pixels[0, y] = _lerp(c0, c1, (t - t0) / (t1 - t0))
                break
        else:
            pixels[0, y] = GOLD_STOPS[-1][1]
    return strip.resize((width, height))


def _ground() -> Image.Image:
    """Radial warm-to-black ground, drawn small and scaled up."""
    small = 128
    base = Image.new("RGB", (small, small))
    pixels = base.load()
    centre = (small - 1) / 2
    longest = math.hypot(centre, centre)
    for y in range(small):
        for x in range(small):
            t = min(math.hypot(x - centre, y - centre) / longest, 1.0)
            pixels[x, y] = _lerp(GROUND_CENTRE, GROUND_EDGE, t**0.75)
    return base.resize((SIZE, SIZE), Image.LANCZOS)


def _rounded_mask() -> Image.Image:
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, SIZE - 1, SIZE - 1), radius=int(SIZE * 0.20), fill=255
    )
    return mask


def _text_layer(text: str, font: ImageFont.FreeTypeFont, tracking: int) -> Image.Image:
    """Render letter-spaced text as its own tight RGBA image."""
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    ascent, descent = font.getmetrics()
    height = ascent + descent

    layer = Image.new("L", (max(int(total) + 4, 1), height + 4), 0)
    draw = ImageDraw.Draw(layer)
    x = 2.0
    for ch, width in zip(text, widths):
        draw.text((x, 2), ch, font=font, fill=255)
        x += width + tracking

    box = layer.getbbox()
    layer = layer.crop(box)

    gold = _gold_gradient(layer.size).convert("RGBA")
    gold.putalpha(layer)
    return gold


def _paste_centred(base: Image.Image, layer: Image.Image, centre_y: int) -> None:
    x = (base.width - layer.width) // 2
    y = centre_y - layer.height // 2
    base.alpha_composite(layer, (x, y))


def build() -> Image.Image:
    icon = Image.new("RGBA", (SIZE, SIZE))
    icon.paste(_ground().convert("RGBA"), (0, 0))

    # The engraved border: a bright hairline inset from a darker one, which
    # is what stops the tile looking like a plain rounded square.
    draw = ImageDraw.Draw(icon)
    draw.rounded_rectangle(
        (26, 26, SIZE - 27, SIZE - 27),
        radius=int(SIZE * 0.17),
        outline=(120, 88, 34, 255),
        width=10,
    )
    draw.rounded_rectangle(
        (44, 44, SIZE - 45, SIZE - 45),
        radius=int(SIZE * 0.15),
        outline=(214, 176, 92, 200),
        width=4,
    )

    nr = _text_layer("NR", _font(400), tracking=48)
    helper = _text_layer("HELPER", _font(132), tracking=26)

    # A soft gold bloom behind the monogram, so the letters sit in light
    # rather than on top of the ground.
    glow = Image.new("RGBA", icon.size)
    _paste_centred(glow, nr, 430)
    glow = glow.filter(ImageFilter.GaussianBlur(38))
    icon.alpha_composite(Image.blend(Image.new("RGBA", icon.size), glow, 0.55))

    _paste_centred(icon, nr, 430)

    # Divider: a rule broken by a diamond, the usual FromSoftware menu motif.
    y = 640
    for x0, x1 in ((250, 452), (572, 774)):
        draw.line((x0, y, x1, y), fill=(196, 156, 74, 235), width=5)
    draw.polygon(
        [(512, y - 22), (534, y), (512, y + 22), (490, y)],
        fill=(233, 198, 118, 255),
    )

    _paste_centred(icon, helper, 760)

    icon.putalpha(_rounded_mask())
    return icon


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    icon = build()

    png = OUT_DIR / "icon.png"
    icon.save(png)

    ico = OUT_DIR / "icon.ico"
    icon.save(ico, sizes=[(s, s) for s in ICO_SIZES])

    print(f"wrote {png} ({SIZE}x{SIZE})")
    print(f"wrote {ico} ({', '.join(str(s) for s in ICO_SIZES)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
