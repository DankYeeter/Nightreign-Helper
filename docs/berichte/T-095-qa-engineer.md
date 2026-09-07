STATUS: erledigt
AUFTRAG: T-095 — Erstpruefung des Build-Beraters gegen A3 bis A8
GELESEN: docs/tasks/T-095.md (vollstaendig, inkl. GOAL.md-Zitate A3-A8 und
state.md-Auszug); .claude/agent-memory/qa-engineer/MEMORY.md und die drei
referenzierten Memory-Dateien (project_nightreign_guard_gaps.md,
project_differential_harness.md, project_qa_sandbox_input_limits.md);
docs/state.md (vollstaendig, fuer den Kontext der 07.09-Entscheidungen);
qa/findings.md (Zeilen 1829-1839, QA-180 bis QA-189); git log/git show auf
90ff81d, d7ed2df, ae02d09, 4462a88, 22ec73e und die Commitkette 90ff81d..HEAD;
Quellcode im eigenen Klon: nrplanner/advisor/{evaluate,candidates,search,
explain,goals,run,worker}.py vollstaendig, nrplanner/relicpicker.py
(Ausschnitte um Ranking/ValueBlock/Curse-Chips), ARCHITECTURE.md (AD-018,
AD-019, Nachtrag II); Testdateien tests/test_advisor_explain.py,
tests/test_advisor_hold.py, tests/test_advisor_apply.py,
tests/test_relic_picker_advisor.py (vollstaendig/in Ausschnitten),
grep-Uebersicht ueber alle tests/test_advisor_*.py und
tests/test_relic_picker_*.py; scripts/measure_advisor_picker.py und
scripts/measure_advisor_language.py (gelesen und im Klon ausgefuehrt).
GEAENDERT: keine Datei im Arbeitsbaum ausser diesem Bericht. Im eigenen Klon
(Scratchpad) frei gearbeitet: `git clone --no-hardlinks` nach
`...\scratchpad\t095_clone`, dort testweise `scripts/_qa095_duchess_probe.py`
angelegt (Wegwerf-Skript, nicht Teil des Projekt-Repos).
ANNAHMEN: Der im Auftrag zitierte state.md-Satz "QA-180 ist die Instanz und
offen — A5 ist deshalb heute nicht erfuellt" wird als Pruefgegenstand
behandelt, nicht als gegebene Tatsache — meine Messung widerspricht ihm (siehe
A5 und "Bekannte Befunde" unten). Wo ARCHITECTURE.md/GOAL.md/state.md und der
tatsaechliche Code auseinanderliefen, habe ich dem Code und einer eigenen
Ausfuehrung Vorrang gegeben.
NAECHSTER: director
BLOCKIERT DURCH: nichts

---

# T-095 — Pruefung des Build-Beraters gegen A3-A8

## Die Testfrage zuerst: pruefen die Tests die Kriterien, oder nur den Code?

