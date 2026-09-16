# T-126 - Retest der zwei Waechter aus T-123 (qa-engineer)

```
STATUS: erledigt
AUFTRAG: T-126 - Retest der zwei Waechter aus T-123 (QA-204, QA-205)
GELESEN: docs/tasks/T-126.md, docs/berichte/T-123-developer.md,
  docs/berichte/T-114-qa-engineer.md, tests/test_interface_language.py,
  tests/test_advisor_covers_every_chalice.py, tests/conftest.py (game_data,
  Snapshot-Fixtures), tests/advisor_cases.py (Auszuege: deep_templates_for,
  raising_effects, scaling_armament, request_for, context),
  nrplanner/advisor/candidates.py (Zeile 293 Umgebung),
  nrplanner/advisorbar.py (_on_failed, State.FAILED-Rendering),
  nrplanner/advisor/worker.py (Fehlerpfad), nrplanner/firstrun.py
  (ensure_data, _Builder-Fehlerpfad), nrplanner/app.py (main(),
  _toggle_shortcut, rescan_save), nrplanner/shortcut.py (create/remove
  Fehlerrueckgabe), CLAUDE.md, ~/.claude/agents/_rahmen.md
GEAENDERT: docs/berichte/T-126-qa-engineer.md (diese Datei). Im Arbeitsbaum
  nichts (git diff --stat -- nrplanner nrdata tests run.py leer, siehe
  Nachweis unten). Mutation und Vollauf liefen in einem eigenen Klon unter
  .../scratchpad/T-126/clone.
ANNAHMEN: keine unbestaetigten. Wo eine Lesart moeglich war (Severity/
  Likelihood des neuen Befunds), ist das unten begruendet, keine offene
  Annahme.
NAECHSTER: director
BLOCKIERT DURCH: nichts.
```

---

## Eigene Suitezahl

`pytest -q -n auto` im Arbeitsbaum (unveraendert, Stand `ad291e6`):

```
1264 passed, 9 skipped in 155.98s (0:02:35)
```

**Deckt sich exakt** mit der Meldung aus T-123 (1264 passed, 9 skipped,
0 failed). Keine Abweichung, kein eigener Befund an dieser Stelle.

---

## Urteil je Befund

### QA-204 (A8, Sprachwaechter) - **teilweise geschlossen**

**Was haelt:** Zwei unabhaengige Zugaenge - Zeichenkettensuche ueber die
ausgelieferten Quelldateien (`ast`, keine Docstrings) und Fenstertext eines
gebauten `Planner` ueber alle sieben Tabs. Beide sind im Code gelesen,
plausibel konstruiert und decken sich mit T-114s Methode. Die
Positivkontrolle (`test_the_mask_notices_german_when_it_meets_it`) verhindert
eine blinde Maske; `test_the_games_own_words_cannot_trip_the_mask` misst statt
anzunehmen, dass Spieldaten die Maske nicht ausloesen. Das schliesst QA-204s
urspruengliche, woertliche Forderung: "wenigstens ein Fall, der rot wird, wenn
ein deutscher Satz in die Oberflaeche geraet" - den gibt es jetzt, zweifach.

**Was nicht haelt, und das ist der dritte Risikopunkt des Auftrags
("Ausnahmetexte"):** Beide Waechter pruefen **Literale** und **gerenderten
Widget-Text**. Dazwischen liegt eine dritte Textklasse, die keiner von beiden
erreicht: **zur Laufzeit eingesetzter Ausnahmetext (`str(exc)`)**, der in
f-Strings vor die Anzeige gesetzt wird. Fuenf Fundstellen, mit einer zweiten,
unabhaengig formulierten Suchmaske gefunden (`grep -rn "str(exc)\|str(e)\b"`
plus `grep -rn "\{error\}\|\{err\}\|\{exc\}\|\{reason\}"` ueber `nrplanner`):

