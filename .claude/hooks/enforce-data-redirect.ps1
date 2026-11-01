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
# PLATTFORMGRENZE (QA-241, behoben T-270b, 15.09.2026): settings.json rief
# diesen Hook zuvor ueber "$CLAUDE_PROJECT_DIR/.claude/hooks/...ps1" auf. In
# der Umgebung eines Subagenten (Task-Tool) ist $CLAUDE_PROJECT_DIR leer, der
# so gebaute Pfad loeste unter Git Bash auf die Git-Installation statt das
# Projekt auf, PowerShell fand die Datei nicht und der Zug lief ohne deny
# durch. Seit T-270b ruft settings.json diese Datei relativ zum Arbeits-
# verzeichnis auf ("-Command \"if (Test-Path .claude/hooks/...) { & ... }
# else { exit 2 }\""); die Arbeitsverzeichnisse von Haupt-, Subagenten- und
# Worktree-Sitzungen zeigen alle auf die jeweilige Projekt- bzw. Worktree-
# Wurzel, in der diese Datei liegt. Fehlt die Datei trotzdem (z. B. ein
# Checkout ohne .claude/), liefert der else-Zweig exit 2 (Block) statt still
# durchzulassen. Keine Handregel mehr fuer diesen Fall.
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
#
# NH-011 (T-330a): der Interpreter muss an Befehlsstelle stehen (Zeilenanfang,
# nach ; & | ( oder nach einem Leerzeichen wie in "VAR=wert python run.py"),
# und das Skript muss sein erstes Argument nach Optionen sein. Die alten
# Masken ("python" irgendwo, Skriptname irgendwo dahinter) wiesen am 22.09.
# sieben Befehle ab, von denen keiner ein Fenster startete: Heredocs, die
# advisor/run.py bearbeiten, "python -m pyflakes ... run.py", Grep-Muster,
# 'run.py' in einer Liste, ein Hilfsskript mit measure_*.py als Argument.
# tests/test_redirect_hook_masks.py haelt diese Faelle als Literale.
$istQuellstart = $cmd -match '(?i)(^|[;&|(]\s*|\s)["'']?(\S*[\\/])?(python3?|pythonw|py)(\.exe)?["'']?\s+((-[A-Za-z]+|-X\s+\S+)\s+)*["'']?(\.[\\/])?run\.py\b|Start-Process\b[^;&|]*\b(python3?|pythonw|py)(\.exe)?\b[^;&|]*[\s"'',](\.[\\/])?run\.py\b'

# NH-004/NH-007 (T-297, sieben Fehlalarme 16.-17.09.): eine blosse Nennung der
# EXE (ls, Get-FileHash) ist kein Start - nur Startformen, in denen die EXE
# das Kommando ist, zaehlen. Dieselbe Maske bedient jetzt beide Gates: das
# Umlenkungs-Gate unten und die Instanzsperre (die Instanzsperre ist
# maschinenweit, nrplanner/singleinstance.py, KEY; ein zweiter Start endet
# stumm und die Rolle wartet - T-241d 23 min, T-285a 28 min. Bei laufender
# Kopie wird der Start abgewiesen, damit die Rolle sofort `blockiert` meldet
# statt zu pollen).
# T-330a Nebenfund: [;&|(] in einem Grep-Muster ("foo|NightreignHelper.exe")
# zaehlte als Befehlsgrenze. T-332b blendete darum Grenzzeichen in jedem
# Anfuehrungszeichen-Text aus - und damit auch verschachtelte Starts
# (powershell -Command "cd dist; .\NightreignHelper.exe", cmd /c, bash -c;
# SEC-052). Jetzt nur noch in den Argumenten eines Suchbefehls (grep, rg,
# Select-String): Wortfolge bis zur ersten Grenze ausserhalb von
# Anfuehrungszeichen. Alles andere wird ungeblendet abgeglichen.
$cmdFuerExeAbgleich = [regex]::Replace($cmd,
    '(?i)(?<![\w-])(grep|rg|Select-String)(\s+("[^"]*"|''[^'']*''|[^\s"'';&|(]+))*',
    { param($m) $m.Value -replace '[;&|(]', ' ' })

$istExeKommando = $cmdFuerExeAbgleich -match '(?i)(^|[;&|(]\s*|Start-Process\s+(-FilePath\s+)?|&\s+)["'']?([^\s"'']*[\\/])?NightreignHelper\.exe["'']?(\s|$)'

# QA-244: von den acht Skripten unter scripts/measure_*.py bauen nur diese
# zwei ein echtes Planner-Fenster (appmod.Planner(...), nachgesehen T-214) und
# lenken NIGHTREIGN_SETTINGS_ORG nicht selbst um. Die anderen sechs oeffnen
# kein Fenster und ruehren an keiner der drei Variablen - ein Muster auf den
# ganzen Ordner wuerde sie ohne Grund abweisen. Baut ein kuenftiges Skript ein
# Fenster, kommt sein Name hier dazu, nicht ein Wildcard auf den Ordner.
# Dieselbe Befehlsstellen-Form wie $istQuellstart; das Skript liegt unter
# scripts/, darum ein beliebiger Ordnervorsatz statt nur ".\".
$istFensterMessskript = $cmd -match
    '(?i)(^|[;&|(]\s*|\s)["'']?(\S*[\\/])?(python3?|pythonw|py)(\.exe)?["'']?\s+((-[A-Za-z]+|-X\s+\S+)\s+)*["'']?(\S*[\\/])?(measure_picker_cards|measure_advisor_block)\.py\b|Start-Process\b[^;&|]*\b(python3?|pythonw|py)(\.exe)?\b[^;&|]*[\s"'',](\S*[\\/])?(measure_picker_cards|measure_advisor_block)\.py\b'

if (-not ($istQuellstart -or $istExeKommando -or $istFensterMessskript)) { exit 0 }

# Ab hier ist mindestens eine der drei Startformen erkannt (siehe Gate oben) -
# die Instanzsperre prueft immer, kein eigenes Gate mehr noetig.
$laeuft = @(Get-Process -Name NightreignHelper -ErrorAction SilentlyContinue)
$laeuft += @(Get-Process -Name python, pythonw -ErrorAction SilentlyContinue |
             Where-Object { $_.MainWindowTitle -like 'Nightreign Helper*' })
if ($laeuft.Count -gt 0) {
    $wer = ($laeuft | ForEach-Object { "$($_.ProcessName) PID $($_.Id) seit $($_.StartTime.ToString('HH:mm:ss'))" }) -join ', '
    $out = @{ hookSpecificOutput = @{
        hookEventName = 'PreToolUse'; permissionDecision = 'deny'
        permissionDecisionReason = "[instanzsperre] Nightreign Helper laeuft bereits ($wer); ein zweiter Start endet stumm (QA-256). Nicht warten, kein Stop-Process auf fremde PIDs: STATUS blockiert melden, der Director reiht die Fensterlaeufe." } }
    [Console]::Out.WriteLine(($out | ConvertTo-Json -Compress -Depth 5)); exit 0
}

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
