# T-079 - developer

```
STATUS: teilweise
AUFTRAG: T-079 - Die drei Befunde der Erstpruefung (QA-180, QA-181, QA-182)
GELESEN: docs/tasks/T-079.md (mit dem GOAL.md-Zitat A4/A5 und dem
         docs/state.md-Auszug, beide tragen den Auftrag) ·
         docs/berichte/T-077-qa-engineer.md (Abschnitte 2 und 3 vollstaendig,
         Gliederung ganz) · nrplanner/model.py (Build, compute) ·
         nrplanner/advisor/{explain,evaluate,candidates,search,types,
         goals,__init__}.py · nrplanner/app.py (_show_breakdown,
         _ar_breakdown_text, active_slots) · tests/conftest.py ·
         tests/advisor_cases.py · tests/test_advisor_{explain,evaluate}.py ·
         tests/test_{move_scoped_effects,breakdown_sources_wiring,
         differential_track}.py · scripts/differential/mutate.py ·
         .gitattributes, pytest.ini, requirements-dev.txt, .github/workflows
GEAENDERT: nrplanner/model.py · nrplanner/advisor/explain.py ·
         nrplanner/app.py · tests/advisor_cases.py ·
         tests/test_advisor_explain.py · tests/test_advisor_evaluate.py ·
         tests/test_move_scoped_effects.py ·
         scripts/differential/mutate.py · docs/berichte/T-079-developer.md
         (diese Datei). Alle sieben Code-Dateien sind in drei Commits
         committet (90ff81d, 6f54445, 219909d); `git status` ist sauber bis
         auf diesen Bericht. Kein push, kein Branch-Wechsel.
ANNAHMEN: (1) Der Auftrag nennt keinen Nightfarer, kein Level und keine
         Referenzwaffe fuer die Abnahme-Stichprobe am echten Spielstand. Ich
         habe T-077s Umgebung uebernommen: Level 15, Referenzwaffe wie
         `advisor_cases.scaling_armament` sie waehlt, alle 74 Gefaesse, Deep
         an und aus, beide Richtungen. (2) Die vier geteilten Grale
         (hero_type 11) gehoeren keinem Nightfarer; ich frage sie mit
         `heroes[0]` ab - das ergibt T-077s 296 Laeufe statt 280.
         (3) `int(eff["id"])` in `model.compute` ist gefahrlos: dieselbe
         Zeile liest `eff["id"]` schon 60 Zeilen weiter oben ohne Fallback.
NAECHSTER: director
BLOCKIERT DURCH: nichts inhaltlich. Offen sind nur zwei Bestaetigungslaeufe,
         die beim Erreichen der Werkzeuggrenze noch liefen - siehe
         Abschnitt 7.
```

---

## 1. Was umgesetzt wurde

### QA-180 - die Zuordnung laeuft ueber die Effekt-Id

**Entscheidung und Grund.** `Build.sources` fuehrt jetzt
`model.SourceEntry(name, own, effect_id)` statt eines nackten Paares.

Die drei Wege, die zur Wahl standen:

* **ein zweiter, id-gefuehrter Weg neben `sources`** (parallele Liste je
  Feld) - verworfen: zwei Listen, die Index fuer Index zusammenpassen
  muessen, sind eine Invariante, die niemand prueft;
* **den Anspruch einer Kopie auf die Felder beschraenken, die ihr Effekt
  erzeugen kann** - verworfen: das ist die zweite Rechnung, die AD-015
  verbietet (T-077 hat es selbst so eingeordnet);
* **die Id in den Eintrag** - gewaehlt. Ein Ort, eine Wahrheit, und der
  Eintrag sagt selbst, von wem er kommt.

`NamedTuple` und nicht ein drittes Tupelfeld ohne Namen, damit die Leser
`entry.name` / `entry.own` schreiben statt `entry[0]` / `entry[1]`.

**Was daran haengt:**

* `model.compute` schreibt `SourceEntry(label, own, int(eff["id"]))`;
* `explain._added` verrechnet einen Eintrag nur noch gegen einen Eintrag
  **desselben Effekts** (Id inbegriffen);
