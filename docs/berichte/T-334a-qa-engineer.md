# T-334a qa-engineer -- Triage aller offenen Befunde, Fixpakete

```
KONTRAKT T-334a
Rolle:      qa-engineer, Modus Triage (statisch + Proben im Scratchpad)
Stand:      HEAD 661bb73 (Branch docs/audit-and-advisor-design), 13.10.2026
Menge:      90 IDs = 81 QA + 9 SEC (letzte Zeile je ID nicht behoben/geschlossen/waived;
            ohne QA-299..301). Abschrift 23.09. sagte 89 + 9.
Urteile:    gueltig 45 (38 QA + 7 SEC) / erledigt 7 / veraltet 9 (8 QA + 1 SEC) /
            Entscheid noetig 26 (25 QA + 1 SEC) / ungeprueft 3 (Fenster noetig)
Pakete:     P-A, P-B, P-C, P-D (disjunkt, keine reservierte T-334c-Datei)
            + Paket "nach T-334c" (app.py, types.py), + 2 Doku-Punkte (architect)
Beruehrt:   nur dieser Bericht. Keine Registerzeile geschrieben.
Fenster:    keins gestartet. Proben offscreen bzw. reine AST-/Datenproben.
Status:     fertig; Belegtiefe je ID unterschiedlich, siehe Spalte "Beleg"
```

## Zaehlung und Methode

Zaehlung per Skript (Scratchpad `T-334a/count.py`): je ID die **letzte**
Tabellenzeile, Zellen an unmaskierten `|` getrennt (QA-040 traegt `\|`), erstes
Wort der Statuszelle. QA: 304 IDs, davon 78 `offen`, 2 `teilweise`,
2 `zurueckgestellt`, 1 `nicht reproduzierbar` (QA-280, kein Statuswort des
Vokabulars, mitgezaehlt), minus QA-300/301 = **81**. SEC: 52 IDs, **9** `offen`.

