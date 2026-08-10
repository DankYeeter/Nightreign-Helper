"""What the community reports about the world events. NOT from the game files.

Everything else in this project is read out of the user's own installation.
This module is the one deliberate exception, and it is kept in its own file,
outside the snapshot, so the separation cannot blur: `nightreign_data.json`
stays game-derived only, and the tab labels this material on screen every time
it shows it.

**This file has shrunk in usefulness, deliberately.** When it was written it
carried the rewards, the penalties and the Nightlord gating, because none of
those were derivable. All three now are, and the tab suppresses any community
line the extracted data already answers. What is left doing real work here is
the *prose* -- how an event behaves in play, which the params never describe --
plus the recorded disagreements between sources.

`nightlords` entries are kept but no longer displayed for any event whose
gating resolved (see `nrdata.extract.EVENT_MODIFIER`). They stay as the record
of what was claimed before the files confirmed it, and because the eight exact
pool matches are what identified the modifiers in the first place -- deleting
them would erase the evidence for the identification.

**Occurrence chance is still absent here and must stay absent.** The tab now
shows pool shares read from the map patterns; no source publishes a real
per-event percentage, so none is written down.

Sources, all fetched 2026-08-09:
  fextralife   https://eldenringnightreign.wiki.fextralife.com/Events
  eldenpedia   https://eldenring.wiki.gg/wiki/Nightreign:Special_Events
  game8        https://game8.co/games/Elden-Ring-Nightreign/archives/526257

Where they disagree, the disagreement is recorded rather than resolved
silently -- except where this project's own extracted text settles it, which
has happened twice and is noted at the entry.
"""

from __future__ import annotations

