# T-046 — Katalysatoren nach der Kennzahl des Spiels reihen (developer)

```
STATUS: erledigt
AUFTRAG: T-046 — Katalysatoren nach der Kennzahl des Spiels reihen: `unknown_1`
         extrahieren, Zauber-/Anrufungsskalierung an einer Stelle bilden
         (docs/tasks/T-046.md)
GELESEN: docs/tasks/T-046.md; docs/berichte/T-043-qa-engineer.md;
         docs/berichte/T-045-developer.md; qa/findings.md (QA-099, QA-099a/b/c);
         ARCHITECTURE.md AD-019, AD-020, AD-021, AD-022, AD-024;
         nrdata/extract.py, nrdata/param.py; nrplanner/weapons.py,
         damage.py, model.py, arsenaltab.py, weaponslots.py, app.py,
         advisor/goals.py, datasource.py; scripts/differential/__init__.py,
         capture.py, compare.py, ratios.py, mutate.py, rasters/*.json;
         scripts/capture_weapon_damage.py; tests/conftest.py,
         weapon_damage_cases.py, test_one_build.py, test_damage_facade.py,
         test_attack_power_against_the_game.py,
         test_arsenal_tab_asks_the_facade.py, test_advisor_goals.py,
         test_weapon_damage_golden.py, test_move_scoped_effects.py,
         test_extraction.py, test_hostile_gamedata.py; README.md;
         UI_SPEC.md (§3.3, AK-34); installierte regulation.bin
         (data_version 10350000); `C:\Users\Daniel\Desktop\Nightreign Weapon
         Scaling.xlsx`, Blatt "Weapon Attack Power", Zeilen 294-321; GOAL.md;
         docs/state.md. Nicht auffindbar und deshalb nicht gelesen:
         `rps_nightreign_weapons.tsv`, die Quelle der 28 Referenzzahlen
         (Abschnitt 5).
GEÄNDERT: nrdata/extract.py; nrplanner/weapons.py, damage.py, arsenaltab.py,
         weaponslots.py, app.py, advisor/goals.py; README.md;
         scripts/differential/__init__.py, scripts/differential/mutate.py;
         tests/conftest.py, tests/data/game_catalyst_scaling.json (neu),
         tests/test_catalyst_scaling_against_the_game.py (neu),
         tests/test_catalyst_scaling_extraction.py (neu),
         tests/test_arsenal_tab_asks_the_facade.py, tests/test_damage_facade.py,
         tests/test_advisor_goals.py, tests/test_move_scoped_effects.py,
         tests/weapon_damage_cases.py,
         tests/golden/weapon_damage.json (neu aufgezeichnet);
         docs/berichte/T-046-developer.md (diese Datei);
         .claude/agent-memory/developer/ (MEMORY.md,
         project_test_data_verification.md,
         reference_game_display_measurements.md — nur Agent-Gedaechtnis,
         nicht committet, per .gitignore ausgeschlossen).
         Ausserhalb des Repos: der Schnappschuss
         `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json` wurde neu
         gebaut (EXTRACT_VERSION 8 -> 9). Acht Code- und Werkzeug-Commits
         auf `docs/audit-and-advisor-design`, 2a6bb3e bis 8bd70a9, dazu
         190f5bd und dieser Nachtrag fuer den Bericht selbst.
         NICHT angefasst: UI_SPEC.md, docs/state.md, qa/findings.md — die
         drei sind im Baum geaendert und gehoeren anderen Rollen.
ANNAHMEN: (1) Beschriftung einheitlich "Spell power" fuer Staebe und Siegel —
         der Auftrag nennt das als Vorgabe, solange der `ui-ux-designer` nicht
         gezogen wird. (2) Die Multiplikatorschicht erreicht die Kennzahl
         nicht (Begruendung unten, Abschnitt 3) — das ist eine Entscheidung,
         die der Auftrag nicht getroffen hat. (3) Die RPS-Zahlen sind aus
         T-043 Abschnitt 3 abgeschrieben, nicht aus der Quelle selbst
         gelesen; die Quelldatei liegt nicht im Repo (Abschnitt 5).
NÄCHSTER: qa-engineer (Retest nach der Abnahmeliste in T-046), danach director
BLOCKIERT DURCH: nichts
```

---

## 1. Umgesetzt

**Die Zahl, die das Spiel fuer einen Stab oder ein Siegel zeigt, ist jetzt die
Zahl, die das Programm zeigt und nach der es reiht.** Die physische AR eines
Katalysators erscheint an keiner Anzeigestelle mehr — nicht auf der Kachel,
nicht in der Tafel, nicht im Aufklapp-Text, nicht im Arsenal-Tab, nicht in der
Beraterzeile und in keiner Rangliste.

