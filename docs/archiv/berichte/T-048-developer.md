# T-048 — developer

```
STATUS: erledigt
AUFTRAG: T-048 — Die Ergebnisform des Beraters umsetzen und seine Waechter
         scharf machen
GELESEN: docs/tasks/T-048.md · docs/berichte/T-047-architect.md (Abschnitt 1,
         "was wird heute falsch", und die fuenf Umsetzungsschritte) ·
         ARCHITECTURE.md Nachtrag VI (AD-025 ab Z. 2883, Praezisierungen zu
         AD-004/AD-009/AD-010/AD-016, Pruefpunkte 29-34, Nicht-tun 33-38) ·
         docs/berichte/T-041-qa-engineer.md (QA-100, QA-101, QA-102, QA-107) ·
         docs/berichte/T-045-developer.md (Befund D-1/D-3 zu QA-115) ·
         docs/berichte/T-051-qa-engineer.md (QA-120, QA-123, QA-124) ·
         qa/findings.md (QA-088, QA-100 bis QA-124) · CLAUDE.md ·
         nrplanner/advisor/{__init__,types,goals,candidates,evaluate}.py ·
         nrplanner/{model,damage,weapons,arsenaltab,app}.py ·
         tests/test_advisor_{types,goals,candidates,evaluate}.py ·
         tests/{advisor_cases,weapon_damage_cases,conftest}.py ·
         tests/test_{one_build,differential_track,arsenal_tab_asks_the_facade}.py ·
         scripts/differential/{__init__,mutate,plan}.py
GEAENDERT: nrplanner/advisor/types.py · nrplanner/advisor/goals.py ·
           nrplanner/advisor/candidates.py · nrplanner/model.py ·
           nrplanner/damage.py · nrplanner/weapons.py ·
           nrplanner/arsenaltab.py · scripts/differential/mutate.py ·
           scripts/bracketing_residue.py (neu) · tests/advisor_cases.py ·
           tests/test_advisor_types.py · tests/test_advisor_goals.py ·
           tests/test_advisor_candidates.py · tests/test_advisor_evaluate.py ·
           tests/test_arsenal_tab_asks_the_facade.py ·
           tests/weapon_damage_cases.py · tests/test_bracketing_residue.py
           (neu) · docs/berichte/T-048-developer.md (diese Datei).
           Elf Commits auf `docs/audit-and-advisor-design`, alle nur mit
           eigenen Dateien. Kein push/pull/fetch/merge/rebase/checkout/
           branch/reset/revert/stash.
ANNAHMEN: (1) `Build.situational` mit `live == False` ist die Menge, die die
          konditionale Zeile zaehlen soll — vom `architect` gelesen, von mir
          gegen einen Lauf **gemessen** (Pruefpunkt 33 gruen, Gegenbau rot),
          damit keine Annahme mehr. (2) QA-113s Laufbefund zaehlt jeden
          Kandidaten mit einem flachen `*AttackPower`-Feld, gated oder nicht;
          ein gated Kandidat kann damit von zwei Zeilen genannt werden. Siehe
          "An den director", Punkt 4. (3) Der Platzhalter-Wortlaut ist meiner
          und ausdruecklich nicht endgueltig.
NAECHSTER: director (sechs Punkte, davon zwei entscheidungsbeduerftig),
           danach ui-ux-designer (OF-20, der Wortlaut) und qa-engineer
BLOCKIERT DURCH: nichts
```

---

## 0. Ergebnis in fuenf Zeilen

1. **Teil 1** ist vollstaendig gebaut, in der Reihenfolge des `architect`:
   `Goal.scope`, die zwei Faelle, `Baseline`, die konditionale Zeile,
   `held_fingerprint` gestrichen. Fuenf Pruefpunkte (29-34) haben je einen
   eigenen, gefahrenen Gegenbau.
2. **Teil 2 (QA-100)** ist erledigt: **alle vier** Gegenbauten werden rot,
   plus ein fuenfter (`declared={}`), den der neue Zustand mitnimmt. Einer der
   vier — `weapon=None` — ist durch **keinen** Build-Vergleich erreichbar; das
   ist gemessen und hat einen zweiten Waechter bekommen. Abschnitt 2.
3. **Teil 3** erledigt, mit einem Befund: QA-114s Zahlen ("12 Zeilen",
   "stateInfo 2101, sieben Mitglieder") sind aus dem extrahierten Datensatz
   **nicht** nachfahrbar. Abschnitt 4.
4. **Teil 4** erledigt, mit dem groessten Einzelbefund: die QA-115-Messung
   ergibt **544**, nicht 574. Abschnitt 5.
5. **Ein eigener Fall lief gegen seinen eigenen Gegenbau gruen** und ist erst
   durch den Mutationslauf aufgefallen. Abschnitt 6.

**Suite:** `-m "not slow"` **592 passed, 5 deselected** (vorher 563);
`-m "slow"` **5 passed**. Beide selbst gefahren, zuletzt am Endstand.

---

## 1. Rueckgabeformat Punkt 2 — was in Schritt 1 gefallen ist

Der `architect` sagt "danach ist die Suite rot an genau zwei Faellen". Es sind
**zwei Testfunktionen**, aber **drei Test-Ids**, und zwei weitere Dinge fallen
mit, die er nicht genannt hat. Gemessen, nicht geschaetzt:

