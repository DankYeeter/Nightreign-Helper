# Stand

2026-09-07, **mitten in Zyklus 15**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf: `docs/archiv/state-bis-2026-09-03.md`. Reihenfolge:
`docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`, `security/findings.md`.
Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-090** · QA ab **QA-187** · AK ab **AK-182** ·
AD ab **AD-027** · DR ab **DR-019** · R ab **R-007** · NH ab **NH-003**.
**Suite:** **1107 passed, 9 skipped, 5 deselected** (`not slow`, T-088,
07.09.); `slow` 5 passed.

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
| A2 | kritisch/hoch behoben oder zurueckgestellt | offen (SEC-009) |
| A3-A6 | der Build-Berater | **in Arbeit** — Kern und Leiste fertig, Slotkarte und Picker offen |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend; **QA-186 ist ein neuer Bruch** |
| A8 | alles Englisch | haelt, ohne Waechter |
| A9 | QA gegen ein **gebautes Artefakt** | **nie geprueft**; es gibt bis heute keine EXE |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ohne Raten ans Ziel | offen (QA-173); **messbar, seit die Klickfrage beantwortet ist** |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | Spec liegt (AK-106-132), Umsetzung offen |

## Zyklus 15 bisher

Gebaut: **Advisor bar** (T-083) · Spec fuer Slotkarte und Picker (T-084/T-086,
AK-162 bis AK-181) · **AD-026** (T-085) · Docstring von `not_counted` mit zwei
Regressionsfaellen (T-087/T-088). Was weiterwirkt, steht im Archiv.

## Entscheidungen des Directors, 07.09.2026

- **4.10 bleibt ohne Erzeuger.** Beide Zielrichtungen liefern immer eine Zahl;
  einen Ausloeser zu bauen hiesse, ein Kriterium zu erfinden — das verbietet
  A7. **AK-20 ist im Test pruefbar, nicht am echten Lauf**, die QA sucht nicht
  danach. Wieder aufmachen bei einer dritten Zielrichtung.
- **S10b geteilt:** T-089 zeichnet und erklaert, T-090 wendet an und haelt
  fest. Anwenden ist **eine** Sache mit **einem** Rueckgaengig-Modell; der
  `Use`-Knopf wird in T-089 **nicht** gezeichnet, auch nicht wirkungslos.
- **QA-186 nach der Slotkarte** — er liegt im Build planner, unabhaengig von S10.

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
  `sources` durchgaengig ueber Ids gefuehrt wird. **QA-180 ist die Instanz und
  offen — A5 ist deshalb heute nicht erfuellt.**

## Offen und niemandem zugeordnet

- **`ui-ux-designer`:** QA-158, QA-159, QA-160, QA-162, QA-173, QA-174,
  QA-179, die Fokusmarke aus T-071. Aus T-083 dazu: §4 hat keine Zeile fuer
  "Vorschlag hat seinen Build ueberlebt"; 4.9 und 4.11 koennen zusammen
  zutreffen; der Plural von 4.11 ist ungeprueft; die Statuszeile bekommt bei
  1320 px nur 158 px; der gepinnte obere Block.
- **`developer`:** QA-171 (mit A15), QA-172, QA-175, QA-177, QA-180, QA-186 ·
  Debt `app.py:3294` (Tooltip ohne `<span>`, `&` erscheint als `&amp;`).
- **QA-157** ist groesser als aufgenommen: 61 Stellen, nicht fuenf.
  **QA-165/166:** Reihenfolge 3 von 120, 34 von 60 Verstecken-Marken.
- **Zurueckgestellt:** QA-066, QA-123, AD-013.4 gegen `copy_key`,
  `CharaInitParam` wird nicht gelesen.

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
  **exakt 0**. Eine Ablesung entscheidet: Grundwert 114, die drei Lesarten
  sagen **91 / 116 / 117**.
- **F-G QA-170** keine Sortierung ueber Waffenkategorien hinweg — waere eine
  **neue Funktion** · **die Streichliste je Tab** (13 Vorschlaege, `UI_SPEC` §8).

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
