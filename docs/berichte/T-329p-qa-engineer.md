# T-329p — Retest am Quellstand (qa-engineer)

**STATUS: teilweise.** Werkzeug-Zugschwelle (150 Aufrufe) erreicht, bevor
Pruefpunkt 4 vollstaendig und die zwei offenen Teilpunkte aus Pruefpunkt 1
abgeschlossen waren. Kein Gesamturteil (PASS/CONCERNS/FAIL) — siehe "Offener
naechster Schritt" unten. Alle bisherigen Befunde sind reproduziert, nicht
vermutet.

Stand: `03ef40f` (n `1494474`, o `23922d2..3a06a8b`, gemerged), Branch
`docs/audit-and-advisor-design`. Kein Code geaendert; einzige Schreibzugriffe
waren dieser Bericht und das eigene Scratchpad `.../scratchpad/T-329p/`.

## Aufbau

`python run.py` mit `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-329p`, `LOCALAPPDATA`
und `APPDATA` auf `scratchpad/T-329p/local` bzw. `/roaming` umgelenkt (eine
Kommandozeile, Hook-konform). Testabzug (841 Dateien, `EXTRACT_VERSION` 16)
nach `local/NightreignHelper/` kopiert. Fuer AK-366 eine **Kopie** des echten,
schreibgeschuetzt gelesenen Saves nach `roaming/Nightreign/<id>/NR0000.sl2`
gelegt; die Fallback-Suche (`Path.home()/AppData/Roaming/Nightreign`, QA-255)
findet zusaetzlich das Original — beide Dateien sind identisch, das ergibt
absichtlich den Gleichstand-Fall. `scripts/drive_window.ps1` dot-gesourct wie
in T-329k, PID ueber `MainWindowTitle -like 'Nightreign Helper*'` ermittelt
(bei offenem Dropdown zeitweise `'python'` — dann PID fest verdrahtet statt
neu gesucht). Vergleichsbilder aus T-329k (`shots_cur2/`) als Rot-vorher-Basis
fuer den Pixelvergleich.

## Bestehende Tests

`pytest tests/test_hostile_gamedata.py tests/test_save_path_memory.py
tests/test_release_spec_datas.py tests/test_picker_track_guards.py -q`:
**104 passed, 80 s** — keine Regression in den vier direkt von n/o
beruehrten Dateien. Volle Suite nicht erneut gelaufen (Direktor hat sie am
Merge bereits mit 1916 passed/9 skipped/179 s gemessen; Retest-Modus verlangt
kein allgemeines Neutesten ohne Hinweis auf breitere Auswirkung).

## Pruefpunkt 1 — AK-368/369/371 sichtbar (Beleg PrintWindow-Pixelprobe)

**AK-368 (Events-Tab Community-Blau = Rot-Varianten-Blau `#7fb2e5`): PASS.**
Pixelvergleich World-Events-Tab gegen T-329k `shots_cur2/6_a.png`: 13 387 px
Differenz, davon 804 exakt `6f9ac4→7fb2e5` (alter eventstab-Wert → neuer
`theme.COMMUNITY`); die uebrigen Pixel sind Nachbar-Antialiasing derselben
Stelle. Keine andere Aenderung auf diesem Tab.

