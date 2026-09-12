STATUS: erledigt
AUFTRAG: T-056 — Spec: die sechs Tabs so festlegen, dass ein Spieler sie versteht
GELESEN: docs/tasks/T-056.md · docs/tasks/T-054.md · GOAL.md (A10 bis A14, Abschnitt „Erweiterung des Zielbilds", Nutzer 2026-09-05) · docs/berichte/T-055-qa-engineer.md (vollstaendig, 1353 Zeilen, QA-125 bis QA-139) · docs/state.md · DESIGN_REVIEW.md (DR-008 bis DR-012) · UI_SPEC.md (vollstaendige Struktur, AK-63 bis AK-67 im Wortlaut) · CLAUDE.md · Quellcode nrplanner/{effectstab,arsenaltab,bosstab,deeptab,depthstab,eventstab,eventlore,datasource}.py · eigene Screenshots docs/screenshots/2026-09-05-T056/ (neu erzeugt) und docs/screenshots/2026-09-05/ · Agent-Memory (project_nightreign_helper, feedback_headless_verification). — **NICHT gelesen, weil nicht vorhanden: `docs/berichte/T-054-power-user.md`** (siehe „Fehlende Quelle" unten).
GEÄNDERT: UI_SPEC.md (neuer Abschnitt am Dateiende, AK-68 bis AK-105; bestehende Abschnitte byteweise unveraendert, geprueft per diff) · DESIGN_REVIEW.md (neuer Abschnitt oben, DR-013 bis DR-018; alter Inhalt byteweise unveraendert, geprueft per diff) · docs/berichte/T-056-ui-ux-designer.md (diese Datei) · docs/screenshots/2026-09-05-T056/ (18 neue PNG). Kein Anwendungscode, kein Test, kein Git-Zustand veraendert (kein add, commit, push, checkout, reset, stash).
ANNAHMEN: (1) Die drei Beobachtungen des `power-user`, die T-056 zitiert, sind korrekt wiedergegeben — ich konnte sie nicht am Original pruefen, weil der Bericht fehlt. Jede darauf gestuetzte Vorgabe traegt zusaetzlich eine eigene Messung oder einen eigenen Screenshot; keine haengt allein am Zitat. (2) Die Messungen von T-055 (QA-125 bis QA-139) habe ich nicht nachgefahren, sondern uebernommen und im Text als *(QA)* gekennzeichnet. (3) Bei zwei Bezugsgroessen (`… buildup`, `Sovereign Sigil`) weiss ich nicht, ob der Extraktor die Bezugsgroesse kennt; die Vorgabe legt deshalb beide Faelle fest, statt einen zu raten.
NÄCHSTER: director — er legt dem App Designer die fuenf offenen Fragen und die dreizehn Streichvorschlaege vor. Danach `developer` (Umsetzung AK-68 bis AK-105), dann `qa-engineer` (A14 je Tab einzeln).
BLOCKIERT DURCH: nichts. Ein Vorbehalt: `docs/berichte/T-054-power-user.md` fehlt, und `docs/state.md` fuehrt T-054 als „geschrieben" — die Diskrepanz gehoert dem `director`.

---

# T-056 — Vorgabe fuer die sechs Inhalts-Tabs

Rolle: `ui-ux-designer`, **Spec-Modus** · Zyklus 13 · 2026-09-05
Nummernkreise: **AK-68 bis AK-105** (`UI_SPEC.md`), **DR-013 bis DR-018**
(`DESIGN_REVIEW.md`)

## Fehlende Quelle — der wichtigste Satz dieses Berichts

`docs/berichte/T-054-power-user.md` **existiert nicht.** Geprueft, nicht
vermutet, mit vier unabhaengigen Zugriffen auf den aktuellen Bestand:

- `find . -iname "*054*"` → nur `docs/tasks/T-054.md` (der Auftrag).
- `find . -iname "*power*user*"` → nichts.
- `git ls-files --others --exclude-standard | grep -i 054` → nur der Auftrag.
- `git log --all --oneline -- "*T-054*"` → leer; `git stash list` → ein
  Stash von 2026-09-02, unbeteiligt.
- Volltextsuche nach `power-user` in allen `.md` → elf Treffer, alle
  Erwaehnungen in Auftraegen, Registern und `docs/state.md`, **keiner** ein
  Bericht.

