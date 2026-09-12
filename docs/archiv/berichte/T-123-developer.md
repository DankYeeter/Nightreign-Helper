# T-123 - Zwei Waechter: A8 (Englisch) und A3 (Vollstaendigkeit) (developer)

```
STATUS: erledigt
AUFTRAG: T-123 - Zwei Waechter: A8 (Englisch) und A3 (Vollstaendigkeit)
GELESEN: docs/tasks/T-123.md, docs/berichte/T-114-qa-engineer.md,
  ~/.claude/agents/_rahmen.md, CLAUDE.md, pytest.ini,
  tests/{conftest,advisor_cases,relics,tabtext,rendered}.py,
  tests/test_advisor_run.py, tests/test_weapon_damage_golden.py (Kopf),
  nrplanner/{advisorbar,app,model,chalices,firstrun}.py,
  nrplanner/advisor/{run,candidates,types,goals}.py, nrdata/extract.py
  (Kelch- und Heldenabschnitt)
GEAENDERT: tests/test_interface_language.py (neu, committet),
  tests/test_advisor_covers_every_chalice.py (neu, committet),
  docs/berichte/T-123-developer.md (diese Datei).
  Commits 4d1955d (die zwei Waechter) und ad291e6 (Wortliste alphabetisch
  geordnet, keine inhaltliche Aenderung), beide Male die Pfade einzeln
  hinter `--`.
  Waehrend der Mutationslaeufe voruebergehend geaendert und per Kopie
  zurueckgeholt: nrplanner/advisor/candidates.py, nrplanner/firstrun.py,
  nrplanner/app.py, tests/test_interface_language.py. Alle vier stehen
  wieder auf HEAD (`git diff --stat -- nrplanner nrdata tests run.py` leer,
  Ausgabe unten).
ANNAHMEN: siehe Abschnitt "Annahmen" - drei, alle im Test niedergeschrieben.
NAECHSTER: director
BLOCKIERT DURCH: nichts.
```

---

## Umgesetzt

Zwei neue Dateien, beide ausschliesslich unter `tests/`, kein
Anwendungscode, keine Doku ausser diesem Bericht.

### `tests/test_interface_language.py` (QA-204, A8) - 4 Faelle

| Fall | was er behauptet |
|---|---|
| `test_the_mask_notices_german_when_it_meets_it` | Positivkontrolle: die Maske schlaegt bei drei deutschen Saetzen an (darunter T-114s `Die Datei kann nicht gelesen werden`) und bei fuenf englischen nicht |
| `test_the_games_own_words_cannot_trip_the_mask` | die Trennung Spieldaten/Oberflaeche, **gemessen** statt behauptet: kein Wort der Maske und kein deutscher Buchstabe kommt irgendwo im Datensatz vor - Schluessel wie Werte |
| `test_no_sentence_this_program_can_author_is_german` | jede Zeichenkette der ausgelieferten Python-Dateien ausser Docstrings: **5 258 Zeichenketten in 63 Dateien**, 0 Treffer |
| `test_what_the_window_puts_on_screen_is_english` | der Text, den ein gebautes `Planner`-Fenster wirklich traegt: **16 249 Textstuecke**, 0 Treffer |

### `tests/test_advisor_covers_every_chalice.py` (QA-205, A3) - 3 Faelle

| Fall | was er behauptet |
|---|---|
| `test_every_nightfarer_and_chalice_is_answered_in_full` | A3 fuer die drei gewoehnlichen Slots ueber **alle 110 Nightfarer/Kelch-Paare**, beide Zielrichtungen = 220 Laeufe |
| `..._in_deep_of_night` | dasselbe fuer die sechs Slots, die Deep of Night oeffnet = weitere 220 Laeufe |
| `test_the_layout_this_file_builds_is_the_one_the_window_asks_about` | die Frage, die der Sweep stellt, ist die Frage des Fensters: `layout_of(vessel, deep).slots` == `advisorbar.asking_from(...).request.problem.slots`, mit Deep aus und an |

