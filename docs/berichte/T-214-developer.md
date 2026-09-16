STATUS: erledigt
AUFTRAG: T-214 — Zwei Aussagen, die ihre zweite Fundstelle nicht geschlossen haben
GELESEN: docs/tasks/T-214.md (vollstaendig); .claude/hooks/enforce-data-redirect.ps1; scripts/measure_*.py (alle acht, per Grep auf QApplication/Planner/environ); nrplanner/paths.py; docs/berichte/T-203-developer.md (Nachweismethode und die sieben Bestandsfaelle); C:\Users\Daniel\Desktop\ClaudeCode\claude-agent-team\commands\director.md (Zeilen 60-80, 840-910); C:\Users\Daniel\Desktop\ClaudeCode\claude-agent-team\hooks\state-line-budget.ps1; C:\Users\Daniel\Desktop\ClaudeCode\claude-agent-team\hooks\selftest.ps1 (Ausschnitt state-line-budget); C:\Users\Daniel\Desktop\ClaudeCode\claude-agent-team\agents\_rahmen.md (Ausschnitt "Regeln pflegen")
GEÄNDERT: Nightreign-Helper/.claude/hooks/enforce-data-redirect.ps1 (committet, Nightreign-Helper); claude-agent-team/commands/director.md (committet, claude-agent-team); Nightreign-Helper/docs/berichte/T-214-developer.md (dieser Bericht)
ANNAHMEN: keine — beide Vorgaben waren eindeutig, die Zeilenangabe "850-853" im Auftrag war veraltet (Datei hat sich seit Auftragserstellung verschoben), die tatsaechliche Fundstelle war 886-889 mit demselben Wortlaut wie zitiert; eindeutig identifiziert per Volltextsuche, keine Annahme noetig.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Ziel 1 — QA-244, enforce-data-redirect.ps1

**Befund bestaetigt:** von acht Skripten unter `scripts/measure_*.py` bauen
nur `measure_picker_cards.py` und `measure_advisor_block.py` ein echtes
`appmod.Planner(data)`-Fenster (per Grep auf `Planner(` bestaetigt). Die
uebrigen sechs (`measure_advisor_cancel.py`, `measure_advisor_language.py`,
`measure_advisor_picker.py`, `measure_advisor_search.py`,
`measure_advisor_worker.py`, `measure_display_thresholds.py`) oeffnen kein
Fenster; `measure_advisor_worker.py` baut zwar eine `QApplication` fuer die
Event-Loop, aber keine `Planner`-Instanz und ruehrt keine der drei
Umlenkungsvariablen an — sein eigener Docstring bzw. der von
`measure_advisor_cancel.py` sagt das explizit ("No window is opened").

