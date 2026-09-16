# T-276 -- QA-279 und QA-281 reproduzieren (qa-engineer, 15.09.2026)

**Artefakt:** `dist/NightreignHelper.exe`, SHA-256 `1c8b4ff5...bb4dc88`
(gemessen 12:25 `sha256sum`, 59 123 168 B), Commit `2907a66`; `nrplanner/`
zwischen `2907a66` und HEAD `ae4d9fd` unveraendert (`git diff --stat`, leer).
**Umgebung:** Windows 11 26200, ein Bildschirm 5120x2160, 125 %; alle Masse
physisch. `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-276`, `LOCALAPPDATA`/`APPDATA`
ins Scratchpad `T-276/`, Testabzug kopiert (841 Dateien, 20 849 867 B auf
Platte). Spielstand: der echte, nur gelesen (313 Relikte, 110 Builds).
**Werkzeug:** `drive.ps1` (Scratchpad): UIA nur zum Lesen und fuer
`Rescan save`-Invoke; Klicks und Bewegungen mit `SetCursorPos` +
`mouse_event` (MOVE/DOWN/UP), Tastatur mit `keybd_event`, Thread
`DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2`; vor jedem Klick
`WindowFromPoint`-Wache auf die eigene PID. Bilder per `PrintWindow`.

**Zwei Laeufe.** 12:23-12:41 lief eine fremde Kopie des Artefakts (PID
10076/18184, Elternprozess `explorer.exe`, ohne Umlenkung -- der Nutzer
selbst); die Einzelinstanz-Sperre (`singleinstance.KEY`, maschinenweit) haette
meinen Start nur deren Fenster gehoben. Lauf A deshalb aus dem Quellbaum
(`run_window.py`: `Planner(data)` ohne `main()`, sonst identisch, PID 33488).
Nach dem Schliessen der fremden Kopie Lauf B am Artefakt (PID 4816, 12:42).
Beide Laeufe ergaben dasselbe; Zahlen unten aus Lauf B, wo vorhanden.

## QA-279 -- Raider-Kachel: **nicht reproduziert**

| Schritt | Ergebnis (Artefakt) |
|---|---|
| Spielstand angekommen (Zeile `313 relics in USER_DATA000, 110 stored builds`), echter Klick auf Kachelmitte `Raider` (2652,904) | `toggled=On`, Kelchliste `Raider's own` nach 730 ms (davon 400 ms Wartezeit des Skripts); Bild `exe_qa279_click_raider.png` |
| `Rescan save` (UIA Invoke, +11 ms) und sofort echter Klick auf `Duchess` (+71 ms) | Klick landet: `Duchess toggled=On`, Liste `Duchess's own`; Kachel `enabled=True` vor und nach; Bild `qa279_rescan_click_duchess.png` (Lauf A, am Artefakt war der UIA-Baum bei +180 ms kurz `ElementNotAvailable`, Nachlesen zeigt denselben Zustand) |
| Klick bei fremdem Vordergrundfenster (Terminal aktiv) | landet, 688 ms (Lauf A) |
| Tastatur: Tab bis Kachel (20 Tabs ab `Reset Chalice`), Space, Pfeil rechts, Space, Pfeil unten, Enter | Space waehlt (`Guardian's own`); Pfeile wandern Wylder -> Guardian -> Ironeye; **Enter waehlt nicht**; Bild `qa279_keyboard.png` |
| Tastatur direkt nach Mausklick auf eine Kachel | Fokus bleibt auf `Rescan save` (Kachel nimmt per Klick keinen Fokus, Qt-Vorgabe `TabFocus`); Pfeil/Space treffen `Rescan save`/`Load equipped` |

**AK-243:** sperrt laut Spec nur `choose_button` und `optimize_button`; die
Kacheln stehen nicht darin, `select_hero` hat keine `is_reading()`-Wache,
`enabled=True` durchgehend. Die Oberflaeche sagt nichts dazu -- muss sie auch
nicht, gesperrt ist nichts. Das Lesen dauerte hier unter 180 ms; ein Klick
"waehrend" laesst sich auf diesem Rechner nur per Zeitstempel belegen (+71 ms).