Geprueft wird je Paar: es kommt eine Antwort, sie traegt **zwei
verschiedene benannte** Zielrichtungen, **jeder** freie Slot ist besetzt,
und jede benannte Kopie ist eine, die der Spieler haelt - in Farbe und
Deep-Eigenschaft passend zum Slot.

---

## Die uebernommene Methode aus T-114, und was daran zu aendern war

**Uebernommen:** T-114 hat A8 nicht als "ist es ASCII" geprueft, sondern als
"steht hier Deutsch" - eine Maske ueber die Zeichenketten des verpackten
Codes (4 806 Stueck, 1 Treffer, ein englischer Docstring) plus die zur
Laufzeit erzeugten Texte, mit einer Positivkontrolle an
`Die Datei kann nicht gelesen werden`. Genau diese drei Bestandteile stehen
jetzt im Test: Zeichenkettensuche, Lauf-Text, Positivkontrolle.

**Was geaendert werden musste, damit es als Test taugt:**

1. **Quelle statt Artefakt.** T-114 hat aus der EXE ausgepackt. Ein Test darf
   keinen Bau voraussetzen, also liest der Waechter die Quelldateien - mit
   `ast`, nicht mit einem regulaeren Ausdruck. Das ist kein Rueckschritt,
   sondern noetig: nur `ast` unterscheidet einen **Docstring** von einem Satz
   (T-114s einziger Treffer war genau so einer und musste von Hand als
   harmlos eingestuft werden). Der Waechter zaehlt Docstrings gar nicht erst
   mit, deshalb 0 Treffer statt 1.
2. **Die Maske ist ausgeschrieben.** T-114 nennt sie nicht; ihre
   Positivkontrolle nennt sie. Sie steht jetzt als
   `GERMAN_FUNCTION_WORDS` (85 Woerter) plus `GERMAN_LETTERS` im Test, mit
   der Begruendung, welche Woerter **absichtlich fehlen**: `die`, `war`,
   `man`, `hat`, `am`, `was` sind gewoehnliche englische Woerter. Ohne diese
   Streichung wird der Waechter zum Wolfsrufer - der erste Entwurf schlug an
   `Two reward orbs ... War` in `nrplanner/eventlore.py:196` an.
3. **Statt der 545 Beratertexte das ganze Fenster.** T-114 konnte den Berater
   am Artefakt laufen lassen; im Test waere das ein zweiter 30-s-Sweep neben
   dem A3-Waechter. Der zweite Zugang ist deshalb breiter und billiger: der
   Text, den ein gebautes Fenster traegt, ueber alle sieben Registerkarten
   (0,7 s). Die Beratersaetze sind dabei ueber die Zeichenkettensuche
   gedeckt - sie werden aus Literalen in `advisor/explain.py` gebaut.

---

## Wie Spieldaten von Oberflaechentext getrennt sind

Der Auftrag verlangt eine Antwort darauf; es sind zwei verschiedene, eine je
Haelfte:

- **Zeichenkettensuche:** die Trennung ist strukturell. Ein Literal im
  Quelltext ist per Konstruktion nie ein Name aus `regulation.bin` - die
  Spieldaten kommen zur Laufzeit aus dem Schnappschuss und stehen nirgends im
  Code. Der Waechter kann an ihnen gar nicht rot werden.
- **Fenstertext:** hier stehen Spielnamen und eigene Saetze nebeneinander.
  Statt die Spielnamen **herauszufiltern** - ein Filter, der an nichts
  ausloest, ist ein Filter, dem niemand trauen kann - wird die Trennung
  **gemessen**: `test_the_games_own_words_cannot_trip_the_mask` geht jede
  Zeichenkette des Datensatzes durch, Schluessel wie Werte, und findet **0**
  Woerter der Maske und **0** deutsche Buchstaben. Ein Treffer im Fenster ist
  also dieses Programms Text, egal woraus er zusammengesetzt wurde. Bringt
  ein Spielpatch je eine Kollision, sagt genau dieser Fall es, und die
  Antwort ist, die Maske zu verengen - nie, dem Fenster-Waechter mehr
  durchgehen zu lassen.

