# T-335e -- Pruefung am Quellstand (qa-engineer, 28.10.2026)

Stand `b33a71e`, Diff `ed93e31..b33a71e`. Fensterlauf `python run.py` aus dem
Quellbaum, Treiber `scripts/drive_window.ps1` (PID-Kopie im Scratchpad, QA-303),
Umlenkung Org `DankYeeterT-335e`, `LOCALAPPDATA`/`APPDATA` im Scratchpad,
Testabzug kopiert (841 Dateien, 21 139 391 Bytes). Echter Spielstand nur
lesend (321 Relikte).

**Urteil: FAIL** -- wegen QA-305 (P2, Absturz, besteht schon in `ed93e31`,
also auch in Exe 1.19.0; kein Rueckschritt aus T-335). Die fuenf Pruefpunkte
von T-335e selbst halten bis auf die Textbefunde QA-306/QA-307 (P3).
Mindestens zu beheben: QA-305, oder der `director` wandelt mit Eigentuemer,
Geltungsbereich und Ablaufdatum in WAIVED.

## Befunde

### QA-305 [P2 | Major | Mittel] Armament-Dialog: waffenloser Eintrag gewaehlt, danach stuerzt das Programm ab

**Adressat:** developer
**Betroffen:** `nrplanner/weaponslots.py` `WeaponDialog._rebuild_effects`
(Zweig `if not pool`), `nrplanner/app.py:1462` `_edit_weapon_slot`
**Umgebung:** jede Nightfarer-Wahl; Quellstand `b33a71e` und `ed93e31`

**Reproduktion (Fenster, zweimal):**
1. Revenant waehlen, leere Kachel 2 doppelklicken (Dialog steht auf
   "Academy Glintstone Staff").
2. Suche "Finger Seal", Eintrag "Finger Seal · 34750000" anklicken.
3. OK (per UIA und per Mausklick) -- oder Cancel.

**Erwartet:** Dialog schliesst, Kachel traegt das Siegel (bzw. bleibt leer).
**Tatsaechlich:** Prozess endet ohne Meldung; stderr "Fatal Python error:
Aborted" / "Windows fatal exception: access violation" in `app.exec`, kein
Python-Traceback.

**Analyse:** Ohne UIA nachgestellt (`off3.py`, offscreen und `windows`):
stuerzt ab fuer Unarmed, Wylder's Small Shield und Finger Seal 34750000 --
drei der sieben angebotenen Waffen ohne rollbare Effekte (ungeprueft:
Guardian's Greatshield, drei Scholar's Thrusting Sword) --, auch als Wylder
und auch bei Cancel.
Haelt: Waffe mit Effekten (Finger Seal 34000000, Academy Staff, Caestus);
Dialog oeffnet schon auf Unarmed; Dialog ohne Planner-Eltern; Planner ohne
anschliessendes `recompute`. Hypothese: die per `deleteLater` im modalen
Dialog-Loop entfernten Effekt-Kaestchen (Wechsel von einer Waffe mit Pool
auf eine ohne) werden erst nach `recompute` geloescht und dann noch
angefasst. Ungeprueft.

**Auswirkung:** Wer seine Linkshand-Waffe (Wylders Schild, Guardians
Grossschild, Revenants Siegel) auf eine Kachel legt, verliert das Fenster.

**Vorschlag:** Absturz mit dem Skript als Test festhalten (offscreen genuegt),
dann den Abbau der Kaestchen in `_rebuild_effects` pruefen.

---

