# T-077 - qa-engineer

```
STATUS: erledigt
AUFTRAG: T-077 - Erstpruefung der Suche (S7) und der Begruendung (S8)
GELESEN: docs/tasks/T-077.md (mit den Pflichtzitaten aus GOAL.md A3/A4/A5 und
         dem Stand-Auszug aus docs/state.md, beide tragen den Auftrag) ·
         docs/berichte/T-067-developer.md (vollstaendig, Abschnitt 8 ist an
         mich adressiert) · nrplanner/advisor/{search,explain,candidates,
         evaluate,goals,types}.py · nrplanner/model.py:985-996 ·
         nrplanner/inventory.py:85-140 · tests/conftest.py ·
         tests/advisor_cases.py · tests/test_advisor_{search,explain,
         candidates,goals,evaluate,types}.py ·
         tests/test_differential_track.py:478-495 ·
         scripts/differential/mutate.py (Ankerpruefung) · UI_SPEC.md
         (Zustandstabelle 4.5/4.6/4.9/4.11) · qa/findings.md (Kopf und
         Schluss)
GEAENDERT: docs/berichte/T-077-qa-engineer.md (diese Datei). Ausserdem mein
         eigenes Rollengedaechtnis unter `.claude/agent-memory/qa-engineer/`
         (drei Dateien) - das liegt zwar im Arbeitsbaum, ist aber ueber
         `.gitignore:22` ausgeschlossen und aendert den git-Zustand nicht;
         ich nenne es trotzdem. Sonst nichts - kein Anwendungscode, kein
         Test, keine andere Doku, kein git-Zustand.
         Alle Mutationen und Messskripte liegen in drei eigenen Klonen im
         Scratchpad (qa-clone, qa-clone2, qa-clone3), jeder nach jedem Lauf
         mit `git checkout --` bereinigt und mit `git status --porcelain`
         als sauber nachgewiesen.
ANNAHMEN: (1) Der Auftrag nennt Stand `1e8697a`; HEAD des Zweigs ist
         `831b859`. `git diff --stat 1e8697a..HEAD` zeigt ausschliesslich
         docs/state.md, docs/tasks/T-077.md und docs/tasks/T-078.md -
         **kein** Anwendungs- oder Testcode. Ich habe gegen HEAD geprueft und
         betrachte das als denselben Code.
         (2) Der Auftrag schreibt "ein Slot mit leerem Pool - auf dem echten
         Spielstand kommt das fuer eine Deep-Farbe wirklich vor". Nachgezaehlt
         kommt es **nicht** vor (Abschnitt 4.3); ich lese die Stelle als
         Paraphrase des `developer`, der von der Poolgroesse **21** spricht,
         nicht von 0. Die Kante habe ich trotzdem gebaut und geprueft.
         (3) Bewertet ist der Spielstand `USER_DATA000`, 309 Relikte,
         Datensatz 10350000, Wylder/Level 15 wie beim `developer`. Jede Zahl
         unten traegt ihren Nenner; auf einem anderen Spielstand sind es
         andere Zahlen.
NAECHSTER: director (drei Befunde entscheidungsbeduerftig, einer mit
         Wortlaut-Anteil fuer den ui-ux-designer)
BLOCKIERT DURCH: nichts
```

---

## 1. Die erste Frage: pruefen die vorhandenen Tests A3, A4 und A5?

**Kurz: A4 ueberwiegend ja, A3 zur Haelfte, A5 nein.**

Belegt habe ich das nicht durch Lesen, sondern durch Gegenbauten: elf
Aenderungen, die je eine Abnahmeklausel brechen, gegen die Suite gefahren.
Was rot wird, ist geprueft; was gruen bleibt, ist es nicht.

| Klausel aus GOAL.md | geprueft? | Beleg |
|---|---|---|
| A3 "mindestens zwei benannte Zielrichtungen" | **ja** | Gegenbau `A3-only-one-direction-is-offered` toetet 16 Faelle |
| A3 "je Slot ein konkretes Relikt aus dem Besitz" | **ja** | Gegenbau `A3-last-slot-left-empty` toetet 10 Faelle |
| A3 "fuer jeden Nightfarer und jedes bekannte Kelch-Layout" | **nein** | Nenner unten |
| A4 Slot-Farben des Kelchs | **ja** | Gegenbau `A4-every-slot-draws-every-colour` toetet 2 Faelle |
| A4 Deep-of-Night-Trennung | **ja** | Gegenbau `A4-deep-slot-takes-ordinary-relics` toetet 2 Faelle |
| A4 Stacking-Regeln | **nein** | Gegenbau `A4-effects-of-a-copy-counted-twice` **ueberlebt den vollen Standardlauf** (Befund 2) |
| A5 "nennt, welche Effekte den Ausschlag gaben" | **nein** | der Waechter ist namensbasiert und kann die Fehlzuordnung nicht sehen, die heute real auftritt (Befund 1) |

**A3 "jeder Nightfarer, jedes Kelch-Layout" - der Nenner.** In den beiden neuen
Testdateien wird genau **ein** Nightfarer namentlich verwendet (`Wylder`, 11
Aufrufe von `hero_by_name`) und **zwei** von 74 Gefaessen (`Wylder's Urn` 6x,
`Wylder's Chalice` 1x). Alles andere sind selbstgebaute Slot-Farben. Der
Datensatz kennt 10 Nightfarer, 74 Gefaesse, **41** verschiedene
Slot-Farbfolgen ohne Deep und **47** mit. Ich habe die Luecke selbst gefuellt
(Abschnitt 2): ueber alle 10 Nightfarer und alle 74 Gefaesse, mit und ohne
Deep, beide Richtungen - **296 Laeufe, keine Verletzung**. A3 gilt also *in
der Sache*; was fehlt, ist ein Waechter, der es weiter gelten laesst.

