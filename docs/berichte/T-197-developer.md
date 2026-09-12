STATUS: erledigt
AUFTRAG: T-197 — QA-233: die zwei ausgeschlossenen Testdateien zurueck in die Suite
GELESEN: docs/tasks/T-197.md, qa/findings.md (Wortlaut QA-233 aus dem Auftrag zitiert), docs/state.md (Wortlaut aus dem Auftrag zitiert), GOAL.md A9 (Wortlaut aus dem Auftrag zitiert), tests/test_hostile_gamedata.py, tests/test_extraction.py, nrdata/binary.py, nrdata/dds.py, nrdata/oodle.py, nrdata/icons.py, nrdata/bossdata.py, requirements.txt, requirements-dev.txt, pytest.ini, tests/conftest.py
GEÄNDERT: tests/test_hostile_gamedata.py (committet, 0838cd9), docs/berichte/T-197-developer.md
ANNAHMEN: keine
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Faehigkeitsprobe

`pip install texture2ddecoder==1.0.6` — durchgelaufen, kein Build-Fehler:

```
Collecting texture2ddecoder==1.0.6
  Using cached texture2ddecoder-1.0.6-cp311-abi3-win_amd64.whl.metadata (8.6 kB)
Using cached texture2ddecoder-1.0.6-cp311-abi3-win_amd64.whl (64 kB)
Installing collected packages: texture2ddecoder
Successfully installed texture2ddecoder-1.0.6
```

Ein `cp311-abi3`-Wheel, kompatibel mit Python 3.12.10 x64 (bestaetigt: `python --version` → 3.12.10, `platform.architecture()` → 64bit). Import danach erfolgreich.

Zusaetzlich musste `pytest-xdist==3.8.0` installiert werden, weil `pytest -n auto` sonst mit `unrecognized arguments: -n` abbricht — auch das ist bereits in `requirements-dev.txt` gepinnt, keine neue Abhaengigkeit, nur derselbe fehlende-Paket-Zustand wie bei `texture2ddecoder`. Ohne diese Installation waere die von `CLAUDE.md` verlangte Suitezahl (`pytest -n auto`) auf dieser Maschine gar nicht erzeugbar gewesen. Das melde ich als ersten Punkt, wie vom Rahmen verlangt.

## Zaehlung der Erwartungen (Vorgabe 3)

`grep -n "pytest.raises" tests/test_hostile_gamedata.py` (vor meiner Aenderung) findet **15** Treffer, nicht 8 und nicht wortwoertlich zehn auf den ersten Blick — aber **zehn davon sind `pytest.raises(ValueError)`**: Zeile 66, 90, 95, 100, 107, 122, 128, 133, 277 und 283. Die Zahl aus dem Befund ("zehn Erwartungen ... sind pytest.raises(ValueError)") war also **korrekt**. Die im Auftrag zitierte Director-Zaehlung ("Das sind acht, nicht zehn") hat Zeile 277 und 283 uebersehen — die beiden `bossdata._parts`-Tests am Dateiende, die nicht in der Director-Aufstellung auftauchen. Die restlichen fuenf Treffer sind bereits eigene Klassen (`NotImplementedError` 112, `oodle.OodleUnavailable` 145, `icons.LayoutError` 176/192/200) und nie Teil der Zehn.

## Erst ausgefuehrt, dann geurteilt (Vorgabe 1)

`pytest tests/test_hostile_gamedata.py -v` lief vor jeder Aenderung durch (20 passed in 0.34s). Danach je Erwartung mit einem Probeskript ermittelt, welche Klasse tatsaechlich geworfen wird (`type(e).__mro__`), getrennt gegen `dds.py`, `oodle.py`, `icons.py`, `bossdata.py`:

| Zeile | Erwartung | tatsaechlich geworfen | Urteil |
|---|---|---|---|
| 66 | `ValueError` (dds, Payload 1 Byte kurz) | `ValueError` (dds.py wirft direkt, kein `binary`-Pfad) | pruefte bereits das Richtige — kein Wechsel |
| 90 | `ValueError` (dds, ungerade Groesse) | `ValueError` (dds.py direkt) | dito |
| 95 | `ValueError` (dds, 0 Pixel) | `ValueError` (dds.py direkt) | dito |
| 100 | `ValueError` (dds, Header zu kurz) | `ValueError` (dds.py direkt) | dito |
| 107 | `ValueError` (dds, DX10 ohne Extended Header) | `ValueError` (dds.py direkt) | dito |
| 112 | `NotImplementedError` | `NotImplementedError` (dds.py direkt) | bereits eigene Klasse, unveraendert |
| 122 | `ValueError` (oodle, ueber der Decke) | `ValueError` (oodle.py direkt) | pruefte bereits das Richtige |
| 128 | `ValueError` (oodle, Groesse 0) | `ValueError` (oodle.py direkt) | dito |
| 133 | `ValueError` (oodle, negative Groesse) | `ValueError` (oodle.py direkt) | dito |
| 145 | `oodle.OodleUnavailable` | dito | bereits eigene Klasse, unveraendert |
| 176 | `icons.LayoutError` | dito | bereits eigene Klasse (Unterklasse von `ValueError`, aber schon benannt), unveraendert |
| 192 | `icons.LayoutError` | dito | dito |
| 200 | `icons.LayoutError` | dito | dito |
| 277 | `ValueError` (bossdata, unterminierter Name) | `binary.NotWhatItClaims` (ueber `binary.read_cstring`) | **gutmuetig gegen die Oberklasse — verengt** |
| 283 | `ValueError` (bossdata, Offset ausserhalb des Records) | `binary.NotWhatItClaims` (ueber `binary.read_cstring`) | **gutmuetig gegen die Oberklasse — verengt** |

