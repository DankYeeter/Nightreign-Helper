# T-161 — Der fehlende Waechter und drei Haertungen am Spielstand (developer)

```
STATUS: erledigt
AUFTRAG: T-161 — Der fehlende Waechter und drei Haertungen am Spielstand
GELESEN: docs/tasks/T-161.md, ~/.claude/agents/_rahmen.md, CLAUDE.md,
         qa/findings.md (QA-215, QA-216, Pruefphase T-159),
         security/findings.md (SEC-029, SEC-035),
         UI_SPEC.md (AK-245 samt Nachtrag, AK-244, AK-126, AK-228),
         ARCHITECTURE.md (R11, R14, R17, V5),
         nrdata/savefile.py, nrplanner/inventory.py, nrplanner/app.py,
         nrdata/gamefiles.py (nur gelesen, Vorbild _changed_at),
         tests/test_hostile_savefile.py,
         tests/test_save_read_in_the_background.py, tests/conftest.py
GEAENDERT: nrdata/savefile.py, nrplanner/inventory.py,
           tests/test_hostile_savefile.py,
           tests/test_save_read_in_the_background.py,
           docs/berichte/T-161-developer.md
           (nrplanner/app.py wurde fuer die Mutationsproben veraendert und
           jeweils aus einer Kopie zurueckgeschrieben — im Git unveraendert,
           siehe "Was am Ende im Baum steht")
ANNAHMEN: siehe Abschnitt "Annahmen"
NAECHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

## Umgesetzt

### 1. QA-215 — AK-245 hat jetzt den Waechter, den es selbst nennt

`tests/test_save_read_in_the_background.py`,
`test_a_takeover_that_works_leaves_load_equippeds_own_sentence` (frueher
`test_a_takeover_that_works_leaves_no_waiting_sentence_either`).

Der Fall hatte drei Behauptungen: die Zeile ist keine Wartezeile, sie ist
nicht leer, sie enthaelt kein Wartewort. Die Bestandsnotiz
(`309 relics in USER_DATA000, 1 stored builds`) erfuellt alle drei — deshalb
blieb die von AK-245 benannte Mutation still. Dazugekommen ist die eine
Behauptung, die die beiden Texte unterscheidet: die Zeile beginnt mit
`"Loaded "`. Das Praefix steht als Literal `LOAD_EQUIPPED_OPENS_WITH` aus dem
Kriteriumstext, **nicht** aus `app.py` gerechnet (L-008 b).

Der Docstring nennt jetzt AK-245 statt AK-244s zweiter Haelfte und traegt die
Begruendung, warum genau diese Zeile die zahnlose Stelle war.

**Rot-vorher, gemessen (nicht behauptet):**

| Lauf | `nrplanner/app.py:4310` | Ergebnis |
|---|---|---|
| 1 (Reproduktion QA-215) | `pass  # MUTATION` | **24 passed** in 100,33 s |
| 2 (Waechter gebaut, unmutiert) | unveraendert | 24 passed in 119,81 s |
| 3 (Waechter gegen dieselbe Mutation) | `pass  # MUTATION` | **1 failed, 23 passed** in 122,27 s |

Die Meldung aus Lauf 3, weil sie die Sache benennt:

```
AssertionError: AK-245: the takeover's own sentence is what stands, not the
note it was written over: '309 relics in USER_DATA000, 1 stored builds'
```

**Welche Aenderung braechte den Test heute zum Brechen** — genau die: der
`setText` im Erfolgszweig von `load_equipped` faellt weg oder schreibt etwas
anderes als den von `load_equipped` gebauten Text. Eine reine
Schnittstellenverschiebung (Umbenennen von `owned_label`, andere Signatur von
`the_line`) braechte ihn auch, ist aber davon getrennt zu lesen: sie braeche
alle 24 Faelle der Datei, nicht diesen einen.

### 2. QA-216 — zwei veraltete Docstrings, nicht einer

Der im Befund genannte ist der Modul-Docstring von
`tests/test_save_read_in_the_background.py` (Zeile 3-6): *"AK-228 is not
covered here … that is V5 and a task of its own."*

**Die Suche nach der Eigenschaft statt nach der Fundstelle (L-006) fand eine
zweite Stelle** in derselben Datei: der Docstring von
`test_every_ending_of_a_read_leaves_a_sentence_of_its_own` (Zeile 350-352)
sagte *"has no ending of its own in this window yet: AD-031 built the way, V5
gives it its sentence"*. Beide sind nachgezogen.

