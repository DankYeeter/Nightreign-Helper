# T-047 — architect

```
STATUS: erledigt
AUFTRAG: T-047 — die Ergebnisform des Beraters nachziehen (QA-102, QA-107) und
         vier Entwurfsluecken schliessen
GELESEN: docs/tasks/T-047.md · GOAL.md · docs/state.md ·
         docs/berichte/T-041-qa-engineer.md (QA-102, QA-107, Abschnitte 9 und 13) ·
         ARCHITECTURE.md (AD-004, AD-007, AD-008, AD-009, AD-010, AD-016,
         AD-018, Nachtraege I bis V) · UI_SPEC.md (§3.2-§3.8, AK-47 bis AK-55,
         Nachtrag zu AK-47, Nachtrag zu QA-116/AK-63 vom 05.09.2026) ·
         qa/findings.md (QA-100 bis QA-124) ·
         nrplanner/advisor/{__init__,types,evaluate,candidates,goals}.py ·
         nrplanner/model.py (is_conditional, Build, Situational, compute) ·
         nrplanner/damage.py (headline_*) ·
         tests/test_advisor_{types,goals,candidates,evaluate}.py
GEAENDERT: ARCHITECTURE.md (Nachtrag VI mit AD-025, vier Praezisierungen,
           Pruefpunkte 29-34, Renummerierung Pruefpunkt 18 -> 28 an drei
           Stellen, historische Markierung des ueberholten AD-004-Zitats) ·
           docs/berichte/T-047-architect.md (diese Datei).
           Kein Anwendungscode, kein Test, keine schreibende Git-Operation.
ANNAHMEN: (1) `Build.situational` mit `live == False` ist die Menge, die die
          konditionale Zeile zaehlen soll — gelesen aus model.py:694-712 und
          model.py:892, nicht gegen einen Lauf gemessen. (2) `UI_SPEC` AK-63
          (05.09.2026) ist der geltende Stand der Anzeige; T-047 wurde am
          03.09. geschrieben und kennt ihn nicht. (3) Die hoechste vergebene
          Pruefpunktnummer war 27 (Nachtrag V) — ausgezaehlt, nicht geschaetzt.
NAECHSTER: director (vier offene Fragen, davon eine terminkritisch: OF-19),
           danach developer (T-048)
BLOCKIERT DURCH: nichts
```

---

## 0. Der Entwurf in fuenf Zeilen

1. **AD-025** trennt Vorbehalte in zwei Klassen und macht die Klasse zu einer
   Eigenschaft des **Wohnorts** statt des Satzes: **Verfahrenssatz** (vor dem
   Lauf schreibbar) wohnt in der Registry (`Goal.scope`, neu), **Laufbefund**
   (braucht den Lauf) wohnt im Ergebnis (`*.unknowns`). Die Registry hat
   keinen Lauf; das Ergebnis gibt es ohne Lauf nicht. Damit kann kein Satz
   mehr in der falschen Klasse landen, ohne dass es auffaellt.
2. **Ergebnisform:** `Baseline` wird die Zeile, die ein Pool ueber eine
   Zielrichtung weiss — `goal_id`, `value` (Bestand) plus `unit`, `unknowns`,
   `weights_note`. Kein neuer Typ, kein `GoalScore` im Pool, keine zweite
   Darstellung einer Zahl. `SlotPool.unknowns` bekommt einen zweiten
   Erzeuger: die konditionale Zeile aus D2.
3. **AD-004** praezisiert: seine „immer mindestens"-Liste ist ab jetzt die
   Liste von `Goal.scope`; die konditionale Zeile entsteht in
   `candidates.pool()`, gezaehlt ueber die Kandidaten **dieses** Pools und
   gebildet aus dem `Build`, nicht aus den Relikt-Definitionen.
4. **AD-010** praezisiert: „Pflichtfeld im Ergebnis" heisst „jeder Laufbefund
   faehrt mit und darf leer sein"; die Zusage „es steht immer etwas da"
   wandert auf `Goal.scope` und wird damit **ohne Spielinstallation**
   pruefbar (QA-106). AK-50 ist nicht die von AD-010 verworfene Option A.
5. **AD-016** praezisiert: der Schluessel ist der `AdvisorRequest`,
   positionsabhaengig; **`held_fingerprint` wird gestrichen**, samt Waechter.
   **AD-009**: die doppelt vergebene Pruefpunktnummer 18 ist aufgeloest.

