# T-189 — Worauf rankt A17, wenn keine Waffe mehr da ist? (architect)

```
STATUS: erledigt
AUFTRAG: T-189 — Worauf rankt A17, wenn keine Waffe mehr da ist?
GELESEN: ~/.claude/agents/_rahmen.md, docs/tasks/T-189.md, CLAUDE.md,
         GOAL.md (A16/A17, Z. 255-315), docs/state.md,
         docs/berichte/T-188-developer.md,
         ARCHITECTURE.md (Entscheidungen, Themenbereich C),
         ARCHITECTURE_REGISTER.md,
         UI_SPEC.md (AK-43, AK-182, AK-190 bis AK-194, AK-205),
         nrplanner/advisor/goals.py, types.py, evaluate.py, candidates.py,
         nrplanner/advisorbar.py, nrplanner/damage.py, nrplanner/model.py,
         nrplanner/weaponslots.py, tests/advisor_cases.py,
         .claude/agent-memory/architect/ (MEMORY.md, project_parallele_laeufe),
         docs/research/R-004.md, R-005.md, R-006.md (Kurzantwort und
         "Konsequenz fuer uns"; alle drei betreffen die Rankinggrundlage und
         sind in AD-032 verarbeitet). R-001 bis R-003 betreffen
         `texture2ddecoder` und Lizenzfragen, nicht den Berater; docs/legal/
         fuehrt C-001 bis C-004 und AUFLAGEN.md, keines beruehrt A17.
         Ein R-007 gibt es nicht (`ls docs/research/`).
GEAENDERT: ARCHITECTURE.md (AD-032 neu, 326 Zeilen, in Themenbereich C;
           zwei Indexstellen nachgezogen), ARCHITECTURE_REGISTER.md
           (Tabelle-1-Zeile AD-032 von "nicht vergeben" auf "vergeben,
           Status offen" plus zwei Saetze darunter),
           docs/berichte/T-189-architect.md,
           .claude/agent-memory/architect/MEMORY.md,
           .claude/agent-memory/architect/project_parallele_laeufe.md,
           .claude/agent-memory/architect/project_datenabzug_katalysatoren.md
           (neu). **Nichts committet**, wie beauftragt. Kein Anwendungscode,
           keine Tests.
ANNAHMEN: 1) "Unterscheidbar" heisst: Grenzbeitrag ungleich 0 im Pool eines
          freien weissen Slots (210 gewoehnliche Kopien), Toleranz 1e-9.
          2) Die Grundgesamtheit des Auftrags ("210 gewoehnliche Kopien") ist
          die des weissen Slots; Deep bleibt draussen, wie in T-188.
          3) Option C rechnet die Attributspunkte der fuenf **offensiven**
          Attribute; welche Attribute eine solche Richtung zaehlen wuerde,
          ist selbst eine Entscheidung und in AD-032 als solche benannt.
NAECHSTER: director — er legt AD-032 dem App Designer vor. Erst nach dessen
           Wahl der `developer` fuer A17 Teil 2 (AK-190/192/193).
BLOCKIERT DURCH: nichts. Meine Arbeit ist fertig; **Teil 2 ist blockiert**,
                 bis der App Designer eine der vier Optionen waehlt.
```

## Urteil

Der Docstring von `_attack_multiplier_mean` und `GOAL.md` A17 widersprechen
sich nicht in der Sache, sondern in der Frage, die sie beantworten. Ohne
Armatur skaliert ein Attributsbonus tatsaechlich nichts — und eine Rangfolge
mit 184 Nullen hilft dem Spieler tatsaechlich nicht. Loesbar ist das nur,
indem man **eine feste Groesse an die Stelle der weggefallenen Waffe setzt**,
und jede solche Groesse kostet etwas. Vier Optionen, alle gemessen, liegen als
**AD-032 mit offenem Ausgang** vor. Ich empfehle **Option B**; entschieden ist
nichts.

## Messumgebung und Rezept (L-001, L-009)

Gilt fuer **jede** Zahl in diesem Bericht und in AD-032.

