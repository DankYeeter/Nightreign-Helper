STATUS: teilweise
AUFTRAG: T-204 — Korb 1: `StrEnum` statt zweier `str`-Unterklassen, `baseline_for` inlinen
GELESEN: docs/tasks/T-204.md, nrplanner/advisor/types.py, nrplanner/advisor/goals.py, nrplanner/relicpicker.py, tests/test_advisor_candidates.py, tests/test_advisor_types.py, tests/picker_track.py, ARCHITECTURE.md (Zeilen um 2455-2469), docs/berichte/T-197-developer.md, docs/berichte/T-201-qa-engineer.md (QA-233-Kontext)
GEÄNDERT: nrplanner/advisor/types.py (baseline_for entfernt), tests/test_advisor_candidates.py (Aufruf inline), docs/berichte/T-204-developer.md (dieser Bericht)
ANNAHMEN: keine
NÄCHSTER: director
BLOCKIERT DURCH: nichts — Ziel 1 ist ein begruendeter Widerspruch, kein Blocker

## Ziel 1 — Widerspruch: `StrEnum` bleibt aus, die Klassen bleiben stehen

`ChosenDirection`/`PoolOrder` werden nicht gegen einen festen Wertevorrat
geprueft, sondern gegen **eine Rolle** (gewaehlte Richtung vs. blosse
Sortierung), und genau das traegt bereits heute: `isinstance(x,
ChosenDirection)` unterscheidet die beiden Klassen zuverlaessig voneinander,
weil es zwei verschiedene Python-Typen sind — das ist der Teil, den
`AdvisorRequest.__post_init__` (types.py:305-307) tatsaechlich braucht und
den auch die heutige Form schon einhaelt.

Was eine leere `str`-Unterklasse nicht kann: den **Wert** pruefen. Sowohl
`ChosenDirection("beliebiger_unsinn")` als auch `PoolOrder("beliebiger_unsinn")`
gelingen anstandslos. Genau das waere der Gewinn von `StrEnum` — Konstruktion
mit einem unbekannten Wert wirft `ValueError`.

Dieser Gewinn ist hier aber nicht sauber zu haben:

1. **Die gueltigen Werte kommen aus `goals.py:GOALS`** — drei Eintraege
   (`max_damage`, `min_damage_taken`, `max_attributes`), als
   `MappingProxyType`, explizit kommentiert als "die Registry ... read-only".
2. **`goals.py` importiert `types.py`** (`from . import types`, goals.py:56).
   `types.py` kann `goals.py` also nicht importieren, um die Werte fuer den
   Enum aus der Registry zu ziehen — Zirkelimport. Eine Umstrukturierung
   dieser Abhaengigkeit ist nicht Teil des Auftrags (Scope-Grenze: kein
   `architect`-Entwurf in diesem Korb).
3. **Bliebe: die drei Strings ein zweites Mal in `types.py` hart codieren.**
   Das widerspricht dem Muster, das dieses Modul selbst an anderer Stelle
   einfordert ("one place, not two", `Slot.colour`-Docstring, types.py:85f)
   und macht aus einer Dokumentationsungenauigkeit eine echte
   Verfuegbarkeitsgefahr: wird `goals.py:GOALS` um eine vierte Richtung
   erweitert (das Registry-Kommentar erwartet das ausdruecklich als normalen
   Vorgang) und der Enum in `types.py` nicht im selben Schritt nachgezogen,
   wirft **jeder** gewoehnliche Aufruf mit der neuen Richtung
   `ChosenDirection(goal_id)` in `__post_init__` einen `ValueError` — eine
   vorher funktionierende Anfrage bricht, statt wie heute nur
   typ-ungeprueft durchzulaufen. Das ist die gleiche Falle wie QA-233 in
   umgekehrter Richtung: nicht eine Pruefung, die durchlaesst, sondern eine
   Pruefung, die durch eine unsynchronisierte zweite Werteliste zufaellig
   und still zu frueh zuschlaegt.

