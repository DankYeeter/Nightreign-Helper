# T-335h -- Nachtest QA-308 (qa-engineer, 28.10.2026)

Stand `ccfe528`. Fensterlauf `python run.py` aus dem Quellbaum, Treiber
`scripts/drive_window.ps1` mit PID-Kopie im Scratchpad, Org
`DankYeeterT-335h`, `LOCALAPPDATA`/`APPDATA` im Scratchpad, Testabzug kopiert.
Vor dem Start keine `NightreignHelper.exe`; am Ende kein Fenster offen.

**Urteil: PASS** -- QA-308 behoben, QA-305 haelt, alle sieben freigegebenen
Dialoge liefern ihr Ergebnis. Neu nur QA-309 (P4, Treiberluecke, kein
Programmfehler).

Suite `pytest -n auto` an `ccfe528`: **2086 passed, 9 skipped** (146,3 s).

## Pruefpunkte

| Punkt | Ergebnis |
|---|---|
| 1 Speicher | 20 Armament-Oeffnungen mit Cancel: 207,6 -> 227,1 MB, weitere 20: 227,4 -> 231,2 MB privat (T-335g: 348 -> 1012 MB). Offscreen 20 Oeffnungen: 134 -> 179 -> 206 -> 206 -> 208 MB, lebende `WeaponDialog` bleiben bei 1 (der zuletzt geschlossene, freigegeben beim naechsten Ereignisdurchlauf) |
| 2 QA-305 | 5/5: Unarmed OK (Maus), Finger Seal 34750000 Cancel (UIA), Wylder's Small Shield OK (UIA), Scholar's Thrusting Sword 5760000 Cancel (Maus), Guardian's Greatshield OK (Maus); jeweils vorher Academy Staff mit 66 Kaesten |
| 3 Armament | Waffe auf der Kachel (siehe Punkt 2) |
| 3 Relikt-Auswahl | Karte gewaehlt -> Slot 1 "Delicate Drizzly Scene" |
| 3 Custom relic | ein Effekt, "Use this relic" -> Slot 2 "Custom relic / Attack power increased for each Night Invader defeated" |
| 3 Favoriten-Menue | Rechtsklick auf Karte, Wylder angeklickt -> Registry `favourites\1010\|7120000\|` = 1; Esc, Picker lebt |
| 3 Effektfilter | Avoid "[Revenant] Power up while fighting alongside family" -> `advisor\excluded` 7220000; naechste Optimize-Antwort: Slot 1 wechselt von Grand zu Delicate Drizzly Scene, Why fuehrt den Effekt nur unter "Effects you've avoided". Zweites Fenster nimmt die Marke zurueck (`excluded` leer) |
| 3 Why | Fenster mit Inhalt, Close; keine Markierknoepfe mehr in den Zeilen, also nichts zu uebernehmen |
| 3 Neustart-Frage | 110 % -> Later: `ui\scale` 1.1, Programm laeuft; 125 % -> Restart now: alter Prozess endet, neuer startet, `ui\scale` 1.25 |

stderr des Laufs: nur `0x8001010d` (UIA-Rauschen), kein Traceback.

## Befunde

### QA-309 [P4 | Minor | Niedrig] Treiber: `Press` haengt an einem QToolButton, der einen modalen Dialog oeffnet

**Adressat:** developer
**Betroffen:** `scripts/drive_window.ps1` `Press` (UIA Invoke)

**Reproduktion:**
1. Relikt-Auswahl eines Slots oeffnen.
2. `Press` auf die Karte "+" (QToolButton, oeffnet Custom relic).

**Erwartet:** Der Aufruf kehrt zurueck, der Dialog ist offen.
**Tatsaechlich:** Der Dialog ist offen, das Treiberskript haengt (ueber 3 min,
dann abgebrochen); danach liefert UIA in diesem Dialog 0 Elemente. Ein
`QPushButton`, der einen Dialog oeffnet (Why, Filters), haelt.

**Analyse (Hypothese):** Fuer einen QToolButton klickt Qt synchron, fuer einen
QPushButton zeitversetzt. Darum kehrt Invoke erst zurueck, wenn die
Modalschleife endet.

**Vorschlag:** Im Treiber eine gepostete Mausnachricht anbieten (wie
`PostClick` in `scratchpad/T-335h/combo.ps1`), oder `Press` warnen lassen.
Das Programm selbst ist nicht betroffen.

## Nicht getestet

- Exe (entsteht nach dem letzten Fix, NH-010).
- Speicher der uebrigen sechs Dialoge ueber viele Oeffnungen; der
  Regressionstest des developers deckt die Freigabe ab, gemessen habe ich nur
  den Armament-Dialog.

## Beobachtungen

- Der echte Doppelklick oeffnete die Kachel im ersten Speicherlauf nach 8
  Oeffnungen nicht mehr (der Nutzer war an der Maschine, Zeiger woanders);
  der Lauf wurde verworfen, mit Wiederholung gingen danach 40 von 40.
