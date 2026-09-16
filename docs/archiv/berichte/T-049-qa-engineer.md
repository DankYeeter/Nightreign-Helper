# T-049 — Die "Starting armament ..."-Relikte: Element-/Statuskonversion in den Params gegen die Behandlung im Programm (qa-engineer)

```
STATUS: erledigt
AUFTRAG: T-049 — Die "Starting armament inflicts ..."-Relikte: Element-/Statuskonversion
         in den Params gegen die Behandlung im Programm (Nachtrag zu QA-101)
GELESEN: docs/tasks/T-049.md, docs/tasks/T-038.md (Fan-Notizen im Wortlaut),
         docs/research/R-005.md, docs/berichte/T-041-qa-engineer.md (QA-101),
         GOAL.md, docs/state.md, qa/findings.md,
         nrplanner/damage.py, nrplanner/weapons.py, nrplanner/model.py,
         nrplanner/weaponslots.py, nrplanner/effecttext.py, nrplanner/inventory.py,
         nrdata/extract.py, nrdata/param.py,
         tests/test_advisor_goals.py, tests/test_damage_facade.py,
         tests/weapon_damage_cases.py, scripts/differential/mutate.py
GEÄNDERT: docs/berichte/T-049-qa-engineer.md (diese Datei, einzige Datei im
         Arbeitsbaum). Kein Git im Arbeitsbaum. Im eigenen Klon
         <scratchpad>/nr-t043: `git fetch origin` und `git checkout --detach 0dc54a6`
         — nur der Klon, nicht der Arbeitsbaum.
ANNAHMEN: (1) Die Frage von T-049 lautet "Programm gegen Param-Lesart", nicht
         "equipped gegen candidate" (das war QA-101). (2) Als Param-Lesart gilt,
         was `SpEffectParam` in den vom Programm selbst gelesenen Feldern sagt;
         wo die Params **nicht** sagen, an welcher Stelle der Rechnung eine Zahl
         angreift, rechne ich alle plausiblen Stellen durch statt eine zu waehlen.
         (3) Die drei Relikte des Auftrags heissen im Datensatz 7120400/500/600;
         ich habe ihre **vier Geschwister** 7120000/100/200/300 mitgemessen, weil
         die Fan-Notiz erkennbar von diesen spricht — das war nicht beauftragt,
         aber ohne sie ist die Auftragsfrage nicht beantwortbar.
NÄCHSTER: director (Audit 3) — Entscheid ueber eine neue Befund-ID; danach developer
BLOCKIERT DURCH: nichts
```

---

## Messumgebung und Belegkette

| Groesse | Wert |
|---|---|
| Klon | `<scratchpad>\nr-t043`, `git checkout --detach` auf **`0dc54a6`** ("test(weapons): die Angriffskraft gegen die Zahlen des Spiels charakterisieren", Kopf von `docs/audit-and-advisor-design` zum Messzeitpunkt) |
| Arbeitsbaum | **nicht angefasst**, kein Git; parallel laeuft dort der `developer` (T-045) |
| Python | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\.venv\Scripts\python.exe` |
| Spieldaten | `D:\SteamLibrary\...\ELDEN RING NIGHTREIGN\Game\regulation.bin`, 1 974 720 B, `sha256 876a3ca279a4561d0c69f81fe5e510c75c59ab9a8a201694f8cf4a42c91e0268`, `data_version 10350000` |
| Save | `76561198179244962`, 309 Relikte, nur lesend |
| QSettings | auf `DankYeeterQA/NightreignHelperQA_T049` umgebogen, Nutzer-Store unberuehrt |
| Skripte | `<scratchpad>\t049\` (11 Stueck, Anhang) |

**Die 0,6-Kalibrierung aus T-045 ist eingerechnet** (`weapons.GAME_ATTACK_POWER_RATE
= 0,6`, seit `99ed022`). Sie kuerzt sich in jeder Rangfolge heraus; wo ich Zahlen
gegen T-041 stelle, nenne ich beide Formen.

**Reproduktion von QA-101 auf diesem Commit, exakt.** T-041s Grundzahl 203,4176
ist **Wylder Level 15, Tier 1** (nicht Level 12 — das war die einzige Unklarheit
beim Nachfahren; Level 12 gibt 191,2986, Level 1 gibt 94,2720). Auf Level 15 /
Tier 1 reproduzieren sich die drei QA-101-Zahlen ziffernweise:

```
ohne die 0,6-Kalibrierung:  baseline 203.4176   d(equipped) -12.3576   d(candidate) +21.3589
mit    der 0,6-Kalibrierung: baseline 122.0506   d(equipped)  -7.4146   d(candidate) +12.8153
Rangfolge equipped  ['R1','R0']   Rangfolge candidate ['R0','R1']   -> VERSCHIEDEN
```

**QA-101 steht nach T-045 unveraendert.** Die Kalibrierung hat den Befund nicht
beruehrt; die Rangfolge dreht auf allen drei gemessenen Leveln (1, 12, 15).

---

## Risiko-Briefing (vor der Messung formuliert)

Die riskanteste Stelle ist nicht die Zahl 0,85, sondern die **Zuordnung der
Fan-Behauptung zu einem Mechanismus**: die Notiz spricht von "elemental damage
added to starting weapon via relic" und R-005 hat sie stillschweigend auf die
drei *inflicts*-Relikte bezogen. Wenn es im selben ID-Block ein zweites
Relikt-Rudel gibt, das genau das tut, faellt die Frage anders aus. Zweitens:
`SpEffectParam` hat 48 vom Def nicht beschriebene Bytes je Zeile (T-042) — eine
Aussage "traegt kein Konversionsfeld" ist ohne diese Bytes nicht belastbar.
Drittens: die Effekt-Id ist eine `AttachEffectParam`-Id, die Nutzlast liegt
woanders — wer nur die gleichnamige `SpEffectParam`-Zeile liest, findet gar
nichts. Viertens: eine Rangfolge-Aussage aus zwei synthetischen Kandidaten ist
schwach; sie muss gegen den echten Bestand gehalten werden. Reihenfolge: Kette
zuerst, dann ID-Band, dann Programm, dann Rangfolge.

Alle vier Risiken sind eingetreten. Das dritte hat mich beim ersten Versuch in
die Irre gefuehrt (siehe Explorationsprotokoll), das erste ist der eigentliche
Befund dieses Laufs.

---

## 1. Die drei Effekte in `SpEffectParam` vollstaendig

### 1.1 Die Kette, mit Zaehlbelegen

Die Effekt-Id ist eine `AttachEffectParam`-Zeile. Die gleichnamige
`SpEffectParam`-Zeile ist ein **leerer Marker**: sie traegt gegenueber dem
haeufigsten Wert je Feld (Modus ueber alle 13 472 Zeilen) genau vier
Abweichungen — `spCategory 10`, `stateInfo 2101`, `effectTargetEnemy 0`,
`bCurrHPIndependeMaxHP 1` — und **keine einzige Zahl**.

Die Zahlen liegen auf den Nachbarzeilen. Vollstaendig, je Familie:

```
7120400  Marker            stateInfo 2101, sonst neutral
7120401..7120404          physicsAttackPowerRate 0.85  magicAttackPowerRate 0.85
                          fireAttackPowerRate 0.85     thunderAttackPowerRate 0.85
                          darkAttackPowerRate 0.85     spAttribute 23  stateInfo 152
                          atkOccurrenceSpEffectId -> 7120405..7120408
7120405..7120408          freezeAttackPower 35, wepParamChange 3, spCategory 10007,
                          effectTargetOpposeTarget 1  (also: am Gegner, beim Treffer)
