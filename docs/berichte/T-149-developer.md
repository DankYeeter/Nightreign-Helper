# T-149 - V2: der Auswahldialog und seine Panels (developer)

```
STATUS: erledigt
AUFTRAG: T-149 - V2: A15 wird sichtbar (Panel, Systemdialog, Pruefung,
         C3, Pfad behalten), plus AK-243/AK-244 aus T-148
GELESEN: docs/tasks/T-149.md · UI_SPEC.md - der ganze A15-Abschnitt
         (Zeilen 2579-3270: §0 bis §12, AK-106 bis AK-132), der T-145-
         Nachtrag (7859-8195, AK-230 bis AK-239), der T-146-Nachtrag
         (8195-8410, AK-240 bis AK-242), der T-148-Nachtrag (8410-8635,
         AK-243/AK-244) · ARCHITECTURE.md Nachtrag XI, Zeilen 5800-5850
         (Bauschritte V1-V4, R7-R12) · docs/berichte/T-147-developer.md ·
         nrplanner/firstrun.py, gamepath.py, app.py (main, rescan_save,
         _on_save_read, load_equipped, reload_chalices), datasource.py,
         inventory.py · nrdata/gamefiles.py · tests/conftest.py,
         test_game_path_memory.py, test_game_dir_recognition.py,
         test_save_read_in_the_background.py, test_interface_language.py ·
         CLAUDE.md
GEAENDERT: nrplanner/firstrun.py · nrplanner/app.py (main) ·
         tests/test_first_run_panel.py (neu, 57 Faelle) ·
         tests/test_game_path_memory.py (die Waechter-Ausnahme geraeumt) ·
         tests/test_save_read_in_the_background.py (3 Faelle fuer
         AK-243/AK-244) · docs/berichte/T-149-developer.md (diese Datei).
         Drei Commits: d2cfbfc, db42d1d, 94689cb - alle mit Pfad hinter
         `--`, kein `-a`, kein `add .`. Kein Push, kein Merge.
ANNAHMEN: (1) Kein gemerkter Pfad **und** brauchbarer Datenabzug: kein
         Panel. A2/A3 haetten dort keinen Pfad zu nennen, A1 wuerde ein
         Programm blockieren, das heute wortlos durchlaeuft. Punkt 4 unten.
         (2) Der Startort des Ordnerdialogs laesst den Schritt "Steams
         `common`-Ordner aus der Bibliothekliste" aus - dafuer gibt es in
         `nrdata` keinen oeffentlichen Namen, und `nrdata` gehoert mir
         nicht. Punkt 5 unten.
         (3) "R7 bis R12 gehoeren hierher" aus dem Auftrag lese ich als
         R7-R9: R10/R11 sind in Nachtrag XI V3 (Spielstand), R12 ist V4,
         und beide schliesst derselbe Auftrag unter Scope-Grenzen aus.
         Punkt 9 unten.
         (4) Die C1/C2-Zeile steht im Bau-Zustand ueber dem Balken; die
         Spec sagt "GOOD, dann sofort der Bau-Zustand", nicht wo. Punkt 6.
NAECHSTER: qa-engineer (AK-129/AK-130/AK-132 am laufenden Fenster, was ich
         nicht kann), danach director wegen der fuenf Meldungen unten
BLOCKIERT DURCH: nichts
```

---

## 1. Umgesetzt

### `nrplanner/firstrun.py` (+700 Zeilen)

**Qt-freie Haelfte - Texte, Panels, Ablauf.** Alles unter "Where is the
game?", alles gegen `UI_SPEC` §7 Wort fuer Wort:

