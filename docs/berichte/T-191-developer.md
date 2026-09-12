# T-191 — A+C bauen: Attribute als eigene Zielrichtung, Waffen-Buffs raus (developer)

```
STATUS: erledigt
AUFTRAG: T-191 — A+C bauen: Attribute als eigene Zielrichtung, Waffen-Buffs raus
GELESEN: docs/tasks/T-191.md, ~/.claude/agents/_rahmen.md, CLAUDE.md (global
         und Projekt), ARCHITECTURE.md (AD-032 vollstaendig, Z. 2936-3310),
         docs/berichte/T-189-architect.md, qa/findings.md (QA-224, QA-226,
         QA-227), nrplanner/advisor/goals.py, types.py, evaluate.py,
         candidates.py, run.py, worker.py, nrplanner/advisorbar.py,
         nrplanner/relicpicker.py, nrplanner/errortext.py, nrplanner/model.py,
         nrplanner/damage.py, nrplanner/weapons.py, nrplanner/weaponslots.py,
         tests/advisor_cases.py, tests/weapon_damage_cases.py, tests/conftest.py,
         tests/test_advisor_goals.py, test_advisor_worker.py,
         test_advisor_run.py, test_picker_track_guards.py,
         test_exception_text_is_english.py, scripts/differential/mutate.py.
         GOAL.md A17 und docs/state.md nur ueber die Zitate im Auftrag —
         beide trugen den Auftrag, siehe ANNAHMEN.
GEAENDERT: nrplanner/advisor/goals.py, nrplanner/advisor/types.py,
           nrplanner/advisorbar.py, nrplanner/advisor/worker.py,
           nrplanner/relicpicker.py, scripts/differential/mutate.py,
           tests/test_advisor_goals.py, tests/test_advisor_run.py,
           tests/test_advisor_worker.py,
           tests/test_exception_text_is_english.py,
           tests/test_picker_track_guards.py,
           docs/berichte/T-191-developer.md (diese Datei).
           Zwei eigene Commits: `6f369a7` (A+C) und `0882330` (A8).
           Kein push, kein checkout, kein branch, kein stash.
ANNAHMEN: 1) "Unterscheidbar" ist wie in AD-032 |Grenzbeitrag| > 1e-9 am
          freien weissen Slot, 210 gewoehnliche Kopien — ich habe die Zahl
          damit reproduziert, nicht neu definiert.
          2) Der Arbeitstitel der neuen Richtung ("Maximise offensive
          attributes", Einheit `pts`) ist meiner und muss vom
          `ui-ux-designer` bestaetigt werden; AD-032 hat die Richtung
          entschieden, nicht ihren Wortlaut.
          3) Die neue Richtung wird **nicht** in `advisorbar.GOAL_ORDER`
          aufgenommen — Begruendung unten, Punkt 4.
NAECHSTER: director — er braucht eine Entscheidung zu drei Punkten (Umfang
           ueberschritten, dritter Eintrag im `Sort by`, QA-227 waechst).
BLOCKIERT DURCH: nichts.
```

## Urteil

A+C ist gebaut und die Abnahme ist reproduziert: **75 von 210** gewoehnlichen
Kopien sind unter mindestens einer der beiden Schadensspalten unterscheidbar,
und jede Einzelzahl von AD-032 kommt auf die Kopie genau heraus. AK-191 ist
jetzt auch woertlich erfuellt; der Test, der das haelt, war vor der Aenderung
rot und ist es mit zurueckgebauter Aenderung wieder.

**Der Auftrag hat sich in einem Punkt geirrt, und das ist der wichtigste Satz
dieses Berichts:** die Dateigrenze von fuenf Quelldateien ist mit Vorgabe 3
nicht einhaltbar. Der Einzeiler in `worker.py` reisst fuenf weitere Dateien
mit, alle durch bestehende Waechter erzwungen. Ich habe ihn zu Ende gebaut
statt drei rote Tests liegenzulassen, und melde die Ueberschreitung hier als
Befund.

## 1. Was gebaut ist

**Die dritte Zielrichtung** (`nrplanner/advisor/goals.py`):
`MAX_ATTRIBUTES` / `_max_attributes`, die Summe der fuenf offensiven
Attributspunkte (`OFFENSIVE_ATTRIBUTES`), Einheit `ATTRIBUTE_POINT_UNIT` =
`pts`, vier Saetze `_ATTRIBUTE_SCOPE`. Keine Gewichte, keine Umrechnung —
die Zahl ist die ungewichtete Summe, weil jede Gewichtung nach Skalierung
Option B mit mehr Schritten waere (AD-023, OF-13). `_max_damage` ist
**unberuehrt**; die Attribute sind kein Summand darin, und ein eigener Test
haelt das fest.

