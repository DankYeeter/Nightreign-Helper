STATUS: erledigt
AUFTRAG: T-203 — Der Waechter, der die Umlenkung erzwingt statt sie zu verlangen
GELESEN: docs/tasks/T-203.md; CLAUDE.md (vollstaendig); run.py; NightreignHelper.spec; requirements-dev.txt; .gitignore; docs/berichte/T-199-developer.md (Auszug: Umlenkungen, `python run.py`); docs/berichte/T-200-developer.md (Auszug: Umlenkungen, `python run.py`, Fensterlauf); nrplanner/favourites.py:15-27; nrplanner/paths.py:10-25; nrplanner/shortcut.py:38-52; C:\Users\Daniel\Desktop\ClaudeCode\claude-agent-team\hooks\no-root-find.ps1; C:\Users\Daniel\Desktop\ClaudeCode\claude-agent-team\hooks\block-source-read.ps1; ~/.claude/settings.json (Format-Referenz fuer Hook-Registrierung)
GEÄNDERT: .claude/hooks/enforce-data-redirect.ps1 (neu); .claude/settings.json (neu); CLAUDE.md; requirements-dev.txt; docs/berichte/T-203-developer.md
ANNAHMEN: Hook-Registrierung fuer `$CLAUDE_PROJECT_DIR` in `command` uebernommen wie von Claude Code dokumentiert (Substitution vor dem Start der Shell) — im Team-Repo selbst nicht als Beispiel vorhanden, da dessen Hooks alle mit absoluten `C:/Users/Daniel/...`-Pfaden arbeiten (dort passend, weil teamweit und nicht projektrelativ). Ein Fehlschlag dieser Substitution wuerde den Hook stumm wirkungslos machen (leerer Pfad zur .ps1) statt ihn ploetzlich zu haerten — das ist ein Risiko, siehe unten.
NÄCHSTER: director

## Erkannte Startformen (aus dem Repository, nicht aus Vorstellung)

- **Quellbaum:** `python run.py` (Entry Point in `run.py`; so gestartet in T-199 und T-200, dort auch mit den drei Variablen belegt).
- **Gebaute Einzeldatei:** `NightreignHelper.exe` (Name aus `NightreignHelper.spec`, `name='NightreignHelper'`, `console=False`; einzige `EXE`-Definition im Spec).

Nicht als eigene Form erkannt und damit bewusst nicht abgedeckt (siehe `ponytail:`-Kommentar im Hook, Zeilen 44-51): `Start-Process`, ein Aufruf ueber `python -c "...nrplanner.app..."`, ein Doppelklick auf die `.exe` (kein Werkzeugaufruf). Taucht eine dieser Formen in einem Bericht als tatsaechlich genutzt auf, ist das ein weiteres `$ist*`-Pattern im Hook.

## Die zwei geforderten Faelle (Vorgabe 2)

Ich habe den Hook nicht ueber einen echten Fensterlauf ausgeloest — `python run.py` als reale Bash-Aktion wurde vom Auto-Mode-Classifier der Umgebung selbst abgewiesen (eine andere, dem Hook vorgelagerte Sperre; nicht Teil dieses Auftrags und nicht mein Nachweis). Stattdessen habe ich das Skript direkt mit dem exakten JSON gefuettert, das Claude Code einem `PreToolUse`-Hook per stdin uebergibt (`tool_name`, `tool_input.command`) — das ist derselbe Mechanismus, den die Registrierung in `.claude/settings.json` verwendet, nur ohne den Umweg ueber einen echten Werkzeugaufruf, den der Classifier ohnehin blockiert haette.

**Fall 1 — abgewiesener Programmstart:**

Kommandozeile: `python run.py`

```
$ echo '{"tool_name":"Bash","tool_input":{"command":"python run.py"}}' | powershell -File .claude/hooks/enforce-data-redirect.ps1
{"hookSpecificOutput":{"permissionDecision":"deny","hookEventName":"PreToolUse","permissionDecisionReason":"[datenumlenkung] Programmstart ohne vollstaendige Umlenkung: NIGHTREIGN_SETTINGS_ORG, LOCALAPPDATA, APPDATA fehlt in dieser Kommandozeile. Setze NIGHTREIGN_SETTINGS_ORG, LOCALAPPDATA und APPDATA in derselben Kommandozeile wie den Start (CLAUDE.md, Abschnitt 'Datenverzeichnisse - und die Sperre davor')."}}
```

**Fall 2 — durchgelassener pytest-Lauf:**

Kommandozeile: `pytest -n auto -q`

```
$ echo '{"tool_name":"Bash","tool_input":{"command":"pytest -n auto -q"}}' | powershell -File .claude/hooks/enforce-data-redirect.ps1
(keine Ausgabe, Exit 0 — durchgelassen)
```

