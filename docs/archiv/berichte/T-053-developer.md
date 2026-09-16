# T-053 — developer

```
STATUS: erledigt
AUFTRAG: T-053 — Die Oberflaechen-Befunde aus dem Design-Review umsetzen
GELESEN: docs/tasks/T-053.md · GOAL.md · docs/state.md · DESIGN_REVIEW.md
  (Review vom 2026-09-05, DR-008 bis DR-012) · UI_SPEC.md (AK-63 bis AK-67
  samt beiden Nachtraegen vom 05.09.) · ARCHITECTURE.md (Nachtrag VI, AD-025)
  · qa/findings.md (QA-099a, QA-108, QA-113, QA-116 bis QA-124) ·
  docs/berichte/T-046-developer.md §7/§8 · docs/berichte/T-048-developer.md
  §6/§7 · docs/berichte/T-052-ui-ux-designer.md ·
  docs/screenshots/2026-09-05/ (alle fuenf Bilder angesehen)
GEÄNDERT: nrdata/extract.py · nrplanner/model.py · nrplanner/damage.py ·
  nrplanner/weaponslots.py · nrplanner/arsenaltab.py · nrplanner/app.py ·
  nrplanner/advisor/candidates.py · scripts/differential/mutate.py ·
  scripts/measure_display_thresholds.py (neu) · tests/golden/weapon_damage.json
  · tests/test_damage_facade.py · tests/test_arsenal_tab_asks_the_facade.py ·
  tests/test_unequippable_catalyst.py (neu) ·
  tests/test_weapon_slot_tile_wrap.py (neu) ·
  tests/test_pool_finding_wording.py (neu) ·
  tests/test_display_thresholds.py (neu) ·
  docs/screenshots/2026-09-05-T053/ (5 Bilder, neu) ·
  docs/berichte/T-053-developer.md (diese Datei).
  Neun Commits, 217796a bis c3f1bc3. Fremde ungespeicherte Dateien nicht
  angefasst und nicht committet.
ANNAHMEN: (1) DR-009 ist im Auftrag ausdruecklich genannt, also greife ich in
  eine Kachel des `Build planner` ein, obwohl der Tab sonst ausgenommen ist.
  (2) Von den beiden Loesungswegen in DR-009 habe ich den zweitgenannten
  gewaehlt (Begriff zusammenhalten statt Kachel umbauen) — Begruendung in
  Abschnitt 2; der `ui-ux-designer` hatte ausdruecklich keine Praeferenz.
  (3) Die drei 0,05/0,5-Literale ausserhalb des von AK-65 benannten
  Bereichs habe ich mitbenannt, weil zwei verschiedene Regeln dieselbe Zahl
  trugen; kein Verhalten geaendert, Beleg in Abschnitt 5.
NÄCHSTER: qa-engineer
BLOCKIERT DURCH: nichts. Eine Vorgabe geht im Kontakt mit dem Code nicht auf
  (AK-67 gegen die dritte Zeile in `SlotPool.unknowns`, QA-113) — sie
  blockiert diesen Auftrag nicht, braucht aber eine Entscheidung des
  `ui-ux-designer`, Abschnitt 6.3.
```

---

## 0. Ergebnis in sechs Zeilen

1. **DR-008/QA-119/AK-66:** die nicht ausruestbare Katalysator-Zeile 33770000
   erscheint in keiner spielerseitigen Waffenliste mehr. Der Geltungsbereich
   steht im Code, nicht im Commit.
2. **DR-009:** `Spell power` bricht in der Slot-Kachel nicht mehr mitten im
   Begriff.
3. **DR-010/QA-121/AK-64:** der Zusammenfassungssatz erklaert beide
   Kennzahlen.
4. **DR-011/AK-63:** nichts zu bauen — der Picker mit Berater-Anzeige (S10)
   existiert nicht; mit zwei unabhaengigen Suchmasken geprueft (6.1).
5. **DR-012/QA-117/AK-65:** Schwellen unveraendert, jetzt benannt, gemessen
   und bewacht.
6. **AK-67:** beide entschiedenen Wortlaute stehen; **ein** Platzhalter
   bleibt (QA-113) und traegt jetzt den Namen der fehlenden Entscheidung.