| Ort | Was |
|---|---|
| `nrdata/extract.py` | `CATALYST_SCALING_FIELD`, `CATALYST_SCALING_ROWS_TODAY`, `catalyst_scaling_rates()`, `reinforce[].catalyst_scaling`, `EXTRACT_VERSION` 8 -> 9 |
| `nrplanner/weapons.py` | `CATALYST_DISPLAY_RATE = 90.0`, `CATALYST_ATTRIBUTES`, `CATALYST_SCALING_KEY`, `_catalyst_scaling()`, `WeaponRating.catalyst_scaling`, `WeaponRating.scaled_headline()`, `rank()` reiht darauf |
| `nrplanner/damage.py` | `ATTACK_RATING_LABEL/NAME`, `SPELL_POWER_LABEL`, `Rating.catalyst_scaling / scaled_headline / final_headline / headline_label / headline_name / shown_per_type`, `breakdown_figures()` liefert die Headline-Werte plus `headline`, `rank_candidates()` reiht auf `final_headline` |
| `nrplanner/arsenaltab.py` | Kachel-Kopfzeile mit `headline_label`/`final_headline`, Typzeilen aus `shown_per_type` |
| `nrplanner/weaponslots.py` | Slot-Kachel mit `headline_label`/`final_headline`; `WeaponDialog._list_label()` zeigt bei Namensgleichheit die Id |
| `nrplanner/app.py` | Tafel: Zeilen aus `shown_per_type`, Summenzeile aus `scaled_headline`/`final_headline` und mit dem Namen der Groesse; Aufklapp-Text mit `ar["headline"]` in der Ueberschrift |
| `nrplanner/advisor/goals.py` | `max_damage` bewertet und beschriftet ueber die Fassade; der Katalysator-Vorbehalt ist raus, an seiner Stelle steht der Geltungsbereich |
| `README.md` | "Known limits": derselbe Austausch |
| `scripts/differential/` | vier neue Mutationen, vier Anker nachgezogen, Paket-Docstring auf fuenf Skripte |
| `tests/` | zwei neue Testdateien, eine neue Datendatei, Golden neu aufgezeichnet, fuenf bestehende Dateien nachgezogen (`test_damage_facade`, `test_arsenal_tab_asks_the_facade`, `test_move_scoped_effects`, `test_advisor_goals`, `weapon_damage_cases`), `conftest` prueft die Extraktorfassung des Schnappschusses |

Acht Code- und Werkzeug-Commits, `2a6bb3e` bis `8bd70a9`, plus den Bericht
selbst — alle auf dem ausgecheckten Branch
`docs/audit-and-advisor-design`. Kein push/pull/fetch/merge/rebase/checkout/
branch/reset/revert/stash.

### Die Formel und wo sie steht

```
Anzeige = floor( 90 x reinforce.catalyst_scaling x (1 + Kurve(A)/100) )
```

`_catalyst_scaling()` in `nrplanner/weapons.py` ist die **einzige** Stelle, an
der die Zahl entsteht; `rate()` bildet sie einmal mit und legt sie in
`WeaponRating.catalyst_scaling` ab, die Fassade reicht sie weiter. `floor`
steht ausschliesslich in `damage.displayed` (QA-074). Die Funktion ist
modulprivat: sie ist damit kein zweiter oeffentlicher Einstieg in die
Arithmetik, `ARITHMETIC_ENTRY` in `test_one_build.py` bleibt unveraendert
`{"rate", "rank"}`, und der AD-021-Waechter ist gruen, ohne dass an ihm etwas
geaendert werden musste.

Die Kurve kommt aus `weapon["curve"]["Physics"]` — der Waffe selbst — und
nicht als 16 im Code. Das Attribut kommt aus `weapon["scaling"]`: Intelligence,
wenn die Waffe darauf skaliert, sonst Faith. Katalysator ist, wofuer
`model.weapon_class(weapon) == "catalyst"` gilt; das benutzt die vorhandene
Familienzuordnung (`Glintstone Staff`, `Sacred Seal`) statt neuer wepType-
Konstanten. Gegenprobe an den Daten: Familienzuordnung und `wep_type` 57/61
sind ueber alle 1793 Waffen deckungsgleich (30 zu 30).

## 2. Die Zahlen, die die Konstante tragen (L-001)

`CATALYST_DISPLAY_RATE = 90.0`. Rezept, im Code neben der Konstante und hier:
Intervallschnitt ueber die 84 `floor`-Bedingungen der gemessenen Zellen,
`K in [89.9982, 90.0147]`; Sicherheitsabstand 0.0018 (0.002 %) nach unten,
0.0147 (0.016 %) nach oben; 90 ist die einzige Zahl mit hoechstens zwei
signifikanten Stellen darin. Erhoben in T-043, hier nicht neu gefittet,
sondern gegen die 84 Zellen nachgeprueft (Abschnitt 5).

`CATALYST_SCALING_ROWS_TODAY = 97` ist **kein** Schwellwert, sondern der
Messwert: 97 von 255 Reinforce-Zeilen tragen einen Wert ungleich 1,0, verteilt
auf 30 Gruppen. Nachgemessen am neu gebauten Schnappschuss: 97. Die Schranke
der Pruefung ist **eins**, mit Begruendung im Code — eine Spielfassung ohne
Katalysatoren ist eine Spielaenderung und kein kaputter Extraktor, und ein
Waechter, der darauf faellt, wird abgeschaltet.

## 3. Entscheidungen, die der Auftrag nicht getroffen hat

**Die Multiplikatorschicht erreicht die Kennzahl nicht.** Die 90 wurde gegen
die Anzeige **ohne Relikte** gefittet. Was "Improved Physical Attack Power"
mit einer Skalierungszahl macht, ist nirgends gemessen, und die Zahl ist keine
Schadenszahl, auf die ein Angriffsratenfeld passt. Sie mit `physicsAttackRate`
zu multiplizieren waere eine erfundene Beziehung — genau das, was A7 verbietet.
Was die Zahl bewegt, ist ein Attribut, und das ueber die Kurve wie im Spiel:
ein Relikt, das Intelligenz hebt, hebt die Zahl eines Stabes. Praktische
Folge: die Vorher/Nachher-Zeile der Tafel funktioniert fuer einen Katalysator,
die Prozentzeile der Multiplikatoren bleibt bei ihm leer. Ich halte das fuer
richtig; es ist aber eine Produktentscheidung, und der `director` kann sie
umdrehen — dann braucht es vorher eine Messung im Spiel, sonst ist die Zahl
nicht mehr die Zahl des Spiels.