Zusaetzlich live im Verlauf dieses Auftrags gemessen (kein Denial durch die Bash-Klassifizierung, kein Hook-Deny sichtbar): `python -m pytest -n auto -q` im Repo-Wurzelverzeichnis lief vollstaendig durch, Ergebnis `1781 passed, 9 skipped in 130.77s` — deckt sich mit der in CLAUDE.md genannten aktuellen Zahl und belegt nebenbei, dass der reale `pytest`-Lauf in dieser Sitzung nicht blockiert wurde.

**Weitere Faelle, mit derselben Methode geprueft (nicht explizit gefordert, aber zur Absicherung der Logik):**
- `& 'C:/Users/Daniel/dist/NightreignHelper/NightreignHelper.exe'` ohne Variablen → deny (alle drei fehlen).
- `NIGHTREIGN_SETTINGS_ORG=DankYeeterT203 LOCALAPPDATA=/c/scratch/localappdata python run.py` (zwei von drei, kein Trennzeichen vor `python`) → deny, nennt nur `APPDATA` als fehlend.
- `NIGHTREIGN_SETTINGS_ORG=DankYeeterT203 LOCALAPPDATA=/c/scratch/T-203/localappdata APPDATA=/c/scratch/T-203/appdata python run.py` → allow (keine Ausgabe).
- PowerShell-Form `$env:NIGHTREIGN_SETTINGS_ORG='...'; $env:LOCALAPPDATA='...'; $env:APPDATA='...'; python run.py` → allow.
- `git status` (kein Programmstart) → allow, unabhaengig vom Variablenstand.

Bei der ersten Fassung des Hooks hatte ich das Startmuster fuer `run.py` faelschlich auf Zeilenanfang oder auf ein vorangehendes `;`/`&`/`|` verankert — das hat den realistischsten Fall (`VAR=wert VAR2=wert python run.py`, ein einzelnes Bash-Kommando mit vorangestellten Env-Zuweisungen ohne Trennzeichen) durchgelassen, obwohl zwei von drei Variablen fehlten. Gefunden beim eigenen Test oben (Fall E), korrigiert durch Entfernen des Ankers.

## `CLAUDE.md` — Zeilenzahlen (Vorgabe 6)

Vorher: **160** Zeilen. Nachher: **159** Zeilen. Kuerzer, wie gefordert — die Kuerzung ist knapp, weil derselbe Abschnitt zugleich den Hook, die neue Nachweis-Unterscheidung, den Sicherheitsnetz-Satz mit Hypothesen-Zuordnung und den korrigierten Testabzug-Absatz tragen musste; ohne mehrfaches Nachverdichten (Absaetze zusammengezogen, Nebensaetze gestrichen) waere die Datei laenger geworden.

Inhaltlich umgesetzt:
- Satz "Gelingt ein Nachweis nicht, wird der Lauf abgebrochen..." entfernt, ersetzt durch die Hook-Aussage.
- Zwei-Zeilen-Unterscheidung: positive Pfadaufloesung haelt (Beispiel `paths.cache_dir()`), Abwesenheits-Nachweis haelt nicht (gleiche geteilte Ueberlagerung, QA-237) — als zwei Saetze in denselben Absatz integriert, nicht als separate Zeilen im Markdown-Sinn (das schien mir die gemeinte Lesart von "in zwei Zeilen", da die Datei insgesamt kuerzer werden musste).
- Satz zur Ueberlagerung als Nicht-Sicherheitsnetz mit der `shortcut.create()`-Kindprozess-Erklaerung, explizit als **Hypothese** des `security-reviewer` markiert (belegt, nicht gegengeprueft).
- "Fester Testabzug"-Abschnitt richtiggestellt: `C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug`, 841 Dateien, 20 812 293 Bytes, `EXTRACT_VERSION` 11, gebaut von 1.9.0, Ersparnis 110,0 s ohne / 5,75 s mit; Begruendung "nicht unter `%LOCALAPPDATA%`" (QA-237) und "nicht im Projektbaum" (NH-002, A-003).
- Testbefehl-Zeile "Stand 08.09.2026: 1257 passed..." bleibt stehen, ergaenzt um "aktuell 1781 passed, 9 skipped, 0 failed (T-199)" mit dem Hinweis, dass die Differenz ungeklaert ist — nicht erklaert, wie gefordert.

## `requirements-dev.txt`

Zehnzeiligen Begruendungskopf gestrichen, `-r requirements.txt` und die beiden Pins (`pytest==9.1.1`, `pytest-xdist==3.8.0`) unveraendert erhalten.

## Scope eingehalten

