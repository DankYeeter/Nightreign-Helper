STATUS: erledigt
AUFTRAG: T-186 — Retest QA-215: steht der Fix, den das Register nicht kennt?
GELESEN: docs/tasks/T-186.md; docs/berichte/T-180-qa-engineer.md (eigener
Vorbericht, Quittung fuer QA-215); qa/findings.md:237 (Tabellenzeile QA-215);
qa/verlauf.md:2353-2368 (Fliesstext QA-215, Herkunft T-159);
tests/test_save_read_in_the_background.py (ganze Datei, Fokus 1000-1115);
nrplanner/app.py:4125-4394 (`_on_save_read`, `load_equipped`); CLAUDE.md
Abschnitt "Projektzeilen fuer jeden Auftrag" (Testbefehl, Datenverzeichnisse);
tests/conftest.py:1-260 (Isolationsmechanik der Suite); `git log -S
LOAD_EQUIPPED_OPENS_WITH` / `git log --oneline` auf
tests/test_save_read_in_the_background.py und Commit f72f93e (Volltext)
GEAENDERT: docs/berichte/T-186-qa-engineer.md (dieser Bericht, neu). Sonst
keine Datei im Arbeitsbaum angefasst — `git status` vor und nach dem Lauf
identisch (nur die von anderer Stelle vorbestehenden Aenderungen an
UI_SPEC.md/UI_SPEC_REGISTER.md, nicht von mir). Ausserhalb des Arbeitsbaums:
`pip install zstandard==0.25.0` in die lokale Python-Umgebung (kein
Projektzustand, siehe Befund unten), ein Git-Klon + eine Ein-Zeilen-Mutation
ausschliesslich unter `…/scratchpad/T-186/clone/`, danach geloescht.
ANNAHMEN: Der Auftrag nennt Commit `1e6bb98`; HEAD stand bei `13cd739`, acht
Commits, davon der letzte zwei reine Doku-Commits (T-185/T-186 anlegen, siehe
`git diff --stat 1e6bb98 13cd739` — nur `docs/tasks/*.md`). Ich habe auf dem
tatsaechlichen Quellstand (`13cd739`) getestet, da er sich im relevanten Code
nicht vom genannten Commit unterscheidet, und das hier vermerkt statt
stillschweigend zu wechseln.
NAECHSTER: director
BLOCKIERT DURCH: nichts

## Ergebnis in Kuerze

**Urteil: behoben.**

Der Test `test_a_takeover_that_works_leaves_load_equippeds_own_sentence`
(`tests/test_save_read_in_the_background.py:1073-1114`) bildet **exakt** den
in QA-215 benannten Fall ab, nicht nur "der Code tut, was er tut":

- **Die Mutation ist identisch.** QA-215 nennt wörtlich: `self.owned_label.setText(note)`
  im Erfolgszweig von `load_equipped`, als No-op. Diese Zeile steht heute bei
  `nrplanner/app.py:4393` (Zeilennummer verschoben, Code identisch).
- **Die Mutation wurde tatsaechlich gebaut und ausgefuehrt**, nicht nur
  gelesen: in einem Klon unter `…/scratchpad/T-186/clone/` wurde exakt diese
  Zeile durch ein `pass` mit Kommentar ersetzt und die Datei im Standardlauf
  (`pytest tests/test_save_read_in_the_background.py`, ohne `-n`) erneut
  ausgefuehrt.
