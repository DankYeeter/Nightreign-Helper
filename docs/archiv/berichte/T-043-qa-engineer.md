# T-043 — Die Katalysator-Konstante C gefunden (qa-engineer, Nachtrag zu QA-099)

```
STATUS: erledigt
AUFTRAG: T-043 — Die Katalysator-Konstante C finden: Zauber-/Anrufungsskalierung
         der Staebe und Siegel (docs/tasks/T-043.md)
GELESEN: docs/tasks/T-043.md; docs/berichte/T-038-qa-engineer.md (Abschn. 8, 9, 14);
         GOAL.md (A7); docs/state.md (Abschn. "Zwei Sessions auf demselben Repo");
         qa/findings.md (QA-095 bis QA-099); nrplanner/weapons.py; nrdata/extract.py
         (Z. 2257-2420, Reinforce + AEC); nrdata/param.py; nrdata/paramdef.py;
         vendor/Paramdex/NR/Defs/{EquipParamWeapon,ReinforceParamWeapon,
         AttackElementCorrectParam}.xml; installierte regulation.bin
         (data_version 10350000); .claude/agent-memory/qa-engineer/
         project_attack_rating_calibration.md
GEAENDERT: docs/berichte/T-043-qa-engineer.md (diese Datei) — sonst keine.
           Kein Git im Arbeitsbaum. Messstrecke ausserhalb des Repos:
           <scratchpad>\t043\ (gt.py, reinforce.py, fit.py, outlier.py, pop.py,
           final.py, search.py, loose_ends.py) und der eigene Klon
           <scratchpad>\nr-t043 auf 89015aa.
ANNAHMEN: (1) Die Fan-Spalten Duchess/Revenant/Recluse und die RPS-Zahl geben die
          Anzeige des Spiels wieder — beide sind Fremdquellen, keine der 28 Zahlen
          ist von mir am Bildschirm nachgelesen. Sie stuetzen sich hier gegenseitig:
          zwei unabhaengig erhobene Spalten erfuellen dieselbe Formel exakt.
          (2) Die Fan-Zeilen stehen auf Level 12 und eigener Raritaet (T-038,
          QA-098 — Duchess-Spalte ist blockweise Level 11; sie trifft hier
          trotzdem 28 von 28, siehe Abschnitt 6).
NAECHSTER: director (Befund-IDs vergeben, Auftrag an developer schneiden)
BLOCKIERT DURCH: nichts
```

---

## 0. Ergebnis in drei Saetzen

Die Konstante C steht in **ReinforceParamWeapon**, im Feld, das der Paramdex
`unknown_1` nennt (Offset 128, f32, letztes Feld der Zeile): die Anzeige des
Spiels ist `floor(90 x unknown_1 x (1 + Kurve16(INT bzw. FAI)/100))`, und das
trifft **84 von 84** gemessenen Fan-Zellen und **28 von 28** RPS-Zahlen **exakt**,
ohne eine einzige Ausnahme. Der eine Katalysator, den T-038 nicht erklaeren
konnte, war kein Datenloch, sondern eine **Namenskollision**: `Recluse's Staff`
existiert zweimal in EquipParamWeapon (33750000 und 33770000), und die Zuordnung
von T-038 hat die falsche Zeile genommen. Damit ist QA-099 vollstaendig
aufloesbar: das Programm kann Katalysatoren nach der Kennzahl des Spiels reihen,
sobald `unknown_1` mitextrahiert wird — die Aussage aus T-038 Abschnitt 8, die
Zauberskalierung sei aus den Params nicht herleitbar, ist damit **widerrufen**.

---

## 1. Risiko-Briefing (vor der Messung, Reihenfolge eingehalten)

Formuliert vor dem ersten Lauf, in der Reihenfolge des Auftrags:

1. **ReinforceParamWeapon zuerst**, weil `reinforceTypeId` das einzige
   Unterscheidungsmerkmal der beiden sonst gleichen Staebe ist, das ueberhaupt
   eine Zahl traegt. Wenn C dort nicht steht, ist die billigste Hypothese
   verbraucht.
2. **AttackElementCorrectParam** als zweites, weil `attackElementCorrectId` das
   zweite unterscheidende Id ist und die Zeile Einfluss-Prozente traegt.
3. **Die Elden-Ring-Form nachrechnen**, nicht uebernehmen — sie liefert die
   *Gestalt* `Basis x (1 + correct/100 x Kurve/100 x Einfluss/100)`, aber keine
   Zahl; jeder Faktor muss einzeln aus den Params kommen.
4. **Globale Suche** als Rueckfallebene, mit gezaehlten Tabellen, damit "nicht
   gefunden" belegt ist statt behauptet.

Groesstes Risiko dabei: eine Formel, die 28 Punkte mit drei freien Parametern
trifft, beweist nichts. Gegenmittel von Anfang an: **kein Punktschaetzer.** Jede
Konstante wird als Intervallschnitt ueber alle Einzelzellen bestimmt, damit sie
widerlegbar ist, und jede Alternative wird ausdruecklich auf leere Schnittmenge
geprueft.

**Was das Briefing nicht vorhergesehen hat:** dass eine Fan-Zeile auf die falsche
Param-Zeile zeigt. Der Verdacht entstand erst in Schritt 4, als der Feldvergleich
des Ausreissers ein Waffen-Profil zeigte, das gar kein Katalysator sein kann
(`equippedSpell_R1/R2 = -1`). Er ist nicht rueckwirkend ins Briefing geschrieben.

---

## 2. Die Formel und die Herkunft jedes Faktors

