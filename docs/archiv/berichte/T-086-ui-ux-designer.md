# T-086 — ui-ux-designer (Modus Spec)

```
STATUS: erledigt
AUFTRAG: T-086 — Die Armaturenzeile sagt 28-mal etwas, das nicht stimmt
GELESEN: docs/tasks/T-086.md vollstaendig (mit dem A7/A11-Zitat aus GOAL.md,
         dem Stand-Auszug aus docs/state.md und dem Nachtrag des Directors
         vom 07.09.2026; beide tragen den Auftrag, GOAL.md und
         docs/state.md daher nicht erneut von vorn gelesen) ·
         docs/berichte/T-085-architect.md vollstaendig (AD-026, §2b, §2c,
         §2d, §4, §6) · docs/berichte/T-084-ui-ux-designer.md (§1-§3,
         Kontrakt) · UI_SPEC.md: T-080-Abschnitt §4 (die sechs Fuellungen),
         §5, §6, T-084-Abschnitt vollstaendig (§0, §2, AK-162 bis AK-176) ·
         gegen den Commit `fd9f2bc` gelesen: nrplanner/model.py
         (CONDITIONAL_FIELDS, WEAPON_TYPE_GATES, satisfied_by_weapon,
         is_conditional, GATE_FIELDS, ENGINE_FIELDS, accumulates),
         nrplanner/advisor/explain.py (_ARMAMENT_GATES, _silent_effect,
         reasons, not_counted, _count_line), advisor/evaluate.py,
         advisor/types.py, advisor/goals.py, scripts/measure_advisor_picker.py
         (als Messvorlage) · CLAUDE.md ·
         .claude/agent-memory/ui-ux-designer/ (Index und beide Dateien)
GEAENDERT: UI_SPEC.md — ein neuer ##-Abschnitt am Ende
           ("(ui-ux-designer, T-086) — 2026-09-07", AK-177 bis AK-181) und
           zwei Nachtragsklammern im Bestand: in §4 des T-080-Abschnitts
           (Reihenfolge und Klammerzahlen als ersetzt gekennzeichnet) und in
           §6 des T-080-Abschnitts (die 170/124/144-Zuordnung). **Nichts
           geloescht, nichts ueberschrieben.** ·
           docs/berichte/T-086-ui-ux-designer.md (diese Datei) ·
           .claude/agent-memory/ui-ux-designer/ (eine neue Datei, ein
           Indexeintrag; ausserhalb der Git-Verfolgung).
           Kein Anwendungscode, kein Skript im Repo, kein Fenster gestartet,
           kein Bildnachweis (NH-002). Git ausschliesslich lesend
           (git status, git log, git show, git diff --stat, git diff
           --quiet). Der Datenabzug und der Spielstand wurden nur gelesen.
           ARCHITECTURE.md nicht angefasst.
ANNAHMEN: (1) `advisorbar.py` und `app.py` weichen im Arbeitsbaum von
          `fd9f2bc` ab (T-083). Ich habe angenommen, dass das meine Messung
          nicht beruehrt, und es geprueft statt vermutet: model.py,
          inventory.py, effecttext.py und das ganze advisor/-Paket sind
          einzeln mit `git diff --quiet fd9f2bc -- <datei>` als byteweise
          identisch bestaetigt, und nur diese werden importiert.
          (2) Umgebung B ist mit der Startwaffe des Nightfarers gemessen
          (`Ironeye's Bow`), so wie der `architect` sie beschreibt. Ich habe
          seine Zahlen nicht uebernommen, sondern unabhaengig neu gerechnet;
          sie stimmen ueberein (434, 159/174/0/101 gebaut,
          159/127/47/101 nach AK-167/168).
          (3) Die Zuordnung Zeile -> Effekt laeuft ueber den Namensanfang
          `f"{name}: "`, wie `_silent_effect` den Text baut. Traegt eine
          Kopie zwei Effekte mit demselben Namen, kann die Zuordnung die
          erste treffen; die Fuellung waere dann dieselbe, weil sie am Namen
          nichts entscheidet. Nicht separat gemessen.