Ort: `ARCHITECTURE.md`, Nachtrag VI (ab Zeile 2867, AD-025 ab 2883), Uebersicht der neuen
Nummern in Abschnitt 4 dieses Berichts.

---

## 1. „Was wird heute falsch" — die Arbeitsanweisung fuer T-048

Stand, an dem ich gemessen habe: Branch `docs/audit-and-advisor-design`,
`tests/test_advisor_{types,goals,candidates,evaluate}.py` **93 passed** in
5,3 s (selbst gefahren, 05.09.2026). Alle Zeilennummern unten sind von diesem
Stand.

### 1.1 `nrplanner/advisor/goals.py`

| Stelle | Was heute dasteht | Was daraus wird |
|---|---|---|
| Z. 4-6 (Modul-Docstring) | „Each entry below therefore hands back a `GoalScore` whose `unknowns` is never empty" | **falsch nach AD-025.2.** Nicht leer ist ab jetzt `Goal.scope`. Der Satz wird umgeschrieben, nicht geloescht — die Begruendung (A7) bleibt, der Ort wechselt. |
| Z. 97-107 `_ATTACK_RATING_UNKNOWNS` | vier Saetze, an `GoalScore.unknowns` gehaengt | zieht nach `MAX_DAMAGE.scope`. Der Kommentarblock Z. 82-96 begruendet die beiden Ersetzungen (QA-095, QA-099) und **bleibt woertlich** — er ist die Herleitung, nicht der Satz. |
| Z. 115-127 `_DAMAGE_TAKEN_UNKNOWNS` | vier Saetze | zieht nach `MIN_DAMAGE_TAKEN.scope`. |
| Z. 108-110 `_NO_ARMAMENT` | in `unknowns`, nur ohne Referenzwaffe | **bleibt in `unknowns`** und ist ab jetzt der Musterfall der Klasse „Laufbefund". Nicht anfassen. |
| Z. 111-113 `_NO_ARMAMENT_NOTE` | in `weights_note` | bleibt. `weights_note` ist Laufbefund (AD-025.3). |
| Z. 165 `unknowns = _ATTACK_RATING_UNKNOWNS` | Vorbelegung beider Zweige | entfaellt. Der Zweig ohne Waffe liefert `(_NO_ARMAMENT,)`, der mit Waffe `()`. |
| Z. 175, 196, 244 `unknowns=…` | drei Aufrufstellen | nachziehen. |
| Z. 249-261 `MAX_DAMAGE` / `MIN_DAMAGE_TAKEN` | Registry-Eintraege ohne `scope` | bekommen `scope=…`. |

### 1.2 `nrplanner/advisor/types.py`

| Stelle | Was heute dasteht | Was daraus wird |
|---|---|---|
| Z. 234-236 (`GoalScore`-Docstring) | „`unknowns` is not optional and is never empty (AD-010, `GOAL.md` A7)" | **falsch nach AD-025.** Der Satz nennt die Zusage am falschen Ort. |
| Z. 243 `unknowns: tuple[str, ...]` | ohne Vorgabewert | bekommt `= ()`. |
| Z. 248ff `class Goal` | vier Felder | bekommt `scope: tuple[str, ...]`. Der Docstring muss sagen, **warum** `scope` hier und nicht in `GoalScore` liegt: weil die Registry keinen Lauf sieht. |
| Z. 328ff `class Baseline` | „Kept apart from `Marginal` … one is an absolute value and the other a difference" | Docstring erweitern, drei Felder dazu (`unit`, `unknowns`, `weights_note`). Die Trennung von `Marginal` bleibt die Begruendung — sie zielt auf Wert gegen Differenz, nicht auf Text. |
| Z. 392-395 (`SlotPool`-Docstring) | „the guarantee that a goal always says something is on `GoalScore`, not here" | **falsch nach AD-025.** Die Garantie liegt auf `Goal.scope`. |
| Modul-Docstring, „the cache key … is the request object itself — there is **no second key form** that could drift" | heute **falsch**, weil `held_fingerprint` existiert (QA-107) | wird durch das Streichen **wahr**. Der Docstring soll ausdruecklich sagen, dass der Haltezustand ueber `problem` im Schluessel steht. |
| Z. 65 (`Slot`-Docstring) | „the problem-wide flag AD-016 puts in the cache key is the set of `(colour, deep)` pairs of the free slots" | beschreibt die **kanonische Form**, die es nicht gibt und nach D3 nicht geben wird. Nachziehen. |
| Z. 206-220 `AdvisorRequest.held_fingerprint` (Property) | „the one property on any dataclass in this module" | **entfaellt**. Damit stimmt auch der Satz „this is the one property" nicht mehr — er faellt mit. |
| Z. 520-554 `held_fingerprint` (freie Funktion) | positionsunabhaengig, `repr`-Sortierung | **entfaellt**. Der `repr`-Kommentar (die `None`-gegen-`int`-Falle) ist eine echte Einsicht und gehoert in den neuen Testfall zu Pruefpunkt 34, nicht in den Papierkorb. |

