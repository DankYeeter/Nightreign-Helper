# Stand

2026-09-07, **Zyklus 16 laeuft**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf: `docs/archiv/state-bis-2026-09-03.md`. Reihenfolge:
`docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`, `security/findings.md`.
Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-106** · QA ab **QA-198** · AK ab **AK-195** ·
AD ab **AD-027** · DR ab **DR-019** · R ab **R-007** · NH ab **NH-003** ·
C ab **C-001** · A (Auflagen) ab **A-001**.
**Suite:** **1256 passed, 9 skipped, 0 failed** (T-102, 07.09.). `pytest -n auto`
**127 s** statt 840 s seriell (`4431c7a`), Namensvergleich ueber 1265 Faelle ohne
Abweichung. **`-n auto` ist bewusst keine Voreinstellung** — eine einzeln
genannte Datei stiege von 1,2 auf 4,0 s, und genau die verlangt die Gegenprobe.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**. **Die Pruefung
im laufenden Spiel macht der Nutzer ganz am Ende.** Der Fragebogen vor dem
Zyklus haelt auch im autonomen Lauf an — autonom gilt **innerhalb** eines
Zyklus.

## Zyklus 16 — der Release-Weg (Nutzerentscheid 07.09.2026)

Ziel **A9 und A2**. A9 hat als einziges Kriterium null Evidenz: es gab nie ein
gebautes Artefakt, obwohl `release.yml` und `NightreignHelper.spec` existieren.
A2 haengt nur noch an SEC-009 — derselbe Weg, dieselbe Datei.

Kette: **T-104** `compliance-agent` (`auflagen`) **+ T-105** `developer`
(SEC-009) parallel → `technical-writer` → `release-manager` (`build`) →
`release-manager` (`clean-room`) → `qa-engineer` **+** `power-user` parallel.

**Clean-room auf diesem Rechner, isoliert** (leeres Verzeichnis, geleerter
PATH, keine `.venv`) — A9 gilt danach **mit Vorbehalt** erfuellt: keine echte
Fremdinstallation. **GOAL-Wortlaut beachten:** A9 verlangt den
**`qa-engineer`** am Artefakt, nicht den `power-user`.

**Stehende `power-user`-Messreihe, ab jetzt unveraendert kopiert:** Erststart
ohne Vorwissen · Spielstand finden lassen · im Build planner ein Relikt
tauschen · den Beratervorschlag anwenden · eine Zahl im Arsenal-Tab deuten ·
beenden und neu starten. Ab jetzt aendert sich nur das Programm, nie das
Messgeraet.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | weitgehend — 197 QA, 24 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **nur noch SEC-009** (T-105) |
| A3-A6 | der Build-Berater | **gebaut** — Kern, Leiste, Slotkarte, `Why`-Dialog, Anwenden/Halten, Picker |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend; **QA-186 offen** |
| A8 | alles Englisch | haelt, ohne Waechter (QA-192) |
| A9 | QA gegen ein **gebautes Artefakt** | **Zyklus 16** |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ohne Raten ans Ziel | offen (QA-173) |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | Spec liegt (AK-106-132), Umsetzung offen |

## Beschlossen, nicht beauftragt

- **D-1** `performance-tuner` auf `model.compute` (94 % der 941,6 ms) — in
  **S11**, Erstlauf im Projekt, also opus.
- **D-11** Doppeltes Zahlenformat: Waechter, AK-136 verlangt, dass beide Orte
  dasselbe schreiben.
- **`compute_resistances`** — Zurueckstellung wieder offen: T-080 zaehlt drei
  Fluche und **33 stumme positive Effekte**, zusammen 36 Zeilen auf einem
  Spielstand. Vor der Bestaetigung nachmessen.
- **QA-185, Klassenmassnahme:** vor der naechsten Aenderung entscheiden, ob
  `sources` durchgaengig ueber Ids gefuehrt wird. Latent (0 von 456 Paaren).
- **A16/A17** (schlechtester/bester Fall, Rangfolge ohne Bezugswaffe),
  spezifiziert in AK-182 bis AK-194, **nicht gebaut**. Zyklus 17.

## Statuskorrektur 07.09.2026 (zweite), am Code geprueft

**SEC-022, SEC-024, QA-194** standen faelschlich auf "offen", sind belegt
behoben (`912a39a`, `2570d86`); Beleg in den Befundlisten. Zweiter Fall
derselben Klasse an einem Tag. **QA-196/QA-197 (an den Director) sind
geklaert** und stehen in der Rollendefinition: Worktree startet auf
`origin/HEAD`, braucht **Schritt 0**; Scratchpad ist pro Sitzung geteilt,
braucht ein Unterverzeichnis je T-Nummer. Ab T-104/T-105 angewandt.

## Offen aus der Pruefphase (Zyklus 15)

QA-181 (Stacking unbewacht) · QA-182 · QA-184 · QA-186 (GATE_FIELDS
beschriftet 51 Gegenstandseffekte falsch, seit T-090 **sichtbar
widerspruechlich**) · QA-188 (zwei alte Wortlaute in der Leiste) · QA-190
(zwei Anzeigen aus `UI_SPEC` §3.3 nie gebaut) · QA-191 (acht Nightfarer
ungetestet) · QA-192 (kein Englisch-Waechter) · QA-193 (zweiter Deckel ohne
Anzeigeweg) · QA-195 (Testeinstellungen unter der Spieler-Organisation) ·
SEC-019/SEC-015 (Mittel) · SEC-021, SEC-023 (Niedrig).

## Der Rest — in dieser Reihenfolge

1. **Zyklus 16** (laeuft): der Release-Weg, A9 und A2.
2. **Zyklus 17**: der Fix-Stapel oben, zwei parallele `developer` mit
   disjunkten Dateilisten, danach parallele Pruefphase.
3. **A16/A17** aus AK-182 bis AK-194.
4. **A11 schliessen:** QA-173 entscheiden und beheben, dann die stehende
   Messreihe erneut fahren.
5. **A15** mit QA-171. **S11** Budget mit dem `performance-tuner`.
6. **P4** · **P5** · **P7**.

## Beim Nutzer — offen

- **F-B QA-096** Raider x1,18 auf Greataxe/Great Hammer, **keine Param-Quelle**
  (252 Tabellen, 6,66 Mio. Zellen) · **F-C QA-097** Cursed Claws x0,88 fuer
  alle ausser dem Revenant. Beide: Lv15-Messung im Spiel.
- **F-F QA-113** vier Relikte wandeln Schadensart um, das Programm bewegt
  **exakt 0**. Eine Ablesung entscheidet: Grundwert 114, drei Lesarten sagen
  **91 / 116 / 117**.
- **F-G QA-170** keine Sortierung ueber Waffenkategorien hinweg, waere eine
  **neue Funktion** · **Streichliste je Tab** (13 Vorschlaege, `UI_SPEC` §8).

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008 bis L-013;
projekteigen NH-001, NH-002. Neu 07.09. im Rahmenblock: **kein Hintergrundlauf,
auf dessen Ende der Agent wartet** · **ein Feldname ist keine Beschreibung**
(drei Gegenproben vor jedem Nutzertext an einem Datenfeld, Anlass QA-186).

**Nie geprueft:** Linux/macOS · eine echte Fremdinstallation.
