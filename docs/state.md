# Stand

2026-09-05, **Zyklus 12 laufend**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — Merge gehoert dem Nutzer.
Verlauf Zyklen 1-11: `docs/archiv/state-bis-2026-09-03.md`.
Reihenfolge: `docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`,
`security/findings.md`. Berichte: `docs/berichte/T-###-<rolle>.md`.
Nummernkreise: T ab **T-053**, R ab **R-007**, QA ab **QA-125**, DR ab
**DR-013**, AK ab **AK-68**.

## Auftragslage (Nutzer, 03.09.2026, "Audit 3")

Alle offenen Punkte abarbeiten, autonom weiterlaufen, **erst zurueckkommen bei
einer echten Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**
(Liste unten), nicht einzeln vorgelegt. **Die Pruefung im laufenden Spiel
macht der Nutzer ganz am Ende** — bis dahin wartet kein Auftrag auf sie.
Obergrenze: die Liste P3-P9. Ein Kriterium aus `GOAL.md` gilt erst als
erfuellt, wenn der `qa-engineer` es geprueft hat.

Die zweite Session ("Scaling Questions") hat abgegeben; Handover in
`docs/handover-scaling-2026-09-03.md`. Ihre Ergebnisse sind unten eingearbeitet.

## Was in Zyklus 12 fertig und abgenommen ist

- **T-037 Rechenkern des Beraters.** `nrplanner/advisor/` (`types`, `evaluate`,
  `candidates`, `goals`), Qt-frei. Suite 291 -> 398.
- **T-041 QA-Erstdurchlauf.** Kein Blocker; 15 von 15 Mutationen unabhaengig
  nachgefahren, Regression am Fenster **null**. Befunde QA-100 bis QA-112.
- **T-045 Faktor 0,6** (Nutzerentscheid F4). Belegt: 97 745 Zahlen um 0,6
  mitgezogen, 17 224 bitgleich (jede ein Multiplikator), 870 um 2-3 ULP
  daneben (alle Summen ueber Schadensarten), **0 von 589 840** Bildschirm-
  zahlen ausserhalb Abschneiden/Runden.
- **T-046 Katalysator-Kennzahl** (Nutzerentscheid "replace physical attack
  with spell power"). 84/84 und 28/28 exakt, **0** Nicht-Katalysator-Werte
  bewegt. Carian Regal Scepter reiht jetzt vor Rotten Crystal Staff.
- **T-051 Retest: alle 4 + 6 Abnahmepunkte erbracht.** Der zuvor offene Punkt
  ist geschlossen — Wylder Lv12 / Dagger zeigt **74** auf Kachel, Tafel und
  Arsenal-Tab, gemessen an einer echten headless `Planner`-Instanz.
- **T-047 `architect`: AD-025** plus Praezisierungen zu AD-004, AD-009,
  AD-010, AD-016. Kern: die Klasse eines Vorbehalts ist Eigenschaft seines
  **Wohnorts**, nicht seines Wortlauts — Verfahrenssatz in die Registry
  (`Goal.scope`), Laufbefund ins Ergebnis (`*.unknowns`).
- **T-052 Design-Review** am laufenden Fenster: DR-008 bis DR-012,
  AK-63 bis AK-67, Screenshots unter `docs/screenshots/2026-09-05/`.

Suite vor T-048: **563 passed, 5 deselected**; `-m "slow"` 5 passed.

## In Arbeit und als Naechstes

**Neuer Nutzerauftrag 05.09.2026: Inhaltsaudit der sechs Tabs** —
`GOAL.md` **A10 bis A14**. Nicht nur Formatierung: zuerst, ob der Inhalt eine
benennbare Spielerfrage beantwortet, dann Verstaendlichkeit ohne Vorwissen,
dann Gestaltung. `Build planner` ist ausgenommen ("der erste passt").
**Abschluss-Deliverable an den Nutzer: eine Streichliste je Tab** — was wuerde
ich entfernen, und was verliert ein Spieler dadurch. Streichen selbst ist
seine Entscheidung, nicht meine.

Reihenfolge, sequenziell, nie zwei Agenten auf demselben Code:

| | | |
|---|---|---|
| **T-048** `developer` | Ergebnisform nach AD-025, QA-100 (der Waechter ueber dem Fenster faengt heute keinen seiner Gegenbauten), QA-101/113/114/115/120/124 | laeuft |
| **T-053** `developer` | Oberflaeche: DR-008 bis DR-012, AK-63 bis AK-67, QA-117/119/121 | geschrieben |
| **T-054** `power-user` + **T-055** `qa-engineer` | die sechs Tabs, parallel und mit verschiedenen Fragen: kommt ein Mensch ans Ziel — stimmt das Gezeigte | geschrieben |
| dann | `ui-ux-designer` (Spec) -> `developer` -> Retest, so oft wie noetig | |
| dann | P3 weiter: S7 Suche · S8 Erklaerung · S9 Worker · S10 · S11 | |
| dann | P4 bis P9 | |

**T-053 laeuft vor T-054/T-055**, sonst meldet der `power-user` Fehler, die
das Design-Review schon kennt.

## Entscheidungen des Directors in Zyklus 12

- **AK-47 ist eingetreten, nicht geaendert** — QA-018 geschlossen, `unverified`
  entfaellt; der Vorbehaltssatz blieb, bis T-045 ihn durch den Geltungsbereich
  ersetzte.
- **QA-101: `damage.equipped` bleibt.** Die Behauptung "die Rangfolge waere bei
  `candidate` dieselbe" ist **widerlegt** (−12,36 gegen +21,36, Reihenfolge
  gedreht, 10 von 309 Relikten). Entscheidung richtiger als ihre Begruendung.
