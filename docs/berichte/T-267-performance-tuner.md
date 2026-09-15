# T-267 — performance-tuner: Optimize-Wandzeit nach dem Beam

```
STATUS: erledigt (Messlauf und Ursache, keine Codeänderung)
AUFTRAG: T-267b (Optimize-Wandzeit-Zuwachs seit 1.10.0 profilen, Ursache benennen, wenn möglich lokal optimieren)
GELESEN: docs/berichte/T-265d-qa-engineer.md · docs/perf/baselines.md (S11-A, S11-L) · nrplanner/advisor/{run,evaluate,search,goals,explain}.py ·
         nrplanner/model.py (compute, compute_qualitative) · nrplanner/effecttext.py · nrplanner/advisorbar.py (asking_from, AdvisorBar) ·
         nrplanner/advisor/worker.py (AdvisorController) · tests/test_advisor_run.py, tests/test_one_build.py · scripts/measure_advisor_search.py
GEÄNDERT: docs/perf/baselines.md (Abschnitt S12 ergänzt) · docs/berichte/T-267-performance-tuner.md (neu). Kein Produktivcode geändert.
ANNAHMEN: (1) Maschine Ryzen 9 5900X (Rechenlastprobe 212,2 ms) ist nicht das Zielgerät und nicht S11-A bis S11-K vergleichbar — neuer Abschnitt S12.
         (2) Der eingefrorene Spielstand ist derselbe wie T-265d (sha256 f4940e4b…3540, 319 Relikte) — direkter Vergleich zur QA-Zahl zulässig.
NÄCHSTER: director (Priorisierung der Spec unten an developer) · developer (Umsetzung `want_qualitative`-Schalter, falls freigegeben)
BLOCKIERT DURCH: nichts
```

## 1. Scope, Messszenario, Umgebung

Auftrag T-267b: QA-Befund aus T-265d (`docs/berichte/T-265d-qa-engineer.md`,
Abschnitt "Beobachtungen") — Optimize-Wandzeit via UI-Automation 1809 ms
(1.12.0) gegen 1229 ms (1.10.0, T-241d), Beam laut S11-A/`measure_advisor_
search.py` unverändert (900 vs. 858 ms). Auftrag: profilen, Ursache benennen,
kleinste wirksame Optimierung ohne Verhaltensänderung, Zielwert Wandzeit
≤ 1.10.0-Niveau ±10 %.

Szenario (S11-A, mit einer Korrektur — siehe unten): `Wylder`, `Wylder's
Chalice`, Deep of Night an, Stufe 15, sechs freie Slots, `Maximise damage`,
K=20/W=40, 319 Relikte, nichts festgehalten. Umgebung: `QT_QPA_PLATFORM=
windows`, reales Fenster, `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-267`, eigenes
`LOCALAPPDATA`/`APPDATA`, Testabzug kopiert (841 Dateien, `extract_version`
11 — Vorlage weiter gültig), Spielstand eingefroren (identisch mit T-265d).
Rechner Ryzen 9 5900X, Rechenlastprobe 212,2 ms — Details und volle Tabellen
in `docs/perf/baselines.md`, Abschnitt **S12**.

## 2. Baseline und Signifikanzschwelle

Volle Zahlen in S12. Kurzfassung:

| Messung | Median (n=5) |
|---|---|
| `measure_advisor_search.py` (alte S11-A-Formel, `reference=Startwaffe`) | 887,9 ms |
| `pools`+`beam` mit dem echten `GoalContext` des Fensters (`reference=None`) | 1260,9 ms |
| `advisor.run.run` headless, voller Pfad | 1286,1 ms |
| `show_the_suggestion` (Kartenaufbau) | 70,3 ms |
| **Klick `Optimize` → `suggestion_changed`, echter Pfad, Cache je Klick geleert** | **1603,9 ms** |

Schwelle: 5 % (2s/Median 2,4–3,0 % über die Wiederholungen). Absolute
Untergrenze A6 (6 s) nicht maßgeblich, die Zahlen liegen weit darunter.

Die letzte Zeile ist das In-Process-Gegenstück zu T-265d's UI-Automation-Zahl
1809 ms: 1603,9 ms Programmlaufzeit + rund 200 ms UIA-Rundlauf decken sie
weitgehend — der QA-Befund ist damit reproduziert, nicht nur geglaubt.

**Methodischer Fallstrick, der die erste Messreihe unbrauchbar machte:**
`AdvisorController` cacht Antworten (AD-007). Ein zweiter Klick mit
unveränderter Anfrage ist ein Cache-Treffer, keine Neuberechnung — die
ersten Messläufe zeigten dadurch scheinbare 290 ms (Cache-Treffer), bis
`before_the_data_changes()` vor jedem Klick den Cache leerte und die reale
Kostenzahl (1603,9 ms) sichtbar wurde.

