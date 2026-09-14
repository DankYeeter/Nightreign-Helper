# T-241d — qa-engineer: A9 am Artefakt 1.10.0

```
STATUS: erledigt
AUFTRAG: T-241d, Teil qa-engineer (A9: A3-A8 gegen dist/NightreignHelper.exe, A6-Zeiten am Artefakt)
GELESEN: docs/tasks/T-241.md · GOAL.md:26-53 · docs/perf/baselines.md (Umgebung, S11-A, S11-B, S11-H, S11-I) ·
         docs/berichte/T-241-release-manager-build.md · docs/archiv/berichte/T-118-performance-tuner.md (P5) ·
         docs/archiv/berichte/T-070-qa-engineer.md (UIA-Weg) · qa/findings.md (QA-002, QA-208, QA-255, QA-256, Kopf) ·
         UI_SPEC.md (AK-09, AK-215) · nrplanner/{model,stacking,advisorbar,relicpicker,savereader,gamepath,
         singleinstance,app}.py, nrplanner/advisor/{run,worker,search}.py, nrdata/savefile.py, scripts/measure_advisor_search.py
GEÄNDERT: docs/berichte/T-241-qa-engineer.md (neu) · qa/findings.md (drei Zeilen angehaengt: QA-257, QA-258, QA-256-Nachtrag). Kein Commit.
ANNAHMEN: (1) Der Spielstand konnte nicht ueber den Dialog gewaehlt werden: die Automatik findet ihn trotz APPDATA-Umlenkung
         ueber Path.home() (QA-255), der Knopf "Find my save..." erscheint nur ohne Fund (app.py:2331). Gelesen wurde
         dieselbe Datei NR0000.sl2 (mtime 13.09. 19:17, 19 531 312 B), nur lesend. (2) "Hauptthread haelt an" ist am Artefakt
         nur von aussen messbar: SendMessageTimeout(WM_NULL)-Umlaufzeiten gegen das Fenster, Abtastung alle ~15 ms; eine
         Blockade >= 50 ms erscheint darin zwingend als Umlauf >= 50 ms. Das misst jede Blockade, nicht nur die Beraterrechnung.
         (3) Befund-IDs QA-257/QA-258 vorlaeufig von mir vergeben, weil der Dispatch Registerzeilen verlangt; Director bestaetigt.
NÄCHSTER: director (Urteil FAIL wegen QA-257 P2 — Fixauftrag oder WAIVED mit Eigentuemer, Geltungsbereich, Ablaufdatum)
BLOCKIERT DURCH: nichts
```

## Artefakt und Umgebung

