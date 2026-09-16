# T-206 — Korb 1: die Prosakuerzung, als Pilot auf drei Dateien

```
STATUS: erledigt
AUFTRAG: T-206 — Korb 1: die Prosakuerzung, als Pilot auf drei Dateien
GELESEN: docs/tasks/T-206.md; CLAUDE.md (Projektzeilen); nrplanner/model.py,
  nrplanner/advisor/explain.py, nrplanner/damage.py (je vollstaendig);
  ARCHITECTURE.md AD-020 (Z. 746-816) und die Trefferliste zu AD-005/019/022;
  UI_SPEC.md Z. 3371-3372; tests/test_advisor_explain.py (Z. 844-852,
  1455-1500), tests/test_interface_language.py (Z. 85-155),
  tests/test_one_dash_style.py, tests/test_one_name_per_figure.py,
  tests/test_move_scoped_effects.py, tests/test_weapon_tile_and_panel_agree.py
  (Z. 170-183), tests/test_one_build.py (Z. 27-45, 300-390),
  scripts/differential/mutate.py (alle 34 Anker auf die drei Dateien)
GEAENDERT: nrplanner/model.py, nrplanner/damage.py, nrplanner/advisor/explain.py
  — committet als 4cd8936 (`git commit ... -- <die drei Pfade>`, kein `-a`);
  docs/berichte/T-206-developer.md (**uncommittet**, liegt auf der Platte, der
  Director legt sie ab); ausserdem zwei eigene Gedaechtnisdateien unter
  .claude/agent-memory/developer/ (Suitelauf-Notiz war falsch, siehe
  "Nebenbefund zum Testbefehl"; Waechter-Notiz um den mutate.py-Anker
  ergaenzt). Keine fremde Datei angefasst, kein Push.
ANNAHMEN: (1) "Doppelt woanders" schliesst Doppelungen **innerhalb derselben
  Datei** ein — der Auftrag nennt woertlich nur ARCHITECTURE.md/UI_SPEC.md,
  verlangt aber "je geloeschtem Block die Ersatzstelle", und zwei der sieben
  Kuerzungen haben ihre Ersatzstelle in derselben Datei. (2) Wo eine Zeile
  sowohl eine AD-Nummer traegt als auch deren Inhalt nacherzaehlt, habe ich
  die Nummer stehen gelassen und nur den nacherzaehlenden Teil geloescht
  (der Auftrag sagt beides: "Verweis bleibt, Wortlaut geht" gegen "jede
  Zeile mit AD-Nummer bleibt woertlich"). Betrifft genau damage.py Z. 22.
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

## Umgesetzt

Sieben Bloecke, 20 Prosazeilen, Commit `4cd8936`. Je Block die Stelle, die
dasselbe sagt (Zeilennummern **nach** der Aenderung):

| # | geloescht | Zeilen | Ersatzstelle, die dasselbe sagt |
|---|---|---|---|
| 1 | `model.py` Krit-Block vor `CONDITIONAL_FIELDS` (war Z. 324-329) | 6 | `nrplanner/model.py:994-998` — derselbe Sachverhalt vollstaendiger an der Verwendungsstelle in `compute()`, plus die Umleitung selbst in `model.py:1042-1047`. Zusaetzlich `nrplanner/damage.py:499-501`. Der Block war **verwaist**: er stand ohne Leerzeile vor dem Kommentar einer *anderen* Konstante und sprach von "this flag", waehrend `CRIT_FLAG` 300 Zeilen weiter unten definiert ist. |
| 2 | `model.py` Rueckfall-Satz vor `FIELD_BASELINE` (war Z. 203-205) | 3 | `nrplanner/model.py:251-256` (derselbe Rueckfall, mit **QA-011** und der Zahl, die er kostet) und `nrplanner/model.py:267-268` (dass `configure()` aus `field_baselines` fuellt, steht als Code da). |
| 3 | `model.py` Schluss des `compute()`-Docstrings (war Z. 904-906) | 3 | `nrplanner/model.py:251-256` (QA-011) und der Meldungstext des `RuntimeError` selbst, `nrplanner/model.py:893-899` — dieselbe Begruendung, dort als Text an den Leser. Der Satz "Raises RuntimeError until configure() has been given the game data." bleibt. |
| 4 | `model.py` Kommentar in `compute_derived()` (war Z. 862-863) | 2 | `nrplanner/model.py:852-853` — die zwei Codezeilen, die er ankuendigt (`raised = evaluate_curve(...)`, dann `rate = build.rates.get(...)`). |
| 5 | `model.py` Docstring von `is_multiplier` (war Z. 281) | 1 | Der Funktionsname plus `nrplanner/model.py:201-202` ("Whether a number multiplies or adds is decided by the field's own neutral value"). `is_sentinel` und `is_better_lower` daneben tragen aus demselben Grund keinen. |
| 6 | `explain.py` Docstring von `_without_the_curse` (war Z. 768) | 1 | `nrplanner/advisor/explain.py:789-791` — "scoring the same assignment once more with that one curse taken off", im Docstring des einzigen Aufrufers. |
| 7 | `damage.py` Fuenf-Punkte-Zusammenfassung von AD-020 (war Z. 22-26) | 4 | `ARCHITECTURE.md:770-790` — AD-020, Punkte 1 bis 5, in derselben Reihenfolge. Der Verweis bleibt als Zeile stehen. |

### Zahlen je Datei, gegen die Tabelle des Auftrags

Gemessen mit `scratchpad/T-206/prosecount.py` (`ast` fuer Docstrings,
`tokenize` fuer Kommentare; Prosa = Docstringzeilen plus Zeilen, die mit `#`
beginnen):

