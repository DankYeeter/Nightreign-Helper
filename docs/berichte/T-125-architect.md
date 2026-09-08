# T-125 — AD-028 nachgezogen: die Entprellung hat nichts zu entprellen (architect)

STATUS: erledigt
AUFTRAG: T-125 — Drei Punkte an AD-028 nachziehen, die der `ui-ux-designer` in T-124 aufgedeckt hat (`docs/tasks/T-125.md`)
GELESEN: `docs/tasks/T-125.md` · `CLAUDE.md` · `GOAL.md` (A6 woertlich, A7, A12, Nicht-Ziele) · `docs/state.md` (Kopf, Nummernkreise Zeile 10-12) · `docs/berichte/T-124-ui-ux-designer.md` (vollstaendig) · `UI_SPEC.md` Zeile 827-855 (Korrekturkasten an §3.8) und Zeile 5886-6185 (der neue Abschnitt, AK-197 bis AK-210) · `ARCHITECTURE.md` Nachtrag VIII ganz (AD-028, AD-029, U1–U8, Risiken, „Bewusst nicht getan", OF-25 bis OF-27) · `docs/perf/baselines.md` S11-B, S11-C, S11-D, S11-F, S11-G · `docs/berichte/T-118-performance-tuner.md` Abschnitt 3.2 (Cache-Groesse und die sieben Bedienspuren) · **Quellstand lesend:** `nrplanner/relicpicker.py`, `nrplanner/advisorbar.py`, `nrplanner/advisor/candidates.py`, `nrplanner/advisor/worker.py`, `nrplanner/advisor/run.py`, `nrplanner/advisor/types.py`, `nrplanner/advisor/goals.py` · eigene Rollennotizen unter `.claude/agent-memory/architect/`
GEÄNDERT: `ARCHITECTURE.md` (AD-028: Lesehinweis unter der Ueberschrift, vier Nachtragsklammern an den Punkten 1–4, eine an W3, ein Ueberholt-Kasten ueber der U-Tabelle aus Nachtrag VIII; **neu angehaengt: Nachtrag IX** mit IX-0 bis IX-5, Umsetzung Fassung 2 von U5a–U7, Risiken, „Bewusst nicht getan", OF-28/OF-29) · `docs/berichte/T-125-architect.md` (diese Datei) · `.claude/agent-memory/architect/` (eigene Rollennotiz fortgeschrieben). **Nichts committet, nichts gestaged.** `git status` zeigt ausserdem `UI_SPEC.md` (T-124) und `docs/state.md` (Director) als geaendert — **beide nicht von mir**, ich habe `UI_SPEC.md` nur gelesen und `docs/state.md` nur gelesen.
ANNAHMEN: (1) Alle Aussagen ueber den Quellstand sind **gelesen, nicht am laufenden Programm bestaetigt** — ich habe nichts gestartet und nichts gemessen, wie der Auftrag es vorgibt. (2) Die Trefferquoten aus T-118 Abschnitt 3.2 stammen aus Bedienspuren, deren Schluesselfolgen ich nicht vor mir habe; dass die Spur „Level-Schieber weit 15-5-15" richtungsbehaftete Schluessel enthaelt, weiss ich **nicht** — deshalb bleibt die 64 stehen und wird nicht gesenkt. (3) Dass ein `SlotPool` mit 206 Kandidaten mehr Speicher braucht als eine `AdvisorResult` mit 20 Suggestions, ist plausibel, aber **nicht gemessen**; ich nenne deshalb eine Schranke und keine Zahl.
NÄCHSTER: `director` — dann `developer` (U5a, haengt an nichts; danach U5b in der Fassung 2 aus Nachtrag IX)
BLOCKIERT DURCH: nichts.

---

## 1. Der Entwurf in fuenf Zeilen

Der Befund des `ui-ux-designer` **haelt** — der Zielrichtungswechsel im
offenen Dialog braucht keine Rechnung, und er traegt weiter, als T-124 gesehen
hat: nicht nur `_sort_chosen` ist Verschwendung, sondern auch die Haelfte des
Picker-Cache-Schluessels. AD-028 bleibt in der Sache unveraendert (zweite
Instanz derselben Klasse, Option D); vier ihrer sieben verbindlichen Punkte
sind nachgezogen. Die Picker-Spur bekommt **0 ms** Entprellung statt 100 ms,
beantwortet eine bereits bekannte Frage **sofort** statt ueber den Zeitgeber
und fragt unter einer **kanonischen** Zielrichtung, damit ein Pool beide
Richtungen bedient. **Vorwaermen ist entschieden abgelehnt** und geht als
Backlog-Vorschlag zurueck an den `director`. Die Cache-Groesse 64 bleibt
stehen, ihre Herleitung deckt die neue Antwortform aber nicht — U7 misst nach.

## 2. Die Nachpruefung des tragenden Befunds

**Er haelt.** Fundstellen in `ARCHITECTURE.md` Nachtrag IX-0, Tabelle. Kurz:
`SlotAdvice.ranking` uebergibt `advisor_goals.GOALS` — die **ganze** Registry
— an `candidates.pool` (`relicpicker.py:325-327`); `pool` baut `marginals` je
Kandidat ueber alle Ziele (`316-320`), `baseline` ueber alle
(`328-330`), und `candidates` ungekuerzt (`331`). `rank_by` wirkt **nur** auf
`measured.sort(...)` (`323`) und auf das gleichnamige Feld (`327`). Der
Grundzustand haengt am Slot (`base_state_for`, `61-79`), `ctx` traegt keine
Richtung, der Dialog ist modal (`setModal(True)`), und `_in_the_chosen_order`
(`1019-1060`) liest beide Richtungen ohnehin schon selbst nach
(`top_handles(other_id)`, Zeile 1054).

**Zwei Dinge, die T-124 nicht genannt hat und die zum Befund gehoeren:**

1. **Die Randbedingung.** Der Schluss traegt nur, solange
   `advisorbar.GOAL_ORDER` (was der Picker zeichnet, Zeile 67) eine Teilmenge
   der Schluessel von `advisor.goals.GOALS` (was gerechnet wird,
   `goals.py:302-305`) ist. Das sind **zwei getrennt geschriebene Stellen**,
   die heute uebereinstimmen und auseinanderlaufen koennen. Dafuer gibt es
   jetzt den Waechter **W4**.
2. **Der Cache-Schluessel ist nicht richtungsfrei, die Antwort schon.**
   `run.cache_key` nimmt jedes Feld ausser `generation` (`run.py:170-180`),
   also auch `goal_id`. Derselbe Slot unter der anderen Richtung ist ein
   anderer Schluessel — dieselben 318 ms noch einmal, nur ueber
   Dialoggrenzen hinweg statt innerhalb einer Oeffnung. **Gemessen ist das
   schon:** T-118 Abschnitt 3.2, Spur „Zielrichtung umschalten", 8 Fragen, 2
   verschieden, 75 % Treffer — diese Spur besteht ausschliesslich aus dieser
   Doppelung.

**Was am Befund nicht haelt:** `candidates.pools()` ist **nicht** das Mittel
zum Vorwaermen (siehe Punkt 4 unten).

## 3. Die drei Punkte des Auftrags, beantwortet

**Punkt 1 — die Entprellung.** *Sie faellt fuer die Picker-Spur auf 0 ms.*
Die 100 ms stammen aus AD-006.5 und wurden fuer Tastendruecke und einen
gezogenen Schieber gesetzt; ihre Randbedingung („zwischen zwei Fragen liegt
weniger als eine Ueberlegung") trifft auf eine modale Oeffnung mit **einer**
Frage nicht zu. Kosten der Konstante, gerechnet aus S11-C: 318,1 → 418,1 ms
am teuersten Slot (24 % des Wartens), 32,3 → 132,3 ms am billigsten (76 %),
und ein Cache-Treffer von 0 auf 100 ms (100 %). Gegen A6s 500-ms-Median
schrumpft der Abstand von 36 % auf 16 %, **bevor** der nie gemessene
Hauptthread-Rest (OF-26) dazukommt.

**Der schaerfere Teil, den erst die Nachpruefung gezeigt hat:** der
Controller sieht im Cache erst **nach** dem Zeitgeber nach
(`worker.py:213` gegen `290-293`). Damit kann eine bekannte Antwort nie beim
Bau des Rasters vorliegen — und `UI_SPEC` §2 sieht genau das vor
(*„Liegt die Antwort schon beim Bau des Rasters vor (Cache-Treffer), wird der
Wartezustand nicht betreten"*). **Dieser Satz der Spec ist mit dem heutigen
Kontrollfluss nicht baubar.** Deshalb bekommt der Controller **eine**
zusaetzliche Methode, die eine bekannte Antwort im selben Aufruf zurueckgibt
(kein Signal, kein Timer, kein zweiter Antwortweg fuer die Advisor bar — die
ruft weiter `ask`). Die 100 ms werden **nicht geloescht**, sondern mit ihrer
Wiederkehrbedingung aufgeschrieben: sie kommen zurueck, sobald die Picker-Spur
mehr als eine Frage je Oeffnung stellen kann — also genau mit dem Rueckweg aus
`UI_SPEC` §4.

**Punkt 2 — Vorwaermen: Backlog-Vorschlag, weder Ersatz noch Zusatz.** Vier
Gruende, der erste korrigiert die Frage:
1. **`candidates.pools()` rechnet etwas anderes.** Es liefert einen Pool je
   **freiem** Slot, jeweils gegen einen Grundzustand, in dem **die uebrigen
   freien Slots leer sind** (`base_state_for`, Docstring: *„For a slot that is
   already free this is `problem` unchanged, which is the Optimize case"*).
   Die Picker-Frage ist die umgekehrte — jeder Slot ausser dem geoeffneten ist
   **gehalten** (AD-018.1, `relicpicker.py:318-322`). In dieser Form ist
   `free_slots(problem)` leer und `pools()` gaebe `()` zurueck. Vorwaermen
   heisst also **sechs einzelne `pool`-Aufrufe**.
2. **Preis: 610,7 ms** (S11-C, Summe aller sechs Slots) je Buildzustand, gegen
   einen Gewinn von hoechstens 318,1 ms **einmal** — der Spieler oeffnet einen
   Slot, nicht sechs. Der Vorrat verfaellt bei jeder Aenderung an Build,
   Level, Waffe, Nightfarer oder Haltezustand; die Spur „Level-Schieber weit
   15-5-15" zaehlt 126 Fragen ueber 66 Zustaende.
3. **Es waere eine dritte rechnende Spur, bevor die zweite gemessen ist**
   (OF-25 offen, `Optimize` bei 5023,6 ms gegen 6 s = 19 % Luft).
4. **Ein warmer Vorrat verdraengt kalte Treffer** aus demselben LRU, an dem
   die gemessenen 30 % haengen.
Und es ist nicht noetig: mit Punkt 1 liegt der teuerste Slot bei 318,1 ms
gegen A6s 500 ms. *Wieder interessant, wenn* U7 den Hauptthread-Rest (OF-26)
oder die Ueberlappung (OF-25) so misst, dass eine Slot-Frage im Median ueber
500 ms liegt — die dann billigere Form ist **ein** `pool`-Aufruf fuer den
zuletzt offenen Slot, nicht `pools()`.

**Punkt 3 — AD-028 Punkt 4.** Der erste der beiden Faelle (`1169-1171`
rechnet beim Richtungswechsel neu) **entfaellt ersatzlos**; der zweite bleibt;
**ein dritter kommt hinzu**, den bisher niemand aufgeschrieben hatte: zwei
Oeffnungen hintereinander an **einer** Spur (Slot A geoeffnet und geschlossen,
Slot B geoeffnet, As Antwort trifft in Bs Dialog ein — dieselben Karten,
plausible Zahlen, kein sichtbarer Fehler). Der Zaehler bleibt noetig, die
Entscheidung kippt nicht. Der alte Wortlaut steht weiter da, mit einer
Nachtragsklammer und dem Grund.

## 4. Der Nebenbefund, der den Auftrag ueberschreitet — und den ich nicht entscheide

**Die 64 des Picker-Caches steht auf einer Messung an einer anderen
Antwortform.** Die **33,4 KiB** aus S11-F sind an einer `AdvisorResult` mit
**20 Suggestions** gemessen; AD-028 gibt der Picker-Spur aber den **ganzen
`SlotPool` mit 206 Kandidaten** als Antwort, und eine `AdvisorResult` traegt
den Pool nicht (`types.py:604-649`). Zweitens stammen die Trefferquoten aus
Spuren, in denen jeder Slot **zweimal** vorkommt, einmal je Richtung — nach
IX-2 gibt es diese Doppelung nicht mehr.

**Ich aendere die Zahl nicht** (Vorgabe: fehlt eine Messung, wird nicht
entschieden). Stattdessen: U7 misst die Eintragsgroesse in der neuen
Antwortform, und es gibt eine Rueckfallschranke mit Rezept — die 64 wurde auf
`64 x 33,4 KiB = 2,09 MiB` beschlossen (4,4 % von 47,7 MiB Grundverbrauch);
der Wert, den AD-028 selbst „nicht billig" nennt, ist 8,75 MiB; daraus
`8,75 MiB / 64 = 140 KiB` je Eintrag. **Ueber 140 KiB faellt die Spur auf 32
zurueck und die Frage kommt zu mir.** Das ist **OF-28**.

## 5. Umsetzungsschritte, direkt als Auftraege verwendbar

Die Fassung 2 der Tabelle steht in `ARCHITECTURE.md`, Nachtrag IX,
„Umsetzung". U1 bis U3 und U8 gelten unveraendert, **U4 ist erledigt**.

1. **U5a (`developer`, haengt an nichts)** — Qt-freie Seite: die Pool-Funktion
   in `advisor/run.py`, kanonische Form nach AD-028.3, `rank_by` aus
   `request.goal_id`, **die benannte Konstante fuer die kanonische
   Zielrichtung entsteht hier** (IX-2.1), `SlotPool`-Gleichheit vorher/nachher
   ueber Handles und Punktzahlen belegt.
2. **U5b (`developer`, haengt an U5a)** — Verdrahtung: Antwortfunktion am
   Controller, zweite Instanz am Fenster mit **0 ms** und Cache 64, die
   zusaetzliche „antworte sofort, falls bekannt"-Methode samt gemeinsamer
   privater Frageerzeugung, `SlotAdvice` fragt die Spur, **`_sort_chosen`
   fragt nicht mehr**, die Anzeige liest ihre Richtung aus der Einstellung
   statt aus `SlotPool.rank_by` (AK-205), `before_the_data_changes`/`shutdown`
   an **beide** Spuren, Docstring `relicpicker.py:276-281` ersetzt (dritte
   Fundstelle der widerlegten ~51 ms, OF-27), direkte `advisor`-Importe aus
   `relicpicker` entfernt.
3. **U6 (`developer`, haengt an U5b)** — W1, W2, **W3 in der neuen Fassung**,
   **W4** (`GOAL_ORDER` ⊆ `GOALS`), **W5** (bekannte Antwort → genau ein
   Rasterbau, mit Gegenprobe), je mit toetender Mutation, alle im
   Standardlauf, keine Wanduhr.
4. **U7 (`performance-tuner`, haengt an U5b)** — 318,1 ms nachmessen;
   **Eintragsgroesse in der neuen Antwortform gegen die 140-KiB-Schranke**;
   **Trefferquote der beiden tragenden Spuren unter dem Schluessel ohne
   Richtung**; Hauptthread-Rest (OF-26); Ueberlappung zweier Spuren (OF-25).

## 6. Was der `developer` ausdruecklich **nicht** tun soll

- Die Entprellung **nicht an der Klasse** aendern — die 0 ms gehoeren der
  Instanz, die Advisor bar behaelt 250 ms.
- Den Cache **nicht generell vor den Zeitgeber ziehen** — das aendert die
  Advisor bar mit und bringt das Flackern zurueck, gegen das AD-006.5 gebaut
  ist.
- Den Rueckweg aus `UI_SPEC` §4 **nicht stillschweigend bauen**. Bedient ein
  Pool die andere Richtung wider Erwarten nicht, ist das ein **Befund**
  (L-008c): melden — dann bekommt der Richtungswechsel seinen Wartezustand
  **und** die 100 ms kommen zurueck.
- **Nicht vorwaermen**, auch nicht „nur den einen Slot".
- **`AdvisorResult` nicht um den Pool erweitern**, um beiden Spuren dieselbe
  Antwortform zu geben — das machte jeden Gesamtlauf-Eintrag um die
  Kandidatenliste schwerer, gegen 279,9 KiB, die schon der teure Fall sind.
- Zusaetzlich gilt die Liste aus Nachtrag VIII unveraendert (kein zweiter
  Zaehler, kein zweiter Thread-Weg, keine Zeitschranke in der Suite, SEC-022
  nicht anfassen, `load()` nicht frueher abbrechen).

## 7. Widersprueche zur `UI_SPEC` — **keine**

Ich habe jeden meiner Punkte gegen AK-197 bis AK-210 geprueft. **Kein
Widerspruch.** Zwei Beruehrungen, die der `director` kennen sollte:

- **AK-197/§2, Cache-Treffer.** Die Spec sieht den einzelnen Anstrich bei
  bekannter Antwort vor. Ohne IX-1.3 waere dieser Satz **unbaubar** gewesen —
  meine Entscheidung loest ihn ein, sie widerspricht ihm nicht.
- **AK-205.** Meine Entscheidung IX-2 macht AK-205 von „gut" zu
  „unverzichtbar": wer die Richtung weiter aus `SlotPool.rank_by` liest, zeigt
  danach **immer** die kanonische Richtung an statt nur manchmal. Das ist
  gewollt — ein Fehler, der immer auftritt, wird gefunden.

## 8. Offene Fragen

- **OF-28 — an den `director`, auszufuehren vom `performance-tuner` (U7).**
  Die Groesse eines Picker-Cache-Eintrags in der Antwortform, die AD-028 ihm
  gibt, ist nie gemessen worden. Schranke und Rueckweg stehen in IX-3.2.
  **Solange die Messung fehlt, ist die 64 gesetzt, aber nicht hergeleitet.**
- **OF-29 — an den `director`.** Nach IX-2 traegt die Picker-Anfrage in
  `goal_id` eine Ordnungskonstante statt der Wahl des Spielers — die zweite
  Stelle in diesem Vorhaben, an der ein Feldname mehr verspricht, als das Feld
  haelt (die erste war `SlotPool.rank_by`, D-4/T-077). Ob eine solche
  Randbedingung kuenftig im Typ stehen muss statt im Docstring daneben, ist
  eine Regelfrage und gehoert zu OF-27.
- **Buchfuehrung, die der `director` nachziehen muss** (`docs/state.md`
  gehoert mir nicht): **AK ab AK-211** — Zeile 11 steht noch auf AK-195,
  T-124 hat es bereits gemeldet, es ist bis jetzt nicht nachgezogen (geprueft
  am heutigen Stand der Datei). **OF ab OF-30.** **AD bleibt bei AD-030** —
  dieser Nachtrag vergibt keine neue AD-Nummer; AD-027 bleibt die Luecke, die
  sie ist.
- **Fuer den Backlog** (`docs/plan-restarbeiten.md` gehoert mir nicht):
  „Slot-Pools vorwaermen" mit der Bedingung aus IX-5.

## 9. Was ich **nicht** getan habe, und was nicht verifiziert ist

- **Keine Zeile Anwendungscode, kein Test, kein UI-Entwurf.** Geaendert wurde
  ausschliesslich `ARCHITECTURE.md` und diese Berichtsdatei.
  `UI_SPEC.md`, `tests/`, `GOAL.md`, `docs/state.md`, `qa/findings.md`,
  `docs/tasks/`, `docs/perf/` sind **unberuehrt** (nur gelesen).
- **Nichts committet, nichts gestaged.**
- **Das Programm nicht gestartet, nichts gemessen, keinen Bildnachweis
  erzeugt.** Damit war keine Umlenkung der drei Datenverzeichnisse noetig; es
  wurde kein Prozess gestartet, es ist nichts aufzuraeumen. Der Spielstand
  wurde nicht angefasst.
- **Die Suite ist nicht gelaufen** — ich habe keinen Code angefasst. Die Zahl
  aus `docs/state.md` (1257 passed, 9 skipped) gilt unveraendert.
- **Alle Quelltextaussagen sind gelesen, nicht am laufenden Fenster
  bestaetigt.** Die drei, an denen am meisten haengt — dass der Picker die
  ganze Registry uebergibt, dass der Cache erst hinter dem Zeitgeber gelesen
  wird, und dass `pools()` fuer die Picker-Form leer ausgeht — stehen je an
  einer benannten Zeile und sind vom `developer` in U5a/U5b ohnehin zu
  beruehren.
- **Nicht geprueft:** ob die Spur „Level-Schieber weit 15-5-15" aus T-118
  richtungsbehaftete Schluessel enthaelt. Genau daran haengt, ob die 64 nach
  IX-2 noch der Knick ist — deshalb geht die Frage als Messauflage an U7 und
  nicht als Entscheidung von mir.
- **Scratchpad:** `…/scratchpad/T-125/nachtrag-ix.md` (der angehaengte
  Abschnitt als Zwischendatei). Nichts ausserhalb von `T-125/` angefasst.
