# T-265d — qa-engineer: A9 am Artefakt 1.12.0

```
STATUS: erledigt
AUFTRAG: T-265d (A9: A3-A8 gegen dist/NightreignHelper.exe 1.12.0, dazu A18/A19/A20 und A6-Zeiten am Artefakt)
GELESEN: GOAL.md:26-53, 298-401 (A3-A9, A17, A18-A20) · docs/berichte/T-265-release-manager-build.md · docs/berichte/T-265-release-manager-cleanroom.md (Kopf; Freigabe der Instanzsperre 05:08) ·
         docs/berichte/T-241-qa-engineer.md (Methode, Vergleichszahlen 1.10.0) · docs/berichte/T-253-qa-engineer.md (A18/A19-Kurzcheck 1.11.0) · docs/berichte/T-265-qa-engineer.md (QA-272-Retest) ·
         qa/findings.md (Kopf, QA-096/256/257/258/259/261/272) · nrplanner/{statsheet,damage,weaponslots,arsenaltab,advisorbar,advisorblock,app}.py, nrplanner/advisor/{goals,explain}.py, nrdata/savefile.py ·
         tests/test_attack_power_calibration_against_the_game.py (A20-Zellen)
GEÄNDERT: docs/berichte/T-265d-qa-engineer.md (neu) · qa/findings.md (vier Zeilen angehaengt: QA-273 neu, QA-259, QA-258, QA-256). Kein Commit. EXE nicht angefasst.
ANNAHMEN: (1) Befund-ID QA-273 vorlaeufig von mir vergeben (Dispatch verlangt Registerzeilen); Director bestaetigt. (2) "Hauptthread haelt an" am Artefakt nur von aussen messbar
         (SendMessageTimeout(WM_NULL)-Umlaufzeiten, ~15 ms Takt) — misst jede Blockade, nicht nur die Beraterrechnung. (3) A18-Nachweis "Rangfolge ohne Markierung = heutige Best-case-Rangfolge":
         am Artefakt 1.12.0 gibt es keinen Lesart-Umschalter mehr; der unmarkierte Lauf ist die Rangfolge, der Vergleich gegen 1.11.0 Best case liegt in der Quell-Suite (T-248d/T-253), nicht hier.
         (4) Die Wirkung des 1H/2H-Schalters auf die Rangfolge ist mit diesem Spielstand nicht zeigbar: kein Relikt im Besitz traegt `Improved Attack Power when Two-Handing` (8300000-2), nur
         `Improved Stance-Breaking when Two-Handing` (5 Kopien), das keine Zahl bewegt. Geprueft wurde Schalter, Anzeige, Speicherung und Fremdbau-Isolation.
NÄCHSTER: director (Urteil A9 PASS mit CONCERNS: QA-273 P3, Beobachtungen zur Optimize-Wandzeit) · power-user (Fensterinstanz seit 05:26 frei)
BLOCKIERT DURCH: nichts
```

## Artefakt und Umgebung

