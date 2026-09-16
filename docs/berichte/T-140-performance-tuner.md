# T-140 — U3 und U7: nachmessen, was gebaut wurde (performance-tuner)

```
STATUS: erledigt
AUFTRAG: T-140 - U3 und U7: nachmessen, was gebaut wurde (performance-tuner)
GELESEN: docs/tasks/T-140.md; docs/perf/baselines.md (S11-A bis S11-H, ganz);
  docs/berichte/T-118-performance-tuner.md (ganz); docs/berichte/
  T-139-developer.md; ARCHITECTURE.md Nachtrag VIII (AD-028, AD-029, Zeilen
  3962-4465) und Nachtrag IX (Fassung 2 von U5a-U7, IX-1 bis IX-4, OF-25,
  OF-26, OF-28, Zeilen 4467-4970); Quellstand: nrplanner/relicpicker.py
  (SlotAdvice, RelicPicker, advice_for), nrplanner/advisor/worker.py
  (AdvisorController, PICKER_DEBOUNCE_MS, PICKER_CACHE_SIZE), nrplanner/
  advisor/run.py (frozen_inventory, inventory_fingerprint, slot_pool),
  nrplanner/advisorbar.py (asking_from, held_slot, AdvisorBar._ask),
  nrplanner/app.py (RelicSlot, held_slot_indices, active_slots), nrplanner/
  inventory.py (load, _scan_save), nrdata/savefile.py (find_saves,
  save_roots, read_owned_relics, find_loadout_table); scripts/
  measure_picker_cards.py, scripts/measure_advisor_picker.py, scripts/
  measure_advisor_search.py
GEÄNDERT: docs/perf/baselines.md (Abschnitte S11-E fortgeschrieben, S11-I/J/K
  neu; committet 596b725), docs/berichte/T-140-performance-tuner.md (diese
  Datei). Kein Anwendungscode angefasst.
ANNAHMEN: (1) "sechs freie Slots" im Messszenario-Satz des Auftrags ist A6s
  kanonischer Szenario-Satz (identisch zu T-118 Abschnitt 2.2) und gilt fuer
  die Familie der S11-Messungen als Ganzes; die vier Einzelzahlen halten sich
  an ihre je eigene, in ARCHITECTURE.md benannte Konfiguration (S11-A "sechs
  frei" fuer OF-25/U3, S11-B/C "ein Slot frei, fuenf gehalten" fuer U7/OF-26
  Picker-Zweig) — beide S11-Faelle stehen bereits in docs/perf/baselines.md.
  (2) ARCHITECTURE.md Nachtrag IX (Fassung 2) weist der U7-Zeile zwei weitere
  Messungen zu (Cache-Eintragsgroesse gegen 140 KiB, IX-3.2; Trefferquote
  unter dem kanonischen Schluessel, IX-3.3), die docs/tasks/T-140.md nicht
  nennt. Ich habe den Auftrag als engeren, gueltigen Zuschnitt genommen (vier
  Zahlen, wie explizit gezaehlt) und beide Punkte NICHT gemessen — das ist
  unten als Luecke an den director gemeldet, keine eigenmaechtige
  Scope-Erweiterung. (3) Bei der "gesamt"-Zeile in S11-E ist nicht rekonstruierbar,
  ob T-118s Uhr vor oder nach den Modulimporten startete (die Harness existiert
  nicht mehr); ich benenne das als Annahme, nicht als Tatsache, und stuetze die
  Kernaussage von U3 ausschliesslich auf die eindeutig vergleichbare Zeile
  `inventory.load`.
NÄCHSTER: director
BLOCKIERT DURCH: nichts. Eine Entscheidung liegt jetzt vor (Stufe-B-Ausloeser
  greift, s. u.) und wartet auf die Vergabe als developer-Auftrag; zwei
  Luecken (ARCHITECTURE.md vs. T-140-Scope, "gesamt"-Zeile) warten auf
  Kenntnisnahme, nicht auf eine Entscheidung von mir.
```

---

## Die vier Zahlen und die Stufe-B-Entscheidung — zuerst

