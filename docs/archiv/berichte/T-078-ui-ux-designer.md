# T-078 — ui-ux-designer (Modus Spec)

```
STATUS: erledigt
AUFTRAG: T-078 — Die Sprache des Beraters (Spec)
GELESEN: docs/tasks/T-078.md (mit dem Zitat von GOAL A5/A12 und dem
         Stand-Auszug aus docs/state.md, beide tragen den Auftrag) ·
         docs/berichte/T-067-developer.md (vollstaendig; tragend sind
         Abschnitt 2, 5.3, 6 D-3, 7 D-2/D-10/D-11, 9, 10) · UI_SPEC.md
         (T-004 §3.1-3.5, Zustandstabelle 4.1-4.14, §5, AK-01 bis AK-30;
         T-024 §3.3, §3.4, §3.6, §3.7, §4.1-4.4, §5.1-5.4, §6 Token;
         Nachtrag zu QA-119; Nachtrag zu OF-20/QA-108/QA-113 mit AK-67;
         T-056 §1.2-1.5 mit AK-69 bis AK-73; T-074 §7 mit AK-127) ·
         ARCHITECTURE.md (AD-025 Nachtrag VI vollstaendig, darin 25.1-25.6,
         die Ergebnisform des SlotPool und die Praezisierung AD-004) ·
         GOAL.md (A5, A7, A8, A11-A14, F3, F4, OF-13) ·
         nrplanner/advisor/explain.py (ganz), types.py (Candidate, SlotPool,
         Suggestion, AdvisorResult), goals.py (die beiden scope-Tupel) ·
         nrplanner/model.py (Build, Situational, compute_qualitative,
         label_for, is_better_lower) · nrplanner/app.py (Zeilen 664-742 und
         2951-3029: Aufzaehlungszeichen, CURSE, Zahlenformat) ·
         DESIGN_REVIEW.md (Suche nach Berater-Befunden; keiner widerspricht) ·
         CLAUDE.md
GEAENDERT: UI_SPEC.md (ein neuer ##-Abschnitt am Ende, Zeilen 3151-3727) ·
           docs/berichte/T-078-ui-ux-designer.md (diese Datei).
           Kein Anwendungscode. Kein git add/commit/push/checkout/branch;
           git ausschliesslich lesend (git status, git branch).
ANNAHMEN: (1) Die Zahlen ueber die heutige Ausgabe (10-43 Zeilen je
          Vorschlag, Median 21, laengste Zeile 142 Zeichen, 36 von 309
          Relikten mit stummem Fluch, davon 3 mit All Resistances Down) sind
          die Messung des `developer` aus T-067 und **von mir nicht
          nachgemessen** — das Fenster durfte nicht starten, und ein eigener
          headless-Lauf haette den Arbeitsbaum des parallel laufenden
          `qa-engineer` beruehrt.
          (2) Ich habe die AD-015-Pflichtzeile **umformuliert und mit der
          Zahlzeile desselben Fluchs zu einer Zeile verschmolzen**. Den
          Wortlaut gibt AD-025.6 mir; dass die Zeile damit aus `unknowns` in
          die Slotgruppe wandert, ist eine Ortsfrage und braucht die
          Zustimmung des `director` (Abschnitt 5 unten).
          (3) Ich habe angenommen, dass der Knopf `Optimize` heisst (T-024
          §5.1) und nicht mehr `Suggest` (T-004 §3.1). Die Zustandstabelle
          4.1-4.14 sagt noch `Suggest`; ich habe sie nicht umgeschrieben.
NAECHSTER: director (drei Entscheidungen unten: die Ortsfrage der
           AD-015-Zeile, die Datenform aus §6 der Spec, und ob
           `model.compute_resistances` nach `sources` schreiben soll),
           danach developer
BLOCKIERT DURCH: nichts
```

---

## 1. Was spezifiziert ist

Ein neuer Abschnitt in `UI_SPEC.md`: *"Die Sprache des Beraters: eine Zeile je
Zahl, und die Fluche, auf die keine Zahl passt (T-078) — 2026-09-06"*, elf
Unterabschnitte, **AK-133 bis AK-150**. Betroffen sind der Vorschlagsblock
(§3.2), der `Why`-Dialog (§3.4), der Zustand 4.9, die vier Wortlaute des
`developer` und ein neues Feld auf `AdvisorResult`.

