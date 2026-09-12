# Bericht T-185 — security-reviewer

*Abgelegt vom Director am 12.09.2026 aus der Antwort der Rolle — der
`security-reviewer` hat kein `Write`. Wortlaut unveraendert; ersetzt wurden nur
die HTML-Entitaeten, die auf dem Weg entstanden sind.*

```
STATUS: erledigt
AUFTRAG: T-185 — Vier SEC-Befunde: haelt der Fix, der im Code steht? (SEC-023, SEC-031, SEC-032, SEC-035)
GELESEN: ~/.claude/agents/_rahmen.md · docs/tasks/T-185.md · CLAUDE.md (Projekt + global) ·
  security/findings.md (35 Zeilen) · security/verlauf.md (Z. 395-612) ·
  nrplanner/inventory.py · nrplanner/app.py (Z. 600-665, 1545-1690, 4180-4290, 5160-5200) ·
  nrplanner/firstrun.py (Z. 160-200, 331-560, 1011-1038) · nrplanner/gamepath.py (Z. 95-165) ·
  nrplanner/datasource.py (Z. 88-185) · nrdata/gamefiles.py (ganz) · nrdata/savefile.py (Ausschnitte) ·
  nrdata/oodle.py (Z. 30-60) · tests/test_hostile_savefile.py · tests/test_save_path_memory.py ·
  tests/test_save_read_in_the_background.py · tests/test_game_dir_recognition.py ·
  tests/test_first_run_panel.py · tests/conftest.py (Ausschnitt) ·
  git log/show zu f645c01, bd6bd90, b0e7ee4, a33f678, e5c2b7a
GEAENDERT: keine. Kein Commit, kein Stage, kein Branchwechsel. Zwei Messverzeichnisse
  (%TEMP%/T185-*, %TEMP%/T185b-*) angelegt und am Ende geprueft entfernt (`ls` meldet
  "No such file or directory"). `git status` am Ende leer.
ANNAHMEN: (1) Die Bedrohungslage ist die eines privaten Einzelplatz-Werkzeugs auf einem
  Windows-Konto, wie CLAUDE.md ("Kategorie: privat") und die Nutzerentscheide vom
  02./05.09.2026 sie setzen. (2) Die ACL-Messung an C:\ und D:\steam\steamapps gilt fuer
  diese Maschine; sie entspricht der Windows-Voreinstellung, ist aber Stichprobe eins.
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

---

## Pruefgrundlage

Gemessen am Arbeitsbaum, Branch `docs/audit-and-advisor-design`. Beim Start stand HEAD auf
`13cd739`, am Ende auf `28dc45c` (parallele Rollen haben zwischendurch committet).
`git diff --stat 13cd739 28dc45c -- nrplanner nrdata tests security` ist **leer** — an keiner
der gemessenen Dateien hat sich waehrend des Laufs etwas geaendert, die Zahlen gelten fuer
beide Staende. Der Auftrag nennt `1e6bb98`; die Codepfade sind zwischen `1e6bb98` und
`28dc45c` unveraendert.

Das Programm wurde nicht gestartet. Gefahren wurden vier Testdateien und zwei
In-Process-Positivkontrollen ohne Qt-Fenster.

---

## Befund 1

### [Niedrig | Niedrig | sehr gering] SEC-023 — Save-Pfad mit Steam-Konto-Id auf der Fensterflaeche

**Urteil: behoben.**

**Betroffen:** `nrplanner/inventory.py:340-361` (`_changed_at`), aufgerufen in `:418`.
Senke unveraendert: `nrplanner/app.py:1679-1682` (`_SaveReadWorker.work`) →
`nrplanner/app.py:4219-4221` (`_on_save_failed`).

**Vertrauensgrenze:** Dateisystem/Betriebssystem → Fensterflaeche. Der Text der Flaeche ist
das, was in einen Screenshot und damit in ein oeffentliches Repository geraet (NH-002).

**Angriffspfad, wie er im Befund stand:** Zwischen `find_saves()` und dem `stat()` des
Sortierschluessels verschwindet oder sperrt eine Datei — das Spiel schreibt den Save im
Betrieb neu, ein USB-Laufwerk wird gezogen, ein Netzpfad faellt. Die rohe `OSError` verlaesst
`scan` ungefangen, `_SaveReadWorker.work` macht `str(exc)` daraus, und `str(OSError)` traegt
den Steam-Pfad mit der Konto-Id in die Zeile unter dem Spielstand.

**Woran er heute scheitert:** `_changed_at` faengt die `OSError` und antwortet `0.0`. Die
Datei sortiert dann als aelteste und wird zuletzt versucht; dort faengt `_scan_save:514-521`
die `OSError` ein zweites Mal und wirft `SaveNotReadable(exc.strerror)` — `strerror` ist die
Haelfte der Meldung, die sagt *was* passiert ist, ohne zu sagen *wo*.

**Nachweis (Positivkontrolle, in-process, ohne Dateiaenderung):** derselbe gestellte Zustand
(`exists()` liefert True, `stat()` wirft `OSError(ENOENT, …, str(pfad))`) einmal gegen den
gebauten Code und einmal gegen den Sortierschluessel ohne sein `try`:

```
BUILT   : SaveNotReadable | "The system cannot find the file specified"   (kein Pfad)
UNGUARD : FileNotFoundError | "[Errno 2] … : 'C:\Users\…\NR0000.sl2'"     (voller Pfad)
```

Die ungeschuetzte Fassung reisst drei Zusicherungen des Waechtertests gleichzeitig: die
Ausnahmeklasse, das Verbot von Trennzeichen im Text und der Ordnername. Der Test ist also
rot ohne den Fix, nicht nur gruen mit ihm.

**Fundstellen-Quittung des Auftrags — geprueft und richtig:** SEC-023 nennt
`inventory.load:199`. Bei `a33f678` (dem Stand vom 07.09.2026) steht in Zeile 199 woertlich
`for path in sorted(saves, key=lambda p: p.stat().st_mtime, reverse=True):`, damals noch in
`load`. Heute steht an derselben Stelle (`:418`) `key=_changed_at`. **Derselbe Aufruf ersetzt
exakt die benannte Zeile** — die Quittung des `qa-engineer` stimmt.

**Randbedingung der Auflage:** Geschlossen ist der Pfad an der **Quelle**, nicht an der
**Senke**. `_on_save_failed` schreibt weiterhin ungeprueft `str(exc)` auf die Flaeche; die
Behebungsrichtung des urspruenglichen Befunds ("die Ausnahme auf ihre Klasse abbilden, nicht
`str(exc)` auf die Flaeche") ist **nicht** gebaut. Das Urteil "behoben" gilt, weil ich auf der
automatischen Route heute keine Ausnahme mehr finde, die einen Pfad traegt — nicht, weil die
Senke sicher waere. Wer eine neue Ausnahme auf diesem Weg einfuehrt, macht den Befund wieder
scharf, und heute schlaegt dabei nichts an.

**Absenz-Nachweis mit Nenner** (Behauptung: "auf der automatischen Route entkommt keine
pfadtragende Ausnahme mehr"): geprueft wurden alle `raise`- und `except OSError`-Stellen in
den beiden Dateien der Lesekette (`nrplanner/inventory.py`, `nrdata/savefile.py`) — 11
`raise`-Stellen mit Textkonstante, davon 0 mit Pfadinterpolation; die vier `OSError`-Quellen
ausserhalb eines `try` in `scan` einzeln durchgesehen: `pathlib` schluckt die ersten beiden,
die letzten beiden sind gefangen. Zweite, unabhaengig formulierte Maske (`AK-126` statt
`SEC-023`/`stat`): 16 Treffer ueber `nrplanner/` und `tests/`, keiner zeigt auf eine offene
Stelle.

**Behebungsrichtung (Haertung, nicht Blocker):** `texts_that_can_land_behind_the_prefix()` in
`tests/test_save_read_in_the_background.py:736` sammelt bereits per AST jeden `raise`-Text
der Lesekette und prueft ihn gegen *eine* Eigenschaft ("behauptet, der Save sei in Ordnung").
Eine zweite Maske derselben Sammlung — Trennzeichen, `%APPDATA%`, `userdata` — waere der
Waechter, der die Senke bindet, und kostet keine neue Mechanik.

---

## Befund 2

### [Niedrig | Niedrig | sehr gering] SEC-035 — `stat()` ausserhalb jedes `try` in `inventory.scan`

**Urteil: behoben.** Fix, Nachweis und Positivkontrolle sind **dieselben wie bei SEC-023**
(Commit `f645c01`, 09.09.2026).

**Widerspruch zum Register — SEC-035 und SEC-023 sind derselbe Defekt an derselben Zeile.**
SEC-023 (07.09.2026) nennt `inventory.load:199`, SEC-035 (09.09.2026) nennt
`inventory.scan:379`. Nachgerechnet:

| Befund | Commit, gegen den gemessen wurde | Zeile | Inhalt der Zeile |
|---|---|---|---|
| SEC-023 | `a33f678` | 199 | `for path in sorted(saves, key=lambda p: p.stat().st_mtime, reverse=True):` |
| SEC-035 | `e5c2b7a` | 379 | `for path in sorted(saves, key=lambda p: p.stat().st_mtime, reverse=True):` |

Zwischen beiden lag die Aufspaltung von `load` in `scan`/`build`; die Anweisung ist
identisch, die Senke (`_SaveReadWorker.work` zum `owned_label`) ist identisch, das Leck
(Steam-Konto-Id, AK-126) ist identisch. **SEC-035 ist die Quellhaelfte von SEC-023, zwei Tage
spaeter ein zweites Mal gefunden und unter neuer Nummer gefuehrt.** Das erklaert, warum ein
Commit beide schliesst, und ist zugleich der Grund, warum sie zwei Tage nebeneinander offen
standen, ohne dass jemandem die Doppelung auffiel.

**Was der Test wirklich prueft.** `tests/test_hostile_savefile.py:836-873`
(`test_a_save_that_goes_away_before_it_is_sorted_names_no_path`) bildet den **Angriffspfad**
ab, nicht nur das Verhalten des Codes: er stellt den Zustand her, den das Rennen erzeugt
(ein Pfad, der `exists()` beantwortet und `stat()` verweigert), faehrt `inventory.scan`
vollstaendig durch und prueft beide Eigenschaften, die AK-126 verlangt — die Ausnahmeklasse
und die Abwesenheit jedes Pfadfragments. Er sagt ehrlich dazu, dass der Ausloeser gestellt und
nicht gerannt ist. Die Positivkontrolle oben belegt, dass er ohne den Fix rot ist.

**Lauf:** `pytest tests/test_hostile_savefile.py` → **44 passed, 39,33 s**.
`pytest tests/test_save_path_memory.py tests/test_save_read_in_the_background.py` →
**60 passed, 73,75 s**.

---

## Befund 3

### [Mittel | Hoch | gering, mit Voraussetzungen] SEC-031 — `find_game_dir()` umgeht Decke und Zustimmung

**Urteil: behoben — aber nicht durch die Stelle, die der Auftrag zitiert.**

**Betroffen:** `nrdata/gamefiles.py:76-86` (Kandidatenliste), Kette unveraendert
`gamepath.py:136` zu `firstrun.py:1025` zu `datasource.py:144-147` zu `nrdata/oodle.py:44`
(`ctypes.CDLL`).

**Vertrauensgrenze:** fremdes Dateisystem (angestecktes Laufwerk) zu Codeausfuehrung im
Prozess des Nutzers, ohne Fenster und ohne Klick.

**Angriffspfad, wie er im Befund stand:** Ein Laufwerk, das auf einen Buchstaben zwischen C
und H faellt, traegt einen praeparierten `Game`-Ordner unterhalb von `SteamLibrary` mit einer
untergeschobenen DLL. `find_game_dir()` nahm diese sechs festen Kandidaten ungefragt in seine
Liste, `resolve_game()` gibt die Antwort ungeprueft weiter, `firstrun.run` stellt **keine
Frage**, wenn `game is not None` (`firstrun.py:1025`), und der Datenaufbau laedt die DLL.

**Woran er heute scheitert:** Die sechs festen Kandidaten sind aus `find_game_dir` entfernt
(Commit `bd6bd90`). Jeder Kandidat kommt jetzt aus Steams eigener Auskunft — Registry
(`HKCU`/`HKLM Software\Valve\Steam`), dann `libraryfolders.vdf` unter diesen Wurzeln. Ein
angestecktes Laufwerk ohne Zugang zum Konto des Nutzers kommt in keine dieser Quellen.

**Der Auftrag zitiert die falsche Haelfte als Beleg.** Die Quittung nennt
`nrdata/gamefiles.py:69` ("Asks `looks_like_the_game` (SEC-031)"). Das Zitat steht dort
tatsaechlich (geprueft, Zeile 69 stimmt) — **aber diese Zeile schliesst den Angriffspfad
nicht.** `looks_like_the_game` verlangt eine `regulation.bin` zwischen 1 Byte und 64 MiB,
eine `*.bhd` und eine DLL; alle drei liegen in der Hand dessen, der den Ordner praepariert.
Ein Angreifer, der eine DLL unterschiebt, legt die drei Dateien mit. Die erste Haelfte ist
eine Praedikat-Angleichung (sie schliesst die SEC-028-Restluecke und die Drift zwischen
"einmal akzeptiert" und "beim naechsten Start noch gueltig") — **kein Riegel gegen einen
Angreifer.** Geschlossen wird der Pfad allein durch die **zweite** Haelfte, die
Kandidatenliste. Wer SEC-031 mit `gamefiles.py:69` fuer geschlossen erklaert, belegt ihn mit
der Stelle, die ihn nicht schliesst.

**Was der Test wirklich prueft.** `tests/test_game_dir_recognition.py:212-237`
(`test_find_game_dir_asks_about_nothing_steam_did_not_name`, Docstring "SEC-031, second
half" — Zeile 214, Quittung stimmt) misst die **Liste der Ordner, denen das Praedikat
vorgelegt wird**, nicht die Antwort. Das ist die richtige Achse: ein Kandidat, den es auf
dieser Maschine heute nicht gibt, ist trotzdem ein Kandidat.

**Positivkontrolle (in-process, ohne Dateiaenderung), und der Nachbarwert auf derselben
Achse:**

```
wie gebaut                                      : 1 befragter Ordner
Rueckfall im Rumpf von find_game_dir            : 7 befragte Ordner   -> Test waere rot
Rueckfall ueber _steam_roots (vom Test gestubbt): der Test sieht ihn nicht
```

Der Waechter schlaegt also an — aber **nur fuer die Bauform, die es einmal gab.** Er ersetzt
`_steam_roots` und `_library_paths` durch Stubs; jeder Kandidat, der aus diesen beiden
Helfern kommt, ist fuer ihn unsichtbar. Und dort stehen heute schon zwei feste Wurzeln:
`C:\Program Files (x86)\Steam` und `C:\Steam` (`gamefiles.py:33-34`). Siehe den neuen Befund
weiter unten — das ist derselbe Mechanismus, einen Schritt weiter auf derselben Achse.

**Lauf:** `pytest tests/test_game_dir_recognition.py tests/test_first_run_panel.py` →
**105 passed, 1 failed, 2,03 s**. Der Fehlschlag betrifft SEC-031/032 nicht, siehe
Beobachtung B3.

**Randbedingung der Auflage:** "behoben" gilt fuer den Angreifer, den der Befundtext nennt —
**ein Laufwerk ohne Zugang zum Konto des Nutzers.** Es gilt **nicht** als Aussage darueber,
dass der Ordner, den `find_game_dir` zurueckgibt, authentisch waere. Das bleibt SEC-026, und
das liegt beim Nutzer.

---

## Befund 4

### [Mittel | Mittel | gering] SEC-032 — `SEARCH_DEPTH = 3` dehnt eine Zustimmung auf drei Ebenen

**Urteil: behoben, im Umfang, den der Director am 09.09.2026 entschieden hat.**

**Betroffen:** `nrplanner/firstrun.py:190` (`LEVELS_TAKEN_ON_TRUST = 1`), `:404-426`
(`_where_it_sits`), `:536-539` (`DEEPER` zu C3), `:361-385` (Panel C3).

**Vertrauensgrenze:** ein Ordner, auf den der Nutzer gezeigt hat, zu dem Ordner, aus dem eine
native Bibliothek geladen wird. Die Zustimmung gilt fuer den ersten, wirksam wird der zweite.

**Angriffspfad, wie er im Befund stand:** Ein Angreifer waehlt die Form des Archivs, das
jemand entpackt. Der Nutzer zeigt auf den entpackten Ordner; der Suchlauf steigt bis zu drei
Ebenen ab und findet den praeparierten `Game`-Ordner zwei oder drei Ebenen tiefer. Bis AK-246
galt jeder Abstieg als seine eigene Wahl: `_confirm` schrieb den gefundenen Ordner, und
zwischen Fund und geladener Bibliothek stand kein Fenster.

**Woran er heute scheitert:** `_where_it_sits` zaehlt die Ebenen zwischen dem gezeigten und
dem aufgeloesten Ordner. `INSIDE` (hoechstens eine Ebene) geht ohne Frage durch; ab **zwei**
Ebenen ist das Ergebnis `DEEPER`, und `settle_the_game_folder:536-539` legt C3 vor — beide
Pfade im Klartext, der Vorgabeknopf ist `ANOTHER_BUTTON`, und nur ein ausdruecklicher Klick
auf "Use this folder" fuehrt zu `_confirm`. **Vor der Frage wird nichts geladen:**
`looks_like_the_game` oeffnet `regulation.bin` und liest ein Byte, prueft die Existenz von
`*.bhd` und DLL — `ctypes.CDLL` laeuft erst im Datenaufbau nach `_confirm`.

`SEARCH_DEPTH` bleibt bei 3 (AK-249) — das ist bewusst so: den Suchradius zu kuerzen haette
den Fund gekostet statt den Klick.

**Was die Tests wirklich pruefen — und der Nachbarwert auf der Achse.** Die Achse ist die
Abstiegstiefe. `tests/test_first_run_panel.py` misst beide Seiten der Grenze ueber die
tatsaechlich gezeigte Panel-Folge, nicht ueber ein Flag:

| Tiefe | Test | Panels |
|---|---|---|
| 0 (`SAME`) | `test_the_game_folder_itself_confirms_without_…` | `["A1"]` |
| 1 (`INSIDE`) | Zeile 360-368 | `["A1"]` — keine Frage |
| 2 (`DEEPER`) | `test_two_levels_down_is_asked_about` (Z. 397, "Der Fall, den SEC-032 gemessen hat") | `["A1", "C3"]` |
| 3 | `test_three_levels_down_is_asked_about_and_not_turned_down` | `["A1", "C3"]` |
| hinaus | `test_a_climb_out_of_the_picked_folder_is_asked_about` | `["A1", "C3"]` |

Die Faelle verlangen zusaetzlich die `USE`-Antwort im Spieler-Skript — ohne den Klick kaeme
kein `settled.game` zurueck. Das bildet den Angriffspfad ab, nicht nur das Verhalten des
Codes. Die Quittung des Auftrags (`test_first_run_panel.py:401`) stimmt.

**Randbedingung der Auflage:** Die eine verbleibende Ebene (`INSIDE`) ist **nicht**
geschlossen und soll es nach dem Entscheid vom 09.09.2026 auch nicht sein — sie ist der
Regelfall aus Paragraf 4.2, Steams `Browse local files`. Ein Angreifer, der sein Archiv mit
einem `Game`-Ordner auf der ersten Ebene formt, bekommt weiterhin die klickfreie Uebernahme.
Das faellt in dieselbe akzeptierte Klasse wie SEC-026 ("der Nutzer hat auf den Ordner
gezeigt") und ist der Preis des Entscheids, nicht ein Rest des Fixes. Wer SEC-032 spaeter
zitiert, zitiert diese eine Ebene mit.

---

## Neu aufgefallen, ohne ID (Nummernvergabe beim Director)

### [Vorschlag Mittel | Schwere Hoch | gering, mit Voraussetzungen] `C:\Steam` ist ein zweiter unbestaetigter Kandidat auf derselben Route, die SEC-031 geschlossen hat

**Betroffen:** `nrdata/gamefiles.py:32-35` (`_steam_roots`, feste Wurzeln), weiter wie
SEC-031 ueber `gamepath.py:136` zu `firstrun.py:1025` zu `oodle.py:44`.

**Vertrauensgrenze:** ein Ordner, den ein **anderes lokales Konto** anlegen kann, zu
`ctypes.CDLL` im Prozess des Nutzers, ohne Fenster und ohne Klick.

**Angriffspfad:** `_steam_roots()` liefert nach den Registry-Wurzeln zwei feste:
`C:\Program Files (x86)\Steam` und **`C:\Steam`**. Die zweite existiert auf einer sauberen
Windows-Installation nicht — und jeder authentifizierte Nutzer darf sie anlegen. Gemessen auf
dieser Maschine, `icacls C:\`:

```
NT AUTHORITY\Authenticated Users:(AD)                 <- Unterordner anlegen
NT AUTHORITY\Authenticated Users:(OI)(CI)(IO)(M)      <- Modify auf allem, was darunter entsteht
```

Wer unter `C:\Steam` die Ordnerkette bis `Game` mit den drei Dateien fuellt, die
`looks_like_the_game` verlangt, bekommt sie beim naechsten Start eines Opfers geladen, das
kein ueber Steam auffindbares Nightreign hat und keinen bestaetigten Ordner gespeichert hat
(`resolve_game` Stufe 1 und die Registry-Kandidaten greifen sonst zuerst). `firstrun.run`
fragt nicht, weil `game is not None`.

**Auswirkung:** Codeausfuehrung im Kontext des Opferkontos, ohne Fenster und ohne Klick —
dieselbe Wirkung wie SEC-031, mit einer anderen Voraussetzung: **kein angestecktes
Laufwerk, sondern irgendein zweites lokales Konto** (oder beliebiger Code, der als
irgendein authentifizierter Nutzer laeuft).

**Warum ich trotzdem Mittel vorschlage und nicht Hoch:** Auf der tatsaechlichen
Nutzungsform — ein privates Einzelplatz-Werkzeug auf einem Ein-Konto-Rechner — sind
Angreifer und Opfer dasselbe Konto, und damit faellt der Pfad in genau die Klasse, die der
Nutzer am 05.09.2026 angenommen hat ("bereits uebernommenes Benutzerkonto"). Erst auf einer
Mehrbenutzer-Maschine ist es ein eigener Pfad. Die Einstufung gehoert dem Director, und die
Ueberschneidung mit SEC-026 ist ausdruecklich: **das ist die DLL-Frage, die beim Nutzer
liegt** — neu daran ist allein, dass sie ueber einen Kandidaten laeuft, den SEC-031 nicht
genannt hat und dessen Entfernung nichts gekostet haette.

**Behebungsrichtung:** Entweder `C:\Steam` aus den festen Wurzeln nehmen (Steam schreibt seine
Wurzel in die Registry; die feste Wurzel traegt nur den Fall "Registry gelesen und nichts
gefunden, Spiel liegt aber unter C:\Steam") — oder den Ordner, der nicht aus der Registry
kommt, wie einen vom Nutzer gezeigten behandeln und C3 vorlegen. Zusaetzlich sollte der
Waechter aus `test_game_dir_recognition.py:212` die **echte** Kandidatenliste messen
(`_steam_roots` nicht stubben), sonst bleibt jede kuenftige feste Wurzel unsichtbar.

**Nachweis:** `icacls C:\` (oben), `nrdata/gamefiles.py:32-35`, `firstrun.py:1025`, und die
Positivkontrolle unter Befund 3 ("via helper: der Test sieht ihn nicht").

---

## Beobachtungen (ohne Angriffspfad, ohne Prioritaet)

**B1 — Zwei Nutzertexte behaupten den entfernten Laufwerks-Rueckfall weiter.**
`nrplanner/datasource.py:180` sagt dem Nutzer: *"it was looked for through Steam's library
list and on the drives C to H."* — dasselbe in `scripts/setup_check.py:228`. Der Rueckfall ist
seit `bd6bd90` weg. Kein Angriffspfad, aber dieselbe Klasse wie SEC-027 (ein Text, der etwas
anderes verspricht als der Code tut), und der Satz ist eine Einladung, den Rueckfall
"wiederherzustellen", weil er ja angeblich existiert. Der Abwesenheitsnachweis in
`docs/berichte/T-164-developer.md:173` zaehlte `for drive in` / `CDEFGH` / `ascii_uppercase`
in `*.py` und fand 0 Treffer; die Maske traf den **Prosatext** nicht. Gehoert zum
`technical-writer` bzw. in denselben Fix.

**B2 — Kein Waechter prueft die Fensterflaeche selbst auf Pfade.** `names_no_path()` hat 9
Aufrufstellen in `tests/`; **2** davon pruefen eine Fensterzeile
(`test_save_path_memory.py:351, 377`), und beide betreffen die **gewaehlte** Datei (S3/S4),
nicht die automatische Route. Fuer die automatische Route stehen die Zusicherungen eine Ebene
tiefer, an `read_the_save`/`scan`. Das traegt heute, bindet aber die Senke nicht — siehe die
Haertung unter SEC-023.

**B3 — Ein Test der Erstlauf-Datei ist nicht hermetisch.**
`tests/test_first_run_panel.py:576`
(`test_the_first_dialog_opens_at_the_folder_that_was_remembered`) faellt auf dieser Maschine:
erwartet `None` oder den Steam-Standardpfad unter `C:\Program Files (x86)`, bekommt
`d:\steam\steamapps\common`, weil `where_to_start_looking` ueber
`gamefiles.steam_common_folders()` die **echte** Steam-Installation des Rechners liest. Auf
einem Rechner ohne Steam waere er gruen. Dasselbe Muster in
`test_save_path_memory.py::test_one_unreadable_save_does_not_hide_a_good_one`, das
`savefile.find_saves()[0]` — den echten Spielstand — benutzt. Kein Sicherheitsbefund, aber
eine Zahl der Suite, die auf einem fremden Rechner anders ausfaellt; gehoert zum
`qa-engineer`.

**B4 — Register-Buchfuehrung.** Die Zahlen des Auftrags stimmen: `security/findings.md` hat
**35** SEC-Zeilen, Status **13 offen / 16 behoben / 6 geschlossen** (nachgezaehlt mit `awk`
ueber die Statusspalte). Alle vier Fundstellen-Zitate des Auftrags habe ich einzeln
nachgeschlagen, alle vier stehen dort, wo sie stehen sollen (`inventory.py:340-361`,
`gamefiles.py:69`, `test_game_dir_recognition.py:214`, `test_first_run_panel.py:401`). Der
Einwand betrifft nicht die Zitate, sondern die Schlussfolgerung aus `gamefiles.py:69`
(Befund 3) und die Doppelung SEC-023/SEC-035 (Befund 2).

---

## Vertrauensgrenzen-Skizze des geprueften Bereichs

```
(1) Spielinstallation / gewaehlter Ordner --> Prozess
    find_game_dir()  [Kandidaten: Registry + libraryfolders.vdf; seit bd6bd90 keine
                      Laufwerke C-H; aber weiter feste Wurzel C:\Steam]
    settle_the_game_folder()  [Abstieg bis 1 Ebene ohne Frage, ab 2 Ebenen C3 mit Klick]
        --> looks_like_the_game()  [Hygiene, kein Riegel gegen einen Angreifer]
        --> ctypes.CDLL            [Codeausfuehrung. Kein Riegel dahinter -> SEC-026, Nutzer]

