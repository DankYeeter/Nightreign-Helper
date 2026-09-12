STATUS: erledigt
AUFTRAG: T-211 - NH-003: ein Waechter fuer die beiden Befundtabellen
GELESEN: docs/tasks/T-211.md, qa/findings.md, security/findings.md, .claude/agent-memory/developer/MEMORY.md, .claude/agent-memory/developer/project_waechter_kosten_dateien.md, tests/test_app_version.py (Stilvorbild fuer REPO_ROOT-Muster)
GEÄNDERT: tests/test_findings_tables.py (neu, committet 61d17f4), docs/berichte/T-211-developer.md (dieser Bericht)
ANNAHMEN: keine, ausser der unten dokumentierten Abweichung bei "vier von fuenf"
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Umgesetzt

`tests/test_findings_tables.py` (neu, 193 Zeilen). Liest `qa/findings.md`
und `security/findings.md` als reinen Markdown-Text (keine Bibliothek,
keine neue Abhaengigkeit) und prueft jede Befundzeile gegen vier Regeln:

1. `test_every_row_has_the_header_column_count` - Spaltenzahl jeder Zeile
   gegen die Spaltenzahl der **eigenen** Kopfzeile (`| ID | ... |`), nicht
   gegen eine Konstante. `qa/findings.md` hat 8 Spalten, `security/findings.md`
   5 - beide Zahlen kommen zur Laufzeit aus der Datei.
2. `test_every_row_closes_with_a_pipe` - die Zeile endet auf ein
   unescapetes `|`.
3. `test_status_column_is_never_a_bare_date` - die Zelle unter der Spalte
   "Status" (per Name aus der Kopfzeile gefunden) ist nach Entfernen von
   Markdown-Sternchen kein reines `JJJJ-MM-TT`.
4. `test_last_checked_column_is_always_a_date` - die Zelle unter "Letzte
   Pruefung" (ebenfalls per Name gefunden) ist genau das.

Fehlermeldungen nennen Datei (Parametrisierung ueber den Pfad), Zeilennummer
(1-basiert, editorgleich) und die Befund-ID (erste Zelle der Zeile).

`split_table_row()` behandelt `\|` als escapetes, woertliches Pipe-Zeichen -
das ist die Schreibweise, die QA-240s eigene Beschreibung heute traegt
(`git show HEAD~1:<datei> \| sed -n`). Ohne diese Behandlung waere die
Kopfzeilen-Zaehlung an genau dieser Zeile falsch positiv angeschlagen.

Blindgaenger geprueft: `qa/findings.md` enthaelt eine echte Leerzeile
mitten in der Tabelle (Zeile 258, zwischen QA-235 und QA-236) - kein Tippfehler
meinerseits, mit `python -c` gegen die Rohbytes nachgemessen. Das Parsen
ueberspringt Leerzeilen, statt die Tabelle dort fuer beendet zu erklaeren,
sonst waeren QA-236 bis QA-243 (8 Zeilen) unbeaufsichtigt geblieben, ohne
dass ein Test das gemeldet haette.

## Rot-vorher, vier Regeln, an einer Kopie im Scratchpad

Vier Kopien von `qa/findings.md` unter
`…/scratchpad/T-211/qa-findings-broken-*.md`, je eine Zeile (QA-018) gezielt
nach dem historischen Fehlerbild von heute mutiert, dann die Erkennerfunktionen
aus dem neuen Modul direkt gegen den mutierten Text aufgerufen (nicht die
echten Dateien angefasst):

```
--- columncount (QA-240-Muster: rohes Pipe im Beschreibungstext) ---
  line 37 (QA-018): 9 columns, header has 8
--- closingpipe (QA-225/226/227-Muster: fehlende Abschlusspipe) ---
  line 37 (QA-018): no closing pipe
--- status-is-date (QA-211-Muster: Status durch Datum ueberschrieben) ---
  line 37 (QA-018): Status column reads a bare date ('2026-09-08')
--- date-not-date (kein historisches Vorbild, symmetrische Haertung) ---
  line 37 (QA-018): Letzte Pruefung column is not a plain YYYY-MM-DD date ('TBD')
```

Jede Regel schlaegt genau auf ihren eigenen Fall an, keine Ueberschneidung
geprueft.

