# T-253 -- Retest der T-252-Fixes auf `08ddba6` (Code `2a0ca0d`, 1.11.0)

## Befriefing

Risiko absteigend: (1) SEC-045/QA-267 -- Registry-Kollision legte den
Berater bis zum Fix komplett lahm, hoechste Schwere; (2) QA-268 --
Zeitfenster-Bug, nur am realen Fenster mit echter Debounce pruefbar, Unit-
Tests mit Fake-Controller koennten das Timing-Verhalten verdecken; (3)
DR-025/026 -- klein, aber A8-nah (woertlicher Text); (4) QA-266 --
Testinfrastruktur, Vollpruefung ueber die Suite. Reihenfolge: Suite zuerst
(Regressionsschutz), dann SEC-045/QA-267 rot-vorher, dann Fensterlauf fuer
QA-268/DR-025/DR-026/A18/A19.

## Suite

`pytest -n auto` mit `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-253`, eigenem
`LOCALAPPDATA`/`APPDATA`, Testabzug kopiert: **1602 passed, 10 skipped in
70.27 s**. Deckt sich mit dem T-252-Abschlussbericht (1602/10).

`MUTATIONS` in `scripts/differential/mutate.py`: 0 Eintraege (bereits
geleert) -- nichts nachzufahren oder zu loeschen.

## SEC-045/QA-267 -- rot-vorher + live

Rot-vorher: `git archive HEAD` in den Scratchpad extrahiert, `EffectFilters
.__init__` auf den Stand vor `e18d782` zurueckgebaut (kein disjunktes
Laden). `test_an_id_under_both_keys_is_required_and_no_longer_excluded`
faellt wie vorhergesagt (`frozenset({5, 6}) != {5}`); die uebrigen 10 Tests
der Datei bleiben gruen.

Live am echten Fenster (Registry vor `Planner()`-Konstruktion vergiftet,
`advisor/excluded = advisor/required = 7000302`): `EffectFilters` wirft
nicht, `excluded == []`, `required == [7000302]` (Director-Regel:
`required` gewinnt). `Optimize` liefert in 0.63 s eine Antwort -- der
Berater rechnet, keine `SlotProblem`-`ValueError` mehr.

## QA-268 -- live, echte Debounce

`Optimize` geklickt, `the_build_changed(marking_changed=True)` sofort
danach (gemessen 0,0 ms, also innerhalb der 250-ms-Debounce): Zustand
`OUTDATED`, Statuszeile woertlich *"The effects you marked changed while
this was working out — use Optimize again."* Nach 1 s Beobachtung bleibt
der Zustand `OUTDATED` -- keine spaeter eintreffende Antwort ueberschreibt
ihn mit den alten Mengen.

## DR-025/DR-026 -- live

`WhyDialog` mit einer echten Optimize-Antwort geoeffnet (21 `MarkedLine`).
Drei `Enter`-Tastendruecke auf den Markierungsknopf: Zyklus `None ->
excluded -> required -> None`. Tooltips je Zustand woertlich identisch zu
`MARK_TOOLTIPS`, inkl. Nachtragstext *"Click to require it instead."* fuer
`excluded`.

## QA-266 -- Testisolation

Kein `nightreign.exe`-Prozess lief waehrend des Laufs (`tasklist` leer).
Die Suite laeuft ueber `conftest.no_living_save` (autouse, Session-Scope)
auf den eingefrorenen Slot; volle Suite bestaetigt oben. Diff gelesen,
Mechanik (leere `save_roots()`, `inventory.scan`-Fallback auf
`frozen_scan()`) stimmt mit dem Commit ueberein.

## A18/A19 -- Kurzcheck am Fenster

Drei Zustaende: siehe DR-025 (Enter-Zyklus). Zaehler-Tooltip (AK-280): nach
Markierung `<span>... · 1 effect required</span>` auf der Beraterzeile.
Persistenz ueber Neustart: `filters.mark(7037300, EXCLUDED)` schreibt
`advisor/excluded=7037300`; eine neu gebaute `EffectFilters()`-Instanz
liest denselben Stand zurueck.

## Kontraktblock

| ID | Ergebnis |
|---|---|
| QA-267 | behoben, bestaetigt (rot-vorher + live), geschlossen |
| SEC-045 | behoben, bestaetigt (rot-vorher + live), geschlossen |
| QA-268 | behoben, bestaetigt (live, echte Debounce), geschlossen |
| DR-025 | behoben, bestaetigt (live, Enter-Zyklus), geschlossen |
| DR-026 | behoben, bestaetigt (live, drei Tooltip-Literale), geschlossen |
| QA-266 | behoben, bestaetigt (Suite 1602/10, kein lebender Save), geschlossen |

Keine neuen P1/P2-Befunde. A18/A19-Kurzcheck ohne Abweichung.

**Gesamturteil: PASS**