## Was die Maske faengt und was sie durchlaesst

**Faengt:** Deutsch, das als Deutsch geschrieben ist - 85 Funktionswoerter
als ganze Woerter, Gross-/Kleinschreibung egal (`(?<![A-Za-z])wort(?![A-Za-z])`,
damit `under` nicht als `der` und `submit` nicht als `mit` gelesen wird), und
die Buchstaben `ÄÖÜäöüß`. Die Umschreibungen des Projekts (`fuer`, `ueber`,
`waehrend`, `koennen`, `muessen`, `duerfen`) stehen deshalb zusaetzlich in
der Wortliste.

**Laesst durch, ausdruecklich:** ein einzelnes deutsches Substantiv ohne
Funktionswort und ohne Umlaut (`Fehler`, `Kelch`); jede andere Fremdsprache,
die ohne diese Buchstaben auskommt; eine absichtliche Umschreibung, die
beiden Listen ausweicht. Der Waechter ist gegen den Satz gerichtet, der
hineinrutscht, nicht ein Beweis fuer Englisch.

**Ebenfalls nicht gedeckt** (steht so im Modul-Docstring): Docstrings und
Kommentare, Text den Qt selbst liefert (Standarddialog-Knoepfe sind
uebersetzt, nicht von uns), und Fenstertext, der erst nach einer Aktion
erscheint, die der Test nicht ausfuehrt - letzteres sieht die
Zeichenkettensuche trotzdem.

---

## Toetende Mutationen (L-008)

Jede Mutation wurde vor der Aenderung mit `cp datei datei.orig` in den
Scratchpad `T-123/` gesichert und danach zurueckkopiert; **kein**
`git checkout --`. Nach jeder Rueckkopie geprueft.

### M1 - A3-Waechter, Achse "Nightfarer"

`nrplanner/advisor/candidates.py:293`

```python
-    offered = inventory.relics_for(slot.colour, slot.deep)
+    offered = () if ctx.hero["id"] == 7 else inventory.relics_for(slot.colour, slot.deep)
```

Held 7 ist Recluse - einer der sechs Nightfarer, die T-114 in **keinem**
Beratertest gefunden hat.

```
E  Recluse / Recluse's Chalice / Deep of Night: max_damage left slots [0, 1, 2, 3, 4, 5] empty and answered for []
   ... (44 Zeilen dieser Art, alle Recluse)
tests\test_advisor_covers_every_chalice.py:242: AssertionError
FAILED tests/test_advisor_covers_every_chalice.py::test_every_nightfarer_and_chalice_is_answered_in_full
FAILED tests/test_advisor_covers_every_chalice.py::test_every_nightfarer_and_chalice_is_answered_in_full_in_deep_of_night
2 failed, 1 passed in 47.91s
```

**Und der Beleg, dass der Waechter eine echte Luecke schliesst:** dieselbe
Mutation gegen die **ganze uebrige Suite**:

```
pytest -q -n auto --ignore=tests/test_advisor_covers_every_chalice.py
1261 passed, 9 skipped in 159.19s
```

Der Berater schlaegt fuer Recluse in keinem Kelch mehr irgendetwas vor, und
1261 Tests bleiben gruen. Das ist QA-205 als Zahl.

### M2 - A8-Waechter, Haelfte "Quelltext"

`nrplanner/firstrun.py:169`

```python
-            else "Refreshing your game data"
+            else "Deine Spieldaten werden neu gelesen"
```

```
E  AssertionError: 1 of 5258 strings in 63 shipped files read as German:
E    nrplanner/firstrun.py:169: ['werden'] in 'Deine Spieldaten werden neu gelesen'
FAILED tests/test_interface_language.py::test_no_sentence_this_program_can_author_is_german
1 failed, 3 passed in 16.23s
```

