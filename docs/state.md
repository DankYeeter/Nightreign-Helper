# Stand

2026-09-08, **Zyklus 18 laeuft**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen, 411 Commits gegen `origin/main`
(`gh pr view 16` / `git rev-list --count`, 08.09.) — **Merge gehoert dem
Nutzer.** Verlauf: `docs/archiv/`. Reihenfolge: `docs/plan-restarbeiten.md`.
Befunde: `qa/findings.md`, `security/findings.md`. Auflagen:
`docs/legal/AUFLAGEN.md`. Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-124** · QA ab **QA-210** · SEC ab **SEC-026** ·
AK ab **AK-195** · AD ab **AD-030** · DR ab **DR-019** · R ab **R-007** ·
NH ab **NH-003** · C ab **C-004** · A (Auflagen) ab **A-033**.
**Suite:** **1257 passed, 9 skipped, 0 failed** (T-109, unabhaengig bestaetigt
in T-111 und T-114 im frischen Klon). *Bis 08.09. stand hier 1256 aus T-102.*
Testbefehl und die Begruendung gegen `-n auto` als Voreinstellung: `CLAUDE.md`.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**; der Fragebogen
vor dem Zyklus haelt trotzdem an. **Die Pruefung im laufenden Spiel macht der
Nutzer ganz am Ende.**

## Zyklus 18 — was laeuft und woran er endet

Beauftragt am 08.09.2026, parallel, disjunkte Dateilisten:

- **T-122 `architect`** (opus) — AD-028 zu **QA-208** (der Picker-Weg des
  Beraters rechnet im Hauptthread, AD-018 ist an einer widerlegten Zahl
  gescheitert: Docstring 51 ms, gemessen 318 ms) und AD-029 zu **QA-209**
  (Spielstand-Lesen 6,15 s im Hauptthread, Gegenentwurf mit Faktor 45
  gemessen). Beruehrt nur `ARCHITECTURE.md`.
- **T-123 `developer`, Stufe normal** — die zwei Waechter **QA-204** (A8,
  Sprache) und **QA-205** (A3, Vollstaendigkeit ueber alle Nightfarer und
  Kelche), je mit toetender Mutation nach L-008. Beruehrt nur `tests/`.

**Erfolgreich**, wenn beide AD-Entscheidungen stehen, die zwei Waechter mit
belegter toetender Mutation laufen und die Suite gruen bleibt. Danach:
`ui-ux-designer` (nur falls AD-028 sichtbar wird) → `developer` (Fix-Stapel)
→ Pruefphase → Neubau → Release.

## Drei Nutzerentscheide vom 08.09.2026

1. **A6 hat seine Zahlen** — woertlich aus T-118 nach `GOAL.md` uebernommen:
   Slot-Frage im Median **unter 500 ms**, `Optimize` **unter 6 s**,
   **Hauptthread hoechstens 50 ms**. Damit ist **QA-203 geschlossen** und A6
   entscheidbar. Die 50-ms-Zeile ist heute verletzt (318 ms) — das ist QA-208.
2. **QA-207** (toter Verweis im Hinweispaket): **nur nach vorn reparieren.**
   Die zwoelf bereits veroeffentlichten Pakete bleiben unangetastet; A-021
   verlangt die Beilage, nicht einen Pfad, der Verstoss bleibt beendet.
3. **QA-209 kommt in den Fix-Stapel vor 1.8.0**, nicht danach — ein Neubau
   statt zwei. Verzoegert das Release um etwa einen Zyklus.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | weitgehend — 209 QA, 25 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt** (T-105), QA-Bestaetigung offen |
