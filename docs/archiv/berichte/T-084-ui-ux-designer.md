# T-084 — ui-ux-designer (Modus Spec)

```
STATUS: erledigt
AUFTRAG: T-084 — Vier offene Wortlaute und eine Zaehlgrenze vor S10b/S10c
GELESEN: docs/tasks/T-084.md (mit den Zitaten aus GOAL.md A7/A12 und dem
         Stand-Auszug aus docs/state.md; beide tragen den Auftrag, GOAL.md
         und docs/state.md daher nicht erneut von vorn gelesen) ·
         UI_SPEC.md (Zeilen 95-270 §3.1-§5, 680-760 Picker, 1030-1045
         AK-47/AK-50, 1229-1343 Nachtrag QA-116/AK-63, 1509-1630 AK-67,
         3380-3500 §5/§6, 3600-3740 AK-133 bis AK-150 und die drei offenen
         Fragen, 3820-4278 T-080-Abschnitt vollstaendig) ·
         ARCHITECTURE.md (Nachtrag VI: AD-025 mit den zwei Klassen und der
         Anwendungstabelle, Praezisierung AD-004/D2, Pruefpunkte 29-34, die
         Risikotabelle bei 3390-3400, OF-19 bis OF-22; nur gelesen) ·
         nrplanner/advisor/types.py · explain.py · goals.py · evaluate.py ·
         run.py (Docstring zu budget_note) · nrplanner/model.py
         (GATE_FIELDS, satisfied_by_weapon, is_conditional,
         compute_qualitative, compute) · qa/findings.md QA-104/QA-108 ·
         docs/berichte/T-080-ui-ux-designer.md · scripts/measure_advisor_picker.py
         (als Messvorlage) · CLAUDE.md ·
         .claude/agent-memory/ui-ux-designer/ (beide Dateien)
GEAENDERT: UI_SPEC.md — ein neuer ##-Abschnitt am Ende (AK-162 bis AK-176)
           und vier kleine Aenderungen im Bestand: die Zelle 4.7 der
           Zustandstabelle, §5.1 ("der heutige `Suggest`-Knopf"), F4 der
           T-004-Fragen (Zusatz), offene Frage 3 des T-078-Abschnitts (als
           beantwortet markiert). ·
           docs/berichte/T-084-ui-ux-designer.md (diese Datei) ·
           .claude/agent-memory/ui-ux-designer/feedback_headless_verification.md
           (ein Absatz angehaengt; liegt ausserhalb der Git-Verfolgung).
           Kein Anwendungscode, kein Skript im Repo, kein Bildnachweis, kein
           Fenster gestartet, Git ausschliesslich lesend (git status,
           git diff --stat). Der Datenabzug wurde nur gelesen.
           nrplanner/app.py und nrplanner/advisorbar.py sind im Arbeitsbaum
           geaendert bzw. neu — das ist T-083, nicht ich.
ANNAHMEN: (1) Alle Zahlen unten stammen aus **einer** Umgebung: Datenabzug
          dieser Maschine, Spielstand des App Designers (309 Kopien, 845
          Effektrollen), Wylder, Stufe 15, Wylder's Greatsword als Bezugs-
          und einzige gefuehrte Waffe, keine Bedingung erklaert, ein Relikt
          je Slotgruppe. Auf einem anderen Nightfarer oder mit einer anderen
          Waffengattung fallen (a) und (c) anders aus.
          (2) Ich habe angenommen, dass `SlotPool.rank_by` die Zielrichtung
          benennt, deren `Baseline`-Eintrag in Zeile 3b gehoert. Der Picker
          zeigt beide Zielrichtungen als Zahl (§3.3), aber nur eine ordnet.
          (3) Fuer 4.7 konnte ich **keine** Pixelbreite messen (Begruendung
          unten, Punkt 3). Die Zeichenzahlen sind ein Rangvergleich, keine
          Sichtbarkeitszusage.
NAECHSTER: director — zwei Entscheidungen (Befund 1 und Befund 2 unten)
           gehoeren ihm bzw. dem `architect`, danach developer (T-085/T-086)
BLOCKIERT DURCH: nichts
```