```
Anzeige(Katalysator, Held) = floor( 90 x U x (1 + Kurve(A)/100) )

  U        = ReinforceParamWeapon[ reinforceTypeId + Stufen ].unknown_1
  Kurve    = CalcCorrectGraph[ EquipParamWeapon.correctType_Physics ]   (= 16)
  A        = Intelligence, wenn EquipParamWeapon.correctMagic != 0   (wepType 57)
             Faith,        wenn EquipParamWeapon.correctFaith != 0   (wepType 61)
  Stufen   = wie in nrplanner/weapons.py: max(0, min(upgrade, 4) - (rarity + 1))
```

| Faktor | Herkunft | Beleg |
|---|---|---|
| `unknown_1` | `ReinforceParamWeapon`, Offset **128**, `f32`, letztes Feld der Zeile | Der Paramdef deckt die Zeile **exakt**: `row_size = 132 B`, `pdef.row_size = 132 B`, `def_is_prefix = False`. Der Offset ist also nicht geraten, sondern die Zeile endet genau hinter diesem Feld. |
| `90` | **nicht aus einem Param belegt** — empirische Konstante | Intervallschnitt ueber alle 84 Fan-Zellen unter `floor`: **K in [89,9982, 90,0147]**. 90 liegt darin, mit Abstand 0,0018 nach unten und 0,0147 nach oben. Herkunftsfrage siehe Abschnitt 5. |
| Kurve 16 | `correctType_Physics` der Waffe; alle **255** Zeilen mit `wepType` 57/61 tragen `(16,16,16,16,16)` | Kurvenscan ueber alle 82 Kurven des Datensatzes: **genau 1 von 82** laesst ueberhaupt ein K zu, naemlich 16. Kurve 16 ist linear, `y = 150 * x/99`. |
| INT bzw. FAI | `correctMagic` = 100 / `correctFaith` = 0 bei allen 132 Stab-Zeilen mit AEC 20000; `correctFaith` = 100 / `correctMagic` = 0 bei allen 122 Siegel-Zeilen mit AEC 30000 | Ueberbestimmt: `wepType`, `correct{Stat}` und die `attackElementCorrectId` sagen dasselbe. Fuer die Umsetzung ist `correct{Stat} != 0` die tragfaehigste Wahl, weil sie ohne Kenntnis der wepType-Nummern auskommt. |
| `floor` | Abschneiden, nicht Runden | Unter `round` ist die Schnittmenge **leer** (K in [89,7833, 89,7333]). Gleiche Signatur wie bei QA-095. |

**`unknown_1` ist katalysatorgebunden, gezaehlt:** 97 von 255 Zeilen der
ReinforceParamWeapon tragen einen Wert != 1,0. Ueber alle **2317** Zeilen der
EquipParamWeapon sitzen **53** auf einer Basiszeile mit `unknown_1 != 1,0` — und
**alle 53 sind Katalysatoren** (`wepType` 57 oder 61). **0** Nicht-Katalysatoren.
Auch die Aufstiegszeilen aendern daran nichts: die 30 Basisgruppen, in deren
Gruppe *irgendeine* Zeile `unknown_1 != 1,0` traegt, werden ausschliesslich von
`wepType` 57 (132 Waffen) und 61 (122 Waffen) benutzt. Das Feld einzulesen
aendert also fuer keine andere Waffe etwas.

---

## 3. Tabelle der 28 Katalysatoren

`U` = `unknown_1` der Basiszeile, `90xU` = die Konstante C, `C(Fan)` = aus den
drei Zauberer-Spalten zurueckgerechneter Median (Vergleichswert aus T-038),
`RPS` = Skalierungszahl der RPS-Liste, `pred` = `floor(90 x U x 1,030303)`.

