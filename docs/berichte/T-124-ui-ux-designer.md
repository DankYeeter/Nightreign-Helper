# T-124 — Was der Spieler in den 318 ms sieht (ui-ux-designer, Spec-Modus)

STATUS: erledigt
AUFTRAG: T-124 — `UI_SPEC` §3.8 neu; Wartezustand des Relikt-Pickers nach AD-028 (`docs/tasks/T-124.md`)
GELESEN: `docs/tasks/T-124.md` · `CLAUDE.md` · `ARCHITECTURE.md` (Nachtrag VIII ganz: AD-028, AD-029, U1–U8, Risiken, „Bewusst nicht getan", OF-25 bis OF-27; dazu AD-018 mit Korrekturkasten und nachgezogenem Punkt 4, AD-006-Kopf) · `docs/berichte/T-122-architect.md` (vollstaendig) · `UI_SPEC.md` §3.2–§3.8, §4, §5, §6, AK-08 bis AK-13, AK-31 bis AK-53, AK-165/166, die Director-Korrektur vom 07.09.2026 (AK-195, AK-196) · `docs/state.md` Zeile 10-11 (Nummernkreise) · Quellstand **lesend**: `nrplanner/relicpicker.py`, `nrplanner/advisorbar.py`, `nrplanner/advisor/candidates.py`, `nrplanner/advisor/types.py` · `qa/findings.md` QA-190
GEÄNDERT: `UI_SPEC.md` (zwei Stellen: Korrekturkasten an §3.8 des T-024-Abschnitts, ohne den alten Absatz zu loeschen; neuer Abschnitt „Der Picker oeffnet vor seinen Zahlen (ui-ux-designer, T-124) — 2026-09-08" am Dateiende, AK-197 bis AK-210. +566/-1) · `docs/berichte/T-124-ui-ux-designer.md` (diese Datei) · `.claude/agent-memory/ui-ux-designer/` (eigene Rollennotiz zum Nummernkreis, plus Indexzeile). **Nichts committet, nichts gestaged.** `git status` zeigt ausserdem `ARCHITECTURE.md` als geaendert — das ist T-122 (`architect`), **nicht von mir**, ich habe die Datei nur gelesen. Waehrend meines Laufs stand dort zeitweise auch `nrplanner/firstrun.py`; am Ende nicht mehr (der parallele `developer` hat T-123 abgeschlossen, sein Bericht liegt jetzt daneben). Auch diese Datei habe ich nie geoeffnet.
ANNAHMEN: (1) Ich lese AK-09/AK-10 als fuer die Advisor bar geschrieben und ersetze sie **fuer den Picker** durch AK-197 bis AK-202; der Auftrag verlangt einen Wartezustand nach AK-10, nicht woertlich einen Fortschrittsbalken. Das ist eine Entscheidung, keine Auslegung des Bestands — sie steht im Abschnitt ausdruecklich. (2) Der Fehlschlag einer Spur ist ein Zustand, den es heute nicht gibt (ein direkter Aufruf schlaegt durch); dass die Spur ihn als Grundtext meldet, ist aus `AdvisorController.failed` geschlossen, nicht am gebauten Stand gesehen. (3) Alle Quelltextaussagen sind gelesen, **nicht am laufenden Fenster bestaetigt** — ich habe das Programm nicht gestartet und nichts gemessen, wie der Auftrag es vorgibt.
NÄCHSTER: `director` — dann `developer` (U5b, jetzt entsperrt; U5a haengt an nichts und kann davor laufen)
BLOCKIERT DURCH: nichts.

---

## 1. Was spezifiziert wurde

`UI_SPEC.md`, neuer Abschnitt am Dateiende: **„Der Picker oeffnet vor seinen
Zahlen (ui-ux-designer, T-124) — 2026-09-08"**, zehn Unterabschnitte, ersetzt
§3.8 des T-024-Abschnitts. Betroffene Bildschirme: **der Relic Picker**, seine
Zusammenfassungszeile, seine Kartenwertspalte, seine Kopfzeile, seine Ordnung
und der Zielrichtungswechsel im offenen Dialog. Sonst nichts.

§3.8 selbst ist **nicht geloescht**: der alte Absatz steht weiter da, mit
einem Korrekturkasten davor, der **beide Zahlen** nennt — die gerechneten
`~51 ms` samt ihrer Herkunft (205 x 0,25 ms, Bewertung vom 01.09.2026 ohne
protokollierte Umgebung) und die gemessenen **318,1 ms** samt Umgebung nach
L-009 (S11-C, Ryzen 7 5800H bei 1102 von 3201 MHz, `Legion Quiet Mode`,
CPython 3.12.10, `76f1887`). Das ist derselbe Schnitt, den der `architect` an
AD-018 gemacht hat, an der dritten der drei Dateien aus OF-27.

**Die fuenf Entscheidungen in je einem Satz:**

1. **Der Dialog oeffnet sofort, mit Karten, ohne Zahlen.** Zwei Anstriche je
   Oeffnung, nie drei.
2. **Der Wartezustand ist kein Element, sondern ein Wortlaut:** `…` in beiden
   Wertzeilen jeder Karte plus ein gewechselter Nebensatz in Zeile 3. **Kein
   Fortschrittsbalken, kein Wartecursor, kein `Cancel`, keine Zeitschwelle,
   kein Verzoegerungstimer** — weil nichts erscheint und nichts verschwindet,
   kann auch bei 32 ms nichts blitzen, und die Vorgabe ist ohne Wanduhr
   pruefbar.
3. **Ordnung, Kopfzeile, Chips (die eigentliche Frage):** der erste Anstrich
   zeigt die **beraterfreie** Ordnung (Favoriten, dann Name), **keinen Chip,
   keine Vorziehung, keine Kopfzeile**; die Antwort ordnet **genau einmal**
   um, gemeinsam mit Zahlen, Chips und Laufbefunden, ohne den Bildlauf, den
   Tastaturfokus, die Dialoggroesse oder die Kartenhoehe zu bewegen.
4. **Der Zielrichtungswechsel im offenen Dialog bekommt gar keinen
   Wartezustand** — er hat nichts zu rechnen (Beleg unten, Abschnitt 3).
   Eine Oeffnung stellt **eine** Frage.
5. **In der Zahlenspalte bleibt `…`**, und die drei Zeichen `…` / `—` /
   `no change` bekommen drei getrennte, nie vertauschbare Bedeutungen.

## 2. Die Akzeptanzkriterien — AK-197 bis AK-210

**Nummernkreis korrigiert, das ist die erste Meldung dieses Berichts:** Der
Auftrag nennt **AK-195** als freien Kreis, `docs/state.md` Zeile 11 ebenfalls.
**Beide sind ueberholt.** AK-195 und AK-196 sind am 07.09.2026 in der
„Director-Korrektur zum Relic Picker" vergeben (`UI_SPEC.md`), AK-195 ist in
`ea3d016` gebaut und wird von fuenf Faellen in
`tests/test_relic_picker_advisor.py` gehalten; AK-195 kommt ausserdem in
`nrplanner/relicpicker.py` (drei Docstrings), `docs/tasks/T-094.md`,
`docs/tasks/T-123.md` und `qa/findings.md` QA-190 vor. Zwei unabhaengig
formulierte Suchen (`AK-19[5-8]` ueber `*.md`/`*.py`; Volltext `AK-195`) —
gleiches Ergebnis. Ich beginne deshalb bei **AK-197**. `docs/state.md` gehoert
mir nicht und ist nicht angefasst; **der `director` muss Zeile 11 auf
`AK ab AK-211` setzen.**

| ID | worum es geht |
|---|---|
| **AK-197** | Zwei Anstriche, nicht drei: alles, was an der Antwort haengt (Zahlen, Chips, Ordnung, Kopfzeile, Laufbefundzeile), wechselt gemeinsam. Kein Zwischenzustand. |
| **AK-198** | **= W2.** Spur, die nie antwortet: jede Karte traegt `…` in beiden Wertzeilen, kein Chip, keine Vorziehung, leere Kopfzeile, Dialog bedienbar. |
| **AK-199** | Ohne Antwort steht das Raster in der beraterfreien Ordnung (Favoriten, dann Name) — Karte fuer Karte dieselbe Liste wie `Sort by` = `Name`. `Sort by` selbst wird **nicht** umgestellt. |
| **AK-200** | Zeile 3 traegt waehrend des Wartens `working out what each is worth with <slot> empty`; `ranked against your build with <slot> empty` erscheint erst mit den Zahlen. Gleiche Zeilenzahl in beiden Zustaenden, **gemessen** mit Umgebung. |
| **AK-201** | Die Pflichtzeile `One slot at a time — …` und die `scope`-Saetze stehen vom **ersten** Anstrich an vollstaendig (AK-50 gilt ab da). Nur die Laufbefundzeile darf auf die Antwort warten. |
| **AK-202** | Zwischen den beiden Anstrichen kommt kein Widget hinzu und faellt keines weg; keine Zeitschwelle, kein Timer. **Ersetzt AK-09/AK-10 fuer den Picker**, nicht fuer die Advisor bar. |
| **AK-203** | Ueber den Wechsel hinweg identisch: Bildlaufwert, Aussenmasse des Dialogs, Kartenhoehe (AK-41). Der Tastaturfokus bleibt; lag er auf einer Karte, liegt er danach auf der Karte **desselben Relikts**. |
| **AK-204** | Ein Zielrichtungswechsel bei stehender Antwort zeigt zu **keinem** Zeitpunkt `…` und keinen Wartesatz. |
| **AK-205** | Gezeichnet wird die **gewaehlte** Richtung (AK-43), **nicht** `SlotPool.rank_by`. |
| **AK-206** | **Eine Frage je Oeffnung.** Filtern, Bildlauf, Favoriten, Richtungswechsel, `Name` loesen keine weitere aus; ein Wechsel waehrend des Wartens beginnt den Wartezustand nicht neu. |
| **AK-207** | Schliessen waehrend des Wartens: sofort zu, spaete Antwort fasst kein Widget an, wirft nichts, aendert die Slot-Belegung nicht. Zusammen mit **W3**. |
| **AK-208** | Fehlschlag der Spur hat einen **eigenen** Satz; der AK-49-Satz ueber die Spieldateien erscheint dabei **nicht** (A7). |
| **AK-209** | `…` / `—` / `no change` = „laeuft noch" / „nicht gemessen" / „gemessen, ohne Wirkung", nie fuereinander. |
| **AK-210** | Der Bestand ueberlebt: AK-41, AK-42, AK-44 (gemessen am **zweiten** Anstrich), AK-45, AK-46, AK-50, AK-52, AK-195, AK-196. |

Jedes Kriterium mit toetender Mutation dort, wo eine naheliegende
Fehlimplementierung existiert (AK-197, 198, 201, 203, 204, 205, 206, 208).
**Keines nennt eine Millisekunde.** Die beiden Vorrichtungen, mit denen fast
alles davon zu stellen ist: eine Spur, die nie antwortet, und eine, die sofort
antwortet.

## 3. Der Befund, der die vierte Frage des Auftrags beantwortet

Der Auftrag fragt, ob der Zielrichtungswechsel im offenen Dialog
(`relicpicker.py:1169-1171`) denselben Wartezustand bekommt.
**Er bekommt gar keinen: er hat nichts zu rechnen.** Am Quelltext belegt:

- `advisor/candidates.py:254-259` (Docstring von `pool`), woertlich:
  *„Every goal in `goals` is scored for every candidate, whichever one
  `rank_by` names."*
- `advisor/candidates.py:316-320` — `marginals` wird in einer Schleife ueber
  `goals.items()` gebaut, also **je Kandidat fuer jede Richtung**.
- `advisor/candidates.py:328-330` — `baseline` traegt je Richtung Wert,
  Einheit, `unknowns` und `weights_note`.
- `advisor/candidates.py:331` — `candidates=tuple(measured)`, die
  **vollstaendige** Liste, nicht gekuerzt.
- Der Grundzustand haengt am Slot, nicht an der Richtung
  (`base_state_for(problem, slot_index)`).
- Die Anzeige sortiert ohnehin selbst um und liest ueber Handles nach
  (`Ranking.gain`, `_in_the_chosen_order`).

Ein fuer `max_damage` gerechneter Pool traegt also **alles**, was die Anzeige
fuer `min_damage_taken` braucht. Richtungsabhaengig sind nur Ordnung, Chips,
Kopfzeile und `scope`-Saetze — drei davon rechnet die Anzeige selbst, den
vierten liest sie aus der Registry. Und weil der Dialog **modal** ist, kann
sich der Grundzustand waehrend einer Oeffnung nicht aendern.

**Die 318 ms in `_sort_chosen` sind heute reine Verschwendung** — der zweite
Fall, den AD-028 nennt, verschwindet nicht durch die Verlagerung, sondern
durch die Frage, ob er ueberhaupt eine Frage ist.

**Die Falle, die dabei aufgeht, steht in der Spec:** `Ranking.goal_id` gibt
heute `SlotPool.rank_by` zurueck — also die Richtung, in der **sortiert
wurde**. Wer einen Pool weiterverwendet und die Richtung weiter von dort
liest, zeigt still die alte an. Das ist genau der Fehler, gegen den D-4
`rank_by` eingefuehrt hat und der in T-077 unbemerkt 10,2 % eines
Angriffswerts gekostet hat. **AK-205 haelt das fest.**

**Rueckweg**, falls der `developer` in U5b feststellt, dass ein Pool die andere
Richtung doch nicht vollstaendig bedient: dann — und nur dann — bekommt der
Wechsel denselben Wartezustand wie das Oeffnen, mit einem Unterschied (die
stehende Ordnung bleibt stehen, sie faellt nicht auf Namensordnung zurueck).
Das steht in der Spec und ist **ein Befund, der berichtet wird**, kein stiller
Umbau (L-008c).

## 4. Was der `director` wissen muss, ohne dass es beauftragt war

1. **`docs/state.md` Zeile 11 ist falsch** (`AK ab AK-195`) — siehe oben. Neu:
   **`AK ab AK-211`**. Ich fasse die Datei nicht an.
2. **Die groessere Bewegung ist nicht die Umsortierung.** Heute versteckt
   `_say_what_was_left_out` **beide** Textzeilen ueber dem Raster — die
   Pflichtzeile aus AD-018.3 **und** den Attack-Rating-Vorbehalt —, solange
   keine Rangfolge vorliegt (`if self.ranking is None: … caveats.setVisible(False)`).
   Bliebe das so, faellt der Vorbehalt fuer 320 ms aus (Bruch von AK-50
   waehrend des Wartens) und schiebt beim Erscheinen **das ganze Raster nach
   unten**. Beide Zeilen brauchen keine Rechnung: die eine ist eine Konstante,
   die andere kommt aus der Registry. **AK-201.** Der `developer` muss das
   ausdruecklich bauen, sonst entsteht der Fehler von selbst.
3. **Eine Messauflage an den `developer`, keine Schaetzung.** Die
   Laufbefundzeile (3b) ist die **einzige** Anzeige ueber dem Raster, die ohne
   Antwort nicht existieren kann; der Dialog misst sich aber nur **einmal**
   (`_fit_to_three_rows`, `self._sized`-Sperre). Der `developer` misst am
   gebauten Stand, um wie viele Pixel die Rasteroberkante wandert, wenn die
   Zeile im schlechtesten realen Fall erscheint, und nennt die Zahl **mit
   Umgebung** (L-009). Bleiben danach weniger als zwei volle Kartenzeilen
   sichtbar, ist **AK-196 verletzt** und die Frage kommt zu mir zurueck — die
   Loesung waere dann der Platz der Zeile, nicht ihr Wortlaut.
4. **Neuer QA-Befund, A7, aelter als AD-028 — bitte als QA-210 aufnehmen:**
   Der Picker zeigt den Satz `The game's data carries no figures this goal can
   be ranked on, so these relics are in name order.` **auch dann**, wenn der
   wirkliche Grund „es wurde kein Spielstand gelesen" ist.
   `advisorbar.asking_from` gibt fuer „kein Save" `None` zurueck
   (Docstring woertlich: *„`None` means there is no save to choose relics
   from"*), `SlotAdvice.ranking` reicht das als `None` durch, und
   `_say_what_they_are_worth` bildet **jedes** `None` auf `NO_FIGURES_AT_ALL`
   ab. Das Programm behauptet damit etwas ueber die **Spieldateien**, was eine
   Aussage ueber den **Spielstand** waere — derselbe A7-Bruch, gegen den A7
   geschrieben ist. **Fertiger Wortlaut, Hausmuster der Advisor bar:**
   `No save was read, so there is nothing to rank these against — use Rescan save.`
   **Unverifiziert (Code-Analyse):** ob dieser Zustand mit Karten auf dem
   Schirm ueberhaupt erreichbar ist (ohne Save koennte `available_items()`
   leer sein), habe ich **nicht** geprueft — ich habe das Programm nicht
   gestartet. Der `qa-engineer` entscheidet das an einem Lauf. **Nicht Teil
   dieser Vorgabe**, ausdruecklich, damit ihn niemand fuer von AK-208
   erledigt haelt.
5. **Fuer den `architect`, zwei Folgen von AD-028, die ich nicht entscheide:**
   - **AD-028 Punkt 4 verliert eines seiner beiden Beispiele.** Die
     Begruendung des Generationszaehlers nennt zwei Faelle; der erste (der
     offene Dialog rechnet beim Richtungswechsel neu) faellt nach Abschnitt 3
     weg. **Der zweite bleibt** (der Dialog kann geschlossen werden, waehrend
     eine Antwort unterwegs ist), also bleibt der Zaehler noetig — die
     Entscheidung kippt **nicht**. Nur ihre Begruendung hat jetzt ein
     Beispiel weniger, und AD-028 sagt heute etwas ueber `1169-1171`, was
     nach dieser Spec nicht mehr gilt.
   - **Die 100-ms-Entprellung der Picker-Spur hat nach dieser Spec nichts
     mehr zu entprellen.** Es gibt eine Frage je Oeffnung, und der Dialog ist
     modal, also kann keine zweite kurz darauf folgen. Was bleibt, sind 100 ms
     **zusaetzliche** Wartezeit auf die einzige Frage, die es gibt (318 → rund
     418 ms bis zum zweiten Anstrich). Das ist eine Zahl aus AD-028.1 und
     gehoert dem `architect`, nicht mir — aber sie kostet den Spieler ein
     Drittel mehr Wartezeit fuer einen Schutz, den diese Spec entfernt hat.
   - **Vorwaermen waere die eigentliche Loesung.** `candidates.pools()`
     berechnet die Pools **aller** freien Slots in einem Zug. Liefe das nach
     jeder Buildaenderung im Hintergrund, waere jedes Oeffnen ein
     Cache-Treffer und der ganze Wartezustand der Ausnahmefall statt der
     Regel. Kostet Rechenzeit gegen zwei Spuren unter dem GIL (OF-25) —
     **Entwurfsfrage, `architect`, nicht in dieser Spec.**
6. **QA-190 beruehrt meinen Abschnitt am Rand:** der dort gemeldete
   `ADVISOR PICK`-Chip und die Zusatzzeile der Zusammenfassung sind
   spezifiziert, aber nicht gebaut. Ich habe daran **nichts** geaendert;
   AK-200 wechselt nur den mittleren Nebensatz derselben Zeile. Wird QA-190
   spaeter gebaut, muss die dortige Zusatzzeile mit dem Wartezustand
   vertraeglich sein — sie ist eine Aussage ueber die Vorziehung und darf
   deshalb im ersten Anstrich ebenfalls nicht stehen.

## 5. Offene Fragen an den App Designer

- **F-P (Bewegung gegen fruehe Inhalte).** Diese Vorgabe zeigt die Karten
  sofort und ordnet sie rund ein Drittel einer Sekunde spaeter **einmal** um.
  Die Gegenoption waere ein leeres Raster bis zur Antwort: gar keine Bewegung,
  dafuer eine drittel Sekunde ohne Namen, ohne Filtertreffer und ohne
  Dialoggroesse. **Empfehlung: so wie vorgegeben** — die Reliktnamen haengen
  am Berater nicht, und wer ein bestimmtes Relikt sucht, braucht die Zahlen
  nie. Wenn den App Designer Bewegung mehr stoert als Warten, ist es eine
  Zeile.
- **F-Q (`Sort by` beim Durchtippen).** Der Richtungswechsel kostet nach
  Abschnitt 3 nichts mehr; damit ordnet sich das Raster bei **jedem** Schritt
  durch die `Sort by`-Liste sofort um, mit Pfeiltasten also auch bei
  Eintraegen, bei denen der Spieler nicht stehen bleiben will. **Empfehlung:
  so lassen** — sofort ist ehrlicher als „erst bei Enter", und es kostet
  nichts. Reine Geschmacksfrage.

## 6. Was ich **nicht** getan habe, und was nicht verifiziert ist

- **Keine Zeile Anwendungscode, kein Test, keine Datei ausser `UI_SPEC.md`
  und diesem Bericht.** `ARCHITECTURE.md`, `tests/`, `GOAL.md`,
  `docs/state.md`, `qa/findings.md`, `docs/tasks/` sind unberuehrt.
- **Nichts committet, nichts gestaged.**
- **Das Programm nicht gestartet, nichts gemessen, keinen Bildnachweis
  erzeugt** — der Auftrag sagt „du entwirfst, du misst nicht". Damit war auch
  keine Umlenkung der drei Datenverzeichnisse noetig; **es wurde kein Server
  und kein Prozess gestartet**, es ist nichts aufzuraeumen.
- **Alle Quelltextaussagen sind gelesen, nicht am laufenden Fenster
  bestaetigt.** Sie sind im Abschnitt als **(Quelltext)** gekennzeichnet. Die
  drei, an denen am meisten haengt — dass ein Pool beide Richtungen traegt,
  dass `caveats` bei fehlender Rangfolge versteckt wird, dass sich der Dialog
  nur einmal misst — sind an je einer benannten Zeile belegt und vom
  `developer` in U5b beim Bauen ohnehin zu beruehren.
- **Die Suite ist nicht gelaufen.** Ich habe keinen Code angefasst; die Zahl
  aus `docs/state.md` (1257 passed, 9 skipped) gilt unveraendert und wird von
  T-123 bewegt, nicht von mir.
- **Zeilenenden:** der angehaengte Abschnitt hat LF, die Datei im
  Arbeitsbaum CRLF. Git speichert LF und normalisiert beim naechsten Anfassen
  (`git diff` meldet +566/-1, also keine Masse-Aenderung). Kein Handlungsbedarf,
  aber genannt, damit es niemanden ueberrascht.
