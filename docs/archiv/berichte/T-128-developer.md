# T-128 - U5a: die Qt-freie Seite der Picker-Spur (developer)

```
STATUS: erledigt
AUFTRAG: T-128 - U5a: die Qt-freie Seite der Picker-Spur
GELESEN: docs/tasks/T-128.md; ARCHITECTURE.md AD-028 (3985-4200), Umsetzungs-
  und Risikotabelle (4380-4460), Nachtrag IX ganz (4461-4960); nrplanner/
  advisor/{run,candidates,types,goals,worker,__init__}.py; nrplanner/
  relicpicker.py:270-340; nrplanner/advisorbar.py:273-295; tests/
  advisor_cases.py; tests/test_advisor_run.py; tests/test_one_build.py;
  tests/test_differential_track.py:478-495; scripts/differential/mutate.py
  (Eintrag advisor-run-takes-a-request-about-another-run)
GEAENDERT: nrplanner/advisor/run.py; nrplanner/advisor/goals.py;
  tests/test_advisor_slot_pool.py (neu); scripts/differential/mutate.py;
  docs/berichte/T-128-developer.md (liegt uncommittet auf der Platte -- die
  Berichte committet in diesem Repo der Director). Zwei Commits: 2be58f5
  (feat), 4b55334 (test). Nichts anderes gestaged oder committet -- UI_SPEC.md und
  docs/state.md sind im Arbeitsbaum veraendert, gehoeren aber T-127 bzw. dem
  Director und wurden nicht angefasst.
ANNAHMEN: siehe Abschnitt "Annahmen" -- drei, alle im Auftrag gedeckt.
NAECHSTER: director (dann U5b, derselbe developer-Auftrag oder ein neuer)
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**1. `run.slot_pool` (`nrplanner/advisor/run.py`, neuer Abschnitt
"the picker's question" am Dateiende).** Die zweite Antwortfunktion des
Moduls, in der **Argumentform von `run.run`** (`request, inventory, ctx,
goals, should_cancel`), damit dieselbe `AdvisorController`-Klasse beide
Spuren tragen kann (AD-028, Option D). Sie

- lehnt eine Anfrage ab, die das Material neben ihr nicht beschreibt --
  derselbe Aufruf von `_refuse_a_request_that_asks_about_another_run`, den
  `run` fuehrt, weil die Antwort unter dieser Anfrage im Cache landet;
- liest die kanonische Form: `types.free_slots(request.problem)` muss **genau
  einen** Slot liefern; sonst `ValueError` mit Slotzahl und den freien
  Indizes;
- nimmt `rank_by` aus `request.goal_id` und gibt `candidates.pool(...)`
  unveraendert zurueck, `should_cancel` durchgereicht.

Kein Import der Registry (AD-004 bleibt), keine Erklaerungen, kein zweiter
Rechenweg. Der Modul-Docstring hat einen Absatz "Two answers, one shape"
bekommen.

**2. `goals.CANONICAL_POOL_ORDER` (`nrplanner/advisor/goals.py`, unter
`GOALS`).** Die benannte Ordnungskonstante aus IX-2.1, als
`CANONICAL_POOL_ORDER = MAX_DAMAGE.id`. Der `#:`-Block darueber (die Form,
in der dieses Repo Konstanten dokumentiert -- `CACHE_SIZE`,
`DEFAULT_BUDGET`) sagt in drei Absaetzen: der Inhalt eines Pools haengt
nicht an der Richtung, sein Cache-Schluessel aber schon; was die Anzeige
ordnet, kommt aus der einen Einstellung (AK-43, AK-205) und nie aus
`SlotPool.rank_by`; der Wert ist die Id des Schadensziels, die **Festigkeit**
ist der Punkt.

