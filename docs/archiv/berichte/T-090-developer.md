# T-090 - Die Fuellungsreihenfolge im Rechenkern nachziehen (QA-187) (developer)

```
STATUS: erledigt
AUFTRAG: T-090 - Die Fuellungsreihenfolge im Rechenkern nachziehen (QA-187)
GELESEN: docs/tasks/T-090.md (vollstaendig); UI_SPEC.md AK-167/168/169 (Z.
  4553-4571) und der T-086-Nachtrag AK-177 bis AK-181 (Z. 4745-5100,
  einschliesslich §0 Messumgebung und §1.1 der Befundtabelle);
  nrplanner/advisor/explain.py (_ARMAMENT_GATES, _silent_effect, reasons,
  not_counted); nrplanner/model.py (WEAPON_TYPE_GATES, satisfied_by_weapon,
  is_conditional, CONDITIONAL_FIELDS, GATE_FIELDS, compute - nur gelesen);
  nrplanner/advisor/evaluate.py (_effects, evaluate);
  nrplanner/advisor/types.py (GoalContext, die SILENT_*-Marken);
  nrplanner/effecttext.py (Z. 278-305, die zweite Lesart von
  wepTypeTriggerCount); scripts/measure_advisor_language.py;
  tests/test_advisor_explain.py, tests/advisor_cases.py, tests/conftest.py
  (game_data); ARCHITECTURE.md Z. 3520-3535 und 3737-3750; qa/findings.md
  QA-186/QA-187.
GEAENDERT: nrplanner/advisor/explain.py, tests/test_advisor_explain.py,
  scripts/measure_advisor_language.py - alle drei committet (58b3459,
  4462a88). Keine fremde Datei angefasst; docs/tasks/T-090.md bleibt
  uncommittet, sie gehoert dem Director.
ANNAHMEN: (1) Fuellung (e) bleibt der erste Test in `_silent_effect`, obwohl
  AK-167 sie zuletzt aufzaehlt - ohne Namen laesst sich keine der anderen
  fuenf Fragen stellen, und `ctx.data["effects"][str(effect_id)]` wuerde
  vorher werfen. Sie bewegt in beiden Umgebungen 0 Zeilen, die Verteilung
  haengt also nicht daran. (2) `explain._ARMAMENT_GATES` ist in zwei Tupel
  zerlegt worden (siehe "An director", Punkt 1); der Auftrag nennt den alten
  Namen, verlangt aber die Regel, die er nicht mehr abbildet.
NAECHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

## Umgesetzt

Alles in `nrplanner/advisor/explain.py`, Abschnitt *"the effects that moved
nothing, and why"*:

- **`_silent_effect` prueft jetzt (a) → (a2) → (c) → (b) → (d)** (AK-167). Die
  zwei Bloecke sind vertauscht, sonst nichts. (e) steht unveraendert vorn,
  siehe Annahme 1.
- **`_armament_bound(effect, armaments)`** ist neu und entscheidet Fuellung
  (c) nach AK-177: entweder eine Schranke aus `model.WEAPON_TYPE_GATES`, fuer
  die `model.satisfied_by_weapon` gegen die gefuehrten Waffentypen falsch ist
  **und** deren verlangter Wert im `wep_type`-Vorrat des Abzugs steht
  (AK-179), oder ein Feld aus `_GATES_THE_NAME_ANSWERS` (`startSwordArtsId`).
- **`_Armaments` und `_armaments(ctx)`** sind neu: die gefuehrten Waffentypen
  (mit demselben Rueckfall auf die Bezugsarmatur, den `model.compute`
  benutzt) und der Waffentyp-Vorrat des Abzugs, **einmal je `reasons`-Lauf**
  gebildet statt einmal je Zeile - der Vorrat ist ein Durchlauf ueber 1793
  Waffen.
- **`_ARMAMENT_GATES` ist ersetzt** durch `_GATES_THE_NAME_ANSWERS`
  (`startSwordArtsId`) und `_GATES_WITH_A_WEAPON_TYPE`
  (`= model.WEAPON_TYPE_GATES`). `wepTypeTriggerCount` steht in keinem von
  beiden (AK-178).
- Die Docstrings von `_silent_effect` und der beiden Tupel tragen die Regel,
  ihren Grund und die AK-180-Zahlen mit der Lesart "Fuellung, nicht Liste"
  (AK-181).

**Kein Wortlaut ist angefasst.** Die sechs Saetze stehen Buchstabe fuer
Buchstabe wie vorher; nachgewiesen dadurch, dass die Zeilentexte der
bestehenden Faelle unveraendert gruen sind und die beiden Messlaeufe
dieselben Saetze in anderer Verteilung ausgeben.

**`model.py` und AD-026 sind nicht angefasst.** `git status` zeigt
`nrplanner/model.py` unveraendert; `satisfied_by_weapon` und
`data["weapons"]` werden nur gelesen.

`scripts/measure_advisor_language.py`: der Nightfarer ist ein Argument
geworden (Gefaess folgt ihm), und die Liste 4.9b wird neben den Fuellungen
gezaehlt. Begruendung im Commit 58b3459 - ohne das haette Umgebung B ein
zweites Messmittel gebraucht, und der Auftrag verbietet genau das.

## Die Verteilung, beide Umgebungen, vorher und nachher

Rezept (L-001): erschoepfende Auszaehlung, keine Stichprobe, also kein
Stichprobenfehler und kein Sicherheitsabstand. Je besessener Kopie ein
Einzelslot-Problem, `explain.reasons` selbst, gezaehlt werden die
`ReasonLine`, die weder `is_curse` noch `CARRIES_A_FIGURE` sind, nach ihrer
`silence`-Marke. Werkzeug `scripts/measure_advisor_language.py`.
Umgebung: `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`,
`data_version` 10350000, 2076 Effekte, 1793 Waffen, Spielstand mit **309**
Kopien und **845** Effektrollen, Stufe 15, keine Bedingung erklaert,
`DEFAULT_WEIGHTING`, Zielrichtung `max_damage`. Nur gelesen, nichts
geschrieben.

**Umgebung A - Wylder, `Wylder's Greatsword` (`wep_type` 5), Stufe 15**