---

## 1. Punkt 1 — AK-63 und OF-19: die zweite Quelle (loest die Sperre fuer T-086)

**Entschieden.** AK-63 ist ersetzt durch **AK-162 bis AK-166**. Die Anzeige
liest ab jetzt beide Klassen aus AD-025, an vier benannten Orten.

**Was ich beim Lesen anders vorgefunden habe als der Auftrag beschreibt.** Der
T-052-Nachtrag war 2026-09-05 bereits einmal nachgezogen worden und nennt
schon zwei Felder — `Goal.scope` (Zeile 4) und `SlotPool.unknowns` (Zeile 3b).
Die Luecke, die OF-19 meint, ist deshalb **nicht** die, die der Auftrag
vermutet: sie liegt bei der **dritten** Haelfte. `Baseline.unknowns` und
`Baseline.weights_note` — die Laufbefunde der **Zielrichtung**, die
Pruefpunkt 32 eigens in den Pool getragen hat — haben in `UI_SPEC` bis heute
keinen Ort. Konkret: ohne Referenzwaffe liefert `goals._max_damage` den Satz
`No armament selected — ranked on attack multipliers only, without weapon
scaling.`, und eine spec-treue Umsetzung von AK-63 alter Fassung haette ihn
nirgends gezeichnet. Genau der A7-Rueckschritt aus der Risikozeile.

**Entscheidung, kurz:**

- **Zeile 4 / `Why` Punkt 4:** `Goal.scope`, unveraendert (AK-162).
- **Zeile 3b:** zuerst `Baseline.unknowns` der Zielrichtung aus
  `SlotPool.rank_by`, danach `SlotPool.unknowns`, ein umbrechender Block,
  entfaellt nur wenn beide leer sind (AK-163).
- **`Why` Punkt 4 beim Lauf:** `AdvisorResult.unknowns`, danach
  `AdvisorResult.weights_note`; die gleichlautenden `Baseline`-Felder werden
  **nicht** zusaetzlich gezeichnet (AK-164) — sonst steht der
  No-armament-Satz zweimal.
- **Keine Entdopplung durch die Anzeige** (AK-165): ein Satz in beiden
  Klassen ist ein Rechnungsfehler (Pruefpunkt 30) und wird sichtbar gemacht,
  nicht weggefiltert.

**Verworfene Alternative: `weights_note` mit in Zeile 3b.** Das war mein
erster Entwurf und ist falsch. Bei `Minimise damage taken` ist
`Baseline.weights_note` **nie** leer (`EVEN_WEIGHTING.note`), und er beginnt
mit denselben acht Woertern wie der zweite `MIN_DAMAGE_TAKEN.scope`-Satz in
Zeile 4: *"The game data gives no relative frequency of damage types, so …"*.
Zwei Zeilen untereinander mit identischem Anfang liest niemand als zwei
Aussagen. Deshalb: `weights_note` gehoert in den `Why`-Dialog, und erst wenn
OF-3 ein Bedienelement fuer die Gewichtung bringt, neben dieses Bedienelement
(AK-166).

**Nachpruefbar:** `advisor/goals.py` um einen sechsten `scope`-Satz erweitern
→ er steht ohne UI-Aenderung an beiden Orten. Einen Lauf ohne Referenzwaffe
herstellen → Zeile 3b traegt den No-armament-Satz. `SlotPool.unknowns` leeren
→ Zeile 3b bleibt trotzdem da, solange die Zielrichtung etwas zu sagen hat.

---

## 2. Punkt 5 — die Grenze (c)/(d): gezaehlt, und sie liegt nicht dort, wo der Auftrag sie vermutet

