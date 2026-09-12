STATUS: erledigt
AUFTRAG: T-073 - `Comes with curse` erklaeren (QA-169)
GELESEN: docs/tasks/T-073.md · GOAL.md (A11 woertlich aus dem Auftrag zitiert; A12 **nicht** zitiert, deshalb selbst nachgelesen, §"A12 — Jede Zahl und jede Beschriftung...") · docs/state.md (Stand-Auszug im Auftrag zitiert, Zeile gegengelesen) · UI_SPEC.md (auf Widerspruch zu `Comes with curse`/`always cursed` geprueft, vor und nach dem waehrend meiner Sitzung dazugekommenen T-074-Anhang) · qa/findings.md (QA-159, QA-160, QA-162) · nrplanner/effectstab.py · tests/test_effects_tab_display.py · tests/tabtext.py · tests/conftest.py (game_data/qapp) · nrdata/extract.py (curse/is_curse/curse_share-Herkunft) · scripts/differential/mutate.py
GEÄNDERT: nrplanner/effectstab.py · tests/test_effects_tab_display.py · scripts/differential/mutate.py (alle drei committet in 7f77e04). Zusaetzlich zwei Wegwerf-Testdateien angelegt und wieder geloescht, nie committet: tests/test_zzz_scratch_curse_check.py, tests/test_zzz_scratch_missing_columns.py (reine Erhebungsskripte fuer die Zahlen unten, siehe "Nicht in den Auftrag gehoerig").
ANNAHMEN:
1. A12 war im Auftrag nicht zitiert (nur A11) — ich habe GOAL.md selbst gelesen und A12 woertlich angewendet.
2. "sofern das zutrifft" (A12-Klausel zur Filterunabhaengigkeit) habe ich empirisch geprueft statt zu unterstellen — sie trifft **nicht** uneingeschraenkt zu (Befund unten). Der sichtbare Satz behauptet deshalb keine Filterunabhaengigkeit; das ist eine bewusste Abweichung von der woertlichen Auftragsvorlage, gedeckt durch deren eigene Ausweichklausel "Trifft es nicht zu, sag im Bericht, was stattdessen gilt."
3. Fuer die zweite Stichprobe (Absatz ohne `missing`/Duplikat-Notiz/Fluecke) habe ich "Physical Attack Up +3" gewaehlt — durch Scan des Datensatzes gefunden, nicht vorgegeben. Dokumentiert im Test mit dem gleichen "faellt laut auf, wenn der Datensatz sich aendert"-Muster wie die vorhandene `DIVERGENT`-Konstante.
4. Platzierung: Konstante direkt nach `COPIES_DEFINITION` (gleiche "eine Definition von X"-Gruppe); Tests direkt nach dem AK-81-Copies-Test und vor den QA-156b-Filtercaption-Tests (thematische Nachbarschaft zu den Copies-Tests, nicht Anhaengsel ans Dateiende).
NÄCHSTER: director
BLOCKIERT DURCH: nichts

---

## Ungewoehnlicher Fund zuerst: der Auftrag sagte "niemand laeuft parallel" — das stimmte nicht durchgehend

Bevor der Rest: `git log` zeigt, dass zwischen meinem Startpunkt (`7d0b2b9`,
so vom Auftrag benannt) und meinem eigenen Commit vier fremde Commits auf
genau diesem Branch (`docs/audit-and-advisor-design`) gelandet sind —
`677a0c3` (director, A15/GOAL.md), `f330824` (director, T-074-Auftrag),
`f9c0aa5` (ui-ux-designer, UI_SPEC.md + eigener Bericht), `389c2d7`
(qa-engineer, QA-171 in qa/findings.md). Alle vier waehrend meiner Sitzung,
vermutlich waehrend einer meiner beiden ca. 7-minuetigen vollen Testlaeufe.

