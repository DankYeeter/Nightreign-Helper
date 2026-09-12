STATUS: erledigt
AUFTRAG: T-055 — Inhaltsaudit der sechs Tabs: stimmt, was dort steht, und beantwortet es eine Frage?
GELESEN: docs/tasks/T-055.md · GOAL.md (A10–A14) · docs/state.md · qa/findings.md (Zyklus 12, QA-114 bis QA-124) · DESIGN_REVIEW.md (DR-008 bis DR-012) · nrplanner/{effectstab,arsenaltab,bosstab,deeptab,depthstab,eventstab,eventlore,stacking,damage}.py · nrdata/extract.py (Herkunft der Zahlen) · tests/ (Abdeckung) · CLAUDE.md
GEÄNDERT: docs/berichte/T-055-qa-engineer.md (nur diese Datei; kein Code, keine Tests, kein Git-Zustand)
ANNAHMEN: keine zur intendierten Funktion — A10 bis A14 in GOAL.md sind die Sollvorgabe und liegen schriftlich vor. Eine Messannahme: alle Messungen laufen gegen den Datensatz `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json` (Stand 05.09.2026 11:27, extract_version des Baums), plus zwei Direktlesungen aus der Installation D:\SteamLibrary\...\ELDEN RING NIGHTREIGN.
NÄCHSTER: ui-ux-designer (Spec-Modus für die Anzeigebefunde), danach developer
BLOCKIERT DURCH: nichts

---

# T-055 — Inhaltsaudit der sechs Tabs

Rolle: `qa-engineer` · Zyklus 13 · 2026-09-05
Nummernkreis: **QA-125 bis QA-139** (fortlaufend ab dem in `docs/state.md`
gesetzten Startwert)

## Was hier geprüft wurde — und was nicht

Geprüft wurde nicht, ob der Code tut, was er soll, sondern ob das, **was auf
dem Bildschirm steht, wahr, vollständig und begründet ist** und ob es eine
Spielerfrage beantwortet (A10, A12, A14). Der Nachweis läuft in drei Formen:

1. **Direkte Bildschirmsonden.** Jeder der sechs Tabs wurde headless
   instanziiert und sein sichtbarer Text vollständig ausgelesen (Labels,
   Tabellenzellen, Detailpanels, Tooltips). Zitate in diesem Bericht sind
   ausgelesener Bildschirmtext, keine Codelesung.
2. **Gegenrechnung gegen die Datenquelle.** Wo eine Zahl aus einer Rechnung
   kommt, wurde die Rechnung nachgefahren; wo sie aus einer Annahme kommt,
   wurde die Annahme benannt. Zwei Zahlen wurden gegen die **Spielparams
   selbst** gelesen (`regulation.bin`, read-only).
3. **Mutationsnachweis für die Abdeckung** (L-002/L-003): sieben
   Anzeigemutationen gleichzeitig, plus eine Kontrollmutation, die rot
   werden **muss**.

Nicht geprüft: `Build planner` (ausgenommen), A11 (läuft parallel beim
`power-user`), A13 am laufenden Fenster (Sichtprüfung ist DR-Sache; T-052 hat
sie gerade gemacht, Screenshots liegen unter `docs/screenshots/2026-09-05/`).

## Testumgebung und Ausgangsstand

- `.venv\Scripts\python.exe -m pytest -q -m "not slow"` im eigenen Klon:
  **622 passed, 5 deselected in 105,43 s** — deckt sich mit dem im Auftrag
  genannten Stand. Kein Fehlschlag vor den eigenen Tests.
- Klon: `scratchpad/nh-clone` auf `30a98bc`. Der Arbeitsbaum hat gegenüber
  diesem Commit **nur Dokumentenänderungen** (`git status --porcelain`:
  8 geänderte `.md`, kein `.py`) — Code im Klon und im Arbeitsbaum sind
  identisch.
- Datensatz: 2 076 Effekte, 849 benannte Reliktvorlagen, 1 792 Armaturen,
  160 Zauber, 10 Nightlords, 11 extrahierte World Events, 25 Deep-Profile.

## Abgleich gegen Bekanntes (keine Doppelmeldung)

Vor jeder Nummernvergabe abgeglichen: DR-008 bis DR-012, QA-116, QA-117,
QA-119, QA-121, QA-122, QA-123, QA-124.

