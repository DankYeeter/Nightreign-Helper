# Leistungs-Grundwerte (Baselines)

Angelegt am 08.09.2026 vom `performance-tuner` (T-118, S11). **Erstlauf im
Projekt: hier steht die unveraenderte Ausgangslage, bevor irgendetwas
angefasst wurde.** Es ist nichts optimiert worden.

**Alte Zeilen bleiben stehen.** Die Historie ist der Zweck dieser Datei. Je
Szenario ist **genau eine** Zeile als `Budget` markiert; das ist der geltende
Sollwert. Weicht eine spaetere Messung um mehr als die unten je Szenario
genannte Signifikanzschwelle davon ab, ist das eine **Regression** und wird
gemeldet, bevor neu optimiert wird.

**Aendert sich das Szenario, entsteht ein neuer Abschnitt.** Alte und neue
Werte werden nie in derselben Tabelle vermischt.

---

## Umgebung aller Messungen dieses Erstlaufs

Ohne diese Angaben ist jede Zahl unten wertlos (L-009). Wer die Reihe
wiederholt, wiederholt **zuerst die Rechenlastprobe** und normiert daran.

| | |
|---|---|
| Rechner | AMD Ryzen 7 5800H, 8 Kerne / 16 Threads |
| **Takt** | **1102 MHz gemessen gegen 3201 MHz Nennwert** — fuenf Stichproben, alle 1102 |
| **Energieplan** | **`Legion Quiet Mode`** (`powercfg /getactivescheme`, GUID `16edbccd-…`) |
| Betriebssystem | Windows 10 10.0.19045 |
| Python | 3.12.10 CPython, `.venv` des Projekts |
| **Rechenlastprobe** | **1205 ms** Median fuer 3 Mio. `x += i*i` (Spanne 1157–1232, n=5) |
| Fremdlast waehrend der Messung | zwei `find /`-Prozesse aus fremden Laeufen (PID 1620 seit 03:16, PID 5144 seit 03:35), zusammen rund 0,4 Kerne von 16 |
| Codestand | `76f1887` (kein Code geaendert; der einzige Commit dieses Laufs betrifft `docs/`) |
| Datenabzug | `nightreign_data.json`, `data_version` 10350000, `extract_version` 11, 8 484 651 B |
| Datenmenge | **309 Relikte, 110 gespeicherte Builds (Loadouts im Spielstand)** |

**Der Energieplan ist die Wahl des Nutzers und damit die richtige Messumgebung**
(gemessen wird gegen die Grenzen des Zielsystems, nicht gegen eine
Wunschmaschine). Die Zahlen unten sind deshalb der **konservative** Fall. Wer
in einem anderen Energieplan misst, misst ein anderes Szenario und legt einen
neuen Abschnitt an — die Rechenlastprobe zeigt es sofort.

**Isolierung (Pflicht, QA-195).** Gemessen wurde mit drei Umlenkungen, jede
gegen ihren ungelenkten Fall geprueft: `LOCALAPPDATA` (`paths.py:20`),
`APPDATA` (`shortcut.py:44-49`), `NIGHTREIGN_SETTINGS_ORG`
(`favourites.py:25`). Vor und nach der Reihe sind die vier schutzwuerdigen
Baeume inhaltsgleich (sha256 ueber Pfad+Inhalt jeder Datei) und der
Registry-Zweig `HKCU\Software\DankYeeter` byte-gleich. Einzelheiten im
Bericht `docs/berichte/T-118-performance-tuner.md`.

---

## S11-A — Gesamtlauf `Optimize`, unguenstigster echter Fall

**Szenario.** `Wylder`, `Wylder's Chalice` mit Deep of Night (Slots `[0,2,4]`
+ deep `[0,1,3]`), Stufe 15, **nichts festgehalten**, sechs freie Slots,
Zielrichtung `max_damage`, K=20 / W=40, Referenzwaffe = Startwaffe. 309
Relikte. Gemessen wird `advisor.run.run` von der Einfrierung bis zum fertigen
`AdvisorResult` — also der ganze Weg des Arbeiters, nicht nur Vorsortierung
und Beam. **Warm** = Laeufe 2–6 in einem Prozess (n=25 ueber 5 Prozesse),
**kalt** = der jeweils erste Lauf eines frischen Prozesses (n=5).