Ich habe das geprueft, nicht nur festgestellt: keiner der vier Commits
beruehrt eine Datei, die ich gelesen, zitiert oder geaendert habe
(`git diff 7d0b2b9 HEAD -- GOAL.md docs/state.md` zeigt bei GOAL.md nur den
rein anhaengenden A15-Abschnitt nach Zeile 197, A11/A12 unveraendert;
docs/state.md ganz ohne Diff). Der UI_SPEC.md-Zusatz (614 Zeilen) sitzt am
Dateiende: die zwei einzigen Stellen, die "Comes with curse" nennen
(Zeile 1852, 2518), stehen unter derselben Zeilennummer wie vor dem Zusatz.
Mein eigener Commit (`git show 7f77e04 --stat`) enthaelt exakt und nur meine
drei Dateien. Kein Datenverlust, keine Vermischung — aber die Praemisse des
Auftrags war fuer einen Teil meiner Sitzung falsch, und haette es sich nicht
zufaellig um disjunkte Dateien gehandelt, waere das ohne eigenen Klon riskant
gewesen. Das gehoert dem `director` zur Kenntnis, nicht mir zur Loesung.

## Umgesetzt

**Eine Konstante, zwei Verwendungen — dem Muster von `COPIES_DEFINITION`
folgend.**

`nrplanner/effectstab.py`:
- Neue Konstante `CURSE_DEFINITION` (nach `COPIES_DEFINITION`, vor
  `UNREACHABLE_TIP`): erklaert, dass Rollen des Effekts einen Fluch mitziehen
  kann, den Unterschied `sometimes` (manche Relikte mit dem Effekt tragen
  auch einen Fluch, die Wahl liegt beim Spieler) gegen `always cursed`
  (ausnahmslos alle), in Spielersprache.
- `HEADER_TIPS[COL_CURSE]` zeigt jetzt auf `CURSE_DEFINITION` statt auf den
  bisherigen eigenen Satz (der Kopf-Tooltip, Zeile ~150).
- Der Absatz-Text in `refresh()` haengt `{CURSE_DEFINITION}` unbedingt hinter
  `{COPIES_DEFINITION}` an (Zeile ~945) — unbedingt wie `CHANCE_DEFINITION`
  und `COPIES_DEFINITION`, nicht hinter einer der drei bedingten Klauseln
  (`note`, `missing`, Fluchzahl).

`tests/test_effects_tab_display.py`: vier neue Tests plus eigene, **nicht
importierte** Kopie von `CURSE_DEFINITION` (L-008) im neuen Abschnitt
"QA-169: the one column the paragraph left out", direkt nach dem
AK-81-Copies-Test:
- `test_curse_is_explained_where_the_reader_is_already_looking` — Spaltenname
  im sichtbaren (nicht Tooltip-)Text, analog QA-156a.
- `test_the_curse_sentence_is_in_the_paragraph` — Rot-vorher 1/2.
- `test_the_curse_sentence_is_in_the_header_tooltip` — Rot-vorher 2/2.
- `test_the_curse_sentence_survives_a_paragraph_with_nothing_else_extra` —
  zweite Stichprobe als Test, nicht nur als manuelle Pruefung.

`scripts/differential/mutate.py`: Anker der Mutation
`copies-explained-only-on-the-header` an die neue Quellzeile angepasst (siehe
"Wieso mutate.py" unten) — **notwendige Folge** meiner Aenderung, kein
eigenstaendiger Auftrag.

**Bewusst nicht behauptet:** dass der Fluch-Befund unabhaengig von den oben
gesetzten Filtern ist. Der Auftrag verlangte diese Aussage nur, "sofern das
zutrifft" — sie trifft nicht durchgehend zu (Befund unten), also steht sie
nicht im sichtbaren Satz. Der Code-Kommentar ueber der Konstante dokumentiert
das ausfuehrlich fuer den naechsten Entwickler.

## Abnahmezahlen — beide Stichproben, gegen den Commit `7f77e04`

**Stichprobe 1 — Standardfilter, Tabelle voll (652 Zeilen, die Ansicht, in
der QA-169 entstand):**
```
577 buffs (blue) then 75 curses (red). 17 identical duplicates merged. For 50
the game gives nothing beyond the name. Chance is per relic effect slot, ...
... 'Copies' is how many separate entries ... 'Stacking' what a second one
does. 'Comes with curse' says whether rolling this effect can also bring you
a curse. 'Sometimes' means only some of the relics that carry the effect
also carry a curse, so which one you take decides it. 'Always cursed' means
every one of them does, so the effect never comes without one.
```
Kopf-Tooltip der Spalte (`Comes with curse`-Spalte, `toolTip()`):
`Comes with curse\n<derselbe Satz wortgleich>`.

