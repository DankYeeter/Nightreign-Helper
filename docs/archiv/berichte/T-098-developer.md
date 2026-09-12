# T-098 - Der Rest von T-097: Gegenbauten, Suite, Commits, Bericht (developer)

```
STATUS: erledigt
AUFTRAG: T-098 - Gegenbauten, Suite-Laeufe, Commits und Bericht zu SEC-022
GELESEN: docs/tasks/T-098.md, docs/tasks/T-097.md, der uncommittete Diff im
  Arbeitsbaum (sieben Dateien), nrdata/savefile.py, nrplanner/inventory.py,
  nrplanner/advisor/{candidates,run,search,types,worker}.py,
  nrplanner/app.py (rescan_save, _relics_by_handle), nrplanner/relicpicker.py,
  tests/{test_hostile_savefile,test_advisor_run,test_settings_store}.py,
  tests/advisor_cases.py, scripts/measure_advisor_search.py,
  docs/berichte/T-096-security-reviewer.md (Messtabelle), pytest.ini
GEAENDERT: nrdata/savefile.py, nrplanner/inventory.py,
  nrplanner/advisor/candidates.py, nrplanner/advisor/run.py,
  nrplanner/advisor/search.py, nrplanner/advisor/types.py,
  nrplanner/advisor/worker.py, tests/test_hostile_savefile.py,
  tests/test_advisor_run.py, scripts/measure_advisor_cancel.py (neu),
  docs/berichte/T-098-developer.md (neu) - drei Commits: c88800e, 645ceee,
  f79f770
ANNAHMEN: (1) Die im Baum gefundene Arbeit stammt aus T-097 und ist so
  gemeint, wie sie dasteht; ich habe sie geprueft und nicht neu geschrieben.
  (2) Die Suite-Vergleichszahl 1239/9 aus dem Auftrag ist die des Directors;
  sie geht auf diesem Baum nicht auf (siehe "Suite"), und ohne `checkout`
  kann ich die Vorher-Zahl nicht selbst messen.
NAECHSTER: qa-engineer (Abnahme SEC-022), danach director
BLOCKIERT DURCH: nichts
```

## Was vorgefunden, was selbst gebaut

**Vorgefunden** (T-097, uncommittet, unveraendert uebernommen): beide Deckel
in `nrdata/savefile.py` und `nrplanner/inventory.py` samt Konstante
`MIN_BYTES_PER_RELIC_RECORD`, die Abbruchpruefung in `candidates.pool`, die
Verlegung von `Cancelled`/`never_cancelled` nach `advisor/types.py`, und neun
neue Faelle in `tests/test_hostile_savefile.py`. Diese neun Faelle liefen
schon gruen, als ich anfing.

**Selbst gebaut:**

* Die Abbruchfaelle in `tests/test_advisor_run.py`. **Der Baum war an dieser
  Stelle nicht gruen** - zwei bestehende Faelle waren rot, weil die
  Vorsortierung jetzt fragt: `test_a_run_asks_once_between_the_pre_sort_and_
  the_search` (11 Fragen statt 3) und `test_a_run_stopped_inside_the_search_
  says_so` (die Meldung kam aus der Vorsortierung). Ein dritter,
  `test_a_run_stopped_before_the_search_says_so`, war **gruen aus dem
  falschen Grund**: sein `match="pre-sort"` passt auf beide Meldungen, sodass
  er nach der Aenderung die Schleifenpruefung mass und nicht mehr die Pruefung
  zwischen den Schritten, ohne dass etwas rot wurde. Jetzt stehen dort vier
  Faelle, die die drei Fragestellen einzeln festhalten (Gegenbau 4).
* `scripts/measure_advisor_cancel.py` - das Rezept zu den Zahlen unten.
* Die vier Gegenbauten, die Suite-Laeufe, die Suche nach weiteren Schleifen,
  die drei Commits und diesen Bericht.