Begruendung fuer die acht, die `ValueError` bleiben (Vorgabe 2, "in einer Zeile"): `dds.py` und `oodle.py` importieren `nrdata.binary` gar nicht und werfen ihre Grenzpruefungen als plain `ValueError` bzw. `NotImplementedError` selbst — verengen wuerde eine Klasse verlangen, die der Code an dieser Stelle nie war und nie sein wollte.

Verengt wurden ausschliesslich `test_an_unterminated_part_name_is_a_data_error` und `test_a_part_name_offset_past_the_record_is_a_data_error` auf `binary.NotWhatItClaims` — beide rufen `bossdata._parts`, das ueber `binary.read_cstring` tatsaechlich `NotWhatItClaims` wirft (Beleg per Probeskript: `type(e).__mro__` → `(NotWhatItClaims, ValueError, ...)`).

## Rot-vorher (L-007)

Simuliert: `binary.read_cstring` durch eine Version ersetzt, die dieselbe `NotWhatItClaims` faengt und als plain `ValueError` neu wirft (eine Regression auf den Zustand vor T-193). Ergebnis: `pytest.raises(binary.NotWhatItClaims)` haette diese Regression gefangen — die alte, unverengte Erwartung `pytest.raises(ValueError)` haette es nicht. Beleg im Bericht via Probeskript, nicht nur behauptet.

## Suitezahl (Vorgabe 3)

Befehl: `pytest -n auto` (nach Installation von `texture2ddecoder==1.0.6` und `pytest-xdist==3.8.0`, **ohne jedes `--ignore`**):

```
2 failed, 1779 passed, 9 skipped in 138.40s (0:02:18)
```

Gegen die Vorgabe aus `CLAUDE.md` (Stand 08.09.2026: 1257 passed, 9 skipped, 0 failed). Ich erklaere die Differenz nicht ueber die zwei hinzugekommenen Dateien hinaus, weil ich sie nicht belegen kann — der Sprung ist deutlich groesser als die 27 Faelle aus `test_hostile_gamedata.py` (20) und `test_extraction.py` (7) allein erklaeren wuerden, und seit dem 08.09.2026 sind mehrere Auftraege gelaufen (u. a. T-193 bis T-196 laut Commit-Historie).

**Zwei Fehlschlaege, beide ausserhalb meines Auftrags und meines Diffs** (mein einziger geaenderter Pfad ist `tests/test_hostile_gamedata.py`, per `git diff --stat` bestaetigt):

1. `tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source[sort-by-offers-a-direction-nobody-scores]` — der Anker der Mutation `sort-by-offers-a-direction-nobody-scores` kommt 0-mal statt 1-mal in `nrplanner/advisorbar.py` vor. Quelltext ist unter dem Test weggedriftet (vermutlich durch die Advisor-Arbeit aus T-194, laut Commit-Historie `06be06e`). Datei ausserhalb meines Auftrags, nicht angefasst.
2. `tests/test_first_run_panel.py::test_the_first_dialog_opens_at_the_folder_that_was_remembered` — `firstrun.where_to_start_looking(None)` liefert auf dieser Maschine den echten Steam-Pfad (`d:/steam/steamapps/common`) statt `None` oder dem erwarteten Default-Windows-Pfad. Sieht nach einer Testisolationsluecke aus (liest den echten Registry-/Dateisystemzustand dieser Maschine statt ihn zu mocken), nicht nach einer Regression meiner Aenderung. Datei ausserhalb meines Auftrags, nicht angefasst.

Beide sind Befunde fuer den Director, kein Teil dieses Auftrags — ich habe weder `nrplanner/advisorbar.py`, `nrplanner/firstrun.py` noch deren Tests angefasst.

## Einzeldateien ohne `-n` (Vorgabe 4, Gegenproben-Regel)

