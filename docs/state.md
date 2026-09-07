# Stand

2026-09-07, **mitten in Zyklus 15**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf: `docs/archiv/state-bis-2026-09-03.md`. Reihenfolge:
`docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`, `security/findings.md`.
Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-090** · QA ab **QA-187** · AK ab **AK-182** ·
AD ab **AD-027** · DR ab **DR-019** · R ab **R-007** · NH ab **NH-003**.
**Suite:** **1256 passed, 9 skipped, 0 failed** (T-102, 07.09.). Seit
`4431c7a` laeuft sie parallel: `pytest -n auto` **127 s** statt 840 s seriell,
Faktor 6,6, Namensvergleich ueber 1265 Faelle ohne Abweichung. **`-n auto` ist
bewusst keine Voreinstellung** — eine gezielt genannte Einzeldatei stiege von
1,2 auf 4,0 s, und genau die verlangt die Gegenproben-Regel.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**. **Die Pruefung
im laufenden Spiel macht der Nutzer ganz am Ende.** Der Fragebogen vor dem
Zyklus haelt auch im autonomen Lauf an — autonom gilt **innerhalb** eines
Zyklus. P6 auf zwei Punkte (SEC-009, SEC-019/015) · P5 auf einen Auftrag
(QA-044/048/054 sind **eine** Wurzel) · P7 vollstaendig.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | weitgehend — 186 QA, 20 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | offen (SEC-009); SEC-022 und SEC-024 behoben |
| A3-A6 | der Build-Berater | **gebaut** — Kern, Leiste, Slotkarte, `Why`-Dialog, Anwenden/Halten, Picker. QA: sechsmal CONCERNS |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend; **QA-186 ist ein neuer Bruch** |
| A8 | alles Englisch | haelt, ohne Waechter |
| A9 | QA gegen ein **gebautes Artefakt** | **nie geprueft**; es gibt bis heute keine EXE |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ohne Raten ans Ziel | offen (QA-173); **messbar, seit die Klickfrage beantwortet ist** |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | Spec liegt (AK-106-132), Umsetzung offen |

## Beschlossen, nicht beauftragt

- **D-2** Fluch ohne Zahlenwirkung **muss genannt werden** — eigenes Feld
  `curses_without_a_figure`, nicht `not_counted` verbreitern. 36 von 309
  Relikten, Wortlaut AK-138 bis AK-141. **In T-089 beauftragt.**
- **D-1** `performance-tuner` auf `model.compute` (94 % der 941,6 ms) — in
  **S11**, Erstlauf im Projekt, also opus.
- **D-11** Doppeltes Zahlenformat: Waechter, AK-136 verlangt, dass beide Orte
  dasselbe schreiben.
- **`compute_resistances`** — Zurueckstellung wieder offen: T-080 zaehlt drei
  Fluche und **33 stumme positive Effekte**, zusammen **36 Zeilen auf einem
  Spielstand**. Vor der Bestaetigung nachmessen; wieder aufmachen, sobald eine
  Zielrichtung Widerstaende rankt.
- **QA-185, Klassenmassnahme:** vor der naechsten Aenderung entscheiden, ob
  `sources` durchgaengig ueber Ids gefuehrt wird. QA-185 bleibt latent (0 von
  456 Paaren). **QA-180 ist behoben** (`90ff81d`) — die frueher hier stehende
  Aussage "A5 ist deshalb heute nicht erfuellt" war ein Buchfuehrungsfehler
  des Directors und ist mit T-095 widerlegt.

## Stand am Ende des 07.09.2026

Der Build-Berater ist im Build planner **vollstaendig** und vom App Designer
am laufenden Fenster gesehen; seine einzige Aenderung (beide Spitzenreiter
oben) ist gebaut. Die Pruefphase ist gelaufen: QA **sechsmal CONCERNS**,
Sicherheit **FAIL** wegen SEC-022 — beide Hoch-Befunde (SEC-022, SEC-024) sind
seitdem behoben und belegt.