| | |
|---|---|
| Artefakt | `dist/NightreignHelper.exe`, 59 083 369 B, SHA-256 `314ca35c9afa9bd71c6fae9928bc0e1e4abdbe19814bbb099cca11a04a3930bd` (selbst gerechnet vor dem ersten Start), Commit `9e8933d`; `git diff --stat 9e8933d HEAD -- nrplanner nrdata *.spec run.py requirements.txt` leer (kein Code seit dem Bau) |
| Prozess | beide PIDs mit Pfad `...\Nightreign-Helper\dist\NightreignHelper.exe`, Fenstertitel `Nightreign Helper 1.10.0`; Bundle (`_MEI`-Ordner) enthaelt `data/icon.ico` und `paramdefs/`, kein `nightreign_data.json`, kein `icons/` |
| Umlenkung | `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-241qa` (positiv: `HKCU\Software\DankYeeterT-241qa\NightreignHelper\{builds,chalices,ui}` nach dem Lauf vorhanden), `LOCALAPPDATA`/`APPDATA` auf Scratchpad `T-241\`; Testabzug kopiert (841 Dateien, 20 812 293 B), Fenster nach ~1 s statt Neubau |
| Daten | 314 Relikt-Kopien, 110 Builds (`inventory.scan` gezaehlt), Anzeige `You own 314 relics in total.`; Datenabzug `data_version 10350000`, `extract_version 11` |
| Rechner | AMD Ryzen 9 5900X 12C/24T, 3701 MHz, Energieplan Balanced, Windows 11 Pro 10.0.26200, Bildschirm 5120x2160, Skalierung 125 % (UIA physisch 2010x1075 zu GetWindowRect logisch 1622x898; Startbreite 1608 px logisch = QA-248). **Nicht das Zielgeraet der Baselines** (Ryzen 7 5800H, 1102 MHz, Quiet Mode): Rechenlastprobe **125 ms** Median (n=5: 125,125,122,123,125) gegen 1205 ms dort |
| Steuerung | .NET `UIAutomationClient` aus PowerShell (Invoke/Toggle/RangeValue/WindowPattern), Liste und Combobox per echtem Mausklick mit Prozess-Wache (UIA `Select` verschiebt bei QListWidget/QComboBox nur die Markierung, nicht die aktuelle Zeile — Beobachtung, kein Befund); Bild nur `PrintWindow` |

## Urteil je Kriterium

| Krit. | Urteil | Beleg am Artefakt |
|---|---|---|
| A3 | **PASS** | Zielwahl bietet drei benannte Richtungen (`Maximise damage`, `Minimise damage taken`, `Maximise offensive attributes`). Stichprobe 3 Nightfarer x 3 Kelche x 3 Richtungen, jeweils `6 of 6 slots filled` aus dem Bestand und per `Apply all` in die Slots gesetzt (Wylder/Wylder's Chalice+Deep/damage; Guardian/Guardian's Goblet+Deep/survival; Revenant/Revenant's Chalice+Deep/attributes). Volle Matrix "jeder Nightfarer x jedes Layout" nicht am Artefakt gefahren (Quell-Suite, QA-191) |
| A4 | **FAIL** | Slot-Farben: alle gesetzten Relikte passen zur Slot-Farbe (Red->Burning, Blue->Drizzly, Green->Tranquil, Yellow->Luminous/Dark Night, White beliebig). Deep-Kennzeichnung: `Deep Slot n`, Deep-Relikte, Fluch-Marke `✦`. **Stacking verletzt: QA-257** — dieselbe Exklusivgruppen-Wirkung wird in zwei Slots empfohlen und doppelt gezaehlt |
| A5 | **PASS** | `Why`-Dialog: je Slot `N of its M effects moved a number in this build.` plus Zeile je Wirkung mit Zahl (`Holy Attack Power Up +2: Holy Attack +6.5%`), ausgelassene Wirkungen mit Grund; Kopfzeile nennt Richtung, Lesart, Nightfarer, Kelch, Deep, 314 relics considered |
| A6 | **PASS (auf dieser Maschine)** | Zahlen unten. Zielgeraet nicht verfuegbar: dort gilt weiter S11 (5,0 s / 315 ms Worker / 7 ms Hauptthread); das Artefakt traegt gegen den Quellstand keinen messbaren Aufschlag (816 ms gegen 858 ms, s. u.). Beobachtung QA-258 (Picker-Aufbau friert das Fenster ~1,5 s) liegt ausserhalb der drei Zahlen |
| A7 | **PASS** | Am Artefakt gelesen: `only applies under a condition, so no number here.` · `no number here shows what this adds.` · `Nothing on this relic moved a number in this build — it fills the slot without changing the figure.` · `Spell damage is not in the game data, so spells are not rated.` · `Effects that convert one damage type into another are not in this figure: how the game applies them cannot be read out of the files, so they are named rather than guessed at.` · Picker-Kopf: `94 of your relics carry effects that only apply under a condition. They were not counted.` · `5 of your relics change what damage type ... This figure does not count that change.` · Werte `no change`/`—` statt Null |
| A8 | **PASS** | 5 544 UIA-Textzeilen aus allen 7 Reitern, Hauptfenster, `Why`-Dialog und Picker: 0 Zeilen mit ae/oe/ue/ss-Umlauten, 0 Treffer auf 40 deutsche Woerter (einziger Treffer der Maske `Additional Night Boss`, englisch). Nicht erreicht: der native Dateidialog (Annahme 1) |

**Gesamturteil A9: FAIL** — ein Befund P2 (QA-257). Mindestens zu beheben oder vom Director mit Eigentuemer, Geltungsbereich und Ablaufdatum in WAIVED zu wandeln: QA-257. Kein Regressionsbefund von 1.10.0 (beide Codestellen von 2026-08-10/11).

## A6-Zahlen am Artefakt

Messfall wie S11-A: Wylder, `Wylder's Chalice` (Slots Red/Yellow/White, Deep Red/Blue/Green, Pools 53/54/208/23/32/21), Deep of Night an, Stufe 15, sechs leere Slots, nichts gehalten, `Maximise damage`, `Worst case`. Kalt erzwungen durch `Rescan save` vor jedem Lauf (leert beide Berater-Caches; Gegenprobe: derselbe Lauf ohne Rescan antwortet nach 413 ms ohne `Working out`-Phase, kalt nach ~1 230 ms mit ihr).

