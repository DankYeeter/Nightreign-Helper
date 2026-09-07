# Stand

2026-09-07, **Zyklus 16 laeuft**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf: `docs/archiv/`. Reihenfolge: `docs/plan-restarbeiten.md`. Befunde:
`qa/findings.md`, `security/findings.md`. Auflagen: `docs/legal/AUFLAGEN.md`.
Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-108** · QA ab **QA-198** · SEC ab **SEC-026** ·
AK ab **AK-195** · AD ab **AD-027** · DR ab **DR-019** · R ab **R-007** ·
NH ab **NH-003** · C ab **C-004** · A (Auflagen) ab **A-033**.
**Suite:** **1256 passed, 9 skipped, 0 failed** (T-102, 07.09.). `pytest -n auto`
**127 s** statt 840 s seriell (`4431c7a`), Namensvergleich ueber 1265 Faelle ohne
Abweichung. **`-n auto` ist bewusst keine Voreinstellung** — eine einzeln
genannte Datei stiege von 1,2 auf 4,0 s, und genau die verlangt die Gegenprobe.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**; der Fragebogen
vor dem Zyklus haelt trotzdem an. **Die Pruefung im laufenden Spiel macht der
Nutzer ganz am Ende.**

## Zyklus 16 — der Release-Weg (Nutzerentscheid 07.09.2026)

Ziel **A9 und A2**. **A2 ist seit T-105 erfuellt** — SEC-009 behoben und
gegengeprueft (`d92bab9`), kein Hoch-Befund mehr offen; Bestaetigung durch den
`security-reviewer` steht aus.

**Falsche Praemisse, korrigiert 07.09.2026.** Die Zeile "es gibt bis heute
keine EXE" stand seit Zyklen hier und war falsch: **12 veroeffentlichte
Releases, alle mit `NightreignHelper.exe`, juengstes `v1.7.1` vom 24.08.2026,
25 Downloads** (`gh release list`, vom Director nachgeprueft; gefunden vom
`release-manager` in T-106). Der Director hat sie ungeprueft in den
Fragebogen, in drei Auftragsdateien und in den Bericht an den Nutzer
getragen. **Folge:** A9 bleibt offen (kein `qa-engineer` lief je gegen ein
Artefakt), aber der Risikoweg ist das **Update ueber eine vorhandene
Installationsbasis**, nicht die Erstinstallation — und die Rechtsschwelle aus
C-003 liegt bereits hinter uns (T-108 laeuft).

Kette: T-104 `compliance-agent` ✔ **+** T-105 `developer` ✔ (parallel) →
**T-106** `release-manager` (`plan`) **+ T-107** `technical-writer` (parallel,
laufen) → `release-manager` (`build`) → (`clean-room`) → `qa-engineer` **+**
`power-user` parallel. Dazwischen ein `developer` fuer **A-020** (Hinweispaket
als Release-Asset) — nicht parallel zum `release-manager`.

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
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt** (T-105), QA-Bestaetigung offen |
| A3-A6 | der Build-Berater | **gebaut** — Kern, Leiste, Slotkarte, `Why`-Dialog, Anwenden/Halten, Picker |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend; **QA-186 offen** |
| A8 | alles Englisch | haelt, ohne Waechter (QA-192) |
| A9 | QA gegen ein **gebautes Artefakt** | **Zyklus 16**; 12 Releases gebaut, nie eines geprueft |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ohne Raten ans Ziel | offen (QA-173) |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | Spec liegt (AK-106-132), Umsetzung offen |

## Beschlossen, nicht beauftragt

- **D-1** `performance-tuner` auf `model.compute` (94 % der 941,6 ms) — S11,
  Erstlauf im Projekt, also opus. · **D-11** doppeltes Zahlenformat: Waechter
  nach AK-136.
- **`compute_resistances`** — Zurueckstellung wieder offen: T-080 zaehlt 36
  stumme Zeilen auf einem Spielstand. Vor der Bestaetigung nachmessen.
- **QA-185, Klassenmassnahme:** vor der naechsten Aenderung entscheiden, ob
  `sources` durchgaengig ueber Ids gefuehrt wird. Latent (0 von 456 Paaren).
