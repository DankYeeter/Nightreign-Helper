# T-085 — architect

```
STATUS: erledigt
AUFTRAG: T-085 — Was `not_counted` bedeutet, wenn die Schranke eine Waffe ist
GELESEN: docs/tasks/T-085.md · GOAL.md · docs/state.md · ARCHITECTURE.md
  (AD-003, AD-004, AD-010, AD-015, AD-025, Nachtrag VI, Präzisierungen) ·
  docs/berichte/T-084-ui-ux-designer.md · docs/berichte/T-067-developer.md
  (D-4 bis D-7) · qa/findings.md (QA-104, QA-106, QA-108) · gegen `fd9f2bc`:
  nrplanner/model.py, nrplanner/advisor/{explain,evaluate,types,run,search,
  candidates,goals}.py, nrplanner/app.py, nrplanner/inventory.py ·
  UI_SPEC.md §4.9a/4.9b, AK-142, AK-143, AK-167 bis AK-169, T-084-Nachtrag §6 ·
  tests/test_advisor_explain.py, tests/advisor_cases.py
GEÄNDERT: ARCHITECTURE.md (Nachtrag VII angehängt, 442 Zeilen; nichts
  gelöscht) · docs/berichte/T-085-architect.md (diese Datei). Kein Git-Zustand
  verändert — keine Commit-Rechte, nichts gestaged.
ANNAHMEN: (1) `EVEN_WEIGHTING` und Stufe 15 sind für die Klassenfrage
  gleichgültig — die Waffenschranke hängt weder an Gewichtung noch an Stufe;
  nicht durchgemessen, aber `is_conditional` liest keines von beiden.
  (2) Die 88 Slotformen der vollen Läufe sind aus den 74 Gefässen des
  Datensatzes abgeleitet (mit und ohne Deep, entdoppelt), nicht aus den
  Gefässen, die dieser Spieler wirklich besitzt.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

---

## 1. Die Entscheidung

**AD-026 (`ARCHITECTURE.md`, Nachtrag VII): eine unerfüllte Waffentyp-Schranke
ist eine Bedingung, in die der Spieler sich versetzen kann.** Der Effekt bleibt
in `CONDITIONAL_FIELDS`, bleibt in `Build.situational`, behält seinen Schalter
und zählt in `not_counted` und damit in Statuszeile 4.9b. **Am Rechenkern
ändert sich nichts. Geändert wird der Docstring von `explain.not_counted`** —
er ist die Stelle, die etwas Falsches behauptet, nicht die Rechnung.

D-3 („`not_counted` behält AD-010, konditionale Effekte") bleibt damit gültig
und bekommt seine Begründung nachgeliefert.

### Warum

1. **Der Bestand hat die Frage schon in Nutzersprache beantwortet.** Der leere
   Zustand des Planers sagt heute: *„Effects that only work below a HP
   threshold, **with a particular armament**, or on a trigger would be listed
   here."* Die Armatur steht dort als eine von drei Bedingungen, unter
   `Conditional & situational`. Der `Build planner`-Tab ist der, den der App
   Designer ausdrücklich für gut befunden hat.
2. **Die Grenze verläuft an der Herstellbarkeit, nicht an der Ausrüstung.**
   Ein Schalter beantwortet „was wäre das wert, wenn die Bedingung hielte".
   Unter 85 % HP kann der Spieler sich bringen; eine Axt kann er anlegen;
   ein anderer Nightfarer kann er nicht werden — und genau dort setzt
   `compute_qualitative` schon heute keinen Schalter (`effecttext.works_for`).
3. **Der Docstring ist ein ausgedehnter Randbedingungssatz, kein Irrtum.** Er
   beruft sich auf QA-104, und QA-104 ist wahr — über den *klassen*gebundenen
   Angriffsbuff (`magicSubCategoryChange` 130/113/118). **Gemessen: 8 solche
   Effekte im Datensatz, 0 davon konditional**, keiner erreicht je
   `Build.situational` (sie landen in `Build.class_rates`). Angewendet wurde
   der Satz auf die *typ*gebundene Schranke. `ARCHITECTURE.md` hatte es an
   seiner eigenen Stelle richtig: Präzisierung AD-004, Punkt 6 sagt
   „Waffen**klasse**". Der Docstring hat Klasse zu Typ verallgemeinert.

### Verworfene Alternative — und warum sie teurer ist als sie aussieht

**Option E: die drei Waffenfelder aus `CONDITIONAL_FIELDS` nehmen.** Das ist
der naheliegende Griff und der Grund, warum die Frage überhaupt offen war.

**Gemessen, nicht vermutet:** dann bekommen **17 von 309 besessenen Kopien
eine Zahl, die der Spieler nicht hat.** `Grand Tranquil Scene` zeigt +9 % auf
allen fünf Angriffsraten, `Deep Polished Tranquil Scene` +20 % — für eine
Waffe, die nicht auf dem Raster liegt. Die stummen Zeilen fallen von 426 auf
409 (Umgebung A) und von 434 auf 417 (B), weil diese 17 nicht mehr stumm
sind, sondern falsch beziffert. Das ist wörtlich der Fehler, gegen den der
Kommentar an `CONDITIONAL_FIELDS` geschrieben ist („a real +12 % Physical
Attack was displayed as +2.5 %"), und ein A7-Bruch.

**Option E' (sauber: dritte Ablage, gated, keine Summe, kein Schalter)** wäre
vertretbar, kostet aber `compute_qualitative`, `Situational`, ein drittes Feld
auf `Build` und 46 Schalter im Planer — ein Umbau des Rechenkerns nach S9 und
eine Änderung an einem Tab, der nicht zur Debatte steht. Als Rückweg benannt,
nicht als Auftrag.

---

## 2. Die Zahlen, beide Umgebungen, mit Rezept

**Grundgesamtheiten sind erschöpfend gezählt, es sind keine Stichproben** —
kein Stichprobenfehler, kein Sicherheitsabstand, weil keine Zahl als Schranke
dient. Die Unsicherheit liegt in der Grundgesamtheit: ein Spielstand, ein
Datenabzug, zwei von zehn Nightfarern. Die Entscheidung ruht auf einem
**Vorzeichen** (17 > 0), nicht auf einem Betrag.

- **Datenabzug:** `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`,
  `data_version` 10350000, `extract_version` 11, 2076 Effekte. Nur gelesen.
- **Codestand:** `fd9f2bc`. Gegengeprüft: `git diff --stat fd9f2bc --
  nrplanner/` nennt allein `nrplanner/app.py` (T-083). `model.py`,
  `inventory.py` und das ganze `advisor/`-Paket sind byteweise `fd9f2bc`, und
  nur diese importieren die Messungen. Kein Fenster gestartet (NH-002).
- **Umgebung A:** Wylder, `Wylder's Greatsword` (3750000, `wep_type` 5),
  Stufe 15, `max_damage`, `EVEN_WEIGHTING`.