**Ganze uebrige Suite unter derselben Mutation:**

```
pytest -q -n auto --ignore=tests/test_interface_language.py
1260 passed, 9 skipped in 205.07s
```

Ein deutscher Satz in einer Fenster-Ueberschrift, und die Suite ohne diesen
Waechter bleibt vollstaendig gruen. Das ist QA-204 als Zahl.

### M3 - A8-Waechter, Haelfte "Fenster" (und der Beleg, dass die zwei Haelften nicht dasselbe tun)

`nrplanner/app.py:1467`

```python
-            f"Nightreign Helper {__version__}"
+            f"Nightreign Helper {__version__} " + "".join(("nic", "ht"))
```

Absichtlich zur Laufzeit zusammengesetzt: die Literale `"nic"` und `"ht"`
sind fuer die Maske unauffaellig.

```
E  AssertionError: 1 of 16249 pieces of text the window carries read as German:
E    ['nicht'] in 'Nightreign Helper 1.8.0 nicht'
FAILED tests/test_interface_language.py::test_what_the_window_puts_on_screen_is_english
1 failed, 3 passed in 16.63s
```

Die Quelltext-Haelfte bleibt dabei **gruen**. Damit ist belegt, dass die
zweite Haelfte nicht bloss Beiwerk ist: sie faengt genau die Klasse, die der
Zeichenkettensuche entgeht.

### M4 - die gemessene Trennung von den Spieldaten

`tests/test_interface_language.py`, `GERMAN_FUNCTION_WORDS` um `"flame"`
erweitert - ein Wort, das der Datensatz benutzt:

```
E  ['Flame'] in 'Flame of Frenzy'
E  ['Flame'] in 'Improved Frenzied Flame Incantations'  ... 
FAILED tests/test_interface_language.py::test_the_games_own_words_cannot_trip_the_mask
FAILED ...::test_no_sentence_this_program_can_author_is_german
FAILED ...::test_what_the_window_puts_on_screen_is_english
3 failed, 1 passed in 16.52s
```

Der Trennungsfall schlaegt an, sobald die Maske ein Wort des Spiels
beansprucht - und zwar **bevor** man den Fehler an einem Relikt-Namen suchen
muss.

### M5 - die Positivkontrolle

`tests/test_interface_language.py`, `german_in()` auf `return []` gesetzt -
die blinde Maske.

```
E  AssertionError: the mask slept through 'Die Datei kann nicht gelesen werden'
FAILED tests/test_interface_language.py::test_the_mask_notices_german_when_it_meets_it
1 failed, 3 passed in 13.06s
```

Die drei anderen bleiben gruen - genau der Grund, warum es die
Positivkontrolle gibt: ohne sie waere eine blinde Maske ein gruener Waechter.

### M6 - A3-Waechter, Achse "Kelch-Layout"

`nrplanner/advisor/candidates.py:293`

```python
-    offered = inventory.relics_for(slot.colour, slot.deep)
+    offered = () if slot.colour == model.WHITE_SLOT else inventory.relics_for(slot.colour, slot.deep)
```

```
E  Wylder / Wylder's Chalice / Deep of Night: max_damage left slots [2] empty and answered for [0, 1, 3, 4, 5]
   ... (Wylder, Guardian, Scholar, Undertaker u. a. - nur die Layouts mit weissem Slot)
2 failed, 1 passed in 41.55s
```

Der Waechter beisst also auf **beiden** Achsen der A3-Zusage, nicht nur auf
der Heldenachse.

**Ueberlebt hat keine der sechs Mutationen.** Nicht gemessen: was die uebrige
Suite zu M3, M4, M5 und M6 sagt (nur zu M1 und M2 gemessen, siehe oben) -
das ist eine Luecke im Beleg, kein Beleg.

### L-008 Bedingung (b): woher die Erwartungen kommen

