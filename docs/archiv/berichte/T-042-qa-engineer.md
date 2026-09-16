# T-042 — Heldengebundene Waffenklassen-Raten in den Params gesucht: Raider und Cursed Claws (qa-engineer)

```
STATUS: erledigt
AUFTRAG: T-042 - Heldengebundene Waffenklassen-Raten in den Params finden: Raider x1,1819 und Cursed Claws x0,87 (Nachtrag zu QA-096 und QA-097)
GELESEN: docs/tasks/T-042.md, docs/berichte/T-038-qa-engineer.md (Abschnitte 5.3, 5.4, 6a-6f, 14),
  GOAL.md, docs/state.md (Abschnitt "Zwei Sessions auf demselben Repo"), qa/findings.md
  (Abschnitt T-038, QA-095 bis QA-099), nrdata/extract.py (Waffen ab Z. 2257, Helden,
  STAT_FIELDS), nrdata/param.py, nrdata/paramdef.py, nrplanner/weapons.py (rate),
  vendor/Paramdex/NR/Defs (alle 235 Defs maschinell; EquipParamWeapon, SpEffectParam,
  HeroParam, HeroStatusParam, CharaInitParam, ReinforceParamWeapon einzeln gelesen);
  Spielinstallation D:\SteamLibrary\...\NIGHTREIGN\Game\regulation.bin (data_version
  10350000) lesend; Messdaten scratchpad/t038/assignment.json (310 zugeordnete Waffen
  x 8 Nightfarer aus T-038).
GEÄNDERT: docs/berichte/T-042-qa-engineer.md (diese Datei, neu). Sonst keine Datei im
  Arbeitsbaum, kein Git-Kommando im Arbeitsbaum. Messskripte liegen ausserhalb des Repos
  unter <scratchpad>\t042\ (22 Schritte), der Messklon unter <scratchpad>\nr-t038, per
  git fetch + git checkout --detach auf 89015aa nachgezogen.
ANNAHMEN:
  1. Die Fan-Messung aus T-038 ist die Bezugsquelle; ihre Guardian-Spalte steht auf
     Level 11 und ihre Duchess-Spalte ist gemischt (QA-098). Beide sind in den
     Herleitungen unten enthalten - sie stuetzen das Ergebnis, sind aber fuer keinen
     Schluss noetig: die Cursed-Claws-Rechnung stimmt auch ohne sie auf 5 von 5, die
     Raider-Rechnung benutzt ohnehin nur die Raider-Spalte.
  2. `weapons.rate(w, attrs, upgrade=rarity+1)` ist der Programmwert, gegen den T-038
     gemessen hat. Ich habe dieselbe Funktion aufgerufen, damit die Zahlen vergleichbar
     bleiben - ein Fehler in ihr wuerde beide Berichte gleich treffen.
  3. Der Nutzer hat bestaetigt (03.09.2026), dass jeder Nightfarer die Cursed Claws
     fuehren kann. Die Fremdtraeger-Zellen der Fan-Tabelle sind daher Messungen.
NÄCHSTER: director (Einordnung der zwei Nachtraege, Entscheid ueber den Level-15-Messauftrag
  an den App Designer; QA-096 und QA-097 behalten ihre IDs, ihre Zahlen aendern sich)
BLOCKIERT DURCH: nichts
```

---

## 0. Ergebnis in vier Saetzen

**Beide Faktoren sind jetzt exakt bekannt, und beide stehen in keinem Param.**
QA-096 ist **exakt 1,18** (nicht 1,1819): `floor(0,6 × 1,18 × rate)` trifft **25 von 25**
Raider-Ablesungen auf die ganze Zahl, `floor(0,6 × rate)` trifft 0 von 25.
QA-097 ist **exakt 0,88** (nicht 0,87): `floor(0,6 × 0,88 × rate)` trifft **7 von 7**
Fremdtraegern und `floor(0,6 × rate)` den Revenant — mit 0,87 fallen 4 der 7 um genau 1
daneben.

Die Suche nach der Fundstelle ist **negativ ausgegangen, mit Nenner**: 252 Param-Tabellen,
257 912 Zeilen, 6 664 912 gelesene Gleitkommazellen; **nur zwei Tabellen im ganzen
regulation.bin koennen ueberhaupt einen Waffentyp nennen** (`EquipParamWeapon` — der Typ
der Waffe selbst — und `SpEffectParam` ueber `triggerOnWepType` / `wepTypeTrigger` /
`wepTypeTriggerCount` / `wepParamChange`), und dort ist die Waffentyp-Bindung **exakt
symmetrisch**: je 5 Zeilen pro Typ, fuer 19/23/35 wie fuer alle anderen, mit hoechstens
×1,09. Kein Feld von `EquipParamWeapon` trennt die 25 Waffen der Klassen 19/23 von den
uebrigen 285 der Fan-Tabelle, und keine heldenseitige Tabelle traegt ein Angriffsfeld.

Ein Ergebnis mit Substanz gibt es trotzdem: **1,18 ist in diesem Spiel keine beliebige
Zahl.** Als spielererreichbarer Angriffsmultiplikator kommt der exakte float32-Wert 1,18
ausschliesslich als **Relikt-Effektstufe** vor — u. a. „Improved Attack Power when
Two-Handing" (39 Wuerfelpools) und „Attack Up when Wielding Two Armaments" (38). Damit
ist ein **Quellenartefakt** die sparsamste Erklaerung fuer QA-096, und der Level-15-Test
in Abschnitt 7 trennt sie von einer echten Klassenregel. Fuer QA-097 gilt das Gegenteil:
0,88 ist als Angriffsrate **nirgends erreichbar** — jede Zeile, die sie traegt, haengt an
einem Eintrag, den nichts referenziert.

---

## 1. Risiko-Briefing (vor der Messung erstellt, Reihenfolge eingehalten)

1. **Groesstes Risiko: eine Namenssuche findet genau das Feld nicht, das man sucht.**
   Wenn Nightreign eine eigene Mechanik eingebaut hat, heisst ihr Feld im Paramdex
   vermutlich `unknown_NN` oder ist gar nicht beschrieben. Deshalb zuerst eine
   **Wertsuche ueber alle Gleitkommafelder aller Tabellen** statt einer Namenssuche —
   und ausdruecklich auch ueber die **vom Def nicht beschriebenen Bytes**.
2. **Zweites Risiko: eine „nicht vorhanden"-Aussage ohne Nenner ist wertlos.** Vor der
   Suche muss feststehen, wie viel jeder Def ueberhaupt abdeckt. `SpEffectParam` hat
   1024 B Zeilen bei 976 B Def — 48 unbeschriebene Bytes ueber 13 472 Zeilen sind genau
   die Stelle, an der ein neues Feld saesse.
3. **Drittes Risiko: 1,18 und 0,87 sind haeufige Zahlen.** Ein Treffer ist erst dann ein
   Fund, wenn der **Traeger** aufgeloest ist: wer referenziert die Zeile, und ist die
   Referenz helden- oder klassengebunden. Deshalb ein Rueckwaerts-Index ueber alle
   SpEffect-Referenzen, bevor irgendein Treffer geglaubt wird.
4. **Viertes Risiko: die Zahl selbst ist falsch.** T-038 hat 1,1819 und 0,87 als
   **Mediane** angegeben. Das Spiel schneidet ab; ein Median ueber abgeschnittene Werte
   ist kein Faktor. Vor der Suche nach dem Traeger also die Zahl per Intervallschnitt
   scharf machen — sonst sucht man nach der falschen Zahl.
5. **Fuenftes Risiko: die Abweichung sitzt nicht dort, wo man sie vermutet.** Ein
   Least-Squares-Fit `game/0,6 = X·Grundwert + Y·Skalierung` sagt vor jeder Hypothese,
   ob es ein flacher Multiplikator ist oder eine Attributsache.

Reihenfolge eingehalten: Inventar (2) → Zahl scharf (4) → Ort im Modell (5) →
Wertsuche (1) → Traegeraufloesung (3).

---

## 2. Messstrecke und Nenner

