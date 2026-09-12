# Stand

2026-09-12, **Zyklus 19 abgeschlossen** (Dokumentenstruktur). Branch
`docs/audit-and-advisor-design`, `main` geschuetzt, PR #16 offen — **Merge
gehoert dem Nutzer.** Verlauf: `docs/archiv/state-bis-2026-09-12.md`.
Reihenfolge: `docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`,
`security/findings.md` (nur noch Tabelle; Fliesstext in `qa/verlauf.md`,
`security/verlauf.md`). Register: `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md`.
**Nummernkreise** (nachgezaehlt 12.09.): T ab **T-187** · QA ab **QA-225** ·
SEC ab **SEC-037** · AK ab **AK-256** · AD ab **AD-032** · OF ab **OF-34** ·
DR ab **DR-019** · R ab **R-007** · NH ab **NH-003** · C ab **C-004** ·
A (Auflagen) ab **A-033**. **AD-027 und OF-14 wurden nie vergeben** und werden
nicht nachbelegt (T-182/T-183).

## Auftragslage (Nutzer, 12.09.2026)

Durcharbeiten, bis die Kriterien aus `GOAL.md` erfuellt sind. **Kein Merge,
kein Release, keine Weitergabe** — bauen und pruefen ist keine Weitergabe.
Angehalten wird bei kritischem Sicherheitsbefund, Verdacht auf Datenverlust
oder zwei Zyklen ohne messbaren Fortschritt.

**Danach, vom Nutzer festgelegt:** Aufraeumlauf gegen toten Code, dann als
letzte Ausbaustufe der Ingame-Test und eine weitere Feedbackrunde.

## Was Zyklus 19 gebracht hat

Lesekosten der vier Dateien, die jede Rolle aufmacht: **18.960 → 9.818
Zeilen**, dazu 515 Zeilen Register, die die grosse Datei oft ersetzen.

| Datei | vorher | nachher |
|---|---|---|
| `UI_SPEC.md` | 9639 | **3392** (7 Bereiche, 0 Datumsabschnitte, 255 AK) |
| `ARCHITECTURE.md` | 5972 | 6129, aber thematisch — Median-Leseabstand **2494 → 325** |
| `qa/findings.md` | 2754 | **244** |
| `security/findings.md` | 595 | **53** |

Beide Verlaufsdateien sind gegen ihren Altstand **bytegleich** geprueft
(`diff -q`), nichts gestrichen. 217 Auftragsdateien und Berichte unter T-140
liegen in `docs/archiv/`.

**Die Befundtabellen sind wieder die Wahrheit** — seit rund Zyklus 10 nicht
fortgeschrieben, 36 QA- und 10 SEC-Nummern standen nur im Fliesstext. Jetzt
227 QA-Zeilen (160 offen, 53 behoben, 6 geschlossen, 5 teilweise, 1
zurueckgestellt, 1 waived, 1 unklar) und 36 SEC-Zeilen (20 behoben, 10 offen,
6 geschlossen), jede Statuszelle mit festem Anfangswort — greppbar statt
lesbar. **Erstmals belegt** ist die OF-Bilanz: von 32 offenen Fragen sind **12
wirklich offen** (OF-3, 10, 11, 16, 18, 21, 22, 23, 27, 28, 29, 32), 17
beantwortet, eine mit Rest, eine unklar. Bei den AD kein echter Widerspruch —
aber AD-008 haengt an OF-22.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | laufend — 227 QA, 36 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt**, T-160; T-185 bestaetigt 0 kritisch, 0 hoch offen |
| A3-A5 | der Build-Berater | **gebaut**, T-114 am Artefakt bestaetigt |
| A6 | Oberflaeche blockiert nicht | **erfuellt und gemessen** |
| A7 | sagen, wo die Daten nichts hergeben | erfuellt, **aber QA-210 ist ein A7-Bruch** |
| A8 | alles Englisch | Waechter steht, **QA-211 offen** |
| A9 | QA gegen ein gebautes Artefakt | **offen — die Baurunde** |
| A10 | jeder Tab nennt seine Frage | erfuellt |
| A11 | ohne Raten ans Ziel | **offen — braucht `power-user` am Artefakt** |
| A12/A13 | Einheiten, Gestaltung | 4 bzw. 3 von 6 Tabs |
| A14 | QA je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | **gebaut**, Nachweis am Artefakt offen |
| A16 | best/worst case | **nicht gebaut** — nachgemessen 12.09.: null Treffer, nur `GoalContext.declared` als Hebel; AK-182 verlangt eine zweite Auswahlliste, `advisorbar.py:476` legt eine an |
| A17 | Ranking ohne Bezugswaffe | **halb** — nur der alte Ausweichzweig (`goals.py:192-208`); die Voreinstellung rankt weiter mit Waffe. AK-190/192/193 offen. Der einzige Test zementiert den Ist-Zustand |

