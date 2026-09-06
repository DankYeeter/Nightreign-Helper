# Stand

2026-09-06, **Ende von Zyklus 13**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Einstieg fuer eine neue Session: `docs/handover-2026-09-06.md`.
Verlauf Zyklen 1-11: `docs/archiv/state-bis-2026-09-03.md`.
Reihenfolge: `docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`,
`security/findings.md`. Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-073** · QA ab **QA-171** · AK ab **AK-106** ·
DR ab **DR-019** · R ab **R-007** · projekteigene Regeln ab **NH-003**.

**Suite:** `-m "not slow"` **860 passed, 9 skipped, 5 deselected**;
`-m "slow"` **5 passed**. 18 registrierte Mutationen aus T-071, alle toetend
im Standardlauf.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**. **Die
Pruefung im laufenden Spiel macht der Nutzer ganz am Ende** — bis dahin
wartet kein Auftrag auf sie.

Eingedampft am 05.09.: **P6 auf zwei Punkte** (SEC-009 und die Label-Fabrik
SEC-019/015; SEC-011/016/017/018/020 gestrichen), **P5 auf einen Auftrag**
(QA-044/048/054 sind **eine** Wurzel: der Speicher adressiert einen Build
ueber einen nicht umkehrbaren abgeleiteten Schluessel, und die Migration setzt
ihren Marker zu frueh). **P7 bleibt vollstaendig** — ausdruecklicher
Nutzerentscheid: die Waechter sichern alles ab, was noch kommt.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit-Bericht mit priorisierten Befunden | weitgehend — 170 QA, 20 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | offen (SEC-009) |
| **A3-A6** | **der Build-Berater** | **offen — der ganze Rest der Arbeit** |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend |
| A8 | alles Englisch | haelt, ohne Waechter |
| A9 | QA gegen ein **gebautes Artefakt** | **nie geprueft** |
| A10 | jeder Tab nennt seine Frage | **erfuellt, 6 von 6** |
| A11 | ein Spieler kommt ohne Raten ans Ziel | **ein Satz fehlt** (QA-169) |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |

## Was Zyklus 12 und 13 gebracht haben

**Die Zahlenbasis ist erstmals gegen das Spiel belegt.** Faktor **0,6** in
`weapons.rate` (97 745 Zahlen mitgezogen, 17 224 bitgleich und jede davon ein
Multiplikator, 0 von 589 840 Bildschirmzahlen ausserhalb Abschneiden/Runden).
Katalysatoren zeigen **Spell power** statt physischer AR (84/84 und 28/28
exakt). Beides vom Nutzer freigegeben und per Retest abgenommen.

**Der Rechenkern des Beraters steht** (`nrplanner/advisor/`: `types`,
`evaluate`, `candidates`, `goals`, Qt-frei) und ist zweimal geprueft.
**AD-025** regelt, wo ein Vorbehalt wohnt: Verfahrenssatz in die Registry,
Laufbefund ins Ergebnis.

**Der Tab-Audit ist fachlich durch.** Drei falsche Zahlen berichtigt (die
Boss-Zeile stand bei den falschen Bossen — 7 von 10 zeigen jetzt eine
**belegte** Stufe, vorher null; `Avg chance` war ungewichtet; `Pools` zaehlte
keine Pools). Sichtbarkeit: alle zehn Nightlords ab **833** statt 1600 px ·
Fenster-Mindesthoehe 1225 → **513** · abgeschnittene Effektnamen 573 → **80** ·
Waffenkacheln beim Oeffnen **0 → 77** · Startbreite jetzt **aus den
Spaltenbreiten abgeleitet**, 0 von 11 Ueberschriften gekuerzt. Deckung:
fuenf Tabs hatten **keinen** Test, der Unsinn bemerkt haette — jetzt 40+
Anzeigetests.

**Fuenf `power-user`-Durchgaenge**, der Fortschritt ist messbar: Runde 1 zwei
"mit Muehe" und eine "teilweise"; Runde 5 **kein Abbruch, ein einziges
"geraten"**. Der Nachtlord oeffnet sich mit **einem** Klick statt vier.

## Der Rest — in dieser Reihenfolge