Suite: **622 passed, 5 deselected** (vorher 592/5); `-m "slow"` **5 passed**.
Acht neue Mutationen, alle gefahren, alle tot. Ergebnis am **laufenden
Fenster** angesehen, fuenf Screenshots.

---

## 1. DR-008 / QA-119 / AK-66 — die Fremdzeile ist weg, und der
## Geltungsbereich steht im Code

Commit `217796a`.

### 1.1 Was das Kriterium braucht

AK-66 nennt `equippedSpell_R1 == -1 and equippedSpell_R2 == -1`. Das Feld war
im extrahierten Waffensatz **nicht vorhanden** (geprueft am Snapshot: die
Waffen-Records tragen `base, curve, effect_pool, element_correct_id, family,
icon, id, name, rarity, regain_hp, reinforce_type, requires, scaling, weight,
wep_type` und sonst nichts). Also traegt der Record es jetzt:

```python
"equipped_spells": [r.values.get("equippedSpell_R1", -1),
                    r.values.get("equippedSpell_R2", -1)],
```

Liste statt Tupel, damit eine Live-Extraktion und ein aus JSON gelesener
Snapshot dasselbe zurueckgeben. `EXTRACT_VERSION` **9 -> 10**; jeder
vorhandene Cache baut sich beim naechsten Start einmal neu (Mechanik war
schon da, `datasource._regulation_matches` / `firstrun.ensure_data`).

Rohwerte direkt aus `EquipParamWeapon` gelesen, vor jeder Codeaenderung:

```
33750000 {'equippedSpell_R1': 4000, 'equippedSpell_R2': 4070}
33770000 {'equippedSpell_R1': -1,   'equippedSpell_R2': -1}
34000000 {'equippedSpell_R1': 6400, 'equippedSpell_R2': 6000}
34750000 {'equippedSpell_R1': 6400, 'equippedSpell_R2': 6421}
2000000  {'equippedSpell_R1': -1,   'equippedSpell_R2': -1}   (Longsword)
```

Das deckt sich mit T-046 §7 und zeigt zugleich die Falle: der Longsword
traegt dieselben −1.

### 1.2 Der Geltungsbereich, im Code

`nrplanner/model.py`:

```python
def is_unequippable_catalyst(weapon: dict | None) -> bool:
```

Der Docstring sagt in seinem ersten Absatz: *"The scope is the whole of this
criterion, and no caller may widen it"* — 1764 von 1793 benannten Waffen
tragen −1 in beiden Slots, weil das ist, was ein Schwert ist; innerhalb der
Katalysator-Familie ist es 1 von 30. Die Funktion prueft `weapon_class` zuerst
und kann ohne diese Pruefung nicht aufgerufen werden.

Am echten Datensatz nachgemessen (nach dem Snapshot-Neubau):

```
named armaments: 1793
catalysts: 30
no spell slot, whole dataset: 1764
no spell slot, catalysts only: 1
dropped by the filter: [(33770000, "Recluse's Staff", 'Glintstone Staff')]
offerable: 1792
names still colliding: {"Scholar's Thrusting Sword": 4, 'Finger Seal': 2}
```

### 1.3 Wo der Filter greift — und wo ausdruecklich nicht

Zwei spielerseitige Waffenlisten existieren, beide gehen durch dieselbe Regel:

* `damage.rank_candidates` (speist den Arsenal-Tab und jede kuenftige
  Berater-Kandidatenliste),
* `weaponslots.WeaponDialog` (Liste **und** Namenszaehlung fuer die
  Id-Beschriftung).

Vier weitere Stellen lesen `data["weapons"]` **ungefiltert**, jede mit Grund
im Code: `weapons.rank` (Rechenschicht — eine Messung ueber die 30
Katalysatoren muss weiter 30 finden), `weaponslots.base_ids` (Infusions-Baender
— ein Band mit fehlender Zeile antwortet anders), `rollable_effects`
(Pool-Vererbung derselben Baender), `app._weapon_by_id` (Nachschlagen beim
Wiederherstellen eines gespeicherten Builds — sonst laesst sich ein alter
Build mit dieser Waffe nicht mehr laden).