| Fuellung | vorher | nachher | AK-180 |
|---|---|---|---|
| (a) anderer Nightfarer | 150 | **150** | 150 |
| (a2) anderswo gezaehlt | 0 | **0** | 0 |
| (b) Bedingung | 170 | **144** | 144 |
| (c) Armaturen | 13 | **38** | 38 |
| (d) Rest | 93 | **94** | 94 |
| (e) nicht im Datensatz | 0 | **0** | 0 |
| Summe | 426 | **426** | 426 |

**Umgebung B - Ironeye, `Ironeye's Bow` (`wep_type` 51), Stufe 15**

| Fuellung | vorher | nachher | AK-180 |
|---|---|---|---|
| (a) anderer Nightfarer | 159 | **159** | 159 |
| (a2) anderswo gezaehlt | 0 | **0** | 0 |
| (b) Bedingung | 174 | **149** | 149 |
| (c) Armaturen | 0 | **25** | 25 |
| (d) Rest | 101 | **101** | 101 |
| (e) nicht im Datensatz | 0 | **0** | 0 |
| Summe | 434 | **434** | 434 |

Beide treffen exakt.

**Wie die "vorher"-Spalten entstanden sind, damit sie nachpruefbar sind:**
`nrplanner/`, `nrdata/` und `scripts/` in ein Scratchpad kopiert und dort
`nrplanner/advisor/explain.py` durch `git show HEAD:...` (HEAD = `5253888`,
also der Stand vor diesem Auftrag) ersetzt - **das neue** Messskript gegen
**den alten** Rechenkern. Nur so sind Vorher und Nachher mit demselben
Messmittel gezaehlt. Die Zahlen der A-Spalte stimmen mit der Quittung aus
T-089 ueberein; die B-Spalte ist hier zum ersten Mal gemessen worden.

Die 20 bzw. 22 Zeilen, um die es dem Nutzer geht, sind darin enthalten:
in A gehen 26 Zeilen von (b) nach (c) (18 nur `triggerOnWepType`, 8
`wepTypeTrigger`+`Count`) und 20 `wepTypeTriggerCount`-Zeilen bleiben, wo sie
hingehoeren; eine Zeile faellt aus (c) nach (d) (13 → 12 `startSwordArtsId`
plus 26). Das deckt sich Posten fuer Posten mit der Tabelle in
`UI_SPEC.md` §1.1 des T-086-Nachtrags.