- **A16/A17**, spezifiziert in AK-182 bis AK-194, **nicht gebaut**. Zyklus 17.

## Buchfuehrung des Directors — zwei Korrekturen am 07.09.

**SEC-022, SEC-024, QA-194** standen faelschlich auf "offen", sind belegt
behoben; zweiter Fall derselben Klasse an einem Tag. **T-104 behauptete,
`docs/legal/AUFLAGEN.md` existiere nicht** — sie existiert seit dem 01.09.;
eine Absenz-Behauptung ohne Durchsicht. **QA-196/QA-197 sind geklaert** und
stehen in der Rollendefinition (Worktree braucht Schritt 0, Scratchpad ein
Unterverzeichnis je T-Nummer).

## Offen aus der Pruefphase (Zyklus 15)

QA-181 (Stacking unbewacht) · QA-182 · QA-184 · **QA-186** (GATE_FIELDS
beschriftet 51 Gegenstandseffekte falsch, seit T-090 sichtbar
widerspruechlich) · QA-188 · QA-190 (zwei `UI_SPEC`-§3.3-Anzeigen nie gebaut) ·
QA-191 (acht Nightfarer ungetestet) · QA-192 · QA-193 · QA-195 · **SEC-025**
(`tests.yml` unpinned) · SEC-019/015 (Mittel) · SEC-021, SEC-023 (Niedrig).

## Der Rest — in dieser Reihenfolge

1. **Zyklus 16** (laeuft): der Release-Weg, A9.
2. **Zyklus 17**: der Fix-Stapel oben plus SEC-025, zwei parallele
   `developer` mit disjunkten Dateilisten, danach parallele Pruefphase.
3. **A16/A17** aus AK-182 bis AK-194. 4. **A11** ueber QA-173, dann die
   stehende Messreihe erneut. 5. **A15** mit QA-171, **S11** Budget.
6. **P4** · **P5** · **P7**.

## Beim Nutzer — offen

**Vor dem ersten Release zu entscheiden (C-003, 07.09.2026).** Ich lege sie
gebuendelt an der Stufengrenze vor Bau und Release vor; sie halten den
laufenden Zyklus **nicht** auf, weil Bauen und Pruefen keine Weitergabe ist.
- **A-025, GRAU:** Die EXE traegt die bekannten Entschluesselungsschluessel.
  Privatgebrauch ist straflos, **mit dem ersten Release-Asset wird aus Nutzung
  Verbreitung** (§ 95a Abs. 3 UrhG, EULA 10(i)). Risiko tragen oder vorher
  anwaltlich klaeren? Alternative ohne das Risiko: Quellcode statt EXE.
- Bleibt das Repo dauerhaft oeffentlich (LGPL haengt daran, A-022)? · Soll das
  Release beworben werden? · Beruehrt die Weitergabe deinen Arbeitsvertrag
  (seit C-001 offen)? · Eigener Auftrag zu US-Recht (17 U.S.C. § 1201)?

**Aus dem Audit, Messung im Spiel:** **F-B QA-096** Raider x1,18 auf
Greataxe/Great Hammer, keine Param-Quelle · **F-C QA-097** Cursed Claws x0,88
fuer alle ausser dem Revenant · **F-F QA-113** vier Relikte wandeln
Schadensart um, das Programm bewegt **exakt 0** (Grundwert 114, drei Lesarten
sagen 91 / 116 / 117).
- **F-G QA-170** Sortierung ueber Waffenkategorien hinweg waere eine **neue
  Funktion** · **Streichliste je Tab** (13 Vorschlaege, `UI_SPEC` §8).

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008 bis L-013;
projekteigen NH-001, NH-002. Neu 07.09. im Rahmenblock: **kein Hintergrundlauf,
auf dessen Ende der Agent wartet** · **ein Feldname ist keine Beschreibung**
(drei Gegenproben vor jedem Nutzertext an einem Datenfeld, Anlass QA-186).

**Nie geprueft:** Linux/macOS · eine echte Fremdinstallation.