# Keyed by UserDispLogParam announcement row -- the same id the extracted
# events carry, so the two layers join without any name matching.
LORE: dict[int, dict] = {
    11110: {
        "buff_id": 8970000,
        "creature_chr": 2130,
        "name": "Fell Omen / Morgott Invasion",
        "what": (
            "It hunts one player specifically, teleporting to them across "
            "the map, and does not switch targets unless that player goes "
            "down."
        ),
        "penalty_sp": 6999400,
        "penalty": (
            "Only the trigger is reported: the debuff lands if the Fell Omen "
            "kills the player it is hunting. Its size is extracted above."
        ),
        "nightlords": ["Adel", "Gnoster", "Heolstor"],
        "sources": ["fextralife", "eldenpedia", "game8"],
    },
    11120: {
        "buff_id": 8970020,
        "creature_chr": 7540,
        "name": "Giant Bubbles / Augur",
        "what": (
            "Entering a bubble pulls you into an arena against a weakened "
            "Augur that barely fights back."
        ),
        "reward": "A passive restoring FP when you use the Flask of Crimson Tears.",
        "penalty": (
            "Reported to expire on its own if the Night's Tide swallows the "
            "arena. One source also claims a loss leaves the same Unhealed "
            "Wound debuff the Fell Omen inflicts; nothing in the files ties "
            "that debuff to this event, so it is not shown as a penalty."
        ),
        "nightlords": ["Gnoster", "Caligo", "Heolstor"],
        "conflict": (
            "The passive is called Unifying Fate by fextralife and Undying "
            "Fate by game8. Eldenpedia labels this event's creature as the "
            "Sentient Pest and the locust one as the Augur -- the reverse of "
            "the other two. This project's own extracted text settles it: the "
            "bubble event's outcome line is \"The master of bubbles was "
            "felled\" and the locust one is \"Find the enemy who is stealing "
            "runes\", so fextralife and game8 have the pairing right."
        ),
        "sources": ["fextralife", "game8"],
    },
    11130: {
        "buff_id": 8970030,
        "name": "Curse of the Demon / Libra, Creature of Night",
        "what": (
            "The demon marks itself on the map and cuts every party member's "
            "maximum HP by about 30%. It is the Scale-Bearing Merchant: you "
            "can trade with it, pay it off, or attack it, in which case it "
            "becomes the Equilibrious Beast."
        ),
        "reward": (
            "Paying 15,000 runes on day 1 (35,000 on day 2) lifts the curse "
            "and gives the team the Demon's Plating buff, plus a reward orb "
            "of talismans and runes and access to its deals. Killing it "
            "instead pays a large pile of runes, Demon's Plating, and an orb "
            "of three random talismans."
        ),
        "penalty": (
            "Ignore it and the reduced maximum HP simply stays for the rest "
            "of the run. Refusing the deal is its own outcome -- the game "
            "announces \"A failed deal has sown enmity\"."
        ),
        "nightlords": ["Caligo", "Fulghor", "Heolstor"],
        "conflict": (
            "Sources split on whether killing it lifts the curse: fextralife "
            "says it does, one summary of the same site says the HP cut "
            "persists for the whole run. This project's extracted text is "
            "decisive -- the game's own outcome banner for that branch reads "
            "\"Foe felled, cleansing the curse\", so killing it does cleanse."
        ),
        "sources": ["fextralife", "eldenpedia", "game8"],
    },
    11140: {
        "buff_id": 8970010,
        "creature_chr": 7520,
        "name": "Plague of Locusts / Sentient Pest",
        "what": (
            "The Sentient Pest is hidden and stationary; its swarms steal "
            "runes and can knock you down whole levels. Follow them back to "
            "it."
        ),
        "reward": (
            "Your stolen runes back, plus Integration of Intelligence. The "
            "size of that proc is extracted above."
        ),
        "penalty": "Levels lost to the swarms stay lost if you never reach it.",
        "nightlords": ["Maris", "Libra", "Heolstor"],
        "sources": ["fextralife", "eldenpedia", "game8"],
    },
    11150: {
        "name": "Additional Night Boss",
        "what": (
            "A second Night Boss spawns straight after the first, with HP, FP "
            "and flasks refilled for the fight."
        ),
        "reward": "A second set of boss rewards -- Dormant Powers and runes.",
        "penalty": "You have to beat it; a team caught unprepared can lose the run there.",
        "nightlords": ["Adel", "Fulghor"],
        "uncertain": (
            "This is the least certain pairing on the tab. The game announces "
            "\"The Night threatens us anew\" and never announces it ending, "
            "which fits an extra boss, but nothing in the files ties that "
            "banner to this community-named event."
        ),
        "sources": ["fextralife", "eldenpedia", "game8"],
    },
    11160: {
        "creature_chr": 4680,
        "name": "Meteor Strike / Fallingstar Beast",
        "what": (
            "The crater is marked on the map and a Fallingstar Beast waits "
            "in it. An ordinary boss fight -- no second phase, nothing to "
            "fail."
        ),
        "reward": "Epic-tier loot; reported as reliably Epic-rarity Dormant Powers.",
        "penalty": "None. Skipping it costs only the loot.",
        "nightlords": ["Gladius", "Adel", "Caligo"],
        "sources": ["fextralife", "eldenpedia", "game8"],
    },
    11170: {
        "name": "Hordes of the Night",
        "what": (
            "A dark cloud marks a spot and fills it with a group of enemies "
            "-- crows, dogs, revenants, trolls, knights, Fingercreepers, "
            "Golem Warriors, depending on the roll."
        ),
        "reward": "Runes and a buff improving Ultimate Art gauge charge speed.",
        "penalty": "None reported.",
        "nightlords": ["Gladius", "Maris", "Fulghor"],
        "sources": ["fextralife", "eldenpedia"],
    },
    11180: {
        "name": "Flame of Frenzy",
        "what": (
            "Frenzied villagers channel an eye of frenzy above a ruined "
            "tower. Kill all of them, avoiding line of sight, which builds "
            "Madness."
        ),
        "reward": (
            "Two reward orbs; reported as a buff of your choice and a frenzy "
            "weapon of your choice, such as the Frenzied Flame Seal or "
            "Vyke's War Spear."
        ),
        "penalty": "Madness builds the longer you stay in the area looking at it.",
        "nightlords": ["Gnoster", "Libra", "Harmonia"],
        "note": "Widely reported as one of the rarest events in the game.",
        "sources": ["fextralife", "eldenpedia"],
    },
    110000: {
        "buff_id": 8970050,
        "name": "Fire-Summoning Beasts",
        "what": (
            "A Scorching debuff drains the team's HP while Fire Spirit Wolves "
            "and a Sundered Tricephalos hold three marked areas. Clearing all "
            "three ends it."
        ),
        "reward": "The Beast's Hunt buff, and the Scorching debuff is removed.",
        "penalty": "Continuous HP drain from Scorching until the areas are cleared.",
        "nightlords": ["Gladius"],
        "sources": ["fextralife"],
    },
    110050: {
        "buff_id": 8970060,
        "name": "Judgment / the Balancers",
        "what": (
            "Half the team's Sacred Flask charges vanish and weakened "
            "Balancers appear. Defeat them to get the charges back."
        ),
        "reward": "All flask charges restored, plus the Power to Balance the World buff.",
        "penalty": "Half your flask charges for as long as the event runs.",
        "nightlords": ["Any"],
        "sources": ["fextralife"],
    },
    110200: {
        "buff_id": 8970040,
        "name": "Blizzard",
        "what": (
            "A red circle marks a dragon. Attack it to drive it off."
        ),
        "reward": "The Cold Mirage effect -- concealment near death, neutralising attacks.",
        "penalty": "None reported.",
        "nightlords": [],
        "sources": ["fextralife"],
    },
}


# Things players call world events that the game never announces, so they have
# no display-log row and cannot appear in the extracted roster. They are worth
# listing anyway -- the Wandering Mausoleum in particular is a real, findable
# thing on the map, it simply arrives without a banner.
UNANNOUNCED: list[dict] = [
    {
        "name": "Wandering Mausoleum",
        "what": (
            "A walking structure with a bell slung between its legs. Climb a "
            "leg to reach the bell inside. It is only a duplicator -- there "
            "is no fight and nothing to fail."
        ),
        "reward": "Duplicates one armament you already hold, up to Legendary.",
        "penalty": "None.",
        "nightlords": ["Maris", "Caligo"],
        "sources": ["fextralife", "eldenpedia", "game8"],
    },
    {
        "name": "Scale-Bearing Merchant",
        "what": (
            "A grey-coated merchant offering wishes whose downsides are "
            "stated up front. Attacking it starts the demon fight instead."
        ),
        "reward": "Stat boosts, flask charges, runes, or a powerful weapon.",
        "penalty": "Each wish carries its own cost -- stats, HP, or levels.",
        "nightlords": [],
        "sources": ["fextralife", "game8"],
    },
    {
        "name": "Cataclysm",
        "what": (
            "Marked at expedition start rather than partway through. Enemies "
            "gain HP and damage, and AI Nightfarers (the Condemned) appear."
        ),
        "reward": "Runes and Dormant Powers; the Condemned drop a +2 starter weapon.",
        "penalty": "None beyond the tougher enemies.",
        "nightlords": ["Any"],
        "sources": ["fextralife", "game8"],
    },
]