**Streuung und Signifikanzschwelle:** 2s/Median = **3,3 %** (warm, n=25).
Schwelle fuer dieses Szenario: **5 %**. Absolute Untergrenze: nicht
zutreffend, der Fall liegt weit darueber.

| Datum | Commit | Umgebung | kalt (n=5) | warm p50 (n=25) | Spanne warm | Bewertungen | Budget | Notiz |
|---|---|---|---|---|---|---|---|---|
| 2026-09-08 | 76f1887 | s. o., 1102 MHz, Quiet Mode | 4901,6 ms | **5023,6 ms** | 4872,1–5225,2 ms | 3621 | **ja** | Erstlauf, nichts optimiert. Poolgroessen `[52,54,208,23,30,21]` |

**Zerlegung** (Stoppuhr um `model.compute`, ein Lauf, ohne Profiler-Aufschlag):
`model.compute` **4123,8 ms in 4084 Aufrufen = 1,010 ms je Aufruf = 81,0 %**
eines 5088,5-ms-Laufs; Rest 964,7 ms. Getrennt nach den beiden Schritten des
alten Messskripts (`scripts/measure_advisor_search.py`): Vorsortierung
226,4 ms, Beam 4755,4 ms.

**Obergrenzen einzelner Kostenbloecke** (je 5 Laeufe, Grundwert 5255,2 ms):

| Block abgeschaltet | Median | Obergrenze des Gewinns |
|---|---|---|
| `model.compute_qualitative` | 2828,6 ms | **2426,6 ms = 46,2 %** |
| `model.compute_resistances` | 5064,2 ms | 191,0 ms = 3,6 % |
| `model.compute_derived` | nicht abschaltbar — `min_damage_taken` liest `build.derived["HP"]` | 0 % (tragend) |

**Abbruchverhalten** (5 Laeufe je Zeile): Abbruchwunsch sofort → Lauf endet
nach 2,3 ms; nach 50 ms → 50,4 ms (0,4 ms Nachlauf); nach 250 ms → 449,7 ms
(**199,7 ms Nachlauf**, weil der Lauf dann in der Beam-Ebene steht, wo nur
zwischen den Ebenen geprueft wird).

---

## S11-B — Picker: eine Slot-Frage, weisser Slot (AD-018-Hauptweg)

**Szenario.** Wie S11-A, aber **ein** Slot offen und alle fuenf anderen
gehalten — die Frage, die AD-018 zum Hauptweg erklaert hat. Gemessen wird der
weisse Slot (Index 2, Farbe 4), der groesste Pool. Zwei Wege, weil das
Programm heute beide hat: `candidates.pool` ist der Aufruf, den
`relicpicker.SlotAdvice.ranking` **im Hauptthread** macht; `run.run` ist der
Weg ueber den `AdvisorController`, den AD-018 beschreibt.

**Streuung und Signifikanzschwelle:** `pool` 2s/Median = 15,5 %, `run.run`
10,4 %. Schwelle fuer dieses Szenario: **16 %** fuer `pool`, **12 %** fuer
`run.run`. Absolute Untergrenze: **100 ms** (Interaktionsantwort).

| Datum | Commit | Weg | kalt (n=5) | warm p50 (n=25) | Spanne warm | Kandidaten | Budget | Notiz |
|---|---|---|---|---|---|---|---|---|
| 2026-09-08 | 76f1887 | `candidates.pool` (heutiger Picker, Hauptthread) | 310,7 ms | **321,2 ms** | 283,8–382,2 ms | 206 | **ja** | AD-018 rechnete mit ~51 ms — **6,3x daneben** |
| 2026-09-08 | 76f1887 | `run.run` (Weg ueber den Controller) | 378,9 ms | **403,3 ms** | 355,3–445,8 ms | 206 | **ja** | trägt zusaetzlich Erklaerung und 20 Vorschlaege |

