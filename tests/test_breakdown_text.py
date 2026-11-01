"""QA-077: the text behind a clicked figure is read by a test.

Before, `StatSheet._show_breakdown` built it inline and handed it to
`QToolTip`; turning `(own - 1) * 100` into `own * 100` left the suite green.
"""

from types import SimpleNamespace

from nrplanner.statsheet import breakdown_text


def source(name, own):
    return SimpleNamespace(name=name, own=own)


def test_a_multiplier_is_shown_as_its_percentage_not_its_factor():
    text = breakdown_text("Attack", [source("Relic A", 1.124)], True)
    assert "+12.4%" in text
    assert "112.4" not in text


def test_several_multipliers_are_combined_multiplicatively():
    text = breakdown_text(
        "Attack", [source("A", 1.1), source("B", 1.1)], True)
    assert "combined multiplicatively: +21.0%" in text


def test_flat_bonuses_are_shown_as_numbers_and_summed():
    text = breakdown_text("Vigor", [source("A", 2), source("B", 3)], False)
    assert "+2" in text and "+3" in text and "total +5" in text
    assert "%" not in text


def test_a_figure_with_no_sources_says_so():
    assert breakdown_text("Attack", [], True) == (
        "Attack\nno contributing effects recorded")