| # | Frage | Vorher | Jetzt | Urteil |
|---|---|---|---|---|
| **U7** | Haelt A6s dritte Zeile (Hauptthread ≤ 50 ms) beim Oeffnen des Pickers? | 318,1 ms (S11-C, T-118) | **7,2–7,5 ms** (Median n=25, zwei unabhaengige Laeufe) | **Haelt jetzt**, mit 42–44x Abstand statt 6,3x Verletzung |
| **OF-26** | Hauptthread-Rest (Anfragebau + `frozen_inventory` + `inventory_fingerprint`), nie gemessen | — | **6,2–8,0 ms**, auf Picker- **und** Optimize-Weg praktisch gleich | Kein Ueberraschungsfund: 12–16 % des 50-ms-Budgets, keine Optimierung noetig |
| **OF-25** | Verlangsamt eine gleichzeitig laufende Picker-Frage `Optimize`? | Solo 5023,6 ms (S11-A, T-118) | Solo **5282,5 ms**, gleichzeitig **5383,9 ms** (n=5 je Reihe, diese Sitzung) | **Differenz 1,9 %, unter der 3,3–3,5 % Eigenstreuung** — kein messbarer GIL-Effekt; A6s 6-s-Zeile haelt in beiden Reihen |
| **U3** | `inventory.load` nach den zwei Vorfiltern (T-133, T-136) | 6147,6 ms (S11-E, T-118) | **657,2 ms** (Median n=5, Spanne 645,4–722,4) | **9,35x** — bestaetigt die hergeleiteten 9,2x aus AD-029 auf 1,3 % genau |

**Stufe-B-Entscheidung (AD-029): Stufe B wird gebaut.** Die Schwelle ist
250 ms Median; gemessen sind **657,2 ms** — **163 % darueber**, weit
ausserhalb der 9,9 % Streuung dieser Reihe. Diese Entscheidung liegt laut
AD-029 beim `performance-tuner` und ist hiermit getroffen, nicht beim
`director` — der `director` vergibt jetzt den Bauauftrag an den `developer`.

**Nichts wurde optimiert.** Alle vier Zahlen sind Nachmessungen an bereits
umgesetztem Code (U1/T-133, T-136 fuer den Scan; U5a-U6 fuer den Worker-Weg
des Pickers). Ich habe keine Codezeile geaendert.

---

## 1. Scope, Messszenario, Umgebung

### 1.1 Was zu messen war und was ich vorher geprueft habe