| | |
|---|---|
| regulation.bin | `D:\SteamLibrary\steamapps\common\ELDEN RING NIGHTREIGN\Game`, data_version 10350000, **nur lesend** |
| Param-Dateien darin | **252** |
| Defs in `vendor/Paramdex/NR/Defs` | 235; **44 Tabellen haben keinen Def** (zusammen 40 324 Zeilen) |
| Zeilen ueber alle Tabellen | **257 912** |
| gelesene Gleitkommazellen | **6 664 912** (alle f32/angle32-Felder der Defs **plus** jeder 4-Byte-Slot der undokumentierten Zeilenreste **plus** jeder 4-Byte-Slot der 44 def-losen Tabellen) |
| Fan-Ablesungen als Bezug | 310 Waffen × 8 Nightfarer aus T-038, `assignment.json` |
| Python | `.venv\Scripts\python.exe` (3.12) des Repos, Klon auf 89015aa |

Die Def-Abdeckung, weil jede Negativaussage davon abhaengt:

| Tabelle | Zeilen | Zeilenlaenge | Def-Laenge | unbeschriebener Rest |
|---|---|---|---|---|
| `EquipParamWeapon` | 2317 | 680 B | 680 B | **0 B, 0 Luecken** — 268 benannte Felder |
| `SpEffectParam` | 13 472 | 1024 B | 976 B | 48 B (12 Slots) — 386 benannte Felder |
| `HeroParam` | 10 | 176 B | 160 B | 16 B (4 Slots) — 30 benannte Felder |
| `CharaInitParam` | 1740 | 320 B | 320 B | **0 B** — 139 benannte Felder |
| `HeroStatusParam` | 100 | 28 B | 28 B | **0 B** — 15 benannte Felder |
| `ReinforceParamWeapon` | 255 | 132 B | 132 B | **0 B** — 39 benannte Felder |
| `PlayerCommonParam` | 1 | 760 B | 392 B | 368 B (92 Slots) — 111 benannte Felder |
| `AtkParam_Pc` | 8988 | 464 B | — | **ganze Zeile** (116 Slots), kein Def |

Die unbeschriebenen Reste wurden vollstaendig als f32 gelesen; Ergebnis in 3.3 und 4.3.

---

## 3. Nachtrag zu QA-096 — der Faktor ist **exakt 1,18**

### 3.1 Herleitung der Zahl (L-001: die Zahl traegt ihr Rezept)

Das Spiel schneidet ab (T-038, 4.1). Eine Ablesung liefert deshalb **keinen** Faktor,
sondern ein Intervall:

```
    game <= 0,6 · m · rate < game + 1
  =>  game / (0,6·rate)  <=  m  <  (game+1) / (0,6·rate)
```

Schnitt ueber alle 25 Raider-Ablesungen der `wep_type` 19 und 23:

| | |
|---|---|
| n | 25 Ablesungen |
| Schnittmenge | **m ∈ [1,179733 ; 1,180116)** — nicht leer |
| Breite | 0,000383 |
| bindende Ablesung (untere Schranke) | Brick Hammer (12190000) |
| enthaelt **1,18** | **ja** |
| enthaelt 1,175 / 1,1875 (19/16) / 7/6 / 1,20 / 1,15 | **nein, alle fuenf ausgeschlossen** |

Kein Mittelwert, kein Fit: das Intervall ist der Schnitt aller Einzelbedingungen. Es ist
**13,8-mal schmaler** als die von T-038 genannte Spanne 1,1786–1,1839 (Breite 0,0053) —
die Spanne war die Streuung der Abschneidefehler, nicht die Streuung des Faktors.

Gegenprobe, gleiche Rechnung fuer den Raider je Waffenklasse (nur Klassen mit n ≥ 4):

| Klasse | n | Intervall | enthaelt 1,0 |
|---|---|---|---|
| 19 + 23 | 25 | [1,1797 ; 1,1801) | **nein** |
| 1 | 17 | [0,9999 ; 1,0003) | ja |
| 5 | 22 | [0,9990 ; 1,0003) | ja |
| 21 | 15 | [1,0000 ; 1,0002) | ja |
| **41 (Kolossal)** | 16 | [0,9997 ; 1,0003) | ja |
| 51 | 13 | [0,9998 ; 1,0004) | ja |
| … 17 weitere Klassen | | alle enthalten 1,0 | ja |
| 3 | 19 | **leer** | — |
| 35 | 10 | **leer** | — |

Die beiden leeren Schnittmengen sind erklaert und **keine neuen Befunde**: Klasse 3
bricht allein an *Sword of Night and Flame* (T-038, 5.4 — dreitypige Waffe, 1,0172),
Klasse 35 allein an den Cursed Claws (Abschnitt 4). Nachgerechnet, nicht vermutet: ohne
diese je eine Waffe ergibt Klasse 3 (n = 18) m ∈ [0,9994 ; 1,0011) und Klasse 35 (n = 9)
m ∈ [0,9990 ; 1,0005) — beide enthalten 1,0.

### 3.2 Nachrechnung (Abnahmekriterium: mindestens drei Waffen)

`shown = floor(0,6 × 1,18 × rate)`, Raider Level 12, Waffe in eigener Raritaet:

| Waffe | id | `weapons.rate` | 0,6·rate | ×1,18 | Modell | Spiel |
|---|---|---|---|---|---|---|
| Greataxe | 15000000 | 224,2036 | 134,5222 | 158,7362 | **158** | **158** |
| Crescent Moon Axe | 15030000 | 224,2036 | 134,5222 | 158,7362 | **158** | **158** |
| Longhaft Axe | 15050000 | 224,2036 | 134,5222 | 158,7362 | **158** | **158** |
| Executioner's Greataxe | 15080000 | 275,9429 | 165,5657 | 195,3676 | **195** | **195** |
| Great Omenkiller Cleaver | 15020000 | 258,6965 | 155,2179 | 183,1571 | **183** | **183** |
| Rusted Anchor | 15060000 | 283,3342 | 170,0005 | 200,6006 | **200** | **200** |

**25 von 25 exakt.** Kontrolle ohne den Faktor: `floor(0,6 × rate)` trifft **0 von 25**.

### 3.3 Negativliste: keine Param-Stelle traegt das als Klassenregel

**(a) Nur zwei Tabellen im ganzen regulation.bin koennen einen Waffentyp nennen.**
Suche ueber die Feldnamen **aller Defs** nach
`wepType|weaponCategory|wepmotionCategory|wepCategory|weaponType|wepParam`:

| Tabelle | Zeilen | Felder |
|---|---|---|
| `EquipParamWeapon` | 2317 | `weaponCategory`, `wepmotionCategory`, `wepType` — der Typ der Waffe selbst |
| `SpEffectParam` | 13 472 | `wepParamChange`, `wepTypeTrigger`, `wepTypeTriggerCount`, `triggerOnWepType` |

Sonst keine. Eine Regel „Greataxes treffen haerter" kann also nur in
`SpEffectParam.triggerOnWepType` stehen — und dort steht sie nicht:

| Feld | Zeilen, die es setzen | Verteilung |
|---|---|---|
| `triggerOnWepType` | 213 | **exakt 5 Zeilen je Waffentyp** fuer 24 Typen (1,3,5,7,9,11,13,14,15,16,17,**19**,21,**23**,24,25,27,28,29,31,**35**,37,39,41,51), dazu 256 (86×) und 512 (2×) |
| `wepTypeTrigger` | 13 472 | 13 444-mal der Wert 1 — ein Vorgabewert, keine Bedingung |
| `wepTypeTriggerCount` | 122 | {3, 256, 512, 768, 1024, 2048} |
| `wepParamChange` | 1368 | {1, 2, 3} |

Die fuenf Zeilen zu `triggerOnWepType` = 19 sind 8161100 und 8600132/133/232/233; zu 23
sind es 8161300 und 8600136/137/236/237. Die einzige Angriffsrate darin ist **1,09**
(8161100 und 8161300) — das ist die Reliktfamilie „Improved ⟨Klasse⟩ Attack Power", die
`nrdata/extract.py` bereits liest, um die Waffenfamilien zu benennen. Fuer 19/23 gibt es
**keine Asymmetrie gegenueber den anderen 22 Typen**.

