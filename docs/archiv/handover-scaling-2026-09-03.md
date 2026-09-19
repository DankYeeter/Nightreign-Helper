# Handover - Angriffskraft und Skalierung (Session "Nightreign Helper Scaling Questions", 03.09.2026)

*Geschrieben vom Director dieser Session. Sie lief read-only parallel zur
Audit-3-Session auf demselben Arbeitsbaum, hat nichts committet und alles an
Audit 3 uebergeben. Der Projektstand insgesamt steht in `docs/state.md`
(fuehrt Audit 3); dieses Dokument ist der Stand **dieses Themas**: was
gemessen ist, was daraus folgt, was der Nutzer noch prueft, wo alles liegt.*

## 1. Auftrag des Nutzers

"Answer the scaling questions and bake the formula into the program" -
Groessenordnung genuegt ("pretty confident", +-10 %), keine Exaktheit;
in-game ist nur die Trainingspuppe (0 Verteidigung, Schaden = angezeigte
Angriffskraft) und Level 15 mit Relikten verlaesslich pruefbar. Gelieferte
Quellen: Fan-Tabelle "Nightreign Weapon Scaling.xlsx" (Angriffskraft Lv12
ohne Relikte, 310 Waffen x 8 Nightfarer), Rock-Paper-Shotgun-Liste (387
Waffen, Skalierungsbuchstaben), Elden-Ring-Rechner eldenring.tclark.io.

## 2. Ergebnis - die Formeln, wie sie ins Programm gehoeren