**L-006-Sweep, zwei unabhaengige Masken** ueber das ganze Paket:
Maske A `'\["weapons"\]'` — 6 Treffer, oben alle einzeln eingeordnet;
Maske B `'for weapon in|for w in '` — 9 Treffer, keine weitere Liste.
Zusaetzlich `grep -n "weapon"` ueber `effectstab/depthstab/bosstab/deeptab/
eventstab/relicpicker/search` — 4 Treffer, alle Prosa ueber Event-Beute, keine
Liste. **Kein weiterer Fundort.**

### 1.4 Warum es ein echter Schaden war, nicht nur unschoen

Ich habe beide Zeilen selbst durchgerechnet (Snapshot dieses Rechners):

| Build | Tier | 33750000 (echt) | 33770000 (Fremdzeile) |
|---|---|---|---|
| Wylder Lv 15 | +1 | 93 | **110** |
| Wylder Lv 15 | +4 | 165 | **110** |
| Recluse Lv 12 | +1 | 128 | **151** |
| Recluse Lv 12 | +4 | 227 | **151** |

Zwei Dinge, die im Review nicht stehen: **bei Tier 1 stand die nicht
ausruestbare Zeile ueber der echten** — ein Spieler, der vergleicht, haette
die falsche gewaehlt. Und ihre Zahl **bewegt sich mit dem Aufstieg nicht**,
weil sie auf der generischen Reinforce-Gruppe 0 sitzt; sie sah bei +4 aus wie
eine Waffe, die sich nicht aufwerten laesst. (128/151 bei Recluse Lv 12 +1
bestaetigt T-046 §8.1 exakt.)

### 1.5 Zwei bestehende Tests mussten mit — das ist eine Vertragsaenderung

`tests/test_damage_facade.py` behauptete zweimal, `rank_candidates` decke
**jede** Zeile des Datensatzes ab (`len(ranked) == len(game_data["weapons"])`
und eine Schleife ueber `game_data["weapons"]`, die auf `KeyError: 33770000`
lief). Beide fragen jetzt `model.offerable_weapons(...)`. Das ist der Vertrag,
der sich aendert, nicht ein Test, der gruen gemacht wird — der Grund steht im
Diff neben der Zeile. **Kein Test geloescht, keiner deaktiviert.**

---

## 2. DR-009 — der Begriff bleibt ganz

Commit `a45bc87`, Golden-Neuaufnahme `8f7b13c`.

`weaponslots.NO_BREAK_SPACE` verbindet die Woerter des Kennzahl-Namens, bevor
er in die eine umbrechende Zeichenkette der Kachel geht. Ergebnis am Fenster:

```
Carian Regal
Scepter
Legendary · 173
Spell power
```

(`docs/screenshots/2026-09-05-T053/weapon-slot-tile-spell-power-whole.png`,
Kontext `build-planner-with-catalyst.png`.)

**Warum nicht der erstgenannte Weg (gestapelte Zeilen wie im Arsenal).** Die
Detailzeile traegt drei Dinge — Raritaet, Kennzahl, Effektzahlen — nicht nur
ein Wertepaar; sie zu stapeln waere ein Umbau der Kachelhoehe im
`Build planner`, dem Tab, den der Auftrag sonst ausnimmt, fuer ein Problem,
das eine Zeile loest. **Warum nicht die Abkuerzung** (`Spell pwr.`, `SP`): sie
gaebe derselben Zahl einen zweiten Namen genau dort, wo der Spieler sie mit
der Arsenal-Kachel vergleicht — AK-64 lehnt einen zweiten Namen im
Nachbarsatz aus demselben Grund ab. Beides steht im Code neben der Konstante.

**Der Test misst den Umbruch, nicht die Zeichenkette.** `QTextLayout` bricht
den echten Kacheltext bei einer Breite in dem Band, in dem der Fehler
auftritt; derselbe Text mit gewoehnlichem Leerzeichen laeuft als Kontrolle
daneben und **muss** brechen, sonst prueft die Breite nichts. Ein Test, der
nur die Zeichenkette liest, waere gruen geblieben, wenn Qt das geschuetzte
Leerzeichen ignorierte.

**Golden-Datei:** zwei Kacheltexte haben sich geaendert, also
neu aufgenommen — zweite der beiden erlaubten Bedingungen (dokumentierte
Entscheidung). Blatt fuer Blatt gegen die alte Datei verglichen, **3
Unterschiede in der ganzen Aufnahme**:

```
cases[10].tiles[0].detail  "236 Spell power" -> "236 Spell\xa0power"
cases[11].tiles[0].detail  "184 Spell power" -> "184 Spell\xa0power"
dataset.extract_version    9 -> 10
```

**Keine einzige Zahl der 18 Faelle hat sich bewegt.** Die beiden
eingefrorenen Aufstiegszahlen 236/184 bleiben ungemessen, wie QA-120 sagt —
diese Neuaufnahme bestaetigt sie nicht und stoert sie nicht.

---

## 3. DR-010 / QA-121 / AK-64 — der Satz steht

Commit `ddfa93a`. Wortlaut aus AK-64, wortgleich, an der vorgegebenen Stelle:

> … plus the +% attack effects your equipped relics grant. **Staves and seals
> show the spell scaling the game displays for them instead of an attack
> rating.** Spell damage is not in the game's data, so spells show their costs
> instead.

Unabhaengig von der Trefferliste, wie AK-64 verlangt. Beleg am Fenster mit
genau dem Aufbau, in dem DR-008/DR-010 aufgenommen wurden (Suche
`"Recluse's Staff"`, Raster zeigt nur Katalysatoren):
`docs/screenshots/2026-09-05-T053/arsenal-recluses-staff-one-card.png`.

---

## 4. DR-011 / AK-63 — nichts zu bauen, und das ist geprueft

Siehe 6.1. Kein UI-Modul liest `SlotPool`, `.unknowns` oder `Goal.scope`; der
Picker mit Berater-Anzeige (S10) existiert nicht. Damit ist AK-63 heute
unerfuellbar **und** unverletzbar. Was ich stattdessen tun konnte, ist die
**Quelle** korrekt zu fuellen — das ist Abschnitt 6.

---

## 5. DR-012 / QA-117 / AK-65 — Schwellen unveraendert, Wirkung gemessen

Commits `0f79672`, `48bb793`.

### 5.1 Was sich geaendert hat: nichts am Bildschirm

Drei Literale haben Namen bekommen (`VISIBLE_CHANGE`, `VISIBLE_PERCENT`,
`COLOURED_CHANGE`), jedes mit seiner Herleitung darueber. **Beleg, dass kein
Pixel wandert:** die Golden-Datei friert die Markup-Ausgabe des Panels fuer 18
Faelle ein und war nach der Umbenennung **ohne Neuaufnahme gruen** (36 von 36).

Zwei der drei Zahlen waren zufaellig gleich (`0.05`) und meinten
Verschiedenes: `VISIBLE_PERCENT` ist die halbe darstellbare Einheit einer
Prozentzahl mit einer Nachkommastelle, `COLOURED_CHANGE` ist ueberhaupt keine
Rundungsgrenze, sondern die Grenze, ab der eine Zelle Farbe bekommt. Genau
diese Gleichheit lud zu der Aenderung ein, die AK-65 verbietet.

### 5.2 Die Wirkung, gemessen statt geschaetzt

`scripts/measure_display_thresholds.py` (neu; Rezept im Modul-Docstring, L-001).
Population: die 1792 angebotenen Waffen, ein Nightfarer, ein Level, ein Tier,
ein attributsteigernder Effekt, gewaehlt durch Befragen von `model.compute`
statt durch eine hingeschriebene Id.

| Population | bewegt sich | heute verborgen | davon durch die 0,6 | verloere bei 0,8333 | kaeme bei 0,3 dazu |
|---|---|---|---|---|---|
| Wylder Lv 15, +1 | 1674 | **13** | **13** | **69** | 13 |
| Wylder Lv 12, +1 | 1674 | 13 | 13 | 69 | 13 |
| Wylder Lv 12, +4 | 1674 | 0 | 0 | 27 | 0 |
| Recluse Lv 12, +1 | 1674 | 0 | 0 | 51 | 0 |
| Recluse Lv 12, +4 | 1674 | 0 | 0 | 2 | 0 |

Lesart, und ich sage die Grenze mit: das sind **Waffen je Population**, nicht
QA-117s 89 — QA-117 hat ueber das ganze Raster `tiles_and_panel` gezaehlt
(viele Builds x Tiers), ich ueber fuenf benannte Punkte. Die Richtung
bestaetigt QA-117: **jede** heute verborgene Zeile ist genau durch die
Kalibrierung verborgen. Und die Gegenrechnung, die bisher nirgends stand:
die Schwelle auf 0,8333 zu heben, um diese 13 zurueckzuholen, **nimmt 69
anderen die Zeile weg**. Das ist AK-65s Argument 2 als Zahl.

