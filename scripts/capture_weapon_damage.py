"""Freeze what the weapon-damage panel says today into the golden file.

Run this **before** touching the calculation, never after. The point of the
file it writes is to prove that a refactoring changed nothing; a file captured
from the refactored code would agree with it by construction and prove
nothing at all.

    python scripts/capture_weapon_damage.py

The dataset comes from the same three places the tests use: the environment
variable NIGHTREIGN_TEST_SNAPSHOT, the snapshot the program built for itself,
or a fresh read of the installed game. The game is only ever read.

The written file records the dataset it was captured from. Against a
different game version the test skips rather than fails, because a value
computed from other inputs is not evidence either way -- re-run this script
after verifying the numbers, and say in the commit that you did.

The `Planner` this drives reads its save in the background (AD-029 stage B,
T-142); this script waits for that read to end before driving it, the way
`tests/conftest.py::wait_for_the_save` does for the suite.
"""

import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Before PySide6 is imported: no display is available, and none is needed.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# The capture drives a real Planner, which stores the build it is holding.
# Without this it would write into the player's own settings.
os.environ.setdefault("NIGHTREIGN_SETTINGS_ORG", "DankYeeterTests")
os.environ.setdefault("NIGHTREIGN_SETTINGS_APP", "NightreignHelperTests")

from scripts.differential.capture import wait_for_the_save  # noqa: E402
from scripts.differential.plan import load_data  # noqa: E402

GOLDEN = ROOT / "tests" / "golden" / "weapon_damage.json"


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from nrplanner import app as appmod
    from tests import weapon_damage_cases as cases

    data = load_data()
    qapp = QApplication.instance() or QApplication([])
    planner = appmod.Planner(data)
    wait_for_the_save(planner)

    entries = []
    for case in cases.cases(data):
        entries.append({"case": case, "expected": cases.run(planner, data, case)})
        print(f"captured: {case['name']}")

    meta = data.get("meta", {})
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_text(
        json.dumps(
            {
                "dataset": {
                    "data_version": meta.get("data_version"),
                    "extract_version": meta.get("extract_version"),
                    "regulation_sha256": meta.get("regulation_sha256"),
                },
                "cases": entries,
            },
            indent=2, ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"\n{len(entries)} cases written to {GOLDEN.relative_to(ROOT)}")
    planner.close()
    del qapp
    return 0


if __name__ == "__main__":
    sys.exit(main())
