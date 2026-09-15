STATUS: erledigt
AUFTRAG: T-092 — Schlechtester und bester Fall, und die Zahl ohne Waffe (ui-ux-designer, Spec-Modus)
GELESEN: docs/tasks/T-092.md · GOAL.md (A16, A17 im Nachtrag 07.09.2026; A7, A8, A11, A12) · docs/state.md (07.09.2026) · UI_SPEC.md vollstaendig in den betroffenen Abschnitten (T-004 §3.1-§3.4 und §4, T-024 §3.2-§3.4, T-078 §2-§6, T-080 §4-§6, T-084 §1 mit AK-162 bis AK-166, T-086 §1-§3 mit AK-177 bis AK-181, Director-Korrektur 06.09.) · Code gegen `84623a4`: nrplanner/model.py, inventory.py, damage.py, advisor/goals.py, advisor/types.py, advisor/evaluate.py, advisor/explain.py, advisor/run.py · nrplanner/advisorbar.py **im Arbeitsbaum** (T-091-Stand, nur gelesen, nicht importiert) · eigene Agenten-Erinnerung (Messmethode, Feldnamen-Falle)
GEAENDERT: UI_SPEC.md (neuer Abschnitt „Schlechtester und bester Fall, und die Zahl ohne Waffe (ui-ux-designer, T-092) — 2026-09-07", 679 Zeilen angehaengt, Datei danach wieder durchgaengig CRLF) · docs/berichte/T-092-ui-ux-designer.md (diese Datei). Sonst nichts; keine Commits, keine Stages.
ANNAHMEN: (1) „Fluch" heisst im Datensatz: Id in `OwnedItem.curse_ids` — es gibt kein Fluch-Flag am Effekt, und `advisor/evaluate.py:55,58` gibt Fluche in dieselbe Liste wie alle anderen Effekte. (2) Die Lesart wird technisch ueber `GoalContext.declared` gesetzt (A16 sagt „das Feld, mit dem der Spieler eine Bedingung heute von Hand erklaert"); der genaue Typ dafuer gehoert dem `architect`. (3) Messumgebung: ein Spielstand, ein Datenabzug, zwei von zehn Nightfarern, ein Relikt je Slotgruppe — jede Zahl unten gilt dafuer und nicht darueber hinaus.
NAECHSTER: director — zwei Fragen an den App Designer (F-K, F-L) und eine Entscheidung, die vor dem Bau von A17 faellt (`weapons_held`, siehe Punkt 3)
BLOCKIERT DURCH: nichts

---

# T-092 — Bericht des ui-ux-designer

## Kurz

Vorgabe liegt in `UI_SPEC.md`, Abschnitt T-092, mit **AK-182 bis AK-194**.
Alle vier Punkte des Auftrags sind entschieden. Drei Dinge, die der Auftrag so
nicht wusste, stehen unten unter „Was mir aufgefallen ist" — eines davon
(Punkt 3, `weapons_held`) entscheidet, ob A17s Abnahme ueberhaupt bestehen
kann.

## Messumgebung (L-009)

Alle Zahlen sind mit den **Produktionsfunktionen selbst** erzeugt
(`advisor.evaluate.evaluate` ueber `model.compute`, `explain.reasons`,
`explain.not_counted`, `explain.curses_without_a_figure`,
`explain.effects_without_a_figure`, `goals.GOALS[...].score`) — keine
Nachbildung. Kein Fenster gestartet, kein Bildnachweis (NH-002). Messskripte
im Scratchpad, nicht im Repo.

- **Codestand:** `84623a4`. `model.py`, `inventory.py`, `damage.py`,
  `effecttext.py` und das ganze `advisor/`-Paket sind byteweise `84623a4`
  (je Datei einzeln mit `git diff --quiet` geprueft). Im Arbeitsbaum weichen
  wegen T-091 ab: `advisorbar.py`, `advisorblock.py`, `app.py`,
  `tests/test_advisor_bar.py`, `tests/test_advisor_block.py`. **Keine davon
  wird von einer Messung importiert**; `advisorbar.py` habe ich im
  Arbeitsbaum-Stand nur **gelesen**.