## 3. Engpässe, priorisiert

**Befund 1 (Impact hoch, Aufwand mittel — struktureller Hebel, nicht
selbst umgesetzt):** Die echte Oberfläche stellt seit AD-032/A17 jede
Anfrage mit `ctx.reference=None` (`advisorbar.asking_from`, kein
Waffenraster mehr gelesen). `goals.py::_max_damage` nimmt dadurch den
billigen `_attack_multiplier_mean`-Zweig — das ist nicht das Problem. Das
Problem: ohne Referenzwaffe kennt `model.compute` keinen `wep_type`, also
gelten mehr Effekte als waffentyp-bedingt (`is_conditional`/
`satisfied_by_weapon` mit `wep_type=None`), und `compute_qualitative` baut
für jeden davon Text (`effecttext.describe/name/owner/works_for`) — **bei
jeder der 3883–4121 Bewertungen des Beams, nicht nur bei den 40 am Ende
erklärten Vorschlägen.** Profil: `model.compute` 4121 Aufrufe, 3,29 s von
3,78 s profilierter Gesamtzeit (88 %); `effecttext.*` allein 0,61 s tottime
(16 % der profilierten Zeit). Der Beam selbst braucht während des reinen
Scorings (`search.py::score`) nur `GoalScore.value`, nie
`build.qualitative`/`build.situational`.

**Warum die S11-A-Messreihe das nie sah:** `measure_advisor_search.py`
setzt weiterhin `reference=<Startwaffe>` — ein Zweig, den `goals.py`
selbst als "reached by no caller inside `nrplanner/` today" dokumentiert
(Zeile 236–244, seit AD-032). "Beam unverändert, 900 vs. 858 ms" (T-265d)
verglich zwei Läufe eines Zweigs, den das Programm nicht mehr anfragt —
die Messreihe maß am tatsächlichen Zuwachs vorbei, nicht weil er nicht da
war, sondern weil das Skript ihn nicht mehr auslösen konnte.

**Befund 2 (Impact klein, ausdrücklich kein Handlungsbedarf):** "Jeder
Vorschlag wird erklärt, nicht nur der erste" (AD-010/AD-014,
`test_every_suggestion_carries_its_reasons_and_not_only_the_first`) kostet
selbst nur rund 60 ms (54,6–63,2 ms über 5 Läufe) — gewollte, getestete
Architektur, nicht die Ursache des gemeldeten Zuwachses.

**Befund 3 (kein Fund):** `required_but_unmet` läuft nur bei leerem Beam
(hier nicht erreicht); `show_the_suggestion`/Fensteraktualisierung kostet
70 ms, klein.

## 4. Durchgeführte Optimierungen

**Keine.** Der wirksame Hebel (Befund 1) sitzt in `model.compute`, der am
zentralsten genutzten Funktion des Programms: `evaluate.py` ist die einzige
erlaubte Aufrufstelle unter `advisor/` (`tests/test_one_build.py::
test_the_user_interface_holds_exactly_one_call_to_compute`, ein AST-Wächter
ohne Zweitstelle), und `compute`/`compute_qualitative` tragen dieselbe Art
Architekturdokumentation (AD-Verweise, benannte Entscheidungen) wie die in
meiner Erinnerung als ULP-empfindlich geführten `weapons.py`/`damage.py`.
Eine Lösung — ein `want_qualitative`-Schalter an `compute`, der beim reinen
Scoring (`search.py::score`) übersprungen wird, aber beim Aufbau der 40
erklärten Vorschläge und beim Basiswert (`base = evaluate(problem, (), ctx)`)
gesetzt bleibt — ist additiv und behielte für jeden anderen der zahlreichen
Aufrufer den Default (`True`) bei. Sie reicht aber quer durch `model.py`,
`evaluate.py` und `search.py` und ändert, was die zentralste Funktion des
Programms berechnet — das ist Architektur, keine lokale Änderung, und geht
nach Rollenregel als Spec an `developer`:

**Spec für `developer` (Priorität 1, Befund 1):**
- `nrplanner/model.py::compute` (und `compute_qualitative`): neuer
  Parameter `want_qualitative: bool = True`. Bei `False` `build.qualitative`
  und `build.situational` leer lassen, alles andere unverändert (gleiche
  Signatur sonst, gleiche Rückgabewerte für `want_qualitative=True`, damit
  jeder heutige Aufrufer unverändert bleibt).
