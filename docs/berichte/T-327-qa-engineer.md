# T-327c qa-engineer — Pruefphase A27 (Weapon art / Spell damage) und Retest QA-293

**STATUS: fertig** — Quellstand geprueft, ein Fensterlauf, zwei neue Befunde
(P4), QA-293 am Fenster bestaetigt.

## Kontraktblock

| Feld | Wert |
|---|---|
| Geprueft | `b286bc0` (Merge `5a35272`: A27 `7d1e216` + QA-293-Fix `46a7e58`), Arbeitsbaum sauber |
| Suite | `pytest -n auto`: **1892 passed, 9 skipped** in 69,8 s (21.09.2026, eigener Lauf) |
| Umlenkung | `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-327c`, `LOCALAPPDATA`/`APPDATA` im Scratchpad, Testabzug v16 (841 Dateien) hineinkopiert; positiv belegt: `paths.cache_dir()` zeigt in das Testverzeichnis, `snapshot_path().is_file()` True |
| Fensterlauf | **einer** (Quellstand `python run.py`, Titel `Nightreign Helper 1.17.0`, Stufe 15, echter Spielstand 319 Relikte), UIA + echte Mausklicks ueber `scripts/drive_window.ps1` |
| NH-004 | vor dem Lauf `Get-Process NightreignHelper` = 0, nach dem Lauf = 0 (`tasklist`-Filter auf nightreign: 0 Zeilen); Registry-Zweig `HKCU\Software\DankYeeterT-327c` geloescht (`Test-Path` danach False) |
| Urteil | **CONCERNS** |

Der Fensterlauf lief am Quellcode, nicht am Artefakt: A27 ist noch nicht
gebaut (1.18.0 steht aus), und `git status` war sauber.

## Nachweis je Teilsatz des Auftrags (alles am Fenster abgelesen)

| Pruefpunkt | abgelesene Zeile | Urteil |
|---|---|---|
| Revenant + Grand Drizzly Scene (7370900) | `Spell damage (Beast Claw) 577 no change 577` | erfuellt, Zahl 577 statt 578 (QA-296) |
| Physical-Relikt bewegt beide Zeilen | `Total 88 1H / 68 2H +1 90 1H / 69 2H (+1.5%)` und `Spell damage (Beast Claw) 577 +29 606` | erfuellt |
| Reihenfolge AK-364 | `Physical` / `Magic` / `Total` / `Weapon art` / `Spell damage (Beast Claw)` / `Rally recovery` / Fussnote | erfuellt |
| Klick auf den Zauberwert (AK-361) | Klick auf den fetten Endwert oeffnet den Tooltip: `Spell damage — Beast Claw`, `Base 577`, `Physical Attack +5.0%`, `Physical Attack Up +1 +5.0%`, `Spell damage 606`, `Spell damage is uncalibrated: ...` (Bildnachweis per `PrintWindow`, Scratchpad) | erfuellt |
| Wylder `Weapon art` | `Weapon art 122 1H / 125 2H no change 122 1H / 125 2H`, keine Zauberzeile | erfuellt |
| Skill-Buff bewegt nur die Kunstzeile | mit `The Will of the Balancers` (Improved Melee + Improved Skill Attack Power): `Total 122 +7 129 (+6.0%)`, `Weapon art 129 +19 148` — die Grundlinie der Kunstzeile ist der Gesamtwert, die Differenz traegt allein der Skill-Faktor; Gegenprobe Revenant mit Physical-Relikt: `Weapon art 90 no change 90` | erfuellt |
| Recluse Katalysator-Satz (AK-356) | `Spell power 135 no change 135`, `Weapon art - not shown: a staff or a seal is ranked on the spell power the game shows for it, and no attack art reaches that figure.`, `Spell damage (Glintstone Pebble) 206 no change 206` | erfuellt |
| Guardian ohne Zauberzeile (AK-358) | `Physical`, `Total`, `Weapon art 107 1H / 110 2H no change`, `Rally recovery` — keine Zauberzeile | erfuellt |
| Revenant ohne Relikt (AK-360) | `Spell damage (Rejection) 0 no change 0` | erfuellt |
| Zweihand-Schalter (AK-359) | `HandSwitch` Off/`1H` → On/`2H` (UIA-ToggleState belegt): `Weapon art 90 1H / 69 2H no change 90 1H / 69 2H`, `Spell damage (Beast Claw) 577 +29 606` in beiden Stellungen unveraendert und ohne Zweihand-Zwilling | erfuellt |
| QA-293 am Fenster | Revenant, Slots leer, `Hit with = Bestial`, `Optimize` → Slot 1 `Grand Drizzly Scene`: `Improved Fundamentalist Incantations: +12.0% - this figure does not count it.` und `Changes compatible armament's incantation to Beast Claw at start of expedition: Spell damage (Beast Claw) +755` | behoben |