| Name | Was es ist |
|---|---|
| `Line`, `Button`, `Panel`, `Verdict`, `Settled` | Datenformen. `Panel.default` ist der **rechte** Knopf - eine Regel statt sechs Einzelfestlegungen (§9, AK-113, AK-234). `Panel.about` traegt den Verdict, den ein `Use…`-Knopf bestaetigt; nur W1 und C3 haben einen, und das ist "hoechstens eine Rueckfrage je Wahl" als Eigenschaft der Panels statt als Zweig der Schleife. |
| `a1 a2 a3 e1 w1 c3` | die sechs Frage-Zustaende, mit Kopfzeile, Zeilen, Knoepfen, Escape-Antwort, Fusszeile und `rejects` (Kopfzeile in `BAD`, nur E1/W1). |
| `found_it` | C1 oder C2. C2 (`, inside the folder you picked.`) **nur** bei `INSIDE`; nach C3 steht C1 (AK-242). |
| `_where_it_sits` | `SAME` / `INSIDE` / `OUTSIDE`, am **aufgeloesten** Fund gegen den **gewaehlten** Baum, als Pfadteile und durch `os.path.normcase` (T-146, SEC-030). |
| `look_at` | Stufe 1 und 2 in einer Antwort: `search_from`, dann `is_named_nightreign`, dann die Lage. |
| `settle_the_game_folder(ask, pick_a_folder, …)` | die ganze Kette §3.1. Beide bildschirmgebundenen Dinge kommen als Parameter herein - dieselbe Naht, die `Planner` fuer das Spielstandlesen hat. |
| `_confirm` | **die einzige Stelle im Programm, die `paths/game` schreibt** (M3). |
| `the_opening_panel`, `where_to_start_looking`, `the_day_the_data_was_read`, `a_question_is_due` | welches Panel oeffnet, wo der Dialog aufgeht, das Datum des Abzugs, und ob ueberhaupt gefragt wird. |

**Qt-Haelfte.** `_Window` hat jetzt zwei Zustaende statt einem (§3):

- `show_the_question(panel)` - normales Fenster mit Titelleiste und
  Taskleisteneintrag (AK-109), feste Breite 460, Hoehe aus dem Inhalt,
  Mindesthoehe 230; Knopfzeile rechtsbuendig, der rechte Knopf ist
  Standardknopf und bekommt den Fokus.
- `ask(panel)` - dasselbe plus verschachtelte `QEventLoop`; `press`,
  `keyPressEvent` (Enter = Standardknopf, Escape = Escape-Antwort) und
  `closeEvent` (Fensterkreuz = Escape) beantworten sie.
- `show_the_build(first_time, said)` - der Splash von heute, plus die
  C1/C2-Zeile in `GOOD` ueber dem Balken.
- `_new_page`, `_height_of_the_content`, `_wrappable` - siehe Punkt 3.
- `_pick_a_folder` - `QFileDialog.getExistingDirectory`, **nativ**
  (kein `DontUseNativeDialog`), Beschriftung von Qt, Startort aus §4.1.
- `run(game) -> FirstRun` - Frage, Bestaetigung, Bau in **einem** Fenster.
  `ensure_data` bleibt als Name erhalten und ruft dasselbe.

### `nrplanner/app.py` (`main`, 19 Zeilen)

`gamefiles.find_game_dir()` → `gamepath.resolve_game()`, und statt
`ensure_data` jetzt `firstrun.run(...)`. `go_on == False` heisst: der Nutzer
hat `Quit`, Escape oder das Kreuz gewaehlt - Rueckgabe 0, **kein**
Fehlerdialog (AK-116). Der `QMessageBox.critical`-Zweig bleibt fuer den
Baufehler und fuer `load_data()` - AK-131 unveraendert.

Damit ist die benannte Ausnahme aus T-147 leer und in
`tests/test_game_path_memory.py` geraeumt; `test_every_named_exception_is_
still_one` haette sie beim naechsten Lauf ohnehin eingefordert.

### Tests

`tests/test_first_run_panel.py` - **57 Faelle**, neu. Wortlaut (zweite,
unabhaengige Abschrift aus `UI_SPEC` §7), verbotene Woerter, Standardknopf
und Escape je Panel, der zurueckgezogene Satz projektweit, welches Panel
oeffnet, der ganze Ablauf ueber die Naht (Abstieg, Gleichstand, Aufstieg,
Verzeichnisverknuepfung, E1, W1, Abbruch, Startorte), was `run` tut, und
das Fenster selbst (Fensterart, Tastatur, Fokus, Hoehe, Umbruch).

`tests/test_save_read_in_the_background.py` - **3 Faelle** fuer AK-243 und
AK-244 (Punkt 7).

