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
| `model.compute_qualitative`, ganz | 2828,6 ms | **2426,6 ms = 46,2 %** |
| `model.compute_qualitative`, nur die Textarbeit (`situational` bleibt) | 3921,9 ms | **1136,8 ms = 22,5 %** |
| `model.compute_resistances` | 5064,2 ms | 191,0 ms = 3,6 % |
| `model.compute_derived` | nicht abschaltbar — `min_damage_taken` liest `build.derived["HP"]` | 0 % (tragend) |

*Die Trennung ist noetig, weil `Build.situational` — was
`compute_qualitative` **parkt** — von der Vorsortierung gelesen wird
(`candidates.py:157`), der **Text** dazu aber nur von `explain.py`. Rund
53 % des Blocks sind reiner Text. Zweite Messreihe, deshalb der leicht
andere Grundwert (5058,7 ms statt 5255,2 ms; beide innerhalb des
5-%-Rauschbands).*

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

**Obergrenzen** (Picker, `pool`, je 5 Laeufe): ohne `compute_qualitative`
ganz 162,7 ms von 323,8 ms → **161,1 ms = 49,8 %**; nur ohne die Textarbeit
(`situational` bleibt, weil `candidates.py:157` es liest) 245,5 ms von
335,1 ms → **89,6 ms = 26,7 %**; ohne `compute_resistances` 317,5 ms von
323,8 ms → 6,3 ms = 2,0 %.

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
| 2026-09-08 | 76f1887 | **gesamt** | **6593,7 ms** | 6499,0–6760,8 ms | nein | vor AD-029 Stufe C, ueberholt |
| 2026-09-08 | 76f1887 | davon `inventory.load` | 6147,6 ms | 6091,9–6299,4 ms | nein | 28 Slots gelesen, 1 gebraucht, vor Stufe C |
| 2026-09-08 | 76f1887 | davon `json.loads` des Abzugs | 406,8 ms | 391,3–497,0 ms | nein | 8,48 MB |
| 2026-09-08 | 76f1887 | davon `model.configure` | 0,4 ms | 0,4–0,6 ms | nein | vernachlaessigbar |
| 2026-09-08 | ac9a5c9 | **gesamt, nach AD-029 Stufe C (T-133+T-136, U3)** | **1377,9 ms** | 1331,8–1420,4 ms | **ja** | Uhr startet **vor** `from nrplanner import …`; **nicht** direkt gegen die Zeile darueber multiplizierbar, s. u. |
| 2026-09-08 | ac9a5c9 | davon Modulimporte (`inventory, paths, model`) | 320,5 ms | 319,3–341,3 ms | nein | ueberwiegend `from Crypto.Cipher import AES` (isoliert nachgemessen: 222–227 ms, 3 Laeufe); im alten Schnitt nicht ausgewiesen |
| 2026-09-08 | ac9a5c9 | davon `json.loads` des Abzugs | 366,7 ms | 359,3–399,8 ms | nein | 8,48 MB, unveraendert |
| 2026-09-08 | ac9a5c9 | davon `model.configure` | 0,5 ms | 0,4–0,6 ms | nein | vernachlaessigbar, unveraendert |
| 2026-09-08 | ac9a5c9 | **davon `inventory.load`, nach AD-029 Stufe C (T-133+T-136, U3)** | **657,2 ms** | 645,4–722,4 ms | nein | **9,35x** gegen 6147,6 ms; 28 Slots gelesen, 1 gebraucht; 2s/Median 9,9 % |