**Beschriftung.** Einheitlich `"Spell power"` fuer Staebe und Siegel, wie der
Auftrag es fuer den Fall vorgibt, dass der `ui-ux-designer` nicht gezogen wird.
Zwei Formen im Code, weil beide schon gebraucht wurden: kurz (`"AR"` /
`"Spell power"`) fuer Kachelzeilen, lang (`"Attack rating"` / `"Spell power"`)
fuer Saetze. Fuer Nicht-Katalysatoren ist an keinem Text etwas geaendert.

**`breakdown_figures` traegt einen Schluessel mehr** (`headline`). Ohne ihn
haette der Aufklapp-Text fuer einen Stab die richtigen Zahlen unter der
falschen Ueberschrift gezeigt ("Attack rating — Carian Regal Scepter"). Der
Preis ist eine Neuaufzeichnung der Golden-Datei; der Beleg, dass dabei kein
Wert gewandert ist, steht in Abschnitt 6.

## 4. Tests

### Neu

* **`tests/data/game_catalyst_scaling.json`** — 84 Zellen (28 Katalysatoren x
  3 Nightfarer, der ganze zusammenhaengende Block der Tabelle, nichts
  ausgewaehlt) und 28 Zahlen der zweiten Liste, mit Kopf: Quelle, Blatt,
  Zeilenbereich, Tag, Spielfassung, was weggelassen wurde und warum, wie die
  Zeilen gewaehlt wurden, die Trefferquote ueber alles, und die
  Namenskollisionen mit der Begruendung der Id-Wahl.
* **`tests/test_catalyst_scaling_against_the_game.py`** — 84 + 28
  parametrisierte Faelle ueber die Fassade (`damage.candidate`), je mit vier
  Vorbedingungen: Name passt zur Id, Tier ist die eigene Raritaet, keine
  Multiplikatoren im Spiel, und die Zahl kam aus dem Katalysator-Zweig (sonst
  koennte ein Fall gruen sein, weil AR und Kennzahl zufaellig auf dieselbe
  ganze Zahl fallen). Dazu: die Reihung Scepter vor Rotten Crystal Staff mit
  beiden Spielzahlen; der Datensatz-Sweep "genau 30 Katalysatoren tragen eine
  Kennzahl, die anderen 1763 keine, und keiner der 30 zeigt eine Typzeile";
  der Herkunftstest ueber den Kopf der Datendatei; der Konstantentest.
* **`tests/test_catalyst_scaling_extraction.py`** — vier Faelle gegen
  Stubtabellen: gutgeformte Tabelle liefert jede Rate, fehlendes Feld wird
  laut abgelehnt (mit dem Feldnamen und dem Ort der Konstante in der Meldung),
  durchgehend 1,0 wird abgelehnt, eine bewegte Zeile genuegt.

### Geaendert

* `test_damage_facade.py`: die beiden Reihungsfaelle stehen auf
  `final_headline` statt `final_total` — auf `final_total` festgenagelt waeren
  sie fuer die 30 Katalysatoren rot, waehrend die Funktion ihr Versprechen
  haelt (dieselbe Form wie die QA-065-Messung, die im Docstring daneben steht).
* `test_arsenal_tab_asks_the_facade.py`: `tile_ar` -> `tile_headline`, das die
  Beschriftung **aus der Antwort der Fassade** nimmt statt unter beiden zu
  suchen — sonst wuerde der Helfer genau die Verwechslung verdecken, gegen die
  er steht.
* `test_move_scoped_effects.py`: zieht denselben Helfer nach.
* `tests/weapon_damage_cases.py`: nur die Docstring-Zeile von
  `arsenal_figure`, die faelschlich "die Zahl, die die Kachel druckt" sagte.
  Der Leser selbst bleibt bei `final_total` — er beantwortet "hat sich die
  Arithmetik bewegt", `arsenal_tiles` daneben "hat sich der Text bewegt"
  (Abschnitt 6).
* `test_advisor_goals.py`: prueft jetzt den **Ersatz** des Vorbehalts, nicht
  seine Abwesenheit — die Zeile muss den Geltungsbereich nennen ("own rarity",
  "spell hits for"), und die alte Formulierung darf nicht zurueckkommen.
* `tests/conftest.py`: ein Schnappschuss aus einer aelteren Extraktorfassung
  wird nicht mehr benutzt (per Umgebungsvariable benannt: lauter Fehlschlag;
  aus dem Cache: uebergangen, die Live-Extraktion darunter greift). Ohne das
  laeuft der naechste Rechner in einen KeyError tief in einer Bewertung, und
  der liest sich wie eine Regression. **Das ist eine Aenderung an fremder
  Testinfrastruktur, die ich gebraucht habe, damit meine eigene Aenderung auf
  einem anderen Rechner ueberhaupt pruefbar ist** — gemeldet, nicht
  stillschweigend.

### Laeufe

| Lauf | Vorher (3602055) | Nachher (8bd70a9) |
|---|---|---|
| `.venv\Scripts\python.exe -m pytest -q -m "not slow"` | 438 passed, 5 deselected | **563 passed, 5 deselected** |
| `... -m "slow"` | 5 passed | **5 passed** |

