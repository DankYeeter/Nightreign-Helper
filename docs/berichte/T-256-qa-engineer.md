# T-256 — Register-Triage der offenen P2 (qa-engineer, 15.09.2026)

Stand: HEAD `ddbea26`, lesend. Register nicht angefasst; die Zeilen zum
Anhaengen stehen unten in Abschnitt 5 (Director/Hauptsession uebernimmt).

## 0. Annahmen

- **Zaehlung:** `grep -n "| P2 |" qa/findings.md` liefert 105 Zeilen; nach
  "juengste Zeile je Befund" und Status-Erstwort nicht in
  {behoben, geschlossen, zurueckgestellt, waived} bleiben **38** Befunde, nicht
  44 wie im Auftrag (Skript `scratchpad/T-256/triage.py`, 15.09. 00:58). Eine
  39. Zeile (QA-244) beginnt mit `**behoben` und faellt nur wegen der
  Fettschrift durch jeden Erstwort-Filter — Formfehler, siehe Beobachtungen.
  Ich habe auf dem Bestand (38) gearbeitet.
- "Behoben" heisst hier: Code am HEAD zeigt die Wirkung, ein Commit oder Test
  belegt sie. Am gebauten Artefakt ist nichts davon wiederholt.
- Fensterlaeufe: keiner noetig ausser fuer QA-222 (echte Maus) und QA-175
  (echter Bildschirm); beide stehen als unklar bzw. am Code geprueft.
  Offscreen-Lauf fuer QA-200 mit eingefrorenem Spielstand und Store
  `DankYeeterTests` (conftest-Rezept), Umlenkung LOCALAPPDATA/APPDATA/
  USERPROFILE in den Scratchpad gesetzt.

## 1. Zaehlung je Kategorie (38 offene P2)

| Kategorie | Anzahl | IDs |
|---|---|---|
| a — bereits behoben | **23** | QA-005, 032, 055, 099, 101, 102, 119, 122, 125, 126, 129, 132, 133, 137, 154, 156, 161, 180, 181, 187, 199, 200, 208 |
| b — noch offen | **10** | QA-004, 016, 036, 099a, 172, 173, 175, 186, 222, 241 |
| c — Prozess-/Testschuld ohne Programmwirkung | **5** | QA-077, 094, 196, 197, 238 |
| d — gegenstandslos | **0** | — |

Nach der Triage bleiben **10 offene P2 mit Programmwirkung**; davon empfehle
ich vier zur Herabstufung (QA-004 → P3, QA-016 → P4, QA-099a → P4, QA-036
Release-Sperre pruefen). Entscheidung: director.

## 2. Triage-Tabelle P2

