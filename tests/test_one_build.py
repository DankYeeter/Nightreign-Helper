"""Every tab reads one build, or the program contradicts itself.

QA-001: the Weapons tab called `model.compute` with its own, shorter argument
list -- no curses, no armament effects, no declared conditionals, no weapon
gates. Measured against the real game data on a Deep of Night build (Wylder,
Wylder's Urn): the Build planner said Vigor 5 and 180 HP, the Weapons tab said
Vigor 8 and 240 HP, and it ranked every weapon in the game on the second set.
Nothing on screen said which was right.

A second argument list is not a thing to correct, it is a thing to remove.
These tests are about the removal: the build is computed once and handed on,
so a new parameter cannot reach one caller and miss the other. The build
advisor will be the third caller, and it is the reason this had to happen
before it was written.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from nrplanner import model


REPO = pathlib.Path(__file__).resolve().parents[1]

# What the model module is called by the modules that import it, in the two
# spellings an import can bind: `from . import model` and `import
# nrplanner.model`.
MODEL_NAMES = frozenset({"model", "nrplanner.model"})


def python_modules(root: pathlib.Path) -> list[pathlib.Path]:
    """Every module under `root`, however deeply it is nested.

    Recursive, and that is why the function exists. The search space used to
    be glob("nrplanner/*.py"), which sees the top of the package and nothing
    inside it -- and the build advisor arrives as a package of its own,
    nrplanner/advisor/ (AD-001). The third caller, the one this guard was
    written for, would have been the one caller it could not see (QA-017).

    The space is still `nrplanner/` alone: `run.py` and `scripts/` are outside
    it and a second call site put there would not be seen (QA-023, held over).
    That is a deliberate boundary rather than an oversight -- the package is
    what ships -- and it is written down here because a guard whose reach is
    unstated is read as a guard with no limits.
    """
    return sorted(root.rglob("*.py"))


UI_MODULES = python_modules(REPO / "nrplanner")


def _dotted(node: ast.AST) -> str:
    """"a.b.c" for a name or a chain of attributes, "" for anything else."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return ""
    parts.append(node.id)
    return ".".join(reversed(parts))


def _local_names(tree: ast.AST) -> tuple[set[str], set[str]]:
    """(what this module calls the model, what it calls compute).

    Both halves are needed. `import nrplanner.model as m` binds the module
    under a name of the importer's choosing, and `from .model import compute`
    skips the module altogether and binds the function.
    """
    modules: set[str] = set()
    functions: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in MODEL_NAMES:
                    modules.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            # `from . import model`, `from nrplanner import model`,
            # `from .model import compute`, `from nrplanner.model import x`.
            tail = (node.module or "").rsplit(".", 1)[-1]
            for alias in node.names:
                if alias.name == "model":
                    modules.add(alias.asname or alias.name)
                elif alias.name == "compute" and tail == "model":
                    functions.add(alias.asname or alias.name)
    return modules, functions


def compute_call_sites(source: str) -> int:
    """How many times one module gets hold of model.compute.

    Read off the syntax tree rather than searched for as text. The rule is
    that there is one caller, not that there is one spelling of one caller: a
    search for "model.compute(" fell out for five of the six ways round it --
    the function imported by name, the module under an alias, getattr, a line
    break after the dot, functools.partial -- and counted a mention in a
    comment as a call (QA-017).

    References rather than calls, for the same reason. A reference handed to
    functools.partial, or assigned to a name, is a call site reached one step
    later, and a guard that insisted on parentheses would wave both through.

    What it cannot see, and is not claimed to: reaching the function at run
    time rather than by name -- `importlib.import_module`, a lookup in
    `sys.modules`, a name bound from a string. A tree is what is written, not
    what is executed, and no reading of the text can close that (QA-023, held
    over). It catches the spellings a second calculation would plausibly be
    written in, which is what it is for; it is not proof that there is one
    caller.
    """
    tree = ast.parse(source)
    modules, functions = _local_names(tree)
    found = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "compute":
            if _dotted(node.value) in modules:
                found += 1
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id in functions:
                found += 1
        elif (isinstance(node, ast.Call) and _dotted(node.func) == "getattr"
                and len(node.args) == 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value == "compute"
                and _dotted(node.args[0]) in modules):
            found += 1
    return found


# One entry per way of reaching model.compute without writing it where a text
# search would find it. Each of them is one call site and counts as one.
WAYS_ROUND_THE_GUARD = {
    "written out in full":
        "from nrplanner import model\nmodel.compute(hero, 15, [], {})\n",
    "the function imported by name":
        "from .model import compute\ncompute(hero, 15, [], {})\n",
    "the module under an alias":
        "from . import model as m\nm.compute(hero, 15, [], {})\n",
    "the module imported whole":
        "import nrplanner.model\n"
        "nrplanner.model.compute(hero, 15, [], {})\n",
    "getattr":
        "from . import model\n"
        "getattr(model, 'compute')(hero, 15, [], {})\n",
    "a line break after the dot":
        "from . import model\n(model.\n compute)(hero, 15, [], {})\n",
    "handed to functools.partial":
        "import functools\nfrom . import model\n"
        "run = functools.partial(model.compute, hero)\nrun(15, [], {})\n",
}


def attributes_on_the_planner_tab(planner) -> dict[str, int]:
    """The attribute totals as the Build planner tab shows them.

    Read off the widgets rather than from the build behind them: the claim
    under test is what the two tabs tell the player, and a figure that never
    reaches the screen cannot contradict anything.
    """
    out = {}
    for row, name in enumerate(model.ATTRIBUTE_ORDER):
        item = planner.attr_grid.itemAtPosition(row, 3)
        out[name] = int(item.widget().text())
    return out


