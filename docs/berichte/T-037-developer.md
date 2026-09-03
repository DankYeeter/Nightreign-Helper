# T-037 — developer

```
STATUS: erledigt
AUFTRAG: T-037 — P3-a: Der Rechenkern des Beraters (S4, S4+, S4b, S5, S5+, S5++, S6)
GELESEN: docs/tasks/T-037.md · GOAL.md (A3-A9, F1-F4, OF-12, OF-13, OF-15) ·
  ARCHITECTURE.md (AD-001 bis AD-006, AD-010 bis AD-024, Schritttabelle,
  Nachtraege I bis V) · docs/state.md · docs/plan-restarbeiten.md ·
  UI_SPEC.md (§3.1 bis §3.4, AK-41 bis AK-62) · qa/findings.md (QA-001,
  QA-018, QA-023, QA-061, QA-064, QA-066, QA-069 bis QA-075, QA-079,
  QA-083 bis QA-088) · README.md (Known limits) · nrplanner/damage.py ·
  nrplanner/model.py · nrplanner/inventory.py · nrplanner/app.py
  (_rebuild, selected_effects, selected_curses, weapon_effects,
  equipped_weapons, RelicSlot) · nrplanner/weaponslots.py ·
  nrdata/savefile.py (read_relic_handles) · tests/test_one_build.py ·
  tests/test_marginal_returns.py · tests/conftest.py · tests/relics.py ·
  tests/weapon_damage_cases.py · tests/test_differential_track.py ·
  scripts/differential/mutate.py
GEÄNDERT: nrplanner/advisor/__init__.py · nrplanner/advisor/types.py ·
  nrplanner/advisor/evaluate.py · nrplanner/advisor/candidates.py ·
  nrplanner/advisor/goals.py · tests/advisor_cases.py ·
  tests/test_advisor_types.py · tests/test_advisor_evaluate.py ·
  tests/test_advisor_candidates.py · tests/test_advisor_goals.py ·
  tests/test_one_build.py · scripts/differential/mutate.py ·
  scripts/measure_advisor_picker.py · docs/berichte/T-037-developer.md
  (Commits 64174eb, 3350172, 690db5f auf docs/audit-and-advisor-design;
  der Messskript- und Berichts-Commit folgt als vierter)
ANNAHMEN: sechs, alle unten unter „Annahmen über die Spieldaten" einzeln
  aufgeführt — die beiden tragenden sind die Formel für effektives HP
  (HP geteilt durch die Schadensdurchlassrate, acht Arten gleich gewichtet)
  und die Ersatzgrösse ohne Referenzwaffe (Mittel der fünf
  Angriffsmultiplikatoren).
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

---

## Umgesetzt

`nrplanner/advisor/` existiert als reines, Qt-freies Paket mit vier Modulen.
Nach diesem Auftrag rechnet ein Test für einen bekannten Build und einen
bekannten Slot den Grenzbeitrag jedes besessenen Kandidaten unter **beiden**
Zielrichtungen aus. Keine Suche, keine Erklärung, kein Thread, keine
Oberfläche.

| Datei | Zeilen gesamt | davon Code | Inhalt |
|---|---|---|---|
| `nrplanner/advisor/__init__.py` | 56 | 23 | öffentliche Namen, Abhängigkeitsrichtung |
| `nrplanner/advisor/types.py` | 577 | 133 | 19 `frozen` Datenklassen, 6 freie Nachschlagefunktionen |
| `nrplanner/advisor/evaluate.py` | 122 | 41 | die **einzige** Stelle mit `model.compute` |
| `nrplanner/advisor/candidates.py` | 191 | 64 | `pool`, `pools`, `shortlist`, `base_state_for` |
| `nrplanner/advisor/goals.py` | 235 | 94 | Registry + `max_damage`, `min_damage_taken` |

(Zeilen mit `ast`/`tokenize` gezählt, Docstrings und Kommentare abgezogen.
AD-001 nennt „jede Datei unter 250 Zeilen" als Folge des Paketschnitts —
gemessen an Codezeilen hält das, an Gesamtzeilen nicht, weil dieses Projekt
seine Begründungen in den Docstrings führt. Das ist eine bewusste Fortsetzung
der Hausform, keine Abweichung, die ich still getroffen habe.)

**Was wo steht**

- **S4 / S4+ — `types.py`.** `Slot`, `HeldRelic`, `HeldSlot`, `SlotProblem`,
  `ArmamentRef`, `Budget`, `AdvisorRequest` (die Frageform) · `GoalScore`,
  `Goal`, `Weighting`, `Baseline`, `Marginal`, `Candidate`, `SlotPool`,
  `SlotChoice`, `Suggestion`, `AdvisorResult` (die Antwortform) ·
  `ReferenceArmament`, `GoalContext` (die zwei benannten Kontexttypen). Der
  Haltezustand steckt als `SlotProblem.held` im `AdvisorRequest`, sein
  Fingerabdruck als **abgeleitete** Eigenschaft `AdvisorRequest.held_fingerprint`
  (Begründung unten). `AdvisorResult` trägt Grundzustandswert (`baseline`),
  Zugewinn (`gain`) und die festgehaltenen Slots (`held`).
- **S4b — `evaluate.py`.** `evaluate(problem, assignment, ctx) -> model.Build`
  plus `effect_ids_of`. Die `compute`-Wächtererwartung ist um **genau einen**
  Eintrag gewachsen: `{"nrplanner/app.py": 1, "nrplanner/advisor/evaluate.py": 1}`.
  `evaluate` weist eine Zuweisung auf einen **gehaltenen** Slot zurück und
  zwei Kandidaten für **einen** Slot ebenfalls — die AD-014-Lesart
  „Randbedingung, nicht Startwert" wird an der einen Tür durchgesetzt statt an
  drei Stellen erinnert.
- **S5 / S5+ / S5++ — `candidates.py`.** `pool` liefert je Slot alle
  zulässigen Kopien mit ihrem Grenzbeitrag **unter allen** Zielrichtungen der
  übergebenen Registry, sortiert nach der genannten. Bezugsgrösse ist
  `base_state_for(problem, slot)` — der aktuelle Build mit **geleertem
  Zielslot**, auch für das Relikt, das darin steckt. Kein Rollen-Dedup;
  Farbregel und Deep-Trennung kommen aus `inventory.relics_for` (der weisse
  Slot zieht damit jede Farbe, ohne dass die Regel hier ein zweites Mal
  stünde); Kopien ohne Handle fliegen raus **und** stehen in `unknowns`;
  Handles der gehaltenen Relikte sind belegt. `shortlist` schneidet auf
  `K + (freie Slots − 1)` — als **Slice derselben Liste**, nicht als zweite
  Rechnung (Prüfpunkt 15).
- **S6 — `goals.py`.** `GOALS` als `MappingProxyType`, `max_damage` und
  `min_damage_taken`, beide mit nie leerer `unknowns`. `DEFAULT_WEIGHTING`
  ist Daten im `GoalContext`, nicht Konstanten in der Zielfunktion (OF-3
  bleibt ohne Registry-Umbau beantwortbar).
- **AD-015 / F3.** Flüche gehen als gewöhnliche Effekte in dieselbe
  `compute`-Liste wie die guten Rolls — es gibt unter `advisor/` keinen
  Fluch-Malus, kein Fluch-Gewicht, keinen Fluch-Sonderweg. Die Information
  für S8 geht nicht verloren: `evaluate` gibt den `Build` zurück, und
  `Build.sources` trägt die Fluchbeiträge mit Vorzeichen.
- **AD-023 / OF-13.** Zwei Zahlen je Kandidat, nie eine gewichtete.

**Nicht angefasst** (`git diff --stat 3650765..HEAD` belegt es): `damage.py`,
`model.py`, `inventory.py`, `app.py`, `relicpicker.py`, `weaponslots.py`,
keine Tab-Datei, `.gitignore` nicht, keine neue Abhängigkeit.

---

## 1. Je neuem Wächter die tötende Mutation und ihr Ergebnis

Alle Läufe: frische `git archive HEAD`-Extraktion des Commits **690db5f**,
`.venv\Scripts\python.exe -m pytest -q -m "not slow"` im extrahierten Baum.
Ungemutiert dort: **398 passed, 5 deselected**. Die Zeile
`test_every_mutation_still_finds_its_anchor_in_the_real_source[<name>]` fällt
bei jedem Lauf mit, weil die Mutation ihren eigenen Anker aus dem Baum nimmt;
sie ist unten nicht als Treffer gezählt.

| Mutation (in `scripts/differential/mutate.py`) | Ergebnis | Der Wächter, der sie tötet |
|---|---|---|
| `advisor-computes-in-a-second-place` | 3 failed, 395 passed | `test_one_build.py::test_the_user_interface_holds_exactly_one_call_to_compute` (+ `test_a_candidate_is_measured_against_the_held_build`) |
| `advisor-presorts-against-the-empty-build` | 4 failed, 394 passed | `test_a_candidate_is_measured_against_the_held_build` (+ 2) |
| `advisor-ranks-the-slot-as-it-stands` | 3 failed, 395 passed | `test_the_relic_in_the_slot_is_worth_what_it_actually_adds` (+ 1) |
| `advisor-offers-a-relic-without-a-handle` | 2 failed, 396 passed | `test_a_copy_without_a_handle_is_not_offered_and_is_reported` |
| `advisor-leaves-a-relic-out-without-saying-so` | 2 failed, 396 passed | dieselbe Zeile, andere Hälfte (die `unknowns`-Zusicherung) |
| `advisor-forgets-the-held-handles` | 3 failed, 395 passed | `test_a_held_copy_is_not_offered_a_second_time` (+ 1) |
| `advisor-scores-only-the-ranking-goal` | 2 failed, 396 passed | `test_every_candidate_carries_both_directions` |
| `advisor-marginals-as-a-mutable-map` | 2 failed, 396 passed | `test_a_pool_the_advisor_produced_can_be_a_cache_key` |
| `advisor-shortlist-without-room-for-the-others` | 3 failed, 395 passed | `test_the_shortlist_leaves_room_for_the_copies_the_other_slots_take` (+ Prüfpunkt 15) |
| `damage-goal-ranks-on-the-bare-figure` | 7 failed, 391 passed | `test_the_damage_goal_counts_the_attack_multipliers` (+ 4) |
| `damage-goal-asks-the-slotless-question` | 3 failed, 395 passed | `test_the_damage_goal_charges_the_starting_armament_penalty` |
| `advisor-goal-without-its-unknowns` | 2 failed, 396 passed | `test_no_goal_hands_back_an_empty_unknowns[min_damage_taken]` |
| `advisor-rates-an-armament-itself` | **1 failed**, 397 passed | `test_one_build.py::test_only_the_facade_calls_weapons_rate_or_rank` |
| `advisor-fingerprint-sorted-naturally` | 2 failed, 396 passed | `test_a_custom_relic_held_beside_an_owned_one_still_fingerprints` |
| `move-scope-list-emptied` (Bestand, T-036) | 7 failed, 391 passed | u. a. der **neue** `test_a_buff_the_game_restricts_to_one_move_is_worth_nothing_here` |

**Drei Punkte, die ich dazu ausdrücklich nennen muss:**

1. `advisor-computes-in-a-second-place` ist genau der in T-037 verlangte
   Gegenbau: ein zweiter `model.compute`-Aufruf an einer zweiten Stelle unter
   `advisor/` macht den Wächter rot. Er ist als **lokaler** Import geschrieben
   (`from .. import model` im Funktionskörper), weil das die Schreibweise ist,
   in der jemand ihn versehentlich nachrüsten würde — der Wächter sieht auch
   sie.
2. `advisor-rates-an-armament-itself` ist der Beleg dafür, dass der
   **AD-021-Wächter tatsächlich in das neue Paket hineinreicht**. `docs/state.md`
   hat das versprochen („greift automatisch, sobald `nrplanner/advisor/`
   existiert"); geprüft war es bis jetzt nicht. Er tötet **genau eine** Zeile
   und sonst nichts — schärfer geht es nicht.
   Die Mutation ist bewusst eine **Referenz** (`_own_arithmetic = weapons.rate`)
   und kein Aufruf: ein Aufruf würde den Lauf abstürzen lassen und damit etwas
   anderes belegen als das, worum es geht.
   Nebenbefund: `test_every_mutation_still_finds_its_anchor_in_the_real_source`
   fällt für **diese** Mutation nicht mit, weil ihr `new` den Anker enthält
   statt ihn zu ersetzen. Das ist korrekt und kein Loch — der Anker ist danach
   weiterhin genau einmal da.
3. `move-scope-list-emptied` stammt aus T-036 und ist hier mitgelaufen, weil
   ich einen Fall dazugestellt habe, der behauptet, der Berater erbe die
   QA-018-Entscheidung über die Fassade. Er tut es: der Fall stirbt, wenn die
   Liste der bewegungsgebundenen Effektfamilien wieder leer ist.

**Zwei Mutationen teilen sich einen Anker** (`damage-goal-ranks-on-the-bare-figure`
und `damage-goal-asks-the-slotless-question`). Das ist zulässig — jede findet
ihn genau einmal — und beide Ankerprüfungen fallen mit, wenn eine von beiden
angewandt ist. In der Tabelle oben ist das der Grund für „7 failed" statt
„6 failed" bei der ersten.

**Was ich nicht per Mutation belegt habe, und das ist eine Lücke, kein Beleg:**
`test_the_advisor_computes_the_build_the_window_shows` (Prüfpunkt 13, der
Vergleich gegen `Planner.current_build()`) hat **keine** eigene registrierte
Mutation. Er hätte eine verdient — der Gegenbau wäre „`evaluate` reicht
`weapons_held` nicht durch" oder „`declared` fällt weg". Ich habe darauf
verzichtet, weil er von den Mutationen `advisor-presorts-against-the-empty-build`
und `advisor-computes-in-a-second-place` bereits mit-getötet würde, aber das
ist ein Argument über Nachbarn und kein Nachweis über ihn selbst. Empfehlung:
mit S9 nachziehen, wenn `worker.py` den Kontext baut.

---

## 2. Die Entscheidung zur Hashbarkeit (QA-066), mit Begründung

**Entscheidung: die Typen sind hashbar, und der Cache-Schlüssel ist der
`AdvisorRequest` selbst.** Es entsteht **keine** zweite Schlüsselform.

Die Regel, aus der das folgt, steht im Modul-Docstring von `types.py`: *die
Formen, die eine Frage beschreiben, tragen keine Abbildung und keine Liste.*
`Slot`, `HeldRelic`, `HeldSlot`, `SlotProblem`, `ArmamentRef`, `Budget` und
`AdvisorRequest` halten nur `int`, `str`, `bool` und Tupel davon. Dieselbe
Regel gilt für die Antwortformen — dort nicht wegen des Caches, sondern wegen
AD-006 Punkt 8: sie gehen über die Threadgrenze, und ein dict-Feld wäre dem
Namen nach eingefroren und in der Sache geteilt.

**Warum nicht ein abgeleiteter Schlüssel neben den Typen?** Weil das die
zweite Repräsentation wäre, die AD-016 Punkt 2 fürchtet: ein Schlüssel, der
von dem Zustand abdriftet, für den er steht, liefert einen Treffer über den
falschen Haltezustand — und das überschreibt einen Slot, den der Spieler
bewusst festgehalten hat. Ein überflüssiger Fehlschlag kostet eine halbe
Sekunde; das kostet die Funktion.

**Die zwei benannten Ausnahmen** sind `GoalContext` und `ReferenceArmament`.
Sie tragen den extrahierten Datensatz beziehungsweise einen Waffensatz — das
*sind* Abbildungen, und kein Umbau hier machte sie hashbar. Keine der beiden
ist je ein Cache-Schlüssel: der `AdvisorRequest` trägt statt des Datensatzes
dessen `data_version` und statt des Bestands einen
`inventory_fingerprint`.

**Belegt statt behauptet, drei Wege (L-002):**

- `test_every_shape_outside_the_context_can_be_a_cache_key` hasht **eine
  Instanz jeder** Datenklasse — nicht ihre Annotationen. Ein dict, das trotz
  Annotation hineingegeben wird, ist genau der Fall, den QA-066 vorhersagt.
- `test_the_sample_covers_every_dataclass_in_the_module` prüft die Stichprobe
  gegen das Modul. Ein neuer Typ muss entweder hashen oder ausdrücklich als
  Ausnahme benannt werden; still dazukommen kann keiner.
- `test_a_context_type_really_is_the_exception_it_is_named_as` hasht die zwei
  Ausnahmen und **verlangt** ein `TypeError`. Hört eine von ihnen auf, den
  Datensatz zu tragen, fällt dieser Test — und der Eintrag gehört dann
  gelöscht statt als Freibrief stehenzubleiben.
- Auf der **Erzeugerseite**: `test_a_pool_the_advisor_produced_can_be_a_cache_key`
  hasht, was `candidates.pool` wirklich gebaut hat. Die Mutation
  `advisor-marginals-as-a-mutable-map` schreibt dort eine `list` statt eines
  Tupels — sie ändert bewusst **genau eine** Eigenschaft (jede Suche, jede
  Sortierung, jede Zahl arbeitet weiter), und der Fall stirbt allein.

**QA-066 selbst bleibt offen und ist nicht angefasst.** `damage.Rating` ist
unverändert flach unveränderlich und unhashbar; unter `advisor/` hält nichts
eine `Rating` fest, also kann ihre Flachheit nicht in einen Schlüssel lecken.

**Eine Abweichung von S4 dabei, ausdrücklich:** `AdvisorRequest.held_fingerprint`
ist eine **Eigenschaft**, kein Feld — S4 sagt „kein Verhalten". Begründung:
ein gespeicherter Fingerabdruck kann von dem Haltezustand abdriften, den er
beschreibt, und ein abgedrifteter Fingerabdruck **ist** der AD-016.2-Fehler.
`damage.Rating` hält den Präzedenzfall für abgeleitete Lesungen auf einer
`frozen` Datenklasse. Wenn der `director` das anders will, ist es ein Feld
plus eine Fabrikfunktion, die es füllt — dann aber mit einem Wächter dagegen,
dass jemand den Request ohne die Fabrik baut.

---

## 3. Annahmen über die Spieldaten, die nicht aus einer Datei belegt sind

Diese gehen an den **Nutzer**, nicht in den Code — im Code stehen sie als
`weights_note` und `unknowns` im Ergebnis, damit sie im Programm sichtbar
werden, aber entschieden sind sie nicht.

1. **Effektives HP = HP geteilt durch die Schadensdurchlassrate.** Die
   Spieldateien nennen die acht Felder (`slash/blow/thrust/neutral` und
   `magic/fire/thunder/dark…DamageCutRate`, Neutral 1.0) und sagen **nicht**,
   dass die Engine sie multiplikativ auf den erlittenen Schaden anwendet. Die
   Formel ist die naheliegende Lesart und trotzdem eine Annahme. Sie steht
   als erste Zeile in `unknowns`.
2. **Alle acht Schadensarten gleich gewichtet.** AD-004 verlangt es so und
   verlangt, dass es ausgesprochen wird; nichts in den Dateien sagt, wie oft
   ein Spieler Feuer statt Hieb trifft. Steht in `weights_note` **und** in
   `unknowns`.
3. **Ohne Referenzwaffe: das arithmetische Mittel der fünf
   Angriffsmultiplikatoren** aus `damage.AR_RATE_FOR`, einheitenlos. AD-004
   sagt für diesen Fall nur „ranked on attack multipliers only" und nennt
   keine Formel — die habe ich gewählt. Sie ist in `weights_note`
   ausgesprochen. Attributsboni bewegen dort nichts, was richtig ist (ohne
   Waffe gibt es keine Skalierung, in die sie fliessen könnten) und trotzdem
   überraschen kann.
4. **Die Rangfolge des Überlebensziels ist „grösser ist besser"** —
   effektives HP, nicht „erlittener Schaden". Damit rankt eine Vergleichsregel
   beide Ziele. Für die Anzeige heisst das ein Vorzeichenwechsel; siehe unten
   an den `ui-ux-designer`.
5. **Die acht Felder sind die vollständige Liste für dieses Ziel.** Status-
   ailments (`bloodDamageRate` und die drei daneben), Stance
   (`toughnessDamageCutRate`) und die Widerstandspunkte aus
   `model.RESISTANCES` sind echt und **nicht** in der Zahl. Steht in
   `unknowns`; der Geltungsbereich steht am Konstantenblock.
6. **Eine Schadensdurchlassrate ist nie null.** Gemessen, mit Rezept:

   ```
   .venv\Scripts\python.exe   # snapshot data_version 10350000, 2026-09-03
   > effects in dataset: 2076
   > damage-cut values: 421  min 0.520000  max 1.460000  non-positive 0
   ```

   Deshalb steht in `_min_damage_taken` **kein** Zweig gegen einen Nullteiler
   — ein Zweig, den keine Daten erreichen, ist genau der tote Code, den QA-061
   in diesem Projekt gerade entfernt hat. Die zwei Vorbedingungen, die ein
   **Aufrufer** falsch machen kann (leere Gewichtung, Datensatz ohne Kurven),
   sind geprüft und haben je einen Fall.

---

## 4. Was mir an AD-014 bis AD-018 im Kontakt mit dem echten Code
   widersprüchlich oder unausführbar erschien

Das entscheidet der `director`, nicht ich. Alle sechs Punkte sind so
umgesetzt, wie ich sie unten begründe; jeder ist mit einer Zeile Code
umzudrehen.

**(a) `damage.equipped` statt `damage.candidate` — ein Widerspruch zwischen
zwei Vorgaben, und ich habe eine gewählt.**
`docs/state.md` und T-037 sagen: „der Berater rechnet Waffenwerte über
`damage.candidate()` / `damage.rank_candidates()`". AD-004 sagt: die
Rangzahl ist das Attack Rating „berechnet von genau derselben Rechnung, die
die Waffentafel zeigt". Die Waffentafel fragt `damage.equipped`. Beides geht
nicht.
Ich habe **`equipped`** genommen, weil `candidate` per Konstruktion keine
Startwaffen-Paarung tragen kann (AD-020 Punkt 3) und der absolute Wert damit
um den Faktor 0,85 von dem abwiche, was die Tafel für dieselbe Waffe zeigt —
und AD-014.6 hält den absoluten Wert als die eine Autorität.
**Die Rangfolge wäre in beiden Fällen dieselbe** (die Strafe ist ein
konstanter Faktor über alle Kandidaten); es geht allein um die Zahl. Der
AD-021-Wächter ist von der Wahl unberührt: `equipped` liegt in derselben
Fassade.
Der Fall, der die beiden Fassungen auseinanderhält, ist
`test_the_damage_goal_charges_the_starting_armament_penalty`, und die
Mutation `damage-goal-asks-the-slotless-question` tötet ihn allein.

**(b) `equipped` rechnet eine Schicht zu viel.** Es liefert
`(bare, equipped)`, also **zwei** `weapons.rate`-Aufrufe je Bewertung; die
`bare`-Hälfte ist die linke Spalte der Aufschlüsselungstafel und wird vom
Berater nie gelesen. Bei 206 Kandidaten an einem weissen Slot sind das 206
verworfene Schicht-1-Rechnungen. Die Fassade hat keinen Eingang „nur die
fertige Antwort für eine Waffe in einem Slot". Einen zu bauen ist eine
Änderung an AD-020 und gehört dem `architect`, nicht mir. **Empfehlung:
`performance-tuner` in S11 beauftragen, den Messwert unten als
Ausgangspunkt.**

**(c) AD-004s `GoalContext` reicht für `model.compute` nicht.** Die
Illustration nennt `(data, hero, level, weapon, weighting)`. `compute`
braucht ausserdem `weapons_held` (ein Waffentyp-Gate ist von **jeder** Waffe
auf dem Gitter erfüllt, nicht nur von der bewerteten), die von den Waffen
gerollten Effekte und `declared`. Ohne sie unterscheidet sich der Build des
Beraters von dem des Fensters — QA-001 an einer neuen Stelle. Ich habe
`GoalContext` um drei Felder erweitert (`weapons_held`,
`armament_effect_ids`, `declared`) statt einen zweiten Kontexttyp einzuführen.
Wenn der `architect` das lieber getrennt hätte („was ein Ziel braucht" gegen
„was eine Bewertung braucht"), ist das ein Schnitt an einer Stelle.
`test_the_advisor_computes_the_build_the_window_shows` ist der Fall, der die
Vollständigkeit hält.

**(d) AD-014.1 nennt keine Form für `assignment`.** Ich habe
`tuple[Candidate, ...]` genommen — der Kandidat trägt seinen Slotindex
selbst, also braucht `evaluate` keine zweite Abbildung. Bitte bestätigen,
bevor S7 darauf baut.

**(e) AD-004 verlangt für `min_damage_taken` die `unknowns`-Zeile „The break
threshold is unknown." — ich habe sie weggelassen.** Sie steht in AD-004
selbst unter dem Vorbehalt „(README, sofern relevant angezeigt)", und sie
handelt von der Schwächenkette der Bosse, also vom **ausgeteilten** Schaden.
Sie in einer Zahl über erlittenen Schaden zu führen verdünnt A7, statt es zu
erfüllen. An ihrer Stelle stehen drei Zeilen, die diese Zahl wirklich
betreffen. **Wenn der `director` die AD-004-Zeile wörtlich will, ist es eine
Zeile in `_DAMAGE_TAKEN_UNKNOWNS`.**

**(f) AD-004s Formulierung „…; all eight are weighted equally." backt die
Standardgewichtung in eine `unknowns`-Zeile ein**, während dieselbe
Entscheidung die Gewichtung zu **Daten** macht (OF-3). Beides zusammen wäre
eine Zusicherung, die bei einer anderen Gewichtung unwahr wird. Ich habe die
`unknowns`-Zeile gewichtungsunabhängig formuliert und den konkreten Satz in
`weights_note` gelegt, wo AD-004 ihn ohnehin haben will.

**(g) Nicht gebaut, obwohl AD-023 es beschreibt: die Kennzeichnung je
Kandidat, ob er ein AR-Ratenfeld trägt.** T-037 beauftragt sie nicht, und
`UI_SPEC` AK-47 verlangt den Vorbehalt derzeit an *jeder* Zeile, solange
QA-018 offen ist — und QA-018 ist geschlossen. Bevor das gebaut wird, sollte
der `ui-ux-designer` AK-47 nachziehen; sonst baut jemand eine Markierung, die
die Spec gar nicht mehr will. Der Einbau wäre ein Feld auf `Candidate` und
eine Abfrage über seine Effekte, keine zweite Rechnung.

---

## Tests

**Neu: 107 Fälle**, und die Summe geht so auf:
`tests/test_advisor_types.py` 46 · `tests/test_advisor_evaluate.py` 8 ·
`tests/test_advisor_candidates.py` 21 · `tests/test_advisor_goals.py` 18 =
**93**, dazu **14** aus `test_every_mutation_still_finds_its_anchor_in_the_real_source`,
das über die Mutationsliste parametrisiert ist und mit ihr von 16 auf 30
Fälle gewachsen ist. 93 + 14 = 107 = 398 − 291.
`tests/test_one_build.py` bekommt **keinen** neuen Fall — dort ist nur die
Erwartung des `compute`-Wächters um einen Eintrag gewachsen.
`tests/advisor_cases.py` ist ein Fallbaukasten und enthält keine Fälle, nur
Helfer, nach dem Muster von `tests/relics.py`.

**Abgedeckt**

- Prüfpunkt 13 (Berater-Build == Fenster-Build) gegen den echten `Planner`,
  einmal ohne und einmal mit einem verfluchten Deep-Relikt.
- AD-014.1: eine `compute`-Stelle; Zuweisung auf gehaltenen Slot verweigert;
  zwei Kandidaten für einen Slot verweigert.
- AD-014.3 / do-not 13, in der einzigen Form, die es scharf prüft: ein
  `isStrongestEffect` gehalten, eine zweite Kopie davon als Kandidat →
  Grenzbeitrag **exakt** 0 neben dem gehaltenen, > 0 ohne ihn.
- AD-018.1: Bezugsgrösse ist der Build mit geleertem Zielslot; das Relikt im
  Slot wird für seinen Slot wieder angeboten und steht nicht auf null.
- AD-013: kein Rollen-Dedup (zwei Kopien einer Rolle = zwei Kandidaten);
  Kopien ohne Handle raus **und** gemeldet; gehaltene Kopie nicht zweimal.
- Farbregel, weisser Slot zieht jede Farbe, Deep-Trennung.
- S5+: Kurzlistenlänge `K + (freie − 1)`; Prüfpunkt 15 als **Objektidentität**
  zwischen Picker-Liste und Suchliste, nicht als Zahlengleichheit.
- A7: keine Zielrichtung liefert je leere `unknowns`; der
  Attack-Rating-Vorbehalt steht in **beiden** Zweigen.
- QA-074: der Wert ist ungerundet, der Anzeigetext getrennt.
- QA-066: siehe Abschnitt 2.
- OF-3: eine andere `Weighting` verändert die Zahl messbar (ganz auf Feuer
  gewichtet bewegt ein reiner Magie-Negationseffekt **nichts**).
- QA-018-Erbe: ein bewegungsgebundener Angriffsbuff steht beim Berater auf
  null, ein flacher daneben nicht.
- Determinismus: zwei Läufe über einen Bestand liefern bei exakten
  Gleichständen dieselbe Reihenfolge (Zweitschlüssel Name, dann Handle).

**Bewusst nicht abgedeckt**

- Suche, Erklärung, Worker, Cache, Oberfläche, Generationszähler,
  Entprellung — S7 bis S10, nicht dieser Auftrag. Damit sind AD-009-Prüfpunkte
  8, 9, 10, 11, 12, 14, 17 und 18 **offen**.
- Prüfpunkt 16 (abnehmender Ertrag) ist von `tests/test_marginal_returns.py`
  gedeckt, das ich nicht angefasst habe. Es misst über
  `damage.attack_rating`, also über dieselbe `Question.EQUIPPED`-Antwort wie
  mein Ziel — die Eigenschaft überträgt sich, aber sie ist für den Berater
  **nicht eigens gemessen**. Das ist eine Lücke, kein Beleg.
- Ein Save **ohne** lesbare Handles gibt es auf dieser Maschine nicht (0 von
  309 Relikten ohne Handle, gemessen). Der Fall ist synthetisch geprüft, nicht
  am echten Ausfall.

**Läufe**

```
.venv\Scripts\python.exe -m pytest -q -m "not slow"
vorher (Sessionbeginn, Commit 3650765):  291 passed, 5 deselected in  81.71s
nachher (Commit 690db5f):                398 passed, 5 deselected in  87.59s
```

Die `slow`-Fälle (5 deselected) habe ich **nicht** gefahren; sie lesen die
Spielinstallation und sind nicht die Abnahme dieses Auftrags.

---

## Definition of Done

- [x] Anforderung verstanden, Annahmen dokumentiert (Abschnitt 3)
- [x] Build & Tests grün in der benannten Testumgebung (Windows 10,
      `.venv\Scripts\python.exe -m pytest -q -m "not slow"`): 398 passed
- [x] Neue Tests für neue Logik; jeder neue Wächter mit tötender Mutation
      (Abschnitt 1) — **eine benannte Ausnahme:** Prüfpunkt 13 hat keine
      eigene registrierte Mutation
- [x] Keine Secrets, keine TODOs, kein toter Code, keine neue Abhängigkeit
- [ ] **Linter: nicht prüfbar.** Es gibt weiterhin keinen Linter im Repo
      (`ruff` steht seit drei Zyklen zurückgestellt). „Linter sauber" kann
      ich nicht behaupten und behaupte es nicht.
- [x] QA-Akzeptanzkriterien selbst durchgespielt, soweit sie diesen Auftrag
      betreffen; UI-Vorgaben nicht berührt (keine Oberflächenänderung)
- [x] Doku: die Begründungen stehen in den Modul-Docstrings; `docs/state.md`,
      `ARCHITECTURE.md` und `qa/findings.md` gehören anderen Rollen und sind
      **nicht** von mir angefasst
- [x] Abschlussbericht geschrieben

**Ungeprüfte Plattformen:** alles ausser Windows 10. Das Paket importiert kein
Qt und keine plattformabhängige Bibliothek, aber gelaufen ist es nur hier.
Ein gebautes Artefakt (A9) ist unverändert nie geprüft worden.

---

## Offene Fragen

**An den `director`** — die sechs Punkte aus Abschnitt 4, davon entscheidend:
(a) `equipped` gegen `candidate`, (c) die Erweiterung von `GoalContext`,
(e) die weggelassene AD-004-Zeile, (g) AD-023 gegen AK-47.

**An den `architect`** — (b): braucht `damage.py` einen Eingang, der nur die
fertige Antwort für eine Waffe in einem Slot liefert, ohne die
`bare`-Hälfte? Das ist eine AD-020-Frage.

**An den `ui-ux-designer`** — siehe unten.

**An den Nutzer, über den `director`** — die sechs Annahmen aus Abschnitt 3,
vor allem die Formel für effektives HP.

---

## An `qa-engineer`

**Was sich am Programm geändert hat: nichts Sichtbares.** Kein Widget, kein
Text, kein Verhalten der Oberfläche. `git diff --stat 3650765..HEAD` zeigt
nur neue Dateien plus `tests/test_one_build.py` und
`scripts/differential/mutate.py`. Ein Regressionsdurchgang am Fenster sollte
**null** Unterschiede finden; findet er welche, ist das ein Befund gegen mich.

**Was zu prüfen wäre, wenn du den Kern selbst anfasst:**

- Die Aussagen aus Abschnitt 1 nachfahren. Rezept: `git archive HEAD | tar -x
  -C <baum>`, dann `python scripts/differential/mutate.py --apply <name>
  --tree <baum>`, dann die Suite im Baum. Erwartung ungemutiert im
  extrahierten Baum: 398 passed, 5 deselected.
- **Der Fall, den ich für den härtesten halte:**
  `test_a_candidate_is_measured_against_the_held_build`. Er hängt daran, dass
  der Datensatz einen nicht-stapelbaren Effekt auf `maxHpRate` enthält
  (`advisor_cases.a_non_stacking_effect`). Es gibt in diesem Datensatz
  **genau einen** („Increased Maximum HP", ×1.12). Ein Spiel-Patch, der ihn
  entfernt, macht den Fall zu einem `LookupError` — laut, nicht still, aber es
  ist eine Abhängigkeit von einem einzigen Datensatz-Eintrag, und du solltest
  sie kennen.
- Gleiches Muster, gleiche Enge: `physicsAttackRate` nicht stapelbar gibt es
  auch nur einmal („Physical Attack Up", ×1.10). Ich benutze ihn nicht, aber
  wenn du den Fall verschärfen willst, ist das der Vorrat.
- **Randfälle, die ich abgedeckt habe und die du gegenprüfen solltest:** alle
  Slots gehalten (kein Pool, kein Fehler); ein Slot **leer** gehalten (zählt
  als gehalten, nicht als frei, und ändert den Fingerabdruck); ein gehaltenes
  Custom relic (kein Handle, belegt keine Kopie, und der Fingerabdruck muss
  trotzdem bildbar sein); weisser Slot; Deep an und aus.
- **Randfall, den ich nicht am echten Ausfall geprüft habe:** ein Save ohne
  lesbare Handles. Siehe den Befund an den `director` unten — auf so einem
  Save wäre der Berater **vollständig leer**, nicht nur ungenau.
- Die `slow`-Fälle sind ungefahren.

---

## An `ui-ux-designer`

Nichts an der Oberfläche geändert. Vier Dinge, die die Spec berühren:

1. **Vorzeichen.** `min_damage_taken.value` ist **effektives HP, grösser ist
   besser**, und der Grenzbeitrag ist entsprechend positiv, wenn ein Relikt
   hilft. `UI_SPEC` §3.3 zeigt „Damage taken −18", also die umgekehrte
   Richtung. Der Kern liefert `+eHP`; die Umrechnung in eine Darstellung als
   „weniger erlittener Schaden" ist eine Anzeigeentscheidung und keine, die
   ich getroffen habe. Bitte festlegen, welche Zahl auf der Karte steht.
2. **Einheit als Signal.** `GoalScore.unit` ist `"AR"` mit Referenzwaffe und
   `""` ohne. §3.3 sagt: einheitenlos ⇒ kein `AR`-Zusatz und damit auch kein
   `unverified`. Das ist damit maschinell entscheidbar und nicht geraten.
3. **Wortlaut.** Der Vorbehalt in `unknowns` lautet, wie AD-004 ihn vorgibt:
   „Attack rating has not been verified against an in-game number." `UI_SPEC`
   (§2, nach T-024/DR-003) hat einen **neueren** Satz beschlossen: „Not
   checked against the game's own attack-power display." Es gibt jetzt zwei
   Sätze für eine Sache. Ich habe den aus meiner Vorgabe genommen; welcher
   ausgeliefert wird, gehört dir.
4. **AK-47 gegen AD-023.** AK-47 verlangt den Vorbehalt an jeder Picker-Zeile,
   „solange QA-018 offen ist". QA-018 ist geschlossen. AD-023 wollte statt
   dessen eine **berechnete** Markierung nur an betroffenen Zeilen. Ich habe
   weder das eine noch das andere gebaut (nicht beauftragt). Solange das offen
   ist, sollte niemand die Markierung bauen.

---

## An `director`

### Sicherheitsfunde
Keine. Das Paket öffnet keine Datei, keinen Socket, keine Shell; es baut
keinen Pfad und keine Abfrage aus Eingaben; es konsumiert ausschliesslich
bereits geparste Daten. Effekt-Ids werden als `str(id)` in einem `dict`
nachgeschlagen, nicht in einen Pfad oder Befehl gebaut. Keine neue
Abhängigkeit, kein Secret, keine Persistenz (AD-007/AD-017 eingehalten:
nichts wird geschrieben).

### Der wichtigste Befund: AD-013.4 gegen `inventory.copy_key`

**AD-013 Punkt 4 sagt: ein Relikt ohne Handle ist kein Kandidat.**
`inventory.copy_key` sagt das Gegenteil und begründet es ausführlich: es
fällt auf den Datensatz-Offset zurück, *„Dropping those relics from the
planner would cost far more than the rule is worth (a player with an
unreadable table would be offered nothing)"*. Genau dieses „would be offered
nothing" ist jetzt der Zustand des **Beraters** — beauftragt so, und ich habe
es so gebaut.

Die Folge auf einem Save ohne lesbare Handles: **jeder** Pool ist leer, der
Berater empfiehlt für **jeden** Slot nichts, während der Relikt-Picker daneben
normal funktioniert. Die `unknowns`-Zeile sagt es, aber die Wirkung ist „das
ganze Merkmal ist dunkel", nicht „ein paar Relikte fehlen".

**Wie akut, gemessen statt geschätzt:** auf dem Save dieser Maschine haben
**0 von 309** Relikten keinen Handle. Es ist ein latentes Risiko, kein
laufender Ausfall.

**Und ein Doku-Befund dazu, den ich beim Prüfen gefunden habe:** die
Begründung in `copy_key` („a save whose loadout table cannot be read yields no
handles at all") trifft den Code nicht. `savefile.read_relic_handles` liest
den Handle aus dem **Relikt-Datensatz** (`relic.offset + HANDLE_OFFSET`),
nicht aus der Loadout-Tabelle; die Tabelle wird getrennt von `read_loadouts`
gelesen, und ihr Scheitern ist in `inventory.loadout_error` gefangen. Ein
Save mit kaputter Loadout-Tabelle hat also sehr wohl Handles. Klasse wie
QA-082 (Begründung trifft den Code nicht). **Nicht behoben — nicht mein
Auftrag.**

**Optionen, mit Konsequenz:**
- **A — so lassen.** Konsequenz: latent, heute ohne Wirkung, und der Fall
  taucht bei irgendeinem Nutzer als „der Berater tut nichts" auf.
- **B — AD-013.4 auf `inventory.copy_key` umstellen** (Handle *oder* Offset
  als Kopie-Identität). Konsequenz: ein Vorschlag kann dann auf eine Kopie
  zeigen, die die Oberfläche über den Handle nicht auswählen kann — AD-013
  Punkt 5 („die Oberfläche wählt darüber dasselbe Exemplar") müsste
  nachgezogen werden. Das ist eine `architect`-Frage.
- **C — so lassen und die `unknowns`-Zeile zur Pflichtzeile im Ergebnis
  machen**, wenn sie **alle** Kandidaten betrifft, damit „leer" nicht als
  „nichts hilft dir" gelesen wird. Billigste Absicherung, ändert die Regel
  nicht.

### Weitere Debt- und Doku-Funde (nicht behoben, nicht mein Auftrag)

| Ort | Art | Risiko | Aufwand |
|---|---|---|---|
| `scripts/differential/mutate.py`, Docstring von `newline_of` | „`app.py` is CRLF in the working tree and the other modules are LF" — in diesem Checkout ist **jede** Datei LF (`b'\r\n' in raw` ist überall falsch). Der Code ist richtig, die Begründung veraltet | P4, keine Wirkung | 1 Zeile |
| `nrplanner/inventory.py`, Docstring von `copy_key` | siehe oben — Begründung trifft den Code nicht | P4, irreführend für die nächste Rolle | 3 Zeilen |
| `nrplanner/advisor/types.py` | `AdvisorResult` und `Suggestion` haben **keinen Erzeuger** — S7/S8/S9 füllen sie. Das ist beauftragte Formgebung, aber bis dahin Fläche ohne Nutzer | P4, bewusst | — |
| `nrplanner/advisor/candidates.py::pools` | prüft `rank_by` nicht, wenn es **keine** freien Slots gibt (dann wird `pool` nie gerufen). Ein falsch geschriebener Ziel-Name fiele dort still durch | P4 | 2 Zeilen |
| Repo | weiterhin **kein Linter**. „Linter sauber" ist für jede Rolle unprüfbar; dritte bis vierte Erwähnung | P3 für die DoD | Nutzerentscheid |

### Performance — gemessen, nicht geschätzt (S11-Eingabe)

Skript im Repo, damit die Zahl ihr Rezept trägt:
`scripts/measure_advisor_picker.py`, Commit siehe unten.

```
309 relics owned, Wylder's Chalice [0, 2, 4] deep [0, 1, 3], Wylder at level 15, both goals scored
  slot 0 colour 0 deep False:   52 candidates,   17.1 ms median of 3
  slot 1 colour 2 deep False:   53 candidates,   16.3 ms median of 3
  slot 2 colour 4 deep False:  206 candidates,   64.5 ms median of 3
  slot 3 colour 0 deep True :   23 candidates,    7.4 ms median of 3
  slot 4 colour 1 deep True :   30 candidates,   10.1 ms median of 3
  slot 5 colour 3 deep True :   21 candidates,    7.0 ms median of 3