## Die Zahl aus 4.9b - vorher und nachher

Der Auftrag verlangt, dass sie sich nicht aendert. Sie tut es nicht,
**gemessen, nicht geschlossen** - in beiden Lesarten:

| Lesart | A vorher | A nachher | B vorher | B nachher |
|---|---|---|---|---|
| `len(explain.not_counted(built))`, ueber alle 309 Laeufe summiert | 197 | **197** | 201 | **201** |
| stumme Zeilen, deren Effekt in `Build.situational` mit `live == False` steht (die Zahl, die `UI_SPEC` §6 nennt) | 170 | **170** | 174 | **174** |

Die zweite Zeile ist die, die AK-181 mit 170 (A) und 174 (B) benennt; sie ist
mit demselben `every_relic`-Durchlauf gezaehlt worden.

## Die drei Gegenbauten, einzeln gefahren

Jeder wurde einzeln angewandt, gefahren und danach aus einer Sicherung
zurueckgesetzt; nie zwei zugleich. Alle drei werden im **Standardlauf** rot
(`-m "not slow"`, keine Marke, kein Skip) - L-008 (a).

**1 - Reihenfolge zurueck auf (b) vor (c).** Die zwei Bloecke in
`_silent_effect` vertauscht.
→ **3 Faelle rot**, davon der Verteilungsfall mit
`{'under_a_condition': 5, 'armament_bound': 1}` statt `{3, 3}`:

```
FAILED tests/test_advisor_explain.py::test_an_effect_that_fits_two_fillings_takes_the_earlier_one
FAILED tests/test_advisor_explain.py::test_a_gate_on_a_weapon_type_no_armament_has_is_not_an_armament_case
FAILED tests/test_advisor_explain.py::test_every_silent_line_lands_in_the_filling_ak_180_gives_it
3 failed, 48 passed
```

Das ist im Kleinen genau die Form des Befundes: die Summe der stummen Zeilen
bleibt 10, nur die Verteilung kippt.

**2 - Die Wertevorrat-Bedingung aus AK-179 entfernt.**
`and wanted in armaments.in_the_data` gestrichen.
→ **2 Faelle rot**, Verteilung `{'under_a_condition': 2, 'armament_bound': 4}`
statt `{3, 3}`:

```
FAILED tests/test_advisor_explain.py::test_a_gate_on_a_weapon_type_no_armament_has_is_not_an_armament_case
FAILED tests/test_advisor_explain.py::test_every_silent_line_lands_in_the_filling_ak_180_gives_it
2 failed, 49 passed
```

Der Fall dafuer ist **konstruiert**, wie der Auftrag es verlangt: derselbe
Effekt (`Improved Greatsword Attack Power`) einmal mit seinem echten
Waffentyp und einmal mit `triggerOnWepType = 256`, sonst Feld fuer Feld
gleich. Auf dem Spielstand bewegt AK-179 null Zeilen, der Waechter waere ohne
diese Konstruktion unbewacht (L-002: Gegenbau als Nachweisweg).

**3 - `wepTypeTriggerCount` wieder als (c)-Ausloeser.** Ein Eintrag in
`_GATES_THE_NAME_ANSWERS` dazu.
→ **3 Faelle rot**:

```
FAILED tests/test_advisor_explain.py::test_the_armament_gates_are_the_ones_the_model_names_bar_the_counting_one
FAILED tests/test_advisor_explain.py::test_a_gate_on_how_many_are_equipped_never_mentions_the_armaments
FAILED tests/test_advisor_explain.py::test_every_silent_line_lands_in_the_filling_ak_180_gives_it
```

und der zweite davon zitiert woertlich die Zeile, die AK-178 als Rot-vorher
nennt:

```
At index 0 diff:
'Stonesword Key in possession at start of expedition: it depends on the armaments you carry, so no number here.'
!=
'Stonesword Key in possession at start of expedition: only applies under a condition, so no number here.'
```

