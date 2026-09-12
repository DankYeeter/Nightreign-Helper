STATUS: erledigt
AUFTRAG: T-094 - Die beiden Spitzenreiter stehen oben (AK-195)
GELESEN: docs/tasks/T-094.md, nrplanner/relicpicker.py, tests/test_relic_picker_advisor.py, tests/conftest.py, nrplanner/advisor/types.py (Candidate/Marginal/SlotPool), nrplanner/advisor/candidates.py (pool()), nrplanner/app.py (active_slots, current_hero, select_hero), UI_SPEC.md §3.3 und AK-40 bis AK-53
GEÄNDERT: nrplanner/relicpicker.py, tests/test_relic_picker_advisor.py (beide committet in ea3d016 "feat(picker): both directions' top picks lead the grid (AK-195)")
ANNAHMEN:
- UI_SPEC §3.3 ("ADVISOR PICK"-Chip, "the advisor's pick is hidden by your filter") gehört zum Vorschlagsblock der Advisor bar (Scope-Grenze, "fertig, nicht anfassen"), nicht zu AK-195's Chip `BEST FOR …`. Beide Features heißen im Text ähnlich, sind aber verschiedene Mechanismen; nicht angefasst.
- Für die "andere Richtung" wird kein zweiter sichtbarer Chip ergänzt — nur die Reihenfolge ändert sich (Beruehrt-Dateien-Vorgabe "nur die Ordnung des Rasters"). Die Karte trägt weiterhin höchstens einen Chip, den der aktuell sortierten Richtung, unverändert zu AK-46.
- "Favoriten, dann Name" für die vorgezogene Gruppe = die Reihenfolge, die `items` bereits hat, bevor `_in_the_chosen_order` läuft (Favoriten-stabil über `slot.available_items()`, das laut bestehendem Code bereits Namensordnung ist).
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Umsetzung

`nrplanner/relicpicker.py`:
- `Ranking.best_text` entfernt, ersetzt durch `Ranking.top_handles(goal_id)` —
  die eine Berechnung, aus der sowohl der Chip (`_say_what_they_are_worth`)
  als auch die Vorziehung (`_in_the_chosen_order`) lesen (Vorgabe 1). Ein
  Handle-Set, per Rundungstext verglichen (AK-45), leer bei leerem Pool,
  `no change` oder negativem Spitzenwert (AK-46).
- `_say_what_they_are_worth` liest jetzt `top_handles(goal_id)` statt einer
  zweiten Textvergleichs-Logik; Verhalten für die bestehenden AK-45/AK-46-Tests
  unverändert (siehe unten).
- `_in_the_chosen_order` splittet die Ausgabe in drei Gruppen: `first`
  (Chip-Träger der sortierten Richtung), `second` (Chip-Träger der anderen
  Richtung, ohne Überschneidung mit `first`), `rest` (der bisherige
  wertbasierte Rest). `first`/`second` werden aus `items` gebildet (Favoriten-
  /Namensordnung), nicht aus der wertsortierten Liste — AK-44. Bei
  `Sort by = Name` oder ohne Ranking bleibt die Funktion beim alten
  Kurzschluss (`return items`), keine Vorziehung.
- Der Filter ändert an der Menge nichts: `top_handles` liest `self.pool.candidates`
  (ganzer Pool, wie schon in T-093), aber vorgezogen werden kann nur, was in
  `items` steht — das ist bereits die gefilterte Liste, die `_candidates()`
  vor dem Aufruf gebaut hat. Ein durch den Filter ausgeblendeter Spitzenwert
  bekommt strukturell keinen Ersatz.

## Reihenfolge an der Spitze (beide Sortierungen, beide Slotarten)

Geprüft mit einem Wegwerf-Skript gegen den echten Spielstand (offscreen,
save read-only, kein zweites Fenster — die App lief nicht als GUI, nur
`QApplication` ohne `.show()`), zwei Nightfarer, je ein normaler und ein
Deep-Slot, beide `Sort by`-Richtungen:

```
Wylder, normaler Slot, sortiert nach Damage:
  1. 'Grand Luminous Scene'  chip=BEST FOR DAMAGE   +4.6 AR / no change
  2. 'Grand Luminous Scene'  chip=''                no change / +64.2 effective HP
Wylder, normaler Slot, sortiert nach Survival:
  1. 'Grand Luminous Scene'  chip=BEST FOR SURVIVAL no change / +64.2 effective HP
  2. 'Grand Luminous Scene'  chip=''                +4.6 AR / no change
```
Karte 2 der Damage-Sortierung trägt exakt den Wert, den Karte 1 der
Survival-Sortierung als Chip-Träger ausweist — der Überlebens-Spitzenreiter
steht direkt hinter dem Schadens-Spitzenreiter, wie AK-195 verlangt.