Beide Zahlen selbst gefahren, beide "nachher"-Laeufe auf dem Endstand
`8bd70a9` wiederholt.

### Toetende Mutationen — alle gefahren, jede mit ihrer Zahl (L-002, L-003)

Jede auf einem eigenen `git archive HEAD | tar -x`-Baum, `mutate.py --apply`,
dann die Zieldatei mit pytest. Die neue Datei hat 117 Faelle.

| Mutation | Ort | Ergebnis |
|---|---|---|
| `catalyst-scaling-rate-ignored` | `weapons.py:226`, Rate -> 1.0 | **105 von 117 rot** (78 von 84 Zellen, 26 von 28 Referenzzahlen, dazu der Reihungsfall) |
| `catalyst-curve-hardcoded-to-zero` | `weapons.py:236`, eigene Kurve -> Kurve 0 | **113 rot** (84/84, 28/28, Reihung) |
| `catalyst-influence-inside-the-bracket` | `weapons.py:247`, Einfluss 0,9 in die Klammer | **91 rot** (84/84, 6/28, Reihung) |
| `attack-power-rounded-instead-of-truncated` | `damage.py:133`, `floor` -> `round` | **55 rot** (39 von 84, 16 von 28) |
| `catalyst-scaling-field-renamed` | `extract.py:105`, Feldname -> ein anderer | **3 von 4 rot** in `test_catalyst_scaling_extraction.py` |

Zur vierten Zeile: die Rundungsmutation ist **nicht** doppelt registriert. Es
gibt eine Anzeigeregel an einer Stelle, und ein zweiter Eintrag mit demselben
Anker waere ein zweiter Name fuer eine Bearbeitung. Der Eintrag von T-045
nennt jetzt beide Zahlenwerke.

Zwei Funde aus dem Mutationslauf, die ich sonst nicht bemerkt haette und die
je einen eigenen Commit bekommen haben:

1. Der Stub in `test_catalyst_scaling_extraction.py` baute seine Zeilen aus
   `extract.CATALYST_SCALING_FIELD` und stimmte damit immer mit dem ueberein,
   wonach der Extraktor gerade sucht. Unter der Umbenennungs-Mutation blieb
   der positive Fall gruen, und rot wurde der Ablehnungsfall — der Waechter
   haette also nicht gemerkt, dass ein Feld gelesen wird, das die Spieldaten
   nicht haben. Jetzt steht der Paramdex-Name als Literal in der Testdatei
   (`ac1410a`).
2. Die Mutation setzte denselben Ersatznamen ein, den der Ablehnungsfall als
   "falschen" Namen benutzt; damit fiel dieser Fall aus einem Grund, der mit
   der Mutation nichts zu tun hat (`af50202`). Und die Beschreibung "die
   Ablehnungsfaelle bleiben gruen" war schlicht falsch: gemessen fallen drei
   von vier (`c5efb80`).

Ausserdem gruen geblieben, ohne Zutun: `tests/test_differential_track.py`
prueft jeden Mutationsanker gegen die echte Quelle. Vier Anker mussten wegen
meiner Aenderungen nachgezogen werden (`arsenal-tile-figure-halved`,
`arsenal-tile-type-row-duplicated`, `ranking-left-in-layer-one-order`,
`ranking-without-the-tie-break`); dass sie jetzt wieder passen, ist von diesem
Test belegt und nicht von mir behauptet.

## 5. Die Datenlage — was Messung ist und was Abschrift (L-001)

**Die 84 Zellen sind fuer diese Datei neu aus der Tabelle gelesen**, nicht aus
T-043 abgeschrieben: `C:\Users\Daniel\Desktop\Nightreign Weapon Scaling.xlsx`,
Blatt "Weapon Attack Power", Zeilen 294-321, Spalten Duchess (4), Revenant (6),
Recluse (7). Gelesen mit einem Wegwerf-Parser aus `zipfile` +
`xml.etree.ElementTree` im Scratchpad — **keine neue Abhaengigkeit**, das venv
hat kein openpyxl und ich habe keins eingebaut. Die drei Beispiele, die T-043
ausschreibt, stimmen ueberein (Carian Regal Scepter 218/198/237, Recluse's
Staff 118/107/128, Frenzied Flame Seal 172/212/212).

Die Zuordnung Tabellenzeile -> Waffen-Id habe ich selbst gelegt und nicht aus
`assignment.json` uebernommen (das ist die Datei, die in T-038 die falsche
Zeile gewaehlt hat, QA-099b). Sie steht in der Datendatei bei jeder Zeile als
`weapon` + `name`, und der Test prueft bei jedem Fall, dass der Name im
Datensatz noch derselbe ist.

Die Attribute stehen **nicht** in der Datei: der Test rechnet sie mit
`model.compute` fuer Level 12, und das liefert Duchess INT 36 / FAI 24,
Revenant INT 27 / FAI 45, Recluse INT 45 / FAI 45 — genau die Werte, die
T-046 vorgibt und T-043 gemessen hat.

**Die 28 RPS-Zahlen sind eine Abschrift einer Abschrift.** Die Quelldatei
(`rps_nightreign_weapons.tsv`) liegt nicht im Repo und war auf diesem Rechner
nicht mehr auffindbar; ich habe die Spalte aus der Tabelle in T-043 Abschnitt 3
uebernommen. Das steht so im Kopf der Datendatei (`reference_list.source`) und
ist hier wiederholt, weil es der einzige Punkt der ganzen Beweiskette ist, den
ich nicht auf eine Primaerquelle zuruckfuehren kann.

