# T-051 — QA-Retest: die beiden Kalibrierungen (T-045 und T-046)

```
STATUS: erledigt
AUFTRAG: T-051 (Retest der Abnahmelisten aus T-045 und T-046, inkl. Nachholen
         von T-045 Abnahmepunkt 3 auf Level 12)
GELESEN: GOAL.md, docs/state.md, docs/tasks/T-051.md, docs/tasks/T-045.md
         (mit Director-Nachtrag), docs/tasks/T-046.md,
         docs/berichte/T-045-developer.md, docs/berichte/T-046-developer.md,
         qa/findings.md (vollstaendig, 1542 Zeilen), scripts/differential/
         __init__.py, plan.py, capture.py, mutate.py (Registry),
         nrplanner/weapons.py, nrplanner/damage.py, nrplanner/arsenaltab.py
         (Ausschnitte _build_weapons/Section/recalculate), nrdata/extract.py
         (Ausschnitt catalyst_scaling_rates + Aufrufstelle),
         tests/weapon_damage_cases.py, tests/conftest.py,
         tests/test_attack_power_against_the_game.py,
         tests/data/game_catalyst_scaling.json (Header),
         tests/golden/weapon_damage.json (Diff 89015aa..HEAD),
         nrplanner/advisor/goals.py (Ausschnitt _ATTACK_RATING_UNKNOWNS),
         README.md (Known limits), eigenes Agent-Gedaechtnis
         (project_differential_harness.md, project_attack_rating_calibration.md,
         feedback_measure_the_state_a_comparison_test_runs_in.md,
         project_nightreign_guard_gaps.md)
GEÄNDERT: docs/berichte/T-051-qa-engineer.md (diese Datei) — sonst nichts im
          Arbeitsbaum. Alle Mutationen, Sonden und der eine git-archive-Klon
          liefen in C:\Users\Daniel\AppData\Local\Temp\claude\...\scratchpad\
          T051\ (head, head2 .. head6, probe_*.py) — ephemer, nicht Teil der
          Abgabe. `git status` im Arbeitsbaum vor und nach meinem Lauf
          verglichen: waehrend meiner Session sind zusaetzlich ein neuer
          Ordner `docs/screenshots/2026-09-05/` und eine rein additive
          Aenderung an `DESIGN_REVIEW.md` (+207 Zeilen, per `git diff
          --stat` selbst geprueft) aufgetaucht. Beides habe ich nicht
          angelegt/geaendert — ich habe `DESIGN_REVIEW.md` in dieser Session
          nie geoeffnet. Vermutlich der parallel laufende `ui-ux-designer`
          im selben Arbeitsbaum.
ANNAHMEN: (1) T-045 Abnahmepunkt (2) zaehlt als erbracht, weil der Auftrags-
          text selbst "Ausnahmen aufgelistet" zulaesst und die Quittung in
          T-051 die 870 Faelle bereits als bekannte, erklaerte Ausnahme
          nennt — siehe meine Antwort auf OF-4 unten. (2) Ich habe den
          vollen ~20-Minuten-Sweep beider Raster nicht selbst neu gefahren
          (Kosten/Nutzen); wo ich eine Zahl nicht selbst nachgerechnet habe,
          steht das explizit dabei, zusammen mit dem, was ich stattdessen
          geprueft habe (Mechanismus im Code, Golden-Datei direkt aus den
          Git-Blobs neu berechnet, Stichproben-Mutationen). (3) QA-123
          (Abschnitt unten) ist an sechs Waffen exakt nachgewiesen; ich habe
          NICHT gegen die tatsaechlichen (nicht im Repo liegenden)
          Capture-Dateien der Entwickler-Laeufe geprueft, wie viele der dort
          gemeldeten "unveraendert"-Faelle genau daran liegen.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

## Kurzfassung

Der wichtigste Einzelpunkt ist geschlossen: **Wylder Lv12 Dagger zeigt 74 auf
Kachel, Tafel und Arsenal-Tab** — gegen die echte, laufende Oberflaeche
gemessen (Planner-Instanz, kein Mock), nicht nur gegen die Fassadenfunktion.
Alle 4 Abnahmepunkte aus T-045 und alle 6 aus T-046 sind **erbracht**. Von den
drei Zusatzfragen ist QA-120 **bestaetigt**, QA-115 **mit den vorhandenen
Werkzeugen nicht pruefbar** (braucht ein Skript), und die QA-118-Klasse bleibt
ein **Einzelfall** — vier weitere stichprobenartig gepruefte Testdateien
faengen ihre Aenderung wirklich. Zwei neue, kleine Befunde in der
Mess-Infrastruktur (QA-123, QA-124), keiner davon ein Produktivfehler.

---

## 1. Abnahme T-045

### (1) Charakterisierung gegen Spielwerte gruen, beide Mutationen rot — **erbracht**

- `tests/test_attack_power_against_the_game.py` unmutiert: **26 passed**
  (23 Ablesungen + 3 Stuetztests), selbst gefahren.
- `attack-power-rate-neutralised` (0,6 → 1,0), eigener `git archive
  HEAD`-Klon, eigene Anwendung von `mutate.py --apply`: **24 failed** in
  dieser Datei (23 Ablesungen + `test_the_factor_is_named_once_and_is_the_
  measured_one`) — deckt sich exakt mit dem Bericht.
- `attack-power-rounded-instead-of-truncated` (`floor`→`round`), eigener
  frischer Klon: **10 failed** in derselben Datei — exakt die zehn
  Ablesungen mit Nachkommaanteil ≥ 0,5, deckt sich exakt.
- Beide Mutationsdiffs selbst gegengelesen (`diff` gegen `git show HEAD:...`):
  genau eine Zeile, genau die behauptete.

### (2) Verhaeltnis neu/alt = 0,6 auf 1 ULP, Ausnahmen aufgelistet — **erbracht**

Eigene, von den Berichten unabhaengige Neuberechnung direkt aus den
Git-Blobs (`git show 89015aa:tests/golden/weapon_damage.json` gegen
`git show HEAD:...`, eigenes Diff-Skript, kein `ratios.py`-Aufruf):

- 51 numerische Blattwerte bewegt. Sechs davon liegen in den beiden
  Katalysator-Faellen (Glintstone Staff Tier 3, Recluse's Staff Tier 2) und
  sind **keine** 0,6-Faelle mehr, weil T-046 sie auf die Kennzahl umgestellt
  hat (erwartungsgemaess, siehe QA-120 unten).
- Die verbleibenden **45 "gewoehnlichen" Zahlen**: min. Verhaeltnis
  0,5999999976380164, max. 0,6000000026163228, **groesster Abstand von 0,6:
  2,6 × 10⁻⁹** — vollstaendig aus der 6-Dezimal-Rundung der Golden-Datei
  erklaerbar, deckungsgleich mit der Groessenordnung, die der Bericht nennt.
- Den vollen 32 274-Fall/115 839-Zahlen-Sweep ueber beide Raster habe ich
  **nicht** selbst wiederholt (Kostenschaetzung laut Bericht ~20 Minuten je
  Baumpaar). Vertrauensbasis dafuer: der Mechanismus ist im Code direkt
  nachgelesen (`nrplanner/weapons.py:301` und `:357` — der Faktor sitzt an
  exakt zwei Multiplikationen, keine Anpassung), die Summierung laeuft
  ueber eine handgeschriebene Schleife statt `sum()` (Zeile 307-317,
  bestaetigt den behaupteten Mechanismus fuer die 2-3-ULP-Ausnahmen als
  Rundungsartefakt der Summenbildung, nicht als zweite Fehlerquelle), und
  alle bisher unabhaengig nachgefahrenen Einzelwerte (Dagger, Golden-Datei)
  trafen exakt.
- **Antwort auf OF-4** (Frage des developer an mich): "1 ULP je Wert" kann
  sich nur auf das beziehen, was die Messstrecke tatsaechlich aufzeichnet —
  und das sind laut Code (`damage.breakdown_figures`,
  `tests/weapon_damage_cases.arsenal_figure`) ausschliesslich die
  **Summen** (`last_ar.base/scaled/final`, `arsenal_figure`), nie die Zahl
  je Schadensart. Eine Lesart "je Schadensart" waere mit der Messstrecke,
  die den Auftragstext selbst nennt ("ueber die gesamte Messstrecke"), gar
  nicht pruefbar — der Auftrag kann also nur die Summen gemeint haben.
  Damit ist Abschnitt 4.1 des Berichts (870 Zahlen bei 2-3 ULP, alles
  Summen) eine **benannte, im Rahmen des Kriteriums zulaessige Ausnahme**,
  kein offener Punkt.

### (3) Kachel, Tafel und Arsenal-Tab zeigen fuer Wylder Lv12 / Dagger die 74 — **erbracht** (nachgeholt)

Dies war nicht erbracht (Messung lief auf Lv15) und ist der Grund fuer diesen
Retest. Nachgemessen gegen die **echte, laufende Oberflaeche** — ein reales,
headless `nrplanner.app.Planner`-Objekt, keine Fassadenfunktion allein —
fuer Wylder, Level 12, Dagger (id 1000000, Common, eigene Raritaet, Tier 1),
ohne Relikte, `PYTHONHASHSEED=0`:

| Ort | Rohwert | Angezeigt |
|---|---|---|
| `damage.candidate()` (Fassade) | `final_total = 74.1846912` | `displayed() = 74` |
| Waffen-Kachel (Slot-Tile) | — | `"Common · **74** AR"` |
| Detailtafel (Breakdown-Popup) | — | `"Base 74 ... Total 74 (+0, +0.0%)"` |
| Arsenal-Tab (Kachel, erzwungen geoeffnet — Begruendung unten) | `arsenal_figure = 74.1846912` (hex-exakt) | `AR 74` |

Alle drei genannten Oberflaechen zeigen **74**, deckungsgleich mit der
Spielmessung aus T-038 (Fan-Tabelle 74, Sonde 74) und mit
`123,641 (alter Wert vor T-045) × 0,6 = 74,1846...`.

**Randbefund waehrend der Messung, methodisch relevant:** Die Standard-
Erfassung (`tests/weapon_damage_cases.arsenal_reading`) sucht im Arsenal-Tab
nach dem **eigenen Namen** der Waffe ("Dagger"). Die Familie "Dagger" hat
73 Mitglieder (alle Infusionsvarianten mehrerer Dolch-Waffen, die dieselbe
`family`-Kennung tragen); der Auto-Aufklapp-Schwellenwert des Tabs liegt bei
60. Die Sektion bleibt deshalb zu, und `arsenal_tiles` kommt aus der
Standard-Erfassung **leer** zurueck — nicht weil nichts gerendert wird,
sondern weil niemand hinschaut. Ich habe die Sektion in meiner eigenen Sonde
programmatisch geoeffnet (`section.expand_all()`, wie ein Nutzer-Klick), um
die 74 tatsaechlich am gerenderten Text abzulesen. Das ist kein
Produktivfehler (ein echter Nutzer kann die Sektion anklicken), aber eine
Luecke der Mess-Infrastruktur — siehe **QA-123** unten.

### (4) AD-021-Waechter gruen — **erbracht**

`tests/test_one_build.py::test_only_the_facade_calls_weapons_rate_or_rank`
selbst gefahren: **1 passed**. `ARITHMETIC_ENTRY = frozenset({"rate",
"rank"})` bestaetigt (Zeile 358).

---

## 2. Abnahme T-046

### (1) 84/84 und 28/28 gruen, vier Mutationen rot — **erbracht**

- `tests/test_catalyst_scaling_against_the_game.py` unmutiert: **117
  passed** (84 + 28 + 5 Stuetztests), selbst gefahren.
- Von den vier fuer diesen Punkt registrierten Mutationen habe ich **drei**
  selbst in frischen Klonen angewendet und die Zieldatei(en) selbst
  gefahren, jeweils mit exakter Uebereinstimmung zum Bericht:

  | Mutation | eigenes Ergebnis | Bericht | Uebereinstimmung |
  |---|---|---|---|
  | `catalyst-scaling-rate-ignored` (`unknown_1`→1,0) | 105 failed, 12 passed | 105 rot | exakt |
  | `attack-power-rounded-instead-of-truncated` (`floor`→`round`) | 55 failed (39/84 + 16/28), 62 passed | 55 rot | exakt |
  | `catalyst-scaling-field-renamed` (gehoert zu Punkt 4, s. u.) | 3 von 4 rot | 3/4 rot | exakt |

  **Nicht selbst gefahren:** `catalyst-curve-hardcoded-to-zero` (Kurve
  16→0, Bericht: 113 rot) und `catalyst-influence-inside-the-bracket`
  (Einfluss 0,9 in die Klammer, Bericht: 91 rot). Angesichts der 100 %-
  Trefferquote der drei selbst gefahrenen Mutationen (inkl. der beiden aus
  T-045) halte ich die verbleibenden zwei fuer sehr wahrscheinlich korrekt,
  habe sie aber nicht nachgerechnet — das ist eine Vertrauensuebernahme,
  keine eigene Messung.

### (2) Arsenal-Tab reiht Carian Regal Scepter vor Rotten Crystal Staff (237 vor 182) — **erbracht**

Doppelt gegengeprueft, mit derselben Praezisierung, die der Bericht selbst
schon nennt (Abschnitt 8.5):

- `damage.rank_candidates(build, 1, data)` fuer Recluse Lv12: Carian Regal
  Scepter auf **Platz 3** (237), Rotten Crystal Staff auf **Platz 20**
  (182) — die interne Rangliste.
- Die **tatsaechlich gerenderte** Arsenal-Tab-Kachelreihenfolge (Sektion
  "Glintstone Staff" erzwungen geoeffnet, Suchtext `"Glintstone Staff"`,
  Raritaetsfilter "All"): Scepter auf **Grid-Position 1**, Rotten Crystal
  Staff auf **Grid-Position 11**, unter 20 gerenderten Kacheln.
- Wie der Bericht offenlegt: der sichtbare Tab sortiert **nicht** nach der
  Zahl, sondern nach Raritaet (absteigend), dann Name, dann Id — direkt
  bestaetigt: Position 2/3 sind "Azur's Glintstone Staff" (209) **vor**
  "Lusat's Glintstone Staff" (212), also nicht wertabsteigend, sondern
  alphabetisch innerhalb derselben Raritaetsstufe. Der Abnahmepunkt trifft
  hier zu, **weil** Scepter Legendary und Rotten Crystal Staff Common ist,
  nicht weil der Tab nach der angezeigten Zahl sortiert.

### (3) Recluse's Staff zeigt fuer Recluse Lv12 die 128 — **erbracht**

`damage.candidate()` fuer id 33750000 (die echte Startwaffe der Recluse):
`final_headline = 128.65909451788121` → `displayed() = 128`. Am gerenderten
Arsenal-Tile bestaetigt: `['', "Recluse's Staff", 'Spell power', '128', ...]`.

Randnotiz, keine neue Erkenntnis: die zweite, nicht spielbare Zeile
(id 33770000) rendert **ebenfalls** als "Recluse's Staff", zeigt **151** und
ist von der echten Waffe nicht zu unterscheiden — das ist QA-119, bereits
erfasst und hiermit unabhaengig gegengeprueft (nicht neu gemeldet).

### (4) Extraktion bricht laut ab, wenn `unknown_1` fehlt — **erbracht**

Eigene Mutation (Feldname `unknown_1` → `spellAttackRate`) in einem frischen
`git archive HEAD`-Klon, `tests/test_catalyst_scaling_extraction.py`
gefahren: **3 von 4 failed**, mit
```
ValueError: ReinforceParamWeapon has no 'spellAttackRate' field in this
paramdef, and it is the only place the spell scaling of staves and seals is
written (offset 128, the last field of the row). It has most likely been
renamed by a Paramdex update: find the new name for offset 128 and put it
in extract.CATALYST_SCALING_FIELD. ...
```
Nennt sowohl den (mutierten) Feldnamen als auch den Ort der Konstante, wie
gefordert. Die Aufrufstelle `catalyst_scaling_rates(reinforce_table)` liegt
in `nrdata/extract.py:2334`, direkt im Hauptextraktionspfad (nicht in totem
Code) — per `grep` bestaetigt. Die volle Live-Extraktion (~40 s gegen das
installierte Spiel) habe ich dafuer nicht zusaetzlich gefahren; der
Stub-Test deckt exakt die Zeile, die dabei auch auslösen wuerde.

### (5) AD-021-Waechter gruen — **erbracht**

Identisch mit T-045 Punkt (4), derselbe Waechter, kein zweiter Test.

### (6) Keine Aenderung an Nicht-Katalysator-Werten — **erbracht**

Nicht durch einen neuen vollen Sweep, sondern durch zwei zusammenpassende
Belege:

1. **Code-Pfad-Argument**, selbst gelesen: `_catalyst_scaling()` gibt fuer
   jede Nicht-Katalysator-Waffe ganz am Anfang `None` zurueck
   (`weapon_class(weapon) != "catalyst"`); der Rest von `rate()` — die
   Schleife ueber `DAMAGE_TYPES`, `base`/`scaled` — ist gegenueber dem
   Stand nach T-045 unveraendert. `scaled_headline()`/`final_headline`
   fallen fuer `catalyst_scaling is None` auf genau die alte Summe zurueck.
   Ein Nicht-Katalysator kann diesen Code strukturell gar nicht anders
   sehen als vor T-046.
2. **Ein eigener Messpunkt**: Dagger (Nicht-Katalysator) liefert nach T-046
   exakt den Wert, der nach T-045 allein erwartet wuerde (74.1846912,
   s. o.) — keine Verschiebung.

Den vollen Sweep (T-046-Bericht Abschnitt 6: 0 von 114 939 zugeordneten
Zahlen bewegt) habe ich nicht wiederholt.

---

## 3. Die drei Zusatzfragen aus T-051

### QA-118 als Klasse — **kein systemisches Muster, Einzelfall bestaetigt**

Methodik: die Fassung einer Testdatei **vor** der jeweiligen Aenderung gegen
den **heutigen** Anwendungscode laufen lassen (git-archive-Klon, Datei
ausgetauscht, restlicher Baum HEAD). Erst die volle T-045+T-046-Spanne
(`89015aa` → HEAD), dann zusaetzlich isoliert T-046s eigenen Anteil
(`2a6bb3e` → HEAD, also nur was `f595edb` an denselben Dateien noch
draufgelegt hat):

| Datei | volle Spanne (89015aa→HEAD) | nur T-046-Anteil (2a6bb3e→HEAD) |
|---|---|---|
| `test_advisor_goals.py` | 2 rot | 1 rot |
| `test_arsenal_tab_asks_the_facade.py` | 2 rot | 1 rot |
| `test_arsenal_tab_wiring.py` (nur T-045) | 2 rot | — |
| `test_damage_facade.py` | 2 rot | 2 rot |
| `test_move_scoped_effects.py` | **0 rot** | **0 rot** |

Vier von fuenf gepruefte Dateien fangen ihre eigene Aenderung wirklich —
mit der alten Fassung wird der heutige Code rot, in exakt den vom
T-045-Bericht selbst schon benannten Faellen (`test_the_damage_goal_
always_carries_the_attack_rating_reservation`,
`test_the_score_is_unrounded_and_the_display_is_the_rounded_one` fuer
`test_advisor_goals.py` — deckungsgleich). **Nur
`test_move_scoped_effects.py` ist in beiden Anlaeufen (T-045 und jetzt auch
T-046) wirkungslos** — bestaetigt QA-118 und erweitert seinen Befund: auch
T-046s zusaetzlicher Touch derselben Datei ist nicht durch einen roten Test
erzwungen. Ich empfehle, das im bestehenden QA-118-Eintrag nachzutragen
statt eine neue ID zu vergeben (siehe QA-Log).

`tests/conftest.py` und `tests/weapon_damage_cases.py` passen nicht in
dieses Pruefschema (kein Assertion-Code): `weapon_damage_cases.py`s Diff ist
per `git diff` bestaetigt reiner Docstring-Text (keine Code-Zeile
veraendert); `conftest.py`s Aenderung ist Fixture-Infrastruktur (Fallback
bei veraltetem Snapshot), fuer die "alte Fassung gegen neuen Code" keine
sinnvolle Frage ist — ich habe sie gelesen, sie ist in sich stimmig, aber
ungetestet durch einen eigenen Fall. Keine neue Meldung dazu (siehe
"Nicht getestet").

### QA-115 — **mit den vorhandenen Werkzeugen nicht pruefbar; braucht ein Skript**

Direkt am Code bestaetigt, nicht nur vermutet: `planner.last_ar =
damage.breakdown_figures(bare, now)` (`nrplanner/app.py:2922`) liefert
ausschliesslich `base`/`scaled`/`final` als **Summen** (`scaled_headline`/
`final_headline`), nie die Zahl je Schadensart. Die Text-Felder
(`tiles`/`panel`/`breakdown`/`arsenal_tiles`) enthalten zwar
Pro-Typ-Zeilen ("Physical 74"), aber schon auf die Anzeigeziffer
abgeschnitten (`damage.displayed()`), also ohne die Nachkommastellen, die
ein ULP-Vergleich braucht. Weder `capture.py` noch `ratios.py` haben also
irgendwo Zugriff auf die rohen Werte je Schadensart.

**Antwort:** Nein, mit der heutigen Messstrecke ist die per-Typ-Aussage
nicht nachpruefbar. Um sie zu belegen, braucht es ein neues Skript (den
fehlenden `dump_rate.py` nachbauen, das `weapons.rate(...).base`/`.scaled`
direkt fuer jede Kombination abfragt und vergleicht) — eine reine
Textaenderung kann die Zahl im Kommentar nicht neu belegen, sondern nur den
Anspruch zurücknehmen (auf das beschraenken, was die Summen hergeben, siehe
Abschnitt 1 Punkt 2 oben).

### QA-120 — **bestaetigt**

Direkter Beleg in der eigenen Datenquelle, nicht nur in der Selbstauskunft
des Berichts: `tests/data/game_catalyst_scaling.json`, Feld
`source.left_out`, woertlich: *"Upgraded catalysts: the sheet reads each
armament at its own rarity, so nothing here says what a reinforced staff
shows."* Die beiden golden-Faelle mit den fraglichen Zahlen sind per `grep`
identifiziert und ihre Tier-Angabe gegen `tests/weapon_damage_cases.py`
gegengelesen: Fall 10 "catalyst: magic buff idle, Intelligence at work"
(Glintstone Staff, `tier: 3`, Ergebnis 236) und Fall 11 "Recluse on her own
starting armament" (Recluse's Staff, `tier: 2`, Ergebnis 184) — beide
oberhalb der eigenen Raritaet (Tier 1), also exakt in der oben zitierten
ausgeschlossenen Kategorie. Die Golden-Datei friert damit tatsaechlich zwei
Zahlen ein, fuer die es keine externe Messung gibt.

---

## 4. Neue Befunde

### [P3 | Minor | Mittel] Die Arsenal-Tab-Messstrecke ist fuer sechs Waffen strukturell blind gegenueber Kachel-Text

**Adressat:** developer
**Betroffen:** `tests/weapon_damage_cases.py::arsenal_reading` (Suchtext =
Waffenname) im Zusammenspiel mit `nrplanner/arsenaltab.py::rebuild`
(Auto-Aufklapp-Schwelle `0 < shown <= 60`, Zeile ~297) und
`arsenaltab.Section` (Kacheln werden erst beim Aufklappen gebaut, Zeile
120-168)
**Umgebung:** installierte Spieldaten, `data_version 10350000`

**Reproduktion:**
1. `search.parse('"Dagger"')` gegen alle 1793 Waffen des Datensatzes
   auswerten (Blob = Name + `family`).
2. 73 Waffen matchen (alle Infusionsvarianten mehrerer Dolch-Waffen tragen
   `family == "Dagger"`).
3. `arsenal_reading()` setzt den Suchtext exakt auf `f'"{weapon["name"]}"'`
   — fuer Dagger also `"Dagger"`.
4. `rebuild()` oeffnet eine Sektion nur automatisch, wenn `0 < shown <= 60`
   — bei 73 Treffern bleibt sie zu, `findChildren(Tile)` liefert **nichts**.

**Erwartet:** Die Messstrecke erfasst, ob sich der gerenderte Kachel-Text
einer Waffe veraendert hat.
**Tatsaechlich:** Fuer sechs Waffen ist `arsenal_tiles` in **jedem** Lauf
leer, unabhaengig davon, ob sich der Text tatsaechlich geaendert hat — ein
Vergleich zweier leerer Listen ist immer "unveraendert".

**Analyse:** Eigene, vollstaendige Auszaehlung ueber alle 1793 Waffen (nur
`nrplanner.search` + der Datensatz, kein Qt noetig): sechs Waffen matchen
mit dem eigenen Namen mehr als 60 Datensaetze —

| Waffe | id | Family | Treffer |
|---|---|---|---|
| Dagger | 1000000 | Dagger | 73 |
| Greatsword | 4000000 | Colossal Sword | 138 |
| Hammer | 11080000 | Hammer | 171 |
| Greataxe | 15000000 | Greataxe | 85 |
| Spear | 16010000 | Spear | 110 |
| Halberd | 18000000 | Halberd | 97 |

Im Raster `arsenal_tab` (sweept laut T-046-Bericht "1793 (jede)") sind das
6 × 4 Konfigurationen = **24 von 7172 Datensaetzen**, bei denen
`arsenal_tiles` strukturell nichts sehen kann — unabhaengig vom Baum. Direkt
nachgewiesen an Dagger: mit erzwungenem `section.expand_all()` (wie ein
Nutzer-Klick) rendert dieselbe Kachel sofort `['', 'Dagger', 'AR', '74',
'Physical', '74', 'Scaling', 'STR 13 · DEX 73', 'Rarity', 'Common']`.

**Auswirkung:** Kein Produktivfehler — ein echter Nutzer kann die Sektion
anklicken, die Daten dahinter (`arsenal_figure`, `arsenal_listed`) sind
unberuehrt und korrekt. Betroffen ist ausschliesslich die Aussagekraft der
Differential-Messstrecke: die "50 unveraendert" in T-045 Abschnitt 2 und die
"0 Nicht-Katalysator-Datensaetze mit echter Aenderung" in T-046 Abschnitt 6
koennten fuer diese 24 Datensaetze auf einer leeren-gegen-leere-Liste
beruhen statt auf einer echten Pruefung. Fuer T-045/T-046 selbst ist das
folgenlos, weil die tragenden Zahlenbeweise beider Berichte auf
`last_ar`/`arsenal_figure` stehen (unbetroffen) und nicht auf
`arsenal_tiles` allein — aber der naechste Bericht, der sich auf
"arsenal_tiles unveraendert" als alleinigen Beleg fuer eine dieser sechs
Waffen(-familien) verlaesst, misst nichts.

**Vorschlag:** `arsenal_reading()` koennte die betroffene(n) Sektion(en)
unabhaengig vom Auto-Schwellenwert gezielt oeffnen (z. B. `section.
expand_all()` wie in dieser Sonde), statt sich auf Suchtext+Schwelle zu
verlassen — das Werkzeug kennt die gesuchte Waffe ohnehin schon per Id.

---

### [P4 | Trivial | Niedrig] Die Zeilen-Zusammenfassung des Arsenal-Tabs liest die Stufe vom Schieberegler, nicht vom gemessenen Build

**Adressat:** developer
**Betroffen:** `nrplanner/arsenaltab.py:245`
(`level = self.planner.level_slider.value()`)
**Umgebung:** nur beim Treiben des Planners ueber
`tests/weapon_damage_cases.py` bzw. `scripts/differential/capture.py`
(`planner._build` wird direkt gesetzt, der Schieberegler nie bewegt)

**Reproduktion:**
1. Eigene Sonde: `planner._build = model.compute(wylder, 12, ...)` direkt
   setzen (wie `arsenal_reading()` es tut), `tab.recalculate()` aufrufen.
2. `tab.summary.text()` lesen.

**Erwartet:** Der Satz nennt die Stufe, mit der tatsaechlich gerechnet
wurde (12).
**Tatsaechlich:** `"Wylder at level 1, +1 · VIG 46 ..."` — die Attributwerte
sind korrekt (Level 12), die Zahl hinter "at level" ist es nicht, weil sie
direkt vom nie bewegten `QSlider` (Minimum 1) kommt statt vom `build`.

**Analyse:** `recalculate()` liest `level = self.planner.level_slider.
value()` separat von `build = self.planner.current_build()`. Im echten
Programm laufen beide immer synchron (der Slider loest `recompute()` aus,
das `_build` neu setzt), deshalb ist das im Produktivbetrieb **kein**
beobachtbarer Fehler. Er zeigt sich ausschliesslich, wenn ein Aufrufer
(Testwerkzeug) `_build` direkt setzt, ohne den Slider zu bewegen — genau
das Muster aus [[feedback-measure-the-state-a-comparison-test-runs-in]].

**Auswirkung:** Keine fuer Nutzer. Fuer Messwerkzeuge: die "Stufe" im
`arsenal_summary`-Text jeder Differential-Aufnahme ist strukturell falsch
(vermutlich immer "level 1"), was bislang folgenlos ist, weil kein
gepruefter Bericht sich auf genau diese Teilzeichenkette verlaesst — beide
Seiten eines Vorher/Nachher-Vergleichs tragen denselben Fehler, ein Vergleich
bleibt also gueltig, eine Behauptung "gemessen bei Level X anhand des
Summary-Texts" waere es nicht.

**Vorschlag:** Falls die Messstrecke den Summary-Text je einmal fuer
belastbar halten soll, `recalculate()` die Stufe aus `build` statt aus dem
Slider lesen lassen, oder das Testwerkzeug den Slider mitfuehren.

---

## 5. Zusammenfassung (an director)

**4 von 4 Abnahmepunkten aus T-045 erbracht, 6 von 6 aus T-046 erbracht.**
Der zuvor offene Punkt (Wylder Lv12 Dagger = 74) ist jetzt gegen die echte
Oberflaeche nachgewiesen, nicht nur gegen die Fassade. Die drei Zusatzfragen
sind beantwortet: QA-120 bestaetigt, QA-115 braucht ein Skript (kein reiner
Textfix), QA-118 bleibt ein Einzelfall (vier von fuenf gepruefte
Testdateien faengen ihre Aenderung wirklich). Zwei neue, kleine
Infrastruktur-Befunde (QA-123, QA-124), keiner ein Produktivfehler, beide
P3/P4.

**Releasefaehig fuer die beiden Kalibrierungen selbst: ja**, aus QA-Sicht
nichts, was T-045/T-046 zurueckhalten muesste. Offen bleiben ausschliesslich
Punkte, die die Entwickler-Berichte selbst schon an den `director` oder
`ui-ux-designer` addressiert haben und die nicht Gegenstand dieses Retests
waren (OF-1/OF-2 zu `ratios.py`/Paket-Docstring — Letzterer ist inzwischen
durch T-046 ohnehin nachgezogen, "Five steps, five scripts" steht bereits
im Docstring —, D-2/QA-116 zum ueberholten Vorbehaltssatz in UI_SPEC.md/
ARCHITECTURE.md, QA-119/QA-121/QA-122 zur Oberflaeche, alle bereits erfasst).

## 6. Explorationsprotokoll

- Volle Suite zweimal selbst gefahren: `-m "not slow"` → 563 passed, 5
  deselected (88,24 s); `-m "slow"` → 5 passed (52,12 s). Deckt sich exakt
  mit dem gemeldeten Ist-Stand, keine Regression.
- Fuenf frische `git archive HEAD`-Klone fuer Mutationen angelegt (im
  Scratchpad), fuenf Mutationen selbst angewendet und gefahren (2 fuer
  T-045, 3 fuer T-046 — davon eine, `attack-power-rounded-instead-of-
  truncated`, deckt beide Auftraege ab), alle mit exakt uebereinstimmenden
  Fehlerzahlen.
- Eine eigene Sonde gegen eine echte, headless `Planner`-Instanz gebaut
  (kein Mock), um Wylder Lv12 Dagger auf allen drei Oberflaechen zu lesen —
  inklusive erzwungenem Aufklappen einer Arsenal-Tab-Sektion, um den
  gerenderten Text zu sehen statt nur die Fassadenzahl.
- Golden-Datei (`tests/golden/weapon_damage.json`) direkt aus den
  Git-Blobs 89015aa/HEAD verglichen, eigenes Diff-/Ratio-Skript, ohne
  `ratios.py` zu benutzen — Gegenprobe zur Messstrecke des developers,
  nicht Wiederholung.
- QA-118-Klasse: fuenf mitgeaenderte Testdateien mit der "alte Fassung
  gegen neuen Code"-Methode geprueft, je zwei Zeitpunkte (volle Spanne und
  isolierter T-046-Anteil).
- README.md "Known limits" und `nrplanner/advisor/goals.py`s
  `_ATTACK_RATING_UNKNOWNS` gelesen und gegen die Berichte abgeglichen —
  deckungsgleich, kein Widerspruch gefunden.
- `git status` vor/nach meinem Lauf verglichen: keine eigene Aenderung im
  Arbeitsbaum ausser diesem Bericht.

## 7. Offene Fragen

Keine neuen an eine andere Rolle — die einzige mir explizit gestellte Frage
(OF-4 des developer) ist oben unter T-045 Punkt (2) beantwortet.

## 8. Nicht getestet

- Der volle ~20-Minuten-Sweep beider Raster (`tiles_and_panel`,
  `arsenal_tab`) wurde nicht komplett neu gefahren — Begruendung und
  Ersatzbeleg jeweils bei den betroffenen Abnahmepunkten. Falls der
  `director` eine vollstaendig unabhaengige Neumessung fuer noetig haelt
  (z. B. vor einem Release), ist das ein eigener, benennbarer Auftrag.
- Zwei der fuenf fuer T-046-Punkt (1) registrierten Mutationen
  (`catalyst-curve-hardcoded-to-zero`, `catalyst-influence-inside-the-
  bracket`) nicht selbst gefahren.
- `tests/conftest.py`s Stale-Snapshot-Fallback nicht mit einem eigenen Fall
  durchgespielt (kein eigener Test im Repo, kein Teil der Abnahmeliste).
- Die Oberflaeche am Bildschirm (laeuft parallel beim `ui-ux-designer`,
  ausdruecklich nicht meine Sache laut Auftrag).
- S7/S9, QA-096/097/113 — ausdruecklich ausgenommen.
- Plattformen ausser Windows 10 — wie in beiden Entwicklerberichten
  vermerkt, unveraendert.

## 9. QA-Log

`qa/findings.md` ist 1542 Zeilen lang und baut sich zyklusweise aus
angehaengten Abschnitten auf (nicht eine einzelne Master-Tabelle). Ich habe
sie vollstaendig gelesen; hier der **anzuhaengende neue Abschnitt** im
Format der letzten beiden Abschnitte (T-045/T-050, T-046), plus
Statushinweise fuer bestehende Zeilen, die dieser Retest praezisiert.

**Statushinweise fuer bestehende Zeilen (Text der Zeilen selbst unveraendert
lassen, nur `Verifiziert`/`Status`/`Letzte Pruefung` nachziehen):**

- **QA-118**: unabhaengig bestaetigt (T-051), zusaetzlich erweitert — auch
  T-046s eigener Touch derselben Datei ist wirkungslos. Vier andere
  mitgeaenderte Dateien sind es **nicht**, das Muster ist ein Einzelfall.
  Letzte Pruefung: 2026-09-05.
- **QA-120**: bestaetigt, mit Primaerbeleg (`source.left_out` in
  `tests/data/game_catalyst_scaling.json`). Letzte Pruefung: 2026-09-05.
- **QA-115**: Zusatzbefund — mit den vorhandenen Werkzeugen nicht
  pruefbar, Fix braucht ein Skript, keine reine Textaenderung. Letzte
  Pruefung: 2026-09-05.
- **QA-119**: unabhaengig gegengeprueft (128 vs. 151, beide als
  "Recluse's Staff" gerendert), unveraendert offen. Letzte Pruefung:
  2026-09-05.

**Neuer Abschnitt:**

```markdown
## Zyklus 12, T-051: Retest der beiden Kalibrierungen (2026-09-05)

