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

GOLDEN = ROOT / "tests" / "golden" / "weapon_damage.json"


def load_data() -> dict:
    """The dataset, from a snapshot if there is one and the game if not."""
    from nrplanner import datasource, model, paths

    raw = os.environ.get("NIGHTREIGN_TEST_SNAPSHOT")
    if raw:
        data = json.loads(pathlib.Path(raw).read_text(encoding="utf-8"))
    elif paths.snapshot_path().is_file():
        data = json.loads(
            paths.snapshot_path().read_text(encoding="utf-8"))
    else:
        data = datasource.load_data()
    model.configure(data)
    return data


#: Ten times `run.run`'s worst measured real case (960 ms), the margin
#: `measure_picker_cards.py` uses for the advisor's own answer.
SAVE_READ_TIMEOUT_S = 10.0


def wait_for_the_save(window, timeout: float = SAVE_READ_TIMEOUT_S) -> None:
    """Let a window finish reading its save before anything drives it.

    Since T-142 (AD-029 stage B) the save is read in a background `QThread`;
    a `Planner` is complete before its relics are. None of the golden cases
    this script captures read `owned`, but a `QThread` still running when
    `planner.close()` runs below is the same hazard T-142 measured for a
    second read started mid-flight (`a-read-per-press`): the process can
    abort instead of exiting cleanly. Waited for as a state, not a span.
    """
    import time

    from PySide6.QtCore import QEventLoop
    from PySide6.QtWidgets import QApplication

    deadline = time.monotonic() + timeout
    app = QApplication.instance()
    while window.save_reader.is_reading():
        app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 10)
        if time.monotonic() > deadline:
            raise SystemExit(
                f"the save was still being read after {timeout:.0f} s; "
                f"nothing to capture")
    for _ in range(5):
        app.processEvents()


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