* `explain._attributed` vergleicht `entry.effect_id != effect_id` statt
  `entry != name`. Der Name bleibt, was die Zeile sagt; die Id ist, was
  sagt, wessen Zahl es ist;
* `app.py::_show_breakdown` und `_ar_breakdown_text` lesen `.name`/`.own`;
  die klassengebundene Zeile baut ihren Eintrag mit `entry._replace(...)`
  statt ein Paar neu zu bauen. Die Anzeige ist unveraendert - kein Text,
  kein Format, keine Reihenfolge bewegt sich.

### QA-181 - die Vielfachheit ist bewacht

`tests/test_advisor_evaluate.py::test_each_source_of_an_effect_reaches_the_
model_exactly_once`. Die Erwartung ist eine **Multimenge**, gebaut aus den
drei Eingaben (gehaltene Relikte des Problems, Zuweisung, Waffeneffekte des
Kontexts), nie aus dem Rueckgabewert. Der Fall weigert sich, leer
durchzulaufen: jede der vier Quellen muss etwas tragen.

### QA-182 - Zahl und Ordnung von `not_counted` sind bewacht

`tests/test_advisor_explain.py::test_what_was_not_counted_keeps_its_number_
and_its_order`. Ein gestellter `Build` mit vier gated Effekten, einer davon
live, zwei der drei uebrigen namensgleich; die Erwartung steht woertlich als
`("Gamma", "Alpha", "Alpha")` da. Ein `set()` liefert zwei statt drei
Eintraege, ein `sorted()` fuehrt mit dem falschen an - zwei verschiedene
Antworten, keine davon gruen.

---

## 2. Der wichtigste Satz des Auftrags: der Waechter benutzt einen anderen Schluessel

Der alte Abnahmefall prueft ueber **Namen** und konnte die Namensverwechslung
deshalb nicht sehen. Die beiden neuen Faelle pruefen etwas anderes:

* `test_two_effects_of_one_name_are_credited_to_the_slot_that_carries_them` -
  der kleinste Fall aus dem Befund, mit **zwei verschiedenen Effekten
  desselben Namens in zwei Slots** (7000090 Vigor +5, 6610400 Max HP +10 %).
  Behauptet wird die Zeile als Ganzes samt **Slotnummer**, woertlich
  hingeschrieben. Der geteilte Name ist in beiden Zeilen derselbe - genau
  deshalb kann dieser Fall nicht dieselbe Frage stellen wie der alte;
* `test_a_name_two_effects_share_in_this_dataset_still_lands_on_two_slots` -
  dieselbe Regel gegen den Datensatz. Das Paar wird **gesucht**
  (`advisor_cases.two_effects_the_dataset_gives_one_name`) und nur
  angenommen, wenn die beiden **disjunkte** Felder bewegen; was jeder der
  beiden bewegt, wird `model.compute` auf dem einzelnen Effekt gefragt, nie
  `explain`. Auf diesem Datensatz faellt die Wahl auf 320000 / 8990010
  (beide `Improved Magic Attack Power`, das eine bewegt Magic Attack und vier
  Damage-Cut-Raten, das andere Critical damage).

---

## 3. Abnahme - beide Stichproben

### Erste Stichprobe: der kleinste Fall aus dem Befund

Skript `scratchpad/repro_smallest.py`, zwei rote Slots, nichts gehalten,
Kopie 1 mit 7000090, Kopie 2 mit 6610400.

**Vorher** (Baum `git archive HEAD` von c74d409):

```
Slot 1, Vigor relic — Increased Maximum HP: Vigor +5
Slot 1, Vigor relic — Increased Maximum HP: Max HP +10.0%
```

**Nachher** (Arbeitsbaum):

```
Slot 1, Vigor relic — Increased Maximum HP: Vigor +5
Slot 2, Max HP relic — Increased Maximum HP: Max HP +10.0%
```

`built.sources` nachher:
`{'Vigor': [SourceEntry(name='Increased Maximum HP', own=5,
effect_id=7000090)], 'maxHpRate': [SourceEntry(name='Increased Maximum HP',
own=1.1000000238418579, effect_id=6610400)]}`