| Zahl | Budget | gemessen (n=5) | Lesart |
|---|---|---|---|
| `Optimize`, Invoke bis Antwort auf dem Schirm | < 6 s | **1 229 ms Median** (1197, 1224, 1229, 1229, 1256) | Obergrenze inkl. ~380 ms UIA-Latenz bis zur ersten sichtbaren Aenderung und 250 ms `WAIT_VISIBLE_MS`; Rechenanteil ~816 ms = kalt minus Cache-Treffer; Quellstand in-process auf derselben Maschine `scripts/measure_advisor_search.py`: 858,3 ms Median, 3621 Bewertungen (identisch mit S11-A) |
| Slot-Frage, weisser Slot (206 Kandidaten) | < 500 ms Median | **5 ms Median** nach Erscheinen des Dialogs (7, 4, 5, 4, 5) | Der Dialog erscheint bereits mit Rangfolge und Chips (`BEST FOR DAMAGE`, Wert `+0.1`); `…` (PENDING) wurde in keinem Lauf gesehen. Invoke bis Dialog sichtbar: 1 810 ms Median (1797, 1797, 1810, 1852, 1893) — das ist Dialogbau, siehe QA-258 |
| Hauptthread waehrend `Optimize` | < 50 ms | **max 25,6 ms**, 0 von 2 862 Umlaeufen >= 50 ms (5 Laeufe je ~573 Umlaeufe in 9 s; p50 0,054 ms) | Fenster antwortet durchgehend; `Cancel` steht waehrend der Rechnung |
| Hauptthread beim Oeffnen des Pickers | (A6 zaehlt Beraterrechnung) | zwei Blockaden je Oeffnung: **685-777 ms** und **839-883 ms**, dazu 3 x 44-65 ms | Nicht vom Berater: `SlotAdvice.ask()` ist 7 ms (S11-I), der Worker rechnet ausserhalb. Am Artefakt nicht trennbar von Kartenbau/Layout (S11-H: 18,5 ms je Karte offscreen auf dem Zielgeraet) |

## Befunde

### [P2 | Major | Hoch] Eine Exklusivgruppen-Wirkung wird in zwei Slots empfohlen und doppelt gezaehlt — QA-257

**Adressat:** developer
**Betroffen:** `nrplanner/model.py:958-1015` (Duplikate nur ueber `stacks`, Exklusivgruppe nur als Warnung fuer *verschiedene* Namen, `if pair[0] == pair[1]: continue`) gegen `nrplanner/stacking.py:120-146` (`repetition` → `EXCLUSIVE`, "one of the group applies") und `nrplanner/effectstab.py:1025`; `nrplanner/advisor/search.py:4-7` setzt voraus, dass die Bewertung Exklusivgruppen honoriert.
**Umgebung:** Artefakt 1.10.0, echter Spielstand (314 Kopien), Testabzug 11.

**Reproduktion (am Artefakt):**
1. Revenant, `Revenant's Chalice`, Deep of Night an, Stufe 15, Slots leer, Richtung `Maximise offensive attributes`, `Optimize`, `Apply all`.
2. Slot 3 `Grand Luminous Scene` und Deep Slot 3 `Deep Polished Tranquil Scene` tragen beide `[Revenant] Improved Strength, Reduced Faith`.
3. `Why`: beide Zeilen `Strength +25` und `Faith -6, counted against it`. Statsheet ATTRIBUTES: `Strength 21 +53 74`, `Faith 51 -6 45` (= 25+25+3 bzw. -6-6+3+3).
4. Reiter `Effects & chances`, Spalte Stacking derselben Wirkung (aus dem Quellstand gelesen, `stacking.classify`): `Exclusive group (no number)`.

**Erwartet:** Nach der eigenen Regel des Programms ("exclusivityId: one of the group applies", `model.py`: "only one will apply") zaehlt die zweite Kopie nichts; der Berater empfiehlt sie nicht bzw. bewertet den Build ohne sie.
**Tatsaechlich:** Beide Kopien zaehlen voll, keine Warnung, `STACKING: All selected effects stack.`; der Berater waehlt das Paar wegen des verdoppelten Werts.