```

Poison (7120500): identisch, `spAttribute 20`, `poizonAttackPower 35`.
Blood loss (7120600): identisch, `spAttribute 22`, `bloodAttackPower 25`.

**Was ausser `*AttackPowerRate` einen Nicht-Neutralwert traegt: nichts, was eine
Schadensart verschiebt.** Auf den vier Nutzlastzeilen jeder Familie stehen nur
die fuenf Raten, `spAttribute`, `stateInfo` und der Kettenzeiger. Kein
`physicsAttackPower`, kein `replaceSpEffectId` (−1), kein `wepParamChange` (0),
kein `magicSubCategoryChange`, kein Feld mit `wep`/`weapon`/`replace`/`infus`
im Namen ausser den genannten Neutralwerten.

**Die vier Stufen sind keine Leiter.** Byte-Vergleich der vollstaendigen
1024-Byte-Zeilen: 7120401 gegen 7120402/03/04 unterscheidet sich in **genau
einem Byte, Offset 300** — und Offset 300 ist `atkOccurrenceSpEffectId`
(21/22/23/24 als niederwertiges Byte). Die vier Zielzeilen 7120405..7120408
sind untereinander **byte-identisch (0 Byte Unterschied)**. Also: 0,85 und
35/35/25 Aufbau auf **jeder** Stufe, unabhaengig von der Relikt-Raritaet.

**Die 48 vom Def nicht beschriebenen Bytes** (row_size 1024, def_row_size 976 —
`def_is_prefix`) tragen auf allen 27 beteiligten Zeilen dieselbe Folge
`1 −1 −1 3,60134e−41 1 nan nan nan nan nan nan nan`. Kein Unterschied zwischen
Marker, Nutzlast und Statuszeile; dort steht nichts.

### 1.2 Referenzen, vorwaerts und rueckwaerts

Rueckwaertsindex ueber **alle 4-Byte-Slots aller Tabellen** der regulation.bin,
Suche nach den 63 Ids 7120000..7120608:

| Tabelle.Feld | Verweise | Bedeutung |
|---|---|---|
| `AttachEffectParam.passiveSpEffectId_1` | **7** | die sieben Marker, je einmal — der einzige Eintrittspunkt |
| `AttachEffectParam.attachTextId` / `.attachFilterParamId`, `AttachEffectFilterParam.filterTextId` | je 7 | Text und UI-Filter |
| `AttachEffectTableParam.attachEffectId` | 280 | die Wuerfelpools |
| `SpEffectParam.atkOccurrenceSpEffectId` | **12** | 7120x01..x04 → 7120x05..x08, sonst nichts |

**Kein `replaceSpEffectId`, kein `cycleOccurrenceSpEffectId`, kein
`applyIdOnGetSoul` und kein Feld irgendeiner anderen Tabelle zeigt auf diese
Zeilen.** Die einzige Verzweigung ist `atkOccurrenceSpEffectId`, und die fuehrt
zum Statusaufbau am getroffenen Gegner.

*Falle, die dabei auffiel und in kuenftigen Rueckwaertsindizes Fehltreffer
erzeugt:* `EquipParamWeapon` und `EquipParamCustomWeapon` haben eigene Zeilen
mit den Ids 7120000/7120100/... (`originEquipWep*`, `targetWeaponId`). Das sind
**Waffen**, keine SpEffects — ein tabellenblinder Id-Scan meldet dort 200+
Fehltreffer.

### 1.3 Antwort auf Punkt 1

**Je Effekt, mit Geltungsbereich:**

| Effekt | Was er laut Params tut |
|---|---|
| `7120400 Starting armament inflicts frost` | **nur x0,85** auf alle fuenf Schadensarten, plus 35 Frost-Aufbau beim Treffer am Gegner. Keine Umwandlung. |
| `7120500 Starting armament inflicts poison` | **nur x0,85** auf alle fuenf, plus 35 Gift-Aufbau. Keine Umwandlung. |
| `7120600 Starting armament inflicts blood loss` | **nur x0,85** auf alle fuenf, plus 25 Blutungs-Aufbau. Keine Umwandlung. |

Geltungsbereich: `regulation.bin` `data_version 10350000`, alle vier Stufen,
alle zehn Nightfarer (die Zeilen sind heldenunabhaengig).

**Gegenprobe mit zwei unabhaengigen Masken ueber alle 13 472 SpEffect-Zeilen:**

- Maske "Zeilen mit `*AttackPowerRate != 1,0`": 490 Zeilen, 150 Wertmuster.
  Das Muster *0,85 auf allen fuenf* kommt auf **genau 12 Zeilen** vor — und das
  sind exakt 7120401-404, 7120501-504, 7120601-604. Der Wert 0,85 in dieser
  Gestalt existiert im Spiel nur fuer diese drei Relikte.
- Maske "`stateInfo == 2101`": **genau 7 Zeilen** im ganzen Spiel — und das sind
  exakt die sieben "Starting armament ..."-Marker. Die Familie ist geschlossen,
  und sie hat **sieben** Mitglieder, nicht drei.

---

## 2. Was die Startwaffe dann ist — die Geschwisterzeilen

### 2.1 Es gibt keine

Alle zehn Startwaffen enden auf `750000`. Zeilen im jeweiligen ID-Band
(`id // 10000`), aus `EquipParamWeapon`:

| Nightfarer | Startwaffe | Id | Zeilen im Band |
|---|---|---|---|
| Wylder | Wylder's Greatsword | 3750000 | **1** |
| Guardian | Guardian's Halberd | 18750000 | **1** |
| Ironeye | Ironeye's Bow | 41750000 | **1** |
| Duchess | Duchess' Dagger | 1750000 | **1** |
| Raider | Raider's Greataxe | 23750000 | **1** |
| Revenant | Revenant's Cursed Claws | 21750000 | **1** |
| Recluse | Recluse's Staff | 33750000 | **1** |
| Executor | Executor's Blade | 9750000 | **1** |
| Scholar | Scholar's Thrusting Sword | 5750000 | **1** |
| Undertaker | Undertaker's Hammer | 11750000 | **2** |

Die einzige Zusatzzeile ist `11750100`; sie unterscheidet sich von `11750000`
in **genau einem von 268 Feldern** (`disableGemAttr` 1 → 0), traegt dieselben
`attackBase*` und dieselbe Skalierung und steht **nicht** im Datensatz des
Programms. Keine Infusionsvariante.

Zum Vergleich das Band einer gewoehnlichen Waffe (Longsword 2000000): acht
Zeilen, `Fire`/`Lightning`/`Sacred`/`Magic`/`Cold`/`Poison`/`Bloody`.

**Die Hypothese aus R-005 — "die Konversion koennte ueber Geschwisterzeilen
laufen" — ist damit widerlegt.** Fuer die Startwaffen gibt es keine.

### 2.2 Wo der Statusaufbau stattdessen herkommt

- **Nicht von der Waffenzeile.** `0 von 2317` `EquipParamWeapon`-Zeilen tragen
  einen der sieben `*AttackPower`-Statuswerte direkt. Auch die Poison-/
  Bloody-Infusionen tun das nicht: sie zeigen ueber `spEffectBehaviorId0/1` auf
  eine SpEffect-Zeile (Poison Longsword → 106010 mit `poizonAttackPower 45`).
- **Nicht ueber einen Waffeneffekt-Pool.** Die zehn Startwaffen liegen alle in
  `weaponslots.base_ids` (also formal "uninfundiert", Limit 3/3), aber
  `why_no_effects` sagt fuer alle zehn: *"This armament never rolls effects."*
  Sie bekommen keinen Pool. Einen Schluessel mit `pool` im Namen gibt es im
  Datensatz nicht.
- **Sondern ueber die Relikt-Kette.** 19 Effekte des Datensatzes tragen
  `inflicts_on_hit`: die drei Startwaffen-Relikte (35/35/25) und 16 weitere
  (`Attacks Inflict Poison/Blood Loss/Sleep/Rot/Frost` in je drei Stufen
  18/23/30, plus `Critical Hits Inflict Blood Loss` 50). Nur die drei
  Startwaffen-Relikte kaufen den Status mit einer Angriffsstrafe.

### 2.3 Was die Infusionszeilen wirklich tun — und was das fuer die Fan-Notiz heisst

Ueber **alle** ID-Baender gemessen, jede Variante gegen die uninfundierte Zeile
desselben Bandes:

| Variante | n Baender | `attackBasePhysics` / Basis, Median (haeufigster Wert) | Elementanteil am Grundschaden, Median (1./3. Quartil) |
|---|---|---|---|
| Fire | 200 | 0,504505 (**exakt 0,5** in 91 Baendern) | **50,00 %** (50,00 / 50,00) |
| Lightning | 199 | 0,504505 (0,5 in 91) | **50,00 %** (50,00 / 50,00) |
| Sacred | 202 | 0,504546 (0,5 in 90) | **50,00 %** (50,00 / 50,00) |
| Magic | 206 | 0,504587 (0,5 in 91) | **50,00 %** (50,00 / 50,00) |
| Cold | 200 | 0,405063 (0,4 in 41) | **50,00 %** (50,00 / 50,00) |
| Poison | 233 | **0,805556** (**exakt 0,8** in 41) | 0,00 % |
| Bloody | 203 | **0,804878** (**exakt 0,8** in 42) | 0,00 % |

Und die Skalierung aendert sich mit: `Longsword` Str 50 / Dex 50 →
`Sacred Longsword` Str 43 / Dex 43 / **Fai 30**, `Poison`/`Bloody Longsword`
Str 43 / Dex 43 / **Arc 45**.

**Das sind die beiden Fan-Zahlen, an ihrem richtigen Ort.** Die Notiz aus T-038
lautet woertlich:

> *"During exploration, random weapons with elemental infusion has altered
> scaling ... But elemental damage added to starting weapon via relic (converts
> ~40-50% AP to elemental) does not change scaling."*
> *"Adding status via Relic reduces ~20% AP."*

- "~40-50 % zu Element" trifft die **Infusionszeile** auf den Punkt: 50,00 %,
  und zwar als Median *und* als beide Quartile ueber 200+ Baender.