## 2. Der Ablauf, wie er jetzt laeuft

```
resolve_game() == None und a_question_is_due()
  -> A1 (nichts gemerkt) | A2 (gemerkt, kein Abzug) | A3 (gemerkt, Abzug)
     Quit/Escape/Kreuz            -> Programm endet, Rueckgabe 0, nichts gespeichert
     Continue with the data …     -> weiter ohne Spielordner (A3)
     Choose folder…               -> Systemdialog
        Abbruch                   -> dasselbe Panel, derselbe Zustand
        kein Spiel gefunden       -> E1, Schleife
        Name ohne NIGHTREIGN      -> W1  -> Use anyway  -> bestaetigt (kein C3)
        aufgeloest verlaesst Baum -> C3  -> Use this folder -> bestaetigt
        aufgeloest innerhalb/gleich -> bestaetigt, ohne Klick
     bestaetigt: paths/game schreiben -> C1/C2 -> Bau-Zustand
```

## 3. Zwei Fehler am eigenen Bau, gefunden durch Messen (Commit 94689cb)

Beide waeren **still** geblieben: die Suite war gruen, und der erste Blick
auf A1 sah richtig aus.

1. **`adjustSize()` misst den falschen Hinweis.** Der `sizeHint` eines
   umbrechenden Labels ist seine Hoehe auf *einer* langen Zeile. Fuenf der
   sechs Panels standen auf der Mindesthoehe 230 px mit abgeschnittenen
   Saetzen. Jetzt: `heightForWidth(460)` der ausgelegten Inhalte.
2. **Ein geleertes Layout antwortet -1.** Nach `takeAt`/`deleteLater`
   liefert `heightForWidth` -1, bis die geloeschten Widgets wirklich weg
   sind - eine Ereignisrunde spaeter. Betroffen: jedes Panel **ab dem
   zweiten**, also E1 nach A1 und C3 danach. Jeder Zustand bekommt jetzt
   eine eigene Seite (`_new_page`), statt die alte zu leeren.

Dazu AK-129 woertlich ("Pfadzeilen umbrechen"): ein Windows-Pfad hat keine
Leerzeichen, an denen ein Label brechen koennte. `_wrappable` setzt nach
jedem Trenner ein nullbreites Leerzeichen (U+200B). `Line.text` bleibt
unveraendert - daran haengt der Wortlautvergleich.

**Messung nach der Aenderung** (Skript `scratchpad/T-149/measure.py`, ein
wiederverwendetes Fenster, ein Pfad von 81 Zeichen):

| Panel | A1 | A2 | A3 | E1 | W1 | C3 | Bau+C1 | Bau |
|---|---|---|---|---|---|---|---|---|
| Hoehe px | 393 | 323 | 263 | 263 | 355 | 288 | 254 | 190 |

Breite ueberall 460, kein abgeschnittenes Label.
**Messumgebung (L-009):** `QT_QPA_PLATFORM=offscreen`, Qt-Stil Fusion mit
der dunklen Palette aus `apply_appearance`, `QT_SCALE_FACTOR` nicht gesetzt,
**logische** Pixel, offscreen. **Das ist kein Nachweis fuer AK-129/AK-239.**
Der gehoert an ein echtes Fenster bei 100/125/150 % und an einen
Bildnachweis aus dem Fenster (AK-132) - Punkt 8.

## 4. Die eine Stelle, an der ich entschieden habe (Annahme 1)

`resolve_game()` ist `None`, es gibt **keinen** gemerkten Pfad, aber einen
brauchbaren Datenabzug. Die Spec kennt den Fall nicht: A2 und A3 setzen
einen gemerkten Pfad voraus (sie drucken ihn), A1 ist der Erststart. Heute
laeuft dieser Fall **wortlos durch** - `_load_data` reicht den Abzug, und
`QMessageBox.critical` erscheint gar nicht.

Ich frage dort **nicht**. Ein A1 haette ein Programm blockiert, das alles
hat, was es braucht (Entwickler mit Abzug neben dem Paket; Spieler, der das
Spiel nach einem Lauf deinstalliert hat). AK-108 nennt als Bedingung
ausdruecklich den Fall, in dem heute die Fehlermeldung erscheint - und die
erscheint nur ohne Abzug. `a_question_is_due()` ist genau diese Regel, mit
einem Waechter und einer toetenden Mutation.