| ID | Kat. | Beleg | Aufwand | Adressat |
|---|---|---|---|---|
| QA-004 | b (teilweise) | `inventory.scan` waehlt weiter still das bestbelegte Save (inventory.py:426-441). Abmilderung: gelesener Ordner im Tooltip der Bestandszeile (61633c5), `Find my save...` mit S3-Satz "more than one Steam account" (3f08e0a, 09.09.). Der dritte Zustand aus dem Director-Entscheid 02.09. ("gelesen, N uebersprungen") fehlt. | klein (SaveScan traegt Zahl der uebersprungenen Saves, Bestandszeile nennt sie) | developer, ui-ux-designer — Empfehlung P3 |
| QA-005 | a | Suite 1627 passed / 9 skipped (Director, `ddbea26`, 15.09.); 102 Dateien unter `tests/` (`git ls-files`). Rest als QA-037 (P3) gefuehrt. | — | — |
| QA-016 | b | Zwei Identitaetsregeln bestehen fort: Picker `inventory.copy_key` (Handle, sonst Offset; relicslots.py:159-170), Berater `relic.handle is None → kein Kandidat` (candidates.py:308; AD-013 Pkt 4 unveraendert). Wirkung nur bei Save ohne lesbare Loadout-Tabelle, dort mit A7-Zeile (`without_handle`). Verlauf-Entscheid 02.09. ("dieselbe Identitaetsregel") nicht umgesetzt. | klein | architect (Entscheid), developer — Empfehlung P4 |
| QA-032 | a | 8f68b49 (09.09.): `if best is None and unreadable: raise SaveNotReadable` (inventory.py:439) → `UNREADABLE_SAVE` (app.py:243); S4-Weg `savereader.read_the_save`. | — | — |
| QA-036 | b | `firstrun.what_is_needed` prueft Manifest-Existenz und `icon_version` (firstrun.py:87-115), `IconPack.available` nur Manifest-Inhalt (iconpack.py:71). Kein Abgleich Manifest gegen Dateibestand; `iconbuild.py` seit 22.08. unveraendert (kein temp+rename). | klein | developer. Register sagt "sperrt Release, A9" — A9 ist seit T-241d am Artefakt PASS: director prueft die Sperre |
| QA-055 | a | Zweite Haelfte (Tier sichtbar): Waffenkachel nennt "Rare +1" (weaponslots.py:246-253), Arsenal-Kopfzeile ", +n" (arsenaltab.py:360), Kachelzeile "Upgraded to +n Rarity" (arsenaltab.py:548-552). Erste Haelfte seit W4 (Pruefpunkt 20). AK-33-Wortlaut `AR at +<n>` ist nicht gebaut — Spec-Frage, kein Nutzerproblem. | — | Spec-Frage an ui-ux-designer |
| QA-077 | c | `_show_breakdown` (statsheet.py:318-358) baut den Tooltip-Text weiter lokal; kein Test referenziert `_show_breakdown` oder `QToolTip` (zwei Masken ueber `tests/*.py`: 0/0 Treffer). Testschuld; kein Fehler bekannt. | klein (Text in `_breakdown_text(key)` ausziehen, Test auf Prozentzeile) | developer |
| QA-094 | c | Prozessbefund (Push vor QA-Ergebnis, 03.09.). | — | director |
| QA-099 | a | f595edb (05.09.) `damage.SPELL_POWER_LABEL`, Katalysator-Skalierung extrahiert (2a6bb3e); Tests `test_weapon_rating_scaled_per_type.py`, `test_one_name_per_figure.py`. | — | — |
| QA-099a | b (teilweise) | Fremdzeile 33770000 aus allen Angeboten (217796a = QA-119). Im Abzug bleiben 3 Doppelnamen / 8 Zeilen: `Finger Seal` 2x, `Scholar's Thrusting Sword` 4x, `Recluse's Staff` 2x — alle zahlengleich (gezaehlt 15.09. am Testabzug, 1793 Waffen). | klein | developer — Empfehlung P4 (kosmetisch) |
| QA-101 | a | cba8335 (05.09.) goals.py rankt auf `equipped`-Basis; Fall in `test_advisor_goals.py:318ff` prueft die Drehung. | — | — |
| QA-102 | a | 5d94d06 (05.09., T-048) `SlotPool` traegt `unknowns/weights_note/unit/display` (types.py:476-486); Pruefpunkt 32 `test_advisor_candidates.py:166`. | — | — |
| QA-119 | a | 217796a (05.09.) `model.is_unequippable_catalyst` (model.py:481), `test_unequippable_catalyst.py`. | — | — |
| QA-122 | a | `qa/verlauf.md:1605` (T-053, 05.09.): zehn Screenshots `docs/screenshots/2026-09-05/`; seither Fensterlaeufe T-076, T-239, T-241 mit PrintWindow-Belegen. | — | — |
| QA-125 | a | da94711 (05.09.): Spalte heisst `Relic slots`, Tooltip "not a count of loot pools" (effectstab.py:141-144); `test_effects_tab_display.py:174`. | — | — |
| QA-126 | a | da94711: Mittel nach Vorkommen gewichtet (effectstab.py:963-970); `test_effects_tab_display.py:99`. | — | — |
| QA-129 | a | 555d749 (05.09.): getippte Debuff-Konstanten entfernt (bosstab.py:135), `ladder.down` gezeigt (bosstab.py:975); `test_nightlord_panel_display.py`. | — | — |
| QA-132 | a | a6f701c (05.09.): `Examples (any map)`, `NO_NAMES = "— the files name none"` (depthstab.py:54-58); `test_red_variants_display.py`. | — | — |
| QA-133 | a | d4ce7c7 (05.09.) eventstab.py:78 (AK-103); `test_world_events_display.py`. | — | — |
| QA-137 | a | cb006e4 (05.09.): je Tab ein Anzeigetest (`test_effects/nightlord_panel/red_variants/world_events/deep_tab_display.py`, `tests/tabtext.py`). | — | — |
| QA-154 | a | c9682d2 (06.09.) Zeigermarke (bosstab.py:52); `test_nightlord_selection.py:318,354`. | — | — |
| QA-156 | a | cae0e2b (06.09.) `COPIES_DEFINITION`, Beschriftung der vier Filter (effectstab.py:156); `test_effects_tab_display.py:270ff`. | — | — |
| QA-161 | a | ab1eab3 (06.09.) `pressable.PressableFrame`/`CardAccessible`, `BossCard` als Button mit Namen; `test_card_is_pressable.py`. | — | — |
| QA-172 | b | `EffectsTab.refresh` behaelt je Identitaet den ersten Roheintrag samt `curse` (effectstab.py:913-920, Anzeige :988). Abzug: **12 von 1064** Identitaeten mit widerspruechlichem `curse` (never/sometimes), nachgezaehlt 15.09. — unveraendert gegen den Befund. | klein (curse ueber die Gruppe neu bilden: alle always → always, alle never → never, sonst sometimes) | developer |
| QA-173 | b | Gefaessliste zeichnet Slot-Chips (seit 21f7a92, vor dem Befund); kein erklaerender Satz oder Tooltip (`chalice_list.setToolTip`: 0 Treffer in app.py). A11-Rest. | klein | ui-ux-designer |
| QA-175 | b | `showEvent` klemmt nur die Breite an `availableGeometry().width()` (app.py:941-958, 996-1021); keine Positionsklemmung, kein `move(` in app.py (0 Treffer). Am echten Bildschirm nicht wiederholt. | klein (nach dem Resize gegen `availableGeometry` klemmen) | developer |
| QA-180 | a | 90ff81d (06.09.) Zuordnung ueber Effekt-Id (explain.py:146, model.py:1057). | — | — |
| QA-181 | a | 6f54445 (06.09.) `test_advisor_evaluate.py:412` haelt die Multimenge der Quellen. | — | — |
| QA-186 | b | `model.GATE_FIELDS` beschriftet `wepTypeTriggerCount` unveraendert "needs several of that weapon equipped" (model.py:1207-1210, angewandt :1304). Abzug 15.09.: **51** Effekte mit Wert != 3 tragen alle `startGoodsId` (256:27, 512:19, 1024:3, 768:2), **31** mit Wert 3 keines — Zahlen des Befunds bestaetigt. `explain.py:329` hat die Trennung (AK-178), `model.py` nicht. | klein (Beschriftung nur ohne `startGoodsId`; `triggerOnWepType` 256/512 nur, wenn der Wert ein Waffentyp ist) | developer |
| QA-187 | a | 4462a88 (07.09.) `_silent_effect` in AK-167-Reihenfolge (explain.py:451-458), `_ARMAMENT_GATES` ohne `wepTypeTriggerCount`; `test_advisor_explain.py:1373`. | — | — |
| QA-196 | c | Prozess (Worktree-Stand). | — | director |
| QA-197 | c | Prozess (geteilter Scratchpad). | — | director |
| QA-199 | a | d2cfbfc (09.09.) `firstrun._pick_a_folder`, `Choose folder...` (firstrun.py:247); A15 laut state.md gebaut. | — | — |
| QA-200 | a | Scratchpad wird bei jeder Aenderung geschrieben (`chalices.save`, app.py:1637) und beim Start wiederhergestellt (app.py:1464-1475). **Nachgestellt 15.09. offscreen** (eingefrorener Spielstand, Store `DankYeeterTests`, Skript `scratchpad/T-256/qa200_restart.py`): Slot 1 von `3229614365/1007202` auf `3229614199/13001` geaendert → Fenster geschlossen → neu gebaut → Slot 1 identisch (`RESTORED`). Die T-115-Beobachtung passt zur AK-226-Race (09518a4, 08.09.). Am Artefakt nicht wiederholt. | — | — |
| QA-208 | a | 1a2cc5b (08.09., AD-028): "Nothing is computed here any more" (relicpicker.py:449); Hauptthread-Anteil 7 ms (T-140) und 5 ms (T-241). | — | — |
| QA-222 | b (unklar) | Nur mit echter Maus am nicht-vorderen Fenster entscheidbar; kein Fensterlauf in diesem Auftrag. Nutzer-Ingame-Session 14.09. (echte Maus) meldet nichts dergleichen — kein Beleg. | — | qa-engineer (Fensterlauf mit `mouse_event`), dann developer |
| QA-238 | c | 5 Laeufe `pytest tests/test_advisor_worker.py` (15.09.): 5x 18 passed. Ein Vorkommnis, nie wieder; Klasse bei QA-249 beobachtet. | — | developer — Empfehlung: in QA-249 aufgehen lassen |
| QA-241 | b | **Reproduziert 15.09. 01:02** in dieser Sitzung: `python C:/does-not-exist-probe/run.py` lief durch (Python-Fehler, keine Hook-Abweisung). Derselbe Befehl per stdin an `.claude/hooks/enforce-data-redirect.ps1` → `permissionDecision: deny`. Logik richtig, Wirkung in der Sitzung fehlt — nicht nur in der Installationssitzung vom 12.09. | — (Umgebung, kein Code) | director / Nutzer: in der Hauptsitzung pruefen; bis dahin gilt die Handregel weiter |

