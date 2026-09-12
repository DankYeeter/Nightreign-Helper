# T-114 - A9: A3 bis A8 gegen das gebaute Artefakt (qa-engineer)

```
STATUS: erledigt
AUFTRAG: T-114 - A9: A3 bis A8 gegen das gebaute Artefakt
GELESEN: docs/tasks/T-114.md, ~/.claude/agents/_rahmen.md, GOAL.md (A3-A9, A15,
  A16, A17), qa/findings.md (Kopf und Schluss), NightreignHelper.spec, run.py,
  nrplanner/{paths,favourites,shortcut,datasource,advisorbar,app,model,
  firstrun}.py, nrplanner/advisor/{run,goals,types,evaluate,worker}.py,
  nrdata/savefile.py, tests/{conftest,advisor_cases}.py,
  tests/test_advisor_{goals,worker,search,evaluate}.py
GEAENDERT: docs/berichte/T-114-qa-engineer.md (nur diese Datei; nichts
  gestaged, nichts committet)
ANNAHMEN: keine unbestaetigten Annahmen zum Auftrag. Eine Lesart ist im
  Bericht als solche gekennzeichnet: A6 traegt in GOAL.md keinen Zielwert
  (S11 offen), deshalb ist seine zweite Haelfte nicht entscheidbar.
NAECHSTER: director
BLOCKIERT DURCH: nichts. Messbaum, Skripte und Bildnachweise liegen
  unversioniert im Scratchpad unter `T-114/` (Temp-Verzeichnis, nicht
  dauerhaft).
```

---

## Urteil je Kriterium

| Kriterium | Urteil | Traeger des Urteils |
|---|---|---|
| **A3** | **PASS** | 440 Beraterlaeufe am verpackten Code: 10/10 Nightfarer, 74/74 Kelche, beide Zielrichtungen, 2 508 Slot-Vorschlaege, kein Lauf ohne Vorschlag, kein freier Slot unbesetzt |
| **A4** | **PASS** | 2 508 Slot-Vorschlaege: 0 Farbverstoesse, 0 Deep-Verstoesse (660 Deep-Slots), 0 doppelt verwendete Kopien; Stacking: 50 von 84 nicht stapelbaren Effekten bewegen eine gerankte Zahl, bei allen 50 ist zweimal == einmal (Positivkontrolle: 202 von 206 stapelbaren aendern sich) |
| **A5** | **PASS** | 12 640 Begruendungszeilen, jeder besetzte Slot mit mindestens einer; Nutzersprache am Fenster des Artefakts belegt |
| **A6** | **CONCERNS** | Nicht-Blockieren belegt (12 890 Durchlaeufe der Ereignisschleife waehrend eines 4,94-s-Laufs, groesste Pause 70,3 ms). Die zweite Haelfte - "im gemessenen Budget" - hat in `GOAL.md` **keinen Zielwert**; S11 ist offen. Gemessen: Median 3,51 s, p90 4,99 s, max 6,02 s bei 309 Relikten |
| **A7** | **PASS** | 423 von 440 Laeufen tragen `not_counted`; 93 verschiedene Nichtwissens-Saetze in Nutzersprache, z. B. "only applies under a condition, so no number here." |
| **A8** | **PASS** | 545 vom Berater erzeugte Texte ohne Fremdsprachentreffer; 4 806 Zeichenketten des verpackten Codes durchsucht, 1 Treffer und der ist ein englischer Docstring; zwei Fensterabzuege des laufenden Artefakts durchgaengig englisch |

**Ist A9 erfuellt?** Ja - A3 bis A8 sind erstmals gegen das gebaute Artefakt
geprueft, fuenf davon mit PASS und A6 mit CONCERNS, weil sein Zielwert im
Abnahmekriterium noch fehlt.

---

## Schritt 0 - die Datenschutzsperre

Alle drei Umlenkungen nachgewiesen, jede mit Positiv- **und** Gegenprobe.

