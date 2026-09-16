# T-081 - Die Sprache des Beraters einbauen (developer)

```
STATUS: teilweise
AUFTRAG: T-081 - Die Sprache des Beraters einbauen (developer)
GELESEN: docs/tasks/T-081.md · UI_SPEC.md (T-078-Abschnitt AK-133 bis AK-150,
  T-080-Nachtrag AK-151 bis AK-161, Director-Korrektur vom 06.09.2026 am
  Dateiende) · nrplanner/advisor/explain.py, types.py, evaluate.py ·
  nrplanner/model.py (Build, SourceEntry, Situational, compute_qualitative,
  GATE_FIELDS, CONDITIONAL_FIELDS, is_conditional) · nrplanner/effecttext.py
  (name, owner, works_for) · tests/test_advisor_explain.py,
  test_advisor_types.py, advisor_cases.py · scripts/differential/mutate.py
  (die 26 Mutationen mit Anker in explain.py) · tests/test_differential_track.py
  · scripts/measure_advisor_picker.py
GEÄNDERT: nrplanner/advisor/explain.py · nrplanner/advisor/types.py ·
  tests/test_advisor_explain.py · tests/test_advisor_types.py ·
  scripts/differential/mutate.py · scripts/measure_advisor_language.py (neu)
ANNAHMEN: fünf, unten einzeln aufgeführt (Vorrangregel der Zählzeile;
  Datenform der beiden neuen Felder; namenloser Fluch bekommt keine Zeile;
  Aufzählungszeichen sind nicht Teil des Textes; Herkunft der Fuellung (a)/(c)
  aus dem Effektsatz statt aus Build.qualitative)
NÄCHSTER: director
BLOCKIERT DURCH: nichts - der Auftragsumfang ist eingebaut und committet.
  Offen ist eine einzelne uncommittete Zeile in scripts/measure_advisor_language.py
  (Details unten) sowie alles, was ausdrücklich S10 gehört.
```

**Warum `teilweise` und nicht `erledigt`:** der Lauf ist beim Aufruflimit
abgebrochen worden, bevor ich die letzte Änderung committen konnte. Der
gesamte Auftragsumfang (die sieben Punkte) ist eingebaut, getestet und in drei
Commits; **uncommittet ist genau eine Datei**, siehe „Uncommitteter Stand".

---

## 1. Testergebnis

| Lauf | Ergebnis | Dauer |
|---|---|---|
| **vorher**, mein Arbeitsbaum, vor der ersten Zeile Code | `960 passed, 9 skipped, 5 deselected` | 464,34 s |
| **nachher**, **frischer Klon** auf Commit `41c4301` | `985 passed, 9 skipped, 5 deselected` | 446,32 s |

Befehl beide Male: `.venv\Scripts\python.exe -m pytest -q -m "not slow"`,
Windows 10, Python aus `.venv`, Branch `docs/audit-and-advisor-design`.
Der frische Klon lag unter dem Scratchpad, geklont aus dem Arbeitsbaum
(`git clone . <tmp>`), gelaufen mit dem `python.exe` des Arbeitsbaums, weil
der Klon kein eigenes `.venv` hat. `git log --oneline -1` im Klon: `41c4301`,
`git status` im Klon: leer.

Der Ausgangswert deckt sich mit der Zahl aus dem Auftrag (960/9/5, Lauf des
`director` aus dem frischen Klon). 25 Fälle sind dazugekommen, keiner ist
weggefallen oder deaktiviert.

## 2. Commits

| Commit | Inhalt |
|---|---|
| `91fbe36` | `fix(advisor): sage die Halte-Zeile und die data_note in Nutzersprache` - die Wortlaute aus §8, dazu QA-183 |
| `d301ac8` | `feat(advisor): jede Zeile kennt ihren Slot, ihren Fluch und ihr Schweigen` - die Struktur, die Fluchfüllungen, die stummen Effektzeilen, die Zählzeile, die beiden neuen Felder |
| `41c4301` | `test(advisor): miss die Sprache des Beraters am echten Spielstand` - das Messskript, der Quelltext-Wächter über die verbotenen Sätze, die Satzzeichenregel |