| Groesse | Formel | Beleg | Sicherheit |
|---|---|---|---|
| Angezeigte Angriffskraft einer Waffe | `floor(0,6 x weapons.rate)` - Elden-Ring-Formel (Grundschaden x Verstaerkung + Grundschaden x Sum(correct x Kurve x Einfluss)) aus den echten Params, mal **0,6**, **abgeschnitten** | T-038, QA-095: k in [0,5993, 0,6009) aus 9 skalierungsfreien Waffen x 8 Helden; 97,5 % von 1974 brauchbaren Ablesungen ganzzahlig exakt; Rundung ausgeschlossen (leere Schnittmenge); level- (Lv 1/12/15) und raritaetsunabhaengig; in keinem gelesenen Param (Hypothesen a-f widerlegt) | **exakt** |
| Multiplikatoren (Relikte, Klassenbuffs) | **multiplikativ**, auch zwischen verschiedenen Effekten; Werte stehen als Faktoren in den Params | R-005: 152/183/219 fuer zwei +20 %-Buffs (1,44 = 1,2^2), +6 %/+9 % -> x1,1554; Nutzermessungen 08/2026 | hoch |
| Startwaffen-Statusstrafe | x0,85 nur fuer eigene Startwaffe in Slot 1 | R-005 (drei Quellen), im Spiel verifiziert 22.08.2026; Fan-Notiz "~20 %" ist falsch | hoch |
| Staebe und Siegel ("Spell power") | `floor(90 x ReinforceParamWeapon.unknown_1 x (1 + Kurve16(INT bzw. FAI)/100))` - **nicht** mal 0,6 | T-043, QA-099: 84/84 Fan-Zellen, 28/28 RPS-Zahlen exakt; `unknown_1` = Offset 128, letztes f32 der Zeile; 53 Waffen mit Wert != 1,0, alle Katalysatoren; Herkunft der 90 offen, fuer Reihenfolge folgenlos; nur Basisraritaet belegt | **exakt** |
| Skalierungsbuchstaben (falls je angezeigt) | S >= 73 · A 60-70 · B 45-58 · C 30-44 · D 16-29 · E 7-13 (Grenzen 45 und 30 scharf, uebrige +-1); Elden-Ring-Schwellen gelten **nicht** | T-038 Abschn. 7, 387/387 Zellen im Band | hoch |
| Raritaetsleiter | Programm 1 : 1,29 : 1,58 : 1,79 (Wylder's Greatsword), Fextralife 1 : 1,254 : 1,534 : 1,737 | R-004, T-038 (f); Basisraritaet exakt, Stufen darueber **nicht gemessen** | offen, 3 % |

**Was der Faktor 0,6 nicht ist:** keine Anzeigekonvention (Trainingspuppe:
Schaden = Anzeige, Nutzer), kein Levellauf auf 1,0 bei Lv15 (widerlegt), kein
Raritaetsversatz (widerlegt), keine Reinforce-Zeile (< 1,0 existiert nicht),
keine Kurven-ID (alle richtig), keine Rundung je Schadensart. Einziger
plausibler Fundort: `PlayerCommonParam` +664, undefinierter Slot mit exakt
0,6 - **kein Beleg**, nur ein Faden (T-042).

**Rangfolgen waren nie falsch** - ein konstanter Faktor ist ordnungserhaltend;
falsch waren alle absoluten Zahlen (x1,67) und die Reihung der Katalysatoren.

## 3. Reste, die der Faktor nicht erklaert - Beobachtungen, keine Regeln

| Befund | Zahl | Stand | Entscheidet |
|---|---|---|---|
| **QA-096** Raider auf Greataxe/Great Hammer (wep_type 19/23), 25 Waffen | **x1,18** exakt; sonst nichts, sonst niemand | keine Param-Quelle (T-042: 252 Tabellen, 257 912 Zeilen, 6,66 Mio. Zellen inkl. undefinierter Bytes); Community kennt es nicht (R-006), Patch 1.02.2 hat genau dieses Klassenpaar beim Raider angefasst (Stagger); 1,18 existiert im Spiel nur als Relikt-Effektstufe -> Fan-Ablesung mit Relikt moeglich | **Nutzer, Lv15** |
| **QA-097** Revenant's Cursed Claws bei Fremdtraegern | **x0,88** exakt (Besitzer 1,00) | Absicht belegt (Item-Text: "reduced to a blunt instrument", R-006), Zahl in keiner Quelle, keine Param-Quelle | **Nutzer, Lv15** |
| **QA-098** Fan-Quelle | Guardian-Spalte = Lv11, Duchess-Spalte gemischt/unbrauchbar | stehende Einschraenkung jeder Weiterverwendung | - |
| Sword of Night and Flame | +1,7-4,4 % bei allen Helden | einzige Waffe mit drei Schadensarten/zwei Kurven; ungeklaert, klein | - |
| Obergrenze des Gesamtmultiplikators | unbekannt | keine Quelle (R-005); trifft stark gestapelte Builds | nur im Spiel |

**Regel, mit Audit 3 vereinbart:** QA-096/097 werden **nicht** eingebaut,
solange keine Quelle in den Params vorliegt (GOAL A7). Bestaetigt der Nutzer
QA-096 im Spiel, ist der Einbau als datierte Kalibrierung eine Produktfrage,
weil er die Waffenrangfolge des Raiders verschiebt.

## 4. Nutzerentscheidungen (03.09.2026, woertlich)

- "bake it in. no warning in the GUI necessary." / "bake it in if it is
  close enough and you are sure enough" -> **T-045** (Faktor 0,6).
- "replace physical attack with spell power" -> **T-046** (Katalysatoren:
  Kennzahl ersetzt die physische AR ueberall, Beschriftung "Spell power").
- "every nightfarer can wield the claws" -> QA-097 ist Spielverhalten, keine
  Schaetzung der Quelle.
- Level 15 mit Relikten ist der Pruefstand; Groessenordnung genuegt.

## 5. Was der Nutzer noch im Spiel prueft (je eine Ablesung)

1. **Raider, ohne Relikte, einhaendig, Greataxe (id 15000000), Lv15:**
   Programm ohne Regel **141**, mit Regel **166** (T-042 Abschn. 7).
   Mit Relikten geht auch das Verhaeltnis Greataxe : Colossal gegen das
   Programmverhaeltnis - Faktor und flache Multiplikatoren kuerzen sich.
   ~1,18 bestaetigt, ~1,00 widerlegt, ~1,09 = klassengebundenes Relikt aktiv.
2. **Recluse mit Revenant's Cursed Claws, Lv15:** **87** = Malus 0,88 real,
   **76** = kein Malus, **75** = Modellfehler. Falle: "Starting armament
   inflicts ..."-Relikte senken nur den Revenant um 15 % - weglassen.
3. **Eine Waffe in zwei Raritaeten, gleicher Held, gleicher Zustand:**
   Verhaeltnis gegen die Programmleiter (3 % Abstand zur einzigen
   Sekundaerquelle; ueber der Basisraritaet ungemessen).
4. **Wylder, eigene Startwaffe in Slot 1, ohne und mit "Starting armament
   deals fire damage"** (beliebiges Level; auf Lv12 waeren es 114 ohne, dann
   91 / 116 / 117 je nach Lesart) - entscheidet, wie QA-113 eingebaut wird.
