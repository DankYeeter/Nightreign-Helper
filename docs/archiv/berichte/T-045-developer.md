# T-045 / T-050 — Der gemessene Faktor 0,6, sein Beleg und die Waechter (developer)

```
STATUS: erledigt
AUFTRAG: T-045 (Faktor 0,6 einziehen, Abschneiden an der Anzeige,
         Charakterisierung gegen Spielwerte) samt Director-Nachtrag,
         fortgesetzt durch T-050 (Vergleichslauf und Bericht)
GELESEN: docs/tasks/T-050.md, docs/tasks/T-045.md (mit Nachtrag), GOAL.md,
         docs/state.md, scripts/differential/__init__.py, capture.py, plan.py,
         compare.py, mutate.py, rasters/tiles_and_panel.json,
         rasters/arsenal_tab.json, nrplanner/weapons.py, nrplanner/damage.py,
         nrplanner/app.py, nrplanner/arsenaltab.py, nrplanner/weaponslots.py,
         nrplanner/advisor/goals.py, tests/weapon_damage_cases.py,
         tests/test_attack_power_against_the_game.py,
         tests/data/game_attack_power.json, tests/test_differential_track.py,
         tests/test_one_build.py (AD-021-Waechter), README.md,
         UI_SPEC.md, ARCHITECTURE.md, git show 99ed022 0dc54a6 82c4c1f
         cb12a50 46edbb9
GEAENDERT: scripts/differential/ratios.py (neu), tests/test_differential_track.py
           (zwoelf Faelle ergaenzt) - beide committet als 6b7a0d2;
           docs/berichte/T-045-developer.md (diese Datei)
ANNAHMEN: (1) Der Vergleichslauf darf ein Auswertungsskript bekommen, das die
          vorhandenen Aufnahmen liest - siehe Abschnitt 8, ich habe die
          Strecke benutzt und nicht neu gebaut, aber um ein fuenftes Skript
          ergaenzt, weil die geforderte Zahl sonst nicht nachfahrbar waere.
          (2) "Verhaeltnis auf 1 ULP" ist als Anforderung an die einzelne
          gemessene Zahl gelesen, nicht an eine Mittelung.
NAECHSTER: qa-engineer (Retest der vier Abnahmepunkte aus T-045)
BLOCKIERT DURCH: nichts
```

**Herkunft:** Die Umsetzung (Konstante, Abschneiden, Charakterisierung,
Texte, Klammerung) stammt aus dem am 03.09.2026 am Wochenlimit
abgebrochenen T-045-Lauf und liegt in den fuenf Commits `99ed022`,
`0dc54a6`, `82c4c1f`, `cb12a50`, `46edbb9`. **Von mir stammt alles ab
Abschnitt 1 dieses Berichts:** der Vergleichslauf ueber beide Raster, beide
Mutationslaeufe, die Nachmessung der Golden-Werte, die Gegenprobe der
T-041-Vorhersage, die Suche nach dem alten Vorbehaltssatz, das
Auswertungsskript `scripts/differential/ratios.py` mit seinen zwoelf
Waechtern und dieser Bericht. Ich habe an der Umsetzung **keine Zeile
Anwendungscode geaendert**, weil der Vergleichslauf sauber ist.

---

## 1. Was gefahren wurde

Alter Baum `89015aa` (Stand vor `99ed022`) gegen `HEAD` (= `46edbb9`),
beide Raster, ganze Strecke, `PYTHONHASHSEED=0` **vor** dem
Interpreterstart:

```
git archive --format=tar 89015aa | tar -x -C <alt>
export PYTHONHASHSEED=0
.venv/Scripts/python.exe scripts/differential/plan.py \
    scripts/differential/rasters/tiles_and_panel.json -o plan_tiles.json
.venv/Scripts/python.exe scripts/differential/capture.py plan_tiles.json \
    -o tiles_new.jsonl
.venv/Scripts/python.exe scripts/differential/capture.py plan_tiles.json \
    -o tiles_old.jsonl --tree <alt>
.venv/Scripts/python.exe scripts/differential/compare.py \
    tiles_old.jsonl tiles_new.jsonl
.venv/Scripts/python.exe scripts/differential/ratios.py \
    tiles_old.jsonl tiles_new.jsonl
```

und dasselbe mit `rasters/arsenal_tab.json`.

| Raster | Waffen | Konfigurationen | Faelle |
|---|---|---|---|
| `tiles_and_panel` | 1793 (jede) | 14 | 25 102 |
| `arsenal_tab` | 1793 (jede) | 4 | 7 172 |

