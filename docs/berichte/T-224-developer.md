STATUS: teilweise
AUFTRAG: T-224 — A16 bauen: Worst case / Best case im Berater nach AD-035
GELESEN: docs/tasks/T-224.md (vollstaendig); CLAUDE.md (vollstaendig); ARCHITECTURE.md Z. 5693-5850 (Themenbereich H, AD-035 ganz); UI_SPEC.md Z. 3114-3200 (AK-182 bis AK-188), Z. 1006-1013 (AK-05), Z. 3269-3281 (AK-194); GOAL.md Z. 240-295 (A16); nrplanner/advisorbar.py, advisorblock.py, relicpicker.py (Zusammenfassung, SlotAdvice), model.py (configure, is_conditional, compute, NO_SWITCH), app.py (Planner-Zustand, _wire_the_advisor, show_the_suggestion, open_why); tests/test_advisor_goals.py, test_advisor_bar.py, test_advisor_block.py, test_advisor_evaluate.py, test_the_fixture_asks_what_the_program_asks.py, advisor_cases.py, conftest.py; scripts/differential/mutate.py
GEÄNDERT: nrplanner/model.py, nrplanner/advisorbar.py, nrplanner/app.py, nrplanner/advisorblock.py, nrplanner/relicpicker.py; tests/test_advisor_goals.py, tests/test_advisor_bar.py; ausserhalb der Liste (Befund 1): tests/test_advisor_block.py, tests/test_relic_picker_advisor.py, tests/test_advisor_evaluate.py; scripts/differential/mutate.py (vier Mutationen); dieser Bericht. Commits b237663, 0656344, 1483d78 auf worktree-agent-accb5328a80ed2f37 (enthaelt e593a44 und 8247792), kein Push.
ANNAHMEN: (1) Der GOAL-Test vergleicht den schlechtesten Fall mit der Leiste **vor A16** (nur Handeingabe), nicht mit dem besten Fall — siehe Befund 2. (2) Lesart in Saetzen kleingeschrieben (`worst case`), in der Box kapitalisiert (`Worst case`); eine Quelle `advisorbar.reading_label`. (3) Bei 4.8 (kein Spielstand) ist die Lesart-Box wie Zielwahl und `Optimize` deaktiviert.
NÄCHSTER: director (Befund 3 entscheiden lassen: App Designer / ui-ux-designer), danach qa-engineer
BLOCKIERT DURCH: Befund 3 — AK-05-Waechter offscreen rot, solange die Leiste eine zweite Box traegt; AK-194 am laufenden Fenster unterschritten (37 px < 105 px), auch mit `Worst`/`Best`

## Die vier benannten Tests (plus einer fuer AK-182/183)

| Test | Rot vorher | Gruen nachher |
|---|---|---|
| `test_reading_defaults_name_the_seven_conditional_curses_and_nothing_else` | AttributeError `reading_defaults` | ja |
| `test_the_readings_share_not_counted_and_invent_nothing` | `(204 + 204) == 204` | ja |
| `test_the_worst_case_moves_the_ranking_where_a_conditional_curse_sits` | AttributeError `Planner.worst_case` | ja |
| `test_a_declared_condition_outlives_both_readings` | AttributeError `reading_defaults` | ja |
| `test_the_reading_is_a_second_box_that_puts_the_answer_away_and_asks_nothing` | AttributeError `reading_box` | ja |

Befehl: `pytest tests/test_advisor_goals.py tests/test_advisor_bar.py -k "reading or readings or worst_case or declared_condition"` — 5 failed vor dem Bau, 5 passed danach.

## Gezaehlte Literale

- Fluch-Ids und Buffzahl am Testabzug (`EXTRACT_VERSION` 11), Skript `count_ids.py` im Scratchpad ueber `model.configure` + `is_conditional(eff, None)`: 2 076 Effekte, 24 `is_curse`, 421 bedingt; **7 bedingte Flueche** `6850700, 6850800, 6850900, 6851200, 6851300, 6851400, 6851700`; bedingte Nicht-Flueche 414, davon `NO_SWITCH` 7037800 → **413** im besten Fall. Deckt sich mit AD-035.
- Am Spielstand (312 Kopien, Literal auf 0 gesetzt und Fehlermeldung gelesen, Kopie zurueckgespielt): `not_counted` **worst 177 + best 27 = today 204** (AK-187; bei 309 Kopien 170 + 27 = 197). **11 Kopien** bewegen ihre `min_damage_taken`-Zahl im schlechtesten Fall (GOAL.md: 11 von 309; jetzt 11 von 312), alle mit einer der sieben Fluch-Ids; die Reihenfolge unterscheidet sich.

## Mutationen (Registry war leer; gefahren gegen `git archive` von b237663)

| Name | Ergebnis |
|---|---|
| `reading-takes-is-debuff-for-curse` | getoetet (1 rot: Sieben-Ids-Test) |
| `worst-case-declares-the-buffs` | getoetet (3 rot: Sieben-Ids, AK-187, GOAL) |
| `reading-overwrites-the-declaration` | getoetet (1 rot: AK-186) |
| `reading-change-starts-a-run` | getoetet (1 rot: AK-182/183-Test) |

`tests/test_differential_track.py`: 44 passed (Anker stimmen).

## Suite

