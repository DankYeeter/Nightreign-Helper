STATUS: teilweise
AUFTRAG: T-218 — Vier Flaechenbefunde: QA-210, QA-232, SEC-039, QA-242 (erster Anlauf)
GELESEN: docs/tasks/T-218.md; CLAUDE.md; ~/.claude/agents/_rahmen.md;
  qa/findings.md:254,265; security/findings.md:57;
  docs/berichte/T-124-ui-ux-designer.md:150-170; T-193-developer.md:240-262;
  T-207-ui-ux-designer.md:30-80; UI_SPEC.md AK-49, AK-51, AK-196, AK-212,
  AK-216, 4.8; nrplanner/relicpicker.py, advisorbar.py, app.py (Slot-Bestand,
  _on_save_read, _on_save_failed, _hand_the_stock_to_the_slots), shortcut.py,
  errortext.py, firstrun.py:596-636; nrdata/binary.py und die acht Dateien
  aus b; scripts/measure_picker_cards.py; tests/test_relic_picker_advisor.py,
  test_exception_text_is_english.py, test_relic_picker_geometry.py,
  test_save_read_in_the_background.py
GEÄNDERT: nrplanner/relicpicker.py, nrplanner/shortcut.py, nrdata/bnd4.py,
  dds.py, dvdbnd.py, extract.py, fmg.py, oodle.py, param.py, paramdef.py,
  tests/test_relic_picker_advisor.py, tests/test_exception_text_is_english.py,
  docs/berichte/T-218-developer.md
ANNAHMEN: Schritt 0 — der Worktree-Branch heisst `worktree-agent-a247febae48665531`
  (vom Harness angelegt), steht aber auf demselben Sha wie
  `docs/audit-and-advisor-design` (83cfed8, Vorfahr 41206be enthalten);
  gearbeitet, weil ein Branch nur in einem Worktree ausgecheckt sein kann und
  die Bedingung sonst nie erfuellbar waere. Der Director fuehrt die drei
  Commits nach.