**(b) Kein Feld von `EquipParamWeapon` trennt die 25 Waffen von den uebrigen 285.**
Der Def deckt die Zeile vollstaendig ab (680 B von 680 B, 0 Luecken), also ist das eine
belastbare Aussage ueber **268 von 268** Feldern. Kriterium „alle 25 tragen denselben
Wert **und** keine der 285 anderen Waffen der Fan-Tabelle traegt ihn": **0 Treffer.**
Das schwaechere Kriterium „konstant ueber die 25" erfuellen 171 der 268 Felder; das
trennschaerfste davon (`unknown_7` = 327954) teilen immer noch 5,3 % der uebrigen
Waffen, danach kommen Schildwerte (`guardBaseRepel` 30, 9,5 %). Nichts, was eine Rate
tragen koennte.

Der Extractor liest **30 der 268** Felder. Die 238 ungelesenen sind damit trotzdem
abgehakt — nicht einzeln beschrieben, aber als Menge geprueft: keines trennt die Gruppe.

**(c) Heldenseitig gibt es nichts.**

| Tabelle | Zeilen | benannte Felder | Befund |
|---|---|---|---|
| `HeroParam` | 10 | 30 (+ 4 unbeschriebene Slots) | Die 16 unbeschriebenen Bytes je Held sind **zwei Text-ID-Reihen**: 411000+n und 413000+n, sauber durchnummeriert wie `characterSkillTitleId` (411010+n) und `ultimateArtTitleId` (413010+n). Kein Gleitkommawert, kein SpEffect. Von den 30 benannten Feldern unterscheiden sich zwischen den Helden nur Text-, Icon- und Freischalt-IDs plus `heroStatusParamId` und `characterAbilityCooldown`. Kein Angriffsfeld. |
| `HeroStatusParam` | 100 | 15 | wie T-038: kein Feld mit Rate/Power/Attack; die zwei Gleitkommafelder sind ueber alle 100 Zeilen 1,0 |
| `CharaInitParam` | 1740 | 139 | **kein einziges** Feld mit `effect`, `rate`, `power`, `atk` oder `attack` im Namen. Ueber die zehn Zeilen 90000–90009 unterscheiden sich 15 Felder, alle Ausruestungs- oder ID-Felder — **ausser einem**: `CharacterScale` (siehe 6.1, gemessen widerlegt) |
| `HeroMenuParam` | 10 | 8 | nur `charaInitParamId`, Kamera- und Text-IDs |
| `HeroOperationExplanationParam` | 30 | 6 | reine Texttabelle |
| `PersonalScenarioParam` | 227 | 15 | `heroId` + Szenario-IDs, keine Rate |
| `SpEffectParam.heroStatusId` | 5 Zeilen | — | 46260–46264 mit Werten 210000–250000; **keine** dieser fuenf traegt ein Angriffsfeld. Die Nightfarer haben `heroStatusParamId` 10000–100000, treffen diese Zeilen also nicht |

Die Waffen, die `CharaInitParam` den Nightfarern in die Hand gibt (Startwaffe,
Skill-Waffe, Ultimate-Waffe, Passiv-Waffe), tragen zusammen genau **vier**
SpEffect-Referenzen (Raider 704030, Ironeye 1940, Recluse 5121800, Executor 105030) —
alle vier ohne `*AttackRate`/`*AttackPowerRate` ungleich 1,0.

**(d) Der unbeschriebene Rest von `SpEffectParam` traegt es nicht.**
48 B = 12 f32-Slots ueber 13 472 Zeilen, vollstaendig gelesen. Fuenf Slots sind nahezu
konstant (+976: 1,0 in 13 466 Zeilen; +980: −1,0 in 13 470; +984: −1,0 in allen; +988:
ganzzahlig; +992: 1,0 in 13 467), die restlichen sieben halten keine Gleitkommadaten
(13 400+ verschiedene Bitmuster, ueberwiegend NaN). **Kein einziger Wert in
[1,17 ; 1,19], [0,86 ; 0,88] oder [1,14 ; 1,16].**

**(e) Eine Sprosse hoeher auf der Verstaerkungsleiter waere 1,23, nicht 1,18.**
`ReinforceParamWeapon`-Band 0 (das die rarity-0-Waffen des Blocks benutzen):
Sprossen 0/1/2/3 = 1,0 / **1,23** / 1,5 / 1,8. Ein Ablesefehler um eine Stufe ist damit
ausgeschlossen, nicht vermutet.

**(f) Kein HP-bedingter Effekt liegt bei 1,18.** Der Passivtext des Raiders nennt
„Attack power boosted when HP is greatly reduced" (T-038). Alle `SpEffectParam`-Zeilen
mit gesetztem `conditionHpRate` **und** flacher Angriffsrate: **6 Stueck**, Werte 1,02 /
1,07 / 1,10 / 1,105 / 1,14 / 1,20. **1,18 ist nicht dabei.**

### 3.4 Wo 1,18 in diesem Spiel ueberhaupt vorkommt (L-003: mechanismus-gebundenes Signal)

Statt eines Fensters die exakte float32-Bitfolge von 1,18, ueber alle 6 664 912 Zellen.
Vollstaendige Trefferliste:

| Tabelle | Feld(er) | Zeilen | wer erreicht das |
|---|---|---|---|
| `SpEffectParam` | die fuenf `*AttackRate` | **10** | siehe unten |
| `SpEffectParam` | die fuenf `*AttackPowerRate` | 1 (46315) | nur ueber `NpcParam` 76000000 ff. — Gegnereffekt |
| `SpEffectParam` | `*DiffenceRate` / `*DamageCutRate` / `maxMpRate` / Flaschenrate | 4 | Verteidigung, nicht Angriff |
| `ReinforceParamWeapon` | `baseAtkRate` + die fuenf `*AtkRate` | 5 (8206, 8506, 9106, 9206, 9906) | Verstaerkungsstufen von Baendern, die **keine** Waffe des Blocks benutzt (der Block liegt in den Baendern 0/200/300/400) |
| `ReinforceParamProtector` | sieben `resist*Rate` | 1 (104) | Ruestung |
| `NpcParam` | `slashDamageCutRate` | 8 | Gegner |

Die zehn `*AttackRate`-Zeilen mit exakt 1,18, mit ihrem Text aus den FMGs und der Zahl
der Wuerfelpools, in denen sie liegen:

| SpEffect | Wuerfelpools | Text (FMG) |
|---|---|---|
| 8300002 | **39** | **„Improved Attack Power when Two-Handing"** |
| 8310002 | **38** | **„Attack Up when Wielding Two Armaments"** |
| 7040100 | 41 | „Improved Guard Counters" |
| 7040200 | 40 | „Improved Critical Hits" |
| 8130001 | 36 | „Improved Critical Hits" |
| 8350001 | 36 | „Improved Skill Attack Power" |
| 8330202 | 37 | „Improved Charged Sorceries" |
| 8330302 | 36 | „Improved Charged Incantation" |
| 330900 | 0 | „Improved Charged Spells & Skills" (nur ueber `EquipParamAccessory` 3090) |
| 7036801 | 0 | von nichts referenziert |

Die Stufenleitern sind sauber: „Improved Attack Power when Two-Handing" hat 1,12 / 1,15 /
**1,18**, „Attack Up when Wielding Two Armaments" 1,12 / 1,15 / **1,18**, „Improved
Skill Attack Power" 1,15 / **1,18** / 1,21. 1,18 ist in diesem Spiel also die oberste
bzw. mittlere Stufe mehrerer **Relikt**-Effektfamilien — und der einzige Ort, an dem ein
Spieler einem Angriffsmultiplikator von genau 1,18 begegnet.

