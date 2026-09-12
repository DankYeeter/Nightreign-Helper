# T-080 — ui-ux-designer (Modus Spec, Nachtrag zu T-078)

```
STATUS: erledigt
AUFTRAG: T-080 — Nachtrag zur Sprache des Beraters (Spec)
GELESEN: docs/tasks/T-080.md (mit dem Zitat von GOAL A5/A12 und dem
         Stand-Auszug aus docs/state.md; beide tragen den Auftrag, GOAL.md
         und docs/state.md daher nicht erneut von vorn gelesen) ·
         UI_SPEC.md, T-078-Abschnitt vollstaendig (§1 bis §11, AK-133 bis
         AK-150) sowie die Token-Tabellen bei Zeile 293 und 931 ·
         docs/berichte/T-078-ui-ux-designer.md (der eigene Vorbericht,
         Abschnitte 1-3 und 9) · nrplanner/advisor/explain.py (ganz) ·
         nrplanner/advisor/types.py (Candidate, GoalContext, Weighting,
         SlotPool) · nrplanner/model.py (SourceEntry, Situational, Build,
         compute, compute_qualitative, collapse_by_label, label_for,
         RATE_LABELS) · nrplanner/effecttext.py (name, owner, works_for,
         describe_full) · nrplanner/paths.py · scripts/measure_advisor_picker.py
         (als Vorlage fuer den Messaufbau) · CLAUDE.md ·
         .claude/agent-memory/ui-ux-designer/ (beide Dateien)
GEAENDERT: UI_SPEC.md (ein neuer ##-Abschnitt am Ende, Zeilen 3728-4223,
           AK-151 bis AK-161; AK-150 wird darin ersetzt, der uebrige
           T-078-Text bleibt unangetastet) ·
           docs/berichte/T-080-ui-ux-designer.md (diese Datei) ·
           .claude/agent-memory/ui-ux-designer/feedback_headless_verification.md
           (ein Absatz zur Messmethode angehaengt).
           Kein Anwendungscode, kein Skript im Repo, kein Bildnachweis.
           Das Fenster wurde nicht gestartet. Git ausschliesslich lesend
           (git status, git branch).
ANNAHMEN: (1) Die Messungen unten stammen aus **einer** Umgebung: Datensatz
          10350000, der eigene Spielstand (309 Relikte), Nightfarer Wylder,
          Stufe 15, Startwaffe als Bezugs- und einzige gefuehrte Waffe, keine
          Bedingung als erfuellt erklaert, ein Relikt je Slotgruppe. Auf
          einem anderen Nightfarer faellt die Verteilung anders aus; welche
          Kopien der Berater wirklich vorschlaegt, konnte ich nicht messen,
          weil es ohne S9/S10 keinen vollstaendigen Lauf gibt.
          (2) Fuellung (a2) — "eine andere Kopie hat ihn schon beigetragen" —
          ist die einzige Fuellung, deren Haeufigkeit ich **nicht** gemessen
          habe; sie kann nur ueber mehrere Slots auftreten. Sie ist so
          spezifiziert, dass sie entfallen darf, wenn das Ergebnis die
          Auskunft nicht traegt.
          (3) Ich habe angenommen, dass die stummen Zeilen an **beiden**
          Orten (Block und Why-Dialog) stehen. Der App Designer hat das fuer
          den Fluch entschieden, fuer den stummen Effekt nicht ausdruecklich;
          ich habe es aus T-078 §1 fortgeschrieben und stelle es als Frage 2
          zur Bestaetigung.
NAECHSTER: director (zwei offene Fragen unten, dazu die Entscheidung zu
           compute_resistances aus Abschnitt 6), danach developer
BLOCKIERT DURCH: nichts
```

---

## 1. Was spezifiziert ist

Ein Nachtrag in `UI_SPEC.md`: *"Nachtrag zu T-078: der stumme Effekt bekommt
seinen Namen, und der schlechteste Fall einer Slotkarte ist gemessen statt
geschaetzt (T-080) — 2026-09-06"*, zwoelf Unterabschnitte, **AK-151 bis
AK-161**, davon ersetzt **AK-160 das bisherige AK-150 vollstaendig**. Alles
uebrige aus AK-133 bis AK-149 bleibt woertlich stehen.