Suchmasken und Trefferzahlen:

| Maske | Treffer | davon veraltet |
|---|---|---|
| `AK-228` ueber alle `*.py` | 9 (in 4 Dateien) | 2, beide korrigiert |
| unabhaengig formuliert: `not covered here\|is not covered\|noch nicht abgedeckt\|has no ending of its own\|no state of this window` | 1 (`tests/test_single_instance.py:13`) | 0 — betrifft das Vordergrundholen eines Fensters, nicht AK-228 |

Die uebrigen sieben `AK-228`-Fundstellen sind zutreffend
(`nrplanner/app.py:642`, `nrplanner/inventory.py:113`,
`tests/test_relic_scan_prefilter.py:293`, die Abschnittsmarke und der
Docstring des abdeckenden Tests, sowie `…:727`, das vom entfernten
Whitelist-Eintrag spricht und richtig bleibt).

**Kein Mutationsbeweis, und warum nicht:** ein Docstring hat keinen
ausfuehrbaren Bruch. Sein Fehler ist sichtbar, sobald jemand die Datei liest,
und die Behauptung ist durch die daneben liegende Testfunktion
(`test_the_slow_way_note_is_said_and_never_a_failure`) belegt, deren Existenz
die Aussage widerlegt. Ein Waechter darauf waere ein Test, der Prosa gegen
Prosa haelt.

### 3. SEC-033 — die Summe, nicht die einzelne Spanne

`nrdata/savefile.py:_members`. Gewaehlt: **eine Schranke auf die Summe der
Mitgliedsgroessen**, geprueft an dem Mitglied, das sie ueberschreitet.

**Warum nicht der vorgeschlagene `offset + size <= len(blob)`:** er bindet
den gemessenen Fall nicht. `offset = 0`, `size = len(blob)` erfuellt die
Pro-Mitglied-Form — und das ist genau die Datei, die der `security-reviewer`
gemessen hat. **Gegengeprueft statt behauptet** (Kontrolle auf derselben
Achse: die Nachbarfassung mitgemessen):

| Fassung | 1 MiB, 200 Mitglieder, jedes beansprucht alles | 8 MiB, 50 Mitglieder, dasselbe |
|---|---|---|
| heute (ohne Schranke) | 200,00 MiB / 2,347 s | 400,00 MiB / 4,267 s |
| **mit `offset + size <= len(blob)`** | **200,00 MiB / 2,068 s** | **400,00 MiB / 3,726 s** |
| mit der Summenschranke | 0,00 MiB / 0,002 s (verweigert) | 0,00 MiB / 0,007 s (verweigert) |

Die Pro-Mitglied-Form aendert an der Verstaerkung **nichts**. Grund: Pythons
Schneiden klemmt ab, statt sich zu beschweren — eine Spanne, die ueber das
Ende hinausgeht, kostet ohnehin nur bis zum Ende. Was kostet, ist die
**Anzahl** der Spannen mal ihre Laenge, und das ist die Summe.

**Kontrolle, dass die Schranke nichts kostet** (dieselbe Achse, ehrlicher
Nachbarwert):

| | vorher | nachher |
|---|---|---|
| 1 MiB, 200 ehrliche Mitglieder | 0,99 MiB / 0,074 s | 0,99 MiB / 0,066 s |
| 8 MiB, 50 ehrliche Mitglieder | 8,00 MiB / 0,096 s | 8,00 MiB / 0,100 s |

**Das Rezept der Schranke.** Sie ist keine gewaehlte Zahl, sondern eine
Struktureigenschaft: BND4-Mitglieder sind disjunkte Spannen des Containers,
also kann ihre Summe die Containergroesse nicht ueberschreiten. Gemessen an
der Grundgesamtheit, die es gibt — **beide** echten Spielstaende dieser
Maschine, `76561198073567627` und `76561198179244962`, je 19 531 312 Byte:
14 Mitglieder, Summe **19 530 432** Byte = **99,9955 %** der Datei; die
restlichen 880 Byte sind Kopf und Namenstabelle. Der Sicherheitsabstand ist
also **null Byte nach oben und 880 Byte nach unten** — enger geht die
Schranke nicht, und weiter braucht sie nicht.

