# Stand

2026-09-12, **pausiert auf Wunsch des Nutzers** (Claude-Neustart). Zyklus 20
laeuft, ist **nicht abgeschlossen**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf: `docs/archiv/state-bis-2026-09-12-zyklus19.md`. Befunde:
`qa/findings.md`, `security/findings.md` (nur Tabelle; Fliesstext in
`qa/verlauf.md`, `security/verlauf.md`). Register: `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md`. Reihenfolge: `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 12.09.): T ab **T-195** · QA ab **QA-234** ·
SEC ab **SEC-037** · AK ab **AK-264** · AD ab **AD-033** · OF ab **OF-34** ·
DR ab **DR-019** · R ab **R-007** · C ab **C-004** · A ab **A-033**. **AD-027
und OF-14 wurden nie vergeben** und werden nicht nachbelegt.

## Auftragslage (Nutzer, 12.09.2026)

Autonom durcharbeiten bis zum fertigen Produkt. **Kein Merge, kein Release,
keine Weitergabe** — bauen und pruefen ist keine Weitergabe. Angehalten wird
bei kritischem Sicherheitsbefund, Verdacht auf Datenverlust oder zwei Zyklen
ohne messbaren Fortschritt. **Danach:** Aufraeumlauf gegen toten Code, dann
Ingame-Test und eine weitere Feedbackrunde als letzte Ausbaustufe.

## HIER WEITERMACHEN — T-194 ist gebaut, aber nicht abgenommen

**`06be06e` liegt im Baum** (8 Dateien, +762/-133: `advisor/goals.py`,
`advisorbar.py`, `relicpicker.py`, fuenf Testdateien). Der `developer` wurde
auf Wunsch des Nutzers **mitten im Lauf gestoppt**, unmittelbar vor der
Fenstermessung. **Es fehlen: der Bericht, die Suitezahl, die Fenstermessung
und die Aussage, welchen der fuenf roten Waechter er gestrichen hat.**

**Erster Schritt der naechsten Sitzung:** `developer`, Stufe klein, mit
`06be06e` als Ausgangspunkt — **nichts nachbauen**, nur nachweisen: Suite mit
Datenbedingung, Fenstermessung gegen die Zahlen aus `UI_SPEC.md` §5.4
(Kartenzeile 210 → 228 px, `wanted_height` 1082 → 1136, **drei ganz sichtbare
Kartenzeilen bleiben drei**), und die Waechterfrage beantworten. Auftrag:
`docs/tasks/T-194.md`, Vorgabe: `UI_SPEC.md` §5.4 (AK-256 bis AK-263).

## Vor der Baurunde zu erledigen

1. **QA-231 — der feste Testabzug existiert nicht** (am Dateisystem geprueft).
   Jeder Fensterlauf zahlt 107 s bis 5 min Neuaufbau. `power-user` und
   `clean-room` sind beide Fensterlaeufe.
2. **QA-233 — zwei Testdateien laufen nur mit `--ignore`**
   (`test_extraction.py`, `test_hostile_gamedata.py`), weil
   `texture2ddecoder` fehlt. Ohne die `--ignore` gibt es **gar keine**
   Suitezahl. T-193 hat an genau diesem Pfad geaendert und nur nachgelesen.
3. **QA-232 — A7-Regression aus dem A8-Fix:** 24 englische Verweigerungen des
   Extraktionspfades kommen beim Nutzer als ein Sammelsatz an.
4. **Pruefphase auf eingefrorenem Stand** — `qa-engineer`, `security-reviewer`,
   UI-Review parallel. **Seit T-188 hat keine Pruefrolle den Code gesehen**,
   sechs Bauauftraege liegen dazwischen.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | laufend — 234 QA, 36 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt**, T-185 bestaetigt 0 kritisch / 0 hoch offen |
| A3-A5 | der Build-Berater | **gebaut**, T-114 am Artefakt bestaetigt |
| A6 | Oberflaeche blockiert nicht | **erfuellt und gemessen** |
| A7 | sagen, wo die Daten nichts hergeben | erfuellt, **aber QA-210 und QA-232 offen** |
| A8 | alles Englisch | **QA-211 behoben** — Bestaetigung durch QA steht aus |
| A9 | QA gegen ein gebautes Artefakt | offen — die Baurunde |
| A10 | jeder Tab nennt seine Frage | erfuellt |
| A11 | ohne Raten ans Ziel | offen — `power-user` am Artefakt |
| A12/A13 | Einheiten, Gestaltung | 4 bzw. 3 von 6 Tabs |
| A14 | QA je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | gebaut, Nachweis am Artefakt offen |
| A16 | best/worst case | **nicht gebaut**, keine Entscheidung getroffen |
| A17 | Ranking ohne Bezugswaffe | **rechnerisch fertig** (AK-191 woertlich erfuellt, 75 von 210 unterscheidbar); sichtbar gebaut in `06be06e`, **unbestaetigt** |

## Befunde

**234 QA-Zeilen:** 165 offen, 57 behoben, 6 geschlossen, 5 teilweise, 1
zurueckgestellt. **36 SEC-Zeilen:** 20 behoben, 10 offen, 6 geschlossen.

**Offene P1:** QA-095 (**Angriffskraft um 1/0,6 zu hoch** — Spiel rechnet
`floor(0,6 x rate)`, belegt ueber neun skalierungsfreie Waffen mal acht
Nightfarer; offen seit Zyklus 9, betrifft die Zahl, nicht die Rangfolge) ·
QA-228 (in `06be06e` gebaut, unbestaetigt) · QA-231.

**Auflagen:** 36 gefuehrt, 15 auf GELB. Vor der Baurunde `compliance-agent`
im Modus `pruefen`; was gelb bleibt, entscheidet der Nutzer.

## Beim Nutzer — offen

1. **SEC-026:** DLL-Seite haerten oder nicht. **Falle:** wer haertet, macht
   SEC-016/017/018 wieder scharf. Blockiert das Release, nicht den Bau.
   **SEC-036** haengt daneben, ist aber unabhaengig fixbar.
2. **C-003, vor der ersten Weitergabe:** A-025 (GRAU — die EXE traegt die
   Entschluesselungsschluessel) · Repo dauerhaft oeffentlich? · Release
   bewerben? · Arbeitsvertrag (C-001)? · US-Recht (17 U.S.C. § 1201)?
3. **Drei `widerspruechliche` Faelle** im AK-Register (`UI_SPEC.md` ab Z. 81).
4. **1320 px als Messumgebung** — gilt sie weiter, obwohl A14 sie als
   Startbreite aufgehoben hat? Betrifft AK-05, AK-160, AK-194.
5. **Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 · F-G QA-170.

## Beschlossen, nicht beauftragt

- **Senken-Waechter zu SEC-023** (12.09.): die Pfadhaelfte ist drin, die
  Sprachhaelfte braucht eine eigene Bauform — die AST-Sammlung fasst Literale,
  `str(exc)` ist keins (Widerspruch des `developer` in T-190).
- **Der SEC-031-Waechter misst die echte Kandidatenliste** statt `_steam_roots`
  zu stubben — sonst bleibt jede kuenftige feste Wurzel unsichtbar. Genau so
  ist SEC-036 durchgerutscht.
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183).
- **Pruefpunkt 13** ist in T-193 auf "gleiche Rechnung bei gleichen Eingaben"
  eingeengt worden. Ob die alte Zusage formal zurueckgezogen wird, ist offen.

## Eigene Fehler, Zyklus 20 — und die Regeln

Der Zuschnitt hat zweimal nicht getragen: T-191 brauchte **elf** Dateien statt
fuenf, T-193 **neun** — beide Male, weil ein Einzeiler Waechterdateien erzwang.
Beim Nachziehen von QA-225 bis QA-227 landete der neue Status in der
**Datumsspalte**, der alte blieb stehen. **QA-233 habe ich drei Auftraege lang
als Fussnote mitgeschleppt**, statt sie als Befund zu fuehren.

Regeln in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008 bis L-018,
projekteigen NH-001/NH-002. **Nie geprueft:** Linux/macOS, Fremdinstallation.