## 3. Triage P3 mit Programmwirkung (teilweise, Kommit-Ebene)

Nur Befunde, deren Fix-Commit die ID oder den Gegenstand nennt und deren
Code-Marke am HEAD steht (Stichprobe im Code bei QA-107, 130, 131, 142, 143,
163, 183). Nicht in der Tabelle = nicht triagiert (53 von 76 offenen P3).

| ID | Kat. | Beleg |
|---|---|---|
| QA-099c | a | 2a6bb3e (05.09.) Katalysator-Skalierung als benanntes Feld extrahiert |
| QA-106 | a | bf421d2 (05.09.) Geltungsbereich in der Registry |
| QA-107 | a | 9d9df0d (05.09.) `held_fingerprint` gestrichen (types.py:22) |
| QA-108 | a | e76123f (05.09.) Pool-Zeilen mit entschiedenem Wortlaut (candidates.py:105) |
| QA-115 | a | 1ae44ab (05.09.) Zahl nachfahrbar |
| QA-120 | a | 9c41325 (05.09.) Geltungsbereich der zwei Zahlen benannt |
| QA-121 | a | ddfa93a (05.09.) Zusammenfassung definiert beide Kennzahlen (AK-64) |
| QA-127 | a | da94711 (05.09.) Copies/Tier je Identitaet (AK-81) |
| QA-130 | a | 555d749 (05.09.) Sentinel -1 (bosstab.py:904) |
| QA-131 | a | 555d749 (05.09.) Adel-Schwaechen (bosstab.py:854) |
| QA-134, QA-135 | a | d4ce7c7 (05.09.) World Events Saetze |
| QA-142, QA-143 | a | fd3c3b6 (05.09.) feste Reihenfolge, Kachel hinter jeder Suche (arsenaltab.py:400, 489) |
| QA-145 | a | b8316f5 (05.09.) zweites Gruen benannt |
| QA-146 | a | 6790f16 (05.09.) Messung unter Fusion (conftest.py:225) |
| QA-150 | a | d7fb01f (05.09.) Auswahlmarke (pressable.py:144) |
| QA-151 | a | 49811a8 (05.09.) Kopf-Tooltip im kurzen Hover |
| QA-155 | a | 7dff1ae (06.09.) Nightfarer benannt, Ort genannt |
| QA-163 | a | 231c42b (06.09.) `singleinstance.py` |
| QA-182 | a | 219909d (06.09.) Zahl und Ordnung von `not_counted` gehalten |
| QA-183 | a | 91fbe36 (06.09.) is/are (explain.py:829) |
| QA-201 | a | d93a6bb (09.09.) `test_the_owned_total_has_its_own_line.py` |
| QA-209 | a | 09518a4 (08.09.) `_SaveReadWorker` (savereader.py), AD-029 |
| QA-157 | b | nur `BossCard` ist `PressableFrame`; `RelicCard`, `CustomRelicCard` (relicpicker.py:640, 805) und `WeaponTile` (weaponslots.py:163) sind weiter `QFrame` mit `mousePressEvent`, kein `enterEvent`/`hover` in diesen Modulen (0 Treffer) — unveraendert offen, ui-ux-designer/developer |
| QA-009 | b | savefile.py:590-611: eine Gruppe wird nur mit gefundenem *naechstem* Marker gezaehlt, die letzte Heldengruppe nie — `len(groups) >= 4` verlangt also weiterhin fuenf Marker. Synthetischer Fall, echte Saves tragen alle Nightfarer-Marker; Aufwand klein (`>= MIN_HEROES - 1` oder letzte Gruppe zaehlen) |