- "~20 % weniger AP" trifft die **Poison-/Bloody-Infusionszeile** auf den Punkt:
  x0,80.
- Fuer das **Relikt** sagen die Params 0,85, also 15 % — genau die Zahl, die
  R-005 aus drei Quellen belegt hat.

Meine Lesart, ausdruecklich als Lesart gekennzeichnet: der Fan-Autor hat zwei
Mechanismen zusammengezogen, die dieselbe Beschreibung im Spiel bekommen. Das
loest den in R-005 offen gebliebenen Widerspruch "15 % gegen ~20 %" auf, ohne
dass eine der beiden Quellen falsch sein muss. **Beweisen kann das nur eine
Ablesung im Spiel** (R-005 Messung C); die Params zeigen nur, dass beide Zahlen
im Datensatz vorkommen und wo.

---

## 3. Programm gegen Param-Lesart, je Schadensart

Grundzustand: **Wylder Level 12** (exakter Level), **Wylder's Greatsword in
Slot 0**, Tier 1, keine weiteren Effekte. `is_starting_armament` = True.

```
final_per_type  Physics 114.779136  Magic 0  Fire 0  Thunder 0  Dark 0
final_total     114.779136   (angezeigt: 114;  ohne die 0,6-Kalibrierung 191.298560)
```

### 3.1 Die drei Relikte des Auftrags

| Effekt | Programm, Physics | Param-Lesart, Physics | Differenz je Art | Differenz Summe |
|---|---|---|---|---|
| 7120400 frost | 97,562268 | 97,562268 | **0,000000** in allen fuenf | **0,000000** |
| 7120500 poison | 97,562268 | 97,562268 | **0,000000** in allen fuenf | **0,000000** |
| 7120600 blood loss | 97,562268 | 97,562268 | **0,000000** in allen fuenf | **0,000000** |

Grenzbeitrag je Relikt: **−17,216868** (= 114,779136 x −0,15). Die vier
Nicht-Physik-Arten sind bei dieser Waffe 0 und bleiben es unter beiden Lesarten.

**Fuer die drei beauftragten Relikte rechnet `damage.equipped` exakt das, was
die Params sagen.** Der Statusaufbau (35/35/25) ist keine Angriffskraft und
erscheint zu Recht nicht in der Zahl; er steht im Effekttext.

### 3.2 Die vier Geschwister — und dort liegt die Differenz

`7120000/100/200/300 Starting armament deals magic/fire/lightning/holy damage`.
Ihre Nutzlastzeilen tragen eine echte Leiter (Byte-Vergleich: Unterschiede bei
Offset 88 = `physicsAttackPower` und beim jeweiligen Elementfeld):

```
Stufe 0:  physicsAttackPower -30   <element>AttackPower +33
Stufe 1:                     -40                        +44
Stufe 2:                     -50                        +55
Stufe 3:                     -60                        +66
```

Das Programm fuehrt Stufe 0 in `modifiers` und die volle Leiter in
`payload_tiers`. Gemessen, Wylder Lv12, Slot 0:

| Lesart | Physics | Fire | Summe | Grenzbeitrag |
|---|---|---|---|---|
| **Programm** | 114,779136 | 0,000000 | 114,779136 | **0,000000** |
| Param P0 (flach in `base`, vor der Skalierung) | 71,736960 | 19,800000 | 91,536960 | −23,242176 |
| Param P1 (flach auf die interne AK, vor x0,6) | 96,779136 | 19,800000 | 116,579136 | **+1,800000** |
| Param P2 (flach auf die angezeigte Zahl) | 84,779136 | 33,000000 | 117,779136 | **+3,000000** |

Differenz je Schadensart Programm→P1: Physics **−18,000000**, Fire
**+19,800000**, Summe **+1,800000**. Programm→P2: Physics **−30,000000**,
Fire **+33,000000**, Summe **+3,000000**.

**Unter jeder der drei Lesarten ist die Programmzahl 0,000000 falsch.** Die
Params sagen nicht, an welcher Stelle der Rechnung ein flaches `*AttackPower`
angreift; sie sagen sehr deutlich, dass es angreift.

**Warum es im Programm nirgends ankommt** — drei unabhaengig formulierte Suchen
ueber das ganze Repo (`physicsAttackPower` ohne `Rate`;
`(fire|magic|dark|thunder)AttackPower` ohne `Rate`; `convert|deals … damage`):

- `nrdata/extract.py:1633` — ein **Kommentar**, der die Leiter beschreibt.
- `nrplanner/effecttext.py:116-120` — eine **Beschriftungstabelle**.
- Sonst **null Treffer**: kein Bucket in `model.compute`, kein Feld in
  `damage.py`, kein Test, keine Golden-Datei, keine Mutation.

Gemessen statt gelesen: `FIELD_BASELINE["physicsAttackPower"] = 0.0`,
`is_multiplier` False, und das Feld steht in keiner der sechs Listen, an denen
die Feldschleife von `model.compute` entlanglaeuft (`ATTRIBUTE_FIELDS`,
`FLAT_BONUSES`, `PERCENT_FIELDS`, `PERCENT_OF_100_FIELDS`, `EXTRA_MULTIPLIERS`,
`RATE_LABELS`). Es faellt hinten heraus. `build.rates`, `build.other`,
`build.attributes` bleiben leer — nachgemessen, alle drei.

**Was der Spieler dazu liest:** `effecttext.describe(7120100)` liefert
*"Physical attack power -30, Fire attack power 33"*. Die Karte nennt die Zahlen;
die Angriffskraft daneben bewegt sich um 0,000000.

### 3.3 Wie gross die Blindstelle ist

- Effekte des Datensatzes mit einem flachen `*AttackPower`: **21 von 2076**.
- Davon **bedingt** (`model.is_conditional`, also zu Recht draussen und unter
  "Conditional & situational" ausgewiesen): **17** — die 16 Waffeneffekte
  `Add Fire/Magic/Lightning/Holy to Weapon` (jeweils −25/+25 bis −35/+35, mit
  `triggerOnWepType` und `invocationConditionsStateChange1`) und ein
  Wylder-Skill-Effekt.
- Davon **unbedingt**: **4** — und das sind genau die vier
  `Starting armament deals ... damage`.

Die Blindstelle ist also scharf umrissen: **vier Relikt-Effekte**, sonst nichts.

**Wie haeufig sie sind:** in `AttachEffectTableParam` hat **jeder der sieben**
Marker **exakt 40** Pooleintraege. Die vier uebersehenen Relikte sind genauso
haeufig wuerfelbar wie die drei modellierten. Auf dem Save dieser Maschine:
**3 von 309** Relikten tragen einen "deals"-Effekt (`Night of the Beast`,
`Delicate Drizzly Scene`, `Grand Luminous Scene`), **10 von 309** einen
"inflicts"-Effekt (T-041s Zahl unabhaengig bestaetigt), zusammen **13**.

---

## 4. Rangfolge: gleich oder gedreht

### 4.1 Der QA-101-Kandidatensatz, um die Geschwister erweitert

Grenzbeitrag = `final_total(Grundzustand + Kandidat) − final_total(Grundzustand)`,
also genau die Groesse, nach der der Berater ordnet (GOAL F2, AD-018).
Wylder Lv12, Slot 0, Tier 1.

| Kandidat | Effekte | Programm | Param P0 | Param P1 | Param P2 |
|---|---|---|---|---|---|
| R0 (frost + Angriffsbuff) | 7120400, 6001400 | −6,972828 | −6,972828 | −6,972828 | −6,972828 |
| R1 (Strength +1) | 7000300 | +0,746496 | +0,746496 | +0,746496 | +0,746496 |
| **R2 (deals fire damage)** | 7120100 | **0,000000** | −23,242176 | **+1,800000** | **+3,000000** |
| **R3 (deals holy damage)** | 7120300 | **0,000000** | −23,242176 | **+1,800000** | **+3,000000** |
| R4 (inflicts poison) | 7120500 | −17,216868 | −17,216868 | −17,216868 | −17,216868 |
| R5 (inflicts blood loss) | 7120600 | −17,216868 | −17,216868 | −17,216868 | −17,216868 |

```
Rangfolge Programm : R1, R2, R3, R0, R4, R5
Rangfolge Param P1 : R2, R3, R1, R0, R4, R5      -> GEDREHT an der Spitze
Rangfolge Param P2 : R2, R3, R1, R0, R4, R5      -> GEDREHT an der Spitze
Rangfolge Param P0 : R1, R0, R4, R5, R2, R3      -> GEDREHT am Fuss
```

**Fuer R0/R1/R4/R5 — die drei beauftragten Relikte und die Kontrollen — ist die
Rangfolge unter jeder Lesart gleich.** Gedreht wird sie ausschliesslich durch
R2/R3, die vier Geschwister.

### 4.2 Dasselbe auf dem echten Bestand, 309 Kandidaten

Jedes besessene Relikt einzeln als Kandidat, gleicher Grundzustand:

- Die drei "deals"-Relikte: Programm **+0,000000** → P1 **+1,800000** → P2
  **+3,000000**.
- **214 von 309** Relikten haben nach dem Programm einen Grenzbeitrag von exakt
  0,000000 (die meisten Relikte beruehren Schaden nicht). Die drei "deals"-
  Relikte sitzen heute **in** diesem Block und verlassen ihn unter der
  Param-Lesart.
- Echte Ueberholvorgaenge, bei denen ein heute hoeher gerankter Kandidat
  ueberholt wuerde: **21 geordnete Paare (P1)** bzw. **75 (P2)**, mit Namen —
  P1: `Grand Luminous Scene` (+0,608256), `Grand Burning Scene` (+1,216512 und
  +1,492992), `Grand Luminous Scene` (+1,216512), `Grand Drizzly Scene`
  (+1,492992), `Grand Tranquil Scene` (+1,216512). P2 zusaetzlich
  `Blessed Flowers`, `Old Pocketwatch`, `Polished Drizzly Scene`,
  `Polished Luminous Scene`, weitere `Grand Burning/Drizzly/Luminous/Tranquil
  Scene`-Kopien (17 Relikte insgesamt).
- Diskordante Paare Programm gegen Param-Lesart, ueber alle 47 586 Paare:
  **348 (P1)** / **402 (P2)**.

### 4.3 Antwort auf Punkt 4

> **Rangfolge gleich fuer die drei beauftragten Relikte; gedreht fuer ihre vier
> Geschwister.**

Namentlich: `Starting armament inflicts frost / poison / blood loss` stehen
unter Programm und Param-Lesart an derselben Stelle (Grenzbeitrag −17,216868,
Differenz 0,000000). `Starting armament deals magic / fire / lightning / holy
damage` stehen im Programm mit **exakt 0,000000** — also ununterscheidbar von
einem Relikt, das mit Schaden nichts zu tun hat — und wandern unter der
Param-Lesart an die Spitze des Feldes (P1/P2) oder ans Ende (P0). Auf dem
Bestand des Nutzers betrifft das `Night of the Beast`, `Delicate Drizzly Scene`
und `Grand Luminous Scene`.

---

## Befunde

### [P2 | Major | Mittel] Vier "Starting armament deals ... damage"-Relikte bewegen die Angriffskraft um exakt 0, obwohl die Params eine Umwandlung tragen

**Adressat:** developer (Umsetzung), director (ID-Vergabe und Reihenfolge)
**Betroffen:** `nrplanner/model.py` Feldschleife (~Z. 946-1010, Zweigkette ohne
Fach fuer flache `*AttackPower`), `nrplanner/damage.py` Z. 53-84
(`AR_RATE_FOR` / `STARTING_AR_RATE_FOR` kennen nur Raten, keine Summanden),
`nrplanner/effecttext.py` Z. 116-120 (die Zahlen werden angezeigt)
**Umgebung:** `data_version 10350000`; Effekte 7120000 / 7120100 / 7120200 /
7120300; jeder Nightfarer, sobald seine eigene Startwaffe in Slot 1 liegt.
Auf dem Save 3 von 309 Relikten; in den Wuerfelpools 40 Eintraege je Effekt,
genauso viele wie fuer die drei modellierten Geschwister.

**Reproduktion:**
1. `data = datasource.load_data()`, Wylder, Level 12, `Wylder's Greatsword`
   in Slot 0, Tier 1.
2. `damage.equipped(slot, 0, model.compute(hero, 12, []), hero, data)[1].final_total`
   → `114.779136`.
3. Dasselbe mit `effects=[data["effects"]["7120100"]]` → `114.779136`.
4. `model.compute(...).rates`, `.other`, `.attributes` pruefen → alle drei leer.
5. `effecttext.describe(effekt)` → `"Physical attack power -30, Fire attack
   power 33"`.

**Erwartet:** Ein Relikt, dessen Effektkarte "Physical attack power -30, Fire
attack power 33" nennt, veraendert die Angriffskraft der Startwaffe — in
irgendeine Richtung.
**Tatsaechlich:** Differenz `0.000000000`, in jeder der fuenf Schadensarten.

**Analyse:** Die Feldschleife in `model.compute` ordnet jedes Modifikatorfeld
einem von sechs Faechern zu. `physicsAttackPower` und die vier elementaren
Geschwister sind in **keinem** — sie haben Neutralwert 0,0 (also kein
Multiplikator), stehen nicht in `FLAT_BONUSES`, nicht in `PERCENT_FIELDS`,
nicht in `RATE_LABELS` von `model`, und fallen hinten aus der Kette. Nur
`effecttext.FLAT_LABELS` kennt sie, und das ist eine Beschriftungstabelle.
Belegt durch drei unabhaengige Repo-weite Suchen (Trefferzahlen oben) und durch
die Messung, nicht durch Codelesung allein. Die Zuordnung ist damit sicher; die
**Hoehe** der Korrektur ist es nicht: die Params sagen nicht, ob die flache
Zahl vor der Skalierung, nach der Skalierung oder auf die angezeigte Zahl
wirkt (P0/P1/P2 oben, Spannweite −23,24 bis +3,00 fuer denselben Effekt).

**Auswirkung:** Der Berater kann diese vier Relikte weder empfehlen noch
abraten — sie sind fuer ihn Nullen. Fuer den Spieler heisst das: das Relikt, das
seine Startwaffe auf Feuer umstellt, taucht in der Schaden-Rangfolge zwischen
den 214 Relikten auf, die mit Schaden nichts zu tun haben. Auf dem Bestand
dieser Maschine ueberholen sie unter der Param-Lesart 6 bzw. 17 namentlich
genannte Relikte. Zugleich beruehrt es A7: die Karte nennt Zahlen, die in keine
Summe eingehen, und **kein Text sagt das**.

**Vorschlag (Richtung, kein Patch):** Zwei Dinge trennen. (a) Die Blindstelle
sichtbar machen — das ist billig, folgt A7 und braucht keine Spielmessung: ein
`unknowns`-Satz bzw. ein Vorbehalt auf der Effektkarte, dass diese vier Relikte
eine Umwandlung tragen, die das Programm nicht rechnet. (b) Die Zahl einbauen
— das braucht **vorher** eine Ablesung im Spiel, weil P0/P1/P2 sich um bis zu
26 Punkte unterscheiden. Die Messung ist billig und entscheidet in einem
Relikt-Wechsel (Vorschlag unten unter "Offene Fragen"). Solange sie fehlt,
waere ein eingebauter Wert eine erfundene Zahl und damit derselbe A7-Verstoss,
den QA-096/097 fuer 1,18 und 0,88 begruendet haben.

**Wenn ein Fix kommt, ist er erst gesichert, wenn (L-007):** ein Fall existiert,
den das **Entfernen des neuen Fachs in der Feldschleife** rot macht — nicht nur
das Umbenennen eines Feldes. Heute faellt bei dieser Aenderung **nichts**: kein
Test im Repo nennt ein flaches `*AttackPower` (drei unabhaengige Suchen, 0
Treffer in `tests/` und `scripts/`). Der bestehende Wächter
`test_the_damage_goal_charges_the_starting_armament_penalty` sucht seine
Effekte ueber `effects_raising_rate(..., "physicsAttackPowerRate")` und ist
gegen diese Klasse blind.

---

### [P4 | Trivial | Niedrig] Der Kommentar in `damage.py` nennt die Familie zu klein

**Adressat:** developer
**Betroffen:** `nrplanner/damage.py` Z. 61-63; wortgleich
`tests/weapon_damage_cases.py` Z. 163-166
**Umgebung:** dieselbe.

**Reproduktion:** `damage.py` Z. 61-63 lesen: *"`*AttackPowerRate` is the second
family, carried by exactly three effects -- the 'Starting armament inflicts
frost / poison / blood loss' relics"*. Dann `stateInfo == 2101` ueber
`SpEffectParam` zaehlen: **7 Zeilen**, nicht 3.

**Erwartet:** Der Satz beschreibt entweder das Feld (`*AttackPowerRate`: dann
stimmen die drei) oder die Relikt-Familie (dann sind es sieben).
**Tatsaechlich:** Beides in einem Satz, und weil er die Familie beim Namen nennt
("Starting armament ..."), liest die naechste Rolle "drei Relikte dieser Art"
statt "drei Traeger dieses Feldes". Genau das ist in R-005 passiert: die
Fan-Notiz zur Konversion wurde auf diese drei bezogen, und die vier Geschwister
kamen in keiner der beiden Untersuchungen vor.

**Analyse:** Die Aussage ueber das *Feld* ist korrekt und gemessen (12 Zeilen,
3 Effekte). Die Aussage ueber die *Familie* ist es nicht.

**Auswirkung:** Keine auf eine Zahl. Wirkung auf die naechste Untersuchung:
belegt.

