# T-118 — S11: das Budget messen und setzen (performance-tuner)

STATUS: erledigt
AUFTRAG: T-118 — S11: das Budget messen und setzen (Erstlauf, `performance-tuner`)
GELESEN: `~/.claude/agents/_rahmen.md` · `docs/tasks/T-118.md` · `GOAL.md` (A6 im Wortlaut) · `docs/state.md` (D-1, Zyklus-16-Abschnitt, Isolierung) · `docs/plan-restarbeiten.md` (E-1) · `ARCHITECTURE.md` Zeilen 1532–1650 (AD-018), 738–760 (AD-007), 2549, 3280 · `docs/berichte/T-067-developer.md` (Herkunft der 941,6 ms und der 0,247 ms) · `UI_SPEC.md` AK-09 bis AK-13, §3.8 · Quellstand: `nrplanner/advisor/{run,worker,evaluate,candidates}.py`, `nrplanner/{model,relicpicker,inventory,paths,favourites,shortcut}.py`, `nrdata/savefile.py`, `scripts/measure_advisor_{search,picker}.py`
GEÄNDERT: `docs/perf/baselines.md` (neu, committet `f2fca6a` Geruest und `44dcaed` Inhalt) · `docs/berichte/T-118-performance-tuner.md` (diese Datei)
ANNAHMEN: (1) Der Auftrag nennt „110 gespeicherte Builds"; im Einstellungsspeicher stehen **null** benannte Builds — die 110 sind die **Loadouts im Spielstand** (11 je Nightfarer x 10). Gemessen wurde mit beidem im Zustand des echten Spielstands. (2) `ARCHITECTURE.md` weist mir „beide Werte" der Entprellung zu; ich lese das als Picker-Wert **und** Gesamtlauf-Wert. (3) Der Energieplan `Legion Quiet Mode` ist die Wahl des Nutzers und damit die gueltige Zielumgebung; ich habe ihn nicht veraendert.
NÄCHSTER: director
BLOCKIERT DURCH: nichts. Zwei Entscheidungen liegen beim `director`: der A6-Zielwert (Abschnitt 2, Satz zum woertlichen Uebernehmen) und die Reihenfolge des Optimierungsplans (Abschnitt 4). Nichts liegt in einem Klon; alles Genannte ist im Arbeitsbaum committet.

---

## 0. Urteil in vier Zeilen

1. **A6 kann seine Zahl bekommen** — hergeleitet in Abschnitt 2. Die
   Antwortzeiten halten sie; **die erste Haelfte von A6 haelt auf dem
   Hauptweg nicht**: der Picker rechnet 318 ms im **Hauptthread**.
2. **Die beiden Architekturwerte sind gesetzt** (Abschnitt 3): Entprellung
   **100 ms Picker / 250 ms Gesamtlauf**, LRU **64 — bedingt**.
3. **D-1 ist nicht bestaetigt und nicht widerlegt.** `model.compute` traegt
   heute **81 % von rund 5090 ms**, nicht 94 % von 941,6 ms. Ob das eine
   Regression ist, ist von hier aus **nicht entscheidbar** (Abschnitt 5).
4. **Der groesste einzelne Posten des Programms ist gar nicht der Berater**,
   sondern das Lesen des Spielstands: **6,15 s im Hauptthread**, bei jedem
   Start und bei jedem `Rescan`. Obergrenze eines Gegenentwurfs gemessen:
   **45x** (Abschnitt 4, P2).

---

## 1. Scope, Messszenario, Umgebung, Isolierung

### 1.1 Was gemessen wurde und was nicht

Gemessen, weil beauftragt: die Rechenzeit des Beraters auf dem echten
Spielstand, kalt und warm, und daraus A6s Zahl, die zwei Architekturwerte und
ein priorisierter Plan. **Nichts optimiert** — jede Codeaenderung ist ein
Folgeauftrag mit den Zahlen hier als Vorher-Wert.

Vollstaendige Umgebung, Szenariendefinitionen und alle Tabellen stehen
versioniert in **`docs/perf/baselines.md`** (acht Abschnitte S11-A bis S11-H).
Dieser Bericht nennt nur, was zur Entscheidung noetig ist.

### 1.2 Die Umgebung — und warum sie hier vorn steht

| | |
|---|---|
| Rechner | AMD Ryzen 7 5800H, 8 Kerne / 16 Threads |
| **Takt** | **1102 MHz gegen 3201 MHz Nennwert**, fuenf Stichproben, alle 1102 |
| **Energieplan** | **`Legion Quiet Mode`** |
| Python | 3.12.10 CPython |
| **Rechenlastprobe** | **1205 ms** fuer 3 Mio. `x += i*i` (1157–1232, n=5) |
| Fremdlast | zwei `find /`-Prozesse aus fremden Laeufen, seit 03:16 bzw. 03:35 |
| Codestand | `76f1887` |
| Daten | 309 Relikte, 110 Loadouts, `data_version` 10350000, `extract_version` 11 |

**Der Rechner lief die ganze Zeit auf einem Drittel seines Nenntakts.** Das
ist kein Messfehler, sondern der Energieplan des Nutzers — und damit die
richtige Zielumgebung: gemessen wird gegen die Grenzen des Zielsystems, nicht
gegen eine Wunschmaschine. Die Zahlen sind der **konservative** Fall.

**Die Reihe ist in sich stabil, und das ist geprueft, nicht behauptet.** Zum
Abschluss habe ich zwei Werte vom Sitzungsanfang wiederholt: Picker warm
317,9 ms gegen 321,2 ms (1,0 % Abweichung, Rauschband 15,5 %), Spielstand
lesen 6106 ms gegen 6147 ms (0,7 %). Die Rechenlastprobe streut ueber fuenf
Laeufe um 6 %. Alle Vergleiche **innerhalb** dieses Berichts sind damit
belastbar; nur der Vergleich mit **T-067** ist es nicht (Abschnitt 5).