**Das Wichtigste zuerst: die Summe stimmt nicht.** Der Auftrag sagt, die
Grenze liege innerhalb der 106 Zeilen von (c)+(d) und die Summe 106 sei
invariant. Am Bestand gezaehlt ist das nicht so. Die Grenze liegt zwischen
**(b) und (c)**; (c)+(d) waechst von **106 auf 152**. Die Summe ueber **alle**
Fuellungen bleibt 426. Nach der Abnahmeregel des Auftrags heisst das: die
Regel war falsch angeschrieben, nicht die Zaehlung — und zwar in der
**Reihenfolge**, nicht im Test.

**Warum die 48 aus T-080 nie eine Messung war.** Meine eigene Tabelle in
T-080 §3 nennt 150 / 170 / 58 / 48. Die ersten drei sind gemessen, die vierte
ist ein Rest: 426 − 150 − 170 − 58. Diese Subtraktion setzt voraus, dass sich
die Toepfe nicht ueberschneiden. Sie tun es: **46 der 58 armaturgebundenen
Effekte stehen zugleich in den 170**, weil eine unerfuellte
Waffentyp-Schranke den Effekt nach `Build.situational` bringt und Fuellung (b)
ihn in der angeschriebenen Reihenfolge vor (c) abfaengt. Der echte Rest ist
94. Das ist mein Fehler aus T-080, und er steht so im Nachtrag.

**Die Zaehlung, beide Lesarten, eine Grundgesamtheit.**
Grundgesamtheit: **845** Effektrollen auf **309** besessenen Kopien, davon
**426** stumme Effektzeilen (Fluchzeilen nicht mitgezaehlt).

| Fuellung | (b) vor (c) — angeschrieben **und** gebaut | (c) vor (b) — diese Vorgabe |
|---|---|---|
| (a) anderer Nightfarer | 150 | 150 |
| (a2) anderswo gezaehlt | 0 (bei einem Relikt je Gruppe nicht herstellbar) | 0 |
| (b) Bedingung | 170 | 124 |
| (c) Armaturen | **13** | **58** |
| (d) Rest | 93 | 94 |
| (e) nicht im Datensatz | 0 | 0 |
| Summe | **426** | **426** |
| (c) + (d) | 106 | **152** |

**Der Weg, auf dem die Zahlen entstanden sind.** Kein Skript im Repo (der
Auftrag laesst mich nur `UI_SPEC.md` anfassen); es lag im Scratchpad und ist
in zwoelf Zeilen nachgebaut. Rezept, ausgefuehrt mit
`.venv\Scripts\python.exe` (die System-Python hat kein `Crypto` und kann
`nrplanner.inventory` nicht importieren):

1. `data = json.loads(paths.snapshot_path().read_text())`,
   `model.configure(data)`, `owned = inventory.load(data)`.
2. `ctx = types.GoalContext(data, hero=Wylder, level=15,
   reference=ReferenceArmament(Wylder's Greatsword, tier=1, slot_index=0),
   weighting=goals.DEFAULT_WEIGHTING, weapons_held=(dieselbe Waffe,))`.
3. Je besessener Kopie: `problem = SlotProblem(slots=(Slot(0, colour, deep),),
   held=())`, `base = evaluate(problem, (), ctx)`,
   `built = evaluate(problem, (cand,), ctx)`,
   `groups = explain.reasons(problem, (cand,), base, built, ctx,
   goals.GOALS["max_damage"])`.
4. Gezaehlt werden die `ReasonLine`, die weder `is_curse` noch
   `silence == CARRIES_A_FIGURE` sind, nach ihrer `silence`-Marke — das ist
   die linke Spalte.
5. Fuer die rechte Spalte wird zusaetzlich gefragt, ob der Effekt eines der
   vier Felder `triggerOnWepType`, `wepTypeTrigger`, `wepTypeTriggerCount`,
   `startSwordArtsId` traegt und `model.satisfied_by_weapon` dafuer **falsch**
   ist.

