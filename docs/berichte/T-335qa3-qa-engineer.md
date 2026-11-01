# T-335qa3 — Nachtest am Fenster (qa-engineer), 31.10.2026

Stand `45942dc` (Code = `99a5679`). Fenster `run.py` aus dem Quellstand,
Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT335qa3`, `LOCALAPPDATA`/`APPDATA`/
`USERPROFILE` in den Scratchpad `T-335qa3/w/`, Testabzug v18 (1027 Dateien,
`extract_version` 18) und eingefrorener Spielstand aus T-335qa2 (sha256
`5fb89851...`). Vor dem Lauf keine `NightreignHelper.exe` (tasklist 17:52:37);
zwei Starts nacheinander (125 % System, 150 % per `QT_SCALE_FACTOR=1.2`); am
Ende kein Fenster und kein `run.py`-Prozess offen (18:01:35).

## Ergebnis je Pruefpunkt

| Punkt | Ergebnis | Beleg |
|---|---|---|
| Volle Suite | 2169 passed, 9 skipped, 162 s | `pytest -n auto`, `T-335qa3/suite.log` |
| QA-315 Popup am Bildschirmrand (150 %) | **behoben**: unten -> ueber dem Chip (Popup-Unterkante = Chip-Oberkante); Umschlagpunkt exakt: Popup unten bis y=2160, ein Pixel tiefer oeffnet es oben; rechts an x=5120 geklemmt, links an x=0; Fusszeile immer sichtbar | s9, s10, Bilder `p01`, `p1-584` |
| QA-316 Tab durch Kacheln 1..6 und ART-Chip | **teilweise behoben**: Kachel 1 aktiv: Chip-Y 1537 und Hand-Schalter 1690 bei jedem Tab-Schritt gleich, Zeilenhoehe 120 konstant; Spalten verschieben sich noch um 1-4 px waagerecht. Kachel 2 aktiv: Tab auf Spalte 3 laesst Zeilen 120 -> 102 px schrumpfen, Hand-Schalter springt 1511 -> 1476 (siehe unten) | s3, s5, s6, Bild `qa316-pair.png` |
| Fokus: Klick durchgezogen | haelt fuer Klick auf eine **andere** Kachel (durchgezogen, auch mit echter Maus); **nicht** fuer Klick auf die Kachel/den Chip, den Tab schon fokussiert hatte -> QA-319 | s4, s7 |
| Fokus: Tab gestrichelt; Tab, Enter, Esc bleibt gestrichelt | haelt: Chip nach Tab gestrichelt, nach Enter/Esc gestrichelt, nach Wahl per Tastatur (Barbaric Roar) gestrichelt auf dem neuen Chip | s3, s4 (`f02`..`f04`) |
| QA-318 World-Events-Liste | **behoben**: stderr beider Starts 0 Byte, 0x "Could not parse"; Liste mit Rahmen, Hintergrund, Innenabstand, goldener Auswahl | s2, Bild `01c.png` |
| QA-317 guide gegen Fenster | **behoben**: Startwaffe Stamp zuerst mit Punkt, Fusszeile "this weapon's own art"; Magic Longsword: gestrichelter Chip "Choose a weapon art", kein Punkt, keine Art-Zeile, Fusszeile "... · Choose this weapon's art"; nach Wahl Zeile "Weapon art (Assassin's Gambit) Assassin's Gambit deals no damage." wie Anleitung; Tab-Kette Kacheln -> Chip -> 1H; Zeile "Unchecked" entfernt | s11, Bilder `g01c`, `g02` |
| Suche projektweit nach weiteren Nicht-f-Strings mit `}}` (QA-318-Klasse) | 1 Treffer `effectfilterdialog.py:180-181`, dort per `.format()` benutzt, also korrekt | grep zwei Masken |

## Befunde

### [P4 | Minor | Niedrig] QA-316 (Rest) Tab verschiebt bei aktiver Kachel 2 weiter alles darunter

**Adressat:** developer
**Betroffen:** `nrplanner/weaponslots.py:243-248` (`WeaponTile._apply_appearance`), ebenso `castingbar.py:278-282`
**Umgebung:** 125 %, Fenster 2448 px physisch, Wylder, Startwaffe auf Kachel 1, Rest leer

**Reproduktion:**
1. Kachel 2 (leer) anklicken.
2. Tab (Fokus auf Kachel 3).

**Erwartet:** Fokuswechsel aendert keine Geometrie.
**Tatsaechlich:** "Slot 3 — empty" passt nach Tab auf eine Zeile, beide Kachelreihen schrumpfen von 120 auf 102 px, Hand-Schalter und Satz darunter springen 35 px nach oben (1511 -> 1476); zurueck bei Fokus auf Spalte 1/2. Mit Kachel 1 aktiv bleibt Y gleich, die Spalten wandern 1-4 px waagerecht.
**Analyse (offscreen belegt):** Der Selektor `QFrame { ... margin: 1px }` der Kachel trifft auch ihre beiden `QLabel` (QLabel ist ein QFrame). Ungeringte Kachel: Label-`contentsRect` (1,1,..), Hinweis 182 px; geringte: (0,0,..), 168 px. Damit aendert der Fokus weiter die Breitenhinweise, das Raster verteilt die Spalten neu, Umbrueche kippen.
**Auswirkung:** Wie zuvor, nur von einer anderen Ausgangslage aus.
**Vorschlag:** Selektor auf die Kachel selbst begrenzen (`objectName` oder `WeaponTile`/`ChipWidget` als Klassenselektor), damit `margin` nicht auf die Labels erbt.

### [P4 | Trivial | Mittel] QA-319 Klick auf die per Tab fokussierte Kachel bzw. den Chip bleibt gestrichelt

**Adressat:** developer
**Betroffen:** `nrplanner/cardgrid.py:157-163` (`_note_focus_reason`, nur aus `focusInEvent`)

**Reproduktion:**
1. Kachel 2 anklicken, Tab (Kachel 3 gestrichelt).
2. Kachel 3 mit der Maus anklicken.

**Erwartet:** Nach Klick durchgezogen (Director-Entscheid T-335qa2: gestrichelt nur bei Tastaturfokus).
**Tatsaechlich:** Kachel 3 wird aktiv, bleibt gestrichelt (echte Maus, s7). Ebenso Chip: Tab auf den Chip, Klick, Esc -> gestrichelt (s4 `f05`).
**Analyse:** Hat das Element den Fokus schon, loest der Klick kein `focusInEvent` aus; `keyboard_focus` bleibt `True`.
**Vorschlag:** `keyboard_focus` auch im `mousePressEvent` loeschen und neu zeichnen.

### [P4 | Trivial | Niedrig] QA-320 Pool-Popup zeigt bei 150 % fuenf statt sechs Symbole je Reihe

**Adressat:** developer
**Betroffen:** `nrplanner/castingbar.py:337-340` (`PoolPopup.__init__`, Zellbreite `(width - 30) // POPUP_COLUMNS`)
**Umgebung:** 150 % (`QT_SCALE_FACTOR=1.2` auf 125 %), Popup 522 px physisch