- **Umgebung B:** Ironeye, `Ironeye's Bow` (41750000, `wep_type` 51),
  Stufe 15, sonst gleich — anderer Nightfarer **und** andere Waffengattung.
- Skripte im Scratchpad (`measure.py`, `gattung.py`, `vessels.py`,
  `reading_e.py`, `reading_e_totals.py`), auftragsgemäss nicht im Repo; das
  Rezept steht in Prosa in `ARCHITECTURE.md`, Nachtrag VII §0.

### 2a. Reproduktion der Fremdmessung

Umgebung A gibt die T-084-Tabelle **Zeichen für Zeichen** wieder:
150 / 0 / 170 / 13 / 93 / 0 gebaut, 150 / 0 / 124 / 58 / 94 / 0 nach AK-167,
Summe 426 in beiden. Die Zahlen des `ui-ux-designer` stehen.

### 2b. Die zweite Umgebung

| Füllung | A gebaut | A AK-167 | **B gebaut** | **B AK-167** |
|---|---|---|---|---|
| (a) anderer Nightfarer | 150 | 150 | **159** | **159** |
| (a2) anderswo gezählt | 0 | 0 | **0** | **0** |
| (b) Bedingung | 170 | 124 | **174** | **127** |
| (c) Armaturen | 13 | 58 | **0** | **47** |
| (d) Rest | 93 | 94 | **101** | **101** |
| (e) nicht im Datensatz | 0 | 0 | **0** | **0** |
| Summe | 426 | 426 | **434** | **434** |

