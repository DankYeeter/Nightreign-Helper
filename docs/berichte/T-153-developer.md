STATUS: erledigt
AUFTRAG: T-153 - Der Spieler erfaehrt den Rueckfall, und der Dialog startet am richtigen Ort (developer)
GELESEN: docs/tasks/T-153.md; UI_SPEC.md AK-228/AK-229 (§9 (d)) und AK-110 bis AK-115, §4.1-4.3;
  GOAL.md A7 und A15 (woertlich, aus dem Auftrag zitiert); docs/berichte/T-149-developer.md
  (Abschnitt 5, "Der Startort des Dialogs ist unvollstaendig"); docs/berichte/T-151-developer.md
  war nicht direkt lesbar unter diesem Namen, sein Wortlaut stand aber vollstaendig im Auftrag
  zitiert; nrplanner/app.py, nrplanner/inventory.py (nur gelesen), nrplanner/firstrun.py,
  nrdata/gamefiles.py, tests/test_save_read_in_the_background.py, tests/test_relic_scan_prefilter.py,
  tests/test_game_dir_recognition.py, tests/test_game_path_memory.py, tests/test_first_run_panel.py
GEÄNDERT: nrplanner/app.py; tests/test_save_read_in_the_background.py; nrdata/gamefiles.py;
  nrplanner/firstrun.py; tests/test_steam_library_start_folder.py (neu). Committet in zwei
  Schritten: 17b2cb9 (Teil 1, A7), bd0093f (Teil 2, AK-110).
ANNAHMEN: siehe unten, Punkt "Abweichung von der Dateiliste" (firstrun.py angefasst, obwohl
  nicht in "Beruehrt Dateien" genannt) - das ist die einzige Annahme, alles andere war im
  Auftrag oder in UI_SPEC.md woertlich festgelegt.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Teil 1 - A7: der Rueckfall wird gesagt

`_on_save_read` in `nrplanner/app.py` haengt jetzt, wenn `Inventory.read_the_slow_way`
gesetzt ist, den Text aus UI_SPEC §9 (d) (AK-228) woertlich an die Bestandszeile an - nach dem
bestehenden `stored builds`/`loadout_error`/`no builds`-Zweig, so wie es das Beispiel in §9
zeigt ("309 relics in <slot name>, 110 stored builds — read the slow way: ..."). Neue Konstante
`READ_THE_SLOW_WAY_NOTE`, Byte-fuer-Byte gegen `UI_SPEC.md` Zeile 7603 geprueft (Python-Vergleich
der beiden Strings, nicht durch Augenschein).

