```
STATUS: erledigt
AUFTRAG: T-059 — Abnahme des Tab-Audits: A10 bis A14, je Tab einzeln
GELESEN: docs/tasks/T-059.md · GOAL.md (A10 bis A14, Abschnitt "Erweiterung des Zielbilds (Nutzer, 2026-09-05)") · UI_SPEC.md (AK-68 bis AK-105 samt den beiden Nachtraegen des Directors vom 05.09. am Dateiende) · DESIGN_REVIEW.md (DR-013 bis DR-018 samt Backlog) · docs/berichte/T-055-qa-engineer.md (QA-125 bis QA-139) · docs/berichte/T-054-power-user.md (existiert, Datei vom 05.09. 13:39 — als Primaerquelle fuer Abschnitt 13 gelesen, nicht aus zweiter Hand) · docs/berichte/T-057-developer.md · docs/berichte/T-058-developer.md · qa/findings.md · nrplanner/{app,arsenaltab,bosstab,cardgrid,deeptab,depthstab,effectstab,eventstab,eventlore,relicpicker,tabheader,weapons,weaponslots}.py · tests/{conftest,rendered,tabtext,test_tab_geometry}.py · scripts/differential/mutate.py · scripts/make_screenshots.py · CLAUDE.md
GEÄNDERT: docs/berichte/T-059-qa-engineer.md (neu, diese Datei). Sonst nichts im Arbeitsbaum; kein git-Zustand veraendert (nur `status`, `log`, `show`, `diff` gelesen). Alle Messungen, Mutationen und Screenshots in einem eigenen Klon unter dem Scratchpad.
ANNAHMEN: (1) "Standardmass" in A13 ist die Groesse, die sich das Fenster selbst gibt: `app.py:1263 self.resize(1320, 860)` logische px. Ich habe dort zusaetzlich zu den fuenf beauftragten Breiten gemessen. (2) Die Umgebung des Spielers ist die Windows-Plattform **mit dem Fusion-Stil und der dunklen Palette**, weil `app.py:3714` beides vor dem Fensterbau setzt. Das ist nicht die Umgebung, in der die Waechter und die Berichte T-056/T-058 gemessen haben — siehe Abschnitt 1 und QA-146. (3) `A11` ist ausdruecklich nicht mein Urteil; Abschnitt 12 nennt nur meine Erwartung.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

# T-059 — Abnahmedurchlauf des `qa-engineer` gegen A10 bis A14

## 0. Kurzfassung

| Kriterium | Urteil | fehlt |
|---|---|---|
| **A10** — jeder Tab beantwortet eine benennbare Frage, und sie steht am Tab | **erfuellt, 6 von 6** | — |
| **A11** — nicht-technischer Spieler kommt allein ans Ziel | **nicht mein Urteil** | `power-user`-Lauf |
| **A12** — jede Zahl nennt Einheit und Bezugsgroesse | **teilweise, 4 von 6 Tabs erfuellt** | Nightlords (2 Abschnitte), World Events (1 Leiter) |
| **A13** — gestalterisch konsistent, nichts abgeschnitten | **teilweise, 3 von 6 Tabs erfuellt** | Effects (Spaltenkoepfe), Weapons (Reihenfolge), Red variants (Spaltenbreite) |
| **A14** — je Tab einzeln bestaetigt | **dieser Bericht** | — |

Zehn neue Befunde, **QA-140 bis QA-149**, davon **kein Blocker und kein
Critical**: ein P2, sechs P3, drei P4. Die fuenfzehn Befunde QA-125 bis
QA-139 aus dem Erstaudit habe ich nachgemessen: **dreizehn behoben, zwei
teilweise**.

Die Zusicherung, die den AK-77-Kompromiss traegt, **haelt fuer die Zellen** —
26 949 gekuerzte Zellen ueber elf Fenster-/Plattform-Kombinationen, **null**
ohne ihren vollen Text als Tooltip. Sie haelt **nicht fuer die
Spaltenkoepfe**; das ist QA-140 und der einzige Punkt, an dem ich die
Genehmigung des Directors beruehre.

---

## 1. Messmethode, und die dritte Messfalle

Der Auftrag warnt vor zwei Fallen: physische gegen logische px, und die
Offscreen-Schrift. Beide habe ich beruecksichtigt und **eine dritte
gefunden**.

**Der Qt-Stil.** `nrplanner/app.py:3714` setzt `app.setStyle("Fusion")` und
`app.setPalette(_dark_palette())`, bevor das Fenster gebaut wird — der
Spieler sieht **Fusion**. `tests/rendered.py::laid_out`, mit dem T-058
gemessen und getestet hat, setzt keinen Stil; dort laeuft **windowsvista**.
Der Unterschied ist nicht kosmetisch, er verschiebt genau die Spalte, um die
AK-77 geht. Beide Zahlenreihen sind an derselben Stelle am selben Datensatz
gemessen, nur der Stil unterscheidet sich:

| Fensterbreite | `Effect` (windowsvista) | `Effect` (Fusion) | Namen gekuerzt (vista) | Namen gekuerzt (Fusion) |
|---|---|---|---|---|
| 833 | 271 | **294** | 173 | **129** |
| 1067 | 320 | 320 | 80 | 80 |
| 1600 | 446 | **388** | 12 | **44** |
| 2100 (1709) | 506 | **448** | 2 | ~0 |

Die Zahlen der windowsvista-Spalte reproduzieren die von T-058 berichteten
**exakt** (271/320/446/506 und 173/80/12/2) — der Bericht ist an dieser Stelle
korrekt, er misst nur eine andere Maschine als die des Spielers. Details und
Bewertung: **QA-146**.

**Zusatzfund derselben Klasse:** unter `QT_QPA_PLATFORM=offscreen` betraegt
die Mindestbreite des Fensters **964** logische px. Ein `window.resize(833, …)`
ergibt dort ein **964 px breites** Fenster. Die Suite laeuft offscreen, und
ihr Fall `[833]` misst damit 964. Unter der Windows-Plattform ist die
Mindestbreite 760, dort greift 833 wirklich.

**Was ich gemessen habe.** Elf Konfigurationen: `offscreen` und `windows`,
je 833 / 1067 / 1250 / 1600 / 2100 logische px, dazu `windows` bei
**1320 x 860** — der Groesse, die sich das Fenster selbst gibt. Alles am
gebauten `Planner`, an gerenderten Rechtecken (`sectionSize`, `mapTo`,
`viewport`, `horizontalScrollBar().isVisible()`), nie an einer Konstante des
gepruefsten Moduls. Screenshots mit echtem Timer statt `processEvents` —
`scripts/make_screenshots.py` warnt selbst davor, zu frueh zu fotografieren,
und diese Warnung war berechtigt (Abschnitt 13, "was nicht gehalten hat").

---

## 2. Risiko-Briefing (vor der Messung erstellt)

Die riskantesten Stellen, in der Reihenfolge, in der ich sie angegangen bin:
(1) **die Tooltip-Zusicherung**, weil eine Genehmigung des Directors daran
haengt und weil "jede Zelle" eine Allaussage ueber 652 x 11 Zellen ist, die
nur eine Zaehlung belegen kann; (2) **die Messumgebung selbst**, weil zwei
Messfallen schon gefunden waren und Fallen dieser Art selten allein kommen —
das war der ertragreichste Punkt; (3) **die Geometrie an den Raendern**
(833 px und 513 px Fensterhoehe), weil dort zwei frische Umbauten aufeinander
treffen; (4) **die Randfaelle, die der `developer` selbst benannt hat**
(Suche loeschen, Picker schmaler ziehen), weil eine benannte Kante die
billigste Reproduktion ist; (5) **A12 je Tab**, weil der Erstaudit sagte,
kein Tab erfuelle es, und eine Sammelaussage darueber nichts wert waere.

---

## 3. Bestehende Tests

| Lauf | Ergebnis | Soll laut Auftrag |
|---|---|---|
| `-m "not slow"` | **722 passed, 5 deselected** (226 s) | 722 passed, 5 deselected |
| `-m "slow"` | **5 passed, 722 deselected** (54 s) | 5 passed |
| `tests/test_tab_geometry.py`, offscreen, Standardstil | 36 passed | — |
| `tests/test_tab_geometry.py`, offscreen, `QT_STYLE_OVERRIDE=Fusion` | 36 passed | — |
| `tests/test_tab_geometry.py`, `QT_QPA_PLATFORM=windows`, Standardstil | 36 passed | — |
| `tests/test_tab_geometry.py`, windows + Fusion | 36 passed | — |

Der Ist-Stand reproduziert. **Wichtig fuer QA-146:** die Geometrie-Waechter
bleiben unter allen vier Kombinationen gruen — der Stilunterschied erzeugt
**kein** falsches Gruen, er macht nur die berichteten Absolutzahlen zu Zahlen
einer anderen Maschine.

---

## 4. `Effects & chances`

**A10 — erfuellt.** Erster sichtbarer Text nach gerenderter Position (nicht
nach Konstruktionsreihenfolge): `y=14 WHAT A RELIC CAN ROLL, AND HOW OFTEN`,
darunter `y=32` der Fragesatz, erst danach bei `y=49` die vier Auswahlfelder.
Wortlaute wortgleich zu AK-76.

**A12 — erfuellt.** Nachgemessen, nicht uebernommen:

* `per relic effect slot` steht **genau einmal** im gesamten Text des Tabs
  (Beschriftungen + Tooltips + Spaltenkoepfe + 7 172 Zellen zusammen) — AK-79.
* Die drei zurueckgezogenen Formulierungen (`averaged over every pool`,
  `how likely an effect is on one roll`, `A pool is one of the lists`):
  **0 Treffer**.
* AK-80 am geforderten Fall: `[Wylder] Improved Mind, Reduced Vigor` zeigt
  **0.91 %** (Best 100.0 %, 241 Slots), `[Scholar] …` zeigt 100.0 % bei
  1 Slot.
* AK-81: `Continuous HP Recovery` traegt ungefiltert `3 of 3` und `1 of 3`,
  bei Farbfilter `Red` weiterhin `1 of 3`, bei `Blue` `3 of 3` — die Sprosse
  ueberlebt das Filtern und stimmt mit den vom Director korrigierten
  Beispielzahlen ueberein.
* Die **50** Zeilen mit `Relic slots = 0` zeigen `—` in beiden Chance-Zellen
  und tragen den AK-78-Tooltip. Kein `0.00 %`.

**A13 — nicht erfuellt.** Positiv zuerst: keine waagerechte Bildlaufleiste bei
**keiner** der elf Konfigurationen; `Effect` ist bei jeder Breite die
breiteste Spalte; die Untergrenzen 320/260 halten ab 1067 px, darunter greift
die genehmigte Ausnahme. Was nicht haelt, sind die **Spaltenkoepfe**: sie
werden nicht elidiert, sondern mitten im Wort beschnitten. Bei 1067 px lesen
sich die beiden Chance-Spalten als `vg chanc` und `est chanc`, bei 833 px
stehen acht Koepfe als drei- bis sechsbuchstabige Bruchstuecke da (`yp`,
`opie`, `olou`, `lic sl`, `cha`, `t cha`, `ackin`, `with`). Das ist **QA-140**.

---

## 5. `Weapons & spells`

**A10 — erfuellt.** `WHICH ARMAMENT HITS HARDEST FOR YOUR BUILD` bei `y=14`,
Fragesatz bei `y=32`, das Suchfeld erst darunter. AK-82 in der vom Director
entschiedenen Lesart (AK-68 gewinnt) ist damit umgesetzt.

**A12 — erfuellt.** Der Zusammenfassungsblock traegt alle drei verlangten
Bezugsgroessen-Saetze wortgleich: die Skalierungs-Skala (AK-85), der
Buildup-Bezug (AK-86), und `Staves and seals show the spell power …` (AK-88).
`spell scaling` kommt in keiner angezeigten Zeichenkette mehr vor — zwei
unabhaengige Masken (`spell scaling`, `scaling the game`) ueber `nrplanner/`
finden nur noch Kommentare und Docstrings (10 bzw. 5 Fundstellen, alle
Kommentar). Kosten der Vollstaendigkeit: der Block laeuft bei 833 px ueber
**fuenf** Zeilen Grau, bevor die erste Kachel kommt — der `developer` hat das
in T-057 §8 selbst an den `ui-ux-designer` gemeldet; ich bestaetige es und
mache keinen eigenen Befund daraus.

**A13 — nicht erfuellt.** Positiv: bei allen elf Konfigurationen **77 von 77**
Kacheln vollstaendig, **0** angeschnitten, keine waagerechte Bildlaufleiste;
das Raster faellt sauber von 9 auf 3 Spalten (833 px); kein Wert bricht
innerhalb einer `·`-Gruppe (`INT +29 · DEX +6 ·` / `STR -21`); der Tab oeffnet
mit `Axe (77)` aufgeklappt (AK-83). Zwei Dinge halten nicht:

* Die Zeile `vs standard` ordnet ihre Gruppen bei **jedem Programmstart
  anders** — **QA-142**, mit vier Reihenfolgen bei vier Hashseeds belegt.
* Eine Suche mit mehr als 60 Treffern liefert wieder die leere schwarze
  Flaeche aus DR-017 — **QA-143**.

---

## 6. `Nightlords`

**A10 — erfuellt.** `HOW TO HURT EACH NIGHTLORD` + Fragesatz stehen ueber der
Bestandszeile `10 Nightlords · 8 also have an Everdark Sovereign …`.

**A12 — teilweise.** Erfuellt sind die drei AK-91-Zeilen (unter
`DAMAGE TAKEN`, `STATUS BUILDUP`, `STANCE`, alle drei wortgleich in allen zehn
Panels), AK-92 (Maris: `Refills at — not in the game's files`), AK-93 (Adel
zeigt `WEAKNESS SPECIAL INTERACTION` samt seiner Notiz) und AK-94 (die
Sichtungszeilen tragen `#7fae72`, gemessen am gerenderten HTML). Sieben der
zehn Bosse zeigen `IT IS WEAKENED`, drei nicht (Maris, Caligo, Heolstor) —
genau die Verteilung, die `ladder.down` hergibt; Gnoster zeigt seine zwei
Eintraege beide.