Datensatz beider Plaene und beider Baeume: `data_version 10350000`,
`extract_version 8`, `regulation_sha256 876a3ca2…`. `capture.py` bricht bei
Abweichung ab; beide Aufnahmen liefen durch, die Kopfzeile jeder Aufnahme
weist den benutzten Baum aus (`nrplanner from …\scratchpad\old` bzw.
`… \Nightreign-Helper`), das Messgeraet
(`tests/weapon_damage_cases.py`) kam in beiden Faellen aus dem HEAD-Checkout.

## 2. Was `compare.py` sagt: alles hat sich bewegt

| Feld | tiles_and_panel | arsenal_tab |
|---|---|---|
| Datensaetze verglichen | 25 102 | 7 172 |
| davon unterschiedlich | 25 102 (100 %) | 7 172 (100 %) |
| `tiles` | 25 102 (43 032 einzelne Kacheltexte) | 7 172 |
| `last_ar` / `panel` / `breakdown` | je 23 309 (92,9 %) | je 7 172 |
| `arsenal_figure` | – | 7 172 |
| `arsenal_tiles` | – | 7 122 (99,3 %) |

Die 25 102 − 23 309 = 1 793 Faelle ohne bewegte Tafel sind genau die
Konfiguration „three tiles and an empty slot active, so none of them is" —
dort ist die aktive Kachel leer, es gibt keine Angriffskraft zu zeigen. Die
Kacheln bewegen sich trotzdem, weil die anderen drei belegt sind.

Das ist die Auskunft, die `compare.py` geben kann, und sie beantwortet die
Frage von T-045 Punkt 3 nicht: **dass** sich alles bewegt hat, war der Zweck.
Wie **weit**, sagt Abschnitt 3.

## 3. Der Beleg: jede bewegte Zahl und um wie viel

`ratios.py` sortiert jeden Blattwert beider Aufnahmen in drei Sorten. Die
Trennung ist nicht geraten, sondern folgt der Art des Wertes (Abschnitt 8
erklaert die Herleitung):

| | tiles_and_panel | arsenal_tab | zusammen |
|---|---|---|---|
| **exakte Zahlen** (als `float.hex()` aufgenommen) | 85 358 | 30 481 | **115 839** |
| davon mit Faktor mitgezogen, ≤ 1 ULP | 69 123 | 28 622 | **97 745** |
| davon bitgleich stehengeblieben | 15 431 | 1 793 | **17 224** |
| davon **weiter als 1 ULP** (Abschnitt 4) | 804 | 66 | **870** |
| davon auf beiden Seiten null | 0 | 0 | **0** |
| **ganze Zahlen auf dem Bildschirm** | 463 407 | 126 433 | **589 840** |
| davon unveraendert | 200 819 | 44 825 | **245 644** |
| davon durch Abschneiden erreichbar | 250 017 | 76 229 | **326 246** |
| davon durch Runden erreichbar | 12 571 | 5 379 | **17 950** |
| davon durch **keine** der beiden Regeln | 0 | 0 | **0** |
| **identische Texte** | 308 396 | 184 925 | **493 321** |
| **Texte mit bewegtem Skelett** (Abschnitt 4) | 156 | 0 | **156** |

Die drei Sorten, die T-045 auseinanderhalten wollte, fallen dabei
mechanisch auseinander — nicht per Toleranz ueber alles:

1. **Mitgezogene Rechengroessen.** Jede Zahl in `last_ar.base/scaled/final`
   und jede `arsenal_figure`. Sie werden gegen `fl(alt × 0,6)` in derselben
   `double`-Arithmetik geprueft, die das Programm benutzt, und der Abstand
   wird in ULP **bitweise** gezaehlt (`struct`-Umdeutung), nicht ueber
   `abs(a-b)/ulp(b)` geschaetzt.
2. **Zahlen, die den Faktor nie gesehen haben.** Alle 17 224 bitgleichen
   Zahlen sind Multiplikatoren: `last_ar.rates.physicsAttackRate` (14 304 +
   1 793), `.magicAttackRate` 455, `.darkAttackRate` 240, `.fireAttackRate`
   228, `.thunderAttackRate` 203, `.physicsAttackPowerRate` 1. **Keine
   einzige** hat sich bewegt. Dazu unveraendert: `arsenal_kind`,
   `arsenal_tier`, `arsenal_listed`, `arsenal_summary` in allen 7 172
   Faellen, jeder Kacheltitel (150 612 + 43 032) und jeder Waffenname.
3. **Abgeschnittene Anzeigewerte.** Sie koennen kein Verhaeltnis zeigen,
   weil die beiden Baeume aus einer Zahl nicht nach derselben Regel eine
   Ziffer machen. Sie werden gegen die hergeleitete Klammer geprueft
   (Abschnitt 8) — und zusaetzlich, wo die Zahl hinter der Ziffer in der
   Aufnahme steht, gegen die Regel selbst:

