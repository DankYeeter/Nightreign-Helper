# T-038 — Programm-Angriffskraft gegen die Fan-Messung (Lv12, 8 Nightfarer) und gegen die RPS-Skalierungsbuchstaben (qa-engineer)

```
STATUS: erledigt
AUFTRAG: T-038 - Programm-Angriffskraft gegen die Fan-Messung (Lv12, 8 Nightfarer) und gegen die RPS-Skalierungsbuchstaben messen
GELESEN: docs/tasks/T-038.md, GOAL.md, docs/state.md (Abschnitt "Parallele Session"),
  nrplanner/weapons.py, nrplanner/damage.py (Kopf-Docstring), nrplanner/datasource.py,
  nrplanner/model.py (evaluate_curve), nrdata/extract.py (Helden- und Waffen-Extraktion,
  _load_text, STAT_FIELDS), nrdata/param.py, README.md ("Known limits"), qa/findings.md,
  CLAUDE.md; Messdaten: scratchpad/nightreign_weapon_ap_lv12.csv (310 Zeilen),
  scratchpad/rps_nightreign_weapons.tsv (387 Zeilen); Spielinstallation
  D:\SteamLibrary\...\NIGHTREIGN (regulation.bin, data_version 10350000) lesend.
GEÄNDERT: docs/berichte/T-038-qa-engineer.md (diese Datei, neu). Sonst keine Datei im
  Arbeitsbaum, kein Git-Zustand angefasst. Messskripte liegen ausserhalb des Repos unter
  <scratchpad>\t038\, der Messklon unter <scratchpad>\nr-t038 (Commit 64174eb).
ANNAHMEN:
  1. Der Arbeitsbaum steht NICHT auf 64174eb: HEAD ist 690db5f ("test(advisor): den
     Fingerabdruck gegen ein gehaltenes Custom relic sichern"), die parallele Session hat
     ihre Aenderungen inzwischen committet. Mein Klon steht auf dem im Auftrag genannten
     64174eb; die drei fuer die Messung benutzten Dateien (weapons.py, model.py,
     extract.py) sind zwischen 64174eb und 690db5f unveraendert (git diff --stat: nur
     advisor/, differential/mutate.py, tests/). Die Zahlen gelten daher fuer beide Staende.
  2. Die Fan-Tabelle misst die im Spiel angezeigte Angriffskraft der Waffe in **ihrer
     eigenen Raritaet** ohne Verstaerkung. Belegt, nicht angenommen: der Faktor ist nur
     bei applied_upgrade=0 konstant (Abschnitt 4, Hypothese f).
  3. Die 28 Stab-/Siegel-Zeilen der Fan-Tabelle messen **nicht** Angriffskraft, sondern
     die Zauber-/Anrufungsskalierung. Belegt in Abschnitt 8, nicht angenommen.
NÄCHSTER: director (Entscheid ueber QA-IDs, Prioritaet und ob der Faktor ins Programm
  soll; die zwei offenen Fragen an den App Designer stehen in Abschnitt 11)
BLOCKIERT DURCH: nichts
```

---

## 0. Ergebnis in drei Saetzen