`docs/state.md:64` fuehrt T-054 als „geschrieben". Das ist mit dem
Dateisystem nicht vereinbar; die Aufloesung gehoert dem `director`.

**Folge fuer diesen Auftrag.** T-056 nennt den `power-user`-Bericht „die
wichtigste Quelle dieses Auftrags", weil er die einzige Aussage darueber
enthaelt, was ein Mensch tatsaechlich verstanden hat. Diese Quelle hatte ich
nicht. Was ich hatte, waren die **drei Zitate daraus in T-056 selbst** — und
die habe ich als *(zweiter Hand)* behandelt: keine einzige Vorgabe unten
stuetzt sich allein auf sie. Jede steht zusaetzlich auf einer Messung des
`qa-engineer` oder auf einem eigenen Screenshot vom laufenden Fenster.

Was dadurch **fehlt** und der naechste Durchlauf braucht: A11 („kein 'ich
habe nicht verstanden' mehr") ist nicht nachweisbar, solange kein
`power-user`-Bericht vorliegt. Die Vorgaben unten sind gegen A10, A12 und
A13 gebaut und pruefbar; A11 bleibt offen und braucht einen zweiten
`power-user`-Lauf **nach** der Umsetzung.

## Methode und was davon gesehen ist

Das Fenster war live steuerbar (`.venv\Scripts\python.exe run.py`, Titel
`Nightreign Helper 1.7.1`). Tabwechsel und Sucheingabe ueber
`UIAutomationClient`, Kartenklick per `SendMessage`, Screenshots nach
`SetProcessDPIAware()` — ohne diesen Aufruf sind auf diesem Rechner
(150 % Skalierung) alle Fenstermasse falsch. Zusaetzlich headless gemessen
(`QT_QPA_PLATFORM=offscreen`, echte Spieldaten): Spaltenbreiten der
Effektetabelle bei drei Fensterbreiten, `minimumSizeHint()` aller sieben
Tab-Seiten, Roster- und Mutationsstruktur des Red-variants-Datensatzes.

18 Screenshots unter `docs/screenshots/2026-09-05-T056/`, **jeder einzeln
mit dem Read-Werkzeug geoeffnet und angesehen**. Drei weitere Aufnahmen sind
entstanden und wurden geloescht statt abgelegt, weil sie nicht zeigten, was
ihr Name behauptete — Begruendung in §8.

Vier Beweisklassen, im `UI_SPEC.md`-Abschnitt je Aussage mitgefuehrt:
*(visuell)*, *(gemessen)*, *(QA)*, *(zweiter Hand)*.

---

## 1. Je Tab: die Frage, und wo dieser Satz steht

Alle sechs bekommen dasselbe Kopfmuster (**AK-68**): `_heading()` in
`#c8a45c`/12 px/bold/letterspacing, GROSSBUCHSTABEN, darunter **ein**
Fragesatz in `#8a8a8a`/11 px mit `setWordWrap(True)` — **oberhalb jedes
Bedienelements und jeder Zahl**. Drei Tabs haben das Muster heute schon und
haben es vorgemacht; drei oeffnen heute mit einer Bestandszaehlung in Grau.

| Tab | Ueberschrift | Fragesatz (englisch, wortgleich) | heute |
|---|---|---|---|
| **Effects & chances** | `WHAT A RELIC CAN ROLL, AND HOW OFTEN` | `Every effect a relic can carry, how likely you are to roll it, and whether carrying a second copy is worth anything.` | keine Ueberschrift, oeffnet mit `577 buffs (blue) then 75 curses (red)…` |
| **Weapons & spells** | `WHICH ARMAMENT HITS HARDEST FOR YOUR BUILD` | `Every armament and spell in the game, rated for the Nightfarer, level and upgrade set above. Spell damage is not in the game's data, so spells show what they cost you instead.` | keine Ueberschrift, oeffnet mit `Wylder at level 1, +1 — VIG 10 …` |
| **Nightlords** | `HOW TO HURT EACH NIGHTLORD` | `What each Nightlord takes extra damage from, what breaks its stance, and what it does to you once it is broken. Click a card for the full profile.` | keine Ueberschrift, oeffnet mit `10 Nightlords · 8 also have …` |
| **Deep of Night** | `DEEP OF NIGHT` (neu, ueber den vier vorhandenen) | `What a deeper run pays you, what it costs you, and how your Depth rating moves. All figures compare a Deep of Night run with a normal expedition.` | vier Frage-Ueberschriften, kein Dach; der zweite Satz schliesst zugleich QA-128 Punkt 9 |
| **Red variants** | `RED VARIANTS: WHAT THEY ARE, AND HOW MANY` | `A red variant is the same enemy made stronger — never a different enemy. The game's files do not say by how much. What they do say is how many of each sort a run places on a map, and that is the table below.` | `RED VARIANTS BY DEPTH` — kuendigt Stueckzahlen an, obwohl die Antwort auf „was ist anders" im Nebensatz darunter steht |
| **World Events** | `WORLD EVENTS` (unveraendert) | der heutige Absatz erfuellt AK-68 bereits und bleibt wortgleich | erfuellt |

Der Ort ist in allen sechs Faellen derselbe: **die ersten beiden Zeilen des
Tabs**, vor Filter, Suche und Bestandszaehlung. Ein Test, der den ersten
sichtbaren Textknoten jedes Tab-Widgets ausliest, findet dort die
Ueberschrift.

### Die drei Punkte, an denen der Auftrag mir die Richtung vorgegeben hat

**`Pools` — entschieden: der Name verschwindet, in beiden Ausgaengen
(AK-78).** Die Spalte heisst nirgends mehr `Pools`, und die Zeichenkette
*„A pool is one of the lists a relic's effects are drawn from"* kommt im
Baum nicht mehr vor. Ich **schlage die Streichung vor** (Ausgang A) und lege
den Ausgang B (Umbenennung auf `Relic slots`, neuer Tooltip) verbindlich mit
fest, weil die Streichung selbst dem App Designer gehoert. In beiden Faellen
wandert die einzige heute tragende Funktion der Spalte — die `0` als Signal
„unter diesen Filtern nicht erreichbar" — in die Chance-Zelle, die dafuer
bereits einen Tooltip besitzt. Der Zustand „steht da und heisst falsch"
endet mit AK-78 unabhaengig davon, wie er entscheidet.

**`Red variants` — geprueft, ob die Daten die Frage hergeben. Sie tun es
nicht, und der Tab sagt das jetzt.** Gemessen am Datensatz:
`deep_of_night.mutations` traegt je Eintrag nur `id`, `counts` (fuenf
Tiefen), `category`, `group`, `varies` — **keine Staerkefaktoren, keine HP-
oder Schadenszahlen**; `deep_of_night.kinds` traegt Roster ohne
Kartendimension. Die Daten sagen nicht, **um wie viel** staerker eine rote
Variante ist. Was sie sagen, steht heute schon auf dem Tab, nur im Nebensatz
eines grauen Absatzes: *„the same enemy, stronger, never a different one"*,
plus die community-berichtete Zeile *„red enemies always drop a weapon, and
red mini-bosses are guaranteed a unique-tier armament"*. AK-98 hebt genau das
in den Fragesatz und laesst die Ueberschrift beides ankuendigen — was sie
sind **und** wie viele. Die ehrliche Grenze steht im selben Satz: *„The
game's files do not say by how much."* Keine neue Funktion, nur eine
Umstellung.

**`Avg chance` — ich entscheide die Wahrheitsfrage, ich reiche die
Darstellungsfrage weiter.** Objektiv und damit meine Entscheidung: Die
heutige ungewichtete Mittelung ueber (Farbe x Modus)-Eimer wird nicht
ausgeliefert (AK-79); auf dem Bildschirm steht **genau eine** Definition, an
**genau einer** Stelle, sie nennt die Bezugsgroesse *„per relic effect
slot"*, sie sagt, dass die Filter darin stecken, und sie sagt, dass die Zahl
nicht pro Relikt und nicht pro Lauf gilt; der angezeigte Mittelwert ist nach
Vorkommen gewichtet, pruefbar an QA-126s Einzelfall (`0,91 %`, nicht
`20,4 %`, AK-80). Damit verschwinden auch die zwei widersprechenden
Definitionen, die heute gleichzeitig auf demselben Bildschirm stehen, und
der Satz *„of the selected colour and mode"*, den die Voreinstellung
`All colours` bereits widerlegt.

**Nicht meine Entscheidung**, und deshalb Frage 1 an den App Designer: ob
danach **zwei** Spalten stehen (gewichteter Mittelwert + bester Fall) oder
**eine** Spannenspalte (`0.5 – 100 %`). Beide sind nach AK-79/AK-80 ehrlich.
Der Grund, warum ich hier nicht selbst waehle: die Spanne ist keine
Genauigkeitsfrage, sondern eine Aussage darueber, wofuer der Tab da ist — ein
Nachschlagewerk vertraegt einen Mittelwert, ein Farm-Planer braucht die
Spanne. Was der App Designer will, kann ich nicht messen. **Meine Empfehlung
ist die Spanne**, weil die Streuung real ist (Faktor bis 22 im gemessenen
Einzelfall) und weil eine Spalte weniger genau die Breite freimacht, die dem
Effektnamen heute fehlt.

---

## 2. Streichliste je Tab

Vollstaendig mit Begruendung in `UI_SPEC.md` §8. Hier die Kurzfassung; jeder
Eintrag traegt dort den Satz „wenn das weg ist, verliert ein Spieler …".
**Vorschlaege, keine Entscheidungen** (GOAL A10).

**Effects & chances**
1. Spalte `Pools` → *verliert nichts Benutzbares*; das 0-Signal zieht um.
2. Spalte `Copies` (638 von 652 Zeilen zeigen `1`) → *verliert die
   Information, dass 14 Effekte mehrfach definiert sind — aendert an keiner
   Rolle etwas.*
3. Spalte `Type` (2 Werte, die die Textfarbe schon sagt) → *verliert die
   Gruppierung von Buffs und Fluechen* — nur streichen, wenn die
   Gruppierung anders erhalten bleibt.
4. Spalte `Colours` auf vier Farbpunkte kuerzen (491 von 652 Zeilen zeigen
   dieselbe Zeichenkette in 295 px) → *verliert nichts; die Breite geht an
   den Effektnamen.*

**Weapons & spells**
1. Die doppelte Kopfzahl bei einschichtigen Waffen (655 von 1 792 Kacheln
   drucken `AR 49` und darunter `Physical 49`) → *verliert nichts.*
2. Zeile `Slots` auf Zauberkacheln (160 von 160 zeigen `1`) → *verliert
   nichts, bis es je einen Zauber mit zwei Plaetzen gibt.*
3. **Nicht streichen: `vs standard`** — die einzige Zeile, die den
   Unterschied zur Standardfassung beziffert.

**Nightlords**
1. Der Klammerzusatz `(smallest Harmonia 75, largest Caligo 160)` auf allen
   zehn Panels → *verliert die Skala fuer `Bar to break`* — einmal an den
   Tabkopf, nicht zehnmal ins Panel.
2. `Stacks: yes — repeats compound` und `harder to stagger` (auf jedem Boss
   identisch, ersteres ohne Datengrundlage) → *verliert die Aussage, dass
   Buffs sich stapeln* — gehoert einmal in den Tabkopf.
3. Abschnitt `BODY PARTS`, solange `PART_NAMES` leer ist → *verliert die
   Information, dass ein Boss gepanzerte Stellen hat — die er ohne
   Koerperteilnamen ohnehin nicht anwenden kann.*
4. **Nicht streichen: der `EVERDARK`-Block** — „identisch" ist geprueft und
   wahr fuer 8 von 8.

**Deep of Night**
1. Die Zeile `Win` mit fuenf identischen `+200` → *verliert nichts; ein Satz
   sagt dasselbe und sagt zusaetzlich, dass es nicht von der Tiefe abhaengt.*
2. `Cursed relic — Uncommon` / `— Rare` aus der Tiefentabelle → *verliert
   zwei echte Zahlen* — also verschieben, nicht loeschen.
3. `Map concealed` und `Nightlord obscured` als zwei Zeilen → *verliert die
   Unterscheidung, welches von beidem passiert* — eine Zeile plus die
   vorhandene Note sagt mehr auf weniger Platz.

**Red variants**
1. Spalte `For example` in ihrer heutigen Form → *verliert nichts Korrektes*
   — sie ist fuer die groesste Zeile leer und fuer die uebrigen kartenblind.
2. Zwei der fuenf Tiefenspalten → *verliert die Moeglichkeit, „Depth 3"
   direkt nachzuschlagen* — deshalb zusammenfassen (`Depth 2–3`,
   `Depth 4–5`) statt streichen.
3. **Nicht streichen: `Night bosses (unconfirmed)`** — das ist A7, wie es
   aussehen soll.

**World Events**
1. `Can fire on Day 1 or Day 2.` in seiner heutigen Form (wortgleich auf
   11 von 11) → *verliert nichts — erst wenn auch die Tagesverteilung
   wegbliebe, die heute schon verworfen wird.*
2. Die Quellennamen in den `Sources disagree`-Bloecken → *verliert nichts,
   was er benutzen kann; „hier widersprechen sich die Quellen" bleibt.*
3. **Nicht streichen: `Every other Nightlord: never.`** → *verliert die
   Zusicherung, dass die Liste vollstaendig ist* — wertvoll, aber nur mit
   ihrem Geltungsbereich (AK-102).
4. **Nicht streichen: `WHAT THE DEMON CAN DO`** — der einzige Ort im
   Programm, an dem eine Spielentscheidung mit sieben Ausgaengen vollstaendig
   aufgelistet ist.

---

## 3. Was ich am laufenden Fenster gefunden habe und niemand sonst finden konnte

T-056 stellt fest, der `power-user` konnte den Bildschirm nicht sehen, und
der `qa-engineer` hat A13 ausdruecklich nicht geprueft. Vier Befunde, alle
neu, alle mit Screenshot, alle in `DESIGN_REVIEW.md` als DR-013 bis DR-018:

- **Zwei von zehn Nightlords sind bei 1600 px Fensterbreite nicht
  sichtbar** (DR-013). Das Kartenraster ist auf `COLUMNS = 4` fest
  verdrahtet, das Detailpanel daneben auf `setFixedWidth(330)`, beide in
  einer `QHBoxLayout` — kein Splitter. Spalte 3 (Gnoster, Caligo) bricht
  mitten im Satz ab, Spalte 4 (**Maris**, **Harmonia**) fehlt ganz, waehrend
  die Kopfzeile „10 Nightlords" sagt. Bei 2100 px erscheinen beide.
- **Alle 652 Effektnamen sind abgeschnitten** (DR-014). Gemessen bei 1516 px
  Tabellenbreite: `Effect` **22 px**, `What it does` **21 px** — zusammen
  2,8 % der Breite. Die uebrigen 1473 px gehen an Spalten mit 2, 4, 9 bzw.
  10 verschiedenen Werten. Vier Zeilen hintereinander lesen sich als
  `Successful …` und sind nicht auseinanderzuhalten.
- **Das Fenster passt auf diesem Bildschirm nicht ueber die Taskleiste**
  (DR-015). Mindesthoehe **1606 physische px** gegen 1552 nutzbare.
  Verursacher ist **ein einziger Tab**: `Deep of Night` meldet
  `minimumSizeHint().height() = 949`, die anderen fuenf 111 bis 443 — vier
  Tabellen mit fester Hoehe, kein Scrollbereich. Folge: die letzten beiden
  Erklaerzeilen des Tabs sind nie sichtbar und **nicht erreichbar**, und
  jede Bildlaufleiste an einer Tab-Unterkante liegt hinter der Taskleiste
  (das ist der Grund, warum DR-013 nicht durch Scrollen zu heilen ist).
- **Die letzte Waffenkachel jeder Zeile ist abgeschnitten, und weil die
  Werte rechtsbuendig stehen, verschwinden die Zahlen zuerst** (DR-016a):
  auf der abgeschnittenen Kachel steht `AR`, `Physical`, `Magic` — ohne
  einen einzigen Wert. Dazu (DR-016b) bricht ein langer Wert mitten im
  Begriff um: `STR -7 · ARC +45 · DEX` / `-7`.

**Korrektur an meiner eigenen frueheren Vorgabe, ausdruecklich.** In T-052
habe ich die Arsenal-Kachel im Abschnitt „Positiv / beibehalten" als Vorbild
gegen DR-009 gelobt („Bezeichnung und Wert in getrennten, gestapelten
Zeilen"). Das war fuer den damals geprueften Fall richtig (`Spell power` /
`145`, ein kurzer Wert) und ist als **allgemeine Regel falsch**: dieselbe
Kachel bricht bei langen Skalierungswerten genauso mitten im Begriff um wie
die Kachel, gegen die ich sie gelobt habe. AK-73 ersetzt das Lob durch eine
Regel, die beide Faelle deckt. Das Lob bleibt als Einzelfallbefund stehen,
taugt aber nicht mehr als Muster.

Ausdruecklich **kein** Kurswechsel gegenueber T-052 ist der Satz „ausserhalb
DR-008/DR-009 ist nichts abgeschnitten": er galt fuer den `Build planner` und
die Waffen-Slot-Kacheln. Die sechs Inhalts-Tabs hat T-052 nicht geoeffnet.

## 4. Was gut ist und nicht schlechter werden darf

- **`Deep of Night` ist das gestalterische Vorbild der sechs** — vier
  Ueberschriften, die je eine Spielerfrage benennen, je eine Tabelle, je eine
  ruhige Erklaernote, dazu eine eigene Herkunftszeile. AK-68 uebertraegt das
  Muster auf alle sechs und darf es dabei nicht verwaessern.
- **`Red variants` traegt die beste Bezugsgroessen-Zeile des Programms** —
  *„The figures are how many red variants of each sort a run puts on the
  selected map."* Eine Zahl mit Einheit **und** Geltungsbereich, in einem
  Satz. AK-98 laesst sie unangetastet.
- **`World Events` trennt Herkunftsklassen sichtbar und benennt die
  Trennung** — die einzige Farbrolle der sechs Tabs, die heute schon eine
  Legende hat. AK-74 macht daraus die Regel.
- **Die Stacking-Spalte des Effekte-Tabs** nennt in jedem Tooltip das
  entscheidende Feld (`exclusivityId 1000 — the game groups these and applies
  only one`). Sie ist die einzige Spalte des Tabs, deren Urteil ein Spieler
  nachpruefen kann, und wird nicht angefasst.

---

## 5. Jede Stelle, an der ich eine Entscheidung des App Designers brauche

Vollstaendig in `UI_SPEC.md` §10; hier gesammelt fuer den `director`:

1. **`Avg chance`: eine Zahl oder eine Spanne?** Nach AK-79/AK-80 ist beides
   ehrlich. *(a)* zwei Spalten (gewichteter Mittelwert + bester Fall),
   *(b)* eine Spannenspalte (`0.5 – 100 %`). **Meine Empfehlung: (b).** Der
   Grund, warum ich nicht selbst entscheide: die Wahl sagt, wofuer der Tab
   da ist — Nachschlagewerk oder Farm-Planer —, und das kann ich nicht
   messen.
2. **`Pools`: streichen oder umbenennen?** AK-78 legt beide Ausgaenge
   verbindlich fest. **Meine Empfehlung: streichen** (Ausgang A). Die
   Entscheidung ist eine Streichung und damit seine.
3. **Die dreizehn uebrigen Streichvorschlaege** aus §2 oben, jeder mit dem
   Satz, was verloren geht.
4. **Zaehlt ein roter Haendler als „red variant"?** Die Intro definiert rote
   Varianten als *„individual empowered enemies"*; die Zeile `Merchants`
   (4 bis 6 je Karte) geht in `Total red variants on the map` ein. Der
   `qa-engineer` hat die Frage in T-055 an den `director` gestellt und
   ausdruecklich nicht als Befund gemeldet. Ich reiche sie weiter und
   beantworte sie nicht: sie ist eine Inhaltsentscheidung.
5. **Will er die Quellenangaben ueberhaupt sehen?** AK-104 haelt die
   selbstgesetzte Regel des `eventstab`-Moduls aufrecht (Herleitungssprache
   gehoert nicht auf den Bildschirm) und verbannt `fextralife`, `game8`,
   `Eldenpedia`, `thefifthmatt`, `pattern modifier` und *„the row this
   project had wrong"* aus dem Fliesstext. Ob die Quellen als eigenes,
   ruhiges Element (`sources`) darunter erscheinen oder gar nicht, ist
   Geschmack — beides ist mit AK-104 vertraeglich. *(Damit ist zugleich
   T-055s offene Frage 4 an mich beantwortet: die Regel bleibt, der Text
   wird nachgezogen.)*

**Von T-055 an mich gerichtet und hier beantwortet:** Frage 3 (welche
Definition der `Avg chance` gewollt ist) → AK-79/AK-80, plus offene Frage 1
oben fuer die Darstellung. Frage 4 (gilt die Modulkopf-Regel noch?) → ja,
AK-104. Fragen 1, 2 und 5 sind an den `director` gerichtet und bleiben dort.

---

## 6. Was der `developer` als Naechstes braucht

Nach Wirkung sortiert, alle mit AK-Nummer in `UI_SPEC.md`:

1. **AK-71/AK-97** — `Deep of Night` in eine `QScrollArea`. Ein Ein-Tab-Fix
   mit Fenster-weiter Wirkung: er nimmt dem ganzen Programm 90 logische px
   Mindesthoehe und macht damit erst die Bildlaufleisten der anderen Tabs
   erreichbar.
2. **AK-72/AK-90/AK-84** — Spaltenzahl der beiden Kachelraster aus der
   Breite rechnen. Danach sind alle zehn Nightlords und alle Waffenwerte
   sichtbar.
3. **AK-77** — Spaltenprioritaet der Effektetabelle umkehren.
4. **AK-79/AK-80/AK-78** — die Zahlen der Effektetabelle: eine Definition,
   gewichteter Mittelwert, `Pools` nach Entscheid.
5. **AK-68/AK-76/AK-82/AK-89/AK-95/AK-98** — das Kopfmuster auf allen sechs.
6. Der Rest (AK-69, AK-70, AK-73 bis AK-75, AK-81, AK-83, AK-85 bis AK-88,
   AK-91 bis AK-94, AK-96, AK-99 bis AK-105).

**Ausserhalb meiner Vorgabe und trotzdem faellig:** QA-137 (fuenf der sechs
Tabs haben keinen Test, der Unsinn bemerken wuerde). Solange das so ist,
haelt keine der 38 Vorgaben oben den naechsten Refactor aus. T-056 schickt
den Punkt direkt an den `developer`; ich unterstreiche ihn hier, weil jede
meiner AKs als Charakterisierungstest formuliert ist und dieselbe Strecke
braucht.

## 7. Nicht bearbeitet, ausdruecklich

- **A11** — nicht nachweisbar ohne `power-user`-Bericht (siehe oben).
  Braucht einen zweiten Lauf **nach** der Umsetzung.
- **Die Rechnungen selbst.** Ob `ladder.down` gezeigt wird, ob
  `DEBUFF_ON_BREAK` derselbe Mechanismus ist (QA-129), ob die Kartenbindung
  der Roster herstellbar ist (QA-132) — Daten- und Rechenfragen. Meine
  Vorgabe regelt, was der Bildschirm ueber die **Herkunft** einer Zahl sagt,
  nicht, welche Zahl richtig ist.
- **QA-137**, laut T-056 ohne Designanteil.
- **`Build planner`** und der Berater (S7 bis S11).
- **Die Tab-Leiste unter 1250 physischen px** wird selbst scrollbar. Ein
  Fensterbefund, kein Tab-Befund; im Backlog von `DESIGN_REVIEW.md` geparkt.
- **Dark/Light** — das Programm hat keine Theme-Umschaltung; es gibt nichts
  zu vergleichen.

## 8. Abgelegte Belege

`docs/screenshots/2026-09-05-T056/`, **18 Dateien** — `tab1-effects.png`,
`tab2-weapons.png`, `tab2-weapons-longsword.png`,
`tab2-weapons-narrow1250.png`, `tab2-weapons-wide2100.png`,
`tab3-nightlords.png`, `tab3-nightlords-gladius.png`,
`tab3-nightlords-wide2100.png`, `tab3-nightlords-bottomedge.png`,
`tab4-deep.png`, `tab4-deep-bottomedge.png`, `tab5-redvariants.png`,
`tab6-worldevents.png`, dazu die Ausschnitte `zoom-tile-clipped.png`,
`zoom-tile-wrap.png`, `zoom-nightlords-wide-top.png`,
`zoom-nightlords-bottom.png`, `zoom-deep-bottom.png`.

**Drei Aufnahmen sind entstanden und wurden geloescht, nicht abgelegt** — ich
nenne sie, damit niemand sie als Luecke sucht: eine, in der ein fremdes
Fenster den Vordergrund uebernommen hatte und die fremden Bildschirminhalt
zeigte; und zwei, mit denen ich das Detailpanel von `World Events` auf
`Plague of Locusts` umschalten wollte, um QA-133 (`10,000 runes for 1s`)
selbst zu sehen. Die Umschaltung per `SelectionItemPattern` hat die Auswahl
gesetzt, aber das Detailpanel blieb auf `Fell Omen` — die Bilder zeigten
nicht, was ihr Name behauptete. **Folge: QA-133 ist in meiner Vorgabe
(AK-103) allein durch die Messung des `qa-engineer` getragen, nicht durch
einen eigenen Screenshot.**
