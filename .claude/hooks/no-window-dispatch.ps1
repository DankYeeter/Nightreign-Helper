# no-window-dispatch.ps1
# PreToolUse-Hook (Matcher "Agent|Task"), projekteigen (nur Nightreign-Helper).
#
# NH-008 (Retrospektive Zyklus 27, docs/berichte/T-297-retrospective.md
# Vorschlag 2): NH-004 sitzt am Start, nicht am Dispatch - eine Rolle, die
# ein Fensterlauf-Auftrag erreicht waehrend eine fremde Kopie noch laeuft,
# wartet auf sie (T-241d 23 min, T-285a 28 min, T-290b ~20 min). Dieser Hook
# weist den Dispatch selbst ab, bevor die Rolle wartet.
#
# Trifft der Dispatch-Prompt eine der Fensterrollen-Marken und laeuft eine
# Kopie von Nightreign Helper, wird der Dispatch abgewiesen. Kein Auftrag
# verlangt Warten - der Director reiht den Fensterlauf stattdessen.
# Bewusst ohne Umlaute (PowerShell 5.1 / kein BOM).

$ErrorActionPreference = 'SilentlyContinue'

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }
try { $p = $raw | ConvertFrom-Json } catch { exit 0 }
if ([string]$p.tool_name -notin @('Agent', 'Task')) { exit 0 }

$prompt = [string]$p.tool_input.prompt
if (-not $prompt) { exit 0 }

# T-297-Wortlaut: Rollennamen und die Umschreibungen, mit denen ein
# Fensterlauf im Dispatch-Prompt bisher auftrat.
if ($prompt -notmatch '(?i)qa-engineer|power-user|clean-room|Fensterlauf|am Artefakt|am Fenster') { exit 0 }

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
