# Stand

2026-09-09, **Zyklus 18 abgeschlossen, Baurunde offen**. Branch
`docs/audit-and-advisor-design`, `main` geschuetzt, PR #16 offen — **Merge
gehoert dem Nutzer.** Verlauf: `docs/archiv/state-bis-2026-09-09.md`.
Reihenfolge: `docs/plan-restarbeiten.md`. Befunde: `qa/findings.md`,
`security/findings.md`. Auflagen: `docs/legal/AUFLAGEN.md`. Berichte:
`docs/berichte/T-###-<rolle>.md`.

**Nummernkreise** (nachgezaehlt 09.09.): T ab **T-165** · QA ab **QA-220** ·
SEC ab **SEC-036** · AK ab **AK-250** · AD ab **AD-033** · OF ab **OF-34** ·
DR ab **DR-019** · R ab **R-007** · NH ab **NH-003** · C ab **C-004** ·
A (Auflagen) ab **A-033**.

**Suite: 1703 passed, 9 skipped, 0 failed — und zwar in BEIDEN
Datenbedingungen** (mit Testabzug im umgelenkten `LOCALAPPDATA` und ohne),
Commit `a1172fb`. Vom Director selbst nachgemessen ohne Abzug, 335 s,
Umlenkung nachgewiesen. **Eine Suitezahl ohne genannte Datenbedingung ist in
diesem Repo wertlos** — siehe `docs/debug/D-001.md`: vier widerspruechliche
Messungen entstanden genau daraus. Testbefehl in `CLAUDE.md`.

## Auftragslage (Nutzer)

Autonomer Lauf ueber Nacht. **Kein Merge, kein Release** — beides bleibt beim
Nutzer. Bauen und Pruefen ist keine Weitergabe. Rechtsfragen und Sicherheit
werden **nach** dem Lauf besprochen.

## Was die Nacht gebracht hat

**A15 ist vollstaendig gebaut** — vorher null Zeilen. V1 bis V5 aus
`ARCHITECTURE.md` Nachtrag XI (AD-030, AD-031):

| | |
|---|---|
| **T-142** | Spielstand-Lesen im Hintergrund (AD-029 Stufe B) |
| **T-147** | ein Aufloesungspunkt, `gamepath.py` neu, SEC-028, SEC-030 |
| **T-149** | Auswahldialog, sechs Panels |
| **T-150** | `Find my save…`, `paths/save`, SEC-029 erste Haelfte |
| **T-151** | der langsame Rueckfallweg (AD-031) |
| **T-153** | der Rueckfall wird gesagt (A7), Dialog-Startort (AK-110) |
| **T-157** | SEC-029 zu Ende, A7-Bruch bei unlesbarem Save |
| **T-161** | Waechter fuer AK-245, SEC-033/034/035 |
| **T-162** | beide Wege fragen dasselbe Praedikat (SEC-031 erste Haelfte) |
| **T-164** | Laufwerks-Rueckfall raus, C3 ab zwei Ebenen, AK-131-Tests |

**Gemessen:** `inventory.load` **6147,6 → 657,2 ms** · Picker-Hauptthread
**318,1 → 7,2 ms** · `read_owned_relics` **4835,3 → 93,3 ms** ·
`find_loadout_table` **360,5 → 133,1 ms**.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | laufend — 219 QA, 35 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt**, T-160 bestaetigt |
| A3-A5 | der Build-Berater | **gebaut**, T-114 am Artefakt bestaetigt |
| A6 | Oberflaeche blockiert nicht | **erfuellt und gemessen** |
| A7 | sagen, wo die Daten nichts hergeben | **erfuellt**, Rueckfallsatz gebaut |
| A8 | alles Englisch | Waechter steht, **QA-211 offen** |
| A9 | QA gegen ein gebautes Artefakt | **offen — die Baurunde** |
| A10 | jeder Tab nennt seine Frage | erfuellt |
| A11 | ohne Raten ans Ziel | **offen — braucht `power-user`** |
| A12/A13 | Einheiten, Gestaltung | 4 bzw. 3 von 6 Tabs |
| A14 | QA je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | **gebaut**, Nachweis am Artefakt offen |
| A16/A17 | Berater: best/worst case, ohne Bezugswaffe | **nicht gebaut** |

## Die Baurunde — was als naechstes kommt

