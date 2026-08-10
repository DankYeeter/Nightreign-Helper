"""Attack rating calculation.

This is the engine's own formula, assembled from four params that all carry an
exact paramdef, so nothing here is estimated:

  base   = attackBase{Type} x reinforce.{type}AtkRate
  factor = correct{Stat}/100 x reinforce.correct{Stat}Rate
           x curve(stat) / 100 x influence{Stat}_by{Type}
  AR     = base x (1 + sum of factors over every scaling stat)

Which stats feed which damage type comes from AttackElementCorrectParam; the
curve id per damage type comes from the weapon's own correctType_{Type}.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import evaluate_curve

DAMAGE_TYPES = ("Physics", "Magic", "Fire", "Thunder", "Dark")

DAMAGE_LABELS = {
    "Physics": "Physical",
    "Magic": "Magic",
    "Fire": "Fire",
    "Thunder": "Lightning",
    "Dark": "Holy",
}


# The upgrade number is an absolute rarity tier, not a count of upgrades:
# 1 Common, 2 Uncommon, 3 Rare, 4 Legendary. Confirmed by the data -- a
# weapon's reinforce group holds exactly (4 - rarity) tiers, so every weapon
# can climb to Legendary and one already there has nowhere to go. Reaching
# tier 4 only happens in the volcano event.
MIN_UPGRADE = 1
MAX_UPGRADE = 4
RARITY_TIERS = 4


@dataclass
class WeaponRating:
    weapon: dict
    base: dict[str, float] = field(default_factory=dict)
    scaled: dict[str, float] = field(default_factory=dict)
    total: float = 0.0
    unmet: dict[str, tuple[int, int]] = field(default_factory=dict)
    applied_upgrade: int = 0

    @property
    def meets_requirements(self) -> bool:
        return not self.unmet


def rate(weapon: dict, attributes: dict[str, int], data: dict,
         upgrade: int = MIN_UPGRADE) -> WeaponRating:
    curves = data["calc_curves"]
    reinforce_table = data["reinforce"]
    element_correct = data["element_correct"]

    # `upgrade` is the target rarity tier (1-4). How far a given weapon has to
    # travel is the gap between its own rarity and that target, so a Rare
    # weapon only moves when the target is Legendary.
    base_type = weapon.get("reinforce_type", 0)
    own_tier = weapon.get("rarity", 0) + 1
    steps = max(0, min(upgrade, MAX_UPGRADE) - own_tier)

    reinforce = None
    applied = 0
    for level in range(steps, -1, -1):
        reinforce = reinforce_table.get(str(base_type + level))
        if reinforce is not None:
            applied = level
            break
    if reinforce is None:
        reinforce = {"atk": {}, "correct": {}}

    aec = element_correct.get(str(weapon.get("element_correct_id")), {})
    result = WeaponRating(weapon=weapon, applied_upgrade=applied)

    for stat, needed in weapon["requires"].items():
        have = attributes.get(stat, 0)
        if needed and have < needed:
            result.unmet[stat] = (have, needed)

    for damage in DAMAGE_TYPES:
        base = weapon["base"].get(damage, 0)
        if not base:
            continue
        base *= reinforce["atk"].get(damage, 1.0)
        result.base[damage] = base

        rules = aec.get(damage, {})
        curve_id = str(weapon["curve"].get(damage))
        curve = curves.get(curve_id)

        bonus = 0.0
        if curve is not None:
            for stat, scaling in weapon["scaling"].items():
                rule = rules.get(stat)
                if not scaling or not rule or not rule["on"]:
                    continue
                # Requirements not met means the scaling contribution is lost.
                if stat in result.unmet:
                    continue
                correct = scaling / 100.0 * reinforce["correct"].get(stat, 1.0)
                ratio = evaluate_curve(curve, attributes.get(stat, 0)) / 100.0
                # Influence is stored as a percentage (100 = full effect).
                influence = rule["influence"] / 100.0
                bonus += correct * ratio * influence

        result.scaled[damage] = base * bonus

    result.total = sum(result.base.values()) + sum(result.scaled.values())
    return result


def rank(data: dict, attributes: dict[str, int], upgrade: int = MIN_UPGRADE,
         require_usable: bool = False) -> list[WeaponRating]:
    out = []
    for weapon in data["weapons"]:
        rating = rate(weapon, attributes, data, upgrade)
        if require_usable and not rating.meets_requirements:
            continue
        out.append(rating)
    out.sort(key=lambda r: -r.total)
    return out
