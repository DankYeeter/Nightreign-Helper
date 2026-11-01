# T-335qa — qa-engineer am Quellstand (Fensterlauf), 31.10.2026

Stand `a200160` (Code = `82b0f07`, Diff `ed93e31..82b0f07`). Fenster `run.py`
aus dem Quellstand, Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT335qa`,
`LOCALAPPDATA`/`APPDATA`/`USERPROFILE` in den Scratchpad `T-335qa/`,
Testabzug v18 (1027 Dateien, `meta.extract_version` 18) kopiert, Spielstand
eingefroren (Kopie, sha256 gleich dem Original `5fb89851...`, mtime Original
15:39:53, 315 Relikte gelesen).

**Abbruch:** Nach Schritt s17 sperrte `~/.claude/pc_guard.ps1` jeden weiteren
Bash-Aufruf ("Spiel laeuft: EpicGamesLauncher" bzw.
"EOSOverlayRenderer-Win64-Shipping", "Warte auf sein 'frei'"). Der Rest blieb
ungeprueft (Liste unten). **Das Fenster dieses Laufs laeuft noch**
(python `run.py`, Launcher-PID 1636, Fenster-PID 26444) und haelt die
maschinenweite Instanzsperre — nach "frei" schliessen.

## Risiko-Briefing

Am riskantesten: (1) die Casting-Leiste als neues Bedienelement mit Popup
(`Qt.Popup`), Fokus und Tab-Kette — von Tests nie gezeigt, nur gebaut;
(2) eine Zahlquelle Tafel/Chip/Berater (AK-415) nach vier Formelaenderungen an
einem Tag; (3) Cache und Antwort-Verfall beim Kachel- und Wahlwechsel;
(4) Texte (Why, Warnzeile, Anleitung), die den alten Bezug "Startwaffe"
beschreiben — dieselbe Klasse wie QA-306. Reihenfolge: Suite, Zahlen am
Fenster, Popup/Tastatur, Berater, Texte, dann AK-405..408/QA-302/QA-030.

## Ergebnis je Pruefpunkt

| Punkt | Ergebnis | Beleg |
|---|---|---|
| Volle Suite | 2159 passed, 9 skipped, 155 s | `pytest -n auto`, `T-335qa/suite1.log` |
| Recluse Lv15 Pebble 123 / Arc 120 | haelt; Chip = Zeile | Fenster s2/s4 |
| Wylder Lv15 Stamp 262, 1H und 2H | haelt (beide 262); Berater-Basis 262,41 in beiden Stellungen, Bestwert 443 gleich | Fenster s7, offscreen off2 |
| Magic Longsword + Glintblade 34 | haelt | Fenster s10 |
| Chips, Popup R2/Art | R1/R2 genau Pebble/Arc; R2-Popup 64 Eintraege, Art-Popup Wylder 54; 6 je Reihe, 5 Reihen, Rollbalken; Standard zuerst; kein Punkt (QA-313) | Fenster s3/s4/s7, Bilder 02/03 |
| Vorbelegung, "Choose a weapon art" | haelt; gestrichelter Chip, keine Art-Zeile | Fenster s9/s10, Bild 04 |
| Tastatur (AK-413) | Enter/Leertaste oeffnet, Pfeile bewegen Fusszeile, Enter waehlt (Adula's Moonblade 130 = Zeile), Esc schliesst, Fokus zurueck auf Chip, R2 -> Hand-Schalter; Kacheln keine Tab-Stopps (QA-312) | Fenster s5/s6, Tab-Ring offscreen HEAD/`ed93e31` |
| Merken je Nightfarer (AK-414) | haelt: Wylder Kachel 2 Glintblade nach Recluse und zurueck (Fenster); Recluse R2 nach Wylder und zurueck, Leeren setzt zurueck (offscreen) | s16, off1 |
| Berater Weapon art vor/nach Kachelwechsel | Antwort verfaellt ("Nothing suggested yet."), neue Zahl je Kachel (Stamp 443 / Glintblade 56) | Fenster s12/s13, off2 |
| Berater Sorceries R1/R2 | Why nennt Glintstone Pebble bzw. Arc; Wahl verwirft die Antwort | Fenster s14 |
| Warnzeile Fire | erscheint unter der Leiste, ueber "Open a slot ..." | Fenster s15 |
| Regression Optimize/Why/Apply all | haelt (Apply all -> "Applied. Undo ..."; Tafel Arc 148) | Fenster s14 |
| Neue Hex-Literale (AK-418) | keine (`git diff ed93e31..82b0f07 -- nrplanner/`, Maske `#[0-9a-fA-F]{6}` 0; `castingbar.py` Maske `#hex|QColor(zahl|rgb(` 0) | git, Grep |
| Spieltext als Text (AK-419) | Chip-Name/Fusszeile PlainText, Tooltips `html.escape`, Art-Zeile escaped | Code gelesen |