```
4 failed, 559 passed, 5 deselected in 88.78s
FAILED tests/test_advisor_goals.py::test_no_goal_hands_back_an_empty_unknowns[max_damage]
FAILED tests/test_advisor_goals.py::test_no_goal_hands_back_an_empty_unknowns[min_damage_taken]
FAILED tests/test_advisor_goals.py::test_the_damage_goal_always_carries_the_attack_rating_reservation
FAILED tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source[advisor-goal-without-its-unknowns]
```

- Die zwei genannten Faelle: **beide rot**, der erste zweimal (parametrisiert
  ueber die zwei Zielrichtungen).
- **Nicht genannt, dritter Roter:** der Ankerwaechter der Messstrecke. Die
  Mutation `advisor-goal-without-its-unknowns` zeigte auf `unknowns=
  _DAMAGE_TAKEN_UNKNOWNS`, das es nach dem Umzug nicht mehr gibt. Das ist der
  Waechter, der genau dafuer gebaut ist — er hat funktioniert.
- **Nicht genannt und vor allen anderen:** `tests/test_advisor_types.py`
  liess sich gar nicht erst einsammeln. `SAMPLES` baut ein `types.Goal` mit
  Schluesselwortargumenten, und `scope` hat keinen Vorgabewert, also
  `TypeError` beim Import — `1 error during collection`, die ganze Datei weg.
  Der Rot-Beleg oben ist deshalb **nach** dem Ergaenzen des Samples gemessen;
  das ist eine Konstruktionsanpassung, keine Zusicherungsaenderung.

**Nach Schritt 2** (Pruefpunkte 29, 30, 31) ist die Suite wieder gruen, und
die alte Zusicherung ist nicht verduennt: `test_the_damage_goal_always_
carries_the_attack_rating_reservation` behaelt **alle acht** Assertions
woertlich und liest sie jetzt aus `GOALS["max_damage"].scope`.

**Gewinn gegen QA-106, gemessen mit `pytest --setup-plan`:** drei Test-Ids
brauchen ab jetzt **kein** `game_data` mehr —
`test_no_direction_carries_an_empty_scope[max_damage]`, `[min_damage_taken]`
und der Vorbehaltsfall. Sie ziehen nur `qapp` und `settings_store`. Das sind
die ersten Berater-Faelle, die auf einem Runner ohne Spielinstallation
ueberhaupt etwas belegen.

---

## 2. Rueckgabeformat Punkt 1 — Teil 2, die vier Gegenbauten

Jeder in einem eigenen `git archive HEAD`-Klon, `mutate.py --apply`, volle
Suite `-m "not slow"`, `PYTHONHASHSEED=0`, offscreen. **Der Ankerwaechter des
mutierten Klons ist in jedem Lauf zusaetzlich rot** — das ist die Bestaetigung,
dass die Mutation griff, kein inhaltlicher Kill, und unten getrennt gefuehrt.

| Gegenbau (Registry-Name) | Suite | inhaltlich rot |
|---|---|---|
| `weapons_held=[]` (`advisor-computes-without-the-armaments-held`) | 3 failed, 589 passed | **Pruefpunkt 13** + der Durchreich-Fall |
| `weapon=None` (`advisor-computes-without-the-reference-armament`) | 2 failed, 590 passed | **nur der Durchreich-Fall** — siehe unten |
| `ctx.level -> 1` (`advisor-computes-at-the-first-level`) | 3 failed, 589 passed | **Pruefpunkt 13** + der Durchreich-Fall |
| `ctx.hero -> heroes[0]` (`advisor-computes-for-the-first-nightfarer`) | 2 failed, 590 passed | **Pruefpunkt 13** |
| `declared={}` (`advisor-computes-with-nothing-declared`, Zugabe) | 5 failed, 587 passed | Pruefpunkt 13, der Durchreich-Fall, die konditionale Zeile, `test_a_declared_conditional_reaches_the_build` |

**Alle vier werden rot. Keiner bleibt gruen.**

### 2.1 `weapon=None` ist durch keinen Build-Vergleich erreichbar — gemessen

Das ist der wichtigste Einzelbefund dieses Teils, und er ist kein Restrisiko,
sondern eine Eigenschaft von `model.compute`:

```python
    if weapons_held:
        wep_type = {w.get("wep_type") for w in weapons_held if w}
        ...
    else:
        wep_type = weapon.get("wep_type") if weapon else None
```

`weapon` wird **ausschliesslich** im `else`-Zweig gelesen. Beide Aufrufer im
Programm — `app.Planner._rebuild` und `advisor.evaluate` — fuellen `weapon`
und `weapons_held` aus demselben Waffengitter, und `equipped_weapons()` ist
nicht leer, sobald irgendein Tile gefuellt ist; eine Referenzwaffe gibt es nur,
wenn das aktive Tile gefuellt ist. **Referenz vorhanden ⇒ Gitter nicht leer ⇒
`weapon` ungelesen.** Meine Sonde gegen den fertigen Zustand:

```
  weapons_held=[]      differs: True
  weapon=None          differs: False
  level -> 1           differs: True
  hero -> heroes[0]    differs: True
  declared -> {}       differs: True
```