> **121 924 gerenderte Gesamtzahlen** (93 236 aus `tiles_and_panel`,
> 28 688 aus `arsenal_tab`) wurden gegen die Zahl geprueft, aus der sie
> entstanden sind: auf der alten Seite muss `round(figure)` dastehen, auf
> der neuen `math.floor(figure)`. **0 widersprechen.** Damit ruht der
> Anzeigeteil nicht nur auf der Klammer, sondern auf der Regel.

## 4. Die Abweichungen, die nicht 0,6 sind — gemeldet, nicht einsortiert

### 4.1 870 Zahlen jenseits der 1-ULP-Schranke

| Feld | 2 ULP | 3 ULP |
|---|---|---|
| `last_ar.final` (tiles) | 424 | 15 |
| `last_ar.base` (tiles) | 197 | – |
| `last_ar.scaled` (tiles) | 168 | – |
| `arsenal_figure` (arsenal) | 65 | 1 |
| **Summe** | **854** | **16** |

Verhaeltnisse, vollstaendig — es sind vier verschiedene Werte:

| Verhaeltnis | Anzahl |
|---|---|
| 0.6000000000000001 | 365 |
| 0.5999999999999999 | 300 |
| 0.5999999999999998 | 146 |
| 0.6000000000000002 | 59 |

Groesster Abstand: 0,5999999999999998 (relativ 3,7 × 10⁻¹⁶), gemessen an
`.last_ar.final` in „multiplier and attributes at once, tier 3, alone and
active :: armament 2150000", 284,1243960675422 → 170,47463764052526.

**Mechanismus, und warum es keine zweite Ursache gibt.** Jede dieser 870
Zahlen ist eine **Summe**: `last_ar.base/scaled/final` sind Summen ueber
Schadensarten, `arsenal_figure` ist `sum(scaled_per_type().values())` bzw.
`final_total`. Der Faktor sitzt seit `46edbb9` an der fertigen Zahl **je
Schadensart**; eine Summe getrennt gerundeter Summanden ist nicht die
gerundete Summe. Genau das steht als Kommentar in `nrplanner/weapons.py`
neben `result.scaled`. Zwei unabhaengige Beobachtungen stuetzen den
Mechanismus statt der Behauptung:

* Im Raster `arsenal_tab` sind **alle** 7 172 `last_ar.base/scaled/final`
  innerhalb 1 ULP — dort steckt in Slot 1 fest Wylders Startwaffe mit genau
  einer Schadensart, die „Summe" hat einen Summanden, und der Rest
  verschwindet.
* Die 16 Werte bei 3 ULP stehen ausschliesslich in `final` bzw.
  `arsenal_figure`, also hinter einer **weiteren** Multiplikation (der
  Multiplikatorschicht), waehrend `base` und `scaled` bei 2 ULP aufhoeren.

**Wertung:** Das ist eine Abweichung von der Erwartung „1 ULP je Wert" und
wird als solche gemeldet. Sie ist kein anderer Faktor — der groesste
gemessene Abstand vom Faktor betraegt 4 Einheiten der 16. Dezimale — und sie
ist aus `weapons.rate()` heraus nicht zu beseitigen. Was T-045 Punkt 3 als
Erwartung formuliert, gilt fuer die **Zahl je Schadensart**; die Messstrecke
nimmt aber nur die Summen auf, weshalb die per-Typ-Aussage aus dem
Commit-Text `46edbb9` (0 von 350 160 ausserhalb 1 ULP) durch diesen Lauf
**nicht** bestaetigt wird — siehe Abschnitt 10, Befund D-3.

### 4.2 156 Texte, deren Skelett sich bewegt hat

Alle im Raster `tiles_and_panel`, keiner im Arsenal-Tab. Zwei Ursachen, beide
eine Schwelle der Anzeige, unter die ein um 0,6 geschrumpfter Unterschied
faellt:

| Anzahl | Ort | Was passiert | Schwelle im Code |
|---|---|---|---|
| 89 | `breakdown` | die Zeile `From attributes  <b>+1</b>` faellt weg | `app.py`: `if abs(from_attributes) >= 0.5:` |
| 66 | `panel` | eine Aenderungszelle `+1` wird zu `—` | `app.py`: `change = f"{diff:+.0f}" if abs(diff) >= 0.5 else "—"` |
| 1 | `panel` | die Aenderungszelle bleibt `—`, wechselt aber die Farbe GOOD → MUTED | `app.py`: `colour = GOOD if diff > 0.05 else …` |

Die 89 sind **nachgerechnet, nicht vermutet**: fuer jeden der 89 Faelle gilt
in den aufgenommenen Zahlen `|scaled − base| >= 0,5` vorher und `< 0,5`
nachher — 89 von 89. Der Farbfall ist „armament 5050900", dort liegt der
Typbeitrag vorher zwischen 0,05 und 0,0833 und nachher darunter.