**Messkript und Umgebung:** das Skript liegt im Scratchpad
(`…/scratchpad/T-161/measure.py`) und ist **nicht** versioniert; es baut seine
Container selbst, schreibt sie in den Scratchpad und loescht sie wieder.
Gemessen mit `tracemalloc` (Spitze) und `time.perf_counter`, Windows 10 x64,
`.venv` dieses Baums, gegen den Stand `698490f` plus meine Commits.
**Keine 256-MiB-Probe gefahren** — der Auftrag verbietet sie, und sie wird
auch nicht gebraucht: die Verstaerkung ist Mitgliederzahl mal Dateigroesse
und damit aus den beiden gemessenen Punkten ablesbar.
**Die Fortschreibung des `security-reviewer` (42,7 GiB) habe ich weder
nachgerechnet noch bestaetigt** — sie bleibt seine, als Fortschreibung
gekennzeichnet. Was ich gemessen habe, sind die vier Punkte oben.

### 4. SEC-034 — der absolute Begleiter, aus demselben Rezept

`nrdata/savefile.py`: `MOST_RELIC_RECORDS_A_SLOT_MAY_HOLD = 16384`, geprueft
in `read_owned_relics` **und** in `Inventory._refuse_a_density_no_save_can_have`
— zwei Tueren wie bei SEC-022, weil die Eigenschaft schuetzt und nicht die
Zeile. Die relative Grenze bleibt unveraendert; `limit` ist das Minimum aus
beiden, und die Meldung sagt, welche der beiden gegriffen hat.

**Das Rezept, eines fuer beide Zahlen** (Punkt 3 und 4 gebuendelt, dieselbe
Datei): der Character-Slot, den das Spiel schreibt, ist **1 048 608 Byte**
(aus `savefile.py:165-167`, gemessen an beiden echten Spielstaenden). Die
Dichtegrenze an dieser Groesse gelesen ist `1 048 608 // 64 = 16 384`. Der
absolute Begleiter ist also **die relative Grenze, ausgewertet an der einzigen
Slotgroesse, die das Spiel nachweislich schreibt**. Damit behaelt er genau den
Abstand, den die relative Grenze dort hat: der vollere echte Slot haelt 309
Datensaetze, **Faktor 53** darunter — dieselbe Zahl wie vor der Aenderung.
Grundgesamtheit: 2 Spielstaende, 28 Slots; Stichprobenfehler: keiner, es ist
eine Auszaehlung, keine Schaetzung.

**Gemessen, 1 und 8 MiB, mit Kontrolle auf derselben Achse:**

| Slot | vorher | nachher |
|---|---|---|
| 1 MiB, ein Datensatz je 64 B | 16 384 angenommen, 5,49 MiB, 2,616 s | **unveraendert** 16 384 angenommen, 5,49 MiB, 2,132 s |
| 1 MiB, Dichte des echten Spielstands (3394 B) | 155 angenommen, 0,035 s | 155 angenommen, 0,021 s |
| **8 MiB, ein Datensatz je 64 B** | **131 072 angenommen**, 44,75 MiB, **20,121 s** | **verweigert** nach 16 385, 5,32 MiB, **2,121 s** |
| 8 MiB, Dichte des echten Spielstands | 1 236 angenommen, 0,183 s | 1 236 angenommen, 0,168 s |

Der 1-MiB-Fall ist die Kontrolle, die zeigt, dass die Decke dort **nichts**
kostet: 1 MiB Slot hat genau 16 384 Datensaetze Platz, und alle 16 384 werden
weiterhin gelesen. Erst der groessere Slot faellt darunter — das ist die
Achse, um die es geht.

*(Der Vergleich der Zeiten 2,616 s gegen 2,132 s in der ersten Zeile ist
**keine** Aussage ueber die Kosten meiner Aenderung: beide Laeufe hatten
`tracemalloc` an, und der Unterschied liegt unter dem Faktor 1,4, unterhalb
dessen eine solche Zahl auf dieser Maschine nichts belegt. Die Zeile steht
hier fuer die **Anzahl**, nicht fuer die Sekunden.)*

### 5. SEC-035 — der eine `stat`, der ausserhalb stand

`nrplanner/inventory.py`: neuer `_changed_at(path)` nach dem Vorbild
`nrdata/gamefiles.py:219-223`; `scan` sortiert damit statt mit
`lambda p: p.stat().st_mtime`.