`ctx` wird in der Funktion nicht gelesen (`del ctx`) — das ist die ehrliche
Form: die Zahl braucht weder Datensatz noch Held noch Gewichtung, weil
`model.compute` alle Caps, Floors und Stat-Swaps schon angewandt hat.

**Die gewuerfelten Buffs fallen** (`nrplanner/advisorbar.py`):
`asking_from` liest das Waffengitter gar nicht mehr — weder
`armament_effect_ids` in den Kontext noch `armaments` in die Anfrage. Beide
mussten zusammen gehen: `run._refuse_a_request_that_asks_about_another_run`
vergleicht die Rollen im Schluessel gegen die im Kontext, und eine von beiden
gefuellt waere die Ablehnung jeder Frage. Damit faellt zugleich P-1 aus T-188
(der Cache-Schluessel trennte zwei Laeufe, die dieselbe Antwort rechnen).

Die Felder bleiben auf `GoalContext` und `AdvisorRequest` stehen und sind in
`types.py` als "vom Programm nicht mehr gefuellt" dokumentiert — wie
`reference` und `weapons_held` seit T-188, aus demselben Grund (A16, Tests).

**A8** (`nrplanner/advisor/worker.py:190`): `errortext.in_english(exc)` statt
`str(exc) or exc.__class__.__name__`. Das war die letzte `str(exc)`-Stelle
auf einem Anzeigeweg.

## 2. Die Messung — Abnahme reproduziert

Skript: `…/scratchpad/T-191/measure_ac.py` (Aufruf:
`python -u measure_ac.py <arbeitsbaum>`). Gemessen gegen den Arbeitsbaum mit
meiner Aenderung, inhaltlich identisch mit Commit `6f369a7`.

| | |
|---|---|
| Datensatz | `C:\Users\Daniel\AppData\Local\NightreignHelper\nightreign_data.json`, `data_version` **10350000**, 8 387 819 Bytes |
| Spielstand | der des Nutzers, **nur lesend** ueber `inventory.load`, **312** Kopien |
| Grundgesamtheit | **210** Kandidaten an einem freien **weissen** Slot, nichts gehalten, Grundzustand leer |
| Nightfarer | Wylder, Level **15** (`advisor_cases.LEVEL`) |
| Weg | `candidates.pool(...)` ueber die echte Registry, `types.marginal_for`. **Kein Programmstart, kein Planner, kein Fenster** — deshalb auch keine Umlenkung noetig; `NIGHTREIGN_SETTINGS_ORG`/`_APP` standen trotzdem auf `DankYeeterT-191` / `NightreignHelperT-191`. Kein Schreibzugriff |
| "unterscheidbar" | `abs(grenzbeitrag) > 1e-9`, die Schranke aus AD-032 unveraendert uebernommen — eine Gleitkomma-Null, kein Sicherheitsabstand |
| Lesart | **Kopien**, nicht Relikt-Arten, nicht Effekt-Ids |

Ausgabe, Zeile fuer Zeile gegen AD-032:

| Grundlage | gemessen | AD-032 sagt | verschiedene Werte | groesste Gleichstandsgruppe |
|---|---|---|---|---|
| `max_damage` (A) | **26** / 210 | 26 | 8 (8) | 184 (184) |
| `max_attributes` (C) | **53** / 210 | 53 | 8 (8) | 157 (157) |
| `min_damage_taken` | **37** / 210 | 37 | 10 (10) | 173 (173) |
| **A oder C** | **75** / 210 | **75** | — | — |
| A oder C oder Ueberleben | **104** / 210 | 104 | — | — |

**Kein Befund. Jede der acht Zahlen stimmt.**

**Der Katalysator-Einwand traegt hier nicht, geprueft statt angenommen.**
Der A+C-Weg ruft `weapons.rate` nie: `_max_damage` nimmt bei
`reference is None` nur `build.rates`, `_max_attributes` nur
`build.attributes`, `_min_damage_taken` nur `build.derived`. Beleg statt
Argument: alle **210** Kopien wurden ohne eine einzige Ausnahme gemessen. Es
bleibt **keine Klasse ungemessen**. Nicht gemessen habe ich die **102
Deep-Kopien** — die lagen auch bei T-189 ausserhalb der Grundgesamtheit.