5. Optional: Wylder's Greatsword Common Lv12 - Fan-Tabelle 114 (passt zum
   Modell), Fextralife 118 (passt zu nichts). Geringer Wert.

## 6. Auftraege und ihr Stand

| Auftrag | Rolle | Stand |
|---|---|---|
| T-038 Programm-AR gegen Fan-Messung und RPS | qa-engineer | erledigt, `docs/berichte/T-038-qa-engineer.md` |
| T-039 R-004 Gesamtfaktor (Recherche) | researcher | erledigt, `docs/research/R-004.md` |
| T-040 R-005 Multiplikatoren | researcher | erledigt, `docs/research/R-005.md` |
| T-042 Params-Suche Raider/Claws | qa-engineer | erledigt, negativ mit Nenner, `T-042-qa-engineer.md` |
| T-043 Katalysator-Konstante | qa-engineer | erledigt, Formel gefunden, `T-043-qa-engineer.md` |
| T-044 R-006 heldengebundene Boni (Recherche) | researcher | erledigt, `docs/research/R-006.md` |
| T-049 "Starting armament inflicts"-Relikte: Konversion vs. Programm | qa-engineer | siehe Abschnitt 7 |
| **T-045** Faktor 0,6 einziehen, Abschneiden an der Anzeige, Charakterisierung gegen Spielwerte, README | developer | **bei Audit 3 in Arbeit** |
| **T-046** `unknown_1` extrahieren, Spell power an einer Stelle, Reihung, Namenskollision, Texte | developer | **bei Audit 3 eingereiht, nach T-045** |
| QA-Retest ueber T-045/T-046 (sonnet) | qa-engineer | bei Audit 3, danach S7 des Beraters |

Register: `qa/findings.md`, Abschnitt "T-038 (2026-09-03 ...)": QA-095 bis
QA-099 mit QA-099a/b/c (Namenskollision `Recluse's Staff` 33750000/33770000,
Messstreckenregel fuer mehrdeutige Namen, Platzhalterfeld `unknown_1` laut
scheitern lassen). Audit 3 vergibt ab QA-100.