**Eigenschaft statt Fundstelle (L-006).** Alle `stat`-Aufrufe des
Anwendungscodes gezaehlt, mit zwei unabhaengigen Masken
(`\.stat\(\)|os\.stat` und `st_mtime|st_size`): **13 Fundstellen** in
`nrplanner/` und `nrdata/`. Davon auf dem Spielstand-Lesepfad: **5**.

| Fundstelle | Zustand |
|---|---|
| `inventory.py:379` (Sortierschluessel) | **war ungeschuetzt — behoben** |
| `inventory.py:251`, `:254` (`_read_settled`) | im `try` von `_scan_save`, wird zu `SaveNotReadable(strerror)` |
| `app.py:1588` (`_refuse_a_file_no_save_can_be`) | im `try` von `read_the_save:1612` |
| `inventory.py` `p.exists()` in `scan` | `Path.exists` faengt `OSError` selbst ab |

Die uebrigen acht (`datasource.py:104`, `firstrun.py:44`, `:522`,
`extract.py:2806`, `gamefiles.py:165`, `:229`, `iconbuild.py:268`) liegen
**nicht** auf dem Spielstandpfad; sie nennen Spiel- und Cachepfade, nicht den
Steam-Konto-Ordner. `gamefiles.py` und `firstrun.py` gehoeren ausserdem
T-162 — **nicht angefasst**, nur gezaehlt.

**Mit Waechter und mit Beweis, obwohl der Auftrag fuer Punkt 5 keinen
verlangt** — und das war die richtige Entscheidung: der Bruch ist hier
*nicht* sofort sichtbar. Faellt der Fix weg, ist die Wirkung eine rohe
`OSError` in einem Rennen, das kein Testlauf von selbst herstellt. Genau die
Bauform, die still bleibt. Der Test stellt den Zustand her (ein Pfad, der
`exists()` bejaht und bei `stat()` scheitert) statt auf das Rennen zu warten,
und prueft beides, was AK-126 verlangt: die Ausnahme kommt als
`SaveNotReadable` an, und ihr Text enthaelt keinen Pfad.

## Der Mutationsbeweis, vollstaendig

Treiber: `…/scratchpad/T-161/mutate.py`, **nicht versioniert**. Jede Mutation
einzeln, jede aus einer `shutil.copy2`-Kopie zurueckgeschrieben, **nie** mit
`git checkout`. Jede im **Standardlauf** der Datei, ohne Marker und ohne
Sonderkonfiguration (L-008 a).

| Mutation | Datei | Ergebnis |
|---|---|---|
| Summenschranke ganz entfernt | `savefile.py` | **KILLED** — 3 failed, 41 passed |
| Summenschranke ein Byte zu locker (`> len+1`) | `savefile.py` | **KILLED** — 2 failed, 42 passed |
| Summenschranke ein Byte zu streng (`>=`) | `savefile.py` | **KILLED** — 1 failed (die Kontrolle) |
| Decke im Leser ignoriert (`limit = by_density`) | `savefile.py` | **KILLED** — 2 failed (fast + slow) |
| Decke um Faktor 10 angehoben (163840) | `savefile.py` | **KILLED** — 3 failed |
| Decke an der zweiten Tuer ignoriert | `inventory.py` | **KILLED** — 1 failed |
| Sortierschluessel zurueck auf den blanken `stat` | `inventory.py` | **KILLED** — 1 failed |
| `except OSError: return 0.0` entfernt | `inventory.py` | **KILLED** — 1 failed |
| `setText(note)` im Erfolgszweig als No-op (QA-215) | `app.py` | **KILLED** — 1 failed, 23 passed |

**Neun Mutationen, neun tot, keine ueberlebende.** Die acht Eintraege der
Tabelle sind **zweimal** gefahren worden: einmal vor und einmal nach der
Umformung der Verweigerungstexte (`b07a461`), beide Male achtmal KILLED. Der
neunte (`app.py`) ist der Beleg zu Punkt 1 oben.

Jede Schutzmassnahme ist
**einzeln** abgeschaltet worden: die beiden Tueren von SEC-034 getrennt, die
beiden Haelften von SEC-035 (Aufrufstelle und `except`-Zweig) getrennt.

Die Erwartungen der neuen Faelle stehen als **Literale** im Test
(`A_SLOT_WIDER_THAN_THE_GAME_WRITES = 1_048_640`, `ONE_RECORD_TOO_MANY =
16_385`, `LOAD_EQUIPPED_OPENS_WITH = "Loaded "`) und werden nirgends aus der
bewachten Konstante gerechnet — die Mutation "Decke um Faktor 10 angehoben"
belegt das: waere die Erwartung aus `MOST_RELIC_RECORDS_A_SLOT_MAY_HOLD`
gerechnet, waere sie gruen geblieben.