| A3-A5 | der Build-Berater | **gebaut**, in T-114 am Artefakt bestaetigt |
| A6 | Oberflaeche blockiert nicht | **Zahl gesetzt**, dritte Zeile verletzt (QA-208) |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend; **QA-186 offen** |
| A8 | alles Englisch | haelt, Waechter in Arbeit (T-123) |
| A9 | QA gegen ein **gebautes Artefakt** | **5 von 6 PASS**, A6 wieder offen |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ohne Raten ans Ziel | offen (QA-173) |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | Spec liegt (AK-106-132), Umsetzung offen |

**Artefakt (Zyklus 16):** `dist/NightreignHelper.exe`, 59 010 777 B, 1.8.0,
SHA-256 `42B21AA2...F221`. Update-Weg an einem echten `v1.7.1` belegt.
**1.8.0 geht erst nach dem Fix-Stapel raus.**

## Beschlossen, nicht beauftragt

- **D-11** doppeltes Zahlenformat: Waechter nach AK-136.
- **`compute_resistances`** — Zurueckstellung wieder offen: 36 stumme Zeilen
  auf einem Spielstand (T-080). Vor der Bestaetigung nachmessen.
- **QA-185, Klassenmassnahme:** vor der naechsten Aenderung entscheiden, ob
  `sources` durchgaengig ueber Ids gefuehrt wird. Latent (0 von 456 Paaren).
- **A16/A17**, spezifiziert in AK-182 bis AK-194, **nicht gebaut**.

## Buchfuehrung des Directors

**Acht falsche Bestandsaussagen am 07./08.09.**, alle derselben Bauform: eine
Notiz wurde fuer eine Messung gehalten (`referenz/director-belege.md` B-22).
*Hier stand bis zum 08.09. "zwoelf" — die neunte derselben Bauform.* Die
Gegenmassnahmen sind **live**: `require-receipt.ps1`, `no-root-find.ps1`,
`remind-rules.ps1` (L-014), Pruefung 4 mit Quittung (L-015), "Regeln pflegen"
in `_rahmen.md` (L-017, L-018). Neu: **die fuenf Pruefungen stehen jetzt in
`templates/task.md`** — am 08.09. beschlossen, nie ausgefuehrt gewesen.

## Offen aus Zyklus 15 bis 17

QA-181 · QA-182 · QA-184 · **QA-186** · QA-188 · QA-190 · QA-191 · QA-193 ·
QA-195 · **QA-198 bis QA-202** · **QA-204 bis QA-209** · **SEC-025**.
Wortlaut, Adressat und Status je Befund in `qa/findings.md` bzw.
`security/findings.md` — **dort nachsehen, nicht hier**; diese Liste ist ein
Zeiger, kein Messwert. Reihenfolge: `docs/plan-restarbeiten.md`.

## Beim Nutzer — offen

**Vor dem ersten Release zu entscheiden (C-003, 07.09.2026).** Gebuendelt an
der Stufengrenze vor Bau und Release; sie halten den laufenden Zyklus **nicht**
auf, weil Bauen und Pruefen keine Weitergabe ist.
- **A-025, GRAU:** Die EXE traegt die bekannten Entschluesselungsschluessel.
  Privatgebrauch ist straflos, **mit dem ersten Release-Asset wird aus Nutzung
  Verbreitung** (§ 95a Abs. 3 UrhG, EULA 10(i)). Risiko tragen oder vorher
  anwaltlich klaeren? Alternative ohne das Risiko: Quellcode statt EXE.
- Bleibt das Repo dauerhaft oeffentlich (LGPL haengt daran, A-022)? · Soll das
  Release beworben werden? · Beruehrt die Weitergabe deinen Arbeitsvertrag
  (seit C-001 offen)? · Eigener Auftrag zu US-Recht (17 U.S.C. § 1201)?

**Aus dem Audit, Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 ·
F-G QA-170 (neue Funktion) · Streichliste je Tab (13 Vorschlaege,
`UI_SPEC` §8). Wortlaut in `qa/findings.md`.

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008 bis L-018;
projekteigen NH-001, NH-002.

**Nie geprueft:** Linux/macOS · eine echte Fremdinstallation.