- `nrplanner/advisor/evaluate.py::evaluate`: neuer Parameter (Default
  `True`), durchgereicht an `model.compute`. Bleibt die eine Aufrufstelle
  (Wächter unberührt, kein zweiter Ort).
- `nrplanner/advisor/search.py::goal_scorer`/`score`: ruft `evaluate(...,
  want_qualitative=False)` — der Beam braucht nur `.value`.
- `nrplanner/advisor/run.py::run`: `base = evaluate(...)` und `_explained`
  (die 40 erklärten Vorschläge) behalten `want_qualitative=True` — deren
  `build.qualitative`/`situational` werden von `explain.reasons` gelesen.
- Test: ein Golden-Vergleich, der `evaluate(..., want_qualitative=False)`
  gegen `evaluate(..., want_qualitative=True)` auf denselben Feldern außer
  `qualitative`/`situational` prüft (bit-identisch), plus ein Lauf von
  `tests/test_advisor_run.py`, `tests/test_one_build.py`,
  `tests/test_advisor_goals.py` unverändert grün.
- Erwarteter Gewinn: bis zu ~40 % der `model.compute`-Zeit für die 3843
  reinen Score-Aufrufe (gemessen: `compute_qualitative`-Anteil 1,343 s von
  3,29 s `compute`-Cumtime unter Profiler) — realistisch rund 400–500 ms
  der 1604 ms Wandzeit, je nach Overhead-Anteil des Profilers.

**Empfehlung an `qa-engineer`/`director` (kein Bugfix, aber Messinfrastruktur):**
`scripts/measure_advisor_search.py` und die S11-A-Zeile in
`docs/perf/baselines.md` messen seit AD-032 ein Szenario
(`reference=<Startwaffe>`), das die Oberfläche nicht mehr anfragt. Empfehlung:
das Skript auf `reference=None` umstellen (oder eine zweite, als
"repräsentativ" markierte Szenario-Variante ergänzen), sonst bleibt der
getrackte Beam-Wert dauerhaft blind für genau diese Klasse Regression.

## 5. Verworfene Optimierungen

- **Memoisierung von `effecttext.describe/name/owner/works_for` nach
  Effekt-Id** (0,61 s von 3,78 s profiliert, 16 %) — real vorhandenes
  Sparpotential, aber ein neuer prozessweiter Cache bräuchte dieselbe
  Invalidierungs-Disziplin wie `AdvisorController._cache`
  (`before_the_data_changes`, AD-006 Punkt 7) — sonst zeigt ein Rescan mit
  neuer `data_version` veraltete Texte für dieselbe Effekt-Id. Das ist ein
  neuer Architekturvertrag, keine lokale Änderung; zurückgestellt bis
  Befund 1 entschieden ist (danach ggf. ohnehin kleiner, weil
  `want_qualitative=False` denselben Code während des Beams gar nicht mehr
  durchläuft). Reaktivieren, falls Befund 1 umgesetzt ist und
  `effecttext.*` weiterhin über der Schwelle liegt.
- **Reduktion der 40 erklärten Vorschläge auf nur den besten** — verworfen,
  nicht weil wirkungslos wäre, sondern weil es dem Auftrag "keine
  Verhaltensänderung" widerspricht: `AD-010`/`AD-014` und ein Test
  (`test_every_suggestion_carries_its_reasons_and_not_only_the_first`)
  legen ausdrücklich fest, dass jeder Vorschlag erklärt wird, nicht nur der
  erste. Kosten ohnehin klein (~60 ms, Befund 2) — kein Grund, hier
  anzusetzen.

## 6. Verifikationsstatus

Keine Codeänderung, daher keine Testpflicht in diesem Lauf; `pytest -n auto`
nicht erneut ausgeführt (letzter bekannter Stand T-265: 1687/10 auf
`02e0721`, Code seit dem Bau unverändert bis `24f9d27`). Die Spec oben nennt
die Tests, die vor Umsetzung durch `developer` grün bleiben müssen.

## 7. Fehlerfunde und Empfehlungen an andere Rollen

Kein Fehlerfund (Bug) — der Zuwachs ist eine Folge einer bewussten,
dokumentierten Architekturentscheidung (AD-032/A17), keine Regression durch
ein Versehen. Empfehlungen: siehe Abschnitt 4 (Spec an `developer`) und die
Messinfrastruktur-Empfehlung oben (`measure_advisor_search.py`).

## Scratchpad-Skripte (nicht Teil des Produktivbaums)

`profile_run.py`, `phase_timing.py`, `profile_ui.py`, `isolate.py` unter dem
Sitzungs-Scratchpad — Rezepte für diese Zahlen, nicht ausgeliefert.
