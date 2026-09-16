# T-041 — qa-engineer

```
STATUS: erledigt
AUFTRAG: T-041 — QA: Erstdurchlauf gegen den Rechenkern des Beraters (T-037)
GELESEN: docs/tasks/T-041.md · docs/tasks/T-037.md ·
  docs/berichte/T-037-developer.md · GOAL.md (A3-A9, F1-F4, OF-12, OF-13,
  OF-15) · ARCHITECTURE.md (AD-004, AD-009 samt Nachtraegen I-V und den
  Pruefpunkten 1-18, AD-010, AD-013 bis AD-021, AD-023, AD-024) ·
  UI_SPEC.md (§3.2/§3.3, AK-47 bis AK-52, Nachtrag zu AK-47) ·
  docs/state.md · qa/findings.md (QA-001, QA-018, QA-023, QA-043, QA-049,
  QA-061, QA-066, QA-070 bis QA-074, QA-079, QA-082 bis QA-099) ·
  nrplanner/advisor/{__init__,types,evaluate,candidates,goals}.py ·
  nrplanner/{app,damage,model,inventory,weaponslots}.py ·
  nrdata/savefile.py (read_relic_handles, read_loadouts) ·
  tests/{conftest,advisor_cases,relics,weapon_damage_cases}.py ·
  tests/test_advisor_{types,evaluate,candidates,goals}.py ·
  tests/test_one_build.py · tests/test_marginal_returns.py ·
  tests/test_settings_store.py · tests/test_differential_track.py ·
  scripts/differential/mutate.py · NightreignHelper.spec
GEÄNDERT: docs/berichte/T-041-qa-engineer.md (diese Datei, einzige Schreibung
  im versionierten Arbeitsbaum) · ausserdem, ausserhalb der Versionierung
  (`.gitignore`): `.claude/agent-memory/qa-engineer/MEMORY.md`,
  `project_differential_harness.md`, `project_nightreign_guard_gaps.md`,
  `feedback_measure_the_state_a_comparison_test_runs_in.md` (neu).
  Kein Git-Zustand veraendert: nur `git status`, `git log`, `git diff`,
  `git archive` (lesend); kein `add`, `commit`, `checkout`, `reset`, `clean`,
  `stash`, `push`. Alle Mutationen, Messskripte und synthetischen Bestaende
  liegen in 27 eigenen Extraktionen im Scratchpad.
  **Nicht von mir:** `UI_SPEC.md` und `qa/findings.md` sind waehrend meines
  Laufs von der parallelen Scaling-Session geaendert worden, ebenso sind
  `docs/archiv/`, `T-042` bis `T-046`, `R-006` und zwei Berichte
  dazugekommen. `nrplanner/`, `tests/` und `scripts/` sind unveraendert
  (`git status` leer), `HEAD` ist durchgehend `89015aa`.
ANNAHMEN: drei, unten unter „Annahmen dieses Laufs" einzeln benannt — die
  tragende ist, dass `tests/advisor_cases.py::problem_from_planner` /
  `context_from_planner` die Form vorwegnehmen, die S10 im Fenster bauen
  wird (der Docstring sagt es so); ohne diese Lesart waere Pruefpunkt 13
  ueberhaupt kein Wächter ueber dem Fenster, sondern nur ueber einer
  Testdatei.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

---

## 0. Die Antwort in drei Saetzen

Die Suite ist ueberwiegend eine Pruefung von **Kriterien**, nicht von Code:
15 von 15 Mutationen des `developer` sind unabhaengig nachgefahren, **alle 15
Zahlen stimmen exakt**, und keine davon toetet durch einen Absturz an der
falschen Stelle. Die eine Ausnahme ist die wichtigste: **Pruefpunkt 13 — der
einzige Fall, der den Berater gegen die Aussenwelt (das Fenster) haelt —
faengt keinen einzigen der Gegenbauten, fuer die er geschrieben wurde**; von
den sieben Argumenten, die `evaluate` an `model.compute` reicht, koennen
**vier** durch eine falsche Konstante ersetzt werden, ohne dass ein Test
der 398 rot wird. Dazu kommt, dass der Hauptweg (der `SlotPool` des Pickers)
**keine einzige A7-Zeile** der Zielrichtungen traegt, und dass die
Begruendung, auf der die vorlaeufige Director-Entscheidung `equipped` gegen
`candidate` steht, **gemessen falsch** ist.

**Releasefaehig ist nichts davon** — es gibt weder Suche noch Oberflaeche;
das ist beauftragt so. Fuer S7 und S9 traegt der Kern, mit zwei Dingen, die
vorher gezogen gehoeren (QA-100, QA-102).

---

## 1. Die Leitfrage, je Abnahmekriterium

> Pruefen die vorhandenen Tests die Abnahmekriterien ueberhaupt, oder nur,
> dass der Code tut, was er tut?

### A3 — mindestens zwei Zielrichtungen, je Slot ein konkretes Relikt
**Nicht pruefbar, mit einer geprueften Haelfte.**
„Mindestens zwei benannte Zielrichtungen" ist geprueft und gilt
(`test_the_project_promised_two_named_directions`, dazu
`test_the_registry_cannot_be_added_to_at_run_time`). „Schlaegt je Slot ein
konkretes Relikt vor" ist **nicht pruefbar**: es gibt keinen Erzeuger fuer
`Suggestion` oder `AdvisorResult` (Volltextsuche ueber `nrplanner/` und
`tests/` mit zwei unabhaengigen Masken: nur der Re-Export in `__init__.py`
und die Typ-Stichprobe in `test_advisor_types.py`). Das ist Auftragslage
(S7), kein Befund.
**Aber A3 ist beruehrt** — QA-101: die Wahl zwischen `equipped` und
`candidate` **aendert** die Reihenfolge, und der Satz, der sie als
gleichgueltig erklaert, ist widerlegt.

### A4 — Slot-Farben, Stacking, Deep-Kennzeichnung
**Teilweise — Kriterium geprueft, wo der Berater es heute anwendet.**

| Teil | Urteil | Beleg |
|---|---|---|
| Slot-Farben | **Ja** (Pool-Ebene) | drei Faelle, darunter der weisse Slot; die Regel wird bei `inventory.relics_for` **erfragt**, nicht ein zweites Mal formuliert — damit kann sie nicht auseinanderlaufen |
| Deep-Trennung | **Ja** | `test_a_deep_slot_and_an_ordinary_slot_see_different_relics` prueft Disjunktheit **der Handles**, nicht nur ein Flag |
| Stacking | **Teilweise** | genau **ein** Fall (`test_a_candidate_is_measured_against_the_held_build`), aber ein sehr guter: der nicht stapelbare Effekt wird ueber `model.compute` **gesucht**, nicht ueber einen Namen geraten. Mutationsbelegt (`advisor-presorts-against-the-empty-build`, 4 rot). AD-009 Pruefpunkt 2 verlangt die Eigenschaft ueber **jeden** Effekt der Daten — den Test gibt es im Repo nicht |

Was **nicht** geprueft ist: dass ein *Vorschlag* die Regeln einhaelt. Es gibt
keinen Vorschlag. Und: `evaluate` — die eine Tuer, die AD-014 durchsetzt —
prueft die **Farbe nicht**. Sie kommt ausschliesslich aus dem Pool. Solange
S7 nur aus Pools schoepft, haelt das; ein Wächter dagegen existiert nicht.

### A5 — die Information fuer eine Begruendung geht nicht verloren
**Teilweise, und ungewacht.**
`evaluate` gibt den `model.Build` zurueck, dessen `sources` die Zurechnung je
Effekt traegt — die Information ist da (AD-015 erfuellt). **Aber `pool()`
verwirft den Build**: was in den `SlotPool` geht, sind `effect_ids`,
`curse_ids` und zwei Floats. S8 muss die Zurechnung aus den Ids neu
herleiten oder je Kandidat ein zweites `model.compute` fahren (bei 206
Kandidaten am weissen Slot ist das die teure Variante).
**Kein Test haelt A5.** Es gibt keinen Fall der Form „aus dem, was der Pool
liefert, ist eine Begruendung noch bildbar". Der Beleg ist eine Codelesung.

### A6 — blockiert die Oberflaeche nicht
**Nicht pruefbar.** Kein Thread, kein Worker, keine Oberflaeche. Die
Messung des `developer` (17-64 ms je Slot) habe ich nicht nachgefahren —
sie hat ihr Skript (`scripts/measure_advisor_picker.py`, L-001 erfuellt) und
faellt in S11.

### A7 — wo die Dateien nichts hergeben, sagt das Ergebnis das
**Teilweise. Auf dem Kriterienweg ja, auf dem Nutzerweg nein.**

Was **haelt**, mit Nachweisweg:
- `GoalScore.unknowns` ist nie leer, je Zielrichtung parametrisiert geprueft,
  und die toetende Mutation `advisor-goal-without-its-unknowns` macht genau
  diesen Fall rot (2 rot, unabhaengig nachgefahren). Das ist ein echter
  Kriterientest, kein Codetest.
- Der Attack-Rating-Vorbehalt steht in **beiden** Zweigen von `_max_damage`
  und wird in beiden geprueft.

Was **nicht** haelt:
- **QA-102:** der `SlotPool` — das Ergebnis des Hauptwegs (AD-018: der
  Picker ist der Hauptweg, nicht ein Zwischenschritt) — traegt von
  `GoalScore` **nur `value`**. `unknowns`, `weights_note`, `unit`, `display`
  gehen an der Poolgrenze verloren. Die Oberflaeche kann nicht vergessen,
  was sie nie bekommt — sie kann es nur nicht zeigen. Das ist genau die
  Anordnung, die AD-010 als Option A verworfen hat.
- **AD-004s gemeinsame `unknowns`-Zeile** („N of your relics carry effects
  that only apply under a condition. They were not counted.") **existiert
  nirgends** — zwei unabhaengige Suchen ueber `nrplanner/advisor/`
  („conditional", „not counted"): ein Treffer, ein Docstring.
- **QA-103:** Annahme 6 des `developer` („eine Durchlassrate ist nie null")
  steht **nur im Docstring**, nicht im Ergebnis — und das ist die einzige
  der sechs, fuer die das gilt.
- **QA-104:** der Geltungsbereich der Ersatzgroesse ohne Referenzwaffe
  schweigt darueber, dass ein klassengebundener Angriffsbuff dort **exakt 0**
  zaehlt (gemessen: derselbe Buff bewegt mit passender Waffe +14,27).

### A8 — alle nutzersichtbaren Zeichenketten Englisch
**Im Bestand ja. Als Pruefung: nein, repo-weit.**
AST-Durchgang ueber alle einzeiligen String-Konstanten in
`nrplanner/advisor/`: alles Englisch; die drei Nicht-ASCII-Zeichen sind `—`
und `×`, also Hausform (`app.py` fuehrt `—` 33-mal). Die von AD-010
verbotenen Woerter („Optimal", „Best possible", „Guaranteed") kommen nicht
vor. **Aber es gibt im ganzen Repo keinen Wächter fuer A8** (zwei
unabhaengige Suchen ueber `tests/`: 0 Treffer). → QA-111.

---

## 2. Die nachgefahrene Mutationstabelle (Prueffrage 1)

Rezept: `git archive HEAD | tar -x -C <baum>` je Mutation (frische
Extraktion, kein `git worktree` — der wuerde den Git-Zustand des Repos
anfassen), dann die **Repo-eigene** `scripts/differential/mutate.py --apply
<name> --tree <baum>`, dann
`.venv\Scripts\python.exe -m pytest -q -m "not slow"` im Baum.
Ungemutiert im extrahierten Baum: **398 passed, 5 deselected** — bestaetigt.

| Mutation | `developer` | mein Lauf | gleich? | toetet aus dem richtigen Grund? |
|---|---|---|---|---|
| `advisor-computes-in-a-second-place` | 3 failed / 395 | 3 / 395 | ✔ | ja — der AST-Wächter faellt. Anmerkung unten (a) |
| `advisor-presorts-against-the-empty-build` | 4 / 394 | 4 / 394 | ✔ | ja, verschobene Zahl, kein Absturz |
| `advisor-ranks-the-slot-as-it-stands` | 3 / 395 | 3 / 395 | ✔ | ja |
| `advisor-offers-a-relic-without-a-handle` | 2 / 396 | 2 / 396 | ✔ | ja — die Zusicherung faellt an der Behauptung, nicht an einem `TypeError` |
| `advisor-leaves-a-relic-out-without-saying-so` | 2 / 396 | 2 / 396 | ✔ | ja |
| `advisor-forgets-the-held-handles` | 3 / 395 | 3 / 395 | ✔ | ja |
| `advisor-scores-only-the-ranking-goal` | 2 / 396 | 2 / 396 | ✔ | ja |
| `advisor-marginals-as-a-mutable-map` | 2 / 396 | 2 / 396 | ✔ | ja — `TypeError` **ist** hier die Zusicherung (Cache-Schluessel) |
| `advisor-shortlist-without-room-for-the-others` | 3 / 395 | 3 / 395 | ✔ | ja |
| `damage-goal-ranks-on-the-bare-figure` | 7 / 391 | 7 / 391 | ✔ | ja |
| `damage-goal-asks-the-slotless-question` | 3 / 395 | 3 / 395 | ✔ | ja — **aber sein `survival_means` traegt die widerlegte Behauptung**, siehe QA-101 |
| `advisor-goal-without-its-unknowns` | 2 / 396 | 2 / 396 | ✔ | ja |
| `advisor-rates-an-armament-itself` | 1 / 397 | 1 / 397 | ✔ | ja — Referenz statt Aufruf, kein Absturz. Vorbildlich |
| `advisor-fingerprint-sorted-naturally` | 2 / 396 | 2 / 396 | ✔ | ja — `TypeError` **ist** die Zusicherung (Fingerabdruck ueberhaupt bildbar) |
| `move-scope-list-emptied` (Bestand) | 7 / 391 | 7 / 391 | ✔ | ja |

**Null Abweichungen von seiner Tabelle.** Auch die von ihm offengelegten
Nebenwirkungen stimmen: die beiden `damage-goal-*` teilen einen Anker und
roeten beide Ankerfaelle; `advisor-rates-an-armament-itself` roetet den
eigenen Ankerfall nicht, weil sein `new` den Anker enthaelt.

**(a) Eine Praezisierung, kein Befund.** `advisor-computes-in-a-second-place`
aendert **zwei** Dinge auf einmal: es gibt eine zweite `model.compute`-Stelle
**und** diese rechnet den Grundzustand ohne die gehaltenen Slots. Deshalb
faellt neben dem AST-Wächter auch
`test_a_candidate_is_measured_against_the_held_build`. Die benannte
Zusicherung („nur eine Tuer") ist trotzdem sauber belegt, weil der
AST-Wächter allein rot wird. Ein engerer Gegenbau — ein zweiter
`model.compute`, dessen Ergebnis verworfen wird — wuerde dasselbe beweisen
und nichts mitnehmen.

**Was in dieser Tabelle nicht steht und stehen sollte:** keiner dieser 15
Gegenbauten trifft `evaluate.py`. Alle 15 sitzen in `candidates.py`,
`goals.py`, `types.py` oder `model.py`. Die eine Datei, die AD-014.1 als
**die eine Tuer** benennt, hat keine einzige registrierte Mutation gegen
ihren Inhalt — nur eine gegen ihre *Existenz* als einzige Stelle. Genau das
ist die Luecke, die Prueffrage 2 aufmacht.

---

## 3. Pruefpunkt 13 — der Kern des Auftrags (Prueffrage 2)

### Was Pruefpunkt 13 zusichert
AD-009 Nachtrag I, Punkt 13: *„ein Build mit verfluchtem Relikt bekommt vom
Berater dieselbe Zahl wie ueber `Planner.current_build()`. **Der Vergleich
gegen die Oberflaeche ist die eigentliche Zusage**, nicht die interne
Konsistenz des Beraters."*
Der `developer` benennt den fehlenden Gegenbau selbst und nennt zwei
Kandidaten: *„`evaluate` reicht `weapons_held` nicht durch"* oder *„`declared`
faellt weg"*.

### Was ich gebaut habe
Sieben Gegenbauten gegen `nrplanner/advisor/evaluate.py`, je in einer
eigenen frischen Extraktion, je die volle Suite:

| Gegenbau (mein Skript, gleiche Anker-Semantik wie `mutate.py`) | Suite | **Pruefpunkt 13 rot?** | wer toetet sonst |
|---|---|---|---|
| `weapons_held=list(ctx.weapons_held)` → `weapons_held=[]` | **398 passed** | **nein** | **niemand** |
| `weapon=reference.weapon …` → `weapon=None` | **398 passed** | **nein** | **niemand** |
| `ctx.level` → `1` | **398 passed** | **nein** | **niemand** |
| `ctx.hero` → `ctx.data["heroes"][0]` | **398 passed** | **nein** | **niemand** |
| `declared=dict(ctx.declared)` → `declared={}` | 1 failed / 397 | **nein** | `test_a_declared_conditional_reaches_the_build` (synthetisch) |
| `ids.extend(ctx.armament_effect_ids)` entfernt | 9 failed / 389 | **nein** | 3 evaluate- + 6 goals-Faelle (alle synthetisch) |
| `ids.extend(relic.curse_ids)` entfernt | 1 failed / 397 | **nein** | `test_a_curse_reaches_the_advisor_as_an_ordinary_effect` |
| *(Lebendprobe)* `ids.extend(relic.effect_ids)` entfernt | 4 failed / 394 | **JA** | + 3 weitere |
| *(Gegenprobe)* `ctx.data.get("curves", {})` → `{}` | 26 failed / 372 | **JA** | + 24 weitere |

### Die Antwort
**Pruefpunkt 13 faengt keinen einzigen der Gegenbauten, fuer die er
geschrieben wurde.** Er ist nicht tot — die Lebendprobe zeigt, dass er rot
wird, wenn man ihm die Relikteffekte nimmt. Aber genau die vier Dinge, die
ihn von den synthetischen Faellen daneben **unterscheiden** — die Waffen des
Fensters, sein Level, seine Deklarationen, seine Fluechte — sind in dem
Zustand, in dem er laeuft, **wirkungslos**.

Gemessen am echten `Planner` in genau dem Zustand, den der Testkoerper
herstellt (`equip_what_the_slots_will_take` + `recompute`):

```
owned: 309 Relikte
weapon slots filled: [True, False, False, False, False, False]   -> equipped_weapons() == 1
active weapon slot: 0  weapon: Wylder's Greatsword               -> reference == genau diese Waffe
armament effect ids: [[], [], [], [], [], []]                    -> ctx.armament_effect_ids == ()
declared: {}                                                     -> ctx.declared == ()
deep checked: False                                              -> 0 Fluch-Ids in allen gehaltenen Slots
level_slider.value(): 1   (QSlider ohne setValue, Minimum 1)     -> ctx.level == 1
```

Daraus folgt jede Zeile der Tabelle:
- `weapons_held=[]` ist unsichtbar, weil `model.compute` dann auf
  `weapon.get("wep_type")` zurueckfaellt — und das ist **dieselbe** Waffe.
- `weapon=None` ist unsichtbar, weil `weapons_held` genau diese Waffe traegt.
- `ctx.level → 1` ist unsichtbar, weil der Regler ohnehin auf 1 steht.
- `ctx.hero → heroes[0]` ist unsichtbar, weil Wylder `heroes[0]` **ist** —
  und `hero_by_name(game_data, "Wylder")` in allen synthetischen Faellen
  ebenfalls.
- `declared={}`, die Waffeneffekte und die Fluechte sind leer bzw. aus.

Der Fall vergleicht damit zwei Rechnungen ueber **denselben, entkernten**
Eingabesatz. Das ist die Bauform „der Code tut, was der Code tut" in
Reinform — und ausgerechnet an der Stelle, die als *Vergleich gegen die
Aussenwelt* deklariert ist.

**Der Schwesterfall `test_a_curse_reaches_the_advisor_as_an_ordinary_effect`
ist die Gegenprobe und macht es richtig:** er schaltet Deep ein und sucht
sich ein verfluchtes Relikt, und deshalb hat er als einziger der beiden einen
echten Gegenbau (Fluch-Ids entfernt → er faellt allein). Prueffunkt 13 gehoert
nach demselben Muster gebaut.

→ **QA-100.**

---

## 4. Die sechs Annahmen ueber die Spieldaten (Prueffrage 3)

| # | Annahme | im **Ergebnis** sichtbar? | wo genau |
|---|---|---|---|
| 1 | effektives HP = HP / Durchlassrate | **Ja** | `_DAMAGE_TAKEN_UNKNOWNS[0]`, woertlich „the game files name the fields, not how the engine applies them" |
| 2 | acht Schadensarten gleich gewichtet | **Ja, doppelt** | `weights_note` (`EVEN_WEIGHTING.note`) **und** `_DAMAGE_TAKEN_UNKNOWNS[1]`, letztere bewusst gewichtungsunabhaengig formuliert |
| 3 | ohne Waffe: Mittel der fuenf Multiplikatoren | **Ja, aber zu eng** | `_NO_ARMAMENT` in `unknowns` + `_NO_ARMAMENT_NOTE` in `weights_note`; **sagt nicht**, dass ein klassengebundener Buff dort 0 zaehlt → QA-104 |
| 4 | Ueberlebensziel rankt „groesser ist besser" | **Halb** | `unit="effective HP"` und `display="Effective HP N"` stehen im Ergebnis; die **Richtung** steht nur im `GoalScore`-Docstring und in einem Testfall. Ein Leser, der nur `value` nimmt, rankt richtig — einer, der „Minimise damage taken" woertlich nimmt, rankt rueckwaerts |
| 5 | die acht Felder sind die vollstaendige Liste | **Fast** | „Ailment and status resistance are not part of this figure." — **Stance (`toughnessDamageCutRate`) wird nicht genannt**, nur von der vagen vierten Zeile mitgedeckt |
| 6 | **eine Durchlassrate ist nie null** | **NEIN** | nur im Docstring von `_min_damage_taken`, mit Rezept. Die einzige der sechs, die A7 nicht erfuellt |

### Annahme 6 im Detail — was bei einem Patch passiert
Gemessen (Build von `evaluate`, eine Rate von Hand verstellt, dann
`min_damage_taken.score`):

```
ungestoert                         -> Effective HP 1120
fireDamageCutRate = 0.0            -> ZeroDivisionError: float division by zero
fireDamageCutRate = -0.5           -> value=700.0   display='Effective HP 700'   (unknowns: nichts)
fireDamageCutRate = 1e-12          -> value=1.4e14  display='Effective HP 140000000000980'  (unknowns: nichts)
```

Drei verschiedene Ausgaenge, und die beiden schlimmeren sind die stillen:
- **exakt 0** → roher `ZeroDivisionError` ohne Satz. Ab S9 faellt der im
  Worker-Thread an, also an der Stelle, an der eine Ausnahme in diesem
  Entwurf am schwersten zurueckzuverfolgen ist (das ist woertlich das
  Argument, mit dem `advisor-fingerprint-sorted-naturally` begruendet ist —
  hier gilt es genauso und ist nicht gezogen).
- **negativ** → eine **plausibel aussehende falsche Zahl**, kein Wort.
- **positiv, aber winzig** → eine absurde Zahl, die jede Rangliste anfuehrt,
  kein Wort. Und das ist der Fall, der die Regel des `developer` **nicht
  verletzt**: seine Messung sagt „non-positive 0", 1e-12 ist positiv.

Die Docstring-Begruendung („a division that fails loudly beats one that
guesses") haelt also fuer genau einen der drei Faelle.
→ **QA-103.**

---

## 5. `equipped` gegen `candidate` (Prueffrage 4)

Die Behauptung des `developer`, die der `director` in `docs/state.md` unter
Vorbehalt gestellt hat: *„Die Rangfolge waere in beiden Faellen dieselbe (die
Strafe ist ein konstanter Faktor ueber alle Kandidaten)."*
Dieselbe Behauptung steht **im Repo**, als `survival_means` der Mutation
`damage-goal-asks-the-slotless-question`.

**Sie ist falsch, und der Gegenbeispiel-Kandidatensatz ist zweizeilig.**

Die Strafe ist kein konstanter Faktor ueber die Kandidaten, weil **Kandidaten
sie selbst mitbringen koennen**: drei Effekte des Datensatzes tragen
`*AttackPowerRate` = 0,85 auf allen fuenf Schadensarten —
`7120400 Starting armament inflicts frost`, `7120500 … poison`,
`7120600 … blood loss`. `damage.equipped` rechnet sie, wenn die
Referenzwaffe die Startwaffe in Slot 1 ist; `damage.candidate` kann sie
per AD-020.3 **gar nicht** rechnen.

Messung, Wylder, `Wylder's Greatsword` in Slot 0 (`is_starting_armament`
True), Tier 1:

```
baseline: equipped=203.4176  candidate=203.4176

relic   effects                d(equipped)   d(candidate)
R0      [7120400, 6001400]        -12.3576        21.3589
R1      [7000300]                   0.8294         0.8294

Rangfolge equipped :  ['R1', 'R0']
Rangfolge candidate:  ['R0', 'R1']   -> VERSCHIEDEN
```

R0 ist ein Relikt, das die Startwaffen-Strafe **und** einen flachen
Angriffsbuff traegt. Unter `candidate` steht es mit **+21,36** an erster
Stelle; unter `equipped` mit **−12,36** an letzter. Ein einzelner Kandidat,
der die Reihenfolge dreht.

**Wie akut, gemessen statt geschaetzt:** auf dem Save dieser Maschine tragen
**10 von 309** Relikten einen der drei Effekte (Grand Drizzly Scene, Night of
the Wise, 3× Grand Burning Scene, 3× Grand Luminous Scene, Dark Night of the
Miasma, Grand Tranquil Scene). Das sind 3,2 % des Bestands, keine Exoten.

**Was das fuer die Entscheidung heisst:** die Entscheidung des `developer`
ist damit **staerker** begruendet, nicht schwaecher — `equipped` bildet ab,
was das Spiel tut, `candidate` haette diesen Relikten die Strafe geschenkt
und sie an die Spitze gesetzt. Falsch ist **die Begruendung**, und sie steht
so im Repo, dass die naechste Rolle sie liest. Haette der `director` auf
dieser Grundlage `candidate` gewaehlt, waere das ein A3-Fehler gewesen: der
Berater haette ein Relikt empfohlen, das die Waffe um 15 % schwaecht.
→ **QA-101.**