**A5 - warum "nein" trotz 22 gruener Faelle.** Der Abnahmefall
`test_the_reasons_name_only_effects_the_suggestion_brought` leitet die
erlaubte Menge unabhaengig her - aber **ueber Effekt-Namen**. Zwei
verschiedene Effekt-Ids mit demselben Namen sind fuer ihn ein Effekt. Genau
das ist die Fehlerklasse, die heute auftritt (Befund 1), und der Fall bleibt
dabei gruen, weil der falsch zugeordnete Name wirklich auf dem genannten
Relikt steht. Das ist kein Versehen im Fall, sondern eine Grenze der Form:
`Build.sources` fuehrt Namen, keine Ids (`nrplanner/model.py:996`), und was
die Zuordnung nicht unterscheiden kann, kann der Fall darueber auch nicht.

---

## 2. Was ich gefahren habe, und in welcher Umgebung

**Umgebung (L-009).** Windows 10 (10.0.19045), Python 3.12.10 (CPython),
`.venv` des Projekts. Datensatz: der Abzug des Programms,
`%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`, `extract_version` 11,
`data_version` 10350000, 2076 Effekte, 849 Relikte, 74 Gefaesse, 10 Helden.
Spielstand `USER_DATA000`, **309 Relikte, davon 101 Deep, 0 ohne Handle**;
Farbverteilung (Farbe, Deep): (0,f) 52, (1,f) 53, (2,f) 54, (3,f) 49,
(0,w) 23, (1,w) 30, (2,w) 27, (3,w) 21. Nightfarer Wylder, Level 15,
Referenzwaffe wie `tests/advisor_cases.scaling_armament` sie waehlt.
Alles headless; **es gibt noch keine Oberflaeche** (S9/S10 fehlen), also kein
Lauf gegen ein gebautes Artefakt (A9).

**Ausgangslauf.** `pytest -q -m "not slow"` im eigenen Klon:
**952 passed, 9 skipped, 5 deselected in 449,75 s**. Das deckt sich mit der
Zahl aus T-067; keine Regression vor meinen eigenen Pruefungen.

**Meine Messstrecken** (alle nur lesend, alle im Scratchpad):

| Messung | Umfang | Ergebnis |
|---|---|---|
| A3/A4/A5-Rundlauf ohne Halten | 10 Helden x ihre 74 Gefaesse x Deep an/aus x 2 Richtungen = **296 Laeufe**, 592 Vorschlaege, 2664 belegte Slots | 0 Farbverstoesse, 0 Deep-Verstoesse, 0 Kopie in zwei Slots, 0 nicht besessene Kopie, 0 unbelegte Slots, 0 leere Pools |
| derselbe Rundlauf mit echten gehaltenen Relikten | 1..n-1 Slots gehalten, **1036 Laeufe**, 3848 Vorschlaege | 0 Verstoesse; jeder Lauf traegt seine Halte-Zeile |
| jede Begruendungszeile gegen `model.compute` gegengerechnet | **10 322 Zeilen** | **130 Zeilen nennen eine Groesse, die der genannte Effekt nicht bewegt** (Befund 1) |
| Slot-Deckung der Begruendung | 2664 belegte Slots | **46 Slots ohne eigene Zeile**; in den 296 besten Vorschlaegen 23 solche Slots, **alle 23 haben die Rangzahl wirklich bewegt** (Befund 1) |
| Determinismus von `explain.py` ueber Prozessgrenzen | 4 Hash-Saaten, voller Lauf `Wylder's Chalice` + Deep, beide Richtungen, 368 Ausgabezeilen | **byte-identisch**, eine sha256; Gegenbau beweist, dass die Probe beisst |
| D-2 nachgezaehlt, mit eigenem Zaehlweg | 309 Relikte, 76 mit Fluch, 112 Fluchrollen | **36 von 309** bestaetigt; zusaetzlich **40 von 112 Fluchrollen** |
| Gegenbauten gegen die Abnahmeklauseln | 11 Aenderungen | 9 toetend, **2 ueberlebend** (Befunde 2 und 3) |
| Budget- und Strukturgrenzen | K/W = 1, 0, -1, 10^6; Problem ohne Slots; Pools doppelt | alle korrekt, laut wo laut sein muss |

Jede meiner Messstrecken habe ich selbst gegengebaut, bevor ich sie verwendet
habe (L-003). Der Farb-/Deep-Rundlauf meldet unter `relics_for(4, slot.deep)`
**315** Farbverstoesse; die Determinismus-Probe liefert unter einem einzigen
eingesetzten `set()` **vier verschiedene Ausgaben aus vier Saaten**.
**Eine Ausnahme, die ich nicht verschweige:** die Zeile "keine gehaltene Kopie
wurde noch einmal vorgeschlagen" aus dem Halte-Rundlauf ist bei dem dort
verwendeten Budget (K=3, W=4) **kein Nachweis** - unter dem Gegenbau
`held_handles -> frozenset()` bleibt sie still. Erst bei `DEFAULT_BUDGET`
schlaegt sie an (6 Treffer). Die Regel selbst ist durch den Fall des
`developer` gedeckt; meine Zahl dazu ist es nicht.

---

## 3. Befunde

