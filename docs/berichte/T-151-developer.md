# T-151 - V4: der langsame Weg kommt zurueck (developer)

```
STATUS: erledigt
AUFTRAG: T-151 - V4 (AD-031): der langsame Weg kommt zurueck
GELESEN: docs/tasks/T-151.md; ARCHITECTURE.md Nachtrag XI (AD-031 ganz,
         Umsetzungstabelle V1-V5, R12-R16, "Was der developer nicht tun soll");
         UI_SPEC.md AK-228/AK-229 und Nachtrag "drei Praezisierungen" §3;
         docs/berichte/T-133-developer.md (Gleichheitsprobe, Positivkontrolle);
         nrdata/savefile.py, nrplanner/inventory.py, nrplanner/paths.py,
         nrplanner/favourites.py, nrplanner/shortcut.py, tests/conftest.py,
         tests/test_relic_scan_prefilter.py, tests/test_hostile_savefile.py,
         tests/test_save_read_in_the_background.py,
         tests/test_differential_track.py, scripts/differential/mutate.py
GEÄNDERT: nrdata/savefile.py, nrplanner/inventory.py,
          tests/test_relic_scan_prefilter.py, tests/test_hostile_savefile.py
          (Commit b575d1d); tests/test_save_read_in_the_background.py
          (Commit ea1de90); docs/berichte/T-151-developer.md (diese Datei)
ANNAHMEN: 1. `tests/test_hostile_savefile.py` gehoert zum Auftrag, obwohl die
          Datei in der Auftragszeile "Beruehrt Dateien" fehlt - R16 nennt sie
          namentlich. 2. `tests/test_save_read_in_the_background.py` ebenso:
          `UI_SPEC` T-148 §3 verlangt woertlich, dass wer AK-228 baut, den
          Whitelist-Eintrag "in derselben Aenderung" entfernt; ohne das waere
          die Suite rot. Beides unten unter "Abweichungen" mit Begruendung.
          3. `mode` ist als Schluesselwort-Argument gebaut (`*, mode=...`),
          nicht positionsfaehig.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**`nrdata/savefile.py`**

- `_every_fourth_offset(slot_data)` - der zweite Versatz-Erzeuger, der alte
  Walk. Gleiche Schrittweite 4, gleiche obere Grenze
  (`len - RELIC_FIELDS_SIZE`, exklusiv) wie `_relic_id_offsets`.
- `FAST, SLOW = "fast", "slow"` und `_OFFSETS_OF_MODE` - die Zuordnung Name →
  Erzeuger.
- `relic_scan_mode(valid_relic_ids)` - `SLOW` ab `>= RELIC_ID_CEILING`, sonst
  `FAST`. Woertlich die Form aus AD-031.
- `read_owned_relics(..., *, mode: str | None = None)` - `None` heisst "selbst
  fragen". Ein unbekannter Wert wird abgelehnt (`ValueError`), statt auf einen
  der beiden Wege zu raten. **Rumpf unveraendert**: Doppel-Id, Id-Gueltigkeit,
  `seen_offsets`, Effekte, Fluechte und die Dichteschranke SEC-022 sind einer
  und werden von beiden Wegen gelaufen; geaendert ist die eine Zeile
  `for off in offsets_of(slot_data)`.
- `_check_the_prefilter_can_see_every_id` **entfaellt** samt Verweigerung.

**`nrplanner/inventory.py`**

- `Inventory.read_the_slow_way: bool = False` und
  `SaveScan.read_the_slow_way: bool = False`.
- `scan()` fragt `relic_scan_mode` **einmal je Ladevorgang** und reicht die
  Antwort durch; `_scan_save(..., *, mode)` gibt sie an jeden
  `read_owned_relics`-Aufruf weiter und setzt das Feld auf `SaveScan`;
  `build()` traegt es auf das `Inventory`.
- `load()` bricht nicht frueher ab, `RELIC_ID_CEILING` unveraendert, SEC-022
  in beiden Wegen nicht angefasst.

**Nicht angefasst:** `nrplanner/app.py`, `UI_SPEC.md`, `ARCHITECTURE.md`,
`GOAL.md`, `docs/state.md`, `qa/findings.md`, `docs/tasks/`,
`scripts/differential/mutate.py` (Mutationsregister, laut Auftrag ausserhalb
des Scope - **hat Folgen, siehe "An den director" Punkt 1**).

## Der langsame Weg ist belegt gleichwertig, nicht nur vorhanden

Skript `…/scratchpad/T-151/equal_both_ways.py`, **nur lesend**, gegen die zwei
echten `.sl2` auf dieser Maschine. Verglichen wird je Record
`(relic_id, offset, effect_ids, curse_ids)`, nicht nur die Anzahl.

```
dataset: 849 relic ids, largest 2013322, mode chosen for it: fast
C:\Users\Daniel\AppData\Roaming\Nightreign\76561198073567627\NR0000.sl2   19531312 B
C:\Users\Daniel\AppData\Roaming\Nightreign\76561198179244962\NR0000.sl2   19531312 B
-> 28 decrypted slots, 39060416 bytes

  NR0000.sl2/USER_DATA000: 234 fast / 234 slow -> equal
  NR0000.sl2/USER_DATA000: 309 fast / 309 slow -> equal