**Wertung:** kein falscher Wert, sondern eine Anzeigeschwelle, die tut, was
sie soll. Sie ist trotzdem eine sichtbare Aenderung fuer den Nutzer und
gehoert deshalb hier hin und nicht in eine Fussnote: auf schwachen
Attributbeitraegen zeigt die Klicktafel eine Zeile weniger als vorher.

## 5. Die Waechter und ihre toetenden Mutationen — beide selbst gefahren

Beide Mutationen aus `0dc54a6`, jede in einer eigenen Extraktion von `HEAD`
(`git archive HEAD | tar -x`), angewandt mit `scripts/differential/mutate.py
--apply … --tree …`, danach die ganze Suite mit `-m "not slow"` **in dem
mutierten Baum**. Belegt ist, dass der Eingriff wirklich im Baum steht
(`GAME_ATTACK_POWER_RATE = 1.0` in Zeile 69 bzw. `return round(figure)` in
Zeile 111) und dass der jeweils andere Baum unberuehrt blieb.

### `attack-power-rate-neutralised` (0,6 → 1,0)

**60 failed, 366 passed, 5 deselected.** Rot in:

| Datei | Faelle |
|---|---|
| `tests/test_attack_power_against_the_game.py` | **24** (alle 23 Ablesungen + `test_the_factor_is_named_once_and_is_the_measured_one`) |
| `tests/test_weapon_damage_golden.py` | 34 |
| `tests/test_damage_facade.py` | 1 (`test_armaments_that_rate_alike_come_back_in_one_fixed_order`) |
| `tests/test_differential_track.py` | 1 (`test_every_mutation_still_finds_its_anchor_in_the_real_source[attack-power-rate-neutralised]` — der Beleg, dass der Eingriff gelandet ist) |

Mechanismus-gebundenes Signal, nicht nur ein Exitcode:

```
AssertionError: "Soldier's Crossbow" for Wylder at level 12:
the game shows 88, this program shows 148 (unrounded 148.0)
```

148 ist genau der alte Programmwert; 88 = `floor(0,6 × 148)`.

### `attack-power-rounded-instead-of-truncated` (`math.floor` → `round`)

**26 failed, 400 passed, 5 deselected.** Rot in:

| Datei | Faelle |
|---|---|
| `tests/test_attack_power_against_the_game.py` | **10** von 23 Ablesungen |
| `tests/test_weapon_damage_golden.py` | 15 |
| `tests/test_differential_track.py` | 1 (Ankerbeleg wie oben) |

```
AssertionError: "Soldier's Crossbow" for Wylder at level 12:
the game shows 88, this program shows 89 (unrounded 88.8)
```

Genau die zehn Ablesungen mit Nachkommaanteil ≥ 0,5 fallen — die Zahl, die
der Dateikopf vorhersagt. `test_at_least_one_reading_tells_truncation_from_rounding`
bleibt dabei **gruen**, und das ist richtig so: der Fall prueft eine
Eigenschaft der Daten (dass eine solche Ablesung in der Datei steht), nicht
das Verhalten von `displayed`. Ohne ihn koennte die zweite Mutation
ueberleben; er ist der Grund, dass sie es nicht tut.

**AD-021-Waechter** (`tests/test_one_build.py::test_only_the_facade_calls_
weapons_rate_or_rank`) ist im unveraenderten Baum gruen; `weapons.rate`/`rank`
wird ausserhalb von `nrplanner/damage.py` an keiner Stelle aufgerufen, die
uebrigen Fundstellen in `advisor/goals.py` und `arsenaltab.py` sind
Kommentartext.

## 6. Die geaenderten Golden-Werte mit Verhaeltnis

Nachgemessen aus `git show 89015aa:tests/golden/weapon_damage.json` gegen
`git show HEAD:…`, Wert fuer Wert:

* **396 Werte unveraendert**, **51 Zahlen bewegt**, **52 Texte bewegt**,
  0 Werte anderer Art bewegt.
* Verhaeltnis der 51 Zahlen: min 0,5999999905630028, max 0,6000000043031785.
  **0 von 51** liegen weiter als 1 × 10⁻⁶ von 0,6.
  Groesster Abstand 9,437 × 10⁻⁹ bei `.cases[10].expected.last_ar.base`
  (42,386364 → 25,431818) — vollstaendig aus der 6-Dezimal-Rundung, mit der
  `weapon_damage_cases.rounded()` die Datei schreibt.
* Die 51 Zahlen sind je Fall `last_ar.base`, `last_ar.scaled`,
  `last_ar.final`: 17 der 18 Faelle × 3, der 18. ist „empty tile“
  und haelt keine Zahl.