Nebenbefund derselben Messung: die Attribute, auf die Armaturen dieses
Datensatzes skalieren, sind **genau** `Arcane, Dexterity, Faith,
Intelligence, Strength` — identisch mit `OFFENSIVE_ATTRIBUTES`. Das ist jetzt
ein Test (`test_the_offensive_attributes_are_the_ones_armaments_scale_on`)
und nicht mehr eine Annahme; er faellt an dem Tag, an dem eine sechste
Statistik einen Skalierungskoeffizienten bekommt, und er faengt zugleich
jeden Tippfehler in der Liste ab (`attributes.get("Strenght", 0)` ist 0 und
summiert sich fehlerfrei).

## 3. Rot vorher — welche Aenderung welchen Test bricht

Zwei Schutzmassnahmen, **einzeln** deaktiviert (Datei vorher mit `cp` zur
Seite kopiert, danach zurueckkopiert — kein `git checkout`):

**(a) Die Rollen zurueck in den Kontext** (`asking_from` fuellt
`armament_effect_ids` wieder):
`tests/test_advisor_goals.py::test_the_ranking_does_not_depend_on_the_rolls_on_the_armament`
**faellt**, mit dem Mechanismus in der Meldung:

```
At index 0 diff: (('max_damage', 1.0200000047683715), ...)
              != (('max_damage', 1.0210000038146974), ...)
```

**(b) Die Armaturen zurueck in die Anfrage** (`armaments=armaments`):
`tests/test_advisor_goals.py::test_the_cache_key_does_not_know_the_armament_or_its_rolls`
**faellt**:

```
armaments: (ArmamentRef(weapon_id=1000000, tier=1, effect_ids=(8850550,)),)
        != (ArmamentRef(weapon_id=2000000, tier=1, effect_ids=(6001400,)),)
```

Beide Male ist es eine echte Verhaltensaenderung und keine
Schnittstellenverschiebung: die Signaturen bleiben, nur die Werte wandern.

**Der Gegenbau, der im Standardlauf beisst** (L-008): der Test
`test_the_rolls_on_the_armament_moved_the_ranking_before_ad_032` stellt
`armament_effect_ids` von Hand wieder her und behauptet, dass die
**Reihenfolge** (Name + Handle, nicht nur die Zahlen) dann auseinanderlaeuft.
Er ist gruen — der Bestand und die beiden Rollen koennen die zwei Laeufe also
wirklich unterscheiden, und die Invarianz oben ist nicht deshalb gruen, weil
nichts im Fall etwas sieht. Er laeuft im Standardlauf, seine Erwartung kommt
nicht aus der bewachten Stelle, und er hat keinen Skip.

**Die Stichprobe ist eine der sechs aus QA-226:** gewaehlt wird sie gemessen
(`advisor_cases.a_non_stacking_effect`, ueber `model.compute` einmal und
zweimal angewandt), nicht per Id festgenagelt; auf diesem Datensatz ist es
**8850550 `Physical Attack Up`, `stacks=False`** — genau einer der beiden,
die T-189 mit "Reihenfolge weicht ab Rang 3 ab" gemessen hat.

## 4. Was ich bewusst **nicht** gebaut habe

**Die neue Richtung steht in keinem Bedienelement.** `advisorbar.GOAL_ORDER`
ist unveraendert, `relicpicker.VALUE_DIRECTIONS` zieht davon ab. Der Waechter
W4 verlangt nur `GOAL_ORDER ⊆ GOALS`, also haelt alles. Ein dritter Eintrag
waere kein Einzeiler:

* `relicpicker.py:1205` `other_id = next(g for g in VALUE_DIRECTIONS if g != goal_id)`
  setzt **genau zwei** Richtungen voraus und wird mit drei mehrdeutig;
* eine Karte zeichnet zwei Wertespalten (`VALUE_CAPTIONS`, `show_values`);
* AK-43 und AK-205 sagen, welche Eintraege das `Sort by` fuehrt, und
  `UI_SPEC.md` braucht neue AK fuer Beschriftung und Einheit.

Das ist Oberflaeche und gehoert dem `ui-ux-designer` — und es ist A17 Teil 2,
den der Auftrag ausdruecklich ausgeschlossen hat. Ein Test haelt den Zustand
fest, damit er eine ausgesprochene Entscheidung bleibt und nicht etwas, das
jemand beim Oeffnen des Fensters bemerkt:
`test_the_third_direction_is_scored_but_not_yet_offered`.

