# T-188 — A17, Teil 1: die Rangfolge haengt an keiner gefuehrten Waffe (developer)

```
STATUS: erledigt
AUFTRAG: T-188 — A17, Teil 1: die Rangfolge haengt an keiner gefuehrten Waffe
GELESEN: docs/tasks/T-188.md, CLAUDE.md, GOAL.md (A17, Abschnitt 285-315),
         nrplanner/advisor/goals.py, nrplanner/advisor/types.py,
         nrplanner/advisor/evaluate.py, nrplanner/advisor/candidates.py,
         nrplanner/advisor/run.py, nrplanner/advisor/explain.py (nur lesend),
         nrplanner/advisorbar.py, nrplanner/model.py, nrplanner/damage.py,
         nrplanner/app.py (Planner._rebuild, equipped_weapons),
         tests/conftest.py, tests/advisor_cases.py, tests/test_advisor_goals.py,
         tests/test_advisor_evaluate.py, tests/test_relic_picker_advisor.py,
         scripts/differential/mutate.py (Eintraege zu advisorbar.py),
         requirements.txt, requirements-dev.txt, .github/workflows/tests.yml
GEAENDERT: nrplanner/advisorbar.py, nrplanner/advisor/goals.py,
           tests/test_advisor_goals.py — committet als 43fd992 auf
           docs/audit-and-advisor-design, Arbeitsbaum danach sauber.
           docs/berichte/T-188-developer.md — geschrieben, aber **nicht
           committet** (der Bericht ist kein Code; frueher hat der archivist
           die Berichte abgelegt). Liegt als einzige Aenderung uncommittet da.
ANNAHMEN: 1) "Voreinstellung" heisst: der Programmpfad. Der Waffenzweig in
          `_max_damage` bleibt stehen, weil der Auftrag nur einen Test zum
          Umschreiben nennt und A16 ihn wieder brauchen wird — er ist damit
          aus `nrplanner/` heraus unerreichbar (siehe Debt D-1).
          2) `armament_effect_ids` bleiben im Kontext. Der Auftrag nennt nur
          Bezugswaffe und `weapons_held`; die gewuerfelten Buffs der Armaturen
          sind eine offene Entscheidung (siehe Frage F-1).
          3) Der Regressionstest liegt in tests/test_advisor_goals.py, nicht
          in tests/test_relic_picker_advisor.py: dort steht die Kartendarstel-
          lung gegen gestellte Pools, kein Pfad durch `asking_from`.
NAECHSTER: director (Entscheidungen F-1 und F-2), danach Teil 2 (AK-190/192/193)
BLOCKIERT DURCH: nichts
```

## Umgesetzt

**`nrplanner/advisorbar.py`, `asking_from`** — der Kontext bekommt weder
`reference` noch `weapons_held`, und `reference_weapon_id` des Cache-Keys
bleibt leer (sonst weist `run._check` die Anfrage zurueck, weil Schluessel und
Kontext sich widersprechen). Die Begruendung steht im Docstring, samt der
Messung und samt dem Satz, dass der Build des Beraters damit **nicht mehr**
der Build des Statblatts ist.

**`nrplanner/advisor/goals.py`** — Blurb von `Ranks by what your reference
armament hits for.` auf `Ranks by attack multipliers, attributes and
passives — what stays fixed between runs.`; die Docstrings von `_max_damage`
und `_attack_multiplier_mean` sagen jetzt, welcher Zweig der Programmpfad ist.
**Keine Textkonstante angefasst** (`_NO_ARMAMENT`, `_NO_ARMAMENT_NOTE`
unveraendert — AK-190, Teil 2).

**`tests/test_advisor_goals.py`** —
`test_without_an_armament_the_damage_goal_says_so` umgeschrieben zu
`test_without_an_armament_the_damage_goal_still_orders_two_builds`: prueft die
Rangfolge zweier Builds, keine Wortlaute mehr.
Neu: `test_the_ranking_does_not_depend_on_the_armament_held` (AK-191, beide
Zielrichtungen, ueber `advisorbar.asking_from` und `candidates.pool`) und
`test_the_armament_moved_the_ranking_before_a17` (der Gegenfall).
Neue Helfer: `armament_gates`, `an_inventory_telling_two_armaments_apart`,
`ranking_with`, Konstante `AR_RATE_FIELDS`.

## Rot-vorher, mit Ausgabe

Reihenfolge der Arbeit: erst die Tests geschrieben, dann gemessen, dann die
Quelle geaendert. Alle Laeufe `pytest tests/test_advisor_goals.py` (ohne `-n`,
wie CLAUDE.md es fuer eine einzeln genannte Datei verlangt).

