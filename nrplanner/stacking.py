"""How an effect combines with another copy of itself, and with everything else.

Two separate questions get confused constantly, so they are kept apart here:

  *Does it stack?*      Whether a second copy adds anything at all. Decided by
                        the game's own isStrongestEffect and exclusivityId.
  *How does it combine?* Whether its numbers add or multiply. Decided by the
                        field's neutral value across every SpEffect row in the
                        game -- 0.0 means the field adds, 1.0 means it
                        multiplies -- and never by whether the name ends in
                        "Rate". Nine fields end in Rate and nevertheless add.

Both answers come from the params, with one exception each way.

How the engine combines two *different* effects touching the same field is
written down nowhere. It was measured instead, five ways, and the answer is
**multiplicative** -- two relics at +6% and +9% give x1.1554, not x1.15. See
HANDOVER section 6.

And the params are not always right. `model.NON_ACCUMULATING` holds the fields
the game refuses to add up despite flagging them as stacking; `repetition()`
consults it, so this module agrees with the totals rather than with the flags.
"""

from __future__ import annotations

from . import model

# What a second copy of the same effect does.
STACKS = "stacks"                 # every copy counts
STRONGEST = "strongest only"      # isStrongestEffect: the best copy wins
EXCLUSIVE = "exclusive group"     # exclusivityId: one of the group applies
# A REJECTED hypothesis, kept because it is convincing and wrong, and would
# otherwise be re-derived by the next person who notices the same field.
#
# Some effects do not carry their number directly. They apply a state, and the
# state carries it -- `replaceSpEffectId` names the SpEffect swapped in, and
# `invocationConditionsStateChange1` the state that gates it:
#
#   Successful guarding fills more of the Art gauge   1.0  -> replace 7030602, state 2009
#   the +1 version of the same                        1.5  -> replace 7030612, state 2382
#
# A state is on or off, so a second copy of one tier should set a state already
# set and be worth nothing, while a different tier sets a different state and
# applies in full. That is exactly what a community source claims, and the two
# magnitudes match its "(1)" and "(1.5)" precisely, which made it look settled.
#
# It was put to the game and did not survive: two relics carrying the identical
# effect appeared to stack. The report is by feel with no number attached, so
# it is weak on its own -- but the params never claimed otherwise either, since
# all of these are flagged as stacking. Weak evidence plus the params both
# pointing one way beats a mechanism argument pointing the other, so the class
# is gone rather than merely doubted.
#
# What would settle it properly: the same family carrying a quantity that shows
# on a panel, owned twice, ungated. Daniel's inventory has none -- every
# duplicate he holds is gated or Nightfarer-specific -- so the Art gauge, which
# can only be eyeballed, was the sharpest instrument available.
STATE_FIELD = "replaceSpEffectId"

# How this effect's own numbers enter the totals.
ADDS = "adds"
MULTIPLIES = "multiplies"
BOTH = "adds + multiplies"
NO_NUMBER = "no number"


def quantities(effect: dict) -> list[str]:
    """The fields on this effect that actually become a number on the sheet.

    Deliberately not "every numeric field". A row carries mechanism alongside
    magnitude -- dontDeleteOnDead, invocationConditionsStateChange1,
    isWaitModeDelete are flags and ids that happen to be stored as numbers.
    Counting those made effects with no magnitude at all report as "adds",
    which is precisely the kind of confident wrong answer this module exists
    to avoid. The set below is the one `model.compute` turns into totals; if
    the sheet does not use a field, this does not claim it combines.
    """
    out = []
    for field_name, value in (effect.get("modifiers") or {}).items():
        if not isinstance(value, (int, float)):
            continue
        if model.is_sentinel(field_name):
            continue
        known = (
            field_name in model.ATTRIBUTE_FIELDS
            or field_name in model.FLAT_BONUSES
            or field_name in model.EXTRA_MULTIPLIERS
            or field_name in model.ELEMENT_ATTACK_RATES
            or field_name in model.PERCENT_FIELDS
            or any(field_name in pair for pair in model.RESISTANCES.values())
            or (field_name.endswith("Rate") and model.is_multiplier(field_name))
        )
        if known:
            out.append(field_name)
    return sorted(out)