| Stelle | Pfad zur Anzeige | Ausloeser |
|---|---|---|
| `nrplanner/advisor/worker.py:135` | `advisorbar._on_failed` -> `f"Could not work that out — {reason}."` (`advisorbar.py:230`) | jeder Fehler waehrend eines Beraterlaufs |
| `nrplanner/firstrun.py:147` | `app.py:4398` `QMessageBox.critical(None, "Nightreign Helper", f"Could not read your game:\n\n{error}")` | Fehler beim Erstaufbau |
| `nrplanner/app.py:4406` | direkt, `QMessageBox.critical(None, "Nightreign Helper", str(exc))` | jede Ausnahme beim Laden der Daten, jeder Programmstart |
| `nrplanner/shortcut.py:131,147` | `app.py:2163-2166` `QMessageBox.warning(self, "Start Menu", f"...\n\n{error}")` | **Klick auf den Start-Menue-Knopf** - ein alltaeglicher, nicht exotischer Weg |
| `nrplanner/app.py:3413` | `self.owned_label.setText(f"Save could not be read: {exc}")` | jeder fehlgeschlagene Spielstand-Reread (`rescan_save`, auch beim Start) |

Diese letzte Stelle ist bemerkenswert: sie erzeugt genau die Satzklasse, die
T-114 als Positivkontroll-Beispiel gewaehlt hat ("Die Datei kann nicht
gelesen werden" / "The file could not be read") - nur dass der reale Code den
Suffix aus `exc` roh anhaengt statt ihn selbst zu formulieren.

**Warum keiner der beiden Waechter das faengt:**
- Die Zeichenkettensuche sieht nur Literale im Quelltext; `str(exc)` ist zur
  Laufzeit erzeugter Text und taucht im AST nicht als String-Konstante auf.
  Der umgebende Literal-Rahmen (`"Could not read your game:\n\n"` etc.) wird
  zwar erfasst und ist sauber Englisch - das reicht nicht, weil der Rest des
  Satzes am Rahmen vorbeilaeuft.
- Der Fenstertext-Waechter erreicht nur Text, der beim Bau des Fensters
  tatsaechlich anliegt. Keiner der vier Testfaelle loest einen dieser fuenf
  Fehlerpfade aus (kein kaputter Spielstand, kein fehlgeschlagener
  Erstaufbau, kein Klick auf den Start-Menue-Knopf), also bleibt die Anzeige
  im Normalzustand.

Das widerspricht einer Aussage im Modul-Docstring von
`tests/test_interface_language.py` selbst: "Text, der erst nach einer Aktion
erscheint ... Die Quelltext-Scan sieht die Zeichenkette trotzdem." Das stimmt
fuer eine reine Literal-Fehlermeldung, aber nicht fuer eine, die zur Laufzeit
mit `str(exc)` zusammengesetzt wird - genau der Fall, der an allen fuenf
Stellen tatsaechlich vorliegt.

**Ob das heute tatsaechlich Deutsch anzeigt, habe ich nicht geprueft und kann
ich mit den mir erlaubten Mitteln nicht pruefen:** `str(exc)` ist bei
Python-eigenen Ausnahmen (KeyError, ValueError, AttributeError ...)
grundsaetzlich Englisch, unabhaengig von der Systemsprache. Bei `OSError` und
seinen Unterklassen (Datei gesperrt, kein Zugriff, Pfad nicht gefunden) stammt
die Meldung unter Windows aus `FormatMessageW` und ist **an die
UI-Sprache des Systems gebunden**. Eine deutsche Windows-Installation wuerde
hier deutschen Text produzieren; ich habe das nicht erzwungen (Aendern der
Systemsprache ist ausserhalb der erlaubten Testumgebung und ausserhalb dieses
Auftrags). Das ist deshalb eine **Testbarkeits-Luecke**, kein bestaetigter
A8-Verstoss - genau die Unterscheidung, die der Auftrag verlangt.

**Verdikt:** QA-204 ist fuer seine urspruengliche, woertliche Forderung
geschlossen (es gibt jetzt einen Fall, der bei einem deutschen Satz im
Quelltext oder im gerenderten Fenster rot wird). Fuer die im Auftrag
ausdruecklich benannte dritte Achse - Ausnahmetexte - bleibt die Regel
unbewacht, an fuenf real erreichbaren Stellen, davon eine (Start-Menue-Knopf)
kein Randfall, sondern ein normaler Klick. **Teilweise geschlossen.**

---

### QA-205 (A3, Vollstaendigkeit) - **geschlossen**

**Risikopunkt 1 (geschnittener Vorrat) - was der Sweep beweist und was
nicht:**

Beweist: fuer einen Vorrat, der jede Farbe und jede Tiefe in ausreichender
Zahl bereithaelt, liefert der Berater fuer **alle** 110 Nightfarer/Kelch-Paare
(beide Zielrichtungen, beide Layouts, 440 Laeufe) zwei benannte Richtungen,
besetzt jeden freien Slot mit einem Relikt aus genau diesem Vorrat, in
passender Farbe und Tiefe. Das ist die Luecke, die QA-205 woertlich benannt
hat (T-114: nur `wylder` in den Beratertests, sechs Nightfarer in keinem Fall
erwaehnt) - und die ist geschlossen, mit einem Nachweis staerker als der
urspruengliche Fund verlangt (alle 10 statt nur 1 Nightfarer, alle 74 statt
0 Kelche).

Beweist **nicht**: das Verhalten bei einem Vorrat, der eine Farbe gar nicht
enthaelt oder in dem ein Slot mangels Besitz leer bleiben muesste. A3 sagt
"aus dem Besitz des Spielers", und ein Spieler kann eine Farbe schlicht nicht
besitzen. Der Test kann diesen Fall strukturell nicht sehen, weil
`copies_per_colour` und `colours_relics_come_in` den Vorrat immer so bauen,
dass jeder Slot bedienbar ist. Der `developer` hat das selbst so benannt
(Annahme 2, "An qa-engineer"-Abschnitt) - das ist eine offen gelegte, keine
versteckte Einschraenkung. Ich werte das nicht als Grund, QA-205
wiederzueroeffnen (der urspruengliche Befund war Abdeckung ueber Helden und
Kelche, nicht Vorratsgroesse), sondern als eigenstaendigen, neuen Rand fuer
den director, siehe unten.

**Risikopunkt 2 (110 Paare vs. 74 Kelche) - nachgerechnet, kein
Widerspruch:**

Direkt aus dem Datensatz gelesen (eigener Skriptlauf gegen
`nrplanner.paths.snapshot_path()`, denselben Schnappschuss, den die Suite
benutzt):

```
Helden: 10
Kelche gesamt: 74
gemeinsamer hero_type (Grale): {11}
eigene Kelche je Held: 7 (bei allen 10 Helden gleich)
Grale: 4
Paare (Held x anbietbarer Kelch): 110
```

`110 = 10 * 7 (eigene) + 10 * 4 (Grale je Held angeboten) = 70 + 40`.
`74 = 70 (eigene, ueber alle Helden verschieden) + 4 (Grale, einmal
gezaehlt)`. Beide Zahlen beschreiben **dieselbe** Menge auf zwei Arten -
T-114 zaehlt eindeutige Kelch-Datensaetze, T-123 zaehlt Held/Kelch-Paare, wie
das Fenster sie tatsaechlich anbietet (jeder der vier Grale wird jedem Helden
einzeln angeboten und dabei mit dessen eigenem Kontext gefragt, was fuer den
Berater nicht dieselbe Frage ist). 110 ist der **staerkere** Nachweis, nicht
der schwaechere: er prueft den Gral zehnmal, einmal je Heldenkontext, statt
einmal insgesamt. Kein Widerspruch, kein Befund.

**Risikopunkt 4 (L-008, Bedingung b) - unabhaengig nachgelesen:** die
Erwartungen des Sweeps kommen aus `game_data` (Heldenliste, Kelchliste,
Slot-Farben, Slot-Zahl), aus `model.WHITE_SLOT` und aus im Test gebauten
Relikten mit `handle`-Wiedererkennung - nicht aus `advisor/candidates.py`
oder `advisor/run.py`, den bewachten Stellen. Die Zielrichtungs-Pruefung
vergleicht zwei **verschiedene, nicht leere** Namen statt gegen
`goals.GOALS[id].label` zu pruefen. Die Hilfsfunktionen aus
`tests/advisor_cases.py` (`raising_effects`, `scaling_armament`,
`deep_templates_for`) ziehen ihre Werte aus `nrplanner.model`/`nrplanner
.damage` (Schadensberechnung) und aus dem Datensatz selbst - einem anderen
Teilsystem als dem, das der Waechter bewacht. Bedingung (b) haelt.

**Risikopunkt 4 (L-008, Bedingung a) - selbst nachgestellt, nicht nur
gelesen:** M1 (Recluse unterdrueckt, `candidates.py:293`) im eigenen Klon
angewandt und der **echte Standardbefehl** `pytest -n auto` (volle Suite,
nicht isoliert, nicht `--ignore`) darueber laufen lassen:

```
FAILED tests/test_advisor_covers_every_chalice.py::test_every_nightfarer_and_chalice_is_answered_in_full
FAILED tests/test_advisor_covers_every_chalice.py::test_every_nightfarer_and_chalice_is_answered_in_full_in_deep_of_night
2 failed, 1262 passed, 9 skipped in 170.21s (0:02:50)
```

Das ist staerker als der T-123-Beleg (der isoliert die eine Datei lief und
den Rest separat mit `--ignore`): hier lief die mutierte Fassung **im
Standardlauf mit den neuen Dateien mit drin**, unter `-n auto`, und ging
rot - exakt an den zwei erwarteten Faellen, sonst gruen (1262 = 1264 - 2).
L-008(a) ist damit fuer diese Mutation nicht nur behauptet, sondern von mir
unabhaengig reproduziert.

**Verdikt:** QA-205 ist fuer seinen woertlichen Fund - Abdeckung ueber alle
Nightfarer und Kelch-Layouts - **geschlossen**, mit eigener Gegenprobe im
Standardlauf. Der Vorrats-Rand aus Risikopunkt 1 ist real, aber ausserhalb
dessen, was QA-205 je behauptet hat; er gehoert als eigener, kleinerer Fund
unten und nicht zur Wiedereroeffnung.

---

## Neuer Befund

### [P3 | Major | Mittel] Zur Laufzeit eingesetzter Ausnahmetext (`str(exc)`) unterlaeuft beide A8-Waechter

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/worker.py:135`, `nrplanner/firstrun.py:147`,
`nrplanner/app.py:2165` (`_toggle_shortcut`), `nrplanner/app.py:3413`
(`rescan_save`), `nrplanner/app.py:4406` (`main`)
**Umgebung:** Quellcode-Lesung, keine Ausfuehrung mit fremder
System-UI-Sprache (siehe unten)

**Reproduktion:**
1. `grep -rn "str(exc)\|str(e)\b" nrplanner nrdata` -> 5 Treffer in
   Produktivcode, alle auf einem Pfad zur Anzeige.
2. Zweite, unabhaengig formulierte Maske:
   `grep -rn "\{error\}\|\{err\}\|\{exc\}\|\{reason\}" nrplanner` -> 3
   Treffer, dieselben f-Strings, die den Text vor die Anzeige setzen.
3. Jede der fuenf Stellen bis zu ihrer Anzeige verfolgt (siehe Tabelle oben) -
   keine liegt hinter einem Filter oder einer Uebersetzung.
4. `pytest tests/test_interface_language.py` (beide Waechter, ohne `-n`,
   Gegenprobe der Vorgabe) bleibt gruen, weil keiner der vier Faelle einen
   dieser fuenf Pfade ausloest.

**Erwartet:** Ein Waechter, der A8 "Alle Texte in der Oberflaeche sind
Englisch" pruefen soll, erreicht jeden Text, den ein Nutzer im Fenster lesen
kann - auch Fehlertexte.
**Tatsaechlich:** Text, der aus `str(exc)` gebildet wird, erreicht weder die
Zeichenkettensuche (kein Literal) noch den Fenstertext-Lauf (keiner der vier
Faelle loest einen dieser Fehlerpfade aus).

**Analyse:** Bei python-eigenen Ausnahmen (KeyError, ValueError,
AttributeError) ist `str(exc)` unabhaengig von der Systemsprache Englisch.
Bei `OSError`-Unterklassen (Datei gesperrt, kein Zugriff, Pfad fehlt) stammt
die Meldung unter Windows aus `FormatMessageW` und folgt der UI-Sprache des
Systems - auf einer deutschsprachigen Windows-Installation waere das
deutscher Text. Ich habe das **nicht erzwungen** (Systemsprache aendern liegt
ausserhalb der erlaubten Testumgebung dieses Auftrags); das ist deshalb eine
**Testbarkeits-Luecke**, kein bestaetigter A8-Verstoss, und wird entsprechend
nicht als Programmfehler ab QA-211 gemeldet, sondern als das, was es ist.

**Auswirkung:** `nrplanner/app.py:3413` (`rescan_save`, Fehler beim Lesen des
Spielstands) und `nrplanner/app.py:2165` (Klick auf den Start-Menue-Knopf)
sind keine exotischen Pfade - ein gesperrter Spielstand (das Spiel schreibt
gerade) oder ein Rechteproblem im Start-Menue sind Situationen, die ein Nutzer
auf einer deutschen Windows-Installation real treffen kann. Genau die
Positivkontroll-Formulierung von T-114 und `test_interface_language.py`
("Die Datei kann nicht gelesen werden" / "The file could not be read")
beschreibt exakt diesen Fall - nur dass der reale Code den zweiten Teil des
Satzes ungefiltert aus dem Betriebssystem uebernimmt.

**Vorschlag:** Entweder `str(exc)` durch eine feste, englische Formulierung
plus `exc.__class__.__name__` ersetzen (kein OS-Text mehr in der Anzeige),
oder die fuenf Stellen bewusst als Ausnahme dokumentieren und einen Testfall
ergaenzen, der einen dieser Fehlerpfade erzwingt (z. B. eine gesperrte
Save-Datei) und pruefy, dass die Anzeige die Maske nicht ausloest. Die
Entscheidung, ob das vor oder nach dem Release geschieht, liegt beim
director.

---

## Beobachtungen

Keine ohne Prioritaet ueber das oben Gesagte hinaus - beide Waechter sind
sauber gebaut, gut dokumentiert und ihre Docstrings benennen die meisten
eigenen Grenzen zutreffend; nur die eine Zeile ueber "Text nach einer Aktion"
trifft auf den Ausnahmetext-Fall nicht zu, siehe Befund oben.

---

## Explorationsprotokoll

1. Beide Testdateien vollstaendig gelesen (Code, nicht nur Bericht).
2. Eigene volle Suite `pytest -q -n auto` im Arbeitsbaum: 1264 passed,
   9 skipped, 0 failed, 155,98 s - deckt sich mit T-123.
3. Datensatz direkt gelesen (`nrplanner.paths.snapshot_path()`, derselbe
   Schnappschuss wie die Suite): 10 Helden, 74 Kelche, ein gemeinsamer
   `hero_type` (11), 110 Paare - rechnerisch nachvollzogen und mit T-114s
   74 in Deckung gebracht.
4. Eigener Klon in `.../scratchpad/T-126/clone` (Stand `ad291e6`, `git
   clone .`), M1 (Recluse-Unterdrueckung) angewandt, **echter Standardbefehl**
   `pytest -q -n auto` (volle Suite, nicht isoliert) darueber: 2 failed,
   1262 passed, 9 skipped, 170,21 s - rot genau an den zwei erwarteten
   Faellen, sonst unveraendert. Staerkerer Nachweis fuer L-008(a) als der
   T-123-Bericht selbst zeigt.
5. Quellcode-Lese-Suche nach Wegen, auf denen Text an den beiden Waechtern
   vorbeikommt (`str(exc)`-Muster, `{error}`/`{err}`/`{exc}`/`{reason}`-Muster,
   `QMessageBox`/`QAction`/`QMenu`-Suche in `app.py`) - fuenf Fundstellen,
   siehe Befund. Kein `QAction`/`QMenu` im Code gefunden, also keine
   Menuepunkte, die dem Fenstertext-Scan entgehen wuerden (er sucht ohnehin
   nur `QWidget`-Kinder; `QAction` ist keines, war aber nicht vorhanden).
6. `git status` und `git diff --stat -- nrplanner nrdata tests run.py` vor
   und nach dem Lauf im Arbeitsbaum geprueft: leer, keine eigene Aenderung.

Keine der drei Datenverzeichnis-Umlenkungen war fuer diesen Auftrag noetig:
kein Programm ausserhalb der Suite gestartet, nur `pytest` (im Arbeitsbaum
und im eigenen Klon), das laut T-123 seine QSettings-Umlenkung selbst
mitbringt (`tests/conftest.py`), und der gelesene Spielstand/Schnappschuss
blieb unveraendert (nur `json.loads`/`pytest`-Lesezugriffe, keine Schreibpfade
angefasst).

---

## Offene Fragen

Keine, die diesen Auftrag blockieren. Eine Frage an den `director`: soll der
Vorrats-Rand aus QA-205/Risikopunkt 1 (Sweep gegen einen immer ausreichenden,
gebauten Vorrat statt gegen eine realistisch knappe Ausstattung) als eigener,
neuer Befund aufgenommen werden, oder gilt die vom `developer` dokumentierte
Annahme 2 als hinreichende Abgrenzung von A3?

---

## Nicht getestet

- Die uebrigen vier Mutationen (M2-M6) wurden **nicht** von mir eigenstaendig
  nachgestellt - nur gelesen und gegen den Code plausibilisiert (siehe
  Bedingung-b-Pruefung oben). Retest-Modus verlangt keine vollstaendige
  Neupruefung; M1 als Stichprobe unter dem echten Standardbefehl war die
  gezielte Verstaerkung des im Auftrag benannten Risikopunkts 4a.
- Ob `str(exc)` auf einer deutschsprachigen Windows-Installation tatsaechlich
  deutschen Text erzeugt - haette eine Aenderung der System-UI-Sprache
  verlangt, ausserhalb der erlaubten Testumgebung dieses Auftrags.
- Linter/Statik ausserhalb dessen, was der `developer` in T-123 schon
  vermerkt hat (kein Linter im Projekt konfiguriert) - nicht erneut gepruefr.

---

## QA-Log - Fortschreibung fuer `qa/findings.md`

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-204 | A8 hat keinen Waechter - Sprachregel von keinem Test gehalten | - | Major | developer | 2 neue Waechter gelesen, eigene Suite 1264/9/0, Ausnahmetext-Luecke selbst gefunden (5 Stellen, 2 Suchmasken) | **teilweise behoben** | 2026-09-08 |
| QA-205 | A3s Aussage "fuer jeden Nightfarer und jedes Kelch-Layout" in keinem Testfall | - | Major | developer | Datensatz nachgerechnet (110=70+40, 74=70+4, kein Widerspruch), M1 im eigenen Klon unter echtem Standardbefehl rot reproduziert | **behoben** | 2026-09-08 |
| (neu) | Zur Laufzeit eingesetzter Ausnahmetext (`str(exc)`) unterlaeuft beide A8-Waechter | P3 | Major | developer | 5 Fundstellen, 2 unabhaengige Suchmasken, Code bis zur Anzeige verfolgt | offen | 2026-09-08 |

Bestehende Zeilen (QA-181, QA-191, QA-198 u. a.) unveraendert, siehe
`docs/berichte/T-114-qa-engineer.md`.

---

## Zusammenfassung (an den director)

**Befunde nach Prioritaet:** P1: 0 · P2: 0 · P3: 1 · P4: 0.

**Gesamturteil: CONCERNS.**

QA-205 ist geschlossen und von mir unabhaengig verstaerkt (Mutation im
eigenen Klon, echter Standardbefehl, nicht nur die isolierte Datei). QA-204
ist teilweise geschlossen: die urspruengliche, woertliche Luecke ("keiner der
71 Testdateien wird bei Deutsch rot") ist zu - aber eine dritte Textklasse,
die der Auftrag ausdruecklich benannt hat (Ausnahmetexte), bleibt an fuenf
real erreichbaren Stellen unbewacht, darunter zwei alltaeglichen (Klick auf
den Start-Menue-Knopf, fehlgeschlagener Spielstand-Reread). Kein P1, kein P2 -
der Fund ist eine Testbarkeits-Luecke, kein bestaetigter, reproduzierter
A8-Verstoss, deshalb CONCERNS statt FAIL.

**Vor der Freigabe zu entscheiden** (nicht von mir):
1. Wird der neue P3-Fund (Ausnahmetext) vor dem Release geschlossen, oder
   zurueckgestellt?
2. Gilt der Vorrats-Rand aus QA-205/Risikopunkt 1 als eigener Fund oder als
   hinreichend durch Annahme 2 des `developer` abgedeckt (offene Frage oben)?

**WAIVED vergebe ich nicht.**