**Wegentscheidung: (a), aber verfeinert — zwei Dateinamen statt Wildcard.**
Ein Muster auf `scripts/measure_*.py` haette sechs von acht Skripten ohne
Grund abgewiesen (die Sorge des Auftrags war berechtigt). Ich habe die
beiden bekannten Fenster-Skripte stattdessen als eigenes `$ist*`-Pattern
aufgenommen, im selben Stil wie `run.py`/`NightreignHelper.exe` — exakte,
belegte Namen statt Vermutung, was zur eigenen Philosophie des Hooks passt
(`ponytail:`-Kommentar: "aus dem Repository abgeleitet, nicht aus
Vorstellung"). Weg (b) habe ich verworfen: er haette Anwendungscode
(zwei Skripte) angefasst, obwohl der Auftrag das nur bei Weg (b) erlaubt und
ich (a) fuer treffsicherer halte — zwei Stellen mit derselben Vergesslichkeit
wie beim urspruenglichen Befund selbst. Kein dritter, grundlegend anderer Weg
gefunden; die Verfeinerung von (a) ist der Weg.

**Aenderung:** `.claude/hooks/enforce-data-redirect.ps1`, neue Variable
`$istFensterMessskript` mit Muster
`\b(python3?|py)(\.exe)?\b[^;&|]*\b(measure_picker_cards|measure_advisor_block)\.py\b`,
in die bestehende `if (-not (...))`-Weiche aufgenommen. Kommentar erklaert das
Kriterium (baut ein Planner-Fenster) fuer kuenftige Ergaenzungen.

**Nachweis, gegen die stdin-Schnittstelle wie in T-203 (Hook in dieser
Sitzung nicht geladen, QA-241):**

| # | Kommandozeile | erwartet | Ergebnis |
|---|---|---|---|
| 1 | `python run.py` (keine Variablen) | deny | deny, alle drei genannt |
| 2 | `pytest -n auto -q` | allow | allow |
| 3 | `NightreignHelper.exe` (keine Variablen) | deny | deny, alle drei genannt |
| 4 | zwei von drei Variablen, kein Trenner vor `python`, `run.py` | deny (nur APPDATA) | deny, nennt nur APPDATA |
| 5 | alle drei Variablen, Bash-Form, `run.py` | allow | allow |
| 6 | alle drei Variablen, PowerShell-Form, `run.py` | allow | allow |
| 7 | `git status` | allow | allow |
| 8 (neu) | `python scripts/measure_picker_cards.py` (keine Variablen) | deny | deny, alle drei genannt |
| 9 (neu) | dieselbe mit allen drei Variablen | allow | allow |
| 10 (neu) | `python scripts/measure_advisor_block.py` (keine Variablen) | deny | deny, alle drei genannt |
| 11 (neu) | dieselbe mit allen drei Variablen | allow | allow |
| 12 (Gegenprobe) | `python scripts/measure_advisor_worker.py` (keine Variablen, baut kein Fenster) | allow | allow |

Fall 12 ist die Positivkontrolle fuer die Entscheidung gegen den Wildcard: ein
Messskript ohne Fenster darf durchlaufen, auch ohne Variablen — sonst waere
die Verfeinerung wirkungslos und ich haette denselben Fehler nur anders
benannt.

## Ziel 2 — zweite Zyklusende-Fundstelle in commands/director.md

Die im Auftrag zitierten Zeilen 850-853 waren nicht mehr aktuell (Datei hat
sich verschoben); per Volltextsuche nach "Zyklusende" und "bewacht, existiert
nicht" gefunden: **Zeilen 886-889**, Wortlaut deckungsgleich mit dem Zitat im
Auftrag.

**Umgesetzt:**
1. Nutzerentscheidung vom 08.09.2026 bleibt stehen, jetzt als ueberholt markiert:
   "galt ... ausdruecklich nicht" (Vergangenheitsform) plus Satz "ueberholt
   seit `hooks/state-line-budget.ps1` (Nutzerfreigabe L-020, 12.09.2026): das
   Budget wird seither beim Schreiben geprueft".
2. Satz "ein Test, der sie bewacht, existiert nicht" entfernt, ohne Ersatz.
   Gegengeprueft, dass die Absenz-Behauptung tatsaechlich falsch war:
   `hooks/selftest.ps1` Zeilen 477-482 pruefen `state-line-budget.ps1` explizit
   (Marke `[state-budget]`, mit Begruendung, warum kein `deny` erwartet wird).

**Dritte Fundstelle — gesucht, nicht angenommen:** Volltextsuche im ganzen
`claude-agent-team`-Repo nach zwei unabhaengigen Masken
(`Zeilenbudget wird` / `bewacht, existiert nicht`) ergab **eine** weitere
Stelle ausserhalb von `commands/director.md`: **`agents/_rahmen.md`,
Zeilen 343-345** — "Das Zeilenbudget fuer `docs/state.md` ... wird deshalb
**nur noch am Zyklusende geprueft**." Das ist dieselbe veraltete Behauptung
(ohne den "kein Test"-Satz, aber mit derselben falschen Zeitangabe). Ich habe
sie **nicht** geaendert: der Auftrag nennt nur `commands/director.md` als
zu aendernde Datei, `agents/_rahmen.md` liegt ausserhalb der Scope-Grenze
("Keine weitere Zeile in commands/director.md als die genannten" plus die
Beruehrt-Dateien-Liste nennt nur director.md). Meldung statt Eigenmacht.

`grep -c` fuer beide Masken im ganzen Repo: `Zeilenbudget wird` → 2 Treffer
(director.md:71 bereits von T-213 korrigiert, director.md:886 jetzt von mir),
`nur noch am Zyklusende geprueft` → 1 Treffer (_rahmen.md:345). Keine weiteren.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (keine wesentlichen).
- [x] Nachweis fuer beide Ziele erbracht wie im Auftrag verlangt (Tabelle
      oben; Ziel 2 durch Volltextsuche und Lesen des Hooks/Selftests).
- Kein Linter im Projekt konfiguriert — entfaellt, keine Luecke.
- [x] Keine Secrets, keine TODOs, kein toter Code.
- [x] Scope eingehalten: kein Anwendungscode unter `nrplanner/`, `nrdata/`,
      `scripts/`; `~/.claude/settings.json` und `~/.claude/agents/`
      unangetastet; nur die genannten Zeilen in `commands/director.md`
      geaendert; kein Push (zwei lokale Commits, einer je Repository).
- [x] Bericht abgelegt.

**Ungepruefte Plattformen:** Linux/macOS wie immer kein Ziel; der Hook ist
PowerShell-5.1/Windows-spezifisch wie sein Vorbild aus T-203.

**Volle pytest-Suite nicht erneut gelaufen** — keine Python-Datei geaendert,
nur eine PowerShell-Hook-Datei und eine Markdown-Datei in einem anderen
Repository. Kein Risiko fuer bestehende Tests, daher als bewusst nicht
wiederholte Pruefung ausgewiesen statt stillschweigend uebersprungen.

## An qa-engineer

Nicht direkt betroffen (kein Anwendungscode, "Parallel: Nein"). Fuer den
naechsten Fensterlauf mit `measure_picker_cards.py` oder
`measure_advisor_block.py` relevant: beide brauchen jetzt alle drei
Umlenkungsvariablen in derselben Kommandozeile, sonst weist der Hook ab.

## An ui-ux-designer

Nicht betroffen — keine Oberflaechenaenderung.

## An director

1. **Dritte Fundstelle gefunden und nicht behoben:** `agents/_rahmen.md`
   Zeilen 343-345 im Repo `claude-agent-team` traegt dieselbe veraltete
   Behauptung ("nur noch am Zyklusende geprueft") wie die jetzt korrigierte
   Stelle in `commands/director.md`. Liegt ausserhalb meines Auftragsscopes
   (nur director.md war zur Aenderung freigegeben). Empfehlung: kleiner
   Folgeauftrag, dieselbe Korrekturlogik (Datum + Grund statt Loeschen).
2. Beide Aenderungen sind jeweils lokal committet (ein Commit je
   Repository, siehe GEÄNDERT). Kein Push — der Auftrag verlangt keinen und
   `archivist` verantwortet den Abgleich mit dem Remote.
3. Die Zeilenangabe "850-853" im Auftrag T-214 war zum Zeitpunkt der
   Bearbeitung veraltet (tatsaechlich 886-889) — vermutlich, weil sich
   `commands/director.md` zwischen Auftragserstellung und -bearbeitung
   veraendert hat. Kein Blocker, nur als Hinweis fuer kuenftige Auftraege mit
   Zeilenzitaten aus Dateien, die parallel bearbeitet werden koennten.