Das Verhältnis ist stabil: A verschiebt 46 Zeilen von (b) nach (c), B
verschiebt 47. Ein Nightfarer- oder Waffenwechsel ändert es nicht. **Ein
Unterschied ist erklärungsbedürftig und erklärt:** die gebaute Spalte hat in
A dreizehn (c)-Zeilen und in B **null**. Das sind die Effekte mit einer
**erfüllten** Greatsword-Schranke, die trotzdem keine Zahl bewegen; auf einer
besessenen Kopie gibt es kein Bogen-Gegenstück dazu. AK-168 ist damit in A
wirksam und in B leer — beides erwartet.

### 2c. Die Zahl, die der Nutzer wirklich liest — und das ist die Überraschung

Die 46 sind eine Eigenschaft der **Kandidatenmenge**, nicht des Vorschlags.
Über 176 volle Läufe je Umgebung (2 Zielrichtungen × 88 Slotformen aus den
74 Gefässen, mit und ohne Deep, entdoppelt), gerechnet mit `advisor.run.run`:

| | A (Wylder / Greatsword) | B (Ironeye / Bow) |
|---|---|---|
| `not_counted`-Einträge zusammen | 565 | 473 |
| Mittel je Lauf | 3,21 | 2,69 |
| Schlechtester Lauf | 9 | 8 |
| davon waffengeschrankt | **1** | **1** |

**Die Entscheidung bewegt die Statuszeile 4.9b in 175 von 176 Läufen um
null.** Strukturell, nicht zufällig: die Beam-Suche rankt nach der Punktzahl,
ein Effekt in keiner Summe trägt genau 0 bei, also wählt sie solche Relikte
fast nie. Sichtbar wird die Klasse im **Picker**, und dort entscheidet nicht
`not_counted`, sondern die Füllung (AK-167/168). Der Auftrag geht von „an der
Antwort hängt eine Zahl in der Statuszeile" aus; gemessen hängt daran etwa
1 von 500. Das gehört zum Ergebnis (OF-24).

### 2d. Punkt 1.3 — die Suche nach der zweiten Gattung

Zwei unabhängige Suchmasken, wie die Abnahme verlangt:

- **Maske 1, strukturell:** alle drei Quellen von `is_conditional` einzeln
  ausgezählt — `CONDITIONAL_FIELDS` (8 Felder), `CONDITIONAL_FIELD_VALUES`
  (`saveCategory` 9) und `timed_window` (`effectEndurance` > 0), über alle
  **2076** Effekte. Treffer: **10 Gattungen**.
- **Maske 2, verhaltensbezogen:** jeden `not_counted`-Eintrag beider
  Umgebungen danach klassifiziert, **ob ein Armaturenwechsel ihn je erfüllen
  könnte** — Wert im Waffentyp-Vorrat des Spiels ja/nein,
  `satisfied_by_weapon` überhaupt zuständig ja/nein. Treffer: **3 Familien**
  innerhalb der Waffenschranke.

| Gattung | Feld | Effekte | Urteil |
|---|---|---|---|
| Zustand des Spielers | `invocationConditionsStateChange1/2` | 202 / 6 | Bedingung |
| Waffentyp | `triggerOnWepType` | 144 | Bedingung — **diese AD** |
| Waffenzahl | `wepTypeTriggerCount` | 82 | Bedingung, **nie prüfbar** |
| Waffentyp | `wepTypeTrigger` | 30 | wie oben |
| Lebenspunkte | `conditionHp`, `conditionHpRate` | 26 / 8 | Bedingung |
| Zeitfenster | `effectEndurance` > 0 | 20 | Bedingung, N Sekunden |
| Gegnerzustand | `enemyStateInfoTrigger` | 9 | Bedingung |
| Zähler | `saveCategory` = 9 | 8 | **keine Bedingung, ein Zähler** |

