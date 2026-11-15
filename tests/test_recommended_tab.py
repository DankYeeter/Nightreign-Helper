"""The Recommended effects tab: ranking, owned counters, and the table."""

from nrplanner import effecttext, inventory, recommendedtab
from nrplanner.advisor import goals


def _relic(effect_id: int, deep: bool) -> inventory.OwnedItem:
    return inventory.OwnedItem(relic_id=1, name="Test", colour=0,
                               effect_ids=[effect_id], is_deep=deep)


def test_ranking_is_best_first_and_counts_normal_and_deep_apart(
        game_data, wylder):
    rows = recommendedtab.rank(game_data, wylder, 15, goals.MAX_DAMAGE.id)
    assert rows and all(row.gain > 0 for row in rows)
    assert [row.gain for row in rows] == sorted(
        (row.gain for row in rows), reverse=True)
    assert all(row.normal.colours or row.deep.colours for row in rows)
    assert all(row.status == recommendedtab.MISSING for row in rows)

    top = rows[0]
    owned = inventory.Inventory(source="test", relics=[
        _relic(top.effect["id"], False), _relic(top.effect["id"], True),
        _relic(top.effect["id"], True)])
    again = recommendedtab.rank(game_data, wylder, 15, goals.MAX_DAMAGE.id,
                                owned)
    first = next(row for row in again
                 if row.effect["id"] == top.effect["id"])
    assert (first.owned, first.owned_deep, first.status) == (
        1, 2, recommendedtab.OWNED)
    # Another strength of the same name is neither owned nor plainly
    # missing; another armament type of the same family is missing.
    for row in again:
        if row is first:
            continue
        same = (recommendedtab._untiered(row.effect)
                == recommendedtab._untiered(top.effect))
        assert (row.status == recommendedtab.OTHER_VERSION) == same, row


def test_an_armament_condition_counts_only_for_the_starting_armament(
        game_data, wylder):
    counted = {effecttext.name(row.effect) for row in recommendedtab.rank(
        game_data, wylder, 15, goals.MAX_DAMAGE.id)
        if effecttext.counts_armaments(row.effect)}
    assert len(counted) <= 1, counted


def test_the_table_shows_one_row_per_family_and_follows_the_planner(
        game_data, qapp):
    tab = recommendedtab.RecommendedTab(game_data)
    shown = tab.rows()
    assert tab.table.rowCount() == len(shown) <= 30
    assert len({row.family for row in shown}) == len(shown)
    assert recommendedtab.NO_SAVE in tab.summary.text()

    other = game_data["heroes"][-1]
    tab.follow(other["id"], 5)
    assert tab.hero_box.currentData() == other["id"]
    assert "level 5" in tab.summary.text()
    tab.set_inventory(inventory.Inventory(source="test", relics=[
        _relic(tab.rows()[0].effect["id"], True)]))
    assert tab.table.item(0, recommendedtab.COL_DEEP).text() == "1"
    tab.missing_only.setChecked(True)
    assert tab.table.rowCount() == len(tab.rows()) - 1