**Warum in `goals.py` und nicht in `run.py`:** so ist die Konstante per
Konstruktion ein Schluessel von `GOALS` -- eine kanonische Richtung, die kein
Ziel beantwortet, wuerde jeden Picker-Lauf mit `KeyError` abweisen. In
`run.py` waere sie ein zweites Mal hingeschriebenes `"max_damage"` gewesen,
und `run.py` importiert die Registry bewusst nicht (AD-004). Falls der
`architect` sie lieber an der Picker-Spur selbst haette: ein Verschieben ist
eine Zeile.

**3. `tests/test_advisor_slot_pool.py` (neu, 11 Faelle).** Inhalt siehe
"Tests".

**4. `scripts/differential/mutate.py` -- eine erzwungene Nachfuehrung,
ausserhalb der im Auftrag genannten Dateien.** Der Anker der Mutation
`advisor-run-takes-a-request-about-another-run` war die Zeile
`_refuse_a_request_that_asks_about_another_run(request, inventory, ctx)`, und
die steht seit `slot_pool` **zweimal** in `run.py`;
`test_every_mutation_still_finds_its_anchor_in_the_real_source` fiel darauf
(`assert 2 == 1`). Der Anker nimmt jetzt die Folgezeile aus `run`
(`if request.goal_id not in goals:`) mit und ist damit wieder eindeutig --
enger, nicht loser, wie die Fehlermeldung des Waechters es verlangt. Die
Wirkung der Mutation ist unveraendert. **Nachgeprueft durch den echten
Treiber**, nicht behauptet: `mutate.py --apply
advisor-run-takes-a-request-about-another-run --tree <scratch>` schreibt
(`run.py:372 rewritten (-76 bytes)`), und
`test_advisor_run.py::test_a_request_that_describes_another_run_is_refused`
faellt dort in **allen sieben** Feldern.

## Annahmen

1. **Die kanonische Form ist die aus AD-028.3 und IX-5.1:** jeder Slot ausser
   dem offenen ist gehalten, mit seinem heutigen Inhalt, leere eingeschlossen
   (`advisorbar.held_slot` haelt einen leeren Slot als `HeldSlot(relic=None)`).
   Der offene Slot ist **nicht** in `held` -- er ist der einzige freie.
2. **Die Konstante ist eine Ordnung, kein Vorschlag an die Anzeige.**
   `slot_pool` erzwingt sie nicht; der Aufrufer entscheidet, was er fragt.
   Das ist Absicht: die Funktion rechnet unter jeder Richtung dasselbe, und
   ein Zwang hier waere eine zweite Stelle, an der die Wahl des Spielers
   verschwindet. Wer die Konstante setzt, ist das Fenster -- **U5b**.
3. **Kein Programmstart, keine Messung.** Alles laeuft in der Suite. Die drei
   Datenverzeichnis-Umlenkungen waren deshalb nicht noetig und wurden nicht
   vorgenommen; `pytest` legt seinen Einstellungsspeicher ohnehin unter die
   Prozess-Id (`tests/conftest.py`). Der Spielstand wurde nicht gelesen und
   nicht geschrieben.

## Der Gleichheitsbeleg (Vorgabe 3, und das Risiko aus `ARCHITECTURE.md:4400`)

**Ergebnis: die kanonische Form liefert denselben `SlotPool`. Die Revision von
AD-018 ist nicht noetig.**

Verglichen wird in `test_the_canonical_form_answers_the_pool_the_picker_
computes_today` (parametriert ueber beide Richtungen, in jedem Lauf ueber
alle fuenf Oeffnungen):

- **vorher** = die Gestalt, die `relicpicker.py:311-328` heute rechnet: jeder
  Slot gehalten, der offene per Index an `candidates.pool` uebergeben. Im
  Test nachgeschrieben statt aufgerufen, weil `relicpicker` Qt ist;
- **nachher** = `run.slot_pool` auf einer Anfrage, deren `problem` genau den
  offenen Slot frei laesst.

Gemessen (Skript im Scratchpad, Ausgabe unten; dieselben Faelle laufen als
Zusicherungen in der Suite):