## Befunde

### [P4 | Minor | Mittel] Die Differenz der Zeile `Weapon art` ist kein Link, AK-355 verlangt einen

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/statsheet.py:584` `_weapon_art_row`; Vorgabe `UI_SPEC.md` AK-355
**Umgebung:** Quellstand, Fenster, Revenant/Wylder, Stufe 15

**Reproduktion:**
1. Fenster oeffnen, Wylder, Stufe 15, ein Relikt mit Skill-Buff in Slot 1.
2. Mauszeiger ueber die Zahlen der Tafel fuehren (Zeigerform `IDC_HAND` je
   Bildpunkt abgefragt, Raster 8 x 4 px ueber der ganzen Tafel).

**Erwartet:** AK-355 ("grauer Wert, farbiger Link mit der Differenz, fetter
Endwert") — dieselbe Form wie die Gesamtzeile.
**Tatsaechlich:** Hand-Zeiger nur auf zwei Flaechen: Gesamtzeile
(x 4262..4278, y 1528..1544) und fetter Zauberwert (x 4366..4382,
y 1568..1584). Die Kunstzeile traegt keinen Klickbereich; ihre Differenz ist
gefaerbter Text.

**Analyse:** Der `developer` hat die Abweichung im Baubericht offengelegt und
begruendet (AK-361 nennt nur *einen* zweiten Link-Schluessel, fuer einen
dritten Tooltip gibt es keinen vorgegebenen Inhalt; ein Link auf die
AR-Aufschluesselung zeigte die Zahl ohne den Kunstfaktor). Die Vorgabe ist
damit nicht eingeloest, der Grund ist nachvollziehbar — zu entscheiden ist,
ob AK-355 nachgezogen wird oder die Zeile einen eigenen Tooltipinhalt
bekommt.

**Auswirkung:** Kein falscher Wert, keine Fehlbedienung; die Zeile bietet nur
keinen Weg zu ihrer Herkunft. Zwei Klickflaechen statt drei in einer Tafel,
die sonst jede Zahl aufschluesselt.

**Vorschlag:** Entweder AK-355 auf "gefaerbter Text ohne Link" nachziehen (und
den Grund dort festhalten), oder eine eigene AK mit Tooltipinhalt fuer die
Kunstzeile (Grundlinie = Gesamtwert, Kunstfaktor, Endwert).

### [P4 | Minor | Hoch] Nachweiszeile GOAL A27 nicht woertlich einloesbar (578 / "(uncalibrated)")

**Adressat:** director
**Betroffen:** `GOAL.md` A27, Nachweisabsatz; Verhalten nach `UI_SPEC.md`
AK-359/AK-361
**Umgebung:** Quellstand, Fenster, Revenant + 7370900, Stufe 15

**Reproduktion:**
1. Revenant, Stufe 15, `Grand Drizzly Scene` (7370900) in Slot 1.
2. Zeile im Schadensblock lesen.

**Erwartet (GOAL-Wortlaut):** `Spell damage (Beast Claw) 578 (uncalibrated)`.
**Tatsaechlich:** `Spell damage (Beast Claw) 577 no change 577`; der
Unkalibriert-Satz steht im Klick-Tooltip, nicht in der Zeile.

**Analyse:** Zwei Abweichungen, beide ohne Rechenfehler. 577 statt 578 ist die
Abschneidung von 577,55 durch `damage.displayed` (dieselbe Regel, der jede
andere Zahl der Tafel folgt). Der fehlende Klammerzusatz ist die ratifizierte
Entscheidung AK-361 (Tooltip statt Dauertext). Derselbe Fall wie QA-291: der
GOAL-Satz stammt aus der Zeit vor der Spezifikation.

**Auswirkung:** Fuer Nutzer keine; fuer die Abnahme, weil das Kriterium
woertlich zitiert wird und so nicht abhakbar ist.

**Vorschlag:** GOAL-Wortlaut nachziehen (577, Hinweis "unkalibriert im
Tooltip, AK-361"), kein Codefix.

## Retest QA-293

**behoben.** Der Fix `46a7e58` ist am Fenster belegt (Zeile oben): unter der
Schulwahl `Bestial` nennt die Why-Karte den Tauschzauber als bewegten Effekt
mit eigener Zahl, der Schulbuff steht mit dem Satz "this figure does not count
it." daneben. Gezielt gruen: `tests/test_advisor_explain.py`, darunter
`test_a_school_mismatched_buff_does_not_steal_the_swaps_line` (in der
Sammelsuite mitgelaufen). QA-294 bleibt zurueckgestellt (Director-Entscheid
21.09., nicht Teil dieses Laufs).

## Beobachtungen (kein Befund, keine Nummer)

- Die Kopfzeile der Why-Gruppe zaehlt den nicht gewerteten Schulbuff mit
  ("2 of its 3 effects moved a number in this build.", waehrend eine der
  beiden Zeilen sagt, dass die Zahl nicht zaehlt) — dieselbe Zaehlweise, die
  `_count_line` seit je fuer Fluchzeilen hat, durch den Fix nicht veraendert.
- Vorbestand, von A27 unberuehrt: in den Zeilen `Physical`/`Total` koennen
  Differenz und angezeigte Zahlen um 1 auseinanderfallen
  (`Physical 17 1H / 13 2H +1 17 1H / 13 2H`, `Total 88 +1 90`), weil die
  Differenz ungerundet gebildet und die Zahlen abgeschnitten werden; der Diff
  `7d1e216` fasst diese Schleife nicht an.
- Der Picker-Kopf zeigt unter einer Schulwahl den QA-289-Fix im Betrieb:
  `Nothing you own raises damage in this slot. (Bestial)`.

## Explorationsprotokoll

Suite vollstaendig (ein Lauf, `-n auto`). Am Fenster: vier Nightfarer (Wylder,
Revenant, Recluse, Guardian) mit leeren Slots gelesen; Relikte ueber den
echten Picker gesetzt (Klick auf die Kachelschaltflaeche, Suche, Klick auf die
Karte), Stufe ueber den Schieber auf 15; Hand-Schalter ueber UIA-Toggle mit
Zustandsbeleg; Klickflaechen ueber die Zeigerform gesucht statt geraten;
Tooltip als Bild ueber `PrintWindow` auf das Tooltipfenster (Klasse
`...QWindowToolTipDropShadowSaveBits`). Zauberzeile in drei Zustaenden (ohne
Relikt, mit Tauschrelikt, mit Tauschrelikt + Angriffsrelikt). Gehalten hat
alles ausser den beiden gemeldeten Punkten.

## Offene Fragen

- An den `ui-ux-designer`: soll die Why-Kopfzeile einen Effekt mitzaehlen,
  dessen eigene Zeile sagt, dass seine Zahl nicht gewertet wird? (Betrifft
  Fluchzeilen genauso, waere also eine Aenderung am Bestand.)

## Nicht getestet

- Artefakt 1.18.0 (noch nicht gebaut) — die Zeilen sind nur am Quellstand
  belegt.
- AK-353 Punkt 3 (Startwaffe auf eine andere Kachel geschoben, gefundene Waffe
  in Slot 3, Siegel von Hand auf eine Kachel gelegt): durch
  `tests/test_stat_sheet_art_and_spell.py` abgedeckt, am Fenster aus
  Zeitgruenden ausgelassen.
- Schmale Fensterbreiten mit dem laengeren Block (DR-028/AK-351) — der
  `developer` nennt sie gruen, aber nur mit Wylder; ein Breitenlauf gehoert in
  die naechste Messrunde.
- Zwei gleichzeitige Tauschrelikte (AK-360, zweiter Absatz).
