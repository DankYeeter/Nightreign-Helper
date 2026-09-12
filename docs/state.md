# Stand

2026-09-12, **Zyklus 20 laeuft**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf: `docs/archiv/state-bis-2026-09-12-zyklus19.md`. Befunde:
`qa/findings.md`, `security/findings.md` (nur Tabelle; Fliesstext in
`qa/verlauf.md`, `security/verlauf.md`). Register: `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md`. Reihenfolge: `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 12.09. am Register, nicht erinnert):
T ab **T-205** · QA ab **QA-240** · SEC ab **SEC-043** · AK ab **AK-264** ·
AD ab **AD-033** · OF ab **OF-34** · DR ab **DR-019** · R ab **R-007** ·
C ab **C-004** · A ab **A-033**. **AD-027 und OF-14 wurden nie vergeben.**

## Auftragslage (Nutzer, 12.09.2026)

Autonom durcharbeiten bis zum fertigen Produkt. **Kein Merge, kein Release,
keine Weitergabe.** Angehalten wird bei kritischem Sicherheitsbefund, Verdacht
auf Datenverlust oder zwei Zyklen ohne messbaren Fortschritt.

**Dazu der Ueberbau-Audit vom 12.09.2026, in drei Koerben:** Korb 1 kleine
Eingriffe (laeuft), Korb 2 Loeschungen (**zurueckgezogen**, siehe unten),
Korb 3 strukturelle Umbauten (**P10** in `docs/plan-restarbeiten.md`).

## HIER WEITERMACHEN

Beide Auftraege liegen geschrieben und sind **nicht** dispatcht. Keiner laeuft
parallel zu etwas anderem — T-203 greift in fremde Werkzeugaufrufe ein.

1. **T-203 — Waechter statt Nachweispflicht** (Nutzerentscheid 12.09.):
   `PreToolUse`-Hook, projekteigen, weist Programmstarts ohne alle drei
   umgelenkten Variablen ab. Zieht `CLAUDE.md` nach und **muss sie kuerzer
   machen**. Dazu der Kopf von `requirements-dev.txt`.
2. **T-204 — Korb 1, mechanische Haelfte:** `StrEnum` statt der zwei
   `str`-Unterklassen (4 Dateien gezaehlt), `baseline_for` inlinen (1
   Aufrufer, im Test). Fuenf Dateien, Obergrenze; der Auftrag verlangt
   **Abbruch** bei einer sechsten.
3. **UI-Review** (`ui-ux-designer`, Review-Modus) — Fensterlauf, deshalb nicht
   neben einem anderen. Traegt **QA-239**: `UI_SPEC.md:2230` fuehrt
   `wanted_height` mit 1136 px, gemessen sind **1121**. Seine Datei, seine
   Zahl.
4. **Prosakuerzung** (Korb 1, Variante *"nur belegt Redundantes"*) — **noch
   nicht geschnitten**, ~20 Dateien. Vorschlag: Pilot auf `chalices.py`,
   `model.py`, `weapons.py`, Ausbeute messen, dann ueber die restlichen
   siebzehn entscheiden.
5. **Danach die Baurunde** (A9). Davor `compliance-agent` (`pruefen`) — 36
   Auflagen, 15 auf GELB.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | laufend — 239 QA, 42 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt** fuer QA; **SEC-027 ist Hoch/offen** (`security/findings.md:45`) und haelt das Release-Tor zu |
| A3-A5 | der Build-Berater | **gebaut**, T-114 am Artefakt bestaetigt |
| A6 | Oberflaeche blockiert nicht | **erfuellt und gemessen** |
| A7 | sagen, wo die Daten nichts hergeben | erfuellt, **QA-210, QA-232 und SEC-039 offen** |
| A8 | alles Englisch | **QA-211 geschlossen**, T-201 bestaetigt mit eigenem Rotlauf. **SEC-039 ist die naechste Senke** |
| A9 | QA gegen ein gebautes Artefakt | offen — die Baurunde |
| A10 | jeder Tab nennt seine Frage | erfuellt |
| A11 | ohne Raten ans Ziel | offen — `power-user` am Artefakt |
| A12/A13 | Einheiten, Gestaltung | 4 bzw. 3 von 6 Tabs |
| A14 | QA je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | gebaut; **SEC-037: seine Route hat die Freigabebedingung von SEC-016/017/018 ueberholt** |
| A16 | best/worst case | **nicht gebaut**, keine Entscheidung getroffen |
| A17 | Ranking ohne Bezugswaffe | **erfuellt und bestaetigt** — `06be06e` gebaut, T-199 gemessen (Kartenzeile 228 px, drei sichtbare Zeilen), T-201 PASS |

## Befunde

**239 QA:** 163 offen, 58 behoben, 11 geschlossen, 6 teilweise, 1
zurueckgestellt. **42 SEC:** davon sechs neu aus T-202 (SEC-037 bis SEC-042).

**Pruefphase auf `b33461d` (T-201, T-202) ist durch** — die erste seit T-186
bzw. T-185, mit 13 Dateien und +685/-136 dazwischen. QA: **PASS**. Security:
**CONCERNS**, 0 kritisch, 0 hoch, 2 mittel, 4 niedrig. **Der Diff selbst fuegt
keine neue Vertrauensgrenzueberschreitung hinzu**, mit zwei unabhaengigen
Masken belegt.

**Offene P1:** QA-095 (Angriffskraft um 1/0,6 zu hoch, seit Zyklus 9; betrifft
die Zahl, nicht die Rangfolge) · **QA-237** (die Ueberlagerung).

**Drei Entscheidungen aus T-202 liegen bei mir, nicht beim Nutzer:**
SEC-037 (Freigabetext nachziehen oder Deckel nachziehen) · SEC-038 **vor** dem
SEC-036-Fix bauen, sonst hat der Fix keine rote Phase (Empfehlung uebernommen)
· ob SEC-039 in die naechste Bauwelle geht.

## Beim Nutzer — offen

1. **SEC-026:** DLL-Seite haerten oder nicht. **Falle, von T-202 praezisiert:**
   Haertung ueber **Herkunft** haelt SEC-016/017/018 geschlossen, Haertung
   ueber **Zustimmung** nicht — ein Klick ist keine Herkunftspruefung.
2. **SEC-027** ist Hoch/offen und das Release-Tor. Wortlaut vor V2.
3. **C-003, vor der ersten Weitergabe:** A-025 (GRAU) · Repo dauerhaft
   oeffentlich? · Release bewerben? · Arbeitsvertrag (C-001)? · US-Recht?
4. **Drei `widerspruechliche` Faelle** im AK-Register (`UI_SPEC.md` ab Z. 81).
5. **1320 px als Messumgebung** — gilt sie weiter? Betrifft AK-05, AK-160,
   AK-194.
6. **Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 · F-G QA-170.

## Beschlossen, nicht beauftragt

- **Senken-Waechter zu SEC-023** (12.09.): die Pfadhaelfte ist drin und haelt
  **fuer die Bauform des Befundtexts** (T-202). Sie darf **nicht** als "kein
  Pfad erreicht die Flaeche" weiterzitiert werden. Die Sprachhaelfte braucht
  eine eigene Bauform.
- **Der SEC-031-Waechter misst die echte Kandidatenliste** statt zu stubben.
  **T-202 hat gezeigt, dass der SEC-036-Waechter genau diesen Fehler hat**
  (SEC-038): 5 von 5 Fundstellen sind Stubs, der echte Koerper lief 26-mal und
  gab beide feste Wurzeln zurueck.
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183).
- **Pruefpunkt 13** ist in T-193 auf "gleiche Rechnung bei gleichen Eingaben"
  eingeengt. Ob die alte Zusage formal zurueckgezogen wird, ist offen.

## Korb 2 ist zurueckgezogen — nichts geloescht

Der Nutzer hatte drei Gruppen freigegeben (35 154 Zeilen). **Die Freigabe
stand auf einer falschen Praemisse von mir**, und die Pruefung der lebenden
Verweise hat sie vor dem Loeschbefehl widerlegt: die Verlaufsdateien sind
**keine Kopien**, T-181/T-182 haben die Spec **geteilt**. `UI_SPEC.md:241` und
neun weitere Stellen sagen woertlich, der geltende Wortlaut stehe *nicht dort,
sondern* im Verlauf. Begruendung und Belege in `docs/plan-restarbeiten.md`,
Abschnitt P10.

## Eigene Fehler, Zyklus 20

**Vier an einem Tag, drei davon in meinen eigenen Buechern:**

1. **Der Ueberbau-Audit hat Zeilen gezaehlt und auf Redundanz geschlossen.**
   Zweimal dieselbe Klasse — die Docstrings (vom Nutzer abgefangen) und die
   Verlaufsdateien (von mir abgefangen, aber erst nach der Freigabe).
2. **QA-235 ist ein Duplikat.** `qa/findings.md:246` fuehrte den Fall schon
   als QA-224. Ich hatte die Tabelle nach **Status** durchsucht, nicht nach
   **Inhalt** — genau die Absenz-Pruefung, die meine eigene Regel verlangt.
3. **QA-236 und QA-237 standen auf einer Zeile** (2086 Zeichen), ein
   fehlender Umbruch beim Anhaengen. Getrennt am 12.09.
4. **Vier Tabellenzeilen waren strukturell kaputt** — QA-211, QA-225, QA-226,
   QA-227: doppeltes Datum, fehlende Abschlusspipe, bei QA-211 zusaetzlich der
   Status von einem Datum ueberschrieben. Diese Datei kannte nur drei davon.
   Alle vier repariert und gegengeprueft.

**Massnahme, die daraus faellt und noch keinen Auftrag hat:** die beiden
Befundtabellen brauchen einen Waechter auf Spaltenzahl und Abschlusspipe. Vier
kaputte Zeilen in einer Datei, die als "die Wahrheit ueber den Zustand
einzelner Befunde" gefuehrt wird, sind kein Schreibfehler, sondern eine
fehlende Pruefung — und `tests/` enthaelt **kein** `.md`-Pfadliteral
(Gegenprobe T-202/Explore).

Regeln in `docs/plan-restarbeiten.md`. Teamweit L-008 bis L-018, projekteigen
NH-001/NH-002. **Nie geprueft:** Linux/macOS, Fremdinstallation.