**Vorschlag:** Den Satz auf das Feld beschraenken und die Familie mit ihrer
vollen Groesse danebenstellen — mit dem Zaehlbeleg `stateInfo 2101 → 7`, damit
die naechste Suche nicht wieder bei drei anfaengt.

---

### Kein Befund, ausdruecklich bestaetigt

- **Die drei Relikte des Auftrags rechnet `damage.equipped` richtig.** x0,85 auf
  alle fuenf Schadensarten, nur fuer die Paarung Slot 1 + eigene Startwaffe.
  Differenz zur Param-Lesart: 0,000000 je Art und in Summe.
- **QA-101 steht nach T-045.** Auf `0dc54a6` reproduzieren sich die drei Zahlen
  aus T-041 ziffernweise (Level 15, Tier 1, vor der Kalibrierung), und die
  Rangfolge dreht auf allen drei gemessenen Leveln.
- **R-005s Hypothese "Konversion ueber Geschwisterzeilen" ist widerlegt**, mit
  Zaehlbeleg: 9 der 10 Startwaffen haben 1 Zeile im Band, die zehnte 2, und die
  zweite ist keine Infusion.
- **Die 48 undefinierten Bytes je SpEffect-Zeile tragen hier nichts.**

---

## Zusammenfassung (an den director)

Befunde: **1x P2 (Major)**, **1x P4 (Trivial)**. Keine neue QA-Id vergeben — der
Auftrag verlangt einen Nachtrag zu QA-101, und der steht unten. **Der P2-Befund
ist ein Rechenfehler und damit der im Auftrag vorgesehene Fall "Vorschlag fuer
eine neue ID an den Audit-3-Director"** (Vorschlag: QA-113).

Die Auftragsfrage ist beantwortet und faellt zweigeteilt aus: fuer die drei
Relikte, nach denen gefragt wurde, rechnet das Programm **genau richtig** — nur
x0,85, keine Umwandlung, Rangfolge unter beiden Lesarten identisch. Die
Fan-Behauptung zur Konversion trifft sie nicht; sie trifft ihre **vier
Geschwister**, die dieselbe Namensfamilie, dieselbe Poolhaeufigkeit und eine
echte Umwandlung von −30/+33 bis −60/+66 haben, und die das Programm mit exakt
0,000000 bewertet.

**Releasefaehig?** Fuer A3/A5 nicht ohne Entscheid: der Berater bewertet vier
wuerfelbare Relikt-Effekte als wirkungslos, waehrend ihre Effektkarte Zahlen
nennt. Das ist kein Blocker (3 von 309 Relikten betroffen, Wirkung klein und in
der Summe sogar leicht positiv), aber es ist eine A7-Luecke ohne Text. Minimum
vor Abnahme von A5/A7: die Blindstelle **benennen**. Der Einbau der Zahl gehoert
hinter eine Spielmessung, sonst waere er eine erfundene Zahl.

---

## Explorationsprotokoll

| Versuch | Ergebnis |
|---|---|
| `SpEffectParam` 7120400/500/600 gegen den Modus je Feld | **haelt nicht** als Fundstelle: die Marker sind leer. Erste Lesung haette "keine Konversion, aber auch keine 0,85" gemeldet — falsch |
| Kette ueber `AttachEffectParam` → `passiveSpEffectId_1` → Nachbarzeilen | fuehrt zu den Nutzlastzeilen; deckt sich mit `extract.py` Z. 1630-1640 |
| Byte-Vergleich der vier Nutzlast- und vier Statuszeilen | haelt: 1 Byte (Kettenzeiger) bzw. 0 Byte Unterschied |
| 48 undefinierte Bytes je Zeile ausgelesen | haelt: konstant, kein Fund |
| Rueckwaertsindex ueber alle 4-Byte-Slots aller Tabellen | haelt, mit einer Falle: `EquipParamWeapon`-Waffen mit derselben Id sind Fehltreffer |
| `stateInfo == 2101` als Familienmaske | haelt und ist der schaerfste Beleg: 7 Zeilen im ganzen Spiel |
| `*AttackPowerRate == 0,85` auf allen fuenf als zweite Maske | haelt: 12 Zeilen, exakt die drei Familien |
| ID-Baender der zehn Startwaffen | haelt: keine Infusionsgeschwister |
| Infusionsbaender ueber alle Waffen statistisch | haelt: Median = Quartile = 50,00 % Element, 0,80 fuer Poison/Bloody |
| `model.compute` auf jeden der sieben Effekte, `rates`/`other`/`attributes` gelesen | haelt: die vier "deals" landen nirgends |
| drei unabhaengige Repo-Suchen nach flachem `*AttackPower` | haelt: 2 Treffer, beide nicht rechnend |
| QA-101 nachgefahren, Level 1/12/15 x Tier 1..4 | haelt: 203,4176 ist Level 15 / Tier 1; Zahlen ziffernweise gleich |
| Rangfolge auf 309 echten Relikten, drei Param-Lesarten | haelt: 348/402 diskordante Paare, 21/75 echte Ueberholvorgaenge |

---

## Offene Fragen

1. **An den Nutzer (App Designer), eine Ablesung, ein Relikt-Wechsel:** Wylder,
   eigene Startwaffe in Slot 1, angezeigte Angriffskraft ablesen; dann ein
   Relikt mit `Starting armament deals fire damage` anlegen und erneut ablesen.
   Bei Level 12 sagen die drei Lesarten **91 / 116 / 117** voraus (Grundwert
   114), bei Level 15 entsprechend. Eine Ablesung entscheidet, und ohne sie
   kann der Einbau nicht stattfinden. Sinnvoll zusammen mit R-005 Messung C
   (15 % gegen 20 %), weil beide dieselbe Ausgangsstellung brauchen.
2. **An den director:** Ist "das Programm bewertet ein wuerfelbares Relikt mit
   exakt 0, waehrend seine Karte Zahlen nennt" ein A7-Fall (Vorbehalt noetig)
   oder ein A3-Fall (Rechnung noetig)? Ich lese beides als beruehrt und
   entscheide es nicht.
3. **An den developer / architect, aus den Params nicht beantwortbar:** Welche
   der vier Stufen (−30/−40/−50/−60) ein konkretes Relikt traegt, steht in
   keiner Tabelle, die das Programm liest — `AttachEffectTableParam` hat drei
   Felder (`unknown_0`, `attachEffectId`, `chanceWeight`), row_size 12 = def
   row_size 12, also keine unbeschriebenen Bytes und kein Stufenwaehler. Das
   Programm fuehrt heute Stufe 0. Fuer die drei "inflicts"-Relikte ist das
   folgenlos (alle vier Stufen identisch); fuer die vier "deals"-Relikte ist es
   ein Faktor 2 zwischen erster und letzter Stufe.
4. **An den director, Beobachtung ohne Befund:** 214 von 309 Relikten haben fuer
   `max_damage` auf diesem Build einen Grenzbeitrag von exakt 0,000000. Der
   Berater ordnet sie heute nach Id. Ob das eine Sortierfrage oder eine
   Anzeigefrage ist, entscheide ich nicht.

---

## Nicht getestet

- **Die Testsuite habe ich nicht laufen lassen.** Begruendung, nicht Versaeumnis:
  im Arbeitsbaum laeuft parallel der `developer` (T-045), und der Test-Store
  (`DankYeeterTests/NightreignHelperTests`) ist maschinenweit — ein zweiter
  Lauf haette dessen Suite roeten koennen und die meine dazu. Der Auftrag ist
  reine Messung; die Suite gehoert zu T-045. **Was daraus folgt:** ich sage
  nichts darueber, ob die Suite auf `0dc54a6` gruen ist. Meine Aussagen ueber
  Testabdeckung stuetzen sich auf Lesung und Suche, nicht auf einen Lauf.
- **Keine Messung im laufenden Spiel.** Deshalb bleibt P0/P1/P2 offen.
- **Nur Wylder ausgemessen.** Die Anteilstabelle in 2.3 rechnet alle zehn
  Nightfarer durch, aber die Rangfolgen (Punkt 4) stehen auf Wylder Lv12.
  Fuer die drei "inflicts"-Relikte ist das folgenlos (x0,85 ist heldenfrei);
  fuer die "deals"-Relikte haengt der Anteil stark am Grundwert der Waffe
  (Raider 13,0 % bis Recluse ueber 100 % unter P1, Stufe 0) — dort ist eine
  Aussage je Held noetig, sobald die Zahl eingebaut wird.
- **`Recluse's Staff` und `Finger Seal`**: Katalysatoren zeigen keine
  Angriffskraft, sondern die Zauberskalierung (QA-099/T-043). Was ein
  "deals ... damage"-Relikt dort tut, habe ich nicht untersucht; die Zeile in
  der Anteilstabelle (ueber 100 %) ist deshalb als Artefakt zu lesen, nicht als
  Messwert.
