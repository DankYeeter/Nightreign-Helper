# T-193 — A8 zu Ende, und der Waechter, der die falsche Welt baut (developer)

```
STATUS: erledigt
AUFTRAG: T-193 — A8 zu Ende (QA-211, Rest) und die Testvorrichtung, die eine
         Welt baut, die es nicht mehr gibt (QA-227)
GELESEN: docs/tasks/T-193.md; qa/findings.md (QA-211, QA-217, QA-224, QA-227);
         docs/berichte/T-188-developer.md (D-2); nrplanner/errortext.py;
         nrplanner/datasource.py; nrplanner/app.py (main, _rebuild,
         current_build, read_the_save); nrplanner/inventory.py;
         nrplanner/firstrun.py; nrdata/savefile.py; nrdata/binary.py;
         nrplanner/advisorbar.py (asking_from, nur gelesen);
         nrplanner/advisor/types.py (GoalContext); tests/advisor_cases.py;
         tests/test_advisor_evaluate.py; tests/test_exception_text_is_english.py;
         tests/test_save_read_in_the_background.py (AK-229-Sammler);
         tests/test_hostile_savefile.py; scripts/differential/mutate.py
GEAENDERT: nrdata/binary.py; nrdata/savefile.py; nrplanner/inventory.py;
         nrplanner/datasource.py; nrplanner/app.py;
         tests/test_exception_text_is_english.py; tests/advisor_cases.py;
         tests/test_the_fixture_asks_what_the_program_asks.py (neu);
         tests/test_advisor_evaluate.py (nur Docstring);
         docs/berichte/T-193-developer.md.
         Commits: 8089d22 (Teil 1), 063f4bc (Teil 2). Nichts uncommittet.
         UI_SPEC.md / UI_SPEC_REGISTER.md / docs/berichte/T-192-ui-ux-designer.md
         sind vom parallelen T-192 geaendert und von mir **nicht angefasst**.
ANNAHMEN: (1) `game_data` und `planner.data` sind dasselbe Objekt — jetzt als
         Assertion in der Vorrichtung festgehalten, also keine stille Annahme
         mehr. (2) Welche Zielrichtung `asking_from` gefragt wird, ist fuer den
         Kontext gleichgueltig (kein Feld von `GoalContext` haengt am Ziel) —
         im Quelltext nachgelesen, nicht geraten.
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

## Umgesetzt

### Teil 1 — QA-211, die letzten zwei Stellen

Beide Senken fangen **alles**, und `errortext.in_english` zeigt die eigenen
Worte einer Ausnahme nur, wenn ihre Klasse in diesem Programm definiert
wurde. Genau daran scheiterten sie: eine `FileNotFoundError` mit unserer
langen englischen Erklaerung ist von der von Windows nicht zu unterscheiden,
ein `ValueError` mit "not a BND4 save container" nicht von dem von
pycryptodome. Nach Klasse abbilden kostete A7, zitieren kostete A8. Was
fehlte, war die Klasse.

* `nrplanner/datasource.py`: **`NoGameData(FileNotFoundError)`** traegt
  `_no_data_message()`. `nrplanner/app.py::main` reicht jetzt weiter an
  `errortext.in_english(exc)`.
* `nrdata/binary.py`: **`NotWhatItClaims(ValueError)`** — "eine Datei haelt
  nicht, was ihr eigener Kopf verspricht". Sie wird in `binary` (4),
  `savefile` (8) und `inventory` (3) geworfen; beide `str(exc)` in
  `nrplanner/inventory.py::_scan_save` gehen durch `errortext`.
* Bewusst **nicht** umgestellt: `read_owned_relics`' unbekannter Scanmodus.
  Das ist ein Fehler des Programms, nicht der Datei, und hat auf der
  Oberflaeche nichts verloren. Der Grund steht am `raise`.
* **Nicht angefasst**, wie angeordnet: `nrdata/extract.py` (Konsole).

Der AST-Scan findet statt vier nur noch zwei Stellen; `STILL_QUOTING`
geschrumpft auf `extract.py::_bosses` (Konsole, Director-Entscheid) und
`icons.py::read_subtextures` (fremder Befund).

### Teil 2 — QA-227

Die Frage des Auftrags war, ob die Vorrichtung **dieselbe Quelle** benutzen
kann wie das Programm. Sie kann, und tut es jetzt:
`tests/advisor_cases.context_from_planner` holt
`advisorbar.asking_from(planner, A_GOAL_ID).ctx` und setzt mit
`dataclasses.replace` **nur** den Armaturen-Rost wieder auf. Jedes andere
Feld ist das des Programms; ein Feld, das `GoalContext` morgen bekommt,
kommt von selbst mit.

**Warum der Rost zurueckgesetzt wird statt wegzufallen** — das ist die eine
Stelle, an der ich vom Wortlaut des Auftrags abweiche, und der Grund steht
unten unter "An den director", weil daran eine Entscheidung haengt.

Neu: `tests/test_the_fixture_asks_what_the_program_asks.py` mit vier Faellen
— Spion auf `asking_from` (Herkunft), Feldvergleich mit der Dreierliste
`THE_STAT_SHEET_KEEPS`, Pruefung dass jede der drei wirklich noch ein
Unterschied ist, und die Positivkontrolle des Vergleichs selbst.

`tests/test_advisor_evaluate.py` hat **nur einen Docstring** bekommen: der
Pruefpunkt 13 sagt jetzt im ersten Absatz, was "whoever asks" seit A17
nicht mehr deckt. Name unveraendert, weil vier Mutationsanker in
`scripts/differential/mutate.py` daran haengen.

## Rot vorher — jede Schutzmassnahme einzeln abgeschaltet

Je Lauf genau eine Zeile zurueckgedreht, Datei vorher kopiert und danach
zurueckkopiert (kein `git checkout`), Skripte unter
`…/scratchpad/T-193/`-Ersatz im Sitzungs-Scratchpad.

| # | abgeschaltet | was faellt |
|---|---|---|
| 1 | `NoGameData` → `FileNotFoundError` | `test_the_no_dataset_dialog_keeps_the_long_explanation` (1 failed, 17 passed) |
| 2 | `main`: `errortext.in_english(exc)` → `str(exc)` | `test_no_new_place_quotes_an_exception` (1 failed, 17 passed) |
| 3 | `savefile`: `NotWhatItClaims("not a BND4 save container")` → `ValueError` | `test_a_file_that_is_not_a_save_keeps_this_program_s_own_sentence` (1 failed, 17 passed) |
| 4 | `_scan_save` erste Senke → `str(exc)` | `test_a_library_s_complaint_about_a_save_is_not_shown` **und** `test_no_new_place_quotes_an_exception` (2 failed, 16 passed) |
| 5 | `loadout_error` → `str(exc)` | `test_the_line_about_the_stored_builds_says_it_in_english` **und** `test_no_new_place_quotes_an_exception` (2 failed, 16 passed) |

QA-227, wie verlangt **vor** der Reparatur gemessen:
`test_the_fixture_goes_through_the_program` war rot — *"the fixture built a
context of its own instead of asking the program for one"* (1 failed, 3
passed). Die drei anderen Faelle waren am selben Tag gruen; der Unterschied
lag wertmaessig genau bei den drei erlaubten Feldern. **Das ist der Beleg,
dass der gefaehrliche Teil die zweite Implementierung war und nicht die drei
Felder.**

Nach der Reparatur, wieder einzeln abgeschaltet:

| # | abgeschaltet | was faellt |
|---|---|---|
| A | Vorrichtung weicht in `level` ab (Feld ohne Erlaubnis) | `test_nothing_but_the_grid_differs_from_the_program` + Pruefpunkt 13 + der Fluch-Fall (3 failed) |
| B | Vorrichtung fuellt `weapons_held` nicht mehr | `test_every_allowance_is_still_a_difference` + Pruefpunkt 13 (2 failed) |

## Zahlen

**Suite:** `python -m pytest -q --ignore=tests/test_extraction.py
--ignore=tests/test_hostile_gamedata.py`, ohne `-n`, nichts nachinstalliert:

```
1 failed, 1737 passed, 9 skipped in 440.68s (0:07:20)
```

Gegen den Vorlauf aus T-191 (1728 passed, 1 failed, 9 skipped in 563 s):
**+9 passed**, das sind genau meine neun neuen Faelle (5 in
`test_exception_text_is_english.py`, 4 im neuen Waechter). Uebersprungene
unveraendert bei 9, also ist keiner der neuen Faelle auf dieser Maschine
weggeskippt.

Der eine Fehlschlag ist **QA-224**,
`test_first_run_panel.py::test_the_first_dialog_opens_at_the_folder_that_was_remembered`
— `where_to_start_looking(None)` liefert `d:/steam/steamapps/common`, die
echte Steam-Bibliothek dieser Maschine. Keine Beruehrung mit dieser
Aenderung.

**Datenbedingung:** echter Datenabzug unter `%LOCALAPPDATA%` vorhanden
(sonst waeren die `game_data`-Faelle uebersprungen), echter Spielstand
vorhanden (`planner.owned` nicht `None`, sonst haetten die vier neuen
Waechterfaelle geskippt statt zu laufen), **Programm nicht gestartet** —
kein `main()`, keine Umlenkung noetig (QA-195). Kein Server gestartet, kein
Port offen.

## Eigenschaft statt Fundstelle (L-006)

Drei unabhaengig formulierte Suchen nach "eine fremde Ausnahme erreicht
einen Anzeigeweg", jeweils ueber den ganzen Baum:

| Maske | Treffer | Bewertung |
|---|---|---|
| AST-Scan `places_that_quote_an_exception` ueber `nrplanner`+`nrdata` | **2** (vorher 4) | beide bewusst offen, siehe `STILL_QUOTING` |
| Volltext `str(exc` in `nrplanner/`+`nrdata/` | **3** | zwei Kommentare, einmal `errortext.py:94` — der erlaubte Durchlass fuer eigene Klassen |
| Volltext `.strerror` / `.winerror` / `exc.args`, ganzer Baum ausser `tests/` | **2** | `errortext.py:118` (Kommentar), `mutate.py:5266` (Mutationstext) |
| Volltext `{exc}` in `scripts/` | **2** | `setup_check.py:141,157` — Konsolenskript, siehe unten |

## DoD

- [x] Anforderung verstanden, Annahmen oben dokumentiert
- [x] Build & Tests gruen in der benannten Umgebung (Windows, Quellstand,
      Branch `docs/audit-and-advisor-design`), ein bekannter Fehlschlag
      (QA-224) ausgewiesen
- [x] Neue Tests fuer neue Logik; jede Schutzmassnahme einzeln abgeschaltet
      und der fallende Fall benannt
- [x] Linter: **im Projekt keiner konfiguriert** — entfaellt
- [x] Keine Secrets, keine TODOs, kein toter Code
- [ ] **Ungeprueft:** `tests/test_extraction.py` und
      `tests/test_hostile_gamedata.py` (beide `--ignore`, `texture2ddecoder`
      fehlt). `test_hostile_gamedata.py` **beruehrt meine Aenderung**: es
      prueft die Ausnahmen des Extraktionspfades, und `binary.magic` wirft
      jetzt `NotWhatItClaims`. Alle zehn dortigen Erwartungen lauten
      `pytest.raises(ValueError)` und sind gegen eine Unterklasse gutmuetig —
      nachgelesen, nicht ausgefuehrt. **Das ist eine Luecke, kein Beleg.**
- [x] QA-Akzeptanzkriterien selbst durchgespielt, UX/UI unberuehrt

## Dateigrenze: neun statt fuenf, je Datei der Grund

Fuenf waren die Vorgabe; der Auftrag nannte sechs Dateien und erlaubte
ausdruecklich, zu Ende zu bauen. Es wurden neun.

| Datei | im Auftrag? | Grund |
|---|---|---|
| `nrplanner/datasource.py` | ja | die benannte A8-Luecke |
| `nrplanner/app.py` | **nein** | **erzwungen**: die zitierende Stelle *ist* `main`. Eine Klasse allein zeigt nichts; ohne diese Zeile bleibt der Scan-Treffer stehen |
| `nrdata/savefile.py` | ja | die zweite benannte Stelle |
| `nrdata/binary.py` | **nein** | **erzwungen**: `savefile._members` ruft `read_cstring`, dessen drei Verweigerungen auf demselben Pfad liegen (`test_hostile_savefile.py:139` faehrt genau das). Ohne die Klasse dort waeren *unsere* englischen Saetze abgebildet worden — A8 gegen A7 getauscht, also das, was T-190 schon einmal zuruecknehmen musste. Die Klasse gehoert nach `binary.py`, weil `savefile` von dort importiert und der umgekehrte Weg ein Zyklus waere |
| `nrplanner/inventory.py` | **nein** | **erzwungen, zweifach**: beide zitierenden Senken stehen darin, und drei eigene Verweigerungen (Groessengrenze, zwei Dichtedeckel) liegen auf demselben Pfad. Das hat mir die Suite gezeigt, nicht mein Lesen — siehe Befund B-1 |
| `tests/test_exception_text_is_english.py` | ja | `STILL_QUOTING` schrumpft, fuenf neue Faelle |
| `tests/advisor_cases.py` | ja | QA-227 |
| `tests/test_the_fixture_asks_what_the_program_asks.py` | ja (neu) | der Waechter fuer QA-227 |
| `tests/test_advisor_evaluate.py` | **nein** | **erzwungen**: dort steht die falsche Aussage, um die es in QA-227 geht. Nur der Docstring, kein Verhalten, kein Name (vier Mutationsanker) |

## Offene Fragen und Befunde

### An den director — Entscheidung noetig: was Pruefpunkt 13 heute behauptet

Ich habe die Vorrichtung **nicht** vollstaendig auf `asking_from`
umgestellt, sondern sie holt den Kontext des Programms und setzt drei
Felder wieder auf. Der Auftrag laesst das zu ("Geht es nicht, sag warum"),
und hier ist das Warum — mit Kosten, damit entschieden werden kann:

Reine Delegation ist technisch moeglich. Sie toetet aber
`test_the_advisor_computes_the_build_the_window_shows`: die rechte Seite
des Vergleichs ist `planner.current_build()`, und das Statblatt liest den
Armaturen-Rost weiter (`app.py::_rebuild`). Damit rechnen die beiden Seiten
verschiedene Builds, und der Fall ist rot.

Ihn zu retten geht nur, indem man den Rost **im Fenster** leert. Das kostet
messbar zwei der fuenf Zaehne, die T-048 fuer QA-100 eingebaut hat: der
waffentyp-gesperrte Effekt (`state["gate"]`) und der erklaerte Zustand
(`declarable`) sitzen beide auf `weapon_slots[0]`. Ohne Rost traegt sie
niemand mehr; ein Relikt als Traeger haengt am Spielstand des Rechners und
waere genau die QA-224-Klasse.

`_rebuild()` nimmt keine Argumente — man kann das Fenster nicht um einen
rostfreien Build bitten, ohne Produktionscode fuer einen Test zu aendern.

**Was ich stattdessen gebaut habe** schliesst die Ursache (zwei
Implementierungen) und macht die drei Unterschiede sichtbar und bewacht.
Die *Aussage* von Pruefpunkt 13 habe ich im Docstring auf das eingeengt,
was sie noch traegt: gleiche Rechnung bei gleichen Eingaben. Das ist
Variante 2 aus T-188s D-2.

**Zu entscheiden (architect, dann director):** soll Pruefpunkt 13 so
bleiben, oder soll die Zusage "der Berater rechnet den Build, den das
Fenster zeigt" ausdruecklich zurueckgezogen und durch die engere ersetzt
werden? Ich habe keine AK-Nummer angelegt und keinen Befund geaendert.

### B-1 — Debt, von mir mitbehoben, weil er meine Aenderung sonst gebrochen haette

`nrplanner/inventory.py` hatte drei eigene englische Verweigerungen als
blankes `ValueError` (Groessengrenze Zeile 234, zwei Dichtedeckel 151/158).
Die Groessengrenze liegt auf dem Weg durch `_scan_save`; mein erster Wurf
hat ihren Satz abgebildet statt durchgereicht, und
`test_save_path_memory.py::test_the_automatic_route_is_held_to_the_same_limit`
ist rot geworden — *"the file is 300 MB, far larger than any save this game
writes"* wurde zu *"Something went wrong that this program has no sentence
for (ValueError)."* Alle drei tragen jetzt `NotWhatItClaims`.

**Der Kommentar aus T-190 war falsch** und hat mich zuerst in die Irre
gefuehrt: *"everything `_decrypt_slots` raises that is not an `OSError`
comes out of `nrdata/savefile.py`"*. Es kommt auch aus `nrdata/binary.py`
und aus `inventory.py` selbst. Der Kommentar ist mit der Aenderung ersetzt.

### B-2 — A7-Verlust auf dem Erstlauf-Weg, **aelter als dieser Auftrag**, nicht behoben

`nrplanner/firstrun.py:627-632` faengt alles und bildet ueber
`errortext.in_english` ab; ausgenommen ist nur `CannotBuild`. Auf diesem
Weg liegen **24 englische Verweigerungen** des Extraktionspfades:
`dds.py` (5), `dvdbnd.py` (5), `fmg.py` (3), `dcx.py` (2), `extract.py` (2),
`oodle.py` (2), `paramdef.py` (2), `bnd4.py` (1), `param.py` (1),
`tpf.py` (1). Der Spieler sieht fuer jede davon seit T-190 *"Something went
wrong that this program has no sentence for (ValueError)."*

Das ist dieselbe Klasse wie B-1, nur auf dem anderen Pfad, und es ist die
Kehrseite dessen, was T-190 fuer A8 gewonnen hat. **Aufwand zur Behebung:
klein** — dieselbe Klasse in denselben `raise`-Zeilen, zehn Dateien,
mechanisch. **Risiko des Stehenlassens:** der erste Start auf einer
Maschine, deren Spieldateien nicht gelesen werden koennen, sagt dem Nutzer
nichts mehr darueber, *was* nicht gelesen werden konnte. Ich habe es nicht
angefasst, weil es ausserhalb des Auftrags liegt (`nrdata/extract.py` ist
ausdruecklich tabu, und die anderen neun stehen nirgends).

### B-3 — `scripts/setup_check.py:141,157` zitiert `{exc}`

Konsolenskript, faellt nach demselben Entscheid wie `extract.py:324` nicht
unter A8. Nur zur Vollstaendigkeit des Nenners, nicht angefasst.

### B-4 — QA-217 hat sich nebenbei bewegt (nicht geschlossen)

QA-217: *"Ein BND4-Mitglied mit Offset hinter dem Dateiende erzeugt eine
`pycryptodome`-Meldung ('Incorrect IV length') statt einer eigenen"*. Die
fremde Meldung erreicht den Spieler jetzt nicht mehr — er liest *"Something
went wrong that this program has no sentence for (ValueError)."* Das ist
**nicht** die eigene Meldung, die der Befund verlangt; er bleibt offen, sein
Text stimmt aber nicht mehr. Statuskorrektur liegt beim director.

## An qa-engineer

* **Zu pruefen (A8, Teil 1):** Programmstart ohne Datenabzug und ohne
  installiertes Spiel — der Dialog muss die lange englische Erklaerung
  zeigen, nicht "Windows refused it". Zweitens ein Spielstandsordner mit
  einer Datei, die keine `.sl2` ist: die Zeile unter dem Spielstand muss
  *"not a BND4 save container"* sagen.
* **Randfaelle:** eine `.sl2` mit gueltigem BND4-Kopf, aber Mitgliedsoffset
  hinter dem Dateiende (das ist QA-217, siehe B-4) — dort steht jetzt der
  Sammelsatz. Und eine Datei ueber 256 MB im Spielstandsordner: der Satz mit
  der MB-Zahl muss erhalten sein (das war B-1).
* **Zu QA-227:** der neue Waechter ueberspringt sich selbst, wenn die
  Maschine keinen Spielstand hat (`planner.owned is None`). Auf einem
  Rechner ohne Save belegt er nichts — das ist bewusst so wie bei den
  Nachbarfaellen, aber es heisst, dass eine CI ohne Spielstand hier vier
  stille Skips zaehlt.
* **Nicht von mir geprueft:** `test_hostile_gamedata.py` (siehe DoD).

## An ui-ux-designer

Keine Abweichung, keine Oberflaechenaenderung ausser den Fehlersaetzen
selbst — und die stehen alle schon in `nrplanner/errortext.py`, das T-190
angelegt hat. Neu sichtbar wird nur, dass die eigenen Saetze des
Spielstandslesers **erhalten** bleiben, wo sie vorher haetten verloren gehen
koennen.