**AK-369 Effects-Tab „Stacks"-Spalte (kein `#ff0000` mehr): PASS.** Ueber den
Stacking-Filter „Exclusive group (no number)" isoliert: Screenshot zeigt die
Spalte durchgehend in `#e07a74` (2704 Treffer exakt), **0** Treffer fuer
reines Rot `#ff0000`. Visuell per Crop bestaetigt (Zeilen wie „[Duchess]
Improved Mind and Faith..." in Rot-Orange statt Signalrot).

**AK-369 Relikt-Slot, gewuerfelter Fluch (`relicslots.py:429`): nicht
unabhaengig pixelbelegt.** Code bestaetigt (`git diff 7903b0c..HEAD --
nrplanner/relicslots.py`: Literal `"#d1655f"` → `DEBUFF` exakt an der von
AK-369 genannten Zeile). Live liess sich in der verfuegbaren Zeit kein
Reliktslot mit einem tatsaechlich **gewuerfelten** Fluch-Effekt herstellen
(Deep of Night aktiviert, Optimize + Apply all fuellte Slots mit Relikten,
die nur *potenzielle* Flueche tragen — die rendern korrekt unveraendert in
`theme.CURSE`/`BAD` `#d1655f`, 637 Treffer bestaetigt, das ist die bewusst
unveraenderte Stelle). Da `DEBUFF` an anderer Stelle bereits bitgenau als
`#e07a74` bestaetigt ist (derselbe Python-Konstantenwert, keine ortsabhaengige
Faerbung in Qt), ist das Restrisiko klein, aber nicht durch eigene Beobachtung
geschlossen.

**AK-371 MUTED-Grau (`#888`→`#8a8a8a`, `relicslots.py:554`,
`relicpicker.py:1115`, `app.py:161`): nicht pixelbelegt.** Code bestaetigt;
alle drei Stellen sind der Fallback-Zweig `SLOT_COLOURS.get(colour, MUTED)`
fuer eine unbekannte Reliktfarbe — mit echten Spieldaten offenbar nie
erreicht (deckt sich mit T-329k „0 Pixel Unterschied" fuer denselben
Refaktor-Typ in T-329h).

**Uebrige Reiter:** Nightlords, Deep of Night, Red variants — identisch zur
T-329k-Basis (0 px). Build planner, Effects & chances, Weapons & spells
zeigten Differenzen, alle auf eigene Testumgebung zurueckgefuehrt, keine
Regression:
- Effects & chances / Weapons & spells: Fokusring (oranger Rahmen) auf dem
  Suchfeld, in der T-329k-Aufnahme nicht vorhanden — UI-Fokuszustand, keine
  Farbrolle.
- Build planner: Listenscroll/-layout verschoben, weil durch den
  selbst angelegten zweiten Save der AK-366-Halbsatz und der Knopf
  „Find my save..." zusaetzlich Platz brauchen (siehe Screenshot-Vergleich
  `crop_old_bp.png`/`crop_new_bp.png`) — Wirkung des eigenen Testaufbaus,
  nicht des Codes.

## Pruefpunkt 2 — QA-004-Rest: PASS

„Load equipped" mit gespeichertem Build und zwei lesbaren Saves (Gleichstand)
traegt den Halbsatz; woertlicher Text (UTF-8 geprueft, `—` ist U+2014,
korrekter Em-Dash):

> „Loaded Wylder — 5 chalices. The equipped Soot-Covered Wylder's Urn is
> empty in game; the others are in the list on the left. — 1 other save was
> found; this is the most recent of those with the most relics"

Mit nur einem Save (vor dem Kopieren) kein Halbsatz — bestaetigt.

**Offene Frage an `ui-ux-designer` (T-329o-Frage woertlich beantwortet):**
lesbar? **Eher nein.** Jeder `load_equipped`-Zweig endet seinen eigenen Satz
mit einem Punkt; `other_saves_clause` haengt danach unbedingt
`" — ..."` an, sodass an der Naht immer „. —" steht (Punkt, Leerzeichen,
Em-Dash, Leerzeichen). AK-366 selbst schreibt nur „kein Punkt am Ende" vor
(fuer das Ende der Klausel) und trifft keine Aussage ueber das, was ihr
vorausgeht. Fuer die urspruengliche Notizzeile (`"{relic_count} relics in
{source}"`, kein Punkt davor) ist die gleiche Klausel unauffaellig; nur an
der `load_equipped`-Notiz, die immer schon einen Punkt hat, entsteht der
Doppel-Interpunktions-Eindruck. Das ist eine Spezifikationsluecke (A12), kein
klarer AK-Verstoss — daher Frage statt Befund.

## Pruefpunkt 3 — Kaputter Snapshot: PASS (soweit hier pruefbar)

Code: `nrplanner/datasource.py:82-90` `_snapshot()` faengt `(OSError,
ValueError)` und liefert `None`; `_load_data()`/`main()` (`app.py:3211ff`)
hatten bereits ein breites `except Exception` mit `QMessageBox.critical` —
kein unbehandelter Absturz auch vorher schon, der Unterschied ist die
Behandlung als „kein Snapshot" statt als technischer JSON-Fehler.
Bestaetigt durch den bestehenden, gruenen Test
`tests/test_hostile_gamedata.py::test_a_damaged_snapshot_counts_as_no_snapshot`
(Datei bleibt unangetastet, `_snapshot()` liefert `None`).

**Live bestaetigt:** umgelenkten Cache durch ungueltiges JSON ersetzt (echtes
Spiel auf dieser Maschine weiterhin vorhanden/auffindbar) — Programm startet
sauber, kein Fehlerdialog, extrahiert im Hintergrund neu (`nightreign_data.json`
danach 8,8 MB statt der kaputten Kurzdatei).