| | |
|---|---|
| Artefakt | `dist/NightreignHelper.exe`, 59 118 289 B, SHA-256 `89c2967acaaaaac8ca108935cac0a79c8292d2c7ec0e77831755a15b295f59d8` (selbst gerechnet 05:01, vor dem ersten Start), Commit `79e6089`; `git diff --stat 79e6089 HEAD -- nrplanner nrdata NightreignHelper.spec run.py` leer |
| Prozess | zwei Laeufe (PID 29096/32688 ab 05:09:01, PID 18220/34440 ab 05:24:20), beide Pfad `...\Nightreign-Helper\dist\NightreignHelper.exe`, Fenstertitel `Nightreign Helper 1.12.0`; vor jedem Start `Get-Process NightreignHelper` leer (Freigabe: cleanroom-Bericht lag 05:08:45 vor, die 1.11.0-Instanz des release-manager war beendet) |
| Umlenkung | `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-265qa` (vorher nicht vorhanden, nachher `HKCU\Software\DankYeeterT-265qa\NightreignHelper\{advisor,chalices,...}` — positiver Nachweis), `LOCALAPPDATA`/`APPDATA`/`USERPROFILE` auf Scratchpad `T-265d\`; Testabzug kopiert (841 Dateien, 20 812 293 B, `extract_version` 11 = `EXTRACT_VERSION` 11), Fenster nach ~1 s |
| Spielstand | eingefrorene Kopie `NR0000.sl2` (mtime 14.09. 23:26, 19 531 312 B, SHA-256 `f4940e4b…3540` identisch mit dem Original) unter dem umgelenkten `APPDATA`; `USERPROFILE` leer, damit `Path.home()`-Fallback (QA-255) nicht auf das lebende Original zeigt. **319 Relikt-Kopien**, 110 Builds (`inventory.load` gezaehlt), Anzeige `You own 319 relics in total.`; kein `nightreign.exe` aktiv |
| Rechner | Ryzen 9 5900X, Windows 11 Pro 10.0.26200, 125 % Skalierung (PrintWindow logisch 1622x898). **Nicht das Zielgeraet** (5800H Quiet Mode, Faktor ~5,9 bei S11-A) |
| Steuerung | .NET UIAutomationClient aus PowerShell: Invoke fuer Buttons, Toggle fuer Deep/HandSwitch, RangeValue fuer Level, echte Mausklicks mit Prozess-Wache fuer Heldenkacheln/Kelchliste/Ziel-Combobox; Dialoge als UIA-Nachfahren des Hauptfensters; Bild nur PrintWindow |

## Urteil je Kriterium

| Krit. | Urteil | Beleg am Artefakt |
|---|---|---|
| A3 | **PASS** | Drei benannte Richtungen (`Maximise damage`, `Minimise damage taken`, `Maximise offensive attributes`). Wylder/Wylder's Chalice+Deep/damage und Revenant/Revenant's Chalice+Deep/attributes: je `6 of 6 slots filled`, per `Apply all` in die Slots gesetzt, alle aus dem Besitz. Volle Matrix nicht am Artefakt (Quell-Suite) |
| A4 | **PASS** | Slot-Farben passen (Red→Burning, Yellow→Luminous, White→Drizzly, Deep Red/Blue/Green→Deep Grand Burning/Deep Grand Drizzly/Deep Polished Tranquil; Revenant Blue/Green/White/Deep Blue/Yellow/Green ebenso). Deep-Kennzeichnung: `Deep Slot n`, Fluch `✦ Ultimate Art Charging Impaired … from Deep Polished Tranquil Scene`. Stacking: QA-257-Hauptfall (Revenant/attributes) — `[Revenant] Improved Strength, Reduced Faith` genau einmal im Vorschlag (Slot 3, `Strength +25`), Statsheet `All selected effects stack.` |
| A5 | **PASS** | `Why`-Dialog je Slot `N of its M effects moved a number in this build.` plus Zeile je Wirkung mit Zahl; Kopfzeile `Maximise damage — Wylder, Wylder's Chalice, Deep of Night on, 319 relics considered.`; bedingte Wirkungen tragen ihre Bedingung im Namen (`… with 3+ Daggers Equipped`, `… when facing poison-afflicted enemy`); ausgeschlossene: `you excluded it, so it is not counted.`; tote: `works only for Scholar, and you are Wylder.` |
| A6 | **PASS (auf dieser Maschine)** | Zahlen unten. Zielgeraet nicht verfuegbar. Beobachtung: Wandzeit `Optimize` 1 809 ms Median gegen 1 229 ms in T-241d (1.10.0), Beam in-process unveraendert (900 gegen 858 ms) — siehe Beobachtungen |
| A7 | **PASS** | `only applies under a condition` entfaellt planmaessig (A18); am Artefakt gelesen: `no number here shows what this adds.` · `it depends on the armaments you carry, so no number here.` · `this figure does not count it.` · `Spell damage is not in the game data, so spells are not rated.` · `No armament selected — ranked on attack multipliers only …` (A17) · A19-Fall: `0 of 3 slots filled · 3 slots are blocked by a requirement you marked.` — Programm sagt es statt zu raten; Wortlaut der Begruendung ist QA-273 |
| A8 | **PASS** | 3 717 nicht-leere UIA-Textzeilen (7 Reiter, Hauptfenster, 5 `Why`-Dumps, Picker mit 211 Karten inkl. Tooltips, Effects-Tabelle sichtbare Zeilen): 0 Umlaute, 0 Treffer auf 42 deutsche Woerter (Python-Regex, zwei Masken). Nicht erreicht: nativer Dateidialog |
| A18 | **PASS** | `Improved Attack Power with 3+ Daggers Equipped` (7080000) per Bullet-Button im `Why` markiert → Registry `advisor\excluded=7080000`, Antwort sofort `Nothing suggested yet.`; neuer `Optimize`: Slot 5 wechselt zu `Deep Polished Drizzly Scene` (Greatsword +9 %), Slot 6 behaelt `Deep Polished Tranquil Scene` mit Zeile `you excluded it, so it is not counted.` (Relikt bleibt waehlbar, uebrige Wirkung traegt), Liste `Effects you've excluded:`. Kein Slot zaehlt die Wirkung |
| A19 | **PASS** | Zweiter Klick → `advisor\required=7080000`, `excluded` leer. `Optimize`: Slots 5 und 6 tragen die Wirkung, Liste `Effects you require:`; Build identisch mit dem unmarkierten Lauf (Pflicht war dort schon erfuellt = Rangfolge der freien Optimierung). Deep aus (keine passende Kopie fuer Red/Yellow/White): `0 of 3 slots filled · 3 slots are blocked by a requirement you marked.` — A7-Satz statt stillem Fallenlassen. Persistenz: nach Neustart `Effects you require:` und Pflicht im Vorschlag |
| A20 | **PASS** | Sechs Zellen (Lv15, keine Relikte, Umschalter 1H): Kachel + Werteblatt `Total`: Wylder's Greatsword **122 / 125 2H**, Raider's Greataxe **158 / 180 2H**, Guardian's Halberd **107 / 110 2H**, Duchess' Dagger **72 / 74 2H**; Arsenal (`"Great Stars"`, +1, Rarity Uncommon): Raider **188 / 216 2H**, Wylder **147 / 151 2H**. Umschalter `1H`→`2H` aendert keine Zahl (beide Haende bleiben nebeneinander, AK-286); Speicherung: `chalices\1\1002` endet nach `Apply all` auf `2H`; Revenant Erstbesuch `1H`, `chalices\6` ohne `2H` (QA-272 haelt); nach Neustart Wylder `2H`, Revenant `1H` |