* Vier Textkorrekturen an Stellen, die die Aenderung selbst falsch gemacht
  hatte: `run.run` versprach eine Messung "measured below", die es nicht gab;
  `worker.py` nannte weiter nur zwei Fragestellen; der Docstring des zweiten
  Deckels behauptete "die Tuer, durch die jeder Leser geht" (`app.py:2307`
  liest `.relics` direkt); und die Zahl 0,084 ms stand unattribuiert neben
  meiner eigenen, abweichenden Messung.

## Schritt 1, Frage 1: sind es zwei unabhaengige Deckel?

**Ja - zwei Pruefungen, ein Schwellenbegriff.** Sie teilen die Konstante und
die Formel; sie messen aber verschiedene Dinge an verschiedenen Stellen:

| | erster Deckel | zweiter Deckel |
|---|---|---|
| wo | `savefile.read_owned_relics`, im Parselauf | `Inventory.relics_for`, am Ausgang |
| woran | Datensaetze, waehrend sie entstehen | die fertige Relikt-Liste |
| Groesse aus | `len(slot_data)`, das Argument | `self.source_bytes`, ein Feld |
| ruft den anderen | nein | nein |

Der gemeinsame Wert (die Bytelaenge desselben Members) ist Absicht und kein
Mangel: zwei verschiedene Schwellen waeren zwei verschiedene Behauptungen
darueber, wie ein Save aussehen darf. **Der Beleg, dass es keine Pruefung mit
zwei Aufrufstellen ist, ist Gegenbau 1 gegen Gegenbau 2: sie toeten
disjunkte Faelle** (drei gegen zwei, kein einziger doppelt). Jede der beiden
faellt ohne die andere.

**Was der zweite Deckel nicht leistet, und das gehoert dazu:** er ist scharf
nur, wenn `source_bytes` gesetzt ist. Gesetzt wird es allein von
`inventory._scan_save`. Ein kuenftiger zweiter Leser, der ein `Inventory`
baut und das Feld vergisst, ist von Deckel 2 nicht geschuetzt - er muesste
dafuer allerdings auch an Deckel 1 vorbei. Das Feld schliessen (Pflichtfeld
statt `None`) hiesse, jedes handgebaute Test-Inventar zu einer Aussage ueber
eine Datei zu machen; das ist eine Entscheidung des `director`, kein
Seiteneffekt dieses Auftrags. **Empfehlung:** so lassen, aber als bekannte
Kante fuehren.

## Schritt 1, Frage 2: faellt der Deckel laut aus?

**Ja, und der Text erreicht den Spieler.** `app.py:3409-3414` faengt in
`rescan_save` jede Ausnahme aus `inventory.load` und schreibt sie auf
`owned_label` - dieselbe Flaeche, die SEC-004 auf Klartext gestellt hat. Der
Spieler sieht also:

> Save could not be read: a save slot of 1048608 bytes holds more than 16384
> relic records, denser than one record per 64 bytes, which is not an
> inventory; the file is damaged or was not written by the game. Take it out
> of the save folder and rescan.

