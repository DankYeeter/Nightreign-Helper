# Architektur

Stand: 2026-09-01 · Angelegt im Zuge T-001 (Zyklus 1, Audit)
Sprache: dieses Dokument Deutsch (Team-Dokument, wie `GOAL.md` und
`docs/state.md`). Bezeichner im Code und **alle nutzersichtbaren Texte
Englisch** (Projektregel, `GOAL.md` A8).

Bezugsstand: 3da8428 (v1.7.1), 16 737 Zeilen Python, 0 Tests.
`GOAL.md` ist vom Nutzer freigegeben; A1–A9 sind für diesen Entwurf bindend.

---

## Gemessene Grundzahlen

Alle Entwurfsentscheidungen unten stützen sich auf diese Messungen, nicht auf
Annahmen. Rechner: dieser (Windows 10, CPython 3.12).

**Aus dem Daten-Snapshot der Installation** (gelesen 2026-09-01):

| Grösse | Wert |
|--------|------|
| Relikt-Vorlagen | 849 — davon 597 normal, 252 Deep of Night |
| Vorlagen je Farbe | Rot 223 · Blau 212 · Gelb 206 · Grün 208 |
| Effekt-Plätze je Relikt | 1 → 230 Vorlagen, 2 → 267, 3 → 349, 0 → 3. **Mittel 2,14** |
| Curse-Plätze je Relikt | 0 → 705, 1 → 72, 2 → 48, 3 → 24 |
| Effekte gesamt | 2 079 |
| Gefässe | **74**, davon **20 mit mindestens einem weissen Slot** |
| verschiedene sortierte 3-Slot-Muster | **26** |
| verschiedene sortierte 6-Slot-Muster (mit Deep) | **47** |

Die letzten beiden Zeilen tragen AD-008: 74 Gefässe stellen nur 26 bzw. 47
verschiedene Suchprobleme.

**Realer Bestand — vom `qa-engineer` gegen das echte Save gemessen**
(2026-09-01, löst OF-7 ab):

| Grösse | Wert |
|--------|------|
| Relikte im Besitz | **309** |
| je Farbe | Rot 75 · Blau 83 · Gelb 81 · Grün 70 |
| davon Deep of Night | **101** (32,7 %), normal 208 |
| Kandidaten für einen **farbigen** Slot | 49–54 normal, 21–30 deep |
| Kandidaten für einen **weissen** Slot | **205 normal, 101 deep** |
| verschiedene Rollen unter den 309 Exemplaren | **306 — Dedup spart 1,0 %** |

Zwei Dinge daran waren aus dem Snapshot **nicht** ableitbar, und beide sind
wichtig:

1. **Weiss ist eine Eigenschaft des Slots, nicht eine Relikt-Farbe.** Ein
   weisser Slot nimmt jede Farbe und hat damit rund das Vierfache an
   Kandidaten. Meine erste Fassung hatte das übersehen und den schlechtesten
   Fall unterschätzt.
2. **Rollen-Dedup bringt nichts.** 309 Exemplare ergeben 306 verschiedene
   Rollen — drei Kollisionen. Drei Effekte aus einem Pool von 2 079 kollidieren
   praktisch nie. Der Gedanke, gleiche Rollen zu einem Kandidaten
   zusammenzufassen, ist damit erledigt; siehe „Bewusst nicht getan".

Ein Build umfasst im Mittel 3 × 2,14 ≈ 6,4 Effekte (3 Slots) bzw. ~13 Effekte
(6 Slots) — nicht 18, wie `EFFECTS_PER_RELIC = 3` nahelegt.

**Suchraum, ungünstigster realer Fall.** `Wylder's Chalice` (id 1002):
normal `[Rot, Gelb, Weiss]`, deep `[Rot, Blau, Grün]`.

| Gefäss | Kandidaten je Slot | Vollprodukt |
|--------|--------------------|-------------|
| `Wylder's Chalice` + Deep | 50 · 55 · **208** · 25 · 27 · 23 | **8,9 · 10⁹** |
| `Wylder's Urn` + Deep (nur farbig) | 50 · 50 · 56 · 25 · 25 · 27 | 1,2 · 10⁹ |
| 3 Slots ohne Deep | 50 · 55 · 208 | 5,7 · 10⁵ |

**Kosten der Bewertung** (`model.compute()`): **0,18–0,25 ms** bei 18
Effekten, **~0,10 ms** bei der realen mittleren Effektzahl.

**Kosten der Beam-Suche**, mit weissem Slot, mit erzwungener
Exemplar-Eindeutigkeit (AD-013) und einschliesslich des Vorsortierlaufs über
alle 309 Relikte:

| Gefäss | K=12 W=24 | K=20 W=40 | K=30 W=60 |
|--------|-----------|-----------|-----------|
| `Wylder's Chalice`, 3 Slots | — | 1 529 Aufrufe · **0,11 s** | — |
| **`Wylder's Chalice` + Deep, 6 Slots** | 1 617 · **0,18 s** | 3 929 · **0,46 s** | 7 927 · **0,98 s** |

**Der weisse Slot kostet fast nichts — und das ist kein Zufall, sondern der
Kern des Verfahrens.** Gegenprobe bei K=20/W=40: `Wylder's Chalice` (Pool 208)
und `Wylder's Urn` (Pool höchstens 56) brauchen **exakt gleich viele**
Bewertungen, nämlich 3 929, und 0,47 s gegen 0,40 s. Der Grund: die Kosten der
Beam-Suche sind `Slots × W × K`, und **K ist eine Obergrenze**. Ein vierfach
grösserer Pool vervierfacht den rohen Produktraum, aber nicht die
Verzweigung. Er verteuert allein den Vorsortierlauf, und der ist eine
Bewertung je *besessenem Relikt* (309), nicht je Slot-Kandidat — rund 30 ms.

Das ist die Zahl, an der der Entwurf hängt: der ungünstigste reale Fall liegt
bei K=20/W=40 unter einer halben Sekunde, mit weissem Slot, mit Deep of
Night — und zwar **mit der echten `model.compute()` an jedem Suchschritt**,
nicht mit einer Näherung.

---

## Überblick

Nightreign Helper liest die Datentabellen der lokal installierten
Spielinstallation und den lokalen Spielstand und hilft beim Planen von
Relikt-Builds. Kein Netz, kein Schreibzugriff auf das Spiel.

Drei Schichten, Abhängigkeit strikt von oben nach unten:

```
  nrdata/      Spieldateien lesen: Archive, Params, Textblöcke, Savefile.
               Erzeugt einen Snapshot (dict) und die Besitzliste.
      ^
  nrplanner/   Domäne: Build-Mathematik (model), Stacking-Regeln (stacking),
  (Kern)       Effekttexte (effecttext), Waffenwerte (weapons), Besitz
               (inventory), Persistenz von Builds (chalices, favourites).
      ^
  nrplanner/   Oberfläche: app.py (Fenster + Planner-Klasse) und die
  (Qt)         Tab-Module. PySide6/Qt.
```

**Datenfluss heute:** `datasource.load_data()` liefert den Snapshot als ein
grosses `dict` und ruft `model.configure(data)`; `inventory.load(data)` liest
den Save und liefert eine `Inventory` mit `OwnedItem`-Einträgen;
`Planner.recompute()` sammelt die Effekte der belegten Slots und ruft
`model.compute(...) -> model.Build`; die Oberfläche liest aus `Build`.

**Was dazukommt:** ein *Build-Berater* — `nrplanner/advisor/`. Er dreht den
Fluss um: statt „Slots sind belegt, was kommt dabei heraus?" fragt er „welche
Belegung aus dem Besitz maximiert eine benannte Zielgrösse?". Er benutzt
dieselbe `model.compute` als einzige Autorität, sucht im Hintergrund-Thread
und liefert eine gerankte Liste mit Begründung und einer ausdrücklichen Liste
dessen, was er *nicht* wissen kann.

---

## Wichtige Korrektur zur Auftragslage (erledigt)

T-001 und die erste Fassung von `GOAL.md` sprechen von **Tkinter**. Das
Programm verwendet **PySide6 (Qt 6.11.1)** — `requirements.txt` und jeder
Import in `nrplanner/app.py` und den Tab-Modulen. Kein einziges `tkinter` im
Repo. Der `director` hat das bestätigt und zieht `GOAL.md` nach.

Das ist keine Kosmetik: Qt bringt `QThread`, `Signal`/`Slot` über die
Thread-Grenze und eine thread-affine Event-Loop mit, und im Repo existiert
bereits ein funktionierendes Hintergrund-Muster (`nrplanner/firstrun.py`,
Worker-Objekt per `moveToThread` plus Signale). AD-006 baut darauf auf statt
auf einer Tkinter-`after()`-Schleife.

---

## Teil 1 — Strukturaudit des Bestands

### Was trägt

Die Schichtung ist sauber und das ist nicht selbstverständlich:

- **Kein Zyklus.** `nrdata` importiert `nrplanner` nirgends (geprüft: 0
  Treffer). Kein Modul importiert `app.py` (geprüft über alle Imports in
  `nrplanner/*.py`). `app.py` ist die Spitze und nicht Teil des Kerns.
- **`model.compute()` ist rein.** Signatur
  `compute(hero, level, effects, curves, weapon, weapons_held, declared) -> Build`,
  keine Qt-Abhängigkeit, kein globaler Zustand ausser der über
  `model.configure()` gesetzten Feldtabelle. Gemessen 0,10–0,25 ms je nach
  Effektzahl (siehe Grundzahlen). Das ist der Grund, warum der Berater keinen
  zweiten, schnelleren Scorer braucht — siehe AD-002.
- **Die Domänenregeln sind belegt, nicht geraten.** `model.py` und
  `stacking.py` führen für praktisch jede Sonderregel die Messung oder das
  Param-Feld an, aus dem sie stammt. Diese Kommentare sind das eigentliche
  Kapital des Projekts.