### 1.3 `nrplanner/advisor/candidates.py`

| Stelle | Was heute dasteht | Was daraus wird |
|---|---|---|
| Z. 123-124 | `baseline = {goal_id: goal.score(base_build, ctx).value …}` — **das ist QA-102** | den ganzen `GoalScore` behalten, nicht nur `.value`. |
| Z. 149-151 | `types.Baseline(goal_id, value)` | `types.Baseline(goal_id, score.value, score.unit, score.unknowns, score.weights_note)`. |
| Z. 145-146 | `unknowns` = nur die Handle-Zeile | plus die konditionale Zeile, wenn der Pool welche traegt. |
| neu, neben Z. 83 `_without_a_handle_line` | — | `_conditional_line(count)`. Der Zaehler kommt aus `Build.situational` mit `live == False` (model.py:694-712), **nicht** aus einer zweiten Ableitung ueber `model.is_conditional` — der Waffentyp wird heute in `model.compute` (model.py:807-811) abgeleitet, und eine zweite Ableitung ist eine zweite Meinung darueber, was gezaehlt wurde. |

**Unabhaengig nachgeprueft, dass die Zeile wirklich fehlt** (zwei verschieden
formulierte Suchen, beide 0 Treffer): `grep -rni "not counted" nrplanner/`
und `grep -rni "only apply|under a condition|situational" nrplanner/advisor/`.
Dritte Probe: `is_conditional` und `situational` werden aus `advisor/`
**nirgends** aufgerufen — der Berater fragt heute ueberhaupt nicht nach
konditionalen Effekten.

### 1.4 Tests

| Datei / Fall | Heute | Nach T-048 |
|---|---|---|
| `test_advisor_goals.py` Modul-Docstring Z. 5 und Z. 21-23 | „no goal ever hands back an empty `unknowns`" / „every score carries the scope … in its `unknowns`" | beide Saetze werden falsch; die Aussage wandert auf `Goal.scope`. |
| `test_advisor_goals.py:71` `test_no_goal_hands_back_an_empty_unknowns` | `assert score.unknowns` | **wird falsch.** Ersetzen durch Pruefpunkt 29: `GOALS[id].scope` nicht leer, **ohne** `game_data` — der Fall laeuft dann auf jedem Runner (QA-106). Der zweite Teil (`assert score.display`) bleibt. |
| `test_advisor_goals.py:101` `test_the_damage_goal_always_carries_the_attack_rating_reservation` | liest `.score(build, context).unknowns` (Z. 131) | Quelle wechselt auf `GOALS["max_damage"].scope`. **Alle acht Assertions bleiben inhaltlich unveraendert** — sie sind der wertvollste Teil dieses Falls (QA-095/QA-099-Historie) und duerfen dabei nicht verduennt werden. Der Fall braucht danach kein `game_data` mehr; wird er dadurch runnerfaehig, ist das ein Gewinn gegen QA-106 und gehoert in den Commit-Text. |
| `test_advisor_goals.py:225` `test_without_an_armament_the_damage_goal_says_so` | `assert any("No armament selected" in line for line in bare.unknowns)` | **bleibt gruen und wird zum Beleg**, dass `_NO_ARMAMENT` Laufbefund ist. Nicht anfassen. |
| `test_advisor_candidates.py:129` `test_nothing_left_out_says_nothing` | `assert pool_for(...).unknowns == ()`; Docstring: „The guarantee that a run always says something is on `GoalScore`" | Docstring wird falsch. Die Assertion gilt nur, **solange der Bestand des Falls keine konditionalen Effekte traegt** — das muss der Fall aussprechen und pruefen, sonst ist er zufaellig gruen. |
| `test_advisor_types.py:182` `test_where_a_relic_is_held_does_not_change_the_fingerprint` | sichert eine Eigenschaft, die der Schluessel nicht hat (QA-107) | **entfaellt vollstaendig.** |
| `test_advisor_types.py:163` `test_two_requests_that_differ_only_in_what_is_held_are_different_keys` | drei Assertions, die letzte ueber `held_fingerprint` | letzte Zeile faellt weg; die ersten beiden werden **der** Waechter fuer AD-016.2. Zusaetzlich ein Paar, das sich nur im **Slot** des Halts unterscheidet (Pruefpunkt 34) — das ist der Fall, den D3 verlangt und den es heute nicht gibt. |
| `test_advisor_types.py:199` `test_a_slot_held_empty_is_not_the_same_question_as_a_free_slot` | letzte Zeile ueber `held_fingerprint` | ersetzen durch denselben Vergleich auf `AdvisorRequest`-Ebene. Ohne das verliert der Fall seine Aussage ueber den Schluessel. |
| `test_advisor_types.py:215` `test_a_custom_relic_held_beside_an_owned_one_still_fingerprints` | sichert, dass ein gehaltenes Custom-Relikt (`handle=None`) den Fingerabdruck nicht sprengt | **echte Zusicherung, darf nicht mit dem Fingerabdruck verschwinden.** Umhaengen auf `hash(AdvisorRequest)` mit gehaltenem Custom-Relikt. Das ist die Stelle, an der beim Streichen still etwas verlorengeht. |
| `test_advisor_types.py` `SAMPLES` (Z. 55ff) | eine Instanz je Dataclass, Hashbarkeit ueber alle | `Baseline` mit **gefuellten** neuen Feldern in das Sample, nicht mit den Vorgabewerten — sonst belegt der Hashbarkeitsfall die neuen Felder nicht. `Goal` bekommt `scope`. |