| Katalysator | id | Rar | reinf | U | 90xU | C(Fan) | Abw. | RPS | pred | |
|---|---|---|---|---|---|---|---|---|---|---|
| Carian Regal Scepter | 33090000 | 3 | 3400 | 1,5675 | 141,07 | 140,92 | +0,11 % | 145 | 145 | ok |
| Lusat's Glintstone Staff | 33240000 | 2 | 4300 | 1,4016 | 126,14 | 125,61 | +0,42 % | 129 | 129 | ok |
| Frenzied Flame Seal | 34090000 | 2 | 6800 | 1,4016 | 126,14 | 126,05 | +0,07 % | 129 | 129 | ok |
| Azur's Glintstone Staff | 33230000 | 2 | 4200 | 1,3824 | 124,42 | 124,24 | +0,15 % | 128 | 128 | ok |
| Dragon Communion Seal | 34080000 | 2 | 6700 | 1,3824 | 124,42 | 124,27 | +0,12 % | 128 | 128 | ok |
| Meteorite Staff | 33250000 | 2 | 4400 | 1,3536 | 121,82 | 121,35 | +0,39 % | 125 | 125 | ok |
| Erdtree Seal | 34070000 | 2 | 6600 | 1,3536 | 121,82 | 121,30 | +0,43 % | 125 | 125 | ok |
| Prince of Death's Staff | 33180000 | 2 | 3800 | 1,3248 | 119,23 | 119,06 | +0,15 % | 122 | 122 | ok |
| Golden Order Seal | 34060000 | 2 | 6500 | 1,3248 | 119,23 | 118,92 | +0,26 % | 122 | 122 | ok |
| Staff of the Guilty | 33260000 | 1 | 4500 | 1,2348 | 111,13 | 110,65 | +0,44 % | 114 | 114 | ok |
| Clawmark Seal | 34040000 | 1 | 6400 | 1,2348 | 111,13 | 110,59 | +0,49 % | 114 | 114 | ok |
| Carian Glintblade Staff | 33170000 | 1 | 3700 | 1,2250 | 110,25 | 110,00 | +0,23 % | 113 | 113 | ok |
| Crystal Staff | 33040000 | 1 | 3100 | 1,2152 | 109,37 | 109,29 | +0,07 % | 112 | 112 | ok |
| Rotten Crystal Staff | 33270000 | 1 | 4600 | 1,2054 | 108,49 | 108,06 | +0,40 % | 111 | 111 | ok |
| Giant's Seal | 34020000 | 1 | 6200 | 1,2054 | 108,49 | 108,22 | +0,25 % | 111 | 111 | ok |
| Carian Glintstone Staff | 33210000 | 1 | 4100 | 1,1956 | 107,60 | 107,16 | +0,41 % | 110 | 110 | ok |
| Albinauric Staff | 33190000 | 1 | 3900 | 1,1760 | 105,84 | 105,74 | +0,09 % | 109 | 109 | ok |
| Gravel Stone Seal | 34030000 | 1 | 6300 | 1,1760 | 105,84 | 105,84 | 0,00 % | 109 | 109 | ok |
| Gelmir Glintstone Staff | 33050000 | 1 | 3200 | 1,1662 | 104,96 | 104,65 | +0,30 % | 108 | 108 | ok |
| Staff of Loss | 33280000 | 1 | 4700 | 1,1466 | 103,19 | 102,88 | +0,30 % | 106 | 106 | ok |
| Godslayer's Seal | 34010000 | 1 | 6100 | 1,1466 | 103,19 | 102,86 | +0,32 % | 106 | 106 | ok |
| Digger's Staff | 33120000 | 0 | 3500 | 1,0600 | 95,40 | 95,12 | +0,30 % | 98 | 98 | ok |
| Academy Glintstone Staff | 33200000 | 0 | 4000 | 1,0400 | 93,60 | 93,18 | +0,45 % | 96 | 96 | ok |
| Astrologer's Staff | 33130000 | 0 | 3600 | 1,0200 | 91,80 | 91,55 | +0,27 % | 94 | 94 | ok |
| Demi-Human Queen's Staff | 33060000 | 0 | 3300 | 1,0100 | 90,90 | 90,59 | +0,34 % | 93 | 93 | ok |
| Glintstone Staff | 33000000 | 0 | 3000 | 1,0000 | 90,00 | 89,78 | +0,24 % | 92 | 92 | ok |
| Finger Seal | 34750000 | 0 | 6000 | 1,0000 | 90,00 | 89,78 | +0,24 % | 92 | 92 | ok |
| **Recluse's Staff** | **33750000** | 0 | **4800** | **0,8500** | **76,50** | **76,11** | +0,51 % | **78** | **78** | ok |

**28 von 28 innerhalb ±3 %** (Erfolgskriterium des Auftrags: 25 von 28).
Groesste Abweichung 0,51 %. Die durchgehend positive Abweichung gegen `C(Fan)`
ist kein Rest, sondern der Abschneide-Versatz: `C(Fan)` ist aus **abgeschnittenen**
Anzeigewerten zurueckgerechnet und liegt deshalb systematisch knapp unter der
ungerundeten Groesse — genau die Signatur, die in T-038 den 0,6-Faktor belegt hat.

### 3.1 Die Anzeige selbst, Zelle fuer Zelle

Nicht die zurueckgerechnete Konstante, sondern die ganzzahlige Anzeige:

| | Duchess (INT 36 / FAI 24) | Revenant (INT 27 / FAI 45) | Recluse (INT 45 / FAI 45) |
|---|---|---|---|
| Gemessene Zellen | 28 | 28 | 28 |
| `floor(90 x U x (1+Kurve16/100))` trifft | **28** | **28** | **28** |

`floor(90 x U x (1 + Kurve16(A)/100))` verfehlt **0 von 84** Zellen. Groesste
relative Abweichung vor dem Abschneiden: 0,74 %.

Beispiele aus dem Lauf: Carian Regal Scepter 218/198/237 gegen 218/198/237;
Recluse's Staff 118/107/128 gegen 118/107/128; Frenzied Flame Seal 172/212/212
gegen 172/212/212.

### 3.2 Die RPS-Zahl als unabhaengige zweite Quelle

Die RPS-Liste fuehrt fuer Katalysatoren keine Buchstaben, sondern eine Zahl
(78…145). Mit **festem** K = 90 verlangen alle 28 Zeilen denselben
Attributbeitrag: `c0 in [2,9856, 3,0568]`. In diesem Intervall liegt
`Kurve16(2) = 3,0303`. Mit `c0 = Kurve16(2)` trifft
`floor(90 x U x (1 + c0/100))` **28 von 28** RPS-Zahlen exakt, Fehlerliste leer.

Das ist ein echter zweiter Beleg, kein Nachrechnen desselben: die RPS-Zahlen
stammen aus einer anderen Erhebung, sind ganzzahlig, und derselbe Wert 90 sowie
dieselbe Spalte `unknown_1` erklaeren sie ohne einen zusaetzlichen freien
Parameter. Die alte Beschreibung "RPS = C/0,973" ist damit erklaert:
1/1,030303 = 0,9706.

Ob `c0` als `Kurve16(2)` (Attributwert 2) oder schlicht als 3,0 zu lesen ist,
entscheidet die Datenlage **nicht** — beide liegen im Intervall. Die Frage ist
fuer das Programm folgenlos, weil das Programm die Anzeige beim echten Attribut
des Helden bildet, nicht bei der RPS-Referenz.

---