**Befund an den `director`, ohne Nummer** — *Zwei verwaiste
`find /`-Prozesse belegen seit sieben Stunden CPU.* PID 1620 (`find / -iname
_rahmen.md`, gestartet 03:16:27, 26 324 s CPU) und PID 5144 (`find /
-maxdepth 6 -iname scratchpad`, gestartet 03:35:58, 25 180 s CPU). Beide
stammen aus fremden Laeufen und sind genau die Bauform, vor der die
Rollendefinition warnt. Ich habe sie **nicht beendet** — es sind nicht meine
Prozesse. Sie haben meine Messung nicht verdorben (zusammen rund 0,4 Kerne
von 16, und die Stabilitaetsprobe oben zeigt keine Drift), aber sie gehoeren
beendet.

### 1.3 Die Datenschutzsperre — Nachweis mit Gegenprobe

**Lesen ja, schreiben nein.** Alle drei Umlenkungen sind nachgewiesen, und
zwar so, dass der Nachweis **anschlagen kann**: dieselbe Pruefung wurde im
umgelenkten und im ungelenkten Fall gefahren, und sie muss verschiedene Pfade
zeigen. Zeigt sie denselben, greift die Umlenkung nicht.

| Pruefpunkt | umgelenkt (dieser Lauf) | echt (Gegenprobe) |
|---|---|---|
| `paths.cache_dir()` (`paths.py:20`) | `…\T-118\localappdata\NightreignHelper` | `C:\Users\Daniel\AppData\Local\NightreignHelper` |
| `shortcut.start_menu_dir()` (`shortcut.py:44-49`) | `…\T-118\appdata\Microsoft\…\Programs` | `C:\Users\Daniel\AppData\Roaming\Microsoft\…\Programs` |
| `favourites.ORG/APP` (`favourites.py:25`) | `T118-PerfTuner/T118-NightreignHelper` | `DankYeeter/NightreignHelper` |

Der Lesetest allein sagt nur, welchen Namen ein Modul traegt. Deshalb
zusaetzlich eine **echte Schreibprobe**: `favourites._settings().setValue(…)`
landete nachweislich unter
`HKCU\Software\T118-PerfTuner\T118-NightreignHelper\T118` (mit `reg query`
gezeigt), waehrend der Export von `HKCU\Software\DankYeeter` **byte-gleich**
blieb.

**Abschlusspruefung, vier schutzwuerdige Baeume, sha256 ueber Pfad, Groesse
und Inhalt jeder Datei:**

| Baum | vorher | nachher |
|---|---|---|
| `%LOCALAPPDATA%\NightreignHelper` | `35872fe8717ebb0e` | `35872fe8717ebb0e` |
| `%APPDATA%\Nightreign` (die Spielstaende) | `8b440d275ed26816` | `8b440d275ed26816` |
| Startmenue `…\Programs` | `fed716af224e6cfc` | `fed716af224e6cfc` |
| `%LOCALAPPDATA%\NightreignHelper-Testabzug` | `35872fe8717ebb0e` | `35872fe8717ebb0e` |
| `HKCU\Software\DankYeeter` (Registry-Export) | md5 `8b29fdf5…` | md5 `8b29fdf5…` |

**Das Messmittel selbst hat eine Positivkontrolle:** derselbe
Fingerabdruck ueber ein Testverzeichnis aendert sich, wenn eine Datei
hinzukommt (`836eab42` → `c4d8f4ce`) **und** wenn sich ein einziges Byte
aendert (`→ 5487db28`). Ein Fingerabdruck, der nur „gleich" sagen kann, waere
kein Nachweis.

**Aufgeraeumt, geprueft statt zugesichert:** der Registry-Zweig
`HKCU\Software\T118-PerfTuner` ist geloescht (`reg query` meldet ihn als nicht
vorhanden), die Messbaeume unter `T-118/` sind entfernt, kein `python.exe` aus
diesem Lauf laeuft noch. **Ich habe keinen Server gestartet**, also ist kein
Port zu pruefen.

### 1.4 Der feste Testabzug — Ersparnis gemessen (E-1)

| Weg | Zeit | n | Ergebnis |
|---|---|---|---|
| **Neubau** (`write_snapshot` + `iconbuild.build`) | **293,81 s und 310,07 s** | 2 | 841 Dateien, 19,8 MiB |
| davon Abzug | 169,38 s / 184,49 s | 2 | |
| davon Symbole | 124,43 s / 125,58 s | 2 | |
| **Kopie des Testabzugs** | **2,54 s** Median (2,42–2,75) | 5 | 841 Dateien, 19,8 MiB |

