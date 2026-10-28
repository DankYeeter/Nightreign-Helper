# T-335g -- Nachtest QA-305/306/307 (qa-engineer, 28.10.2026)

Stand `0123ce5` (Fixes `b647c6c`, `ff46e96`, `0123ce5`). Fensterlauf
`python run.py` aus dem Quellbaum, Treiber `scripts/drive_window.ps1` mit
PID-Kopie im Scratchpad, Org `DankYeeterT-335g`, `LOCALAPPDATA`/`APPDATA` im
Scratchpad, Testabzug kopiert (`EXTRACT_VERSION` 16). Vor dem Start keine
`NightreignHelper.exe` (tasklist 21:23), nach dem Lauf Fenster geschlossen.

**Urteil: CONCERNS** -- QA-305, QA-306, QA-307 behoben. Neu QA-308 (P3,
Speicher waechst je geoeffnetem Armament-Dialog, schon seit dem ersten Stand,
kein Rueckschritt). Der `director` entscheidet, ob QA-308 vor dem Release
behoben wird.

Suite `pytest -n auto` an `0123ce5`: **2080 passed, 9 skipped** (151,6 s).

## Retest

| Befund | Urteil | Beleg |
|---|---|---|
| QA-305 | behoben | 13 Faelle am Fenster: Kachel erst auf Academy Glintstone Staff (66 Effektkaesten), dann Unarmed, Wylder's Small Shield, Finger Seal 34750000, Guardian's Greatshield, Scholar's Thrusting Sword 5760000/5770000/5780000 (0 Kaesten), OK und Cancel per Maus und UIA: Prozess lebt 13/13, Kachel traegt die Waffe bzw. bleibt leer. Umfeld: 2 Kaesten angehakt, dann Unarmed OK/Cancel; Unarmed -> Caestus OK (79 Kaesten, keiner uebernommen) -- haelt. stderr nur UIA-Rauschen `0x8001010d` |
| QA-306 | behoben | Raider, Academy Staff auf Kachel 2, Sorceries/Fire: Warnzeile im neuen Wortlaut, ganz sichtbar bei 2448 px (2 Zeilen) und 1487 px (4 Zeilen, 80 px; "Open a slot"-Zeile und Slot 1 darunter, nichts ueberdeckt). Magic: Why-Umfang "... on the staff or seal on the selected tile, or else the starting one — never on a spell picked up in a run." Suche "starting equipment"/"starts an expedition" in `nrplanner/`: 1 Treffer, `statsheet.py:791`, Kommentar zur Weapon-art-Zeile, richtig |
| QA-307 | behoben | `guide.md:128-130` stimmt: Tafel `Spell damage (Glintstone Pebble)` Common 144, Legendary +3 208 (Fenster); Berater auf `weapons.MIN_UPGRADE` (`goals.py:457`). Die Beraterzahl selbst zeigt das Fenster nicht; verlassen auf T-335e (331 auf allen vier Stufen), Pfad seither nur im Wortlaut geaendert |

## Befunde

### QA-308 [P3 | Major | Mittel] Armament-Dialog bleibt nach jedem Oeffnen im Speicher

**Adressat:** developer
**Betroffen:** `nrplanner/app.py:1462` `_edit_weapon_slot`
**Umgebung:** jede Nightfarer-Wahl; Stand `0123ce5` und `b33a71e`

**Reproduktion:**
1. Programm starten, eine Waffenkachel doppelklicken, Cancel.
2. Schritt 1 zwanzigmal wiederholen.

**Erwartet:** Speicher nach dem Schliessen etwa wie vorher.
**Tatsaechlich:** Fenster 348 -> 1012 MB privat nach 20 Oeffnungen.
Offscreen (`leak2.py`, 10 Oeffnungen per `reject`): 134 -> 296 -> 454 MB,
nach jeder Oeffnung ein `WeaponDialog` mehr am Leben (10 nach 10), rund
32 MB je Oeffnung; gleiche Zahlen an `b33a71e`.

**Analyse:** Der Dialog hat den Planner als Eltern und wird nach `exec()`
nie geloescht; der developer hat das in T-335f als Schuld genannt. Die
Funktion ist seit `cec61c7` (10.08.2026) unveraendert, der Fehler steckt
also vermutlich in allen Releases (geschlossen aus der Codegeschichte, nicht
an alten Staenden gemessen).

**Auswirkung:** Der Speicherbedarf waechst ohne Grenze, solange das Programm
laeuft; 100 Oeffnungen waeren rund 3 GB. Keine falsche Funktion gemessen;
ein Neustart gibt den Speicher frei.

**Vorschlag:** Den Dialog nach `exec()` freigeben. Der Waechter fuer QA-305
(`test_weapon_dialog_teardown.py`) und ein Fensterlauf mit einer Waffe ohne
Effekte gehoeren zum Fix, weil QA-305 genau an der Lebensdauer dieses
Dialogs hing.

P3 statt P2: der Fehler ist alt, schadet in einer ueblichen Sitzung kaum,
und ein Neustart hilft.

## Explorationsprotokoll

- Fenster: 17 Dialoglaeufe (13 Waffen ohne Effekte, 1 mit Effekten, 3 im
  Umfeld), Warnzeile bei zwei Breiten mit Bild (`shots/warn-1487.png`),
  Stufenwechsel Common/Legendary, 20 Dialogoeffnungen mit Speichermessung.
- Offscreen: Speicher und lebende Dialoge an `0123ce5` und `b33a71e`
  (git-archive-Klon).
- Abbau-Stellen in `nrplanner/` angesehen (`deleteLater`): `app.py:145` und
  `statsheet.py:890` sitzen in Hauptfenster-Widgets, nicht in Modaldialogen;
  die Suche des developers bestaetigt.
- Treiber: Doppelklick per `PostMessage` oeffnete die Kachel nach dem ersten
  echten Mausklick nicht mehr; ein echter Doppelklick mit PID-Waechter ging.
  Liegt am Treiber, nicht am Programm.

## Nicht getestet

- Exe: das Artefakt entsteht erst nach dem letzten Fix (NH-010).
- Speicherverlauf ueber 20 Oeffnungen hinaus, und alte Releases gemessen.

## Beobachtungen

- Why fuehrt neben dem neuen Zaubersatz weiter "Scaled on the Nightfarer's own
  starting armament at its lowest tier"; fuer Waffe und Weapon Art stimmt das,
  ein Leser kann es auf Zauber beziehen.
- Die Register-Waechtertests (10 passed) liefen einmal ohne
  `LOCALAPPDATA`-Umlenkung; sie lesen nur Dateien im Repo.