**Hypothese (als solche gekennzeichnet, nicht gemessen):** Der Greataxe-/Great-Hammer-
Block der Raider-Spalte wurde mit einer aktiven 1,18-Stufe abgelesen. „Improved Attack
Power when Two-Handing" passt am besten — es sind genau die Klassen, die man beidhaendig
fuehrt, die Fan-Tabelle ist nach Waffenklasse gegliedert (also blockweise abgelesen), und
der Faktor ist **flach**: der Least-Squares-Fit ueber die 25 Waffen ergibt
X(Grundwert) = 1,1869 und Y(Skalierung) = 1,1710 — beide gleich, also **kein**
Attributeffekt (ein STR×1,5 aus dem Beidhaendigfuehren wuerde X = 1 und Y > 1 liefern und
ist von T-038 ohnehin widerlegt). Gegenprobe an den Kontrollen: Wylder X = 1,0137 /
Y = 0,9823, Executor 0,9865 / 1,0093, Ironeye 1,0338 / 0,9406.

**Die konkurrierende Lesart bleibt offen:** eine echte, in der Engine verdrahtete
Klassenaffinitaet des Raiders, die in keinem Param steht. Beide Lesarten erzeugen
dieselbe Tabelle. Der Test in Abschnitt 7 trennt sie.

---

## 4. Nachtrag zu QA-097 — der Faktor ist **0,88**, nicht 0,87

### 4.1 Herleitung der Zahl

Derselbe Intervallschnitt, ueber die sieben Nightfarer, die die Claws nicht besitzen:

| | |
|---|---|
| n | 7 Ablesungen |
| Schnittmenge | **m ∈ [0,877440 ; 0,882700)** — nicht leer |
| Breite | 0,005259 |
| bindende Ablesung (untere Schranke) | Executor |
| enthaelt **0,88** | **ja** |
| enthaelt 0,87 / 0,875 (7/8) / 0,869565 (= 1/1,15) / 0,86 / 0,85 | **nein, alle fuenf ausgeschlossen** |
| Besitzer allein (Revenant) | m ∈ [0,999414 ; 1,011455) — **enthaelt 1,0** |

Der in T-038 genannte Median 0,87 lag **unterhalb** der Schnittmenge. Er entstand, weil
ein Median ueber abgeschnittene Werte systematisch nach unten zieht: `floor` nimmt im
Mittel 0,5 weg, was bei Anzeigen zwischen 42 und 71 rund 1 % ausmacht — genau der
Abstand zwischen 0,87 und 0,88.

### 4.2 Nachrechnung — alle acht Nightfarer exakt

`shown = floor(0,6 × m × rate)` mit m = 1,00 fuer den Revenant und m = 0,88 sonst:

| Nightfarer | `weapons.rate` | 0,6·rate | m | Modell | Spiel |
|---|---|---|---|---|---|
| Wylder | 96,2955 | 57,7773 | 0,88 | **50** | **50** |
| Guardian | 103,5039 | 62,1024 | 0,88 | **54** | **54** |
| Ironeye | 86,1266 | 51,6760 | 0,88 | **45** | **45** |
| Duchess | 105,5548 | 63,3329 | 0,88 | **55** | **55** |
| Raider | 97,1634 | 58,2980 | 0,88 | **51** | **51** |
| **Revenant** | 138,4145 | 83,0487 | **1,00** | **83** | **83** |
| Recluse | 135,9383 | 81,5630 | 0,88 | **71** | **71** |
| Executor | 79,7775 | 47,8665 | 0,88 | **42** | **42** |

**8 von 8 exakt.** Kontrolle mit m = 0,87: Ironeye 44 statt 45, Raider 50 statt 51,
Recluse 70 statt 71, Executor 41 statt 42 — **4 Fehlschlaege von 7**. Die Zahl ist damit
mechanismus-gebunden belegt und nicht nur „ungefaehr richtig".

Dass es ein **flacher** Multiplikator ist und keine Attributsache, ist unabhaengig
belegt: **Recluse und Revenant haben beide Faith 45**, ihre Skalierungsanteile sind
69,94 und 72,41 (3,5 % auseinander), ihre Spielzahlen 71 und 83 (17 % auseinander). Der
Least-Squares-Fit ueber die sieben Fremdtraeger liefert X(Grundwert) = 0,8743 und
Y(Skalierung) = 0,8640 — beide gleich, Restfehler ≤ 0,65 % je Held. Der Revenant liegt
in diesem Fit **+15,02 %** ueber der Vorhersage, als einziger.

### 4.3 Negativliste: 0,88 ist als Angriffsrate nirgends erreichbar

Exakte float32-Suche nach 0,88 ueber alle 6 664 912 Zellen. Vollstaendige Trefferliste
bei den **Angriffs**feldern:

| SpEffect | Feld(er) | referenziert von | erreichbar? |
|---|---|---|---|
| 96011 | die fuenf `*AttackRate` | `SpEffectParam#96010.replaceSpEffectId` — und 96010 wird **von nichts** referenziert | **nein** |
| 96201 | die fuenf `*AttackRate` | `SpEffectParam#96200.replaceSpEffectId` — 96200 von nichts referenziert | **nein** |
| 96211 | die fuenf `*AttackRate` | `SpEffectParam#96210.replaceSpEffectId` — 96210 von nichts referenziert | **nein** |
| 7347 | die fuenf `*AttackPowerRate` | **von nichts** | **nein** |
| 7500401 | die fuenf `*AttackRate` (0,87) | **von nichts** | **nein** |

Der Rueckwaerts-Index umfasst **6169 verschiedene Effekt-IDs**, gesammelt aus jedem
ganzzahligen Feld jeder Tabelle, dessen Name `spEffect` oder `effectId` enthaelt. Die
uebrigen 0,88-Treffer liegen auf `saReceiveDamageRate` (29 Zeilen), Ruestungs-Schnitt-
raten (`EquipParamProtector`, 12 Zellen), Schadensminderungen und `MaterialExParam` —
alle ohne Bezug zur Angriffskraft.