```
pytest tests/test_hostile_gamedata.py -v   → 20 passed in 0.35s (nach der Aenderung)
pytest tests/test_extraction.py -v         → 7 passed in 57.08s
```

`test_extraction.py` brauchte **keine Aenderung**: die Datei enthaelt kein `pytest.raises` und lief bereits gruen gegen die echte Installation (die `slow`-Marker-Fixtures fanden ein installiertes Spiel auf dieser Maschine). Sie ist eine der drei erlaubten "Beruehrt Dateien" im Auftrag, blieb aber unveraendert — nur gepruewft.

## Scope-Grenzen eingehalten

- Extraktionscode (`nrdata/*.py`) nicht angefasst — keine Regel verletzt, kein echter Fehler dort gefunden.
- Keine `--ignore` in `pytest.ini`, keine `skipif`-Marke ergaenzt.
- `C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug` nicht angefasst (nicht existent laut QA-231/T-196, ich habe nichts dort erzeugt oder gelesen).
- `tests/conftest.py` (nicht meine Datei, nur gelesen) lenkt `NIGHTREIGN_SETTINGS_ORG`/`_APP` bereits automatisch fuer die ganze Suite um; ich habe keinen Fensterlauf des Programms selbst gestartet, nur `pytest`.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (keine)
- [x] Build & Tests: `pytest -n auto` lief; 2 Fehlschlaege ausserhalb meines Diffs benannt und nicht verdeckt
- [x] Neue/geaenderte Tests fuer geaenderte Erwartung (Rot-vorher belegt); kein Linter im Projekt konfiguriert
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Auftragskriterien selbst durchgespielt (Faehigkeitsprobe, Zaehlung, Urteil je Erwartung, Rot-vorher, Suitezahl, Einzeldatei ohne `-n`)
- [x] Doku: keine eigene Doku-Datei ausser diesem Bericht noetig; Befunde an director gemeldet statt selbst in `qa/findings.md`/`docs/state.md` eingetragen

## An qa-engineer

Nichts Neues zu testen aus diesem Auftrag selbst (reine Testverengung). Falls QA-233 formal geschlossen wird: die Suitezahl `2 failed, 1779 passed, 9 skipped` (Befehl `pytest -n auto`, ohne `--ignore`) ist die neue Referenz, nicht die 1257/9/0 von `CLAUDE.md` — die zwei aktuellen Fehlschlaege sind eigene Befunde, keine Regression dieses Auftrags.

## An director

1. **Neuer Befund (nicht QA-233, nicht dieser Auftrag):** `pytest-xdist` fehlte ebenfalls auf dieser Maschine, obwohl in `requirements-dev.txt` gepinnt — ich habe es installiert, sonst waere `pytest -n auto` (der in `CLAUDE.md` festgelegte Testbefehl) gar nicht ausfuehrbar gewesen. Keine neue Abhaengigkeit, nur derselbe Fehlbestand wie bei `texture2ddecoder`.
2. **Befund `test_differential_track.py`:** Mutationsanker `sort-by-offers-a-direction-nobody-scores` findet seinen Text nicht mehr in `nrplanner/advisorbar.py` — Quelltext ist unter dem Test weggedriftet, vermutlich durch die Advisor-Aenderungen aus T-194 (`06be06e`). Risiko: die Mutation deckt aktuell nichts ab, bis der Anker nachgezogen ist. Empfehlung: `developer`-Auftrag zum Nachziehen des Ankers.
3. **Befund `test_first_run_panel.py`:** `test_the_first_dialog_opens_at_the_folder_that_was_remembered` liest den echten Steam-Installationspfad dieser Maschine (`d:/steam/steamapps/common`) statt eines isolierten/gemockten Werts — sieht nach fehlender Testisolation aus, nicht nach einer echten Verhaltensaenderung. Risiko: auf jeder Maschine mit abweichender Steam-Installation rot, unabhaengig vom Code. Empfehlung: `fehlerdiagnostiker` oder `developer`-Auftrag zur Pruefung der Isolation in `test_first_run_panel.py`.
4. Beide Befunde 2 und 3 waren bereits vor meiner Aenderung im Baum vorhanden (mein Diff beruehrt ausschliesslich `tests/test_hostile_gamedata.py`) — ich habe sie nicht verursacht, nur beim geforderten vollen Suitelauf entdeckt.
5. Korrektur an der Director-Zaehlung im Auftrag: "acht, nicht zehn" (Zeile 65 in T-197.md) war selbst ungenau — die tatsaechliche Zahl der `pytest.raises(ValueError)`-Erwartungen war **zehn** (die Ausgangs-Zahl aus dem Befund stimmte), die Director-Aufstellung hatte Zeile 277 und 283 nicht erfasst.

Der Auftrag stimmte inhaltlich — keine Eskalation, nur die Korrektur unter Punkt 5 und die zwei neuen Befunde unter 2/3.