**Wo die Suite das heute abfaengt:** `test_the_damage_goal_charges_the_
starting_armament_penalty` haelt den Unterschied — als **Zahl**, nicht als
Reihenfolge. Der Fall ist scharf (die Mutation toetet ihn allein). Ein Fall
ueber die *Reihenfolge* fehlt.

---

## 6. AD-013.4 gegen `inventory.copy_key` (Prueffrage 5)

Synthetischer Bestand, jede Kopie ohne Handle, zwei Slots (rot und weiss),
beide Zielrichtungen. Was der Aufrufer bekommt:

```
slot 0: 0 candidates
   unknowns: 4 owned relics of this colour are not offered: this save carries
             no handle for them, so one copy cannot be told from another and a
             suggestion naming one could not be applied to a slot.
   baseline: [('max_damage', 1.0), ('min_damage_taken', 1120.0)]
slot 1: 0 candidates   (gleiche Zeile)
```

**Was der Nutzer saehe: eine leere Liste mit einer `unknowns`-Zeile** — also
die mittlere der drei vom Auftrag genannten Moeglichkeiten. Es ist nicht
still. Aber die Zeile beschreibt einen Teilausfall („4 Relikte fehlen"),
waehrend die Wirkung ein Totalausfall ist („der Berater bietet nichts an"),
und sie steht **je Slot einmal**, also sechsmal dasselbe. Die Option C des
`developer` (Pflichtzeile, wenn **alle** Kandidaten betroffen sind) trifft
genau das.

**Zwei Dinge daneben, die ich beim Bauen gefunden habe:**

1. **Der Wortlaut ist am weissen Slot falsch.** Gemessen, weisser Slot, zwei
   handle-lose rote Kopien und je eine angebotene rote und blaue:
   ```
   candidates: [('Antique', 0, 12), ('Delicate Drizzly Scene', 1, 300)]
   unknowns:   ('2 owned relics of this colour are not offered: …')
   ```
   „of this colour" gibt es am weissen Slot nicht — er zieht jede Farbe. →
   **QA-108** an den `ui-ux-designer`.

2. **Der reale Weg zu `handle is None` ist ein anderer als der beschriebene.**
   Der `developer` hat richtig gefunden, dass die Begruendung in `copy_key`
   („a save whose loadout table cannot be read yields no handles at all")
   den Code nicht trifft; ich habe es unabhaengig nachgelesen und bestaetige
   es: `savefile.read_relic_handles` liest aus dem **Relikt-Datensatz**
   (`relic.offset + HANDLE_OFFSET`). Der Code hat aber **zwei** Wege zu
   `None`, und beide stehen nirgends:
   - `read_relic_handles` schluesselt sein Ergebnis **nach Handle**
     (`out[handle] = relic`). Zwei Datensaetze mit demselben Handle-Wert
     kollabieren; der Verlierer bekommt `handle=None` in `inventory.py`.
   - `if off < 0: continue` — ein Datensatz nahe am Dateianfang wird
     uebersprungen.
   Auf diesem Save: **0 von 309 ohne Handle, 0 doppelte Handles** — die
   Messung des `developer` ist unabhaengig bestaetigt. → **QA-112**.

---

## 7. Regression am Fenster (Prueffrage 6)

**Keine Abweichung gefunden — mit einem Signal, nicht nur mit einem Diff.**

Primaerquelle zuerst: `git diff --stat 3650765..HEAD -- nrplanner/
':!nrplanner/advisor'` ist **leer**. Kein Modul unterhalb `nrplanner/`
ausserhalb des neuen Pakets ist angefasst. Und das Paket ist zur Laufzeit
**inert**: zwei unabhaengige Suchen (`grep -rn "advisor"` ueber
`nrplanner/`, `run.py`, `scripts/`, `NightreignHelper.spec`) finden nur
Kommentare — kein `import`. Es steht auch nicht in `hiddenimports` der
`.spec`.

Weil ein leerer Diff kein mechanismus-gebundenes Signal ist (L-003), habe ich
zusaetzlich einen festen Bedienweg auf **beiden** Baeumen gefahren
(`3650765` gegen `HEAD`, je frisch extrahiert, offscreen):
3 Nightfarer × Deep an/aus × Level 1/8/15 = 18 Konfigurationen, je mit
Relikten in allen aktiven Slots, und je abgezogen: `attributes`,
`base_attributes` (implizit), `derived`, `rates`, `other`, `resistances`,
`warnings`, **`sources`**, das `owned_label`, je Waffenkachel
`damage.equipped` (bare **und** equipped), die Attribute des Weapons-Tabs,
seine **Top-10-Rangliste** mit Zahlen, und die Angebotslisten aller
Relikt-Slots.

```
before: 297 Zeilen   after: 297 Zeilen   diff: 0 Zeilen Unterschied
```

Die Behauptung des `developer` haelt. Der zusaetzliche `slow`-Lauf (5 Faelle,
alle in `test_extraction.py`) ist gruen, und die volle Suite **mit** `slow`
ist `403 passed`.

---

## 8. Was die Suite ueber den Runner sagt (Prueffrage 7)

Gemessen, nicht geschaetzt: in einem eigenen Klon habe ich `conftest.py` so
verstellt, dass `_snapshot_from_cache`, `_snapshot_from_game` und
`installed_game` das liefern, was ein Runner ohne Spielinstallation liefert
(`None` bzw. `skip`), und `NIGHTREIGN_TEST_SNAPSHOT` aus der Umgebung
entfernt.

| Datei | Faelle | laeuft auf dem Runner | ueberspringt |
|---|---|---|---|
| `tests/test_advisor_types.py` | 46 | **46** | 0 |
| `tests/test_advisor_evaluate.py` | 8 | **0** | 8 |
| `tests/test_advisor_candidates.py` | 21 | **0** | 21 |
| `tests/test_advisor_goals.py` | 18 | **1** | 17 |
| neue Ankerfaelle in `test_differential_track.py` | 14 | **14** | 0 |
| **Summe der 107 neuen Faelle** | **107** | **61** | **46** |

Und jetzt die Zahl, die zaehlt: **von diesen 61 rechnet kein einziger
etwas.** Die 46 Typfaelle pruefen Form, Einfrierung und Hashbarkeit; der eine
goals-Fall prueft, dass die Registry ein `MappingProxyType` ist; die 14
Ankerfaelle pruefen, dass Textstellen im Quelltext noch da sind — sie sind
Tests **des Messwerkzeugs**, nicht des Beraters.

**Auf einem Runner ohne Spielinstallation prueft kein Fall dieses Auftrags
einen Build, eine Zielpunktzahl oder einen Grenzbeitrag.** Pruefpunkt 13
ueberspringt dort zweifach (kein Datensatz, kein Save). Die Zahl 398
suggeriert auf einem Runner deutlich mehr, als sie traegt — die Einschaetzung
des `developer` ist damit bestaetigt und beziffert. → **QA-106.**

Nebenbefund zur Formulierung im Auftrag: die 5 `slow`-Faelle sind **alle** in
`test_extraction.py`. Sie sind der einzige Kontakt der Suite zu den
**Archiven**; Kontakt zu echten Spiel*daten* hat jeder Fall, der `game_data`
nimmt (ueber den Snapshot). Kein `slow`-Fall beruehrt den Berater.

---

## 9. AD-009, Pruefpunkte 1 bis 18 — Deckungsstand

| # | Pruefpunkt | Urteil | Beleg / Grund |
|---|---|---|---|
| 1 | Golden AD-005 | ja (Vorbestand) | `test_weapon_damage_golden.py`, nicht Teil von T-037 |
| 2 | Stacking-Eigenschaft ueber **jeden** Effekt | **nein** | im Repo nicht vorhanden; der Berater prueft **einen** Fall (gut gebaut, mutationsbelegt) |
| 3 | Farb-Nebenbedingung | teilweise | drei Pool-Faelle; kein Vorschlag existiert; `evaluate` prueft die Farbe nicht |
| 4 | kein Relikt doppelt, Gefaess mit wiederholten Farben | teilweise | `[RED, RED]`-Fall vorhanden; die Suchseite fehlt |
| 5 | Monotonie | nein | keine Suche (S7) |
| 6 | Determinismus | ja | Zweitschluessel gemessen, zwei Laeufe verglichen |
| 7 | Honesty-Vertrag A7 | teilweise | erste Haelfte ja; zweite Haelfte (`not_counted`) hat **keinen Erzeuger** |
| 8 | gehaltener Slot bleibt unveraendert | teilweise | `evaluate` weist Zuweisungen ab (2 Faelle); im Ergebnis nicht pruefbar |
| 9 | kein Handle eines gehaltenen Relikts im freien Slot | ja (Pool) | mutationsbelegt |
| 10 | Symmetriefalle AD-014.4 | nein | Suche |
| 11 | Cache: anderer Halteinhalt ⇒ kein Treffer | **teilweise, mit Widerspruch** | auf Typebene ja — aber der als Schluessel benannte `AdvisorRequest` ist positions**abhaengig**, `held_fingerprint` positions**unabhaengig** → QA-107 |
| 12 | Nullfall h=0 | teilweise | implizit in jedem Fall ohne `held`, nicht als eigener Vergleich |
| 13 | Berater-Build == Fenster-Build | **nein** | 9 Gegenbauten, keiner der sieben gemeinten macht ihn rot → QA-100 |
| 14 | alle Slots gehalten | halb | `pools()==()` ist geprueft; „und `unknowns` sagt es" hat **keinen Traeger** — `pools` gibt ein leeres Tupel und sonst nichts |
| 15 | Grenzbeitrag == Vorsortierwert | **ja, stark** | Objektidentitaet statt Zahlengleichheit, mutationsbelegt. Der beste Wächter des Auftrags |
| 16 | abnehmender Ertrag | teilweise | `test_marginal_returns.py` misst ueber `damage.attack_rating`, nicht ueber den Berater — vom `developer` als Luecke benannt, bestaetigt |
| 17 | Halt ueberlebt Gefaesswechsel | nein | S10 |
| 18 | kein `QSettings` im Berater-Pfad | **nein (ungewacht)** | die Eigenschaft haelt heute (zwei Suchen ueber `nrplanner/advisor/`: 0 Treffer), aber `test_no_source_opens_a_settings_store_of_its_own` prueft die **Namen** des Stores, nicht seinen Ort → QA-110 |

**Doku-Beobachtung nebenbei:** die Nummer **18** ist doppelt vergeben —
Nachtrag II („kein `QSettings` im Berater-Pfad") und Nachtrag III („untere
Schicht bitgleich"). Frage an den `architect`/`director`, nicht Befund.

---

## 10. Befunde

### [P2 | Major | Mittel] QA-100 — Pruefpunkt 13 faengt keinen seiner Gegenbauten; vier der sieben `compute`-Argumente des Beraters sind ungewacht

**Adressat:** developer
**Betroffen:** `tests/test_advisor_evaluate.py:70` (`test_the_advisor_computes_the_build_the_window_shows`) · `nrplanner/advisor/evaluate.py:113-122` · `tests/advisor_cases.py::context_from_planner`
**Umgebung:** Windows 10, `.venv`, echtes Save (309 Relikte), Snapshot `data_version 10350000`

**Reproduktion:**
1. `git archive HEAD | tar -x -C <baum>`
2. In `<baum>/nrplanner/advisor/evaluate.py` `weapons_held=list(ctx.weapons_held),` durch `weapons_held=[],` ersetzen.
3. `cd <baum> && .venv\Scripts\python.exe -m pytest -q -m "not slow"`
4. Dasselbe je einzeln fuer `weapon=reference.weapon if reference is not None else None,` → `weapon=None,`; `ctx.level,` → `1,`; `ctx.hero,` → `ctx.data["heroes"][0],`.

**Erwartet:** Pruefpunkt 13 wird rot — er sichert zu, dass der Berater
denselben Build rechnet wie das Fenster, und jede dieser vier Aenderungen
gibt ihm einen anderen.
**Tatsaechlich:** **398 passed, 5 deselected** in allen vier Faellen. Kein
Test der Suite wird rot.

**Analyse:** Der Zustand, den der Testkoerper herstellt, ist entkernt:
Level 1 (der `QSlider` in `app.py:1476` bekommt nie ein `setValue`, sein
Minimum ist 1), genau eine Waffe im Gitter (die zugleich die Referenzwaffe
ist, weshalb `model.compute`s Rueckfall `wep_type = weapon.get("wep_type")`
dasselbe liefert), keine Waffeneffekte, `declared == {}`, Deep aus (also
keine Fluechte), und Wylder ist `heroes[0]`. Damit vergleicht der Fall zwei
Rechnungen ueber denselben trivialen Eingabesatz. Die Lebendprobe (Entfernen
von `ids.extend(relic.effect_ids)`) macht ihn rot, er ist also nicht tot —
aber die einzige Eingabe, die er sieht, sehen drei synthetische Faelle
ebenfalls.
Das ist dieselbe Klasse wie QA-070/QA-073/QA-083/QA-086 („Wächter mit
unausgesprochener Reichweite"), diesmal am zentralsten Wächter des Auftrags.
QA-001 — der Befund, aus dem diese ganze Konstruktion stammt — war woertlich
„ein zweiter, kuerzerer Argumentsatz". Genau dagegen ist der Fall gebaut, und
genau das kann er nicht sehen.

**Auswirkung:** Der Berater darf ab sofort auf einem anderen Nightfarer,
einem anderen Level, ohne die gehaltenen Waffen und ohne die Referenzwaffe
rechnen, und die Suite bleibt gruen. Ab S9/S10 baut der Worker den
`GoalContext` — genau dort entsteht ein solcher Fehler, und genau dort faellt
er nicht auf. Fuer den Nutzer waere die Folge eine Rangliste, die zu einem
Build gehoert, den er nicht hat.

**Vorschlag:** Den Fall den Zustand **herstellen** lassen, den er behauptet
zu vergleichen, statt den Vorgabezustand zu nehmen: Level auf einen anderen
Wert als 1, eine zweite Waffe ins Gitter (mit eigenem Typ), ein Effekt auf
einer Waffe, eine deklarierte Bedingung, Deep an mit einem verfluchten
Relikt, und moeglichst ein anderer Nightfarer als `heroes[0]`. Danach die
vier ueberlebenden Gegenbauten als benannte Eintraege nach
`scripts/differential/mutate.py`, damit die Zusicherung ihren Nachweisweg
behaelt (L-002). Ein zweiter, billiger Weg dazu: ein Fall, der prueft, dass
`evaluate` **jedes** Feld des `GoalContext` an `model.compute` weiterreicht
(z. B. ueber ein Aufzeichnungs-Double), damit ein spaeter dazukommendes Feld
nicht wieder still verlorengeht.

---

### [P2 | Major | Mittel] QA-101 — „Die Rangfolge waere bei `candidate` dieselbe" ist widerlegt; die Begruendung steht im Repo

**Adressat:** director (offene Entscheidung 4a aus T-037), developer
**Betroffen:** `scripts/differential/mutate.py` (`survival_means` von `damage-goal-asks-the-slotless-question`) · `nrplanner/advisor/goals.py:136-145` (Docstring `_max_damage`) · `docs/berichte/T-037-developer.md` Abschnitt 4a · `docs/state.md`
**Umgebung:** Wylder, `Wylder's Greatsword` in Slot 0 (Startwaffe), Tier 1, Snapshot `data_version 10350000`

**Reproduktion:**
1. Kandidat R0 bauen mit den Effekten `[7120400, 6001400]` („Starting armament inflicts frost" + flacher Physical-Attack-Buff), Kandidat R1 mit einem +Staerke-Effekt.
2. Je `evaluate(problem, (kandidat,), ctx)` und den Grenzbeitrag einmal ueber `damage.equipped(ref, ref.slot_index, build, hero, data)[1].final_total` und einmal ueber `damage.candidate(ref.weapon, ref.tier, build, data).final_total` bilden.

**Erwartet (laut Behauptung):** dieselbe Reihenfolge.
**Tatsaechlich:**
```
R0 [7120400, 6001400]:  d(equipped) = -12.3576   d(candidate) = +21.3589
R1 [7000300]         :  d(equipped) =  +0.8294   d(candidate) =  +0.8294
equipped  -> ['R1', 'R0']
candidate -> ['R0', 'R1']
```

**Analyse:** Die Strafe ist kein konstanter Faktor ueber die Kandidaten,
weil ein Kandidat sie **selbst mitbringen** kann. Genau drei Effekte des
Datensatzes tragen `*AttackPowerRate` = 0,85 auf allen fuenf Schadensarten
(7120400/7120500/7120600); `damage.equipped` rechnet sie bei der Paarung
Startwaffe/Slot 1, `damage.candidate` per AD-020.3 nie. Auf dem Save dieser
Maschine tragen **10 von 309** Relikten einen davon.

**Auswirkung:** Die Entscheidung des `developer` (`equipped`) wird durch
diese Messung **gestuetzt**, nicht widerlegt — `candidate` haette genau
diesen zehn Relikten die Strafe geschenkt und sie nach oben sortiert, was
A3 verletzt haette. Der Schaden liegt in der Begruendung: sie steht als
`survival_means` **im Repository** und wird von der naechsten Rolle als
belegt gelesen. `docs/state.md` haelt die Entscheidung ausdruecklich unter
Vorbehalt „bis T-041 misst" — hiermit gemessen.

**Vorschlag:** Die Entscheidung `equipped` bestaetigen und die Begruendung
austauschen: nicht „die Rangfolge ist gleich", sondern „die Rangfolge ist
**nicht** gleich, und `equipped` ist die richtige der beiden, weil ein
Relikt, das die Waffe um 15 % schwaecht, auch so gerankt gehoert". Den Satz
in `mutate.py`, in `_max_damage` und im Bericht nachziehen. Dazu ein Fall,
der die **Reihenfolge** haelt, nicht nur die Zahl — der vorhandene
`test_the_damage_goal_charges_the_starting_armament_penalty` prueft den
Betrag.

---

### [P2 | Major | Hoch] QA-102 — Der Hauptweg (`SlotPool`) traegt keine A7-Zeile der Zielrichtungen

**Adressat:** director (Spec-Konflikt), developer
**Betroffen:** `nrplanner/advisor/types.py` (`SlotPool`, `Baseline`, `Marginal`) · `nrplanner/advisor/candidates.py:120-152` (`pool`)
**Umgebung:** unabhaengig vom Save

**Reproduktion:**
1. `pool(inventory, problem, 0, ctx, goals.GOALS, "min_damage_taken")` fahren.
2. Das Ergebnis ansehen: `baseline` ist `(Baseline(goal_id, value), …)`, `candidates[i].marginals` ist `(Marginal(goal_id, gain), …)`, `unknowns` ist `()` (oder die eine Handle-Zeile).
3. Volltextsuche unter `nrplanner/advisor/` nach „conditional" und nach „not counted": ein Treffer, ein Docstring.

**Erwartet:** AD-010 — *„`unknowns` als Pflichtfeld … vom Rechner gefuellt.
Konsequenz: die Oberflaeche kann ihn nicht vergessen, weil er Teil dessen
ist, was sie zeichnet"* — auf dem Weg, den der Nutzer benutzt.
**Tatsaechlich:** `pool()` ruft `goal.score(...)` und nimmt **nur `.value`**.
`unknowns`, `weights_note`, `unit` und `display` werden an der Poolgrenze
verworfen. Die einzige `unknowns`-Zeile, die je in einem `SlotPool` steht,
ist die ueber handle-lose Kopien.
Zusaetzlich: AD-004s **gemeinsame** Zeile („N of your relics carry effects
that only apply under a condition. They were not counted.") existiert
nirgends im Paket.

**Analyse:** Zwei Ursachen, eine davon eine Entscheidung, die nicht mir
gehoert.
(1) `Baseline` und `Marginal` sind bewusst „nur eine Goal-Id und ein Float"
(Docstring: „Kept apart … one is an absolute value and the other a
difference"). Damit ist die Poolgrenze eine Zahlengrenze — richtig fuer die
Zahl, folgenreich fuer den Text.
(2) **Spec-Konflikt, neutral dargestellt:** `UI_SPEC` §3.2/AK-50 legt den
Attack-Rating-Vorbehalt als **einen festen Satz** ausserhalb der Karten fest
— das ist genau die statische Fassung, die AD-010 als Option A verworfen
hat, mit der Begruendung „welche Luecken gelten, haengt vom konkreten Lauf
ab". Beide Lesarten sind vertretbar: entweder gilt AD-010 fuer den Picker
nicht (dann sollte AD-010 oder AD-018 das sagen), oder `SlotPool` muss die
`GoalScore`s tragen. **Das entscheide nicht ich.**
Von dem Konflikt unberuehrt ist die konditionale Zeile: sie ist per
Konstruktion laufabhaengig („N of your relics …"), also kein statischer Satz,
und sie fehlt schlicht.

**Auswirkung:** A7 ist an `GoalScore` geprueft und gilt dort — aber auf dem
Weg, den der Nutzer nach AD-018 zu 100 % benutzen wird (der Picker), traegt
das Ergebnis heute nichts davon. Ein starkes situatives Relikt steht dort mit
0,00, und nichts sagt warum. Genau dieses Bild nennt AD-004 als Grund fuer
die Zeile: *„Ohne diesen Satz saehe ein Spieler ein starkes situatives Relikt
ungenutzt und hielte den Berater fuer kaputt."*

**Vorschlag:** Entscheidung des `director` zu (2) einholen. Unabhaengig davon
die konditionale Zeile bauen — sie braucht nur `model.is_conditional` ueber
die Effekte des Bestands und einen Zaehler, und sie gehoert dorthin, wo sie
laufabhaengig entsteht (Pool oder Ergebnis). Wenn `SlotPool` die
`GoalScore`s tragen soll: ein Feld `scores: tuple[GoalScore, ...]` neben
`baseline` waere hashbar und aenderte an der Zahl nichts.

---

### [P3 | Major | Niedrig] QA-103 — Annahme „eine Durchlassrate ist nie null" steht nur im Docstring; null bricht roh, negativ und fast-null liefern still falsche Zahlen

**Adressat:** developer, director (A7-Anteil)
**Betroffen:** `nrplanner/advisor/goals.py:178-215` (`_min_damage_taken`)
**Umgebung:** unabhaengig vom Save; ausgeloest durch einen Spiel-Patch oder einen fremden Datensatz

**Reproduktion:**
1. `build = evaluate(problem, (), ctx)`
2. `b2 = dataclasses.replace(build, rates=dict(build.rates)); b2.rates["fireDamageCutRate"] = X`
3. `goals.GOALS["min_damage_taken"].score(b2, ctx)` fuer X ∈ {0.0, −0.5, 1e-12}

**Erwartet:** Entweder eine verstaendliche Meldung oder eine Zahl mit einer
`unknowns`-Zeile, die den Fall benennt.
**Tatsaechlich:**
```
X = 0.0    -> ZeroDivisionError: float division by zero      (kein Satz)
X = -0.5   -> Effective HP 700         statt 1120            (kein Wort)
X = 1e-12  -> Effective HP 140000000000980                   (kein Wort)
```

**Analyse:** Die Docstring-Begruendung („a branch no data can reach is the
dead code QA-061 had this project delete, and a division that fails loudly
beats one that guesses") deckt genau den ersten Fall. Der dritte Fall
**verletzt die gemessene Regel gar nicht** — die Messung sagt „non-positive
0", und 1e-12 ist positiv. Ein solcher Wert wuerde jede Rangliste anfuehren.
Die Regel ist eine Regel ueber **den heutigen Datensatz**, im Ergebnis steht
sie nicht, und sie ist die einzige der sechs Annahmen, die A7 nicht erfuellt
(die anderen fuenf stehen in `unknowns`/`weights_note` — Nachweis in
Abschnitt 4).

**Auswirkung:** Nach einem Spiel-Patch entweder ein Absturz ohne Erklaerung
(ab S9 im Worker-Thread, wo dieses Projekt selbst eine Ausnahme als
„hardest place to trace back" bezeichnet) oder eine plausibel aussehende
falsche Rangliste. Beides ohne Vorwarnung.

**Vorschlag:** Nicht der Zweig gegen den Nullteiler — der bleibt tot —,
sondern eine **Plausibilitaetsschranke** am Eingang der Zahl, die ihren
Geltungsbereich mitbringt: „diese Zahl gilt fuer Durchlassraten im gemessenen
Band; ausserhalb sagt der Berater nichts". Als Zeile in `unknowns` das
Rezept, das heute im Docstring steht (421 Werte, min 0,52, Stand
`data_version`), damit die Annahme im Ergebnis sichtbar wird. Als Wächter ein
Fall ueber genau diese drei X-Werte.

---

### [P3 | Minor | Mittel] QA-104 — Ohne Referenzwaffe zaehlt ein klassengebundener Angriffsbuff exakt 0, und keine Zeile sagt es

**Adressat:** developer, ui-ux-designer (Wortlaut)
**Betroffen:** `nrplanner/advisor/goals.py:104-120` (`_attack_multiplier_mean`), `_NO_ARMAMENT_NOTE`
**Umgebung:** `ctx.reference is None` — erreichbar, sobald der Spieler eine leere Waffenkachel aktiv hat

**Reproduktion:**
1. Effekt `321500` („Improved Ranged Weapon Attacks", klassengebunden `ranged`) in den Build geben.
2. `max_damage` einmal ohne Referenzwaffe scoren, einmal mit einer `ranged`-Waffe.

**Erwartet:** Entweder ein Beitrag, oder eine Zeile, die sagt, dass er hier
nicht zaehlt.
**Tatsaechlich:**
```
ohne Referenzwaffe:  plain=1.000000   mit Buff=1.000000   delta=0.000000000
mit 'Shortbow':      plain=101.9242   mit Buff=116.1936   delta=+14.269390
unknowns / weights_note: kein Wort dazu
```

**Analyse:** `_attack_multiplier_mean` liest ausschliesslich `build.rates`.
Ein klassengebundener Buff landet in `model.compute` in `build.class_rates`
(`model.py:987`), nie in `build.rates`. Der Datensatz traegt **8** solcher
Effekte. `_NO_ARMAMENT_NOTE` sagt „With no armament chosen there is nothing
to scale, so the five attack multipliers are averaged with equal weight" —
das liest sich als „Attribute zaehlen nicht" und deckt „ein
klassengebundener Angriffsbuff zaehlt nichts" nicht ab. Dieselbe Klasse wie
QA-046/050/052/062/063/064/070/073/082/083/086/087: eine Zusicherung, die
ihren Geltungsbereich nicht nennt.

**Auswirkung:** Ein Relikt mit „Improved Melee Attack Power" steht ohne
gewaehlte Waffe bei 0,00, waehrend es mit Waffe 14 % traegt — und der
Berater sagt nicht, dass die Null an der fehlenden Waffe liegt. Das ist die
stille Fehlklasse, gegen die AD-013/AD-018 argumentieren.

**Vorschlag:** Eine Zeile in `unknowns` des waffenlosen Zweigs, die den
Umfang nennt („buffs tied to a weapon class are not in this figure — choose
an armament to see them"), oder — die schaerfere Variante — die
`class_rates` mit einbeziehen und den Umfang dann anders benennen. Die
Entscheidung, welche, gehoert dem `architect`/`ui-ux-designer`, weil sie die
Bedeutung der Zahl aendert.

---

### [P3 | Minor | Niedrig] QA-105 — Systemisch: die Vorbedingungspruefungen des Beraters nennen ihren Umfang zu weit

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/goals.py:195-215` · `nrplanner/advisor/candidates.py:156-191`

**Belegliste (jeder Fall einzeln nachgestellt):**

| Fall | Eingabe | Verhalten heute |
|---|---|---|
| a | `Weighting(weights=(("slashDamageCutRate", 0.0),))` | `ZeroDivisionError: float division by zero` — nackt |
| b | `Weighting(weights=(("slash…",1.0),("fire…",−1.0)))` | `ZeroDivisionError` — nackt |
| c | `Weighting(weights=(("slash…",−1.0),))` | still `Effective HP 1120` — plausibel und bedeutungslos |
| d | `Weighting(weights=(("nosuchDamageCutRate",1.0),))` | still `Effective HP 1120`; das unbekannte Feld geht als neutrale 1.0 ein |
| e | `Weighting(weights=(("fire…",1.0),("fire…",5.0)))` | `dict(...)` verwirft den ersten still |
| f | `Budget(candidates_per_slot=0)` | `shortlist` liefert leer, ohne Einwand; `beam_width` wird nirgends gelesen |
| g | `pools(..., rank_by="tippfehler")` ohne freien Slot | still `()`, weil `pool` nie gerufen wird (vom `developer` selbst als P4 gemeldet) |

**Erwartet:** Der Docstring von `_min_damage_taken` sagt: *„The two
preconditions a caller **can** get wrong are checked instead, because a
caller is not the dataset."*
**Tatsaechlich:** Es sind mehr als zwei, und die drei stillen (c, d, e) sind
schlimmer als die zwei lauten.

**Analyse:** Die Wurzel ist eine: die Randpruefungen sind fallweise gesetzt
und der Umfangssatz beschreibt sie als vollstaendig. Fall (d) ist im
Modul-Docstring sogar **vorhergesagt** („A field named here that the dataset
does not carry would be weighted into the average as a neutral 1.0 for ever,
and nothing would say so") — der zugehoerige Wächter
`test_the_eight_damage_kinds_are_the_ones_the_model_knows` haelt aber nur die
**ausgelieferte Konstante**, nicht eine vom Aufrufer uebergebene
`Weighting`.

**Auswirkung:** Heute keine — es gibt nur einen Aufrufer und eine
`Weighting`. **OF-3 ist genau die Frage, ob der Spieler ein Bedienelement
fuer diese Gewichte bekommt.** Sobald er es bekommt, sind (a) und (b) ein
Absturz aus dem Worker heraus, und (c) ist eine Rangliste ohne Bedeutung.

**Vorschlag:** Eine Pruefstelle statt sieben: `Weighting` beim Bauen
validieren (Summe > 0, Feldnamen gegen `DAMAGE_CUT_FIELDS`, keine
Doppelten) und den Umfangssatz im Docstring auf das eindampfen, was wirklich
geprueft wird. `Budget` und `rank_by` gehoeren in dieselbe Bewegung.

---

### [P3 | Major | Niedrig] QA-106 — Auf einem Runner ohne Spielinstallation prueft keiner der 107 neuen Faelle eine Zahl des Beraters

**Adressat:** director, developer
**Betroffen:** `tests/conftest.py` (`game_data`), `tests/test_advisor_*.py`

**Reproduktion:** In einer eigenen Extraktion `_snapshot_from_cache` und
`_snapshot_from_game` auf `None` und `installed_game` auf `pytest.skip`
setzen, `NIGHTREIGN_TEST_SNAPSHOT` aus der Umgebung nehmen, dann je Datei
`pytest -q -m "not slow"`.

**Erwartet:** Ein Teil der 107 Faelle rechnet; die Zahl 398 traegt auf einem
Runner ungefaehr das, was sie hier traegt.
**Tatsaechlich:** 61 von 107 laufen, 46 ueberspringen — und **von den 61
rechnet keiner**. 46 pruefen Datenklassenformen, 1 prueft, dass die Registry
schreibgeschuetzt ist, 14 pruefen, dass Textanker im Quelltext noch da sind.
Pruefpunkt 13 ueberspringt zweifach.

**Analyse:** Kein Fehler im Entwurf — `conftest.py` sagt ausdruecklich, dass
ein Runner keine Installation hat und das der richtige Zustand ist. Der
Befund ist die **Groesse** der Luecke: die 46 lauffaehigen Faelle sind
Formpruefungen, die 14 sind Tests des Messwerkzeugs. Wenn dieses Projekt je
CI bekommt, ist der Berater dort ungeprueft, und eine gruene Anzeige sagt es
nicht.

**Auswirkung:** Fuer den Nutzer heute keine (er ist der Runner). Fuer jede
kuenftige Automatisierung und fuer A9 (Pruefung gegen ein gebautes Artefakt)
eine grosse: 398 gruen auf einem Runner belegt vom Rechenkern des Beraters
nichts ausser seiner Form.

**Vorschlag:** Entscheidung des `director`, ob ein winziger, im Repo
liegender **synthetischer** Datensatz (ein paar Effekte, eine Kurve, eine
Waffe, ein Held — keine Spieldaten, keine Rechte) fuer die Faelle taugt, die
nur „eine Zahl bewegt sich in die richtige Richtung" behaupten. Das waere
die Trennung „Eigenschaft" gegen „echte Daten", die das Repo an anderer
Stelle (`slow`) schon fuehrt.

---

### [P3 | Minor | Mittel] QA-107 — `held_fingerprint` ist positionsunabhaengig, der als Cache-Schluessel benannte `AdvisorRequest` ist es nicht

**Adressat:** developer, architect (AD-016), director
**Betroffen:** `nrplanner/advisor/types.py` (`AdvisorRequest.held_fingerprint`, `held_fingerprint`) · `tests/test_advisor_types.py::test_where_a_relic_is_held_does_not_change_the_fingerprint`

**Reproduktion:**
```python
p1 = SlotProblem(slots, held=(HeldSlot(0, A), HeldSlot(1, B)))
p2 = SlotProblem(slots, held=(HeldSlot(0, B), HeldSlot(1, A)))
held_fingerprint(p1) == held_fingerprint(p2)          # True
AdvisorRequest(..., problem=p1) == AdvisorRequest(..., problem=p2)   # False
hash(...) == hash(...)                                 # False
```

**Erwartet:** Was der Fingerabdruck gleichsetzt, setzt auch der Schluessel
gleich — sonst beschreibt der Fingerabdruck nichts.
**Tatsaechlich:** gemessen wie oben.

**Analyse:** Der Modul-Docstring sagt: *„the cache key of AD-007/AD-016 is
the request object itself — there is **no second key form** that could
drift"*. `held_fingerprint` ist trotzdem da, ist eine zweite Schluesselform,
und ihre erklaerte Wirkung (AD-016 Option A wurde verworfen, weil „der
Picker, der sechs Slots nacheinander abgeht, jedes Mal den Cache verfehlen
wuerde") tritt nicht ein, solange der `AdvisorRequest` der Schluessel ist:
er traegt `problem.held` als **geordnetes Tupel**.
Der Wächter `test_where_a_relic_is_held_does_not_change_the_fingerprint`
prueft damit eine Eigenschaft, die der tatsaechliche Schluessel nicht hat.
Dieselbe Klasse wie QA-082 („Begruendung trifft den Code nicht") und
QA-087 („im Code richtig, im Nachweis nicht").

**Auswirkung:** Heute keine — es gibt keinen Cache. In S9 zwei moegliche
Ausgaenge: entweder der Fingerabdruck wird nie benutzt (dann sind Feld, Test
und AD-016-Begruendung tote Flaeche), oder jemand baut den Cache auf den
`AdvisorRequest` und wundert sich ueber die Trefferquote.

**Vorschlag:** In AD-016 entscheiden, welches der beiden der Schluessel ist,
und das andere entfernen oder ausdruecklich als Nebeninformation kennzeichnen.
Wenn `held_fingerprint` der Schluessel sein soll, muss der Wächter das
pruefen — heute prueft er den Fingerabdruck, nicht den Schluessel.

---

### [P3 | Minor | Niedrig] QA-108 — Bestand ohne Handles: jeder Pool leer, und die erklaerende Zeile sagt „of this colour" auch am weissen Slot

**Adressat:** ui-ux-designer (Wortlaut), director (Optionen A/B/C aus T-037)
**Betroffen:** `nrplanner/advisor/candidates.py:86-93` (`_without_a_handle_line`)

**Reproduktion:**
1. Bestand aus vier roten Kopien bauen, alle mit `handle=None`; Problem mit einem roten und einem weissen Slot.
2. `candidates.pools(...)` fahren.
3. Zweiter Fall: weisser Slot, zwei handle-lose rote Kopien, eine rote und eine blaue mit Handle.

**Erwartet:** Ein Text, der beschreibt, was tatsaechlich weggefallen ist.
**Tatsaechlich:**
```
Fall 1: slot 0 -> 0 candidates,  "4 owned relics of this colour are not offered: …"
        slot 1 -> 0 candidates,  dieselbe Zeile (also 6× dasselbe bei einem vollen Gefaess)
Fall 2: weisser Slot, angeboten: [('Antique', Farbe 0), ('Delicate Drizzly Scene', Farbe 1)]
        unknowns: "2 owned relics of this colour are not offered: …"
```

**Analyse:** `pool` zaehlt die handle-losen Kopien aus
`inventory.relics_for(slot.colour, slot.deep)`. Fuer den weissen Slot
(Farbe 4) liefert das **jede** Farbe — „of this colour" beschreibt dort
nichts. Zusaetzlich sagt die Zeile „N Relikte fehlen", waehrend die Wirkung
im Grenzfall „das ganze Merkmal ist dunkel" ist.

**Auswirkung:** Latent — auf diesem Save 0 von 309 ohne Handle, unabhaengig
nachgemessen. Der Wortlaut ist dagegen nicht latent: er trifft **jeden**
weissen Slot, sobald ueberhaupt eine Kopie ohne Handle im Bestand ist.

**Vorschlag:** Wortlaut ohne Farbaussage („N owned relics that fit this slot
…"). Fuer den Totalausfall die Option C des `developer` (eine eigene,
deutlichere Zeile, wenn **alle** Kandidaten betroffen sind) — der `director`
entscheidet zwischen A, B und C.

---

### [P4 | Trivial | Niedrig] QA-109 — `effect_ids_of` behauptet dieselbe Reihenfolge wie `Planner._rebuild`; sie ist es nicht

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/evaluate.py:41-52` (Docstring von `effect_ids_of`)

**Reproduktion:** Planner mit Deep an und drei verfluchten Relikten fuellen,
dann `[e["id"] for e in p.selected_effects() + p.weapon_effects() + curses]`
gegen `effect_ids_of(problem_from_planner(p), (), context_from_planner(p, data))`
halten.

**Erwartet (laut Docstring):** *„the same three sources `Planner._rebuild`
gathers, **in the same order**"*.
**Tatsaechlich:**
```
gleiche Multimenge?  True
gleiche Reihenfolge? False
```
`_rebuild` sammelt Relikteffekte, dann Waffeneffekte, dann **alle** Fluechte
am Ende; `effect_ids_of` sammelt je Relikt Effekte **und** Fluechte, dann die
Waffeneffekte.

**Analyse:** Ohne Wirkung auf eine Zahl: `sources`, `warnings` und
`attributes` waren im gemessenen Zustand identisch. Aber `Build.sources` ist
per AD-015 die Quelle, aus der S8 die Fluechte ausweist, und seine
Listenreihenfolge folgt der Effektreihenfolge. Bemerkenswert ist, wo der
Wächter steht: das `figures()`-Helferlein von Pruefpunkt 13 schliesst
`warnings` und `sources` **ausdruecklich aus** — also genau die zwei Felder,
in denen der Unterschied sichtbar waere.

**Auswirkung:** Heute keine. Fuer S8 eine Falle: wer den Docstring liest und
sich auf Reihenfolgegleichheit verlaesst, baut auf etwas, das nicht gilt.

**Vorschlag:** Docstring auf das korrigieren, was gilt („dieselbe Multimenge;
die Reihenfolge weicht ab und bewegt keine Zahl, weil …"), oder die
Reihenfolge angleichen und einen Fall darueber setzen. Ersteres ist billiger
und ehrlicher.

---

### [P4 | Minor | Niedrig] QA-110 — Pruefpunkt 18 („kein `QSettings` im Berater-Pfad") hat keinen Wächter

**Adressat:** developer
**Betroffen:** `tests/test_settings_store.py::test_no_source_opens_a_settings_store_of_its_own`

**Reproduktion:** Den Wächter lesen: er sammelt jede `QSettings`-Konstruktion
und beanstandet die, die **nicht** `favourites.ORG` / `favourites.APP`
uebergeben. Ein `QSettings(favourites.ORG, favourites.APP)` in
`nrplanner/advisor/worker.py` wuerde ihn passieren.

**Erwartet:** AD-009 Nachtrag II, Pruefpunkt 18: *„hier genuegt, dass unter
`advisor/` und im Haltezustand kein `QSettings` vorkommt"*.
**Tatsaechlich:** Die Eigenschaft haelt heute (zwei unabhaengige Suchen ueber
`nrplanner/advisor/` nach `QSettings` und nach `favourites`/`settings`:
0 Treffer), aber nichts haelt sie.

**Analyse:** Der bestehende Wächter prueft den **Namen** des Stores, der
Pruefpunkt verlangt den **Ort**. Zwei verschiedene Zusicherungen mit einem
Werkzeug.

**Auswirkung:** Erst ab S9/S10 relevant — dort entsteht der Haltezustand, und
OF-15 verbietet ausdruecklich, ihn zu persistieren („nach drei Datenverlusten
im QSettings-Schluesselraum … die tragende Begruendung").

**Vorschlag:** Eine Zeile im vorhandenen AST-Durchgang: kein Modul unterhalb
`nrplanner/advisor/` baut ueberhaupt einen Store. Gegenbau: ein `QSettings`
unter `advisor/` einsetzen und den Fall rot sehen.

---

### [P4 | Minor | Niedrig] QA-111 — A8 („alle nutzersichtbaren Zeichenketten Englisch") hat repo-weit keinen Wächter

**Adressat:** director, developer
**Betroffen:** `tests/` insgesamt

**Reproduktion:** Zwei unabhaengige Volltextsuchen ueber `tests/`
(„English"/„englisch"/„A8"/„language" und „umlaut"/„isascii"/„non_ascii"):
0 einschlaegige Treffer.

**Erwartet:** A8 ist ein Abnahmekriterium.
**Tatsaechlich:** Es wird von keinem Test gehalten. Der Bestand ist in
Ordnung — mein AST-Durchgang ueber alle einzeiligen String-Konstanten in
`nrplanner/advisor/` findet nur Englisch, und die von AD-010 verbotenen
Woerter kommen nicht vor —, aber das ist eine Momentaufnahme.

**Analyse:** Vorbestand, nicht von T-037 verursacht. Ich melde ihn hier, weil
dieser Auftrag das erste Paket ist, dessen Kommentare deutsch und dessen
Ausgaben englisch sind und in dem beide **in derselben Datei** stehen — das
ist die Konstellation, in der ein deutscher Satz versehentlich in ein
`display` rutscht.

**Auswirkung:** Ein deutscher Satz in einer Nutzerzeile faellt erst am
Artefakt auf (A9), also spaet.

**Vorschlag:** Ein AST-Wächter ueber `nrplanner/`, der einzeilige
String-Konstanten ausserhalb von Docstrings gegen eine kleine Sperrliste
haelt (Umlaute, „ss"-Woerter, die verbotenen Woerter aus AD-010).
Umfangsaussage dazuschreiben: er sieht keine zusammengesetzten Zeichenketten.

---

### [P4 | Trivial | Niedrig] QA-112 — `inventory.copy_key`s Begruendung trifft den Code nicht; die realen Wege zu `handle=None` sind andere

**Adressat:** developer
**Betroffen:** `nrplanner/inventory.py:47-70` (Docstring `copy_key`) · `nrdata/savefile.py::read_relic_handles` · `nrplanner/inventory.py:224-250`

**Reproduktion:** Die drei Stellen nebeneinander lesen.

**Erwartet:** *„a save whose loadout table cannot be read yields no handles
at all"*.
**Tatsaechlich:** `read_relic_handles(slot_data, owned)` liest den Handle aus
`relic.offset + HANDLE_OFFSET`, also aus dem **Relikt-Datensatz**. Die
Loadout-Tabelle liest `read_loadouts` getrennt, und ihr Scheitern faengt
`inventory.loadout_error`. Ein Save mit kaputter Tabelle hat sehr wohl
Handles.
Die zwei Wege, die es wirklich gibt: (i) `read_relic_handles` schluesselt
nach Handle (`out[handle] = relic`), zwei Datensaetze mit demselben
Handle-Wert kollabieren und der Verlierer bekommt `None`; (ii) `if off < 0:
continue`.

**Analyse:** Der `developer` hat (den ersten Teil) gemeldet; ich habe es
unabhaengig nachgelesen und bestaetige es und ergaenze die zwei realen Wege.
Klasse wie QA-082.

**Auswirkung:** Dokumentation. Aber die falsche Begruendung ist genau die,
auf der die Abwaegung zu AD-013.4 steht — sie wird gerade dem `director` zur
Entscheidung vorgelegt (Optionen A/B/C), und er sollte sie auf der richtigen
Grundlage treffen.

**Vorschlag:** Drei Zeilen Docstring. Und wenn der `director` Option B
erwaegt: die Handle-Kollision ist der Fall, an dem sich Handle und Offset
tatsaechlich unterscheiden.

---

## 11. Zusammenfassung (an den `director`)

**Befunde nach Prioritaet:** P1: 0 · P2: 3 (QA-100, QA-101, QA-102) ·
P3: 5 (QA-103 bis QA-108) · P4: 4 (QA-109 bis QA-112).
**Blocker: keiner.** Der Testlauf ist vollstaendig durchgefahren.

Der Rechenkern ist **handwerklich der beste Stand, den dieses Projekt bisher
abgeliefert hat**: 15 von 15 Mutationen unabhaengig nachgefahren, 15 von 15
Zahlen exakt, jede toetet aus dem richtigen Grund, Pruefpunkt 15 ist ueber
Objektidentitaet statt ueber Zahlengleichheit gesichert, und die Regression
am Fenster ist bei 297 abgezogenen Zeilen ueber 18 Konfigurationen bei
**null**. Releasefaehig ist er nicht und soll es nicht sein — es gibt weder
Suche noch Oberflaeche.

**Was vor S7/S9 mindestens gezogen gehoert:**
1. **QA-100** — der einzige Wächter, der den Berater gegen das Fenster haelt,
   haelt heute nichts. Vier `compute`-Argumente sind frei. S9 baut genau
   diesen Kontext; ohne den Fix entsteht der naechste QA-001 dort, wo ihn
   niemand sieht.
2. **QA-102** — die A7-Zusage auf dem Hauptweg. Sie braucht **eine
   Entscheidung von dir** (AD-010 gegen `UI_SPEC` AK-50), bevor S8/S10 auf
   einer der beiden Lesarten aufbauen.
3. **QA-101** — deine Entscheidung `equipped` steht in `docs/state.md` unter
   Vorbehalt „bis T-041 misst". Gemessen: die Behauptung ist falsch, die
   Entscheidung ist richtig. Die Begruendung im Repo gehoert getauscht,
   bevor sie jemand als Beleg weiterreicht.

Alles Uebrige kann in P7 mitlaufen.

---

## 12. Explorationsprotokoll

**Gefahren, und was gehalten hat:**
- 27 eigene Extraktionen (`git archive HEAD | tar -x`, nie `git worktree`),
  **26 volle Suitelaeufe** je ~90 s, plus ein `slow`-Lauf und ein Volllauf.
- 15 Mutationen des `developer` nachgefahren → **0 Abweichungen**.
- 9 eigene Gegenbauten gegen `evaluate.py` → 4 ueberleben die volle Suite.
- Zustandssonde am echten `Planner` in genau dem Zustand von Pruefpunkt 13.
- Reihenfolgenvergleich Fenster gegen Berater (Multimenge, `sources`,
  `warnings`, `attributes`).
- Gegenbeispiel-Kandidatensatz `equipped` gegen `candidate`, plus Auszaehlung
  der drei Traegereffekte im Datensatz und der 10 betroffenen Relikte im Save.
- Synthetischer Bestand ohne Handles, dazu der weisse Slot mit gemischten
  Farben.
- Fuenf Randfaelle der `Weighting`, drei Randwerte einer Durchlassrate.
- Klassengebundener Angriffsbuff mit und ohne Referenzwaffe.
- Runner-Simulation (conftest im Klon entschaerft), Faelle je Datei gezaehlt.
- UI-Differential `3650765` gegen `HEAD`, 18 Konfigurationen, 297 Zeilen.
- Hash-/Gleichheitsprobe `AdvisorRequest` gegen `held_fingerprint`.
- Statische Pruefungen: A8-AST-Durchgang, verbotene Woerter, `QSettings` unter
  `advisor/`, Importe des Pakets, `.spec`.

**Was gehalten hat und hier ausdruecklich als „geprueft, kein Befund" steht:**
die Farbregel und die Deep-Trennung (an `relics_for` delegiert, nicht
dupliziert); der Determinismus samt Zweitschluessel; Pruefpunkt 15 als
Objektidentitaet; die Hashbarkeit aller Antwortformen **auf der
Erzeugerseite**; die Ableitung des `held_fingerprint` statt seiner Speicherung
(die Begruendung gegen ein Feld ist richtig, unabhaengig von QA-107); der
AD-021-Wächter reicht wirklich in das neue Paket (`advisor-rates-an-armament-itself`
toetet genau eine Zeile); die Fluchbehandlung als gewoehnlicher Effekt ohne
Sonderweg; und die Messung „0 von 309 Relikten ohne Handle" (unabhaengig
nachgemessen, dazu 0 Handle-Kollisionen).

**Worauf ich mich verlassen habe, statt es zu wiederholen:** die Messungen
der parallelen Scaling-Session (`docs/berichte/T-038-qa-engineer.md`,
`T-043-qa-engineer.md`; QA-095 bis QA-099, der 0,6-Faktor, die
Raider-Anomalie, die Katalysator-Konstante) — nicht nachgefahren. Sie
beruehren diesen Auftrag an drei Stellen, und alle drei sind **Zukunft, nicht
Bestand**; ich habe am aktuellen Baum nachgesehen:
- **QA-095** (Spiel = `floor(0,6 × weapons.rate)`) trifft AD-014.6, das die
  **absolute** Zahl als „die eine Autoritaet" haelt. Der Nutzer hat am
  03.09.2026 entschieden („bake it in. no warning in the GUI necessary.",
  Auftrag T-045). Sobald das drin ist, **aendert sich jede Zahl, die dieser
  Rechenkern liefert, um den Faktor 0,6** — die Rangfolge nicht. Die
  Charakterisierungen des Beraters sind alle relativ (`>`, `< `, `== 0`),
  also erwarte ich **keinen** roten Fall daraus; genau deshalb ist es
  erwaehnenswert: der Einbau von T-045 wird an der Advisor-Suite
  **unsichtbar** vorbeigehen.
- **QA-096** (Raider ×1,1819) ist laut `docs/state.md` „ordnungsrelevant" und
  wird ohne Fundstelle nicht eingebaut. Fuer den Berater ist das heute
  folgenlos: er rankt Relikte bei **fester** Referenzwaffe, und ein
  waffentypgebundener Faktor kuerzt sich in dieser Differenz heraus. Sichtbar
  waere er erst, wenn eine Zielrichtung Waffen gegeneinander vergleicht — was
  AD-019/W6 bis auf Weiteres ausschliesst.
- **QA-099/T-046** (Katalysatoren): `docs/state.md` spricht von einem
  Vorbehaltssatz „in `README.md` und `advisor/goals.py`". **Den gibt es im
  Baum noch nicht** — zwei Suchen ueber `nrplanner/advisor/goals.py`
  („catalyst/staff/seal/spell", „0.6/calibrat/floor") finden nur die
  AD-004-Zeile „Spell damage is not in the game data…", und
  `git status nrplanner` ist leer. Meine Messungen stehen also gegen den
  unveraenderten Stand 89015aa.

Ebenso nicht nachgefahren: die Picker-Zeitmessung des `developer` (sie hat
ihr Skript im Repo, L-001 erfuellt) und die Zaehlung „309 Kopien, 306 Rollen"
des `architect`.

**Zum Arbeitsbaum waehrend meines Laufs:** die Zusage „Stand eingefroren"
galt fuer den **Anwendungscode** und hat gehalten — `git status` ueber
`nrplanner/`, `tests/` und `scripts/` ist am Ende meines Laufs leer, `HEAD`
ist unveraendert `89015aa`. Dokumente sind waehrenddessen sehr wohl
dazugekommen (`UI_SPEC.md`, `docs/state.md` und `qa/findings.md` geaendert;
`docs/archiv/`, `T-043`, `T-044`, `R-006`, `T-042` bis `T-046` neu). Das
betrifft meine Messungen nicht, aber es betrifft die Nummernvergabe: siehe
den Hinweis am Anfang von Abschnitt 16.

---

## 13. Offene Fragen

1. **An den `director`:** Gilt AD-010 („`unknowns` ist Teil des Ergebnisses,
   damit die Oberflaeche es nicht vergessen kann") fuer den Picker-Weg, oder
   gilt dort `UI_SPEC` §3.2/AK-50 (ein fester Satz ausserhalb der Karten)?
   Beide Lesarten sind vertretbar und schliessen einander aus. Von der
   Antwort haengt ab, ob `SlotPool` die `GoalScore`s tragen muss (QA-102).
2. **An den `director`:** Ist die fehlende Zeile „N of your relics carry
   effects that only apply under a condition. They were not counted."
   (AD-004, gemeinsame `unknowns`) auf S8/S9 verschoben oder uebersehen? Sie
   ist die einzige der gemeinsamen Zeilen, die laufabhaengig ist.
3. **An den `architect`/`director`:** AD-016 — ist der Cache-Schluessel der
   `AdvisorRequest` (positionsabhaengig) oder der `held_fingerprint`
   (positionsunabhaengig)? Heute sind beide da und behaupten Verschiedenes
   (QA-107).
4. **An den `architect`:** AD-009 vergibt die Nummer **18** zweimal
   (Nachtrag II: kein `QSettings`; Nachtrag III: untere Schicht bitgleich).
   Absicht oder Versehen?
5. **An den `director`:** QA-095 ist per Nutzerentscheid F4 („bake it in")
   auf T-045 gesetzt. Danach aendert sich **jede** Zahl dieses Rechenkerns um
   den Faktor 0,6, und **kein** Fall der Advisor-Suite wird davon rot — alle
   Charakterisierungen dort sind relativ. Soll T-045 einen
   Charakterisierungsfall auf einer **absoluten** Advisor-Zahl mitbringen
   (AD-014.6 haelt die absolute Zahl als die eine Autoritaet), oder wird die
   Kalibrierung bewusst nur an `weapons.rate` belegt? Das ist eine
   Scope-Frage zwischen zwei Auftraegen, keine, die ich entscheide.
6. **An den `ui-ux-designer`** (vom `developer` uebernommen, hier
   bestaetigt): es gibt zwei Saetze fuer den Attack-Rating-Vorbehalt — der
   aus AD-004 steht heute in `goals.py`, der aus T-024/DR-003 in `UI_SPEC`.
   Beide auszuliefern geht nicht.

---

## 14. Annahmen dieses Laufs

1. **`problem_from_planner` / `context_from_planner` sind die Form, die S10
   bauen wird.** Ihr Docstring sagt es so („This does the reading S10 will do
   in the window"). Waere das anders gemeint, waere Pruefpunkt 13 gar kein
   Wächter ueber dem Fenster, sondern nur ueber einer Testdatei — dann waere
   QA-100 schwerer, nicht leichter.
2. **Der Zustand des `Planner` beim Bau ist auf dieser Maschine
   repraesentativ.** Level 1 und eine gefuellte Waffenkachel sind
   Konstruktion (Slider ohne `setValue`, `apply_hero_weapon`), nicht Zufall
   des Saves; die 309 Relikte sind es nicht. Ein anderes Save aendert an
   QA-100 nichts (die vier ueberlebenden Mutationen haengen an Level, Held,
   Waffen — nicht am Bestand).
3. **Meine Runner-Simulation ist die richtige Nachbildung.** Ich habe
   `conftest.py` im Klon an drei Stellen entschaerft, statt eine Maschine
   ohne Spiel zu benutzen. Wer es genauer will, faehrt die Suite auf einem
   Rechner ohne NIGHTREIGN; die Zahlen sollten dieselben sein.

---

## 15. Nicht getestet

- **Suche, Erklaerung, Worker, Cache, Oberflaeche** (S7 bis S10) — existieren
  nicht. Damit sind AD-009 Pruefpunkte 5, 10, 17 offen und 8, 11, 12, 14 nur
  auf Typ-/Poolebene beruehrbar.
- **Ein gebautes Artefakt (A9)** — nie geprueft, in diesem Projekt noch von
  niemandem.
- **Performance** — die Zahlen des `developer` haben ihr Skript; S11 gehoert
  dem `performance-tuner`. Ich habe nichts nachgemessen.
- **Nebenlaeufigkeit** — es gibt keinen Thread. Ab S9 gehoeren Doppelklick,
  schneller Wechsel, Abbruch mitten im Lauf und Generationszaehler geprueft;
  heute nicht anwendbar.
- **Die 5 `slow`-Faelle inhaltlich** — gefahren (5 passed), aber sie liegen
  alle in `test_extraction.py` und beruehren den Berater nicht.
- **Zweites Save / zweiter Rechner** — nur das Save dieser Maschine.
- **QA-095 bis QA-099** — parallele Session, bewusst nicht wiederholt.

---

## 16. QA-Log — Fortschreibung fuer `qa/findings.md`

Fortgeschrieben, nicht neu begonnen; QA-095 bis QA-099 stammen aus
`docs/berichte/T-038-qa-engineer.md`/`T-043-qa-engineer.md` und bleiben
unberuehrt.

**Nummernvergabe geprueft, nicht angenommen (Stand 2026-09-03, nach meinem
Lauf):** `docs/state.md` Abschnitt „Zwei Sessions auf demselben Repo"
reserviert der Scaling-Session „QA-095 bis QA-099 samt a/b/c" und dieser
Session „**ab QA-100**". In `qa/findings.md` ist die hoechste vergebene
Nummer heute **QA-099**; `docs/berichte/T-043-qa-engineer.md` nennt QA-100
nur als *freien* Bereich („7.2 bis 7.4 brauchen Ids aus dem Audit-3-Kreis,
ab QA-100"), nicht als vergebene Id. **QA-100 bis QA-112 sind damit frei und
korrekt vergeben.** Sollte die Scaling-Session zwischen meinem Lauf und dem
Eintrag doch in denselben Kreis greifen, ist meine Liste geschlossen zu
verschieben — die Reihenfolge der Befunde untereinander traegt keine
Bedeutung.

Anzuhaengen:

```markdown
## Zyklus 12, T-041: Erstdurchlauf gegen den Rechenkern des Beraters (2026-09-03)

Quelle: `docs/berichte/T-041-qa-engineer.md`. Grundlage: T-037 (`developer`),
Commit 690db5f/6ab589a auf `docs/audit-and-advisor-design`. Nachweisweg: 27
frische `git archive`-Extraktionen, 26 volle Suitelaeufe. Die 15 Mutationen
des `developer` sind unabhaengig nachgefahren — **0 Abweichungen**. Neun
eigene Gegenbauten gegen `advisor/evaluate.py`, davon vier ueberlebend.
Regression am Fenster ueber 18 Konfigurationen: 0 Unterschiede.

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-100 | **Pruefpunkt 13 faengt keinen seiner eigenen Gegenbauten; vier der sieben `model.compute`-Argumente des Beraters sind ungewacht.** `weapons_held=[]`, `weapon=None`, `ctx.level→1` und `ctx.hero→heroes[0]` lassen je **398 passed** stehen. Ursache: der Testzustand ist entkernt (Level 1, eine Waffe = die Referenz, keine Waffeneffekte, `declared={}`, Deep aus, Wylder ist `heroes[0]`). Der Fall ist lebendig (Relikteffekte entfernt → rot), sieht aber genau das nicht, wofuer er gebaut ist. Klasse QA-070/073/083/086 | P1-Kandidat, eingestuft **P2** (Wirkung erst ab S9) | Major | developer | 9 Gegenbauten, je volle Suite im eigenen Baum; Planner-Zustandssonde | offen | 2026-09-03 |
| QA-101 | **„Die Rangfolge waere bei `candidate` dieselbe" ist widerlegt.** Drei Effekte (7120400/500/600) tragen die Startwaffen-Strafe ×0,85 selbst; ein Kandidat kann sie mitbringen. Gemessen: R0 `[7120400, 6001400]` → d(equipped) −12,36 gegen d(candidate) +21,36, R1 +0,83 in beiden → **Reihenfolge gedreht**. 10 von 309 Relikten des Saves betroffen. Die Entscheidung `equipped` ist damit **richtiger**, die Begruendung falsch — und sie steht als `survival_means` in `mutate.py` | P2 | Major | director, developer | Gegenbeispiel-Kandidatensatz, Effekt- und Bestandsauszaehlung | offen — Entscheid des Directors (Vorbehalt aus `docs/state.md` aufgeloest) | 2026-09-03 |
| QA-102 | **Der `SlotPool` — das Ergebnis des Hauptwegs — traegt keine A7-Zeile der Zielrichtungen.** `pool()` nimmt von `GoalScore` nur `.value`; `unknowns`, `weights_note`, `unit`, `display` fallen an der Poolgrenze weg. AD-004s gemeinsame Zeile ueber nicht gezaehlte konditionale Effekte existiert nirgends (zwei Suchen). Spec-Konflikt AD-010 (Pflichtfeld im Ergebnis) gegen `UI_SPEC` AK-50 (fester Satz ausserhalb der Karten) — nicht vom `qa-engineer` zu entscheiden | P2 | Major | director, developer | Codelesung + Pool-Ausgabe | offen | 2026-09-03 |
| QA-103 | **Annahme 6 („eine Durchlassrate ist nie null") steht nur im Docstring.** Gemessen: 0,0 → nackter `ZeroDivisionError`; −0,5 → still `Effective HP 700` statt 1120; 1e-12 → still `Effective HP 1,4e14`, was jede Rangliste anfuehrt und die gemessene Regel („non-positive 0") **nicht verletzt**. Einzige der sechs Annahmen, die A7 nicht erfuellt | P3 | Major | developer, director | drei Randwerte einzeln gefahren | offen | 2026-09-03 |
| QA-104 | **Ohne Referenzwaffe zaehlt ein klassengebundener Angriffsbuff exakt 0, und keine Zeile sagt es.** Gemessen: derselbe Effekt 0,000000000 ohne Waffe, +14,27 mit passender `ranged`-Waffe. 8 solcher Effekte im Datensatz. `_NO_ARMAMENT_NOTE` nennt den Geltungsbereich zu eng | P3 | Minor | developer, ui-ux-designer | Messung mit und ohne Referenzwaffe | offen | 2026-09-03 |
| QA-105 | **Systemisch: die Vorbedingungspruefungen des Beraters nennen ihren Umfang zu weit.** Der Docstring sagt „die zwei Vorbedingungen, die ein Aufrufer falsch machen kann"; es sind mehr: Gewichtssumme 0 → `ZeroDivisionError` (2 Faelle), negatives Gewicht → still falsche Zahl, unbekannter Feldname → still neutral 1.0, doppelte Schluessel → still verworfen, `Budget(0)` ungeprueft, `pools` prueft `rank_by` ohne freie Slots nicht. OF-3 (Bedienelement fuer die Gewichte) macht daraus einen Nutzerpfad | P3 | Minor | developer | sieben Faelle einzeln nachgestellt | offen | 2026-09-03 |
| QA-106 | **Auf einem Runner ohne Spielinstallation prueft keiner der 107 neuen Faelle eine Zahl des Beraters.** Gemessen (conftest im Klon entschaerft): 61 laufen, 46 ueberspringen — und die 61 sind 46 Formpruefungen, 1 Registry-Pruefung und 14 Tests des Messwerkzeugs. Pruefpunkt 13 ueberspringt zweifach. Die Zahl 398 traegt dort fast nichts vom Berater | P3 | Major | director, developer | Runner-Simulation, Faelle je Datei gezaehlt | offen | 2026-09-03 |
| QA-107 | **`held_fingerprint` ist positionsunabhaengig, der als Cache-Schluessel benannte `AdvisorRequest` ist es nicht.** Gemessen: Fingerabdruck gleich, Request und Hash verschieden. Der Wächter `test_where_a_relic_is_held_does_not_change_the_fingerprint` prueft damit eine Eigenschaft, die der Schluessel nicht hat; AD-016s Begruendung fuer die Positionsunabhaengigkeit tritt nicht ein. Klasse QA-082/QA-087 | P3 | Minor | developer, architect | Hash-/Gleichheitsprobe | offen | 2026-09-03 |
| QA-108 | **Bestand ohne Handles: jeder Pool leer, Zeile sagt „of this colour" auch am weissen Slot.** Synthetisch gebaut: 0 Kandidaten je Slot plus eine `unknowns`-Zeile (also nicht still, aber sechsmal dieselbe Teilausfall-Formulierung fuer einen Totalausfall). Am weissen Slot ist „of this colour" falsch — gemessen: zwei weggefallene rote Kopien, angeboten rot **und** blau. Latent (0 von 309 ohne Handle) | P3 | Minor | ui-ux-designer, director | synthetischer Bestand, zwei Faelle | offen | 2026-09-03 |
| QA-109 | `effect_ids_of` behauptet „the same three sources `Planner._rebuild` gathers, **in the same order**"; gemessen: gleiche Multimenge, **verschiedene Reihenfolge**. Ohne Wirkung auf eine Zahl (sources/warnings/attributes im Messzustand identisch), aber `Build.sources` ist per AD-015 die Quelle fuer S8 — und Pruefpunkt 13 schliesst mit `figures()` genau `warnings` und `sources` aus | P4 | Trivial | developer | Reihenfolgenvergleich am echten Planner | offen | 2026-09-03 |
| QA-110 | Pruefpunkt 18 („kein `QSettings` im Berater-Pfad") hat keinen Wächter: `test_no_source_opens_a_settings_store_of_its_own` prueft die **Namen** des Stores, nicht seinen **Ort** — ein `QSettings(favourites.ORG, favourites.APP)` unter `advisor/` passiert ihn. Eigenschaft haelt heute (zwei Suchen, 0 Treffer) | P4 | Minor | developer | Wächterlesung + zwei Suchen | offen | 2026-09-03 |
| QA-111 | **A8 („alle nutzersichtbaren Zeichenketten Englisch") hat repo-weit keinen Wächter** (zwei unabhaengige Suchen ueber `tests/`, 0 einschlaegige Treffer). Bestand in Ordnung: AST-Durchgang ueber `nrplanner/advisor/` findet nur Englisch, die von AD-010 verbotenen Woerter kommen nicht vor. Vorbestand, hier gemeldet, weil `advisor/` das erste Paket mit deutschen Kommentaren und englischen Ausgaben in derselben Datei ist | P4 | Minor | director, developer | AST-Durchgang + zwei Suchen | offen | 2026-09-03 |
| QA-112 | `inventory.copy_key`s Begruendung trifft den Code nicht (vom `developer` gemeldet, hier unabhaengig verifiziert): `read_relic_handles` liest aus dem **Relikt-Datensatz**, nicht aus der Loadout-Tabelle. Die zwei realen Wege zu `handle=None` stehen nirgends: (i) `read_relic_handles` schluesselt nach Handle, kollidierende Datensaetze kollabieren; (ii) `off < 0` wird uebersprungen. Gemessen: 0 handle-lose und 0 kollidierende Handles auf diesem Save. Klasse QA-082 | P4 | Trivial | developer | drei Stellen gelesen, Save nachgemessen | offen | 2026-09-03 |

**Bestaetigt, kein Befund (T-041):** die 15 Mutationen des `developer`
reproduzieren exakt; der AD-021-Wächter reicht wirklich in `advisor/`; die
Regression am Fenster ist null (18 Konfigurationen, 297 Zeilen, 0
Unterschiede); Pruefpunkt 15 ist ueber Objektidentitaet gesichert; die
Hashbarkeit ist auf der **Erzeugerseite** belegt; Farbregel und
Deep-Trennung sind an `inventory.relics_for` delegiert statt dupliziert;
`0 von 309` Relikten ohne Handle unabhaengig nachgemessen; die `slow`-Faelle
sind gruen (5 passed, alle in `test_extraction.py`, keiner beruehrt den
Berater); volle Suite mit `slow`: **403 passed**.
```