### Zweite Stichprobe: der echte Spielstand

Skript `scratchpad/sweep.py`, gefahren gegen **zwei Baeume** mit demselben
Skript: `git archive HEAD` (= c74d409) und den Arbeitsbaum.

**Zaehlweg** (mein eigener, nicht aus einer Notiz uebernommen): 74 Gefaesse x
Deep an/aus x 2 Richtungen = **296 Laeufe**; je Lauf die **zwei** besten
Vorschlaege erklaert = **592 Vorschlaege**, **2664** belegte Slots; der
**erste** jedes Laufs ist der "beste Vorschlag" (**296**). Deep an heisst
`Planner.active_slots`: die Deep-Reihe **kommt zur** gewoehnlichen dazu, also
sechs Slots statt drei - ohne das kommt man auf 280 Laeufe und 1680 Slots und
misst etwas anderes. Eine Zeile ist **falsch**, wenn das Feld, das sie nennt,
kein Feld ist, das der genannte Effekt bewegt; gefragt wird `model.compute`
auf diesem **einen** Effekt (`Build.sources` plus `collapse_by_label`), nie
`explain`. Ein Slot ist **stumm**, wenn der Vorschlag eine Kopie
hineinlegt und keine Zeile diesen Slot nennt.

| Groesse | vorher (c74d409) | nachher | T-077 |
|---|---|---|---|
| Laeufe | 296 | 296 | 296 |
| Vorschlaege | 592 | 592 | 592 |
| belegte Slots | 2664 | 2664 | 2664 |
| Begruendungszeilen | 9568 | 9568 | 10 322 |
| **falsch zugeordnete Zeilen** | **130** | **0** | 130 |
| stumme Slots (alle 592) | 47 | **0** | 46 |
| stumme Slots (296 beste) | 23 | **0** | 23 |
| davon mit bewegter Rangzahl | 23 | 0 | 23 |
| sha256 ueber alle Rangzahlen | `ad69f0b2…` | `ad69f0b2…` | - |

**Die Aussage, die der Auftrag braucht:** **0 von 9 568** falsch zugeordneten
Zeilen und **0 von 2 664** stummen Slots, davon **0 von 296** in den besten
Vorschlaegen.

**Wo ich von T-077 abweiche, offen gesagt.** Fuenf der sechs Zahlen decken
sich exakt (296 / 592 / 2664 / 130 / 23-von-23); die stummen Slots ueber alle
Vorschlaege liegen bei 47 gegen 46. Den **Nenner der Zeilen** habe ich nicht
reproduziert: ich zaehle 9 568, T-077 zaehlt 10 322, eine Differenz von 754
(7,3 %). Die Vermutung, T-077 habe die Fluchzeilen (`explain.curses`)
mitgezaehlt, traegt nicht - das waeren 963, macht 10 531. Ich kann nicht
sagen, wo die 754 herkommen, und schreibe deshalb meinen eigenen Nenner hin
statt seinen zu uebernehmen. Der **Zaehler** ist derselbe: 130 vorher, 0
nachher.

### Die Rangzahlen sind nicht angefasst

Der Sweep bildet ueber **alle 592** Vorschlaege einen sha256 aus
`(Gefaess, Deep, Richtung, Rang, Handles, Rangzahl)`.

* vorher: `ad69f0b2af2b0446d98abbeb09c9910cfd6d108e76f630b7f5604dc4dc5512b1`
* nachher: `ad69f0b2af2b0446d98abbeb09c9910cfd6d108e76f630b7f5604dc4dc5512b1`

**Beisst die Probe?** Ja - derselbe Baum ueber ein Gefaess gibt
`ad2b709f…`, ueber zwei `c4fc9008…`. Der Digest reagiert auf seinen Inhalt.

---

## 4. Rot-vorher, je Gegenbau (L-007, L-008)

Alle Gegenbauten sind in `scripts/differential/mutate.py` eingetragen und
wurden mit `mutate.py --apply … --tree …` auf **Kopien** des Baumes
angewandt (kein `.git` darin, wie das Werkzeug es verlangt). **Welcher Fall
rot wurde, steht dabei** - die Ankerpruefung
`test_every_mutation_still_finds_its_anchor_in_the_real_source` ist in keinem
dieser Belege der rote Fall.