```

- **AD-018 sagte ~51 ms für 205 Kandidaten am weissen Slot; gemessen 64,5 ms
  für 206.** Rund ein Viertel darüber. Die naheliegendste Ursache ist (b) aus
  Abschnitt 4: `damage.equipped` rechnet die `bare`-Hälfte mit, die niemand
  liest. Ich habe das **nicht** nachgewiesen — es ist eine Hypothese, keine
  Messung, und es zu belegen wäre eine Aufgabe für den `performance-tuner`.
- Der teuerste Picker-Lauf bleibt damit weit unter der 250-ms-Schwelle aus
  `UI_SPEC` AK-09.
- Die zweite Zielrichtung kostet praktisch nichts, wie AD-018 Punkt 2
  vorhergesagt hat: `model.compute` ist der Aufwand, nicht `goal`.
- **Der Gesamtlauf (`Optimize`) ist nicht gemessen** — es gibt noch keine
  Suche.
- **Empfehlung: `performance-tuner` in S11 beauftragen**, mit (b) als erstem
  Prüfpunkt. Ich habe nichts optimiert; das ist nicht meine Rolle.

### Risiken

- **Die Rangfolge kann richtig und die Zahl trotzdem falsch sein.** Der
  Attack-Rating-Vorbehalt aus den Known limits gilt unverändert; er steht in
  jeder `GoalScore.unknowns`. QA-018 ist geschlossen, „gegen die
  Angriffskraft-Anzeige des Spiels geprüft" ist die Zahl deswegen nicht.
- **Der Kern ist ohne Oberfläche und ohne Suche nicht benutzbar.** Er ist
  vollständig für das, was T-037 verlangt, und für einen Nutzer bis S10 ohne
  Wirkung.
- **Prüfpunkt 13 hängt an einem Save.** Ohne Save überspringen sich die zwei
  stärksten Fälle des Auftrags. Auf einem Runner ist die Aussagekraft dieser
  Suite deutlich kleiner, als die Zahl 398 suggeriert.

### Was ich über den Auftrag hinaus angefasst habe, und warum

Genau eines: **`scripts/measure_advisor_picker.py`** ist neu. T-037 verlangt
„miss, was dir auffällt, und nenne es", und die Hausregel L-001 verlangt, dass
eine gemessene Zahl ihr Skript mitbringt. Ohne die Datei wäre die Tabelle oben
eine Behauptung. Sie ist ein Entwicklerwerkzeug ohne Laufzeitwirkung, sie
liegt bewusst **nicht** unter `scripts/differential/` (die Strecke vergleicht
Zahlen zweier Bäume, dieses Skript stoppt Sekunden auf einem), und wenn der
`director` sie nicht will, ist ihre Entfernung ein `git rm`.

### Commits auf `docs/audit-and-advisor-design`

| Commit | Inhalt |
|---|---|
| `64174eb` | `feat(advisor)`: der Rechenkern, vier Module, fünf Testdateien, zwölf Mutationen |
| `3350172` | `test(advisor)`: Wächter geschärft (Kontexttypen belegt, Prüfpunkt 15, Attack-Rating-Vorbehalt, eHP-Annahme), AD-021-Gegenbau nachgetragen |
| `690db5f` | `test(advisor)`: Fingerabdruck gegen ein gehaltenes Custom relic; QA-018-Erbe als Fall |
| (folgt) | `chore`: Messskript und dieser Bericht |

Kein `push`, kein `merge`, kein Branchwechsel, `.gitignore` unberührt.