**Stichprobe 2 — Filterstellung ohne die uebrigen Bausteine:** Suchfeld auf
`Physical Attack Up +3` (isoliert genau eine Zeile; Copies=1, kein Fluch,
eigene Beschreibung — kein `missing`-Teil, keine Duplikat-Notiz, null
Fluecke):
```
1 buffs (blue) then 0 curses (red). Chance is per relic effect slot, ...
'Comes with curse' says whether rolling this effect can also bring you a
curse. 'Sometimes' means ... 'Always cursed' means every one of them does,
so the effect never comes without one.
```
Der neue Satz steht in beiden Ansichten, wortgleich. Beide Auszuege stammen
aus einem echten `EffectsTab` (offscreen-QApplication, wie die Suite selbst
liest — `tab.summary.text()` / `horizontalHeaderItem(...).toolTip()`, nicht
aus dem Quelltext zitiert).

## Rot-vorher, je Verwendungsstelle einzeln (L-008)

Beide Wege einzeln deaktiviert, Suite auf `tests/test_effects_tab_display.py`
gelaufen, dann zurueckgesetzt:

**Absatz-Pfad entfernt** (`{COPIES_DEFINITION} {CURSE_DEFINITION}` ->
`{COPIES_DEFINITION}`):
```
FAILED test_curse_is_explained_where_the_reader_is_already_looking
FAILED test_the_curse_sentence_is_in_the_paragraph
FAILED test_the_curse_sentence_survives_a_paragraph_with_nothing_else_extra
3 failed, 1 passed
```
(der eine verbleibende Pass ist `test_the_curse_sentence_is_in_the_header_tooltip`.)

**Tooltip-Pfad entfernt** (`COL_CURSE: CURSE_DEFINITION` -> der alte, fest
codierte Satz):
```
FAILED test_the_curse_sentence_is_in_the_header_tooltip
1 failed, 3 passed
```
Jeder der beiden Wege bricht **genau** seinen eigenen Test, keinen der
anderen drei — die vier Tests sind wie beabsichtigt unabhaengig voneinander
scharf. Die Erwartung (`CURSE_DEFINITION` in der Testdatei) ist eine eigene,
nicht importierte Kopie; ein Test, der stattdessen `effectstab.CURSE_DEFINITION`
importiert haette, waere bei beiden Experimenten gruen geblieben, weil er
sich nur gegen sich selbst geprueft haette.

**Mutation `copies-explained-only-on-the-header` neu belegt:** mein Edit
strandete ihren Anker (`f"one name. {COPIES_DEFINITION}"` kam nicht mehr
exakt einmal im Quelltext vor, seit die Zeile jetzt `{CURSE_DEFINITION}`
mittraegt — `test_every_mutation_still_finds_its_anchor_in_the_real_source`
schlug deshalb rot an, bevor ich es reparierte). Anker aktualisiert auf
`f"one name. {COPIES_DEFINITION} {CURSE_DEFINITION}"` ->
`f"one name. {CURSE_DEFINITION}"` (entfernt weiterhin nur `COPIES_DEFINITION`,
laesst `CURSE_DEFINITION` stehen). Manuell angewandt und gegen die Suite
gelaufen, um `survival_means` nicht ungeprueft zu lassen:
```
FAILED test_copies_is_explained_where_the_reader_is_already_looking
FAILED test_the_explanation_of_copies_keeps_it_apart_from_the_two_it_is_not
FAILED test_the_header_and_the_sentence_say_one_thing_about_copies
3 failed, 14 passed
```
Genau die drei in `survival_means` benannten Faelle, alle vier neuen
Curse-Tests unberuehrt. Danach zurueckgesetzt.

## Eigenschaft statt Fundstelle — QA-159, Trefferzahl, nicht behoben

