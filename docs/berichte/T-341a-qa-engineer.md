# T-341a — Nachtest QA-341 und QA-342 (qa-engineer)

Quellstand `bc210e3`. Umlenkung `DankYeeterT-341a`, `LOCALAPPDATA`/`APPDATA` auf `<SP>\T-341a`, Cache
v20/v5 aus T-340d kopiert (1545 Dateien). Registry `HKCU\Software\DankYeeter` nicht beruehrt. Volle
Suite: 2560 passed, 9 skipped (113 s). Zaehlungen aus Laeufen ohne Bildaufnahme.

**Urteil: FAIL** — QA-341 behoben, QA-342 (Beschreibungen) behoben, aber das Kriterium "nichts neu
gekuerzt gegen `9cd99ca`" ist an zwei Stellen verletzt (QA-343, QA-344, beide P4). Der `director`
entscheidet ueber Fix oder WAIVED.

## Nachtest

**QA-341 — behoben.** Raider, Raider's Goblet, Stufe 15, Deep an; 100/125/150 % je `Balanced` und
`Maximise damage`. Kleinste Breite 1190/1192/1192: keine waagrechte Bildlaufleiste (vorher `34a4b6e`:
sichtbar, Maximum 52), 0 Zeilen ueber den Viewport gemalt (vorher 7 bzw. 4), Groessenwunsch der Zeilen
0 (vorher 259 bis 336). Gekuerzt mit `…`: 7 von 7 Zeilen (Balanced), 4 von 7 (Maximise damage). Tooltip
jeder Zeile mit gekuerzter zweiter Zeile: Name, ganze Zeile, Rest (16 von 16). Standardbreite gleich
vor/nach: Fenster 1979, Viewport 414, nichts gekuerzt. UIA-Lauf mit `drive_window.ps1` und echtem
Fenster bei Mindestbreite: keine waagrechte Leiste, Bild zeigt Ellipsen. Regressionstest gegen den
alten `advisorbar.py` im Klon rot.

**QA-342 — behoben (Beschreibungen).** `What it does` 510 px (vorher 458, `9cd99ca` 477), gekuerzte
Beschreibungen gegen `9cd99ca`: 0 neu, 20 weniger (100/125/150 %, Standardbreite); bei Mindestbreite
gleich (205/206/206). Drei Masken: Laufweite+8, Textrechteck des Stils, Zelle gerendert bei Spaltenbreite
gegen 4000 px (125 %). Regressionstest gegen den alten `effectstab.py` im Klon rot.

**QA-340 doppelt:** nicht nachvollzogen. `git grep QA-340 bc210e3` findet genau eine Zeile
(`qa/findings.md:828`).

## Befunde

### [P4 | Minor | Mittel] QA-343 — Effects: zwei Effektnamen bei Standardbreite neu gekuerzt (durch den QA-342-Fix)

**Adressat:** developer (Kriterium: director)
**Betroffen:** `nrplanner/effectstab.py:663`, Spalte `Effect`
**Reproduktion:** Reiter Effects & chances, Standardbreite, 100/125/150 %.
**Erwartet:** nichts neu gekuerzt gegen `9cd99ca`.
**Tatsaechlich:** `Effect` 586 auf 511 px; gekuerzt "[Duchess] Reprise events upon nearby enemies by
landing the final blow of a chain attack with dagger" und "[Wylder] Standard attacks enhanced with fiery
follow-ups when using Character Skill (greatsword only)". `9cd99ca` und `34a4b6e`: 0. Alle drei Masken
einig. Der Tooltip traegt den Namen.
**Vorschlag:** `Effect` nur bis zur Breite seines laengsten Namens abgeben lassen, oder das Kriterium
fuer Namen lockern (director).

### [P4 | Minor | Niedrig] QA-344 — Effects: `Colours` bei kleinster Fensterbreite 3 Zellen neu gekuerzt (seit T-340)

**Adressat:** developer (Kriterium: director)
**Betroffen:** Spalte `Colours` (4), Edelsteinreihe vor dem Text
**Reproduktion:** Reiter Effects & chances, Fenster auf `minimumSizeHint` (1190/1192).
**Tatsaechlich:** `Colours` 67 px wie vorher, aber die Edelsteine nehmen Platz: neu gekuerzt bei
"Improved Critical Hits +1", "Improved Melee Attack Power", "Improved Skill Attack Power" (100 %
zusaetzlich "Continuous HP Recovery"). `34a4b6e` gleich, also nicht vom Fix. Tooltip traegt den Text.
**Vorschlag:** Untergrenze von `Colours` um die Edelsteinbreite heben, oder hinnehmen (director).

## Beobachtung

Unter Balanced zeigt die Gefaessliste bei kleinster Breite in keiner Zeile die Defense-Zahl
("AR +61 % / Def…"); sie steht nur im Tooltip, wie das Kriterium es zulaesst.

## Nicht getestet

Maske C (gerendert) nur bei 125 %; 100/150 % mit Masken A und B. Balanced nur im Prozess
(`choose_goal`), nicht ueber das UIA-Combo. Artefakt (T-341c). Skripte: `<SP>\T-341a\` (`q341.py`,
`q342.py`, `q342c.py`, `d1.ps1`).