*(Ehrlichkeitshalber: beim ersten Lauf dieses Gegenbaus fiel der Fall an
`Crimsonspill Crystal Tear ...`, weil die Schleife den nach Id kleinsten
Effekt der Familie zuerst nahm. Der Fall ist danach so umgestellt worden,
dass der **namentlich** genannte Effekt zuerst geprueft wird - nicht um gruen
zu werden, sondern damit das Rot die Zeile zitiert, ueber die die Vorgabe
spricht. Danach erneut gefahren, Ausgabe oben.)*

**Kein Gegenbau ist gruen geblieben.**

## Tests

**Neu (3 Faelle):**

- `test_every_silent_line_lands_in_the_filling_ak_180_gives_it` - der
  Verteilungsfall. Ein Korpus von 10 Effektrollen auf zwei Kopien, dessen
  Soll-Verteilung **1 / 1 / 3 / 3 / 1 / 1** lautet ((a)/(a2)/(c)/(b)/(d)/(e)),
  als Ganzes gegen die tatsaechliche gehalten. Die Summe wird **zusaetzlich**
  geprueft, nie **statt** dessen - das ist die Falle, die der Auftrag nennt.
- `test_a_gate_on_a_weapon_type_no_armament_has_is_not_an_armament_case` -
  AK-179, ein Effekt gegen zwei Datenabzuege, die sich in genau einem
  Feldwert unterscheiden.
- `test_a_gate_on_how_many_are_equipped_never_mentions_the_armaments` -
  AK-178, an `Stonesword Key in possession at start of expedition` und an
  einem zweiten Effekt derselben Familie; prueft ausserdem, dass die
  Zeichenfolge `armaments you carry` nirgends in der Zeile steht.

**Geaendert (2 Faelle):**

- `test_an_effect_that_fits_two_fillings_takes_the_earlier_one` - derselbe
  Fall, andere Erwartung: die fruehere Fuellung ist seit AK-167 (c), nicht
  (b). Der Hilfsgriff sucht den Effekt jetzt ueber den Waffentyp-Vorrat und
  die Armatur in der Hand statt ueber die vier Feldnamen.
- `test_the_armament_gates_are_the_ones_the_model_names` →
  `..._bar_the_counting_one`. Haelt die Vereinigung der beiden Tupel gegen
  `model.GATE_FIELDS` und nennt die eine gewollte Abweichung. Der Fall prueft
  zusaetzlich, dass `wepTypeTriggerCount` im Modell ueberhaupt noch als
  Armaturenschranke steht - sonst wuerde er nichts mehr bewachen und trotzdem
  gruen sein (L-008 b).

**Woran die Erwartungen haengen (L-008 b).** Kein Korpuseintrag ist ueber
`explain` ausgewaehlt. Die Auswahl fragt `data["weapons"]` (Waffentyp-Vorrat),
die Armatur in der Hand, `effecttext.owner`/`works_for` und `model.compute`
(`sources`/`situational`). Jeder Eintrag ist zusaetzlich daraufhin geprueft,
dass er ueberhaupt **stumm** ist - sonst waere der Korpus um eine Zeile
kuerzer, aus einem Grund, der mit den Fuellungen nichts zu tun hat.

**Was ich bewusst nicht getestet habe:** die Zahlen 426/434 selbst. Sie
zaehlen den Spielstand des App Designers; ein frischer Klon hat ihn nicht,
und ein Fall, der ohne ihn uebersprungen wird, bewacht nichts (L-008 a). Die
Eigenschaft dahinter steht im Verteilungsfall, die Zahlen stehen in diesem
Bericht mit ihrem Rezept.

**Suite** (`.venv\Scripts\python.exe -m pytest -m "not slow"`, Windows 10,
Python 3.12.10, PySide6, `QT_QPA_PLATFORM=offscreen` aus `conftest.py`):

- vorher, laut Auftrag: **1143 passed, 9 skipped, 5 deselected**
- nachher, dieser Lauf: **1146 passed, 9 skipped, 5 deselected in 532.52s**

Die drei zusaetzlichen sind die drei neuen Faelle. **Achtung fuer die
Reproduktion:** dieser Lauf ist aus dem Arbeitsbaum, nicht aus einem frischen
Klon. Ein Klonlauf steht aus; er ist ueblicherweise Sache der Abnahme.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (zwei, oben)
- [x] Build & Tests gruen in der benannten Testumgebung
- [x] Neue Tests fuer neue Logik; jeder der drei Waechter hat einen
      toetenden Gegenbau