* Von den 52 bewegten Texten hat **kein einziger** ein bewegtes Skelett; sie
  enthalten 156 geaenderte Bildschirmzahlen, alle innerhalb der
  hergeleiteten Klammer, groesster Abstand |neu − 0,6 × alt| = 1,0.
* **Keine Multiplikatorkarte** hat sich bewegt (die `rates`-Eintraege sind
  Teil der 396 unveraenderten Werte).

Damit ist die Angabe aus dem Commit-Text von `99ed022` unabhaengig
nachgemessen und bestaetigt.

## 7. Fundstellen des alten Vorbehaltssatzes

Gesucht projektweit mit vier unabhaengig formulierten Masken (L-006), jeweils
ueber `*.py`, `*.md`, `*.json`, `*.txt` ohne `.git`:

| Maske | Treffer |
|---|---|
| `has not been verified against an in-game number` | 3 |
| `in-game number` | 9 |
| `verified against` | 17 (davon 1 in `.venv`, 5 in Auftrags-/Berichtsdateien) |
| `not (yet )?been (verified\|checked)\|never been (verified\|checked)` | 13 |

**Erledigt (der Satz ist weg und durch den Geltungsbereich ersetzt):**

* `README.md` „Known limits", Z. 546–557: zwei Punkte, der zweite nennt
  Staebe und Siegel ausdruecklich als Ausnahme mit umgekehrter Reihung.
* `nrplanner/advisor/goals.py` Z. 82–99: `_ATTACK_RATING_UNKNOWNS` traegt
  vier Zeilen, die ersten beiden sind Geltungsbereich und Katalysator-
  Ausnahme. Der Director-Nachtrag ist damit erfuellt.
* `tests/test_advisor_goals.py` Z. 112–127 haelt das fest
  (`assert not any("has not been verified" in line …)`).

**Steht noch da — nicht meine Dateien, deshalb gemeldet statt geaendert:**

| Datei | Zeile | Wortlaut |
|---|---|---|
| `ARCHITECTURE.md` | 513 | „Attack rating has not been verified against an in-game number." als Inhalt, den `unknowns` *immer mindestens* enthalte |
| `UI_SPEC.md` | 192 | derselbe Satz als Pflichtzeile des Berater-Dialogs |
| `UI_SPEC.md` | 1221–1222 | derselbe Satz als eine von zwei zur Wahl stehenden Fassungen |
| `UI_SPEC.md` | 696 | **anderer Wortlaut**: „Attack rating has not been checked against the game, so these figures may be wrong." im Picker-Bildschirm |
| `UI_SPEC.md` | 981, 1201 | derselbe andere Wortlaut, als AK-37 bzw. als „Der Vorbehalt selbst bleibt" |

`docs/berichte/T-037-developer.md:525` und die Auftragsdateien nennen den Satz
historisch; die habe ich nicht mitgezaehlt.

**Wichtig fuer den Director:** T-045 Punkt 5 nannte nur „UI_SPEC 3.2". Es sind
**zwei verschiedene Wortlaute an sechs Stellen in zwei Dateien**, und
`ARCHITECTURE.md` war in keinem Auftrag benannt. Wer nur nach dem einen Satz
sucht, findet die drei Picker-Stellen nicht.

**Entwarnung zur Oberflaeche, direkt geprueft:** keiner der beiden Wortlaute
steht heute im Programmcode. `grep` ueber `nrplanner/` nach „checked against
the game", „attack-power display", „may be wrong", „Not checked", `unverified`
findet ausschliesslich Kommentare und Testtext. Der Arsenal-Tab-Text
(`arsenaltab.py` Z. 306–311) enthaelt keine Verifikationsaussage mehr, und
`arsenal_summary` ist in allen 7 172 Aufnahmen auf beiden Seiten identisch.
Das Programm zeigt also keinen ueberholten Vorbehalt an; UI_SPEC beschreibt
Zeichenketten, die es nicht mehr gibt.

## 8. Was ich hinzugefuegt habe und warum (`scripts/differential/ratios.py`)

**Das ist die einzige Erweiterung des Auftragsumfangs, und sie steht hier
oben statt in einer Fussnote.** `compare.py` kann die von T-045 Punkt 3
verlangte Aussage nicht liefern: es sagt, **dass** ein Feld sich bewegt hat,
nie **um wie viel**. Ohne ein Skript waere die zentrale Zahl dieses Berichts
eine Behauptung, die niemand nachfahren kann — genau die Lage, wegen der die
Strecke ueberhaupt im Repo liegt (QA-075, L-001). Ich habe die Strecke
**benutzt** (dieselben Plaene, dieselben Aufnahmen, dieselben Aufrufwege) und
um ein fuenftes Skript ergaenzt, das nur die Aufnahmen liest. Kein
Anwendungscode ist beruehrt.