| | |
|---|---|
| Datensatz | `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`, `data_version` **10350000**, 8 387 819 Bytes, 2026-08-24 |
| Spielstand | der des Nutzers, **nur lesend** ueber `inventory.load`; **312** Kopien, davon **210** gewoehnliche, 102 Deep |
| Grundgesamtheit | die **210 gewoehnlichen** Kopien, gezogen ueber einen freien **weissen** Slot, nichts gehalten, Grundzustand leer |
| Nightfarer | Wylder, wo nicht anders genannt; Level **15** (`tests/advisor_cases.LEVEL`) |
| Weg | `candidates.pool(...)` mit je einer Zielrichtungs-Registry, `types.marginal_for`. **Kein Programmstart, kein `Planner`** — damit waren auch keine Umlenkungen noetig; `NIGHTREIGN_SETTINGS_ORG`/`_APP` standen trotzdem auf `DankYeeterT-189` / `NightreignHelperT-189`. Kein Schreibzugriff. |
| "unterscheidbar" | `abs(grenzbeitrag) > 1e-9`. Kein Sicherheitsabstand noetig: die Werte liegen exakt auf 0 oder ueber 0,01 |
| Lesart | **Kopien**, nicht Relikt-Arten und nicht Effekt-Ids |
| Skripte | `…/scratchpad/T-189/explore.py`, `measure_options.py`, `measure2.py` … `measure6.py` |
| gemessen gegen | Commit `b8f71a8`, Branch `docs/audit-and-advisor-design`, 2026-09-12 |

**Scratchpad-Hinweis (Rahmen).** Die Skripte liegen im Temp-Verzeichnis und
ueberleben die Sitzung nicht. Wird eine der Optionen gebaut, sollte
`measure6.py` (Option B je Nightfarer und je Stufe) als versioniertes
Messskript unter `scripts/` wieder entstehen — er ist der Nachweis, dass die
Stufe die Rangfolge nicht bewegt.

## Die Zahlen

**Unterscheidbare Kopien von 210, je Grundlage** (alle gemessen, keine
Schaetzung ausser der markierten):

| Grundlage | unterscheidbar | verschiedene Werte | groesste Gleichstandsgruppe |
|---|---|---|---|
| **A** — Mittel der fuenf Angriffsmultiplikatoren (heute gebaut) | **26** | 8 | **184** |
| **B** — Startarmatur des Nightfarers als feste Bezugswaffe | **51** | 17 | 159 |
| **C** — offensive Attributspunkte als eigene Richtung | **53** | 8 | 157 |
| **D** — Erwartungswert ueber 32 Waffentypen | **81** | nicht gemessen | nicht gemessen |
| *zum Vergleich:* `min_damage_taken`, unveraendert | 37 | 10 | 173 |

**Ueberschneidungen.** A und B teilen nur **11** Kopien: 15 sind A-eigen
(Element-Multiplikatoren, die ein physisches Greatsword nicht nutzt), 40
B-eigen. `A oder C` = **75**. `A oder C oder min_damage_taken` = **104**.

**Die Obergrenze, und sie ist die wichtigste Zahl des Berichts.** Jede hier
gepruefte Grundlage vereinigt, beide Richtungen zusammen: **111 von 210**.
**99 Kopien** dieses Bestands bewegen unter *keiner* Option irgendetwas. Ein
grosser Teil der 184 Nullen ist also keine Schwaeche der Rechnung, sondern
eine Eigenschaft der Sammlung — aber eben nur ein Teil: fuer die
uebrigen 85 ist die Null eine Aussage ueber die Rechnung, und die Oberflaeche
unterscheidet beides heute nicht.

**Option B, je Nightfarer** (Stufe 1, Startarmatur in Slot 1):

| Wylder | Guardian | Ironeye | Duchess | Raider | Revenant | Executor | Scholar | Undertaker | Recluse |
|---|---|---|---|---|---|---|---|---|---|
| 51 | 50 | 47 | 52 | 39 | 56 | 51 | 50 | 51 | **ungemessen** |

**Der freie Parameter von B ist gemessen keiner.** Stufe 1 bis 4, alle neun
messbaren Nightfarer: gleiche Anzahl **und gleiche Reihenfolge**, erster
Unterschied `None`. Die Stufe bewegt die absolute Zahl, nicht den Rang.

