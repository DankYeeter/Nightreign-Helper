# T-288 - developer - Zwei favorisierte Effekte, einer auf dem gehaltenen Relikt (17.09.2026)

```
STATUS: erledigt
AUFTRAG: T-288
GELESEN: docs/tasks/T-288.md; nrplanner/advisor/search.py, run.py, explain.py, types.py; effectfilters.py, effectfilterdialog.py, advisorbar.py (asking_from), advisorblock.py, app.py (apply/restore/settle), relicslots.py (select_copy), chalices.py; UI_SPEC AK-281/AK-290/AK-291; Registry HKCU\Software\DankYeeter\NightreignHelper (advisor, builds\4, chalices\4) nur gelesen
GEÄNDERT: nrplanner/advisor/explain.py, nrplanner/advisor/run.py, tests/test_advisor_run.py (Commit bc4443e); docs/berichte/T-288-developer.md
ANNAHMEN: Welches Relikt der Nutzer hielt, steht nirgends; einzige Duchess-Konstellation im Spielstand, die den Befund erzeugt, ist Duchess' Chalice mit Slot 2 (Polished Luminous Scene, traegt den Night-Invader-Effekt) gehalten. Wortlaut des neuen Satzes ist mein Vorschlag, nicht per AK festgelegt.
NÄCHSTER: director (Wortlaut an ui-ux-designer, Abnahme an qa-engineer)
BLOCKIERT DURCH: nichts
```

## Ergebnis

Ursache ist **(a)** aus dem Nachtrag: das gehaltene Relikt traegt den
Night-Invader-Effekt (7060200). Die Suche setzt dafuer korrekt keinen
zweiten Traeger (AD-036.4), der Vorschlag fuegt nur den Duchess-Effekt
(6643000) hinzu, und **kein Satz und keine Why-Zeile nannte den zweiten
Favoriten** - der Nutzer liest das als "nur einer kam an". Der Build traegt
beide.

**(b)** - Suche laesst den zweiten Effekt ohne Satz fallen - ist am echten
Spielstand nicht reproduzierbar: in 874 Laeufen mit `required={6643000,
7060200}` traegt jeder Vorschlag beide Effekte oder es kommt der AK-281-Satz
(`blocked_by_a_requirement=True`). Keine der Hypothesen H1-H4 trifft.

## Reproduktionszahlen (ohne GUI, Spielstand read-only, Testabzug kopiert)

Nutzer-Marken aus der Registry: `advisor/required = 6643000,7060200`
("[Duchess] Improved Vigor and Strength, Reduced Mind", nur rot bzw. Deep
alle Farben; "Attack power increased for each Night Invader defeated", alle
Farben). Besitz: 5 Kopien mit 6643000 (1 gewoehnlich rot, 4 Deep), 9 mit
7060200 (keine Deep). Aktuelle Ansicht laut Registry: Duchess, Sealed
Duchess' Urn (4004), Deep an.

| Lauf (Skript im Scratchpad T-288) | Laeufe | Treffer "nur einer, kein Satz" |
|---|---|---|
| `repro_pair.py`: 3 Ziele x 12 Duchess-Gefaesse x Deep an/aus, nichts gehalten | 72 | 0 (16 x AK-281-Satz bei Gefaessen ohne roten Slot, Deep aus) |
| `repro_held.py`: 12 Gefaesse x Deep x 1-2 gehaltene Slots x {ohne, mit 6643000, mit 7060200, leer gehalten} | 840 | 0 |
| `repro_loadouts.py`: jedes Relikt jedes Duchess-Loadouts aus dem Spielstand einzeln gehalten, Deep an/aus | 34 | 0 |
| `repro_a.py`: Duchess' Chalice, Slot 2 = Polished Luminous Scene [7011000, 7060200] gehalten | 2 | 2: Vorschlag traegt 6643000 (Slot 5 bzw. Slot 3), keine Zeile/kein Satz nennt "Night Invader" |

