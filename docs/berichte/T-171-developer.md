# T-171 - Der Datensatz bekommt eine Gestalt (developer)

```
STATUS: erledigt
AUFTRAG: T-171 - Der Datensatz bekommt eine Gestalt (docs/tasks/T-171.md)
GELESEN: docs/debug/D-001.md, docs/tasks/T-171.md, CLAUDE.md,
         nrdata/extract.py, nrdata/bossdata.py, nrplanner/model.py,
         nrplanner/paths.py, nrplanner/shortcut.py, nrplanner/favourites.py,
         scripts/build_snapshot.py, tests/conftest.py, tests/test_extraction.py,
         tests/test_advisor_evaluate.py, tests/test_marginal_returns.py
GEÄNDERT: nrdata/extract.py, nrdata/bossdata.py, nrplanner/model.py,
          scripts/build_snapshot.py, tests/test_extraction.py
          (alle fuenf in Commit a1172fb), docs/berichte/T-171-developer.md
ANNAHMEN: keine
NÄCHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

## Umgesetzt

Ein Commit, `a1172fb`, fuenf Dateien, genau die Whitelist des Auftrags.

| Stelle | vorher | nachher |
|---|---|---|
| `nrdata/extract.py:1917` (jetzt `:1922`) | `levels[lvl]`, Annotation `dict[int, …]` | `levels[str(lvl)]`, Annotation `dict[str, …]`, Kommentar mit D-001-Bezug |
| `nrdata/bossdata.py:415` (jetzt `:420`) | `{c: _profile(…) for c in chars}` | `{str(c): …}` |
| `nrdata/bossdata.py:487` (jetzt `:493`) | `{best: best_profile}` | `{str(best): …}` |
| `nrplanner/model.py:915` | Doppelgriff `… if str(level) in … else hero["levels"][level]` | `dict(hero["levels"][str(level)])` |
| `scripts/build_snapshot.py:28` | `hero["levels"][1]`, `[15]` | `["1"]`, `["15"]` |
| `tests/test_extraction.py` | — | neuer Regressionstest (+ `import json`) |

Die zehn heute roten Faelle in `test_advisor_evaluate.py` und
`test_marginal_returns.py` wurden **nicht angefasst** — sie sind von selbst
gruen geworden, wie der Auftrag es vorhergesagt hat. Kein Befund an dieser
Stelle.

## Der Regressionstest

`tests/test_extraction.py::test_the_built_dataset_survives_a_json_round_trip_unchanged`,
`slow`-markiert wie die ganze Datei, Eingabe die Fixture `extracted_game_data`
(also `extract.build()` gegen die Installation, nicht der Abzug).

Er prueft die **Eigenschaft**, nicht die zwei Fundstellen: er laeuft den
gebauten Baum ab und sammelt jede Abbildung, die einen Schluessel traegt, der
keine Zeichenkette ist — die Meldung nennt den Pfad, den Schluesseltyp und ein
Beispiel. Danach zusaetzlich der Kontrakt selbst,
`json.loads(json.dumps(data)) == data`, weil der auch die Wertseite deckt
(Tupel, Menge, NaN), von der der Schluesselgang nichts weiss.

**Rot vorher, gemessen** (leeres umgelenktes `LOCALAPPDATA`, `pytest
tests/test_extraction.py -k round_trip`, ohne `-n`):

```
E   AssertionError: 28 mappings would be renamed by a JSON round trip:
E     data['heroes'][0]['levels']: 15 of 15 keys are int, e.g. 1
E     …
1 failed, 5 deselected in 156.52s
```

28 — dieselbe Zahl, die der Diagnostiker vorhergesagt hat.

**Jede der beiden Schutzmassnahmen einzeln zurueckgenommen** (Mutation per
`cp`-Kopie gesetzt und zurueckgeholt, **nie** `git checkout --`):

| Mutation | Ergebnis |
|---|---|
| `levels[str(lvl)]` → `levels[lvl]`, sonst alles wie im Fix | **rot**, `10 mappings … data['heroes'][0..9]['levels']` |
| beide `parts`-Schluessel zurueck auf `int`, `levels` bleibt Text | **rot**, `18 mappings … data['bosses'][*]['weakness']['parts']`, z. B. Schluessel `7500` |

10 + 18 = 28. Beide Mutationen toeten im **Standardlauf** (kein Skip, keine
Sonderkonfiguration), und die Erwartung des Tests wird **nicht** aus der
bewachten Stelle gerechnet — sie ist die Sprachregel `isinstance(key, str)`.
Kein Gegenbau hat ueberlebt. Beide Dateien danach aus der `.orig`-Kopie
zurueckgeschrieben und per `grep` nachgesehen.

## Die Datei auf der Platte aendert sich um kein Zeichen — gemessen

Der Auftrag gibt das als gepruefte Vorbedingung mit; ich habe es nachgemessen,
weil daran haengt, ob `EXTRACT_VERSION` steigen muss und ob der feste
Testabzug gueltig bleibt. Einmal gebaut, dann eine Kopie, in der genau die
beiden reparierten Abbildungen wieder `int`-Schluessel tragen, und beide mit
den Parametern von `write_snapshot()` serialisiert:

```
vorher : 8007011 Zeichen  sha256 bf08618ac78c5b920e608a882e5f58c4d9b636b47076da7da7fdbcfbef4d7cc4
nachher: 8007011 Zeichen  sha256 bf08618ac78c5b920e608a882e5f58c4d9b636b47076da7da7fdbcfbef4d7cc4
identisch: True
```

`EXTRACT_VERSION` bleibt auf 11. Der feste Testabzug bleibt gueltig, jeder
vorhandene Spieler-Cache ebenso. Skript:
`…/scratchpad/T-171/datei_unveraendert.py`.

## Suitezahlen — mit Datenbedingung, beide Bedingungen

Befehl jeweils `pytest -n auto`, Branch `docs/audit-and-advisor-design`,
Windows 10 x64, `.venv/Scripts/python.exe`, alle drei Umlenkungen gesetzt.

| Bedingung | vorher (laut D-001) | **nachher, gemessen** |
|---|---|---|
| **leeres umgelenktes `LOCALAPPDATA`** (die eigentliche Abnahme) | 1692 passed, 1 failed, 9 errors | **1703 passed, 9 skipped, 0 failed** (287,94 s) |
| Testabzug im umgelenkten `LOCALAPPDATA` | 1702 passed | **1703 passed, 9 skipped, 0 failed** (179,70 s) |

Die Rechnung geht auf: 1692 + 10 wieder gruene + 1 neuer Test = 1703, und
1702 + 1 neuer Test = 1703. **Beide Bedingungen liefern jetzt dieselbe Zahl** —
das ist die Aussage des Fixes.

Nebenbei gemessen und fuer die Auflage aus D-001 relevant: der Lauf **ohne**
Abzug kostet 288 s gegen 180 s, weil unter `-n auto` jeder xdist-Worker seine
eigene Extraktion baut. Rund 108 s Aufschlag je Zyklus fuer den vom
Diagnostiker verlangten abzugsfreien Lauf.

## Umlenkungsnachweis — mit Positivkontrolle und Gegenprobe danach

Sondierungsskript druckt `paths.cache_dir()`, `paths.snapshot_path()`,
`shortcut.shortcut_path()` und `favourites.ORG`.

**Kontrolle ohne Umlenkung** (zeigt, dass die Messung wirklich auf die Orte
des Spielers zeigt, wenn nichts umlenkt):

```
cache_dir()      -> C:\Users\Daniel\AppData\Local\NightreignHelper
shortcut_path()  -> C:\Users\Daniel\AppData\Roaming\…\Programs\Nightreign Helper.lnk
favourites.ORG   -> DankYeeter
```

**Mit Umlenkung** (beide Bedingungen, hier die Abzugs-Variante):

```
cache_dir()      -> …\scratchpad\T-171\local_abzug\NightreignHelper
shortcut_path()  -> …\scratchpad\T-171\appdata_abzug\Microsoft\Windows\Start Menu\Programs\Nightreign Helper.lnk
favourites.ORG   -> DankYeeterT-171
```

Alle drei Variablen sind umgelenkt: `LOCALAPPDATA`, `APPDATA`,
`NIGHTREIGN_SETTINGS_ORG`.

**Gegenprobe nach allen Laeufen**, jeweils Vorher-/Nachher-Liste `diff`t:

| geprueft | Ergebnis |
|---|---|
| echtes `%LOCALAPPDATA%\NightreignHelper` (843 Eintraege, Zeit/Groesse/Pfad) | identisch |
| echtes Start-Menue `Programs` (79 Eintraege) | identisch |
| `HKCU\Software\DankYeeter` (`reg query … -s`, 160 Zeilen) | identisch |
| `HKCU\Software\DankYeeterT-171` (mein eigener Org-Schluessel) | existiert vorher **und nachher nicht** |
| Vorlage `…\NightreignHelper-Testabzug` | unveraendert, 841 Dateien in die Umlenkung kopiert |

Einschraenkung, damit die Zeile nicht mehr behauptet als sie traegt: das
umgelenkte `APPDATA` nimmt der Suite den Spielstand **nicht** weg —
`savefile.save_roots()` sucht `~/AppData/Roaming/Nightreign` unbedingt, also
lesen die savestand-abhaengigen Faelle weiter die echte Datei, **read-only**.
Umgelenkt ist damit der Verknuepfungspfad, nicht der Save-Ordner. Und: unter
`pytest` ueberschreibt `tests/conftest.py` den Org-Wert ohnehin mit
`DankYeeterTests` — auch das ist vom Speicher des Spielers weg, aber es ist
nicht mein Wert, der benutzt wurde.

## L-006: die Eigenschaft geschlossen, nicht die Fundstelle

Nach dem Fix projektweit gesucht, zwei unabhaengig formulierte Masken, `.venv`
und `.git` ausgenommen:

| Maske | Treffer |
|---|---|
| `\["levels"\]\[[0-9]` (Zahl-Indizierung von `levels`) | **1** — und der ist `docs/tasks/T-171.md:45`, also der Auftragstext selbst, kein Code |
| `\["parts"\]\[` (Indizierung von `parts` ueberhaupt) | **0** |

Der belastbarere Nachweis ist aber nicht der Grep, sondern der Test: er misst
den **tatsaechlich gebauten** Datensatz und findet dort **0** Abbildungen mit
Nicht-Text-Schluessel. Damit ist die Eigenschaft fuer den ganzen Baum
geschlossen, nicht nur fuer die drei benannten Zeilen.

## Annahmen

Keine. Alle Vorgaben standen im Auftrag oder in D-001; nichts geraten.

## Tests

- **Neu:** der Regressionstest oben. Abgedeckt: jede Abbildung im gebauten
  Datensatz, plus die Wertseite ueber den Rundlauf.
- **Bewusst nicht abgedeckt:** ein Test, der `bosses[*]["weakness"]["parts"]`
  fachlich indiziert. Es gibt heute **keinen** Verbraucher dieser Abbildung
  (Grep-Treffer 0, siehe oben), also gaebe es nichts zu bewachen ausser der
  Schluesselform — und die bewacht der neue Test bereits.
- Keine bestehende Testdatei geaendert, keine Erwartung angepasst, kein Test
  deaktiviert oder geloescht.

## DoD

- [x] Anforderung verstanden, keine offenen Annahmen
- [x] Build & Tests gruen in **beiden** benannten Datenbedingungen, Zahlen mit
      Bedingung genannt
- [x] Neuer Test fuer neue Logik, rot-vorher und je Schutzmassnahme einzeln
      belegt
- [ ] **Linter entfaellt** — das Projekt hat keinen konfiguriert (kein
      `ruff`/`flake8`/`pylintrc`/`pyproject.toml`/`setup.cfg` im Baum;
      `pytest.ini` ist die einzige Werkzeugkonfiguration). Das ist keine
      Luecke und braucht keine Ersatzpruefung.
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Abnahmekriterium des Auftrags selbst durchgespielt
- [x] Abschlussbericht geschrieben und abgelegt

**Ungeprueft:** Linux und macOS — kein Zielsystem. Die Oberflaeche wurde nicht
gestartet; dieser Fix beruehrt keine Anzeige, und der `power-user`-Lauf ist
ausdruecklich nicht mein Scope.

## An qa-engineer

- Der Regressionstest heisst
  `tests/test_extraction.py::test_the_built_dataset_survives_a_json_round_trip_unchanged`
  und ist `slow`. **Er laeuft mit `-m "not slow"` nicht** — eine gruene Zahl
  aus so einem Lauf sagt ueber diesen Fix nichts.
- **Der abnahmerelevante Lauf ist der ohne erreichbaren Datenabzug**: leeres
  umgelenktes `LOCALAPPDATA`. Erwartung `1703 passed, 9 skipped, 0 failed`.
  Mit Testabzug kommt dieselbe Zahl heraus — dass beide Bedingungen jetzt
  gleich sind, **ist** das Abnahmekriterium.
- Kantenfaelle, die ich empfehle: (a) ein Nightfarer-Stat-Blatt fuer Level 1
  und 15 in beiden Bedingungen vergleichen — die Zahlen muessen identisch
  sein, denn nur der Schluesseltyp hat sich geaendert; (b) der Nightlord-Tab
  mit `weakness.profile` (nicht `parts`) in beiden Bedingungen; (c) ein
  vorhandener `nightreign_data.json` aus der Zeit **vor** diesem Commit muss
  weiter geladen werden — er ist byteweise derselbe, siehe der sha256-Beleg,
  aber ein Ladeversuch mit dem alten Abzug ist die billigste Gegenprobe dazu.
- Der abzugsfreie Lauf kostet unter `-n auto` rund **108 s mehr** (288 s statt
  180 s), weil jeder Worker selbst extrahiert. Bitte einplanen, das ist kein
  Haenger.

## An ui-ux-designer

Keine Abweichung. Der Fix beruehrt keine Oberflaeche und keinen angezeigten
Wert — die Datei auf der Platte ist byteweise dieselbe.

## An director

**Sicherheitsfunde:** keine.

**Performance-Fund (kein Handlungsbedarf, nur zur Kenntnis):** die volle Suite
ohne Datenabzug kostet 288 s gegen 180 s mit Abzug, weil unter `-n auto` jeder
xdist-Worker seine eigene 40-s-Extraktion baut. Wenn die Auflage aus D-001
("mindestens einmal je Zyklus ohne erreichbaren Abzug") dauerhaft gilt, sind
das rund 108 s je Zyklus. Eine Sitzungs-uebergreifende Wiederverwendung waere
denkbar, ist aber **nicht** mein Auftrag und faellt in den Bereich des
`performance-tuner`.

**Debt-Fund, klein, nicht behoben:** `bosses[*]["weakness"]["parts"]` hat
heute **keinen** Verbraucher — Volltextsuche nach `["parts"][` ergibt 0
Treffer. Die Abbildung wird gebaut, serialisiert (rund 18 Eintraege) und nie
gelesen. Nach dem Fix tragen ihre Schluessel Text, waehrend die Nachbarfelder
`chars` und `primary` weiter `int` sind; wer sie spaeter benutzt, muss
`parts[str(primary)]` schreiben. Das steht als Kommentar an der Fundstelle.
**Ort:** `nrdata/bossdata.py:415-425` und `:489-494`. **Art:** ungenutztes
Datenfeld mit Stolperkante. **Risiko:** niedrig, der neue Test faengt die
Schluesselform, nicht aber einen `parts[primary]`-Griff. **Aufwand:** Feld
entfernen ~15 min, oder eine Zeile Doku. Ich habe es **nicht** angefasst — es
stand nicht im Auftrag.

**Eskalation:** keine. Es gab keinen Widerspruch zwischen D-001, dem Auftrag
und dem Code; alle drei benannten Fundstellen lagen dort, wo sie angekuendigt
waren, und die zehn roten Faelle mussten nicht angefasst werden.

**Fuer `docs/state.md`** (ich schreibe dort nicht hinein): Suite jetzt
**1703 passed, 9 skipped, 0 failed — und zwar in beiden Datenbedingungen**,
leeres umgelenktes `LOCALAPPDATA` wie auch Testabzug im umgelenkten
`LOCALAPPDATA`. Commit `a1172fb`.
