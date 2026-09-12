# T-137 — U9 (`shutdown`) und U10 (W8) — developer

```
STATUS: erledigt
AUFTRAG: T-137 — U9 und U10: der `shutdown`-Ausgang und sein Waechter
GELESEN: docs/tasks/T-137.md · ARCHITECTURE.md Nachtrag X (X-0 bis X-3, Zeilen
  4952-5290) · UI_SPEC.md Abschnitt „AK-218 nachgezogen" (Zeilen 6999-7180,
  Fassung 2 und §3) · nrplanner/advisor/worker.py · nrplanner/advisor/run.py
  (`cache_key`, `ResultCache`) · nrplanner/relicpicker.py (`SlotAdvice.ask`,
  `_refresh`, `_say_what_they_are_worth`) · nrplanner/favourites.py,
  paths.py, shortcut.py (die drei Schreiborte) · tests/picker_track.py ·
  tests/test_picker_track_guards.py · tests/test_relic_picker_advisor.py
  (Zeilen 1140-1200) · tests/conftest.py · scripts/differential/mutate.py
  (Format und Endteil) · CLAUDE.md
GEÄNDERT: nrplanner/advisor/worker.py · tests/test_picker_track_guards.py ·
  tests/picker_track.py · docs/berichte/T-137-developer.md (diese Datei).
  Zwei Commits auf docs/audit-and-advisor-design: e2cfc10 (U9), 10d6df2 (U10).
ANNAHMEN: (1) W8 ist der Waechter aus AK-218 Fassung 2 („Weg hinein → was die
  Oberflaeche zeigt"), wie der Auftrag ihn beschreibt — **nicht** der
  Struktur-Waechter ueber die vier unterbrechenden Stellen, den Nachtrag X-2
  unter demselben Namen fuehrt. Siehe „An den director", Punkt 1.
  (2) Die zwei uebrigen Teile von U10 aus der Nachtrag-X-Tabelle (W1 um
  `candidates.pools` erweitern, Randbedingung in den Tabellen-Docstring) sind
  im Auftragstext nicht enthalten und deshalb **nicht** gebaut. Punkt 2.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

**Namensgebrauch nach Auftrag:** `W6` heisst hier immer der Waechter der
Picker-Spur (`tests/test_picker_track_guards.py`, AD-028/Nachtrag IX), nie der
Fassaden-`W6` aus AD-019. `W8` ist der neue Waechter aus diesem Auftrag.

---

## 1. Die Herleitung des `architect` — geprueft, und sie stimmt

Der `architect` hat X-1 ausdruecklich als *hergeleitet, nicht gemessen*
markiert. Ich habe sie zuerst am Code nachgelesen und dann **gefahren**.

**Am Code festgemacht** (Stand vor dem Fix, `worker.py`):

| Stelle | erhoeht die Generation? | wie |
|---|---|---|
| `ask` / `ask_and_answer_if_known` | ja | ueber `_question_from`, Zeile 322 |
| `cancel` | ja | Zeile 351, direkt |
| `shutdown` | **nein** | Zeilen 371-383, kein `+= 1` |

`shutdown` unterbricht und wartet; `thread.wait()` verarbeitet die
Ereigniswarteschlange des Hauptthreads **nicht**. Ein `ready`, das der Worker
zwischen seiner letzten Pruefung und der Unterbrechung abgeschickt hat, liegt
danach in dieser Warteschlange, und `_on_ready` (444-456) vergleicht gegen eine
**unveraenderte** Generation.

**Gefahren, nicht nur gelesen.** Ich habe den sechsten W6-Fall *vor* dem Fix
geschrieben und laufen lassen:

```
FAILED tests/test_picker_track_guards.py::
  test_w6_a_question_ends_in_exactly_one_of_the_three[the window is closing]