**Keine Zeitschranke in die Suite gebaut.** Die neuen Faelle laufen unter dem
schon vorhandenen `within_time_limit` (10 s, Waechter gegen die
Endlosschleife von SEC-001), das keine Leistung misst. Alle Zeitzahlen dieses
Berichts stammen aus dem Messkript im Scratchpad.

## Tests

Neu: **11 Faelle**, alle in `tests/test_hostile_savefile.py`:

* SEC-033: `test_members_each_claiming_the_whole_file_are_a_data_error`,
  `test_a_member_may_not_claim_more_than_the_file_alone_either`,
  `test_members_that_together_fill_the_file_exactly_still_read` (Kontrolle an
  der Grenze, und es ist die Form des echten Spielstands),
  `test_one_byte_more_than_the_file_holds_is_a_data_error`.
* SEC-034: `test_a_slot_too_large_for_the_density_is_bounded_by_the_count`
  und `test_a_slot_holding_as_many_records_as_a_save_may_is_read_in_full`,
  beide ueber `BOTH_WAYS` (fast und slow) = 4 Faelle; dazu an der zweiten
  Tuer `test_an_inventory_longer_than_any_save_offers_nothing` und
  `test_an_inventory_as_long_as_a_save_may_be_still_offers_its_relics`.
* SEC-035: `test_a_save_that_goes_away_before_it_is_sorted_names_no_path`.

Geaendert: `test_a_takeover_that_works_leaves_load_equippeds_own_sentence`
(umbenannt und um die Praefix-Behauptung erweitert), zwei Docstrings.

**Jede Refusal hat ihre Kontrolle** — kein Fall belegt nur den Fehlerpfad,
weil ein solcher Fall auch gegen einen Leser gruen waere, der alles
verweigert.

Teillaeufe (`pytest <datei>` ohne `-n`, wie `CLAUDE.md` es fuer Gegenproben
verlangt):

* `tests/test_hostile_savefile.py`: **44 passed** in 9,77 s (vorher 33).
* `tests/test_save_read_in_the_background.py`: **24 passed** in 110,61 s
  (vorher 24).
* `tests/test_relic_scan_prefilter.py`: **18 passed** in 1,85 s — nicht
  geaendert, aber es liest `MIN_BYTES_PER_RELIC_RECORD` und die
  Verweigerungstexte mit, also mitgeprueft.

**Volle Suite, vom frischen Klon** (`git clone` des lokalen Repos in den
Scratchpad, damit die uncommitteten Arbeiten paralleler Rollen nicht
mitzaehlen), Stand `44554c3`, `pytest -n auto`, alle drei Verzeichnisse
umgelenkt:

```
1691 passed, 9 skipped in 178.71s (0:02:58)
```

**0 failed.** Gegen die genannte Grundlage 1674/9/0: **+17 Faelle**. Davon
sind **11 meine** — nachgezaehlt, nicht geschaetzt:

| Datei | `698490f` | `b07a461` |
|---|---|---|
| `tests/test_hostile_savefile.py` | 33 (28 `def test_` + 5 `@BOTH_WAYS`) | **44** (37 + 7) |
| `tests/test_save_read_in_the_background.py` | 24 | 24 |

Die uebrigen **6** kommen aus T-162 (`55c441c`, `caa8c11`) — ich habe deren
Dateien weder angefasst noch committet.

### Ein Volllauf hat einen Fehler gefunden, den drei Teillaeufe nicht sahen

**Der erste Volllauf war rot:** `test_the_collector_of_the_texts_really_fires`
(AK-229s Positivkontrolle) fiel, weil meine erste Fassung von SEC-034 den
unterscheidenden Halbsatz in eine Variable `why` **neben** dem `raise` legte.
AK-229s Sammler liest die Texte dieses Pfads per AST **aus dem `raise`
selbst**; ein Halbsatz daneben ist unsichtbar. Das war nicht nur ein roter
Test, sondern eine echte Schwaechung: ein kuenftiger Verweigerungstext haette
in einer solchen Variablen jeden verbotenen Satz tragen koennen, ohne dass
AK-229 ihn sieht.