Kein `push`, kein `pull`, kein `checkout`, kein `stash`, keine
Historienänderung. Der Branch ist unverändert `docs/audit-and-advisor-design`.

## 3. Uncommitteter Stand - bitte zuerst lesen

`scripts/measure_advisor_language.py` trägt **eine uncommittete Änderung**:
die Zeile über die höchste Karte, die ein einzelnes besessenes Relikt
erzeugen kann, nennt jetzt **Block und Dialog getrennt** statt nur den Dialog
(AK-161 verlangt beide Orte). Konkret: `worst` ist ein Dreier-Tupel statt
eines Zweier-Tupels, und die `print`-Zeile nennt den zweiten Wert mit.

**Diese Fassung ist nach der Änderung nicht mehr ausgeführt worden** - der
Lauf wurde vom Aufruflimit unterbrochen, und `git commit` war da schon
gesperrt. Das ist eine Lücke, kein Beleg. Die gemessenen Zahlen unten stammen
alle aus dem Stand von `41c4301`; die Änderung betrifft nur die ausgegebene
Zeile, nicht die Zählung. **Nächster Schritt:**
`.venv\Scripts\python.exe scripts\measure_advisor_language.py` einmal laufen
lassen und die Datei committen (oder verwerfen - der Rest des Skripts ist
committet und läuft).

Sonst ist der Arbeitsbaum sauber.

## 4. Was umgesetzt ist, Punkt für Punkt

**1. Die vier Wortlaute (§8).** `_held_slots_line` und `data_note` in
`explain.py`. Die Halte-Zeile endet nicht mehr auf `scored.`, die `data_note`
sagt nicht mehr `from the stored snapshot`, sondern **wann** gelesen wurde
(`read from your game files just now` / `earlier and kept since`). Das Wort
`snapshot` kommt im Beraterpaket nicht mehr vor.

**2. Die Slotnummer fällt aus der Zeile.** `_line` schreibt nur noch
`{Effektname}: {Größe} {Zahl}[, counted against it]`. `Slot 4, <Relikt> — `
steht im Kopf der Gruppe.

**3. Die drei Fluchfüllungen** in `_curse_lines`. Füllung (ii) ist aus zwei
Zeilen eine geworden: die Zahl stand in `reasons`, der Satz
`A curse on <relic> changes <field>, which this goal does not rank.` in
`unknowns`. `unknowns` trägt jetzt nur noch die Halte-Zeile und hat deshalb
die Signatur `unknowns(problem)`.

**4. Die sechs stummen Effektfüllungen** in `_silent_effect`, in der Reihenfolge
a → a2 → b → c → d → e, die erste zutreffende gewinnt.

**5. `not_counted` unverändert** (AD-010, konditionale Effekte aus
`Build.situational`). Die Trennung, die 4.9a von 4.9b trägt, liegt jetzt in
den Feldern: `curses_without_a_figure` neben `not_counted`. Die
Statuszeilenklauseln selbst erzeugt niemand - siehe „Was hier nicht entsteht".

**6. QA-183:** `is`/`are` folgt den gehaltenen Slots, `was`/`were` dem Rest.

**7. Die strukturierte Rückgabe.** `types.ReasonLine` (Slot, Text,
`is_curse`, `silence`) und `types.SlotReasons` (Slot, Reliktname,
`effects_total`, `effects_with_a_figure`, `count_line`, `lines`).
`Suggestion.reasons` trägt jetzt `tuple[SlotReasons, ...]`.
`types.drawn_in_the_block(line)` entscheidet Block gegen Dialog auf der Form,
nicht auf den Worten.

**Die Director-Korrektur** ist an zwei Stellen eingebaut:
`drawn_in_the_block` lässt jeden Fluch in den Block und hält die stummen
Effektzeilen im Dialog; und `types.SILENT_ANOTHER_NIGHTFARER` ist eine eigene
Auskunft, an der S10 `NOT WORKING` mit Durchstreichung setzen kann, während
der **Wortlaut** der aus §4 (a) bleibt, weil er den Besitzer nennt.

## 5. Abnahme, erste Stichprobe: die synthetischen Fälle