- Heldenliste, Kelchliste, Slot-Farben, Anzahl der Slots: aus
  `game_data["heroes"]` / `["vessels"]` - dem Datensatz, nicht dem Berater.
- Welcher `hero_type` "allen gemeinsam" heisst: aus den Daten abgeleitet (der
  eine Typ, den keine Held-Id beansprucht), **nicht** aus
  `app.GRAIL_HERO_TYPE` importiert.
- Wieviele Kopien je Farbe noetig sind: `max(len(vessel["slots"]))` - aus den
  Kelchen abgeleitet, keine 3 im Code.
- Die Farbregel: `model.WHITE_SLOT` und die Farbe der gebauten Kopie, nicht
  das, was der Berater darueber sagt.
- Die Relikte: im Test gebaut, ueber `handle` wiedererkannt.
- Die Zielrichtungen: es wird **nicht** `result.goal_label ==
  goals.GOALS[id].label` geprueft (das waere die bewachte Stelle), sondern
  dass zwei **verschiedene**, nicht leere Namen zurueckkommen.
- Die Sprachmaske: von Hand geschrieben, ihre Beispielsaetze ebenfalls -
  nichts davon stammt aus dem Programm.

---

## Messungen (Windows 10, `.venv`, Schnappschuss `extract_version` 11, `data_version` 10350000)

**Suitezahl gegen die Vorgabe 1257 passed / 9 skipped / 0 failed:**

| Lauf | Ergebnis |
|---|---|
| `pytest -q -n auto` **mit** den zwei neuen Dateien | **1264 passed, 9 skipped, 0 failed** in 153,24 s |
| `pytest -q -n auto` mit `--ignore` auf beide neuen Dateien, gleiche Maschine, gleiche Sitzung | **1257 passed, 9 skipped, 0 failed** in 163,21 s |

Die zweite Zeile trifft die Vorgabe auf den Test genau; die erste ist sie
plus die 7 neuen Faelle (3 + 4). **Die Wandzeit steigt nicht messbar** - der
Lauf mit den Waechtern war sogar 10 s schneller als der ohne. Die Streuung
zwischen zwei Laeufen derselben Suite betraegt auf dieser Maschine 153-205 s
(vier volle Laeufe heute), gegen 127 s in `CLAUDE.md` und 180,81 s in T-114:
**jede Aussage "der Waechter kostet X Sekunden Wandzeit" waere unter dieser
Streuung nicht belegbar**, deshalb steht hier der Paarvergleich statt einer
Differenz.

**Einzeln, ohne `-n` (was die Gegenproben-Regel verlangt):**

| Datei / Fall | Zeit |
|---|---|
| `tests/test_advisor_covers_every_chalice.py` gesamt | 46,89 s |
| &nbsp;&nbsp;`..._in_deep_of_night` (220 Laeufe, 6 Slots) | 26,99 s |
| &nbsp;&nbsp;`..._answered_in_full` (220 Laeufe, 3 Slots) | 5,32 s |
| &nbsp;&nbsp;`equipment`-Fixture (10 Inventare + 10 Referenzwaffen) | 4,95 s |
| &nbsp;&nbsp;`shared_planner` fuer den Fenster-Abgleich | 8,56 s |
| `tests/test_interface_language.py` gesamt | 16,05 s |
| &nbsp;&nbsp;`shared_planner` | 8,61 s |
| &nbsp;&nbsp;Spieldaten-Trennung | 3,59 s |
| &nbsp;&nbsp;Zeichenkettensuche (5 258 Literale, 63 Dateien) | 1,49 s |
| &nbsp;&nbsp;Fenstertext (16 249 Stuecke) | 0,71 s |

