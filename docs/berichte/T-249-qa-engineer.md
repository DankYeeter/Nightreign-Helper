# T-249 -- Retest der seit `1b36238` gebauten Fixes (qa-engineer)

Datum 14.09.2026, Quellstand `dde2efc` (Version 1.10.1), Arbeitsbaum vor
Beginn sauber. Geaendert in diesem Auftrag: dieser Bericht, `qa/findings.md`
(nur angehaengt), `scripts/differential/mutate.py` (drei bestaetigt tote
Mutationen geloescht, OF-35).

## Suite

`pytest -n auto`: 1563 passed, 9 skipped, **1 fail**
(`test_the_waiting_state_is_a_state_and_not_a_nothing`). Isoliert
(`pytest tests/test_save_read_in_the_background.py`): 26/26 gruen -- die
bekannte xdist-Querkontamination (ein Worker laesst einen modalen
`RelicPicker` aus einem anderen Test offen, den `activeModalWidget()` in
diesem Test dann sieht), keine neue Regression. Gezielt vorab gruen (32
Faelle): `test_attack_power_calibration_against_the_game.py`,
`test_damage_conversion_against_the_game.py`, `test_search.py`,
`test_relic_picker_geometry.py`.

## QA-096 / QA-097 (Raider-Waffen, Revenant's Cursed Claws)

`weapons.nightfarer_calibration` traegt `RAIDER_HEAVY_ARMAMENT_RATE = 1.18`
und `BORROWED_CURSED_CLAWS_RATE = 0.88`. Rot-vorher je Mutation am
`git archive dde2efc`-Klon: `raider-heavy-armament-rate-neutralised` toetet
3 Faelle (Raider-Great-Stars-Zeile, Faktor-Test, Popup-Text-Test),
`borrowed-cursed-claws-rate-neutralised` toetet 2 (Wylder/Claws-Zeile,
Faktor-Test) -- beide wie in `survival_means` vorhergesagt. **Bestaetigt.**

## QA-113 (Startwaffen-Elementumwandlung, Fall 3)

`nrplanner/damage.py`: Wylder 123, Revenant 91, Duchess 74 -- alle drei
Ingame-Messpunkte, Aufschluesselung trennt Phys/Element. Rot-vorher
`damage-type-conversion-ignored`: 4 Faelle rot (drei Helden-Zeilen plus
Breakdown-Test). **Bestaetigt.**

Mutationsregistrierung: alle drei Mutationen liefen wie vorhergesagt rot,
danach aus `MUTATIONS` entfernt (OF-35). `exclusive-group-counts-every-copy`
(QA-257) bleibt stehen -- nicht Teil dieses Auftrags.

## QA-260 (`Why` je Vorschlagskarte)

`tests/test_advisor_block.py::test_the_cards_why_opens_the_same_dialog_as_the_bars`
und `::test_the_cards_why_follows_the_bars_own_gate` gruen: die Karte oeffnet
denselben `WhyDialog` wie die Leiste und folgt derselben
Sichtbarkeitsregel (`ACTING_STATES`). **Bestaetigt** ueber Testkoerper, kein
Fensterlauf noetig.

## QA-262 (Kartenbreite)

`test_relic_picker_geometry.py` gruen; `_measure_card_width()` liefert lokal
208 px, wie im Fix-Bericht. **Lokal bestaetigt** -- der CI-Nachweis auf
`windows-latest` bleibt offen, dieser Auftrag hat nichts gepusht.

## QA-263 / QA-264 / QA-265 (Relic-picker-Suche)

`test_search.py` haelt explizit fest, dass die Treffer-Zahlen "qa-engineer's
to reconfirm" sind. Nachgefahren mit der frozen 314-Kopien-Grundlage aus
`tests/data/frozen_inventory.json` (T-244), echtes `RelicSlot`/`RelicPicker`
offscreen (Skript im Scratchpad, `nrplanner`-Code unveraendert):

| Query | Slot | Treffer | Vorher (T-244) |
|---|---|---|---|
| `but not for self` | weiss, Basis | 4 of 208 | 0 of 210 |
| `-afflicted` (roh) | weiss, Basis | 204 of 208 (4 ausgeblendet) | 206 von 210 |
| `"-afflicted"` (Zitat) | weiss, Basis | 4 of 208 | -- |
| `All Resistances Down` | weiss, Deep | 3 of 103 | 0 of 104 |

Zahlen decken sich mit dem Auftrag (Denominator 208/103 statt 210/104 --
314 statt 315 Kopien in der eingefrorenen Grundlage, ein Relikt weniger,
kein Befund). Das rohe `-afflicted` bleibt bewusst NOT (Nutzerentscheid
T-245: fuehrendes `-` bleibt Operator, Zitieren ist der Workaround) -- genau
das Verhalten, das der Auftrag als "NOT gross weiter Operator" nennt.
QA-265: Platzhalter `Filter by effect — supports AND, OR, NOT and "quoted
phrases"` steht in `relicpicker.py:1087`, wortgleich zum Weapons-Feld.

**Alle drei bestaetigt, geschlossen.**

## Nicht getestet

- CI-Lauf zu QA-262 (kein Push in diesem Auftrag).
- Kein UIA-Fensterlauf der echten EXE -- die Offscreen-Nachfahrung mit
  echten Produktionsklassen (`RelicSlot`, `RelicPicker`, echte
  Reliktdaten) traf dieselben Zahlen wie der Auftrag nennt; ein
  zusaetzlicher Klicklauf haette denselben Code elektiv nochmal gezeigt.
- Volle Neupruefung der uebrigen `qa/findings.md`-Eintraege (nicht
  Gegenstand dieses Retests).

## Zusammenfassung

Kontraktblock:

| ID | Ergebnis |
|---|---|
| QA-096 | bestaetigt, geschlossen (Mutation getoetet + geloescht) |
| QA-097 | bestaetigt, geschlossen (Mutation getoetet + geloescht) |
| QA-113 | bestaetigt, geschlossen (Mutation getoetet + geloescht) |
| QA-260 | bestaetigt, geschlossen |
| QA-262 | lokal bestaetigt -- CI-Nachweis offen (nicht P1/P2-blockierend) |
| QA-263 | bestaetigt am eingefrorenen Save, geschlossen |
| QA-264 | bestaetigt am eingefrorenen Save, geschlossen |
| QA-265 | bestaetigt, geschlossen |

Keine neuen P1/P2-Befunde. Die eine `-n auto`-Fehlschlagzeile ist bekannte
xdist-Querkontamination (isoliert gruen), kein neuer Befund.

**PASS**