### Die vier neuen Gegenbauten

| Gegenbau | rot geworden ist | Lauf |
|---|---|---|
| `explain-attributes-a-figure-by-name-instead-of-by-id` | `…two_effects_of_one_name_are_credited_to_the_slot_that_carries_them` **und** `…a_name_two_effects_share_in_this_dataset_still_lands_on_two_slots` | 2 failed, 34 passed |
| `model-records-a-source-without-saying-which-effect` | u. a. `…a_name_two_effects_share_in_this_dataset_still_lands_on_two_slots`, `…the_reasons_name_only_effects_the_suggestion_brought`, `…a_stacking_effect_on_three_copies_is_named_once_per_copy` | 7 failed, 29 passed |
| `advisor-counts-each-chosen-copy-twice` | **nur** `…each_source_of_an_effect_reaches_the_model_exactly_once` | 1 failed, 35 passed |
| `explain-loses-the-count-of-what-was-not-counted` | **nur** `…what_was_not_counted_keeps_its_number_and_its_order` | 1 failed, 35 passed |

Fuer QA-181 und QA-182 ist der Gegenbau **genau die Mutation, die T-077
gefahren hat** (zweites `ids.extend(candidate.effect_ids)`; `not_counted`
durch ein `set()`, verankerte Zeile ansonsten unangetastet). Dass jeweils
**nur** der neue Fall faellt, ist der Beleg dafuer, dass vorher nichts
zusah - dieselbe Beobachtung, aus der T-077s Befund entstand.

### Die vier neu verankerten alten Gegenbauten

Mein Umbau von `_added`/`_attributed` hat vier bestehende Anker unbrauchbar
gemacht. Sie sind auf die neue Quelle nachgezogen und toeten weiter - jeder
einzeln angewandt, jeder faellt genau bei dem Fall, den sein
`survival_means` nennt:

| Gegenbau | rot geworden ist |
|---|---|
| `explain-reasons-against-the-empty-build` | `…a_copy_whose_effect_the_held_relic_already_caps_is_not_credited` (1 failed) |
| `explain-renders-every-figure-in-the-build` | `…the_reasons_name_only_effects_the_suggestion_brought` und 7 weitere |
| `explain-lets-one-copy-claim-every-entry-of-its-name` | `…a_stacking_effect_on_three_copies_is_named_once_per_copy` (1 failed) |
| `explain-credits-every-copy-with-the-same-entry` | `…a_copy_whose_effect_the_game_refused_to_stack_gets_no_line` (1 failed) |

**Kein Gegenbau hat ueberlebt.** Waere einer ueberlebt, staende er hier als
Befund und nicht als stiller Nachbesserungsauftrag an mich selbst.

---

## 5. Eigenschaft statt Fundstelle (L-006)

Gesucht wurde projektweit, mit drei voneinander unabhaengig formulierten
Masken, nach **jeder** Stelle, die einen Effekt ueber seinen Namen
identifiziert statt ueber seine Id.

| Maske | Ausdruck | Treffer | Ergebnis |
|---|---|---|---|
| 1 | jeder Vergleich gegen einen Namen: `(name\|label)\s*(==\|!=\|in)` und Umkehrung, ueber `nrplanner/` + `nrdata/` | 36 Zeilen, davon 1 ueber einen Effektnamen | `explain.py:275` `label == contribution.effect_name` - das ist ein **Anzeige**-Vergleich ("den Namen nicht zweimal sagen"), keine Zuordnung. Bleibt. |
| 2 | Effekte, die nach Namen gruppiert oder nachgeschlagen werden: `[…name…]`, `setdefault(name`, `get(name` | 28 Zeilen | keine betrifft Effekte; alles Dateinamen, Attributnamen, Waffennamen, Buildnamen. |
| 3 | die Faltungsformel, unter der `sources` seinen Namen bildet: `" ".join(str(…name…).split())` | 18 Zeilen (11 im Programm) | drei sind Anzeige (`effectstab`, `effecttext`, `weaponslots`), eine ist `explain._effect_name` (bleibt, ist die Beschriftung), eine ist `model.compute` selbst (behoben), eine ist `extract.py:2779` (parst den **eigenen** Namen eines Effekts auf Statwoerter - keine Identifikation), eine ist `app.py:3144` (siehe unten), eine ist `model.py:987` (siehe Befund unten). |

