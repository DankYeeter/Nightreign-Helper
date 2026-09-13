# T-228 — Developer-Bericht (13.09.2026)

```
STATUS: erledigt
AUFTRAG: docs/tasks/T-228.md — Ponytail-Audit Beta-Gate: 15 Loeschungen toten Codes, bedingt PressableFrame -> QAbstractButton
GELESEN: docs/tasks/T-228.md (ganz); CLAUDE.md; _rahmen.md Z. 23-100; nrplanner/pressable.py (ganz), bosstab.py Z. 295-440; tests/test_card_is_pressable.py Z. 40-260; tests/test_exception_text_is_english.py Z. 500-545; nrplanner/datasource.py Z. 120-175; nrdata/param.py Z. 69-102; die Fundstellen der Funde 1-12 je mit Umgebung
GEÄNDERT: nrplanner/app.py, stacking.py, firstrun.py, uiscale.py, search.py, effecttext.py, deeptab.py, arsenaltab.py, effectstab.py, bosstab.py, relicpicker.py, datasource.py, advisor/__init__.py, advisor/worker.py; nrdata/bhd5.py, binary.py, bnd4.py, extract.py, gamefiles.py, tae.py; tests/test_exception_text_is_english.py; docs/berichte/T-228-developer.md (neu). Commits 3ee6f7d, 142788b, 101022f auf worktree-agent-a2f7c1c1a1712abdc (enthaelt 550efc5), kein Push. Arbeitsbaum sauber.
ANNAHMEN: (1) "pyflakes leer" gilt fuer die ganze Ausgabe, nicht nur die fuenf im Auftrag genannten Zeilen — vier f-Strings ohne Platzhalter und `bnd4.py:156 extended` mit beseitigt (Befund 1). (2) Zum Kommentar einer geloeschten Konstante gehoert der Kommentar (NPC_NAME_PREFIX, DEEP_LABEL_ID: Halbsatz gekuerzt).
NÄCHSTER: director (Befund 2: Testumbau anders als im Auftrag; Befund 3: Fund 16 nicht gebaut; Befund 4: ein Test faellt unter -n auto)
BLOCKIERT DURCH: nichts
```

## Funde

| Fund | Ergebnis | Grep-Beleg (nrplanner nrdata scripts tests, *.py) |
|---|---|---|
| 1 VariantDialog | geloescht, 71 Z. | 1 Treffer (Definition) |
| 2 VesselStrip._backing/SPRITE/_tinted | geloescht | 6 Treffer, alle in der Definition; `PORTRAIT_SPRITE`/`ITEM_SPRITE` in icons.py sind andere Namen |
| 3 RelicSlot._chance_suffix | geloescht | 1 |
| 4 stacking.tier_note | geloescht | 1 |
| 5 firstrun.ensure_data | geloescht; worker.py:7 nennt jetzt `_build_what_is_missing`, wo die Warteschleife (Z. 1017) wirklich steht | 2 (Definition, Docstring) |
| 6 uiscale.label_for | geloescht | alle uebrigen Treffer sind `model.label_for` |
| 7 tae.Event.to_end + _FLT_MAX | geloescht | 3, alle Definition; `move_to_end` in run.py ist OrderedDict |
| 8 Reader.i8/i16 | geloescht | 2 (Definitionen) |
| 9 search.matches | geloescht | 1 |
| 10 effecttext.is_described | geloescht | 1 |
| 11 sieben Konstanten | geloescht mit Kommentaren | je 1; `CUSTOM_RELIC_ID` (inventory) ist ein anderer Name |
| 12 pyflakes | leer nach dem Lauf; `_pc_row = param.read(player_common, None)`: ohne pdef kein raise, kein Zustand — weg | — |
| 13 advisor/__init__ Re-Exporte | geloescht, 31 Z. | 0 Aufrufer der Paketattribute; `advisor.RED` usw. in Tests ist `tests.advisor_cases as advisor` |
| 14 prefer_live | Parameter und beide Tore weg | 2 Aufrufer, beide Tests |
| 16 PressableFrame -> QAbstractButton | **nicht gebaut** | siehe Befund 3 |

Audit-Irrtuemer im Sinn "Grep zeigt einen Aufrufer": keine.

## Befunde

