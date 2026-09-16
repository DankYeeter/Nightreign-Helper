```
STATUS: erledigt
AUFTRAG: T-150 - V3: der Spielstand bekommt seinen eigenen Weg (developer)
GELESEN: docs/tasks/T-150.md; ARCHITECTURE.md Nachtrag XI (AD-030, V-Tabelle,
  R10/R11); UI_SPEC.md Abschnitt 5, 7 (S1-S5), 9, AK-121 bis AK-130 und
  Abschnitt 9 (f)/(g) der T-141-Fassung; docs/berichte/T-144-security-reviewer.md
  (SEC-029); nrplanner/app.py, nrplanner/gamepath.py, nrplanner/inventory.py,
  nrplanner/firstrun.py, nrdata/savefile.py; tests/conftest.py,
  tests/test_game_path_memory.py, tests/test_save_read_in_the_background.py,
  tests/test_first_run_panel.py; CLAUDE.md
GEÄNDERT: nrplanner/app.py, nrplanner/gamepath.py (Commit 3f08e0a);
  tests/test_save_path_memory.py (neu, Commit f3abaa0);
  tests/test_save_read_in_the_background.py - drei Stellen an `StatedRead`
  (Signatur der Lesestelle) von mir geschrieben, aber **von T-151 mit
  committet** (ea1de90), bevor ich dazu kam
ANNAHMEN: fuenf, unten einzeln aufgefuehrt (Abschnitt 3)
NÄCHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

# T-150 - V3: `Find my save...`, der gemerkte Spielstand, die drei Ausgaenge

## 1. Umgesetzt

**`nrplanner/gamepath.py`** - `resolve_save()`. Die gemerkte Datei, solange sie
eine Datei ist; sonst `None`, was fuer den Aufrufer "entscheide ueber die
Automatik" heisst. Eine Stufe flacher als `resolve_game`, weil `inventory.scan`
`find_saves()` bei `None` selbst laeuft - eine zweite Saveliste hier waere eine
zweite Antwort auf dieselbe Frage. `is_file()` beantwortet jede `OSError` von
sich aus mit False, also ist "Laufwerk weg" derselbe Fall wie "geloescht".

**`nrplanner/app.py`**

| Was | Wo |
|---|---|
| Texte S1-S5, Knopfbeschriftung, Dialogtitel, die drei Filter | Modulkonstanten `FIND_MY_SAVE`, `FIND_MY_SAVE_TOOLTIP`, `CHOOSE_YOUR_SAVE`, `SAVE_FILE_FILTERS`, `CHOSEN_SAVE_IS_EMPTY`, `CHOSEN_SAVE_UNREADABLE`, `NO_SAVE_FOUND` |
| Startort des Dialogs (AK-123) | `where_saves_usually_are()` - aufgeloester `Nightreign`-Ordner, sonst das Roaming-Profil, sonst `None` |
| Der Systemdialog | `_pick_a_save_file(parent)` |
| Groessengrenze vor dem Lesen (SEC-029) | `LARGEST_SAVE_TO_READ`, `_refuse_a_file_no_save_can_be()` |
| Die drei Ausgaenge auseinanderhalten | `read_the_save(data, save_path=None)` - neue Voreinstellung von `SaveReader` |
| Der Knopf | `Planner.find_save_button`, `Planner.find_my_save()` |
| Welche Datei gelesen wird | `rescan_save` fragt `gamepath.resolve_save()`; `SaveReader.start(data, save_path)` und `_SaveReadWorker` reichen sie durch |
| S3 / S5 | `_on_save_read`, Zweig `owned is None` |
| S4 / heutiges Praefix | `_on_save_failed` |

Der lokale Import `from . import gamepath` in `main()` (aus V2) ist durch den
Modulimport ersetzt - dieselbe Datei, dieselbe Sache, keine zwei Wege.

### Warum `read_the_save` ueberhaupt existiert

`inventory.scan` **kann** die drei Ausgaenge nicht auseinanderhalten und soll es
nicht: sie antwortet `None` sowohl fuer "hier ist gar kein Spielstand" als auch
fuer "diese Datei enthaelt keine Relikte", und eine unlesbare Datei verschluckt
sie mit Absicht (`_scan_save`, `except Exception: return best`), weil auf dem
Automatikweg die naechste Datei die gute sein kann.

Fuer eine Datei, auf die der Nutzer gezeigt hat, sind das drei verschiedene
Nachrichten. `read_the_save` trennt sie im Aufrufer:

```
save_path is None  -> inventory.scan(data)              wie bisher
sonst              -> Groessenpruefung
                      inventory.scan(data, save_path)
                      kam None zurueck: savefile.read(save_path)
                          wirft  -> S4 mit dem Grund
                          laeuft -> S3, lesbar und leer