NAECHSTER: director — er vergibt die Nummern fuer die drei Befunde unten und
           entscheidet, ob Befund 1 (GATE_FIELDS im Build planner) einen
           eigenen Auftrag bekommt. Danach developer.
BLOCKIERT DURCH: nichts
```

---

## Kurzfassung

Die 28 des `architect` stimmen — in **beiden** Umgebungen, mit derselben
Summe aus einer anderen Mischung. Sie sind aber **nicht eine Klasse, sondern
zwei**, und die eine ist schlimmer als gemeldet: **19 der 20 problematischen
Zeilen in A** (19 der 22 in B) gehoeren zu Effekten, die mit Armaturen
ueberhaupt nichts zu tun haben — sie geben dem Spieler einen **Gegenstand**
zu Beginn der Expedition (`Stonesword Key in possession at start of
expedition`). Fuellung (c) waere dort nicht vage, sondern **falsch**.

Entschieden ist deshalb weder eine siebte Fuellung noch eine Umformulierung,
sondern eine **Verengung des Tests**: Fuellung (c) trifft nur noch, wo das
Programm die Armaturenfrage gestellt und mit Nein beantwortet bekommen hat.
Der Wortlaut aller sechs Fuellungen bleibt Buchstabe fuer Buchstabe stehen.

---

## Punkt 1 — AK-168 nachgezogen (AK-177 bis AK-180)

### Die Entscheidung

**Fuellung (c) trifft genau dann zu, wenn**

1. der Effekt ein Feld aus `model.WEAPON_TYPE_GATES` traegt
   (`triggerOnWepType`, `wepTypeTrigger`), `model.satisfied_by_weapon` dafuer
   gegen die gefuehrten Waffentypen **falsch** ist, **und** der verlangte
   Wert der `wep_type` mindestens einer Waffe des Datenabzugs ist, **oder**
2. der Effekt `startSwordArtsId` traegt.

`wepTypeTriggerCount` allein schickt keine Zeile mehr nach (c). Solche Zeilen
fallen auf **(b)** — `{effect name}: only applies under a condition, so no
number here.` — was wahr ist, mit der Liste 4.9b uebereinstimmt und keinen
Hebel verspricht.

**Warum diese und nicht die drei Wege des Auftrags:** weil die Messung die
Voraussetzung der drei Wege widerlegt. Alle drei gehen davon aus, die 28
seien Waffen*anzahl*-Faelle. Sie sind es zu einem Zwanzigstel.

### Der Befund, aufgeschluesselt

Die 46 Zeilen, die AK-167/168 in Umgebung A nach (c) schieben, plus die 12
Zeilen, die dort schon standen (Summe 58):

| Klasse | A | B |
|---|---|---|
| nur `triggerOnWepType` unerfuellt — echte Typschranke, Hebel vorhanden | 18 | 19 |
| `wepTypeTrigger` **und** `wepTypeTriggerCount` unerfuellt (`Improved Attack Power with 3+ Bows Equipped`) — Typ pruefbar und unerfuellt, der Effektname nennt die Anzahl selbst | 8 | 6 |
| **nur `wepTypeTriggerCount` unerfuellt** | **20** | **22** |
| `startSwordArtsId` — tauscht die Waffenkunst der passenden Armatur | 12 | 0 |
| **(c) gesamt nach AK-167/168** | **58** | **47** |

Die 28 des `architect` = Zeile 2 + Zeile 3 (8+20 in A, 6+22 in B). **Nur
Zeile 3 ist falsch beschriftet**, denn Zeile 2 traegt ein pruefbares,
unerfuelltes Typfeld — fuer sie ist *"it depends on the armaments you carry"*
wahr.

Und Zeile 3 zerfaellt nach dem Wert des Feldes:

| Wert | A: Zeilen / Effekte | B: Zeilen / Effekte | Effektnamen |
|---|---|---|---|
| 256 | 9 / 6 | 9 / 6 | `Crimsonburst Crystal Tear in possession at start of expedition`, `Stonesword Key …`, `Small Pouch …` |
| 512 | 9 / 6 | 9 / 6 | `Fire Pots …`, `Lightning Grease …`, `Starlight Shards …` |
| 1024 | 1 / 1 | 1 / 1 | `Poisonbone Darts in possession at start of expedition` |
| **3** | **1 / 1** | **3 / 2** | `Improved Attack Power with 3+ Daggers Equipped` (B zusaetzlich `… with 3+ Bows Equipped`) |

**Ohne eine Vermutung ueber die Spieldateien** (AK-140/AK-157): im Abzug
tragen **alle 51** `wepTypeTriggerCount`-Effekte mit einem anderen Wert als 3
**zugleich `startGoodsId`**, und **alle 31** mit dem Wert 3 tragen es
**nicht** — 82 von 82, saubere Trennung. `GATE_FIELDS` beschriftet
`startGoodsId` selbst mit *"grants an item at the start of an expedition"*.
Was 256/512/768/1024 **bedeuten**, sage ich nicht; ich brauche es auch nicht.

**Genau ein Effekt im ganzen Abzug** (2076) ist eine echte Waffenanzahl ohne
pruefbares Typfeld: `Improved Attack Power with 3+ Daggers Equipped`
(7080000). Die anderen 30 mit Wert 3 tragen zusaetzlich `wepTypeTrigger`.

### Der latente Fall (Befund 2 des `architect`)

**Er faellt in die Loesung von Punkt 1, braucht keine eigene Aussage.** Die
Bedingung „der verlangte Wert ist der `wep_type` mindestens einer Waffe des
Abzugs" schliesst ihn mit derselben Regel: 256 und 512 sind kein Waffentyp,
also kein (c). Unabhaengig nachgemessen: **72 von 144** `triggerOnWepType`
(70 auf 256, 2 auf 512), Waffentyp-Vorrat **34** Werte ueber 1793 Waffen;
`wepTypeTrigger` 0 von 30. Auf diesem Spielstand **0 von 314** entdoppelten
besessenen Effekt-Ids, also 0 Zeilen — das Kriterium bewegt heute nichts und
ist ein reiner Waechter (so steht es auch in AK-179).

### Die Zahlen, beide Umgebungen, mit Rezept

**Messumgebung (L-009), erschoepfend gezaehlt, keine Stichprobe** — also kein
Stichprobenfehler und kein Sicherheitsabstand; die Unsicherheit liegt in der
Grundgesamtheit (ein Spielstand, ein Abzug, zwei von zehn Nightfarern). Alle
Zahlen sind **Zeilen im `Why`-Dialog**, keine Effekt-Ids und keine Pixel.

- **A:** Wylder, `Wylder's Greatsword` (`wep_type` 5), Stufe 15.
- **B:** Ironeye, `Ironeye's Bow` (`wep_type` 51), Stufe 15.
- Beide: Abzug `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`,
  `meta.extract_version` 11, `meta.data_version` 10350000, 2076 Effekte,
  1793 Waffen, nur gelesen. Spielstand des App Designers, **309** Kopien,
  **845** Effektrollen. `declared` leer. Ein Relikt je Slotgruppe, Slot 0,
  kein gehaltener Slot. `max_damage`, `EVEN_WEIGHTING`. Codestand `fd9f2bc`.