- **Namenskollision im Arsenal (DR-008/QA-119/QA-099a): keine neue Nummer.**
  Ich melde nur eine Beobachtung dazu unter „Offene Fragen": der in QA-119
  genannte Auslöser („zwei `Recluse's Staff` mit 128 und 151") ist auf dem
  aktuellen Datensatz **nicht mehr reproduzierbar** — `Recluse's Staff`
  kommt genau einmal vor (id 33750000, Kennzahl 139), auf allen vier
  Aufstiegsstufen. Die **Klasse** besteht weiter: 6 Kacheln tragen einen
  Namen, den eine zweite Kachel auch trägt (`Scholar's Thrusting Sword` 4×,
  `Finger Seal` 2×) — diesmal aber mit **identischen** Zahlen, also als
  reine Doppelgänger statt als widersprüchliche Angaben.
- QA-121/DR-010 (Zusammenfassungssatz des Arsenal-Tabs) gilt als behoben; der
  Satz definiert jetzt beide Kennzahlen. Ich melde dazu nur den
  **Bezeichnungswechsel** (QA-139), der dabei entstanden ist.
- QA-117/DR-012, QA-116/DR-011, QA-122, QA-123, QA-124: nicht erneut geprüft,
  nicht erneut gemeldet.

**Suche nach überholten Beschriftungen (L-006, zwei unabhängige Masken):**
Maske A `60%|under investigation|ranking between weapons is unaffected` →
5 Treffer in `nrplanner/`, **alle in Kommentaren** (`arsenaltab.py:307-308`
zitiert die AK-34-Regel selbst; `model.py:221,257,892` beschreiben einen
anderen Sachverhalt). Maske B
`unverified|not verified|physical attack rating|uncalibrated|provisional` →
2 Treffer, beide in Docstrings (`advisor/goals.py:97`, `damage.py:328`).
**Kein überholter Wortlaut steht in einer angezeigten Zeichenkette.** Ein
Rest bleibt (QA-139, Bezeichnungswechsel) — der ist neu entstanden, nicht
überholt.

## Risiko-Briefing (vor dem Testen formuliert, in dieser Reihenfolge abgearbeitet)

Die riskanteste Stelle sind die **abgeleiteten Kennzahlen der Effektetabelle**
(`Pools`, `Avg chance`, `Best chance`): sie entstehen aus einer Aggregation
über Farben und Modi, tragen große Zahlen und eine Beschriftung, die eine
präzise Bedeutung behauptet — genau die Konstellation, in der eine falsche
Aggregation jahrelang unbemerkt bleibt. Zweitens die **handgepflegten
Konstanten im Nightlords-Tab** (`DEBUFF_ON_BREAK`, `BUFF_TRIGGER`,
`WEAKNESS_NOTE`): sie stehen im selben Panel und in derselben Typografie wie
extrahierte Werte, altern aber unabhängig vom Datensatz. Drittens die
**Spannen und Mediane des Deep-Tabs**, weil sie aus 25 Profilen mit
unbekannter Zuordnung entstehen. Viertens die **Kartenauswahl im
Red-variants-Tab**, weil eine Auswahl, die nur einen Teil der Anzeige bewegt,
immer ein Kandidat für eine falsche Aussage ist. Zuletzt die **Abdeckung**:
nach QA-123 war zu erwarten, dass die Messstrecke die Inhalte dieser Tabs
nicht sieht — das wollte ich mit einem Gegenbau belegen, nicht behaupten.

Alle fünf Vermutungen haben sich bestätigt; die vierte am deutlichsten.

---

# Tab 1 — Effects & chances

### 1. Welche Spielerfrage beantwortet dieser Tab?

„Welche Effekte kann ein Relikt tragen, wie wahrscheinlich rolle ich einen
bestimmten, und lohnt sich ein zweiter davon?" — Der Tab beantwortet sie
grundsätzlich; die Frage steht aber nirgends auf dem Tab (siehe QA-138), und
zwei der drei Zahlenspalten beantworten sie nicht so, wie ihre Beschriftung
verspricht (QA-125, QA-126).

### 2. Stimmen die Zahlen?

| Angezeigt | Herkunft | Urteil |
|---|---|---|
| `577 buffs (blue) then 75 curses (red)` | Auszählung der gefilterten Zeilen | stimmt (652 Zeilen gezählt) |
| `17 identical duplicates merged` | `len(candidates) - len(rows)` | stimmt |
| `For 50 the game gives nothing beyond the name` | Zählung `describe_full == NO_DESCRIPTION` | stimmt, und ist A7-vorbildlich |
| Spalte `Pools` | **Summe der `pools`-Felder über alle Farb- und Modus-Einträge** | **falsch beschriftet — QA-125** |
| Spalte `Avg chance` | **ungewichtetes Mittel über die Farb-/Modus-Eimer** | **entspricht keiner der beiden Definitionen auf dem Bildschirm — QA-126** |
| Spalte `Best chance` | `max` über dieselben Einträge | rechnerisch richtig; 182 von 652 Zeilen zeigen `100.0%`, jede davon durch einen Ein-Eintrag-Pool (192 Effekte im Datensatz, 192 davon mit einem Eintrag `max = 1.0` — Mechanismus bestätigt) |
| Spalte `Stacking` + Tooltip | `stacking.classify` / `stacking.evidence` | **stimmt und ist der stärkste Teil des Tabs** — jeder Tooltip nennt das entscheidende Feld, z. B. `exclusivityId 1000 — the game groups these and applies only one` |
| Spalten `Tier`, `Copies` | aus dem **gefilterten** Ausschnitt gebildet | **filterabhängig, obwohl als Eigenschaft der Spieldaten beschrieben — QA-127** |

Gegenprobe, die keine war: `Avg > Best` kam in **0 von 652** Zeilen vor.

### 3. Nennt jede Zahl ihre Einheit und ihren Bezug? (A12)

Nein. `Pools 878` ist eine Zahl ohne Grundgesamtheit und mit einer falschen
Bezugsgröße im Tooltip. `Avg chance 20.4%` nennt weder die Grundgesamtheit
(pro Effektplatz? pro Relikt? pro Pool?) noch, dass sie über Farben **und**
Modi gemittelt wurde, während die Zusammenfassung von „the selected colour and
mode" spricht — bei der Voreinstellung ist gar keine Farbe gewählt.

### 4. Was steht da, das keine Frage beantwortet?

- **`Pools`.** Der eigene Tooltip sagt: *„More pools does not mean more likely
  — the two chance columns say that."* Eine Spalte, die im Tooltip erklärt,
  dass sie die Frage nicht beantwortet.
- **`Copies`.** 638 von 652 Zeilen zeigen `1`; nur 14 Zeilen zeigen 2, 3 oder 4.
- **`Type`.** Redundant zur Farbkodierung (Name und Beschreibung sind bereits
  blau bzw. rot) — trägt aber die Sortierung, die die Gruppierung herstellt.
- Nicht sichtbar, aber erwähnenswert: `effectstab.deduplicate()` ist definiert
  und wird nirgends aufgerufen (`refresh()` baut die Verschmelzung selbst).

### 5. Was fehlt?

Zur Frage „lohnt sich der zweite?" fehlt nichts — die Stacking-Spalte
beantwortet sie mit Beleg. Zur Frage „wie komme ich an diesen Effekt?" fehlt
der **Relikt-Bezug**: `Best chance 100%` sagt, dass es irgendwo einen Pool
gibt, der ihn garantiert, aber nicht auf welchem Relikt. Ohne den ist die
Spalte für 182 Zeilen nicht handlungsfähig.

### 6. Ist es abgedeckt?

**Nein — kein Test der Suite berührt `effectstab`.** Zwei unabhängige
Suchmasken: `grep -rn "effectstab" tests/` → 0 Treffer;
`grep -rn "EffectsTab" tests/` → 0 Treffer. Mutation M4 (`format_chance`
zeigt Prozente **zehnfach**) lässt 622 von 622 grün. Siehe QA-137.

---

# Tab 2 — Weapons & spells

### 1. Welche Spielerfrage beantwortet dieser Tab?

„Welche Waffe schlägt mit meinem aktuellen Build am härtesten zu, und was
kostet mich ein Zauber?" — Der Tab beantwortet die erste Hälfte gut und die
zweite bewusst nur teilweise (Zauberschaden steht nicht in den Spieldaten, und
der Tab sagt das).

### 2. Stimmen die Zahlen?

Stichproben an einer echten headless `Planner`-Instanz (Wylder, Level 1, +1):

| Kachel | Angezeigt | Urteil |
|---|---|---|
| Longsword | `AR 49 · Physical 49 · Scaling STR 50 · DEX 50 · Rarity Common` | Zahlen konsistent; Kopfzahl und einzige Typzeile sind dieselbe Zahl |
| Fire Longsword | `AR 48 · Physical 24 · Fire 23` | 24+23 = 47 ≠ 48 — **kein Befund**: die Summe der abgeschnittenen Teile ist nicht die abgeschnittene Summe, das ist in T-045 als Rundungsverhalten abgenommen |
| Carian Regal Scepter | `Spell power 145 · Scaling INT 100 · Legendary` | passt zur T-046-Abnahme (Scepter reiht vor Rotten Crystal Staff: 145 > 111) |
| Bloodhound's Fang | `AR 70 · Physical 70 · Blood Loss buildup 38` | konsistent |
| Glintstone Pebble | `FP 7 · Stamina 20 · Slots 1` + Spieltext | konsistent |

Kopfzeile und Zusammenfassung stimmen mit dem Build überein (1 792 Armaturen
+ 160 Zauber = „1952 shown").

### 3. Nennt jede Zahl ihre Einheit und ihren Bezug? (A12)

**Nein, und das ist der schwerste A12-Verstoß der sechs Tabs.** Die Zeile
`Scaling STR 50 · DEX 50` steht auf **jeder** der 1 792 Waffenkacheln.
Gemessen: die Werte laufen von 7 bis 100 über 46 verschiedene Zahlen, es gibt
**keine** Kachel mit `Scaling none`. Weder Tooltip noch Zusammenfassung noch
Überschrift sagen, was diese Zahl ist — das Spiel selbst zeigt an dieser
Stelle Buchstabengrade (E bis S). Ebenso ohne Bezug: `Blood Loss buildup 38`,
`Slots 1`, `Stamina 20`. Siehe QA-128.

### 4. Was steht da, das keine Frage beantwortet?

- **Die doppelte Kopfzahl.** Bei **655 von 1 792** Armaturen druckt die
  Kopfzeile und die einzige Schadensartzeile dieselbe Zahl (`AR 49` /
  `Physical 49`).
- **`Slots`** auf Zauberkacheln: **160 von 160** Zaubern zeigen `1`.
- `Stamina` ist auf allen 160 gesetzt, `FP charged` nur auf 66 — die
  bedingten Zeilen arbeiten also, die unbedingte `Slots` nicht.

### 5. Was fehlt?

Nichts, was ohne neue Funktion zu haben wäre. Die eine echte Lücke ist die
Erklärung der `Scaling`-Zeile (QA-128) — das ist Beschriftung, keine Funktion.

### 6. Ist es abgedeckt?

**Ja, als einziger der sechs Tabs wirklich.** Kontrollmutation
(`rank_candidates` bekommt eine Stufe zu viel) → **6 failed, 2 passed** in
`test_arsenal_tab_asks_the_facade.py` und `test_arsenal_tab_wiring.py`. Die
Abdeckung reicht aber nur bis zur AR-Zeile: Mutation M7 (Zusammenfassungssatz
verfälscht) bleibt grün, und die Zauberkacheln sind ungedeckt (QA-123
beschreibt die verwandte Blindstelle der Messstrecke).

---

# Tab 3 — Nightlords

### 1. Welche Spielerfrage beantwortet dieser Tab?

„Womit greife ich diesen Nightlord an, und was macht er, wenn ich ihn treffe?"
— Für 9 von 10 Nightlords beantwortet der Tab das. Für **Adel** beantwortet er
es gar nicht (QA-131).

### 2. Stimmen die Zahlen?

| Behauptung auf dem Bildschirm | Prüfung | Urteil |
|---|---|---|
| `Same stats as above — resistances, stance and buff are identical` (Everdark) | Profile aller 8 Paare byteweise verglichen | **stimmt, 8 von 8 identisch** — kein Befund |
| `3 of 10 for bar size (smallest Harmonia 75, largest Caligo 160)` | gegen alle 10 Balkenwerte | stimmt; Gleichstände teilen sich einen Platz (drei Bosse bei 150 zeigen alle „6 of 10") |
| `Refills at x0.846` | `stance.recovery` | stimmt — **außer bei Maris: `x-1`, QA-130** |
| `Debuff x2.0 damage taken / x0.8 attack power` | gegen `ladder.down` | **entkoppelt vom gezeigten Boss — QA-129** |
| `Buff x1.35 attack · harder to stagger` | `ladder.up` | stimmt |
| `Stacks: yes — repeats compound` | im Datensatz nicht vorhanden | fest verdrahtet, in extrahierter Typografie — Teil von QA-129 |
| `takes 90% less damage · 60s` (Libra) | `defence_buffs` id 45875, `taken=0.1`, `seconds=60` | stimmt |
| Schadensbalken `x1.35` usw. | `profile.damage` | stimmt; Balkenlänge ist **pro Boss** skaliert (`widest = max(values + [1.0])`), also nicht zwischen Bossen vergleichbar |

### 3. Nennt jede Zahl ihre Einheit und ihren Bezug? (A12)

Nein, an drei Stellen: `Bar to break 120` (Einheit unbenannt, Skala nur über
die Ranking-Zeile), `Refills at x0.846` (**Rate ohne Zeitbasis** — pro
Sekunde? pro Treffer?), und der ganze Block `STATUS BUILDUP` (`Poison 542`
gegen `Poison 154` — nichts sagt, ob mehr besser oder schlechter ist). Der
grüne Farbton markiert die schwachen Status, aber **keine Legende sagt das**.

### 4. Was steht da, das keine Frage beantwortet?

- **Der Klammerzusatz `(smallest Harmonia 75, largest Caligo 160)`** steht auf
  allen zehn Panels wörtlich gleich.
- **`BODY PARTS: Part 2 · x0.6 damage — armoured`.** `PART_NAMES` ist leer
  (bewusst, dokumentiert), also stehen dort Slotnummern. Bei Caligo beginnt
  die Liste bei `Part 2` — der Leser sucht `Part 1`.
- **`harder to stagger`** auf jeder Buff-Zeile: `stance_taken` ist bei **allen
  zehn** Bossen 0,85.
- **`Stacks: yes — repeats compound`**: auf jedem Boss mit Buff identisch.

### 5. Was fehlt?

Der Gegenpol zu „IT BUFFS ITSELF": **7 von 10 Bossen tragen im Datensatz eine
`ladder.down`** (Gladius 0,815 · Adel 0,917 · Gnoster 0,846/0,957 · Libra
0,957 · Fulghor 0,88 · Harmonia 0,8 · Straghess 0,8), und **keine davon wird
gezeigt**. Stattdessen steht auf drei Bossen eine handgetippte Zahl (QA-129).

### 6. Ist es abgedeckt?

**Fast nicht.** Ein Test berührt `bosstab`: `test_game_text_is_never_markup.py`
konstruiert `BossTab` und prüft, dass Spieltext nicht als Markup gerendert wird
(SEC-012) — er prüft **keinen** Inhalt. Mutation M6 (`x2.0`→`x9.9`,
`x0.8`→`x0.1`) lässt 622 von 622 grün.

---

# Tab 4 — Deep of Night

### 1. Welche Spielerfrage beantwortet dieser Tab?

„Lohnt sich die nächste Tiefe, was kostet sie mich, und wie komme ich hin?" —
Der Tab beantwortet sie in genau dieser Reihenfolge und ist inhaltlich der am
saubersten gebaute der sechs. Sein Problem sind die Bezugsgrößen.

### 2. Stimmen die Zahlen?

| Angezeigt | Herkunft | Urteil |
|---|---|---|
| `Rating needed 0-999 … 6000+` | Regex über `TutorialBody` des Spiels | stimmt, wörtlich aus dem Spieltext |
| `Reward multiplier x1.47 … x2.41` | `SessionRewardByModeRankParam`, f32 bei Offset 0 | Wert stimmt; **Bezugsgröße nirgends benannt, auch nicht im Code — QA-128** |
| `Sovereign Sigil 8/10/12/15/18` | s32 bei Offset 36 | Wert stimmt; die **Zuordnung zum Sigil ist eine Identifikation im Spiel**, nicht ein Link aus den Params — der Extraktor sagt das, der Bildschirm nicht |
| `Relic tier: Deep Delicate, Polished, Grand` (Depth 1) | Lostabelle, 12 Items | stimmt: 4× `Deep Delicate …`, 4× `Polished …`, 4× `Grand …` |
| `by Depth 4 only Grand relics are on the table` | Lostabellen Depth 4/5: je 4 Items, alle `Grand …` | **stimmt** |
| `Enemy HP x1.30 / 1.20 to 1.55` | Median über 25 Profile, gewichtet mit `len(rows)` | stimmt; 4 von 25 Profilen tragen für keine Tiefe Werte und fallen still heraus, `scaling_unresolved = 0` |
| „die fünf elementaren Raten bewegen sich gemeinsam" (Codebegründung für eine Zeile statt fünf) | über alle Profile und Tiefen geprüft | **stimmt, 0 Abweichungen** |
| `Two cataclysms 50 … 95%` + Note | `cataclysmWeight_1 + _2 = 100` in allen 5 Zeilen | **stimmt**, die Note ist korrekt hergeleitet |
| `Map concealed / Nightlord obscured 10%` + Note „never … in the same run" | `mapChallengeWeight_Map/_Nightlord/_None = 10/10/80` | **stimmt** |
| `Win +200`, Verlusttabelle | keine Param-Quelle | korrekt als solche ausgewiesen — die Herkunftszeile ist vorbildlich |

### 3. Nennt jede Zahl ihre Einheit und ihren Bezug? (A12)

Nein, an drei Stellen, alle im obersten Block: `Reward multiplier x1.47`
(Multiplikator worauf?), `Sovereign Sigil 8` (pro was?), und die ganze
Skalierungstabelle `x1.30` (verglichen womit? — die Antwort ist „mit einer
normalen Expedition", und sie steht nirgends). Siehe QA-128.

### 4. Was steht da, das keine Frage beantwortet?

- **Die Zeile `Win`** trägt fünfmal `+200`. Sie variiert nicht über die
  einzige Achse der Tabelle.
- **`Cursed relic — Uncommon` und `— Rare`** sind über alle fünf Spalten
  konstant (25 % / 40 %), und die Note darunter sagt das bereits.
- **`Map concealed` und `Nightlord obscured`** sind in allen fünf Spalten
  paarweise identisch (0/0/10/10/10).

### 5. Was fehlt?

Der Datensatz trägt `description` (die Erklärung des Modus aus dem Spiel) und
`sigil_info` (*„rays of everdark used for bartering in the Roundtable Hold"*).
Beide werden geladen und **nie gezeigt**, während der Tab eine Zeile
`Sovereign Sigil 8` ohne jede Erklärung führt. Das ist keine neue Funktion —
es ist eine Zeile, die die Frage aus Punkt 3 beantworten würde.

### 6. Ist es abgedeckt?

**Nein.** `grep -rn "deeptab" tests/` → 0; `grep -rn "DeepTab" tests/` → 0.
Mutation M1 (`WIN_RATING = 200` → `999`) und M2 (die beiden Zeilen
`saReceiveDamageRate`/`staminaAttackRate` vertauscht — genau die Verwechslung,
die der Code im Kommentar als schon einmal passiert beschreibt) lassen 622 von
622 grün.

---

# Tab 5 — Red variants

### 1. Welche Spielerfrage beantwortet dieser Tab?

„Wie viele rote Gegner erwarten mich auf dieser Karte in dieser Tiefe, und was
kann überhaupt rot sein?" — Die erste Hälfte beantwortet der Tab; die zweite
(„was kann rot sein") beantwortet er für die **größte** Zeile gar nicht
(QA-132).

### 2. Stimmen die Zahlen?

Die Summenbildung ist korrekt: Default Limveld, Depth 1 → 32 + 49 + 5 + 1 = 87,
und `Total` zeigt 87. Über alle sechs Karten und fünf Tiefen stimmen Zeilen-
und Summenzeile überein.

Gemessen: die fünf Tiefenspalten tragen **drei verschiedene Werte**, nicht
fünf. Für jede der sechs Karten gilt Depth 2 = Depth 3 und Depth 4 = Depth 5:

| Karte | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|
| Default Limveld | 87 | 96 | 96 | 100 | 100 |
| Mountaintop | 81 | 90 | 90 | 93 | 93 |
| Crater | 74 | 84 | 84 | 87 | 87 |
| Rotted Woods | 81 | 92 | 92 | 95 | 95 |
| Noklateo | 78 | 91 | 91 | 94 | 94 |
| Great Hollow | 110 | 126 | 126 | 134 | 134 |

Das ist die Datenlage des Spiels, kein Anzeigefehler: von 22 Mutationszeilen
hat **keine einzige** mehr als 3 verschiedene Werte über die fünf Tiefen.

Die Intro-Behauptung *„the boss tiers only join from Depth 2 on"* stimmt für
fünf Karten; auf **Great Hollow** gibt es überhaupt keine Evergaol-Zeile, und
die Zusammenfassung sagt das auch richtig („joining from Depth 2: Night
bosses"). Der Intro-Satz ist damit die allgemeinere und ungenauere Aussage von
beiden.

### 3. Nennt jede Zahl ihre Einheit und ihren Bezug? (A12)

Ja — hier ist der Tab gut. Die Intro sagt ausdrücklich: *„The figures are how
many red variants of each sort a run puts on the selected map."* Das ist eine
Zahl mit Einheit und Geltungsbereich. Der Geltungsbereich stimmt allerdings
nicht für die Spalte `For example` (QA-132).

### 4. Was steht da, das keine Frage beantwortet?

- **`For example` in ihrer heutigen Form.** Leer für die größte Zeile,
  identisch auf allen sechs Karten (siehe QA-132).
- **Zwei der fünf Tiefenspalten** wiederholen ihre Nachbarspalte.
- **`Night bosses (unconfirmed)`** zeigt 5 bis 9 Stück für etwas, das der Tab
  selbst als nie gesichtet kennzeichnet — das ist ehrlich und bleibt besser
  stehen als weg; es ist kein Streichkandidat, sondern ein Beispiel dafür, wie
  A7 richtig aussieht.

### 5. Was fehlt?

Nichts, was ohne neue Funktion zu haben wäre.

### 6. Ist es abgedeckt?

**Nein.** `grep -rn "depthstab" tests/` → 0; `grep -rn "DepthsTab" tests/` → 0.
Mutation M3 (Kategorie 160 — die Evergaol-Bosse — in die Zeile der gewöhnlichen
Gegner verschoben, wodurch die Evergaol-Zeile verschwindet und alle
Zeilenwerte kippen) lässt 622 von 622 grün.

---

# Tab 6 — World Events

### 1. Welche Spielerfrage beantwortet dieser Tab?

„Was ist das gerade, lohnt es sich, und was passiert, wenn ich es liegen
lasse?" — Der Tab beantwortet alle drei, für 11 extrahierte und 4
community-berichtete Ereignisse, und die Trennung der beiden Herkunftsklassen
über die Farbe ist konsequent durchgehalten.

### 2. Stimmen die Zahlen?

| Angezeigt | Herkunft | Urteil |
|---|---|---|
| `Adel 18% · Gnoster 10% · …` | Anteil der Kartenmuster des Nightlords, die den Modifier tragen | Wert stimmt; die Erklärzeile beschreibt ihn richtig als Poolzusammensetzung |
| `Can fire on Day 1 or Day 2` | `day1_patterns`/`day2_patterns` | wahr, aber auf **allen 11** Ereignissen identisch — QA-134 |
| `+2% attack power, all damage types each time it triggers, up to +10 stacks` | `buff.per_trigger` + `stacks_to` | stimmt |
| `Runes: 3,750–7,500 base` | `creature.runes` min/max | stimmt |
| `Drops: 20 different Dormant Powers` | Zählung nach `kind` | stimmt |
| `10,000 runes for 1s` | `part.duration = 1.0`, `part.lines = ['10,000 runes']` | **sinnfrei — QA-133** |
| `restores 100 stamina for 0.3s` | `part.duration = 0.3` | dieselbe Klasse |
| `invulnerable · +10% attack power, all damage types for 45s` | zwei Teile: `invulnerable` mit Dauer 0.0, `+10%` mit 45.0 | die Unverwundbarkeit steht ohne Dauer, während dieselbe Zeile bei Cold Mirage `invulnerable for 5s` sagt |
| `Lasts the rest of the expedition — not consumed, no cooldown.` | `buff.duration = -1` | stimmt, steht aber direkt unter einer Zeile mit `for 45s` — der Leser sieht zwei Dauern |

### 3. Nennt jede Zahl ihre Einheit und ihren Bezug? (A12)

Überwiegend ja — dieser Tab ist bei den Bezugsgrößen der beste der sechs (die
Prozentzeile erklärt sich selbst, die Rune-Zeile sagt „base"). Zwei Lücken:
`stamina recovery speed +5` (Einheit unbenannt) und `Runes: … base — rises the
more expeditions you have cleared` (Steigerung unbeziffert, obwohl die Zahlen
im Datensatz liegen und geladen werden — QA-135).

Eine Zusicherung ohne Geltungsbereich: **`Every other Nightlord: never.`** Das
ist eine Allaussage über alle 10 Nightlords, gestützt auf die extrahierten
Kartenmuster, und der Bildschirm sagt nicht, worauf sie beruht. Der Extraktor
sagt zusätzlich ausdrücklich, dass die Muster **gewichtet** sind und die
Prozentzahl deshalb *„not a spin probability"* ist — auch das steht nicht auf
dem Bildschirm.

### 4. Was steht da, das keine Frage beantwortet?

- **`Can fire on Day 1 or Day 2. Every other Nightlord: never.`** — beide Sätze
  wörtlich gleich auf allen 11 Ereignissen.
- **Die Quellennamen in den `Sources disagree`-Blöcken** (`fextralife`,
  `game8`, `Eldenpedia`, `thefifthmatt`) und Sätze wie *„It is pattern modifier
  230, the row this project had wrong"* — Herleitungssprache auf dem
  Bildschirm, gegen die selbst formulierte Regel des Moduls (QA-135).
- **`Scale-Bearing Merchant`** steht zweimal in der Liste: einmal als eigener
  Eintrag, einmal als Auflösung von `Curse of the Demon` (QA-136).

### 5. Was fehlt?

Die Tagesverteilung, die der Datensatz hergibt und die Anzeige wegwirft:
`Judgment` hat 19 Day-1- gegen 1 Day-2-Muster, `Fire-Summoning Beasts` 9
gegen 21. Beide zeigen denselben Satz „Can fire on Day 1 or Day 2".

### 6. Ist es abgedeckt?

**Nein.** `grep -rn "eventstab" tests/` → 0; `grep -rn "WorldEventsTab" tests/`
→ 0; `grep -rn "eventlore" tests/` → 0. Mutation M5 (das Tages-Gating sagt
`Fires on Day 2 only`, wo beide Tage möglich sind) lässt 622 von 622 grün.

---

# Befunde

### [P2 | Major | Hoch] QA-125 — Die Spalte `Pools` zählt keine Pools, sondern Relikt-Effektplätze; die Zahl ist größer als die Zahl der Pools, die es gibt

**Adressat:** developer (Zahl), ui-ux-designer (Beschriftung)
**Betroffen:** `nrplanner/effectstab.py:52-57` (Tooltip), `:361` (`pools = sum(...)`); Ursprung `nrdata/extract.py:2262-2274`
**Umgebung:** Effects & chances, Voreinstellung („All colours", „Normal + Deep")

**Reproduktion:**
1. Effects & chances öffnen, nichts filtern.
2. Zeile `Vigor +3` suchen. Spalte `Pools` zeigt **878**.
3. Kopfzeile `Pools` überfahren: *„How many of the game's loot pools can produce this effect. A pool is one of the lists a relic's effects are drawn from."*

**Erwartet:** eine Anzahl von Pools.
**Tatsächlich:** die Summe der Vorkommen über (Relikt × Effektplatz).
`Vigor +3` trägt vier Farbeinträge mit 221 + 222 + 217 + 218 = 878.

**Analyse — zwei unabhängige Belege, beide mechanismus-gebunden:**
1. *Identität, exakt aufgegangen:* Summe aller `pools`-Felder über alle
   Effekte, Farben und Modi = **338 927**. Summe der `pool_sizes` aller 849
   Reliktvorlagen = **333 167**; Summe aller `curse_options`-Längen =
   **5 760**. 333 167 + 5 760 = 338 927. Die Zahl zählt genau die
   (Relikt, Platz, Effekt)-Tripel — `shares[...]` wird in
   `extract.py:2216/2237` **je Relikt** angehängt, nicht je Pool.
2. *Obergrenze aus dem Spiel:* Direktlesung von `EquipParamAntique`
   (`attachEffectTableId_1..3` plus `unknown_8..10`) ergibt **598 verschiedene
   Pool-Tabellen**, auf die insgesamt **2 619 Reliktplätze** zeigen; der
   meistgenutzte Pool (id 2000000) wird von 240 Plätzen referenziert. Die
   größte auf dem Tab anzeigbare Zahl ist **1 110** („Defeating enemies fills
   more of the Art gauge"). **1 110 > 598** — ein Effekt kann nicht in mehr
   Pools liegen, als das Spiel hat.

**Auswirkung:** Die Spalte gibt eine Größenordnung vor, die es nicht gibt, und
der Tooltip erklärt einen Begriff („a pool is one of the lists…"), der auf die
gezeigte Zahl nicht passt. Sie ist zugleich der Träger der 0-Erkennung
(„nicht erreichbar unter diesen Filtern"), also nicht folgenlos zu entfernen.

**Vorschlag:** Entweder die Zahl auf das umbenennen, was sie ist (Relikte
bzw. Effektplätze, die diesen Effekt rollen können — das ist sogar die für
einen Spieler nützlichere Größe), oder die Poolzahl tatsächlich als Anzahl
verschiedener Tabellen extrahieren. Die Entscheidung, welche der beiden
Größen die Spielerfrage beantwortet, gehört zum ui-ux-designer.

---

### [P2 | Major | Hoch] QA-126 — `Avg chance` ist ein ungewichtetes Mittel über Farb-/Modus-Eimer und entspricht keiner der beiden Definitionen, die daneben stehen

**Adressat:** developer, ui-ux-designer
**Betroffen:** `nrplanner/effectstab.py:363` (`avg = sum(...)/len(relevant)`), Definitionen in `:58-61` (Tooltip) und `:349-353` (Zusammenfassung)
**Umgebung:** Effects & chances, Voreinstellung

**Reproduktion:**
1. Effects & chances öffnen, in die Suche `Improved Mind, Reduced Vigor` tippen.
2. Zeile `[Wylder] Improved Mind, Reduced Vigor`: `Avg chance` zeigt **20.4%**.

**Erwartet:** laut Zusammenfassung *„how likely an effect is on one roll"* —
also die Wahrscheinlichkeit pro Effektplatz.
**Tatsächlich:** 20,4 % gegen einen vorkommensgewichteten Wert von **0,91 %**
(Faktor 22,3).

**Analyse:** Die Datenlage des Effekts ist
`chance = {Rot: 1 Vorkommen, avg 1.0}` und
`deep_chance = {4 Farben: je 60 Vorkommen, avg 0.005012}`. Der Tab mittelt die
**fünf Eimer gleich**: (1,0 + 4 × 0,005012) / 5 = 0,204. Ein einziges
garantiertes Relikt bekommt damit 20 % des Gewichts gegen 240 Vorkommen mit
0,5 %. Der Wert ist weder „pro Roll" (dann 0,91 %) noch „averaged over every
pool" im Sinne des Tooltips, sondern ein Mittel über Farb-/Modus-Eimer — eine
Größe, die auf dem Bildschirm nicht benannt ist.
**Umfang:** **129 von 616** Effekten mit Chance-Eintrag ändern ihre angezeigte
Prozentzahl, wenn nach Vorkommen gewichtet wird. Die acht größten Abweichungen
sind alle Nightfarer-Attributrelikte, alle mit demselben Faktor 22,3.
**Gegenlesart, ausdrücklich benannt:** liest man „pool" als *verschiedene
Tabelle*, ist 20,4 % gegen diese Definition verteidigbar. Dann steht der
Widerspruch nicht in der Rechnung, sondern zwischen Tooltip und
Zusammenfassung — beide sind auf demselben Bildschirm sichtbar und sagen
Verschiedenes. Welche der beiden die gewollte ist, entscheidet nicht QA.

**Auswirkung:** Die Spalte ist die Kernzahl des Tabs. Ein Spieler, der nach
einem Wylder-Attributrelikt sucht, liest „jede fünfte Rolle" statt „etwa jede
hundertzehnte".

**Vorschlag:** Erst festlegen, welche Frage die Spalte beantwortet (pro
Effektplatz oder pro Pool), dann die Rechnung darauf ziehen und die
Beschriftung an genau **einer** Stelle formulieren, statt an zweien.

---

### [P3 | Major | Mittel] QA-127 — `Copies` und `Tier` ändern sich mit den Filtern, obwohl beide als Eigenschaft der Spieldaten beschrieben sind

**Adressat:** developer
**Betroffen:** `nrplanner/effectstab.py:318-333` (`merged`, `by_name` aus den gefilterten Kandidaten), Tooltips `:47-51`
**Umgebung:** Effects & chances, Farbfilter

**Reproduktion:**
1. Effects & chances, „All colours": `Continuous HP Recovery` steht zweimal,
   mit `Tier` = `1 of 2` und `2 of 2`.
2. Farbfilter auf `Red` stellen.
3. Die `Tier`-Zelle ist leer.

**Erwartet:** Der Tooltip sagt *„How many identical copies of this effect the
game defines"* und *„each rung is its own effect"* — beides sind Eigenschaften
der Spieldaten.
**Tatsächlich:** filterabhängig. Gemessen gegen „All colours":
`Red` 25, `Blue` 39, `Yellow` 34, `Green` 34 Namen mit anderer `Copies`-Liste;
`Red` 17, `Blue` 31, `Yellow` 26, `Green` 27 Namen, deren Leitersprosse
verschwindet.

**Entwarnung, ausdrücklich gemessen:** Eine **Umnummerierung** („1 of 3" wird
zu „1 of 2") kommt **nicht** vor — 0 Fälle über alle vier Farben und beide
Modi. Die Sprosse verschwindet, sie lügt nicht.

**Auswirkung:** Ein Spieler, der auf eine Farbe filtert, sieht einen Effekt
ohne Leiterkennzeichnung und schließt, es gebe nur eine Stärke.

**Vorschlag:** Beide Größen aus dem ungefilterten Effektbestand bilden und nur
die Anzeige filtern.

---

### [P2 | Major | Hoch] QA-128 — Systemisch: Zahlen ohne Bezugsgröße auf fünf der sechs Tabs (A12)

**Adressat:** ui-ux-designer (Beschriftung), developer (wo der Bezug auch im
Code unbekannt ist), director (bei `Reward multiplier`: A7-Abwägung)
**Betroffen:** siehe Belegliste
**Umgebung:** alle sechs Tabs, Voreinstellungen

**Reproduktion:** je Zeile der Belegliste den genannten Tab öffnen und die
genannte Zeile lesen. Keine der Zeilen trägt Tooltip, Legende oder Erklärsatz,
der die Bezugsgröße nennt.

| # | Tab | Angezeigt | Was fehlt | Umfang |
|---|---|---|---|---|
| 1 | Weapons & spells | `Scaling STR 50 · DEX 50` | Einheit und Skala; das Spiel selbst zeigt hier Buchstabengrade | **alle 1 792 Kacheln**, Werte 7–100 |
| 2 | Weapons & spells | `Blood Loss buildup 38` | Aufbau pro Treffer? pro Sekunde? | 830 Armaturen mit `inflicts` |
| 3 | Weapons & spells | `Slots 1`, `Stamina 20` | wovon | 160 Zauber |
| 4 | Nightlords | `Refills at x0.846` | **Rate ohne Zeitbasis** | 10 Panels |
| 5 | Nightlords | `Bar to break 120` | Einheit | 10 Panels |
| 6 | Nightlords | `STATUS BUILDUP: Poison 542` | Richtung (mehr = besser oder schlechter?) und Legende zur grünen Markierung | 10 Panels × 6 Zeilen |
| 7 | Deep of Night | `Reward multiplier x1.47` | **Multiplikator worauf** — im Code steht dazu nur „nine identical f32 multipliers" | 5 Spalten |
| 8 | Deep of Night | `Sovereign Sigil 8` | pro was; und dass die Zuordnung eine Identifikation im Spiel ist, kein Param-Link | 5 Spalten |
| 9 | Deep of Night | `Enemy HP x1.30` | verglichen womit (normale Expedition) | 4 Zeilen × 5 Spalten |
| 10 | World Events | `stamina recovery speed +5` | Einheit | 1 Ereignis |

**Analyse:** Ein Muster, kein Einzelfall: überall dort, wo eine Zahl aus einem
Param **direkt** durchgereicht wird, wandert der Feldname weg (richtig) und die
Bezugsgröße wandert mit ihm weg (falsch). Wo der Tab dagegen selbst rechnet
(Red variants, Chance-Spalten), steht die Bezugsgröße in einem Erklärsatz da —
der Red-variants-Tab macht es vor: *„The figures are how many red variants of
each sort a run puts on the selected map."*

**Sonderfall 7:** Hier ist die Bezugsgröße **auch im Code nicht bekannt**. Das
ist der Fall, für den A7 die Hausregel hat: sagen, dass man es nicht weiß,
statt es wegzulassen. Heute steht die Zahl kommentarlos da.

**Auswirkung:** Betrifft die meistgesehene Zeile des Programms (Punkt 1) und
die Kopfzahl des meistbesuchten Vergleichs (Punkt 7).

**Vorschlag:** Eine Regel je Tab, nicht je Zeile: die drei erklärenden Tabs
(Deep of Night, Red variants, World Events) haben ein Muster, das trägt — ein
kurzer Erklärsatz unter der Überschrift. Für Punkt 7 zusätzlich eine
A7-Entscheidung des directors: benennen als unbekannt, oder im Spiel messen.

---

### [P2 | Major | Hoch] QA-129 — Die Debuff-Zahlen im Nightlords-Panel stehen bei Bossen, deren Daten sie nicht kennen, und fehlen bei den beiden, deren Daten sie tragen

**Adressat:** developer, ui-ux-designer (Herkunftsfarbe)
**Betroffen:** `nrplanner/bosstab.py:59` (`DEBUFF_ON_BREAK`), `:576-588` (Ausgabe)
**Umgebung:** Nightlords, Detailpanel

**Reproduktion:**
1. Nightlords öffnen, Karte `Caligo` anklicken.
2. Unter `WEAKNESS SPECIAL INTERACTION` steht `Debuff x2.0 damage taken` und
   `Debuff x0.8 attack power`.
3. Karte `Harmonia` anklicken: keine solche Zeile.

**Erwartet:** Zahlen, die zu dem Boss gehören, bei dem sie stehen.
**Tatsächlich:** `DEBUFF_ON_BREAK` ist eine feste Menge aus drei Namen; die
beiden Zahlen sind Konstanten im Quelltext.

**Analyse — gegen `ladder.down` aller zehn Bosse gemessen:**

| Boss | `ladder.down` Angriff | zeigt `x0.8 attack power`? |
|---|---|---|
| Gladius | **0,815** | ja (Zahl weicht ab) |
| Caligo | **keine** | ja |
| Heolstor the Nightlord | **keine** | ja |
| Harmonia | **0,8** | nein |
| Straghess | **0,8** | nein |
| Adel / Gnoster / Libra / Fulghor | 0,917 / 0,846 + 0,957 / 0,957 / 0,88 | nein |

Der handgetippte Wert 0,8 steht also bei drei Bossen, von denen zwei **gar
keinen** Down-Wert in den Daten haben, und fehlt bei den beiden, deren Daten
exakt 0,8 sagen. `x2.0 damage taken` hat im Datensatz überhaupt keine
Entsprechung. Zusätzlich: **`ladder["down"]` wird nirgends gerendert** — 7 von
10 Bossen tragen eine belegte Schwächungsstufe, die der Tab nicht zeigt.
**Herkunftsdarstellung:** Der Tab führt eigens `OBSERVED_COLOUR` („watched in
play: above a wiki claim, below a param read") und benutzt sie für
`WEAKNESS_NOTE` — die Debuff-Zeilen sind in derselben Typografie wie
extrahierte Werte gesetzt. Dasselbe gilt für `Stacks: yes — repeats compound`,
das im Datensatz nicht vorkommt.

*Hypothese, ausdrücklich als solche gekennzeichnet:* Die drei Namen in
`DEBUFF_ON_BREAK` sind Sichtungen und beziehen sich womöglich auf einen
anderen Mechanismus als die `ladder.down`. Dann ist der Befund nicht „falsche
Zahl", sondern „zwei Größen im selben Panel ohne Unterscheidung" — die
Konsequenz für den Leser ist dieselbe.

**Auswirkung:** Ein Spieler entscheidet anhand dieser Zeile, ob sich das
Brechen der Stance lohnt — und bekommt die Antwort bei drei Bossen ohne
Datengrundlage und bei zwei Bossen gar nicht.

**Vorschlag:** Die Down-Stufe aus den Daten zeigen, wo sie existiert; die
gesichteten Zeilen in `OBSERVED_COLOUR` setzen; die Kopplung Name → Konstante
durch eine Kopplung Effekt-Id → Sichtung ersetzen, wie es `DEFENCE_TRIGGER`
bereits richtig macht (dort geprüft: Libra 45852 ist vorhanden, Treffer).

---

### [P3 | Major | Mittel] QA-130 — Maris zeigt `Refills at x-1`

**Adressat:** developer
**Betroffen:** `nrplanner/bosstab.py:611-613`
**Umgebung:** Nightlords, Karte Maris

**Reproduktion:**
1. Nightlords öffnen, `Maris` anklicken.
2. Abschnitt `STANCE`: `Refills at  x-1`.

**Erwartet:** eine Rate oder gar keine Zeile.
**Tatsächlich:** `-1` ist ein Sentinel-Wert („kein Wert"), der als
Multiplikator gedruckt wird. Gemessen: `stance.recovery = -1.0` genau bei
Maris; die übrigen neun liegen zwischen 0,154 und 1,462.

**Analyse:** `if "recovery" in stance` prüft nur die Anwesenheit des
Schlüssels, nicht die Gültigkeit des Werts. Dieselbe Klasse wie `Madness
immune` in der Statusliste, wo `>= 999` **richtig** abgefangen wird — der
Wächter existiert also im selben Modul, nur für das andere Feld.

**Auswirkung:** Eine unmögliche Zahl auf dem Bildschirm; bei einem Boss, der
ohnehin als einziger keinen Selbstbuff hat, wirkt das Panel defekt.

**Vorschlag:** Sentinel wie bei `immune` behandeln — Zeile weglassen oder
ausdrücklich als „nicht in den Dateien" ausweisen (A7).

---

### [P3 | Major | Mittel] QA-131 — Adel ist der einzige Nightlord mit reiner Status-Schwäche; sein gesamter Schwächen-Abschnitt samt der dafür geschriebenen Notiz erscheint nie

**Adressat:** developer (unerreichbarer Zweig), ui-ux-designer (Farbe ohne Legende)
**Betroffen:** `nrplanner/bosstab.py:558-573` (`if weak:` umschließt auch `WEAKNESS_NOTE`), `:66-77`
**Umgebung:** Nightlords, Karte Adel

**Reproduktion:**
1. Nightlords öffnen, `Adel` anklicken.
2. Das Panel beginnt direkt mit `DAMAGE TAKEN`. Es gibt keinen Abschnitt
   `WEAKNESS SPECIAL INTERACTION` und keinen Hinweis, wie man Adel bricht.

**Erwartet:** Der Tab verspricht in seinem Kopf *„click a card for damage
taken, status buildup and more"* und liefert bei neun Bossen einen
Schwächen-Abschnitt.
**Tatsächlich:** `weak_damage` ist bei Adel leer, also wird der ganze Block
übersprungen — und mit ihm die im Quelltext hinterlegte Sichtung *„Phase 1
only — the poison stagger is gone in phase 2 and in the Everdark version."*,
die nie auf den Bildschirm kommt.

**Analyse:** Adel hat sehr wohl eine Schwäche, nur eine andere Art:
`weak_status = ['Frostbite', 'Poison', 'Scarlet Rot', 'Sleep']`. Die
Statusliste färbt diese Einträge grün — **aber keine Legende sagt, was Grün
bedeutet**. Der einzige Ort, an dem der Tab das Wort „weakness" erklärt, ist
genau der Abschnitt, der bei Adel fehlt.

**Auswirkung:** Für 1 von 10 Nightlords beantwortet der Tab seine Kernfrage
nicht, und die Antwort liegt im Programm.

**Vorschlag:** Den Abschnitt an „hat irgendeine Schwäche" hängen statt an
`weak_damage`, und die grüne Markierung der Statusliste einmal benennen.

---

### [P2 | Major | Hoch] QA-132 — Die Spalte `For example` ignoriert die gewählte Karte und ist für die größte Zeile leer

**Adressat:** developer, ui-ux-designer
**Betroffen:** `nrplanner/depthstab.py:167-175` (`_examples`), `:44-56` (`PLAYER_GROUPS`)
**Umgebung:** Red variants, alle sechs Karten

**Reproduktion:**
1. Red variants öffnen. Karte `Default Limveld`.
2. Zeile `Named field enemies & minibosses`, Spalte `For example`:
   `Golden Hippopotamus, Horned Warrior, Grave Warden Duelist …`
3. Karte auf `Great Hollow` umstellen. **Dieselbe** Zeichenkette.
4. Zeile `Ordinary enemies in camps & ruins` (32–38 Stück, die größte Gruppe
   auf jeder Karte): Spalte leer, auf jeder Karte.

**Erwartet:** Die Tabelle sagt über sich selbst *„how many red variants of each
sort a run puts on the selected map"* — die Beispiele sollten zur Karte passen.
**Tatsächlich:** `_examples` liest `self.kinds`, und die Rosterstruktur hat
überhaupt keine Kartendimension (`kind 101` trägt nur `chrs`, `rows`, `tiles`).

**Analyse:** Zwei getrennte Mängel mit einer Wurzel — die Spalte wird aus einer
Quelle gefüllt, die die Frage der Tabelle nicht kennt. Gemessene benannte
Mitglieder je Zeile: `Ordinary enemies` **0**, `Named field enemies` 5,
`Evergaol bosses` 4, `Night bosses` 3, `Merchants` 1, `Unidentified` 0. Die
Spalte ist also für zwei von sechs Zeilen strukturell leer und für die
restlichen vier kartenblind.

**Auswirkung:** Ein Spieler auf Great Hollow liest Namen, die dort
möglicherweise nicht vorkommen — die Spalte behauptet mehr, als die Daten
tragen. Für die größte Zeile beantwortet der Tab „was kann rot sein" gar nicht.

**Vorschlag:** Entweder die Rosternamen an die Kartengruppe binden (falls die
Daten das hergeben) oder die Spalte als kartenunabhängige Erklärung
kennzeichnen, statt sie neben kartenabhängige Zahlen zu stellen. Für die leere
Zeile gilt A7: sagen, dass die Dateien keine Namen liefern.

---

### [P2 | Major | Hoch] QA-133 — Einmalige Belohnungen werden mit einer Dauer gedruckt: `10,000 runes for 1s`

**Adressat:** developer
**Betroffen:** `nrplanner/eventstab.py:216-221`
**Umgebung:** World Events, `Plague of Locusts / Sentient Pest` und
`Fire-Summoning Beasts`

**Reproduktion:**
1. World Events öffnen, `Plague of Locusts / Sentient Pest` wählen.
2. Abschnitt `WIN`, zweite Zeile: `▸ 10,000 runes for 1s`.
3. `Fire-Summoning Beasts` wählen: `restores 100 stamina for 0.3s`.

**Erwartet:** eine Belohnung oder eine Dauer, nicht beides verrechnet.
**Tatsächlich:** `part["duration"]` wird unbesehen als Wirkdauer angehängt.
Gemessen: Buff 8970010 hat `part.duration = 1.0` mit
`lines = ['10,000 runes']`; Buff 8970050 hat `part.duration = 0.3` mit
`lines = ['restores 100 stamina']`.

**Analyse:** Bei einem Effekt, der einen Betrag **gewährt**, ist die
Param-Dauer ein technisches Fenster, keine Aussage für den Spieler. Beim
Nachbarfall stimmt die Regel: `invulnerable for 5s` (Cold Mirage,
`duration = 5.0`) ist richtig. Der Code unterscheidet nicht zwischen einer
Wirkdauer und einem Auslösefenster.
**Zweiter Fall derselben Zeile:** Beim `Judgment`-Buff hat `invulnerable`
`duration = 0.0` und `+10% attack power` `duration = 45.0`; auf dem Bildschirm
steht `invulnerable · +10% attack power, all damage types for 45s` — die
Unverwundbarkeit steht dort ohne jede Dauer, während sie beim anderen
Ereignis eine bekommt.

**Auswirkung:** „10 000 Runen für 1 Sekunde" ist die einzige Zeile der sechs
Tabs, die ein Spieler mit Sicherheit falsch versteht.

**Vorschlag:** Dauern nur an Zeilen hängen, die einen Zustand beschreiben, und
0-Dauern nicht stillschweigend als „keine Angabe" behandeln.

---

### [P3 | Minor | Hoch] QA-134 — Zwei Sätze stehen wörtlich auf allen elf Ereignissen, und die Tagesverteilung, die die Daten hergeben, wird dabei verworfen

**Adressat:** ui-ux-designer, developer
**Betroffen:** `nrplanner/eventstab.py:186-193`
**Umgebung:** World Events, alle extrahierten Ereignisse

**Reproduktion:**
1. World Events öffnen, alle elf extrahierten Einträge durchklicken.
2. Unter der Prozentzeile steht jedes Mal: *„Can fire on Day 1 or Day 2. Every
   other Nightlord: never. The percentage is how much of that Nightlord's map
   pool carries the event."*

**Erwartet:** Ein Satz, der zwischen den Ereignissen unterscheidet.
**Tatsächlich:** Der erste Teilsatz ist auf 11 von 11 identisch, weil jedes
Ereignis `day1 ≥ 2` **und** `day2 ≥ 1` hat. Die Verteilung dahinter ist stark
ungleich: `Judgment` 19 Day-1- gegen 1 Day-2-Muster; `Fire-Summoning Beasts` 9
gegen 21; `Flame of Frenzy` 2 gegen 12.

**Analyse:** Die drei Zweige `Day 1 or Day 2 / Day 1 / Day 2` sind so gebaut,
dass nur der erste je erreicht wird. Der Zweig verliert die Information, statt
sie zu zeigen.
**Zweiter Punkt derselben Zeile (A12):** *„Every other Nightlord: never."* ist
eine Allaussage über zehn Nightlords, gestützt auf die extrahierten
Kartenmuster; der Bildschirm sagt nicht, worauf sie beruht. Und der Extraktor
schreibt ausdrücklich, die Musterziehung sei **gewichtet** und die Zahl
deshalb *„the composition of the pool … not a spin probability"* — auch das
steht nicht auf dem Bildschirm, obwohl A12 „was sie **nicht** deckt" verlangt.

**Auswirkung:** Ein Spieler, der wissen will, ob ihn `Judgment` an Tag 2 noch
treffen kann, bekommt „ja" statt „so gut wie nie".

**Vorschlag:** Die Tagesverteilung zeigen (die Zahlen liegen im Datensatz) und
den Geltungsbereich der Prozentzahl in einem Halbsatz nennen.

---

### [P3 | Minor | Mittel] QA-135 — Herleitungs- und Quellensprache steht auf dem Bildschirm, gegen die selbst formulierte Regel des Tabs; zwei geladene Felder, die die offene Frage beantworten würden, werden nie gezeigt

**Adressat:** ui-ux-designer, developer
**Betroffen:** `nrplanner/eventlore.py` (Felder `note`, `uncertain`,
`conflict`), `nrplanner/eventstab.py:74,78` (`self.unknowns`,
`self.rune_scaling` — geladen, nie benutzt)
**Umgebung:** World Events

**Reproduktion:**
1. `Giant Bubbles / Augur` wählen. Letzte Zeile: *„Sources disagree: The
   passive is called Unifying Fate by fextralife and Undying Fate by game8.
   Eldenpedia labels this event's creature as the Sentient Pest …"*
2. `Difficult Sorcerer's Rise` wählen: *„… catalogued in thefifthmatt's
   per-pattern dump. It is pattern modifier 230, the row this project had
   wrong …"*

**Erwartet:** Der Modulkopf von `eventstab.py` schreibt die Regel selbst:
*„Everything about *how* any of it was derived stays in the project's
documents — none of it belongs on screen."*
**Tatsächlich:** Wiki-Namen, „pattern modifier 230" und „the row this project
had wrong" stehen auf dem Bildschirm. Gleichzeitig trägt jeder Lore-Eintrag ein
Feld `sources`, das **nicht** angezeigt wird — die Quellenangabe ist also
strukturiert vorhanden und leckt trotzdem durch den Fließtext.

**Analyse:** Zwei Seiten derselben Sache. Dazu passend: `rune_scaling` (drei
Sätze, die genau die auf dem Bildschirm stehende Behauptung *„rises the more
expeditions you have cleared"* beziffern) und `unknowns` werden im Konstruktor
geladen und nirgends verwendet.

**Auswirkung:** Ein Spieler ohne Codekontext liest Projektinterna; die
quantifizierte Antwort auf die einzige unbezifferte Behauptung des Tabs bleibt
im Datensatz liegen.

**Vorschlag:** Entweder die Regel des Moduls durchsetzen (Fließtext ohne
Quellennamen, `sources` als eigenes, ruhiges Element) oder die Regel ändern —
das ist eine Entscheidung des ui-ux-designers, nicht meine.

---

### [P4 | Minor | Mittel] QA-136 — Der `Scale-Bearing Merchant` steht zweimal in der Ereignisliste

**Adressat:** ui-ux-designer, director (Inhaltsentscheid)
**Betroffen:** `nrplanner/eventlore.py` (`LORE` zu `log_id 11130` und
`UNANNOUNCED`)
**Umgebung:** World Events, Liste links

**Reproduktion:**
1. `Curse of the Demon / Libra, Creature of Night` wählen. Unter `WHAT HAPPENS`:
   *„It is the Scale-Bearing Merchant: you can trade with it, pay it off, or
   attack it …"*
2. In der Liste weiter nach unten: eigener Eintrag `Scale-Bearing Merchant`
   (blau, community-berichtet) mit einer anderen Beschreibung.

**Erwartet:** eine Sache, ein Eintrag — oder eine sichtbare Verbindung.
**Tatsächlich:** zwei Listeneinträge, die dieselbe Kreatur beschreiben, ohne
aufeinander zu verweisen.

**Analyse:** Die Liste mischt zwei Ordnungen: extrahierte Ereignisse nach
`log_id` und community-berichtete Phänomene nach Name. Der Merchant fällt in
beide.

**Auswirkung:** gering, aber die Liste ist das Navigationselement des Tabs.

**Vorschlag:** Entscheiden, ob das eine Sache oder zwei sind — das ist ein
Inhaltsentscheid, kein Fix.

---

### [P2 | Major | Hoch] QA-137 — Fünf der sechs Tabs haben keinen Test, der bemerken würde, wenn sie Unsinn anzeigen

**Adressat:** developer, director (Priorisierung)
**Betroffen:** `tests/` insgesamt; betroffene Module `effectstab.py`,
`deeptab.py`, `depthstab.py`, `eventstab.py`, `eventlore.py`, inhaltlich auch
`bosstab.py`
**Umgebung:** `-m "not slow"`, Snapshot gesetzt

**Reproduktion (Gegenbau, alle sieben Mutationen gleichzeitig in einem frischen Klon):**

| # | Modul | Mutation | Was ein Spieler sähe |
|---|---|---|---|
| M1 | `deeptab.py` | `WIN_RATING = 200` → `999` | „Win +999" in allen fünf Spalten |
| M2 | `deeptab.py` | `saReceiveDamageRate` und `staminaAttackRate` vertauscht | genau die Verwechslung, die der Code im Kommentar als schon einmal passiert beschreibt |
| M3 | `depthstab.py` | Kategorie 160 in die Zeile der gewöhnlichen Gegner verschoben | Evergaol-Zeile verschwindet, alle Zeilenwerte kippen |
| M4 | `effectstab.py` | `format_chance` mal 1000 statt 100 | jede Prozentzahl zehnfach |
| M5 | `eventstab.py` | Gating-Satz sagt `Fires on Day 2 only` | falsche Aussage auf allen elf Ereignissen |
| M6 | `bosstab.py` | `x2.0`→`x9.9`, `x0.8`→`x0.1` | falsche Debuff-Zahlen bei drei Bossen |
| M7 | `arsenaltab.py` | Zusammenfassung: „base" → „raw base" | Definition der Kopfzahl verändert |

**Erwartet:** mindestens ein roter Test.
**Tatsächlich:** **622 passed, 5 deselected** — bitgleich zum Ausgangslauf.

**Kontrolle (L-007, damit „grün" nicht „Harness kaputt" heißt):** dieselbe
Klontechnik, eine Mutation, die getroffen werden **muss** — `arsenaltab`
übergibt `rank_candidates` eine Aufstiegsstufe zu viel. Ergebnis:
**6 failed, 2 passed** in `test_arsenal_tab_asks_the_facade.py` und
`test_arsenal_tab_wiring.py`. Die Strecke funktioniert; die Lücke ist echt.

**Suchbelege (L-006, je zwei unabhängige Masken):**
Modulnamen `effectstab|deeptab|depthstab|eventstab|eventlore` in `tests/` →
**0 Treffer**. Klassennamen `EffectsTab|DeepTab|DepthsTab|WorldEventsTab` →
**0 Treffer**. `bosstab`/`BossTab` → 1 Datei
(`test_game_text_is_never_markup.py`), die Markup-Escaping prüft, keinen Inhalt.

**Analyse:** Die Tabs **laufen** in der Suite (jeder `planner`-Fixture-Test
baut sie über `appmod.Planner`), also fängt die Suite einen Absturz. Sie prüft
aber keine einzige angezeigte Zahl oder Zeichenkette dieser fünf Module. Das
ist dieselbe Klasse wie QA-123, eine Ebene höher: dort war die Messstrecke für
sechs Waffen blind, hier ist sie für fünf ganze Tabs blind.

**Auswirkung:** Jeder Befund QA-125 bis QA-136 konnte entstehen und bestehen
bleiben, ohne dass etwas rot wurde. Solange das so ist, sagt „Suite grün" über
diese Tabs nichts.

**Einstufung, begründet:** Severity Major bei hoher Wahrscheinlichkeit ergäbe
P1. Ich stufe **P2** ein, weil kein Nutzer diesen Befund selbst auslöst — er
ist die Ursache der anderen, nicht ein eigener Schaden. Für den director ist
er trotzdem der wichtigste der Liste.

**Vorschlag:** Kein voller Testaufbau für fünf Tabs. Ein
Charakterisierungstest je Tab, der den sichtbaren Text gegen eine
aufgezeichnete Fassung hält, würde alle sieben Mutationen fangen — die
`golden`-Technik des Projekts existiert bereits und ist erprobt.

---

### [P3 | Minor | Hoch] QA-138 — Drei der sechs Tabs sagen nicht, welche Frage sie beantworten; die anderen drei tun es (A10)

**Adressat:** ui-ux-designer
**Betroffen:** `effectstab.py` (nur `self.summary`), `arsenaltab.py` (nur
`self.summary`), `bosstab.py` (nur `self.summary`) gegen `deeptab.py:105`,
`depthstab.py:82`, `eventstab.py:96` (jeweils `_heading` + Einführungsabsatz)
**Umgebung:** alle sechs Tabs, Erstöffnung

**Reproduktion:**
1. `Deep of Night` öffnen: Überschrift `WHAT EACH DEPTH IS WORTH`, darunter
   erklärende Absätze. Ebenso `Red variants` (`RED VARIANTS BY DEPTH` + zwei
   Absätze) und `World Events` (`WORLD EVENTS` + Absatz).
2. `Effects & chances` öffnen: erste Textzeile ist
   `577 buffs (blue) then 75 curses (red). …` in Grau, 11 px.
3. `Weapons & spells`: `Wylder at level 1, +1 — VIG 10 MIN 4 …`.
4. `Nightlords`: `10 Nightlords · 8 also have an Everdark Sovereign …`.

**Erwartet:** A10 — *„ein Spieler kann sie am Tab selbst ablesen, ohne sie
erraten zu müssen."*
**Tatsächlich:** Bei drei Tabs beginnt der Inhalt mit einer Zählung des
Bestands statt mit der Frage. Die Zusammenfassungszeilen erklären danach
durchaus etwas — aber erst, nachdem der Leser selbst erschlossen hat, wozu der
Tab da ist.

**Analyse:** Kein Fehler, sondern eine ungleiche Konvention: die drei später
gebauten Tabs haben ein Kopfmuster, die drei älteren nicht.

**Auswirkung:** Direkt auf A10 und indirekt auf A13 (gestalterische
Konsistenz), die der `ui-ux-designer` ohnehin führt.

**Vorschlag:** Das vorhandene Muster der drei erklärenden Tabs übernehmen.
Kein neuer Inhalt — nur die Frage, die der Tab ohnehin beantwortet, einmal
hinschreiben.

---

### [P4 | Trivial | Hoch] QA-139 — Derselbe Wert heißt auf einem Bildschirm zweimal anders: `Spell power` auf der Kachel, `spell scaling` in der Zusammenfassung

**Adressat:** ui-ux-designer (AK-34/AK-64 regeln diese Zeichenkette)
**Betroffen:** `nrplanner/arsenaltab.py:318-324` (Zusammenfassung) gegen
`rating.headline_label` auf der Kachel
**Umgebung:** Weapons & spells, Suche nach einem Stab- oder Siegelnamen

**Reproduktion:**
1. Weapons & spells öffnen, `Carian Regal Scepter` suchen.
2. Kachel: `Spell power  145`.
3. Zusammenfassung darüber: *„Staves and seals show the **spell scaling** the
   game displays for them instead of an attack rating."*

**Erwartet:** ein Name für eine Größe.
**Tatsächlich:** zwei, sechs Zeilen voneinander entfernt.

**Analyse:** Beim Schließen von QA-121/DR-010 ist die Kachelbeschriftung
(T-046) und der Zusammenfassungssatz (T-053) aus zwei Richtungen gekommen. Der
Satz ist inhaltlich richtig — er benennt nur nicht den Ausdruck, der auf der
Kachel steht. **Kein Widerspruch, nur ein Bezeichnungswechsel.**

**Auswirkung:** Minimal, aber es ist genau die Zeile, die AK-34 unter
Wortlautkontrolle stellt.

**Vorschlag:** Einen der beiden Ausdrücke wählen. AK-34-Sache.

---

# Die Streichliste, je Tab

Priorisiert; jeder Eintrag mit dem Satz, was ein Spieler verliert. **Die
Entscheidung trifft der App Designer, nicht QA** (GOAL A10).

## Effects & chances

1. **Spalte `Pools`.** Ihr eigener Tooltip sagt: *„More pools does not mean
   more likely — the two chance columns say that."*
   *Wenn das weg ist, verliert ein Spieler* nichts, was er benutzen kann —
   **außer** dem heutigen 0-Signal „unter diesen Filtern nicht erreichbar".
   Das müsste in die Chance-Zellen wandern, die dafür schon einen Tooltip
   haben. (Voraussetzung: QA-125 ist entschieden.)
2. **Spalte `Copies`.** 638 von 652 Zeilen zeigen `1`.
   *Wenn das weg ist, verliert ein Spieler* die Information, dass 14 Effekte
   im Spiel mehrfach definiert sind — was an keiner Rolle etwas ändert.
3. **Spalte `Type`.** Die Farbe sagt es bereits auf Name und Beschreibung.
   *Wenn das weg ist, verliert ein Spieler* die Sortierung, die heute Buffs und
   Flüche gruppiert — die müsste ersetzt werden, sonst ist der Verlust größer
   als der Gewinn. **Nur streichen, wenn die Gruppierung anders erhalten
   bleibt.**
4. **Spalte `Best chance` in ihrer heutigen Form.** 182 von 652 Zeilen zeigen
   `100.0%`, ohne zu sagen, auf welchem Relikt.
   *Wenn das weg ist, verliert ein Spieler* die Spannweite zwischen bestem und
   mittlerem Fall bei den übrigen ~470 Zeilen — die ist echt. Das ist ein
   „beantwortbar machen", kein sauberer Schnitt.

## Weapons & spells

1. **Die Wiederholung der Kopfzahl bei einschichtigen Waffen.** 655 von 1 792
   Kacheln drucken `AR 49` und darunter `Physical 49`.
   *Wenn das weg ist, verliert ein Spieler* nichts — die Typzeile verdient
   ihren Platz erst ab zwei Schadensarten.
2. **Zeile `Slots` auf Zauberkacheln.** 160 von 160 zeigen `1`.
   *Wenn das weg ist, verliert ein Spieler* nichts; sollte das Spiel je einen
   Zauber mit zwei Plätzen bekommen, müsste die Zeile zurück.
3. **Nicht streichen: `vs standard`.** Erscheint nur auf Infusionen und ist die
   einzige Zeile, die den Unterschied zur Standardfassung beziffert.

## Nightlords

1. **Der Klammerzusatz `(smallest Harmonia 75, largest Caligo 160)`** auf allen
   zehn Panels.
   *Wenn das weg ist, verliert ein Spieler* die Skala für „Bar to break" —
   also: einmal an den Tab, nicht zehnmal ins Panel.
2. **`Stacks: yes — repeats compound`** und **`harder to stagger`**: auf jedem
   Boss identisch, ersteres ohne Datengrundlage.
   *Wenn das weg ist, verliert ein Spieler* die Aussage, dass sich Buffs
   stapeln — die gehört einmal in den Tabkopf, nicht in jedes Panel.
3. **Abschnitt `BODY PARTS`** in seiner heutigen Form (`Part 2 · x0.6 damage —
   armoured`).
   *Wenn das weg ist, verliert ein Spieler* die Information, dass Caligo vier
   gepanzerte Stellen hat — die er ohne Körperteilnamen nicht anwenden kann.
   Der Abschnitt wird wertvoll, sobald `PART_NAMES` gefüllt ist, und ist bis
   dahin ein Kandidat.
4. **Nicht streichen: der `EVERDARK`-Block.** Die Behauptung „identisch" ist
   **geprüft und wahr für 8 von 8** — sie erspart dem Spieler das Nachschlagen
   einer zweiten Tabelle.

## Deep of Night

1. **Die Zeile `Win` mit fünf identischen `+200`.**
   *Wenn das weg ist, verliert ein Spieler* nichts — ein Satz „Ein Sieg bringt
   in jeder Tiefe +200" sagt dasselbe und sagt zusätzlich, dass es nicht von
   der Tiefe abhängt.
2. **Die Zeilen `Cursed relic — Uncommon` und `— Rare`** aus der Tiefentabelle.
   25 % / 40 %, konstant über alle fünf Spalten; die Note darunter sagt das
   bereits.
   *Wenn das weg ist, verliert ein Spieler* zwei echte Zahlen — also:
   **verschieben**, nicht löschen.
3. **`Map concealed` und `Nightlord obscured` als zwei Zeilen.** Immer paarweise
   0/0/10/10/10.
   *Wenn das weg ist, verliert ein Spieler* die Unterscheidung, welches von
   beidem passiert — die ist relevant. Eine Zeile „Karte **oder** Nightlord
   verborgen: 0/0/20/20/20" plus die vorhandene Note sagt mehr auf weniger
   Platz.

## Red variants

1. **Spalte `For example` in ihrer heutigen Form** (QA-132).
   *Wenn das weg ist, verliert ein Spieler* nichts Korrektes — sie ist für die
   größte Zeile leer und für die übrigen kartenblind. Mit Kartenbindung wäre
   sie eine der nützlichsten Spalten der sechs Tabs.
2. **Zwei der fünf Tiefenspalten** (D3 wiederholt D2, D5 wiederholt D4 — auf
   allen sechs Karten und in 22 von 22 Datenzeilen).
   *Wenn das weg ist, verliert ein Spieler* die Möglichkeit, „Depth 3" direkt
   nachzuschlagen. Also **markieren statt streichen**: „gleich wie Depth 2"
   ist eine Aussage, fünf identische Zahlen sind keine.
3. **Nicht streichen: `Night bosses (unconfirmed)`.** Eine Zeile mit Zahlen für
   etwas, das nie gesichtet wurde, mit genau diesem Wort im Titel — das ist A7,
   wie es aussehen soll.

## World Events

1. **`Can fire on Day 1 or Day 2.`** Wörtlich gleich auf 11 von 11.
   *Wenn das weg ist, verliert ein Spieler* nichts — er verliert erst dann
   etwas, wenn auch die Tagesverteilung wegbleibt, die heute schon verworfen
   wird (QA-134).
2. **`Every other Nightlord: never.`** Ebenfalls auf 11 von 11.
   *Wenn das weg ist, verliert ein Spieler* die Zusicherung, dass die Liste
   vollständig ist. Die ist wertvoll — aber nur mit ihrem Geltungsbereich, und
   den trägt sie heute nicht.
3. **Die Quellennamen in den `Sources disagree`-Blöcken.**
   *Wenn das weg ist, verliert ein Spieler* nichts, was er benutzen kann; die
   Aussage „hier widersprechen sich die Quellen" bleibt und ist das, was ihn
   angeht.
4. **Nicht streichen: `WHAT THE DEMON CAN DO`** (die sieben Angebotszeilen).
   Das ist der einzige Ort im Programm, an dem eine Spielentscheidung mit
   sieben Ausgängen vollständig aufgelistet ist.

---

# Einschätzung je Tab gegen A10, A12 und A14

| Tab | A10 (benennbare Frage, ablesbar) | A12 (Einheit und Geltungsbereich) | Begründung |
|---|---|---|---|
| **Effects & chances** | **teilweise** | **nicht erfüllt** | Die Frage wird beantwortet, steht aber nicht am Tab (QA-138). Zwei der drei Zahlenspalten bedeuten nicht, was ihre Beschriftung sagt (QA-125, QA-126); zwei weitere Spalten ändern sich mit den Filtern, obwohl sie als Dateneigenschaft beschrieben sind (QA-127). |
| **Weapons & spells** | **teilweise** | **nicht erfüllt** | Die Frage wird gut beantwortet, steht aber nicht am Tab (QA-138). Die Zeile `Scaling` steht auf allen 1 792 Kacheln ohne Einheit und ohne Skala (QA-128, Punkt 1); dazu drei weitere Zeilen ohne Bezug. |
| **Nightlords** | **teilweise** | **nicht erfüllt** | Für 9 von 10 Bossen beantwortet, für Adel gar nicht (QA-131). Drei Zahlenblöcke ohne Einheit oder Richtung (QA-128, Punkte 4–6); eine unmögliche Zahl (QA-130); handgetippte Werte ohne Herkunftsmarkierung bei den falschen Bossen (QA-129). |
| **Deep of Night** | **erfüllt** | **teilweise** | Der Tab benennt seine vier Fragen als Überschriften und beantwortet sie in der Reihenfolge, in der ein Spieler sie stellt. Die Herkunftszeilen sind vorbildlich. Drei Bezugsgrößen fehlen, davon eine (`Reward multiplier`), die auch im Code nicht bekannt ist und deshalb nach A7 benannt gehört (QA-128, Punkte 7–9). |
| **Red variants** | **erfüllt** | **teilweise** | Frage und Einheit stehen ausdrücklich am Tab (*„how many red variants … a run puts on the selected map"*) — das ist das beste Beispiel der sechs. Der Geltungsbereich stimmt aber für die Spalte `For example` nicht (QA-132). |
| **World Events** | **erfüllt** | **teilweise** | Frage benannt, Herkunftsklassen konsequent getrennt. Eine sinnfreie Einheit (QA-133), eine Zusicherung ohne Geltungsbereich und eine verworfene Unterscheidung (QA-134), eine unbezifferte Behauptung neben den geladenen Zahlen (QA-135). |

**A14 — je Tab einzeln bestätigt:** ja. Jeder der sechs Tabs ist oben einzeln
mit den sechs Punkten des Auftrags behandelt, und die Urteile stehen je Tab in
der Tabelle. **Keiner der sechs Tabs erfüllt A12 vollständig.** A10 erfüllen
drei von sechs; die anderen drei beantworten ihre Frage, sagen sie aber nicht.

**Zu A13 und A11:** nicht mein Urteil. A13 verlangt den Nachweis am laufenden
Fenster mit Screenshots — das ist die Strecke des Design-Reviews (T-052,
DR-008 bis DR-012). A11 beantwortet der `power-user`, der parallel läuft.

---

# Zusammenfassung (an den director)

**Befunde nach Priorität:** P1 **0** · P2 **7** (QA-125, QA-126, QA-128,
QA-129, QA-132, QA-133, QA-137 — letzteres mit begründeter Herabstufung von
P1) · P3 **6** (QA-127, QA-130, QA-131, QA-134, QA-135, QA-138) · P4 **2**
(QA-136, QA-139). Gesamt 15. Kein Blocker; der Testlauf ist vollständig
durchgelaufen.

**Gesamteinschätzung.** Die sechs Tabs sind inhaltlich weiter, als ihre
Prüfbarkeit vermuten lässt: die drei jüngeren Tabs (Deep of Night, Red
variants, World Events) benennen ihre Frage, trennen Herkunftsklassen sauber
und sagen an mehreren Stellen ausdrücklich, was sie **nicht** wissen — das ist
A7 in vorbildlicher Form. Der Bruch liegt woanders: **kein Test der Suite
prüft eine einzige angezeigte Zahl auf fünf dieser sechs Tabs** (QA-137,
belegt mit sieben Mutationen bei unverändert 622 grün und einer roten
Kontrollmutation). In genau dieser Lücke sind die drei Befunde entstanden, die
ein Spieler direkt falsch versteht: eine Wahrscheinlichkeitsspalte, die um bis
zu Faktor 22 danebenliegt (QA-126), eine Poolzahl, die größer ist als die Zahl
der Pools, die es gibt (QA-125), und eine Belohnung, die „für 1 Sekunde"
gewährt wird (QA-133).

**Releasefähig?** Für die Inhaltsabnahme nach A10/A12: **nein.** Mindestens
behoben sein müssen vor einer Abnahme:

1. **QA-126 und QA-125** — die beiden Zahlenspalten der Effektetabelle, weil
   sie eine Kernfrage des Programms falsch beantworten;
2. **QA-133** — die einzige Zeile, die mit Sicherheit falsch verstanden wird;
3. **QA-129** — Zahlen, die beim falschen Boss stehen;
4. **QA-128 Punkt 1** — die `Scaling`-Zeile, weil sie auf jeder der 1 792
   Waffenkacheln steht;
5. **QA-137** — ohne einen Charakterisierungstest je Tab ist jede Behebung
   der obigen Punkte nach dem nächsten Refactoring wieder offen.

Die übrigen Befunde und die Streichliste sind Material für den
`ui-ux-designer` und für die Entscheidung des App Designers, nicht für die
Abnahme.

---

# Explorationsprotokoll

**Was ich versucht habe und was gehalten hat:**

- Suite im eigenen Klon: 622 passed, 5 deselected — **hält**, deckt sich mit
  dem Auftrag.
- Alle sechs Tabs headless instanziiert und ihren **gesamten sichtbaren Text**
  ausgelesen (Labels, Tabellenzellen, Rich-Text-Panels, Listeneinträge). Jedes
  Zitat in diesem Bericht stammt daraus.
- Deep-of-Night-Skalierung: Behauptung „die fünf elementaren Raten bewegen sich
  gemeinsam" über alle 25 Profile × 5 Tiefen geprüft — **0 Abweichungen, hält**.
- Deep-of-Night-Kontrollzeilen: `cataclysmWeight_1 + _2 = 100` und
  `mapChallengeWeight_Map/_Nightlord/_None = 10/10/80` geprüft — die beiden
  Erklärnoten sind **korrekt hergeleitet, halten**.
- Everdark-Behauptung „identische Werte": alle 8 Paare byteweise verglichen —
  **8 von 8 identisch, hält**.
- `Avg > Best` auf der Effektetabelle: **0 von 652** — hält.
- Summenbildung im Red-variants-Tab über 6 Karten × 5 Tiefen — **hält**.
- Rundungsverdacht bei `Fire Longsword` (`AR 48` gegen `24 + 23`) verfolgt und
  **fallengelassen**: das ist das in T-045 abgenommene Abschneideverhalten,
  kein Befund.
- Zwei Direktlesungen aus `regulation.bin` (read-only): `AttachEffectTableParam`
  (22 088 Zeilen) und `EquipParamAntique` (1 397 Zeilen), um QA-125 nicht auf
  eine Snapshot-Identität allein zu stützen.
- Suche nach überholten Beschriftungen mit zwei unabhängigen Masken: **kein
  überholter Wortlaut in einer angezeigten Zeichenkette** — hält.
- Sieben Anzeigemutationen gleichzeitig (QA-137) plus eine Kontrollmutation,
  die rot werden musste und rot wurde.

**Werkzeuge:** eigener Klon unter `…\scratchpad\nh-clone` (Messungen) und zwei
Wegwerf-Klone `mut1`/`mut2` (Mutationen). Im Arbeitsbaum ist genau eine Datei
geschrieben worden, diese hier. Kein `push`, `checkout`, `reset`, `clean`,
`stash`. Nie zwei Testprozesse gleichzeitig.

# Offene Fragen

1. **An den director / developer — QA-119 lässt sich nicht mehr auslösen.**
   Der in QA-119 genannte Auslöser (zwei `Recluse's Staff` mit 128 und 151)
   ist auf dem heutigen Datensatz nicht reproduzierbar: `Recluse's Staff`
   kommt genau einmal vor (id 33750000, `Spell power 139`), auf allen vier
   Aufstiegsstufen. Ist QA-119 durch T-046/T-053 geschlossen worden, oder hat
   sich der Datensatz geändert? Die **Klasse** besteht weiter (6 Kacheln mit
   doppeltem Namen, diesmal mit identischen Zahlen), aber die Schwere ist eine
   andere. Ich habe QA-119 deshalb **nicht** angefasst.
2. **An den director — zählt ein roter Händler als „red variant"?** Die Intro
   des Red-variants-Tabs definiert rote Varianten als *„individual empowered
   enemies"*; die Zeile `Merchants` (4–6 Stück je Karte) geht in
   `Total red variants on the map` ein. Beides ist verteidigbar. Ich melde das
   ausdrücklich **nicht** als Befund, weil die Antwort eine Inhaltsentscheidung
   ist.
3. **An den ui-ux-designer — welche Definition der `Avg chance` ist die
   gewollte?** Tooltip („averaged over every pool") und Zusammenfassung („how
   likely … on one roll") sagen Verschiedenes; die Rechnung entspricht
   keiner von beiden ganz. QA-126 kann erst danach richtig behoben werden.
4. **An den ui-ux-designer — gilt die Regel des `eventstab`-Modulkopfs
   („none of it belongs on screen") noch?** Sie wird an mehreren Stellen
   gebrochen (QA-135). Entweder die Regel oder der Text muss nachgezogen
   werden; welches von beidem, entscheide ich nicht.
5. **An den director — `DEBUFF_ON_BREAK` gegen `ladder.down`:** sind das zwei
   verschiedene Spielmechanismen oder zwei Beschreibungen desselben? Davon
   hängt ab, ob QA-129 ein Zahlenfehler oder ein Darstellungsfehler ist.

# Nicht getestet

- **`Build planner`** — laut Auftrag ausgenommen.
- **A11 (kommt ein Mensch ans Ziel)** — läuft parallel beim `power-user`; sein
  Bericht ist nicht meiner, und ich habe ihn bewusst nicht vorweggenommen.
- **A13 am laufenden Fenster (Screenshots, Abschneiden, waagerechte
  Bildlaufleisten)** — Sichtprüfung ist die Strecke des Design-Reviews; T-052
  hat sie am 05.09. gefahren (DR-008 bis DR-012, Screenshots unter
  `docs/screenshots/2026-09-05/`). Ich habe mich darauf verlassen und nur
  stichprobenartig gegengelesen, ob die dort behandelten Zeichenketten heute
  im Baum stehen — ja.
- **QA-096 / QA-097 / QA-113** — warten laut Auftrag auf Messungen im Spiel.
- **QA-116, QA-117, QA-122, QA-123, QA-124** — bekannt, nicht erneut geprüft.
- **Der Berater (S7 bis S11)** — nicht gebaut.
- **Die Eingabeprüfung der Filter- und Suchfelder** (überlange Eingaben,
  Steuerzeichen, Unicode) auf diesen sechs Tabs. Bewusst ausgelassen: T-055
  fragt nach der Wahrheit des Angezeigten, nicht nach der Robustheit der
  Eingabe, und die Suchsyntax ist über `search.parse` an anderer Stelle
  geprüft. **Kandidat für einen eigenen Lauf**, falls der director ihn will.
- **Die Kopplungen der Tabs untereinander.** Der Arsenal-Tab ist der einzige
  der sechs mit einer Kopplung zum `Planner`, und die ist durch
  `test_arsenal_tab_wiring.py` gedeckt (Kontrollmutation rot). Für die anderen
  fünf gibt es keinen geteilten veränderlichen Zustand — sie lesen nur `data`.

---

# QA-Log — Fortschreibung für `qa/findings.md`

`qa/findings.md` ist 1 560 Zeilen lang und in Zyklusabschnitte gegliedert; die
Datei wird vom director geführt. Unten steht der **Anfügeblock** für Zyklus 13
im Format der bestehenden Abschnitte, nicht die ganze Datei. Bestehende
Einträge bleiben unverändert; ich habe an keinem etwas geändert.

```markdown
## Zyklus 13, T-055: Inhaltsaudit der sechs Tabs (2026-09-05)

Quelle: `docs/berichte/T-055-qa-engineer.md`. Grundlage GOAL A10 bis A14.
Alle Zahlen an headless instanziierten Tabs ausgelesen; zwei Belege aus einer
Direktlesung von `regulation.bin`. Suite vor und nach dem Lauf: 622 passed,
5 deselected. Kein Blocker. Keine Doppelmeldung zu DR-008..012,
QA-116/117/119/121/122/123/124.

**Bestaetigt, kein Befund:** die Everdark-Behauptung „identical figures"
(8 von 8 Paaren byteweise gleich) · die Begruendung, die fuenf elementaren
Deep-Raten zu einer Zeile zusammenzulegen (0 Abweichungen ueber 25 Profile x
5 Tiefen) · die beiden Erklaernoten zu Kataklysmen und Verschleierung
(Gewichte summieren zu 100) · `Avg > Best` in 0 von 652 Zeilen · die
Summenbildung im Red-variants-Tab ueber alle 6 Karten.

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| QA-125 | **Effects & chances: die Spalte `Pools` zaehlt keine Pools.** Der Tooltip sagt "How many of the game's loot pools can produce this effect"; die Zahl ist die Summe der (Relikt x Effektplatz)-Vorkommen. Zwei unabhaengige Belege: Identitaet 333 167 + 5 760 = **338 927** exakt aufgegangen; und das Spiel definiert nur **598** verschiedene Pool-Tabellen, waehrend der Tab bis **1 110** anzeigt | P2 | Major | developer, ui-ux-designer | Snapshot-Identitaet + Direktlesung `EquipParamAntique` | offen | 2026-09-05 |
| QA-126 | **Effects & chances: `Avg chance` ist ein ungewichtetes Mittel ueber Farb-/Modus-Eimer** und entspricht weder dem Tooltip ("averaged over every pool") noch der Zusammenfassung ("how likely … on one roll"). **129 von 616** Effekten aendern die angezeigte Zahl bei Gewichtung nach Vorkommen; schlimmster Fall `[Wylder] Improved Mind, Reduced Vigor` **20,4 % gegen 0,91 %** (Faktor 22,3) | P2 | Major | developer, ui-ux-designer | Nachrechnung ueber alle Effekte, Einzelfall aufgeschluesselt | offen | 2026-09-05 |
| QA-127 | **Effects & chances: `Copies` und `Tier` sind filterabhaengig**, obwohl beide Tooltips sie als Eigenschaft der Spieldaten beschreiben. Gemessen gegen "All colours": 25-39 Namen mit anderer `Copies`-Liste, 17-31 Namen, deren Leitersprosse verschwindet. **Entwarnung: keine Umnummerierung, 0 Faelle** ueber vier Farben und beide Modi | P3 | Major | developer | Filterdurchlauf ueber alle Farben und Modi | offen | 2026-09-05 |
| QA-128 | **Systemisch (A12): Zahlen ohne Bezugsgroesse auf fuenf der sechs Tabs.** 10 Belegstellen, u. a. `Scaling STR 50` auf **allen 1 792** Waffenkacheln (Einheit und Skala unbenannt; das Spiel zeigt hier Buchstabengrade), `Refills at x0.846` (Rate ohne Zeitbasis), `STATUS BUILDUP 542` (Richtung und Farblegende fehlen), `Reward multiplier x1.47` (**Bezugsgroesse auch im Code unbekannt -> A7-Fall**), `Enemy HP x1.30` (Vergleichsbasis fehlt) | P2 | Major | ui-ux-designer, developer, director | Belegliste mit Umfang je Stelle | offen | 2026-09-05 |
| QA-129 | **Nightlords: die Debuff-Zahlen stehen bei den falschen Bossen.** `DEBUFF_ON_BREAK` zeigt "x2.0 damage taken / x0.8 attack power" bei Gladius (Daten: 0,815), Caligo (**keine** Down-Stufe) und Heolstor (**keine**) - und **nicht** bei Harmonia und Straghess, deren Daten exakt 0,8 sagen. `ladder["down"]` wird fuer **7 von 10** Bossen nie gezeigt. Die Zeilen tragen die Typografie extrahierter Werte, obwohl der Tab fuer Sichtungen eine eigene Farbe fuehrt | P2 | Major | developer, ui-ux-designer | `ladder.down` aller 10 Bosse gegen die Konstantenliste | offen | 2026-09-05 |
| QA-130 | **Nightlords: Maris zeigt `Refills at x-1`.** `stance.recovery = -1.0` ist ein Sentinel und wird als Multiplikator gedruckt; die uebrigen neun liegen zwischen 0,154 und 1,462. Derselbe Waechter existiert im selben Modul fuer `>= 999` ("immune"), nur nicht fuer dieses Feld | P3 | Major | developer | Wert am Widget und im Datensatz | offen | 2026-09-05 |
| QA-131 | **Nightlords: Adels Schwaechen-Abschnitt erscheint nie.** Er ist der einzige Boss mit leerem `weak_damage` (Schwaeche liegt auf vier Status), und `if weak:` umschliesst auch `WEAKNESS_NOTE['Adel']` - die dafuer geschriebene Sichtung erreicht den Bildschirm nicht. Die gruene Markierung der Statusliste hat **keine Legende**; der einzige Ort, der "weakness" erklaert, ist der fehlende Abschnitt | P3 | Major | developer, ui-ux-designer | alle 10 Panels ausgelesen, `weak_status` gegengeprueft | offen | 2026-09-05 |
| QA-132 | **Red variants: `For example` ignoriert die gewaehlte Karte und ist fuer die groesste Zeile leer.** Identische Beispielnamen auf allen sechs Karten (die Rosterstruktur hat keine Kartendimension); `Ordinary enemies in camps & ruins` (32-38 von 87-134) und `Unidentified enemies` haben **0** benannte Mitglieder. Die Tabelle sagt ueber sich selbst "on the selected map" | P2 | Major | developer, ui-ux-designer | 6 Karten ausgelesen, Roster je Gruppe ausgezaehlt | offen | 2026-09-05 |
| QA-133 | **World Events: einmalige Belohnungen werden mit einer Dauer gedruckt.** `10,000 runes for 1s` (Buff 8970010, `part.duration = 1.0`) und `restores 100 stamina for 0.3s`. Beim Nachbarfall (`invulnerable for 5s`) ist dieselbe Regel richtig; der Code trennt Wirkdauer und Ausloesefenster nicht. Zusatz: beim `Judgment`-Buff steht `invulnerable` ganz ohne Dauer (`duration = 0.0`) | P2 | Major | developer | Buff-Teile aller 7 Buffs gegen den Bildschirmtext | offen | 2026-09-05 |
| QA-134 | **World Events: zwei Saetze stehen woertlich auf allen 11 Ereignissen**, und die Tagesverteilung wird dabei verworfen: `Judgment` hat 19 Day-1- gegen 1 Day-2-Muster, `Fire-Summoning Beasts` 9 gegen 21 - angezeigt wird ueberall "Can fire on Day 1 or Day 2". Dazu (A12): "Every other Nightlord: never" ist eine Allaussage ohne Geltungsbereich, und der Extraktor nennt die Prozentzahl ausdruecklich "not a spin probability" - das steht nicht auf dem Bildschirm | P3 | Minor | ui-ux-designer, developer | Gating-Daten aller 11 Ereignisse | offen | 2026-09-05 |
| QA-135 | **World Events: Herleitungssprache auf dem Bildschirm, gegen die Regel des eigenen Modulkopfs.** Wiki-Namen (fextralife, game8, Eldenpedia, thefifthmatt), "pattern modifier 230", "the row this project had wrong". Gleichzeitig werden `self.unknowns` und `self.rune_scaling` geladen und **nie** angezeigt - letzteres beziffert genau die auf dem Bildschirm stehende Behauptung "rises the more expeditions you have cleared" | P3 | Minor | ui-ux-designer, developer | Bildschirmtext gegen Modul-Docstring, Feldnutzung | offen | 2026-09-05 |
| QA-136 | **World Events: der `Scale-Bearing Merchant` steht zweimal in der Liste** - einmal als eigener community-berichteter Eintrag, einmal als Aufloesung von `Curse of the Demon` ("It is the Scale-Bearing Merchant"), ohne Verweis aufeinander | P4 | Minor | ui-ux-designer, director | Listeninhalt und beide Detailtexte | offen | 2026-09-05 |
| QA-137 | **Fuenf der sechs Tabs haben keinen Test, der Unsinn bemerken wuerde.** Sieben Anzeigemutationen gleichzeitig (u. a. Prozente zehnfach, Boss-Debuff x9.9, `WIN_RATING` 999, vertauschte Deep-Zeilen, falsches Tages-Gating) -> **622 passed, 5 deselected, unveraendert**. Kontrollmutation im Arsenal-Tab -> **6 failed**: die Strecke funktioniert. Suchbelege: Modulnamen 0 Treffer, Klassennamen 0 Treffer in `tests/`. **Herabgestuft von P1 auf P2**, weil kein Nutzer den Befund selbst ausloest - er ist die Ursache von QA-125 bis QA-136 | P2 | Major | developer, director | 7 Mutationen + 1 Kontrollmutation in frischen Klonen | offen | 2026-09-05 |
| QA-138 | **Drei der sechs Tabs sagen nicht, welche Frage sie beantworten** (A10). Deep of Night, Red variants und World Events oeffnen mit Ueberschrift und Erklaerabsatz; Effects & chances, Weapons & spells und Nightlords oeffnen mit einer Bestandszaehlung in Grau, 11 px | P3 | Minor | ui-ux-designer | Erstoeffnung aller sechs Tabs | offen | 2026-09-05 |
| QA-139 | **Derselbe Wert heisst auf einem Bildschirm zweimal anders:** die Kachel sagt `Spell power`, die Zusammenfassung sechs Zeilen darueber sagt "the **spell scaling** the game displays for them". Kein Widerspruch, ein Bezeichnungswechsel - entstanden beim Schliessen von QA-121/DR-010 aus zwei Richtungen (T-046 Kachel, T-053 Satz). AK-34 stellt diese Zeichenkette unter Wortlautkontrolle | P4 | Trivial | ui-ux-designer | Bildschirmtext beider Stellen | offen | 2026-09-05 |
```

**Beobachtung ohne eigene Nummer (gehört an QA-119):** der Auslöser aus QA-119
ist auf dem heutigen Datensatz nicht reproduzierbar — `Recluse's Staff` kommt
genau einmal vor (id 33750000, `Spell power 139`), auf allen vier
Aufstiegsstufen. Die Klasse besteht weiter: `Scholar's Thrusting Sword` (4×)
und `Finger Seal` (2×) tragen denselben Namen mehrfach, diesmal mit
**identischen** Zahlen. Ob QA-119 damit geschlossen ist oder sich nur der
Datensatz geändert hat, entscheidet der director.