- **D1 bis D4** (Vorbehalts-Klassen, konditionale Zeile, positionsabhaengiger
  Cache-Schluessel, doppelte Pruefpunktnummer) — vom `architect` in AD-025 und
  vier Praezisierungen ausgearbeitet. Er hat **zwei meiner Vorgaben
  korrigiert**, beide zu Recht: der Massstab brauchte "und die Frage, ob er
  gilt", und meine Begruendung fuer D3 trug nicht (die Entscheidung schon).
- **QA-115: das fehlende Messskript wird gebaut**, nicht der Kommentar
  entschaerft — der `qa-engineer` hat bestaetigt, dass die per-Typ-Aussage
  sonst unpruefbar bleibt.
- **`ratios.py` bleibt im Repo** — es macht die Abnahmezahl nachfahrbar,
  genau das, dessen Fehlen QA-115 zum Befund macht.
- **QA-113 wird benannt, nicht gefuellt.** Die Einbauhoehe ist ohne
  Spielmessung nicht entscheidbar und wird nicht geraten (F-F).
- **Kein `security-reviewer` in Zyklus 12** — kein Datei-, Socket-, Shell- oder
  Pfadzugriff, keine neue Abhaengigkeit. Bewusst uebersprungen.

## Kleine offene Punkte, die im naechsten developer-Lauf mitlaufen

- **Platzhalter ersetzen:** `[wording pending: QA-113]` in
  `advisor/candidates.py` — der Wortlaut ist seit 05.09. in **AK-67**
  festgelegt ("{n} of your relics change what damage type your starting
  armament deals ..."). AK-67 erlaubt jetzt **drei** Saetze statt zwei.
- **`ARCHITECTURE.md` nennt `held_fingerprint` an vier Stellen ausserhalb
  von Nachtrag VI weiter als geltend** (Z. 1438, 1627, 2434, 2468) — gehoert
  dem `architect`, ueberholte Zusicherung.
- **`model.Build.level`** ist neu (fuer QA-124 noetig) und im Entwurf noch
  nicht nachgetragen — ebenfalls `architect`.
- **`mutate.py::newline_of`** begruendet sich mit CRLF in `app.py`; der Baum
  ist durchgehend LF. Code richtig, Begruendung veraltet.

## Beschlossen, nicht beauftragt

- **`ruff`** (vierte Erwaehnung) — ohne Linter ist "Linter sauber" in der DoD
  jeder Rolle unpruefbar. Frage F-A.
- **AD-013.4 gegen `inventory.copy_key`** — ohne lesbare Handles waere **jeder**
  Pool leer (QA-108). Latent: 0 von 309.
- **`CharaInitParam` liest der Extractor nicht** (Startausruestung aller zehn
  Nightfarer) — beruehrt AD-020.3, kein Beleg fuer einen Fehler.
- **QA-066** (`damage.Rating` nicht hashbar) bleibt offen, P7 — im Berater
  umgangen, nicht behoben.
- **QA-123** (Arsenal-Messstrecke fuer 6 von 1793 Waffen blind) — P7.

## Gesammelte Fragen an den App Designer (fuer das Sessionende)

- **F-A `ruff` als Linter aufnehmen?** Neue Abhaengigkeit, zieht `researcher`
  und `compliance-agent` (`lizenzen`) nach.
- **F-B QA-096** — Raider trifft mit Greataxe/Great Hammer exakt x1,18 (25/25),
  **keine Param-Quelle** (Negativliste mit Nenner: 252 Tabellen, 6,66 Mio.
  Zellen). Der Nutzer misst auf Lv15. Bestaetigt die Messung ihn, ist zu
  entscheiden, ob eine Zahl ohne Beleg eingebaut wird — A7-Abwaegung.
- **F-C QA-097** — Cursed Claws x0,88 fuer jeden ausser dem Revenant (8/8).
  Spielregel oder geschaetzte Zellen der Fan-Quelle? Nutzermessung Lv15.
- **F-F QA-113, die Einbauhoehe.** Vier Relikte tragen in den Params eine echte
  Umwandlung, das Programm bewegt dafuer **exakt 0**, waehrend die Karte die
  Zahlen nennt. Drei Lesarten; **eine Ablesung im Spiel entscheidet**:
  Grundwert 114, die Lesarten sagen **91 / 116 / 117**. Gehoert in dieselbe
  Lv15-Runde wie F-B und F-C.

## Regeln und Ungeprueftes

Arbeitsregeln stehen wortgleich in `docs/plan-restarbeiten.md` und werden nur
dort gepflegt: toetende Mutation je Waechter · ungerundete Zahl fuer
Charakterisierungen · Messstrecke benutzen, nicht neu bauen · **jede
Zusicherung nennt ihren Geltungsbereich**.

Nie geprueft: die Oberflaeche als **benutztes Programm** (`power-user`, nach
P9) · ein **gebautes Artefakt** (GOAL A9) · Linux/macOS (Windows-only).
