# T-335qa4 — Nachtest am Fenster (qa-engineer), 31.10.2026

Stand `cbb4da2` (Code = `35082f7`). Fenster `run.py` aus dem Quellstand,
Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT335qa4`, `LOCALAPPDATA`/`APPDATA`/
`USERPROFILE` in den Scratchpad `T-335qa4/w/`, Testabzug v18 (1027 Dateien),
eingefrorener Spielstand (sha256 `5fb89851...`). Vor dem Lauf keine
`NightreignHelper.exe` (tasklist 18:41:15); drei Starts nacheinander; am Ende
kein Fenster und kein `run.py`-Prozess (18:47:24).

**Umgebung geaendert seit T-335qa3:** Der Bildschirm ist jetzt 3840x2160 bei
225 % (Fenster-DPI 216, vorher 5120x2160 bei 125 %). 125 % und 150 % sind per
`QT_SCALE_FACTOR` 0,5556 bzw. 0,6667 nachgebildet; 225 % lief nativ.

**Korrektur zu QA-320 (T-335qa3):** "Blood Claymore 30 Arts" war falsch. Die
Pools haben 52 (Magic Longsword), 53 (Blood Claymore) und 54 (Wylder's
Greatsword) Eintraege (`art_pool` gegen `arts` im Testabzug). UIA meldet nur die
Eintraege der sichtbaren Reihen (6 Reihen inklusive der angeschnittenen). Jeder
Pool braucht also einen Rollbalken. Das Kriterium "5 Reihen zu 6 ohne Rollbalken"
aus dem Auftrag ist nicht erreichbar; geprueft wurde "6 je Reihe".

## Ergebnis je Pruefpunkt

| Punkt | Ergebnis | Beleg |
|---|---|---|
| Volle Suite | 2171 passed, 9 skipped, 157 s | `T-335qa4/suite.log` |
| (1) QA-316 Kachel 2 aktiv, Tab auf 3 und weiter | **behoben**: 225 %, 125 % und 150 %: alle Kachelrechtecke, Hand-Schalter und Chip bei jedem Tab-Schritt pixelgleich (125 %: 7 von 7 bzw. 8 von 8 Zustaenden; 150 %: 7 von 7 bzw. 8 von 8 Zustaenden). Auch mit Kachel 1 aktiv bleiben die Spalten fest. Bei 225 % rollt die Seite, sobald der Chip den Fokus bekommt (alles 333 px gleichmaessig, Groessen unveraendert) | `sA.out`, `sA125.out`, `sA150.out` |
| (2) QA-319 Tab, dann Klick | **behoben**: Tab auf Kachel 3 gestrichelt, Klick darauf durchgezogen (PostMessage), ebenso Kachel 4 mit echter Maus; Chip: Tab gestrichelt, Klick und Esc durchgezogen; Gegenprobe Tab, Enter, Esc bleibt gestrichelt | `sB.out`, Bilder `b1`..`b7` |
| (3) QA-320 sechs je Reihe | **behoben**: 125 %, 150 % und 225 %: Magic Longsword beim ersten und zweiten Oeffnen, Blood Claymore 3 von 3, Stamp, jeweils 6 je Reihe, keine Luecke rechts | `sC125/150/225.out`, Bilder `c1-longsword-first-150`, `c2-claymore-125` |
| (4) QA-315 mit neuer Popup-Breite (150 %, Popup 518x432) | **haelt**: Rand unten rechts: Popup ueber dem Chip, rechts geklemmt (3323..3841); links an x=0; oben mit Platz: unter dem Chip; Umschlag: Chip-Oberkante 1618 -> Popup unten bis y=2160, 1620 -> ueber dem Chip; Fusszeile sichtbar | `sD.out`, `sE.out`, Bild `d1-bottom-right` |
| stderr | alle drei Starts 0 Byte | `stderr-225.txt`, `stderr-125.txt`, `stderr.txt` |

## Befunde

Keine.

## Beobachtungen

- Bei 150 % mit Faktor 1,5 entstehen Rundungen von einem Pixel: Popup bis x=3841 bei Bildschirmbreite 3840 (Rahmenpixel); ueber dem Chip 1 px Ueberlappung.

## Nicht getestet

- 125 % und 150 % als echte Windows-Einstellung; hier per `QT_SCALE_FACTOR` auf 225 %.
- 100 %; ein Arbeitsbereich mit Taskleistenabzug (hier 0,0..3840,2160).

## Gesamturteil

**PASS**: Kein Befund P1/P2, alle vier Punkte am Fenster belegt. Abweichung vom Auftrag: Punkt (3) ist als "6 je Reihe" geprueft, weil die 30 Arts aus T-335qa3 falsch gezaehlt waren (siehe oben).

## Register-Zeilen (zum Anhaengen durch den Director)

```
| QA-315 | **Retest T-335qa4 (31.10.2026, qa-engineer, Quellstand `35082f7`): behoben** -- mit neuer Popup-Breite (518x432 bei 150 % auf 3840x2160): unten rechts ueber dem Chip und rechts geklemmt, links an x=0, Umschlag an y=2160 exakt, Fusszeile sichtbar | P3 | Minor | developer | ja - Fenster T-335qa4, Bild d1 | behoben -- Fix `ffeecd2`, Retest T-335qa3/qa4 | 2026-10-31 |
| QA-316 | **Retest T-335qa4 (31.10.2026, qa-engineer, Quellstand `35082f7`): behoben** -- Kachel 2 aktiv bzw. Kachel 1 aktiv, Tab durch Kacheln 1..6, Chip und 1H: Kachelrechtecke, Hand-Schalter und Chip pixelgleich bei 125/150/225 %. Fix `653c0cc` | P4 | Minor | developer | ja - Fenster T-335qa4 | behoben -- Fix `d6ae45d`, `653c0cc`, Retest T-335qa4 | 2026-10-31 |
| QA-319 | **Retest T-335qa4 (31.10.2026, qa-engineer, Quellstand `35082f7`): behoben** -- Tab, dann Klick auf dieselbe Kachel (auch echte Maus) bzw. denselben Chip: durchgezogen, auch nach Esc; Tab, Enter, Esc bleibt gestrichelt. Fix `3da468b` | P4 | Trivial | developer | ja - Fenster T-335qa4 | behoben -- Fix `3da468b`, Retest T-335qa4 | 2026-10-31 |
| QA-320 | **Retest T-335qa4 (31.10.2026, qa-engineer, Quellstand `35082f7`): behoben** -- 6 je Reihe bei 125/150/225 %, Magic Longsword beim ersten Oeffnen, Blood Claymore 3/3. Korrektur: Pools haben 52-54 Arts, nicht 30 (UIA zaehlt nur sichtbare Reihen), Rollbalken also immer. Fix `35082f7` | P4 | Trivial | developer | ja - Fenster T-335qa4, Bilder c1/c2 | behoben -- Fix `35082f7`, Retest T-335qa4 | 2026-10-31 |
```