- [ ] Linter - **entfaellt**: das Projekt hat keinen konfiguriert
      (kein `.flake8`, `setup.cfg`, `tox.ini`, `pyproject.toml`, keine
      ruff-/pylint-Konfiguration im Wurzelverzeichnis; `pytest.ini` ist die
      einzige Werkzeugkonfiguration)
- [x] Keine Secrets, keine TODOs, kein toter Code. Beide neuen Tupel werden
      in `_armament_bound` benutzt; kein auskommentierter Rest.
- [x] Abnahmekriterien selbst durchgespielt (beide Umgebungen, 4.9b in zwei
      Lesarten, drei Gegenbauten einzeln)
- [ ] Doku: **nicht durch mich.** `UI_SPEC.md`, `ARCHITECTURE.md`,
      `docs/state.md` und `qa/findings.md` gehoeren anderen Rollen; die
      Stellen, die nachzuziehen sind, stehen unten.

**Ungeprueft:** Linux und macOS - dort ist nichts gelaufen. Das Geaenderte ist
Qt-frei und plattformunabhaengig, aber gelaufen ist es nur unter Windows 10.
Ebenso ungeprueft: das Fenster. Ich habe kein Programm gestartet und keinen
Bildnachweis gezogen (NH-002); dass die Slotkarte die neue Fuellung richtig
faerbt, ist damit **nicht** belegt - nur, dass `test_advisor_block.py` und
`test_advisor_bar.py` unveraendert gruen sind.

## Suche nach demselben Muster im ganzen Projekt (L-006)

Nicht nur die im Befund genannte Stelle, sondern das Muster - vier unabhaengig
formulierte Masken ueber `*.py` und `*.md`, `__pycache__` ausgenommen:

| Maske | Treffer | in Produktivcode |
|---|---|---|
| `wepTypeTriggerCount` | 63 | `explain.py` (1, meiner), `effecttext.py` (3), `model.py` (3) |
| `armaments you carry` | 33 | `explain.py` (2, meine) |
| `startSwordArtsId` | 24 | `explain.py` (1, meiner), `effecttext.py` (1), `model.py` (2) |
| `_ARMAMENT_GATES` | 20 | **0** (nach diesem Auftrag; siehe unten) |

**Ergebnis: keine zweite Stelle im Produktivcode, die dieselbe zu weite
Regel baut.** Die drei `effecttext.py`-Treffer sind eine **andere** Regel und
sie ist bereits richtig: `effecttext.py` Z. 287-298 laesst
`wepTypeTriggerCount` fuer die eigene Beschriftung genau dann weg, wenn kein
`wepTypeTrigger` daneben steht - dieselbe Unterscheidung wie AK-178, nur ueber
das Geschwisterfeld statt ueber den Wert. Die `model.py`-Treffer sind
`CONDITIONAL_FIELDS`, `GATE_FIELDS` und der Kommentar an
`WEAPON_TYPE_GATES`; sie gehoeren zu QA-186 und sind Scope-Grenze dieses
Auftrags.

## An qa-engineer

**Was zu pruefen ist**, und zwar am Fenster, denn ich habe keines gestartet:

1. **Der `Why`-Dialog auf dem echten Spielstand.** 26 Zeilen (Wylder) bzw. 25
   (Ironeye) sagen jetzt `it depends on the armaments you carry`, wo vorher
   `only applies under a condition` stand, und 20 bzw. 22 Zeilen umgekehrt.
   Beides ist Nutzertext an derselben Stelle. Ein Relikt, an dem es sichtbar
   wird: jedes mit einem `Improved <Waffe> Attack Power`-Effekt, dessen Waffe
   der Spieler nicht traegt.
2. **Die Faerbung der Slotkarte.** Der Auftrag sagt, die Anzeige nehme die
   Fuellung nur entgegen; ich habe das nicht am Fenster nachgesehen. Wenn
   `advisorblock`/`advisorbar` je Fuellung anders faerbt oder zaehlt, aendert
   sich das Bild ohne dass eine Zeile Anzeigecode angefasst wurde.
3. **Gegenstandseffekte.** `Stonesword Key in possession at start of
   expedition` und die 50 Geschwister mit `startGoodsId` duerfen nirgends
   mehr nach einem Waffenwechsel klingen. Das ist der Fall, der dem Nutzer
   aufgefallen ist.