**Analyse:** `model.compute` prueft Duplikate nur ueber `eff["stacks"]` (isStrongestEffect). Die 64 Wirkungen mit `exclusivity > 0` tragen `stacks = True`; die Exklusivpruefung erzeugt nur Warnungen fuer Paare verschiedener Namen und reduziert die Summen nie. Quellstand-Minimalfall: `model.compute(revenant, 15, [e, e])` → Strength +50, Faith -12, `warnings == []`; `stacking.repetition(e) == "exclusive group"`. Umfang (gezaehlt): 64 Wirkungen mit Gruppe, 29 Gruppen, davon 27 mit einem Mitglied; bei 23 davon veraendert die zweite Kopie die Summen (die zwanzig `[Nightfarer] Improved X, Reduced Y` plus `Increased Maximum HP/FP/Stamina` ids 7000090/7000190/7000290). Im Spielstand tragen 75 Relikte eine solche Wirkung (46 verschiedene), 12 Wirkungen liegen in 2-4 Kopien vor — darunter HP/FP/Stamina je 2 und `[Duchess] Improved Vigor and Strength, Reduced Mind` 4. Beide Codestellen stammen vom 10./11.08.2026 (`cec61c7`, `1b2df01`): kein Regressionsbefund von 1.10.0. Ob das Spiel selbst so rechnet, ist hier nicht pruefbar; der Befund ist der Widerspruch zweier Programmteile (A4: "bestehende Regeln des Programms").
**Auswirkung:** Fuer `Maximise offensive attributes` und `Minimise damage taken` bevorzugt der Berater Paare identischer Exklusivwirkungen (Statistikbonus, HP/FP/Stamina) und meldet Zahlen, die der Effects-Reiter widerlegt; der Statsheet zeigt dieselben ueberhoehten Summen auch bei Handbelegung.
**Vorschlag:** Richtung klaeren (welcher Teil hat recht) und dann eine Quelle: Duplikat-Regel im `model.compute` an `stacking.repetition` haengen (zweite Kopie einer `EXCLUSIVE`-Wirkung wie `STRONGEST` behandeln, mit Warnung), Test mit zwei Kopien von 6645100 (rot vorher: Strength +50).

### [P3 | Minor | Hoch] Oeffnen des weissen Slot-Pickers friert das Fenster ~1,5 s ein (auf dieser Maschine) — QA-258

**Adressat:** director (Entscheidung), developer, ui-ux-designer
**Betroffen:** `nrplanner/relicpicker.py` (Kartenbau `RelicPicker.__init__`, 206 `RelicCard`), `nrplanner/relicslots.py:337` (`_open_picker`, modaler `exec()`)
**Umgebung:** wie A6-Messfall, Slot 3 White, 206 Kandidaten, Ryzen 9 5900X.

**Reproduktion:** Slot 3 oeffnen; Umlaufzeit-Sonde gegen das Hauptfenster: je Oeffnung zwei Blockaden 685-777 ms und 839-883 ms (5 von 5 Laeufen), Dialog nach 1 810 ms Median sichtbar; die Rangfolge steht dann schon.
**Erwartet / Lesart A:** AK-09 (250 ms fuer "eine Rechnung") und A6 Satz 1 ("das Fenster bleibt bedienbar") gelten sinngemaess auch fuer den Weg zum Berater; ein 1,5-s-Freeze auf dem Hauptweg (AD-018) ist ein Mangel. **Lesart B:** AK-215 nimmt die Wartezeit des Pickers bewusst ohne Anzeige hin, A6 zaehlt nur Beraterrechnung; der Aufbau ist Widget-Bau, kein Befund.
**Analyse:** Deckt sich mit T-118 P5 (08.09.: 18,5 ms je Karte offscreen, hochgerechnet ~3,8 s fuer 206 Karten auf dem Zielgeraet) — an `ui-ux-designer`/`developer` uebergeben, seither ohne Registereintrag und ohne Bildschirm-Messung (Suche `Dialogbau`/`S11-H`/`P5` in qa/, docs/state.md, docs/plan-restarbeiten.md, DESIGN_REVIEW.md, UI_SPEC.md: 0 Treffer ausser Baselines und T-118/T-140). Auf dem Zielgeraet (Faktor ~5,9 bei S11-A: 5024 ms gegen 858 ms) waeren es hochgerechnet mehrere Sekunden — **hochgerechnet, nicht gemessen**.
**Vorschlag:** Vor dem Ingame-Test einmal auf dem Zielgeraet messen (Klick bis Dialog); danach entscheiden, ob Kartenbau verzoegert/gebuendelt wird.