| Ort | Positivkontrolle (Schreibzugriff landet im Testverzeichnis) | Gegenprobe (echter Ort unveraendert) |
|---|---|---|
| `NIGHTREIGN_SETTINGS_ORG` (`favourites.py:25`) | `QSettings.fileName()` = `HKEY_CURRENT_USER\Software\DankYeeterQA-T114\NightreignHelper`; Marker geschrieben und zurueckgelesen; per `reg query` im QA-Zweig nachgewiesen | `reg export HKCU\Software\DankYeeter` vorher/nachher **byteidentisch** (auch nach dem vollen EXE-Lauf) |
| `LOCALAPPDATA` (`paths.py:20`) | `cache_dir()` zeigt in den Sandkasten; Datei geschrieben; das **Artefakt selbst** hat dort seinen Icon-Pack gebaut (840 Dateien) | `find` ueber `%LOCALAPPDATA%\NightreignHelper` (841 Dateien) vorher/nachher **identisch** |
| `APPDATA` (`shortcut.py:44-49`) | `shortcut.create()` schrieb `Nightreign Helper.lnk` in den Sandkasten - einmal aus dem Quellstand mit gesetztem `FROZEN`, einmal aus dem verpackten Code | `find` ueber das echte Startmenue (79 Eintraege) vorher/nachher **identisch** |

Nach dem Lauf ist der Registry-Zweig `HKCU\Software\DankYeeterQA-T114`
geloescht und die Loeschung geprueft. Der Arbeitsbaum ist unveraendert
(`git status` leer ausser diesem Bericht).

**Gelesen, nie geschrieben:** der echte Spielstand. `nrdata/savefile.py`
enthaelt keinen Schreibpfad (Volltextsuche nach `write` und `open(...,"w")`:
1 Treffer, ein Kommentar). Wichtig fuer die naechste Rolle:
`savefile.save_roots()` haengt **zusaetzlich** `~/AppData/Roaming` an, deshalb
findet das Programm den echten Spielstand auch bei umgelenktem `APPDATA` -
das ist gewollt und harmlos (Lesepfad), aber es heisst, dass `APPDATA` allein
den Spielstand **nicht** abschirmt.

---

## Was geprueft wurde, und womit

**Artefakt.** `dist\NightreignHelper.exe`, 59 010 777 Byte, SHA-256
`42b21aa2743fe64a83a093be0261abaec361d99903150d620e5324bd4301f221` -
**stimmt mit der Vorgabe ueberein**, nicht neu gebaut. Gemessen gegen
Repositoriumsstand `004b295` (der Bau selbst stammt aus `T-111`; die vier
Commits seither sind reine Dokumentation, siehe naechster Absatz).

**Drei Zugaenge, absichtlich verschieden:**

1. **Auspacken.** `PyInstaller.archive.readers` liest 510 Eintraege aus der
   EXE und 355 Module aus `PYZ.pyz`, ohne die EXE zu starten.
2. **Bundle-Pruefstand.** Der ausgepackte Baum als `sys.path`, `sys._MEIPASS`
   und `sys.frozen` gesetzt wie im laufenden Artefakt. Damit laufen **die
   .pyc des Artefakts** mit **den Qt-Binaerdateien des Artefakts**
   (PySide6 6.11.1 aus dem Bundle, `nrplanner.__version__` = 1.8.0). Hier
   sind die 440 Beraterlaeufe entstanden.
3. **Das Artefakt selbst.** `NightreignHelper.exe` gestartet, Erstaufbau
   abgewartet, ueber UI Automation `Reset Chalice` und `Optimize` gedrueckt,
   Fensterabzuege ueber `PrintWindow` auf das **eigene HWND** des Programms
   (kein Bildschirmabzug, NH-002).

### Der Kern der Frage: haelt der Quellstand in der verpackten Fassung?

**Ja, und zwar nachweisbar auf der Ebene des Bytecodes.** Alle 62 Module aus
`nrplanner` und `nrdata` liegen im PYZ (41 + 21, genau die Zahl der
Quelldateien). Ihre Codeobjekte wurden gegen den frisch uebersetzten
Quellstand disassembliert und verglichen:

```
identisch=62 abweichend=0 nur-im-artefakt=0
Positivkontrolle (mutierte Quelle vs. Artefakt): erkannt
```