| Vessel | offener Slot | Kandidaten | Handles gleich | Punktzahlen gleich | ganzer SlotPool gleich |
|---|---|---|---|---|---|
| drei gewoehnliche Slots (rot, rot, weiss) | 0 | 4 | ja | ja | ja |
| " | 1 | 3 | ja | ja | ja |
| " | 2 (weiss) | 5 | ja | ja | ja |
| zwei Deep-Slots (rot, weiss) | 0 | 3 | ja | ja | ja |
| " | 1 (weiss) | 2 | ja | ja | ja |

Je Zeile zweimal, einmal pro Richtung: **10 Vergleiche, 34 Kandidatenzeilen,
68 Handle/Richtungs-Punktzahlen**, dazu `baseline`, `unknowns`, `rank_by` und
`slot_index` ueber die Gleichheit der ganzen Datenklasse. Keine Abweichung.

**Woher die Faelle stammen:** gebaut, nicht gelesen -- `tests/advisor_cases.py`
baut Inventar, Vessel und Kontext aus dem **echten Datensatz** (Relikt-
Vorlagen und Effekte kommen aus `game_data`, welcher Effekt wirklich etwas
bewegt wird `model.compute` gefragt). Das ist die Hauslinie fuer den Berater
(die 309 Relikte des Spielers waeren ein 6-s-Lesen je Lauf), und sie ist hier
noetig: ein gehaltener Slot, ein **leer** gehaltener Slot, ein weisser Slot
und ein Deep-Vessel muessen gesagt werden, sonst belegt ein gruener Lauf nur,
dass dieser Spielstand zufaellig bequem aussieht.

**Positivkontrollen, damit die Gleichheit nicht leer ist:**

- Der Test prueft **vorher**, dass die beiden Gestalten sich wirklich
  unterscheiden (`len(held)` differiert um genau 1, und die Probleme sind
  ungleich). Ohne das waere ein Fall, in dem beide Seiten dasselbe Problem
  bauen, gruen und ohne Aussage.
- Jeder Pool muss **mindestens zwei** Kandidaten haben; bei einem waere jede
  Aussage ueber Ordnung und Inhalt trivial. Deshalb sind die beiden farbigen
  Slots gleichfarbig -- eine Farbe, von der der Spieler eine Kopie besitzt,
  gibt einen Pool von eins.
- Die Relikte tragen **zwei** Wirkungsarten (Staerke bewegt den Schaden,
  Vigor die effektive HP). Truegen alle dieselbe, waere "gleiche Punktzahlen
  unter beiden Richtungen" ein Vergleich von 0,00 mit 0,00.

**Die zweite Haelfte, IX-0/IX-2:** ein Pool bedient beide Richtungen
(`test_one_pool_serves_both_directions_and_only_its_order_follows_one`).
Ueber dieselben fuenf Oeffnungen sind `scores`, `baseline`, `unknowns` und
die nach Handle sortierten Kandidaten unter der kanonischen und unter der
anderen Richtung identisch; nur `rank_by` und die Reihenfolge folgen der
Richtung. **Zaehlbeleg als Positivkontrolle: 3 von 5 Oeffnungen kommen
tatsaechlich in anderer Reihenfolge zurueck** (z. B. `[104, 102, 100, 103]`
gegen `[103, 100, 102, 104]`), sonst waere "dieselben Kandidaten in anderer
Ordnung" eine Aussage ueber Pools, die schlicht identisch sind. Die zwei
Deep-Oeffnungen ordnen gleich -- ihre Kopien tragen nur Staerke-Rollen; das
ist im Testtext gesagt.

**Kein Rueckfallweg gebaut** (Auftrag): es gab nichts aufzufangen.

## Tests

`pytest tests/test_advisor_slot_pool.py` (ohne `-n`, wie vorgeschrieben):
**11 passed in 6,09 s**.