**Kein Dateipfad, kein Kontoname, kein `.sl2`** - festgehalten von
`test_the_refusal_over_a_packed_slot_names_no_file_path`, das auf `\`, `/`
und `.sl2` prueft und verlangt, dass "save folder" und "rescan" vorkommen
(SEC-023 wird nicht vergroessert). Englisch (A8). Dass er **nicht** still
kuerzt, haelt Gegenbau 3 fest.

Der zweite Deckel benutzt denselben Wortlaut:

> this inventory holds 101 relics read from 6400 bytes of save slot, denser
> than one per 64 bytes, which is not an inventory; the file is damaged or
> was not written by the game. Take it out of the save folder and rescan.

**Hier ist meine Aussage schwaecher, und das ist eine Luecke, kein Beleg:**
seine Aufrufer sind `app.py:1020` (Slot-Widget) und `relicpicker.py:325`
(ueber `frozen_inventory`), und **keiner von beiden faengt**. Er wuerde als
Traceback in einem Qt-Slot enden, nicht als Satz auf der Fensterflaeche. Da
er nur greifen kann, wenn Deckel 1 vorher entfernt wurde, habe ich daran
nichts gebaut - **Meldung an den `director`**, siehe unten.

## Die Schranke, mit Rezept und Sicherheitsabstand

**Formel:** `limit = max(1, len(slot_data) // 64)`, mit
`MIN_BYTES_PER_RELIC_RECORD = 64`. Relativ zur Slotgroesse, nicht absolut.

**Herleitung der 64:** ein Datensatz ist auf dem echten Save 80 Byte breit
(`read_owned_relics` liest alle Felder innerhalb dieser 80: `EFFECT_OFFSETS`
bis 44, `CURSE_OFFSETS` bis 60, `HANDLE_OFFSET` -4). 64 ist die naechste
Zweierpotenz darunter - nah genug, dass ein echter Datensatz nie darunter
faellt, lose genug, dass die Schranke nichts ueber das Layout behauptet.

**Sicherheitsabstand, heute gemessen** (`scripts/measure_advisor_cancel.py`
und `savefile.find_loadout_table` auf dem eigenen Save, nur lesend):

| | Datensaetze | je Byte | zur Schranke |
|---|---|---|---|
| echter Save, `USER_DATA000`, 1 048 608 Byte | 309 | einer je 3 394 B | **Faktor 53 darunter** |
| die Schranke | 16 384 | einer je 64 B | - |
| praeparierte Datei (T-096, gemessen) | 131 069 je MiB | einer je 8 B | Faktor 8 darueber |

**Stichprobe:** zwei `.sl2` auf dieser Maschine, der bestbefuellte
Charakterslot davon. Der `security-reviewer` mass an einer aelteren Datei 284
Datensaetze; beide liegen zwei Groessenordnungen unter der Schranke. Der
Slot muesste **53-mal dichter** werden, ehe ein Spieler etwas merkt, und die
Schranke waechst mit der Slotgroesse mit, wenn das Spiel sie erhoeht.

## Die Messung der Abbruchpruefung

`scripts\measure_advisor_cancel.py`, Windows-10-10.0.19045-SP0, Python
3.12.10 CPython, 2026-09-07, Datenstand 10350000:

| | Zeit je Aufruf | ueber dem nackten Aufruf |
|---|---|---|
| nackter Python-Aufruf (Nullmessung) | 46,6 ns | - |
| `types.never_cancelled` (kopfloser Lauf) | 54,4 ns | +7,8 ns |
| `QThread.isInterruptionRequested` (das Fenster) | 77,0 ns | +30,4 ns |

1 000 000 Aufrufe, Median aus 5. Die Nullmessung steht daneben, weil sonst
die Schleife gemessen waere und nicht die Pruefung.

Im Verhaeltnis zur Arbeit: 309 Relikte, `Wylder's Chalice`, sechs freie
Slots, **388 angebotene Relikte insgesamt**; Vorsortierung 68,1 ms (Median
aus 3) = **175,6 us je angebotenem Relikt**. Die Pruefung ist davon
**0,077 us = 0,04 %**; der ganze Lauf zahlt 388 x 77 ns = **30 us**.

**Ehrlich dazu:** der Lauf *mit* der echten Pruefung mass 62,2 ms, der ohne
68,1 ms - die Pruefung ist im Rauschen der Vorsortierung nicht auffindbar.
Genau deshalb steht die Zahl je Aufruf und nicht eine Differenz zweier
Laeufe. AK-11 (200 ms) ist damit nicht die Pruefung, sondern der Abstand
zwischen zwei Pruefungen: 175,6 us.

## Die vier Gegenbauten

Jeder einzeln hergestellt (`cp datei datei.orig`, Mutation, Lauf,
`cp datei.orig datei`), gefahren mit
`pytest tests/test_hostile_savefile.py tests/test_advisor_run.py -m "not
slow"` (Gegenbau 4 zusaetzlich mit `test_advisor_worker.py` und
`test_advisor_search.py`) - **Standardlauf, keine Sonderkonfiguration**.

**1. Deckel in `read_owned_relics` entfernt** (`raise` -> `pass`) -> **3 rot**:
`test_a_slot_packed_with_relic_records_is_a_data_error`,
`test_the_refusal_over_a_packed_slot_names_no_file_path`,
`test_one_record_more_than_the_slot_can_hold_is_a_data_error`.

**2. Zweiten Deckel entfernt** (Aufruf von
`_refuse_a_density_no_save_can_have` aus `relics_for` gestrichen) -> **2 rot**:
`test_an_inventory_denser_than_the_slot_it_came_from_offers_nothing`,
`test_the_advisor_is_not_handed_an_inventory_of_that_density`.
**Kein einziger Fall ueberschneidet sich mit Gegenbau 1** - das ist der
Beleg fuer die zweite Sicherung.

**3. Deckel kuerzt still** (`raise` -> `del out[limit:]; break`) -> **3 rot**,
dieselben wie bei 1. Das ist hier kein Mangel, sondern die Aussage: dieser
Mutant **haelt die Schranke ein** (die Liste ist begrenzt, der Speicher
gedeckelt) und faellt trotzdem - die Faelle verlangen die Ausnahme, nicht
bloss die Begrenzung.

**4. `should_cancel` aus der Vorsortierschleife genommen** -> **4 rot**:
`test_a_run_stopped_inside_the_pre_sort_says_so`,
`test_a_run_stopped_between_the_pre_sort_and_the_search_says_so`,
`test_a_run_asks_once_per_offered_relic_and_once_per_level`,
`test_a_run_stopped_inside_the_search_says_so`. Der erste bricht mit
`Expected regex: 'during the pre-sort of slot 0, after 0'` /
`Actual message: 'stopped after the pre-sort, before the search'` - er faellt
also am Ort der Meldung, nicht an einer Signatur.

**L-008(b):** die Erwartung dieser Faelle kommt **nicht** aus der bewachten
Stelle. `whole_pre_sort()` zaehlt, was `relics_for` je freiem Slot antwortet
(die Momentaufnahme), nicht was die Schleife tut; die Meldungstexte sind
woertlich gefordert.

**Nichts blieb uebrig:** nach jedem Zurueckkopieren `git status --porcelain`,
zuletzt nach Gegenbau 4 zusaetzlich `git diff --stat` - **beide leer** bis
auf die zwei unversionierten Auftragsdateien `docs/tasks/T-097.md` und
`docs/tasks/T-098.md`, die dem `director` gehoeren.

## Suche nach weiteren unbegrenzten Schleifen ueber Save-Inhalte

**Maske 1** (laengengetriebene Schleifenkoepfe):
`grep -rn "for .* in range(.*len(" nrdata/*.py nrplanner/inventory.py` ->
**2 Treffer**: `nrdata/bhd5.py:68` (Spielinstallation, nicht Save, durch die
Datei begrenzt) und `nrdata/savefile.py:200` (der behobene).

**Maske 2**, unabhaengig formuliert (jeder Schleifenkopf im Save-Lesepfad):
`grep -nE "^\s*(for |while )" nrdata/savefile.py nrplanner/inventory.py` ->
**27 Treffer**, einzeln durchgesehen. Aus Dateiinhalt gesteuert sind zwei:
`_members` (seit SEC-002 gegen die Dateigroesse geprueft) und
`read_owned_relics` (jetzt gedeckelt). Der Rest laeuft gegen Modulkonstanten
(`MAX_HEROES`, `MAX_GRAILS`, `VESSELS_PER_HERO`, `EFFECT_OFFSETS`,
`CURSE_OFFSETS`) oder ueber bereits gebaute Listen.

**Dabei ein neuer Fund, den ich nicht behoben habe** (Befund-IDs vergibt der
`director`): `savefile.find_loadout_table` (Zeile 316) laeuft `range(0,
len(slot_data)-8, 4)` und startet an **jedem** Offset, der den Marker
`HERO_MARKER_BASE+1` traegt, zwei geschachtelte Schleifen (`while hero <=
MAX_HEROES` x `for records in range(0, MAX_GRAILS+1)`). Der Markerwert steht
in der Datei. Gemessen heute, gleicher Slot, gleiche Groesse:

| Inhalt, 1 048 608 Byte | `find_loadout_table` |
|---|---|
| echter Charakterslot | 0,049 s |
| jeder 4. Byte ein Marker | **1,251 s** (Faktor 25) |

Linear: 16/32/64 KiB -> 0,017/0,035/0,073 s, also ~1,25 s je MiB. Erreichbar
ist es: `inventory._scan_save` ruft `read_loadouts(blob)` **nach** dem
Reliktscan auf demselben Member, und der neue Deckel schlaegt nicht an - er
zaehlt Reliktdatensaetze, und **ein einziger** genuegt, damit der Slot nicht
uebersprungen wird (`if not owned: continue`). 19 MB Member sind damit ~24 s
eingefrorenes Fenster beim Start, 200 MB ~4 Minuten, ohne Zutun des Spielers.
Gemessen habe ich die Funktion, **nicht** den ganzen Startpfad - fuer den
waere ein vollstaendiger BND4/AES-Container noetig, und das ist ein eigener
Auftrag.

## Commits

| | |
|---|---|
| `c88800e` | `feat(savefile): refuse a save slot denser than one relic per 64 bytes` - `nrdata/savefile.py`, `tests/test_hostile_savefile.py` (nur die fuenf Faelle des ersten Deckels) |
| `645ceee` | `feat(inventory): refuse to offer relics denser than the slot they came from` - `nrplanner/inventory.py`, `tests/test_hostile_savefile.py` (die vier Faelle des zweiten) |
| `f79f770` | `feat(advisor): ask whether the run was stopped inside the pre-sort` - `candidates.py`, `run.py`, `search.py`, `types.py`, `worker.py`, `tests/test_advisor_run.py`, `scripts/measure_advisor_cancel.py` |

Alle drei mit Pfadangabe hinter `--`, kein `-a`, kein `add .`. Damit die
zwei Deckel getrennte Commits mit **je gruenem Lauf** bekommen konnten -
ihre Faelle liegen in einer Datei -, habe ich fuer den ersten Commit eine
Fassung der Testdatei ohne die Faelle des zweiten Deckels abgelegt
(Sicherungskopie im Scratchpad, danach die volle Fassung zurueck; kein
`stash`, kein `checkout`). Laeufe je Commit: c88800e 18 passed, 645ceee 48
passed (`test_hostile_savefile`, `test_relic_ownership`, `test_relic_restore`,
`test_loadout_table`), f79f770 107 passed (die vier Advisor-Dateien).

## Suite, geteilt und im Vordergrund

| Teil | Ergebnis | Dauer |
|---|---|---|
| `test_relic_picker_advisor.py` + `test_relic_picker_geometry.py` | **48 passed** | 163,64 s |
| Rest mit `--ignore` auf beide | **1195 passed, 1 failed, 9 skipped, 5 deselected** | 844,55 s |
| **Summe** | **1243 passed, 1 failed, 9 skipped** | ~16,8 min |

**Der eine Fehlschlag ist nicht meiner:**
`test_settings_store.py::test_no_source_opens_a_settings_store_of_its_own`
meldet
`{'.claude/worktrees/agent-ae1f6543a6c23b08a/nrplanner/app.py': [933, 937]}`.
Das ist ein **stehengebliebener, gesperrter Git-Worktree** eines anderen
Agentenlaufs (`git worktree list`: `.claude/worktrees/agent-ae1f6543a6c23b08a
11f0d97 [worktree-agent-...] locked`), in dem eine alte Fassung von `app.py`
noch `QSettings("DankYeeter", "NightreignHelper")` fest verdrahtet. Der
Waechter laeuft ueber den ganzen Baum und schliesst nur
`.venv/.git/__pycache__/build/dist` aus, nicht `.claude`. Im Arbeitsbaum
selbst oeffnet keine Zeile den Store anders (`grep -n "QSettings("
nrplanner/app.py`: fuenfmal `favourites.ORG, favourites.APP`), und meine drei
Commits fassen `app.py` nicht an (`git show --stat`). **Ich habe den Worktree
nicht angeruehrt** - fremdes Git.

**Zur Vergleichszahl 1239/9 aus dem Auftrag:** sie geht auf diesem Baum nicht
auf. Meine Faelle bringen nachweislich **+10** eingesammelte Faelle
(`pytest --collect-only` gegen die Fassungen aus `39e6a84`: 52 -> 62 in den
zwei beruehrten Dateien), und meine Commits beruehren keine dritte Testdatei;
die Summe liegt aber nur **+5** ueber 1248 ausgewaehlten. Ohne `checkout`
kann ich die Vorher-Zahl nicht selbst messen (Rahmen: die Zahl verantwortet
der `director`). Anmerkung dazu: der Kontext beim Aufruf nannte als HEAD
`fd9f2bc` und vier weitere Commits (`5fa50c1`, `c609e87`, `792318a`,
`bafc3e1`), die in der Historie dieses Branches **nicht vorkommen** - HEAD
war `39e6a84`, wie im Auftrag. Wahrscheinlich stammt der Auszug aus dem
fremden Worktree.

## An den qa-engineer

* **Der Deckel im Betrieb:** eine praeparierte `.sl2` gehoert **nicht** in
  den Save-Ordner des Nutzers. Der Weg zur Anzeige ist trocken pruefbar:
  `rescan_save` schreibt jede Ausnahme aus `inventory.load` auf
  `owned_label`. Zu pruefen ist der Satz auf Englisch, Klartext (kein Markup)
  und **ohne Pfad/Konto-Id**.
* **Randfaelle der Schranke:** genau an der Grenze (Slot mit `len//64`
  Datensaetzen) muss **alles** gelesen werden - der Fall dazu ist
  `test_a_slot_filled_to_the_limit_is_read_in_full`, und er ist der wichtige:
  ein Spieler mit sehr vollem Inventar darf nichts verlieren. Ein Save mit
  mehr als 16 384 Relikten in einem 1-MiB-Slot ist kein Spielstand.
* **Abbruch (AK-11):** `Cancel` waehrend eines Laufs ueber ein grosses
  Inventar. Erwartet: `Stopped. Nothing was changed.`, und der Abbruch wirkt
  jetzt auch waehrend der Vorsortierung, nicht erst danach. Zeitliche Kante:
  175,6 us zwischen zwei Pruefungen.
* **Kein Regressionsrisiko am Berater erwartet**, aber die Reihenfolge der
  Fragen hat sich geaendert: `should_cancel` wird jetzt je angebotenem Relikt
  gefragt (bei 388 Angeboten also 388-mal statt einmal). Wer eigene
  Zaehlungen dagegen haelt, muss sie anpassen.

## An den director

1. **Neuer Fund, ungeloest, gleiche Form wie SEC-022:**
   `savefile.find_loadout_table` amplifiziert einen frei waehlbaren
   Dateiinhalt, 1,25 s je MiB gegen 0,049 s auf dem echten Slot (Faktor 25,
   linear), erreichbar beim Start ueber `_scan_save` -> `read_loadouts`, und
   von beiden neuen Deckeln **nicht** gedeckt. Braucht eine ID und einen
   eigenen Auftrag. Aufwand geschaetzt klein (dieselbe Form: eine relative
   Schranke auf die Zahl der Marker-Startpunkte), Risiko: der Leser ist schon
   zweimal an falschen Annahmen ueber das Layout gescheitert, laut seinem
   eigenen Docstring - also mit Messung am echten Save, nicht mit einer
   geratenen Konstante.
2. **Der zweite Deckel hat keinen Anzeigeweg.** Seine Ausnahme wuerde in
   `app.py:1020` bzw. `relicpicker.py:325` als Traceback enden statt als Satz
   auf `owned_label`. Er ist eine Rueckfallsicherung und heute nur nach
   Entfernen des ersten Deckels erreichbar - trotzdem: entweder so lassen und
   als Kante fuehren, oder die zwei Aufrufer fangen lassen und auf dieselbe
   Beschriftung leiten. Deine Entscheidung; ich habe nichts gebaut.
3. **`source_bytes is None` schaltet den zweiten Deckel ab.** Absicht (ein
   handgebautes Inventar behauptet nichts ueber eine Datei), aber es macht
   die zweite Sicherung fuer kuenftige Leser **opt-in**. Schliessen hiesse:
   Pflichtfeld, und jedes Test-Inventar muesste eine Groesse nennen.
4. **Stehengebliebener Worktree bricht die Suite.**
   `.claude/worktrees/agent-ae1f6543a6c23b08a` (gesperrt, Commit `11f0d97`)
   laesst `test_settings_store` rot werden. Zwei Wege: den Worktree entfernen
   (Sache des `director`/`archivist`, ich fasse fremdes Git nicht an), oder
   `NOT_OURS` in `tests/test_settings_store.py` um `.claude` erweitern -
   Letzteres ist auch inhaltlich richtig, denn der Waechter soll den
   Projektquelltext pruefen, nicht eine fremde Arbeitskopie. **Solange das
   steht, ist jede Suite-Zahl dieses Projekts um diesen Fehlschlag zu
   korrigieren.**
5. **Keine MD5-Pruefung nachgeruestet** (Scope-Grenze eingehalten). Meine
   Einschaetzung unveraendert zu T-097: der oeffentliche Schluessel macht sie
   zu keiner Echtheitspruefung. Sie wuerde SEC-022 auch nicht schliessen -
   ein Angreifer mit dem Schluessel rechnet die Pruefsumme mit.
6. **Zwei bestehende Faelle musste ich aendern**, weil die Aenderung ihr
   Verhalten aendert (siehe oben), und einer davon war **gruen aus dem
   falschen Grund**. Wenn du das als Scope-Frage siehst: ohne diese Aenderung
   waere die Suite rot geblieben.
7. **Neue Datei ohne vorherige Freigabe:** `scripts/measure_advisor_cancel.py`.
   Keine neue Abhaengigkeit (PySide6 und stdlib), Muster ist
   `scripts/measure_advisor_search.py`. Wenn du das Rezept nicht im Repo
   willst, sag es - dann kommt sie wieder raus und die Zahlen stehen nur hier.

## Was nicht geprueft ist

* **Kein Fenster gestartet** (Nutzer hat eine Programmkopie offen), also ist
  der Anzeigeweg des Fehlertexts **gelesen, nicht gesehen**.
* **Keine praeparierte `.sl2`** angelegt - alle feindlichen Puffer entstehen
  im Test im Speicher. Der Save wurde ausschliesslich gelesen.
* Nur Windows 10 / Python 3.12.10 / PySide6 offscreen. **macOS, Linux,
  Android, iOS: ungeprueft.**
* Kein Linter im Projekt konfiguriert (kein flake8/ruff/pylint in
  `requirements-dev.txt` oder `.github/workflows/`), der Punkt entfaellt.
