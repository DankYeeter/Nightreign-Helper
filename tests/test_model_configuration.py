"""The model refuses to compute before it has been told what the fields mean.

QA-011. Whether a number multiplies or adds is not decided by its name but by
the field's own neutral value in the game data, and `model.configure` is what
loads those. Until it has run, the module falls back to a name-based guess --
and the guess is not a rougher answer, it is a different one: "Improved Item
Discovery" carries itemDropRate 0.2 against a neutral of 0.0, a straight
+40% at two stacks, which read as -60% when taken for a multiplier.

The build advisor will call `model.compute` from a background thread, far
from the startup path that happens to call `configure` today. A silent wrong
answer there would be indistinguishable from a right one.
"""

from __future__ import annotations

import pytest

from nrplanner import model

# The field the divergence was measured on.
FRACTION_FIELD = "itemDropRate"


@pytest.fixture
def unconfigured(game_data):
    """Put the module back in the state it is in before any data is loaded.

    `game_data` is taken first on purpose: it configures the module, so this
    fixture is undoing something that has definitely happened, and the
    restore at the end puts back exactly that.
    """
    model._CONFIGURED = False
    model.FIELD_BASELINE.clear()
    model.PERCENT_FIELDS.clear()
    model.PERCENT_OF_100_FIELDS.clear()
    yield
    model.configure(game_data)


def test_compute_refuses_until_the_data_has_configured_it(
        game_data, unconfigured):
    hero = game_data["heroes"][0]

    with pytest.raises(RuntimeError) as raised:
        model.compute(hero, 1, [], game_data.get("curves", {}))

    assert "configure" in str(raised.value)


def test_the_guess_it_refuses_to_make_is_the_wrong_one(
        game_data, unconfigured):
    """Named here so the refusal above is not mistaken for caution.

    Unconfigured, the module would treat a fraction-of-one field as a
    multiplier because its name ends in "Rate". Configured, the data says its
    neutral is 0.0 and it adds.
    """
    assert model.is_multiplier(FRACTION_FIELD) is True

    model.configure(game_data)

    assert model.is_multiplier(FRACTION_FIELD) is False
    assert FRACTION_FIELD in model.PERCENT_FIELDS


def test_a_configured_model_computes_as_before(game_data):
    """The guard costs nothing on the ordinary path."""
    hero = game_data["heroes"][0]

    build = model.compute(hero, 1, [], game_data.get("curves", {}))

    assert build.attributes == build.base_attributes
