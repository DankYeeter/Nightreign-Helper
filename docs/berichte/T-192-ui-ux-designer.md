# T-192 — Die dritte Zielrichtung sichtbar machen (ui-ux-designer, Spec-Modus)

```
STATUS: erledigt
AUFTRAG: T-192 — Die dritte Zielrichtung sichtbar machen (Spec)
GELESEN: docs/tasks/T-192.md, ~/.claude/agents/_rahmen.md, CLAUDE.md (global
         und Projekt), GOAL.md (A3, A7, A12, A13, A16, A17 vollstaendig),
         docs/state.md, ARCHITECTURE.md (AD-032 vollstaendig, Z. 2936-3310),
         UI_SPEC.md (Kopf, Bereich 3 §3.1, Bereich 5 vollstaendig,
         AK-190 bis AK-194), UI_SPEC_REGISTER.md, qa/findings.md (QA-228),
         docs/berichte/T-191-developer.md, nrplanner/relicpicker.py,
         nrplanner/advisorbar.py, nrplanner/advisor/goals.py, types.py,
         candidates.py, nrplanner/paths.py, favourites.py, shortcut.py,
         tests/conftest.py, tests/advisor_cases.py,
         tests/test_relic_picker_geometry.py, tests/test_advisor_bar.py
         (Ausschnitte), scripts/build_snapshot.py.
GEAENDERT: UI_SPEC.md (§5.4 neu, AK-256 bis AK-263; Vermerke an AK-42, AK-43,
           AK-46, AK-195, AK-205; Kopfzahlen und Bereichstabelle),
           UI_SPEC_REGISTER.md (8 neue Zeilen, 5 fortgeschriebene, Nachtrag
           zur Zaehlung), docs/berichte/T-192-ui-ux-designer.md (diese
           Datei). **Kein Anwendungscode, kein Commit, kein git-Zustand
           veraendert.**
ANNAHMEN: 1) `docs/state.md` nennt AK ab **AK-256** — nachgelesen, stimmt;
          die Nummern AK-256 bis AK-263 sind vergeben.
          2) Der Auftrag nennt T-191 mit `6f369a7`; gemessen habe ich gegen
          einen Klon von **`7bcb093`** (HEAD zum Startzeitpunkt), der
          `6f369a7` enthaelt.
          3) „Unterscheidbar" und die Grundgesamtheit 210 sind die von
          AD-032; ich habe sie reproduziert, nicht neu definiert.
NAECHSTER: director — er hat drei offene Fragen an den App Designer, sechs
           Befunde und einen Bauauftrag zu verteilen.
BLOCKIERT DURCH: nichts.
```

## Urteil

**Drei Richtungen funktionieren in diesem Picker** — kein Widerspruch. Jede
enge Stelle ist gemessen und keine reisst: der laengste Eintrag braucht
183 px gegen die 200 px der Advisor bar, die dritte Wertzeile kostet 18 px
Kartenhoehe und die zwei ganzen Kartenzeilen aus AK-196 bleiben (gemessen
sind drei), und die Vorziehung aus AK-195 waechst von 3-5 auf **6** Karten,
nicht auf zwanzig.

**Die scharfe Stelle war eine andere, als der Auftrag vermutet hat.** Nicht
die Breite und nicht die Hoehe, sondern AK-195 selbst: die vorgezogenen
Karten der **nicht gelesenen** Richtung tragen heute **keinen Chip**, obwohl
AK-195 sich damit begruendet, die Anordnung sage nichts, was der Chip nicht
schon sage. Mit zwei Richtungen ist das eine unerklaerte Karte, mit drei sind
es vier von sechs. AK-262 macht den Satz wahr.

## 1. Was spezifiziert ist — UI_SPEC.md §5.4, AK-256 bis AK-263