## 4. Was die Formel widerlegen wuerde (Gegenbauten, einzeln durchgefuehrt)

Jeder Faktor ist einzeln angegriffen worden; "trifft" allein ist kein Beleg.

| Aenderung am Modell | Ergebnis |
|---|---|
| `unknown_1` weglassen (U := 1,0 fuer alle) | 27 von 28 Konstanten falsch; Carian Regal Scepter 90,0 statt 141,1 (−36 %), Recluse's Staff 90,0 statt 76,5 (+18 %) |
| Kurve 16 durch eine der 81 anderen Kurven ersetzen | **1 von 82** Kurven laesst ueberhaupt ein K zu. Fuer alle anderen 81 ist die Schnittmenge leer |
| Den AEC-Einfluss 0,90 **in** die Klammer nehmen (`1 + 0,9 x Kurve/100`) | Schnittmenge **leer**: K in [93,8009, 92,5061]. Untergrenze aus Albinauric Staff, Obergrenze aus Giant's Seal |
| `round` statt `floor` | Schnittmenge **leer**: K in [89,7833, 89,7333] |
| K von 90 abruecken | Erlaubt sind nur [89,9982, 90,0147]; ab 89,998 nach unten faellt Albinauric Staff, ab 90,015 nach oben faellt Carian Glintstone Staff |

Die dritte Zeile ist die interessanteste: sie zeigt, dass der **Einfluss 90** aus
AttackElementCorrectParam in der Anzeige der Zauberskalierung **nicht** wirkt,
obwohl `nrplanner/weapons.py` ihn in der Angriffskraft anwendet. Wer die Formel
umsetzt, darf `element_correct` fuer diesen Wert also **nicht** wiederverwenden.

---

## 5. Die Herkunft der 90 — offen, mit gezaehlter Negativliste

Die 90 ist **gemessen, nicht gefunden**. Nach L-001 gehoert ihr Rezept dazu:
Intervallschnitt ueber 84 `floor`-Bedingungen, `K in [89,9982, 90,0147]`,
Sicherheitsabstand nach unten 0,0018 (0,002 %), nach oben 0,0147 (0,016 %). Der
Wert 90 ist die einzige Zahl mit hoechstens zwei signifikanten Stellen in diesem
Intervall.

Gesucht wurde ueber die **gesamte** regulation.bin:

- 252 Param-Tabellen, **alle 252 dekodierbar**, 0 Fehlschlaege.
- 208 davon mit Paramdef, zusammen **6082 lesbare Felder je Zeilensatz**.
- Suche (a): jede Zeile, deren Id eine der 28 Katalysator-Ids **oder** eine ihrer
  referenzierten Ids ist (`behaviorVariationId`, `swordArtsParamId`,
  `spAtkcategory`, `spEffectBehaviorId0..2`, `residentSpEffectId`,
  `equippedSpell_R1/R2`, `attackElementCorrectId`, `reinforceTypeId`), mit einem
  Zahlenwert innerhalb 4 % des jeweiligen C: **1101 Treffer**, alle als
  Zufallstreffer erkennbar (`ActionButtonParam.angle = 110`,
  `AiSoundParam.aiSoundLevel = 128`, Reihen von `Influence…=100`). Kein Treffer
  bildet ueber die 28 hinweg ein Muster.
- Suche (b): jedes Feld der gesamten regulation, dessen Name auf
  magic/spell/sorcery/incantation/faith/correct/scaling deutet und den Wert 90
  oder 0,9 traegt: **213 Zellen**, und sie liegen **ausschliesslich** in
  `AttackElementCorrectParam` in den `Influence…`-Feldern der Zeilen 20000 und
  30000 — den Katalysator-Zeilen.

**Zwei Lesarten, die die Daten nicht trennen koennen:**

1. 90 ist eine Motorkonstante (Basis-Zauberskalierung).
2. 90 = `correct{Stat}` (100 bei allen 28) x `Influence…CorrectRate` (90 bei allen
   28) / 100 — also dieselbe Multiplikation, die die AR-Formel kennt, nur
   **ausserhalb** der Klammer statt darin.

Trennen liesse sich das nur an einem Katalysator mit `correct{Stat} != 100` oder
mit einer anderen AEC-Zeile. Ueber alle 255 Katalysator-Zeilen tragen aber
**alle** `correct{Stat} = 100`, und ausser der Fremdzeile 33770000 nutzen alle die
AEC 20000/30000. Der Fall existiert im Spiel nicht — die Frage ist heute
unentscheidbar und **muss** in der Umsetzung als Annahme benannt werden. Fuer die
Rangfolge ist sie folgenlos: beide Lesarten liefern denselben Wert.

---

## 6. Kopplungen und Nebenwirkungen

- **Die Duchess-Spalte ist hier brauchbar.** QA-098 haelt sie fuer die
  AR-Messung fuer unbrauchbar (Level-Mischung). Fuer Katalysatoren trifft sie
  28 von 28. Das ist kein Widerspruch: die Anzeige haengt ueber Kurve16 nur am
  Attributwert, und der Auftraggeber der Spalte hat INT 36 / FAI 24 offenbar
  einheitlich verwendet. **Nicht** verallgemeinern — es belegt nur, dass die
  Katalysator-Zellen dieser Spalte konsistent sind.
- **Die Aufstiegsstufen sind nicht gemessen.** `unknown_1` waechst je Gruppe
  monoton (Beispiel Glintstone Staff: 90,00 / 105,84 / 120,96 / 136,80; Carian
  Regal Scepter hat nur die eine Stufe). Die Fan-Quelle misst nur bei eigener
  Raritaet, also ist **nur die Basiszeile belegt**. Die Stufenlogik von
  `weapons.rate` (`min(upgrade,4) - (rarity+1)`) wuerde uebernommen werden, ist
  fuer diese Groesse aber ungeprueft.