Drei Beispiele aus `repro_pair.py` fuer den korrekten Satzfall: Duchess'
Goblet [2,2,3] Deep aus, Sacred Erdtree Grail [2,2,2] Deep aus, Giant's
Cradle Grail [1,1,1] Deep aus -> "You own 5 copies carrying [Duchess]
Improved Vigor and Strength, Reduced Mind, but none fits the open slots."

## Fix (bc4443e)

`explain.required_met_by_a_hold(problem, ctx)`: je favorisiertem Effekt,
den ein gehaltenes Relikt traegt, ein Satz in `result.unknowns` (Why-Dialog-
Fuss, derselbe Kanal wie AK-281/AK-291), nach der Held-Slots-Zeile:

`Attack power increased for each Night Invader defeated, which you favourited, is carried by Polished Luminous Scene held in Slot 2.`

Regressionstest `test_a_required_effect_a_held_relic_carries_is_said_to_be_there`
(synthetisches Inventar, zwei rote Slots, Slot 1 gehalten mit Traeger von
Favorit A, Favorit B frei): faellt ohne die Verdrahtung in `run.py`
(Mutation nachgefahren: 1 failed, 46 passed; zurueckkopiert).

## Zahlen

- `pytest tests/test_advisor_run.py`: 47 passed.
- `pytest -n auto` Hauptbaum nach bc4443e: **1728 passed, 10 skipped, 68 s** (19:05).
- Klon-Volllauf: **1728 passed, 10 skipped, 71 s** (Klon auf bc4443e, 19:10-19:11, `<Scratchpad>/T-288/klon.txt`).
- Ponytail-Durchgang ueber `git diff f291ce7..HEAD`: net +64 Zeilen (26 Code, 3 Verdrahtung, 36 Test, davon Docstrings 9+7); nichts zu streichen - eine Funktion, ein Aufruf, ein Test.

## An ui-ux-designer (ueber director)

Wortlaut des neuen Satzes ist nicht in `UI_SPEC.md` festgelegt (AK-281/
AK-291 decken nur "kein Traeger"/"keine Kombination"). Vorschlag steht oben,
im Satzmuster von AK-281 ("…, which you favourited, …") und der Held-Slots-
Zeile; Slot-Nummerierung wie `explain.curses` ("Slot {index+1}", Deep-Slots
zaehlen durch). Aenderung ist ein String in `explain.required_met_by_a_hold`
plus die Erwartung im Test.

## An qa-engineer

Abnahme am Fenster: Duchess, Duchess' Chalice, Deep an, Slot 2 (Polished
Luminous Scene) per Hold festhalten, beide Effekte favorisieren, Optimize,
Why: Fuss traegt den Satz oben; der Duchess-Effekt steht mit dem
Favourite-Zeichen in Slot 5. Gegenprobe: Hold loesen -> kein Satz, beide
Effekte in freien Slots. Randfall: zwei gehaltene Relikte mit demselben
Favoriten -> ein Satz, beide Traeger mit Komma.

## An director

- Nebenfund, nicht behoben: die Registry-Records `chalices\4\4003`, `4000`,
  `4002` tragen Handles um 1 kleiner als der aktuelle Spielstand (z. B.
  3229614315 vs. 3229614316 fuer The Will of Balance); `4004` passt. Der
  Spielstand wurde offenbar seit dem Speichern umnummeriert; `select_roll`
  faengt das ab (QA-021-Pfad). Kein Handlungsbedarf erkannt, nur zur
  Kenntnis.
- Der Wortlaut fuer AK-281 bei "besessen, passt nicht" (`You own {n} copies …
  but none fits the open slots.`) enthaelt das Wort "favourited" nicht; wer
  im Fenster nach diesem Wort sucht, uebersieht den Satz. Keine Aenderung
  vorgenommen (AK-300-Wortlaut).
