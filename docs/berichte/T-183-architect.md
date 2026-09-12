# T-183 — Gegenprobe und Abnahme zu T-182 (architect)

```
STATUS: erledigt
AUFTRAG: T-183 — T-182 zu Ende bringen: Gegenprobe und Bericht (architect)
GELESEN: ~/.claude/agents/_rahmen.md · CLAUDE.md · GOAL.md · docs/state.md ·
  docs/tasks/T-183.md · docs/tasks/T-182.md · ARCHITECTURE.md (Kopf, alle H2,
  Themenbereich D, AD-028/Nachtrag IX/X) · ARCHITECTURE_REGISTER.md (ganz) ·
  docs/archiv/architecture-verlauf.md (Kopf und Rumpfvergleich) ·
  git show de710a5:ARCHITECTURE.md · git show e06386c:qa/findings.md ·
  git show e06386c:security/findings.md · qa/findings.md · qa/verlauf.md ·
  security/verlauf.md · docs/perf/baselines.md · docs/lessons.md ·
  docs/archiv/berichte/T-041, T-084, T-085, T-086, T-122, T-125, T-128, T-135 ·
  docs/berichte/T-140, T-143, T-144 · docs/archiv/tasks/T-125, T-130, T-134
GEAENDERT: docs/berichte/T-183-architect.md (neu) — die einzige Projektdatei.
  Ausserdem, ausserhalb des Projektbestands, mein eigenes Rollengedaechtnis:
  .claude/agent-memory/architect/MEMORY.md und
  .claude/agent-memory/architect/project_parallele_laeufe.md (beide neu).
  Nichts gestaged, nichts committet, nichts gepusht.
ANNAHMEN: (1) Massgeblicher Messstand ist der Arbeitsbaum an HEAD d90e791; ich
  habe nachgewiesen, dass ARCHITECTURE.md, ARCHITECTURE_REGISTER.md und
  docs/archiv/architecture-verlauf.md seit 9098229 unveraendert sind
  (git log 9098229..HEAD auf diese Pfade ist leer). (2) Die Zeilennummern der
  Registerspalten lese ich nach der im Register selbst festgelegten Konvention
  als Nummern der Fassung de710a5.
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

---

## 0. Messgrundlage

Alle Zahlen dieses Berichts stammen aus dem Arbeitsbaum an HEAD `d90e791`,
Altstand `de710a5` ueber `git show`. Reine Dokumentenarbeit: kein
Programmstart, kein Bau, keine Suite — so beauftragt.

**Der Arbeitsbaum war bei Beginn dieses Laufs sauber und ist es jetzt nicht
mehr.** Waehrend T-183 lief, haben die parallelen Auftraege T-180 und T-184
geschrieben: `qa/findings.md` und `security/findings.md` sind veraendert,
`qa/verlauf.md`, `security/verlauf.md` und `docs/archiv/ui-spec-verlauf.md`
sind neu und nicht versioniert. Das ist fuer Befund B-1 tragend. Meine drei
Pruefgegenstaende sind davon nicht beruehrt.

---

## 1. Gegenprobe der Zahlen aus dem Auftrag

Alle sieben Messungen des Directors sind **bestaetigt**, jede von mir selbst
nachgefahren.

| Messung | Auftrag | eigene Messung | Urteil |
|---|---|---|---|
| H2-Abschnitte in `ARCHITECTURE.md` | 20 (vorher 21) | **20**; `de710a5`: **21** | bestaetigt |
| davon Nachtrag/Director-Korrektur | 0 (vorher 11) | **0**; `de710a5`: **11** | bestaetigt |
| AD-IDs in `ARCHITECTURE.md`, keine verloren | 32 | **32**; Menge deckungsgleich mit `de710a5` (AD-001 bis AD-032, kein Zugang, kein Abgang) | bestaetigt |
| AD-Zeilen in `ARCHITECTURE_REGISTER.md` | 32 | **32** | bestaetigt |
| OF-Zeilen in `ARCHITECTURE_REGISTER.md` | 32 | **32** | bestaetigt |
| Dubletten im Register | keine | `sort` + `uniq -d` in beiden Tabellen **leer** | bestaetigt |
| Zeilen ARCHITECTURE + Verlauf | 6129 + 6137 = 12266 (Altstand 5972) | **6129 + 6137 = 12266**; `de710a5`: **5972** | bestaetigt |

### Eine Zahl, die der Auftrag nicht auffuehrt und die sich geaendert hat

Die Zaehlung der verschiedenen OF-Nummern in `ARCHITECTURE.md` liefert heute
**33**, an `de710a5` lieferte sie **32**. Grund: die Buchfuehrungszeile in
`ARCHITECTURE.md` Z. 42 nennt die nie vergebene Nummer **OF-14** woertlich.
**Sachlich hat sich nichts geaendert** — es gibt weiterhin 32 OF-Vorgaenge —,
aber wer diese Zaehlung als Waechter oder Kennwert benutzt, bekommt ab jetzt
33 und muss die Buchfuehrungszeile ausnehmen. Die Zahl gehoert nicht
ungefiltert nach `docs/state.md`.

### Zwei Messungen, die der Auftrag nicht verlangt, die die Abnahme aber erst tragen

**(a) Der Verlauf ist bytegleich mit dem Altstand.** Der Kopf der
Verlaufsdatei ist genau **165** Zeilen; ab Zeile 166 folgt der Altstand.
Der Rumpf ab Zeile 166 gegen `git show de710a5:ARCHITECTURE.md`: beide
**5972** Zeilen, `diff` **leer**, md5 beidesmal
`8f34c8bce819c004bd154e28a48e169c`. Damit ist die Vorgabe aus T-182
("Nichts wird inhaltlich gestrichen") nicht behauptet, sondern belegt — und
zwar staerker, als die blosse Zeilensumme es kann, denn eine Summe ueberlebt
auch einen Austausch.

**(b) In `ARCHITECTURE.md` selbst ist keine Entscheidungszeile
verlorengegangen.** Mengenvergleich der nichtleeren, verschiedenen Zeilen alt
gegen neu:

- **12** Zeilen des Altstands fehlen im neuen — und es sind **genau** die
  zwoelf H2-Ueberschriften, die zu H3 herabgestuft wurden (elf Nachtraege plus
  "Wichtige Korrektur zur Auftragslage (erledigt)"). Keine davon ist Inhalt.
- **104** Zeilen sind neu — alle Wegweiser: der Lesehinweis, die sechs
  Themenbereichs-Koepfe mit Einleitung, die Zuordnungstabelle Bereich/AD, der
  Verweiskasten bei den offenen Fragen, der Abschnitt "Verlauf".
  **Keine Entscheidungszeile, kein geaenderter Entscheidungstext.**
- `### AD-`-Ueberschriften: **30** alt, **30** neu, dieselbe Menge.
  `###` gesamt: **108** alt, **120** neu — die Differenz ist exakt die
  Herabstufung der zwoelf H2.
