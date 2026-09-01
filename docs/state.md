# Stand

Stand: 2026-09-02, Ende Zyklus 2. Branch `docs/audit-and-advisor-design`,
19 Commits, gepusht. **Pull Request #16** offen — Merge nach `main` gehoert dem
Nutzer, `main` ist geschuetzt.

## Wo wir stehen
- Nightreign Helper, PySide6/Qt, ~17k Zeilen Python, Windows-only.
- Zyklus 1 = vollstaendiger Audit (nur Dokumentation, kein Codewechsel).
- Zyklus 2 = "eine Rechenstelle, nachweislich unveraendert" plus die
  Regressionen, die dabei entstanden sind. Drei Developer-Runden, drei
  QA-Runden.
- **Testsockel steht:** 0 → 78 Tests, headless, mit CI-Job, gegen echte
  Spieldaten. Vorher gab es null Tests, und die im Code zitierten Waechter
  existierten im veroeffentlichten Repo gar nicht.

## Was in Zyklus 2 geschlossen wurde
QA-001 (zwei driftende Rechenstellen — es waren drei), QA-011, QA-013, QA-014,
QA-015, QA-017, QA-021, QA-022, QA-024, QA-025. Die Schadensrechnung ist aus der
Oberflaeche nach `nrplanner/damage.py` gezogen, **nachweislich verhaltensgleich**
(10 000 Differentialfaelle, 0 Abweichungen; sechs Mutationen alle gefangen).

## Naechster Zyklus (Zyklus 3): der Build-Berater
**Von QA freigegeben.** Grundlage: `ARCHITECTURE.md` AD-001 bis AD-013,
`UI_SPEC.md` AK-01 bis AK-30.

Auflagen, die beim Bau gelten:
- Das Berater-Paket muss unter `nrplanner/` liegen, sonst sieht der
  `compute`-Waechter es nicht (QA-023).
- Bewertet wird mit `model.compute()` selbst, an jedem Suchschritt (AD-002) —
  kein zweiter Scorer.
- Beam-Suche K=20/W=40. Gemessen im ungueenstigsten realen Fall
  (`Wylder's Chalice`, weisser Slot, Deep): **0,46 s**.
- Exemplar-Eindeutigkeit ueber Handles (AD-013). Ohne sie sind bei
  `Wylder's Urn` 40 von 40 Vorschlaegen unbrauchbar.
- Eine **feste, benannte** Gewichtung der acht Schadensarten, im Ergebnis
  sichtbar ausgewiesen. Kein Bedienelement.
- Kein Gefaess-Vorschlag (Nicht-Ziel).

## Offen beim Nutzer
- **UI F1-F4** (blockiert den Berater-Bau): Slots festhalten? Statblatt-Vorschau
  vor dem Anwenden? Flueche mitbewerten? Name des Features?
  Meine Empfehlungen: nein / nein (Undo genuegt) / ja, mitbewerten und benennen
  / offen.
- **`nightlords.png`** (C-002, Ampel ROT): Bildausschnitt neu setzen (empfohlen),
  oder anderer Weg. Dazu: Git-Historie umschreiben oder nicht?
- **PR #16** mergen, wenn gewuenscht — inhaltlich tragfaehig, aber der Stand ist
  nicht releasefaehig.

## Release-Blocker (GOAL A2)
- **QA-003** (P2/Critical): Build-Namen landen ungeprueft im
  QSettings-Schluesselraum; ein `/` im Namen loescht gespeicherte Builds.
- **QA-018** (P2): Waffen-Tab nennt 203,4, die Detailtafel 244,1 fuer dieselbe
  Waffe. Entschieden: Tabs ranken ueber `damage.attack_rating`, Fallback ist
  Umbenennung der Spalte mit gemessener Begruendung.
- **SEC-001 bis SEC-011** — der Sicherheitszyklus ist noch nicht gelaufen.
  SEC-001 (Endlosschleife aus einem heruntergeladenen Save, beim Start, auf dem
  GUI-Thread) ist vier Zeilen Arbeit und sperrt jedes Release.
- **GOAL A9**: keine Pruefung gegen ein gebautes Artefakt. Erststart,
  Startmenue-Eintrag, Icon-Pack-Bau sind ungeprueft. Braucht
  `release-manager` (build, clean-room) und danach `power-user`.

## Naechste kleinere Auftraege, geordnet
1. QA-030 (verdeckte Deep-Aufloesung sichtbar machen) + QA-028 (Custom relic
   gehoert dem Build) + die Luecke "genannten Slot leeren aendert nichts".
2. QA-003 und QA-018 — beide Release-Blocker.
3. QA-016: `architect` korrigiert AD-013 Punkt 4 an der Messung (die Praemisse
   "ein Save ohne lesbare Loadout-Tabelle liefert keine Handles" ist **falsch** —
   beide echten Saves liefern 100 % Handles).
4. QA-027, QA-029, QA-031, QA-019, QA-026 — klein, dokumentiert.

## Was niemand geprueft hat, und das bleibt so, bis es jemand tut
- **Die Oberflaeche hat in Zyklus 2 kein Mensch gesehen.** Das Fenster liess
  sich in dieser Umgebung nicht fokussieren; alle Belege sind headless ueber die
  echten Widgets. Schliesst erst der `power-user` auf einem gebauten Artefakt.
- **Zahlenrichtigkeit gegen das laufende Spiel.** Geprueft wurde gegen die
  Spieldateien und gegen sich selbst, nie gegen das, was das Spiel anzeigt. Der
  README-Vorbehalt zum Attack Rating bleibt offen — **das kann nur der Nutzer
  im Spiel schliessen, und fuer den Berater waere es die wertvollste Pruefung.**
- Nebenlaeufigkeit auf echten Widgets (Doppelklick, Abbruch mitten im Restore).
- Der `("record", offset)`-Zweig von `copy_key`: mit echten Daten nicht
  erreichbar, synthetisch geprueft, unbewacht.

## Prozessfehler dieses Zyklus, zur Kenntnis
- T-008 bis T-012 wurden **ohne Auftragsdatei** vergeben, nur als Freitext im
  Dispatch. Der `ui-ux-designer` hat es gemerkt und vermerkt, der `archivist`
  hat die Luecke im Repo gefunden. Die Vorschrift lautet: je nicht-trivialem
  Auftrag eine Datei unter `docs/tasks/`.
- Zwei parallel laufende `researcher` haben sich beim Schreiben ihres
  gemeinsamen Rollengedaechtnisses ueberschrieben. Aufgefallen ist es nur, weil
  der zweite es bemerkt und zusammengefuehrt hat.
