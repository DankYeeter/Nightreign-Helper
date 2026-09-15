# T-263c — ui-ux-designer — Nachtrag zu T-258 auf `478101c` (15.09.2026)

```
STATUS: erledigt
AUFTRAG: T-263c - alle sieben Tabs bei 1536 px, vier Content-Tabs zusaetzlich
  bei 1608 px, DR-028 als Messartefakt schliessen, DR-029 Retest, DR-030
  Nachtrag (AN-8), AK-292/286/296/294/295 live
GELESEN: docs/tasks/T-263.md; docs/state.md (AN-1..AN-8, Zyklus-24-Verlauf);
  DESIGN_REVIEW.md (T-258-Abschnitt, DR-028/029/030 volltext);
  UI_SPEC.md §AK-294/AK-295; tests/test_stat_sheet_at_the_window.py;
  tests/advisor_row_at_the_window.py; nrplanner/app.py (Tab-Aufbau,
  _opening_width, vessel_tooltip); nrplanner/statsheet.py (HandSwitch);
  nrplanner/advisorbar.py, effecttext.py, model.py (AK-294/295-Stellen)
GEAENDERT: DESIGN_REVIEW.md (neuer Abschnitt oben, DR-028/029 ✔, DR-030
  gegenstandslos, DR-031 neu, Nice-to-have) — kein Code, kein Commit
ANNAHMEN: keine neuen
NAECHSTER: qa-engineer (T-263a) kann jetzt starten — Fensterinstanz frei,
  Registry-Rest geloescht
BLOCKIERT DURCH: nichts
```

## Methode

Live am laufenden Fenster, kein `dangerouslyDisableSandbox` diesmal noetig
(anders als T-258 — der Sandbox-Pfad rendert diesmal durch). Umlenkung
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-263`, eigenes `LOCALAPPDATA`/`APPDATA`
im Scratchpad, Testabzug (841 Dateien, `EXTRACT_VERSION` 11) hineinkopiert.
Kein eigener Klon: `git status` sauber, `HEAD` (`97b0d9a`) traegt gegenueber
dem eingefrorenen `478101c` nur einen Doku-Commit, `qa-engineer` war laut
Auftrag bis zu diesem Bericht zurueckgehalten — kein paralleler
Schreibzugriff. Zwei eigene Scratchpad-Skripte (`shoot.py`, `verify.py`,
kein Repo-Code), `PrintWindow` auf das eigene HWND (NH-002). Alle zwoelf
Bilder mit dem Read-Tool angesehen. Registry-Rest (`HKCU:\Software\
DankYeeterT-263`) danach geloescht.

## Ergebnis

**DR-028 geschlossen, Messartefakt bestaetigt.** Waechter
`tests/test_stat_sheet_at_the_window.py` laeuft gruen (3 passed) und deckt
1608/1536/1366 px ab. Live am Fenster bei 1536 px: Werteblatt vollstaendig
lesbar, „Physical 56 / 58 2H — 56 / 58 2H" unabgeschnitten, eigene
Bildlaufleiste fuer den Rest — deckt sich mit T-259s 348-px-in-356-Beleg.
Screenshot `design-review/2026-09-15/t263-buildplanner-1536.png`.

**DR-029 live retestet, behoben.** Suchfilter „Finger Seal" auf Weapons &
spells: „Weapons (1)"/„Sacred Seal (1)" bei genau einer Kachel. Screenshot
`t263-weapons-fingerseal-retest.png`.

**DR-030 gegenstandslos** (AN-8, Director) — nur vermerkt, kein Code
betroffen.

**AK-292** (Schalter „1H"/„2H"): bei 1536 px sichtbar und lesbar, eine
Instanz. **AK-286** (Kachelformat `{1H} / {2H} 2H`): auf dem Weapons-Tab bei
1536 px ueber ein volles Rasterblatt gepruedft, kein Umbruch. **AK-296**
(Gefaess-Tooltip): programmatisch aus `chalice_list` gelesen (ein
`QToolTip` ist ein eigenes Fenster, `PrintWindow` faengt es nicht),
Wortlaut deckungsgleich mit der Spec, Em-Dash korrekt (U+2014).

**AK-294/AK-295 nicht live ausgeloest** — beide brauchen einen
praeparierten Build (unerfuellbare Pflicht bzw. ein Feld mit
`conditionHp`/unbenanntem Schluessel), den dieser Lauf nicht aufgesetzt
hat. Code gelesen und deckungsgleich mit der Spec
(`advisorbar.py:176/184/185`, `effecttext.py:27/28/130/131`,
`model.py:1212/1213`); `qa-engineer`s T-263a deckt QA-269/270 auf
Datenebene ab. Als Luecke im Backlog vermerkt, kein Blocker.

Alle sieben Tabs bei 1536 px, alle vier Content-Tabs zusaetzlich bei
1608 px: keine abgeschnittenen Spalten, keine ueberlappenden Elemente.

## Neuer Fund

**DR-031, Nice-to-have** — Nightlords-Tab, rechte Detailflaeche ohne
Auswahl bleibt bei beiden Breiten zu rund 60 % leer (Platzhalter „Select a
Nightlord" auf sonst leerer Flaeche). Kein Fehler, Geschmacksfrage
(vorausgewaehlter erster Nightlord vs. knapperer Text) — kein Ruecklauf an
den App Designer noetig, im Backlog.

**Dateien:** `DESIGN_REVIEW.md`, zwoelf Screenshots unter
`design-review/2026-09-15/t263-*.png`.