Rohdaten im Scratchpad dieser Session (nicht im Repo, vergaenglich):
`nightreign_weapon_ap_lv12.csv` (Fan-Tabelle), `rps_nightreign_weapons.tsv`,
Messskripte `t038\`, `t042\`, `t043\`, Klone `nr-t038`, `nr-t043`. Die
tragenden Skripte stehen im Wortlaut in den Berichten; T-045/T-046 legen die
Referenzwerte als Testdaten ins Repo (`tests/data/`).

## 7. T-049 - die "Starting armament"-Relikte (Bericht `T-049-qa-engineer.md`, Klon 0dc54a6)

- **Die drei "inflicts frost/poison/blood loss"-Relikte rechnet das Programm
  exakt** wie die Params: nur x0,85 auf alle fuenf Schadensarten (12 Zeilen
  im ganzen Spiel mit diesem Muster) plus Statusaufbau am Gegner, keine
  Umwandlung. QA-101 (Rangfolge dreht mit `candidate` statt `equipped`) ist
  auf dem Stand nach der 0,6-Kalibrierung ziffernweise reproduziert.
- **Die Fan-Zahlen gehoeren woandershin:** "~40-50 % AP zu Element" und
  "~20 % weniger AP" beschreiben die **Infusions-Geschwisterzeilen** der
  Waffen (Fire/Lightning/Sacred/Magic: 50 % Elementanteil, phys x0,5; Cold
  x0,4; Poison/Bloody: phys x0,8, Skalierung auf Arc 45), die das Programm
  bereits als eigene Waffenzeilen fuehrt. Das Relikt kostet 15 %, die
  Infusion 20 % - der Widerspruch aus R-005 ist damit aufgeloest (Lesart,
  im Spiel nicht nachgemessen).
- **Neuer Rechenfehler (Vorschlag QA-113, P2, ID vergibt Audit 3):** die vier
  Geschwister "Starting armament **deals** magic/fire/lightning/holy damage"
  (7120000/100/200/300) tragen `physicsAttackPower -30/-40/-50/-60` und
  `<element>AttackPower +33/+44/+55/+66`; flache `*AttackPower`-Felder haben
  in `model.compute` kein Fach und bewegen die Angriffskraft um **exakt 0**,
  waehrend die Karte die Zahlen nennt. 3 von 309 Relikten im Save, gleiche
  Poolhaeufigkeit wie die drei modellierten, Rangfolge des Beraters an der
  Spitze gedreht. Die Einbauhoehe haengt daran, wo die Zahl in der Rechnung
  angreift (drei Lesarten: -23,24 / +1,80 / +3,00 fuer Wylder Lv12) - **nur
  eine Ablesung im Spiel entscheidet**: Wylder, eigene Startwaffe in Slot 1,
  ohne und mit "Starting armament deals fire damage", Lv12-Vorhersagen
  **91 / 116 / 117** bei Grundwert 114. Kein Test nennt das Feld.
- Vorschlag QA-114 (P4): der Kommentar in `damage.py` Z. 61-63 nennt die
  Familie mit drei statt sieben Mitgliedern - das hat R-005 in die Irre
  gefuehrt.

## 8. Prozess - was fuer die naechste parallele Session gilt

- **Nummernkreise vorher reservieren, in `docs/state.md`**, und nur die
  reservierten benutzen; bei Bedarf per Session-Nachricht nachfragen. So
  liefen zwei Directors auf einem Baum ohne Kollision.
- **Read-only heisst: genau eine Berichtsdatei je Agent im Arbeitsbaum**,
  Skripte und Klone im Scratchpad, kein Git im Arbeitsbaum. Der Klon wird
  per `fetch` + `checkout --detach` im Klon nachgezogen, nie der Baum.
- **Absenz-Behauptungen brauchen einen Nenner.** "In keinem Param" wurde
  erst uebernommen, als Tabellen, Zeilen und Zellen gezaehlt waren.
- **Median ueber abgeschnittene Werte ist kein Faktor.** Intervallschnitt
  statt Punktschaetzer - so wurden 1,1819 -> 1,18 und 0,87 -> 0,88 korrigiert
  und 0,6 als exakt erkannt.
- **Namensgleiche Datensaetze als Nichttreffer melden**, nicht fuzzy
  zuordnen (QA-099b) - eine falsche Zeile hat die Katalysator-Suche in
  T-038 scheitern lassen.
- Die Fan-Quelle bleibt mit QA-098 belastet; wer sie weiterverwendet, nimmt
  Guardian als Lv11 und laesst Duchess weg.