```

Das zweite Lesen laeuft **nur**, wenn der Scan leer zurueckkam - im Normalfall
also nie. `nrplanner/inventory.py` ist damit nicht angefasst worden; die
Meldepflicht aus dem Auftrag entfaellt fuer diesen Punkt.

**Kein Pfad geht in einen Text (AK-126).** Eine `OSError` schreibt den ganzen
Pfad in ihre Meldung, und der Ordner traegt die Steam-Konto-Kennung - deshalb
faengt `read_the_save` `OSError` und gibt nur `strerror` weiter.

### SEC-029 - die Haelfte, die im Aufrufer sitzt

`LARGEST_SAVE_TO_READ = 256 MiB`, geprueft mit `stat().st_size` **vor** dem
ersten `read_bytes()`, Ausgang S4 mit der Groesse im Text.

*Rezept der Zahl (L-001):* gemessen am 09.09.2026,
`find %APPDATA%/Nightreign -printf "%s"` ueber beide Konten dieser
Installation: **19 531 312 Byte** je `NR0000.sl2`, beide gleich. 256 MiB ist
das **13,7fache**. Der Spielstand ist ein festes Layout aus Charakterslots und
waechst nicht mit dem Inhalt, also schneidet die Grenze nichts weg.

## 2. Tests

`tests/test_save_path_memory.py`, **32 Faelle**, alle neu.

| Bereich | Faelle |
|---|---|
| R10 - gemerkte Datei bevorzugt, ihr Verlust still, Eintrag bleibt | 5 (davon 1 am Fenster) |
| AD-030 - nur eine Bestaetigung schreibt (Verhalten + Quelltextsuche) | 3 |
| R11 - die drei Ausgaenge, kein Ordnername in einem Text | 3 |
| AK-123/AK-106 - der Knopf ist da, wenn und nur wenn kein Spielstand da ist | 2 |
| Dialog: Titel, drei Filter, Startort (drei Lagen) | 4 |
| `read_the_save` an echten Dateien: kein Save, leerer Container, Datei weg, ohne Pfad | 4 |
| SEC-029: ueber der Grenze, in Save-Groesse, Rezept der Zahl | 3 |
| AK-127/AK-128: verbotene Woerter, Dateiendung nur wo sie hilft | 8 |

**Rot-vorher (L-007), jede Schutzmassnahme einzeln abgeschaltet.** 18 Mutationen
in einem Baum, der **nur** meine Aenderungen traegt (`git archive HEAD` plus
meine vier Dateien), Treiber `mutieren.py`, Anker jeweils genau einmal im
Quelltext, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, je ~34 s.
**18 von 18 tot**, jede von dem Fall, fuer den sie geschrieben ist:

| Mutation | Datei | faellt |
|---|---|---|
| `the-lost-file-is-forgotten` (leert `paths/save` beim Fehlschlag) | gamepath.py | `..._falls_back_and_is_not_forgotten`, `..._window_whose_picked_file_is_gone...` |
| `the-lost-file-is-read-anyway` | gamepath.py | dieselben zwei plus `..._folder_where_the_file_was...` |
| `existence-is-enough` (`exists()` statt `is_file()`) | gamepath.py | `..._folder_where_the_file_was_is_not_a_save` |
| `s3-names-the-file` (voller Pfad an S3) | app.py | `..._picked_save_without_relics_says_which_account` |
| `the-two-empty-endings-are-one` | app.py | derselbe |
| `no-reason-for-a-file-that-is-not-a-save` (Sonde weg) | app.py | `..._file_that_is_not_a_save_is_refused_with_a_reason` |
| `s4-puts-the-reason-first` | app.py | `..._cannot_be_read_says_so_in_his_words_first` |
| `the-chosen-failure-keeps-the-prefix` | app.py | derselbe |
| `the-size-is-not-looked-at` | app.py | `..._file_too_large_to_be_a_save_is_not_read` |
| `the-limit-is-under-a-real-save` (16 MiB) | app.py | `..._save_of_the_ordinary_size_is_read`, `..._limit_is_far_above_a_real_save` |
| `the-reason-carries-the-path` (`str(exc)`) | app.py | `..._says_so_without_saying_where` |
| `the-button-never-appears` | app.py | `..._button_appears_when_there_is_nothing_to_show` + S3-Fall |
| `the-button-stays-when-a-save-is-loaded` | app.py | `..._button_is_there_only_while_no_save_is` + Ausgang 1 |
| `an-automatic-find-is-written-back` | app.py | `..._only_the_pick_writes_the_key`, `..._ordinary_read_writes_no_path` |
| `a-cancelled-dialog-writes-something` | app.py | `..._cancelled_pick_keeps_nothing` |
| `a-text-names-the-machinery` (`AppData` in S3) | app.py | `..._forbidden_word[S3]` |
| `the-file-type-leaks-into-another-text` | app.py | `..._file_type_is_named_only_where_it_helps` |
| `the-tooltip-stops-naming-the-file` | app.py | derselbe (Positivkontrolle der Maske) |

**Ein Fall war zunaechst zahnlos, und das ist gemessen und nicht geraten.**
`test_an_ordinary_read_writes_no_path` lief auf dem Ende **ohne** Spielstand -
und `an-automatic-find-is-written-back` ueberlebte ihn, weil dieses Ende die
Zeilen gar nicht erreicht, in die ein Rueckschreiben geschrieben wuerde. Der
Fall laeuft jetzt mit einem Spielstand, der **ankommt**, und faellt (zweiter
Lauf, `ergebnis-c.txt`). Gefunden hat das der Mutationslauf, nicht die gruene
Suite.

**Nicht ins Mutationsregister eingetragen** (`scripts/differential/mutate.py`) -
das steht ausdruecklich ausserhalb des Auftrags. Treiber und Ergebnisse liegen
im Scratchpad `T-150/` (`mutieren.py`, `ergebnis-a/b/c.txt`); wer
nachregistriert, findet die Anker dort und nicht in diesem Bericht abgetippt.

### Suitezahl

| Lauf | Ergebnis |
|---|---|
| Vorgabe T-149 | 1550 passed, 9 skipped, 0 failed |
| Baum mit **nur** meinen Aenderungen (`git archive cfb8a3b` + 4 Dateien), `pytest -n auto` | **1582 passed, 9 skipped, 0 failed** (= 1550 + 32) |
| Arbeitsbaum nach meinen Commits, Stand `f3abaa0` (traegt T-151 und T-152 mit) | **1590 passed, 9 skipped, 0 failed**, 176 s |
| Nur die neue Datei, ohne `-n` | 32 passed, 24 s |

Der isolierte Lauf war noetig, weil T-151 gleichzeitig im selben Arbeitsbaum
gearbeitet hat (siehe Abschnitt 5).

## 3. Annahmen

1. **Die drei Ausgaenge gehoeren zur Wahl, nicht zum Start.** AK-124 sagt "die
   drei Ausgaenge einer Spielstand**wahl**". Startet das Programm mit einer
   gemerkten Datei, die leer oder unlesbar ist, bleiben deshalb die heutigen
   Zeilen aus `UI_SPEC` Abschnitt 9 (f)/(g). S3/S4 erscheinen nur als Antwort
   auf ein Klicken von `Find my save...`.
2. **Gemerkt wird, sobald der Lauf startet, nicht erst wenn er glueckt.** Wie
   AK-117 es fuer den Ordner sagt: ein Absturz waehrend des Lesens darf die
   Angabe nicht kosten. Eine unlesbare gewaehlte Datei bleibt also gemerkt;
   AK-121 verlangt genau das, und der Knopf steht daneben.
3. **Der Knopf ist waehrend eines laufenden Lesens nicht da**, nicht nur "wenn
   kein Spielstand geladen ist". Sonst erschiene er bei jedem Start fuer die
   Dauer des ersten Lesens und verschwaende bei der Ankunft wieder - eine
   Bewegung in dieser Knopfzeile, die AK-106 fuer den geglueckten Fall
   ausschliesst. Ein Druck waehrend eines Lesens tut nichts (wie
   `Load equipped`, UI_SPEC Abschnitt 9 (h)).
4. **Der Dialogtitel S2 wird gesetzt**, obwohl `firstrun._pick_a_folder` seine
   Beschriftung Qt ueberlaesst. Begruendung: die Spec gibt S2 als Text dieses
   Programms vor (AK-128), und die Beschriftung ist die einzige Stelle, die
   sagt, welche Datei gesucht wird.
5. **Die heutige Zeile bekommt den dritten Satz aus S5.** Siehe den
   Widerspruch in Abschnitt 6.

## 4. DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests gruen in der benannten Umgebung (Windows 10 x64, offscreen)
- [x] Neue Tests fuer neue Logik, mit toetender Mutation je Waechter
- [ ] Linter: **entfaellt** - das Projekt hat keinen konfiguriert
  (kein flake8/ruff/pylint in `requirements-dev.txt`, kein Konfigurationsfile,
  in `.github/workflows/` nur `tests.yml` und `release.yml`)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Datenverzeichnisse umgelenkt und nachgewiesen (Abschnitt 7)
- [ ] **AK-129 und AK-130 nicht geprueft** - Skalierung 100/125/150 % und
  Tastaturbedienung verlangen einen Nachweis am laufenden Fenster mit
  Bildnachweis (A13-Muster). Das habe ich nicht gemacht: kein Programmstart
  ausserhalb der Suite. Gehoert zum `qa-engineer`.
- [x] Bericht geschrieben

## 5. An den director

**a) Die Dateilisten von T-150 und T-151 waren nicht disjunkt.** T-151 hat
`tests/test_save_read_in_the_background.py` und `tests/test_hostile_savefile.py`
mit angefasst, beide nicht in seiner Liste. Meine drei Zeilen an `StatedRead` in
der ersten Datei sind in **seinem** Commit `ea1de90` gelandet, ohne dass ich sie
committet habe. Schaden ist keiner entstanden - die Aenderung ist meine und ist
richtig drin -, aber die Zuordnung stimmt in der Historie nicht, und der Fall
haette auch andersherum ausgehen koennen: ich hatte die Datei zwei Stunden lang
in einem Zustand, in dem sein Stand und meiner nebeneinander lagen. **Wenn zwei
`developer` gleichzeitig laufen, gehoert die gemeinsame Testdatei in die Liste
genau eines von beiden.**

**b) SEC-029 ist nicht geschlossen, nur halbiert.** Der Befund nennt
`nrplanner/inventory.py:194` (`_read_settled`); die Zeile ist unveraendert
(heute `:201`, `blob = path.read_bytes()`, kein Deckel davor). Mein Deckel sitzt
im Aufrufer und deckt **den Weg, den A15 hinzufuegt** - die vom Nutzer benannte
oder gemerkte Datei. Der Automatikweg (`find_saves()`, Glob `*/*.sl2` im
Roaming-Profil) erreicht `_read_settled` weiterhin ungedeckelt; dort muss der
Angreifer die Datei erst ablegen, was der Befund selbst als die schwaechere
Haelfte beschreibt. **Empfehlung:** eigener Auftrag auf `inventory.py`, der den
Deckel an die Fundstelle setzt; danach kann meiner im Aufrufer bleiben (er faellt
lauter aus, mit S4 statt mit einer verschluckten Ausnahme) oder entfallen.

*Suche nach der Eigenschaft statt nach der Fundstelle (L-006), zwei unabhaengige
Masken ueber `nrplanner/` und `nrdata/`:* `read_bytes(` → **9 Treffer**,
`open(..., "rb")|.read()` → **4 Treffer**. Auf dem Spielstandweg liegen davon
**zwei**: `inventory.py:201` (offen, oben) und `savefile.py:105`
(`savefile.read`, das ich fuer die S3/S4-Unterscheidung rufe - es liegt
**hinter** meinem Deckel). Die uebrigen lesen Spieldateien und gehoeren zur
Vertrauensgrenze des Spielordners (SEC-028, dort mit eigenem Deckel in
`looks_like_the_game`).

**c) Ein bestehender Fehler, den ich nicht behoben habe.** Ist genau **ein**
Spielstand da und der ist unlesbar, sagt das Programm auf dem Automatikweg
weiterhin "No save file found" - eine falsche Tatsachenbehauptung, im
`DESIGN_REVIEW.md:552-566` schon beschrieben. Meine Trennung S3/S4 gilt nur fuer
die vom Nutzer gewaehlte Datei. Aufwand fuer den Automatikweg: klein, aber er
aendert eine Zeile, die AK-229 und Abschnitt 9 (f) beschreiben - das ist eine
Spec-Entscheidung, keine Nachbesserung.

**d) Nicht unter Test: der Aufruf des Systemdialogs selbst.** Jeder Fall ersetzt
`_pick_a_save_file`; Titel, Filterzeichenkette und Startort sind einzeln
festgenagelt, aber dass `QFileDialog.getOpenFileName` mit ihnen gerufen wird,
prueft nichts. Dieselbe Lage wie bei `firstrun._pick_a_folder` seit V2. Das ist
eine Luecke, kein Beleg - QA sollte den Dialog einmal von Hand oeffnen.

**e) Vier Zeilen ueber 79 Zeichen** (2 in `app.py`, 2 in der Testdatei, alle
80-82). Ich habe sie **nicht** umgebrochen: zwei davon sind Anker gelaufener
Mutationen, und Umbrechen nach dem Lauf kostet den Lauf (die Regel steht so im
Rahmen). `app.py` traegt heute 52 Zeilen ueber 79, bis 98 Zeichen - eine harte
Grenze gibt es hier nicht.

## 6. An den ui-ux-designer

**`UI_SPEC` widerspricht sich bei der Zeile "kein Spielstand".**

- Abschnitt 7, **S5** (Zeile 3027-3030): *"No save file found. Relic slots stay
  empty; the Effects and Weapons tabs still work in full. **If your save is
  somewhere else, use Find my save.**"* - ausdruecklich als "Ersatz fuer die
  heutige Zeile `app.py:3217`" bezeichnet.
- Abschnitt 9 (f) der T-141-Fassung (Zeile 7622-7624): dieselbe Zeile **ohne**
  den dritten Satz, ueberschrieben mit *"Kein Spielstand - unveraendert"*.

Ich bin S5 gefolgt: er ist die spaetere Entscheidung, er gehoert zu AK-125, und
ohne ihn steht der neue Knopf ohne Hinweis da. **Die aeltere Stelle sollte
nachgezogen werden**, sonst liest der naechste Auftrag die falsche. Ich fasse
`UI_SPEC.md` nicht an.

Ausserdem zitiert `DESIGN_REVIEW.md:558-562` die alte Fassung - dort als
historischer Befundtext, vermutlich richtig so.

## 7. Datenverzeichnisse - Nachweis

**Positivkontrolle zuerst** (`probe.py`, ohne Umlenkung):

```
cache_dir()     : C:\Users\Daniel\AppData\Local\NightreignHelper
shortcut_path() : C:\Users\Daniel\AppData\Roaming\...\Programs\Nightreign Helper.lnk
favourites.ORG  : DankYeeter
```

**Mit Umlenkung** (derselbe Aufruf, dieselbe Ausgabe):

```
cache_dir()     : ...\scratchpad\T-150\local\NightreignHelper
shortcut_path() : ...\scratchpad\T-150\roaming\Microsoft\Windows\...\Nightreign Helper.lnk
favourites.ORG  : DankYeeterT-150
```

Alle Laeufe (Suite, Mutationen, Einzellaeufe) mit `LOCALAPPDATA`, `APPDATA` und
`NIGHTREIGN_SETTINGS_ORG` auf das Verzeichnis des Auftrags. Der Testabzug wurde
**kopiert** (841 Dateien, 22 MB) und nicht verlinkt.

**Vorher/Nachher, jeweils `diff` ueber die volle Liste, nach dem letzten Lauf:**

| Ort | Umfang | Ergebnis |
|---|---|---|
| `HKCU\Software\DankYeeter` (`reg query -s`) | 160 Zeilen | unveraendert |
| `%LOCALAPPDATA%\NightreignHelper` | 843 Eintraege | unveraendert |
| Startmenue `Programs` | 79 Eintraege | unveraendert |
| `%APPDATA%\Nightreign` (der echte Spielstand) | 10 Eintraege, mtime und Groesse | unveraendert |

**Zwei Dinge, die ich dazu sagen muss, statt sie stehen zu lassen:**

1. **Unter pytest gilt mein ORG-Wert nicht.** `tests/conftest.py:44-45` setzt
   `NIGHTREIGN_SETTINGS_ORG=DankYeeterTests` und die App auf
   `NightreignHelperTests-<pid>`, unbedingt. Geschrieben wurde also dorthin,
   nicht nach `DankYeeterT-150` - vom Speicher des Spielers weg ist beides, und
   die Registry oben belegt es.
2. **Der echte Spielstand wurde trotz umgelenktem `APPDATA` gelesen**, und das
   ist Absicht: `savefile.save_roots()` sucht ausser `%APPDATA%` auch
   `~/AppData/Roaming` fest. Deshalb bleiben die save-abhaengigen Faelle der
   Suite gruen und die Vergleichszahl 1550 gilt. Gelesen, nie geschrieben - die
   mtimes in der Tabelle oben sind der Beleg.

Kein Server, kein Port, kein Prozess bleibt zurueck; ausser den beiden
Mutationsshells (beide beendet, `DONE` in beiden Ergebnisdateien) lief nichts im
Hintergrund. Die drei Kopierbaeume im Scratchpad sind geloescht, die
Messprotokolle liegen noch dort.

## 8. An den qa-engineer

**Was neu ist:** neben `Rescan save` und `Load equipped` steht `Find my save...`,
sobald kein Spielstand geladen ist.

Bitte pruefen, in dieser Reihenfolge:

1. **AK-129** - 100 %, 125 %, 150 % Windows-Anzeige und Programmfaktoren bis
   200 %: die Knopfzeile hat jetzt **drei** Knoepfe statt zwei. Bricht sie um?
   Ist der dritte noch im Fenster? Bildnachweis nur aus dem Programmfenster
   (`PrintWindow`), nie vom Bildschirm.
2. **AK-130** - Tab erreicht den neuen Knopf, Fokus sichtbar, Enter loest aus.
3. **Der Systemdialog von Hand** (siehe 5d): oeffnet er im
   `Nightreign`-Ordner? Stehen die drei Filter in der Reihenfolge
   `Nightreign save (NR*.sl2)`, `Save file (*.sl2)`, `All files (*)`? Traegt er
   den Titel `Choose your Nightreign save file`?
4. **Der Fall, fuer den das alles gebaut ist:** diese Maschine hat **zwei**
   Konto-Ordner (`76561198073567627` und `76561198179244962`), beide mit einem
   19,5-MB-Spielstand. Den jeweils anderen waehlen und pruefen, dass die
   Reliktzahl wechselt und beim naechsten Start so bleibt.
5. **R10 von Hand:** eine Datei waehlen, das Programm beenden, die Datei
   umbenennen, neu starten. Erwartet: kein Wort darueber, kein Dialog, die
   Automatik uebernimmt - und nach dem Zurueckbenennen ist wieder die gewaehlte
   Datei dran, ohne erneutes Fragen.
6. **Randfaelle**, die ich abgedeckt habe und die trotzdem einen zweiten Blick
   verdienen: Dialog abbrechen (nichts darf sich aendern); eine beliebige
   Nicht-Save-Datei waehlen (S4 mit dem Grund darunter, kein Pfad im Text); eine
   sehr grosse Datei waehlen (S4 mit der Groesse, und das Programm darf nicht
   haengen); `Find my save...` druecken, waehrend `Rescan save` noch laeuft
   (nichts passiert).
7. **Was ich nicht abbilden konnte:** einen echten Spielstand, der lesbar ist
   und **keine** Relikte enthaelt (S3). Mein Fall dafuer ist ein von Hand
   gebauter leerer BND4-Container. Ein frisch angelegter Charakter waere der
   echte Fall.
