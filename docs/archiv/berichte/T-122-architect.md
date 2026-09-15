# T-122 — Der Berater rechnet im Hauptthread: zwei Entscheidungen (architect)

STATUS: erledigt
AUFTRAG: T-122 — AD-028 zu QA-208 und AD-029 zu QA-209 (`docs/tasks/T-122.md`)
GELESEN: `docs/tasks/T-122.md` · `GOAL.md` (A6 im Wortlaut, F2, Vertrauensentscheid 02.09.) · `docs/state.md` (Zyklus 18, Nummernkreise, drei Nutzerentscheide vom 08.09.) · `CLAUDE.md` · `docs/berichte/T-118-performance-tuner.md` (vollstaendig) · `docs/perf/baselines.md` (S11-A bis S11-H) · `qa/findings.md` QA-208, QA-209, D-1 · `ARCHITECTURE.md` AD-006, AD-007, AD-018, Kopfabschnitt · `UI_SPEC.md` AK-08 bis AK-13, §3.3, §3.5, §3.8 · Kopftexte aller `docs/research/R-001..006` und `docs/legal/C-001..004` (keiner beruehrt eine der beiden Entscheidungen) · Quellstand lesend: `nrplanner/relicpicker.py`, `nrplanner/advisorbar.py`, `nrplanner/advisor/{worker,run,candidates,types}.py`, `nrplanner/inventory.py`, `nrplanner/app.py`, `nrdata/savefile.py`
GEAENDERT: `ARCHITECTURE.md` (drei Stellen nachgezogen + Nachtrag VIII angehaengt, +501/-1) · `docs/berichte/T-122-architect.md` (diese Datei). **Nichts committet, nichts gestaged** — `git status` zeigt genau diese beiden Dateien.
ANNAHMEN: (1) Die Herleitung „666 ms nach dem Vorfilter" setzt voraus, dass die **zweite** Spielstanddatei so viel kostet wie die erste; separat gemessen ist nur eine (2802,7 ms). Die Summe passt (91 % des Ganzen), die Aufteilung ist nicht belegt. Steht in AD-029 im Text. (2) Ich lese den Auftrag „AD-028 (QA-208) und AD-029 (QA-209)" als verbindliche Nummernvergabe des `director`; **AD-027 ist in keiner Datei vergeben** und bleibt eine Luecke. (3) Neuer Text in `ARCHITECTURE.md` schreibt Umlaute nach `CLAUDE.md` um (`ae/oe/ue/ss`), obwohl die Altbestaende der Datei echte Umlaute tragen. Zitate aus Bestandstexten bleiben unveraendert.
NAECHSTER: `director` — dann `ui-ux-designer` (U4, `UI_SPEC` §3.8), parallel `developer` (U1, AD-029 Stufe C, haengt an nichts)
BLOCKIERT DURCH: nichts. Zwei Messungen fehlen, keine davon blockiert eine der beiden Entscheidungen — sie sind als **OF-25** und **OF-26** an den `performance-tuner` adressiert und als Pruefpunkte in `ARCHITECTURE.md` verankert.

---

## 1. Urteil in fuenf Zeilen

1. **AD-028 (QA-208):** Der Picker-Weg bekommt eine **zweite Instanz der
   vorhandenen `AdvisorController`-Klasse** mit eigener Antwortfunktion,
   eigener Entprellung (100 ms) und eigenem Cache (64). Kein zweiter
   Thread-Weg, kein zweiter Generationszaehler, keine zweite
   Schluesselform.
2. **Ja, es wird sichtbar** — `UI_SPEC` §3.8 steht woertlich auf der
   widerlegten Zahl und muss neu geschrieben werden. **Der `ui-ux-designer`
   geht vor dem `developer`.** Ich habe die Oberflaeche nicht entworfen.
