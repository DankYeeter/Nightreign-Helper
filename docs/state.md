# Stand

2026-09-06, **Ende von Zyklus 14**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Einstieg fuer eine neue Session: `docs/handover-2026-09-06.md`.
Verlauf Zyklen 1-13: `docs/archiv/state-bis-2026-09-03.md`.
Reihenfolge: `docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`,
`security/findings.md`. Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-077** · QA ab **QA-180** · AK ab **AK-133** ·
DR ab **DR-019** · R ab **R-007** · projekteigene Regeln ab **NH-003**.

**Suite:** `-m "not slow"` **864 passed, 9 skipped, 5 deselected**;
`-m "slow"` **5 passed**. 18 registrierte Mutationen, alle toetend.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**. **Die
Pruefung im laufenden Spiel macht der Nutzer ganz am Ende.**

**Eingeschraenkt am 06.09.:** Der neue **Fragebogen vor dem Zyklus**
(`/director`, Nutzerentscheidung) haelt auch im autonomen Lauf an. Autonom
gilt damit **innerhalb** eines Zyklus, nicht ueber Zyklen hinweg — vor dem
ersten Auftrag eines neuen Zyklus steht der Director beim Nutzer.

P6 auf zwei Punkte (SEC-009, Label-Fabrik SEC-019/015) · P5 auf einen
Auftrag (QA-044/048/054 sind **eine** Wurzel) · P7 vollstaendig.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit-Bericht mit priorisierten Befunden | weitgehend — 179 QA, 20 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | offen (SEC-009) |
| **A3-A6** | **der Build-Berater** | **offen — der ganze Rest der Arbeit** |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend |
| A8 | alles Englisch | haelt, ohne Waechter |
| A9 | QA gegen ein **gebautes Artefakt** | **nie geprueft** |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ein Spieler kommt ohne Raten ans Ziel | **offen — neue Stelle** (QA-173) |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| **A15** | **Erststart fuehrt ohne fremde Hilfe zu Daten** | **neu 06.09., Spec liegt** |

## Was Zyklus 14 gebracht hat

**QA-169 ist behoben und am laufenden Fenster belegt** (T-073, T-076). Der
Erklaersatz zu `Comes with curse` steht ohne Hover im Absatz und wortgleich
im Kopf-Tooltip; eine Konstante speist beide, Rot-vorher je Verwendungsstelle
einzeln. **Wichtig fuer spaeter:** die vier Tests dazu laufen offscreen und
belegen nur den programmierten Text — den Sichtnachweis liefert T-076.

**A15 ist aufgenommen und spezifiziert.** Der Erststart endet heute in einer
Sackgasse, wenn die Automatik Spielordner oder Spielstand nicht findet — es
gibt **nirgends** einen Ordnerdialog. Spec: `UI_SPEC.md`, **AK-106 bis
AK-132**, kompletter englischer Wortlaut. Nutzerentscheid: Dialog **nur** bei
gescheiterter Automatik, fuer **Spielordner und Spielstand**. Director-
Festlegungen: aus dem Spielordner wird nichts verschoben, der Zielort des
Datenabzugs bleibt fest. Vier Designer-Rueckfragen vom Director entschieden
(kein nachtraegliches Aendern, kein aktives Anbieten des Spielstands, alter
Abzug wird gezeigt aber mit Datum, keine woertlichen Steam-Menuenamen).

**Der sechste `power-user`-Lauf misst A11 nicht** (T-075). Seine echten
Mausklicks kamen nicht an, er wich auf die Bedienungshilfen-Schnittstelle
aus; und er hat den Effekte-Tab nie geoeffnet, der Fix war nie auf dem
Schirm. Gueltig bleiben seine zwei Ratestellen: **QA-173** (Gefaess-Auswahl
unerklaert) und **QA-174** (Build beim Oeffnen schon befuellt).

**Aus beidem sind Teamregeln geworden** (Agenten-Repo `2ef09c1`):
Fragebogen vor dem Zyklus · L-010 von vier auf fuenf Pruefungen
(Faehigkeitsprobe gehoert in den Auftrag; Beweisstelle; Messreihen behalten
ihre Aufgabenliste) · vierte Sorgfaltspflicht des Directors · `power-user`
Schritt 0.

## Offen und niemandem zugeordnet