| Fuellung | A gebaut | A AK-167/168 | **A AK-177/178** | B gebaut | B AK-167/168 | **B AK-177/178** |
|---|---|---|---|---|---|---|
| (a) anderer Nightfarer | 150 | 150 | **150** | 159 | 159 | **159** |
| (a2) anderswo gezaehlt | 0 | 0 | **0** | 0 | 0 | **0** |
| (b) Bedingung | 170 | 124 | **144** | 174 | 127 | **149** |
| (c) Armaturen | 13 | 58 | **38** | 0 | 47 | **25** |
| (d) Rest | 93 | 94 | **94** | 101 | 101 | **101** |
| (e) nicht im Datensatz | 0 | 0 | **0** | 0 | 0 | **0** |
| **Summe** | **426** | **426** | **426** | **434** | **434** | **434** |

**Rezept** (Skript im Scratchpad, nicht im Repo; gerechnet mit
`explain.reasons` selbst, nicht mit einer Nachbildung):

1. `data = json.loads(paths.snapshot_path().read_text())`,
   `model.configure(data)`, `owned = inventory.load(data)`.
2. `ctx = types.GoalContext(data, hero, level=15,
   reference=ReferenceArmament(Startwaffe, tier=1, slot_index=0),
   weighting=goals.DEFAULT_WEIGHTING, weapons_held=(dieselbe Waffe,))`.