**Mitbehoben:** `model.compute` (die Ursache) und `explain._attributed` (die
Fundstelle). **Nicht mitbehoben, gemeldet:** die zwei Stellen unten.

---

## 6. Was mir aufgefallen ist und nicht in den Auftrag gehoerte

**An den `director`, ohne Nummer:**

**(a) Der Ausschliesslichkeits-Hinweis unterdrueckt sich selbst, wenn zwei
Ids einen Namen teilen.** `nrplanner/model.py:983-990` bildet das Paar aus
zwei **Namen** und ueberspringt es bei `pair[0] == pair[1]`. Zwei
verschiedene Effekte einer `exclusivityId`, die denselben Namen tragen,
bekaemen also keinen Hinweis - dieselbe Eigenschaft wie QA-180, eine andere
Stelle. **Nachgezaehlt, bevor ich es melde:** auf diesem Datensatz 29
Gruppen, 456 Paare, davon **0** betroffen. Heute also folgenlos; es wird
folgenreich, sobald ein Patch zwei gleichnamige Effekte in eine Gruppe legt.
Aufwand klein (Paar ueber die Id bilden, Namen nur anzeigen). Ich habe es
nicht angefasst: es ist nicht der Auftrag, und der Hinweistext waere dann
zweimal derselbe Name, was eine Wortlautfrage fuer den `ui-ux-designer` ist.

**(b) `app.py:3142-3155` fuehrt die On-Hit-Statuszeilen ueber den
Effektnamen.** Zwei gleichnamige Effekte, die denselben Status aufbauen,
erscheinen dort als zwei Zeilen mit einem Namen. Das ist eine
Anzeige-Doppelung, **keine** Fehlzuordnung - die Summe stimmt. Ich melde es,
weil es dieselbe Maske trifft; Handlungsbedarf sehe ich nicht.

**(c) Zwei Zahlen aus T-077 habe ich nachgerechnet, weil ich sie in
Docstrings schreibe:** 2076 Effekte tragen **707** verschiedene Namen, davon
**160** auf mehr als einer Id - beides bestaetigt. Den Zeilennenner 10 322
konnte ich nicht bestaetigen (Abschnitt 3).

**(d) Zeilenenden.** Sechs der bearbeiteten Dateien lagen nach meinen
Skript-Schreibvorgaengen mit CRLF im Arbeitsbaum, wo `.gitattributes`
`eol=lf` vorgibt. Vor dem ersten Commit auf LF zurueckgesetzt; die Commits
enthalten keine Zeilenenden-Aenderung (`git diff --stat` zeigt nur die
inhaltlichen Zeilen).

**(e) Der Auftrag nennt unter "Rahmen" `NH-002: keine Bildschirmabzuege.
Dieses Repo ist oeffentlich.` `CLAUDE.md` dieses Projekts sagt
`Kategorie: privat`.** Ich habe keine Bilder erzeugt, die Regel ist also
folgenlos eingehalten - aber die beiden Saetze widersprechen sich, und wer
das naechste Mal ein Bild braucht, liest je nach Datei etwas anderes. Zur
Klaerung an den `director`.

---

## 7. Testergebnis, ausgefuehrte Befehle, offene Laeufe

**Ausgangslauf, frischer Baum von c74d409** (`git archive HEAD | tar -x`):

```
.venv\Scripts\python.exe -m pytest -q -m "not slow"
952 passed, 9 skipped, 5 deselected in 477.19s (0:07:57)
```

Das deckt sich mit der Zahl im Auftrag.

**Lauf nach der Arbeit, Arbeitsbaum, byte-identisch mit dem committeten
Stand** (per `diff` gegen die drei aufgeteilten Dateien bestaetigt):