**Zur 30-s-Schranke des Auftrags:** der teuerste **Einzelfall** liegt mit
26,99 s darunter. Die A3-Datei als ganze liegt mit 46,9 s darueber, und das
ist eine bewusste Wahl, die ich hier begruende: **geschnitten wurde der Fall,
nie die Zusage.** Alle 110 Nightfarer/Kelch-Paare, beide Zielrichtungen,
beide Layouts - 440 Antworten - werden gestellt; klein gemacht wurde nur der
Relikt-Vorrat (drei Kopien je Farbe, gewoehnlich und Deep, statt der 309
echten). Der Grund ist gemessen: T-114 brauchte gegen die 309 echten Relikte
**3,5 s Median fuer einen einzigen Lauf**; 440 davon waeren rund 25 Minuten.
Die Aufteilung in zwei Faelle statt einem ist ebenfalls Absicht - so kann
`-n auto` die 27 s und die 5 s auf zwei Arbeiter legen.

Die Zahl 3 im Vorrat ist **nicht** verdrahtet: sie ist
`max(len(vessel["slots"]))` ueber die Kelche, also die Zahl, die auch dann
noch reicht, wenn ein Layout drei weisse Slots hat.

**Abgeleitete Zahlen des Datensatzes** (keine davon steht im Test):
10 Nightfarer, 74 Kelche (7 je Held + 4 Grale), 110 Held/Kelch-Paare,
47 verschiedene Layouts - je Held sind alle 11 seiner Kelche verschieden,
deshalb bringt ein Zusammenfassen gleicher Layouts hier nichts (110 statt
110) und wurde nicht gemacht.

---

## Annahmen

1. **"Jedes bekannte Kelch-Layout" = jedes Paar aus Nightfarer und dem Kelch,
   den dieses Fenster ihm anbietet** - seine sieben eigenen plus die vier
   Grale, also 110 Paare, und je Kelch beide Fassungen (3 Slots / 6 Slots in
   Deep of Night). Das ist die Menge, die T-114 gefahren hat (10 x 11 x 2 x 2
   = 440), und sie steht so im Modul-Docstring.
2. **Die Zusage gilt einem Vorrat, der die Slots bedienen kann.** A3 sagt
   "ein konkretes Relikt aus dem Besitz des Spielers" - ein Spieler mit
   leerem Beutel bekommt keinen Vorschlag, und das waere kein Fehler. Der
   Waechter stellt deshalb einen Vorrat bereit, der jeden Slot bedienen
   koennte, und prueft dann, dass auch jeder bedient wird.
3. **Der Geltungsbereich der Sprachpruefung** ist das ausgelieferte Python
   (`nrplanner`, `nrdata`, `run.py`) - nicht `tests/` und nicht `scripts/`,
   die nach Projektregel deutsch sind und die niemand laufen sieht.

---

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (3, oben und im Test)
- [x] Build & Tests gruen in der benannten Umgebung: Windows 10, Arbeitskopie,
      Branch `docs/audit-and-advisor-design`, 1264 passed / 9 skipped / 0 failed
- [x] Neue Tests fuer neue Logik: 7 Faelle, 6 toetende Mutationen belegt
- [ ] **Linter: entfaellt** - das Projekt hat keinen konfiguriert
      (`pytest.ini` enthaelt keine, es gibt keine `.flake8`, `ruff.toml`,
      `setup.cfg` oder `pyproject.toml` im Baum). Das ist keine Luecke und
      keine ungeprueft gemeldete Plattform.
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Keine neue Abhaengigkeit
- [x] Doku aktualisiert: nur dieser Bericht (`GOAL.md`, `docs/state.md`,
      `qa/findings.md`, `ARCHITECTURE.md` gehoeren anderen und wurden nicht
      angefasst)
- [x] Arbeitsbaum nach den Mutationen sauber

**Ungeprueft:** Linux und macOS (kein Ziel). Das gebaute Artefakt - die
Waechter laufen am Quellstand; T-114 hat die Artefaktseite abgedeckt.

---

## Bestandsaussagen des Auftrags - nachgeprueft

