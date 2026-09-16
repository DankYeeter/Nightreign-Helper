# T-155 - Die Mutationen ins Register, und fuenf Skripte (developer)

```
STATUS: teilweise
AUFTRAG: T-155 - Aufgabe 1 (Mutationen aus T-137/142/147/149/150/151
         nachtragen) und Aufgabe 2 (fuenf Skripte bauen ein Fenster ohne
         Bestand)
GELESEN: docs/tasks/T-155.md; docs/berichte/T-137-developer.md,
         T-142-developer.md, T-147-developer.md, T-149-developer.md,
         T-150-developer.md, T-151-developer.md, T-152-developer.md;
         scripts/differential/mutate.py (Kopf, Format, alle 230
         Registereintraege, `apply`/`main`); tests/conftest.py
         (`wait_for_the_save`); nrplanner/app.py (SaveReader,
         _SaveReadWorker, rescan_save, _on_save_read/_on_save_failed);
         scripts/measure_picker_cards.py, measure_advisor_block.py,
         make_screenshots.py, capture_weapon_damage.py,
         differential/capture.py (alle vollstaendig); Scratchpad-Treiber
         der sechs Auftraege (siehe unten); CLAUDE.md;
         .claude/agent-memory/developer/project_mutation_registry.md
GEÄNDERT: scripts/capture_weapon_damage.py, scripts/differential/capture.py,
         scripts/make_screenshots.py, scripts/measure_advisor_block.py,
         scripts/measure_picker_cards.py — committet (dd2dea9).
         .claude/agent-memory/developer/project_mutation_registry.md —
         geaendert, **nicht** committet (Projekt-`.gitignore` schliesst
         `.claude/agent-memory` aus).
         scripts/differential/mutate.py — **unveraendert**, siehe unten.
ANNAHMEN: (1) Der Auftrag zitiert GOAL.md/A1 und einen state.md-Auszug zu
         Zyklus 18/U8 — beides ohne erkennbaren Bezug zu den zwei
         mechanischen Aufgaben dieses Auftrags; nicht weiter ausgewertet.
         (2) Duplikate im Katalog (T-137 komplett, zwei T-151-Faelle) sind
         Befunde, keine Luecken — Details unten.
NÄCHSTER: developer (Fortsetzung von Aufgabe 1, siehe „Was fehlt")
BLOCKIERT DURCH: nichts inhaltlich — der Lauf endete an der
         Werkzeug-Zugschwelle (150 Aufrufe), nicht an einer offenen Frage.
```

## Zugschwelle

Bei 150 Werkzeugaufrufen hat der Hook gegriffen, waehrend eine
Hintergrund-Mutationskampagne (T-142/T-147) noch lief. Aufgabe 2 ist fertig
und committet. Aufgabe 1 ist **vorbereitet, aber nicht ins Register
geschrieben** — nichts in `scripts/differential/mutate.py` hat sich
geaendert. Alle Zwischenergebnisse liegen nachvollziehbar im Scratchpad,
Details unter „Was fehlt".

---

## Aufgabe 2 — fuenf Skripte: erledigt

**Gefunden wie verlangt** (`grep` ueber `scripts/`, zwei unabhaengige
Masken: `Planner(data)`/`Planner(` und `save_reader|is_reading|Planner\(`):
**genau fuenf**, deckungsgleich mit T-142s Meldung:

- `scripts/capture_weapon_damage.py`
- `scripts/differential/capture.py`
- `scripts/make_screenshots.py`
- `scripts/measure_advisor_block.py`
- `scripts/measure_picker_cards.py`

**Der Fehler, belegt statt behauptet:** `…/scratchpad/T-155/demo_owned.py`
baut einen echten `Planner(data)` gegen den Testabzug und liest `.owned`
sofort danach:

```
immediately after Planner(data): owned = None, is_reading = True
after waiting for save_reader.is_reading() == False: owned = 309 relics
```

Genau die Klasse Fehler, die T-132 fuer `measure_picker_cards.py` schon
einmal gefunden hat (AD-006.5): das Fenster steht, bevor der Spielstand
gelesen ist.