### [P2 | Major | Hoch] Die Begruendung ordnet Effekte gleichen Namens dem falschen Relikt zu - ein belegter Slot bleibt ganz ohne Zeile

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/explain.py:126-164`, entscheidend Zeile 153
(`entry != name`); Ursache im Datenweg `nrplanner/model.py:993-996`
(`Build.sources` fuehrt den Effekt**namen**, nie die Id)
**Umgebung:** echter Spielstand, jeder Nightfarer, Deep of Night an,
Richtung `min_damage_taken`; ein Standardbudget ist nicht noetig

**Reproduktion** (kleinster Fall, ohne Suche, ohne Spielstand):

1. Zwei freie rote Slots, nichts gehalten.
2. Slot 1 bekommt eine Kopie mit Effekt **7000090** - im Spiel
   `Increased Maximum HP`, Modifier `addLifeForceStatus: 5`.
3. Slot 2 bekommt eine Kopie mit Effekt **6610400** - ebenfalls
   `Increased Maximum HP`, Modifier `maxHpRate: 1.10`.
4. `explain.reasons(...)` aufrufen.

**Erwartet:** `Slot 1 ... Increased Maximum HP: Vigor +5` **und**
`Slot 2 ... Increased Maximum HP: Max HP +10.0%`.

**Tatsaechlich:** beide Zeilen stehen unter **Slot 1**; Slot 2 bekommt
**keine** Zeile.

```
Slot 1, Vigor relic — Increased Maximum HP: Vigor +5
Slot 1, Vigor relic — Increased Maximum HP: Max HP +10.0%
```

`built.sources` ist dabei richtig: `{'Vigor': [('Increased Maximum HP', 5)],
'maxHpRate': [('Increased Maximum HP', 1.1)]}`. Falsch ist allein die
Zuordnung.

**Am echten Spielstand, mit Nenner:**

* **130 von 10 322** erzeugten Begruendungszeilen nennen eine Groesse, die der
  genannte Effekt gar nicht bewegt (gegengerechnet gegen `model.compute` auf
  dem einzelnen Effekt, nie gegen `explain`). Sie verteilen sich auf
  **112 von 592** Vorschlaegen (19 %).
* **23 von 296** besten Vorschlaegen enthalten einen Slot, ueber den die
  Begruendung **gar nichts** sagt. Alle 23 haben die Rangzahl wirklich
  bewegt - gemessen durch Herausnehmen der Kopie: **137 bis 184 Effective HP**.
  Im nachgerechneten Fall (`Wylder's Urn` + Deep) war der stumme Slot mit
  **+162,15 EHP der groesste Einzelbeitrag des ganzen Builds**.
  Gegenprobe: **0** stumme Slots, die nichts bewegt haben.
* Reichweite im Datensatz: **160 von 707** Effektnamen werden von mehr als
  einer Id getragen, **48** davon mit unterschiedlichen Modifier-Feldern. Auf
  diesem Spielstand: **15 von 297** getragenen Effektnamen kollidieren,
  **52 von 309** Relikten tragen mindestens einen solchen Effekt.

