"""Turn the source icon artwork into the sizes the program ships.

The artwork itself is a file, not something this script draws: see
`SOURCE`. All this does is take the corners off, downscale it properly, and
write the multi-resolution ICO that Windows and Qt want.

Downscaling in one jump from 2048 px to 16 px throws away the strokes and
leaves mush, so it steps down by halves, which keeps the letterforms
readable at the small sizes where the icon actually gets looked at.

    python scripts/make_icon.py [source.png]
"""

from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "nrplanner" / "data"
SOURCE = ROOT / "art" / "icon_source.png"

MASTER = 1024
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]

# The artwork already has rounded corners drawn into it, so the mask only
# has to clear the few pixels outside them rather than cut a new shape.
CORNER_RADIUS = 0.19

# Below this the fine corrosion reads as noise and eats the strokes, so the
# small sizes get a touch of sharpening after the last step down.
SHARPEN_BELOW = 64


def _rounded_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size * 4 - 1, size * 4 - 1),
        radius=int(size * 4 * CORNER_RADIUS),
        fill=255,
    )
    return mask.resize((size, size), Image.LANCZOS)


def _step_down(image: Image.Image, target: int) -> Image.Image:
    """Halve repeatedly, then land on the target.

    A single LANCZOS jump from 2048 to 16 samples far too sparsely and the
    letters dissolve. Halving keeps every pixel contributing.
    """
    out = image
    while out.width // 2 > target:
        out = out.resize((out.width // 2, out.height // 2), Image.LANCZOS)
    out = out.resize((target, target), Image.LANCZOS)

    if target <= SHARPEN_BELOW:
        out = out.filter(ImageFilter.UnsharpMask(radius=1, percent=90, threshold=2))
    return out


def main() -> int:
    source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE
    if not source.exists():
        print(f"no artwork at {source}")
        return 1

    art = Image.open(source).convert("RGBA")
    print(f"source: {source.name} ({art.width}x{art.height})")

    master = _step_down(art, MASTER)
    master.putalpha(_rounded_mask(MASTER))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    png = OUT_DIR / "icon.png"
    master.save(png)

    # Each size is resampled from the artwork rather than from the master,
    # so nothing is downscaled twice.
    frames = []
    for size in ICO_SIZES:
        frame = _step_down(art, size)
        frame.putalpha(_rounded_mask(size))
        frames.append(frame)

    ico = OUT_DIR / "icon.ico"
    frames[-1].save(ico, format="ICO", sizes=[(s, s) for s in ICO_SIZES],
                    append_images=frames[:-1])

    print(f"wrote {png} ({MASTER}x{MASTER})")
    print(f"wrote {ico} ({', '.join(str(s) for s in ICO_SIZES)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