Betroffen sind: die Slotgruppe im Vorschlagsblock und im `Why`-Dialog, die
Zaehlzeile aus T-078 §6, ein zweites neues Feld auf `AdvisorResult`, und die
Messumgebung des Kartenhoehen-Kriteriums.

---

## 2. Die drei Auftragspunkte

**Punkt 3 (Frage 1 festhalten).** Erledigt in §1 des Nachtrags und als
**AK-159** pruefbar gemacht: die Menge der Fluchnamen **im Block** ist gleich
der Menge der `curse_ids` der vorgeschlagenen Kopie — nicht nur im Dialog.
Verglichen werden Namen, nicht Zeilen, weil ein Fluch mit zwei Groessen zwei
Zeilen erzeugt. Damit ist die Entscheidung nicht nur notiert, sondern
messbar, und der naechste Durchgang kann sie nicht versehentlich aufmachen.

**Punkt 2 (Spielwissen in die Spec).** Erledigt in §2, nachgezaehlt statt
uebernommen. Alle Zahlen des Auftrags bestaetigt: 0 von 597 nicht-Deep-Relikten
mit Fluch; Deep 108/72/48/24 fuer null/ein/zwei/drei Fluche. Dazu neu:
Effektrollen je Relikt 230/267/349 fuer eine/zwei/drei — **und drei Relikte
mit gar keiner** (`Murk`, `Sovereign Sigil`, `Scenic Flatstone`). Auf dem
Spielstand liegen 6 Relikte mit drei Fluchen; "drei plus drei" ist real.

**Punkt 1 (der Wortlaut).** Erledigt in §3 und §4. Der stumme Effekt bekommt
eine Zeile in seiner Slotgruppe, mit `•`, in `MUTED`, 11 px, **in der Ordnung
des Relikts** (also zwischen den Zahlzeilen, nicht ans Ende sortiert), kein
`✦`, kein `CURSE`, kein `⚠`. Sechs Fuellungen, die erste zutreffende gewinnt:

| # | Fall | Wortlaut |
|---|---|---|
| a | gehoert einem anderen Nightfarer | `{effect name}: works only for {owner}, and you are {hero}.` |
| a2 | eine andere Kopie hat ihn schon beigetragen | `{effect name}: another copy of it is already counted, so this one adds nothing.` |
| b | wartet auf eine Bedingung | `{effect name}: only applies under a condition, so no number here.` |
| c | haengt an den Armaturen | `{effect name}: it depends on the armaments you carry, so no number here.` |
| d | alles Uebrige | `{effect name}: no number here shows what this adds.` |
| e | Datensatz kennt den Effekt nicht | `One of its effects is not in your game data, so it has no name here and counted for nothing.` |

(d) ist bewusst die Familie der Fluchfuellung (iii) aus T-078 — `costs` dort,
`adds` hier, sonst derselbe Satz.

**Die Zaehlzeile bleibt** (§5), aus drei Gruenden: sie traegt den Nenner, sie
wird durch die Namen darunter **nachrechenbar** (`{total} − {n}` gleich der
Zahl der stummen Zeilen, AK-155), und eine Regel mit Ausnahme kostet mehr als
die eine Zeile, die sie spart. Zwei Fuellungen kommen dazu, die T-078 fehlten:
fuer eine Kopie **ohne** Effektrollen und fuer eine Kopie, bei der **weder**
Effekt noch Fluch eine Zahl bewegt hat.

---

## 3. Warum nicht eine einzige Fuellung: der Befund, der das entschieden hat

Ich habe die 426 stummen Effekte der 309 besessenen Relikte danach sortiert,
**warum** das Programm sie fuer stumm haelt — die Auskunft steht bereits
berechnet in `Build.qualitative`:

| Grund | Anzahl |
|---|---|
| arbeitet fuer einen **anderen** Nightfarer (totes Gewicht) | **150** |
| wartet auf eine Bedingung, in der der Spieler sein kann | **170** |
| haengt an den Armaturen (Waffentyp, mehrere davon, Skill) | **58** |
| wirkt, laesst sich aber auf keine Zahl bringen | **48** |