- **Datenabzug:** `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`,
  `extract_version` 11, `data_version` 10350000, 2076 Effekte, 1793 Waffen,
  849 Relikte — nur gelesen.
- **Bestand:** Spielstand des App Designers, **309** Kopien mit Handle,
  **845** Effektrollen, **112** Fluchrollen. Save read-only, kein Netz.
- **Umgebung A** Wylder Lv15 / `Wylder's Greatsword` · **Umgebung B**
  Ironeye Lv15 / `Ironeye's Bow`. Ein Relikt je Slotgruppe, Slot 0, kein
  gehaltener Slot, `EVEN_WEIGHTING`, `declared` leer ausser wo eine Lesart
  es setzt.
- **Gegenprobe, dass das Rezept dasselbe misst wie T-086:** die Umgebung
  reproduziert **AK-180 Zahl fuer Zahl** — (b) 144/149, (c) 38/25, stumme
  Effektzeilen 426/434. Die Zahlen sind also vergleichbar und nicht aus einer
  zweiten Rechnung.

## Punkt 1 — das Bedienelement (A16)

**Entschieden:** ein **eigenes** Bedienelement, keine Erweiterung der
Zielwahl. Zweite `QComboBox` zwischen Zielwahl und `Optimize`, Eintraege
**`Worst case`** und **`Best case`**, `Worst case` voreingestellt,
`AdjustToContents`, `setMaximumWidth(140)`, mit einem Tooltip, der beide
Lesarten erklaert. **Kein Aktionsknopf** im Sinne von AK-07 — AK-07 zaehlt
die Knoepfe rechts, die etwas tun; dies ist eine Einstellung links, in
derselben Klasse wie die Zielwahl. Damit die Ausnahme keine Tuer ist:
**links von `Optimize` stehen hoechstens zwei Einstellungen.**

**Warum nicht vier Eintraege in der Zielwahl** (der billigere Weg, verworfen):

1. Es ist ein Kreuzprodukt — 2x2 heute, 2x3 bei einem dritten Ziel. Der
   Modul-Docstring von `goals.py` sagt zu, dass ein drittes Ziel *"one
   function and one registry entry"* ist; die Liste braeche diese Zusage in
   der Oberflaeche.
2. Die Zielwahl ist im Picker **dieselbe** Einstellung wie in der Leiste
   (T-024 §3.4), und die Picker-Karte zeigt **beide** Zielrichtungen
   gleichzeitig (AD-018.2). Eine in der Zielwahl versteckte Lesart waere fuer
   die zweite Spalte nicht gesetzt.