3. Je besessener Kopie `problem = SlotProblem(slots=(Slot(0, colour, deep),),
   held=())`, `base = evaluate(problem, (), ctx)`,
   `built = evaluate(problem, (cand,), ctx)`,
   `groups = explain.reasons(problem, (cand,), base, built, ctx,
   goals.GOALS["max_damage"])`.
4. Gezaehlt: `ReasonLine`, die weder `is_curse` noch
   `silence == CARRIES_A_FIGURE` sind. Zeile -> Effekt ueber den
   Namensanfang.
5. (c) je Zeile nach der neuen Regel neu bestimmt; (a), (a2), (e) gewinnen
   weiterhin vorher.

**Die Fremdmessungen sind reproduziert, nicht uebernommen.** Die
T-084-Spalte kommt Zeichen fuer Zeichen wieder heraus (150/0/124/58/94/0 =
426), die B-Spalte des `architect` ebenso (159/0/127/47/101/0 = 434).

**Zwei Unterschiede zwischen A und B, erklaerungsbeduerftig und erklaert:**

- (c) ist in B um 13 kleiner. Das sind die 12 `startSwordArtsId`-Zeilen plus
  eine: `effecttext.works_for` sagt fuer Ironeye bei allen **zehn** besessenen
  `Changes compatible armament's skill to …`-Effekten Nein, sie bekommen
  also Fuellung (a).
- Die Verschiebung selbst ist stabil: 20 Zeilen in A, 22 in B von (c) nach
  (b). Weder Nightfarer noch Waffengattung aendern das Bild.

### Verworfen, und warum

- **Siebte Fuellung, die die Anzahl benennt.** Ein Satz wie *"you need
  several of that weapon equipped"* waere auf **19 der 20** Zeilen **neu
  falsch**. Der Weg glaubt dem Feldnamen; der Feldname luegt hier. Dazu haette
  er AK-169 aufgemacht und eine siebte Fuellung eingefuehrt, die keinen Fall
  sauber trifft.
- **(c) vager umformulieren.** Kein Satz ueber Armaturen ist fuer
  `Fire Pots in possession at start of expedition` wahr, auch kein vager. Der
  Weg haette zusaetzlich den 26 Zeilen (18+8 in A) die konkrete Auskunft
  genommen, bei denen der Hebel existiert — Preis zweimal gezahlt, Fehler
  nicht behoben.
- **Die 28 nach (d).** Erstens so nicht herstellbar: (d) ist die letzte
  Fuellung, und diese Zeilen sind `Situational live == False`, fallen also
  auf (b), sobald (c) sie nicht mehr faengt. Zweitens ist (b) die bessere
  Auskunft: derselbe Effekt steht in der Liste 4.9b unter *"only apply under
  a condition"*, und (d) (*"no number here shows what this adds"*) haette dem
  Spieler zwei verschiedene Antworten auf eine Frage gegeben.