Der Vergleich kanonisiert nur zwei seed-abhaengige Darstellungsdetails
(Objektadressen, Reihenfolge in `frozenset`-Reprs). **Rot-vorher:** eine
zusaetzliche Zeile in `nrplanner/advisor/evaluate.py` macht den Vergleich
sofort rot - das ist die Positivkontrolle in der Ausgabe oben. Vier Module
(`extract`, `effecttext`, `model`, `search`) waren vor der Kanonisierung
faelschlich als abweichend gemeldet; die Ursache war ausschliesslich die
Elementreihenfolge in `frozenset`-Literalen, nachgewiesen an einem
Einzeldiff.

**Damit ist die im Auftrag genannte Fehlerklasse abgedeckt** - und die
Ressourcenseite gesondert:

| Risiko | Befund am Artefakt |
|---|---|
| Fehlende Ressourcen im Bundle | `data\icon.ico` vorhanden, **236** `paramdefs\*.xml` vorhanden; Qt-Plattform-Plugin `qwindows.dll`, `qmodernwindowsstyle.dll`, 10 Bildformat-Plugins, `python312.dll` vorhanden |
| Pfade, die nur mit `__file__` funktionieren | Genau **eine** `__file__`-Stelle im ganzen Produktivcode (`datasource.py:21`), und sie steht hinter der `_MEIPASS`-Abfrage. Mit gesetztem `_MEIPASS` loesen `icon_path()` und `defs_dir()` auf das Bundle auf; ohne `_MEIPASS` liefern beide `None` - das ist der Unterschied, den nur ein Lauf in der verpackten Fassung zeigt |
| Daten, die zur Laufzeit gebaut statt mitgeliefert werden | Bestaetigt und gewollt: der Schnappschuss und der Icon-Pack werden aus der Spielinstallation gebaut. Das Artefakt hat das im Lauf getan und **in das umgelenkte Verzeichnis** geschrieben |
| Verhalten nur mit warmen Caches der Entwicklung | Der Bundle-Pruefstand laeuft ohne `.venv`, ohne `vendor/`, ohne `tests/`-Daten und ohne Quellbaum; die 440 Laeufe kamen ohne einen einzigen Fehler durch |

### Der Weg, den ein Mensch benutzt

Das gestartete Artefakt meldet den Titel **"Nightreign Helper 1.8.0"**,
Fenster 1365 x 897 logische Pixel auf 1707 x 1067 logischem Bildschirm,
Windows-10-Standardskalierung, Qt-Fusion-Stil wie ihn `apply_appearance`
setzt (L-009). Statuszeile: **"309 relics in USER_DATA000, 110 stored
builds"** - die Zahlen des Auftrags, vom Artefakt selbst gelesen.

Nach `Reset Chalice` + `Optimize` steht je Slot ein Vorschlag mit Kopfzeile
`SUGGESTED - MAXIMISE DAMAGE`, dem Relikt-Namen, der Zeile
*"2 of its 3 effects moved a number in this build."* und den Effektzeilen -
und daneben `Apply all`, `Why`, `Cancel`. Das ist A3, A5 und A8 an der
Oberflaeche des gebauten Programms, nicht an einer Testdoppelung.

---

## Antwort auf die zweite Frage: pruefen die vorhandenen Tests A3 bis A8?

Die Suite ist gruen und gross - **1257 passed, 9 skipped, 0 failed in
180,81 s** (`pytest -q -n auto`, frischer Klon `004b295`, dieselbe
Zahl wie T-111). Sie deckt die Kriterien aber **sehr ungleich** ab.

