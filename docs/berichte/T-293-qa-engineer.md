```
STATUS: erledigt
AUFTRAG: T-293b - Pruefphase 1.14.0 am Artefakt (A22 AK-315, A23 AK-316/317,
AK-314 Nachholung aus T-290b), Umlenkung DankYeeterT-293b.
GELESEN: docs/tasks/T-293.md; docs/berichte/T-293-release-manager-build.md;
docs/berichte/T-290-qa-engineer.md (Lehren Alt-Trick, Filterfenster als
Top-Level); UI_SPEC.md AK-314/AK-315/AK-316; tests/test_advisor_goals.py
und tests/test_advisor_explain.py (Literale 72/70, Wortlaut); nrplanner/
advisorbar.py (_on_ready, _slots_with_nothing); nrplanner/advisor/explain.py
(_rating_word, AK-315-Zeile); qa/findings.md (Kopf, letzte Zeilen).
GEÄNDERT: docs/berichte/T-293-qa-engineer.md (neu); qa/findings.md (zwei
Zeilen angehaengt, QA-284, QA-285). Kein Commit, kein Anwendungscode.
ANNAHMEN: "Wertspalte" im Auftrag = Total-Zeile des Stat-Sheets (Grau = Basis
72, Aenderung, Ergebnis 70); die AK-315-Why-Zeile ist nur fuer
*vorgeschlagene* Relikte sichtbar (AD-014.6: gehaltene Slots sind Baseline),
deshalb wurde der Fluch als Favourite erzwungen statt gehalten.
NÄCHSTER: director (Urteil unten; Ingame-Test des Nutzers steht vor dem Tag).
BLOCKIERT DURCH: nichts.
```

# T-293b - QA am Artefakt 1.14.0

## Umgebung

- Artefakt `dist/NightreignHelper.exe`: **59.213.433 B, SHA-256
  `79E217617481B086FD63610EB3DB0A60E1C64BDBAE15294045320D98C22FD8B4`**
  (Python `hashlib`, 22:10) - deckungsgleich mit T-293a. Fenstertitel
  "Nightreign Helper 1.14.0". Stand `7fc2898` (= `df73927` plus
  Doku-Commit T-293c; `git diff df73927 HEAD -- nrplanner/` leer).
- NH-004: `tasklist` vor dem ersten Start ohne `NightreignHelper`/
  `nightreign` (22:10); am Ende `Get-Process NightreignHelper` = **0**
  (22:27). Zwei Starts (Persistenzpruefung), beide per `WindowPattern.Close`
  sauber beendet.
- Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-293b`, `LOCALAPPDATA`/
  `APPDATA`/`USERPROFILE` auf `<Scratchpad>/T-293/qa-engineer/`; Testabzug
  v12 kopiert (841 Dateien vor und nach dem Lauf). Spielstand als Kopie
  eingefroren (SHA-256 `a4ec107c…6312`, identisch mit dem Original um 22:10;
  Fenster meldet 313 Relikte). Positivnachweis: Marken landeten unter
  `HKCU\Software\DankYeeterT-293b\NightreignHelper\advisor`; unter
  `HKCU\Software\DankYeeter\…\advisor` sind `avoided_families`/`allowed`
  nach dem Lauf leer (nur gelesen).
- Steuerung: .NET UIAutomation (Invoke/Toggle/RangeValue/Value) plus echte
  Mausklicks fuer HeroTile, Gefaessliste und die Kaestchen im `QTreeWidget`
  (Kaestchen sitzt am linken Zellenrand, +12 px; Zellenmitte selektiert nur).
  Bildnachweise per `PrintWindow` aus dem Programmfenster (Windows 11, Thread
  per-monitor-DPI-aware v2; Groessen wie gespeichert, Skalierung nicht
  gemessen), Skripte `s1..s27.ps1` + `drv.ps1` im Scratchpad.
- Suite im Arbeitsbaum (`-n auto -p no:cacheprovider`, 22:27): **1777 passed,
  11 skipped, 66 s** - wie T-292e.

## Ergebnis je Pruefpunkt

| # | Pruefpunkt | Ergebnis |
|---|---|---|
| 1a | A22 Wertspalte, Duchess Lv15, Duchess' Chalice, alle Slots leer, Deep Slot 1 = `Deep Polished Burning Scene` (Effekte ohne AR-Bezug, Fluch 6830200) | Stat-Sheet `Total 72 1H / 74 2H  -2  70 1H / 72 2H (-2.9%)`; Picker-Karte `Damage -2.1 AR` |
| 1b | AK-315.1/.2/.3 Why-Zeile (fuenf leere Slots gehalten, Fluch als Favourite, Optimize -> Why) | wortgleich `Reduced Intelligence and Dexterity: Dexterity -3 → Attack rating -2, counted against it` (UTF-8-Bytes `e2 86 92` geprueft, `21_dex_line.txt`); Intelligence-Zeile ohne Betrag |
| 1c | AK-315.1 im vollen Vorschlag (sechs Slots, Multiplikatoren) | `… Dexterity -3 → Attack rating -3, counted against it` - AD-038.5 misst im gerankten Build, nicht an der Basis; kein Befund |
| 1d | Raider Lv15 (Greataxe), Deep an, Fluch erzwungen | Stat `Total 158 1H / 180 2H  no change  158`; Why `…: Dexterity -3 — this figure does not count it.` und dieselbe Form fuer Intelligence (AK-315.4); Buff-Gegenprobe `Strength +3: Strength +3 → Attack rating +6` ohne Zusatz (AK-315.2) |
| 1e | Recluse Lv15 (Staff) | Wort `Spell power`: `…: Dexterity -3 → Spell power -3, counted against it` - Betrag steht auf der Dexterity-Zeile, obwohl der Stab auf Intelligence skaliert -> QA-285 (Spec-Frage) |
| 2a | A23 Filters: Familie `Improved Attack Power` (13 Mitglieder, Copies 18) Avoid, `Improved Dagger Attack Power` Allow | Registry `avoided_families=[Improved Attack Power]`, `allowed=[7330000]`; Zaehler `18 of 340 effects · 1 family avoided` (Bild `18_filters_family.png`) |
| 2b | Optimize danach (Duchess, sechs Slots) | Why-Volltext ohne jedes Familienmitglied (vor dem Avoid standen Hammers/Great Hammers/Thrusting Swords/Daggers im Vorschlag); Allow-Mitglied nicht erzwungen (nicht im Vorschlag) |
| 2c | Picker-Gegenprobe | `Improved Dagger Attack Power` zaehlt (`+3.2 AR`, Slot 3 und Deep Slot 2); Hammers/Great Hammers/Thrusting Swords/Katana `no change` |
| 2d | AK-316.5 Zaehlerklausel | `3 of 340 effects · 2 favourited · 1 family avoided` - Ids und Familien getrennt, nie addiert; Nullklauseln entfallen; Singular `1 family avoided` (Annahme des developers, an T-293d) |
| 2e | AK-316.7 Persistenz | Nach Neustart ohne Bedienung: `340 of 340 effects · 1 family avoided`, Avoid-Kaestchen am Kopf und Allow bei Dagger gesetzt (`25_filters_after_restart.png`) |
| 2f | AK-316.4 Allow bleibt gespeichert | Familien-Avoid aus -> `allowed` bleibt `[7330000]`, Zaehler ohne Klausel; wieder an -> Klausel und Haekchen sofort zurueck |
| 2g | AK-316.6 Suche `Dagger` | Kopf `Improved Attack Power` bleibt, darunter nur die zwei Dolch-Mitglieder; `{gezeigt}` = 4 (Id-Zeilen, keine Koepfe) |
| 3a | AK-314.1 Hold Deep Slot 1 + ein Favourite darauf | Block Slot 1: `Partial HP Restoration upon Post-Damage Attacks +1, which you favourited, is carried by Deep Polished Burning Scene held in Slot 4.` - nur auf der ersten Karte |
| 3b | AK-314.2 zwei Favourites | `2 favourited effects are already carried by relics you hold.` - eine Zeile, nur Karte Slot 1 (AK-314.3) |
| 3c | Gegenprobe Hold geloest, Favourites entfernt | keine Zeile; Fluch-Favourite ohne passenden Slot: `3 slots are blocked by a requirement you marked` + Why `You own 8 copies carrying …, but none fits the open slots (Deep of Night is off).` |

## Befunde

### [P3 | Minor | Hoch] Statuszeile zaehlt gehaltene Slots als "nothing to choose from"

**Adressat:** developer
**Betroffen:** `nrplanner/advisorbar.py:926-936` (`_on_ready`: `slots` = alle
Slots, `filled` = `len(best.choices)` ohne gehaltene; `slots - filled` wird
`slots_without_a_choice`)
**Umgebung:** Artefakt 1.14.0, Duchess' Chalice, Deep an

**Reproduktion:**
1. Deep Slot 1 mit einem Relikt belegen, `Hold` setzen.
2. Optimize.

**Erwartet:** Zeile nennt den gehaltenen Slot als gehalten (wie der
Why-Footer: `5 of 6 slots are held, so only the other 1 was filled.`).
**Tatsaechlich:** `Maximise damage — 5 of 6 slots filled · 1 slot has nothing
to choose from.`; mit fuenf gehaltenen Slots `… 1 of 6 slots filled · 5 slots
have nothing to choose from.` - der gehaltene Slot hat 22 waehlbare Kopien.
**Analyse:** Zaehlung seit `775173c`/`e1cad99` (07.09.) unveraendert - kein
Regress von 1.14.0; Hypothese: `filled` muesste die gehaltenen Slots
mitzaehlen oder die Klausel auf `slots - held - filled` gehen.
**Auswirkung:** Falsche Aussage auf dem Hauptpfad (Hold ist Alltagsfunktion);
Workaround: Why-Footer sagt es richtig.
**Vorschlag:** `slots_without_a_choice` aus den tatsaechlich leer
zurueckgekommenen Pools ableiten; Test mit einem gehaltenen und einem
leeren Slot, der ohne Fix rot ist.

### [unklar | Spec-Frage] AK-315.3: Betrag haengt an der ersten Attributzeile in `ATTRIBUTE_ORDER`, nicht an dem Attribut, das die Waffe skaliert

**Adressat:** ui-ux-designer (Spec-Eigner), Entscheidung director
**Betroffen:** `nrplanner/advisor/explain.py` `_first_attribute` (setzt
AK-315.3 woertlich um)
**Belege am Artefakt (Why-Dialog):**
- Recluse (Staff, Int-skaliert): `Reduced Intelligence and Dexterity:
  Dexterity -3 → Spell power -3, counted against it`, Intelligence-Zeile
  nackt; `[Recluse] Improved Intelligence and Faith, Reduced Mind: Mind -13
  → Spell power +13` (Intelligence +12 nackt); `Reduced Strength and
  Intelligence: Strength -3 → Spell power -3, counted against it`.
- Duchess (Dagger, Dex-skaliert): `[Duchess] Improved Vigor and Strength,
  Reduced Mind: Vigor +3 → Attack rating +8` (Strength +24 nackt).
- Die Zeilen eines Effekts stehen zudem nicht in `ATTRIBUTE_ORDER`
  (Recluse: Intelligence vor Dexterity), der Betrag also auch nicht auf der
  ersten sichtbaren Zeile.

**Lesart A (Absicht):** AK-315.3 verlangt genau das ("nur die erste Zeile in
`model.ATTRIBUTE_ORDER` traegt den Betrag"); ein Effekt, ein Betrag; die
Umsetzung ist spec-konform, A22-Nachweis (Betrag genannt) erfuellt.
**Lesart B (Bug in der Spec):** Der Leser schliesst aus `Mind -13 → Spell
power +13`, dass Mind die Zauberkraft hebt; AD-038.3 "an derselben Zeile,
die den Attributwert nennt" meinte das tragende Attribut. Traefe B, waere
das ein Minor/Mittel (Erklaerung falsch zugeordnet, Zahl richtig).
**Nicht von mir entschieden.** Register: `unklar`.

## Beobachtungen (ohne Nummer)

- AK-314.1 nennt den gehaltenen Deep Slot 1 als `held in Slot 4` (Format
  `explain.curses`, spec-konform), waehrend Karte und Picker ihn `Deep Slot
  1` nennen - an T-293d zur Kenntnis.
- Der Betrag im vollen Vorschlag (-3) weicht vom Basisbeispiel der Spec (-2)
  ab, weil die Multiplikatoren des Builds mitskalieren - AD-038.5-konform.
- Nach dem Neustart oeffnete das Fenster auf Wylder (vorher Recluse aktiv);
  ob die Heldenwahl persistieren soll, ist nicht Teil dieses Auftrags.
- Picker-Suche `"Burning Scene"` trifft keinen Reliktnamen (nur Effekttexte)
  - bestehendes Verhalten, kein A22/A23-Punkt.

## Explorationsprotokoll

Gehalten: Optimize-Cache (zweiter identischer Lauf ohne Working-Phase),
Hold/Held-Toggle in beide Richtungen, Filterfenster oeffnen/schliessen
viermal, Suche im Filterfenster mit Familientreffer und Mitgliedstreffer,
Familien-Avoid aus/an, Heldenwechsel Duchess -> Raider -> Recluse -> Duchess
mit Deep-Zustand je Held, sauberes Beenden zweimal (Registry-Sync vollstaendig,
Werte nach Schliessen identisch).

## Nicht getestet

- Spaltenklick-Sortierung (AK-316 Akzeptanzpunkt 2), Tooltip am `Filters`-
  Knopf und Legende/Tooltips AK-317 - T-293d (ui-ux-designer).
- AK-314.4/.5/.6 (already_equipped-Fall, Why-Footer-Volltext, Stylesheet) -
  ueber die Suite (1777 passed) abgedeckt, nicht am Fenster wiederholt.
- Optimize-Laufzeit (A6) - nicht Teil des Auftrags.

## Zusammenfassung (an director)

Befunde: P3 x1 (QA-284, Bestand seit 07.09., kein Regress), Spec-Frage x1
(QA-285, `unklar`). Keine P1/P2. Abnahmekriterien A22 (72 -> 70, Betrag in
der Why-Zeile wortgleich) und A23 (Familie vermieden, Allow-Mitglied zaehlt,
nicht erzwungen, persistent) am Artefakt belegt; Suite gruen.

**Urteil: CONCERNS** - releasefaehig aus QA-Sicht, sobald der director
QA-285 (Lesart A oder B) entschieden hat; QA-284 kann nach dem Release
folgen. Releasevotum: ja, mit dieser einen Entscheidung.
