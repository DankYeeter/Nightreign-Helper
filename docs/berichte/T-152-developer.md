# T-152 - Die Suite ist rot: zwei Anker zeigen auf geloeschten Code (developer)

```
STATUS: erledigt
AUFTRAG: T-152 - zwei tote und zwei veraltete Registereintraege in
         scripts/differential/mutate.py
GELESEN: docs/tasks/T-152.md; docs/berichte/T-151-developer.md;
         .claude/agent-memory/developer/project_mutation_registry.md;
         scripts/differential/mutate.py (Register, Kopf, alle vier
         Id-Decke-Eintraege); nrdata/savefile.py (RELIC_ID_CEILING,
         relic_scan_mode, Docstrings); tests/test_differential_track.py
         (test_every_mutation_still_finds_its_anchor_in_the_real_source);
         tests/test_relic_scan_prefilter.py (aktuelle Testnamen)
GEÄNDERT: scripts/differential/mutate.py (Commit e372086)
ANNAHMEN: keine - der Auftrag zitiert GOAL.md und docs/state.md, beides
          gelesen, kein Widerspruch zu meinem Auftrag.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**`scripts/differential/mutate.py`** - vier Eintraege zur Id-Decke:

1. **`the-id-ceiling-is-never-checked`** entfernt. Anker war die Aufrufzeile
   `_check_the_prefilter_can_see_every_id(valid_relic_ids)`, die T-151 aus
   `nrdata/savefile.py` entfernt hat (AD-031, Nutzerentscheid 08.09.2026: eine
   gebrochene Id-Annahme faellt jetzt auf den langsamen Weg zurueck statt die
   Datei abzulehnen). Ihr Gegenstand existiert nicht mehr - geprueft per
   `grep -n "_check_the_prefilter_can_see_every_id" nrdata/savefile.py`: keine
   Treffer. Kein Wiederaufleben-Kandidat, also entfernt statt umgebogen.
2. **`the-id-ceiling-looks-at-the-smallest-id`** entfernt. Anker war
   `biggest = max(valid_relic_ids, default=0)`, ebenfalls Teil der geloeschten
   Funktion; die Berechnung steht jetzt inline in `relic_scan_mode`
   (`return SLOW if max(valid_relic_ids, default=0) >= RELIC_ID_CEILING else
   FAST`) und ist keine eigene Zeile mehr, auf die dieser Anker zeigen
   koennte.
3. Ein Kommentarblock direkt vor den beiden verbleibenden Id-Decke-Eintraegen
   nennt den Grund fuer beide Entfernungen (AD-031, T-151, T-152), damit die
   Luecke nicht spaeter als vergessene Registrierung missverstanden wird.
4. **`the-id-ceiling-is-raised-past-its-assumption`** (Anker
   `RELIC_ID_CEILING = 0x01000000`, weiterhin vorhanden) - `survival_means`
   aktualisiert: die vier alten Fallnamen sind weg, dafuer heute zwei echte
   (siehe Nachweis unten).
5. **`the-id-ceiling-drops-below-the-games-own-ids`** (derselbe Anker) -
   `survival_means` aktualisiert: von 9 alten Fallnamen (Stand vor AD-031, als
   eine gebrochene Annahme noch eine Ausnahme warf und dadurch praktisch jeden
   Testfall der Datei mitriss) auf die vier, die heute tatsaechlich fallen.

**Register jetzt 230 Eintraege** (232 aus T-139, minus die zwei entfernten).

## Nachweis, dass die zwei aktualisierten Eintraege heute wirklich toeten

Kein `git checkout`, keine Aenderung am Arbeitsbaum: `git archive HEAD | tar
-x` in zwei Kopien im Scratchpad (`…/scratchpad/T-152/mutant_raised` und
`…/mutant_drops`), dort `RELIC_ID_CEILING = 0x01000000` per `sed` exakt so
ersetzt, wie es der jeweilige Registereintrag tut, dann
`.venv/Scripts/python.exe -m pytest -q tests/test_relic_scan_prefilter.py`
in der Kopie:

- **raised-past-its-assumption** (`0x02000000`): `2 failed, 16 passed` -
  `test_the_choice_is_made_at_three_stated_ids`,
  `test_the_largest_id_the_fast_way_can_see_is_read_in_full`.
- **drops-below-the-games-own-ids** (`0x00000100`): `4 failed, 14 passed` -
  `test_an_id_above_the_ceiling_is_read_the_slow_way_and_not_refused`,
  `test_an_inventory_read_the_fast_way_says_that_too`,
  `test_the_choice_is_made_at_three_stated_ids`,
  `test_the_games_own_relic_ids_still_allow_the_fast_way`.

Beide Laeufe im **Standardlauf**, ohne Sonderkonfiguration (L-008 a). Die
Erwartung stammt aus den Testfaelen selbst, nicht aus `RELIC_ID_CEILING`
zurueckgerechnet (L-008 b) - `test_the_choice_is_made_at_three_stated_ids`
sagt es im eigenen Docstring ausdruecklich.

**Rot-vorher fuer die Entfernung** (L-007): vor dieser Aenderung waren genau
diese zwei Faelle rot -
`tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source[the-id-ceiling-is-never-checked]`
und `[the-id-ceiling-looks-at-the-smallest-id]` - weil ihr Anker in
`nrdata/savefile.py` keine Uebereinstimmung mehr fand (`raw.count(anchor) ==
0`, nicht 1). Die Entfernung macht sie nicht gruen, sondern nimmt sie aus dem
Parametrisierungs-Set.

## Umfang und Zaehlung des Registers

- **Vorher:** 232 Eintraege (T-139), davon 2 rot (T-151-Befund).
- **Jetzt:** 230 Eintraege.
- **Anker-Waechter fuer alle 230 gruen:**
  `pytest -q tests/test_differential_track.py -k
  test_every_mutation_still_finds_its_anchor_in_the_real_source` ->
  `230 passed, 40 deselected` - jeder Anker findet sich noch genau einmal im
  echten Quelltext.
- **Heute nachweislich toetend, von mir selbst campagniert:** die zwei oben
  (raised-past-its-assumption, drops-below-the-games-own-ids). **Keinen
  vollstaendigen Mutationslauf ueber alle 230 Eintraege gefahren** - das ist
  der groessere Folgeauftrag, den der Auftrag selbst ausdruecklich ausnimmt
  ("die Nachregistrierung der rund 77 Mutationen ... ist ein eigener
  Auftrag"). Fuer die uebrigen 228 gilt nur, was der Anker-Waechter zusichert
  (Anker gefunden), nicht, dass ich sie heute einzeln habe toeten sehen -
  T-139 haelt dieselbe Grenze fuer seine 232 ("38 von 38 Ankern matchen genau
  einmal", nicht "38 von 38 toeten").
- **Weitere ins Leere zeigende Anker:** keine gefunden. Der Anker-Waechter
  deckt alle 230 automatisch ab und lief gruen; ich habe daneben keine
  gezielte Volltextsuche nach weiteren toten Testnamen in `survival_means`
  ueber das ganze Register gemacht, weil das ausserhalb dessen liegt, was
  T-151 gemeldet hat und ausserhalb der harten Grenze ("nur
  scripts/differential/mutate.py", "zaehlen und melden" bezog sich laut
  Kontext auf das, was beim Lesen dieser Datei fuer diesen Auftrag auffaellt).

## Suitezahl

```
pytest -n auto   ->   1590 passed, 9 skipped in 188.46s
```

**0 failed.** Groesser als T-151s 1582, wie im Auftrag angekuendigt - T-150
(`developer`, V3) arbeitet parallel uncommittet an `nrplanner/app.py`,
`nrplanner/gamepath.py` und `tests/test_save_path_memory.py` (bei
`git status` sichtbar, nicht meine Aenderung). Die Differenz von +8 gegenueber
T-151s damaligem Zwischenstand ordne ich nicht weiter zu - laut Auftrag ist
das hinzunehmen, nicht zu erklaeren.

## Tests

Keine neue Anwendungslogik, kein neuer Test noetig - die Aenderung ist
Registerpflege. Abgedeckt durch den bestehenden
`test_every_mutation_still_finds_its_anchor_in_the_real_source` (parametrisiert
direkt aus `mutate.MUTATIONS`, siehe oben) und den vollen Suitelauf.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (keine)
- [x] Build & Tests gruen in der benannten Umgebung (Windows 10/11 x64,
      `.venv`): `0 failed`
- [x] Neue Tests: keine neue Logik, keine noetig; bestehender Waechter deckt
      die Aenderung ab
- [ ] Linter: entfaellt, das Projekt hat keinen konfiguriert
- [x] Keine Secrets, keine TODOs, kein toter Code - im Gegenteil, zwei toter
      Code verweisende Eintraege entfernt
- [x] Nur `scripts/differential/mutate.py` beruehrt, wie vorgegeben
- [x] Doku: Kommentar im Register selbst erklaert den Grund; dieser Bericht
      abgelegt

## An den director

1. **Der von T-151 gemeldete Folgeauftrag bleibt offen:** die Nachregistrierung
   der rund 77 Mutationen aus T-137, T-142, T-147, T-149 und T-151 ist
   weiterhin nicht Teil dieses Auftrags und nicht erledigt.
2. **Kein neuer Befund.** Ich habe keine weiteren dangling Anker gefunden;
   siehe Einschraenkung oben zur Reichweite dieser Aussage (Anker-Waechter
   deckt alle 230 ab, eine gezielte Suche nach weiteren veralteten
   `survival_means`-Testnamen im ganzen Register habe ich nicht gemacht -
   waere ein eigener, groesserer Durchgang).
3. Punkte 2-5 aus T-151s Bericht an dich (A7/V5 noch offen, SEC-029 offen,
   Performance-Fund zum langsamen Weg, Debt in `docs/state.md`/`qa/findings.md`/
   `ARCHITECTURE.md`) sind von mir nicht erneut geprueft - reine Wiederholung
   waere keine neue Information; sie stehen weiterhin in T-151s Bericht.

## Offene Fragen

Keine.