**Analyse:** `_attributed` sucht zu jedem Effekt einer gewaehlten Kopie
Eintraege in `sources`, die **denselben Namen** tragen, und nimmt je Feld den
ersten unbeanspruchten. Zwei Ids mit einem Namen sind fuer diese Suche ein
Effekt; die Kopie, die in Slot-Reihenfolge zuerst kommt, nimmt beide Felder
mit, die spaetere findet nichts mehr. Der Modul-Docstring nennt das als
Grenze ("it is a guess where a dataset gives one name to two different
effects") - was dort nicht steht, ist, dass die Folge **eine falsche Zahl auf
dem einen Slot und gar keine Zeile auf dem anderen** ist, und dass es auf dem
vorliegenden Spielstand alltaeglich vorkommt.

**Warum kein Test es sieht:** der Abnahmefall prueft, dass jede Zeile *einen
Namen* der vorgeschlagenen Kopien nennt. `Increased Maximum HP` **ist** ein
Name der Kopie in Slot 1. Der Fall kann nicht rot werden.

**Auswirkung:** Die Rangzahl ist **nicht** betroffen - gerechnet wird durch
`model.compute`, die Zahlen stimmen. Betroffen ist genau das, was A5 zusagt:
der Spieler liest auf einem Relikt einen Vorteil, den es nicht hat, und
bekommt fuer das Relikt, das den Vorteil wirklich bringt, keine Begruendung.
Fuer S9/S10 heisst das: der `Why`-Dialog ist an dieser Stelle nicht
nachpruefbar, und wer im Spiel gegenprueft, findet den Widerspruch.

**Vorschlag:** Die Zuordnung braucht die Effekt-**Id**, nicht den Namen. Der
saubere Weg ist, `Build.sources` die Id mitfuehren zu lassen
(`model.py:996`) - das beruehrt auch `app.py`s Aufschluesselung und ist ein
eigener Auftrag. Der billige Weg, den Anspruch einer Kopie auf die Felder zu
beschraenken, die dieser Effekt erzeugen kann, waere eine **zweite Rechnung**
und stiesse gegen AD-015; das ist eine Entscheidung, keine Umsetzung.

---

### [P2 | Major | Mittel] Kein Waechter sieht es, wenn die Effekte einer Kopie doppelt in die Rechnung gehen (A4 Stacking)

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/evaluate.py:56-58` (`effect_ids_of`)
**Umgebung:** Standardlauf `pytest -q -m "not slow"`, unveraenderte Tests

**Reproduktion:**

1. In `effect_ids_of` die Zeile `ids.extend(candidate.effect_ids)` ein
   zweites Mal einfuegen - jede gewaehlte Kopie zaehlt damit doppelt.
2. Vollen Standardlauf fahren.

**Erwartet:** rot - A4 sagt zu, dass die bestehenden Regeln des Programms
respektiert werden, und jede Zahl des Beraters aendert sich.
**Tatsaechlich:** **952 passed, 9 skipped, 5 deselected in 467,27 s** -
identisch zum Ausgangslauf.

**Kein Aequivalent, gemessen:** ein Build aus einer Kopie mit
`Physical Attack Up +4` gibt statt `physicsAttackRate` 1,1200 den Wert
1,2544; `max_damage` steigt von 1,0240 auf 1,0509 (+2,6 %); `sources` traegt
den Eintrag zweimal. Die Begruendung zeigt trotzdem **eine** Zeile mit
`+12.0%` - auch sie deckt den Fehler nicht auf.

**Analyse:** Zwischen `Candidate` und `model.compute` liegt genau diese eine
Stelle, und keine Zusicherung im Baum spricht ueber die **Vielfachheit** der
uebergebenen Ids. `test_advisor_evaluate.py` prueft die Reihenfolge der drei
Quellen und die beiden Verweigerungen; die Frage "wie oft" stellt kein Fall.
Damit ist die A4-Klausel "nicht stapelbare Effekte werden nicht doppelt
gezaehlt" am Berater-Rand unbewacht - `model.compute` haelt sie, aber nichts
haelt fest, dass der Berater `model.compute` richtig fuettert.

**Auswirkung:** Ein spaeterer Umbau von `effect_ids_of` - etwa fuer die
Waffeneffekte oder fuer eine dritte Quelle - kann jede Beraterzahl still um
mehrere Prozent verschieben, und die Suite bleibt gruen. Das ist derselbe
Riss wie QA-001 an einer neuen Stelle.

**Vorschlag:** Ein Fall, der die Vielfachheit festhaelt statt der
Reihenfolge: die Id-Liste einer bekannten Belegung gegen eine unabhaengig
gebildete Multimenge stellen (gehaltene Rollen + gewaehlte Rollen +
Waffeneffekte, je genau einmal), dazu eine Mutation in
`scripts/differential/mutate.py`.

---

### [P3 | Minor | Mittel] `not_counted` darf Reihenfolge und Doppelnennungen verlieren, ohne dass ein Verhaltenstest anschlaegt

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/explain.py:344-362`
**Umgebung:** Standardlauf

**Reproduktion:**

1. `not_counted` durch ein `set()` fuehren, also Reihenfolge und Duplikate
   aufgeben. Die verankerte Quellzeile dabei **unangetastet** lassen (sonst
   antwortet nur die Ankerpruefung, siehe Abschnitt 5).
2. Vollen Standardlauf fahren.

**Erwartet:** rot - der Docstring sagt ausdruecklich "Duplicates are kept.
… `len(not_counted)` is the count AD-010 asks for", und die Reihenfolge ist
die, in der `model.compute` geparkt hat.
**Tatsaechlich:** **952 passed, 9 skipped, 5 deselected in 465,53 s** -
identisch zum Ausgangslauf.

**Analyse:** Die einzige Mutation auf dieser Zeile
(`explain-reports-a-declared-condition-as-uncounted`) nimmt den
`live`-Filter weg, prueft also eine andere Eigenschaft. Zahl und Ordnung der
Liste sind zugesagt und ungeprueft. Am echten Spielstand entstehen ueber alle
309 Relikte **199** solcher Eintraege, mit Doppelnennungen - ein Verlust waere
im `Why`-Dialog als falsche Anzahl sichtbar.

**Auswirkung:** klein heute, weil die Liste noch niemand anzeigt; genau
deshalb ist jetzt der billige Zeitpunkt.

**Vorschlag:** ein Fall, der zwei Relikte mit derselben unerfuellten
Bedingung waehlt und `len(not_counted) == 2` verlangt, dazu die Ordnung gegen
`built.situational`.

---

### [P3 | Minor | Hoch] Die Halte-Zeile ist grammatisch falsch, sobald genau ein Slot uebrig bleibt

**Adressat:** ui-ux-designer (der Wortlaut gehoert dir; das hier ist kein
Geschmack, sondern Kongruenz)
**Betroffen:** `nrplanner/advisor/explain.py:398-400`
**Umgebung:** jedes Gefaess, sobald `slots - held == 1`

**Reproduktion:** ein Problem mit 2 Slots, einer gehalten - oder 6 Slots,
fuenf gehalten - und `explain.unknowns(...)` lesen.

**Erwartet:** "so only the other 1 **was** filled." (oder eine Formulierung,
in der die Zahl nicht regiert).
**Tatsaechlich:** `1 of 2 slots is held, so only the other 1 **were**
filled.`

Alle elf moeglichen Fuellungen (2, 3 und 6 Slots) habe ich ausgegeben;
betroffen sind die drei mit einem verbleibenden Slot: 2/1, 3/2, 6/5.

**Analyse:** Die Singular-/Plural-Entscheidung wird auf `held` gebildet
(`one = held == 1`), das zweite Satzglied zaehlt aber `slots - held`.

**Auswirkung:** Nur Text - aber es ist der Satz, den jeder Lauf mit
Haltungen traegt, und A8 verlangt englische Oberflaechentexte, keine
fehlerhaften.

**Vorschlag:** zweite Kongruenz aus `slots - held` bilden, oder den Satz so
fassen, dass die Zahl nicht regiert.

---

### [P3 | Minor | Mittel] UI_SPEC 4.11 hat keinen Erzeuger: ein Slot ohne Auswahl bleibt unerwaehnt

**Adressat:** director (Zuschnitt: gehoert das nach S5, S8 oder S9?), dann
developer
**Betroffen:** `nrplanner/advisor/candidates.py:206-239` (`_pool_findings`
kennt drei Zeilen, keine fuer den leeren Pool); `nrplanner/advisor/types.py`
(weder `Suggestion` noch `AdvisorResult` traegt die Zahl der freien Slots)
**Umgebung:** ein Gefaess mit einer Farbe, von der der Spielstand nichts
besitzt

**Reproduktion:**

1. Inventar mit nur roten Relikten, Gefaess `[Rot, Blau]`.
2. `candidates.pools(...)` - Poolgroessen `[2, 0]`.
3. `search.beam(...)` - zwei Vorschlaege, jeder belegt **einen** Slot.
4. `pools[1].unknowns` und `explain.unknowns(...)` lesen.

**Erwartet** (UI_SPEC 4.11): `... 3 of 4 slots filled · 1 slot has nothing
to choose from.` und am Slot `No <colour> relic in your save fits this slot.`
**Tatsaechlich:** beide leer. Nichts unter `nrplanner/` sagt, dass ein Slot
leer blieb.

**Nenner der Absenz (L-013):** Volltextsuche ueber den ganzen Baum mit drei
unabhaengigen Masken - `slots filled` (7 Treffer: eine Docstring-Zeile in
`search.py:184`, eine Mutationsbeschreibung, `scripts/measure_advisor_search.py`,
ein Test-Docstring, `UI_SPEC.md` und zwei Berichte), `nothing to choose from`
und `fits this slot` (je 0 Treffer ausserhalb `UI_SPEC.md`). **Kein Erzeuger
in `nrplanner/`.**

**Analyse:** Der `beam` traegt den Zustand ueber einen leeren Slot hinweg -
das ist gebaut und richtig - aber die Nachricht darueber entsteht nirgends.
Ableitbar ist sie fuer S9 (`len(free_slots)` gegen `len(choices)`,
`pools[i].candidates == ()`), also ist es womoeglich Absicht, dass S8 sie
nicht schreibt. Entschieden ist es nirgends.

**Zweiter Weg in dieselbe Form, damit er nicht uebersehen wird:** ein
Vorschlag mit weniger Belegungen entsteht auch, wenn dem Zweig die Kopien
ausgegangen sind (`nrplanner/advisor/search.py:193-195`). Beide Faelle sehen
von aussen gleich aus. Auf diesem Spielstand tritt keiner auf (0 unbelegte
Slots in 296 Laeufen), bei kleinem K aber sehr wohl.

**Auswirkung:** Ohne die Zeile liest sich "5 von 6 Slots belegt" als Fehler
des Programms statt als Aussage ueber den Besitz - genau das, wogegen A7
geschrieben ist.

**Vorschlag:** Entscheiden, wo die Zeile entsteht. Wenn in S5: eine vierte
Zeile in `_pool_findings` bei leerem Pool. Wenn in S9: dann bitte
ausdruecklich in den S9-Auftrag, sonst faellt sie zwischen die Schritte.

---

## 4. Die vier Angriffswege aus dem Auftrag

### 4.1 Determinismus von `explain.py` ueber Prozessgrenzen - **haelt**

Aufbau wie `test_two_processes_under_two_hash_seeds_answer_the_same`: vier
Kindprozesse unter `PYTHONHASHSEED` 0, 1, 12345 und 424242, jeder faehrt
einen vollen Lauf auf `Wylder's Chalice` + Deep, beide Richtungen, und gibt
**alle** Ausgaben von `reasons`, `curses`, `not_counted`, `unknowns` und
`data_note` aus - 368 Zeilen. Vier Saaten, **eine** sha256.

Das ist eine Messung und keine Behauptung: mit einem einzigen `set()` in
`not_counted` liefern dieselben vier Saaten **vier verschiedene** Ausgaben
(erste Abweichung in Zeile 37). Die Probe kann also rot werden.

### 4.2 Gehaltenes `isStrongestEffect` neben einer vorgeschlagenen Kopie - **haelt, und die Kante ist auf diesem Spielstand unerreichbar**

Durch die ganze Kette gefahren (`candidates` -> `search` -> `explain`), nicht
nur durch `explain` wie der vorhandene Fall:

* Die Vorsortierung misst die gedeckelte Kopie mit **+0,000000** und stellt
  sie ans Ende des Pools.
* Der Beam setzt sie an die letzte Stelle; ihr Vorschlag hat **exakt** den
  Wert des Grundzustands.
* Zwingt man sie in den Slot, gibt `explain.reasons` **keine** Zeile, und die
  Punktzahl steigt nicht.

Der `developer` hat recht, dass das der schaerfste Fall ist. **Er ist auf
diesem Spielstand aber nicht erreichbar, und das ist neu:** von **338**
verschiedenen Effekt-Ids auf den 309 besessenen Relikten ist **keine**
nicht-stapelbar (im Datensatz sind es 84 von 2076). Es gibt auch **kein**
Paar besessener Kopien, das sich einen nicht-stapelbaren Effekt teilt. Der
Fall bleibt richtig gebaut, aber jeder Lauf gegen echte Daten geht daran
vorbei - wer ihn nachstellen will, braucht gebautes Material. Der reale
Vertreter derselben Fehlerklasse ("eine Kopie bekommt eine Zahl
gutgeschrieben, die sie nicht gebracht hat") ist Befund 1.

### 4.3 Die drei Kanten

**Leerer Pool:** gebaut (Inventar nur einer Farbe), Verhalten korrekt, aber
stumm - siehe Befund 5. **Auf dem echten Spielstand kommt ein leerer Pool
nicht vor:** ueber alle 74 Gefaesse x Deep an/aus = 296 Laeufe, **0** Pools
mit null Kandidaten; die kleinste Deep-Farbe traegt **21** Kopien. Die
Annahme des Auftrags ist damit widerlegt (siehe ANNAHMEN 2).

**Gefaess mit allen Slots gehalten:** korrekt. `pools` ist leer, der Beam
liefert **einen** Vorschlag ohne Belegungen, sein Wert ist der des
Grundzustands, und `unknowns` traegt
`All 2 slots are held, so nothing was searched: this is the build as it
stands, scored.` Auch wenn alle Slots **leer** gehalten sind (AD-014.7) kommt
dieselbe Zeile - der Build ist dann leer, und das ist konsistent.

**Abbruch zwischen zwei Ebenen:** korrekt an jeder Ebene. Bei drei Slots
wirft ein Abbruch nach 0, 1 und 2 Pruefungen je `Cancelled("stopped after N
of 3 slots")`; nach 3 Pruefungen laeuft der Lauf durch. Der Aufruf ist rein -
nach den drei Abbruechen liefert ein normaler Lauf wieder dieselbe Antwort,
dieselben Handles, denselben Wert. Kein Zustand bleibt liegen.

**Ergaenzend geprueft, weil billig:** K oder W auf 0 oder -1 wird laut
verweigert; K=1/W=1 liefert genau einen Vorschlag; K=10^6 und W=10^6 laufen
durch; ein Problem ganz ohne Slots gibt den Grundzustand; zweimal derselbe
Pool wird mit der Slot-Liste im Text verweigert; ein `Suggestion` ist hashbar
und zwei Laeufe liefern gleiche Objekte.

### 4.4 D-2 nachgezaehlt - **die Zahl stimmt**

Ich habe **nicht** den Zaehlweg des `developer` wiederholt, sondern die Frage
von der anderen Seite gestellt: jedes besessene Relikt einzeln in einen
echten Ein-Slot-Lauf gesetzt, **alle** Zeilen erzeugt, die `explain.py`
erzeugen kann (`reasons`, `curses`, `not_counted`, `unknowns`, beide
Richtungen), und geprueft, ob der Fluchname darin vorkommt.

**Nenner:** 309 besessene Relikte, davon **76** mit mindestens einem Fluch,
zusammen **112** Fluchrollen; **0** Fluch-Ids, die dieser Datensatz nicht
kennt.

**Ergebnis: 36 von 309 Relikten** tragen einen Fluch, den das Ergebnis
nirgends nennt - **genau die Zahl aus T-067**. Meine Zaehlung liefert
zusaetzlich: **40 von 112 Fluchrollen** sind stumm (vier Relikte tragen
zwei), und die Aufschluesselung deckt sich Zeile fuer Zeile mit der des
`developer`: Madness 9, Sleep 7, Rot 6, Poison 5, Frost 5, Blood Loss 4,
Death 1, `All Resistances Down` 3.

**Auf einem anderen Spielstand ist es eine andere Zahl** - uebertragbar ist
der Anteil: **32 %** der Fluchrollen dieses Bestandes und **47 %** der
Relikte, die ueberhaupt einen Fluch tragen.

---

## 5. Was ausserdem aufgefallen ist (nicht im Auftrag)

**Eine Methodenfalle fuer jeden, der hier Gegenbauten faehrt.**
`tests/test_differential_track.py::test_every_mutation_still_finds_its_anchor_in_the_real_source`
wird rot, sobald man eine **verankerte** Quellzeile aendert - auch wenn kein
Verhalten geprueft wurde. Mein erster Lauf gegen `not_counted` meldete
"1 failed" und war damit scheinbar toedlich; der einzige rote Fall war die
Ankerpruefung. Wer L-008 in diesem Baum anwendet, muss ansehen, **welcher**
Fall rot wurde, nicht nur den Exitcode - genau L-003. Der `developer` ist dem
nicht aufgesessen: er hat gegen die beiden Advisor-Testdateien gefahren, die
diese Pruefung nicht enthalten. Sein Wort "Standardlauf" meint dort diese
beiden Dateien, nicht `pytest -q -m "not slow"`.

**D-4 ist teuer, nicht nur theoretisch.** Der `developer` meldet, dass
`SlotPool` seine Sortierrichtung nicht mitfuehrt und `beam` sie nicht pruefen
kann. Gemessen auf `Wylder's Chalice` + Deep, Standardbudget, Scorer
`max_damage`: mit richtig sortierten Pools **Attack rating 323,30**, mit
Pools aus `min_damage_taken` **290,39** - **10,2 % schlechter**, gleiche
Form, gleiche Zahl an Vorschlaegen, **keine Beschwerde**; vier der sechs
Handles sind andere. Das ist die Groessenordnung, um die es bei der
Entscheidung geht.

**Zwei Zeilenformen, die dem `ui-ux-designer` gehoeren.** (a) Ein
bewegungsgebundener Buff verliert seine Feldbezeichnung und liest sich als
`Slot 6, Deep Grand Drizzly Scene — Improved Thorn Sorcery: +12.0%` - "12 %
wovon" steht nicht da. (b) Die laengste Zeile ueber 10 322 gemessene Zeilen
hat **150 Zeichen** (`Slot 1, Grand Drizzly Scene — [Recluse] Improved Vigor,
Endurance, and Dexterity, Reduced Intelligence and Faith: Intelligence -10,
counted against it`); UI_SPEC §3.2 nennt 160 als Grenze fuer **einen Satz je
Slot**, und je Slot stehen bis zu sieben solcher Zeilen. Zahl je Vorschlag:
**4 bis 42, Median 17** (592 Vorschlaege).

**Ein Vorschlag darf heute den Wert des Grundzustands haben.** Im Fall aus
4.2 ist der dritte Vorschlag exakt so gut wie "nichts einsetzen" und traegt
null Begruendungszeilen. Ob so etwas auf den Schirm darf, ist eine
S9/S10-Frage, keine von S7.

**Feindlicher Text - kein Befund, eine Notiz fuer S10.** Reliktnamen gehen
ungefaltet in die Zeile, Effektnamen gefaltet. Im Datensatz tragen **124 von
711** Effektnamen einen Zeilenumbruch - die werden gefaltet, und ueber 309
Relikte kam **kein** Umbruch in `not_counted` an (199 Eintraege geprueft).
Reliktnamen: **0 von 77** im Datensatz und **0 von 57** auf dem Spielstand
tragen Umbruch, Geviertstrich oder `": "`. Ein selbst benanntes
Custom-Relikt koennte das - es wird aber gehalten und nie vorgeschlagen, also
heute nicht erreichbar.

**Fluch-Namenskollisionen, zur Reichweite von Befund 1.** Auf diesem
Spielstand kollidiert **kein** Fluchname mit einem anderen (24 von 24
eindeutig), und **kein** Name tritt zugleich als Fluch und als Nicht-Fluch
auf. Im Datensatz tun das **10** Namen. Ein Spielstand, der zwei davon
besitzt, haette dieselbe Fehlzuordnung in `curses()` und in der
AD-015-Pflichtzeile. Heute nicht reproduzierbar, deshalb kein eigener Befund.

---

## 6. Explorationsprotokoll - was gehalten hat

Damit "keine Befunde" von "nicht geprueft" unterscheidbar bleibt. Alles
folgende habe ich angegriffen und **nicht** brechen koennen:

* **Farbregel und Deep-Trennung** ueber 296 + 1036 Laeufe, mit und ohne
  Haltungen, gegen `inventory.relics_for` gegengerechnet - 0 Verstoesse; die
  Probe meldet unter einem Gegenbau 315.
* **Eine Kopie liegt in einem Slot**, auch ueber weisse Slots und
  Deep-Gruppen hinweg - 0 Verstoesse in 4440 Vorschlaegen.
* **Jeder vorgeschlagene Handle ist eine wirklich besessene Kopie**, Name und
  `relic_id` stimmen mit dem Spielstand ueberein - 0 Abweichungen.
* **Jeder freie Slot wird belegt**, wenn der Pool etwas hergibt - 0
  unbelegte Slots in 296 Laeufen.
* **Beide Zielrichtungen** liefern fuer jedes der 74 Gefaesse Vorschlaege.
* **Gehaltene Slots** werden nie befuellt und der Halte-Satz fehlt in keinem
  der 1036 Laeufe.
* **Determinismus** ueber vier Prozesse (4.1) und innerhalb eines Prozesses
  (zwei Laeufe liefern gleiche Objekte).
* **Abbruch, Budgetgrenzen, doppelte Pools, Problem ohne Slots** (4.3).
* **Der gedeckelte `isStrongestEffect`** (4.2).
* **Neun von elf Gegenbauten** gegen die Abnahmeklauseln werden rot, mit je
  benanntem Fall.

---

## 7. Offene Fragen

| # | Frage | An wen |
|---|---|---|
| 1 | Darf ein Vorschlag ausgeliefert werden, der fuer einen belegten Slot **keine** Begruendung traegt - oder ist das ein Auslieferungshindernis? (Befund 1) | director |
| 2 | Traegt `Build.sources` kuenftig die Effekt-Id? Das ist der einzige Weg, der ohne zweite Rechnung auskommt, und er beruehrt `model.py` und `app.py`. (Befund 1) | director, dann developer |
| 3 | Wo entsteht die Zeile aus UI_SPEC 4.11 - S5, S8 oder S9? Heute nirgends. (Befund 5) | director |
| 4 | Ist es Absicht, dass `SlotChoice` weder Farbe noch `is_deep` traegt, waehrend `Candidate` beides hat? A4 nennt die Deep-Kennzeichnung ausdruecklich; S10 muesste sie ueber den Handle nachschlagen und braeuchte dafuer die Pools des Laufs, die `AdvisorResult` nicht mitfuehrt | director, developer |
| 5 | D-4: 10,2 % schlechtere Antwort ohne jede Beschwerde - reicht das fuer ein `rank_by` auf `SlotPool`? | director |

---

## 8. Nicht geprueft

* **S9, S10, S11** - existieren nicht. Damit auch **A6** (Hintergrundlauf,
  Antwortzeit) und **A9** (Lauf gegen ein gebautes Artefakt) nicht.
* **Laufzeit** - gehoert dem `performance-tuner`. Ich habe die Zahlen aus
  T-067 nicht nachgemessen und mich fuer meine eigenen Laeufe bewusst auf
  kleine Budgets gestuetzt; die Invarianten, die ich pruefe, haengen nicht am
  Budget (die eine Ausnahme steht in Abschnitt 2).
* **Die Wortlaute der vier neuen Satzarten** - Auftragsgrenze. Den
  Kongruenzfehler in Befund 4 melde ich als Defekt, nicht als
  Formulierungsvorschlag.
* **A8 (alle Texte Englisch)** - kein Waechter im Baum, aber auch nicht mein
  Auftrag; steht schon als bekannte Luecke.
* **Ein zweiter Spielstand** - alle Zahlen gelten fuer `USER_DATA000` mit 309
  Relikten. Besonders 4.2 (kein nicht-stapelbarer Effekt im Besitz) und D-2
  sind bestandsabhaengig.
* **Linux und macOS**, wie in T-067.

---

## 9. Zusammenfassung an den `director`

**Befunde: 2x P2 (Major), 3x P3 (Minor).** Keine Blocker, keine
Datenverluste, keine Rechtefrage. **Die Rangzahlen des Beraters sind in
keinem meiner Laeufe falsch gewesen** - A3 und A4 halten in der Sache ueber
alle 10 Nightfarer und alle 74 Gefaesse.

**Releasefaehig ist das noch nicht, und der Grund ist A5.** Die Begruendung
ist der Teil, den der Spieler liest und gegen das Spiel pruefen kann, und sie
schreibt heute auf einem von fuenf Vorschlaegen eine Zahl aufs falsche Relikt
und laesst auf jedem achten besten Vorschlag einen Slot unerklaert. Das
mindeste vor S9/S10: **Befund 1 entschieden** (Frage 1 und 2) - solange
`Build.sources` nur Namen fuehrt, kann keine Oberflaeche daraus etwas
Richtiges bauen. **Befund 2** ist kein Fehler von heute, aber die Stelle, an
der der naechste entsteht, und er kostet einen Testfall.

## 10. QA-Log - Zeilen fuer `qa/findings.md`

Ohne Nummern, wie im Auftrag verlangt; die Ids vergibt der `director`. Format
wie die vorhandenen Zeilen; einzufuegen hinter QA-179.

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| (neu) | **Die Begruendung ordnet Effekte gleichen Namens dem falschen Relikt zu; ein belegter Slot bleibt ganz ohne Zeile.** `explain._attributed` (`explain.py:153`) sucht Eintraege in `Build.sources` ueber den Effekt**namen**; `model.py:996` legt dort keine Id ab. Zwei Ids mit einem Namen (`7000090` = Vigor +5 und `6610400` = Max HP +10 %, beide `Increased Maximum HP`) werden zu einem Effekt: die in Slot-Reihenfolge erste Kopie nimmt beide Felder, die zweite bekommt nichts. Gemessen am echten Spielstand: **130 von 10 322** Zeilen nennen eine Groesse, die der genannte Effekt nicht bewegt, verteilt auf **112 von 592** Vorschlaegen; **23 von 296** besten Vorschlaegen haben einen Slot ohne jede Zeile, und **alle 23** haben die Rangzahl wirklich bewegt (137-184 EHP, im nachgerechneten Fall der groesste Einzelbeitrag des Builds). Reichweite: **160 von 707** Effektnamen im Datensatz auf mehr als einer Id, **48** davon mit anderen Modifier-Feldern; **52 von 309** besessenen Relikten betroffen. **Die Rangzahl ist nicht betroffen** - nur die Begruendung, also genau A5. Der Abnahmefall `test_the_reasons_name_only_effects_the_suggestion_brought` kann es nicht sehen, weil er ebenfalls ueber Namen prueft | P2 | Major | developer | Minimalfall ohne Suche im Bericht, plus Rundlauf ueber 10 Nightfarer x 74 Gefaesse, gegengerechnet gegen `model.compute` | offen | 2026-09-06 |
| (neu) | **Kein Waechter sieht doppelt gezaehlte Effekte einer Kopie (A4 Stacking).** Wird `ids.extend(candidate.effect_ids)` in `advisor/evaluate.py:56-58` ein zweites Mal ausgefuehrt, laeuft der volle Standardlauf mit **952 passed** durch - identisch zum Ausgangslauf. Kein Aequivalent: `physicsAttackRate` steigt von 1,1200 auf 1,2544, `max_damage` um 2,6 %, und `sources` traegt den Eintrag zweimal; auch die Begruendung zeigt nur eine Zeile. `test_advisor_evaluate.py` prueft die Reihenfolge der drei Quellen, nie die Vielfachheit | P2 | Major | developer | ueberlebender Gegenbau im vollen Standardlauf (467 s), plus Zahlenvergleich | offen | 2026-09-06 |
| (neu) | **`not_counted` darf Reihenfolge und Doppelnennungen verlieren, ohne dass ein Verhaltenstest anschlaegt.** Der Docstring sagt "Duplicates are kept … `len(not_counted)` is the count AD-010 asks for"; die einzige Mutation auf der Zeile prueft den `live`-Filter, nicht Zahl und Ordnung. Voller Standardlauf unter dem Gegenbau: **952 passed** (465 s). Am echten Spielstand entstehen ueber 309 Relikte 199 solcher Eintraege | P3 | Minor | developer | Gegenbau ueber der verankerten Zeile, voller Standardlauf | offen | 2026-09-06 |
| (neu) | **Die Halte-Zeile ist grammatisch falsch, sobald genau ein Slot uebrig bleibt.** `explain.py:398-400` bildet die Kongruenz auf `held`, zaehlt im zweiten Satzglied aber `slots - held`: `1 of 2 slots is held, so only the other 1 were filled.` Betrifft 3 der 11 moeglichen Fuellungen (2/1, 3/2, 6/5) | P3 | Minor | ui-ux-designer | alle 11 Fuellungen ausgegeben | offen | 2026-09-06 |
| (neu) | **UI_SPEC 4.11 hat keinen Erzeuger.** Ein Slot, dessen Pool leer ist, wird korrekt uebersprungen, aber weder `SlotPool.unknowns` (`_pool_findings` kennt drei Zeilen, keine dafuer) noch `explain.unknowns` sagt etwas darueber, und weder `Suggestion` noch `AdvisorResult` traegt die Zahl der freien Slots. Volltextsuche mit drei Masken (`slots filled`, `nothing to choose from`, `fits this slot`): **kein Erzeuger in `nrplanner/`**. Auf diesem Spielstand tritt der leere Pool nicht auf (0 in 296 Laeufen, kleinste Deep-Farbe 21 Kopien); dieselbe Form entsteht aber auch, wenn einem Zweig die Kopien ausgehen (`search.py:193-195`) | P3 | Minor | director, developer | leerer Pool gebaut, Verhalten gemessen, Absenz mit drei Suchmasken belegt | offen | 2026-09-06 |