4. **Randfall, den ich nicht am Bestand pruefen konnte:** ein Effekt, dessen
   Waffentyp-Schranke die Armatur **erfuellt**. Er darf weder (b) noch (c)
   bekommen, sondern muss zaehlen oder auf (d) fallen. Auf diesem Spielstand
   ist mir kein Relikt bekannt, das ihn zeigt; im Test ist er ueber
   `test_an_effect_bound_to_the_armaments...` und den Vergleichsfall gedeckt.
5. **Zweiter Nightfarer.** Ironeye hat **0** `startSwordArtsId`-Zeilen und
   Wylder 12; die Fuellung (c) ist damit stark heldenabhaengig. Ein Test nur
   an Wylder uebersieht die Haelfte.

## An ui-ux-designer

Keine Abweichung. Die sechs Wortlaute stehen unveraendert; dieser Auftrag hat
ausschliesslich verschoben, welche Zeile welchen bekommt. Die Zahlen aus
AK-180 sind in beiden Umgebungen exakt getroffen, und die 170/174 aus
`UI_SPEC` §6 sind unveraendert - beides oben mit Rezept.

## An director

1. **`explain._ARMAMENT_GATES` gibt es nicht mehr, und das macht vier
   Fundstellen in fremden Dateien schief.** Die Regel nach AK-177/178
   beantwortet die vier Felder nicht mehr gleich: `startSwordArtsId` ist mit
   seiner blossen Anwesenheit beantwortet, die zwei Waffentyp-Felder ueber
   `satisfied_by_weapon` und den Wertevorrat, `wepTypeTriggerCount` gar
   nicht. Ein Tupel, das alle vier fuehrt, waere nach diesem Auftrag entweder
   eine Luege oder toter Code - beides verboten. Es steht jetzt als
   `_GATES_THE_NAME_ANSWERS` und `_GATES_WITH_A_WEAPON_TYPE` da.
   Nachzuziehen ist der alte Name in: `ARCHITECTURE.md` Z. 3528, 3737, 3750
   (`architect`), `UI_SPEC.md` Z. 4319, 4749, 5004 (`ui-ux-designer`, wobei
   Z. 5004 das Rot-vorher von AK-177 beschreibt und historisch richtig
   bleibt), und `.claude/agent-memory/ui-ux-designer/feedback_field_names_lie.md`
   Z. 29. Ich habe keine davon angefasst.
2. **Die Messumgebung §0 des T-086-Nachtrags nennt Codestand `fd9f2bc`.**
   Ab diesem Commit ist `explain.py` ein anderer; die Zahlen der Vorgabe sind
   damit **Soll**-Zahlen, nicht mehr Ist-Zahlen desselben Standes. Wer sie
   spaeter nachmisst, misst gegen `4462a88`.
3. **Eine dritte Zahl ueber die stummen Zeilen, die `UI_SPEC` nicht kennt.**
   `len(explain.not_counted(built))` ueber denselben Bestand ergibt **197**
   (A) und **201** (B) - nicht 170/174. Der Unterschied ist echt und harmlos:
   `not_counted` zaehlt jeden `situational`-Eintrag mit `live == False`, auch
   wo derselbe Effekt zugleich eine Zahl bewegt hat (AD-026 laesst das
   ausdruecklich zu), waehrend 170/174 nur **stumme Zeilen** zaehlt. AK-181
   verlangt, dass jede Zahl ueber die stummen Zeilen ihre Lesart nennt; diese
   dritte kommt in der Datei nicht vor. Falls die Liste 4.9b je mit einer
   Zahl beschriftet werden soll, ist 197/201 die, die der Spieler sieht -
   nicht 170/174. **Kein Befund, eine Vorwarnung.**