```
.venv\Scripts\python.exe -m pytest -q -m "not slow"
960 passed, 9 skipped, 5 deselected in 481.57s (0:08:01)
```

**+8 aufgeschluesselt:** 4 neue Faelle (2x QA-180, 1x QA-181, 1x QA-182) und
4 neue Parametrierungen von
`test_every_mutation_still_finds_its_anchor_in_the_real_source`, weil vier
Gegenbauten dazugekommen sind. 952 + 8 = 960, keine Zeile fehlt.

**Nicht geprueft:** die `slow`-Faelle (lesen das installierte Spiel; nicht
Teil des im Auftrag benannten Laufs). Ein Lauf gegen ein gebautes Artefakt
oder gegen eine Oberflaeche ist nicht moeglich, S9/S10 existieren noch
nicht. Linter: das Projekt hat keinen konfiguriert (kein `.flake8`, kein
`ruff.toml`, kein `pyproject.toml`, `requirements-dev.txt` = pytest allein,
`.github/workflows` ruft keinen) - der DoD-Punkt entfaellt.

**STATUS teilweise, und warum genau:** Beim Erreichen der Werkzeuggrenze
liefen noch zwei **Bestaetigungs**-Laeufe. Inhaltlich fehlt nichts, und kein
Ergebnis haengt an ihnen, das ich nicht schon anders belegt haette:

1. **`pytest -q -m "not slow"` im frischen Klon des committeten Standes**
   (Ausgabe nach `scratchpad/verify-run.txt`). Der Rahmen verlangt die Zahl
   aus dem frischen Klon; ich habe sie vom Arbeitsbaum (960 passed) und den
   Nachweis, dass Arbeitsbaum und Commit byte-identisch sind. Die
   Klon-Bestaetigung steht aus.
2. **Volle Standardlaeufe der vier neuen Gegenbauten** (Ausgabe nach
   `scratchpad/full-<name>.txt`). Ich habe fuer alle vier den **gezielten**
   Lauf ueber `tests/test_advisor_explain.py` +
   `tests/test_advisor_evaluate.py` (Tabelle in Abschnitt 4) - beide Dateien
   sind Teil der Standardauswahl, ein rotes Ergebnis dort faerbt den
   Standardlauf rot. Was aussteht, ist die volle Zeile
   `n failed, m passed` je Mutant.

**Konkreter naechster Schritt fuer den, der uebernimmt:** die beiden Laeufe
starten bzw. ihre Ausgaben lesen und die Zahlen in diesen Bericht
nachtragen. Kein Code haengt daran, es ist kein uncommitteter Stand offen,
und ich habe nichts zurueckgebaut.

---

## 8. Commits

| Commit | Titel |
|---|---|
| `90ff81d` | `fix(advisor): attribute a figure to the effect's id, not to its name (QA-180)` |
| `6f54445` | `test(advisor): hold how often an effect reaches the model, not only which (QA-181)` |
| `219909d` | `test(advisor): hold the count and the order of what was not counted (QA-182)` |

Drei Commits, weil es drei Befunde sind; die Aufteilung ist mit der Hand
gemacht (Bloecke aus `mutate.py` und den zwei Testdateien heraus- und
wieder hineingesetzt) und der Endstand ist per `diff` als identisch mit dem
Stand nachgewiesen, der 960 passed und die Sweep-Zahlen erzeugt hat. Kein
Formatierungs- und Logik-Gemisch in einem Commit. Kein `push`, kein
`branch`, kein `stash`, kein `checkout`; gearbeitet wurde auf dem
ausgecheckten `docs/audit-and-advisor-design`.

---

## 9. An den `qa-engineer`

Was ich fuer pruefenswert halte, ueber die drei Befunde hinaus:

* **Die Kante, die mein Datensatz-Fall nicht erreicht:** zwei gleichnamige
  Effekte, die **dasselbe** Feld bewegen. Mein Helfer
  `two_effects_the_dataset_gives_one_name` waehlt ausdruecklich ein Paar mit
  **disjunkten** Feldern, weil nur so eine Fehlzuordnung sichtbar wird. Bei
  gleichem Feld ist die Zuordnung ueber die Id weiter richtig, aber kein
  Fall zeigt das - die beiden Zeilen waeren nicht auseinanderzuhalten. Ob
  das eine Luecke ist oder eine Eigenschaft, kann ich nicht entscheiden.