**Ergebnis: keine Gattung muss aus `situational` heraus.** Zwei sind trotzdem
zu nennen, weil sie nicht dasselbe sind wie „ich trage die Waffe nicht":

- **`wepTypeTriggerCount` — 28 der 46 bzw. 47 Einträge, also die Mehrheit.**
  Steht **absichtlich nicht** in `WEAPON_TYPE_GATES`: die Schranke will
  mehrere Armaturen desselben Typs, und `satisfied_by_weapon` kann das nicht
  beantworten. Sie bleibt daher konditional, **auch wenn der Spieler die
  Waffen wirklich trägt**. Unter der Entscheidung richtig — der Spieler kann
  die Bedingung herstellen, das Programm kann es nur nicht sehen, und der
  Schalter ist die ehrliche Antwort. Aber es ist **kein** Fall, den „wechsle
  die Waffe" löst; wer die 46 pauschal so liest, liest 28 davon falsch.
- **Der Zähler (`saveCategory` 9, 8 Effekte)** ist keine Ja/Nein-Bedingung,
  sondern eine Menge. Er trägt sein eigenes Kennzeichen
  (`Situational.accumulates`, `count`), `live` heisst dort „count > 0". Schon
  getrennt, bleibt getrennt; `not_counted` zählt ihn zu Recht mit.

**Und eine dritte Familie, latent:** **72 der 144** `triggerOnWepType`-Effekte
tragen einen Wert, der **kein Waffentyp ist** (256 auf 70 Effekten, 512 auf
2). Kein Armaturenwechsel erfüllt sie je. Auf diesem Spielstand erreichen sie
`not_counted` **nicht** (0 Einträge in beiden Umgebungen — keine besessene
Kopie trägt einen). Kein Fall dieser Entscheidung, aber eine Falle für die
Anzeige: `GATE_FIELDS` beschriftet sie mit *„only with a matching weapon
type"*, und einen passenden Typ gibt es nicht. → **Befund, OF-23.**

---

## 3. Fixrichtung an den `developer`, mit Regressionstest

**Zu tun, genau eines:** den Abschnitt „Scope" im Docstring von
`explain.not_counted` ersetzen. Er muss sagen, was drin ist — **jede**
Bedingung, in die der Spieler sich versetzen kann, einschliesslich einer
Armatur, die er nicht oder nicht oft genug führt — und was nicht: ein Effekt
eines anderen Nightfarers, und ein **klassen**gebundener Angriffsbuff ohne
Referenzarmatur (QA-104, 8 Effekte, keiner konditional). Der QA-104-Verweis
bleibt stehen, aber als Beleg für die **Ausnahme**.

**Ausdrücklich nicht zu tun:** keine Änderung an `CONDITIONAL_FIELDS`,
`WEAPON_TYPE_GATES`, `is_conditional`, `compute_qualitative`, `Situational`,
`not_counted` selbst oder an einer Zahl. Kein Anfassen von `UI_SPEC.md` oder
4.9b. QA-185 nicht mitnehmen. `wepTypeTriggerCount` nicht auswertbar machen.

**Regressionstest — zwei Fälle gegen eine Grenze**, in
`tests/test_advisor_explain.py`. Der Baustein steht schon da:
`tests/advisor_cases.py::an_armament_type_gate` liefert
`(effect id, Armatur des verlangten Typs, Armatur eines anderen)`.

- **Fall 1, Schranke unerfüllt:** nur `other` auf dem Raster. Erwartet: der
  Effektname **ist** in `explain.not_counted(built)`, `len(...) == 1`.
- **Fall 2, dieselbe Schranke erfüllt:** `carrier` zusätzlich auf dem Raster.
  Erwartet: Name **nicht** darin, `len(...) == 0`.

Beide Erwartungen stehen **als Literal im Fall**, nicht gerechnet aus
`built.situational`, `CONDITIONAL_FIELDS` oder `_ARMAMENT_GATES` — sonst
bleibt der Fall grün, gleichgültig was die bewachte Stelle sagt (L-008 b).