**Folge, die der `director` kennen muss:** fuer den Spieler aendert sich
heute **nichts**. Die Zahl wird gerechnet, gecacht und nicht gezeigt. Die 75
von 210 sind erst dann auf dem Bildschirm, wenn Teil 2 gebaut ist.

**Keine Texte geaendert** (Vorgabe 4). Insbesondere steht
`MAX_DAMAGE.blurb` unveraendert auf *"Ranks by attack multipliers, attributes
and passives — what stays fixed between runs."* — AD-032 nennt diesen Satz
selbst als nachzuziehen, aber er gehoert zu AK-190/192/193.

## 5. Befund: die Dateigrenze des Auftrags traegt Vorgabe 3 nicht

Geplant waren fuenf Dateien. Es sind **elf** geworden. Die sechs zusaetzlichen
sind **keine** Bequemlichkeit — jede einzelne war ein Waechter, der durch die
beauftragte Aenderung rot geworden ist:

| Datei | warum erzwungen | Umfang |
|---|---|---|
| `tests/test_exception_text_is_english.py` | `STILL_QUOTING` fuehrt die worker-Zeile; `test_the_list_of_the_ones_left_is_still_true` faellt, wenn die Stelle repariert und der Eintrag stehen bleibt. Der Docstring des Waechters sagt selbst, dass das Streichen zur Reparatur gehoert | 1 Eintrag, 1 Kommentarzeile |
| `tests/test_advisor_worker.py` | behauptete `"the dataset lost a curve" in seen.failed[0]` — genau den Rohtext, der nicht mehr ankommen darf | 1 Fall geschaerft |
| `tests/test_picker_track_guards.py` | dasselbe an der Picker-Ueberschrift | 1 Erwartung |
| `nrplanner/relicpicker.py` | **Regression, die ich sonst eingebaut haette:** `could_not_work_out` setzt den Punkt hinter den Grund, `errortext`-Saetze bringen einen mit — die Ueberschrift las `"… (ValueError).. They are in name order below."`. `advisorbar` macht an seiner Senke seit jeher `reason.rstrip(". ")`; ich habe dieselbe Zeile in die eine komponierende Funktion gesetzt | 1 Zeile + Docstring |
| `scripts/differential/mutate.py` | die Mutation `a-run-that-raises-says-nothing` zitiert die alte Zeile woertlich; `test_every_mutation_still_finds_its_anchor_in_the_real_source` faellt sonst | 1 Zeile |
| `tests/test_advisor_run.py` | Nennerwaechter: `assert set(goals.GOALS) == {DAMAGE, SURVIVAL}`. **Er hat seine Arbeit getan** — die Cache-Parametrisierung deckte weiter zwei Richtungen ab und der Waechter hat es gesagt. Jetzt sechs Kombinationen, Testname nachgezogen | Parametrisierung + 1 Nenner |

Fuenf der sechs haengen an Vorgabe 3, eine an der dritten Richtung.

**Zur Entscheidung des `director`:** ich habe zu Ende gebaut, weil die
Alternative — Vorgabe 3 zurueckbauen — den Auftrag verletzt haette, und
"drei rote Tests liegenlassen" keine ist. Wer die Grenze naechstes Mal setzt,
sollte die Waechter mitzaehlen: in diesem Projekt haengt an einer Zeile
Anzeigetext regelmaessig ein AST-Waechter, eine Mutation und zwei Fallakten.

## 6. Tests

Neu in `tests/test_advisor_goals.py`:

* `test_the_offensive_attributes_are_the_ones_armaments_scale_on` — die fuenf
  gegen den Datensatz (und gegen Tippfehler);
* `test_the_attribute_goal_counts_the_points_and_not_a_conversion` — als
  **Gleichung**, damit kein spaeteres Gewicht durchrutscht;
* `test_the_attribute_goal_rises_with_the_points_a_relic_brings`;
* `test_the_attribute_goal_leaves_the_other_three_attributes_alone` — Vigor
  bewegt die Attributszahl nicht und die Ueberlebenszahl schon;
* `test_the_attribute_points_are_not_a_summand_of_the_damage_figure` — genau
  die "Reparatur", die T-189 dem `developer` verboten hat;
* `test_the_third_direction_is_scored_but_not_yet_offered`;
* `test_the_ranking_does_not_depend_on_the_rolls_on_the_armament` — AK-191
  woertlich, ueber **jede** Richtung, ganze Antwort verglichen;
* `test_the_rolls_on_the_armament_moved_the_ranking_before_ad_032` — der
  Gegenbau dazu, auf die **Reihenfolge**;