Belegweg je ID: `grep -rlw <ID>` in `nrplanner nrdata tests scripts run.py`,
`git log --grep`/`-S`, dann Codestelle am HEAD lesen. Fuenf Proben gefahren
(alle umgelenkt: `LOCALAPPDATA`/`APPDATA` auf Scratchpad,
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-334a`):

| Probe | Ergebnis |
|---|---|
| QA-012: Effekte mit Resistenzfeld **und** Gate im Testabzug | 59 mit Resistenzfeld, 421 gegated, **0** beides (latent) |
| QA-052/053: `stores_built_another_way` gegen 5 Formen | Zuweisungs-Alias, Subklasse ohne `__init__`, lokale ORG/APP-Literale -> `[]` (unentdeckt); `favourites as fav` und Drei-Argument-Form -> `[3]` (falsch rot) |
| QA-091: `rate_rank_call_sites('from .weapons import *\nrate(1,2)')` | **0** (Kontrolle `weapons.rate` -> 1) |
| QA-047/195: `reg query HKCU\Software\DankYeeterTests` (nur lesend) | 11 Unterschluessel, davon 10 `NightreignHelperTests-<pid>`; unter `HKCU\Software\DankYeeter` nur noch `NightreignHelper` |
| QA-044/048/054: `reg query ...\NightreignHelper\builds /s /v __schema` (nur lesend) | alle 6 Nightfarer-Gruppen auf Schema `3` |

## Urteil je Befund

Legende: G gueltig, E erledigt, V veraltet, ? Entscheid noetig, U ungeprueft.
Paket: A/B/C/D oder "nT" = nach T-334c.

### Speicher, Inventar, Datenquelle

| ID | Urteil | Beleg | Fixvorgabe / Empfehlung | Testidee | Paket |
|---|---|---|---|---|---|
| QA-006 | ? | Nutzerentscheid, zurueckgestellt | so lassen (Nutzer) | -- | -- |
| QA-007 | ? | `nrdata/savefile.py:119-129` und `inventory.py:256-266` pruefen keine MD5; Messung T-115: 0/28 Slots mit gueltiger Summe = Verfahren unbekannt | Empfehlung wontfix: Programm liest nur, `_read_settled` faengt halb geschriebene Dateien; eine unverstandene Summe wuerde gute Saves abweisen | -- | -- |
| QA-213 | ? | wie QA-007; "nirgends benutzt" ueberholt: `savereader.py:123` ruft `savefile.read` | mit QA-007 schliessen | -- | -- |
| QA-038 | ? | Teil "unbenutzt" ueberholt (`savereader.py:123`); Doppelung steht: `inventory.py:256-266` vs `savefile.py:119` | Empfehlung wontfix: `_decrypt_slots` braucht den Klartext **mit** Laengenpraefix (Offsets), `decrypt_member` schneidet ihn ab -- Vereinheitlichen verschiebt Offsets im Spielstandleser | -- | -- |
| QA-008 | G | `app.py:2472-2474`: automatischer Weg zeigt `NO_SAVE_FOUND` auch fuer einen gefundenen Save ohne Relikte | `scan` liefert None fuer beides; im Automatikweg pruefen, ob `savefile.save_roots()` eine Datei fand, dann `CHOSEN_SAVE_IS_EMPTY`-artiger Satz | Offscreen: save_roots mit leerem Slot-Fixture, Label != NO_SAVE_FOUND | nT |
| QA-009 | G | `nrdata/savefile.py:604`: `groups` zaehlt nur Gruppen mit Folgemarker, also braucht `MIN_HEROES=4` fuenf Marker; Test haelt es bewusst offen `tests/test_loadout_table.py:75-77` | Vergleich auf `len(groups) + 1 >= MIN_HEROES` (letzte Gruppe zaehlt) | Tabelle mit genau 4 Markern liefert Loadouts; `test_loadout_table.py:77` von `+1` befreien | A |
| QA-010 | G | `inventory.py:239-245`: drei Lesungen ohne Pause, nach der dritten still zurueck | kurze Pause (z. B. 0,2 s) zwischen den Versuchen; Aufgeben im Ergebnis vermerken (Docstring nennt "lieber falsch als nichts" als Absicht -- nur das Warten ist Fehler) | `path.stat` monkeypatchen, das zwei Mal wechselt: drei Versuche mit Pause, `time.sleep` aufgerufen | A |
| QA-012 | G | `model.py:1424` `compute_resistances(build, counted)`; `counted` enthaelt gegatete Effekte, Schleife `:1092-1103` prueft kein Gate. Heute 0 betroffene Effekte (Probe) | dieselbe Bedingung wie `:1262` (`is_conditional(...) and not FORCED` -> ueberspringen) | synthetischer gegateter Effekt mit `changePoisonResistPoint`: zaehlt nicht, deklariert zaehlt | A |
| QA-020 | G | `savefile.py:629-633` `NotWhatItClaims` mit "markers present: ff01x3"; als eigene Klasse wortgleich ins Fenster (`errortext.py:93`, `app.py:2486`) | Klartextsatz fuer den Spieler; Markerliste nur in den Tooltip/Log | Text enthaelt kein `ff0` und kein `MIN_HEROES` | A |
| QA-027 | G | `inventory.py:508` `item_by_handle.get(h) if h else None` -- unbekannter Handle still None | Zaehler je Loadout (`missing`) in `EquippedLoadout` (`inventory.py:68-78`); Anzeige im Load-equipped-Satz | Loadout mit fremdem Handle: `missing == 1` | A (Feld), nT (Satz in `app.py:2706ff`) |
| QA-171 | G | `datasource.py:149-152`: Ausnahme in `_regulation_matches` liefert den Abzug kommentarlos | Rueckgabe markieren (z. B. `meta["stale_check_failed"]`); Anzeige spaeter | `_regulation_matches` wirft -> Markierung gesetzt | A (Markierung), nT (Anzeige) |
| QA-193 | G | `relicslots.py:692` ruft `owned.relics_for` ohne `try`; `relics_for` wirft SEC-022 (`inventory.py:175`) | `NotWhatItClaims` fangen, Slot leer mit Grundsatz (`clear_relic(reason)`) | Inventar mit Dichteverletzung: kein Traceback, Grund am Slot | A |
| QA-223 | G | `datasource.py:194-195` "and on the drives C to H" -- Laufwerkssuche seit `bd6bd90` weg | Satz auf die Registry-/Bibliothekssuche kuerzen; projektweite Suche nach "drives C to H" | Text ohne "drives" | A |
| QA-214 | E | tote Zeile ist mit dem Umzug in `savereader.py` entfallen (`a6b10b1`); `app.py` enthaelt kein `SaveNotReadable` mehr | -- | -- | -- |
| QA-217 | E | fremde `ValueError` bekommt eigenen Satz, Waechter `tests/test_exception_text_is_english.py:576` (`8089d22`) | -- | -- | -- |
| QA-219 | V | feste Steam-Wurzel entfernt (SEC-036, `bd6bd90`); `nrdata/gamefiles.py:13-37` nur noch Registry | -- | -- | -- |
| QA-245 | V | `datasource.py:105` verwirft Abzuege mit anderer `extract_version`; Cache seither mehrfach neu (heute 16) | -- | -- | -- |

### Builds, Slots, Migration

| ID | Urteil | Beleg | Fixvorgabe / Empfehlung | Testidee | Paket |
|---|---|---|---|---|---|
| QA-026, QA-030 | G | `app.py:2313` setzt `_unresolved_clash=False` bei **jeder** Reliktbewegung; fuer einen ausgeblendeten Deep-Slot war der Hinweis nie sichtbar. Director-Entscheid 02.09. (`qa/verlauf.md:335`): Deep-Schalter markieren, Statuszeile sagt es | in `_settle_slots` (`app.py:2134-2183`) bei geleertem, ausgeblendetem Slot Statuszeile + Markierung am Deep-Schalter | Deep aus, Doppelung im Deep-Slot restaurieren: Statuszeile nennt es | nT |
| QA-028 | G | `relicslots.py:793-797` `clear_relic` laesst `custom_item` stehen; Restore `app.py:1709-1731` | beim Restore `custom_item` verwerfen, wenn der Schluessel kein Custom ist (Director 02.09.) | Custom in Slot, anderen Build gleicher Farbe laden: Picker bietet es nicht an | nT |
| QA-031 | G | `app.py:2706-2726`: "Nothing ... could be placed." plus "N could not be placed: ..." | bei `placed == 0` beide Gruende in einen Satz | Load equipped mit nur unpassenden Relikten: "could not be placed" genau einmal | nT |
| QA-044, QA-048, QA-054 | ? | Code unveraendert (`chalices.py:284-449`); betrifft nur Speicher vor Schema 3 (Releases v1.0.0..v1.7.1, `git tag --no-contains 543f69d`) **und** Abbruch mitten in der Migration bzw. Name > 16 383 Zeichen. Dieser Rechner: 6/6 Gruppen Schema 3 | Empfehlung wontfix/zurueckgestellt: ein Fix fasst die Migration an, die bei oeffentlichen Alt-Nutzern laeuft; Nutzen nahe null | -- | -- |
| QA-165 | E | Ausloeser (zweite Kopie) seit Instanzsperre `231c42b` entzogen; Befund nannte das selbst | -- | -- | -- |
| QA-166 | E | dto. (`docs/archiv/berichte/T-071-developer.md:396-450`: braucht zwei gleichzeitige Kopien) `231c42b` | -- | -- | -- |
| QA-047 | G | 10 verwaiste `NightreignHelperTests-<pid>` unter `HKCU\Software\DankYeeterTests` (Probe); `tests/conftest.py:47` | beim Sitzungsstart Geschwister-Gruppen toter PIDs loeschen (nur Organisation `DankYeeterTests`) | Gruppe mit nicht existenter PID anlegen, Fixture laufen lassen, weg | D |
| QA-195 | V | Teil 1 (Testschluessel unter der Spieler-Organisation): `HKCU\Software\DankYeeter` haelt nur `NightreignHelper`; Teil 2 ist QA-047 | -- | -- | -- |

### Berater-Rechenkern

| ID | Urteil | Beleg | Fixvorgabe / Empfehlung | Testidee | Paket |
|---|---|---|---|---|---|
| QA-103 | G | `advisor/goals.py:687-690` teilt durch `build.rates.get(...)` und `total` ungeprueft; Docstring `:667-674` begruendet "kein Zweig" | `total > 0`, Gewichte >= 0, Rate > 0 pruefen, sonst `ValueError` mit Satz | Gewichtssumme 0 / Rate 0 -> `ValueError`, nicht `ZeroDivisionError` | B |
| QA-105 | G | Docstring `goals.py:673` "The two preconditions"; mehr Faelle (Gewicht negativ, Feldname unbekannt, `pools` `candidates.py:282`); `Budget(0)` liegt in `advisor/types.py` | Docstring auf die wirklich geprueften Faelle; Pruefungen in `goals.py`/`candidates.py`; `Budget` erst nach T-334c | je Fall ein `pytest.raises` | B (+ `Budget`: nT) |
| QA-104 | G | `goals.py:157` `_NO_ARMAMENT_NOTE` sagt nicht, dass klassengebundene Angriffsbuffs ohne Waffe 0 zaehlen; `candidates.py:150` verspricht "a line of its own" | Satz in `goals.py:157` um den Fall ergaenzen (explain.py nicht anfassen) | ohne Waffe: `weights_note` nennt den Klassenbuff | B |
| QA-109 | G | `advisor/evaluate.py:46-48` "in the same order" -- Messung: gleiche Multimenge, andere Reihenfolge | Docstring korrigieren | (keiner noetig) | B |
| QA-066 | V | Folge fuer AD-018 abgefangen (`64174eb`, `advisor/types.py:9`); `damage.Rating` wird nirgends gehasht (`functools.cache` nur in `bosstab.py:462`, `effecttext.py:264`, `relicpicker.py:107`, alle ohne Rating) | -- | -- | -- |

### Oberflaeche ausserhalb T-334c

| ID | Urteil | Beleg | Fixvorgabe / Empfehlung | Testidee | Paket |
|---|---|---|---|---|---|
| QA-077 | G | `statsheet.py:388` `_show_breakdown` baut Text lokal, 0 Treffer in `tests/` | Textbau in eine Funktion ziehen, `_show_breakdown` ruft sie | Prozentzeile `+12.4 %` fuer Rate 1.124 | B |
| QA-078 | G | `weaponslots.py:225-227` `active` nur im Stylesheet; kein Test liest, welche Kachel `active` traegt | Test, kein Code | nach Wechsel der aktiven Waffe: genau Kachel i `active`, Stylesheet traegt ACCENT | C |
| QA-157 | G | Zeigermarke vorhanden (`relicpicker.py:656, 810, 902`, `weaponslots.py:173`, seit `cec61c7`/`a4963b9`), aber kein `:hover`-Zustand in `relicpicker.py`/`weaponslots.py` | Hover-Rahmen wie QA-154-Fix | Stylesheet enthaelt `:hover` | C |
| QA-158 | G | `relicpicker.py:893-910` Portrait, Name nur `setToolTip` | Name unter/neben dem Portrait wie QA-155(b) | Kachel traegt sichtbaren Namen | C |
| QA-160 | G | `effectstab.py:831-834` `AdjustToMinimumContentsLengthWithIcon`, 8 Zeichen: Wert abgeschnitten (bewusst fuer die Fensterbreite) | Tooltip des geschlossenen Menues = aktueller Text | nach Auswahl `toolTip() == currentText()` | C |
| QA-162 | G | `effectstab.py`: kein `setAccessible*`/`AccessibleTextRole` (0 Treffer) | Kopf-Items `Qt.AccessibleTextRole` = voller Spaltenname, `AccessibleDescriptionRole` = Tooltip | Header-Item-Daten je Spalte gesetzt | C |
| QA-292 | G | Knoepfe Optimize/Apply all/Clear schrumpfen unter Startbreite (`advisorbar.py`, reserviert) | nach T-334c | -- | nT |
| QA-089 | ? | `arsenaltab.py:621-640` `_build_spells` ohne Rarity-Filter; Zauber haben keine Rarity | Empfehlung ui-ux: bei Rarity != All Zauber ausblenden und im Summary sagen | -- | -- |
| QA-067 | ? | AR einzeln gerundet vs. Summe der Typzeilen | Empfehlung ui-ux: lassen (Spiel zeigt ebenfalls gerundete Einzelwerte), ggf. ein Satz im Tooltip | -- | -- |
| QA-159 | ? | Absatz ueber der Tabelle erklaert jetzt Chance (avg/best), Tier, Copies, Relic slots, Stacking, Comes with curse (`effectstab.py:955-961`, `7f77e04`); `Colours` nicht | Empfehlung: schliessen, `Colours` zeigt die Farben selbst | -- | -- |
| QA-179 | ? | `uiscale.py:12` "there is deliberately no 100% entry" -- Absicht dokumentiert | Empfehlung: schliessen als Absicht | -- | -- |
| QA-138 | E | alle sechs Tabs oeffnen mit `tabheader.heading`+`question` (AK-68, `d0d04c9`) | -- | -- | -- |
| QA-190 | V | `ADVISOR PICK` steht weder in `UI_SPEC.md` noch im Code (Spec gekuerzt `f5eb7bd`) | -- | -- | -- |
| QA-174, QA-177, QA-178 | U | brauchen Fenster/UIA; pc_guard nicht geprueft, kein Fensterlauf | offen lassen bis zum naechsten Fensterlauf | -- | -- |

### Waechter und Testschuld

| ID | Urteil | Beleg | Fixvorgabe | Testidee | Paket |
|---|---|---|---|---|---|
| QA-037 | G | kein Test in `tests/` greift `bnd4._check_entry_table` (`nrdata/bnd4.py:41-54`), `dvdbnd.py:44`, `tae.py:78` mit feindlichen Zaehlern an | drei Tests in `tests/test_hostile_gamedata.py` | Kopf mit `file_count` 2**31 -> `NotWhatItClaims` | D |
| QA-052 | G | Probe: 3 Formen unentdeckt (`tests/test_settings_store.py:150`) | Alias-Zuweisung, Subklasse ohne `__init__`, lokale ORG/APP-Literale erkennen | drei Eintraege in `WAYS_ROUND_THE_GUARD` (`:208`) | D |
| QA-053 | G | Probe: 2 korrekte Formen rot | Modul-Alias von `favourites` und Drei-Argument-Form zulassen | zwei Eintraege in `SPELLINGS_THAT_ARE_RIGHT` (`:242`) | D |
| QA-110 | G | kein Waechter "kein QSettings unter `nrplanner/advisor/`" (Ausnahme `worker.py:62` importiert nur QObject/QThread) | Ort pruefen: jeder `QSettings`-Aufruf unter `advisor/` ist rot | Positivkontrolle mit `QSettings(favourites.ORG, favourites.APP)` in advisor-Quelle | D |
| QA-087 | G | `tests/test_differential_track.py:564` legt `.git` als Verzeichnis an, Docstring nennt Datei; accepting-Richtung ist inzwischen getestet (`:569`) | `.git` als **Datei** mit `gitdir:` anlegen | Mutation `.exists()`->`.is_dir()` wird rot | D |
| QA-091 | G | Probe: Sternimport -> 0 Aufrufstellen (`tests/test_one_build.py:63-95` `_local_names`) | `alias.name == "*"` als Import aller Funktionsnamen werten | Eintrag in `test_the_rate_rank_guard_sees_every_way_round_itself` (`:419`) | D |
| QA-212 | G | `tests/conftest.py` lenkt `LOCALAPPDATA`/`APPDATA` nicht um (nur Docstring `:421`) | **Vorsicht:** Fixture `game_data` liest den Abzug ueber `paths.cache_dir()`; erst messen, dann Umlenkung auf ein Sitzungsverzeichnis mit kopiertem Abzug | Suite gruen mit Umlenkung; `paths.cache_dir()` liegt unter tmp | D |
| QA-093 | G | `tests/test_damage_facade.py:356` "on the one input where it is visible at all" (gemessen 25 von 160) | Docstring abschwaechen (keine Logik) | -- | D (nur Text) |
| QA-236 | G | `tests/test_shortcut_interpreter.py:28` liest `os.environ["SystemRoot"]` | SystemRoot per `monkeypatch` setzen | -- | kein Paket (Kapazitaet) |
| QA-088 | G (Rest b) | `scripts/differential/plan.py`: keine Warnung bei Rarity-Band unter Ziel-Tier (0 Treffer "warn") | Warnung/Ausschluss in `plan.py` | Konfiguration Band < Tier -> Warnung | kein Paket |
| QA-123 | G | Messstrecke blind fuer 6/1793 Waffen (Familie ueber Aufklappschwelle) | in `scripts/differential/capture.py` Familie erzwingen | -- | kein Paket |
| QA-023 | ? | Reichweite des Waechters ist inzwischen ausdruecklich als Grenze dokumentiert (`tests/test_one_build.py:39-43, 111-117`, `advisor/evaluate.py:20-24`) | Empfehlung: schliessen als dokumentierte Grenze | -- | -- |
| QA-118 | ? | Aussage betrifft die Waechterqualitaet einer Testdatei; der Faktor aus `99ed022` liegt im Goldfile `tests/golden/weapon_damage.json` (im selben Commit geaendert). Keine Mutation gefahren | Empfehlung: schliessen | -- | -- |
| QA-218 | ? | Positivkontrolle existiert (`tests/test_hostile_gamedata.py:320` `quoted_in_refusals`), prueft Zitate, nicht "Satz ganz im raise" | Empfehlung: schliessen; Rest ist Kommentarregel | -- | -- |
| QA-185 | ? | `model.py` fuehrt Quellen ueber Id (`90ff81d`); `app.py`-Stelle (Anzeigedoppelung) nicht nachgeprueft, Datei reserviert | Empfehlung: als Klassenmassnahme mit nT pruefen | -- | -- |
| QA-092 | V | `MUTATIONS` geleert (`64dd006`), die Zahlen existieren nicht mehr | -- | -- | -- |
| QA-099b | V | kein Fuzzy-Abgleich mehr im Repo (0 Treffer "fuzzy" in `scripts tests nrplanner`) | -- | -- | -- |
| QA-240 | E | Zeilennummern-Zitate geheilt (`608a4cf`, "QA-240 geheilt"); 0 Treffer "see line N" in `model.py`, `damage.py`, `advisor/explain.py` | -- | -- | -- |

### Doku (architect / ui-ux-designer, kein developer)

| ID | Urteil | Beleg | Fixvorgabe |
|---|---|---|---|
| QA-090 | G | `ARCHITECTURE.md:1041, 1111` begruenden "unsichtbar" mit "0 von 7 172" | Satz ergaenzen: Messung sieht Reihenfolge nicht (23/80 Layer-eins-Bewegungen) |
| QA-189 | G | `_ARMAMENT_GATES` noch in `ARCHITECTURE.md:2672, 2881, 2894`, `UI_SPEC.md:4941` | auf `_GATES_THE_NAME_ANSWERS`/`_GATES_WITH_A_WEAPON_TYPE` umstellen |
| QA-116 | E | Wortlaut als historisch markiert, `UI_SPEC` Nachtrag A05 (`cb0600d`); Restnennungen `ARCHITECTURE.md:2042, 2145` sind als historisch gekennzeichnet | -- |

### Prozess, Umgebung, Rest

| ID | Urteil | Beleg | Empfehlung |
|---|---|---|---|
| QA-094, QA-196, QA-197 | ? | Prozessbefunde vom 03.-07.09.; heute je Auftrag eigener Scratchpad-Ordner (T-334: `T-334a/` usw.) | director: schliessen |
| QA-221 | ? | `tests/conftest.py:46` setzt fest `DankYeeterTests`; `CLAUDE.md` verlangt je Auftrag eigenen Wert | Nutzer/director: Satz in `CLAUDE.md` auf "ausserhalb pytest" einschraenken |
| QA-202, QA-206 | ? | zweiter Start liest neu / falscher Grund; T-334b ordnet QA-301 (50 s) als Testabzug-Frage ein | mit QA-301 Teil 3 zusammen messen oder schliessen |
| QA-246 | ? | Exit 127 in Git-Bash, nie reproduziert | schliessen, falls kein Nachweis |
| QA-278 | ? | Kernbeschwerde nur ingame pruefbar | Nutzer im Ingame-Test 1.19.0 |
| QA-282 | ? | Werkzeugbefund, zurueckgestellt | so lassen |
| QA-167 | ? | Performance, nie gemessen | performance-tuner bei S11 oder schliessen |
| QA-280 | V | "nicht reproduzierbar" (T-278a) ist kein Statuswort; kein Auto-Wechsel im Code | Statuswort normalisieren |

### Sicherheit

| ID | Urteil | Beleg | Fixvorgabe | Paket |
|---|---|---|---|---|
| SEC-019 | ? | Klassenbefund, Senken-Retests bestanden | offen als Klasse lassen | -- |
| SEC-015 | V | `detail_expedition`/`everdark_label` gibt es nicht mehr; `bosstab.py:814, 828, 834` setzen das Textformat ausdruecklich, `:1120` escaped | -- | -- |
| SEC-021 | G | `relicslots.py`: kein `html.escape`, kein `setTextFormat` (0 Treffer) in `_sync_mode` (`:389`)/`curse_tooltip` (`:517`) | Namen escapen bzw. PlainText | A |
| SEC-025 | G | `.github/workflows/tests.yml:28, 30` `@v4`/`@v5` ohne SHA (`release.yml` gepinnt) | SHAs wie `release.yml:39, 43` | D (keine Logik) |
| SEC-040 | G | `tests/test_exception_text_is_english.py:78` `WORDING_ATTRIBUTES` ohne `filename` | `filename`, `filename2` aufnehmen | B |
| SEC-042 | G | `firstrun.py:182` `STEAM_COMMON` fest, benutzt `:531` | Haertung bei Gelegenheit | kein Paket |
| SEC-044 | G | `traceback.print_exc()` in `savereader.py:171`, `advisor/worker.py:190`, `firstrun.py:673` | Haertung bei Gelegenheit | kein Paket |
| SEC-049 | G | `nrdata/bossdata.py:103ff` (kein Fixcommit gefunden; nicht neu gemessen) | Deckel fuer `size` | kein Paket |
| SEC-050 | G | `nrdata/bossdata.py:687-688` `unpack` des ganzen Records + `dict.fromkeys` | Record-Groesse deckeln | kein Paket |

## Fixpakete

Disjunkt gegeneinander und gegen die T-334c-Reservierung (`app.py`,
`advisorbar.py`, `advisorblock.py`, `advisor/explain.py`, `advisor/types.py`).

| Paket | Stufe | Dateien mit Logik | Befunde |
|---|---|---|---|
| **P-A Speicher und Slots** | normal | `nrdata/savefile.py`, `nrplanner/inventory.py`, `nrplanner/relicslots.py`, `nrplanner/datasource.py`, `nrplanner/model.py` | QA-009, QA-010, QA-012, QA-020, QA-027 (Feld), QA-171 (Markierung), QA-193, QA-223, SEC-021 |
| **P-B Berater-Kern und Aufschluesselung** | klein | `nrplanner/advisor/goals.py`, `nrplanner/advisor/evaluate.py`, `nrplanner/advisor/candidates.py`, `nrplanner/statsheet.py`, `tests/test_exception_text_is_english.py` | QA-103, QA-104, QA-105 (ohne `Budget`), QA-109, QA-077, SEC-040 |
| **P-C Oberflaeche ausserhalb T-334c** | normal | `nrplanner/effectstab.py`, `nrplanner/relicpicker.py`, `nrplanner/weaponslots.py` | QA-078 (nur Test), QA-157, QA-158, QA-160, QA-162 |
| **P-D Waechter und Testumgebung** | klein | `tests/test_settings_store.py`, `tests/test_hostile_gamedata.py`, `tests/conftest.py`, `tests/test_differential_track.py`, `tests/test_one_build.py`; ohne Logik: `tests/test_damage_facade.py`, `.github/workflows/tests.yml` | QA-037, QA-047, QA-052, QA-053, QA-087, QA-091, QA-093, QA-110, QA-212, SEC-025 |
| **nach T-334c** | normal | `nrplanner/app.py`, `nrplanner/advisorbar.py`, `nrplanner/advisor/types.py` | QA-008, QA-026+QA-030, QA-028, QA-031, QA-027 (Satz), QA-171 (Anzeige), QA-292, QA-105 (`Budget(0)`), QA-185 (Pruefung) |

Hinweise: P-A und "nach T-334c" haengen bei QA-027/QA-171 zusammen (Feld zuerst,
Anzeige danach). P-C QA-157/158 ohne neue AK; Muster QA-154/QA-155(b) folgen,
sonst ui-ux fragen. P-D QA-212 zuerst messen (siehe Tabelle), notfalls aus dem
Paket nehmen. Ohne Paket (gueltig, Kapazitaet): QA-088(b), QA-123, QA-236,
SEC-042, SEC-044, SEC-049, SEC-050; Doku: QA-090, QA-189.

## Registerzeilen zum Anhaengen

`qa/findings.md`:

```
| QA-116 | Ueberholter Attack-Rating-Vorbehalt in den Dokumenten | P4 | Minor | architect, ui-ux-designer | Triage T-334a | geschlossen -- Wortlaut historisch markiert, UI_SPEC A05 (`cb0600d`) | 2026-10-13 |
| QA-138 | Drei Tabs ohne Frage-Ueberschrift (A10) | P3 | Minor | ui-ux-designer | Triage T-334a | geschlossen -- alle sechs Tabs mit `tabheader` (AK-68, `d0d04c9`) | 2026-10-13 |
| QA-165 | Zwei Kopien verlieren Build-Reihenfolge und Versteckt-Marken | P3 | Minor | developer | Triage T-334a | geschlossen -- Ausloeser durch Instanzsperre entzogen (`231c42b`) | 2026-10-13 |
| QA-166 | `_migrate_keys` verstuemmelt Namen bei veraltetem Schema-Lesen | P3 | Major | developer | Triage T-334a | geschlossen -- braucht zwei gleichzeitige Kopien, Instanzsperre `231c42b` | 2026-10-13 |
| QA-214 | Tote Zeile in `app.py` nach SEC-029-Umbau | P4 | Minor | developer | Triage T-334a | geschlossen -- mit dem Umzug nach `savereader.py` entfallen (`a6b10b1`) | 2026-10-13 |
| QA-217 | BND4-Offset hinter Dateiende gibt pycryptodome-Meldung | P4 | Minor | developer | Triage T-334a | geschlossen -- eigener Satz fuer fremde Klassen (`8089d22`), Waechter `tests/test_exception_text_is_english.py:576` | 2026-10-13 |
| QA-240 | Zeilennummern-Zitate im Quelltext verrotten | P3 | Minor | developer | Triage T-334a | geschlossen -- geheilt `608a4cf`, 0 Treffer am HEAD `661bb73` | 2026-10-13 |
| QA-066 | `damage.Rating` nicht hashbar (Rest) | P4 | Minor | developer | Triage T-334a | geschlossen -- veraltet, kein Verbraucher hasht Rating; AD-018 ueber `advisor/types.py` (`64174eb`) | 2026-10-13 |
| QA-092 | Zahlen im Mutationsregister zu QA-086(c) | P4 | unklar | unklar | Triage T-334a | geschlossen -- veraltet, `MUTATIONS` geleert (`64dd006`) | 2026-10-13 |
| QA-099b | Fuzzy-Zuordnung Recluse Staff | P3 | Major | director, qa | Triage T-334a | geschlossen -- veraltet, kein Fuzzy-Abgleich mehr im Repo | 2026-10-13 |
| QA-190 | `ADVISOR PICK` und Picker-Zusatzzeile fehlen | P3 | Major | ui-ux-designer, developer | Triage T-334a | geschlossen -- veraltet, Spec traegt beides nicht mehr (`f5eb7bd`) | 2026-10-13 |
| QA-195 | Testeinstellungen unter der Spieler-Organisation | P3 | Major | developer | Triage T-334a, reg query | geschlossen -- veraltet, unter `DankYeeter` nur `NightreignHelper`; Waisen-Rest laeuft als QA-047 | 2026-10-13 |
| QA-219 | `_steam_roots()` baut Bibliothek doppelt | P4 | Minor | developer | Triage T-334a | geschlossen -- veraltet, feste Wurzel entfernt (SEC-036, `bd6bd90`) | 2026-10-13 |
| QA-245 | Alter Nutzer-Cache stuerzt Planner mit KeyError | P3 | Minor | director | Triage T-334a | geschlossen -- veraltet, `datasource.py:105` verwirft fremde `extract_version` (heute 16) | 2026-10-13 |
| QA-280 | Figurenwechsel ohne Nutzerhandlung | P3 | Minor | director | Triage T-334a | geschlossen -- nicht reproduzierbar (T-278a), Statuswort normalisiert | 2026-10-13 |
```

`security/findings.md`:

```
| SEC-015 | `bosstab.py detail_expedition` auf AutoText | Niedrig | geschlossen -- veraltet, Stelle entfallen; `bosstab.py:814, 828, 834` setzen das Format ausdruecklich (Triage T-334a) | 2026-10-13 |
```

## Nicht getestet

- QA-174, QA-177, QA-178: brauchen Fenster/UIA; kein Fensterlauf (Auftrag:
  Triage am Quellstand).
- Keine Mutationslaeufe fuer QA-037, QA-077, QA-078, QA-118; Urteil aus
  Abwesenheit von Testtreffern (`grep` in `tests/`), nicht aus roten Mutanten.
- SEC-049 nicht neu gemessen; nur "kein Fixcommit gefunden".
- Suite nicht gelaufen (keine Codeaenderung in diesem Auftrag).