- **Ergebnis der Mutation: 1 failed, 23 passed** — und zwar genau der
  Zielrest:
  ```
  FAILED tests/test_save_read_in_the_background.py::test_a_takeover_that_works_leaves_load_equippeds_own_sentence
  AssertionError: AK-245: the takeover's own sentence is what stands, not the
  note it was written over: '312 relics in USER_DATA000, 1 stored builds'
  assert False
   +  where False = <...>.startswith('Loaded ')
  ```
  Der Anzeigetext bleibt bei der Bestandsnotiz aus `_on_save_read`
  (`nrplanner/app.py:4152`, `"{relic_count} relics in {source}, {n} stored
  builds"`) stehen — exakt das Symptom, das QA-215 beschreibt ("der stehen
  gebliebene Bestandshinweis ist keine Wartezeile, also blieben die drei
  vorherigen Assertions gruen").
- **Die drei aelteren Assertions in derselben Testfunktion (Zeilen
  1106-1109) bleiben unter der Mutation tatsaechlich gruen** — im
  Pytest-Traceback sichtbar: der Fehlschlag tritt erst bei der letzten,
  vierten Assertion (Zeile 1110) auf. Das deckt sich woertlich mit dem
  Registertext ("die drei Assertions, die dieser Fall vorher hatte, blieben
  alle gruen") und ist der staerkste Beleg, dass der neue Test genau die
  Luecke schliesst, die QA-215 benennt, nicht irgendeine andere.
- **Die Erwartung ist nicht aus der mutierten Stelle abgeleitet (L-008 b).**
  `LOAD_EQUIPPED_OPENS_WITH = "Loaded "` (Zeile 1070) ist ein wörtliches
  Literal mit explizitem Kommentar: *"quoted from AK-245 ... and not read out
  of `app.py`"*. Waere die Erwartung stattdessen z. B. durch Aufruf der
  mutierten Funktion selbst berechnet worden, haette der Test die Mutation
  nie gesehen — das ist hier nicht der Fall.
- **Der Test wurde eigens fuer QA-215 angelegt**, nicht zufaellig treffend:
  `git log -S LOAD_EQUIPPED_OPENS_WITH` zeigt genau einen Commit,
  `f72f93e` — Commit-Nachricht: *"test(save): AK-245 bekommt den Waechter,
  den es selbst nennt (QA-215, QA-216)"*, Body zitiert wortgleich die
  Mutation und den Befund.
- **Standardlauf, kein Sonderfall (L-008 a).** Kein Marker, kein `-n`-Zwang,
  keine Bedingung, unter der ein normaler `pytest`-Aufruf diesen Test
  uebersprnge (`game_data` faellt auf einen Cache/eine Datei zurueck, bevor
  es das echte Spiel braucht; der Testfall selbst nutzt keine `installed_game`-
  Fixture).

**Damit ist die entscheidende Frage klar zu beantworten:** Der Test bildet den
Fall aus QA-215 ab — er ist ein echter Wächter gegen genau die genannte
Mutation, kein Test, der nur das aktuelle Verhalten wiederholt.

## Testlaeufe (Zahlen mit Rezept)

Umgebung: Python 3.12.10, pytest 9.1.1, Commit `13cd739` (Quellstand,
Abweichung zu `1e6bb98` s. o. nur Doku), Windows 11.

**Unmutierter Quellstand, Standardlauf, alle drei Datenverzeichnisse
umgelenkt:**
```
NIGHTREIGN_SETTINGS_ORG=DankYeeterT-186
LOCALAPPDATA=…\scratchpad\T-186\localappdata
APPDATA=…\scratchpad\T-186\appdata
pytest tests/test_save_read_in_the_background.py -q
-> 24 passed in 63.44s
```
Nachweis der Umlenkung: `LOCALAPPDATA/NightreignHelper/nightreign_data.json`
und `.../icons` hatten vor und nach dem Lauf identischen mtime-Unixstempel
(`1787592537` bzw. `1787396695`) — kein Schreibzugriff auf den echten
309-Relikte-Bestand. Der reale Registerpfad `HKCU\Software\DankYeeter\
NightreignHelper` (Player-Settings) ist unveraendert; unter der umgelenkten
Organisation `DankYeeterT-186` ist **keine** Registerspur entstanden, weil
`tests/conftest.py:44` `NIGHTREIGN_SETTINGS_ORG` beim Import ohnehin
zwingend auf die suiteneigene Test-Organisation `DankYeeterTests` ueberschreibt
(zusaetzliche, im Testcode fest eingebaute Isolationsschicht) — auch das
gegengeprueft: kein Registerschluessel unter `DankYeeterTests` blieb nach
Lauf-Ende stehen (Session-Fixture `settings_store`/`clear_settings` raeumt
selbst auf).

**Mutierter Klon (nur `…/scratchpad/T-186/clone/`, Commit `1e6bb98`, danach
geloescht), dieselbe Umlenkung, derselbe Befehl:**
```
-> 1 failed, 23 passed in 65.89s
FAILED …::test_a_takeover_that_works_leaves_load_equippeds_own_sentence
```

## Befund: fehlende Testabhaengigkeit blockierte den ersten Lauf

**Adressat:** developer (Environment-Doku), director (Kenntnisnahme)

**Betroffen:** `requirements.txt:3` (`zstandard==0.25.0`), lokale
Python-Umgebung dieser Maschine

**Reproduktion:**
1. `pip show zstandard` vor diesem Lauf -> "Package(s) not found"
2. `pytest tests/test_save_read_in_the_background.py -q` (vor der Installation)
   -> 21 von 24 Tests brechen mit `ModuleNotFoundError: No module named
   'zstandard'` in `nrdata/dcx.py:36` ab, darunter auch der hier zu
   pruefende Test.

**Erwartet:** `requirements.txt` listet `zstandard` als Laufzeitabhaengigkeit;
eine Umgebung, die danach eingerichtet wurde, sollte es haben.
**Tatsaechlich:** Es fehlte in der lokal vorgefundenen Installation (sonst
vollstaendig: PySide6, pytest, pillow vorhanden).

**Analyse:** Vermutlich eine unvollstaendige/veraltete lokale Einrichtung
dieser Maschine, kein Projektfehler — `requirements.txt` selbst nennt die
Version korrekt. Ich habe `pip install zstandard==0.25.0` in die lokale
Umgebung nachgezogen (kein Eingriff in den Projektbaum) und danach normal
weitergetestet.

**Auswirkung:** Ohne diesen Schritt waere der angeforderte Retest an einem
Umgebungsproblem gescheitert, nicht an einer Aussage ueber QA-215 — deshalb
hier dokumentiert statt stillschweigend uebergangen (Abbruchkriterium
"instabile Umgebung", hier aber behebbar und behoben, kein Abbruch noetig).

**Vorschlag:** Kein Code-/Docs-Fix noetig; falls das oefter vorkommt, waere
ein Hinweis im Testbefehl-Abschnitt von `CLAUDE.md` ("vor dem ersten Lauf
`pip install -r requirements-dev.txt`") denkbar — das ist eine
Verfahrensfrage fuer den director, kein Bug.

## Beobachtungen

Der urspruengliche QA-215-Fliesstext nennt die alte Zeilennummer `app.py:4310`
fuer die Mutationsstelle; sie liegt heute bei Zeile 4393 (Code textgleich,
nur verschoben) — reine Zeilendrift durch spaetere Commits, kein inhaltlicher
Unterschied, daher kein eigener Befund.

## Explorationsprotokoll

- Register- und Fliesstext beider betroffener Dateien gelesen (`qa/findings.md`
  Zeile 237, `qa/verlauf.md` Zeilen 2353-2382 vollstaendig samt der
  T-159-Urteilszusammenfassung, die QA-215 als einzigen FAIL nennt).
- Zielzeile im Code gegen den Testdocstring abgeglichen (`grep -n
  "owned_label.setText" nrplanner/app.py`, alle zehn Fundstellen durchgesehen,
  nicht nur die eine erwartete) und die Erfolgszweig-Stelle (4393) anhand des
  umgebenden Codes (Erfolgszweig von `load_equipped`, letzte Zeile vor
  `recompute()`) bestaetigt, nicht nur an der Zeilennummer geraten.
- Herkunft des Tests unabhaengig von der Auftragsbehauptung nachgesucht:
  `git log --oneline` auf die Testdatei und gezielt `git log -S
  LOAD_EQUIPPED_OPENS_WITH` (zwei unabhaengige Suchmasken) — beide fuehren auf
  denselben Commit `f72f93e`, dessen Volltext QA-215 wörtlich zitiert.
- Positivkontrolle durchgefuehrt, nicht nur behauptet: Klon angelegt, exakt
  die im Befund benannte Zeile mutiert, Standardlauf wiederholt, Fehlschlag
  an der erwarteten Stelle mit erwarteter Fehlermeldung beobachtet, und
  gegengeprueft, dass die drei *aelteren* Assertions derselben Funktion dabei
  gruen blieben (sonst waere unklar, ob die neue oder eine alte Assertion die
  Mutation faengt).
- Datenverzeichnis-Umlenkung nachgewiesen durch mtime-Vergleich vor/nach Lauf
  am echten `LOCALAPPDATA\NightreignHelper` (unveraendert) und Registerpruefung
  vor/nach (kein neuer Schluessel unter der echten oder der umgelenkten
  Organisation blieb stehen).
- Aufgeraeumt: Klon geloescht, Scratchpad-Verzeichnisse leer bis auf die
  zwei angelegten (leeren) Umlenkungsordner, kein Server/Prozess gestartet
  (kein QT-Fenster sichtbar, `offscreen`-Platform durch die Suite selbst
  erzwungen), `git status` im Projektbaum vor/nach identisch.

## Offene Fragen

Keine an eine andere Rolle — das Urteil ist mit einer direkten Messung
(Mutationslauf, nicht nur Lesung) belegt.

## Nicht getestet

- Ob AK-245 noch **andere**, nicht in QA-215 benannte tötende Mutationen hat,
  die weiterhin überleben (Scope-Grenze: "Nur QA-215", ausdrücklich im
  Auftrag).
- Die volle Testsuite (Auftrag: "nicht noetig").
- Rendering/Verhalten an einem echten, sichtbaren Fenster (Suite laeuft
  `offscreen`, wie in jedem Lauf dieser Suite).

## QA-Log

Aenderung am Register selbst ist nicht mein Auftrag (Ausnahme aus T-180 galt
nur dort). Zur Uebernahme durch den director:

| ID | Titel | Prioritaet | Adressat | Status | Datum letzter Pruefung |
|---|---|---|---|---|---|
| QA-215 | AK-245 nennt seine toetende Mutation und sie ueberlebt den vollen Testlauf | P2 | developer | **behoben** — Mutationslauf im Klon bestaetigt: `test_a_takeover_that_works_leaves_load_equippeds_own_sentence` (Commit f72f93e) toetet die exakt benannte Mutation (`app.py:4393`, vormals 4310) im Standardlauf; Erwartung unabhaengig vom mutierten Code formuliert (L-008 a/b erfuellt) | 2026-09-12 |
| (kein neuer Fund, Umgebungshinweis) | `zstandard` fehlte in der lokalen Python-Umgebung dieser Maschine, `requirements.txt` nennt es korrekt | P4 | developer/director | behoben (lokal nachinstalliert, kein Projektfehler) | 2026-09-12 |

## Zusammenfassung (an director)

**Befunde:** 0x P1/P2 (Neufunde), 1x P4 (Umgebungshinweis, bereits behoben).
QA-215 selbst wird hier nicht als "Befund", sondern als **Urteil** gefuehrt:
**behoben**.

**Testlauf:** `pytest tests/test_save_read_in_the_background.py` (ohne `-n`,
alle drei Datenverzeichnisse umgelenkt und nachgewiesen) -> **24 passed in
63.44s** am unmutierten Quellstand; **1 failed, 23 passed** an einem gezielt
in einem Klon eingefuegten Gegenbau derselben, in QA-215 benannten Mutation —
das ist der Beleg, den ein gruener Lauf allein nicht liefert.

**Gesamturteil: PASS** fuer die in diesem Auftrag gestellte Frage
("ist QA-215 durch den vorhandenen Code geschlossen?"). Kein Kriterium aus
`GOAL.md` wird hier unmittelbar abgenommen (siehe Auftrag); die Empfehlung an
den `director` ist, die Statuszeile fuer QA-215 in `qa/findings.md` von
"offen" auf "behoben" mit Verweis auf Commit `f72f93e` und diesen Bericht zu
ziehen.