| Kriterium | Was die Suite dazu wirklich behauptet |
|---|---|
| A3 | **Nur die Registerkarte der Ziele.** `test_the_project_promised_two_named_directions` prueft `GOALS` auf zwei Eintraege und ihre Beschriftungen. Kein Test laesst den Berater **fuer jeden Nightfarer und jedes Kelch-Layout** antworten. Das ist der Teil des Satzes, der die Arbeit macht - und er ist unbewacht |
| A4 | Teilweise. Farbregel und Stacking haben je einen Fall (`test_advisor_search.py:153`, `test_advisor_evaluate.py:379`); QA-181 zeigt, dass der Rand offen ist |
| A5 | Ja, mehrere Faelle in `test_advisor_explain.py` |
| A6 | **Ja, und bindend.** `test_the_window_keeps_its_event_loop_while_the_run_goes_on` schiebt ein kuenstlich langsames Ziel unter und zaehlt Timer-Ticks *waehrend* des Laufs. Ein Lauf im Hauptfaden wuerde ihn rot machen. Die **Zahl** aus A6 prueft er nicht - es gibt keine |
| A7 | Ja, mehrfach (`test_advisor_candidates.py:126`, `test_advisor_explain.py:1928`, `test_advisor_goals.py:79`) |
| A8 | **Gar nicht.** Drei unabhaengige Suchmasken ueber **71** Testdateien: `english` (0 Dateien), `A8` (0 Zeilen), `ascii\|umlaut\|sprache\|non-english\|localis\|localiz` (3 Zeilen, alle in `test_build_names.py` und alle ueber Build-Namen, nicht ueber Oberflaechentexte) |

**Kurz:** fuer A5, A6 und A7 belegen die Tests das Kriterium. Fuer A3 und A8
belegen sie, dass der Code tut, was er tut - die Aussage des
Abnahmekriteriums steht in keinem Testfall. Genau diese beiden Luecken hat
dieser Lauf am Artefakt zugemacht, aber er hat sie **einmal** zugemacht; ein
Test tut es bei jedem Commit.

---

## Befunde

### [P3 | Major | Hoch] A6 traegt keinen Zielwert, deshalb ist die Haelfte des Kriteriums nicht entscheidbar

**Adressat:** director
**Betroffen:** `GOAL.md` A6; `ARCHITECTURE.md:2271` (Schritt S11)
**Umgebung:** Bundle-Pruefstand des Artefakts, echter Spielstand, 309 Relikte

**Reproduktion:**
1. `GOAL.md` A6 lesen: *"bei grossen Relikt-Bestaenden bleibt die Antwortzeit
   im gemessenen Budget (Zielwert wird vom performance-tuner gesetzt)"*.
2. In `GOAL.md` nach einer Zahl fuer dieses Budget suchen.
3. `ARCHITECTURE.md` S11 lesen: *"`performance-tuner` misst K/W gegen den
   echten Bestand ... A6 bekommt seine Zahl."* - Schritt offen.

**Erwartet:** eine Schranke, gegen die eine gemessene Antwortzeit PASS oder
FAIL ergibt.
**Tatsaechlich:** kein Wert. Jede gemessene Zahl erfuellt das Kriterium
gleich gut, was es als Abnahmekriterium wirkungslos macht.

**Analyse:** Kein Produktfehler, eine Luecke in der Anforderung. Die erste
Haelfte von A6 - "blockiert die Oberflaeche nicht" - ist belegt und haelt.

**Auswirkung:** A6 kann von niemandem abgenommen werden, auch nicht von einem
spaeteren Lauf. Zur Einordnung die Zahlen dieses Laufs, damit die Festlegung
eine Grundlage hat (Skript `T-114/sweep2.py`, Rechner dieses Laufs,
Bundle-Pruefstand, 309 Relikte, 440 Laeufe):

| Fall | Median | p90 | max |
|---|---|---|---|
| ohne Deep of Night (220 Laeufe, 3 freie Slots) | 2,52 s | - | 5,36 s |
| mit Deep of Night (220 Laeufe, 6 freie Slots) | 4,18 s | - | 6,02 s |
| alle 440 | 3,51 s | 4,99 s | 6,02 s |

**Lesart, die nicht meine ist:** `nrplanner/advisor/run.py:346` nennt fuer den
schlimmsten *echten* Fall - 309 Relikte, Wylder's Chalice, Deep of Night,
sechs freie Slots - **960 ms**. Meine Messung desselben Falltyps liegt bei
4,94 s (Einzelmessung, `T-114/stack_a6.py`). Ob das ein anderer Rechner, eine
andere Last oder eine Verschlechterung ist, kann ich nicht entscheiden: die
960 ms tragen kein Rezept (kein Skript, kein Commit, keine Maschine). Das
gehoert zur Festlegung des Zielwerts, nicht in einen Befund.