### 5.3 Der erste Waechter hatte keine Zaehne — und ich sage es, statt es zu
### verstecken

Die erste Fassung von `tests/test_display_thresholds.py` rechnete ihre beiden
Baender aus `app.VISIBLE_CHANGE` aus — der Konstante, um die es geht. Beide
Mutationen dieser Konstante verschoben die Baender mit und **ueberlebten**:
620 von 622 gruen, die zwei Fehlschlaege waren nur die Ankerpruefungen der
Registry selbst. Gemessen am 05.09., nachgetragen in `48bb793`. Die Baender
gehen jetzt vom **Display** aus (`f"{x:+.0f}"` -> Schritt 1 -> halbe Einheit
0,5) und nicht von der Konstante. L-003 in seiner unangenehmen Form: eine
gruene Suite ueber einem selbstbezueglichen Test ist kein Beleg.

---

## 6. AK-63 / AK-67 — die zwei Vorbehalts-Klassen

Commit `e76123f`.

### 6.1 Erst die Abwesenheitspruefung (Primaerquelle)

* `grep -rn "advisor" --include=*.py nrplanner` ausserhalb von
  `nrplanner/advisor/` — 7 Treffer, **alle Kommentare**.
* `grep -rn "SlotPool|\.unknowns|Goal.scope|goals\." nrplanner/relicpicker.py
  nrplanner/app.py` — **0 Treffer**.
* `grep -rni "unverified"` ueber `nrplanner nrdata tests scripts` — **0**;
  `"not been verified|has not been checked|may be wrong|under investigation"` —
  4 Treffer, alle Kommentar/Testprosa, **keine Oberflaechen-Zeichenkette**.

Damit ist QA-116s Entwarnung heute noch wahr, und AK-63 hat keinen Ort im
gebauten Programm.

### 6.2 Was gebaut ist

* **Konditionale Zeile:** Platzhalter weg, AK-67-Wortlaut wortgleich, Singular
  und Plural.
* **Handle-Zeile:** `of this colour` nur noch am farbigen Slot; am weissen
  `of any colour`. Ein Satzgeruest, zwei Fuellungen, wie AK-67 verlangt.
* **`model.WHITE_SLOT`** ist neu und wird aus `COLOUR_NAMES` gelesen
  (`next(v for v, n in ... if n == "White")`), nicht als 4 geschrieben — die
  Pruefung, die AK-67 dem `developer` ueberlaesst.
* Der Testfall fuer den weissen Slot macht die **blaue** Kopie handle-los,
  waehrend der Rest rot ist: der farbige Slot meldet dann gar nichts und der
  weisse meldet genau sie. Ein Fall, in dem beide Slots dasselbe sagen,
  koennte die zwei Wortlaute nicht unterscheiden.

### 6.3 Wo AK-67 im Kontakt mit dem Code nicht aufgeht — **an den
### `ui-ux-designer`**

AK-67 sagt: *"`SlotPool.unknowns` traegt fuer den heutigen Bestand hoechstens
zwei Saetze."* **Das Feld traegt drei.** Die dritte ist die
Umwandlungszeile aus QA-113, die T-048 gebaut hat; der Nachtrag vom 05.09.
nennt weder sie noch QA-113 in seiner Grundlage. Der Auftrag geht davon aus,
AK-67 liefere den Wortlaut fuer **beide** Platzhalter — er liefert ihn fuer
die konditionale Zeile und fuer die Handle-Zeile (die nie einen Platzhalter
trug). Fuer die dritte gibt es keinen entschiedenen Text.

**Was ich getan habe:** den Platzhalter stehen lassen und ihn ehrlich
beschriftet — `WORDING_PENDING = "[wording pending: QA-113] "` statt
`"[wording pending OF-20] "`, weil OF-20 beantwortet ist und der Marker sonst
auf eine erledigte Frage zeigt. Er erscheint heute **nirgends** am Bildschirm
(S10 ist nicht gebaut). Ein Testfall haelt fest, dass eine unentschiedene
Zeile als solche erkennbar bleibt, und ist so geschrieben, dass er an dem Tag
rot wird, an dem der Wortlaut faellt — der Marker soll absichtlich entfernt
werden, nicht uebersehen.