### 1.5 `ARCHITECTURE.md` — erledigt, nicht Aufgabe des `developer`

Nachtrag VI ist geschrieben. Zusaetzlich in dieser Sitzung nachgezogen:
Pruefpunkt 18 → 28 an drei Stellen (Nachtrag III Z. 2650 und die zwei
Verweise Z. 2671/2708) und das seit QA-095 falsche Zitat in AD-004 (Z. 513)
als **historisch** markiert statt geloescht — QA-116 zeigt genau darauf.

### 1.6 Reihenfolge, in der ich es bauen wuerde

1. **`Goal.scope` einfuehren und die acht Saetze umhaengen** (goals.py,
   types.py). Danach ist die Suite rot an genau zwei Faellen — das ist der
   Rot-vorher-Beleg, dass die Trennung wirkt. **Zuerst rot sehen, dann die
   Faelle umschreiben.**
2. **Die zwei Faelle umschreiben** (Pruefpunkte 29, 30, 31).
3. **`Baseline` erweitern und `pool()` nachziehen** (Pruefpunkt 32). Fuer
   sich lauffaehig und fuer sich pruefbar.
4. **Die konditionale Zeile** (Pruefpunkt 33). Braucht 3, nicht umgekehrt.
5. **`held_fingerprint` streichen**, drei Testfaelle umhaengen oder loeschen
   (Pruefpunkt 34). Unabhaengig von 1-4; kann auch zuerst laufen.

Schritt 5 beruehrt keinen der Schritte 1-4 und umgekehrt. Wer teilen will,
teilt hier.

---

## 2. Meine Entscheidung zu `held_fingerprint`: gestrichen, nicht positionsabhaengig gemacht

Der `director` hat mir die Wahl gelassen. Ich streiche ihn — Funktion,
Property und Waechter.

1. **Er waere eine zweite Schluesselform.** Der Modul-Docstring von
   `advisor/types.py` verbietet genau das, mit ausgeschriebener Begruendung:
   *„there is no second key form that could drift from the state it stands
   for."* Dieser Satz ist **heute falsch**, weil der Fingerabdruck dasteht.
   Streichen macht ihn wahr; positionsabhaengig machen liesse ihn falsch und
   fuegte eine ableitbare Kopie hinzu, die niemand liest.
