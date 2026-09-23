# no-window-dispatch.ps1
# PreToolUse-Hook (Matcher "Agent|Task"), projekteigen (nur Nightreign-Helper).
#
# NH-008 (Retrospektive Zyklus 27, docs/berichte/T-297-retrospective.md
# Vorschlag 2): NH-004 sitzt am Start, nicht am Dispatch - eine Rolle, die
# ein Fensterlauf-Auftrag erreicht waehrend eine fremde Kopie noch laeuft,
# wartet auf sie (T-241d 23 min, T-285a 28 min, T-290b ~20 min). Dieser Hook
# weist den Dispatch selbst ab, bevor die Rolle wartet.
#
# Trifft der Dispatch eine Fensterrolle und laeuft eine Kopie von Nightreign
# Helper, wird der Dispatch abgewiesen. Kein Auftrag verlangt Warten - der
# Director reiht den Fensterlauf stattdessen.
#
# Nachtrag 21.09.2026 (NH-010): die erste Fassung prueft nur Woerter im
# Prompt. Ein researcher- und zwei ui-ux-designer-Dispatches, die andere
# Rollen nur erwaehnten, wurden abgewiesen; T-324f lag 76 min. Jetzt
# entscheidet zuerst die Rolle: qa-engineer und power-user fahren immer das
# Fenster; developer und release-manager nur, wenn der Auftrag es sagt; alle
# anderen Rollen passieren ohne Pruefung.
# Bewusst ohne Umlaute (PowerShell 5.1 / kein BOM).

$ErrorActionPreference = 'SilentlyContinue'

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }
try { $p = $raw | ConvertFrom-Json } catch { exit 0 }
if ([string]$p.tool_name -notin @('Agent', 'Task')) { exit 0 }

$prompt = [string]$p.tool_input.prompt
$rolle  = [string]$p.tool_input.subagent_type

switch ($rolle) {
    { $_ -in @('qa-engineer', 'power-user') } { }
    'developer'       { if ($prompt -notmatch '(?i)Fensterlauf|am Fenster|drive_window') { exit 0 } }
    'release-manager' { if ($prompt -notmatch '(?i)clean-room|\bbuild\b|Rauchtest|Fensterlauf|am Artefakt') { exit 0 } }
    default           { exit 0 }
}

$laeuft = @(Get-Process -Name NightreignHelper -ErrorAction SilentlyContinue)
$laeuft += @(Get-Process -Name python, pythonw -ErrorAction SilentlyContinue |
             Where-Object { $_.MainWindowTitle -like 'Nightreign Helper*' })
if ($laeuft.Count -eq 0) { exit 0 }

$wer = ($laeuft | ForEach-Object { "$($_.ProcessName) PID $($_.Id) seit $($_.StartTime.ToString('HH:mm:ss'))" }) -join ', '
$out = @{ hookSpecificOutput = @{
    hookEventName            = 'PreToolUse'
    permissionDecision       = 'deny'
    permissionDecisionReason = "Nightreign Helper laeuft bereits ($wer); warte selbst oder gib Arbeit ohne Programmstart; kein Auftrag verlangt 'warten'."
} } | ConvertTo-Json -Depth 4 -Compress
[Console]::Out.WriteLine($out)
exit 0