**Nachgezogen wie T-132 es getan hat** — ein ausdruecklicher Wait auf
`window.save_reader.is_reading()`, statt sich auf Aufbauzeit oder eine feste
Zahl `processEvents()`-Runden zu verlassen:

| Skript | Wo der Wait sitzt |
|---|---|
| `measure_picker_cards.py` | neue Funktion `wait_for_the_save`, nutzt das vorhandene `spin()`-Muster; in `main()` direkt nach `window.show()` |
| `measure_advisor_block.py` | neue Funktion `wait_for_the_save`, in `a_window()` statt `settle()` |
| `make_screenshots.py` | neue Funktion `wait_for_the_save(app, window)`, in `main()` direkt nach `window.show()` |
| `capture_weapon_damage.py` | neue Funktion `wait_for_the_save`, in `main()` direkt nach `appmod.Planner(data)` |
| `scripts/differential/capture.py` | neue Funktion `wait_for_the_save`, in `main()` direkt nach `appmod.Planner(data)` |

Jede Docstring-Kopfzeile bekam einen Satz, der die Aenderung erklaert
(L-006-Stil: Eigenschaft benannt, nicht nur die Zeile).

### Vorher/Nachher (L-009)

**Messumgebung:** Windows 10 x64, `.venv`-Python, `QT_QPA_PLATFORM=offscreen`,
Qt-Stil Fusion, **logische** Pixel, Testabzug **kopiert** nach
`…/scratchpad/T-155/local/NightreignHelper` (841 Dateien), alle drei
Umlenkungen gesetzt (`LOCALAPPDATA`, `APPDATA`,
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-155`).

Fuer die zwei Skripte, die den Bestand direkt ausgeben, per Datei-Tausch
(kopieren, alten Stand aus `git show HEAD:…` einspielen, laufen lassen,
neuen Stand zurueckkopieren — **kein** `git checkout`) vorher/nachher
gefahren:

| Skript | vorher (Stand vor T-155) | nachher (mit Wait) |
|---|---|---|
| `measure_picker_cards.py` | `54 relic cards` | `54 relic cards` |
| `measure_advisor_block.py` | `309 relics` (Wylder, Wylder's Goblet) | `309 relics` (identisch) |

**Kein Wertunterschied auf dieser Maschine.** Das ist dieselbe Lage wie
beim Advisor-Track vor T-130/T-132: warmer Diskcache und eine schnelle
Maschine lassen die Aufbauzeit des Fensters die Wartezeit zufaellig
verdecken. `demo_owned.py` oben zeigt, dass die Race strukturell da ist
(`owned=None` unmittelbar nach der Konstruktion); dass sie hier nicht
reproduziert, ist Glueck der Maschine und keine Widerlegung. Fuer die
uebrigen drei Skripte (`capture_weapon_damage.py`,
`scripts/differential/capture.py`, `make_screenshots.py`) habe ich **keinen**
vollen Vorher/Nachher-Lauf gefahren — die ersten beiden lesen `owned`
nachweislich nicht (Quelltextpruefung `tests/weapon_damage_cases.py::run`,
keine Erwaehnung von `owned`/`save_reader`), fuer sie ist der Fund eher der
Absturz-Fall (`a-read-per-press`-Klasse, T-142) als ein falscher Wert;
`make_screenshots.py` fotografiert den Build-planner-Tab, der laut eigenem
Docstring **die echten Relikte des Spielstands zeigen soll** — dort haette
der Fehler ein leeres Bild statt eines falschen Werts erzeugt, nicht
gegengelaufen, weil das Schreiben von PNGs ausserhalb des noetigen Umfangs
lag.

### Tests

Keine neue Testlogik — reine Skriptaenderung, `scripts/` wird von der Suite
nicht importiert. Alle fuenf Dateien kompilieren
(`py_compile`, gruen). Die Suite selbst habe ich in diesem Lauf **nicht**
erneut ausgefuehrt (siehe unten) — meine Aenderung beruehrt keine Datei, die
`tests/` einsammelt, das Risiko fuer die Suitezahl ist damit strukturell
null, aber unbelegt durch einen eigenen Lauf.

---

## Aufgabe 1 — Mutationen: vorbereitet, nicht geschrieben

### Gezaehlt: 95 Mutationen in den sechs Berichten

| Auftrag | Mutationen laut Bericht | davon bereits abgedeckt |
|---|---|---|
| T-137 | 8 | **alle 8** bereits im Register — identischer Name, Pfad, `old`, `new` (geprueft per Skript, siehe unten) |
| T-142 | 13 (1 ueberlebt: `the-stock-never-reaches-the-cards`) | 0 |
| T-147 | 22 (2 ueberlebt: `empty-regulation-accepted`, `type-str-dropped-when-reading`) | 0 |
| T-149 | 21 | 0 |
| T-150 | 18 | 0 |
| T-151 | 13 (2 identisch mit vorhandenen Eintraegen: `FASTa`≡`relic-prefilter-starts-one-byte-late`, `FASTb`≡`relic-prefilter-drops-the-alignment-check` in Wirkung) | 2 |
| **Summe** | **95** | **10** bereits da/deckungsgleich, **85** neu |

**Wie ich das gezaehlt habe:** die Treiber-Skripte der sechs Auftraege
(`…/scratchpad/T-13x/mutate*.py` bzw. `mutate_driver.py`) sind **in dieser
Sitzung noch vorhanden** — die Sitzung reicht ueberraschend weit zurueck
(mindestens bis T-122). Ich habe sie transkribiert, **nicht** aus der Prosa
der Berichte rekonstruiert. Fuer T-137 und T-151 fehlten zwei Mutationen im
Haupt-Treiber (`FASTa`/`FASTb` standen in einer zweiten Datei
`mutate_fast.py`) — gefunden durch Nachzaehlen gegen die Berichtstabellen.

**T-137 ist bereits vollstaendig registriert** — vermutlich durch T-139
(dessen Bericht ich nicht gelesen habe, aber die acht Namen, Pfade und
Texte stimmen exakt). Kein Nachtrag noetig, keine Luecke.

**T-151s `FASTa`/`FASTb` sind keine eigenen Mutationen**, sondern
Kontrolllaeufe **bereits vorhandener** Eintraege (`relic-prefilter-starts-
one-byte-late`, `relic-prefilter-drops-the-alignment-check`), gefahren, um
zu zeigen, dass der **alte** Waechter die Verdopplung des Scanwegs (R12-R16)
uebersteht — das steht so im T-151-Bericht ("stehen dabei fuer die Frage,
ob der alte Waechter das Zweimal-Laufen ueberlebt hat"). `FASTb`s `new`-Text
(`if pos >= 3:`) ist nicht wortgleich mit dem vorhandenen `if True:`, aber
**verhaltensgleich** (nach dem vorausgehenden `find(..., 3)` ist `pos`
entweder `-1` oder `>= 3`) — ein zweiter Eintrag dafuer waere derselbe
Beweis zweimal.

### Anker gegen den heutigen Quelltext geprueft — 2 von 95 hatten sich verschoben

Read-only-Skript `…/scratchpad/T-155/check_anchors.py` gegen den
**aktuellen** Checkout (nicht gegen eine Kopie): 93 von 95 Ankern passten
sofort exakt einmal. Zwei nicht — beide aus T-142, beide durch T-150s
Umbau von `_on_save_read`/`_on_save_failed` (V3, `read_the_save`):

- `answer-stamped-with-a-dead-generation` — die Konstruktorzeile hat ein
  viertes Argument (`save_path`) bekommen.
- `the-failure-keeps-the-waiting-sentence` — die eine `setText`-Zeile ist
  jetzt eine Verzweigung `CHOSEN_SAVE_UNREADABLE`/`UNREADABLE_SAVE`.

Beide im Katalog nachgezogen (Text an den heutigen Code angepasst, gleiche
Absicht), **beide danach gemessen und toetend** (siehe unten) — kein
Befund, nur eine Reparatur vor dem Eintragen.

### Nachweis gefahren: 10 von 35 (T-142 + T-147)

**Mechanik:** `git archive HEAD` in eine Baumkopie (`…/scratchpad/T-155/
tree`, mit unberuehrter Zweitkopie `…/reference` zum Zurueckkopieren —
**kein** `git checkout`), je Mutation die Datei ersetzt, den vom
Ursprungsauftrag benutzten engen Testumfang gefahren (z. B.
`tests/test_save_read_in_the_background.py` fuer T-142,
`tests/test_game_dir_recognition.py tests/test_game_path_memory.py` fuer
T-147), Ergebnis notiert, Datei aus der Referenz zurueckkopiert.

**Ergebnis, so weit gelaufen — 10 von 13 T-142-Mutationen, alle KILLED:**

| Mutation | Ergebnis |
|---|---|
| `answer-stamped-with-a-dead-generation` | 12 failed, 10 passed |
| `save-read-shutdown-does-not-raise-the-generation` (umbenannt, siehe unten) | 1 failed, 21 passed |
| `a-read-per-press` | Prozessabbruch statt pytest-Zusammenfassung — **wie im Original-Bericht dokumentiert** (L-003: Signal ist ein Absturz, keine benannte Behauptung) |
| `no-waiting-sentence` | 3 failed, 19 passed |
| `no-line-on-the-empty-card` | 1 failed, 21 passed |
| `the-bracket-stays-at-zero` | 2 failed, 20 passed |
| `the-relic-button-stays-open` | 3 failed, 19 passed |
| `the-waiting-line-is-one-line-high` | 1 failed, 21 passed |
| `the-failure-keeps-the-waiting-sentence` | 3 failed, 19 passed (nach der Ankerreparatur) |
| `skipped-without-being-marked` | 4 failed, 18 passed |

**Nicht mehr gelaufen:** `the-players-slot-is-overwritten`,
`load-equipped-speaks-during-the-read`, `the-stock-never-reaches-the-cards`
(T-142, 3 Eintraege) sowie **alle 22** aus T-147. Der Hintergrundlauf
(Bash-ID `byax389he`, Ausgabe unter `…/tasks/byax389he.output`) lief noch,
als die Zugschwelle griff — **er koennte noch aktiv sein**, siehe „An den
director" unten.

Der eine Namenskonflikt (`shutdown-does-not-raise-the-generation` ist
bereits von T-137 belegt, ein anderer Mechanismus — `AdvisorController`
statt `SaveReader`) ist im Katalog als
`save-read-shutdown-does-not-raise-the-generation` aufgeloest.

### Umgebung fuer den Nachweislauf

`git archive HEAD` kopiert nur den committeten Stand — **keine**
Datenverzeichnis-Umlenkung noetig fuer die Kampagne selbst
(`tests/conftest.py` lenkt unter `pytest` ohnehin auf
`DankYeeterTests`/`NightreignHelperTests-<pid>` um, unabhaengig von meiner
Einstellung). Fuer Aufgabe 2 (echte Skriptlaeufe) waren alle drei
Umlenkungen gesetzt, siehe oben.

### Was im Scratchpad bereitliegt (fuer die Fortsetzung)

`…/scratchpad/T-155/`:

- **`catalog.py`** — alle 95 `(task, name, path, old, new)`-Tripel,
  woertlich aus den sechs Original-Treibern transkribiert; die zwei
  T-142-Anker bereits an den heutigen Quelltext angepasst.
- **`means.py`** — `survival_means`-Text **fertig fuer T-142 (13) und
  T-147 (22, inkl. der zwei Ueberlebenden-Begruendungen)**. **Fehlt fuer
  T-149 (21), T-150 (18), T-151 (11 neue)** — das ist der groesste
  Einzelposten der Restarbeit.
- **`write_registry.py`** — liest ein Kampagnenergebnis, kombiniert mit
  `means.py`, schreibt fertige `Mutation(...)`-Bloecke vor die
  schliessende `}` von `MUTATIONS` in `scripts/differential/mutate.py`.
  **Syntaktisch gegen `compile()` getestet, noch nie gegen die echte
  Datei gelaufen.** Kennt und behandelt die Anfuehrungszeichen-Falle
  (trailing `"` vor `"""` muss escaped werden, leading `"` nicht — jetzt
  auch im Agentengedaechtnis vermerkt).