* `test_the_cache_key_does_not_know_the_armament_or_its_rolls` — P-1.

Geschaerft: `test_a_run_that_raises_is_a_signal_and_not_a_silence` prueft
jetzt beide Richtungen (der Rohtext ist **weg**, der gemappte Satz ist da).

**Nicht abgedeckt, ausdruecklich:** die 102 Deep-Kopien unter der neuen
Richtung; wie die Nullen im Picker **aussehen** (kein Programmstart); die
neue Richtung im Bedienelement (gibt es nicht).

## 7. Suitelauf

```
python -m pytest -q --ignore=tests/test_extraction.py --ignore=tests/test_hostile_gamedata.py
1728 passed, 1 failed, 9 skipped in 563.32s (0:09:23)
```

Gegen T-190s **1712 / 1 / 9**: **+16 bestanden**, gleiche eine Fehlschlagende,
gleiche neun uebersprungene. Die 16 sind vollstaendig erklaerbar — 9 neue
Faelle, +5 aus den fuenf ueber `sorted(goals.GOALS)` parametrisierten Faellen
in `test_advisor_goals.py`, +2 aus der Cache-Parametrisierung (vier → sechs
Kombinationen). **Kein Test entfernt, keiner deaktiviert, keiner uebersprungen
worden, der es vorher nicht war.**

Der eine Fehlschlag ist **QA-224**
(`test_first_run_panel.py::test_the_first_dialog_opens_at_the_folder_that_was_remembered`,
`where_to_start_looking(None)` liefert `d:/steam/steamapps/common`, die echte
Steam-Installation dieses Rechners). Die Datei habe ich nicht angefasst, und
derselbe Fall fiel schon in meinem ersten Volllauf.

**Datenbedingung:** echter Datenabzug `data_version` 10350000 unter
`%LOCALAPPDATA%`, echter Spielstand (312 Kopien) vorhanden, Spielinstallation
vorhanden, Programm **nicht** gestartet, ohne `-n` (kein `pytest-xdist`),
`texture2ddecoder` fehlt — daher die beiden `--ignore`. **Nichts
nachinstalliert.**

Zwischenlaeufe: `tests/test_advisor_goals.py test_advisor_worker.py
test_exception_text_is_english.py test_advisor_bar.py
test_advisor_candidates.py` → `148 passed in 57.72s`;
`test_advisor_run.py test_picker_track_guards.py test_differential_track.py`
→ `410 passed in 67.23s`.

## 8. L-006 — die Eigenschaft, nicht die Fundstelle

Der A8-Waechter selbst ist die primaere Suche (AST ueber `nrplanner/` und
`nrdata/`). Zwei unabhaengig formulierte Gegenproben:

* `grep -rn "emit(str(\|setText(str(\|showMessage(str(\|reason=str(" nrplanner/ nrdata/`
  → **2 Treffer**, beide `setText(str(<int>))` (`app.py:289`, `app.py:4841`),
  keine Ausnahme;
* `grep -rn "except .* as \(err\|error\|e\)\b" nrplanner/ nrdata/` → **0
  Treffer**; es gibt keine Senke, die sich hinter einem anderen
  Variablennamen als `exc` versteckt und am AST-Waechter vorbeikaeme.

Offen bleiben die **vier** bekannten Stellen aus `STILL_QUOTING`
(`app.py::main`, `inventory.py::_scan_save` zweimal,
`nrdata/extract.py::_bosses`, `nrdata/icons.py::read_subtextures`) — alle mit
ihrer Begruendung in der Liste, alle ausserhalb dieses Auftrags.

## 9. Befunde und Meldungen

**An den `director`:**

1. **Die Dateigrenze hat nicht getragen** (Abschnitt 5). Elf statt fuenf
   Dateien, sechs davon von Waechtern erzwungen.
2. **QA-227 ist um ein Feld gewachsen, und ich habe es nicht angefasst.**
   `tests/advisor_cases.context_from_planner` fuellt nach wie vor
   `reference`, `weapons_held` **und `armament_effect_ids`** — der
   Checkpoint-13-Waechter bewacht damit jetzt in **drei** Feldern eine
   Aussage, die fuer den Programmweg nicht mehr stimmt, statt in zweien. Der
   Auftrag hat QA-227 ausdruecklich ausgeschlossen; das ist die Meldung
   dazu, die er verlangt hat.