| Datei | Auftrag | vorher (mein Zaehler) | nachher | Differenz |
|---|---|---|---|---|
| `nrplanner/model.py` | 584 | **597** (Docstring 152 / Kommentar 445) | 582 | **-15** |
| `nrplanner/advisor/explain.py` | 415 | **445** (413 / 32) | 444 | **-1** |
| `nrplanner/damage.py` | 369 | **385** (278 / 107) | 381 | **-4** |
| zusammen | 1368 | **1427** | 1407 | **-20 (1,4 %)** |

**Mein Zaehler weicht vom Auftrag ab, und zwar nur bei den Docstrings.** Die
Kommentarzahlen stimmen auf die Zeile (445 / 32 / 107). Die Docstringzahlen
liegen um +13 / +30 / +16 hoeher. Ursache nicht aufgeklaert: Leerzeilen
innerhalb von Docstrings abzuziehen ergibt 132 / 352 / 241 und trifft es
auch nicht. Wer die Hochrechnung des Audits gegen meine Zahl haelt, muss
denselben Zaehler benutzen — das Skript liegt im Scratchpad und ist zehn
Zeilen lang.

### Das Kommando, mit dem "nur Prosa im Diff" belegt ist

`scratchpad/T-206/onlyprose.py`, zwei unabhaengige Pruefungen:

1. **AST-Gleichheit nach Entfernen aller Docstrings.** `git show HEAD~1:<datei>`
   gegen die Arbeitsfassung, beide geparst, alle Docstrings aus dem Baum
   entfernt, `ast.dump` verglichen. Aendert sich eine Codezeile, unterscheidet
   sich der Baum.
2. **Zeilenweise Einordnung.** `git diff -U0 -- <datei>`, und fuer jede
   geaenderte Zeile geprueft, ob ihre Nummer in der Docstring-Spanne oder in
   der Kommentarmenge der jeweiligen Fassung liegt.

Ausgabe:

```
(1) nrplanner/model.py: AST ohne Docstrings identisch: True
(2) nrplanner/model.py: Codezeilen im Diff: 0
(1) nrplanner/advisor/explain.py: AST ohne Docstrings identisch: True
(2) nrplanner/advisor/explain.py: Codezeilen im Diff: 0
(1) nrplanner/damage.py: AST ohne Docstrings identisch: True
(2) nrplanner/damage.py: Codezeilen im Diff: 0
ERGEBNIS: nur Prosa
```

**Positivkontrolle, damit das nicht nur mein Pruefmittel misst.** In
`damage.py:143` `return math.floor(figure)` durch `return int(figure)`
ersetzt (Datei vorher mit `cp` zur Seite gelegt, danach zurueckkopiert — kein
`git checkout`). Beide Pruefungen schlagen an:

```
(1) nrplanner/damage.py: AST ohne Docstrings identisch: False
(2) nrplanner/damage.py: Codezeilen im Diff: 2
     -147:     return math.floor(figure)
     +143:     return int(figure)
ERGEBNIS: ABBRUCHGRUND   (exit 1)
```

Danach zurueckkopiert und erneut geprueft: `ERGEBNIS: nur Prosa`.

### Suitezahl

```
python -m pytest -n auto -q
1781 passed, 9 skipped in 131.10s (0:02:11)
```

Identisch zum Ausgangswert des Auftrags (`1781 passed, 9 skipped`). QA-238
(`tests/test_advisor_worker.py:360`) ist in diesem Lauf nicht geflackert.
Datenbedingung: Programm nicht gestartet, keine Umlenkung gesetzt, weil
nichts geschrieben wurde — die Suite lief ohne Fensterlauf durch.

**Nebenbefund zum Testbefehl:** meine eigene Notiz sagte, `-n auto` gehe auf
dieser Maschine nicht (`pytest-xdist` fehle) und zwei `--ignore` seien
noetig (`texture2ddecoder` fehle). Beides ist heute falsch: `xdist 3.8.0` und
`texture2ddecoder` sind installiert, der Volllauf braucht 131 s statt 7-10
min. Ich habe die Notiz korrigiert.

## Prueft ein Test eine dieser Docstrings? — geprueft, nicht angenommen

Suchkommandos, in dieser Reihenfolge:

```
grep -rn --include=*.py "__doc__" tests/ scripts/ nrplanner/ nrdata/
grep -rn --include=*.py "getsource|inspect\.|get_docstring|getcomments" tests/ scripts/ nrplanner/ nrdata/
grep -rn --include=*.py "model\.py|damage\.py|explain\.py" tests/ scripts/
grep -rln --include=*.py "read_text|ast.parse|tokenize" tests/ scripts/
```

und zuletzt, als mechanismus-gebundene Gegenprobe (L-003), je geloeschtem
Block eine Volltextsuche nach einem Satzstueck daraus ueber `*.py`, `*.md`,
`*.spec`, `*.txt`, `*.json` des ganzen Baums:

```
grep -rn "bucket of their own" .            -> 1 Treffer (die Stelle selbst)
grep -rn "less accurate of the two" .       -> 1
grep -rn "nobody was warned about" .        -> 1
grep -rn "feed back into the curve" .       -> 1
grep -rn "Does this field scale" .          -> 1
grep -rn "one curse taken off" .            -> 2 (Stelle selbst + explain.py:790)
grep -rn "the questions, not the drift" .   -> 1
```

Kein geloeschter Block wird ausserhalb seiner eigenen Datei zitiert.

**Was die Suche dagegen gefunden hat — und was ich deshalb nicht angefasst
habe:**

1. **`scripts/differential/mutate.py` verankert 34 Mutationen woertlich in
   diesen drei Dateien**, und einer dieser Anker enthaelt Prosa:
   `mutate.py:175-183` (`move-scope-constant-emptied`) zitiert den ganzen
   Block `MOVE_SCOPED_EFFECT_IDS = frozenset({...})` **einschliesslich seiner
   vier nachgestellten Kommentare** (`# Thrusting Counter.`, `# Sorceries`,
   `# Incantations`, `# both at once`). Wer diese vier Kommentare kuerzt,
   macht die Mutation unauffindbar, und der Mutationslauf meldet das nicht als
   Fehler, sondern gar nichts. Die uebrigen 33 Anker sind reiner Code
   (geprueft mit einem `ast`-Durchlauf ueber alle `Mutation(...)`-Aufrufe,
   Filter auf `path`, Ausgabe von `old`).