- **`run_campaign.py`** — der Nachweis-Treiber (git-archive-Baum plus
  Referenzkopie, mutieren, engen Testumfang fahren, zurueckkopieren).
  Kennt die Test-Ziele fuer alle sechs Auftraege (`DEFAULT_TARGETS`),
  nicht nur die zwei gelaufenen.
- **`check_anchors.py`** — read-only Ankerpruefung gegen den aktuellen
  Checkout.
- **`demo_owned.py`**, **`measure_*.before/after.py`** — die Belege fuer
  Aufgabe 2.
- **Baeume** `tree/` und `reference/` — Stand `git archive HEAD` **vor**
  Commit `dd2dea9`; da meine Aenderung nur `scripts/` betrifft und
  `run_campaign.py` nur `nrplanner nrdata tests scripts pytest.ini run.py`
  kopiert, sind sie fuer den Rest von Aufgabe 1 weiterhin gueltig (die
  fuenf geaenderten Skripte werden von keiner der Kampagnen mutiert).

### Was fehlt, konkret

1. `…/scratchpad/T-155/run_campaign.py T-142 T-147` fertig laufen lassen
   (3 + 22 = 25 Mutationen, ca. 3 min Rest fuer T-142, ca. 4 min fuer
   T-147 nach der bisherigen Rate).