25 neue Fälle in `tests/test_advisor_explain.py`, dazu zwei angepasste in
`tests/test_advisor_types.py` (die beiden neuen Formen werden dort gehasht und
auf `frozen` geprüft, wie jede andere).

Je Füllung mindestens ein Fall: (a) und (d) am selben Effekt auf zwei
Nightfarern (AK-152s eigener Prüfweg), (a2) zweimal - zweite Kopie eines
`isStrongestEffect` und gehaltenes Relikt, das den Effekt schon deckt -,
(b) mit erklärter Bedingung in beiden Richtungen (AK-154), (c) am
Waffengatter, (e) an einer Effekt-Id, die der Datensatz nicht kennt.
Fluchfüllungen (i)/(ii) an einem Fluch unter beiden Zielrichtungen, (iii) an
einem Fluch ohne jede Zahl. Zählzeile in fünf Füllungen parametrisiert, dazu
zwei aus dem Datensatz. AK-155 (`{total} − {n}` = Zahl der stummen Zeilen)
wird in jedem parametrisierten Fall und in **jedem der 309 Relikte** des
Messlaufs als `assert` mitgeprüft.

## 6. Abnahme, zweite Stichprobe: der echte Spielstand

**Messumgebung (L-009).** Datensatz `nightreign_data.json` aus dem
Nutzerverzeichnis, `data_version` **10350000**, 2076 Effekte. Spielstand des
App Designers über `nrplanner.inventory.load`, **nur lesend**, **309 Relikte**.
Nightfarer **Wylder**, **Stufe 15**, seine Startwaffe als Bezugswaffe und als
einzige geführte Waffe, **keine** Bedingung erfüllt erklärt,
`goals.DEFAULT_WEIGHTING`. Windows 10, Python aus `.venv`, 06./07.09.2026.
Alle Zahlen sind **Zeilen und Zeichen, keine Pixel**.
Rezept: `.venv\Scripts\python.exe scripts\measure_advisor_language.py`,
Stand `41c4301`. Teil 1 setzt je Relikt **eine** Kopie in **einen** Slot
gegen einen Grundzustand ohne Reliktwirkung und wertet mit `explain.reasons`
selbst aus - kein Nachbau der Zeilenlogik.

**845 Effektrollen auf 309 Relikten, davon 426 ohne Zahl.** 272 Relikte
tragen mindestens einen stummen Effekt, 49 tragen keinen einzigen Effekt mit
Zahl.

| Füllung | mein Lauf | ui-ux-designer (T-080 §4) |
|---|---|---|
| (a) works only for another Nightfarer | **150** von 426 | 150 |
| (a2) another copy is already counted | **0** von 426 | nicht gemessen |
| (b) waits on a condition | **170** von 426 | 170 |
| (c) depends on the armaments carried | **13** von 426 | 58 |
| (d) no number here | **93** von 426 | 48 |
| (e) not in the game data | **0** von 426 | 0 |

**142 Fluchzeilen** über dieselben Relikte: (i) 56, (ii) 19, (iii) 67.

**Die Zählzeile**, nach ihrem ersten Wort: `1 of its …` 116, `2 of its …` 107,
`Nothing on this relic …` 46, `All …` 35, `None of its …` 3, `Its one effect …` 2.
Die Füllung `This relic carries no effects of its own.` kommt auf diesem
Spielstand **nicht** vor - `Murk`, `Sovereign Sigil` und `Scenic Flatstone`
liegen nicht im Inventar; sie ist nur synthetisch belegt.

**Höchste Karte eines einzelnen besessenen Relikts: 16 Zeilen** einschließlich
der beiden Kopfzeilen, auf **`Deep Grand Tranquil Scene`** - genau das Relikt
und genau die Zahl aus AK-160, unabhängig nachgemessen. Für dieses Relikt sind
Block und Dialog gleich hoch: seine drei Effekte bewegen alle eine Zahl, die
Korrektur nimmt ihm also keine Zeile.

**AK-161, Zeilen je Vorschlag** (40 Vorschläge des Beam über `Wylder's Chalice`,
sechs freie Slots, Richtung `Maximise damage`; je Gruppe zwei Kopfzeilen
mitgezählt):

