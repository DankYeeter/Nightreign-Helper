# T-334p qa-engineer -- Pruefung am Quellstand `a5cd4eb`

```
STATUS: erledigt
AUFTRAG: T-334p
GELESEN: docs/tasks/T-334.md (ganz), ~/.claude/agents/_rahmen.md, CLAUDE.md, UI_SPEC.md Nachtrag T-334n (Z. 8209 ff.) und AK-381/382 (Z. 7965-7995), qa/findings.md (letzte Zeile je ID), qa/verlauf.md QA-206, docs/berichte/T-334a-qa-engineer.md (QA-185, QA-202/206), Commit-Texte 661bb73..a5cd4eb, scripts/drive_window.ps1, nrplanner/firstrun.py:505-540/985-1000, nrplanner/statsheet.py:800-830, tests/test_load_and_title_wording.py:37-46
GEAENDERT: docs/berichte/T-334p-qa-engineer.md (nicht committet, Rolle nur lesend in git)
ANNAHMEN: (1) "kein Traceback" bei beschaedigtem Spielstand gilt fuer das Fenster; der Konsolen-Traceback ohne Ausnahmetext ist SEC-044 Option A (Director 13.10. 18:52). (2) SEC-IDs beurteilt T-334q; hier nur deren Fensterwirkung.
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

## Urteil: CONCERNS

Kein Befund P1/P2. Jeder in T-334 als behoben gemeldete QA-Befund haelt im Retest; QA-030 bleibt teilweise (dritter Punkt laut Director im naechsten Zyklus). Zwei neue Befunde P4, zwei offene Fragen.

## Zahlen

- **Suite** `pytest -n auto` im Klon `git archive a5cd4eb` (Scratchpad `T-334p/tree`), 14.10. 18:16-18:19: **2063 passed, 9 skipped, 1 failed** in 190 s. Der eine Fehlschlag ist der Klon selbst: `test_the_half_written_snapshot_is_ignored_by_git` ruft `git check-ignore`, das Archiv hat kein `.git` ("fatal: not a git repository"). Im Hauptbaum (Code = `a5cd4eb`, `git diff a5cd4eb HEAD` nur `docs/tasks/T-334.md`) gruen: `tests/test_release_spec_datas.py` 2 passed. Gezaehlt also **2064 / 9**, wie rechnerisch erwartet. Parallel lief eine fremde pytest-Suite (ApplicationHelper, 4 Prozesse) - Zeiten nicht vergleichbar.
- **Rot-vorher** (Code von `C^`, `tests/` von `C`, nur die vom Commit beruehrten Testdateien): 23 Fix-Commits, **23 von 23 rot**. Einzeln: 38b733b 1, 7f23375 1, d477626 1, 94f8309 1, 90df965 1, eab0fc0 3, 108ead5 Sammelfehler (Funktion fehlt), 54f6802 8, 8ef056e 3 (inkl. QA-123-Test, Fix liegt in `tests/weapon_damage_cases.py` aus 1471544), aa0952e 1, c4f0f9d 2, bf4f622 1, dbca09f 16, 1388656 6, 425b523 3, d8af698 9, 264572a 8, f129b22 2, fcf4a7e 4, 91ac5e1 15, 366cbd5 3 F + 3 E (mit `conftest.py` von `366cbd5^`), c84cd54 1 F + 23 E (Fenster-Fixture scheitert am alten Code).
- **Mutationen fuer reine Testcommits:** QA-037 (`bnd4._check_entry_table` Schrittweitenpruefung entfernt) 2 rot; QA-078 (`active=False` in `statsheet.py:703`) 1 rot; QA-087 (`.exists()` -> `.is_dir()` in `scripts/differential/mutate.py:198`) 1 rot. QA-052/053/110, QA-091, QA-236, SEC-040 nicht mutiert, Commit-Angabe uebernommen.
- **Fenster:** Windows 11, DPR 1,25 (GetDpiForWindow 120), Zahlen physisch, wo nicht anders genannt; Quellstand `python run.py` aus dem Klon, Treiberkopie mit PID-Pin (siehe Befund 2), `-Real`.

## Fensterpunkte

| Punkt | Ergebnis |
|---|---|
| Why-Dialog Faltknoepfe | Tab erreicht alle vier (`FoldButton`), Leertaste und Enter schalten `Show 1 effect without a number` <-> `Hide ...`, Dialog bleibt offen; Fokusrahmen sichtbar (Bild `why_keys.png`). Enter auf der Scrollflaeche schliesst den Dialog (Standardknopf `Close`) - Qt-ueblich, kein Befund |
| `Why this relic` | Deep an, 6 Gruppen: Karte 4 -> Gruppe "Slot 4" oben im Sichtfeld; Karte 6 -> bis zum Ende gescrollt, Gruppe 6 sichtbar; Karte 1 -> oben. Bar-`Why` oeffnet oben |
| Notes offen bei `unknowns` | am Fenster nicht erzeugt (kein Fall mit `unknowns` gefunden); nur Test (rot-vorher dbca09f) |
| Speichern-Tooltip | `Saved "QA T-334p build".`, zweites Mal `Saved over "QA T-334p build".`, unter der Build-Liste, nach 4,7 s weg |
| Nightfarer-Wiederklick | Tooltip `Wylder is already selected.` unter der Kachel, Kachel bleibt `On`, nach 4,8 s weg |
| Deep-Schalter "— n left empty" | Harness unter `QT_QPA_PLATFORM=windows` (logisch): sizeHint 173 -> 255 px bei n=1/3; linke Spalte 430 (Start) bzw. 300 (Fenster 1190) - passt, Fenster-Minimum bleibt 1190. Der Zustand selbst ist am Fenster nicht erzeugt |
| Hover Relikt-Karten | Groesster Picker dieses Spielstands: 55 Relikte je Farbe (alle Gefaesse und Deep-Slots durchgezaehlt), ein ~211-Karten-Picker existiert hier nicht. Bei 51 Karten: 58 Groessenschritte 1411<->700 px, Median 18 ms (Zeiger auf Karte) gegen 20 ms (Zeiger ausserhalb), Maximum 54/50 ms - kein Unterschied. Nach Umbruch traegt die Karte unter dem Zeiger die Marke (`hover_900.png`) |
| Favoritenmenue | `Undertaker` voll lesbar unter dem Portrait, alle zehn Namen sichtbar (`favmenu0.png`) |
| Filter-Tooltips | bei 132 px Boxbreite: `All colours`, `Normal + Deep`, `Any stacking` + Erklaerzeile, `Buffs and curses` |
| Spaltenkoepfe | bei Fenster 1190 (Spalten 82 px): UIA-Name voll, z. B. `Comes with curse` |
| Leiste zweizeilig | Echter Mauszug 2467 -> 1506 px (Fenster 1959 -> 1190 logisch), 65 Messpunkte: **genau ein** Wechsel (zwischen 2452 und 2422), zurueck genau einer (2436); Kipppunkt per SetWindowPos auf 1 px: 2433 zweizeilig / 2434 einzeilig = 1932,8 logisch (Spec 1933). Fokus blieb auf `Save`. Optimize nie unter 100 px (80 logisch), `goal_box` unten 150 px (120 logisch). Richtungswechsel bei 1750 logisch: `Maximise damage` zweizeilig -> `Minimise damage taken` einzeilig -> zurueck zweizeilig, Fokus auf `Goal`. An 2434 und 2433: Optimize, Apply all -> `Undo apply`, Undo, Clear - Zeile aendert sich nie. `Cancel` nie beobachtet (Lauf kuerzer als 50 ms Abtastung) |
| Leerer Spielstand (`USERPROFILE` + `APPDATA` umgelenkt) | "No save file found. Relic slots stay empty; ... use Find my save." und Knopf `Find my save...`; Konsole leer |
| Beschaedigte Kopie (1 Byte bei 0x10000, nur im Testordner; Original unveraendert, mtime 11.10. 16:46:22) | Fenster: "Save could not be read: a character slot in this save does not match its own checksum"; Konsole: Traceback mit Frames und `nrplanner.inventory.SaveNotReadable`, ohne Text (Option A) |
| QA-202/QA-206 | Erststart ohne Abzug: `nightreign_data.json` 40 s, Symbolvorrat 72 s nach Start (Datei-mtimes). Zweiter Start: Fenster sofort, beide mtimes unveraendert - kein Neueinlesen, also auch kein Grundsatz. Je eine Probe |
| QA-301 Teil 3 | Mit korrekt kopiertem Testabzug (`<LOCALAPPDATA>\NightreignHelper\`) Fenster nach hoechstens 7,9 s |
| Ersteinrichtung ohne Steam | siehe Befund 1 |

## Befunde

### [P4 | Minor | Niedrig] Ordnerdialog ohne Steam-Bibliothek oeffnet im Arbeitsverzeichnis, nicht in "This PC"

**Adressat:** developer (zur Kenntnis security-reviewer, SEC-042)
**Betroffen:** `nrplanner/firstrun.py:513-532` (`where_to_start_looking`), `:997` (`_pick_a_folder`)
**Umgebung:** kein Steam-Eintrag bzw. keine Bibliothek; Windows-Plattform, nativer Dialog

**Reproduktion:**
1. Harness `T-334p/sec042.py`: `gamefiles.steam_common_folders = lambda: []`, dann `_pick_a_folder(None, where_to_start_looking(None))`.
2. Adresse des Dialogs `Select Folder` per UIA lesen.
3. Mit anderem Arbeitsverzeichnis wiederholen.

**Erwartet:** Start in "This PC" (Docstring Z. 516, Ergebnis T-334g, Director-Annahme 18:50).
**Tatsaechlich:** `Address: ...\T-334p\tree`, beim zweiten Lauf `...\T-334p\w5` - jeweils das Arbeitsverzeichnis des Prozesses.

**Analyse:** Ein leerer Startordner laesst Qt `QDir::currentPath()` nehmen, nicht die Windows-Voreinstellung. Beim ausgelieferten Programm ist das der Ordner, aus dem die EXE gestartet wurde. Vor `bf4f622` galt das ebenso, sobald `C:\Program Files (x86)\Steam\steamapps\common` fehlte. `test_a_registry_without_steam_offers_no_root_at_all` prueft nur `None`, nicht den Startort (NH-016: Code, nicht Kriterium).
**Auswirkung:** Der Spieler sucht vom Download-Ordner aus statt von den Laufwerken. Sicherheitlich harmlos, die SEC-042-Absicht bleibt erfuellt.
**Vorschlag:** "This PC" ausdruecklich angeben (Qt erlaubt unter Windows `clsid:`-URLs mit `getExistingDirectoryUrl`, CLSID 20D04FE0-3AEA-1069-A2D8-08002B30309D) und am nativen Dialog pruefen.

### [P4 | Minor | Hoch] `drive_window.ps1` findet keinen Quellstand-Lauf

**Adressat:** developer
**Betroffen:** `scripts/drive_window.ps1:79`
**Reproduktion:** `python run.py` (venv) starten, Treiber dot-sourcen, `Main`.
**Erwartet:** Fenster gefunden (CLAUDE.md, NH-010: QA prueft "am Quellstand mit `scripts/drive_window.ps1`").
**Tatsaechlich:** `$PIDW` sucht nur den Prozess `NightreignHelper`; der Quellstand laeuft als `python.exe`, der venv-Starter erzeugt zwei PIDs (5488 Starter, 3968 Fenster). Die Suche ueber `MainWindowTitle` kippt, sobald ein modaler Dialog offen ist ("Slot 1 - Green"), und `ListTop` liefert dann leer. Seit T-325 baut jeder QA-Lauf eine Kopie.
**Vorschlag:** PID als Parameter oder ueber `EnumWindows` nach Fenstertitel "Nightreign Helper*" ermitteln und fuer die Sitzung festhalten.

## Offene Fragen

- **ui-ux-designer:** Ohne Spielstand rät die Leiste "No save was read, so there are no relics to choose from — use Rescan save.", das linke Panel "use Find my save". Rescan findet ohne Datei nichts. Beides gleich lassen oder die Leiste auf `Find my save...` umstellen?
- **ui-ux-designer:** Im Why-Dialog steht eine fremde Nightfarer-Zeile durchgestrichen und rot ("[Undertaker] ... works only for Undertaker, and you are Wylder."). Die Legende darunter erklaert Durchstreichen nur als "one you avoided". Das ist ein Bestand (`advisorblock.py:132`, Director). Soll die Legende den zweiten Fall nennen?

## Retest je ID

Spalte "Test prueft" (NH-016): **K** = das Kriterium (sichtbares Verhalten oder Wortlaut), **C** = nur Code oder Struktur, **-** = kein Test (Text).

| ID | Urteil | Beleg | Test prueft |
|---|---|---|---|
| QA-007 | behoben | fcf4a7e rot-vorher 4; Fenster: beschaedigte Kopie -> Satz | K |
| QA-008 | behoben | 264572a, 91ac5e1 rot; Fenster nicht (Spielstand ohne Relikte nicht erzeugt) | K |
| QA-009 | behoben | 54f6802 rot 8 | K |
| QA-010 | behoben | d8af698 rot | K (Wartezeit zwischen Versuchen) |
| QA-012 | behoben | d8af698 rot | K |
| QA-020 | behoben | 54f6802 rot | K |
| QA-026 | behoben | 264572a/91ac5e1 rot; Breite am Windows-Harness | K |
| QA-027 | behoben | d8af698 (Feld) + 264572a/91ac5e1 (Satz) rot | K |
| QA-028 | behoben | 264572a rot | K |
| QA-030 | teilweise | Markierung und Satz behoben (rot-vorher); dritter Punkt (leerer Slotsatz wird nie gespeichert) offen, Director -> naechster Zyklus | K |
| QA-031 | behoben | 264572a, 91ac5e1 rot | K |
| QA-037 | behoben | Mutation bnd4 -> 2 rot | K (Waechter) |
| QA-038 | behoben | fcf4a7e `test_the_inventory_and_the_save_reader_decrypt_in_one_place` rot | C |
| QA-047 | behoben | 366cbd5 rot-vorher; `reg query HKCU\Software\DankYeeterTests` 14.10. nach allen Laeufen: kein PID-Store | K |
| QA-052 | behoben | Commit-Angabe uebernommen | K (Waechter) |
| QA-053 | behoben | dto. | K (Waechter) |
| QA-077 | behoben | 108ead5 rot (Funktion fehlt) | C - prueft `breakdown_text`, nicht den `showText`-Aufruf |
| QA-078 | behoben | Mutation `active=False` -> rot | K |
| QA-087 | behoben | Mutation `.is_dir()` -> rot | K |
| QA-088 | behoben (b) | 8ef056e rot 2 | K |
| QA-091 | behoben | Commit-Angabe uebernommen | K (Waechter) |
| QA-093 | behoben | c8a13bc, nur Docstring | - |
| QA-103 | behoben | eab0fc0 rot | K |
| QA-104 | behoben | eab0fc0 Hinweistext rot, 90df965 Docstring | K |
| QA-105 | behoben | eab0fc0, 90df965, 94f8309 rot; `Budget(0)` laut T-334h seit b5059c6, nicht nachgeprueft | K |
| QA-109 | behoben | 9d2d743, nur Docstring | - |
| QA-110 | behoben | Ortswaechter mit Positivkontrolle (bd4ae9f), Commit-Angabe | K (Waechter) |
| QA-123 | behoben | Test rot ohne 1471544 | K |
| QA-157 | behoben | 1388656 rot 4; Fenster: Marke folgt nach Umbruch, kein Zeitunterschied | K |
| QA-158 | behoben | 1388656 rot 2; Fenster: Namen sichtbar | K |
| QA-160 | behoben | 425b523 rot; Fenster: Tooltips | K |
| QA-162 | behoben | 425b523 rot; Fenster: UIA-Name voll. UIA-`HelpText` bleibt leer - die Beschreibung liegt vermutlich unter `FullDescription`, nicht gemessen | K |
| QA-171 | behoben | d8af698 + 264572a + 91ac5e1 rot; Fenster nicht (Spielordner nicht entfernt) | K |
| QA-185 | geschlossen | kein Fehler (T-334h). Nachgesehen: die frueher `app.py:3142` genannte Stelle steht in `statsheet.py:806-827` als Liste (Name, Wert), kein Schluessel nach Name | - |
| QA-193 | behoben | d8af698 rot | K |
| QA-202 | geschlossen | nicht reproduziert: zweiter Start ohne Neueinlesen, mtimes unveraendert (eine Probe) | - |
| QA-206 | geschlossen | mit QA-202: kein Neubau, also kein Grundsatz | - |
| QA-212 | behoben | 366cbd5 rot-vorher (alte conftest) | K |
| QA-213 | behoben | wie QA-007 | K |
| QA-223 | behoben | d8af698 rot 2 | K |
| QA-236 | behoben | a1f80a3, Commit-Angabe | K |
| QA-292 | behoben | c84cd54 rot; Fenster-Mauszug siehe oben | K |
| QA-300 | behoben | dbca09f rot 13; Fenster: Falten, Tastatur, Kartensprung, Accessible-Names `Goal`/`Hit with`/`Damage type` | K |
| QA-301 | behoben | dbca09f rot 3; Fenster: beide Tooltips; Teil 3 mit korrektem Abzug <= 7,9 s | K |
| T-333g (AK-383) | behoben | aa0952e rot | K |

SEC-021/025/040/042/044/049/050: Urteil bei T-334q. Am Fenster gesehen: SEC-044 Konsole ohne Ausnahmetext; SEC-042 siehe Befund 1.

## Registerzeilen (anhaengbar an `qa/findings.md`)

```
| QA-007 | Save-Pruefsumme immer falsch; Lesepfad prueft sie nicht | P3 | Major | developer | Retest T-334p, rot-vorher fcf4a7e, Fenster | behoben -- Pruefsumme je Slot (`fcf4a7e`), beschaedigte Kopie -> Satz im Fenster | 2026-10-14 |
| QA-008 | "No save file found." bei vorhandenem Save ohne Relikte | P3 | Minor | ui-ux-designer, developer | Retest T-334p, rot-vorher | behoben -- `264572a`, `91ac5e1` (AK-388/389); Fenster ungeprueft | 2026-10-14 |
| QA-009 | `MIN_HEROES = 4` verlangt tatsaechlich fuenf Gruppen | P3 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `54f6802` | 2026-10-14 |
| QA-010 | `_read_settled` wartet nicht und meldet nicht, wenn es aufgibt | P3 | Minor | developer, ui-ux-designer | Retest T-334p, rot-vorher | behoben -- `d8af698` | 2026-10-14 |
| QA-012 | Gated-Effekte umgehen die Bedingungspruefung bei Resistenzen | P4 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `d8af698` | 2026-10-14 |
| QA-020 | Loadout-Fehlermeldung zeigt Leserinterna | P4 | Minor | ui-ux-designer | Retest T-334p, rot-vorher | behoben -- `54f6802` | 2026-10-14 |
| QA-026 | `_settle_slots` leert einen ausgeblendeten Deep-Slot; Begruendung unsichtbar | P4 | Minor | developer | Retest T-334p, rot-vorher, Windows-Harness | behoben -- Deep-Schalter "— n left empty" (`264572a`, `91ac5e1`) | 2026-10-14 |
| QA-027 | Nicht mehr besessenes Relikt aus der Loadout-Tabelle wird still zu `None` | P3 | Minor | developer | Retest T-334p, rot-vorher | behoben -- Feld `d8af698`, Satz `264572a`/`91ac5e1` | 2026-10-14 |
| QA-028 | `custom_item` ueberlebt Gefaesswechsel | P4 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `264572a` | 2026-10-14 |
| QA-030 | Doppelung in ausgeblendetem Deep-Slot wird festgeschrieben, Hinweis nie sichtbar | P3 | Major | developer | Retest T-334p | teilweise -- Markierung behoben (`264572a`, `91ac5e1`); leerer Slotsatz wird nie gespeichert: offen, naechster Zyklus | 2026-10-14 |
| QA-031 | "Load equipped" nennt den Grund zweimal | P4 | Trivial | ui-ux-designer | Retest T-334p, rot-vorher | behoben -- `264572a`, `91ac5e1` | 2026-10-14 |
| QA-037 | SEC-002-Waechter in `bnd4`, `dvdbnd`, `tae` ungetestet | P3 | Minor | developer | Retest T-334p, Mutation bnd4 | behoben -- `2c5a0dc`, Mutation 2 rot | 2026-10-14 |
| QA-038 | Entschluesselungsschleife existiert zweimal | P4 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `fcf4a7e` | 2026-10-14 |
| QA-047 | Abgebrochener Testlauf laesst PID-Store zurueck | P4 | Minor | developer | Retest T-334p, rot-vorher, reg query | behoben -- `366cbd5`, kein PID-Store nach allen Laeufen | 2026-10-14 |
| QA-052 | AST-Waechter prueft Schreibweise statt Speicher | P3 | Minor | developer | Retest T-334p, Commit-Angabe | behoben -- `bd4ae9f` | 2026-10-14 |
| QA-053 | Waechter meldet zwei korrekte Schreibweisen rot | P4 | Minor | developer | Retest T-334p, Commit-Angabe | behoben -- `bd4ae9f` | 2026-10-14 |
| QA-077 | `_show_breakdown` ungetestet | P2 | Major | developer | Retest T-334p, rot-vorher | behoben -- `108ead5`, Test prueft den Text, nicht den Tooltip-Aufruf | 2026-10-14 |
| QA-078 | Goldring-Zuordnung von keinem Test geprueft | P3 | Minor | developer | Retest T-334p, Mutation `active=False` | behoben -- `1388656` | 2026-10-14 |
| QA-087 | Worktree-Fall im Nachweis falsch | P4 | Minor | developer | Retest T-334p, Mutation `.is_dir()` | behoben -- `57c3f30` | 2026-10-14 |
| QA-088 | (b) `plan.py` warnt nicht bei leerem Rarity-Band | P4 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `8ef056e` | 2026-10-14 |
| QA-091 | Sternimport umgeht AD-021-Waechter | P3 | Minor | developer | Retest T-334p, Commit-Angabe | behoben -- `7022958` | 2026-10-14 |
| QA-093 | Zweitschluessel-Test Titel zu stark | P4 | Minor | developer | Retest T-334p | behoben -- Docstring `c8a13bc` | 2026-10-14 |
| QA-103 | Durchlassrate nie null nur im Docstring | P3 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `eab0fc0` | 2026-10-14 |
| QA-104 | Klassengebundener Angriffsbuff ohne Waffe 0, keine Zeile sagt es | P3 | Minor | developer, ui-ux-designer | Retest T-334p, rot-vorher | behoben -- `eab0fc0`, `90df965` | 2026-10-14 |
| QA-105 | Vorbedingungspruefungen des Beraters zu weit | P3 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `eab0fc0`, `90df965`, `94f8309`; `Budget(0)` `b5059c6` | 2026-10-14 |
| QA-109 | `effect_ids_of` Reihenfolge-Behauptung | P4 | Minor | developer | Retest T-334p | behoben -- Docstring `9d2d743` | 2026-10-14 |
| QA-110 | Kein Waechter "kein QSettings im Berater-Pfad" | P4 | Minor | developer | Retest T-334p, Commit-Angabe | behoben -- Ortswaechter `bd4ae9f` | 2026-10-14 |
| QA-123 | Arsenal-Messstrecke fuer sechs Waffen blind | P4 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `1471544` | 2026-10-14 |
| QA-157 | Fuenf anklickbare Flaechen ohne Zeigermarke | P3 | Minor | developer | Retest T-334p, rot-vorher, Fenster | behoben -- `1388656`, `968b4b9`; Marke folgt nach Umbruch, kein Zeitunterschied | 2026-10-14 |
| QA-158 | `FavouriteMenu` Nightfarer nur als Portrait | P3 | Minor | ui-ux-designer, developer | Retest T-334p, rot-vorher, Fenster | behoben -- `1388656`, Namen sichtbar | 2026-10-14 |
| QA-160 | Geschlossene Filtermenues schneiden ihren Wert ab | P3 | Minor | developer | Retest T-334p, rot-vorher, Fenster | behoben -- `425b523`, voller Wert im Tooltip | 2026-10-14 |
| QA-162 | Gekuerzter Spaltenkopf an der Schnittstelle | P3 | Minor | developer | Retest T-334p, rot-vorher, UIA | behoben -- `425b523`, UIA-Name voll bei 82 px | 2026-10-14 |
| QA-171 | Ohne Spielordner alter Abzug kommentarlos | P3 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `d8af698`, `264572a`, `91ac5e1`; Fenster ungeprueft | 2026-10-14 |
| QA-185 | Zwei weitere Stellen fuehren Effekte ueber den Namen | P3 | Minor | developer | Retest T-334p, `statsheet.py:806-827` | geschlossen -- model.py ueber Id (`90ff81d`), Anzeigestelle ist Liste, kein Fehler (T-334h) | 2026-10-14 |
| QA-193 | Zweiter SEC-022-Deckel ohne Anzeigeweg | P3 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `d8af698` | 2026-10-14 |
| QA-202 | Zweiter Start liest Spieldaten erneut ein | P3 | Minor | developer | Retest T-334p, Messung mtimes | geschlossen -- nicht reproduziert: zweiter Start ohne Neueinlesen (eine Probe) | 2026-10-14 |
| QA-206 | Neubau des Symbolvorrats nennt falschen Grund | P4 | Minor | ui-ux-designer | Retest T-334p | geschlossen -- mit QA-202, kein Neubau beim zweiten Start | 2026-10-14 |
| QA-212 | Suite lenkt nur ein Datenverzeichnis um | P3 | Major | developer | Retest T-334p, rot-vorher | behoben -- `366cbd5` | 2026-10-14 |
| QA-213 | Pruefsummen-Lesepfad unbenutzt | P4 | Minor | developer | Retest T-334p, rot-vorher | behoben -- mit QA-007 (`fcf4a7e`) | 2026-10-14 |
| QA-223 | Nutzertexte versprechen Laufwerkssuche | P3 | Minor | developer | Retest T-334p, rot-vorher | behoben -- `d8af698` | 2026-10-14 |
| QA-236 | Test liest `SystemRoot` statt es zu setzen | P4 | Minor | developer | Retest T-334p, Commit-Angabe | behoben -- `a1f80a3` | 2026-10-14 |
| QA-292 | Knoepfe der Leiste schrumpfen unter der Startbreite | P4 | Minor | developer | Retest T-334p, rot-vorher, echter Mauszug | behoben -- `c84cd54`; ein Umbruch je Richtung bei 1933 logisch, Knoepfe >= 80 logisch | 2026-10-14 |
| QA-300 | Why-Fenster: Antwort geht unter, zwei gleiche Why-Knoepfe, Zielwahl ohne Namen | P3 | Minor | ui-ux-designer | Retest T-334p, rot-vorher, Fenster | behoben -- `dbca09f` | 2026-10-14 |
| QA-301 | Speichern und Nightfarer-Wiederklick ohne Rueckmeldung | P4 | Minor | ui-ux-designer | Retest T-334p, rot-vorher, Fenster | behoben -- `dbca09f`; Einrichtung mit korrektem Abzug <= 7,9 s | 2026-10-14 |
| (neu) | Ordnerdialog ohne Steam-Bibliothek oeffnet im Arbeitsverzeichnis statt "This PC" (`firstrun.py:513`, `:997`) | P4 | Minor | developer | T-334p, nativer Dialog per UIA, 2 Arbeitsverzeichnisse | offen | 2026-10-14 |
| (neu) | `drive_window.ps1` findet keinen Quellstand-Lauf (`scripts/drive_window.ps1:79`) | P4 | Minor | developer | T-334p | offen | 2026-10-14 |
```

## Nicht getestet

- Fensterzustaende, die einen konstruierten Spielstand oder ein entferntes Spiel brauchen: QA-008 (Datei ohne Relikte), QA-027/031 (Load equipped mit fehlenden Relikten), QA-171-Titel, Deep-Doppelung QA-026/030 (Breite nur per Harness), Notes offen bei `unknowns`.
- `Cancel` an der Schwelle (Lauf zu kurz zum Abtasten).
- Ein Picker mit ~211 Karten (in diesem Spielstand nicht vorhanden).
- SEC-Befunde inhaltlich (T-334q).

## Hinterlassenes

Registry: Schluessel `HKCU\Software\DankYeeterT-334p` (Testbuild "QA T-334p build", Fensterzustand); Loeschung nicht durch mich. Dateien nur im Scratchpad `T-334p/`. Echter Spielstand nur gelesen (kopiert).
