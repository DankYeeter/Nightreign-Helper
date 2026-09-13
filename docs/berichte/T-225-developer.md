# T-225 — Developer-Bericht (13.09.2026)

```
STATUS: teilweise
AUFTRAG: docs/tasks/T-225.md — AK-264, AK-266, AK-267, AK-05/AK-194-Waechter am laufenden Fenster, AK-268
GELESEN: docs/tasks/T-225.md (ganz); CLAUDE.md; UI_SPEC.md Z. 190-225 (AK-264), 1060-1085 (AK-05), 1950-1990 (AK-267), 2078-2135 (AK-266), 3258-3280 (AK-268), 3439-3480 (AK-194); ARCHITECTURE.md AD-033; docs/berichte/T-218-developer.md, T-224-developer.md; nrplanner/firstrun.py, relicpicker.py (Groessenwahl, _refresh, done), app.py (showEvent, _opening_width, _the_save_has_been_read, _on_save_read, _on_save_failed, _hand_the_stock_to_the_slots, RelicSlot.populate, _open_picker), advisorbar.py (Zeile, _ElidingLabel, GOAL_BOX_WIDTH, answerable); tests/conftest.py, rendered.py, test_first_run_panel.py, test_relic_picker_geometry.py, test_relic_picker_advisor.py, test_advisor_bar.py, test_advisor_apply.py, test_differential_track.py; scripts/differential/mutate.py
GEÄNDERT: nrplanner/firstrun.py, relicpicker.py, app.py; tests/test_first_run_panel.py, test_relic_picker_geometry.py, test_relic_picker_advisor.py, test_advisor_bar.py, test_advisor_apply.py, conftest.py, advisor_row_at_the_window.py (neu); scripts/differential/mutate.py. Commits 544b3fa (a), deabb80 (b), 459f2d2 (c), 1855ed2 (d), 1a36c53 (e), 4d4644f (Mutationen) auf worktree-agent-a95ed3f94b076b9f5 (enthaelt 4017938), kein Push. Arbeitsbaum sauber.
ANNAHMEN: (1) "am laufenden Fenster, nicht offscreen" = Windows-Plattform in einem Kindprozess, Fenster mit WA_DontShowOnScreen (gemessen: gleiche Zahlen wie gezeigt) — keine Fensterblitzer waehrend der Suite. (2) AK-194-Bezugsbreite = dieselbe abgeleitete Startbreite wie AK-05 (Director 13.09.). (3) "Text abgeschnitten" = Beschriftung breiter als Textfeld (Box: SC_ComboBoxEditField; Knopf: Breite minus 2x PM_ButtonMargin; Label: Breite) oder Widget ausserhalb der Zeile — nicht sizeHint, weil Fusion jedem Knopf 80 px vorschreibt. (4) Die Kurzform Worst/Best ist NICHT gebaut (Befund 2).
NÄCHSTER: Director entscheidet Befund 1 (Vorschlagszustand passt nicht in die Startbreite) und Befund 2 (Kurzform-Hebel misst 0 px); danach `pytest -n auto` — von mir NICHT mehr gefahren (Zugschwelle), erwartet 1 failed (Befund 1) sonst gruen; Mutation d und e im Mutantenbaum nachfahren.
BLOCKIERT DURCH: Zugschwelle (150 Werkzeugaufrufe) vor dem Suitelauf und vor den Mutationen d/e.
```

## Je Abschnitt

| | Status | Test | Rot/Gruen | Zahlen | Commit |
|---|---|---|---|---|---|
| a AK-264 | erledigt | `test_e1_says_when_the_folder_lies_outside_every_steam_library`, `test_a_complete_game_outside_every_steam_library_is_turned_down` (E1_OUTSIDE_STEAM neue Headline) | rot 2/66 → gruen 66 | Suche `does not hold a copy`: Code nur firstrun.py:335 (inside-Zweig), Tests Z. 52, sonst Doku | 544b3fa |
| b AK-266 | erledigt | `test_the_height_asked_for_is_the_figure_of_the_sizing_and_stays_it` (Spy auf `_fit_to_three_rows`, T-218-Rezept) | rot (offscreen 1203 ≠ 1179) → gruen 7/7 | laufendes Fenster (Windows, Fusion, dpr 1,25, avail 1728): Groessenwahl wanted 1061 / height 1061; nach Antwort wanted_height **1061** == height **1061**; frisch waeren 406+715 = 1121 | deabb80 |
| c AK-267 | erledigt | `test_a_rescan_that_finds_no_save_takes_the_cards_out_of_the_picker` (T-218a umgedreht), neu `test_a_picker_standing_open_loses_its_cards_with_the_save` | rot 2 (55 alte Karten) → gruen; Nachbarsuiten 128 passed | Bestand geht in `_the_save_has_been_read` an jedem Ende an die Karten; `RelicSlot.stock_replaced` → offener Picker `_refresh`, `done()` trennt | 459f2d2 |
| d AK-05/194 | teilweise | `test_at_the_opening_width_only_the_status_is_shortened`, neu `..._the_status_keeps_some_width` (bar); `..._no_action_button_is_cut` (apply) — Sitzungs-Fixture `advisor_row_at_the_window` | 4.12-Zustand: gruen auf HEAD, rot mit 400-px-Box (status '' / 0 > 0). Vorschlagszustand: **rot auf HEAD** (Befund 1) | Fenster **1350** = `_opening_width()`, Zeile 498; Statuszeile **67 px** (4.12), nichts abgeschnitten; Vorschlagszustand: Statuszeile **0 px**, goal_box 66, reading_box 67, Knoepfe 66/67 — Bedarf 683 px | 1855ed2 |
| e AK-268 | erledigt | `test_without_a_save_the_row_says_so_and_disables_its_own_two_controls` + `reading_box.isEnabled() is False` | rot mit entfernter setEnabled-Zeile → gruen | | 1a36c53 |