## 6. Abnahme (6): die Messstrecke — kein Nicht-Katalysator-Wert hat sich bewegt

Zwei Baeume, beide Raster, `PYTHONHASHSEED=0` vor dem Interpreterstart, alter
Baum aus `git archive 3602055 | tar -x` (nicht aus einem Klon).

### Raster `tiles_and_panel`, 25 102 Faelle

`compare.py`: 23 339 Datensaetze unterscheiden sich. Aufgeschluesselt mit
einem eigenen Skript, das jeden Datensatz danach sortiert, ob er einen
Katalysator beruehrt und ob der ganze Unterschied der neue Schluessel ist:

```
records          25102
identical        1763
nur der neue Schluessel `headline`, Werte unveraendert:  22919
Katalysator-Datensaetze mit echter Aenderung:              420
NICHT-Katalysator-Datensaetze mit echter Aenderung:          0
Felder hinter den echten Aenderungen: panel 300, last_ar 300,
                                      tiles 420, breakdown 300
```

`ratios.py --factor 1.0` (der Faktor 1,0 heisst: "old muss bitgleich new
sein") ueber dieselben zwei Aufnahmen:

```
figures 85358: 84458 scaled by the factor within 1 ULP, 0 unmoved
texts identical 397026
furthest figure 0 ULP
unplaced 25229  = 23309 x der neue Schluessel `headline`
                + 1920 Katalysator-Werte (3x300 last_ar, 300 breakdown,
                  300 panel, 420 Kacheltexte)
```

**"furthest figure 0 ULP"** ist die eigentliche Aussage: von den 84 458
zugeordneten Zahlen ist keine einzige auch nur um ein letztes Bit gewandert.

Die 1 763 voellig identischen Datensaetze habe ich nachgezaehlt statt
erklaert: sie liegen **alle** in der einen Konfiguration "three tiles and an
empty slot active, so none of them is" — dort ist `last_ar == {}`, es gibt
also auch keinen neuen Schluessel — und **keiner** von ihnen beruehrt einen
Katalysator. 1 793 Waffen minus die 30 Katalysatoren, deren Kacheltexte auch
in dieser Konfiguration wandern, sind genau 1 763.

### Raster `arsenal_tab`, 7 172 Faelle

`compare.py`: alle 7 172 Datensaetze unterscheiden sich — der neue
Schluessel `headline` steht in jedem, weil dieses Raster die Slots fest auf
Wylders Startwaffe haelt und nur der Arsenal-Block wandert. Aufgeschluesselt:

```
records          7172
identical           0
nur der neue Schluessel `headline`, Werte unveraendert:  7053
Katalysator-Datensaetze mit echter Aenderung:             119
NICHT-Katalysator-Datensaetze mit echter Aenderung:         0
Feld hinter den echten Aenderungen: arsenal_tiles 119
```

119 und nicht 120 (30 Katalysatoren x 4 Konfigurationen): nachgezaehlt, der
eine fehlende ist **Carian Regal Scepter in der Konfiguration "Rare only"**.
Er ist Legendary, das Raritaetsfilter zeichnet fuer ihn keine Kachel, und ohne
Kachel gibt es keinen Text, der sich aendern koennte.

`ratios.py --factor 1.0`:

```
figures 30481: 30481 scaled by the factor within 1 ULP, 0 unmoved
texts identical 223770
furthest figure 0 ULP
unplaced 7307 = 7172 x der neue Schluessel `headline`
              +  135 Kacheltext-Werte
  .arsenal_figure scaled: 7172      <- alle, bitgleich
  .arsenal_tier   still:  7172
  .arsenal_listed still:  7172
  .arsenal_summary still: 7172
```

**`arsenal_figure` ist bei allen 7 172 bitgleich, auch bei den
Katalysatoren** — und das ist kein Widerspruch, sondern die Trennung, auf der
die Aufnahme beruht: das Feld liest `final_total`, also die Arithmetik der
zweiten Schicht, und die habe ich nicht angefasst. Was sich bei einem
Katalysator geaendert hat, ist **welche** Zahl die Kachel zeigt, und das ist
eine Textaenderung; sie steht in `arsenal_tiles`. Die Docstring-Zeile, die
`arsenal_figure` faelschlich "die Zahl, die die Kachel druckt" nannte, ist
nachgezogen (`8bd70a9`).

### Zusammen

Ueber beide Raster, 32 274 Faelle und **115 839 Zahlen** (85 358 + 30 481 —
dieselbe Gesamtzahl, die T-045 fuer die 0,6-Kalibrierung gemessen hat):
**0 Datensaetze ohne Katalysator haben einen Wert geaendert**, und keine
einzige der 114 939 zugeordneten Zahlen ist weiter als **0 ULP** gewandert.
Die 900 nicht zugeordneten sind die `last_ar`-Zahlen der Katalysatoren
(3 x 300). Was sich geaendert hat, ist genau zweierlei:

* der neue Schluessel `headline` in `last_ar` — 23 309 + 7 172 = 30 481
  Vorkommen, ueberall mit unveraenderten Werten daneben;
* 2 055 Werte an Katalysatoren — 1 920 im Raster `tiles_and_panel`
  (3 x 300 Zahlen in `last_ar`, 300 Tafeltexte, 300 Aufklapp-Texte,
  420 Kacheltexte) und 135 Kacheltexte im Raster `arsenal_tab`.

Beide Aufnahmepaare liegen im Scratchpad dieser Session; die Befehle stehen
in `scripts/differential/__init__.py` unter "Running it".

## 7. QA-099a — die Namenskollision: Kriterien, die der Datensatz hergibt

Gebaut habe ich nur, was der Auftrag freigibt: **bei Namensgleichheit die Id
sichtbar machen**, und zwar dort, wo ausgewaehlt wird (`WeaponDialog`). Kein
Filter. Die Kriterien fuer die Entscheidung des `director`:

Genau **drei** von 1 788 Namen im Datensatz gehoeren zu mehr als einer Zeile
(1 793 Waffen):

| Name | Ids | Felder verschieden (von 268) |
|---|---|---|
| `Recluse's Staff` | 33750000, 33770000 | 40 |
| `Finger Seal` | 34000000, 34750000 | 30 |
| `Scholar's Thrusting Sword` | 5750000, 5760000, 5770000, 5780000 | 3 |

*(T-043 nennt fuer `Recluse's Staff` 42 Felder, ich zaehle 40. Der
Unterschied ist folgenlos fuer die Sache, aber er ist da; wer die Zahl
weiterverwendet, sollte sie selbst nachzaehlen.)*

**Drei Kriterien, die auf dieselbe eine Zeile zeigen** — jedes fuer sich
gemessen ueber die 30 benannten Katalysatoren:

* `equippedSpell_R1/R2 == -1` (kein Zauberplatz): **1 von 30** — 33770000.
* `reinforceTypeId == 0` (die generische Gruppe): **1 von 30** — 33770000.
* `attackElementCorrectId == 10000` (die generische AEC): **1 von 30** —
  33770000.

**Warnung zum ersten Kriterium:** ausserhalb der Katalysator-Familie sagt es
nichts. 1 764 von 1 793 benannten Waffen haben keinen Zauberplatz — das ist
der Normalfall fuer ein Schwert. Als Filter taugt es nur **innerhalb** der
Familie, und dort taugt es scharf.

`Finger Seal`: beide Zeilen tragen Zauberplaetze und sitzen auf derselben
Reinforce-Gruppe 6000, sind also zahlengleich; sie unterscheiden sich in
`equippedSpell_R2` (6000 gegen 6421), `disableParam_NT`, `disableGemAttr`,
`properLuck`. Welche der beiden "die richtige" ist, ist an den Zahlen nicht
entscheidbar und **fuer die Anzeige folgenlos**. Ich habe 34750000 gewaehlt,
weil T-043 sie gewaehlt hat. Nebenbefund gegen die Begruendung in T-043 7.2:
die Endung `750000` bedeutet **nicht** "Startwaffe" — die zehn Startwaffen
enden alle darauf, aber 34750000 ist keine von ihnen (die Recluse startet mit
33750000, kein Nightfarer startet mit einem Finger Seal).

`Scholar's Thrusting Sword`: die vier Zeilen unterscheiden sich nur in
`equipModelId`, `iconId`, `disableGemAttr` — zahlengleich, die Kollision ist
kosmetisch.

## 8. Was ich nicht gebaut habe, aber gefunden — an den `director`

### 8.1 [dringend] Der Arsenal-Tab zeigt zwei `Recluse's Staff` mit 128 und 151, ununterscheidbar

Gemessen, Recluse Lv 12, Spinbox 1, Suche "Staff": der Tab zeichnet zwei
Kacheln mit demselben Namen, `Spell power 128` (33750000, die echte) und
`Spell power 151` (33770000, die Fremdzeile). **Meine Aenderung macht diese
Kollision sichtbarer als vorher**: bis heute standen beide bei ~25 AR und
sahen gleich aus, jetzt stehen 23 Punkte dazwischen, und die falsche steht
oben. Die Id habe ich nur im Auswahldialog sichtbar gemacht, nicht auf der
Kachel — bewusst: die Kachel-Beschriftung ist UI_SPEC-Gebiet, und eine
Aenderung dort kostet eine Neuaufzeichnung des Arsenal-Rasters und bricht die
Testhelfer, die Kacheln ueber den Namen finden. Entscheidung gehoert dem
`director`: entweder die nicht spielbaren Zeilen filtern (Kriterien in
Abschnitt 7) oder die Id auf die Kachel. Ich rate zum Filter — eine Waffe, die
keinen Zauber tragen kann, ist kein Katalysator, den ein Spieler vergleichen
will.

### 8.2 Der Zusammenfassungssatz des Arsenal-Tabs erklaert nur noch die Haelfte

`nrplanner/arsenaltab.py:306` sagt: "Attack rating is base damage, plus what
your stats add to it, plus the +% attack effects your equipped relics grant."
Der Tab zeigt jetzt zwei verschiedene Groessen, und dieser Satz definiert nur
eine. Ich habe ihn **nicht** angefasst: die Zeichenkette ist ausdruecklich
UI_SPEC-geregelt (AK-34, mit verbotenen und verlangten Teilstrings), das ist
das Gebiet des `ui-ux-designer`. Vorschlag zur Weitergabe, falls er gezogen
wird: ein Satz dahinter, etwa *"For staves and seals the game shows a spell
scaling instead of an attack power, so that is what their tiles show."* Kein
Warnhinweis — eine Definition.

### 8.3 Die Golden-Datei friert jetzt zwei ungemessene Katalysator-Zahlen ein

Zwei der 18 Faelle stehen auf Katalysatoren mit **Aufstieg**: Glintstone Staff
auf Tier 3 (236) und Recluse's Staff auf Tier 2 (184). Belegt ist nur die
Basisraritaet; die Stufenlogik uebernimmt `unknown_1` der Aufstiegszeile, was
plausibel und ungeprueft ist. Als Charakterisierung ist das genau richtig
(die Datei friert ein, was das Programm sagt), aber niemand sollte die beiden
Zahlen fuer belegt halten. Wenn eine Fremdquelle fuer aufgewertete
Katalysatoren auftaucht, ist das die naechste Messung.

### 8.4 Reihenfolge quer ueber zwei Groessen

`rank_candidates` reiht Katalysatoren jetzt nach 78..237, alle anderen nach
ihrer AR. Gemessen (Recluse Lv 12, Tier 1): die Rangliste beginnt mit Jar
Cannon 350 und Hand Ballista 258, dann kommen sieben Katalysatoren
(237..200), dann wieder Bogen und Klingen. Katalysatoren steigen also, aber
sie beherrschen die Liste nicht. Das ist die unvermeidliche Folge von "zeig
dem Spieler die Zahl des Spiels", sobald das Spiel zwei verschiedene Zahlen
zeigt — und es ist eine Produktentscheidung, keine Rechenfrage.

### 8.5 Der sichtbare Tab reiht nicht nach der Rangliste

Fuer den QA-Retest wichtig: Abnahmepunkt (2) ist erfuellt, aber nicht durch
die Rangliste. `arsenaltab._build_weapons` verwirft die Reihenfolge von
`rank_candidates` und sortiert jede Familie neu nach Raritaet, dann Name, dann
Id. Carian Regal Scepter (237) steht vor Rotten Crystal Staff (182), weil er
Rare ist und der andere Common. Innerhalb eines Raritaetsbandes steht der Tab
alphabetisch: Albinauric Staff (178) vor Carian Glintblade Staff (185). Wer
Abnahmepunkt (2) an der Rangliste pruefen will, muss `damage.rank_candidates`
fragen — dort liegt der Scepter auf Platz 2 und Rotten Crystal Staff auf 19.

### 8.6 Vorhandene Debt, nicht von mir angefasst

* `nrplanner/damage.py`: `AttackRating` und `attack_rating()` haben nach wie
  vor keinen Produktionsleser (die Klasse sagt das selbst) und liefern fuer
  Katalysatoren weiterhin die physischen Felder `final_per_type`,
  `scaled_total`, `final_total` — nur `figures()` geht ueber die Fassade.
  Wer die Klasse kuenftig doch benutzt, bekommt fuer einen Stab die physische
  AR. Ich habe sie nicht umgestellt, weil sie kein Anzeigepfad ist und jede
  Aenderung an ihr die Golden-Datei bewegt.
* Zwei weitere Testdateien haben je einen eigenen `tile_ar`-Helfer mit der
  fest verdrahteten Beschriftung `"AR"`: `tests/test_arsenal_tab_wiring.py`
  und `tests/test_weapon_tile_and_panel_agree.py`. Beide waehlen ihre Waffen
  ueber Wylders Startwaffe, einen Bogen und ein Kolossalschwert — nie einen
  Katalysator — und **beide wuerden laut scheitern**, nicht still
  durchgehen, falls je einer hineingeriete (`assert AR_ROW in texts` bzw.
  `assert match`). Ich habe sie deshalb nicht umgebaut; wer sie spaeter auf
  eine Waffenauswahl umstellt, die Katalysatoren treffen kann, muss den
  Helfer wie in `test_arsenal_tab_asks_the_facade.py` label-fuehrend machen.
* `tests/data/game_attack_power.json`: der `left_out`-Eintrag "Staves and
  seals: the game shows the spell scaling for them, not an attack rating, so
  the factor does not describe them (QA-099)" ist weiterhin **richtig** (die
  0,6 beschreibt sie nicht) und bleibt stehen. Nur damit niemand ihn beim
  naechsten Durchgang fuer den geloeschten Vorbehalt haelt.