Nicht erfuellt: **`IT BUFFS ITSELF` und `BODY PARTS` tragen keine
Bezugsgroesse**, waehrend der direkt benachbarte Abschnitt `IT IS WEAKENED`
eine hat — **QA-149**. Und **drei Bedeutungen liegen auf einem Gruen**, mit
einem zweiten, fast gleichen Gruen daneben, ohne Legende — **QA-145**.

**A13 — erfuellt, mit einer Einschraenkung.** Alle **zehn** Karten bei jeder
der elf Konfigurationen vollstaendig gezeichnet, **0** angeschnitten, keine
waagerechte Bildlaufleiste; das Raster geht von 6 Spalten (2100) auf 1
(833) herunter. DR-013 ist damit an der Wurzel weg. Die Einschraenkung ist
kein Datenverlust, sondern Flaeche: bei 833 px haelt das leere Detailpanel
330 von 833 px, waehrend die Karten einspaltig untereinander stehen —
**QA-147**.

---

## 7. `Deep of Night`

**A10 — erfuellt.** `DEEP OF NIGHT` + Fragesatz ueber den vier
Bestandsueberschriften, die unveraendert darunter stehen (AK-95).

**A12 — erfuellt.** Beide AK-96-Notizen stehen wortgleich unter der ersten
Tabelle, dazu der bisher nie gezeigte `sigil_info`-Satz. Jede der vier
Tabellen hat benannte Zeilenkoepfe (`Rating needed`, `Reward multiplier`,
`Sovereign Sigil`, `Relic tier`; `Enemy HP`, `Enemy attack power`, …), und die
Skalierungstabelle bekommt ihre Bezugsgroesse aus dem Fragesatz (*„All figures
compare a Deep of Night run with a normal expedition"*) plus der Zeile
*„The big figure is typical; the range under it is the spread …"*. Die
Ratingtabelle nennt ihre Zusatzregel (`Unknown Nightlord +100 …`) und
kennzeichnet, was community-berichtet ist.

**A13 — erfuellt.** `minimumSizeHint().height()` = **68** logische px gegen
die Schranke 860; die letzte Zeile *„Read from the game's own depth table."*
ist bei 900 px Fensterhoehe durch Scrollen erreichbar; keine waagerechte
Bildlaufleiste bei einer der elf Konfigurationen; die vier Tabellen behalten
ihre feste Hoehe innerhalb **einer** Bildlaufleiste, wie vom Director
bestaetigt. Der Tab ist gestalterisch weiterhin der beste der sechs.

*Nicht bestaetigt:* Meine erste Messung meldete die Zelle
`Deep Delicate, Polished, Grand` als abgeschnitten und ohne Tooltip. Am
laufenden Fenster **bricht sie um** statt zu elidieren und ist bei 833 und
1067 px vollstaendig lesbar. Kein Befund.

---

## 8. `Red variants`

**A10 — erfuellt.** `RED VARIANTS: WHAT THEY ARE, AND HOW MANY` + Fragesatz,
darunter der gekuerzte Intro-Absatz und die `COMMUNITY-REPORTED`-Zeile.
Der Tab sagt jetzt selbst, was er **nicht** beantwortet (*„The game's files do
not say by how much"*) — das war der Kern von QA-132.

**A12 — erfuellt.** `Examples (any map)` traegt den AK-99-Kopftooltip
wortgleich; die zwei Zeilen ohne benannte Mitglieder tragen
`— the files name none`; die Spaltenkoepfe lauten `Depth 1`, `Depth 2–3`,
`Depth 4–5` (AK-100) und die Zusammenlegung ist aus den Daten gelesen — ueber
alle sechs Karten geprueft; der Bezugssatz *„The figures are how many red
variants of each sort a run puts on the selected map."* steht an der Tabelle.

**A13 — nicht erfuellt.** Bei 1067 px und darueber ist alles in Ordnung: keine
waagerechte Bildlaufleiste, keine gekuerzte Zelle, `What can be red` ist
klar die breiteste Spalte. Bei **833 px** kippt das Verhaeltnis:
`Examples (any map)` = **349 px** gegen `What can be red` = **281 px**. Der
letzte Satz von AK-99 („die Spalte ist **nie** breiter als `What can be red`")
ist damit verletzt — **QA-144**.

---

## 9. `World Events`

**A10 — erfuellt.** `WORLD EVENTS` + der bestehende Absatz, der AK-68 schon
vorher erfuellte.

**A12 — teilweise.** Erfuellt: AK-101 (elf Ereignisse, **elf verschiedene**
Tagessaetze, `Judgment` 19/20, `Fire-Summoning Beasts` 9/30), AK-102
(Geltungsbereich der Prozentzahl und Beleg der Allaussage stehen wortgleich an
jedem Ereignis), AK-103 (`10,000 runes` **ohne** Dauer, `restores 100 stamina`
**ohne**, `invulnerable for 5s` **mit**; kein `for 0s` im ganzen Tab),
AK-104 (die sechs verbotenen Zeichenketten: **0** Treffer ueber alle 15
Listeneintraege), AK-105 (`Scale-Bearing Merchant` **einmal** in der Liste).
Nicht erfuellt: die Runen-Leiter `runs ×1 → ×1.1 → … → ×1.275` nennt nicht,
welcher Schritt zu welcher Anzahl Expeditionen gehoert, und der Satz beginnt
nach dem Entfernen des Param-Namens mit einem Rest — **QA-148**.

**A13 — erfuellt.** Keine waagerechte Bildlaufleiste, keine gekuerzte
Beschriftung, kein ` -- ` — **0** Vorkommen ueber alle elf Konfigurationen
**und** ueber einen Durchklick-Auszug aller 15 Listeneintraege (dort standen
die acht, die T-058 gefunden hat). `minimumSizeHint().height()` = 149.

---

## 10. Die Zusicherung, die den AK-77-Kompromiss traegt

**Der Auftrag:** unterhalb von rund 1100 px werden die Beschriftungsspalten
stark gekuerzt; genehmigt **unter der Bedingung**, dass jede gekuerzte Zelle
ihren vollen Text als Tooltip traegt.

**Gemessen** an der gerenderten Spaltenbreite gegen die gerenderte Textbreite,
ueber alle 652 Zeilen x 11 Spalten, in elf Konfigurationen:

| Plattform | Fenster (angefordert / tatsaechlich) | gekuerzte Zellen | davon ohne vollen Text im Tooltip |
|---|---|---|---|
| windows | 833 / 833 | 4 101 | **0** |
| windows | 1067 / 1067 | 1 830 | **0** |
| windows | 1250 / 1250 | 1 431 | **0** |
| windows | 1320 / 1320 (Standardmass) | 1 378 | **0** |
| windows | 1600 / 1600 | 702 | **0** |
| windows | 2100 / 1709 | 535 | **0** |
| offscreen | 833 / **964** | 5 122 | **0** |
| offscreen | 1067 / 1067 | 4 734 | **0** |
| offscreen | 1250 / 1250 | 2 921 | **0** |
| offscreen | 1600 / 1600 | 2 259 | **0** |
| offscreen | 2100 / 2100 | 1 936 | **0** |
| | **Summe** | **26 949** | **0** |

**Urteil: die Bedingung haelt fuer die Zellen.** Ich habe keine einzige
gekuerzte Zelle gefunden, deren voller Text nicht im Tooltip steht — auch
nicht in den zwei Spalten, die einen eigenen Tooltip hatten (Name mit
Spielkategorie, Stacking mit Beleg): beide tragen ihren eigenen Text jetzt
darueber.

**Sie haelt nicht fuer die Spaltenkoepfe.** Der Kopf ist keine Zelle im
Wortsinn, aber er ist die Zeichenkette, die sagt, was in der Spalte steht, und
er wird nicht elidiert, sondern beidseitig beschnitten. Bei 1067 px sind vier
Koepfe betroffen und zwei davon werden voneinander ununterscheidbar. Von den
elf Koepfen tragen acht einen erklaerenden Tooltip; `Effect`, `Type` und
`What it does` tragen **keinen**, und `Type` ist bei 833 px auf `yp`
beschnitten. Das ist **QA-140**, und es ist der Punkt, an dem die Genehmigung
haengt: die Aussage „gekuerzt heisst erreichbar, nicht verloren" stimmt fuer
den Inhalt und nicht fuer die Ueberschrift.

---

## 11. Die Befunde

### [P3 | Major | Mittel] QA-140 — Effects & chances: die Spaltenkoepfe werden mitten im Wort beschnitten; bei 1067 px lesen sich `Avg chance` und `Best chance` als `vg chanc` und `est chanc`

**Adressat:** developer (Umsetzung), ui-ux-designer (welche Koepfe wie
gekuerzt werden duerfen)
**Betroffen:** `nrplanner/effectstab.py`, `EffectTable.column_widths` /
`OTHER_CAP` (Zeile 197-206) und der Spaltenkopf der Tabelle
**Umgebung:** Windows-Plattform, Fusion-Stil und dunkle Palette wie `run.py`
sie setzt, 150 % Skalierung, echte Spieldaten, Voreinstellung der Filter

**Reproduktion:**
1. `.venv\Scripts\python.exe run.py`
2. Fenster auf **1067** logische px Breite ziehen (auf diesem Bildschirm:
   das Fenster auf die halbe Breite schnappen)
3. Tab `Effects & chances`, die Kopfzeile der Tabelle lesen

**Erwartet:** Jeder Spaltenkopf ist entweder vollstaendig lesbar oder mit
Auslassungspunkten gekuerzt und in jedem Fall eindeutig; A13 verlangt
„nichts abgeschnitten, kein Wortumbruch mitten im Begriff".
**Tatsaechlich:** `Relic slots` → `Relic slot`, `Avg chance` → `vg chanc`,
`Best chance` → `est chanc`, `Comes with curse` → `es with c`. Bei 833 px sind
es acht Koepfe: `yp`, `opie`, `olou`, `lic sl`, `cha`, `t cha`, `ackin`,
`with`. Am Standardmass 1320 x 860 ist nur `Comes with curse` betroffen.

**Analyse:** `OTHER_CAP` deckelt die neun Beschriftungsspalten und
`_levelled()` verteilt den Rest; beide arbeiten mit der Zellbreite und nehmen
die Kopfzeilenbreite nur als Wunsch (`_natural`), nicht als Untergrenze. Der
Kommentar in `_levelled` nennt genau diese Absicht („`Type` haelt die 37 px,
die seine eigene Kopfzeile braucht") — sie greift bei 1067 px fuer `Type`
auch, aber nicht fuer die vier langen Koepfe. Dazu kommt, dass Qt einen
zentrierten Kopf beidseitig beschneidet statt zu elidieren, was aus `Avg` und
`Best` dasselbe Wort macht. *Hypothese* zum zweiten Teil: die
`textElideMode` des `QHeaderView` greift nicht, weil der Kopf zentriert und
kuerzer als seine Mindestbreite gezeichnet wird; ich habe das nicht am
Qt-Quelltext nachgewiesen, nur am Bild.

**Auswirkung:** Die beiden Spalten, um die es dem Tab geht, verlieren bei
einem halbbreiten Fenster ihre Unterscheidbarkeit. Der Inhalt bleibt ueber die
Zell-Tooltips erreichbar, die Bedeutung der Spalte nur ueber den
Kopf-Tooltip — und `Type` hat keinen. Das ist der Riss in der Zusicherung, auf
der die Genehmigung des AK-77-Kompromisses steht.

**Vorschlag:** Die Kopfzeilenbreite als Untergrenze in dieselbe Verteilung
aufnehmen, die heute die Zellbreite bedient — dieselbe Stelle, an der `Type`
seine 37 px schon bekommt. Wo auch das nicht reicht, den Kopf ausdruecklich
elidieren und ihm seinen vollen Text als Tooltip geben, wie es die Zellen
haben. Die drei Koepfe ohne Tooltip (`Effect`, `Type`, `What it does`)
brauchen einen, sobald sie gekuerzt werden koennen.

---

### [P2 | Major | Mittel] QA-141 — Relic picker: die fuenfte Kartenspalte wird schon bei der Groesse angeschnitten, die sich der Dialog selbst gibt

**Adressat:** developer, director (Einplanung, heute an S10 gehaengt)
**Betroffen:** `nrplanner/relicpicker.py:16` (`COLUMNS = 5`), `:395`
(`resize(CARD_WIDTH * COLUMNS + 80, 720)`), `:531`
(`grid.addWidget(card, i // COLUMNS, i % COLUMNS)`)
**Umgebung:** Windows-Plattform, Fusion, echtes Save (54 Relikte im
gepruefsten Slot)

**Reproduktion:**
1. `run.py`, Tab `Build planner`, einen Reliktslot oeffnen
2. Den Dialog **nicht** anfassen — er oeffnet 1030 x 720
3. Rechten Rand des Kartenbereichs ansehen; dann den Dialog auf 900 px
   Breite ziehen

**Erwartet:** Nach AK-72 wird nie eine Karte teilweise gezeichnet, und es
erscheint keine waagerechte Bildlaufleiste.
**Tatsaechlich:** Bei **1030** px (Voreinstellung) sind **11 von 55** Karten
um 12 px angeschnitten, die waagerechte Bildlaufleiste ist da. Bei **900** px
sind es dieselben 11 Karten, jetzt um **142 von 190 px** — Reliktnamen und
Effektzeilen enden mitten im Wort (`Lightnin`, `start of ex`, `Arcane +`).
Bei 700 px sind zwei Spalten betroffen, 22 Karten.

**Analyse:** Genau DR-016a, an einer Stelle, die T-058 ausdruecklich
ausgenommen hat. `CARD_WIDTH * COLUMNS + 80` rechnet die Randbreiten des
Rasters und die senkrechte Bildlaufleiste nicht mit: fuenf Karten brauchen
5 x 190 + 4 x 8 = 982 px plus Raender, der Sichtbereich bekommt 988. Deshalb
bricht es **ohne** Zutun des Nutzers, nicht erst beim Schmalerziehen. Der
Befund war als „wer ihn schmaler zieht" notiert; er ist eine Stufe schaerfer.

**Auswirkung:** Der Picker ist der Hauptweg des `Build planner` und damit des
kuenftigen Beraters. Ein Spieler, der die abgeschnittene Spalte sucht,
findet die Bildlaufleiste an der Unterkante des Dialogs — im Gegensatz zum
Tab-Fall liegt sie hier **nicht** hinter der Taskleiste, der Inhalt ist also
erreichbar. Das ist der Grund fuer Mittel statt Hoch bei der Wahrscheinlichkeit
und fuer P2 statt P1.

**Vorschlag:** `CardGrid` liegt fertig vor und deckt beide anderen Raster ab;
die Spaltenzahl aus der Sichtbereichsbreite rechnen und die Startbreite aus
derselben Formel ableiten. Gehoert in denselben Auftrag wie
`weaponslots.py:59` und `app.py:1416`.

---

### [P3 | Minor | Hoch] QA-142 — Weapons & spells: die Zeile `vs standard` ordnet ihre Gruppen bei jedem Programmstart anders

**Adressat:** developer
**Betroffen:** `nrplanner/arsenaltab.py:508`
(`for stat in scaling.keys() | base_scaling.keys():`)
**Umgebung:** beliebig; unabhaengig von Plattform, Stil und Fenstergroesse

**Reproduktion:**
1. `run.py`, Tab `Weapons & spells`, Kachel `Cold Icerind Hatchet`, Zeile
   `vs standard` lesen
2. Programm schliessen und neu starten, dieselbe Kachel lesen
3. (deterministisch nachstellbar mit `PYTHONHASHSEED=0..3`)

**Erwartet:** Dieselbe Waffe zeigt dieselben Werte in derselben Reihenfolge,
und dieselbe Reihenfolge wie die Zeile `Scaling` unmittelbar darueber.
**Tatsaechlich:** Vier Startvorgaenge, vier Reihenfolgen:
`STR -21 · INT +29 · DEX +6` / `INT +29 · STR -21 · DEX +6` /
`DEX +6 · STR -21 · INT +29` / `STR -21 · INT +29 · DEX +6`. Innerhalb eines
Starts weichen benachbarte Kacheln voneinander ab
(`FAI +30 · DEX -6 · STR -8` neben `DEX -6 · STR -8 · INT +30`), und die
Zeile `Scaling` derselben Kachel ist stabil sortiert — zwei Zeilen
uebereinander, zwei Ordnungen derselben drei Werte.

**Analyse:** Die Vereinigungsmenge zweier `dict`-Schluesselmengen ist ein
`set`; die Iterationsreihenfolge von Zeichenketten haengt am
`PYTHONHASHSEED`, der pro Prozess zufaellig ist. Der Screenshot von T-058
(`weapons-1067-after.png`) und meiner zeigen dieselbe Kachel in
unterschiedlicher Reihenfolge — das ist derselbe Effekt, nicht eine
Aenderung am Code.

**Auswirkung:** Kosmetisch, aber auf bis zu 1 792 Kacheln und bei jedem Start
sichtbar; A13 verlangt Konsistenz ausdruecklich. **Fuer die Testbarkeit
wichtiger:**
`test_arsenal_tab_asks_the_facade::test_every_type_row_and_the_upgrade_line_match_the_facade`
vergleicht diese Zeichenkette byteweise gegen die Fassade — beide Seiten
werden im selben Prozess gebildet und bekommen dieselbe Zufallsordnung, der
Fall kann die Unordnung also nie sehen. Ein Waechter, der sie sieht, muesste
zwei Prozesse mit verschiedenen Seeds vergleichen.

**Vorschlag:** Die Vereinigung in einer festen Ordnung durchlaufen — am
naheliegendsten in der Reihenfolge, die die Zeile `Scaling` daruber schon
benutzt, damit die zwei Zeilen zusammenpassen.

---

### [P3 | Minor | Mittel] QA-143 — Weapons & spells: eine Suche mit mehr als 60 Treffern zeigt wieder die leere schwarze Flaeche aus DR-017

**Adressat:** ui-ux-designer; die Spec-Frage an den director
**Betroffen:** `nrplanner/arsenaltab.py:302` (Aufklappen nur bei <= 60
Treffern), `:139` (`Section.toggle.setChecked(False)`)
**Umgebung:** beliebig

**Reproduktion:**
1. Tab `Weapons & spells` — er oeffnet korrekt mit `Axe (77)` und 77 Kacheln
2. In das Suchfeld `a` tippen und die halbe Sekunde Verzoegerung abwarten

**Erwartet:** Der Tab zeigt Treffer oder sagt, dass er sie zusammengeklappt
hat.
**Tatsaechlich:** Drei zugeklappte Ueberschriften, **0** sichtbare Kacheln,
darunter leere Flaeche — der Zustand, den DR-017 fuer den Erstoeffnungsfall
beschreibt. `moonveil` (1 Treffer) und `frost` (4) klappen korrekt auf; das
Loeschen der Suche stellt den Erstzustand `Axe (77)` wieder her.

**Analyse:** AK-83 ist auf den Erstzustand geschrieben („beim ersten
Oeffnen"), und der ist erfuellt. Der Suchfall behaelt die 60er-Schwelle aus
der Zeit vor AK-83. Der Kommentar an der Stelle benennt das Problem
(*„which made searching feel broken"*) und die Schwelle war die Antwort
darauf — sie loest es nur unterhalb von 60.

**Auswirkung:** Ein Spieler, der nach `sword` oder einem einzelnen Buchstaben
sucht, bekommt eine leere Seite und kann nicht unterscheiden, ob nichts
passt oder alles zugeklappt ist. Die Zusammenfassungszeile nennt zwar eine
Trefferzahl, aber die steht ueber der leeren Flaeche.

**Vorschlag:** Zwei Lesarten, beide vertretbar, und die Wahl gehoert nicht
mir: entweder AK-83 gilt auch fuer den Suchfall (dann muss immer mindestens
eine Gruppe offen sein), oder der zugeklappte Zustand bleibt und sagt es
(eine Zeile ueber der Flaeche: „N Treffer in M Gruppen — aufklappen").
**Frage an den director:** deckt AK-83 den Suchfall mit ab?

---

### [P3 | Minor | Mittel] QA-144 — Red variants: `Examples (any map)` ist bei 833 px breiter als `What can be red`, entgegen dem letzten Satz von AK-99

**Adressat:** developer
**Betroffen:** `nrplanner/depthstab.py`, Spaltenpolitik der Tabelle
**Umgebung:** Windows-Plattform, Fusion, 833 logische px Fensterbreite

**Reproduktion:**
1. Fenster auf 833 logische px Breite bringen
2. Tab `Red variants`, die zwei Textspalten vergleichen

**Erwartet:** AK-99, letzter Satz: „Und die Spalte ist **nie** breiter als die
Spalte `What can be red`."
**Tatsaechlich:** `Examples (any map)` **349 px**, `What can be red`
**281 px**. Ab 1067 px stimmt das Verhaeltnis (515 / 349) und bleibt bis
2100 px richtig.

**Analyse:** T-057 hat statt einer Breitenregel den Stretch-Modus getauscht
(Spalte 0 bekommt den Rest, Spalte 1 `ResizeToContents`) und das im Bericht
ausdruecklich als halbe Umsetzung gemeldet; `ResizeToContents` haelt seine
349 px auch dann, wenn fuer Spalte 0 nur noch 281 uebrig sind. T-058 hat die
Stelle nicht angefasst.

**Auswirkung:** Die Spalte mit den Beispielnamen — nach AK-99 die
nachrangige — dominiert bei schmalem Fenster die Spalte, die die Zeile
benennt. Kein Datenverlust, keine Bildlaufleiste, keine gekuerzte Zelle.

**Vorschlag:** Dieselbe Deckelung wie im Effects-Tab: `Examples` bekommt eine
Obergrenze, die an der gerenderten Breite von `What can be red` haengt.

---

### [P3 | Minor | Mittel] QA-145 — Nightlords: drei Bedeutungen auf einem Gruen, daneben ein zweites, fast gleiches Gruen ohne Legende (AK-74)

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/bosstab.py:33` (`GOOD = "#6fbf73"`), `:35`
(`OBSERVED_COLOUR = "#7fae72"`), verwendet in `:430`, `:455`, `:584`, `:588`,
`:645`, `:680`
**Umgebung:** beliebig; gemessen am gerenderten HTML des Detailpanels

**Reproduktion:**
1. Tab `Nightlords`, Karte `Gladius` anklicken
2. `DAMAGE TAKEN` (gruene Schadensart), `STATUS BUILDUP` (gruene Werte),
   `IT IS WEAKENED` (gruenes `Weakened`) und die Zeilen `Watched in play …`
   / `Stacks: yes — repeats compound` vergleichen

**Erwartet:** AK-74 — jede bedeutungstragende Farbe wird auf dem Tab genau
einmal benannt.
**Tatsaechlich:** `#6fbf73` traegt **drei** Bedeutungen (Schwaeche gegen eine
Schadensart, leichtester Status, und die Beschriftung des Abschnitts
`IT IS WEAKENED`); die AK-91-Saetze benennen davon zwei. `#7fae72` (Sichtung
statt Datei) ist nirgends benannt und unterscheidet sich vom Nachbargruen nur
im Rotkanal (0x6f gegen 0x7f).

**Analyse:** AK-74 nennt als „Betroffen" nur „Gruen im Nightlords-Tab (zwei
Bedeutungen)". T-057 hat die zwei umgesetzt und die zwei weiteren Faelle
ausdruecklich an den `ui-ux-designer` gemeldet, ohne selbst etwas zu
erfinden — das war richtig. Sie stehen seither offen.

**Auswirkung:** Ein Leser sieht in `IT IS WEAKENED` ein Gruen, das er aus der
Schadenstafel als „hier bist du im Vorteil" gelernt hat, an einer Zahl, die
den Boss beschreibt. Die Zeile `Stacks: yes — repeats compound` ist gruen,
ohne dass irgendetwas sagt warum.

**Vorschlag:** Je ein Satz, im Stil der drei AK-91-Zeilen; die Entscheidung,
ob stattdessen eine der beiden Farben weicht, gehoert ebenfalls dem
`ui-ux-designer`.

---

### [P3 | Minor | Niedrig] QA-146 — Die Geometrie-Waechter und alle berichteten Pixelzahlen entstehen unter einem anderen Qt-Stil als dem, den das Programm setzt

**Adressat:** developer, director
**Betroffen:** `tests/rendered.py::laid_out` (setzt keinen Stil) gegen
`nrplanner/app.py:3714` (`setStyle("Fusion")`); alle Pixelzahlen in
`DESIGN_REVIEW.md` DR-014, `UI_SPEC.md` §2.2 und `docs/berichte/T-058-developer.md`
Abschnitt 4
**Umgebung:** Windows 10, PySide6 6.11.1

**Reproduktion:**
1. `tests/rendered.laid_out(data, "effects_tab", 1600)` und
   `sectionSize(0)` lesen → **446**
2. Vor dem Fensterbau `app.setStyle("Fusion")` und
   `app.setPalette(appmod._dark_palette())` setzen — beides tut `main()` —,
   dasselbe lesen → **388**

**Erwartet:** Eine Zahl, die als Beleg fuer den Bildschirm des Spielers
dient, entsteht unter der Konfiguration, die der Spieler startet (L-001,
L-003).
**Tatsaechlich:** Die Waechter und die Berichtszahlen laufen unter
`windowsvista`, der Spieler unter `fusion`. Der Unterschied betraegt an der
AK-77-Spalte bis zu **58 px** und aendert die Zahl der gekuerzten Namen bei
1600 px von **12** auf **44**. Zweiter Fall derselben Klasse: unter
`offscreen` hat das Fenster eine Mindestbreite von **964** px, der
Testparameter `[833]` misst dort also 964.

**Analyse:** Kein Fehler des Programms und **kein falsches Gruen**: ich habe
`tests/test_tab_geometry.py` in allen vier Kombinationen (offscreen/windows x
Standardstil/Fusion) gefahren, **36 passed** in jeder. Die Waechter behaupten
Beziehungen, die unter beiden Stilen halten — das war die ausdrueckliche
Entscheidung von T-058 und sie traegt. Was nicht traegt, sind die absoluten
Zahlen daneben.

**Auswirkung:** Jede kuenftige Aussage der Form „bei 1600 px sind noch 12
Namen gekuerzt" ist um den Faktor 3,7 zu guenstig. Fuer die
Streichdiskussion in `UI_SPEC.md` §8 ist das der Unterschied zwischen
„fast alles lesbar" und „jeder fuenfzehnte Name gekuerzt".

**Vorschlag:** `laid_out` setzt Stil und Palette wie `main()`; die
Berichtszahlen bekommen den Stil dazugeschrieben. Fuer die 833er-Faelle
zusaetzlich das erreichte `window.width()` mitpruefen, damit ein Fall nicht
still bei einer anderen Breite misst als in seinem Namen steht.

---

### [P4 | Minor | Mittel] QA-147 — Nightlords bei 833 px: das leere Detailpanel haelt 330 von 833 px

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/bosstab.py:288` (`setFixedWidth(330)`), `:263-277`
(`QHBoxLayout` ohne Splitter)
**Umgebung:** 833 logische px Fensterbreite

**Reproduktion:** Fenster auf 833 px, Tab `Nightlords`, ohne eine Karte
anzuklicken.

**Erwartet:** Bei knapper Breite bekommt der Inhalt den Platz.
**Tatsaechlich:** Das Panel zeigt nur `Select a Nightlord` und haelt 40 % der
Breite; die Karten stehen einspaltig darunter weg.

**Analyse:** Der `developer` hat die Kante in T-058 §11 selbst benannt. Das
Panel hat feste Breite und liegt in einer `QHBoxLayout`; DR-013 hatte den
Splitter als Loesungsrichtung genannt, T-058 hat ihn bewusst nicht gebaut,
weil das Kartenraster das Problem auch ohne ihn loest — was fuer die Karten
stimmt und fuer die Flaechenverteilung nicht.

**Auswirkung:** Kosmetisch. Alle zehn Karten sind erreichbar, nichts ist
abgeschnitten.

**Vorschlag:** Eine Mindestbreite statt einer festen, oder das Panel
unterhalb der Karten, sobald die Breite nicht fuer beides reicht.

---

### [P4 | Trivial | Mittel] QA-148 — World Events: die Runen-Leiter nennt ihre Bezugspunkte nicht, und der Satz beginnt mit einem Rest

**Adressat:** developer (Extraktor), ui-ux-designer (Wortlaut)
**Betroffen:** `nrdata/extract.py::_rune_scaling` (schreibt den Param-Namen in
den Anzeigetext), `nrplanner/eventstab.py` (`PARAM_NAME`, entfernt ihn beim
Zeichnen)
**Umgebung:** beliebig; jedes Ereignis mit einer Runenzeile

**Reproduktion:** Tab `World Events`, `Fell Omen / Morgott Invasion`, Zeile
unter `Runes: 3,750–7,500 base`.

**Erwartet:** A12 — eine Leiter aus sieben Faktoren nennt, welcher Schritt zu
welcher Anzahl abgeschlossener Expeditionen gehoert, oder sagt nach A7, dass
die Dateien das nicht hergeben.
**Tatsaechlich:** `Expeditions completed: runs ×1 → ×1.1 → ×1.125 → ×1.2 →
×1.225 → ×1.25 → ×1.275, so a well-progressed profile earns more from the
same kill.` Der Satz beginnt mit dem Rest des entfernten Param-Namens
(`… completed: runs ×1 …`), und die sieben Faktoren haben keine Bezugspunkte.

**Analyse:** Der Datensatz traegt den Satz genau so, mit
`ClearCountCorrectParam.SoulRate` an der Stelle, an der heute nichts steht;
Zaehlwerte sind im Datensatz **nicht** enthalten. Die Reparatur im Renderer
ist die vom `developer` bewusst gewaehlte, an der falschen Stelle sitzende
(T-057 §10, Debt-Liste). Der fehlende Bezug ist damit ein A7-Fall.

**Auswirkung:** Ein Spieler kann die Leiter nicht benutzen; sie sagt nur
„mehr ist mehr".

**Vorschlag:** Im Extraktor entweder die Zaehlwerte mitliefern oder den
Satz ohne Param-Namen bilden und den fehlenden Bezug nach A7 aussprechen.
Beides ist eine Formataenderung mit `EXTRACT_VERSION`-Anhebung.

---

### [P4 | Minor | Mittel] QA-149 — Nightlords: `IT BUFFS ITSELF` und `BODY PARTS` nennen keine Bezugsgroesse, der Nachbarabschnitt schon

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/bosstab.py`, Abschnitte `IT BUFFS ITSELF` und
`BODY PARTS` des Detailpanels
**Umgebung:** beliebig

**Reproduktion:** Tab `Nightlords`, `Gladius` anklicken, die vier
Zahlenabschnitte des Panels von oben nach unten lesen.

**Erwartet:** A12 — jede Zahl nennt Einheit und Bezugsgroesse.
**Tatsaechlich:** `DAMAGE TAKEN`, `STATUS BUILDUP`, `STANCE` und
`IT IS WEAKENED` haben je einen Bezugssatz. `IT BUFFS ITSELF` zeigt
`Buff x1.35 attack · harder to stagger` ohne einen; `BODY PARTS` zeigt
`Part 1  x1.5 damage — soft spot` ohne einen und mit einem Platzhalternamen
(`PART_NAMES` ist leer, T-057 §10).

**Analyse:** AK-91 schreibt drei Erklaerzeilen vor und nennt diese beiden
Abschnitte nicht; T-057 hat fuer `IT IS WEAKENED` von sich aus eine
geschrieben. Dadurch stehen jetzt vier Abschnitte mit Bezug neben zwei ohne —
die Inkonsistenz ist sichtbarer als vorher.

**Auswirkung:** `x1.35 attack` — von welcher Grundlage aus, und wie lange?
Die Antwort steht teilweise in der Zeile `Set off by …`, aber der Faktor
selbst bleibt unbezogen.

**Vorschlag:** Je ein Satz im Stil der AK-91-Zeilen; fuer `BODY PARTS` steht
in `UI_SPEC.md` §8 bereits ein Streichvorschlag, der die Frage anders loesen
wuerde.

---

## 12. Die uebrigen Auftragspunkte

### 12.1 Build planner bei 513 px Fensterhoehe (Punkt 2)

Gemessen mit echtem Timer, weil `scripts/make_screenshots.py` vor zu fruehem
Fotografieren warnt:

| Tab | Fenster | Seite | `minimumSizeHint().height()` | senkrecht scrollbar | waagerechte Leiste | ueberlappende Beschriftungen |
|---|---|---|---|---|---|---|
| **Build planner** | 514 | 484 | 482 | 3 Bereiche | 0 | 0 |
| Effects & chances | 514 | 484 | 192 | 1 | 0 | 0 |
| Weapons & spells | 514 | 484 | 191 | 1 | 0 | 0 |
| Nightlords | 514 | 484 | 162 | 1 | 0 | 0 |
| Deep of Night | 514 | 484 | 68 | 1 | 0 | 0 |
| Red variants | 514 | 484 | 242 | 0 (passt) | 0 | 0 |
| World Events | 514 | 484 | 149 | 2 | 0 | 0 |

**Kein Befund.** Der `Build planner` ist bei 513 px vollstaendig bedienbar:
seine drei Bereiche (Nightfarer/Gefaess links, Reliktslots mitte, Werte
rechts) scrollen alle drei, keine Beschriftung liegt unter der Unterkante
ohne Bildlaufleiste, nichts ueberlappt. Die neue Fenster-Mindesthoehe ist
**514** logische px, nicht 513 — eine Rundungsstelle, kein Widerspruch.

### 12.2 Weapons: Suche eingeben und wieder loeschen (Punkt 3)

Bestaetigt und **so gewollt, soweit ich das beurteilen kann**: nach dem
Loeschen steht wieder `Weapons (1792)` → `Axe (77)` offen, mit 77 sichtbaren
Kacheln — derselbe Zustand wie beim Oeffnen des Tabs, nicht ein dritter.
Verloren geht dabei eine **von Hand geoeffnete** andere Gruppe; wer
`Greatsword` aufklappt, sucht und die Suche loescht, steht wieder bei `Axe`.
Das ist konsistent mit AK-83 und keine eigene Nummer wert. Der Befund an
dieser Stelle ist ein anderer: die Suche **mit vielen Treffern** (QA-143).

### 12.3 Die Mutationen aus T-057 und T-058 (Punkt 4)

Sechs der einundzwanzig nachgefahren, je in einem frischen Baum
(`git archive HEAD | tar -x`), volle schnelle Suite:

| Mutation | Herkunft | mein Ergebnis | berichtet | Abweichung |
|---|---|---|---|---|
| `card-grid-minimum-back-to-the-whole-row` | T-058 | 4 failed, 718 passed — `…card_is_drawn_whole[833]`, `[1067]`, `…count_above_the_grid…` + Anker | 3 (ohne Anker) | **keine** |
| `effect-column-back-to-the-leftovers` | T-058 | 11 failed, 711 passed — 10 Faelle + Anker, Liste identisch | 10 (ohne Anker) | **keine** |
| `effects-average-over-buckets-again` | T-057 | 3 failed, 719 passed — beide `test_effects_tab_display`-Faelle + Anker | 3 (mit Anker), 659 passed | **keine** (Suite ist von 662 auf 722 gewachsen) |
| `nightlord-weakened-step-inflated` | T-057 | 2 failed, 720 passed — `…every_weakened_step_in_the_data_reaches_the_panel` + Anker | 2 (mit Anker), 660 passed | **keine** |
| `deep-tab-back-outside-a-scroll-area` | T-058 | 3 failed, 719 passed — `…asks_the_window_for_more_than_the_limit`, `…last_line_of_deep_of_night_can_be_reached_by_scrolling` + Anker | 2 (ohne Anker) | **keine** |
| `events-day-sentence-for-every-event` | T-057 | 2 failed, 720 passed — `…day_sentence_names_this_event_s_own_split` + Anker | 2 (mit Anker), 660 passed | **keine** |

**Sechs von sechs bestaetigen die berichteten Zahlen genau**, einschliesslich
der Namen der fallenden Faelle. Die Trennung „Ankertest zaehlt nicht als
zweiter Waechter" ist in beiden Berichten korrekt angegeben, und in jedem der
sechs Laeufe faellt neben dem Anker mindestens ein Fall, den nur der
gepruefsten Mechanismus rot machen kann (L-003).

### 12.4 Die vier fest verdrahteten Spaltenzahlen (Punkt 5)

**Ja, der Picker geht heute reproduzierbar kaputt — und er tut es, ohne dass
man ihn schmaler zieht.** Siehe QA-141. Von den vier Stellen ist damit eine
am laufenden Fenster als Fehlbild belegt; `weaponslots.py:59` (`SLOT_COLUMNS`)
und `app.py:1416` (`i // 5`) habe ich **nicht** geprueft — siehe „Nicht
getestet".

---

## 13. Wo ich einen `power-user` haengen sehe (A11, nicht mein Urteil)

Meine Erwartung, nach Wahrscheinlichkeit geordnet:

1. **`Effects`, die beiden Chance-Spalten bei halbbreitem Fenster.** Er wird
   `vg chanc` und `est chanc` nicht auseinanderhalten und die Zahlen
   verwechseln (QA-140).
2. **`Effects`, Spalte `Stacking`.** Jede Zelle steht als `Stacks …` da; das
   Urteil, das die Spalte faellt, ist ohne Hovern unsichtbar, und rot
   bedeutet dort „zweite Kopie verschwendet", ohne dass es jemand sagt.
3. **`Effects`, `Relic slots` mit Werten bis 1 105.** Der Tooltip erklaert
   es richtig; die Zahl sieht trotzdem nach „Menge" aus. Genau diese Spalte
   ist die eine, die der `power-user` nicht verstanden hat — nachgelesen in
   `docs/berichte/T-054-power-user.md` Zeile 82-88 und 187 (*„eine Zahl wie
   864 als 'Pools' wirkt riesig"*), nicht aus zweiter Hand uebernommen. Der
   Kopf heisst jetzt `Relic slots` und traegt den erklaerenden Tooltip; ob
   das reicht, entscheidet der zweite Lauf.
4. **`Nightlords`, `Refills at x0.846`.** Der vorgeschriebene Satz sagt
   ehrlich, dass die Datei den Bezug nicht hergibt, und laesst den Leser mit
   „vergleiche es zwischen Nightlords" zurueck — brauchbar zum Vergleichen,
   nicht zum Planen. Dazu die zwei Gruentoene (QA-145).
5. **`Deep of Night`, `Reward multiplier x1.47`.** „The files do not say what
   it multiplies" ist die richtige Antwort und die unbefriedigendste; ich
   erwarte hier ein „und was mach ich damit".
6. **`Weapons`, Suche mit vielen Treffern** (QA-143) — er wird `sword` tippen.
7. **`Weapons`, `Scaling STR 54 · DEX 44`.** Wer die Buchstabengrade des
   Spiels kennt, wird sie zuordnen wollen; der Satz sagt ausdruecklich, dass
   das nicht geht.
8. **`Red variants`.** Der Tab beantwortet jetzt sichtbar „was ist das und wie
   viele", nachdem der `power-user` ihn als den ueberfluessigsten bezeichnet
   hat. Ob ihm das reicht, ist genau die offene Frage — ich erwarte, dass er
   weiterhin „wie viel staerker" fragt und die Antwort „sagen die Dateien
   nicht" als Luecke empfindet, nicht als Auskunft.

---

## 14. Explorationsprotokoll

**Was gehalten hat** (gepruefte Behauptungen, kein Befund):

* AK-68 auf allen sechs Tabs, gemessen an der **gerenderten Position** aller
  Beschriftungen, Eingabefelder, Auswahlfelder und Tabellen — Ueberschrift
  ist auf jedem Tab der oberste Text, der Fragesatz der zweite.
* AK-75: **0** Vorkommen von ` -- ` im gezeichneten Text, ueber elf
  Konfigurationen x sechs Tabs, zusaetzlich ueber einen Durchklick aller
  zehn Nightlord-Panels, aller 15 World-Events-Eintraege und aller sechs
  Karten des Red-variants-Tabs.
* AK-71: hoechste Tab-Mindesthoehe **242** px (Red variants) gegen die
  Schranke 860.
* AK-72/84/90: 10 von 10 Karten und 77 von 77 Kacheln vollstaendig, bei
  allen elf Konfigurationen; **keine** waagerechte Bildlaufleiste auf einem
  der sechs Tabs unter der Windows-Plattform.
* AK-77-Tooltips: 26 949 gekuerzte Zellen, 0 ohne vollen Text.
* AK-79/80/81, AK-92/93/94, AK-96, AK-99 (Beschriftungsteil), AK-100 ueber
  alle sechs Karten, AK-101 bis AK-105 — je oben belegt.
* Suite und Waechter unter vier Plattform-/Stil-Kombinationen.
* Effects-Tab: Sortieren nach `Avg chance`, Suche ohne Treffer (Tabelle 0
  Zeilen, Bestandszeile sagt `0 buffs … 0 curses`), Filter zuruecksetzen,
  Fensterbreite mehrfach aendern — die Spaltenaufteilung bleibt jedes Mal
  genau so breit wie der Sichtbereich, nie breiter.

**Was nicht gehalten hat — an mir, nicht am Programm:**

* Mein erster 513-px-Screenshot zeigte im `Build planner` uebereinander
  gezeichnete Attributzeilen. Das ist **kein Befund**: `make_screenshots.py`
  warnt genau davor, und mit einem echten Timer statt `processEvents`
  verschwand es. Ich habe die Messung wiederholt und zusaetzlich einen
  Ueberlappungstest ueber alle sichtbaren Beschriftungen gefahren: **0**.
* Meine Schriftmetrik meldete auf dem `Deep of Night`- und dem
  `Red variants`-Tab gekuerzte Zellen ohne Tooltip. Am Bild bricht die Zelle
  **um** statt zu elidieren und ist vollstaendig lesbar. Kein Befund.
* Die violetten Waffenkacheln sind Seltenheitsfarben, kein Fehlbild — mit
  `docs/screenshots/2026-09-05-T058/weapons-1067-after.png` gegengeprueft.

---

## 15. Offene Fragen

1. **An den director:** Deckt AK-83 den Suchfall mit ab, oder gilt sie nur
   fuer das erste Oeffnen? Davon haengt ab, ob QA-143 ein Befund oder eine
   bewusste Grenze ist.
2. **An den director:** Ist der **Spaltenkopf** von der Bedingung „jede
   gekuerzte Zelle traegt ihren vollen Text als Tooltip" mitgemeint? Ich
   lese ihn als mitgemeint, weil er ohne seine Zellen nichts erklaert; die
   engere Lesart ist genauso vertretbar. Nach der engeren Lesart ist die
   Bedingung vollstaendig erfuellt und QA-140 ein eigenstaendiger
   A13-Befund.
3. **An den ui-ux-designer:** `STATUS BUILDUP  Sleep 154` — die AK-91-Zeile
   sagt, wofuer die Zahl steht („how much status you have to apply"), nennt
   aber keine Einheit. Nach A12 woertlich fehlt sie; nach AK-91 woertlich ist
   der Satz erfuellt. Beide Lesarten sind vertretbar, die Entscheidung ist
   nicht meine.
4. **An den ui-ux-designer:** `Red variants` fuellt am Standardmass rund ein
   Drittel der Seite, `Deep of Night` die ganze. Ist das unter „gestalterisch
   konsistent" (A13) ein Thema, oder ist eine kurze Tabelle einfach kurz?
5. **An den ui-ux-designer:** Im World-Events-Buff `Power to Balance the
   World` steht `invulnerable · +10% attack power, all damage types for 45s`.
   Nach AK-103 ist es richtig, dass `invulnerable` keine Dauer bekommt
   (`duration = 0.0`); auf dem Bildschirm sieht es so aus, als gaelten die
   45 s fuer beides.

---

## 16. Nicht getestet

* **A11** — ausdruecklich nicht mein Urteil; ein zweiter `power-user`-Lauf
  laeuft dafuer. Abschnitt 13 ist eine Erwartung, kein Nachweis.
* **Der Berater (S7 bis S11)**, QA-096/097/113 und die dreizehn
  Streichvorschlaege — per Auftrag ausgenommen.
* **`weaponslots.py:59` (`SLOT_COLUMNS = 3`) und `app.py:1416`
  (`i // 5`)** — die zwei uebrigen festen Spaltenzahlen. Ich habe den
  Reliktpicker geprueft, weil der Auftrag ihn nennt; die beiden anderen
  liegen im `Build planner` und ich habe die Zeit in die sechs Tabs gesteckt.
  Die Eigenschaft besteht dort unveraendert fort (L-006: die Suche nach
  `^[A-Z_]*COLUMNS *= *[0-9]+` und nach `addWidget\(.*//.*,` findet beide
  weiterhin).
* **Die uebrigen fuenfzehn Mutationen** aus T-057/T-058 — sechs nachgefahren,
  das ist eine Stichprobe und keine Vollpruefung.
* **Ein gebautes Artefakt** (GOAL A9) — dieser Lauf misst den Quellstand.
* **Linux und macOS**, andere Windows-Skalierungen als 150 %, und ein
  System mit vergroesserter Schrift. Die Offscreen-Messungen sind der
  naechstliegende Hinweis darauf, was dort passiert: dort werden auf dem
  Weapons-Tab 62 Beschriftungen gekuerzt (`vs standard`, `Blood Loss
  buildup`) und der `Red variants`-Tab zieht bei 833 und 1067 px eine
  waagerechte Bildlaufleiste. Unter der Windows-Plattform tritt beides
  **nicht** auf. Das ist ein Hinweis, kein Befund.
* **Tastaturbedienung, Bildschirmleser, Kontrastwerte** — kein Auftrag.

---

## 17. QA-Log — Fortschreibung fuer `qa/findings.md`

Fuer die Haupttabelle (Spalten wie im Kopf der Datei):

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-125 | Spalte `Pools` zaehlt keine Pools | P2 | Major | developer, ui-ux-designer | Widget, 1600 px | **behoben** — Kopf `Relic slots`, AK-78-Tooltip wortgleich, die verbotene Pool-Zeile 0 Treffer | 2026-09-05 |
| QA-126 | `Avg chance` ungewichtet | P2 | Major | developer, ui-ux-designer | Widget, Einzelfall | **behoben** — `[Wylder] Improved Mind, Reduced Vigor` 0.91 %; `per relic effect slot` genau einmal; beide alten Definitionen 0 Treffer | 2026-09-05 |
| QA-127 | `Copies`/`Tier` filterabhaengig | P3 | Major | developer | Widget, 3 Filterzustaende | **behoben** — `Continuous HP Recovery` traegt `3 of 3`/`1 of 3` ungefiltert, `1 of 3` bei Red, `3 of 3` bei Blue | 2026-09-05 |
| QA-128 | Systemisch: Zahlen ohne Bezugsgroesse | P2 | Major | ui-ux-designer, developer, director | Widget, alle 6 Tabs | **teilweise behoben** — die 10 benannten Stellen gedeckt; offen: QA-149 (2 Abschnitte im Nightlord-Panel), QA-148 (Runen-Leiter) | 2026-09-05 |
| QA-129 | Debuff-Zahlen bei den falschen Bossen | P2 | Major | developer, ui-ux-designer | alle 10 Panels | **behoben** — getippte Zahlen weg, 7 von 10 zeigen `IT IS WEAKENED` aus `ladder.down`, Sichtung in `#7fae72` | 2026-09-05 |
| QA-130 | Maris `Refills at x-1` | P3 | Major | developer | Panel Maris | **behoben** — `Refills at — not in the game's files` | 2026-09-05 |
| QA-131 | Adels Schwaechen-Abschnitt fehlt | P3 | Major | developer, ui-ux-designer | Panel Adel | **behoben** — Abschnitt und Notiz erscheinen; Farblegende bleibt offen als QA-145 | 2026-09-05 |
| QA-132 | `For example` ignoriert die Karte | P2 | Major | developer, ui-ux-designer | 6 Karten x 5 Breiten | **teilweise behoben** — `Examples (any map)` + Kopftooltip + `— the files name none`; die Breitenzusicherung faellt bei 833 px → QA-144 | 2026-09-05 |
| QA-133 | Einmalige Belohnung mit Dauer | P2 | Major | developer | alle 15 Eintraege | **behoben** — `10,000 runes` ohne Dauer, `invulnerable for 5s` mit, kein `for 0s` | 2026-09-05 |
| QA-134 | Zwei Saetze auf allen 11 Ereignissen | P3 | Minor | ui-ux-designer, developer | alle 11 | **behoben** — 11 verschiedene Tagessaetze, Judgment 19/20, Fire-Summoning 9/30 | 2026-09-05 |
| QA-135 | Quellensprache auf dem Bildschirm | P3 | Minor | ui-ux-designer, developer | alle 15 Eintraege | **behoben** — 6 verbotene Zeichenketten 0 Treffer, `rune_scaling` erscheint; Restfrage zum Wortlaut → QA-148 | 2026-09-05 |
| QA-136 | `Scale-Bearing Merchant` zweimal | P4 | Minor | ui-ux-designer, director | Listeninhalt | **behoben** — einmal in der Liste | 2026-09-05 |
| QA-137 | Fuenf Tabs ohne Waechter | P2 | Major | developer, director | 6 Mutationen nachgefahren | **behoben** — 92 neue Faelle; 6 von 6 Stichproben toeten genau die berichteten Faelle | 2026-09-05 |
| QA-138 | Drei Tabs sagen ihre Frage nicht | P3 | Minor | ui-ux-designer | gerenderte Position, 6 Tabs | **behoben** — Ueberschrift und Fragesatz sind auf jedem Tab der erste und zweite Text | 2026-09-05 |
| QA-139 | `Spell power` gegen `spell scaling` | P4 | Trivial | ui-ux-designer | 2 Suchmasken ueber `nrplanner/` | **behoben** — 0 Treffer in angezeigtem Text, Rest nur Kommentare | 2026-09-05 |
| QA-140 | **Effects: Spaltenkoepfe mitten im Wort beschnitten; `vg chanc` gegen `est chanc` bei 1067 px** | P3 | Major | developer, ui-ux-designer | Screenshot + `sectionSize` bei 5 Breiten x 2 Plattformen | offen | 2026-09-05 |
| QA-141 | **Relic picker schneidet die 5. Kartenspalte schon bei seiner eigenen Startbreite an (11 von 55 Karten)** | P2 | Major | developer, director | Screenshot + gerenderte Rechtecke bei 1030/900/700 px | offen | 2026-09-05 |
| QA-142 | **`vs standard` ordnet seine Gruppen bei jedem Programmstart anders (`set`-Iteration)** | P3 | Minor | developer | 4 Hashseeds, 4 Reihenfolgen | offen | 2026-09-05 |
| QA-143 | **Weapons: Suche mit mehr als 60 Treffern zeigt wieder die leere Flaeche aus DR-017** | P3 | Minor | ui-ux-designer, director | Widget, 6 Sucheingaben | offen | 2026-09-05 |
| QA-144 | **Red variants: `Examples (any map)` bei 833 px breiter als `What can be red` (AK-99)** | P3 | Minor | developer | `sectionSize` bei 5 Breiten | offen | 2026-09-05 |
| QA-145 | **Nightlords: drei Bedeutungen auf `#6fbf73`, dazu `#7fae72` ohne Legende (AK-74)** | P3 | Minor | ui-ux-designer | gerendertes HTML, 10 Panels | offen | 2026-09-05 |
| QA-146 | **Waechter und Berichtszahlen messen unter `windowsvista`, das Programm laeuft unter `fusion` (bis 58 px Unterschied); offscreen kann 833 px gar nicht darstellen** | P3 | Minor | developer, director | dieselbe Messung unter 4 Kombinationen | offen | 2026-09-05 |
| QA-147 | **Nightlords bei 833 px: leeres Detailpanel haelt 330 von 833 px** | P4 | Minor | ui-ux-designer | Screenshot | offen | 2026-09-05 |
| QA-148 | **World Events: Runen-Leiter ohne Bezugspunkte, Satzrest nach dem Entfernen des Param-Namens** | P4 | Trivial | developer, ui-ux-designer | Bildschirmtext gegen Datensatz | offen | 2026-09-05 |
| QA-149 | **Nightlords: `IT BUFFS ITSELF` und `BODY PARTS` ohne Bezugsgroesse, die Nachbarabschnitte mit** | P4 | Minor | ui-ux-designer | 10 Panels | offen | 2026-09-05 |

---

## 18. Zusammenfassung an den director

**Befunde nach Prioritaet:** P1 **0** · P2 **1** (QA-141) · P3 **6**
(QA-140, 142, 143, 144, 145, 146 — davon QA-146 eine Messfrage, kein
Nutzerfehler) · P4 **3** (QA-147, 148, 149). Kein Blocker, kein Critical,
kein Datenverlust, kein Sicherheitsbefund.

**Releasefaehigkeit gegen A10 bis A14:** A10 und A14 sind erfuellt. A12 und
A13 sind es fuer vier bzw. drei der sechs Tabs; keiner der offenen Punkte
macht einen Tab unbenutzbar. Der Sprung seit dem Erstaudit ist gross:
dreizehn von fuenfzehn Befunden sind belegbar geschlossen, und die fuenf
zuvor voellig ungedeckten Tabs haben Waechter, die in sechs von sechs
Stichproben genau das toeten, was sie sollen.

**Mindestens behoben sein muss vor der Abnahme:**

1. **QA-141** — der Reliktpicker zeigt heute ohne jedes Zutun angeschnittene
   Karten. Er liegt zwar im ausgenommenen `Build planner`, ist aber der
   Hauptweg zum Berater, und `CardGrid` liegt fertig da.
2. **QA-140** — die Bedingung, unter der du die AK-77-Abweichung genehmigt
   hast, deckt die Spaltenkoepfe nicht. Entweder die Koepfe werden von der
   Zusicherung mitgetragen (dann ist es ein Fix), oder du schraenkst die
   Bedingung ausdruecklich auf die Zellen ein (dann bleibt QA-140 ein
   gewoehnlicher A13-Befund). **Die Entscheidung ist deine**, meine Messung
   liegt bei.
3. **QA-146** — solange die Waechter unter einem anderen Stil messen als das
   Programm laeuft, ist jede kuenftige Pixelzusage um bis zu 58 px daneben.
   Der Fix ist zwei Zeilen in `tests/rendered.py`.

Alles Uebrige ist mit einem Vermerk auslieferbar. **A11 fehlt** und ist die
einzige Luecke, die dieser Lauf grundsaetzlich nicht schliessen kann.