2. **`tests/test_advisor_explain.py:1475-1498`** liest den **Volltext** jeder
   Datei unter `nrplanner/advisor/` — Kommentare und Docstrings eingeschlossen
   — und verbietet vier Saetze ("Chosen for", "carry no numbers", "carries no
   numbers", "counted for nothing:"). Loeschen kann den nie brechen,
   *Formulieren* schon: neue Prosa in `advisor/` darf diese vier nicht
   enthalten.
3. **`tests/test_interface_language.py`, `test_one_dash_style.py`,
   `test_one_name_per_figure.py`** lesen die Quelltexte, nehmen Docstrings
   aber ausdruecklich aus und sehen Kommentare (keine String-Knoten) ohnehin
   nicht.

## Haette ich gekuerzt, habe es nicht

Die Regel sagt: im Zweifel stehen lassen und hier nennen. Elf Faelle, nach
Groesse:

| Ort | Was | Warum stehen geblieben |
|---|---|---|
| `damage.py:502-505` | "A buff tied to a weapon *class* covers only that class … a buff merely *gated* on a weapon type is not restricted at all" — steht so auch in `model.py:1023-1026` und als AD-020 Punkt 4 | **Die Richtung des Belegs ist umgekehrt:** AD-020 Punkt 4 nennt diesen Kommentar als seine Quelle ("AD-005-Kommentar, unveraendert gueltig", `ARCHITECTURE.md:783-784`). Das Dokument ist hier nicht die Ersatzstelle, sondern das Abgeleitete. Loeschen wuerde das Zitat ins Leere zeigen lassen. |
| `damage.py:621-627` | "There used to be a `require_usable` flag here …", reine Verlaufsprosa ueber etwas, das es nicht mehr gibt (7 Zeilen) | Traegt **QA-061**, **T-034** und eine Messung (1791 von 1793). Bleibt ohne Ermessen. Der grosse Einzelposten, wenn der Nutzer die Regel lockern will. |
| `model.py:903-905` | Der Kommentar "Weapon-type gates are met by any armament being held, not just the one being broken down" wiederholt `model.py:581-583` | Wiederholung **an der Verwendungsstelle** ist der Fall, in dem eine Doppelung nuetzlich ist. Ausserdem traegt der dritte Satz einen Grund, der nirgends sonst steht ("so older callers keep working"). |
| `model.py:881-884` | Der `compute()`-Docstring nennt die Zaehlregeln ("Additive attribute bonuses sum; '*Rate' fields multiply", `isStrongestEffect`) noch einmal, die der Code in `model.py:931-937` ausfuehrt | Das ist der **oeffentliche Vertrag** der einzigen Einstiegsfunktion des Moduls, nicht ein Nachsprechen. Wer ihn kuerzt, verlagert die Frage in den Rumpf. |
| `model.py:1029-1031` | "A scope that names a kind of armament rather than a kind of attack …" — dieselbe Unterscheidung in `scoped_class` (`model.py:409-417`) und im Kommentar zu `WEAPON_CLASS_SCOPES` (`model.py:390-399`) | Dritte Nennung derselben Unterscheidung, aber an der Stelle, wo sie eine Verzweigung erklaert. Grenzfall, klar kuerzbar, wenn der Nutzer "auch an der Verwendungsstelle" zulaesst. |
| `model.py:429` | `"""'melee', 'ranged' or 'catalyst' for an armament."""` | Zaehlt den Rueckgabebereich auf, den der Rumpf ueber acht Zeilen verteilt. `None` fehlt darin — beim Kuerzen waere mir das nicht aufgefallen, beim Lesen schon: **kleiner Doku-Fehler, kein Debt**, ich habe ihn nicht behoben (nicht mein Auftrag). |
| `model.py:242` | `"""The value of an additive percentage field, as a percentage."""` | Sieht wie das Lehrbuchbeispiel des Auftrags aus, ist es aber nicht: "additive percentage field" ist eine **Vorbedingung** (nur fuer `PERCENT_FIELDS` gueltig), die in der Signatur nicht steht. |
| `damage.py:308`, `damage.py:315` | `""""AR" or "Spell power" …"""` und `"""The same thing in a sentence …"""` | Sprechen den Rumpf nach — aber die beiden Werte stehen dort als Konstanten (`SPELL_POWER_LABEL`, `ATTACK_RATING_LABEL`), der Docstring spart den Sprung nach `damage.py:102-105`. |
| `damage.py:398` | `"""Damage type -> the figure after the multipliers, the number shown."""` | Sagt, was die zwei Bestandteile des `dict` bedeuten; der Typ `dict[str, float]` sagt es nicht. |
| `explain.py:358-362` | "Same fallback as the model's: with no armament grid given, …" erzaehlt die drei Rumpfzeilen nach | Der erste Halbsatz ist die modulaebergreifende Zusage ("same as the model's"), und die laesst sich nicht kuerzen, ohne den zweiten mitzunehmen. |
| `model.py:8`, `:25`, `:209`, `:678`, `:682`, `:689` | Sechs einzeilige Kopfzeilen ueber Konstanten ("# SpEffect field -> the attribute it adds to.") | Jede nennt **die Herkunft** des Schluessels oder eine Auswahl ("worth surfacing"), die im Literal nicht steht. Zusammen 6 Zeilen — die Ausbeute waere 0,4 % und der Verlust je Zeile groesser als der Gewinn. |

## Hochrechnung auf die restlichen siebzehn Dateien

**Ausbeute hier: 20 von 1427 Prosazeilen, 1,4 %.** Sieben Bloecke von 175
(99 + 38 + 38).

Die Verteilung sagt mehr als die Summe. Ich habe alle 175 Prosabloecke
maschinell danach sortiert, ob sie ein Schutzmerkmal der Regel tragen
(`scratchpad/T-206/blocks.py`, Suchmaske `\b(QA|AD|AK|SEC|DR|OF|L|T|R|P|F|W|Z|S)-?\d`
fuer Befundnummern, plus "enthaelt eine Ziffer" fuer Messungen):

| Datei | Bloecke | mit Befundnummer | ohne Nummer, mit Zahl | ohne beides |
|---|---|---|---|---|
| `model.py` | 99 | 9 | 38 | 52 |
| `explain.py` | 38 | 22 | 4 | 12 |
| `damage.py` | 38 | 19 | 6 | 13 |
| zusammen | 175 | 50 (29 %) | 48 (27 %) | **77 (44 %)** |

56 % der Bloecke sind durch "bleibt ohne Ermessen" **vor jedem Urteil**
geschuetzt. Die restlichen 77 habe ich einzeln gelesen; sieben davon waren
kuerzbar, 11 sind oben als Grenzfall genannt, 59 tragen eine Begruendung, eine
Deckenangabe oder eine Nicht-Entscheidung, die nirgends sonst steht.

**Erwartung fuer die siebzehn: 1 bis 3 %, also grob 100 bis 300 Zeilen von
rund 10 000.** Woran sie haengt, in dieser Reihenfolge:

1. **Wie viel Prosa eine Befundnummer traegt.** Bei `explain.py` — der Datei,
   die der Audit als "fast reiner Docstring" fuehrte — waren es 58 % der
   Bloecke, und die Ausbeute war **eine Zeile**. Bei `model.py`, dem
   kommentarlastigen Gegenstueck, 9 %, und dort lagen 15 der 20 Zeilen. Die
   Faustregel ist damit: **je aelter und berater-naeher die Datei, desto
   geringer die Ausbeute.** `advisor/*` und alles, was nach AD-025 entstanden
   ist, traegt fast nur numerierte Prosa.
2. **Ob Doppelungen innerhalb derselben Datei zaehlen.** Zwei der sieben
   Kuerzungen haengen daran (Annahme 1 oben). Sagt der Nutzer nein, sinkt die
   Ausbeute hier auf 11 Zeilen.
3. **Ob Verlaufsprosa mit Befundnummer kuerzbar wird.** Das ist der einzige
   Hebel, der die Groessenordnung aendern koennte: die laengsten Bloecke der
   drei Dateien sind Historie mit QA-Nummer (`damage.py:621-627`,
   `damage.py:355-379`, `model.py:224-236`). Sie fallen heute unter "bleibt
   woertlich". Waere das anders, lieferten allein die drei Dateien gut 60
   Zeilen statt 20 — und der Preis waere, dass die Begruendung, warum eine
   Messung nicht wiederholt werden muss, nur noch im `git log` steht.

### Empfehlung: **die Kuerzung fuer die restlichen siebzehn Dateien nicht durchfuehren.**

Drei Gruende, der dritte ist der, den ich vorher nicht erwartet habe:

1. **Der Ertrag steht in keinem Verhaeltnis zum Leseaufwand.** Die 20 Zeilen
   haben einen vollen Lesedurchgang durch 2848 Zeilen gekostet, plus die
   Pruefung von 34 Mutationsankern und vier Waechtern. Auf siebzehn Dateien
   sind das sieben bis zehn Auftraege dieser Groesse fuer 1 bis 3 % Prosa.
   Der Audit hat die Prosadichte als groessten Posten gefuehrt; **kuerzbar ist
   davon der kleinste Teil.** Die Zahl war gezaehlt und nicht gelesen, und
   das Lesen widerlegt sie: 11 402 Prosazeilen heisst nicht 11 402 kuerzbare
   Zeilen, sondern rund 150 bis 350.
2. **Die Prosa dieses Projekts traegt.** Das ist das eigentliche Ergebnis des
   Piloten. Von 175 Bloecken waren sieben redundant, und **einer von den
   sieben war verwaist** (der Krit-Block), also ein Umzugsschaden und kein
   Stilproblem. Kein einziger Block sagte etwas Falsches.
3. **Prosa loeschen verschiebt Zeilennummern, und dieses Projekt zitiert
   Zeilennummern.** Sechs Zitate zeigen in die drei Dateien:
   `tests/test_weapon_tile_and_panel_agree.py:176` (`model.py:739-742`), `:178`
   (`damage.py:376-391`), `:179` (`damage.py:326`), `ARCHITECTURE.md:560`
   (`damage.py:140`), `UI_SPEC.md:3371-3372` (`model.py:889`, `model.py:1058`).
   **Alle sechs waren schon vor meiner Aenderung falsch** — mit
   `git show HEAD~1:<datei> | sed -n '<zeile>p'` nachgeprueft: `model.py:739-742`
   zeigte in `swap_deltas`, `damage.py:326` und `376-391` mitten in Docstrings,
   `damage.py:140` in den `displayed()`-Docstring. Meine Kuerzung verschiebt
   sie um weitere 4 bis 15 Zeilen. Eine Kuerzungsrunde ueber siebzehn Dateien
   macht jedes solche Zitat im Repo unbrauchbar, und niemand merkt es, weil
   kein Test sie prueft.

Wenn der Nutzer es dennoch will: dann **nicht nach Prosadichte auswaehlen,
sondern nach Alter.** Die einzige Stelle, an der der Pilot etwas Kaputtes
gefunden hat, war ein Block, der bei einem frueheren Umbau seinen Bezug
verloren hat. Ein Auftrag "finde verwaiste Kommentarbloecke" — Prosa, die von
einem Bezeichner spricht, der nicht in ihrer Naehe definiert ist — waere
billiger zu pruefen und haette denselben Fund gebracht, ohne 1400 Zeilen
Urteil.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (zwei, im Kopfblock)
- [x] Build & Tests gruen: `python -m pytest -n auto -q` → `1781 passed, 9 skipped in 131.10s`, gleich dem Ausgangswert. Zielsystem Windows 11 x64, wie im Auftrag.
- [x] Neue Tests: **keine, und das ist richtig** — es ist keine Logik entstanden. Statt eines Tests liegt der Nachweis im Pruefskript mit Positivkontrolle (oben).
- [x] Linter: **entfaellt** — das Projekt hat keinen konfiguriert (weder `setup.cfg`, `.flake8`, `ruff.toml`, `pyproject.toml`, `.pylintrc` noch `tox.ini` vorhanden; `pytest.ini` enthaelt nur `testpaths` und `markers`).
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Nicht geprueft: Linux und macOS (nie Ziel), und kein Fensterlauf — beides fuer eine Prosaaenderung ohne Aussage.
- [x] Bericht geschrieben

## An den director

**Befunde, alle ausserhalb meines Auftrags, keiner behoben:**

1. **Sechs Zeilennummern-Zitate in die drei Dateien waren bereits vor meiner
   Aenderung falsch** (Belege oben, Punkt 3 der Empfehlung). Art: Doku-Debt.
   Risiko: gering, aber sie kosten jeden Leser, der ihnen folgt, einen
   Fehlschluss — `tests/test_weapon_tile_and_panel_agree.py:176` belegt mit
   `model.py:739-742` eine Aussage ueber Waffentyp-Gates, und dort steht
   Kurven-Interpolation. Aufwand: klein je Stelle, aber die Zitate stehen in
   `tests/`, `ARCHITECTURE.md` und `UI_SPEC.md` und damit in drei fremden
   Zustaendigkeiten. **Empfehlung: keine Reparatur, sondern die Praxis
   aufgeben** — auf Bezeichner verweisen statt auf Zeilen. Das ist eine
   Entscheidung des Nutzers, nicht meine.
2. **`scripts/differential/mutate.py:175-183` verankert eine Mutation in vier
   Kommentaren** (Details oben). Art: stiller Kopplungspunkt. Risiko: mittel —
   ein Kuerzungslauf, der die vier Zeilen mitnimmt, entwaffnet
   `move-scope-constant-emptied`, ohne rot zu werden. Aufwand: klein, wenn der
   Anker auf die erste und letzte Codezeile verkuerzt wird. Falls Korb 1
   fortgesetzt wird, gehoert das **davor**.
3. **AD-020 Punkt 4 zitiert einen Code-Kommentar als seine Quelle**
   (`ARCHITECTURE.md:783-784` → `damage.py:502-505`). Das ist kein Fehler,
   aber es widerlegt die Annahme des Audits, ARCHITECTURE.md sei generell die
   Ersatzstelle fuer Code-Prosa. An dieser Stelle ist es umgekehrt. Wer weiter
   kuerzt, muss die Richtung je Fall pruefen.
4. **Kein Performance-Fund, kein Sicherheitsfund.** Beides geprueft, weil ich
   die drei Dateien vollstaendig gelesen habe; nichts zu melden.

**Widerspruch zum Auftrag — einer, klein:** Der Auftrag verlangt "jede Zeile
mit AD-Nummer bleibt woertlich" und gleichzeitig "traegt ein Docstring eine
Begruendung, die unter ihrer AD-Nummer steht, bleibt der Verweis und der
Wortlaut geht". Bei `damage.py:22` treffen beide auf **dieselbe Zeile** zu.
Ich habe sie zugunsten der zweiten Regel aufgeloest (Nummer steht, Wortlaut
weg) und das als Annahme 2 verbucht. Wenn der Nutzer die erste Regel
strenger meint, ist Kuerzung 7 zurueckzunehmen, und die Ausbeute sinkt auf
16 Zeilen.

## An qa-engineer

Es gibt hier nichts zu testen — kein Verhalten hat sich geaendert, belegt
durch AST-Gleichheit ohne Docstrings und durch die unveraenderte Suitezahl.
Zwei Dinge sind aber pruefbar, falls du den Piloten abnehmen sollst:

- **Der Beleg selbst.** `python scratchpad/T-206/onlyprose.py` (Skript liegt
  im Scratchpad, nicht im Repo — wenn es bleiben soll, sag es, ich lege es
  ab). Seine Positivkontrolle ist oben dokumentiert; wiederhol sie ruhig mit
  einer anderen Codezeile.
- **Die Ersatzstellen.** Sieben Stueck, in der Tabelle unter "Umgesetzt" mit
  Datei und Zeile. Der Fall, der am ehesten strittig ist, ist Nr. 7
  (`damage.py` gegen AD-020): dort ist die Ersatzstelle ein 6513 Zeilen langes
  deutsches Dokument, waehrend der geloeschte Text englisch und drei Zeilen
  lang war. Wenn dein Urteil "der Leser von `damage.py` findet das nicht
  mehr" lautet, ist das ein Befund und kein Missverstaendnis.

Edge case, den ich nicht abdecken kann: ob ein Leser, der `model.py` zum
ersten Mal oeffnet, `is_multiplier` ohne Docstring noch versteht. Das ist
Leseurteil, kein Testfall.

## An ui-ux-designer

Keine Abweichung, keine Beruehrung. Kein Anzeigetext geaendert (die Suite
haelt das ueber `tests/test_interface_language.py` selbst fest).