## Befunde

### [P3 | Minor | Mittel] QA-310 Why und Warnzeile beschreiben unter Weapon art die Startwaffe statt der markierten Kachel

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/goals.py:147`, `:234-238`; `nrplanner/advisor/run.py:326-330`
**Umgebung:** Wylder, Lv15, Kachel 2 Magic Longsword mit Glintblade Phalanx, markiert

**Reproduktion:**
1. Kachel 2 Magic Longsword, Art Glintblade Phalanx waehlen, Kachel 2 markieren.
2. Hit with *Weapon art*, Damage type *All*, Optimize, Why.
3. Damage type *Fire*, Optimize.

**Erwartet:** Why und Warnzeile nennen den Bezug, auf dem gerechnet wird: die Art der markierten Kachel, deren Stufe, einhaendig (T-335z, `goals._art_cell`).
**Tatsaechlich:** Why: "Scaled on the Nightfarer's own starting armament at its lowest tier ...; one- or two-handed as the stat sheet's hand switch says" und "It scales the armament's attack rating" (Glintblade ist Flach-Klasse, ohne AR). Warnzeile: "... for a spell the staff or seal on the selected tile, or else the starting one; otherwise the starting armament ...".
**Analyse:** Die Saetze stammen aus der Zeit, als Weapon art auf der Startwaffe rankte; T-335z hat die Rechnung umgestellt, die Texte nicht.
**Auswirkung:** Falsche Erklaerung genau dort, wo der Spieler nachliest, worauf gerechnet wurde.
**Vorschlag:** Saetze je Hit-with-Zweig aus derselben Regel bilden (wie QA-306 fuer Zauber); projektweite Suche nach "starting armament" in `nrplanner/advisor/`.

### [P3 | Minor | Mittel] QA-311 Anleitung: Weapon-art-Zeile nach altem Stand, Casting-Leiste fehlt

**Adressat:** director (technical-writer-Ausloeser)
**Betroffen:** `docs/anleitung/guide.md:323-344`
**Reproduktion:** Anleitung gegen das Fenster lesen (Wylder Kachel 1 und Kachel 2 wie oben).
**Erwartet:** Zeile erscheint auf jeder gefuellten Nicht-Katalysator-Kachel mit Art (AK-416a), Grundwert = derselbe Treffer ohne Ausruestung; Zauber und Art waehlbar ueber die Casting-Leiste.
**Tatsaechlich:** "appears only on the tile that carries your Nightfarer's own starting armament", "its own base figure is that Total", "The spell shown is the one that catalyst casts"; am Fenster `Weapon art (Glintblade Phalanx) 34` auf Kachel 2, `Weapon art (Stamp (Upward Cut)) 262 no change 262` bei Total 122. Suche `(?i)casting` in `guide.md`: 0 Treffer.
**Vorschlag:** technical-writer laut CLAUDE.md-Tabelle (neues Bedienelement).

### [P4 | Minor | Niedrig] QA-312 Kacheln sind keine Tab-Stopps (AK-413)

**Adressat:** developer
**Betroffen:** `nrplanner/weaponslots.py:163-211` (`WeaponTile`)
**Reproduktion:** UIA `SetFocus` auf eine `WeaponTile` -> "Target element cannot receive focus"; Tab-Ring offscreen: vor R1 steht der StatSheet-Bereich.
**Erwartet (AK-413):** Kacheln -> R1 -> R2 -> Hand-Schalter.
**Tatsaechlich:** R1 -> R2 -> Hand-Schalter haelt; Kacheln fehlen im Ring, per Tastatur ist keine andere Kachel waehlbar.
**Analyse:** Kein Rueckschritt, an `ed93e31` gleich (48 Tab-Stopps, HEAD 50 = plus zwei Chips). Die AK setzt eine Tastaturbedienung der Kacheln voraus, die es nie gab.
**Vorschlag:** Fokus-Policy und Enter/Leertaste (markieren) auf `WeaponTile`, oder AK-413 an den Bestand anpassen (Entscheid ui-ux/director).

### [P4 | Trivial | Hoch] QA-313 Pool-Popup ohne Standardpunkt (AK-411)

**Adressat:** developer
**Betroffen:** `nrplanner/castingbar.py:307`
**Reproduktion:** Wylder, ART-Chip anklicken (Bild `03-wylder-art-popup.png`).
**Erwartet:** Standardart als erster Eintrag **mit** ACCENT-Punkt.
**Tatsaechlich:** erster Eintrag ja, kein Punkt; nur die Fusszeile sagt "this weapon's own art".

### [P4 | Minor | Mittel] QA-314 "Choose a weapon art" und "this weapon's own art" zugleich

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/castingbar.py:335`
**Reproduktion:** Wylder, Kachel 2 Magic Longsword ohne Wahl markieren, ART-Chip anklicken.
**Erwartet:** eine Aussage: entweder gilt die Art als unbekannt (gerollt, AD-056.4) oder als Eigenart der Waffe.
**Tatsaechlich:** Chip "Choose a weapon art", Popup-Fusszeile "Square Off · FP 0 · this weapon's own art".