**Ursache des T-275-Befunds (Hypothesen, nicht belegt):** (a) Tastatur nach
Mausklick trifft die Kacheln nie (siehe Tabelle) -- deckt "Tastatur reagierte
nicht"; (b) veraltete Koordinaten: mein Fenster wurde waehrend Lauf A von Hand
von 48,77 nach 2623,340 verschoben, der Nutzer war am Rechner -- ein Klick auf
gemerkte Koordinaten trifft dann nichts oder die Nachbarkachel (Duchess liegt
102 px links von Raider); (c) die parallel laufende Nutzerkopie am selben Ort
(2160,780, dieselbe Groesse) faengt Klicks ab. Kein Programmfehler gefunden.

## QA-281 -- Kelch-Tooltip: **nicht reproduziert, Ursache benannt**

| Schritt | Ergebnis |
|---|---|
| Echte Bewegung (25 Schritte) auf `Guardian's Urn`, Fenster aktiv | Tooltip-HWND `Qt6111QWindowToolTipDropShadowSaveBits` 534x88 nach **814 ms**, steht 3,4 s; Text `Guardian's Urn / Slots: Red, Yellow, Yellow / Deep of Night adds: Red, Yellow, Yellow / Each vessel has its own fixed slots -- choose by colour and count, not by name.` (AK-296 1-3); Bild `exe_qa281_tooltip.png` |
| Trennzeile `Guardian's own`, Fenster aktiv | Tooltip 218x28 nach 798 ms: `Only Guardian can equip these.` (AK-296 4); Bild `qa281_separator_tooltip.png` |
| Dieselbe Bewegung, **Fenster nicht aktiv** (Terminal im Vordergrund) | kein Tooltip in 3 s (2 Versuche, Kelchzeile und Trennzeile) |
| Einzelner `SetCursorPos`-Sprung ohne MOVE-Ereignis | kein Tooltip in 3 s (2 Versuche) |
| UIA `ControlType.ToolTip` auf dem Desktop | **0** in jedem Fall, auch waehrend der Tooltip sichtbar war |

**Ursache: Simulationsgrenze, nicht Programm.** `item.toolTip()` ist gesetzt
und wird gezeichnet. Drei Bedingungen der power-user-Laeufe reichen einzeln
aus, ihn nicht zu sehen: Qt zeigt Widget-Tooltips nur im aktiven Fenster (UIA
Invoke aktiviert nicht); ein Sprung ohne Bewegungsereignisse loest kein
`QEvent::ToolTip` aus; und UIA sieht das Tooltip-Fenster gar nicht -- ein
Pruefer, der nur den UIA-Baum liest, meldet "kein Tooltip" auch bei
sichtbarem Tooltip. `setMouseTracking` ist nicht noetig (Tooltip-Ereignisse
kommen ohne gedrueckte Taste ueber den Viewport an, belegt durch den Treffer).

## Beobachtungen (keine Befunde)

- Enter waehlt eine fokussierte Kachel nicht, Space schon (Qt-Vorgabe
  `QToolButton`). Frage an ui-ux-designer, ob A-Kriterium dazu gewuenscht.
- Kacheln nehmen per Mausklick keinen Tastaturfokus (Qt `TabFocus`); die
  Kachel ist erst nach 20 Tabs erreichbar.
- Beim Start ohne Rescan stand in der UIA-Statuszeile kein `... relics in ...`
  (Lauf A, vor dem ersten Rescan); ab dem Rescan wie erwartet. Nicht verfolgt.

## Nicht getestet

Langsames Lesen (Zielgeraet 1205 ms) -- hier < 180 ms; Rechtsklick-Varianten;
andere Kacheln als Wylder/Guardian/Duchess/Raider.

## Register-Zeilen (angehaengt in `qa/findings.md`)

Siehe Zeilen `QA-279` und `QA-281` mit Datum 2026-09-15 am Tabellenende.

Bilder: `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\1102cb1a-733e-4319-a4c2-e819573c0f84\scratchpad\T-276\*.png`
(10 Dateien; Hauptfenster 2028x1122 physisch, Fensterinhalt per PrintWindow).
Prozesse 33488 (Lauf A), 23896/4816 (Lauf B) beendet; `tasklist` 12:47: 0
Nightreign-Prozesse.
