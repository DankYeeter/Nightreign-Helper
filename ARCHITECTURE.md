# Architektur

Stand: 2026-09-01 · Angelegt im Zuge T-001 (Zyklus 1, Audit)
Sprache: dieses Dokument Deutsch (Team-Dokument, wie `GOAL.md` und
`docs/state.md`). Bezeichner im Code und **alle nutzersichtbaren Texte
Englisch** (Projektregel, `GOAL.md` A8).

Bezugsstand: 3da8428 (v1.7.1), 16 737 Zeilen Python, 0 Tests.
`GOAL.md` ist vom Nutzer freigegeben; A1–A9 sind für diesen Entwurf bindend.

---

## Wie dieses Dokument zu lesen ist

*Konsolidiert am 12.09.2026 (T-182). **Keine neue Entscheidung, keine neue
AD-Nummer, kein geaenderter Wortlaut.** Umgestellt wurde die Reihenfolge:
frueher chronologisch nach Nachtrag, jetzt nach Themenbereich.*

Bis zum 12.09.2026 wuchs diese Datei chronologisch: elf Nachtraege, in denen
eine Entscheidung an drei Stellen fortgeschrieben werden konnte. Wer den
heutigen Vertrag des `AdvisorController` brauchte, las Nachtrag VIII, IX und X
und entschied selbst, welcher gewinnt. Drei Dateien teilen sich die Arbeit
jetzt so:

| Datei | Frage, die sie beantwortet |
|---|---|
| `ARCHITECTURE_REGISTER.md` | **Welche Fassung gilt heute?** Eine Zeile je AD- und je OF-Nummer, mit Fundstelle und Stand. **Hier faengt man an.** |
| `ARCHITECTURE.md` (diese Datei) | **Was gilt** — nach Themenbereich A bis F geordnet, jede Entscheidung mit der Begruendung, die zu ihr gehoert. |
| `docs/archiv/architecture-verlauf.md` | **Wie es dazu kam** — der vollstaendige chronologische Verlauf, unveraendert, mit allen verworfenen Alternativen. |

**Nichts ist gestrichen.** Jede der 5972 Zeilen der bisherigen Fassung steht
in einer der beiden Dateien; nachgerechnet wurde das als Partition
(jede Quellzeile genau einmal, keine doppelt, keine fehlend).

**Wo eine Entscheidung nachgezogen wurde, steht der Nachtrag direkt
darunter** — nicht mehrere hundert Zeilen weiter unten. Der urspruengliche
Wortlaut bleibt dabei stehen, damit nachlesbar ist, worauf er gebaut war; die
Nachtragsklammer sagt, was heute gilt. Das ist die Bauform, die Nachtrag VIII
bis X bereits benutzt haben, und sie wird hier nur zusammengefuehrt.

**Zwei Nummern sind nie vergeben worden** und werden nicht neu belegt:
**AD-027** und **OF-14**. Die naechste freie AD-Nummer ist **AD-032**.

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

## Gemessene Grundzahlen

Alle Entwurfsentscheidungen unten stützen sich auf diese Messungen, nicht auf
Annahmen. Rechner: dieser (Windows 10, CPython 3.12).

> **Warnung, nachgetragen 2026-09-08 (AD-028).** Die **Laufzeiten** dieses
> Abschnitts sind vom 01.09.2026, ohne protokollierte Umgebung, und sind
> ueberholt: gemessen am 08.09.2026 kostet eine Bewertung **1,095 ms** statt
> „0,18–0,25 ms" und ein Gesamtlauf **5,02 s** statt „0,46 s"
> (`docs/perf/baselines.md`, S11-A/S11-D). Ob das eine Regression ist oder
> die Umgebung, ist offen (D-1). **Die Mengenangaben** — 849 Vorlagen, 309
> besessene Kopien, 206 Kandidaten am weissen Slot, 26/47 Slot-Muster — sind
> davon unberuehrt und tragen weiter.
> **Fuer jede Zeitzahl gilt ab jetzt `docs/perf/baselines.md` als Quelle**,
> und keine Entscheidung stuetzt sich auf eine Zeitzahl aus diesem Abschnitt,
> ohne sie dort nachzuschlagen. Der Anlass ist QA-208: AD-018 hat aus
> „0,25 ms je Bewertung" mal 205 Kandidaten **~51 ms gerechnet**, die Zahl in
> drei Dateien geschrieben, und keine der drei sagte, dass sie gerechnet und
> nicht gemessen war.

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

Die Entscheidungen stehen in sechs Themenbereichen. Innerhalb eines Bereichs
folgt auf eine Entscheidung unmittelbar das, was sie nachzieht oder korrigiert.
Die Reihenfolge der Vergabe (AD-001 bis AD-032) steht im Verlauf; welche
Nummer wo liegt, sagt `ARCHITECTURE_REGISTER.md` in einer Zeile.

**Eine Entscheidung ist noch keine:** AD-032 liegt als vorgelegte Wahl mit
vier gemessenen Optionen in Bereich C. Bis der App Designer waehlt, gilt dort
der gebaute Zustand.

| Bereich | Inhalt | AD |
|---|---|---|
| **A** | Schnitt, Rechenautoritaet, Fassade, Benennung | AD-001, AD-002, AD-021, AD-005, AD-019, AD-020, AD-022, AD-023, AD-024 |
| **B** | Suche, Kandidaten, Haltezustand, Grenzbeitrag | AD-003, AD-008, AD-013, AD-014, AD-016, AD-017, AD-018 |
| **C** | Zielrichtungen, Vorbehalte, Fluechte | AD-004, AD-010, AD-025, AD-015, AD-026, **AD-032 (offen)** |
| **D** | Nebenlaeufigkeit, Cache, Hauptthread | AD-006, AD-007, AD-028, AD-029 |
| **E** | Daten lesen, Erststart, Pfade | AD-011, AD-012, AD-030, AD-031 |
| **F** | Test und Nachweis | AD-009 |

---

## Themenbereich A — Schnitt, Rechenautoritaet, Fassade, Benennung

*Wer darf rechnen, wo liegt die eine Formel, und wie heisst, was aus ihr
herauskommt. AD-002 ist die tragende Entscheidung des Bereichs; AD-021 sagt,
was der Waechter darueber wirklich zusichert.*

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

### AD-021 — Der Wächter sichert nicht „ein Aufrufer", sondern „nur die Fassade rechnet"; dasselbe Werkzeug, zwei Zusicherungen (2026-09-02, Status: aktiv; erweitert AD-002 und `test_one_build.py`)

**Kontext:** QA-058 stellt die Frage, wie „eine Rechenstelle" für **beide**
Schichten gelten kann. Der bestehende Wächter
(`test_one_build.py::test_the_user_interface_holds_exactly_one_call_to_compute`)
zählt über den Syntaxbaum, kennt alle sechs Aufrufschreibweisen, sucht rekursiv
unter `nrplanner/` und weiss ausdrücklich, was er nicht sehen kann
(Laufzeitauflösung, QA-023, festgehalten). Das Werkzeug ist gut; nur seine
**Zusicherungsform** passt für die obere Schicht nicht: dort gibt es nicht
einen richtigen Aufrufer, sondern eine richtige Fassade (AD-019).

**Optionen:**
- **A — Den `compute`-Wächter kopieren und auf `rate`/`rank` umbenennen.**
  Konsequenz: zwei fast gleiche Testdateien, die getrennt driften; und die
  falsche Zusicherung aus AD-019 Option A.
- **B — `compute_call_sites` zu `call_sites(source, modules, functions)`
  verallgemeinern und zweimal aufrufen: einmal mit
  (`model`, `compute`) → Erwartung `{app.py: 1}`, einmal mit
  (`weapons`, `rate`/`rank`) → Erwartung `{damage.py: n}` und **überall sonst
  Null**.** Konsequenz: eine Implementierung, zwei Zusicherungen; der Test
  „sieht jeden Weg um sich herum" prüft beide mit denselben sieben
  Schreibweisen.
- **C — Zusätzlich den Ausdruck `base.get(d,0) + scaled.get(d,0)` im
  Syntaxbaum verbieten.** Konsequenz: brüchig (jede Umformulierung entkommt),
  und nach W1 gegenstandslos, weil eine Stelle ohne Zugriff auf `rate` gar
  keine `WeaponRating` mehr selbst erzeugt.

**Entscheidung:** B. C wird **nicht** gebaut; die Formel deckt der
Golden-Test ab, und die Grenze wird im Wächter-Docstring genannt statt
behauptet.

**Form der zweiten Zusicherung (illustrierend):**

```python
ARITHMETIC_ENTRY = ("rate", "rank")   # weapons.py, untere Schicht
FACADE = "nrplanner/damage.py"        # die einzige Stelle, die sie anfassen darf

# Erwartung: {FACADE: n}. Jede andere Datei unter nrplanner/ muss 0 haben.
# Konstanten und Typen aus weapons.py (DAMAGE_TYPES, DAMAGE_LABELS,
# RARITY_TIERS, WeaponRating) bleiben ausdruecklich erlaubt -- der Waechter
# zielt auf zwei Funktionsnamen, nicht auf den Import des Moduls.
```

**Reichweite, ausdrücklich, weil ein Wächter mit unausgesprochener Reichweite
als Wächter ohne Grenzen gelesen wird:**
- Suchraum bleibt `nrplanner/` (QA-023). `run.py` und `scripts/` liegen
  ausserhalb; `scripts/capture_weapon_damage.py` ruft die Rechnung
  absichtlich und ist deshalb kein Verstoss — aber auch nicht gesichert.
- **Das Berater-Paket muss unter `nrplanner/advisor/` liegen** (AD-001, von
  `test_the_search_space_reaches_inside_a_package` bereits geprüft), sonst
  sieht der Wächter es nicht. Diese Bedingung gilt jetzt für **beide**
  Zusicherungen.
- Der Berater ruft die Fassade, nicht `weapons.rate`. Damit gilt für ihn
  dieselbe Regel wie für jeden Tab.

**Konsequenzen:** Leicht wird — eine fünfte Anzeigestelle, die sich ihre
Waffenzahl selbst zusammenrechnet, fällt beim Testlauf auf statt beim Spieler.
Dauerhaft schwer wird — der `developer` kann `weapons.rate` nicht mehr „mal
eben" für eine Sonderansicht rufen; er muss eine `Basis` beantragen. Das ist
der Preis und der Zweck.

**Umkehrbarkeit:** leicht. Ein Test.

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

### Nachtrag III 2026-09-02 — Die zweite Rechenschicht (AD-019 bis AD-021, QA-058)

Anlass: QA-058. Der `compute`-Wächter ist grün und bleibt grün — er sichert
die Schicht, für die er geschrieben wurde. Die Waffenzahl entsteht eine Etage
höher, und dort wählen vier Anzeigestellen ihre Eingaben unabhängig. Das ist
dieselbe Klasse von Befund wie QA-001, nur eine Schicht weiter oben.

### AD-019 — Eine gemeinsame Fassade über beiden Rechenschichten, kein zweiter Wächter über `weapons.rate` (2026-09-02, Status: aktiv; erweitert AD-005, Vorbedingung für AD-018)

**Kontext:** QA-058. Die Waffen-Arithmetik hat zwei Schichten. Bis
`weapons.rate` (Grundschaden x Verstärkung + Attributskalierung) sind alle
Pfade bitgleich — das ist gemessen, nicht vermutet. `damage.attack_rating`
legt danach eine **Multiplikatorschicht** (`build.rates` x `class_rates`, flach
je Schadensart) darauf, die drei der vier Anzeigestellen nie sehen. Der
`compute`-Wächter aus AD-002/QA-001 ist grün und bleibt grün: er deckt die
Schicht darunter ab (`model.compute`), nicht diese. Die Randbedingung, unter
der „eine Rechenstelle" geprüft wurde, war der **Build** — nicht die
**Waffenzahl**.

Vier Anzeigestellen wählen ihre drei Eingaben — Attributsatz, Tier,
Multiplikatorschicht — heute unabhängig voneinander, und keine von ihnen sagt,
welche sie gewählt hat:

| Stelle | Attributsatz | Tier | Multiplikatoren |
|--------|--------------|------|-----------------|
| `damage.attack_rating`, `after` | `build.attributes` | `slot.tier` | ja |
| `damage.attack_rating`, `before` | `build.base_attributes` | `slot.tier` | nein |
| `app.py:2865` (Waffenkachel) | `build.attributes` | `slot.tier` | **nein** |
| `arsenaltab` (über `rank`) | `build.attributes` | **Ziel-Tier aus der Spinbox** | nein |
| `weaponstab` (toter Code) | `build.attributes` | Spinbox 0..25 | nein |

Daraus die drei unabhängig gemessenen Abweichungsachsen: **A** Multiplikatoren
(QA-018, Tab 203,4 gegen Tafel 244,1), **B** Tier (QA-055, Slot auf Tier 3 und
Spinbox auf 1 ohne ein einziges Relikt: Kachel und Tafel 321,4, Tab 203,4),
**C** Attributsatz (QA-056, mit „Strength +1": Kachel 323, linke Tafelzahl
321,4, Tab 204,2). Dazu ist die Formel je Schadensart
`base.get(d,0) + scaled.get(d,0)` **viermal ausgeschrieben** (`damage.py:140`,
`weaponstab.py:107`, `arsenaltab.py:368`, `app.py:2900`), weil `WeaponRating`
zwar `total` trägt, aber keinen Zugriff je Typ.

**Die Kräfte:** Konsistenz gegen Richtigkeit. Nicht jede der drei Achsen ist
ein Fehler — der Arsenal-Tab rankt bewusst auf einem **Ziel-Tier**, nicht auf
dem ausgerüsteten, und die linke Tafelzahl steht bewusst auf den
**Grundattributen**, sonst gäbe es kein Vorher/Nachher. Eine Struktur, die das
wegvereinheitlicht, macht das Programm falsch statt konsistent. Die Grenze
zieht AD-020.

**Optionen:**
- **A — Im Bestand bleiben, zweiter Wächter über `weapons.rate`/`weapons.rank`
  nach dem Muster von `test_one_build.py`.** Kein Umbau, das Werkzeug steht
  bereits (AST-Zählung über alle sechs Aufrufschreibweisen, rekursiv über
  `nrplanner/`). Konsequenz: **die Zusicherung wäre falsch.** Der
  `compute`-Wächter trägt, weil es genau *einen* richtigen Build gibt. Hier
  gibt es mehr als eine richtige **Frage**: „was hängt in Slot 1" und „wie gut
  wäre diese Waffe als Legendary" sind verschiedene Fragen an dieselbe Formel.
  Ein Wächter auf einen Aufrufer erzwänge entweder eine falsche
  Vereinheitlichung (Achse B) oder bräuchte eine Ausnahmeliste — und ein
  Wächter mit Ausnahmeliste sichert die Ausnahmen nicht zu.
- **B — Zweiter Wächter plus ausdrückliche Ausnahmeliste je Aufrufer.**
  Konsequenz: die Liste beschreibt den Ist-Zustand, statt ihn zu binden. Sie
  wächst mit jedem neuen Tab und sagt weiterhin nicht, *warum* eine Stelle
  abweicht. QA-058 wäre dokumentiert, nicht geschlossen.
- **C — Gemeinsame Fassade in `nrplanner/damage.py`.** Eine Stelle legt für
  **jede benannte Frage** alle drei Eingaben fest; die Anzeigestellen nennen
  die Frage und bekommen eine Zahl. Der Wächter sichert danach nicht „ein
  Aufrufer", sondern „nur die Fassade fasst `weapons.rate`/`rank` an"
  (AD-021). Konsequenz: ein Eingriff in vier Stellen, der Regressionsschutz
  braucht.
- **D — Fassade in einem neuen Modul `nrplanner/rating.py`.** Sauberer
  Namensschnitt. Konsequenz: ein drittes Modul für eine Rechnung, die schon
  zwei hat, und `damage.py` bliebe als halbe Fassade daneben stehen. Verworfen
  zugunsten von C: `damage.py` ist bereits die obere Schicht (AD-005) und
  liegt bereits unter `nrplanner/`, was QA-023 verlangt.

**Entscheidung:** C. Der `developer` hat recht, und der Grund ist nicht
Sauberkeit, sondern Zusicherbarkeit: Option A behauptet etwas, das nicht
stimmt, und Option B sichert nichts zu. Die Fassade ist die einzige Option, in
der die Wahl der drei Eingaben eine **benannte, an einer Stelle getroffene
Entscheidung** ist statt einer Nebenwirkung davon, welches Modul man importiert
hat.

**Schnittstelle (illustrierend, kein Anwendungscode):**

```python
# nrplanner/weapons.py -- die vierfach ausgeschriebene Formel, einmal.
@dataclass
class WeaponRating:
    ...
    def per_type(self) -> dict[str, float]:
        """base + scaled je Schadensart, nur die von Null verschiedenen."""

# nrplanner/damage.py -- die Fassade.
class Basis(enum.Enum):
    """Welche Frage gestellt wird. Es gibt genau diese drei."""
    EQUIPPED  = "equipped"    # diese Waffe, in diesem Slot, wie sie steht
    CANDIDATE = "candidate"   # eine nicht ausgeruestete Waffe, auf Ziel-Tier
    BARE      = "bare"        # Grundattribute, ohne alles Ausgeruestete

# Die EINZIGE Stelle, die sagt, ob die Multiplikatorschicht zu einer Frage
# gehoert. Die Spielmessung zu QA-018 aendert hier einen Wert und sonst
# nichts im Programm.
MULTIPLIERS_FOR = {Basis.EQUIPPED: True, Basis.CANDIDATE: OFFEN,
                   Basis.BARE: False}
ATTRIBUTES_FOR  = {Basis.EQUIPPED: "attributes", Basis.CANDIDATE: "attributes",
                   Basis.BARE: "base_attributes"}

@dataclass(frozen=True)
class Rating:
    weapon: dict
    basis: Basis            # welche Frage beantwortet wurde -- steht mit dabei
    tier_applied: int       # welches Tier tatsaechlich erreicht wurde
    per_type: dict[str, float]
    total: float
    rates: dict[str, float]     # nur die != 1.0, fuer die Aufklapp-Tafel
    weapon_class: str | None
    starting_armament: bool

def equipped(slot, slot_index, build, hero, data) -> tuple[Rating, Rating]:
    """Die ausgeruestete Waffe: (BARE-Vergleichszahl, EQUIPPED-Zahl).
    Tier kommt aus dem Slot, die Startwaffen-Paarung aus (slot_index, hero)."""

def candidate(weapon, target_tier, build, data) -> Rating:
    """Eine Waffe, die nirgends steckt, auf einem gewaehlten Ziel-Tier.
    Kein slot_index, also nie eine Startwaffen-Strafe (AD-020, Punkt 3)."""

def rank_candidates(build, target_tier, data) -> list[Rating]:
    """Jede Waffe im Datensatz als Kandidat, `weapons.rank` gefolgt vom
    Aufbau der Antwort je Zeile. Kein `require_usable`-Parameter mehr:
    Nightreign kennt keine Attributsanforderungen fuer Waffen, nur
    Charakterlevel (QA-061, T-034) -- die Anforderungspruefung war toter
    Code und ist samt `WeaponRating.unmet` entfernt."""
```

`AttackRating` aus AD-005 bleibt als Rückgabetyp der Aufklapp-Tafel bestehen
oder geht in `Rating` auf — das entscheidet der `developer` beim Umbau; es ist
eine Umbenennung, keine Struktur.

**Abhängigkeitsrichtung, unverändert und ohne Zyklus:**
`app.py`/`arsenaltab.py` → `damage.py` → `weapons.py` → `model.py`.
`arsenaltab.py` importiert `weapons` künftig nur noch für Konstanten und
Typen (`DAMAGE_TYPES`, `DAMAGE_LABELS`, `RARITY_TIERS`, `WeaponRating`), nicht
mehr für Arithmetik. Der Wächter aus AD-021 zielt auf die zwei
Arithmetik-Einstiege, nicht auf das Modul.

**Migrationspfad — vier Anzeigestellen, nicht in einem Rutsch:**

| Schritt | Inhalt | Bitgleich? | Hängt ab von |
|---------|--------|-----------|--------------|
| **W0** | `nrplanner/weaponstab.py` löschen (QA-057). Kein Importeur im ganzen Baum; `app.py:1342` bindet `ArsenalTab` an `self.weapons_tab`, das Attribut überlebt. | ja, trivial | — |
| **W1** | `WeaponRating.per_type()` in `weapons.py`; die drei verbleibenden Ausschreibungen darauf umstellen. | **ja, bitgleich** | W0 |
| **W1b** | Umbenennung nach der Schichtregel aus AD-022 (`scaled_*` / `final_*`, `Basis` → `Question`). Reine Umbenennung. | **ja, bitgleich** | W1 |
| **W2** | Fassade in `damage.py` anlegen, `MULTIPLIERS_FOR`/`ATTRIBUTES_FOR` **mit den heutigen Werten** befüllen. `attack_rating` ruft die Fassade; sonst ändert sich nichts. | **ja, bitgleich** | W1 |
| **W3** | `app.py` Kachel **und** Tafel auf `damage.equipped()` umstellen. Hier fällt Achse C zwischen Kachel und Tafel — sie sind dieselbe Frage. | **nein, gewollt** | W2 |
| **W4** | `arsenaltab` auf `damage.rank_candidates()` umstellen, Ziel-Tier ausdrücklich als `target_tier` durchgereicht. | **nein, gewollt** | W2 |
| **W5** | Wächter aus AD-021 scharfschalten; `WeaponRating.total` fällt, sobald es keinen Leser mehr hat (Z1); `weapons.rank` bekommt einen stabilen Zweitschlüssel. | — | W3, W4 |
| **W6** | Nach der Spielmessung: **ein Wert** in `MULTIPLIERS_FOR[Basis.CANDIDATE]`. | nein, das ist die Antwort auf QA-018 | Nutzer |

W3 und W4 sind voneinander unabhängig und können in beliebiger Reihenfolge
oder in zwei Aufträgen erledigt werden — beide hängen nur an W2.

**Trägt das Verfahren aus Zyklus 2 (10 000 Differentialfälle, 0 Abweichungen)
hier?** **Für W1 und W2 ja, für W3 bis W6 nicht — und das ist die wichtigste
Aussage dieses Entwurfs.** Zyklus 2 belegte „nichts hat sich geändert", und der
Golden-Stand war der Beleg. Hier sollen sich drei der vier Stellen **ändern**;
ein eingefrorener Golden-Stand würde den Befund einfrieren statt ihn zu
sichern. Also:
- **W1, W2:** Differentialtest gegen den Vor-Zustand, Abbruch bei jeder
  Abweichung. Genau das Verfahren aus Zyklus 2, unverändert.
- **W3 bis W6:** `tests/golden/weapon_damage.json` muss neu aufgenommen
  werden. Sein eigener Vertrag erlaubt das heute nur nach einem
  **Spiel-Patch**. Der Vertrag ist zu erweitern um: „oder wenn eine
  dokumentierte Entscheidung eine Eingabe geändert hat; der Commit nennt die
  AD- oder QA-Nummer." Ohne diese Erweiterung ist die erste Neuaufnahme ein
  stiller Vertragsbruch und löscht den einzigen Beleg, dass die Rechnung
  unverändert ist.
- **Was bei W3/W4 trotzdem bitgleich bleiben muss:** die **untere** Schicht.
  `weapons.rate` liefert über alle Differentialfälle dieselben Zahlen wie
  vorher; abweichen darf nur, was die Fassade darüberlegt. Das ist prüfbar und
  trennt Umbau von Bedeutungsänderung.

**Zusicherung Z1 — es gibt je Schicht genau eine Darstellung, und jedes `_total`
ist ihre Summe** (nachgetragen 2026-09-02 auf Vorlage des `director` nach W1):
Die Fassade hält je Schicht **eine** Abbildung Schadensart → Zahl. Jedes
`*_total` ist definitionsgemäss `sum(*_per_type.values())` und wird **nirgends
unabhängig gebildet**.

Anlass: heute zeigt der Waffen-Tab „AR" aus `WeaponRating.total`
(`sum(base) + sum(scaled)`), die Typzeilen darunter aus `per_type()`
(typweise summiert). Dieselben Summanden, **andere Klammerung**. Dass beide auf
dieselbe angezeigte Ganzzahl runden, ist heute Gleitkomma-Glück, nicht
Konstruktion. Der `director` liest das als stillen Driftpfad derselben Art, die
W1 gerade geschlossen hat — **das ist richtig, und es ist schlimmer als eine
Anzeigefrage:** der Grenzbeitrag des Beraters (AD-018) ist eine **Differenz
zweier Totals**. Werden die beiden Seiten unterschiedlich geklammert, setzt
nicht die Arithmetik das Rauschniveau des Vergleichs, sondern die
Inkonsistenz — und Grenzbeiträge sind klein.

Prüfbar als **exakte** Gleichheit (`==`, kein `pytest.approx`), über dieselben
Differentialfälle: `rating.total == sum(rating.per_type.values())` für jede
Schicht. Eine Toleranz würde genau die Drift verstecken, deretwegen die
Zusicherung existiert.

`weapons.WeaponRating.total` bleibt bis W4 **bitgleich unverändert** — es ist
der Bezugspunkt der Differentialprüfung, solange es zwei Pfade gibt. Es fällt
in W5, wenn es keinen Leser mehr ausserhalb der Fassade hat; ab da gibt es im
Programm genau eine Summation. `weapons.rank` sortiert dann über die
abgeleitete Summe und bekommt im selben Zug einen **stabilen Zweitschlüssel**
(`weapon["id"]`) — QA-059 hat gerade belegt, dass nicht reproduzierbare
Sortierung in diesem Programm kein Gedankenspiel ist.

**Konsequenzen:** Leicht wird — die Antwort auf QA-018 ist danach eine
Zeilenänderung an einer benannten Stelle statt eines Eingriffs an vier
Anzeigestellen; und jede neue Ansicht muss ihre Frage benennen, statt sie zu
erben. Dauerhaft schwer wird — eine Anzeige, die eine **vierte** Frage stellen
will, muss sie in `Basis` eintragen und begründen, statt sich die Eingaben
selbst zusammenzustellen. Das ist Absicht und der ganze Zweck.

**Umkehrbarkeit:** mittel. W0 bis W2 sind trivial rückgängig. Ab W3 hängt die
Anzeige daran, ab dem Berater (AD-018) die Rangfolge.

---

### AD-020 — Was die Fassade ausdrücklich NICHT vereinheitlicht (2026-09-02, Status: aktiv; Randbedingung von AD-019)

**Kontext:** Die drei gemessenen Abweichungsachsen aus QA-018/055/056 sind
**nicht drei Fehler**. Eine Fassade, die alle drei einebnet, macht das
Programm konsistent und falsch. Diese Entscheidung trennt Absicht von Fehler,
damit der `developer` beim Umbau nicht raten muss.

**Optionen:**
- **A — Alles vereinheitlichen, eine Zahl je Waffe.** Konsequenz: der
  Arsenal-Tab könnte nicht mehr fragen „wie gut wäre diese Waffe als
  Legendary", weil er auf dem ausgerüsteten Tier ränge — für eine Waffe, die
  in keinem Slot steckt, gibt es dieses Tier gar nicht. Der Tab verlöre seinen
  Zweck.
- **B — Nichts festlegen, jede Stelle behält ihre Wahl, die Fassade bündelt
  nur die Formel.** Konsequenz: QA-058 wäre auf die Formelduplikate
  zusammengeschrumpft; die drei Achsen blieben, und der nächste Tab öffnet
  eine vierte.
- **C — Absicht und Fehler einzeln benennen, die Absichten als eigene `Basis`
  führen.** Konsequenz: die Liste muss gepflegt werden und wächst mit jeder
  echten neuen Frage.

**Entscheidung:** C.

**Absicht — bleibt verschieden, und die Fassade muss es tragen:**
1. **Ziel-Tier gegen Slot-Tier (Achse B).** Der Arsenal-Tab rankt bewusst auf
   einem gewählten Ziel-Tier. Das ist keine Abweichung, sondern die Frage des
   Tabs. `Basis.CANDIDATE` bekommt `target_tier` als Pflichtargument; es gibt
   keinen Vorgabewert, der still das Slot-Tier einsetzt.
2. **Grundattribute gegen erhöhte Attribute (Achse C, linke Tafelzahl).** Die
   „vorher"-Zahl steht auf `build.base_attributes`, weil sonst das Vorher/
   Nachher der Tafel verschwindet. `Basis.BARE` ist genau dafür da.
3. **Startwaffen-Strafe (`*AttackPowerRate`, x0,85).** Sie hängt an der
   **Paarung** Slot 1 + eigene Startwaffe des Nightfarers, im Spiel verifiziert
   2026-08-22. `Basis.CANDIDATE` hat keinen Slot und darf sich keinen erfinden;
   die Strafe erscheint nur in `Basis.EQUIPPED`.
4. **Klassengebundene Raten (`class_rates`) sind je Waffe verschieden**, nicht
   je Build. Sie dürfen nicht zu einem einzigen Build-Faktor zusammengezogen
   werden — „Improved Melee Attack Power" hebt das Greatsword und nicht den
   Bogen daneben (AD-005-Kommentar, unverändert gültig).
5. **Krit-Rate bleibt draussen** (`model.CRIT_RATE`). Attack Rating ist der
   gewöhnliche Treffer. Unverändert aus `damage.py`.

**Fehler — wird vereinheitlicht:**
6. **Kachel gegen Tafel (`app.py:2865` gegen `attack_rating`).** Dieselbe
   Waffe, derselbe Slot, dasselbe Tier, zwei Zahlen gleichzeitig auf dem
   Schirm, und nichts unterscheidet die Fragen. Das ist eine Frage, zweimal
   beantwortet. Beide gehen auf `Basis.EQUIPPED`.
7. **Die vierfach ausgeschriebene Formel je Schadensart.** `WeaponRating`
   bekommt `per_type()`.
8. **Die implizite Wahl der Multiplikatorschicht.** Heute entscheidet
   darüber, welches Modul eine Anzeigestelle importiert hat. Künftig
   entscheidet `MULTIPLIERS_FOR`, und die Entscheidung hat einen Namen.

**Keine Absicht und kein Fehler, sondern eine andere Art von Frage:**

9. **Die Summationsreihenfolge (Klammerung).** Sie stellt keine andere Frage, sie beantwortet dieselbe mit einem anderen letzten Bit. Diese Liste trennt Absicht von Fehler bei **semantischen** Unterschieden; eine numerische Klammerung gehört nicht hinein. Entschieden in **AD-024** (sie folgt aus Zusicherung Z1 und ist keine Genauigkeitsfrage). Wer hier nach ihr sucht, findet sie dort — nachgetragen 2026-09-02 aus W4, weil der `developer` sie zu Recht gemeldet statt einsortiert hat.

**Was diese Entscheidung ausdrücklich NICHT festlegt:** ob die Zahl 203,4 oder
244,1 richtig ist. Sie legt fest, **wo** die Zahl entsteht, nicht **welchen
Wert** sie hat. Der Wert hängt an der Spielmessung des Nutzers (siehe
`docs/state.md`, Abschnitt „Die Messung im Spiel") und wird zu W6.

**Konsequenzen:** Leicht wird — eine begründete Abweichung ist im Code als
`Basis` sichtbar statt als stille Unterschiedlichkeit der Aufrufargumente.
Dauerhaft schwer wird — wer eine neue Ansicht baut, muss vorher entscheiden,
welche Frage sie stellt. Das ist Absicht.

**Umkehrbarkeit:** leicht. Die Liste ist Dokumentation plus ein Enum; ein
Eintrag mehr oder weniger kostet nichts.

---

### Nachtrag IV 2026-09-02 — Antworten vor W2 (Z1, AD-022, AD-023)

Anlass: der W1-Bericht des `developer` (W0 und W1 gebaut, 30 000
Differentialfälle, 0 Abweichungen, Vergleicher selbst mutationsgeprüft) und
eine Korrektur des `ui-ux-designer` an meiner Begründung aus Nachtrag III.

### Auflagen für W2

**A1 — Die Fassade bildet kein `total` unabhängig.** Zusicherung Z1 in AD-019,
mit exaktem Gleichheitstest (`==`, kein `approx`). Die Lesart des `director`
ist bestätigt und trägt weiter als angenommen: der Grenzbeitrag (AD-018) ist
eine **Differenz zweier Totals**, und zwei Klammerungen setzen das
Rauschniveau des Vergleichs statt der Arithmetik.

**A2 — Die doppelte `fields`-Schleife in `attack_rating` darf in W2
zusammengelegt werden, aber nur unter Erhalt der Multiplikationsreihenfolge.**
Heute wird je Feld erst `build.rates[f]`, dann `class_rates[f]` an `rate`
heranmultipliziert; `rates_in_play` benutzt daneben das Produkt beider. Eine
Zusammenlegung, die stattdessen `value = build.rates[f] * class_rates[f]`
bildet und `rate *= value` rechnet, ändert die Assoziationsreihenfolge und
damit potentiell das letzte Bit — W2 ist als bitgleich zugesagt. Also:
zusammenlegen mit unveränderter Reihenfolge, oder gar nicht. Gelingt es nicht
sauber, wandert es nach W5, wo keine Bitgleichheit mehr zugesagt ist. Die
Entscheidung darüber trifft der `developer` am Differentialtest, nicht am
Augenschein.

**A3 — W2 fasst nur `nrplanner/damage.py` an.** Dass `arsenaltab` weiterhin
`weapons.rank` ruft, ist **richtig und W4**, nicht W2. Bestätigt. Genau
deshalb kann W2 bitgleich sein: es ändert keinen Aufrufer.

**A4 — W1b geht W2 voraus** (AD-022): reine Umbenennung, durch die bestehende
Differentialstrecke gedeckt, damit W2 „umbenannt" nicht mit „verändert"
vermischt.

### AD-022 — Ein Name je Schicht: `scaled_*` vor der Multiplikatorschicht, `final_*` danach; die Umbenennung ist ein eigener Schritt W1b vor W2 (2026-09-02, Status: aktiv; präzisiert AD-019)

**Kontext:** Meldung des `developer` aus W1. Nach W1 heissen drei Dinge auf
drei Schichten gleich: `weapons.WeaponRating.per_type()` ist eine **Methode**
(vor Multiplikatoren), `damage.AttackRating.per_type` ein **Feld** (nach
Multiplikatoren), und AD-019 sah `Rating.per_type` als drittes vor. Zwei davon
unterscheiden genau das, was der ganze Umbau trennen soll.

**Beim Nachlesen kommt eine vierte Kollision dazu, die nicht gemeldet war und
eine Schicht tiefer sitzt:** `weapons.WeaponRating.base` heisst „vor der
Attributskalierung"; `damage.AttackRating.base_total` heisst „auf den
**Grundattributen**" (`base_total = before.total`, und `before` ist
`weapons.rate(..., build.base_attributes, ...)`). Zwei Bedeutungen von `base`
in zwei Modulen, die einander importieren. Dieselbe Fehlerklasse wie QA-058,
nur in der Benennung statt in der Arithmetik.

**Optionen:**
- **A — Nur das gemeldete `per_type` entzerren.** Billig. Konsequenz: `base`
  bleibt doppeldeutig, und die Fassade erbt die Zweideutigkeit in ihrem
  Feldnamen.
- **B — Freie Namen je Stelle** („`per_damage_type`", „`by_type`", …).
  Konsequenz: verschieden genug, um nicht zu kollidieren, und nichtssagend
  genug, um nicht zu erklären, welche Schicht gemeint ist.
- **C — Eine mechanische Regel über alle drei Schichten**, abgeleitet aus dem
  Vokabular, das `damage.py` schon führt (`base_total`, `scaled_total`,
  `final_total`).

**Entscheidung:** C. Die Regel lautet:

> Der Name nennt die **Schicht**, und `X_total` ist immer die Summe genau des
> gleichnamigen `X_per_type` (Zusicherung Z1 in AD-019). Kein Name ohne
> Schichtpräfix.

| Schicht | je Schadensart | Summe | Bedeutung |
|---------|----------------|-------|-----------|
| 1 | `scaled_per_type` | `scaled_total` | Grundschaden x Verstärkung + Attributskalierung |
| 2 | `final_per_type` | `final_total` | nach `build.rates` x `class_rates` — die angezeigte Zahl |

Konkret: `weapons.WeaponRating.per_type()` → **`scaled_per_type()`**;
`damage.AttackRating.per_type` → **`final_per_type`**; `Rating` aus AD-019
führt beide Paare und **kein** unpräfigiertes `per_type`/`total`.
`AttackRating.base_total` → **`bare_scaled_total`** (die Schicht-1-Summe auf
Grundattributen), womit `base` wieder nur eines heisst.

Ausserdem: das Enum aus AD-019 heisst **`Question`**, nicht `Basis` — `Basis`
neben `base_*` ist dieselbe Falle noch einmal. Mitglieder unverändert
`EQUIPPED`, `CANDIDATE`, `BARE`.

**Eigener Schritt W1b, vor W2 — nicht in W2 hinein.** Begründung, und sie ist
nicht Ordnungsliebe: W1b ist eine reine Umbenennung und damit **beweisbar
bitgleich**; die Differentialstrecke aus W1 (30 000 Fälle, Vergleicher
mutationsgeprüft) deckt sie ohne eine Zeile neuen Testcode. W2 legt die Fassade
an. Steckt die Umbenennung in W2, kann der Differentialtest „umbenannt" nicht
mehr von „verändert" unterscheiden — und genau diese Trennung ist das Gerüst
des ganzen Migrationspfads (AD-019: W1/W2 bitgleich, ab W3 gewollt anders).
Nebenbei bleibt der W2-Diff lesbar.

**Konsequenzen:** Leicht wird — man kann einer Zahl ihren Namen ansehen, statt
ihren Aufrufweg zurückzuverfolgen. Dauerhaft schwer wird — jeder künftige
Zahlenname trägt ein Präfix, auch wo es umständlich klingt. Der Preis ist
Tipparbeit, der Gegenwert ist, dass QA-058 nicht als Benennungsbefund
zurückkommt.

**Umkehrbarkeit:** leicht. Eine Umbenennung, durch die Differentialstrecke
abgesichert.

---

### AD-023 — Das Invarianzargument aus Nachtrag III gilt nur für Multiplikatoren des Grundzustands; für Kandidaten, die selbst eine Angriffsrate mitbringen, kann W6 die Reihenfolge drehen (2026-09-02, Status: aktiv; **korrigiert Nachtrag III**)

**Kontext:** Der `ui-ux-designer` hat beim Schreiben der Spec einen Fehler in
meiner Begründung gefunden. Nachtrag III behauptete, der Berater-Bau sei ab W5
nicht mehr von der Spielmessung (W6) abhängig, weil eine flache
Multiplikatorschicht den Grenzbeitrag nur **skaliert**. **Die Randbedingung
dieser Aussage war „der Multiplikator kommt aus dem Grundzustand" — und sie
wurde still auf jeden Kandidaten ausgedehnt.** Genau der Fehler, vor dem meine
eigene Rollenregel warnt.

**Nachgerechnet.** Sei `S(·)` die Schicht-1-Summe und `m(·)` das Produkt der
Angriffsraten. Der Grenzbeitrag eines Kandidaten `k` auf Grundzustand `B` ist

```
Delta(k) = m(B+k) * S(B+k) - m(B) * S(B)
```

- Bringt `k` **nur Attribute** mit, ist `m(B+k) = m(B) = m`, also
  `Delta(k) = m * (S(B+k) - S(B))`. Ein gemeinsamer Faktor über alle
  Kandidaten: Grössen ändern sich, Rangfolge nicht. **So weit trug
  Nachtrag III.**
- Bringt `k` **selbst eine Angriffsrate** `r > 1` mit, ist `m(B+k) = m * r`:

```
Delta(k) = m * (r - 1) * S(B)  +  m * r * (S(B+k) - S(B))
```

Der erste Summand hängt an `S(B)` — am **ganzen** Angriffswert, nicht am
Zuwachs. Grössenordnung: bei `S(B) ~ 300` und `r = 1,20` sind das 60, während
ein Relikt mit +5 Stärke `S` im einstelligen Bereich bewegt. Und der Term ist
**genau dann null, wenn W6 die Multiplikatorschicht für `Question.CANDIDATE`
abschaltet**. W6 entscheidet also nicht die Grösse, sondern **welche
Effektfamilie gewinnt**. Die strittige Familie aus T-023 (Improved Thrusting
Counterattack, Improved Sorceries, Improved Incantations) ist genau diese.

**Der `ui-ux-designer` hat recht, die Korrektur des `director` in
`docs/state.md` ist richtig, und Nachtrag III ist an dieser Stelle falsch.**

**Optionen für den Umgang bis W6:**
- **A — Berater bis W6 gar nicht ausliefern.** Sicher, und es hängt ein ganzes
  Feature an einer Beobachtung, die der Nutzer machen soll, wenn er Zeit hat.
- **B — Pauschaler, immer sichtbarer Reihenfolgevorbehalt an jeder
  Picker-Zeile.** Ehrlich, aber falsch dosiert: er stünde auch dort, wo die
  Rangfolge nachweislich invariant ist, und ein Vorbehalt, der immer da ist,
  wird nicht gelesen.
- **C — Der Vorbehalt wird berechnet statt gesetzt.** Die Invarianz ist keine
  Eigenschaft der Zielrichtung, sondern des **Kandidatenfelds**, und sie ist
  exakt prüfbar: ein Kandidat ist betroffen, wenn einer seiner Effekte ein Feld
  aus `AR_RATE_FOR` oder dessen klassengebundener Variante trägt. Die Familie
  ist **vollständig aufgezählt** (~20 IDs, `docs/state.md`), also ist das ein
  Test, keine Heuristik.

**Entscheidung:** C.

1. **Kein Kandidat des Laufs trägt ein AR-Ratenfeld** → die Rangfolge ist
   gegenüber W6 invariant. **Kein Vorbehalt.** Das ist der häufige Fall.
2. **Mindestens einer trägt eines** → der Vorbehalt erscheint, und zwar **an
   den betroffenen Zeilen**, nicht als Banner über der Liste.

Die Zahlengrösse bleibt in beiden Fällen unter dem Attack-Rating-Vorbehalt aus
AD-004, bis W6 steht — das ist unverändert.

**Folge für die Reihenfolge, und das ist die Korrektur an Nachtrag III:** Der
**Bau** des Beraters ist ab W5 nicht von der Spielmessung blockiert. Die
**Auslieferung einer Rangfolge, die AR-Raten-Kandidaten enthält**, ist es sehr
wohl — bis W6 nur mit der Markierung aus Punkt 2. Prüfpunkt 16 (abnehmender
Ertrag) bleibt gültig, weil er auf Attributskandidaten formuliert ist; er ist
**kein** Beleg für die Rangfolge gemischter Felder und darf nicht als solcher
gelesen werden.

**Konsequenzen:** Leicht wird — der Nutzer sieht den Vorbehalt dort, wo er
zutrifft, und nirgends sonst. Dauerhaft schwer wird — der Berater muss je Lauf
wissen, welche Kandidaten eine Angriffsrate tragen; das ist eine Zusatzabfrage
über die Effekte des Kandidaten, keine zweite Rechnung.

**Umkehrbarkeit:** leicht. Fällt W6 auf „aus", verschwindet der Fall
vollständig; fällt er auf „an", bleibt die Markierung als Erklärung stehen und
kann dann entfallen.

---

### Korrektur an Nachtrag III

Der Abschnitt „Reihenfolge gegenüber dem Berater" in Nachtrag III ist an einer
Stelle **falsch** und wird durch AD-023 ersetzt: die Invarianz des
Grenzbeitrags gegenüber W6 gilt nur, solange der Multiplikator aus dem
**Grundzustand** kommt. Bringt der Kandidat selbst eine Angriffsrate mit, tritt
ein Term `m·(r−1)·S(B)` hinzu, der am **ganzen** Angriffswert hängt und die
Rangfolge drehen kann. Die Randbedingung meiner Aussage war benannt gewesen —
angewendet wurde sie trotzdem auf den allgemeinen Fall.

Was von Nachtrag III **stehen bleibt:** die Fassade muss vor den Berater; der
**Bau** des Beraters ist ab W5 nicht von der Spielmessung blockiert.
Was **ersetzt** wird: die Auslieferung einer Rangfolge, die
AR-Raten-Kandidaten enthält, ist es sehr wohl — mit der berechneten Markierung
aus AD-023, Punkt 2, statt eines pauschalen Vorbehalts.

### Nachtrag V 2026-09-02 — Die Klammerungsfrage aus W4 (AD-024)

Anlass: der `developer` hat in W4 eine Abweichung gemessen, die zu keinem der
acht AD-020-Punkte passt, und sie **gemeldet statt einsortiert**. Das war
richtig; sie gehört in keine der beiden vom `director` vorgeschlagenen Stellen.

### Die drei Antworten in Kurzform

1. **Ort:** weder neunter AD-020-Punkt noch Absatz in AD-022, sondern
   **AD-024**. AD-020 trennt Absicht von Fehler bei *semantischen*
   Unterschieden; die Klammerung ist keiner. AD-022 wäre der Ort gewesen,
   solange es um die Fassade ginge — die Frage betrifft aber inzwischen eine
   **zweite Stelle** (`bonus`-Schleife in `weapons.rate`), die mit der Fassade
   nichts zu tun hat und eine **andere** Antwort bekommt. AD-020 erhält einen
   Punkt 9, der auf AD-024 verweist, damit man sie dort findet, wo man sucht.
2. **Absicht oder Fehler: keins von beidem, und die vorgelegte Lesart trifft
   nicht zu.** „Alte Klammerung = Fehler, 584 ULP = Korrektur" behauptet, eine
   der beiden Summationen sei genauer — das ist nicht belegbar, und gegen das
   Spiel ist keine von beiden geprüft. **Der Fehler war nie einer der beiden
   Werte, sondern dass es zwei gab.** Die 584 ULP sind der Preis der
   Vereinheitlichung; die Messung belegt, dass er unsichtbar ist (0 von 7 172
   Anzeigetexten).
3. **W5:** Die Frage verschwindet nicht. Z1 bleibt tragend; Teilsummen bleiben
   erlaubt, aber nicht auf Gleichheit mit `final_total` prüfbar; und
   Nicht-tun-Regel 29 (stabiler Zweitschlüssel in `weapons.rank`) ist ab jetzt
   **gemessen begründet** statt vorsorglich — nahe Gleichstände können durch
   1 ULP die Plätze tauschen.

### Beide Stellen unter einer Regel

> Die Summationsreihenfolge wird nur geändert, wenn die Änderung **zwei
> Darstellungen derselben Zahl auf eine reduziert**. Eine Änderung, die nur
> „genauer" verspricht, wird nicht vorgenommen.

Arsenal-Tab (W4): erfüllt sie, wird gemacht. `bonus`-Schleife: erfüllt sie
nicht (nur eine Darstellung, 48 100 von 258 192 Karten betroffen), **bleibt
dauerhaft** eine Schleife. Der dortige Kommentar bindet sie heute an die
Bitgleichheit eines Schrittes und sagt damit das Falsche — beim nächsten
Anfassen auf die Begründung aus AD-024 umschreiben. Das ist eine
Kommentarkorrektur, kein eigener Auftrag.

### AD-024 — Summationsreihenfolge ist eine Eindeutigkeits-, keine Genauigkeitsentscheidung; sie wird nur geändert, wo sie zwei Darstellungen derselben Zahl beseitigt (2026-09-02, Status: aktiv; folgt aus Zusicherung Z1 in AD-019, ergänzt AD-020)

**Kontext:** Meldung des `developer` aus W4, ausdrücklich **nicht** einsortiert,
weil sie zu keinem der acht Punkte in AD-020 passt. Der Umzug des Arsenal-Tabs
von `WeaponRating.total` auf `Rating.final_total` tauscht zwei Klammerungen
derselben Summanden:

```
WeaponRating.total   = sum(base) + sum(scaled)          # je Ebene
Rating.final_total   = sum(base[t] + scaled[t] ...)     # je Schadensart
```

Gemessen: **584 von 7 172 Datensätzen (8,1 %) verschieben sich um exakt 1 ULP**,
grösster Absolutbetrag **5,68e-14**, auf 424 Armaturen; **ausnahmslos
mehrtypige** Armaturen, keine einzige einartige — bei einer Schadensart sind
beide Klammerungen identisch. **Der Anzeigetext bewegt sich in 0 von 7 172
Fällen.** Vorlauf über zwei Level: 1 403 von 14 344 (9,8 %), gleiche Richtung
und Grössenordnung. Mechanismus: ab CPython 3.12 summiert das eingebaute `sum()`
kompensiert (Neumaier), eine ausgeschriebene Schleife nicht — gleiche
Summanden, gleiche Reihenfolge, bis zu 1 ULP Unterschied.

**Warum das weder in AD-020 noch in AD-022 gehört.** AD-020 trennt Absicht von
Fehler bei **semantischen** Unterschieden: welche Frage eine Anzeige stellt
(Attributsatz, Tier, Multiplikatorschicht). Die Klammerung stellt keine andere
Frage; sie beantwortet dieselbe mit einem anderen letzten Bit. Sie als neunten
Punkt zu führen, würde verwischen, wofür die Liste da ist. AD-022 regelt die
**Benennung** (`X_total` zu `X_per_type`) und ist der Ort, aus dem die
Klammerung folgt — aber die Frage betrifft inzwischen eine **zweite Stelle**,
die mit der Fassade nichts zu tun hat (siehe unten), und die trägt eine andere
Antwort. Deshalb eine eigene Entscheidung; AD-020 bekommt nur einen Verweis.

**Optionen:**
- **A — Die alte Klammerung war der Fehler, die 584 ULP sind die Korrektur.**
  Konsequenz: Es wird behauptet, eine der beiden Summationen sei genauer. Das
  ist **nicht belegbar** — beide sind gleich gute Näherungen der exakten Summe,
  und gegen das Spiel ist keine von beiden geprüft (die Messung zu QA-018 steht
  noch aus). Die Behauptung lädt dazu ein, die Frage später wieder
  aufzumachen: „welche ist denn nun genauer?"
- **B — Toleranz einführen und beide zulassen.** Konsequenz: hebt Z1 auf und
  stellt den Driftpfad wieder her, den W1 bis W4 gerade geschlossen haben.
- **C — Die Klammerung je Schadensart ist verbindlich, weil sie aus Z1 folgt —
  nicht weil sie genauer wäre.** Konsequenz: die Frage ist ein für alle Mal
  entschieden und kann nicht mit Genauigkeitsargumenten aufgerollt werden.

**Entscheidung:** C, und damit **Widerspruch im Detail** zur Vorlage des
`director`: die Einordnung „alte Klammerung = Fehler, 584 ULP = Korrektur"
trifft nicht zu. **Der Fehler war nie einer der beiden Werte — der Fehler war,
dass es zwei gab.** Die 584 ULP sind der **Preis der Vereinheitlichung**, nicht
ihre Korrektur, und die Messung des `developer` belegt genau das, wofür sie
gebraucht wird: der Preis ist auf dem Bildschirm nicht sichtbar (0 von 7 172).

**Die Regel, die beide Stellen entscheidet:**

> Die Summationsreihenfolge wird **nur** geändert, wenn die Änderung **zwei
> Darstellungen derselben Zahl auf eine reduziert**. Eine Änderung, die nur
> „genauer" verspricht, wird nicht vorgenommen.

Angewendet:
1. **Arsenal-Tab auf `final_total` (W4):** erfüllt die Bedingung — zwei
   Darstellungen werden eine. **Wird gemacht**, Kosten gemessen und unsichtbar.
2. **Die `bonus`-Schleife in `weapons.rate`:** erfüllt die Bedingung **nicht**.
   Dort gibt es nur **eine** Darstellung; kompensierte Summation wäre eine
   einseitige Genauigkeitsänderung ohne Konsistenzgewinn — und sie verschiebt
   **48 100 von 258 192 Karten**, zwei Grössenordnungen mehr. **Bleibt eine
   Schleife**, und zwar **dauerhaft**, nicht „bis W5". Der Kommentar dort, der
   sie an die Bitgleichheit eines Schrittes bindet, sagt damit das Falsche und
   ist beim nächsten Anfassen auf diese Begründung umzuschreiben. Wieder
   interessant wird die Stelle erst, wenn eine Abweichung **auf dem Bildschirm
   oder gegen das Spiel** gemessen wird — nicht wenn jemand sie im Code sieht.

**Was nach W5 übrig bleibt** (Frage 3 des `director`): Die Frage verschwindet
**nicht**. Mit `WeaponRating.total` fällt eine der beiden Klammerungen weg, und
Z1 wird innerhalb der Fassade trivial wahr — aber die **Regel** muss stehen
bleiben, sonst schreibt die nächste Anzeige `sum(base) + sum(scaled)` erneut
hin. Drei Reste, ausdrücklich:
- **Z1 bleibt die tragende Zusicherung** (exakte Gleichheit, kein `approx`).
- **Teilsummen sind erlaubt, Vergleiche nicht.** Wer über ausgewählte
  Schadensarten summiert, bildet das aus `final_per_type` — und vergleicht das
  Ergebnis **nicht** auf Gleichheit mit `final_total`.
- **`weapons.rank` braucht den stabilen Zweitschlüssel aus Nicht-tun-Regel 29,
  und das ist ab jetzt gemessen begründet statt vorsorglich:** nach dem Wegfall
  von `total` sortiert `rank` über die abgeleitete Summe; 584 von 7 172 Werten
  verschieben sich um 1 ULP, also können nahe Gleichstände die Plätze tauschen.
  `(-summe, weapon["id"])`.

**Geprüft und ausdrücklich kein Risiko:** Der Golden-Stand ist von der
CPython-Version **nicht** betroffen — `tests/weapon_damage_cases.rounded()`
rundet auf sechs Nachkommastellen, und 5,68e-14 liegt acht Grössenordnungen
darunter. Ein Wechsel der CPython-Version kann `weapon_damage.json` nicht rot
färben. (Nachgesehen, nicht angenommen: die Alternative wäre gewesen, hier eine
Warnung zu hinterlassen, die es nicht braucht.)

**Konsequenzen:** Leicht wird — künftige Meldungen dieser Klasse sind in einem
Satz entschieden, ohne Genauigkeitsdebatte. Dauerhaft schwer wird — eine
tatsächlich vorhandene Ungenauigkeit in der `bonus`-Schleife bliebe unter
dieser Regel unangetastet, bis sie sichtbar wird. Das ist bewusst: gegen das
Spiel ist keine dieser Zahlen validiert, und das letzte Bit einer unvalidierten
Zahl zu ändern ist Bewegung ohne Information.

**Umkehrbarkeit:** leicht für Punkt 1 (die Klammerung folgt aus Z1 und fiele
mit ihr), leicht für Punkt 2 (es bleibt alles, wie es ist).

---

---

## Themenbereich B — Suche, Kandidaten, Haltezustand, Grenzbeitrag

*Wie aus dem Besitz des Spielers ein Vorschlag wird. AD-003 waehlt das
Verfahren, AD-013 den Gegenstand, den es bewegt, AD-014 bis AD-017 den
Haltezustand, und AD-018 dreht den Hauptweg vom Gesamtlauf zum Grenzbeitrag
im Picker.*

### Nachtrag 2026-09-02 — Festhalten und Flüche (AD-014 bis AD-016)

Dieser Nachtrag schreibt die Umsetzung, die Prüfpunkte, die Risiken und die
offenen Fragen fort. **Was er nicht anfasst: AD-002.** Die Entscheidung,
`model.compute()` an jedem Suchschritt zu benutzen, trägt beide neuen
Anforderungen unverändert — sie ist der Grund, warum Stacking-Regeln bei
festgehaltenen Slots und Flüche in der Bewertung **nichts kosten**. Wären
die Regeln in einem zweiten Scorer nachgebaut, wäre jede der beiden
Anforderungen ein eigener Umbau gewesen.

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

### Korrekturnotiz zu AD-003.5 (2026-09-07; Herkunft: D-5 des `director` vom 06.09.2026, gemeldet vom `developer` in T-067)

**Ersetzt** AD-003, Ausgestaltung Punkt 5: „*Ausgabe: die besten `top_n`
Endzustände, nicht nur der beste*".

**Der ursprüngliche Wortlaut bleibt stehen.**

**Neu verbindlich:** **Es gibt kein `top_n`.** Die Beam-Breite **W ist die
Zahl der Endzustände**; `search.beam` gibt sie geordnet zurück, bester
zuerst, und ein Aufrufer, der weniger will, nimmt den Kopf der Liste.

**Begründung, in der Reihenfolge ihres Gewichts:**

1. **Ein `top_n` wäre eine zweite Zahl mit eigener Herleitung.** AD-003 hat
   K und W gemessen begründet (K=20, W=40, ungünstigster realer Fall unter
   einer halben Sekunde). Eine dritte Stellschraube ohne eigene Messung
   verstiesse gegen L-001.
2. **Sie wäre eine dritte Grösse im Cache-Schlüssel** und damit ein weiterer
   Weg, an dem zwei Läufe sich für denselben halten können.
3. **Sie hat keinen Leser.** `top_n` kommt in `nrplanner/` nicht vor
   (Volltextsuche gegen `fd9f2bc`: ein Treffer, und der steht im Docstring
   von `search.py:321`, wo er genau diesen Sachverhalt erklärt).

**Die Zusage aus AD-003 bleibt vollständig erfüllt:** der Spieler sieht
Alternativen und kann Begründungen vergleichen (A5) — er sieht W davon statt
`top_n` davon.

**Was das nicht ist:** kein Verzicht auf ein Bedienelement, das es je gab.
D-5 sagt ausdrücklich „kein `top_n`-Stellrad" — die Frage war, ob der Nutzer
die Zahl der gezeigten Vorschläge selbst dreht, und die Antwort ist nein.
Kommt sie je, ist es eine Entscheidung des `ui-ux-designer` über eine
Anzeigemenge, nicht eine zweite Suchbreite.

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

### AD-014 — Ein festgehaltener Slot ist Randbedingung der Suche, nicht Startwert: er geht als Grundzustand in jede Bewertung ein (2026-09-02, Status: aktiv)

**Kontext:** Der Nutzer hat am 2026-09-02 entschieden (`GOAL.md`, F1): der
Spieler kann einzelne Slots festhalten, der Berater optimiert nur den Rest.
Seine Begründung: „Ich will immer vom aktuellen Stand aus optimieren können.
Falls ich z. B. um 1 Relikt herum bauen will und dann ein Build optimieren
will, wo es aber um dieses eine 'nicht optimale' Relikt geht."

Die Lesart des `director` — **festgehalten heisst Randbedingung, nicht
Startwert** — ist am Bestand geprüft und **bestätigt**. Der Beleg ist die
Signatur, an der alles hängt:
`model.compute(hero, level, effects, curves, weapon, weapons_held, declared)`
nimmt **eine flache Effektliste über alle Slots**. Die Bewertung kennt keine
Slots. Ein festgehaltenes Relikt kann deshalb nur auf einem Weg wirken: seine
Effekte (und Flüche, AD-015) stehen in *jeder* Liste, die die Suche bewertet.
Damit ist „optimiere um dieses Relikt herum" tatsächlich ein **anderes
Suchproblem** — ein Problem über weniger Variablen mit einem anderen
Grundzustand, nicht dasselbe Problem mit einem anderen Anfangspunkt.

Ein Startwert wäre auch fachlich falsch: er würde in der Beam-Suche in der
nächsten Ebene wieder verdrängt, und genau der Fall, um dessentwillen der
Nutzer die Funktion will (ein für sich *nicht* optimales Relikt), ist der
Fall, in dem er zuerst verdrängt würde.

**Kräfte:** Die Rechnung darf nicht zweimal existieren (AD-002). Der
Grundzustand darf an keiner Bewertungsstelle vergessen werden — vergisst ihn
die Vorsortierung, empfiehlt der Berater Kandidaten, deren Beitrag das
festgehaltene Relikt bereits abdeckt. Und das Budget aus A6 darf nicht kippen.

**Optionen:**
- **A — Startwert.** Festgehaltene Relikte werden als Anfangsbelegung in den
  Beam gelegt, die Suche läuft über alle Slots. Konsequenz: der Beam ersetzt
  sie in der nächsten Ebene wieder; „festhalten" wäre nur eine Vorbelegung
  und beantwortete die Frage des Nutzers nicht. Verworfen.
- **B — Nachträglich filtern.** Frei suchen, am Ende nur Ergebnisse behalten,
  die den festgehaltenen Slot zufällig gleich belegen. Konsequenz: derselbe
  Fehler wie AD-013 Option B, nur schärfer — bei einem bewusst nicht optimalen
  Relikt bleibt von 40 Ergebnissen keines übrig. Verworfen.
- **C — Grundzustand.** Die festgehaltenen Slots bilden einen `held_build`;
  die Suche läuft nur über die freien Slots, und jede Bewertung — auch die
  Vorsortierung — bewertet `held_effects + gewählte Effekte`. Konsequenz: die
  Suche wird kleiner statt grösser, die Stacking-Regeln greifen von selbst
  (AD-002), und es kommt genau eine Datenstruktur dazu.

**Entscheidung:** C.

**Ausgestaltung, verbindlich:**

1. **Genau eine Bewertungsstelle im Berater.** Neu im Modulschnitt aus
   AD-001: `nrplanner/advisor/evaluate.py` mit einer Funktion

   ```python
   # advisor/evaluate.py  (illustrierend, kein Anwendungscode)
   def evaluate(problem, assignment, ctx) -> model.Build:
       """The one place under advisor/ that reaches model.compute.

       Held slots, chosen candidates, their curses and the weapon effects are
       assembled here and nowhere else -- pre-sort, beam step and baseline all
       come through this door, so none of them can forget the held slots.
       """
   ```

   Das ist kein Stilwunsch, sondern die Durchsetzung: „der festgehaltene
   Beitrag geht in jede Bewertung ein" ist eine Regel, die man an drei Stellen
   vergessen kann, solange es drei Stellen gibt. `candidates.py`, `search.py`
   und der Grundlauf rufen `evaluate`; keines von ihnen ruft `model.compute`.
   Der `compute`-Wächter (`tests/test_one_build.py`) erwartet danach
   `{"nrplanner/app.py": 1, "nrplanner/advisor/evaluate.py": 1}` — **eine**
   neue Zeile, und jede zweite fällt auf. Abhängigkeitsrichtung:
   `types` → `evaluate` → `candidates`/`goals`/`search`/`explain`.

2. **Suchtiefe = Zahl der freien Slots.** Festgehaltene Slots sind keine
   Ebenen der Beam-Suche. Sind alle Slots festgehalten, findet **keine Suche**
   statt: das Ergebnis ist der bewertete Ist-Zustand mit einer Zeile, die das
   sagt. Ein leerer Beam ist kein Fehlerfall.

3. **Die Vorsortierung bewertet gegen den Grundzustand**, nicht isoliert:
   Rang eines Kandidaten = `goal(evaluate(held + Kandidat))`. Das ist die
   einzige Stelle, an der das Festhalten die *Qualität* verbessert statt nur
   den Raum zu verkleinern — die in AD-003 benannte schärfste Schwäche
   (isolierte Vorsortierung, OF-10) wird für jeden festgehaltenen Slot
   kleiner, weil der Kontext, den ihr fehlte, jetzt teilweise dasteht.

4. **Farbsymmetrie nur über freie Slots.** AD-003 Punkt 2 schränkt die Wahl
   innerhalb einer Gruppe gleichfarbiger Slots auf aufsteigende
   Kandidatenreihenfolge ein. **Diese Regel wurde unter der Bedingung
   „alle Slots sind frei" geprüft und ist dort richtig; das Festhalten
   verletzt diese Bedingung.** Beispiel `Wylder's Urn` `[Rot, Rot, Blau]`:
   ist der erste rote Slot festgehalten, sind die beiden roten Slots **nicht
   mehr austauschbar**, und die aufsteigende Regel würde jeden roten
   Kandidaten mit kleinerem Index als das festgehaltene Relikt still
   ausschliessen. Die Symmetriegruppen werden deshalb **über die freien Slots
   allein** gebildet. Ein einzelner freier Slot einer Farbe hat keine
   Symmetrie und keine Einschränkung.

5. **Handles: der Grundzustand belegt vor.** Der Anfangszustand der Suche
   trägt die Handles der festgehaltenen Relikte in seinem `frozenset`
   (AD-013 Punkt 2). Damit kann kein festgehaltenes Exemplar ein zweites Mal
   vorgeschlagen werden. Der Fall „festgehaltenes Relikt **ohne** Handle"
   (Custom relic, oder ein Save ohne lesbare Handle-Tabelle) trägt sich ohne
   neue Regel: AD-013 Punkt 4 nimmt handle-lose Relikte bereits aus dem
   Kandidatenraum, sie können also gar nicht vorgeschlagen werden. Ein
   festgehaltenes „Custom relic" ist zulässig — es ist eine Randbedingung,
   kein Vorschlag, und `UI_SPEC` AK-16 (kein Custom relic **im Vorschlag**)
   bleibt unberührt.

6. **Erklärt wird gegen den Grundzustand, nicht gegen den leeren Build.**
   S8/AD-010 nannten „die Differenz zum leeren Build". Mit festgehaltenen
   Slots ist das falsch: die Begründung schriebe dem Vorschlag die Effekte
   des festgehaltenen Relikts gut. Bezugspunkt ist `evaluate(held, {})`.
   Die Rangzahl bleibt der **absolute** Wert des ganzen Builds (eine
   Autorität); zusätzlich weist das Ergebnis den **Zugewinn gegenüber dem
   Grundzustand** aus. Das kostet genau einen zusätzlichen `evaluate`-Aufruf
   je Lauf.

7. **Ein festgehaltener leerer Slot bedeutet „bleibt leer"** und wird nicht
   belegt. Ob die Oberfläche das anbietet, entscheidet der `ui-ux-designer`;
   die Suche muss es vertragen.

8. **Nichts wird persistiert.** Der Haltezustand ist Teil des
   `AdvisorRequest` (AD-006 Punkt 8: unveränderliche Datenklassen über die
   Thread-Grenze), nicht `QSettings`, nicht Platte (AD-007).

**Laufzeit — das Budget hält, und zwar beweisbar ohne neue Messung.** Die
Kosten der Beam-Suche sind `Ebenen × W × K` Bewertungen; die Kosten *einer*
Bewertung wachsen mit der Zahl der beitragenden Relikte (0,10 ms bei wenigen,
0,18–0,25 ms bei vollem Build). Ein Lauf mit `h` festgehaltenen Slots
bewertet auf seiner ersten Ebene Builds aus `h+1` Relikten, auf seiner
letzten aus 6 — er zahlt also **genau die tiefsten `6−h` Ebenen des heutigen
Laufs** und keine einzige zusätzliche. Damit ist er durch die gemessenen
**0,46 s** des freien Laufs (`Wylder's Chalice` + Deep, weisser Slot,
K=20/W=40) nach oben beschränkt.

Teurer wird genau eine Stelle: die Vorsortierung. Sie bewertet 309 Relikte,
und zwar jetzt im Kontext des Grundzustands — bei `h=5` also volle Builds
statt einzelner Relikte, rund **77 ms statt 31 ms**. Der zugehörige
Suchanteil ist dann aber nur noch eine Ebene (1 × 40 × 20 × 0,25 ms ≈ 0,2 s),
Gesamtlauf ≈ 0,28 s.

**Der ungünstigste Fall bleibt derselbe: `Wylder's Chalice` + Deep mit
nichts festgehalten, 0,46 s.** Bei `h=0` ist der Entwurf verhaltensgleich
mit dem heutigen — der Grundzustand ist dann der leere Build. Das ist die
Prüfbedingung, unter der die 0,46 s gemessen wurden, und sie bleibt gültig.
Der `performance-tuner` bestätigt in S11 zusätzlich einen Lauf mit `h=5`.

**Nebenertrag, ungeplant und für T-004 wichtig:** „Was passt in **diesen**
Slot?" (die Picker-Frage aus `GOAL.md` F4) ist in diesem Entwurf **kein
neuer Mechanismus**, sondern derselbe Lauf mit `h = Slotzahl − 1`. Kosten
nach obiger Rechnung ≈ 0,28 s im schlechtesten Fall. Der `ui-ux-designer`
kann die beiden Fragen also frei anordnen, ohne dass eine davon Architektur
kostet.

**Konsequenzen:** Leicht wird — inkrementelles Bauen („von hier aus weiter"),
die Picker-Frage, und eine bessere Vorsortierung bei jedem festgehaltenen
Slot. Dauerhaft schwer wird — eine Aussage über den *Wert des Festhaltens*
selbst („dieses Relikt kostet dich 40 AR"); dafür bräuchte es einen zweiten
Lauf ohne Haltezustand und einen Vergleich. Das ist möglich (zwei Läufe,
zwei Cache-Einträge), aber es ist ein Merkmal und keine Nebenwirkung.

**Umkehrbarkeit:** leicht. Ohne Haltezustand ist der Grundzustand der leere
Build und alles läuft wie bisher; die Struktur ist die allgemeinere Form
dessen, was ohnehin gebaut wird.

---

### AD-016 — Der Haltezustand geht in die Kanonisierung, den Cache-Schlüssel und den Generationszähler ein (2026-09-02, Status: aktiv; präzisiert AD-006, AD-007, AD-008)

**Kontext:** AD-008 schlüsselt ein Suchproblem über die **sortierte
Slot-Farbmenge** statt über die Gefäss-Id — geprüft unter der Bedingung, dass
alle Slots gleichberechtigt frei sind; dort ist die Sortierung verlustfrei,
weil ein Slot ausser seiner Farbe keine Eigenschaft hat. **Festhalten führt
eine zweite Eigenschaft ein** und stösst diese Bedingung um:
`[Rot(gehalten), Rot(frei), Blau]` und `[Rot(frei), Rot(frei), Blau]` haben
dieselbe sortierte Farbmenge und sind verschiedene Probleme.

**Optionen:**
- **A — Cache aus, sobald etwas festgehalten ist.** Immer korrekt, nichts zu
  bauen. Konsequenz: ausgerechnet der Fall mit den meisten festgehaltenen
  Slots — die Picker-Frage aus AD-014, sechs Slots nacheinander geöffnet —
  träfe nie, und dort ist der Nutzen des Caches am grössten.
- **B — Gefäss-Id plus Slotindizes in den Schlüssel**, Kanonisierung fallen
  lassen. Konsequenz: korrekt, aber der Trefferanteil aus AD-008 ist weg, und
  mit ihm das Argument, mit dem der `qa-engineer` A3 über 26 bzw. 47
  kanonische Probleme statt 74 Gefässe prüft.
- **C — Kanonische Form erweitern.** Schlüssel ist `(sortierte Farben der
  **freien** Slots, deep, Fingerabdruck des Haltebündels, …)`. Das Haltebündel
  wirkt positionsunabhängig — seine Effekte gehen in eine flache Liste, und es
  belegt Handles —, also genügt ein Fingerabdruck über
  `(handle, relic_id, sorted(effect_ids), sorted(curse_ids))` je gehaltenem
  Relikt, sortiert. Konsequenz: die Rückabbildung in `worker.py` bildet nur
  noch die **freien** Slots zurück, ein paar Zeilen mehr.

**Entscheidung:** C.

**Verbindlich:**
1. `AdvisorRequest` trägt den Haltezustand als eingefrorene Abbildung
   Slotindex → Inhalt (Handle, oder ein Custom-Relikt-Inhalt, oder „leer").
2. Der Cache-Schlüssel aus AD-007 wird um `held_fingerprint` ergänzt. Das ist
   dieselbe Abwägung wie bei den Handles im Nachtrag zu AD-007: ein
   überflüssiger Fehlschlag kostet 0,46 s, ein Treffer über den falschen
   Haltezustand liefert einen Vorschlag, der einen bewusst festgehaltenen
   Slot überschreibt.
3. Der Generationszähler aus AD-006 Punkt 3 wird **auch** erhöht, wenn ein
   Slot festgehalten oder freigegeben wird oder sich der Inhalt eines
   festgehaltenen Slots ändert. Die dort festgeschriebene Kopplung gilt
   unverändert: was den Cache-Schlüssel ändert, macht ein laufendes Ergebnis
   veraltet.
4. Die Rückabbildung permutiert nur freie Slots; festgehaltene behalten ihren
   Platz per Konstruktion.

**Konsequenzen:** Leicht wird — der Picker-Fall bleibt cachefähig, und die
Prüfbarkeit aus AD-008 bleibt erhalten. Dauerhaft schwer wird — nichts von
Belang; der Schlüssel wird um ein Feld länger.

**Umkehrbarkeit:** leicht.

---

### Präzisierung AD-016 — der Cache-Schlüssel ist positionsabhängig, und `held_fingerprint` entfällt (D3, QA-107)

**Der Befund:** `held_fingerprint` ist positionsunabhängig (sortiert, ohne
Slotindex), der als Schlüssel benannte `AdvisorRequest` ist es nicht — er
trägt `problem.held` als geordnetes Tupel. Gemessen: Fingerabdruck gleich,
Request und Hash verschieden. Der Wächter
`test_where_a_relic_is_held_does_not_change_the_fingerprint` sichert damit
eine Eigenschaft, die der Schlüssel nicht hat.

**Entscheidung (D3, Vorgabe des `director`): der Schlüssel ist der
`AdvisorRequest`, positionsabhängig.**

**Meine Entscheidung zur zweiten Hälfte, die der `director` mir überlassen
hat: `held_fingerprint` wird gestrichen — die Funktion, die Property und der
Wächter.** Nicht positionsabhängig gemacht. Drei Gründe, in dieser
Reihenfolge:

1. **Er wäre eine zweite Schlüsselform.** Der Modul-Docstring von
   `advisor/types.py` verbietet genau das, mit ausgeschriebener Begründung:
   *„there is no second key form that could drift from the state it stands
   for."* Heute ist dieser Satz **falsch**, weil der Fingerabdruck da ist.
   Ihn zu streichen macht den Satz wahr; ihn positionsabhängig zu machen
   liesse ihn falsch und fügte eine ableitbare Kopie hinzu, die niemand
   liest.
2. **Er hat keinen Leser und bekommt keinen.** Der Cache schlüsselt auf den
   Request (AD-018: *„Es entsteht keine zweite Schlüsselform"*). Der
   Generationszähler (AD-016.3) braucht nur „ist der Request ein anderer" —
   `SlotProblem` ist eine gefrorene Datenklasse und vergleicht sich selbst.
3. **Er ist eine Falle.** Solange er dasteht und behauptet, zwei
   Haltezustände seien dasselbe, wird ihn irgendwann jemand für etwas
   Schlüsselartiges benutzen — und dann tritt der Fehler ein, gegen den D3
   geschrieben ist: ein Treffer über den falschen Haltezustand überschreibt
   einen bewusst festgehaltenen Slot. Ein positionsabhängiger Fingerabdruck
   wäre keine Falle mehr, aber auch kein Nutzen; er wäre nur eine Kopie, die
   driften kann.

**Rückweg, benannt:** braucht S9 doch eine kanonische Form, wird sie dort
gebaut — **positionsabhängig**, und der Wächter zeigt dann auf den
**Schlüssel**, nicht auf den abgeleiteten Wert. Das sind zwölf Zeilen.

**Verbindlich, ersetzt AD-016 Punkt 2 und 4:**

- **AD-016.2 (neu):** Der Haltezustand ist im Cache-Schlüssel, **weil
  `AdvisorRequest.problem` im Schlüssel ist**. Kein abgeleiteter
  Fingerabdruck, keine zweite Form. Die Abwägung des ursprünglichen Punktes 2
  gilt unverändert: ein überflüssiger Fehlschlag kostet 0,46 s (Gesamtlauf)
  bzw. ~51 ms (Picker), ein Treffer über den falschen Haltezustand kostet
  einen überschriebenen Halt.
- **AD-016.4 (neu):** Es gibt keine Rückabbildung, weil es keine
  Kanonisierung gibt. Festgehaltene Slots behalten ihren Platz, weil im
  Schlüssel steht, wo sie sind.
- **AD-016.1 und AD-016.3 bleiben unverändert.**

**Was das AD-008 kostet, ausdrücklich benannt, weil eine neue Entscheidung
einer alten widerspricht:** AD-008 hat entschieden, ein Suchproblem über die
kanonisierte Slot-Farbmenge zu schlüsseln statt über das Gefäss. Für den
**Cache-Schlüssel** ist diese Entscheidung damit abgelöst — er ist der
Request, und der kennt Gefäss und Slotindizes. Der Trefferanteil, mit dem
AD-008 argumentiert hat (74 Gefässe → 26 bzw. 47 Muster), entfällt.
**Tragbar, weil:** der Hauptweg nach AD-018 erzeugt ohnehin je Slot einen
eigenen Eintrag („freie Slots = genau einer"), die Einträge sind klein, und
die LRU aus AD-007 ist ohnehin in S11 neu zu setzen (Vorschlag 64).
**Nicht abgelöst ist AD-008 als Prüfäquivalenz:** die 26 bzw. 47 kanonischen
Probleme bleiben das Mass, an dem der `qa-engineer` A3 vollständig prüft.
Das war ein zweites, unabhängiges Argument in AD-008 und es hängt nicht am
Cache. Siehe OF-22.

**Warum D3 richtig ist, obwohl seine Begründung zu eng ist** — das gehört in
die Akte, weil die Begründung sonst als Regel weiterlebt: der `director`
begründet die Positionsabhängigkeit damit, dass *„die Slots verschiedene
Farben tragen und die Menge der freien Slots eine andere ist"*. Der Fall, um
den es geht, setzt aber voraus, dass **dasselbe** Relikt in beide Slots
passt, also tragen sie in aller Regel **dieselbe** Farbe; und die Menge der
freien Slots wäre unter einer Kanonisierung nach Farben gerade **gleich**.
Der tragende Grund ist ein anderer und stärker: **die Antwort trägt
Slotindizes** (`SlotChoice.slot_index`, `Candidate.slot_index`,
`SlotPool.slot_index`). Ein Treffer über eine Permutation gäbe eine Antwort
zurück, deren Indizes auf die Slots des *anderen* Problems zeigen; das
geradezuziehen ist genau die Rückabbildung aus AD-016.4, die es nicht gibt
und die niemand gebaut hat. Solange sie fehlt, ist jeder
positionsunabhängige Treffer ein überschriebener Halt. Die Entscheidung ist
damit **richtiger als ihre Begründung** — dieselbe Lage wie bei QA-101.

---

### Nachtrag II 2026-09-02 — Antworten des Nutzers zu OF-12, OF-13, F2 (AD-017, AD-018)

**OF-13 — erledigt, wie vorgeschlagen:** zielfremde Flüche werden genannt,
nicht abgewertet. AD-015 bleibt unverändert in Kraft.
**OF-12 — erledigt, aber anders als vorgeschlagen:** siehe AD-017. Meine
Nicht-tun-Regel 15 („Haltezustand nicht persistieren") galt unter der
Annahme, der Halt sei reiner Sitzungszustand ohne Ort; unter der Antwort des
Nutzers bekommt er einen Ort im Fenster. Nicht auf Platte, nicht in
`QSettings` — insofern gilt die Regel weiter, und sie ist in AD-017.5
präzisiert statt aufgehoben.
**F2 — die Fragestellung ist vom Nutzer verworfen:** siehe AD-018. Die alte
Formulierung „Vorschlag erzeugen, dann anwenden" ist damit **abgelöst**; sie
war unter der Annahme richtig, der Berater sei ein Ereignis auf Knopfdruck.

### AD-017 — Der Haltezustand gehört zum Paar (Nightfarer, Gefäss) und lebt im Fenster, nicht auf Platte (2026-09-02, Status: aktiv; präzisiert AD-014.8 und die Nicht-tun-Regel 15)

**Kontext:** Antwort des Nutzers auf OF-12, wörtlich: *„Die Relikte selbst
verfallen beim Wechsel, wenn man zurueck auf das Gefaess oder den Nightfarer
springt soll es aber noch da sein. Also persistent in dem Gefaess selbst,
sonst flexibel."* Das ist die dritte Option, die weder mein Vorschlag
(„verfällt") noch „wandert mit" war: der Haltezustand ist eine Eigenschaft
des Paars (Held, Gefäss), nicht der Sitzung und nicht des Slots.

**Kräfte:** Die verlangte Wirkung ist „weg und zurück, und es steht wieder
da". Dagegen steht die Geschichte des Schlüsselraums: Zyklus 4 und 5 haben
dreimal Nutzerdaten zerstört, es gilt Schema 3, Schlüssel sind prozentkodiert
und **im Speicher** eindeutig, und jede Migration hält die Nachbedingung
„erst alles lesen, dann schreiben, dann `sync()`, dann Rücklesung, und nur
entfernen, was nachweislich steht". Und der Inhalt ist heikel: ein Halt
verweist auf einen **Handle**, und Handles werden beim Einschmelzen oder
Rechnerwechsel neu vergeben (Nachtrag zu AD-007).

**Optionen:**
- **A — `QSettings`, eigener Schlüsselraum je (Held, Gefäss).** Überlebt
  Neustarts. Konsequenz: ein **neues Schema** mit allem, was daran hängt —
  Prozentkodierung, Eindeutigkeit im Speicher, Migration mit der
  Nachbedingung oben, und eine Auflösungsregel für den Fall, dass das
  gehaltene Relikt beim nächsten Start nicht mehr im Besitz ist. Das ist die
  volle Maschinerie eines Werks für Ansichtszustand.
- **B — Im Fenster, Abbildung `(hero_id, vessel_id, deep) -> Haltezustand`,
  gehalten am `Planner`.** Konsequenz: „weg und zurück" trägt genau so, wie
  der Nutzer es beschrieben hat; kein Schema, keine Migration, kein
  Schlüsselraum, kein Datenverlustrisiko. Beim Programmende ist der Halt weg.
- **C — In den bestehenden Build-Speicher (`chalices.save_build`).**
  Konsequenz: ein Halt ist kein Bestandteil eines Builds; das Format eines
  **Werks** würde für Ansichtszustand geändert. Schlechteste Option.

**Entscheidung: B.** Der Nutzer beschreibt Hin- und Herspringen, also einen
Vorgang **innerhalb** einer Sitzung; B erfüllt das vollständig. Ein Halt ist
Ansichtszustand, kein Werk — und die Regel des Hauses lautet, ihn im Zweifel
zu verwerfen statt zu retten. Ein über den Neustart geretteter Halt wäre
ausserdem genau der Fall, gegen den AD-013 gebaut ist: er zeigt auf ein
Exemplar, das inzwischen eingeschmolzen sein kann.

**Verbindlich:**
1. Die Abbildung lebt am `Planner`, **nicht** im `AdvisorController` — sie
   überdauert einen Beraterlauf, aber nicht das Fenster. Der Berater bekommt
   sie weiterhin nur als eingefrorenen Teil des `AdvisorRequest` (AD-014.8).
2. Schlüssel ist `(hero_id, vessel_id, deep)`. Der Deep-Schalter gehört dazu,
   weil er die Slotmenge ändert.
3. **Gültigkeit wird beim Bauen des Requests geprüft, nicht beim Speichern.**
   Ein Halt, dessen Handle nicht mehr im Besitz ist (Neu-Scan des Saves,
   Einschmelzen), fällt weg und wird in `unknowns` genannt:
   `"A held slot was released: that relic is no longer in your inventory."`
   Stillschweigend weiterrechnen wäre die Variante, die einen falschen
   Vorschlag erzeugt.
4. **Kein `QSettings`-Eintrag, kein Schema, keine Migration.** Damit ist die
   Nachbedingung aus Zyklus 4/5 nicht berührt — nicht weil sie eingehalten
   wird, sondern weil kein persistenter Zustand entsteht.
5. Nicht-tun-Regel 15 gilt in dieser Fassung weiter: nicht auf Platte, nicht
   in `QSettings`. Die Ergänzung ist, dass der Zustand **im Fenster** einen
   definierten Ort bekommt statt gar keinen.

**Bedingung für eine Neubewertung:** Sagt der Nutzer, dass der Halt einen
**Programmneustart** überleben soll (OF-15), ist A richtig — dann aber mit
allem: eigenes Schema, Migrationsnachbedingung, und eine ausgesprochene Regel
für nicht mehr besessene Relikte. Das ist ein eigener Auftrag und nicht Teil
des Beraters.

**Konsequenzen:** Leicht wird — die Funktion, die der Nutzer beschrieben hat,
ohne einen Meter neuen Speicherraum. Dauerhaft schwer wird — nichts, solange
die Bedingung oben gilt.

**Umkehrbarkeit:** leicht.

---

### AD-018 — Der Hauptweg des Beraters ist der Grenzbeitrag je Kandidat im Picker; er ist dieselbe Rechnung wie die Vorsortierung, und der Gesamtlauf bleibt als zweite Frage bestehen (2026-09-02, Status: aktiv in der Sache; **Punkt 4 und die Laufzeittabelle nachgezogen durch AD-028**, 2026-09-08)

**Kontext:** Der Nutzer hat F2 nicht beantwortet, sondern die Fragestellung
verworfen. Wörtlich: *„Ich will im Relikte-Auswahlfenster Vorschlaege haben.
Diese Vorschlaege sollen immer schon die Berechnung machen vom aktuellen
Build aus. … Z.B. macht ein +Staerke weniger viel aus, wenn ich schon sehr
viel Staerke habe, weil der Schaden dann weniger stark steigt."*

**Die Lesart des `director` ist bestätigt, und sie kostet nichts Neues.**
Der Wert eines Kandidaten ist sein Grenzbeitrag
`goal(evaluate(held + Kandidat)) − goal(evaluate(held))`. Das ist **wörtlich
die Vorsortierung aus AD-014.3** — dieselbe Zahl, für denselben Slot, aus
demselben `evaluate`. Was AD-014 als internen Zwischenschritt beschrieb, ist
jetzt die sichtbare Hauptausgabe. Es kommt keine Rechnung dazu; es wird eine
Rechnung, die ohnehin läuft, angezeigt.

Der abnehmende Ertrag, nach dem der Nutzer fragt, fällt tatsächlich von
selbst heraus: die Attributkurven und die Skalierung stecken in
`damage.py`/`model.py`, und eine Differenz zweier Punkte auf einer konkaven
Kurve ist am oberen Ende kleiner. **Er fällt aber nur heraus, wenn die
Steigung dieser Kurve stimmt — siehe das Risiko unten (QA-018).**

**Optionen:**
- **A — Beim alten Entwurf bleiben:** Gesamtlauf auf Knopfdruck, Picker zeigt
  nur eine Markierung (`UI_SPEC` AK-28). Konsequenz: beantwortet die Frage des
  Nutzers nicht; „was bringt *mir* dieses Relikt jetzt" bliebe unbeantwortet.
- **B — Picker-Bewertung als alleiniger Weg**, Gesamtlauf streichen.
  Konsequenz: wer sich Slot für Slot durchklickt, baut **greedy** — und das
  ist AD-003 Option B, gemessen falsch bei Exklusivgruppen und
  `isStrongestEffect`. Der Berater verlöre genau die Fähigkeit, für die es die
  Beam-Suche gibt.
- **C — Beides, aus einer Rechnung:** der Picker beantwortet „was ist für
  **diesen** Slot jetzt das Beste" (Grenzbeitrag, h = Slotzahl − 1), der
  Gesamtlauf „welche **Menge** ist zusammen die beste" (Beam über die freien
  Slots). Konsequenz: zwei Ansichten, ein `evaluate`, eine Bewertungsautorität.

**Entscheidung:** C. Es sind zwei verschiedene Fragen und nicht zwei
Darstellungen derselben Antwort — deshalb bleibt der `Optimize`-Lauf, den der
Nutzer ohnehin weiter will.

**Verbindlich:**
1. **Grenzbeitrag statt Absolutwert im Picker.** Angezeigt wird die Differenz
   zum Grundzustand; gerankt wird danach. Der Grundzustand ist der aktuelle
   Build ohne den geöffneten Slot — dieser Slot ist im Sinne von AD-014 der
   **einzige freie**, alle anderen sind gehalten, gleichgültig ob der Spieler
   sie festgehalten hat oder nicht.
2. **Beide Zielrichtungen kosten fast nichts.** Teuer ist `compute`, nicht
   `goal`. `evaluate` liefert einen `Build`; ihn unter beiden Zielrichtungen
   zu bewerten kostet zwei Funktionsaufrufe über fertige Felder. Ob der Picker
   eine Spalte oder zwei zeigt, ist damit eine Frage des `ui-ux-designer` und
   keine Kostenfrage.
3. **Ein Hinweis, der aus dem Verfahren folgt** (A7, Pflichtzeile, sobald der
   Spieler slotweise wählt): `"Chosen slot by slot. Relics that only pay off
   together are not visible this way — the Optimize run looks for those."`
   Ohne diesen Satz behauptet die Picker-Liste eine Optimalität, die AD-003
   Option B widerlegt hat.
4. **Der Lauf bleibt im Worker.** Auch 50 ms gehören nicht in den
   Hauptthread, wenn sie bei jedem Tastendruck im Filterfeld anfallen können
   (AD-006). Entprellung und Generationszähler gelten unverändert.
   *(Nachtrag 2026-09-08: dieser Punkt ist gebaut worden als sein Gegenteil —
   `relicpicker.SlotAdvice.ranking` rechnet im Hauptthread, mit einem
   Docstring, der es aus der widerlegten `~51 ms`-Zahl begruendet. **AD-028
   zieht Punkt 4 nach und macht ihn verbindlich**; die Entscheidung hier war
   richtig und ist an ihrer Zahl gescheitert, nicht an ihrem Argument.)*

**Laufzeit — die entscheidende Verschiebung, gerechnet aus den Grundzahlen.**
Aus „ein Lauf auf Knopfdruck" wird „ein Lauf bei jeder Interaktion". Die
gute Nachricht steht in den Zahlen: ein Picker-Lauf ist **eine** Ebene, also
eine Bewertung je Kandidat des Slots, nicht `Ebenen × W × K`.

| Fall | Bewertungen | Kosten |
|------|-------------|--------|
| weisser Slot, normal (grösster Pool) | 205 | ~51 ms |
| weisser Slot, deep | 101 | ~25 ms |
| farbiger Slot | 21–55 | ~5–14 ms |
| Grundzustand je Lauf | 1 | ~0,25 ms |
| **Gesamtlauf (`Optimize`), unverändert** | 3 929 | **0,46 s** |

(0,25 ms je Bewertung, weil im Picker fast immer ein voller Build bewertet
wird — der obere Rand der gemessenen Spanne.)

> **Korrektur vom 2026-09-08 (AD-028), ersetzt die Zahlen dieser Tabelle,
> nicht ihre Aussage.** Jede Zahl der Tabelle ist **gerechnet**, nicht
> gemessen: 205 Kandidaten mal 0,25 ms. Gemessen wurde sie am 08.09.2026 zum
> ersten Mal, und beide Faktoren waren daneben — 206 Kandidaten mal
> **1,095 ms**, ergibt **318,1 ms** (Median, n=25, Spanne 289,6–358,9;
> `docs/perf/baselines.md` S11-C, Slot 2, weiss; Umgebung: Ryzen 7 5800H bei
> 1102 von 3201 MHz unter `Legion Quiet Mode`, CPython 3.12.10, Codestand
> `76f1887` — der konservative Fall, nicht der guenstige).
> Damit gilt: `~51 ms` → **318,1 ms** · `~25 ms` (weiss, deep) → nicht neu
> gemessen · farbiger Slot `~5–14 ms` → **32,3–81,7 ms** (S11-C) ·
> Gesamtlauf `0,46 s` → **5,02 s** (S11-A).
> **Was daran haelt:** das Verhaeltnis. Der teuerste Picker-Lauf ist rund ein
> Sechzehntel des Gesamtlaufs, und der unguenstigste Fall des Beraters bleibt
> der Gesamtlauf. **Was faellt:** der Satz „liegt unter der 250-ms-Schwelle
> aus AK-09". 318,1 ms liegen **darueber**, und der naechste Absatz — „Auch
> 50 ms gehoeren nicht in den Hauptthread" — ist damit nicht mehr eine
> Vorsichtsregel, sondern der Befund QA-208.

Der teuerste Picker-Lauf ist damit rund **ein Neuntel** des Gesamtlaufs und
liegt unter der 250-ms-Schwelle aus `UI_SPEC` AK-09, ab der überhaupt ein
Wartezustand gezeigt wird. Der ungünstigste Fall des Beraters bleibt
unverändert der Gesamtlauf mit nichts festgehalten, 0,46 s.

Was sich verschiebt, ist nicht die Spitze, sondern die **Häufigkeit**: der
Berater rechnet jetzt beim Öffnen des Pickers und nach jeder Änderung, die
den Grundzustand bewegt (Level, Waffe, ein anderer Slot, ein deklarierter
konditionaler Effekt). Deshalb sind die beiden bereits beschlossenen
Schutzmechanismen jetzt tragend statt vorsorglich: die Entprellung (AD-006.5)
und der Generationszähler (AD-006.3). Neu ist nur die Empfehlung, die
Entprellung für den Picker-Pfad **kürzer** zu setzen als für den Gesamtlauf
(Vorschlag 100 ms gegen 250 ms) — 50 ms Rechnung hinter 250 ms Wartezeit
fühlt sich träger an, als sie ist. Der `performance-tuner` setzt beide Werte
in S11.

**Zwischenspeicher und Generation (präzisiert AD-016).** Es entsteht **keine
zweite Schlüsselform.** Ein Picker-Lauf ist in der Kanonisierung aus AD-016
der Fall „freie Slots = genau einer": Schlüssel ist
`(Farbe des freien Slots, deep, held_fingerprint, goal_id, weighting_id,
inventory, snapshot, weapon, declared, hero, level)`. Zwei Folgen, beide
gewollt: das Durchklicken durch sechs Slots erzeugt sechs kleine Einträge
statt eines grossen, und ein zurückgeklickter Slot antwortet aus dem Cache.
Weil die Einträge nun kleiner und zahlreicher sind, ist die LRU-Grösse aus
AD-007 (Vorschlag 32) neu zu setzen — Aufgabe des `performance-tuner` in S11,
Vorschlag 64.

**Konsequenzen:** Leicht wird — die Frage, die der Nutzer tatsächlich stellt,
und zwar ohne neue Rechnung; ausserdem ist der Picker-Wert *dieselbe* Zahl,
nach der der Gesamtlauf vorsortiert, die beiden Ansichten können sich also
nicht widersprechen. Dauerhaft schwer wird — der Berater ist jetzt an der
Interaktion beteiligt statt daneben; jede künftige Verlangsamung von
`model.compute()` wird sofort spürbar, nicht erst auf Knopfdruck. Das ist der
Preis dieser Entscheidung und gehört als Messpunkt in S11.

**Umkehrbarkeit:** mittel. Die Rechnung ist dieselbe; rückgängig wäre nur die
Anzeige. Was nicht leicht zurückgeht, ist die Erwartung des Nutzers, dass
jede Auswahl sofort bewertet ist.

---

---

## Themenbereich C — Zielrichtungen, Vorbehalte, Fluechte

*Was eine Zielrichtung ist, und was das Programm sagt, wo die Spieldateien
nichts hergeben. Das ist der Bereich, an dem A7 haengt: keine erfundene Zahl,
und der Vorbehalt gehoert ins Ergebnis, nicht in eine Fussnote.*

### Nachtrag VI 2026-09-05 — Zwei Klassen von Vorbehalten, die Ergebnisform des Pickers, und vier Präzisierungen (AD-025)

Anlass: der Erstdurchlauf des `qa-engineer` über den Rechenkern (T-041) hat
zwei Entwurfslücken gefunden, die er ausdrücklich nicht selbst geschlossen
hat — QA-102 (der `SlotPool` trägt keine A7-Zeile der Zielrichtungen) und
QA-107 (`held_fingerprint` und der als Schlüssel benannte `AdvisorRequest`
behaupten Verschiedenes). Der `director` hat in T-047 vier Entscheidungen
getroffen (D1 bis D4); dieser Nachtrag arbeitet sie aus.

**Was dieser Nachtrag nicht anfasst:** keine Zahl, keine Zielfunktion, kein
Schwellenwert. D1 bis D4 betreffen ausschliesslich **Form und Text**. Der
Rechenkern rechnet nach diesem Nachtrag dasselbe wie davor; er sagt mehr
darüber.

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
`unknowns` enthält *immer mindestens* — **ab AD-025 ist das die Liste von
`Goal.scope`, nicht die von `GoalScore.unknowns`**:
- „Attack rating has not been verified against an in-game number." (README
  Known limits) — **historisch. Seit QA-095 (2256 Vergleiche) ist der Satz
  falsch; an seiner Stelle steht der Geltungsbereich der Übereinstimmung
  (`advisor/goals.py`, `UI_SPEC` Nachtrag zu QA-116). Hier stehengelassen
  als Beleg dafür, wie die Zeile einmal lautete — nicht als geltende
  Vorgabe (QA-116).**
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

### Präzisierung AD-004 — die `unknowns` einer Zielrichtung zerfallen, und die konditionale Zeile bekommt einen Ort (D2)

AD-004 bleibt in der Sache unverändert: eine Zielrichtung ist eine Zahl mit
erklärtem Geltungsbereich, als Registry reiner Funktionen. Präzisiert wird,
**wo** der Geltungsbereich steht.

1. **Die Liste „`unknowns` enthält *immer mindestens* …" in AD-004 ist ab
   jetzt die Liste von `Goal.scope`**, nicht die von `GoalScore.unknowns`.
   „Immer mindestens" war schon in AD-004 die Beschreibung eines
   Verfahrenssatzes; das Feld war nur das falsche.
2. **Der dort zitierte Wortlaut ist historisch, nicht geltend.** Die Zeile
   *„Attack rating has not been verified against an in-game number."*
   (ARCHITECTURE.md in AD-004, von QA-116 gemeldet) ist seit QA-095 **falsch**
   — 2256 Vergleiche haben die Übereinstimmung belegt. Was heute in
   `goals.py` steht, ist der **Geltungsbereich** dieser Übereinstimmung. Der
   verbindliche Wortlaut ist keiner der beiden alten: `UI_SPEC`, Nachtrag zu
   QA-116 (T-052, 2026-09-05) entscheidet, dass die Anzeige die Sätze aus dem
   Programm liest statt einen eigenen zu führen. AD-004s Zitat steht ab jetzt
   als Beleg dafür, wie die Zeile einmal lautete.
3. **Die gemeinsame konditionale Zeile ist übersehen, nicht verschoben**
   (D2). *„N of your relics carry effects that only apply under a condition.
   They were not counted."* existiert nirgends im Paket (zwei unabhängige
   Volltextsuchen, T-041). Sie trägt eine Anzahl, ist also ein **Laufbefund**,
   und sie wird gebaut.
4. **Wo sie entsteht: in `candidates.pool()`, gezählt über die Kandidaten
   *dieses* Pools**, und sie geht nach `SlotPool.unknowns`. Begründung: die
   Zeile existiert nach AD-004s eigener Begründung dafür, dass *„ein Spieler
   ein starkes situatives Relikt ungenutzt sähe und den Berater für kaputt
   hielte"* — dieses Bild entsteht in der Kandidatenliste des Pickers, und
   nur dort kann der Spieler die Zahl gegen das prüfen, was auf dem Schirm
   steht. Eine Zählung über den ganzen Bestand nennte Relikte mit, die
   farblich gar nicht in diesen Slot passen.
5. **Woraus gezählt wird, damit die Zahl nicht widerspricht, was gerechnet
   wurde:** aus dem `Build`, den der Pool für den Kandidaten ohnehin bildet —
   `Build.situational` mit `live == False`. Das ist dieselbe Disziplin wie
   AD-015 bei den Flüchen (*„aus `Build.sources` statt aus den
   Relikt-Definitionen, damit ein Fluch, den die Rechnung nicht angewandt
   hat, nicht so gezeigt wird, als hätte sie es"*). **Ausdrücklich nicht**
   erlaubt ist eine zweite, in `candidates.py` selbst geschriebene Ableitung
   des Waffentyps für `model.is_conditional` — `model.compute` leitet ihn
   heute in `model.py` aus `weapons_held`/`weapon` ab, und eine zweite
   Ableitung ist eine zweite Meinung darüber, was gezählt wurde.
6. **Der Geltungsbereich dieser Zeile, ausgesprochen:** `Build.situational`
   führt nur Bedingungen, die der Spieler erklären kann — **nicht** einen
   Effekt, der an einer nicht getragenen Waffenklasse hängt. Dieser Fall ist
   QA-104 und bekommt seine eigene Zeile; er wird von der konditionalen Zeile
   nicht mitgezählt und darf es nicht, sonst nennt eine Zahl zwei
   verschiedene Sachverhalte.
7. **Ein Kriterium, zwei Darstellungen.** Derselbe Sachverhalt erscheint auf
   dem Ergebnisweg als `AdvisorResult.not_counted` (Effektnamen, S7/S9) und
   auf dem Pickerweg als Zeile mit einer Anzahl von **Relikten**. Die
   Nenner sind verschieden und das ist gewollt; das **Kriterium** ist
   dasselbe und darf nur einmal geschrieben werden.
8. **Der Wortlaut ist nicht meiner.** AD-004 sagt „N of your relics", gezählt
   wird dieser Pool. Der `ui-ux-designer` entscheidet den Satz (OF-20); bis
   dahin baut der `developer` ihn mit dem gezählten Bestand im Text, nicht
   mit „your relics".

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

### Präzisierung AD-010 — was „Pflichtfeld im Ergebnis" nach D1 heisst, und warum AK-50 nicht widerspricht

AD-010 bleibt gültig, mit einer geschärften Reichweite.

1. **AD-010 hat eine statische Liste *aller denkbaren* Lücken verworfen** —
   einen Text, der immer dasselbe sagt, gleichgültig ob die Lücke im Lauf
   überhaupt eingetreten ist. Es hat **nicht** einen festen Satz über eine
   Eigenschaft des Verfahrens verworfen. Die Bedingung, unter der Option A
   geprüft wurde (*„welche Lücken gelten, hängt vom konkreten Lauf ab"*),
   trifft auf einen Verfahrenssatz nicht zu. `UI_SPEC` AK-50 ist damit nicht
   die von AD-010 verworfene Option A.
2. **Pflicht im Ergebnis ist der Laufbefund**, und zwar vollständig: was in
   diesem Lauf weggefallen ist, fährt mit und erscheint dort, wo es entstand.
   `unknowns` **darf leer sein**; leer heisst „in diesem Lauf ist nichts
   weggefallen" und ist eine Aussage, keine Auslassung.
3. **Pflicht in der Registry ist der Verfahrenssatz**, und dort gilt „nie
   leer": eine Zielrichtung ohne `scope` ist keine. Die Zusage aus AD-010,
   dass immer etwas dasteht, wandert damit von `GoalScore.unknowns` auf
   `Goal.scope` — sie wird nicht schwächer, sie wird prüfbar ohne
   Datensatz (QA-106).
4. **Die verbindliche Inhaltsliste jedes `AdvisorResult`** (AD-010) bleibt
   Wort für Wort bestehen und ist nach dieser AD durchweg Laufbefund:
   `unknowns`, `weights_note`, `not_counted`, `curses`, `data_note`,
   `budget_note`. Das ist kein Zufall — AD-010 hat die Klasse schon richtig
   getroffen, ohne sie zu benennen.
5. **Nutzersprache bleibt verbindlich:** „Best found", „Top suggestions",
   „Not counted", „Not verified" — nie „Optimal", „Best possible",
   „Guaranteed". Für beide Klassen.

---

### AD-025 — Ein Vorbehalt gehört entweder der Registry oder dem Ergebnis, und die Frage „kann der Satz geschrieben werden, bevor der Lauf bekannt ist?" entscheidet, welchem (2026-09-05, Status: aktiv; präzisiert AD-004 und AD-010, Vorbedingung für S8/S9/S10)

**Kontext:** A7 verlangt, dass das Programm sagt, wo die Spieldateien keine
Antwort geben. AD-010 hat daraus ein **Pflichtfeld im Ergebnis** gemacht, mit
der Begründung: *„welche Lücken gelten, hängt vom konkreten Lauf ab"*.
`UI_SPEC` AK-50 legt daneben **einen festen Satz ausserhalb der Karten** fest.
Der `qa-engineer` hat beides nebeneinander gefunden und als Spec-Konflikt
gemeldet (QA-102), weil beide Lesarten vertretbar sind und einander
auszuschliessen scheinen.

Sie schliessen einander nicht aus. Der Massstab ist AD-010s **eigene**
Begründung, und sie ist eine Bedingung, keine Behauptung: *„welche Lücken
gelten, hängt vom konkreten Lauf ab"*. Wo diese Bedingung zutrifft, gilt
AD-010. Wo sie **nicht** zutrifft — wo ein Satz für jeden Lauf derselbe ist —
war sie nie geprüft, und AD-010 sagt dort nichts. Genau dort steht AK-50.

Die Kraft, die aufzulösen ist: **eine Zahl braucht ihren Geltungsbereich,
und ein Bildschirm, der denselben Geltungsbereich sechsmal wiederholt,
verliert ihn.** Der eine Fehler ist Schweigen, der andere ist Rauschen; A7
verbietet den ersten, und der dritte Blick des Nutzers bestraft den zweiten.

**Der Massstab (D1, Vorgabe des `director`):**

> **Kann der Satz geschrieben werden, bevor der Lauf bekannt ist?**

**Operational, damit er entscheidbar ist:** ein Satz ist ein
**Verfahrenssatz**, wenn sowohl sein Wortlaut **als auch die Frage, ob er
gilt**, allein aus der Registry folgen — aus `Goal` und `Weighting`, ohne
Bestand, ohne `SlotProblem`, ohne `Build`. Er ist ein **Laufbefund**, wenn
eines von beidem den Lauf braucht: eine Anzahl, ein benanntes Relikt, ein
bestimmter Effekt, ein bestimmter Slot — **oder auch nur die Entscheidung, ob
der Satz überhaupt dasteht**.

Der Zusatz „ob er gilt" ist nicht Zierrat; ohne ihn geht der Massstab an
`_NO_ARMAMENT` schief. *„No armament selected — ranked on attack multipliers
only, without weapon scaling."* lässt sich wörtlich vor jedem Lauf
aufschreiben und wäre danach ein Verfahrenssatz — und stünde dann auch da,
wenn eine Waffe gewählt ist. Das ist der Fall, an dem sich die Regel prüfen
lässt, und er entscheidet ihre Fassung.

**Die zwei Klassen, benannt nach ihrer Antwort auf die Frage:**

| | **Verfahrenssatz** | **Laufbefund** |
|---|---|---|
| Antwort | ja, vor dem Lauf schreibbar | nein, er entsteht im Lauf |
| Aussage über | das Verfahren | diesen Bestand, diesen Slot, diesen Lauf |
| Beispiele | Geltungsbereich der Angriffsrechnung · „alle acht Schadensarten gleich gewichtet" · die Formel für effektives HP · „Zauberschaden steht nicht in den Daten" | „N of your relics carry effects that only apply under a condition." · „3 copies had no readable handle." · „No armament selected …" · der weggefallene Halt |
| Wohnt in | der **Registry**: `Goal.scope`, `Weighting.note` | dem **Ergebnis**: `GoalScore.unknowns`, `Baseline.unknowns`, `SlotPool.unknowns`, `AdvisorResult.*` |
| Erscheint | **einmal je Bildschirm**, ausserhalb der Karten (AK-50) | **dort, wo er entsteht** — im Pool beim Pool, im Ergebnis beim Ergebnis (AD-010) |
| Leer erlaubt | nein — eine Zielrichtung ohne Geltungsbereich ist keine | ja — „in diesem Lauf ist nichts weggefallen" ist eine Aussage |

**Optionen:**

- **A — Im Bestand bleiben.** `GoalScore.unknowns` trägt beide Klassen in
  einem Feld, `SlotPool` trägt nichts davon weiter. Konsequenz: QA-102 bleibt
  offen; auf dem Weg, den der Nutzer nach AD-018 zu 100 % benutzt, trägt das
  Ergebnis keine A7-Zeile. Ein starkes situatives Relikt steht mit `0,00` da
  und nichts sagt warum — das Bild, das AD-004 als Grund für die Zeile nennt.
  Und die Oberfläche muss raten, welchen der fünf Sätze sie einmal und
  welchen sie je Lauf zeichnet.
- **B — Ein Feld, eine Marke.** Beide Klassen bleiben in `unknowns`, jeder
  Satz bekommt ein Kennzeichen: `tuple[tuple[str, bool], ...]`. Konsequenz:
  hashbar wäre es, und die Oberfläche könnte trennen. Aber die Klasse wäre
  eine Eigenschaft des **Strings**, die jeder Schreiber neu und richtig
  setzen muss — und die Registry dürfte weiterhin laufabhängige Sätze führen,
  die Zielfunktion weiterhin statische. Der Fehler bliebe möglich, er wäre
  nur benannt.
- **C — Trennung nach Ort.** Der Verfahrenssatz zieht auf die Registry
  (`Goal.scope`), der Laufbefund bleibt im Ergebnis. Konsequenz: die Klasse
  ist keine Eigenschaft des Satzes mehr, sondern seines Wohnorts. Ein
  Verfahrenssatz **kann** den Lauf nicht sehen, weil die Registry keinen hat;
  ein Laufbefund **kann** ohne Lauf nicht entstehen. Preis:
  `GoalScore.unknowns` darf jetzt leer sein — die Zusage „es steht immer
  etwas da" wandert von dort auf `Goal.scope` —, und `UI_SPEC` AK-63 nennt
  eine Quelle, wo es ab jetzt zwei gibt.

**Entscheidung: C.** Der Grund ist derselbe, mit dem AD-010 seinerzeit den
statischen Warntext verworfen hat: *ein Kriterium, dessen Erfüllung von der
Sorgfalt beim Schreiben abhängt, ist nicht erfüllt.* B verlagert die Sorgfalt
nur von der Oberfläche auf den Autor des Satzes. C nimmt sie beiden ab.

**Verbindlich:**

1. **`Goal` bekommt ein Feld `scope: tuple[str, ...]`** — die
   Verfahrenssätze dieser Zielrichtung, nicht leer. Es ist **ohne Datensatz
   lesbar**: `GOALS["max_damage"].scope` braucht keine Spielinstallation,
   keinen `Build` und keinen Bestand. Das ist die Eigenschaft, die die Klasse
   definiert, und sie ist damit auch auf einem Runner ohne Spiel prüfbar
   (QA-106).
2. **`GoalScore.unknowns` trägt ab jetzt nur noch Laufbefunde** und darf leer
   sein. Es behält seinen Namen: AD-010 hat ihn geprägt, drei weitere Typen
   führen ihn, und `UI_SPEC` AK-63 nennt ihn. Eine Umbenennung wäre
   Vereinheitlichung ohne Ertrag.
3. **`weights_note` ist ein Laufbefund** und bleibt, wo es ist. Der
   *Wortlaut* steht in der Registry (`Weighting.note`), aber **welcher** der
   möglichen Wortlaute gilt, sagt erst der Lauf — für `max_damage` hängt es
   daran, ob eine Referenzwaffe gewählt ist. Es fährt deshalb im Ergebnis
   mit.
4. **Ein Satz steht in genau einer der beiden Klassen.** Derselbe String in
   `Goal.scope` und in einem `unknowns` ist ein Fehler, kein Nachdruck: die
   Oberfläche zeichnet ihn dann zweimal, an zwei Orten, mit zwei
   Begründungen.
5. **Die Zuordnung eines Satzes ist eine Entwurfsentscheidung, keine
   Formulierungsfrage.** Wer einen neuen Vorbehalt schreibt, beantwortet
   zuerst die Frage oben und wählt danach den Ort. Wer einen bestehenden Satz
   von einer Klasse in die andere verschiebt, braucht eine AD.
6. **Der Wortlaut selbst gehört dem `ui-ux-designer`** (`UI_SPEC` AK-63,
   T-052). Diese AD legt fest, **welcher Klasse** ein Satz angehört und **wo**
   er wohnt, nicht wie er heisst.

**Anwendung auf den heutigen Bestand** (`nrplanner/advisor/goals.py`, Stand
2026-09-05, nach T-045 und T-046):

| Satz | Klasse | Ab jetzt in |
|---|---|---|
| `_ATTACK_RATING_UNKNOWNS`, alle vier | Verfahrenssatz | `MAX_DAMAGE.scope` |
| `_DAMAGE_TAKEN_UNKNOWNS`, alle vier | Verfahrenssatz | `MIN_DAMAGE_TAKEN.scope` |
| `_NO_ARMAMENT` | Laufbefund (gilt nur ohne Referenzwaffe) | `GoalScore.unknowns` |
| `_NO_ARMAMENT_NOTE` | Laufbefund (dieselbe Bedingung) | `GoalScore.weights_note` |
| `ctx.weighting.note` | Laufbefund der Auswahl, Verfahrenssatz dem Wortlaut nach | `GoalScore.weights_note` |
| `_without_a_handle_line(n)` | Laufbefund (trägt eine Anzahl) | `SlotPool.unknowns` (Bestand) |
| die konditionale Zeile (D2, neu) | Laufbefund (trägt eine Anzahl) | `SlotPool.unknowns` |
| QA-113s Blindstelle, sobald sie benannt wird | **beides, getrennt**: „flache `*AttackPower`-Felder gehen in diese Zahl nicht ein" ist ein Verfahrenssatz; „N deiner Relikte tragen so einen Effekt" ist ein Laufbefund | `Goal.scope` bzw. `SlotPool.unknowns` |
| QA-104s klassengebundener Buff ohne Waffe | Laufbefund (gilt nur ohne Referenzwaffe) | `GoalScore.unknowns` |

Die letzten beiden Zeilen sind **keine Beauftragung** — QA-113s Einbauhöhe
hängt an einer Messung des Nutzers (F-F), QA-104 ist ein eigener Befund. Sie
stehen hier, weil die Regel sonst nur an den Fällen geprüft wäre, aus denen
sie entstanden ist.

**Konsequenzen:** Leicht wird — die Oberfläche muss nicht mehr raten: was in
der Registry steht, zeichnet sie einmal; was im Ergebnis ankommt, zeichnet
sie dort, wo das Ergebnis steht. Eine dritte Zielrichtung bringt ihren
Geltungsbereich mit, ohne dass irgendwo eine Liste nachgezogen wird. Und A7
ist auf dem Hauptweg zum ersten Mal prüfbar statt behauptet.
Dauerhaft schwer wird — ein Vorbehalt, der *fast* für jeden Lauf gilt, muss
sich für eine der beiden Klassen entscheiden; es gibt keine dritte. Wer
findet, dass er in keine passt, hat einen Entwurfsbefund, keinen Sonderfall.

**Umkehrbarkeit:** leicht für die Form, schwer für die Zusage. `Goal.scope`
wieder in die Zielfunktion zu ziehen ist eine Zeile je Zielrichtung. Die
Zusage an den Nutzer, dass jede Zahl ihren Geltungsbereich nennt,
zurückzunehmen, ist es nicht — dieselbe Asymmetrie, die AD-010 schon nennt.

---

### Die Ergebnisform: was `SlotPool` bekommt und was ausdrücklich nicht

**Das Problem, gemessen (QA-102):** `pool()` ruft `goal.score(base_build,
ctx)` einmal je Zielrichtung und nimmt davon **nur `.value`**. `unknowns`,
`weights_note`, `unit` und `display` fallen an der Poolgrenze weg. Der
`SlotPool` ist der Hauptweg (AD-018) — was hier wegfällt, sieht der Nutzer
nie.

**Entscheidung: `Baseline` wird die Zeile, die dieser Pool über eine
Zielrichtung weiss** — nicht ein zweiter, danebenstehender Datensatz.

```python
# advisor/types.py  (illustrierend, kein Anwendungscode)

@dataclass(frozen=True)
class Goal:
    id: str
    label: str
    blurb: str
    scope: tuple[str, ...]              # NEU: die Verfahrenssaetze (AD-025.1)
    score: Callable[[model.Build, "GoalContext"], "GoalScore"]

@dataclass(frozen=True)
class GoalScore:
    value: float
    display: str
    unit: str
    unknowns: tuple[str, ...] = ()      # nur noch Laufbefunde, darf leer sein
    weights_note: str = ""

@dataclass(frozen=True)
class Baseline:
    """Was dieser Pool ueber eine Zielrichtung weiss -- eine Zeile je Ziel."""
    goal_id: str
    value: float                        # Bestand: der Bezugspunkt
    unit: str = ""                      # NEU: laufabhaengig seit T-046
    unknowns: tuple[str, ...] = ()      # NEU: die Laufbefunde dieses Ziels
    weights_note: str = ""              # NEU

# SlotPool unveraendert in der Form; neu ist nur, was `unknowns` enthaelt:
#   - handle-lose Kopien              (Bestand)
#   - die konditionale Zeile aus D2   (neu, siehe Praezisierung AD-004)
```

**Warum `Baseline` und nicht ein neuer Typ:** die drei neuen Felder sind
**der Rest derselben Antwort**, aus der `value` schon kommt. Ein zweiter
per-Ziel-Datensatz neben `Baseline` hiesse zwei Nachschlagefunktionen, zwei
Orte, an denen eine `goal_id` fehlen kann, und zwei Datensätze, die
auseinanderlaufen können. `baseline_for(pool, goal_id) -> float` bleibt
unverändert gültig und liest weiterhin `.value`.

**Warum nicht `scores: tuple[GoalScore, ...]`** (der Vorschlag des
`qa-engineer`, ausdrücklich als tragfähig bezeichnet): `GoalScore.value`
wäre dann eine **zweite Darstellung** von `Baseline.value` — dieselbe Zahl,
zweimal im selben Objekt. Das ist die Fehlerklasse, die dieses Projekt schon
zweimal getroffen hat (QA-082, QA-087) und gegen die AD-024 ausdrücklich
entschieden hat. Und `GoalScore` trägt kein `goal_id`, also wäre die
Zuordnung entweder eine Parallelordnung zweier Tupel oder ein zusätzliches
Feld auf `GoalScore`, das die Zielfunktion selbst setzen müsste — womit die
Registry-Id an zwei Stellen stünde.

**Hashbar bleibt es** (QA-066, AD-016, Modul-Docstring `advisor/types.py`):
`str`, `float`, `str`, `tuple[str, ...]`, `str` — kein Mapping, keine Liste,
kein Feld, das ein Mapping enthält. `SlotPool` bleibt damit hashbar, ohne
dass ein Test seine Begründung ändern muss.

**Was ausdrücklich NICHT über die Poolgrenze fährt:**

1. **`GoalScore.display`.** Es ist die formatierte **Absolutzahl des
   Grundzustands**. Der Picker zeigt die **Differenz** (AD-018.1,
   `UI_SPEC` §3.3). Eine formatierte Absolutzahl im Pool ist eine Einladung,
   die falsche Zahl auf die Karte zu schreiben, und sie wäre die zweite
   Darstellung von `value`.
   *Wieder interessant, wenn:* eine Ansicht den Absolutwert des
   Grundzustands zeigen soll. Dann aber mit eigener AD — zwei Zahlen auf
   einem Schirm stellen die Frage „welche ist die Rankinggrösse" neu, und
   AD-014.6 hat darauf schon einmal geantwortet.
2. **Der `Build`, der `GoalContext`, der Datensatz.** Nicht hashbar, und die
   beiden Ausnahmetypen sind abschliessend aufgezählt (Modul-Docstring).
3. **Die Verfahrenssätze.** Sie stehen in der Registry und werden von dort
   gelesen. Sechs Pools eines Deep-Gefässes trügen sonst sechsmal dieselben
   vier Sätze — genau die Wiederholung, gegen die AK-50 geschrieben ist.
4. **Kein `not_counted`-Feld auf `SlotPool`.** Der Ergebnisweg hat
   `AdvisorResult.not_counted` **mit Namen**; der Pool trägt die **Zeile mit
   der Anzahl**. Beide entstehen aus einem Kriterium (siehe Präzisierung
   AD-004), aber der Pool zeigt, was der Spieler auf dem Schirm nachzählen
   kann.

**Eine benannte Lücke, die dieser Entwurf nicht schliesst:** der Picker zeigt
`+12.4 AR` und `−18` — eine Differenz, je Zielrichtung anders formatiert.
`GoalScore.display` formatiert den **Absolutwert** und taugt dafür nicht;
`unit` allein reicht nicht, weil die Nachkommastellen je Zielrichtung
verschieden sind. **Heute existiert für die Formatierung einer Differenz
nirgends eine Regel.** Sie gehört zu S8/S10 und zum `ui-ux-designer`, nicht
in T-048 — aber wer QA-102 liest („`display` fällt weg"), wird sie einbauen
wollen, und das wäre der falsche Ort. Siehe OF-21.

---

### AD-015 — Flüche gehen als gewöhnliche Effekte in dieselbe `compute()`-Bewertung; ausgewiesen werden sie aus `Build.sources`, nicht aus einer zweiten Rechnung (2026-09-02, Status: aktiv)

**Kontext:** `GOAL.md` F3, entschieden vom Nutzer am 2026-09-02: Flüche
werden mitbewertet und im Ergebnis ausgewiesen. Begründung: „Falls meine
negativen auf Relikten meine Benefits vernichten, muss ich das wissen."

Am Bestand geprüft: `Planner.current_build()` (`app.py:3300 f.`) reicht
`self.selected_effects() + self.weapon_effects() + curses` in **einen**
`model.compute`-Aufruf; der Kommentar dort nennt den Grund („Leaving them out
meant a curse ... made the sheet quietly wrong for every Deep of Night
build"). Flüche sind für die Rechnung also längst gewöhnliche Effekte. Für
den Berater ist F3 damit **keine neue Mechanik**, sondern die Auflage, den
bestehenden Weg nicht zu verlassen.

**Optionen:**
- **A — Flüche nur anzeigen, nicht bewerten.** Konsequenz: die Rangliste
  widerspricht dem Statblatt desselben Programms — genau der Fehler aus
  QA-001, wegen dessen es den `compute`-Wächter gibt. Und F3 wäre verletzt.
- **B — Flüche als gewöhnliche Effekte in dieselbe Effektliste**, wie
  `current_build()` es tut. Konsequenz: das Ranking stimmt mit dem Statblatt
  überein, ohne dass jemand darauf achten muss; ein Fluch, der den Nutzen
  auffrisst, senkt die Rangzahl von selbst.
- **C — Zusätzlicher Fluch-Malus auf die Zielpunktzahl.** Konsequenz: eine
  zweite Bewertungsautorität mit eigenen Gewichten — gegen AD-002 — und die
  Gewichte stünden nirgends in den Spieldateien, also gegen A7.

**Entscheidung:** B. C ist die Versuchung, weil ein Malus den blinden Fleck
unten scheinbar schliesst; er schlösse ihn mit erfundenen Zahlen.

**Ausweisen, ohne zweite Rechnung:** `Build.sources` ist bereits
`field -> [(Effektname, Einzelwert)]` und enthält die Fluchbeiträge mit
negativem Vorzeichen, weil sie durch dieselbe Rechnung gelaufen sind.
`explain.py` liest daraus:
- je vorgeschlagenem Relikt die Flüche mit Namen **und** dem Feld, das sie
  bewegt haben, samt Betrag (`UI_SPEC` 3.2 und AK-19 verlangen die Nennung
  vor dem Anwenden; die Zahl kommt jetzt aus derselben Quelle wie die
  Begründungszeile),
- `AdvisorResult.curses` bleibt wie in AD-010 gefordert, wird aber
  ausdrücklich aus `sources` gefüllt statt aus der Relikt-Definition — sonst
  stünde ein Fluch da, den die Rechnung gar nicht angewandt hat (etwa ein
  konditionaler).

**Der blinde Fleck, ausdrücklich benannt (A7).** Bewertet wird alles,
**gerankt** wird eine Zahl. Ein Fluch, der ein Feld bewegt, das die gewählte
Zielrichtung nicht misst — etwa `-HP` unter „Maximise damage" —, ist im Build
korrekt verrechnet, ändert die Rangzahl aber nicht. Dass er im Vorschlagsblock
steht, ist damit nicht Kosmetik, sondern der einzige Ort, an dem er sichtbar
wird. Pflichtzeile in `unknowns`, sobald ein vorgeschlagenes Relikt einen
Fluch trägt, dessen Felder ausserhalb der Zielgrösse liegen:
`"A curse on <relic> changes <field>, which this goal does not rank."`

Ein Schalter „ohne Flüche" (`UI_SPEC` F3, Alternative) ist damit **nicht**
entschieden worden und auch nicht nötig: er wäre ein Kandidatenfilter in
`candidates.py`, eine Zeile, und berührt weder Suche noch Bewertung. Ob er
kommt, entscheidet der `ui-ux-designer` mit dem Nutzer.

**Konsequenzen:** Leicht wird — F3 kostet im Kern null Struktur, und jede
künftige Korrektur an der Fluchbehandlung in `model.py` erreicht den Berater
ohne Zutun. Dauerhaft schwer wird — eine *Abwägung* zwischen Nutzen und Fluch
über Dimensionen hinweg; die braucht Gewichte, die es nicht gibt (siehe
OF-13).

**Umkehrbarkeit:** leicht.

---

### Korrekturnotiz zu AD-015 (2026-09-07; Herkunft: Entscheidung des `director` vom 06.09.2026, umgesetzt in `explain.py` seit T-081)

**Ersetzt** in AD-015 den Absatz „*Pflichtzeile in `unknowns`, sobald ein
vorgeschlagenes Relikt einen Fluch trägt, dessen Felder ausserhalb der
Zielgrösse liegen:* `"A curse on <relic> changes <field>, which this goal
does not rank."`".

**Der ursprüngliche Wortlaut bleibt dort stehen und wird nicht gelöscht** —
er ist der Beleg dafür, wie die Zusage einmal lautete.

**Neu verbindlich:** Die AD-015-Pflichtzeile **wandert aus `unknowns` in die
Slotgruppe** und wird **mit der Zahlzeile desselben Fluchs verschmolzen** —
aus zwei Zeilen wird eine:

```
✦ {curse name}: {figure label} {amount} — this figure does not count it.
```

**Begründung:** Beide Hälften sagten dieselbe Sache an zwei Orten — die Zahl
in `reasons`/`curses`, die Einordnung in `unknowns`. Ein Spieler soll einen
Fluch **einmal** lesen, unter dem Relikt, das ihn trägt. Der Reliktname im
alten Wortlaut war ausserdem überflüssig, weil die Slotgruppe ihn in ihrer
Überschrift führt.

**Unberührt bleibt alles Tragende von AD-015:** Flüche gehen als gewöhnliche
Effekte in dieselbe `compute()`-Bewertung; ausgewiesen werden sie aus
`Build.sources`; die Frage „fühlt die Rankingzahl diesen Fluch" wird **je
Fluch** gestellt und an der Rankingzahl beantwortet; kein Satz sagt, ein
Relikt sei **wegen** seines Fluchs schlechter platziert (OF-13, AD-023).
Geändert hat sich der **Ort** und die **Form** der Zeile, nicht die Zusage.

**Stand im Code (`fd9f2bc`, geprüft):** `explain.unknowns` trägt die Zeile
nicht mehr und begründet das in seinem eigenen Docstring; der Wortlaut steht
in `UI_SPEC` T-078 §3, Füllung (ii). Die Notiz holt `ARCHITECTURE.md`
nach — sie ordnet nichts Neues an.

---

### Nachtrag VII 2026-09-07 — Was `not_counted` zählt, wenn die Schranke eine Waffe ist (AD-026), und zwei Korrekturnotizen

**Anlass:** Der `ui-ux-designer` hat in T-084 gemeldet, dass
`explain.not_counted` seinen eigenen Docstring nicht einhält. Der Docstring
sagt, ein Effekt an einer **nicht geführten Armatur** sei nicht in
`not_counted`; die Rechnung legt ihn dort ab. Der `director` hat den
Mechanismus im Code nachgelesen und bestätigt. Entschieden wird hier keine
Reparatur, sondern eine **Bedeutung**: ob „ich führe diese Waffe gerade
nicht" eine Bedingung ist, in die der Spieler sich versetzen kann.

### 0. Messumgebung, für jede Zahl dieses Nachtrags (L-001, L-009)

Alle Zahlen unten sind **erschöpfende Zählungen über eine feste
Grundgesamtheit**, keine Stichproben — es gibt daher keinen
Stichprobenfehler, und keine Zahl dient als Schranke. Die Unsicherheit liegt
nicht in der Zählung, sondern in der **Grundgesamtheit**: ein Spielstand,
ein Datenabzug, zwei von zehn Nightfarern.

- **Datenabzug:** `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`,
  `data_version` 10350000, `extract_version` 11, `effect_count` 2076. Nur
  gelesen.
- **Bestand:** 309 besessene Kopien, 845 Effektrollen, 426 bzw. 434 stumme
  Effektzeilen (je nach Nightfarer).
- **Codestand:** `fd9f2bc`. Gegengeprüft mit
  `git diff --stat fd9f2bc -- nrplanner/`: die einzige Abweichung im
  Arbeitsbaum ist `nrplanner/app.py` (T-083, läuft parallel).
  `model.py`, `inventory.py` und das ganze `advisor/`-Paket sind
  byteweise `fd9f2bc`, und nur diese importieren die Messungen.
- **Umgebung A (die des Befunds):** Wylder, `Wylder's Greatsword`
  (`id` 3750000, `wep_type` 5), Stufe 15, `weapons_held` = dieselbe eine
  Armatur, Zielrichtung `max_damage`, `weighting` = `EVEN_WEIGHTING`.
- **Umgebung B (die zweite, vom Auftrag verlangt):** Ironeye,
  `Ironeye's Bow` (`id` 41750000, `wep_type` 51), Stufe 15, sonst gleich.
  Anderer Nightfarer **und** andere Waffengattung — Fernkampf gegen Nahkampf
  ist der Fall, an dem sich eine Waffenschranke am ehesten anders verhält.
- **Rezept, in Prosa statt als Datei**, weil die Messskripte auftragsgemäss
  im Scratchpad liegen und nicht im Repo:
  1. `model.configure(data)`, `inventory.load(data)`.
  2. Je besessener Kopie ein Einzelslot-Problem in ihrer eigenen Farbe und
     Deep-Lage, `base = evaluate(problem, (), ctx)`,
     `built = evaluate(problem, (cand,), ctx)`.
  3. Gezählt werden (i) die `ReasonLine` aus `explain.reasons`, die weder
     `is_curse` noch `CARRIES_A_FIGURE` sind, nach ihrer `silence`-Marke,
     und (ii) `len(explain.not_counted(built))`.
  4. Für die Spalte „AK-167" wird eine Zeile mit
     `SILENT_UNDER_A_CONDITION` nach `SILENT_ARMAMENT_BOUND` umgehängt, wenn
     ihr Effekt eines der vier Felder aus `explain._ARMAMENT_GATES` trägt
     und `model.satisfied_by_weapon` dafür **falsch** ist; umgekehrt fällt
     eine Zeile `SILENT_ARMAMENT_BOUND` mit **erfüllter** Schranke nach
     `SILENT_NO_NUMBER_HERE`.
  5. Für die Zahl, die der Spieler wirklich liest, zusätzlich **volle Läufe**
     über `advisor.run.run`: 2 Zielrichtungen × 88 Slotformen (die 74 Gefässe
     des Datensatzes, mit und ohne Deep, entdoppelt) = **176 Läufe** je
     Umgebung.
  6. Für die verworfene Lesart wird `model.CONDITIONAL_FIELDS` **im
     Speicher** um die drei Waffenfelder erleichtert und alles wiederholt.
     Nichts wird geschrieben.
- **Reproduktion der Fremdmessung:** Umgebung A gibt die Tabelle des
  `ui-ux-designer` aus T-084 Zeichen für Zeichen wieder (150 / 0 / 170 / 13 /
  93 / 0 gebaut, 150 / 0 / 124 / 58 / 94 / 0 nach AK-167, Summe 426 in
  beiden). Seine Zahlen stehen.

---

### AD-026 — Eine unerfüllte Waffentyp-Schranke ist eine Bedingung, in die der Spieler sich versetzen kann, und bleibt in `Build.situational`; falsch ist nicht die Rechnung, sondern der Docstring (2026-09-07, Status: aktiv; präzisiert AD-010, bestätigt D-3)

**Kontext.** `not_counted` liest `Build.situational` ab, gefiltert auf
`not entry.live`. `model.is_conditional` wertet eine unerfüllte
Waffentyp-Schranke als Bedingung, und `compute_qualitative` schreibt denselben
Effekt in **beide** Listen — nach `qualitative` immer, nach `situational`
zusätzlich, sofern er zum Nightfarer passt und nicht in `NO_SWITCH` steht.
Der Docstring behauptet daraus, `situational` halte solche Effekte nicht.

**Der Docstring ist nicht schlicht falsch, sondern ein ausgedehnter
Randbedingungssatz.** Er beruft sich auf **QA-104**, und QA-104 ist wahr —
aber über einen **anderen** Fall. QA-104 misst den *klassengebundenen*
Angriffsbuff (`magicSubCategoryChange` 130 / 113 / 118, „melee" bzw.
„ranged"). Nachgemessen: **8 solche Effekte im Datensatz, 0 davon
konditional**, keiner erreicht je `Build.situational` — sie landen in
`Build.class_rates`. Für sie stimmt der Satz. Angewendet wurde er auf die
*typgebundene* Schranke (`triggerOnWepType`, `wepTypeTrigger`,
`wepTypeTriggerCount`), und dort stimmt er nicht. Zwei verschiedene
Mechanismen, ein Satz. Das ist genau der Fehler, den die Regel „jede
tragende Aussage nennt ihre Randbedingung" verhindern soll — und
`ARCHITECTURE.md` hatte es an seiner eigenen Stelle **richtig** stehen:
Präzisierung AD-004, Punkt 6 sagt „Waffen**klasse**", nicht Waffentyp. Der
Docstring hat die Klasse zum Typ verallgemeinert.

**Kräfte.** Der Spieler kann eine Waffe wechseln, einen Nightfarer nicht —
das spricht für „Bedingung". Der Docstring, QA-104 und D-3 sprechen dem
Wortlaut nach für „Ausrüstungseigenschaft". Dahinter steht die härtere
Frage: was der Schalter im Planer verspricht, und was eine Zahl in der
Statuszeile behauptet.

**Optionen.**

- **K — konditional (Bestand).** Die unerfüllte Waffentyp-Schranke bleibt in
  `CONDITIONAL_FIELDS`, der Effekt bleibt in `situational`, bekommt seinen
  Schalter und zählt in `not_counted` und damit in 4.9b. *Konsequenz:* nichts
  am Rechenkern, nichts am `Build planner`-Tab, den der App Designer
  ausdrücklich für gut befunden hat. Der Docstring wird richtiggestellt. Der
  Preis: derselbe Effekt kann im `Why`-Dialog zweimal vorkommen — als Zeile
  „it depends on the armaments you carry" (Füllung c nach AK-167) und als
  Name im Abschnitt 4.9b.
- **E — ausrüstungsgebunden, naheliegend umgesetzt.** Die drei Waffenfelder
  fallen aus `CONDITIONAL_FIELDS`. *Konsequenz, gemessen statt vermutet:*
  **17 von 309 besessenen Kopien bekommen eine Zahl, die der Spieler nicht
  hat.** `Grand Tranquil Scene` zeigt dann +9 % auf allen fünf
  Angriffsraten, `Deep Polished Tranquil Scene` +20 % — für eine Waffe, die
  nicht auf dem Raster liegt. Die stummen Zeilen fallen von 426 auf 409 (A)
  und von 434 auf 417 (B), weil diese 17 nicht mehr stumm sind, sondern
  falsch beziffert. Das ist wörtlich der Fehler, gegen den der Kommentar an
  `CONDITIONAL_FIELDS` geschrieben ist („a real +12 % Physical Attack was
  displayed as +2.5 %"), und ein A7-Bruch: eine Zahl, vor der niemand gewarnt
  hat.
- **E' — ausrüstungsgebunden, sauber umgesetzt.** Eine dritte Ablage: gated,
  in keine Summe, **ohne** Schalter. *Konsequenz:* `compute_qualitative`,
  `Situational` und `Build` bekommen eine dritte Klasse; der Planer verliert
  46 Schalter, die heute eine beantwortbare Frage beantworten („was wäre das
  wert, wenn ich eine Axt trüge?"). Umbau des Rechenkerns nach S9 — in
  diesem Zyklus nicht umsetzbar, und er ändert einen Tab, der nicht zur
  Debatte steht.

**Entscheidung: K.** Drei Gründe, in dieser Reihenfolge:

1. **Der Bestand hat die Frage schon beantwortet, in Nutzersprache.** Der
   leere Zustand des Planers sagt heute: *„Effects that only work below a HP
   threshold, **with a particular armament**, or on a trigger would be listed
   here."* Die Armatur steht dort als eine von drei Bedingungen, unter der
   Überschrift `Conditional & situational`. Eine Architekturentscheidung, die
   das Gegenteil festlegt, führt ein zweites Muster für dasselbe Problem ein.
2. **Der Schalter ist der Beweis der Klasse.** Ein Schalter existiert, um zu
   beantworten „was wäre das wert, wenn die Bedingung hielte". Bei
   „unter 85 % HP" kann der Spieler die Bedingung herstellen; bei „mit einer
   Axt" auch — er wechselt die Waffe. Bei „ein anderer Nightfarer" kann er es
   nicht, und genau dort setzt `compute_qualitative` den Schalter schon heute
   nicht (`effecttext.works_for`). Die Grenze verläuft an der
   **Herstellbarkeit**, nicht an der Frage, ob eine Waffe im Spiel ist.
3. **E kostet Wahrheit, nicht nur Arbeit.** 17 falsche Zahlen sind ein
   messbarer Rückschritt gegen A7; E' kostet 46 Schalter und einen Umbau. K
   kostet einen Docstring.

**Was das an der Zahl ändert, die der Nutzer liest.** Die 46 aus dem Befund
sind eine Eigenschaft der **Kandidatenmenge**, nicht des Vorschlags. Über
176 volle Läufe je Umgebung:

| | Umgebung A (Wylder / Greatsword) | Umgebung B (Ironeye / Bow) |
|---|---|---|
| Läufe (2 Zielrichtungen × 88 Slotformen) | 176 | 176 |
| `not_counted`-Einträge zusammen | 565 | 473 |
| Mittel je Lauf | 3,21 | 2,69 |
| Schlechtester Lauf | 9 | 8 |
| davon waffengeschrankt | **1** | **1** |

**Die Entscheidung bewegt die Statuszeile 4.9b in 175 von 176 Läufen um
null.** Der Grund ist strukturell und nicht zufällig: die Beam-Suche rankt
nach der Punktzahl, und ein Effekt, der in keine Summe eingeht, trägt genau 0
bei — sie wählt solche Relikte fast nie. Sichtbar wird die Klasse im
**Picker**, wo jeder Kandidat seine Zeilen bekommt, und dort entscheidet
nicht `not_counted`, sondern die Füllung (AK-167/168). Damit hängt an dieser
Entscheidung weniger, als der Befund vermuten liess — aber die Zeile, die
`not_counted` **beschreibt**, hängt ganz daran.

**Ob eine zweite Gattung im selben Topf liegt — geprüft, mit Zahlen.**
Untersucht wurden `CONDITIONAL_FIELDS`, `CONDITIONAL_FIELD_VALUES` und
`timed_window` über alle 2076 Effekte:

| Gattung | Feld | Effekte | Urteil |
|---|---|---|---|
| Zustand des Spielers | `invocationConditionsStateChange1/2` | 202 / 6 | Bedingung, herstellbar |
| Waffentyp | `triggerOnWepType` | 144 | Bedingung, herstellbar — **diese AD** |
| Waffenzahl | `wepTypeTriggerCount` | 82 | Bedingung, herstellbar; **das Programm kann sie nie prüfen** |
| Waffentyp | `wepTypeTrigger` | 30 | wie `triggerOnWepType` |
| Lebenspunkte | `conditionHp`, `conditionHpRate` | 26 / 8 | Bedingung, herstellbar |
| Zeitfenster | `effectEndurance` > 0 | 20 | Bedingung, herstellbar, nur für N Sekunden |
| Gegnerzustand | `enemyStateInfoTrigger` | 9 | Bedingung, herstellbar |
| Zähler | `saveCategory` = 9 | 8 | **keine Ja/Nein-Bedingung**, sondern ein Zähler |

**Ergebnis: keine Gattung muss aus `situational` heraus.** Zwei sind aber
ausdrücklich zu nennen, weil sie nicht dasselbe sind wie die Waffe:

- **Der Zähler (`saveCategory` 9, 8 Effekte)** ist keine Bedingung, sondern
  eine Menge. Er trägt sein eigenes Kennzeichen (`Situational.accumulates`,
  `count`), und `live` heisst dort „count > 0". Er ist bereits getrennt und
  bleibt es. Kein Handlungsbedarf, aber `not_counted` zählt ihn mit, und das
  ist richtig: bei count 0 ist nichts gezählt worden.
- **`wepTypeTriggerCount` (82 Effekte im Datensatz, 28 Einträge je Umgebung —
  also die *Mehrheit* der 46 bzw. 47)** ist die Gattung, die man beim
  Entscheiden übersieht. Sie steht **absichtlich nicht** in
  `WEAPON_TYPE_GATES`: die Schranke will mehrere Armaturen desselben Typs,
  und `satisfied_by_weapon` kann das nicht beantworten. Sie bleibt daher
  **auch dann konditional, wenn der Spieler die Waffen wirklich trägt.** Das
  ist unter K richtig — der Spieler kann die Bedingung herstellen, das
  Programm kann es nur nicht sehen, und ein Schalter ist genau die ehrliche
  Antwort darauf. Es ist aber **kein** Fall, den „wechsle die Waffe" löst,
  und wer die 46 pauschal als „Waffe wechseln" liest, liest 28 davon falsch.

**Eine dritte Familie, latent, ausdrücklich benannt:** 72 der 144
`triggerOnWepType`-Effekte tragen einen Wert, der **kein Waffentyp ist**
(256 auf 70 Effekten, 512 auf 2). Kein Armaturenwechsel erfüllt sie je; was
sie bedeuten, geben die Spieldateien nicht her. Auf diesem Spielstand
erreichen sie `not_counted` **nicht** (0 Einträge in beiden Umgebungen), weil
keine besessene Kopie sie trägt. Sie sind damit kein Fall dieser
Entscheidung, aber eine Falle für die Anzeige: `GATE_FIELDS` beschriftet sie
mit *„only with a matching weapon type"*, und einen passenden Typ gibt es
nicht. Das ist ein Befund, kein Auftrag (siehe OF-23).

**Konsequenzen.** Leicht wird — nichts am Rechenkern, nichts am
`Build planner`, `AK-142` bleibt Wort für Wort gültig, und die Grenze von
`not_counted` ist ab jetzt an der Herstellbarkeit begründet statt an einer
Aufzählung. Dauerhaft schwer wird — der Satz in 4.9b muss eine Bedingung
beschreiben, die auch „du trägst diese Waffe nicht" und „du trägst nicht
genug davon" abdeckt, ohne den Spieler auf eine Suche zu schicken. Und ein
Effekt kann im `Why`-Dialog zweimal auftauchen; das ist gewollt und war schon
vor dieser AD so (`UI_SPEC` T-084-Nachtrag §6).

**Umkehrbarkeit: mittel.** K zurückzunehmen heisst E' zu bauen — eine dritte
Ablage in `compute_qualitative`, ein drittes Feld auf `Build`, und der
Planer verliert Schalter, die heute etwas beantworten. Der Rückweg ist
benannt und teuer; K selbst kostet nichts, weil es der Bestand ist.

---

### Was der `developer` zu tun hat (Fixrichtung, kein Patch)

1. **`explain.not_counted`: den Abschnitt „Scope" ersetzen.** Er muss sagen,
   was drin ist — jede Bedingung, in die der Spieler sich versetzen kann,
   **einschliesslich** einer Armatur, die er gerade nicht führt oder nicht oft
   genug führt — und was nicht: ein Effekt, der einem anderen Nightfarer
   gehört (`compute_qualitative` gibt ihm keinen Schalter), und ein
   **klassen**gebundener Angriffsbuff, der ohne Referenzarmatur 0 zählt
   (QA-104, 8 Effekte, keiner konditional). Der Verweis auf QA-104 bleibt
   stehen, aber als Beleg für die **Ausnahme**, nicht für die Regel.
2. **Sonst nichts.** Keine Änderung an `CONDITIONAL_FIELDS`,
   `WEAPON_TYPE_GATES`, `is_conditional`, `compute_qualitative`,
   `Situational`, `not_counted` selbst oder an einer Zahl. „Keine Änderung,
   aber der Docstring wird richtiggestellt" ist das vollständige Ergebnis
   dieser AD.
3. **Zwei Regressionsfälle**, weil ein Docstring nicht testbar ist, die
   Grenze aber schon.

**Der Regressionstest, und was ihn heute rot färbt** (L-002, L-008):

`tests/test_advisor_explain.py`, zwei Fälle gegen **eine** Grenze. Der
Baustein steht schon da: `tests/advisor_cases.py::an_armament_type_gate`
liefert `(effect id, Armatur des verlangten Typs, Armatur eines anderen)`.

- **Fall 1 — die Schranke ist unerfüllt:** Kontext nur mit `other` auf dem
  Raster. Erwartet: der Effektname **ist** in `explain.not_counted(built)`,
  und `len(...) == 1`.
- **Fall 2 — dieselbe Schranke ist erfüllt:** Kontext mit `carrier`
  zusätzlich auf dem Raster. Erwartet: der Name ist **nicht** darin, und
  `len(...) == 0`.

**Beide Erwartungen stehen als Literal im Fall**, nicht gerechnet aus
`built.situational`, `CONDITIONAL_FIELDS` oder `_ARMAMENT_GATES` — sonst
bleibt der Fall grün, gleichgültig was die bewachte Stelle sagt (L-008 b).
Beide laufen im **Standardlauf** (L-008 a); `an_armament_type_gate` braucht
den echten Datensatz, der Fall trägt also dieselbe Markierung wie seine
Nachbarn und wird auf einem Runner ohne Spielinstallation übersprungen — das
ist QA-106 und keine neue Lücke, muss aber im Bericht stehen.

**Die Änderung, die sie heute rot färbt** — der Gegenbau, ohne den der
`director` den Fix nicht abnimmt: in `nrplanner/model.py`
`CONDITIONAL_FIELDS` um `"triggerOnWepType"`, `"wepTypeTrigger"` und
`"wepTypeTriggerCount"` erleichtern. Das ist genau Option E. Fall 1 wird
dann rot (die Liste ist leer). Ein zweiter, unabhängiger Gegenbau: in
`explain.not_counted` einen Filter einziehen, der Einträge mit einem der
`_ARMAMENT_GATES` überspringt — auch dann wird Fall 1 rot, und Fall 2 bleibt
grün. Fall 2 wird rot, wenn `satisfied_by_weapon` die Grid-Menge nicht mehr
durchsucht (`isinstance`-Zweig entfernt).

**Überlebt einer der Gegenbauten, ist das ein Befund und wird berichtet,
nicht nachgebessert** (L-008 c).

---

### AK-167 und AK-168 — nachgeprüft, nicht übernommen

Der `ui-ux-designer` sagt, seine Vorgabe funktioniere unter beiden Lesarten.
**Gemessen: sie tut es — die Regel und ihre tragende Zahl. Ihre
Partitionssumme tut es nicht.**

| | A: K (Entscheidung) | A: E | B: K | B: E |
|---|---|---|---|---|
| (a) anderer Nightfarer | 150 | 150 | 159 | 159 |
| (a2) anderswo gezählt | 0 | 0 | 0 | 0 |
| **(b) Bedingung** | **124** | **124** | **127** | **127** |
| (c) Armaturen | 58 | 41 | 47 | 30 |
| (d) Rest | 94 | 94 | 101 | 101 |
| (e) nicht im Datensatz | 0 | 0 | 0 | 0 |
| **Summe** | **426** | **409** | **434** | **417** |

- **Die Prüfreihenfolge (AK-167 i) hält unter beiden Lesarten**, und (b)
  ergibt unter beiden dieselbe Zahl — 124 in A, 127 in B. Genau die Zahl, mit
  der er argumentiert, ist gegen die Lesart unempfindlich. Sein Satz ist
  bestätigt.
- **Die Reihenfolge ist unter K nicht überflüssig, sondern tragend.** Unter K
  überschneiden sich (b) und (c) auf 46 bzw. 47 Zeilen, und erst die
  Voranstellung von (c) entscheidet sie. Unter E überschneiden sie sich fast
  nicht mehr. Die Regel arbeitet also genau dort, wo diese AD entscheidet.
- **AK-168 (ii) hält unabhängig von der Lesart.** Der Test auf die
  **unerfüllte** Schranke ist es, der die 13 falschen Zeilen aus A entfernt
  (`HP Restoration upon Greatsword Attacks` bei geführtem Greatsword). In B
  sind es 0 gebaute (c)-Zeilen — die Regel ändert dort nichts Falsches,
  weil kein Bogeneffekt dieser Art auf einer besessenen Kopie liegt. Der
  Fall ist damit in einer Umgebung wirksam und in der anderen leer; beides
  ist erwartet.
- **Was unter E nicht überlebt, ist seine Summe.** 426 fällt auf 409, weil 17
  Zeilen aufhören, stumm zu sein — sie bekommen eine Zahl, die der Spieler
  nicht hat. AK-169 („die sechs Füllungen sind eine Partition, Rezept und
  Zahlen dabei") bliebe formal wahr, aber mit anderen Zahlen. Unter der hier
  getroffenen Entscheidung K bleibt AK-169 Wort für Wort und Zahl für Zahl
  gültig.

**Kein Auftragswechsel nötig.** Die Reihenfolge der beiden Aufträge bleibt,
wie der `director` sie gesetzt hat.

---

---

### AD-032 — Worauf „Schaden maximieren" rankt, seit keine Waffe mehr in die Zahl eingeht (2026-09-12, Status: **offen — vorgelegt, nicht entschieden**; die Wahl trifft der App Designer)

**Diese Entscheidung ist nicht getroffen.** Sie liegt als vier gemessene
Optionen vor. Was der `developer` daraus baut, steht erst fest, wenn der App
Designer eine davon waehlt; bis dahin gilt **Option A**, weil sie der
gebaute Zustand ist. Umgesetzt wird keine, bevor gewaehlt ist — AK-190,
AK-192 und AK-193 beschreiben sonst eine Zahl, die gleich wieder wechselt.

**Kontext.** T-188 (Commit `43fd992`) hat `advisorbar.asking_from` beide
Waffenfelder genommen: der Beraterlauf kennt weder `reference` noch
`weapons_held`. AK-191 ist damit erfuellt. Die Zahl, die uebrig bleibt, ist
`goals._attack_multiplier_mean` — das Mittel der fuenf Angriffsmultiplikatoren
aus `damage.AR_RATE_FOR`. Attribute und Passive gehen darin nicht auf.

Damit stehen zwei wahre Saetze gegeneinander:

- Der Docstring von `_attack_multiplier_mean` hat recht: *ohne Armatur gibt
  es keine Skalierung, die ein Attributsbonus fuettern koennte.* Das ist keine
  Luecke, das ist die Spielmechanik.
- `GOAL.md` A17 hat auch recht: die Zielrichtung soll *„nach
  Angriffsmultiplikatoren, **Attributen** und Passiven"* ranken — und eine
  Rangfolge, in der **184 von 210** Kopien auf exakt 0,0000 stehen, ist fuer
  den Spieler keine Rangfolge.

Die Entscheidung ist deshalb nicht „ist der Docstring richtig", sondern:
**welche feste Groesse tritt an die Stelle der weggefallenen Waffe** — und
was nimmt man dafuer in die Zahl auf, das zwischen Runden *nicht* fest ist.

**Kraefte.**

1. **Fest gegen aussagekraeftig.** Jede Option, die mehr Kopien unterscheidbar
   macht, holt etwas herein, das die Runde neu wuerfelt. Das ist kein
   Nebeneffekt, das ist der Preis.
2. **A7 gegen Vollstaendigkeit.** Eine erfundene Umrechnung zwischen
   Attributspunkten und Schaden ist genau das, was AD-023 und OF-13 verbieten.
   Erlaubt ist eine **benannte Annahme** (Vorbild: `EVEN_WEIGHTING`), nicht
   ein stiller Gewichtsfaktor.
3. **Zwei Zahlen, nie eine** (AD-004, AD-023). Eine Groesse, die Schaden und
   Attribute in einen Wert mischt, bricht die tragende Regel des Bereichs.
4. **Betreibbarkeit.** Der Grenzbeitrag wird je Kandidat und je Slot
   gerechnet; das Laufzeitbudget aus AD-018/AD-028 liegt bei Zehntelsekunden
   je Lauf, nicht bei Sekunden.

#### Messumgebung und Rezept — gilt fuer **jede** Zahl unten

Ohne diese Zeilen ist keine der Zahlen lesbar (L-001, L-009).

| | |
|---|---|
| Datensatz | `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`, `data_version` **10350000** |
| Spielstand | der des Nutzers, **nur lesend** ueber `inventory.load`; **312** Kopien, davon **210** gewoehnliche und 102 Deep |
| Grundgesamtheit | die **210 gewoehnlichen** Kopien — ein freier **weisser** Slot zieht jede Farbe, nichts gehalten, Grundzustand also leer |
| Nightfarer | Wylder, sofern nicht anders genannt; Level **15** (`tests/advisor_cases.LEVEL`) |
| Weg | `candidates.pool(...)` mit einer Zielrichtungs-Registry je Option, `types.marginal_for` je Kandidat — **kein** Programmstart, **kein** `Planner` |
| „unterscheidbar" heisst | Grenzbeitrag mit `abs(wert) > 1e-9`. Die Schranke ist eine Gleitkomma-Null, kein Sicherheitsabstand: die Werte liegen entweder exakt auf 0 oder ueber 0,01 |
| Skripte | `…/scratchpad/T-189/measure_options.py`, `measure2.py` … `measure6.py`, gemessen gegen Commit `b8f71a8` |
| Lesart | **Kopien**, nicht Relikt-Arten und nicht Effekt-Ids |

**Die Zahlen sind gemessen, nicht geschaetzt** — bis auf eine Ausnahme, die
als solche gekennzeichnet ist (Recluse unter Option B, siehe dort).

**Zwei Zahlen zum Einordnen, bevor die Optionen kommen.** Die Richtung
„Schaden minimieren" unterscheidet auf demselben Bestand **37 von 210**
Kopien. Unter beiden heutigen Richtungen zusammen haben **149 von 210**
Kopien gar keine Zahl. Und die Obergrenze ueberhaupt — jede hier gepruefte
Grundlage vereinigt, beide Richtungen — liegt bei **111 von 210**: **99
Kopien** dieses Bestands bewegen weder Schaden noch Ueberleben, unter keiner
Option. Ein Teil der 184 Nullen ist also nicht Fehler der Zahl, sondern
Eigenschaft der Sammlung.

#### Was die vorliegenden Recherchen dazu beitragen

Drei der sechs `docs/research/`-Berichte betreffen diese Entscheidung; sie
sind gelesen und hier verarbeitet, statt bezahlte Recherche zu wiederholen.

- **R-005** (Multiplikatoren kombinieren **multiplikativ**, hoch belegt) ist
  **kein** Einwand gegen Option A. Das arithmetische Mittel in
  `_attack_multiplier_mean` mittelt nicht *gestapelte Effekte* — die stapelt
  `model.compute` bereits multiplikativ —, sondern die **fuenf Schadensarten**.
  Es ist damit dieselbe Bauform wie `EVEN_WEIGHTING`: eine gleichgewichtete
  Annahme ueber Schadensarten. Wer das anders gewichten will, uebergibt eine
  andere `Weighting` — dieselbe Antwort wie bei OF-3.
- **R-004** (globaler Gesamtfaktor ~0,60, Ursache unbelegt) **stuetzt Option
  B**: ein konstanter Faktor kuerzt sich aus jeder Rangfolge und jedem
  Grenzbeitrag heraus. Die dortige Einschraenkung gilt aber auch hier — der
  Guardian-Versatz von rund 3 % ist nicht konstant, und Option B rankt je
  Nightfarer gegen eine **andere** Waffe. Zwischen zwei Nightfarern sind die
  B-Zahlen deshalb nicht vergleichbar. Das ist kein Mangel, solange die
  Oberflaeche nie zwei Helden nebeneinanderstellt — heute tut sie das nicht.
- **R-006** (heldengebundene Waffenklassen-Effekte; Claws-Mechanik belegt,
  Zahl unbelegt, Raider-Fall nur Indiz) trifft **genau** Option B. Zwei
  Richtungen, und beide sind eher Argumente **fuer** B:
  1. Der Claws-Malus gilt fuer *fremde* Traeger. Unter B rankt jeder
     Nightfarer gegen seine **eigene** Startarmatur — der Fall tritt nie ein.
     Unter Option D dagegen traete er fuer sieben von acht Helden auf, und
     zwar mit einer Zahl, die R-006 ausdruecklich als unbelegt fuehrt.
  2. Ein etwaiger Raider-Bonus laege auf genau der Waffenklasse seiner
     Startarmatur — also auf Bs Anker. Wird R-006 spaeter mit einer
     Kalibrierung beantwortet, bewegt sie unter B die Zahlen genau eines
     Helden und ist dort auch sichtbar; unter A bewegt sie gar nichts, weil
     keine Waffe in der Rechnung ist.

#### Option A — so lassen: das Mittel der fuenf Angriffsmultiplikatoren

**Grundlage.** `build.rates` fuer die fuenf Felder aus `damage.AR_RATE_FOR`.
Fest zwischen Runden, weil ein Multiplikator auf dem Relikt steht und auf
nichts sonst wartet.

**Unterscheidbar: 26 von 210** (gemessen). **8** verschiedene Werte, die
groesste Gruppe gleicher Werte umfasst **184** Kopien. Die 184 werden danach
nur noch nach Name und Handle sortiert.

**Was der Spieler sieht — ehrlich durchgerechnet.** Eine Liste, deren erste
26 Zeilen eine Ordnung haben und deren restliche 184 alphabetisch sind, ohne
dass die Oberflaeche das sagt. Ein reines Staerke-Relikt steht zwischen zwei
Relikten, die mit Schaden nichts zu tun haben, und traegt dieselbe +0,00.
**Das ist teilweise die wahre Aussage:** von den 184 bewegen 99 unter
*keiner* geprueften Grundlage irgendetwas. Fuer die uebrigen 85 ist die Null
aber eine Aussage ueber die *Rechnung*, nicht ueber das Relikt — und die
Oberflaeche unterscheidet beides heute nicht.

**Kosten.** Null im Code. Aber zwei Texte werden dann falsch und muessen
nachgezogen: `GOAL.md` A17 (*„Attributen und Passiven"* — streichen oder auf
„was die Multiplikatoren tragen" zuruecknehmen) und `MAX_DAMAGE.blurb`, den
T-188 auf denselben Wortlaut gesetzt hat. AK-190/192/193 bleiben, wie sie
geschrieben sind; AK-193 (`Attack multipliers`, keine Einheit) passt genau
auf diese Option und **nur** auf diese.

**Was verlorengeht.** Der Nutzerentscheid *„wir optimieren die stats und
passiven"* wird nicht eingeloest — Attribute bleiben unsichtbar. Und die
Zielrichtung „Schaden maximieren" ist fuer 88 % des Bestands keine Rangfolge;
der Spieler kann daraus nicht ablesen, ob er das Relikt behalten soll.

#### Option B — die Startarmatur des Nightfarers als **feste** Bezugswaffe

**Grundlage.** `hero["starting_weapon"]` — ein Feld des Datensatzes, keine
Annahme. Die Armatur, mit der ein Nightfarer jede Expedition beginnt, ist die
**einzige**, die nicht gewuerfelt wird. Der vorhandene Zweig
`_max_damage` mit `damage.equipped` wird damit wieder der Programmweg, mit
`slot_index=0` (die Startarmatur-Paarung, AD-020.6) und **ohne** die Rollen
der Armatur (siehe QA-226 unten).

**Unterscheidbar: 51 von 210** (gemessen, Wylder). **17** verschiedene Werte,
groesste Gruppe **159**. Je Nightfarer gemessen:

| Wylder | Guardian | Ironeye | Duchess | Raider | Revenant | Executor | Scholar | Undertaker | Recluse |
|---|---|---|---|---|---|---|---|---|---|
| 51 | 50 | 47 | 52 | 39 | **56** | 51 | 50 | 51 | **nicht messbar** |

**Der eine freie Parameter ist gemessen keiner.** Welche Stufe die
Startarmatur hat, ist zwischen Runden nicht fest — sie wird im Lauf
aufgewertet. Gemessen fuer alle neun messbaren Nightfarer, Stufe 1 bis 4:
**gleiche Anzahl und gleiche Reihenfolge**, erster Unterschied `None`. Die
Stufe bewegt die absolute Zahl, nicht die Rangfolge. Der Einwand „welche
Stufe denn?" ist damit erledigt, nicht weggeredet.

**Recluse ist die Luecke, und sie ist keine Kleinigkeit.** Recluse startet mit
`Recluse's Staff` (`wep_type` 57). Auf dem heute im System liegenden
Datenabzug wirft `weapons.rate` dafuer `KeyError` — die `reinforce`-Tabelle
dieses Abzugs kennt kein `catalyst_scaling`, sie stammt von einem Extraktor
vor `EXTRACT_VERSION` 9. **Option B ist fuer Recluse ungemessen und wuerde auf
diesem Abzug abstuerzen.** Vor einer Umsetzung von B ist das auf einem
frischen Abzug (Version 11) zu messen; die Schaetzung bis dahin lautet „in
der Groessenordnung der uebrigen, 40 bis 55", und sie ist eine Schaetzung.

**Kosten.** `asking_from` setzt `reference` wieder — aber auf die
Startarmatur des Helden, nicht auf das, was im Gitter liegt; `weapons_held`
entsprechend. `AdvisorRequest.reference_weapon_id` wird wieder belegt, sonst
weist `run._check` die Anfrage zurueck. **AK-193 bricht** (die Spalte heisst
dann wieder `Attack rating` mit Einheit `AR`) und muss neu geschrieben werden;
**AK-190** ebenso (`_NO_ARMAMENT` / `_NO_ARMAMENT_NOTE` entfallen, an ihre
Stelle tritt ein Satz ueber die feste Bezugswaffe); **AK-192** aendert seine
Zahlen, weil Waffentyp-Schranken wieder erfuellbar sind. **AK-191 haelt
wortwoertlich**: die Rangfolge haengt weiter an keiner *gefuehrten* Waffe, der
Bezug ist der Held. Gemessene Laufzeit: 0,023 s statt 0,018 s je Pool von 210
— ohne Bedeutung. **D-1 aus T-188 loest sich auf** (der Waffenzweig ist nicht
mehr toter Code), und A16 wird denselben Zweig brauchen.

**Was verlorengeht.** Drei Dinge, und das dritte ist das unangenehme:

1. **15 Kopien, die A heute rankt, verlieren ihre Zahl.** A und B
   ueberschneiden sich nur in 11 Kopien; 15 sind A-eigen, 40 B-eigen
   (26 = 15 + 11, 51 = 40 + 11). Die 15 sind Element-Multiplikatoren —
   `Night of the Lord`, `Dark Night of the Champion`, `Grand Drizzly Scene`
   — die auf einem physischen Greatsword nichts bewirken. **Man kann das als
   Gewinn lesen** (sie helfen Wylder nur, wenn er eine magische Waffe findet,
   und das ist genau das RNG, das A17 aussperrt) **oder als Verlust** (dem
   Spieler, der auf eine Element-Waffe hin plant, fehlt die Information).
   Beide Lesarten sind vertretbar; die Wahl gehoert dem App Designer.
2. **Die Zahl traegt wieder den Namen einer Waffe.** Wer die Startwaffe in
   Minute fuenf ablegt, rankt Relikte gegen etwas, das er nicht mehr fuehrt.
   Fest ist die Waffe **am Rundenanfang**, nicht ueber die Runde.
3. **Der Berater rechnet einen dritten Build.** Nicht den des Statblatts
   (das kennt die gefuehrte Waffe) und nicht den von heute (der kennt gar
   keine). Der Waechter aus D-2 (T-188) muss das aushalten.

#### Option C — zwei Zahlen: Multiplikatoren bleiben, Attribute werden eine eigene Zielrichtung

**Grundlage.** Eine dritte `Goal`-Funktion neben `MAX_DAMAGE` und
`MIN_DAMAGE_TAKEN`: die Summe der zugelegten **offensiven** Attributspunkte
(Staerke, Geschick, Intelligenz, Glaube, Arkan). Fest zwischen Runden, weil
ein Attributsbonus auf dem Relikt steht. Keine Umrechnung, keine Gewichte —
darum vertraeglich mit AD-023 und OF-13.

**Unterscheidbar: 53 von 210** unter der neuen Richtung allein (gemessen);
**75 von 210** haben unter *mindestens einer* der beiden Schadensspalten eine
Zahl; mit „Schaden minimieren" dazu **104 von 210**. Die neue Richtung hat
**8** verschiedene Werte, groesste Gruppe **157** — fuer sich genommen also
keine bessere Rangfolge als A, aber eine **andere**.

**Kosten.** Eine Funktion und ein Registry-Eintrag — die Bauform aus AD-004
traegt das ohne Aenderung an `candidates.py`, `evaluate.py` oder der Suche.
Aber: **AK-43** (das `Sort by` des Pickers fuehrt „genau die Eintraege") und
**AK-205** bekommen einen dritten Eintrag, `UI_SPEC.md` braucht neue AK fuer
Beschriftung und Einheit (`pts`), und `CANONICAL_POOL_ORDER` bleibt bei
`max_damage`. AK-190/192/193 bleiben unveraendert gueltig.

**Was verlorengeht.** **Attributspunkte sind nicht Schaden.** Zehn Punkte
Glaube auf einem Wylder, der auf Staerke skaliert, zaehlen in dieser Zahl
genauso viel wie zehn Punkte Staerke — die Richtung ist blind dafuer, ob das
Attribut ueberhaupt etwas traegt. Wer sie dagegen nach der Skalierung
gewichtet, hat Option B gebaut, nur mit mehr Schritten. Zweitens: der Spieler
muss zwei Spalten vergleichen, und die Richtung „Schaden maximieren" behaelt
ihre 184 Nullen.

#### Option D — Erwartungswert ueber die Armaturen statt Verzicht auf die Armatur

**Grundlage.** Statt die gewuerfelte Waffe *auszublenden*, ueber sie
**mitteln**: je eine Armatur pro Waffentyp, gleich gewichtet, und der
Grenzbeitrag ist der Mittelwert. Das Vorbild steht im selben Modul —
`EVEN_WEIGHTING` mittelt die acht Schadensarten gleich und **sagt, dass das
eine Annahme ist**. Die Antwort auf „die Waffe ist RNG" waere dann nicht
„also ignorieren wir sie", sondern „also nehmen wir ihren Erwartungswert".

**Unterscheidbar: 81 von 210** (gemessen als Vereinigung ueber 32 Waffentypen;
je Typ zwischen **10** und **60**, Median **43**). Das ist zugleich die
gemessene Obergrenze dessen, was eine waffenbezogene Zahl auf diesem Bestand
ueberhaupt trennen kann.

**Kosten.** Die hoechsten von allen vieren. Gemessen in der naiven Form — ein
vollstaendiger Pool je Waffentyp — **0,70 s** fuer 32 Pools von je 210
Kandidaten, gegen **0,018 s** heute; das ist Faktor 39 und liegt ueber dem
Budget aus AD-018/AD-028, sechs Slots gerechnet. Eine sparsame Fassung
(`model.compute` einmal je Kandidat, darueber 32 `weapons.rate`-Aufrufe) ist
deutlich billiger, **aber ungemessen** — und sie braucht einen Umbau von
`damage.equipped`, also einen Eingriff in die Fassade (AD-019). Dazu: die
zwei Katalysator-Typen fallen auf dem heutigen Abzug aus (siehe Option B),
`Goal.scope` braucht eine neue A7-Zeile, und der Cache-Schluessel waechst um
die Typmenge.

**Was verlorengeht.** **Das Gewicht ist erfunden.** Der Datensatz sagt nicht,
wie oft man einen Bogen findet und wie oft einen Greatsword; „alle Waffentypen
gleich haeufig" ist nachweislich falsch und waere nur als *benannte* Annahme
tragbar. Und die Zahl beantwortet eine Frage, die kein Spieler stellt: sie
sagt, was das Relikt im Mittel ueber Waffen wert ist, die er zu 31/32 nicht
fuehren wird. Zweitens verliert sie die Schaerfe — ein Relikt, das auf einem
Waffentyp stark ist und auf 31 nichts tut, verschwindet im Mittel.

#### Bewusst nicht als Option vorgelegt

- **Ein Mischindex aus Multiplikatoren und Attributspunkten** (etwa
  `mittel × (1 + punkte/100)`). Das ist genau der erfundene Umrechnungskurs,
  den AD-023 und OF-13 verbieten. *Wieder interessant, wenn:* der Datensatz
  je eine belegte Umrechnung von Attributspunkt zu Angriffswert hergibt —
  heute tut er das nur ueber eine konkrete Waffe, und das ist Option B.
- **Eine synthetische „Durchschnittswaffe"** mit gemittelten
  Skalierungskoeffizienten. Sie sieht wie Option B aus, ist aber eine Waffe,
  die es im Spiel nicht gibt; die Zahl waere mit nichts vergleichbar, was der
  Spieler auf dem Bildschirm sieht (A12).

#### Empfehlung des `architect` — eine Empfehlung, keine Entscheidung

**Option B**, aus drei Gruenden, die alle gemessen sind und nicht geraten:

1. „Fest zwischen Runden" ist bei B eine **Eigenschaft des Datensatzes**
   (`hero["starting_weapon"]`), bei C und D eine Annahme.
2. Sie verdoppelt die unterscheidbaren Kopien (26 → 51) und liefert als
   einzige Option, was A17 woertlich verspricht: Attribute bewegen die Zahl.
3. Ihr einziger freier Parameter — die Stufe — ist gemessen wirkungslos auf
   die Rangfolge.

**Wogegen die Empfehlung steht, und der App Designer kann es anders sehen:**
B holt die Waffe zurueck, die der Nutzerentscheid gerade hinauswerfen wollte.
Wer diesen Satz streng liest, waehlt **A + C** (75 von 210 unterscheidbar,
keine Waffe in der Rechnung) und nimmt dafuer die 184 Nullen in der
Schadensspalte in Kauf.

#### QA-226 — die gewuerfelten Buffs der Armaturen: **sie sollten fallen**

**Befund, gemessen.** `ctx.armament_effect_ids` geht heute weiter in jeden
Build (`evaluate.effect_ids_of`, letzte Zeile). Wirkung auf den Bestand:

- Ein **stapelbarer** Armaturen-Buff (`Physical Attack Up`, id 7001400 u. a.,
  13 solcher Ids liegen auf den 210 Kopien) bewegt **10 von 210** Zahlen,
  aber **nicht die Reihenfolge** (erster Unterschied `None`) — ein
  gemeinsamer Faktor verschiebt alle Grenzbeitraege gleich.
- Ein **nicht stapelbarer** (`isStrongestEffect`) bewegt die Reihenfolge. Der
  Datensatz kennt **6** nicht stapelbare Effekte, die eine Angriffsrate
  bewegen; **keiner** davon liegt auf einer der 210 Kopien, aber jeder ist auf
  **120 bis 141** Armaturen rollbar. Gemessen, je ein Effekt im Gitter:
  `Improved Holy Attack Power` — Reihenfolge weicht **ab Rang 3** ab;
  `Improved Fire Attack Power` — **ab Rang 4**; `Physical Attack Up`
  (8850550) — **ab Rang 3**; `Improved Magic` / `Improved Lightning` — ab
  Rang 16.

**Damit ist AK-191 woertlich gelesen heute nicht erfuellt**: zwei Laeufe, die
sich nur in der gefuehrten Armatur unterscheiden, koennen verschiedene
Rangfolgen ergeben, sobald die Armaturen etwas gerollt haben. Der Test aus
T-188 sieht das nicht — seine beiden Armaturen tragen keine Rollen, was der
`developer` als Luecke gemeldet hat.

**Empfehlung: `armament_effect_ids` faellt — unter jeder der vier Optionen.**
Der Nutzerentscheid nennt sie ausdruecklich (*„waffen **und deren buffs** sind
alle in der runde RNG-basiert"*), und sie sind messbar reihenfolgewirksam.
Unter Option B heisst das ausdruecklich auch: die **Startarmatur geht ohne
ihre Rollen** in die Rechnung.

**Was dabei verlorengeht:** die Passiven der Waffen verschwinden ganz aus der
Beraterrechnung, und der Berater entfernt sich ein weiteres Stueck vom
Statblatt (D-2). **Was dadurch leicht wird:** `armament_effect_ids` kann aus
`GoalContext` und `AdvisorRequest.armaments` verschwinden — P-1 aus T-188
(der Cache-Schluessel verfehlt sich beim Waffenwechsel) wird damit ueberhaupt
erst behebbar.

#### Konsequenzen

**Was jede Wahl gemeinsam nach sich zieht.** `GOAL.md` A17 und
`MAX_DAMAGE.blurb` muessen mit der gewaehlten Option in Deckung gebracht
werden — heute behaupten beide „Attribute und Passive" und keine gebaute Zahl
haelt das. Und die Oberflaeche braucht eine Antwort auf die Nullen: eine Zahl,
die „dieses Relikt tut fuer diese Richtung nichts" bedeutet, sollte nicht
aussehen wie eine Zahl, die „hier konnte nicht gerechnet werden" bedeutet.
Das ist eine Frage an den `ui-ux-designer`, keine an diese AD.

**Umkehrbarkeit.**

| Option | Umkehrbarkeit | was ein Rueckbau kostet |
|---|---|---|
| A | — (Ist-Zustand) | — |
| B | **leicht** | drei Zeilen in `asking_from`, plus die AK-Texte 190/192/193 zurueck. Kein Datenmodell, keine Schnittstelle |
| C | **mittel** | ein Registry-Eintrag ist billig; der dritte Eintrag im `Sort by` ist ein Oberflaechenversprechen, das man schlecht zurueckzieht, und gespeicherte Zieleinstellungen zeigen dann auf eine Richtung, die es nicht mehr gibt |
| D | **schwer** | die sparsame Fassung greift in `damage.equipped` und damit in die Fassade (AD-019) ein; der Cache-Schluessel aendert seine Form |
| QA-226 (Buffs fallen) | **leicht** | ein Feld wieder fuellen; solange es im Cache-Schluessel bleibt, ist nichts stale |

**Offene Fragen, die mit der Wahl beantwortet werden muessen** (Nummern
vergibt der `director`):

1. Sollen die 15 Element-Kopien, die Option B nicht mehr rankt, als Gewinn
   (RNG korrekt ausgesperrt) oder als Verlust (Planung auf Element-Waffen)
   gelten?
2. Soll die Oberflaeche „bewegt diese Richtung nicht" von „konnte nicht
   gerechnet werden" unterscheiden? 99 der 210 Kopien bewegen unter **keiner**
   Grundlage etwas — das ist eine Aussage, die das Programm treffen koennte.
3. Wird Option B gewaehlt: Recluse muss auf einem Abzug mit
   `EXTRACT_VERSION` ≥ 9 nachgemessen werden, **bevor** gebaut wird.

---

## Themenbereich D — Nebenlaeufigkeit, Cache, Hauptthread

*Wo gerechnet wird und wer dabei wartet. AD-006 und AD-007 legen die Bauform
fest; AD-028 zieht den Picker-Weg nach, nachdem gemessen war, dass er im
Hauptthread rechnet. **AD-028 ist die Entscheidung mit den meisten
Nachtraegen** — Nachtrag IX zieht die Punkte 1 bis 4 und W3 nach, Nachtrag X
den Vertrag des `AdvisorController` und W1. Beide beruehren disjunkte Punkte;
wo welcher gilt, steht als Klammer an der Stelle selbst.*

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

### Nachtrag VIII 2026-09-08 — Der Berater rechnet im Hauptthread, und das Lesen des Spielstands auch (AD-028, AD-029)

**Anlass:** Der `performance-tuner` hat in S11 (T-118) am echten Spielstand
gemessen und dabei zwei Befunde gefunden, die beide Struktur betreffen:
**QA-208** (der Picker-Weg des Beraters rechnet im Hauptthread — die
Begruendung von AD-018 Punkt 4 steht auf einer widerlegten Zahl) und
**QA-209** (das Lesen des Spielstands kostet 6,15 s im Hauptthread, bei jedem
Start und jedem `Rescan`). Der Nutzer hat am 08.09.2026 entschieden, dass
QA-209 **vor** dem Release von 1.8.0 angefasst wird.

**Quellen dieser beiden Entscheidungen:** `docs/perf/baselines.md` (S11-A bis
S11-H, versioniert, mit Umgebung), `docs/berichte/T-118-performance-tuner.md`
(Abschnitte 2.4, 3.1, 3.2, 4/P2, 4/P3, 6), `qa/findings.md` QA-208 und
QA-209. **Jede Zahl unten stammt von dort; dieser Nachtrag misst nichts
selbst.**

*Buchfuehrung: **AD-027 ist nicht vergeben.** Die Nummer existiert in keiner
Datei des Arbeitsbaums (Volltextsuche ueber das ganze Repository, 08.09.2026,
0 Treffer); `docs/state.md` fuehrt den Kreis bereits ab AD-030. Die Luecke
bleibt eine Luecke — Nummern werden in dieser Datei nicht neu vergeben.*

---

### AD-028 — Der Picker-Weg verlaesst den Hauptthread ueber eine **zweite Instanz derselben** `AdvisorController`-Klasse, nicht ueber die vorhandene und nicht ueber einen eigenen Weg (2026-09-08, Status: aktiv **in der Sache**; **Punkte 1 bis 4, W3 und die Schritte U5a/U5b/U6/U7 nachgezogen durch Nachtrag IX**, 2026-09-08; **W1 und der Vertrag des `AdvisorController` nachgezogen durch Nachtrag X**, 2026-09-08; zieht AD-018 Punkt 4 nach, praezisiert AD-006 und AD-007)

> **Lesehinweis (T-125, 2026-09-08).** Die Entscheidung — zweite Instanz
> derselben Klasse, Option D — **steht unveraendert**. Vier ihrer sieben
> verbindlichen Punkte tragen aber eine Annahme, die nach `UI_SPEC` AK-197
> bis AK-210 (T-124) nicht mehr gilt: dass der Zielrichtungswechsel im
> offenen Dialog eine zweite Frage stellt. Was daraus folgt, steht in
> **Nachtrag IX**; die Punkte unten bleiben im Wortlaut stehen, damit
> nachlesbar ist, worauf sie gebaut waren.

**Kontext.** AD-018 Punkt 4 sagt „Der Lauf bleibt im Worker". Gebaut ist das
Gegenteil, und zwar mit Absicht und Begruendung:
`relicpicker.SlotAdvice.ranking` ruft `advisor_candidates.pool` direkt auf
(`nrplanner/relicpicker.py:326-328`), und der Docstring darueber
(`276-281`) begruendet es mit „AD-018 measures the worst slot at ~51 ms
against the 250 ms of AK-09, so there is nothing to draw a wait for".
`AdvisorController` kommt in `relicpicker.py` nirgends vor; sein einziger
Nutzer ist `advisorbar.py` (52, 438, 441), also der `Optimize`-Weg.

**Die Voraussetzung ist widerlegt, und die Bauform des Fehlers ist die
eigentliche Lehre.** Die `~51 ms` waren nie gemessen: AD-018 hat sie aus
„205 Kandidaten mal 0,25 ms je Bewertung" **gerechnet**, die 0,25 ms stammten
aus einer Bewertung vom 01.09.2026 ohne protokollierte Umgebung, und die
gerechnete Zahl wurde anschliessend in drei Dateien geschrieben —
`ARCHITECTURE.md`, `UI_SPEC` §3.8, `relicpicker.py`. Keine der drei sagte,
dass sie gerechnet war. Gemessen sind **318,1 ms** (Median, n=25, Spanne
289,6–358,9; S11-C, Slot 2 weiss, 206 Kandidaten; Umgebung Ryzen 7 5800H bei
1102 von 3201 MHz unter `Legion Quiet Mode`, CPython 3.12.10, `76f1887`) —
Faktor 6,3, und **oberhalb** der 250-ms-Schwelle aus AK-09, ab der ein
Wartezustand gezeigt werden **muss**.

**Zwei Stellen sind betroffen, nicht eine.** Das Oeffnen des Pickers am
weissen Slot haelt das Fenster 318 ms an; `_sort_chosen`
(`relicpicker.py:1169-1171`) rechnet dieselben 318 ms im **bereits offenen**
Dialog noch einmal, wenn der Spieler die Zielrichtung wechselt. Das zweite
ist eine laufende Interaktion, kein Dialogaufbau.

**Kraefte, die im Konflikt stehen:**

| | |
|---|---|
| A6, dritte Zeile | keine Beraterrechnung haelt den Hauptthread laenger als **50 ms** an |
| AK-09 / AK-10 | unter 250 ms **kein** Wartezustand, ueber 250 ms **muss** einer gezeigt werden |
| AK-08 | waehrend eines laufenden Laufs muss sich ein Slot oeffnen lassen |
| AD-006.4 | **hoechstens ein Lauf gleichzeitig** — je Controller-Instanz |
| Antwortform | der Picker braucht den **ganzen** Pool (alle 206 Kandidaten, beide Zielrichtungen); `AdvisorResult` traegt die **besten 20** |
| Kosten | `run.run` 403,3 ms gegen `candidates.pool` 321,2 ms (S11-B) — 82 ms fuer Erklaerungen, die der Picker nicht zeigt |
| Bestand | zwei Muster fuer dasselbe Problem sind ein Entwurfsfehler, auch wenn das zweite besser waere |

**Optionen:**

- **A — im Bestand bleiben, nichts Neues einfuehren.** Die Rechnung bleibt im
  Hauptthread und wird nur billiger: P1a aus T-118 (Text erst bauen, wenn ihn
  jemand liest) senkt `pool` gemessen von 335,1 auf **245,5 ms** (S11-B).
  Konsequenz: A6s dritte Zeile bliebe um Faktor 5 verletzt, und 245,5 ms
  liegen 2 % unter einer 250-ms-Schwelle, deren Messrauschen 16 % betraegt —
  eine Schranke, die bei jeder zweiten Messung kippt. **Verworfen: die Zahl
  traegt nicht.**
- **B — der Picker fragt die vorhandene Instanz der Advisor bar** ueber
  `run.run`. Konsequenz: eine Instanz ist **eine** Spur (AD-006.4) — das
  Oeffnen eines Slots braeche einen laufenden `Optimize` ab und hoehlte AK-08
  aus; die Antwortform passt nicht (20 Vorschlaege statt 206 Kandidaten);
  +82 ms je Frage. **Verworfen.**
- **C — ein eigener Weg fuer den Picker:** zweiter QThread, eigene
  Entprellung, eigener Zaehler, neu geschrieben. Konsequenz: das zweite
  Muster fuer dasselbe Problem, und der Generationszaehler existierte dann an
  zwei Stellen mit zwei Regeln. **Verworfen.**
- **D — dieselbe Klasse, zweite Instanz, zweite Antwortfunktion.** Der
  `AdvisorController` bekommt die Funktion, die sein Worker ausfuehrt, bei
  der Konstruktion; die Advisor bar konstruiert ihn mit `run.run`, das
  Fenster eine zweite Instanz mit einer neuen Qt-freien Funktion in `run.py`,
  die genau das antwortet, was `SlotAdvice.ranking` heute selbst rechnet.
  Konsequenz: zwei Spuren, ein Muster, ein Ort fuer Thread, Entprellung,
  Zaehler und Cache.

**Entscheidung: D.**

**Verbindlich:**

1. **Zwei Instanzen, eine Klasse, drei Zahlen aus S11.** Advisor bar:
   `run.run`, Entprellung **250 ms**, Cache **32**. Picker-Spur: die neue
   Pool-Funktion, Entprellung **100 ms**, Cache **64**. Die Bedingung, unter
   der der `performance-tuner` die 64 gegeben hat — *„sobald der Picker ueber
   den `AdvisorController` fragt"* — ist mit dieser Entscheidung erfuellt und
   vorher nicht.
   *(**Nachgezogen, Nachtrag IX-1:** die Entprellung der Picker-Spur ist
   **0 ms**. Die 100 ms bleiben als Zahl mit ihrer Wiederkehrbedingung
   stehen. **Nachtrag IX-3:** die 64 stehen weiter, ihre Herleitung deckt
   die Antwortform der Picker-Spur aber nicht — U7 misst nach.)*
2. **Zwei Caches, getrennt bemessen.** Das ist die Antwort auf die Frage, die
   T-118 Abschnitt 3.2 dem `architect` gestellt hat. Ein Cache mit Eintraegen
   von **33,4 KiB** (Picker) und **279,9 KiB** (Gesamtlauf) unter **einer**
   Grenze zwingt eine der beiden Zahlen, falsch zu sein: 64 Gesamtlauf-
   Eintraege waeren 17,49 MiB fuer gemessene **0** Treffer, 32 Picker-
   Eintraege liessen **41** gemessene Treffer und 16,5 s je Sitzung liegen.
   Die Groesse gehoert an die Instanz, nicht an die Klasse.
   *(**Nachgezogen, Nachtrag IX-3:** die **33,4 KiB** sind an einer
   `AdvisorResult` mit **20 Suggestions** gemessen, nicht an dem `SlotPool`
   mit **206 Kandidaten**, den diese Entscheidung der Picker-Spur als
   Antwortform gibt. Die **Aufteilung** in zwei Caches bleibt richtig; die
   **Zahl 64** haengt an einer Messung, deren Grundgesamtheit eine andere
   ist.)*
3. **Keine zweite Schluesselform** — AD-018 haelt woertlich. Die Picker-Frage
   ist der kanonische Fall „freie Slots = genau einer": ein `SlotProblem`, in
   dem jeder Slot **ausser** dem geoeffneten gehalten ist. Der Slot-Index ist
   dann der einzige nicht gehaltene und braucht **kein** neues Feld in
   `AdvisorRequest`. `candidates.base_state_for` behandelt beide Formen
   bereits gleich („For a slot that is already free this is `problem`
   unchanged"), der Grundzustand ist derselbe. **Nachzuweisen ist das, nicht
   zu glauben:** derselbe `SlotPool` vorher und nachher, verglichen ueber
   Handles und Punktzahlen, mit dem differentiellen Aufbau unter
   `scripts/differential/`.
   *(**Nachgezogen, Nachtrag IX-2:** „keine zweite Schluesselform" galt fuer
   den **Slot-Index** — geprueft an `SlotProblem`. Auf das Feld `goal_id`
   desselben Schluessels trifft die Bedingung **nicht** zu: der Pool haengt
   nicht an der Zielrichtung, der Schluessel heute schon. Die Picker-Spur
   fragt deshalb unter einer **kanonischen** Zielrichtung.)*
4. **Der Generationszaehler gilt jetzt auch im Picker**, und das kehrt den
   Docstring `276-281` um. Seine Randbedingung war *„die Rechnung kehrt
   zurueck, bevor der Dialog oeffnet"* — genau die entfaellt. Zwei Faelle,
   beide heute im Code: der offene Dialog rechnet beim Wechsel der
   Zielrichtung neu (`1169-1171`), und der Dialog kann geschlossen werden,
   waehrend eine Antwort unterwegs ist. **Kein zweiter Zaehler**: der Zaehler
   gehoert der Instanz, und die Picker-Spur ist eine Instanz derselben
   Klasse. Der Docstring wird ersetzt, nicht ergaenzt — er begruendet heute
   das Gegenteil dessen, was gilt.
   *(**Nachgezogen, Nachtrag IX-4:** der **erste** der beiden Faelle —
   `1169-1171` rechnet beim Richtungswechsel neu — **entfaellt**; er ist nach
   AK-204/AK-206 keine Frage mehr. Der zweite bleibt und traegt den Zaehler
   allein; ein dritter kommt hinzu. Der Zaehler bleibt noetig, die
   Entscheidung kippt nicht.)*
5. **Die Picker-Spur lebt am Fenster, nicht am Dialog.** Ein Cache im Dialog
   stirbt mit ihm, und der gemessene Nutzen entsteht gerade ueber
   Dialoggrenzen hinweg (S11, Spur „beide Ziele x 6 Slots x 4 Zustaende":
   30 % Treffer). Der Dialog verbindet sich beim Oeffnen und trennt beim
   Schliessen; eine Antwort, die danach eintrifft, faellt am Zaehler und
   fasst kein Widget an.
6. **`before_the_data_changes` und `shutdown` muessen beide Spuren
   erreichen.** `rescan_save` ruft heute `advisor_bar.the_data_is_changing()`
   — eine Stelle fuer eine Spur. Mit zwei Spuren ist ein vergessener Aufruf
   ein Cache, der einen Neu-Scan ueberlebt, also genau der Fehler, gegen den
   AD-006.7 gebaut ist. Die Verteilung gehoert an **eine** Stelle im Fenster,
   nicht als zwei Aufrufe nebeneinander an jede Aufrufstelle.
7. **`relicpicker` fragt den Berater nicht mehr direkt.** Heute importiert es
   `advisor.candidates` und `advisor.run`. Danach fragt `SlotAdvice` die Spur
   des Fensters. Abhaengigkeitsrichtung: `relicpicker` → `advisorbar`/Fenster
   → `advisor.worker` → `advisor.run` → `advisor.candidates`. Kein Zyklus;
   die Kopplung wird kleiner, nicht groesser.

**Sichtbare Aenderung: ja — der `ui-ux-designer` geht vor dem `developer`.**
Drei Dinge, die ich benenne und ausdruecklich **nicht** entwerfe:

- **(a)** `UI_SPEC` §3.8 steht woertlich auf der widerlegten Zahl (*„AD-018
  misst den teuersten Picker-Lauf mit ~51 ms … kein Fortschrittsbalken, kein
  Wartecursor, kein Aufblitzen"*). Bei 318,1 ms greift die andere Haelfte von
  AK-09/AK-10. §3.8 muss neu geschrieben werden.
- **(b)** Der Dialog oeffnet jetzt **vor** den Zahlen. Zur Haelfte ist das
  bereits spezifiziert und gebaut: §3.3 reserviert den Platz und setzt `…`
  (`PENDING`), AK-41 verlangt 0 px Hoehenunterschied. **Nicht** spezifiziert
  ist, was mit **Ordnung, Kopfzeile und Spitzenwert-Chips** geschieht, die
  heute beim Bauen des Rasters aus der Rangfolge entstehen — eine
  Neusortierung 320 ms nach dem Oeffnen bewegt Karten unter dem Zeiger.
  §3.5 Punkt 2 („die Sortierung ist stabil") beantwortet das nicht: dort
  geht es um zwei Oeffnungen, hier um zwei Anstriche derselben.
- **(c)** Was der Spieler sieht, wenn er die Zielrichtung im offenen Dialog
  wechselt und die Antwort 320 ms braucht.

**Der Regressionstest — drei Waechter, jeder mit seiner toetenden Mutation
(L-008), alle im Standardlauf, keiner mit einer Wanduhr-Schranke:**

- **W1 — strukturell.** Keine Datei unter `nrplanner/` ausser
  `advisor/worker.py` ruft `run.run`, die neue Pool-Funktion oder
  `candidates.pool` auf. Form: dieselbe AST-Zaehlung, die
  `tests/test_one_build.py` fuer `model.compute` schon fuehrt. **Die
  Erwartung ist eine Liste erlaubter Aufrufer im Test, nicht das, was in
  `relicpicker.py` steht** (L-008b — eine Erwartung, die aus der bewachten
  Stelle gerechnet wird, bleibt gruen, was auch immer dort steht).
  *Toetende Mutation:* den Aufruf `326-328` wieder einsetzen → rot.
  *Bau-Konfiguration (L-004):* keine. Der Waechter ist ein reiner
  pytest-Test, den kein Buildsystem-Schalter aktiviert; es gibt daher keine
  tragende Zeile, deren Entfernen rot werden muesste. Das ist die
  Herleitung der Unnoetigkeit, nicht ihr Fehlen.
  *(**Nachgezogen, Nachtrag X-3:** der Wortlaut oben — „keine Datei ausser
  `advisor/worker.py`" — ist vor U5b geschrieben und steht gegen den gebauten
  Zustand. **Verbindlich ist Fassung 2 in X-3** mit vier benannten Stellen und
  „nennt" statt „ruft auf"; die Sache — kein Fenster, kein Dialog, kein Tab
  bekommt die Rechnung zu fassen — ist unveraendert. Der Wortlaut hier bleibt
  stehen, damit die Aenderung nachlesbar ist.)*
- **W2 — der erste Anstrich traegt keine Zahlen.** Der Picker wird mit einer
  Spur geoeffnet, die nie antwortet; jede Karte traegt `PENDING` in beiden
  Wertzeilen, und der Dialog steht.
  *Toetende Mutation:* die Rechnung wieder synchron vor dem Oeffnen → die
  Karten tragen Zahlen → rot. Kein Zeitmass, damit nichts flackert.
- **W3 — die ueberholte Antwort erreicht nichts.** Zwei Fragen hintereinander
  (Wechsel der Zielrichtung), die erste Antwort wird **nach** der zweiten
  zugestellt; auf dem Bildschirm steht die zweite, und die erste hat nichts
  angefasst.
  *Toetende Mutation:* die Generationspruefung ausbauen → rot.
  *(**Nachgezogen, Nachtrag IX-4:** die Vorrichtung „Wechsel der
  Zielrichtung" **gibt es nicht mehr** — sie stellt keine zweite Frage. W3
  bekommt in Nachtrag IX eine Vorrichtung, die es noch gibt; sonst waere der
  Waechter gruen, weil sein Fall nicht herstellbar ist.)*
- **Ausdruecklich nicht in der Suite: die 50-ms-Zeile von A6.** Sie ist eine
  Messgroesse und gehoert in `docs/perf/baselines.md` zum
  `performance-tuner`. Eine Wanduhr-Schranke in der Suite misst auf jeder
  Maschine etwas anderes und waere genau die Zahl ohne Rezept, an der AD-018
  gescheitert ist (L-001, L-009).
- **Ein ueberlebender Gegenbau ist ein Befund** und wird berichtet, nicht
  stillschweigend nachgebessert (L-008c).

**Konsequenzen.** *Leicht wird:* A6s dritte Zeile wird auf dem Hauptweg
ueberhaupt erst erreichbar; die Entprellung von 100 ms entprellt jetzt etwas;
der LRU-Wert 64 bekommt seinen gemessenen Nutzen; ein Wartezustand im Picker
wird moeglich, weil es etwas zu warten gibt. *Dauerhaft schwer wird:* **zwei
Spuren koennen gleichzeitig rechnen.** Das ist gewollt — AK-08 verlangt, dass
sich waehrend eines `Optimize` ein Slot oeffnen laesst —, kostet aber unter
dem GIL Durchsatz auf beiden Seiten. **Nicht gemessen; siehe OF-25.** Und:
der Picker haengt jetzt an einer Objektkette (Slot → Fenster → Spur), die ein
Test von Hand nicht mehr nebenbei stellt; `advice_for` faengt den Fall
„Slot ohne Fenster" heute schon ab und muss ihn weiter abfangen.

**Umkehrbarkeit: mittel.** Die Rechnung ist dieselbe Funktion; zurueck ginge
der Aufruf an einem Tag. Was nicht zurueckgeht, ist die Oberflaeche: ein
Dialog, der ohne Zahlen oeffnet und sie nachtraegt, ist eine Erwartung des
Spielers, und §3.8 waere dann ein zweites Mal zu schreiben.

---

### Nachtrag IX 2026-09-08 — Der Zielrichtungswechsel war nie eine Frage (Nachtraege zu AD-028, Fassung 2 von U5a bis U7)

**Anlass.** Der `ui-ux-designer` hat in T-124 die Oberflaeche des wartenden
Pickers vorgegeben (`UI_SPEC.md`, AK-197 bis AK-210) und dabei drei Punkte an
AD-028 zurueckgegeben. Der `director` hat sie als T-125 hierher gegeben, mit
der ausdruecklichen Auflage, den tragenden Befund **nachzupruefen** statt ihn
zu uebernehmen.

**Was hier geprueft wurde und was nicht.** Alle Aussagen unten sind am
**Quellstand gelesen** (`nrplanner/relicpicker.py`,
`nrplanner/advisor/candidates.py`, `advisor/worker.py`, `advisor/run.py`,
`advisor/types.py`, `advisor/goals.py`, `nrplanner/advisorbar.py`), mit
Fundstelle. **Es wurde nichts gestartet und nichts gemessen** — jede Zahl ist
aus `docs/perf/baselines.md` oder `docs/berichte/T-118-performance-tuner.md`
zitiert; wo eine Zahl aus zitierten Zahlen **gerechnet** ist, steht das dabei
(L-001). Die `UI_SPEC` ist gesetzt und wurde nicht angefasst.

---

### IX-0 — Die Nachpruefung: der Befund haelt, an einer Stelle weiter als behauptet, an einer anderen nicht

**Behauptung aus T-124 (Abschnitt 3 seines Berichts):** `candidates.pool`
bewertet ohnehin jedes Ziel fuer jeden Kandidaten, der Dialog ist modal, also
braucht der Zielrichtungswechsel im offenen Dialog **gar keine Rechnung**; die
318 ms in `_sort_chosen` (`relicpicker.py:1169-1171`) sind reine Verschwendung.

**Geprueft — er haelt.** Die Stuecke, jedes an einer Zeile:

| Stueck | Fundstelle | Befund |
|---|---|---|
| Der Picker uebergibt **die ganze Registry** als `goals` | `relicpicker.py:325-327` (`advisor_goals.GOALS`) | ja — das ist die Voraussetzung, die T-124 **nicht** genannt hat, und ohne die der Rest nicht traegt |
| `marginals` je Kandidat ueber **alle** Ziele | `candidates.py:316-320` | ja |
| `baseline` je Ziel, `candidates` ungekuerzt | `candidates.py:328-331` | ja |
| `rank_by` wirkt **nur** auf `measured.sort(...)` und auf das Feld selbst | `candidates.py:323`, `327` | ja — der **Inhalt** des Pools ist richtungsfrei, nur seine **Reihenfolge** nicht |
| `unknowns` haengt an Slot und Bestand, nicht an der Richtung | `candidates.py:_pool_findings` ueber `without_handle`/`conditional`/`converting` | ja |
| Grundzustand am Slot, nicht an der Richtung | `candidates.py:61-79` (`base_state_for`) | ja |
| `ctx` traegt keine Richtung | `advisorbar.asking_from` (`weighting = DEFAULT_WEIGHTING`) | ja |
| Der Dialog ist modal | `relicpicker.py`, `self.setModal(True)` im `__init__` | ja |
| Die Anzeige ordnet selbst um und liest ueber Handles nach | `relicpicker.py:1019-1060` (`_in_the_chosen_order`), `Ranking.gain`, `Ranking.top_handles` | ja — beide Richtungen werden dort ohnehin schon gelesen (`top_handles(other_id)`, Zeile 1054) |

**Die Randbedingung, die T-124 nicht genannt hat und die den Befund traegt:**
Ein Pool bedient beide Richtungen nur, solange **jede Richtung, die der Picker
zeichnen kann, auch in dem `goals` steckt, mit dem der Pool gebaut wurde.**
Heute sind das zwei getrennt geschriebene Stellen:
`advisorbar.GOAL_ORDER = ("max_damage", "min_damage_taken")` (Zeile 67 — was
der Picker zeichnet, ueber `relicpicker.VALUE_DIRECTIONS = advisorbar.GOAL_ORDER`)
und `advisor/goals.py:302-305` `GOALS` (was gerechnet wird). Sie stimmen heute
ueberein und **koennen auseinanderlaufen** — eine dritte Zielrichtung, die in
`GOAL_ORDER` steht und nicht in `GOALS`, laesst den ganzen
Wiederverwendungsschluss still fallen. Dagegen steht unten **W4**.

**Die zweite Stelle, die dieser Befund trifft und die T-124 nicht gesehen hat:
der Cache-Schluessel.** `run.cache_key` nimmt **jedes** Feld der
`AdvisorRequest` ausser `generation` (`run.py:170-180`), also auch `goal_id`.
Damit ist die Antwort richtungsfrei, der Schluessel darueber aber nicht: eine
Oeffnung desselben Slots unter der anderen Richtung ist ein **anderer**
Schluessel, ein Fehltreffer und dieselben 318 ms noch einmal. Das ist genau
die Verschwendung aus `_sort_chosen`, nur ueber Dialoggrenzen hinweg statt
innerhalb einer Oeffnung — und sie ist gemessen: T-118 Abschnitt 3.2, Spur
**„Zielrichtung umschalten": 8 Fragen, 2 verschiedene, 75 % Treffer.** Diese
Spur besteht ausschliesslich aus dieser Doppelung. Siehe **IX-2**.

**Was am Befund nicht haelt:** die Nebenbemerkung, `candidates.pools()` sei
„die eigentliche Loesung" — siehe **IX-5**. `pools()` rechnet etwas anderes.

---

### IX-1 — Die Entprellung der Picker-Spur ist **0 ms**, und eine bereits bekannte Antwort wird **sofort** zurueckgegeben, nicht ueber den Zeitgeber

**Kontext.** AD-028 Punkt 1 gibt der Picker-Spur die 100 ms aus AD-006.5. Die
Zahl stammt dort aus einem Fall, den es in der Picker-Spur nicht gibt:
gedaempft wurden **Tastendruecke im Filterfeld und ein gezogener
Level-Schieber** — vierzig Fragen, von denen der Spieler neununddreissig schon
verworfen hat, waehrend er sie stellt. Die Randbedingung dieser Zahl ist
„zwischen zwei Fragen liegt weniger als eine Ueberlegung", und **fuer die
Picker-Spur trifft sie nicht zu**:

- Nach `UI_SPEC` AK-206 gibt es **eine Frage je Oeffnung**; Filter, Bildlauf,
  Favoriten und `Name` fragen nicht, und nach IX-0 fragt auch der
  Richtungswechsel nicht.
- Der Dialog ist **modal**: waehrend einer Oeffnung kann keine zweite Frage
  entstehen.
- Zwischen zwei Oeffnungen liegt mindestens ein Schliessen und ein Klick, also
  ein Vielfaches von 100 ms. Die Kette „ein Lauf zur Zeit" haelt auch ohne
  Entprellung: `_start_what_is_pending` steigt aus, solange ein Thread lebt,
  und `_on_thread_finished` holt die wartende Frage nach
  (`worker.py:285-286`, `307-321`).

**Was die 100 ms stattdessen kosten** — gerechnet aus gemessenen Zahlen, keine
eigene Messung:

| Fall | gemessen (S11-C) | mit 100 ms Entprellung | Anteil der Konstante |
|---|---|---|---|
| teuerster Slot (2, weiss, 206 Kandidaten) | 318,1 ms | 418,1 ms | 24 % |
| billigster Slot (5, Deep, 21 Kandidaten) | 32,3 ms | 132,3 ms | 76 % |
| Cache-Treffer | 0 ms | 100 ms | 100 % |

Gegen **A6** („eine Slot-Frage ist im Median unter 500 ms beantwortet")
schrumpft der Abstand von 36 % auf 16 % — und der **Hauptthread-Rest** einer
Frage (Anfragebau, `frozen_inventory` ueber 309 Kopien, `inventory_fingerprint`)
ist in dieser Rechnung noch gar nicht enthalten, weil er nie gemessen wurde
(OF-26). Eine Konstante, die 24 % eines Budgets aufbraucht, das an einer
ungemessenen Stelle noch belastet wird, ist nicht zu rechtfertigen, wenn sie
nichts daempft.

**Der Cache-Treffer ist der schaerfere Teil.** Der `AdvisorController` sieht
im Cache erst **nach** dem Zeitgeber nach: `ask` armiert den Timer
(`worker.py:213`), die Abfrage steht in `_start_what_is_pending`
(`worker.py:290-293`). Eine bekannte Antwort kommt damit **nie** vor dem
ersten Anstrich an — auch bei 0 ms nicht, weil ein `QTimer` fruehestens im
naechsten Durchlauf der Ereignisschleife feuert. `UI_SPEC` §2 sieht aber
ausdruecklich vor: *„Liegt die Antwort schon beim Bau des Rasters vor
(Cache-Treffer), wird der Wartezustand nicht betreten: dann gibt es einen
einzigen Anstrich, wie heute."* **Dieser Satz ist mit dem heutigen
Kontrollfluss nicht baubar.** Kein Widerspruch zur Spec — eine Vorgabe, die
diese Entscheidung erst einloest.

**Optionen:**

- **A — im Bestand bleiben** (100 ms, Cache hinter dem Zeitgeber).
  Konsequenz: 100 ms auf jede Frage, ein Cache-Treffer verliert seinen ganzen
  gemessenen Wert (er spart die Rechnung, nicht die Wartezeit), und der
  Cache-Treffer-Satz der `UI_SPEC` bleibt unerfuellbar. **Verworfen.**
- **B — Entprellung 0 ms, sonst nichts.** Konsequenz: 100 ms gespart, der
  Cache-Treffer kommt weiter als **zweiter** Anstrich. Billig, laesst aber die
  Haelfte liegen.
- **C — Entprellung 0 ms, und der Controller beantwortet eine bereits bekannte
  Frage im selben Aufruf.** Konsequenz: ein zweiter Rueckgabeweg an einer
  Klasse, die zwei Instanzen bedient.
- **D — die Klasse sieht generell vor dem Zeitgeber im Cache nach.**
  Konsequenz: **aendert die Advisor bar mit** — ein gezogener Level-Schieber
  zeichnete den Streifen bei jedem Treffer neu, also genau das Flackern, gegen
  das AD-006.5 gebaut ist. **Verworfen.**

**Entscheidung: C.**

**Verbindlich:**

1. **Die Picker-Spur wird mit `debounce_ms = 0` konstruiert.** Die Advisor bar
   behaelt ihre 250 ms.
2. **Die 100 ms werden nicht geloescht, sondern mit ihrer Wiederkehrbedingung
   aufgeschrieben:** *sobald die Picker-Spur mehr als eine Frage je Oeffnung
   stellen kann.* Das ist genau der Rueckweg, den `UI_SPEC` §4 fuer den Fall
   vorsieht, dass ein Pool die andere Richtung doch nicht bedient — dann fragt
   jeder Schritt durch die `Sort by`-Liste erneut (mit Pfeiltasten auch
   ungewollt, siehe F-Q in T-124), und die 100 ms sind sofort wieder richtig.
   **Wer diesen Rueckweg baut, holt die 100 ms zurueck; beides gehoert in
   denselben Commit.**
3. **Ein zweiter Rueckgabeweg, kein zweiter Antwortweg.** Der Controller
   bekommt **eine** zusaetzliche Methode („frag, und gib mir die Antwort
   sofort, falls du sie schon hast"), die
   (a) die Frage genau so baut wie `ask` — dieselbe Momentaufnahme, derselbe
   Fingerabdruck, **derselbe** Generationszaehler, hochgezaehlt;
   (b) im Cache nachsieht und einen Treffer **zurueckgibt**, ohne `ready`,
   ohne `started`, ohne etwas zu starten;
   (c) sonst wie heute den Zeitgeber armiert und `None` zurueckgibt.
   Das Teure (`frozen_inventory`, `inventory_fingerprint`) wird dabei
   **einmal** getan, nicht zweimal: es liegt in einer gemeinsamen privaten
   Stelle, die `ask` und die neue Methode teilen. **Die Advisor bar ruft
   weiter `ask` und ist damit nachweislich unveraendert.**
4. **Der Generationszaehler laeuft auch fuer die sofort beantwortete Frage
   hoch.** Sonst kann eine Antwort aus einer frueheren Oeffnung, die noch
   unterwegs ist, den Cache-Treffer auf dem Bildschirm ueberschreiben.

**Konsequenzen.** *Leicht wird:* der Picker antwortet im teuersten gemessenen
Fall in 318,1 ms statt in gerechneten 418,1 ms; ein Cache-Treffer kostet
nichts und zeichnet **einen** Anstrich, wie `UI_SPEC` §2 es verlangt.
*Dauerhaft schwer wird:* der Picker hat zwei Wege, eine Antwort zu bekommen —
Rueckgabewert und Signal —, und ein `developer`, der nur einen baut, faellt
nicht auf. Dagegen steht **W5**.

**Umkehrbarkeit: leicht.** Zwei Konstanten und eine Methode; der Rueckbau ist
ein Tag und beruehrt keine Datenform.

---

### IX-2 — Die Picker-Spur fragt unter einer **kanonischen** Zielrichtung; die gewaehlte Richtung ist Sache der Anzeige

**Kontext.** AD-028 Punkt 3 sagt „keine zweite Schluesselform". **Die
Randbedingung dieser Aussage war der Slot-Index** — geprueft an der Frage, ob
`AdvisorRequest` ein neues Feld braucht. Auf das Feld `goal_id` desselben
Schluessels trifft sie nicht zu, und genau das ist hier der Fall: nach IX-0
haengt der **Inhalt** eines Pools nicht an der Zielrichtung, sein
**Schluessel** aber schon (`run.cache_key`, `run.py:170-180`).

**Optionen:**

- **A — im Bestand bleiben.** Die Picker-Spur fragt mit der gewaehlten
  Richtung. Konsequenz: derselbe Pool wird unter zwei Schluesseln zweimal
  gerechnet und zweimal abgelegt; die gemessene Spur „Zielrichtung
  umschalten" (8 Fragen, 2 verschiedene) bleibt genau deshalb eine Spur.
  Und: `Ranking.goal_id` (= `pool.rank_by`) liefert **zufaellig meistens** die
  richtige Richtung — der Fehler, gegen den AK-205 geschrieben ist, waere
  unregelmaessig und damit schwer zu fangen.
- **B — die Picker-Spur fragt immer unter derselben, festen Richtung**, und
  die Anzeige nimmt ihre Richtung aus der einen Einstellung des Programms
  (AK-43, AK-205). Konsequenz: ein Eintrag bedient beide Richtungen; die Zahl
  der Picker-Schluessel halbiert sich; das Feld `goal_id` der Picker-Anfrage
  sagt nicht mehr, was der Spieler gewaehlt hat.

**Entscheidung: B.**

**Verbindlich:**

1. Die Anfrage der Picker-Spur traegt in `goal_id` eine **benannte Konstante
   der Picker-Spur**, nicht die Einstellung des Spielers. Sie muss an ihrer
   Definition sagen, dass sie eine Ordnung ist und keine Wahl. Als Wert bietet
   sich der erste Eintrag von `advisorbar.GOAL_ORDER` an, damit die Ordnung im
   Pool die haeufigste bleibt; der Wert ist frei, die **Festigkeit** ist der
   Punkt.
2. **D-4 bleibt wahr, nicht ausgehebelt.** `SlotPool.rank_by` sagt weiterhin,
   was diese Liste geordnet hat — die Liste **ist** so geordnet. Was nicht mehr
   gilt, ist der stille Kurzschluss „was geordnet hat, ist auch, was gelesen
   wird". Genau den verbietet AK-205.
3. **Der Fehler wird dadurch regelmaessig statt zufaellig** — das ist ein
   Vorteil und der eigentliche Grund fuer B: wer AK-205 nicht baut, zeigt
   **immer** die kanonische Richtung an, nicht nur manchmal. Der Gegenbau
   beisst (L-008a).
4. **`run`s Ablehnungspruefung wird nicht beruehrt:**
   `_refuse_a_request_that_asks_about_another_run` (`run.py:241-283`) prueft
   `goal_id` **nicht** — der Kontext traegt keine Richtung. Geprueft, nicht
   vermutet.
5. **Nur die Picker-Spur.** Die Advisor bar fragt weiter unter der gewaehlten
   Richtung: ihre Antwort (`AdvisorResult`) **haengt** an ihr — sie traegt
   `goal_id`, `goal_label`, eine nach dieser Richtung gebaute Vorschlagsliste
   und deren Begruendungen (`types.py:604-649`).

**Konsequenzen.** *Leicht wird:* ein Richtungswechsel kostet nie wieder eine
Rechnung, weder im offenen Dialog noch ueber Oeffnungen hinweg. *Dauerhaft
schwer wird:* ein Feld der Picker-Anfrage sagt etwas anderes, als sein Name
nahelegt; wer die Picker-Anfrage einmal an etwas uebergibt, das `goal_id` als
„die Richtung des Spielers" liest, baut einen stillen Fehler. Heute gibt es
diesen Leser nicht (die Picker-Antwort ist ein `SlotPool` und traegt kein
`goal_label`), und **W1** haelt fest, dass es bei einem Aufrufer bleibt.

**Umkehrbarkeit: leicht** — eine Konstante zurueck auf die Einstellung.

---

### IX-3 — Die 64 bleibt stehen, ihre Herleitung deckt die neue Antwortform nicht; U7 misst nach

**Der Fund.** AD-028 Punkt 2 bemisst die beiden Caches mit **33,4 KiB**
(Picker) gegen **279,9 KiB** (Gesamtlauf) und begruendet den Sprung von 32 auf
64 mit „+41 Treffer (+16,5 s) fuer +1,05 MiB" (T-118 Abschnitt 3.2, S11-F).
Die 33,4 KiB sind gemessen an einer **`AdvisorResult` mit 20 Suggestions**
(S11-F woertlich: *„Picker-Antwort mit 20 Vorschlaegen"*). Die Antwortform,
die AD-028 der Picker-Spur gibt, ist eine andere: **der ganze `SlotPool`, alle
206 Kandidaten mit je zwei `Marginal`** — AD-028 sagt das selbst in seiner
Kraeftetabelle (*„der Picker braucht den ganzen Pool"*). Eine `AdvisorResult`
traegt den Pool nicht (`types.py:604-649`: `suggestions`, `baseline`, `gain`,
`held`, `unknowns`, …). **Die Zahl gilt fuer eine Antwortform, die die
Picker-Spur gerade nicht traegt.** Das ist zum dritten Mal in diesem Vorhaben
dieselbe Bauart von Fehler: eine Zahl, deren Grundgesamtheit eine andere ist
als die des Satzes daneben (QA-208, QA-209).

**Der zweite Riss in derselben Herleitung:** die Trefferquoten stammen aus
Spuren, in denen jeder Slot **zweimal** vorkommt, einmal je Richtung — die
tragende Spur heisst woertlich „beide Ziele x 6 Slots x 4 Zustaende" (60
Fragen, 42 verschieden). Nach IX-2 gibt es diese Doppelung nicht mehr;
dieselbe Bedienung stellt dann rund 30 Fragen mit rund 21 verschiedenen
Schluesseln und passt in 32. Ob der Knick bei 64 bleibt, entscheidet die
**andere** tragende Spur („Level-Schieber weit 15-5-15", 126 Fragen, 66
verschieden) — und ob deren Schluessel richtungsbehaftet sind, geht aus T-118
nicht hervor.

**Entscheidung: die 64 bleibt — und bekommt eine Messauflage mit
Rueckfallschranke.** Ich ersetze eine gemessene Zahl nicht durch eine
geschaetzte.

1. **U7 misst die Groesse eines Picker-Cache-Eintrags in der neuen
   Antwortform** (`SlotPool`, weisser Slot, 206 Kandidaten), mit derselben
   tiefen Zaehlung und derselben Umgebung wie S11-F, und schreibt S11-F fort.
2. **Rueckfallschranke, mit Rezept:** die Entscheidung fuer 64 wurde auf
   `64 x 33,4 KiB = 2,09 MiB` getroffen — 4,4 % des gemessenen
   Grundverbrauchs von 47,7 MiB (S11-F). Der Wert, den AD-028 selbst als
   „nicht billig" fuehrt, ist die **8,75 MiB** des Gesamtlauf-Falls. Daraus
   die Schranke: `8,75 MiB / 64 = 140 KiB` je Eintrag. **Misst U7 mehr als
   140 KiB, faellt die Picker-Spur auf 32 zurueck und die Groessenfrage kommt
   zurueck zu mir** — dann ist es eine Entscheidung zwischen Speicher und
   Trefferquote, keine Nachbesserung.
3. **U7 misst die Trefferquote der beiden tragenden Spuren aus T-118
   Abschnitt 3.2 unter dem Schluessel nach IX-2** (ohne Richtung). Faellt der
   Knick bei 64 weg, ist 32 die richtige Zahl und spart 1,05 MiB.
4. Bis diese beiden Messungen vorliegen gilt: **die 64 ist gesetzt, ihre
   Begruendung ist es nicht.** Wer sie zitiert, zitiert diesen Absatz mit.

---

### IX-4 — AD-028 Punkt 4 nachgezogen, W3 neu gegruendet, W4 und W5 dazu

**Punkt 4 verliert seinen ersten Fall.** Der Text nennt zwei Faelle, in denen
der Generationszaehler im Picker gebraucht wird. Der erste — *„der offene
Dialog rechnet beim Wechsel der Zielrichtung neu (`1169-1171`)"* — **entfaellt
ersatzlos**: nach IX-0 und `UI_SPEC` AK-204/AK-206 ist der Wechsel keine Frage
mehr, und `_sort_chosen` ruft `advice.ranking` nicht mehr auf. Der zweite —
*„der Dialog kann geschlossen werden, waehrend eine Antwort unterwegs ist"* —
**bleibt**, und ein dritter kommt hinzu:

3. **Zwei Oeffnungen hintereinander an einer Spur.** Die Spur lebt am Fenster
   (AD-028.5). Wird Slot A geoeffnet und geschlossen, bevor seine Antwort da
   ist, und danach Slot B geoeffnet, dann trifft As Antwort ein, waehrend Bs
   Dialog steht. Ohne Zaehler traegt Bs Raster As Zahlen — dieselben Karten,
   plausible Werte, kein Fehler, den irgendjemand sieht.

**Der Zaehler bleibt noetig; AD-028 Punkt 4 kippt nicht.** Was kippt, ist
seine Begruendung zur Haelfte — und mit ihr die Vorrichtung von W3.

**W3 neu.** Der alte Wortlaut stellt die zweite Frage durch einen **Wechsel
der Zielrichtung**. Diesen Fall gibt es nicht mehr; ein Test, der ihn
herstellen will, muss `advice.ranking` von Hand aufrufen und prueft dann eine
Bedienung, die es nicht gibt — gruen, ohne etwas zu belegen (L-008b).
**Neue Fassung:**

> **W3 — die ueberholte Antwort erreicht nichts.** Zwei Fragen an **einer**
> Picker-Spur, gestellt durch **zwei Oeffnungen zweier Slots**; die Antwort
> der ersten wird **nach** der zweiten Frage zugestellt. Auf dem Bildschirm
> steht die zweite, und die erste hat kein Widget angefasst.
> *Toetende Mutation:* die Generationspruefung in `_on_ready` ausbauen → rot.
> *Zweite Vorrichtung fuer denselben Waechter, weil sie den ueberlebenden Fall
> abdeckt:* die Antwort trifft ein, **nachdem** der Dialog geschlossen wurde —
> nichts wird angefasst, nichts wirft.

**W4 — neu, haelt die Randbedingung aus IX-0.** `advisorbar.GOAL_ORDER` (was
der Picker zeichnet) ist eine Teilmenge der Schluessel von
`advisor.goals.GOALS` (was der Pool bewertet). Ein reiner Struktur-Test, ohne
Fenster.
*Toetende Mutation:* eine dritte Id in `GOAL_ORDER` eintragen, ohne sie in
`GOALS` einzutragen → rot. **Ohne diesen Waechter ist die ganze
Wiederverwendung aus IX-0 eine Annahme ueber zwei Dateien, die niemand
zusammenhaelt.**
*Bau-Konfiguration (L-004):* keine — ein reiner pytest-Test, den kein
Buildsystem-Schalter aktiviert; das ist die Herleitung der Unnoetigkeit, nicht
ihr Fehlen.

**W5 — neu, haelt IX-1 Punkt 3.** Eine Spur, deren Cache die Antwort schon
haelt: der Dialog baut sein Raster **genau einmal** und trug zu keinem
Zeitpunkt `PENDING`. Gezaehlt wird der Bau des Rasters (Signalvorrat plus
Zaehlbeleg nach L-002), **nicht** die Zeit — keine Wanduhr.
*Toetende Mutation:* den Cache-Treffer wieder ueber den Zeitgeber und das
Signal leiten → zwei Anstriche → rot.
*Gegenprobe im selben Test:* dieselbe Spur ohne Cache-Eintrag baut das Raster
**zweimal**. Ohne diese Gegenprobe waere auch ein Raster gruen, das nie neu
gebaut wird.

**Ein ueberlebender Gegenbau ist ein Befund** und wird berichtet, nicht
stillschweigend nachgebessert (L-008c). Das gilt fuer W3 bis W5 wie fuer W1
und W2.

---

### IX-5 — Vorwaermen: **Backlog-Vorschlag**, weder Ersatz fuer AD-028 noch Zusatz zu ihm

Der `ui-ux-designer` haelt `candidates.pools()` beim Oeffnen des Build
planners fuer „die eigentliche Loesung". **Entschieden: nein — aus vier
Gruenden, von denen der erste die Frage selbst korrigiert.**

1. **Das genannte Mittel rechnet etwas anderes.** `candidates.pools()` liefert
   **einen Pool je freiem Slot** (`candidates.py:337-350`), und jeder davon
   wird gegen einen Grundzustand gerechnet, in dem **die uebrigen freien Slots
   leer sind** — `base_state_for` gibt fuer einen bereits freien Slot
   `problem` unveraendert zurueck (`candidates.py:61-79`, Docstring woertlich:
   *„For a slot that is already free this is `problem` unchanged, which is the
   Optimize case"*). Die Picker-Frage ist die umgekehrte: **jeder Slot ausser
   dem geoeffneten ist gehalten, mit seinem heutigen Inhalt** (AD-018.1,
   `relicpicker.py:318-322`). In dieser Form ist `free_slots(problem)` **leer**
   und `pools()` gaebe `()` zurueck. Vorwaermen fuer den Picker heisst also
   **sechs einzelne `pool`-Aufrufe**, nicht einen `pools()`-Aufruf.
2. **Der Preis ist damit die Summe, nicht der teuerste Slot:** gemessen
   **610,7 ms** fuer alle sechs Slots (S11-C, Median n=25, Spanne
   577,7–655,2 ms, `76f1887`, Ryzen 7 5800H bei 1102 von 3201 MHz) — gegen
   einen Gewinn von hoechstens 318,1 ms **einmal**, denn der Spieler oeffnet
   einen Slot, nicht sechs. Und dieser Vorrat verfaellt bei **jeder**
   Aenderung an Build, Level, Waffe, Nightfarer oder Haltezustand; wie oft das
   ist, steht in T-118: die Spur „Level-Schieber weit 15-5-15" zaehlt 126
   Fragen ueber 66 verschiedene Zustaende.
3. **Es waere eine dritte rechnende Spur, bevor die zweite gemessen ist.**
   Unter dem GIL teilen sich rechnende Python-Threads einen Kern; `Optimize`
   liegt gemessen bei 5023,6 ms gegen A6s 6-s-Schranke, also 19 % Luft, und
   die Ueberlappung **zweier** Spuren ist bis heute nicht gemessen (OF-25).
   Eine dritte hinzuzufuegen, bevor OF-25 beantwortet ist, ist Architektur auf
   Vorrat gegen ein Budget, das schon knapp ist.
4. **Ein warmer Vorrat verdraengt kalte Treffer.** Sechs vorgewaermte
   Eintraege je Buildzustand laufen durch denselben LRU wie die Antworten auf
   Fragen, die der Spieler wirklich gestellt hat. Der gemessene Nutzen des
   Caches (30 % ueber Dialoggrenzen) haengt daran, dass alte **echte** Fragen
   drinbleiben. Das ist kein Nebeneffekt, sondern eine Wechselwirkung mit
   AD-028 Punkt 2 und mit IX-3.

**Und es ist nicht noetig:** mit IX-1 antwortet der teuerste gemessene Slot in
318,1 ms gegen A6s 500-ms-Median. Vorgewaermt wuerde ein Wert optimiert, der
in seinem Budget liegt.

**Als Backlog-Vorschlag aufgenommen, mit der Bedingung, unter der er wieder
interessant wird** (fuer den `director`, von mir nicht eingeplant): *wenn U7
den Hauptthread-Rest (OF-26) oder die Ueberlappung (OF-25) so misst, dass eine
Slot-Frage im Median ueber 500 ms liegt.* Die dann billigere Form ist **nicht**
`pools()`, sondern **ein** `pool`-Aufruf fuer den Slot, den der Spieler zuletzt
offen hatte — ein Eintrag, 32 bis 318 ms, kein Verdraengen.

---

### Nachtrag X 2026-09-08 — Was der Vertrag des `AdvisorController` wirklich zusagt (drei Nachtraege zu AD-028, **keine neue AD-Nummer**)

**Anlass:** Der `developer` hat beim Bau der Waechter (U6, T-131) drei Punkte
gemeldet und **nicht behoben**, wie beauftragt. Alle drei betreffen denselben
Gegenstand: die Zusage im Klassen-Docstring des `AdvisorController` und die
Frage, wo sie getragen wird. Der `director` hat sie als T-134 gebuendelt
hierher gegeben.

**Quellen und was ich selbst geprueft habe.** `docs/berichte/T-131-developer.md`
(Befunde 1 und 2, Abschnitt „Zwei Entscheidungen, die nicht meine sind"),
`docs/tasks/T-131.md` (W6 und W7, vom `director` entschieden),
`tests/test_picker_track_guards.py`, `tests/picker_track.py`. **Jede tragende
Aussage unten ist am Stand `0128971` an einer benannten Zeile nachgeprueft**,
nicht aus dem Bericht uebernommen; `nrplanner/advisor/worker.py` ist seit
`1a2cc5b` (U5b) unveraendert, der Bericht und dieser Nachtrag lesen also
dieselbe Datei. Gemessen wird hier nichts.

**Buchfuehrung:** dieser Nachtrag vergibt **keine** AD-Nummer, er schreibt
AD-028 fort. Neu vergeben werden **ein** Waechter (**W8**) und **eine** offene
Frage (**OF-30**); die Umsetzungsschritte heissen **U9** und **U10** (U8 ist
AD-029 Stufe B und bleibt es).

*Zum W-Kreis, damit es nicht noch einmal jemanden kostet:* **`W6` steht in
dieser Datei fuer zwei verschiedene Dinge** — die Fassaden-Kette aus AD-019
(`W0` bis `W6`, „`MULTIPLIERS_FOR[Basis.CANDIDATE]` setzen", Zeile 1835 und
2662) und die Waechter der Picker-Spur (`W1` bis `W7`, AD-028 und Nachtrag
IX). Die Kollision besteht seit T-131 und ist mit `W8` nicht schlimmer
geworden, aber auch nicht besser. Ein Praefix (`AW-1` fuer die Waechter) waere
die Loesung; sie beruehrt Testnamen und Berichte und ist deshalb **eine
Entscheidung des `director`**, nicht meine. Bis dahin gilt: ein `W`-Zitat
nennt die Entscheidung dazu.

---

### X-0 — Die Zusage, praezise: sie gilt fuer die Frage, die beim Ende noch die aktuelle ist

**Der heutige Wortlaut** (`nrplanner/advisor/worker.py:200-201`, woertlich):

> „The window asks with `ask` and hears back on exactly one of `ready`,
> `failed` and `stopped`."

**Er ist nicht bloss ungenau, er ist zweideutig — und in einer der beiden
Lesarten falsch.** Gelesen als *„das Fenster hoert je Frage genau einen
Ausgang"* ist er schon fuer den gewoehnlichen Fall falsch, den AD-006 Punkt 3
ausdruecklich baut: eine ueberholte Frage endet **wortlos**, und das ist der
Zweck des Generationszaehlers. Gelesen als *„das Fenster hoert fuer die Frage,
die gerade gilt, genau einen Ausgang"* stimmt er — und trug bis U5b, als `ask`
der einzige Weg hinein war. **Seit U5b gibt es einen zweiten Weg hinein**
(`ask_and_answer_if_known`, IX-1.3), dessen Treffer die Antwort als
**Rueckgabewert** liefert und ausdruecklich **kein** Signal sendet
(`worker.py:288-290`, woertlich: *„A hit comes back as the return value and
**only** as the return value: no `ready`, no `started`, and nothing started"*).
Die Ausnahme steht also bereits in der Datei — im Docstring der Schwester,
nicht in der Zusage, die sie einschraenkt. Das ist genau die Bauform, an der
AD-018 gescheitert ist: **zwei Texte ueber dieselbe Sache, die nicht
zusammengelesen werden.**

**Entschieden: die Zusage wird praezisiert, und ihre Ausnahmen werden
aufgezaehlt** — je Ausnahme mit der Entscheidung, die sie traegt. Verbindliche
Fassung (Docstring, Englisch nach Projektsprache):

```
The window asks with `ask` and hears back on exactly one of `ready`,
`failed` and `stopped` -- for the question that is still the current one
when it ends. Three things end a question without any of the three, and
each of them is a decision rather than a gap:

* **an overtaken question.** A later asking has raised the generation, and
  the earlier answer is dropped without a word (AD-006 point 3); the later
  question is the one that will be answered.
* **a hit in `ask_and_answer_if_known`.** The answer goes back as the
  return value and nothing is emitted, so that a known answer can be drawn
  in the first paint rather than one turn of the event loop later
  (Nachtrag IX-1.3).
* **`shutdown`.** The window is closing. Nothing is emitted, and nothing
  will be: the generation goes up here as it does in `cancel`, so an
  answer already on its way cannot arrive after the wait (Nachtrag X-1).
```

**Randbedingung dieser Fassung, benannt:** sie gilt fuer **beide** Instanzen
(AD-028 Option D — nichts in der Klasse fragt, welche Spur sie ist). Der
dritte Punkt setzt den Fix aus X-1 voraus; ohne ihn waere er eine Zusage ueber
einen Wettlauf.

---

### X-1 — `shutdown()`: der Text wird praezisiert, **und** das Schweigen wird zur Eigenschaft gemacht (Punkt 1)

**Der Befund haelt, und er traegt weiter, als er gemeldet wurde.**
`shutdown` (`worker.py:371-383`) leert `_pending`, stoppt den Zeitgeber,
unterbricht den Worker und wartet — und sendet keines der drei Signale. So
weit der Bericht.

**Was er nicht nennt, ist die Randbedingung seines eigenen „im Betrieb
harmlos":** `shutdown` ist die **einzige** der vier unterbrechenden Stellen,
die den Generationszaehler **nicht** erhoeht (`cancel` tut es in Zeile 351,
`_wait_for` und `ask_and_answer_if_known` ueber `_question_from`, Zeile 322).
Damit ist der Ausgang nach `shutdown` nicht „Schweigen", sondern
**unbestimmt**: hat der Worker seine Antwort abgeschickt, **bevor** er die
Unterbrechung bemerkt hat, liegt ein `ready` in der Warteschlange des
Hauptthreads; `thread.wait()` verarbeitet sie nicht, und `_on_ready`
(`444-456`) findet die Generation unveraendert und **sendet** `ready` — nach
`closeEvent`. Ob das eintritt, haengt daran, ob sich die Ereignisschleife
zwischen dem `emit` des Workers und dem Ende des Prozesses noch einmal dreht;
`app.py:2039-2041` ruft `shutdown_the_advisor()` und danach
`super().closeEvent(event)`, das Beenden der Anwendung ist selbst ein
gebuchtes Ereignis.

**Hergeleitet, nicht gemessen** (L-001): ich behaupte nicht, dass es im Feld
vorkommt. Ich behaupte, dass die Klasse es nicht ausschliesst — und dass **ein
Waechter fuer den Fall sonst ein Wettlauf waere**, also kein Waechter.

**Optionen:**

- **A — im Bestand bleiben, nur den Text praezisieren.** Konsequenz: Text und
  Verhalten stimmen wieder ueberein, aber die Zusage lautet dann „nach
  `shutdown` kommt **meistens** nichts". Eine Zusage mit „meistens" ist keine.
  **Verworfen** — sie waere nicht bewachbar, und ein W6-Fall darueber waere
  flatterhaft gruen.
- **B — `shutdown` sendet `stopped`.** Konsequenz: `stopped` ist nach
  `UI_SPEC` 4.5 und AK-11 ein **Satz an den Spieler** (*„Stopped. Nothing was
  changed."*), und `advisorbar` zeichnet darauf Zustand 4.5 — in ein Fenster,
  das gerade verschwindet. Das Signal bekaeme zwei Bedeutungen („der Spieler
  hat abgebrochen" und „das Programm endet"), und beide Spuren muessten die
  zweite unterscheiden. **Verworfen.**
- **C — die Ausgaenge buendeln:** `_interrupt_the_running_worker` bekommt ein
  Argument „was die abgehende Frage hoert", damit keine Stelle mehr
  versehentlich schweigen kann. Konsequenz: die richtige Form, wenn es einmal
  fuenf oder sechs Stellen sind; heute vier Aufrufer umbauen, um eine
  Eigenschaft zu erzwingen, die X-2 auch zaehlend haelt. **Verworfen als
  Architektur auf Vorrat**; *wieder interessant, wenn* W8 (X-2) zum zweiten
  Mal wegen einer neuen Aufrufstelle rot wird.
- **D — A plus eine Zeile: `shutdown` erhoeht die Generation wie `cancel`.**
  Konsequenz: das Schweigen ist eine **Eigenschaft** statt eines Wettlaufs,
  die vier unterbrechenden Stellen verhalten sich gleich, und der W6-Fall
  darueber ist deterministisch schreibbar.

**Entscheidung: D.** Der Docstring bekommt die Fassung aus X-0, und
`shutdown` erhoeht den Zaehler, bevor es unterbricht.

**Das ist Anwendungscode — also ein Fixauftrag, kein Vollzug** (T-134,
Vorgabe 3). Er steht als **U9** unten.

**Konsequenzen.** *Leicht wird:* jede unterbrechende Stelle folgt derselben
Regel („wer unterbricht, erhoeht"), und die Zusage aus X-0 ist ohne „meistens"
formulierbar. *Dauerhaft schwer wird:* nichts — nach `shutdown` gibt es keine
Frage mehr, deren Generation noch jemand liest. *Nicht beruehrt:*
`_on_ready` legt die Antwort weiter **vor** der Generationspruefung in den
Cache (`453`); das bleibt richtig (AD-007) und ist nach `shutdown` folgenlos,
weil der Cache mit der Instanz stirbt.

**Umkehrbarkeit: leicht.** Eine Zeile hin, eine zurueck; der Docstring haengt
daran und waere mitzunehmen.

---

### X-2 — `search.Cancelled` ist kein Ausgang, sondern eine Quittung — und „haelt ueber drei Aufrufer" ist **keine** bewachbare Zusage (Punkt 2)

**Der Befund haelt; seine Zahl haelt nicht.** `_Worker.work` faengt
`search.Cancelled` und sendet nur `finished` (`worker.py:186-187, 194`).
Erreichbar ist das, nachdem `requestInterruption()` gelaufen ist — und
`slot_pool` kann es tatsaechlich ausloesen: es reicht `should_cancel` an die
Vorsortierung durch, die einmal je angebotenem Relikt fragt
(`run.py:463-464`), und geworfen wird in `search.py:327`. Der Weg ist also auf
**beiden** Spuren offen, nicht nur auf der des Gesamtlaufs.

**Aufrufer von `_interrupt_the_running_worker` sind vier, nicht drei.**
Gezaehlt am Stand `0128971`, `worker.py`: Zeilen **309**
(`ask_and_answer_if_known`, Cache-Treffer), **334** (`_wait_for`), **354**
(`cancel`), **380** (`shutdown`); Definition in 387. Die vierte ist keine tote
Stelle: der Picker ruft `ask_and_answer_if_known` bei **jeder** Oeffnung
(`relicpicker.py:413-415`), und ein Treffer ist der gemessen haeufige Fall
(30 % der Oeffnungen, S11-F).

**Das ist die Antwort auf die gestellte Frage.** „Die Zusage haelt ueber drei
Aufrufer" ist als **Verhaltenszusage nicht bewachbar**: sie behauptet etwas
ueber das *Komplement* einer Menge von Aufrufstellen — dass es keine fuenfte
gibt, die schweigend unterbricht —, und kein Fall, den man abspielen kann,
zeigt die Abwesenheit einer Stelle, die niemand geschrieben hat. **Der Beleg
dafuer ist die Aussage selbst:** sie wurde am 08.09.2026 mit „drei"
aufgeschrieben, waehrend die vierte Stelle seit `1a2cc5b` (U5b, derselbe Tag)
im selben File stand. Eine Zusage, deren Zaehlung am Tag ihrer Niederschrift
falsch ist, gehoert nicht in Prosa.

**Bewachbar ist sie als Struktur** — dieselbe Form wie W1: eine Tabelle
erlaubter Stellen **im Test**, nicht abgelesen aus der bewachten Datei
(L-008b). Verbindlich ist damit **nicht** „drei Aufrufer", sondern:

> **Jede Stelle, die einen laufenden Worker unterbricht, sagt, was die
> abgehende Frage hoert** — entweder sie sendet in derselben Aufrufung einen
> der drei Ausgaenge, oder sie stellt in derselben Aufrufung eine
> Nachfolgefrage, die ihn senden wird, oder sie beendet die Spur ganz.

| Stelle | `worker.py` | was die abgehende Frage hoert |
|---|---|---|
| `cancel()` | 354 | **`stopped`**, in derselben Aufrufung (AK-11) |
| `_wait_for()` | 334 | nichts — die **Nachfolgefrage** ist jetzt die aktuelle und endet in genau einem der drei |
| `ask_and_answer_if_known()`, Treffer | 309 | nichts — die Antwort ging in derselben Aufrufung als **Rueckgabewert** zurueck (IX-1.3) |
| `shutdown()` | 380 | nichts, und danach nichts mehr (X-1) |

**Verworfen: `_Worker.work` sendet `stopped`, statt `Cancelled` still zu
schlucken.** Das ist der naheliegende Fix und er ist falsch: nach `cancel()`
haette die Frage dann **zwei** `stopped` — eines aus der Aufrufung, eines aus
dem Worker —, und „genau einer der drei" waere gebrochen, um „genau einer der
drei" herzustellen. Der Worker kann nicht wissen, wer ihn unterbrochen hat;
die Zusage gehoert deshalb dorthin, wo es jemand weiss.

**W8 — neu: die unterbrechenden Stellen sind gezaehlt und benannt.** Ein
reiner Struktur-Test ueber `nrplanner/advisor/worker.py`: die Aufrufstellen
von `_interrupt_the_running_worker` werden ueber den Syntaxbaum gezaehlt und
gegen eine **im Test stehende** Tabelle (Methodenname → welcher Ausgang, mit
Begruendung) verglichen, Mengengleichheit in beide Richtungen.
*Toetende Mutation:* eine fuenfte Stelle einsetzen — z. B. in
`before_the_data_changes` `self._interrupt_the_running_worker()`
**zusaetzlich** zu `self.cancel()` — → rot, weil die Menge der Stellen die
Tabelle verlaesst.
*Zweite Mutation, die die andere Richtung deckt:* den Aufruf in `cancel`
entfernen → rot (die Tabelle nennt eine Stelle, die es nicht mehr gibt).
*Bau-Konfiguration (L-004):* keine — ein reiner pytest-Test, den kein
Buildsystem-Schalter aktiviert; das ist die Herleitung der Unnoetigkeit, nicht
ihr Fehlen.
*Nachweisweg nach L-002:* Gegenbau (die beiden Mutationen oben).

**Was W8 nicht kann, ausdruecklich:** er prueft die **Zahl und die Namen** der
Stellen, nicht ihr Verhalten. Dass `cancel` wirklich `stopped` sendet, haelt
W6; dass die Nachfolgefrage wirklich antwortet, halten W6 und W3. W8 ist der
Waechter darueber, dass diese drei Waechter **vollstaendig** sind — und genau
das war die Luecke, die „drei Aufrufer" nicht schliessen konnte.

**Umkehrbarkeit: leicht** — ein Test, der geloescht werden kann. Der Preis des
Behaltens ist eine Tabellenzeile je neuer Aufrufstelle, und diese Zeile zu
schreiben ist genau die Ueberlegung, die hier gefehlt hat.

---

### X-3 — W1 erlaubt drei Aufrufstellen: **so ist es gemeint.** Der Wortlaut von AD-028 wird nachgezogen (Punkt 3)

**Geprueft, nicht uebernommen.** Die drei Stellen stehen so in
`tests/test_picker_track_guards.py:73-88` (`MAY_REACH_THE_CALCULATION`), und
die beiden zusaetzlichen sind am Quellstand belegt: `app.py` **nennt**
`run.slot_pool` bei der Konstruktion der zweiten Instanz und ruft es nirgends
auf (AD-028 Option D verlangt genau das); `run.py` ruft `candidates.pool`,
weil `slot_pool` die Pool-Funktion **ist**. Beides konnte nach AD-028 gar
nicht woanders liegen.

**Der Wortlaut steht gegen den gebauten Zustand, also wird er nachgezogen —
sichtbar, mit beiden Fassungen.**

> **Fassung 1 (AD-028, Nachtrag VIII, 08.09.2026 — bleibt woertlich stehen):**
> „**W1 — strukturell.** Keine Datei unter `nrplanner/` ausser
> `advisor/worker.py` ruft `run.run`, die neue Pool-Funktion oder
> `candidates.pool` auf."

> **Fassung 2 (Nachtrag X, 08.09.2026 — verbindlich):** **W1 — strukturell.**
> Unter `nrplanner/` **nennt** keine Datei `run.run`, `run.slot_pool`,
> `candidates.pool` oder `candidates.pools` ausser diesen vier:
> `advisor/worker.py` → `run.run`; `app.py` → `run.slot_pool`;
> `advisor/run.py` → `candidates.pool`; `advisor/run.py` → `candidates.pools`.
> Kein Fenster, kein Dialog und kein Tab bekommt die Rechnung zu fassen — das
> ist die Sache, und sie ist unveraendert.

**Drei Aenderungen, jede mit Grund:**

1. **„nennt" statt „ruft auf".** Der gebaute Waechter zaehlt Nennungen, und
   das ist **strenger** und richtig: eine Referenz in `functools.partial` oder
   an einen Namen gebunden ist ein Aufruf einen Schritt spaeter. Fassung 1 war
   an dieser Stelle zu schwach, nicht zu streng.
2. **Die Pool-Funktion heisst jetzt.** „die neue Pool-Funktion" war
   geschrieben, bevor sie `run.slot_pool` hiess (U5a).
3. **`candidates.pools` (Mehrzahl) kommt in die Tabelle**, erlaubt nur in
   `advisor/run.py` (`run.py:379`, innerhalb von `run.run`). *Grund, und er
   ist kein Vorrat:* IX-5 hat genau diesen Weg als Vorschlag auf dem Tisch
   gehabt — der `ui-ux-designer` hielt `candidates.pools()` beim Oeffnen des
   Build planners fuer „die eigentliche Loesung", gemessene **610,7 ms**
   (S11-C) im Hauptthread. Der Vorschlag ist abgelehnt; ohne diese Zeile
   bewacht W1 die naechstgelegene Umgehung seiner selbst nicht.
   *Toetende Mutation dafuer:* `candidates.pools` in `app.py` nennen → rot.

**Verworfen: die Alternative des `developer`** (*„dann muesste die
Antwortfunktion der Picker-Spur ueber `worker.py` benannt werden"*, T-131,
Abschnitt „Zwei Entscheidungen"). Sie machte Fassung 1 woertlich wahr und
kostete den Kern von AD-028 Option D: `worker.py` wuesste dann, welche Spur
welche ist, waehrend der Klassen-Docstring zu Recht sagt *„Nothing here asks
which track it is"*. Die Verdrahtung gehoert an die Verdrahtungsstelle;
`app.py` **darf** nennen, was es zusammensteckt. **Kein Auftrag an den
`developer` fuer `app.py`.**

**Randbedingung von W1, die bisher nirgends stand:** der Waechter haengt an
`test_one_build.call_sites` und damit an **Modulkurzname plus Funktionsname**.
Er sieht die sieben Schreibweisen, die dort aufgezaehlt sind — nicht aber eine
Rechnung, die unter einem **anderen Namen** in den Hauptthread kaeme (etwa ein
direkter Griff in `search`). Das ist keine Luecke des Waechters, sondern seine
Grenze; wer eine neue rechnende Einstiegsfunktion baut, traegt sie in die
Tabelle ein. *Diese Bedingung gehoert in den Docstring der Tabelle* — Teil von
U10.

---

### Meldung an den `director`: **AK-218 ist im Wortlaut enger als der gebaute Zustand** — `UI_SPEC.md` habe ich nicht angefasst

AK-218 sagt woertlich: *„Jede Frage einer Oeffnung endet in genau einem von
drei Ausgaengen — `ready`, `failed`, `stopped` —, und jeder der drei fuellt
das Raster."* **Der haeufige Fall erfuellt das nicht:** trifft der Cache
(30 % der Oeffnungen, S11-F), endet die Frage im **Rueckgabewert** von
`ask_and_answer_if_known` und in keinem der drei Ausgaenge
(`relicpicker.py:413-417`, `worker.py:288-290`) — so von IX-1.3 entschieden
und von **AK-211** vorausgesetzt, das *„hoechstens zwei Zustaende"* sagt und
den einen Anstrich damit ausdruecklich erlaubt.

**Die Sache von AK-218 ist unberuehrt** — „ein Ausgang, der das Raster leer
laesst, ist ein Fehler" gilt weiter, und der Treffer fuellt das Raster sogar
im ersten Anstrich. **Betroffen ist nur der Wortlaut**, und zwar in derselben
Weise wie der von W1: geschrieben, bevor der zweite Weg hinein existierte.
**Vorschlag an den `ui-ux-designer`** (Spec ist gesetzt, ich aendere sie
nicht): *„… endet in genau einem von drei Ausgaengen — oder, wenn die Antwort
beim Fragen schon bekannt war, in dem einen Anstrich, den AK-211 erlaubt."*

*Warum es dem Waechter nicht aufgefallen ist:* W6 faehrt fuenf Vorrichtungen,
alle ueber `ask` (`tests/test_picker_track_guards.py:436-506`). Der zweite Weg
hinein kommt in keiner davon vor.

---

### AD-029 — Das Lesen des Spielstands wird **zuerst am Lesen selbst** repariert; die Verlagerung in einen Worker ist eine zweite Stufe, die an eine Messung mit benanntem Ausloeser haengt (2026-09-08, Status: aktiv; beruehrt AD-006.7, AD-006.8, SEC-022)

**Kontext — was die 6,15 s kosten, belegt an T-118 und `baselines.md`
S11-E:**

| Posten | Wert | Quelle |
|---|---|---|
| `inventory.load`, Hauptthread | **6147,6 ms** (p50, n=5, 6091,9–6299,4) | S11-E |
| davon Scan aller 14 Slots **einer** Datei | 2802,7 ms | S11-E |
| `savefile.read_owned_relics`, Eigenzeit, 28 Aufrufe | 6,562 s **unter cProfile** | S11-E |
| darin `struct.unpack_from` | **10 293 488** Aufrufe, 5,576 s **unter cProfile** | S11-E |
| Prozessstart gesamt | 6593,7 ms | S11-E |
| Obergrenze eines Gegenentwurfs (Vorfilter) | 14 Slots in **61,9 ms** statt 2802,7 = **45x** | S11-E |
| Verhaltensgleichheit des Gegenentwurfs | **28 von 28** Slots **beider** Spielstaende, mit Positivkontrolle | T-118 4/P2, 7 |

Die Ursache ist die Schleife `for off in range(0, len(slot_data) - 24, 4)` in
`nrdata/savefile.py`, die **jeden** 4-Byte-Versatz eines Slots anfasst.
Gelesen werden **28** Slots — zwei Spielstanddateien mit je 14 —, gebraucht
wird **einer**: `inventory.load` waehlt den bestbestueckten. Aufgerufen wird
das im Hauptthread bei jedem Start (`app.py:1575`) und bei jedem `Rescan`
(`app.py:1682`).

**Die 45x sind ein Faktor ueber den Scan, nicht ueber den Start — und das ist
die Verwechslung, die diese Entscheidung sonst falsch machen wuerde.**
Herleitung aus den Posten oben (L-001):

```
nicht im Scan (Entschluesseln, Records bauen, Loadouts):
    6147,6 - 2 x 2802,7 = 542,2 ms
nach dem Vorfilter:
    542,2 + 2 x 61,9    = 666,0 ms   ->  inventory.load rund 9,2x, nicht 45x
```

**Annahme darin, ausdruecklich benannt:** die zweite Spielstanddatei kostet so
viel wie die erste. Separat gemessen ist nur eine (2802,7 ms); die Summe passt
in das Ganze (5605 von 6148 ms = 91 %), belegt ist die Aufteilung nicht. Die
Zahl 666 ms ist damit **hergeleitet, nicht gemessen** — sie taugt zum
Entscheiden ueber die Reihenfolge, nicht als Abnahmewert.

**Optionen:**

- **A — im Bestand bleiben.** Der Nutzer hat am 08.09.2026 anders entschieden
  (QA-209 in den Fix-Stapel vor 1.8.0). **Entfaellt.**
- **B — nur verlagern**, das Lesen unveraendert in einen Worker. Konsequenz:
  6,15 s bleiben 6,15 s, nur woanders; der Start wird nicht schneller, nur die
  Fenstersperre beim `Rescan` verschwindet. Der groesste gemessene Hebel des
  Programms bliebe liegen, und der Umbau ist der teurere von beiden.
- **C — nur das Lesen.** Vollstaendig gemessen, eine Schleife, eine Datei,
  Verhaltensgleichheit an 28 von 28 Slots belegt. Restwert hergeleitet
  666 ms.
- **D — beides in einem Auftrag.**

**Entscheidung: C jetzt; B nur, wenn eine Messung es verlangt — also nicht
D.** C ist belegt und klein. B verlangt einen **dritten Fensterzustand**
(„wird gelesen"): `self.owned = None` heisst heute *„kein Spielstand
gefunden"* und ist der Satz, den der Spieler dann liest — ein Zustand
„noch nicht da" existiert nicht. Dazu kommen eine neue Thread-Grenze und eine
Ergaenzung der `UI_SPEC`. Das auf Verdacht zu bauen, bevor die Zahl nach C
bekannt ist, waere Architektur auf Vorrat.

**Der Ausloeser fuer Stufe B, benannt statt geschaetzt.** Nach C wird
`inventory.load` am echten Spielstand neu gemessen (`performance-tuner`,
Szenario S11-E, dasselbe Skript, dieselbe Umgebung, Vorher-Wert 6147,6 ms).
**Liegt der Median ueber 250 ms, wird B gebaut; darunter nicht.** Die 250 ms
sind nicht neu erfunden: es ist die Schwelle, die AK-09 bereits traegt fuer
„der Spieler bekommt keinen Wartezustand gezeigt", und ein **eingefrorenes**
Fenster ist strenger zu bewerten als eine rechnende Hintergrundspur. Nach der
Herleitung oben (666 ms) ist zu **erwarten**, dass der Ausloeser greift —
erwartet ist nicht gemessen, und die Reihenfolge kostet nichts, weil B ohnehin
auf C aufsetzt: B ohne C verlagerte 6,15 s, statt 5,5 s davon zu beseitigen.
Die `UI_SPEC`-Ergaenzung fuer den dritten Zustand kann parallel zu C
entstehen.

**Form von Stufe B, falls der Ausloeser greift — eingegrenzt, nicht
entworfen:**

1. **Die Thread-Grenze liegt zwischen Lesen und Bauen.** Der Worker liest die
   Datei, entschluesselt sie und scannt die Records; der Hauptthread baut aus
   den Records das `Inventory`. Damit bleibt **AD-006.8 unangetastet** — ueber
   die Grenze gehen nur unveraenderliche Datenklassen (`OwnedRelic` ist eine),
   nicht das lebende `Inventory` —, und die Grenze liegt genau um den gemessen
   teuren Teil.
2. **Kein Wartemuster aus `firstrun.py`** (AD-006.2): kein
   `processEvents`, keine modale Warteschleife.
3. **Die Cache-Entwertung wandert vom Beginn an die Ankunft.** Heute ruft
   `rescan_save` `advisor_bar.the_data_is_changing()` **vor** dem Lesen, was
   richtig ist, solange das Lesen synchron ist. Asynchron gilt der alte
   Bestand waehrend des Lesens weiter; entwertet wird in dem Moment, in dem
   `self.owned` ersetzt wird. (`rescan_save` ruft `model.configure` **nicht**
   auf — die Gefahr F4 aus AD-006.7 betrifft den Datenneuaufbau, nicht den
   Neu-Scan.)
4. **Ein Lesen zur Zeit** (AD-006.4 sinngemaess): ein zweiter `Rescan`-Klick
   waehrend eines laufenden Lesens startet kein zweites.
5. **Der dritte Fensterzustand ist Oberflaeche** und gehoert dem
   `ui-ux-designer`, nicht dieser Entscheidung.

**Die Vertrauensgrenze wird beruehrt — Fall fuer den `security-reviewer`.**
Der Vorfilter entscheidet, **welche** Versaetze ueberhaupt geprueft werden.
Drei Dinge folgen daraus:

1. Die Dichteschranke aus **SEC-022** (`MIN_BYTES_PER_RELIC_RECORD = 64`, der
   laute `raise` an dem Record, der die Linie ueberschreitet) zaehlt
   **gefundene** Records. Ein Filter, der weniger findet, verschiebt sie. Er
   darf sie nicht antasten.
2. Die Verhaltensgleichheit ist an **28 von 28 Slots zweier echter
   Spielstaende** belegt — also gerade **nicht** an der Dateiklasse, fuer die
   SEC-022 gebaut ist. Der `security-reviewer` hat aus T-096 eine praeparierte
   Datei (131 069 Records je MiB, Faktor 8 ueber der Schranke); die Gleichheit
   gehoert **auch dort** gezeigt, bevor der Fix als abgeschlossen gilt.
   Argument, das dafuer spricht und die Pruefung nicht ersetzt: ein Record
   verlangt `first == second` und `first >= RELIC_ID_FLAG`, traegt also
   zwangslaeufig das Byte, auf das der Filter vorsortiert.
3. Die tragende Annahme **`relic_id < 0x01000000`** (groesste Id im heutigen
   Datensatz: 2 013 322) ist eine Kopplung an die Spieldaten, die ein
   Spiel-Patch aendern kann. Sie gehoert als Pruefung in den Code, nicht als
   Kommentar daneben — laut werden, nicht still danebenliegen.

> **Punkt 3 ist abgeloest durch AD-031 (Nachtrag XI, 08.09.2026).** Die
> Annahme bleibt geprueft; „laut werden" heisst aber nicht mehr
> **verweigern** (so in T-133 gebaut, `savefile.py:237-246`), sondern
> **auf den langsamen Weg zurueckfallen und es in der Bestandszeile sagen**
> — Nutzerentscheid vom 08.09.2026, Wortlaut in `UI_SPEC` AK-228/AK-229.
> Die Punkte 1 und 2 gelten unveraendert. Wer Punkt 3 zitiert, liest
> AD-031 mit.

Der eigene Spielstand gilt seit 02.09.2026 als vertrauenswuerdig; ein
**heruntergeladener** bleibt die scharfe Grenze, und der Vorfilter laeuft auf
beiden.

**Der zweite Hebel, den T-118 dem `architect` ausdruecklich vorgelegt hat —
„28 Slots lesen, um einen zu benutzen; darf `load()` frueher aufhoeren?": Nein,
nicht anfassen.** Die Regel „der bestbestueckte gewinnt" ist gegen einen
realen Fall gebaut (zweites Steam-Konto, wiederhergestelltes Backup,
Ueberrest einer Neuinstallation) und steht als Begruendung im Docstring von
`load`. Nach dem Vorfilter kosten alle 28 Slots zusammen noch rund 124 ms von
666 ms. Eine Korrektheitsregel, die den **falschen** Spielstand waehlen kann,
gegen einen Bruchteil einer bereits behobenen Zeit zu tauschen, ist der
schlechteste Tausch im ganzen Befund. *Wieder interessant, wenn:* der
Vorfilter sich als unhaltbar erweist — dann ist ohnehin der `array`-Rueckfall
aus T-118 Abschnitt 6 dran (2,1x statt 45x), und die Frage stellt sich neu.

**Umfang in Dateien** (fuer den Schnitt der Auftraege, Obergrenze fuenf):

| Schritt | Rolle | Produktivdateien | Dazu |
|---|---|---|---|
| C — Vorfilter + Id-Pruefung | `developer` | **1** (`nrdata/savefile.py`) | Tests |
| Pruefung an der praeparierten Datei | `security-reviewer` | **0** (lesend) | — |
| Nachmessung, Ausloeser fuer B | `performance-tuner` | **0** (`docs/perf/baselines.md`) | — |
| B, falls ausgeloest | `developer` | **3** (`nrplanner/inventory.py`, ein neues kleines Qt-Modul fuer die Spur, `nrplanner/app.py`) | Tests, **nach** der `UI_SPEC`-Ergaenzung |

**Konsequenzen.** *Leicht wird:* der Programmstart faellt hergeleitet von
6,59 s auf rund 1,1 s, und das ist der groesste einzelne Hebel, den das
Programm hat. *Dauerhaft schwer wird:* der Scan wird eine Spur trickreicher,
und er traegt eine Annahme ueber die Spieldaten, die ein Patch brechen kann —
deshalb muss sie laut sein. Faellt Stufe B, kommt ein Fensterzustand dazu,
den es heute nicht gibt.

**Umkehrbarkeit.** C: **leicht** — eine Schleife, mit einem gemessenen
Rueckfallweg daneben. B: **mittel** — Zustand und Thread-Grenze zurueckzubauen
kostet mehr als sie zu bauen, und die `UI_SPEC` haette den Zustand dann zu
streichen.

---

---

## Themenbereich E — Daten lesen, Erststart, Pfade

*Wie das Programm an die Spieldaten kommt. AD-011 und AD-012 sichern das
Lesen; AD-030 und AD-031 tragen A15 — der Erststart bekommt einen Weg von
Hand, und der Vorfilter faellt zurueck, statt zu verweigern.*

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

### Nachtrag XI 2026-09-08 — Der Erststart bekommt einen Weg von Hand (AD-030), und der Vorfilter faellt zurueck statt zu verweigern (AD-031)

**Anlass, zwei getrennte:**

1. **A15** ist seit AK-106 bis AK-132 spezifiziert und **null Zeilen gebaut**
   (QA-199). Die Spec entscheidet die Oberflaeche vollstaendig; sie entscheidet
   **nicht**, wie der gemerkte Pfad die drei Datenverluste ueberlebt, gegen die
   OF-15 gebaut ist, und sie entscheidet nicht, **wer im Programm den
   Spielordner aufloest**. Beides gehoert hierher.
2. **AD-029, Vertrauensgrenze Punkt 3, ist ueberholt.** Gemeldet vom
   `ui-ux-designer` in T-141 (`UI_SPEC` §13). Der Nutzerentscheid vom 08.09.2026
   verlangt den Rueckfall auf den langsamen Weg statt der Verweigerung — und
   diesen langsamen Weg gibt es im Code nicht mehr.

**Buchfuehrung:** vergeben werden **AD-030** und **AD-031**, die offenen Fragen
**OF-31** und **OF-32**, und die Umsetzungsschritte **V1 bis V5** (der
`U`-Kreis ist mit U1–U10 belegt und wird nicht fortgesetzt, damit „U8"
eindeutig AD-029 Stufe B bleibt). **AD ab AD-032.**

---

### XI-0 — Was ich am Bestand nachgeprueft habe, statt es zu uebernehmen

Stand `a8d31bb`. Kein Lauf, keine Messung; alles gelesen.

| Aussage | Herkunft | Nachpruefung |
|---|---|---|
| „Der Code verweigert, statt zurueckzufallen" | T-141 | **haelt.** `nrdata/savefile.py:237-246`, `_check_the_prefilter_can_see_every_id`, Docstring *„Refuse to scan at all rather than scan half the ids"*, `raise ValueError`. Aufgerufen als erste Zeile von `read_owned_relics` (`:257`). |
| „Den langsamen Weg gibt es nicht mehr" | T-141 | **haelt**, mit zwei eigenen Suchen: `range(0, len(` ueber `nrdata/` und `nrplanner/` → 2 Treffer, beide fremd (`bhd5.py:68`, `relicpicker.py:1113`); `slow (way|path|scan)`, `fallback scan`, `every fourth`, `stride` → kein zweiter Versatz-Erzeuger fuer Relikte. Es gibt genau einen: `_relic_id_offsets`, `savefile.py:209`. |
| „kein `QFileDialog` in `nrplanner/`" | Auftrag, QA-199 | **haelt**, zwei Suchen: `QFileDialog|getExistingDirectory|getOpenFileName` ueber den ganzen Baum ausser `.venv` → **0 Treffer**; `choose folder|browse local files|find my save` → **0 Treffer**. Ebenso `paths/game|paths/save` → **0 Treffer**. |

**Was T-141 nicht gezaehlt hat und ich nachgezaehlt habe:** `nrdata/savefile.py`
traegt **zwei** Vorfilter, nicht einen — `_relic_id_offsets` (`:209`) und
`_loadout_marker_offsets` (`:388`, aus T-136). Ein Rueckfall wird trotzdem nur
an **einer** Stelle gebraucht, und der Grund steht im Code: der
Loadout-Vorfilter sucht `HERO_MARKER_BASE + 1`, eine **Programmkonstante**
(`savefile.py:380-385`), waehrend der Relikt-Vorfilter auf einer **Annahme
ueber die Spieldaten** steht (`RELIC_ID_CEILING`, `:197`). Nur die zweite kann
ein Patch still brechen. **Eins von zwei, mit Grund** — nicht „der Vorfilter".

**Was T-141 nicht wissen konnte und die Reihenfolge bestimmt:** U3 (T-140) hat
den Ausloeser fuer **AD-029 Stufe B** gemeldet — `inventory.load` **657,2 ms**
gegen die Schwelle 250 ms (`docs/perf/baselines.md`, Zeilen 191 und 213).
Stufe B ist damit faellig, und `UI_SPEC` §11 (AK-220 bis AK-229) ist ihre
Vorgabe. Der Rueckfallweg und Stufe B gehoeren deshalb in **eine** Reihenfolge,
nicht in zwei unabhaengige Straenge: AK-228 verlangt den Rueckfallsatz in
derselben Zeile, die Stufe B ohnehin umbaut.

---

### AD-030 — Der gemerkte Pfad lebt in **zwei festen Schluesseln** des vorhandenen Speichers, und das Programm hat **einen** Ort, an dem es den Spielordner aufloest (2026-09-08, Status: aktiv; benennt die Reichweite von OF-15, beruehrt AD-013, AK-107, AK-117, AK-121, AK-125)

**Kontext — der Widerspruch, den ich aufloesen soll.**

> **A15** (GOAL, Nachtrag 06.09.2026): „der gewaehlte Pfad wird geprueft,
> **behalten** und beim naechsten Start wieder benutzt."

> **OF-15** (GOAL, 02.09.2026): „Damit entsteht **kein neuer persistenter
> Zustand** — nach drei Datenverlusten im QSettings-Schluesselraum (Zyklus 4
> und 5) ist das die tragende Begruendung, nicht die Bequemlichkeit."

A15 ist die spaetere Entscheidung des Nutzers und gilt. Die Frage ist nicht
*ob*, sondern *wie* — und die Antwort haengt daran, **was die drei
Datenverluste tatsaechlich verursacht hat.** Das habe ich nicht aus OF-15
uebernommen, sondern an der Stelle nachgelesen, an der es dokumentiert ist
(`nrplanner/chalices.py:190-320`):

| Verlust | Bauform | Beleg |
|---|---|---|
| QA-003 | Ein Build hiess `Fire / ice`. QSettings liest `/` als Pfadtrenner: der Name war kein Eintrag, sondern eine **Gruppe** `Fire ` mit dem Eintrag ` ice`. `childKeys()` sah ihn nicht, und das Loeschen der Builds nahm die Gruppe mit. | `chalices.py:193-200` |
| QA-046 | Ein Schluessel ist auf Windows der Name eines Registry-Wertes, und die Registry unterscheidet Namen **nicht nach Gross-/Kleinschreibung**. `Bleed build` und `bleed build` landeten in **einem** Eintrag; Loeschen des einen nahm den anderen mit. | `chalices.py:215-222` |
| QA-033 | Beim Umschluesseln wurde waehrend des Laufens entfernt. `remove("Fire ice")` nimmt die **gleichnamige Gruppe** mit — `Fire ice/v2` war geloescht, bevor es gelesen war. | `chalices.py:305-318` |

**Die gemeinsame Randbedingung aller drei — und sie ist die ganze
Entscheidung:** in allen drei Faellen wurde **Nutzertext zum Schluessel**. Der
Schluesselraum war unbegrenzt, aus Eingaben abgeleitet, und die zerstoerende
Operation war `remove`. **Kein einziger** der drei Verluste betrifft einen
**festen** Schluessel mit veraenderlichem **Wert** — die Bauform von
`ui/scale` und `ui/panes`, die seit Zyklus 1 nichts verloren hat.

Dazu die zweite tragende Aussage aus OF-15, die auf A15 **nicht** zutrifft:
*„Ein Halt verweist ausserdem auf einen Handle, und Handles werden beim
Einschmelzen neu vergeben"* (AD-013). Ein Pfad ist kein Handle. Er ist ein von
aussen pruefbarer Name, und er wird bei **jedem** Start gegen die Platte
geprueft, bevor er benutzt wird. Der Fehlermodus, gegen den AD-013 gebaut ist —
ein gespeicherter Verweis, dessen Ziel sich unbemerkt unter ihm ausgetauscht
hat — existiert hier nicht.

**Damit ist OF-15s Begruendung nicht widerlegt, sondern in ihrer Reichweite
benannt:** sie traegt gegen *aus Nutzertext abgeleitete Schluessel* und gegen
*persistierte Handles*. A15 verlangt keines von beiden.

**Der zweite, unabhaengige Teil des Kontexts — und der ist in der Spec nicht
entschieden:** `gamefiles.find_game_dir()` wird im Produktivcode an **vier**
Stellen gerufen, nicht an einer:

```
nrplanner/app.py:4428        firstrun.ensure_data(gamefiles.find_game_dir())
nrplanner/datasource.py:96   _regulation_matches  -> "kein Spiel da, der Abzug ist alles, was wir haben"
nrplanner/datasource.py:142  _load_data           -> Live-Extraktion nach einem Patch
nrplanner/datasource.py:168  _no_data_message     -> "No ELDEN RING NIGHTREIGN installation was found."
```

Wird nur `app.py:4428` auf den gemerkten Pfad umgestellt, heisst
`find_game_dir()` an drei weiteren Stellen weiterhin *„der automatisch
gefundene Ordner"* und wird dort als *„der Spielordner"* gelesen. Die Folgen
sind einzeln klein und zusammen genau die Luecke, in der QA-171 schon sitzt:
`_load_data` extrahiert nach einem Patch **nicht** live aus dem gewaehlten
Ordner, `_regulation_matches` faellt in den Zweig *„No install to compare
against; the snapshot is all we have"* und reicht den alten Abzug
**kommentarlos** durch, und `_no_data_message` behauptet, es sei keine
Installation gefunden worden, waehrend eine gemerkt ist.

**Optionen.**

- **A — im Bestand bleiben, nichts persistieren.** Der Pfad wird bei jedem
  Start neu erfragt. Konsequenz: A15s Satz „und beim naechsten Start wieder
  benutzt" faellt; der Nutzer mit ungewoehnlichem Speicherort klickt bei
  **jedem** Start. Das ist die Sackgasse, die A15 beseitigen soll, nur einmal
  pro Start statt einmal. **Entfaellt** — der Nutzer hat A15 nach OF-15
  entschieden.
- **B — eigene Datei** (`%LOCALAPPDATA%\NightreignHelper\paths.json`).
  Konsequenz: umgeht den QSettings-Schluesselraum vollstaendig, kostet aber ein
  neues Format, einen neuen Lese- und Schreibweg mit eigenen Fehlerfaellen, und
  legt die Angabe in **dasselbe** Verzeichnis, das das Programm bei einem
  Neuaufbau ausraeumt. Ausserdem waere sie der erste Zustand des Programms, der
  nicht im einen Speicher liegt, und `tests/test_settings_store.py` haelt genau
  die Einheitlichkeit fest, die damit fiele. Widerspricht zudem AK-117.
- **C — zwei feste Schluessel im vorhandenen Speicher**, Wert = Pfad. Genau die
  Bauform von `ui/scale` und `ui/panes`, und genau das, was AK-117 und AK-125
  bereits vorgeben.
- **D — C, aber zusaetzlich mit einem Aufloesungspunkt**, den alle vier
  Aufrufstellen benutzen.

**Entscheidung: D.** C allein waere die halbe Entscheidung: sie sagt, **wo**
der Pfad liegt, aber nicht, **wer ihn liest**, und die vier Aufrufstellen oben
laufen dann auseinander. Die vier Dinge, die der Auftrag ausdruecklich
verlangt, im Einzelnen:

**1. Ort.** Der vorhandene `QSettings`-Speicher, geoeffnet ueber
`favourites.ORG` / `favourites.APP` — nie ueber Literale.
**Genau zwei Schluessel, fuer immer:**

```
paths/game   der Ordner, der regulation.bin direkt enthaelt
paths/save   die Spielstanddatei
```

Beide sind **fest**. Kein Nutzertext wird je Teil eines Schluessels; der Pfad
steht ausschliesslich im **Wert**. Damit ist der Schluesselraum, den A15
hinzufuegt, **konstant zwei** — das ist die direkte Antwort auf die drei
Datenverluste, die alle drei aus einem *unbegrenzten, aus Eingaben
abgeleiteten* Schluesselraum kamen.

**2. Format.** Ein `str`: der absolute Pfad, so wie das Betriebssystem ihn
schreibt, aufgeloest (`os.fspath` des Ordners, der `regulation.bin` direkt
enthaelt — also **dieselbe Form, die `find_game_dir()` liefert**). Keine Liste,
kein JSON, kein zweiter Schluessel daneben, keine Zeitstempel, keine Historie.

*Warum das Lesen `type=str` erzwingt und nicht ohne auskommt:* QSettings gibt
einen Wert ohne Typangabe je nach Speicherform als Liste zurueck, sobald er ein
Komma enthaelt. Ein Ordnername darf ein Komma enthalten
(`D:\Games\Elden Ring, alt\...`), und der Wert kaeme dann als `QStringList`
zurueck — der Pfad waere still ein anderer Gegenstand als der geschriebene.
`value(key, "", type=str)` schliesst das; die Gegenprobe ist ein Ordnername mit
Komma, der unveraendert zurueckkommt.

**3. Beschaedigter Eintrag.** Beschaedigt heisst: leer, kein `str`, oder ein
Text, aus dem sich kein Pfad bauen laesst (`ValueError`/`OSError` aus
`pathlib.Path`). **Behandlung: wie abwesend.** Kein Dialog, keine Meldung, kein
Abbruch — die Aufloesung geht weiter zur Automatik. **Und der Eintrag wird
nicht geloescht.**

*Warum nicht geloescht:* `remove` ist die Operation, an der zwei der drei
Datenverluste haengen. Ein unbrauchbarer Wert kostet pro Start eine Pruefung
und nichts sonst; ein `remove` kann mehr treffen als den Schluessel, auf den es
zeigt. **Invariante, die daraus wird und die einen Waechter bekommt:**

> Das Programm ruft `QSettings.remove` **nie** auf einem Schluessel auf, der
> mit `paths/` beginnt. Diese beiden Werte werden ausschliesslich
> **ueberschrieben**, und nur durch einen bestaetigten Pfad.

Das ist strenger als AK-121 („ein einzelner Fehlschlag loescht sie nicht") und
widerspricht ihm nicht.

**4. Der gemerkte Pfad existiert beim naechsten Start nicht mehr.** Die
Reihenfolge, vollstaendig, deckungsgleich mit AK-107 und `UI_SPEC` §6:

1. Gemerkter Pfad **gueltig** → benutzt, kein Fenster. Gueltig heisst: er
   besteht **dieselbe** Stufe-1-Pruefung, unter der er angenommen wurde
   (AK-112: `regulation.bin` lesbar und nicht leer, eine `data*.bhd` aus
   `bhd5.ARCHIVE_KEYS`, eine DLL aus `oodle._DLL_NAMES`).
   **Eine Funktion fuer beides** — Annahme und spaetere Gueltigkeit koennen so
   nicht auseinanderlaufen; zwei Praedikate fuer dieselbe Frage waeren die
   Bauform, die `find_loadout_table` laut seinem eigenen Docstring schon zweimal
   falsch gemacht hat.
2. Ungueltig, **oder die Pruefung wirft** (Laufwerk weg, Netzpfad tot,
   Rechteproblem) → jede `OSError` gilt als „ungueltig", nie als Fehler nach
   oben. Weiter mit `find_game_dir()`.
3. `find_game_dir()` findet etwas → **benutzt, ohne Fenster** (AK-107) und
   **ohne den gemerkten Wert zu ueberschreiben**. Geschrieben wird nur, was der
   Nutzer bestaetigt hat; ein Fund der Automatik ist keine Bestaetigung, und
   ein Laufwerk kommt wieder (`UI_SPEC` §6).
4. Auch die Automatik leer → das Panel entscheidet nach Datenlage: Abzug
   vorhanden → Text A3, kein Abzug → Text A2 (AK-119/AK-120).
5. Erst eine Bestaetigung (C1/C2) schreibt — **vor** dem Bau (AK-117). Ein
   Ordner, der bestaetigt wurde und dessen Bau danach scheitert, bleibt
   gemerkt: er hat die Annahmebedingung bestanden, und der naechste Start
   versucht den Bau erneut, statt zu fragen.

Fuer `paths/save` gilt dasselbe eine Stufe flacher und ohne Panel (AK-125):
gemerkte Datei weg → **still** auf `find_saves()` zurueck; auch das leer → die
Zeile mit `Find my save…`. Der gemerkte Wert bleibt stehen.

**Der Aufloesungspunkt, und wo die Grenze liegt.**

```
nrdata/gamefiles.py      Qt-frei. Suchen und Erkennen:
                         find_game_dir()          wie heute, unveraendert
                         looks_like_the_game(p)   Stufe 1 (AK-112), das eine Praedikat
                         is_named_nightreign(p)   Stufe 2 (AK-113), weich
                         search_from(p)           §4.2: 3 runter, 2 rauf, 400 Verzeichnisse, 2 s

nrplanner/gamepath.py    NEU, Qt-Seite. Merken und aufloesen:
                         GAME_KEY = "paths/game"  SAVE_KEY = "paths/save"
                         remembered_game()  remember_game(p)
                         remembered_save()  remember_save(p)
                         resolve_game() -> Path | None      die Kette 1-4 oben
```

**Abhaengigkeitsrichtung: `nrplanner` → `nrdata`, nie zurueck.** Die Suche und
die Erkennung sind reine Pfadlogik und gehoeren zu `find_game_dir`, den sie
ergaenzen; sie bleiben **Qt-frei** und damit ohne Qt testbar. Das Gedaechtnis
braucht QSettings und darf deshalb nicht nach `nrdata`. Die Alternative — ein
`gamefiles.set_override()`, das `app.py` beim Start setzt — waere globaler
veraenderlicher Zustand in der untersten Schicht und ist verworfen.

**Alle vier Produktivstellen rufen `gamepath.resolve_game()`.**
`datasource.py` importiert `gamepath` lazy in der Funktion, wie es
`from nrdata import gamefiles` heute schon tut. `scripts/` bleiben auf
`find_game_dir()` — sie sind Entwicklerwerkzeuge ohne Fenster und ohne Nutzer,
der einen Pfad bestaetigt haette; das ist eine **benannte Ausnahme**, keine
vergessene Stelle.

**Konsequenzen.** *Leicht wird:* der Nutzer mit ungewoehnlichem Speicherort
kommt an; `_load_data` extrahiert nach einem Patch auch aus einem gewaehlten
Ordner live; `_no_data_message` kann nicht mehr behaupten, es sei nichts
gefunden, waehrend etwas gemerkt ist. *Dauerhaft schwer wird:* das Programm hat
zum ersten Mal einen persistenten Zustand, der auf die **Aussenwelt** zeigt —
jede kuenftige Aenderung an der Erkennung muss zwei Faelle bedienen (gemerkt
und gefunden) statt einen. Und: eine Pfadpruefung beim Start kann blockieren,
wenn der gemerkte Pfad ein nicht erreichbares Netzlaufwerk ist (siehe Risiken).

**Umkehrbarkeit: mittel.** Die zwei Schluessel und das Modul sind in einem Zug
zurueckzubauen; der Rueckbau kostet aber jeden Nutzer, der einen Pfad gewaehlt
hat, seine Angabe, und A15 faellt damit. Der **Aufloesungspunkt** allein ist
**leicht** umkehrbar (vier Zeilen).

**Die Vertrauensgrenze — sie verschiebt sich, und das ist ein Fall fuer den
`security-reviewer`.** Ich entscheide das nicht; ich benenne, was sich bewegt:

1. **Der Ordnerdialog macht aus einer Menge von rund vierzehn Kandidaten eine
   beliebige Menge.** Heute liefert `find_game_dir()` ausschliesslich Pfade aus
   der Steam-Bibliothekliste oder dem Muster
   `<Laufwerk>:/SteamLibrary/steamapps/common/ELDEN RING NIGHTREIGN/Game`
   (`gamefiles.py:48-70`). Nach A15 ist der gelesene Ordner der, den der Nutzer
   benennt.
2. **Der angenommene Ordner wird nicht nur gelesen — aus ihm wird eine native
   DLL in den Prozess geladen.** `oodle.load()` ruft
   `ctypes.CDLL(str(game_dir / name))` (`nrdata/oodle.py:34-46`). AK-112 nimmt
   einen Ordner **gerade deshalb** an, weil eine dieser DLLs darin liegt. Der
   Weg „Ordner waehlen → Code aus diesem Ordner laeuft im Prozess" ist neu.
3. **Drei gestrichene Befunde standen auf genau der Bedingung, die A15
   verschiebt.** SEC-016, SEC-017 und SEC-018 sind am 05.09.2026 vom Nutzer
   gestrichen worden, woertlich: *„setzt eine boesartige Spielinstallation oder
   ein bereits uebernommenes Benutzerkonto voraus; nicht erneut vorlegen"*
   (SEC-016/SEC-017 in `security/findings.md`; der Fliesstext dazu steht seit dem 12.09.2026 in `security/verlauf.md`). Es sind Entpackbomben im Spieldatenpfad
   (`dcx.py` ohne Deckel, `tpf.py` 3,2 GiB Spitzenhaufen aus 256 KiB Eingabe).
   Die Bedingung „boesartige Spielinstallation" war bisher nur ueber ein
   uebernommenes Konto erreichbar; nach A15 ist sie eine Ordnerauswahl weit
   entfernt. **Der Befundstatus aendert sich dadurch nicht von selbst** — die
   Streichung gehoert dem Nutzer, und er hat „nicht erneut vorlegen" gesagt.
   Aber die **Randbedingung**, unter der er gestrichen hat, gilt fuer den
   geprueften Fall und nicht fuer den neuen. Das zu melden ist meine Pflicht;
   was daraus folgt, ist OF-31.
4. **Der Spielstand:** `Find my save…` traegt nach `UI_SPEC` §5 den dritten
   Filtereintrag `All files (*)`. Ein **heruntergeladener** Spielstand — die
   scharfe Grenze, die der Nutzer am 02.09.2026 ausdruecklich stehen gelassen
   hat — ist damit in einem Klick erreichbar statt nur durch Ablegen im
   Roaming-Profil. **Die Abwehr dagegen aendert sich nicht** und traegt weiter:
   SEC-022 (`MIN_BYTES_PER_RELIC_RECORD`, `savefile.py:173`), die zweite
   Dichtepruefung in `Inventory._refuse_a_density_no_save_can_have`, die Deckel
   aus SEC-002 und die Id-Pruefung. Was sich aendert, ist die
   **Erreichbarkeit**, nicht die Haerte. Auch das gehoert dem
   `security-reviewer`.

---

### AD-031 — Bricht die Id-Annahme, **waehlt** der Scan den langsamen Weg, statt zu verweigern; der langsame Weg wird dafuer wieder gebaut (2026-09-08, Status: aktiv; **loest AD-029 Vertrauensgrenze Punkt 3 ab**)

**Was abgeloest wird, woertlich aus AD-029:**

> Die tragende Annahme `relic_id < 0x01000000` … gehoert als Pruefung in den
> Code, nicht als Kommentar daneben — laut werden, nicht still danebenliegen.

**Das war richtig und ist zu eng.** „Laut werden" hat der `developer` in T-133
als `raise` umgesetzt (`savefile.py:237-246`) — die einzige Form, die zur
Verfuegung stand, denn der langsame Weg war im selben Zug verschwunden. Der
Nutzerentscheid vom 08.09.2026 verlangt: *benutzbar bleiben, aber nicht
stillschweigend.* **Die Lautstaerke wandert von der Ausnahme in die
Bestandszeile** (AK-228); die Annahme bleibt geprueft.

**Kontext, was auf dem Spiel steht.** Ein Spielpatch, der Relikt-Ids ueber
`0x01000000` vergibt, macht den Vorfilter blind fuer ein ganzes Id-Band. Der
Scan gaebe eine kurze Liste zurueck, die von einem leeren Inventar nicht zu
unterscheiden ist — deshalb die Pruefung. Heute endet das Programm dann in
`app.py:3445`, `"Save could not be read: …"`, obwohl mit dem Spielstand nichts
ist. Der heutige Text sagt das sogar selbst („nothing is wrong with the save")
und steht trotzdem hinter dem Praefix, das das Gegenteil behauptet — das ist
die Reibung, die AK-229 abstellt.

**Optionen.**

- **A — im Bestand bleiben (verweigern).** Konsequenz: nach einem Patch ist das
  Programm fuer jeden Nutzer tot, bis eine neue Fassung erscheint, obwohl es
  weiterlesen koennte. Vom Nutzer am 08.09.2026 verworfen.
- **B — Vorfilter ausbauen, immer langsam scannen.** Konsequenz: gibt die
  gemessenen 51,8x auf (4835,3 → 93,3 ms, T-133) und damit den groessten
  einzelnen Hebel des Programms, um einen Fall abzudecken, der heute nicht
  eintritt. Architektur gegen einen Fall, der nie kommt.
- **C — beide Wege im Code, die Datenlage waehlt.** Der schnelle Weg, solange
  die Annahme traegt; der langsame, sobald sie bricht; die Zeile sagt es.

**Entscheidung: C.**

**Form — vier Punkte, und der dritte ist der, an dem es schiefgehen kann.**

1. **Die Wahl haengt an den Daten, nicht an der Datei.** Die Annahme betrifft
   `valid_relic_ids` — den Datensatz —, nicht den Spielstand. Also wird sie
   **einmal je Ladevorgang** entschieden, bevor ein Byte gescannt wird:

   ```python
   # nrdata/savefile.py
   FAST, SLOW = "fast", "slow"

   def relic_scan_mode(valid_relic_ids: set[int]) -> str:
       """Which offset generator can see every id in this dataset."""
       return SLOW if max(valid_relic_ids, default=0) >= RELIC_ID_CEILING else FAST
   ```

   `read_owned_relics` bekommt ein Schluesselwort `mode: str | None = None`
   (`None` = selbst fragen). **Der Rueckgabetyp aendert sich nicht.** Damit
   braucht es weder einen Modulzustand — der bei AD-029 Stufe B in einem Worker
   liefe und dort falsch waere — noch eine Aenderung an einer Aufrufstelle, die
   den Weg nicht wissen will.

2. **Ein Rekord-Leser, zwei Versatz-Erzeuger.** Der langsame Weg ist **nur** ein
   zweiter Generator neben `_relic_id_offsets`:

   ```python
   def _every_fourth_offset(slot_data: bytes):
       """Every four-byte-aligned offset a record could begin at."""
       yield from range(0, len(slot_data) - RELIC_FIELDS_SIZE, 4)
   ```

   Der Rumpf von `read_owned_relics` — Doppel-Id, Id-Gueltigkeit,
   `seen_offsets`, Effekte, Fluechte, **und die Dichteschranke SEC-022** —
   bleibt **einer**. Zwei Rumpfkopien waeren die Bauform, an der
   `find_loadout_table` laut seinem eigenen Docstring schon zweimal falsch lag.

3. **Der Waechter darf seine Erwartung nicht aus dem Produktivcode nehmen — und
   diese Falle ist hier bereits gestellt.**
   `tests/test_relic_scan_prefilter.py:43-80` traegt `full_walk`, eine
   **absichtliche** dritte Implementierung des ganzen Scans, mit dem Kommentar
   *„the only one in the tree: it is the independent expectation the prefilter
   is held against, so sharing code with the thing under test would be the whole
   point missed."* Zoege der `developer` sie nach `savefile.py` und liesse den
   Test dann Produktion gegen Produktion vergleichen, waere der Waechter
   entkernt, ohne dass ein Test rot wuerde — genau L-008 (b).
   **Also: `full_walk` bleibt, wo es ist, und wird nicht ersetzt.** Der neue
   Generator wird **gegen** es geprueft, nicht aus ihm gebaut.

4. **Der Weg reist auf dem Bestand, nicht auf einem Signal.** `inventory.load`
   fragt `relic_scan_mode` einmal, gibt den Wert an jeden
   `read_owned_relics`-Aufruf weiter und legt ihn als Feld auf das Ergebnis:

   ```python
   @dataclass
   class Inventory:
       ...
       read_the_slow_way: bool = False
   ```

   Ein Vorgabewert, also bleiben alle handgebauten `Inventory`-Objekte in den
   Tests gueltig. Ein `bool` ist unveraenderlich und passiert damit die
   Thread-Grenze von AD-029 Stufe B ohne Sonderfall (AD-006.8 unangetastet).
   Die Zeile in `app.py` liest das Feld — **kein** Signal, **keine** Ausnahme,
   **kein** Modulzustand.

**Was AD-031 ausdruecklich nicht anfasst:** `RELIC_ID_CEILING` und seine
Herleitung; die Dichteschranke SEC-022 in beiden Wegen;
`_loadout_marker_offsets` (Programmkonstante, siehe XI-0); die Regel „der
bestbestueckte Spielstand gewinnt" (AD-029 haelt).

**Konsequenzen.** *Leicht wird:* ein Spielpatch kostet Geschwindigkeit statt
Benutzbarkeit, und der Nutzer erfaehrt warum. *Dauerhaft schwer wird:* das
Modul traegt zwei Wege durch dieselbe Schleife, und jede kuenftige Aenderung am
Rekord-Leser muss beide bedienen — die Gleichheitspruefung ist deshalb kein
Zusatz, sondern die Bedingung, unter der die Entscheidung traegt.
*Ausserdem, unangenehm und zu sagen:* faellt der Rueckfall, faellt
`inventory.load` von den gemessenen 657,2 ms auf die Groessenordnung der
gemessenen 6147,6 ms zurueck. **Das ist kein geschaetzter Wert, sondern der
Zustand von 1.7.1** — und genau der Grund, warum AD-029 Stufe B (U8) **vor oder
unmittelbar nach** dem Rueckfall gebaut gehoert: im Worker ist die Zahl
ertraeglich, im Hauptthread ist sie ein eingefrorenes Fenster.

**Umkehrbarkeit: leicht.** Ein Generator, ein Schluesselwort, ein Feld. Der
Rueckweg ist die heutige Fassung, und sie steht in der Historie.

---

---

## Themenbereich F — Test und Nachweis

*Womit geprueft wird, und welche Pruefpunkte eine Entscheidung tragen muss.*

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

### Präzisierung AD-009 — die Nummer 18 war zweimal vergeben (D4)

**Befund:** Nachtrag II vergibt Prüfpunkt **18** an *„Kein
`QSettings`-Zugriff im Berater-Pfad"*, Nachtrag III vergibt dieselbe **18**
an *„Untere Schicht bitgleich über den ganzen Umbau"*. Beide sind vom
2026-09-02. Nachtrag III vergibt danach 19 bis 22, die frei waren; die
Kollision betrifft **nur** die 18.

**Auflösung, mit zwei unabhängigen Gründen, die auf dasselbe zeigen:**

- **Prüfpunkt 18 bleibt bei Nachtrag II:** „Kein `QSettings`-Zugriff im
  Berater-Pfad". Er hat den ersten Anspruch auf die Nummer (Nachtrag II
  steht vor Nachtrag III), **und** er ist der einzige der beiden, der noch
  **offen** ist: QA-110 zeigt auf ihn und geht an den `developer`. Eine
  offene Zusicherung umzunummerieren heisst, in einem laufenden Befund eine
  falsche Nummer stehen zu lassen.
- **Nachtrag IIIs Prüfpunkt wird Prüfpunkt 28:** „Untere Schicht bitgleich
  über den ganzen Umbau". Er ist **erledigt** — der Umbau W0–W5 ist
  abgeschlossen, und die Stellen, die auf ihn zeigen (`docs/tasks/T-027.md`,
  `T-029.md`, `T-030.md`, `qa/findings.md` bei der Golden-Neuaufnahme), sind
  Verläufe passierter Tore, keine offenen Aufträge. 28 ist die nächste freie
  Nummer nach Nachtrag V.

**Ab jetzt gilt:**

| Zusicherung | Nummer bis 05.09.2026 | Nummer ab jetzt |
|---|---|---|
| Kein `QSettings`-Zugriff im Berater-Pfad (Nachtrag II) | 18 | **18** (unverändert) |
| Untere Schicht bitgleich über den ganzen Umbau (Nachtrag III) | 18 | **28** |

Die Verweise in dieser Datei sind nachgezogen. Wer in
`docs/tasks/T-027.md`, `T-029.md`, `T-030.md`, `docs/berichte/` vor dem
05.09.2026 oder in `qa/findings.md` auf „Prüfpunkt 18" trifft, liest ihn im
Licht dieser Tabelle: im Zusammenhang mit der Golden-Neuaufnahme und mit
`weapons.rate` ist die 28 gemeint, im Zusammenhang mit dem Berater und
QA-110 die 18.

**Regel, damit es nicht wieder passiert:** Prüfpunkte werden wie AD-Nummern
**fortlaufend** vergeben und **nie neu**. Ein Nachtrag schaut auf die höchste
vergebene Nummer im ganzen Dokument, nicht auf die höchste in seinem eigenen
Abschnitt. Höchste vergebene Nummer nach diesem Nachtrag: **34**.

---

---

*Ab hier steht, was aus den Entscheidungen folgt: der Umsetzungsschnitt, die
Verbote an den `developer`, die Pruefpunkte, die Risiken, das bewusst nicht
Getane und die offenen Fragen. Innerhalb jedes Blocks stehen die Fassungen in
der Reihenfolge, in der sie entstanden sind — die **juengste zuletzt**, und wo
eine aeltere ueberholt ist, sagt sie es an Ort und Stelle.*

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

### Änderungen am Umsetzungsschnitt

| Schritt | Änderung |
|---------|----------|
| **S4+** | `AdvisorRequest` trägt den Haltezustand (eingefrorene Abbildung Slotindex → Handle / Custom-Inhalt / „leer") und dessen Fingerabdruck. `AdvisorResult` trägt zusätzlich den Wert des Grundzustands und den Zugewinn (AD-014.6) sowie die festgehaltenen Slots. |
| **S4b (neu, vor S5)** | **`advisor/evaluate.py`** — die einzige Stelle unter `advisor/`, die `model.compute` erreicht (AD-014.1). Die Erwartung im `compute`-Wächter (`tests/test_one_build.py`) wird um **genau diesen einen** Eintrag erweitert. *Fertig, wenn:* Wächter grün mit zwei Einträgen, **und** ein probeweise in `search.py` eingefügter zweiter Aufruf ihn rot macht. |
| **S5+** | Vorsortierung gegen den Grundzustand statt isoliert (AD-014.3); Handles der festgehaltenen Relikte im Anfangszustand belegt (AD-014.5); Mindestlänge der Kandidatenliste `K + (Zahl der freien Slots − 1)`. |
| **S7+** | Ebenen der Beam-Suche = **freie** Slots; Symmetriegruppen nur über freie Slots (AD-014.4); alle Slots gehalten ⇒ kein Suchlauf. |
| **S8+** | Bezugspunkt der Begründung ist der Grundzustand, nicht der leere Build (AD-014.6); Flüche und ihre Beträge aus `Build.sources` (AD-015); neue `unknowns`-Zeilen für gehaltene Slots und zielfremde Flüche. |
| **S9+** | `held_fingerprint` im Cache-Schlüssel, Generationszähler auch bei Halteänderung, Rückabbildung nur der freien Slots (AD-016). |
| **S11+** | Der `performance-tuner` misst zusätzlich einen Lauf mit `h=5` (die Picker-Frage) und bestätigt, dass der ungünstigste Fall weiterhin `h=0` ist. |

Die Reihenfolge bleibt: S4 → S4b → S5/S6 → S7 → S8 → S9 → S10.

### Änderungen am Umsetzungsschnitt (zusätzlich zu Nachtrag I)

| Schritt | Änderung |
|---------|----------|
| **S5++** | Die Vorsortierung ist ab jetzt ein **öffentliches Ergebnis**, nicht ein Zwischenschritt: `candidates` liefert je Kandidat den Grenzbeitrag gegen den Grundzustand, unter beiden Zielrichtungen. `search` verbraucht dieselbe Liste. |
| **S9++** | Zwei Entprellungswerte (Picker kürzer als Gesamtlauf), LRU-Grösse neu (Vorschlag 64). Kein zweiter Cache, keine zweite Schlüsselform (AD-016). |
| **S10++** | Der Halt lebt am `Planner` als `(hero_id, vessel_id, deep) -> Haltezustand` (AD-017). Die Anbindung des Pickers gehört ebenfalls hierher — `relicpicker.py` bekommt die bewertete Liste über den Controller, **nicht** einen eigenen Rechenweg. |
| **S11++** | Zusätzlich zu messen: Picker-Lauf am weissen Slot (Erwartung ~51 ms), beide Entprellungswerte, LRU-Grösse, und ob der Gesamtlauf weiterhin der ungünstigste Fall ist. |

### Änderungen am Umsetzungsschnitt

Vor S10 (Berater-Bau) tritt die Fassaden-Kette **W0 bis W5** aus AD-019. W6
(ein Wert in `MULTIPLIERS_FOR`) steht ausserhalb der Kette und wartet auf die
Spielmessung des Nutzers.

| Schritt | Inhalt | Hängt ab von |
|---------|--------|--------------|
| **W0** | `nrplanner/weaponstab.py` löschen (QA-057) | — |
| **W1** | `WeaponRating.per_type()`, drei Ausschreibungen umstellen | W0 |
| **W2** | Fassade in `damage.py`, Politik mit den **heutigen** Werten | W1 |
| **W3** | `app.py` Kachel + Tafel auf `damage.equipped()` | W2 |
| **W4** | `arsenaltab` auf `damage.rank_candidates()`, `target_tier` explizit | W2 |
| **W5** | Wächter aus AD-021 scharfschalten | W3, W4 |
| **W6** | `MULTIPLIERS_FOR[Basis.CANDIDATE]` setzen | Spielmessung |

### Reihenfolge gegenüber dem Berater — die Frage des `director`

**Die Fassade kommt vor dem Berater. Die Spielmessung nicht.** Das ist die
Präzisierung gegenüber dem Nachtrag II, wo QA-018 als Ganzes vor den Berater
gezogen wurde.

- **Warum die Fassade davor muss:** Der Hauptweg des Beraters ist der
  Grenzbeitrag über `attack_rating` (AD-018). Solange `attack_rating` eine von
  vier Lesarten ist, erbt der Berater die Mehrdeutigkeit, und eine falsche
  **Steigung** kürzt sich in einer Differenz nicht heraus.
- **Warum die Messung danach kommen darf:** Der Berater vergleicht Kandidaten
  **bei fester Waffenmenge**. Eine flache Multiplikatorschicht wirkt auf jeden
  Kandidaten mit demselben Faktor je Schadensart; sie skaliert den
  Grenzbeitrag, dreht ihn nicht um und verändert den abnehmenden Ertrag nicht.
  Prüfpunkt 16 (derselbe +Stärke-Kandidat hat bei hohem Stärkewert einen
  kleineren Grenzbeitrag) ist gegenüber diesem Faktor **invariant**.
  **Randbedingung dieser Aussage, und sie ist scharf:** sie gilt für
  Rangfolgen über Relikte bei fester Waffe. Sobald eine Zielrichtung
  **Waffen gegeneinander** stellt, sind die `class_rates` je Waffe
  verschieden, und dann entscheidet W6 mit. Zielrichtungen, die Waffen
  vergleichen, dürfen erst nach W6 scharfgestellt werden.

**Folge für den `director`:** Der Berater-Bau ist ab W5 nicht mehr durch die
Spielmessung blockiert. Was noch blockiert ist, ist die **angezeigte absolute
Zahl** — und dafür trägt jede Picker-Zeile weiterhin den
Attack-Rating-Vorbehalt aus AD-004, bis W6 steht.

### Umsetzung — Schnitt in einzeln lauffaehige Schritte (Nachtrag VIII)

Reihenfolge und Abhaengigkeiten; jeder Schritt ist fuer sich lauffaehig und
fuer sich pruefbar. **U1 haengt an nichts** und kann sofort parallel laufen.

> **Ueberholt am 2026-09-08 (Nachtrag IX, T-125) fuer U5a, U5b, U6 und U7.**
> U1 bis U4 und U8 gelten unveraendert; **U4 ist erledigt** (T-124). Wer
> U5a, U5b, U6 oder U7 beauftragt oder umsetzt, nimmt die Fassung aus
> Nachtrag IX — die Zeilen unten bleiben als Verlauf stehen.

| # | Rolle | Inhalt | haengt an |
|---|---|---|---|
| **U1** | `developer` | AD-029 Stufe C: Vorfilter in `nrdata/savefile.py`, Id-Annahme als Pruefung im Code, Gleichheitsprobe gegen den heutigen Scan, Dichteschranke unangetastet | — |
| **U2** | `security-reviewer` | Vorfilter gegen die praeparierte Datei aus T-096 und gegen SEC-022; lesend | U1 |
| **U3** | `performance-tuner` | `inventory.load` und den Prozessstart nachmessen (S11-E fortschreiben); **entscheidet den Ausloeser fuer Stufe B** | U1 |
| **U4** | `ui-ux-designer` | `UI_SPEC` §3.8 neu; erster Anstrich ohne Zahlen; Ordnung, Kopfzeile und Chips beim Nachliefern; Zielrichtungswechsel im offenen Dialog | — |
| **U5a** | `developer` | AD-028, Qt-freie Seite: die Pool-Funktion in `advisor/run.py`, kanonische Form nach Punkt 3, `SlotPool`-Gleichheit vorher/nachher belegt | — |
| **U5b** | `developer` | AD-028, Verdrahtung: `AdvisorController` nimmt seine Antwortfunktion, zweite Instanz am Fenster (100 ms / 64), `SlotAdvice` fragt die Spur, Verteilung von `before_the_data_changes`/`shutdown`, Docstring `276-281` ersetzt, direkte `advisor`-Importe aus `relicpicker` entfernt | U4, U5a |
| **U6** | `developer` | W1, W2, W3 mit ihren toetenden Mutationen | U5b |
| **U7** | `performance-tuner` | 318,1 ms nachmessen; **den Hauptthread-Rest messen** (OF-26); Ueberlappung zweier Spuren messen (OF-25) | U5b |
| **U8** | `developer` | Stufe B aus AD-029 — **nur**, wenn U3 den Ausloeser gemeldet hat | U3, Spec fuer den dritten Zustand |

**Was der `developer` ausdruecklich nicht tun soll:** keine Oberflaeche
entwerfen (U4 geht vor U5b); die Rechnung nicht schneller machen, um sie im
Hauptthread zu behalten (P1a ist ein eigener Auftrag und ersetzt AD-028
nicht); keinen zweiten Generationszaehler und keinen zweiten Thread-Weg
bauen; die Dichteschranke SEC-022 nicht anfassen; `load()` nicht frueher
abbrechen lassen; keine Zeitschranke in die Suite schreiben.

---

### Umsetzung — Fassung 2 von U5a bis U7 (ersetzt die entsprechenden Zeilen in Nachtrag VIII)

**U1 bis U3 und U8 gelten unveraendert. U4 ist erledigt** (T-124,
`UI_SPEC.md`, AK-197 bis AK-210).

| # | Rolle | Inhalt | haengt an |
|---|---|---|---|
| **U5a** | `developer` | AD-028, Qt-freie Seite: die Pool-Funktion in `advisor/run.py`; kanonische Form nach AD-028.3; sie nimmt ihr `rank_by` aus `request.goal_id`; **die benannte Konstante fuer die kanonische Zielrichtung (IX-2.1) entsteht hier**; `SlotPool`-Gleichheit vorher/nachher ueber Handles und Punktzahlen belegt | — |
| **U5b** | `developer` | AD-028, Verdrahtung: `AdvisorController` nimmt seine Antwortfunktion; zweite Instanz am Fenster mit **Entprellung 0 ms** und Cache **64** (IX-1.1, IX-3); die zusaetzliche Methode „antworte sofort, falls bekannt" samt gemeinsamer privater Frageerzeugung (IX-1.3); `SlotAdvice` fragt die Spur; `_sort_chosen` fragt **nicht** mehr (IX-0); die Anzeige liest ihre Richtung aus der Einstellung, nicht aus `SlotPool.rank_by` (AK-205); Verteilung von `before_the_data_changes`/`shutdown` an **beide** Spuren; Docstring `relicpicker.py:276-281` ersetzt (er begruendet heute das Gegenteil **und** traegt die widerlegten ~51 ms — OF-27, dritte Fundstelle); direkte `advisor`-Importe aus `relicpicker` entfernt | U5a |
| **U6** | `developer` | **W1, W2, W3 (neue Fassung IX-4), W4, W5** mit ihren toetenden Mutationen, alle im Standardlauf, keine Wanduhr-Schranke | U5b |
| **U7** | `performance-tuner` | 318,1 ms nachmessen; **Groesse eines Picker-Cache-Eintrags in der neuen Antwortform gegen die 140-KiB-Schranke aus IX-3.2**; **Trefferquote der beiden tragenden Spuren unter dem Schluessel ohne Richtung (IX-3.3)**; Hauptthread-Rest (OF-26); Ueberlappung zweier Spuren (OF-25) | U5b |

**U5b haengt jetzt nur noch an U5a**, weil U4 geliefert ist.

**Was der `developer` ausdruecklich nicht tun soll** (zusaetzlich zur Liste in
Nachtrag VIII):

- **Die Entprellung nicht auf der Klasse aendern.** Die 0 ms gehoeren der
  Instanz; die Advisor bar behaelt 250 ms.
- **Den Cache nicht generell vor den Zeitgeber ziehen** (Option D in IX-1) —
  das aendert die Advisor bar mit.
- **`UI_SPEC` §4s Rueckweg nicht stillschweigend bauen.** Stellt sich beim
  Bauen heraus, dass ein Pool die andere Richtung doch nicht bedient, ist das
  ein **Befund** (L-008c): melden; dann bekommt der Richtungswechsel seinen
  Wartezustand **und** die 100-ms-Entprellung kommt zurueck (IX-1.2).
- **Nicht vorwaermen** (IX-5), auch nicht „nur den einen Slot".
- **`AdvisorResult` nicht um den Pool erweitern**, um beide Spuren dieselbe
  Antwortform tragen zu lassen — das machte jeden Gesamtlauf-Eintrag um die
  Kandidatenliste schwerer, gegen 279,9 KiB, die schon der teure Fall sind.

---

### Umsetzung — U9 und U10 (zu den Schritten aus Nachtrag VIII und IX)

| # | Rolle | Inhalt | haengt an |
|---|---|---|---|
| **U9** | `developer` | **Anwendungscode, eine Datei:** `shutdown` erhoeht den Generationszaehler vor dem Unterbrechen (X-1, Entscheidung D); Klassen-Docstring `worker.py:198-216` bekommt die Fassung aus X-0; **Regressionstest** = sechster W6-Fall „the window is closing" mit erwarteter Ausgangsliste **leer** als Literal | — |
| **U10** | `developer` | **Nur `tests/`:** **W8** neu (X-2, Tabelle der vier unterbrechenden Stellen, beide Mutationen); **W1** um die Zeile `candidates.pools` → `advisor/run.py` erweitert (X-3.3) und um die Randbedingung im Docstring der Tabelle (X-3, letzter Absatz) | — |

**U9 und U10 sind unabhaengig voneinander** und beruehren disjunkte Dateien
(`nrplanner/advisor/worker.py` gegen `tests/test_picker_track_guards.py`) —
bis auf den sechsten W6-Fall, der zu U9 gehoert, weil er ohne dessen Fix ein
Wettlauf waere.

**Der sechste W6-Fall, so genau, dass er nicht versehentlich gruen wird:** die
Vorrichtung haelt die Antwortfunktion fest (`picker_track.StatedAnswers(...,
hold=True)`), stellt **eine** Frage ueber `ask`, wartet, bis der Lauf
angefangen hat (`answers.calls == 1`), ruft `track.shutdown(timeout_ms=0)`,
gibt **danach** die Antwort frei und dreht die Schleife aus. Erwartet wird
eine **leere** Ausgangsliste, als Literal geschrieben und nicht aus `shutdown`
gerechnet (L-008b).
*Toetende Mutation:* die Erhoehung des Generationszaehlers aus `shutdown`
entfernen → die freigegebene Antwort traegt die noch gueltige Generation,
`_on_ready` sendet `ready`, die Liste ist einelementig statt leer → rot
(L-008a: im Standardlauf).
**Ueberlebt die Mutation, ist das ein Befund und wird berichtet, nicht
nachgebessert** (L-008c) — dann sagt sie, dass der Fall in der Vorrichtung gar
nicht hergestellt wird, und der Fall ist wertlos, bis er es tut.

**Was der `developer` ausdruecklich nicht tun soll:**

- **`shutdown` kein Signal senden lassen** (X-1 Option B) — auch nicht „nur
  `stopped`, nur wenn etwas lief".
- **`_Worker.work` auf `search.Cancelled` nichts senden lassen** (X-2) — das
  doppelte den Ausgang nach `cancel()`.
- **`_interrupt_the_running_worker` keine Signatur geben** (X-1 Option C) —
  das ist der Umbau, den W8 gerade unnoetig macht.
- **`app.py` nicht anfassen**, um Fassung 1 von W1 woertlich wahr zu machen
  (X-3).
- **`UI_SPEC.md` nicht anfassen.** Die AK-218-Meldung gehoert dem
  `ui-ux-designer`.
- **Die Entprellung, die Cache-Groessen und die Antwortformen nicht
  beruehren** — das sind IX-1, IX-3 und U7.

---

### Umsetzung — Schnitt in einzeln lauffaehige Schritte

Obergrenze fuenf Dateien je Auftrag; die Schaetzung ist eine Schaetzung und als
solche benannt (kein Messwert, keine Herleitung — sie stuetzt nur die
Reihenfolge). Jeder Schritt ist fuer sich lauffaehig und fuer sich pruefbar.

| # | Rolle | Inhalt | Produktivdateien | Tests | Schaetzung | haengt an |
|---|---|---|---|---|---|---|
| **V1** | `developer` | AD-030, Qt-freie Seite plus Gedaechtnis: `looks_like_the_game`, `is_named_nightreign`, `search_from` (§4.2/§4.3, Budget 400/2 s) in `nrdata/gamefiles.py`; neues `nrplanner/gamepath.py` mit den zwei Schluesseln und `resolve_game()`; die drei Aufrufstellen in `nrplanner/datasource.py` auf `resolve_game()`. **Keine Oberflaeche.** | **3** — `nrdata/gamefiles.py`, `nrplanner/gamepath.py` (neu), `nrplanner/datasource.py` | R1–R6 | 45–60 min | — |
| **V2** | `developer` | AD-030, das Panel: Frage-Zustand in `firstrun.py` (Fensterart, die Texte aus §7, Ordnerdialog, C1/C2/E1/W1, Speichern **vor** dem Bau); die eine Zeile `app.py:4428`. | **2** — `nrplanner/firstrun.py`, `nrplanner/app.py` | R7–R9 | 60 min, **grenzwertig** | V1 |
| **V3** | `developer` | AD-030, Spielstand: Knopf `Find my save…`, Dateiauswahl mit den drei Filtern, die drei Ausgaenge S3/S4/die heutige Zeile, `paths/save` schreiben und lesen, `inventory.load(save_path=…)` fuettern (der Parameter existiert bereits). | **2** — `nrplanner/app.py`, `nrplanner/gamepath.py` | R10–R11 | 40–50 min | V1 (**nicht** V2) |
| **V4** | `developer` | AD-031: `_every_fourth_offset`, `relic_scan_mode`, `mode`-Schluesselwort, `_check_the_prefilter_can_see_every_id` entfaellt; `Inventory.read_the_slow_way`. | **2** — `nrdata/savefile.py`, `nrplanner/inventory.py` | R12–R16 | 40 min | — |
| **V5** | `developer` | **= U8**, AD-029 Stufe B nach `UI_SPEC` §11: Lesen in den Worker, dritter Fensterzustand, Bestandszeile samt Rueckfallsatz (AK-228) und Praefix-Eigenschaft (AK-229). | **3** — `nrplanner/app.py`, `nrplanner/inventory.py`, ein kleines Qt-Modul fuer die Lesespur | R17–R18 | eigener Auftrag, hier nicht geschnitten | V4, U3 (**gemeldet**, 657,2 ms) |

**Reihenfolge und was daran haengt.** V1 → (V2 ‖ V3), beide auf V1. V4 haengt an
nichts und kann jederzeit laufen. **V4 vor V5**, und moeglichst **unmittelbar**
davor: zwischen beiden faellt das Programm im Patch-Fall zwar zurueck, sagt es
aber noch nicht — ein A7-Bruch, der genau so lange besteht, wie die zwei
Auftraege auseinanderliegen. Ist eine Luecke absehbar, gehoert V4 hinter V5
statt davor.

**V2 und V3 fassen beide `app.py` an** und laufen deshalb nacheinander, nicht
parallel. **`app.py` ist zum Zeitpunkt dieser Entscheidung durch T-142 belegt.**

**Zwei Auflagen haengen daran** (`docs/legal/AUFLAGEN.md`, geprueft 08.09.2026):
**A-026** („kein Pfad mit Steam-Konto-Id auf der Flaeche", SEC-023) traegt V3
und wird von R11 gehalten. **A-024/A-027** — der Transparenztext und der
README-Absatz „What it reads and where it writes" — zaehlen auf, was das
Programm speichert; A15 fuegt dem **zwei** gespeicherte Werte hinzu. **Das ist
nach V3 vom `technical-writer` nachzuziehen und steht in keinem Auftrag.**
**A-032** ist **nicht** ausgeloest: A15 schreibt weder in den Spielstand noch in
die Installation.

---

### Regressionstests — dieselben fuer `developer` und `qa-engineer`

Der `developer` baut sie, der `qa-engineer` prueft sie nach. Jede Zeile nennt
ihre **toetende Mutation**; ein Gegenbau zaehlt erst, wenn er im
**Standardlauf** rot wird und seine Erwartung **nicht** aus der Stelle bezieht,
die er bewacht (L-008 a/b). Ein **ueberlebender** Gegenbau ist ein Befund und
wird berichtet, nicht nachgebessert (L-008 c).

| # | Datei | Was gehalten wird | Toetende Mutation |
|---|---|---|---|
| **R1** | `tests/test_game_path_memory.py` (neu) | **Die zwei Schluessel heissen `"paths/game"` und `"paths/save"`** — als **Literal** im Test, zusaetzlich `assert gamepath.GAME_KEY == "paths/game"`. Ohne das Literal bliebe ein Umbenennen der Konstante gruen. | Konstante umbenennen. |
| **R2** | dieselbe | **`remove` wird auf keinem `paths/`-Schluessel gerufen.** Zwei Wege zusammen: (a) Verhalten — nach einem gescheiterten Start ist der gespeicherte Wert **byteweise derselbe**; (b) Klasse — AST-Scan ueber den Baum in der Form von `test_settings_store.py`, kein `remove(...)` mit einem Literal, das mit `paths/` beginnt. **`OFFEN`-Liste: leer**, und ein Fall haelt fest, dass sie nur schrumpfen darf. | Im Fehlerzweig `settings.remove("paths/game")` einfuegen → (a) **und** (b) rot. |
| **R3** | dieselbe | **Beschaedigter Eintrag = abwesend, nicht Fehler.** Vier Faelle: leer, kein `str`, Text mit `\0`, Text ueber 16 383 Zeichen. Jeder liefert den Wert der Automatik, wirft nicht, und laesst den Speicher unveraendert. | Typ- und Leerpruefung entfernen: `Path("")` loest auf das Arbeitsverzeichnis auf und wuerde angenommen → rot. |
| **R4** | dieselbe | **Ein Pfad mit Komma kommt unveraendert zurueck** (`D:\Games\Elden Ring, alt\Game`). | `type=str` beim Lesen entfernen → der Wert kommt als Liste → rot. |
| **R5** | dieselbe | **Die Kette und ihre Zaehlung** (AK-107): gemerkt gueltig → `find_game_dir` wird **0** mal gerufen; gemerkt ungueltig und Automatik findet → Ergebnis der Automatik, **kein** Panel, und der gemerkte Wert ist danach **unveraendert**. Zaehlwerte gegen Literale. | Nach erfolgreicher Automatik `remember_game()` rufen → der Unveraendert-Fall rot. |
| **R6** | dieselbe | **Ein Aufloesungspunkt** (Klassenwaechter, Form von `test_settings_store.py`): kein Modul unter `nrplanner/` ruft `gamefiles.find_game_dir()` ausser `gamepath`. **Benannte Ausnahme: `scripts/`**, mit Grund im Docstring. Der Scan laesst `.claude/` aus (Worktrees). | Den Aufruf in `datasource.py` wieder einsetzen → rot. |
| **R7** | `tests/test_first_run_panel.py` (neu) | **Annahme und Ablehnung** (AK-112): nur `regulation.bin` → abgelehnt; + `data*.bhd` → abgelehnt; + DLL → angenommen. Und: **dasselbe Praedikat** entscheidet Annahme und spaetere Gueltigkeit (was angenommen wurde, gilt beim naechsten Start als gueltig, und umgekehrt). | Eine der drei Bedingungen aus `looks_like_the_game` streichen → rot; ein zweites Praedikat fuer die Startpruefung einfuehren → der Umkehrfall rot. |
| **R8** | dieselbe | **Suche und Budget** (AK-111): `…\ELDEN RING NIGHTREIGN` findet `…\Game`; ein Unterordner von `Game` findet `Game` (2 rauf); ein Baum mit **mehr als 400** Verzeichnissen endet in „nicht erkannt", und die **Zahl besuchter Verzeichnisse** steht gegen das Literal `400`. | Tiefe auf 4 erhoehen oder das Budget entfernen → rot. |
| **R9** | dieselbe | **Gespeichert wird vor dem Bau** (AK-117): nach der Bestaetigung steht der Wert im Speicher, **bevor** der Bau-Zustand betreten wird — Reihenfolge als Zaehlwert, nicht als Zustandsprobe. Dazu **A8**: die neuen Texte laufen durch `tests/test_interface_language.py`. | Das Speichern hinter den Bau schieben → rot. |
| **R10** | `tests/test_save_path_memory.py` (neu) | **`paths/save`** (AK-125): gemerkte Datei weg → **still** `find_saves()`, kein Text, kein Dialog, und der gemerkte Wert bleibt stehen. | Bei Fehlschlag loeschen → rot; eine Meldung ausgeben → rot. |
| **R11** | dieselbe | **Die drei Ausgaenge** (AK-124) und **AK-126**: kein Text ausser dem Tooltip enthaelt den Ordnernamen des Spielstands. | Den vollen Pfad in S3 setzen → rot. |
| **R12** | `tests/test_relic_scan_prefilter.py` (**vorhanden, erweitert**) | **Beide Wege sagen dasselbe.** `both_scans_agree` laeuft jeden vorhandenen Fall **zweimal**, `mode=FAST` und `mode=SLOW`, je gegen das **unabhaengige** `full_walk` — das bleibt unveraendert im Test und wandert **nicht** in den Produktivcode. | Den langsamen Generator auf Schrittweite 8 oder ohne Ausrichtung setzen → rot. |
| **R13** | dieselbe | **Die Wahl, an drei Literalen:** `relic_scan_mode({2013322}) == "fast"`, `relic_scan_mode({0x00FFFFFF}) == "fast"`, `relic_scan_mode({0x01000000}) == "slow"`. Erwartungen als Literale, **nicht** aus `RELIC_ID_CEILING` gerechnet. | `>=` zu `>` → der Grenzfall rot. |
| **R14** | dieselbe | **Es wird nicht mehr verweigert** (AK-228, Kern): bei einer Id ueber der Decke liefert `read_owned_relics` die Records — **Anzahl gegen ein Literal aus der Vorrichtung** — statt zu werfen. Der heutige Fall `test_a_relic_id_above_the_ceiling_is_refused_out_loud` wird **ersetzt**, nicht ergaenzt, und der Ersatz nennt im Docstring, was er abloest. | Den `raise` wieder einsetzen → rot. **Das ist die Mutation, die AK-228 selbst nennt.** |
| **R15** | dieselbe | **Der Weg steht am Bestand:** ein Datensatz ueber der Decke ergibt `Inventory.read_the_slow_way is True`, einer darunter `False`. | Feld fest auf `False` verdrahten → rot. |
| **R16** | `tests/test_hostile_savefile.py` (**vorhanden, erweitert**) | **SEC-022 gilt in beiden Wegen.** Die vorhandenen Dichtefaelle laufen zweimal, `FAST` und `SLOW`. | Die Schranke in den schnellen Zweig verschieben → im langsamen Weg rot. |
| **R17** | V5, `UI_SPEC` AK-228 | Der Rueckfallsatz steht in der Zeile; **dieselbe Reliktzahl** auf beiden Wegen; kein Dialog, keine Farbe ausser `MUTED`, keines der Woerter `error`/`failed`/`warning`/`corrupt`. | Id-Pruefung wieder werfen lassen. |
| **R18** | V5, `UI_SPEC` AK-229 | Das Praefix `Save could not be read: ` erscheint nur, wenn am Ende kein Bestand vorliegt. **Positivkontrolle:** dieselbe Pruefung gegen den **heutigen** Wortlaut (`… nothing is wrong with the save.`) **muss** anschlagen. | Den Rueckfallsatz wieder als Ausnahme werfen. |

**Was in keinen dieser Tests gehoert:** eine Zeitschranke. Zeiten stehen in
`docs/perf/baselines.md`, mit Umgebung und Streuung (L-001, L-009). Der
Rueckfallweg ist **langsam von Bauart**; ein Test, der ihn unter eine
Millisekundenzahl zwingt, misst den Rechner und nicht den Code.

---

---

## Was der `developer` ausdruecklich nicht tun soll — alle Fassungen

*Jeder Nachtrag hat diese Liste fortgeschrieben. Sie ist hier zusammengezogen,
weil eine Verbotsliste, die an sieben Stellen steht, keine Verbotsliste ist.
Die Fassungen stehen in der Reihenfolge ihrer Entstehung; keine hebt eine
fruehere auf, jede kommt hinzu.*

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

### Was der `developer` zusätzlich ausdrücklich nicht tun soll

11. **Kein zweiter `model.compute`-Aufruf unter `advisor/`.** Genau einer, in
    `evaluate.py`. Die Wächtertabelle wird um genau eine Zeile erweitert.
12. **Festgehaltene Relikte nicht als Anfangsbelegung in den Beam legen.**
    Sie sind kein Zustand, den die Suche verändern darf.
13. **Die Vorsortierung nicht gegen den leeren Build laufen lassen**, wenn
    etwas festgehalten ist.
14. **Keinen Fluch-Malus, kein Fluch-Gewicht, keinen Fluch-Sonderweg** in der
    Bewertung. Flüche sind Effekte.
15. **Den Haltezustand nicht persistieren** — nicht in `QSettings`, nicht auf
    Platte, auch nicht „nur für die Sitzung".
16. **Kein Bedienelement erfinden** — ob Schloss, wo es sitzt, wie es heisst,
    entscheidet der `ui-ux-designer`. Der `developer` baut, was die Suche
    braucht: den Haltezustand im Request.

### Was der `developer` zusätzlich nicht tun soll

17. **Keinen `QSettings`-Eintrag für den Haltezustand** und kein neues Schema
    (AD-017). Bei Zweifeln: verwerfen, nicht retten.
18. **Im Picker keine eigene Bewertung.** `relicpicker.py` zeigt an, was der
    Controller liefert; es gibt weiterhin genau eine `compute`-Stelle
    (`advisor/evaluate.py`).
19. **Den Gesamtlauf nicht streichen**, auch wenn der Picker die häufiger
    benutzte Ansicht wird. Es sind zwei Fragen (AD-018, Option B).
20. **Den Grenzbeitrag nicht in der Zielfunktion bilden.** `goal` bewertet
    einen `Build`; die Differenz bildet der Aufrufer. Sonst wandert
    Grundzustandswissen in die Registry aus AD-004.

### Was der `developer` zusätzlich ausdrücklich nicht tun soll

21. **Nicht entscheiden, ob 203,4 oder 244,1 richtig ist.** W2 trägt die
    heutigen Werte ein, nicht die vermuteten. Der Wert ist eine Messung, kein
    Entwurf.
22. **`weaponstab.py` nicht migrieren, sondern löschen** (W0). Es hat keinen
    Importeur und ist bereits gedriftet (`setRange(0, 25)` gegen die
    Tier-Semantik 1..4). Es zu migrieren hiesse zu entscheiden, was „+17"
    bedeutet — eine Frage ohne Antwort.
23. **Kein Vorgabewert für `target_tier`** in `candidate`/`rank_candidates`.
    Ein Vorgabewert setzt still das Slot-Tier ein und stellt Achse B als
    Fehler dar.
24. **Keine vierte `Basis` ohne AD-Eintrag.** Wer eine neue Frage braucht,
    meldet sie; er stellt sie sich nicht selbst zusammen.
25. **Den `compute`-Wächter nicht anfassen ausser zur Verallgemeinerung von
    `compute_call_sites`.** Seine Zusicherung `{app.py: 1}` bleibt wörtlich
    stehen.
26. **`scripts/capture_weapon_damage.py` nicht nach `nrplanner/` verschieben**,
    um den Wächter zufriedenzustellen. Es liegt absichtlich ausserhalb
    (QA-023); die Grenze wird im Docstring genannt, nicht umgangen.

### Was der `developer` zusätzlich nicht tun soll

27. **`weapons.WeaponRating.total` vor W5 nicht umdefinieren.** Solange es zwei
    Pfade gibt, ist es der Bezugspunkt der Differentialprüfung; eine
    Neuklammerung dort macht die Prüfung uninterpretierbar.
28. **Keine Toleranz in der Z1-Prüfung.** `pytest.approx` würde genau die
    Drift verstecken, wegen der die Zusicherung existiert.
29. **Beim Fallenlassen von `WeaponRating.total` in W5 die Sortierung von
    `weapons.rank` nicht ohne Zweitschlüssel lassen.** QA-059 hat gerade
    belegt, dass nicht reproduzierbare Sortierung in diesem Programm real ist;
    `(-summe, weapon["id"])`.

---

### Was der `developer` zusätzlich nicht tun soll

30. **Die `bonus`-Schleife in `weapons.rate` nicht auf `sum()`, `math.fsum()`
    oder kompensierte Summation umstellen** — auch nicht „im Vorbeigehen" bei
    W5. AD-024, Punkt 2.
31. **Keine der beiden Klammerungen als „genauer" bezeichnen**, weder im Code
    noch im Commit. Sie ist verbindlich, weil Z1 sie festlegt; sie ist nicht
    besser.
32. **Teilsummen über ausgewählte Schadensarten nicht gegen `final_total`
    prüfen.** Sie werden aus `final_per_type` gebildet und dort belassen.

---

### Was der `developer` zusätzlich ausdrücklich nicht tun soll

33. **`GoalScore.display` nicht in den Pool durchreichen.** Es formatiert den
    Absolutwert des Grundzustands; der Picker zeigt eine Differenz. Wer eine
    Formatregel für eine Differenz braucht, meldet sie (OF-21) und baut sie
    nicht nebenbei.
34. **`GoalScore.unknowns` nicht umbenennen** und `Baseline` nicht durch
    einen neuen per-Ziel-Typ ersetzen. Beides wäre Vereinheitlichung ohne
    Ertrag und zieht `UI_SPEC` AK-63 und drei Testdateien mit.
35. **Keinen `dict`- und keinen `list`-Typ in die neuen Felder.** Die Regel
    des Modul-Docstrings gilt unverändert (QA-066): die Formen, die eine
    Frage oder eine Antwort beschreiben, tragen kein Mapping und keine
    Liste.
36. **Keine zweite Ableitung des Waffentyps** für `model.is_conditional` in
    `candidates.py`. Die Zahl muss beschreiben, was `model.compute`
    tatsächlich weggelassen hat, nicht was eine zweite Rechnung dafür hält.
37. **`held_fingerprint` nicht „vorsichtshalber" stehenlassen**, auch nicht
    als private Funktion. Streichen heisst streichen; die drei Testfälle, die
    ihn benutzen, werden umgehängt oder gelöscht, nicht deaktiviert.
38. **Den Wortlaut der konditionalen Zeile nicht als endgültig setzen.** Er
    gehört dem `ui-ux-designer` (OF-20); im Code steht bis dahin die
    Fassung, die den **gezählten** Bestand beschreibt, nicht „your relics".

---

### Was der `developer` ausdruecklich **nicht** tun soll

- **`UI_SPEC.md` nicht anfassen.** AK-106 bis AK-132 und AK-220 bis AK-229
  gehoeren dem `ui-ux-designer`. Weicht der Bau ab, wird es gemeldet.
- **Keinen dritten Pfad einstellbar machen.** Der Zielort des Datenabzugs
  bleibt `paths.cache_dir()` (Festlegung des Directors, `UI_SPEC` §11).
- **`QSettings` nicht mit Literalen oeffnen.** Immer `favourites.ORG` /
  `favourites.APP`; `tests/test_settings_store.py` haelt das und hat schon
  einmal in den Speicher des Nutzers geschrieben.
- **Keinen `remove` auf `paths/…`.** Nicht beim Fehlschlag, nicht beim
  Aufraeumen, nicht beim Umschluesseln.
- **`full_walk` aus `tests/test_relic_scan_prefilter.py` nicht in den
  Produktivcode ziehen** und nicht durch den neuen Generator ersetzen. Es ist
  die unabhaengige Erwartung; teilt sie sich Code mit dem Geprueften, belegt
  der ganze Waechter nichts mehr.
- **Die Dichteschranke SEC-022 nicht anfassen**, in keinem der beiden Wege.
- **`RELIC_ID_CEILING` nicht erhoehen**, um den Rueckfall zu vermeiden. Die
  Decke ist die Bedingung, nicht das Problem.
- **`load()` nicht frueher abbrechen lassen** (AD-029 haelt).
- **Aus dem Spielordner nichts verschieben, kopieren oder loeschen** (GOAL,
  Nachtrag 06.09.2026).
- **Keine Suche von einer Laufwerkswurzel ohne Budget.** 400 Verzeichnisse,
  2 Sekunden, und beide Zahlen stehen im Test.
- **Nicht in `app.py`, `inventory.py` oder `tests/` arbeiten, solange T-142
  laeuft.**

---

---

## Pruefpunkte — alle Ergaenzungen

*Der Mindestumfang steht in AD-009 (Themenbereich F); die Nachtraege haben ihn
sechsmal ergaenzt. **Die Nummer 18 war einmal zweimal vergeben** — das ist in
der Praezisierung AD-009 (D4) aufgeloest, siehe Themenbereich F.*

### Prüfpunkte, Ergänzung zum Mindestumfang aus AD-009

8. **Ein festgehaltener Slot steht im Ergebnis unverändert** — der Test, der
   die Lesart „Randbedingung, nicht Startwert" absichert.
9. **Kein Handle eines festgehaltenen Relikts erscheint in einem freien Slot.**
10. **Symmetriefalle (AD-014.4):** `Wylder's Urn` `[Rot, Rot, Blau]`, der
    erste rote Slot festgehalten mit einem Relikt hohen Kandidatenindex. Der
    freie rote Slot **muss** ein Relikt mit kleinerem Index wählen dürfen.
    Ohne AD-014.4 fällt dieser Test — und nur dieser; bei einem Gefäss mit
    lauter verschiedenen Farben bliebe der Fehler unsichtbar. Das ist
    dieselbe Falle wie bei AD-013 Punkt 4 in AD-009.
11. **Cache:** gleiches Problem, anderer Halteinhalt ⇒ **kein** Treffer.
    Determinismus gilt bei festgehaltenem Haltezustand.
12. **Nullfall:** `h=0` liefert dasselbe Ergebnis wie ein Lauf ohne die
    Haltefunktion. Das ist die Bedingung, unter der die 0,46 s gemessen
    wurden, und sie muss messbar erhalten bleiben.
13. **Fluchbeitrag (AD-015):** ein Build mit verfluchtem Relikt bekommt vom
    Berater dieselbe Zahl wie über `Planner.current_build()`. Der Vergleich
    gegen die Oberfläche ist die eigentliche Zusage, nicht die interne
    Konsistenz des Beraters.
14. **Alle Slots gehalten:** kein Suchlauf, Ergebnis ist der bewertete
    Ist-Zustand, und `unknowns` sagt es.

### Prüfpunkte, Ergänzung (zu AD-009 und Nachtrag I)

15. **Grenzbeitrag = Vorsortierwert.** Der im Picker gezeigte Wert eines
    Kandidaten ist bitgleich die Zahl, nach der der Gesamtlauf denselben
    Kandidaten für denselben Slot vorsortiert. Zwei Ansichten, eine Zahl.
16. **Abnehmender Ertrag ist nachweisbar:** derselbe `+Stärke`-Kandidat hat
    bei hohem Stärkewert einen kleineren Grenzbeitrag als bei niedrigem. Das
    ist die Zusage des Nutzers an sich selbst und muss ein Test sein, kein
    Argument. **Fällt dieser Test, ist die Ursache in `damage.py`/`model.py`
    zu suchen, nicht im Berater.**
17. **Halt überlebt den Gefässwechsel und kommt zurück** (AD-017), und ein
    Halt auf ein nicht mehr besessenes Relikt fällt weg und wird genannt.
18. **Kein `QSettings`-Zugriff im Berater-Pfad.** Der Wächtertest aus QA-049
    deckt den literalen Aufbau ab; hier genügt, dass unter `advisor/` und im
    Haltezustand kein `QSettings` vorkommt.

### Prüfpunkte, Ergänzung

28. **Untere Schicht bitgleich über den ganzen Umbau.** (Bis 05.09.2026 als
    Prüfpunkt 18 geführt; umnummeriert in Nachtrag VI, weil Nachtrag II
    dieselbe Nummer bereits vergeben hatte.) Über die
    Differentialfälle aus Zyklus 2: `weapons.rate` liefert vor und nach W0–W5
    dieselben Zahlen. Abweichungen dürfen nur oberhalb der Fassade entstehen.
19. **Kachel und Tafel nennen dieselbe Zahl.** Nach W3, headless über die
    echten Widgets: für jeden gefüllten Slot ist die Kachelzahl gleich der
    Gesamtzahl der Tafel. Das ist der Test, den es zu QA-018 nie gab.
20. **Das Ziel-Tier überlebt den Umbau.** Nach W4: Slot auf Tier 3, Spinbox
    auf 1, kein Relikt — der Arsenal-Tab muss weiterhin auf Tier 1 ranken und
    **darf** von Kachel und Tafel abweichen (AD-020, Punkt 1). Ein Test, der
    hier Gleichheit fordert, wäre der Fehler, nicht der Befund.
21. **Der zweite Wächter sieht jeden Weg um sich herum.** Dieselben sieben
    Schreibweisen wie beim `compute`-Wächter, gegen `weapons.rate`/`rank`.
22. **Der Golden-Vertrag ist erweitert, bevor er gebrochen wird.** Der
    Docstring von `test_weapon_damage_golden.py` nennt die zweite erlaubte
    Neuaufnahme-Bedingung (dokumentierte Entscheidung, AD-/QA-Nummer im
    Commit), **bevor** W3 die erste Neuaufnahme auslöst.

### Prüfpunkte, Ergänzung

23. **`total == sum(per_type.values())` exakt**, je Schicht, über die
    Differentialfälle aus W1.
24. **Der Vorbehalt aus AD-023 erscheint genau dann**, wenn das Kandidatenfeld
    mindestens einen Effekt mit einem Feld aus `AR_RATE_FOR` oder dessen
    klassengebundener Variante enthält — und sonst nicht. Zwei Fälle, beide
    konstruierbar, weil die Familie vollständig aufgezählt ist.
25. **Nach W5 gibt es im Programm genau eine Summation** der Schadensarten:
    `WeaponRating.total` hat keinen Leser mehr oder existiert nicht mehr.

### Prüfpunkte, Ergänzung

26. **Einartige Armaturen sind gegenüber der Klammerung invariant.** Bei einer
    Schadensart sind beide Klammerungen identisch — das ist der Gegenprobe-Fall
    zur Messung des `developer` und eine billige Zusicherung, dass die
    gemessene Verschiebung wirklich aus der Klammerung stammt und nicht aus
    etwas anderem, das W4 mitgebracht hat.
27. **Nach W5 sortiert `weapons.rank` reproduzierbar**, auch bei
    ULP-Gleichstand: zweimal derselbe Lauf, byteweise dieselbe Reihenfolge.
    Verwandt mit QA-059, aber ein eigener Fall.

### Prüfpunkte, Ergänzung (zu AD-009, Nachträge I bis V)

29. **Jede Zielrichtung hat einen Geltungsbereich, und zwar ohne
    Spielinstallation.** Für jeden Eintrag der Registry ist `Goal.scope`
    nicht leer, geprüft **ohne** `game_data`, ohne `Build`, ohne Bestand.
    Das ist der Fall, der QA-106 nicht trifft: er läuft auf jedem Runner.
    **Gegenbau:** `scope` einer Zielrichtung leeren ⇒ rot.
30. **Kein Satz steht in beiden Klassen.** Kein String aus `Goal.scope`
    erscheint in `GoalScore.unknowns`, `Baseline.unknowns` oder
    `SlotPool.unknowns` desselben Laufs. **Gegenbau:** einen Satz aus
    `scope` zusätzlich in `unknowns` legen ⇒ rot. Läuft ohne Datensatz,
    soweit über die Modulkonstanten geprüft.
31. **Ein Laufbefund überlebt nicht jeden Lauf.** Über mindestens zwei
    wirklich herstellbare Kontexte derselben Zielrichtung (mit und ohne
    Referenzwaffe) ist der **Durchschnitt** der `unknowns`-Mengen leer: ein
    Satz, der in jedem Lauf dasteht, ist ein Verfahrenssatz und gehört nach
    `Goal.scope`. **Gegenbau:** einen der vier Geltungsbereichssätze zurück
    in `unknowns` schieben ⇒ er steht in beiden Läufen ⇒ rot. Braucht den
    Datensatz und überspringt ohne Spielinstallation (QA-106, stehende
    Einschränkung).
32. **Der Pool trägt, was die Zielrichtung nicht wusste.** Für jeden Pool und
    jede Zielrichtung gilt: `Baseline.unknowns` und `weights_note` sind
    wortgleich das, was `goal.score(base_build, ctx)` geliefert hat, und
    `unit` ebenso. **Gegenbau:** in `pool()` wieder nur `.value` übernehmen
    ⇒ rot. Das ist der Wächter über QA-102.
33. **Die konditionale Zeile zählt, was wirklich nicht gezählt wurde.** Ein
    Bestand mit K Relikten, deren Effekt gated und nicht deklariert ist,
    ergibt eine Zeile mit K; derselbe Bestand mit denselben Effekten
    **deklariert** ergibt **keine** Zeile. **Gegenbau:** die Zeile aus einer
    zweiten Ableitung über die Relikt-Definitionen bilden statt aus dem
    `Build` ⇒ der deklarierte Fall zählt weiter mit ⇒ rot.
34. **Der Haltezustand ist im Schlüssel, ohne zweite Form.** Zwei Requests,
    die sich nur im Halt unterscheiden — auch nur darin, **in welchem Slot**
    gehalten wird —, sind verschieden und hashen verschieden. Ein
    gehaltenes Custom-Relikt (`handle=None`) neben einem besessenen bricht
    weder Gleichheit noch Hash. **Gegenbau:** `SlotProblem.held` aus dem
    Request nehmen oder zu einer sortierten Menge machen ⇒ rot. Ersetzt den
    Wächter über `held_fingerprint`.

---

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

### Risiken, Ergänzung

| Risiko | Woran man es merkt | Rückweg |
|--------|--------------------|---------|
| Der Grundzustand wird an **einer** Bewertungsstelle vergessen (typisch: der Vorsortierung). | Vorschläge doppeln einen Effekt, den das festgehaltene Relikt bereits kappt (`NON_ACCUMULATING`, `isStrongestEffect`) — die Punktzahl steigt nicht, der Vorschlag sieht trotzdem plausibel aus. | Es gibt nur eine Bewertungsstelle (AD-014.1), und der `compute`-Wächter erzwingt das. Kein zweiter Rückweg nötig. |
| Festhalten wird doch als Startwert gebaut. | Der festgehaltene Slot ändert sich im Ergebnis. | Prüfpunkt 8. |
| Cache liefert ein Ergebnis zum falschen Haltezustand. | Gefäss weg und zurück, danach ist ein gehaltener Slot überschrieben. | Prüfpunkt 11; `held_fingerprint` im Schlüssel (AD-016). |
| Ein Fluch steht im Vorschlag, ist aber nicht in die Rechnung eingegangen (konditional), oder umgekehrt. | Anzeige und Statblatt widersprechen sich beim selben Relikt. | Flüche werden aus `Build.sources` ausgewiesen, nicht aus der Relikt-Definition (AD-015). |
| Die isolierte Vorsortierung an weissen Slots (OF-10) bleibt die schärfste Schwäche. | Unverändert wie in AD-003 beschrieben. | Sie **verkleinert** sich mit jedem festgehaltenen Slot, weil die Vorsortierung dann Kontext hat. OF-10 bleibt trotzdem offen — für `h=0` ändert sich nichts. |

### Risiken, Ergänzung

| Risiko | Woran man es merkt | Rückweg |
|--------|--------------------|---------|
| **QA-018 trifft den Kern von AD-018.** Der Waffen-Tab nennt 203,4, die Detailtafel 244,1 für dieselbe Waffe — ein offener, gemessener Widerspruch in genau der Rechnung, aus der der Grenzbeitrag entsteht. Ein konstanter Versatz kürzt sich in einer Differenz heraus, eine falsche **Steigung** nicht — und der abnehmende Ertrag *ist* die Steigung. | Prüfpunkt 16 und der Vergleich der beiden Anzeigen. | **QA-018 ist damit keine Nebenbaustelle mehr, sondern Vorbedingung des Hauptwegs.** Empfehlung an den `director`: vor S10 einplanen. Solange er offen ist, trägt jede Picker-Zeile den Attack-Rating-Vorbehalt aus AD-004 sichtbar, nicht aufklappbar. |
| Der Berater rechnet jetzt bei jeder Interaktion; eine spätere Verlangsamung von `model.compute()` wird sofort spürbar. | Ruckeln beim Tippen im Picker-Filter. | Entprellung erhöhen; Messpunkt in S11; im Äussersten AD-002 Option C, die weiterhin nachrüstbar ist. |
| Der Spieler baut sich slotweise einen greedy Build und hält ihn für das Beste. | Der `Optimize`-Lauf findet mehr, als die sechs Picker-Entscheidungen ergaben. | Kein Fehler, sondern die Natur der beiden Fragen — aber die Pflichtzeile aus AD-018.3 muss dastehen. |
| Ein Halt zeigt auf ein eingeschmolzenes Relikt. | Nach einem Neu-Scan des Saves. | AD-017.3: der Halt fällt beim Bauen des Requests weg und wird genannt. |

### Risiken, Ergänzung

| Risiko | Woran man es merkt | Rückweg |
|--------|--------------------|---------|
| Die Neuaufnahme des Golden-Stands bei W3/W4 löscht den Beleg, dass die Rechnung unverändert ist. | Ein grüner Lauf, der nichts mehr belegt. | Prüfpunkt 28 (bis 05.09.2026: 18) hängt an der **unteren** Schicht und überlebt die Neuaufnahme. Er ist der eigentliche Beleg; der Golden-Stand ist danach der Beleg für die Anzeige. |
| Die Fassade vereinheitlicht Achse B mit und der Arsenal-Tab rankt auf dem Slot-Tier. | Prüfpunkt 20 fällt. | AD-020, Punkt 1: `target_tier` ist Pflichtargument ohne Vorgabewert. |
| W6 wird nie beantwortet und `MULTIPLIERS_FOR[CANDIDATE]` bleibt auf dem Platzhalter stehen. | Nichts — genau das ist die Gefahr. | Der Platzhalter ist keiner: W2 setzt den **heutigen** Wert (`False`), das Verhalten ist damit unverändert und der Vorbehalt aus AD-004 bleibt sichtbar, bis der Nutzer misst. |
| Eine Zielrichtung des Beraters vergleicht Waffen gegeneinander, bevor W6 steht. | Eine Empfehlung, die die Waffe wechselt. | Solche Zielrichtungen bleiben bis W6 aus der Registry (AD-004) heraus. |

### Risiken, Ergänzung

| Risiko | Woran man es merkt | Rückweg |
|--------|--------------------|---------|
| Die Trennung wird gebaut, aber die Oberfläche liest nur eine Hälfte — `UI_SPEC` AK-63 nennt heute genau eine Quelle. Dann zeigt der Picker **weniger** als vorher, und A7 ist auf dem Hauptweg schlechter statt besser. | Zeile 4 des Pickers steht leer oder trägt nur die AD-018.3-Pflichtzeile. | OF-19: `UI_SPEC` nachziehen, **bevor** S10 gebaut wird. Prüfpunkt 29 hält die Registry-Hälfte, Prüfpunkt 32 die Ergebnis-Hälfte; die Anzeige selbst hält beides erst, wenn AK-63 zwei Quellen nennt. |
| Die konditionale Zeile nennt eine Anzahl, die der Spieler auf dem Schirm nicht nachzählen kann (weil sie über einen anderen Bestand gebildet wurde als den angezeigten). | Ein Spieler zählt vier situative Relikte und die Zeile sagt sieben. | Prüfpunkt 33 und die Festlegung „gezählt über die Kandidaten dieses Pools, gebildet aus dem `Build`". |
| `held_fingerprint` wird gestrichen, und mit ihm fällt still eine echte Zusicherung weg: dass ein **gehaltenes Custom-Relikt** (`handle=None`) den Schlüssel nicht sprengt. Der heutige Fall prüft das über den `repr`-Sort des Fingerabdrucks. | Nichts — bis ein Spieler ein Custom-Relikt festhält. | Prüfpunkt 34, zweiter Satz. Der Fall wird **nicht gelöscht**, sondern auf `AdvisorRequest` umgehängt. |
| Der Cache trifft seltener als AD-008 versprochen hat, und S11 misst es als Regression. | Trefferquote in S11 unter der Erwartung aus AD-008. | Das ist die bewusste Folge von D3 und keine Regression; die Zahl aus AD-008 gilt für den Schlüssel nicht mehr. Wenn es doch drückt: kanonische Form in S9 nachrüsten, **mit** Rückabbildung, nicht ohne. |
| Der `developer` baut aus QA-102 heraus auch `display` in den Pool und der Picker zeigt den Absolutwert des Grundzustands als Kandidatenwert. | Eine Karte zeigt „Attack rating 122" statt „+12.4". | „Was ausdrücklich nicht über die Poolgrenze fährt", Punkt 1, und Nicht-tun-Regel 33. |

---

### Risiken und Pruefpunkte, neu

| Risiko | Woran man es merkt | Rueckweg |
|---|---|---|
| Zwei Spuren rechnen gleichzeitig und A6s 6-s-Zeile faellt | U7 misst `Optimize` mit gleichzeitig laufender Picker-Frage | A6 bekommt die Randbedingung „ohne gleichzeitige zweite Spur", **oder** die Picker-Spur bekommt Vorrang. Beides ist eine Entscheidung, kein Fix — sie faellt an der Zahl. |
| Der Hauptthread-Rest ist selbst groesser als 50 ms | U7 misst Anfragebau + `frozen_inventory` (309 Kopien) + `inventory_fingerprint` (sha256 ueber 309 Zeilen) **getrennt** vom Lauf | Das Einfrieren einmal je Bestandsaenderung statt einmal je Frage; das ist ein eigener Entwurf und beruehrt AD-007s Fingerabdruck. |
| Die kanonische Form nach Punkt 3 liefert einen anderen `SlotPool` | U5a vergleicht vorher/nachher ueber Handles und Punktzahlen | Slot-Index doch als Feld in `AdvisorRequest` — dann ist AD-018s „keine zweite Schluesselform" ausdruecklich zu revidieren, nicht stillschweigend. |
| Der Vorfilter findet auf einer praeparierten Datei weniger als der heutige Scan | U2 | `array`-Rueckfall aus T-118 Abschnitt 6 (2,1x statt 45x). |
| Der Wartezustand blitzt bei schnellen Slots auf (32–82 ms, S11-C) | am laufenden Fenster, nach U5b | Die 100-ms-Entprellung deckt den Fall bereits — der Wartezustand darf erst **nach** dem Start des Laufs erscheinen, wie AK-09 es fuer die Advisor bar schon regelt (`WAIT_VISIBLE_MS`). |

---

### Risiken und Pruefpunkte, neu (zu den Zeilen aus Nachtrag VIII)

| Risiko | Woran man es merkt | Rueckweg |
|---|---|---|
| Ein Picker-Cache-Eintrag ist viel groesser als die 33,4 KiB, auf denen die 64 steht | U7 misst ihn gegen die 140-KiB-Schranke (IX-3.2) | zurueck auf 32; die Groessenfrage kommt zum `architect` |
| Der `developer` baut nur einen der beiden Antwortwege (Rueckgabewert **oder** Signal) | W5 samt Gegenprobe | — |
| `GOAL_ORDER` und `GOALS` laufen auseinander, und die Wiederverwendung des Pools faellt still | W4 | — |
| Die Anzeige liest ihre Richtung weiter aus `SlotPool.rank_by` | mit IX-2 **immer** falsch statt manchmal; AK-205 und sein Gegenbau | — |
| Die 0 ms verstopfen die Spur, weil doch zwei Fragen kurz hintereinander kommen | am laufenden Fenster: zwei Oeffnungen in Folge; „ein Lauf zur Zeit" haelt ohnehin (`worker.py:285-286`, `307-321`) | die 100 ms zurueck (IX-1.2) |

---

### Risiken und Pruefpunkte, neu (zu Nachtrag VIII und IX)

| Risiko | Woran man es merkt | Rueckweg |
|---|---|---|
| Der sechste W6-Fall stellt seinen Fall nicht her und ist immer gruen | die Mutation aus U9 ueberlebt | Fall streichen und als Befund melden; die Zusage aus X-0 traegt dann den dritten Punkt nicht |
| Eine fuenfte unterbrechende Stelle entsteht und schweigt | **W8** | Tabelle ergaenzen **oder** die Stelle einen Ausgang senden lassen — die Zeile zu schreiben ist die Entscheidung |
| `shutdown` erhoeht die Generation und etwas anderes las sie mit | die Suite; `ask` gibt die Generation zurueck, `shutdown` an niemanden | eine Zeile zurueck |
| W1 waechst zur Pflegelast, weil jede neue rechnende Funktion eine Zeile braucht | mehr als zwei neue Zeilen in einem Zyklus | dann ist X-1 Option C (gebuendelte Ausgaenge) und eine Namenskonvention statt einer Tabelle zu pruefen |

---

### Risiken und Pruefpunkte

| Risiko | Woran man es merkt | Rueckweg |
|---|---|---|
| **Der gemerkte Pfad zeigt auf ein nicht erreichbares Netzlaufwerk.** Die Gueltigkeitspruefung ist ein `stat` und kann bei totem UNC-Ziel zehn Sekunden blockieren — **vor** dem ersten Fenster. Nicht gemessen; auf diesem Rechner ohne Freigabe nicht messbar. | Ein `power-user`-Lauf mit einem gemerkten UNC-Pfad auf einen abgeschalteten Host: Zeit bis zum ersten Fenster. | Die Pruefung wandert hinter den Splash oder in einen Faden mit Frist. Das ist ein Nachtrag zu AD-030, kein Umbau. |
| **`datasource` bekommt ueber `gamepath` eine Qt-Abhaengigkeit.** Heute ist es Qt-frei. | Ein Import von `nrplanner.datasource` ohne PySide6 im Pfad. | Lazy-Import in der Funktion (so entworfen). Reicht das nicht, kehrt die Richtung sich um und `app.py` reicht den Pfad als Argument durch — teurer, weil vier Aufrufstellen dann Parameter tragen. |
| **Der Rueckfall macht den Start wieder sechs Sekunden lang** und friert das Fenster ein, wenn V5 (Stufe B) noch nicht steht. | Trifft nur ein, wenn ein Patch die Ids umnummeriert. | V5 vor oder unmittelbar nach V4 bauen. Sonst bleibt nur die Verweigerung, und die ist verworfen. |
| **Der Ordnerdialog nimmt einen Ordner an, aus dem eine fremde DLL geladen wird.** | `security-reviewer`, OF-31. | Stufe 2 haerten: ein harter Identitaetsnachweis statt Text W1. `UI_SPEC` §4.3 nennt ihn selbst als offen — *„ob es eine `nightreign.exe` o. ae. gibt, an der die Identitaet hart haengen koennte. Der Code kennt keinen solchen Namen."* Das ist an einer echten Installation zu pruefen. |
| **V2 ist zu gross** (Fensterart, sieben Texte, Dialog, fuenf Zustaende, Skalierung). | Der Auftrag laeuft ueber 60 Minuten oder ueber die Zugschwelle. | Schnitt entlang der Textlage: erst der Erststart-Zweig (A1/E1/W1/C1/C2), dann der Spaeter-Zweig (A2/A3). A3 haengt am Datum des Abzugs und ist der einzige Teil, der `datasource` befragt. |

---

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

### Bewusst nicht getan, Ergänzung

- **`held_fingerprint` nicht positionsabhängig gemacht, sondern gestrichen.**
  *Wieder interessant, wenn:* S9 eine kanonische Form braucht — dann
  positionsabhängig, mit Rückabbildung, und mit dem Wächter auf dem
  Schlüssel statt auf dem abgeleiteten Wert.
- **Die kanonische Form aus AD-008 nicht als Cache-Schlüssel gebaut.**
  *Wieder interessant, wenn:* S11 misst, dass die Trefferquote drückt, **und**
  die Rückabbildung der freien Slots gebaut ist. Ohne die Rückabbildung ist
  die kanonische Form kein Schlüssel, sondern ein überschriebener Halt.
- **Keine Formatregel für eine Differenz je Zielrichtung.** *Wieder
  interessant, wenn:* S8/S10 gebaut werden — dann als Entscheidung des
  `ui-ux-designer`, nicht als Feld, das im Vorbeigehen im Pool landet.
- **Kein Kennzeichen am einzelnen Satz** (Option B). *Wieder interessant,
  wenn:* eine dritte Klasse auftaucht, die weder in die Registry noch ins
  Ergebnis passt. Bis dahin ist der Ort die Klasse.

---

### Bewusst nicht getan, Ergänzung

- **Die Waffentyp-Schranke nicht aus `CONDITIONAL_FIELDS` genommen**
  (Option E). *Wieder interessant, wenn:* jemand die dritte Ablage aus E'
  ohnehin baut — also eine Klasse „gated, in keine Summe, kein Schalter". Vor
  E' muss messbar sein, dass die 46 Schalter dem Spieler nichts wert sind;
  heute beantworten sie eine Frage, die er durch Waffenwechsel wirklich
  beantworten kann.
- **`wepTypeTriggerCount` nicht auswertbar gemacht.** Das Raster hält sechs
  Armaturen; man **könnte** zählen, wie viele davon den verlangten Typ
  tragen, und die Schranke damit erfüllen. *Wieder interessant, wenn:* eine
  Ablesung im laufenden Spiel bestätigt, welche Zahl das Feld meint. Ohne
  diese Ablesung wäre es geraten — 82 Effekte hängen daran, und A7 verbietet
  die Vermutung.
- **QA-185 nicht mitbehoben** (`Build.qualitative` trägt keine Effekt-Id).
  Diese AD **berührt** sie: die richtige Grenze zwischen `qualitative` und
  `situational` wird erst prüfbar, wenn beide Listen dieselbe Id führen —
  heute muss `explain` über den Namen zurückschliessen. Die Entscheidung
  hängt nicht daran, der spätere Wächter schon. Eigener Auftrag, eigener
  Code, gerade in fremder Hand.
- **Den Wortlaut von 4.9b nicht angefasst.** Er gehört dem
  `ui-ux-designer`; diese AD sagt nur, **welche Menge** er beschreiben muss.

---

### Bewusst nicht getan, neu

- **Kein eigener Thread-Weg fuer den Picker** (AD-028 Option C). *Wieder
  interessant, wenn:* die beiden Antwortformen so weit auseinanderlaufen,
  dass eine Klasse zwei Betriebsarten haette statt einer austauschbaren
  Funktion.
- **Der Picker rechnet nicht „nur schneller" im Hauptthread** (AD-028
  Option A). *Wieder interessant, wenn:* die Slot-Frage je unter 50 ms faellt
  — nach P1a sind es gemessen 245,5 ms, also Faktor 5 zu weit.
- **`load()` bricht nicht frueher ab** (AD-029). Grund und
  Reaktivierungsbedingung stehen dort.
- **Der Ergebnis-Cache bleibt im Speicher** (AD-007 haelt). Die Bedingung aus
  T-118 Abschnitt 6 — „wenn der Prozessstart nach AD-029 den Berater
  dominiert" — ist nach Stufe C zu pruefen: bei hergeleiteten 1,1 s Start
  gegen 5,02 s Gesamtlauf tut er es weiter nicht.
- **Keine Zeitschranke in der Testsuite.** Zeiten gehoeren in
  `docs/perf/baselines.md`, mit Umgebung und Streuung (L-001, L-009).

---

### Bewusst nicht getan, neu (zu Nachtrag VIII)

- **Kein Vorwaermen der Slot-Pools** (IX-5). Grund und Wiederkehrbedingung
  stehen dort; das Mittel waere dann nicht `pools()`.
- **Kein Cache-Blick vor dem Zeitgeber fuer beide Spuren** (IX-1 Option D).
  *Wieder interessant, wenn:* die Advisor bar ihren Wartezustand so umbaut,
  dass ein sofort gezeichneter Treffer nicht mehr flackern kann.
- **Die 100-ms-Entprellung wird nicht geloescht, nur auf 0 gesetzt** (IX-1.2).
  Sie ist die richtige Zahl fuer den Fall, den `UI_SPEC` §4 als Rueckweg
  vorsieht.
- **Kein Feld `slot_index` in `AdvisorRequest`** — AD-028.3 haelt; nur das Feld
  `goal_id` wird fuer die Picker-Spur kanonisch belegt (IX-2).

---

### Bewusst nicht getan, neu (zu Nachtrag VIII und IX)

- **Kein Signal aus `shutdown`** (X-1 Option B). *Wieder interessant, wenn:*
  eine Spur einmal ohne schliessendes Fenster beendet wird — dann hoert
  jemand zu, und Schweigen waere falsch.
- **Kein gebuendelter Ausgang in `_interrupt_the_running_worker`** (X-1
  Option C). *Wieder interessant, wenn:* W8 ein zweites Mal wegen einer neuen
  Aufrufstelle rot wird.
- **Keine Verhaltenszusage ueber die Zahl der Aufrufer** (X-2). Sie ist als
  Prosa nicht bewachbar und war am Tag ihrer Niederschrift falsch gezaehlt.
- **Keine Umbenennung des W-Kreises** (Kopf dieses Nachtrags). Sie beruehrt
  Testnamen und Berichte und gehoert dem `director`.
- **Kein Umbau von `app.py` fuer den Wortlaut von W1** (X-3).

---

### Bewusst nicht getan

- **Keine eigene Datei fuer die zwei Pfade** (Option B zu AD-030). *Wieder
  interessant, wenn:* ein vierter oder fuenfter Pfad dazukaeme oder eine
  Einstellungsseite entstuende — dann ist ein Format billiger als fuenf
  Einzelschluessel. Solange es zwei sind, ist der vorhandene Speicher der Ort.
- **Kein `gamefiles.set_override()`.** Globaler veraenderlicher Zustand in der
  untersten Schicht, mit einer Reihenfolgeabhaengigkeit beim Start, die kein
  Test billig festhaelt. *Wieder interessant, wenn:* `nrdata` je ohne
  `nrplanner` ausgeliefert wuerde.
- **Kein Loeschen eines unbrauchbaren Eintrags.** *Wieder interessant, wenn:*
  ein gemessener Fall zeigt, dass ein Altwert einen Nutzer wirklich behindert —
  bis dahin kostet er einen `stat` je Start, und `remove` hat zwei der drei
  Datenverluste verursacht.
- **Keine Einstellungsseite fuer die beiden Pfade.** `UI_SPEC` §11 stellt sie
  ausdruecklich zurueck; sie ist offene Frage 1 des `ui-ux-designer`.
- **Kein zweiter Rekord-Leser fuer den langsamen Weg** (AD-031, Punkt 2).
  *Wieder interessant, wenn:* die beiden Wege je verschiedene Felder lesen
  muessten — dann sind es zwei Formate und nicht zwei Wege.
- **Kein Rueckfall fuer `_loadout_marker_offsets`.** Seine Konstante ist die des
  Programms, nicht die der Spieldaten; ein Bruch waere laut und leer, nicht
  still und kurz. *Wieder interessant, wenn:* ein Patch die Marker-Basis
  verschiebt — dann ist es dieselbe Entscheidung ein zweites Mal.
- **Keine Aenderung an `RELIC_ID_CEILING`.**

---

---

> **Die offenen Fragen stehen ab sofort in `ARCHITECTURE_REGISTER.md`,
> Tabelle 2.** Dort steht je Nummer, ob sie noch offen ist, wer auf sie
> wartet, und welche Fundstelle eine Antwort belegt. Stand 12.09.2026:
> **32 Nummern, davon 12 offen, 17 beantwortet, 1 beantwortet mit benanntem
> Rest, 1 unklar, 1 nie vergeben.** Der Wortlaut jeder Frage steht unveraendert
> unten — das Register ersetzt ihn nicht, es sortiert ihn.

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

---

### Offene Fragen, neu

**OF-12 — an den App Designer, über `director`:** Überlebt ein Haltezustand
den Wechsel von Gefäss, Nightfarer oder Deep-Schalter? Bei einem Wechsel
ändern sich Zahl, Farbe und Bedeutung der Slots; ein „Slot 2 gehalten" von
vorher zeigt danach auf etwas anderes. Die Architektur trägt beides. Der
Entwurfsvorschlag lautet: **Haltezustand verfällt** bei jeder Änderung, die
die Slotmenge verändert, und wird nicht über Programmstarts gemerkt. Wird das
bestätigt, ändert sich an AD-014 bis AD-016 nichts; wird es verneint, braucht
es eine Regel, welcher Halt auf welchen Slot abgebildet wird.

**OF-13 — an den App Designer, über `director`:** Ein Fluch, der ein Feld
bewegt, das die gewählte Zielrichtung nicht misst (`-HP` unter „Maximise
damage"), ist im Build verrechnet, aber nicht in der Rangzahl. Der Entwurf
**nennt** ihn im Vorschlag und in `unknowns` (AD-015). Genügt Nennen, oder
soll ein solches Relikt schlechter gerankt oder ausgeschlossen werden? Eine
Abwertung bräuchte Gewichte über Dimensionen hinweg, die die Spieldateien
nicht hergeben — sie wäre also eine erfundene Zahl und stünde gegen A7.
Der `developer` kann ohne diese Antwort beginnen: ein Ausschluss wäre später
ein Kandidatenfilter in `candidates.py` und berührt weder Suche noch
Bewertung.

**Erledigt am 2026-09-02** (Nutzerentscheid in `GOAL.md`): `UI_SPEC` F1
(Slots festhalten — **ja**, siehe AD-014) und F3 (Flüche mitbewerten —
**ja**, siehe AD-015). `UI_SPEC` F2 und F4 bleiben beim `ui-ux-designer`
bzw. beim Nutzer; keine der beiden bewegt diesen Entwurf.


---

### Offene Frage, neu

**OF-15 — an den App Designer, über `director`:** Soll der Haltezustand einen
**Programmneustart** überleben? AD-017 liest die Antwort des Nutzers als
„innerhalb der Sitzung, gebunden an Held und Gefäss" und kommt damit ohne
persistenten Speicher aus. Soll er den Neustart überleben, ist das ein
eigener Auftrag mit eigenem Schema, der Migrationsnachbedingung aus Zyklus
4/5 und einer ausgesprochenen Regel für Relikte, die nicht mehr im Besitz
sind — nicht eine Zeile mehr im Berater.

---

### Offene Fragen, neu

**OF-16 — an den App Designer, über `director`, entscheidet W6:** Die
Spielmessung aus `docs/state.md` ist unverändert die offene Frage. Neu ist,
dass sie **nur noch einen Wert** bestimmt (`MULTIPLIERS_FOR[Basis.CANDIDATE]`)
und nicht mehr den Bauplan. Sie blockiert ab W5 die angezeigte Zahl, nicht
mehr den Berater.

**OF-17 — an den `director`:** Darf `tests/golden/weapon_damage.json` bei W3
und W4 neu aufgenommen werden, mit AD-019 im Commit-Text als Grund? Ohne diese
Freigabe hält W3 an, weil sein eigener Vertrag die Neuaufnahme heute nur nach
einem Spiel-Patch erlaubt. **Empfehlung: ja, aber erst nachdem Prüfpunkt 28
(bis 05.09.2026: 18) grün ist** — sonst gibt es keinen zweiten Beleg mehr.

**OF-18 — an den `ui-ux-designer`, nicht an mich:** `Basis.EQUIPPED`,
`CANDIDATE` und `BARE` sind drei verschiedene Fragen, die gleichzeitig auf dem
Schirm stehen können. Die Benennung der Spalten und Beschriftungen (QA-018
Weg B) sollte diese drei Fragen unterscheidbar machen; welche Wörter, ist
nicht meine Entscheidung. Der Entwurf liefert `Rating.basis` mit, damit die
Anzeige benennen **kann**, was sie zeigt.

---

### Offene Fragen, neu

**OF-19 — an den `director`, weiterzugeben an den `ui-ux-designer`:**
`UI_SPEC` AK-63 (T-052, 2026-09-05) legt fest, dass Zeile 4 des Pickers und
Punkt 4 des Why-Dialogs **ausschliesslich** die Sätze aus
`GoalScore.unknowns` der gewählten Zielrichtung zeigen. Nach AD-025 sind es
**zwei** Quellen: `Goal.scope` (der Geltungsbereich, immer) und die
Laufbefunde des Pools (`Baseline.unknowns`, `SlotPool.unknowns`,
`weights_note`). Die **Absicht** von AK-63 bleibt vollständig erfüllbar — ein
fünfter Satz in `advisor/goals.py` erscheint danach an beiden Anzeigeorten,
ohne dass ein UI-String angefasst wird. Der **Wortlaut** von AK-63 nennt eine
Quelle, wo es zwei gibt. Wird AK-63 nicht nachgezogen, zeigt eine
spec-treue Umsetzung nach der Trennung **weniger** als heute. Das ist der
einzige Punkt dieses Nachtrags, der A7 verschlechtern kann.

**OF-20 — an den `ui-ux-designer`, über den `director`:** der Wortlaut der
konditionalen Zeile. AD-004 sagt „N of your relics", gezählt wird nach dieser
AD über die Kandidaten **dieses Pools**. Gehört in dieselbe Runde wie QA-108
(„of this colour" stimmt am weissen Slot nicht) — es sind zwei Zeilen
desselben Bautyps im selben Feld, und sie sollten zusammen geschrieben
werden.

**OF-21 — an den `director`:** die Formatierung einer **Differenz** je
Zielrichtung (`+12.4 AR` gegen `−18`) hat heute nirgends einen Ort. Ich lese
sie als S8/S10 und ausdrücklich **nicht** als Teil von T-048. Bestätigung
erbeten, weil QA-102 „`display` fällt weg" meldet und der nächstliegende
Griff der falsche wäre.

**OF-22 — an den `director`:** AD-008 hatte zwei Argumente — Trefferquote im
Cache **und** Prüfäquivalenz (26 bzw. 47 kanonische Probleme statt 74
Gefässe, mit der A3 überhaupt vollständig prüfbar wird). D3 hebt das erste
auf. Ich lese das zweite als **unberührt**, weil es nicht am Cache hängt.
Falls der `director` das anders sieht, ist der Prüfumfang für A3 neu zu
bemessen, und das trifft den `qa-engineer`, nicht den `developer`.

---

### Offene Fragen, neu

**OF-23 — an den `director`, weiterzugeben an den `ui-ux-designer`:**
`GATE_FIELDS["triggerOnWepType"]` beschriftet **72 Effekte** des Datensatzes
(Wert 256 auf 70, 512 auf 2) mit *„only with a matching weapon type"*,
obwohl **kein** Waffentyp des Spiels diesen Wert trägt — der Spieler sucht
eine Waffe, die es nicht gibt. Auf diesem Spielstand ist der Fall **latent**
(0 von 197 bzw. 201 `not_counted`-Einträgen in beiden Umgebungen), weil keine
besessene Kopie einen solchen Effekt trägt; ein anderer Bestand kann ihn
sichtbar machen. Es ist eine A11-Frage („ich habe geraten"), kein
Rechenfehler. Der Text steht in `model.py`, die Entscheidung über den Text
nicht bei mir.

**OF-24 — an den `director`:** Der Befund aus T-084 nennt „46 von 170" als
Anteil an einer Zahl, die der Nutzer liest. Gemessen ist das der Anteil an
der **Kandidatenmenge**; die Zahl in der Statuszeile 4.9b bewegt sich in 175
von 176 vollen Läufen um **null** (Umgebung A: 1 von 565; B: 1 von 473).
Falls Priorität oder Reihenfolge eines Auftrags an der Grösse dieses
Befundes hing, ist die Grundlage jetzt eine andere — die Klasse ist trotzdem
zu entscheiden gewesen, weil der Docstring die **Beschreibung** der Menge
falsch führt und Füllung (c) im Picker jede der 46 Zeilen betrifft.

---

### Offene Fragen, neu

**OF-25 — an den `director`, auszufuehren vom `performance-tuner`:** Nach
AD-028 koennen zwei Spuren gleichzeitig rechnen (AK-08 verlangt es). **A6s
6-s-Zahl fuer `Optimize` ist gemessen, waehrend sonst nichts rechnete** —
`docs/perf/baselines.md` S11-A sagt nichts ueber eine gleichzeitige zweite
Spur, und unter dem GIL teilen sich zwei rechnende Python-Threads einen Kern.
Bei 5023,6 ms gemessen und 6 s Schranke bleiben 19 % Luft; eine Halbierung
des Durchsatzes waere mehr. **Zu messen:** `Optimize` mit einer gleichzeitig
laufenden Picker-Frage, gegen S11-A. Faellt die Zahl durch, ist es eine
Entscheidung fuer den `director` (Randbedingung an A6 oder Vorrang der
Picker-Spur), keine Nachbesserung.

**OF-26 — an den `director`, auszufuehren vom `performance-tuner`:** Der
**Hauptthread-Rest** einer Beraterfrage ist nie gemessen worden — auf keinem
der beiden Wege. Auch nach AD-028 bleiben im Hauptthread: der Bau der
Anfrage, `run.frozen_inventory` (309 Kopien plus die Angebotslisten je
Slot-Farbe) und `run.inventory_fingerprint` (sha256 ueber 309 sortierte
Zeilen). **A6s dritte Zeile steht und faellt mit dieser Zahl**, und sie gilt
schon heute fuer den `Optimize`-Weg, der als „haelt" gefuehrt wird. Zu messen
getrennt vom Lauf, im selben Szenario wie S11-B.

**OF-27 — an den `director`:** `UI_SPEC` §3.8, `ARCHITECTURE.md` (hier
korrigiert) und `relicpicker.py:276-281` tragen **dieselbe** gerechnete Zahl,
und keine der drei Stellen sagte, dass sie gerechnet war. Zwei davon sind
jetzt richtiggestellt, die dritte gehoert dem `ui-ux-designer` (U4). **Die
Frage dahinter ist allgemeiner:** ob eine Zahl, die in einem Entwurfstext
eine Entscheidung traegt, kuenftig ihre Herkunft mitfuehren muss — gemessen
oder gerechnet, mit Datum und Quelle. L-001 verlangt das fuer Testschranken
und Architekturkennwerte; QA-208 ist der Fall, in dem eine **gerechnete**
Zahl drei Dateien weit gewandert ist. Entscheidung des `director`, ob das als
Regel aufgeschrieben wird.

---

### Offene Fragen, neu

**OF-28 — an den `director`, auszufuehren vom `performance-tuner` (U7):** Die
Groesse eines Picker-Cache-Eintrags ist **in der Antwortform, die AD-028 der
Picker-Spur gibt, nie gemessen worden**; die 33,4 KiB, auf denen die 64 steht,
gelten fuer eine `AdvisorResult` mit 20 Suggestions. Schranke und Rueckweg
stehen in IX-3.2. **Solange diese Messung fehlt, ist die 64 eine gesetzte Zahl
ohne gueltige Herleitung** — sie steht, aber sie belegt nichts.

**OF-29 — an den `director`:** Nach IX-2 traegt die Picker-Anfrage in
`goal_id` eine Ordnungskonstante und nicht die Wahl des Spielers. Das ist die
zweite Stelle in diesem Vorhaben, an der ein Feldname mehr verspricht, als das
Feld haelt (die erste war `SlotPool.rank_by`, D-4/T-077). Die allgemeinere
Frage, die schon OF-27 stellt, wird damit dringender: **ob ein Feld, das nur
unter einer Randbedingung bedeutet, was sein Name sagt, diese Bedingung im Typ
tragen muss** statt im Docstring daneben. Entscheidung des `director`, ob das
als Regel aufgeschrieben wird; ein Umbau der Datenformen ist es nicht.

**Nummernkreise, die der `director` nachziehen muss** (`docs/state.md` gehoert
mir nicht): **AK ab AK-211** (bereits von T-124 gemeldet, Zeile 11 steht noch
auf AK-195) und **OF ab OF-30**. AD bleibt bei **AD-030** — dieser Nachtrag
vergibt **keine** neue AD-Nummer, er schreibt AD-028 fort.

---

### Offene Frage, neu

**OF-30 — an den `director`, Adressat `ui-ux-designer`:** AK-218 ist im
Wortlaut enger als der gebaute Zustand (siehe die Meldung oben); der
Cache-Treffer endet in keinem der drei Ausgaenge, sondern im Rueckgabewert,
was IX-1.3 entschieden und AK-211 vorausgesetzt hat. **Vorschlag steht dort;
`UI_SPEC.md` ist von mir nicht angefasst.** Solange der Wortlaut steht, misst
AK-218 den haeufigen Fall als Fehler.

**Nummernkreise, die der `director` nachziehen muss** (`docs/state.md` gehoert
mir nicht): **OF ab OF-31**. **AD bleibt bei AD-030** — dieser Nachtrag
vergibt keine AD-Nummer. Neu belegt sind ausserdem **W8** (Waechter der
Picker-Spur) sowie die Umsetzungsschritte **U9** und **U10**.

---

### Offene Fragen

**OF-31 — an den `director`, Adressat `security-reviewer`, vor V2.** A15
verschiebt die Vertrauensgrenze an **zwei** Stellen, und eine davon beruehrt
eine Nutzerentscheidung, die ich nicht aufmachen darf:

1. Der vom Nutzer gewaehlte Ordner wird nicht nur gelesen — `oodle.load()`
   laedt eine **native DLL** daraus in den Prozess (`nrdata/oodle.py:34-46`),
   und AK-112 nimmt den Ordner gerade deshalb an, weil sie darin liegt.
2. **SEC-016, SEC-017 und SEC-018 sind am 05.09.2026 mit der Begruendung
   gestrichen worden, sie setzten „eine boesartige Spielinstallation oder ein
   bereits uebernommenes Benutzerkonto voraus"**, samt „nicht erneut vorlegen".
   Diese Bedingung ist unter A15 keine Kontouebernahme mehr, sondern eine
   Ordnerauswahl. **Ich lege den Befund nicht erneut vor** — ich melde, dass
   die **Randbedingung** der Streichung fuer den geprueften Fall galt und fuer
   den neuen nicht geprueft ist. Ob daraus etwas folgt, entscheidet der Nutzer
   ueber den `director`.
3. Der Spielstand-Dialog macht ein **heruntergeladenes** Save in einem Klick
   erreichbar (Filter `All files (*)`, `UI_SPEC` §5). Die Abwehr aendert sich
   nicht — SEC-022, die zweite Dichtepruefung, die Deckel aus SEC-002 —, die
   Erreichbarkeit schon. **Zu pruefen:** ob die vorhandene Abwehr fuer einen
   Spielstand reicht, den der Nutzer bewusst von aussen holt.

**OF-32 — an den `director`, Adressat `performance-tuner`, nach V1.** Die
Gueltigkeitspruefung des gemerkten Pfades laeuft **vor** dem ersten Fenster.
Auf einem toten UNC-Ziel kann ein `stat` zweistellige Sekunden kosten. **Zu
messen** ist das nicht auf diesem Rechner ohne Freigabe; **zu entscheiden** ist,
ob die Frist gebaut wird, bevor jemand sie gemessen hat. Meine Empfehlung: erst
messen — der Fall setzt voraus, dass der Nutzer sein Spiel auf einer Freigabe
hat, und Architektur auf Vorrat ist teurer als ein Nachtrag.

**Meldung an den `ui-ux-designer`, keine Frage:** Ich habe AK-106 bis AK-132
und AK-220 bis AK-229 gegen diesen Entwurf gelesen. **Kein Widerspruch
gefunden.** Was AD-030 hinzufuegt und die Spec nicht sagt: (a) der **eine**
Aufloesungspunkt, den auch `datasource.py` benutzt; (b) die Invariante, dass
die zwei Schluessel **nie geloescht**, nur ueberschrieben werden (strenger als
AK-121, nicht anders); (c) `type=str` beim Lesen; (d) dass **dasselbe**
Praedikat Annahme (AK-112) und spaetere Gueltigkeit (AK-107) entscheidet.
Nichts davon ist sichtbar, alles davon ist pruefbar.

**Nummernkreise, die der `director` nachziehen muss** (`docs/state.md` gehoert
mir nicht): **AD ab AD-032** · **OF ab OF-33**. Neu belegt sind ausserdem die
Umsetzungsschritte **V1 bis V5** (V5 ist U8 unter neuem Namen; der `U`-Kreis
wird nicht fortgesetzt) und die Regressionsfaelle **R1 bis R18**.
---

## Erledigtes und Randnotizen

*Zwei Abschnitte, die zu keinem Themenbereich gehoeren und die niemand mehr
sucht — sie stehen hier, damit sie nicht verloren gehen.*

### Wichtige Korrektur zur Auftragslage (erledigt)

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

### Folgen für `UI_SPEC.md` — an den `ui-ux-designer`

Nicht meine Entscheidung, aber es hängt daran: **AK-13, AK-14 und AK-16
brauchen eine Fassung für den Haltezustand.** „`Apply all` belegt alle Slots"
und „`Suggest` verändert keinen Slot" sind unter Festhalten nicht mehr
vollständig — ein festgehaltener Slot darf von `Apply all` nicht angefasst
werden, und der Inhalt eines festgehaltenen Slots ist eine **Eingabe** der
Rechnung, kein Vorschlag (AK-16 bleibt für Vorschläge gültig, ein
festgehaltenes Custom relic ist zulässig). Ausserdem: die Picker-Frage aus
`GOAL.md` F4 ist algorithmisch derselbe Lauf mit `h = Slotzahl − 1`
(AD-014) — sie kostet keine Architektur und darf frei angeordnet werden.

---

## Verlauf

Der vollstaendige chronologische Verlauf dieser Datei — alle elf Nachtraege in
ihrer urspruenglichen Reihenfolge, mit Inhaltsverzeichnis — steht in
**`docs/archiv/architecture-verlauf.md`**.

Dort steht nach, wer eine Entscheidung wann und gegen welche Alternative
getroffen hat. **Bevor eine Entscheidung revidiert wird, gehoert der Verlauf
gelesen:** die verworfene Alternative ist meistens schon einmal geprueft
worden, und der Grund, aus dem sie verworfen wurde, ist der teuerste Teil
dieser Datei.