### QA-306 [P3 | Minor | Mittel] Berater-Texte binden den Zauber weiter an die Startausruestung

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/goals.py:138-140` (`_ATTACK_RATING_SCOPE`,
festgehalten von `tests/test_advisor_goals.py:252`), `nrplanner/advisor/run.py:319`
(`no_carrier_sentence`, auch die neue gelbe Warnzeile)

**Reproduktion:**
1. Raider, Academy Glintstone Staff auf Kachel 2, Kachel 2 gewaehlt.
2. Hit with Sorceries, Damage type All, Optimize, Why.
3. Damage type Fire, Optimize.

**Erwartet:** Vorgabe T-335a "Why-Text passend halten"; seit `b3db0f8`
rechnet der Berater den Zauber des Stabs auf der gewaehlten Kachel.
**Tatsaechlich:** Why sagt woertlich "What a spell hits for is rated ... on
the equipment the Nightfarer starts an expedition with — never on a spell
picked up in a run." Bei Fire nennt die Warnzeile "your starting equipment
does not carry it", obwohl der gefragte Stab kein Startgegenstand ist
(offscreen `off6.py`, alle vier Stufen).

**Auswirkung:** Zwei Aussagen widersprechen dem, was die Zahl tatsaechlich
misst (A7-Muster: falscher Vorbehalt).

**Vorschlag:** Beide Saetze auf "Stab oder Siegel der gewaehlten Kachel,
sonst der Start-Katalysator" umstellen, Waechtertest mitziehen.

---

### QA-307 [P3 | Minor | Mittel] Anleitung: Berater-Zahl soll der Kachelstufe folgen, tut sie nicht

**Adressat:** developer (Spec-Frage an director, siehe unten)
**Betroffen:** `docs/anleitung/guide.md:128-129`; `nrplanner/advisor/goals.py:457`

**Reproduktion:** Raider, Academy Glintstone Staff auf Kachel 2 gewaehlt,
Sorceries/All; Stufe Common, Uncommon, Rare, Legendary.

**Erwartet (Anleitung):** "The figure is worked out at the upgrade level that
tile shows."
**Tatsaechlich:** Berater 331 auf allen vier Stufen (`weapons.MIN_UPGRADE`);
nur die Tafel folgt (144/166/186/208).

**Analyse:** T-335b legt die Stufe nur fuer die Tafelzeile fest; der Berater
bleibt bewusst auf `MIN_UPGRADE` (Kommentar `goals.py:454`). Die Anleitung
stellt den Berater falsch dar -- oder die Absicht war eine andere.

**Vorschlag:** Satz in `guide.md` dem Code anpassen, sofern der director
`MIN_UPGRADE` fuer den Berater bestaetigt.

## Pruefpunkte T-335e

| # | Pruefung | Ergebnis |
|---|---|---|
| 1 | Wylder, Greatsword gewaehlt, Weapon/Magic/Maximise damage | Fenster: kein "3+"-Relikt gezaehlt (Why aller 6 Plaetze). Offscreen echter Spielstand: Annahme nur Typ 5; `ed93e31` zaehlte "3+ Hammers" (Score 39,34 -> 32,79) -- rot-vorher. Dolch-Kachel: "3+ Daggers" zaehlt (Gegenprobe). Kachelwechsel leert die Antwort; drei Cache-Schluessel verschieden (alt: einer) |
| 2 | Recluse, Sorceries, Fire | gelbe Zeile mit ⚠, voller Satz, unter der Leiste, ueber "Open a slot ..."; bei 1487 / 1682 / 2032 px zwei Zeilen, nichts ueberdeckt; Magic: keine Zeile, Leiste 45 statt 65 px hoch. Save ueber Build-Feld = QA-304 (bekannt) |
| 3 | Spell damage je Kachel | Raider und Duchess: `Spell damage (Glintstone Pebble)` folgt der Stufe (Raider 144/186/208). Wylder Greatsword: keine Zeile. Revenant Claws: `Weapon art` + `Spell damage (Rejection) 0`; Caestus auf Kachel 3: keine der beiden Zeilen |
| 4 | Hit with Sorceries vor/nach Kachelwechsel | Raider Staff-Kachel: rangiert; Axt-Kachel: `_NO_CATALYST` woertlich im Why und Warnzeile. Recluse Incantations: `_WRONG_GENUS` woertlich. Tooltip `HIT_WITH_TOOLTIP` woertlich (Hover) |
| 5 | Regression | Suite 2079 passed, 9 skipped (88,6 s). Why mehrfach gelesen; Apply all nicht gedrueckt (siehe unten) |

## Explorationsprotokoll

Haelt: Datenzuordnung `wepTypeTrigger` <-> `wep_type` fuer alle 29 Typen
geprueft (Namen passen; Basiswert 1 = Dolch); Kachelklick verwirft die
Antwort (`the_build_changed`). Nicht beobachtet: Verschwinden der Warnzeile
bei einer Leisteneingabe ohne neuen Lauf (nur Code gelesen, `_show`).

## Offene Fragen

- director: Soll der Berater den Kachel-Katalysator auf Kachelstufe rechnen
  (wie die Tafel) oder auf `MIN_UPGRADE` (wie die Startwaffe)? Beide
  Lesarten sind mit T-335b vereinbar; davon haengt QA-307 ab.

## Nicht getestet

- Apply all am Fenster (Zugbudget); Why nur gelesen.
- Exe 1.19.0 selbst (QA-305 am Quellstand `ed93e31` belegt).
- Tauschrelikt am Start-Katalysator auf Kachel (keins im Spielstand gesucht).

## Beobachtungen

- `damage.py:941` (Entwicklermeldung) nennt weiter nur den Start-Katalysator.