Der Faktor ist **0,6 — exakt**, und das Spiel **schneidet ab** (nicht rundet):
`Anzeige = floor(0,6 × weapons.rate)`. Das Modell trifft **1965 von 2256** Messwerten
(87,1 %) **auf die angezeigte ganze Zahl genau**; sechs der acht Nightfarer liegen
zwischen 98,9 % und 99,6 %. Der Rest ist nicht Rauschen, sondern hat vier benannte
Ursachen, davon **zwei in der Fan-Quelle** (Guardian-Spalte auf Level 11, Duchess-Spalte
gemischt) und **zwei im Spiel, die das Programm nicht kennt** (Raider ×1,1819 auf
Greataxe/Great Hammer; Revenant's Cursed Claws ×0,87 fuer jeden ausser dem Revenant).

Die Ursache des Faktors liegt **nicht** in den Spieldaten, die das Programm liest:
Hypothesen (a) bis (e) sind alle einzeln widerlegt, (f) ebenfalls. Der Faktor ist eine
Konstante ausserhalb von EquipParamWeapon / ReinforceParamWeapon / CalcCorrectGraph /
AttackElementCorrectParam / HeroStatusParam.

---

## 1. Risiko-Briefing (vor der Messung erstellt, Reihenfolge eingehalten)

1. **Groesstes Risiko: die Zuordnung.** 310 Fan-Namen gegen 1793 Programmeintraege, mit
   Abkuerzungen und Tippfehlern. Eine falsche Zuordnung erzeugt genau die Art Ausreisser,
   die man danach als Spielmechanik fehldeutet. Deshalb zuerst, und mit einem von den
   Namen **unabhaengigen** Gegencheck (Klassenbloecke der Tabellenreihenfolge).
2. **Zweitgroesstes Risiko: der Faktor ist keine Konstante.** Zwoelf Stichproben koennen
   einen Faktor vortaeuschen, den 2256 Messwerte nicht halten. Deshalb kein Mittelwert,
   sondern Intervallschnitt: jede Messung schraenkt k ein, und entweder es bleibt ein k
   uebrig oder es bleibt keins.
3. **Drittes Risiko: Verwechslung von Quelle und Programm.** Eine Abweichung kann am
   Programm, an der Fan-Messung oder am Spiel liegen. Deshalb pro Abweichung erst die
   billigste Erklaerung pruefen (falsches Level in der Quelle), bevor eine Spielmechanik
   erfunden wird.
4. **Viertes Risiko: die Waffen mit gesplittetem Schaden und eigener Kurve** — dort haengen
   drei Unbekannte zusammen (Kurven-ID, AEC-Regel, Rundung je Schadensart).
5. **Fuenftes Risiko: Staebe/Siegel.** Fuenf leere Spalten in der Quelle sind ein Hinweis,
   dass dort etwas anderes gemessen wurde als bei Waffen.

Alle fuenf wurden in dieser Reihenfolge abgearbeitet; alle fuenf haben getragen.

---

## 2. Zuordnung: 310 von 310, keine Nichttreffer

Fuenf Normalisierungsstufen, **global und exklusiv** vergeben (eine Waffe, die eine
sicherere Stufe belegt hat, ist fuer die unsichereren weg), danach eine Nachbarschafts-
Stufe. Der Kandidatenvorrat sind die 310 Familienkoepfe (`id % 10000 == 0`); die
Infusionsvarianten (+500…+1100) sind ausgeschlossen, weil die Fan-Tabelle sie nicht fuehrt.

| Stufe | Regel | Treffer |
|---|---|---|
| exact | Kleinschreibung, Akzente/Apostrophe entfernt, Suffix `; 30 bleed` abgeschnitten | 251 |
| abbrev | `GS`→greatsword, `SS`→straight sword, `CS`→curved sword | 21 |
| squash | Leerzeichen egal (`Short bow` = `Shortbow`) | 12 |
| stem | Possessiv-/Plural-s egal (`Lordsworn` = `Lordsworn's`) | 12 |
| nostop | `the`/`of` egal (`Staff of Guilty` = `Staff of the Guilty`) | 2 |
| fuzzy | naechster Name, nur bei eindeutigem Abstand > 0,06 | 12 |
| **Summe** | | **310 (100 %)** |

**Nichttreffer: keine.** Die 14 Zuordnungen der beiden unsichersten Stufen im Wortlaut,
jede einzeln nachgesehen:

| Fan-Zeile | Programm | Bewertung |
|---|---|---|
| `Flameberge; 42 bleed` | Flamberge | Tippfehler der Quelle |
| `Ordovis GS` | Ordovis's Greatsword | Abkuerzung + Possessiv |
| `Morgots Cursed Sword` | Morgott's Cursed Sword | Tippfehler |
| `Warwick` | Warpick | Tippfehler |
| `Scepter of All Knowing` | Scepter of the All-Knowing | fehlendes „the" |
| **`Goldens Halberd`** | **Golem's Halberd** | **Tippfehler; Zeile 181 steht im Kolossal-Block, `Golden Halberd` steht separat als Zeile 229 → beide Zeilen sind verschiedene Waffen** |
| `Celebrant's Rob Rake` | Celebrant's Rib-Rake | Tippfehler |
| `Bolt of Gransaxx` | Bolt of Gransax | Tippfehler |
| `Cestus` / `Spiked Cestus` | Caestus / Spiked Caestus | Schreibvariante |
| `Crepus Black Key Crossbow` | Crepus's Black-Key Crossbow | Possessiv + Bindestrich |
| `Recluse Staff` | Recluse's Staff | Possessiv |
| `Staff of Guilty` | Staff of the Guilty | fehlendes „the" |
| `Finger Seal` | Finger Seal (id 34750000) | **zwei Datensaetze gleichen Namens** (34000000 und 34750000), in allen gemessenen Feldern identisch (base 25, correctFaith 100) → die Wahl ist zahlenmaessig folgenlos |

**Unabhaengiger Gegencheck (nicht Teil der Zuordnungsregel):** die Fan-Tabelle ist nach
Waffenklasse sortiert. Fuer jede zugeordnete Zeile wurde geprueft, ob ihr `wep_type` im
Fenster der sechs Nachbarzeilen vorkommt. **0 Ausreisser von 310.** Genau dieser Check hat
`Gargoyles Black blade` (Zeile 48, Greatsword-Block → *Gargoyle's Blackblade*, id 3210000)
von `Gargoyles Black Blades` (Zeile 118, Twinblade-Block → id 10090000) getrennt; die
erste Fassung des Matchers hatte beide auf dieselbe Waffe gelegt.

Verteilung der zugeordneten Waffen: Raritaet 0 → 78, 1 → 116, 2 → 90, 3 → 26. 62 Zeilen
tragen ein Status-Suffix, 28 sind Katalysatoren (`wep_type` 57/61).

---

## 3. Verhaeltnis-Statistik (roh, Programm bei eigener Raritaet, Level 12)

2256 Vergleichspaare (282 Waffen × 8 Nightfarer; die 28 Katalysatoren separat in
Abschnitt 8). Alles auf der **ungerundeten** Programmzahl.

**Global:** Median 0,5968 · Min 0,5192 · Max 0,7078.

### je Nightfarer

| Nightfarer | n | Median | Min | Max |
|---|---|---|---|---|
| Wylder | 282 | 0,5977 | 0,5192 | 0,6184 |
| **Guardian** | 282 | **0,5824** | 0,5217 | 0,6095 |
| Ironeye | 282 | 0,5976 | 0,5225 | 0,6184 |
| **Duchess** | 282 | **0,5849** | 0,5211 | 0,6131 |
| Raider | 282 | 0,5978 | 0,5249 | **0,7078** |
| Revenant | 282 | 0,5972 | 0,5903 | 0,6247 |
| Recluse | 282 | 0,5970 | 0,5223 | 0,6183 |
| Executor | 282 | 0,5979 | 0,5265 | 0,6121 |

Die Sonde des Directors ist bestaetigt und praezisiert: Guardian faellt heraus — und
**Duchess ebenfalls**, was zwoelf Stichproben nicht zeigen konnten.

### je Raritaet und je Schadensart-Zusammensetzung

| Gruppe | n | Median | Spannweite |
|---|---|---|---|
| Raritaet 0 (Common) | 568 | 0,5958 | 0,5192–0,7078 |
| Raritaet 1 | 832 | 0,5967 | 0,5746–0,7078 |
| Raritaet 2 | 656 | 0,5971 | 0,5739–0,7077 |
| Raritaet 3 (Legendary) | 200 | 0,5978 | 0,5772–0,7075 |
| rein physisch | 1552 | 0,5964 | 0,5704–0,7078 |
| physisch + elementar | 688 | 0,5973 | 0,5192–0,7077 |
| rein elementar | 16 | 0,5974 | 0,5914–0,5995 |

**Weder Raritaet noch Schadensart verschieben den Faktor.** Die Spannweiten stammen
komplett aus den vier in Abschnitt 5 benannten Sonderfaellen.

### je Waffenklasse — die aussagekraeftigste Tabelle

Quotient **Spiel / (0,5972 × Programm bei Level 12)**; 1,000 heisst „durch den Faktor
allein erklaert". Ausschnitt; die vollstaendigen 27 Klassen stehen im Messlauf
`residual_map.py`.

| Klasse | Wylder | Guardian | Ironeye | Duchess | Raider | Revenant | Recluse | Executor |
|---|---|---|---|---|---|---|---|---|
| Dagger | 1,000 | 0,974 | 0,998 | 0,970 | 0,995 | 0,998 | 0,996 | 1,000 |
| Greatsword | 1,002 | 0,974 | 1,002 | 0,982 | 1,001 | 1,000 | 1,001 | 1,001 |
| Katana | 1,001 | 0,973 | 1,000 | 0,969 | 1,001 | 0,997 | 0,999 | 1,001 |
| **Greataxe** | 1,000 | 0,979 | 0,999 | 0,997 | **1,183** | 1,000 | 0,999 | 1,001 |
| **GreatHammer** | 1,001 | 0,976 | 1,003 | 0,993 | **1,183** | 0,997 | 1,000 | 1,003 |
| Colossal | 1,000 | 0,980 | 1,002 | 1,001 | 1,002 | 1,001 | 1,002 | 1,002 |
| Bow | 0,997 | 0,969 | 0,998 | 0,967 | 0,999 | 0,998 | 0,993 | 0,999 |
| Crossbow | 0,999 | 0,999 | 0,999 | 0,999 | 0,999 | 0,999 | 0,999 | 0,999 |
| Ballista | 1,003 | 1,003 | 1,003 | 1,003 | 1,003 | 1,003 | 1,003 | 1,003 |
| **Spaltenmedian** | 1,0008 | **0,9752** | 1,0007 | **0,9794** | 1,0010 | 0,9999 | 0,9996 | 1,0012 |

Drei Dinge stehen hier ablesbar nebeneinander: die Guardian- und Duchess-Abweichung ist
**gleichmaessig ueber alle Klassen** (also kein Waffenthema), die Raider-Abweichung ist
**auf genau zwei Klassen beschraenkt** (also kein Heldenthema), und Crossbow/Ballista —
die Waffen **ohne jede Attributskalierung** — stehen bei jedem Helden auf demselben Wert.
Der letzte Punkt ist der Hebel fuer Abschnitt 4.

---

## 4. Der beste Faktor: k = 0,6 exakt, mit Abschneiden

### 4.1 Herleitung (L-001: die Zahl traegt ihr Rezept)

Neun Waffen der Fan-Tabelle haben **keine Attributskalierung** (alle correct-Werte 0):
sieben Armbrueste, Hand Ballista, Jar Cannon. Bei ihnen kann die Anzeige keine Kurve
enthalten, also gilt `Anzeige = D(k × attackBase)` mit genau einer Unbekannten. Jede
Ablesung schraenkt k auf ein Intervall ein:

- Anzeige rundet: `k ∈ [(g−0,5)/base, (g+0,5)/base)`
- Anzeige schneidet ab: `k ∈ [g/base, (g+1)/base)`

Geschnitten ueber alle 9 Waffen × 8 Nightfarer:

| Anzeigeregel | Schnittmenge | Ergebnis |
|---|---|---|
| runden | [0,598459 , 0,597973) | **leer — die Anzeige rundet nicht** |
| **abschneiden** | **[0,599315 , 0,600928)** | **konsistent, Breite 0,0016** |

`k = 0,6` liegt in diesem Intervall. Kein anderer „glatter" Wert tut das (0,595 und
0,5972 liegen ausserhalb). Die Belegdaten: Soldier's Crossbow 148 → 88, Light Crossbow
149 → 89, Heavy Crossbow 151 → 90, Arbalest 154 → 92, Crepus's Black-Key 186 → 111,
Full Moon 186 → 111, Pulley 106 → 63, Hand Ballista 431 → 258, Jar Cannon 584 → 350.

### 4.2 Zweiter, unabhaengiger Nachweis derselben Zahl (L-003: mechanismus-gebundenes Signal)

Eine Kleinste-Quadrate-Schaetzung auf **allen** Waffen liefert je Held k = 0,5972…0,5980 —
also scheinbar *nicht* 0,6. Das ist kein Widerspruch, sondern die vorhergesagte Folge des
Abschneidens: unter `g = floor(0,6·p)` ist `E[g] = 0,6p − 0,5`, und damit

    k_LS = Σp·g / Σp² = 0,6 − 0,5 · Σp/Σp²

| Nightfarer | vorhergesagt aus der Formel | gemessen (LS-Fit) |
|---|---|---|
| Wylder | 0,59798 | **0,59791** |
| Executor | 0,59788 | **0,59796** |

Die Abweichung des LS-Schaetzers von 0,6 ist auf 1·10⁻⁴ genau die Groesse, die das
Abschneiden erzwingt. Ein anderer wahrer Faktor als 0,6 wuerde diese Uebereinstimmung
zerstoeren. **Der Faktor trifft Grundschaden und Skalierung gleich** — das war die
Sonden-Hypothese des Directors und sie haelt ueber 2256 Faelle: da AR linear im
Grundschaden ist, ist „0,6 × Gesamtzahl" identisch mit „0,6 × Grundschaden, Skalierung
unveraendert"; die Fan-Daten koennen die beiden Lesarten nicht trennen, und sie muessen es
auch nicht.

### 4.3 Restfehler des Gesamtmodells

Modell: `Anzeige = floor(0,6 × (Σbase + Σscaled))`, Attribute aus `hero["levels"]`,
eigene Raritaet, keine Effekte — plus die zwei in Abschnitt 5 belegten Korrekturen
(Guardian auf Level 11, Raider ×1,1819 auf `wep_type` 19/23).

| Ebene | n | exakte Treffer | Median rel. Fehler | p95 | max |
|---|---|---|---|---|---|
| **alle** | **2256** | **87,1 %** | **0,47 %** | 2,88 % | 15,55 % |
| Wylder | 282 | 99,3 % | 0,40 % | 0,90 % | 15,55 % |
| Guardian (L11) | 282 | 87,2 % | 0,41 % | 1,19 % | 12,72 % |
| Ironeye | 282 | 98,9 % | 0,40 % | 0,95 % | 14,84 % |
| **Duchess** | 282 | **14,5 %** | 2,58 % | 3,96 % | 15,15 % |
| Raider | 282 | 98,2 % | 0,39 % | 1,14 % | 14,31 % |
| Revenant | 282 | 99,6 % | 0,47 % | 1,15 % | 3,96 % |
| Recluse | 282 | 99,3 % | 0,51 % | 1,42 % | 14,88 % |
| Executor | 282 | 99,3 % | 0,35 % | 0,92 % | 13,97 % |
| Raritaet 0 / 1 / 2 / 3 | 568/832/656/200 | 88,4 / 88,8 / 85,1 / 82,5 % | ≤0,63 % | ≤3,40 % | |
| rein phys. / gesplittet / rein elem. | 1552/688/16 | 89,2 / 82,1 / 87,5 % | ≤0,64 % | ≤2,95 % | |

Ohne die beiden Korrekturen: 75,8 % exakt. Guardian-Korrektur allein: 86,1 %. Beide: 87,1 %.
**Zieht man die Duchess-Spalte ab** (deren Quelle nachweislich gemischt ist, Abschnitt 5.2),
liegt das Modell bei **97,5 % exakter Treffer ueber 1974 Ablesungen.**

### 4.4 Geltungsbereich dieser Zusicherung

Gemessen fuer: **Level 12** (plus zwei Anker auf Level 1 und 15, Abschnitt 6f), **acht**
Nightfarer (Scholar und Undertaker sind in der Quelle nicht enthalten), **eigene
Raritaet ohne Verstaerkung** (`applied_upgrade = 0`), **ohne Relikte, ohne Effekte**,
310 Waffen ohne Infusionsvarianten. Fuer verstaerkte Waffen (`applied_upgrade > 0`),
fuer infundierte Varianten, fuer Scholar/Undertaker und fuer Level ausser 1/12/15 ist der
Faktor **nicht gemessen** — er ist dort nur plausibel, nicht belegt.

---

## 5. Was der Faktor nicht erklaert — vier benannte Reste

### 5.1 Guardian: die Fan-Spalte steht auf Level 11, nicht 12

Fuer jede Fan-Spalte wurde geprueft, welches der Level 8–15 sie am besten reproduziert
(k je Kandidat frei gefittet, Bewertung = Median der Abweichung auf der Anzeigezahl):

| Nightfarer | bestes Level | k dort | Median Abw. | Anteil < 0,5 AP |
|---|---|---|---|---|
| Wylder | **12** | 0,59795 | 0,251 | 86,9 % |
| **Guardian** | **11** | 0,59846 | 0,306 | 66,7 % |
| Ironeye | **12** | 0,59779 | 0,250 | 88,7 % |
| Duchess | (keins, s. 5.2) | — | 0,635 | 44,0 % |
| Raider | **12** | 0,59791 | 0,235 | 88,3 % |
| Revenant | **12** | 0,59755 | 0,264 | 83,7 % |
| Recluse | **12** | 0,59722 | 0,250 | 86,5 % |
| Executor | **12** | 0,59799 | 0,246 | 89,4 % |

Waffenweise ausgezaehlt (nur Waffen, bei denen sich die Level um mehr als 2 AP
unterscheiden): Guardian **265 von 271 Waffen auf Level 11**, 2 auf Level 12. Kontrolle:
Wylder 269/271 auf Level 12, Ironeye 268/271 auf Level 12. Das Verfahren entscheidet also
scharf.

Guardian Level 11 (STR 34 / DEX 24) gegen Level 12 (STR 36 / DEX 26) — die Programmzahlen
sind korrekt, die **Quelle** ist es an dieser Stelle nicht. Damit faellt die
Guardian-Anomalie der Director-Sonde vollstaendig weg: Guardians k ist 0,59846 und damit
das gleiche wie bei allen anderen.

### 5.2 Duchess: die Fan-Spalte ist in sich gemischt

Kein einziges Level erklaert die Duchess-Spalte. Waffenweise: **198 Waffen passen auf
Level 11, 69 auf Level 12**, 2 auf Level 10. Und die Mischung ist nicht zufaellig verteilt,
sondern folgt der Zeilenordnung des Tabellenblatts:

| Zeilen | L11 | L12 |
|---|---|---|
| 0–39 | 37 | 1 |
| 40–79 | 27 | 13 |
| 80–119 | 39 | 1 |
| 120–159 | 21 | 18 |
| **160–199** | **10** | **30** |
| 200–239 | 36 | 3 |
| 240–279 | 28 | 3 |

Blockweises Muster = in mehreren Sitzungen auf unterschiedlichem Stand erfasst. Mit
Level 11 gerechnet steigt die Duchess-Trefferquote von 14,5 % auf 33,7 % und der mediane
relative Fehler faellt von 2,58 % auf 0,89 % — beides bleibt weit unter dem, was die
anderen sieben Spalten erreichen. **Die Duchess-Spalte ist als Messquelle nicht
brauchbar.**

### 5.3 Raider auf Greataxe und Great Hammer: ×1,1819, ungeklaert

Alle 25 Waffen der `wep_type` 19 und 23, nur beim Raider, mit einem sehr engen Faktor:

| | Wert |
|---|---|
| implizierter Multiplikator | Median **1,1819**, Min 1,1786, Max 1,1839 (n = 25) |
| Kontrolle Wylder auf denselben Waffen | 0,9989 (0,9964–1,0034) |
| Kontrolle Executor | 1,0016 (0,9927–1,0032) |
| Kontrolle Raider auf `wep_type` 41 (Kolossal) | 0,9983–1,0032 |

Geprueft und **widerlegt**: (i) Zeilenversatz im Tabellenblatt — die Ablesung passt zu
keiner Nachbarwaffe; (ii) Zweihaendig gefuehrt (STR × 1,5) — ergibt Faktoren 0,995–1,052
statt 1,0, und fuer Brick Hammer waere ein Kurvenwert von 250 noetig, waehrend Kurve 0 bei
240 endet; (iii) eine Passiv-Faehigkeit — der Text des Raiders (`HeroParam
passiveAbilityTitleId` 415014, „Fighter's Resolve": *Taking damage boosts Retaliate
potency. Attack power boosted when HP is greatly reduced.*) nennt keine Waffenklasse.
**Ungeklaert; als Beobachtung gemeldet, nicht als Mechanik behauptet.**

### 5.4 Revenant's Cursed Claws: ×0,87 fuer jeden ausser dem Revenant

| Nightfarer | Spiel | Modell | Spiel/Modell |
|---|---|---|---|
| Wylder | 50 | 57,78 | 0,8654 |
| Guardian | 54 | 60,87 | 0,8872 |
| Ironeye | 45 | 51,68 | 0,8708 |
| Duchess | 55 | 63,33 | 0,8684 |
| Raider | 51 | 58,30 | 0,8748 |
| **Revenant** | **83** | **83,05** | **0,9994** |
| Recluse | 71 | 81,56 | 0,8705 |
| Executor | 42 | 47,87 | 0,8774 |

Fuer den **Besitzer** der Waffe stimmt das Modell auf 0,06 % genau, fuer alle anderen fehlen
~13 %. Gegenprobe ueber **alle acht** Startwaffen: kein anderer Fall zeigt das Muster
(Wylder's Greatsword, Guardian's Halberd, Ironeye's Bow, Duchess' Dagger, Raider's
Greataxe, Executor's Blade liegen bei jedem Helden zwischen 0,951 und 0,999). Es ist also
**keine** allgemeine Startwaffen-Regel, sondern eine Eigenheit dieser einen Waffe.
Ungeklaert.

Ausserdem, kleiner: **Sword of Night and Flame** liegt bei allen acht Helden 1,7–4,4 %
ueber dem Modell (Spiel/Modell 1,0172–1,0443). Einzige Waffe mit drei Schadensarten und
zwei Kurven-IDs.

---

## 6. Hypothesen (a) bis (f) — jede mit Beleg oder Widerlegung

### (a) Level-SpEffects der Helden tragen `*AttackPowerRate` — **widerlegt**

`HeroStatusParam` hat einen **vollstaendigen** Paramdef (`def_is_prefix = False`,
row_size 28 vollstaendig beschrieben) und genau 15 Felder: `disableParam_NT`,
`totalLevel`, die acht `stat*`, sowie `unknown_3c`, `unknown_3d`, `unknown_4`,
`unknown_5`, `unknown_6`. **Kein Feld mit `Rate`, `Power`, `Attack` im Namen.** Die beiden
Gleitkommafelder `unknown_4` und `unknown_5` sind ueber **alle 100 Zeilen** der Tabelle
1,0 (gezaehlt, nicht gestichprobt); `unknown_3c/3d/6` folgen dem Level (0/1/11/14 bei
totalLevel 1/2/12/15). Die Zeilen sind ausserdem **eindeutig**: jeder Block hat exakt vier
Zeilen, eine je Level — es gibt keine Variante, die das Programm haette verwechseln
koennen. Es gibt an dieser Stelle nichts, was das Programm nicht anwendet.

### (b) Das Spiel benutzt eine andere ReinforceParamWeapon-Zeile — **widerlegt**

Alle 45 in der Fan-Tabelle vorkommenden `reinforce_type`-Basiszeilen haben
`physicsAtkRate = 1,0` und `correctStrengthRate = correctAgilityRate = 1,0`. Die Wahl
`reinforce_type + 0` ist also bei eigener Raritaet neutral und richtig. Entscheidender:
ueber die **gesamte** Tabelle (255 Zeilen) sind die vorkommenden `physicsAtkRate`-Werte
{1,0 … 1,98} — **keine einzige Zeile liegt unter 1,0**. Kein Zeilenwechsel, welcher auch
immer, kann einen Faktor 0,6 erzeugen.

### (c) Die CalcCorrectGraph-IDs je Schadensart stimmen nicht — **widerlegt**

Benutzte Kurven: Physics → 0 (280 Waffen) und 16 (28 Katalysatoren); Magic → 4 (34) und
0 (3); Fire → 4 (17); Thunder → 4 (4); Dark → 4 (27), 0 (4), 16 (1).
Rueckgerechnet aus den Fan-Zahlen (k = 0,6, Waffen mit genau einer treibenden Attribut-
Kurve):

| Kurve/Attribut | STR 9 | STR 17 | STR 22 | STR 34 | STR 44 | STR 60 |
|---|---|---|---|---|---|---|
| aus dem Spiel zurueckgerechnet | 26,5 | 48,8 | 63,5 | 100,9 | 131,2 | 180,3 |
| Programm, **Kurve 4** | 27,3 | 51,5 | 66,7 | 103,0 | 133,3 | 181,8 |
| Programm, Kurve 0 (falsche Wahl) | 36,0 | 68,0 | 88,0 | 124,8 | 153,6 | 189,1 |

Die zurueckgerechneten Werte folgen Kurve 4 (Abweichung 0,8–5 %) und liegen weit von
Kurve 0 (26–36 %). Ueber alle 648 Ablesungen auf Waffen mit einer Kurve ≠ 0 betraegt der
mediane relative Fehler **0,40 %** — dasselbe Niveau wie bei reinen Kurve-0-Waffen. Die
Kurvenzuordnung des Programms ist korrekt.

### (d) Rundung/Abschneiden je Schadensart vor der Summe — **teilweise belegt, aber nicht die Ursache**

Belegt ist eine Rundung, und zwar **am Ende, nicht je Schadensart**: die Anzeige
**schneidet ab** (Abschnitt 4.1 — die Rundungshypothese liefert eine leere Schnittmenge,
die Abschneidehypothese eine konsistente). Eine zusaetzliche Rundung *je Schadensart vor*
der Summe ist mit den Daten nicht noetig: das Modell ohne sie trifft 87,1 % exakt, und die
Reste haben die vier benannten Ursachen. Der Hinweis des App Designers (Trainingspuppe:
realer Schaden = angezeigte Angriffskraft) heisst zusaetzlich, dass das Abschneiden
**keine reine Anzeigekonvention** ist, sondern auf der wirksamen Zahl sitzt — das Programm
wuerde also nicht nur eine Anzeige, sondern die Rechengroesse selbst korrigieren.

### (e) `status_block` oder andere heldenspezifische Felder erklaeren Guardian — **widerlegt, Frage hat sich erledigt**

Der Guardian-Versatz war kein Spieleffekt, sondern das Level der Quelle (5.1). `HeroParam`
enthaelt ueber alle zehn Nightfarer hinweg **kein** Feld mit Angriffsbezug — die Felder,
die sich zwischen den Helden unterscheiden, sind ausschliesslich IDs (Portraits, Texte,
Icons, `heroStatusParamId`, `characterAbilityCooldown`, `characterUnlockFlag`).
`CharaInitParam` 90000–90009 traegt im Paramdef **kein** SpEffect-Feld. Guardians k
(0,59846 auf Level 11) ist von den uebrigen sieben nicht unterscheidbar.

### (f) Raritaets-Versatz statt echter Faktor (Nachtrag aus R-004) — **widerlegt**

1. **Leiter im Programm**, Wylder's Greatsword, Wylder Lv12, `upgrade` 1…4:
   191,299 / 246,775 / 302,252 / 342,424 → Leiter **1 : 1,290 : 1,580 : 1,790**.
   Fextralife: 1 : 1,254 : 1,534 : 1,737. Abweichung 2,9 / 3,0 / 3,1 %.
   Die Leiter ist im Programm **nicht** waffenunabhaengig: Dagger, Zweihander und Longbow
   ergeben 1 : 1,23 : 1,50 : 1,70, Battle Hammer (Raritaet 1) 1 : 1,00 : 1,21 : 1,37.
2. **Entscheidend ist aber die Stufe 1**, und dort gibt es keinen Versatz: bei eigener
   Raritaet ist `applied_upgrade = 0` und die Reinforce-Zeile neutral (Hypothese b). Ein
   Versatz um eine Stufe wuerde 23–29 % ausmachen, nicht 40 %; und er wuerde die
   Konstanz ueber alle vier Raritaeten (Abschnitt 3) zerstoeren, die tatsaechlich gilt.
3. **Faktor je Level** (die Anker aus R-004, Fextralife als Sekundaerquelle):

| Waffe / Held | Level | Attribute STR/DEX/INT/FAI/ARC | Programm | Fextralife | Faktor |
|---|---|---|---|---|---|
| Wylder's Greatsword / Wylder | 1 | 5/4/2/2/10 | 94,272 | 58 | 0,6152 |
| | 2 | 18/15/4/4/10 | 132,224 | — | — |
| | 12 | 44/35/12/12/10 | 191,299 | 118 | 0,6168 |
| | 15 | 50/40/15/15/10 | 203,418 | 125 | 0,6145 |
| Executor's Blade / Executor | 1 | 5/8/2/2/28 | 78,095 | 46 | 0,5890 |
| | 2 | 9/20/3/3/28 | 101,110 | — | — |
| | 12 | 22/60/7/5/28 | 154,689 | 92 | 0,5947 |
| | 15 | 25/63/8/6/28 | 158,172 | 94 | 0,5943 |

**Der Faktor haengt nicht vom Level ab** — beide Anker liefern auf Level 1, 12 und 15
denselben Wert (Streuung ≤ 1 %, und Level 1 mit Anzeige 46 bzw. 58 traegt allein durch das
Abschneiden bis zu 2 % Unschaerfe). Level 1 reisst **nicht** aus, obwohl die Attribute
dort auffaellig niedrig sind.
**Aber:** die beiden Sekundaerquellen widersprechen sich. Fuer Executor's Blade Lv12 sagen
Fan-Tabelle und Fextralife beide 92 (Faktor 0,5947). Fuer Wylder's Greatsword Lv12 sagt
die Fan-Tabelle **114** (Faktor 0,5959, exakt `floor(0,6·191,299) = 114`), Fextralife
**118** (Faktor 0,6168). Die Fan-Tabelle ist hier die Quelle, die zu 0,6 passt; die
Fextralife-Zahl passt zu keiner Stufe des Programms. Als offene Frage in Abschnitt 11.

**Der Elden-Ring-Rechner `eldenring.tclark.io`** wurde nur mit einem HEAD-Abruf beruehrt
(HTTP 200, 1677 Byte — eine JavaScript-Huelle ohne Formeltext in der Auslieferung). Er
wurde **nicht** als Quelle benutzt und keine Elden-Ring-Zahl in diesen Bericht
uebernommen; die Formelstruktur ist ohnehin aus den Nightreign-Params selbst belegt
(Hypothese c). Als ungenutzt gekennzeichnet, nicht als geprueft.

---

## 7. Skalierungsbuchstaben (RPS) — zweite, unabhaengige Quelle

387 von 387 RPS-Zeilen liessen sich einem Programmeintrag zuordnen. Jede
Buchstabe/Attribut-Zelle wurde gegen den rohen `correct`-Wert des Programms gestellt.

| Buchstabe | n | min | max | Median | Elden-Ring-Band (Hypothese) | passt |
|---|---|---|---|---|---|---|
| S | 71 | 73,0 | 80,0 | 76,0 | ≥ 175 | **0 von 71** |
| A | 113 | 60,0 | 70,0 | 64,0 | 140–174 | **0 von 113** |
| B | 173 | 45,0 | 58,0 | 54,0 | 90–139 | **0 von 173** |
| C | 191 | 30,0 | 44,0 | 38,0 | 60–89 | **0 von 191** |
| D | 151 | 16,0 | 29,0 | 28,0 | 25–59 | 98 von 151 |
| E | 72 | 7,0 | 13,0 | 12,0 | 1–24 | 72 von 72 |

**Die Elden-Ring-Schwellen gelten in Nightreign nicht.** Aber die beobachteten Baender
sind **ueberschneidungsfrei**, also lassen sich Schwellen empirisch angeben:

| Buchstabe | empirisches Band | Grenze zur naechsten Stufe |
|---|---|---|
| S | ≥ 73 (beobachtet 73–80) | Luecke 71–72 unbeobachtet |
| A | 60–70 | Luecke 59 unbeobachtet |
| B | 45–58 | **Grenze exakt bei 45** (C endet bei 44) |
| C | 30–44 | **Grenze exakt bei 30** (D endet bei 29) |
| D | 16–29 | Luecke 14–15 unbeobachtet |
| E | 7–13 (kein Wert < 7 beobachtet) | |

Zwei der fuenf Grenzen (45 und 30) sind **scharf** belegt, drei liegen in einer Luecke von
ein bis zwei Zaehlern und sind damit nur auf ±1 bestimmt. **Widersprueche zwischen RPS und
den Programmwerten: keine** — keine einzige Zelle faellt aus dem Band ihres Buchstabens.
Das ist der wertvollste Teil dieses Abschnitts: eine von der Fan-Messung voellig
unabhaengige Quelle bestaetigt die `scaling`-Werte, die das Programm aus den Params liest.

Das Programm zeigt derzeit **Zahlen, keine Buchstaben** (`arsenaltab.scaling_text`), also
folgt daraus kein Fehler — wohl aber eine Warnung fuer den Fall, dass jemand spaeter
Buchstaben anzeigen will.

---

## 8. Staebe und Siegel: die Fan-Spalte misst etwas anderes

Die 28 Katalysator-Zeilen tragen nur bei **Duchess, Revenant, Recluse** Werte; die
anderen fuenf Spalten sind leer. Das Verhaeltnis Spiel/Programm liegt bei 2,6–6,5 —
weit weg von 0,6. Das ist kein Ausreisser, sondern eine andere Groesse:

    Fan-Zahl = C × (1 + Kurve16(INT bzw. FAI)/100)

mit einer waffeneigenen Konstanten C. Rueckgerechnet ueber die drei Zauberer:

| Katalysator | Duchess | Revenant | Recluse | C (Median) |
|---|---|---|---|---|
| Recluse's Staff (INT) | 76,4 | 75,9 | 76,1 | **76,1** |
| Astrologer's Staff (INT) | 91,2 | 91,5 | 91,6 | **91,4** |
| Glintstone Staff (INT) | 89,9 | 89,4 | 89,8 | **89,7** |
| Erdtree Seal (FAI) | 121,7 | 121,3 | 121,3 | **121,4** |
| Frenzied Flame Seal (FAI) | 126,1 | 126,1 | 126,1 | **126,1** |

Das ist die **Zauber-/Anrufungsskalierung**, nicht die Angriffskraft — die Kurve ist die
des Katalysators (`correctType_Physics` = 16, linear 0…150), und der treibende Wert ist
INT bei Staeben, FAI bei Siegeln (Revenant und Recluse haben beide FAI 45 und stehen bei
den Siegeln deshalb auf identischen Zahlen: 151/151, 178/178, 204/204 — ein guter
Selbsttest der Quelle).

**Die RPS-Zahl (78…145) ist dasselbe C, um den Faktor 1/0,973 groesser** — sie korreliert
mit der Fan-Spalte praktisch perfekt (Recluse-Spalte = 1,638 × RPS-Zahl fuer jeden der 28
Katalysatoren).

**C steht in keinem Feld, das das Programm liest.** Gepruefte Gegenprobe: Recluse's Staff
(C = 76,1) und Astrologer's Staff (C = 91,4) sind in EquipParamWeapon **in allen
Zahlenfeldern identisch** (attackBasePhysics 25, attackBaseMagic 0, correctMagic 100,
weight 1,0) und unterscheiden sich nur in IDs (`behaviorVariationId`, `swordArtsParamId`,
`attackElementCorrectId`, `equippedSpell_R1/R2`, Icons, `reinforceTypeId`). Eine Suche
ueber **alle** numerischen Felder der 28 Katalysatoren nach einem Wert innerhalb von 4 %
von C ergab **0 Treffer**. Die beiden staerksten Korrelationen zur Fan-Zahl sind `rarity`
(r = 0,965) und `throwAtkRate` (r = 0,940) — beides Stellvertreter, keine Traeger.

Fuer GOAL A7 heisst das: die Zauberskalierung eines Katalysators ist aus den heute
gelesenen Params **nicht** herleitbar. Das Programm sollte das sagen, statt die
physische AR eines Stabes (~40) als dessen Kennzahl anzubieten.

---

## 9. Abnahme: die Sonde des Directors

Der Auftrag nennt zwoelf Waffen, beziffert im Text sind vier. Alle vier reproduziert:

| Waffe | Held | Programm (dieser Lauf) | Sonde | Fan-Tabelle | Sonde | Verhaeltnis |
|---|---|---|---|---|---|---|
| Dagger | Wylder | 123,641 | 124 | 74 | 74 | 0,5985 |
| Dagger | Raider | 99,357 | 99 | 59 | 59 | 0,5938 |
| Zweihander | Wylder | 245,264 | 245 | 147 | 147 | 0,5994 |
| Club | Raider | 180,933 | 181 | 108 | 108 | 0,5969 |

**Keine Abweichung.** Die restlichen acht Sondenwerte sind im Auftrag nicht beziffert und
konnten deshalb nicht einzeln gegengerechnet werden; sie sind in der Vollmessung
enthalten.

---

## 10. Befunde

### [P1 | Major | Hoch] Die angezeigte Angriffskraft ist um den Faktor 1/0,6 zu hoch

**Adressat:** developer (Umsetzung), director (Entscheid, ob und wo korrigiert wird)
**Betroffen:** `nrplanner/weapons.py:75` `rate()` — und damit jede Anzeige, die darauf
steht (`arsenaltab`, Waffenkacheln, Detailtafel, `damage.candidate()`/`rank_candidates()`
und der geplante Berater), sowie `README.md` „Known limits"
**Umgebung:** Level 12, acht Nightfarer, eigene Raritaet, ohne Relikte; 2256 Vergleiche

**Reproduktion:**
1. `datasource.load_data()`, Wylder-Attribute aus `hero["levels"]["12"]`.
2. `weapons.rate(dagger, attrs, data, upgrade=1)` → `sum(base)+sum(scaled) = 123,641`.
3. Spiel/Fan-Messung fuer dieselbe Kombination: **74**.
4. `floor(0,6 × 123,641) = 74`.

**Erwartet:** Die Zahl, die das Programm „Attack rating" nennt, ist die Zahl, die im Spiel
in der Waffentafel steht (und laut App Designer auf der Trainingspuppe auch wirklich
trifft).
**Tatsaechlich:** Sie ist konstant um 1/0,6 = 1,667 zu hoch.

**Analyse:** Die Formel selbst ist richtig — Grundschaden, Reinforce-Zeile, Kurven-IDs,
AEC-Regeln und die Attribute sind alle einzeln gegengeprueft (Abschnitt 6a–f). Das Spiel
legt einen konstanten Faktor 0,6 darueber, der in **keinem** der vom Programm gelesenen
Params steht. Der Faktor trifft Grundschaden und Skalierung gleich; die Anzeige schneidet
danach ab. Ob 0,6 als globale Konstante in der Engine sitzt oder in einem noch nicht
gelesenen Param, ist **nicht** ermittelt — das ist der offene Rest.

**Auswirkung:** Jede Zahl, die der Nutzer mit dem Spiel vergleicht, ist um zwei Drittel zu
hoch. Fuer die **Reihenfolge** von Waffen ist es folgenlos (ein positiver konstanter
Faktor ist ordnungserhaltend), fuer den Berater-Grenzbeitrag
`compute(Basis+Kandidat) − compute(Basis)` ebenso: er skaliert mit, die Rangfolge bleibt.
Falsch werden alle **absoluten** Aussagen — und der Vergleich mit dem Spiel ist genau der
Weg, auf dem ein Nutzer dem Programm vertraut oder nicht.

**Vorschlag:** Richtung, keine Umsetzung: den Faktor **einmal, benannt und mit
Geltungsbereich** in `weapons.rate` einziehen (etwa `DISPLAY_CALIBRATION = 0.6` mit
Herleitung im Kommentar), **nicht** an den Anzeigestellen — sonst entstehen wieder mehrere
Darstellungen einer Zahl (AD-019/QA-018). Das Abschneiden gehoert **an die Anzeige**, nicht
in die Rechengroesse (QA-074-Disziplin). Der Satz in README „Known limits" wird damit
falsch und muss mitgezogen. **Entscheidung gehoert dem director/App Designer**, nicht mir:
0,6 ist gemessen, aber nicht aus den Spieldaten *hergeleitet* — das beruehrt GOAL A7.

---

### [P2 | Major | Mittel] Der Raider trifft mit Greataxe und Great Hammer 18 % haerter, als das Programm rechnet

**Adressat:** developer (Kenntnisnahme), director (Frage an den App Designer)
**Betroffen:** `nrplanner/weapons.py` `rate()` — keine heldengebundene Klassenregel
vorhanden; Auswirkung auf `damage.rank_candidates()` und den Berater
**Umgebung:** Raider, Level 12, `wep_type` 19 (Greataxe) und 23 (Great Hammer), 25 Waffen

**Reproduktion:**
1. Raider Lv12, Great Mace: `weapons.rate` → 218,989; `floor(0,6 × 218,989) = 131`.
2. Fan-Messung: **155**. Quotient 1,184.
3. Dasselbe fuer alle 25 Waffen der Klassen 19 und 23: Multiplikator 1,1786–1,1839.
4. Gegenprobe Wylder auf denselben Waffen: 0,9964–1,0034. Raider auf Klasse 41: 0,998–1,003.

**Erwartet:** Derselbe Faktor wie bei jeder anderen Held/Klasse-Paarung.
**Tatsaechlich:** Konstant ×1,182 — und nur dort.

**Analyse:** Hypothese (nicht belegt): eine heldengebundene Waffenklassen-Regel, die in
den vom Programm gelesenen Params nicht vorkommt. Zweihaendigkeit, Zeilenversatz der
Quelle und der Passivtext des Raiders sind einzeln ausgeschlossen (5.3). Ich habe keine
Erklaerung und behaupte auch keine.

**Auswirkung:** Fuer den Raider unterschaetzt das Programm zwei ganze Waffenklassen um
18 %. Das ist **ordnungsrelevant**: ein Berater, der dem Raider Waffen empfiehlt, stellt
Greataxen und Great Hammer zu weit hinten ein.

**Vorschlag:** Nicht ins Programm einbauen, solange die Ursache unbekannt ist — eine
eingebaute Zahl ohne Quelle in den Spieldaten verstiesse gegen A7. Stattdessen: der App
Designer prueft im Spiel, ob der Raider mit einem Great Hammer sichtbar mehr Angriffskraft
zeigt als ein anderer Nightfarer mit denselben Attributen (Frage F2 in Abschnitt 11).

---

### [P3 | Minor | Niedrig] Revenant's Cursed Claws: 13 % zu hoch fuer jeden ausser dem Revenant

**Adressat:** developer (Kenntnisnahme), director
**Betroffen:** Waffe id 21750000, `wep_type` 35
**Umgebung:** Level 12, alle acht Nightfarer

**Reproduktion:** siehe Tabelle 5.4 — Besitzer 0,9994, alle sieben anderen 0,865–0,887.

**Erwartet:** derselbe Faktor wie fuer die uebrigen sieben Startwaffen (dort 0,951–0,999).
**Tatsaechlich:** ~0,87 fuer Fremdtraeger.

**Analyse:** Zwei Lesarten, ich entscheide keine: (i) eine Spielregel, die nur diese Waffe
betrifft; (ii) die Fan-Quelle hat die sieben Fremdtraeger-Zellen **geschaetzt statt
gemessen**, weil die Waffe fuer andere Nightfarer moeglicherweise nicht erreichbar ist —
dafuer spricht, dass die sieben Werte untereinander sehr konsistent sind (0,865–0,887),
also aus einer Formel stammen koennten.

**Auswirkung:** Eine Waffe von 310. Fuer den Berater unerheblich, solange sie nicht
empfohlen wird; als Beleg dafuer, dass die Quelle stellenweise gerechnet statt gemessen
sein koennte, aber wichtig.

**Vorschlag:** Mit der Duchess-Spalte (unten) zusammen als Quellenqualitaet behandeln,
nicht als Programmfehler.

---

### [P3 | Major | Hoch — gegen die Datenquelle, nicht gegen das Programm] Zwei der acht Fan-Spalten stehen nicht auf Level 12

**Adressat:** director (die Quelle gehoert dem Vorhaben, nicht dem Code)
**Betroffen:** `nightreign_weapon_ap_lv12.csv`, Spalten `Guardian` und `Duchess`
**Umgebung:** —

**Reproduktion:**
1. Fuer jede Spalte je Level 8–15 den Faktor frei fitten und den Median der Abweichung
   bestimmen (`which_level.py`).
2. Guardian: bestes Level **11** (Median 0,306 gegen 0,412 bei Level 12); waffenweise
   265 von 271 auf Level 11.
3. Duchess: **kein** Level passt (bestes Level 8, Median 0,635, nur 44 % innerhalb 0,5);
   waffenweise 198 auf Level 11, 69 auf Level 12, blockweise nach Zeilennummer.
4. Kontrolle Wylder/Ironeye/Raider/Revenant/Recluse/Executor: Level 12, 83–89 % innerhalb
   0,5 AP.

**Erwartet:** „Tables shows weapon Attack Power at lv12" gilt fuer alle acht Spalten.
**Tatsaechlich:** Guardian durchgehend Level 11; Duchess in Bloecken gemischt.

**Analyse:** Belegt, nicht vermutet: Level 11 und 12 unterscheiden sich fuer den Guardian
in STR (34/36) und DEX (24/26), und die Fan-Zahlen folgen ueber 265 Waffen dem kleineren
Satz. Der scheinbare „Guardian-Sonderfaktor" der Director-Sonde (0,577–0,583) loest sich
damit vollstaendig auf.

**Auswirkung:** Wer die Tabelle als Referenz nimmt, ohne das zu wissen, baut einen
Held-abhaengigen Faktor ein, den es nicht gibt. Fuer diesen Bericht: die Duchess-Spalte
ist als Beleg **nicht verwendbar**, die Guardian-Spalte nur mit Level 11.

**Vorschlag:** Die Quelle mit dieser Einschraenkung versehen, wo immer sie weiterverwendet
wird. Wenn der App Designer die Guardian- und Duchess-Werte im Spiel nachmisst, sind es
zwei Stichproben, nicht 564.

---

### [P3 | Minor | Mittel] Keine Kennzahl fuer Staebe und Siegel — das Programm zeigt eine Zahl, die im Spiel nirgends steht

**Adressat:** developer, ui-ux-designer (was an der Stelle stehen soll), director (A7)
**Betroffen:** Katalysatoren (`wep_type` 57/61) in `arsenaltab`/`weapons.rank`
**Umgebung:** 28 Katalysatoren

**Reproduktion:**
1. `weapons.rate(recluses_staff, …)` → 42,05 (physische AR).
2. Das Spiel zeigt fuer denselben Stab bei Recluse Lv12 **128** (Zauberskalierung).
3. `128 = 76,1 × (1 + Kurve16(45)/100)`; 76,1 steht in **keinem** gelesenen Feld
   (Abschnitt 8).

**Erwartet:** Entweder die Zahl, die das Spiel zeigt, oder die Aussage, dass sie nicht
verfuegbar ist (A7).
**Tatsaechlich:** Eine dritte Zahl, die im Spiel an keiner Stelle vorkommt, ohne Hinweis.

**Analyse:** Die physische AR eines Stabes ist nicht falsch gerechnet — sie ist nur nicht
die Kennzahl, nach der ein Spieler einen Stab auswaehlt. Die richtige Kennzahl haengt an
einer Konstanten, die nicht in EquipParamWeapon steht.

**Auswirkung:** Ein Vergleich „welcher Stab ist besser" liefert im Programm eine andere
Reihenfolge als im Spiel (nach der physischen AR sortiert steht Rotten Crystal Staff mit
67,8 vor dem Carian Regal Scepter mit 37,1 — im Spiel ist es umgekehrt: 182 gegen 237).
**Das ist eine echte Fehlreihung, keine Kosmetik.**

**Vorschlag:** Kurzfristig: Katalysatoren in Ranglisten kennzeichnen oder herausnehmen und
sagen, warum (A7). Laengerfristig: die Herkunft von C suchen — Kandidat ist ein Param
ausserhalb von EquipParamWeapon (die beiden Staebe unterscheiden sich in
`behaviorVariationId` und `equippedSpell_R1/R2`), das waere ein Auftrag fuer den
`researcher`, nicht fuer QA.

---

### [P3 | Minor | Niedrig] Testbarkeit: der Faktor hat im Code keinen Ort, an dem er gemessen werden koennte

**Adressat:** developer
**Betroffen:** `nrplanner/weapons.py` `rate()`

**Beobachtung, kein Fehlverhalten:** `rate()` liefert eine Zahl, die nirgends gegen eine
Aussenreferenz gehalten wird; der Docstring sagt „nothing here is estimated" und das
stimmt fuer die Formel, aber die Gesamtzahl hat bis heute keine Gegenprobe (README „Known
limits"). Es gibt keinen Einhaengepunkt fuer eine Kalibrierung und keinen
Charakterisierungstest gegen eine Spielzahl. Jetzt gibt es erstmals Material: 310 Waffen ×
8 Nightfarer mit bekannter Erwartung.

**Vorschlag (Richtung, kein Patch):** Ein Charakterisierungstest, der eine kleine feste
Auswahl (etwa die neun skalierungsfreien Waffen + je zwei je Held) gegen die gemessenen
Anzeigezahlen haelt. **Toetende Mutation dazu benennbar:** `DISPLAY_CALIBRATION` von 0,6
auf 1,0 setzen — der Test muss rot werden; und ebenso, wenn `floor` durch `round` ersetzt
wird (bei Soldier's Crossbow: 88 gegen 89). Beides sind Aenderungen an der gepruefen
Mechanik selbst, nicht an einer Schnittstelle (L-007).

---

## 11. Offene Fragen (an den App Designer, ueber den director)

**F1 — Wylder's Greatsword auf Level 12: 114 oder 118?** Die Fan-Tabelle sagt 114
(= `floor(0,6 × 191,299)`, passt exakt), Fextralife sagt 118 (Faktor 0,6168, passt zu
keiner Raritaetsstufe des Programms). Beide sind Sekundaerquellen. Fuer Executor's Blade
sind sich beide einig (92). Eine einzige Ablesung im Spiel entscheidet das.

**F2 — Trifft der Raider mit Greataxe/Great Hammer wirklich haerter?** Wenn der App
Designer im Spiel mit dem Raider eine Greataxe und danach eine Kolossalwaffe anlegt und
beide Anzeigen mit denen eines anderen Nightfarers vergleicht, ist die Frage in zwei
Minuten beantwortet. Bis dahin baue ich nichts ein und behaupte nichts.

**F3 — Ist `Revenant's Cursed Claws` fuer andere Nightfarer ueberhaupt tragbar?** Wenn
nein, sind die sieben Fremdtraeger-Zellen der Quelle geschaetzt und der Befund erledigt
sich.

**F4 — Soll der Faktor 0,6 ins Programm?** Er ist gemessen (2256 Faelle, exakte
Schnittmenge), aber nicht aus den Spieldaten *hergeleitet*. GOAL A7 sagt: wo die
Spieldateien eine Bewertung nicht hergeben, sagt das Programm das, statt zu raten. Eine
gemessene Konstante ist kein Raten, aber auch keine Quittung aus den Params. Das ist eine
Entscheidung ueber den Anspruch des Programms, nicht ueber Code — sie gehoert dem App
Designer und dem director.

---

## 12. Nicht getestet (bewusst)

- **Verstaerkte Waffen** (`applied_upgrade > 0`, Raritaetsstufen 2–4): die Fan-Quelle
  fuehrt nur die eigene Raritaet. Der Faktor ist dort **nicht** gemessen, und die
  Raritaetsleiter des Programms weicht von der einzigen verfuegbaren Sekundaerquelle um
  ~3 % ab (6f). Das ist die groesste ungemessene Flaeche und ein eigener Auftrag wert.
- **Infusionsvarianten** (id +500…+1100, ~1480 Eintraege): kommen in keiner der beiden
  Quellen vor.
- **Scholar und Undertaker**: in der Fan-Messung nicht enthalten.
- **Level ausser 1, 12, 15**: nur diese drei sind belegt; 2 ist ein exakter Anker ohne
  Referenzwert, alle uebrigen sind im Programm interpoliert.
- **Effekte, Relikte, Multiplikatoren aus `damage.py`**: der Auftrag misst `weapons.rate`
  ohne Effekte; `AR_RATE_FOR`, `STARTING_AR_RATE_FOR` und der Kritwert bleiben ungeprueft.
- **Die Testsuite des Projekts wurde nicht ausgefuehrt.** Dieser Auftrag ist reine
  Messung, aendert nichts und beruehrt keinen Waechter; ein Lauf haette nichts belegt, was
  die Messung nicht selbst belegt. Der Stand der Suite ist der von T-037 (parallele
  Session, HEAD 690db5f) — ich habe mich darauf **nicht** gestuetzt und nichts daraus
  uebernommen.
- **`eldenring.tclark.io`**: nur ein HEAD-Abruf (HTTP 200, 1677 Byte JavaScript-Huelle),
  keine Formel und keine Zahl entnommen.

---

## 13. QA-Log — neue Zeilen fuer `qa/findings.md`

`qa/findings.md` wurde gelesen (1432 Zeilen, hoechste vergebene Nummer **QA-094**). Ich
vergebe **keine IDs** — das tut der director (CLAUDE.md). Die folgenden Zeilen sind zum
Anhaengen an die bestehende Tabelle vorgesehen, mit vorlaeufigen Marken; der director
ersetzt sie durch QA-095 ff.

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| (T-038/1) | Angezeigte Angriffskraft um 1/0,6 zu hoch — Faktor 0,6 exakt, Anzeige schneidet ab | P1 | Major | developer, director | echte Spieldaten + Fan-Messung, 2256 Vergleiche, 87,1 % exakt | offen | 2026-09-03 |
| (T-038/2) | Raider ×1,1819 auf wepType 19/23, Ursache unbekannt | P2 | Major | developer, director | echte Spieldaten, 25 Waffen, Kontrollen negativ | offen (Frage F2 an App Designer) | 2026-09-03 |
| (T-038/3) | Revenant's Cursed Claws ×0,87 fuer Fremdtraeger, exakt fuer den Besitzer | P3 | Minor | developer, director | echte Spieldaten, 8 Helden, Gegenprobe ueber alle 8 Startwaffen | offen (Frage F3) | 2026-09-03 |
| (T-038/4) | Fan-Quelle: Guardian-Spalte auf Level 11, Duchess-Spalte gemischt | P3 | Major | director | 271 Waffen je Spalte, Kontrollspalten eindeutig auf L12 | offen — Quellenmangel, kein Codefehler | 2026-09-03 |
| (T-038/5) | Katalysatoren: Programm zeigt physische AR statt Zauberskalierung → Fehlreihung | P3 | Minor | developer, ui-ux-designer | 28 Katalysatoren, Formel rekonstruiert, Traegerfeld nicht auffindbar | offen | 2026-09-03 |
| (T-038/6) | `weapons.rate` ohne Einhaengepunkt und ohne Charakterisierung gegen eine Spielzahl | P3 | Minor | developer | statisch + jetzt vorhandenes Referenzmaterial | offen | 2026-09-03 |
| (T-038/7) | Skalierungsbuchstaben: Elden-Ring-Schwellen gelten in Nightreign nicht (Info, kein aktueller Fehler) | P4 | Trivial | developer | 387 RPS-Zeilen, 0 Widersprueche zu den correct-Werten | offen — nur relevant, wenn Buchstaben angezeigt werden | 2026-09-03 |

---

## 14. Anhang: Messstrecke

Alles ausserhalb des Repos: Klon `<scratchpad>\nr-t038` (Commit 64174eb, unveraendert),
Skripte `<scratchpad>\t038\`, Python
`C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\.venv\Scripts\python.exe`.

| Skript | Zweck | tragende Ausgabe |
|---|---|---|
| `match_weapons.py` | Zuordnung der 310 Fan-Zeilen | 310/310, 0 Klassenausreisser |
| `measure.py` | Rohverhaeltnisse je Held/Klasse/Raritaet/Schadensart | Abschnitt 3 |
| `dissect.py` | Traegt die Streuung die Waffe oder der Held? | Abschnitt 5 |
| `fit_curve.py` | 6-Parameter-Fit je Held (k + Kurvenwert je Attribut) | fuehrte auf 5.1/5.2 |
| `which_level.py` | Welches Level erklaert jede Fan-Spalte? | Abschnitt 5.1/5.2 |
| `raw_params.py` | HeroStatusParam, HeroParam, ReinforceParamWeapon roh | Hypothesen (a), (b) |
| `hero_effects.py` | Heldengebundene Angriffsfelder | Hypothese (e) |
| `hero_text.py` | Passivtexte der zehn Nightfarer aus den FMGs | 5.3 |
| `raider_block.py` | Der ×1,1819-Block, drei Erklaerungen getrennt | 5.3 |
| `residual_map.py` | Held × Klasse Restfehlerkarte, Duchess-Mischung | Abschnitt 3, 5.2 |
| `rarity_and_levels.py` | Raritaetsleiter, Faktor je Level | Hypothese (f) |
| `best_factor.py` | **Intervallschnitt fuer k, Modellwertung** | Abschnitt 4 |
| `curves.py` | Kurven-IDs rueckgerechnet | Hypothese (c) |
| `probe_and_letters.py` | Director-Sonde, RPS-Buchstabenbaender | Abschnitt 7, 9 |
| `catalysts.py` | Staebe/Siegel | Abschnitt 8 |
| `final.py` | Alle Berichtszahlen aus **einem** Lauf | Abschnitt 4.3 |

### 14.1 `match_weapons.py` (Zuordnung)

```python
"""T-038 / step 1: assign every row of the fan measurement to a program weapon.

Reads the fan CSV, normalises names on both sides and assigns in six stages of
decreasing certainty. Every stage is global and claims exclusively: a weapon
already taken by a more certain stage cannot be taken again, which is what
keeps "Gargoyle's Black Blade" and "Gargoyle's Black Blades" apart.

Nothing is guessed. A row that reaches no unique free candidate stays
unmatched and is listed with its near misses.

Independent check on the assignment (not a match rule): the sheet is ordered
by weapon class, so every matched row's `wep_type` must agree with the class
block it sits in. Disagreements are printed and have to be judged by hand.
"""
from __future__ import annotations

import csv
import difflib
import json
import pathlib
import re
import sys
import unicodedata

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
CSV_PATH = SCRATCH / "nightreign_weapon_ap_lv12.csv"
OUT = SCRATCH / "t038" / "assignment.json"

HEROES = ["Wylder", "Guardian", "Ironeye", "Duchess", "Raider",
          "Revenant", "Recluse", "Executor"]

ABBREV = {"gs": "greatsword", "ss": "straight sword", "cs": "curved sword"}
STOPWORDS = {"the", "of"}


def fold(name: str) -> str:
    """Lowercase, de-accented, apostrophe-free, single-spaced."""
    name = name.split(";")[0]
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.replace("\u2019", "'").replace("'", "").replace(".", "")
    name = re.sub(r"[^a-zA-Z0-9 ]+", " ", name)
    return re.sub(r"\s+", " ", name).strip().lower()


def expand(name: str) -> str:
    return " ".join(ABBREV.get(tok, tok) for tok in name.split())


def squash(name: str) -> str:
    """Spacing differences only: 'Short bow' == 'Shortbow'."""
    return name.replace(" ", "")


def stem(name: str) -> str:
    """Crude possessive/plural fold -- late stages only."""
    return " ".join(tok[:-1] if len(tok) > 3 and tok.endswith("s") else tok
                    for tok in name.split())


def nostop(name: str) -> str:
    return " ".join(t for t in name.split() if t not in STOPWORDS)


def keys(name: str) -> dict[str, str]:
    f = fold(name)
    e = expand(f)
    return {
        "exact": f,
        "abbrev": e,
        "squash": squash(e),
        "stem": squash(stem(e)),
        "nostop": squash(stem(nostop(e))),
    }


def load_rows():
    rows = []
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as fh:
        for rec in csv.DictReader(fh):
            raw = rec["Weapon"]
            rows.append({
                "raw": raw,
                "suffix": raw.split(";", 1)[1].strip() if ";" in raw else "",
                "order": float(rec["Default Order"]),
                # Staves and seals carry a figure for the three casters only;
                # an empty cell is "not measured", never zero.
                "game": {h: (float(rec[h]) if rec[h].strip() else None)
                         for h in HEROES},
            })
    return rows


def main() -> int:
    sys.path.insert(0, str(SCRATCH / "nr-t038"))
    from nrplanner import datasource

    data = datasource.load_data()
    weapons = data["weapons"]
    # The fan sheet lists un-infused armaments only; the infused variants sit
    # at id + 500..1100 of the same family. The pool is the family heads.
    heads = [w for w in weapons if w["id"] % 10000 == 0]
    wkeys = {w["id"]: keys(w["name"]) for w in heads}

    tables = {}
    for stage in ("exact", "abbrev", "squash", "stem", "nostop"):
        table: dict[str, list] = {}
        for w in heads:
            table.setdefault(wkeys[w["id"]][stage], []).append(w)
        tables[stage] = table

    rows = load_rows()
    for row in rows:
        row["keys"] = keys(row["raw"])
        row["weapon_id"] = None

    taken: set[int] = set()
    for stage in ("exact", "abbrev", "squash", "stem", "nostop"):
        for row in rows:
            if row["weapon_id"] is not None:
                continue
            free = [w for w in tables[stage].get(row["keys"][stage], [])
                    if w["id"] not in taken]
            if len(free) == 1:
                row["weapon_id"] = free[0]["id"]
                row["stage"] = stage
                taken.add(free[0]["id"])

    # Last stage: nearest name, only when it is unique and clearly nearest.
    pool = {wkeys[w["id"]]["squash"]: w for w in heads if w["id"] not in taken}
    for row in rows:
        if row["weapon_id"] is not None:
            continue
        close = difflib.get_close_matches(row["keys"]["squash"],
                                          sorted(pool), n=2, cutoff=0.80)
        scores = [(difflib.SequenceMatcher(None, row["keys"]["squash"], c)
                   .ratio(), c) for c in close]
        row["near"] = [(round(s, 3), c) for s, c in scores]
        if scores and (len(scores) == 1 or scores[0][0] - scores[1][0] > 0.06):
            w = pool.pop(scores[0][1])
            row["weapon_id"] = w["id"]
            row["stage"] = "fuzzy"
            taken.add(w["id"])

    by_id = {w["id"]: w for w in weapons}
    matched, unmatched = [], []
    for row in rows:
        if row["weapon_id"] is None:
            unmatched.append(row)
            continue
        w = by_id[row["weapon_id"]]
        row["weapon_name"] = w["name"]
        row["rarity"] = w["rarity"]
        row["wep_type"] = w["wep_type"]
        matched.append(row)

    # ---- independent check: class blocks --------------------------------
    ordered = sorted(matched, key=lambda r: r["order"])
    odd = []
    for i, row in enumerate(ordered):
        window = ordered[max(0, i - 3):i] + ordered[i + 1:i + 4]
        neigh = [r["wep_type"] for r in window]
        if neigh and row["wep_type"] not in neigh:
            odd.append((int(row["order"]), row["raw"], row["weapon_name"],
                        row["wep_type"], sorted(set(neigh))))

    print(f"rows={len(rows)} matched={len(matched)} unmatched={len(unmatched)}")
    print("by stage:", {st: sum(1 for r in matched if r["stage"] == st)
                        for st in sorted({r["stage"] for r in matched})})
    print("fuzzy stage assignments (each needs an eye):")
    for row in matched:
        if row["stage"] in ("nostop", "fuzzy"):
            print(f"   {row['raw']!r} -> {row['weapon_name']!r} "
                  f"[{row['stage']}] near={row.get('near')}")
    print(f"class-block outliers: {len(odd)}")
    for o in odd:
        print("   ", o)
    print("unmatched:")
    for row in unmatched:
        print(f"   {row['raw']!r} near={row.get('near')}")

    for row in rows:
        row.pop("keys", None)
    OUT.write_text(json.dumps({"matched": matched, "unmatched": unmatched},
                              indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 14.2 `best_factor.py` (Herleitung des Faktors und Modellwertung)

```python
"""T-038 / step 11: the best factor, and what it leaves over.

Part 1 uses the armaments that scale off nothing -- five crossbows and one
ballista, whose displayed figure cannot contain a curve -- so game = D(k*base)
with a single unknown. Each reading confines k to an interval; the
intersection is the factor, and its width is the measurement's precision.

Part 2 scores whole models over all 2256 readings: how many are hit exactly,
and how far off the rest are. The corrections that earlier steps measured are
switched on one at a time, so each one's contribution is visible instead of
being buried in a total.
"""
from __future__ import annotations

import json
import math
import pathlib
import statistics
import sys

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
ASSIGN = SCRATCH / "t038" / "assignment.json"
HEROES = ["Wylder", "Guardian", "Ironeye", "Duchess", "Raider",
          "Revenant", "Recluse", "Executor"]
CATALYSTS = {57, 61}


def main() -> int:
    sys.path.insert(0, str(SCRATCH / "nr-t038"))
    from nrplanner import datasource, weapons as wmod

    data = datasource.load_data()
    by_id = {w["id"]: w for w in data["weapons"]}
    heroes = {h["name"]: h for h in data["heroes"]}
    rows = sorted(json.loads(ASSIGN.read_text(encoding="utf-8"))["matched"],
                  key=lambda r: r["order"])

    def prog(w, hero, lvl="12"):
        r = wmod.rate(w, heroes[hero]["levels"][lvl], data,
                      upgrade=w["rarity"] + 1)
        return sum(r.base.values()) + sum(r.scaled.values())

    print("=== part 1: armaments with no attribute scaling ===")
    flat = []
    for r in rows:
        w = by_id[r["weapon_id"]]
        if any(w["scaling"].values()):
            continue
        vals = {h: r["game"][h] for h in HEROES if r["game"][h] is not None}
        if not vals:
            continue
        base = sum(w["base"].values())
        flat.append((w["name"], base, vals))
        print(f"   {w['name'][:28]:28} param base={base:5.0f} "
              f"program={prog(w, 'Wylder'):8.3f} readings={sorted(set(vals.values()))}")
    for rule, lo0, hi0 in (("round", -math.inf, math.inf),
                           ("floor", -math.inf, math.inf)):
        lo, hi = lo0, hi0
        for name, base, vals in flat:
            for hero, g in vals.items():
                a, b = ((g - 0.5) / base, (g + 0.5) / base) if rule == "round" \
                    else (g / base, (g + 1.0) / base)
                lo, hi = max(lo, a), min(hi, b)
        state = "consistent" if lo < hi else "EMPTY"
        print(f"   rule={rule:5}: k in [{lo:.6f}, {hi:.6f})  {state}  "
              f"width={hi - lo:.6f}")
    print()

    # ---- part 2: whole models -------------------------------------------
    obs = []
    for r in rows:
        if r["wep_type"] in CATALYSTS:
            continue
        w = by_id[r["weapon_id"]]
        for hero in HEROES:
            g = r["game"][hero]
            if g is not None:
                obs.append((w, hero, g))

    def score(k, rule, guardian_level=False, raider_bonus=False):
        exact = 0
        devs = []
        for w, hero, g in obs:
            lvl = "11" if (guardian_level and hero == "Guardian") else "12"
            p = k * prog(w, hero, lvl)
            if raider_bonus and hero == "Raider" and w["wep_type"] in (19, 23):
                p *= 1.1819
            shown = math.floor(p) if rule == "floor" else round(p)
            exact += (shown == g)
            devs.append(abs(p - g))
        return exact / len(obs), statistics.median(devs), max(devs)

    print("=== part 2: model scores over all 2256 readings ===")
    print(f"{'k':>8} {'rule':>6} {'GuardL11':>9} {'RaiderX':>8} "
          f"{'exact':>7} {'med|dev|':>9} {'max|dev|':>9}")
    for k in (0.6, 0.5972, 0.595):
        for rule in ("floor", "round"):
            for gl in (False, True):
                for rb in (False, True):
                    ex, med, mx = score(k, rule, gl, rb)
                    print(f"{k:8.4f} {rule:>6} {str(gl):>9} {str(rb):>8} "
                          f"{ex:6.1%} {med:9.3f} {mx:9.2f}")
    print()
    k, rule = 0.6, "floor"
    print(f"=== residual detail for k={k}, rule={rule}, both corrections on ===")
    worst = []
    per_hero = {h: [] for h in HEROES}
    for w, hero, g in obs:
        lvl = "11" if hero == "Guardian" else "12"
        p = k * prog(w, hero, lvl)
        if hero == "Raider" and w["wep_type"] in (19, 23):
            p *= 1.1819
        d = p - g
        worst.append((abs(d), w["name"], hero, g, round(p, 2)))
        per_hero[hero].append(abs(d))
    for hero in HEROES:
        v = per_hero[hero]
        print(f"   {hero:9} median={statistics.median(v):.3f} "
              f"p95={sorted(v)[int(0.95 * len(v))]:.3f} max={max(v):.2f} "
              f"within 1.0: {sum(1 for x in v if x < 1.0) / len(v):5.1%}")
    worst.sort(reverse=True)
    print("   ten largest deviations:")
    for d, name, hero, g, p in worst[:10]:
        print(f"      {d:6.2f}  {hero:9} {name[:32]:32} game={g:5.0f} model={p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 14.3 `which_level.py` (welches Level erklaert eine Fan-Spalte)

```python
"""T-038 / step 6: which level does each column of the fan sheet fit?

For each Nightfarer column, which of the levels 1..15 -- the program's own
attribute table, interpolated where the game does not state a level --
reproduces the column best, with the factor k fitted freely for each
candidate? For every level the factor is the one that minimises the sum of
squared deviations, k = sum(prog*game)/sum(prog^2), and the score is the
median absolute deviation on the displayed number.
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
ASSIGN = SCRATCH / "t038" / "assignment.json"
HEROES = ["Wylder", "Guardian", "Ironeye", "Duchess", "Raider",
          "Revenant", "Recluse", "Executor"]
CATALYSTS = {57, 61}
EXCLUDE_TYPES_FOR = {"Raider": {19, 23}}


def main() -> int:
    sys.path.insert(0, str(SCRATCH / "nr-t038"))
    from nrplanner import datasource, weapons as wmod

    data = datasource.load_data()
    by_id = {w["id"]: w for w in data["weapons"]}
    heroes = {h["name"]: h for h in data["heroes"]}
    assign = json.loads(ASSIGN.read_text(encoding="utf-8"))

    for hero in HEROES:
        rows = [r for r in assign["matched"]
                if r["game"][hero] is not None
                and r["wep_type"] not in CATALYSTS
                and r["wep_type"] not in EXCLUDE_TYPES_FOR.get(hero, set())]
        best = []
        for lvl in range(8, 16):
            attrs = heroes[hero]["levels"][str(lvl)]
            num = den = 0.0
            progs, games = [], []
            for r in rows:
                w = by_id[r["weapon_id"]]
                rat = wmod.rate(w, attrs, data, upgrade=w["rarity"] + 1)
                prog = sum(rat.base.values()) + sum(rat.scaled.values())
                game = r["game"][hero]
                num += prog * game
                den += prog * prog
                progs.append(prog)
                games.append(game)
            k = num / den
            dev = [abs(k * p - g) for p, g in zip(progs, games)]
            best.append((statistics.median(dev), lvl, k, max(dev),
                         sum(1 for d in dev if d < 0.5) / len(dev)))
        best.sort()
        print(f"--- {hero}: n={len(rows)} armaments")
        for med, lvl, k, mx, share in sorted(best, key=lambda b: b[1]):
            mark = "  <== best" if (med, lvl) == (best[0][0], best[0][1]) else ""
            print(f"    level {lvl:2}: k={k:.5f} median|dev|={med:6.3f} "
                  f"max={mx:6.2f} within-half={share:5.1%}{mark}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Die uebrigen elf Skripte liegen unveraendert im Scratchpad-Ordner `t038` und sind in der
Tabelle oben mit ihrer tragenden Ausgabe benannt; sie folgen demselben Muster (Zuordnung
laden, `weapons.rate` aufrufen, gegen die Fan-Zahl stellen) und enthalten keine Konstante,
die nicht in diesem Bericht steht.
