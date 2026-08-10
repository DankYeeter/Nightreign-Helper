"""Draw the Nightreign Helper application icon.

Original artwork. Nothing here comes from the game: the wordmark on the
title screen is hand-lettered bitmap art with no alphabet behind it, so
there is no letter set to borrow even if it were ours to borrow. The
letterforms are Cinzel Black, a Trajan-derived display serif under the SIL
Open Font License.

The ground is keyed to the night-sky blue of the game's own desktop icon --
sampled as roughly #0d1134 in shadow through #252c56 in the midtones --
rather than to a neutral black.

Writes a layered PNG and a multi-resolution ICO next to the package data.

    python scripts/make_icon.py
"""

from __future__ import annotations

import math
import pathlib
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "nrplanner" / "data"

SIZE = 1024

# A cold slate with a blue lean, close to the game icon's midtones but flat
# enough that the corrosion on the letters is what carries the texture.
GROUND_CENTRE = (58, 66, 84)
GROUND_EDGE = (34, 39, 52)

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

# Fixed, so the wear falls the same way every time this is run.
NOISE_SEED = 20260810


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


def _noise(size: tuple[int, int], scale: int, seed: int) -> Image.Image:
    """Blotchy greyscale noise: random at low resolution, then smoothed up."""
    rng = random.Random(seed)
    small = (max(size[0] // scale, 2), max(size[1] // scale, 2))
    field = Image.new("L", small)
    field.putdata([rng.randrange(256) for _ in range(small[0] * small[1])])
    return field.resize(size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))


def _weather(alpha: Image.Image, seed: int) -> Image.Image:
    """Eat into the letters so they read as struck metal, not vector fill.

    The wear is concentrated at the edges. Chewing the solid interiors as
    hard would cost legibility at 16 px, where the strokes are a pixel or
    two wide and every bite counts.
    """
    # Where the edges are: the letter minus an eroded copy of itself. Only
    # this band gets chewed. Speckling the solid interiors instead reads as
    # dirt on the lens rather than as a worn casting, and it costs legibility
    # at 16 px where a stroke is a pixel or two wide.
    inner = alpha.filter(ImageFilter.MinFilter(9))
    edge = ImageChops.subtract(alpha, inner)

    # Two octaves: the coarse one decides which stretches of outline erode,
    # the fine one gives those stretches their tooth.
    coarse = _noise(alpha.size, 16, seed)
    fine = _noise(alpha.size, 5, seed + 1)
    grain = ImageChops.multiply(coarse, fine).point(lambda v: min(v * 3, 255))

    bite = ImageChops.multiply(ImageChops.invert(grain), edge)
    worn = ImageChops.subtract(alpha, bite)

    # Corrosion proper: holes bitten clean through the casting, kept away
    # from the very centre of a stroke so the letter never breaks in two.
    core = alpha.filter(ImageFilter.MinFilter(21))
    body = ImageChops.subtract(inner, core)
    rot = _noise(alpha.size, 9, seed + 5).point(lambda v: 255 if v < 74 else 0)
    return ImageChops.subtract(worn, ImageChops.multiply(rot, body))


def _ground() -> Image.Image:
    """Radial indigo-to-black ground, drawn small and scaled up."""
    small = 128
    base = Image.new("RGB", (small, small))
    pixels = base.load()
    centre = (small - 1) / 2
    longest = math.hypot(centre, centre)
    for y in range(small):
        for x in range(small):
            t = min(math.hypot(x - centre, y - centre) / longest, 1.0)
            pixels[x, y] = _lerp(GROUND_CENTRE, GROUND_EDGE, t**0.72)
    ground = base.resize((SIZE, SIZE), Image.LANCZOS)

    # A wash of cloud, so the blue is a night sky rather than a gradient.
    cloud = _noise((SIZE, SIZE), 90, NOISE_SEED + 7).filter(
        ImageFilter.GaussianBlur(26)
    )
    veil = Image.new("RGB", ground.size, (78, 88, 148))
    return Image.composite(
        Image.blend(ground, veil, 0.30), ground, cloud.point(lambda v: v // 2)
    )


def _rounded_mask() -> Image.Image:
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, SIZE - 1, SIZE - 1), radius=int(SIZE * 0.20), fill=255
    )
    return mask


def _text_layer(
    text: str, font: ImageFont.FreeTypeFont, tracking: int, seed: int
) -> Image.Image:
    """Render letter-spaced text, weathered, as its own tight RGBA image."""
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    ascent, descent = font.getmetrics()

    pad = 24
    layer = Image.new("L", (int(total) + pad * 2, ascent + descent + pad * 2), 0)
    draw = ImageDraw.Draw(layer)
    x = float(pad)
    for ch, width in zip(text, widths):
        draw.text((x, pad), ch, font=font, fill=255)
        x += width + tracking

    layer = _weather(layer, seed)
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

    nr = _text_layer("NR", _font(430), tracking=14, seed=NOISE_SEED)
    helper = _text_layer("Helper", _font(176), tracking=4, seed=NOISE_SEED + 3)

    # A soft gold bloom behind the monogram, so the letters sit in light
    # rather than on top of the ground.
    glow = Image.new("RGBA", icon.size)
    _paste_centred(glow, nr, 430)
    glow = glow.filter(ImageFilter.GaussianBlur(42))
    icon.alpha_composite(Image.blend(Image.new("RGBA", icon.size), glow, 0.5))

    _paste_centred(icon, nr, 430)

    # Divider: a rule broken by a diamond, the usual FromSoftware menu motif.
    draw = ImageDraw.Draw(icon)
    y = 648
    draw.line((96, y, SIZE - 96, y), fill=(176, 148, 92, 150), width=3)

    _paste_centred(icon, helper, 792)

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
