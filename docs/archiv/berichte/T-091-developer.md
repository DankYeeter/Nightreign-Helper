# T-091 - S10b, Teil 2: anwenden, rueckgaengig machen, festhalten (developer)

```
STATUS: erledigt
AUFTRAG: T-091 - S10b, Teil 2: anwenden, rueckgaengig machen, festhalten
GELESEN: docs/tasks/T-091.md (vollstaendig, mit dem woertlichen GOAL.md-
  Kriterium A3 und dem woertlichen Stand-Auszug aus docs/state.md - beide
  Zitate tragen den Auftrag, GOAL.md und docs/state.md wurden daher nicht
  eigens nachgelesen); UI_SPEC.md §3.1, §3.2, §3.4, §3.5, §4 (Tabelle),
  §5, AK-03 bis AK-22, AK-29/AK-30, AK-53 bis AK-62, den T-024-Abschnitt
  §4.1 bis §5.4, den T-078-Abschnitt §3 bis §6 (4.9a/4.9b, AK-141 bis
  AK-147), den T-084-Abschnitt zu 4.7 (AK-173/AK-174);
  ARCHITECTURE.md AD-014 bis AD-017; qa/findings.md QA-188/QA-189;
  nrplanner/advisorbar.py, advisorblock.py, app.py, chalices.py,
  inventory.py, advisor/types.py, advisor/run.py (nur gelesen);
  tests/test_advisor_bar.py, test_advisor_block.py, tests/conftest.py,
  tests/rendered.py; .claude/agent-memory/developer/ (Index und vier
  Eintraege)
GEAENDERT: nrplanner/advisorbar.py, nrplanner/advisorblock.py,
  nrplanner/app.py, tests/test_advisor_bar.py, tests/test_advisor_block.py,
  tests/test_advisor_apply.py (neu), tests/test_advisor_hold.py (neu),
  docs/berichte/T-091-developer.md (diese Datei). Drei Commits auf
  docs/audit-and-advisor-design, kein push.
ANNAHMEN: vier, unten unter "Annahmen" einzeln begruendet - der Undo-
  Zeitpunkt bei mehreren `Use`, `Apply all` bei 4.10, `Use` auf einem
  gehaltenen Slot, und die Folge der 4.9-Teilung fuer
  `effects_without_a_figure`
NAECHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

---

## 1. Was gebaut wurde, und warum so

### 1.1 Anwenden (Commit 51dd6b2)

**Die drei Aktionsknoepfe der Leiste** (`nrplanner/advisorbar.py`):
`Apply all`/`Undo apply`, `Why`, `Clear`, rechts, in der Reihenfolge aus
§3.1. `Apply all` und `Undo apply` sind **ein** Knopf, weil sie eine
Handlung von zwei Seiten sind und die Tabelle dafuer genau einen Zustand
fuehrt (4.13). Zwei Knoepfe muessten sich darueber einigen, welcher gerade
lebt, und waeren im angewendeten Zustand vier sichtbare Aktionsknoepfe -
genau der Fall, gegen den AK-07 geschrieben ist (Gegenbau 4 unten).

Der `Why`-Knopf ist die fehlende Haelfte aus T-089: `why_requested` hatte
keinen Sender, `Planner.open_why` war verbunden. Es war eine Zeile.

**`Use`** (`nrplanner/advisorblock.py`): ein `QPushButton` rechts in der
Kopfzeile des Blocks, wie §3.2 ihn zeichnet. Der Block wendet nichts an -
er haelt keine Relikte - sondern sagt `use_requested`; das Fenster tut es.

**Der Weg ist der vorhandene** (`nrplanner/app.py`,
`Planner._apply_the_answer_to` / `_put_these_keys_in_the_slots`): Anwenden
schreibt die gewuenschten Schluessel in die Liste, die die Slots gerade
halten (`slot.saved_key()`), und uebergibt die ganze Liste an
`_restore_slot_keys` - denselben vier Schritten, auf die `_apply_stored_build`
endet (Restore, `_settle_slots`, `recompute`, `_store_chalice`). Damit
gelten Persistenz je Kelch, Neuberechnung und Build-Liste unveraendert
weiter (AK-14). Kein zweiter Weg, ein Relikt in einen Slot zu bekommen.

Genau das macht **`Undo apply`** zu einer Liste derselben Art und nicht zu
einem zweiten Mechanismus: ein leerer Slot ist der leere Schluessel, ein
Custom relic einer, der seine Effekte selbst traegt (AK-15). Ein Handle,
das der Save nicht kennt, wird uebergangen statt geraten (AK-16) - das
Fenster ist die letzte Stelle, an der ein Vorschlag sonst zu einem Relikt
im Slot wuerde.

**`while_the_player_applies_it`**: Anwenden aendert den Build, und jede
Aenderung des Builds endet in `recompute`, das der Leiste sagt, die Antwort
sei ueberholt (AK-12). Ohne diese eine Ausnahme haette das Anwenden seine
eigene Antwort zwischen dem ersten und dem zweiten Slot weggeworfen und
`Undo apply` haette nichts mehr zurueckzunehmen gehabt. Als Kontextmanager
und nicht als Flag: eine Ausnahme mitten im Anwenden liesse die Leiste
sonst dauerhaft taub fuer Buildaenderungen.

**QA-188**, beide Wortlaute:
- **4.7** lautet jetzt `Your build changed while this was working out — use
  Optimize again.` (AK-173).
- **4.9** zerfaellt in die zwei Klauseln 4.9a und 4.9b (AK-142/AK-143), je
  mit Singular/Plural, jede nur wenn ihre Menge nicht leer ist, in der
  Reihenfolge der Tabelle. `Situation.silent_effects` ist ersetzt durch
  `curses_without_a_number` und `effects_left_out`; `_on_ready` liest sie
  aus `result.curses_without_a_figure` und `result.not_counted`.

### 1.2 Festhalten (Commit e1cad99)

**Der Knopf** (`RelicSlot`): ein checkbarer `QToolButton` mit Text in der
Kopfzeile der Karte, **links neben `self.chip`** (§4.1, AK-54), `Hold` in
`MUTED` ohne Rahmen, `Held` in `ACCENT` mit 1 px `ACCENT`-Rahmen, Tooltip
woertlich. Wort statt Schloss, aus dem Grund, den §4.1 nennt: ein Schloss
hiesse "du kannst das nicht aendern", und ein Halt bindet den Berater,
nicht den Spieler.

**Der Zustand lebt am `Planner`**, `dict[(hero_id, vessel_id, deep),
dict[slot_index, handle | None]]`, und **erreicht `QSettings` nirgends**
(OF-15, AD-017.4). Neben dem Slotindex steht das **Handle, auf dem der Halt
gemacht wurde** - ohne das lassen sich spaeter "gehalten und leer" (AK-55)
und "gehalten auf ein Relikt, das es nicht mehr gibt" (AK-56) nicht
auseinanderhalten, denn beide sehen hinterher wie ein leerer gehaltener
Slot aus. Ein Custom relic und ein leerer Slot tragen beide `None` und
loesen deshalb nie eine Freigabe aus - richtig, denn ein Custom relic kann
nicht eingeschmolzen werden und ein leerer Slot hat nichts zu verlieren.

**Gezeichnet wird in `recompute()`** und nur dort. Das ist der eine
Trichter, in dem jede Aenderung endet, die entscheidet, welche Haltezustaende
gelten (Nightfarer, Gefaess, Deep) oder worauf ein Halt gemacht ist
(Relikt). Der erste Entwurf rief `_show_the_holds()` an drei Stellen
(`apply_chalice`, `_relic_changed`, `reload_chalices`) - das war falsch,
siehe 1.3.

**In die Anfrage** (`advisorbar.asking_from`): `problem.held` war bisher
immer leer und der Docstring sagte "Every slot is free". Jetzt traegt die
Anfrage `HeldSlot` je gehaltenem Slot, mit `relic=None` fuer "gehalten und
bleibt leer" (AD-014.7). Fluche reisen neben den Effekten, weil die
Bewertung beide durch denselben `model.compute`-Aufruf schickt (AD-015).

**Beim Anwenden**: kein Anwenden fasst einen gehaltenen Slot an (AK-57,
§5.4), und `Undo apply` gibt einem seit dem Anwenden gehaltenen Slot
nichts zurueck, weil nichts vom Berater darin liegt.

### 1.3 Eine Falle, die im Bau aufgefallen ist

`_show_the_holds()` **darf nicht mitten in einem Restore laufen**. In
`reload_chalices` steht zwischen `apply_chalice()` und `_restore_slot_keys`
eine Schleife, die **jeden** Slot leert. Ein dort geschriebener
`HOLD_RELEASED`-Satz wird eine Zeile spaeter ueberschrieben - und weil der
Halt beim ersten Durchgang schon aus `_holds` entfernt ist, wird er beim
zweiten nicht noch einmal gemeldet. Der Halt fiele **stillschweigend** weg,
und genau das verbietet §4.3 ("Stillschweigen waere hier der Fall, der
einen falschen Vorschlag erzeugt").

Deshalb: `if self._restoring: return` am Kopf von `_show_the_holds`, und
der einzige Aufrufer ist `recompute()`, das jede restaurierende Bahn mit
gesenktem Wachtposten erreicht. Der Fall
`test_a_hold_whose_relic_left_the_save_falls_away_and_says_so` haette den
Fehler gefunden - er ist rot geworden, bevor die Schranke da war.

---

## 2. Annahmen (vier, keine davon steht in `UI_SPEC`)

1. **Der Undo-Zeitpunkt bei mehreren Anwendungen.** `UI_SPEC` sagt nicht,
   worauf `Undo apply` zurueckstellt, wenn der Spieler `Use` dreimal
   gedrueckt hat. Gebaut: **eine** Aufzeichnung je lebender Antwort,
   genommen beim **ersten** Anwenden, und `Undo apply` stellt darauf
   zurueck. Begruendung: 4.13 sagt `Undo puts your slots back as they were`
   - "as they were" kann bei genau einem Knopf nur einen Zeitpunkt meinen,
   und die Leiste fuehrt fuer beliebig viele `Use` genau einen Zustand.
   Gemessen in `test_undo_after_two_uses_takes_both_of_them_back`.
   **Wenn der `ui-ux-designer` das anders will**, ist es eine Zeile.
2. **`Apply all` bei 4.10.** §3.1 nennt drei Faelle der Knopfgruppe: kein
   Vorschlag - keiner; Vorschlag lebt - drei; angewendet - drei. 4.10 hat
   eine **Antwort**, aber keinen **Vorschlag**. Gebaut: bei 4.10 stehen
   `Why` und `Clear`, `Apply all` nicht - er haette nichts zu tun, und ein
   gezeichneter Knopf ohne Wirkung ist das, was `advisorblock.py` seit
   T-089 ausdruecklich ablehnt. 4.10 sagt in der Tabelle selbst, dass `Why`
   erreichbar bleibt.
3. **`Use` auf einem gehaltenen Slot.** Gebaut: der `Use`-Knopf wird auf
   einer gehaltenen Karte **nicht gezeichnet** (der Block bleibt, nur der
   Knopf geht). Begruendung: §5.4 sagt, kein Anwenden fasst einen
   gehaltenen Slot an, und ein Knopf, dessen einzige Aufgabe das Aendern
   dieses Slots ist, waere dort ohne Wirkung. **Gegenargument, das ich
   sehe:** der Tooltip sagt "You can still change it yourself", und man
   koennte `Use` als eine solche eigene Aenderung lesen. Ich halte das fuer
   die schwaechere Lesart - der Satz meint den Picker -, melde es aber, weil
   es eine Oberflaechenentscheidung ist.
4. **Was die 4.9-Teilung fuer `effects_without_a_figure` bedeutet.** Die
   alte einteilige Fassung zaehlte `effects_without_a_figure` **plus**
   `not_counted`. Die neue Tabelle schreibt genau zwei Klauseln, und keine
   davon ist ueber `effects_without_a_figure` (4.9a sind Fluche ohne Zahl,
   4.9b ist Weggelassenes). Folge: eine Antwort, die **nur** stumme
   Nicht-Fluch-Effekte traegt, ist jetzt 4.6 und nicht mehr 4.9. Das steht
   so nicht in QA-188 und ist die Haelfte des Befundes, die ein
   Wortlautvergleich nicht zeigt. Festgehalten in
   `test_an_effect_with_no_figure_is_not_a_clause_of_the_status_line`.
   **Bitte durch `ui-ux-designer` bestaetigen.**

---

## 3. Die zehn Rundreisen des Haltezustands

`tests/test_advisor_hold.py::test_the_hold_survives_ten_round_trips_over_the_vessels`

**Aufbau.** Die ersten drei waehlbaren Gefaesse des aktuellen Nightfarers
aus der Kelchliste, beide Deep-Zustaende: **sechs** Builds. In jedem wird
ein Slot gehalten - Slot 0 bei Deep aus, **Slot 4 bei Deep an**, absichtlich
verschieden, weil `deep` Teil des Schluessels ist und ein Halt, der ueber
den Schalter mitgereist waere, auf einem Slot laege, den der Spieler nicht
sieht. Gewechselt wird ueber die beiden Bedienelemente
(`deep_check.setChecked`, `chalice_list.setCurrentRow`), nicht ueber die
Felder.

**Durchlauf.** Zehn Runden ueber alle sechs Builds = **60 Landungen**. Nach
jeder Landung werden zwei Dinge geprueft: `planner.held_slot_indices()` -
was das Fenster haelt - und die **Kopfzeilen der Karten**, also welche
Knoepfe `Held` zeigen. AK-60 verlangt beides ("die Slot-Kopfzeilen zeigen
ihn unmittelbar danach richtig an"), und die zweite Haelfte ist die, die
ein Zeichnen zum falschen Zeitpunkt findet.

**Ergebnis: 60 von 60 gruen.** Kein Halt ging verloren, keiner reiste in
einen fremden Build mit, keine Kopfzeile war nach dem Wechsel im falschen
Zustand.

Zwei weitere Faelle sichern die Kanten desselben Zustands:
`test_a_hold_whose_relic_left_the_save_falls_away_and_says_so` (Save wird
ohne **jede** Kopie dieser Rolle neu gelesen - jede, weil ein Build auch
die Rolle nennt und sonst mit der Kopie nebenan geantwortet wuerde) und
`test_a_hold_whose_relic_is_still_owned_survives_a_re_read` als Spiegel:
sonst waere "beim Neu-Lesen jeden Halt fallen lassen" eine Regel, die den
ersten Fall besteht und die Arbeit des Spielers mitnimmt.

---

## 4. Die drei `Undo`-Faelle, einzeln

AK-15 nennt drei Formen ausdruecklich. Alle drei laufen ueber dieselbe
Schluesselliste, und das ist der Grund, warum sie ueberhaupt gemeinsam
loesbar sind.

| Fall | Test | Was er festhaelt |
|---|---|---|
| **vorher leer** | `test_undo_puts_a_slot_that_was_empty_back_to_empty` | Der Fall, den ein in Relikten geschriebenes Zurueckstellen falsch macht: es gibt kein Relikt zurueckzulegen, "nichts zuruecklegen" muss ausdrueckbar sein. Der Fall **prueft vorher**, dass beide Slots wirklich leer waren (`== ["", ""]`), sonst waere er gruen, was Undo auch taete. |
| **vorher ein Custom relic** | `test_undo_puts_a_custom_relic_back_where_it_was` | Ein Custom relic gehoert niemandem und steht in keiner Liste; es ueberlebt ein Zurueckstellen nur, indem es aus dem Aufgeschriebenen neu gebaut wird (QA-025). Geprueft wird nach dem Undo `relic_id == inventory.CUSTOM_RELIC_ID` **und** die Effektliste, nicht nur der Schluesselvergleich. |
| **vorher belegt** | `test_undo_puts_an_occupied_slot_back_to_its_own_copy` | Der Slot bekommt vorher gezielt eine **andere** Kopie, damit das Anwenden wirklich etwas veraendert; danach steht die alte Kopie wieder da. |

Dazu zwei Faelle, die keine der drei Formen sind, sondern das Modell
darum: `test_undo_after_two_uses_takes_both_of_them_back` (Annahme 1) und
`test_a_real_optimize_can_be_applied_and_taken_back` - der einzige Fall
der beiden neuen Dateien, der den **echten** Lauf ueber den **echten** Save
fuehrt, anwendet und zurueckdreht. Er haelt ausdruecklich fest, dass sich
die Slots durch das Anwenden geaendert haben, sonst waere er gruen, was
`apply_all` auch taete.

---

## 5. Die vier Gegenbauten, einzeln gefahren

Jeder wurde einzeln in den Baum geschrieben, gefahren und wieder entfernt;
der Baum ist danach jedes Mal auf `git diff` geprueft worden.

### Gegenbau 1 - `Apply all` fasst auch gehaltene Slots an (AK-57)

**Aenderung:** in `Planner._apply_the_answer_to` wird
`if index >= len(slots) or index in held:` zu `if index >= len(slots):` -
die Halte-Bedingung faellt weg.

**Ergebnis: rot.** 2 von 38 Faellen fielen:
- `test_apply_all_does_not_touch_a_held_slot`
- `test_apply_all_does_not_fill_a_slot_held_empty`
  (`AssertionError: assert '3229614199|13001|7280000,7031900|' == ''`)

**Warum dieser Gegenbau ueberhaupt beisst (L-008b/Fallenform 4):** eine
Anfrage nimmt die gehaltenen Slots heraus, also nennt eine **nach** dem
Halt gerechnete Antwort keinen gehaltenen Slot, und ein Filter darueber
waere ein aequivalenter Mutant. Der Fall faehrt deshalb die **andere**
Reihenfolge: die Antwort kommt, **dann** haelt der Spieler einen der Slots,
die sie nennt. Das ist der einzige Weg, auf dem ein gehaltener Slot in
einer lebenden Antwort steht - und der Weg, den ein Spieler wirklich geht.

### Gegenbau 2 - der Haltezustand wird nach `QSettings` geschrieben (OF-15)

**Aenderung:** `_hold_changed` schreibt `repr(self._holds)` unter den
Schluessel `holds` in `QSettings(favourites.ORG, favourites.APP)`, und
`Planner.__init__` liest ihn mit `ast.literal_eval` zurueck. Ein
vollstaendiges Schreiben **und** Lesen, weil ein Schreiben ohne Lesen die
Verhaltensfaelle gruen liesse und trotzdem den Schluesselraum vergroessert.

**Ergebnis: rot.** 2 von 18 Faellen fielen:
- `test_a_window_opened_afresh_holds_nothing`
  (`assert frozenset({0}) == frozenset()`) - **das ist der Fall, den der
  Auftrag zu bauen verlangt.** Er baut ein **zweites** `Planner`-Fenster
  ohne `clear_settings()`, was der Unterschied zwischen einem Neustart und
  einer frischen Installation ist; die Fixture `planner` aus `conftest.py`
  leert den Speicher vorher und haette den Mutanten am Leben gelassen.
- `test_holding_writes_nothing_to_the_settings_store` - die schaerfere
  Haelfte: `QSettings.allKeys()` vor und nach zwei Haltevorgaengen ist
  dieselbe Liste. Dieser Fall faellt auch dann, wenn nur geschrieben und
  nie gelesen wird.

### Gegenbau 3 - `Undo apply` stellt einen vorher leeren Slot als belegt wieder her

**Aenderung:** in `Planner._restore_slot_keys` faellt bei leerem Schluessel
das `slot.clear_relic()` weg (`if not key: continue`) - der Slot behaelt
also, was das Anwenden hineingelegt hat.

**Ergebnis: rot.** 4 von 20 Faellen fielen:
- `test_undo_puts_a_slot_that_was_empty_back_to_empty` - der Fall, fuer den
  der Gegenbau geschrieben ist
  (`At index 1 diff: '3229614263|135|7020000,...' != ''`)
- `test_undo_puts_a_custom_relic_back_where_it_was`,
  `test_undo_after_two_uses_takes_both_of_them_back`,
  `test_a_real_optimize_can_be_applied_and_taken_back` - **nur nebenbei
  mitgefallen**, weil in ihren Belegungen auch leere Slots vorkommen. Sie
  sind kein Beleg fuer die Regel, fuer die der Fall oben steht.

### Gegenbau 4 - ein vierter Aktionsknopf ist gleichzeitig sichtbar (AK-07)

**Aenderung:** ein zusaetzlicher `QPushButton("Undo apply")` wird in
`AdvisorBar.__init__` in die Reihe gesetzt und in `_show_the_actions` mit
den anderen sichtbar geschaltet - der naheliegende Bau, den die
Ein-Knopf-Loesung vermeidet.

**Ergebnis: rot.** 5 von 69 Faellen fielen, darunter
- `test_never_a_fourth_action_in_any_state_of_the_row` - der Fall, der
  **jeden** Zustand aus `advisorbar.State` durchgeht statt nur den
  belebtesten
- `test_advisor_bar.py::test_never_more_than_three_actions_stand_beside_the_status`
  (`assert 4 <= 3`)
- drei Faelle ueber die Beschriftungsliste (`["Apply all", "Why", "Clear"]`)

**Kein Gegenbau ist gruen geblieben.**

---

## 6. Messungen (mit Messumgebung, L-009)

Umgebung: Windows 10, Python 3.12.10 aus `.venv`, PySide6, Stil **Fusion**
(durch `app.apply_appearance`, wie der Spieler ihn laeuft), UI scale
**Automatic**, **logische** Pixel, gemessen vor dem ersten `show()` am
gebauten `Planner`. Skript:
`scratchpad/measure_floor2.py` (Arbeitskopie, nicht committet), Baum-Stand
`725182f`.

Gemessen im belebtesten Zustand der Leiste - alle drei Aktionsknoepfe
gleichzeitig sichtbar (`['Optimize', 'Apply all', 'Why', 'Clear']`):

| Groesse | Plattform `windows` | Plattform `offscreen` |
|---|---|---|
| Fensterboden `minimumSizeHint()` | **760 x 547 px** | 988 x 508 px |
| mittlere Spalte, Mindestbreite | 68 px | 68 px |
| Leiste, eigene Mindestbreite | 568 px | 714 px |
| Leiste, `sizeHint().height()` | 36 px | 34 px |

**Der Fensterboden hat sich nicht bewegt.** `advisorbar.py` haelt fuer
denselben Baum und dieselbe Umgebung am 07.09.2026 - **vor** diesem Auftrag
- 760 px fest ("760 px against the page's 756"). Nach drei neuen Knoepfen
in der Leiste und einem in jeder Slotkarte steht er unveraendert bei 760.
Der Grund ist die Groessenpolitik: die Leiste ist horizontal `Ignored`
(ihre eigenen 568 px erreichen das Fenster nicht), und die Slotkarten
liegen in der `QScrollArea`. Die Hoehe 36 px liegt unter dem Budget von 44
(§3.1: hoechstens 32 px Inhalt plus 6 px oben und unten).

Die beiden Plattformen sind **verschiedene Zahlen fuer dieselbe Sache** -
der offscreen-Boden ist 228 px breiter und 39 px niedriger. Wer eine dieser
Zahlen zitiert, muss die Plattform mitzitieren.

---

## 7. Testergebnis

| Lauf | Ergebnis | Dauer |
|---|---|---|
| **vorher**, Arbeitsbaum (`fd9f2bc`), selbst gemessen | **1146 passed, 9 skipped, 5 deselected** | 550,03 s |
| vorher, Zahl aus dem Auftrag | 1146 passed, 9 skipped, 5 deselected | - |
| nach Commit 1 (Anwenden), Arbeitsbaum | 1171 passed, 9 skipped, 5 deselected | 563,12 s |
| nach Commit 2 (Festhalten), Arbeitsbaum | 1189 passed, 9 skipped, 5 deselected | 623,46 s |
| **nachher**, Arbeitsbaum (`725182f`) | **1190 passed, 9 skipped, 5 deselected** | 621,35 s |
| **nachher, frischer Klon von `725182f`** | **1190 passed, 9 skipped, 5 deselected** | 622,47 s |

Befehl jedes Mal `.venv\Scripts\python.exe -m pytest -m "not slow"`. Der
Klonlauf lief in einem `git clone` des Repos im Scratchpad, mit dem
Interpreter des Hauptbaums; `tests/conftest.py` stellt den Klonpfad an
`sys.path[0]`, es lief also der Klon. **Die Zahl aus dem Klon und die aus
dem Arbeitsbaum stimmen ueberein.**

**+44 Faelle**: 21 in `tests/test_advisor_apply.py` (neu), 18 in
`tests/test_advisor_hold.py` (neu), 2 neue Zeilen der §4-Tabelle (4.9 ist
jetzt drei Faelle statt einem), 1 neuer Fall in `test_advisor_bar.py`
(`effects_without_a_figure` ohne Klausel), 2 neue in
`test_advisor_block.py` (`use_requested`, `may_be_used`).

Die 9 Skips sind dieselben wie vorher (Faelle, die die installierte
Spielinstallation brauchen). Keiner der neuen Faelle hat auf dieser
Maschine geskippt - insbesondere ist der Fall mit dem echten
`Optimize`-Lauf gelaufen, nicht uebersprungen.

**Linter:** das Projekt hat keinen konfiguriert. Geprueft am Bestand, nicht
aus einer Notiz: es gibt weder `pyproject.toml` noch `setup.cfg`, `tox.ini`,
`.flake8`, `ruff.toml` oder `.pylintrc` (die einzige Konfigurationsdatei ist
`pytest.ini`); `requirements-dev.txt` enthaelt genau eine Zeile,
`pytest==9.1.1`; und `.github/workflows/` (`tests.yml`, `release.yml`) nennt
`ruff`, `flake8` und `pylint` nirgends. Der Punkt entfaellt damit nach dem
Nutzerentscheid vom 06.09.2026.

**Abweichung von der Testumgebung des Auftrags:** der Auftrag nennt
Python 3.11; `.venv\Scripts\python.exe -V` sagt **Python 3.12.10**, und
`pytest` nennt in jedem Lauf dieselbe Fassung. Alle Zahlen oben sind auf
3.12.10 gemessen. Kein Grund zur Sorge, aber die Angabe im Auftrag ist
falsch und sollte fuer die naechste Rolle berichtigt werden.

---

## 8. Ein bestehender Test wurde umgeschrieben (nicht geloescht)

`tests/test_advisor_block.py::test_the_block_carries_no_control` hielt
fest, dass der Block **kein** Bedienelement traegt - mit der Begruendung,
Anwenden sei eine Sache fuer eine spaetere Aufgabe. Diese Aufgabe ist die
spaetere. Der Fall heisst jetzt
`test_the_block_carries_the_one_control_of_the_section` und haelt die
Nachfolgeaussage fest: **genau ein** Knopf, und der heisst `Use`. Er wurde
nicht entfernt, um gruen zu werden - er prueft dieselbe Eigenschaft
(welche Knoepfe der Block hat) gegen die jetzt geltende Vorgabe, und er
fragt weiterhin **alle** Knoepfe ab statt der, an die sich der Fall
erinnert.

Ebenso wurde der Docstring von
`test_never_more_than_three_actions_stand_beside_the_status` berichtigt: er
sagte "Today the row offers `Clear` and nothing else", was seit Commit 1
falsch ist.

---

## 9. L-006: die Eigenschaft, nicht die Fundstelle

QA-188 nennt `advisorbar.py:181`. Gesucht wurde projektweit nach beiden
alten Wortlauten, mit zwei unabhaengigen Masken:

- Maske 1, ueber alle `*.py` des Baums: `carry no numbers|working out\. Optimize`
  - **6 Treffer, davon 0 lebendig**: drei Kommentare in `nrdata/extract.py`
    und `nrplanner/model.py` ueber SpEffect-Zeilen ohne Zahlen, drei Stellen
    in `tests/test_advisor_explain.py`, die den Satz ausdruecklich
    **verbieten**.
- Maske 2, ueber `UI_SPEC.md`: alle Zeilen mit `ersetzt`/`buchstabengetreu`
  im Umfeld der §4-Zustaende, um zu sehen, ob T-084 noch weitere Wortlaute
  nachgezogen hat, die im Code stehen. Gefunden wurden 4.7 (AK-173) und
  4.9 (AK-142/AK-143) - beide sind dieser Auftrag - sowie AK-162/AK-163
  (Registry und Picker) und AK-190, die alle **nicht** in
  `advisorbar.py`/`advisorblock.py` stehen.

**Keine weitere Fundstelle desselben Musters im Code.**

---

## 10. An den `qa-engineer`

**Was zu pruefen ist:**

1. **`Apply all` gegen den Picker** (AK-14): dieselben Relikte einmal per
   `Apply all` und einmal einzeln im Picker gewaehlt - Statblatt, Slotkarten
   und der gespeicherte Kelch muessen deckungsgleich sein. Ich pruefe die
   Schluesselliste und den Speicher; das Statblatt Zeile fuer Zeile ist
   E2E.
2. **`Undo apply` nach einem Kelchwechsel.** `Undo apply` bleibt sichtbar,
   solange 4.13 steht; ein Kelchwechsel geht ueber `recompute` und wirft die
   Antwort weg, womit auch die Aufzeichnung faellt. Der Weg ist gebaut und
   von `test_a_change_of_the_build_after_applying_still_ends_the_answer`
   gedeckt - aber nur ueber den Level-Schieber, nicht ueber die Kelchliste.
3. **`Use` auf allen sechs Karten hintereinander**, dann `Undo apply`
   (Annahme 1 in Aktion). Ich messe zwei Karten, nicht sechs.
4. **Halten waehrend ein Lauf laeuft.** Der Halt geht in die **naechste**
   Anfrage; ein laufender Lauf wird davon nicht abgebrochen (Halten ist
   keine Buildaenderung nach AK-12). Ungeprueft, ob das die erwartete
   Erfahrung ist.
5. **Deep-Schalter mit gehaltenen Deep-Slots.** Deep aus - der gehaltene
   Slot 4 verschwindet aus `active_slots`, sein Halt bleibt unter dem
   anderen Schluessel liegen. Die zehn Rundreisen decken das; ein Spieler,
   der dabei zusaetzlich Relikte bewegt, nicht.
6. **AK-06 mit lebendem Vorschlag und sechs belegten Deep-Slots bei UI
   scale 150 %.** Die Karten tragen jetzt einen Knopf mehr und der Block
   auch. Ich habe bei UI scale Automatic gemessen (Abschnitt 6), nicht bei
   150 %.

**Randfaelle, die ich absichtlich gebaut habe und die im echten Spiel
schwer herzustellen sind** (sie sind in den Testdateien, aber E2E gehoert
Ihnen): eine Antwort, die eine Kopie nennt, die der Save nicht hat; eine
Antwort fuer einen Slot, den das Gefaess nicht hat; ein Halt, dessen
Relikt zwischen zwei Save-Lesungen verschwindet.

---

## 11. An den `ui-ux-designer`

- **Drei Entscheidungen, die `UI_SPEC` offen laesst** - Annahmen 1, 2 und 3
  in Abschnitt 2. Alle drei sind eine Zeile Code, wenn Sie sie anders
  wollen.
- **Der Tooltip des `Hold`-Knopfes ist ein einfacher Literal**, nicht als
  Rich Text verpackt. §3.5 verlangt die Verpackung fuer Tooltips, die
  fremden Text tragen; dieser traegt einen Hauskonstanten-Satz, und AK-54
  verlangt ihn **woertlich**. Eine `<span>`-Huelle wuerde `toolTip()` von
  der Vorgabe abweichen lassen, ohne auf dem Schirm etwas zu aendern.
- **`_slots_with_nothing`s Mehrzahl** (aus T-083) steht weiterhin
  ungeprueft; ich habe sie nicht angefasst. Die neuen Mehrzahlformen 4.9a
  und 4.9b sind dagegen woertlich aus §5 der T-078-Fassung.
- **Der `Use`-Knopf traegt keinen Tooltip.** §3.2 nennt keinen, und ich
  habe keinen erfunden.

---

## 12. An den `director`

### 12.1 Nicht geliefert, ausserhalb des Umfangs

**AK-56 hat zwei Orte, gebaut ist einer.** Der Satz am Slot
(`A relic you were holding is no longer in your inventory, so this slot was
released.`) steht. Die zweite Haelfte - die Zeile in den `unknowns` des
naechsten Laufs, AD-017.3 woertlich
`"A held slot was released: that relic is no longer in your inventory."` -
gehoert nach `nrplanner/advisor/run.py` bzw. `explain.py`. Beide stehen
**nicht** unter "Beruehrt Dateien", `explain.py` ist ausdruecklich
ausgeschlossen. **AK-56 ist damit halb erfuellt** und braucht einen eigenen
kleinen Auftrag. Aufwand: klein - der Lauf muesste die freigegebenen Halte
aus dem Request erfahren, was heute niemand ihm sagt; der Request traegt
die **verbliebenen** Halte, nicht die weggefallenen. Das ist die eigentliche
Arbeit daran: eine Stelle, an der die Freigabe den Lauf erreicht.

### 12.2 Zur Kenntnis

- **Bestehende Schuld, nicht angefasst:** QA-189 (`_ARMAMENT_GATES` in
  `ARCHITECTURE.md` und `UI_SPEC.md`) und SEC-021 (`_sync_mode` und
  `curse_tooltip` maskieren nicht) stehen wie sie standen. **SEC-021 wurde
  nicht vergroessert:** die zwei Zeilen, die ich `_sync_mode` hinzugefuege
  (`HELD_EMPTY`, `HOLD_RELEASED`), sind Modulkonstanten ohne fremden Text.
  `empty_reason` lief schon vorher ungeschuetzt durch dieselbe Stelle.
- **Zeilenende-Rauschen:** `nrplanner/advisorbar.py` und
  `tests/test_advisor_bar.py` standen beim Start als geaendert mit leerem
  `git diff` in `git status`. Beide habe ich wirklich geaendert; `git diff
  --stat` zeigte vor dem Commit 203 bzw. 80 geaenderte Zeilen, keine
  Ganzdatei-Umschreibung. Die drei Commits tragen nur meine Zeilen.
- **Kein `push`, kein Branch, kein Merge.** Drei Commits auf
  `docs/audit-and-advisor-design`.
- **`docs/state.md` habe ich nicht angefasst.** Einzutragen waeren: S10b
  ist vollstaendig (T-089 zeichnet und erklaert, T-091 wendet an und haelt
  fest), QA-188 geschlossen, AK-56 halb erfuellt, Suite bei 1190.

### 12.3 Was mir aufgefallen ist und nicht in den Auftrag gehoerte

1. **`ANSWERED_STATES` ist jetzt zweideutig benannt.** Es heisst "Zustaende
   mit einer Antwort", enthaelt aber 4.13 nicht, obwohl dort eine Antwort
   steht. Ich habe `ACTING_STATES` danebengestellt statt umzubenennen, weil
   `ANSWERED_STATES` in `test_advisor_bar.py` als oeffentliche Zusicherung
   gelesen wird. Kleine Schuld, ein Umbenennen waere sauberer.
2. **`Planner` waechst.** `nrplanner/app.py` steht bei rund 4300 Zeilen und
   `Planner` traegt jetzt zusaetzlich das Anwenden und den Haltezustand.
   Kein Fehler, aber die naechste Rolle, die den Picker (S10c) an dieselbe
   Klasse haengt, arbeitet in einer Datei, in der "wo steht das" teuer
   geworden ist. Empfehlung: **keine** Umstrukturierung nebenbei, sondern
   ein eigener Auftrag, falls es weh tut.
3. **`_show_the_holds()` laeuft jetzt in jedem `recompute()`.** Es fragt
   die Inventarliste nur, wenn ueberhaupt ein Halt gesetzt ist - der uebliche
   Fall kostet sechs Schleifendurchlaeufe. Ich habe **nicht** gemessen, was
   das an Rechenzeit ausmacht, und halte es fuer irrelevant neben dem
   Neubau des Statblatts, das im selben Aufruf steht. Falls S11 den
   `recompute`-Pfad misst, gehoert die Stelle in die Liste - **nicht** von
   mir zu optimieren.
4. **`test_a_real_optimize_can_be_applied_and_taken_back` ist der einzige
   Fall der beiden neuen Dateien, der den echten Suchlauf faehrt**, und er
   kostet allein rund 4 Sekunden. Die Suite ist von 550 s auf 621 s
   gewachsen, also um 71 s fuer 44 Faelle - der groesste Teil davon geht
   auf die `planner`-Fixture, die je Fall ein volles Fenster baut. Falls
   das zum Problem wird, waere `shared_planner` fuer die Faelle ohne
   Slotaenderung der Hebel; die meisten meiner Faelle aendern Slots und
   duerfen ihn nicht nehmen.