**Gesamturteil A9: PASS mit CONCERNS** — kein P1/P2. Vor dem Release zu entscheiden: QA-273 (P3, Wortlaut der Pflicht-Begruendung), Beobachtung Optimize-Wandzeit (Zielgeraet).

## A6-Zahlen am Artefakt

Messfall S11-A: Wylder, `Wylder's Chalice` (Red/Yellow/White + Deep Red/Blue/Green, Pools 53/55/213/22/33/22), Deep an, Stufe 15, sechs leere Slots, `Maximise damage`, Umschalter 1H, keine Markierung. Kalt je Lauf per `Rescan save` (Antwort nach 210-230 ms verworfen).

| Zahl | Budget | gemessen | Lesart |
|---|---|---|---|
| `Optimize`, Invoke bis Antwort sichtbar | < 6 s | **1 809 ms Median** (Block 1: 1752, 1768, 1809, 1872, 1877; Block 2: 1741, 1752, 1817, 1856, 1870 → Median 1817), n=10 | inkl. ~370 ms UIA-Latenz bis erste sichtbare Aenderung und 250 ms `WAIT_VISIBLE_MS` (`Working out …` bei 630-750 ms). In-process Quellstand `scripts/measure_advisor_search.py` gleiche Umlenkung: pre-sort 53 ms, **Beam 854,5 ms**, whole run 899,7 ms Median von 3, 3621 Bewertungen (T-241d: 858 ms, 3621) |
| Slot-Frage, weisser Slot 3 (211 Kandidaten) | < 500 ms Median | Rangfolge steht beim Erscheinen des Dialogs: 211 Karten, **0 pending** in 5 von 5 Laeufen; Dialog sichtbar nach **1 747 ms Median** (1642, 1741, 1747, 1823, 1859) | Der Dialogbau ist QA-258 (unveraendert: Hauptthread-Blockaden 1 050-1 536 ms je Oeffnung, 4-6 Umlaeufe ≥ 50 ms) |
| Hauptthread waehrend `Optimize` | < 50 ms | **1 von 5 009 Umlaeufen ≥ 50 ms** (62,1 ms, erster Kaltlauf nach Programmstart); uebrige 9 Laeufe max 19-40 ms, p50 0,07 ms | Der eine Ausreisser fiel in den ersten Lauf nach Start und Erst-`Rescan`; in 9 weiteren Kaltlaeufen und 5 Einzellaeufen (max ≤ 38 ms) nicht wiederholt — nicht der Beraterrechnung zuzuordnen (Annahme 2) |