**Laufzeit** (ein Pool von 210 Kandidaten): A **0,018 s**, B **0,023 s**, D
naiv **0,70 s** fuer 32 Pools — Faktor 39 gegen heute und ueber dem Budget aus
AD-018/AD-028. Eine sparsame D-Fassung waere billiger, ist aber **ungemessen**
und braeuchte einen Eingriff in die Fassade (AD-019).

## QA-226 — Antwort: die Armaturen-Buffs sollten fallen

- Ein **stapelbarer** Armaturen-Buff bewegt **10 von 210** Zahlen, aber
  **nicht die Reihenfolge** (erster Unterschied `None`). 13 solcher Ids liegen
  auf den 210 Kopien; alle 13 sind stapelbar.
- Ein **nicht stapelbarer** bewegt die Reihenfolge. Der Datensatz kennt **6**
  nicht stapelbare Effekte, die eine Angriffsrate bewegen; keiner liegt auf
  diesen Relikten, jeder ist auf **120 bis 141** Armaturen rollbar. Gemessen:
  `Improved Holy Attack Power` und `Physical Attack Up` (8850550) drehen die
  Reihenfolge **ab Rang 3**, `Improved Fire Attack Power` **ab Rang 4**,
  `Improved Magic` / `Improved Lightning` ab Rang 16.

**Damit ist AK-191 woertlich gelesen heute nicht erfuellt** — sobald die
gefuehrten Armaturen etwas gerollt haben, koennen zwei Laeufe verschiedene
Rangfolgen ergeben. Der T-188-Test sieht das nicht, weil seine beiden
Armaturen keine Rollen tragen; der `developer` hat diese Luecke selbst
gemeldet.

**Empfehlung: fallen lassen, unter jeder der vier Optionen** — inklusive
Option B, wo die Startarmatur dann **ohne ihre Rollen** in die Rechnung geht.
Preis: die Waffenpassiven verschwinden aus der Beraterrechnung, der Berater
entfernt sich weiter vom Statblatt (D-2). Gewinn: `armament_effect_ids` kann
aus `GoalContext` und `AdvisorRequest` verschwinden, womit P-1 aus T-188
(Cache-Schluessel verfehlt sich beim Waffenwechsel) ueberhaupt erst behebbar
wird.

## Empfehlung — eine Empfehlung, keine Entscheidung

**Option B** (Startarmatur des Nightfarers als feste Bezugswaffe), weil:

1. "fest zwischen Runden" bei B eine **Eigenschaft des Datensatzes** ist
   (`hero["starting_weapon"]`), bei C und D dagegen eine Annahme;
2. sie die unterscheidbaren Kopien verdoppelt (26 → 51) und als einzige
   liefert, was A17 woertlich verspricht: Attribute bewegen die Zahl;
3. ihr einziger freier Parameter — die Stufe — gemessen ohne Wirkung auf die
   Rangfolge ist;
4. sie D-1 aus T-188 aufloest (der Waffenzweig ist dann kein toter Code mehr)
   und A16 denselben Zweig ohnehin brauchen wird.

**Was dagegen spricht, und der App Designer kann es anders sehen:** B holt die
Waffe zurueck, die der Nutzerentscheid hinauswerfen wollte. Wer den Satz
streng liest, waehlt **A + C** — 75 von 210 unterscheidbar, keine Waffe in der
Rechnung, dafuer bleiben die 184 Nullen in der Schadensspalte stehen.

## Was die Recherchen beitragen (R-004, R-005, R-006)

Alle drei sind gelesen und in AD-032 eingearbeitet, statt sie zu wiederholen.

- **R-005** (multiplikativ, hoch belegt) ist **kein** Einwand gegen Option A:
  `_attack_multiplier_mean` mittelt nicht gestapelte Effekte — die stapelt
  `model.compute` bereits multiplikativ —, sondern die fuenf **Schadensarten**.
  Dieselbe Bauform wie `EVEN_WEIGHTING`, dieselbe Antwort wie bei OF-3.