- **Die physische AR der Katalysatoren bleibt unberuehrt** und bleibt falsch als
  Kennzahl. Beide Zahlen nebeneinander zu fuehren ist eine Anzeige-Entscheidung
  (ui-ux-designer), keine Rechenfrage.
- **Kein Test gelaufen.** `pytest` wurde bewusst **nicht** ausgefuehrt: der
  Test-Store `DankYeeterTests/NightreignHelperTests` ist maschinenweit, und
  parallel laeuft T-042 auf demselben Rechner. Ein zweiter Testprozess macht
  fremde Laeufe rot und sieht dabei wie eine Regression aus. Der Auftrag ist
  reine Messung; es wurde kein Anwendungscode angefasst, also besteht kein
  Regressionsverdacht, der einen Lauf rechtfertigt.

---

## 7. Befunde

Der Auftrag vergibt keine neue QA-Id (Nachtrag zu QA-099). Die drei Befunde
unter 7.2 bis 7.4 sind **neu** und brauchen eine Id vom Director; der
Nummernkreis der Scaling-Session (QA-095…099) ist erschoepft.

### 7.1 [Nachtrag zu QA-099 | Major | Hoch] Die Kennzahl der Katalysatoren ist herleitbar — die Aussage "in keinem Param" ist widerrufen

**Adressat:** developer (Umsetzung), director (A7-Lage), ui-ux-designer (Anzeige)
**Betroffen:** `nrdata/extract.py:2261-2281` (Reinforce-Extraktion, `unknown_1`
fehlt), `nrplanner/weapons.py:75` `rate()` (kennt nur die AR), jede Rangliste
ueber Waffen (`weapons.rank`, `damage.rank_candidates`, Arsenal-Tab)
**Umgebung:** regulation.bin data_version 10350000, mit DLC; Klon auf 89015aa

**Reproduktion:**
1. `nrplanner.weapons.rate` fuer alle 28 Katalysatoren mit Recluse Lv 12, eigene
   Raritaet, und nach Summe der Schadensarten ordnen.
2. Ergebnis: Rotten Crystal Staff 67,77 an erster, Carian Regal Scepter 37,11 an
   vorletzter Stelle.
3. Dieselben 28 nach `floor(90 x unknown_1 x (1 + Kurve16(INT|FAI)/100))` ordnen.

**Erwartet:** dieselbe Reihenfolge wie im Spiel.
**Tatsaechlich:** nach AR fuehrt Rotten Crystal Staff (182 im Spiel), nach der
Formel fuehrt Carian Regal Scepter (237 im Spiel) — die Formel gibt die
Spielreihenfolge, die AR nicht. Die vier Ersten nach AR: Rotten Crystal Staff,
Erdtree Seal, Meteorite Staff, Digger's Staff. Nach der Formel: Carian Regal
Scepter, Lusat's Glintstone Staff, Frenzied Flame Seal, Azur's Glintstone Staff.

**Analyse:** `extract.py` liest aus ReinforceParamWeapon fuenf `*AtkRate` und
fuenf `correct*Rate`, aber nicht `unknown_1`; damit kommt die einzige Zahl, die
Katalysatoren unterscheidet, gar nicht erst im Datensatz an. Volltextsuche im
Repo mit drei unabhaengigen Masken (`unknown_1`;
`spell.?scal|sorcer|incant|catalyst`; die Feldliste `AtkRate|correct.*Rate` in
`extract.py`): **kein Treffer** ausserhalb von `EquipParamAntique.unknown_1b`,
das ein anderes Feld einer anderen Tabelle ist. Das Feld wird heute nirgends
gelesen.

**Auswirkung:** Fuer die 28 Katalysatoren zeigt und ordnet das Programm eine
Groesse (~27…68), die das Spiel gar nicht anzeigt; die Spielzahl liegt zwischen
78 und 237. Jeder Berater-Vorschlag, der einen Katalysator gegen einen anderen
stellt, kann heute die Reihenfolge umdrehen. Nach A7 durfte das Programm bisher
zu Recht schweigen — dieser Grund ist entfallen.

**Vorschlag:** `unknown_1` in `extract.py` neben die Reinforce-Raten aufnehmen
(sprechender Name, mit der Herkunft im Kommentar: Offset 128, Paramdex-Name
`unknown_1`, hier als Zauberskalierungs-Rate belegt), und die Kennzahl an
**einer** Stelle bilden — analog zur Kalibrierkonstante aus QA-095, damit es nicht
zwei Rechenwege gibt. Die Konstante 90 mit ihrem Intervall benennen, nicht nackt.
Charakterisierungstest gegen die 84 gemessenen Zellen dieses Berichts; toetende
Mutationen sind vorhanden und benannt (Abschnitt 4): `unknown_1 -> 1,0`,
`floor -> round`, Kurve 16 -> irgendeine andere, Einfluss 0,9 in die Klammer.

### 7.2 [P2 | Major | Mittel] Zwei verschiedene Waffen heissen `Recluse's Staff` — der Datensatz macht sie ununterscheidbar

**Adressat:** developer, ui-ux-designer (Anzeige), director (Id)
**Betroffen:** `nrdata/extract.py` (Waffenliste), jede namensbasierte Zuordnung;
`nrplanner` Arsenal-Tab
**Umgebung:** regulation.bin data_version 10350000