3. **Der Generationszaehler gilt jetzt auch im Picker.** Die Randbedingung
   der alten Aussage („die Rechnung kehrt zurueck, bevor der Dialog oeffnet")
   entfaellt genau durch diesen Entwurf; `relicpicker.py:1169-1171` ist der
   zweite, schon heute vorhandene Fall.
4. **AD-029 (QA-209):** Zuerst das **Lesen selbst** (Vorfilter, eine Datei,
   vollstaendig gemessen). Die **Verlagerung in einen Worker** wird nicht auf
   Verdacht gebaut, sondern haengt an einer Nachmessung mit benanntem
   Ausloeser (`inventory.load` ueber 250 ms → bauen, darunter nicht).
5. **Die Vertrauensgrenze wird beruehrt** — der Vorfilter entscheidet, welche
   Versaetze SEC-022 ueberhaupt zaehlt, und die Gleichheit ist nur an echten
   Spielstaenden belegt. **Fall fuer den `security-reviewer`**, vor dem
   Abschluss.

## 2. Die Bestandsaussagen des Auftrags — nachgeprueft, alle bestaetigt

Ich habe jede Aussage am Arbeitsbaum geprueft, nicht aus dem Auftrag
uebernommen.

| Aussage | Befund |
|---|---|
| Direkter Aufruf `relicpicker.py:326-328` | **bestaetigt** (`grep -n` auf `return Ranking(advisor_candidates.pool(`) |
| Docstring `276-281`, Wortlaut | **bestaetigt**, Zeile 276 beginnt mit „The pool is computed here" |
| `AdvisorController` in `worker.py:141`, Nutzer `advisorbar.py:52,438,441` | **bestaetigt**; `grep -rn "AdvisorController" nrplanner/` zeigt **0** Treffer in `relicpicker.py` |
| Zweite Fundstelle `1169-1171` (`_sort_chosen`) | **bestaetigt**, `NAME_ORDER` rechnet nichts neu |
| AD-018 Punkt 4 auf `ARCHITECTURE.md:1588-1590`, die ~51 ms auf 1597-1599 | **bestaetigt** (vor meiner Aenderung) |
| Kein Commit an `relicpicker.py` seit 08.09. | **bestaetigt**, `git log --since=2026-09-08 -- nrplanner/relicpicker.py` leer |
| 318,1 ms / 6,15 s / Faktor 45 | **bestaetigt** in `docs/perf/baselines.md` S11-C und S11-E |

**Eine Praezisierung, die der Auftrag nicht hatte:** Der Faktor **45 gilt fuer
den Scan**, nicht fuer `inventory.load`. Ueber den ganzen Ladevorgang sind es
hergeleitet **9,2x** (6147,6 → 666 ms). Das ist genau die Verwechslung
Kandidatenmenge/Vorschlag in anderer Kleidung, und sie haette die Reihenfolge
der Stufen falsch entschieden. Herleitung steht in AD-029.

## 3. Was ich in `ARCHITECTURE.md` geaendert habe

1. **Kopfabschnitt „Gemessene Grundzahlen"** — Warnkasten: die **Laufzeiten**
   dieses Abschnitts (0,18–0,25 ms je Bewertung, 0,46 s Gesamtlauf) sind
   ueberholt, die **Mengenangaben** tragen weiter; fuer jede Zeitzahl gilt ab
   jetzt `docs/perf/baselines.md`. Das ist der strukturelle Teil des Fixes:
   der naechste Entwurf haette sonst wieder aus 0,25 ms gerechnet.
2. **AD-018 Kopfzeile** — Status „aktiv in der Sache; Punkt 4 und die
   Laufzeittabelle nachgezogen durch AD-028". Nicht ueberschrieben.
3. **AD-018 Laufzeittabelle** — Korrekturkasten mit **beiden** Zahlen
   (`~51 ms` gerechnet → 318,1 ms gemessen, mit Umgebung nach L-009), und
   was daran haelt (das Verhaeltnis) und was faellt (der Satz „unter der
   250-ms-Schwelle").
4. **AD-018 Punkt 4** — Nachtrag: dieser Punkt wurde als sein Gegenteil
   gebaut; AD-028 zieht ihn nach.
5. **Nachtrag VIII angehaengt** — AD-028, AD-029, Umsetzungsschnitt U1–U8,
   Risiken, „Bewusst nicht getan", OF-25 bis OF-27.

## 4. Was ich **nicht** getan habe

- **Keine Zeile Anwendungscode, kein Test, kein UI-Entwurf.** `git status`
  zeigt `ARCHITECTURE.md` und diesen Bericht.
- **Nichts committet** — der Auftrag verbietet es, und ein `developer` haelt
  parallel `tests/`.
- **Das Programm nicht gestartet, nichts gemessen.** Alle Zahlen sind
  zitiert, jede mit Fundstelle.
- **Die Oberflaeche des Wartezustands nicht entworfen** — benannt, was zu
  entscheiden ist, nicht wie.
- **`GOAL.md`, `docs/state.md`, `qa/findings.md`, `docs/tasks/` nicht
  angefasst.**

## 5. Antworten auf die fuenf Vorgaben zu QA-208

1. **Ueber den vorhandenen Controller oder einen eigenen Weg?** Ueber die
   vorhandene **Klasse**, aber eine **zweite Instanz**. Was der Controller
   mitbringt und der Picker braucht: QThread-Muster, Entprellung,
   Generationszaehler, Cache, kooperativer Abbruch (`candidates.pool` nimmt
   `should_cancel` bereits). Was er mitbringt und der Picker **nicht**
   brauchen kann: die **Antwortform** (`AdvisorResult` traegt 20 Vorschlaege,
   der Picker braucht alle 206 Kandidaten mit beiden Zielrichtungen), den
   **Weg** (`run.run` 403,3 ms gegen `pool` 321,2 ms — 82 ms fuer Beam und
   Erklaerungen, die der Picker nicht zeigt) und vor allem die **eine Spur**:
   eine Instanz laesst hoechstens einen Lauf zu (AD-006.4), also braeche das
   Oeffnen eines Slots einen laufenden `Optimize` ab, was AK-08 aushoehlt.
2. **Was sieht der Spieler in den 318 ms?** Das ist die Frage des
   `ui-ux-designer`, und sie ist jetzt zwingend: 318,1 ms liegen ueber der
   250-ms-Schwelle, ab der AK-10 einen Wartezustand **verlangt**, waehrend
   `UI_SPEC` §3.8 heute das Gegenteil vorschreibt und es aus den ~51 ms
   begruendet. Halb ist es schon gebaut (§3.3 reserviert den Platz, `…` steht
   an der Stelle der Zahl, AK-41 verlangt 0 px Hoehenunterschied); **offen
   ist, was mit Ordnung, Kopfzeile und Spitzenwert-Chips passiert**, die
   heute beim Bauen des Rasters aus der Rangfolge entstehen — eine
   Neusortierung 320 ms nach dem Oeffnen bewegt Karten unter dem Zeiger.
3. **Braucht der Picker jetzt einen Zaehler?** **Ja**, und keinen zweiten:
   der Zaehler gehoert der Instanz. Die alte Begruendung war an die
   Modalitaet **und** an „die Rechnung kehrt zurueck, bevor der Dialog
   oeffnet" gebunden; die zweite Haelfte entfaellt durch diesen Entwurf, und
   `relicpicker.py:1169-1171` ist der Fall, der schon heute im offenen Dialog
   neu rechnet.
4. **AD-018 nachgezogen, nicht ueberschrieben** — siehe Abschnitt 3, mit
   beiden Zahlen im Text.
5. **Regressionstest** — drei Waechter mit toetender Mutation, im
   Standardlauf, ohne Wanduhr-Schranke: **W1** strukturell (nur
   `advisor/worker.py` darf `run.run`/Pool-Funktion/`candidates.pool`
   aufrufen; Erwartung aus einer Aufruferliste im Test, **nicht** aus
   `relicpicker.py` — L-008b), **W2** der erste Anstrich traegt `PENDING`
   statt Zahlen, **W3** die ueberholte Antwort erreicht nichts. Zu L-004: der
   Waechter hat **keine** aktivierende Buildsystem-Zeile, das ist die
   Herleitung der Unnoetigkeit und steht so im Dokument.

## 6. Antworten auf die vier Vorgaben zu QA-209

1. **Was kostet die 6,15 s** — belegt an S11-E, nicht vermutet:
   `savefile.read_owned_relics` 6,562 s Eigenzeit in 28 Aufrufen **unter
   cProfile**, darin **10 293 488** `struct.unpack_from`; Ursache ist die
   Schleife ueber jeden 4-Byte-Versatz. 28 Slots gelesen (zwei Dateien à 14),
   einer gebraucht. Gerufen im Hauptthread bei jedem Start (`app.py:1575`)
   und jedem `Rescan` (`app.py:1682`).
2. **Form des Gegenentwurfs:** eine **Aenderung am Lesen selbst** (Vorfilter
   ueber das immer gleiche hoechste Byte) — das ist der gemessene Teil. Die
   **Verlagerung** ist eine zweite, getrennte Stufe und wird **nicht**
   mitentschieden, sondern an eine Nachmessung gebunden. Beides zugleich
   waere Architektur auf Vorrat: die Verlagerung verlangt einen dritten
   Fensterzustand („wird gelesen" — `owned=None` heisst heute „kein
   Spielstand gefunden"), eine neue Thread-Grenze und eine Spec-Ergaenzung.
3. **Vertrauensgrenze: ja, beruehrt.** Der Vorfilter entscheidet, welche
   Versaetze geprueft und damit welche Records fuer die SEC-022-Dichteschranke
   gezaehlt werden; die Gleichheit ist an 28 von 28 Slots **echter**
   Spielstaende belegt, also gerade nicht an der Dateiklasse, fuer die
   SEC-022 gebaut ist. **Der `security-reviewer` prueft das an der
   praeparierten Datei aus T-096, bevor der Fix als abgeschlossen gilt.** Die
   Annahme `relic_id < 0x01000000` gehoert als Pruefung in den Code.
4. **Umfang in Dateien:** Stufe C **1** Produktivdatei (`nrdata/savefile.py`)
   + Tests; Pruefung 0; Nachmessung 0; Stufe B **3** Produktivdateien
   (`nrplanner/inventory.py`, ein neues kleines Qt-Modul, `nrplanner/app.py`)
   + Tests, **nach** der Spec. Drei bis vier Auftraege, keiner an der
   Fuenf-Dateien-Grenze.

## 7. Was der `director` von mir wissen muss, ohne dass es beauftragt war

- **AD-027 existiert nicht.** Volltextsuche ueber das ganze Repository,
  08.09.2026, null Treffer; `docs/state.md` fuehrt den Kreis ab AD-030. Die
  Luecke ist im Nachtrag VIII vermerkt, damit sie niemand „auffuellt".
- **A6s dritte Zeile ist auch fuer den `Optimize`-Weg nie vollstaendig
  gemessen worden** (OF-26). `AdvisorController.ask` baut die Anfrage,
  friert 309 Kopien ein und rechnet einen sha256 ueber 309 Zeilen — **im
  Hauptthread**, bei jeder Frage. Der Weg gilt in T-114 und T-118 als
  „haelt", aber gemessen wurde der **Lauf**, nicht der Rest. Die Zahl kann
  klein sein; sie ist unbekannt, und A6 haengt daran.
- **A6s 6-s-Zahl gilt fuer einen Lauf, waehrend sonst nichts rechnet**
  (OF-25). Nach AD-028 sind zwei rechnende Spuren ein vorgesehener Zustand
  (AK-08), und 19 % Luft ueberleben eine GIL-Teilung nicht zwangslaeufig.
  Das ist kein Argument gegen AD-028 — die Alternative (Slot oeffnen bricht
  `Optimize` ab) ist schlechter —, aber A6 braucht danach entweder die Zahl
  oder die Randbedingung.
- **Dieselbe gerechnete Zahl steht in drei Dateien** (OF-27). Zwei sind
  korrigiert, die dritte (`UI_SPEC` §3.8) gehoert dem `ui-ux-designer`. Die
  Regel dahinter — eine Zahl in einem Entwurfstext traegt, ob sie gemessen
  oder gerechnet ist — ist eine Entscheidung des `director`, nicht meine.
- **T-118 P1a bleibt sinnvoll und ersetzt AD-028 nicht.** 26,7 % weniger
  Rechnung im Picker sind ein eigener Auftrag; sie bringen die Slot-Frage auf
  245,5 ms und damit **nicht** unter 50 ms. Wer P1a fuer die Loesung von
  QA-208 haelt, macht denselben Fehler noch einmal, nur mit einer kleineren
  Zahl.
- **`docs/plan-restarbeiten.md` E-1** wartet weiter auf die von T-118
  gemessene Zahl (99,1–99,2 %); die Datei gehoert weder T-118 noch mir.

## 8. Was noch nicht verifiziert ist

- **Die Suite ist nicht gelaufen.** Ich habe keine Codezeile angefasst; ein
  Volllauf waere Selbstbestaetigung. Die Zahl aus `docs/state.md` (1257
  passed, 9 skipped) gilt unveraendert und wird von T-123 (`developer`,
  parallel, nur `tests/`) bewegt, nicht von mir.
- **Die Gleichheit der kanonischen Anfrageform nach AD-028 Punkt 3** ist
  argumentiert (`candidates.base_state_for` behandelt beide Formen gleich,
  Docstring woertlich), **nicht gemessen**. Der `developer` weist sie in U5a
  am `SlotPool` nach; als Rueckweg steht in den Pruefpunkten, was zu tun ist,
  wenn sie nicht haelt.
- **Die 666 ms** sind hergeleitet, nicht gemessen. Sie entscheiden die
  Reihenfolge der Stufen und sind ausdruecklich **kein** Abnahmewert.