---

## 2. Die Formfrage (Auftrag Punkt 1) — entschieden: die Zeilen, §3.2s
## Einzelsatz faellt ersatzlos

Von den drei angebotenen Wegen — eine Zeile im Slot-Block, eine daraus
gebaute Zusammenfassung, oder §3.2 geht auf mehrere Zeilen — habe ich den
dritten gewaehlt, und den ersten und zweiten aus **einem** Grund verworfen,
der mir waehrend der Arbeit erst aufgefallen ist:

**Der Einzelsatz aus §3.2 ist nicht ehrlich schreibbar.** Sein Beispiel
lautet `Chosen for +15.0% Skill Attack Power and +6.0% all damage — the
largest gain of any Blue relic you own.` Jede Fassung dieser Art behauptet
eine Rangfolge unter den Beitraegen. Die gibt es nicht: ein Prozentsatz und
ein flacher Bonus sind ohne einen Umrechnungskurs nicht vergleichbar, den die
Spieldateien nicht hergeben. Das ist dieselbe Grenze, die AD-023 und OF-13
fuer den Fluch schon gezogen haben und die `explain.py` in seinem Docstring
ausdruecklich benennt (*"a percentage and a flat bonus cannot be put on one
scale without inventing the exchange rate A7 forbids"*). **Meine eigene
Vorgabe von 2026-09-01 verstiess damit gegen A7.** Sie ist aufgehoben, nicht
gekuerzt. Der `developer` hat richtig gehandelt, als er nichts erfunden hat.

Der zweite Grund ist der Platz, und er faellt kleiner aus als es die Zahl "21
Zeilen" nahelegt: §3.2 zeigt heute schon **eine Aufzaehlungszeile je Effekt**
(`• Improved Melee Attack Power`, aus `_sync_mode`). Die neue Form **ersetzt**
diese Zeilen — aus `• <Effektname>` wird `• <Effektname>: <Groesse> <Zahl>`.
Median 21 Zeilen auf sechs Slots sind rund 3,5 je Slot, also ungefaehr die
Zahl der Punkte, die dort ohnehin stehen. Teuer wird nur der schlechteste
Slot (sieben statt drei), und die Slotkarten stehen in der `QScrollArea`.

**Keine Kuerzung, kein "and 3 more".** Eine Kuerzung muesste nach A7/L-013
ihren Nenner tragen, und der Spieler muesste danach doch den `Why`-Dialog
oeffnen — zwei Formen derselben Aussage an zwei Orten, die Fehlerklasse aus
QA-082/QA-087.

---

## 3. Die vier Wortlaute (Auftrag Punkt 2)

**Zwei uebernommen, zwei korrigiert.**

| Satzart | Entscheidung |
|---|---|
| Begruendungszeile | **uebernommen** in ihrer Substanz, **gekuerzt um `Slot 4, <Reliktname> — `** (siehe Punkt 4 unten). Neue Form: `{effect name}: {figure label} {amount}[, counted against it]`. |
| Fluchzeile | **umgebaut**: drei Fuellungen statt einer, siehe Abschnitt 5. |
| Halte-Zeile | **uebernommen**, ein Fall korrigiert. |
| `data_note` | **uebernommen**, ein Wort korrigiert. |

**`, counted against it` bleibt woertlich.** Es sagt, dass gegengerechnet
wurde, ohne zu behaupten, wie viel es gekostet hat — genau die Auskunft, die
F3 verlangt, und keine mehr. Dass die Richtung aus `model.is_better_lower`
kommt und nicht aus dem Vorzeichen, ist als AK-137 festgehalten, damit es
niemand "vereinfacht".

**Halte-Zeile, korrigiert ist nur der dritte Fall.** Gebaut: `All 6 slots are
held, so nothing was searched: this is the build as it stands, scored.` Neu:
`All 6 slots are held, so there was nothing to search — this is your build as
it stands, with its figure.` Grund: `scored` steht als alleinstehendes
Partizip am Satzende und ist die Sorte Verkuerzung, bei der ein
nicht-technischer Spieler raten muss (A11). `the build` → `your build`, weil
es seiner ist. Die ersten beiden Fassungen sind gut, wie sie sind: sie tragen
ihren Nenner und benutzen `held`, also genau das Wort, das der Knopf in der
Slotkopfzeile traegt (T-024 §4.1).

**`data_note`, korrigiert ist das Wort `snapshot`.** Es steht in **AK-127 auf
der Verbotsliste des Erststarts** — ein Spieler weiss nicht, was ein "stored
snapshot" ist, und es gibt keinen Grund, dasselbe Wort auf einem anderen
Schirm doch zu benutzen. Wichtiger: die Auskunft, auf die es ankommt, ist
nicht der Speicherort, sondern der **Zeitpunkt**. Neu:
`Ranked on game data version 10350000, read from your game files earlier and
kept since.` bzw. `…, read from your game files just now.`; ohne Version ein
zweiter Satz, der sagt, dass die Zahlen keinem Patch zuzuordnen sind. Die
Versionsnummer selbst bleibt stehen — sie ist die Kennung des Spiels, und
`game data version` nennt ihren Geltungsbereich (A12).

---

## 4. Die Slotnummer (Auftrag Punkt 4) — sie faellt aus der Zeile

Sie ist doppelt, und die Zeile ist die schlechtere der beiden Stellen. Die
gebaute Zeile wiederholt auf bis zu sieben aufeinanderfolgenden Zeilen
dieselben rund 35 Zeichen (`Slot 4, Deep Grand Burning Scene — `). Kopf der
Gruppe traegt beides einmal: im `Why`-Dialog `Slot {n} — {Reliktname}`, im
Vorschlagsblock nur der Reliktname, denn **die Karte ist der Slot**.
Nebenwirkung: die laengste Zeile sinkt von gemessenen 142 auf rund 105
Zeichen. Die Nummer bleibt **einsbasiert** im gezeichneten Kopf und
nullbasiert im Datenweg, so wie der `developer` es begruendet hat.

**Das hat eine Folge, die nicht in meiner Hand liegt** (Spec §6): sobald je
Slot gruppiert gezeichnet wird, muesste das Fenster den Satz zerlegen, um zu
wissen, wohin er gehoert — und das bricht am ersten Reliktnamen mit einem
Gedankenstrich. Ich habe deshalb **die Eigenschaft** verbindlich gemacht, nicht
die Bauart: jede Zeile erreicht die Anzeige mit ihrer Slotnummer, mit der
Auskunft, ob sie ein Fluch ist, und je Slot mit den beiden Zaehlungen der
Kopfzeile. Ob das ein Tupel von Tupeln, ein Feld auf `Suggestion` oder ein
eigener Datensatz je Slot wird, gehoert `architect` und `developer`. AK-147
prueft die Eigenschaft per Grep (kein `.split(`, `.startswith(`, `.find(`,
kein `re.` auf den Zeilenfeldern).

---

## 5. Der Fluch ohne Zahl (Auftrag Punkt 3) und die drei Fluchzeilen

**Wie der Spieler es erfaehrt:** an dem Relikt, das ihn kostet — nicht in
einer Sammelliste am Dialogende, die ihn zwingt, den Namen zurueckzusuchen.
Eine Zeile je Fluch, `✦`, `CURSE`, in der Gruppe ihres Slots, in einer von
drei Fuellungen:

1. `✦ {curse}: {figure label} {amount}, counted against it` — er bewegt eine
   gezaehlte Zahl.
2. `✦ {curse}: {figure label} {amount} — this figure does not count it.` — er
   bewegt eine Zahl, die diese Zielrichtung nicht zaehlt.
3. `✦ {curse}: no number here shows what this costs.` — er bewegt hier gar
   keine Zahl. **Das ist D-2.**

Dazu genau **einmal je `Why`-Dialog**, unter allen Gruppen:
`✦ marks a curse. A cost with no number beside it is still a cost — weigh it
before you apply.` Der Satz ist zugleich die `✦`-Legende, die §1.4 des
T-056-Abschnitts fuer jede Farbrolle verlangt, und die einzige Stelle mit
einer Aufforderung. Sechsmal derselbe Satz waere das Rauschen, gegen das
AK-50 geschrieben ist.

**Der Wortlaut von (3) sagt bewusst nichts ueber die Spieldateien.** Bei drei
der 36 Relikte (`All Resistances Down`, Effekt 6850200) **gibt** es Zahlen —
sieben Widerstandswerte um je 80 —, nur die Rechnung des Beraters fuehrt sie
nirgends. Ein Satz wie *"the game files carry no numbers for these"* waere
dort schlicht falsch. Er steht heute in 4.9 und ist dort entfernt (AK-140
verbietet die Zeichenkette).

**Das Kriterium des neuen Feldes ist absichtlich weit:** *ein Fluch einer
vorgeschlagenen Kopie, zu dem keine Zeile entstanden ist.* Nicht "ohne Zahlen
in den Daten", nicht "konditional". Damit ist es vorwaertskompatibel: schreibt
`compute_resistances` eines Tages nach `sources`, wandern die drei Relikte von
selbst aus Fuellung (3) in (1) oder (2), ohne dass hier ein Satz nachgezogen
wird. Eine Vorgabe, die "die 36" festschreibt, waere am naechsten Spielstand
falsch.

**Feldname:** `curses_without_a_figure`, ohne Zaehlfeld daneben — die Anzahl
ist die Laenge, wie `types.py` es fuer `not_counted` schon begruendet.

### Die eine Stelle, an der ich ueber meinen Auftrag hinausgegriffen habe

Fuellung (2) **verschmilzt zwei heute getrennte Ausgaben zu einer Zeile**: die
Zahlzeile des Fluchs aus `reasons`/`curses` und die AD-015-Pflichtzeile aus
`unknowns` (`A curse on <relic> changes <field>, which this goal does not
rank.`). Heute steht dieselbe Sache zweimal da, an zwei Orten, und der
Reliktname in der zweiten ist ueberfluessig, weil die Gruppe ihn traegt.

Den **Wortlaut** gibt AD-025.6 mir. Den **Ort** nicht: die Zeile wandert damit
aus `AdvisorResult.unknowns` in die Slotgruppe. Das ist eine Entscheidung des
`director`, und ich melde sie an, statt sie zu behaupten. **Wird sie
abgelehnt**, bleibt (2) als eigener Satz in `unknowns` stehen und der Fluch
erscheint wieder an zwei Stellen — die Spec bleibt im uebrigen gueltig, nur
AK-148 und §3 Fuellung (2) waeren zu streichen.

Nebenbefund dazu: bleibt es bei der Verschmelzung, traegt `unknowns` danach
nur noch die Halte-Zeile und die Zeile fuer einen weggefallenen Halt (T-024
§4.3).

---

## 6. Korrektur an 4.9 (Vorgabe D-3)

`not_counted` behaelt AD-010 (konditionale Effekte). 4.9 zerfaellt in zwei
Klauseln der Statuszeile, die unabhaengig voneinander auftreten:

- **4.9a** `{n} curses carry no number.` (das neue Feld)
- **4.9b** `{n} effects were left out: they only apply under a condition.`
  (`not_counted`)

Reihenfolge: erst der Preis, dann das Weggelassene. Im `Why`-Dialog steht
4.9a **bei seinem Relikt** und 4.9b als eigener Abschnitt mit der Ueberschrift
`These effects only apply under a condition, so this ranking did not count
them:`. Der alte Satz `The game files carry no numbers for these, so they
counted for nothing:` entfaellt ersatzlos.

Der Wortlaut von 4.9b folgt der Familie, die im `SlotPool` schon steht
(*"…carry effects that only apply under a condition. They were not
counted."*), ohne das Wort "conditional" zu benutzen — dieselbe Ueberlegung
wie im Nachtrag zu OF-20.

---

## 7. Die Akzeptanzkriterien AK-133 bis AK-150

Fuer den `director` zum Weiterreichen an den `developer`; volle Fassung in
`UI_SPEC.md`.

**Form**
- **AK-133** Kein zusammenfassender Begruendungssatz; `Chosen for` kommt im
  Programm nicht vor; keine Zeile endet auf eine Kuerzungsformel.
- **AK-134** Die Zahl gezeichneter Zeilen je Slotgruppe ist gleich der Zahl,
  die das Ergebnis fuer diesen Slot traegt. *Ersetzt AK-18.*
- **AK-135** Keine Zeile wiederholt Slotnummer oder Reliktnamen ihres Kopfes;
  die Slotnummer erscheint einsbasiert und nur im `Why`-Dialog.
- **AK-136** Jede Zeile folgt woertlich einer der Fassungen aus §2/§3, samt
  Satzzeichenregel (Zahl am Ende: kein Punkt; Satz am Ende: Punkt).
- **AK-137** `, counted against it` genau nach `model.is_better_lower`, nie
  nach dem Vorzeichen. Pruefweg: ein Feld, das kleiner besser ist, gesenkt —
  der Zusatz steht **nicht** da.

**Fluche**
- **AK-138** Je vorgeschlagener Kopie ist die Menge der gezeigten Fluchnamen
  **gleich** der Menge ihrer `curse_ids`, unabhaengig ueber
  `ctx.data["effects"]` aufgeloest; jeder in genau einer der drei Fuellungen.
- **AK-139** `AdvisorResult.curses_without_a_figure` existiert, getrennt von
  `not_counted`, mit gepruefter Gegenrichtung.
- **AK-140** Kein Text behauptet, die Spieldateien traegen keine Zahlen; die
  Zeichenketten `carry no numbers` / `carries no numbers` kommen nicht vor.
- **AK-141** Der Schlusssatz mit der `✦`-Legende steht genau einmal je
  `Why`-Dialog und in keinem Vorschlagsblock.

**4.9 und Statuszeile**
- **AK-142** `not_counted` traegt nur konditionale Effekte; der alte
  4.9-Satz erscheint nirgends. *Ersetzt AK-21.*
- **AK-143** Die beiden Klauseln woertlich, in dieser Reihenfolge, mit
  richtigem Singular/Plural, voller Text im Tooltip.

**Sprache**
- **AK-144** Der gezeigte Text enthaelt keines der Woerter `field`, `pool`,
  `handle`, `beam`, `scorer`, `source`, `snapshot`, `slot_index`,
  `not_counted`, `contribution`.
- **AK-145** Halte-Zeile und `data_note` woertlich in allen Fuellungen.
- **AK-146** Die Zaehlzeile woertlich; `{n}` zaehlt **Effekte**, nicht Zeilen.

**Struktur und Sicherheit**
- **AK-147** Kein Anzeigecode zerlegt oder durchsucht eine Zeichenkette aus
  `explain.py` (Grep-Liste in der Spec).
- **AK-148** Kein Fluchname zweimal je Slotgruppe; `reasons` und `curses`
  werden nie beide gezeichnet.
- **AK-149** AK-29/AK-30 gelten fuer jede neue Zeile (`setTextFormat()`,
  buchstabengetreue Anzeige eines praeparierten Namens).

**Am laufenden Fenster**
- **AK-150** Schlechtester Fall (sieben Effekt- plus zwei Fluchzeilen in einem
  von sechs belegten Slots, laengster Reliktname): keine waagerechte
  Bildlaufleiste, nichts abgeschnitten, kein Umbruch mitten im Begriff, alles
  durch senkrechtes Scrollen erreichbar — bei 1320 px und UI scale
  `Automatic` **und** 150 %. Die Messung nennt Plattform, Qt-Stil,
  Skalierung und ob physisch oder logisch (L-009), sonst zaehlt sie nicht.

---

## 8. Was mir aufgefallen ist und nicht in den Auftrag gehoerte

1. **`curses` ist die Teilmenge von `reasons`, nicht ihr Gegenstueck.** Beide
   entstehen aus `_attributed`; `curses` filtert `is_curse`. Wer beide
   Listen zeichnet — und das ist die naheliegende Lesart von AD-010 —, zeigt
   **jeden Fluch zweimal**. Das Feld ist von AD-010 verlangt und bleibt;
   gezeichnet wird `reasons`. AK-148 haelt es fest, aber es ist ein
   Entwurfsbefund, kein Anzeigedetail: zwei Felder, eine Wahrheit.
2. **`model.compute_resistances` schreibt nicht nach `Build.sources`.** Das
   ist die eigentliche Ursache dafuer, dass `All Resistances Down` in keinem
   Feld auftaucht — 7 x 80 Widerstandspunkte, die kein Text nennt. Meine
   Fuellung (3) faengt es ab, ohne zu luegen, aber sie ersetzt keine Zahl.
   **Empfehlung an den `director`:** einen eigenen Auftrag pruefen lassen, ob
   `compute_resistances` `sources` fuellen soll. Die Spec funktioniert in
   beiden Faellen, aber mit Zahl waere die Auskunft besser.
   **Wichtig fuer die Beurteilung:** dass diese Zahl heute in keiner der
   beiden Rankingzahlen steckt, ist kein Versehen — `_DAMAGE_TAKEN_SCOPE`
   sagt woertlich *"Ailment and status resistance are not part of this
   figure."* Eine dritte Zielrichtung, die Widerstaende rankt, macht Fuellung
   (3) fuer diese drei Relikte falsch; dann muss sie wieder aufgemacht
   werden.
3. **Die Zustandstabelle 4.1-4.14 spricht noch vom Knopf `Suggest`,** T-024
   §5.1 hat ihn in `Optimize` umbenannt. Ich habe `Optimize` benutzt und die
   Tabelle nicht umgeschrieben — das ist eine Ersetzung an rund einem Dutzend
   Stellen und gehoert entschieden, bevor S10 gebaut wird, nicht danach. Als
   offene Frage 3 in der Spec.
4. **T-024 §3.3 schreibt `−18` mit typografischem Minuszeichen**, das
   Statblatt (`app.py`, `f"{x:+g}"`) und `explain.py::_amount` schreiben
   ASCII. Fuer die Beraterzeilen habe ich ASCII festgeschrieben; die
   Wertspalte des Pickers habe ich **nicht** angefasst, sie ist nicht mein
   Auftrag. Wer sie baut, sollte ASCII nehmen, sonst stehen zwei
   Schreibweisen derselben Zahl auf einem Schirm.
5. **D-11 des `developer` (Zahlenformat an zwei Orten) wird durch diese Spec
   teurer, nicht billiger.** `_amount` und `_show_breakdown` muessen jetzt
   nachweisbar dasselbe schreiben (AK-136 verlangt das Statblatt-Format).
   Solange beide Orte existieren, ist das eine Zusicherung ohne Waechter.
6. **Was ich nicht geprueft habe:** nichts am laufenden Fenster. Keine
   Zeilenhoehe, keine Kartenhoehe, keine Breite, kein Kontrast der neuen
   Zeilen (die Token sind Bestand: `CURSE` 4,50:1 und `MUTED` 4,77:1 auf
   `PANEL`, gerechnet in T-024, nicht von mir nachgerechnet). AK-150 ist
   deshalb ein Pruefauftrag und kein Befund.

---

## 9. Offene Fragen an den App Designer

Sie stehen wortgleich in `UI_SPEC.md`, Abschnitt 11:

1. **Wie viel Fluch vertraegt die Slotkarte?** Diese Vorgabe zeigt jeden
   Fluch im Block, auch den ohne Zahl — bei drei Fluchrollen sind das drei
   rote Zeilen in einer sonst vierzeiligen Karte. Die Gegenposition (stumme
   Fluche erst im `Why`-Dialog) waere ruhiger und verstiesse gegen §3.2s
   "der Preis darf nicht erst nach dem Anwenden sichtbar werden".
2. **Soll ein Effekt ohne Zahl beim Namen genannt werden, so wie ein Fluch
   ohne Zahl?** Heute sagt die Zaehlzeile `3 of its 5 effects moved a number
   in this build.` und schweigt darueber, welche zwei nichts bewegt haben.
3. **`Optimize` oder doch `Suggest`?** Siehe Abschnitt 8 Punkt 3.

**Pfad zur Spec:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\UI_SPEC.md`
(neuer Abschnitt am Ende, ab Zeile 3153).