Die Klammer fuer Bildschirmzahlen ist hergeleitet, nicht gewaehlt:

```
alt   f"{x:.0f}"                 =>  |x_alt - gezeigt_alt| <= 0,5
neu   damage.displayed = floor   =>  0 <= x_neu - gezeigt_neu < 1
      (Aenderungszeilen weiter f"{d:+.0f}")
Behauptung  x_neu = 0,6 * x_alt
=> gezeigt_neu muss aus [0,6*(gezeigt_alt-0,5); 0,6*(gezeigt_alt+0,5)]
   unter einer der beiden Regeln erreichbar sein
```

Das Intervall ist 0,6 breit und laesst hoechstens **zwei** ganze Zahlen zu;
welche Regel eine Zahl gezogen hat, wird nicht geraten, sondern beide werden
versucht und getrennt gezaehlt.

**Zwoelf Faelle in `tests/test_differential_track.py`, jeder mit Gegenbau
gefahren** (acht Eingriffe, je einer allein, Datei danach per SHA-256
zurueckgeprueft):

| Eingriff | rot geworden |
|---|---|
| 1-ULP-Schranke → 3 ULP | 1 Fall |
| Anzeigeklammer vervierfacht | 2 Faelle |
| beide Rundungsregeln als „Abschneiden" gezaehlt | 1 Fall |
| Skelettvergleich der Texte entfernt | 2 Faelle |
| Tokenizer liest Ziffern aus Farben | 1 Fall |
| Tokenizer liest Ziffern aus `10px` | 1 Fall |
| Null auf beiden Seiten als „skaliert" gezaehlt | 1 Fall |
| Feldvereinigung → nur Felder der alten Aufnahme | 1 Fall |

Der Farbfall ist die Stelle, an der der erste Anlauf **nichts** belegte: mit
`#6fbf73`/`#8a8a8a` blieb die Suite gruen, weil die Palette dieses Programms
Buchstaben enthaelt und der Lookahead die Ziffern ohnehin haelt. Der Fall
steht jetzt auf `#116622`/`#884422` — in CSS genauso gueltig — und toetet den
Eingriff. Das ist ausdruecklich vermerkt, weil ein Waechter ohne Gegenbau
kein Waechter ist (L-002).

## 9. Die T-041-Vorhersage: eingetreten, aber nicht ganz

Der `qa-engineer` hatte vorhergesagt, **kein einziger Fall der Advisor-Suite**
werde von dieser Aenderung rot, weil dort alles relativ charakterisiert ist.

**Gemessen** (HEAD-Programm mit der Testsuite aus `89015aa`, `-m "not slow"`,
41 failed / 359 passed): **zwei Faelle der Advisor-Suite sind rot geworden.**

| Fall | Warum |
|---|---|
| `test_the_damage_goal_always_carries_the_attack_rating_reservation` | die `unknowns`-Zeile wurde ersetzt — Punkt 5 des Auftrags, nicht der Faktor |
| `test_the_score_is_unrounded_and_the_display_is_the_rounded_one` | prueft `f"{score.value:.0f}" in score.display`, also eine **zweite Kopie der Anzeigeregel im Test** |

Der Kern der Vorhersage stimmt: **kein einziger Fall ist rot geworden, weil
ein Wert oder eine Rangfolge sich bewegt haette.** Falsch ist der Schluss
„nichts wird rot": rot wurde, was eine absolute **Darstellung** oder einen
**Text** festgehalten hat. Das ist der interessantere Ausgang, denn es zeigt
die Sorte Test, die die Fassade eigentlich ueberfluessig machen soll.

Vollstaendige Liste der Roten in diesem Lauf: 34 Golden-Faelle (17 je
Golden-Funktion), 2 × `test_advisor_goals.py`, 2 ×
`test_arsenal_tab_asks_the_facade.py`, 2 × `test_arsenal_tab_wiring.py`,
1 × `test_damage_facade.py`.

**Und ein Befund dazu:** `tests/test_move_scoped_effects.py` wurde in
`99ed022` mitgeaendert, war aber in seiner **alten** Fassung gegen das neue
Programm gruen (5 passed; auch der einzeln nachgefahrene Fall
`test_the_tab_and_the_panel_name_one_figure_for_the_measured_case` ist gruen).
Diese Aenderung war also nicht durch einen roten Test erzwungen, sondern eine
Konsistenzaenderung — richtig in der Sache (sie nimmt eine zweite Kopie der
Anzeigeregel aus dem Test), aber sie ist **keine Regressionssicherung**: der
alte `f"{unbuffed:.0f}"`-Vergleich wuerde heute nicht brechen (L-007).

## 10. Befunde an den Director