## 5. Der Startort des Dialogs ist unvollstaendig (Annahme 2)

§4.1 zaehlt auf: gemerkter Pfad → dessen Elternordner → **Steams
`common`-Ordner aus der Bibliothekliste** → `C:\Program Files (x86)\Steam\
steamapps\common` → "Dieser PC". Gebaut sind alle **ausser dem dritten**.

Grund: die Bibliothekliste kennt nur `gamefiles._steam_roots()` und
`gamefiles._library_paths()` - zwei **private** Namen in `nrdata`, und
`nrdata` steht im Auftrag unter "nicht anfassen". Ich habe sie weder
benutzt (das waere neue Cross-Package-Debt, dieselbe Art, die T-147 an
`oodle._DLL_NAMES` gemeldet hat) noch die Logik kopiert (Duplikat).

**Folge:** wer Steam auf einem anderen Laufwerk hat, wacht in
`C:\Program Files (x86)\Steam\steamapps\common` auf statt in seiner echten
Bibliothek - oder, wenn es die nicht gibt, in "Dieser PC". Er kommt trotzdem
ans Ziel; AK-110 ("startet in dem ersten existierenden Ort aus der Liste in
4.1") ist damit **nicht vollstaendig erfuellt**. Behebung: ein oeffentlicher
Name in `nrdata/gamefiles.py` (z. B. `steam_common_folders()`), zwei Zeilen
hier - ein eigener kleiner Auftrag.

## 6. Wo die C1/C2-Zeile steht (Annahme 4)

`UI_SPEC` sagt "`GOOD`, dann sofort der Bau-Zustand", aber nicht, an welcher
Stelle des Bau-Zustands. Ich habe sie als eigenes Label ueber den
Fortschrittsbalken gesetzt, in `GOOD`, und das Fenster um genau die Hoehe
dieses Labels wachsen lassen (gemessen: 190 → 254 px, `heightForWidth`, kein
Zahlenraten). Die heutige Statuszeile bleibt damit unveraendert - haette ich
die Bestaetigung dort hineingeschrieben, waeren die Fortschrittstexte gruen
geworden, und "der Bau-Zustand bleibt wie heute" waere gebrochen.

## 7. AK-243 und AK-244

**AK-243** (`test_the_two_shut_controls_come_free_on_different_conditions`):
fuenf Vorrichtungen, und `optimize_button.isEnabled()` in **jedem**
Endzustand, nicht nur waehrend des Lesens. Belegt: waehrend des Lesens sind
beide zu; nach einem Lesen **mit** Bestand sind beide frei; nach "kein
Spielstand" und nach "nicht lesbar" ist der Reliktknopf frei und `Optimize`
weiter zu. Toetende Mutation gemessen: `answerable = True` in
`advisorbar.py:818` → rot.

**AK-244** (`test_a_failed_takeover_writes_its_own_sentence_and_not_the_
waiting_one`): die drei Saetze aus §2 des Nachtrags, woertlich, je einmal
ausgeloest, die drei Ausgangslagen als `SaveScan` hereingereicht (ein echter
Spielstand mit lesbarer Buildtabelle kann nicht dreimal verschieden
scheitern). Toetende Mutation gemessen: die drei Saetze in `load_equipped`
unterdruecken → rot.

**Befund an den `ui-ux-designer`: AK-244s zweite Haelfte trifft nicht zu.**
"Scheitert das automatische Uebernehmen **nicht**, gilt AK-224 unveraendert
und die Bestandsnotiz bleibt stehen" - sie bleibt nicht stehen.
`load_equipped` schreibt am Ende immer `Loaded {Nightfarer} — {n} chalices,
…` in dieselbe Zeile (`app.py:4079`), auf diesem Weg wie auf dem frueheren
synchronen. Das ist ein **sechster** Satz, der weder zu AK-224s vier noch zu
den drei aus §2 gehoert. Der T-142-Lauf kannte ihn (der Kommentar in
`test_every_ending_of_a_read_leaves_a_sentence_of_its_own` nimmt die
gespeicherten Builds genau deshalb heraus); AK-244 hat ihn beim Nachziehen
nicht mitgenommen. Ich habe **nichts umgebaut**: der Erfolgsfall prueft, was
beide Haelften wirklich tragen (nie der Wartesatz, nie leer, nie eine
Mischung), und die Entscheidung, welcher Satz dort stehen soll, gehoert dem
`ui-ux-designer`.

## 8. Was ich **nicht** geprueft habe - gesagt, nicht verschwiegen

1. **Kein gebautes Artefakt, kein echtes Fenster, kein Bildnachweis.**
   AK-129, AK-130 (am laufenden Fenster), AK-132 und AK-239 sind offen. Die
   Tastatur ist ueber `keyPressEvent` geprueft, nicht ueber echte
   Tastendruecke; die Fokusfrage offscreen, wo kein Fenster aktiv ist.
2. **`_pick_a_folder` laeuft in keinem Test.** Der Systemdialog ist genau
   das, was die Naht ersetzt - er wird nie geoeffnet, also ist auch der
   Startort nur als Rueckgabe von `where_to_start_looking` geprueft und nie
   als das, was der Dialog daraus macht. AK-110 gehoert damit ganz zur QA.
3. **`ask()` und seine verschachtelte `QEventLoop`** sind ungetestet;
   geprueft sind `show_the_question` und `press` einzeln. Ein Fehler dort
   waere kein stiller: das Fenster bliebe stehen.
4. **AK-106/AK-107 am laufenden Programm** (der geglueckte Fall aendert sich
   nicht) sind ueber `a_question_is_due` und den Rauchtest unten belegt,
   nicht ueber einen Start mit Fenster.
5. **AK-117s eigene Pruefung** ("waehrend des Baus hart beenden") ist eine
   Handlung am laufenden Programm; hier steht die Reihenfolge als Zaehlwert
   (`["kept", "built"]`).
6. **125 % und 150 %** - gar nicht geprueft.

**Rauchtest** (offscreen, alle drei Umlenkungen, `scratchpad/T-149/smoke.py`):
`resolve_game()` findet die Installation auf D:, `a_question_is_due()` ist
`False`, `run(None)` gibt `FirstRun(game=None, go_on=True, error=None)`
zurueck, **kein Fenster** wird gebaut, und der Speicher bleibt leer.

## 9. Mutationsbeweis - 21 Mutationen, 21 tot

Getrieben von `scratchpad/T-149/mutate.py`: Datei zur Seite kopieren,
mutieren, zielgenau testen, zurueckkopieren (**kein** `git checkout`).

| # | Mutation | Ergebnis |
|---|---|---|
| a | der Fund wird gespeichert, **bevor** er bestaetigt ist | tot (2 rot) |
| b | ein Automatikfund wird in `run` zurueckgeschrieben | tot (1 rot) |
| c | `_confirm` speichert nicht mehr | tot (2 rot) |
| c2 | stattdessen wird **nach** dem Bau gespeichert | tot (2 rot) |
| d | C3 bei **jeder** Abweichung (die zurueckgezogene T-145-Regel) | tot (3 rot) |
| e | der gewaehlte Pfad wird vor dem Vergleich aufgeloest | tot (1 rot) |
| f | der Name wird nicht mehr rueckgefragt (kein W1) | tot (2 rot) |
| g | die Bestaetigung sagt immer "inside the folder you picked" | tot (3 rot) |
| h | der **linke** Knopf ist der Standardknopf | tot (7 rot) |
| i | ein Abbruch im Systemdialog beendet das Programm | tot (1 rot) |
| j | A2 und A3 sind dasselbe Panel | tot (1 rot) |
| k | es wird immer gefragt | tot (1 rot) |
| l | A3 quittiert auf Escape statt weiterzumachen | tot (2 rot) |
| m | der Frage-Zustand bleibt ein SplashScreen | tot (1 rot) |
| n | der Fokus wird vor dem Neubau des Fensters gesetzt | tot (1 rot) |
| o | `It is only read.` kommt zurueck (SEC-027) | tot (2 rot) |
| p | es wird ueberhaupt nichts gespeichert | tot (2 rot) |
| s | die Fensterhoehe kommt aus `sizeHint` | tot (1 rot) |
| t | ein Pfad bekommt keine Umbruchstellen | tot (1 rot) |
| q | `Optimize` ist waehrend des Lesens frei (AK-243) | tot (1 rot) |
| r | die drei Saetze eines gescheiterten Imports fallen weg (AK-244) | tot (1 rot) |

**Kein Ueberlebender.** m und n sind zugleich die Positivkontrollen fuer die
beiden Fenster-Faelle; o ist die fuer den SEC-027-Suchlauf.

**Rot-vorher fuer die zwei Messfehler aus Punkt 3** ist gemessen und nicht
als Mutation gefuehrt: `adjustSize()` (= Mutation s) bringt fuenf von sechs
Panels auf 230 px mit abgeschnittenem Text; die alte Seiten-Leerung bringt
jedes Panel ab dem zweiten dorthin. Der Waechter benutzt deshalb **ein**
Fenster fuer alle sechs Panels - mit sechs frischen Fenstern waere er gruen
geblieben.

**L-006, Eigenschaft statt Fundstelle (SEC-027):** zwei unabhaengig
formulierte Masken ueber `nrplanner/` und `nrdata/` (alle `*.py`),
`it is only read` und `only read\b`: **0 Treffer**. Die zweite Maske hat
beim ersten Lauf einen falschen Positivtreffer geliefert
(`app.py:1717`, "the only reading a single button can carry") - deshalb die
Wortgrenze; der Fall ist im Test dokumentiert.

## 10. Suite und Umlenkungen

**Suite:** `pytest -n auto` → **1550 passed, 9 skipped, 0 failed**
(180,6 s). Ausgangswert T-147: 1490/9/0. +60 = 57 neue Faelle in
`test_first_run_panel.py` + 3 in `test_save_read_in_the_background.py`.
Keine Zeitschranke in einem der neuen Faelle.

**Alle drei Umlenkungen nachgewiesen, mit Positivkontrolle** - dasselbe
Skript zweimal, einmal ohne und einmal mit Umlenkung:

| | ohne (Positivkontrolle) | mit |
|---|---|---|
| `favourites.ORG` | `DankYeeter` | `DankYeeterT-149` |
| `paths.cache_dir()` | `…\Local\NightreignHelper` | `…\scratchpad\T-149\localappdata\NightreignHelper` |
| `shortcut.shortcut_path()` | `…\Roaming\…\Start Menu\Programs\Nightreign Helper.lnk` | `…\scratchpad\T-149\appdata\…\Nightreign Helper.lnk` |

**Unter `pytest` wird die erste Umlenkung ueberschrieben:**
`tests/conftest.py` setzt `NIGHTREIGN_SETTINGS_ORG=DankYeeterTests` und
`…APP=NightreignHelperTests-<pid>` bedingungslos. Das ist ebenfalls neben
dem Speicher des Nutzers, aber es ist nicht mein Wert - gesagt statt
behauptet. `LOCALAPPDATA` und `APPDATA` waren in **jedem** Lauf umgelenkt.

**Gegengeprueft nach der Arbeit:** `HKCU\Software\DankYeeter` (der Speicher
des Nutzers) enthaelt **keinen** `paths`-Schluessel; im echten Start-Menue
liegt **keine** Verknuepfung mit "Night" im Namen; die Vorlage
`%LOCALAPPDATA%\NightreignHelper-Testabzug` hat unveraendert 841 Dateien.
Der Testabzug wurde **kopiert**, nicht neu gebaut. Kein Server, kein
Hintergrundprozess, nichts laeuft weiter.

## 11. An den `qa-engineer`

Was hier **nicht** geprueft werden kann und an das laufende Fenster gehoert:

1. **AK-129/AK-239/AK-132** - die sechs Frage-Zustaende bei 100/125/150 %
   und den Programmfaktoren bis 200 %, mit einem Bildnachweis **aus dem
   Fenster**. Meine Zahlen in Punkt 3 sind offscreen und logisch; nimm sie
   als Erwartung, nicht als Beleg.
2. **AK-110** - der Systemdialog wird in keinem Test geoeffnet. Startort
   pruefen, und dabei den Fall "Steam auf einem anderen Laufwerk" (Punkt 5).
3. **AK-115** am echten Dialog: zweimal hintereinander abbrechen.
4. **AK-117s eigene Pruefung**: waehrend des Baus hart beenden, neu starten
   - es darf nicht erneut fragen.
5. **AK-106** auf einer Maschine mit Standardinstallation: die Fensterfolge
   muss die von heute sein. Der Rauchtest in Punkt 8 sagt dasselbe ohne
   Fenster.
6. **Eine Falle:** `tests/test_first_run_panel.py` darf `QSettings.remove`
   auf `paths/…` nicht benutzen - der Scan aus R5 liest die Tests mit.
   Aufraeumen laeuft ueber `conftest.clear_settings()`.
7. **Der Weg, den ich nicht bauen konnte:** ein Ordner, der Stufe 1 besteht,
   aber dessen Lesen scheitert (AK-131) - dort muessen die heutigen
   Meldungen stehen bleiben, kein Panel.

## 12. An den `ui-ux-designer`

1. **AK-244, zweite Haelfte, trifft nicht zu** - Punkt 7. Entscheidung
   noetig: bleibt `Loaded {Nightfarer} — …` (dann braucht AK-244 einen
   fuenften Ausgang), oder soll die Bestandsnotiz wirklich stehen bleiben
   (dann ist es eine Code-Aenderung an `load_equipped`, und der Spieler
   verliert die Rueckmeldung ueber den Import)?
2. **Der Fall aus Punkt 4** (kein gemerkter Pfad, aber Daten da) hat keinen
   Text. Ich frage dort nicht. Wenn dort gefragt werden soll, fehlt ein
   Panel-Wortlaut - A2/A3 passen nicht, sie drucken einen Pfad.
3. **Die Fusszeile** steht in A1 und A2 (§7 zeigt sie nur dort). A3, E1, W1
   und C3 haben keine - so gebaut, weil §7 sie dort nicht nennt.
4. **`_wrappable`** (Punkt 3): Pfade brechen jetzt nach jedem Trenner. Das
   ist eine Darstellungsentscheidung, die §7 nicht trifft; AK-129 verlangt
   nur, dass sie umbrechen.

## 13. An den `director`

1. **Der Auftrag nennt "R7 bis R12", Nachtrag XI ordnet R10/R11 zu V3 und
   R12 zu V4** - und derselbe Auftrag schliesst V3/V4 unter Scope-Grenzen
   aus. Ich habe R7-R9 gebaut (Annahme 3). R10/R11 (`paths/save`) und R12
   (langsamer Rueckfallweg) bleiben offen und gehoeren zu V3 bzw. V4.
2. **AK-110 ist unvollstaendig** (Punkt 5). Es fehlt ein oeffentlicher Name
   in `nrdata/gamefiles.py`. Empfehlung: kleiner Auftrag `developer`, zwei
   Dateien, oder als Anhaengsel an V3.
3. **AK-244 ist als Kriterium falsch** (Punkt 7, Adressat
   `ui-ux-designer`). Kein Codebefund - das Verhalten ist aelter als
   T-141.
4. **Bestehende Debt, nicht behoben:** `firstrun` schreibt `GOOD`/`BAD`/
   `MUTED` erneut aus, wie sieben andere Module auch. Ein gemeinsames
   Token-Modul waere die saubere Loesung und beruehrt zehn Dateien - nicht
   meine Entscheidung, und nicht in diesem Auftrag.
5. **Kein Sicherheitsbefund aus diesem Lauf.** M3 haelt (vier Mutationen);
   der Offenlegungsteil von SEC-030 ist jetzt sichtbar gebaut (C3 bei
   Verzeichnisverknuepfung, mit Fall belegt). SEC-029 war ausgeschlossen und
   ist nicht angefasst.
6. **Der Satz "Parallel laeuft nichts" hat diesmal gestimmt.** Waehrend
   meines Laufs war der Arbeitsbaum ausser meinen eigenen Dateien sauber,
   und `git log` zeigt zwischen `b414ab0` und meinem ersten Commit nichts
   Fremdes.