2. **Er hat keinen Leser und bekommt keinen.** Der Cache schluesselt auf den
   Request (AD-018: „Es entsteht keine zweite Schluesselform"). Der
   Generationszaehler (AD-016.3) braucht nur „ist der Request ein anderer";
   `SlotProblem` ist eine gefrorene Datenklasse und vergleicht sich selbst.
3. **Er ist eine Falle.** Solange er dasteht und behauptet, zwei
   Haltezustaende seien dasselbe, benutzt ihn irgendwann jemand fuer etwas
   Schluesselartiges — und dann tritt genau der Fehler ein, gegen den D3
   geschrieben ist. Ein positionsabhaengiger Fingerabdruck waere keine Falle
   mehr, aber auch kein Nutzen.

**Was ich dabei nicht uebersehe:** der Fall
`test_a_custom_relic_held_beside_an_owned_one_still_fingerprints` sichert
etwas Reales — dass ein gehaltenes Custom-Relikt (`handle=None`) neben einem
besessenen (`handle=int`) den Schluessel nicht sprengt. Python weigert sich,
`None` gegen `int` zu ordnen; der `repr`-Sortierschluessel im Fingerabdruck
war die Antwort darauf. Faellt der Fingerabdruck, faellt das Problem mit ihm
weg (ein Tupel gefrorener Datenklassen wird nicht sortiert, nur gehasht) —
aber die **Zusicherung** darf nicht mitfallen. Sie wird auf
`hash(AdvisorRequest)` umgehaengt. Das steht als Risikozeile in Nachtrag VI
und als Pruefpunkt 34.

**Rueckweg, benannt:** braucht S9 doch eine kanonische Form, wird sie dort
gebaut — positionsabhaengig, mit Rueckabbildung, und der Waechter zeigt dann
auf den **Schluessel**, nicht auf den abgeleiteten Wert. Zwoelf Zeilen.

---

## 3. Wo D1 bis D4 im Kontakt mit dem echten Code nicht aufgehen

Das entscheidet der `director`, nicht ich. Ich habe im Entwurf jeweils die
Lesart gewaehlt, die ich unten begruende, und sie ist umkehrbar.

### 3.1 D1s Massstab, woertlich genommen, sortiert `_NO_ARMAMENT` falsch ein

*„Kann der Satz geschrieben werden, bevor der Lauf bekannt ist?"* — *„No
armament selected — ranked on attack multipliers only, without weapon
scaling."* laesst sich woertlich vor jedem Lauf aufschreiben. Nach dem
Buchstaben des Massstabs ist er damit **statisch** und stuende dann auch da,
wenn eine Waffe gewaehlt ist. Das ist offensichtlich nicht gemeint.

**Was ich getan habe:** den Massstab um vier Worte erweitert — der Wortlaut
**und die Frage, ob er gilt**, muessen aus der Registry folgen. Damit ist
`_NO_ARMAMENT` Laufbefund, und `test_without_an_armament_the_damage_goal_says_so`
(heute gruen) wird zum Beleg dafuer. Betrifft ausserdem `weights_note`
(zwei moegliche Wortlaute, die Auswahl trifft der Lauf) und QA-104.

### 3.2 D1s Trennung braucht einen Ort fuer die statische Haelfte, und der Bestand hat keinen

D1 sagt, die statischen Saetze stehen „einmal je Bildschirm … **nicht je
Karte und nicht je Pool**". Damit duerfen sie nicht in `SlotPool` fahren.
Sie stehen heute aber ausschliesslich in `GoalScore`, und einen `GoalScore`
gibt es nur, wenn ein Build bewertet wurde. Die Oberflaeche haette also
keinen Weg, an sie heranzukommen, ohne zu rechnen — ausser ueber die
Registry. Deshalb `Goal.scope`. Das ist **mehr**, als D1 woertlich verlangt
(D1 spricht nur vom `SlotPool`), und es ist die Stelle, an der ich den
Auftrag am weitesten ausgelegt habe.

**Gegenprobe, falls der `director` es enger will:** dann muessten die vier
Saetze doch in jedem Pool mitfahren, und „nicht je Pool" faellt. Ich halte
das fuer falsch, sage es aber, weil es die eine Alternative ist.

### 3.3 D3s Begruendung ist zu eng; die Entscheidung ist trotzdem richtig

D3 begruendet die Positionsabhaengigkeit damit, dass *„die Slots
verschiedene Farben tragen und die Menge der freien Slots eine andere ist"*.
Beides traegt nicht:

- Der Fall setzt voraus, dass **dasselbe** Relikt in beide Slots passt — also
  tragen sie in aller Regel **dieselbe** Farbe (oder einer ist weiss).
- Die Menge der freien Slots waere unter der Kanonisierung aus AD-008 (nach
  Farben sortiert) gerade **gleich**. Genau dafuer gibt es sie.

**Der tragende Grund ist ein anderer und staerker: die Antwort traegt
Slotindizes** (`SlotChoice.slot_index`, `Candidate.slot_index`,
`SlotPool.slot_index`). Ein Treffer ueber eine Permutation gaebe eine
Antwort zurueck, deren Indizes auf die Slots des *anderen* Problems zeigen.
Das geradezuziehen ist die Rueckabbildung aus AD-016.4 — die niemand gebaut
hat. Solange sie fehlt, ist jeder positionsunabhaengige Treffer ein
ueberschriebener Halt. **Die Entscheidung ist richtiger als ihre
Begruendung**, dieselbe Lage wie bei QA-101. Ich habe die Begruendung im
Nachtrag ersetzt, nicht die Entscheidung.

### 3.4 D3 loest AD-008 fuer den Schluessel ab — das steht in D3 nicht drin

AD-008 hat entschieden, ein Suchproblem ueber die **kanonisierte
Slot-Farbmenge** zu schluesseln statt ueber das Gefaess, mit einer gemessenen
Zahl (74 Gefaesse → 26 bzw. 47 Muster). D3 macht den Request zum Schluessel;
damit ist diese Entscheidung fuer den Cache abgeloest und der Trefferanteil
entfaellt. Ich halte das fuer tragbar (der Hauptweg nach AD-018 erzeugt
ohnehin je Slot einen eigenen Eintrag) und habe es als Ablösung ausdruecklich
in den Nachtrag geschrieben. **AD-008s zweites Argument — die Prueflast fuer
A3 ueber 26/47 statt 74 Probleme — haengt nicht am Cache und bleibt nach
meiner Lesart stehen.** Wenn der `director` das anders sieht, ist der
Pruefumfang fuer A3 neu zu bemessen (OF-22).

### 3.5 D4: die Nummer 18 kann nicht schadlos umgehaengt werden, nur ausgewaehlt

Die Kollision betrifft **nur** die 18 (Nachtrag II vergibt 15-18, Nachtrag
III 18-22; 19-22 sind kollisionsfrei). Auf „Pruefpunkt 18" zeigen **sechs**
Stellen im Baum, und sie zeigen auf **beide** Bedeutungen:
`ARCHITECTURE.md` 2×, `docs/tasks/T-027.md`, `T-029.md`, `T-030.md` und
`qa/findings.md:795` meinen Nachtrag IIIs 18 (untere Schicht bitgleich);
`qa/findings.md:1470` (QA-110) und `docs/berichte/T-041-qa-engineer.md` 3×
meinen Nachtrag IIs 18 (kein `QSettings`). Es gibt keine Wahl, die alle
Verweise richtig laesst.

**Meine Wahl, mit zwei unabhaengigen Gruenden, die auf dasselbe zeigen:**
18 bleibt beim **QSettings**-Punkt — er hat den ersten Anspruch (Nachtrag II
steht vor Nachtrag III), **und** er ist der einzige der beiden, der noch
**offen** ist (QA-110 zeigt auf ihn und geht an den `developer`). Nachtrag
IIIs Punkt ist erledigt (W0-W5 sind gebaut); seine Verweise sind Verlaeufe
passierter Tore. Er wird **Pruefpunkt 28**.

### 3.6 Ausserhalb von D1-D4, aber im Weg: `UI_SPEC` AK-63 ist zwei Tage juenger als T-047

Der `ui-ux-designer` hat am 05.09.2026 entschieden (Nachtrag zu QA-116),
dass Zeile 4 des Pickers und Punkt 4 des Why-Dialogs **ausschliesslich** die
Saetze aus `GoalScore.unknowns` zeigen. Nach AD-025 sind es **zwei** Quellen.
Die **Absicht** von AK-63 bleibt vollstaendig erfuellbar — sein eigener
Pruefsatz („ein fuenfter Satz in `advisor/goals.py` erscheint danach an beiden
Anzeigeorten, ohne dass ein UI-String angefasst wurde") gilt unveraendert,
wenn der fuenfte Satz in `Goal.scope` steht. Der **Wortlaut** nennt eine
Quelle, wo es zwei gibt.

**Das ist der einzige Punkt dieses Auftrags, der A7 verschlechtern kann:**
wird AK-63 nicht nachgezogen, zeigt eine spec-treue Umsetzung nach der
Trennung **weniger** als heute — Zeile 4 waere leer bis auf die
AD-018.3-Pflichtzeile. Siehe OF-19; das ist die eine Frage mit Termin.

### 3.7 Eine Luecke, die QA-102 nahelegt und die T-048 nicht schliessen soll

QA-102 meldet, dass auch `display` an der Poolgrenze wegfaellt. Das ist
richtig und trotzdem kein Auftrag: `display` formatiert den **Absolutwert des
Grundzustands**, der Picker zeigt eine **Differenz** (`+12.4 AR` gegen `−18`).
Fuer die Formatierung einer Differenz je Zielrichtung gibt es heute **nirgends**
eine Regel — auch `unit` reicht nicht, weil die Nachkommastellen je
Zielrichtung verschieden sind (`UI_SPEC` §3.3). Ich habe `display`
ausdruecklich aus der Poolgrenze herausgehalten und die Luecke benannt; sie
gehoert zu S8/S10 und zum `ui-ux-designer`. OF-21.

---

## 4. Die neuen Nummern

| Nummer | Was |
|---|---|
| **AD-025** | Verfahrenssatz gegen Laufbefund; die Frage entscheidet, der Ort traegt die Klasse |
| **Pruefpunkt 18** | unveraendert: „Kein `QSettings`-Zugriff im Berater-Pfad" (Nachtrag II). QA-110 zeigt weiterhin richtig darauf. |
| **Pruefpunkt 28** | **neu vergeben** an „Untere Schicht bitgleich ueber den ganzen Umbau" (bisher Nachtrag IIIs 18) |
| **Pruefpunkt 29** | jede Zielrichtung hat einen nicht leeren `Goal.scope` — **ohne Spielinstallation** pruefbar |
| **Pruefpunkt 30** | kein Satz steht in beiden Klassen |
| **Pruefpunkt 31** | ein Laufbefund ueberlebt nicht jeden Lauf (Durchschnitt ueber zwei Kontexte leer) |
| **Pruefpunkt 32** | der Pool traegt, was die Zielrichtung nicht wusste — der Waechter ueber QA-102 |
| **Pruefpunkt 33** | die konditionale Zeile zaehlt, was wirklich nicht gezaehlt wurde |
| **Pruefpunkt 34** | der Haltezustand ist im Schluessel, ohne zweite Form — ersetzt den Waechter ueber `held_fingerprint` |
| **Nicht-tun 33-38** | siehe Abschnitt 5 |
| **OF-19 bis OF-22** | siehe Abschnitt 6 |

Jeder der sechs neuen Pruefpunkte traegt im Nachtrag seinen **Gegenbau**
(L-002). Pruefpunkte 29 und 30 laufen ohne Spielinstallation und sind damit
die ersten Advisor-Faelle, die auf einem nackten Runner etwas belegen —
Pruefpunkt 31 und 33 tun es nicht und sagen es (QA-106, stehende
Einschraenkung).

---

## 5. Was der `developer` ausdruecklich **nicht** tun soll

33. **`GoalScore.display` nicht in den Pool durchreichen.** Es formatiert den
    Absolutwert des Grundzustands; der Picker zeigt eine Differenz.
34. **`GoalScore.unknowns` nicht umbenennen** und `Baseline` nicht durch einen
    neuen per-Ziel-Typ ersetzen. Beides zieht `UI_SPEC` AK-63 und drei
    Testdateien mit, ohne etwas zu gewinnen.
35. **Kein `dict` und kein `list` in den neuen Feldern** (QA-066,
    Modul-Docstring).
36. **Keine zweite Ableitung des Waffentyps** fuer `model.is_conditional` in
    `candidates.py`. Die Zahl muss beschreiben, was `model.compute`
    tatsaechlich weggelassen hat.
37. **`held_fingerprint` nicht „vorsichtshalber" stehenlassen**, auch nicht
    als private Funktion. Die drei Faelle werden umgehaengt oder geloescht,
    nicht deaktiviert.
38. **Den Wortlaut der konditionalen Zeile nicht als endgueltig setzen.** Er
    gehoert dem `ui-ux-designer` (OF-20).

Ausserdem, aus dem Auftrag uebernommen und hier bestaetigt: **keine Zahl,
keine Zielfunktion, kein Schwellenwert.** Dieser Nachtrag aendert Form und
Text; der Rechenkern rechnet danach dasselbe wie davor.

---

## 6. Offene Fragen

**OF-19 — an den `director`, weiterzugeben an den `ui-ux-designer`.
Terminkritisch: vor S10.** `UI_SPEC` AK-63 nennt `GoalScore.unknowns` als
einzige Quelle der Vorbehaltszeile; nach AD-025 sind es zwei (`Goal.scope`
plus die Laufbefunde des Pools). Absicht erfuellbar, Wortlaut nicht. Wird
AK-63 nicht nachgezogen, zeigt der Picker nach T-048 **weniger** als heute.

**OF-20 — an den `ui-ux-designer`, ueber den `director`.** Wortlaut der
konditionalen Zeile: AD-004 sagt „N of your relics", gezaehlt wird ueber die
Kandidaten **dieses Pools**. Gehoert in dieselbe Runde wie QA-108 („of this
colour" stimmt am weissen Slot nicht) — zwei Zeilen desselben Bautyps im
selben Feld.

**OF-21 — an den `director`.** Die Formatierung einer **Differenz** je
Zielrichtung hat heute nirgends einen Ort. Ich lese sie als S8/S10 und
ausdruecklich **nicht** als Teil von T-048. Bestaetigung erbeten, weil
QA-102 „`display` faellt weg" meldet und der naechstliegende Griff der
falsche waere.

**OF-22 — an den `director`.** AD-008 hatte zwei Argumente: Trefferquote im
Cache **und** Prueflast fuer A3 (26/47 statt 74 Probleme). D3 hebt das erste
auf; ich lese das zweite als unberuehrt. Sieht der `director` das anders,
trifft es den `qa-engineer`, nicht den `developer`.

---

## 7. Was ich **nicht** geprueft und **nicht** entschieden habe

- **Ob `Build.situational` mit `live == False` die richtige Menge ist**, habe
  ich aus `model.py` (Z. 694-712, Z. 892, Z. 1097-1110) **gelesen**, nicht
  gegen einen Lauf **gemessen**. Der Geltungsbereich steht im Nachtrag:
  `situational` fuehrt nur Bedingungen, die der Spieler erklaeren kann —
  nicht den an einer nicht getragenen Waffenklasse haengenden Effekt (das ist
  QA-104 mit eigener Zeile). Stimmt das nicht, faellt Pruefpunkt 33 und der
  `developer` meldet es, statt die Menge stillschweigend zu erweitern.
- **QA-113** (die vier Relikte, die die Angriffskraft um exakt 0 bewegen)
  habe ich nur als **Anwendungsfall der Regel** eingeordnet: der
  Verfahrenssatz („flache `*AttackPower`-Felder gehen in diese Zahl nicht
  ein") gehoert nach `Goal.scope`, die Anzahl in den Pool. Die **Einbauhoehe**
  haengt an einer Messung des Nutzers (F-F) und ist nicht meine.
- **QA-100** (Pruefpunkt 13 faengt seine Gegenbauten nicht), **QA-101** (der
  Begruendungstausch in `mutate.py`), **QA-103 bis QA-106**, **QA-108 bis
  QA-112**: nicht beauftragt, nicht bearbeitet. **QA-101 beruehrt keine
  meiner Praezisierungen** — `damage.equipped` bleibt, der Docstring von
  `_max_damage` (goals.py Z. 122-140) begruendet die Wahl heute korrekt ueber
  AD-020.3 und AD-014.6 und ist von der falschen `survival_means`-Begruendung
  in `mutate.py` nicht beruehrt. Ich habe ihn gelesen und nichts daran zu
  aendern gefunden.
- **Die Suite habe ich nicht vollstaendig gefahren**, nur die vier
  Advisor-Dateien (93 passed). Die im Auftrag genannten 563 passed habe ich
  **nicht** nachgeprueft.
- **Kein Anwendungscode, kein Test, keine schreibende Git-Operation.** Fremde
  ungespeicherte Dateien (`docs/state.md`, `qa/findings.md`, `UI_SPEC.md`,
  `DESIGN_REVIEW.md`, andere Berichte) sind unberuehrt. Gegenprobe:
  `git status --short` zeigt dieselben vier fremden `M`-Eintraege wie beim
  Beginn dieser Sitzung (`DESIGN_REVIEW.md`, `UI_SPEC.md`, `docs/state.md`,
  `qa/findings.md`) — ich habe keine davon angefasst. Von mir stammen genau
  zwei Aenderungen: `ARCHITECTURE.md` (+628/-6) und diese Berichtsdatei.