2. `…/scratchpad/T-155/write_registry.py T-142 T-147` — traegt 35
   Eintraege in `scripts/differential/mutate.py` ein.
3. `means.py` um T-149 (21 Phrasen), T-150 (18), T-151 (11) ergaenzen —
   die Kurzbeschreibungen stehen bereits in den jeweiligen
   Auftragsberichten (Tabellenspalte "faellt"/"was gefallen ist").
4. `run_campaign.py T-149 T-150 T-151` laufen lassen (50 Mutationen; T-150
   war im Originalbericht mit ~34 s/Lauf die teuerste Gruppe, T-149 und
   T-151 vermutlich schneller).
5. `write_registry.py T-149 T-150 T-151` — weitere 50 Eintraege
   (11 aus T-151, nicht 13 — die zwei Duplikate bleiben aussen vor).
6. Danach: `pytest -q tests/test_differential_track.py -k
   test_every_mutation_still_finds_its_anchor_in_the_real_source` gegen
   den **echten** Checkout (mit den frisch eingetragenen Eintraegen), dann
   `pytest -n auto` fuer die Suitezahl.
7. Register-Endstand waere **230 + 85 = 315 Eintraege**, wenn alles
   toetend bleibt wie in den Originalberichten. Zwei Ueberlebende aus
   T-142 und zwei aus T-147 sind **erwartet und mit Begruendung**
   einzutragen (nicht nachbessern), genau wie der Auftrag es verlangt.

