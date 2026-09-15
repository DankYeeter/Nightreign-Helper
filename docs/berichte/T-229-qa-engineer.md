# T-229a — Pruefphase Zyklus 21, qa-engineer (13.09.2026)

**Stand gemessen:** Code `719c46d` (letzter Commit unter `nrplanner/`,
`nrdata/`, `scripts/`: `101022f`, `git log -1 -- nrplanner nrdata scripts`);
Archiv fuer Klon und Mutationen `git archive 8ce5b3b` (HEAD beim Start; beim
Schreiben dieses Berichts `c499c64`, nur Doku-Commits von T-229b/c dazwischen).
Suite in beiden Laeufen **1 failed / 1518 passed / 9 skipped** (Punkt 5).
Umlenkung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-229`, `LOCALAPPDATA` und
`APPDATA` auf `<scratchpad>/T-229/qa/data/{local,roaming}`; Testabzug
kopiert (841 Dateien, 20 812 293 Bytes, nachgezaehlt). Spielstand nur gelesen.

**Praemisse widerlegt:** Der Spielstand hat **314** Kopien, nicht 312
(`inventory.load` -> `relic_count 314`, `len(relics) 314`, 103 Deep;
`NR0000.sl2` geaendert **13.09.2026 19:17:02**, also nach T-222/T-224).
Alle Zahlen unten sind auf 314 gezaehlt.

## Urteil: FAIL

Ein P2 (Befund 1). Mindestens zu beheben vor PASS: Befund 1. Die Retests
(Punkt 1) halten alle bis auf QA-232 (teilweise, Befund 3).

## Punkt 1 — Retest der "behoben -- Retest in der Pruefphase"-Zeilen

| ID | Urteil | Beleg (Verhalten + Test, rot-vorher in eigener Extraktion) |
|---|---|---|
| QA-210 | **behoben** | `NO_SAVE_WAS_READ` in `relicpicker.py:145`, Literal in `tests/test_relic_picker_advisor.py:508`; `NO_FIGURES_AT_ALL` im Code 0 Treffer (`grep -rn` ueber `nrplanner tests`, nur `UI_SPEC.md:1648` als Verlauf) |
| QA-232 | **teilweise** | dds.py:69 zurueck auf `ValueError` -> `test_the_first_run_keeps_a_refusal_of_the_extraction_path` rot (1 failed / 19 passed). Aber 6 Verweigerungen des Extraktionspfads erreichen die Flaeche weiter als Sammelsatz -> Befund 3 |
| QA-242 | **behoben** | Mutation `wanted-height-is-read-afresh` getoetet (`test_the_height_asked_for_is_the_figure_of_the_sizing_and_stays_it`) |
| QA-247 | **behoben** (Kartenhaelfte) | Mutation `cards-keep-the-stock-of-a-save-no-longer-held` getoetet (2 failed / 67 passed); am Fenster: Rescan ohne Fund bei offenem Picker -> 54 Karten -> 0, Slot 1 leer, Zeile `No save file found. Relic slots stay empty ...`. Der offene Picker traegt danach **keine** Kopfzeile (`headline.text() == ""`) -- das ist DR-022 (T-229c), nicht neu gemeldet; der Test prueft nur `relic_cards(dialog) == []`, nicht die Kopfzeile |
| QA-248 | **behoben fuer Desktops >= 1608 px**, sonst Befund 1 | Mutation `opening-width-ignores-the-advisor-row` getoetet; am Fenster (windows, dpr 1,25) oeffnet 1608 px, `cut == []`, Statuszeile 67 px |
| SEC-026 | **behoben** (Verhalten/Test) | `looks_like_the_game` ohne `in_a_steam_library` -> 3 rot in 3 Dateien (`test_a_game_outside_every_steam_library_is_not_a_game`, `test_a_remembered_folder_outside_every_steam_library_falls_through`, `test_a_complete_game_outside_every_steam_library_is_turned_down`), 111 passed |
| SEC-036 / SEC-038 | **behoben** | `_steam_roots` + `C:/Steam` -> `test_the_real_root_list_holds_nothing_the_registry_did_not_name` und `test_a_registry_without_steam_offers_no_root_at_all` rot (2 failed / 7 passed) |
| SEC-037 | **behoben** | ZSTD-Deckel (`dcx.py:59`) abgeschaltet -> `test_a_zstd_member_over_the_ceiling_is_refused` rot (1 failed / 24 passed) |
| SEC-039 | **behoben** | `shortcut.py:144` gibt `stderr` zurueck -> `test_the_start_menu_button_never_quotes_powershell` rot (1 failed / 19 passed) |

Angriffspfad-Seite der SEC-Zeilen: T-229b (gelesen: `security/findings.md`
Z. 72, SEC-043), nicht wiederholt.

## Punkt 2 — Pruefen die Tests die Kriterien?

- **A16, `test_the_worst_case_moves_the_ranking_where_a_conditional_curse_sits`: ja, am echten Spielstand.** Der `planner`-Fixture liest den Spielstand ueber `savefile.save_roots()` (Fallback `Path.home()/AppData/Roaming`, unabhaengig von der `APPDATA`-Umlenkung); der Test lief **PASSED, nicht SKIPPED** (`pytest -v -rs tests/test_advisor_goals.py`: 45 passed). Er misst beide GOAL-Haelften: `orders_differ` (Rangfolge bewegt sich) und je bewegter Kopie `curse_ids & CONDITIONAL_CURSES` (jede bewegte Kopie traegt einen der sieben Flueche), ueber `advisorbar.asking_from` (der Weg des Programms) und `candidates.pool` fuer beide Slotarten -- alle 314 Kopien. Dazu die Zahl `COPIES_THE_WORST_CASE_MOVES = 11` als Literal. Mutation `worst-case-declares-the-buffs` toetet ihn (4 rot). **Grenze:** auf jeder Maschine ohne diesen Spielstand `pytest.skip`; die Abnahme ist nur hier belegt, und das Literal 11 haengt an einer Datei, die sich mit jedem Spielabend aendert (heute 19:17 geaendert, 312 -> 314) -- Befund 6.
- **"jede Zahl sagt, welche gerade gilt" (AK-185):** kein Test zaehlt die Vorkommen je Ort; `test_advisor_block.py` prueft den Kopf des Blocks und den `Why`-Titel mit `"worst case"`, die Picker-Zusammenfassungszeile prueft `test_relic_picker_advisor.py` (nicht rot-vorher geprueft). Beobachtung, kein Befund.
- **A15, gemerkter Pfad durch die Herkunftspruefung: ja.** `tests/test_game_path_memory.py::test_a_remembered_folder_outside_every_steam_library_falls_through` (`resolve_game` -> `looks_like_the_game` -> `in_a_steam_library`), rot ohne Herkunft (siehe SEC-026-Zeile oben).
- **QA-242/QA-248-Waechter messen am echten Fenster** (Kindprozess `QT_QPA_PLATFORM=windows`), nicht offscreen -- das ist die richtige Messgrundlage. **Aber:** beide messen bei `_opening_width()` der Maschine, auf der sie laufen (hier 4096 px Platz); den Deckel `room` misst keiner (Befund 1).

## Punkt 3 — Adversarial

| Fall | Ergebnis |
|---|---|
| Rescan ohne Fund bei offenem Picker | Karten 54 -> 0, Slot leer, Zeile `No save file found. Relic slots stay empty ...`; Kopfzeile des offenen Pickers leer (DR-022). Beraterleiste bleibt in 4.1 mit allen drei Bedienelementen aktiv -> **Befund 2** |
| Lesart umschalten waehrend eines Laufs (AK-183) | Lauf wird abgebrochen, `OUTDATED`, kein Ergebnis unter falscher Lesart (AK-184 haelt); Satz sagt `Your build changed while this was working out` -- der Build hat sich nicht geaendert -> **Befund 5** |
| Fremdordner ohne Steam in der Registry | jeder Ordner abgelehnt (`test_a_registry_without_steam_offers_no_root_at_all`, rot mit fester Wurzel). Verhalten wie entschieden ("Haertung ueber Herkunft"); offene Frage 1 |
| Fensterbreite 1608 px auf 1366-px-Bildschirm | `_opening_width(room=1366)` = 1366; Vorschlagszustand: `cut == ['goal_box', 'reading_box']` (je 69 px), Statuszeile **0 px** -> **Befund 1** |
| dito 1536 px (1080p bei 125 %) | nichts abgeschnitten, Statuszeile **0 px** -> Befund 1 |
| dito 1600 px | Statuszeile 59 px, nichts abgeschnitten |
| Englische Verweigerungen erreichen die Flaeche woertlich | `dds.decode(b"RIFF")` kommt durch `_Builder.run` woertlich (Test, rot-vorher). `dcx.py:79` (`ValueError` "DCX size mismatch") und `dcx.py:74` (`NotImplementedError`) kommen als `Something went wrong that this program has no sentence for (ValueError|NotImplementedError).` -> **Befund 3** |

## Punkt 4 — Mutationen nachgefahren (AD-033 Punkt 5)

Je Name eine eigene Extraktion von `8ce5b3b`, `PYTHONHASHSEED=0`, nur die
Datei des genannten Toeters:

| Mutation | Ergebnis |
|---|---|
| reading-takes-is-debuff-for-curse | getoetet (1 failed / 44) |
| worst-case-declares-the-buffs | getoetet (4 failed / 41) |
| reading-overwrites-the-declaration | getoetet (1 failed / 53) |
| reading-change-starts-a-run | getoetet (1 failed / 53) |
| e1-headline-ignores-the-origin | getoetet (2 failed / 64) |
| wanted-height-is-read-afresh | getoetet (1 failed / 6) |
| cards-keep-the-stock-of-a-save-no-longer-held | getoetet (2 failed / 67) |
| **goal-box-400-px** | **ueberlebt** (`tests/test_advisor_bar.py` 54 passed) |
| reading-box-stays-live-without-a-save | getoetet (1 failed / 53) |
| opening-width-ignores-the-advisor-row | getoetet (1 failed / 20) |

**9 von 10 getoetet.** `goal-box-400-px` ueberlebt seit T-227: die
Startbreite folgt jetzt der Leiste (`_width_around_the_advisor_row`), also
waechst das Fenster mit der 400-px-Box mit und die beiden Waechter (AK-05,
AK-194 "an der abgeleiteten Startbreite") sehen nichts. Die Mutation beisst
nur noch dort, wo der Bildschirm deckelt -- und das misst kein Test
(Befund 1). Kein Befund gegen die Waechter, Beobachtung.

**Geloescht:** alle 10 Eintraege; `MUTATIONS` ist `{}`, Datei sonst
wortgleich (`git diff --stat`: 1 insertion, 144 deletions; 302 -> 159
Zeilen, LF). Literale liegen in `git show 8ce5b3b:scripts/differential/mutate.py`.
`tests/test_differential_track.py` danach 40 passed / 1 skipped (leere
Parametermenge). Erwartete Suite nach dem Commit: 1509 passed / 10 skipped
(10 Ankerfaelle weniger, 1 Skip mehr) -- **nicht gemessen**, beide
Suitelaeufe waren fuer Punkt 5 verbraucht. Kein Commit (Director).

## Punkt 5 — QA-249

- `pytest -n auto` Lauf 1: **1 failed / 1518 passed / 9 skipped, 76,95 s** --
  rot: `tests/test_save_path_memory.py::test_a_window_whose_picked_file_is_gone_says_nothing_about_it`
  (Fehlertext **nicht erfasst**, mein Mitschnitt hielt nur die letzten 40
  Zeilen; seriell danach 36 passed in 9,26 s).
- Lauf 2: **1 failed / 1518 passed / 9 skipped, 76,13 s** -- rot:
  `tests/test_advisor_worker.py::test_cancel_is_visible_at_once_however_long_the_worker_takes`,
  Fehlertext: `AssertionError: the run had scored 3 times when the window was
  told it had stopped and 3 in the end, so the window was told after the
  worker had finished rather than before it noticed` / `assert 3 > 3`
  (`tests/test_advisor_worker.py:260`, gw5).
- `tests/test_save_read_in_the_background.py` unter Last (32 Rechenprozesse
  auf 24 Kernen, 150 s): 6 Laeufe seriell, **6 x 26 passed** (116,8 / 44,8 /
  34,2 / 36,4 / 35,9 / 35,2 s). Die beiden anderen Dateien unter Last mit
  `-n 4`: 4 x 54 passed.
- **QA-249 selbst 0 von 8 reproduziert; die Klasse schon:** ueber vier
  bekannte `-n auto`-Laeufe (T-228, Director, meine zwei) sind **drei
  verschiedene** zeitabhaengige Tests je einmal rot -> Befund 4.

## Punkt 6 — Nachzaehlen AK-188 / AK-169 (auf 314 Kopien)

Rezept A = Umgebung von `scripts/measure_advisor_language.py` (T-092
"Umgebung A": Wylder, Stufe 15, Startwaffe als Bezug und einzige Waffe,
`DEFAULT_WEIGHTING`, `max_damage`, je Kopie allein in einem weissen Slot,
`explain.reasons` -> `curses_without_a_figure` / `effects_without_a_figure`).
Rezept B = derselbe Zaehler, Kontext aus `advisorbar.asking_from(planner,
"min_damage_taken")` (Wylder Stufe 1, **ohne** Bezugswaffe, A17), also der Weg
des Programms. Skript `<scratchpad>/T-229/qa/recount.py`.

| Zahl (Spec) | Spec, 309 Kopien | **Rezept A, 314** | Rezept B, 314 |
|---|---|---|---|
| `curses_without_a_figure` heute (AK-188: 67) | 67 | **67** | 67 |
| dito schlechtester Fall (AK-188: 42) | 42 | **42** | 42 |
| `effects_without_a_figure` heute (AK-169: 426 von 845) | 426 / 845 | **437 / 860** | 438 / 860 |
| dito bester Fall (AK-188: 323) | 323 | **331** | 331 |
| `not_counted` worst + best = heute (AK-187 A31: 177 + 27 = 204 auf 312) | 170 + 27 = 197 | 174 + 27 = 201 | **176 + 27 = 203** |

Bedingte Fluchrollen der sieben: 27 (unveraendert). Nur Zahlen; die Spec
zieht der `ui-ux-designer` nach.

## Befunde

### [P2 | Major | Hoch] Befund 1 — Am Bildschirmdeckel kehrt QA-248 zurueck: Statuszeile 0 px ab < 1600 px Platz, Boxen abgeschnitten bei 1366 px

**Adressat:** developer (Spec-Frage an ui-ux-designer, s. offene Frage 2)
**Betroffen:** `nrplanner/app.py:2446-2471` (`_opening_width`, Term `room`), `nrplanner/advisorbar.py` (Vorschlagszustand)
**Umgebung:** Windows 11, `QT_QPA_PLATFORM=windows`, Fusion, dpr 1,25, Fenster per `WA_DontShowOnScreen`; Skript `<scratchpad>/T-229/qa/row_at_room.py` (Messung wie `tests/advisor_row_at_the_window.py`, Fenster auf `_opening_width(room=N)` gesetzt)

**Reproduktion:**
1. Planner mit Spielstand oeffnen, auf `_opening_width(room=1366)` (= 1366 px) bzw. `room=1536` (1080p bei 125 %) setzen.
2. Vorschlagszustand herstellen (`_show(Situation(SUGGESTED, ...))` mit Apply all / Why / Clear).

**Erwartet:** AK-05 (kein Text ausser der Statuszeile abgeschnitten) und AK-194 (Statuszeile nie 0 px an der Startbreite) an der Breite, mit der das Fenster auf diesem Desktop oeffnet.
**Tatsaechlich:** 1366 px: `cut == ['goal_box', 'reading_box']` (69 px statt 183/87), Statuszeile **0 px**. 1536 px: nichts abgeschnitten, Statuszeile **0 px**. 1600 px: 59 px. 1608 px (hier): 67 px.

**Analyse:** `_opening_width` deckelt bewusst mit `room` ("der Desktop gewinnt", Docstring). T-227 hat die Leiste in die Startbreite gerechnet, aber nur fuer Desktops, die 1608 px logisch hergeben. Ein 1080p-Monitor bei 125 % Skalierung hat 1536 px -- das ist eine haeufige Einstellung, nicht ein exotischer Laptop. Beide Waechter messen `_opening_width()` ohne `room`, also auf der Maschine des Laufs (hier 4096 px) -- deshalb gruen, und deshalb ueberlebt auch `goal-box-400-px`.
**Auswirkung:** Auf solchen Desktops steht nach dem ersten Vorschlag keine Statuszeile (`Maximise damage — 1 of 6 slots filled.` nur im Tooltip); bei 1366 px sind Zielwahl und Lesart-Box unlesbar. Workaround: Splitter nach rechts ziehen.
**Vorschlag:** Entweder die Leiste unter dem Deckel umbrechen/kuerzen (Entscheidung ui-ux-designer: einzeilig war Nutzerentscheid 13.09.) oder der Waechter misst zusaetzlich `room=1366` und `room=1536` mit demselben Kriterium, damit der Fall eine rote Phase hat.

---

### [P3 | Minor | Niedrig] Befund 2 — Nach einem Rescan ohne Fund bleibt die Beraterleiste in 4.1 mit allen drei Bedienelementen aktiv statt in 4.8

**Adressat:** developer
**Betroffen:** `nrplanner/app.py:3991-4002` (`_the_save_has_been_read`), `nrplanner/advisorbar.py:686-694` (`the_data_is_changing` vergisst die Antwort, zeigt aber `_resting()` nicht neu), `:890-894`
**Umgebung:** offscreen, Testabzug, echter Spielstand; Skript `<scratchpad>/T-229/qa/adversarial_c.py`

**Reproduktion:**
1. Planner mit Spielstand; Leiste sagt `Nothing suggested yet.`, drei Bedienelemente aktiv.
2. `save_reader._read` auf `None` stubben, `Rescan save` klicken, warten.

**Erwartet:** wie ein frisches Fenster ohne Spielstand (gemessen: `NO_SAVE`, `No save was read, so there are no relics to choose from — use Rescan save.`, Zielwahl/Lesart/Optimize **deaktiviert**; AK-268).
**Tatsaechlich:** `NOTHING_YET`, `Nothing suggested yet.`, alle drei **aktiv**; erst ein Klick auf `Optimize` fuehrt nach 4.8. Zeile darueber sagt gleichzeitig `No save file found`.

**Analyse:** Der Rescan-Pfad ruft `the_data_is_changing()` (Antwort weg, kein Neuzeichnen) und haendigt den Bestand an die Karten (AK-267), aber nichts ruft `the_build_changed()`/`_show(_resting())` fuer die Leiste. Der Startpfad kommt ueber einen anderen Weg nach 4.8 (`test_the_two_shut_controls_come_free_on_different_conditions` prueft nur den Start).
**Auswirkung:** Zwei Zeilen widersprechen sich (kein Spielstand / Optimize anklickbar); kein Datenfehler, ein Klick klaert es.
**Vorschlag:** Am Ende von `_the_save_has_been_read` die Leiste neu ruhen lassen (derselbe Weg wie AK-267 fuer die Karten); den Test um den Rescan-Uebergang erweitern.

---

### [P3 | Major | Niedrig] Befund 3 — QA-232 nur teilweise: sechs Verweigerungen des Extraktionspfades erreichen die Flaeche weiter als Sammelsatz

**Adressat:** developer (Status QA-232 -> teilweise, kein neuer Befund)
**Betroffen:** `nrdata/dcx.py:74` (`NotImplementedError`, Kompressionsart), `nrdata/dcx.py:79` (`ValueError`, "DCX size mismatch"), `nrdata/dds.py:97`, `:99`, `:103` (`NotImplementedError`: unkomprimiert / FourCC / DXGI), `nrdata/bnd4.py:192` (`NotImplementedError`, Inline-Kompression)
**Umgebung:** `errortext.in_english` auf den geworfenen Ausnahmen

**Reproduktion:** DFLT-Container, dessen Kopf 200 Bytes behauptet und dessen Nutzlast 100 ergibt (`tests.test_hostile_gamedata.dcx_container`), durch `dcx.decompress` -> `ValueError` -> `in_english`: `Something went wrong that this program has no sentence for (ValueError).`; Methode `LZ4\0` -> `... (NotImplementedError).`
**Erwartet (QA-232):** die Verweigerung sagt, *was* schiefging (A7), wie die 21 umgestellten Stellen.
**Tatsaechlich:** Sammelsatz. Register QA-232 zaehlt "dcx 2 ... in T-219"; `670d879` hat in `dcx.py` nur die Magic-Zeile umgestellt.
**Zweite Masken (ganzer Baum `nrdata/*.py`):** `raise (ValueError|NotImplementedError|RuntimeError|KeyError|TypeError|struct\.error)\(` = 10 Treffer; `^\s*raise\s+[A-Za-z_.]+\(` ohne `NotWhatItClaims|OSError|FileNotFoundError|CannotBuild` = 14 Treffer. Davon Dateiaussagen: die 6 oben. Rest: `bossdata.py:67/70`, `icons.py:133` (`KeyError`, Programmnachschlagen), `savefile.py:358` (Programmfehler, laut T-218 bewusst), `LayoutError`/`OodleUnavailable` (eigene Klassen, werden zitiert).
**Auswirkung:** Nur bei beschaedigten oder fremden Spieldateien in einer Steam-Bibliothek; Text englisch (A8 haelt), aber ohne Grund (A7).
**Vorschlag:** die 6 Stellen auf `NotWhatItClaims` mit Satz ohne Dateibytes (SEC-043-Regel); QA-232-Zeile auf teilweise.

---

### [P3 | Minor | Hoch] Befund 4 — Suite unter `-n auto` nicht deterministisch: drei verschiedene zeitabhaengige Tests je einmal rot (QA-249 ist ein Fall von dreien)

**Adressat:** developer (Vorschlag: QA-249 erweitern statt neue ID)
**Betroffen:** `tests/test_save_read_in_the_background.py:194` (QA-249, T-228), `tests/test_save_path_memory.py::test_a_window_whose_picked_file_is_gone_says_nothing_about_it` (Lauf 1), `tests/test_advisor_worker.py:260` (Lauf 2)
**Umgebung:** `pytest -n auto`, 24 Kerne, 2 Laeufe je ~77 s

**Reproduktion:** zwei volle Laeufe (Punkt 5): jeder 1 failed, jedes Mal ein anderer Test; seriell und unter kuenstlicher Last alle gruen (0 von 8 bzw. 0 von 4).
**Erwartet:** 1519 passed / 9 skipped, reproduzierbar (Abnahmezahl des Directors).
**Tatsaechlich:** die Abnahmezahl ist in 2 von 2 eigenen Laeufen nicht erreicht; der Fehlertext von `test_advisor_worker` zeigt, dass der Worker unter Last seine drei Bewertungen vor dem `stopped`-Signal fertig hatte (`assert 3 > 3`) -- das Kriterium "der Worker arbeitete noch" haengt an der Prozessorzeit, die xdist ihm laesst.
**Auswirkung:** Kein Nutzerschaden; aber jede Abnahme "1519/9" ist ein Wuerfelwurf, und ein echter Regressionsfehler in einem der drei Tests faellt als "sporadisch" durch.
**Vorschlag:** die drei Tests auf Zustaende statt Zeitspannen umbauen (`Watched.delay` so waehlen, dass der Worker beim Abbruch nachweislich noch laeuft, z. B. per Ereignis statt Zeit) oder sie unter xdist in eine eigene Gruppe (`--dist loadgroup`) legen.

---

### [P4 | Trivial | Mittel] Befund 5 — Lesart-Wechsel waehrend eines Laufs sagt `Your build changed ...`

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/advisorbar.py:661-684` (`the_build_changed`, 4.7-Satz), AK-183
**Reproduktion:** `Optimize`, waehrend `WORKING_QUIETLY` `Best case` waehlen.
**Erwartet:** ein Satz, der die Ursache nennt (Lesart oder Ziel geaendert).
**Tatsaechlich:** `Your build changed while this was working out — use Optimize again.` Verhalten sonst korrekt (Abbruch, kein Ergebnis unter falscher Lesart). Gilt ebenso fuer den Zielwechsel waehrend eines Laufs (vor A16).

---

### [P3 | Minor | Hoch] Befund 6 — Die A16-Abnahme haengt an einer Datei, die sich mit jedem Spielabend aendert, und laeuft nur auf dieser Maschine

**Adressat:** developer; Praemisse an director
**Betroffen:** `tests/test_advisor_goals.py:1116` (`COPIES_THE_WORST_CASE_MOVES = 11`), `:1193`; `tests/conftest.py:334` (`planner` liest den echten Spielstand); `UI_SPEC.md` AK-187 A31 (312/177/204)
**Reproduktion:** `NR0000.sl2` geaendert 13.09.2026 19:17:02; `inventory.load` zaehlt 314 (Praemisse 312, T-222/T-224 frueher am Tag). Test heute noch gruen (11 bewegte Kopien), `not_counted` schon verschoben (203 statt 204).
**Erwartet:** die Abnahmezahl A16 ist reproduzierbar, unabhaengig davon, ob der Nutzer gestern gespielt hat.
**Tatsaechlich:** das Literal 11 wird beim naechsten Relikt mit einem der sieben Flueche rot, ohne dass der Code sich geaendert hat; auf jeder anderen Maschine `pytest.skip` -- die Abnahme ist dort nie belegt.
**Vorschlag:** einen eingefrorenen Inventar-Fixture (Handles, Effekt-/Fluch-IDs der 314 Kopien, keine Spielstanddatei) neben den Live-Lauf legen: das Literal gegen den Fixture, der Live-Lauf nur noch mit den beiden qualitativen Zusicherungen (Rangfolge bewegt sich, jede bewegte Kopie traegt einen Fluch).

## Beobachtungen (ohne Nummer)

- Der Testabzug hat exakt die Zahlen aus `CLAUDE.md` (841 / 20 812 293), Kopie funktioniert; Fensterlaeufe 5-9 s statt 110 s.
- `tests/advisor_row_at_the_window.py` liess sich fuer die `room`-Messung wiederverwenden; mit einem `room`-Parameter waere Befund 1 ein Dreizeiler im Waechter.

## Offene Fragen

1. **director:** Ohne Steam-Schluessel in der Registry (HKCU und HKLM WOW6432Node fehlen -- Steam unter anderem Windows-Konto installiert, portable Steam) wird jeder Ordner abgelehnt und A15 "fuehrt jeden Nutzer bis zu lesbaren Daten" ist per Bau nicht erreichbar. Entschieden ("Haertung ueber Herkunft") oder Restfall fuer E1-Text?
2. **ui-ux-designer:** Gilt AK-05/AK-194 an der Breite, die der Desktop *hergibt*, oder nur an `max(Tabelle, Leiste)` ohne Deckel? Der Code deckelt ausdruecklich; die Spec nennt "abgeleitete Startbreite" ohne den Fall.
3. **director:** Praemisse 312 Kopien ist ueberholt (314). Welche Zahl gilt fuer AK-187/AK-169-Nachtraege -- die von heute, oder wird der Spielstand fuer Zahlen eingefroren (Befund 6)?

## Nicht getestet

- Angriffspfade der SEC-Zeilen (T-229b, PASS, gelesen).
- Bildnachweise der Beraterleiste und Picker-Hoehen (T-229c, DR-022 bis DR-024).
- Suite nach dem Leeren der Registry (Limit zwei volle Laeufe, beide fuer QA-249).
- QA-232-Restfaelle am laufenden Erststart-Dialog (nur `in_english` auf der Ausnahme).

## QA-Log (Fortschreibung `qa/findings.md`, nur neue/geaenderte Zeilen; IDs vergibt der Director)

| ID | Titel | Prio | Adressat | Status | Datum |
|---|---|---|---|---|---|
| QA-210 | Statuswechsel T-229a: Retest bestanden | P3 | developer | behoben | 2026-09-13 |
| QA-232 | Statuswechsel T-229a: 6 Restfaelle (dcx 74/79, dds 97/99/103, bnd4 192) | P3 | developer | teilweise | 2026-09-13 |
| QA-242 | Statuswechsel T-229a: Mutation getoetet, Retest bestanden | P2 | developer | behoben | 2026-09-13 |
| QA-247 | Statuswechsel T-229a: Kartenhaelfte bestanden; Kopfzeile des offenen Pickers -> DR-022 | P3 | developer | behoben (Rest DR-022) | 2026-09-13 |
| QA-248 | Statuswechsel T-229a: bestanden fuer >= 1608 px; am Bildschirmdeckel offen -> neu (Befund 1) | P2 | developer | behoben (Folgebefund) | 2026-09-13 |
| QA-249 | Statuswechsel T-229a: 0/8 reproduziert; Klasse ja (3 Tests, je 1x rot unter -n auto) -> Befund 4 | P3 | developer | offen (erweitert) | 2026-09-13 |
| neu | Befund 1 -- Am Bildschirmdeckel kehrt QA-248 zurueck (Statuszeile 0 px < 1600 px, Boxen abgeschnitten bei 1366 px) | P2 | developer | offen | 2026-09-13 |
| neu | Befund 2 -- Beraterleiste bleibt nach Rescan ohne Fund in 4.1 statt 4.8 | P3 | developer | offen | 2026-09-13 |
| neu | Befund 4 -- Suite unter -n auto nicht deterministisch (3 Tests) -- oder als QA-249-Erweiterung | P3 | developer | offen | 2026-09-13 |
| neu | Befund 5 -- Lesart-Wechsel im Lauf sagt "Your build changed" | P4 | ui-ux-designer | offen | 2026-09-13 |
| neu | Befund 6 -- A16-Abnahme haengt am lebenden Spielstand (312 -> 314), nur auf dieser Maschine | P3 | developer | offen | 2026-09-13 |