**Was ich nicht getan habe:** einen Wortlaut erfinden. Das ist die
Entscheidung des `ui-ux-designer`, und AK-67s Satz „hoechstens zwei" muss
dabei mitentschieden werden — entweder er wird auf drei erweitert, oder die
Umwandlungszeile bekommt einen anderen Ort.

---

## 7. Ausgefuehrte Befehle und ihre Ausgabe

```
.venv\Scripts\python.exe -m pytest -q -m "not slow"
  vorher (2e3f374):  592 passed,   5 deselected in  90.16s
  nachher (c3f1bc3): 622 passed,   5 deselected in 104.50s
.venv\Scripts\python.exe -m pytest -q -m "slow"
  nachher:             5 passed, 622 deselected in  50.03s
.venv\Scripts\python.exe -m compileall -q nrplanner nrdata tests scripts
  exit 0, keine Ausgabe
.venv\Scripts\python.exe run.py
  Fenster erschien, Save gelesen (309 Relikte), sauber beendet (exit 0)
```

30 neue Faelle: 6 (`test_unequippable_catalyst`) + 3 (`test_weapon_slot_tile_wrap`)
+ 7 (`test_pool_finding_wording`) + 5 (`test_display_thresholds`) + 1
(`test_arsenal_tab_asks_the_facade`) + 8 (je eine Ankerpruefung pro neuer
Mutation).

**Kein Linter ist im Repo konfiguriert** (`pytest.ini` ist die einzige
Werkzeugkonfiguration, `requirements-dev.txt` enthaelt nur pytest). Statt
dessen: `compileall` sauber, und alle neu hinzugefuegten Zeilen unter 80
Spalten geprueft — die einzigen Ueberlaeufe sind Mutations-Anker, die laut
`mutate.py` woertlich sein muessen, und JSON der Golden-Datei.

## 8. Die acht Mutationen, gegen den ausgelieferten Stand gefahren

Jede auf einer frischen `git archive HEAD`-Kopie (`c3f1bc3`), Suite `-m "not
slow"`. **Alle acht tot.**

| Mutation | rot / gruen | wer sie toetet |
|---|---|---|
| `unequippable-catalyst-offered-again` | 7 / 615 | 5 der 6 Faelle in `test_unequippable_catalyst.py` |
| `unequippable-catalyst-criterion-without-its-family` | 13 / 607 | 3 Faelle dort + `arsenal_tab_asks_the_facade`, `arsenal_tab_wiring` (2), `damage_facade`, `move_scoped_effects`, `display_thresholds` |
| `figure-name-broken-across-the-wrap` | 5 / 617 | 2 Faelle in `test_weapon_slot_tile_wrap.py` + 2 Golden-Faelle |
| `arsenal-summary-defines-one-figure-of-two` | 2 / 620 | `test_the_summary_defines_both_figures_the_grid_can_show` |
| `handle-line-names-a-colour-the-white-slot-has-not` | 2 / 620 | `test_the_handle_line_at_a_white_slot_names_every_colour` |
| `settled-wording-still-marked-as-pending` | 4 / 618 | 3 Faelle in `test_pool_finding_wording.py` |
| `display-threshold-raised-with-the-calibration` | 4 / 618 | `test_the_threshold_is_half_a_printed_unit…`, `test_a_row_just_over_the_threshold_is_shown` |
| `display-threshold-lowered-with-the-calibration` | 4 / 618 | `test_the_threshold_is_half_a_printed_unit…`, `test_a_row_just_under_the_threshold_is_not_shown` |

**Beim Zaehlen abzuziehen:** in jeder Zeile ist zusaetzlich
`test_differential_track::test_every_mutation_still_finds_its_anchor_in_the_real_source`
rot, weil die Mutation ihren eigenen Anker verbraucht hat. Wo zwei Mutationen
denselben Anker teilen (die beiden `model.py`- und die beiden
`app.py`-Eintraege), sind es zwei. Das ist Vorbestand (T-048 hat dasselbe
gemeldet) und **kein** Kill.

**L-007 — welche Aenderung braecht jeden Test heute:**