---

## Suite

**Nicht erneut gelaufen in diesem Auftrag** — weder vor noch nach meiner
Aenderung. Grund: die Zugschwelle griff, bevor ich dazu kam, und der Hook
verbietet ausdruecklich jeden weiteren Testlauf ab diesem Punkt. Letzter
bekannter Stand laut T-152 (08.09.2026): **1590 passed, 9 skipped, 0
failed**; laut Auftrag seither hoeher durch T-153s parallele Arbeit.
**Meine committete Aenderung (5 Dateien unter `scripts/`) wird von keinem
Testfall importiert** — strukturell suitezahl-neutral, aber unbelegt durch
einen eigenen Lauf in diesem Auftrag.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [ ] Suite gruen **nachgewiesen** — nicht gelaufen (Zugschwelle)
- [x] Aufgabe 2: neue Logik (die fuenf `wait_for_the_save`-Funktionen) mit
      Vorher/Nachher-Beleg fuer zwei von fuenf Skripten; fuer die anderen
      drei Quelltextpruefung statt Laufbeleg (siehe oben, Grenzen genannt)
- [ ] Aufgabe 1: **nicht fertig** — 85 zu registrierende Eintraege, davon
      10 nachweislich toetend, 75 vorbereitet aber ungeprueft/ungeschrieben