Ein einziger Satz fuer alle vier haette die 150 aus der ersten Zeile mit den
170 aus der zweiten gleichgesetzt. Das eine ist tot, das andere wartet nur —
den Unterschied nicht zu sagen, obwohl das Programm ihn kennt, ist genau die
bequeme Ungenauigkeit, gegen die A11 geschrieben ist.

---

## 4. Was der Auftrag nicht wissen konnte: AK-150 wird nicht kleiner,
## sondern **groesser**

Der Auftrag geht davon aus, dass "drei plus drei" den schlechtesten Fall der
Karte **begrenzt** und AK-150 mit "sieben plus zwei" zu gross gegriffen hat.
Die erste Haelfte stimmt, die zweite nicht — und das ist der wichtigste Punkt
dieses Berichts:

**"Drei plus drei" begrenzt die Namen, nicht die Zeilen.** Ein Effekt kann
mehrere Groessen bewegen und dann mehrere Zeilen erzeugen. Gemessen:

- Ueber die 483 Effekte, die auf einem Relikt ueberhaupt rollen koennen:
  einer erzeugt bis zu **fuenf** Zeilen, ein fluchfaehiger bis zu **vier**.
- Auf dem Spielstand gibt es Relikte mit **neun** Effektzeilen und Relikte mit
  **vier** Fluchzeilen.
- Der schlimmste gezeichnete Fall ist die Kopie von `Deep Grand Tranquil
  Scene`: 3 Effekte → 9 Zahlzeilen, 3 Fluche → 4 Zahlzeilen und 1 stumme
  Zeile = **14 Zeilen**, plus Reliktname und Zaehlzeile = **16 Zeilen** in
  **einer** Karte.
- Die laengste Zeile ist nicht die mit der Zahl (106 Zeichen, wie T-078 mit
  ~105 geschaetzt hatte), sondern eine **stumme**: der Effektname `[Wylder]
  Standard attacks enhanced with fiery follow-ups when using Character Skill
  (greatsword only)` ist allein 101 Zeichen lang, mit Fuellung (b) sind es
  **rund 150** — laenger als die 142 Zeichen, die T-078 als heutigen
  Schlechtfall abschaffen wollte.

AK-160 traegt diese Tabelle und benennt die Kopie, an der sie nachzustellen
ist. **AK-161** verpflichtet zusaetzlich dazu, die Zeilenzahl je Vorschlag
nach dem Einbau **neu** zu messen: die T-067-Zahlen (10 bis 43 Zeilen, Median
21) sind vor den stummen Zeilen entstanden und tragen nicht mehr.

---

## 5. Zwei Berichtigungen an meiner eigenen T-078-Vorgabe

1. **Zwei Beispiele in T-078 zeigen ein unmoegliches Relikt.** Der
   Beispielkopf in §6 (`3 of its 5 effects moved a number in this build.`) und
   der Beispielblock in §7 (`The Will of the Balancers` mit fuenf Effekten)
   gibt es im Spiel nicht: `{total}` ist hoechstens 3. Die **Wortlaute** dort
   bleiben gueltig, nur die Zahl im Beispiel war falsch. Im Nachtrag steht
   stattdessen eine **echte** Kopie aus dem Spielstand (`Deep Grand Drizzly
   Scene`, Handle `3229614356`) mit ihren wirklichen Zeilen.
2. **T-078 §6 hat keine Fuellung fuer eine Kopie ohne Effektrollen.** Drei
   Relikte im Datensatz haben keine; die Zaehlzeile haette dort `None of its 0
   effects …` gesagt. Nachgetragen in §5 des Nachtrags.

---

## 6. Was der `director` entscheiden muss (ausserhalb der Fragen an den
## App Designer)

**Die Widerstandsluecke ist groesser als T-078 wusste.** T-078 nannte drei
besessene Relikte mit `All Resistances Down`, deren Zahlen `explain.py`
nirgends findet, weil `model.compute_resistances` weder nach `sources` noch
nach `qualitative` schreibt. Gemessen sind es **nicht nur die Fluche**: von
den 426 stummen positiven Effekten sind **33** Widerstandseffekte
(`Improved Poison Resistance` und Verwandte). Sie sind die einzige Gruppe
stummer Effekte, fuer die das Programm **keinen** Grund kennt, und bekommen
deshalb die schwaechste Fuellung (d), obwohl es die Zahl gibt.

