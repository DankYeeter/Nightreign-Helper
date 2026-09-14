# Stand

2026-09-14, **Zyklus 22: Release-Kette abgeschlossen, Artefakt 1.10.0 fuer den Eigenlauf**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` · Befunde
`qa/findings.md` und `security/findings.md` (Tabelle; Fliesstext in den
`verlauf.md` daneben) · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 12.09. am Register): T ab **T-243** · QA ab
**QA-259** · SEC ab **SEC-045** · AK **AK-273** · AD **AD-036** · OF **OF-36**
· DR **DR-025** · R **R-009** · C **C-005** · A **A-037** (T-241a: vergeben bis A-036). **AD-027 und OF-14
wurden nie vergeben.**

## Auftragslage (Nutzer, 12.09.2026)

Autonom durcharbeiten bis zum fertigen Produkt. **Kein Merge, kein Release,
keine Weitergabe.** Angehalten wird bei kritischem Sicherheitsbefund, Verdacht
auf Datenverlust oder zwei Zyklen ohne messbaren Fortschritt. Dazu der
**Ueberbau-Audit** in drei Koerben: 1 kleine Eingriffe (laeuft), 2 Loeschungen
(**zurueckgezogen**, Fehler 1), 3 Umbauten (**P10** in `plan-restarbeiten.md`).

## HIER WEITERMACHEN

**Zyklus 22 abgeschlossen (14.09.2026), Plan `~/.claude/plans/nightreign-helper-part-11-graceful-starfish.md`.**
Ziel: gebautes Artefakt (1.10.0) fuer den Ingame-Test des Nutzers am Abend;
kein Merge, kein Release, keine Signatur. Nutzerentscheidungen 14.09.: AD-034
Schritt 1-3 heute · A12/A13-Befunde **vor** dem Build fixen · QA-237 und
P3/P4-Schulden zurueckgestellt. **QA-095 war seit `99ed022` (03.09.) behoben**,
Registerzeile stand falsch (nachgezogen 14.09.); T-235 ist darum AD-034.
**Bauwelle abgeschlossen `79de9ba`, Suite 1527 passed / 9 skipped (Director 07:12).** T-235 AD-034 a/b/c erledigt: app.py **5145 → 3085**, neu `relicslots.py` 888, `savereader.py` 332, `statsheet.py` 938. Fuer den `architect`-Nachtrag (AD-034/AD-029-031): `draw()` statt `show()`, `Signal(object)` statt `Signal(dict)` (int-Schluessel, Emit schlug stumm fehl), kein `icons`, `SituationalRow`/`_heading` mit umgezogen, stale-`declared` in `Planner.recompute`, Fundstelle des Lesens jetzt `savereader.py`; Debt: Farbkonstanten in 6 Modulen kopiert (`theme.py`-Kandidat), `app.WHITE_SLOT` doppelt `model.WHITE_SLOT`. T-236 erledigt ohne Code (alle fuenf bereits behoben; Waechterluecke QA-128 Pkt 10). T-237 erledigt (QA-229/QA-230 behoben `5dd0cf7`, zwei Mutationen lebend → QA faehrt nach; QA-141/QA-144/DR-016 seit 05.09. behoben). Spec-Nachtrag `ui-ux-designer`: AK-262 (`BEST FOR ATTRIBUTES` passt in 118 px), DR-013..016 Status, UI_SPEC-Zitat Z. 3883 → statsheet. **Beta-Gate 07:30 auf `a68cd3d`:** Ponytail-Audit (Explore) 7 Funde → T-238 **erledigt** `5817a89`+`a68cd3d` (net -24 Zeilen, Waechter QA-128 Pkt 10), Suite **1528 passed / 9 skipped** (Director). Schuldenbuch: 1 `ponytail:` (Hook), kein Auftrag. pyflakes: 7 Altmeldungen (Tests/`ratios.py`), zurueckgestellt. Nebenfunde ohne Auftrag: `WHITE_SLOT = 4` in zwei `scripts/measure_*.py`, 13. `blockSignals`-Paar `weaponslots.py:385`. **Pruefphase T-239 laeuft (Freigabe 07:31):** `security-reviewer` **PASS** 0/0/0/0 (SEC-029 seit `aec3d05` behoben, Register nachgezogen; SEC-044 Beobachtung stderr-Traceback, zurueckgestellt); `qa-engineer` **PASS** (kein P1/P2; QA-128 komplett behoben — Pkt 1-3 seit `324abf0`; QA-229/230 bestaetigt, Mutationen geleert; AK-188/AK-169 auf 314 Kopien: 67 Curses, 437/860 Effekte, Partition 154/0/147/40/96/0 — Rezept B/`42` nicht nachgerechnet, an `ui-ux-designer`) · `ui-ux-designer` ship-ready, DR-013..016/022/023 geschlossen, AK-262 Empfehlung `BEST FOR ATTRIBUTES` · `architect` Nachtrag `9527517`. **Pruefphase abgeschlossen 07:50, Stand `a68cd3d` unveraendert im Code (nur `MUTATIONS` geleert).** Entschieden 07:52: AK-262 `BEST FOR ATTRIBUTES` (T-240 `982072b`), GOAL.md 314 nachgetragen. **Release-Kette T-241 laeuft:** Version 1.10.0 `9e8933d` · T-241a `compliance-agent` **GRUEN** fuer den lokalen Bau (Schwelle: erste Kopie an Dritte → A-020/A-023/A-031/A-033, dringend A-008 `release.yml` ohne pytest; QA-243 behoben) · T-241b README **erledigt** (Steam-Herkunft, Advisor/Hold/Worst-Best, Mindestbreite 1536 px, Grenze ohne Steam; Befund: `docs/screenshots/build_planner.png` vom 20.08. zeigt den Stand vor dem Berater — Regenerierung `scripts/make_screenshots.py` beruehrt A-010/A-012, **Nutzerentscheidung vor dem naechsten Release**, nicht heute) · T-241c **Build** `dist/NightreignHelper.exe` 1.10.0, 59.083.369 B, SHA-256 `314ca35c…930bd`, Commit `9e8933d` (`.venv` fehlte, neu angelegt) · T-241d: `clean-room` bestanden, **Update-Weg ungeprueft** (kein 1.9.0-Artefakt mehr) · `power-user` 3/6 erreicht, Ziele 3/4 klickkontaminiert · `qa-engineer` **A9 FAIL**: A4 bricht an **QA-257** (Exklusivgruppe doppelt gezaehlt, `model.compute` warnt nur) → **T-242 behoben `0e1269f`** (Suite **1532/9**, Director; Golden Wylder 3 Startwaffen-Strafen 118 → 163 AR; zwei neue A7-Saetze fuer `ui-ux-designer`-Abnahme im Retest), Rebuild `473e109d…`, **Retest PASS** (A4/A9), AK-272 Textfix `1b36238` (Spiel-Id raus), **finaler Build `dist/NightreignHelper.exe` 59.083.751 B, SHA-256 `11f5eecd3be4dbc2583ad1dca82dda0f78d54f84b205a4ab6f060f028792158c`**; `notes` erledigt (`CHANGELOG.md` neu, `ROLLOUT.md` 1.10.0). Suite auf `1b36238`: 2x 1532/9, 1x 2 sporadisch rot (Namen nicht erfasst, QA-249-Klasse); A3/A5/A6/A7/A8 PASS am Artefakt (Optimize 1229 ms Median, Hauptthread max 25,6 ms auf dem 5900X, nicht Zielgeraet); QA-258 Picker-Kartenbau 1,5 s (P3, = T-118 P5) und QA-255 (Save-Fallback `Path.home()`, A15-Spielstandhaelfte am Artefakt nicht provozierbar) zurueckgestellt. **Ingame-Session 14.09. 17:44-18:03 durch** (`d577958`): Kalibrierung, QA-257, Persistenz bestanden; QA-096 (1,175), QA-097 (0,885), QA-113 (+1 Wylder / +3 Recluse, charakterabhaengig) bestaetigt; neu QA-259 Zweihand (zurueckgestellt), QA-260 Why-Platz, QA-261 Best-case-Lesart; QA-170 geschlossen. **Zyklus 23, Stufengrenze 21:10 auf `47abd1e`+`02d738e`, Suite 1564/9:** T-246 **erledigt** (QA-096 Raider 1,18, QA-097 Claws 0,88, QA-113 flache Umwandlung 3/3 — alle als gemessene Kalibrierung deklariert) · T-247 Spec AK-273-275 · T-248c **erledigt** `14ebb78` (Why je Karte, Suchfeld-Hinweis) · **GOAL neu: A18** (Lesarten weg, Don't include) **A19** (Must include) **A20** (Zweihand) — Nutzer 20:35-20:58 · T-248a `architect` AD-036 (Mengen auf `SlotProblem`, 4 Schritte, kein Anker faellt, kein `__schema`) + AD-037 (Zweihand, **Bau gesperrt bis R-008**: STR x1,5 trifft 208/169 statt 216/151) · T-248b Spec AK-276-288. Nutzer 21:15: OF-37 ja (bedingte Fluechte zaehlen) · OF-41 Hand per **neuem Umschalter 1H/2H an der Waffe** · sechs Zweihand-Messzellen geliefert (GOAL A20) · Rebuild ja. **Retest T-249 PASS** (QA-096/097/113/260/265 geschlossen, 263/264 bestaetigt, drei Mutationen geloescht) · **Build 1.10.1 `dist/NightreignHelper.exe` 59.089.432 B, SHA-256 `dfdeadc42475707241b6764904e7a791a536fb25b65494460f2cea560676a558`, Commit `dde2efc`** — im Startmenue. **R-008 erledigt** (`docs/research/R-008.md`): keine Attributregel trifft; **flacher Faktor auf die ungerundete Einhandzahl je Nightfarer: T = 1,03** (Wylder/Guardian/Duchess, Intervall [1,0259; 1,0324)) und **T_Raider = 1,144** ([1,1439; 1,1445), 216 an der floor-Kante) — 6/6. Params ohne Zweihandrate; Paramdef nennt STR x1,5 nur fuer den Treffer, nicht die Anzeige. Director: AD-037 bauen als gemessene Kalibrierung (wie 0,6/1,18/0,88), uebrige Nightfarer bis zur Messung mit 1,03 und A7-Hinweis; Bau nach T-248d. **A18/A19 gebaut und abgenommen (15.09. 00:11):** T-248d 1-3 (`d6fda65`, `9423eee`, `e7a8eef`), T-250a/b (`115dd4e`, `528ff78`), Pruefphase T-251 (QA FAIL an QA-267, Security 0/0/0/1, Review DR-025/026), Fix T-252 (`e18d782`..`2a0ca0d`, QA-266 = Tests lasen lebenden Spielstand → `conftest.no_living_save`), Retest T-253 **PASS**, Suite **1602 passed / 10 skipped** (Director). **Build 1.11.0 `dist/NightreignHelper.exe` 59.105.391 B, SHA-256 `f23eb0f784665a8c018c19f353ad114e9809061033076311dcdf21dbb916e8e0`, Commit `08ddba6`** — im Startmenue; CHANGELOG 1.10.1/1.11.0, ROLLOUT 1.11.0. **Offen:** AD-037 Zweihand (R-008: T=1,03 / Raider 1,144, Umschalter 1H/2H an der Waffe per Nutzer OF-41) → naechster Bauauftrag; QA-269 Feldnamen, QA-270 Wortlaut, A18-Satz-1 (Bedingung in Why) → Spec; ~42 tote `skip("no save to read")`; Screenshots-Regenerierung; Update-Weg nie am Artefakt geprueft. Director-Entscheide: OF-38 ein Auftrag mit Ausnahme (zwei Durchreich-Zeilen), OF-39 ja — Nachfolgesatz zu AK-270 vom `ui-ux-designer` im Bauauftrag. Startmenue-Verknuepfung `Nightreign Helper.lnk` zeigt auf `dist/` (Director 17:42). **Abend 14.09. (19:21-20:10):** kein Merge-Konflikt (PR #16 MERGEABLE); CI war rot seit T-237 → **T-243** `70bbe3d` Kartenbreite aus `QFontMetrics`, **CI gruen** auf `ba4e009` (QA-262 behoben); zwei Rest-Worktrees entfernt. **T-244** QA Picker-Suche: vollstaendig, CONCERNS → **T-245** `99a5bc5` (Operatoren nur GROSS, Fluchtext im Haystack, README; QA-263/264 behoben, QA-265 Hinweis an `ui-ux-designer`). Suite **1541 passed / 9 skipped** (Director 20:10). **Artefakt `dist/` ist noch der Stand `1b36238`** — Rebuild mit T-243/T-245 im Zyklus 23.

**Zyklus 21 (13.09.2026), Verlauf.** Nutzerentscheidungen 13.09.: Bauwelle +
P10-Entwurf parallel · SEC-026 **haerten ueber Herkunft** (DLL nur aus
Registry-/`libraryfolders.vdf`-Bibliotheken, feste Wurzeln raus) · SEC-037
**Deckel nachziehen**. Teamregeln vom 12./13.09. gelesen (`templates/task.md`
Praemissen-Pflichtfeld, Gate-Kriterium, Phasenmodell).

**Dispatch 13.09.:** T-217 `developer` (SEC-038 → SEC-036 → SEC-026, **erledigt** `09f5cdb`+`ffb82dd` Worktree; Befunde: E1-Headline passt nicht zum Herkunftssatz → Spec-Nachtrag; ohne Steam in der Registry wird jeder Ordner abgelehnt → Folge der Entscheidung, **dem Nutzer nennen**) · T-218
`developer` (QA-210, QA-232, SEC-039 **behoben**; QA-242 Ursache gemessen, A/B an `ui-ux-designer`; Nebenfund QA-247) · T-219
`developer` klein (SEC-037, **erledigt** `670d879` auf Worktree-Branch, noch nicht zusammengefuehrt) · T-220 `architect` (**erledigt**: AD-033 Registry als Quittung je Zyklus, `MUTATIONS` einmal leer; AD-034 Planner-Schnitt in drei Schritten `relicslots.py` → `savereader.py` → `statsheet.py`; `ARCHITECTURE.md` ab Z. 5325). **Reihenfolge P10:** erst T-217 zusammenfuehren (aendert Anker in `mutate.py`), dann AD-033 Punkt 2, dann AD-034 Schritte 1-3. Drei
Worktrees, **zusammengefuehrt** `e465c17` (ein Importkonflikt `oodle.py`, beide Zeilen), Suite auf dem Merge **1805 passed, 9 skipped** (Director, 13.09.); dafuer `origin/HEAD` lokal auf
`docs/audit-and-advisor-design` gesetzt (B-03). **Vorgaben-Vorlauf
uebersprungen:** die Vorgaben sind die T-202-Befunde selbst, keine neue
Vertrauensgrenze, keine neue Abhaengigkeit.

**SEC-027 stand hier faelschlich als offenes Release-Tor:** `security/verlauf.md:553`
fuehrt es als "behoben, Retest bestanden" (T-146), `It is only read` kommt in
`nrplanner/`/`nrdata/` nicht vor (grep 13.09.). Registerzeile nachgezogen.
Release-Tor ist damit **SEC-026** (T-217).

**Welle 2 (13.09., gepusht bis `59c6cd1`):** T-221 `ui-ux-designer` Spec-Nachtrag
(**erledigt** `503fbed`: AK-264 E1-Headline `That folder is not part of a Steam installation.` → bauen; AK-265 nur Doku; AK-266 QA-242 **Wahl A** → bauen; AK-267 QA-247 A7-Verstoss → bauen) · T-222 `architect` A16-AD (**erledigt** AD-035 `e593a44`; B-1: Spielstand hat **312** Kopien, `GOAL.md`/`UI_SPEC.md` rechnen mit 309 — **dem Nutzer nennen**, GOAL-Zahl nicht selbst aendern) · T-223
`developer` klein AD-033 Punkt 2 (**erledigt** `64dd006`, ff-merged: `mutate.py` 5464 → 158 Zeilen, **301** Eintraege entfernt, nicht 289 wie AD-033 sagt — Archiv `git show f1fc79c:scripts/differential/mutate.py`; Suite im Worktree 1501 passed / 10 skipped, Director nicht nachgemessen). **T-224 A16 gebaut** (`9069d83` gemerged, 4 Commits, +482/-52, vier Mutationen getoetet), Suite im Worktree **1 failed / 1509 passed / 9 skipped** — der Fehlschlag ist der AK-05-Waechter (zweite Box laesst der Statuszeile 0 px offscreen, 37 px am Fenster). **Nutzerentscheidung 13.09.:** 1320 px aufgeben, Statuszeile darf schrumpfen (AK-05 auf A14-Startbreite, AK-194 auf > 0 px). Dazu 312 Relikte in `GOAL.md` nachgetragen (`541bba8`). T-226 (`4017938`: AK-05 auf A14-Startbreite, AK-194 > 0 px, AK-268) und AD-035-Nachtrag (`1a37481`) **erledigt**. **Bauphase Zyklus 21 abgeschlossen** (`dbf44ae`): T-217 bis T-227 gebaut, Suite **1519 passed / 9 skipped** (Director gemessen 13.09.). QA-248 behoben: Startfenster jetzt **1608 px** statt 1350 (abgeleitet; Nutzer erwartete ca. 1540 — Zahl gemessen, nicht geschaetzt). Mutations-Registry traegt die lebenden Eintraege von T-224/T-225/T-227 — QA faehrt nach und loescht (AD-033 Punkt 5). **Beta-Gate 13.09., Nutzerentscheidung:** Audit-Auftrag, dann Pruefrollen; **kein Build vor der Pruefphase.** Ponytail-Audit (Explore, `550efc5`): 22 Funde, net -570 Z.; Schuldenbuch: 1 `ponytail:`-Kommentar (Hook), kein Auftrag. **T-228 erledigt** (`719c46d`, ff-merged): 14 Loeschungen, 21 Dateien +32/-271, pyflakes leer; Fund 16 (`PressableFrame` → `QAbstractButton`) **nicht gebaut, als native geschlossen** (Sonde: Press-Binding leer, `QAccessibleButton` in PySide6 nicht exportiert, Klick beim Loslassen — Verhaltensaenderung). Suite auf dem Merge **1519 passed / 9 skipped** (Director); im Worktree einmal 1 failed sporadisch → **QA-249**. Nicht in T-228, an den `architect` beim naechsten Auftrag: `AttackRating` (QA-071), `Weighting` (OF-3), `reading_changed`-Signal vs. AD-035, QSettings-Konstruktoren (Director: bleiben, tragen die Umlenkung). **Pruefphase T-229 laeuft (eingefroren auf `05c6787`, Code `719c46d`):** `qa-engineer` (Kriterien pruefen, nicht Code; `MUTATIONS` nachfahren und loeschen; AK-188/AK-169 auf 312 nachzaehlen), `security-reviewer` **PASS** (0/0/0/1: SEC-026/036/037/038/039 geschlossen, SEC-043 neu Niedrig, SEC-016/017/018-Freigabe traegt wieder; Bericht abgelegt), `ui-ux-designer` Review **braucht Arbeit** (`42914fa`: DR-022 Kritisch — offener Picker faellt nach Rescan ohne Fund nicht auf AK-212 zurueck, `relicpicker.py:1006` setzt `ranking` nie zurueck; DR-023 Statuszeile ohne Tastatur-/Screenreader-Zugang; DR-024 nice-to-have; AK-160-Redaktion vorgeschlagen; Hinweis: Spielstand hat 314 Kopien, nicht 312 — QA zaehlt). `qa-engineer` **FAIL** (ein P2: QA-250 kleine Bildschirme; QA-251, QA-232 teilweise, QA-249 erweitert, QA-252, QA-253; Retests QA-210/242/247/248 und SEC-Retests bestaetigt; A16-Test misst beide GOAL-Haelften; 9 von 10 Mutationen getoetet, 10 geloescht `43edd95`; Spielstand hat **314** Kopien). **Nutzerentscheidung 13.09.:** Boxen haben Vorrang, Statuszeile darf unter der abgeleiteten Breite verschwinden. **T-230 gemerged `a73b3b1`** (7 Abschnitte, 6 erledigt, 7 Mutationen getoetet; Suite **1525 passed / 9 skipped** dreimal — developer 1x, Director 2x; DR-022/DR-023 gebaut, Register `DESIGN_REVIEW.md` zieht der `ui-ux-designer` im Retest nach). **Nutzerentscheidung 13.09.: AK-05 gilt ab 1536 px** logischer Breite (bei 1366 px fehlen der Leiste 169 px). T-232 **erledigt** (`7bc8b04`: AK-270, Waechterfall 1366, `done()` idempotent = QA-254; Suite **1531 passed / 9 skipped / 0 warnings**, Director) · T-233 **erledigt** (AK-271 Untergrenze 1536 px; DR-022/023 gebaut, Retest offen). **Retest T-234: CONCERNS** (`3110b4e`) — alle 11 Punkte bestaetigt, 9 Mutationen (nicht 2: die 7 aus T-230 waren noch drin) nachgefahren und geloescht; einziger CONCERN QA-249 (ein zeitabhaengiger Test, 5 gruene Laeufe in Folge) — **Director: angenommen, beobachten.** DR-022/DR-023 zieht der `ui-ux-designer` im naechsten Lauf auf behoben. **Pruefphase Zyklus 21 abgeschlossen. Naechstes Gate: Release-Kette** (`security-reviewer` Pflicht auf `7bc8b04` → `compliance-agent` auflagen → `technical-writer` (README: 1536 px, Steam-Herkunft, Worst/Best) → `build` → `clean-room` → `power-user` A11 → `notes`); **kein Merge, kein Release, keine Weitergabe** (Nutzer 12.09.). · T-231 A33 **erledigt** (AK-269 kleine Bildschirme, AK-270 `The reading changed while this was working out — use Optimize again.` → in den Retest-Fix; AK-160 aufgeloest, **Widerspruch-Liste leer**). Danach **ein** Retest (`qa-engineer`, sonnet) → Gate. Offener Zaehlauftrag: AK-188/AK-169-Zahlen (67/42/426/323) auf 312 Kopien nachzaehlen — in der Pruefphase. Dann AD-034 Schritt 1-3,
QA-242-Fix → Beta-Gate mit `/ponytail-audit`, `/ponytail-debt`, Pruefrollen
in einer Nachricht.

## Stand gegen `GOAL.md` (14.09.2026, 10:00, Artefakt `11f5eecd…158c`)

| | | |
|---|---|---|
| A1 | Audit-Bericht mit Status je Befund | laufend: Register `qa/`, `security/`, `DESIGN_REVIEW.md` |
| A2 | kritisch/hoch behoben | **erfuellt**: QA P1 QA-095 behoben (`99ed022`), QA-237 **zurueckgestellt (Nutzer 14.09.)**; SEC 0 kritisch/hoch |
| A3-A8 | Berater, A6, A7, A8 | **erfuellt am Artefakt** (T-241d + Retest, PASS); A6 auf dem 5900X gemessen, Zielgeraet offen |
| A9 | QA gegen gebautes Artefakt | **erfuellt** (T-241d Retest PASS auf `0e1269f`; finaler Build `1b36238` = Textfix) |
| A10, A14 | Tab-Fragen, QA je Tab | erfuellt (T-059) |
| A11 | ohne Raten ans Ziel | **teilweise**: power-user 3/6 erreicht, Ziele 3/4 klickkontaminiert, Ziel 5 Produktfrage ("haeufigster Effekt in meinem Besitz") — Ingame-Test des Nutzers heute Abend |
| A12/A13 | Einheiten, nichts abgeschnitten | **erfuellt** je Tab (T-239a, T-236/T-237) |
| A15 | Erststart fuehrt zu Daten | gebaut; am Artefakt nur Spielordner-Haelfte pruefbar (QA-255: Save-Fallback `Path.home()`) — **ungeprueft am Artefakt** |
| A16, A17 | Worst/Best, ohne Bezugswaffe | erfuellt und bestaetigt |

## Befunde

**258 QA**, **44 SEC**, **24 DR**. Offen P1: **QA-237** (zurueckgestellt). Offen P2:
QA-208 (Register veraltet, S11-I/T-241 bestaetigen die Hauptthread-Zeile —
nachziehen), Rest siehe Register. Neu 14.09.: QA-255 (Save-Fallback), QA-256
(Instanzsperre bei Paralleltests), QA-258 (Picker-Oeffnen 1,5 s = T-118 P5),
SEC-044 (stderr-Traceback, zurueckgestellt).

## Beim Nutzer — offen

1. **QA-259 Zweihand-Anzeige:** Umfang entscheiden ("fuer spaeter merken", 14.09.).
2. **Screenshots** `docs/screenshots/*.png` vom 20.08. zeigen den Stand vor dem Berater; Regenerierung beruehrt A-010/A-012 — vor dem naechsten Release.
3. **C-003, vor der Weitergabe:** Repo dauerhaft oeffentlich? Release bewerben? US-Recht? — A-025 entschieden (FORTSETZEN, 09.09.).
4. **Update-Weg 1.9.0 → 1.10.0** ungeprueft (kein 1.9.0-Artefakt); Migration laut Diff nicht noetig (`__schema` 3, `EXTRACT_VERSION` 11).
5. **A-008:** `release.yml` faehrt keine Tests — vor einem GitHub-Release.

## Beschlossen, nicht beauftragt

- **OF-34 (13.09.):** reine Test-Umbenennungen zaehlen **nicht** gegen die
  Fuenf-Dateien-Grenze; AD-034 Schritt 3 ist ein Auftrag mit 2 Code- und 6
  Testdateien.
- **OF-35 (13.09.):** die nachgefahrenen `MUTATIONS`-Eintraege loescht der
  `qa-engineer` im Pruefphasenlauf (er hat `Edit`), der Director committet es
  mit seiner Buchfuehrung.
- **Senken-Waechter zu SEC-023:** die Pfadhaelfte haelt **nur fuer die Bauform
  des Befundtexts** (T-202), nicht als "kein Pfad erreicht die Flaeche".
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183).
- **Pruefpunkt 13** ist in T-193 eingeengt; ob die alte Zusage formal
  zurueckgezogen wird, ist offen.

## Eigene Fehler, Zyklus 20 — sieben, ausgewertet in T-209

Kurzfassung; Muster und Massnahmen stehen in `docs/lessons.md` (L-019, L-020, NH-003).

1. **Korb 2 zurueckgezogen** — der Audit hat Zeilen gezaehlt und auf Redundanz
   **geschlossen**; die Verlaufsdateien sind keine Kopien (Belege: P10).
2. **QA-235 doppelt zu QA-224** — nach Status durchsucht, nicht nach Inhalt.
3. **Fuenf kaputte Tabellenzeilen** — geheilt, NH-003 bewacht sie jetzt.
4. **`docs/state.md` mit 149 Zeilen committet**, Waechterlauf danach statt
   davor. Drittes Mal — daher L-020.
5. **T-205/T-208 ohne Auftragsdatei**, T-205 ohne Bericht. Nachgetragen.
6. **Drei Auftraege fuer einen Satz** (T-213/214/215): jeder Zuschnitt gab nur
   **eine** Fundstelle frei; L-016 in Reinform.
7. **Vier Zahlen von Rollen korrigiert** (Erwartungen, Befundzeilen,
   Messskripte, Hook-Muster) — **jedes Mal lag die Rolle richtig.**

Regeln in `docs/plan-restarbeiten.md`, teamweit L-008 bis L-020, projekteigen
NH-001 bis NH-003. **Nie geprueft:** Linux/macOS, Fremdinstallation.