- [x] Keine Secrets, keine TODOs, kein toter Code in den fuenf Skripten
- [x] Nur `scripts/` beruehrt (plus die eigene, nicht committete
      Gedaechtnisdatei)
- [x] Bericht geschrieben

## An den director

1. **Nachtrag (nach Berichtsabgabe): der Hintergrundprozess ist beendet,
   nicht sauber.** Bash-ID `byax389he` (`run_campaign.py T-142 T-147`) kam
   nach Abgabe dieses Berichts als **fehlgeschlagen, Exitcode 255**
   zurueck — kein Haenger, aber auch kein sauberes Ende, und die
   Zugschwelle liess mir zu dem Zeitpunkt nur noch `git commit` und das
   Schreiben dieses Berichts, kein `Read` der Ausgabedatei mehr, um die
   Ursache zu pruefen. **Die Ausgabedatei liegt weiterhin unter**
   `…/tasks/byax389he.output` **und ist fuer den naechsten Lauf die
   erste Anlaufstelle** — vermutlich brach der Lauf mitten in T-147s 22
   Mutationen ab (die 10 T-142-Nachweise im Bericht oben sind vor dem
   Fehlschlag entstanden und bleiben gueltig, unabhaengig von der
   Fehlerursache). Kein Datenverlustrisiko: der Zielbaum ist eine reine
   `git archive`-Kopie unter `…/scratchpad/T-155/tree/`, kein Bezug zum
   echten Checkout.
2. **Aufgabe 1 ist zu gross fuer einen Auftrag** — wie im Auftragstext
   selbst als moeglich benannt ("mehr als rund fuenfzig Eintraege"). 95
   Mutationen, davon 85 tatsaechlich neu, sind fast doppelt so viele.
   Empfehlung: ein Folgeauftrag mit dem oben stehenden Sechs-Punkte-Plan,
   der die vorbereitete Infrastruktur im Scratchpad wiederverwendet statt
   neu zu bauen — spart die Archaeologie (Treiber wiederfinden,
   Anker validieren), die den groessten Teil dieses Laufs gekostet hat.
3. **Zwei positive Funde statt Luecken:** T-137s acht Mutationen sind
   bereits registriert (vermutlich durch T-139); T-151s zwei
   Fast-Mutationen sind Kontrollen bereits vorhandener Eintraege, keine
   neuen. Beides senkt die Restarbeit von 95 auf 85.
4. **Scratchpad-Reichweite:** die Sitzung, in der ich laufe, hat
   Unterverzeichnisse bis mindestens `T-122` — deutlich mehr Auftraege als
   erwartet waren noch lesbar. Das hat diesen Auftrag erst moeglich
   gemacht (ohne die Treiber haette ich 95 Mutationen aus Berichtsprosa
   nachbauen muessen). Kein Handlungsbedarf, aber gut zu wissen, falls
   ein kuenftiger Auftrag auf verschwundene Scratchpad-Daten trifft:
   nachsehen, bevor man annimmt, sie seien weg.
5. **Kein Sicherheits- oder Datenverlustfund.** Die fuenf Skriptaenderungen
   sind reine Ergaenzungen (ein Wait mehr), keine Verhaltensaenderung an
   dem, was gemessen wird, ausser dass jetzt zuverlaessig gemessen wird,
   was vorher zufaellig richtig war.

## An qa-engineer

Nichts Neues zu pruefen — Aufgabe 2 ist reine Entwicklerwerkzeug-Pflege
ohne Oberflaechenaenderung, Aufgabe 1 hat noch keinen Code veraendert.