### Nachtrag zu QA-256 (Einzelinstanz-Sperre, Paralleltests)

Meine erste Instanz (Start 08:29:47, PID 24132/3108) war um 08:31:17 weg, als die clean-room-Kopie startete (PID 11708/9800, `scratchpad\T241d-cleanroom\install\`); kein Absturzereignis im Anwendungsprotokoll. Ein paralleler Lauf hat also nicht nur gewartet, sondern eine fremde laufende Instanz beendet. Vorher hatte ich 23 min auf die power-user-Kopie gewartet (08:05-08:29). Zweiter Start 08:33:40 blieb bis zum Ende (09:02) stabil. Prozessregel wie QA-256, Zusatz: vor `Stop-Process` PID und Pfad pruefen.

## Beobachtungen (keine Befunde)

- QA-208 (`qa/findings.md:230`) steht auf `offen` (08.09.), obwohl S11-I (T-140) den Hauptthread-Anteil der Slot-Frage mit 7 ms misst und dieser Lauf 5 ms nach Dialog bestaetigt — Statuskorrektur pruefen.
- `Grand Burning Scene` fuer Wylder empfohlen mit `[Guardian] ... — not working (Guardian only)`: die tote Wirkung ist durchgestrichen und zaehlt nichts (Why: "works only for Guardian, and you are Wylder."), Wahl wegen `Holy Attack Power Up +2` — regelkonform.
- UIA `Select` auf `QListWidget`/`QComboBox` verschiebt nur die Markierung (Kelchliste zeigte `Wylder's Chalice` markiert, Slots blieben `Wylder's Urn`); ein Screenreader-Nutzer koennte das treffen. Nicht Ziel des Auftrags, nicht als Befund gefuehrt.
- Bildbeleg `scratchpad\T-241\out\revenant-attributes-applied.png` (PrintWindow, logisch 1622x898 bei 125 %, Statsheet rechts durch den nicht DPI-bewussten Aufnehmer beschnitten — Aufnahmefehler, nicht Programm).

## Explorationsprotokoll

Gehalten: Start mit kopiertem Testabzug (kein Neubau, Fenster ~1 s) · Spielstand-Lesen im Hintergrund (`Rescan save`: Antwort nach ~210 ms verworfen, Zeile bleibt) · `Optimize`/`Cancel`-Wechsel · `Apply all` → `Applied. Undo puts your slots back as they were.` + `Undo apply` · `Clear` → `Nothing suggested yet.` · Cache-Treffer 413 ms gegen kalt 1 229 ms · `Why` oeffnen/schliessen · Picker oeffnen/schliessen 6x (WindowPattern.Close) · Reiterwechsel alle 7 · Reset Chalice leert Slots, springt auf ersten Kelch und Deep aus (wie `reset_chalice` dokumentiert) · Level-Slider per RangeValue 1→15 · Deep-Toggle · Heldenkacheln per Klick (UIA Toggle ohne Wirkung).
Nicht gehalten: nichts ausser QA-257/QA-258.

## Nicht getestet

- Zielgeraet (5800H, Quiet Mode): nicht in dieser Sitzung verfuegbar; A6 dort weiter nur ueber S11 belegt.
- Volle Matrix Nightfarer x Kelch-Layout am Artefakt (Quell-Suite deckt sie; nicht wiederholt).
- Nativer Dateidialog (`Find my save...`) und A15-Pfaddialog — power-user/clean-room, und wegen QA-255 hier nicht provozierbar.
- Volle pytest-Suite: nicht gefahren (Auftrag ist das Artefakt; Codestand unveraendert seit 9e8933d; Pruefphase 07:50 laut docs/state.md — abgeleitete Quelle).
- Statsheet-Zahlen gegen das Spiel (QA-095-Formel), Best-case-Lesart (nur `Worst case` gemessen), Favoriten, Speichern/Loeschen von Builds im umgelenkten Register.