3. A16 sagt „zwei Lesarten **derselben** Rechnung". `Maximise damage (worst
   case)` behauptet eine andere Zielrichtung.

**Warum diese Woerter, gegen den Einwand des Auftrags.** `Safe` / `Risky`
sind die Woerter des Nutzers und die kuerzesten, benennen aber die **Haltung
des Spielers** statt der **Annahme der Rechnung** — „safe" neben `Maximise
damage` liest sich als „sicherer Schaden". Vor allem: `GOAL.md` A16, der
Auftrag, die Berichte und alle kuenftigen Testnamen sagen „schlechtester /
bester Fall". Eine Leiste, die `Safe` / `Risky` sagt, gaebe **einer Sache
zwei Namen** — die Fehlerklasse D-11, nur in Woertern statt in Zahlen. Die
Frage „worauf kann ich mich verlassen?" beantwortet nicht die Beschriftung,
sondern der Satz neben der Zahl (Punkt 2). Ebenfalls verworfen: ein Kaestchen
`Assume the worst` (nennt nur eine Lesart, die andere haette keinen Namen)
und zwei einrastende Knoepfe (kosten die Breite **beider** Beschriftungen).

**Breite — Rangaussage, keine Pixelzusage.** Eine Pixelbreite ist hier nicht
messbar (offscreen liefert dieser Rechner 12,0 px je Zeichen fuer jede
Zeichenkette, T-084 §0; ein Fenster startet dieser Auftrag nicht). Rang:
`Minimise damage taken` 21 Zeichen, `Worst case` 10, `Best case` 9 — rund die
Haelfte des Textes der bestehenden Combobox plus Rahmen und Pfeil. **AK-194**
verlangt die Messung am laufenden Fenster mit einer harten Untergrenze fuer
die Statuszeile (>= 105 px bei 1320 px, zwei Drittel der heutigen 158 px) und
einen benannten Rueckfall auf `Worst` / `Best`.

## Punkt 2 — was die Zahl ueber sich sagt (A16, A12)

**Vier Orte, je einmal:** das Bedienelement · der Kopf des Vorschlagsblocks
(`SUGGESTED — MAXIMISE DAMAGE, WORST CASE`) · der `Why`-Dialog (Titel plus
**eine** Zeile im Kopf) · die Zusammenfassungszeile des Pickers
(`  ·  worst case`). **Nie je Zeile, nie je Slot, nie auf einer Karte** —
dieselbe Ueberlegung wie AK-22 und AK-50.

**Die Statuszeile traegt die Lesart nicht.** Der Zusatz `, worst case`
muesste in 4.3, 4.4, 4.6, 4.9 und 4.11 stehen — fuenf Zeilen laenger in einer
Zeile, die bei 1320 px 158 px hat, waehrend das Bedienelement daneben
dasselbe sagt. Die Lesart steht dort, wo eine **Zahl** ohne die Leiste im
Blick gelesen wird.

**Umschalten = Zielwechsel.** `_goal_chosen` sagt heute *"A direction is a
different question, so the old answer goes"* und ruft `the_build_changed()`.
Die Lesart tut genau dasselbe: **kein neuer Zustand in §4, kein neuer
Wortlaut.** Das ist zugleich die Antwort auf die D-11-Auflage des Auftrags —
**es stehen nie zwei Zahlen nebeneinander**, es lebt immer hoechstens ein
Ergebnis, und `declared` ist bereits Teil des Anfrage-Schluessels
(`advisor/run.py:269`), ein altes Ergebnis kann also nicht unter neuem Namen
ausgeliefert werden. Ein Nebeneinander beider Zahlen wird **nicht** gebaut.

**Was die Lesart setzt:** ausschliesslich `GoalContext.declared`. Keine
Gewichte, keine Zahlen. **Die eigenen Erklaerungen des Spielers gewinnen ueber
beide Lesarten** — die Lesart ist Voreinstellung fuer die Bedingungen, die er
**nicht** beantwortet hat. Anders waere es eine Annahme gegen ein Wissen (A7)
und die Zahl wiche vom Statblatt daneben ab, ohne dass es jemand sagt.

**Die Folgefrage des Auftrags — wie sich die Listen verhalten — ist gemessen,
und die Antwort ist besser als erhofft** (Umgebung A, Summe ueber die 309
Ein-Relikt-Probleme):

| | heute | schlechtester Fall | bester Fall |
|---|---|---|---|
| `not_counted` (4.9b) | **197** | **170** | **27** |
| `curses_without_a_figure` (4.9a) | **67** | **42** | 67 |
| `effects_without_a_figure` | **426** | 426 | **323** |
| gezeichnete Zeilen gesamt | 1164 | 1281 | 1354 |
| Fuellung (b) | 144 | 144 | **0** |
| Fuellung (c) | 38 | 38 | 23 |

**`170 + 27 = 197`.** Jede Lesart nimmt aus `not_counted` **genau** eine
Seite heraus: der schlechteste Fall die 27 konditionalen Fluchrollen, der
beste die konditionalen Buffrollen. Die Identitaet ist ein Waechter, und sie
ist AK-187. **Folge fuer den Wortlaut: keine.** 4.9a, 4.9b, die
`Why`-Ueberschrift und die Zaehlzeile bleiben Buchstabe fuer Buchstabe; nur
die Zahlen wandern. AK-155 haelt in beiden Lesarten, weil die Lesart Zeilen
zwischen „mit Zahl" und „stumm" verschiebt und keine erzeugt.

## Punkt 3 — der Satz zur fehlenden Waffe (A17)

**Entschieden: er wird `Goal.scope`** — weil der Berater unter A17 **immer**
ohne Bezugswaffe rankt, nicht „in der Voreinstellung mit Umschaltung". Nur
dann ist A17s Abnahme ueberhaupt eine pruefbare Aussage, und fuer eine dritte
Einstellung ist in der Leiste kein Platz.

Neu, an den Anfang von `MAX_DAMAGE.scope`:

> `This ranks what stays with you between expeditions — attack multipliers, attributes and passives. Armaments are not part of the figure.`
>
> `With no armament in the figure there is nothing to scale, so the five attack multipliers are averaged with equal weight.`

Der zweite Satz ist der heutige `_NO_ARMAMENT_NOTE` mit **einer** Aenderung
(`chosen` → `in the figure`). **Was der Satz bewusst nicht sagt:** dass Waffen
pro Runde ausgewuerfelt sind — das ist Spielwissen des Nutzers und steht in
keinem Datenabzug; AK-140/AK-157 gelten sinngemaess auch fuer Behauptungen
ueber das Spiel. Der Satz sagt, **was die Zahl ist**, nachpruefbar an
`goals._attack_multiplier_mean`.

**AK-162 bis AK-166 nachgezogen, nicht stehengelassen:** die Aufteilung
Registry/Ergebnis bleibt richtig, es wandert nur ein Satz. AK-162, AK-164,
AK-165, AK-166 gelten unveraendert; **AK-163 behaelt seine Regel und verliert
seinen einzigen heutigen Inhalt** (`Baseline.unknowns` ist fuer `max_damage`
dann leer, Zeile 3b entfaellt genau so, wie AK-163 es beschreibt). Sein
Rot-vorher ist erledigt und wird durch **AK-190** ersetzt: die Gefahr ist
jetzt, dass der Satz an **zwei** Orten steht.

**Und hier der Befund, der ueber A17 entscheidet — gemessen:** die
Bezugswaffe wegzulassen **genuegt nicht**. `model.compute` erfuellt
Waffentyp-Schranken aus **`weapons_held`**, nicht aus der Bezugswaffe. Mit
`reference=None` und weiterhin gefuehrter Waffe:

| Vergleich (Umgebung A, `max_damage`) | Kopien mit anderer Zahl | Rangfolge |
|---|---|---|
| Greatsword gefuehrt vs. Bogen gefuehrt | **2 von 309** | anders **ab Rang 0** |
| Greatsword gefuehrt vs. nichts gefuehrt | 1 von 309 | anders ab Rang 0 |

Namentlich: `Deep Polished Drizzly Scene` /
`Improved Greatsword Attack Power` (`triggerOnWepType` 5): +0,09 mit
Greatsword, 0,00 sonst · `Grand Luminous Scene` /
`Improved Bow Attack Power` (`triggerOnWepType` 51): +0,06 mit Bogen, 0,00
sonst. Von 845 Effektrollen tragen 20 `triggerOnWepType`, 8 `wepTypeTrigger`.

**Empfehlung (Mechanismus gehoert dem `architect`, Zielsetzung dem Nutzer):**
der Berater rechnet mit `reference=None` **und** `weapons_held=()`. Erst dann
gilt A17s Abnahme woertlich, und es folgt A17s eigener Begruendung — ein
waffentypgebundener Buff ist genauso wenig „zwischen Runden fest" wie die
Bezugswaffe. **Gemessene Folgen:** (c) waechst 38 → **40** (A) und 25 → **28**
(B), (b) bleibt 144 (A) bzw. faellt 149 → 147 (B), die stummen Effektzeilen
steigen um 1 (426 → 427). **Preis, benannt:** die Zahl des Beraters weicht
dann bewusst vom Statblatt daneben ab — der `GoalContext`-Docstring fuehrt
genau diese Abweichung heute als Fehlerklasse (*"QA-001 in a new place"*).
Unter A17 ist sie gewollt, und der erste `scope`-Satz sagt sie dem Spieler.
Als **F-L** an den App Designer gestellt.

**Nebenwirkung im Picker, die niemand notiert hatte:** ohne Bezugswaffe ist
die Zielpunktzahl einheitenlos, T-024 §3.3 laesst dann den Zusatz `AR`
entfallen — auf der Karte stuende `Damage  +0.09`, eine Zahl ohne Groesse
(A12 gebrochen). Vorgabe (**AK-193**): die linke Beschriftung heisst
`Attack multipliers`, solange ohne Armatur gerankt wird, und kommt aus
derselben Quelle wie `GoalScore.display`. Ob sie stattdessen als Prozentwert
gezeigt werden soll, ist **F-K** (Empfehlung: nein).

## Punkt 4 — die Armaturenzeile (die eine wieder aufgemachte Vorgabe)

**Sie bleibt, mit geaendertem Ende.**

| | Wortlaut |
|---|---|
| ersetzt | `{effect name}: it depends on the armaments you carry, so no number here.` |
| neu | `{effect name}: it depends on the armaments you carry, which this figure leaves out.` |

**Begruendet an dem, was der Spieler damit anfangen kann.** Zwei Dinge
bleiben unter A17 wahr: (1) der **Startarmatur-Teil ist nicht ausgewuerfelt**
— jeder Nightfarer beginnt jede Expedition mit seiner eigenen Waffe, das
Programm rechnet die Paarung sogar aus (`damage.is_starting_armament`,
Slot 1); ein Relikt mit `Improved Greatsword Attack Power` ist fuer Wylder
etwas anderes als fuer Ironeye. (2) Die Zeile **erklaert eine Null** — ohne
sie haelt der Spieler das Relikt fuer wertlos.

Geaendert hat sich nicht die Wahrheit der Zeile, sondern der **Hebel**
dahinter: heute bewegt sich die Zahl, wenn er die Waffe anlegt (gemessen:
+0,09 / +0,06 auf zwei Kopien), unter A17 nicht mehr. `so no number here`
liest sich dann als Aufforderung, an einem toten Hebel zu ziehen. Der neue
Schluss steht in der Familie, die diese Datei schon fuehrt (T-078 §3 (ii),
T-024 §3.6, QA-113) — „figure" ist hier das Wort fuer die Rankingzahl.

**Verworfen: die 38 Zeilen fallen nach (b).** Dann laesen sie `only applies
under a condition, so no number here.` — die schwaechere Auskunft, von
T-086 §1.4 fuer dieselben Zeilen schon einmal verworfen; ausserdem naehme (b)
Zeilen auf, die nach QA-104 **nicht** in `not_counted` stehen, und der Spieler
faende den Effekt in der Liste der bedingten Effekte nicht wieder.

**Zaehlung** (A / B): (c) heute 38 / 25 · ohne gefuehrte Waffe **40 / 28** ·
im besten Fall 23 / 11. **(b) faellt im besten Fall auf 0** (beide
Umgebungen) — keine unerklaerte Bedingung bleibt uebrig.

## Die neuen AK, je eine Zeile

- **AK-182** Eigene Combobox `Worst case` / `Best case` zwischen Zielwahl und `Optimize`; hoechstens zwei Einstellungen links.
- **AK-183** Umschalten verwirft den Vorschlag wie ein Zielwechsel; kein neuer Zustand in §4.
- **AK-184** Nie zwei Zahlen fuer dieselbe Kopie; die Lesart reist in der Anfrage und im Schluessel.
- **AK-185** Die Lesart steht genau viermal (Element, Blockkopf, `Why`, Pickerzeile) und in keiner Zeile.
- **AK-186** Die Lesart wirkt nur ueber `declared`; die eigenen Erklaerungen des Spielers gewinnen; kein Gewicht wird angefasst.
- **AK-187** Schlechtester Fall = `not_counted` ohne die konditionalen Flueche, bester Fall = nur sie; 170 + 27 = 197.
- **AK-188** 4.9a, 4.9b, Ueberschrift und Zaehlzeile bleiben woertlich; nur die Zahlen wandern (67 → 42, 426 → 323).
- **AK-189** Der schlechteste Fall ist laenger: laengste Slotgruppe 14 → 21, laengster Block 15 → 22; nach dem Einbau je Lesart neu messen (AK-161).
- **AK-190** `_NO_ARMAMENT` und `_NO_ARMAMENT_NOTE` wandern nach `MAX_DAMAGE.scope`, neu formuliert; der Zweig **mit** Bezugswaffe braucht dann einen eigenen Laufbefund.
- **AK-191** Zwei Laeufe, die sich nur in der gefuehrten Armatur unterscheiden, ergeben dieselbe Rangfolge (Rot-vorher gemessen: 2 von 309, Rang 0).
- **AK-192** Fuellung (c) endet auf `which this figure leaves out.`; `armaments you carry, so no number here` kommt nirgends mehr vor.
- **AK-193** Die Wertspalte des Pickers heisst `Attack multipliers`, solange ohne Armatur gerankt wird, und der Wert traegt keine Einheit.
- **AK-194** Die Breite der Statuszeile wird am laufenden Fenster gemessen (>= 105 px bei 1320 px), sonst heissen die Eintraege `Worst` / `Best`.

## Was mir aufgefallen ist und nicht in den Auftrag gehoerte

1. **Der Fluch-Zensus in A16 zaehlt Ids, nicht Zeilen — und der Unterschied
   ist Faktor vier.** Nachgezaehlt: **24 verschiedene Fluch-Ids** auf den
   Relikten (das ist die Zahl aus `GOAL.md`), aber **112 Fluchrollen** auf
   den 309 Kopien, davon **27 konditional auf 23 Kopien** (die 7 Ids aus
   A16), und heute **142 gezeichnete Fluchzeilen**. Die Abnahme von A16
   („die sieben bedingten Flueche bewegen die Rangfolge") ist erfuellbar:
   gemessen aendern im schlechtesten Fall **8 von 309** Kopien ihre
   `max_damage`-Zahl und **11 von 309** ihre `min_damage_taken`-Zahl, und die
   Rangfolge unterscheidet sich ab Rang 1 bzw. 2. Im besten Fall sind es
   36 bzw. 10 Kopien, Rangfolge ab Rang 0. In Umgebung B (Ironeye) dieselben
   Groessenordnungen (8 / 11 / 36 / 10). **Die Formulierung „7 Flueche"
   sollte in kuenftigen Auftraegen ihre Einheit tragen** (AK-181 sagt genau
   das fuer die stummen Zeilen; es gilt fuer die Flueche genauso).
2. **Der schlechteste Fall sprengt die Zeilenbudgets von AK-160.** Ein
   konditionaler Fluch, der stumm **eine** Zeile war, wird als erfuellte
   Bedingung zu **einer Zeile je bewegter Groesse** — die
   Damage-Negation-Flueche bewegen acht Felder. Gemessen: laengste
   Slotgruppe **14 → 21** Zeilen, laengster Vorschlagsblock **15 → 22**,
   meiste Fluchzeilen auf einer Kopie **5 → 15**. Das ist die groesste
   Layoutfolge von A16 und keine Kleinigkeit fuer die Slotkarte.
3. **Ein gebauter Text weicht von `UI_SPEC` ab, unabhaengig von diesem
   Auftrag.** `advisorbar.status_line` gibt fuer 4.7 bei `84623a4`
   `"Your build changed while this was working out. Optimize again."`,
   waehrend §4 seit T-084 `"Your build changed while this was working out —
   use Optimize again."` verlangt. Ich vergebe keine Befund-Ids; der
   `director` moege entscheiden, ob das eine QA-Nummer bekommt oder ob T-091
   es ohnehin gerade zieht.
4. **`explain.not_counted` enthaelt heute auch Flueche** (197 = 170 Buff- +
   27 Fluchbedingungen). Das ist kein Fehler, aber es steht in keinem
   Docstring und keiner Vorgabe; es ist die Grundlage der Identitaet in
   AK-187 und sollte dem `architect` bekannt sein, bevor er `not_counted`
   anfasst.
5. **Ich habe kein Fenster gestartet.** T-091 laeuft parallel im selben
   Arbeitsbaum, und seit T-071 laesst das Programm nur eine laufende Kopie
   zu — ein Start haette stillschweigend nichts getan und dem anderen Agenten
   das Fenster nach vorn geholt. Deshalb sind **alle Breitenaussagen dieses
   Berichts Raenge, keine Messungen**; AK-194 ist die Stelle, an der sie
   nachgeholt werden.
