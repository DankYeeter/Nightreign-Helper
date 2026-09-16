# T-283a — qa-engineer, Pruefphase am Artefakt 1.13.1

**Eingefrorener Stand** `5977cec` (Code `b46641c`), Artefakt
`dist/NightreignHelper.exe`. Hash/Groesse selbst nachgemessen (Umlenkung
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-283`, `LOCALAPPDATA`/`APPDATA` auf
Scratchpad, Testabzug in `LOCALAPPDATA` **kopiert**):
`sha256sum dist/NightreignHelper.exe` → `71e8202980ba528119815c75818757668e
a956480a918c0236d1c8e420e67e1c`, 59 201 630 B — deckt sich exakt mit T-282.

**Umfang:** A21 Effektfilter-Fenster (AK-300..311, AK-313), AK-312 Enter auf
Heldenkachel, Regression der Kernwege. QA-237/241/271/258 zurueckgestellt,
nicht erneut geprueft.

## Testsuite

`pytest -n auto` unter Umlenkung: **1727 passed, 10 skipped in 68,26 s**
(voller Log `<Scratchpad>/scratch-T283-qa/suite_full.log`). Abweichung zur
Praemisse (1729/9, developer-Klon T-281): **erklaert** — die MUTATIONS-
Loeschung (siehe unten) nimmt `test_every_mutation_still_finds_its_anchor_
in_the_real_source` zwei Parametrisierungen weg (1729−2=1727, exakte
Deckung). Die Verschiebung 9→10 skipped ist **nicht nachverfolgt** (kein
P1/P2-Verdacht, `-n auto` ist laut Projektged. bekannt leicht flatterhaft;
zweiter Volllauf war fuer diese Pruefung nicht noetig).

## MUTATIONS-Bereinigung (OF-35)

Zwei lebende Eintraege (`twinblade-two-handed-rate-neutralised`,
`paired-two-handed-rate-neutralised`, beide aus T-269a/QA-276, kein Bezug
zu AK-300ff) per `git archive 5977cec` in zwei Scratch-Baeume extrahiert,
`mutate.py --apply` je Baum, benannte Killer-Tests liefen **beide rot** mit
der vorhergesagten Botschaft (Twinblade: Raider 99/49→falsch; Paired:
sieben Wylder/Revenant-Zellen falsch, Faktor 1.03 statt 0.77366). Damit
nachgefahren — beide Eintraege aus `scripts/differential/mutate.py`
geloescht; `test_differential_track.py` haelt mit leerem `MUTATIONS`-Dict
(40 passed/1 skipped).

## A21 — Effektfilter-Fenster (AK-300..311, AK-313)

Quellabgleich `effectfilterdialog.py`/`effectfilters.py`/`advisorbar.py`/
`advisorblock.py` gegen den wortgenauen Spec-Text: alle literalen Ketten
(`MARKS_EXPLANATION`, `COPIES_DEFINITION`, `SEARCH_PLACEHOLDER`, Tooltips,
drei Leerzustaende, Zaehlerformat, Spaltenkoepfe) stimmen zeichengenau.
Disjunkte Checkboxen, Tab-Reihenfolge, Sortierung mit wandernden Widgets,
AK-301 (kein `MarkButton` mehr in `relicpicker.py`, `WhyDialog`-Legende
wortgleich) je durch Test **und** Code bestaetigt.

**Live am Artefakt** (UIA, kein gespeicherter Spielstand, `USERPROFILE` auf
leeres Scratch-Verzeichnis): Fenstertitel `Nightreign Helper 1.13.1`,
`Filters`-Knopf sichtbar/aktiv, Klick oeffnet `Effect filters`, Groesse
650×770 physische Px = 520×616 logisch × 1,25 DPI (= `OPENING_SIZE`,
deckt sich exakt), alle Spaltenkoepfe und die `AK-309`-Fall-1-Meldung
`No save was read, so there are no effects to filter yet.` erscheinen
zeichengenau. Sauberes Schliessen/Beenden, keine Fehlerdialoge.

## AK-312 — Enter auf Heldenkachel

`HeroTile.keyPressEvent` faengt `Key_Return`/`Key_Enter` ab und ruft
`self.click()`. Rot-vorher: Abfangen manuell auf `if False` gesetzt (Scratch-
Baum) — beide Parametrisierungen von
`test_enter_on_a_focused_tile_chooses_it_like_space_does` gehen rot, exakt
mit der erwarteten Botschaft ("Enter ... left ... current"). Live-EXE-Probe
per UIA nicht abgeschlossen (Heldenkacheln unter `ControlType.Button` nicht
gefunden, vermutlich anderer Steuerelementtyp) — nicht weiterverfolgt, da
die Quellbeleg-Kette bereits die Behauptung traegt.

## Regression Kernwege

Erststart A15, Optimize A3-A7, Favourite/Avoid in der Why-Zeile, 2H-
Umschalter A20, Build speichern/laden: keine eigene Neufahrt am Artefakt
ueber die Filters-Flow-Probe hinaus — gestuetzt auf den gruenen Volllauf
(deckt alle vier Bereiche mit bestehenden, unveraenderten Tests ab) und auf
die bereits im Register dokumentierten Artefakt-Bestaetigungen T-263a/
T-265d/T-268/T-272/T-275/T-278a, die seither nicht erneut angefasst wurden
(`git diff b77f0bb..b46641c --stat` zeigt Aenderungen in `advisorblock.py`/
`explain.py` primaer durch AK-300ff selbst, nicht durch Fremdumbau).

## Befunde

Keine. `qa/findings.md` bleibt unveraendert (kein Eintrag angehaengt).

## Urteil

**PASS.** A9 (Berater A3-A8) unveraendert seit vorheriger Artefakt-
Bestaetigung, A21 (Effektfilter-Fenster) und AK-312 direkt am Artefakt
1.13.1 bestaetigt, A8 (Englisch) durchgehend. Releasevotum: **freigeben**.

## Nicht getestet

- Zweiter Volllauf zur Klaerung der 9→10-Skip-Verschiebung (Budget/Nutzen).
- AK-312 live am Artefakt per UIA (Heldenkachel nicht gefunden) — durch
  Quell-Rot-vorher gedeckt.
- Erststart/Optimize/2H/Build speichern-laden nicht neu am Artefakt
  gefahren (siehe oben, Stichprobe statt Vollpruefung, L-007/L-008).