### Der Preis, ausdruecklich (A12)

- **1 Zeile in A, 3 in B verlieren die konkrete Auskunft**, obwohl sie
  wirklich an einer Waffenanzahl haengen. **Der Spieler verliert nichts:** der
  Effektname sagt selbst *"with 3+ Daggers Equipped"* — die Auskunft steht
  vor dem Doppelpunkt.
- **Wer einer (c)-Zeile folgt und die Waffe anlegt, kann auf (b) landen.**
  Umgebung B zeigt es an `Improved Attack Power with 3+ Bows Equipped`: fuer
  Wylder (c), fuer den bogenfuehrenden Ironeye (b), weil dann nur noch die
  Anzahl fehlt. Kein Widerspruch, aber die zweite Zeile ist schwaecher als
  die erste. Ein Satz *"you need three of them"* waere eine Aussage ueber die
  Spieldateien, die der Abzug fuer den Wert 3 nicht hergibt.
- **Nicht gemessen:** wie oft eine solche Zeile in einem **vollen Lauf** vor
  dem Spieler steht. Der `architect` hat fuer die Nachbarfrage 1 von 176
  Laeufen gemessen (T-085 §2c). Meine Zahlen beschreiben die
  **Kandidatenmenge** des Pickers, nicht den Vorschlag.

---

## Punkt 2 — die Zahl in §6 (AK-181)

Der Satz ist **richtig**; er beschreibt die **Liste**, nicht die **Zeile**.
Nachgemessen, unabhaengig von jeder Fuellungsreihenfolge: **170** stumme
Zeilen in A (174 in B) gehoeren zu einem Effekt, der in `Build.situational`
mit `live == False` steht — genau die Menge, aus der 4.9b und `not_counted`
gespeist werden. Zum Vergleich: `explain.not_counted(built)` liefert ueber
denselben Bestand **197** Eintraege (A) bzw. **201** (B); auch das deckt sich
mit T-085.

Die **124** (T-084) und **144** (T-086) sind etwas anderes: die Zahl der
Zeilen, die Fuellung (b) **bekommen**. Kleiner, weil (a), (a2) und (c) in der
Reihenfolge nach AK-167 vorher zugreifen.

§6 ist mit einer Nachtragsklammer angeschrieben, die beide Zahlen ihrer
Lesart zuordnet; der urspruengliche Satz steht unveraendert. Zusaetzlich hat
**§4 des T-080-Abschnitts** eine Klammer bekommen, weil dort die
Reihenfolge (b) vor (c) und die alten Klammerzahlen (150 / 170 / 58 / 48)
noch als geltende Vorgabe dastanden — ohne den Vermerk waere `UI_SPEC.md`
nach Punkt 1 in sich widerspruechlich gewesen. Die **Wortlaute** der
Fuellungen sind unangetastet.

---

## Abnahme: die Eigenschaft, nicht die Fundstelle

Meine Frage ist eine andere als die des `architect` (er fragte nach der
Klasse, ich nach dem Wortlaut): **welches Feld traegt eine Beschriftung, die
dem Spieler einen Hebel nennt, den es nicht gibt?** Drei unabhaengig
formulierte Masken ueber alle 2076 Effekte:

- **Maske 1 — Beschriftung.** Jede `GATE_FIELDS`-Beschriftung, die eine
  Handlung des Spielers nennt (`with`, `equipped`, `armament`, `weapon`),
  gegen die Frage, ob `satisfied_by_weapon` sie ueberhaupt beantworten kann.
  **4 Treffer**, davon **2 nicht pruefbar**: `wepTypeTriggerCount` (82
  Effekte, *"needs several of that weapon equipped"*) und `startSwordArtsId`
  (20, *"changes the armament's skill"*). Die uebrigen 11 Beschriftungen
  nennen einen Zustand oder ein Ereignis, keinen Griff.