Der Zusatz steht **nur** im Erfolgspfad, nach `self.owned is not None` - AK-229 ("kein
`Save could not be read: ` davor") ist damit strukturell erfuellt, nicht nur durch einen Test
behauptet: der Code-Pfad, der `UNREADABLE_SAVE` schreibt (`_on_save_failed`), sieht
`read_the_slow_way` nie.

**Voller Mutationsbeweis**, vier Mutationen, alle toetend (einzeln angewandt, Testlauf
`pytest tests/test_save_read_in_the_background.py -k test_the_slow_way_note_is_said_and_never_a_failure`,
danach zurueckgesetzt und der Diff gegen die Sicherungskopie der Datei auf Gleichheit geprueft):

1. Bedingung entfernt (`if True:` statt `if self.owned.read_the_slow_way:`) - rot.
2. Anhaengen ganz entfernt - rot.
3. Text der Konstante veraendert (`fixing!` statt `fixing.`) - rot.
4. Reihenfolge vertauscht (Zusatz vor statt nach dem builds-Zweig) - rot.

Bei Mutation 3 mit der ersten Testfassung (die den Vergleichstext aus `appmod.READ_THE_SLOW_WAY_NOTE`
selbst zusammensetzte) **ueberlebte** die Mutation - der Test hatte sich an der bewachten Konstante
gemessen, nicht an der Spec (L-008). Behoben: `THE_SLOW_WAY_NOTE` steht jetzt als eigene, von
`app.py` unabhaengige Literale im Testmodul, zweite Quelle fuer denselben Wortlaut, genau wie
`THE_WORDING_AD_031_TOOK_OFF_THE_PATH` es im selben Testfile schon vormacht.

Test: `test_the_slow_way_note_is_said_and_never_a_failure` in
`tests/test_save_read_in_the_background.py`. Treibt den echten Weg (`StatedRead` durch
`Planner`, kein Aufruf einer internen Methode von aussen); `inventory.build` ist gepatcht,
damit `StatedRead` das fertige `Inventory` unveraendert durchreicht (`build` selbst gehoert zu
`nrplanner/inventory.py`, das ich nicht anfassen durfte und auch nicht musste). `hero_id=-1`
im mitgegebenen `EquippedLoadout` verhindert, dass `reload_chalices` die automatische
Uebernahme (AK-224) ausloest und die Zeile ueberschreibt, bevor der Test sie liest.

## Teil 2 - AK-110: der Startort des Dialogs

`nrdata/gamefiles.py` bekommt `steam_common_folders()`: liest `_steam_roots()` und
`_library_paths()` (beide unveraendert, keine Duplikation) und gibt eine Liste aller
`common`-Ordner jeder gefundenen Bibliothek zurueck, naechster Root zuerst, Existenz ungeprueft
- wie `find_game_dir()` es mit denselben zwei Helfern schon haelt.

`nrplanner/firstrun.py`, `where_to_start_looking()`: befragt diese Liste jetzt vor dem
hartcodierten `STEAM_COMMON`, das nur noch greift, wenn Steam selbst nicht gefunden wird (Reihenfolge
aus §4.1: gemerkter Pfad, dessen Elternordner, Steams Bibliothekliste, `C:\Program Files (x86)\
Steam\steamapps\common`, "Dieser PC"). Der Kommentar an `STEAM_COMMON`, der bislang erklaerte,
warum die Bibliothekliste fehlt, ist entsprechend umgeschrieben.

**Kein Mutationsbeweis fuer Teil 2** - Nutzerentscheidung laut Auftrag, weil ein falscher
Startort beim manuellen Durchspielen von AK-110 sofort auffaellt (der Dialog oeffnet sichtbar am
falschen Ort). Stattdessen vier funktionale Tests in `tests/test_steam_library_start_folder.py`:
Standardbibliothek ohne vdf, mehrere Bibliotheken in vdf-Reihenfolge, ein verschwundener
Registry-Eintrag (leere Liste), und ein Ende-zu-Ende-Fall gegen `where_to_start_looking` selbst.
Die vdf-Parsing-Logik (`_library_paths`) laeuft dabei echt, gegen eine selbst geschriebene
`libraryfolders.vdf` in `tmp_path` - nicht gegen echte Steam-Registry-Daten.

### Abweichung von der Dateiliste

Der Auftrag nennt `nrplanner/app.py, nrdata/gamefiles.py, tests/` als beruehrte Dateien. Die
tatsaechliche Verdrahtung von AK-110 sitzt in `nrplanner/firstrun.py`
(`where_to_start_looking`, `STEAM_COMMON`) - `app.py` ruft nur `firstrun.run(...)` auf und hat
auf den Startort des Dialogs keinen Zugriff. T-149s eigener Bericht (Abschnitt 5) nennt
`firstrun.py` als den Ort, an dem "zwei Zeilen" fehlen. `firstrun.py` steht **nicht** auf der
"Nicht anfassen"-Liste des Auftrags (die nennt `inventory.py`, `savefile.py`, `gamepath.py` und
die Doku-Dateien), anders als bei den drei tatsaechlich verbotenen Quelldateien.

Ich habe `firstrun.py` trotzdem angefasst, mit dieser Abwaegung: die Beruehrt-Dateien-Liste
scheint mir eine unvollstaendige Angabe zu sein (vermutlich aus den Zitaten von T-149 und T-151
zusammengesetzt, ohne selbst zu pruefen, wo der Code fuer AK-110 tatsaechlich sitzt), waehrend
die "Nicht anfassen"-Liste die tatsaechliche Sperre ist und `firstrun.py` dort fehlt. Ohne diese
Aenderung waere "Gib den Kandidaten ... einen oeffentlichen Namen und benutz ihn" nur zur Haelfte
erfuellt gewesen - der Name stuende da, ohne dass ihn irgendetwas ruft, was den in CLAUDE.md
verbotenen toten Code erzeugt haette. Der Director sollte das fuer kuenftige Auftraege pruefen:
entweder die Beruehrt-Dateien-Liste wird strenger als Whitelist gelesen (dann waere hier Teil 2
nur zur Haelfte lieferbar gewesen und ich haette stoppen und `firstrun.py` als fehlenden
Scope melden muessen), oder sie ist wie hier behandelt eine unvollstaendige Angabe neben der
massgeblichen "Nicht anfassen"-Liste.

## Tests

- `pytest tests/test_save_read_in_the_background.py -q` - 23 passed (davon 1 neu).
- `pytest tests/test_steam_library_start_folder.py -q` - 4 passed (alle neu).
- `pytest tests/test_game_path_memory.py tests/test_game_dir_recognition.py tests/test_first_run_panel.py -q`
  - 130 passed (Regression um `find_game_dir`, die Erkennungsstufen und den bestehenden
  `where_to_start_looking`-Test, der `firstrun.STEAM_COMMON` als moegliches Ergebnis weiter
  zulaesst - auf dieser Maschine unveraendert gruen, weil die erste vorhandene Bibliothek dieser
  Maschine pfadgleich mit `STEAM_COMMON` ist).
- Volle Suite: `pytest -n auto -q` → **1595 passed, 9 skipped, 0 failed** (Referenz aus dem
  Auftrag: 1590 passed, 9 skipped, 0 failed; Differenz +5 = meine fuenf neuen Testfaelle).

Bewusst nicht abgedeckt: `_pick_a_folder`s echter `QFileDialog` (existiert seit T-149 in keinem
Test - der Systemdialog wird nie geoeffnet, das ist eine bestehende Luecke, keine neue), und ein
Lauf gegen eine echte Steam-Installation (die vier neuen Tests bauen ihre eigene
`libraryfolders.vdf`, keine echte gelesen).

## Datenverzeichnisse - Nachweis

Scratchpad: `…/scratchpad/T-153/`. Alle drei Variablen umgelenkt und geprueft, bevor irgendein
Test lief:

- `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-153` (zusaetzlich zu `conftest.py`s eigener,
  bereits isolierter Umlenkung auf `DankYeeterTests`/`NightreignHelperTests-<pid>`, die bei
  jedem Testlauf greift).
- `LOCALAPPDATA` auf `…/scratchpad/T-153/localappdata` gesetzt und mit
  `nrplanner.paths.cache_dir()` bestaetigt: `…\scratchpad\T-153\localappdata\NightreignHelper`.
  Der feste Testabzug (`C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug`, 22 MB) wurde
  dorthin **kopiert**, nicht referenziert.
- `APPDATA` auf `…/scratchpad/T-153/appdata` gesetzt und mit
  `nrplanner.shortcut.start_menu_dir()` bestaetigt: `…\scratchpad\T-153\appdata\Microsoft\Windows\
  Start Menu\Programs`. Genutzt wird dieser Pfad unter Testbedingungen ohnehin nie:
  `shortcut.available()` verlangt `sys.frozen`, das unter `pytest` nie gesetzt ist - die
  Umlenkung ist damit nachweislich wirkungslos-sicher, nicht bloss vermutet.

Spielstand: nirgends geschrieben, nur `inventory.build`-Mocks und handgebaute `Inventory`-Objekte
verwendet; wo echte Spieldaten liefen (`game_data`-Fixture), read-only wie ueberall im Projekt.

## Fund: fremde, uncommittete Aenderungen im geteilten Arbeitsbaum

Waehrend dieses Laufs sind in `scripts/` fuenf Dateien als geaendert aufgetaucht, die ich nicht
angefasst habe: `scripts/capture_weapon_damage.py`, `scripts/differential/capture.py`,
`scripts/make_screenshots.py`, `scripts/measure_advisor_block.py`, `scripts/measure_picker_cards.py`.
Sie sind weiterhin unstaged und uncommittet - ich habe beide Commits ausschliesslich mit
`git commit -- <meine Dateien>` gemacht, nie mit `-a` oder `add -A`. Vermutlich derselbe geteilte
Arbeitsbaum, den `docs/berichte` unter "Parallel runs" schon einmal als Ursache genannt hat
(ein anderer Lauf schreibt in denselben Checkout). Nichts davon wurde von mir committet oder
verworfen; der Director sollte pruefen, wessen Arbeit das ist, bevor sie verloren geht.

## An qa-engineer

- AK-228/A7: ein Spielstand mit einer Relikt-Id oberhalb `savefile.RELIC_ID_CEILING` (auf einem
  aktuellen Spielstand vermutlich nicht reproduzierbar, da das ein zukuenftiges Spiel-Update
  voraussetzt) sollte die Bestandszeile mit " — read the slow way: ..." enden lassen, niemals
  mit "Save could not be read: " davor.
- AK-110: der `Choose folder...`-Dialog sollte auf einer Maschine mit mehreren Steam-Bibliotheken
  (z. B. eine zweite auf einem anderen Laufwerk) in der **naechstgelegenen** Bibliothek starten,
  nicht zwingend im Standardpfad. Das laesst sich nur mit echtem gebautem Artefakt und echtem
  Fenster pruefen (Punkt aus T-149s Bericht weiterhin offen: kein Bildnachweis, kein echtes
  Fenster in diesem Lauf).

## An director

- Die Abweichung von der Beruehrt-Dateien-Liste (`firstrun.py`) oben bitte pruefen und, falls
  die Liste als Whitelist gemeint war, fuer kuenftige Auftraege praeziser fassen.
- Fund zu den fremden `scripts/`-Aenderungen oben - unklare Herkunft, nicht von mir.
- `docs/state.md` nennt A15 weiterhin mit "null Zeilen gebaut" (laut Zitat im Auftrag, Stand vor
  T-149 bis T-153) - das ist jetzt veraltet; A7s Bestandszeile und AK-110s Bibliothekliste sind
  ab diesem Lauf gebaut. Aktualisierung liegt beim Director, nicht bei mir (`docs/state.md` ist
  eine fremde Datei).