28 of 28 slots equal, 543 records found in total
fast 87.6 ms, slow 5509.1 ms, over all 28 slots (one run, this machine)
positive control (one record dropped from the best-populated slot, 309 records): DIFFERENT
```

**28 von 28 Slots, 543 Records** - dieselbe Grundgesamtheit, gegen die T-133
gemessen hat, und dieselben Zahlen. **Positivkontrolle:** derselbe Vergleich um
einen Record gekuerzt meldet `DIFFERENT`, der Vergleich ist also nicht blind.

**Zur Zeitzeile (L-001/L-009):** ein einziger Lauf, kein Median, dieser Rechner,
Slots im Speicher, ohne Entschluesselung gemessen; sie steht hier als
Groessenordnung fuer die Kosten des Rueckfalls (AD-031 nennt 657,2 → 6147,6 ms
fuer `inventory.load` insgesamt) und **nicht** als Schranke. **Keine
Zeitschranke ist in die Suite gewandert.**

## Tests

**`tests/test_relic_scan_prefilter.py`** (13 → 18 Faelle)

- **R12:** `both_scans_agree` laeuft jeden Fall **zweimal**, `mode=FAST` und
  `mode=SLOW`, je gegen das unabhaengige `full_walk`. `full_walk` ist
  unveraendert geblieben und **nicht** in den Produktivcode gewandert; die
  beiden Wege werden nie gegeneinander gehalten, immer nur gegen es.
- **R13:** `test_the_choice_is_made_at_three_stated_ids` - die drei Literale
  aus dem Auftrag, plus der leere Datensatz. Keine Erwartung ist aus
  `RELIC_ID_CEILING` gerechnet.
- **R14:** `test_an_id_above_the_ceiling_is_read_the_slow_way_and_not_refused`
  **ersetzt** `test_a_relic_id_above_the_ceiling_is_refused_out_loud`; der
  Docstring nennt, was er abloest. Drei Records ueber der Decke, Anzahl und
  Offsets gegen Literale, dazu die Kontrolle, dass der **schnelle** Weg auf
  demselben Slot **nichts** findet - sonst koennte der Fund von irgendwoher
  kommen.
- **R15:** `test_an_inventory_read_the_slow_way_says_so` /
  `..._the_fast_way_says_that_too` / `test_an_inventory_nobody_read_makes_no_claim_about_a_way`.
  Zusaetzlich `test_the_way_is_chosen_once_for_a_load_and_not_once_per_slot` -
  Zaehlwert 1 ueber drei Slots, weil "einmal je Ladevorgang" in keinem Ergebnis
  sichtbar ist (AD-031 Punkt 1).
- Dazu `test_a_mode_that_is_neither_way_is_refused_rather_than_guessed`.
- **Entfallen:** `test_the_refusal_says_the_program_is_too_old_and_names_no_file`
  (prueft den Wortlaut der geloeschten Verweigerung). **Die
  SEC-023-Eigenschaft "kein Pfad in einer Meldung dieses Moduls" bleibt
  gedeckt** durch `test_hostile_savefile.py::test_the_refusal_over_a_packed_slot_names_no_file_path`
  und `..._over_packed_table_starts_...`.

**`tests/test_hostile_savefile.py`** (R16, 28 → 33 Faelle): die fuenf
Dichtefaelle laufen ueber `BOTH_WAYS` je zweimal, `FAST` und `SLOW`.

**`tests/test_save_read_in_the_background.py`**: siehe "Abweichungen".

## Mutationsbeweis - 13 Mutationen, 13 tot, keine Ueberlebende

Treiber `…/scratchpad/T-151/mutate.py`, jede Mutation eine exakte
Ersetzung im Produktivcode, Datei vorher zur Seite kopiert und danach
zurueckkopiert (kein `git checkout`). Alle im **Standardlauf**, ohne
Sonderkonfiguration. Ausgabe vollstaendig in
`…/scratchpad/T-151/mutations.out`.

| # | Mutation | faellt |
|---|---|---|
| R12a | langsamer Erzeuger Schrittweite 4 → **8** | `test_the_last_record_the_walk_does_reach_is_read`, `test_an_id_carrying_the_flag_byte_inside_itself_is_still_found` (2 failed) |
| R12b | langsamer Erzeuger **ohne Ausrichtung** (Schrittweite 1) | `test_a_doubled_id_off_the_four_byte_grid_is_not_a_record` |
| R12c | langsamer Erzeuger endet **eine Position spaeter** | `test_a_record_at_the_walks_own_upper_bound_is_not_read` |
| R13 | `>=` → `>` in `relic_scan_mode` | `test_the_choice_is_made_at_three_stated_ids` |
| R14 | **Verweigerung wieder eingesetzt** (`raise`, alter Wortlaut) | `..._is_read_the_slow_way_and_not_refused`, `test_an_inventory_read_the_slow_way_says_so`, **und** `test_the_collector_of_the_texts_really_fires`, `test_no_text_behind_the_prefix_says_the_save_is_fine` (AK-229) |
| R14b | `mode is None` → immer `FAST` | `..._is_read_the_slow_way_and_not_refused` |
| R15a | `read_the_slow_way` auf `SaveScan` fest `False` | `test_an_inventory_read_the_slow_way_says_so` |
| R15b | `build()` traegt das Feld nicht weiter | dieselbe |
| R16 | Dichteschranke nur im schnellen Zweig (`and mode == FAST`) | `test_a_slot_that_is_nothing_but_the_searched_byte_is_still_refused` **und drei `[slow]`-Faelle** in `test_hostile_savefile.py`; die `[fast]`-Faelle bleiben gruen, wie es sein muss |
| – | unbekannter `mode` faellt still auf den schnellen Weg zurueck | `test_a_mode_that_is_neither_way_is_refused_rather_than_guessed` |
| – | Wahl **je Slot** statt je Ladevorgang | `test_the_way_is_chosen_once_for_a_load_and_not_once_per_slot` |
| FASTa | `bytes.find` beginnt bei 4 statt 3 | 6 Faelle, u. a. `test_a_record_at_the_very_first_offset_is_found` |
| FASTb | Ausrichtungspruefung des schnellen Erzeugers entfernt | `test_a_doubled_id_off_the_four_byte_grid_is_not_a_record` |

FASTa/FASTb stehen dabei fuer die Frage, ob der **alte** Waechter das
Zweimal-Laufen ueberlebt hat: er beisst unveraendert.

**Rot-vorher, getrennt von Schnittstellenverschiebung:** R12a-c, R13, R14b,
R15a/b, R16 und die beiden namenlosen aendern **nur Verhalten**, keine
Signatur - die Faelle werden rot, weil das Ergebnis anders ist, nicht weil ein
Aufruf nicht mehr passt. R14 fuegt eine Zeile hinzu und aendert ebenfalls keine
Signatur.

## Testumgebung, Umlenkungen, Spielstand

Windows 10 x64, Branch `docs/audit-and-advisor-design`, `.venv`-Python.

**Alle drei Umlenkungen gesetzt und jede mit einem Schreibvorgang belegt** (die
blosse Pfadausgabe belegt nur, wohin gezeigt wird, nicht, wo geschrieben wird):

| Variable | Wert | Nachweis |
|---|---|---|
| `LOCALAPPDATA` | `…/scratchpad/T-151/local` | `paths.cache_dir()` zeigt dorthin; geschriebene Datei `T-151-redirect-control.txt` liegt dort |
| `APPDATA` | `…/scratchpad/T-151/roaming` | `shortcut.shortcut_path()` zeigt dorthin; dort geschriebene `Nightreign Helper.lnk` liegt dort - im **echten** Start-Menue liegt keine (geprueft) |
| `NIGHTREIGN_SETTINGS_ORG` | `DankYeeterT-151` | `QSettings(...).fileName()` = `\HKEY_CURRENT_USER\Software\DankYeeterT-151\NightreignHelper`; geschriebener Wert `T-151/redirect-control` dort per `reg query` gefunden. Schluessel danach geloescht |

Der feste Testabzug wurde nach `…/scratchpad/T-151/local/NightreignHelper`
**kopiert** (841 Dateien), nicht darauf gezeigt.

**Spielstand read-only, gegengeprueft:** sha256, Groesse und mtime beider
`.sl2` vor dem ersten und nach dem letzten Lauf identisch
(`save_before.txt` / `save_after2.txt`, `diff` leer). Es wurde nur gelesen.

## Suitezahl

```
pytest -n auto   ->   2 failed, 1582 passed, 9 skipped in 158.72s
```

Gegen T-149 (**1550 passed, 9 skipped, 0 failed**) geht die Rechnung genau auf:
1550 + 10 (meine: Vorfilterdatei +5, `test_hostile_savefile` +5 durch die
Parametrisierung) + 24 (`tests/test_save_path_memory.py`, **neu und
uncommittet von T-150**, laeuft parallel im selben Arbeitsbaum) - 2
(die zwei roten, siehe unten) = 1582.

**Die zwei roten Faelle sind eine Folge meiner Aenderung in einer Datei, die
ich laut Auftrag nicht anfassen darf** - Punkt 1 an den director.

Beide Faelle:
`tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source[the-id-ceiling-is-never-checked]`
und `[the-id-ceiling-looks-at-the-smallest-id]`.

**Einmalig gesehen, nicht reproduzierbar, nicht meins:**
`tests/test_save_path_memory.py::test_a_picked_save_with_relics_reads_as_one_always_did`
fiel im **ersten** vollen Lauf. Geprueft: mit meinen Aenderungen einzeln gruen
und in seiner Datei gruen (24 passed), im zweiten vollen Lauf gruen; die
Fehlermeldung betrifft die Zeile, die `load_equipped` ueber die Bestandsnotiz
schreibt, nicht den Scan. Ich halte es fuer eine Reihenfolgeabhaengigkeit in
der noch laufenden Arbeit von T-150 und melde es dorthin, ohne es zu bewerten.

## Abweichungen vom Auftrag (beide mit Beleg, keine stillschweigende)

1. **`tests/test_hostile_savefile.py` angefasst**, obwohl die Zeile "Beruehrt
   Dateien" nur drei Dateien nennt. **R16 nennt genau diese Datei** ("vorhanden,
   erweitert") und verlangt die Dichtefaelle auf beiden Wegen. Ohne sie waere
   R16 nicht erfuellt.
2. **`tests/test_save_read_in_the_background.py` angefasst.** Der Waechter aus
   T-142 fuehrte `_check_the_prefilter_can_see_every_id` als **befristeten
   Whitelist-Eintrag** und dazu eine Positivkontrolle, deren Docstring bereits
   sagt: *"When AK-228 lands this case must go, together with the exception it
   names."* `UI_SPEC` T-148 §3 sagt es noch deutlicher: *"wer AK-228 baut,
   entfernt beides in derselben Aenderung."* Haette ich es gelassen, waere die
   Suite rot gewesen.
   **Wichtig, weil ein Waechter dabei zahnlos werden konnte:** die alte
   Positivkontrolle *war* der Ausnahmefall. Faellt sie ersatzlos, prueft der
   Waechter die leere Menge - und die liefert ein Sammler, der nichts mehr
   sammelt, genauso. Die neue Kontrolle steht deshalb auf zwei Beinen, die
   keine Fundstelle brauchen: (a) der Sammler findet den SEC-022-Text in
   `read_owned_relics`, (b) die Wortliste schlaegt auf dem Wortlaut an, den
   AD-031 vom Pfad genommen hat, und schlaegt auf dem SEC-022-Text **nicht**
   an. **Beleg, dass das beisst:** Mutation R14 (Verweigerung wieder
   eingesetzt) macht **beide** AK-229-Faelle rot.
   Ausserdem zwei Docstrings derselben Datei, die behaupteten, den langsamen
   Weg gebe es im Quelltext nicht - das stimmt seit dieser Aenderung nicht
   mehr. Die Bestandszeile dazu bleibt V5.

## Eigenschaft statt Fundstelle (L-006)

Nach dem Entfernen der Verweigerung ueber den ganzen Baum gesucht, mit zwei
unabhaengig formulierten Masken:

- Maske A, Bezeichner `_check_the_prefilter_can_see_every_id`: **3 Treffer**,
  keiner im Anwendungscode - `scripts/differential/mutate.py:4085` (das
  Register, Punkt 1 unten), `tests/test_save_read_in_the_background.py:651`
  (der neue Kontrolltext, absichtlich), `.claude/agent-memory/ui-ux-designer/…`
  (fremdes Gedaechtnis, nicht meins).
- Maske B, Wortlaut `nothing is wrong with the save|too old to read|renumbered
  its relics` ueber alle `.py`: **2 Treffer**, beide dieselbe Konstante des
  neuen Kontrolltextes. Im Anwendungscode **null**.
- Maske C, Aufrufstellen `read_owned_relics` ausserhalb `tests/` und
  `savefile.py`: **eine** (`nrplanner/inventory.py:397`), und die uebergibt
  `mode`.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests gruen in der benannten Umgebung - **bis auf die zwei
      Register-Anker**, die ich nicht beheben darf (Punkt 1)
- [x] Neue Tests fuer neue Logik; Mutationsbeweis vollstaendig, keine
      Ueberlebende
- [ ] Linter: **entfaellt**, das Projekt hat keinen konfiguriert (weder
      `.flake8`, `setup.cfg`, `ruff.toml`, `pyproject.toml` noch `.pylintrc`;
      `requirements-dev.txt` nennt keinen)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Linux/macOS **ungeprueft** und kein Ziel (CLAUDE.md)
- [x] Bericht geschrieben

## An den director

1. **Das Mutationsregister ist an zwei Ankern rot, und ich darf es nicht
   anfassen** (Auftrag: "Nicht: … das Mutationsregister").
   `scripts/differential/mutate.py` haelt vier Mutationen zur Id-Decke; zwei
   davon ankern auf der geloeschten Funktion und finden ihren Anker nicht mehr:
   - `the-id-ceiling-is-never-checked` (Anker: die Aufrufzeile
     `_check_the_prefilter_can_see_every_id(valid_relic_ids)`),
   - `the-id-ceiling-looks-at-the-smallest-id` (Anker:
     `biggest = max(valid_relic_ids, default=0)`).
   Die anderen beiden (`…-is-raised-past-its-assumption`,
   `…-drops-below-the-games-own-ids`) ankern auf `RELIC_ID_CEILING = 0x01000000`
   und bleiben gruen, **aber ihr `survival_means`-Text nennt Faelle, die es
   nicht mehr gibt** (`test_a_relic_id_above_the_ceiling_is_refused_out_loud`,
   `test_the_refusal_says_the_program_is_too_old_and_names_no_file`,
   `test_the_largest_id_the_prefilter_can_see_is_read_in_full`,
   `test_the_games_own_relic_ids_are_all_below_the_ceiling`) - sie sind also
   nicht kaputt, aber sie beschreiben einen Stand, den es nicht mehr gibt.
   **Empfehlung:** ein kleiner Folgeauftrag, der die zwei toten Eintraege durch
   die 13 Mutationen dieses Berichts ersetzt (Anker und Ergebnisse stehen in
   `…/scratchpad/T-151/mutate.py` und `mutations.out`, generiert und nicht
   abgetippt) und die `survival_means`-Texte der zwei ueberlebenden auf die
   neuen Fallnamen zieht. Solange das offen ist, meldet die Suite **2 failed**.
2. **A7 ist bis V5 noch nicht geschlossen.** Der Rueckfall laeuft und steht auf
   dem Bestand, **aber niemand sagt es dem Spieler** - `nrplanner/app.py` liest
   `Inventory.read_the_slow_way` nicht (geprueft: die Zeichenkette kommt in
   `nrplanner/` nur in `inventory.py` vor). Genau die Luecke, die Nachtrag XI
   beim Schnitt "V4 vor V5" vorhergesagt hat. V5 sollte zeitnah folgen.
3. **Performance-Fund, kein Tuning-Auftrag von mir:** faellt der Rueckfall,
   kostet der reine Record-Scan ueber 28 Slots 5509,1 ms statt 87,6 ms (ein
   Lauf, diese Maschine, Slots im Speicher). Im Hauptthread waere das ein
   eingefrorenes Fenster; die Lesespur aus AD-029 Stufe B ist damit die
   Bedingung, unter der der Rueckfall ertraeglich ist. Falls jemand die Zahl
   als Kennwert braucht, gehoert sie mit Median und Streuung gemessen -
   **empfohlen: `performance-tuner`**, nicht ich.
4. **Sicherheitsfunde: keine.** SEC-022 ist unangetastet und in **beiden**
   Wegen belegt (R16 plus Mutation R16). Die zweite Dichtepruefung in
   `Inventory._refuse_a_density_no_save_can_have`, die Deckel aus SEC-002 und
   `RELIC_ID_CEILING` sind unveraendert. **SEC-029** (das `stat().st_size` vor
   `read_bytes()` in `inventory.py`) ist **nicht** eingebaut - von T-150 kam
   keine Zeile, und ohne Auftrag baue ich sie nicht. Steht weiterhin offen.
5. **Bestehende Debt, nicht behoben, nur gemeldet:** `docs/state.md`,
   `qa/findings.md` und `ARCHITECTURE.md` (Nachtrag XI, V4-Zeile) beschreiben
   V4 noch als offen; `UI_SPEC` T-148 §3 traegt einen Vermerk, der mit dieser
   Aenderung hinfaellig geworden ist ("Landet V4/AK-228, ist der Vermerk
   hinfaellig"). Das sind fremde Dateien, ich habe sie nicht angefasst.

## An den qa-engineer

- **Was zu testen ist:** dass ein Spielstand auf beiden Wegen dieselbe
  Reliktzahl ergibt. Der billigste Aufbau ist der aus
  `test_relic_scan_prefilter.py`: `read_owned_relics(..., mode=savefile.SLOW)`
  gegen `mode=savefile.FAST` am echten Spielstand - **read-only**, mein Skript
  `…/scratchpad/T-151/equal_both_ways.py` tut genau das und braucht nur die
  drei Umlenkungen.
- **Kanten, die ich absichtlich so gebaut habe:** unbekannter `mode` wird
  abgelehnt statt geraten; `relic_scan_mode(set())` ist `FAST`; ein
  handgebautes `Inventory` sagt `read_the_slow_way is False`, ohne dass jemand
  gelesen haette.
- **Wo ich eine Luecke lasse:** AK-228 ist damit **nicht** abnehmbar - der Satz
  im Fenster fehlt, das ist V5 (siehe Punkt 2 oben). Wer AK-228 heute prueft,
  prueft die Haelfte, die gebaut ist.
- **Nicht mehr vorhanden:** `test_a_relic_id_above_the_ceiling_is_refused_out_loud`
  und `test_the_refusal_says_the_program_is_too_old_and_names_no_file`. Wer
  eine Regression an "kein Pfad in einer Fehlermeldung" sucht, findet sie in
  `test_hostile_savefile.py`.

## An den ui-ux-designer

Keine Abweichung von einer Vorgabe. Zwei Meldungen:

- Der Rueckfallweg, den du in T-141 §13 Punkt 2 als fehlend gemeldet hast,
  **existiert jetzt**, und der Bestand traegt `Inventory.read_the_slow_way`.
  Die Voraussetzung von AK-228 steht damit.
- Der befristete Whitelist-Eintrag aus deinem Vermerk (T-148 §3) ist entfernt;
  AK-229 zweite Haelfte gilt jetzt **ohne** Ausnahme, und der Waechter prueft
  die leere Menge mit einer Positivkontrolle, die nicht mehr an einer
  Fundstelle haengt. Der Selbstwiderspruch aus §8 kann einen echten Spieler
  nicht mehr treffen: es gibt keinen Text mehr, der sagt, mit dem Spielstand
  sei alles in Ordnung, und gleichzeitig hinter `Save could not be read: `
  landen kann.

## Offene Fragen

Keine, die mich blockiert haetten. Die zwei Entscheidungen, die ich gebraucht
haette und selbst getroffen habe, stehen oben unter "Abweichungen" - beide mit
dem Zitat, auf das ich mich gestuetzt habe.