## Beobachtungen

- Ein pytest-Prozess (PID 27048, `-m pytest tests/test_save_path_memory.py -q -k this_pc`, gestartet 12:20:56) laeuft seit dem echten Dateidialog der T-335p-Gegenprobe; nicht von mir, nicht beendet.
- AK-419 verlangt die neuen Senken im Waechter `tests/test_game_text_is_never_markup.py`; die Pruefung steht in `tests/test_casting_bar.py` (Chip-Name, Tooltip), Popup-Fusszeile und Art-Zeile ohne Test. Code escaped korrekt; security-reviewer prueft parallel.

## Offene Fragen

- **director:** Recluse, Arc auf Kachel 1 gewaehlt, Kachel 2 (Greatsword) markiert, Hit with Sorceries: der Berater rankt den Start-Stab mit **Pebble** (163), nicht mit der auf seiner Kachel gewaehlten Arc; die Tafel zeigt fuer Kachel 2 keine Zauberzeile (offscreen off2). Soll der Rueckfall "sonst Start-Katalysator" die Wahl der Kachel uebernehmen, auf der dieser Katalysator liegt?

## Nicht getestet (Abbruch durch PC-Waechter)

Mindestbreite und `grab()` bei 100/125/150 % (AK-418); RELIC-Chip am Fenster
(AK-417); Pool mit einem Eintrag; Neustart -> Standard (AK-414); AK-405..408
am Fenster; Buendelung Fluch 6850900 am Fenster; QA-302 Ordnerdialog "This
PC"; QA-030 leer speichern; NH-003-Waechter nach dem Registeranhang. Alle
haben gruene Tests in der Suite (2159/9), am Fenster ungeprueft.

## Gesamturteil

**FAIL (formal)**: kein Befund P1/P2, aber die Abnahme ist wegen des Abbruchs
nicht vollstaendig belegt. Mindestens noetig: die Punkte unter "Nicht
getestet" nach "frei" am Fenster. Mit gruenem Rest waere das Urteil CONCERNS
(QA-310, QA-311 P3; QA-312..314 P4).