**Reproduktion:**
1. Im Datensatz die Waffennamen zaehlen: `Recluse's Staff` -> [33750000, 33770000],
   `Finger Seal` -> [34000000, 34750000], `Scholar's Thrusting Sword` ->
   [5750000, 5760000, 5770000, 5780000].
2. Die beiden `Recluse's Staff`-Zeilen vergleichen: **42 von 268 Feldern**
   unterscheiden sich, darunter `reinforceTypeId` 4800 gegen 0,
   `attackElementCorrectId` 20000 gegen 10000, `weaponCategory` 8 gegen 5,
   `equippedSpell_R1/R2` 4000/4070 gegen −1/−1.

**Erwartet:** Zwei unterscheidbare Eintraege, oder nur der spielbare.
**Tatsaechlich:** Zwei gleichnamige Eintraege mit verschiedener Kennzahl
(76,50 gegen 90,00 nach der Formel) und identischer physischer AR-Groessenordnung.

**Analyse:** 33750000 ist die **Startwaffe der Recluse** (`starting_weapon` im
Datensatz; alle zehn Nightfarer-Startwaffen enden auf `750000`). 33770000 kann
keinen Zauber tragen (`equippedSpell_R1/R2 = −1`) und sitzt auf der generischen
Reinforce-Gruppe 0 und der generischen AEC 10000 — Hypothese, nicht belegt: eine
Nicht-Spieler-Fassung. Fan-Tabelle und RPS fuehren beide **genau eine**
`Recluse's Staff`, und beider Zahlen gehoeren eindeutig zu 33750000.

**Auswirkung:** Zwei Zeilen mit gleichem Namen im Arsenal; jede Auswahl,
Favoritenmarkierung oder Bericht-Referenz ueber den Namen ist mehrdeutig.
Konkret hier: die Messstrecke von T-038 hat deswegen die falsche Zeile benutzt
(7.3).

**Vorschlag:** Entscheiden, ob nicht-spielbare Waffenzeilen ueberhaupt in den
Datensatz gehoeren (Filterkriterium waere z. B. Erreichbarkeit ueber eine
Beutequelle — ungeprueft), und bis dahin bei Namensgleichheit die Id sichtbar
machen. Die Entscheidung gehoert dem director/ui-ux-designer, nicht dem Fix.

### 7.3 [P3 | Major | Niedrig] Korrektur an T-038 Abschnitt 8: die Zeile `Recluse's Staff` war falsch zugeordnet

**Adressat:** director (Berichtslage), qa (Messstrecke)
**Betroffen:** `docs/berichte/T-038-qa-engineer.md` Abschnitt 8;
`<scratchpad>\t038\match_weapons.py`; die C-Tabelle in QA-099

**Reproduktion:**
1. In `assignment.json` die Zeile `Recluse Staff` nachschlagen: `weapon_id`
   33770000, Stufe **`fuzzy`**.
2. `Finger Seal` ebenso: 34750000, Stufe `fuzzy`.

**Erwartet:** Eindeutige Zuordnung oder ein Nichttreffer, den die Strecke meldet.
**Tatsaechlich:** Bei zwei gleichnamigen Kandidaten faellt die Zuordnung durch
alle sicheren Stufen und wird in der Fuzzy-Stufe stillschweigend entschieden —
bei `Recluse's Staff` auf die falsche Zeile. `Finger Seal` ist folgenlos, weil
beide Zeilen zahlengleich sind.

**Analyse:** Die Zuordnungsstufen von T-038 sind global und exklusiv, aber die
Mehrdeutigkeit "zwei Familienkoepfe, ein Name" faellt in keine der Stufen und
erreicht die Fuzzy-Stufe, die einen Kandidaten waehlt statt abzubrechen.
Der Bericht T-038 nennt die 310/310-Quote als Guete — sie ist richtig gezaehlt,
sagt aber nichts ueber die Richtigkeit einer mehrdeutigen Zeile.

**Auswirkung:** T-038 Abschnitt 8 nennt fuer `Recluse's Staff` C = 76,1 als
unerklaerbar; genau diese eine Zeile hat die Suche nach der Herkunft in T-038
scheitern lassen. Alle anderen Zahlen von T-038 sind unberuehrt (nur diese zwei
Namen sind im Datensatz mehrdeutig, und nur einer davon ist folgenreich).

**Vorschlag:** In der C-Tabelle von QA-099 die Id 33750000 nachtragen. Fuer
kuenftige Fremdquellen-Zuordnungen: Mehrdeutigkeit im Kandidatenpool als
Nichttreffer melden, statt sie einer Aehnlichkeitsstufe zu ueberlassen.

### 7.4 [P3 | Minor | Niedrig] Ein Feldname ohne Bedeutung wird tragend — `unknown_1` ist nicht gegen einen Paramdex-Umbau abgesichert

**Adressat:** developer, architect (Datenschicht)
**Betroffen:** `vendor/Paramdex/NR/Defs/ReinforceParamWeapon.xml:294`
(`<Field Def="f32 unknown_1" />`), kuenftige `nrdata/extract.py`-Nutzung

**Reproduktion:** `param.read` zeigt fuer ReinforceParamWeapon
`row_size = 132`, `pdef.row_size = 132`, `def_is_prefix = False`; `unknown_1`
liegt auf Offset 128 und ist das letzte Feld.

**Erwartet:** Ein tragendes Feld wird ueber eine stabile Kennung gelesen.
**Tatsaechlich:** Der Zugriff laeuft ueber einen Platzhalternamen, den ein
Paramdex-Update jederzeit in einen richtigen Namen aendert. Dann liefert
`values.get("unknown_1", 1.0)` still den Vorgabewert 1,0 — und alle 28
Katalysatoren fallen lautlos auf dieselbe Kennzahl 90 zurueck.