**Vorschlag:** S11 vor der Freigabe ziehen und die Zahl in A6 eintragen, oder
A6 auf seine erste Haelfte kuerzen. Beides ist eine Entscheidung des
`director`.

---

### [P3 | Major | Mittel] A8 hat keinen Waechter - die Sprachregel wird von keinem Test gehalten

**Adressat:** developer (Umsetzung), director (Reihenfolge)
**Betroffen:** `tests/` insgesamt (71 Dateien)
**Umgebung:** frischer Klon `004b295`

**Reproduktion:**
1. `grep -ril "english" tests/` -> **0** Dateien.
2. `grep -rn "A8" tests/*.py` -> **0** Zeilen.
3. `grep -rniE "ascii|umlaut|sprache|non-english|localis|localiz" tests/*.py`
   -> **3** Zeilen, alle in `test_build_names.py`, alle ueber Build-Namen.

**Erwartet:** wenigstens ein Fall, der rot wird, wenn ein deutscher Satz in
die Oberflaeche geraet.
**Tatsaechlich:** keiner. Die Regel haelt heute, weil sie eingehalten wird,
nicht weil etwas sie haelt.

**Analyse:** Die Projektsprache fuer Dokumente ist Deutsch, die fuer
Oberflaechentexte Englisch. Diese Grenze verlaeuft mitten durch dieselben
Dateien und ist nirgends maschinell markiert.

**Auswirkung:** Ein einzelner deutscher Satz in einer Fehlermeldung faellt
erst einem Nutzer auf. Der Bestand ist heute sauber: 4 806 Zeichenketten in
62 verpackten Modulen durchsucht, ein einziger Treffer und der steht in einem
englischen Docstring in `advisor/explain.py`; dazu 545 zur Laufzeit erzeugte
Beratertexte ohne Treffer. Die Positivkontrolle der Maske schlaegt auf
"Die Datei kann nicht gelesen werden" an.

**Vorschlag:** Ein Waechter ueber die Zeichenketten der Module, die
Oberflaechentext erzeugen, mit einer `OFFEN`-Liste, die nur schrumpfen darf.
Nicht ueber Docstrings - sonst bewacht er die falsche Menge.

---

### [P3 | Major | Mittel] A3s eigentliche Aussage - "fuer jeden Nightfarer und jedes Kelch-Layout" - steht in keinem Testfall

**Adressat:** developer
**Betroffen:** `tests/test_advisor_goals.py:59-64` und die uebrigen elf
`tests/test_advisor_*.py`
**Umgebung:** frischer Klon `004b295`

**Reproduktion:**
1. `tests/test_advisor_goals.py::test_the_project_promised_two_named_directions`
   lesen: es prueft `GOALS` und zwei Beschriftungen.
2. Die zehn Nightfarer-Namen ueber alle zwoelf `test_advisor_*.py` plus
   `advisor_cases.py` suchen.

**Erwartet:** ein Fall, der den Berater fuer jeden Nightfarer und jedes
Layout antworten laesst.
**Tatsaechlich:** in den Beratertests namentlich erwaehnt sind **Wylder**
(11 Dateien), **Duchess** (2), **Scholar** (1), **Undertaker** (1). Sechs
Nightfarer - Guardian, Ironeye, Raider, Revenant, Recluse, Executor - kommen
in **keiner** Beraterdatei vor. Ein einziger Fall
(`test_advisor_evaluate.py:95`) waehlt dynamisch "irgendeinen ausser dem
ersten"; welcher das ist, entscheidet der Datensatz.

**Praezisierung zu QA-191:** dort steht "acht von zehn". Nachgezaehlt mit
zwei unabhaengigen Masken (Namensliste ueber 13 Dateien; zweite Maske
`select_hero|hero_index|heroes\[`) sind es **sechs** ohne jede Erwaehnung und
einer dynamisch getroffen. Die Aussage von QA-191 bleibt richtig, die Zahl
war zu gross.