**1. pyflakes zeigte 10 Zeilen, der Auftrag nannte 5.** Die fuenf weiteren
(`app.py:3865/3970`, `bosstab.py:861`, `relicpicker.py:654` f-String ohne
Platzhalter; `bnd4.py:156` `extended` zugewiesen, nie gelesen) sind ohne
Verhaltensaenderung beseitigt (f-Praefix weg; `r.u8()  # extended` wie die
Nachbarzeilen), weil "danach muss pyflakes leer sein" sonst nicht haelt.

**2. Testumbau Fund 14 anders als vorgegeben.** Der Auftrag sagt
"`_regulation_matches` monkeypatchen". Der erste Test setzt `_snapshot` auf
`None`; damit wird `_regulation_matches` nie erreicht, und ohne das
`prefer_live`-Tor liefe die Live-Extraktion (`gamepath.resolve_game` findet
auf dieser Maschine das Spiel). Stattdessen `gamepath.resolve_game -> None`;
der zweite Test braucht nichts, `_snapshot` wirft vor jedem Tor.

**3. Fund 16 nicht gebaut — die Bedingung haelt nicht.** Sonde
`scratchpad/T-228/qabstractbutton_probe.py` (PySide6, offscreen) an einem
nackten `QAbstractButton` mit `setAccessibleName`:

- `keyBindingsForAction(Press)` liefert `['']` (Qt nennt den Button-Shortcut,
  es gibt keinen). `test_every_key_the_card_announces_really_presses_it`
  fiele ("announces '' which is not a key"). `QAccessibleButton` ist in PySide6
  nicht exportiert (`hasattr(QtWidgets, "QAccessibleButton") == False`), also
  auch nicht als Basis fuer `CardAccessible` nutzbar — die Klasse bliebe ganz.
- Space loest `clicked` erst beim KeyRelease aus; Return/Enter gar nicht.
  Die Tests senden nur KeyPress — `keyPressEvent` bliebe ganz.
- Accessible Press geht ueber `animateClick()`: `clicked` erst nach ~100 ms.
- Maus: `QAbstractButton` klickt beim Loslassen, `BossCard` drueckt beim
  Druecken — Verhaltensaenderung, also `mousePressEvent` bleibt.
- `paintEvent` ist auf `QAbstractButton` rein virtuell: der Stylesheet-Kasten
  (`#card`, 7 px Radius) muesste per `PE_Widget` von Hand gezeichnet werden —
  neuer Code, Pixel-/Geometriegleichheit fuer QA-150/154 ungeprueft.
- `BossCard.clicked = Signal(dict)` kollidiert mit `QAbstractButton.clicked(bool)`.

Was bliebe: `setFocusPolicy(StrongFocus)` faellt weg (Qt-Vorgabe unter
Fusion ist 11 = StrongFocus). Eine Zeile gegen sechs neue Stellen. Empfehlung:
Fund als `native` schliessen, nicht bauen.

**4. Ein Test faellt unter `-n auto`, seriell gruen.**
`tests/test_save_read_in_the_background.py::test_the_waiting_state_is_a_state_and_not_a_nothing`
— 1 failed, 1518 passed, 9 skipped in 74 s. Dieselbe Datei seriell danach:
26 passed in 36 s. Der Test liest den Wartezustand eines Hintergrund-Reads
innerhalb `READ_FUSE_S`; keine geloeschte Stelle liegt auf dem Save-Read-Pfad.
Fehlertext nicht erfasst (nur die Summenzeile). Kein zweiter Suitelauf, weil
kein Fix vorlag (Regel: zweiter Lauf nur nach Fix). Verdacht Race unter Last;
qa-engineer kann es mit einem eigenen `-n auto`-Lauf bestaetigen oder
entkraeften.

## Zahlen

- `git diff --numstat 437998b..HEAD`: 21 Dateien, +32 / -271, **net -239 Zeilen**.
- `python -m pyflakes nrplanner nrdata`: leer.
- Gezielt vor dem Commit: 7 Testdateien, 88 passed in 45,7 s.
- Ponytail-Durchgang des eigenen Diffs (delete/stdlib/native/yagni/shrink):
  nur Loeschungen, nichts zu streichen.
- Datenumlenkung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-228`, `LOCALAPPDATA`/
  `APPDATA` im Scratchpad, Testabzug kopiert (841 Dateien), nach dem Lauf
  entfernt; Sonde bleibt im Scratchpad.