**Reproduktion:**
1. Wylder, Blood Claymore (30 Arts) auf Kachel 3, Kachel 3 waehlen.
2. ART-Chip anklicken.

**Erwartet:** 6 Symbole je Reihe, hoechstens 5 Reihen, dann Rollbalken (`UI_SPEC.md:8749`); 30 Arts = 5 Reihen ohne Rollbalken.
**Tatsaechlich:** 5 je Reihe, 6 Reihen, Rollbalken, Luecke rechts (3 von 3 Oeffnungen, Bild `g05`). Magic Longsword (36) zeigte beim ersten Oeffnen ebenfalls 5 je Reihe (`g02`), danach 6.
**Analyse (Hypothese):** Bei 150 % reicht die Viewportbreite nach Abzug von Rahmen und reserviertem Rollbalken knapp nicht fuer 6 Zellen. Besteht schon vor QA-315: T-335qa2-Bild `15-popup-150.png` (Stand `59559a7`) zeigt ebenfalls 5 je Reihe, also keine Folge des Fixes.
**Vorschlag:** Zellbreite aus der tatsaechlichen Viewportbreite abzueglich Rollbalken rechnen.

## Beobachtungen

- Die Kacheln haben weiter keinen UIA-Namen (wie T-335qa2).
- Ein Chip ganz oberhalb des Bildschirms (Fenster nach y=-1300 geschoben) oeffnet das Popup darunter, oben 180 px abgeschnitten; per Ziehen nicht erreichbar, daher kein Befund.

## Nicht getestet