- **Maske 2 — Wertebereich.** Jedes waffenbezogene Feld gegen den
  Waffentyp-Vorrat des Abzugs (34 Werte, 1793 Waffen).
  **`triggerOnWepType` 72 von 144 ausserhalb** (256/512),
  **`wepTypeTriggerCount` 51 von 82 ausserhalb** (256/512/768/1024),
  `wepTypeTrigger` **0 von 30**.
- **Maske 3 — Effektname, unabhaengig von Feldname und Wert.** Nennt der
  Effektname selbst eine Armatur? `wepTypeTriggerCount`: **48 von 82 nennen
  keine** (die ganze `… in possession at start of expedition`-Familie).
  `triggerOnWepType`: **20 von 144 nennen keine** (`Lightning upon Precision
  Aiming` u. a., alle mit Wert 256). `wepTypeTrigger` **0 von 30**,
  `startSwordArtsId` **0 von 20** — diese beiden sind sauber.

**Alle drei Masken zeigen auf dieselben zwei Stellen** und auf keine dritte:
`wepTypeTriggerCount` mit einem anderen Wert als 3, und `triggerOnWepType`
mit 256/512. `startSwordArtsId` ist zwar nicht pruefbar (Maske 1), aber seine
Beschriftung beschreibt, was der Effekt **tut**, und der Effektname sagt es
in 20 von 20 Faellen selbst — kein toter Hebel. **Kein weiteres Feld hat
diese Eigenschaft.**

---

## Neue Akzeptanzkriterien, je eine Zeile

- **AK-177** — Fuellung (c) nur bei einem unerfuellten `WEAPON_TYPE_GATES`-
  Feld mit einem Wert aus dem Waffentyp-Vorrat, oder bei
  `startSwordArtsId`; (c) = 38 (A) / 25 (B). *Rot-vorher:* eine Umsetzung
  nach dem Wortlaut von AK-168 gibt 20 (A) bzw. 22 (B) Zeilen *"it depends on
  the armaments you carry"*, davon je 19 an Gegenstandseffekten.
- **AK-178** — eine Zeile, deren einzige unerfuellte Armaturenschranke
  `wepTypeTriggerCount` ist, bekommt Fuellung (b) und enthaelt nirgends
  `armaments you carry`; (b) waechst auf 144 (A) / 149 (B). *Rot-vorher:*
  `Stonesword Key in possession at start of expedition: it depends on the
  armaments you carry, so no number here.`
- **AK-179** — eine Schranke auf einen Wert, den keine Waffe des Abzugs als
  `wep_type` fuehrt, ist kein (c); bewegt heute 0 Zeilen, bewacht 72
  Effekte. *Rot-vorher:* dieselbe Zeile, sobald der Spieler eine Kopie mit
  `triggerOnWepType = 256` findet.
- **AK-180** — Partition mit fortgeschriebenen Zahlen: 150/0/144/38/94/0 =
  426 (A), 159/0/149/25/101/0 = 434 (B). **Ersetzt die Zahlenreihe in
  AK-169**, dessen Regel bleibt. *Rot-vorher:* die AK-169-Reihe summiert sich
  auch auf 426, verteilt aber 20 Zeilen falsch — die Summe allein ist kein
  Waechter.
- **AK-181** — jede Zahl ueber die stummen Effektzeilen nennt ihre Lesart
  (Liste oder Fuellung) und ihre Messumgebung. *Rot-vorher:* §6 vor diesem
  Nachtrag, wo 170 und 124 wie zwei Messungen derselben Groesse aussehen.

---

## Was mir aufgefallen ist und nicht in den Auftrag gehoerte

**Befunde ohne Nummer — die vergibt der `director`.**