| Aussage im Auftrag | mein Befund |
|---|---|
| 71 Python-Dateien unter `tests/`, davon 64 mit `test_`-Praefix | **bestaetigt** vor meiner Aenderung; jetzt 73 bzw. 66 |
| kein Sprachwaechter vorhanden | **bestaetigt**, mit einer zweiten, unabhaengig formulierten Maske: `english\|german\|deutsch\|umlaut\|isascii\|non_ascii\|i18n\|locale\|gettext\|sprache` ueber `tests/*.py` findet ausser meiner neuen Datei nur `test_build_names.py` (Build-Namen, nicht Oberflaeche) |
| kein Vollstaendigkeitstest fuer A3 | **bestaetigt** - und stark belegt: M1 nimmt Recluse jeden Vorschlag, 1261 Tests bleiben gruen |
| Suitestand 1257/9/0 | **bestaetigt**, exakt reproduziert (Lauf mit `--ignore` auf meine zwei Dateien) |
| QA-204/QA-205 offen, kein Commit seit Aufnahme | nicht nachgeprueft (fremde Datei, gelesen genuegt) |

**Widerspruch:** keiner.

---

## Offene Fragen

Keine, die diesen Auftrag blockieren. Eine aus T-114 ist an den `developer`
gerichtet und in T-123 nicht enthalten, deshalb hier nur weitergereicht:
`AdvisorResult.unknowns` blieb in allen 440 Laeufen von T-114 leer. Mein
Sweep prueft dieses Feld nicht und sagt dazu nichts.

---

## An qa-engineer

- **Was neu bewacht ist:** A8 auf zwei Wegen (Quelltext-Literale;
  Fenstertext) und A3 ueber alle 110 Nightfarer/Kelch-Paare. Beide melden
  **alle** Verstoesse eines Laufs auf einmal, nicht nur den ersten - die
  Fehlermeldung nennt Held, Kelch, Layout, Zielrichtung und Slot.
- **Randfaelle, die der A8-Waechter bewusst nicht faengt** und die deshalb
  bei euch bleiben: ein einzelnes deutsches Substantiv ohne Funktionswort
  (`Kelch`), Text von Qt selbst (Standarddialoge auf deutschem Windows),
  und Fenstertext, der erst nach einer Aktion erscheint (Fehlermeldungen
  beim Lesen eines kaputten Spielstands) - letzteres deckt die
  Zeichenkettensuche, aber nicht der Fensterlauf.
- **Randfall, den der A3-Waechter bewusst nicht faengt:** ob der Vorschlag
  der **beste** ist. Er prueft, dass ueberhaupt einer kommt, dass er passt
  und dass er dem Spieler gehoert.
- **Ein Rand, den ihr messen koennt:** der A3-Waechter faehrt einen gemachten
  Vorrat von 24 Kopien. Ein Fehler, der erst bei hunderten Kopien auftritt
  (Budget, Abschneiden der Kandidatenliste), faellt ihm nicht auf. T-114 hat
  das einmal gegen die echten 309 gefahren.

## An ui-ux-designer

Keine Abweichung von einer UI-Vorgabe - dieser Auftrag hat die Oberflaeche
nicht angefasst. Eine Beobachtung, die euch gehoert: `nrplanner/app.py:1467`
setzt den Fenstertitel bei einem veralteten Schnappschuss auf
`Nightreign Helper 1.8.0  —  updated for your installed game version`. Der
Waechter laesst das durch (englisch), ich nenne es nur, weil ich beim
Mutieren dort war.

## An director

- **Kein Verstoss gegen A8 oder A3 gefunden.** Beide Waechter sind gruen im
  Bestand: 0 von 5 258 Zeichenketten, 0 von 16 249 Fenstertexten, 0 von 440
  Beraterlaeufen. Es gibt nichts zu beheben und keinen Waechter, der rot
  bleiben muss.
- **QA-204 und QA-205 koennen geschlossen werden** - beide mit einer Zahl
  belegt (M1: 1261 gruen ohne den Waechter; M2: 1260 gruen ohne den
  Waechter). `qa/findings.md` gehoert nicht mir.
