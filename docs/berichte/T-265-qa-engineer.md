# T-265 -- Retest (qa-engineer), 15.09.2026

Stand `02e0721` (Code `2640602`, Version 1.12.0), eingefroren. Umlenkung
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-265`, `LOCALAPPDATA`/`APPDATA`/
`USERPROFILE` ins Scratchpad `T-265/`, Testabzug (841 Dateien) kopiert (nicht
verlinkt), `paths.cache_dir()` zurueckgelesen. Kein `nightreign.exe` aktiv
(`tasklist`, vor Beginn). Einzige Fensterinstanz dieser Session.

## Urteil: PASS

QA-272, SEC-046, SEC-047 bestaetigt behoben. Kein P1/P2. Volle Suite gruen.

## Nachweise

**Suite:** `pytest -n auto` 1687 passed / 10 skipped, 70,9 s, 0 rot. Zielgerichtet
`test_two_handed_switch.py` + `test_icon_pack_completeness.py`: 33 passed.

**Mutationsregister:** `grep -c "Mutation("` in `scripts/differential/mutate.py`
= 0 -- nichts nachzufahren oder zu loeschen (bereits geleert vor T-265).

### QA-272 (Hand-Schalter, `d898bfd`)

Rot-vorher: `git archive 02e0721` in Scratch-Klon extrahiert, die zwei
`_set_two_handed(False)`-Zeilen (`app.py:1907`, `2584`) auskommentiert (Zeilen
im Fix). `pytest tests/test_two_handed_switch.py` im mutierten Klon: genau die
drei vom Fix-Commit benannten Waechter rot --
`test_the_first_import_of_another_nightfarer_stores_one_handed`,
`test_load_equipped_takes_the_save_s_hand_which_is_one`,
`test_reset_chalice_puts_the_hand_back_to_one` (14 andere gruen). Am
unmutierten Code (02e0721) alle 17 gruen -- deckt A->B->A, `Load equipped`,
Reset exakt wie in der T-263-Reproduktion.

Zusaetzlich A20-Persistenz mit gefuelltem Build (Auftrag): zwei
`appmod.Planner(data, read_save=frozen_scan)`-Instanzen nacheinander (echte
Registry, `DankYeeterT-265`, kein `clear_settings` dazwischen, simuliert
Neustart). Held 1 / Gefaess 1001 (3 Relikte belegt, `selected=True` in
`frozen_inventory.json`): Klick -> `chalices.load(1,1001)[3] is True`; zweite
Instanz (Neustart) -> Schalter zeigt `2H`, Store weiterhin `True`. Kein
Fremdbau betroffen (nur Held 1/Gefaess 1001 angefasst).

### SEC-046 (`inside_pack`, `2640602`)

Kopie des Testabzugs (`icons/manifest.json`, `icon_version` passend zu
`ICON_VERSION=3`), drei Manifest-Eintraege einzeln injiziert:
`\\127.0.0.1\x\evil.png`, `C:\Windows\win.ini`, `..\..\outside.png`. Fuer
alle drei: `firstrun.what_is_needed(...)` liefert `['icons']` (gone/Rebuild),
`pathlib.Path.stat` global ueberwacht -- **kein** `stat()`-Aufruf beruehrt den
externen Pfad (leere Trefferliste), Laufzeit 0,31-0,35 s je Aufruf (kein
Netz-Stall). SEC-008-Schutz greift vor `resolve()`.

### SEC-047 (`manifest_files`/`what_is_needed`, `8e1ea80`)

Gleiche Kopie, Variante ohne `"file"` und mit `"file": 5` einzeln in
`variants` injiziert (sonst unveraendertes, gueltiges Manifest): kein
Absturz in beiden Faellen, `what_is_needed` liefert `[]` (nicht `['icons']')
-- der fehlerhafte Eintrag wird vom Walk stillschweigend uebersprungen
(`manifest_files` liest nur `str`-Dateinamen), der Rest des Manifests bleibt
gueltig, kein Rebuild ausgeloest. Das entspricht dem eigenen Waechter
`test_the_walk_skips_a_variant_without_a_file_or_with_a_non_string` des
Fix-Commits, nicht dem in diesem Auftrag genannten `['icons']`-Ergebnis --
siehe Offene Fragen.

## Beobachtungen

Register-Zeilen fuer alle drei Funde stehen aktuell auf "behoben -- Retest
offen" (Anhang `aaaaa10`, vom developer selbst nach dem Fix ergaenzt); dieser
Bericht liefert die QA-Bestaetigung dazu.

## Offene Fragen

- **developer:** Der Auftragstext erwartet fuer SEC-047 "Variante ohne `file`
  / `file: 5` -> `what_is_needed` liefert `icons`". Gemessen liefert eine
  einzelne fehlerhafte Variante in einem sonst gueltigen Manifest `[]` (die
  fehlerhafte Datei wird nur stillschweigend uebersprungen); `['icons']`
  entsteht im Fix-Commit nur, wenn das Manifest **insgesamt** eine andere
  Form hat (z. B. `icon_version` fehlt komplett, per Top-Level-`except`).
  Deckt sich der Auftragstext mit einer anderen Testvariante, oder ist die
  Erwartung eine Ungenauigkeit? Kein Befund, da "kein Absturz" (das
  eigentliche Sicherheitsziel) in beiden Faellen haelt.

## Nicht getestet

Zielgeraet (5800H); echtes Fenster/UIA-Klicks (reine Funktionsproben ueber
`appmod.Planner` offscreen statt Maus); Artefakt-/EXE-Weg (kein Rebuild in
diesem Auftrag); weitere Nightfarer/Gefaesse als die genannten Stichproben.

## QA-Log (Anhang, nicht committet)

| QA-272 | T-265 Retest (15.09.2026): behoben bestaetigt -- rot-vorher (3/3
Waechter wie vorhergesagt rot in mutiertem Klon), A20-Persistenz mit
gefuelltem Build (Held 1/Gefaess 1001) ueber zwei Instanzen | P2 | developer |
behoben | 2026-09-15 |

| SEC-046 | T-265 Retest (15.09.2026): behoben bestaetigt -- UNC/Laufwerk/
Traversal in Kopie des Testabzugs -> gone/Rebuild, 0 `stat()`-Aufrufe ausserhalb
des Packs, ~0,3 s (kein Netz-Stall) | Niedrig | developer | behoben |
2026-09-15 |

| SEC-047 | T-265 Retest (15.09.2026): behoben bestaetigt -- Variante ohne
`file`/mit `file: 5` kein Absturz (Walk ueberspringt sie, `[]` statt Absturz);
Praezisierung zum Auftragstext siehe Offene Fragen | Niedrig | developer |
behoben | 2026-09-15 |