**Gerechnet wird mit `explain.reasons` selbst**, nicht mit einer Nachbildung
— sonst beschreiben die Zahlen meine Kopie statt das Programm.

**Die Regel, wie sie jetzt dasteht (AK-167, AK-168):**

- **(i) Pruefreihenfolge (a), (a2), (c), (b), (d), (e)** — (c) vor (b).
  Begruendung: fuer einen Effekt, dessen Schranke die Armatur ist, nennt
  *"it depends on the armaments you carry"* den Hebel; *"only applies under a
  condition"* schickt den Spieler auf die Suche. Dieselbe Logik, mit der (a)
  vor allem anderen steht. Und es ist die Lesart, die der Rest des Systems
  schon behauptet: der Docstring von `explain.not_counted` sagt unter Berufung
  auf QA-104 ausdruecklich, ein Effekt an einer nicht gefuehrten Armatur sei
  **nicht** in `not_counted`.
- **(ii) Der Test fragt nach der *unerfuellten* Schranke**, nicht nach dem
  Vorhandensein des Feldes. Die heutige Fassung fragt nur nach dem Feld und
  schreibt deshalb an einer Stelle des Bestands etwas Falsches: `HP
  Restoration upon Greatsword Attacks` bekommt bei gefuehrtem Greatsword *"it
  depends on the armaments you carry"*, obwohl der Spieler den Greatsword
  traegt. Mit (ii) faellt diese Zeile nach (d), wo sie hingehoert — sie ist
  stumm, weil sie beim Angriff ausloest, nicht wegen der Waffe.

**Verworfene Alternative: die gebaute Grenze (13) einfach anschreiben.** Sie
haette nichts gekostet und alles konsistent gelassen. Dagegen sprechen drei
Dinge: 46 Zeilen sagen dann das Unspezifische, obwohl das Programm das
Spezifische weiss (A11); QA-104 und der Docstring von `not_counted` behaupten
das Gegenteil; und die eine falsche Zeile aus (ii) bliebe stehen.

**Was ich ausdruecklich nicht angefasst habe:** 4.9b und `not_counted`
bleiben `Build.situational, live == False` (AK-142 unveraendert). Fuellung (c)
nimmt einen Effekt aus der **Zeile**, nicht aus der **Liste**. AK-154 gilt
fort, praezisiert.

---

## 3. Punkt 3 — die Statuszeile 4.7

**Entschieden: die Aussage bleibt, die Form aendert sich.** Neu und
verbindlich (AK-173):

> `Your build changed while this was working out — use Optimize again.`

**Zur ersten Frage des Auftrags (Breite): ich konnte sie nicht in Pixeln
beantworten, und ich sage das statt zu raten.** Die Advisor bar existiert
nicht (T-083 baut sie parallel), und eine Offscreen-Messung waere hier eine
Falle nach L-009: unter `QT_QPA_PLATFORM=offscreen` liefert diese Maschine
eine Ersatzschrift mit **exakt 12,0 px je Zeichen** ueber alle 17 gemessenen
Statustexte — `Segoe UI` wird substituiert, nicht geladen, und der Stil ist
`fusion` statt des Windows-Stils. Eine Zahl daraus haette wie eine Messung
ausgesehen und keine beschrieben. Belastbar ohne Fenster ist nur der
**Rangvergleich in Zeichen**: 4.7 neu hat **67** Zeichen und ist damit kuerzer
als 4.8 (74), 4.9 einklauselig (72), 4.11 (76), 4.10 (102) und 4.9 mit beiden
Klauseln (131). Sie traegt also **kein neues** Kuerzungsrisiko in die Leiste.
Ob sie ungekuerzt ankommt, entscheidet erst das laufende Fenster — deshalb
**AK-174**, das am Fenster gemessen wird und im Konfliktfall die Anordnung
nachgeben laesst, nicht den Satz.