- **`Build` trägt bereits die Begründungsspur.** `Build.sources` ist
  `field -> [(Effektname, Einzelwert)]`. Abnahmekriterium A5 („nachvollziehbare
  Begründung in Nutzersprache") ist damit keine neue Mechanik, sondern eine
  Formatierung von etwas, das schon existiert.

### Befunde, priorisiert

| # | Prio | Befund | Empfehlung |
|---|------|--------|------------|
| F1 | **hoch** | **Die Schadensrechnung sitzt in der Oberfläche.** Die eigentliche Attack-Rating-Mathematik — Multiplikatoren auf die skalierten Werte, Waffenklassen-Buffs, die Startwaffen-Sonderregel — steht in `Planner._refresh_weapon_damage` (`app.py:2451`, 197 Zeilen) und liest dabei `self.AR_RATE_FOR`, `self.STARTING_AR_RATE_FOR`, `self.STARTING_SLOT`, `self.active_weapon`, `self.data`. Sie ist untrennbar mit dem Beschreiben von Widgets verwoben. Der Berater braucht genau diese Zahl. Ohne Extraktion gäbe es sie zweimal — und zwei Antworten auf eine Frage sind schlimmer als eine unsichere. | `nrplanner/damage.py` als reines Modul herausziehen, `app.py` ruft es. **Voraussetzung für den Berater**, siehe AD-005 und Schritt S1. |
| F2 | **hoch** | **Keine Tests, kein Test-Job.** `.github/workflows/` enthält nur `release.yml`. `model.py` kodiert ~30 handverlesene, teils im Spiel gemessene Regeln (`NON_ACCUMULATING`, `INVERTED_RATES`, `CONDITIONAL_FIELD_VALUES`, `WEAPON_CLASS_SCOPES`, …). Keine einzige ist ausführbar abgesichert. Ein Berater, der auf dieser Mathematik rankt, ist ohne Tests nicht abnehmbar (`GOAL.md` A9). | Headless-Testsockel vor dem Berater, siehe AD-009 und Schritt S2. Regressionsschutz für F1 ist derselbe Sockel. |
| F3 | **hoch** | **`Planner` ist ein Gottobjekt.** 2277 Zeilen, 59 Methoden, 67 gesetzte Instanzattribute. `recompute()` allein 335 Zeilen: sie speichert den Build, rechnet, reisst Layouts ab (`while grid.count(): takeAt(0)`) und baut Widgets neu — vier Verantwortungen in einer Methode. Jede neue Anzeige wächst sie weiter. | Nicht jetzt umbauen (Scope). Aber **harte Regel für diesen Auftrag: der Berater wächst `app.py` nicht.** Eigenes Tab-Modul wie `effectstab.py`/`bosstab.py`, Anbindung an `Planner` über genau einen Worker und dessen Signale. |
| F4 | mittel | **`model.py` hält veränderlichen Modulzustand.** `FIELD_BASELINE`, `PERCENT_FIELDS`, `PERCENT_OF_100_FIELDS` sind Modulglobals, die `model.configure(data)` leert und neu füllt. Das ist zweierlei Risiko: (a) ein Hintergrund-Suchlauf, der rechnet, während der Hauptthread nach einem Spiel-Patch neu extrahiert und `configure()` erneut aufruft, rechnet mitten im Umbau der Tabelle; (b) Tests werden reihenfolgeabhängig. | Sofort entschärfen: ein Datenneuaufbau **bricht laufende Beraterläufe ab und verwirft den Cache** (AD-006, AD-007). Sauber lösen (Config-Objekt statt Globals) ist ein eigener Auftrag, nicht dieser. |
| F5 | mittel | **Eine Regel, zwei Orte.** `stacking.py` *klassifiziert* („Stacks", „Strongest only", „Exclusive group"), aber die Arithmetik, die das durchsetzt — Duplikatsunterdrückung über `seen_ids`, Exklusivgruppen über `exclusivity` — steht in `model.compute()`. Beide sind heute konsistent, weil `stacking.repetition()` `model.NON_ACCUMULATING` konsultiert. Sie können auseinanderlaufen, und A4 hängt daran. | Kein Umbau. Stattdessen: der Testsockel bekommt eine Eigenschaftsprüfung „für jeden Effekt gilt: `stacking.repetition(e) == STACKS` ⟺ zwei Kopien in `compute` bewegen das Total doppelt". Das bindet die beiden Orte aneinander, ohne einen zu verschieben. |
| F6 | mittel | **Domänenkonstanten in einem UI-Modul.** `AR_RATE_FOR`, `STARTING_AR_RATE_FOR`, `STARTING_SLOT` (Klassenattribute von `Planner`), dazu `WHITE_SLOT = 4`, `EFFECTS_PER_RELIC = 3`, `GRAIL_HERO_TYPE = 11` als Modulkonstanten in `app.py`. `inventory.relics_for()` nimmt `white_slot` bereits als Parameter entgegen, weil der Wert dort nicht liegt, wo er hingehört. | Mit F1 zusammen nach `nrplanner/damage.py` bzw. `nrplanner/model.py` verschieben. Der Berater braucht `WHITE_SLOT` und `EFFECTS_PER_RELIC` und darf sie nicht aus `app.py` importieren. |
| F7 | mittel | **Stiller Rückfall auf möglicherweise veraltete Daten.** `datasource._load_data` fängt auf dem Live-Extraktionspfad `except Exception: pass` und liefert dann den gebündelten Snapshot — ohne Kennzeichnung. Nach einem Spiel-Patch rechnet der Berater dann auf altem Stand und sagt es nicht. Das verstösst gegen die Hausregel. | Kein Umbau von `extract.py` (Scope-Grenze). Aber: der Berater trägt `meta.data_version`, `meta.extract_version` und `meta.regenerated` in seinen Ergebniskopf und kennzeichnet einen nicht gegen das Spiel verifizierten Datenstand. Siehe AD-010. |
| F8 | niedrig | **`requirements.txt` mischt Laufzeit und Werkzeug.** `pyinstaller` steht neben `PySide6`. Sobald Tests dazukommen, fehlt die Trennung Laufzeit / Entwicklung. | Bei S2 mitziehen: `requirements-dev.txt`. Kostet nichts und verhindert, dass ein Test-Paket im PyInstaller-Bundle landet. |
| F9 | niedrig | **`app.py` ist mit 3259 Zeilen die grösste Datei, aber nicht die schlimmste.** Der eigentliche Schaden ist F3 (die Klasse), nicht die Datei. `nrdata/extract.py` mit 2728 Zeilen ist ein Extraktor mit hoher Kommentardichte und einer klaren Aufgabe — gross, aber nicht falsch geschnitten, und ausdrücklich ausserhalb des Scope. | Kein Handlungsbedarf in diesem Zyklus. |

**Zusammengefasst:** die Struktur ist nicht kaputt, sie ist *oben zu schwer*.
Der Kern (`model`, `stacking`, `weapons`, `inventory`, `effecttext`) ist rein,
schnell und wiederverwendbar. Genau eine Domänenrechnung ist in die
Oberfläche gerutscht (F1), und genau die braucht der Berater. Das ist der
einzige Umbau, den dieser Auftrag zwingend erfordert.

---

## Teil 2 — Struktur des Build-Beraters

### Modulschnitt

```
nrplanner/advisor/
  __init__.py     öffentliche Namen: Goal, GOALS, Suggestion, AdvisorRequest
  types.py        Datenklassen: SlotProblem, Candidate, Suggestion,
                  GoalScore, AdvisorRequest, AdvisorResult
  candidates.py   Besitz -> Kandidatenpool je Slotfarbe (Dedup, Filter)
  goals.py        Zielrichtungs-Registry: Build -> GoalScore
  search.py       Beam-Suche über die Slots. Rein, abbrechbar.
  explain.py      Build.sources -> englische Begründung + "not counted"
  worker.py       EINZIGE Qt-Datei: QThread-Worker, Signale, LRU-Cache
```

**Erlaubte Abhängigkeitsrichtung — verbindlich:**

```
nrdata
  ^
nrplanner.model  nrplanner.stacking  nrplanner.weapons
nrplanner.damage (neu, aus app.py)   nrplanner.effecttext  nrplanner.inventory
  ^
nrplanner.advisor.types
  ^
nrplanner.advisor.candidates, .goals, .search, .explain
  ^
nrplanner.advisor.worker            <- hier und nur hier PySide6
  ^
nrplanner.advisortab (neu, Qt)  ->  nrplanner.app
```

Ausdrücklich verboten:
- Kein Modul unter `advisor/` ausser `worker.py` importiert PySide6.
- Kein Modul unter `advisor/` importiert `nrplanner.app` oder ein `*tab.py`.
- `nrplanner.app` importiert aus `advisor/` **nur** `worker` und `types`.
- Kein Modul unter `advisor/` importiert ein anderes `advisor/`-Modul
  entgegen der Reihenfolge oben. `types.py` importiert nichts aus `advisor/`.

Der Grund für die Qt-Grenze in genau einer Datei: die gesamte Suche muss ohne
Display laufen, sonst ist sie nicht testbar (F2, `GOAL.md` A9), und ohne Tests
ist der Berater nicht abnehmbar.

### Wo Zustand liegt

- **Kein Zustand in `search.py`, `goals.py`, `candidates.py`, `explain.py`.**
  Reine Funktionen über `AdvisorRequest`.
- **`worker.py`** hält den einzigen veränderlichen Zustand des Beraters: den
  laufenden `QThread`, das Abbruch-Flag und den LRU-Cache. Er lebt am
  `Planner`, nicht global.
- **Nichts wird persistiert.** Kein `QSettings`-Eintrag, keine Datei. Ein
  Vorschlag ist eine Antwort auf den Bestand von jetzt; ein gespeicherter
  Vorschlag wäre in dem Moment falsch, in dem ein Relikt eingeschmolzen wird.
  Übernimmt der Spieler einen Vorschlag, geht er über den **bestehenden** Weg
  in die Slots (`chalices.save_build`) — der Berater bekommt keine zweite
  Persistenzform. Siehe AD-007.

### Datenfluss eines Laufs

```
Planner (Qt-Hauptthread)
  |  baut AdvisorRequest: hero, level, slot_colours, deep, goal_id,
  |  weapon_context, declared, budget, data-Fingerprint
  v
worker.AdvisorController.request(req)
  |  1. kanonisiert den Request (AD-008)
  |  2. Cache-Treffer? -> Signal `ready` sofort, kein Thread
  |  3. sonst: laufenden Lauf abbrechen, QThread starten
  v
[Hintergrund-Thread]
  candidates.pools(inventory, problem, data)   -> Kandidaten je Slot
  search.beam(problem, pools, goal, budget)    -> ruft model.compute() N-mal
  explain.reasons(best_build, empty_build, …)  -> englische Zeilen
  v
Signal `ready(AdvisorResult)`  ->  Qt-Hauptthread  ->  advisortab zeichnet
```

`AdvisorResult` enthält: die gerankte Liste (je Eintrag: Relikt je Slot,
Punktzahl, Begründungszeilen), den Zielrichtungs-Namen und **`unknowns`** —
die Liste dessen, was diese Bewertung nicht wissen kann (A7).

---

## Entscheidungen

### AD-001 — Der Berater wird ein eigenes Paket, nicht ein Modul und nicht Teil von `app.py` (2026-09-01, Status: aktiv)

**Kontext:** Der Berater braucht Kandidatenauswahl, Zielfunktionen, ein
Suchverfahren, eine Begründungsschicht und eine Thread-Anbindung. Das sind
fünf verschiedene Gründe zur Änderung. `app.py` hat bereits 3259 Zeilen und
eine Klasse mit 59 Methoden (F3).

**Optionen:**
- **A — in `Planner` einbauen.** Kürzester Weg zum Ergebnis, direkter Zugriff
  auf `self.data`, `self.owned`, `self.current_hero()`. Konsequenz: F3 wächst
  um mehrere hundert Zeilen, und die Suche ist ohne laufendes Qt nicht
  aufrufbar — also nicht testbar. A9 wäre nicht erfüllbar.
- **B — eine Datei `nrplanner/advisor.py`.** Passt zum bestehenden Muster
  flacher Module. Konsequenz: nach Erfahrung dieses Projekts (`model.py` 1122,
  `app.py` 3259) landet das bei 700+ Zeilen mit fünf Verantwortungen — genau
  der Fehler, der bereits einmal gemacht wurde.
- **C — Paket `nrplanner/advisor/` mit Qt in genau einer Datei.**
  Konsequenz: ein Verzeichnis mehr als das Projekt bisher kennt; dafür ist
  jede Datei unter 250 Zeilen, die Suche ohne Display aufrufbar und die
  Zielrichtungen erweiterbar, ohne die Suche anzufassen.

**Entscheidung:** C. Der ausschlaggebende Punkt ist nicht Eleganz, sondern
A9: das Ergebnis muss gegen ein Artefakt geprüft werden, und eine Suche, die
ein `QApplication` voraussetzt, ist im CI nicht prüfbar. Die Qt-Grenze in
genau einer Datei ist die billigste Art, das zu garantieren.

**Konsequenzen:** Leicht wird — Tests ohne Display, eine neue Zielrichtung
ohne Eingriff in die Suche, ein zweites Frontend (CLI zur Diagnose) ohne
Aufwand. Dauerhaft schwer wird — schneller Durchgriff der UI auf Interna der
Suche; alles muss durch `AdvisorRequest`/`AdvisorResult`. Das ist beabsichtigt.

**Umkehrbarkeit:** leicht. Ein Paket lässt sich zu einer Datei
zusammenziehen, solange keine externen Importe darauf zeigen.

---

### AD-002 — `model.compute()` ist die einzige Bewertungsautorität; es gibt keinen zweiten, schnelleren Scorer (2026-09-01, Status: aktiv)

**Kontext:** Der naheliegende Entwurf für einen Optimierer ist ein
spezialisierter, schneller Akkumulator, der nur die Felder verfolgt, die die
Zielrichtung liest — Mikrosekunden statt Millisekunden. Dagegen steht: die
Stacking-Regeln (A4) sind nicht trivial. Duplikatsunterdrückung bei
`isStrongestEffect`, Exklusivgruppen über `exclusivityId`, `NON_ACCUMULATING`,
Konditionalitätsprüfung, `works_for` je Nightfarer, additiv-versus-
multiplikativ nach `field_baselines`. Ein zweiter Scorer müsste all das
nachbauen — und würde irgendwann abweichen. Dann rankt der Berater nach einer
anderen Wahrheit, als die Statustafel anzeigt.

**Messung — siehe „Gemessene Grundzahlen".** Der schlechteste Fall, ein
6-Slot-Deep-Gefäss mit weissem Slot (`Wylder's Chalice`) gegen den realen
Bestand von 309 Relikten, kostet bei K=20/W=40 **0,46 s** und bei K=30/W=60
**0,98 s**, jeweils mit der echten `model.compute()` an jedem Schritt. Ein 3-Slot-Gefäss liegt bei **0,11 s**.

**Optionen:**
- **A — Zweitscorer für die Suche, `compute()` nur für die Endauswahl.**
  Schnellste Suche. Konsequenz: zwei Implementierungen einer Regel, dauerhaft
  synchron zu halten, und ein Divergenzrisiko genau bei A4.
- **B — `compute()` an jedem Suchschritt.** Konsequenz: teurer, aber die
  Stacking-Regeln, die Curse-Behandlung, `works_for` und die
  Konditionalitätsprüfung gelten *von selbst* und richtig. Messung zeigt: bei
  K=20/W=40 eine halbe Sekunde für den schlechtesten Fall (6 Slots, Deep).
- **C — Zweitscorer plus Eigenschaftstest gegen `compute()`.** Rettet die
  Konsistenz, kostet aber die Implementierung *und* die Testinfrastruktur, in
  einem Projekt, das noch keinen einzigen Test hat.

**Entscheidung:** B. Der Zweitscorer löst ein Problem, das die Messung nicht
zeigt. Eine halbe Sekunde im Hintergrund ist kein Problem, zwei divergierende
Stacking-Implementierungen sind eines.

**Konsequenzen:** Leicht wird — A4 ist strukturell erfüllt, nicht durch
Sorgfalt; jede künftige Korrektur an `model.py` erreicht den Berater ohne
Zutun. Dauerhaft schwer wird — sehr viel grössere Suchräume (etwa: alle 74
Gefässe auf einmal) sind in diesem Rahmen nicht drin; sie brauchten dann A
oder C.

**Umkehrbarkeit:** mittel. Ein Zweitscorer lässt sich später hinter derselben
Schnittstelle einziehen, sofern `search.py` den Scorer als Parameter nimmt —
was es tun soll. Kosten dann: die Testinfrastruktur, die heute ohnehin fehlt.

---

### AD-003 — Beam-Suche über die Slots, nicht Vollprodukt, nicht Greedy, nicht Solver (2026-09-01, Status: aktiv)

**Kontext (gegen das echte Save gemessen, siehe Grundzahlen):** Der reale
Bestand von 309 Relikten ergibt 49–54 Kandidaten je Farbe für einen normalen
Slot, 21–30 für einen Deep-Slot — und **205 für einen weissen Slot**, der
jede Farbe nimmt. Der ungünstigste reale Fall ist `Wylder's Chalice` mit
Deep of Night:

- 3 Slots ohne Deep: 50 · 55 · 208 = **5,7 · 10⁵** Belegungen
- 6 Slots mit Deep: 50 · 55 · 208 · 25 · 27 · 23 = **8,9 · 10⁹** Belegungen

Die Bewertung ist **nicht separabel**: durch Exklusivgruppen,
`isStrongestEffect` und multiplikative Raten hängt der Wert eines Relikts
davon ab, was in den anderen Slots liegt.

**Optionen:**
- **A — Vollprodukt.** Exakt. Für das 3-Slot-Gefäss ist es *nicht* absurd:
  5,7 · 10⁵ Bewertungen à 0,10 ms sind **~57 s**. Für das 6-Slot-Gefäss sind
  es **~10 Tage**. Ausgeschlossen — aber ausgeschlossen aus einem gemessenen
  Grund und nur im Deep-Fall hoffnungslos. Das ist der Grund, warum unten ein
  *Regler* steht und kein Entweder-oder: bei kleinen Problemen darf die Suche
  fast erschöpfend sein.
- **B — Greedy je Slot.** Bestes Relikt je Slot einzeln, unabhängig: ~390
  Aufrufe, ~0,04 s. Konsequenz: falsch genau dort, wo es interessant wird —
  zwei Kopien desselben `isStrongestEffect` werden gewählt und die zweite ist
  wertlos; zwei Effekte einer Exklusivgruppe werden gewählt und nur einer
  greift. Der Berater empföhle dann Builds, deren Punktzahl er selbst
  widerlegt.
- **C — Beam-Suche über die Slots, Bewertung des Teil-Builds bei jedem
  Schritt mit `model.compute()`.** Beam-Breite W, Kandidatenzahl K. Greedy
  ist der Sonderfall W=1, Vollprodukt der Grenzfall K=alle, W=∞ — ein Regler
  statt zweier Extreme. Konsequenz: keine Optimalitätsgarantie (was `GOAL.md`
  ausdrücklich als Nicht-Ziel führt: „Heuristik-Ratgeber, kein Löser mit
  Beweis"). Gemessen **0,11 s (3 Slots) bis 0,46 s (6 Slots mit Deep und
  weissem Slot)** bei K=20/W=40.
- **D — Ganzzahlige Optimierung (`ortools` CP-SAT / `pulp`).** Beweisbar
  optimal für lineare Ziele. Konsequenz: **neue Dependency** (ortools ~50 MB
  im PyInstaller-Bundle für ein 20-MB-Werkzeug), und die Zielfunktion ist
  nicht linear — multiplikative Raten, „nur der stärkste zählt",
  Exklusivgruppen. Linearisierbar, aber nur unter Annahmen, die die
  gemessenen Regeln in `model.py` gerade verneinen. Der Beweis wäre ein
  Beweis über ein falsches Modell.

**Entscheidung:** C. Sie fasst die Kopplung zwischen den Slots exakt (weil
sie den echten Scorer benutzt), sie ist über zwei Zahlen (K, W) einstellbar,
und ihre Kosten sind gemessen statt geschätzt.

**Voreinstellung: K=20, W=40.** Der ungünstigste reale Fall bleibt damit
unter einer halben Sekunde. Der `performance-tuner` bestätigt oder korrigiert
das in S11.

**Warum die Poolgrösse die Kosten nicht treibt — und was das für K bedeutet.**
Die Beam-Suche kostet `Slots × W × K` Bewertungen. **K ist eine Obergrenze auf
die Verzweigung, keine Quote auf den Pool.** Gegenprobe bei K=20/W=40:
`Wylder's Chalice` (weisser Slot, Pool 208) und `Wylder's Urn` (nur farbig,
Pool höchstens 56) brauchen **exakt gleich viele Bewertungen — 3 929**. Der
weisse Slot vervierfacht den rohen Produktraum und ändert die Suchkosten
nicht. Er verteuert allein den Vorsortierlauf, und der ist eine Bewertung je
*besessenem Relikt* (309), nicht je Slot-Kandidat.

Die Kehrseite gehört dazu: K=20 behält bei einem farbigen Slot ~40 % des
Pools, bei einem weissen aber nur ~10 %. Die Vorsortierung trägt an einem
weissen Slot also deutlich mehr Last. Sie bewertet jedes Relikt **isoliert**,
also ohne die Wechselwirkungen, um derentwillen es die Beam-Suche überhaupt
gibt — ein Relikt, das erst neben einem anderen stark wird, kann an einem
weissen Slot durch das Raster fallen. Das ist die schärfste bekannte Schwäche
des Verfahrens. Sie ist erträglich, weil `GOAL.md` keine Optimalität verlangt,
und sie ist **messbar**: Prüfpunkt in der Risikotabelle, K für weisse Slots
notfalls eigenständig höher setzen. Weil die Kosten linear in K sind und ein
Lauf 0,46 s dauert, ist dafür Luft.

**Ausgestaltung, verbindlich für `search.py`:**
1. **Slot-Reihenfolge: die des Gefässes.** Meine erste Fassung schrieb „engste
   Farbe zuerst, Weiss zuletzt" vor. Gemessen macht das **keinen Unterschied** —
   gleiche Trefferqualität, 0,46 s gegen 0,48 s. Die Regel wird gestrichen,
   statt sie ohne Beleg mitzuschleppen. Die Reihenfolge des Gefässes ist
   ausserdem stabil und damit reproduzierbar, was AD-009 Punkt 6 braucht.
2. **Farbsymmetrie:** ein Gefäss `[0, 0, 1]` hat zwei austauschbare rote
   Slots. Innerhalb einer Gruppe gleichfarbiger Slots wird nur in
   aufsteigender Kandidatenreihenfolge gewählt. Das verkleinert den Baum und
   verhindert, dass die Ergebnisliste dieselbe Belegung zweimal in
   vertauschten Slots zeigt.
3. **Exemplar-Eindeutigkeit über Handles** — siehe AD-013. Nicht optional:
   ohne sie sind auf `Wylder's Urn` **40 von 40** Vorschlägen nicht tragbar.
4. **Abbruchprüfung** zwischen den Slot-Ebenen, nicht innerhalb (siehe AD-006).
5. **Ausgabe:** die besten `top_n` Endzustände, nicht nur der beste — der
   Spieler sieht Alternativen und kann die Begründung vergleichen (A5).

**Konsequenzen:** Leicht wird — mehr Zielrichtungen, andere Slotzahlen,
Budgetanpassung durch den `performance-tuner` ohne Codeänderung. Dauerhaft
schwer wird — jede Aussage der Form „das ist das Beste, was du bauen kannst".
Der Berater darf so nicht formulieren. Nutzersprache: „Best found" / „Top
suggestions", nie „Optimal".

**Umkehrbarkeit:** leicht. `search.py` ist rein und hinter
`AdvisorRequest`/`AdvisorResult` gekapselt; ein anderes Verfahren ersetzt
genau diese eine Datei.

---

### AD-004 — Zielrichtungen als Registry reiner Funktionen `Build -> GoalScore`, mit ausdrücklicher Unwissensliste (2026-09-01, Status: aktiv)

**Kontext:** A3 verlangt mindestens zwei benannte Zielrichtungen und
Erweiterbarkeit. A7 verlangt, dass das Programm sagt, wo die Spieldateien
keine Antwort geben. Beides trifft sich an derselben Stelle: eine
Zielrichtung ist nicht nur eine Zahl, sondern eine Zahl *mit erklärtem
Geltungsbereich*.

**Optionen:**
- **A — Ein Gewichtsvektor über Feldnamen** (`{"physicsAttackRate": 1.0, …}`),
  Zielrichtungen als Datensätze. Sehr einfach erweiterbar, sogar zur Laufzeit.
  Konsequenz: kann nur linear über `build.rates` — kann kein Attack Rating
  bilden (das braucht die Waffe, die Attributkurven und die Skalierung), kann
  kein effektives HP bilden (das braucht `build.derived` mal die
  Schadensminderung). Die beiden geforderten Zielrichtungen sind genau die,
  die so nicht ausdrückbar sind.
- **B — `if goal == "damage": … elif goal == "tank": …` in der Suche.**
  Konsequenz: jede neue Zielrichtung fasst die Suche an. Genau die Kopplung,
  die AD-001 vermeiden soll.
- **C — Eine `Goal`-Datenklasse mit `score(build, ctx) -> GoalScore`, in
  einem Dict registriert.** Konsequenz: eine neue Zielrichtung ist eine
  Funktion plus ein Registry-Eintrag; die Suche kennt nur das Protokoll.

**Entscheidung:** C.

```python
# advisor/types.py  (illustrierend, kein Anwendungscode)
@dataclass(frozen=True)
class GoalScore:
    value: float                       # die Rankinggrösse, gross = besser
    display: str                       # "Attack rating 812" (Englisch)
    unit: str                          # "AR" | "effective HP" | ...
    unknowns: tuple[str, ...]          # A7: was diese Zahl NICHT weiss
    weights_note: str                  # die offengelegte eigene Annahme

@dataclass(frozen=True)
class Goal:
    id: str                            # "max_damage"
    label: str                         # "Maximise damage"       (Englisch)
    blurb: str                         # ein Satz für die Oberfläche
    score: Callable[[model.Build, GoalContext], GoalScore]

GOALS: dict[str, Goal] = {...}         # die Registry
```

**Die zwei ausgelieferten Zielrichtungen:**

**`max_damage` — „Maximise damage".** Rankinggrösse ist das Attack Rating der
gewählten Referenzwaffe unter `build.attributes`, mit den Angriffsraten
darauf — berechnet von `nrplanner/damage.py` (AD-005), also von genau
derselben Rechnung, die die Waffentafel zeigt.
`unknowns` enthält *immer mindestens*:
- „Attack rating has not been verified against an in-game number." (README
  Known limits)
- „Spell damage is not in the game data, so spells are not rated." (README)
- „Critical-only bonuses are excluded — attack rating is the ordinary hit."
  (bereits so in `_refresh_weapon_damage` entschieden, siehe `model.CRIT_RATE`)
- bei fehlender Referenzwaffe: „No armament selected — ranked on attack
  multipliers only, without weapon scaling."

**`min_damage_taken` — „Minimise damage taken".** Rankinggrösse ist
effektives HP: `build.derived["HP"]` geteilt durch die Schadensminderung, je
Schadensart getrennt gerechnet (die vier physischen —
`slash/blow/thrust/neutralDamageCutRate` — und die vier elementaren —
`magic/fire/thunder/darkDamageCutRate`), dann zu einem Skalar gemittelt.
**Die Mittelung ist eine Annahme, und sie wird ausgesprochen:** die
Spieldateien sagen nichts darüber, wie oft welche Schadensart vorkommt. Daher
gleiches Gewicht auf allen acht, und `weights_note` sagt genau das im
Klartext. Wer es besser weiss, verstellt die Gewichte (offene Frage OF-3).
`unknowns` enthält mindestens:
- „The game data gives no relative frequency of damage types; all eight are
  weighted equally."
- „Ailment and status resistance are not part of this figure."
- „The break threshold is unknown." (README, sofern relevant angezeigt)

**Nachtrag 2026-09-01 — Beschluss des `director` zu OF-3 und OF-5.**

*OF-5 (bestätigt):* Ohne gewählte Referenzwaffe wird der Lauf **nicht**
verweigert. `max_damage` rechnet gegen eine benannte Annahme, und die Annahme
steht sichtbar im Ergebnis. Begründung des `director`, die ich übernehme:
A7 ist erfüllt, solange die Annahme dasteht — Schweigen wäre der Verstoss,
nicht die Annahme.

*OF-3 (noch beim Nutzer):* Ob die Gewichtung der acht Schadensarten ein
Bedienelement wird, ist offen. Der Entwurf muss beides tragen, **ohne die
Registry umzubauen**. Deshalb verbindlich: die Gewichte sind **Daten im
`GoalContext`**, nicht Konstanten in der Zielfunktion.

```python
# advisor/types.py  (illustrierend, kein Anwendungscode)
@dataclass(frozen=True)
class Weighting:
    id: str                            # "even"
    label: str                         # "All damage types equally" (Englisch)
    note: str                          # der Satz, der in weights_note landet
    weights: Mapping[str, float]

@dataclass(frozen=True)
class GoalContext:
    data: Mapping
    hero: Mapping
    level: int
    weapon: Mapping | None
    weighting: Weighting               # Voreinstellung: DEFAULT_WEIGHTING
```

`score()` liest `ctx.weighting.weights` und schreibt `ctx.weighting.note` nach
`GoalScore.weights_note`. Bleibt es bei der festen Annahme, liefert der
`AdvisorController` immer `DEFAULT_WEIGHTING` — ein Bedienelement später
liefert eine andere Instanz und sonst ändert sich nichts. `weighting.id`
gehört in den Cache-Schlüssel (AD-007), sonst überlebt ein Ergebnis den
Wechsel der Gewichtung.

Der Punkt ist die Trennung: **die Zielfunktion kennt keine Zahlen, nur woher
sie kommen.** Eine Gewichtung fest in `min_damage_taken` einzubacken wäre
heute drei Zeilen kürzer und machte OF-3 später zu einem Eingriff in die
Zielrichtung statt in den Aufrufer.

**Gemeinsame `unknowns` für jede Zielrichtung**, von der Suche beigesteuert,
nicht von der Zielrichtung:
- „N of your relics carry effects that only apply under a condition. They
  were not counted." — folgt direkt daraus, dass `model.compute()`
  konditionale Effekte aus den Totals hält, solange sie nicht `declared` sind.
  Ohne diesen Satz sähe ein Spieler ein starkes situatives Relikt ungenutzt
  und hielte den Berater für kaputt.
- Deep-of-Night-Kennzeichnung und die **Curses** der vorgeschlagenen Relikte:
  Curses gehören zum Relikt und gehen in die Bewertung ein, genauso wie
  `Planner.recompute()` es tut (`selected_curses()`). Ein Deep-Vorschlag ohne
  genannten Curse wäre unehrlich.

**Konsequenzen:** Leicht wird — eine dritte Zielrichtung („maximise FP
economy", „maximise item discovery") ist eine Funktion und ein Eintrag.
Dauerhaft schwer wird — Zielrichtungen, die *nicht* aus einem `Build`
ablesbar sind (etwa etwas über den Spielverlauf). Die müssten
`GoalContext` erweitern, und das berührt alle.

**Umkehrbarkeit:** leicht.

---

### AD-005 — Die Attack-Rating-Rechnung wird aus `app.py` nach `nrplanner/damage.py` gezogen, bevor der Berater gebaut wird (2026-09-01, Status: aktiv)

**Kontext:** Befund F1. `Planner._refresh_weapon_damage` (197 Zeilen)
enthält die einzige Stelle, an der aus einer Waffe, den Attributen und den
Raten eine Schadenszahl wird. Sie ist an Widgets, an `self.active_weapon` und
an Klassenkonstanten von `Planner` gebunden. Die Zielrichtung `max_damage`
braucht sie.

**Optionen:**
- **A — Der Berater rechnet sein eigenes Attack Rating.** Keine Änderung am
  Bestand. Konsequenz: zwei Schadensrechnungen. Die Startwaffen-Sonderregel
  (Slot 1 + eigene Startwaffe, in Spiel verifiziert 2026-08-22), der
  Ausschluss der Krit-Rate und die Waffenklassen-Buffs müssten zweimal
  stimmen. Der Berater könnte dann ein Build empfehlen, dessen Zahl die
  Waffentafel bestreitet.
- **B — Der Berater rankt ohne Attack Rating**, nur über das Produkt der
  Angriffsraten. Kein Umbau. Konsequenz: er ignoriert die Attributskalierung
  vollständig — ein Relikt mit +5 Stärke wäre für „maximise damage" wertlos,
  obwohl es genau dort wirkt. Die Zielrichtung wäre ihren Namen nicht wert.
- **C — Extraktion in ein reines Modul.** `damage.rate_with_effects(weapon,
  tier, build, data, starting_slot) -> DamageBreakdown`, plus die Konstanten
  aus F6. `app.py` ruft es und formatiert nur noch. Konsequenz: ein Eingriff
  in `app.py`, der vor dem Berater liegt und einen Regressionsschutz braucht.

**Entscheidung:** C. Es ist die einzige Option, bei der es die Zahl genau
einmal gibt.

**Konsequenzen:** Leicht wird — die Schadensrechnung ist testbar (heute ist
sie es nicht), und `_refresh_weapon_damage` schrumpft von 197 auf
schätzungsweise 60 Zeilen reine Darstellung, was F3 ein Stück zurücknimmt.
Dauerhaft schwer wird — nichts; die Richtung ist eine Verbesserung in jeder
Hinsicht. Das Risiko liegt allein in der Ausführung: eine stille
Verhaltensänderung beim Verschieben. Deshalb der Golden-Test in S1.

**Umkehrbarkeit:** mittel. Die Extraktion selbst ist trivial rückgängig zu
machen; sobald der Berater darauf zeigt, hängt mehr daran.

---

### AD-006 — Hintergrundlauf über `QThread` + Worker-Objekt + Signale, mit kooperativem Abbruch (2026-09-01, Status: aktiv)

**Kontext:** A6 verlangt, dass die Oberfläche bedienbar bleibt. Gemessen
0,11 s (3 Slots) bis 0,46 s (6 Slots mit Deep und weissem Slot) reine Python-Rechnung je Lauf. Das Programm ist Qt, nicht Tkinter,
und `nrplanner/firstrun.py` fährt bereits ein Worker-Objekt per `moveToThread`
mit `progress`/`finished`-Signalen.

**Optionen:**
- **A — `QThread` + Worker + Signale.** Ein Muster, das im Projekt schon
  betrieben wird. Konsequenz: durch den GIL echte Nebenläufigkeit nur bedingt;
  bei einer halben Sekunde reiner Python-Rechnung sind kurze Ruckler im Hauptthread
  möglich, aber keine Blockade. Kein neues Konzept, keine Dependency.
- **B — `multiprocessing` / `ProcessPoolExecutor`.** Echte Parallelität, GIL
  irrelevant. Konsequenz: der Snapshot (~20 MB JSON) muss in den Kindprozess;
  unter PyInstaller braucht es `freeze_support()` und ein sauberes
  Einstiegsverhalten für die gefrorene EXE — ein bekannt fehleranfälliger Weg,
  bei dem ein Fehler als „Programm startet sich selbst mehrfach" auftritt.
  Prozessstart plus Übergabe kostet mehr als der Lauf selbst.
- **C — Häppchenweise im Hauptthread über `QTimer`.** Kein Thread, keine
  Race-Bedingung mit `model.configure()` (F4). Konsequenz: die Latenz wird
  schlechter, nicht besser, und die Suchschleife müsste als Zustandsmaschine
  geschrieben werden — `search.py` verlöre seine Reinheit und damit seine
  Testbarkeit.

**Entscheidung:** A. Der gemessene Lauf ist zu kurz, als dass B seine
Betriebskosten wert wäre, und C zahlt mit genau der Eigenschaft, die AD-001
erkauft hat. Betreibbarkeit zählt: das Team fährt dieses Muster bereits.

**Verbindliche Ausgestaltung:**

1. **Wie das Ergebnis in die Oberfläche kommt.** Ein `QObject`-Worker mit den
   Signalen `ready(object)`, `failed(str)`, `progress(int, int)` wird per
   `moveToThread(thread)` in einen `QThread` verschoben; `thread.started`
   ruft `worker.run`. Die Signale sind über die Thread-Grenze hinweg
   `Qt.QueuedConnection` — Qt stellt die Nutzlast in die Event-Loop des
   Empfängers, und der Slot läuft im **Hauptthread**. Nur dort werden Widgets
   angefasst. **Kein Widget-Zugriff aus dem Worker**, auch nicht lesend.
2. **Nicht das Muster aus `firstrun.py` kopieren.** Dort steht
   `while not thread.wait(50): QApplication.processEvents()` — eine modale
   Wartschleife, richtig für einen Startbildschirm, falsch für den Berater:
   starten, `ready` verbinden, zurückkehren. Kein `processEvents()`.
3. **Veraltete Ergebnisse dürfen nicht ankommen.** Der `AdvisorController`
   führt einen monoton wachsenden **Generationszähler**. Jede Anfrage bekommt
   die aktuelle Generation mit, und `AdvisorResult` trägt sie zurück. Der
   Slot im Hauptthread verwirft jedes Ergebnis, dessen Generation nicht die
   aktuelle ist — **wortlos, ohne die Anzeige anzufassen**. Das ist die
   einzige Absicherung, die trägt: Abbrechen allein genügt nicht, weil ein
   Lauf, der zwischen der letzten Abbruchprüfung und dem `emit` steht, sein
   `ready` bereits abgeschickt hat, während der Spieler das Gefäss wechselt.
   Der Zähler wird erhöht bei: Wechsel von Nightfarer, Gefäss, Deep-Schalter,
   Zielrichtung, Level, Referenzwaffe, deklarierten situativen Effekten,
   Neu-Scan des Saves und Datenneuaufbau — also bei **jeder** Änderung, die
   in den Cache-Schlüssel aus AD-007 eingeht. Beides aus einer Quelle
   abzuleiten ist Absicht: was den Cache-Schlüssel ändert, macht ein
   laufendes Ergebnis veraltet, und umgekehrt. Zwei getrennte Listen liefen
   auseinander.
4. **Höchstens ein Lauf gleichzeitig.** Eine neue Anfrage bricht die alte ab
   und erhöht die Generation. Der `QThread` wird nicht neu erzeugt, solange
   der alte noch läuft: `requestInterruption`, `quit`, dann auf `finished`
   den nächsten starten. Kein `terminate()`, kein `wait()` im Hauptthread.
5. **Anfragen entprellen** über einen `QTimer` mit `setSingleShot(True)`
   (Vorschlag 250 ms; `performance-tuner` setzt den Wert), damit ein
   gezogener Level-Regler nicht vierzig Läufe auslöst.
6. **Kooperativer Abbruch:** `search.beam()` nimmt ein
   `should_cancel: Callable[[], bool]` und prüft es **zwischen den
   Slot-Ebenen** — bei 6 Ebenen und höchstens 0,98 s ist die gröbste
   Reaktionszeit ~0,15 s, fein genug. Innerhalb einer Ebene zu prüfen kostet
   mehr, als es bringt.
7. **Race gegen F4:** ein Datenneuaufbau (`load_data` nach Spiel-Patch, oder
   ein Neu-Scan des Saves) bricht jeden laufenden Lauf ab, erhöht die
   Generation und verwirft den Cache, *bevor* `model.configure()` erneut
   läuft. `model` hält Modulglobals; ein Lauf, der währenddessen rechnet,
   rechnet auf einer halb ersetzten Tabelle.
8. **Über die Thread-Grenze gehen nur unveränderliche Datenklassen.** Keine
   Widgets, keine `QSettings` (die sind nicht thread-affin nutzbar wie hier
   gebraucht), kein `Inventory`-Objekt, das der Hauptthread weiter anfasst.
   `AdvisorRequest` und `AdvisorResult` sind `frozen`; die Kandidatenliste
   wird beim Bauen des Requests eingefroren, nicht im Worker aus dem
   lebenden `Inventory` gelesen.
9. **Fehler im Worker sind ein Signal, kein Absturz.** `run()` fängt breit
   und sendet `failed(text)`. Eine Ausnahme in einem `QThread` beendet sonst
   still den Lauf, und die Oberfläche wartet für immer auf ein `ready`.

**Konsequenzen:** Leicht wird — Abbrechen, Fortschritt anzeigen, Budget
messen. Dauerhaft schwer wird — mehrere Läufe echt parallel (etwa alle
Gefässe gleichzeitig); dafür bräuchte es B.

**Umkehrbarkeit:** mittel. Weil `search.py` rein und abbrechbar ist, lässt
sich B später hinter derselben `AdvisorController`-Fassade nachrüsten.
Kosten: das PyInstaller-Verhalten des gefrorenen Artefakts.

---

### AD-007 — Ergebnis-Cache nur im Speicher (LRU), nichts auf Platte (2026-09-01, Status: aktiv)

**Kontext:** Der Spieler wechselt zwischen Gefässen und Nightfarern hin und
her. Jeder Wechsel wäre ein Lauf von bis zu 0,46 s.

**Optionen:**
- **A — Kein Cache.** Einfachst. Konsequenz: Zurückklicken auf ein Gefäss
  rechnet neu; die Oberfläche fühlt sich zäh an, obwohl die Antwort bekannt ist.
- **B — LRU im Speicher, an den `AdvisorController` gebunden** (Vorschlag 32
  Einträge). Konsequenz: ein paar MB, und mit dem Fenster ist er weg.
- **C — Zusätzlich auf Platte, neben dem Snapshot unter `paths`.** Konsequenz:
  überlebt Neustarts — und wird falsch, sobald der Spieler ein Relikt
  einschmilzt, ein neues findet oder das Spiel gepatcht wird. Ein Cache, der
  einen Vorschlag über ein nicht mehr besessenes Relikt zeigt, verletzt A7
  direkt. Der Schutz dagegen wäre eine Invalidierungslogik, die teurer zu
  pflegen ist als der halbsekündige Lauf, den sie spart.

**Entscheidung:** B.

**Cache-Schlüssel — vollständig, damit nichts stillschweigend fehlt:**
`(snapshot_fingerprint, hero_id, level, canonical_slots, deep, goal_id,
inventory_fingerprint, weapon_fingerprint, declared_fingerprint, budget)`

- `snapshot_fingerprint` = `meta.regulation_sha256` + `meta.extract_version`.
- `inventory_fingerprint` = Hash über die sortierten Tupel
  `(handle, relic_id, sorted(effect_ids), sorted(curse_ids), colour, is_deep)`.

> **Korrektur vom 2026-09-01, ersetzt die ursprüngliche Fassung dieser Zeile.**
> Ursprünglich stand hier „ausdrücklich **ohne** `handle`", mit der Begründung
> aus `chalices.py`: Handles werden beim Einschmelzen oder Rechnerwechsel neu
> vergeben, und ein Handle im Schlüssel entwertete den Cache ohne jede
> Änderung am Besitz. Diese Begründung ist für sich richtig und **hier
> trotzdem falsch**, seit AD-013 gilt: das Ergebnis *enthält* Handles. Ein
> Treffer im Cache nach einer Neuvergabe lieferte Handles, die auf ein anderes
> oder gar kein Relikt zeigen — ein Vorschlag, den der Spieler nicht tragen
> kann, also genau der Fehler, den AD-013 verhindern soll. Die Abwägung ist
> einseitig: ein überflüssiger Cache-Fehlschlag kostet 0,46 s, ein veralteter
> Handle kostet eine falsche Empfehlung. Handles gehören in den Schlüssel.
- `declared_fingerprint` deckt die vom Spieler als aktiv erklärten
  konditionalen Effekte ab — sie ändern die Totals und damit das Ranking.

**Konsequenzen:** Leicht wird — sofortige Antwort beim Hin- und Herwechseln.
Dauerhaft schwer wird — nichts von Belang; ein Plattencache liesse sich
nachrüsten, wenn er je gebraucht wird (Bedingung siehe „Bewusst nicht getan").

**Umkehrbarkeit:** leicht.

---

### AD-008 — Das Suchproblem wird über die kanonisierte Slot-Farbmenge geschlüsselt, nicht über die Gefäss-Id (2026-09-01, Status: aktiv)

**Kontext (gemessen):** Der Snapshot führt **74 Gefässe**. Nach Sortierung
der Slotfarben bleiben davon **26 verschiedene 3-Slot-Muster** und **47
verschiedene 6-Slot-Muster** (mit den Deep-Slots). `[0,0,1]`, `[0,1,0]` und
`[1,0,0]` sind dasselbe Problem mit vertauschten Spalten; das häufigste
Muster kommt siebenmal vor.

**Optionen:**
- **A — Je Gefäss ein Problem.** Naheliegend, denn der Spieler wählt ein
  Gefäss. Konsequenz: bis zu 74 Läufe für dieselben Antworten; der Cache
  trifft bei einem Gefässwechsel nie, obwohl die Antwort identisch ist.
- **B — Kanonische Form: sortiertes Tupel der Slotfarben + Deep-Flag.**
  Konsequenz: `[0,0,1]`, `[0,1,0]` und `[1,0,0]` sind ein Problem. Beim
  Anzeigen müssen die Ergebnisse auf die tatsächliche Slot-Reihenfolge des
  gewählten Gefässes zurückabgebildet werden — ein Permutationsschritt in
  `worker.py`.

**Entscheidung:** B. Die Rückabbildung ist ein Dutzend Zeilen; der
Trefferanteil im Cache steigt um ein Vielfaches, und A3 („für jedes bekannte
Kelch-Layout") wird dadurch überhaupt erst mit vertretbarem Aufwand prüfbar:
der `qa-engineer` prüft **26 bzw. 47 kanonische Probleme statt 74 Gefässe**,
und die vollständige Abdeckung aller Layouts für beide Zielrichtungen kostet
gemessen 47 × 0,46 s ≈ **22 s** statt 74 × 0,46 s ≈ 34 s — pro Zielrichtung,
im Hintergrund, und nur wenn A3 vollständig durchgeprüft wird.

**Konsequenzen:** Leicht wird — Abdeckung aller Layouts, hohe Cache-Trefferrate.
Dauerhaft schwer wird — eine künftige Regel, die ein Gefäss *ausser* über
seine Slotfarben unterscheidet (etwa ein gefässgebundener Bonus). Gäbe es die,
müsste die Gefäss-Id in den Schlüssel zurück. Der Snapshot kennt heute nichts
dergleichen: ein `vessels`-Eintrag hat `id`, `name`, `icon`, `hero_type`,
`slots`, `deep_slots` — und nur die letzten beiden wirken auf einen Build.

**Umkehrbarkeit:** leicht.

---

### AD-009 — Testsockel headless, ohne neue Laufzeit-Dependency (2026-09-01, Status: aktiv; Werkzeug auf `pytest` geändert, siehe Nachtrag)

**Kontext:** Kein Test im Repo (F2), und A9 verlangt eine Bestätigung gegen
ein gebautes Artefakt. Der Berater rankt auf `model.py`, dessen Regeln
grösstenteils gemessen und nirgends abgesichert sind. AD-005 verschiebt
funktionierenden Code und braucht einen Regressionsschutz.

**Optionen:**
- **A — `pytest` + `pytest-qt`.** Komfortabel, parametrisierbar, im
  Ökosystem üblich. Konsequenz: **zwei neue Dependencies**, freigabepflichtig
  durch den `director`. Reine Entwicklungsabhängigkeit, also kein Einfluss auf
  das Bundle — aber `requirements.txt` trennt heute nicht zwischen Laufzeit
  und Werkzeug (F8), was das Risiko birgt, dass sie im Artefakt landen.
- **B — `unittest` aus der Standardbibliothek.** Konsequenz: keine Freigabe
  nötig, kein Bundle-Einfluss, läuft auf jedem Python 3.11+ ohne
  Vorbereitung; dafür umständlicher bei parametrisierten Tabellen
  (`subTest` statt `parametrize`).
- **C — Gar keine Tests, nur manuelle Prüfung durch den `qa-engineer`.**
  Konsequenz: A9 nicht erfüllbar; und AD-005 würde ohne Netz ausgeführt.

**Entscheidung:** B für diesen Zyklus. Die Tests, die der Berater braucht,
sind Tests reiner Funktionen über Datenklassen — genau der Fall, in dem
`unittest` nichts kostet. Damit ist der Sockel nicht von einer Freigabe
abhängig und die Arbeit kann sofort beginnen. **Der `director` kann A
freigeben; dann ist der Wechsel trivial**, weil `unittest`-Tests unter
`pytest` unverändert laufen — die umgekehrte Richtung gilt nicht. Das ist der
eigentliche Grund für B: es ist die Option, die die andere offenhält.

**Testsockel, Mindestumfang (Vorlage für den `qa-engineer`, T-002):**
1. **Golden-Test für AD-005:** ein Satz Builds, für die
   `_refresh_weapon_damage` heute Zahlen liefert; nach der Extraktion muss
   `damage.py` dieselben liefern. Aufzunehmen **vor** dem Verschieben.
2. **Stacking-Eigenschaft (bindet F5):** für jeden Effekt der Daten gilt —
   `stacking.repetition(e) == STACKS` genau dann, wenn zwei Kopien in
   `model.compute()` das Total doppelt bewegen.
3. **Farb-Nebenbedingung:** kein Vorschlag legt ein Relikt in einen Slot, den
   `inventory.relics_for(colour, deep)` dafür nicht zulässt (A4).
4. **Kein Relikt doppelt (AD-013):** kein Handle erscheint zweimal in einem
   Vorschlag. Der Test muss ein Gefäss mit **wiederholten Slotfarben**
   benutzen (`Wylder's Urn`, `[0,0,1]`) — dort schlägt die Regel ohne
   Absicherung in 40 von 40 Fällen fehl, bei einem Gefäss mit lauter
   verschiedenen Farben nur in 5 von 40. Ein Test auf dem gutmütigen Gefäss
   bestünde und bewiese nichts.
5. **Monotonie:** eine echte Verbesserung im Bestand (ein zusätzliches,
   streng besseres Relikt) darf die beste gefundene Punktzahl nicht senken.
6. **Determinismus:** derselbe Request liefert zweimal dasselbe Ergebnis,
   Reihenfolge eingeschlossen. Ohne das ist der Cache nicht prüfbar.
7. **Honesty-Vertrag (A7):** jeder `GoalScore` von `max_damage` führt den
   Attack-Rating-Vorbehalt; jeder `AdvisorResult` mit ungezählten konditionalen
   Effekten sagt es.

**Nachtrag 2026-09-01 — der `director` hat `pytest` freigegeben.** Damit gilt
Option A, aber nur unter der Auflage, die den Einwand gegen sie entkräftet:
**ausschliesslich als Entwicklungs-Abhängigkeit in einer eigenen
`requirements-dev.txt`**, nicht in `requirements.txt` und nicht im
PyInstaller-Artefakt. Genau dafür war die Trennung aus F8 ohnehin schon Teil
von S1; sie ist jetzt keine Aufräumarbeit mehr, sondern Voraussetzung.

Der Kern der Entscheidung bleibt unberührt: headless, keine Laufzeit-
Abhängigkeit, Tests vor der Extraktion aus AD-005. Nur das Werkzeug ändert
sich. Der Mindestumfang unten gilt unverändert — er ist als Liste von
Eigenschaften formuliert, nicht als Liste von Testfunktionen, und ist damit
vom Rahmenwerk unabhängig.

**Konsequenzen:** Leicht wird — der Umbau in AD-005 ist abgesichert, A9
bekommt eine Grundlage, und die Eigenschaftstabellen aus Punkt 2 und 3 lassen
sich parametrisieren statt über `subTest` zu laufen. Dauerhaft schwer wird —
Tests der Qt-Schicht; die gibt es hier nicht und sie sind auch nicht Teil
dieses Entwurfs. Der `ui-ux-designer` und der `qa-engineer` prüfen die
Oberfläche am Artefakt.

**Umkehrbarkeit:** leicht.

---

### AD-010 — Die Unwissensliste ist Teil des Ergebnisses, nicht eine Fussnote in der Oberfläche (2026-09-01, Status: aktiv)

**Kontext:** Hausregel und A7. Die naheliegende Umsetzung ist ein statischer
Hinweistext im Beratungs-Tab. Der taugt nicht: welche Lücken gelten, hängt
vom konkreten Lauf ab — ob eine Waffe gewählt ist, ob Deep-Slots im Spiel
sind, wie viele besessene Relikte konditional sind, ob der Datenstand aus dem
gebündelten Snapshot statt aus der Installation kommt (F7).

**Optionen:**
- **A — Statischer Warntext im Tab.** Nichts zu bauen. Konsequenz: er sagt
  immer dasselbe, wird nach dem dritten Mal nicht mehr gelesen, und er sagt
  nichts über *diesen* Vorschlag.
- **B — `unknowns` als Pflichtfeld auf `GoalScore` und `AdvisorResult`,
  vom Rechner gefüllt.** Konsequenz: die Oberfläche kann ihn nicht vergessen,
  weil er Teil dessen ist, was sie zeichnet; und der Testsockel kann ihn
  prüfen (AD-009, Punkt 7).

**Entscheidung:** B. A7 ist ein Abnahmekriterium; ein Kriterium, dessen
Erfüllung von der Sorgfalt beim Zeichnen abhängt, ist nicht erfüllt.

**Verbindlicher Inhalt jedes `AdvisorResult`:**
- `unknowns` der Zielrichtung (siehe AD-004),
- `weights_note`, wo der Berater eine eigene Annahme getroffen hat,
- `not_counted`: konditionale Effekte im Besitz, die nicht in die Totals
  eingingen, mit Anzahl,
- `curses`: die Curses der vorgeschlagenen Deep-Relikte, benannt,
- `data_note`: aus `meta` — gebündelter Snapshot oder frisch aus der
  Installation, mit `data_version`,
- `budget_note`: Suchbreite und ob der Lauf abgeschnitten wurde. Ein Ergebnis
  aus einer beschnittenen Suche muss sagen, dass es beschnitten wurde.

**Nutzersprache, verbindlich:** „Best found", „Top suggestions", „Not
counted", „Not verified" — nie „Optimal", „Best possible", „Guaranteed".

**Konsequenzen:** Leicht wird — A7 ist prüfbar statt behauptet. Dauerhaft
schwer wird — der Vorschlag ist textlastiger, als eine reine Rangliste es
wäre. Das ist der Preis der Hausregel und die Aufgabe des `ui-ux-designer`
(T-004), nicht ein Grund, die Regel zu lockern.

**Umkehrbarkeit:** mittel. Ein Pflichtfeld wieder zu entfernen ist leicht;
die Zusage an den Nutzer zurückzunehmen ist es nicht.

---

### AD-011 — Prüfvokabular als freie Funktionen in `binary.py`, nicht als Methoden der `Reader`-Klasse (2026-09-01, Status: aktiv, vom `director` angenommen)

**Kontext:** Der `security-reviewer` (T-003) fand an fünf Stellen aus der
Datei gelesene Zähler, die ungeprüft Schleifen und Allokationen steuern
(`savefile.py`, `bnd4.py`, `fmg.py`, `dvdbnd.py`, `tae.py`), und vier
Endlosschleifen beim Lesen UTF-16-terminierter Namen. Sein Vorschlag: eine
gemeinsame Hilfsfunktion im `binary.Reader` statt fünf Einzelprüfungen. Die
Stossrichtung ist richtig — eine Regel, ein Ort.

**Nur trägt der vorgeschlagene Ort nicht.** Nachgezählt:

| Modul | benutzt `binary.Reader` | benutzt `struct` direkt |
|-------|------------------------|-------------------------|
| `bnd4.py` | ja (5×) | — |
| `param.py` | ja (3×) | 3× |
| `savefile.py` | **nein** | 18× |
| `tae.py` | **nein** | 13× |
| `fmg.py` | **nein** | 6× |
| `dvdbnd.py` | **nein** | 5× |

Eine Methode auf `Reader` erreicht **zwei der fünf** Fundstellen. Die drei
übrigen bleiben ungeprüft — darunter `savefile.py`, ausgerechnet der einzige
Parser, der eine Datei liest, die nicht die Spielinstallation, sondern der
laufende Spielprozess schreibt, und der damit am ehesten halbfertige oder
beschädigte Zähler sieht (`_read_settled` existiert genau deswegen). Die
Empfehlung würde in ihrer wörtlichen Form die am stärksten exponierte Stelle
auslassen und dabei so aussehen, als sei das Problem behoben.

Auch die Endlosschleife hat nur einen ihrer vier Auftritte in
`Reader.cstr_at`: `while self.data[end:end+2] != b"\0\0": end += 2` läuft
unbegrenzt weiter, wenn der Terminator fehlt oder ungerade ausgerichtet ist
— Python schneidet über das Ende hinaus zu `b""` ab, und `b"" != b"\0\0"`.
Die anderen drei stehen in `fmg.py`, `savefile.py` und `tpf.py`.

**Optionen:**
- **A — Prüfmethoden auf `Reader`, Rest so lassen.** Kleinster Eingriff.
  Konsequenz: deckt 2 von 5 Zählern und 1 von 4 Schleifen ab, und der Befund
  gilt als erledigt. Der schlechteste mögliche Ausgang.
- **B — Prüfmethoden auf `Reader`, und `savefile`/`fmg`/`dvdbnd`/`tae` auf
  `Reader` migrieren.** Vollständig und am Ende die sauberste Struktur.
  Konsequenz: vier Parser umschreiben, ~40 `struct`-Aufrufe, **ohne einen
  einzigen Test** (F2). Genau der Umbau, bei dem ein Vorzeichen- oder
  Offset-Fehler wochenlang unbemerkt bleibt und den Relikt-Bestand still
  falsch liest.
- **C — Freie Prüffunktionen auf Modulebene in `binary.py`, aufrufbar ohne
  `Reader`.** `Reader` bekommt dünne Methoden, die dorthin delegieren; die
  vier struct-basierten Parser rufen dieselben Funktionen direkt auf — je
  eine Zeile an jeder der fünf Zählerstellen, kein Umschreiben.

**Entscheidung:** C.

```python
# nrdata/binary.py  (illustrierend, kein Anwendungscode)
def check_count(count, item_size, remaining, what) -> int:
    """A count read from the file, refused when it cannot fit what is left."""

def cstr16_at(data, offset, limit=None) -> str:
    """UTF-16 up to the terminator, or to the end of the buffer."""
```

Der Punkt ist das **Prüfvokabular**, nicht die Klasse. Die Regel steht einmal;
sie ist von einem `Reader` aus und von rohem `struct`-Code aus gleich
erreichbar; und ein Zähler ohne `check_count` daneben fällt beim Lesen auf.
Damit ist auch die Migration nach B später möglich, ohne dass sie jetzt
erzwungen wird — B ist der richtige Endzustand, aber erst nach dem
Testsockel aus S1.

**Verhalten im Fehlerfall:** `ValueError` mit dem Namen des Feldes und den
beiden Zahlen. Nicht abschneiden, nicht auf 0 setzen, nichts still
reparieren — ein Parser, der einen kaputten Zähler heimlich glättet, liefert
Daten, die niemand als falsch erkennt. Die Aufrufer fangen bereits breit
(`inventory._scan_save` überspringt ein unlesbares Save und macht mit dem
nächsten weiter), so dass eine Ausnahme hier zu einem übersprungenen Save
führt und nicht zu einem Absturz.

**Einordnung:** Diese Arbeit gehört **nicht** in den Berater-Strang. Sie ist
ein eigener Auftrag für den `developer`, nach S1 (Testsockel) und unabhängig
von S2–S11. Sie berührt `nrdata/extract.py` nicht und verletzt damit die
Scope-Grenze aus T-001 nicht.

**Konsequenzen:** Leicht wird — jede weitere Zählerstelle prüfen, ohne den
Parser umzubauen. Dauerhaft schwer wird — nichts; C ist ein Zwischenschritt
auf dem Weg zu B und verbaut ihn nicht.

**Umkehrbarkeit:** leicht.

---

### AD-012 — Kein `defusedxml`; stattdessen Grössendeckel vor dem Parsen (2026-09-01, Status: aktiv, vom `director` angenommen samt Neubewertungs-Bedingung)

**Kontext:** `nrdata/icons.py:65` parst `.layout`-XML aus dem Archiv
`01_common_h.sblytbnd.dcx` der Spielinstallation mit
`xml.etree.ElementTree.fromstring`. `ElementTree` gilt gegen „billion
laughs" und quadratische Expansion als verwundbar (externe Entitäten und
DTD-Abruf sind ab Python 3.7 abgeschaltet). Der Pfad läuft **im
ausgelieferten Programm**, nicht nur im Build-Skript: `firstrun.py:139` ruft
`iconbuild.build(...)` beim ersten Start und nach einem Spiel-Patch.

**Bedrohungsmodell, ehrlich zu Ende gedacht:** Die Datei stammt aus dem
Installationsverzeichnis des Spiels auf dem Rechner des Nutzers. Kein Netz,
kein fremder Upload — `GOAL.md` schliesst beides als Nicht-Ziel aus. Wer
diese Datei ersetzen kann, kann auch `nightreign.exe` ersetzen. Der Angreifer
müsste bereits gewonnen haben, um diesen Weg zu brauchen. Der realistische
Fall ist nicht Angriff, sondern **Beschädigung**: eine halb heruntergeladene
oder von einem Mod-Werkzeug verstümmelte Datei. Deren Wirkung ist dieselbe —
das Programm hängt beim ersten Start mit wachsendem Speicherverbrauch, ohne
zu sagen, warum.

**Optionen:**
- **A — `defusedxml`.** Ein Zeilenwechsel im Import, deckt die
  Expansionsklasse vollständig ab. Konsequenz: eine dritte Partei mehr in
  einem ~60-MB-Artefakt; Eintrag in `THIRD_PARTY.md` und Pflege durch
  `scripts/check_licences.py`; und ein Paket, dessen letzte Veröffentlichung
  (0.7.1) mehrere Jahre zurückliegt — es ist stabil, aber es ist auch nicht
  in Bewegung. Für **eine** Aufrufstelle mit einer rein lokalen Quelle.
- **B — Grössendeckel vor dem Parsen**, gegen die entpackte Grösse des
  Archivmitglieds, plus ein Deckel auf der Elementzahl. Konsequenz: keine
  neue Abhängigkeit; fängt Expansion **und** Beschädigung; deckt die
  Entitätenexpansion aber nur über ihre Wirkung ab, nicht über ihre Ursache.
- **C — Nichts tun**, weil das Bedrohungsmodell es nicht hergibt.
  Konsequenz: der Beschädigungsfall bleibt ein stiller Hänger beim ersten
  Start — der schlechteste Ort für einen stillen Hänger.

**Entscheidung: B — Empfehlung an den `director`.** Eine Dependency ist eine
dauerhafte Verpflichtung; hier stünde sie für eine Aufrufstelle, deren Quelle
lokal ist und deren realistischer Fehlerfall ein Deckel ohnehin besser fängt
als eine Entitätenprüfung. Der Deckel kostet drei Zeilen und braucht keine
Freigabe.

**Ausgestaltung:** vor `fromstring` prüfen, ob das entpackte Mitglied einen
Deckel überschreitet (Vorschlag 8 MB — die echten `.layout`-Dateien liegen um
Grössenordnungen darunter; der `security-reviewer` soll den Wert gegen die
tatsächliche Grösse setzen). Bei Überschreitung: Icon-Aufbau mit klarer
Meldung überspringen, nicht abstürzen — `iconpack` kommt ohne Icons aus,
`firstrun` meldet es bereits über seinen `finished`-Signalweg.

**Bedingung für eine Neubewertung — ausdrücklich festgehalten:** Sobald das
Programm XML aus einer Quelle parst, die **nicht** die lokale
Spielinstallation ist (importierte Builds, ein Icon-Pack aus fremder Hand,
irgendetwas aus dem Netz), fällt dieses Bedrohungsmodell in sich zusammen und
A ist die richtige Antwort. Dann ist es keine Dependency für eine
Aufrufstelle mehr, sondern die Absicherung einer Vertrauensgrenze.

**Konsequenzen:** Leicht wird — das Artefakt bleibt, wie es ist; kein
Lizenz- und Pflegeaufwand. Dauerhaft schwer wird — nichts, solange die
Bedingung oben gilt. Erklärtes Restrisiko: eine bösartig konstruierte
`.layout`-Datei unterhalb des Deckels könnte immer noch expandieren. Bei
8 MB Eingabe ist die Expansion durch den Speicher begrenzt, nicht durch die
Datei — deshalb der zweite Deckel auf der Elementzahl.

**Umkehrbarkeit:** leicht. `defusedxml` nachzuziehen ist ein Import.

---

### AD-013 — Ein Vorschlag ist eine Menge von Handles, nicht von Rollen; ein belegtes Exemplar fällt aus dem Kandidatenraum (2026-09-01, Status: aktiv)

**Kontext:** Der Nutzer hat entschieden, dass der Besitz erzwungen wird
(QA-002): ein bereits belegtes Exemplar wird in den übrigen Slots nicht mehr
angeboten, freies Planen läuft über „Custom relic". Damit muss der Berater
dieselbe Regel einhalten — sonst schlägt er Builds vor, die der Spieler nicht
tragen kann.

Meine erste Fassung wollte in S5 gleiche **Rollen** zu einem Kandidaten
zusammenfassen (mehrere Kopien mit identischem Effekt-Multiset als ein
Eintrag, ein Vertreter behält den Handle). Die Messung nimmt dieser Idee
beide Beine weg:

- **Sie spart nichts.** 309 Exemplare ergeben 306 verschiedene Rollen — drei
  Kollisionen, 1,0 %.
- **Sie ist nicht einmal korrekt.** Bei 306 Rollen auf 309 Exemplaren steht
  ein Eintrag in 99 % der Fälle für genau ein physisches Relikt.
  Rollen-Identität ersetzt Exemplar-Identität also nicht; sie *verschleiert*
  sie in den drei Fällen, in denen es darauf ankäme.

**Wie gross der Fehler ohne diese Regel wäre — gemessen, nicht geschätzt.**
Beam-Suche bei K=20/W=40, ohne Exemplar-Prüfung, Anteil der 40 besten
Ergebnisse, die dasselbe Relikt mehrfach belegen:

| Gefäss | unbrauchbare Ergebnisse | bester Vorschlag unbrauchbar? |
|--------|-------------------------|-------------------------------|
| `Wylder's Chalice` `[Rot, Gelb, Weiss]` + Deep | 5 von 40 | nein |
| `Wylder's Urn` `[Rot, Rot, Blau]` + Deep | **40 von 40** | **ja** |

Bei einem Gefäss mit wiederholten Slotfarben ist ohne diese Regel **jeder**
Vorschlag unbrauchbar, der beste eingeschlossen — und zwar auf die
unauffälligste denkbare Art: die Punktzahl ist plausibel, die Relikte sind
alle im Besitz, nur liegt eines davon zweimal.

**Optionen:**
- **A — Rollen-Dedup, Handle nur zur Anzeige.** Konsequenz: siehe oben, in
  drei Fällen falsch und spart 1 %.
- **B — Nachträglich filtern:** suchen ohne Prüfung, unbrauchbare Ergebnisse
  am Ende verwerfen. Konsequenz: auf `Wylder's Urn` bliebe von 40 Ergebnissen
  nichts übrig. Ein Filter, der die ganze Liste leert, ist keiner.
- **C — Handles im Suchzustand.** Jeder Beam-Zustand trägt die Menge der
  bereits belegten Handles; beim Aufklappen eines Slots werden Kandidaten mit
  belegtem Handle übersprungen.

**Entscheidung:** C.

**Ausgestaltung, verbindlich:**
1. Der Kandidat ist das **Exemplar** (`OwnedItem.handle`), nicht die Rolle.
   Kein Dedup.
2. Jeder Beam-Zustand führt ein `frozenset[int]` der belegten Handles. Beim
   Aufklappen werden belegte übersprungen, und es werden die ersten K
   **verfügbaren** genommen — nicht die ersten K der Liste, von denen dann
   welche wegfallen. Sonst schrumpft die Verzweigung an tiefen Slots still.
3. Die vorsortierte Kandidatenliste je Slot ist deshalb mindestens
   `K + (Slotzahl − 1)` lang, damit nach dem Ausschluss immer noch K übrig
   sind.
4. `OwnedItem.handle` kann `None` sein (`inventory.py` setzt es aus
   `read_relic_handles`, und ein Save ohne lesbare Tabelle liefert keine).
   **Ein Relikt ohne Handle ist kein Kandidat** und wird mit genannter
   Begründung in `unknowns` aufgeführt (AD-010). Es stillschweigend
   mitzunehmen hiesse, die Eindeutigkeit für genau die Relikte aufzugeben,
   für die sie nicht prüfbar ist.
5. `AdvisorResult` nennt je Slot den **Handle** und daneben Name und Rolle
   für die Anzeige. Die Oberfläche wählt darüber dasselbe Exemplar aus, das
   der Picker anbietet.

**Konsequenzen:** Leicht wird — der Vorschlag ist per Konstruktion tragbar,
und die Übernahme in die Slots ist eine Handle-Zuweisung ohne Suchen. Dauerhaft
schwer wird — Vorschläge, die den Besitz *überschreiten* („kauf dir noch so
eins"). Die wären ein anderes Merkmal und bräuchten einen anderen
Kandidatenraum; siehe „Bewusst nicht getan".

**Umkehrbarkeit:** mittel. Die Handle-Menge sitzt im Suchzustand von
`search.py` und im Ergebnistyp; sie später herauszunehmen berührt beide, aber
keinen Aufrufer.

---

## Umsetzung — Schnitt in einzeln lauffähige Schritte

Jeder Schritt ist für sich lauffähig und für sich prüfbar. Reihenfolge ist
bindend, wo Abhängigkeiten genannt sind.

| Schritt | Inhalt | Hängt ab von | Fertig, wenn |
|---------|--------|--------------|--------------|
| **S1** | **Testsockel.** `tests/` mit `pytest` (vom `director` freigegeben, **nur** in `requirements-dev.txt`, nie in `requirements.txt` und nie im Artefakt — F8). Ein Fixture, das einen Snapshot lädt und `model.configure()` ruft, plus eine synthetische `Inventory` ohne Save-Datei, mit Handles. | — | `pytest` läuft grün und ohne Display; ein Build des Artefakts enthält `pytest` nicht. |
| **S2** | **Golden-Test der Schadensrechnung**, gegen das *heutige* `_refresh_weapon_damage`. Werte werden festgeschrieben, bevor irgendetwas bewegt wird. | S1 | Ein Satz Waffen × Builds ist als erwartete Zahlen hinterlegt. |
| **S3** | **AD-005: Extraktion** nach `nrplanner/damage.py`, rein, ohne Qt. Konstanten aus F6 mitnehmen. `_refresh_weapon_damage` ruft nur noch und formatiert. **Kein Verhalten ändern.** | S2 | S2 grün, Waffentafel zeigt unverändert dieselben Zahlen. |
| **S4** | **`advisor/types.py`** — die Datenklassen aus AD-004/AD-006/AD-010, alle `frozen`. Kein Verhalten. | S1 | Importierbar, Testsockel legt Instanzen an. |
| **S5** | **`advisor/candidates.py`** — `Inventory` + `SlotProblem` → Kandidatenpool je Slot. **Kein Rollen-Dedup** (AD-013: spart 1 % und ist falsch). Farbfilter über `inventory.relics_for` inklusive **weisser Slot = jede Farbe**, Deep-Trennung, Relikte ohne Handle aussortiert und in `unknowns` gemeldet, Vorsortierung nach isoliertem Beitrag, Liste mindestens `K + Slotzahl − 1` lang. | S4 | Tests: Farbregel, weisser Slot zieht alle vier Farben, Deep-Trennung, handle-lose Relikte draussen und gemeldet, Listenlänge. |
| **S6** | **`advisor/goals.py`** — Registry plus die zwei Zielrichtungen aus AD-004, jede mit gefüllter `unknowns`. | S3, S4 | Tests: beide liefern eine Zahl für einen bekannten Build; `unknowns` nie leer. |
| **S7** | **`advisor/search.py`** — Beam-Suche nach AD-003, Handle-Menge im Suchzustand nach AD-013, rein, abbrechbar, deterministisch. Scorer als Parameter (offen für AD-002/C). | S5, S6 | Tests 3–6 aus AD-009 grün, Punkt 4 **gegen `Wylder's Urn`**; Laufzeit gegen `Wylder's Chalice` + Deep gemessen und protokolliert. |
| **S8** | **`advisor/explain.py`** — aus `Build.sources` und der Differenz zum leeren Build englische Begründungszeilen; dazu `not_counted`, `curses`, `data_note` (AD-010). | S7 | Test: jede Zeile nennt einen Effekt, der im Vorschlag tatsächlich vorkommt. |
| **S9** | **`advisor/worker.py`** — `AdvisorController` nach AD-006: `QThread`, Signale `ready`/`failed`/`progress`, Entprellung, Abbruch, LRU-Cache nach AD-007, Rückabbildung der kanonischen Slots nach AD-008. | S7, S8 | Manuell: Anfrage stellen, Fenster bleibt bedienbar, zweite Anfrage bricht die erste ab. |
| **S10** | **Anbindung an die Oberfläche** — neues Tab-Modul nach dem Muster von `effectstab.py`. **`app.py` wächst nur um die Instanziierung des Tabs und des Controllers.** Layout nach der Spezifikation des `ui-ux-designer` (T-004). | S9, T-004 | A3, A5, A6, A7, A8 am gebauten Artefakt prüfbar. |
| **S11** | **Budget setzen.** `performance-tuner` misst K/W gegen den echten Bestand und bestätigt oder korrigiert die Voreinstellung K=20/W=40; A6 bekommt seine Zahl. | S10 | Zielwert in `GOAL.md` A6 eingetragen. |

**Parallelisierbar:** S4 neben S2/S3. S6 und S5 nebeneinander, sobald S4 steht.
**Kritischer Pfad:** S1 → S2 → S3 → S6 → S7 → S8 → S9 → S10.

**Ausserhalb dieses Strangs, eigener Auftrag:**

| Schritt | Inhalt | Hängt ab von |
|---------|--------|--------------|
| **X1** | **AD-011** — Prüfvokabular in `nrdata/binary.py`, aufgerufen an den fünf Zählerstellen und den vier UTF-16-Schleifen. Kein Parser wird umgeschrieben. | S1 |
| **X2** | **AD-012** — Grössen- und Elementdeckel vor `ElementTree.fromstring` in `nrdata/icons.py`. Wert vom `security-reviewer`. | — |

X1 und X2 laufen unabhängig vom Berater und blockieren ihn nicht.

### Was der `developer` ausdrücklich nicht tun soll

1. **`nrdata/extract.py` nicht anfassen.** Scope-Grenze aus T-001.
2. **`Planner` nicht umbauen**, ausser der einen Extraktion in S3. F3 ist
   erkannt und zurückgestellt; ein Aufräumen nebenher macht S3 unprüfbar.
3. **Keine zweite Bewertungsmathematik.** Wenn eine Zahl fehlt, gehört sie in
   `model.py` oder `damage.py`, nicht in `advisor/`.
4. **Kein PySide6-Import unter `advisor/` ausser in `worker.py`.**
5. **Kein `QApplication.processEvents()`** im Beraterpfad, auch nicht als
   schnelle Lösung gegen ein hängendes Fenster (AD-006, Punkt 1).
6. **Keine Dependency installieren**, auch keine Entwicklungsabhängigkeit.
   Freigabe erteilt der `director`.
7. **Keine Vorschläge persistieren** und keinen Plattencache anlegen (AD-007).
8. **Verhalten in S3 nicht verbessern.** Fällt beim Verschieben ein Fehler in
   der Schadensrechnung auf: melden, nicht beheben. Sonst ist der Golden-Test
   wertlos.
9. **Kein „Optimal" in nutzersichtbarem Text** (AD-003, AD-010).
10. **Layout nicht selbst festlegen** — T-004.

---

## Risiken und Prüfpunkte

| Risiko | Woran man es merkt | Rückweg |
|--------|--------------------|---------|
| Beam-Suche findet auf echten Beständen deutlich schlechtere Builds, als der Spieler von Hand baut. | Vergleich gegen die von Daniel bereits gebauten Builds: der Berater sollte sie erreichen oder schlagen. Tut er es nicht, ist die Kandidatenkappung (K) oder die Beam-Breite (W) zu eng. | K und W sind Parameter, nicht Struktur. Erhöhen und neu messen; die Grundzahlen zeigen Luft bis mindestens K=30/W=60 (0,98 s im ungünstigsten realen Fall). |
| **Die isolierte Vorsortierung wirft an einem weissen Slot gute Kandidaten weg**, weil K=20 dort nur ~10 % von 205 behält und ein Relikt, das erst neben einem anderen stark wird, isoliert schwach aussieht. | Ein von Hand gebauter Build auf einem Gefäss **mit** weissem Slot wird nicht erreicht, während er auf Gefässen ohne weissen Slot erreicht wird. Das ist der Trennschnitt, der diese Ursache von einem allgemein zu engen K unterscheidet. | Eigenes, höheres K für weisse Slots — die Kosten sind linear in K. OF-10 an den `performance-tuner`. |
| **Ein Vorschlag ist nicht tragbar**, weil dasselbe Exemplar in zwei Slots liegt. | Gemessen: ohne AD-013 auf `Wylder's Urn` 40 von 40 Ergebnissen, der beste eingeschlossen. Mit AD-013 muss es null sein. | Kein Rückweg nötig — Testpunkt 4 in AD-009 fängt es, und er läuft gegen ein Gefäss mit wiederholten Slotfarben, wo die Regel scharf ist. |
| GIL-Kontention lässt das Fenster ruckeln, obwohl es nicht blockiert. | Sichtbares Stocken beim Ziehen des Level-Reglers während eines Laufs. | Entprellung erhöhen; wenn das nicht reicht, AD-006 Option B (Prozess) — mit den dort genannten PyInstaller-Kosten. |
| `model.compute()` wird durch eine spätere Korrektur langsamer, und das Budget kippt. | S11 ist eine Messung, kein Gefühl. Sie muss wiederholbar sein. | Der Scorer ist in `search.py` ein Parameter — AD-002 Option C bleibt nachrüstbar. |
| Die Extraktion in S3 verändert stillschweigend eine Zahl. | S2 schlägt fehl. Genau dafür liegt S2 vor S3. | Zurückrollen; S3 ist ein einzelner, abgegrenzter Commit. |
| Race zwischen Hintergrundlauf und `model.configure()` (F4). | Sporadisch absurde Werte nach einem Spiel-Patch oder Neu-Scan — schwer zu reproduzieren, also vorbeugen statt entdecken. | AD-006 Punkt 5 ist Pflicht, nicht Empfehlung. Dauerhaft: `model` von Modulglobals befreien (eigener Auftrag). |
| Der Berater rankt auf einem veralteten Snapshot und sagt es nicht (F7). | `meta.data_version` weicht von der Spielversion ab. | `data_note` in AD-010 macht es sichtbar. Die Ursache in `datasource` zu beheben ist ein eigener Auftrag. |
| Die Unwissensliste ist so lang, dass sie niemand liest — und A7 damit faktisch nicht erfüllt ist. | Beurteilung durch `ui-ux-designer` in T-004. | Nicht kürzen, sondern schichten: die für diesen Lauf zutreffenden Punkte sichtbar, der Rest aufklappbar. Die Entscheidung darüber gehört T-004, nicht hierher. |

---

## Bewusst nicht getan

- **Kein Solver (`ortools`, `pulp`).** Die Zielfunktion ist nicht linear, und
  eine Linearisierung widerspräche den gemessenen Regeln in `model.py`.
  *Wieder interessant, wenn:* der Suchraum durch eine künftige Anforderung
  wächst (etwa: über alle 74 Gefässe gleichzeitig optimieren) **und** sich
  zeigt, dass die Nichtlinearität auf wenige, modellierbare Fälle beschränkt
  ist.
- **Kein zweiter, schneller Scorer.** AD-002. *Wieder interessant, wenn:* die
  Messung in S11 auf einem echten Bestand über dem Budget landet und K/W nicht
  weiter zu senken sind, ohne die Qualität der Vorschläge zu verlieren.
- **Kein `multiprocessing`.** AD-006. *Wieder interessant, wenn:* das Fenster
  trotz Entprellung sichtbar ruckelt, oder eine Anforderung „alle Gefässe auf
  einmal" hinzukommt.
- **Kein Plattencache.** AD-007. *Wieder interessant, wenn:* die Rechnung
  Sekunden statt Zehntelsekunden dauert **und** eine Invalidierung über
  `inventory_fingerprint` + `snapshot_fingerprint` als sicher nachgewiesen ist.
- **Kein Umbau von `Planner`.** F3 ist erkannt und aufgeschrieben. *Fällig,
  wenn:* der `director` einen eigenen Auftrag dafür schneidet — sinnvoll erst
  nach dem Testsockel aus S1, vorher fehlt das Netz.
- **`model.py` behält seine Modulglobals.** F4. Nur entschärft, nicht
  behoben. *Fällig, wenn:* ein zweiter nebenläufiger Verbraucher dazukommt
  oder die Tests reihenfolgeabhängig werden.
- **Keine Zielrichtung, die Spielverlauf oder Bosskenntnis braucht** (etwa
  „bestes Build gegen Gladius"). `nrdata/bossdata.py` und der Boss-Tab hätten
  die Daten. *Wieder interessant, wenn:* A3 erfüllt ist und der App Designer
  es will — es wäre eine dritte `Goal`-Funktion plus ein erweiterter
  `GoalContext`, kein Strukturbruch.
- **Keine Vorschläge über Waffen oder Zauber**, nur über Relikte. Der Auftrag
  nennt Relikte, und Zauberschaden existiert als Feld nicht (README).
- **Kein Rollen-Dedup im Kandidatenpool.** Gemessen: 309 Exemplare ergeben
  306 verschiedene Rollen — 1,0 % Ersparnis, und die Zusammenfassung wäre
  gegen AD-013 sogar falsch. *Wieder interessant, wenn:* nie. Drei Effekte
  aus einem Pool von 2 079 kollidieren nicht in nennenswerter Zahl, und das
  ändert sich durch mehr Relikte im Besitz nicht, sondern wird schlimmer.
  **Ausdrücklich hier festgehalten, damit es niemand ein zweites Mal
  versucht** — die Idee ist naheliegend und die Messung widerlegt sie.
- **Der Berater schlägt das Gefäss nicht mit vor.** Entscheidung des Nutzers
  (OF-4). Es scheitert nicht an der Rechenzeit — 47 kanonische Probleme
  wären ~23 s — sondern daran, dass der Wartezustand unsichtbar bleiben
  soll. *Wieder interessant, wenn:* der Nutzer die Frage neu stellt; AD-008
  hält den Weg offen, es wäre eine Schleife über die kanonischen Probleme
  und kein neuer Mechanismus.
- **Keine Vorschläge, die den Besitz überschreiten** („dieses Relikt fehlt
  dir noch"). AD-013 macht den Kandidatenraum zur Besitzmenge. *Wieder
  interessant, wenn:* der App Designer einen Wunschzettel-Modus will; das
  wäre ein zweiter Kandidatenraum aus `data["relics"]` statt aus
  `Inventory`, und die Suche bliebe unverändert.

---

## Offene Fragen

**Erledigt** (Stand 2026-09-01, nach dem Nachtrag des `director`):

| # | Frage | Ergebnis |
|---|-------|----------|
| OF-1 | Tkinter oder PySide6 | Fehler in der Auftragsdatei; es ist PySide6. AD-006 steht auf Qt-Grundlage. |
| OF-2 | Testwerkzeug | **`pytest` freigegeben**, ausschliesslich als Entwicklungs-Abhängigkeit in `requirements-dev.txt`. Nachtrag in AD-009. |
| OF-4 | Gefäss mitvorschlagen? | **Nein**, Entscheidung des Nutzers. Als Nicht-Ziel aufgenommen. |
| OF-5 | `max_damage` ohne Referenzwaffe | **Gekennzeichneter Rückfall**, nicht verweigern. Nachtrag in AD-004. |
| OF-6 | `GOAL.md`-Freigabe | Erteilt; A1–A9 bindend. |
| OF-7 | echte Bestandszahlen | Vom `qa-engineer` gemessen: 309 Relikte, weisse Slots als Slot-Eigenschaft, Dedup wertlos. Siehe Grundzahlen, AD-003, AD-013. |
| OF-8 | `defusedxml` | Empfehlung angenommen: kein `defusedxml`, Grössendeckel, mit Neubewertungs-Bedingung. |
| OF-9 | Prüfung durch `security-reviewer` | Der `director` gibt die Deckelwerte direkt in den Auftrag; nicht abzuwarten. |

**Noch offen:**

**OF-3 — beim Nutzer, über `director`:** Gewichtung der acht Schadensarten
für `min_damage_taken`. Der Entwurf ist so gebaut, dass die Antwort ihn nicht
mehr bewegt: die Gewichte sind Daten im `GoalContext` (`Weighting`), die
Voreinstellung ist benannt und wird im Ergebnis ausgewiesen, und ein
Bedienelement liefert später eine andere Instanz. Der `developer` kann ohne
diese Antwort beginnen. **Was sie noch berührt:** `weighting.id` muss in den
Cache-Schlüssel (AD-007) — das gilt in beiden Fällen und ist eingearbeitet.

**OF-10 — an `performance-tuner`, für S11:** K=20 behält an einem farbigen
Slot ~40 % des Pools, an einem weissen nur ~10 % (205 Kandidaten). Die
Vorsortierung bewertet **isoliert**, also ohne die Wechselwirkungen, wegen
derer es die Beam-Suche gibt. Bitte messen, ob ein weisser Slot ein eigenes,
höheres K braucht. Die Kosten sind linear in K und ein Lauf dauert 0,46 s,
also ist Luft da. Das ist die schärfste bekannte Schwäche des Verfahrens und
die einzige, die ich nicht selbst ausmessen konnte.

**OF-11 — an `qa-engineer`:** `OwnedItem.handle` kann `None` sein, wenn
`savefile.read_relic_handles` für ein Exemplar nichts liefert. AD-013 nimmt
solche Relikte aus dem Kandidatenraum und meldet sie. Wie viele der 309 sind
das tatsächlich? Bei null ist die Regel eine Formalie, bei einer
nennenswerten Zahl ist sie ein sichtbarer Verlust an Vorschlagsqualität und
gehört in die Oberfläche statt nur in `unknowns`.