Kein Anwendungscode angefasst (nichts unter `nrplanner/`, `nrdata/`). Kein teamweiter Hook (nichts unter `claude-agent-team` oder `~/.claude` veraendert — dort nur gelesen, zur Formuebernahme). Keine Konfigurationsebene: die drei Variablennamen stehen als Literale im Hook (Zeilen 58-60), keine Liste, aus der sie gelesen werden. Fuenf beruehrte Dateien, wie in der Auftragsdatei vorgegeben.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (oben).
- [x] Der Hook selbst mit sieben Kommandozeilen-Faellen direkt geprueft (siehe oben) — das ist keine `pytest`-Suite, da PowerShell-Hooks in diesem Projekt keine eigene Testinfrastruktur haben; die Pruefung erfolgte durch dieselbe stdin-JSON-Schnittstelle, die Claude Code selbst benutzt.
- [x] Volle Suite lief im Zuge dieses Auftrags real durch: `1781 passed, 9 skipped in 130.77s` — deckt sich mit der in CLAUDE.md dokumentierten aktuellen Zahl. Kein Linter im Projekt konfiguriert (kein Punkt, keine Luecke).
- [x] Keine Secrets, keine TODOs, kein toter Code. Der `ponytail:`-Kommentar im Hook benennt die Decke und den Weg nach oben, wie gefordert — das ist Dokumentation einer bewussten Vereinfachung, kein Schuldenposten.
- [ ] QA-Akzeptanz nicht durchgespielt — der Auftrag hat keine QA-Uebergabe vorgesehen (Stufe "klein", kein Fensterlauf, "Parallel: Nein").
- [x] Doku (`CLAUDE.md`) aktualisiert, Bericht abgelegt.

**Ungepruefte Plattformen:** Linux/macOS wie immer kein Ziel. Der Hook selbst ist PowerShell-5.1-spezifisch (wie die beiden Vorbilder) und nur fuer Windows gedacht — passt zum Zielsystem.

## Offene Punkte / Risiken (an director)

1. **`$CLAUDE_PROJECT_DIR` in `.claude/settings.json` ist unter Annahme eingesetzt**, nicht end-to-end in einer echten Session verifiziert (ein echter `python run.py`-Aufruf wurde vom Auto-Mode-Classifier der Umgebung abgewiesen, bevor er den PreToolUse-Hook haette erreichen koennen — das ist eine andere Sperre als die hier gebaute). Sollte die Variable in der tatsaechlichen Claude-Code-Registrierung anders heissen oder nicht existieren, greift der Hook fuer PowerShell-Aufrufe unter diesem Projekt gar nicht (stiller Ausfall, keine Fehlermeldung), waehrend `no-root-find.ps1`/`block-source-read.ps1` im Team-Repo diese Variable gar nicht brauchen (sie liegen fest unter `~/.claude/hooks/` und werden mit absoluten Pfaden registriert). **Empfehlung:** beim naechsten echten Fensterlauf (T-Nummer noch offen) einmal bewusst pruefen, ob der Hook tatsaechlich feuert — z. B. indem der Fensterlauf-Auftrag absichtlich zuerst ohne alle drei Variablen startet und das Deny im Transcript zeigt.
2. **Die Positivliste der Startformen ist eng** (nur `run.py` und `NightreignHelper.exe`). Das ist Absicht (Vorgabe 3: aus dem Repository ableiten, nicht raten) und im `ponytail:`-Kommentar als Decke benannt — aber jede Rolle, die eine neue Startform einfuehrt (z. B. ein `power-user`-Fensterlauf ueber einen Installer), muss den Hook erweitern lassen, sonst laeuft sie ungeprueft durch die Luecke, nicht durch den Waechter.
3. Die Formulierung "in zwei Zeilen" aus Vorgabe 5 habe ich als "zwei Saetze, die die Unterscheidung tragen" gelesen, nicht als exakt zwei Markdown-Zeilen — weil eine isolierte Zwei-Zeilen-Passage die Gesamtkuerzung gefaehrdet haette. Wenn das nicht die gemeinte Lesart war, bitte ich um eine kurze Korrektur statt eigenmaechtiger Nacharbeit.

## An ui-ux-designer

Nicht betroffen — keine Oberflaechenaenderung.

## An qa-engineer

Nicht betroffen im Sinne einer Test-/Fensterlauf-Uebergabe (kein Anwendungscode, "Parallel: Nein"). Fuer den naechsten Fensterlauf-Auftrag relevant: der Programmstart muss jetzt alle drei Variablen in **derselben Kommandozeile** setzen, sonst weist der Hook ab, bevor irgendein Prozess startet — das ersetzt den bisherigen Nach-dem-Lauf-Nachweis vollstaendig.