- **Die 16 `Add ... to Weapon`-Waffeneffekte** habe ich nur klassifiziert
  (bedingt, also zu Recht draussen), nicht durchgerechnet.

---

## QA-Log — Nachtrag zu QA-101 und Vorschlag fuer `qa/findings.md`

Die Datei bestand bereits und wird fortgefuehrt; ich lege sie nicht selbst an.
**Zeile QA-101 ersetzen durch:**

| ID | Titel | Prio | Adressat | Status | Letzte Pruefung |
|---|---|---|---|---|---|
| QA-101 | **"Die Rangfolge waere bei `candidate` dieselbe" ist widerlegt.** Drei Effekte (7120400/500/600) tragen die Startwaffen-Strafe x0,85 selbst; ein Kandidat kann sie mitbringen. Gemessen: R0 `[7120400, 6001400]` → d(equipped) −12,36 gegen d(candidate) +21,36, R1 +0,83 in beiden → **Reihenfolge gedreht**. 10 von 309 Relikten des Saves betroffen. **Nachtrag T-049 (2026-09-03, Commit `0dc54a6`): auf dem Stand nach der 0,6-Kalibrierung ziffernweise reproduziert (Level 15 / Tier 1: 203,4176 / −12,3576 / +21,3589 vor der Kalibrierung; 122,0506 / −7,4146 / +12,8153 danach), Rangfolge dreht auf Level 1, 12 und 15. Ausserdem geprueft und bestaetigt: die drei Effekte tragen laut Params **nur** x0,85 (12 Zeilen im ganzen Spiel mit diesem Muster) und keine Schadensart-Umwandlung; Differenz Programm gegen Param-Lesart 0,000000 je Schadensart. Die Fan-Behauptung "~40-50 % AP werden umgewandelt" gehoert nicht zu ihnen — siehe QA-113.** | P2 | director, developer | offen — Entscheid des Directors | 2026-09-03 |

**Neue Zeile anhaengen (ID vom Audit-3-Director zu vergeben, Vorschlag QA-113):**

| ID | Titel | Prio | Adressat | Status | Letzte Pruefung |
|---|---|---|---|---|---|
| QA-113 (vorgeschlagen) | **Vier "Starting armament deals magic/fire/lightning/holy damage"-Relikte (7120000/100/200/300) bewegen die Angriffskraft um exakt 0.** Die Params tragen eine echte Umwandlung `physicsAttackPower −30/−40/−50/−60` mit `<element>AttackPower +33/+44/+55/+66`; die flachen `*AttackPower`-Felder haben in `model.compute` kein Fach und erscheinen im ganzen `nrplanner/` nur als Beschriftung (`effecttext.py` Z. 116-120) — drei unabhaengige Suchen. Gemessen Wylder Lv12: Programm 0,000000, Param-Lesart +1,80 (vor der 0,6-Kalibrierung) bzw. +3,00 (danach), Physics −18/−30 gegen Fire +19,8/+33. Auf dem Save 3 von 309 Relikten (`Night of the Beast`, `Delicate Drizzly Scene`, `Grand Luminous Scene`); in den Wuerfelpools 40 Eintraege je Effekt, genauso viele wie fuer die drei modellierten Geschwister. Rangfolge gedreht: 21 bzw. 75 echte Ueberholvorgaenge, 348/402 diskordante Paare von 47 586. Die Effektkarte nennt die Zahlen, die Angriffskraft nicht → beruehrt A3, A5 und A7. Kein Test im Repo nennt ein flaches `*AttackPower`. Einbauhoehe erst nach einer Ablesung im Spiel entscheidbar (drei Lesarten, 91 / 116 / 117 bei Grundwert 114) | P2 | developer, director | offen | 2026-09-03 |

| ID | Titel | Prio | Adressat | Status | Letzte Pruefung |
|---|---|---|---|---|---|
| QA-114 (vorgeschlagen) | `damage.py` Z. 61-63 (wortgleich `tests/weapon_damage_cases.py` Z. 163-166) nennt `*AttackPowerRate` "carried by exactly three effects — the 'Starting armament inflicts ...' relics" und verschmilzt damit die Feldaussage (richtig: 3 Effekte, 12 Zeilen) mit der Familienaussage (falsch: die Familie hat 7 Mitglieder, `stateInfo 2101` → genau 7 Zeilen im ganzen Spiel). Wirkung belegt: R-005 hat die Fan-Notiz zur Konversion auf diese drei bezogen und die vier Geschwister nicht gesehen | P4 | developer | offen | 2026-09-03 |

---

## Anhang — Messskripte

Alle unter `<scratchpad>\t049\`, gegen den Klon `<scratchpad>\nr-t043` auf
`0dc54a6`. Reihenfolge wie im Bericht.

### `common.py` — gemeinsamer Zugriff (aus T-042 uebernommen, Pfad auf nr-t043 gedreht)

```python
"""T-049 shared helpers: raw row access and text lookup. Read-only.

Clone: <scratchpad>/nr-t043, detached at 0dc54a6.
"""
from __future__ import annotations

import pathlib
import struct
import sys

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
CLONE = SCRATCH / "nr-t043"
sys.path.insert(0, str(CLONE))

GAME = pathlib.Path(r"D:\SteamLibrary\steamapps\common\ELDEN RING NIGHTREIGN\Game")
DEFS = CLONE / "vendor" / "Paramdex" / "NR" / "Defs"

from nrdata import param, paramdef, regulation  # noqa: E402


class Bank:
    def __init__(self):
        self.defs = paramdef.load_all(DEFS)
        self.members = {f.basename[: -len(".param")]: f.data
                        for f in regulation.load_params(GAME / "regulation.bin")}
        self._cache = {}

    def table(self, name):
        if name not in self._cache:
            self._cache[name] = param.read(self.members[name], self.defs.get(name))
        return self._cache[name]

    def raw_rows(self, name):
        """[(row_id, row_bytes)] straight from the file, def-independent."""
        data = self.members[name]
        (strings_offset,) = struct.unpack_from("<I", data, 0)
        (row_count,) = struct.unpack_from("<H", data, 0x0A)
        (data_offset,) = struct.unpack_from("<Q", data, 0x30)
        row_size = (strings_offset - data_offset) // row_count if row_count else 0
        out = []
        for i in range(row_count):
            rid, off, _n = struct.unpack_from("<qQQ", data, 0x40 + i * 24)
            out.append((rid, data[off:off + row_size]))
        return out, row_size

    def def_row_size(self, name):
        pdef = self.defs.get(name)
        return pdef.row_size if pdef else None


def texts():
    from nrdata import extract
    return extract._load_text(GAME)


def f32_at(buf: bytes, off: int):
    if off + 4 > len(buf):
        return None
    (v,) = struct.unpack_from("<f", buf, off)
    return v
```

### `chain.py` — Punkt 1: Kette und undefinierte Bytes

```python
"""T-049 Punkt 1: AttachEffectParam 7120400/500/600 und ihre SpEffect-Kette
vollstaendig, inklusive der 48 vom Def nicht beschriebenen Bytes."""
from __future__ import annotations
import struct
from collections import Counter
from common import Bank, f32_at

IDS = [7120400, 7120500, 7120600, 7120100]  # 7120100 = "deals fire damage", Gegenprobe
b = Bank()
attach = b.table("AttachEffectParam")
sp = b.table("SpEffectParam")
sp_by_id = {r.id: r for r in sp.rows}
raw, row_size = b.raw_rows("SpEffectParam")
raw_by_id = dict(raw)
def_size = b.def_row_size("SpEffectParam")
pdef = b.defs.get("SpEffectParam")

# Neutralwert je Feld = haeufigster Wert ueber alle 13472 Zeilen
neutral = {}
for f in pdef.fields:
    if f.is_padding:
        continue
    c = Counter()
    for r in sp.rows:
        v = r.values.get(f.name)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            c[round(float(v), 6)] += 1
    if c:
        neutral[f.name] = c.most_common(1)[0][0]

def dump_sp(sid, tag=""):
    r = sp_by_id.get(sid)
    if r is None:
        print(f"    SpEffect {sid}: FEHLT")
        return
    out = []
    for f in pdef.fields:
        if f.is_padding:
            continue
        v = r.values.get(f.name)
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        n = neutral.get(f.name)
        if n is None or abs(float(v) - n) <= 1e-9:
            continue
        out.append(f"{f.name}={v!r}")
    print(f"    SpEffect {sid} {tag}: " + (", ".join(out) if out else "(alles neutral)"))

def tail_bytes(sid):
    buf = raw_by_id.get(sid)
    return None if buf is None else buf[def_size:]

