STATUS: erledigt
AUFTRAG: T-313c - Retest QA-288 (UIA-Toggle, Leertaste, Mausklick) am neuen
Artefakt 1.15.0 (`dist\NightreignHelper.exe`, Code `6edab2e`, 59.151.716 B,
SHA-256 `1D4197DF0F0C765B507CCA824FBA480DBCFCA76C482CF3F7A852B199CB6BBDF0`),
plus Stichprobe Fell Omen/Runebear unveraendert
GELESEN: docs/tasks/T-313.md (vollstaendig); docs/berichte/T-312-qa-engineer.md
(QA-288-Abschnitt, Vorgehen); docs/berichte/T-313-release-manager.md
(Artefaktdaten); qa/findings.md (Tabellenkopf + Endstand, letzte Nummer
QA-288); nrplanner/bosstab.py Z. 840-995 (Fix: `loot_button.toggled.connect`
statt `clicked`, Kommentar nennt QA-288 und den Grund - `TogglePattern.Toggle()`
loest nur `toggle()`/`toggled`, nicht `clicked`); scripts/drive_window.ps1
(Volltext, Treiberrezept)
GEAENDERT: nichts im Arbeitsbaum. `docs/berichte/T-313-qa-engineer.md` (dieser
Bericht, neu). Kein Eintrag in `qa/findings.md` durch mich selbst - Zeile am
Ende dieses Berichts als QA-Log zum Anhaengen. Scratchpad:
`<Scratchpad>/T-313/qa-engineer/` (LOCALAPPDATA/APPDATA mit Testabzug 841
Dateien/21.131.645 B)
ANNAHMEN: keine
NAECHSTER: director (Freigabe T-313d, Release-Notes-Auftrag)
BLOCKIERT DURCH: nichts

---

# T-313c - qa-engineer: Retest QA-288

## Vorgehen

Artefakt-Hash/-Groesse gegen den Bericht des release-manager gegengeprueft
(deckungsgleich). Start mit `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-313c`,
`LOCALAPPDATA`/`APPDATA` auf frische Scratchpad-Ordner umgelenkt, Testabzug
(841 Dateien, 21.131.645 B) vorher hineinkopiert. Fenstertreiber
`scripts/drive_window.ps1` dot-gesourct, Fenster maximiert (sonst UIA-
Klickkoordinaten ausserhalb des sichtbaren Bereichs, bekannte Werkzeuggrenze
aus T-312c).

## Retest QA-288

Nightlords-Tab -> Gladius -> Feldboss Fell Omen (HP 2521, Loot-Liste
deckungsgleich mit T-312c) -> Knopf "Show 15 more" (UIA-`ControlType` ist
`CheckBox`, nicht `Button` - `QToolButton.setCheckable(True)` wird von der
Qt-Accessibility-Bruecke als CheckBox abgebildet, ein Werkzeugdetail, kein
Befund).

1. **UIA `TogglePattern.Toggle()`:** Zustand vorher `Off`, nach `Toggle()`
   `On`; Beschriftung wechselt sofort zu "Show fewer", Liste erweitert sich
   live auf 20 Eintraege. Vorher (QA-288) keine Reaktion.
2. **Leertaste im Fokus:** `SetFocus()` auf den Knopf, `IsKeyboardFocusable`
   = `True`, `HasKeyboardFocus` nach `SetFocus()` = `True`; echter
   `keybd_event` VK_SPACE klappt die Liste zurueck auf "Show 15 more".
3. **Echter Mausklick:** `SetCursorPos`+`mouse_event` auf denselben Knopf
   klappt zurueck auf "Show fewer" - unveraendert wie in T-312c.

Alle drei Weg fuehren zu identischem, korrektem Ergebnis (Beschriftung und
Listenlaenge synchron). QA-288 **behoben**.

Regressionstest `tests/test_nightlord_panel_display.py` (T-313a-Ergaenzung):
**20 passed in 35,15 s**, keine Fehlschlaege.

## Stichprobe Fell Omen/Runebear unveraendert

- **Fell Omen** (Feldboss, Gladius): HP 2521, WEAKNESS/STANCE/STATUS-Werte
  und die fuenf Basis-Loot-Zeilen (`All Resistances Up` .. `Ice Storm Surge
  Sprint`, je 5 %) deckungsgleich mit dem A24-Nachweis aus T-312c.
- **Runebear** (Nachtboss Day 1, unter Straghess - in T-312c nicht namentlich
  gefunden, hier lokalisiert): Rollenzeile "Night boss · Day 1", HP 640,
  Loot-Liste (`Vyke's War Spear` .. `Eclipse Crest Greatshield`) plausibel
  befuellt, kein Ausreisser gegenueber dem sonstigen Panelformat.

Kein Befund an diesen beiden Stichproben.

## Prozess

`Get-Process NightreignHelper` vor dem Start: 0 Treffer. Nach dem Test
`Stop-Process -Force`, danach erneut geprueft: **0 Treffer** (NH-004
belegt).

## Nicht getestet

- Vollstaendige Testsuite (`pytest -n auto`) - Auftrag begrenzt den Umfang
  ausdruecklich auf QA-288 plus Stichprobe; nur die betroffene Testdatei
  gezielt gelaufen.
- Alle uebrigen AK-319..326-Punkte, Erstlauf-Schranke (QA-287) - ausserhalb
  des Auftragsumfangs, bereits in T-312c geprueft, hier nicht erneut
  angefasst.

## Zusammenfassung (an director)

QA-288 am Artefakt 1.15.0 (`6edab2e`) **behoben** - UIA-Toggle, Leertaste
und Mausklick fuehren jetzt alle drei zum selben Ergebnis. Keine neuen
Befunde, keine Regression an der Stichprobe Fell Omen/Runebear. `Get-Process
NightreignHelper` nach Testende = 0.

**Gesamturteil: PASS** - kein P1/P2-Befund, Retestkriterium (QA-288 an allen
drei Bedienwegen) belegt erfuellt.

## Explorationsprotokoll

Fensterlauf ueber `scripts/drive_window.ps1` (UIA-Toggle, echte Tastatur,
echte Maus), ein isolierter LOCALAPPDATA-Ordner mit Testabzug, eigener
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-313c`. Fenster maximiert (sonst
Klick-Guard blockt Koordinaten ausserhalb des Fensters - Werkzeugbeobachtung,
kein Produktfehler).

## QA-Log (Anhang an `qa/findings.md`)

```
| QA-288 | **Retest T-313c (19.09.2026, qa-engineer, Artefakt 1.15.0, SHA-256 1D4197DF...BBDF0): behoben** -- UIA `TogglePattern.Toggle()` auf "Show 15 more" (Feldboss Fell Omen, `CheckBox`-Rolle): Zustand `Off`->`On`, Beschriftung "Show fewer", Liste live auf 20 Eintraege; Leertaste im Fokus (`IsKeyboardFocusable`=True) klappt zurueck; echter Mausklick unveraendert wirksam. Fix `nrplanner/bosstab.py`: `loot_button.toggled` statt `.clicked`. Regressionstest `test_nightlord_panel_display.py` 20 passed. Stichprobe Fell Omen/Runebear unveraendert, kein neuer Befund | P3 | Minor | developer | ja - 3x am Artefakt (Toggle/Leertaste/Maus), T-313c | behoben -- am Artefakt bestaetigt | 2026-09-19 |
```