| Fall | was er festhaelt |
|---|---|
| `..._answers_the_pool_the_picker_computes_today[max_damage\|min_damage_taken]` | der Gleichheitsbeleg oben, 5 Oeffnungen je Richtung |
| `..._names_the_open_slot_by_leaving_it_free` | der zurueckgegebene Pool traegt den Index des freien Slots |
| `test_one_pool_serves_both_directions_...` | IX-0/IX-2 samt Reordnungs-Kontrolle |
| `test_the_canonical_order_is_a_direction_the_registry_answers_to` | `CANONICAL_POOL_ORDER in GOALS`, und ein Pool unter ihr antwortet mit ihr |
| `test_a_problem_that_is_not_one_open_slot_is_refused[0\|2]` | kein freier Slot / zwei freie Slots -> `ValueError` |
| `test_a_request_that_describes_another_run_is_refused` | die Ablehnungspruefung steht auch hier |
| `test_a_request_that_names_an_unknown_direction_is_refused` | `KeyError` mit der genannten Id |
| `test_a_stopped_pool_says_so_and_is_asked_once_per_offered_relic` | `should_cancel` erreicht den Vorsortierlauf (SEC-022); die Meldung nennt den Slot, der Zaehler steht auf 3 |
| `test_the_picker_s_answer_is_reachable_without_qt` | Vorgabe 1, in einem **eigenen Prozess** |

**Der Qt-Beleg ist ein Test, keine Zusicherung.** In diesem Prozess laedt
`conftest` PySide6 lange vor jedem Berater-Fall, also kann die Aussage nur in
einem Kindprozess gemacht werden: der importiert `advisor.goals` und
`advisor.run` und druckt jeden `PySide`-Eintrag aus `sys.modules`. Das ist
**transitiv** -- ein Qt-Import irgendwo unterhalb dieser beiden Dateien
taucht dort auf, was eine Durchsicht der zwei Dateien nicht leisten wuerde.

### Rot-vorher: die toetende Aenderung je Waechter (L-007, L-008)

Sieben Mutationen, je **eine** Eigenschaft, gefahren in einer Kopie des
Arbeitsbaums ausserhalb des Repos (`tar`-Kopie, `PYTHONDONTWRITEBYTECODE=1`,
nur diese Testdatei), **nach** der endgueltigen Fassung des Testmaterials
wiederholt. Alle sieben toeten; **kein Ueberlebender**.

| # | Aenderung | faellt |
|---|---|---|
| M1 | der offene Slot wird als `problem.slots[0].index` gelesen statt als der freie | 4 Faelle (beide Gleichheitsfaelle, der Index-Fall, der Abbruch-Fall) |
| M2 | die `len(open_slots) != 1`-Pruefung wird nie wahr | 2 (beide Ablehnungsfaelle) |
| M3 | `_refuse_a_request_that_asks_about_another_run` faellt weg | 1 |
| M4 | `should_cancel` wird nicht an `candidates.pool` weitergereicht | 1 |
| M5 | `CANONICAL_POOL_ORDER = "max_style"` (kein Ziel antwortet darauf) | 2 |
| M6 | `from PySide6 import QtCore` in `run.py` | 1 (der Qt-Fall, mit 15 geladenen PySide-Modulen im Text) |
| M7 | `base_state_for` hebt die Haltung des offenen Slots nicht mehr auf | 2 (beide Gleichheitsfaelle) |

**Was diese Faelle nicht sehen koennen und nicht behaupten:** beide Seiten des
Gleichheitsvergleichs laufen durch `candidates.pool`, also bewegt eine
Mutation **innerhalb** von `pool` beide Seiten und bleibt gruen (Bauform 2 aus
den bekannten Waechterfallen). Der Anspruch ist auch nur der Unterschied der
**Fragegestalt** -- und M1 und M7 zeigen, dass er dort beisst.

### Volle Suite