**Behoben an meiner Stelle, nicht am Waechter** (`b07a461`): jetzt zwei
vollstaendige Saetze, einer je Grenze, jeder ganz im `raise`. Der gemeinsame
Schluss steht dadurch zweimal ausgeschrieben — das ist der Preis dafuer, dass
der Waechter beide sieht, und er steht als Begruendung im Code daneben.

**Warum die Teillaeufe es nicht fanden:** der Sammler wohnt in
`test_save_read_in_the_background.py`, geprueft hatte ich zu dem Zeitpunkt
`test_hostile_savefile.py`. Genau der Fall, fuer den der Volllauf am Ende da
ist. Nach der Reparatur sind alle drei beruehrten Dateien einzeln gruen
(44 / 24 / 18 in `test_relic_scan_prefilter.py`) und die Mutationskampagne
ist **vollstaendig wiederholt** worden — acht von acht weiterhin tot.

## Annahmen

1. **`nrplanner/app.py` wird nicht geaendert.** Punkt 1 verlangt einen
   Waechter, kein Verhalten — das Verhalten ist laut QA-215 heute richtig.
   Die Datei steht auf der Whitelist und wurde nur fuer die Mutationsproben
   angefasst; im Git ist sie unveraendert.
2. **Der Waechter fuer SEC-035 gehoert in `tests/test_hostile_savefile.py`.**
   Die Whitelist nennt zwei Testdateien; die andere
   (`test_save_read_in_the_background.py`) ist der Fensterfaden. Ein Save,
   der zwischen Finden und Sortieren verschwindet, ist ein feindlicher bzw.
   entarteter Dateizustand und gehoert zur ersten.
3. **Die Meldung bei gegriffener Decke ist eine neue Beschriftung** ("more
   records than any save this game writes"). Sie steht in der Reihe der
   vorhandenen Verweigerungen, ist englisch (A8) und nennt weder Pfad noch
   Einheit ohne Bezug (A12: "16 384 relic records", "1048640 bytes"). Der
   `ui-ux-designer` hat sie nicht abgenommen — sie erscheint nur im Fall
   einer praeparierten Datei.
4. **Suitezahl-Grundlage.** Der Auftrag nennt 1674/9/0. Diese Zahl stammt vom
   Stand vor T-162 und T-163; beide haben waehrend meines Laufs auf denselben
   Branch committet. Mein Klon steht auf `44554c3` und enthaelt ihre Arbeit.
   Die Differenz ist deshalb **nicht** allein meine — siehe unten.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests gruen in der benannten Testumgebung (Windows 10 x64)
- [x] Neue Tests fuer neue Logik; **Linter: das Projekt hat keinen
      konfiguriert** — der Punkt entfaellt (kein Mangel, keine Ersatzpruefung)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] QA-Akzeptanzkriterien selbst durchgespielt (AK-245, AK-228, AK-126)
- [x] Bericht geschrieben
- **Ungeprueft:** Linux und macOS (kein Ziel, nie geprueft). Kein gebautes
  Artefakt, kein echtes Fenster — die drei Vorbehalte aus T-159 (AK-110,
  AK-129, AK-131) bleiben ungeprueft und waren nicht mein Auftrag.

## Datenschutz und Umlenkungen — nachgewiesen

Alle drei Umlenkungen gesetzt und **einzeln belegt**, nicht zugesichert:

```
NIGHTREIGN_SETTINGS_ORG = DankYeeterT-161  ->  favourites.ORG = DankYeeterT-161
LOCALAPPDATA            = …/scratchpad/T-161/appdata/Local
    paths.cache_dir()   = …\scratchpad\T-161\appdata\Local\NightreignHelper
    snapshot exists     = True
APPDATA                 = …/scratchpad/T-161/appdata/Roaming
    shortcut.start_menu_dir()
                        = …\scratchpad\T-161\appdata\Roaming\Microsoft\Windows\Start Menu\Programs
```

Testabzug **kopiert**, nicht daraufgezeigt: 841 Dateien, 22 MB, nach
`…/scratchpad/T-161/appdata/Local/NightreignHelper`. `EXTRACT_VERSION` ist
weiterhin 11, der Abzug bleibt gueltig.

*Anmerkung fuer den naechsten Lauf:* `savefile.find_saves` faellt nach
`Path.home()/AppData/Roaming` zurueck, wenn `%APPDATA%` woanders zeigt. Die
Umlenkung von `APPDATA` schuetzt also das Startmenue, versteckt die
Spielstaende aber **nicht** — das ist gut so (die Suite braucht sie
lesend), muss man aber wissen, sonst haelt man die Umlenkung fuer wirkungslos.