**Obergrenze** (Picker, `pool`, Grundwert 323,8 ms, je 5 Laeufe): ohne
`compute_qualitative` 162,7 ms → **161,1 ms = 49,8 %**; ohne
`compute_resistances` 317,5 ms → 6,3 ms = 2,0 %.

**Abbruchverhalten:** sofort → 4,5 ms; nach 50 ms → 50,8 ms; nach 250 ms →
251,4 ms (1,4 ms Nachlauf). Ein verworfener Picker-Lauf ist also billig.

---

## S11-C — Picker: alle sechs Slots einzeln (`candidates.pool`)

**Szenario.** Wie S11-B, aber jeder der sechs Slots einmal geoeffnet — was ein
Spieler tut, der einen Kelch durchsieht. Summe und Einzelwerte.

**Signifikanzschwelle:** Summe 2s/Median = 7,0 % → **8 %**. Fuer die einzelnen
Slots liegt 2s bei 10–36 %; die fuenf Slots unter 100 ms fallen ohnehin unter
die absolute Untergrenze und werden nicht optimiert.

| Datum | Commit | Slot | Farbe | Deep | Kandidaten | warm p50 (n=25) | Spanne | 2s | Budget |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-08 | 76f1887 | **Summe aller sechs** | — | — | 385 | **610,7 ms** | 577,7–655,2 ms | 7,0 % | **ja** |
| 2026-09-08 | 76f1887 | 0 | 0 | nein | 52 | 81,0 ms | 71,0–102,0 ms | 25,0 % | nein |
| 2026-09-08 | 76f1887 | 1 | 2 | nein | 53 | 81,7 ms | 69,7–100,6 ms | 20,8 % | nein |
| 2026-09-08 | 76f1887 | 2 | 4 (weiss) | nein | 206 | 318,1 ms | 289,6–358,9 ms | 10,3 % | nein |
| 2026-09-08 | 76f1887 | 3 | 0 | ja | 23 | 37,7 ms | 30,9–51,5 ms | 24,7 % | nein |
| 2026-09-08 | 76f1887 | 4 | 1 | ja | 30 | 54,3 ms | 45,1–68,0 ms | 21,1 % | nein |
| 2026-09-08 | 76f1887 | 5 | 3 | ja | 21 | 32,3 ms | 29,2–50,8 ms | 35,7 % | nein |

Die Kosten sind linear in den Kandidaten: **1,54 ms je Kandidat**
(318,1 / 206) am weissen Slot, 1,53–1,81 ms an den uebrigen.

---

## S11-D — Eine einzelne Bewertung (`model.compute` ueber `evaluate`)

**Szenario.** Ein voller Sechs-Relikt-Build, 18 Effekt-Ids, `evaluate` mit
leerer Zuweisung, n=300. Dieselbe Groesse, die T-067 am 06.09.2026 mit
**0,247 ms** genannt hat.

**Signifikanzschwelle:** die Spanne ist hier breit (0,879–2,252 ms), 2s ist
kein brauchbares Mass fuer eine einzelne Bewertung. Verglichen wird der
Median; Schwelle **10 %**.

| Datum | Commit | Fall | p50 (n=300) | Spanne | Budget | Notiz |
|---|---|---|---|---|---|---|
| 2026-09-08 | 76f1887 | unveraendert | **1,095 ms** | 0,879–2,252 ms | **ja** | |
| 2026-09-08 | 76f1887 | ohne `compute_qualitative` | 0,499 ms | 0,385–1,167 ms | nein | Obergrenzen-Messung, kein gueltiger Zustand |
| 2026-09-06 | (T-067) | unveraendert, anderer Rechnerzustand | 0,247 ms | nicht genannt | nein | **nicht vergleichbar** — s. Bericht T-118, Abschnitt „D-1" |

---

## S11-E — Prozessstart: Datenabzug und Spielstand lesen

**Szenario.** Vom Prozessstart bis zum benutzbaren Zustand, ohne Fenster:
`nightreign_data.json` einlesen, `model.configure`, `inventory.load`. 309
Relikte, 110 Loadouts, **zwei** Spielstanddateien mit je 14 Slots. n=5, je
ein frischer Prozess. Dies ist der Weg, den `Planner.__init__` (Zeile 1575)
und der `Rescan`-Knopf (Zeile 1682) **im Hauptthread** gehen.