AssertionError: ... was answered with ['ready'] and not with []
assert ['ready'] == []
1 failed, 5 passed in 6.70s
```

Das `ready` kommt also wirklich, wenn die Schleife sich noch einmal dreht — die
Herleitung ist damit ein beobachteter Fall und kein Wettlauf mehr, ueber den
man nur reden kann. **Was ich nicht behaupte:** dass es im Feld vorkommt. Der
Fall stellt die Reihenfolge her (`timeout_ms=0`, Antwort erst danach
freigegeben); ob `app.py:2039-2041` der Schleife im Feld noch eine Drehung
laesst, habe ich nicht gemessen und es ist fuer den Fix ohne Belang.

## 2. U9 — was gebaut ist

`nrplanner/advisor/worker.py`, Commit `e2cfc10`:

- **eine Zeile Verhalten:** `shutdown` erhoeht `self._generation` als erstes,
  vor `_pending = None` und vor dem Unterbrechen (Entscheidung D aus X-1);
- **der Klassen-Docstring** traegt die Fassung aus X-0 woertlich: die Zusage
  gilt fuer die Frage, die beim Ende noch die aktuelle ist, mit den drei
  benannten Ausnahmen (ueberholte Frage, Treffer, `shutdown`);
- **der Methoden-Docstring** von `shutdown` nennt den Grund der Zeile und die
  verworfene Option B (`stopped` senden) in einem Satz, damit sie nicht als
  Luecke wieder aufgemacht wird.

Nicht angefasst, wie beauftragt: kein Signal aus `shutdown`, kein `stopped` aus
`_Worker.work`, keine Signatur an `_interrupt_the_running_worker`, `app.py`
unberuehrt, `UI_SPEC.md`/`ARCHITECTURE.md` unberuehrt.

**Regressionstest:** sechster W6-Fall `"the window is closing"` in
`WAYS_A_QUESTION_ENDS`, erwartete Ausgangsliste `[]` **als Literal**. Dafuer
sind die fuenf vorhandenen Erwartungen von `"ready"` auf `["ready"]` umgestellt
— eine Formangleichung, damit „nichts" ein Wert derselben Messung ist und kein
Sonderweg.

**Weg des Beweises fuer U9, wie verlangt benannt:** ein Fall **mit** vollem
Mutationsbeweis, obwohl der Auftrag hier weniger verlangt hat. Grund: die
Mutation ist genau der Zustand von vorgestern, sie kostete 28 s, und ohne sie
haette ich „der Bruch faellt sofort auf" nur behauptet. Ergebnis unten.

## 3. U10 — W8, gebaut nach AK-218 Fassung 2

`tests/test_picker_track_guards.py`, Commit `10d6df2`. W8 hat **zwei
Haelften**, und die Tabelle steht zwischen ihnen.

**Die Tabelle `WAYS_INTO_THE_TRACK`** — Weg hinein → was die Oberflaeche zeigt:

| Weg hinein | Wege zurueck | was die Oberflaeche zeigt |
|---|---|---|
| `ask` | Signal | die Frage laeuft; `ready`/`failed`/`stopped`, jeder fuellt das Raster |
| `ask_and_answer_if_known` | Rueckgabewert **oder** Signal | Treffer: volles Raster im ersten Anstrich, nie eine Wartezeile · Fehlschlag: wie `ask` |

**Mengengleichheit, beidseitig, zweimal:**

1. `test_w8_every_way_into_the_track_has_a_row_and_every_row_a_way_in` liest
   ueber den **Syntaxbaum** von `worker.py`, welche Methoden des
   `AdvisorController` `_question_from` aufrufen — das ist die eine Stelle, die
   aus einer Fragestellung eine `Question` macht, also der Engpass, durch den
   ein dritter Weg hinein muesste. Gefunden = Tabellenschluessel, in beide
   Richtungen.
2. `test_w8_both_ways_back_are_driven_by_an_opening`: die in der Tabelle
   genannten Wege zurueck = die Wege, fuer die es unten eine Vorrichtung gibt.

**Die vier Oeffnungen** (`WHAT_THE_SURFACE_SHOWS`, parametrisiert als
`test_w8_every_way_back_leaves_cards_to_choose_from`) fahren die **echte** Spur
und den **echten** Dialog:

| Oeffnung | Weg zurueck | gepruefter Zustand des Rollbereichs |
|---|---|---|
| the answer is there at once | Signal (`ready`) | Karten stehen, `Your relics appear here.` weg, mindestens eine Karte traegt den Chip, nicht jede Karte sagt `—`, keine Kopfzeile |
| the answer fails | Signal (`failed`) | Karten stehen, Kopfzeile = `could_not_work_out("the dataset lost a curve")`, jede Karte `—`/`—`, kein Chip |
| the search is stopped | Signal (`stopped`) | dasselbe mit `<reason>` = `the search was stopped` |
| the answer was already known | Rueckgabewert | `answers.calls == 1`, `not dialog.waiting`, Karten **im ersten Anstrich** |

**Die drei Vorgaben, die der Auftrag ausdruecklich nennt:**

1. *Gezaehlt wird, was im Rollbereich steht.* Keine Zeile von W8 zaehlt
   Signale. Gelesen werden `cards_in(dialog)`, `area_labels(dialog)`,
   `card.block.values`, `card.chip.text()`, `dialog.headline`.
2. *Positivkontrolle.* Beide vom `ui-ux-designer` verlangten Belege stehen in
   `_shows_the_grid_in_the_first_paint`, und beide ohne Uhr: `answers.calls`
   ueber **beide** Oeffnungen ist 1, und die Karten werden gelesen, **bevor**
   die Ereignisschleife nach dem Bau des zweiten Dialogs auch nur einmal
   gedreht wurde. Dass das nicht bloss dasteht, zeigt die Mutation
   `the-cache-never-hits` (unten): sie toetet genau diesen Fall.
3. *Keine Frist.* Kein `assert` ueber eine Dauer, kein „innerhalb von X ms",
   keine Behauptung ueber die Zahl der Anstriche. `spin` wird nur als
   Zustandswarte benutzt, seine Frist ist eine Sicherung und kommt in keiner
   Behauptung vor.

**Eine Aenderung an `tests/picker_track.py`:** `StatedAnswers` bekommt
`raises=<Grund>` und `a_track` reicht es durch. Grund: die scheiternde Spur
soll ihre Fragen **zaehlen** wie die anderen; eine ad-hoc-Funktion im Fall
haette keinen Zaehler, und `calls` ist das, was eine gefahrene Vorrichtung von
einer ungefahrenen unterscheidet.

## 4. Die ungefahrene Annahme des `ui-ux-designer` — sie traegt

*„Zwei Oeffnungen desselben Slots treffen den Zwischenspeicher wirklich."*
**Angetroffen, kein Befund.** Beleg: `answers.calls == 1` ueber beide
Oeffnungen in `_the_answer_was_already_known`, gruen; und die Mutation
`the-cache-never-hits` macht daraus `calls == 2` und toetet den Fall. Der
Treffer ist also da und die Pruefung darauf ist scharf.

## 5. Mutationslauf — acht Mutationen, acht Tote

Gefahren gegen `tests/test_picker_track_guards.py` in einer **Kopie** des
Arbeitsbaums (`shutil.copytree` von `nrplanner nrdata tests scripts pytest.ini
run.py`, je Mutation ein frischer Baum, `PYTHONDONTWRITEBYTECODE=1`,
`-p no:cacheprovider`, Anker muss **genau einmal** passen). Treiber:
`…/scratchpad/T-137/mutate_t137.py`. Je Lauf 28-63 s.

| Mutation | Datei | gefallen ist |
|---|---|---|
| `a-third-way-into-the-track` (eine dritte Methode, die `_question_from` ruft) | worker.py | `test_w8_every_way_into_the_track_has_a_row…` |
| `a-way-into-the-track-goes-away` (`ask_and_answer_if_known` baut die Frage selbst) | worker.py | dasselbe **plus** `test_w3_the_answer_of_a_closed_opening…` |
| `the-table-forgets-the-return-value` (Tabellenzeile verliert `BY_RETURN_VALUE`) | Testdatei | `test_w8_both_ways_back_are_driven_by_an_opening` |
| `the-cache-never-hits` (`known = None`) | worker.py | W8 `[…-the answer was already known]` **plus** W5 |
| `the-picker-does-not-handle-stopped` | relicpicker.py | W8 `[…-the search is stopped]` — **nur** dieser |
| `the-picker-does-not-handle-ready` | relicpicker.py | W8 `[…-the answer is there at once]` **plus** W5, W3, W8-Treffer |
| `the-picker-does-not-handle-failed` | relicpicker.py | W8 `[…-the answer fails]` — **nur** dieser |
| `shutdown-does-not-raise-the-generation` | worker.py | W6 `[the window is closing]` |

**Ueberlebt hat keine.** Zwei Beobachtungen, die ich nicht verschweige:

- `the-picker-does-not-handle-stopped` und `-failed` toeten **je genau einen**
  Fall, und beide sind neu. Das heisst: vor W8 war der Umgang des Pickers mit
  `stopped`/`failed` **ueber die echte Spur** von nichts bewacht — die
  vorhandenen Faelle in `test_relic_picker_advisor.py` fahren `FakeAdvice` und
  ersetzen genau die Strecke. Das ist der Zugewinn von W8, und es ist zugleich
  die Antwort auf „welche Regel hielt das sonst gruen": keine.
- `a-way-into-the-track-goes-away` reisst W3 mit. Das ist Kollateral, nicht der
  Beleg; der Beleg ist der W8-Strukturfall in derselben Zeile.

**Rot-vorher, getrennt benannt** (L-007): der W6-Fall bricht heute an der
**einen Zeile** `self._generation += 1` in `shutdown` — nimmt man sie weg,
faellt er, und **nur** er. Er faellt nicht wegen einer
Schnittstellenverschiebung: `shutdown`s Signatur, Aufrufer und Rueckgabe sind
unveraendert. Die Schutzmassnahme des Fixes ist eine einzige, sie wurde einzeln
deaktiviert, und es fiel ein Test.

## 6. Die Eigenschaft, nicht die Fundstelle (L-006)

Der Befund lautet „eine unterbrechende Stelle erhoeht den Zaehler nicht".
Projektweit gesucht, mit drei unabhaengig formulierten Masken:

1. Volltext `_interrupt_the_running_worker` ueber `**/*.py`: **4 Aufrufstellen**
   (worker.py 324, 349, 369, 410) plus die Definition (417); ausserhalb von
   `worker.py` nur die Anker in `scripts/differential/mutate.py`, kein
   Anwendungscode.
2. Unabhaengige Maske ueber den **Mechanismus** statt den Namen:
   `requestInterruption|isInterruptionRequested|\.quit\(\)|\.terminate\(\)` in
   `nrplanner nrdata scripts` — **keine** weitere Stelle im Anwendungscode, die
   einen rechnenden Thread unterbricht (`app.py:2162` ist
   `QApplication.quit()`, das Ende des Programms).
3. Syntaxbaum-Auswertung ueber `AdvisorController`: welche Methode
   unterbricht, erhoeht selbst, stellt eine Nachfolgefrage. Ergebnis nach dem
   Fix:

| Methode | unterbricht | erhoeht selbst | stellt Nachfolgefrage |
|---|---|---|---|
| `ask_and_answer_if_known` | ja | nein | **ja** (`_question_from` in derselben Aufrufung) |
| `_wait_for` | ja | nein | nein — der Aufrufer hat in derselben Aufrufung erhoeht |
| `cancel` | ja | **ja** | nein |
| `shutdown` | ja | **ja** (neu) | nein |

**Weitere Fundstellen derselben Eigenschaft: null.** Alle vier Stellen sind
jetzt gedeckt, direkt oder durch die Frage, die sie in derselben Aufrufung
stellen — das ist genau die Zusage aus X-2.

## 7. Testumgebung, Umlenkungen, Zahlen

**Alle drei Schreiborte umgelenkt, jede Umlenkung mit Positivkontrolle**
(`…/scratchpad/T-137/prove_redirect.py`, einmal ohne und einmal mit
Umlenkung — die Kontrolle zeigt, dass die Messung ohne Umlenkung wirklich auf
den echten Ort zeigt):

| Variable | ohne Umlenkung | mit Umlenkung |
|---|---|---|
| `LOCALAPPDATA` → `paths.cache_dir()` | `C:\Users\Daniel\AppData\Local\NightreignHelper` | `…\scratchpad\T-137\localappdata\NightreignHelper` |
| `APPDATA` → `shortcut.shortcut_path()` | `…\Roaming\…\Start Menu\Programs\Nightreign Helper.lnk` | `…\scratchpad\T-137\appdata\…\Programs\Nightreign Helper.lnk` |
| `NIGHTREIGN_SETTINGS_ORG` → `favourites.ORG` | `DankYeeter` | `DankYeeterT-137` |

*Genau gesagt zum dritten:* unter `pytest` setzt `tests/conftest.py` die Org
selbst auf `DankYeeterTests` und die App auf `NightreignHelperTests-<pid>` und
ueberschreibt meinen Wert. Beide sind vom Speicher des Spielers weg; die
Registrierung zeigt nach dem Lauf **keinen** neuen Schluessel unter
`HKCU\Software` und `DankYeeterT-137` existiert nicht.

**Der feste Testabzug** wurde in das umgelenkte `LOCALAPPDATA` **kopiert**
(841 Dateien, 22 MB), nicht darauf gezeigt.

**Nachweis, dass die echten Orte unberuehrt sind** — Bestandslisten mit
Zeitstempel und Groesse vor und nach allen Laeufen, `diff` leer:

- `%LOCALAPPDATA%\NightreignHelper`: 843 Eintraege, unveraendert;
- Start-Menue `…\Programs`: 25 Eintraege, unveraendert;
- `HKCU\Software\DankYeeter` (`reg query … -s`): 160 Zeilen, unveraendert.

**Suitezahl.** `pytest -n auto`, ganze Suite, in der umgelenkten Umgebung:

```
1357 passed, 9 skipped in 172.97s (0:02:52)
```

Gegen die Vorgabe **1350 passed, 9 skipped, 0 failed**: **+7 passed**, Skips
und Fehlschlaege unveraendert. Die sieben sind genau die neuen Faelle — ein
W6-Fall und sechs W8-Faelle (2 Struktur + 4 Oeffnungen). Einzeln:
`pytest tests/test_picker_track_guards.py` → `22 passed in 27.26s` (vorher 15).
Zusaetzlich `test_picker_track_guards.py + test_advisor_worker.py +
test_relic_picker_advisor.py` seriell: `94 passed in 317.43s`.

**Zielsystem:** Windows 10 x64, Python 3.12, PySide6 offscreen. Linux und
macOS **ungeprueft** und kein Ziel.

## 8. DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (Block oben)
- [x] Build & Tests gruen in der benannten Umgebung; Linux/macOS ungeprueft
- [x] Neue Tests fuer neue Logik; **Linterpunkt entfaellt** — es ist keiner
      konfiguriert (kein `.flake8`, `ruff.toml`, `setup.cfg`, `pyproject.toml`,
      `tox.ini`; nichts in `requirements-dev.txt` oder `pytest.ini`). Statt
      dessen geprueft: keine neue Zeile ueber 79 Zeichen (die eine 80er in
      `picker_track.py:199` ist Bestand und nicht von mir).
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] QA-Akzeptanzkriterien selbst durchgespielt (AK-218 Fassung 2 (a) und (b),
      AK-208, AK-212 unberuehrt); UI-Vorgaben eingehalten — **kein**
      Anwendungscode an der Oberflaeche geaendert
- [x] Bericht geschrieben (diese Datei), zwei atomare Commits

---

## An den `director`

**1. W8 heisst in Nachtrag X-2 und in AK-218 Fassung 2 zwei verschiedene
Waechter — ich habe den aus dem Auftragstext gebaut.**
Nachtrag X-2 vergibt `W8` an einen **reinen Struktur-Test** ueber die vier
unterbrechenden Stellen (Tabelle „Stelle → was die abgehende Frage hoert").
Der `ui-ux-designer` benutzt in T-135 §1 und §3.5 denselben Namen fuer den
Waechter ueber AK-218 Fassung 2, und **so steht es im Auftrag** (U10, vier
Punkte). Gebaut ist der aus dem Auftrag. Die Bauform von X-2 ist darin
enthalten — Tabelle, Mengengleichheit beidseitig, Erwartung im Test —, der
**Gegenstand** ist ein anderer: Wege *hinein*, nicht Stellen, die
*unterbrechen*. Die vier unterbrechenden Stellen habe ich fuer diesen Bericht
von Hand ausgewertet (Abschnitt 6) und **nicht** als Test gebaut. Entscheidung
noetig: eigener Waechter mit eigener Nummer, oder erledigt durch Abschnitt 6.
*Aufwand, wenn er gebaut werden soll: klein* — dieselbe Syntaxbaum-Auswertung
wie in Abschnitt 6, gegen eine Tabelle im Test, plus zwei Mutationen; eine
halbe Stunde.

**2. Zwei Teile von U10 aus der Nachtrag-X-Tabelle stehen nicht im Auftrag und
sind nicht gebaut.** Die Tabelle in `ARCHITECTURE.md` (Abschnitt „Umsetzung —
U9 und U10") nennt fuer U10 ausser W8 noch: **W1 um die Zeile
`candidates.pools` → `advisor/run.py` erweitern** (X-3.3) und **die
Randbedingung von W1 in den Docstring der Tabelle** (X-3, letzter Absatz:
W1 haengt an Modulkurzname plus Funktionsname und sieht keine Rechnung, die
unter anderem Namen in den Hauptthread kaeme). Der Auftragstext T-137 nennt
beides nicht. Nach „nur der erteilte Auftrag" habe ich es liegen lassen.
*Beides liegt in `tests/test_picker_track_guards.py`, ist zusammen ein
Zehnminuten-Auftrag* (ein Tabelleneintrag, ein Absatz, eine Mutation
„`candidates.pools` in `app.py` nennen").

**3. Die acht Mutationen sind nicht in `scripts/differential/mutate.py`
registriert** — die Datei liegt ausserhalb meiner Grenzen („nur
`nrplanner/advisor/worker.py` und `tests/`"). Gefahren sind sie mit einem
eigenen Treiber, der dieselbe Mechanik benutzt (Anker genau einmal, Kopie statt
Arbeitsbaum). **Der Treiber liegt im Scratchpad und ist damit fluechtig.** Wenn
die Eintraege bleiben sollen, ist das ein kleiner Folgeauftrag; die acht
Anker-/Ersatzpaare stehen fertig in
`…/scratchpad/T-137/mutate_t137.py`, Vorschlag fuer die Namen wie in der
Tabelle in Abschnitt 5. *Empfehlung: ja, mindestens
`shutdown-does-not-raise-the-generation`, `the-cache-never-hits` und
`a-third-way-into-the-track` — die drei bewachen je eine Entscheidung aus
Nachtrag X.*

**4. Zwei Beobachtungen ohne Auftrag, gemeldet statt behoben:**

- **`tests/test_picker_track_guards.py` ist mit 900 Zeilen und acht Waechtern
  gross geworden**, und `WAYS_A_QUESTION_ENDS` und `WHAT_THE_SURFACE_SHOWS`
  stehen jetzt in derselben Datei nebeneinander, obwohl sie verschiedene Dinge
  zaehlen. Keine Debt im engeren Sinn, aber der naechste Waechter macht sie
  eine. *Risiko gering, Aufwand einer Teilung mittel.*
- **Der Zeiger von W6 auf AK-218 zeigt weiter auf Fassung 1.** Der
  `ui-ux-designer` hat das in §3.6 als „Textpflege bei der naechsten
  Beruehrung" bezeichnet, ohne Verhaltensaenderung; ich habe den Docstring von
  `test_w6_…` beim Anfassen auf die neue Fassung des Zusagesatzes gebracht, die
  AK-218-Zitate in `nrplanner/relicpicker.py` aber **nicht** angefasst
  (Anwendungscode ausserhalb des Auftrags).

**Sicherheitsfunde: keine.** Nichts in diesem Auftrag nimmt externen Input,
baut Pfade oder Kommandos zusammen. **Performance-Funde: keine** — es ist eine
Zeile Zuweisung; die Messung des Vorfilters ist ausdruecklich der
`performance-tuner` und nicht angefasst.

## An den `qa-engineer`

Zu testen ist eine **Abwesenheit**, und sie ist von Hand schwer zu sehen:

- **Der Fall selbst:** Picker oder Advisor-Leiste beim laufenden Lauf, dann das
  Hauptfenster schliessen. Erwartet: nichts blitzt auf, keine Ausgabe, kein
  Fenster, das nach dem Schliessen noch zeichnet. Vorher konnte ein spaetes
  `ready` durchkommen; ein sichtbarer Fehler war das nur, wenn die Schleife
  sich noch drehte, also **selten und nicht reproduzierbar** — bitte nicht
  als „war nie kaputt" lesen.
- **Randfall, den ich nicht gefahren habe:** Schliessen **waehrend** die
  Entprellung laeuft (Frage gestellt, Lauf noch nicht angefangen). Der Zaehler
  steigt auch dort, aber die Vorrichtung deckt nur den laufenden Worker.
- **W8s Gegenstand von Hand:** denselben Slot zweimal hintereinander oeffnen,
  ohne dazwischen etwas am Build zu aendern. Die zweite Oeffnung darf
  `Your relics appear here.` **nie** zeigen, auch nicht kurz. Zeigt sie es,
  ist der Zwischenspeicher verfehlt worden — dann interessiert **was** sich
  dazwischen geaendert hat (Ziel, Level, Reliktbestand, Favorit).
- **Und der Gegenfall:** einen **anderen** Slot oeffnen — dort **soll** das
  leere Raster kurz stehen (AK-212). Ohne diesen Gegenfall misst die Pruefung
  ihr eigenes Pruefmittel.

## An den `ui-ux-designer`

**Keine Abweichung von der Vorgabe, eine Praezisierung an einer Stelle.**
AK-218 Fassung 2 nennt fuer Weg (b)/`ready` „Karten in der sortierten Ordnung".
W8 prueft die **Ordnung nicht** — es prueft, dass Karten stehen, dass
mindestens eine den Chip traegt und dass nicht jede Karte `—` sagt. Grund: die
Ordnung ist Gegenstand von AK-195/AK-44 und wird von den Faellen in
`test_relic_picker_advisor.py` gehalten; ein zweiter Waechter darueber haette
dieselbe Regel doppelt und an der schwaecheren Stelle. Ebenso ungeprueft: die
Namensordnung bei `failed`/`stopped` (dort steht `_in_the_chosen_order` ohne
Ranking auf der Ordnung, die das Raster ohnehin hat). **Sagen Sie, wenn W8 das
tragen soll** — dann braucht es einen Fall, der die beiden Ordnungen
gegeneinander stellt, sonst ist er zahnlos.