**Vor der Aenderung** (Quelle unveraendert, nur die Tests neu):

```
FAILED tests/test_advisor_goals.py::test_the_ranking_does_not_depend_on_the_armament_held
1 failed, 26 passed in 51.21s

E  AssertionError: ranked by max_damage, swapping the armament in the slot
   moved the answer: the run is still asked about what the player happens to
   be carrying (AK-191)
E  At index 0 diff: (('max_damage', 39.769439999999996), ('min_damage_taken', 240.0))
                != (('max_damage', 49.56), ('min_damage_taken', 240.0))
```

**Nach der Aenderung:** `27 passed in 47.22s`.

**Jede Schutzmassnahme einzeln abgeschaltet** (L-007). Die Datei wurde vorher
mit `cp` zur Seite kopiert und danach zurueckkopiert, nie `git checkout`:

| abgeschaltet | Ergebnis |
|---|---|
| `weapons_held` wieder in den Kontext, `reference` weiter `None` | `1 failed, 26 passed in 37.12s` — `test_the_ranking_does_not_depend_on_the_armament_held` |
| `reference` wieder in den Kontext, `weapons_held` weiter weg | `1 failed, 26 passed in 37.62s` — derselbe Test |

Beide Haelften sind also einzeln noetig, und der Test sieht beide. `git status`
nach dem Zurueckkopieren: leer, `git diff HEAD`: leer.

**Was den Test nicht leer laufen laesst:** `test_the_armament_moved_the_ranking_
before_a17` baut denselben Bestand unter dem Kontext von **vor** A17 und
verlangt, dass die Rangfolge sich dort unterscheidet. Wuerde jemand
`_max_damage` auf eine Konstante setzen, waere der AK-191-Test gruen und
dieser Gegenfall rot. Das Paar ist die Pruefung, nicht der einzelne Fall.

## Messungen

Alle drei Skripte liegen in
`…/scratchpad/T-188/` (`measure_ak191.py`, `measure_save.py`,
`measure_grid_only.py`). Sie bauen **keinen** `Planner`, lesen den Spielstand
ueber `inventory.load` nur lesend und setzen `NIGHTREIGN_SETTINGS_ORG` /
`NIGHTREIGN_SETTINGS_APP` auf eigene Werte. Rezept fuer alle Zahlen unten:
Wylder, Probe-Level aus `advisor_cases.LEVEL`, ein weisser Slot (zieht jede
Farbe), Greatsword (`wep_type` 5) gegen Bogen (`wep_type` 51), Datenstand
`nightreign_data.json` aus `%LOCALAPPDATA%\NightreignHelper`, gemessen
2026-09-12.

**Der Rot-vorher-Satz des Auftrags reproduziert.** Bezugswaffe weggelassen,
`weapons_held` gefuellt:

| Pool | Kandidaten | Kopien, deren Zahl sich aendert | Rangfolge unterscheidet sich ab |
|---|---|---|---|
| gewoehnlich | 210 | 1 — `Grand Luminous Scene` (0,0000 mit Greatsword, **+0,0600** mit Bogen) | Rang 3 |
| Deep | 102 | 1 — `Deep Polished Drizzly Scene` (**+0,0900** mit Greatsword, 0,0000 mit Bogen) | Rang 0 |

Zusammen **2 Kopien**, beide mit genau den Zahlen des Auftrags. Der Auftrag
sagt "2 von 309" und "ab Rang 0" — beides stimmt in der Sache; praezisiert:
`inventory.load` zaehlt heute **312** Kopien, die 2 verteilen sich auf zwei
getrennte Pools, und "ab Rang 0" gilt fuer den Deep-Pool.

**Nach der Aenderung:** in beiden Pools 0 Kopien, die ihre Zahl aendern; die
Reihenfolge ist identisch (`order differs from rank: None`).

## DoD

- [x] Anforderung verstanden, Annahmen oben.
- [x] Neue Logik hat Tests; rote Phase mit Ausgabe belegt, jede Haelfte des
      Fixes einzeln als toetend nachgewiesen.
