# T-336qa — Stack-Spalte im Fenster (qa-engineer), 07.11.2026

Stand `61b9ae1`. Fenster `run.py` aus dem Quellstand mit `scripts/drive_window.ps1`
(PID nachgesetzt), Tippen und Klicken ueber `PostMessage`, keine echte Maus,
kein Fokusraub. Dazu dieselben Widgets im Prozess unter `QT_QPA_PLATFORM=windows`,
Eingabe-Grenzfaelle unter `offscreen` (eigene Zwischenablage).
Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-336qa`, `LOCALAPPDATA`/`APPDATA` in
den Scratchpad `<SP>/T-336qa/`, Testabzug 1027 Dateien kopiert. Spielstand nur gelesen,
nicht eingefroren (324 Relikte, Spiel lief nicht). Bildschirm 5120x2160, Fenster-DPI
120 (125 %); 100 % und 150 % per `QT_SCALE_FACTOR` 0,8 und 1,2. Kein Registry-Schluessel
geloescht, nichts unter `DankYeeter`; Testschluessel `DankYeeterT-336qa` bleibt liegen.

Bilder in `<SP>/T-336qa/shots/`, Skripte in `<SP>/T-336qa/s/`.

**Gesamturteil: CONCERNS.** Alle Pruefpunkte des Auftrags halten. Vor dem Release ist
QA-335 zu entscheiden: Unter Lesart A (siehe dort) wird das Urteil FAIL.

## Risiko-Briefing

Am riskantesten waren der Weg des Werts in andere Fragen ("nur fuer Optimize"), die
Wirkung von 0 und n in `compute`/`explain`, der Verlust beim Schliessen ohne
`editingFinished`, die Grenze 999 (Laufzeit, Ueberlauf), zuletzt Sortieren und Tab in
einer Spalte aus Eingabefeldern. In dieser Reihenfolge geprueft.

## Ergebnis je Pruefpunkt

| Punkt | Ergebnis | Beleg |
|---|---|---|
| Volle Suite | 2479 passed, 9 skipped, 121 s | `<SP>/full1.log` |
| Spalte zwischen Allow und Name, nur auf Stack-Effekten | **haelt**: 7 Felder bei 343 Zeilen dieses Spielstands; `[Scholar] Earn runes for each ...` hat keins (`accumulates` falsch) | `f2.png` |
| Fensterbreite 702 im echten Fenster | **haelt**: 702x707 physisch bei 100 %, 877x883 bei 125 % (= 702 logisch), 1053x1060 bei 150 %. `Stacks` 62/77/93 physisch; `Name` 288 bei 100 %. Kein waagerechter Rollbalken. `999` passt ins Feld | `f11.png`, `s100-f.png`, `s150-f.png` |
| Tippen, Schliessen per X/Esc | **haelt**: Registerwert nach jedem Tastendruck; Wert nach WM_CLOSE und nach Esc vorhanden | `a4.ps1`, `a5.ps1` |
| Neustart | **haelt**: 2, 0, 999, 12, 3 nach Neustart unveraendert; 0 bleibt 0, nicht leer | `f7.png`, `a9.ps1` |
| Filter gegen ×-Zahl | **haelt** (echte `SituationalRow`, Haken + ×3, Relikte angewendet): Filter leer: Frage 3, +22,5 %. Filter 2: Frage 2, +14,5 %. Filter 0 und 1: Frage 0 bzw. 1, Relikt nicht mehr gewaehlt. Wieder leer: +22,5 %. Haken, ×-Zahl, `value()`, `ar_label`, `planner.declared` nach jedem Schritt gleich | `s4.py` |
| Alte Antwort beim Tippen | **haelt**: `Why` weg, "Nothing suggested yet." noch bei offenem Filter. Aenderung 0 ms nach dem Klick und waehrend des Laufs: `OUTDATED`, keine Antwort. Folgelauf rechnet mit dem neuen Wert. Hin und zurueck (2, 3, 2) trifft den Cache mit der richtigen Zahl. Gefaesszeilen verlieren `BEST`, Zahlen bleiben (AK-432/434, gewollt) | `s4.py`, `s10.py` |
| Wert 2 | **haelt**: "Stacks you set for Optimize:" und +14,5 % (1,07²) je Relikt | `w1.png` |
| Wert 0 | **haelt**: "you set its stacks to 0, so it is not counted." mit Favorit (in der Faltung "Show n effects without a number"), dazu in "only apply under a condition". Ohne Favorit: Relikt nicht gewaehlt, also keine Zeile; Satz in `explain` direkt geprueft. Alle 8 Effekte mit 0, 1, 2, 3 und 999, auch Arcane additiv (+4/+8/+12) | `w0fav.png`, `s150-why.png`, `test_scratch_additive.py` |
| Leeres Feld = wie vorher | **haelt**: Relikte und Zahl in 6 Laeufen (3 Richtungen, Deep aus/an) gleich mit `114d0a1` | `s10old.log`, `s10new.log` |
| Grenze 999 | Eingabe **haelt** (4. Ziffer abgewiesen); Laufzeit siehe QA-336. Kein Absturz in den gemessenen Laeufen | `a8.ps1`, `s2.py` |
| Unsinnseingaben | **haelt**: Buchstaben, `-`, `+`, Leerzeichen, arabische und vollbreite Ziffern, Emoji abgewiesen; Einfuegen von `12abc`, `1000`, `-1`, `2.5`, `\n5` abgewiesen; `007` wird 7; Undo/Redo/Ausschneiden schreiben mit; Enter schliesst nicht | `s7.log` |
| Beschaedigter Speicher | Lesen **haelt** (26 Faelle, auch Liste, Zahl, Bytes: leer oder gueltig, nie Fehler); Why siehe QA-337 | `s5.py` |
| Sortieren nach Stacks | **haelt** im echten Fenster: auf/ab richtig, Felder bleiben an ihrer Zeile (0 von 7 falsch), Eingabe danach trifft die Zeile; kein Umsortieren waehrend des Tippens | `f9.png`, `f10.png`, `f11.png` |
| Suche, Tab | **haelt**: Feld folgt der Suche, Wert bleibt. Tab: Favourite, Avoid, (Allow), Stacks, naechste Zeile | `s7.log` |
| Zeilenhoehe | 16/24 physisch bei 100 %, 20/30 bei 125 %, 24/36 bei 150 % (ohne/mit Feld). Siehe Beobachtungen | `f11.png` |
| Sortieren nach Type mit Familienzeile (`TypeError`) | **Bestand**: am Stand `114d0a1` ebenso auf- und absteigend `TypeError`; in `61b9ae1` unveraendert. Nicht neu gemeldet | `s3.py` |

Hauptthread waehrend eines Laufs mit 999 (10 s): groesste Luecke 31 ms; Wertaenderung bei
offenem Filter 24 ms im Median (n=20). 30 Mal Oeffnen und Schliessen: kein Fehler beim
naechsten `changed`. Stderr der Fensterstarts leer.

## Befunde

### [offene Frage, P3 oder P2 nach Lesart | Major oder Minor | Hoch] QA-335: Stacks-Wert bewegt auch die Damage-Spalte des Relikt-Pickers

**Adressat:** director
**Betroffen:** `nrplanner/relicpicker.py:518` (`asking_from`), `nrplanner/advisorbar.py:964-968`; Texte `STACKS_TOOLTIP`, `MARKS_EXPLANATION`, `guide.md`, `CHANGELOG.md`
**Umgebung:** Wylder, Slot 1, Suche "Night Invader" im Picker

**Reproduktion:**
1. Picker von Slot 1 oeffnen, Suche "Night Invader": `Grand Burning Scene` zeigt -6.0 AR.
2. Filter, Night Invader Stacks 4: Picker zeigt +9.3 AR.
3. Stacks 0: Picker zeigt -9.3 AR.

**Erwartet:** Vorgabe 1: "Der Filter-Wert gilt nur fuer Optimize"; Tooltip "Only for Optimize"; Changelog "applies to Optimize only".
**Tatsaechlich:** Die Picker-Frage baut auf `asking_from` auf und traegt den Wert mit.

**Lesart A:** "nur fuer Optimize" heisst woertlich nur die Optimize-Antwort; der Picker rechnet dann falsch. Major, Hoch: P2, Urteil FAIL.
**Lesart B:** gemeint war "nicht die Statistik-Seite"; der Picker gehoert zum Berater wie die Marken (Docstring `asking_from`: "the picker's own question ... carries them"), sonst widersprechen sich Picker und Why. Dann stimmen nur die Texte nicht: Minor, P3.

**Auswirkung:** Unter A zeigt der Picker fuer die Handwahl Zahlen mit einem Wert, den der Nutzer nur fuer Optimize gesetzt hat; unter B liest er "Only for Optimize" und sieht den Picker sich bewegen.
**Vorschlag:** Director entscheidet die Lesart; danach entweder den Picker vom Wert trennen oder die vier Texte angleichen.

---

### [P4 | Minor | Niedrig] QA-336: Laufzeit von Optimize waechst mit dem Stack-Wert; ab 50 ueber 6 s, bei 999 kein Ergebnis in 120 s

**Adressat:** developer
**Betroffen:** `nrplanner/model.py:1182-1191`, `nrplanner/effectfilters.py` (`MOST_STACKS`)
**Umgebung:** A6-Messfall Wylder's Chalice, Deep an, sechs freie Slots, dieser Rechner (Zielgeraet nicht gemessen), nur Night Invader gesetzt

**Reproduktion:** Stacks setzen, `Optimize`.

| Wert | leer | 2 | 4 | 10 | 50 | 100 | 200 | 300 | 999 |
|---|---|---|---|---|---|---|---|---|---|
| s | 1,64 | 1,80 | 2,21 | 3,10 | 8,50 | 14,60 | 28,93 | 43,05 | ueber 45, von mir abgebrochen |

Alle sieben Felder auf 999, zuletzt gewaehltes Gefaess, Deep an: nach 120 s keine Antwort, von
mir abgebrochen. `Cancel` reagiert in 25 ms, das Fenster bleibt bedienbar. Das naechste
`Optimize` mit leerem Feld brauchte danach 12,58 s.

**Erwartet:** A6: `Optimize` unter 6 s. Der Commit nennt 999 die Grenze, damit der Lauf nicht haengt.
**Tatsaechlich:** Bei 999 kam in den gemessenen Zeiten keine Antwort; der Lauf bleibt abbrechbar.
**Analyse:** Hypothese: `compute` legt je Stack eine Kopie an, die Messreihe passt zu linearem Wachstum. Hypothese zu den 12,58 s: der abgebrochene Lauf rechnet noch weiter. Fuer die Werte 0 bis 4 aus dem Nutzerbeispiel hier unkritisch.
**Vorschlag:** Kopien durch Multiplikation ersetzen oder die Grenze senken; Entscheidung beim developer.

---

### [P4 | Minor | Niedrig] QA-337: Why nennt gespeicherte Stack-Werte, die Optimize nicht verwendet

**Adressat:** developer
**Betroffen:** `nrplanner/advisorblock.py:825-829`, gegen `nrplanner/advisorbar.py:964-967`
**Umgebung:** `advisor/stacks` von aussen geaendert; ueber die Oberflaeche nicht erreichbar

**Reproduktion:** `advisor/stacks = 7060200=2,99999999=3,10001=5`, Programm starten, `Optimize`, `Why`.

**Erwartet:** Vorgabe "beschaedigte Werte lesen sich als leer"; `asking_from` filtert solche Ids auch aus.
**Tatsaechlich:** Why listet "Taking attacks improves attack power: 5" und "effect 99999999: 3"; in der Frage steht fuer 10001 weiter 1.
**Vorschlag:** Why liest dieselbe gefilterte Menge wie `asking_from`.

---

### [P4 | Trivial | Niedrig] QA-338: `drive_window.ps1` kennt die Stacks-Spalte nicht

**Adressat:** developer
**Betroffen:** `scripts/drive_window.ps1:190` (`Reg` ohne `stacks`), `:147` (`SetText`)
**Reproduktion:** `Els $f "" "Edit"` im Filterfenster liefert nur das Suchfeld; die Felder sind ueber UIA nicht erreichbar (Tree-Zellen, wie die Kaestchen). `Reg` zeigt `advisor/stacks` nicht.
**Auswirkung:** Fensterlaeufe brauchen ein eigenes Klick- und Tastenrezept (`<SP>/T-336qa/s/keys.ps1`, `PostMessage`). `setAccessibleName` des Felds erreicht UIA nicht.
**Vorschlag:** `Reg` ergaenzen, Klick und Tasten in den Treiber uebernehmen.

## Beobachtungen

- Zeilen mit Feld sind 1,5-mal so hoch wie die uebrigen; ohne Vorgabe, an `ui-ux-designer`.
- Tooltip und Erklaerung: "empty uses the stat sheet's count". Bei abgehaktem Effekt zaehlt die Statistik-Seite ihn nicht, Optimize rechnet mit 1; nur `guide.md` sagt "(one if the sheet says nothing)". Wortlaut stammt aus dem Auftrag; an `ui-ux-designer`.
- Getippt `2.5` wird 25: der Punkt wird stumm verworfen.
- Der Wert gilt je Relikt: zwei Relikte mit Wert 2 zeigen je +14,5 % (wie `compute` es fuer zwei Relikte vorsieht).

## Nicht getestet

- Tooltip per echtem Hover (nimmt dem Nutzer die Maus); Text am Quellstand gelesen.
- 225 %: Der Bildschirm steht heute auf 125 %.
- Zielgeraet und EXE (laut Auftrag nur Quellstand).
- Dauer der Picker-Frage bei 999: die Messung war nicht belastbar.

## Register

Angehaengt an `qa/findings.md`: QA-335 bis QA-338. IDs vorlaeufig fortgezaehlt (hoechste vorher
QA-334, `grep` 07.11.2026), der Director vergibt sie endgueltig. Nicht committet.