| AK | was es festlegt | Verhaeltnis zum Bestand |
|---|---|---|
| **AK-256** | `Sort by` ist die **Projektion** von `advisorbar.GOAL_ORDER`, nicht eine Liste von Woertern; `GOAL_ORDER` deckt `goals.GOALS` vollstaendig; `Name` immer zuletzt; kein Richtungsname als Literal; eine Zielwahl im ganzen Programm | **ersetzt AK-43** |
| **AK-257** | Label `Maximise offensive attributes`, an **dritter** Stelle, hinter den beiden bisherigen; Messauflage an der 200-px-Schranke der Advisor bar; Rueckfallwortlaut `Maximise attack stats` | neu |
| **AK-258** | **drei** staendige Wertzeilen statt einer wechselnden, eine je Richtung, in jedem Zustand | **erweitert AK-42** |
| **AK-259** | Beschriftung `Offensive attributes`, Einheit `pts` aus `Baseline.unit` — A12 | neu |
| **AK-260** | dieselbe Rundung wie jeder andere Gewinn (`+3.0 pts`), keine Rundung je Richtung | neu |
| **AK-261** | **alle drei** Spitzengruppen fuehren, in fester Reihenfolge: gelesene Richtung, dann `GOAL_ORDER`, dann Wertordnung | **ersetzt AK-195** |
| **AK-262** | jede vorgezogene Karte traegt den Chip der Richtung, die sie vorgezogen hat; dritter Chip `BEST FOR STATS` | **erweitert AK-46** |
| **AK-263** | was in der gelesenen Richtung gezeichnet wird (Kopfzeile, `scope`, Wertordnung, Chip) und was **keine** Richtung hat (die drei Wertzeilen) | **ersetzt AK-205** |

**Die drei Entscheidungen des Auftrags, je in einem Satz:**

1. **Eintrag:** `Maximise offensive attributes`, hinten. Der Arbeitstitel des
   `developer` ist bestaetigt, weil er **gemessen passt** — `Maximise
   attributes` waere kuerzer und falsch (die Richtung zaehlt fuenf von acht
   Attributen), und Kuerze ist kein Argument, wenn der ehrliche Name 17 px
   Luft hat. Hinten, weil `GOAL_ORDER` zugleich die Reihenfolge der
   Wertzeilen ist und ein Einschub in der Mitte eine seit T-024 stehende
   Zeile verschoebe **und AK-193 falsch machte**, das von der *ersten* Zeile
   der Wertspalte spricht.
2. **Wertespalte:** eine **dritte, staendige** Zeile, keine wechselnde. Grund
   ist nicht Geschmack, sondern eine Messung: eine Zeile, die mit der
   Richtung kaeme und ginge, aenderte die Kartenhoehe um **18 px** bei jedem
   `Sort by`-Wechsel und braeche AK-41 (0 px), AK-204 und AK-216. Dazu der
   Grund von AK-42 selbst (OF-13): die Kosten in der anderen Richtung
   muessen sichtbar bleiben.
