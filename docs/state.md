# Stand

2026-09-06, **Ende von Zyklus 14**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Einstieg fuer eine neue Session: `docs/handover-2026-09-06.md`.
Verlauf Zyklen 1-13: `docs/archiv/state-bis-2026-09-03.md`.
Reihenfolge: `docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`,
`security/findings.md`. Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-077** · QA ab **QA-180** · AK ab **AK-133** ·
DR ab **DR-019** · R ab **R-007** · projekteigene Regeln ab **NH-003**.

**Suite:** **864 passed, 9 skipped, 5 deselected** (`not slow`), `slow`
5 passed. 18 Mutationen, alle toetend.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**. **Die
Pruefung im laufenden Spiel macht der Nutzer ganz am Ende.**

**Eingeschraenkt am 06.09.:** Der neue **Fragebogen vor dem Zyklus**
(`/director`, Nutzerentscheidung) haelt auch im autonomen Lauf an. Autonom
gilt damit **innerhalb** eines Zyklus, nicht ueber Zyklen hinweg — vor dem
ersten Auftrag eines neuen Zyklus steht der Director beim Nutzer.

P6 auf zwei Punkte (SEC-009, SEC-019/015) · P5 auf einen Auftrag
(QA-044/048/054 sind **eine** Wurzel) · P7 vollstaendig.

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

**QA-169 ist behoben und am laufenden Fenster belegt** (T-073, T-076): der
Satz zu `Comes with curse` steht ohne Hover im Absatz und wortgleich im
Tooltip, eine Konstante speist beide. **Fuer spaeter:** die vier Tests dazu
laufen offscreen und belegen nur den programmierten Text.

**A15 ist aufgenommen und spezifiziert.** Der Erststart endet heute in einer
Sackgasse, wenn die Automatik Spielordner oder Spielstand nicht findet — es
gibt **nirgends** einen Ordnerdialog. Spec: `UI_SPEC.md`, **AK-106 bis
AK-132**. Dialog **nur** bei gescheiterter Automatik, fuer beide Pfade; aus
dem Spielordner wird nichts verschoben, der Zielort bleibt fest. Vier
Designer-Rueckfragen sind im Bericht zu T-074 entschieden.

**Der sechste `power-user`-Lauf misst A11 nicht** (T-075): seine Klicks kamen
nicht an, und er hat den Effekte-Tab nie geoeffnet. Gueltig bleiben zwei
Ratestellen — **QA-173**, **QA-174**.

**Daraus wurden Teamregeln** (Agenten-Repo `2ef09c1`): Fragebogen vor dem
Zyklus · L-010 auf fuenf Pruefungen · `power-user` Schritt 0.

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
- **Nebenwirkung von T-076:** der Lauf hat die laufende Kopie bedient (Held,
  Fenstergroesse). Sie schreibt in den Registrierungsschluessel der echten
  Installation; moeglich, dass "zuletzt gewaehlter Build" fuer Guardian auf
  den Standard zurueckfiel. Kein Build geloescht, "Save" nie gedrueckt.

## Beschlossen, nicht beauftragt

Aus T-067, vom Director entschieden am 06.09.2026:

- **D-2** Ein Fluch, der im Ergebnis keine Zahl bewegt, **muss trotzdem
  genannt werden** (`UI_SPEC` §3.2: ein Preis, der erst nach dem Anwenden
  sichtbar wird, ist eine Falle). Weg: **eigenes Feld auf `AdvisorResult`**,
  nicht `not_counted` verbreitern. Betrifft 36 von 309 Relikten, darunter
  drei mit `All Resistances Down`, das echte Zahlen bewegt und **in keinem
  Feld** auftaucht. Wortlaut vom `ui-ux-designer`, Umsetzung eigener Auftrag.
- **D-3** `not_counted` behaelt die Bedeutung aus **AD-010** (konditionale
  Effekte). Die Menge "bewegt keine Zahl" ist eine **andere** und bekommt das
  Feld aus D-2. `UI_SPEC` 4.9 ist entsprechend zu korrigieren.