**Zur zweiten Frage (Aufforderung, wo der Nutzer nichts falsch gemacht hat).**
Die Aufforderung selbst ist richtig — der Nutzer braucht den Weg zurueck, und
es ist nichts kaputt: der Berater schreibt ohne Zustimmung in keinen Slot
(§5.1). Falsch war die **Form**: `Optimize again.` ist unter allen vierzehn
Zustaenden der einzige nackte Imperativ. Das Hausmuster gibt den Weg nach vorn
als Angebot mit dem Namen des Bedienelements (4.8: `… — use Rescan save.`)
oder als Feststellung (4.13). Der Imperativ direkt hinter einer
Stoerungsmeldung liest sich als Zuweisung; dieselbe Auskunft im Hausmuster
liest sich als Angebot. Zusaetzlich **AK-175**: keine Statuszeile des Beraters
enthaelt `you changed`, `you must`, `please`, `try again` oder ein
Ausrufezeichen.

---

## 4. Punkt 4 — `AdvisorResult.budget_note`

**Entschieden: kein Wortlaut jetzt, Feld bleibt, Anzeige zeichnet fuer ein
leeres Feld nichts** (AK-170 bis AK-172). Ort fuer den Tag, an dem der Satz
existiert: `Why`-Dialog, eigene Zeile unter Punkt 4 — **nicht** die
Statuszeile.

**Begruendung in drei Schritten:**

1. Ein Budgetsatz sagt, dass **dieser** Lauf vorzeitig abgebrochen hat. Die
   Groesse dafuer setzt der `performance-tuner` in S11. Ein Text, der sie
   heute nennt, verspricht eine ungemessene Zahl — A12.
2. Der naheliegende zahlenfreie Ersatz (*"Not every combination was tried."*)
   ist wahr, aber in **jedem** Lauf wahr. Nach AD-025 ist das ein
   **Verfahrenssatz** und gehoert in die Registry; Pruefpunkt 31 wuerde ihn im
   Ergebnis rot faerben. Verloren geht dadurch nichts: AD-025.5 haelt
   `Best found` / `Top suggestions` als verbindliche Nutzersprache fest und
   verbietet `Optimal` / `Best possible`.
3. Deshalb **nicht** "gar nicht", sondern "noch nicht" — und damit **kein**
   Befund an den `architect`. AD-010 verlangt das Feld, `run.py` sagt in
   seinem Docstring bereits, dass es leer bleibt, bis der Satz existiert, und
   der Fall kommt in S11 wirklich. Streichen und in drei Wochen wieder
   einbauen kostet mehr als eine leere Zeichenkette.

**Warum nicht die Statuszeile:** sie kuerzt, und eine Aussage darueber, was
die Suche **nicht** versucht hat, waere die letzte im Satz und damit die
erste, die verschwindet — genau die Einschraenkung, um derentwillen der Satz
geschrieben wuerde.

---

## 5. Punkt 2 — `Suggest` im Fliesstext, je Stelle einzeln

