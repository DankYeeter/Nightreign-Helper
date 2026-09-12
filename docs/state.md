# Stand

2026-09-12, **Zyklus 20 laeuft**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` · Befunde
`qa/findings.md` und `security/findings.md` (Tabelle; Fliesstext in den
`verlauf.md` daneben) · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 12.09. am Register): T ab **T-216** · QA ab
**QA-247** · SEC ab **SEC-043** · AK **AK-264** · AD **AD-033** · OF **OF-34**
· DR **DR-022** · R **R-007** · C **C-005** · A **A-033**. **AD-027 und OF-14
wurden nie vergeben.**

## Auftragslage (Nutzer, 12.09.2026)

Autonom durcharbeiten bis zum fertigen Produkt. **Kein Merge, kein Release,
keine Weitergabe.** Angehalten wird bei kritischem Sicherheitsbefund, Verdacht
auf Datenverlust oder zwei Zyklen ohne messbaren Fortschritt. Dazu der
**Ueberbau-Audit** in drei Koerben: 1 kleine Eingriffe (laeuft), 2 Loeschungen
(**zurueckgezogen**, Fehler 1), 3 Umbauten (**P10** in `plan-restarbeiten.md`).

## HIER WEITERMACHEN

**Zyklus 20 ist abgeschlossen.** Alle drei Pruefrollen durch (QA **PASS**,
Security **CONCERNS**, UI-Review **fast fertig**), Korb 1 des Ueberbau-Audits
erledigt, drei Retrospektiv-Massnahmen gebaut. Suite **1789 passed, 9 skipped**
(T-211 und T-212 unabhaengig, seither keine `.py` geaendert — geprueft).

1. **Beim Nutzer, und es haelt `selftest.ps1` rot:** vier Hooks sind in keiner
   Registrierung (`require-receipt`, `no-root-find`, `remind-sync-out`, neu
   `state-line-budget`). `~/.claude/settings.json` ist seine Datei, kein Agent
   fasst sie an. Schnipsel in `docs/berichte/T-213-developer.md`. **101 PASS,
   4 FAIL**, alle vier sind diese Luecken.
2. **Eine Bauwelle** fuer QA-242 (90 px, Ursache unbekannt — erster Anlauf,
   beim zweiten der `fehlerdiagnostiker`), QA-210, QA-232, SEC-037, SEC-038
   (**vor** dem SEC-036-Fix, sonst keine rote Phase), SEC-039.
3. **P10 braucht den `architect`:** Planner 3 318 Zeilen, Mutations-Registry
   5 300 — beides bestaetigte Schuld. **P10-2 vor oder mit P10-1.**
4. **A16 ist nicht gebaut und nicht entschieden** — das einzige offene
   Kriterium, das eine Entscheidung des Nutzers braucht, nicht einen Auftrag.
5. **Release-Kette** (auflagenseitig frei, GELB ohne ROT): `technical-writer`
   → `release-manager` (`build`) → `clean-room` → `power-user` (A11) →
   `notes`. **SEC-027 ist das Release-Tor**, sonst nichts.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A2 | kritisch/hoch behoben | **erfuellt** fuer QA; **SEC-027 ist Hoch/offen** (`security/findings.md:45`) und haelt das Release-Tor zu |
| A3-A5 | der Build-Berater | **gebaut**, T-114 am Artefakt bestaetigt |
| A6 | Oberflaeche blockiert nicht | **erfuellt und gemessen** |
| A7 | sagen, wo die Daten nichts hergeben | erfuellt, **QA-210, QA-232, SEC-039 offen** |
| A8 | alles Englisch | **QA-211 geschlossen**, T-201 mit eigenem Rotlauf bestaetigt; **SEC-039 ist die naechste Senke** |
| A9/A11 | gegen ein gebautes Artefakt / ohne Raten ans Ziel | offen — die Baurunde, dann `power-user` |
| A15 | Erststart fuehrt zu Daten | gebaut; **SEC-037: seine Route hat die Freigabebedingung von SEC-016/017/018 ueberholt** |
| A16 | best/worst case | **nicht gebaut**, keine Entscheidung getroffen |
| A17 | Ranking ohne Bezugswaffe | **erfuellt und bestaetigt** — `06be06e` gebaut, T-199 gemessen (Kartenzeile 228 px, drei sichtbare Zeilen), T-201 PASS |

## Befunde

**249 QA** (171 offen, 59 behoben, 12 geschlossen, 6 teilweise, 1
zurueckgestellt), **42 SEC**, **21 DR**.

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
   nicht — ein Klick ist keine Herkunftspruefung. **SEC-027** ist Hoch/offen
   und damit **das** Release-Tor. **A-020 sperrt nicht mehr** (Nutzer 09.09.,
   von T-210 belegt) — meine fruehere Angabe hier war veraltet.
2. **C-003, vor der Weitergabe:** Repo dauerhaft oeffentlich? Release
   bewerben? Arbeitsvertrag (C-001)? US-Recht? — **A-025 ist entschieden**
   (FORTSETZEN, Nutzer 09.09.), stand hier faelschlich als offen.
3. **Drei `widerspruechliche` Faelle** im AK-Register (`UI_SPEC.md` ab Z. 81).
4. **1320 px als Messumgebung** — gilt sie weiter? AK-05, AK-160, AK-194.
5. **Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 · F-G QA-170.

## Beschlossen, nicht beauftragt

- **Senken-Waechter zu SEC-023:** die Pfadhaelfte haelt **nur fuer die Bauform
  des Befundtexts** (T-202), nicht als "kein Pfad erreicht die Flaeche".
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183).
- **Pruefpunkt 13** ist in T-193 auf "gleiche Rechnung bei gleichen Eingaben"
  eingeengt; ob die alte Zusage formal zurueckgezogen wird, ist offen.

## Eigene Fehler, Zyklus 20 — sieben, ausgewertet in T-209

Kurzfassung; Muster, Wirkungskontrolle und Massnahmen stehen in
`docs/lessons.md` (L-019, L-020, NH-003).

1. **Korb 2 zurueckgezogen** — der Audit hat Zeilen gezaehlt und auf Redundanz
   **geschlossen**; die Verlaufsdateien sind keine Kopien (Belege: P10).
2. **QA-235 doppelt zu QA-224** — nach Status durchsucht, nicht nach Inhalt.
3. **Fuenf kaputte Tabellenzeilen** (QA-236/237 auf einer Zeile, QA-240 mit
   neun Spalten, vier Altzeilen) — geheilt, NH-003 bewacht sie jetzt.
4. **`docs/state.md` mit 149 Zeilen committet**, Waechterlauf danach statt
   davor. Drittes Mal — daher L-020.
5. **T-205 und T-208 liefen ohne Auftragsdatei**, T-205 zusaetzlich ohne
   abgelegten Bericht. Nachgetragen.
6. **Drei Auftraege fuer einen Satz** (T-213/214/215): jeder Zuschnitt gab nur
   **eine** Fundstelle frei, und meine Zeilenangabe war beim zweiten schon
   veraltet. L-016 in Reinform.
7. **Vier Zahlen von Rollen korrigiert** (Erwartungen, Befundzeilen,
   Messskripte, Hook-Muster) — **jedes Mal lag die Rolle richtig.**

Regeln in `docs/plan-restarbeiten.md`, teamweit L-008 bis L-020, projekteigen
NH-001 bis NH-003. **Nie geprueft:** Linux/macOS, Fremdinstallation.