Die Vorgabe funktioniert in beiden Faellen — sie ist am Kriterium "keine Zeile
entstanden" gebaut, nicht an einer Liste. Aber die Empfehlung aus T-078 §11
wiegt jetzt schwerer: die Luecke betrifft **36 Zeilen auf einem einzigen
Spielstand**, nicht drei.

**Nebenbei, fuer AK-147:** ich habe beim Messen einen Feldnamen gefunden, der
**heute schon** einen Gedankenstrich enthaelt —
`model.RATE_LABELS["regainRate"]` heisst woertlich `Regain — HP won back by
attacking after a hit`. Anzeigecode, der eine Zeile an `—` zerlegt, bricht
also nicht erst an einem hypothetischen Reliktnamen, sondern an einer Zeile,
die auf dem Spielstand des App Designers wirklich vorkommt.

---

## 7. Was nicht gesehen ist

- **Kein Pixel.** Das Fenster wurde nicht gestartet (Auftrag). Alle Zahlen
  sind Zeilen und Zeichen. Ob 16 Zeilen in einer Karte auf 1320 px Breite
  passen, entscheidet AK-160 am laufenden Fenster — das ist offen.
- **Kein vollstaendiger Beraterlauf.** Es gibt ohne S9/S10 keinen. Gemessen
  ist deshalb je Relikt **einzeln**, nicht die Belegung von sechs Slots. Was
  das nicht zeigen kann: Effekte, die sich ueber mehrere Slots nicht stapeln
  (Fuellung a2), und wie oft eine Kopie, deren Effekte alle stumm sind
  (49 der 309), wirklich vorgeschlagen wird.
- **Ein Nightfarer, eine Stufe.** Wylder, Stufe 15. Auf Ironeye waeren andere
  Effekte stumm; die 150 Faelle der Fuellung (a) sind eine Wylder-Zahl.
- **Eine Abweichung zu T-067, ungeklaert:** der `developer` zaehlte 36 von 309
  Relikten mit einem Fluch, den das Ergebnis in keinem Feld nennt; ich zaehle
  **52** Relikte mit mindestens einem stummen Fluch (37 mit einem, 15 mit
  zwei). Die Umgebungen unterscheiden sich (er: echte Vorschlaege ueber beide
  Zielrichtungen; ich: ein Relikt je Gruppe, Wylder, Stufe 15). Ich habe seine
  Zahl **nicht** widerlegt und meine nicht gegen seine gerechnet — wer beide
  braucht, muss sie in **einer** Umgebung neu erheben.

---

## 8. Offene Fragen an den App Designer

1. **Der Effekt, der auf dieser Figur totes Gewicht ist — reicht ihm `MUTED`?**
   Fuellung (a) trifft **150 der 426** stummen Effekte auf dem eigenen
   Spielstand. Sie ist die einzige, die sagt: dieser Effekt tut hier **nie**
   etwas. Der Rest des Programms zeigt genau das auf den Slotkarten als
   `NOT WORKING` mit Durchstreichung. Im Vorschlagsblock steht er nach dieser
   Vorgabe still und grau wie die anderen Fuellungen — weil die Ansage lautete:
   keine Warnfarbe, er kostet nichts. Das stimmt, solange man "kostet" als
   Rechengroesse liest; als **Slotplatz** kostet er sehr wohl. Soll Fuellung
   (a) die Behandlung bekommen, die der Rest des Programms ihr gibt?
2. **Sollen die stummen Zeilen im Vorschlagsblock stehen, oder nur im
   `Why`-Dialog?** Diese Vorgabe zeigt sie an beiden Orten, weil zwei Formen
   an zwei Orten die Fehlerklasse aus QA-082 sind. Der Preis ist Hoehe: die
   Karte waechst im gemessenen schlimmsten Fall auf 16 Zeilen, und eine davon
   ist rund 150 Zeichen lang. Die Gegenposition waere: im Block nur die Zeilen
   mit Zahl und die Fluche, die stummen Effekte erst im Dialog — anders als
   beim Fluch waere das kein verstecktes Risiko, denn ein stummer Effekt ist
   keine Falle.