| Ort | Spanne | Median |
|---|---|---|
| ganzer Vorschlag, **Block** | 33 bis 47 Zeilen | 38 |
| ganzer Vorschlag, **`Why`-Dialog** | 39 bis 50 Zeilen | 43 |
| eine Slotgruppe, Dialog | 5 bis 10 Zeilen | 8,5 |

**Längste Zeile: 153 Zeichen** -
`[Wylder] Standard attacks enhanced with fiery follow-ups when using Character Skill (greatsword only): only applies under a condition, so no number here.`
(T-080 §4 schätzte „rund 150"; die 106-Zeichen-Zahlzeile aus AK-160 bleibt die
längste Zeile **mit** Zahl.)

Die Zahlen aus T-067 (10 bis 43 Zeilen, Median 21) tragen damit nicht mehr:
der Median ist von 21 auf 43 gestiegen, weil jeder Effekt und jeder Fluch
jetzt eine Zeile bekommt statt nur die mit Zahl.

**Über dieselben 40 Vorschläge: 204 stumme Effektzeilen** - (a) 46, (a2) **0**,
(b) 64, (c) 0, (d) 94, (e) 0. Das ist der einzige Ort, an dem (a2) überhaupt
entstehen kann (mehrere Slots), und es entsteht dort nicht.

**Die dritte Zahl, vor der der Auftrag gewarnt hat:** T-067 zählt 36 Relikte
mit stummem Fluch, T-080 zählt 52. Mein Lauf zählt die Fluchzeilen, nicht die
Relikte: 67 Zeilen der Füllung (iii) über 309 Relikte. Ich habe die drei
Zahlen **nicht** gegeneinander gerechnet; sie messen verschiedene Dinge in
verschiedenen Umgebungen.

## 7. Abweichung von den Zahlen des ui-ux-designer

**(c) 13 statt 58, (d) 93 statt 48. Die Summe stimmt exakt: 106 in beiden
Zählungen** - die Grenze zwischen den beiden Füllungen liegt verschieden,
sonst nichts. (a), (b), (e), die 426, die 272 und die 49 stimmen auf den
Kopf überein.

Ich habe nachgerechnet, woher der Unterschied kommt, und finde die 58 mit der
in §4 (c) **angeschriebenen** Regel nicht wieder: baut man sie nach - ein
stummer Effekt, dessen `Build.qualitative`-Begründung `only with a matching
weapon type`, `needs several of that weapon equipped` oder `changes the
armament's skill` enthält, geprüft nach (a) und (b) wie die Reihenfolge es
verlangt -, kommen auf demselben Spielstand **12** heraus, nicht 58. Meine
Regel (dasselbe Gatter, am Effektsatz statt am Begründungstext gelesen) gibt
13. Die beiden weichen um genau einen Fall voneinander ab.

Das heißt nicht, dass 58 falsch ist - es heißt, dass die Zahl aus einer
anderen Regel stammt als der, die in der Vorgabe steht. **An den
`ui-ux-designer`:** welche Menge waren die 58? Solange das offen ist, ist die
Grenze zwischen (c) und (d) die einzige Stelle dieser Vorgabe, an der Einbau
und Messung auseinandergehen.