- **Die Klickfrage ist unentschieden.** T-076 konnte sie nicht beantworten:
  seine eigenen synthetischen Klicks erreichten **kein einziges Fenster**,
  auch nicht das des Windows-Rechners. Sein Urteil "Regression
  unwahrscheinlich" ist eine Abwaegung, keine Messung. **Eine echte
  Handprobe des Nutzers von zehn Sekunden entscheidet es.**
- **Wartet auf `ui-ux-designer`:** QA-158, QA-159 (jetzt 6 von 11 Spalten
  ohne Erklaerung im Absatz), QA-160, QA-162, QA-173, QA-174, QA-179, die
  Fokusmarke aus T-071.
- **Wartet auf `developer`:** QA-171 (alter Datenabzug kommentarlos, mit A15
  zu erledigen), QA-172 (Fluchspalte folgt der Filteransicht, 10 von 1064),
  QA-175 (Fenster teilweise ausserhalb des Bildschirms), QA-177.
- **QA-157 ist groesser als aufgenommen:** 61 Stellen, nicht fuenf.
- **QA-165/166:** Reihenfolge 3 von 120, 34 von 60 Verstecken-Marken;
  `_migrate_keys` macht aus `Bleed build` den Namen `%42leed%20build`.
- **Zurueckgestellt:** QA-066, QA-123, AD-013.4 gegen `copy_key`,
  `CharaInitParam` wird nicht gelesen.
- **Nebenwirkung von T-076:** der Lauf hat die laufende Programmkopie
  bedient (Held auf Guardian, Fenster verschoben und zweimal in der Groesse
  geaendert). Sie schreibt in denselben Registrierungsschluessel wie die
  Installation des Nutzers; moeglich, dass "zuletzt gewaehlter Build" fuer
  Guardian auf den Standard zurueckfiel. Kein Build geloescht, "Save" nie
  gedrueckt.

## Der Rest — in dieser Reihenfolge

1. **A11 schliessen:** QA-173 braucht eine `ui-ux-designer`-Entscheidung,
   danach ein `developer`-Auftrag, danach ein siebter Durchgang — mit
   **fester** Aufgabenliste und Faehigkeitsprobe als Schritt 0.
2. **P3, der Build-Berater** — der eigentliche Rest. **`docs/tasks/T-067.md`
   liegt fertig** (S7 Suche, S8 Begruendung). Danach S9 Worker, S10
   Oberflaeche, S11 Budget.
3. **A15 umsetzen** (Spec liegt), zusammen mit QA-171.
4. **P4** Save/Inventar · **P5** ein Auftrag · **P6** zwei Punkte ·
   **P7** vollstaendig · **P8** · **P9** mit **A9 und A15**.

## Gesammelte Fragen an den App Designer

**Erledigt 06.09.:** F-A (`ruff`) — Option B, kein Linter. Nicht erneut
vorlegen.

- **F-B QA-096** — Raider x1,18 auf Greataxe/Great Hammer, **keine
  Param-Quelle** (Nenner: 252 Tabellen, 6,66 Mio. Zellen). Lv15-Messung.
- **F-C QA-097** — Cursed Claws x0,88 fuer alle ausser dem Revenant.
- **F-F QA-113** — vier Relikte wandeln Schadensart um, das Programm bewegt
  **exakt 0**. **Eine Ablesung entscheidet:** Grundwert 114, die drei
  Lesarten sagen **91 / 116 / 117**.
- **F-G QA-170** — keine Sortierung ueber Waffenkategorien hinweg nach
  Angriffswert; der Spieler hat "die beste Waffe finden" aufgegeben. Waere
  eine **neue Funktion**.
- **F-H QA-172 (neu)** — widersprechen sich zwei Roheintraege desselben
  Effekts beim Fluch, was soll der Spieler sehen: die vorsichtige Aussage
  (*sometimes*) oder die Datenlage?
- **Die Streichliste je Tab** (13 Vorschlaege in `UI_SPEC.md` §8).

## Regeln

In `docs/plan-restarbeiten.md`, nur dort gepflegt. Teamweit: **L-008**
(Gegenbau) · **L-009** (Messumgebung) · **L-010** (Director: **fuenf**
Pruefungen vor jedem Dispatch) · **L-012** (Bildnachweise aus dem Fenster) ·
**L-013** (Absenz-Behauptung traegt ihren Nenner). Dazu **NH-001** (jede
Arbeit hat eine T-Nummer und eine Datei) und **NH-002** (keine
Bildschirmabzuege).

**Nie geprueft:** ein gebautes Artefakt (A9) · Linux/macOS · ein
angekommener echter Mausklick.