- **QA-191 (acht von zehn Nightfarern in keinem Berater-Test)** ist damit
  erledigt, aber **nicht dadurch, dass die alten Tests mehr Helden sehen** -
  die laufen weiter ueber `wylder`. Erledigt ist die *Wirkung*: eine
  Held-spezifische Regression faellt jetzt auf. Wenn die Zeile geschlossen
  wird, sollte das dabeistehen.
- **Bestehende Debt, die ich nicht angefasst habe** (T-114 hat sie schon
  gemeldet, ich bestaetige sie): `tests/advisor_cases.py` haelt mit
  `problem_from_planner` / `context_from_planner` eine **zweite** Uebersetzung
  vom Fenster zur Beraterfrage, deren eigener Docstring sagt, sie sei vor
  `advisorbar.asking_from` entstanden. Ich habe sie nicht benutzt und
  stattdessen den Abgleich `layout_of` == `asking_from` in den Waechter
  gelegt. Aufwand fuer die Ablösung: klein (die zwei Funktionen entfernen
  und ihre Aufrufer auf `asking_from` ziehen), Risiko: mittel, weil die
  Aufrufer Qt-frei laufen wollen. **Nicht in diesem Auftrag.**
- **Performance-Fund, kein Tuning-Auftrag:** die volle Suite streute heute
  ueber vier Laeufe zwischen 153 s und 205 s bei identischem Umfang. Das ist
  ein Faktor 1,34 und macht jede Wandzeit-Aussage unterhalb dieser Spanne
  unbelegbar. Ob das an gleichzeitig laufenden Agenten liegt (T-122 lief
  parallel) oder an der Maschine, habe ich nicht untersucht. Falls kuenftig
  jemand eine Laufzeitschranke setzen soll: `performance-tuner` beauftragen,
  nicht schaetzen.
- **Sicherheitsfunde:** keine.
- **Eskalationen:** keine.

---

## Belege der Rueckkopien

```
$ git status --short
 M ARCHITECTURE.md
 M UI_SPEC.md
?? docs/berichte/T-122-architect.md
?? docs/tasks/T-124.md

$ git diff --stat -- nrplanner nrdata tests run.py
(leer)

$ sed -n '169p' nrplanner/firstrun.py
            else "Refreshing your game data"

$ sed -n '293p' nrplanner/advisor/candidates.py
    offered = inventory.relics_for(slot.colour, slot.deep)
```

`ARCHITECTURE.md`, `UI_SPEC.md` und die beiden neuen Dateien unter `docs/`
stammen vom parallel laufenden `architect` (T-122) bzw. vom `director`;
ich habe sie weder gelesen noch angefasst und nicht committet. Meine zwei
Commits `4d1955d` und `ad291e6` nennen ihre Pfade einzeln hinter `--`.

Kopien fuer die Mutationsruecknahme liegen unter
`…/scratchpad/T-123/` (`candidates.py.orig`, `firstrun.py.orig`,
`app.py.orig`, `test_interface_language.py.orig`) - Temp-Verzeichnis, nicht
dauerhaft, nichts davon im Repository.

**Kein Prozess offen gelassen:** dieser Auftrag hat kein Programm und keinen
Server gestartet. Alle Qt-Fenster entstanden innerhalb von pytest
(`QT_QPA_PLATFORM=offscreen`) und endeten mit dem jeweiligen Prozess.
**Keine der drei Datenverzeichnis-Umlenkungen war noetig**, weil das Programm
nie ausserhalb der Suite gestartet wurde; innerhalb der Suite lenkt
`tests/conftest.py` `NIGHTREIGN_SETTINGS_ORG`/`_APP` auf einen eigenen,
prozess-benannten Speicher um, und das ist der eingefuehrte Weg. Der
Spielstand und der Schnappschuss wurden ausschliesslich **gelesen**.