1. **QA-169 (P2, ein Satz):** `Comes with curse` ist die **einzige** Spalte,
   die der Erklaerabsatz auslaesst, und die einzige, bei der der Spieler
   raten musste. Danach **A11 mit einem sechsten `power-user`-Lauf
   bestaetigen** — sonst ist "erfuellt" meine Behauptung, keine Messung.
2. **P3, der Build-Berater** — der eigentliche Rest. **`docs/tasks/T-067.md`
   liegt fertig** (S7 Suche, S8 Begruendung). Danach S9 Worker, S10
   Oberflaeche, S11 Budget.
3. **P4** Save/Inventar · **P5** ein Auftrag · **P6** zwei Punkte ·
   **P7** vollstaendig · **P8** · **P9** mit **A9**.

## Offene Befunde, die niemandem zugeordnet sind

- **Wartet auf eine `ui-ux-designer`-Entscheidung:** QA-158 (Favoriten-
  Portraits ohne Namen), QA-159 (sechs Spalten nur im Tooltip erklaert —
  QA-169 ist eine Instanz davon), QA-160 (Filtermenues schneiden ihren
  eigenen Wert ab), QA-162, die Fokusmarke aus T-071 (liegt im selben warmen
  Kanal wie die Auswahl).
- **QA-157 ist groesser als aufgenommen:** der Laufzeit-Durchgang ueber 395
  Widgets findet **61** Stellen mit derselben Eigenschaft (6 `WeaponTile`,
  54 `RelicCard`, 1 `CustomRelicCard`), nicht fuenf.
- **QA-165/166:** zwei Instanzen kosten **keinen** Build (120/120), aber die
  Reihenfolge (3 von 120) und 34 von 60 Verstecken-Marken; `_migrate_keys`
  macht aus `Bleed build` den Namen `%42leed%20build`.
- **Zurueckgestellt:** QA-066, QA-123, AD-013.4 gegen `copy_key`,
  `CharaInitParam` wird nicht gelesen.

## Gesammelte Fragen an den App Designer

**Erledigt 06.09.:** F-A (`ruff`) — **Option B gewaehlt**, keine
Linter-Abhaengigkeit; die DoD-Zeile entfaellt, wo kein Linter konfiguriert
ist. Nicht erneut vorlegen.

- **F-B QA-096** — Raider x1,18 auf Greataxe/Great Hammer, **keine
  Param-Quelle** (Nenner: 252 Tabellen, 6,66 Mio. Zellen). Lv15-Messung.
- **F-C QA-097** — Cursed Claws x0,88 fuer alle ausser dem Revenant.
- **F-F QA-113** — vier Relikte wandeln Schadensart um, das Programm bewegt
  **exakt 0**. **Eine Ablesung entscheidet:** Grundwert 114, die drei
  Lesarten sagen **91 / 116 / 117**.
- **F-G QA-170 (neu)** — keine Sortierung ueber Waffenkategorien hinweg nach
  Angriffswert; der Spieler hat "die beste Waffe finden" **aufgegeben**. Waere
  eine **neue Funktion**, also Nicht-Ziel der A10-A14-Erweiterung.
- **Die Streichliste je Tab** (13 Vorschlaege in `UI_SPEC.md` §8).

## Regeln

In `docs/plan-restarbeiten.md`, nur dort gepflegt. Seit 06.09. teamweit:
**L-008** (Gegenbau: rot im Standardlauf · Erwartung nicht aus der bewachten
Stelle · Ueberlebender ist ein Befund) · **L-009** (jede Oberflaechenzahl
nennt ihre Messumgebung, jede Messung prueft, dass sie ihren Namen erreicht
hat) · **L-010** (Director: Medium, Werkzeug, Quelle vor jedem Dispatch) ·
**L-012** (Bildnachweise aus dem Fenster, nie vom Bildschirm) · **L-013**
(Absenz-Behauptung traegt ihren Nenner). Dazu **NH-001** (jede Arbeit hat eine
T-Nummer und eine Datei) und **NH-002** (keine Bildschirmabzuege).

**Nie geprueft:** ein gebautes Artefakt (A9) · Linux/macOS.