## Befunde

### [P3 | Minor | Mittel] Pflicht-Begruendung behauptet "No copy you own carries …", obwohl Kopien im Besitz sind — QA-273

**Adressat:** developer (Satzentscheidung), ui-ux-designer (Wortlaut)
**Betroffen:** `nrplanner/advisor/explain.py:929-946` (`required_but_unmet`: `uncarried` wird ueber die Pools der *freien Slots* entschieden, der Satz spricht ueber den *Besitz*)
**Umgebung:** Artefakt 1.12.0, Spielstand 319 Kopien; Wylder, `Wylder's Chalice`, Deep of Night **aus**, `Improved Attack Power with 3+ Daggers Equipped` (7080000) als `Must include` markiert.

**Reproduktion:**
1. Deep an, Effekt 7080000 im `Why` zweimal klicken (→ required); `Optimize` liefert 6/6 mit der Wirkung in Deep Slot 2 und 3.
2. Deep aus; `Optimize`.
3. Leiste: `Maximise damage — 0 of 3 slots filled · 3 slots are blocked by a requirement you marked.` `Why`: `No copy you own carries Improved Attack Power with 3+ Daggers Equipped, which you marked as required — no suggestion can meet that.`

**Erwartet:** Ein wahrer Satz: keine Kopie **passt in die freien Slots** (beide Kopien sind Deep-Relikte, Deep ist aus) — A7 "sagen statt raten" verlangt eine zutreffende Aussage.
**Tatsaechlich:** Der Spieler besitzt zwei Kopien (`Deep Polished Tranquil Scene`, `Deep Grand Drizzly Scene`, `inventory.load` gezaehlt), die der Satz verneint.
**Analyse:** Der Docstring nennt den Satz "a fact about what is owned", die Entscheidung faellt aber ueber `pool.candidates` der freien Slots, die Deep-Relikte bei Deep aus (oder bei fehlender Slot-Farbe) nicht enthalten. Hypothese: gleicher Fehltext, wenn eine Kopie nur in einer Farbe existiert, die der Kelch nicht bietet.
**Auswirkung:** Der Spieler sucht die Ursache im Besitz statt bei Deep/Kelch; er koennte die Markierung loeschen, obwohl Deep an das Problem loest.
**Vorschlag:** Besitz gegen das Inventar pruefen und drei Saetze unterscheiden: nicht im Besitz / nur auf Deep-Relikten (Deep ist aus) / passt in keine freie Slot-Farbe. Test rot-vorher: Pflicht auf 7080000, Deep aus, Erwartung enthaelt "Deep".

## Beobachtungen (keine Befunde)

- **Optimize-Wandzeit +47 % gegen 1.10.0 bei unveraendertem Beam:** 1 809 ms gegen 1 229 ms (T-241d, gleiche Maschine, gleiche Methode), Beam in-process 900 gegen 858 ms. Die Differenz (~0,5 s) liegt zwischen Beam-Ende und Antwort (Erklaerung/Uebergabe; A18 zaehlt jetzt 413 bedingte Effekte, mehr Zeilen je Slot). Auf dem Zielgeraet (S11-A Beam 5,0 s, Faktor ~5,9) waere die Antwort **hochgerechnet, nicht gemessen** nahe oder ueber 6 s. Empfehlung an `performance-tuner`: Post-Beam-Phase einmal trennen und auf dem Zielgeraet messen.
- Der Berater zaehlt in einem Build `3+ Thrusting Swords`, `3+ Great Hammers`, `3+ Hammers` und zweimal `3+ Daggers` gleichzeitig (Slots 1, 2, 3, 5, 6 des unmarkierten Laufs) — nach A18 korrekt (alle bedingten Effekte zaehlen, bis ausgeschlossen), aber die vier Bedingungen sind mit sechs Waffenplaetzen nicht gemeinsam erfuellbar. Frage unten.
- Nach `Apply all` desselben Builds zeigt das Werteblatt `Total 122 / 125 2H no change` (bedingte Effekte zaehlen dort nur deklariert), waehrend der Berater +20 % x5 gezaehlt hat — AD-036.6 gegen Deklaration, Frage unten.
- Der 1H/2H-Schalter auf einem **leeren** Gefaess wird nicht gespeichert (`_store_chalice` schreibt leere Builds nie; `chalices\1\1002` entstand erst mit `Apply all`) — Tooltip sagt "Saved with this build", also konsistent; Frage unten.
- Der Bullet-Button (`MarkButton`) liefert per UIA weder `Name` noch `HelpText` (Tooltip intern gesetzt, `MARK_TOOLTIPS`); ein Screenreader haette keine Beschriftung. Nicht Ziel des Auftrags.
- Wortlaut in der Leiste `3 slots are blocked by a requirement you marked.` und im `Why` sind konsistent; `Why` erschien in 186-303 ms.
- Bildbeleg `scratchpad\T-265d\out\wylder-chalice-2h-applied.png` (PrintWindow, logisch 1622x898 bei 125 %, rechter Rand durch den nicht DPI-bewussten Aufnehmer beschnitten — Aufnahmefehler, nicht Programm).

