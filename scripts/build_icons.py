"""Extract the icons the planner needs into an icon pack.

The work itself lives in nrdata/iconbuild.py, because the application runs
it too: on first launch there is no pack, and building one is part of
starting up rather than part of a build step.

Writes into the per-user cache by default, which is where the app looks.
Pass a directory to write somewhere else.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nrdata import gamefiles, iconbuild
from nrplanner import paths

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFS = ROOT / "vendor" / "Paramdex" / "NR" / "Defs"


def main() -> int:
    game = gamefiles.find_game_dir()
    if game is None:
        print("no Nightreign installation found")
        return 1

    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else paths.icons_dir()
    print(f"game: {game}")
    iconbuild.build(game, DEFS, out, report=print)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