**Analyse:** Der stille Rueckfall ist die eigentliche Gefahr, nicht die
Umbenennung. Der heutige Extraktionsstil (`r.values.get(name, default)`) macht
ein fehlendes Feld ununterscheidbar von einem Feld mit Vorgabewert. Das ist eine
Testbarkeitsfrage, kein heutiger Fehler.

**Vorschlag:** Beim Einlesen einmal pruefen, dass das Feld existiert **und** dass
mindestens eine Katalysator-Gruppe einen Wert != 1,0 traegt (heute 53 von 2317
Waffen; die Zahl gehoert mit ihrer Herkunft an die Pruefstelle), und sonst laut
scheitern statt still zu rechnen.

---

## 8. Offene Fragen (nicht von mir zu entscheiden)

1. **An den director / App Designer:** Soll die Katalysator-Kennzahl die
   physische AR in der Anzeige **ersetzen** oder **daneben** stehen? Beides ist
   mit A7 vereinbar; das ist eine Produktfrage.
2. **An den director:** Die 90 ist gemessen, nicht in einem Param gefunden
   (Abschnitt 5). Genuegt das dem A7-Massstab ("wo die Spieldateien eine
   Bewertung nicht hergeben, sagt das Programm das")? Meine neutrale Lesart:
   die Bewertung *folgt* aus den Spieldateien bis auf einen Skalenfaktor, der
   fuer die Reihenfolge ohne Belang ist — aber die Entscheidung ist nicht meine.
3. **An den developer:** Ist 33770000 (`Recluse's Staff` Nr. 2) ueberhaupt
   erreichbar? Wenn nein, ist es eine Datensatzfrage, nicht nur eine Anzeigefrage.
4. **An den director:** Der Nummernkreis QA-095…099 der Scaling-Session ist
   voll; 7.2 bis 7.4 brauchen Ids aus dem Audit-3-Kreis (ab QA-100).

---

## 9. Nicht getestet (bewusst)

- **Anzeige bei Aufstiegsstufen +1…+3.** Keine Fremdquelle vorhanden; nur die
  Basiszeile ist belegt (Abschnitt 6).
- **Die 227 unbenannten Katalysator-Zeilen.** Sie tragen dieselbe Struktur
  (`correctType` 16, AEC 20000/30000, `correct{Stat}` 100), aber keine
  Vergleichszahl.
- **Der Zusammenhang zwischen Kennzahl und tatsaechlichem Zauberschaden.** Die
  Formel gibt die *Anzeige* wieder; ob und wie sie in den Schaden eingeht, ist
  eine andere Messung (Magic/MagicTableParam wurden nicht ausgewertet).
- **Die Testsuite.** Bewusst nicht gestartet, Begruendung in Abschnitt 6.
- **Oberflaeche.** Kein Qt-Fenster geoeffnet; der Befund 7.1 ist an der
  Rechenschicht gemessen, nicht am Bildschirm.
- **Die uebrigen offenen Punkte der Scaling-Session** (QA-096 Raider x1,1819,
  QA-097 Cursed Claws) — nicht Gegenstand von T-043.

---

## 10. QA-Log — Fortschreibung fuer `qa/findings.md`

Bestehende Zeilen QA-001 bis QA-098 unveraendert. QA-099 wird **ersetzt**, drei
neue Zeilen brauchen Ids vom Director (hier als QA-1xx-Platzhalter markiert).

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-099 | **Staebe und Siegel: das Programm zeigt die physische AR (~27-68), das Spiel die Zauber-/Anrufungsskalierung (78-237).** Herkunft in T-043 gefunden: `Anzeige = floor(90 x ReinforceParamWeapon.unknown_1 x (1 + Kurve16(INT bzw. FAI)/100))` — trifft **84 von 84** Fan-Zellen und **28 von 28** RPS-Zahlen exakt. `unknown_1` (Offset 128, f32, letztes Feld; Paramdef deckt die Zeile exakt) wird von `extract.py` nicht gelesen; 53 von 2317 Waffen sitzen auf einer Gruppe mit Wert != 1,0, **alle** davon Katalysatoren. K = 90 aus Intervallschnitt [89,9982, 90,0147]; `round` statt `floor`, Einfluss 0,9 in der Klammer und 81 von 82 Kurven ergeben je eine **leere** Schnittmenge. Herkunft der 90 selbst offen (Motorkonstante oder correct x Einfluss/100 — nicht trennbar). **Echte Fehlreihung bestaetigt** (Rotten Crystal Staff 67,8 vor Carian Regal Scepter 37,1; Spiel 182 vs 237). Die Aussage aus T-038 "C steht in keinem Param" ist widerrufen | P2 | Major | developer, ui-ux-designer, director (A7) | 28 Katalysatoren x 3 Zauberer + RPS-Liste; alle 252 Param-Tabellen durchsucht; Bericht `docs/berichte/T-043-qa-engineer.md` | offen — umsetzbar | 2026-09-03 |
| QA-1xx (a) | **Zwei verschiedene Waffen heissen `Recluse's Staff`** (33750000 = Startwaffe der Recluse, Kennzahl 76,5; 33770000 = Fremdzeile ohne Zauberplatz, 42 von 268 Feldern verschieden). Ebenso `Finger Seal` (34000000/34750000, zahlengleich) und `Scholar's Thrusting Sword` (4 Zeilen). Namensbasierte Zuordnung und Anzeige sind mehrdeutig | P2 | Major | developer, ui-ux-designer, director | echte Spieldaten, Feldvergleich | offen | 2026-09-03 |
| QA-1xx (b) | **Korrektur an T-038 Abschnitt 8:** die Fan-Zeile `Recluse Staff` wurde ueber die Fuzzy-Stufe auf 33770000 statt 33750000 gelegt; genau diese Zeile hat die Herkunftssuche in T-038 scheitern lassen. Mehrdeutige Kandidaten muessen als Nichttreffer gemeldet werden statt einer Aehnlichkeitsstufe zu ueberlassen. Uebrige 308 Zuordnungen unberuehrt | P3 | Major | director, qa | `assignment.json` nachgeschlagen, Stufe `fuzzy` | offen | 2026-09-03 |
| QA-1xx (c) | **`unknown_1` ist ein Platzhaltername und wird tragend.** `values.get("unknown_1", 1.0)` macht ein umbenanntes Feld ununterscheidbar vom Vorgabewert — alle 28 Katalysatoren fielen still auf 90 zurueck. Pruefung beim Einlesen noetig (Feld vorhanden **und** mindestens eine Gruppe != 1,0) | P3 | Minor | developer, architect | `param.read`: row_size 132 = def 132, `def_is_prefix=False` | offen | 2026-09-03 |

---

## 11. Explorationsprotokoll

| Schritt | Skript | Ergebnis |
|---|---|---|
| 1 | `t043\gt.py` | Zielzahlen fixiert: C je Katalysator aus den drei Zauberer-Spalten, RPS-Zahl, alle unterscheidenden Ids. Auffaellig: **28 verschiedene** `reinforceTypeId`, 3 verschiedene AEC-Ids, eine Kurve |
| 2 | `t043\reinforce.py` | `unknown_1` gefunden: 27 von 28 erfuellen C ≈ 89,8 x unknown_1; Recluse's Staff faellt heraus |
| 3 | `t043\fit.py` | Kurvenscan, Intervallschnitt; `def_is_prefix=False` belegt den Offset; AEC-Zeilen 20000/30000 tragen Einfluss **90** |
| 4 | `t043\outlier.py` | 42 von 268 Feldern unterscheiden Recluse's Staff von Glintstone Staff — Profil eines Nicht-Katalysators |
| 5 | `t043\pop.py` | **Namenskollision:** `Recluse's Staff` existiert zweimal; 33750000 traegt `unknown_1 = 0,85` |
| 6 | `t043\final.py` | Mit der richtigen Zeile: 84/84 Fan-Zellen, 28/28 RPS, K in [89,9982, 90,0147]; drei Alternativmodelle mit leerer Schnittmenge widerlegt |
| 7 | `t043\search.py` | Negativliste: 252 Tabellen, 208 mit Def, 6082 Felder je Zeilensatz; einziger 90-Kandidat ist der AEC-Einfluss |
| 8 | `t043\loose_ends.py` | Gruppe 8700 gehoert zwei unbenannten Staeben (kein Nicht-Katalysator betroffen); QA-099-Fehlreihung auf 89015aa reproduziert; Stufenleiter je Gruppe |
| 9 | (Bash) | Startwaffen der zehn Nightfarer: Recluse -> **33750000**; Volltextsuche im Repo nach `unknown_1` mit drei Masken |

**Was gehalten hat:** Die Formel hat jeden Angriff ueberstanden, den ich fahren
konnte — anderer Kurvenindex, Rundung statt Abschneiden, Einfluss in der
Klammer, `unknown_1` entfernt, und die zweite Quelle mit festgehaltenem K. Kein
Rest, den ich nicht benennen kann; der einzige offene Punkt ist die Herkunft der
Zahl 90 selbst, und die ist als offen markiert, nicht weggerundet.

---

## 12. Anhang: Messstrecke

Alles ausserhalb des Repos. Klon `<scratchpad>\nr-t043` auf **89015aa** (eigener
Klon, weil `nr-t038` von einem parallelen Lauf mitbenutzt wird und dort ein
`checkout` waehrend meiner Messung den Baum verschoben haette). Python
`C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\.venv\Scripts\python.exe`.
Spieldaten ausschliesslich lesend.

Wiederverwendet aus T-038: `<scratchpad>\t038\assignment.json` (Fan-Zuordnung),
`<scratchpad>\rps_nightreign_weapons.tsv` (RPS-Liste). `t038\catalysts.py` und
`t038\raw_params.py` dienten als Vorlage; die Skripte dieses Laufs stehen in
`<scratchpad>\t043\` und sind unveraendert lauffaehig.

**Reproduktion in einem Befehl:**

```
.venv\Scripts\python.exe <scratchpad>\t043\gt.py      # Zielzahlen -> ground_truth.json
.venv\Scripts\python.exe <scratchpad>\t043\final.py   # alle Zahlen dieses Berichts
```

**Kern der Messung (aus `final.py`, gekuerzt):**

```python
# unknown_1 der Basiszeile, Kurve 16 beim Attribut des Helden
u = reinforce_rows[weapon["reinforceTypeId"]].values["unknown_1"]
stat = "Intelligence" if weapon["wepType"] == 57 else "Faith"
pred = 90.0 * u * (1 + evaluate_curve(curves["16"], attrs[stat]) / 100)
assert math.floor(pred) == fan_value          # 84 von 84

# K nie schaetzen, immer schneiden: floor(K*f) == g  <=>  K in [g/f, (g+1)/f)
lo = max(g / f for g, f in cells)             # 89.9982  (Albinauric Staff)
hi = min((g + 1) / f for g, f in cells)       # 90.0147  (Carian Glintstone Staff)
```