## 4. Befunde und Beobachtungen aus diesem Lauf

### [P2 | Major | Hoch] Der Datenumlenkungs-Hook feuert in dieser Sitzung nicht (QA-241 fortbestehend, kein neuer Befund)

**Adressat:** director (Umgebung), Nachweis beim Nutzer
**Reproduktion:** siehe QA-241 in Tabelle 2 (Befehl, Zeit, stdin-Gegenprobe).
**Auswirkung:** `CLAUDE.md` verspricht eine Sperre, die fuer Subagenten-
Sitzungen nachweislich nicht greift; jede Rolle muss die Umlenkung weiter
von Hand setzen. Kein Datenzugriff in diesem Lauf (Probe-Datei existiert nicht).

**Beobachtungen (keine Befunde):**
- `qa/findings.md:269` (QA-244) beginnt die Statuszelle mit `**behoben` —
  Fettschrift vor dem Erstwort; NH-003 prueft die Spaltenform, nicht das
  Erstwort. Bei der naechsten Fortschreibung als `behoben -- ...` anhaengen.
- Nach einer Slot-Aenderung bleibt `build_box` auf `Equipped in game`
  (offscreen beobachtet, QA-200-Skript: `after = (..., 'Equipped in game')`).
  Ob die Liste nach einer Aenderung auf `Unsaved build` springen soll, ist
  eine Spec-Frage (ui-ux-designer); QA-170 war geschlossen, Zusammenhang
  nicht geprueft.