- Die Zuordnungstabelle Bereich A bis F fuehrt **9+7+5+4+4+1 = 30** AD. Das
  ist die Gegenprobe zu "Gebaute Entscheidungen: 30" im Register (32 minus
  AD-027 nie vergeben, minus AD-032 nur Nummernkreis). Beide Zaehlungen
  stimmen ueberein und sind unabhaengig entstanden.

Die Vorgabe "Keine neue AD-Nummer, keine neue Entscheidung, kein geaenderter
Wortlaut" ist damit gemessen eingehalten, nicht nur zugesichert.

---

## 2. Die OF-Bilanz — worauf der Director wartet

**32 Nummern. 12 offen · 17 beantwortet · 1 beantwortet mit benanntem Rest ·
1 unklar · 1 nie vergeben.** Summe 32, jede Nummer in genau einer Klasse.

### Offen — 12

| OF | Frage in einer Zeile | wartet auf |
|---|---|---|
| **OF-3** | Gewichtung der acht Schadensarten fuer `min_damage_taken`, und bekommt der Spieler ein Bedienelement? | Nutzer, ueber `director` |
| **OF-10** | Braucht ein **weisser** Slot ein eigenes, hoeheres K? (K=20 behaelt dort nur ~10 % von 205 Kandidaten.) | `performance-tuner` |
| **OF-11** | Wie viele der 309 Kopien haben `OwnedItem.handle is None` und fallen aus dem Kandidatenraum? | `qa-engineer` |
| **OF-16** | Die Spielmessung zu QA-018, die `MULTIPLIERS_FOR[Basis.CANDIDATE]` bestimmt | Nutzer, am laufenden Spiel |
| **OF-18** | Machen die Spaltennamen `Basis.EQUIPPED` / `CANDIDATE` / `BARE` unterscheidbar? | `ui-ux-designer` |
| **OF-21** | Wo gehoert die Formatierung einer **Differenz** je Zielrichtung hin? | `ui-ux-designer` |
| **OF-22** | Bleibt AD-008s zweites Argument (Pruefaequivalenz) nach D3 unberuehrt? | `director` |
| **OF-23** | `GATE_FIELDS["triggerOnWepType"]` beschriftet 72 Effekte falsch | `ui-ux-designer` |
| **OF-27** | Muss eine Zahl in einem Entwurfstext ihre Herkunft mitfuehren? | `director` |
| **OF-28** | Wie gross ist ein Picker-Cache-Eintrag in der Antwortform aus AD-028? | `performance-tuner` |
| **OF-29** | Gehoert eine Randbedingung eines Feldes in den **Typ** statt in den Docstring? | `director` |
| **OF-32** | Frist fuer die Gueltigkeitspruefung des gemerkten Pfades, bevor jemand sie gemessen hat? | `performance-tuner` |

