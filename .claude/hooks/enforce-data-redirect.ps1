# enforce-data-redirect.ps1
# PreToolUse-Hook auf Bash|PowerShell, projekteigen (nur Nightreign-Helper).
#
# WARUM ES DIESEN HOOK GIBT
#
# CLAUDE.md verlangt von jeder Rolle, die das Programm startet, drei
# Umlenkungen (NIGHTREIGN_SETTINGS_ORG, LOCALAPPDATA, APPDATA) - sonst
# schreibt der Lauf in die echten 309 Relikte und rund 110 Builds des
# Nutzers. Der bisherige Nachweis dafuer (nach dem Lauf zeigen, dass unter
# dem echten Pfad nichts entstanden ist) haelt nicht: Schreibvorgaenge unter
# dem echten %LOCALAPPDATA% landen in einer Ueberlagerung, die alle
# Claude-Sitzungen teilen, und wer darin sitzt liest seine eigenen
# Schreibvorgaenge immer erfolgreich zurueck (QA-237). T-196 hat genau
# diesen Schein als Nachweis gemeldet und den Auftrag verloren.
#
# Der Nutzer hat entschieden: Waechter statt Nachweispflicht (12.09.2026).
# Dieser Hook weist jeden erkannten Programmstart ohne alle drei Variablen
# in derselben Kommandozeile ab - der Beleg ist, dass der Hook nicht
# ausgeloest hat, nicht mehr ein Blick in ein Verzeichnis.
#
# PLATTFORMGRENZE (QA-241, gemessen 15.09.2026): settings.json ruft diesen
# Hook ueber "$CLAUDE_PROJECT_DIR/.claude/hooks/...ps1" auf. In der Umgebung
# eines Subagenten (Task-Tool) ist $CLAUDE_PROJECT_DIR leer - Beleg: `echo
# $CLAUDE_PROJECT_DIR` liefert in einer Subagenten-Bash-Sitzung nichts, und
# der so gebaute Pfad ("/.claude/hooks/...") loest unter Git Bash auf die
# Git-Installation statt das Projekt auf ("C:/Program Files/Git/.claude/...").
# PowerShell findet die Datei nicht, bricht vor der ersten Zeile dieses
# Skripts ab, und der Zug laeuft ohne deny durch - die Logik unten ist davon
# nicht betroffen (per stdin direkt geprueft: korrekt). Kein Fix im Skript
# moeglich, das Skript startet in diesem Fall nie. Bis Claude Code
# $CLAUDE_PROJECT_DIR fuer Subagenten setzt, bleibt die Umlenkung fuer jede
# Rolle, die aus einem Subagenten heraus einen Programmstart ausloest,
# Handregel (CLAUDE.md, Abschnitt "Datenverzeichnisse und Umlenkung").
#
# Bewusst ohne Umlaute (PowerShell 5.1 / kein BOM).

$ErrorActionPreference = 'SilentlyContinue'

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }
try { $p = $raw | ConvertFrom-Json } catch { exit 0 }

$tool = [string]$p.tool_name
if ($tool -notin @('Bash', 'PowerShell')) { exit 0 }

$cmd = [string]$p.tool_input.command
if (-not $cmd) { exit 0 }

# Kommentare zuerst weg, sonst zaehlt eine blosse Erwaehnung der Variablen
# in einer Zeile wie "# braucht LOCALAPPDATA" bereits als Umlenkung.
$cmd = (($cmd -split "`n") | ForEach-Object { $_ -replace '#.*$', '' }) -join ' '

# pytest stellt seine Umgebung per monkeypatch her und braucht die drei
# Variablen nicht in der Kommandozeile (Vorgabe 2). Ein pytest-Aufruf ist nie
# ein Programmstart im Sinne dieses Hooks.
if ($cmd -match '\bpytest\b') { exit 0 }

# ponytail: erkannte Startformen, aus dem Repository abgeleitet (run.py,
# NightreignHelper.spec, die Fensterlaeufe in T-199/T-200, die beiden
# fensterbauenden Messskripte aus QA-244/T-214) - nicht aus Vorstellung. Eine
# Startform, die hier nicht steht, rutscht durch: kein Start-Process, kein
# "python -c ...nrplanner.app...", kein Doppelklick auf die .exe (das ist
# ohnehin kein Werkzeugaufruf). Taucht eine neue Startform in einem Bericht
# auf, kommt sie hier als weiteres $ist*-Pattern dazu.
# Kein Anker auf Zeilenanfang: "VAR=wert VAR2=wert python run.py" ist ein
# einzelnes Kommando ohne Trenner vor "python" und muss trotzdem greifen.
$istQuellstart = $cmd -match '\b(python3?|py)(\.exe)?\b[^;&|]*\brun\.py\b'
$istExeStart = $cmd -match '(?i)\bNightreignHelper\.exe\b'

# QA-244: von den acht Skripten unter scripts/measure_*.py bauen nur diese
# zwei ein echtes Planner-Fenster (appmod.Planner(...), nachgesehen T-214) und
# lenken NIGHTREIGN_SETTINGS_ORG nicht selbst um. Die anderen sechs oeffnen
# kein Fenster und ruehren an keiner der drei Variablen - ein Muster auf den
# ganzen Ordner wuerde sie ohne Grund abweisen. Baut ein kuenftiges Skript ein
# Fenster, kommt sein Name hier dazu, nicht ein Wildcard auf den Ordner.
$istFensterMessskript = $cmd -match
    '\b(python3?|py)(\.exe)?\b[^;&|]*\b(measure_picker_cards|measure_advisor_block)\.py\b'

if (-not ($istQuellstart -or $istExeStart -or $istFensterMessskript)) { exit 0 }

$fehlend = @()
if ($cmd -notmatch '\bNIGHTREIGN_SETTINGS_ORG\b\s*=') { $fehlend += 'NIGHTREIGN_SETTINGS_ORG' }
if ($cmd -notmatch '\bLOCALAPPDATA\b\s*=') { $fehlend += 'LOCALAPPDATA' }
if ($cmd -notmatch '\bAPPDATA\b\s*=') { $fehlend += 'APPDATA' }

if ($fehlend.Count -eq 0) { exit 0 }

$msg = "[datenumlenkung] Programmstart ohne vollstaendige Umlenkung: " +
       "$($fehlend -join ', ') fehlt in dieser Kommandozeile. Setze " +
       "NIGHTREIGN_SETTINGS_ORG, LOCALAPPDATA und APPDATA in derselben " +
       "Kommandozeile wie den Start (CLAUDE.md, Abschnitt " +
       "'Datenverzeichnisse - und die Sperre davor')."

$out = @{
    hookSpecificOutput = @{
        hookEventName            = 'PreToolUse'
        permissionDecision       = 'deny'
        permissionDecisionReason = $msg
    }
}
[Console]::Out.WriteLine(($out | ConvertTo-Json -Compress -Depth 5))
exit 0