- **R-004** (globaler Faktor ~0,60) **stuetzt** Option B: ein konstanter
  Faktor kuerzt sich aus jeder Rangfolge heraus. Aber der Guardian-Versatz
  von ~3 % ist nicht konstant, und B rankt je Nightfarer gegen eine andere
  Waffe — **B-Zahlen zweier Helden sind nicht vergleichbar.** Unschaedlich,
  solange die Oberflaeche nie zwei Helden nebeneinanderstellt; heute tut sie
  das nicht.
- **R-006** (heldengebundene Waffenklassen-Effekte) trifft Option B direkt und
  spricht eher **fuer** sie: der Claws-Malus gilt fuer *fremde* Traeger und
  tritt unter B nie ein, weil jeder Held gegen seine eigene Startarmatur
  rankt — **unter Option D dagegen fuer sieben von acht Helden**, mit einer
  Zahl, die R-006 als unbelegt fuehrt. Ein etwaiger Raider-Bonus laege genau
  auf der Waffenklasse seiner Startarmatur, also auf Bs Anker, und waere dort
  sichtbar statt wirkungslos.

## Befunde — der Auftrag gegen den Bestand (Pflicht aus dem Auftrag)

**B-1 — Der Datenabzug im System kann keine Katalysatoren bewerten, und das
trifft Option B bei Recluse.** `weapons.rate` wirft fuer `wep_type` 57/61
`KeyError`: *"this dataset's reinforce table carries no 'catalyst_scaling' …
built by an extractor older than EXTRACT_VERSION 9"*. Recluse startet mit
`Recluse's Staff` (57). **Option B ist fuer Recluse ungemessen und wuerde auf
diesem Abzug abstuerzen.** Die Schaetzung "40 bis 55, wie die uebrigen" ist
eine Schaetzung. `CLAUDE.md` nennt fuer den **Testabzug** `EXTRACT_VERSION`
11 — der Abzug im echten `%LOCALAPPDATA%` ist aelter. Ob das nur meine
Messumgebung betrifft oder auch den Nutzer beim naechsten Start (das Programm
baut den Abzug bei zu niedriger Version neu), habe ich **nicht** geprueft;
ohne Programmstart ist das nicht zu belegen. **Vor einem Bau von Option B
muss Recluse auf einem Abzug ≥ 9 nachgemessen werden.**