4. **Bestehende Debt, nicht angefasst:** QA-186 (`model.GATE_FIELDS`
   beschriftet 51 Gegenstandseffekte als Waffenanzahl) ist dieselbe
   Fehlerfamilie in einem anderen Modul und steht auf dem Build planner, den
   der Nutzer schon fuer gut befunden hat. Meine Aenderung repariert die
   Beraterzeile und **nicht** die Beschriftung im Planer - ein Spieler sieht
   ab jetzt beide Lesarten nebeneinander: die Beraterzeile sagt
   `only applies under a condition`, die Zeile unter `Conditional &
   situational` sagt weiter `needs several of that weapon equipped`. Ort:
   `nrplanner/model.py` `GATE_FIELDS`, Schluessel `wepTypeTriggerCount` und
   `triggerOnWepType`. Risiko: A7-Bruch, sichtbar, unveraendert. Aufwand:
   klein, wenn die Unterscheidung von `explain._armament_bound` uebernommen
   wird - aber es ist `model.py` und damit ausdruecklich nicht mein Scope.
5. **Performance:** `_armaments(ctx)` bildet den Waffentyp-Vorrat mit einem
   Durchlauf ueber 1793 Waffen. Ich habe ihn aus `_silent_effect` nach
   `reasons` gehoben, damit er einmal je Lauf statt einmal je Zeile faellt;
   ein voller Suchlauf ruft `reasons` aber je Vorschlag auf. Der Messlauf
   ueber 309 Relikte plus 40 Vorschlaege ist dadurch nicht spuerbar langsamer
   geworden, und die Suite ist mit 532 s im gewohnten Rahmen. **Keine
   Empfehlung an den `performance-tuner`** - ich nenne es, weil ich die
   Stelle angefasst habe, nicht weil sie auffaellig waere.
6. **Sicherheit:** nichts gefunden. Kein Netzwerkzugriff, kein Schreibzugriff
   auf den Datenabzug, keine Secrets, kein neuer externer Input. Die
   konstruierten Datensaetze der Tests sind flache Kopien im Speicher und
   beruehren keine Datei.
7. **Keine neue Abhaengigkeit.** Nichts eingebunden, auch nichts
   "offensichtliches".
8. **Zwei Dateien bleiben absichtlich uncommittet:** `nrplanner/advisorbar.py`
   und `tests/test_advisor_bar.py` zeigen sich in `git status` als geaendert
   bei leerem `git diff` - Zeilenende-Rauschen, wie der Auftrag es
   ankuendigt. `git diff --stat` auf beide gibt nichts aus. Ich habe sie
   nicht angefasst und in keinen Commit genommen.

## Commits

| Commit | Was |
|---|---|
| `58b3459` | `feat(scripts): miss die Fuellungen in beiden Umgebungen und die Liste 4.9b` - `scripts/measure_advisor_language.py` |
| `4462a88` | `fix(advisor): (c) vor (b), und (c) fragt, was die Rechnung beantwortet hat` - `nrplanner/advisor/explain.py`, `tests/test_advisor_explain.py` |

Beide mit Pfadangabe hinter `--` committet, kein `-a`, kein `add .`. Kein
`push`, kein `pull`, kein `checkout`, kein `stash`, kein `branch` - die
Gegenbauten sind ueber eine Dateisicherung im Scratchpad zurueckgesetzt
worden, nicht ueber git.

## Was mir aufgefallen ist und nicht in den Auftrag gehoerte

- **Der Verteilungsfall haette leicht ein Waechter ohne Zaehne werden
  koennen.** Mein erster Entwurf hat die Korpuseintraege ueber dieselbe
  Bedingung ausgewaehlt, die er bewacht - dann waere er unter jedem der drei
  Gegenbauten gruen geblieben. Die Auswahl fragt jetzt den Datenabzug und
  `model.compute`. Das ist derselbe Fehler, den L-008 (b) beschreibt, und er
  ist mir hier zum zweiten Mal begegnet.
- **`_silent_effect` hatte in seinem Docstring eine Zahl ohne Lesart** -
  *"150 of the first and 170 of the second among 426 silent effects"*. Genau
  die Verwechslung, gegen die AK-181 geschrieben ist, und sie stand im Code,
  nicht in der Spec. Sie ist mit der Aenderung ersetzt und nennt jetzt beide
  Lesarten.
- **`scripts/measure_advisor_language.py` misst nur Wylder gewesen**, und die
  Vorgabe steht seit T-086 in zwei Umgebungen. Das Werkzeug war der Vorgabe
  einen Schritt hinterher - so wie der Rechenkern es war. Es ist jetzt
  nachgezogen; ob weitere Werkzeuge unter `scripts/` dieselbe Luecke haben,
  habe ich nicht geprueft.