### Beantwortet, Fundstelle belegt — 17

OF-1 (PySide6, nicht Tkinter) · OF-2 (`pytest`, nur Entwicklungs-Abhaengigkeit)
· OF-4 (Gefaess wird **nicht** mitvorgeschlagen) · OF-5 (gekennzeichneter
Rueckfall statt Verweigerung) · OF-6 (`GOAL.md` freigegeben, A1 bis A9
bindend) · OF-7 (309 Relikte gemessen) · OF-8 (kein `defusedxml`,
Groessendeckel) · OF-9 (Deckelwerte direkt in den Auftrag) · OF-12
(Haltezustand gehoert zum Gefaess) · OF-13 (zielfremde Fluechte nennen, nicht
abwerten) · OF-15 (Haltezustand ueberlebt keinen Neustart) · OF-17
(Golden-Datei darf bei W3/W4 neu aufgenommen werden, sobald Pruefpunkt 18
gruen ist) · OF-19 (AK-63 durch AK-162 bis AK-166 ersetzt) · OF-20 (Wortlaut
der konditionalen Zeile in AK-67) · OF-25 (kein GIL-Engpass: 1,9 % Differenz
der Mediane) · OF-26 (Hauptthread-Rest 6,2 bis 8,0 ms von 50 ms) · OF-30
(AK-218 in `UI_SPEC.md` nachgezogen).

### Beantwortet mit benanntem Rest — 1

**OF-31** — der `security-reviewer` hat in T-144 geantwortet, Gesamturteil
CONCERNS. **Offen bleibt daraus:** zwei Wortlautfragen (SEC-027/SEC-028) beim
`director`, und die Neubewertung von SEC-006/SEC-016/017/018 beim Nutzer.

### Unklar — 1

**OF-24** — der Befund "46 von 170" ist sachlich richtiggestellt (Anteil an
der Kandidatenmenge; Statuszeile 4.9b bewegt sich in 175 von 176 Laeufen um
null), aber die Folge fuer Prioritaet oder Reihenfolge hat der `director` nie
beantwortet, und `UI_SPEC.md` fuehrt den Docstring-Widerspruch weiter als
offen. Deshalb weder offen noch beantwortet.

### Nie vergeben — 1

**OF-33** — nur als naechster freier Kreis genannt; `docs/state.md` fuehrt
inzwischen "OF ab OF-34".

### Zwei Lesarten, damit die Zahl nicht wandert

Der Director braucht eine Zahl fuer `docs/state.md`. Es sind zwei moeglich,
und sie meinen Verschiedenes — die Lesart gehoert dazu (L-001):

- **"offen" im engen Sinn: 12.** Nur die Klasse `offen`.
- **"wartende Vorgaenge": 14.** 12 + OF-24 (unklar, der `director` muss
  antworten) + der benannte Rest aus OF-31.

Empfehlung: **14 wartende Vorgaenge nennen, davon 12 als `offen` fuehren** —
weil OF-24 und der OF-31-Rest sonst in keiner Liste stehen und genau so schon
einmal untergegangen sind.

### Wer auf wie viele wartet