**Signifikanzschwelle:** 2s/Median = 3,1 % (gesamt), 2,6 % (Spielstand) →
**5 %**. Der Abzug allein streut mit 22,6 % und bekommt **25 %**.

| Datum | Commit | Schritt | p50 (n=5) | Spanne | Budget | Notiz |
|---|---|---|---|---|---|---|
| 2026-09-08 | 76f1887 | **gesamt** | **6593,7 ms** | 6499,0–6760,8 ms | **ja** | |
| 2026-09-08 | 76f1887 | davon `inventory.load` | 6147,6 ms | 6091,9–6299,4 ms | nein | 28 Slots gelesen, 1 gebraucht |
| 2026-09-08 | 76f1887 | davon `json.loads` des Abzugs | 406,8 ms | 391,3–497,0 ms | nein | 8,48 MB |
| 2026-09-08 | 76f1887 | davon `model.configure` | 0,4 ms | 0,4–0,6 ms | nein | vernachlaessigbar |

**Wo die 6,1 s liegen** (cProfile, ein Lauf): `savefile.read_owned_relics`
6,562 s Eigenzeit in 28 Aufrufen, darin **10 293 488** Aufrufe von
`struct.unpack_from` (5,576 s). Alle 14 Slots **einer** Datei kosten
2802,7 ms.

**Obergrenze, gemessen an einem Gegenentwurf** (Vorfilter ueber das immer
gleiche hoechste Byte von `relic_id + RELIC_ID_FLAG`): alle 14 Slots in
**61,9 ms** statt 2802,7 ms = **45x**, bei bit-gleichem Ergebnis an **28 von
28** Slots beider Spielstaende. Zwei weitere Gegenentwuerfe siehe Bericht.

---

## S11-F — Speicher

**Szenario.** Arbeitssatz (`WorkingSet64`, physisch) desselben kopflosen
Prozesses an vier Punkten. Ein Fenster kommt darauf noch obendrauf und ist
hier nicht gemessen.

| Datum | Commit | Punkt | Arbeitssatz | Zuwachs | Budget |
|---|---|---|---|---|---|
| 2026-09-08 | 76f1887 | nackter Interpreter | 11,4 MiB | — | nein |
| 2026-09-08 | 76f1887 | nach den Modul-Importen | 20,5 MiB | +9,1 MiB | nein |
| 2026-09-08 | 76f1887 | **nach Abzug + Spielstand** | **47,7 MiB** | +27,1 MiB | **ja** |
| 2026-09-08 | 76f1887 | + LRU mit 32 Picker-Antworten | 49,3 MiB | +1,7 MiB | nein |

**Groesse eines Cache-Eintrags** (tiefe Zaehlung ueber `sys.getsizeof`,
jedes Objekt einmal): Picker-Antwort mit 20 Vorschlaegen **33,4 KiB** Median
(Spanne 28,4–38,5, Schluessel 2,9–3,1 KB davon); Gesamtlauf-Antwort mit 40
Vorschlaegen **279,9 KiB**.

---

## S11-G — Fester Testabzug gegen Neubau (E-1)

**Szenario.** Was der feste Testabzug unter
`%LOCALAPPDATA%\NightreignHelper-Testabzug` je Lauf spart. Neubau =
`extract.write_snapshot` + `iconbuild.build` in ein leeres Verzeichnis, also
genau das, was `firstrun._Builder.run` tut. Kopie = `Copy-Item -Recurse` wie
in `docs/plan-restarbeiten.md` E-1 beschrieben.

| Datum | Commit | Weg | Median | Spanne | n | Ergebnis | Budget |
|---|---|---|---|---|---|---|---|
| 2026-09-08 | 76f1887 | **Neubau** | — | **293,81–310,07 s** | 2 | 841 Dateien, 19,8 MiB | nein |
| 2026-09-08 | 76f1887 | davon Abzug | — | 169,38–184,49 s | 2 | | nein |
| 2026-09-08 | 76f1887 | davon Symbole | — | 124,43–125,58 s | 2 | | nein |
| 2026-09-08 | 76f1887 | **Kopie des Testabzugs** | **2,54 s** | 2,42–2,75 s | 5 | 841 Dateien, 19,8 MiB | **ja** |