**D-1 — `dump_rate.py` fehlt im Repo (L-001).** Der Commit `46edbb9` und der
Kommentar in `nrplanner/weapons.py` (neben `result.scaled`) belegen die
Klammerung mit „350 160 Zahlen je Schadensart … `dump_rate.py`, 04.09.2026"
und „574 von 350 160 bei 2 ULP". Das Skript existiert nicht: `find` ueber den
Baum, `grep -rn "dump_rate"` ueber `*.py/*.md/*.json` und
`git log --all -- "*dump_rate*"` liefern **null** Treffer. Die Zahl im
Quelltextkommentar ist damit nicht nachfahrbar. Aufwand fuer eine Behebung
(Skript nachreichen oder die Zahl mit ihrer Herleitung ersetzen): klein,
Risiko: keins. Ich habe es nicht selbst behoben — ausserhalb des Auftrags.

**D-2 — der ueberholte Vorbehalt steht noch an sechs Stellen** in
`UI_SPEC.md` (fuenf, in **zwei** Wortlauten) und `ARCHITECTURE.md` (eine).
Details in Abschnitt 7. `ARCHITECTURE.md` war keinem Auftrag zugewiesen.
Zusaetzlich: UI_SPEC AK-37 und AK-50 binden zwei Zeichenketten, die im Code
nicht mehr vorkommen — Spezifikation und Programm sind an dieser Stelle
auseinander.

**D-3 — die per-Typ-Aussage der Klammerung ist durch diesen Lauf nicht
belegt.** Der Kommentar in `weapons.py` sagt „jede Zahl je Schadensart ist
exakt `fl(alt × 0,6)`, keine von 350 160 weiter als 1 ULP". Die Messstrecke
nimmt nur die **Summen** auf; sie kann das weder bestaetigen noch
widerlegen. Belegt ist durch meinen Lauf: die Summen liegen zu 99,12 %
(97 745 von 98 615 bewegten Zahlen) innerhalb 1 ULP und zu 100 % innerhalb
4 Einheiten der 16. Dezimale. Wer die per-Typ-Aussage braucht, braucht
D-1 (das Skript) — beides haengt zusammen.

**D-4 — Anzeigeschwellen bewegen sich mit dem Faktor.** 156 Faelle des
Rasters, in denen eine Zeile oder eine farbige Aenderungszelle verschwindet
(Abschnitt 4.2). Fachlich richtig, aber eine sichtbare Aenderung, die im
Auftrag nicht vorhergesagt war. Falls der App Designer die Schwelle als
„halbe Einheit der Anzeige" versteht, muesste sie mit dem Faktor
mitwandern (0,5/0,6 ≈ 0,83) — das waere eine Produktentscheidung, keine
Entwicklerentscheidung, und ich habe nichts geaendert.

**Keine Sicherheitsfunde.** Keine neue Abhaengigkeit. Keine Secrets. Der
Vergleichslauf hat nur gelesen; das Spiel wird von `-m slow` gelesen und
nicht geschrieben.

**Performance:** nichts Auffaelliges gefunden, das an den
`performance-tuner` gehen muesste. `plan.py` braucht 1 min 36 s fuer das
grosse Raster (Effektaufloesung), die Aufnahmen je rund 9 min — beides fuer
ein Entwicklerwerkzeug, das nie in einer Abnahme laeuft, unauffaellig.

## 11. Definition of Done

- [x] Anforderung verstanden, Annahmen im Kontraktblock dokumentiert.
- [x] Build & Tests gruen in der benannten Testumgebung (Windows 10,
      `.venv\Scripts\python.exe -m pytest -q`):
      **`-m "not slow"`: 438 passed, 5 deselected** (Ausgangsstand 426 + 12
      neue Faelle) — **`-m "slow"`: 5 passed, 438 deselected**, gegen die
      installierte Spielinstallation gefahren, wie T-050 verlangt.
- [x] Neue Logik hat Tests; jeder neue Waechter hat seinen gefahrenen
      Gegenbau (Abschnitt 8).
- [x] Kein Linter im Projekt konfiguriert (weder in `requirements-dev.txt`
      noch in `.github/workflows`); geprueft wurde stattdessen die
      Hauskonvention: 79 Spalten, keine Leerzeichen am Zeilenende, LF wie in
      den uebrigen Skripten des Pakets.
- [x] Keine Secrets, keine TODOs, kein toter Code.
- [x] QA-Abnahmekriterien aus T-045 selbst durchgespielt: (1) gruen und beide
      Mutationen rot — Abschnitt 5; (2) Verhaeltnis ueber die Strecke —
      Abschnitte 3 und 4; (4) AD-021-Waechter gruen — Abschnitt 5.