## 5. Registerzeilen zum Anhaengen (qa/findings.md, nur anhaengen)

```
| QA-004 | **Statuswechsel (T-256, 15.09.2026):** Automatik waehlt weiter still (inventory.py:426-441); Abmilderung Ordner-Tooltip (61633c5), Find my save mit Konto-Satz (3f08e0a); Zustand "N uebersprungen" fehlt | P2 | Major | developer, ui-ux-designer | Codelesung T-256 | teilweise -- Empfehlung P3, Rest klein | 2026-09-15 |
| QA-005 | **Statuswechsel (T-256, 15.09.2026):** 1627 passed / 9 skipped auf ddbea26, 102 Testdateien; Rest ist QA-037 | P2 | Major | director, developer | Director-Lauf 15.09. | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-016 | **Statuswechsel (T-256, 15.09.2026):** zwei Identitaetsregeln bestehen fort (copy_key mit Offset im Picker, Handle-only im Berater, AD-013 Pkt 4 unveraendert); Wirkung nur ohne lesbare Loadout-Tabelle, A7-Zeile vorhanden | P2 | Major | architect, developer | Codelesung T-256 | offen -- Empfehlung P4, Aufwand klein | 2026-09-15 |
| QA-032 | **Statuswechsel (T-256, 15.09.2026):** seit 8f68b49 (09.09.) wirft inventory.scan SaveNotReadable, wenn kein Save lesbar war; UNREADABLE_SAVE statt "No save file found" | P2 | Major | developer, ui-ux-designer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-036 | **Statuswechsel (T-256, 15.09.2026):** what_is_needed prueft nur Manifest und icon_version, kein Dateibestand, iconbuild seit 22.08. unveraendert; A9 inzwischen am Artefakt PASS (T-241d) | P2 | Major | developer, director | Codelesung T-256 | offen -- Aufwand klein; Release-Sperre pruefen | 2026-09-15 |
| QA-055 | **Statuswechsel (T-256, 15.09.2026):** Tier sichtbar auf Waffenkachel (Rare +1), Arsenal-Kopfzeile (+n) und Kachelzeile "Upgraded to +n"; AK-33-Wortlaut "AR at +n" nicht gebaut (Spec-Frage) | P2 | Major | developer, ui-ux-designer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-077 | **Statuswechsel (T-256, 15.09.2026):** _show_breakdown weiter ungetestet (0 Treffer in tests/), kein Fehler bekannt | P2 | Major | developer | grep T-256 | offen -- Testschuld ohne Programmwirkung, Aufwand klein | 2026-09-15 |
| QA-094 | **Statuswechsel (T-256, 15.09.2026):** Prozessbefund | P2 | Major | director | -- | offen -- Prozess ohne Programmwirkung | 2026-09-15 |
| QA-099 | **Statuswechsel (T-256, 15.09.2026):** f595edb (05.09.) Spell power als Kennzahl der Katalysatoren, Tests test_weapon_rating_scaled_per_type, test_one_name_per_figure | P2 | Major | developer, ui-ux-designer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-099a | **Statuswechsel (T-256, 15.09.2026):** 33770000 aus allen Angeboten (217796a); im Abzug bleiben Finger Seal 2x und Scholar's Thrusting Sword 4x zahlengleich | P2 | Major | developer | Testabzug gezaehlt T-256 | teilweise -- Rest kosmetisch, Empfehlung P4 | 2026-09-15 |
| QA-101 | **Statuswechsel (T-256, 15.09.2026):** cba8335 (05.09.) equipped-Basis, Drehungsfall in test_advisor_goals | P2 | Major | director, developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-102 | **Statuswechsel (T-256, 15.09.2026):** 5d94d06 (05.09., T-048) SlotPool traegt unknowns; Pruefpunkt 32 | P2 | Major | director, developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-119 | **Statuswechsel (T-256, 15.09.2026):** 217796a (05.09.) is_unequippable_catalyst, test_unequippable_catalyst | P2 | Major | ui-ux-designer, developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-122 | **Statuswechsel (T-256, 15.09.2026):** verlauf.md:1605, Screenshots 05.09. (T-053); Fensterlaeufe T-076/T-239/T-241 | P2 | Major | ui-ux-designer | verlauf T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-125 | **Statuswechsel (T-256, 15.09.2026):** da94711 (05.09.) Spalte Relic slots, Tooltip nennt es; test_effects_tab_display:174 | P2 | Major | developer, ui-ux-designer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-126 | **Statuswechsel (T-256, 15.09.2026):** da94711 gewichtetes Mittel (effectstab.py:963-970); test_effects_tab_display:99 | P2 | Major | developer, ui-ux-designer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-129 | **Statuswechsel (T-256, 15.09.2026):** 555d749 (05.09.) Konstanten weg, ladder.down gezeigt; test_nightlord_panel_display | P2 | Major | developer, ui-ux-designer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-132 | **Statuswechsel (T-256, 15.09.2026):** a6f701c (05.09.) Examples (any map), NO_NAMES; test_red_variants_display | P2 | Major | developer, ui-ux-designer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-133 | **Statuswechsel (T-256, 15.09.2026):** d4ce7c7 (05.09.) eventstab.py:78 (AK-103); test_world_events_display | P2 | Major | developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-137 | **Statuswechsel (T-256, 15.09.2026):** cb006e4 (05.09.) Anzeigetest je Tab, tabtext.py | P2 | Major | developer, director | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-154 | **Statuswechsel (T-256, 15.09.2026):** c9682d2 (06.09.) Zeigermarke; test_nightlord_selection:318 | P2 | Major | ui-ux-designer, developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-156 | **Statuswechsel (T-256, 15.09.2026):** cae0e2b (06.09.) COPIES_DEFINITION, Filterbeschriftung; test_effects_tab_display:270ff | P2 | Major | ui-ux-designer, developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-161 | **Statuswechsel (T-256, 15.09.2026):** ab1eab3 (06.09.) PressableFrame, BossCard als Button mit Namen; test_card_is_pressable | P2 | Major | developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-172 | **Statuswechsel (T-256, 15.09.2026):** unveraendert, 12 von 1064 Identitaeten mit widerspruechlichem curse (Testabzug), merge behaelt ersten Roheintrag (effectstab.py:913-920) | P2 | Major | developer | Testabzug gezaehlt T-256 | offen -- Aufwand klein | 2026-09-15 |
| QA-173 | **Statuswechsel (T-256, 15.09.2026):** kein erklaerender Text an der Gefaessliste (Slot-Chips bestanden schon vor dem Befund) | P2 | Major | ui-ux-designer | Codelesung T-256 | offen -- Aufwand klein | 2026-09-15 |
| QA-175 | **Statuswechsel (T-256, 15.09.2026):** showEvent klemmt nur die Breite, keine Positionsklemmung (kein move in app.py); Bildschirm nicht wiederholt | P2 | Major | developer | Codelesung T-256 | offen -- Aufwand klein | 2026-09-15 |
| QA-180 | **Statuswechsel (T-256, 15.09.2026):** 90ff81d (06.09.) Zuordnung ueber Id | P2 | Major | developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-181 | **Statuswechsel (T-256, 15.09.2026):** 6f54445 (06.09.) Multimengen-Test test_advisor_evaluate:412 | P2 | Major | developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-186 | **Statuswechsel (T-256, 15.09.2026):** unveraendert in model.GATE_FIELDS; 51 startGoodsId-Effekte mit Waffenzahl-Text bestaetigt (Testabzug); explain.py hat die Trennung (AK-178), model.py nicht | P2 | Major | developer | Testabzug gezaehlt T-256 | offen -- Aufwand klein | 2026-09-15 |
| QA-187 | **Statuswechsel (T-256, 15.09.2026):** 4462a88 (07.09.) AK-167-Reihenfolge; test_advisor_explain:1373 | P2 | Major | developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-196 | **Statuswechsel (T-256, 15.09.2026):** Prozessbefund | P2 | Major | director | -- | offen -- Prozess ohne Programmwirkung | 2026-09-15 |
| QA-197 | **Statuswechsel (T-256, 15.09.2026):** Prozessbefund | P2 | Major | director | -- | offen -- Prozess ohne Programmwirkung | 2026-09-15 |
| QA-199 | **Statuswechsel (T-256, 15.09.2026):** d2cfbfc (09.09.) Ordnerwahl im Erststart (A15) | P2 | Major | developer | Codelesung T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-200 | **Statuswechsel (T-256, 15.09.2026):** Scratchpad wird je Aenderung gespeichert und beim Start wiederhergestellt; offscreen nachgestellt (Slot geaendert, geschlossen, neu gebaut: identisch); T-115 passt zur AK-226-Race (09518a4); Artefakt nicht wiederholt | P2 | Major | developer | offscreen-Lauf T-256 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-208 | **Statuswechsel (T-256, 15.09.2026):** 1a2cc5b (08.09., AD-028) Picker rechnet nicht mehr im Aufrufer; Hauptthread 7 ms (T-140), 5 ms (T-241) | P2 | Major | architect, developer | Messungen T-140/T-241 | behoben -- Nachzug T-256 | 2026-09-15 |
| QA-222 | **Statuswechsel (T-256, 15.09.2026):** ohne echte Maus nicht entscheidbar, kein Fensterlauf in T-256 | P2 | Major | qa-engineer, developer | -- | unklar -- Fensterlauf mit echter Maus offen | 2026-09-15 |
| QA-238 | **Statuswechsel (T-256, 15.09.2026):** 5x 18 passed in test_advisor_worker.py, nie wieder beobachtet | P2 | Major | developer | 5 Laeufe T-256 | offen -- Testschuld ohne Programmwirkung, Empfehlung in QA-249 aufgehen lassen | 2026-09-15 |
| QA-241 | **Statuswechsel (T-256, 15.09.2026):** reproduziert 01:02 in einer Subagent-Sitzung: python C:/does-not-exist-probe/run.py lief durch, stdin-Gegenprobe des Hooks sagt deny | P2 | Major | director | live und stdin T-256 | offen -- Wirkung fehlt weiter, Nachweis in der Hauptsitzung | 2026-09-15 |
```