`compliance-agent` (`auflagen`) → `technical-writer` → `release-manager`
(`build`) → (`clean-room`) → `power-user` → (`notes`).

**Drei Vorbehalte aus T-159 warten genau darauf** — alle brauchen ein **echtes
Fenster**, keinen weiteren Quellstandlauf: **AK-110** (Systemdialog, mehrere
Steam-Bibliotheken) · **AK-129** (Skalierung 100/125/150 %) · **A11/A15**
(kommt ein Mensch ohne fremde Hilfe bis zu Zahlen).

**Fuer den `technical-writer` vorgemerkt:** A-024/A-027 und der ehrliche
README-Satz aus SEC-006 — der Text muss sagen, dass eine Bibliothek **aus dem
gewaehlten Ordner ausgefuehrt** wird. Steht in keinem Auftrag.

## Beim Nutzer — offen

1. **SEC-026:** Gilt die Annahme von SEC-006 (*"wer dort schreiben kann, hat
   den Nutzerkontext ohnehin"*) in der Fassung *"… oder der Nutzer hat auf den
   Ordner gezeigt"* weiter — oder soll die DLL-Seite geprueft werden?
   **Falle:** wer die DLL haertet, macht SEC-016/017/018 wieder scharf.
   **Blockiert das Release, nicht den Bau.**
2. **C-003, vor der ersten Weitergabe:** A-025 (GRAU — die EXE traegt die
   Entschluesselungsschluessel; Privatgebrauch straflos, mit dem ersten
   Release-Asset wird aus Nutzung Verbreitung) · Repo dauerhaft oeffentlich? ·
   Release bewerben? · Arbeitsvertrag (C-001)? · US-Recht (17 U.S.C. § 1201)?
3. **Aus dem Audit, Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 ·
   F-G QA-170.

## Entschieden in dieser Nacht

**Vom Nutzer:** A6 bekommt seine drei Zahlen · QA-207 nur nach vorn reparieren
· QA-209 vor 1.8.0 · **F-P leeres Raster** (gegen die Empfehlung) · F-Q so
lassen · F-R auch bei `Sort by` = `Name` · Streichliste freigegeben, Nightlords
**ohne Kopfzeile** · **der Laufwerks-Rueckfall faellt**.

**Vom Director:** SEC-026 und SEC-031 bleiben Mittel, Gegenposition jeweils
offengelegt, **kein WAIVED** · W2 nimmt seine Form aus AK-212 · IX-1.C ist
Voraussetzung, nicht Ersparnis · `goal_id` traegt die Unterscheidung im Typ ·
**`Beruehrt Dateien` bindet als Whitelist** — fehlt eine Datei, wird gemeldet
und angehalten · die zwei W-Reihen werden mit Herkunft zitiert, nicht
umbenannt.

## Buchfuehrung des Directors — acht eigene Verstoesse, alle von aussen gefunden

Dieselbe Klasse: **den Auftrag aus dem geschrieben, was ich gerade gelesen
hatte, statt aus der Quelle, auf die der Bericht verweist.** T-137 und T-140
(Bauteile bzw. Messungen fehlten) · "drei Aufrufer" statt vier · T-148 ohne
GOAL-Zitat und Stand-Auszug · T-147 sagte "Parallel: nichts", waehrend T-148
lief · T-150/T-151 als disjunkt bezeichnet und waren es nicht · die
`Beruehrt Dateien`-Liste aus Berichtszitaten zusammengesetzt · **und der
Commit, der diese Datei "auf Budget" nannte, als sie 132 Zeilen hatte.**

**Die fuenf Pruefungen stehen seit dem 08.09. in `templates/task.md` und haben
nicht gegriffen** — ich oeffne die Vorlage nicht, wenn ich die Datei direkt
schreibe. **Zwei Vorschlaege fuer die `retrospective`:** ein Hook auf
`Write`/`Edit` gegen `docs/tasks/T-*.md`, der GOAL-Zitat, Stand-Auszug,
Quittung und `Beruehrt Dateien` prueft (Bauform: `require-receipt.ps1`) — und
ein zweiter Blick auf das **Mutationsregister**, dessen Nachtrag in vier
Anlaeufen dreimal an der Zugschwelle gescheitert ist: nicht die Disziplin der
Rollen ist das Problem, sondern das Verfahren.

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008 bis L-018;
projekteigen NH-001, NH-002.

**Nie geprueft:** Linux/macOS · eine echte Fremdinstallation.