- [ ] **Abnahmepunkt (3) aus T-045 nicht durchgespielt:** „Kachel, Tafel und
      Arsenal-Tab zeigen fuer Wylder Lv12 / Dagger die 74 des Spiels." Der
      Vergleichslauf faehrt Wylder auf **Level 15**, weil die Raster darauf
      stehen, und ich habe die Raster nicht angefasst. Der Fall gehoert in
      den QA-Retest.
- [x] Bericht geschrieben; Dokumentation: `ratios.py` traegt seine
      Herleitung im Modulkopf, das Paket-Docstring habe ich **nicht**
      geaendert (fremde Reihenfolge-Aussage „vier Schritte, vier Skripte" —
      siehe offene Frage OF-2).

## 12. Offene Fragen

**OF-1 (an den `director`):** Bleibt `scripts/differential/ratios.py` im
Repo? Ich halte es fuer noetig (L-001, Abschnitt 8), es ist aber eine
Erweiterung des Auftragsumfangs. Wenn nein: `6b7a0d2` zuruecknehmen — das
ist eine Git-Operation, die mir nicht zusteht.

**OF-2 (an den `director`):** Das Paket-Docstring von
`scripts/differential/__init__.py` sagt „Four steps, four scripts". Mit
`ratios.py` sind es fuenf. Ich habe die Datei nicht angefasst, weil sie die
Strecke als Ganzes beschreibt und der Satz sonst in zwei Commits
auseinanderfaellt. Soll ich ihn nachziehen, oder gehoert das zu OF-1?

**OF-3 (an den `ui-ux-designer`, ueber den `director`):** Abschnitt 4.2 —
die Anzeigeschwellen `>= 0.5` und `> 0.05` sind absolute Grenzen auf einer
Zahl, die jetzt um 0,6 kleiner ist. Bleiben sie, wo sie sind?

**OF-4 (an den `qa-engineer`):** Die 870 Werte aus Abschnitt 4.1 sind mit
2 bzw. 3 ULP dokumentiert. Ist „1 ULP je Wert" fuer **summierte** Groessen
als Abnahmekriterium gemeint, oder gilt es fuer die Zahl je Schadensart? Das
entscheidet, ob Abschnitt 4.1 ein bestandener oder ein offener Punkt ist.

## 13. An den `qa-engineer`

Zu pruefen, mit den Randfaellen, die ich gesehen habe:

1. **Abnahmepunkt 3 aus T-045 fehlt** (siehe DoD): Wylder Lv12, Dagger, die
   74 des Spiels auf Kachel, Tafel und Arsenal-Tab. Mein Lauf steht auf
   Lv15.
2. **Die verschwundene Zeile.** Auf Waffen mit schwachem Attributbeitrag
   zeigt die Klicktafel jetzt keine `From attributes`-Zeile mehr (89 von
   25 102 Faellen). Beispielfall aus meinem Lauf: „multiplier and attributes
   at once, tier 3, alone and active :: armament 1000000" (Dagger).
3. **Die Aenderungszelle, die `—` wird** (66 Faelle), z. B. armament 1000500
   und 1000600, Zeile „Fire"/„Lightning". Und der eine Farbwechsel:
   armament 5050900.
4. **Katalysatoren.** Der Faktor ist auf sie angewandt, obwohl die Messung
   sie ausdruecklich ausnimmt. Die Zahl fuer einen Stab ist jetzt 0,6 × einer
   Zahl, die ohnehin die falsche Groesse misst; nach `docs/state.md` ist die
   richtige Formel inzwischen bekannt (QA-099 geloest, Einbau ist T-046).
   Bis dahin sagt es der Nutzertext (README Z. 553–557, `unknowns` Zeile 2)
   — ob das reicht, ist eine QA-Frage, und meine Messung sagt dazu nur, dass
   die Katalysator-Zahlen im Lauf mit demselben Faktor gewandert sind wie
   alle anderen, also nicht gesondert behandelt werden.
5. **Nachfahrbarkeit meiner Zahlen:** jede Zahl dieses Berichts entsteht aus
   `plan.py` → `capture.py` → `compare.py`/`ratios.py` mit den Aufrufen aus
   Abschnitt 1. Die Zwischendateien liegen nicht im Repo (25 MB je
   Aufnahme); der Lauf dauert rund 20 Minuten.

## 14. An den `ui-ux-designer`

Keine Abweichung von einer UI-Vorgabe. Zwei Beobachtungen: die
Anzeigeschwellen aus OF-3, und dass UI_SPEC an fuenf Stellen einen
Vorbehalt festschreibt, den weder README noch `unknowns` noch der Code noch
tragen (Abschnitt 7). Welcher der beiden Wortlaute ausgeliefert wird, ist in
UI_SPEC Z. 1219–1225 ausdruecklich als offene Frage an dich vermerkt — sie
ist jetzt vermutlich gegenstandslos, weil beide Wortlaute falsch geworden
sind.