NÄCHSTER: director (d: Entscheidung ui-ux-designer, siehe unten)
BLOCKIERT DURCH: nichts fuer a-c; d durch AK-216 (Messauflage: "Jede
  Differenz ausser 0 px ist ein Befund und kommt zurueck zu mir, nicht in
  eine Nachbesserung") gegen die Auftragszeile "Ursache gefunden -> Fix"

# T-218 — Bericht developer

Messumgebung ueberall: Windows 11 Pro 26200, Python 3.12, Qt-Plugin
`windows`, Stil Fusion mit dunkler Palette, Skalierung 1,25 (Zahlen logisch,
Grabs physisch), Bildschirm 4096x1728 logisch, kein Klemmen. Datenumlenkung
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-218`, `LOCALAPPDATA`/`APPDATA` auf
`<scratchpad>/T-218/`, Testabzug hineinkopiert (841 Dateien, 20 812 293
Bytes), `paths.cache_dir()` positiv geprueft. Spielstand des Nutzers nur
gelesen.

## a — QA-210 · erledigt · Commit 3798c57

**Erreichbar, belegt durch Test.** `available_items()` liest den Bestand
der *Karte* (`RelicSlot.owned`), `asking_from` den des *Fensters*
(`planner.owned`). `_on_save_read(found=None)` (app.py:4143-4154) und
`_on_save_failed` (app.py:4220-4221) setzen den Fensterbestand auf `None`
und kehren **vor** `_hand_the_stock_to_the_slots` zurueck — die Karten
behalten den alten Bestand. Ein Rescan ohne Fund oder ein per "Find my
save" gewaehlter leerer Spielstand nach einem gelungenen ersten Lesen
liefert also: Karten im Picker, keine Rangfolge, und die Kopfzeile sagte
etwas ueber die Spieldaten.

**Befund, der den Auftrag korrigiert:** `NO_FIGURES_AT_ALL` hatte im
Programm **keinen zweiten Ausloeser**. `ranking is None` ohne Fehlschlag
entsteht nur, wenn `SlotAdvice.ask` `None` gibt, und das tut es nur fuer
"kein Spielstand" (`asking_from` -> `None`) oder einen Slot ausserhalb
`active_slots()` (aus dem sich kein Picker oeffnen laesst). Die "Richtung
ohne Zahlen" laeuft ueber eine vorhandene Rangfolge und sagt
`nothing_raises(...)` (AK-46). Deshalb kein getrennter zweiter Satz, sondern
Ersatz: `NO_FIGURES_AT_ALL` -> `NO_SAVE_WAS_READ`, Wortlaut woertlich aus
T-124: `No save was read, so there is nothing to rank these against — use
Rescan save.` Ein toter Satz auf der Flaeche waere derselbe A7-Bruch.

Tests: `test_with_no_ranking_every_card_says_so_and_the_header_says_why`
(Literal als Waechter), `test_a_rescan_that_finds_no_save_leaves_cards_the_picker_can_show`
(Erreichbarkeit am echten Fenster: Rescan mit `None`, `planner.owned is
None`, Karten im Picker, Kopfzeile), `test_a_failure_fills_the_grid_and_says_why`
haelt beide Saetze auseinander. Projektweite Suche nach dem alten Satz:
Code 0 Treffer; Doku: UI_SPEC.md:1854 (nennt ihn als *nicht* erscheinend),
T-180-Bericht, T-218-Auftrag, Archiv — unveraendert, nicht meine Dateien.

**An ui-ux-designer:** UI_SPEC §3.7/AK-49 nennt den alten Satz; im Code
gibt es ihn nicht mehr. AK-49 bleibt durch `nothing_raises` erfuellt.

**Nebenfund (nicht behoben):** dass die Karten nach einem Rescan ohne Fund
den alten Bestand behalten (app.py:4143-4154, 4220-4221), widerspricht
AD-029 Punkt 3 ("bis `self.owned` ersetzt wird") — der Fensterbestand ist
ersetzt, der Kartenbestand nicht. Der Spieler kann Relikte eines Spielstands
waehlen, den das Fenster nicht mehr kennt. Titel: "Kartenbestand ueberlebt
einen Rescan ohne Fund". Entscheidung Director.

## b — QA-232 · erledigt · Commit e7f485c

Nachgezaehlt vor der Aenderung: `grep -c "raise ValueError" nrdata/*.py` =
25 = 21 (meine acht Dateien) + dcx 2 + tpf 1 (T-219) + savefile.py:358 (1).
Geaenderte `raise`-Zeilen je Datei: bnd4 1, dds 5, dvdbnd 5, extract 2,
fmg 3, oodle 2, param 1, paramdef 2 = **21**, dazu je Datei eine
Import-Zeile (8). Alle 21 sind Aussagen ueber die Datei (Magic, Tabellen
und Nutzlasten, die nicht in die Datei passen, 0x0-Bild, verschluesselter
Eintrag, Feld, das das Paramdef nicht traegt, Feld ohne Bewegung,
Paramdef groesser als die Zeile, unlesbare Felddefinition, unbekannter
Typ) — **keine ist ein Programmfehler**; `savefile.py:358` (falscher
`mode`) ist einer und bleibt `ValueError`. Zweite Maske
(`grep -rn "ValueError" nrdata/*.py` ohne `except`/Kommentar): 5 Treffer —
dcx 2, tpf 1 (T-219), savefile 1 (Programmfehler), `icons.LayoutError`
(eigene Klasse, wird zitiert). `firstrun.py` unveraendert.

Test: `test_the_first_run_keeps_a_refusal_of_the_extraction_path` — der
echte `dds.decode(b"RIFF")`-Fehler kommt durch `_Builder.run` woertlich an:
`not a DDS file (magic b'RIFF')`. Toetende Mutation: dds.py:69 zurueck auf
`ValueError` -> "Something went wrong ... (ValueError)".
`test_a_library_never_supplies_the_words` (SEC-023-Seite) bleibt gruen.

**An T-217/T-219:** oodle.py traegt jetzt `from .binary import
NotWhatItClaims` nach `import pathlib` (Zeile 13) — Konfliktstelle, falls
T-217 dort ebenfalls Importe aendert.

## c — SEC-039 · erledigt · Commit 47ffcaa

shortcut.py:136-143: `detail[0]` weg; `returncode != 0` oder Datei fehlt ->
`"the shortcut could not be written"` (vorhandener Satz, der Aufrufer stellt
`The Start Menu entry could not be changed.` davor); `stderr`/`stdout` per
`print(..., file=sys.stderr)` — das Modul hat kein Logging, die Konsole ist
der Weg, den `traceback.print_exc()` im Projekt schon nimmt. Test:
`test_the_start_menu_button_never_quotes_powershell` — gestubbtes
`subprocess.run` mit `returncode 1` und `stderr` = deutscher Text +
`A_SAVE_PATH`; beides fehlt im Rueckgabewert, beides steht auf `stderr`
(`capsys`). Zweite Maske (`subprocess.run|CompletedProcess|.returncode` in
nrplanner/ ausser shortcut.py): 0 Treffer.

## d — QA-242 · teilweise: Ursache gefunden und gemessen, kein Fix

Messskript `<scratchpad>/T-218/measure_90px.py` (Rezept von
`scripts/measure_picker_cards.py`, dazu ein Spy auf `_fit_to_three_rows`,
der Chrome und Zeilen **im Moment der Groessenwahl** liest). Slot 1, 56
Karten (55 Relikte + Custom-Kachel), Dialogbreite 1024. Grabs
(`QWidget.grab()`, physisch 1280 breit): `relicpicker-natural-1061.png`
(1280x1326), `relicpicker-forced-1121.png` (1280x1401).

| Zustand | `_chrome_height` | drei Zeilen | `wanted_height` | `height()` |
|---|---|---|---|---|
| bei der Groessenwahl (Wartezustand, `__init__`) | 316 | 745 `[228, 243, 258]` | **1061** | 1061 |
| nach der Antwort, Karten in Rasterordnung | 406 | 715 `[228, 228, 243]` | 1121 | 1061 |
| nach der Antwort, Karten in beraterfreier Ordnung | 406 | 745 | **1151** | 1061 |
| `frameGeometry()` bei 1121 | | | | 1151 |

**Die 90 px sind der Chrome-Unterschied 406 - 316**, exakt: die
`findings`-Zeile (3b) ist bei der Groessenwahl unsichtbar und zaehlt 0, nach
der Antwort sichtbar und zaehlt **75**; die `summary` waechst um den
`ranked against ... empty`-Zusatz von 30 auf **45**. T-207s 1151 ist
`wanted_height()` nach der Antwort mit den Karten in beraterfreier Ordnung
(406 + 745); T-199s 1121 dieselbe Rechnung mit der Rasterordnung nach der
Antwort (406 + 715); 1061 ist die Zahl der Groessenwahl. Alle drei Werte
sind dieselbe Funktion in drei Zustaenden.

Ausgeschlossen (gemessen): Fensterrahmen (30 px, `frameGeometry` 1091 zu
`geometry` 1061 — erklaert nicht die 90, nur die Bildhoehe); Klemmen
(avail 1728); Bildlaufleiste (waagerecht nie sichtbar, senkrecht in der
Breite eingerechnet); `minimumSizeHint` (464) und `sizeHint` (614) spielen
nicht mit.

**Zwei weitere Messbefunde in `_chrome_height`, die den Fix zur
Designfrage machen:**

1. `_asked_height` nimmt `max(heightForWidth(room), item.sizeHint())`;
   fuer umbrechende `QLabel` ist `sizeHint` Qts Umbruch bei ~80 Zeichen,
   nicht "eine lange Zeile" (Docstring :1122-1125). Gefragt gegen
   tatsaechlich: `caveats` **150 zu 60**, `summary` 45 zu 15, `findings`
   75 zu 30.
2. `layout.spacing() * (count - 1)` zaehlt Abstaende fuer verborgene Zeilen
   (headline, findings): +10 je Zeile; Qt setzt sie nicht.

Tatsaechlicher Chrome bei 1061: 231 (Sichtbereich 830 = 1061 - 231).
Bei der Groessenwahl gerechnet: 316 — **125 px zu viel**. Genau dieser
Ueberschuss traegt heute AK-51: nach der Antwort kostet die
`findings`-Zeile real 40 px (30 + Abstand), und drei Zeilen (715 oder 745)
passen in 830 nur, weil zu viel reserviert wurde. Eine korrekte
`_chrome_height` (191 + 745 = 936) gaebe nach der Antwort 705 px
Sichtbereich — **zwei** ganze Zeilen, AK-196 haelt, AK-51 nicht.

**Warum kein Fix in diesem Lauf:** AK-216 legt die Groesse auf den ersten
Anstrich in beraterfreier Ordnung fest und verbietet ein zweites Messen; die
Zeile, die nach der Antwort dazukommt (3b), ist vorher inhaltlich unbekannt.
Damit `wanted_height()` und `height()` im selben Lauf gleich sind, gibt es
zwei Wege, und beide sind Designentscheidungen:

- **A (Definition):** `wanted_height` ist die Zahl der Groessenwahl und wird
  einmal festgehalten (beraterfreie Ordnung, Wartechrome); spaetere Aufrufe
  geben sie zurueck. Beide Zahlen gleich (1061 == 1061), Messgrundlage
  eindeutig, keine Aenderung auf der Flaeche. Laesst die 125 px
  Ueberschaetzung stehen, die AK-51 traegt — dokumentiert, nicht behoben.
- **B (Reservierung):** `_chrome_height` korrekt (heightForWidth,
  Abstaende nur fuer Sichtbares) **plus** eine bewusste Reserve fuer 3b
  (z. B. eine Zeile je Fundstelle, Obergrenze) — wie viel, ist die Frage
  an den ui-ux-designer; danach A obendrauf.

AK-216 selbst sagt fuer diese Differenz: "kommt zurueck zu mir, nicht in
eine Nachbesserung". Ich habe deshalb nichts an `_fit_to_three_rows`
geaendert. Ein zweiter Anlauf braucht keinen `fehlerdiagnostiker` — die
Ursache steht — sondern die Entscheidung A oder B.

## Suite

`pytest -n auto`: **1792 passed, 9 skipped** in 64,5 s (Stand 47ffcaa;
1789 + 3 neue). Kein Linter konfiguriert. Ponytail-Durchsicht des Diffs
83cfed8..47ffcaa: 12 Dateien, +147/-45 — Lean already (die Zeilen sind
Docstrings im Hausstil und drei Tests).
