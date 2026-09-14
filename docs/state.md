# Stand

2026-09-13, **Zyklus 21 laeuft**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` · Befunde
`qa/findings.md` und `security/findings.md` (Tabelle; Fliesstext in den
`verlauf.md` daneben) · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 12.09. am Register): T ab **T-235** · QA ab
**QA-255** · SEC ab **SEC-044** · AK **AK-272** · AD **AD-036** · OF **OF-36**
· DR **DR-025** · R **R-007** · C **C-005** · A **A-033**. **AD-027 und OF-14
wurden nie vergeben.**

## Auftragslage (Nutzer, 12.09.2026)

Autonom durcharbeiten bis zum fertigen Produkt. **Kein Merge, kein Release,
keine Weitergabe.** Angehalten wird bei kritischem Sicherheitsbefund, Verdacht
auf Datenverlust oder zwei Zyklen ohne messbaren Fortschritt. Dazu der
**Ueberbau-Audit** in drei Koerben: 1 kleine Eingriffe (laeuft), 2 Loeschungen
(**zurueckgezogen**, Fehler 1), 3 Umbauten (**P10** in `plan-restarbeiten.md`).

## HIER WEITERMACHEN

**Zyklus 22 laeuft (14.09.2026), Plan `~/.claude/plans/nightreign-helper-part-11-graceful-starfish.md`.**
Ziel: gebautes Artefakt (1.10.0) fuer den Ingame-Test des Nutzers am Abend;
kein Merge, kein Release, keine Signatur. Nutzerentscheidungen 14.09.: AD-034
Schritt 1-3 heute · A12/A13-Befunde **vor** dem Build fixen · QA-237 und
P3/P4-Schulden zurueckgestellt. **QA-095 war seit `99ed022` (03.09.) behoben**,
Registerzeile stand falsch (nachgezogen 14.09.); T-235 ist darum AD-034.
**Bauwelle abgeschlossen `79de9ba`, Suite 1527 passed / 9 skipped (Director 07:12).** T-235 AD-034 a/b/c erledigt: app.py **5145 → 3085**, neu `relicslots.py` 888, `savereader.py` 332, `statsheet.py` 938. Fuer den `architect`-Nachtrag (AD-034/AD-029-031): `draw()` statt `show()`, `Signal(object)` statt `Signal(dict)` (int-Schluessel, Emit schlug stumm fehl), kein `icons`, `SituationalRow`/`_heading` mit umgezogen, stale-`declared` in `Planner.recompute`, Fundstelle des Lesens jetzt `savereader.py`; Debt: Farbkonstanten in 6 Modulen kopiert (`theme.py`-Kandidat), `app.WHITE_SLOT` doppelt `model.WHITE_SLOT`. T-236 erledigt ohne Code (alle fuenf bereits behoben; Waechterluecke QA-128 Pkt 10). T-237 erledigt (QA-229/QA-230 behoben `5dd0cf7`, zwei Mutationen lebend → QA faehrt nach; QA-141/QA-144/DR-016 seit 05.09. behoben). Spec-Nachtrag `ui-ux-designer`: AK-262 (`BEST FOR ATTRIBUTES` passt in 118 px), DR-013..016 Status, UI_SPEC-Zitat Z. 3883 → statsheet. **Beta-Gate 07:30 auf `a68cd3d`:** Ponytail-Audit (Explore) 7 Funde → T-238 **erledigt** `5817a89`+`a68cd3d` (net -24 Zeilen, Waechter QA-128 Pkt 10), Suite **1528 passed / 9 skipped** (Director). Schuldenbuch: 1 `ponytail:` (Hook), kein Auftrag. pyflakes: 7 Altmeldungen (Tests/`ratios.py`), zurueckgestellt. Nebenfunde ohne Auftrag: `WHITE_SLOT = 4` in zwei `scripts/measure_*.py`, 13. `blockSignals`-Paar `weaponslots.py:385`. **Pruefphase T-239 laeuft (Freigabe 07:31):** `security-reviewer` **PASS** 0/0/0/0 (SEC-029 seit `aec3d05` behoben, Register nachgezogen; SEC-044 Beobachtung stderr-Traceback, zurueckgestellt); offen qa-engineer, ui-ux-designer, architect. Danach (`qa-engineer`, `security-reviewer`, `ui-ux-designer` Review, `architect` AD-034-Nachtrag in einer Nachricht), dann Release-Kette bis `notes`.

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

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A2 | kritisch/hoch behoben | **erfuellt** fuer QA; SEC-027 behoben (verlauf:553), Release-Tor jetzt SEC-026 (Mittel, Wirkung kritisch) — T-217 |
| A3-A5 | der Build-Berater | **gebaut**, T-114 am Artefakt bestaetigt |
| A6 | Oberflaeche blockiert nicht | **erfuellt und gemessen** |
| A7/A8 | Datenlage nennen / alles Englisch | **QA-211 geschlossen** (T-201 mit eigenem Rotlauf); QA-210, QA-232 und SEC-039 offen |
| A9/A11 | gegen ein gebautes Artefakt / ohne Raten ans Ziel | offen — die Baurunde, dann `power-user` |
| A15 | Erststart fuehrt zu Daten | gebaut; **SEC-037: seine Route hat die Freigabebedingung von SEC-016/017/018 ueberholt** |
| A16 | best/worst case | **gebaut** (T-224, AD-035), 11 Kopien bewegen die Rangfolge am Spielstand; QA-Pruefung offen, AK-05-Waechter rot bis T-225 |
| A17 | Ranking ohne Bezugswaffe | **erfuellt und bestaetigt** — `06be06e` gebaut, T-199 gemessen (Kartenzeile 228 px, drei sichtbare Zeilen), T-201 PASS |

## Befunde

**253 QA**, **43 SEC**, **24 DR** — Zaehlung nach Status nach dem Retest.

**Pruefphase auf `b33461d` durch** (T-201/T-202; die naechste auf `719c46d`, T-229) — erste seit T-186 bzw.
T-185, 13 Dateien und +685/-136 dazwischen. QA **PASS**, Security **CONCERNS**
(0 kritisch, 0 hoch, 2 mittel, 4 niedrig). **Der Diff fuegt keine neue
Vertrauensgrenzueberschreitung hinzu**, zwei unabhaengige Masken. A1 laufend.

**Offene P1:** QA-095 (Angriffskraft um 1/0,6 zu hoch, seit Zyklus 9 — die
Zahl, nicht die Rangfolge) · **QA-237** (die Ueberlagerung).

**Drei Entscheidungen aus T-202 liegen bei mir:** SEC-037 (Freigabetext oder
Deckel nachziehen) · SEC-038 **vor** dem SEC-036-Fix, sonst hat der keine rote
Phase · ob SEC-039 in die naechste Bauwelle geht.

## Beim Nutzer — offen

1. **SEC-026:** DLL-Seite haerten? **Falle, von T-202 praezisiert:** Haertung
   ueber **Herkunft** haelt SEC-016/017/018 geschlossen, ueber **Zustimmung**
   nicht. **Entschieden 13.09.: Herkunft**, T-217. **A-020 sperrt nicht mehr** (Nutzer 09.09.,
   von T-210 belegt) — meine fruehere Angabe hier war veraltet.
2. **C-003, vor der Weitergabe:** Repo dauerhaft oeffentlich? Release
   bewerben? Arbeitsvertrag (C-001)? US-Recht? — **A-025 ist entschieden**
   (FORTSETZEN, Nutzer 09.09.), stand hier faelschlich als offen.
4. **1320 px als Messumgebung** — **entschieden 13.09.: aufgegeben** (AK-05, AK-194 in T-226); AK-160 prueft der `ui-ux-designer` mit.
5. **Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 · F-G QA-170.

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