Quelle: docs/berichte/T-051-qa-engineer.md. Alle vier Abnahmepunkte aus
T-045 und alle sechs aus T-046 unabhaengig erbracht, inkl. Nachholen von
T-045 Punkt (3) auf Level 12 gegen die echte Oberflaeche (Kachel, Tafel,
Arsenal-Tab je 74 fuer Wylder/Dagger). QA-118 bleibt Einzelfall (vier von
fuenf gegengeprueften Testdateien fangen ihre Aenderung wirklich). QA-120
bestaetigt. QA-115: braucht ein Skript, keine Textaenderung.

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| QA-123 | **Die Arsenal-Tab-Messstrecke ist fuer sechs Waffen strukturell blind gegenueber Kachel-Text.** `arsenal_reading()` sucht nach dem eigenen Waffennamen; bei Dagger/Greatsword/Hammer/Greataxe/Spear/Halberd matcht das ueber 60 Familienmitglieder, die Auto-Aufklapp-Schwelle des Arsenal-Tabs (`0 < shown <= 60`) greift nicht, `arsenal_tiles` bleibt leer — 24 von 7172 Datensaetzen im Raster `arsenal_tab` betroffen. Kein Produktivfehler (ein Klick oeffnet die Sektion), aber ein "unveraendert" bei diesen Waffen kann eine leere-gegen-leere-Liste sein statt eine echte Pruefung | P3 | Minor | developer | vollstaendige Auszaehlung ueber alle 1793 Waffen + eigene Sonde gegen die echte Oberflaeche (vorher/nachher erzwungenem Aufklappen) | offen | 2026-09-05 |
| QA-124 | **`arsenaltab.recalculate()` liest die angezeigte Stufe vom `level_slider`, nicht vom gemessenen `build`.** Betrifft nur Werkzeuge, die `planner._build` direkt setzen (wie `weapon_damage_cases.arsenal_reading`, die gesamte Differential-Messstrecke); im echten Programm laufen Slider und Build immer synchron. Der `arsenal_summary`-Text jeder Differential-Aufnahme nennt daher vermutlich durchgehend "level 1" unabhaengig vom tatsaechlichen Fall — folgenlos fuer Vorher/Nachher-Vergleiche (beide Seiten tragen denselben Fehler gleich), aber eine Falle fuer jede kuenftige Behauptung "gemessen bei Level X laut Summary-Text" | P4 | Trivial | developer | eigene Sonde, `planner._build` direkt gesetzt, `tab.summary.text()` gelesen | offen | 2026-09-05 |
```
