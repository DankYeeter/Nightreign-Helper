# T-272 -- Retest am Artefakt 1.12.2 (qa-engineer, 15.09.2026)

Artefakt `dist/NightreignHelper.exe`, SHA-256 `72795285...7abcf`
(59 120 312 B, Commit `fb23e24`) -- Hash und Groesse vor Testbeginn geprueft,
stimmen mit dem Auftrag ueberein. Umlenkung durchgaengig
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-272qa`, `LOCALAPPDATA`/`APPDATA` auf
eigene Scratch-Verzeichnisse.

## Risiko-Briefing

Fuenf Pruefpunkte, priorisiert: (1) der v11→v12-Cache-Neubau ist der einzige
Pfad, der den Extraktor am echten Spiel anfasst -- Fehlschlag waere ein
Blocker fuer jeden weiteren Punkt, deshalb zuerst. (2) QA-276 (Paarwaffen-
Zweihandfaktor) ist eine Modelrechnung mit sieben harten Zahlen -- am
groessten das Risiko einer verwechselten Zelle. (3) QA-258 ist eine
Performance-Regression mit Hintergrund-`QTimer`: genau dort, wo ein
Nachbau mit einer Nutzeraktion waehrend der Fuellung kollidieren kann, habe
ich das Risiko am hoechsten eingeschaetzt und darum gezielt adversarial
getestet, nicht nur die Median-Zahl nachgemessen. (4) AN-5 ist eine reine
Anzeige-Erweiterung, geringes Risiko. (5) A18/A20-Persistenz zuletzt, weil
dieser Zyklus keine Aenderung an den Persistenzpfaden traegt (siehe unten).

## 1 -- Cache-Neubau v11 → v12

Echten Nutzer-Cache (`%LOCALAPPDATA%\NightreignHelper`, geprueft
`extract_version: 11`, 1793 Waffen ohne `paired`-Feld, 841 Dateien,
20 812 293 B) in die Umlenkung kopiert, Artefakt gestartet. Neubau lief ohne
Fehler im Log, Dauer ca. 35 s (nur `nightreign_data.json` neu geschrieben,
Symbole blieben -- deckt sich mit T-269a). Ergebnis geprueft:
`extract_version: 12`, 1793 Waffen, 79 mit `paired: true` (45 Fist + 32 Claw
+ Ornamental Straight Sword + Starscourge Greatsword). Fenster zeigt danach
reale Zahlen (313 Relikte aus dem echten Save, „Weapons (1788)“ im
Arsenal-Tab, Wylders Greatsword-Kachel `122 / 125 2H`).

## 2 -- QA-276 (Zweihand-Paarwaffen-Faktor)

`tests/test_attack_power_calibration_against_the_game.py` (38/38 gruen)
laeuft gegen dieselbe echte Extraktion (`game_data`-Fixture liest das
installierte Spiel/den Cache, kein Mock) und deckt alle im Auftrag genannten
Zellen exakt ab, inkl. Raider Twinblade 99/49 und Revenant Hookclaws 59/46.
Live am Fenster nachgestellt (Wylder, Level 15 per Slider, Slot mit
Hookclaws bestueckt ueber den Arsenal-Picker): Statsheet zeigt
`Physical 80 / 62 2H - 80 / 62 2H`, Waffenkachel `Common · 80 / 62 2H AR` --
deckungsgleich mit der Aufgabe. Die Popup-Faktornennung (A7) selbst wurde
nicht per Klick am Fenster nachgestellt (kein stabiler UIA-Zugriff auf den
Qt-Rich-Text-Link ohne Pixelsuche gefunden); dafuer steht
`test_the_shape_of_the_armament_names_the_factor_before_the_nightfarer`
(gruen), das exakt den Text "two-handing a pair" fuer Wylder+Hookclaws-Fall
gegenprueft. **Befund:** behoben, Retest bestanden.

## 3 -- QA-258 und eine neue Regression (QA-277)

Sichtbarkeit bestaetigt: am weissen Slot 3 (Wylder's Chalice, Deep an, 209
Kandidaten) ist der Dialog per UIA-Polling deutlich vor der vollen
Kartenzahl da (bei Erstlesung schon Karten vorhanden, aber < 209; volle
209/209 erst spuerbar spaeter) -- die externe UIA-Abfrage selbst kostet
genug Overhead, dass ich keine belastbare ms-Zahl gegen die
Entwickler-Median-Angabe (115 ms) stelle; qualitativ haelt der Effekt.
`tests/test_relic_picker_advisor.py` 83/83 gruen.

Beim geforderten Adversarial-Test **"Filter tippen waehrend Fuellung"**
brach die Fuellung reproduzierbar (2/2): Slot 3 geoeffnet, sofort "attack"
in den Filter getippt (< 1 s nach Sichtbarkeit, Hintergrund-Nachbau lief
nachweislich noch). Ergebnis siehe Befund unten. **Sortwechsel waehrend
Fuellung** wurde versucht, landete aber zeitlich nach Abschluss der Fuellung
(209/209 bereits gebaut) -- kein Beleg in beide Richtungen, nicht erneut
versucht (Zeitbudget). **Rescan waehrend Fuellung** nicht mehr erreicht
(Zeitbudget) -- nicht getestet, siehe unten.

### [P1 | Major | Hoch] Picker-Fuellung bricht bei Filtereingabe waehrend des Nachbaus (QA-277, Regression von QA-258)

**Adressat:** developer
**Betroffen:** `nrplanner/relicpicker.py:1631` (`_paint_more`),
`nrplanner/relicpicker.py:1529` (`_refresh`), Cache `self._card_cache`
(Zeile 1084/1624/1627)
**Umgebung:** Artefakt 1.12.2, Wylder, Wylder's Chalice, Deep of Night an,
Slot 3 (weiss, 209 Kandidaten), Umlenkung `DankYeeterT-272qa`

**Reproduktion:**
1. Slot 3 (leer oder belegt) anklicken -- Picker-Dialog oeffnet.
2. Sofort (< 1 s, waehrend der Hintergrund-Nachbau der restlichen Karten
   noch laeuft) in das Filterfeld "attack" tippen.
3. Ergebnis abwarten (500 ms+).

**Erwartet:** Der Filter greift, das Raster zeigt alle 106 passenden
Karten (laut Kopfzeile "106 of 209 relics matching 'attack'"), so wie
`_refresh()`s Kommentar es verspricht ("ein Tastendruck im Filter [haengt]
die alte Reihenfolge nicht hinter die neue").

**Tatsaechlich:** Programmfenster bleibt bedienbar (`Responding=True`,
keine Absturzmeldung), aber im Log erscheint:
```
Traceback (most recent call last):
  File "nrplanner\relicpicker.py", line 1641, in _paint_more
    self._say_what_they_are_worth(pairs)
  ...
  File "nrplanner\relicpicker.py", line 632, in show_values
    value.setText(text)