Auftrag: mit zwei unabhaengigen Suchmasken pruefen, ob weitere Spalten im
Absatz fehlen. Gegen `tab.summary.text()` (den Absatz selbst, **nicht**
`tabtext.labels(tab)` — das zaehlt auch die vier Filterlabels "Colour" /
"Relics" / "Stacking" / "Type" mit, was "Type" und "Stacking" als
Falsch-Treffer meldet, obwohl sie dort nur als Box-Beschriftung stehen, nicht
als Spaltenerklaerung; gegen QA-159 selbst gegengeprueft, um das zu merken).

Maske A: Teilstring `Spaltenname in Absatztext`. Maske B: Wortgrenzen-Regex
`(?<![A-Za-z])Name(?![A-Za-z])`. Beide liefern identische Ergebnisse.

- **Vorher** (Stand vor diesem Auftrag): 7 von 11 fehlen — `Effect`, `Type`,
  `Colours`, `Avg chance`, `Best chance`, `Comes with curse`, `What it does`.
- **Nachher** (gegen `7f77e04`): 6 von 11 — dieselbe Liste ohne
  `Comes with curse`.

**Abweichung von QA-159 offengelegt, nicht aufgeloest:** QA-159 zaehlt
`Relic slots` und `Stacking` zu "nur im Tooltip erklaert". Meine Suchmasken
finden beide Namen im Absatz — sie stehen in `COPIES_DEFINITION`s
Abgrenzungssatz ("'Relic slots' says how many slots can roll it, 'Stacking'
what a second one does"). Eine blosse **Namensnennung zur Abgrenzung** ist
etwas anderes als eine **eigene Erklaerung** der Spalte, und das ist eine
Wertung, die eine Textsuche nicht treffen kann. Ich melde die Zahl aus der
vorgegebenen Methode (Suchmasken), nicht eine Neubewertung von QA-159 — das
bleibt Sache des `ui-ux-designer`. **Nicht behoben**, wie verlangt.

## Neuer Befund fuer den director (nicht behoben, nicht Teil des Auftrags)

**Titel:** `Comes with curse` folgt bei einigen Effekten der Filteransicht
statt dem Effekt selbst — AK-81 wurde nie auf diese Spalte angewendet.

**Fundstelle:** `nrplanner/effectstab.py`, `EffectsTab.refresh()`. Die
`merged`-Zusammenfuehrung haelt fuer jede `identity()`-Gruppe nur den zuerst
gefundenen Roh-Eintrag (`prev_eff`) fest und uebernimmt dessen `colours`
gemerged, aber **nicht** dessen `curse`/`is_curse` — die Anzeigezeile
(`"is a curse" if eff.get("is_curse") else CURSE_LABEL.get(eff.get("curse", "never"), "")`)
liest das direkt von diesem einen Roh-Eintrag.

**Wie ich es gefunden habe:** beim Pruefen der A12-Klausel ("haengt am
Effekt, nicht an den Filtern"). `effectstab.identity()` gruppiert nach Name +
`sp_effect_ids` + `modifiers`; `curse`/`is_curse` werden in
`nrdata/extract.py` aber pro **Roh-Eintrag** (`effect_id`) gesetzt, nicht pro
Identitaetsgruppe. Zwei Roh-Eintraege koennen also dieselbe Identitaet und
trotzdem unterschiedliche Fluch-Werte tragen — genau die Faellklasse, die
`self._rung`/`self._copies` (Kommentar direkt in `EffectsTab.__init__`) fuer
`Tier`/`Copies` schon einmal beheben musste (QA-127/AK-81), hier aber nie
angefasst wurde.

**Zahl und Beleg (gegen den Snapshot in `%LOCALAPPDATA%\NightreignHelper`,
2076 Roh-Effekte, 1064 Identitaeten, gemessen am 06.09.2026):** 12 von 1064
Identitaeten haben zwei Roh-Eintraege mit gleichem `identity()`, aber
unterschiedlichem `curse`-Feld (`sometimes` gegen `never`, nie `always`
beteiligt). Bei 10 davon ist das in der Tabelle tatsaechlich sichtbar
instabil: mit den Standardfiltern (`All colours`, `Rollable on relics only`
angehakt) zeigen alle zehn `sometimes`; hakt man **nur** "Rollable on relics
only" ab (bei weiterhin `All colours`), zeigen dieselben zehn Zeilen — selber
Name, selbe Tier-Zelle, selbe Beschreibung — stattdessen eine leere Zelle.
Bei den restlichen 2 (`Physical Attack Up +2`, `Small Pouch in possession at
start of expedition`) bleibt es zufaellig stabil, weil ihr `never`-Eintrag
eine nicht-leere Farbliste traegt und in der Datenreihenfolge nie zuerst
steht — kein Beleg fuer Robustheit, nur Zufall der Reihenfolge. Reproduktion
(Kurzfassung, ohne die geloeschten Wegwerfdateien):
```python
import collections, json
from nrplanner import effectstab, paths
data = json.loads(paths.snapshot_path().read_text(encoding="utf-8"))
by_identity = collections.defaultdict(list)
for eff in data["effects"].values():
    by_identity[effectstab.identity(eff)].append(eff)
disagreeing = [k for k, v in by_identity.items() if len(v) > 1
               and len({m.get("curse", "never") for m in v}) > 1]
print(len(disagreeing))  # -> 12
```
Die UI-Instabilitaet habe ich zusaetzlich am echten `EffectsTab` durch
Durchschalten aller Kombinationen aus Farb-, Modus-, Stacking- und
Typ-Filter sowie der Checkbox bestaetigt (10 von 12 Namen zeigen sowohl
`sometimes` als auch `""` je nach Kombination).

**Risiko:** sichtbarer Widerspruch fuer einen Spieler, der genau die
Checkbox anfasst, die mehr zeigen soll ("Rollable on relics only" abhaken),
und dafuer bei zehn Effekten eine **andere** Aussage zur selben Zeile
bekommt. Kein Datenverlust, keine Sicherheitsfrage.

**Aufwand-Einschaetzung:** klein bis mittel. Das Muster liegt vor
(`self._rung` / `self._copies` in `__init__`, ausserhalb der gefilterten
`candidates`-Schleife berechnet). Fehlt: eine Entscheidung, wie zwei
widerspruechliche Rohwerte einer Identitaet zusammengefasst werden (z. B.
"schlechtester Fall gewinnt": `always` > `sometimes` > `never`) — das ist
eine Bewertungsfrage und keine, die ich in diesem Auftrag beilaeufig
entscheiden sollte.

**Empfehlung:** eigener `developer`-Auftrag, analog zu AK-81/QA-127. Keine
`ui-ux-designer`-Frage — es geht um Datenkorrektheit, nicht um Wortlaut.

## Tests

**Neu:** vier Tests in `tests/test_effects_tab_display.py` (siehe oben).
**Bewusst nicht:** kein neuer Mutationseintrag fuer die beiden neuen
Verwendungsstellen von `CURSE_DEFINITION` (das waere ueber "ein Satz, ein
Test" hinausgegangen; P7/die Mutationskampagne ist ein eigener, vom Nutzer
als "bleibt vollstaendig" gefuehrter Bestand — Entscheidung, ob das
nachgezogen wird, liegt beim director). Kein Test fuer den neu gefundenen
Merge-Fehler oben — waere Test fuer nicht behobenen Code, also nur ein
weiterer roter/uebersprungener Fall ohne Nutzen; die Reproduktion oben
gehoert stattdessen ins Backlog des Fixes.

## Testergebnis

Vorher (Auftrag nennt): `.venv\Scripts\python.exe -m pytest -q -m "not slow"`
-> 860 passed, 9 skipped, 5 deselected.

Nachher, dieser Lauf (Commit `7f77e04`, Arbeitsbaum, da laut Auftrag kein
paralleler Klon noetig):
```
864 passed, 9 skipped, 5 deselected in 432.03s (0:07:12)
```
+4 durch meine neuen Tests, sonst unveraendert. Zwischenzeitlich einmal
`863 passed, 1 failed` (die gestrandete Mutations-Anker-Pruefung, siehe
Rot-vorher-Abschnitt) — behoben, nicht als Endzustand liegen gelassen.

## Commit

`7f77e04` `fix(effects-tab): explain \`Comes with curse\` in the paragraph, not just the tooltip`
— genau die drei genannten Dateien, 142 Einfuegungen, 5 Loeschungen.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Build & Tests gruen unter Windows/.venv (siehe oben)
- [x] Neue Tests fuer neue Logik, Rot-vorher je Verwendungsstelle einzeln
      belegt (L-008). Linter: keiner konfiguriert (Nutzerentscheid
      06.09.2026, "Option B: kein Linter", `docs/plan-restarbeiten.md`) —
      entfaellt.
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Abnahmekriterien selbst durchgespielt (beide Stichproben, textuell
      gegen den echten Widget-Zustand, wie die Suite selbst liest)
- [ ] **Ungeprueft:** Sichtpruefung am laufenden Fenster
      (`.venv\Scripts\python.exe run.py`). Kein Werkzeug hier kann ein
      Fenster-only-Bildnachweis erzeugen (NH-002 verbietet Bildschirmabzuege,
      auch zugeschnittene; das verfuegbare `computer-use` liefert nur
      Vollbild). Die programmatische Pruefung (echtes Offscreen-Widget,
      `tab.summary.text()` / `toolTip()`) ist inhaltlich gleichwertig zu dem,
      was die Projekt-Testsuite selbst als Nachweis akzeptiert, ersetzt aber
      keine visuelle Pruefung auf Umbruch/Abschneiden bei den beiden neuen
      Saetzen. Da `self.summary.setWordWrap(True)` gesetzt ist, sollte die
      Fensterbreite unberuehrt bleiben; die Fensterhoehe bei sehr schmalem
      Fenster habe ich nicht mit blossem Auge gegengeprueft.
- [x] Doku: dieser Bericht unter docs/berichte/T-073-developer.md.

## Nicht in den Auftrag gehoerig, aber aufgefallen

- Die eingangs beschriebene Nicht-Isolation (vier fremde Commits waehrend
  meiner Sitzung trotz "niemand laeuft parallel").
- Der neue Merge-Befund oben (Comes with curse folgt der Filteransicht bei
  10 von 1064 Effekten).
- Fuer die beiden Abnahmezahlen habe ich zwei Wegwerf-Testdateien in
  `tests/` angelegt (`test_zzz_scratch_curse_check.py`,
  `test_zzz_scratch_missing_columns.py`), ausschliesslich zur Erhebung,
  vor dem Commit wieder geloescht — nie Teil des Git-Standes.

## An qa-engineer

Zu pruefen: beide Stichproben oben am laufenden Fenster (Standardfilter;
Suche nach "Physical Attack Up +3"); dass `Comes with curse` jetzt ohne
Hover lesbar ist; optional den sechsten `power-user`-Lauf fuer A11, wie
docs/state.md es fuer nach QA-169 vorsieht (nicht meine Rolle, nur Hinweis).
Edge Case fuer den `power-user`: der neue Satz ist bewusst lang (drei Saetze)
— falls das im Lesefluss stoert, ist das eine Kuerzungsfrage an
`ui-ux-designer`, kein Fehler in der Bedeutung.

## An ui-ux-designer

Keine Abweichung von UI_SPEC.md gefunden (geprueft vor und nach dem
T-074-Zusatz). QA-159 bleibt wie sie ist — nur die Trefferzahl oben ist neu
(6 statt 7 von 11), keine Empfehlung von mir zur Loesung. Die
Abweichung meiner Suchmasken von QA-159s eigener Zaehlung (`Relic slots`/
`Stacking` als "im Absatz genannt" statt "nur Tooltip") ist eine
Definitionsfrage, die ich nicht entscheide.

## An director

- Der Prozess-Befund oben (parallele Commits trotz gegenteiliger
  Auftragsangabe) — bitte zur Kenntnis, keine Handlung von mir aus noetig,
  da ohne Ueberschneidung.
- Der neue Merge-Befund oben (Comes with curse, 10 von 1064 Effekten) —
  Titel und Fundstelle wie oben, ohne Nummer, Vergabe liegt bei dir.
- QA-159-Trefferzahl aktualisiert: 6 statt 7 von 11 (siehe oben), weiterhin
  offen und bei `ui-ux-designer`.