## 6. Explorationsprotokoll

- Zaehlskript ueber das Register (juengste Zeile je ID), P2 und P3.
- Je P2: Codelesung am HEAD, `git log -S`/`--grep`, Tests per Dateiname;
  Zaehlungen am Testabzug (Waffen-Doppelnamen, curse-Widersprueche,
  wepTypeTriggerCount/startGoodsId) mit Python, lesend.
- Offscreen-Lauf QA-200 (eingefrorener Spielstand, Store der Tests).
- `pytest tests/test_advisor_worker.py` 5x (QA-238).
- Hook-Probe live und per stdin (QA-241).
- Kein Fensterlauf, kein Vollauf, keine Datei im Arbeitsbaum ausser diesem
  Bericht.

## 7. Uebergabe (STATUS: teilweise — Zugschwelle 150 erreicht, 01:23)

- **Fertig:** Triage aller 38 offenen P2 (Tabelle 2, Registerzeilen 5), 25
  P3 auf Kommit-Ebene (Tabelle 3). Kein Commit (Auftrag: keiner), keine
  Datei im Arbeitsbaum ausser diesem Bericht.
- **Offen:** Fensterlauf QA-222 mit echter Maus. Vorbereitet, nicht
  gestartet: `scratchpad/T-256/qa222_run.ps1` (setzt die drei Umlenkungen,
  startet `run.py`, ruft `qa222_click.ps1`: WinForms-Fenster nach vorn,
  ein `mouse_event`-Klick auf den Reiter `Nightlords`, dann `Build planner`,
  dann `Optimize`, liest Reiterwahl/Advisor-Text per UIA, beendet den
  Prozess). Testabzug liegt kopiert unter `scratchpad/T-256/la/
  NightreignHelper/` (841 Dateien). Um 01:20 lief keine Instanz
  (`Win32_Process`: kein python/NightreignHelper). Registry-Org
  `DankYeeterT-256` nach dem Lauf loeschen.
- **Nicht geprueft:** Spaltenform des Registerblocks (Abschnitt 5) mit dem
  NH-003-Skript — von Hand auf 8 Spalten und Erstwort geschrieben, keine
  Pipes in Zellen.
- Kein Testlauf in diesem Auftrag ausser 5x `pytest tests/test_advisor_worker.py`
  (5x 18 passed); Suite zuletzt laut Director 1627/9 auf `ddbea26`.

## 8. Nicht getestet

- QA-222 (echte Maus am nicht-vorderen Fenster) und QA-175 (Position am
  echten Bildschirm): brauchen einen sichtbaren Fensterlauf mit Umlenkung.
- Alle (a)-Befunde am gebauten Artefakt.
- 53 von 76 offenen P3 (Zeit).