`pytest -n auto`: **1275 passed, 9 skipped, 0 failed in 157,75 s**, gegen die
Vorgabe 1264/9/0. Differenz **+11**, genau die elf neuen Faelle.

Zwischenstand zur Ehrlichkeit: der **erste** volle Lauf war
`1 failed, 1274 passed, 9 skipped` -- der Ankerfehler aus Punkt 4 oben. Nach
der Nachfuehrung von `mutate.py` gruen.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests gruen in der benannten Testumgebung (Windows 10 x64,
      Arbeitskopie, Branch `docs/audit-and-advisor-design`)
- [x] Neue Tests fuer neue Logik, jeder mit seiner toetenden Aenderung belegt
- [ ] **Linter: entfaellt** -- das Projekt hat keinen konfiguriert
      (`requirements-dev.txt` fuehrt nur `pytest` und `pytest-xdist`, es gibt
      keine ruff-/flake8-/pyproject-Konfiguration). Zeilenlaenge trotzdem
      geprueft: keine meiner Zeilen ueber 79 Zeichen (die zwei 80er in
      `goals.py`, Zeilen 24 und 116, sind Bestand).
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] UI/UX: nichts beruehrt -- `UI_SPEC.md` nicht angefasst, keine
      Oberflaeche entworfen
- [x] Bericht geschrieben; `ARCHITECTURE.md`, `GOAL.md`, `docs/state.md`,
      `qa/findings.md`, `docs/tasks/` unberuehrt

**Ungeprueft:** Linux und macOS (kein Ziel). Kein Programmstart, also keine
Aussage ueber das laufende Fenster -- die gehoert zu U5b/U6.

## An qa-engineer

- Die Datei ist **Qt-frei und schnell** (6 s), lauft sie einzeln ohne `-n`.
- Kanten, die ich abgedeckt habe: kein freier Slot, zwei freie Slots, leer
  gehaltener Slot, weisser Slot (zieht jede Farbe), Deep-Vessel, gehaltene
  Kopie faellt aus dem Pool, unbekannte Richtung, Abbruch im Vorsortierlauf.
- Kanten, die ich **nicht** abgedeckt habe und die interessant waeren:
  (a) die Gleichheit gegen den **echten** Spielstand des Nutzers (309
  Relikte) statt gegen gebautes Material -- ich habe darauf verzichtet, weil
  ein Lesen 6 s je Lauf kostet und die awkward-Faelle dort nicht garantiert
  vorkommen; (b) die Gleichheit ueber **alle** Chalice-Layouts, wie es
  `test_advisor_covers_every_chalice.py` fuer den ganzen Lauf tut. Beides ist
  eine Ausweitung, keine Luecke im Auftrag -- aber wenn irgendwo ein
  Unterschied der beiden Fragegestalten steckt, dann dort.
- Ein Pool mit **einem** Kandidaten macht jede Ordnungsaussage leer; wer hier
  Faelle ergaenzt, prueft die Kandidatenzahl mit.

## An ui-ux-designer

Keine Abweichung; ich habe keine Oberflaeche beruehrt. Eine Zusicherung, die
dich betrifft: `run.slot_pool` **erzwingt** die kanonische Richtung nicht --
sie liest `request.goal_id`. Die Festlegung, dass die Picker-Anfrage
`goals.CANONICAL_POOL_ORDER` traegt und die Anzeige ihre Richtung aus der
Einstellung nimmt (AK-205), faellt in U5b. Bis dahin ist AK-205 baubar, aber
nicht gebaut.

## An director

1. **Der Gleichheitsbeleg faellt so aus, wie der `architect` erwartet hat**
   (Risikozeile `ARCHITECTURE.md:4400`): 10 von 10 Vergleichen identisch, der
   ganze `SlotPool`, nicht nur Handles und Punktzahlen. **AD-018 muss nicht
   revidiert werden, `AdvisorRequest` bekommt kein `slot_index`.**