## 9. Volltextsuche nach dem Vorbehalt (L-006)

Drei unabhaengig formulierte Masken ueber den ganzen Baum (ohne `.venv`,
`docs/berichte`, `docs/tasks`, `docs/archiv`, `qa/findings.md`, `.claude`,
`docs/handover-*`):

| Maske | Treffer nachher | Bewertung |
|---|---|---|
| `catalyst` (case-insensitive) | **169** (vorher 16) | Der Anstieg ist die neue Umsetzung selbst: 36 in `weapons.py`, 29 + 16 in den beiden neuen Testdateien, 20 in `extract.py`, 19 in `mutate.py`, 13 in `damage.py`. Kein Treffer behauptet mehr, das Programm zeige fuer einen Stab die physische AR. |
| `stave|staff|\bseal` | **274** (vorher 23) | Dito; die Zunahme steckt in der Datendatei (28 Waffennamen x mehrere Felder) und in den Docstrings. |
| `outside that match|physical attack rating|cannot be compared with the game` | **9** | Alle neun sind **historische** Erklaerungen in Kommentaren, Docstrings und einer Assertion, die die Rueckkehr der alten Zeile verbietet. Keine ist ein Vorbehalt an den Spieler. |

Die zwei Fundstellen, an denen der Vorbehalt als **Nutzertext** stand, und die
er verlassen hat:

