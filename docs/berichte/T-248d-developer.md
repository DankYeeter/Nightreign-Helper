# T-248d - developer - Uebergabe nach Zugschwelle (14.09.2026)

```
STATUS: teilweise
AUFTRAG: T-248d Schritte 1-4 (AD-036); Schritte 1-3 abgenommen, Schritt 4 nicht begonnen
GELESEN (Schritt 4): UI_SPEC.md AK-285 Schluss, AK-289, AK-290; advisorblock.py WhyDialog (Z. 338-420); relicpicker.py RelicCard (Z. 639-800)
GEÄNDERT: nichts uncommittet - Arbeitsbaum sauber auf e7a8eef (git status leer)
ANNAHMEN: keine neuen
NÄCHSTER: Schritt 4 als neuer Auftrag (Fenster und Speicher), Vorarbeit unten
BLOCKIERT DURCH: Zugschwelle des Hooks (151 Werkzeugaufrufe); kein Testlauf mehr moeglich
```

## Stand

- Schritt 1 `d6fda65`, Schritt 2 `9423eee`, Schritt 3 `e7a8eef` - alle vom
  Director abgenommen. Letzter Volllauf (Director, nach e7a8eef): 1568
  passed, 4 failed (QA-266-Trio + QA-249-Flacker).
- Schritt 4: **keine Datei angefasst.** Nur gelesen.

## Befunde aus dem Lesen fuer Schritt 4 (spart dem Nachfolger den Einstieg)

1. **`ReasonLine` traegt keine Effekt-Id.** AK-276 bindet die Kontrolle an
   die Id, aber `types.ReasonLine` hat nur `slot_index, text, is_curse,
   silence`. Noetig: Feld `effect_id` auf `ReasonLine`, gesetzt an den fuenf
   Konstruktionsstellen in `explain.py` (Z. 417, 458, 613, 668, 674 - alle
   kennen die Id). Tests konstruieren `ReasonLine` an 5 Stellen mit
   Schluesselwoertern (test_advisor_apply:35, test_advisor_bar:489/513,
   test_advisor_block:50, test_advisor_types:61) - ein Default vermeidet
   deren Umbau; AD-036 verbietet Felder nur auf GoalContext/AdvisorRequest/
   AdvisorResult.
2. **WhyDialog zeichnet je Slotgruppe EIN Rich-Text-QLabel**
   (`lines_markup(group.lines)`, advisorblock.py Z. 356-359). Fuer eine
   Kontrolle je Zeile (AK-277: `QToolButton` statt Aufzaehlpunkt) muss die
   Gruppe in eine Zeile-je-Widget-Form zerfallen; `line_markup` (Z. 90-104)
   liefert heute den HTML-Aufzaehlpunkt mit. AK-277 fordert: Karte/Dialog
   nicht breiter/hoeher als mit QLabel-Zeile (Messung vor/nach).
3. **RelicCard bekommt nur Namen** (`effect_names: list[str]`,
   `curses: list[(name, detail)]`, relicpicker.py Z. 642-645) - keine Ids.
   Aufbauort der Karten um Z. 1432 (`curse_ids`), dort sind `item.effect_ids`
   und `item.curse_ids` verfuegbar; die Karte braucht Id je Zeile.
4. Bereits vorhanden aus Schritt 2/3: `SlotProblem.excluded/required`,
   `SILENT_EXCLUDED`, `explain._excluded_line`, `required_but_unmet`
   (AK-281). AK-290.2 (`you required it, so it always counts.`) und die
   Legende AK-290.3 sind noch nirgends gebaut. Mutationsanker in
   `scripts/differential/mutate.py`: `baseline-dropped-from-the-ask`
   (advisorbar.py Merge-Zeile), `exclusion-ignored` (evaluate.py),
   `feasibility-cut-removed` (search.py) - beim Umbau von `asking_from`
   die Merge-Zeile wortgleich lassen.
5. `advisorbar.the_build_changed()` hat seit Schritt 1 kein kwarg mehr;
   AK-289 braucht wieder einen Ursachen-Zweig fuer OUTDATED (`The effects
   you marked changed while this was working out — use Optimize again.`).
6. `README.md:181-192, 459-460` beschreibt noch die entfallene
   Worst/Best-Box - in Schritt 4 mit der neuen Markierung umschreiben.

## Offene Wortlaute (ui-ux-designer)

- Satz fuer "jeder Pflicht-Effekt hat einen Traeger, aber keine Konstellation
  passt in die freien Slots" (explain.required_but_unmet, Platzhalter).
- Zustandsnummer der Leiste bei leerem Beam unter Pflicht (heute 4.11
  `0 of N slots filled`; AK-281 will den Effektnamen in der Statuszeile).