Deshalb hat dieser Gegenbau einen zweiten Waechter bekommen, den QA-100 selbst
vorgeschlagen hat: `test_evaluate_hands_the_whole_context_to_the_model` legt
ein aufzeichnendes Double auf `model.compute` (das echte laeuft weiter) und
prueft Argument fuer Argument. Dazu eine Tabelle `CONTEXT_REACHES_COMPUTE`,
die **jedes** Feld des `GoalContext` einem `compute`-Argument zuordnet oder
begruendet, warum es keinem zugeordnet ist (`weighting`: das ist die Sache der
Zielrichtung). `test_every_field_of_the_context_is_accounted_for` bricht,
sobald jemand ein Feld hinzufuegt, ohne die Zuordnung zu entscheiden — QA-001
war "ein zweiter, kuerzerer Argumentsatz", und so kommt er ein Feld nach dem
anderen zurueck.

### 2.2 Der neue Zustand

`a_state_worth_comparing()` in `tests/test_advisor_evaluate.py` stellt her:
ein Nightfarer, dessen Grundattribute sich von `heroes[0]` unterscheiden
(**nach den Zahlen** gewaehlt, nicht nach Name oder Index), Level 15 statt der
Reglergrenze 1, zwei Waffen verschiedenen Typs, ein Effekt, der auf dem Typ
der **zweiten** haengt (per Abfrage gefunden und durch `model.compute`
verifiziert, dass er wirklich eine Zahl bewegt — 102 Effekte tragen so ein
Gate, die meisten bewegen nichts), eine erklaerte Bedingung, Deep an mit
verfluchten Relikten. Der Fall **sichert diesen Zustand zu**, bevor er
vergleicht; ein Fall, der an einen Zustand glaubt, den er nicht hat, ist genau
der behobene Fehler.

---

## 3. Teil 1 — die Ergebnisform, Schritt fuer Schritt

**Schritt 1/2 (Commit `bf421d2`).** `Goal.scope` eingefuehrt, acht Saetze
umgehaengt. Die Konstanten heissen jetzt `_ATTACK_RATING_SCOPE` und
`_DAMAGE_TAKEN_SCOPE` — **das ist eine Abweichung**, der `architect` hat keine
Umbenennung verlangt. Begruendung: AD-025 macht "scope" zum Fachwort, und die
Klasse eines Satzes soll an seiner Definitionsstelle sichtbar sein; do-not
Regel 34 verbietet die Umbenennung des **Feldes** `GoalScore.unknowns`, nicht
die zweier privater Modulkonstanten. Der Kommentarblock zur QA-095/QA-099-
Historie steht woertlich unveraendert.
`_NO_ARMAMENT` und `_NO_ARMAMENT_NOTE` bleiben, wo sie waren, und sind jetzt
im Docstring als Musterfall der Gegenklasse benannt.

**Schritt 3 (Commit `5d94d06`).** `Baseline` traegt `unit`, `unknowns`,
`weights_note`; `pool()` behaelt den ganzen `GoalScore` statt nur `.value`.
`display` faehrt **nicht** mit (Nicht-tun 33). Kein neuer Typ, kein `dict`,
keine `list`, `GoalScore.unknowns` nicht umbenannt, `baseline_for()`
unveraendert gueltig.

**Schritt 4 (derselbe Commit).** Die konditionale Zeile entsteht in `pool()`,
gezaehlt ueber die Kandidaten **dieses** Pools, gebildet aus
`Build.situational` mit `live == False` und gefiltert auf die Effekt-Ids des
Kandidaten. Keine zweite Ableitung des Waffentyps (Nicht-tun 36) — sie waere
an dieser Stelle nicht einmal schreibbar, weil die Funktion keinen Datensatz
haelt.
**Schritt 3 und 4 sind ein Commit**, weil beide in derselben Zeile von
`pool()` zusammenlaufen (`return types.SlotPool(...)`) und ein Zwischenstand
die Suite rot liesse. Bewusst so, im Commit-Text begruendet.

**Schritt 5 (Commit `9d9df0d`).** `held_fingerprint` gestrichen: freie
Funktion, Property und Waechter. Drei Testfaelle umgehaengt, **keiner**
geloescht. `test_where_a_relic_is_held_does_not_change_the_fingerprint` wird
zu `test_where_a_relic_is_held_is_part_of_the_question` — dieselbe Stelle, die
umgekehrte Aussage, mit der staerkeren Begruendung des `architect`
(Slotindizes in der Antwort, keine Rueckabbildung). Der `repr`/`None`-gegen-
`int`-Einsicht steht jetzt im Docstring des umgehaengten Custom-Relikt-Falls.

**Die neuen Waechter und ihre Gegenbauten** (je eigener Klon, volle Suite;
Ankerwaechter des Klons getrennt gezaehlt):

| Pruefpunkt | Gegenbau | Ergebnis |
|---|---|---|
| 29 | `advisor-goal-without-its-scope` | 2 failed → `test_no_direction_carries_an_empty_scope[min_damage_taken]` |
| 30 | `advisor-scope-sentence-repeated-as-a-run-finding` | 2 failed → `test_no_sentence_stands_in_both_classes[max_damage]` |
| 31 | `advisor-run-finding-that-outlives-every-run` | 2 failed → `test_a_run_finding_does_not_survive_every_run[min_damage_taken]` |
| 32 | `advisor-pool-keeps-only-the-figure` | 2 failed → `test_the_pool_carries_what_the_direction_could_not_know` |
| 33 | `advisor-counts-conditions-it-did-count` | 2 failed → `test_the_conditional_line_counts_what_was_really_left_out` |
| AD-004.4 | `advisor-counts-the-held-bundle-s-conditions` | 2 failed → `test_the_conditional_line_counts_this_pool_and_not_the_held_bundle` |
| 34 | `advisor-key-forgets-the-held-state` | **4 failed, kein** Ankerwaechter → die drei Schluesselfaelle plus die Ungleichheitshaelfte des Custom-Relikt-Falls |