| Zeile (vor meiner Aenderung) | Klasse | Was ich getan habe und warum |
|---|---|---|
| 463 — F4 der T-004-Fragen, "Alternativen waeren `Suggest a build`" | Historie **und** Verwechslungsgefahr | **Stehen gelassen, Zusatz angehaengt.** Die Frage meint den Namen des *Bereichs*, nicht den Knopf; ohne den Zusatz liest man sie als offene Knopffrage. |
| 541 — T-024 §1, "der Knopf heisst `Optimize` statt `Suggest`" | geltende Vorgabe, **richtig** | **Unveraendert.** Das ist die Umbenennung selbst; ohne das Wort `Suggest` verliert der Satz seinen Gegenstand. |
| 886 — §5.1, "`Optimize` ist der **heutige** `Suggest`-Knopf" | geltende Vorgabe, **falsch** | **Umgeschrieben** auf "der in der Fassung vom 01.09.2026 noch `Suggest` hiess", mit Datumsvermerk. "heutige" behauptet einen Knopf, den es nicht gibt. |
| 3161 — T-078 "Grundlage", `Suggestion` | Typname | **Unveraendert.** |
| 3693 — T-078 "nicht Teil dieser Vorgabe", `Suggestion` | Typname | **Unveraendert.** |
| 3723-3726 — offene Frage 3 des T-078-Abschnitts | offene Frage, **beantwortet** | **Als beantwortet markiert, nicht geloescht.** Der ueberholte Halbsatz durchgestrichen, die Antwort (GOAL F4, Commit `bafc3e1`) darunter. Die Begruendung von damals — der Preis einer spaeteren Umbenennung — war der Grund, die Frage vor S10 zu stellen, und bleibt lesbar. |

**AK-176** haelt das Ergebnis pruefbar: jede verbleibende `Suggest`-Fundstelle
in `UI_SPEC.md` ist entweder ein Typname oder ausdruecklich Verlauf.

---

## 6. Die neuen Akzeptanzkriterien, je eine Zeile

| ID | Kurz |
|---|---|
| **AK-162** | Zeile 4 / `Why` Punkt 4 zeigen `Goal.scope` wortgleich, vollstaendig, ohne verdrahteten Zusatzsatz. |
| **AK-163** | Zeile 3b traegt `Baseline.unknowns` der ordnenden Zielrichtung, danach `SlotPool.unknowns`; entfaellt nur, wenn beide leer sind. |
| **AK-164** | `Why` Punkt 4 zeigt `AdvisorResult.unknowns` und `weights_note`; die `Baseline`-Kopien derselben Saetze werden nicht zusaetzlich gezeichnet. |
| **AK-165** | Die Anzeige vergleicht, filtert, sortiert und entdoppelt die Vorbehaltssaetze nicht. |
| **AK-166** | `EVEN_WEIGHTING.note` kommt im Picker nicht vor, solange OF-3 kein Bedienelement bringt. |
| **AK-167** | Pruefreihenfolge der Fuellungen: (a), (a2), (c), (b), (d), (e). |
| **AK-168** | (c) trifft zu bei **unerfuellter** Armaturenschranke, nicht bei blossem Vorhandensein des Feldes. |
| **AK-169** | Die sechs Fuellungen sind eine **Partition** der stummen Zeilen; Rezept und Zahlen (150/0/124/58/94/0 = 426 von 845 Rollen auf 309 Kopien) stehen dabei. |
| **AK-170** | Leeres `budget_note` ⇒ nichts gezeichnet, kein Platzhalter. |
| **AK-171** | Nicht leeres `budget_note` ⇒ `Why`-Dialog, nie Statuszeile. |
| **AK-172** | In `budget_note` steht kein Satz, der in jedem Lauf zutraefe. |
| **AK-173** | 4.7 lautet `Your build changed while this was working out — use Optimize again.` |
| **AK-174** | 4.7 erreicht den Nutzer ungekuerzt; im Konfliktfall gibt die Leiste nach, nicht der Satz. Am Fenster zu messen, Umgebung nach L-009. |
| **AK-175** | Keine Statuszeile gibt dem Nutzer die Schuld (Wortliste). |
| **AK-176** | `Suggest` bezeichnet in `UI_SPEC.md` kein Bedienelement mehr. |

---

## 7. Befunde — was nicht in den Auftrag gehoerte, aber jemand wissen muss