RuntimeError: libshiboken: Internal C++ object (PySide6.QtWidgets.QLabel) already deleted.
```
Das Raster bleibt dauerhaft bei 15 Karten stehen, obwohl die Kopfzeile
weiterhin "106 of 209 relics matching" zeigt. Filter wieder leeren stellt
die restlichen 194 Karten **nicht** wieder her (weiterhin 15, ein zweiter
Traceback aus `_refresh` selbst folgt). Ein frischer Dialog (schliessen,
neu oeffnen, diesmal ohne sofortiges Tippen) baut wieder korrekt alle 209 --
der Schaden bleibt auf die eine Dialoginstanz begrenzt.

**Analyse (Hypothese, code-gestuetzt):** `self._card_cache` (Zeile 1084)
lebt fuer die gesamte Dialoginstanz und wird nur punktuell invalidiert
(Zeile 1475, beim Favoriten-Umschalten -- mit explizitem Kommentar an
Zeile 1468f., dass `_refresh()` die Karte, an der ein Menue haengt,
zerstoert). Beim Tastendruck ersetzt `_refresh()` (Zeile 1606-1608) das
`CardGrid` durch ein neues (`self.scroll.setWidget(...)`), was die alten,
bereits im Raster platzierten `RelicCard`-Widgets auf C++-Seite loescht.
`self._more.stop()` (Zeile 1530) verhindert nur ein kuenftiges Timer-Feuern,
nicht ein bereits in der Event-Queue haengendes. Trifft `_paint_more`
danach dennoch (oder liest ein spaeterer `_refresh`/`_cards_for`-Aufruf,
Zeile 1624, denselben `id(item)` erneut -- z. B. beim Filter-Leeren, wenn
dieselben Relikt-Objekte wieder auftauchen), liefert `self._card_cache.get`
eine bereits zerstoerte Karte zurueck, und `show_values` stuerzt auf ihr
QLabel. Die gleiche Faelle, die der Kommentar bei Zeile 1468f. fuer den
Favoriten-Pfad explizit umgeht (`.pop(id(item))` vor dem naechsten
`_refresh()`), fehlt fuer den Tipp-waehrend-Nachbau-Pfad.

**Auswirkung:** Der Nutzer bekommt eine Kopfzeile, die mehr Treffer
verspricht als das Raster zeigt (106 vs. 15), ohne jede Fehlermeldung --
er waehlt aus einer sichtbar unvollstaendigen Liste, in dem Glauben, sie sei
vollstaendig. Da die Ursache eine dialoglokale, aber dauerhafte
Cache-Verletzung ist, hilft in der laufenden Session kein Filter-Aendern
oder -Leeren; nur ein Schliessen und Neu-Oeffnen des Slots (und diesmal
ohne sofortiges Tippen) fuehrt zu vollstaendigen Ergebnissen. Da die
QA-258-Fuellung schneller sichtbar wird (115 ms statt 1007 ms), ist ein
Tippen waehrend des noch laufenden Nachbaus eher wahrscheinlicher als vor
dem Fix, nicht seltener -- Hauptpfad-Nutzung bei grossen Slots (weiss,
Deep), nicht exotisch.

**Vorschlag:** Cache-Eintraege, deren Karte in einem inzwischen ersetzten
`CardGrid` sass, vor jedem `_refresh()`/`_paint_more()`-Zugriff verwerfen
(analog zur bestehenden `.pop()`-Behandlung beim Favoriten-Pfad) oder den
gesamten `_card_cache` beim `CardGrid`-Tausch leeren und den Preis (erneuter
Kartenbau) in Kauf nehmen -- Korrektheit vor der QA-258-Ersparnis.

## 4 -- AN-5 (Typzeilen beidhaendig im Weapons-Tab)

Live am Arsenal-Tab (Suche "Hookclaws", Level 1): Kachel zeigt neben `AR`
auch jede Schadensart-Zeile mit `2H`-Zusatz, z. B. `Physical 38 / 30 2H`,
`Fire 19 / 15 2H`. Bestaetigt, kein Befund.

## 5 -- A18/A20-Persistenz

`git log`/`git diff` fuer den Bereich seit `989ebdf` zeigt keine Aenderung
an `nrplanner/favourites.py` oder `nrplanner/chalices.py` -- die
Persistenzpfade fuer Markierungen (A18/A19) und 1H/2H-Speicherung (A20)
sind in diesem Zyklus nicht angefasst; beide wurden in T-253/T-265/T-265d
bereits am Artefakt bestaetigt (Register QA-259, QA-272). Ergaenzend live
geprueft: Hero-Auswahl (Wylder) und Deep-of-Night-Haken ueberleben einen
sauberen Neustart der EXE unveraendert; Level-Slider und Waffen-Slot-
Belegung nicht (setzen auf den Save-Wert bzw. leer zurueck) -- das ist nach
Lesart des Labels "Exact value from the game data" und der
Save/Delete/Hide-Logik der Chalice-Builds beabsichtigtes Verhalten, kein
Befund.

## Explorationsprotokoll

- Cache-Neubau v11→v12: 1x, ohne Fehler, Felder/Zahlen gegenprueft.
- QA-276: Testlauf `test_attack_power_calibration_against_the_game.py`
  (38/38), plus ein Live-Fall (Wylder+Hookclaws) am Fenster ueber Arsenal-
  Picker + Level-Slider.
- QA-258: Suite `test_relic_picker_advisor.py` (83/83), eine
  UIA-Sichtbarkeitsmessung (qualitativ), zwei reproduzierte
  Filter-waehrend-Fuellung-Versuche (beide brachen), ein Sortwechsel-Versuch
  (zu spaet getimt, kein Ergebnis), eine Recovery-Pruefung nach dem Crash
  (Filter leeren stellt nichts wieder her; neuer Dialog ohne fruehes Tippen
  baut wieder vollstaendig).
- AN-5: ein Live-Blick auf die Arsenal-Kachel.
- A18/A20: `git log`/`git diff` auf die Persistenzdateien seit dem letzten
  bestaetigten Stand, plus ein Neustart-Zyklus (Hero/Deep persistieren,
  Level/Waffenslot nicht -- als beabsichtigt eingeordnet).

## Offene Fragen

Keine neuen. Die A7-Popup-Textpruefung fuer QA-276 wurde ueber die
bestehende gruene Testzusicherung abgedeckt, nicht per Klick am Fenster --
falls das fuer den Abnahmenachweis nicht reicht, bitte als eigenen Punkt
zurueckgeben.

## Nicht getestet

- "Sortwechsel waehrend Fuellung" und "Rescan waehrend Fuellung" (Auftrag
  Punkt 3): aus Zeitbudget nicht sauber in der Fuellphase reproduziert.
  Gegebener Fund (QA-277) legt nahe, dass derselbe `_card_cache`/
  `CardGrid`-Tausch-Mechanismus betroffen ist (`_refresh()` wird von Sort-
  und Rescan-Pfaden ebenso aufgerufen) -- nicht unabhaengig bestaetigt.
- Volle n=5-Median-Messung fuer QA-258 mit praeziser ms-Instrumentierung
  (die verfuegbare UIA-Polling-Messung hat zu viel Eigen-Overhead fuer eine
  belastbare Zahl gegen die 115-ms-Angabe des Commits).

## Zusammenfassung (an director)

P1: 1 (QA-277, neu). P2: 0 (QA-276 Retest bestanden). P3: 0 offen neu
(QA-258-Sichtbarkeit bestaetigt). P4: 0.

**Gesamturteil: FAIL** -- QA-277 (P1, Major, Hoch) muss vor Release behoben
sein: die QA-258-Perf-Fix fuehrt beim naheliegenden Tippen-waehrend-Fuellung
zu einer dauerhaft unvollstaendigen, aber als vollstaendig beschrifteten
Kartenliste im Picker. Alle anderen Punkte (Cache-Neubau v11→v12, QA-276,
AN-5, A18/A20) bestaetigt/unauffaellig.
