"""`recompute()` itself has to wire `last_sources`/`last_rates`, not a test.

`StatSheet.draw()`, called from `Planner.recompute()`, sets
`self.last_sources = dict(build.sources)` and `self.last_rates =
dict(build.rates)` right before it draws the weapon-damage panel
(`statsheet.py`). `tests/weapon_damage_cases.run` -- the harness behind the
golden file -- does not go through `recompute()` at all: it assembles its own
build (`build_for`, deliberately outside the Planner, so the golden values
survive a refactor of `Planner._rebuild`) and then sets `last_sources`/
`last_rates` itself before drawing. That is the right choice for the golden
file, and it has a cost nobody had measured: no golden case exercises the two
lines in `recompute()` that the real click-through breakdown depends on.
Mutating `self.last_sources = dict(build.sources)` to `self.last_sources = {}`
left the entire suite -- 259 of 259 -- green (QA-076).

This file exercises `recompute()` directly instead, so the wiring has an
owner. It asserts `last_sources`/`last_rates` against the build `recompute()`
produced on its own (`current_build()`), never against a hand-written
expectation -- so it cannot pass by coincidence: if the assignment were
skipped, `last_sources` would keep whatever the previous state left it while
`current_build()` already holds the real contribution, and the two would
disagree.
"""

from __future__ import annotations

from nrplanner import statsheet
from tests import advisor_cases
from tests import weapon_damage_cases as cases


def test_recompute_wires_last_sources_and_last_rates_from_its_own_build(
        planner, game_data):
    hero = cases.hero_by_name(game_data, "Wylder")
    strength = cases.effects_raising_attribute(game_data, hero, "Strength", 1)
    rate = cases.effects_raising_rate(
        game_data, hero, "physicsAttackRate", 1)
    effects = [cases.effect_by_id(game_data, i) for i in strength + rate]

    planner.hero_index = game_data["heroes"].index(hero)
    planner.selected_effects = lambda: effects
    planner.recompute()

    build = planner.current_build()
    assert planner.stat_sheet.last_sources == dict(build.sources)
    assert planner.stat_sheet.last_rates == dict(build.rates)

    # Not vacuous: both chosen effects have to actually show up as a source,
    # or the equality above would hold for two empty dicts and prove nothing.
    assert planner.stat_sheet.last_sources.get("Strength"), (
        "the chosen effect left no trace in build.sources, so the equality "
        "above cannot tell a wired recompute() from an unwired one")
    assert any(field in planner.stat_sheet.last_rates for field in
               ("physicsAttackRate",)), (
        "the chosen effect left no trace in build.rates, so the equality "
        "above cannot tell a wired recompute() from an unwired one")


def test_a_condition_switch_reaches_declared_through_the_window(
        planner, game_data):
    """AD-034: the sheet emits `declared_changed`; `declared` stays the
    window's, which recomputes with it and prunes what is no longer equipped.
    """
    hero = planner.current_hero()
    declarable = advisor_cases.a_declarable_effect(game_data, hero)
    planner.selected_effects = lambda: [
        cases.effect_by_id(game_data, declarable)]
    planner.recompute()
    assert planner.declared == {}

    planner.stat_sheet.situational_rows[declarable].check.setChecked(True)
    assert planner.declared == {declarable: 1}
    assert [entry.live for entry in planner.current_build().situational
            if entry.effect_id == declarable] == [True]

    planner.selected_effects = lambda: []
    planner.recompute()
    assert planner.declared == {}, "a declaration outlived its effect"


def test_the_sheet_stops_a_count_at_the_effect_limit_and_nonsense_stays_one(
        planner, game_data):
    """100000 of an attack effect took 1.4 s and made the attack rating
    infinite, and `damage.displayed` raised in the middle of drawing the page
    (T-336h). `declared` only ever holds what the row says, so the row is the
    one place to stop it."""
    night_invader = 7060200
    planner.selected_effects = lambda: [
        cases.effect_by_id(game_data, night_invader)]
    planner.recompute()
    row = planner.stat_sheet.situational_rows[night_invader]
    row.check.setChecked(True)

    def left_with(text: str) -> tuple:
        row.count.setText(text)
        row.count.editingFinished.emit()
        return row.count.text(), planner.declared[night_invader]

    assert left_with("100000") == ("4", 4)
    assert left_with("5") == ("4", 4)
    assert left_with("3") == ("3", 3)
    for nonsense in ("abc", "", "-5", "0", "2.5"):
        assert left_with(nonsense) == ("1", 1), nonsense

    entry = next(entry for entry in planner.current_build().situational
                 if entry.effect_id == night_invader)
    seeded = statsheet.SituationalRow(entry, 100000, lambda: None)
    assert seeded.count.text() == "4"
    assert seeded.value() == 4
    assert seeded.count.toolTip().endswith("at most 4")