Vier Zahlen aus `docs/tasks/T-140.md`, alle nach dem Zuschnitt des Auftrags
(nicht nach der breiteren Fassung 2 in `ARCHITECTURE.md` Nachtrag IX — dazu
unter „Befunde an den director"). **Vor der ersten Messung geprueft, wie die
Aufgabe verlangt:**

- **`scripts/measure_picker_cards.py`** ist **nicht** das richtige
  Messgeraet fuer U7: es misst Kartenzahlen und Pixelmasse (S11-H), nicht die
  Hauptthread-Haltezeit. Der T-132-Wait auf `dialog.waiting` ist vorhanden
  und korrekt, aber das Skript beantwortet eine andere Frage. Ich habe ein
  eigenes Messgeraet gebaut (Abschnitt 3), das den wirklichen Produktionsweg
  misst (`relicpicker.SlotAdvice.ask()` ueber die echte zweite
  `AdvisorController`-Instanz), nicht `candidates.pool` wie die alte S11-B/C-
  Messung.
- **Parallelitaet geprueft:** `git status` vor Beginn war sauber, Commit
  `ac9a5c9` entspricht dem im Auftrag genannten Stand. Waehrend des Laufs kein
  fremder Commit (`git log` am Ende zeigt `ac9a5c9` als Basis meines eigenen
  Commits `596b725`).

### 1.2 Umgebung

| | |
|---|---|
| Rechner | AMD Ryzen 7 5800H, 1102 MHz (5 Stichproben, alle 1102), Nennwert 3201 MHz |
| Energieplan | `Legion Quiet Mode` (`powercfg /getactivescheme`, identisch zu T-118) |
| Betriebssystem | Windows 10 10.0.19045 |
| Python | 3.12.10 CPython, `.venv` des Projekts |
| Rechenlastprobe | 1114,4 ms Median fuer 3 Mio. `x += i*i` (Spanne 1010,3–1189,0, n=5) — **7,5 % schneller** als T-118s 1205 ms |
| Fremdlast | mehrere `claude`-Prozesse und `chrome` mit hoher kumulierter CPU-Zeit liefen parallel (andere Sitzungen/Tabs); keine verwaisten `find`-Prozesse wie in T-118 |
| Codestand | `ac9a5c9` (Auftragscommit), kein Code geaendert |
| Datenabzug | fester Testabzug, 841 Dateien, `EXTRACT_VERSION` 11, unveraendert seit T-118 |
| Datenmenge, gezaehlt statt behauptet | **309 Relikte, 110 Loadouts** (per Skript ausgezaehlt), zwei Spielstanddateien |

**Rechenlastprobe ist schneller, aber die OF-25-Optimize-Zeit ist 5,2 %
langsamer als T-118s Baseline** (Abschnitt 5) — das ist benannt, nicht
erklaert, weil ich die Ursache nicht zweifelsfrei zuordnen kann.

### 1.3 Die Datenschutzsperre — Nachweis mit Gegenprobe (QA-195)

Alle drei Umlenkungen gegen ihren ungelenkten Fall geprueft, wie L-009/QA-195
es verlangen — die Pruefung zeigt in beiden Faellen einen **unterschiedlichen**
Pfad, nicht nur "gleich" oder "verschieden" ohne Gegenprobe:

| Pruefpunkt | ohne Umlenkung (Positivkontrolle) | mit Umlenkung |
|---|---|---|
| `paths.cache_dir()` | `C:\Users\Daniel\AppData\Local\NightreignHelper` | `…\scratchpad\T-140\local\NightreignHelper` |
| `shortcut.shortcut_path()` | `…\Roaming\Microsoft\…\Programs\Nightreign Helper.lnk` | `…\scratchpad\T-140\appdata\Microsoft\…\Programs\Nightreign Helper.lnk` |
| `favourites.ORG`/`APP` | `DankYeeter` / `NightreignHelper` | `DankYeeterT-140` / `NightreignHelper` |

**Save-Erkennung bleibt trotz umgelenktem `APPDATA` auf dem echten
Spielstand** — geprueft, nicht angenommen: `nrdata/savefile.save_roots()`
haengt den echten Save-Ordner zusaetzlich ueber `pathlib.Path.home() /
"AppData" / "Roaming"` an, unabhaengig vom Umgebungsvariablenwert. Mit
umgelenktem `APPDATA` fand `find_saves()` beide echten Dateien:

```
C:\Users\Daniel\AppData\Roaming\Nightreign\76561198073567627\NR0000.sl2
C:\Users\Daniel\AppData\Roaming\Nightreign\76561198179244962\NR0000.sl2
```

**Fester Testabzug kopiert, nicht neu gebaut** (3,3 s, `Copy-Item -Recurse`),
in das umgelenkte `LOCALAPPDATA` hineinkopiert.

**Registry-Schreibprobe:** eine echte Schreibprobe entsteht automatisch, weil
der Fenstertest `QSettings` beruehrt — `HKCU\Software\DankYeeterT-140` existierte
nach dem Lauf tatsaechlich (`reg query`, ein Treffer), belegt, dass die
Umlenkung wirklich griff, nicht nur einen Namen zeigte. Aufgeraeumt (`reg
delete`) und die Loeschung mit `reg query` bestaetigt (Fehlermeldung
"unable to find the specified registry key"). `HKCU\Software\DankYeeter`
(die echte Registry) blieb unberuehrt — nur `NightreignHelper` und
`NightreignHelperTests` stehen darunter, kein `T-140`-Zweig.

**Vier schutzwuerdige Baeume, sha256-Fingerabdruck vor und nach der ganzen
Reihe (inklusive Positivkontrolle des Fingerabdrucks selbst):**

| Baum | vorher | nachher |
|---|---|---|
| `%LOCALAPPDATA%\NightreignHelper` | `364ae9a5f679318b` | `364ae9a5f679318b` |
| `%APPDATA%\Nightreign` (Spielstaende) | `98e2fdaa17546f1d` | `98e2fdaa17546f1d` |
| Startmenue `…\Programs` | `f6836bd478045402` | `f6836bd478045402` |
| `%LOCALAPPDATA%\NightreignHelper-Testabzug` | `364ae9a5f679318b` | `364ae9a5f679318b` |

**Positivkontrolle des Fingerabdruck-Werkzeugs selbst:** an einem
Wegwerfverzeichnis gezeigt, dass es sowohl auf ein geaendertes Byte
(`6848513a7403ba0c` → `cbb34dd65d026f61`, Datei erweitert) als auch auf eine
zusaetzliche Datei anschlaegt — ein Werkzeug, das nur "gleich" sagen kann,
waere kein Nachweis. Ein erster Testlauf dieser Kontrolle lieferte einen
verdaechtig identischen Wert nach einer Dateierweiterung; nachgefahren mit
frischem Verzeichnis und expliziter `ls`-Kontrolle zwischen den Schritten
zeigte sich, dass es ein Artefakt der ersten Testfuehrung war (wahrscheinlich
eine verzoegerte Dateisystem-Sichtbarkeit zwischen zwei schnellen
Bash-Aufrufen) — beim sauberen Nachlauf hat die Kontrolle zweimal
angeschlagen, wie erwartet.

**Aufgeraeumt, geprueft statt zugesichert:** die kopierten `local`/`appdata`-
Baeume unter dem Scratchpad sind entfernt; kein `python.exe` laeuft mehr
(`Get-Process python` liefert 0 Treffer); kein Server wurde gestartet, also
kein Port zu pruefen.

---

## 2. U7 — Haelt A6s dritte Zeile?

**Das Messgeraet musste neu gebaut werden**, weil `candidates.pool` seit U5b
nicht mehr der Weg ist, den der Picker beim Oeffnen geht
(`relicpicker.py:340`: „Nothing is computed here any more"). Gemessen wird
jetzt der wirkliche Aufruf aus `RelicPicker.__init__` Zeile 924:
`self.advice.ask(self._the_answer_arrived)` — `SlotAdvice.ask()` ueber die
echte zweite `AdvisorController`-Instanz des Fensters
(`window.picker_advisor`, `PICKER_DEBOUNCE_MS=0`, `PICKER_CACHE_SIZE=64`),
mit dem echten `window.owned` (309 Relikte).

**Szenario, identisch zu S11-C Slot 2:** `Wylder`, `Wylder's Chalice` +
Deep of Night, Stufe 15, weisser Slot (Farbe 4) frei, die fuenf anderen mit
einem passenden Relikt aus dem echten Bestand besetzt (per
`RelicSlot.select_copy(handle)`, dieselbe Auswahlregel wie
`scripts/measure_advisor_picker.py`s `a_relic_for`) — **206 Kandidaten**,
exakt wie S11-C. **Erzwungener Fehltreffer:** Cache vor jedem der 25 Rufe
geleert, jeweils eine neue `SlotAdvice`, genau das Verhalten eines Spielers,
der eine bisher ungefragte Kombination oeffnet.

| Was | Lauf 1 (n=25) | Lauf 2 (n=25) |
|---|---|---|
| `SlotAdvice.ask()`, Hauptthread, Fehltreffer | **7,165 ms** (6,648–10,111) | **7,539 ms** (6,609–10,462) |
| Zeit bis die Antwort ankommt (Rechnung im Worker) | 315,220 ms (303,771–345,281) | 312,704 ms (300,869–363,232) |
| `SlotAdvice.ask()`, Hauptthread, Treffer (Cache) | 7,051 ms (6,340–55,316) | 7,212 ms (6,355–53,081) |

**Antwort: A6s dritte Zeile haelt, mit 42–44x Abstand statt 6,3x
Verletzung.** Von 318,1 ms auf 7,2–7,5 ms Median, reproduziert ueber zwei
unabhaengige volle Laeufe (Abweichung der Mediane 5,2 %). **Die
Kandidatenrechnung ist nicht schneller geworden — sie ist umgezogen:** die
Zeile „Zeit bis die Antwort ankommt" (312,7–315,2 ms) liegt innerhalb der
10,3 % Streuung, die S11-C fuer die alte 318,1-ms-Zahl schon auswies. Wirkung
und Ursache sind sauber getrennt: AD-028 traegt die ganze Verbesserung.

**Grenze des Vergleichs, benannt (L-009):** S11-B/C massen `candidates.pool`
ohne Qt, als reine Funktion. Diese Messung geht mit Qt durch
`AdvisorController`, weil der Weg das seit U5b verlangt. Ein „ohne Qt" gegen
„mit Qt" ist zwei verschiedene Messgeraete, nicht nur zwei Codepfade — die
Rechenzeit (Zeile 2 der Tabelle) ist trotzdem vergleichbar, weil
`run.slot_pool` denselben `candidates.pool`-Aufruf macht; die
Hauptthread-Zeile (Zeile 1) ist ein wirklich neues Messgeraet.

**Nicht gemessen, obwohl `ARCHITECTURE.md` es der U7-Zeile zuweist** (Fassung
2, Nachtrag IX-3): Cache-Eintragsgroesse gegen die 140-KiB-Schranke (IX-3.2)
und die Trefferquote der beiden Spuren unter dem kanonischen Schluessel
(IX-3.3). `docs/tasks/T-140.md` zaehlt vier Zahlen, diese zwei sind keine
davon — Befund an den `director`, Abschnitt 6.

---

## 3. OF-26 — Der Hauptthread-Rest, zerlegt

Zerlegt in seine drei Bestandteile, direkt aufgerufen (reine Funktionen,
keine Seiteneffekte, deckungsgleich mit dem, was `_question_from` in
`worker.py` intern tut). Gemessen fuer **beide** Wege, wie OF-26 verlangt:

| Bestandteil | Weg | Lauf 1 | Lauf 2 |
|---|---|---|---|
| `advisorbar.asking_from` | Picker | 0,200 ms | 0,295 ms |
| `advisor_run.frozen_inventory` (309 Kopien) | Picker | 4,151 ms | 4,945 ms |
| `advisor_run.inventory_fingerprint` (sha256, 309 Zeilen) | Picker | 1,911 ms | 2,754 ms |
| **Summe** | Picker | **6,262 ms** | **7,994 ms** |
| `advisorbar.asking_from` | Optimize | 0,223 ms | 0,215 ms |
| `advisor_run.frozen_inventory` (309 Kopien) | Optimize | 4,295 ms | 4,108 ms |
| `advisor_run.inventory_fingerprint` (sha256, 309 Zeilen) | Optimize | 1,900 ms | 1,893 ms |
| **Summe** | Optimize | **6,418 ms** | **6,216 ms** |

**Antwort: kein Ueberraschungsfund.** 6,2–8,0 ms von 50 ms Budget = 12–16 %,
auf beiden Wegen fast gleich (beide teilen `_question_from`, beide bauen 309
Kopien plus Fingerabdruck, unabhaengig davon wie viele Slots frei sind).
Zusammen mit U7 Zeile 1 (7,2–7,5 ms) ergibt sich der ganze
Hauptthread-Aufenthalt beim Oeffnen des Pickers — **rund 7,5 ms insgesamt**,
nicht zusaetzlich zu den 6,2–8,0 ms: die volle `ask()`-Zeile umfasst diese
drei Bestandteile bereits, der Rest (rund 1 ms) ist Problem-Zusammenbau,
Signalverbindung und Cache-Abfrage, hier nicht gesondert gemessen.

**Streuung bei so kleinen Werten:** 2s/Median liegt bei 43–74 % — bei
Werten unter 5 ms ist das kein brauchbares Mass, die absolute Streuung
(0,3–7 ms) ist Scheduler-Jitter dieser Groessenordnung. Beurteilt gegen die
absolute 50-ms-Untergrenze: selbst die ungeguenstigste Einzelmessung
(11,2 ms) bleibt unter einem Viertel des Budgets.

---

## 4. OF-25 — Ueberlappung zweier rechnender Spuren

`Optimize` (sechs freie Slots, nichts gehalten — S11-A-Fall) allein gegen
`Optimize` waehrend gleichzeitig eine Picker-Frage am weissen Slot (206
Kandidaten, S11-C-Fall) laeuft. Die fuenf anderen Slots tragen ein Relikt
(fuer eine realistische Picker-Frage), sind aber **nicht** gehalten — der
Picker haelt die anderen Slots so, wie sie physisch stehen, unabhaengig vom
`Hold`-Schalter (AD-018.1); `Optimize` liest den Schalter und sieht
weiterhin sechs freie Slots. Beide Fragen so gleichzeitig wie moeglich
gestartet: `Optimize` zuerst (250 ms Entprellung), die Picker-Frage im
selben Tick hinterher (0 ms Entprellung) — ihr Worker laeuft also schon,
wenn `Optimize`s Worker startet.

| Reihe | p50 (n=5) | Spanne | 2s/Median |
|---|---|---|---|
| `Optimize`, allein | **5282,5 ms** | 5241,7–5469,5 ms | 3,5 % |
| `Optimize`, mit gleichzeitiger Picker-Frage | **5383,9 ms** | 5351,0–5576,2 ms | 3,3 % |

**Antwort: keine gemessene Verlangsamung ueber der Signifikanzschwelle.**
Differenz der Mediane 101,3 ms = **1,9 %** — unter der 5-%-Schwelle dieses
Szenarios und unter der 3,3–3,5 % Eigenstreuung beider Reihen. `Optimize`
bleibt mit 5383,9 ms deutlich unter den 6 s aus A6 (10,3 % Luft). Die Sorge
aus OF-25 (GIL-Teilung zweier Python-Threads) war begruendet, trifft hier
aber nicht in messbarer Groesse zu — vermutlich weil die Picker-Frage (rund
313 ms Rechenzeit, aus U7) nur einen kleinen Teil von `Optimize`s rund 5,3 s
ueberlappt.

**Randbemerkung, ehrlich benannt:** Der Solo-Median dieser Reihe (5282,5 ms)
liegt 5,2 % ueber S11-As Solo-Median (5023,6 ms, T-118) und ausserhalb von
dessen damaliger Spanne. Kein Code auf diesem Pfad hat sich seit T-118
geaendert; die Rechenlastprobe dieser Sitzung ist sogar 7,5 % schneller als
die aus T-118, was eine langsamere Maschine als Erklaerung ausschliesst. Die
wahrscheinlichste Ursache ist Sitzungsrauschen (mehrere parallel laufende
`claude`/`chrome`-Prozesse, Abschnitt 1.2) — **belegt ist das nicht**, und
ich melde die Zahl deshalb, statt eine Ursache zu erfinden. Der **Vergleich
innerhalb dieser Sitzung** (allein gegen gleichzeitig, beide unter denselben
Bedingungen) ist davon unberuehrt und traegt die Aussage von OF-25.

---

## 5. U3 — `inventory.load` und der Prozessstart, und die Stufe-B-Entscheidung

**Szenario identisch zu S11-E:** vom Prozessstart bis zum benutzbaren
Zustand, ohne Fenster, ohne Qt, n=5, je ein frischer Prozess, echter
Spielstand (309 Relikte, 110 Loadouts, zwei Dateien).

| Schritt | Vorher (76f1887) | Jetzt (ac9a5c9) | Faktor |
|---|---|---|---|
| **`inventory.load`** | **6147,6 ms** (6091,9–6299,4) | **657,2 ms** (645,4–722,4) | **9,35x** |
| gesamt (Import + json.loads + configure + inventory.load) | 6593,7 ms | 1377,9 ms | s. Vorbehalt unten |
| davon Modulimporte | nicht ausgewiesen | 320,5 ms (davon 222–227 ms `Crypto.Cipher.AES` allein) | — |
| davon `json.loads` | 406,8 ms | 366,7 ms | — |
| davon `model.configure` | 0,4 ms | 0,5 ms | — |

**Vorbehalt zur "gesamt"-Zeile, damit sie nicht falsch gelesen wird:** die
alte Zeile minus ihre drei ausgewiesenen Teile laesst nur 38,9 ms unerklaert
— deutlich weniger als die 320,5 ms, die Modulimporte jetzt allein kosten
(davon 222–227 ms isoliert fuer `from Crypto.Cipher import AES`, **dieselbe
Abhaengigkeit stand schon im damals gemessenen Commit** `76f1887`, per
`git show` nachgesehen). Die einzige damit vereinbare Erklaerung: T-118s Uhr
begann nach den Modulimporten, meine davor — die Harness von T-118 existiert
nicht mehr (T-118 Befund 6), das laesst sich nicht am Code pruefen. Ich
nenne das als Annahme, nicht als Tatsache, und stuetze U3 ausschliesslich
auf die eindeutig vergleichbare Zeile `inventory.load` — dieselbe Funktion,
derselbe Aufruf, kein Uhr-Grenzenstreit.

**Herleitung aus AD-029 bestaetigt:** `ARCHITECTURE.md` leitet aus S11-E
**666 ms** fuer `inventory.load` nach dem Vorfilter her, ausdruecklich als
Herleitung, nicht Messung, gekennzeichnet. Gemessen sind **657,2 ms** — die
Herleitung lag **1,3 %** daneben, innerhalb der 9,9 % Streuung dieser Reihe.
Meine Zahl bestaetigt die Herleitung, ersetzt sie aber als Messwert: sie
deckt zusaetzlich `find_loadout_table` (T-136) ab, das in der Herleitung
nicht gesondert vorkam.

### Die Entscheidung

**AD-029 setzt die Schwelle auf 250 ms Median fuer `inventory.load`. Gemessen
sind 657,2 ms — 163 % darueber, weit ausserhalb der 9,9 % Streuung.**

> **Stufe B (Verlagerung des Lesens in einen Worker) wird gebaut.**

Diese Entscheidung liegt laut AD-029 explizit beim `performance-tuner`
("entscheidet den Ausloeser fuer Stufe B") und ist hiermit getroffen — nicht
beim `director`. Der `director` vergibt jetzt den Bauauftrag an den
`developer` (Umfang laut AD-029: `nrplanner/inventory.py`, ein neues kleines
Qt-Modul fuer die Spur, `nrplanner/app.py`, **nach** der `UI_SPEC`-Ergaenzung
fuer den dritten Fensterzustand, die U4/`ui-ux-designer` liefert).

---

## 6. Verworfene Optimierungen

Keine — dieser Lauf war ein reiner Messlauf, wie der Auftrag es verlangt
("Miss zuerst"). Kein Code wurde geaendert, also gibt es nichts zu verwerfen
oder zu bestaetigen.

---

## 7. Verifikationsstatus

**Kein Code geaendert**, also kein „Verhalten vorher/nachher" zu sichern.
Verifiziert ist die **Gueltigkeit der Messung**:

| Was | Wie | Ergebnis |
|---|---|---|
| Die drei Umlenkungen greifen | dieselbe Pruefung umgelenkt und ungelenkt, plus echte Registry-Schreibprobe | 3 von 3, Gegenprobe zeigt jeweils den echten Pfad |
| Save-Erkennung funktioniert trotz Umlenkung | `find_saves()` mit umgelenktem `APPDATA` aufgerufen | beide echten Dateien gefunden |
| Nichts geschrieben | sha256-Fingerabdruck vor/nach ueber vier Baeume | 4 von 4 gleich |
| Das Messmittel kann anschlagen | Positivkontrolle: Byte geaendert, Datei hinzu (an einem frischen Wegwerfverzeichnis, nach einem verworfenen ersten Versuch nachgefahren) | schlaegt in beiden Faellen an |
| Das Szenario ist das beauftragte | Relikte/Loadouts per Skript ausgezaehlt | 309 Relikte, 110 Loadouts |
| U7 reproduziert | zwei unabhaengige volle Laeufe | Mediane 7,165/7,539 ms, 5,2 % Abweichung |
| Der weisse Slot traegt dieselbe Kandidatenzahl wie S11-C | im Skript ausgegeben | 206, exakt wie S11-C |
| Erzwungener Fehltreffer/Treffer wirklich erzwungen | `assert asked.ranking is None` (Fehltreffer) bzw. `is not None` (Treffer) in jeder der 50 Iterationen | keine Assertion ist gefallen |
| Kein Fremd-Commit im Zeitfenster | `git log` vor/nach: Basis `ac9a5c9`, mein Commit `596b725`, sonst nichts | bestaetigt |
| Aufgeraeumt | Scratchpad-Kopien entfernt, Registry-Zweig geloescht und mit `reg query` als fehlend bestaetigt, keine `python.exe` mehr aktiv, kein Server gestartet | bestaetigt |

**Was ich nicht verifiziert habe:** die Testsuite ist **nicht** gelaufen —
ich habe keine Codezeile angefasst, ein Volllauf waere Selbstbestaetigung
statt Messung. Die zuletzt genannte Zahl (1398 passed, 9 skipped, T-139)
gilt unveraendert fuer den Codestand `ac9a5c9`.

---

## 8. Befunde und Empfehlungen an andere Rollen

Alle ohne Nummer — Befund-IDs vergibt der `director`.

**An den `director`:**

1. **Stufe-B-Entscheidung liegt vor** (Abschnitt 5): bauen. Vergabe an den
   `developer`, nach der `UI_SPEC`-Ergaenzung fuer den dritten Fensterzustand
   (U4, `ui-ux-designer`) — AD-029 verlangt diese Reihenfolge ausdruecklich.
2. **Luecke zwischen `ARCHITECTURE.md` und `docs/tasks/T-140.md`.** Nachtrag
   IX (Fassung 2, Zeile 4878) weist der U7-Zeile zwei weitere Messungen zu:
   Cache-Eintragsgroesse der Picker-Spur gegen die 140-KiB-Schranke (IX-3.2)
   und die Trefferquote der beiden Spuren unter dem kanonischen Schluessel
   ohne Richtung (IX-3.3). `docs/tasks/T-140.md` zaehlt „vier Zahlen" und
   nennt beides nicht. Ich habe den engeren, im Auftrag stehenden Zuschnitt
   genommen und beide Punkte **nicht gemessen** — das ist eine offene Luecke,
   keine erledigte Aufgabe. Ebenfalls offen: **OF-28** (Nachtrag IX, Zeile
   4929), an den `performance-tuner` fuer U7 adressiert, in `docs/tasks/T-140.md`
   ebenfalls nicht genannt und von mir nicht bearbeitet.
3. **Die "gesamt"-Zeile in S11-E hat einen ungeklaerten Uhr-Grenzenstreit**
   (Abschnitt 5, Vorbehalt): T-118s Messung liess nur 38,9 ms fuer
   Modulimporte, meine misst 320,5 ms dafuer, obwohl dieselbe Abhaengigkeit
   (`Crypto.Cipher.AES`) schon im damaligen Commit stand. Die T-118-Harness
   existiert nicht mehr und kann nicht nachgepruft werden. Betrifft die
   Vergleichbarkeit der „gesamt"-Zahl, **nicht** die tragende
   `inventory.load`-Zahl, die sauber vergleichbar ist.
4. **OF-25s Solo-Baseline liegt 5,2 % ueber der alten** (Abschnitt 4,
   Randbemerkung), ohne Codeaenderung auf diesem Pfad und trotz einer
   schnelleren Rechenlastprobe dieser Sitzung. Nicht als Regression
   gemeldet, weil unbelegt — aber der `director` sollte wissen, dass die
   absolute Zahl (5282,5 ms Solo) naeher an der 6-s-Schranke liegt als
   T-118s 5023,6 ms, falls kuenftig ein knapperer Fall gemessen wird.
5. **Kein Sicherheitsfund, kein Bug.** Beim Bau des Messgeraets sind keine
   Abweichungen vom dokumentierten Verhalten aufgefallen — `held_slot`,
   `frozen_inventory`, `inventory_fingerprint`, `AdvisorController` verhalten
   sich exakt wie in `ARCHITECTURE.md`/`worker.py`s Docstrings beschrieben.

**An den `developer`:** Stufe B aus AD-029 ist ein Folgeauftrag mit dem
Vorher-Wert 657,2 ms aus `docs/perf/baselines.md` S11-E. Formvorgaben stehen
in AD-029 Punkt 1–5 (Thread-Grenze zwischen Lesen und Bauen, kein
`processEvents`, Cache-Entwertung bei Ankunft statt Beginn, ein Lesen zur
Zeit, dritter Fensterzustand ist Oberflaeche).

**An den `ui-ux-designer`:** der dritte Fensterzustand ("wird gelesen") aus
AD-029 Punkt 5 wird jetzt gebraucht — die Stufe-B-Entscheidung ist gefallen.

**An den `security-reviewer`:** keine neue Beruehrung der Vertrauensgrenze
durch diesen Lauf (nur gemessen, nichts gebaut). AD-029s Hinweis zur
Vorfilter-Pruefung an der praeparierten Datei (U2) bleibt unveraendert
gueltig und ist nicht mein Auftrag.

**An den `qa-engineer`:** keine neue Testabdeckung noetig aus diesem Lauf
(keine Codeaenderung). Fuer den kommenden Stufe-B-Auftrag: der dritte
Fensterzustand und das "ein Lesen zur Zeit"-Verhalten (AD-029 Punkt 4)
werden neue Testfaelle brauchen, sobald der `developer` sie baut.