## Explorationsprotokoll

Gehalten: Start mit kopiertem Testabzug (~1 s) · `Rescan save` 15x (Antwort verworfen, Zaehler bleibt 319) · `Optimize`/`Cancel`-Wechsel · `Apply all` → `Applied. Undo puts your slots back as they were.` · Markierung im `Why` invalidiert die Antwort sofort (`Nothing suggested yet.`, `Why`/`Apply all` weg) · Zyklus neutral→excluded→required ueber zwei Klicks, Registry folgt · `Why` 8x oeffnen/schliessen · Picker 6x oeffnen/schliessen · Reiterwechsel alle 7 · Reset Chalice (leert Slots, springt auf ersten Kelch, Deep aus) · Level 15 per RangeValue · Deep an/aus · Heldenwechsel Wylder/Raider/Guardian/Duchess/Revenant · Arsenal-Suche `"Great Stars"` (8 Kacheln) · Beenden per WindowPattern.Close (kein Restprozess) · Neustart (Held, Kelch, Deep, Hand, Markierung wiederhergestellt).
Nicht gehalten: QA-273 (Wortlaut); QA-258 unveraendert.

## Offene Fragen

- **director / ui-ux-designer:** Soll die A18-Grundlinie einander ausschliessende Waffenzaehl-Bedingungen (`3+ Daggers` + `3+ Hammers` + `3+ Thrusting Swords` + `3+ Great Hammers` in einem Build) gemeinsam zaehlen, oder gehoert eine Klasse "hoechstens zwei Waffentypen zu dritt" in die Grundlinie? Heute: Spec-konform (A18), Ergebnis fuer den Spieler aber nicht gleichzeitig erreichbar.
- **ui-ux-designer:** Berater (`+20 % x5` gezaehlt) und Werteblatt (`no change`) widersprechen sich nach `Apply all` sichtbar auf einem Schirm — reicht der Hinweis in den Situational-Zeilen, oder braucht die Leiste einen Satz dazu?
- **director:** Hand-Schalter auf leerem Gefaess geht beim Neustart auf `1H` zurueck (Build wird nicht gespeichert). Absicht ("Saved with this build") oder Luecke?

## Nicht getestet

- Zielgeraet (5800H, Quiet Mode): A6 dort weiter nur ueber S11 belegt.
- Wirkung des 1H/2H-Schalters auf die Rangfolge (kein `when Two-Handing`-Angriffseffekt im Besitz, Annahme 4); Quell-Tests `test_two_handed_switch.py`/`test_attack_power_calibration_against_the_game.py` (40 passed, 8,8 s, `79e6089`) decken es.
- `Minimise damage taken` am Artefakt (T-241d gefahren; Richtung unveraendert seit 1.10.0 ausser A18).
- Volle Matrix Nightfarer x Kelch, nativer Dateidialog, Favoriten, Speichern/Loeschen von Builds, Update-Pfad (release-manager clean-room), volle pytest-Suite (T-265 Retest: 1687/10 auf 02e0721; Code seit dem Bau unveraendert).

## QA-Log (angehaengt an `qa/findings.md`)

Vier Zeilen: QA-273 (neu, offen, P3), QA-259 (A20 am Artefakt bestaetigt → behoben), QA-258 (am Artefakt 1.12.0 unveraendert teilweise), QA-256 (kein Konflikt in diesem Lauf, Ablauf mit Wartebedingung hat gehalten).