## Was als naechstes kommt

1. **A16 und A17 bauen** — getrennte Auftraege, Spec liegt vor (AK-182,
   AK-186, AK-187, AK-190 bis AK-193).
2. **Aufraeumen:** tote Zeilenverweise **erledigt** 12.09. (in lebenden
   Dokumenten durch stabile Befund-IDs ersetzt; Altberichte bleiben stehen,
   Hinweis am Kopf der Verlaufsdateien). Offen: neun Registerzeilen zeigen auf
   ganze Abschnitte von 24 bis 232 Zeilen · Aufraeumlauf gegen toten Code.
3. **Die Baurunde:** `compliance-agent` (`auflagen`) → `technical-writer` →
   `release-manager` (`build`) → (`clean-room`) → `power-user` → (`notes`).
   Drei Vorbehalte aus T-159 brauchen ein **echtes Fenster**: AK-110, AK-129, A11/A15.

## Beim Nutzer — offen

1. **Drei `widerspruechlich`-Faelle** im AK-Register (T-184, ab Z. 344).
2. **1320 px als Messumgebung** — gilt sie weiter, obwohl A14 sie als
   Startbreite aufgehoben hat? Betrifft AK-05, AK-160, AK-194; bei "nein" muss
   die Schranke `>= 105 px` aus AK-194 neu abgeleitet werden.
3. **SEC-026:** DLL-Seite haerten oder nicht. **Falle:** wer haertet, macht
   SEC-016/017/018 wieder scharf. Blockiert das Release, nicht den Bau.
   **SEC-036 haengt daneben, ist aber unabhaengig fixbar.**
4. **C-003, vor der ersten Weitergabe:** A-025 (GRAU — die EXE traegt die
   Entschluesselungsschluessel) · Repo dauerhaft oeffentlich? · Release
   bewerben? · Arbeitsvertrag (C-001)? · US-Recht (17 U.S.C. § 1201)?
5. **Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 · F-G QA-170.

## Beschlossen, nicht beauftragt

- **Senken-Waechter zu SEC-023** (12.09.): `texts_that_can_land_behind_the_prefix()`
  um eine zweite Maske erweitern — Trennzeichen, `%APPDATA%`, `userdata`.
  Heute ist der Pfad an der Quelle zu, die Senke ungebunden.
- **Der SEC-031-Waechter misst die echte Kandidatenliste** statt `_steam_roots`
  zu stubben (12.09.). Sonst bleibt jede kuenftige feste Wurzel unsichtbar —
  genau so ist SEC-036 durchgerutscht.
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183). Ohne ihn
  waechst der Bestand wieder zusammen.

## Eigene Fehler dieses Zyklus — alle von Rollen gefunden, keiner selbst

**QA-210** war kein Loch im Nummernkreis, sondern ein Befund, den T-124 zur
Aufnahme angemeldet hatte und den ich nie eingetragen habe. **256 AK** waren
255 — meine Suche fiel auf ein Suchmuster herein, das im Text der Spec steht.
Commit `1e6bb98` nennt "157 offen", richtig waren **158**: Zugang QA-210 gegen
Abgang QA-215 nicht gegengerechnet. Das Splitten der Register hat 7
Zeilenverweise ins Leere zeigen lassen.

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008 bis L-018;
projekteigen NH-001, NH-002. **Nie geprueft:** Linux/macOS, Fremdinstallation.
