# Stand

2026-09-12, **Zyklus 20 laeuft**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` · Befunde
`qa/findings.md` und `security/findings.md` (Tabelle; Fliesstext in den
`verlauf.md` daneben) · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 12.09. am Register): T ab **T-205** · QA ab
**QA-240** · SEC ab **SEC-043** · AK **AK-264** · AD **AD-033** · OF **OF-34**
· DR **DR-019** · R **R-007** · C **C-004** · A **A-033**. **AD-027 und OF-14
wurden nie vergeben.**

## Auftragslage (Nutzer, 12.09.2026)

Autonom durcharbeiten bis zum fertigen Produkt. **Kein Merge, kein Release,
keine Weitergabe.** Angehalten wird bei kritischem Sicherheitsbefund, Verdacht
auf Datenverlust oder zwei Zyklen ohne messbaren Fortschritt. Dazu der
**Ueberbau-Audit** in drei Koerben: 1 kleine Eingriffe (laeuft), 2 Loeschungen
(**zurueckgezogen**, Fehler 1), 3 Umbauten (**P10** in `plan-restarbeiten.md`).

## HIER WEITERMACHEN

Die Pruefphase ist vollstaendig: QA **PASS**, Security **CONCERNS**, UI-Review
**fast fertig** (DR-019 bis DR-021, 0 kritisch).

1. **Korb 1 ist abgeschlossen** (T-203, T-204, T-206) — rund **-37**
   Quellzeilen gegen die 120 000 des Audits, dazu ein Waechter, zwei
   bestaetigte strukturelle Schulden und acht Befunde. Bilanz und die
   widerlegten Punkte: `docs/plan-restarbeiten.md`.
2. **QA-241** — der Waechter ist erst **nach Sitzungsneustart** wirksam. Bis
   dahin schreibt der Director die drei Umlenkungen weiter woertlich in jeden
   Auftrag; `CLAUDE.md` behauptet inzwischen das Gegenteil.
3. **QA-242** — `wanted_height()` berechnet 1151 px, die Dialoghoehe erreicht
   im selben Lauf 1061. **Kein Bildschirmanschlag** (4096x1728 nachgemessen),
   Ursache unbekannt. Erster Anlauf; scheitert ein zweiter, geht es an den
   `fehlerdiagnostiker`.
4. **Dann die Baurunde** (A9), davor `compliance-agent` (`pruefen`): 36
   Auflagen, 15 GELB.

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

**242 QA**, **42 SEC** (sechs neu aus T-202), **21 DR** (drei neu aus T-207).

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
   und das Release-Tor (Wortlaut vor V2).
2. **C-003, vor der Weitergabe:** A-025 (GRAU) · Repo oeffentlich? · Release
   bewerben? · Arbeitsvertrag (C-001)? · US-Recht?
3. **Drei `widerspruechliche` Faelle** im AK-Register (`UI_SPEC.md` ab Z. 81).
4. **1320 px als Messumgebung** — gilt sie weiter? AK-05, AK-160, AK-194.
5. **Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 · F-G QA-170.

## Beschlossen, nicht beauftragt

- **Senken-Waechter zu SEC-023:** die Pfadhaelfte haelt **fuer die Bauform des
  Befundtexts** (T-202) und darf **nicht** als "kein Pfad erreicht die Flaeche"
  weiterzitiert werden. Sprachhaelfte braucht eigene Bauform.
- **Waechter muessen die echte Kandidatenliste messen** statt zu stubben —
  **T-202 hat belegt, dass der SEC-036-Waechter genau das nicht tut** (SEC-038:
  5 von 5 Fundstellen Stubs, echter Koerper 26-mal gelaufen).
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183).
- **Pruefpunkt 13** ist in T-193 auf "gleiche Rechnung bei gleichen Eingaben"
  eingeengt; ob die alte Zusage formal zurueckgezogen wird, ist offen.

## Eigene Fehler, Zyklus 20 — fuenf an einem Tag

1. **Korb 2 ist zurueckgezogen, nichts geloescht.** Der Audit hat Zeilen
   gezaehlt und auf Redundanz **geschlossen**; die Verlaufsdateien sind keine
   Kopien, T-181/T-182 haben die Spec **geteilt** (Belege: P10). Dieselbe
   Klasse zweimal — Docstrings (vom Nutzer abgefangen), Verlauf (von mir, aber
   erst nach der Freigabe).
2. **QA-235 ist ein Duplikat von QA-224.** Ich hatte nach **Status**
   durchsucht, nicht nach **Inhalt**.
3. **QA-236 und QA-237 standen auf einer Zeile** (2086 Zeichen, fehlender
   Umbruch). Getrennt.
4. **Vier Tabellenzeilen strukturell kaputt** — QA-211, QA-225 bis QA-227:
   doppeltes Datum, fehlende Abschlusspipe, bei QA-211 der Status von einem
   Datum ueberschrieben. Diese Datei kannte nur drei. Alle repariert.
5. **Diese Datei wurde mit 149 Zeilen committet**, 29 ueber Budget — der
   Waechterlauf kam nach dem Commit statt davor. Drittes Mal.

**Massnahme, noch ohne Auftrag:** ein Waechter auf Spaltenzahl und
Abschlusspipe beider Befundtabellen — `tests/` haelt **kein** `.md`-Pfadliteral,
also bewacht sie heute nichts. Regeln in `docs/plan-restarbeiten.md`, teamweit
L-008 bis L-018, projekteigen NH-001/NH-002. **Nie geprueft:** Linux/macOS,
Fremdinstallation.