**Gemischt, und das Bild ist besser als der Auftrag unterstellt.** Fuer drei
der neun mitgegebenen Befunde (QA-180, QA-183, QA-187) fand ich beim Nachlesen
des Codes und beim Ausfuehren der zustaendigen Tests/Messskripte, dass sie
**bereits behoben** sind — mit echten Regressionstests, die auf der ID/dem
Slot pruefen und nicht mehr auf dem Namen. Der Fix zu QA-180 (Commit
`90ff81d`) und die Nachbesserung zu QA-187 (`4462a88`) liegen beide **vor**
dem eingefrorenen Stand (`06c4fe0`) und sind damit Teil dessen, was ich
pruefe. Der Befund-Text in `qa/findings.md` und die daraus abgeleitete
Direktor-Entscheidung vom 07.09. ("QA-180 ist offen — A5 ist deshalb heute
nicht erfuellt") sind an dieser Stelle **veraltet**: Der Fix kam am selben
bzw. am folgenden Tag wie der Fund, die Statuszeile in `qa/findings.md` wurde
nie nachgezogen. Das ist selbst der wichtigste Befund dieses Laufs — siehe
unten.

Gleichzeitig gilt fuer echte Luecken (A3 Heldenabdeckung, A4 Stacking, A6
Picker-Pfad ungefenstert): **ein gruener Lauf sagt nichts** dazu, weil kein
Test danach fragt. Detail je Kriterium unten, mit Beleg.

## A3 — mindestens zwei Zielrichtungen, konkretes Relikt je Slot, jeder Held

**Urteil: CONCERNS.**

Der Mechanismus selbst ist solide und **wird getestet**: `goals.py` fuehrt
genau zwei Richtungen (`max_damage`, `min_damage_taken`), jede Kandidatur
traegt beide Werte (`candidates.pool`), `search.beam` liefert je freiem Slot
ein konkretes Handle. `tests/test_advisor_apply.py::
test_a_real_optimize_can_be_applied_and_taken_back` laesst das gegen den
echten Spielstand laufen.

**Die Luecke ist die Heldenabdeckung, und sie ist gross.** Grep ueber alle
`tests/test_advisor_*.py` und `tests/test_relic_picker_*.py` (382 Treffer
insgesamt) zeigt: **Wylder 372 Treffer, Duchess 10 — die anderen acht Helden
(Guardian, Ironeye, Raider, Revenant, Recluse, Executor, Scholar, Undertaker)
kein einziger.** Die zehn Duchess-Treffer sind ausserdem **keine** Lauf-Tests:
alle acht liegen in `test_advisor_block.py`/`test_advisor_explain.py` und
pruefen ausschliesslich die eine Zeile "works only for Duchess" (Effekt
gehoert einem anderen Helden) — nicht Suche, nicht Anwenden, nicht den Picker.
Vessel-seitig ist es dasselbe Bild: nur drei benannte Kelche tauchen ueberhaupt
auf (`Wylder's Urn`, `Wylder's Chalice`, `Wylder's Earring`), alle zu einem
Helden.

**Die Stichprobe, die den Gegenbeweis versucht:** Ich habe die drei
Kernfunktionen (`candidates.pools`, `search.beam`, `explain.reasons`) selbst
gegen **Duchess' Urn** (Duchess, 3 normale + 3 Deep-Slots, Farben [0,1,1])
laufen lassen — Held und Kelch, die in keinem Test vorkommen:

```
hero: Duchess vessel: Duchess' Urn colours [0, 1, 1] deep [0, 1, 1]
  deep=False: 3 slots, 40 suggestions, top score 1.1095295465270294
    3 slots filled, 12 reason lines, colours match: True
  deep=True: 6 slots, 40 suggestions, top score 1.2425225921291295
    6 slots filled, 31 reason lines, colours match: True
```

Beide Slotarten liefern vollstaendig gefuellte, farblich korrekte
Vorschlaege mit Begruendungszeilen — die Mechanik selbst ist heute nicht
kaputt. Das mindert die Schwere (kein akuter Bug), aendert aber nichts an der
Testbarkeitsluecke: **eine Regression, die nur bei einem der acht nie
geprueften Helden auftritt, wuerde die Suite nicht rot faerben.** Das ist
genau die "unstated reach" aus der Guard-gap-Notiz meines Gedaechtnisses
([[project_nightreign_guard_gaps]]) — ich habe sie hier mit Zahl und
Gegenprobe belegt statt nur zitiert.

## A4 — Slot-Farben, Stacking, Deep-Kennzeichnung

**Urteil: CONCERNS.**

Slot-Farbe ist eine **echte** Abnahmepruefung:
`tests/test_advisor_search.py`, Funktion mit dem Docstring "A4: the
suggestion respects the vessel's own slot colours" — asserted gegen
`inventory.relics_for`, nicht gegen die eigene Ausgabe. Die Deep-Trennung
laeuft durch dieselbe Funktion (`slot.colour, slot.deep` als ein Schluessel in
`candidates.pool`/`FrozenInventory`) und ist laut meinem Guard-gap-Gedaechtnis
bereits mit toetendem Gegenbau bestaetigt.

**Stacking ist die bestaetigte Luecke (QA-181), und ich habe sie strukturell
nachvollzogen statt nur zitiert.** `evaluate.effect_ids_of` reiht die IDs
jedes gewaehlten Kandidaten **ungeprueft aneinander** (Zeile 56-58): kein Code
dort fragt, ob eine ID schon vorkam. Die Korrektheit von heute steht und
faellt allein damit, dass jede Liste (`candidate.effect_ids`) jede ID genau
einmal traegt — das ist heute so, aber nichts hindert eine kuenftige Aenderung
daran, es zu brechen. Getestet wird nur die **Reihenfolge** der drei Quellen
(gehaltene Relikte, gewaehlte Kandidaten, Waffen), nie die Vielfachheit. Die
QA-181-Messung (ein doppelt gezaehlter, nicht stapelbarer Effekt hebt
`max_damage` um 2,6 % und die volle Suite bleibt gruen) habe ich nicht erneut
mutiert (Zeitbudget), aber der Code ist exakt in der beschriebenen Form —
**bestaetigt**, nicht widerlegt.

## A5 — nachvollziehbare Begruendung in Nutzersprache

**Urteil: CONCERNS — nicht FAIL, wie die state.md-Entscheidung vom 07.09.
nahelegt.**

**QA-180 ist gemessen behoben, nicht offen.** Drei voneinander unabhaengige
Belege:

1. **Code:** `model.SourceEntry` ist ein `NamedTuple(name, own, effect_id)`;
   `explain._attributed` (Zeile 141-186) matcht ueber `entry.effect_id !=
   effect_id`, nie ueber den Namen. Der Docstring sagt es explizit: "Matched
   on the effect id, never on the name (QA-180)."
2. **Commit:** `90ff81d` ("fix(advisor): attribute a figure to the effect's
   id, not to its name (QA-180)") liegt **vor** dem eingefrorenen Stand
   `06c4fe0` und traegt seine eigene Messung: "130 lines ... 47 filled slots
   got no line ... After this change: 0 and 0."
3. **Eigener Testlauf, heute, gegen den echten Spielstand:**
   ```
   tests/test_advisor_explain.py::test_two_effects_of_one_name_are_credited_to_the_slot_that_carries_them PASSED
   tests/test_advisor_explain.py::test_a_name_two_effects_share_in_this_dataset_still_lands_on_two_slots PASSED
   2 passed, 49 deselected in 0.95s
   ```
   Der zweite Test sucht das Kollisionspaar **im echten Datensatz**
   (`advisor.two_effects_the_dataset_gives_one_name`, 160 von 707 Namen
   betroffen) und prueft die Zuordnung slot-genau gegen eine aus
   `model.compute` abgeleitete, vom Modul unabhaengige Erwartung.

**Der Auftragstext hat trotzdem recht mit einer Teilaussage:** der
**urspruengliche** Abnahmefall `test_the_reasons_name_only_effects_the_
suggestion_brought` prueft wirklich nur `any(name in line for name in
allowed)` — er waere fuer eine Namenskollision blind. Er ist nur nicht mehr
der **einzige** Test auf diesem Pfad; die beiden oben genannten wurden mit dem
Fix ergaenzt und pruefen die Zuordnung, nicht nur die Namensmenge.

**QA-187 (Fuellungsreihenfolge der stummen Zeilen) ist ebenfalls gemessen
behoben.** Eigener Lauf von `scripts/measure_advisor_language.py` gegen den
echten Spielstand (309 Relikte, 845 Effektrollen, Wylder Stufe 15):

```
(a)  works only for another Nightfarer        150 of 426
(a2) another copy is already counted            0 of 426
(b)  waits on a condition                     144 of 426
(c)  depends on the armaments carried          38 of 426
(d)  no number here                            94 of 426
(e)  not in the game data                       0 of 426
```

Das ist exakt die von QA-187 **verlangte** Verteilung (150/0/144/38/94/0),
nicht mehr die gebaute falsche (150/0/170/13/93/0). Der Reparatur-Commit
`4462a88` ("(c) vor (b), und (c) fragt, was die Rechnung beantwortet hat")
liegt ebenfalls vor `06c4fe0`.

**QA-183 (Kongruenzfehler "is"/"were") ist ebenfalls gemessen behoben** —
`explain._held_slots_line` traegt jetzt zwei getrennte Zaehler fuer die zwei
Verbformen, und ein eigener Test haelt es fest:
`assert lines == ("1 of 2 slots is held, so only the other 1 was filled.",)`
in `tests/test_advisor_explain.py` (um Zeile 1729).

**Was daraus folgt: ein wiederkehrendes Muster, nicht drei Einzelfaelle.**
QA-180, QA-183 und QA-187 wurden alle am selben oder am naechsten Tag
behoben, wie sie gefunden wurden (T-077/T-089/T-090), aber die Statuszeile in
`qa/findings.md` blieb in allen drei Faellen auf "offen" stehen — und genau
diese Zeile hat die state.md-Entscheidung vom 07.09. ("A5 ist deshalb heute
nicht erfuellt") ungeprueft uebernommen. Das ist die Art Befund, die dieser
Auftrag ausdruecklich sucht: ein gruener Zustand, den niemand nachgezogen hat,
diesmal in der falschen Richtung — als **zu pessimistisches** Statusbild
statt als zu optimistisches.

**Was fuer A5 wirklich offen bleibt** (nicht neu, nur bestaetigt, nicht
selbst nachmutiert): **QA-185** — zwei weitere namensbasierte Stellen
(`model.py:983-990`, `app.py:3142`), heute 0 von 456 Paaren betroffen, aber
ungewacht, falls ein kuenftiger Spielstand ein Kollisionspaar dort trifft.
**QA-184** (unerreichbarer Leerpool-Fall, Minor). Diese beiden halten A5
bei CONCERNS statt PASS.

## A6 — blockiert nicht

**Urteil: CONCERNS.**

Der `Optimize`-Lauf (der Beam-Search) ist architektonisch sauber
hintergrundgelagert: `worker.py` baut einen echten `QThread`, mit Debounce,
Generation-Zaehler und `requestInterruption()`-Abbruch, dokumentiert gegen
AD-006. `tests/test_advisor_worker.py` misst das mit `time.perf_counter`
gegen die 200-ms-Reaktionszeit aus AK-11 — eine echte, zeitbasierte
Pruefung, kein Attrappentest.

**Der Relic Picker — laut F2 der Hauptweg — laeuft dagegen bewusst
synchron im aufrufenden (GUI-)Thread.** `relicpicker.py`, Docstring zu
`SlotAdvice.ranking`: *"The pool is computed here, in the calling thread,
and that is deliberate: AD-018 measures the worst slot at ~51 ms ..., so
there is nothing to draw a wait for."* Das ist eine bewusste
Architekturentscheidung, keine Nachlaessigkeit — aber sie steht und faellt
mit der Zahl.

**Ich habe die Zahl heute selbst nachgemessen**, mit dem im Repo vorhandenen
Skript `scripts/measure_advisor_picker.py`, gegen den echten Spielstand
(309 Relikte, Wylder's Chalice, Stufe 15, Median von 3 Laeufen):

```
slot 0 colour 0 deep False:   52 candidates,   17.7 ms
slot 1 colour 2 deep False:   53 candidates,   17.3 ms
slot 2 colour 4 deep False:  206 candidates,   67.0 ms   <- weisser Slot, groesster Pool
slot 3 colour 0 deep True :   23 candidates,    7.6 ms
slot 4 colour 1 deep True :   30 candidates,   10.3 ms
slot 5 colour 3 deep True :   21 candidates,    7.4 ms
```

67 ms statt der in `ARCHITECTURE.md` genannten ~51 ms (andere Messung, selbe
Groessenordnung) — komfortabel unter den 200-250 ms, die AK-11 fuer die
Suche als Budget nennt. Auf dem heutigen Datenstand blockiert der Picker die
Oberflaeche also nicht spuerbar.

**Zwei Luecken bleiben, beide unbewacht:**
1. **Keine Regressionsschranke.** Kein Test im ganzen Repo behauptet eine
   Obergrenze fuer diese Rechenzeit — sie ist ein einmaliges Skriptergebnis,
   kein gruener Waechter. Waechst die Rechnung (mehr Relikte, teurere
   Kandidatenbewertung), faellt nichts rot, bis ein Nutzer es fuehlt. A6
   verlangt ausdruecklich "bei grossen Relikt-Bestaenden bleibt die
   Antwortzeit im gemessenen Budget" — das Budget existiert nur als
   Kommentarzeile in `ARCHITECTURE.md`, nicht als Pruefung.
2. **Die 51/67 ms decken nur die Zahlen-Rechnung.** Das Oeffnen des Dialogs
   baut zusaetzlich bis zu ~205 Kartenwidgets auf; diese Kosten sind in
   keiner Messung, die ich gefunden habe, enthalten. Ob **das** die
   Oberflaeche spuerbar blockiert, ist unbeantwortet — weder durch Test noch
   durch Messskript.

Da A6 laut Auftrag noch keinen Zielwert hat, bewerte ich "blockiert nicht":
haelt heute, gemessen; **CONCERNS** wegen der fehlenden Regressionsschranke
auf dem jetzt wichtigsten Pfad.

## A7 — sagen, wo Daten nichts hergeben

**Urteil: CONCERNS.**

Die Architektur ist breit und mit echten Zaehlern belegt: `candidates.
_pool_findings` (Griffe ohne Handle, bedingte Effekte, unmodellierte
Konvertierung — je mit eigenem Zaehler und eigener Zeile), `explain.
not_counted`, `explain.unknowns`, `explain.data_note`, die sechs
Stumm-Fuellungen und die drei Fluch-Fuellungen — alle mit Nenner (AD-025.2)
und, soweit ich im vorhandenen Testbestand nachvollzogen habe, mit
Einzeltests belegt (`test_advisor_candidates.py`, `test_advisor_explain.py`).
Die "not one figure is computed here"-Garantie des Pickers (jede Zahl kommt
aus `SlotPool`, keine zweite Rechnung) ist durch den Bit-Vergleich
`ranking.gain(item, goal_id).hex() == types.marginal_for(candidate,
goal_id).hex()` in `test_relic_picker_advisor.py::
test_the_figure_on_a_cards_own_float` (Checkpoint 15, AD-018) tatsaechlich
scharf getestet — ich habe diesen Lauf im Vollsuite-Ergebnis bestaetigt
(0 Skips in den 48 Picker-Tests).

**Nicht neu re-verifiziert, nur uebernommen:** QA-186 (`GATE_FIELDS`
verwechselt 51 Gegenstandseffekte mit Waffenanzahl, seit T-090 sichtbar
widerspruechlich zur eigenen Beraterzeile) — liegt ausserhalb des heutigen
Fokus (Effects-Tab, nicht Advisor-Kern), ich habe nur kurz gegengelesen, dass
die `_GATES_*`-Aufteilung in `explain.py` bereits die von QA-186/QA-187
verlangte Trennung ueber `model.WEAPON_TYPE_GATES` nutzt statt sie zu
wiederholen — das mindert QA-186 nicht, es zeigt nur, dass der Advisor-Teil
der Klasse sauber ist, waehrend der Tab-Teil offen bleibt.

## A8 — alles Englisch

**Urteil: CONCERNS.**

Zwei unabhaengige Suchmasken gegen die Advisor-nahen Oberflaechendateien
(`relicpicker.py`, `advisorbar.py`, `advisorblock.py`,
`nrplanner/advisor/*.py`): eine Unicode-Umlaut-Suche
(`[äöüßÄÖÜ]`, Treffer nur bei ×, ✦, ✓ und typografischen Anfuehrungszeichen —
keine deutschen Woerter) und eine Stichwortsuche auf deutsche Fuellwoerter
("nicht", "und", "oder", "Fehler", "kein", "keine", "bitte") in den drei
GUI-Dateien — **null Treffer**. A8 haelt heute auf dem geprueften
Ausschnitt.

**Kein Waechter, an keiner Stelle.** Wie im Gedaechtnis
([[project_nightreign_guard_gaps]]) bereits notiert: es gibt im ganzen Repo
keinen Test, der auf ASCII/Englisch prueft. Meine Suche deckt nur die fuer
diesen Auftrag relevanten Dateien ab, nicht das gesamte Programm (A8 gilt
programmweit) — das ist der Nenner, den diese Aussage braucht: **8 Dateien
geprueft, 0 Treffer, 0 automatischer Schutz.**

## Bekannte Befunde — bestaetigt oder widerlegt

| Befund | Ergebnis meiner Messung |
|---|---|
| QA-180 | **Widerlegt.** Behoben in `90ff81d`, vor dem eingefrorenen Stand. Zwei einschlaegige Tests pruefen heute auf ID/Slot und sind gruen (eigener Lauf, siehe A5). |
| QA-181 | **Bestaetigt.** `evaluate.effect_ids_of` bleibt strukturell ungeschuetzt gegen doppelte IDs; Code gelesen, nicht neu mutiert. |
| QA-182 | Nicht neu gemessen (Zeitbudget) — weder bestaetigt noch widerlegt. |
| QA-183 | **Widerlegt.** Behoben, eigener Test in `test_advisor_explain.py` haelt die korrigierte Kongruenz fest. |
| QA-184 | Nicht neu gemessen — ausserhalb des Fokus, P3/Minor. |
| QA-185 | **Bestaetigt** in seiner eigenen Formulierung (0 von 456 Paaren heute betroffen, latent) — konsistent mit dem, was ich in `explain.py`/`model.py` gesehen habe. |
| QA-186 | Nicht neu gemessen — ausserhalb des Advisor-Kerns, siehe A7. |
| QA-187 | **Widerlegt.** Behoben, eigener Messlauf trifft die verlangte Verteilung exakt. |
| QA-188 | Nicht neu gemessen (UI-Wortlaut, `ui-ux-designer`-Domaene). |

**Empfehlung an den director:** `qa/findings.md` fuer QA-180, QA-183, QA-187
auf "behoben" nachziehen und die state.md-Entscheidung vom 07.09.
("A5 ist heute nicht erfuellt") anhand der obigen Messung neu bewerten. Ich
vergebe keine Status, das ist Ihre Zeile.

## Zahlen mit Rezept

- **Heldenabdeckung A3:** `grep -rohP` fallunabhaengig ueber
  `tests/test_advisor_*.py` und `tests/test_relic_picker_*.py` nach den zehn
  Heldennamen — 382 Treffer, davon Wylder 372, Duchess 10 (alle acht in
  `test_advisor_block.py`/`test_advisor_explain.py`, alle zur selben Zeile).
  Nenner: 10 Helden im echten Datensatz (`nightreign_data.json`, Feld
  `heroes`).
- **Picker-Rechenzeit A6:** `scripts/measure_advisor_picker.py`, unveraendert
  aus dem Repo, ausgefuehrt im eigenen Klon (Commit `06c4fe0`) gegen
  `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json` (309 Relikte),
  Wylder's Chalice, Stufe 15, Median von 3 Wiederholungen je Slot. Ergebnis
  siehe A6.
- **Fuellungsverteilung A5:** `scripts/measure_advisor_language.py`,
  unveraendert aus dem Repo, gleicher Klon und Spielstand, Wylder Stufe 15,
  `goals.DEFAULT_WEIGHTING`. 426 stumme Effektzeilen ueber 309 Relikte / 845
  Effektrollen. Ergebnis siehe A5.
- **Duchess-Gegenprobe A3:** eigenes Wegwerf-Skript
  `scripts/_qa095_duchess_probe.py` im Klon (nicht im Projekt-Repo),
  `Duchess' Urn`, Stufe 15, `Budget` = `types.DEFAULT_BUDGET`, ein Lauf je
  Slotart (normal/Deep), keine Wiederholung noetig, da nur auf
  Vollstaendigkeit und Farbkonsistenz geprueft wird, nicht auf eine Zeitzahl.

## Suite, geteilt

Ausgangsstand laut Auftrag: 1239 passed, 9 skipped.

- **Picker-Testdateien allein** (`tests/test_relic_picker_advisor.py`,
  `tests/test_relic_picker_geometry.py`): **48 passed in 121.33s.**
- **Rest der Suite** (`tests/` mit `--ignore` auf die beiden obigen Dateien):
  **1191 passed, 9 skipped in 654.93s (10:55 min).** Dieser Lauf ist zu lang
  fuer einen Vordergrundaufruf gelaufen und wurde automatisch in den
  Hintergrund verschoben; ich habe **nicht** darauf gewartet, sondern mit der
  Codepruefung fortgefahren und das Ergebnis erst beim Abschluss gelesen —
  kein Verstoss gegen "kein Hintergrundlauf, auf dessen Ende der Agent
  wartet", weil ich die Wartezeit fuer produktive Arbeit genutzt habe statt
  fuer einen Polling-Loop.
- **Summe: 1239 passed, 9 skipped** — exakt der im Auftrag genannte
  Ausgangsstand. Der Stand war waehrend meines gesamten Laufs eingefroren,
  keine Drift.

## Was mir sonst aufgefallen ist

- **Das Muster "Fix vor Statuszeile" betrifft mindestens drei Befunde in
  derselben Datei-Nachbarschaft (`explain.py`) am selben Tag.** Das ist mehr
  als ein Einzelfall und spricht dafuer, `qa/findings.md` als letzten Schritt
  jedes `fix`-Commits zu pflegen statt als eigene, spaeter nachgeholte
  Aufgabe — sonst liest der naechste Director-Blick auf die Datei
  systematisch zu pessimistisch.
- **Der Picker-Docstring nennt eine eigene Zahl (~51 ms), die ich mit einer
  anderen (67 ms) reproduziert habe** — beide im grünen Bereich, aber die
  Differenz zeigt, dass die zitierte Zahl selbst schon leicht veraltet ist
  (vermutlich vor T-093/T-094, die zusaetzliche Kartenfelder eingefuehrt
  haben). Kein eigener Befund, da beide Zahlen weit unter dem Budget liegen —
  aber ein Hinweis, dass eine feste Zahl in einem Docstring ohne Messdatum
  leise altert.
- **Die Duchess-Gegenprobe** war nicht Teil der neun bekannten Befunde,
  sondern meine eigene Reaktion auf die "mindestens zwei Nightfarer"-Vorgabe
  des Auftrags — sie gehoert eher unter "A3" als hierher, ist aber der
  einzige Codepfad, den ich in diesem Lauf **selbst durch den Berater
  geschickt** habe statt nur zu lesen.

## Nicht getestet

- **QA-182, QA-184, QA-186, QA-188** nicht erneut nachgemessen — Zeitbudget
  bewusst auf A3-A6 (die vom Auftrag als "am wenigsten bewacht" markierten
  Kriterien) und auf A5/QA-180 konzentriert, wie der Auftrag es priorisiert.
- **A9** (gebautes Artefakt) — es gibt keine EXE, wie der Auftrag selbst
  festhaelt; nicht mein Gegenstand.
- **A16, A17** — spezifiziert, nicht gebaut; ausdruecklich nicht mein
  Gegenstand.
- **Die tatsaechliche Fensterreaktion beim Oeffnen des Pickers** (Aufbau der
  ~205 Kartenwidgets) — ich habe nur die reine Zahlen-Rechnung gemessen, wie
  oben unter A6 genannt; ein echter End-to-End-Zeitstempel vom Klick bis zum
  ersten Frame fehlt.
- **SEC-021** und alles, was `security-reviewer` in T-096 parallel bearbeitet
  — nicht mein Gegenstand, kein Kontakt zu diesem Lauf noetig gewesen.
- **Determinismus ueber mehrere Prozessstarts** (Hash-Seed) — laut Grep gibt
  es Tests dafuer in `test_advisor_goals.py`/`test_advisor_search.py`; ich
  habe sie nicht einzeln nachvollzogen, da `search.py`s eigener Docstring die
  Regel bereits mit den historischen Faellen QA-059/QA-142 begruendet und ich
  keinen Hinweis auf eine Regression fand.

## QA-Log

`qa/findings.md` ist zu gross (1800+ Zeilen), um sie hier vollstaendig und
sicher zu reproduzieren — ich reiche keine Kopie ein, sondern die Delta, die
der `director` einpflegen kann:

| Zeile in qa/findings.md | Vorschlag |
|---|---|
| QA-180 | Status von "offen" auf "behoben" (Commit `90ff81d`, vor dem eingefrorenen Stand; zwei ID/Slot-basierte Regressionstests gruen) |
| QA-183 | Status von "offen — mit AK-145 zu beheben" auf "behoben" (Test in `test_advisor_explain.py` haelt die korrigierte Kongruenz fest) |
| QA-187 | Status von "offen" auf "behoben" (Commit `4462a88`; eigener Messlauf trifft die verlangte Verteilung 150/0/144/38/94/0 exakt) |

Alle anderen Zeilen (QA-181, QA-182, QA-184 bis QA-186, QA-188, QA-189,
SEC-021) unveraendert — nicht neu gemessen bzw. bestaetigt wie oben notiert.
Neue Befunde ohne ID (Vergabe liegt beim director):

- **Heldenabdeckung des Advisor-Testbestands.** Acht von zehn Helden kommen
  in keinem Advisor- oder Picker-Test vor; Duchess nur in einer isolierten
  Textzeile. Adressat: developer (Testbestand), Fundstelle: grep-Zahlen oben,
  A3.
- **Keine Regressionsschranke fuer die Picker-Rechenzeit.** `~51/67 ms` ist
  eine Skriptmessung, kein Testwaechter. Adressat: developer/
  performance-tuner (S11), Fundstelle: `nrplanner/relicpicker.py`,
  `SlotAdvice.ranking`-Docstring, A6.