- **D-4** `SlotPool` bekommt ein `rank_by`. Ohne das kann die Suche nicht
  pruefen, dass Pools und Bewertung dieselbe Zielrichtung meinen — heute eine
  ungeprueft zugesagte S9-Eigenschaft. Kleiner Auftrag, mit S9.
- **D-5** **Kein** `top_n`-Stellrad. Die Beam-Breite W bleibt die Zahl der
  Endzustaende; AD-003.5 bekommt eine Korrekturnotiz.
- **D-1** `performance-tuner` bekommt `model.compute` (94 % der 941,6 ms),
  nicht die Fassade — aber **in S11**, nicht jetzt: vor S10 gemessen zu
  optimieren misst einen Stand, den es so nicht mehr geben wird. Erstlauf im
  Projekt, also opus.
- **D-10** Der Maskierungshinweis (`html.escape`, `setTextFormat`) geht
  **woertlich** in den S10-Auftrag.
- **D-11** Doppelte Zahlenformatierung: akzeptiert, zurueckgestellt bis S10.
  **Der `ui-ux-designer` weist zu Recht darauf hin, dass AK-136 sie teurer
  macht** — beide Orte muessen nachweisbar dasselbe schreiben. Bleibt
  zurueckgestellt, aber mit Waechter im S10-Auftrag.

Aus T-078, entschieden am 06.09.2026:

- **Die AD-015-Pflichtzeile wird mit der Zahlzeile desselben Fluchs
  verschmolzen** und wandert aus `unknowns` in die Slotgruppe. Zugestimmt:
  dieselbe Sache an zwei Orten ist die Fehlerklasse QA-082/QA-087, und der
  Reliktname der zweiten Zeile ist ueberfluessig, weil die Gruppe ihn traegt.
  **AD-015 bekommt eine Korrekturnotiz**, bevor S10 gebaut wird.
- **Die Datenform bleibt beim `developer`.** Verbindlich ist die
  **Eigenschaft** (jede Zeile erreicht die Anzeige mit Slotnummer,
  Fluch-Kennzeichen und den zwei Zaehlungen), nicht die Bauart. Ein neuer Typ
  in `types.py` liegt in seinem Ermessen; dafuer braucht es keinen
  `architect`.
- **`model.compute_resistances` schreibt vorerst nicht nach `sources`** —
  zurueckgestellt mit Grund: `_DAMAGE_TAKEN_SCOPE` nimmt Widerstaende
  ausdruecklich aus der Kennzahl heraus, also waere eine Quelle ohne
  Rankingwirkung irrefuehrend. Fuellung (3) der Fluchzeile deckt die drei
  Relikte ehrlich ab. **Wieder aufzumachen**, sobald eine Zielrichtung
  Widerstaende rankt.
- **Der Knopf heisst `Optimize`.** T-024 hat ihn so benannt, nur die
  Zustandstabelle 4.1-4.14 spricht noch von `Suggest`. Sie wird im
  S10-Auftrag mitkorrigiert, nicht danach.

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
- **F-I (neu, T-078)** — Wie viel Fluch vertraegt die Slotkarte? Die Spec
  zeigt **jeden** Fluch im Vorschlagsblock, auch den ohne Zahl: bei drei
  Fluchrollen drei rote Zeilen in einer sonst vierzeiligen Karte. Ruhiger
  waere, stumme Fluche erst im `Why`-Dialog zu zeigen — das verstiesse aber
  gegen "der Preis darf nicht erst nach dem Anwenden sichtbar werden".
- **F-J (neu, T-078)** — Soll auch ein **Effekt** ohne Zahlenwirkung beim
  Namen genannt werden, so wie ein Fluch? Heute sagt die Zeile nur
  "3 of its 5 effects moved a number in this build" und verschweigt, welche
  zwei nichts bewegt haben.
- **Die Streichliste je Tab** (13 Vorschlaege in `UI_SPEC.md` §8).

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008, L-009,
L-010 (jetzt **fuenf** Pruefungen), L-012, L-013; projekteigen NH-001,
NH-002.

**Nie geprueft:** ein gebautes Artefakt (A9) · Linux/macOS · ein
angekommener echter Mausklick.