**Neu entschieden und noch nicht gebaut:** A16 (schlechtester/bester Fall) und
A17 (Rangfolge ohne Bezugswaffe), spezifiziert in AK-182 bis AK-194.

**Offen aus der Pruefphase:** QA-181 (Stacking unbewacht), QA-186, QA-190,
QA-191 (acht Nightfarer ungetestet), QA-192 (kein Englisch-Waechter), QA-193,
QA-195 bis QA-197, SEC-021, SEC-023.

**Beim Director, nicht beim Code:** QA-196 (ein Worktree stand sechs Tage
zurueck) und QA-197 (der Scratchpad ist zwischen gleichzeitigen Rollen
geteilt). Beide treffen die parallele Arbeitsweise selbst und sind zu klaeren,
bevor der naechste Worktree-Auftrag rausgeht.

**Im Agenten-Repo, PR `claude-agent-team#1`:** der gemeinsame Rahmen
(`agents/_rahmen.md`), auf den alle Rollen ausser dem `power-user` verweisen,
plus ein Selbsttest, der den Verweis erzwingt. Anlass: beim Umzug des Rahmens
aus der Auftragsvorlage in die Rollendefinitionen fielen **sechs von sieben
Regeln** aus — drei kamen in null von fuenfzehn Rollen an —, und vier Stunden
spaeter starb ein Lauf an genau der Regel, die verlorenging.

## Der Rest — in dieser Reihenfolge

1. **T-089** Vorschlagsblock und `Why`-Dialog (liegt geschrieben bereit).
2. **T-090** Anwenden und Festhalten.
3. **S10c** der Relic Picker als Hauptweg (AD-018, AK-41-53, AK-62).
4. **Pruefphase parallel** — `qa-engineer`, `security-reviewer`,
   `ui-ux-designer` (Review). Erst wenn der Stand eingefroren ist.
5. **S11** Budget mit dem `performance-tuner`.
6. **A11 schliessen:** QA-173 entscheiden, beheben, siebter `power-user`-Lauf
   mit **fester** Aufgabenliste und Faehigkeitsprobe als Schritt 0.
7. **A15** mit QA-171. Dann **QA-186**.
8. **P4** · **P5** · **P6** · **P7** · **P8** · **P9** mit **A9 und A15**.

## Beim Nutzer — offen

**Erledigt 06.09.:** F-A (kein Linter), F-I, F-J. **07.09.:** die Klickfrage
(Handprobe: Klicks kommen an, Tooltip beim Ueberfahren) · zwei Teamregeln.

- **F-B QA-096** Raider x1,18 auf Greataxe/Great Hammer, **keine Param-Quelle**
  (252 Tabellen, 6,66 Mio. Zellen) · **F-C QA-097** Cursed Claws x0,88 fuer
  alle ausser dem Revenant. Beide: Lv15-Messung im Spiel.
- **F-F QA-113** vier Relikte wandeln Schadensart um, das Programm bewegt
  **exakt 0**. Eine Ablesung entscheidet: Grundwert 114, drei Lesarten sagen
  **91 / 116 / 117**.
- **F-G QA-170** keine Sortierung ueber Waffenkategorien hinweg, waere eine
  **neue Funktion** · **Streichliste je Tab** (13 Vorschlaege, `UI_SPEC` §8).

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008, L-009,
L-010 (fuenf Pruefungen), L-012, L-013; projekteigen NH-001, NH-002.
**Neu 07.09.2026, vom Nutzer angenommen, Agenten-Repo `a2db0db`**, beide im
Rahmenblock von `templates/task.md` und damit teamweit: **kein Hintergrundlauf,
auf dessen Ende der Agent wartet** (acht Berichte ohne Uebergabe-Kontrakt, der
juengste bei 79 von 150 Zuegen — nicht die Zugschwelle) · **ein Feldname ist
keine Beschreibung**, drei Gegenproben vor jedem Nutzertext an einem Datenfeld
(Anlass QA-186).

**Nie geprueft:** ein gebautes Artefakt (A9) · Linux/macOS.
