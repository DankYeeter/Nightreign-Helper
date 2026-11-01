# T-335qa2 — Rest-Fensterlauf und Retest (qa-engineer), 31.10.2026

Stand `f9ded44` (Code = `59559a7`). Fenster `run.py` aus dem Quellstand,
Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT335qa2`, `LOCALAPPDATA`/`APPDATA`/
`USERPROFILE` in den Scratchpad `T-335qa2/w/`, Testabzug v18 (1027 Dateien,
`meta.extract_version` 18) und eingefrorener Spielstand aus T-335qa kopiert
(sha256 `5fb89851...` gleich, 315 Relikte). Vor dem Lauf keine
`NightreignHelper.exe` (tasklist 16:58); am Ende kein Fenster dieses Laufs offen
(17:18). Fuenf Starts nacheinander, nie zwei zugleich: Skalierung 125 % (System),
100 % und 150 % (`QT_SCALE_FACTOR` 0.8/1.2 auf 125 %), ohne Spielstand
(`APPDATA` leer bzw. fehlend).

## Risiko-Briefing

Am riskantesten: (1) die neue Fokus-Policy der Kacheln (QA-312) — Fokus und
Rahmenbreite wirken auf das Rasterlayout; (2) das Popup als eigenes
Top-Level-Fenster bei verschiedenen Skalierungen und Fensterlagen; (3) Texte,
die nach den Fixes von QA-310/314 wieder vom Fenster abweichen (Klasse QA-306/
QA-311); (4) Rueckfall der Zauberwahl auf die Start-Katalysator-Kachel.
Reihenfolge: Suite, Tastatur/Fokus, Popup, Why/Warnzeile, Rueckfall,
RELIC-Chip, Buendelung, Mindestbreite/Skalierung, Neustart, ohne Spielstand,
Anleitung.

## Ergebnis je Pruefpunkt

| Punkt | Ergebnis | Beleg |
|---|---|---|
| Volle Suite | 2165 passed, 9 skipped, 153 s | `pytest -n auto`, `T-335qa2/suite.log` |
| QA-310 Why/Warnzeile unter Weapon art | **behoben**: Why "It is one hit of Glintblade Phalanx from Magic Longsword on the selected tile, at its tier, one-handed"; leere Kachel: "... from Wylder's Greatsword — the starting armament at its lowest tier, as the selected tile is empty"; Warnzeile (Fire) nennt "for a weapon art the armament on it" | s10, s11 |
| QA-312 Kacheln als Tab-Stopps | **behoben**: Tab-Kette Kachel 1..6 -> ART-Chip -> 1H -> Tab-Leiste; Enter auf Kachel 2 macht sie aktiv | s2, s3 |
| QA-313 Standardpunkt im Popup | **behoben**: ACCENT-Punkt am ersten Eintrag (Wylder, Stamp) | Bild `05-wylder-art-popup.png` |
| QA-314 gerollte Waffe | **behoben**: Magic Longsword auf Kachel 2: Chip "Choose a weapon art", Fusszeile "Square Off · FP 0 · Choose this weapon's art", kein Punkt | s9, Bild `06` |
| Rueckfall (Director-Entscheid) | **haelt**: Recluse, Arc auf Kachel 1, Kachel 2 leer bzw. Blood Claymore markiert, Sorceries: Why rechnet `Spell damage (Glintstone Arc)` | s13, s14 |
| Fokus gestrichelt | haelt: aktive+fokussierte Kachel gestrichelt, nur aktive durchgezogen, fokussierter Chip gestrichelt ACCENT | Bilder `c01`..`c04` |
| Puppenzahlen | Pebble 123, Arc 120 (Lv15, ohne Relikte) = Chip = Zeile | s24, s25 |
| RELIC-Chip (AK-417) | haelt: Grand Luminous Scene (Night Shard) in Slot 1: genau ein Chip `RELIC: Night Shard, 94, selected`, Satz woertlich, Zeile 94, Klick oeffnet nichts; ohne Relikt wieder R2 Arc gewaehlt | s24, s25, Bild `c09` |
| Pool mit einem Eintrag (AK-413) | haelt: Blood Parrying Dagger, Chip `ART: Parry`, Klick und Enter oeffnen nichts, Zeile "Parry deals no damage." | s9 |
| R1 ein Klick, gleiche Waffe behaelt, andere setzt zurueck (AK-414) | haelt | s46-s48 |
| Neustart -> Standard (AK-414) | haelt: nach Neustart R1 gewaehlt, Kacheln leer bis auf Startwaffe | s31 |
| Mindestbreite / AK-405 / AK-418 | haelt bei 100/125/150 %: Mindestbreite 1189/1487/1785 px physisch (= 1190 logisch); Build-Zeile ohne Ueberdeckung, `Show hidden` zweite Zeile, Feld 200/>=225/301 px (>= 180 logisch); beide Chips innerhalb der StatSheet-Spalte; kein waagerechter Rollbalken; zusaetzlich 1366 logisch und 1506 physisch bei 125 % | s28, s32, s34, Bilder `10`-`15` |
| Buendelung Fluch 6850900 | haelt: Slotkarte und Why je genau eine Zeile "Reduced Damage Negation for Flask Usages: All damage taken +45.0% — this figure does not count it." | s22 |
| AK-406a/c, AK-407c | haelt: ohne Spielstand "No save was read, so there are no relics to choose from — use Find my save.", nach Optimize unveraendert; Rescan-Tooltip mit Zusatz "If none was found, use Find my save." | s40, Bild `16` |
| AK-408a | haelt: Legende im Why woertlich wie Spec | s10 |
| QA-302 "This PC" (Spielstand-Dialog) | haelt: `APPDATA` fehlend -> Adresse "This PC"; `APPDATA` vorhanden ohne `Nightreign` -> startet im Profilordner (Absicht laut `where_saves_usually_are`) | s42, s45, Bild `19` |
| QA-030 leer speichern | haelt: Relikt in Slot 1, Kelchwechsel und zurueck -> bleibt; `Empty slot`, Kelchwechsel und zurueck -> leer; nach Neustart leer | s26, s31 |
| Anleitung "Unchecked" gegen Fenster | Wortlaut, Tab-Reihenfolge, Merken, RELIC-Satz, Staff-Satz, Tooltip (Name, Schule, FP, "default of this weapon") stimmen; Abweichung siehe QA-317 | s3, s46-s49, Bild `20` |

## Befunde

### [P3 | Minor | Mittel] QA-315 Pool-Popup ragt unter den Bildschirmrand

**Adressat:** developer
**Betroffen:** `nrplanner/castingbar.py:377-380` (`PoolPopup.open_under`)
**Umgebung:** 150 % (125 % System, `QT_SCALE_FACTOR=1.2`), Fenster 1785x1153 an y=720, Bildschirm 5120x2160 physisch

**Reproduktion:**
1. Wylder, Kachel 1, Fenster so legen, dass die Casting-Leiste im unteren Drittel des Bildschirms steht.
2. ART-Chip anklicken.

**Erwartet:** Das Popup bleibt im sichtbaren Bildschirm (bei Platzmangel ueber dem Chip).
**Tatsaechlich:** Popup 3332,1784..3809,2240 bei Bildschirmhoehe 2160: 80 px unterhalb des Randes, die Fusszeile (Name, FP, Standardvermerk) liegt ausserhalb.
**Analyse:** `open_under` setzt die Lage auf `mapToGlobal(bottomLeft)` ohne Abgleich mit `screen().availableGeometry()`; das Fenster-Popup wird von Qt nicht verschoben (gemessen).
**Auswirkung:** Auf kleinen Bildschirmen (Laptop 1080p bei 125/150 %) liegt die Leiste nach Rechnung (nicht gemessen) meist in der unteren Haelfte; dann fehlt die einzige Textzeile des Popups.
**Vorschlag:** Lage gegen `availableGeometry()` klemmen, bei Platzmangel ueber dem Chip oeffnen.

### [P4 | Minor | Niedrig] QA-316 Tab durch die Kacheln verschiebt alles darunter um 18-20 px

**Adressat:** developer
**Betroffen:** `nrplanner/weaponslots.py` (`WeaponTile._apply_appearance`, Rahmen 1 -> 2 px bei Fokus)
**Umgebung:** 125 %, Fensterbreite 2448 px physisch, Wylder

**Reproduktion:**
1. Kachel 1 anklicken, dann Tab, Tab, ...
2. Lage des ART-Chips je Fokusstellung lesen.

**Erwartet:** Fokuswechsel aendert keine Geometrie.
**Tatsaechlich:** Chip-Y 1472 (Fokus Kachel 1/3/4) gegen 1490/1492 (Fokus Kachel 2/5/6); die Spalten verteilen sich um 1-2 px neu, "Slot 3 — empty" bricht zweizeilig um, die Kachelreihe waechst (Bilder `c01`/`c02`).
**Analyse:** Der 2-px-Rahmen vergroessert die Mindestbreite der fokussierten Kachel; das Raster verteilt neu. Dieselbe Ursache gab es fuer die aktive Kachel schon vorher; neu ist Tab als Ausloeser (`849190c`/`59559a7`).
**Auswirkung:** Casting-Leiste und Hand-Schalter springen beim Tabben; abhaengig von der Fensterbreite.
**Vorschlag:** Rahmenbreite konstant halten (immer 2 px, Farbe wechselt) oder Innenabstand ausgleichen.

### [P4 | Minor | Mittel] QA-317 Anleitung: Standardart mit Punkt gilt nur noch fuer die Startwaffe

**Adressat:** director (technical-writer)
**Betroffen:** `docs/anleitung/guide.md` Abschnitt Casting und Weapon art (Stand `e38d3dd`, vor `faa4293`)
**Reproduktion:** Wylder, Kachel 2 Magic Longsword (Daten: `art_default` 115) ohne Wahl.
**Erwartet (Anleitung):** "The weapon's own default art is listed first and marked with a dot"; die Zeile Weapon art erscheint mit "the weapon's default art".
**Tatsaechlich:** Seit QA-314 (`faa4293`) hat eine Waffe abseits der Startwaffe keine eigene Art: Chip "Choose a weapon art", kein Punkt, keine Art-Zeile (s9; ebenso Blood Claymore bei Recluse, s14).
**Vorschlag:** Satz auf "only your starting armament has a default art" ziehen; die Zeile "*Unchecked: ...*" kann danach entfallen (alle dort genannten Punkte sind am Fenster bestaetigt, s. Tabelle).

### [P4 | Trivial | Hoch] QA-318 Stylesheet der World-Events-Liste wird verworfen

**Adressat:** developer
**Betroffen:** `nrplanner/eventstab.py:102-108` (seit `cec61c7`, 10.08.2026)
**Reproduktion:** Programm starten; stderr zeigt bei jedem Start 3x "Could not parse stylesheet of object QListWidget(...)".
**Erwartet:** Liste mit PANEL-Hintergrund, Rahmen, Abstaenden und Auswahlfarbe.
**Tatsaechlich:** Zeile 104 `" border-radius: 4px; padding: 4px; }}"` ist kein f-String, die Klammer bleibt doppelt; Qt verwirft das ganze Stylesheet.
**Vorschlag:** `f` voranstellen oder einfache Klammer; ein Test, der das Stylesheet parst bzw. stderr auf "Could not parse" prueft.

## Beobachtungen

- Die Kacheln haben keinen UIA-Namen (`WeaponTile` Name leer); ein Bildschirmleser liest beim Tabben nichts vor.
- PostMessage-Doppelklick oeffnet den Armament-Dialog nicht mehr, echter Doppelklick schon (Treiberthema, wie T-335g).
- stderr enthaelt nach dem nativen Dateidialog 6x "Windows fatal exception: code 0x80010012" vom Faulthandler; das Programm lief weiter und schloss normal.
- Der Dialog "Location is not available" (`home\Desktop`) ist eine Folge der `USERPROFILE`-Umlenkung, nicht des Programms.
- pytest PID 27048 (12:20:56, echter Dateidialog aus T-335p) laeuft weiter; ab 17:14 lief ein fremder `pytest -n 8` (nicht von mir).

## Offene Fragen

- **ui-ux-designer:** Waehlt man per Maus eine Kachel, bleibt sie fokussiert und damit gestrichelt, solange nichts anderes den Fokus nimmt; die aktive Kachel sieht nach jedem Klick gestrichelt aus. Gewollt (Entscheid T-335fix2) oder nur fuer Tastaturfokus?

## Nicht getestet

- Ordnerdialog des Erststarts (`firstrun._pick_a_folder`, QA-302 erster Teil): braucht einen Erststart ohne Steam-Bibliothek; Test in der Suite gruen.
- AK-406b (gelesener, leerer Spielstand): kein solcher Spielstand verfuegbar; Test gruen.
- AK-408b (nur Zeilen anderer Nightfarer durchgestrichen), Klick-Tooltip der Spell-damage-Zahl.
- 100/150 % sind per `QT_SCALE_FACTOR` nachgebildet, nicht per Windows-Einstellung; ein Laptop-Bildschirm (QA-315) nicht gemessen.

## Gesamturteil

**CONCERNS**: kein Befund P1/P2; die Rest-Pruefpunkte aus T-335qa sind am
Fenster belegt, QA-310, QA-312, QA-313, QA-314 behoben, Rueckfall haelt. Vor dem
Release zu entscheiden: QA-315 (P3), QA-316/317/318 (P4).