**Ersparnis: 291,3 bis 307,5 s je Lauf = 99,1–99,2 %.** Die Vorlage ist
**nachweislich** gleichwertig: der frisch gebaute Baum hat denselben
Inhalts-Fingerabdruck wie der Testabzug (`35872fe8717ebb0e` ueber Pfad,
Groesse und sha256 jeder der 841 Dateien).

---

## S11-H — Picker-Dialog: Rechnung gegen Fensterbau

**Szenario und seine Grenze (L-009).** Qt-Plattform **`offscreen`**, Stil
`fusion`, logische Pixel — **nicht der Bildschirm des Nutzers**. Offscreen
faellt das Zeichnen weg; die Zahlen sind eine **Untergrenze**, keine Messung
der Nutzererfahrung. Sie stehen hier, weil ohne sie die Haelfte der Wartezeit
unsichtbar bliebe. Kelch des Fensters beim Start, nicht `Wylder's Chalice` —
**kein weisser Slot dabei**, deshalb keine 206 Karten.

| Datum | Commit | Slot | Kand. | Karten | Rechnung p50 (n=5) | Dialogbau p50 (n=5) | Summe | Budget |
|---|---|---|---|---|---|---|---|---|
| 2026-09-08 | 76f1887 | 0 | 51 | 50 | 94,5 ms | 944,9 ms | 1039,5 ms | nein |
| 2026-09-08 | 76f1887 | 1 | 51 | 51 | 100,7 ms | 921,2 ms | 1021,9 ms | nein |
| 2026-09-08 | 76f1887 | 2 | 53 | 51 | 107,7 ms | 973,8 ms | **1081,5 ms** | **ja** |
| 2026-09-08 | 76f1887 | 3 | 22 | 22 | 40,1 ms | 422,4 ms | 462,5 ms | nein |
| 2026-09-08 | 76f1887 | 4 | 22 | 22 | 49,1 ms | 455,5 ms | 504,7 ms | nein |
| 2026-09-08 | 76f1887 | 5 | 30 | 30 | 60,1 ms | 619,7 ms | 679,8 ms | nein |

**Der Dialogbau kostet rund 18,5 ms je Karte** und damit **rund das Zehnfache
der Rechnung**. Fuer den weissen Slot mit 206 Karten waeren das
hochgerechnet ~3,8 s Dialogbau neben 318 ms Rechnung — **hochgerechnet, nicht
gemessen**, und offscreen.

---

## Ableitungen aus diesen Werten

**Signifikanzschwellen dieses Projekts** (aus der Streuung der Grundwerte,
Richtwert 2s):

| Szenario | 2s/Median | Schwelle | absolute Untergrenze |
|---|---|---|---|
| S11-A Gesamtlauf | 3,3 % | **5 %** | — |
| S11-B Picker `pool` | 15,5 % | **16 %** | 100 ms |
| S11-B Picker `run.run` | 10,4 % | **12 %** | 100 ms |
| S11-C Summe sechs Slots | 7,0 % | **8 %** | 100 ms |
| S11-D eine Bewertung | — | **10 %** | — |
| S11-E Prozessstart | 3,1 % | **5 %** | — |

**Absolute Untergrenze, projektweit:** was unter **100 ms** liegt, wird nicht
weiter optimiert (Interaktionsantwort). Das nimmt die Slots 0, 1, 3, 4 und 5
aus S11-C heraus (32–82 ms).

**Die beiden Architekturwerte, die `ARCHITECTURE.md` dem
`performance-tuner` zuweist** (Zeile 1620 ff. und 1632 ff.), sind aus diesen
Zahlen hergeleitet und stehen mit ihrer Begruendung im Bericht
`docs/berichte/T-118-performance-tuner.md`, Abschnitt 3.