* `README.md` (Abschnitt "Known limits", frueher ~Z. 553-556): der ganze
  Aufzaehlungspunkt ist ersetzt.
* `nrplanner/advisor/goals.py` `_ATTACK_RATING_UNKNOWNS[1]` (frueher ~Z. 88-97
  samt Kommentarblock): Zeile und Begruendung sind ersetzt.

Beide sind durch `tests/test_advisor_goals.py::test_the_damage_goal_always_
carries_the_attack_rating_reservation` gegen eine stille Rueckkehr **und**
gegen ein stilles Verschwinden des Ersatzes gesichert.

## 10. Definition of Done

- [x] Anforderung verstanden, Annahmen im Kopfblock und in Abschnitt 3
- [x] Build & Tests gruen in der benannten Umgebung (Windows 10,
      `.venv\Scripts\python.exe`): `-m "not slow"` **563 passed, 5 deselected**;
      `-m "slow"` **5 passed**
- [x] Neue Logik hat neue Tests; jeder neue Waechter hat eine gefahrene
      toetende Mutation mit Zahl
- [x] Keine Secrets, keine TODOs, kein toter Code, keine neue Abhaengigkeit
- [x] Die Abnahmepunkte (1) bis (6) selbst durchgespielt — (2) mit dem
      Vorbehalt aus 8.5