**Spielstand read-only, gegengeprueft:**

| Datei | vorher | nachher |
|---|---|---|
| `…\76561198073567627\NR0000.sl2` | 19 531 312 B, sha256 `884c16fd307f838f…` | **identisch** |
| `…\76561198179244962\NR0000.sl2` | 19 531 312 B, sha256 `53c7edf21363d0b1…` | **identisch** |

## Was am Ende im Baum steht

`git status` sauber. Drei Commits, jeder mit Pfad hinter `--`, keiner mit
`-a`, `add .` oder `add -A`:

| Commit | Inhalt |
|---|---|
| `f72f93e` | `test(save)`: QA-215 und QA-216, nur `tests/test_save_read_in_the_background.py` |
| `54618cd` | `fix(savefile)`: SEC-033 und SEC-034 |
| `f645c01` | `fix(inventory)`: SEC-035 |
| `b07a461` | `fix(savefile)`: die neuen Verweigerungen tragen ihren Satz im `raise` (AK-229) |

SEC-035 ist bewusst **von** SEC-033/034 getrennt, obwohl beide dieselben zwei
Dateien beruehren: dafuer wurden die SEC-035-Teile kurz beiseitegelegt
(Kopie im Scratchpad), der erste Commit gesetzt und die Kopie
zurueckgeschrieben. Kein `stash`, kein `checkout`.

**Scratchpad aufgeraeumt, geprueft statt zugesichert.** Entfernt: der Klon,
die Kopie des Testabzugs (22 MB) und die vier `.orig`/`.with035`-Kopien.
Uebrig sind nur `env.sh`, `measure.py`, `mutate.py` (`ls` bestaetigt), und
auch die stehen in einem Temp-Verzeichnis und ueberleben die Sitzung nicht
zuverlaessig. Sollen sie bleiben, waere `scripts/differential/` der Ort —
**Entscheidung des `director`**; ich habe nichts dorthin gelegt, `scripts/`
steht auf der Nicht-anfassen-Liste.

Kein Dienst, kein Port, kein Hintergrundprozess gestartet; die
Mutationslaeufe waren `subprocess.run` im Vordergrund. Das echte Startmenue
(`%APPDATA%\Microsoft\Windows\Start Menu\Programs`) enthaelt **keinen**
Nightreign-Eintrag — nachgesehen, nicht angenommen.

## An qa-engineer

**Was zu testen ist:**

* **AK-245 am echten Fenster.** Mein Waechter faehrt durch die
  `StatedRead`-Naht, nicht durch einen echten Spielstand. Die vierte
  Vorrichtung (uebernehmbares Build) ist gestellt; am gebauten Programm ist
  offen, ob die Zeile bei einem echten ersten Lesen dasselbe zeigt.