**Ersparnis: 291,3 bis 307,5 s je Lauf = 99,1–99,2 %.** Die in
`docs/plan-restarbeiten.md` E-1 als „erwartet, nicht gemessen" gefuehrte Zahl
ist damit gemessen — und liegt am **oberen** Rand der dort genannten Spanne
(„107 s bis 5 min"): der Neubau ist auf diesem Rechner in diesem Energieplan
durchgaengig knapp fuenf Minuten, nicht 107 s.

**Und die Vorlage ist nachweislich gleichwertig, nicht nur gleich gross:** der
frisch gebaute Baum hat denselben Inhalts-Fingerabdruck wie der Testabzug
(`35872fe8717ebb0e`, 841 Dateien). Bisher war das eine Annahme.

*Empfehlung an den `director`:* die Zahl in `docs/plan-restarbeiten.md` E-1
nachtragen (mein Auftrag beruehrt diese Datei nicht).

---

## 2. A6 bekommt seine Zahl

### 2.1 Was gemessen wurde

| Frage | kalt (n=5) | warm p50 (n=25) | Spanne warm | Schwelle |
|---|---|---|---|---|
| Gesamtlauf `Optimize`, sechs freie Slots | 4901,6 ms | **5023,6 ms** | 4872,1–5225,2 ms | 5 % |
| Picker, weisser Slot, ueber `run.run` | 378,9 ms | **403,3 ms** | 355,3–445,8 ms | 12 % |
| Picker, weisser Slot, `candidates.pool` (heutiger Weg) | 310,7 ms | **321,2 ms** | 283,8–382,2 ms | 16 % |
| alle sechs Slots durchgeklickt | 609,3 ms | 610,7 ms | 577,7–655,2 ms | 8 % |

**Kalt und warm sind praktisch gleich** — und das ist selbst ein Ergebnis: es
gibt **kein Warmlaufen innerhalb** des Beraters, keine Memoisierung, die ein
zweiter Lauf nutzen wuerde. Der ganze Unterschied zwischen „kalt" und „warm"
liegt im **Prozessstart** (6,59 s, Abschnitt 4/P2). Fuer die LRU heisst das:
**der Cache ist der einzige warme Pfad, den es ueberhaupt gibt.**

### 2.2 Der Satz, so wie er nach `GOAL.md` uebernommen werden kann

> **A6** Die Berechnung blockiert die Oberflaeche nicht: sie laeuft im
> Hintergrund, das Fenster bleibt bedienbar, und bei grossen
> Relikt-Bestaenden bleibt die Antwortzeit im gemessenen Budget — eine
> **Slot-Frage des Beraters ist im Median unter 500 ms** beantwortet, ein
> **Gesamtlauf (`Optimize`) unter 6 s**, und **keine Beraterrechnung haelt
> den Hauptthread laenger als 50 ms an**. Messfall: 309 Relikte, 110
> gespeicherte Builds, `Wylder's Chalice` mit Deep of Night, sechs freie
> Slots, Zielgeraet und Messumgebung nach `docs/perf/baselines.md`.

### 2.3 Woher jede der drei Zahlen kommt

**500 ms fuer eine Slot-Frage.** Gemessen 403,3 ms (warm, n=25, Spanne
355,3–445,8). Das Rauschband dieses Szenarios ist 12 %; 500 ms liegt **24 %
ueber** dem Median und damit sicher ausserhalb. Ein knapperer Wert wuerde bei
jeder zweiten Messung kippen, ohne dass sich etwas geaendert haette.

**6 s fuer den Gesamtlauf.** Gemessen 5023,6 ms (warm, n=25, Spanne
4872,1–5225,2). Rauschband 5 %; 6 s liegt **19 %** darueber. Der Gesamtlauf
hat ausserdem einen anderen Vertrag als der Picker: `UI_SPEC` AK-10 gibt ihm
Fortschrittsbalken, Wartetext und `Cancel`, AK-11 verlangt sichtbare Reaktion
binnen 200 ms. Das ist gemessen erfuellt — ein Abbruchwunsch beendet den Lauf
in der Vorsortierung nach 2,3 ms, in der Beam-Ebene nach hoechstens 199,7 ms.

**50 ms fuer den Hauptthread.** Drei Bilder bei 60 Hz. Das ist die Zahl, die
den **ersten** Halbsatz von A6 pruefbar macht — bisher war „blockiert die
Oberflaeche nicht" eine Aussage ohne Messgroesse, und genau deshalb konnte
T-114 sie nur an einem Weg pruefen.

### 2.4 Haelt der heutige Stand die Zahl?

| Teil des Budgets | heute | Urteil |
|---|---|---|
| Slot-Frage unter 500 ms | 403,3 ms | **haelt** (24 % Luft) |
| Gesamtlauf unter 6 s | 5023,6 ms | **haelt** (19 % Luft) |
| Hauptthread hoechstens 50 ms | **318,1 ms** | **haelt nicht** |

**Der dritte Teil haelt nicht, und das ist der wichtigste Befund dieses
Laufs.**

**Befund an den `director`, ohne Nummer** — *Der Berater rechnet auf dem
Hauptweg im Hauptthread, entgegen AD-006.1 und AD-018 Punkt 4.*
`relicpicker.SlotAdvice.ranking` (`nrplanner/relicpicker.py:325-328`) ruft
`advisor_candidates.pool` **direkt** auf, nicht ueber den
`AdvisorController`. Der Docstring darueber (Zeilen 277–281) nennt den Grund
im Klartext:

> „The pool is computed here, in the calling thread, and that is deliberate:
> AD-018 measures the worst slot at ~51 ms against the 250 ms of AK-09, so
> there is nothing to draw a wait for."

**Die Voraussetzung dieser Entscheidung ist widerlegt.** Der schlimmste Slot
kostet nicht ~51 ms, sondern **318,1 ms** (Median, n=25, Spanne
289,6–358,9) — **6,3x** die Annahme, und **oberhalb** der 250-ms-Schwelle aus
AK-09, ab der ein Wartezustand gezeigt werden **muss**. AD-018 Punkt 4 sagt
selbst: „Auch 50 ms gehören nicht in den Hauptthread."

Zwei Folgen, beide mit Zahl:
- Beim Oeffnen des Pickers am weissen Slot steht das Fenster **318 ms**.
- Der Wechsel der Zielrichtung **im offenen Dialog**
  (`relicpicker.py:1171`) rechnet dieselben 318 ms noch einmal, ebenfalls im
  Hauptthread — das ist eine laufende Interaktion, kein Dialogaufbau.

**Warum T-114 das nicht gesehen hat:** A6s erste Haelfte wurde am
`Optimize`-Weg geprueft, und **dort haelt sie** — der Lauf sitzt im
`QThread`, der Generationszaehler und die Entprellung greifen. Der
Picker-Weg, seit AD-018 der Hauptweg, wurde nie daran gemessen. Der scharfe
Fall lag einen Schritt weiter auf derselben Achse.

**Ich fixe das nicht** (kein Bugfix, und es ist eine Architekturfrage). Es
gehoert an `director` → `architect`/`developer`.

### 2.5 Was das Budget **nicht** deckt — und wer es messen muss

Das Budget deckt die **Berechnung**, weil A6 von der Berechnung spricht. Vom
Klick bis zur Anzeige liegt aber noch der **Bau des Dialogs** dazwischen, und
der ist zehnmal so teuer wie die Rechnung:

| Slot | Karten | Rechnung | Dialogbau | Summe |
|---|---|---|---|---|
| 0 | 50 | 94,5 ms | 944,9 ms | 1039,5 ms |
| 2 | 51 | 107,7 ms | 973,8 ms | 1081,5 ms |
| 5 | 30 | 60,1 ms | 619,7 ms | 679,8 ms |

**Rund 18,5 ms je Karte.** Fuer den weissen Slot mit 206 Karten waeren das
hochgerechnet ~3,8 s — hochgerechnet, nicht gemessen.

**Und die Umgebung dieser Zahlen ist nicht die des Nutzers (L-009):**
Qt-Plattform `offscreen`, Stil `fusion`, logische Pixel, ohne Zeichnen. Es
sind **Untergrenzen**. Der Kelch des Fensters beim Start hatte ausserdem
keinen weissen Slot, deshalb keine 206 Karten in der Messung.

*Empfehlung:* das gehoert dem `ui-ux-designer` (wahrgenommene Leistung,
Wartezustand, Nachladen der Karten) und dem `developer`, nicht mir — und es
braucht eine Messung **am Bildschirm**, nicht offscreen.

---

## 3. Die zwei Werte, die `ARCHITECTURE.md` mir zuweist

### 3.1 Entprellung — `ARCHITECTURE.md` Zeilen 1618–1622

> „Neu ist nur die Empfehlung, die Entprellung für den Picker-Pfad **kürzer**
> zu setzen als für den Gesamtlauf (Vorschlag 100 ms gegen 250 ms) — 50 ms
> Rechnung hinter 250 ms Wartezeit fühlt sich träger an, als sie ist. Der
> `performance-tuner` setzt beide Werte in S11."

**Gesetzt: Picker 100 ms, Gesamtlauf 250 ms** (`worker.py:63`,
`DEBOUNCE_MS`, bleibt bei 250; der Picker-Wert ist neu und existiert heute
nirgends, weil der Picker gar nicht entprellt).

**Der Gesamtlauf bleibt bei 250 ms — begruendet mit der Schwelle, nicht mit
Geschmack.** Die Antwort dauert 5023,6 ms. Eine Verkuerzung von 250 auf
100 ms verschiebt die Gesamtantwort um 150 ms, also **2,8 %** — unterhalb der
Signifikanzschwelle dieses Szenarios (5 %). Ein Wert, dessen Aenderung man
nicht messen kann, wird nicht geaendert.

**Der Picker bekommt 100 ms — aber aus einem anderen Grund, als der
`architect` hatte.** Sein Argument („50 ms Rechnung hinter 250 ms Wartezeit")
haengt an einem Rechenwert von ~51 ms; gemessen sind es 403,3 ms. Die
Entprellung ist damit **nicht mehr der beherrschende Posten**. Der Schluss
haelt trotzdem:

| | Entprellung 250 ms | Entprellung 100 ms |
|---|---|---|
| Gesamtantwort Picker | 653 ms | **503 ms** |
| Anteil der Entprellung | 38 % | 20 % |

150 ms sind **37 % der Rechnung** und **23 % der Gesamtantwort** — beides
weit ueber der 12-%-Schwelle dieses Szenarios. Und der Preis des kuerzeren
Werts ist gemessen und klein: ein Lauf, der gestartet und gleich wieder
verworfen wird, endet **0,4 bis 4,5 ms** nach dem Abbruchwunsch, solange er
in der Vorsortierung steht, und hoechstens 199,7 ms spaeter, wenn er schon in
der Beam-Ebene ist. Ein ueberfluessiger Start kostet also Hintergrund-CPU,
nie eine sichtbare Verzoegerung.

**Bedingung, die dazugehoert:** der Picker-Wert wird erst wirksam, wenn der
Picker ueberhaupt ueber den `AdvisorController` fragt (Abschnitt 2.4). Heute
gibt es auf diesem Weg keine Entprellung, weil es keinen Arbeiter gibt.

### 3.2 LRU-Groesse — `ARCHITECTURE.md` Zeilen 1631–1633

> „Weil die Einträge nun kleiner und zahlreicher sind, ist die LRU-Grösse aus
> AD-007 (Vorschlag 32) neu zu setzen — Aufgabe des `performance-tuner` in
> S11, Vorschlag 64."

**Gesetzt: 64 — bedingt.** Die Zahl stimmt, die Bedingung ist neu.

**Was ein Eintrag kostet** (tiefe Zaehlung, jedes Objekt einmal):

| Eintragsart | Groesse | LRU 32 | LRU 64 | LRU 128 |
|---|---|---|---|---|
| Picker-Antwort (20 Vorschlaege) | 33,4 KiB Median (28,4–38,5) | 1,04 MiB | 2,09 MiB | 4,18 MiB |
| Gesamtlauf-Antwort (40 Vorschlaege) | 279,9 KiB | 8,75 MiB | **17,49 MiB** | 34,99 MiB |

Am Prozess gemessen: 32 Picker-Antworten kosten **+1,7 MiB** Arbeitssatz
gegen 47,7 MiB des Prozesses ohne Fenster.

**Was ein Eintrag bringt.** Sieben Bedienspuren, je eine Folge von Fragen,
wie eine Sitzung sie stellt; gezaehlt wird nur der Schluessel
(`run.cache_key`). Ein Treffer spart gemessene 403 ms (Picker) bzw. 5024 ms
(Gesamtlauf).

| Spur | Fragen | versch. | 16 | 32 | 48 | **64** | 96 | 128 |
|---|---|---|---|---|---|---|---|---|
| Durchklicken (ein Zustand) | 8 | 6 | 25 % | 25 % | 25 % | 25 % | 25 % | 25 % |
| Kelch fuellen + zwei zurueck | 48 | 31 | 35 % | 35 % | 35 % | 35 % | 35 % | 35 % |
| Zielrichtung umschalten | 8 | 2 | 75 % | 75 % | 75 % | 75 % | 75 % | 75 % |
| Level-Schieber 15-12-15 | 42 | 24 | 14 % | 43 % | 43 % | 43 % | 43 % | 43 % |
| gemischte Sitzung | 49 | 43 | 12 % | 12 % | 12 % | 12 % | 12 % | 12 % |
| **Level-Schieber weit 15-5-15** | 126 | 66 | 5 % | **19 %** | 33 % | **43 %** | 48 % | 48 % |
| **beide Ziele x 6 Slots x 4 Zustaende** | 60 | 42 | 10 % | **12 %** | **30 %** | 30 % | 30 % | 30 % |
| **ueber alle Spuren** | | | 49 Tr. | **80 Tr.** | 109 Tr. | **121 Tr.** | 127 Tr. | 127 Tr. |
| **gespart** | | | 19,8 s | **32,3 s** | 44,0 s | **48,8 s** | 51,2 s | 51,2 s |

**Die ersten fuenf Spuren unterscheiden 32 und 128 ueberhaupt nicht.** Haette
ich dort aufgehoert, waere die Antwort „32 reicht" gewesen — und sie waere
falsch begruendet gewesen, weil keine dieser Spuren weit genug zurueckgreift,
um den Unterschied ueberhaupt sehen zu koennen. Erst die beiden letzten
Spuren sind der Fall, in dem die Pruefung **anschlagen** kann: ein weit
gezogener Level-Schieber (66 verschiedene Schluessel) und ein Kelch, der
unter beiden Zielrichtungen gefuellt wird (42). Beides sind Bedienungen, die
`UI_SPEC` und AD-018 ausdruecklich vorsehen.

**Der Knick liegt bei 64:** 32 → 64 bringt **+41 Treffer (+16,5 s)** fuer
+1,05 MiB; 64 → 128 bringt nur **+6 Treffer (+2,4 s)** fuer weitere
+2,09 MiB. 128 kauft ein Siebtel des Gewinns zum doppelten Preis.

**Die Bedingung — und sie ist heute nicht erfuellt.** Die obige Rechnung
gilt fuer **Picker**-Eintraege. Heute landet **kein einziger** davon im
Cache: der `AdvisorController` und damit `ResultCache` werden ausschliesslich
von `AdvisorBar` benutzt, und der Picker geht am Controller vorbei
(Abschnitt 2.4). Der Cache kann heute also nur Gesamtlauf-Eintraege halten —
280 KiB das Stueck, und in der Spur „gemischte Sitzung" sind **alle sieben**
`Optimize`-Fragen verschieden, also **null Treffer**.

**Damit lautet die Empfehlung praezise:**

> **64, sobald der Picker ueber den `AdvisorController` fragt.** Bis dahin
> bleibt es bei **32**: eine Erhoehung allein wuerde den schlimmsten Fall von
> 8,75 auf 17,49 MiB heben, fuer einen Gewinn, den ich mit **0 Treffern**
> gemessen habe.

**Trade-off, ausdruecklich:** 64 kostet +1,05 MiB (Picker-Betrieb) bis
+8,75 MiB (reiner Gesamtlauf-Betrieb) fuer bis zu 16,5 s gesparte Rechenzeit
je Sitzung. Bei 47,7 MiB Grundverbrauch ohne Fenster ist der Picker-Fall
billig und der Gesamtlauf-Fall nicht. Wer beides in einem Cache haelt, sollte
die Groesse nach Eintragsart begrenzen — das ist aber ein Entwurf und
gehoert dem `architect`.

### 3.3 Der Messpunkt, den `ARCHITECTURE.md` Zeile 1637–1641 ausdruecklich verlangt

> „der Berater ist jetzt an der Interaktion beteiligt statt daneben; jede
> künftige Verlangsamung von `model.compute()` wird sofort spürbar, nicht
> erst auf Knopfdruck. Das ist der Preis dieser Entscheidung und gehört als
> Messpunkt in S11."

**Gemessen und eingetragen** als S11-D in `docs/perf/baselines.md`: eine
einzelne Bewertung eines vollen Sechs-Relikt-Builds kostet **1,095 ms**
(Median, n=300, Spanne 0,879–2,252). Das ist der Messpunkt, an dem eine
Verlangsamung von `model.compute` zuerst sichtbar wird; Schwelle 10 %.

**Und der Preis ist bereits faellig:** bei 1,54 ms je Kandidat und 206
Kandidaten am weissen Slot ist die Interaktion heute schon bei 318 ms.

---

## 4. Der priorisierte Optimierungsplan

Sortiert nach Wirkung x Aufwand. **Nichts davon ist umgesetzt.** Jede Zeile
ist ein Folgeauftrag mit dem Vorher-Wert aus `docs/perf/baselines.md`.

### P1 — `model.compute_qualitative` baut in jeder Bewertung Text, den fast niemand liest

**Ursache.** `model.compute` ruft am Ende `compute_qualitative` auf
(`model.py:1150`). Der Block tut **zweierlei**, und nur eins davon wird im
Suchpfad gebraucht:

| Was der Block tut | Wer liest es |
|---|---|
| entscheidet, **welche** Effekte geparkt sind → `Build.situational` | **die Vorsortierung**, `candidates.py:157` (`_brought_an_uncounted_condition`), fuer die A7-Zeile „N of your relics carry effects that only apply under a condition" — sie liest **nur** `entry.effect_id` und `entry.live` |
| baut den **Text** dazu (`name`, `detail`, `why`, `Build.qualitative`) | ausschliesslich `explain.py`, also die 20 bzw. 40 Builds, die wirklich erklaert werden |
| — | die Zielrichtungen lesen von beidem **nichts**: `goals.py` greift nur auf `build.rates` und `build.derived` zu |

In einem Gesamtlauf faellt dafuer `effecttext.describe` **19 483** mal an und
`model.is_conditional` **98 838** mal — fuer 4084 Bewertungen, von denen 3621
im Beam liegen, wo weder Text **noch** `situational` gelesen wird.

**Deshalb zwei Stufen, beide gemessen** (je 5 Laeufe):

| | Gesamtlauf | Picker (`pool`) |
|---|---|---|
| (a) unveraendert | 5058,7 ms | 335,1 ms |
| **(b) Text spaeter bauen, `situational` bleibt** | **3921,9 ms** | **245,5 ms** |
| (c) ganzer Block weg (reine Obergrenze, **kein gueltiger Zustand**) | 2910,8 ms | 168,4 ms |
| Gewinn (b) | **1136,8 ms = 22,5 %** | **89,6 ms = 26,7 %** |
| Gewinn (c) | 2147,9 ms = 42,5 % | 166,7 ms = 49,8 % |
| Anteil des reinen Textes am ganzen Block | 52,9 % | 53,7 % |

- **P1a — den Text erst bauen, wenn ihn jemand liest.** Gewinn **22,5 %**
  (Gesamtlauf) und **26,7 %** (Picker), beide weit ueber der Schwelle (5 %
  bzw. 16 %). **Risiko: niedrig** — `situational` entsteht unveraendert, die
  A7-Zeile der Vorsortierung ist nicht betroffen. **Aufwand: klein bis
  mittel** (die drei Felder werden erst bei Zugriff gefuellt).
- **P1b — den Block im **Beam** ganz ueberspringen.** Der Beam bewertet 3621
  von 4084 Builds und liest von `compute_qualitative` gar nichts. Der
  restliche Abstand zwischen (b) und (c) — 1011 ms im Gesamtlauf — liegt
  praktisch vollstaendig dort. **Fuer den Picker bringt P1b nichts**: dessen
  Weg ist reine Vorsortierung, ohne Beam.
  **Risiko: mittel**, **Aufwand: mittel** — `compute` braucht eine zweite
  Betriebsart, ohne dass eine zweite Rechenstelle entsteht (AD-015, AD-019).
  Der Waechter
  `test_one_build.py::test_the_user_interface_holds_exactly_one_call_to_compute`
  bleibt unberuehrt: es bleibt **ein** `compute`.
- **Wirkung auf A6.** Mit P1a faellt die Slot-Frage von 403 auf rund
  **310 ms** (`run.run`) bzw. von 335 auf **246 ms** (`pool`). Das ist knapp
  an der 250-ms-Schwelle aus AK-09, **nicht sicher darunter** — ein
  A6-Budget von **400 ms** waere danach haltbar, ein 250-ms-Budget nicht.
- **Trade-off.** P1a kostet Traegheit im Datenmodell (ein Feld, das erst bei
  Zugriff entsteht) — das ist die uebliche Falle „billig zu schreiben, teuer
  zu debuggen", und `Build` ist heute ein schlichter Wert. P1b kostet eine
  zweite Betriebsart an genau der Stelle, die AD-002/AD-019 bewusst einfach
  halten. Der `director` entscheidet, ob eine oder beide Stufen gebaut werden;
  **P1a allein traegt schon 22–27 %** und ist die risikoaermere.
- **Verifikation, die ich verlange:** die 440-Beraterlaeufe-Probe aus T-114
  wiederholen und den sha256 ueber Handles und Score aller Vorschlaege
  vergleichen — genau die Form, die `90ff81d` schon einmal benutzt hat.
  Zusaetzlich der differentielle Aufbau unter `scripts/differential/`. Und
  eigens: die A7-Zeile der Vorsortierung an einem Slot, dessen Kandidaten
  bedingte Effekte tragen — vorher und nachher dieselbe Zahl.

### P2 — `savefile.read_owned_relics` scannt 28 Slots Byte fuer Byte im Hauptthread

- **Ursache.** `for off in range(0, len(slot_data) - 24, 4):
  struct.unpack_from("<II", …)` (`nrdata/savefile.py:201-202`) — eine
  Python-Schleife ueber **jeden** 4-Byte-Versatz. cProfile zaehlt
  **10 293 488** `unpack_from`-Aufrufe fuer einen `inventory.load`.
  `load()` liest **zwei** Spielstanddateien mit je 14 Slots, um den
  bestbestueckten zu finden; gebraucht wird einer.
- **Vorher: 6147,6 ms** (Median, n=5) im **Hauptthread**, bei jedem
  Programmstart (`app.py:1575`) und bei jedem Klick auf `Rescan`
  (`app.py:1682`).
- **Obergrenze, gemessen:** ein Vorfilter ueber `bytes.find(b"\x80")` —
  `relic_id + RELIC_ID_FLAG` hat wegen `0x80000000` immer `0x80` als
  hoechstes Byte, und nur **0,22 %** der Bytes eines Slots sind `0x80` —
  bringt alle 14 Slots einer Datei von **2802,7 ms auf 61,9 ms = 45x**.
  Hochgerechnet faellt `inventory.load` von 6,15 s auf **rund 0,7 s**.
- **Bit-gleich, und breiter geprueft als gefunden:** identisches Ergebnis an
  **28 von 28** Slots **beider** Spielstaende (der Befund wurde an einem
  gefunden). Der Vergleich hat eine Positivkontrolle: um einen Eintrag
  gekuerzt, meldet er „ungleich".
- **Aufwand: klein.** Eine Schleife.
- **Risiko: niedrig, mit einer benannten Annahme.** Der Vorfilter setzt
  voraus, dass `relic_id + 0x80000000` in Little-Endian immer `0x80` als
  viertes Byte hat, also `relic_id < 0x01000000`. Die groesste Id im heutigen
  Datensatz ist **2 013 322**. Das ist eine Kopplung an die Daten und gehoert
  als `assert` in den Code, nicht in einen Kommentar. Die SEC-022-Dichtegrenze
  bleibt unveraendert.
- **Trade-off:** der Code wird eine Spur trickreicher. Bei 45x und einem
  `assert` daneben ist das vertretbar; der Kommentar muss Grund **und**
  Messwert tragen.
- **Zweiter, unabhaengiger Hebel, den ich nicht messe, weil er ein Entwurf
  ist:** 28 Slots lesen, um einen zu benutzen. Ob `load()` frueher aufhoeren
  darf, ist eine Frage an den `architect` — die Regel „der bestbestueckte
  gewinnt" ist bewusst so gebaut.

### P3 — Der Picker rechnet im Hauptthread und am Cache vorbei

Kein Tuning, sondern die Architekturfrage aus Abschnitt 2.4. **Sie steht hier
an dritter Stelle, weil P1 und P2 sie kleiner machen, aber nicht loesen:**
auch 200 ms gehoeren nicht in den Hauptthread. Entscheidung: `director` →
`architect`. Von ihr haengt ab, ob der LRU-Wert 64 seinen Nutzen bekommt
(3.2) und ob die Entprellung von 100 ms ueberhaupt etwas entprellt (3.1).

### P4 — LRU 32 → 64

Erst nach P3. Begruendung, Zahlen und Bedingung in Abschnitt 3.2.

### P5 — Der Picker-Dialog kostet rund 18,5 ms je Karte

Zehnmal die Rechnung. **Nicht meine Rolle**: das ist Widget-Bau und
wahrgenommene Leistung → `ui-ux-designer` und `developer`. Braucht eine
Messung **am Bildschirm**; meine Zahlen sind offscreen und damit
Untergrenzen (Abschnitt 2.5).

---

## 5. D-1: nachgemessen, und das Ergebnis ist ein Nein zu beiden Seiten

`docs/state.md` fuehrt D-1 als „`model.compute` (94 % der 941,6 ms)".
**Nachgemessen, nicht uebernommen:**

| | T-067 (06.09.2026) | T-118 (08.09.2026) |
|---|---|---|
| Skript | `scripts/measure_advisor_search.py` | dasselbe |
| Fall | `Wylder's Chalice` + Deep, nichts gehalten | derselbe |
| Poolgroessen | `[52, 54, 208, 23, 30, 21]` | **identisch** |
| Bewertungen | 3621 | **identisch** |
| Vorsortierung | 43,9 ms | 226,4 ms |
| Beam | 895,6 ms | 4755,4 ms |
| **ganzer Lauf** | **941,6 ms** | **4979,2 ms** |
| je Bewertung | 0,247 ms | 1,313 ms |
| Anteil `model.compute` | 94 % | **81,0 %** |

**Gleiches Skript, gleicher Fall, gleiche Poolgroessen, gleiche
Bewertungszahl — und 5,3x die Zeit.** Der Anteil von `model.compute` ist
dabei **gesunken** (94 % → 81 %), was heisst, dass der Rest noch staerker
gewachsen ist als `compute` selbst.

**Trotzdem sage ich nicht „Regression", und der Grund ist eine Messung:** der
Rechner lief waehrend meiner ganzen Reihe auf **1102 von 3201 MHz**
(`Legion Quiet Mode`), und meine Rechenlastprobe (1205 ms fuer 3 Mio.
Iterationen) hat **kein Gegenstueck** aus T-067 — dort ist keine Umgebung
protokolliert. Ein Drittel Takt erklaert grob den Faktor 3; der Rest waere
real. Das ist eine Rechnung, keine Messung, und deshalb bleibt die Frage
offen.

**Gegen die Vermutung, es liege am Code, spricht die Primaerquelle:**
`nrplanner/model.py` hat sich seit dem T-067-Bericht (`1e8697a`) um genau
einen Commit veraendert (`90ff81d`, QA-180, +30/-3 Zeilen), und
`nrplanner/effecttext.py` ueberhaupt nicht (419 Zeilen bei `1e8697a`,
`90ff81d` und `HEAD`). Ein Faktor 5,3 aus 27 Zeilen ist unwahrscheinlich.
Wahrscheinlicher sind Energieplan **oder** ein gewachsener Datensatz
(`extract_version` 11).

**Was daraus folgt — eine kleine, klar umrissene Aufgabe fuer den
`director`:** eine Wiederholung von `scripts/measure_advisor_search.py`
in **beiden** Energieplaenen, mit der Rechenlastprobe daneben. Zwei
Prozessstarts, unter fuenf Minuten. Danach ist entschieden, ob es eine
Regression gibt.

**Was unabhaengig vom Takt gilt und deshalb belastbar ist:** alle
**Verhaeltnisse** dieses Berichts — 81 % `model.compute`, 46,2 %
`compute_qualitative`, 45x fuer P2, die LRU-Trefferquoten. Sie sind
Quotienten aus derselben Reihe und kuerzen den Takt heraus.

---

## 6. Verworfene Optimierungen — mit Grund und mit Reaktivierungsbedingung

| Ansatz | Gemessen | Grund | Wieder interessant, wenn |
|---|---|---|---|
| **`bytes.find` je Relikt-Id** statt Vorfilter (P2-Variante) | 128 476,8 ms fuer 14 Slots gegen 2802,7 ms heute — **45x langsamer** | 849 gueltige Relikt-Ids x je ein voller 4-MB-Scan. Meine Hypothese, von der Messung widerlegt. | nie in dieser Form; die Zahl steht hier, damit niemand sie zweimal ausprobiert |
| **`array`-Vorlauf** statt `unpack_from` (P2-Variante) | 277,7 statt 589,7 ms am groessten Slot = **2,1x** | der Vorfilter aus P2 bringt 45x bei gleichem Aufwand | wenn sich die Annahme aus P2 (`relic_id < 0x01000000`) je als unhaltbar erweist — dann ist das der Rueckfallweg |
| **`model.compute_resistances` aus dem Suchpfad nehmen** | Gesamtlauf 191,0 ms = **3,6 %**, Picker 6,3 ms = **2,0 %** | beides unter der Signifikanzschwelle (5 % bzw. 16 %) — nicht messbar | **nach P1**: 191 ms von dann rund 2830 ms sind **6,8 %** und damit ueber der Schwelle. Dann lohnt es sich. *(Nebenbefund fuer den offenen Punkt „`compute_resistances` — Zurueckstellung wieder offen" in `docs/state.md`: die Leistungsseite spricht heute **nicht** fuer eine Aenderung.)* |
| **`model.compute_derived` aus dem Suchpfad nehmen** | nicht abschaltbar | `goals._min_damage_taken` liest `build.derived["HP"]` und bricht sonst ab | nie — der Block ist tragend |
| **Entprellung des Gesamtlaufs unter 250 ms** | 150 ms von 5274 ms = **2,8 %** | unter der 5-%-Schwelle des Szenarios | nach P1: 150 ms von dann rund 3080 ms sind 4,9 % — immer noch knapp darunter. Erst wenn der Gesamtlauf unter ~3 s faellt |
| **Slots 0, 1, 3, 4, 5 im Picker** | 32,3 bis 81,7 ms | unter der absoluten Untergrenze von 100 ms fuer eine Interaktionsantwort | wenn ein Spielstand mehr Relikte je Farbe traegt; die Kosten sind linear mit **1,53–1,81 ms je Kandidat**, die Grenze liegt also bei rund **60 Kandidaten** je Slot |
| **Ergebnis-Cache auf Platte** (AD-007 Option C) | nicht gemessen | AD-007 hat es entschieden; ich habe keinen Messwert, der die Entscheidung beruehrt | wenn der Prozessstart nach P2 den Berater dominiert — heute tut er es nicht |

---

## 7. Verifikationsstatus

**Was ich verifiziert habe.** Ich habe **keinen Code geaendert**, also gibt es
kein „Verhalten vorher/nachher" zu sichern. Verifiziert ist stattdessen die
**Gueltigkeit der Messung**:

| Was | Wie | Ergebnis |
|---|---|---|
| Die drei Umlenkungen greifen | dieselbe Pruefung umgelenkt **und** ungelenkt, plus echte Schreibprobe | 3 von 3, Gegenprobe zeigt jedes Mal den echten Pfad |
| Nichts geschrieben | sha256-Fingerabdruck vor/nach ueber vier Baeume + Registry-Export | 4 von 4 gleich, Registry byte-gleich |
| Das Messmittel kann anschlagen | Positivkontrolle: Datei hinzu, Byte geaendert | schlaegt in beiden Faellen an |
| Der Testabzug ist gleichwertig | Fingerabdruck des Neubaus gegen die Vorlage | identisch, 841 Dateien |
| Die Reihe ist in sich stabil | zwei Werte am Sitzungsende wiederholt | 1,0 % und 0,7 % Abweichung, Rauschband 12–16 % |
| Der Gegenentwurf zu P2 ist verhaltensgleich | 28 Slots **beider** Spielstaende, plus Positivkontrolle des Vergleichs | 28 von 28 gleich; der Vergleich meldet „ungleich", wenn ein Eintrag fehlt |
| Das Szenario ist das beauftragte | Reliktzahl und Loadouts aus dem echten Spielstand gezaehlt | **309 Relikte, 110 Loadouts** |

**Was ich nicht verifiziert habe.** Die Suite ist **nicht** gelaufen — ich
habe keine Codezeile angefasst, und ein Volllauf waere Selbstbestaetigung
statt Messung. Die Zahl aus T-102 (1256 passed, 9 skipped) gilt unveraendert.
Der letzte Suitelauf, der meinen Stand deckt, ist der von `76f1887`.

---

## 8. Befunde und Empfehlungen an andere Rollen

Alle ohne Nummer — Befund-IDs vergibt der `director`.

**An den `director`:**
1. *Zwei verwaiste `find /`-Prozesse belegen seit sieben Stunden CPU*
   (PID 1620, PID 5144). Abschnitt 1.2. Beenden.
2. *A6s erste Haelfte haelt auf dem Hauptweg nicht.* Abschnitt 2.4. Trifft
   das A9-Urteil von T-114 — dort geprueft am `Optimize`-Weg, nicht am
   Picker-Weg.
3. *D-1 ist nicht entscheidbar, solange die Umgebung von T-067 unbekannt
   ist.* Abschnitt 5. Vorschlag: eine Wiederholung in beiden Energieplaenen,
   unter fuenf Minuten.
4. *Die Zahl fuer E-1 liegt vor* (99,1–99,2 %, Abschnitt 1.4) und gehoert in
   `docs/plan-restarbeiten.md` — diese Datei liegt ausserhalb meines Auftrags.
5. *`ARCHITECTURE.md` AD-018 traegt eine widerlegte Zahl.* Die Tabelle bei
   Zeile ~1600 nennt „weisser Slot, normal (grösster Pool) — 205 — ~51 ms";
   gemessen 206 Kandidaten und **318,1 ms**. Auch „0,25 ms je Bewertung"
   (gemessen 1,095 ms) und „Gesamtlauf 0,46 s" (gemessen 5,02 s) stehen dort
   noch. → `architect`.
6. *Ein Messwerkzeug, das ein zweiter Lauf brauchen wird.* Meine Messbaeume
   im Scratchpad sind aufgeraeumt; die Harness dahinter existiert damit nicht
   mehr. Die vorhandenen Skripte `scripts/measure_advisor_search.py` und
   `…_picker.py` decken **nicht** ab, was S11 gebraucht hat: kalt/warm
   getrennt, `run.run` statt nur `pools`+`beam`, Streuung, die
   Rechenlastprobe. Ich schlage einen versionierten
   `scripts/measure_advisor_budget.py` vor, der genau die Tabellen aus
   `docs/perf/baselines.md` erzeugt — **Auftrag an den `developer`**, mein
   Auftrag beruehrt `scripts/` nicht.

**An den `architect`:** P3 (Abschnitt 4) und Befund 5. Zusaetzlich die Frage
aus 3.2, ob ein Cache mit Eintraegen von 33 KiB und 280 KiB dieselbe
Groessengrenze tragen soll.

**An den `developer`:** P1 und P2 als Folgeauftraege, mit den Vorher-Werten
aus `docs/perf/baselines.md` S11-A/B und S11-E. Beide haben eine gemessene
Obergrenze und eine benannte Verhaltensgarantie; keiner von beiden darf ohne
die in P1/P2 genannte Verifikation abgeschlossen werden.

**An den `qa-engineer`:** die Testabdeckung fuer P1 ist die kritische. Vor
der Umsetzung ist zu pruefen, ob ein Test heute rot wird, wenn
`compute_qualitative` fuer die **erklaerten** Builds ausfaellt — nicht nur
fuer alle. Faellt dabei kein Test aus, fehlt die Absicherung, und P1 darf
nicht beginnen.

**An den `ui-ux-designer`:** P5 (Abschnitt 2.5). Der Dialogbau ist zehnmal so
teuer wie die Rechnung. Die tatsaechliche Rechenzeit liegt im Budget; was
sich langsam anfuehlt, entsteht danach.