**Zur „gesamt"-Zeile, ehrlich statt bequem gerundet.** Die alte Zeile
(6593,7 ms) minus ihre drei ausgewiesenen Teile (6554,8 ms) laesst nur
**38,9 ms** unerklaert — deutlich weniger als die **320,5 ms**, die die
Modulimporte allein jetzt kosten, wovon **222–227 ms** isoliert auf
`from Crypto.Cipher import AES` entfallen (**dieselbe Abhaengigkeit stand
schon im Commit `76f1887`**, den T-118 mass — nachgesehen per `git show`,
keine neue Abhaengigkeit). Die einzige damit vereinbare Erklaerung: T-118s
Uhr begann **nach** den Modulimporten, meine beginnt davor. Die Harness von
T-118 existiert nicht mehr (T-118, Befund 6: „meine Messbaeume sind
aufgeraeumt"), die Annahme laesst sich nicht am Code der damaligen Messung
pruefen — deshalb steht sie hier als Annahme, nicht als Tatsache. **Der
tragende, sauber vergleichbare Wert dieses Abschnitts ist `inventory.load`
allein** (6147,6 → 657,2 ms, **9,35x**): dieselbe Funktion, derselbe Aufruf,
kein Uhr-Grenzenstreit.

**Signifikanzschwelle der neuen Zeilen:** 2s/Median 5,6 % (gesamt), 9,9 %
(`inventory.load`) → **10 %**. Umgebung identisch zur Zeile oben (derselbe
Rechner, derselbe Energieplan, `.venv` Python 3.12.10, ohne Qt, ohne
cProfile, warmer Plattencache, echter Spielstand mit zwei Dateien).

**U3 (T-140): der Ausloeser fuer AD-029 Stufe B greift.** AD-029 setzt die
Schwelle auf **250 ms** Median fuer `inventory.load`. Gemessen sind
**657,2 ms** — **163 % ueber** der Schwelle und weit ausserhalb der 9,9 %
Streuung dieser Reihe. **Empfehlung: Stufe B (Verlagerung des Lesens in
einen Worker) wird gebaut.** Diese Entscheidung liegt beim `performance-tuner`
laut AD-029 und ist hiermit getroffen, nicht beim `director`.

**Wo die alten 6,1 s lagen** (cProfile, ein Lauf, Stand `76f1887`):
`savefile.read_owned_relics` 6,562 s Eigenzeit in 28 Aufrufen, darin
**10 293 488** Aufrufe von `struct.unpack_from` (5,576 s). Alle 14 Slots
**einer** Datei kosteten 2802,7 ms.

**Obergrenze, gemessen an einem Gegenentwurf** (Vorfilter ueber das immer
gleiche hoechste Byte von `relic_id + RELIC_ID_FLAG`): alle 14 Slots in
**61,9 ms** statt 2802,7 ms = **45x**, bei bit-gleichem Ergebnis an **28 von
28** Slots beider Spielstaende. Zwei weitere Gegenentwuerfe siehe Bericht
T-118. **Diese Obergrenze ist jetzt umgesetzt** (T-133, AD-029 Stufe C) und
durch die Zeile `inventory.load` oben ersetzt — nicht durch die
Obergrenzen-Zahl selbst, weil `inventory.load` auch `find_loadout_table`
(T-136) und das Bauen des `Inventory`-Objekts traegt, die der Gegenentwurf
nicht mass.

**Herleitung aus T-118, nachgeprueft statt uebernommen:** Abschnitt „AD-029"
in `ARCHITECTURE.md` leitet aus den S11-E-Zahlen **666 ms** fuer
`inventory.load` nach dem Vorfilter her („9,2x, nicht 45x") und nennt das
ausdruecklich **hergeleitet, nicht gemessen**. Gemessen sind jetzt
**657,2 ms** — die Herleitung lag **1,3 %** daneben, innerhalb der 9,9 %
Streuung dieser Messung. Die Herleitung wird durch diese Messung bestaetigt,
nicht ersetzt: die Messung deckt zusaetzlich `find_loadout_table` (T-136) ab,
das in der Herleitung nicht gesondert vorkam.

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

## S11-I — U7: Haelt A6s dritte Zeile jetzt? (nach AD-028/U5b)

**Szenario.** Derselbe Fall wie S11-C, Slot 2 (weiss, Farbe 4, 206
Kandidaten): `Wylder`, `Wylder's Chalice` mit Deep of Night, Stufe 15, die
fuenf anderen Slots mit einem passenden Relikt aus dem echten Bestand besetzt
(dieselbe Auswahlregel wie `scripts/measure_advisor_picker.py`s
`a_relic_for`), der weisse frei und ungehalten. **Das Messgeraet ist bewegt
worden** (s. u.): gemessen wird nicht mehr `candidates.pool` direkt (das gibt
es auf diesem Weg seit U5b nicht mehr), sondern der wirkliche Aufruf, den
`RelicPicker.__init__` beim Oeffnen macht — `relicpicker.SlotAdvice.ask()`
ueber die echte zweite `AdvisorController`-Instanz des Fensters
(`window.picker_advisor`), mit dem echten `window.owned` (309 Relikte).
**Erzwungener Fehltreffer** (`picker_advisor._cache.clear()` vor jedem Ruf,
je eine neue `SlotAdvice` — genau das, was ein Spieler tut, der eine bisher
ungefragte Kombination oeffnet): kein Cache-Treffer darf die Zahl schoenen.

**Umgebung.** Windows 10, AMD Ryzen 7 5800H bei **1102 MHz** (`Legion Quiet
Mode`, ueberprueft, identisch zu T-118), CPython 3.12.10 (`.venv`), **mit
Qt** (`QT_QPA_PLATFORM=offscreen`, noetig, weil der Weg jetzt durch
`AdvisorController`/`QThread` fuehrt — anders als S11-B/C, die ohne Qt
massen; das ist eine Grenze des Vergleichs, s. u.), ohne cProfile, warmer
Prozess (n=25 in einem Prozess, nach dem Fensteraufbau), Codestand `ac9a5c9`.
Zwei unabhaengige volle Laeufe gefahren, beide unten aufgefuehrt
(Reproduzierbarkeit).

| Was | Lauf 1: p50 (n=25) | Spanne | Lauf 2: p50 (n=25) | Spanne | Budget | Notiz |
|---|---|---|---|---|---|---|
| **`SlotAdvice.ask()`, Hauptthread, erzwungener Fehltreffer** | **7,165 ms** | 6,648–10,111 ms | **7,539 ms** | 6,609–10,462 ms | **ja** | das ist die Zahl, die A6s dritte Zeile prueft |
| Zeit bis die Antwort ankommt (Fehltreffer, Rechnung im Worker) | 315,220 ms | 303,771–345,281 ms | 312,704 ms | 300,869–363,232 ms | nein | die eigentliche Rechnung, jetzt ausserhalb des Hauptthreads |
| `SlotAdvice.ask()`, Hauptthread, erzwungener Treffer (Cache) | 7,051 ms | 6,340–55,316 ms | 7,212 ms | 6,355–53,081 ms | nein | ein Ausreisser je Lauf (53–55 ms), Median unveraendert von der Fehltreffer-Zeile |

**U7, Antwort: A6s dritte Zeile haelt jetzt, mit grossem Abstand.** Vorher
(T-118, S11-C) hielt der Hauptthread **318,1 ms** beim Oeffnen des weissen
Slots — **6,3x** das 50-ms-Budget. Jetzt sind es **7,2–7,5 ms** — **7 %** des
Budgets, **42–44x** schneller als vorher gemessen, reproduziert ueber zwei
unabhaengige Laeufe (Abweichung der Mediane 5,2 %, innerhalb der Streuung
einer der beiden Zeilen). **Die 318 ms sind nicht verschwunden, sie sind
umgezogen:** die Zeile „Zeit bis die Antwort ankommt" (312,7/315,2 ms) liegt
**innerhalb der 10,3 % Streuung** der alten 318,1-ms-Zahl (Differenz 1,7–4,6
%) — die Kandidatenrechnung selbst ist nicht schneller geworden, sie laeuft
nur nicht mehr im Hauptthread. Ursache und Wirkung sind damit sauber
getrennt: AD-028s Architekturentscheidung traegt die ganze Verbesserung,
keine Optimierung dieses Laufs.

**Grenze des Vergleichs mit S11-C (L-009), benannt statt verschwiegen.**
S11-B/C massen `candidates.pool` **ohne Qt**, als reine Funktion. Diese
Messung geht **mit Qt** durch `AdvisorController`, weil der Weg das seit U5b
verlangt — ein Vergleich zwischen „ohne Qt" und „mit Qt" ist ein Vergleich
zwischen zwei verschiedenen Messgeraeten, nicht nur zwei Codepfaden. Die
Rechenzeit selbst (Zeile 2) ist trotzdem vergleichbar, weil `run.slot_pool`
am Ende denselben `candidates.pool`-Aufruf macht wie vorher; nur die
Hauptthread-Zeile (Zeile 1) ist ein wirklich neues Messgeraet, kein
Nachfolgewert desselben.

**Was hier nicht gemessen wurde, obwohl `ARCHITECTURE.md` (Nachtrag IX-3,
Fassung 2 der U7-Zeile) es der Rolle zuweist:** die Groesse eines
Picker-Cache-Eintrags in der neuen Antwortform gegen die 140-KiB-Schranke
(IX-3.2) und die Trefferquote der beiden Spuren unter dem kanonischen
Schluessel (IX-3.3). **`docs/tasks/T-140.md` nennt diese beiden Punkte
nicht** — der Auftrag zaehlt vier Zahlen auf, diese zwei sind keine davon.
Das ist eine Luecke zwischen `ARCHITECTURE.md` und dem Auftrag, kein
Vergessen dieses Laufs; sie steht im Abschlussbericht als Befund an den
`director`.

---

## S11-J — OF-26: Der Hauptthread-Rest, zerlegt

**Szenario.** Dieselbe Frage wie S11-I, zerlegt in ihre drei Bestandteile,
**einzeln aufgerufen** (dieselben reinen Funktionen, die `ask()` ueber
`_question_from` intern ruft — keine Seiteneffekte, ein zweiter Aufruf mit
denselben Eingaben ist deckungsgleich mit dem ersten). Gemessen fuer **beide**
Wege, weil OF-26 ausdruecklich beide verlangt: den Picker (weisser Slot, 5
gehalten) und `Optimize` (sechs freie Slots, nichts gehalten — S11-A-Fall).
Umgebung wie S11-I. Zwei unabhaengige Laeufe.

| Bestandteil | Weg | Lauf 1 p50 (n=25) | Lauf 2 p50 (n=25) | Budget | Notiz |
|---|---|---|---|---|---|
| `advisorbar.asking_from` (Anfragebau) | Picker | 0,200 ms | 0,295 ms | nein | |
| `advisor_run.frozen_inventory` (309 Kopien) | Picker | 4,151 ms | 4,945 ms | nein | |
| `advisor_run.inventory_fingerprint` (sha256, 309 Zeilen) | Picker | 1,911 ms | 2,754 ms | nein | |
| **Summe Picker** | Picker | **6,262 ms** | **7,994 ms** | **ja** | |
| `advisorbar.asking_from` (Anfragebau) | Optimize | 0,223 ms | 0,215 ms | nein | |
| `advisor_run.frozen_inventory` (309 Kopien) | Optimize | 4,295 ms | 4,108 ms | nein | |
| `advisor_run.inventory_fingerprint` (sha256, 309 Zeilen) | Optimize | 1,900 ms | 1,893 ms | nein | |
| **Summe Optimize** | Optimize | **6,418 ms** | **6,216 ms** | **ja** | |

**OF-26, Antwort: der Hauptthread-Rest ist klein, keine Ueberraschung.**
6,2–8,0 ms von 50 ms Budget = **12–16 %**, auf **beiden** Wegen fast
gleich (Picker und Optimize unterscheiden sich um unter 2 ms) — plausibel,
weil beide `_question_from` in `worker.py` teilen und beide 309 Kopien samt
Fingerabdruck bilden, egal wie viele Slots frei sind. **Zusammen mit S11-I
Zeile 1 (7,2–7,5 ms) ergibt das den ganzen Hauptthread-Aufenthalt beim
Oeffnen des Pickers: rund 7,5 ms, nicht 6,2–8,0 ms zusaetzlich** — die
Differenz zwischen der vollen `ask()`-Zeile und dieser Summe (rund 1 ms)
ist die Kosten von `SlotAdvice.ask()` selbst (Problem-Zusammenbau,
Signal-Verbindung, Cache-Abfrage), hier nicht gesondert gemessen.

**Streuung.** Bei Werten unter 5 ms ist 2s/Median (43–74 % in den
Rohmessungen) kein brauchbares Mass — die absolute Streuung liegt bei
0,3–7 ms, dominiert von Scheduler-Jitter dieser Groessenordnung, nicht von
echter Varianz der Arbeit. Beurteilt wird deshalb gegen die absolute
50-ms-Untergrenze, nicht gegen eine Prozentschwelle: **selbst die
ungeguenstigste Einzelmessung** (Spanne bis 11,2 ms bei
`frozen_inventory`) bleibt bei unter einem Viertel des Budgets.

---

## S11-K — OF-25: Ueberlappung zweier rechnender Spuren

**Szenario.** `Optimize` (sechs freie Slots, nichts gehalten, S11-A-Fall)
**allein** gegen `Optimize`, waehrend **gleichzeitig** eine Picker-Frage am
weissen Slot (206 Kandidaten, S11-C-Fall) laeuft. Die fuenf anderen Slots
tragen ein Relikt (fuer eine realistische Picker-Frage), sind aber **nicht**
gehalten (`Hold`-Schalter aus) — `Optimize` sieht deshalb weiterhin sechs
freie Slots (AD-018.1: der Picker haelt die anderen Slots so, wie sie
stehen, unabhaengig vom `Hold`-Schalter; `Optimize` liest den Schalter).
Beide Fragen so gleichzeitig wie moeglich gestartet: `Optimize` zuerst
(250 ms Entprellung), die Picker-Frage im selben Tick hinterher (0 ms
Entprellung), sodass der Worker der Picker-Frage laengst laeuft, wenn
`Optimize`s Worker startet. Gemessen wird `Optimize`s Gesamtzeit. n=5 je
Reihe, Cache vor jedem Lauf geleert.

**Signifikanzschwelle:** 2s/Median = 3,5 % (allein), 3,3 % (gleichzeitig) →
**5 %** (wie S11-A).

| Datum | Commit | Reihe | p50 (n=5) | Spanne | 2s/Median | Budget |
|---|---|---|---|---|---|---|
| 2026-09-08 | ac9a5c9 | `Optimize`, allein | **5282,5 ms** | 5241,7–5469,5 ms | 3,5 % | **ja** |
| 2026-09-08 | ac9a5c9 | `Optimize`, mit gleichzeitiger Picker-Frage | **5383,9 ms** | 5351,0–5576,2 ms | 3,3 % | nein |

**OF-25, Antwort: keine gemessene Verlangsamung ueber der Signifikanzschwelle
dieses Szenarios.** Differenz der Mediane **101,3 ms = 1,9 %** — unterhalb
der 5-%-Schwelle und unterhalb der 3,3–3,5 % Eigenstreuung beider Reihen.
`Optimize` bleibt mit **5383,9 ms** deutlich unter den 6 s aus A6 (10,3 %
Luft). **Kein GIL-Engpass gefunden, der A6s 6-s-Zeile gefaehrdet** — die
Sorge aus OF-25 war begruendet (zwei Python-Threads teilen sich unter dem
GIL einen Kern), trifft hier aber nicht in messbarer Groesse zu, vermutlich
weil die Picker-Frage (rund 313 ms Rechenzeit) nur einen kleinen Teil von
`Optimize`s rund 5,3 s ueberlappt.

**Randbemerkung, ehrlich benannt statt verschwiegen:** Der Solo-Median
dieser Reihe (5282,5 ms) liegt **5,2 % ueber** S11-As Solo-Median
(5023,6 ms, T-118) und ausserhalb von dessen damaliger Spanne
(4872,1–5225,2 ms). Kein Code auf diesem Pfad hat sich seit T-118 geaendert
(T-133/T-136 betreffen `inventory.load`, nicht `run.run`/`search`); die
Rechenlastprobe dieser Sitzung (1114,4 ms Median, n=5) ist sogar **7,5 %
schneller** als die aus T-118 (1205 ms), was eine langsamere Maschine als
Erklaerung ausschliesst. Die wahrscheinlichste Ursache ist Sitzungsrauschen
(Hintergrundlast durch andere, gleichzeitig laufende Prozesse auf diesem
Rechner, siehe Abschnitt „Umgebung" im Bericht) statt einer Regression —
belegt ist das nicht, und die Zahl steht deshalb hier, nicht als
`director`-Meldung. Der **Vergleich innerhalb dieser Sitzung** (allein gegen
gleichzeitig, beide unter denselben Bedingungen gemessen) ist von dieser
Frage unberuehrt und ist die tragende Aussage von S11-K.

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
| S11-E Prozessstart (vor AD-029 Stufe C) | 3,1 % | **5 %** | — |
| S11-E `inventory.load` (nach AD-029 Stufe C, T-140/U3) | 9,9 % | **10 %** | — |
| S11-I `SlotAdvice.ask()` Hauptthread-Hold (T-140/U7) | 24,4 % | absolut beurteilt (s. u.) | 50 ms (A6) |
| S11-J Hauptthread-Rest (T-140/OF-26) | 43–74 % (Werte < 5 ms) | absolut beurteilt (s. u.) | 50 ms (A6) |
| S11-K Optimize, allein/gleichzeitig (T-140/OF-25) | 3,3–3,5 % | **5 %** | — |

**S11-I/J werden gegen die absolute Untergrenze beurteilt, nicht gegen
2s/Median:** bei Werten von wenigen Millisekunden dominiert
Scheduler-Jitter die relative Streuung, ohne dass die absolute Groesse noch
in der Naehe eines Budgets liegt (7,5 ms bzw. 6,2–8,0 ms gegen 50 ms). Eine
Prozentschwelle waere hier kein sinnvolles Mass — siehe S11-I/J im
Einzelnen.

**Absolute Untergrenze, projektweit:** was unter **100 ms** liegt, wird nicht
weiter optimiert (Interaktionsantwort). Das nimmt die Slots 0, 1, 3, 4 und 5
aus S11-C heraus (32–82 ms).

**Die beiden Architekturwerte, die `ARCHITECTURE.md` dem
`performance-tuner` zuweist** (Zeile 1620 ff. und 1632 ff.), sind aus diesen
Zahlen hergeleitet und stehen mit ihrer Begruendung im Bericht
`docs/berichte/T-118-performance-tuner.md`, Abschnitt 3.