def test_every_tab_computes_the_same_build(planner, game_data):
    """An armament's own effect must reach the Weapons tab as well.

    Armament effects are one of the four things the second argument list left
    out. This one is set on the tile rather than in a relic slot so the test
    needs no save file -- the divergence is the same either way.
    """
    from tests import weapon_damage_cases as cases

    hero = game_data["heroes"][planner.hero_index]
    raises_strength = cases.effects_raising_attribute(
        game_data, hero, "Strength", 1)[0]
    planner.weapon_slots[0].effect_ids = [raises_strength]
    planner.recompute()
    planner.weapons_tab.recalculate()

    assert planner.weapons_tab.attributes == attributes_on_the_planner_tab(planner)


def a_gated_attribute_effect(data: dict, hero: dict) -> int:
    """A gated effect that raises an attribute once its condition is declared.

    It has to move an attribute rather than a multiplier: the Weapons tab
    ranks on attributes, so a rate it never received is a divergence nothing
    on that tab could show.
    """
    curves = data.get("curves", {})
    for key in sorted(data["effects"], key=int):
        effect = data["effects"][key]
        if not model.is_conditional(effect, None):
            continue
        silent = model.compute(hero, 15, [effect], curves)
        declared = model.compute(hero, 15, [effect], curves,
                                 declared={int(effect["id"]): 1})
        if declared.attributes != silent.attributes:
            return int(effect["id"])
    raise LookupError("no gated attribute effect in this dataset")


def test_a_declared_conditional_reaches_every_tab(planner, game_data):
    """Declaring a gated effect changes the build, so it changes every tab."""
    hero = game_data["heroes"][planner.hero_index]
    declarable = a_gated_attribute_effect(game_data, hero)
    planner.weapon_slots[0].effect_ids = [declarable]
    planner.declared = {declarable: 3}
    planner.recompute()
    planner.weapons_tab.recalculate()

    assert planner.weapons_tab.attributes == attributes_on_the_planner_tab(planner)


def test_a_curse_reaches_every_tab(planner, game_data):
    """The case QA measured: a Deep of Night relic's curse.

    Needs the player's own save, because the curse has to come from a relic
    they actually own -- the planner offers nothing else.
    """
    cursed = _equip_a_cursed_deep_relic(planner)
    if cursed is None:
        pytest.skip("this save owns no Deep of Night relic carrying a curse")

    planner.recompute()
    planner.weapons_tab.recalculate()

    assert planner.weapons_tab.attributes == attributes_on_the_planner_tab(planner)


def _equip_a_cursed_deep_relic(planner):
    """Put the first owned cursed Deep relic into its slot, or return None."""
    planner.deep_check.setChecked(True)
    for slot in planner.deep_slots:
        for index in range(slot.relic_box.count()):
            item = slot.relic_box.itemData(index)
            if item is not None and getattr(item, "curse_ids", None):
                slot.relic_box.setCurrentIndex(index)
                return item
    return None


def test_the_user_interface_holds_exactly_one_call_to_compute():
    """One call site, so a new argument cannot reach one tab and miss another.

    This is the guard that outlives the fix above. Correcting the second
    argument list would have made the numbers agree today and drifted again at
    the next parameter; what keeps them together is that there is only one
    place to pass one.
    """
    callers = {
        path.relative_to(REPO).as_posix():
            compute_call_sites(path.read_text("utf-8"))
        for path in UI_MODULES
    }

    assert {name: n for name, n in callers.items() if n} == {
        "nrplanner/app.py": 1
    }, ("every tab must take the build from Planner.current_build(); "
        f"model.compute is reached in {callers}")


def test_the_guard_sees_every_way_round_itself():
    """A guard that knows one spelling guards the spelling.

    Five of these were invisible to the search this replaces, and the advisor
    is being written now: whoever writes the second caller will not write it
    in the one form a text search happened to look for.
    """
    missed = {label for label, source in WAYS_ROUND_THE_GUARD.items()
              if compute_call_sites(source) != 1}

    assert not missed, f"reached model.compute unnoticed: {sorted(missed)}"


def test_the_guard_does_not_mistake_a_mention_for_a_call():
    """Writing about the rule is not breaking it.

    The search this replaces counted the words in a comment, so the passage
    that most needs to explain why there is one call site was the passage it
    accused of being a second one.
    """
    mentioned = (
        "# The tabs used to call model.compute( with a shorter argument\n"
        "# list of their own -- see QA-001.\n"
        "TEXT = \"nothing here calls model.compute(...) but the Planner\"\n"
    )

    assert compute_call_sites(mentioned) == 0


def test_the_search_space_reaches_inside_a_package(tmp_path):
    """The advisor is a package, and a package has an inside.

    Against a tree of its own rather than the real one, because the module
    this is about does not exist yet -- and by the time it does, a guard that
    cannot see into it is worth exactly as much as no guard.
    """
    (tmp_path / "app.py").write_text("", encoding="utf-8")
    (tmp_path / "advisor").mkdir()
    (tmp_path / "advisor" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "advisor" / "beam.py").write_text("", encoding="utf-8")

    found = {p.relative_to(tmp_path).as_posix()
             for p in python_modules(tmp_path)}

    assert found == {"app.py", "advisor/__init__.py", "advisor/beam.py"}