- [x] README und Beraterzeile nachgezogen, Bericht geschrieben
- [ ] **Ungeprueft: jede Plattform ausser Windows 10.** Es wurde kein macOS-,
      Linux-, Android- oder iOS-Lauf gemacht. Der geaenderte Code ist reines
      Python ohne Plattformzweig, aber gepruefte Plattform ist genau eine.
- [ ] **Ungeprueft: die Oberflaeche am Bildschirm.** Alle Qt-Laeufe waren
      offscreen. Ob "Spell power 237" auf der Arsenal-Kachel in die 200 px
      passt, ohne umzubrechen, hat niemand gesehen — UI_SPEC §3.3 hat die
      Zeilenbreite fuer `AR at +1` einmal ausdruecklich geprueft, und
      "Spell power" ist deutlich laenger als "AR". **Das ist eine Luecke,
      kein Beleg.**

## 11. An den `qa-engineer`

Was zu pruefen ist, mit den Kanten, die ich kenne:

1. **Die Abnahmeliste** (1)-(6). Zu (2) siehe 8.5: die sichtbare Reihenfolge
   des Tabs ist nicht die Rangliste. Zu (6): die Zahlen stehen in Abschnitt 6,
   die Aufnahmen liegen im Scratchpad dieser Session und sind mit `plan.py` /
   `capture.py` / `compare.py` / `ratios.py` reproduzierbar.
2. **Am Bildschirm**, nicht offscreen: passt `Spell power 237` in die
   Arsenal-Kachel? Und in die Slot-Kachel neben Raritaet und Effektzahl
   (`Uncommon +1 · 184 Spell power`)?
3. **Die Tafel fuer einen Katalysator.** Sie hat jetzt keine Typzeile mehr,
   nur die Kopfzeile `Spell power  vorher  Aenderung  nachher`. Bewegt sich
   die Zahl, wenn ein Relikt Intelligenz hebt? (Sie soll.) Bewegt sie sich,
   wenn ein Relikt `physicsAttackRate` hebt? (Sie soll **nicht** — Abschnitt 3.)
4. **Der Aufklapp-Text** auf der Summenzeile eines Stabes: Ueberschrift
   `Spell power — <Name>`, "From attributes", und "nothing equipped moves this
   weapon" bei nacktem Build.
5. **Die Beraterzeile** mit einem Stab als Referenzwaffe: `Spell power 128`
   statt `Attack rating 25`, und der Vorbehalt in `unknowns` mit "own rarity"
   und "spell hits for".
6. **Der Auswahldialog**: `Recluse's Staff · 33750000` und
   `Recluse's Staff · 33770000` sind unterscheidbar; `Scholar's Thrusting
   Sword` erscheint viermal mit Id; jeder andere Name **ohne** Id.
7. **Katalysator-Randfaelle**: `Finger Seal` erscheint zweimal mit identischen
   Zahlen; die zweite `Recluse's Staff` zeigt 151 und ist im Tab nicht von der
   echten zu unterscheiden (8.1).
8. **Die laute Extraktion**: den Feldnamen in `extract.CATALYST_SCALING_FIELD`
   verbiegen und den Schnappschuss neu bauen lassen — der Bau muss abbrechen
   und im Text den Feldnamen und die Konstante nennen.

## 12. An den `ui-ux-designer`

* Wortwahl `"Spell power"` fuer Staebe **und** Siegel, wie der Auftrag es
  vorgibt, falls du nicht gezogen wirst. `"Incantation power"` fuer Siegel
  waere eine Aenderung an zwei Konstanten in `nrplanner/damage.py`
  (`SPELL_POWER_LABEL` wuerde zu zwei Werten, gewaehlt nach
  `weapon["family"]`), plus eine Neuaufzeichnung der Golden-Datei.
* Zwei Abweichungen, die du kennen solltest: die Kachel eines Katalysators hat
  **keine** Schadensart-Zeilen mehr (die waren die physische AR), und die
  Summenzeile der Tafel heisst bei ihm `Spell power` statt `Total`, weil ueber
  ihr nichts steht, was summiert waere.
* Der offene Text in 8.2.
