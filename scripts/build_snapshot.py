"""Build nightreign_data.json from the installed game."""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nrdata import extract, gamefiles

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFS = ROOT / "vendor" / "Paramdex" / "NR" / "Defs"
OUT = ROOT / "nrplanner" / "data" / "nightreign_data.json"


def main() -> None:
    game = gamefiles.find_game_dir()
    if game is None:
        print("no Nightreign installation found")
        raise SystemExit(1)
    print(f"game: {game}")

    data = extract.write_snapshot(game, DEFS, OUT)
    print(json.dumps(data["meta"], indent=2))
    print(f"\nwrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)\n")

    for hero in data["heroes"]:
        lv1, lv15 = hero["levels"][1], hero["levels"][15]
        print(
            f"  {hero['name']:<22} block={hero['status_block']:<4} "
            f"exact={hero['exact_levels']}  "
            f"Vig {lv1['Vigor']}->{lv15['Vigor']}  Str {lv1['Strength']}->{lv15['Strength']}"
        )

    colours = {0: "Red", 1: "Blue", 2: "Yellow", 3: "Green", 4: "White"}
    print("\n  chalices for hero_type 1:")
    for v in data["vessels"]:
        if v["hero_type"] != 1:
            continue
        base = "/".join(colours.get(c, str(c)) for c in v["slots"])
        deep = "/".join(colours.get(c, str(c)) for c in v["deep_slots"])
        print(f"    {v['name'][:32]:<33} {base:<22} + deep {deep}")

    print("\n  sample effects:")
    shown = 0
    for eff in data["effects"].values():
        if not eff["modifiers"] or not eff["colours"]:
            continue
        mods = ", ".join(f"{k}={v}" for k, v in list(eff["modifiers"].items())[:3])
        flag = "stacks" if eff["stacks"] else "STRONGEST ONLY"
        print(f"    {eff['name'][:38]:<38} [{flag:<14}] colours={eff['colours']} {mods}")
        shown += 1
        if shown >= 8:
            break

    stacking = sum(1 for e in data["effects"].values() if e["stacks"])
    with_mods = sum(1 for e in data["effects"].values() if e["modifiers"])
    print(f"\n  effects: {len(data['effects'])}, stackable {stacking}, "
          f"non-stacking {len(data['effects']) - stacking}")
    print(f"  effects with measurable stat modifiers: {with_mods}")


if __name__ == "__main__":
    main()