**Die Waffe selbst traegt nichts.** `EquipParamWeapon` 21750000 hat **keinen** der neun
SpEffect-Verweise gesetzt (`spEffectBehaviorId0..2`, `residentSpEffectId`, `…Id1`,
`…Id2`, `spEffectMsgId0..2` — alle ≤ 0). Dasselbe gilt fuer 23750000 (Raider's Greataxe)
und fuer die Beispielwaffen 15000000 / 12000000 des Raider-Blocks.

### 4.4 Was die Claws tatsaechlich von allen anderen unterscheidet

Feldweiser Vergleich gegen die anderen sieben Startwaffen (54 Felder abweichend) und
gegen **alle 310** Waffen der Fan-Tabelle (38 Felder). Nach Abzug von Modell-, Icon-,
Sortier- und `originEquipWep*`-Feldern bleiben vier Kandidaten, drei davon **durch
Messung widerlegt**:

| Feld | Wert | Gegenprobe | Ergebnis |
|---|---|---|---|
| `isDualBlade` | 1 | **15 weitere** Waffen der Fan-Tabelle tragen ebenfalls 1 (Katar, Caestus, Spiked Caestus, Iron Ball, Star Fist, Clinging Bone, Veteran's Prosthesis, Cipher Pata, Grafted Dragon, Hookclaws, Bloodhound Claws, Venomous Fang, Raptor Talons, Ornamental Straight Sword, Starscourge Greatsword) — alle acht Helden zwischen **0,957 und 1,000** | **widerlegt** |
| `spAttribute` | 10 | 33 weitere Waffen tragen 10, alle zwischen 0,957 und 1,041 | **widerlegt** |
| `reinforceTypeId` | 100 bei `rarity` 0 | Band 100 haben **20** Waffen — alle acht Startwaffen und deren Varianten. Sprosse 100 ist wie Sprosse 0 vollstaendig neutral (alle Raten 1,0) | **widerlegt** |
| `spAtkcategory` | **999** | **einzig** auf den vier Cursed-Claws-Zeilen 21750000, 21760000, 21770000, 72175000 im gesamten `EquipParamWeapon` (2317 Zeilen; naechsthaeufige Werte 240 ×122, 128 ×21, 145 ×21). **Kein** SpEffect referenziert 999: 77 Zeilen setzen `spAttributeVariationValue`, keine davon auf 999 | **nicht widerlegt, aber auch keine Rechnung** |

`spAtkcategory` = 999 ist damit der einzige Marker, der die Waffe im Param singulaer
macht — und er zeigt **auf nichts**. Das ist genau das Bild, das entsteht, wenn die
Engine einen Sonderfall an einem Param-Wert festmacht, den kein anderer Param aufloest.
Als Hypothese gekennzeichnet, nicht als Fund.

---

## 5. Negativliste je Tabelle (Auftragspunkt „traegt es nicht", mit Feldzahl)

Fenstersuche [1,17;1,19] ∪ [0,86;0,88] ∪ [1,14;1,16] ueber **252 Tabellen**:
**240 Tabellen enthalten in keinem einzigen Gleitkommafeld einen Wert in irgendeinem der
drei Fenster.** Die zwoelf mit Treffern sind vollstaendig aufgeloest (Abschnitte 3.4,
4.3, 6). Auszug der fuer die Frage relevanten Tabellen; „Zellen" ist die tatsaechlich
gelesene Zahl:

| Tabelle | Zeilen | benannte Felder | f32-Felder | Rest-Slots | Zellen | Treffer 1,18/0,87/1,15 |
|---|---|---|---|---|---|---|
| `SpEffectParam` | 13 472 | 386 | 139 | 12 | 2 034 272 | 277 / 149 / 1808 — **alle aufgeloest, keiner helden- oder klassengebunden** |
| `EquipParamWeapon` | 2317 | 268 | 46 | 0 | 106 582 | 0 / 0 / 13 (`criticalMultiplier` 8×, `weakC_DamageRate` 5×) |
| `EquipParamCustomWeapon` | 5148 | 9 | 0 | 0 | 0 | traegt es nicht (keine Gleitkommafelder) |
| `CharaInitParam` | 1740 | 139 | 1 | 0 | 1740 | 0 / 0 / 57 — alle auf `CharacterScale`, siehe 6.1 |
| `HeroParam` | 10 | 30 | 1 | 4 | 50 | **0 / 0 / 0 — traegt es nicht** |
| `HeroStatusParam` | 100 | 15 | 2 | 0 | 200 | **0 / 0 / 0 — traegt es nicht** |
| `HeroMenuParam` | 10 | 8 | 2 | 0 | 20 | **0 / 0 / 0 — traegt es nicht** |
| `HeroMenuCameraParam` | 6 | 12 | 10 | 0 | 60 | **0 / 0 / 0 — traegt es nicht** |
| `HeroOperationExplanationParam` | 30 | 6 | 0 | 0 | 0 | traegt es nicht |
| `PersonalScenarioParam` | 227 | 15 | 0 | 0 | 0 | traegt es nicht |
| `ReinforceParamWeapon` | 255 | 39 | 30 | 0 | 7650 | 37 / 0 / 40 — Verstaerkungsstufen fremder Baender (3.3e, 3.4) |
| `AttachEffectParam` | 2079 | 31 | 0 | 0 | 0 | traegt es nicht (Reliktzuordnung, keine Zahlen) |
| `AttachEffectTableParam` | 22 088 | 3 | 0 | 0 | 0 | traegt es nicht |
| `AttackElementCorrectParam` | 152 | 75 | 0 | 0 | 0 | **traegt es nicht** |
| `CalcCorrectGraph` | 82 | 19 | 19 | 0 | 1558 | **0 / 0 / 0 — traegt es nicht** |
| `SwordArtsParam` | 194 | 19 | 0 | 4 | 776 | **0 / 0 / 0 — traegt es nicht** |
| `EquipParamAccessory` | 136 | 17 | 1 | 0 | 136 | **0 / 0 / 0 — traegt es nicht** |
| `SpEffectVfxParam` | 1937 | 66 | 5 | 0 | 9685 | **0 / 0 / 0 — traegt es nicht** |
| `Magic` | 178 | 111 | 1 | 0 | 178 | **0 / 0 / 0 — traegt es nicht** |
| `PlayerCommonParam` | 1 | 111 | 51 | 92 | 143 | **0 / 0 / 0 — traegt es nicht** |
| `GameSystemCommonParam` | 1 | 412 | 132 | 2 | 134 | **0 / 0 / 0 — traegt es nicht** |
| `MenuCommonParam` | 1 | 74 | 49 | 13 | 62 | **0 / 0 / 0 — traegt es nicht** |
| `NpcParam` | 3016 | 338 | 75 | 8 | 250 328 | 8 / 14 / 38 — Gegnerzeilen (76000000 ff., 79300000 ff.) |
| `EquipParamProtector` | 307 | 208 | 23 | 0 | 7061 | 0 / 74 / 0 — Ruestungs-Schnittraten |
| `ClearCountCorrectParam` | 8 | 31 | 31 | 0 | 248 | 0 / 0 / 12 — NG+-Zeilen 3 und 5 |
| `MaterialExParam` | 381 | 7 | 5 | 0 | 1905 | 0 / 6 / 0 — Materialparameter |
| `Bullet` | 12 254 | 132 | 49 | 3 | 637 208 | 0 / 0 / 1 |
| `ActionButtonParam` | 220 | 26 | 9 | 0 | 1980 | 0 / 0 / 3 |
| `ReinforceParamProtector` | 17 | 19 | 15 | 0 | 255 | 7 / 0 / 7 — Ruestung |
| `AtkParam_Pc` | 8988 | **kein Def** | — | 116 | 1 042 608 | 0 / 3 / 44 — siehe 6.4 |
| `AtkParam_Npc` | 11 783 | **kein Def** | — | 116 | 1 366 828 | **0 / 0 / 0 — traegt es nicht** |
| `BehaviorParam_PC` | 10 855 | **kein Def** | — | 8 | 86 840 | **0 / 0 / 0 — traegt es nicht** |

Die uebrigen 41 def-losen Tabellen (Ladebalancer, Wwise-Zuordnungen, ItemLot, Shop,
Estus) sind mitgescannt und **trefferfrei**; sie sind sachlich ohnehin ohne Bezug.

---

## 6. Nebenbefunde (keine eigenen IDs, gehoeren aber in die Akte)

### 6.1 `CharaInitParam.CharacterScale` — eine je Nightfarer verschiedene Zahl, die der Extractor nie liest

| Zeile | heroId | Startwaffe | `CharacterScale` |
|---|---|---|---|
| 90000 | 1 Wylder | 3750000 | 1,00 |
| 90001 | 2 Guardian | 18750000 | **1,15** |
| 90002 | 3 Ironeye | 41750000 | 1,00 |
| 90003 | 4 Duchess | 1750000 | 0,96 |
| 90004 | 5 Raider | 23750000 | **1,12** |
| 90005 | 6 Revenant | **21750000** | **0,85** |
| 90006 | 7 Recluse | 33750000 | 1,05 |
| 90007 | 8 Executor | 9750000 | 1,02 |
| 90008 | 9 | 5750000 | 0,97 |
| 90009 | 10 | 11750000 | 0,99 |

Die Naehe von 0,85 zum vermuteten 0,87 und von 1,12 zu 1,18 ist **Zufall**, gemessen
(eigene Verhaeltnisse mit k = 0,6, Level 12, nicht die aus T-038 uebernommenen):
Pearson r(Scale, Verhaeltnis) = **−0,709** ueber alle acht — aber **+0,335**, sobald man
den Revenant weglaesst, der die Korrelation allein traegt. Entscheidender ist das
Einzelpaar: **Wylder (Scale 1,00) liegt bei 0,865, Guardian (Scale 1,15) bei 0,870** —
**0,58 % auseinander**, wo eine skalengetriebene Rate 15 % verlangen wuerde.
Fuer QA-096 scheidet das Feld schon konstruktiv aus: eine
Konstante je Held kann nicht nur auf zwei von 24 Waffenklassen wirken. **Kein Traeger —
aber ein bisher unbeschriebenes Feld, das der `architect` kennen sollte, falls je eine
Reichweiten- oder Trefferzonen-Rechnung dazukommt.**

Ebenfalls dort und bisher unbenutzt: die vollstaendige Startausruestung aller zehn
Nightfarer (`equip_Wep_Right_1`, `equip_Wep_Left_1`, Ruestungsteile,
`characterSkillWeapon`, `ultimateArtWeapon`, `passiveAbilityWeapon` — letzteres nur bei
Ironeye und Revenant gesetzt).

### 6.2 `PlayerCommonParam` hat 368 unbeschriebene Bytes, und darin steht 0,6

Slot +664 haelt exakt 0,6000000238418579, Slot +668 0,65, +660 0,5, +656 1,0, +648 0,8,
+652 0,9 — eine Reihe, keine einzelne Konstante. Die benannten Felder `unknown_34` und
`unknown_35` halten dieselben 0,6 und 0,65. **Das ist kein Beleg fuer QA-095**, sondern
ein Hinweis auf einen moeglichen Fundort: die Tabelle hat eine Zeile, 111 benannte und
92 unbeschriebene Slots, und ist von T-038 nicht angesehen worden. Wer QA-095 doch noch
einen Ort geben will, faengt hier an. Ausdruecklich unbewiesen.

### 6.3 Der Extractor liest 30 von 268 Feldern von `EquipParamWeapon`

Kein Fehler — nur die Zahl, weil der Auftrag danach fragt. Der Def ist vollstaendig
(680 B = 680 B, keine Luecken), es gibt also **kein** ungelesenes Nightreign-Feld, das
sich der Pruefung entzogen haette. Die 238 ungelesenen Felder sind fuer beide Befunde
als Menge geprueft (3.3b).

### 6.4 `AtkParam_Pc` bleibt eine Blindstelle mit Nenner

8988 Zeilen à 464 B, **kein NR-Def**. Alle 116 Slots je Zeile wurden als f32 gelesen
(1 042 608 Zellen); drei Zellen halten exakt 0,88 (Zeilen 200100, 210100, 212300 am
Offset +16), 44 liegen im 1,15-Fenster. Die Feldnamen sind unbekannt, also ist keine
dieser Zellen deutbar. Zwei Einschraenkungen halten den Befund klein: (a) die Zeilen des
Claws-Verhaltens (`behaviorVariationId` 2151 → Band 2151xx) existieren dort nicht, und
im Band 215100–215199 gibt es **null** Zellen in irgendeinem Fenster; (b) `AtkParam`
beschreibt einzelne Angriffe, nicht die angezeigte Waffenkennzahl. **Als Blindstelle
gemeldet, nicht als Verdacht.**

### 6.5 Zwei Bestaetigungen von T-038, beilaeufig mitgemessen

- Die Liste der heldengebundenen Ausreisser ist **vollstaendig**: von 310 Waffen zeigen
  genau **26** eine Spannweite ueber 8 % zwischen den acht Nightfarern — die 25 des
  Raider-Blocks und die Cursed Claws. Sonst nichts.
- *Sword of Night and Flame* (T-038, 5.4) bleibt der einzige Grund, warum der
  Intervallschnitt fuer `wep_type` 3 leer ist.

---

## 7. Messvorschlag fuer den App Designer (Level 15, mit Relikten)

Nur das Spiel kann jetzt noch entscheiden. Beide Tests brauchen **kein** Relikt — im
Gegenteil, sie brauchen den relikt**freien** Zustand; die Relikte sind nur insofern
noetig, als Level 15 ohne sie nicht erreichbar ist.

### Test A (QA-096) — ist 1,18 eine Regel oder ein Artefakt der Quelle?

**Vorgehen:** Raider auf **Level 15**, **kein Relikt eingesteckt** (oder wenigstens
keines mit „Improved Attack Power when Two-Handing", „Attack Up when Wielding Two
Armaments", „Improved Skill Attack Power", „Improved Critical Hits", „Improved Guard
Counters"), Waffe in ihrer eigenen Raritaet, **einhaendig** gefuehrt. Angezeigte
Angriffskraft ablesen. Dann dieselbe Waffe **beidhaendig** ablesen.

| Waffe | id | ohne Regel | mit ×1,18 | Abstand |
|---|---|---|---|---|
| Greataxe | 15000000 | **141** | **166** | 25 |
| Executioner's Greataxe | 15080000 | **174** | **205** | 31 |
| Great Omenkiller Cleaver | 15020000 | **163** | **192** | 29 |
| Rusted Anchor | 15060000 | **178** | **211** | 33 |
| Beastclaw Greathammer | 12150000 | **206** | **243** | 37 |
| Devourer's Scepter | 12200000 | **224** | **264** | 40 |

**Kontrollen in derselben Sitzung** (dieselbe Ausruestung, dieselbe Fuehrung):

| Kontrolle | Waffe | id | Erwartung ohne Regel | mit ×1,18 |
|---|---|---|---|---|
| Raider auf Kolossal (zeigt die Abweichung nie) | Raider's Greataxe | 23750000 | **158** | 186 |
| Raider auf Kolossal | Rotten Greataxe | 23150000 | **194** | 229 |
| anderer Nightfarer, gleiche Waffe | Greataxe / Wylder | 15000000 | **132** | — |
| anderer Nightfarer, gleiche Waffe | Greataxe / Executor | 15000000 | **107** | — |

**Auswertung:** Zeigt der Raider einhaendig und reliktfrei **141**, war 1,18 ein
Quellenartefakt — QA-096 faellt weg und die Fan-Tabelle bekommt eine zweite
Einschraenkung neben QA-098. Zeigt er **166**, ist es eine echte Regel, die in keinem
Param steht, und der `developer` braucht sie als benannte Ausnahme. Zeigt er einhaendig
141 und beidhaendig 166, ist es die Beidhaendigkeit — dann ist es weder Artefakt noch
Klassenregel, sondern eine Anzeigemechanik, die das Programm nicht kennt.
Die Abstaende sind ueberall ≥ 25 Punkte, also weit ueber jeder Ableseunsicherheit.

### Test B (QA-097) — traegt jeder Fremdtraeger 0,88?

**Vorgehen:** Revenant's Cursed Claws (21750000) in der Hand eines **Nicht-Revenants**
auf Level 15, reliktfrei, Angriffskraft ablesen. Wenn moeglich zusaetzlich mit dem
Revenant selbst.

| Nightfarer | ohne Regel | mit ×0,88 | (mit ×0,87) | Abstand |
|---|---|---|---|---|
| Recluse | **87** | **76** | 75 | 11 |
| Revenant (Besitzer) | **88** | — | — | — |
| Duchess | **66** | **58** | 57 | 8 |
| Guardian | **65** | **57** | 57 | 8 |
| Wylder | **61** | **54** | 53 | 7 |
| Raider | **61** | **53** | 53 | 8 |
| Ironeye | **54** | **48** | 47 | 6 |
| Executor | **49** | **43** | 42 | 6 |

**Auswertung:** Der **Recluse** ist der schaerfste Traeger — 87 gegen 76 gegen 75 trennt
alle drei Lesarten in einer einzigen Ablesung. Fuer die zweite Nachkommastelle
(0,88 gegen 0,87) genuegen Recluse **und** Ironeye: 76/75 und 48/47.

**Praktischer Vorbehalt:** wie ein Nicht-Revenant im Spiel an die Claws kommt, weiss ich
nicht — der Nutzer hat bestaetigt, dass es geht, aber nicht wie. Falls die Waffe nur
ueber einen Revenant-Mitspieler erreichbar ist, ist Test B teurer als Test A; er ist auch
der weniger dringende, weil QA-097 eine einzige Waffe betrifft.

---

## 8. Offene Fragen

**An den director, weiterzureichen an den App Designer:**

1. **QA-096 — Regel oder Quellenartefakt?** Beide Lesarten erklaeren die 25 Ablesungen
   gleich gut, und keine steht in den Params. Ich entscheide das nicht. Test A oben
   entscheidet es mit einer Ablesung. **Bis dahin sollte QA-096 nicht als Spielregel
   formuliert werden** — die Formulierung „Raider trifft ×1,18 haerter" in
   `qa/findings.md` ist eine Beobachtung, keine Mechanik.
2. **QA-097 — die Zahl war falsch.** 0,87 ist durch den Intervallschnitt ausgeschlossen;
   0,88 trifft alle acht. Sollen QA-096/097 ihre Zahlen im Log korrigiert bekommen
   (Vorschlag in Abschnitt 10), oder soll die alte Zahl als historischer Stand
   stehenbleiben?
3. **Reicht die Sicherheit fuer den Berater?** Der Nutzer hat „Groessenordnung ±10 %"
   als Rahmen gesetzt. Beide Abweichungen liegen bei 18 % bzw. 12 % — knapp ausserhalb.
   Die Rangfolge im Waffen-Tab aendert sich durch QA-097 kaum (eine Waffe), durch QA-096
   schon (25 Waffen beim Raider). Ob das eingebaut wird, ist eine A7-Frage, keine
   QA-Frage.

**An den `developer`, ohne Dringlichkeit:** `nrdata/extract.py` liest von
`CharaInitParam` keine Zeile. Falls der Berater je Startausruestung oder
Charaktergroesse braucht, liegen sie in den Zeilen 90000–90009 (6.1).

---

## 9. Nicht getestet (bewusst)

- **Das Spiel selbst.** Reine Messung laut Auftrag; alle Zahlen stammen aus
  regulation.bin und der Fan-Tabelle. Abschnitt 7 ist ein Vorschlag, kein Ergebnis.
- **Die Bedeutung der 44 def-losen Tabellen.** Sie sind wertmaessig durchsucht
  (40 324 Zeilen), aber ihre Felder sind unbenannt. `AtkParam_Pc` bleibt damit eine
  benannte Blindstelle (6.4); die uebrigen 43 sind sachlich ohne Bezug.
- **Nicht-Gleitkomma-Traeger.** Ein Faktor 1,18 koennte theoretisch als Ganzzahl 118
  mit implizitem Faktor 100 gespeichert sein. Ich habe nur f32 gesucht. Begruendung:
  jede Rate in diesem Paramsatz, die ich gesehen habe, ist f32; eine Ganzzahlsuche ueber
  118/88 haette hunderttausende Treffer ohne Trennschaerfe geliefert. **Das ist eine
  Luecke der Negativliste, und sie ist hier benannt.**
- **Die Vollstaendigkeit des Rueckwaerts-Index.** Er sammelt Felder, deren Name
  `spEffect` oder `effectId` enthaelt (6169 verschiedene IDs). Eine Referenz ueber ein
  anders benanntes Feld waere ihm entgangen.
- **Andere Level als 12 und 15.** T-038 hat die Level-Unabhaengigkeit des 0,6-Faktors
  belegt; fuer 1,18 und 0,88 habe ich sie **nicht** geprueft — die Fan-Tabelle hat nur
  Level 12.
- **Die FMG-Texte der SpEffect-Zeilen selbst.** SpEffect-Zeilen tragen keinen eigenen
  Text; aufgeloest habe ich ueber `AttachEffectParam.attachTextId`. Effekte ohne
  AttachEffect-Zeile bleiben namenlos (z. B. 7036801).
- **QA-099 (Katalysatoren).** Laeuft parallel als T-043, nicht mein Thema.

---

## 10. QA-Log — Nachtraege zu bestehenden IDs (keine neuen IDs)

Vorschlag fuer `qa/findings.md`; der Director uebertraegt. Zwei bestehende Zeilen
bekommen einen Nachtrag, keine neue ID wird vergeben.

| ID | Titel | Prio | Sev | Adressat | Status | Letzte Pruefung |
|----|-------|------|-----|----------|--------|----------------|
| QA-095 | Die Angriffskraft des Programms ist um den Faktor 1/0,6 zu hoch | P1 | Major | director, developer | offen — Entscheid F4 gefallen (einbauen), Auftrag T-045 liegt | 2026-09-03 |
| QA-096 | **Nachtrag T-042: der Faktor ist exakt 1,18, nicht 1,1819.** Intervallschnitt ueber 25 Ablesungen: m ∈ [1,179733 ; 1,180116); `floor(0,6·1,18·rate)` trifft **25/25**, `floor(0,6·rate)` 0/25; 1,175, 1,1875, 7/6, 1,20, 1,15 ausgeschlossen. **Keine Param-Stelle traegt es:** nur `EquipParamWeapon` und `SpEffectParam` koennen im ganzen regulation.bin einen Waffentyp nennen; `triggerOnWepType` ist ueber alle 24 Typen symmetrisch (je 5 Zeilen, max. 1,09); kein Feld von 268 trennt die 25 Waffen; `HeroParam`/`HeroStatusParam`/`CharaInitParam`/`HeroMenuParam` tragen kein Angriffsfeld; der unbeschriebene Rest von `SpEffectParam` (48 B × 13 472) traegt keinen Wert im Fenster; eine Sprosse hoeher waere 1,23. **Neue Spur:** exakt 1,18 existiert als spielererreichbarer Angriffsmultiplikator ausschliesslich als Relikt-Effektstufe — „Improved Attack Power when Two-Handing" (39 Pools), „Attack Up when Wielding Two Armaments" (38), „Improved Skill Attack Power", „Improved Critical Hits", „Improved Guard Counters". **Zwei Lesarten offen: Klassenregel des Raiders oder Ablesung der Quelle mit aktivem 1,18-Relikt.** Level-15-Test in T-042 Abschn. 7 trennt sie (Greataxe 15000000: 141 gegen 166) | P2 | Major | director (Entscheid), App Designer (Messung) | **offen — nicht einbauen, solange die Lesart nicht entschieden ist (A7)** | 2026-09-03 |
| QA-097 | **Nachtrag T-042: der Faktor ist 0,88, nicht 0,87.** Intervallschnitt ueber die sieben Fremdtraeger: m ∈ [0,877440 ; 0,882700); mit 0,88 stimmen **8 von 8** Ablesungen exakt (Besitzer m = 1,0), mit 0,87 fallen Ironeye, Raider, Recluse und Executor je um 1 daneben. Flacher Multiplikator, kein Attributeffekt (Recluse und Revenant haben beide Faith 45, Skalierung 69,9 gegen 72,4, Anzeige 71 gegen 83). **Keine Param-Stelle traegt es:** die Waffe hat keinen einzigen SpEffect-Verweis; jede Zeile mit exakt 0,88 auf einer `*AttackRate` (96011, 96201, 96211) haengt an einem `replaceSpEffectId`-Elter, den nichts referenziert; 7347 und 7500401 sind unreferenziert. Widerlegt durch Gegenprobe: `isDualBlade` (15 weitere Waffen, alle 0,957–1,000), `spAttribute` 10 (33 weitere), `reinforceTypeId` 100 (neutral, 20 Waffen). **Einziger singulaerer Marker: `spAtkcategory` = 999**, nur auf den vier Cursed-Claws-Zeilen, und kein Param loest ihn auf. Level-15-Test in T-042 Abschn. 7 (Recluse: 87 gegen 76 gegen 75) | P3 | Minor | director, App Designer (Messung) | offen — Zahl korrigiert, Ursache weiter unbekannt | 2026-09-03 |
| QA-098 | Fan-Messung: zwei der acht Spalten stehen nicht auf Level 12 | P3 | Major | director | offen — Quelle mit Einschraenkung fuehren | 2026-09-03 |
| QA-099 | Staebe und Siegel: das Programm zeigt die physische AR | P3 | Minor | developer, ui-ux-designer, director | offen (T-043 laeuft) | 2026-09-03 |

**Nebenbefund ohne ID (T-042):** `CharaInitParam` wird vom Extractor nicht gelesen und
enthaelt mit `CharacterScale` eine je Nightfarer verschiedene Zahl (Guardian 1,15,
Revenant 0,85) sowie die Startausruestung aller zehn. Als Traeger der beiden Abweichungen
gemessen widerlegt; als Datenquelle bisher unbenutzt.

**Nebenbefund ohne ID (T-042):** `PlayerCommonParam` hat eine Zeile mit 111 benannten und
**92 unbeschriebenen** 4-Byte-Slots; in den unbeschriebenen steht an +664 exakt 0,6.
Kein Beleg fuer QA-095, aber der erste plausible Fundort, den die Suche uebrig laesst.

---

## 11. Anhang: Messstrecke

Alle Skripte unter
`C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-ApplicationHelper\1bdcd2ac-606b-47f3-b01a-9963efeb41a0\scratchpad\t042\`,
Klon unter `…\scratchpad\nr-t038` (89015aa), Eingabedaten aus
`…\scratchpad\t038\assignment.json`. Alle lesen die Spieldateien ausschliesslich lesend.

| Skript | Zweck | Ausgabe |
|---|---|---|
| `common.py` | gemeinsamer Zugriff: Rohzeilen def-unabhaengig, Def-Laengen, FMG-Texte | — |
| `inventory.py` | 252 Tabellen: Zeilen, Zeilenlaenge, Def-Laenge, Feldzahl, unbeschriebener Rest, Luecken | `inventory.txt` |
| `sp_scan.py` | `SpEffectParam`: Fenstersuche ueber 139 benannte f32-Felder **und** die 12 unbeschriebenen Slots | `sp_scan.txt` |
| `sp_fields.py` | Bedingungsfelder von `SpEffectParam`, Detail des unbeschriebenen Rests | — |
| `carriers.py` | `triggerOnWepType` / `wepTypeTrigger` / `wepParamChange` / `heroStatusId` vollstaendig | `carriers.txt` |
| `hero_side.py` | `HeroParam`-Restbytes je Held, alle Felder je Held, `CharaInitParam` 90000–90009 | `hero_side.txt` |
| `scale_test.py` | `CharacterScale` gegen die Ablesungen (Widerlegung) | — |
| `equip_diff.py` | `EquipParamWeapon` feldweise: Gruppe 19/23 gegen Rest, Claws gegen Startwaffen und gegen alle 310 | `equip_diff.txt` |
| `split_fit.py` | Least-Squares `game/0,6 = X·Grundwert + Y·Skalierung` je Block und je Klasse | — |
| `global_scan.py` | **die Negativliste**: alle 252 Tabellen, 6 664 912 Zellen, drei Fenster | `global_scan.txt`, `global_scan.json` |
| `drill.py` | Detail der zwoelf Tabellen mit Treffern, Verstaerkungszeilen, SpEffect-Verweise der zwei Waffen | `drill.txt` |
| `xref.py` | Rueckwaerts-Index ueber 6169 Effekt-IDs; alle Zeilen mit flacher Rate im Fenster samt Referenten | `xref.txt` |
| `ladder.py` | Verstaerkungsleitern der benutzten Baender, Waffen der Nightfarer, Feldhistogramm der 25 | `ladder.txt` |
| `hero_tables.py` | alle Tabellen mit Hero/Chara/Player-Feld, alle Tabellen im Heldenband | `hero_tables.txt` |
| `groupA.py` | schwaecheres Trennkriterium fuer die 25, `isHeroPointCorrect`, `PlayerCommonParam`-Rest | `groupA.txt` |
| `dualblade.py` | Gegenproben `isDualBlade` / `spAttribute` / `spAtkcategory`; vollstaendige Ausreisserliste | `dualblade.txt` |
| `final_sweep.py` | Tabellen, die einen Waffentyp nennen koennen; `spAtkcategory` 999; HP-bedingte Raten; Passivtexte | `final_sweep.txt` |
| **`exact_factor.py`** | **Intervallschnitt fuer beide Faktoren** (L-001) | `exact_factor.txt` |
| **`verify.py`** | **Nachrechnung 25/25 und 8/8 mit Gegenprobe** (L-003) | `verify.txt` |
| **`exact_value_scan.py`** | **exakte float32-Suche nach 1,18 und 0,88 ueber alle Zellen** (L-003) | `exact_value_scan.txt` |
| `chase.py` | verfolgt die 0,88- und 1,18-Ketten bis zum Eintrittspunkt eines Spielers | — |
| `relic118.py` | Stufenleitern der Reliktfamilien, die 1,18 erreichen, mit Pool-Zahlen und FMG-Text | — |
| `lv15.py` | die Vorhersagetabellen aus Abschnitt 7 | — |

### 11.1 `exact_factor.py` — die Herleitung (Kern)

```python
K = 0.6

def interval(cells):
    """game <= 0.6*m*rate < game+1  ->  m in [game/(0.6 rate), (game+1)/(0.6 rate))"""
    lo, hi = 0.0, float("inf")
    worst = None
    for wid, hero, game in cells:
        rt = K * rate_of(wid, hero)          # nrplanner.weapons.rate, upgrade=rarity+1
        a, b = game / rt, (game + 1) / rt
        if a > lo:
            lo, worst = a, (wid, hero, "lower")
        if b < hi:
            hi, worst = b, (wid, hero, "upper")
    return lo, hi, worst

# QA-096: alle 25 Raider-Ablesungen der wep_type 19 und 23
cells = [(e["weapon_id"], "Raider", e["game"]["Raider"])
         for e in rows if e["wep_type"] in (19, 23)]
# -> m in [1.179733, 1.180116);  1.18 innen, 1.175/1.1875/7-6/1.20/1.15 aussen

# QA-097: die sieben Nightfarer, denen die Claws nicht gehoeren
cells = [(21750000, h, e["game"][h]) for h in HEROES if h != "Revenant"]
# -> m in [0.877440, 0.882700);  0.88 innen, 0.87/0.875/0.869565/0.86/0.85 aussen
```

### 11.2 `verify.py` — die Nachrechnung (Kern)

```python
# Claim A: Raider, wep_type 19/23
ok = sum(1 for e in rows if e["wep_type"] in (19, 23)
         and math.floor(0.6 * 1.18 * rate_of(e["weapon_id"], "Raider"))
             == e["game"]["Raider"])                      # -> 25 von 25
kontrolle = sum(1 for e in rows if e["wep_type"] in (19, 23)
                and math.floor(0.6 * rate_of(e["weapon_id"], "Raider"))
                    == e["game"]["Raider"])               # -> 0 von 25

# Claim B: Cursed Claws
for h in HEROES:
    m = 1.0 if h == "Revenant" else 0.88
    assert math.floor(0.6 * m * rate_of(21750000, h)) == e["game"][h]   # 8 von 8
# mit m = 0.87 statt 0.88: Ironeye 44/45, Raider 50/51, Recluse 70/71, Executor 41/42
```

### 11.3 `exact_value_scan.py` — die Negativliste (Kern)

```python
TARGETS = {"1.18": struct.unpack("<f", struct.pack("<f", 1.18))[0],
           "0.88": struct.unpack("<f", struct.pack("<f", 0.88))[0]}

for name in sorted(bank.members):                 # alle 252 Param-Dateien
    pdef = bank.defs.get(name)
    raw, row_size = bank.raw_rows(name)           # def-unabhaengig aus der Datei
    slots = []
    if pdef is not None:
        slots += [(f.name, f.offset) for f in pdef.fields
                  if f.type in ("f32", "angle32") and not f.is_padding and f.count == 1]
        slots += [(f"<tail+{o}>", o)              # der unbeschriebene Rest
                  for o in range(pdef.row_size, row_size - 3, 4)]
    else:
        slots += [(f"<nodef+{o}>", o)             # Tabellen ohne Def: ganze Zeile
                  for o in range(0, row_size - 3, 4)]
    for rid, buf in raw:
        for fname, off in slots:
            (v,) = struct.unpack_from("<f", buf, off)
            for label, target in TARGETS.items():
                if v == target:                   # exakte Bitgleichheit, kein Fenster
                    found[(name, fname, label)].append(rid)
# 6 664 912 Zellen; 1,18 in 6 Tabellen, 0,88 in 6 Tabellen; alle Treffer in 3.4 / 4.3
```