2. **Eine Datei ausserhalb der Auftragsliste geaendert:**
   `scripts/differential/mutate.py`, Ankernachfuehrung (Punkt 4 oben). Sie war
   erzwungen -- ohne sie ist die Suite rot -- und ist auf eine Zeile Anker
   plus einen erlaeuternden Satz begrenzt, in einem **eigenen** Commit
   (4b55334). Melde ich, weil der Auftrag die Datei nicht nennt.
3. **Nicht registriert: die sieben Mutationen dieses Auftrags.** Die Hausregel
   ("jeder neue Waechter bekommt eine registrierte toetende Mutation") wuerde
   sieben Eintraege in `scripts/differential/mutate.py` verlangen. Ich habe
   sie **gefahren und dokumentiert**, aber **nicht eingetragen**, weil die
   Datei nicht zum Auftrag gehoert und U6 ohnehin Mutationen dort ergaenzen
   wird. **Das ist eine Luecke, kein Beleg** -- Entscheidung, ob sie mit U6
   nachgetragen werden oder als eigener kleiner Auftrag. Der Treiber, mit dem
   ich sie gefahren habe, liegt unter
   `…/scratchpad/T-128/mutate.py` (die beiden Baumkopien habe ich geloescht).
4. **OF-29 bekommt einen konkreten Fall.** Der `architect` fragt, ob ein Feld,
   das nur unter einer Randbedingung bedeutet, was sein Name sagt, diese
   Bedingung im Typ tragen muss. Nach diesem Auftrag ist die Lage: `goal_id`
   heisst auf der Advisor-bar-Spur "die Wahl des Spielers" und auf der
   Picker-Spur "die Ordnung dieser Liste", und **nichts im Typ unterscheidet
   die beiden**. Meine Konstante macht den Unterschied benennbar, nicht
   erzwingbar. Wenn die Entscheidung faellt, dass der Typ es tragen soll, ist
   der Ort `types.AdvisorRequest` und der Zeitpunkt **vor** U5b, nicht danach.
5. **Kein Sicherheitsfund.** SEC-022 nicht angefasst; die Dichteschranken
   liegen unveraendert in `savefile.py`/`inventory.py`. Die Abbruchkette
   erreicht den neuen Weg (Fall `..._is_asked_once_per_offered_relic`), was
   sie muss, weil der Vorsortierlauf auf einem praeparierten Spielstand der
   ganze Lauf ist.
6. **Keine neue Abhaengigkeit**, keine Netzzugriffe, keine Spieldaten im
   Repository, kein Bildnachweis.
7. **Bestandsschuld, nicht behoben, nur gemeldet:** `relicpicker.py:276-281`
   begruendet den Hauptthread-Lauf weiter mit den widerlegten ~51 ms (OF-27,
   dritte Fundstelle). Das ist ausdruecklich U5b und ich habe die Datei nicht
   angefasst.

## Ausgefuehrte Befehle (Auszug, mit Ausgabe)

```
pytest tests/test_advisor_slot_pool.py -q      -> 11 passed in 6.09s
pytest -n auto -q          (1. Lauf)           -> 1 failed, 1274 passed, 9 skipped in 161.81s
pytest tests/test_differential_track.py -q     -> 222 passed in 3.90s
pytest -n auto -q          (nach dem Fix)      -> 1275 passed, 9 skipped in 157.75s
python scripts/differential/mutate.py --apply advisor-run-takes-a-request-about-another-run --tree <scratch>
                                               -> run.py:372 rewritten (-76 bytes)
  danach dort: pytest tests/test_advisor_run.py tests/test_advisor_slot_pool.py
                                               -> 7 failed, 44 passed (alle sieben Felder des benannten Falls)
Mutationslauf M1..M7 (Kopie ausserhalb des Repos)
                                               -> 7 von 7 toeten, kein Ueberlebender
```