Damit haelt `StrEnum` die Aussage aus Nachtrag IX-2 ("eine Richtung, die nur
sortiert hat, darf nie als gewaehlte gelesen werden") nicht besser als die
heutigen Klassen — die Rollentrennung funktioniert bereits per `isinstance`.
Es wuerde nur eine zusaetzliche, unabhaengig zu pflegende Wertepruefung
einfuehren, deren Pflegekosten (zwei Quellen fuer dieselben drei Strings,
ohne dass der Zirkelimport das automatisch absichert) den Nutzen im aktuellen
Zuschnitt uebersteigen. Ich habe die Klassen **unveraendert gelassen**.

Der Kommentarsatz "enforced rather than hoped for" (types.py:225) ist davon
unabhaengig weiterhin ungenau — er ueberzeichnet, was `isinstance` allein
leistet. Weil dieser Auftrag Prosakuerzung ausdruecklich ausschliesst und die
Ausnahme dafuer ("den ziehst du nach") explizit an die Umsetzung von Ziel 1
gebunden war, habe ich den Satz **nicht** angefasst. Das ist ein offener
Punkt fuer die separate Prosa-Aufgabe oder eine erneute Entscheidung des
`director`, nicht etwas, das ich in diesem Auftrag stillschweigend regeln
durfte.

## Ziel 2 — `baseline_for` inlined und entfernt

Zweiter Aufrufer nicht gefunden — die Zaehlung des Directors stimmt (`grep -rn
baseline_for` im ganzen Baum: nur `nrplanner/advisor/types.py:801`
[Definition], `tests/test_advisor_candidates.py:398` [einziger Aufruf], dazu
zwei Doku-Erwaehnungen in `ARCHITECTURE.md` und `docs/state.md`, keine davon
ein Aufruf).

`nrplanner/advisor/types.py`, Funktion `baseline_for` (vormals Zeilen
801-807) entfernt.

`tests/test_advisor_candidates.py:398` (in
`test_the_base_state_of_a_slot_is_the_build_with_that_slot_emptied`):

```python
baseline_value = next(baseline.value for baseline in pool.baseline
    if baseline.goal_id == SURVIVAL)
assert baseline_value == pytest.approx(
    goals.GOALS[SURVIVAL].score(evaluate(emptied, (), ctx), ctx).value)
```

statt vormals `types.baseline_for(pool, SURVIVAL)`. Verhalten fuer den
getesteten Fall identisch (Wert existiert in `pool.baseline`); auf das
`KeyError` mit eigener Fehlermeldung bei fehlendem Eintrag habe ich verzichtet
— in dieser Testfunktion wird der Fall nie erreicht, ein `StopIteration` aus
`next()` ohne Default waere im Fehlerfall ebenso sichtbar (Testlauf schlaegt
fehl), nur mit generischerer Meldung. Das ist eine Formsache, kein
Verhaltensunterschied fuer den Test selbst.

**Nicht angefasst, aber betroffen:** `ARCHITECTURE.md:2459` nennt
`baseline_for(pool, goal_id) -> float` als weiterhin gueltige Funktion — das
ist jetzt eine Doku-Ungenauigkeit. `ARCHITECTURE.md` gehoert laut Rollenregel
nicht mir; ich melde es hier, statt es selbst zu aendern.

## Zeilendifferenz

`git diff --stat`:
```
nrplanner/advisor/types.py       | 9 ---------
tests/test_advisor_candidates.py | 4 +++-
2 files changed, 3 insertions(+), 10 deletions(-)
```

`types.py` netto -9 Zeilen (die entfernte Funktion inkl. Leerzeilen),
`tests/test_advisor_candidates.py` netto +3 Zeilen (Inline-Ausdruck statt
Funktionsaufruf). Insgesamt **-6 Zeilen** ueber beide Dateien. Die Differenz
stammt ausschliesslich aus Ziel 2 — Ziel 1 ist nicht umgesetzt und traegt
keine Zeilen bei.

## Suitezahl

```
python -m pytest -n auto -q
```
→ `1781 passed, 9 skipped in 131.23s` — deckungsgleich mit dem vom Director
gemessenen Ausgangswert (`0 failed, 1781 passed, 9 skipped in 135.24s`).
Zusaetzlich `pytest tests/test_advisor_candidates.py tests/test_advisor_types.py -q`
(ohne `-n`, die beiden unmittelbar beruehrten Dateien): `82 passed in 35.26s`.

QA-238 (`tests/test_advisor_worker.py:360`) ist in keinem der beiden Laeufe
aufgefallen — kein Nachlauf noetig.

## Dateien

Fuenf erlaubte plus Bericht — genutzt wurden zwei: `nrplanner/advisor/types.py`
und `tests/test_advisor_candidates.py`. `nrplanner/relicpicker.py`,
`tests/test_advisor_types.py` und `tests/picker_track.py` blieben unberuehrt,
weil Ziel 1 nicht umgesetzt wurde. Die Fuenf-Dateien-Grenze wurde nicht
erreicht, geschweige denn gerissen.

## DoD

- Anforderung verstanden, Annahmen: keine offenen.
- Build/Tests gruen wie oben, Windows-Testumgebung (dieser Rechner) — keine
  andere Plattform zu pruefen fuer diesen Auftrag.
- Kein Linter im Projekt konfiguriert (`.flake8`/`setup.cfg`/`pyproject.toml`/
  `tox.ini` nicht vorhanden) — Punkt entfaellt, keine Luecke.
- Neuer Test fuer neue Logik: keine neue Logik, reine Formsache (Inline eines
  Zugriffs, Entfernen einer ungenutzten Funktion); bestehende Tests decken
  den geaenderten Pfad bereits ab (siehe Suitelauf oben).
- Keine Secrets, keine TODOs, kein toter Code.
- Kein QA-Akzeptanzkriterium in diesem Auftrag (Formsache, keine
  Oberflaeche betroffen).
- Doku: `ARCHITECTURE.md` ist jetzt an einer Stelle veraltet (siehe oben) —
  nicht von mir aktualisierbar, an director gemeldet.

## An director

- **Ziel 1 nicht umgesetzt, mit Begruendung** (siehe oben): Zirkelimport
  `goals.py` ↔ `types.py` und Registry-Duplikat waeren der Preis, der Nutzen
  (Wertepruefung statt reiner Rollenpruefung) ist gegen dieses Risiko klein.
  Falls der Wunsch nach `StrEnum` bestehen bleibt: das braeuchte entweder
  einen `architect`-Schnitt, der den Zirkelimport aufloest (z. B. die
  Goal-Id-Liste an einen dritten, von beiden importierten Ort verschieben),
  oder eine bewusste Entscheidung, die Werteliste doppelt zu fuehren und den
  Pflegeaufwand in Kauf zu nehmen.
- Der Kommentarsatz "enforced rather than hoped for" (types.py:225) bleibt
  ungenau — unabhaengig von meiner Ziel-1-Entscheidung. Gehoert entweder in
  die separate Prosa-Kuerzung oder als eigener kleiner Folgeauftrag.
- `ARCHITECTURE.md:2459` erwaehnt `baseline_for` als weiterhin gueltig — nach
  Ziel 2 nicht mehr wahr. Bitte durch die zustaendige Rolle nachziehen.

## An qa-engineer

Nichts Neues zu testen — reine interne Formsache ohne Oberflaechenwirkung.
Falls geprueft werden soll: `test_the_base_state_of_a_slot_is_the_build_with_that_slot_emptied`
in `tests/test_advisor_candidates.py` deckt den inlineten Pfad ab und ist
Teil der oben gemeldeten gruenen Laeufe.

## An ui-ux-designer

Keine Beruehrung — kein UI-Code, keine Oberflaechentexte geaendert.