* `test_unequippable_catalyst`: `is_unequippable_catalyst` gibt `False` zurueck
  (Mutation 1) bzw. verliert die Familienpruefung (Mutation 2).
* `test_weapon_slot_tile_wrap`: `replace(" ", NO_BREAK_SPACE)` faellt weg.
* Arsenal-Zusammenfassung: der mittlere Satz faellt weg.
* Handle-Zeile: `reach` fest auf `"this"`.
* Konditionale Zeile: der Marker steht wieder davor.
* Schwellen: `VISIBLE_CHANGE` mit 0,6 multipliziert bzw. dividiert.

**Eine ueberlebende Zusicherung, ausdruecklich benannt:**
`test_an_older_dataset_loses_no_catalyst` bleibt unter Mutation 1 gruen. Das
ist richtig — der Fall bewacht die Lesart eines **fehlenden** Feldes ("kein
Filter" ist die korrekte Antwort darauf), nicht die Existenz des Filters. Wer
Kills zaehlt, darf ihn nicht mitzaehlen.

---

## 9. Am laufenden Fenster angesehen (QA-122)

`docs/screenshots/2026-09-05-T053/`, alle aus einem **gezeigten** Fenster mit
der Palette des Programms (`app.setStyle("Fusion")`,
`app.setPalette(_dark_palette())`), nicht aus der Offscreen-Plattform der
Suite:

| Datei | was sie belegt |
|---|---|
| `run-py-starts.png` | `run.py` laeuft gegen Extraktor 10, Save gelesen |
| `arsenal-recluses-staff-one-card.png` | **eine** Karte wo zwei waren; AK-64-Satz sichtbar |
| `weapon-slot-tile-spell-power-whole.png` | `Legendary · 173` / `Spell power`, ungebrochen |
| `build-planner-with-catalyst.png` | dieselbe Kachel neben ihren fuenf Nachbarn |
| `armament-dialog-recluses-staff.png` | eine Zeile, ohne Id daneben |

Die Gegenstuecke des Reviews liegen unveraendert in
`docs/screenshots/2026-09-05/`.

Zusaetzlich **mit angesehen und in Ordnung befunden**: die Total-Zeile des
Panels (`Spell power 173 no change 173`) bricht nicht — der Bereich ist breit
genug; DR-009 betrifft nur die enge Kachel.

---

## An den `qa-engineer`

1. **Der Filter ist der Kern.** Randfaelle, die ich nicht abgedeckt habe:
   ein **gespeicherter Build**, der 33770000 in einem Waffenslot haelt.
   `app._weapon_by_id` sucht bewusst weiter im ganzen Datensatz, damit so ein
   Build ladbar bleibt; die Kachel zeigt die Waffe dann, obwohl sie in keiner
   Liste mehr waehlbar ist. Ich halte das fuer richtig (Daten des Spielers
   nicht stillschweigend verlieren), aber **gesehen hat es niemand**.
2. **Die Differential-Strecke zaehlt ab jetzt 1792 statt 1793 Arsenal-Zeilen.**
   Ein Skelettvergleich gegen eine aeltere Aufnahme wird genau eine fehlende
   Zeile melden. Das ist die Aenderung, kein Fehler.
3. **`EXTRACT_VERSION` 10:** der erste Start nach diesem Stand baut den Cache
   neu (~16–40 s). Auf einer Maschine ohne Spiel bleibt ein alter Snapshot
   liegen und `is_unequippable_catalyst` antwortet dann bewusst „nein" —
   d. h. dort erscheinen wieder zwei `Recluse's Staff`. Beabsichtigt (lieber
   eine Zeile zu viel als 30 fehlende), aber pruefenswert.
4. **AK-66 gegen die verbliebenen Kollisionen:** `Finger Seal` (2 Zeilen) und
   `Scholar's Thrusting Sword` (4) tragen weiter ihre Id im Auswahldialog. Ein
   Fall prueft das; am Fenster habe ich nur `Recluse's Staff` fotografiert.
5. **DR-009 an anderen Schriftgroessen:** der Test faehrt eine Breite im
   gefaehrlichen Band aus. Bei `UI scale` ungleich „Automatic" habe ich nicht
   nachgesehen.
6. **Mutationszaehlung:** siehe die zwei Hinweise am Ende von Abschnitt 8
   (Ankerpruefungen abziehen, `test_an_older_dataset_loses_no_catalyst` nicht
   als Kill zaehlen).

## An den `ui-ux-designer` (ueber den `director`)

1. **AK-67 deckt zwei Saetze, das Feld traegt drei** (Abschnitt 6.3). Bitte
   Wortlaut fuer die Umwandlungszeile (QA-113) **und** eine Entscheidung, ob
   „hoechstens zwei Saetze" auf drei geht.
2. **DR-009: ich habe den zweiten Weg gewaehlt**, nicht die gestapelten
   Zeilen (Begruendung Abschnitt 2). Falls die Vorlage-Struktur des Arsenals
   gewollt war, ist das ein eigener, groesserer Auftrag am `Build planner`.
3. **AK-64 ist woertlich umgesetzt**, ohne Bindung an die Trefferliste — wie
   vorgegeben. Nebenwirkung: die Zeile ist jetzt drei Saetze lang und laeuft
   am Standardmass auf zwei Zeilen um (siehe Screenshot). Kein Umbruch mitten
   im Begriff, aber es ist mehr Text als vorher.

## An den `director`

**Sicherheitsfunde:** keine. Der neue Code liest nur bereits gelesene
Param-Felder; kein Netz, kein Schreibzugriff, keine Secrets.

**Performance:** keine Auffaelligkeit. Der Filter ist ein
Praedikat pro Waffe in einer Liste, die ohnehin 1793-mal bewertet wird; der
Suitelauf wuchs von 90 s auf 105 s, und das sind die 30 neuen Faelle, nicht
das Programm.

**Debt, gefunden, nicht behoben (dein Ruf, nicht meiner):**

1. **Der weisse Slot steht dreimal im Baum.** Neu und kanonisch:
   `model.WHITE_SLOT` (aus `COLOUR_NAMES` abgeleitet). Vorbestand:
   `app.WHITE_SLOT = 4` und der Vorgabewert `white_slot: int = 4` in
   `inventory.relics_for` / `inventory.available`. Ich habe sie **nicht**
   zusammengefuehrt (Auftragsgrenze). Aufwand klein, Risiko klein, aber es
   ist ein Refactoring quer durch drei Module.
2. **`EXTRACT_VERSION` 10 gehoert in die Release-Notiz:** jeder vorhandene
   Cache baut sich beim naechsten Start einmal neu. Verhalten war schon so
   gebaut; neu ist nur, dass es diesmal wirklich ausgeloest wird.
3. **QA-118** (die alte Fassung von `test_move_scoped_effects.py` ist gegen
   das neue Programm gruen — Klasse L-007) steht weiter offen und war nicht
   Teil dieses Auftrags.

**Deine zwei Vorgaben habe ich uebernommen, nicht neu entschieden:** die
Doppelnennung bei QA-113 bleibt (ich habe an der Zaehlung nichts geaendert),
und `model.Build.level` habe ich nicht angefasst.

**Selbstmeldung, damit sie nicht untergeht:** ich habe DR-009 committet, bevor
die volle Suite lief, und dabei zwei Golden-Faelle gebrochen; gefunden habe
ich es erst beim naechsten Mutationslauf. Behoben in `8f7b13c` mit
Blattvergleich. Der Fehler war der Ablauf, nicht das Ergebnis — aber er
haette ohne den Mutationslauf bis zur QA gelegen.

## Definition of Done

- [x] Anforderung verstanden, Annahmen im Kopfblock dokumentiert
- [x] Build & Tests gruen in der benannten Umgebung (Windows 10,
      `.venv\Scripts\python.exe`): 622 passed / 5 deselected, slow 5 passed
- [x] Neue Tests fuer jede neue Logik; je Waechter eine toetende Mutation,
      gefahren, Ergebnis in Abschnitt 8
- [x] Kein Linter konfiguriert; `compileall` sauber, Zeilenbreite geprueft
- [x] Keine Secrets. **Ein** bewusster Platzhalter bleibt (Abschnitt 6.3),
      begruendet und mit einem Test, der ihn sichtbar haelt; kein toter Code
- [x] QA-Kriterien selbst durchgespielt, am laufenden Fenster, mit
      Screenshots
- [ ] **Ungeprueft:** jede Plattform ausser Windows 10. Das Programm ist
      Windows-only (GOAL.md), aber gesagt sei es.