**Rot-vorher, der Gegenbau:** in `nrplanner/model.py` `CONDITIONAL_FIELDS` um
`"triggerOnWepType"`, `"wepTypeTrigger"`, `"wepTypeTriggerCount"`
erleichtern — das ist genau Option E. **Fall 1 wird rot** (die Liste ist
leer). Zweiter, unabhängiger Gegenbau: in `explain.not_counted` einen Filter
einziehen, der Einträge mit einem der `_ARMAMENT_GATES` überspringt — auch
dann Fall 1 rot, Fall 2 grün. **Fall 2 wird rot**, wenn `satisfied_by_weapon`
die Grid-Menge nicht mehr durchsucht (`isinstance`-Zweig entfernt).

**Überlebt ein Gegenbau, ist das ein Befund und wird berichtet, nicht
nachgebessert** (L-008 c).

**Einschränkung, die dazugehört:** beide Fälle laufen im Standardlauf
(L-008 a), brauchen aber den echten Datensatz und werden auf einem Runner
ohne Spielinstallation übersprungen. Das ist **QA-106**, keine neue Lücke —
aber es heisst, dass diese Grenze auf einem fremden Rechner unbewacht ist.

---

## 4. AK-167 und AK-168 — nachgeprüft, nicht übernommen

Der `ui-ux-designer` sagt, seine Vorgabe funktioniere unter beiden Lesarten.
**Sie tut es — die Regel und ihre tragende Zahl. Ihre Partitionssumme tut es
nicht.** Reading E wurde dafür simuliert (`CONDITIONAL_FIELDS` im Speicher
erleichtert, alles neu gezählt):

| Füllung | A: Entscheidung K | A: E | B: K | B: E |
|---|---|---|---|---|
| (a) | 150 | 150 | 159 | 159 |
| (a2) | 0 | 0 | 0 | 0 |
| **(b) Bedingung** | **124** | **124** | **127** | **127** |
| (c) Armaturen | 58 | 41 | 47 | 30 |
| (d) Rest | 94 | 94 | 101 | 101 |
| (e) | 0 | 0 | 0 | 0 |
| **Summe** | **426** | **409** | **434** | **417** |

- **AK-167 (i) hält unter beiden Lesarten**, und (b) ergibt unter beiden
  **dieselbe** Zahl — 124 in A, 127 in B. Genau die Zahl, mit der er
  argumentiert, ist gegen die Lesart unempfindlich. Seine Behauptung ist
  bestätigt.
- **Die Reihenfolge ist unter der getroffenen Entscheidung tragend, nicht
  überflüssig.** Unter K überschneiden sich (b) und (c) auf 46 bzw. 47
  Zeilen, und erst die Voranstellung von (c) entscheidet sie. Unter E
  überschneiden sie sich fast nicht mehr. Die Regel arbeitet genau dort, wo
  AD-026 entscheidet.
- **AK-168 (ii) hält lesartunabhängig.** Der Test auf die *unerfüllte*
  Schranke entfernt die 13 falschen Zeilen aus A.