(2) Spielstanddatei --> Lesekette --> Fensterflaeche
    find_saves() -> _changed_at() [OSError gefangen] -> _scan_save() [OSError -> strerror]
        --> SaveNotReadable/ValueError --> _SaveReadWorker.work: str(exc)
        --> owned_label: "Save could not be read: " + reason    [SENKE, ungefiltert]
    Schutzgut: die Steam-Konto-Id im Pfad (AK-126, NH-002: oeffentliches Repo)
```

Innerhalb einer Grenze vertrauenswuerdig: das Konto des Nutzers und seine eigene
Spielinstallation (Nutzerentscheid 02./05.09.2026). Ausserhalb: angesteckte Laufwerke,
entpackte Archive, jede Datei im Save-Ordner, **und — heute nicht abgedeckt — ein zweites
lokales Konto.**

---

## Zusammenfassung an director

| ID | Urteil | Was den Pfad schliesst |
|---|---|---|
| **SEC-023** | **behoben** | `inventory._changed_at` (`f645c01`) — Quelle, nicht Senke |
| **SEC-035** | **behoben** | derselbe Commit, **dieselbe Zeile** — SEC-035 ist SEC-023s Quellhaelfte, doppelt gefuehrt |
| **SEC-031** | **behoben** | Entfernung der Kandidaten C-H (`bd6bd90`) — **nicht** der `looks_like_the_game`-Aufruf, den der Auftrag zitiert |
| **SEC-032** | **behoben** | `LEVELS_TAKEN_ON_TRUST = 1` + C3 ab zwei Ebenen (`b0e7ee4`), im entschiedenen Umfang |

**Befunde je Prioritaet:** Kritisch 0 · Hoch 0 · **Mittel 1 (neu, ohne ID: `C:\Steam` als
unbestaetigter Kandidat)** · Niedrig/Haertung 2 (Senken-Waechter zu SEC-023; echte
Kandidatenliste im SEC-031-Waechter) · Beobachtungen 4.

**Gesamturteil: CONCERNS.** Die vier beauftragten Befunde sind zu; das Register darf auf
"behoben" nachgezogen werden. Offen bleibt ein Mittel-Befund derselben Bauform wie SEC-031,
der eng an der Nutzerfrage zu SEC-026 haengt. Kein Kritisch und kein Hoch offen, also kein
FAIL; mehr als Niedrig, also kein PASS. **WAIVED vergebe ich nicht.**

**Zwei Entscheidungen, die ich nicht treffen darf:**

1. Bekommt der `C:\Steam`-Kandidat eine eigene ID, oder faellt er in die SEC-026-Vorlage an
   den Nutzer?
2. SEC-035 als Duplikat von SEC-023 schliessen (mit Verweis), oder beide getrennt auf
   "behoben" setzen? Ich empfehle: beide auf "behoben", und in SEC-035 den Satz "ist die
   Quellhaelfte von SEC-023, dieselbe Zeile" — sonst zaehlt das Register denselben Defekt
   auf Dauer zweimal.

---

## Geprueft / nicht geprueft

**Geprueft:** die vier Angriffspfade am Code; die vier zitierten Fundstellen einzeln
nachgeschlagen; die historischen Fundstellen bei `a33f678` und `e5c2b7a` nachgeschlagen; vier
Testdateien gefahren (105+1F, 44, 60 Faelle); zwei Positivkontrollen in-process; die
Statusverteilung des Registers nachgezaehlt; ACLs von `C:\` und `D:\steam\steamapps`.

**Nicht geprueft, und warum:**

- **SEC-026, SEC-016/017/018, die DLL-Haertung** — per Scope beim Nutzer.
- **QA-215 / T-186** — laeuft parallel.
- **Vollsuite** — nicht beauftragt und fuer diese vier Urteile ohne Aussage; gefahren wurden
  die vier Dateien, die die Angriffspfade decken.
- **Das laufende Programm** — per Auftrag nicht gestartet. Fuer keines der vier Urteile
  gebraucht: die Ketten sind am Code und ueber die Testseams vollstaendig belegt.
- **Frischer Klon** — nicht gezogen; ich habe nichts geaendert und der Arbeitsbaum war beim
  Start und am Ende sauber, an den gemessenen Dateien im ganzen Lauf unveraendert
  (`git diff --stat 13cd739 28dc45c` leer). Die Testzahlen oben sind deshalb
  Arbeitsbaum-Zahlen und **keine** Freigabezahlen.
- **Mein Rollengedaechtnis** habe ich **nicht** beschrieben: dafuer fehlt mir `Write`, und
  ein Umweg ueber `Bash` waere genau die Dateianlage, die meine Rolle ausschliesst. Was dort
  haette stehen sollen, steht unter "Beobachtungen" und in dieser Zusammenfassung.

**Aufgeraeumt:** kein Server gestartet, kein Hintergrundlauf offen. Die zwei
Messverzeichnisse (`%TEMP%\T185-*`, `%TEMP%\T185b-*`) sind entfernt, geprueft mit `ls` —
"No such file or directory". Keine Suche ab einer Laufwerkswurzel.