print("A. AttachEffectParam-Zeilen")
att_by_id = {r.id: r for r in attach.rows}
for eid in IDS:
    r = att_by_id.get(eid)
    sp_ids = [r.values.get(f"passiveSpEffectId_{i}") for i in (1, 2, 3)]
    sp_ids += [r.values.get("permanentSpEffectId"), r.values.get("onHitSpEffect")]
    sp_ids = [i for i in sp_ids if isinstance(i, int) and i > 0]
    print(f"\n{eid}: attachTextId={r.values.get('attachTextId')} sp_ids={sp_ids} "
          f"exclusivityId={r.values.get('exclusivityId')} "
          f"isStrongestEffect={r.values.get('isStrongestEffect')} "
          f"isDebuff={r.values.get('isDebuff')}")
    for sid in sp_ids:
        dump_sp(sid, "(eigene Zeile)")
    for k in range(1, 9):
        nxt = eid + k
        if nxt in sp_by_id:
            dump_sp(nxt, f"(Nachbar +{k})")
        else:
            print(f"    SpEffect {nxt}: existiert nicht -> Nachbarschaft endet")
            break

print("\nB. Die 48 vom Def nicht beschriebenen Bytes (Offsets 976..1023)")
for eid in IDS:
    for k in range(0, 9):
        t = tail_bytes(eid + k)
        if t is None:
            continue
        vals = [f32_at(t, o) for o in range(0, len(t), 4)]
        print(f"  {eid + k}: " + " ".join(f"{v:g}" for v in vals))
```

### `tiers.py` — Byte-Vergleich der Stufen und die `stateInfo`-Maske

```python
"""T-049: sind die vier Nutzlastzeilen der drei 'inflicts'-Effekte identisch?
Und was ist die stateInfo-Konvention?"""
from __future__ import annotations
from collections import Counter
from common import Bank

b = Bank()
raw, row_size = b.raw_rows("SpEffectParam")
raw_by_id = dict(raw)
sp = b.table("SpEffectParam")
sp_by_id = {r.id: r for r in sp.rows}

print("== a) Byte-Vergleich der Nutzlastzeilen ==")
for base in (7120400, 7120500, 7120600, 7120000, 7120100, 7120200, 7120300):
    ref = raw_by_id.get(base + 1)
    same = []
    for k in (2, 3, 4):
        buf = raw_by_id.get(base + k)
        if buf is None:
            continue
        diff = [i for i in range(row_size) if buf[i] != ref[i]]
        same.append((base + k, len(diff), diff[:12]))
    print(f"  {base}: +1 gegen +2/+3/+4 -> " +
          "; ".join(f"{rid}: {n} Byte verschieden {offs}" for rid, n, offs in same))
    ref5 = raw_by_id.get(base + 5)
    if ref5 is not None:
        s2 = []
        for k in (6, 7, 8):
            buf = raw_by_id.get(base + k)
            if buf is None:
                continue
            diff = [i for i in range(row_size) if buf[i] != ref5[i]]
            s2.append(f"{base+k}: {len(diff)} Byte")
        print(f"       +5 gegen +6/+7/+8 -> " + "; ".join(s2))

print("\n== b) stateInfo ==")
c = Counter(r.values.get("stateInfo") for r in sp.rows)
for v in (2101, 152, 0):
    print(f"  stateInfo={v}: {c.get(v, 0)} Zeilen")
print("  Zeilen mit stateInfo=2101:",
      [r.id for r in sp.rows if r.values.get("stateInfo") == 2101])
```

*(`offsets.py` bildet dazu Offset 88/92/96/100/300/484 auf die Feldnamen ab und
liest `atkOccurrenceSpEffectId` bzw. `physicsAttackPower` der vier Stufen aus —
`[21,22,23,24]` bzw. `[-30,-40,-50,-60]`.)*

### `conversion_scan.py` — die unabhaengigen Suchmasken

```python
"""T-049: welche SpEffect-Zeilen im ganzen Spiel verschieben Schaden zwischen
Arten? Und welche tragen ueberhaupt *AttackPowerRate != 1?"""
from __future__ import annotations
from collections import Counter, defaultdict
from common import Bank

b = Bank()
sp = b.table("SpEffectParam")
FLAT = ["physicsAttackPower", "magicAttackPower", "fireAttackPower",
        "thunderAttackPower", "darkAttackPower"]
RATE = [f + "Rate" for f in FLAT]

print("== Maske 1: negatives physicsAttackPower UND positiver Elementwert ==")
hits = []
for r in sp.rows:
    p = r.values.get("physicsAttackPower", 0) or 0
    el = {f: r.values.get(f, 0) or 0 for f in FLAT[1:]}
    if p < 0 and any(v > 0 for v in el.values()):
        hits.append((r.id, p, {k: v for k, v in el.items() if v}))
print(f"  Treffer: {len(hits)}")
for rid, p, el in hits:
    print(f"    {rid}: physicsAttackPower={p} {el}")

print("\n== Maske 3: alle Zeilen mit einem *AttackPowerRate != 1.0 ==")
rate_rows = defaultdict(list)
for r in sp.rows:
    vals = {f: r.values.get(f) for f in RATE}
    if any(isinstance(v, float) and abs(v - 1.0) > 1e-9 for v in vals.values()):
        key = tuple(sorted((k, round(v, 6)) for k, v in vals.items()
                           if isinstance(v, float) and abs(v - 1.0) > 1e-9))
        rate_rows[key].append(r.id)
print(f"  Zeilen: {sum(len(v) for v in rate_rows.values())}, "
      f"Wertmuster: {len(rate_rows)}")
for key, ids in sorted(rate_rows.items(), key=lambda kv: -len(kv[1]))[:15]:
    print(f"    {dict(key)} -> {len(ids)} Zeilen, z.B. {ids[:8]}")
```

### `siblings.py` — Punkt 2: die ID-Baender der zehn Startwaffen

```python
"""T-049 Punkt 2: Geschwisterzeilen der zehn Startwaffen (...750000) im ID-Band."""
from __future__ import annotations
import sys, pathlib, os, collections
CLONE = pathlib.Path(__file__).resolve().parent.parent / "nr-t043"
sys.path.insert(0, str(CLONE))
os.environ.setdefault("NIGHTREIGN_SETTINGS_ORG", "DankYeeterQA")
os.environ.setdefault("NIGHTREIGN_SETTINGS_APP", "NightreignHelperQA_T049")
from common import Bank
from nrplanner import datasource

b = Bank()
epw = b.table("EquipParamWeapon")
rows = {r.id: r for r in epw.rows}
data = datasource.load_data()
names = {w["id"]: w["name"] for w in data["weapons"]}

STATUS_FIELDS = ["poizonAttackPower", "diseaseAttackPower", "bloodAttackPower",
                 "freezeAttackPower", "sleepAttackPower", "madnessAttackPower",
                 "curseAttackPower"]
ATK = ["attackBasePhysics", "attackBaseMagic", "attackBaseFire",
       "attackBaseThunder", "attackBaseDark", "attackBaseStamina"]
COR = ["correctStrength", "correctAgility", "correctMagic", "correctFaith",
       "correctLuck"]