| Adressat | Anzahl | welche |
|---|---|---|
| `director` | 4 (+2 aus OF-31, +1 aus OF-24) | OF-22, OF-27, OF-29, OF-24; SEC-027/028 |
| `ui-ux-designer` | 3 | OF-18, OF-21, OF-23 |
| `performance-tuner` | 3 | OF-10, OF-28, OF-32 |
| Nutzer / App Designer | 2 (+1 aus OF-31) | OF-3, OF-16; Neubewertung SEC-006/016/017/018 |
| `qa-engineer` | 1 | OF-11 |

### Was ich in T-183 davon nachgeprueft habe

**13 der 32 Verdikte** erneut gegen die Primaerquelle gehalten, ausgewaehlt
nach Risiko (alle mit Fremddatei-Fundstelle, plus die beiden `offen`, die eine
Abwesenheit behaupten):

- **OF-3** — `qa/findings.md` Z. 127 (QA-105) traegt die Frage, entscheidet
  sie nicht. `offen` haelt.
- **OF-7** — Sache belegt ("Nachmessung OF-7", heute `qa/verlauf.md` Z. 238).
- **OF-10** — drei unabhaengige Muster (`OF-10` woertlich; "hoeheres K";
  Volltext ueber `docs/perf/baselines.md`): **kein** Treffer ausserhalb
  `ARCHITECTURE.md`, Register und Verlauf. Keine Messung. `offen` haelt.
- **OF-11** — zwei Muster (`OF-11`; `handle is None`). Der einzige
  Fremdtreffer, `docs/archiv/berichte/T-041-qa-engineer.md` Z. 412, behandelt
  den **Weg** zu `handle is None`, nicht die **Zahl** der betroffenen Kopien.
  `offen` haelt.
- **OF-12 / OF-13 / OF-15** — `GOAL.md` Z. 113 / 122 / 152, Nutzerwortlaut.
- **OF-17** — "OF-17 entschieden: ja …" woertlich gefunden. `beantwortet`
  haelt.
- **OF-18** — die Fundstelle reicht die Frage an den `ui-ux-designer` weiter,
  entscheidet sie nicht. `offen` haelt.
- **OF-20** — `docs/lessons.md` Z. 417 bis 418 belegt den Abschluss.
- **OF-25 / OF-26** — `docs/perf/baselines.md` Z. 421 (S11-K) und Z. 379
  (S11-J), beide mit Antwortsatz.
- **OF-27** — alle Treffer im Baum zitieren die Frage; in `docs/lessons.md`
  steht keine Regel dieser Art. `offen` haelt.
- **OF-28** — `docs/berichte/T-140-performance-tuner.md` Z. 397: "Ebenfalls
  offen: OF-28". `offen` haelt.
- **OF-30 / OF-32** — T-135 Z. 152 bzw. T-143 Z. 209.

**Kein Verdikt musste geaendert werden.** Die uebrigen 19 stehen so, wie T-182
sie belegt hat; sie sind in T-183 **nicht** erneut gegengelesen.

---

## 3. Die `widerspruechlich`-Faelle bei den AD

**Null.** Keine AD traegt `widerspruechlich`. Das ist kein Ausweichen: die
Spalte "ueberholt durch" haette den Eintrag aufnehmen muessen, und ich habe
die drei Faelle, die danach aussehen, einzeln aufgeloest.

**Fall 1 — AD-028, Nachtrag IX gegen Nachtrag X.** Der schwerste Kandidat:
beide schreiben dieselbe AD fort, und Nachtrag X vergibt ausdruecklich keine
neue Nummer. Geprueft: **IX** zieht AD-028s Punkte 1 bis 4, W3 und die
Schritte U5a/U5b/U6/U7 nach; **X** zieht W1 und den Vertrag des
`AdvisorController` nach. Die beruehrten Stellen sind **disjunkt**, jede
Ueberholung steht als Inline-Klammer an der Stelle selbst. Kein Widerspruch.