- [~] **Build & Tests gruen — mit zwei Einschraenkungen dieser Maschine**,
      siehe U-1 und U-2 unten. Gemessen:
      `pytest -q --ignore=tests/test_extraction.py --ignore=tests/test_hostile_gamedata.py`
      → **1697 passed, 1 failed, 9 skipped in 451,55 s**.
      **Datenbedingung:** ohne Testabzug, ohne Umlenkung von `LOCALAPPDATA` /
      `APPDATA` — der dokumentierte Testbefehl, also gegen den echten
      Datenabzug (`%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`) und
      den echten Spielstand (nur lesend, 312 Relikte). Das Programm wurde
      **nicht** gestartet; es gab keine Schreibzugriffe ausserhalb des von
      `conftest.py` umgelenkten Einstellungsspeichers.
- [x] Linter: **entfaellt** — dieses Projekt konfiguriert keinen (kein
      `.flake8`, `ruff.toml`, `setup.cfg`, `tox.ini`; `.github/workflows/`
      ruft nur `pytest`).
- [x] Keine Secrets, keine TODOs, kein toter Code **neu** erzeugt (zu vorhan-
      denem: D-1).
- [x] Selbst durchgespielt: AK-191 in beiden Zielrichtungen, ueber den echten
      Bestand und ueber einen gestellten.
- [x] Bericht geschrieben, Commit 43fd992 mit Pfadangabe hinter `--`.

**Ungeprueft:** Linux, macOS (kein Ziel). Die Oberflaeche selbst wurde nicht
angesehen — ich habe kein Fenster geoeffnet; was der Berater-Streifen und die
Relikt-Karte mit den neuen Zahlen **anzeigen**, ist ungeprueft und gehoert zu
Teil 2 und zur QA.

## An den director

### U-1 — diese Python-Umgebung entspricht nicht requirements-dev.txt

`pip show`: **`pytest-xdist` und `texture2ddecoder` sind nicht installiert**,
obwohl beide in `requirements-dev.txt` / `requirements.txt` gepinnt stehen
(3.8.0 bzw. 1.0.6). Folgen:

* `pytest -n auto` bricht mit `unrecognized arguments: -n` ab. Die Suite lief
  seriell in 451 s.
* `tests/test_extraction.py` und `tests/test_hostile_gamedata.py` sind **nicht
  einsammelbar** (`ModuleNotFoundError: No module named 'texture2ddecoder'`
  beim Import) — ohne `--ignore` bricht der ganze Lauf beim Einsammeln ab:
  `2 errors in 2.09s`.

Ich habe **nichts installiert** (keine Abhaengigkeit ohne Freigabe). Damit ist
die Auftragsschranke **1703 passed, 9 skipped, 0 failed** auf dieser Maschine
nicht erreichbar, und meine Zahl ist mit ihr nicht direkt vergleichbar.
Entscheidung noetig: Nachinstallieren der beiden gepinnten Pakete, oder die
Schranke bekommt ihre Umgebungsangabe.

### U-2 — ein Fehlschlag, der nicht von mir kommt

`tests/test_first_run_panel.py::test_the_first_dialog_opens_at_the_folder_that_was_remembered`

```
E  AssertionError: assert WindowsPath('d:/steam/steamapps/common')
   in (None, WindowsPath('C:/Program Files (x86)/Steam/steamapps/common'))
```

Nachgewiesen auf einem **frischen Klon des HEAD** (`git clone` des lokalen
Repos in den Scratchpad, Stand `ef0d130`, ohne meine Aenderung):
`1 failed, 63 passed in 2.07s` — derselbe Fehlschlag. Der Test haengt daran,
wo auf dieser Maschine ein Spielordner gemerkt ist (`d:/steam/…`), nicht an
T-188. Der Klon ist geloescht.

### F-1 — Entscheidung noetig: die gewuerfelten Buffs der Armaturen

Der Nutzerentscheid sagt woertlich "waffen **und deren buffs** sind alle in der
runde RNG-basiert". Der Kontext traegt weiterhin `armament_effect_ids`
(`advisorbar.py`, aus `slot.effect_ids` jeder gefuellten Armatur), und die
gehen ueber `evaluate._effects` in jeden Build. Wer die Armatur wechselt,
wechselt in der Regel auch deren Rollen — dann aendern sich Zahlen und
Rangfolge wieder, und AK-191 waere woertlich gelesen **nicht** erfuellt.

Mein Test sieht das **nicht**: die beiden Armaturen im Fall tragen keine
gewuerfelten Effekte. Das ist eine Luecke, kein Beleg.

