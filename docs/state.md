# Stand

2026-09-13, **Zyklus 21 laeuft**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` · Befunde
`qa/findings.md` und `security/findings.md` (Tabelle; Fliesstext in den
`verlauf.md` daneben) · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 12.09. am Register): T ab **T-225** · QA ab
**QA-248** · SEC ab **SEC-043** · AK **AK-264** · AD **AD-036** · OF **OF-36**
· DR **DR-022** · R **R-007** · C **C-005** · A **A-033**. **AD-027 und OF-14
wurden nie vergeben.**

## Auftragslage (Nutzer, 12.09.2026)

Autonom durcharbeiten bis zum fertigen Produkt. **Kein Merge, kein Release,
keine Weitergabe.** Angehalten wird bei kritischem Sicherheitsbefund, Verdacht
auf Datenverlust oder zwei Zyklen ohne messbaren Fortschritt. Dazu der
**Ueberbau-Audit** in drei Koerben: 1 kleine Eingriffe (laeuft), 2 Loeschungen
(**zurueckgezogen**, Fehler 1), 3 Umbauten (**P10** in `plan-restarbeiten.md`).

## HIER WEITERMACHEN

**Zyklus 21 laeuft (13.09.2026).** Nutzerentscheidungen 13.09.: Bauwelle +
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
(E1/AK-230, AK-49, QA-242 A/B, QA-247) · T-222 `architect` A16-AD (**erledigt** AD-035 `e593a44`; B-1: Spielstand hat **312** Kopien, `GOAL.md`/`UI_SPEC.md` rechnen mit 309 — **dem Nutzer nennen**, GOAL-Zahl nicht selbst aendern) · T-223
`developer` klein AD-033 Punkt 2 (**erledigt** `64dd006`, ff-merged: `mutate.py` 5464 → 158 Zeilen, **301** Eintraege entfernt, nicht 289 wie AD-033 sagt — Archiv `git show f1fc79c:scripts/differential/mutate.py`; Suite im Worktree 1501 passed / 10 skipped, Director nicht nachgemessen). **T-224** `developer` A16 nach AD-035 (Worktree, laeuft). Danach: AD-034 Schritt 1-3,
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
| A16 | best/worst case | **nicht gebaut**, keine Entscheidung getroffen |
| A17 | Ranking ohne Bezugswaffe | **erfuellt und bestaetigt** — `06be06e` gebaut, T-199 gemessen (Kartenzeile 228 px, drei sichtbare Zeilen), T-201 PASS |

## Befunde

**250 QA** (QA-247 neu), **42 SEC**, **21 DR** — Zaehlung nach Status nach der Pruefphase.

**Pruefphase auf `b33461d` durch** (T-201/T-202) — erste seit T-186 bzw.
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
3. **Drei `widerspruechliche` Faelle** im AK-Register (`UI_SPEC.md` ab Z. 81).
4. **1320 px als Messumgebung** — gilt sie weiter? AK-05, AK-160, AK-194.
5. **Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 · F-G QA-170.

## Beschlossen, nicht beauftragt

- **OF-34 (13.09.):** reine Test-Umbenennungen zaehlen **nicht** gegen die
  Fuenf-Dateien-Grenze; AD-034 Schritt 3 ist ein Auftrag mit 2 Code- und 6
  Testdateien.
- **OF-35 (13.09.):** die nachgefahrenen `MUTATIONS`-Eintraege loescht der
  `qa-engineer` im Pruefphasenlauf (er hat `Edit`), der Director committet es
  mit seiner Buchfuehrung.
- **T-220 B-1:** `VariantDialog` (`app.py:1363-1435`, kein Aufrufer) wird in
  AD-034 Schritt 1 **gestrichen**, nicht umgezogen (`delete`).
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