3. **AK-195/AK-205:** **alle drei** Spitzengruppen werden vorgezogen, in
   fester Reihenfolge, und jede vorgezogene Karte sagt per Chip, welche
   Richtung sie vorgezogen hat. Der Satz des App Designers (*„zeig mir aber
   immer den top pick für dmg und survival als erstes"*) meint „die Spitze
   jeder Richtung ist immer sichtbar"; bezahlbar ist es gemessen (6 Karten).

## 2. Messungen — Umgebung, Rezept, Positivkontrolle

**Messumgebung (L-009), gilt fuer jede px-Zahl in diesem Bericht und in
§5.4:** Windows 11, PySide6/Qt, Stil **`fusion`** mit der dunklen Palette des
Programms (`app.apply_appearance`) — **nicht** der Vorgabestil `windows11`;
Schrift Segoe UI 9,0 pt; Bildschirm 4096 x 1728 **logische** px, verfuegbar
ebenso; `devicePixelRatio` 1,25 (physisch 5120 x 2160), `logicalDotsPerInch`
96. **Alle Zahlen sind logische px**, wie Qt sie in `setMaximumWidth` und
`width()` nimmt.

**Datengrundlage:** Datensatz frisch aus der Spielinstallation gebaut (nur
lesend), `data_version` 10350000, `extract_version` **11**, 8 484 644 Bytes;
Spielstand des Nutzers **nur lesend**, 312 Kopien.

**Zwei Stichproben, nicht eine:**

- **S1** — freier weisser Slot, leerer Grundzustand, Wylder Level 15, **210**
  gewoehnliche Kandidaten ueber `candidates.pool`, kein Fenster. Das ist die
  Grundgesamtheit aus AD-032.
- **S2** — das **laufende Fenster**: `Planner` mit dem Spielstand des
  Nutzers, Picker auf `base_slots[0]` (gelber Slot), **56** Karten samt
  Custom-Kachel, Frage beantwortet, dann dieselbe Oeffnung ein zweites Mal
  mit einer simulierten dritten Wertzeile (`VALUE_DIRECTIONS` im Messprozess
  gepatcht, **kein** Anwendungscode geaendert).

**Positivkontrolle der Messeinrichtung (S1):** 26 / 37 / 53 unterscheidbare
Kopien je Richtung, **75** unter A oder C, **104** unter allen dreien,
groesste Gleichstandsgruppen 184 / 173 / 157 — **acht von acht Zahlen
identisch** mit AD-032 und T-191. Eine Einrichtung, die das nicht
reproduziert, misst etwas anderes.

**Breiten (S2 und Widget-Messungen im selben Prozess):**

| | gemessen | Schranke | Urteil |
|---|---|---|---|
| `Maximise offensive attributes`, Text | 155 px | — | — |
| Combo mit dem dritten Eintrag, `sizeHint` | **183 px** | 200 px (Advisor bar), 220 px (`SORT_BOX_WIDTH`) | passt, 17 bzw. 37 px Luft |
| `Sort by` im laufenden Fenster | 155 → **183 px** | 220 px | passt |
| Wertzeile `Offensive attributes` + `+24.0 pts` | 95 + 53 + 6 = **154 px** | 174 px | passt |
| Chip `BEST FOR ATTRIBUTES` | **106 px** | 102 px (Streifen) | **abgeschnitten** → `BEST FOR STATS`, 76 px |

**Hoehen (S2, laufendes Fenster, dieselbe Kartenliste):**

| | zwei Wertzeilen | drei Wertzeilen |
|---|---|---|
| Kartenzeile im Raster | 210 px | **228 px** (+18) |
| `wanted_height`, `MINIMUM_ROWS` = 3 | 1082 px | **1136 px** (+54) |
| Dialoghoehe | 1007 px | 1151 px |
| ganz sichtbare Kartenzeilen | 3 | **3** |
| waagerechte Bildlaufleiste | keine | keine |

**Vorziehung (AK-261), beide Stichproben:**

| | Schaden | Ueberleben | Attribute | fuehrend heute (2 Richtungen) | fuehrend mit drei |
|---|---|---|---|---|---|
| S1 (210 Karten) | 3 | 2 | 1 | 5 | **6** |
| S2 (56 Karten) | 2 | 1 | 3 | 3 | **6** |

In S1 sind die drei Spitzengruppen paarweise ueberschneidungsfrei. Die dritte
Wertzeile traegt in S2 bei **17 von 55** Reliktkarten eine Zahl (`+1.0` 2x,
`+2.0` 4x, `+3.0` 7x, `+5.0` 1x, `+6.0` 3x), bei 38 `no change`.

**Skripte:** `…/scratchpad/T-192/measure_promotion.py`, `measure_picker.py`,
`measure_widths.py`, `measure_chip.py`. Sie ueberleben die Sitzung nicht —
siehe Befund 6.

## 3. Nachweis der drei Umlenkungen (CLAUDE.md, QA-195)

Vor jeder Messung gesetzt **vor** dem ersten `nrplanner`-Import und im Lauf
ausgedruckt und mit `assert` geprueft:

| Variable | Nachweis im Lauf |
|---|---|
| `NIGHTREIGN_SETTINGS_ORG` = `DankYeeterT-192` (+ `_APP` = `NightreignHelperT-192`) | `favourites._settings().fileName()` = `\HKEY_CURRENT_USER\Software\DankYeeterT-192\NightreignHelperT-192` |
| `LOCALAPPDATA` | `paths.cache_dir()` = `…\scratchpad\T-192\localappdata\NightreignHelper`, `paths.snapshot_path()` ebenda |
| `APPDATA` | `shortcut.shortcut_path()` = `…\scratchpad\T-192\appdata\Microsoft\Windows\Start Menu\Programs\Nightreign Helper.lnk` |

Zusaetzlich geprueft: `nrplanner` kam aus dem **Klon** im Scratchpad
(`model.__file__`), nicht aus dem Arbeitsbaum. Nach den Laeufen: der
Registrierungsschluessel `HKCU:\Software\DankYeeterT-192` ist **entfernt**
(geprueft), `HKCU:\Software\DankYeeter` (der echte) ist unberuehrt vorhanden,
und im echten Start-Menue liegt **keine** Verknuepfung.

## 4. Befunde (Nummern vergibt der `director`)

1. **Der Chip ist auf einer favorisierten Karte schon heute abgeschnitten.**
   Gemessen am echten `RelicCard`-Widget (Fusion, 190 px Karte): der
   Chipstreifen ist **102 px** breit, mit Stern nur **79 px**.
   `BEST FOR DAMAGE` misst 91 px, `BEST FOR SURVIVAL` 95 px — auf jeder
   favorisierten Karte also um 12 bzw. 16 px **gekappt** (`QLabel` mit
   `SizePolicy.Ignored` elidiert nicht, es schneidet). Das bricht AK-46, ist
   aelter als diese Vorgabe und von ihr unabhaengig. *Gemessen am Widget, im
   geoeffneten Dialog nicht gegengesehen.*
2. **Sechs von 56 Wertzellen sind im laufenden Fenster abgeschnitten.**
   Ueberlebenszeile, z. B. `+64.2 effective HP`: will 104 px, hat 95 px. Die
   dritte Zeile macht das nicht schlimmer (`+24.0 pts` = 53 px), aber die
   Zelle ist zu eng fuer die laengsten Werte dieser Einheit.
3. **Der feste Testabzug aus `CLAUDE.md` existiert nicht.** Zwei unabhaengige
   Pruefungen (Dateisystem ueber Bash und `Test-Path`):
   `C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug` fehlt. Der
   **echte** Cache `…\Local\NightreignHelper` passt auf die Beschreibung
   (841 Dateien, 19,8 MB), ist aber **`extract_version` 8**, waehrend der Baum
   auf 11 steht — ein `Planner` darauf stuerzt ab (`KeyError
   catalyst_scaling` in `weapons.rate`, Arsenal-Tab beim Bau). Ich habe mir
   deshalb einen frischen Abzug (Version 11) ins umgelenkte Verzeichnis
   gebaut; er ist mit dem Scratchpad wieder weg. **Solange der Abzug fehlt,
   zahlt jeder Lauf, der ein Fenster baut, den Neubau** (hier rund zwei
   Minuten). Vorschlag: Abzug in Version 11 an den dokumentierten Pfad legen
   oder die Zeile in `CLAUDE.md` korrigieren.
4. **AK-195 hat sich selbst falsch begruendet.** *„Es sind genau die Karten,
   die nach AK-46 einen `BEST FOR …`-Chip tragen"* — den Chip vergibt
   `_say_what_they_are_worth` nur fuer die **gelesene** Richtung; die Karten
   der anderen Spitzengruppe stehen unbeschriftet vorn (S2: 1 von 3). AK-262
   schliesst das.
5. **Waechter, die mit der Umsetzung rot werden** (nicht durch die Umsetzung
   kaputt, sondern durch sie ueberholt):
   `tests/test_advisor_goals.py::test_the_third_direction_is_scored_but_not_yet_offered`
   (haelt genau das Gegenteil von AK-256 fest — **streichen**, nicht
   umdrehen); `tests/test_advisor_bar.py::test_the_two_directions_stand_in_the_order_the_spec_lists_them`
   (zaehlt zwei Labels woertlich auf — gegen `GOAL_ORDER` schreiben, AK-256
   Punkt 2); `tests/picker_track.py:200` und
   `tests/test_relic_picker_advisor.py:140` (beide `next(goal_id for … if
   goal_id != …)` als „die andere Richtung") sowie `relicpicker.py:1214`
   dasselbe im Anwendungscode — das ist die Stelle aus AK-261.
6. **Die Messskripte liegen im Scratchpad und ueberleben die Sitzung nicht.**
   Dieselbe Meldung wie T-191 Punkt 6: soll die Vorziehungszahl (6 von 56)
   oder die 18 px je wieder nachweisbar sein, gehoeren sie unter `scripts/`.
   Das ist ein eigener Auftrag, kein Nebenbei.
7. **Kleiner Textbefund:** der Docstring von
   `relicpicker._fit_to_three_rows` nennt „AK-51 asks for 1122 px against
   1027 available" mit Datum 2026-09-07. Auf demselben Rechner misst heute
   derselbe Weg **1082 px gegen 1728 px verfuegbar** — die Zahl hat ihre
   Umgebung (Bildschirm) nicht mitgenannt und liest sich als Eigenschaft des
   Programms.

## 5. Offene Fragen an den App Designer

1. **Sollen wirklich alle drei Spitzengruppen vorgezogen werden?** Der Satz,
   auf dem AK-195 steht, nennt **Schaden und Ueberleben**. Ich habe ihn als
   „die Spitze jeder Richtung ist immer sichtbar" gelesen und auf drei
   ausgeschrieben; die Kosten sind gemessen **6 Karten** vor der Wertordnung
   (heute 3 bis 5), bei fuenf Karten je Rasterzeile also gut eine Zeile. Die
   Alternative waere: nur die Spitze der **gelesenen** Richtung fuehrt, die
   anderen findet man ueber den Richtungswechsel. Das ist eine
   Geschmacksfrage, keine Messfrage.
2. **Chip: `BEST FOR STATS` — oder den Chipstreifen verbreitern?**
   `BEST FOR ATTRIBUTES` passt um 4 px nicht (106 gegen 102 px), auf
   favorisierten Karten sind schon die heutigen zwei Chips gekappt (Befund
   1). Wird der Streifen verbreitert, ist `attributes` moeglich und ein
   heutiger Fehler nebenbei behoben — das ist Arbeit an einer Karte, die
   sonst niemand angefasst haette, und deshalb eine Entscheidung und keine
   Selbstverstaendlichkeit.
3. **Die 157 `no change` in der neuen Zeile** (S1: 157 von 210 Kopien
   bewegen die Attributszahl nicht). AD-032 hat die Frage schon gestellt und
   der Director sie offengelassen: soll die Oberflaeche *„bewegt diese
   Richtung nicht"* von *„konnte nicht gerechnet werden"* unterscheiden?
   Heute tun das `no change` und `—` (AK-219) — ob ein Spieler den
   Unterschied sieht, beantwortet der `power-user`, nicht ich.

## 6. Was diese Vorgabe an anderen Auftraegen beruehrt

- **AK-190 / AK-192 / AK-193 (A17 Teil 2)** sind ausdruecklich **nicht**
  Gegenstand. Beruehrt ist einzig **AK-193**: es spricht von der **ersten**
  Zeile der Wertspalte. Weil der dritte Eintrag **hinten** steht, bleibt die
  Schadenszeile die erste und AK-193 woertlich richtig. Wer den Eintrag
  spaeter nach vorn zieht, muss AK-193 mitschreiben.
- **A16** (bester/schlechtester Fall): kommt sie als zweite Auswahlliste, ist
  sie **keine** Zielrichtung und gehoert nicht in `GOAL_ORDER` — AK-256
  Punkt 1 verlangt Deckungsgleichheit mit `goals.GOALS`, nicht mit allem, was
  eine Combo anbietet.
- **`MAX_ATTRIBUTES.blurb`** (T-191 bat um Bestaetigung): **nicht
  festgelegt**, und zwar mit Grund — `Goal.blurb` wird nirgends gelesen.
  Zwei unabhaengige Suchen: `grep -rn "\.blurb" nrplanner/ nrdata/` → **0
  Treffer**; `grep -rn "blurb" nrplanner/` → 14 Treffer, davon 4 die
  Zuweisungen in `goals.py`, 1 die Felddeklaration in `types.py` und 9
  gleichnamige **lokale** Variablen anderer Tabs (`arsenaltab`,
  `relicpicker` 816 ist die Custom-Kachel, `bosstab` ein Docstring). Einen
  Text, den nichts zeichnet, lege ich nicht fest.
- **`CANONICAL_POOL_ORDER`** bleibt `max_damage` (AD-032). AK-263 haengt
  daran: die gelesene Richtung darf nie von dort kommen.
- **Keine Persistenz betroffen:** die Zielwahl wird nirgends gespeichert
  (geprueft: keine `setValue`-Stelle zu einem Ziel), der Picker startet auf
  `GOAL_ORDER[0]`, wenn kein Berater da ist. Die Sorge aus AD-032
  („gespeicherte Zieleinstellungen zeigen auf eine Richtung, die es nicht
  mehr gibt") trifft heute nicht zu.

## 7. Aufgeraeumt

Kein Server, kein Port. Vier Messlaeufe, alle beendet; `Get-CimInstance
Win32_Process` zeigt **keinen** `python.exe` von mir. Die zwei laufenden
pytest-Prozesse gehoeren nicht mir (einer dem Projekt `ApplicationHelper`,
einer vermutlich dem parallelen T-193). Klon, umgelenktes `LOCALAPPDATA`
(samt frischem Abzug und Symbolen) und `APPDATA` sind geloescht, der
Registrierungsschluessel der Umlenkung entfernt; im Scratchpad liegen nur
noch die vier Messskripte. Im Arbeitsbaum sind genau zwei Dateien geaendert
(`UI_SPEC.md`, `UI_SPEC_REGISTER.md`) plus dieser Bericht; **nichts
committet**, keine Bildnachweise erzeugt (NH-002).