Nebenbefund derselben Rechnung: **226 Effekte des Datensatzes** erfüllen (b)
**und** (c) gleichzeitig (Waffengatter, das der Spieler als Schalter erklären
kann). Die Reihenfolge entscheidet sie für (b). Das ist so gewollt (§4:
„die erste zutreffende gewinnt"), erklärt aber, warum (c) klein ausfällt.

## 8. Rot-vorher-Belege (L-007, L-008)

Vierzehn Gegenbauten, jeder einzeln in den Quelltext eingesetzt und wieder
zurückgenommen, jeder **im Standardlauf** (`-m "not slow"`) rot, und jeder von
einem **Verhaltensfall** getötet - nicht von
`test_every_mutation_still_finds_its_anchor_in_the_real_source`.

| # | Gegenbau | erster tötender Fall |
|---|---|---|
| 1 | `'was' if rest == 1 else 'were'` → immer `were` | `test_the_two_counts_of_the_held_line_each_take_their_own_verb` |
| 2 | alte Halte-Zeile (`…, scored.`) wieder eingesetzt | `test_every_slot_held_says_that_nothing_was_searched` |
| 3 | alte `data_note` (`from the stored snapshot`) wieder eingesetzt | `test_the_data_note_names_the_version_and_where_it_was_read` (+2 weitere) |
| 4 | Zeile trägt wieder `Slot n, <Relikt> — ` | `test_a_stacking_effect_on_three_copies_is_named_once_per_copy` |
| 5 | Fluchzeile ohne `is_curse` | `test_a_curse_is_among_the_reasons_as_a_cost_that_was_counted` |
| 6 | stumme Zeilen fallen ersatzlos weg | `test_a_copy_whose_effect_the_held_relic_already_caps_is_not_credited` |
| 7 | Füllung (a2) feuert nie | `test_a_copy_whose_effect_the_held_relic_already_caps_is_not_credited` |
| 8 | (c) vor (b) geprüft | `test_an_effect_that_fits_two_fillings_takes_the_earlier_one` |
| 9 | Füllung (a) feuert nie | `test_an_effect_of_another_nightfarer_says_whose_it_is` |
| 10 | „Nothing on this relic" auch dort, wo ein Fluch eine Zahl bewegt hat | `test_a_copy_whose_curse_moved_a_number_is_not_told_nothing_moved` |
| 11 | Zählzeile zählt Zeilen statt Effekte | `test_the_heading_counts_effects_and_not_the_lines_they_produced` |
| 12 | Fluch ohne Zahl bekommt keine Zeile | `test_a_curse_to_which_no_figure_was_written_is_still_named` |
| 13 | `drawn_in_the_block` → immer `True` | `test_every_curse_of_the_suggested_copy_stands_in_the_block` |
| 14 | `curses_without_a_figure` nimmt **jede** Fluchzeile | `test_the_two_lists_of_what_carried_no_figure_are_the_lines_themselves` |
| 15 | `unfelt` wird nie gefüllt | `test_a_curse_the_direction_cannot_feel_is_named` |
| 16 | Zahlzeile bekommt einen Schlusspunkt | `test_a_line_that_ends_on_a_figure_carries_no_full_stop` (+7 weitere) |
| 17 | verbotene Behauptung über die Spieldateien wieder eingebaut | `test_the_advisor_carries_none_of_the_barred_sentences_at_all` (+2 weitere) |

**Ein Gegenbau hat zuerst überlebt** (Nr. 14, L-008 c): `curses_without_a_figure`
gab jede Fluchzeile zurück statt nur die ohne Zahl, und die Suite blieb grün -
mein Fall trug damals nur einen Fluch **ohne** Zahl, also konnte er die beiden
Mengen nicht unterscheiden. Der Fall trägt jetzt zusätzlich einen Fluch **mit**
Zahl und behauptet das ausdrücklich, bevor er die Listen vergleicht; danach
tötet er den Gegenbau. Ich melde ihn hier, statt ihn still nachzubessern.

**Nicht als Rot-vorher zu lesen:** vier Mutationen des Differentialkatalogs
ankern auf Zeilen, die ich geändert habe. Ich habe ihre `old`-Fassung auf den
neuen Quelltext gezogen, ihre Aussage unverändert gelassen und zwei
`survival_means`-Texte nachgeführt, die die alten Zeichenketten zitierten:
`explain-does-not-say-that-nothing-was-searched`,
`explain-does-not-say-where-the-data-came-from`,
`explain-interpolates-a-version-that-is-not-there`,
`explain-says-nothing-about-the-held-slots`. Die übrigen 22 Anker sind
unberührt - `_added`, `_attributed`, `_scales`, `_amount`, `_is_a_cost`,
`_field_label`, `not_counted`, `curses`, `chosen_for` und die beiden
Fluch-Mutationen habe ich bewusst zeichengenau stehen lassen.

**Die 14 neuen Gegenbauten sind nicht in den Katalog aufgenommen.** Sie stehen
hier mit Fundstelle und Opfer; ob sie als Mutationen nach
`scripts/differential/mutate.py` gehören, entscheidet der `director` - es wären
14 Einträge und ein eigener Lauf.

## 9. Annahmen (bitte gegenlesen)

1. **Vorrang in der Zählzeile.** Eine Kopie, die gar nichts bewegt hat, bekommt
   `Nothing on this relic moved a number in this build — …` **auch dann, wenn
   sie genau einen Effekt trägt** - also vor `Its one effect moved no number in
   this build.`. T-080 §5 nennt die neue Füllung als Ersatz für
   `None of its {total} effects …` und sagt zum Einzeleffekt nichts. Ich habe
   für den informativeren Satz entschieden, weil er die Frage beantwortet, die
   der Spieler dann stellt. `This relic carries no effects of its own.` gewinnt
   weiterhin über beides. Auf dem Spielstand betrifft die Entscheidung 46
   Relikte; wie viele davon einen einzigen Effekt tragen, habe ich nicht
   getrennt gezählt. **An den `ui-ux-designer`.**
2. **`curses_without_a_figure` und `effects_without_a_figure` tragen
   `ReasonLine`-Objekte, nicht Namen** - und zwar **dieselben** Objekte, die
   auch in den Slotgruppen stehen, nicht Kopien. Grund: §4 verlangt „dieselbe
   Zuordnung zu einem Slot wie die übrigen Zeilen", ein Name allein trägt keinen
   Slot, und Füllung (e) hat überhaupt keinen Namen, den man in eine Namensliste
   schreiben könnte. Die Anzahl ist die Länge, wie bei `not_counted`.
3. **Ein Fluch, den der Datensatz nicht kennt, bekommt keine Zeile.** Ein
   **Effekt** in derselben Lage bekommt eine (Füllung e), weil die Zählzeile
   sonst nicht aufgeht (AK-155). Für Flüche gibt es keinen Nenner, und einen
   Wortlaut für den namenlosen Fluch nennt die Vorgabe nicht.
4. **`•` und `✦` sind nicht Teil des Textes.** Sie stehen in §7 als
   Aufzählungszeichen des Fensters; die Zeile trägt `is_curse`, und S10 setzt
   das Zeichen. Sonst müsste die Anzeige den Text lesen, um zu wissen, was sie
   zeichnet - genau das, was AK-147 verbietet.
5. **Die Herkunft der Füllungen (a) und (c).** Siehe den nächsten Abschnitt -
   das ist die einzige bewusste Abweichung vom Buchstaben der Vorgabe.

## 10. Abweichung vom Buchstaben der Vorgabe: T-080 §7 Punkt 6

§7 Punkt 6 verlangt, die Füllung aus derselben Rechnung zu lesen, die
`Build.qualitative` und `Build.situational` füllt, und den Effektsatz **nicht
ein zweites Mal** zu lesen.

Für **(b)** ist das wörtlich erfüllt: `Build.situational` trägt `effect_id`,
und ich vergleiche über die **Id** - dieselbe Menge, aus der `not_counted`
gespeist wird, was AK-154 verlangt.

Für **(a)** und **(c)** ist es nicht erfüllbar, ohne einen bekannten Fehler zu
wiederholen: **`Build.qualitative` ist eine Liste von `(name, detail, why)`
und trägt keine Effekt-Id.** Ein Rücklesen könnte nur über den **Namen**
zuordnen - und genau das ist QA-180, das auf diesem Spielstand 130 falsche
Zeilen erzeugt hat (160 der 707 Effektnamen dieses Datensatzes werden von mehr
als einer Id getragen). Zusätzlich müsste die Zuordnung den Begründungstext
zerlegen.

Ich lese die beiden Füllungen deshalb am Effektsatz, aber **mit den Funktionen
des Modells**, nicht mit einer zweiten Meinung: `effecttext.works_for` ist
dieselbe Funktion, die `compute_qualitative` fragt, und die vier Gatterfelder
sind die Schlüssel aus `model.GATE_FIELDS`. Ein Testfall
(`test_the_armament_gates_are_the_ones_the_model_names`) hält meine Liste
gegen die des Modells, damit sie nicht auseinanderlaufen. `explain.py` liest
`ctx.data["effects"]` ohnehin schon - für den Namen jeder Zeile.

**An den `director`:** die saubere Behebung ist, dass `Build.qualitative`
seine Effekt-Id trägt. Das ist eine Änderung in `model.py` mit Wirkung auf
`app.py` und gehört zu QA-185 („`model.py:983-990`, `app.py:3142` führen über
Namen"), das der Auftrag ausdrücklich ausklammert. Ich habe es **nicht**
angefasst.

## 11. Was hier nicht entsteht (damit es niemand voraussetzt)

* **AK-141**, der Schlusssatz mit der `✦`-Legende: ein fester Satz ohne
  Laufeingabe, gehört in den `Why`-Dialog und damit zu S10.
* **AK-143**, die Statuszeilenklauseln 4.9a und 4.9b
  (`{n} curses carry no number.`, `{n} effects were left out: …`): ebenfalls
  S10. Die beiden Zahlen dafür stehen jetzt bereit
  (`len(curses_without_a_figure)`, `len(not_counted)`).
* **Die Überschrift aus 4.9b** (`These effects only apply under a condition,
  so this ranking did not count them:`): S10.
* **AK-147 als Grep über den Anzeigecode:** nicht durchführbar, weil es keinen
  Anzeigecode gibt, der Beraterergebnisse liest - ich habe im ganzen Baum
  gesucht (`explain`, `AdvisorResult`, `reasons`), es gibt bis heute keinen
  Aufrufer außerhalb der Tests. Die strukturelle Hälfte ist gebaut; der Grep
  gehört in die Abnahme von S10.
* **AK-149**, Maskierung und `setTextFormat`: `explain.py` bleibt Qt-frei und
  trifft keine Annahme über Markup; das Escapen gehört nach S10.
* **AK-160**, die Messung am laufenden Fenster: nicht gemacht, es gibt kein
  Fenster für den Berater. Meine 16-Zeilen-Zahl ist eine **Zeilen**-Zahl, kein
  Pixel.

## 12. An den `director`: Befunde, Debt, Risiken

1. **`Build.qualitative` trägt keine Effekt-Id** (`nrplanner/model.py`,
   `compute_qualitative`, Feld `Build.qualitative`). Wirkung: jede
   Rückzuordnung dieser Liste kann nur über den Namen laufen - die
   QA-180-Fehlerklasse. Aufwand: klein in `model.py` (Tupel um die Id
   erweitern), mittel in `app.py`, wo die Liste gezeichnet wird. Risiko heute:
   keins in `explain.py`, weil ich den Weg umgangen habe; hoch für jeden, der
   es später doch über den Namen versucht. Verwandt mit QA-185.
2. **`explain.curses()` steht im alten Format.** Es liefert weiterhin
   `Slot 1, <Relikt> — <Fluch>: <Zahl>` und ist damit die letzte Stelle im
   Programm, die die Slotnummer in den Text schreibt. Gezeichnet wird es nie
   (§6 Punkt 4, AK-148), AD-010 verlangt das Feld. Ich habe es **nicht**
   angefasst, weil es nicht im Auftrag stand. Entscheidung nötig: soll
   `AdvisorResult.curses` künftig Namen tragen (wie `not_counted`) oder das
   Feld ganz entfallen, da die Fluchzeilen jetzt in `reasons` markiert sind?
3. **Füllung (a2) ist spezifiziert, eingebaut und auf diesem Spielstand nie
   beobachtet** - 0 von 426 bei einem Relikt je Lauf und 0 von 204 über 40
   Sechs-Slot-Vorschläge. Sie ist synthetisch zweifach belegt (nicht stapelnder
   Effekt auf zwei Kopien; gehaltenes Relikt, das den Effekt schon deckt). Kein
   Fehler, aber die Zahl gehört neben die anderen fünf.
4. **Die (c)/(d)-Abweichung** aus Abschnitt 7 - Frage an den
   `ui-ux-designer`, keine Codefrage.
5. **Zwei Altlasten in `tests/test_advisor_search.py`**, beide grün und beide
   nicht von mir angefasst, weil sie zu S7 gehören: Zeile 796 übergibt
   `reasons=("a line",)`, was seit dieser Änderung nicht mehr dem Typ
   entspricht (der Fall prüft nur, dass `dataclasses.replace` ein anderes
   Objekt liefert, und besteht weiterhin); der Moduldocstring in Zeile 13
   zitiert die abgelöste Formulierung „the build as it stands, scored".
6. **Sicherheitsbefunde: keine.** Der Berater verarbeitet weiterhin nur den
   Datensatz und den Spielstand, beide nur lesend; das Messskript schreibt
   nichts. Keine Secrets, keine neuen Abhängigkeiten - `effecttext` und
   `model` sind Projektmodule, sonst ist nichts dazugekommen.
7. **Performance:** `reasons` wertet je Fluch mit Zahl **einmal** die ganze
   Belegung neu aus (AD-015, unverändert aus dem Bestand). Neu ist, dass ich
   das Bewerten überspringe, wenn kein Fluch eine Zahl bewegt hat - vorher lief
   `goal.score(built, ctx)` immer. Für 40 Vorschläge über sechs Slots war der
   Messlauf nicht spürbar langsamer als vorher; ich habe **nicht** gemessen.
   Wenn S9 den Berater in den Hintergrund legt, ist das die Stelle, die der
   `performance-tuner` ansehen sollte, nicht ich.

## 13. An den `qa-engineer`

* **Die Wortlaute** stehen wörtlich in den Tests, nicht importiert. Wer sie
  gegen `UI_SPEC` prüfen will, findet sie in
  `tests/test_advisor_explain.py::test_the_heading_of_a_group_says_which_case_this_is`
  (Zählzeile), in den sechs Füllungsfällen und in
  `test_the_data_note_names_the_version_and_where_it_was_read`.
* **Kanten, die ich für die interessantesten halte:** ein Relikt ohne jede
  Effektrolle (`Murk`, `Sovereign Sigil`, `Scenic Flatstone`) - im Inventar des
  App Designers nicht vorhanden, deshalb nur synthetisch belegt; ein Effekt,
  der zwei Größen bewegt, gegen die Zählzeile (AK-146); eine Effekt-Id, die der
  Datensatz nicht kennt, gegen AK-155; dieselbe Bedingung erklärt und nicht
  erklärt, gegen AK-154; derselbe Fluch unter beiden Zielrichtungen.
* **Zwei Zahlen zum Nachrechnen:** `effects_total − effects_with_a_figure`
  muss in jeder Gruppe der Zahl der stummen Zeilen gleichen, und die Menge der
  Fluchnamen einer Gruppe muss der Menge der `curse_ids` gleichen - **Namen,
  nicht Zeilen**, ein Fluch mit zwei Größen ist zwei Zeilen und ein Name.
* **Nicht geprüft und nicht prüfbar in diesem Auftrag:** alles am laufenden
  Fenster (AK-149, AK-160), die Statuszeile und der `Why`-Dialog als Ganzes.
* **Linter:** dieses Projekt hat keinen konfiguriert (kein `setup.cfg`, keine
  `pyproject.toml`, keine `.flake8`, keine Ruff-Konfiguration; `requirements-dev.txt`
  führt nur `pytest`). Der Punkt entfällt.

## 14. An den `ui-ux-designer`

* Die **(c)/(d)-Grenze** aus Abschnitt 7 - welche Menge waren die 58?
* Die **Vorrangfrage** der Zählzeile aus Annahme 1.
* Die **längste Zeile ist 153 Zeichen**, nicht „rund 150" - und es ist eine
  Zeile der Füllung (b), nicht (a) wie in §4 angenommen. Der Effektname allein
  ist 101 Zeichen lang.
* Die höchste Karte eines einzelnen Relikts ist **16 Zeilen** und damit genau
  die Zahl aus AK-160; für dieses Relikt (`Deep Grand Tranquil Scene`) nimmt
  die Director-Korrektur dem Block **keine** Zeile ab, weil alle drei Effekte
  eine Zahl bewegen. Über alle Vorschläge gerechnet spart der Block gegenüber
  dem Dialog im Median fünf Zeilen (38 gegen 43).