`pytest -n auto` mit Datenumlenkung (`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-224`, `LOCALAPPDATA`/`APPDATA` ins Scratchpad, Testabzug kopiert): **1 failed, 1509 passed, 9 skipped** in 66 s. Der eine Fehlschlag ist Befund 3. Baseline aus dem Auftrag: 1501 passed / 10 skipped.

## Befunde

**1 — Dateiliste von AD-035 reicht nicht (Testseite).** `tests/test_advisor_block.py` haelt die Literale des `Why`-Titels und des Blockkopfs (`"Why this build — Maximise damage"`, `"SUGGESTED — MAXIMISE DAMAGE"`) sowie den `WhyHeading`-Konstruktor; AK-185 ist dort abzunehmen, also mussten die Literale um `, worst case` wachsen und `reading=` in den Helfer. `tests/test_relic_picker_advisor.py`: eine Zeile in `test_line_three_names_the_size_the_figures_are_measured_against` prueft jetzt die Lesart in der Picker-Zusammenfassung (sonst haette der vierte Ort keinen Waechter). `tests/test_advisor_evaluate.py` (Checkpoint 13): vergleicht Berater- gegen Statblattrechnung; seit A16 traegt das Berater-`declared` die Vorbelegung, das Statblatt laut A16 nicht — der Vergleich setzt jetzt `planner.declared` zurueck (wie `ranking_with(as_the_bar_asked_before_a16)`), `THE_STAT_SHEET_KEEPS` bleibt bei drei Feldern.

**2 — AD-035 nennt fuer den GOAL-Test die falsche Gegenseite.** AD-035 sagt "declared einmal aus reading_defaults(True), einmal aus reading_defaults(False)" **und** "jede Kopie, deren Zahl sich bewegt, traegt eine der sieben Fluch-Ids". Beides zusammen kann nicht gelten: zwischen Worst und Best bewegen sich auch die 260 bedingten Buffrollen. GOAL.md misst "11 Kopien im schlechtesten Fall" gegen **heute** (keine Vorbelegung). Gebaut ist der GOAL-Wortlaut: Worst gegen die Leiste vor A16 (`as_the_bar_asked_before_a16`, nur `planner.declared`). Architect moege AD-035 nachziehen.

**3 — AK-05/AK-194 gegen AK-182: die zweite Box laesst der Statuszeile bei 1320 px keinen Platz (Eskalation).** Gemessen mit einem Probe-Test (geloescht) an `planner.resize(1320, 900)`, Spalte 468 px:
- offscreen (die Umgebung der Suite; 12 px je Zeichen, T-084 §0): heute Statuszeile 54 px; mit `Worst case`-Box **0 px** (Boxen 124/124, `Optimize` 110, Kopf 86); mit `Worst`/`Best` ebenfalls 0 px. Der Waechter `test_at_the_opening_width_only_the_status_is_shortened` (AK-05, `endswith("…")`) ist deshalb **rot** und kann mit keiner lesbaren zweiten Box gruen werden.
- Windows-Plattform (laufendes Fenster, Fusion, devicePixelRatio 1,25, 9 pt): heute **130 px** (AK-194 nennt 158), mit Box **37 px** (Ziel-Box 183, Lesart-Box 87, `Optimize` 80, Kopf 57); `Worst`/`Best`-Kurzform aendert die Boxbreite offscreen wie am Fenster nicht messbar (87 px bleibt) — AK-194s Ausweichwortlaut erreicht 105 px nicht.
Optionen fuer director/App Designer: (a) AK-05-Waechter am laufenden Fenster messen statt offscreen (Test-Aenderung; die Spec selbst sagt in AK-194, offscreen-Breiten seien keine Messung) und den AK-194-Schwellenwert neu setzen; (b) `GOAL_BOX_WIDTH` senken (widerspricht AK-257); (c) Lesart aus der Leiste in einen anderen Ort verlegen (widerspricht AK-182). Ich habe nichts davon getan; der Test bleibt rot, die Box wie AK-182 verlangt.

**4 — Kein Waechter fuer 4.8 an der neuen Box**: `test_without_a_save_the_row_says_so_and_disables_its_own_two_controls` prueft zwei Elemente; die Lesart-Box wird mit deaktiviert, ohne Test (bewusst nicht ergaenzt: Spec nennt dort zwei Elemente — ui-ux-designer moege sagen, ob die dritte dazu gehoert).

## An qa-engineer

Umschalten waehrend eines Laufs → 4.7 (Pfad `the_build_changed`, nicht eigens getestet); `Why`-Kopf-Satz und Blockkopf mit `, worst case` / `, best case`; keine Lesart auf Effekt-, Fluch-, Zaehlzeilen oder Karten (AK-185 zaehlen); zwei Anfragen, die nur in der Lesart differieren, haben verschiedene Schluessel (AK-184 — folgt aus `declared` im Schluessel, `run.py:271`, nicht eigens getestet).

## Ponytail-Review

`git diff 8247792..HEAD` durchgesehen: `READING_ORDER`-Konstante gestrichen (inline). Anwendungscode net **+96 Zeilen** (5 Dateien, +119/-23), kein neuer Typ, kein Feld auf Request/Result, nichts persistiert. Lean already.

## Aufgeraeumt

Probe-Test `tests/_probe_t224.py` geloescht, Mutanten und `head.tar` im Scratchpad geloescht, `tests/test_advisor_goals.py.orig` nach der Literal-Messung zurueckgespielt und entfernt; kein Server, kein Port. `git status` sauber bis auf diesen Bericht.