1. **`GATE_FIELDS` beschriftet im Build planner 51 Gegenstandseffekte als
   Waffenanzahl.** Fundstelle `nrplanner/model.py`, `GATE_FIELDS`,
   Schluessel `wepTypeTriggerCount`. Unter `Conditional & situational` steht
   heute *"needs several of that weapon equipped"* an Effekten wie
   `Stonesword Key in possession at start of expedition`, die zugleich
   `startGoodsId` tragen und daher direkt darunter *"grants an item at the
   start of an expedition"* zeigen — zwei Beschriftungen, von denen eine
   nicht stimmt. Dazu der bereits gemeldete Fall *"only with a matching
   weapon type"* an 72 Effekten mit 256/512 (das ist OF-23 des `architect`,
   ich bestaetige seine Zahl unabhaengig). **Das ist eine andere Oberflaeche
   als die Beraterzeile** und liegt auf dem Tab, den der App Designer
   ausdruecklich gut findet; AK-177 bis AK-179 fassen sie **nicht** an.
   Beleg: 51 von 82 bzw. 72 von 144, Messung wie oben.
2. **Der Feldname ist in diesem Datensatz keine Beschreibung des Effekts.**
   `wepTypeTriggerCount` traegt zwei voellig verschiedene Bedeutungen,
   getrennt allein durch den Wert (3 gegen 256/512/768/1024) und begleitet von
   `startGoodsId`. Das ist die verallgemeinerbare Lehre aus T-085 und T-086:
   wer eine Nutzerzeile an einem Feldnamen aufhaengt, ohne den Wertebereich
   und die Effektnamen dahinter angesehen zu haben, schreibt frueher oder
   spaeter etwas Falsches hin. Die drei Masken oben sind billig und haetten
   den Fehler in T-084 verhindert. **Das gehoert in eine Hausregel**, nicht
   nur in diesen Bericht — Vorschlag an den `director`.
3. **Nicht ausgefuehrt: die Suite.** Ich habe keine Zeile Anwendungscode
   angefasst, und `tests/test_advisor_bar.py`, `nrplanner/advisorbar.py`,
   `nrplanner/app.py` aendern sich gerade unter mir (T-083). Der Stand
   1059 / 9 / 5 aus `docs/state.md` ist von mir **nicht** nachgeprueft.
4. **Der Arbeitsbaum hat sich waehrend meines Laufs bewegt.** Beim Start war
   HEAD `fd9f2bc` mit uncommittetem UI_SPEC.md; am Ende ist HEAD `cecf0fd`
   (der T-084-Nachtrag, AD-026 und die Auftragsdateien sind committet), und
   `nrplanner/advisor/explain.py` ist neu geaendert: ein `developer` hat den
   `not_counted`-Docstring nach AD-026 ersetzt. **Die Aenderung ist
   ausschliesslich Docstring** (9 Zeilen ein, 4 aus, alle innerhalb der
   Zeichenkette) und beruehrt keine meiner Zahlen; zum Zeitpunkt der Messung
   war die Datei byteweise `fd9f2bc`, einzeln geprueft. Ein entsprechender
   Vermerk steht in §0 des neuen `UI_SPEC`-Abschnitts. Ebenfalls neu
   aufgetaucht: `docs/tasks/T-087.md` (nicht gelesen, nicht meiner).
5. **Meine Aenderung an `UI_SPEC.md` ist uncommittet** — ich habe keine
   Commit-Rechte, der `director` committet.

---

## Offene Fragen an den App Designer

**Keine neue.** Punkt 1 und Punkt 2 sind Richtigkeitsfragen mit einem
messbaren Richtig und Falsch, kein Geschmack. Die vier bestehenden Fragen
(F-B, F-C, F-F, F-G) sind unberuehrt.

Eine **Frage an den `director`**, nicht an den App Designer: soll Befund 1
(die `GATE_FIELDS`-Beschriftungen im Build planner) ein eigener Auftrag
werden? Er betrifft einen bereits abgenommenen Tab, ist derselbe A7-Bruch,
und er ist heute **sichtbar** — anders als die Beraterzeile, die noch nicht
gebaut ist.
