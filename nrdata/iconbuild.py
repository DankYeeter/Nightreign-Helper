"""Building the icon pack from the installed game.

Decoding 4096x4096 BC7 atlases takes ~25 seconds, so it is done once and
cached rather than on every start. Lives here rather than in scripts/
because the application itself runs it on first launch.
"""

from __future__ import annotations

import json
import pathlib
from typing import Callable

from . import (bnd4, dds, dvdbnd, icons, param, paramdef, regulation, tpf)

PORTRAIT_SIZE = 128
ITEM_SIZE = 64
VARIANT_SIZE = 256
BOSS_SIZE = 128
BOSS_LARGE = 256

SOLO_HEADER = "/menu/00_solo_h.tpfbhd"
SOLO_DATA = "/menu/00_solo_h.tpfbdt"

# The DLC patch shipped Scholar's and Undertaker's illustrations in an archive
# pair whose paths are in no published dictionary. Located by scanning unnamed
# entries for a detached header containing MENU_Character members; the header
# and its data blob differ only in the tail of the name hash.
DLC_SOLO_HEADER = 0x6D0C219038D068B1
DLC_SOLO_DATA = 0x6D0C219038D066AD


def build(
    game: pathlib.Path,
    defs_dir: pathlib.Path,
    out_dir: pathlib.Path,
    report: Callable[[str], None] = lambda _: None,
) -> dict:
    """Extract every icon the app needs into out_dir; return the manifest.

    `report` is called with a human-readable line as each stage finishes, so
    a caller with a progress dialog can show it.
    """
    OUT = out_dir
    defs = paramdef.load_all(defs_dir)
    members = {f.basename[: -len(".param")]: f.data
               for f in regulation.load_params(game / "regulation.bin")}
    # Clear the output first. Without this a previous run's icons stay behind
    # and get packaged, since the whole directory is added to the executable.
    OUT.mkdir(parents=True, exist_ok=True)
    for stale in OUT.iterdir():
        if stale.is_file():
            stale.unlink()
    source = icons.IconSource(game)
    manifest = {"portraits": {}, "items": {}, "variants": {}, "menu": {}}

    # --- hero portraits ---------------------------------------------------
    hero = param.read(members["HeroParam"], defs.get("HeroParam"))
    for row in hero.rows:
        pid = row.values.get("properPortraitId")
        image = source.portrait(pid, PORTRAIT_SIZE)
        if image is None:
            report(f"   hero {row.id}: portrait {pid} missing")
            continue
        name = f"hero_{row.id}.png"
        image.save(OUT / name)
        manifest["portraits"][str(row.id)] = name
    report(f"portraits: {len(manifest['portraits'])}")

    # --- relic and chalice icons -----------------------------------------
    wanted = set()
    antique = param.read(members["EquipParamAntique"], defs["EquipParamAntique"])
    wanted |= {r.values.get("iconId") for r in antique.rows}
    stands = param.read(members["AntiqueStandParam"], defs["AntiqueStandParam"])
    wanted |= {r.values.get("iconId") for r in stands.rows}
    weapon_rows = param.read(members["EquipParamWeapon"], defs["EquipParamWeapon"])
    wanted |= {r.values.get("iconId") for r in weapon_rows.rows}
    magic_rows = param.read(members["Magic"], defs["Magic"])
    wanted |= {r.values.get("iconId") for r in magic_rows.rows}
    wanted = {i for i in wanted if isinstance(i, int) and i > 0}

    for icon_id in sorted(wanted):
        image = source.item_icon(icon_id, ITEM_SIZE)
        if image is None:
            continue
        name = f"item_{icon_id}.png"
        image.save(OUT / name)
        manifest["items"][str(icon_id)] = name
    report(f"item icons: {len(manifest['items'])} of {len(wanted)} requested")

    # --- boss artwork -----------------------------------------------------
    # Boss art is addressed as MENU_MenuIcon_<id>, the same sprite family as
    # the hero portraits rather than the item atlas, so it needs its own pass.
    # The two square sizes are packed; expeditionBackgroundId is 1360x600 and
    # is left out, since crop() squares whatever it is given.
    boss = param.read(members["NightBossMenuParam"], defs.get("NightBossMenuParam"))
    boss_icons = set()
    for row in boss.rows:
        for field in ("bossIconId", "largeBossIconId"):
            value = row.values.get(field)
            if isinstance(value, int) and value > 0:
                boss_icons.add((value, BOSS_LARGE if field == "largeBossIconId"
                                else BOSS_SIZE))

    for icon_id, size in sorted(boss_icons):
        image = source.portrait(icon_id, size)
        if image is None:
            continue
        name = f"menu_{icon_id}.png"
        image.save(OUT / name)
        manifest["menu"][str(icon_id)] = name
    report(f"boss icons: {len(manifest['menu'])} of {len(boss_icons)} requested")

    source.release()

    # --- full-body character variants ------------------------------------
    from PIL import Image

    archives = dvdbnd.open_all(game)
    arc = next(a for a in archives.values() if SOLO_HEADER in a)

    sources = [(
        [e for e in bnd4.read_split_header(arc.read(SOLO_HEADER))
         if e.basename.startswith("MENU_Character_")],
        lambda e: arc.read_range(SOLO_DATA, e.offset, e.size),
    )]

    if DLC_SOLO_HEADER in arc.entries:
        dlc_entries = [
            e for e in bnd4.read_split_header(arc.read_hash(DLC_SOLO_HEADER))
            if e.basename.startswith("MENU_Character_")
        ]
        sources.append((
            dlc_entries,
            lambda e: arc.read_range_hash(DLC_SOLO_DATA, e.offset, e.size),
        ))
        report(f"DLC illustrations found: {len(dlc_entries)}")

    entries = [(e, reader) for group, reader in sources for e in group]

    for entry, reader in entries:
        digits = "".join(c for c in entry.basename if c.isdigit())
        if len(digits) < 5:
            continue
        texture_id = int(digits[:5])
        hero_index = (texture_id - 49000) // 100 + 1
        if not 1 <= hero_index <= 10:
            continue

        blob = reader(entry)
        texture = tpf.read(blob)[0]
        width, height, rgba = dds.decode(texture.dds)
        image = Image.frombytes("RGBA", (width, height), rgba)
        image = image.resize((VARIANT_SIZE, VARIANT_SIZE), Image.LANCZOS)

        name = f"variant_{texture_id}.png"
        image.save(OUT / name)
        manifest["variants"].setdefault(str(hero_index), []).append(
            {"id": texture_id, "file": name}
        )
    total = sum(len(v) for v in manifest["variants"].values())
    report(f"character variants: {total} across "
          f"{len(manifest['variants'])} heroes")

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    size = sum(f.stat().st_size for f in OUT.iterdir())
    report(f"\nicon pack: {size / 1024 / 1024:.1f} MB in {OUT}")
    return manifest