**Befund 1 (architect, AD-010/QA-104): `explain.not_counted` haelt seinen
eigenen Docstring nicht ein.** Der Docstring sagt woertlich, ein Effekt, der
an einer nicht gefuehrten Armatur haengt, sei **nicht** in `not_counted`, und
beruft sich dafuer auf QA-104. Gemessen (Umgebung §0 des Nachtrags): **46 von
170** Eintraegen sind es doch, weil `not_counted` aus
`Build.situational, live == False` gebildet wird und `compute_qualitative`
waffengebundene Effekte genau dorthin schreibt. Entweder der Docstring oder
die Rechnung ist falsch. Meine Vorgabe funktioniert in **beiden** Faellen —
sie verschiebt nur die Zeile, nicht die Liste —, aber die Zahl in der
Statuszeilenklausel 4.9b haengt daran. Ich habe es **nicht** entschieden:
`not_counted` ist AD-010, nicht Anzeige.

**Befund 2 (director, Zuschnitt von T-085): §2 dieses Nachtrags aendert Code
ausserhalb der Oberflaeche.** AK-167 und AK-168 treffen
`nrplanner/advisor/explain.py` (`_silent_effect`, `_ARMAMENT_GATES`) — die
Reihenfolge der Fuellungen und ihr Test liegen im Rechenkern, nicht im
Fenster. Wer T-085 als reinen Oberflaechenauftrag zuschneidet, kann diese
beiden AK dort nicht erfuellen. Der Eingriff ist klein (Reihenfolge zweier
Zweige plus ein `satisfied_by_weapon`-Aufruf), aber er braucht Tests und
gehoert benannt.

**Befund 3 (architect, AD-015): die Korrekturnotiz aus `docs/state.md` steht
noch aus.** Ich habe `ARCHITECTURE.md` auftragsgemaess nicht angefasst; die
dort vermerkten Korrekturnotizen zu AD-003.5 und AD-015 ("die AD-015-Zeile
verschmilzt mit der Zahlzeile desselben Fluchs und wandert aus `unknowns` in
die Slotgruppe") sind im Bestand weiterhin nicht geschrieben — direkt geprueft
per Volltextsuche in `ARCHITECTURE.md` nach `AD-015` und nach `verschmolzen`
/ `Korrekturnotiz`.

**Befund 4 (director, keine Aufgabe fuer mich): die Zustandstabelle nennt
`AdvisorResult.unknowns` und `weights_note` nirgends.** Sie haben mit AK-164
jetzt einen Ort im `Why`-Dialog, aber keinen Zustand in 4.1-4.14 — das heisst,
ein Lauf **ohne** Referenzwaffe sieht in der Statuszeile aus wie ein normaler
Lauf. Ob das reicht oder ob 4.6 eine dritte Klausel braucht, ist eine
Produktfrage (`product-strategist`), keine Luecke, die ich in diesem Auftrag
schliessen durfte.

**Befund 5 (kein Handlungsbedarf, aber merken): die Zahl `426` ist eine
Wylder-Zahl.** Fuellung (a) mit 150 Faellen haengt vollstaendig am gewaehlten
Nightfarer, Fuellung (c) mit 58 vollstaendig am gefuehrten Waffentyp. Wer die
Tabelle aus §2 des Nachtrags auf einer anderen Figur oder mit einer anderen
Waffe nachrechnet, bekommt andere Zahlen — und das ist kein Fehler, sondern
die Messumgebung.

---

## 8. Offene Fragen an den App Designer

**Keine neuen.** Alle fuenf Punkte waren Sachfragen mit einer pruefbaren
Antwort, keine Geschmacksfragen. Die vier bestehenden Fragen (F-B, F-C, F-F,
F-G) habe ich auftragsgemaess nicht angefasst.

Eine **Vorwarnung**, falls Befund 1 zugunsten des Docstrings entschieden
wird: dann sinkt die Zahl in der Statuszeilenklausel 4.9b (`{n} effects were
left out …`) in der Umgebung §0 von 170 auf 124, und das ist eine Zahl, die
der App Designer auf dem Schirm sieht. Das ist keine Frage an ihn, sondern
eine Ankuendigung fuer den Fall.
