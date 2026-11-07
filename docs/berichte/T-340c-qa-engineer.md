# T-340c — Nachtest T-339 und T-340 im Fenster (qa-engineer)

Stand `34a4b6e`, Quellstand. Umlenkung `DankYeeterT-340c`, `LOCALAPPDATA`/`APPDATA` auf `<SP>\T-340c`,
Testabzug v20/v5 kopiert (1545 Dateien). Registry `HKCU\Software\DankYeeter` nicht beruehrt.
Volle Suite vorab: 2558 passed, 9 skipped (185 s).

**Urteil: FAIL** — zwei Abnahmepunkte des Auftrags nicht erfuellt ("nichts abgeschnitten, auch bei
kleinster Fensterbreite"; "nichts neu abgeschnitten"). Beide Befunde P3/P4, der erste besteht schon
seit `3463d96`. Der `director` entscheidet ueber Fix oder WAIVED.

## Befunde

### [P3 | Minor | Mittel] Gefaessliste bei kleinster Fensterbreite: Zeilen abgeschnitten, auch unter Balanced

**Adressat:** developer (Abnahmepunkt: director)
**Betroffen:** `nrplanner/app.py` Gefaessliste, `advisorbar.VesselRowDelegate.paint`
**Reproduktion:** Raider, Raider's Goblet, Stufe 15, Deep an, Balanced, Optimize; Fenster auf
`minimumSizeHint` (1192 logisch bei 125 %, 1190 bei 100/150 %).
**Erwartet:** jede Zeile ganz lesbar (`AR +x % / Defense +y %`).
**Tatsaechlich:** Textbereich ab x=192, 141 px breit, Viewport 284 px: alle 7 sichtbaren Zeilen ragen
rechts hinaus, waagrechte Bildlaufleiste (Maximum 52). Bild: "AR +10 % / Defens", "BEST AR +22 % / D".
Die `BEST`-Zeile braucht 161 px und wird nicht gekuerzt, sondern abgeschnitten. Bei 100 % reicht auch
die Bereichsbreite nicht: "AR +61 % / Defense +102 %" 142 px gegen 139.
**Rot-vorher:** `9cd99ca` (vor T-340) gleich; `3463d96` (vor T-339) unter `Maximise damage` 4 von 7
Zeilen abgeschnitten. Die Gefaessliste passt bei kleinster Breite schon vorher nicht; Balanced macht
nur die Zeilen laenger.
**Auswirkung:** gering, die Zahlen sind per Bildlauf oder breiterem Fenster lesbar.
**Vorschlag:** Mindestbreite der Gefaessliste aus dem Platzbedarf von Name und Zeile ableiten, oder die
Zeile umbrechen.

### [P4 | Minor | Mittel] Effects: "What it does" verliert Breite, Beschreibungen neu gekuerzt

**Adressat:** developer
**Betroffen:** `nrplanner/effectstab.py`, Spalte `Colours` (4) und `What it does` (10)
**Reproduktion:** Reiter Effects & chances, Fenster in Standardgroesse, Quellstand gegen `9cd99ca`.
**Tatsaechlich (125 %):** `Colours` 133 auf 195 px (+62; UI_SPEC T-340 erlaubt 56), `What it does`
477 auf 458 px. Neu gekuerzt (Ellipse, Tooltip traegt den Volltext): 3 Beschreibungen bei 100 %, je 1
bei 125 und 150 % ("Boosts damage negation when HP is at max ..."); vorher 21/23/23.
**Vorschlag:** die 56 px einhalten oder die Breite einer anderen Spalte entnehmen.

## Explorationsprotokoll (gehalten)

- Fall T-337: Gefaessliste Raider's Goblet `AR 292 (+85 %)` bei Stacks 2 (vorher 299). Optimize bei
  Stacks leer/1/2/4: in keinem Vorschlag ein zweiter Traeger von 7060200 (je Wahl die Effekte des Exemplars
  geprueft). Stacks 4: `AR 334`, Why `+31.1%`.
- Zweiter Traeger von Hand (Grand Luminous Scene): AR n=2 bleibt 212,083; Warnung
  `... x2 — only one will apply` auf der Statistik-Seite mit `⚠`; `⚠` an beiden Slot-Karten; Effects-Spalte
  `Strongest only (multiplies)`.
- Stacks-Feld: 7060200 `5` `7` `10` rot und leer, `4` `0` gelten; 7060000 bis 7; 6060300 und 6500500 bis
  10, `11` rot. ×-Zahl: `100000` wird ×4, `5` ×4, `-2` ×1, `abc` ×1, Tooltip "at most 4".
- Balanced bei Standardbreite und 100/125/150 %: Zeilen `AR +x % / Defense +y %`, negativ mit Vorzeichen
  (Recluse `Spell -5 %`); Staff-Nightfarer `Spell +0 % / Defense +214 %`. `BEST` folgt mit Favoriten der
  Zahl ausgelassener Favoriten, sonst dem Produkt. Picker: Sortierung Balanced, Wertzeile auf allen Karten,
  ein `BEST FOR BALANCE`, nichts abgeschnitten.
- Optimize unter Balanced, erste Frage, sechs freie Slots: Antwort 1,78 s (Recluse), 2,43 (Raider),
  2,20 (Wylder), 2,01 (Duchess), A6 6 s; ganze Gefaessliste 19,7 bis 23,3 s (Maximise damage 19,9 s).
- Slot-Bilder: Kontaktbogen `slot_chip` 5 Farben x normal/Deep x leer/belegt: Licht je Farbe und Art,
  Edelstein nur belegt, Weiss ohne. Leiste, Gefaessliste, Kartenkopf, Picker normal und Deep im Bild.
- Symbole je Reiter (Labels mit Bild / Zellen mit Symbol, 125 %): Build planner 33/11, Effects 0/1200,
  Weapons 237/0, Nightlords 10/0, Deep of Night 0/15, Red variants 0/0 (laut ARCHITECTURE ohne Beleg),
  World Events 1/0, Picker 155. Rohes `<img` in Label, Knopf, Combo, Zelle, Kopf: 0 in allen Fenstern und
  Massstaeben; UIA-Namen im Quelllauf (`drive_window.ps1`): 239, keiner mit `<img` oder `&nbsp;`.
- Abgeschnittene Labels gegen `9cd99ca` bei 100/125/150 %: in allen Reitern und im Picker keine neuen.

## Nicht getestet

Balanced ueber das echte Combo im UIA-Lauf (UIA-Auswahl griff nicht; im Prozess ueber `choose_goal`
gefahren); Why-Satz am zweiten Traeger; Artefakt.

Skripte und Bilder: `<SP>\T-340c\` (`c1.py` bis `c5.py`, `shots\`).