**Mutationen** (Registry 4d4644f, `test_differential_track.py` 49 passed; gefahren gegen `git archive HEAD` im Scratchpad): `e1-headline-ignores-the-origin` getoetet (2 rot), `wanted-height-is-read-afresh` getoetet (1 rot), `cards-keep-the-stock-of-a-save-no-longer-held` getoetet (2 rot); `goal-box-400-px` und `reading-box-stays-live-without-a-save` **nicht im Mutantenbaum gefahren** (Zugschwelle) — dieselben Aenderungen per Kopie am Arbeitsbaum haben die Waechter rot gezeigt (d: 2 rot, e: 1 rot).

**Suite:** `pytest -n auto` nicht gefahren (Zugschwelle). Gezielt gruen: test_first_run_panel 66, test_relic_picker_geometry 7, test_relic_picker_advisor+save_read+owned_total+geometry+custom_relic+relic_restore 128, test_advisor_bar+test_advisor_apply 74 passed / **1 failed** (Befund 1). Erwartung fuer die volle Suite: 1 failed.

## Befunde

**1 — Vorschlagszustand der Advisor-Zeile passt bei der abgeleiteten Startbreite nicht (AK-05/AK-194, laufendes Fenster).** Windows, Fusion, Segoe UI 9 pt, dpr 1,25: Fenster 1350 px, Zeile 498 px. Mit Apply all/Why/Clear braucht die Zeile 57+183+87+80+80+80+80+6·6 = 683 px: Zielwahl (66 px, `Maximise damage`) und Lesart-Box (67 px, `Worst case`) sind abgeschnitten, Statuszeile 0 px. `test_at_the_opening_width_no_action_button_is_cut` ist deshalb auf HEAD rot und bleibt es (Test nicht abgeschwaecht). Das war schon vor A16 so (596 > 498); der alte Waechter sah es nicht, weil `rendered.clipped` nur Widgets ausserhalb der Zeile fand, nicht abgeschnittene Beschriftungen. Optionen (Director/App Designer/ui-ux-designer): (a) `_width_around_the_effect_table` um den Zeilenbedarf ergaenzen (A14 aendern); (b) Aktionsknoepfe in eine zweite Zeile oder ein Menue (AK-03/§3.1); (c) AK-05 auf den 4.12-Zustand einschraenken (dann Test anpassen). Nicht von mir entschieden.

**2 — Kurzform `Worst`/`Best` (AK-194) nicht gebaut, weil der Hebel gemessen 0 px ist.** Kein bestehender Pfad (T-224 hatte nur gemessen). Am laufenden Fenster: `setItemText` auf `Worst`/`Best` senkt `sizeHint` 87 → 61, aber `minimumSizeHint` bleibt 87 und die Box bleibt 87 px — auch nach `clear()`+`addItem`, `setFont`, Policy-Toggle, `setMinimumWidth`. Nur eine **neu gebaute** Box misst 61 px. Der Rueckfall braeuchte also Box-Austausch samt Signal-Neuverdrahtung und Hysterese (26 px Gewinn in einem 26-px-Band von Fensterbreiten; bei 67 px Statuszeile am Startfenster nie ausgeloest). Das ist nicht "klein" und eine Designfrage → Director: streichen (ui-ux-designer zieht AK-194-Satz nach) oder eigener Auftrag.

**3 — Sichtbare Folge von c:** nach einem Rescan ohne Fund stehen die Slots leer (populate mit Bestand None verwirft das getragene Relikt; Signale geblockt, Build in Settings unveraendert). Folgt aus "kein Bestand ueberlebt" (AK-267, AD-029.3); an QA/App Designer zur Abnahme.

**4 — Task-Praemisse "monkeypatch GOAL_BOX_WIDTH":** `GOAL_BOX_WIDTH` ist ein Maximum (`setMaximumWidth`); 400 statt 200 aendert bei 183 px Bedarf nichts. Rote Phase und Mutation nutzen deshalb `setFixedWidth(400)`.

## An qa-engineer
Rescan ohne Fund bei offenem Picker (Lesen laeuft, Picker oeffnen, Lesen endet leer) → Raster leer; danach Slots leer (Befund 3). AK-05/194 nur ueber den Kindprozess pruefbar (`python -m tests.advisor_row_at_the_window <snapshot.json>` mit `QT_QPA_PLATFORM=windows` und Datenumlenkung). Mutationen d/e nachfahren.

## Ponytail-Review
`git diff 7f3f760..HEAD`: Anwendungscode +26/-10 (firstrun 6, relicpicker 12, app 18), kein neuer Typ ausser einem Signal; Tests netto +140 (neues Messmodul 160 Zeilen ersetzt zwei 1320-px-Tests und zwei Skips). Kurzform bewusst nicht gebaut (yagni, Befund 2). Lean already.

Scratchpad-Messgut (`<scratchpad>/T-225/`: probe_window.py, probe_combo.py, probe_picker.py, mutant/) bleibt liegen; kein Server, kein Port.