Jeder Gegenbau toetet **genau seinen** Waechter; 30 und 31 sind bewusst durch
verschiedene Eingriffe getrennt (30 legt einen vorhandenen Scope-Satz in den
Zweig ohne Referenzwaffe, 31 legt einen **neuen** Satz in einen Zweig, den
jeder Lauf erreicht), damit keiner der beiden fuer den anderen einspringt.

**Drei Abweichungen von den Vorgaben des `architect`, benannt:**

1. **Pruefpunkt 33s Gegenbau ist nicht der vorgeschriebene.** Vorgegeben:
   "die Zeile aus einer zweiten Ableitung ueber die Relikt-Definitionen
   bilden". Das ist an dieser Stelle **nicht schreibbar** — `_brought_an_
   uncounted_condition(build, candidate)` haelt keinen Datensatz, aus dem die
   Effektsaetze zu lesen waeren. Genau das ist der Entwurf, der wirkt: die
   falsche Ableitung ist von hier aus unerreichbar. Der registrierte Gegenbau
   streicht stattdessen `and not entry.live` — der kuerzeste Eingriff, der
   exakt die vorhergesagte Wirkung hat (der deklarierte Fall zaehlt weiter
   mit). Steht so im `survival_means`.
2. **Pruefpunkt 34s Gegenbau schreibt ein `__eq__`/`__hash__`-Paar in den
   Rumpf von `SlotProblem`,** statt `held` aus dem Request zu nehmen. Grund:
   `advisor/types.py` importiert `dataclass`, nicht `dataclasses`, also gaebe
   es fuer `field(compare=False)` keinen Ein-Anker-Eingriff; und ein Paar im
   Klassenrumpf wird von `dataclasses` respektiert (nachgeprueft), ist die
   Form, die der Fehler wirklich haette, und laesst den Anker stehen —
   dieser Gegenbau erzeugt als einziger **keinen** Zusatz-Roten.
3. **Der Custom-Relikt-Fall hat doch eine toetende Mutation.** Ich hatte in
   seinen Docstring geschrieben, er sei eine Charakterisierung ohne Gegenbau.
   Der Lauf hat das widerlegt: `advisor-key-forgets-the-held-state` faerbt ihn
   rot. Korrigiert (Commit `fb146a8`) — die `hash()`-Haelfte ist ohne
   Gegenbau, die Ungleichheits-Haelfte nicht. Ich hatte es behauptet, ohne es
   gemessen zu haben; die Messung war zwanzig Minuten Arbeit.

---

## 4. Teil 3 — die Begruendungen

### QA-101 — die Begruendung getauscht, selbst nachgemessen

Die widerlegte Behauptung stand an **drei** Stellen im Code, nicht an einer.
Volltextsuche mit zwei unabhaengigen Masken:

- `"constant factor|konstanter faktor"` → 3 Treffer in `nrplanner/`, `tests/`,
  `scripts/`
- `"ranking would surviv|order would surviv|surviv.*the swap"` → 2 Treffer

Zusammen: `nrplanner/advisor/goals.py` (`_max_damage`-Docstring),
`scripts/differential/mutate.py` (`survival_means`),
`tests/test_advisor_goals.py` (Modul-Docstring). Alle drei getauscht;
dieselben Suchen liefern jetzt nur noch die **korrigierten** Saetze (die
`docs/`-Treffer gehoeren fremden Berichten und sind Verlauf).

**Selbst nachgemessen statt uebernommen** (Wylder, Level 15, eigene Startwaffe
in Slot 1, Tier 1, Endstand des Programms):

```
R0 [7120400, 6001400]      d(equipped) =  -7.4146   d(candidate) = +12.8153
R1 [7000300]               d(equipped) =  +0.4977   d(candidate) =  +0.4977
equipped  -> ['R1', 'R0']
candidate -> ['R0', 'R1']
Effekte, die die Strafe selbst tragen: [7120400, 7120500, 7120600]
```

R0 deckt sich ziffernweise mit dem Nachtrag in `qa/findings.md` (T-049,
Post-Kalibrierung: −7,4146 / +12,8153). R1 weicht ab (+0,4977 gegen die dort
genannten +0,8294) — die dort genannte Zahl ist die **vor** der 0,6-
Kalibrierung; 0,8294 × 0,6 = 0,4976, also dieselbe Messung. Die Aussage ist
unberuehrt: die Reihenfolge dreht.

**Neuer Fall `test_the_damage_goal_ranks_a_self_inflicted_penalty_below`.**
Er haelt die **Reihenfolge**, nicht den Betrag, und seine erste Zusicherung
ist die, die ihn nicht leer laufen laesst: sie prueft, dass die beiden Fragen
ueber dieses Kandidatenpaar ueberhaupt verschieden antworten. Ein Ordnungstest
ohne diesen Nachweis ist leer.
Gefahren: `damage-goal-asks-the-slotless-question` faerbt jetzt **zwei** Faelle
rot (Betrag und Reihenfolge) statt einem.

### QA-114 — die Feldaussage von der Familienaussage getrennt, mit einem Befund

Gemessen ueber die 2076 Effekte von `data_version 10350000`:

- `*AttackPowerRate`: **3 Effekte** (7120400/500/600), **15**
  Modifier-Eintraege (jeder Effekt traegt alle fuenf Felder auf 0,85).
- flache `*AttackPower`: **21 Effekte**, darunter die vier
  7120000/100/200/300.

**Befund, und darum steht die Zahl nicht im Kommentar:** Die Auftragsangabe
"3 Effekte / **12 Zeilen** fuer das Feld, **7 Mitglieder** fuer die Familie
(`stateInfo 2101`)" ist aus dem extrahierten Datensatz **nicht nachfahrbar**.
Ich zaehle 15 statt 12 Modifier-Eintraege, und der Datensatz traegt **kein**
`stateInfo`-Feld (die einzigen `state`-haltigen Schluessel sind
`invocationConditionsStateChange1/2/3` und `enemyStateInfoTrigger`). Beides
stammt offenbar aus den Params, nicht aus der Extraktion. Der Kommentar sagt
jetzt, was hier zaehlbar ist, und dass die Gruppierungsangabe die Lesart des
`qa-engineer` aus den Params ist und aus diesem Datensatz nicht reproduziert
werden kann. Eine Zahl in den Quelltext zu schreiben, die der naechste Leser
nicht nachfahren kann, waere derselbe Fehler wie QA-115.

### QA-113 — die Blindstelle benannt, die Hoehe nicht geraten

Drei Teile, nach AD-025 getrennt:

- `model.FLAT_ATTACK_POWER_FIELDS` — die fuenf Felder, mit der Messung
  (21 Effekte; die vier Relikte tragen `physicsAttackPower` −30 mit
  `<element>AttackPower` +33 an der **ersten von vier** `payload_tiers`,
  steigend bis −60/+66 — beide Zahlenreihen des Auftrags stimmen also, sie
  stehen nur an zwei verschiedenen Orten des Datensatzes) und mit dem
  ausdruecklichen Satz, dass die Einbauhoehe eine Ablesung im Spiel braucht.
- Ein **Verfahrenssatz** in `MAX_DAMAGE.scope`: die Zahl enthaelt keine
  Umwandlung.
- Ein **Laufbefund** im Pool: wie viele Kandidaten dieses Pools betroffen sind.

Damit ist dies zugleich der erste **fuenfte** Satz in `advisor/goals.py` —
also der Pruefsatz aus AK-63 ("ein fuenfter Satz erscheint danach an beiden
Anzeigeorten, ohne dass ein UI-String angefasst wurde"), sobald S10 gebaut
ist.

---

## 5. Teil 4

### QA-115 — Rueckgabeformat Punkt 3: die Messung ergibt **544**, nicht 574

`scripts/bracketing_residue.py` (neu, ohne Argumente lauffaehig) ist die
Messung. Voller Lauf, 05.09.2026, `data_version 10350000`:

```
10 Nightfarers x levels [1, 12, 15] x tiers [1, 2, 3, 4] x 1793 armaments
  = 215160 cases, 350160 figures per damage type
  every shipped figure matches weapons.rate bit for bit
  per damage type:
    shipped        0 of 350160 at 2 ULP or more; spread {0: 350160}
    on_the_base  544 of 350160 at 2 ULP or more; spread {0: 228136, 1: 121480, 2: 544}
  summed per case:
    shipped      447 of 215160 at 2 ULP or more
    on_the_base 3058 of 215160 at 2 ULP or more