```
Wylder, Deep-Slot, sortiert nach Damage (Gleichstand):
  1. 'Deep Grand Luminous Scene'     chip=BEST FOR DAMAGE  +5.9 AR / no change
  2. 'Deep Polished Luminous Scene'  chip=BEST FOR DAMAGE  +5.9 AR / no change
  3./4. zwei Karten mit +19.1 effective HP (Survival-Spitzenwert, in der
       Damage-Sortierung ohne Chip, aber vorgezogen)
Wylder, Deep-Slot, sortiert nach Survival:
  1.-4. vier Karten mit +19.1 effective HP, chip=BEST FOR SURVIVAL
```
Zwei gleich gute Damage-Karten stehen gleichberechtigt oben (AK-44, kein
Rang), danach die (im Pool sogar vierfach gleichstehenden) Survival-Karten.

```
Guardian, normaler Slot, Damage:  1. 'Grand Burning Scene' BEST FOR DAMAGE
                                   2. 'Night of the Fathom' (chip='', aber
                                      exakt der Survival-Spitzenwert +100.0)
Guardian, normaler Slot, Survival: 1. 'Night of the Fathom' BEST FOR SURVIVAL
                                   2. 'Grand Burning Scene' (chip='', Damage-
                                      Spitzenwert +8.2 AR)
Guardian, Deep-Slot, Damage:      1./2. zwei Karten BEST FOR DAMAGE (+6.4 AR)
Guardian, Deep-Slot, Survival:    1. BEST FOR SURVIVAL (+28.0 effective HP)
```
Alle acht Kombinationen (2 Helden × 2 Slotarten × 2 Richtungen) zeigen die
erwartete Reihenfolge.

## Die vier Gegenbauten (einzeln gefahren, jeweils per `cp` gesichert und
zurückgesetzt, nie `git checkout`)

1. **Nur die sortierte Richtung vorziehen** (`trailing = frozenset()` statt
   `top_handles(other_id)`). Kern des Auftrags: nach Damage sortiert, beste
   Survival-Karte soll oben stehen. Szenario mit vier Kandidaten, deren
   reine Wertordnung die Survival-Spitzenkarte sonst hinter zwei andere
   Karten setzen würde (nicht nur eine Position dahinter — sonst hätte die
   Mutation zufällig dasselbe Ergebnis geliefert). Rot:
   `test_the_survival_top_pick_leads_when_sorted_by_damage` UND die
   symmetrische `test_the_damage_top_pick_leads_when_sorted_by_survival`
   (`assert [.., 3229614182] == [.., 3229614199]`, index 1 abweichend).
2. **Bei `Sort by = Name` trotzdem vorziehen** (Namensordnungs-Kurzschluss
   nur noch für den Wertsort, nicht mehr für die Vorziehung). Rot:
   `test_no_promotion_when_sort_by_name`
   (`'Dark Night of the Beast' != 'Cracked Sealing Wax'`).
3. **Vorziehen trotz `no change`-Spitzenwert** (Bedingung
   `top == NO_CHANGE or top.startswith("-")` durch `if False` ersetzt). Rot:
   die neue `test_no_promotion_when_the_other_top_is_no_change`
   (`assert 2 < 1`) UND die bestehende
   `test_nothing_is_marked_best_when_the_best_is_no_change` — beide reißen,
   weil Chip und Vorziehung dieselbe Quelle teilen (Vorgabe 1 wörtlich
   bestätigt).
4. **Vorgezogene Karten nach Wert statt Favorit/Name ordnen** (`first`/
   `second` aus `by_value` statt aus `items` gebaut). Echter Gleichstand:
   12.36 und 12.44 runden beide auf `+12.4 AR` (AK-45), sind also beide
   Chip-Träger, aber verschieden im Rohwert. Rot:
   `test_tied_top_picks_keep_favourite_then_name_order`
   (`assert [.., 3229614199] == [.., 3229614256]`, vertauscht).

Kein Gegenbau blieb grün. Nach jedem Lauf wurde `relicpicker.py` aus einer
vor der Mutation angelegten Kopie (`cp relicpicker.py relicpicker.py.orig`,
danach zurückkopiert) wiederhergestellt; `git diff --stat -- nrplanner/relicpicker.py`
war danach leer, die Kopie wurde entfernt.

## Suite (zwei Vordergrundläufe, wie vom Auftrag verlangt)

- Lauf 1, `tests/test_relic_picker_advisor.py` + `tests/test_relic_picker_geometry.py`:
  **48 passed in 117.54s** (Wiederholung nach den Gegenbauten:
  48 passed in 118.25s, identisch).
- Lauf 2, Rest mit `--ignore` auf beide Dateien:
  **1191 passed, 9 skipped in 654.40s (0:10:54)**.
- Summe: **1239 passed, 9 skipped**.

Rezept der Zahl: Stand vor dem Auftrag war 1229 passed, 9 skipped, 5
deselected (737,87 s in einem Lauf, mit einer nicht genannten `-m`-Deselektion).
Dieser Lauf verwendete keine Deselektion, lief also 5 vorher deselektierte
Tests zusätzlich mit (1229 + 5 = 1234), plus 5 neue AK-195-Tests
(1234 + 5 = 1239) — deckt sich exakt mit der gemessenen Summe. Kein
Regressionsverdacht.

## DoD

- Anforderung verstanden, Annahmen oben dokumentiert.
- Build & Tests grün in der benannten Testumgebung (Windows 10, Python
  3.12.10 aus `.venv`, PySide6, `QT_QPA_PLATFORM=offscreen`). Keine andere
  Plattform zu prüfen (keine Angabe im Auftrag).