**B-2 — Ein Kommentar in `nrplanner/weaponslots.py` wird vom Datensatz
widerlegt.** `rollable_effects` sagt: *"A base armament with an empty pool --
Unarmed, the Nightfarers' starting weapons -- has no lower sibling and must
stay empty."* Gemessen hat **jede** der zehn Startarmaturen einen gefuellten
Pool (49 bis 55 Eintraege; Wylder's Greatsword 54). Die Startarmatur kann
also sehr wohl rollen. Fuer Option B ist das die Stelle, an der ausdruecklich
stehen muss: **ohne Rollen**. Fuer den Bestand ist es ein Kommentar, der einen
Leser in die Irre fuehrt. Kein Nummernvorschlag — Befund-Ids vergibt der
Director.

**B-3 — `docs/state.md` ist bei A17 seit `43fd992` ueberholt.** Dort steht:
*"A17 | Ranking ohne Bezugswaffe | halb — nur der alte Ausweichzweig
(`goals.py:192-208`); die Voreinstellung rankt weiter mit Waffe."* Beides
stimmt nicht mehr: die Voreinstellung rankt seit T-188 **ohne** Waffe, und der
Zweig steht heute in `goals.py:214-230`, nicht 192-208.

**B-4 — Praezisierung zur "59 von 210" aus dem Auftrag, kein Widerspruch.**
Die Zahl ist exakt reproduziert — aber mit `Inseparable Sword` (id 2090000),
der ersten Waffe mit `wep_type` 5 im Datensatz, **nicht** mit Wylders eigener
Startarmatur. Mit `Wylder's Greatsword` ergibt dieselbe Messung **51**. Wer
"59" als Obergrenze fuer Option B liest, liest sie zu hoch.

**B-5 — Der Arbeitsbaum hat sich waehrend meines Laufs mehrfach geaendert.**
Bei Beginn sauber, HEAD `b8f71a8`. Waehrenddessen erschien unversioniert
`tests/test_exception_text_is_english.py` und war am Ende committet; HEAD
steht jetzt auf `e23f51f`, drei Commits von T-190 weiter (QA-211). **Alle
meine Zahlen sind gegen `b8f71a8` gemessen** — die drei Commits beruehren
`app.py`, `firstrun.py`, `datasource.py` und Fehlertexte, keines der Module
meines Messwegs. Dauerhaft unversioniert bleibt `klon/` **im
Projektwurzelverzeichnis** (nicht im Scratchpad), von mir nicht angefasst.
Das ist meldenswert: jeder Waechtertest, der von der Repo-Wurzel aus
`os.walk`/`rglob`/`glob` faehrt, liest dort jede Fundstelle ein zweites Mal —
aus einer Kopie, die kein Lauf reparieren kann.

## Was der `developer` ausdruecklich **nicht** tun soll

1. **Keine der vier Optionen bauen, bevor der App Designer gewaehlt hat.**
   AK-190, AK-192 und AK-193 beschreiben sonst eine Zahl, die gleich wieder
   wechselt — das ist der Grund, aus dem T-188 den `architect` verlangt hat.
2. **`_attack_multiplier_mean` nicht "reparieren"**, indem Attributspunkte
   hineinaddiert werden. Das waere der erfundene Umrechnungskurs, den AD-023
   und OF-13 verbieten.
3. **Den Waffenzweig in `_max_damage` nicht loeschen** (D-1). Option B und A16
   brauchen ihn.
4. **Keine Zahl aus diesem Bericht als Testschranke setzen.** 26, 51, 53, 81
   sind Messwerte an *einem* Spielstand und *einer* Datenversion; eine
   Schranke braucht ihren eigenen Sicherheitsabstand (L-001).
5. **`docs/state.md` nicht nebenbei korrigieren** (B-3) — das gehoert dem
   `director`.

## Offene Fragen

**An den App Designer, ueber den `director`:**

1. **Welche der vier Optionen?** A (so lassen, 26/210) · B (Startarmatur,
   51/210) · C (Attribute als eigene Richtung, mit A zusammen 75/210) ·
   D (Erwartungswert ueber die Waffentypen, 81/210). Empfehlung: B.
2. **Die 15 Element-Kopien**, die Option B nicht mehr rankt: Gewinn (das RNG
   ist korrekt ausgesperrt) oder Verlust (wer auf eine Element-Waffe hin
   plant, verliert die Information)?
3. **Sollen "bewegt diese Richtung nicht" und "konnte nicht gerechnet werden"
   unterschiedlich aussehen?** 99 von 210 Kopien bewegen unter keiner Option
   etwas — das ist eine Aussage, die das Programm treffen koennte, statt sie
   als +0,00 zu tarnen. Gehoert dem `ui-ux-designer`, sobald die Wahl steht.

**An den `director`:**

4. Nummern fuer B-1 bis B-4 (QA oder OF) — ich vergebe keine.
5. Wird Option B gewaehlt: **erst** Recluse auf einem Abzug mit
   `EXTRACT_VERSION` ≥ 9 nachmessen lassen, **dann** bauen.
6. QA-226 ist damit beantwortet (fallen lassen) — der Umbau ist aber Teil der
   gewaehlten Option und kein eigener Auftrag davor.

## Was ich nicht geprueft habe

- **Nichts an der Oberflaeche.** Kein Fenster geoeffnet, kein Programmstart.
  Wie die 184 Nullen im Picker und im Beraterstreifen *aussehen*, ist
  ungeprueft.
- **Deep-Relikte.** Der Auftrag nennt die 210 gewoehnlichen; die 102 Deep
  habe ich unter keiner Option gemessen.
- **Ob der Nutzerabzug beim naechsten Programmstart neu gebaut wird** (B-1).
- **Die sparsame Fassung von Option D** — nur die naive ist gemessen.
- **Keine Testsuite gelaufen.** Ich habe keinen Code geaendert; ein Volllauf
  haette nichts belegt. Die Messskripte importieren `nrplanner` und `tests`
  aus dem Arbeitsbaum, waehrend T-190 parallel an `app.py`, `firstrun.py` und
  `datasource.py` arbeitet — keines dieser drei Module wird von meinem
  Messweg importiert, `advisorbar.py` habe ich nur gelesen.
