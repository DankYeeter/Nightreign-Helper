# drive_window.ps1
# UIA-Fenstertreiber fuer eine laufende Nightreign-Helper-Instanz. Dot-sourcen,
# nicht ausfuehren - die Funktionen bleiben danach in der Sitzung erreichbar:
#
#   . scripts\drive_window.ps1 -Org $env:NIGHTREIGN_SETTINGS_ORG
#   $m = Main; Dump $m                          # UIA-Baum des Hauptfensters
#   Click ((Els $m '^Optimize$' 'Button')[0])    # Klick per echter Mausposition
#   Shot $m out.png                              # PrintWindow-Bildnachweis
#
# NH-009 (Retrospektive Zyklus 27, docs/berichte/T-297-retrospective.md
# Vorschlag 3): das Rezept - Fenster finden, per Alt-Trick in den
# Vordergrund holen, per GetWindowRect-Koordinaten klicken, Text per UIA
# lesen - stand in 15 Berichten und wurde in T-290b erneut teuer entdeckt.
# Aus dem Treiber der QA-Laeufe T-285/T-290b/T-293b uebernommen. Bei
# Luecken (fehlende Funktion, neues Steuerelement) einen Befund an den
# developer, nicht selbst neu bauen.
#
# Setzt eine bereits laufende, umgelenkte Instanz voraus
# (NIGHTREIGN_SETTINGS_ORG/LOCALAPPDATA/APPDATA gemaess CLAUDE.md, Abschnitt
# "Datenverzeichnisse und die Sperre davor"). Dieses Skript selbst startet
# nichts und schreibt nichts - Reg liest nur HKCU\Software\<Org>\
# NightreignHelper; ohne -Org bzw. NIGHTREIGN_SETTINGS_ORG zeigt Reg auf
# keinen echten Schluessel (kein Zugriff auf die echten Nutzerdaten).
# Bewusst ohne Umlaute (PowerShell 5.1 / kein BOM).