**Abweichung von Vorgabe 4, gemeldet statt stillschweigend passend gemacht:**
der Auftrag erwartet "vier von fuenf Regeln haetten die echten Faelle von
heute fangen muessen". Ich baue vier Regeln (Vorgabe 2 nennt genau vier), und
die fuenf realen kaputten Zeilen verteilen sich so: QA-240 -> Regel 1
(Spaltenzahl), QA-225/QA-226/QA-227 -> Regel 2 (Abschlusspipe), QA-211 ->
Regel 3 (Status kein Datum). Das sind **drei** meiner vier Regeln, die
zusammen **alle fuenf** realen Zeilen gefangen haetten. Regel 4
(Datumsspalte ist ein Datum) hat unter den fuenf dokumentierten Faellen kein
Vorbild - sie ist die von Vorgabe 2 ausdruecklich verlangte Gegenrichtung zu
Regel 3, nicht durch einen realen Fall belegt. Ich habe keine sechste kaputte
Zeile gefunden, die Regel 4 gebraucht haette; falls der `director` eine
kennt, bitte nennen, dann baue ich den fuenften Rotlauf nach.

## Gegenprobe: beide Dateien heute gruen

```
python -m pytest tests/test_findings_tables.py -v
8 passed in 0.37s
```

Deckt sich mit der Director-Zahl (243 QA-Zeilen als grobe Angabe, 42
SEC-Zeilen, 0 kaputt) - mit einer Praezisierung: die exakte Zeilenzahl in
`qa/findings.md` ist 246, nicht 243. Der Unterschied sind QA-099a, QA-099b,
QA-099c - drei Buchstaben-Varianten derselben Nummer, die in einer reinen
`QA-\d+`-Zaehlung fehlen. Kein Waechter dieser Datei zaehlt Zeilen insgesamt,
also hat das keine Auswirkung auf den Test - nur auf die Vergleichszahl im
Bericht, deshalb hier vermerkt statt verschwiegen.

## Suitezahl

```
python -m pytest -n auto -q
1789 passed, 9 skipped in 136.74s (0:02:16)
```

Ausgangswert laut Auftrag: 1781 passed, 9 skipped. Differenz +8 = genau die
acht neuen parametrisierten Tests (4 Regeln x 2 Dateien). Keine neuen
Skips, keine Fehlschlaege.

## DoD

- Anforderung verstanden, eine Abweichung dokumentiert (siehe oben) statt
  stillschweigend passend gemacht.
- Build & Tests gruen unter Windows 10/11 x64 (Zielsystem laut CLAUDE.md;
  diese Maschine). Keine andere Plattform zu pruefen.
- Neue Tests fuer neue Logik: der gesamte Auftrag *ist* neue Testlogik.
  Kein Linter im Projekt konfiguriert (`ruff`/`flake8`/`pylint` nicht
  gefunden) - Punkt entfaellt, keine Luecke.
- Keine Secrets, keine TODOs, kein toter Code.
- QA-Akzeptanzkriterien: keine gesonderten, der Auftrag *ist* die
  Akzeptanzpruefung fuer NH-003.
- Doku: keine der mir gehoerenden Dateien (`docs/state.md`,
  `qa/findings.md` etc.) angefasst - das ist Sache des Directors laut
  Scope-Grenze des Auftrags.

DoD erfuellt, keine offenen Punkte in meinem Scope.

## An director

- Die Abweichung "vier von fuenf Regeln" oben - bitte pruefen, ob eine
  sechste kaputte Zeile bekannt ist, die Regel 4 (Datumsspalte) historisch
  belegen wuerde, oder ob die Formulierung im Auftrag ungenau war und drei
  von vier reicht.
- Praezisierung der Zeilenzahl: 246 statt 243 in `qa/findings.md` (Grund:
  QA-099a/b/c), falls das an anderer Stelle als Referenzzahl weiterlebt.
- Fremde, nicht von mir verursachte Aenderungen im Arbeitsbaum bei Auftragsende:
  `scripts/measure_advisor_block.py` und `scripts/measure_picker_cards.py`
  stehen als `M` in `git status`, ich habe sie nicht angefasst - vermutlich
  Rest von T-212 (`scripts/`), das laut Auftrag parallel laeuft. Nicht
  committet, nur zur Kenntnis.
- Kein Sicherheits- oder Datenverlustrisiko in meinem Teil gefunden.

## An qa-engineer

Zu pruefen waere vor allem die Symmetrie-Annahme: verhaelt sich der Waechter
korrekt, wenn eine kuenftige Zeile in `security/findings.md` (5 Spalten,
andere Spaltenindizes als `qa/findings.md`) denselben Fehler macht wie
QA-211/QA-240? Die vier Regeln sind absichtlich generisch ueber die
Kopfzeile gebaut, das ist aber nur an den beiden echten Dateien geprueft,
nicht an einer dritten, absichtlich anders geformten Tabelle. Kein
Edge-Case-Test fuer eine Tabelle ganz ohne Datenzeilen (leere Kopfzeile
plus Separator, keine Zeile danach) - beide echten Dateien haben immer
mindestens eine Zeile, daher kein Testfall dafuer im neuen Modul.

## An ui-ux-designer

Nicht betroffen, kein UI-Bezug.