```

**Bestaetigt die Zahl im Kommentar nicht.** Fallzahl (215 160) und
Zahlenzahl (350 160) werden **exakt** reproduziert, es ist also dieselbe
Messung; die Restzahl ist 544 gegen 574. Was die 30 erklaert, ist ohne das
verschollene `dump_rate.py` nicht entscheidbar; die naechstliegende Lesart
steht im Kommentar (sein `bonus` duerfte mit `sum()` akkumuliert worden sein,
wo `weapons.rate` eine Schleife hat — genau ein letztes Bit, und das ist die
gezaehlte Groesse). **Bestaetigt** ist dagegen die eigentliche Aussage, und
schaerfer als behauptet: der versendete Weg liegt bei **0 von 350 160**
ueberhaupt daneben — jede Zahl je Schadensart ist exakt `fl(alt × 0,6)`, nicht
bloss innerhalb eines Bits.
Die Summenzahlen (447/3058 gegen 480/1081) sind **nicht** vergleichbar: das
alte Paar nannte keine Definition von "der Summe". Die neuen Zahlen sind die
des Skripts, und die qualitative Aussage ("ein Rest bleibt in beiden Faellen
und ist aus dieser Funktion heraus nicht zu beseitigen") gilt unveraendert.

**Das Skript haelt sich an das Programm.** Es leitet die Arithmetik neu her —
anders geht es nicht — und prueft **jede** versendete Zahl bitgleich gegen
`weapons.rate`. Der Waechter schlug beim ersten Lauf sofort zu: `influence /
100` in das Produkt hineingezogen ist eine andere Klammerung, 105 von 1680
Zahlen daneben. `tests/test_bracketing_residue.py` haelt diesen Waechter
fest, damit ein Refactoring von `weapons.rate` einen roten Testlauf erzeugt
statt eine stille Fehlmessung.
**Rot-vorher-Beleg fuer den Waechter:** dieselbe Klammerungsaenderung
zurueckgebaut → `1 failed, 3 passed`, `105 of 1320 figures ... are not the
ones weapons.rate forms`. Datei danach byte-genau zurueckgelegt,
sha256 `677b12851ab3d3f49c71457453fc039f57edb3c220f525b2f9677f559466f57f`
vorher und nachher identisch.

### QA-120 — gesagt statt geaendert

Die zwei Aufstiegszahlen (236 fuer den Stab auf Tier 3, 184 fuer Recluses
eigene Startwaffe auf Tier 2) stehen jetzt mit ihrem Geltungsbereich in
`tests/weapon_damage_cases.py`: belegt ist nur die Basisraritaet, die 84
Ablesungen sagen das in ihrem eigenen `left_out` bereits, die Faelle sagten es
nicht. Nur Text, keine Zahl bewegt, Golden unangetastet.

### QA-124 — und eine Abweichung, die entschieden werden sollte

`arsenaltab.recalculate()` liest die Stufe jetzt aus dem Build. **Das waren
nicht "eine Zeile":** `model.Build` trug kein Level, also war "aus dem Build
lesen" woertlich nicht moeglich. Ich habe `Build.level` eingefuehrt (ein Feld
mit Vorgabewert, in `compute` gesetzt) statt eine Rueckwaertssuche in
`hero["levels"]` zu bauen — die waere eine zweite Meinung darueber, was
gerechnet wurde, und zwei Stufen mit gleichen Grundattributen waeren nicht
unterscheidbar. In `arsenaltab.py` ist es eine Zeile. **Das ist eine
Formaenderung an `model.Build` und gehoert dem `director` gemeldet, nicht
stillschweigend gemacht** — sie steht hier.

### OF-2 — schon erledigt

`scripts/differential/__init__.py` sagt bereits "Five steps, five scripts"
(Commit `3ef1c24`, T-046). Geprueft, nichts geaendert.

---

## 6. Rueckgabeformat Punkt 5 — wo die Vorgabe im Kontakt mit dem Code nicht aufgeht

**Das entscheidet der `director`, nicht ich.** Ich habe jeweils die Lesart
gewaehlt, die ich unten begruende, und sie ist umkehrbar.

1. **"Genau zwei Faelle fallen" waren drei Test-Ids plus zwei Kollateralfaelle
   (Ankerwaechter, Sammel-Fehler an `SAMPLES`).** Abschnitt 1. Kein Widerspruch
   in der Sache, aber wer den Rot-Beleg nachfahren will, sieht andere Zahlen.
2. **`weapon=None` ist kein Build-Unterschied** (Abschnitt 2.1). Der Auftrag
   fuehrt ihn unter den vier Gegenbauten, die "rot werden muessen"; er wird
   rot, aber durch einen anderen Waechtertyp. Ohne diesen zweiten Waechter
   waere die Zusage nicht einloesbar gewesen.
3. **Pruefpunkt 33s vorgeschriebener Gegenbau ist nicht schreibbar**
   (Abschnitt 3, Abweichung 1).
4. **QA-113s Laufbefund kann einen Kandidaten doppelt nennen.** Von den 21
   Effekten mit flachem `*AttackPower` sind 16 ("Add \<element\> to Weapon")
   zugleich gated. Ein Kandidat, der einen davon traegt, wird von der
   konditionalen Zeile **und** von der Umwandlungszeile gezaehlt — zwei
   wahre Saetze ueber dasselbe Relikt aus zwei Gruenden. Die Alternative
   waere, nur die nicht-gateten zu zaehlen; dann verschwiegen wir die
   Umwandlung ausgerechnet bei denen, wo sie zusaetzlich zur Bedingung
   greift. Ich habe **alle** gezaehlt und es im Docstring von
   `_pool_findings` als gewollt benannt. **Wenn der `ui-ux-designer` zwei
   Zeilen ueber ein Relikt nicht will, ist das eine Anzeigeentscheidung, und
   die Zaehlung muesste getrennt werden.**
5. **QA-114s Zahlen sind nicht nachfahrbar** (Abschnitt 4).
6. **QA-115s Zahl ist eine andere** (Abschnitt 5).

---

## 7. Rueckgabeformat Punkt 4 — der Platzhalter

```python
# nrplanner/advisor/candidates.py
WORDING_PENDING = "[wording pending OF-20] "
```

Er steht **vor** beiden neuen Zeilen. Voller Wortlaut, wie er heute erzeugt
wird (Beispiel mit zwei betroffenen Relikten):

> `[wording pending OF-20] 2 of the relics offered for this slot carry an
> effect that only applies under a condition you have not declared, so they
> were not counted.`

> `[wording pending OF-20] 1 of the relic offered for this slot converts
> damage from one type to another. The game files do not say how much of it
> arrives, so the figure beside it leaves the conversion out entirely.`

Singular/Plural sind gebeugt, der Text beschreibt den **gezaehlten Bestand**
("the relics offered for this slot"), nicht "your relics" (Nicht-tun 38).
Die zweite Zeile hat im Singular einen Grammatikfehler ("1 of the relic"), den
ich absichtlich **nicht** repariere: der Satzbau gehoert dem
`ui-ux-designer`, und ein halb geglaetteter Platzhalter wird eher fuer fertig
gehalten als ein sichtbar unfertiger. Der Test prueft die Zeile ueber ihre
Anzahl und ihre Position, nicht ueber ihren Wortlaut — der Wortlaut kann
ausgetauscht werden, ohne dass ein Test bricht.

---

## An den `qa-engineer`

**Was zu testen ist:**

1. **Die Mutationsliste.** 14 Eintraege sind neu oder geaendert:
   `advisor-computes-{without-the-armaments-held,without-the-reference-armament,at-the-first-level,for-the-first-nightfarer,with-nothing-declared}`,
   `advisor-{goal-without-its-scope,scope-sentence-repeated-as-a-run-finding,run-finding-that-outlives-every-run,pool-keeps-only-the-figure,counts-conditions-it-did-count,counts-the-held-bundle-s-conditions,key-forgets-the-held-state}`,
   `arsenal-summary-reads-the-slider`, dazu die nachgezogenen Anker von
   `advisor-{leaves-a-relic-out-without-saying-so,scores-only-the-ranking-goal}`
   und der getauschte `survival_means` von
   `damage-goal-asks-the-slotless-question`. Alle von mir gefahren; Zahlen in
   Abschnitt 2 und 3.
2. **`advisor-fingerprint-sorted-naturally` ist geloescht.** Es mutierte eine
   Funktion, die es nicht mehr gibt.
3. **Randfall, den ich nicht abgedeckt habe:** ein Pool mit **allen drei**
   Zeilen gleichzeitig (handle-los + konditional + Umwandlung). Die Reihenfolge
   ist in `_pool_findings` festgelegt, aber kein Fall prueft sie.
4. **Randfall:** ein Kandidat, der eine konditionale **und** eine
   Umwandlungszeile ausloest (Abschnitt 6, Punkt 4) — heute in beiden Zahlen.
5. **`damage-goal-asks-the-slotless-question` faerbt im mutierten Klon einen
   zweiten Ankerwaechter rot** (`damage-goal-ranks-on-the-bare-figure`), weil
   beide auf denselben Quelltextbereich zeigen. Vorbestand, nicht von mir
   verursacht; beim Zaehlen trennen.
6. **`--step` des neuen Skripts.** `scripts/bracketing_residue.py --step N`
   druckt seinen Step mit; eine Teilstichprobe darf nicht als Ganzzahl zitiert
   werden.

## An den `ui-ux-designer` (ueber den `director`)

- **OF-20 ist jetzt terminwirksam:** zwei Zeilen tragen
  `[wording pending OF-20] `. Sobald der Wortlaut steht, faellt der Marker weg
  und es ist eine Zeile Aenderung je Satz. Die Zaehlung ist "die Kandidaten
  **dieses Pools**", nicht "your relics" — das ist der Punkt, an dem AD-004s
  Vorschlagswortlaut nicht mehr stimmt, und er gehoert in dieselbe Runde wie
  QA-108.
- **Zwei Zeilen ueber ein Relikt sind moeglich** (Abschnitt 6, Punkt 4).
- **AK-63 (OF-19) ist unveraendert offen und jetzt sichtbar wirksam:** nach
  AD-025 hat der Picker zwei Quellen. Ich habe die Registry-Haelfte und die
  Ergebnis-Haelfte gebaut; wer nur `GoalScore.unknowns` zeichnet, zeigt nach
  T-048 **weniger** als vorher. Ich habe keine Oberflaeche angefasst.

## An den `director`

**Entscheidungsbeduerftig:**

1. **`model.Build` hat ein Feld bekommen** (`level`), weil QA-124s "aus dem
   Build lesen" sonst woertlich nicht moeglich war (Abschnitt 5). Kleine
   Formaenderung an einem zentralen Typ, keine Zahl bewegt, 592 gruen. Wenn du
   das dem `architect` vorlegen willst, ist das der Ort.
2. **QA-113s Doppelzaehlung** (Abschnitt 6, Punkt 4). Meine Wahl ist
   umkehrbar.

**Zur Kenntnis, ohne Entscheidungsbedarf:**

3. **QA-115 ist mit einer anderen Zahl geschlossen** (544 statt 574). Die
   Klammerungsentscheidung selbst wird durch die Messung **staerker**
   gestuetzt als behauptet (0 statt "hoechstens 1 ULP").
4. **QA-114s Zahlen stammen aus den Params und sind aus dem Repo nicht
   pruefbar** (Abschnitt 4). Wer sie braucht, braucht die Params.
5. **Ein eigener Fall lief gegen seinen eigenen Gegenbau gruen** und ist nur
   durch den Mutationslauf aufgefallen (Abschnitt 5, QA-124-Fall; Ursache:
   `"at level 1"` ist Teilstring von `"at level 15"`). Behoben in `fb146a8`,
   und die Ursache steht als Warnung im `survival_means` des Gegenbaus. Das
   ist der beste Beleg dieses Auftrags dafuer, dass L-002 kein Formalismus
   ist: die Suite war gruen, der Test sah richtig aus, und er belegte nichts.

**Vorgefundene Schuld, nicht behoben (ausserhalb des Auftrags):**

6. **`ARCHITECTURE.md` nennt `held_fingerprint` an vier Stellen ausserhalb von
   Nachtrag VI weiter als geltend** (Z. 1438, 1627, 2434, 2468). Nachtrag VI
   loest sie ab, aber wer vorne liest, findet die alte Fassung. Ort:
   `ARCHITECTURE.md`. Art: ueberholte Zusicherung. Risiko: niedrig (die
   Funktion ist weg, ein Leser laeuft ins Leere). Aufwand: klein. Gehoert dem
   `architect`, ich habe die Datei nicht angefasst.
7. **`scripts/differential/mutate.py::newline_of` und der Kommentar daneben
   behaupten, `app.py` sei im Arbeitsbaum CRLF.** Ist es nicht — `.gitattributes`
   setzt `* text=auto eol=lf`, und alle Dateien im Arbeitsbaum sind LF
   (nachgezaehlt). Die Funktion ist trotzdem richtig (sie liest die Datei),
   nur ihre Begruendung ist veraltet. Risiko: keins. Aufwand: eine Zeile.
   Nicht behoben, weil ausserhalb des Auftrags.
8. **`weapons.rank` sortiert 1793 Elemente, die `rank_candidates` danach
   nochmals sortiert** — steht seit T-033 als gemeldet, unveraendert.

**Performance:** Der Pool ruft `evaluate` je Kandidat und jetzt zusaetzlich
zwei billige Praedikate darauf (`_brought_an_uncounted_condition` laeuft ueber
`build.situational`, `_converts_a_damage_type` ueber die Effektsaetze des
Kandidaten). Beides ist O(Effekte je Relikt), also gegen das `model.compute`
davor vernachlaessigbar. **Ich habe es nicht gemessen** und melde es als
Beobachtung, nicht als Zahl; wenn S11 den Picker misst, gehoert das in die
Messung. Kein Anlass, den `performance-tuner` jetzt zu beauftragen.

**Sicherheit:** keine Funde. Keine Secrets, keine neuen Abhaengigkeiten, kein
externer Input in Pfade oder Kommandos. `scripts/bracketing_residue.py` liest
nur den Datensatz und schreibt nur, wohin `--json` zeigt.

**Fremde Dateien:** unberuehrt. `git status --short` zeigt am Ende
`ARCHITECTURE.md`, `DESIGN_REVIEW.md`, `GOAL.md`, `UI_SPEC.md`,
`docs/plan-restarbeiten.md`, `docs/state.md`, `qa/findings.md`,
`security/findings.md` als fremd geaendert. **Vier davon — `GOAL.md`,
`docs/plan-restarbeiten.md`, `security/findings.md` und zuletzt weitere —
sind waehrend meiner Sitzung dazugekommen**, also von parallel laufenden
Rollen. Keine davon steht in einem meiner elf Commits (`git log --name-only`
ueber `216388e..HEAD` gegen `docs/|qa/|GOAL|ARCHITECTURE|UI_SPEC|
DESIGN_REVIEW|security/` gefiltert: null Treffer).

---

## Definition of Done

- [x] Anforderung verstanden, Annahmen dokumentiert (Kopfblock)
- [x] Build & Tests gruen in der benannten Testumgebung: Windows 10,
      `.venv\Scripts\python.exe -m pytest -q -m "not slow"` → **592 passed,
      5 deselected**; `-m "slow"` → **5 passed**. Beides selbst gefahren.
- [x] Neue Tests fuer neue Logik: 29 neue Test-Ids, jede neue Zusicherung mit
      registriertem und gefahrenem Gegenbau (L-002)
- [x] Keine Zeile ueber 79 Zeichen in den Dateien dieses Auftrags
      (`mutate.py` ausgenommen — seine Anker sind der Quelltext woertlich und
      duerfen nicht umgebrochen werden). Kein Linter im Repo konfiguriert.
- [x] Keine Secrets, keine TODOs, kein toter Code. `held_fingerprint` ist
      geloescht, nicht deaktiviert (Nicht-tun 37).
- [x] QA-Akzeptanzkriterien selbst durchgespielt (Abschnitt 2, 3, 5)
- [ ] **UI/UX:** nicht anwendbar — ausser der einen QA-124-Zeile keine
      Oberflaeche angefasst. `arsenaltab.py` ist die einzige beruehrte
      UI-Datei; `weaponslots.py`, `relicpicker.py` und `app.py` sind
      unveraendert.
- [x] Doku aktualisiert (Docstrings und Kommentare an jeder geaenderten
      Stelle), Abschlussbericht geschrieben

**Ungeprueft ausgewiesen:**
- **Die Oberflaeche hat niemand gesehen.** Alle Qt-Laeufe waren offscreen. Die
  QA-124-Zeile aendert einen Text (`arsenaltab.summary`), und ob er auf dem
  Bildschirm dasselbe zeigt wie vorher, ist nicht angesehen worden — er zeigt
  im laufenden Programm dieselbe Zahl wie vorher, aber das ist eine
  Herleitung, kein Blick. Gehoert zu QA-122.
- **Linux, macOS, Android, iOS:** ungeprueft. Das Projekt ist Windows-only
  (`gamefiles.find_game_dir`), CI ist `windows-latest`.
- **Ein Runner ohne Spielinstallation:** nicht real gefahren. Dass drei neue
  Test-Ids dort laufen, ist mit `pytest --setup-plan` belegt (kein
  `game_data`-Fixture), nicht durch einen Lauf ohne Datensatz.