by_band = collections.defaultdict(list)
for rid in rows:
    by_band[rid // 10000].append(rid)

for h in data["heroes"]:
    sw = h.get("starting_weapon")
    band = sw // 10000
    sib = sorted(by_band[band])
    print(f"\n  {h['name']}: {names.get(sw)!r} id={sw} band={band} "
          f"-> {len(sib)} Zeilen im Band")
    for rid in sib:
        r = rows[rid]
        st = {f: r.values.get(f) for f in STATUS_FIELDS if r.values.get(f)}
        atk = {f[len('attackBase'):]: r.values.get(f) for f in ATK if r.values.get(f)}
        cor = {f[len('correct'):]: r.values.get(f) for f in COR if r.values.get(f)}
        mark = "  <== Startwaffe" if rid == sw else ""
        print(f"     {rid}  {names.get(rid, r.name)!r} atk={atk} "
              f"scaling={cor} status={st}{mark}")

print("\n== Gegenprobe: Longsword-Band 2000000 ==")
for rid in sorted(by_band[200]):
    r = rows[rid]
    atk = {f[len('attackBase'):]: r.values.get(f) for f in ATK if r.values.get(f)}
    print(f"     {rid}  {names.get(rid, r.name)!r} atk={atk}")
```

### `infusion.py` — was die Infusionszeilen wirklich tun

```python
"""T-049: die Infusionszeilen ueber alle ID-Baender, plus der Fan-Prozentsatz."""
# (Kopf wie siblings.py)
OFFSETS = {0: "uninfundiert", 500: "Fire", 600: "Lightning", 700: "Sacred",
           800: "Magic", 900: "Cold", 1000: "Poison", 1100: "Bloody"}
ratios, elem_share = collections.defaultdict(list), collections.defaultdict(list)
for band, ids in by_band.items():
    ids = sorted(ids)
    base_id = ids[0]
    if base_id % 10000 != 0:
        continue
    bp = rows[base_id].values.get("attackBasePhysics", 0)
    if not bp:
        continue
    for rid in ids[1:]:
        label = OFFSETS.get(rid - base_id)
        if label is None:
            continue
        r = rows[rid]
        p = r.values.get("attackBasePhysics", 0)
        el = sum(r.values.get(f, 0) for k, f in ATK.items() if k != "Physics")
        ratios[label].append(p / bp)
        if p + el:
            elem_share[label].append(el / (p + el))
for label in OFFSETS.values():
    if label == "uninfundiert" or label not in ratios:
        continue
    rs, es = sorted(ratios[label]), sorted(elem_share[label])
    print(f"  {label:<10} n={len(rs):>4} phys/basis Median {statistics.median(rs):.6f} "
          f"haeufigste {collections.Counter(round(x,6) for x in rs).most_common(3)} | "
          f"Elementanteil Median {statistics.median(es)*100:6.2f} % "
          f"(Q1 {es[len(es)//4]*100:.2f} / Q3 {es[3*len(es)//4]*100:.2f})")
```

### `measure.py` / `rank.py` — Punkt 3 und 4, synthetischer Satz

```python
"""T-049 Punkt 3+4: Programm gegen Param-Lesart, je Schadensart und als Rangfolge.

Grundzustand: Wylder Lv12, Wylder's Greatsword in Slot 0 (Startwaffenpaarung),
Tier 1, sonst nichts. Kandidat = ein Relikt, Grenzbeitrag = final_total(mit) -
final_total(ohne), ungerundet.
"""
from __future__ import annotations
import sys, pathlib, os, json
CLONE = pathlib.Path(__file__).resolve().parent.parent / "nr-t043"
sys.path.insert(0, str(CLONE))
os.environ.setdefault("NIGHTREIGN_SETTINGS_ORG", "DankYeeterQA")
os.environ.setdefault("NIGHTREIGN_SETTINGS_APP", "NightreignHelperQA_T049")
from nrplanner import datasource, model, damage, weapons

data = datasource.load_data()
hero = next(h for h in data["heroes"] if h["name"] == "Wylder")
LEVEL, TIER = 12, 1
weapon = next(w for w in data["weapons"] if w["id"] == hero["starting_weapon"])
by_id = {int(e["id"]): e for e in data["effects"].values()}
TYPES = ["Physics", "Magic", "Fire", "Thunder", "Dark"]
K = weapons.GAME_ATTACK_POWER_RATE
FLAT_FOR_TYPE = {"physicsAttackPower": "Physics", "magicAttackPower": "Magic",
                 "fireAttackPower": "Fire", "thunderAttackPower": "Thunder",
                 "darkAttackPower": "Dark"}

class Slot:
    def __init__(self, weapon, tier):
        self.weapon, self.tier = weapon, tier
slot = Slot(weapon, TIER)

def build_for(ids):
    return model.compute(hero, LEVEL, [by_id[i] for i in ids],
                         data.get("curves", {}), weapon=weapon,
                         weapons_held=[weapon])

def program(ids):
    b = build_for(ids)
    _bare, now = damage.equipped(slot, 0, b, hero, data)
    return dict(now.final_per_type), now

def flat_shift(ids):
    """Summe der flachen *AttackPower der gewaehlten Effekte, je Schadensart."""
    out = {t: 0.0 for t in TYPES}
    for i in ids:
        for f, t in FLAT_FOR_TYPE.items():
            v = by_id[i]["modifiers"].get(f)
            if isinstance(v, (int, float)):
                out[t] += float(v)
    return out

def param_reading(ids, placement):
    """P0 = flach in `base` vor der Skalierung, P1 = auf die interne AK vor K,
    P2 = auf die angezeigte Zahl. Die Params sagen nicht, welche gilt."""
    per_type, now = program(ids)
    shift = flat_shift(ids)
    if not any(shift.values()):
        return dict(per_type)
    wr, scaled = now.weapon_rating, now.scaled_per_type
    out = dict(per_type)
    for t in TYPES:
        s = shift[t]
        if not s:
            continue
        if placement == "P2":
            out[t] = out.get(t, 0.0) + s
        elif placement == "P1":
            out[t] = out.get(t, 0.0) + s * K
        else:
            base = wr.base.get(t, 0.0)
            factor = (scaled.get(t, 0.0) / base) if base else 1.0
            out[t] = out.get(t, 0.0) + s * K * factor
    return out

CANDS = {
    "R0 (frost + Angriffsbuff)": [7120400, 6001400],
    "R1 (nur Angriffsbuff)":     [7000300],
    "R2 (deals fire damage)":    [7120100],
    "R3 (deals holy damage)":    [7120300],
    "R4 (inflicts poison)":      [7120500],
    "R5 (inflicts blood loss)":  [7120600],
}
base_prog, base_now = program([])
base_tot = sum(base_prog.values())
rows = []
for name, ids in CANDS.items():
    p = sum(program(ids)[0].values()) - base_tot
    q = {pl: sum(param_reading(ids, pl).values()) - base_tot
         for pl in ("P0", "P1", "P2")}
    rows.append((name, p, q))
for key, get in (("Programm", lambda r: r[1]), ("Param P0", lambda r: r[2]["P0"]),
                 ("Param P1", lambda r: r[2]["P1"]), ("Param P2", lambda r: r[2]["P2"])):
    print(f"  Rangfolge {key:<9}: {[r[0] for r in sorted(rows, key=lambda r: (-get(r), r[0]))]}")
```

### `flip.py` — Punkt 4 auf allen 309 besessenen Relikten

```python
"""T-049 Punkt 4: dreht die Param-Lesart die Rangfolge auf dem echten Bestand?"""
# (Kopf wie rank.py, zusaetzlich `from nrplanner import inventory`)
DEALS = {7120000, 7120100, 7120200, 7120300}

def shift(ids):
    """Nettoverschiebung der flachen *AttackPower -- nur die vier unbedingten
    Effekte. Die 17 uebrigen Traeger im Datensatz sind bedingt
    (`model.is_conditional`) und bleiben zu Recht draussen."""
    s = 0.0
    for i in ids:
        if i not in DEALS:
            continue
        for f in FLAT:
            v = by_id[i]["modifiers"].get(f)
            if isinstance(v, (int, float)):
                s += float(v)
    return s

inv = inventory.load(data)
base = total([])
rows = []
for n, it in enumerate(inv.relics):
    ids = list(it.effect_ids) + list(it.curse_ids)
    p = total(ids) - base
    s = shift(ids)
    rows.append((n, it.name, ids, p, p + K * s, p + s))

def rank_of(idx):
    return {rid: i for i, rid in
            enumerate([r[0] for r in sorted(rows, key=lambda r: (-r[idx], r[0]))])}

def discordant(a, b):
    ids = [r[0] for r in rows]
    return sum(1 for x, y in itertools.combinations(ids, 2)
               if (a[x] - a[y]) * (b[x] - b[y]) < 0)

rp, r1, r2 = rank_of(3), rank_of(4), rank_of(5)
print("diskordante Paare P1:", discordant(rp, r1), " P2:", discordant(rp, r2))
for label, idx, add in (("P1", 4, K * 3), ("P2", 5, 3.0)):
    ov = sorted({(r[1], round(r[3], 6)) for r in rows
                 if 0 < r[3] < add and not (set(r[2]) & DEALS)})
    print(f"{label}: {len(ov)} ueberholte Relikte", ov)
```

### Weitere Skripte im selben Ordner

| Datei | Zweck |
|---|---|
| `effects.py` | erste, in die Irre fuehrende Lesung der Marker-Zeilen (im Protokoll dokumentiert) |
| `offsets.py` | Offset → Feldname, und die Stufenwerte roh |
| `family.py` | alle sieben "Starting armament"-Effekte aus `data["effects"]` mit `modifiers`, `payload_tiers`, `inflicts` |
| `pools.py` | `11750100`, `weaponslots.base_ids`/`why_no_effects`, wo Statusaufbau sonst herkommt |
| `weapon_status.py` | `EquipParamWeapon`-Statusfelder, `spEffectBehaviorId`-Kette der Poison-/Bloody-Infusionen, die 8110xxx-Familie |
| `where.py` | wo die flachen `*AttackPower` im Programm landen (sechs Listen) plus zwei Repo-Suchen |
| `flat_family.py` | 21 Traeger flacher `*AttackPower`, 17 bedingt / 4 unbedingt, Bestandszaehlung |
| `xref.py` | Rueckwaertsindex ueber alle 4-Byte-Slots aller Tabellen |
| `pool_count.py` | 40 Pooleintraege je Effekt aus `AttachEffectTableParam` |
| `save_count.py` | 13 von 309 Relikten, aufgeschluesselt je Effekt |
| `rank_owned.py` | Rangfolge auf dem 13er-Kandidatensatz plus drei Kontrollen |
| `qa101_repro.py` | QA-101 auf Level 1/12/15 nachgefahren |
| `find203.py` | Identifikation der T-041-Grundzahl 203,4176 (Level 15 / Tier 1) |
| `rung.py` | `AttachEffectTableParam`-Felder: kein Stufenwaehler |
