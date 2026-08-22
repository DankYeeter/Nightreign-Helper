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

# What this builder produces, so an existing pack can be told from a current
# one. Exactly the reason extract.EXTRACT_VERSION exists, and it was missed
# here: the pack was rebuilt only when its manifest was *missing*, so a player
# upgrading kept the pack an older build wrote, forever. 1.5.0 added the UI
# sprites for the chalice slots and the damage icons -- every 1.4.0 player
# would have upgraded into a program that draws slots it has no art for.
#
# Raise this whenever the pack gains or changes a sprite.
#   2  the relic-slot cell, the four slot gems, the twelve damage-type icons
#   3  Scarlet Rot and Sleep, the two status symbols the Nightlords tab had
#      no art for
ICON_VERSION = 3

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


# Sprite name -> the file it is written as. Damage-type icons are keyed by
# what they depict, which was read off the extracted images.
UI_SPRITES = {
    "MENU_In_RaritySlot_00.png": "ui_slot.png",
    # The slot-colour gems. The game shows these in the corner of a filled
    # slot, where the relic covers the coloured glow behind it and the colour
    # would otherwise be unreadable. Exactly four exist -- checked across the
    # whole MenuIcon range -- so White has none and is drawn.
    "MENU_MenuIcon_40480.png": "ui_gem_red.png",
    "MENU_MenuIcon_40481.png": "ui_gem_blue.png",
    "MENU_MenuIcon_40482.png": "ui_gem_green.png",
    "MENU_MenuIcon_40483.png": "ui_gem_yellow.png",
    "MENU_FL_40141.png": "ui_dmg_standard.png",
    "MENU_FL_40142.png": "ui_dmg_strike.png",
    "MENU_FL_40143.png": "ui_dmg_slash.png",
    "MENU_FL_40144.png": "ui_dmg_pierce.png",
    "MENU_FL_40145.png": "ui_dmg_holy.png",
    "MENU_FL_40146.png": "ui_dmg_magic.png",
    "MENU_FL_40147.png": "ui_dmg_frost.png",
    "MENU_FL_40148.png": "ui_dmg_fire.png",
    "MENU_FL_40150.png": "ui_dmg_lightning.png",
    "MENU_FL_40151.png": "ui_dmg_madness.png",
    "MENU_FL_40172.png": "ui_dmg_poison.png",
    "MENU_FL_40173.png": "ui_dmg_blood.png",
    # Scarlet Rot and Sleep are absent from the MENU_FL set -- it holds exactly
    # twelve icons, which is the relic screen's filter list and nothing more --
    # so the Nightlords tab printed those two rows with a blank where every
    # other status has a symbol.
    #
    # They come instead from MENU_PropertyIcon_3123x, the seven status symbols
    # the equipment screen uses, and the pairing is not eyeballed:
    # `MenuPropertySpecParam` rows 3026-3034 carry these very ids in `IconID`,
    # and the block 31230-31236 runs in the game's own status order. Three of
    # the seven are already in this table under their MENU_FL names -- 31230
    # is the same green as MENU_FL_40172 (Poison), 31232 the same red as 40173
    # (Blood loss), 31233 the same frost as 40147 (Frostbite) -- so the three
    # known members anchor the run and fix the two wanted here: 31231 is the
    # red growth (Scarlet Rot) and 31234 the closed eye (Sleep).
    #
    # 31235 (Madness) and 31236 (Death Blight) are deliberately left out:
    # Madness already has its MENU_FL icon, and no Nightlord row reports Death
    # Blight.
    "MENU_PropertyIcon_31231.png": "ui_dmg_rot.png",
    "MENU_PropertyIcon_31234.png": "ui_dmg_sleep.png",
}


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

    # -- UI sprites -------------------------------------------------------
    # The relic screen's own artwork, named by its Scaleform file rather than
    # guessed at: 01_125_itemsummary_antique.gfx references MENU_In_RaritySlot
    # for the slot backing and MENU_FL_401xx for the damage-type icons. The
    # slot sprite ships greyscale and is tinted per relic colour at draw time,
    # because the five that exist are a rarity ladder and carry no green.
    for sprite, name in UI_SPRITES.items():
        image = source.crop(sprite)
        if image is None:
            continue
        image.save(OUT / name)
        manifest.setdefault("ui", {})[sprite] = name
    report(f"ui sprites: {len(manifest.get('ui', {}))} of {len(UI_SPRITES)}")

    source.release()

    # -- read-back verification -------------------------------------------
    # A written file is not a delivered file: a scanner holding the
    # directory produced icons that existed at full size and failed every
    # open() minutes later. Each file is re-read and re-decoded here, with
    # one rewrite attempt, so a bad write is caught while the game data to
    # redo it is still in hand -- not at draw time on some later launch.
    from PIL import Image as _Image
    import io as _io
    bad = []
    for group in manifest.values():
        entries = group.items() if isinstance(group, dict) else []
        for _key, filename in entries:
            if not isinstance(filename, str):
                continue
            target = OUT / filename
            try:
                _Image.open(_io.BytesIO(target.read_bytes())).load()
            except OSError:
                bad.append(filename)
    if bad:
        report(f"verification: {len(bad)} of the written files failed to "
               f"read back (e.g. {bad[0]}) -- something on this machine is "
               "holding the icons directory; the pack may show gaps until "
               "the next rebuild")
    else:
        report("verification: every written icon reads back")

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

    manifest["icon_version"] = ICON_VERSION
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    size = sum(f.stat().st_size for f in OUT.iterdir())
    report(f"\nicon pack: {size / 1024 / 1024:.1f} MB in {OUT}")
    return manifest