def combination(effect: dict) -> str:
    """Whether this effect's numbers add or multiply, from the field baselines.

    An effect can do both -- "Physical Attack Up +3" alongside a rate on the
    same row -- and saying so is more honest than picking the louder half.
    """
    adds = multiplies = False
    for field_name in quantities(effect):
        if model.is_multiplier(field_name):
            multiplies = True
        else:
            adds = True
    if adds and multiplies:
        return BOTH
    if multiplies:
        return MULTIPLIES
    if adds:
        return ADDS
    return NO_NUMBER


def repetition(effect: dict) -> str:
    """What a second copy of this exact effect is worth.

    Order matters. exclusivityId is the game stating a group outright, so it
    wins. isStrongestEffect is the game stating it per effect. A shared state
    is the game implying it through the delivery mechanism, so it is checked
    last and only decides effects the first two say nothing about.
    """
    exclusivity = effect.get("exclusivity", -1)
    if isinstance(exclusivity, int) and exclusivity > 0:
        return EXCLUSIVE
    if not effect.get("stacks", True):
        return STRONGEST
    # Measured behaviour beats the flags. model.NON_ACCUMULATING lists fields
    # the game refuses to add up despite the params marking them as stacking,
    # and the tab has to say the same thing the totals do -- a column claiming
    # an effect stacks while the sheet declines to stack it is worse than no
    # column.
    if any(f in model.NON_ACCUMULATING
           for f in (effect.get("modifiers") or {})):
        return STRONGEST
    # A shared state was expected to mean a duplicate is wasted -- see
    # STATE_FIELD -- and the game says otherwise, so the check is gone rather
    # than merely doubted.
    return STACKS


def classify(effect: dict) -> str:
    """The one-line class shown in the Effects tab.

    Reads as the answer to "if I equip two of these, what do I get" followed
    by "and how does its number land", because those are the two things a
    player is actually asking when they compare relics.
    """
    how = combination(effect)
    what = repetition(effect)
    if what == STACKS:
        # One bracket style across all three classes; the old dash form
        # ("Stacks — no number") read as a different kind of statement from
        # "Stacks (adds)" while answering the same question.
        return f"Stacks ({how})"
    if what == EXCLUSIVE:
        return f"Exclusive group ({how})"
    return f"Strongest only ({how})"


def evidence(effect: dict) -> str:
    """Which field decided the class, so the claim can be checked."""
    exclusivity = effect.get("exclusivity", -1)
    if isinstance(exclusivity, int) and exclusivity > 0:
        return (f"exclusivityId {exclusivity} — the game groups these and "
                f"applies only one")
    if not effect.get("stacks", True):
        return "isStrongestEffect — the game keeps only the strongest copy"
    measured = sorted(f for f in (effect.get("modifiers") or {})
                      if f in model.NON_ACCUMULATING)
    if measured:
        return (f"{', '.join(measured)} does not add up — measured in game, "
                f"the params mark this as stacking and it is not")
    state = (effect.get("modifiers") or {}).get(STATE_FIELD)
    if state:
        return (f"stacks — delivered by swapping in SpEffect {int(state)}, "
                f"which looked like it should make a duplicate worthless; "
                f"the game says otherwise, so the flag is what counts")
    fields = quantities(effect)
    if not fields:
        return "carries no quantity, so nothing combines"
    parts = [f"{f} ({'x' if model.is_multiplier(f) else '+'})" for f in fields]
    return "neutral value of " + ", ".join(parts)


def tier_note(effect: dict, siblings: list[dict]) -> str:
    """Whether this effect is one rung of a same-name ladder, and what that means.

    A ladder -- Grief at +3 / +6 / +9 -- is made of separate effects with
    their own SpEffect ids, not of one effect at three strengths. Two rungs
    therefore both apply. This is worth stating outright because the opposite
    is the natural assumption.
    """
    if len(siblings) < 2:
        return ""
    if not effect.get("stacks", True):
        return (f"one of {len(siblings)} strengths under this name; only the "
                f"strongest applies")
    return (f"one of {len(siblings)} strengths under this name — separate "
            f"effects, so two rungs both apply")