**Nicht live reproduziert:** „Spielpfad unauffindbar" zusaetzlich zum
kaputten Cache. `gamepath.resolve_game()` faellt auf `gamefiles.find_game_dir()`
zurueck, das ueber die echte Steam-Registry/`libraryfolders.vdf` sucht — auf
dieser Maschine ist das echte Spiel wirklich installiert und wuerde gefunden,
unabhaengig von der Sandbox-Umlenkung. Das echte Spiel zu verstecken waere
ein Eingriff in echte Nutzerdaten/-installation (verboten). Fuer den
„Spiel wirklich nicht gefunden"-Zweig stuetze ich mich auf den bestehenden
gruenen Unit-Test und die Codelesung des `NoGameData`-Pfads in `main()`.

## Pruefpunkt 4 — Kriteriumsfrage: unvollstaendig

Neue/veraenderte Tests seit `e9bc8a0` (vor Runde 1) in `tests/`: 20 Dateien
mit echten Ergaenzungen, davon geprueft (drei):

- `tests/test_advisor_run.py::test_a_chosen_kind_nothing_owned_reaches_says_so`
  / `_alone_keeps_its_label` / `_something_owned_reaches_says_nothing_of_it`:
  **prueft das Kriterium** — echte Recluse/Sorceries/Fire-Spieldaten, prueft
  den woertlichen AK-365-Satz gegen `result.no_carrier_for`/`unknowns`, nicht
  nur, dass irgendein Code-Pfad laeuft.
- `tests/test_advisor_bar.py` (zwei neue `TABLE`-Zeilen „4.11 no carrier"):
  **prueft das Kriterium** — der komplette erwartete Statuszeilen-Satz steht
  woertlich im Test, Ende-zu-Ende von `Situation` bis String.
  Fehlermeldung fuer sofortige Diagnose bei Fehlschlag.
- `tests/test_hostile_gamedata.py::test_a_damaged_snapshot_counts_as_no_snapshot`:
  **prueft das Kriterium** — die Director-Entscheidung „gilt wie eine
  fehlende" woertlich (Datei bleibt liegen, `None` statt Ausnahme).

**Nicht mehr geprueft (Zugschwelle):** `tests/test_save_path_memory.py`
(AK-366, neue Datei, 129 Zeilen), `tests/test_relic_ownership.py` (AD-055),
`tests/test_extraction.py` (atomarer Cache-Schreiber), `tests/test_icon_pack_paths.py`
(Symbolcache), `tests/test_picker_track_guards.py` (Spin-Frist-Selbstpruefung,
T-329o Punkt 5), `tests/test_release_spec_datas.py`, sowie alle Dateien, die
nur durch den T-329j-Dedup-Refaktor beruehrt sind (vermutlich keine neuen
Kriteriumsaussagen, aber ungeprueft).

## Offener naechster Schritt (fuer die Fortsetzung durch den `director`)

1. Pruefpunkt 1: AK-369 (gewuerfelter Fluch im Reliktslot) und AK-371
   (MUTED-Fallback) live pixelbelegen — braucht ein Deep-of-Night-Relikt mit
   tatsaechlich gewuerfeltem Fluch-Effekt bzw. einen erreichbaren
   „unbekannte Farbe"-Zustand; ggf. per gezieltem Testrelikt/-fixture statt
   Optimize/Apply all.
2. Pruefpunkt 4: die sechs oben genannten Testdateien durchsehen, je Test ein
   Satz Kriterium-ja/nein.
3. Danach erst das Gesamturteil (PASS/CONCERNS/FAIL) fuer T-329p bilden —
   bisher spricht nichts Gefundenes fuer FAIL, aber das Urteil ist erst nach
   1./2. belegt.
4. Aufraeumen: der in diesem Lauf gestartete Prozess (`python run.py`,
   umgelenkter Org `DankYeeterT-329p`) laeuft unter Umstaenden noch;
   `scratchpad/T-329p/` kann geloescht werden.

## QA-Log (Zeilen fuer `qa/findings.md`, an die bestehende Tabelle anhaengen)

Keine neuen QA-IDs vergeben — die einzige Beobachtung mit moeglichem
Befund-Charakter (". —"-Naht bei QA-004-Rest) ist als offene Frage an
`ui-ux-designer` dokumentiert, nicht als Befund, da AK-366 dazu keine
Aussage trifft. Register unveraendert gegenueber dem letzten Stand.