- Kein Linter im Projekt konfiguriert — Punkt entfällt (Nutzerentscheid
  2026-09-06).
- Neue Tests für die neue Logik: 5 neue Fälle in
  `tests/test_relic_picker_advisor.py`, davon 4 als Gegenbau-Killer verifiziert.
- Keine Secrets, keine TODOs, kein toter Code — `Ranking.best_text` entfernt,
  da durch `top_handles` ersetzt und sonst unreferenziert (per Grep über den
  gesamten Baum geprüft, ein Treffer: die eigene Definition).
- QA-Akzeptanzkriterien (Zweite Stichprobe: 2 Helden × normaler + Deep-Slot)
  selbst durchgespielt, siehe oben.
- Kein Datenabzug geschrieben, kein Save geschrieben, kein Netzwerkzugriff,
  keine Bildschirmabzüge — das Akzeptanz-Skript öffnete kein sichtbares
  Fenster (`QApplication` ohne `.show()`, `QT_QPA_PLATFORM=offscreen`).

## Commits

- `ea3d016` `feat(picker): both directions' top picks lead the grid (AK-195)`
  — `nrplanner/relicpicker.py`, `tests/test_relic_picker_advisor.py`.

Ein Teilschritt, ein Commit — die vier Gegenbauten liefen alle nach diesem
Commit gegen mutierte Arbeitskopien und wurden per `cp` zurückgesetzt, nicht
committet.

## Was aufgefallen ist, aber nicht in den Auftrag gehörte

- `UI_SPEC.md` §3.3 beschreibt einen ZWEITEN, andersartigen Chip
  (`ADVISOR PICK`, an der Kopfzeile rechts vom Namen) und die Zeile
  `the advisor's pick is hidden by your filter` für den Vorschlagsblock der
  Advisor bar. Diese Zeile existiert nirgends im Code (per Volltextsuche über
  das ganze Repo, zwei unabhängige Begriffe: `"hidden by your filter"` und
  `"ADVISOR PICK"` — beide nur in `UI_SPEC.md`, keiner in `.py`-Dateien).
  Das ist außerhalb des Scopes von T-094 (`app.py`, Advisor bar,
  Vorschlagsblock sind laut Auftrag "fertig, nicht anfassen") und war schon
  vor diesem Auftrag so; nur zur Kenntnisnahme, falls das an anderer Stelle
  als offen geführt wird.
- Kein Sicherheits- oder Datenverlustrisiko, keine neue Abhängigkeit, keine
  bestehende Debt an den berührten Stellen gefunden.

## An qa-engineer

- Kernfall: einen Slot mit ≥2 verschiedenen Kandidaten öffnen, nach Damage
  sortieren, prüfen, dass die beste Survival-Karte (per `BEST FOR SURVIVAL`
  in der Survival-Sortierung identifizierbar) direkt nach der Damage-
  Spitzenkarte steht, nicht irgendwo weiter unten. Gleiches umgekehrt.
- Gleichstand: ein Slot, in dem mehrere Karten denselben Chip tragen
  (z. B. ein Deep-Slot mit mehreren baugleichen Basisrelikten) — die
  Reihenfolge unter ihnen darf sich beim erneuten Öffnen nicht ändern
  (AK-44) und darf nicht nach Rohwert wirken.
- Filter: einen Suchtext eintragen, der die Spitzenkarte einer Richtung
  ausblendet — die restlichen Karten dürfen nicht "eine Stufe aufrücken"
  oder eine falsche Karte als Ersatz vorziehen.
- `Sort by = Name`: keine Vorziehung, Grid identisch zur reinen
  Namensordnung ohne Advisor.
- Edge Case, den ich nicht automatisiert nachgebaut habe: ein Slot, in dem
  BEIDE Richtungen exakt denselben Kandidatensatz als Spitzenreiter haben
  (z. B. ein Relikt, das auf beiden Achsen gleichermaßen führt) — die
  Reihenfolge-Logik entfernt Duplikate zwischen `first`/`second`
  (`trailing = ... - leading`), sodass so eine Karte nur einmal erscheint;
  das folgt aus dem Code, wurde aber nicht gegen einen echten Spielstand mit
  dieser Konstellation geprüft (keiner der acht Stichproben zeigte diesen
  Fall).

## An ui-ux-designer

Keine Abweichung von AK-195. Eine Designentscheidung, die im Auftrag nicht
explizit stand und die ich getroffen habe: die Karte der "anderen" Richtung
trägt weiterhin **keinen sichtbaren Chip**, wenn sie nicht die aktuell
sortierte Richtung ist — nur ihre Position wandert nach vorn. Grund: der
Auftrag beschränkt die berührten Dateien auf "nur die Ordnung des Rasters",
und AK-46 spricht ausdrücklich von "der sortierten Zielrichtung". Falls das
UX-seitig anders gewünscht ist (z. B. ein zweiter, schwächerer Chip für die
nicht-sortierte Richtung), ist das ein eigener Auftrag mit eigenem
Abnahmekriterium.