* **Die neue Verweigerungsmeldung** ("more records than any save this game
  writes") landet auf demselben Weg im Fenster wie die Dichte-Meldung
  (`Inventory.loadout_error` bzw. `SaveNotReadable`). Wert zu pruefen: kein
  Dialog, keine Farbe ausser MUTED, kein Pfad.
* **Der echte Spielstand liest weiterhin vollstaendig** — 309 bzw. 234
  Relikte, 110 Builds. Das ist die Kontrolle, die meine beiden neuen
  Schranken am wenigsten schuldig bleiben duerfen. Ich habe die **Geometrie**
  beider Dateien gelesen (14 Mitglieder, Summe 99,9955 %), aber **keinen
  vollen Programmstart** gefahren.

**Randfaelle, die ich kenne und die offen bleiben:**

1. **Ein Mitglied mit `offset` hinter dem Dateiende** wird von der
   Summenschranke **nicht** gefangen, wenn seine `size` klein ist
   (`offset = 10^9`, `size = 4`). Das Schneiden liefert dann leere Bytes und
   `AES.new(…, iv=b"")` wirft einen `ValueError` — also eine Datenfehlermeldung
   und kein Absturz, aber der Text kommt aus `pycryptodome`, nicht von uns.
   **Das war vor meiner Aenderung genauso**; es ist kein Regress, aber es ist
   eine offene Kante, und ich habe sie bewusst nicht mitbehoben (Punkt 3
   verlangte eine Schranke, nicht zwei).
2. **Ein Character-Slot ueber 1 048 608 Byte** — sollte ein Spielpatch ihn
   vergroessern, bindet ab dann die absolute Decke statt der relativen. Bei
   309 echten Datensaetzen ist der Abstand Faktor 53; erst ein Slot mit mehr
   als 16 384 echten Relikten braeche das. Steht so im Kommentar.
3. **`Path.exists()` in `scan`** faengt `OSError` selbst ab; ein Pfad, der
   dabei scheitert, faellt lautlos aus der Liste. Das ist heutiges Verhalten
   und war nicht Teil von SEC-035.

## An ui-ux-designer

Eine neue Beschriftung, ohne Abnahme gebaut, weil sie nur bei praeparierten
Dateien erscheint und in einer bestehenden Satzform steht:

> `a save slot of {n} bytes holds more than {limit} relic records, more
> records than any save this game writes, which is not an inventory; the file
> is damaged or was not written by the game. Take it out of the save folder
> and rescan.`

Sie ersetzt in genau dem Fall den Halbsatz *"denser than one record per 64
bytes"*; alles davor und danach ist unveraendert. **Bitte gegenlesen** — wenn
der Satz anders lauten soll, ist es eine Zeile in `savefile.py` und eine in
`inventory.py`, und die Tests haengen am Teilstring "more records than any
save this game writes".

## An director

**Befunde, die ich melde statt zu beheben** (Titel und Fundstelle, keine
Nummer):

1. **Die Begruendung des `security-reviewer` zu SEC-033 ist widerlegt.** Sein
   bevorzugter Fix (`offset + size <= len(blob)`) bindet den von ihm selbst
   gemessenen Fall nicht — gemessen, siehe Tabelle oben: dieselben 200,00 MiB
   und 400,00 MiB. Das ist kein Vorwurf, sondern ein Hinweis fuer den
   Retest: **wer SEC-033 abnimmt, muss die Summe pruefen, nicht die Spanne.**
2. **Offene Kante, `nrdata/savefile.py:decrypt_member`:** ein Mitglied mit
   Offset hinter dem Dateiende erzeugt eine `ValueError` aus `pycryptodome`
   ("Incorrect IV length"), also einen Fremdtext im Fenster statt einer
   eigenen Meldung. Aufwand: eine Zeile plus Test. Risiko: niedrig, der Text
   nennt keinen Pfad. **Bestand, kein Regress.**
3. **Zwei Docstrings statt einem bei QA-216** — der Befund nannte einen, die
   Eigenschaftssuche fand zwei. Beide behoben; die Nummer QA-216 deckt jetzt
   mehr, als ihr Text sagt.
4. **Eigener Fehler, gemeldet statt verschwiegen:** meine erste Fassung von
   SEC-034 hat AK-229s Sammler blind gemacht (Halbsatz in einer Variablen
   neben dem `raise`). Der Volllauf hat es gefunden, `b07a461` behebt es.
   **Der Waechter selbst wurde nicht angefasst.** Wert fuer die Regelpflege:
   *jede neue Verweigerung auf dem Lesepfad traegt ihren ganzen Satz im
   `raise`* — das ist heute nur ein Kommentar an zwei Stellen und kein
   Waechter. Ein Test, der `ast`-sichtbare gegen tatsaechlich erzeugte Texte
   haelt, waere das Mittel dagegen; **das ist ein eigener Auftrag, nicht
   meiner.**

**Kein Sicherheitsfund darueber hinaus.** Kein Netzzugriff, kein Secret, kein
Schreiben in Spielstand oder Spielinstallation.

**Performance:** nichts fuer den `performance-tuner`. Die einzige Zahl, die
sich bewegt, bewegt sich in die richtige Richtung (8-MiB-Fall von 20,121 s
auf 2,121 s) und ist Folge einer Verweigerung, keiner Optimierung.

**Zur Suitezahl.** Der Auftrag nennt 1674/9/0 als Grundlage. Waehrend meines
Laufs haben T-162 und T-163 auf denselben Branch committet
(`55c441c`, `caa8c11`, `b1a2776`, `44554c3` und der UI_SPEC-Commit). Meine
elf neuen Faelle sind **11**; alles darueber hinaus gehoert den
Nachbarlaeufen. Ich habe die Zahl vom frischen Klon auf `44554c3` gemessen,
nicht aus dem Arbeitsbaum — dort haetten ihre uncommitteten Dateien
mitgezaehlt.