3. **Der dritte Eintrag im `Sort by` ist eine offene Entscheidung**
   (Abschnitt 4) und braucht `ui-ux-designer` plus `UI_SPEC`-AK. Bis dahin
   sieht der Spieler von A+C nichts. Das ist die Zeile fuer `docs/state.md`.
4. **`MAX_DAMAGE.blurb` und `GOAL.md` A17 behaupten weiter "Attribute und
   Passive"** fuer eine Zahl, die das nicht tut. Gehoert zu
   AK-190/192/193.
5. **D-1 aus T-188 besteht fort:** der Armatur-Zweig in `_max_damage` ist vom
   Programm weiterhin unerreichbar (nur Tests und kuenftig A16 rufen ihn).
   AD-032 Option A+C hat das bestaetigt, nicht aufgeloest.
6. **Vorschlag, keine Handlung:** das Messskript `measure_ac.py` liegt im
   Scratchpad und ueberlebt die Sitzung nicht. Wenn die 75 je wieder
   nachweisbar sein soll, gehoert es versioniert unter `scripts/` — das ist
   ein eigener Auftrag, kein Nebenbei.

**An den `qa-engineer`:**

* **Zu testen:** dass zwei Laeufe mit verschiedenen gefuehrten Armaturen
  **und verschiedenen Rollen** dieselbe Liste liefern — jetzt auch am
  laufenden Programm, nicht nur ueber `asking_from`. Sechs nicht stapelbare
  Effekte kommen dafuer in Frage (QA-226); `8850550 Physical Attack Up` ist
  der, den mein Test nimmt.
* **Kantenfall Cache:** Waffe wechseln, Optimize erneut — es darf **kein**
  zweiter Lauf starten, wo frueher einer startete (P-1). Sichtbar an der
  Wartezeile 4.2/4.3.
* **Kantenfall 4.12 / AK-208:** ein Lauf, der scheitert, sagt jetzt einen
  Satz aus `errortext` statt der Worte der Ausnahme. Bitte im Beraterstreifen
  **und** in der Picker-Ueberschrift ansehen — dort war der doppelte Punkt,
  den ich behoben habe; in `SEARCH_WAS_STOPPED` ("the search was stopped")
  darf sich nichts geaendert haben.
* **Nicht geprueft von mir:** Deep-Kopien unter der neuen Richtung; das
  Aussehen der 184 Nullen; alles am laufenden Fenster.

**An den `ui-ux-designer`:**

* **Arbeitstitel, bitte bestaetigen oder ersetzen:** Label *"Maximise
  offensive attributes"*, Blurb *"Ranks by the attribute points a relic
  brings — the part of a build no expedition rerolls."*, Einheit `pts`
  (aus AD-032), Anzeige *"Offensive attributes 23"*. Der Label-Wortlaut ist
  bewusst laenger als "Maximise attributes": die Richtung zaehlt Vigor, Mind
  und Endurance **nicht**, und der kuerzere Name verspricht mehr, als sie
  haelt. `SORT_BOX_WIDTH` ist 220 px — ob der Titel dort hineinpasst, habe
  ich **nicht** gemessen.
* **Der dritte Eintrag ist nicht gesetzt** (Abschnitt 4) — mit ihm kommen
  eine dritte Wertespalte auf der Karte und `relicpicker.py:1205`, das genau
  zwei Richtungen annimmt.

**Sicherheitsfunde:** keine.

**Performance:** nichts Auffaelliges gemessen; der Pool von 210 Kandidaten
laeuft mit drei statt zwei Richtungen unauffaellig (die dritte Zahl ist zwei
Woerterbuchzugriffe auf einen bereits gerechneten Build). Kein Auftrag an den
`performance-tuner` noetig. **Dagegen gerechnet, nicht gemessen:** ich habe
keine Zeitzahl je Lauf genommen.

## 10. Aufgeraeumt

Kein Programmstart, kein Server, kein Fenster. Zwei `python`-Prozesse meiner
Messung: der erste haengte in einer Endlosschleife meines eigenen Skripts
(Suche nach dem Arbeitsbaum ueber `Path.parent` aus dem Scratchpad heraus —
oberhalb der Wurzel bleibt `parent` stehen) und ist beendet; geprueft mit
`Get-CimInstance Win32_Process`, es laeuft **kein** Prozess von mir mehr. Die
zwei verbleibenden `python.exe` gehoeren einem anderen Projekt
(`ApplicationHelper`) und sind nicht meine. Kein Klon angelegt — die
Vergleichszahl 1712/1/9 stand im Auftrag. Der Arbeitsbaum ist sauber,
`git status` leer.