- **Was unter E nicht überlebt, ist die Summe:** 426 → 409, weil 17 Zeilen
  aufhören stumm zu sein und stattdessen eine falsche Zahl tragen. **AK-169**
  („die sechs Füllungen sind eine Partition, Rezept und Zahlen dabei") bliebe
  formal wahr, aber mit anderen Zahlen. Unter K bleibt AK-169 Wort für Wort
  und Zahl für Zahl gültig.

**Kein Auftragswechsel nötig.** Die Reihenfolge der beiden Aufträge bleibt,
wie der `director` sie gesetzt hat.

---

## 5. Die beiden Korrekturnotizen

**Vorher unabhängig geprüft** (`git grep -c "Korrekturnotiz" fd9f2bc --
ARCHITECTURE.md` → **kein Treffer**): die Beobachtung des `ui-ux-designer`,
dass beide Notizen fehlten, trifft zu. Beide sind jetzt nachgetragen, mit
Datum und Herkunft; **kein ursprünglicher Wortlaut wurde gelöscht**, beide
sind als ersetzt markiert.

- **AD-015:** Die Pflichtzeile `A curse on <relic> changes <field>, which
  this goal does not rank.` wandert aus `unknowns` in die Slotgruppe und
  verschmilzt mit der Zahlzeile desselben Fluchs zu
  `✦ {curse name}: {figure label} {amount} — this figure does not count it.`
  **Im Code ist das seit T-081 so** (`explain.unknowns` trägt sie nicht mehr
  und begründet es im eigenen Docstring); die Notiz holt `ARCHITECTURE.md`
  nach und ordnet nichts Neues an. Alles Tragende von AD-015 bleibt.
- **AD-003.5 (D-5):** Es gibt kein `top_n`. Die Beam-Breite W **ist** die
  Zahl der Endzustände. Nachgeprüft mit zwei Suchmasken gegen `fd9f2bc`
  (`top_n` und `top[_ ]?n|n_best|best_n` über `nrplanner/`): **genau ein
  Treffer**, `advisor/search.py:321`, und der erklärt genau diesen
  Sachverhalt. Die A5-Zusage aus AD-003 bleibt erfüllt — der Spieler sieht W
  Alternativen statt `top_n`.

---

## 6. Was mir aufgefallen ist und nicht in den Auftrag gehörte

**Befunde, ohne Nummer — die vergibt der `director`.**

1. **`GATE_FIELDS` verspricht eine Waffe, die es nicht gibt.** 72 Effekte
   (`triggerOnWepType` 256 auf 70, 512 auf 2) werden mit *„only with a
   matching weapon type"* beschriftet, obwohl kein Waffentyp des Spiels
   diesen Wert trägt. Fundstelle `nrplanner/model.py`, `GATE_FIELDS`. Latent
   auf diesem Spielstand (0 von 197 bzw. 201 Einträgen). A11-Frage, kein
   Rechenfehler. → OF-23.
2. **Die Grösse des T-084-Befundes ist eine andere als angenommen.** „46 von
   170" beschreibt die Kandidatenmenge; die Statuszeile bewegt sich um 1 von
   565 bzw. 1 von 473. Die Klasse war trotzdem zu entscheiden — der Docstring
   beschreibt die Menge falsch, und Füllung (c) im Picker betrifft jede der
   46 Zeilen. → OF-24.
3. **`UI_SPEC` T-084-Nachtrag §6 trägt eine Zahl, die zur eigenen Tabelle
   nicht mehr passt.** Dort steht „170 der 426 stummen Effekte sind
   konditional und stehen damit auch in der Liste 4.9b". Nach AK-167 sind es
   in der Füllungstabelle 124; in `not_counted` bleiben es die 170. Beides
   ist richtig, aber der Satz nennt nur eine der beiden Zahlen und liest sich
   wie eine Aussage über die Tabelle darüber. **`UI_SPEC.md` gehört dem
   `ui-ux-designer`** — gemeldet, nicht angefasst.
4. **AD-026 berührt QA-185.** Die Grenze zwischen `qualitative` und
   `situational` wird erst maschinell prüfbar, wenn beide Listen dieselbe
   Effekt-Id führen; heute muss `explain` über den **Namen** zurückschliessen
   (`_silent_effect` gleicht den Namen aus `line.text` gegen den Effektsatz
   ab). Die Entscheidung hängt nicht daran, ein späterer Wächter schon.
5. **`satisfied_by_weapon` könnte `wepTypeTriggerCount` grundsätzlich
   beantworten**, weil das Raster sechs Armaturen hält und man zählen könnte,
   wie viele den verlangten Typ tragen. Nicht getan: was die Zahl im Feld
   genau meint, geben die Spieldateien nicht her — 82 Effekte hängen daran,
   und A7 verbietet die Vermutung. Wieder interessant nach einer Ablesung im
   laufenden Spiel. In `ARCHITECTURE.md` unter „Bewusst nicht getan"
   eingetragen.

**Nicht ausgeführt:** die Suite. Der Auftrag verlangt es nicht, ich habe
keine Zeile Anwendungscode angefasst, und `tests/test_advisor_bar.py` sowie
`nrplanner/advisorbar.py` ändern sich gerade unter mir (T-083). Der Stand
1059 / 9 / 5 aus `docs/state.md` ist von mir **nicht** nachgeprüft.