param([string]$Org = $env:NIGHTREIGN_SETTINGS_ORG)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class W4 {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, int dx, int dy, uint data, UIntPtr extra);
    [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr ctx);
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    [DllImport("user32.dll")] public static extern IntPtr WindowFromPoint(POINT p);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
    public struct RECT { public int L, T, R, B; }
    public struct POINT { public int X, Y; }
    public static List<IntPtr> Windows(uint pid) {
        var r = new List<IntPtr>();
        EnumWindows((h, l) => { uint p; GetWindowThreadProcessId(h, out p); if (p == pid && IsWindowVisible(h)) r.Add(h); return true; }, IntPtr.Zero);
        return r;
    }
    public static string Title(IntPtr h) { var s = new StringBuilder(256); GetWindowText(h, s, 256); return s.ToString(); }
    public static string Cls(IntPtr h) { var s = new StringBuilder(256); GetClassName(h, s, 256); return s.ToString(); }
}
'@
[W4]::SetThreadDpiAwarenessContext([IntPtr](-4)) | Out-Null
$A = [System.Windows.Automation.AutomationElement]
$TS = [System.Windows.Automation.TreeScope]
$PIDW = (Get-Process NightreignHelper | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1).Id
function Main {
    $ws = [W4]::Windows([uint32]$script:PIDW)
    foreach ($h in $ws) { if ([W4]::Cls($h) -eq "Qt6111QWindowIcon" -and [W4]::Title($h) -like "Nightreign Helper*") { return $A::FromHandle($h) } }
    foreach ($h in $ws) { if ([W4]::Title($h) -like "Nightreign Helper*") { return $A::FromHandle($h) } }
    throw "main window not found"
}
function TopWin($titleLike) {
    foreach ($h in [W4]::Windows([uint32]$script:PIDW)) { if ([W4]::Title($h) -like $titleLike) { return $A::FromHandle($h) } }
    return $null
}
function ListTop { foreach ($h in [W4]::Windows([uint32]$script:PIDW)) { "{0} | {1} | {2}" -f $h, [W4]::Cls($h), [W4]::Title($h) } }
function Els($root, $name = "", $ctrl = "", $cls = "") {
    $out = @()
    $all = $root.FindAll($TS::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($e in $all) {
        $c = $e.Current
        if (($name -eq "" -or $c.Name -match $name) -and ($ctrl -eq "" -or $c.ControlType.ProgrammaticName -match $ctrl) -and ($cls -eq "" -or $c.ClassName -match $cls)) { $out += $e }
    }
    return ,$out
}
function Desc($e) { $c = $e.Current; $r = $c.BoundingRectangle; "{0} | {1} | '{2}' | en={3} off={4} | {5},{6} {7}x{8}" -f $c.ControlType.ProgrammaticName, $c.ClassName, $c.Name, $c.IsEnabled, $c.IsOffscreen, [int]$r.X, [int]$r.Y, [int]$r.Width, [int]$r.Height }
function Dump($root, $name = "", $ctrl = "", $cls = "") { foreach ($e in (Els $root $name $ctrl $cls)) { Desc $e } }
function Fg($e) {
    $h = [IntPtr]$e.Current.NativeWindowHandle
    if ($h -eq [IntPtr]::Zero) { $h = [IntPtr](Main).Current.NativeWindowHandle }
    for ($i = 0; $i -lt 6; $i++) {
        if ([W4]::GetForegroundWindow() -eq $h) { return $true }
        [W4]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero); [W4]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
        [W4]::SetForegroundWindow($h) | Out-Null; Start-Sleep -Milliseconds 150
    }
    return ([W4]::GetForegroundWindow() -eq $h)
}
function ClickAt($x, $y) {
    $pt = New-Object W4+POINT; $pt.X = [int]$x; $pt.Y = [int]$y
    $h = [W4]::WindowFromPoint($pt); [uint32]$p = 0; [W4]::GetWindowThreadProcessId($h, [ref]$p) | Out-Null
    if ($p -ne $script:PIDW) { return "GUARD: point $x,$y belongs to pid $p not $script:PIDW" }
    [W4]::SetCursorPos([int]$x, [int]$y) | Out-Null; Start-Sleep -Milliseconds 60
    [W4]::mouse_event(0x0001, 1, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 40
    [W4]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 60
    [W4]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 250
    return "clicked $x,$y"
}
function Click($e, $dx = 0, $dy = 0) {
    $w = $e; try { $top = [System.Windows.Automation.TreeWalker]::ControlViewWalker } catch {}
    $r = $e.Current.BoundingRectangle
    ClickAt ($r.X + $r.Width/2 + $dx) ($r.Y + $r.Height/2 + $dy)
}
function Invoke-El($e) { $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 300 }
function Toggle-El($e) { $p = $e.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern); $b = $p.Current.ToggleState; $p.Toggle(); Start-Sleep -Milliseconds 300; "toggle $b -> $($p.Current.ToggleState)" }
function ToggleState($e) { $e.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState }
function SetText($e, $t) { $e.SetFocus(); Start-Sleep -Milliseconds 100; $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($t); Start-Sleep -Milliseconds 400 }
function Shot($e, $out) {
    $h = [IntPtr]$e.Current.NativeWindowHandle
    $g0 = New-Object W4+RECT; [W4]::GetWindowRect($h, [ref]$g0) | Out-Null
    $w = $g0.R - $g0.L; $ht = $g0.B - $g0.T
    $bmp = New-Object System.Drawing.Bitmap $w, $ht
    $g = [System.Drawing.Graphics]::FromImage($bmp); $hdc = $g.GetHdc()
    [W4]::PrintWindow($h, $hdc, 2) | Out-Null; $g.ReleaseHdc($hdc)
    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
    "saved $out ($w x $ht)"
}
function Texts($root, $name = "") { foreach ($e in (Els $root $name "Text")) { $e.Current.Name } }
function SlotButtons {
    for ($i = 0; $i -lt 20; $i++) {
        $m = Main
        $s = @()
        foreach ($e in (Els $m "" "Button" "QPushButton")) { if ($e.Current.BoundingRectangle.Width -gt 800) { $s += $e } }
        if ($s.Count -ge 3) { return ,$s }
        Start-Sleep -Milliseconds 500
    }
    return ,@()
}
function Rows($f) {
    # group TreeItem cells by their Y into rows: returns list of @{Y; Cells(array by X)}
    $items = Els $f "" "TreeItem"
    $rows = @{}
    foreach ($e in $items) { $r = $e.Current.BoundingRectangle; if ($r.Width -le 0) { continue }; $y = [int]$r.Y; if (-not $rows.ContainsKey($y)) { $rows[$y] = @() }; $rows[$y] += $e }
    $out = @()
    foreach ($y in ($rows.Keys | Sort-Object)) { $cells = $rows[$y] | Sort-Object { $_.Current.BoundingRectangle.X }; $out += ,@{Y=$y; Cells=$cells} }
    return ,$out
}
function RowText($row) { ($row.Cells | ForEach-Object { $x=[int]$_.Current.BoundingRectangle.X; "${x}:'$($_.Current.Name)'" }) -join " " }
function CellState($e) { try { return [string]($e.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState) } catch { return "-" } }
function CountLine($f) { (Texts $f "of 340") -join "" }
function FindRow($f, $nameRegex) { foreach ($r in (Rows $f)) { foreach ($c in $r.Cells) { if ($c.Current.Name -match $nameRegex) { return $r } } }; return $null }
function ClickCell($f, $nameRegex, $col) {
    # col: 0 Favourite, 1 Avoid, 2 Allow
    $r = FindRow $f $nameRegex
    if ($r -eq $null) { return "ROW NOT FOUND $nameRegex" }
    $c = $r.Cells[$col]; $b = $c.Current.BoundingRectangle
    Fg $f | Out-Null
    return ("row " + $nameRegex + " col $col " + (ClickAt ($b.X + 12) ($b.Y + $b.Height/2)))
}
function Reg { $k = "HKCU:\Software\$script:Org\NightreignHelper"; if (Test-Path $k) { $p = Get-ItemProperty "$k\advisor" -ErrorAction SilentlyContinue; if ($p) { foreach ($n in @("excluded","required","allowed","avoided_families")) { "  advisor/$n = [" + ($p.$n -replace "`n", " ; ") + "]" } } else { "  no advisor key" } } else { "  no org key" } }
function OpenFilters { $f = TopWin "Effect filters*"; if ($f -eq $null) { Invoke-El ((Els (Main) "^Filters$" "Button")[0]); Start-Sleep -Milliseconds 1500; $f = TopWin "Effect filters*" }; return $f }
function CloseWin($w) { $w.GetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern).Close(); Start-Sleep -Milliseconds 800 }
function Optimize {
    $m = Main
    Invoke-El ((Els $m "^Optimize$" "Button")[0])
    for ($i = 0; $i -lt 60; $i++) { Start-Sleep -Milliseconds 500; $w = Els (Main) "^Why$" "Button"; if ($w.Count -gt 0) { break } }
    Start-Sleep -Milliseconds 800
    "optimize done after $i x 0.5 s, Why buttons: $($w.Count)"
}
function Blocks { Texts (Main) "^Slot|^Deep Slot|SUGGESTED|held in Slot|favourited|already|nothing to choose|filled|Nothing suggested|^Maximise" }