* **Ein gehaltenes Relikt und eine vorgeschlagene Kopie mit zwei
  gleichnamigen, verschieden-idigen Effekten.** `_added` verrechnet jetzt
  nur noch gegen denselben Effekt; vorher hat der Basiszustand einen
  fremden, gleichnamigen Eintrag schlucken koennen. Mein Sweep faehrt
  **ohne** gehaltene Slots (wie T-077s erster Rundlauf); der Halte-Rundlauf
  mit dieser Kante ist ungefahren.
* **Die Aufschluesselung im Fenster** (`_show_breakdown`,
  `_ar_breakdown_text`). Ich habe die Leseart geaendert, nicht den Text;
  `tests/test_breakdown_sources_wiring.py` und die Golden-Faelle sind gruen,
  aber es gibt keinen Fall, der den **gerenderten** Tooltip liest. Ein
  Blick von aussen waere hier mehr wert als noch ein Fall von mir.
* **`explain.not_counted` gegen den echten Spielstand.** Mein Fall stellt
  den `Build` selbst hin. Dass `model.compute` auf 309 Relikten wirklich 199
  solcher Eintraege mit Doppelnennungen parkt, ist T-077s Zahl und von mir
  nicht nachgerechnet.

## 10. An den `ui-ux-designer`

Keine Abweichung. Kein Wortlaut, kein Format und keine Reihenfolge einer
Zeile hat sich geaendert - die Zeilen stehen nur unter dem Slot, der sie
verdient hat. Die Halte-Zeile aus T-077s Befund 4 und die Wortlaute aus
T-078 sind ausdruecklich nicht dieser Auftrag und sind nicht angefasst.

---

## Nachtrag des Directors, 06.09.2026 — die beiden offenen Laeufe sind gelesen

Der `developer` konnte die Ausgaben am Ende seines Laufs nicht mehr oeffnen
und hat den Status deshalb zu Recht auf `teilweise` gelassen. Ich habe die
Dateien gelesen; **STATUS ist damit `erledigt`.**

**Frischer Klon** (`git archive HEAD | tar -x`, eigener Lauf des Directors,
Stand mit dem Fix): **960 passed, 9 skipped, 5 deselected**. Der Lauf des
`developer` (`scratchpad/verify-run.txt`) zeigt dieselbe Zahl.

**Die vier Gegenbauten im vollen Standardlauf** — jeder toetet, und der im
Bericht benannte Fall ist jeweils dabei:

| Mutation | Ergebnis | benannter Fall gefallen |
|---|---|---|
| `advisor-counts-each-chosen-copy-twice` | 2 failed, 958 passed | `test_each_source_of_an_effect_reaches_the_model_exactly_once` |
| `explain-attributes-a-figure-by-name-instead-of-by-id` | 5 failed, 955 passed | `test_two_effects_of_one_name_are_credited_to_the_slot_that_carries_them` |
| `explain-loses-the-count-of-what-was-not-counted` | 3 failed, 957 passed | `test_what_was_not_counted_keeps_its_number_and_its_order` |
| `model-records-a-source-without-saying-which-effect` | 8 failed, 952 passed | `test_the_reasons_name_only_effects_the_suggestion_brought` |

**Eine Beobachtung dazu, die der `qa-engineer` in T-077 vorhergesagt hat:**
In jedem der vier Laeufe faellt zusaetzlich
`test_every_mutation_still_finds_its_anchor_in_the_real_source`, bei der
dritten Mutation sogar fuer einen **fremden** Mutationsnamen. Dieser Test
prueft kein Verhalten, sondern nur, ob der Anker noch im Quelltext steht —
wer ihn als Toetungsbeleg zaehlt, zaehlt nichts. Die vier Toetungen oben
stehen unabhaengig davon, jede an einem Verhaltensfall.