- QA-315 bei 100 % und auf einem Laptop-Bildschirm; der Arbeitsbereich hier ist 5120x2160 ohne Taskleistenabzug, `availableGeometry` mit Taskleiste also nicht belegt.
- QA-320 bei 125 % (T-335qa2 zeigte dort 6 je Reihe).
- Rueckwaerts-Tab (Shift+Tab), nicht per PostMessage sendbar.

## Gesamturteil

**CONCERNS**: kein Befund P1/P2. QA-315, QA-317, QA-318 behoben; QA-316 im
beauftragten Weg (Kachel 1 aktiv, Chip-Y) gehalten, Rest offen (P4); Fokus
"Klick durchgezogen" haelt nicht beim Klick auf das schon fokussierte Element
(QA-319, P4); QA-320 (P4) besteht seit vor dem Fix. Der `director` entscheidet,
ob QA-316-Rest und QA-319 vor dem Release behoben werden.

## Register-Zeilen (zum Anhaengen durch den Director)

```
| QA-315 | **Retest T-335qa3 (31.10.2026, qa-engineer, Quellstand `99a5679`): behoben** -- 150 %: unten ueber dem Chip, Umschlag exakt an y=2160, rechts an x=5120, links an x=0 geklemmt, Fusszeile sichtbar. Fix `ffeecd2` | P3 | Minor | developer | ja - Fenster T-335qa3, Bilder p01/p1-584 | behoben -- Fix `ffeecd2`, Retest T-335qa3 | 2026-10-31 |
| QA-316 | **Retest T-335qa3 (31.10.2026, qa-engineer, Quellstand `99a5679`): teilweise behoben** -- Kachel 1 aktiv: Chip-Y 1537 bei Tab 1..6 konstant. Kachel 2 aktiv, Tab auf Kachel 3: Reihen 120 -> 102 px, Hand-Schalter 1511 -> 1476. Ursache offscreen belegt: `QFrame { margin: 1px }` erbt auf die QLabels der Kachel (`weaponslots.py:243-248`, `castingbar.py:278-282`). Fix `d6ae45d` | P4 | Minor | developer | ja - Fenster T-335qa3, Bild qa316-pair | teilweise | 2026-10-31 |
| QA-317 | **Retest T-335qa3 (31.10.2026, qa-engineer, Quellstand `99a5679`): behoben** -- guide.md Casting/Weapon art stimmt mit dem Fenster (Startwaffe mit Punkt, Magic Longsword "Choose a weapon art" ohne Punkt und Zeile, Fusszeile "Choose this weapon's art"); "Unchecked" entfernt. Fix `3414152` | P4 | Minor | director | ja - Fenster T-335qa3 | behoben -- Fix `3414152`, Retest T-335qa3 | 2026-10-31 |
| QA-318 | **Retest T-335qa3 (31.10.2026, qa-engineer, Quellstand `99a5679`): behoben** -- stderr zweier Starts 0 Byte, Liste gestylt; Suche nach weiteren Nicht-f-Strings mit `}}`: 1 Treffer `effectfilterdialog.py:180`, per `.format()` korrekt. Fix `780be29` | P4 | Trivial | developer | ja - Fenster T-335qa3, Bild 01c | behoben -- Fix `780be29`, Retest T-335qa3 | 2026-10-31 |
| QA-319 | **T-335qa3 (31.10.2026, qa-engineer):** Klick auf die per Tab fokussierte Kachel (oder Chip) laesst sie gestrichelt: `cardgrid.py:157-163` setzt `keyboard_focus` nur in `focusInEvent`, ein Klick auf das schon fokussierte Element loest keins aus. Entscheid T-335qa2: gestrichelt nur bei Tastaturfokus | P4 | Trivial | developer | ja - Fenster T-335qa3 (echte Maus) | offen | 2026-10-31 |
| QA-320 | **T-335qa3 (31.10.2026, qa-engineer):** Pool-Popup bei 150 % mit 5 statt 6 Symbolen je Reihe (`UI_SPEC.md:8749`): Blood Claymore 30 Arts in 6 Reihen mit Rollbalken, 3/3; besteht schon vor `ffeecd2` (Bild T-335qa2 `15-popup-150.png`). `castingbar.py:337-340` | P4 | Trivial | developer | ja - Fenster T-335qa3, Bild g05 | offen | 2026-10-31 |
```