> **Aber eine Lesefalle bleibt, und sie ist meine.** Die Ueberschriften
> **X-1** und **X-3** tragen im Titel "(Punkt 1)" und "(Punkt 3)". Das sind
> die **drei vom `developer` in T-131 gemeldeten Punkte**, nicht AD-028s
> Punkte 1 und 3 — belegt am Kopf von Nachtrag X ("Der `developer` hat …
> drei Punkte gemeldet", `ARCHITECTURE.md` Z. 3737) und am Inhalt von X-1
> (`shutdown()`, `worker.py:371-383`). Wer nur die Ueberschrift liest, liest
> einen Widerspruch zur Registerzeile "Punkte 1 bis 4 durch Nachtrag IX", wo
> keiner ist. Das ist genau die Sorte Kollision, die dieser Umbau abstellen
> sollte, und sie steht noch da. Siehe Befund B-5.

**Fall 2 — AD-008, "teilweise" abgeloest.** Als **Cache-Schluessel** abgeloest
(Nachtrag VI), als **Pruefaequivalenz** ausdruecklich **nicht**. Kein
Widerspruch, weil die Trennung an Ort und Stelle steht — **aber die
Nicht-Abloesung ist die Lesart des `architect`, und genau danach fragt OF-22,
das offen ist.** Faellt OF-22 anders aus, wird aus diesem Fall ein echter
Widerspruch und der Pruefumfang fuer A3 ist neu zu bemessen. Das ist die
einzige der 32 AD, deren Status an einer offenen Frage haengt.

**Fall 3 — AD-023 gegen Nachtrag III.** AD-023 sagt woertlich, die
Invarianzaussage aus Nachtrag III sei "an dieser Stelle falsch". Eine
Korrektur mit klarem Vorrang und Datum ist kein Widerspruch, sondern das
Gegenteil davon.

*Zur Abgrenzung:* die drei `widerspruechlich`-Faelle, die der Director aus
`UI_SPEC_REGISTER.md` kennt, stammen aus T-181 und betreffen AK-Nummern. Sie
haben mit diesem Register nichts zu tun.

---

## 4. Warum `ARCHITECTURE.md` von 5972 auf 6129 Zeilen wachsen durfte

**Kurz: ja, es ist billiger — aber nicht aus dem Grund, der die Zahl erklaert,
und die Vermutung des Directors stimmt nur zur Haelfte.**

Das Wachstum sind **+157 Zeilen, +2,6 %**, und es ist restlos Navigation: alle
104 neu hinzugekommenen verschiedenen Zeilen sind Wegweiser (Abschnitt 1b).
Wer Lesekosten an der Dateilaenge misst, misst die falsche Groesse — die
richtige ist **der Weg zu einer Antwort**.

**Diesen Weg habe ich gemessen.** Grundgesamtheit: die **16** AD, fuer die das
Register eine nachziehende Fundstelle mit Zeilennummer nennt (Vollerhebung,
keine Stichprobe, kein Stichprobenfehler; Zeilennummern exakt). Gemessen wird
der Abstand in Zeilen zwischen der Urfassung einer AD und der Stelle, die sie
zuletzt nachzieht — alt gegen `de710a5`, neu gegen `9098229`. Rezept und
Skript: `…/scratchpad/T-183/abstand.py`, Formel
`Abstand = |Zeile(Nachzug) − Zeile(Urfassung)|`.

| | alt | neu | |
|---|---|---|---|
| **Median** | **2494 Zeilen** | **325 Zeilen** | Faktor **7,7** |
| Summe ueber 16 Faelle | 35 906 | 9 561 | Faktor 3,8 |
| Faelle ueber 1000 Zeilen | 15 von 16 | **4 von 16** | |
| schlechter geworden | — | **1** (AD-014 ← AD-017: 284 → 317) | |

Groesste Einzelgewinne: AD-002 ← AD-021 **1643 → 45** · AD-015 ←
Korrekturnotiz **2485 → 66** · AD-003 ← Korrekturnotiz **3502 → 100** ·
AD-009 ← Praezisierung D4 **2503 → 75** · AD-016 **1876 → 53**.

**Zur Vermutung des Directors, Teil 1 (das Register): bestaetigt, und es ist
die groessere Haelfte.** Die Frage "welche Fassung gilt, und ist diese OF noch
offen?" hatte im ganzen Projekt **keine** Antwortstelle; man rekonstruierte
sie aus 5972 Zeilen. Sie steht jetzt in **154** Zeilen, eine Zeile je Nummer.
Das ist keine Umstellung, das ist eine Information, die es vorher nicht gab.

**Zur Vermutung des Directors, Teil 2 (die geltende Fassung steht jetzt neben
ihrem Ausgangswortlaut): richtig im Mechanismus, aber schwaecher als sie
klingt. Drei Einschraenkungen, die ich nennen muss, statt zu nicken:**

1. **Der Nachtragstext wurde nicht gekuerzt, nur bewegt.** Wer AD-028 wirklich
   liest, liest dieselben rund 975 Zeilen wie vorher. Gespart wird **Suche**
   und **die Entscheidung, welcher Nachtrag gewinnt** — nicht Lesemenge. Der
   Gewinn heisst nicht "weniger lesen", sondern "nicht mehr selbst entscheiden
   muessen".
2. **Beim Beispiel AD-028 trifft die Praemisse nicht zu.** Die Nachtraege
   VIII, IX und X standen im Altstand bereits **unmittelbar hintereinander**
   (Z. 3962–4474, 4475–4959, 4960–5369) — sie waren nie "elf Nachtraege weit"
   auseinander. Repariert wurde dort etwas anderes: AD-029 (262 Zeilen) sass
   **zwischen** AD-028 und seinen beiden Nachtraegen und steht jetzt dahinter.
   Die dramatischen Abstandsgewinne liegen woanders — bei thematisch
   verwandten AD, die chronologisch Tausende Zeilen auseinanderlagen.
3. **Vier von 16 Faellen bleiben ueber 1000 Zeilen**, weil die Nachziehung
   einen Themenbereich kreuzt: AD-013 ← AD-030 **3085** (B gegen E) · AD-007 ←
   Praezisierung AD-016 **1389** (D gegen B) · AD-018 ← AD-028 **1289** (B
   gegen D) · AD-006 ← AD-029 **1117**. Die thematische Ordnung **kann**
   bereichsuebergreifende Nachziehungen nicht aufloesen; nur das Register kann
   das, und dort tut es das auch.

**Was die Vermutung nicht nennt und was der Preis ist:** der Gesamtbestand ist
von **5972** auf **12 420** Zeilen ueber drei Dateien gewachsen (Faktor
**2,08**), weil der Verlauf eine **vollstaendige Kopie** ist. Das ist gewollt
— ein eingefrorenes Archiv — aber es kostet zweierlei. Erstens stehen ab jetzt
zwei Fassungen desselben Wortlauts im Repository, und **kein Waechter haelt
den Verlauf eingefroren**; heute traegt das nur eine Zusage im Text. Zweitens
loesen sich die Zeilennummern des Registers **nur im Archiv** auf, nicht in
der Datei, die die geltende Fassung haelt: das Register sagt "Hier faengt man
an", sein Schnellzugriff fuehrt aber in den Verlauf. Das Register weist selbst
darauf hin ("massgeblich ist immer die genannte Abschnittsueberschrift") —
gemildert, nicht sauber.

**Urteil in einem Satz:** Die 157 Zeilen sind ein guter Kauf, aber sie sind
nicht der Gewinn; der Gewinn ist das Register und der Fall der Suchdistanz von
median 2494 auf 325 Zeilen — die 157 Zeilen kaufen nur die Orientierung, die
einen Erstleser ueberhaupt zum Register schickt.

---

## 5. Nebenbefund: AD-027 und OF-14 wurden nie vergeben

Beides bestaetigt, beides mit zwei unabhaengig formulierten Mustern ueber den
ganzen Baum geprueft (woertlich sowie tolerant `AD[^a-z0-9]{0,3}0?27\b` bzw.
`OF[^a-z0-9]{0,3}14\b`), zusaetzlich gegen eine sortierte Liste **aller** AD-
und OF-Nummern des Baums gegengelesen.

**AD-027 — nie vergeben, aber der Befund ist nicht neu.** Zwoelf Treffer in
zehn Dateien; **jeder einzelne ist eine Buchfuehrungsnotiz ueber die Luecke,
keiner vergibt die Nummer.** Gefunden hat es nicht T-182, sondern **T-122**
(`docs/archiv/berichte/T-122-architect.md` Z. 157: "AD-027 existiert nicht.",
Volltextsuche ueber das ganze Repository) — und seither tragen es T-125,
T-134, T-143 und deren Auftragsdateien weiter. **Der Director sollte es in
`docs/state.md` als Wiederbestaetigung eintragen, nicht als Entdeckung.** Dass
dieselbe Feststellung in vier Zyklen vier Mal neu getroffen wurde und trotzdem
nie in `docs/state.md` stand, ist der eigentliche Befund daran.

**OF-14 — nie vergeben, und dieser Teil ist neu.** Vor T-182 kommt die Nummer
im ganzen Baum **nirgends** vor. Die einzigen heutigen Treffer sind die
Buchfuehrungszeilen, die T-182 selbst geschrieben hat (`ARCHITECTURE.md`
Z. 42, `ARCHITECTURE_REGISTER.md` Z. 128 und 130), plus `docs/tasks/T-183.md`.
Der OF-Kreis springt von OF-13 auf OF-15 — eine Luecke, kein verlorener
Vorgang.

**Folge fuer die Nummernkreise:** `docs/state.md` fuehrt "AD ab AD-033" und
"OF ab OF-34". Beides bleibt richtig. **AD-027 und OF-14 duerfen nicht
nachbelegt werden** — sonst zeigen zehn bzw. drei bestehende Notizen auf etwas
anderes, als sie behaupten.

---

## 6. Befunde

*Ohne Nummern — Befund-IDs vergibt der `director`.*

**B-1 · Vier Fundstellen des Registers zeigen seit heute ins Leere, und das
Problem ist viel groesser als mein Register.**
T-180 hat waehrend dieses Laufs `qa/findings.md` von **2754 auf 243** Zeilen
und `security/findings.md` von **595 auf 53** Zeilen gekuerzt und den Rest
nach `qa/verlauf.md` (2680) und `security/verlauf.md` ausgelagert — **alles
noch nicht committet**. Betroffen im Register: OF-7 (`qa/findings.md` Z. 153 →
`qa/verlauf.md` Z. 238), OF-17 (Z. 794 → Z. 819), OF-18 (Z. 804 → Z. 829),
OF-31 (`security/findings.md` Z. 473 → `security/verlauf.md`).
**Alle vier waren an `e06386c` exakt richtig** — einzeln nachgewiesen ueber
`git show e06386c:qa/findings.md` an den genannten Zeilen. Kein Sachverhalt
aendert sich, nur der Zeiger.
**Die Bauform ist ausgezaehlt, bevor sie beschrieben wird:** im ganzen Baum
stehen **32** Verweise auf `qa/findings.md` oder `security/findings.md` **mit
Zeilennummer**; **26 davon zeigen nach dem Split hinter das Dateiende.** Nur
vier gehoeren mir. Betroffen sind unter anderem `docs/lessons.md`,
`docs/berichte/T-143`, `T-144`, `T-145`, `docs/archiv/ui-spec-verlauf.md` und
`UI_SPEC_REGISTER.md` aus T-181. **Das ist eine Aufraeumaktion fuer den
`director`, kein Fix fuer mich** — und sie kann erst erteilt werden, wenn
T-180 committet ist, weil die Zielzeilen sonst nicht verbindlich sind.

**B-2 · `ARCHITECTURE_REGISTER.md` Z. 59 behauptet zu viel (meine Arbeit).**
Der Satz "Die Nummer existiert in keiner Datei des Arbeitsbaums" ist zu stark:
AD-027 kommt in **zehn** Dateien vor, ueberall als Notiz ueber die Luecke.
Richtig waere "wird in keiner Datei als Entscheidung vergeben". Die Sache
stimmt, der Satz nicht — und er ist genau die Bauform, vor der der Rahmen bei
Abwesenheits-Behauptungen warnt.

**B-3 · `ARCHITECTURE_REGISTER.md` Z. 128 bis 132 ist durch sein eigenes
Schreiben falsch geworden (meine Arbeit).** Dort steht, eine Volltextsuche
nach OF-14 ergebe "0 Treffer". Das war richtig, als es entstand; heute sind es
**drei** — und alle drei stammen aus diesem Umbau. Eine selbstbezuegliche
Abwesenheitsaussage muss ihren eigenen Text ausnehmen, sonst ist sie ab dem
Moment des Schreibens falsch.

**B-4 · `ARCHITECTURE.md` Z. 37 bis 39 benutzt das falsche Wort (meine
Arbeit).** Die Aufteilung ist dort "Partition (jede Quellzeile genau einmal,
keine doppelt, keine fehlend)" genannt. Es ist **keine Partition, sondern eine
Ueberdeckung**: der Verlauf traegt alle 5972 Zeilen, `ARCHITECTURE.md` traegt
denselben Inhalt noch einmal, umgestellt. Die tragende Aussage davor ("Nichts
ist gestrichen") stimmt und ist jetzt bytegleich belegt (Abschnitt 1a) — nur
die Begruendung in Klammern beschreibt eine Rechnung, die so nicht gefuehrt
wurde.

**B-5 · Ueberschriften-Kollision in Nachtrag X (meine Arbeit, nicht ohne
Wortlautaenderung behebbar).** "(Punkt 1)" / "(Punkt 3)" in X-1 und X-3 meinen
die drei Meldepunkte des `developer`, nicht AD-028s Punkte 1 bis 7. Siehe
Abschnitt 3, Fall 1. Eine Behebung aendert den Wortlaut eines Nachtrags und
war deshalb ausdruecklich weder Teil von T-182 noch von T-183.

**B-6 · Der W-Kreis kollidiert seit dem 08.09.2026 und faellt durch jedes
Register (Bestand, nicht meine Arbeit).** `W6` bezeichnet in dieser Datei zwei
verschiedene Dinge: die Fassaden-Kette aus AD-019 (`W0` bis `W6`) und die
Waechter der Picker-Spur (`W1` bis `W7`, inzwischen `W8`). Nachtrag X nennt
das selbst, schlaegt ein Praefix (`AW-1`) vor und legt die Entscheidung
ausdruecklich beim `director` — sie ist seit vier Tagen nicht getroffen.
**Das Register fuehrt sie nicht, weil sie weder AD- noch OF-Nummer hat**, und
sie faellt damit beim naechsten Zyklus wieder heraus. Vorschlag: OF-Nummer
vergeben oder als Befund fuehren.

**B-7 · Der Verlauf-Kopf nennt seine eigene Laenge nicht.** Er sagt, die
Zeilennummern laegen "um die Laenge dieses Kopfes hoeher". Die Laenge ist
**165**. Wer umrechnen will, muss nachzaehlen. Eine Zahl im Kopf waere billiger
als jede Erklaerung daneben.

---

## 7. Offene Fragen an den `director`

1. **Welche OF-Zahl kommt in `docs/state.md`** — 12 (`offen` im engen Sinn)
   oder 14 (wartende Vorgaenge inkl. OF-24 und des OF-31-Rests)? Empfehlung:
   **14 nennen, 12 als `offen` fuehren.** Ohne genannte Lesart wandert die
   Zahl.
2. **Wann wird B-1 erteilt?** Die 26 toten Verweise koennen erst nachgezogen
   werden, wenn T-180 committet ist. Vor oder nach der Baurunde?
3. **B-6, der W-Kreis:** eigene Nummer oder weiter ohne? Ohne Nummer steht sie
   in keinem Register.
4. **Soll der Verlauf gegen Aenderung gesichert werden?** Ein Waechter, der
   die Pruefsumme des Verlauf-Rumpfs (ab Zeile 166) gegen
   `8f34c8bce819c004bd154e28a48e169c` haelt, waere wenige Zeilen gross und
   macht aus der Textzusage eine gepruefte Eigenschaft. Der Gegenbau ist
   trivial herstellbar (eine Zeile im Verlauf aendern) und wuerde im
   Standardlauf rot. Auftrag fuer `qa-engineer` oder `developer`, nicht fuer
   mich.

---

## 8. Was ich nicht geprueft habe

- **19 der 32 OF-Verdikte** habe ich in T-183 nicht erneut gegen die
  Primaerquelle gehalten. Sie stehen so, wie T-182 sie belegt hat.
- **Kein Abgleich der Entscheidungen gegen den Code.** Ob AD-028 den heute
  gebauten `AdvisorController` beschreibt, sagt dieser Bericht nicht — das ist
  A9 und gehoert dem `qa-engineer`.
- **`UI_SPEC.md` und `UI_SPEC_REGISTER.md`:** nicht angefasst und nicht
  beurteilt; T-181 und T-184 gehoeren dort hin. Die Aussage zu
  `UI_SPEC_REGISTER.md` in B-1 stammt aus der Bauform-Auszaehlung, nicht aus
  einer Durchsicht dieser Datei.
- **Kein Programmstart, kein Bau, keine Suite.** So beauftragt.
- **Nichts geaendert, nichts committet.** Auch nicht die vier Befunde an
  meiner eigenen Arbeit (B-2 bis B-5) — sie sind laut Auftrag zu melden, nicht
  zu beheben.