Ich habe es bewusst nicht mitgeaendert (Auftrag nennt nur Bezugswaffe und
`weapons_held`; "nur der erteilte Auftrag"). Optionen:
**(a)** `armament_effect_ids` ebenfalls weglassen — konsequent zum
Nutzerentscheid, aber der Berater rechnet dann auch die Passiven der Waffen
nicht mehr mit, was weitere Zahlen bewegt und Teil 2 beruehrt;
**(b)** so lassen und in `Goal.scope` benennen (A12);
**(c)** eigener Auftrag nach Teil 2.
Ich empfehle **(c)** mit Vorentscheid des `architect`, weil es dieselbe Frage
ist wie F-2 und beide zusammen beantwortet gehoeren.

### F-2 — A17 verspricht Attribute, die Zahl kennt sie nicht (wichtigster Fund)

`GOAL.md` A17: *"rankt … nach Angriffsmultiplikatoren, **Attributen** und
Passiven"*. Der gebaute Zweig `_attack_multiplier_mean` mittelt **nur** die
fuenf Angriffsmultiplikatoren aus `damage.AR_RATE_FOR`. Attributsboni bewegen
ihn um exakt 0 — der Docstring sagt das seit jeher ("without an armament there
is no scaling for them to feed"), aber A17 verspricht das Gegenteil.

Gemessen (Rezept wie oben, gewoehnlicher Pool, 210 Kandidaten):

| Kontext | Kopien mit einer Zahl ungleich 0 unter "Maximise damage" |
|---|---|
| vor der Aenderung (Greatsword als Bezugswaffe) | **59 von 210** |
| nach der Aenderung | **26 von 210** |

**184 von 210 Kopien stehen jetzt auf exakt 0,0000** und werden nur noch nach
Name und Handle sortiert; ein reines Staerke-Relikt gewinnt nichts. Die
Richtung "Schaden maximieren" ist damit fuer den groessten Teil des Bestands
keine Rangfolge mehr.

AK-191 ist davon unberuehrt und erfuellt — aber das Abnahmekriterium des
Zielbilds A17 ist es nicht. Das ist ein Spezifikationsfehler bzw. eine fehlende
Architekturentscheidung: **wie ist ein Attributsbonus ohne Waffe zu bewerten?**
(z. B. gegen eine feste Referenz-Skalierung, oder ueber `damage.candidate` mit
einer neutralen Armatur). Das ist Sache des `architect`, nicht meine, und es
sollte **vor** Teil 2 entschieden werden: die Texte von AK-190/192/193
beschreiben sonst eine Zahl, die gleich wieder wechselt.

### D-1 — Debt: der Waffenzweig in `_max_damage` ist aus `nrplanner/` unerreichbar

`advisorbar.asking_from` ist die einzige Stelle in `nrplanner/`, die einen
`GoalContext` baut (Volltextsuche, s. u.), und sie uebergibt jetzt immer
`reference=None`. Damit ist `goals.py` Zeile 231 (`damage.equipped`) im
Programm nicht mehr erreichbar; am Leben halten ihn nur Tests. Nach dem
Massstab dieses Projekts (QA-061: "a branch no data can reach is dead code")
ist das Debt. Ich habe ihn **stehen gelassen** — er traegt das Wissen aus
QA-101/AD-020, und A16 (schlechtester/bester Fall) wird genau diese Frage
wieder stellen. Im Docstring steht jetzt, dass er unerreichbar ist.
Aufwand zum Entfernen: klein im Code, aber es faellt damit
`test_the_damage_goal_charges_the_starting_armament_penalty` und
`test_the_damage_goal_ranks_a_self_inflicted_penalty_below`. Risiko des
Stehenlassens: ein Leser haelt ihn fuer den Normalfall.

### D-2 — Debt: `tests/advisor_cases.context_from_planner` ist eine zweite Fassung von `asking_from`

`tests/advisor_cases.py:379-406` baut den Kontext selbst und fuellt
`reference` und `weapons_held` weiter aus dem Fenster. Dadurch bleibt
`tests/test_advisor_evaluate.py::test_the_advisor_computes_the_build_the_window_shows`
(Checkpoint 13, QA-001: "der Berater rechnet den Build, den das Fenster zeigt")
**gruen, obwohl die Aussage fuer den Programmpfad nicht mehr stimmt** — der
Berater rechnet seit A17 bewusst einen anderen Build als das Statblatt. Die
Datei gehoert nicht zu meinem Umfang, und die Aenderung ist keine Zeile,
sondern eine Entscheidung: entweder der Waechter zieht auf `asking_from` um,
oder er wird ausdruecklich auf "dieselbe Rechnung bei gleichen Eingaben"
umformuliert. **Fuer den `qa-engineer` ist das der gefaehrlichste Punkt dieses
Zyklus**, weil der Waechter nach der Aenderung genau so gruen aussieht wie
vorher.

### P-1 — Performance (nicht selbst angefasst)

`AdvisorRequest.armaments` traegt weiter `weapon_id` und `tier` jeder Armatur
und ist Teil des Cache-Keys. Wechselt der Spieler die Waffe, faellt der
Treffer aus, obwohl die Antwort jetzt bitgleich dieselbe ist. Empfehlung:
`performance-tuner` beauftragen, **nachdem** F-1 entschieden ist — solange
`armament_effect_ids` drin bleiben, ist der Key nicht einfach kuerzbar.

### Teil 2 — was dort auf dem Tisch liegt (nicht angefasst)

`nrplanner/advisor/explain.py:363-366` (`_armaments`) liest erst
`ctx.weapons_held`, dann `ctx.reference`. Beide sind jetzt leer, also ist die
Menge der gefuehrten Waffentypen **immer** leer, und jeder waffentyp-gesperrte
Effekt bekommt die Zeile "es haengt an den Armaturen, die du fuehrst". `GOAL.md`
fuehrt genau diese Zeile unter A17 bereits als offen ("Fuellung (c), 38 Zeilen")
— sie wird jetzt haeufiger, nicht seltener. Gehoert in den S10-Review.

## Eigenschaft statt Fundstelle (L-006)

Drei unabhaengig formulierte Volltextsuchen ueber den ganzen Baum, nach dem
Muster "eine Armatur erreicht einen Beraterlauf":

| Maske | Treffer gesamt | in `nrplanner/` |
|---|---|---|
| `GoalContext(` | 12 | **1** — `advisorbar.py` (behoben). Sonst 5 in `scripts/measure_advisor_*.py`, 6 in `tests/` |
| `weapons_held=` | 24 | **2** — `advisor/evaluate.py:120` (gibt das Kontextfeld weiter, jetzt immer leer) und `app.py:4800` (Statblatt, **muss** bleiben) |
| `ReferenceArmament(` | 12 | **0** |

Bewusst nicht mitbehoben: die fuenf Messskripte unter `scripts/` bauen ihren
Kontext weiter mit `weapons_held=(starting,)`. Sie messen Laufzeit, nicht
Rangfolge, und `scripts/` liegt ausserhalb meines Umfangs — gemeldet, nicht
angefasst.

## An den qa-engineer

* **Zu testen:** Berater-Streifen und Relikt-Karte mit einer Waffe im aktiven
  Slot gegen eine andere Waffe — Reihenfolge und Zahlen muessen identisch sein,
  in **beiden** Richtungen des Auswahlfelds.
* **Kantenfall 1:** leeres Waffengitter gegen gefuelltes Gitter. Beides muss
  jetzt dieselbe Rangfolge ergeben; frueher nicht.
* **Kantenfall 2:** die beiden Kopien aus der Messung oben,
  `Deep Polished Drizzly Scene` und `Grand Luminous Scene` — vor der Aenderung
  bewegten genau sie sich, jetzt duerfen sie es nicht mehr.
* **Kantenfall 3 (Erwartung, die ueberraschen wird):** unter "Maximise damage"
  stehen jetzt sehr viele Karten auf +0,0 (gemessen 184 von 210). Das ist
  **kein** Fehler meiner Aenderung, sondern F-2. Bitte nicht als Regression
  melden, sondern gegen F-2 fuehren.
* **Kantenfall 4:** Cache. Waffe wechseln loest einen neuen Lauf aus (der Key
  enthaelt weiter die Armaturen), das Ergebnis muss bitgleich sein.
* Mein Testfall ueberspringt sich ohne Spielstand (`planner.owned is None`).
  Auf einem Runner ist AK-191 damit **nicht** abgedeckt.

## An den ui-ux-designer

Eine Abweichung, die dir gehoert: der Blurb der Richtung "Maximise damage"
lautet jetzt `Ranks by attack multipliers, attributes and passives — what
stays fixed between runs.` Zwei Dinge dazu:

1. `Goal.blurb` hat heute **keinen Leser im Programm** (Volltextsuche: nur die
   Registry-Definition und `types.Goal`). Der Satz steht also nirgends auf dem
   Bildschirm; eine Breitenmessung gibt es folglich nicht.
2. Er nennt "attributes", und die Zahl kennt Attribute heute nicht (F-2). Wenn
   F-2 anders entschieden wird, muss der Satz mit. Er ist von keinem Test
   festgehalten — bewusst, weil Wortlaute zu AK-190 und damit zu Teil 2
   gehoeren.