**Auswirkung:** Ein Fehler, der nur einen bestimmten Nightfarer oder ein
bestimmtes Kelch-Layout trifft, faellt der Suite nicht auf. Dieser Lauf hat
es einmal ueberprueft - 440 Laeufe, 10 Nightfarer, 74 Kelche, 2 508
Slot-Vorschlaege, 0 Fehler -, aber am Artefakt und von Hand.

**Vorschlag:** Einen parametrisierten Fall ueber `planner.heroes` und die
Kelchliste, der `advisorbar.asking_from` benutzt (nicht die Testkopie, siehe
Beobachtungen) und die drei billigen Zusagen prueft: Vorschlag vorhanden,
Farbe passt, Begruendung nicht leer. Er kostet Laufzeit - deshalb gehoert die
Entscheidung ueber den Umfang dem `director`.

---

### [P3 | Minor | Hoch] Beim reinen Icon-Neubau meldet das Fenster, die Zahlen wuerden neu gelesen

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/firstrun.py` (`what_is_needed`, Fenstertext des
`_Window`)
**Umgebung:** Artefakt, gueltiger Schnappschuss im Cache
(`extract_version` 11 = aktuell), Icon-Pack fehlt

**Reproduktion:**
1. Ein Cache-Verzeichnis anlegen, das ein gueltiges `nightreign_data.json`
   enthaelt, aber kein `icons/`.
2. `NightreignHelper.exe` starten.

**Erwartet:** eine Meldung ueber das, was tatsaechlich gebaut wird.
**Tatsaechlich:** Fenster 460 x 150, Ueberschrift **"Refreshing your game
data"**, darunter **"Re-reading your installation so the numbers are up to
date"** - obwohl `what_is_needed` in diesem Fall nur `"icons"` zurueckgibt
und die Zahlen unangetastet bleiben. Belegt: `nightreign_data.json` behielt
im Sandkasten seinen Zeitstempel (08:10), waehrend `icons/` um 08:22 neu
entstand.

**Analyse:** Der Fenstertext ist fuer den Schnappschuss formuliert und wird
fuer beide Bauschritte gezeigt. Vermutung, nicht geprueft: derselbe Text
erscheint auch bei einer reinen Version-Erhoehung von `ICON_VERSION`, also
bei jedem Nutzer nach einem Update dieser Art.

**Auswirkung:** Der Nutzer wartet rund fuenf Minuten und liest dabei eine
Begruendung, die nicht zutrifft. In Verbindung mit QA-198 (angesagte
"etwa eine Minute") ist das die zweite falsche Erwartung im selben Fenster.

**Vorschlag:** Den Satz aus `what_is_needed` ableiten statt ihn fest zu
schreiben.

---

### Bestaetigt, nicht neu

- **QA-198** (Erstaufbau dauert real rund fuenf Minuten): am Artefakt
  reproduziert. Prozessstart 08:21:21, Kindprozess 08:21:26, Hauptfenster mit
  Titel "Nightreign Helper 1.8.0" beim naechsten Nachsehen um ca. 08:26 -
  und in diesem Lauf war nur der Icon-Pack faellig, nicht der Schnappschuss.
- **QA-181** (Stacking-Rand unbewacht): der Befund betrifft die *Bewachung*,
  nicht das Verhalten. Das Verhalten haelt am Artefakt: 50 von 84 nicht
  stapelbaren Effekten bewegen eine gerankte Zahl, und bei allen 50 ist
  zweimal genau soviel wert wie einmal.
- **QA-191** (Nightfarer-Abdeckung der Beratertests): bestaetigt, Zahl
  praezisiert, siehe Befund oben.

---

## Explorationsprotokoll

Was versucht wurde und was gehalten hat:

1. **SHA-256 des Artefakts** gegen die Vorgabe - stimmt, kein Neubau.
2. **Schritt 0** mit drei Positiv- und drei Gegenproben - alle sechs
   bestanden, danach am laufenden Artefakt ein zweites Mal.
3. **510 Bundle-Eintraege ausgepackt**, 355 PYZ-Module, davon 62 aus
   `nrplanner`/`nrdata`; Bytecode-Vergleich gegen den Quellstand mit
   Positivkontrolle.
4. **Ressourcen im Bundle gezaehlt**: 236 Paramdefs, `data\icon.ico`,
   Qt-Plattform- und Bildformat-Plugins, `python312.dll`.
5. **`_MEIPASS`-Abhaengigkeit gemessen**: mit gesetztem `_MEIPASS` loesen
   `icon_path()` und `defs_dir()` auf; ohne liefern sie `None`. Das ist der
   Unterschied, den ein Test am Quellstand strukturell nicht sieht.
6. **440 Beraterlaeufe** ueber den verpackten Code: 10 Nightfarer x 11 Kelche
   x 2 Ziele, einmal ohne und einmal mit Deep of Night. Gefahren ueber
   `advisorbar.asking_from` - den Weg, den das Fenster geht - plus die zwei
   Felder, die `AdvisorController.ask` selbst einsetzt (Zeilen 203-211).
7. **A4-Stacking** an der Zahl gemessen, nach der der Berater rankt
   (`GoalScore`), nicht am `repr` des Builds. Ein erster Versuch ueber `repr`
   meldete 84 von 84 als doppelt gezaehlt - das war die Quellenliste, nicht
   die Rechnung. Die Positivkontrolle (202 von 206 stapelbaren Effekten
   aendern sich beim Verdoppeln) unterscheidet die beiden Maessungen.
8. **A6** zweifach: im Pruefstand ueber `AdvisorController` mit gezaehlter
   Ereignisschleife, am Artefakt ueber UI Automation, die waehrend des Laufs
   weiter bedient wurde.
9. **A8** dreifach: Zeichenketten des verpackten Codes, erzeugte
   Beratertexte, Fensterabzuege.
10. **Volle Suite** einmal am Ende im frischen Klon: 1257 passed, 9 skipped,
    0 failed, 180,81 s.

---

## Offene Fragen

1. **`AdvisorResult.unknowns` bleibt in allen 440 Laeufen leer**, waehrend
   `not_counted` in 423 Laeufen gefuellt ist. Ist `unknowns` fuer Faelle
   gedacht, die dieser Datensatz nicht enthaelt, oder wird es nirgends
   gefuellt? Frage an den `developer`; A7 ist davon nicht betroffen, weil die
   Nichtwissens-Saetze ueber `not_counted` und die Zeilentexte kommen.
2. **Sind 3,5 s Median und 6,0 s Maximum bei 309 Relikten in Ordnung?**
   Ohne Zielwert kann ich es nicht beantworten. Frage an den `director` bzw.
   den `performance-tuner`.

---

## Beobachtungen

Ohne Nummer, ohne Prioritaet - keines davon macht ein Verhalten falsch oder
verletzt eines der zitierten Kriterien.

- `tests/advisor_cases.py` haelt mit `problem_from_planner` und
  `context_from_planner` eine zweite, eigene Uebersetzung vom Fenster zur
  Beraterfrage; der Docstring sagt selbst, sie sei geschrieben worden, bevor
  `advisorbar.asking_from` existierte. Zwei Uebersetzungen derselben Sache
  koennen auseinanderlaufen, und die Tests wuerden es nicht merken, weil sie
  die eigene benutzen. Ich habe fuer alle Messungen `asking_from` genommen.
- Waehrend meines Laufs lief auf diesem Rechner ein fremder Prozess
  `pytest -q tests/test_wortwahl_oberflaeche.py`; diese Datei gibt es im
  Arbeitsbaum nicht (64 `test_*.py`, `git status` leer). Nur zur Kenntnis,
  falls der Stand doch nicht ueberall eingefroren ist.
- Die Titelleiste des Artefakts erscheint im zweiten Fensterabzug rot; das
  ist die Akzentfarbe des aktiven Fensters von Windows, kein Fehler.

---

## Nicht getestet

- **SmartScreen und Virenscanner** - ohne Browser-Download strukturell nicht
  ausloesbar, wie schon T-113 vermerkt hat.
- **Der Update-Weg** (v1.7.1 -> 1.8.0) - in T-113 geprueft, ich habe mich
  darauf verlassen und nur stichprobenartig gegengeprueft, dass das Artefakt
  aus einem leeren Cache heraus startet.
- **A1, A2, A10-A17** - nicht Gegenstand dieses Auftrags.
- **Der Berater unter Abbruch** (`Cancel` mitten im Lauf) und die
  Ergebnis-Zwischenspeicherung - in `test_advisor_worker.py` gedeckt und
  nicht Teil von A3-A8.
- **Andere Skalierungen und Qt-Stile** - alle Fensterzahlen dieses Berichts
  gelten fuer Windows 10, Fusion-Stil, 100 % Skalierung, logische Pixel
  (L-009).
- **Ein zweiter Rechner** - alle Messungen stammen von dieser Maschine.

---

## QA-Log - Fortschreibung fuer `qa/findings.md`

Bestehende Zeilen bleiben unveraendert; anzuhaengen sind vier neue Zeilen und
drei Statusfortschreibungen. Die IDs vergibt der `director`.

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| (neu) | A6 traegt keinen Zielwert, das Kriterium ist zur Haelfte nicht entscheidbar | P3 | Major | director | Artefakt, 440 Laeufe | offen | 2026-09-08 |
| (neu) | A8 hat keinen Waechter - Sprachregel von keinem Test gehalten | P3 | Major | developer | 3 Suchmasken ueber 71 Testdateien | offen | 2026-09-08 |
| (neu) | A3s Aussage "fuer jeden Nightfarer und jedes Kelch-Layout" in keinem Testfall | P3 | Major | developer | 2 Suchmasken ueber 13 Beraterdateien | offen | 2026-09-08 |
| (neu) | Icon-Neubau meldet "Re-reading your installation so the numbers are up to date" | P3 | Minor | ui-ux-designer | Artefakt, Zeitstempel belegt | offen | 2026-09-08 |
| QA-181 | Stacking-Regel am Rand des Beraters unbewacht | - | - | developer | Artefakt: Verhalten haelt (50/50), Bewachung weiter offen | offen | 2026-09-08 |
| QA-191 | Acht von zehn Nightfarern in keinem Berater-Test | - | - | developer | nachgezaehlt: **sechs** ohne Erwaehnung, einer dynamisch | offen (Zahl praezisiert) | 2026-09-08 |
| QA-198 | Erstaufbau dauert real rund fuenf Minuten | - | - | ui-ux-designer | am Artefakt reproduziert (~5 min, nur Icon-Pack faellig) | offen | 2026-09-08 |

---

## Zusammenfassung (an den director)

**Befunde nach Prioritaet:** P1: 0 · P2: 0 · P3: 4 · P4: 0.

**Gesamturteil: CONCERNS.**

A3, A4, A5, A7 und A8 sind am gebauten Artefakt belegt erfuellt - mit
Stichproben, die breiter sind als der Auftrag verlangt hat (alle zehn
Nightfarer, alle 74 Kelche, beide Zielrichtungen, mit und ohne Deep of Night,
gegen die echten 309 Relikte). Kein P1 und kein P2. **A6 bekommt CONCERNS,
weil sein Zielwert fehlt, nicht weil das Programm etwas falsch macht.**

Die verpackte Fassung verhaelt sich wie der Quellstand: 62 von 62 Modulen
bytecode-identisch, alle Ressourcen im Bundle, der eine `__file__`-Pfad hinter
`_MEIPASS`. Der einzige Verhaltensunterschied, den ich gefunden habe, liegt
nicht im Berater, sondern im Erststart - und der ist als QA-198 und als neuer
Wortlaut-Befund benannt.

**Vor der Freigabe zu entscheiden** (nicht von mir):
1. Bekommt A6 seine Zahl (S11), oder wird A6 gekuerzt?
2. Werden die zwei fehlenden Waechter (A3-Abdeckung, A8-Sprache) vor dem
   Release gebaut, oder wird dieser Lauf als einmaliger Beleg akzeptiert?

**WAIVED vergebe ich nicht.** Wandelt der `director` etwas davon um, trage
ich es mit Eigentuemer, Geltungsbereich und Ablaufdatum ins QA-Log nach.
