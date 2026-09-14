# T-251a -- Pruefphase A18/A19 auf `528ff78` (qa-engineer)

Datum 14.09.2026 22:58-00:10, HEAD `70c135b`, Code `528ff78` (eingefroren).
Geaendert in diesem Auftrag: dieser Bericht, `qa/findings.md` (nur
angehaengt), `scripts/differential/mutate.py` (sechs bestaetigt tote
Mutationen geloescht, OF-35/AD-033; die Literale liegen in `528ff78`).
Kein Commit.

**Umgebung:** `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-251qa` (Registry
`HKCU\Software\DankYeeterT-251qa\NightreignHelper`, am Ende geleert),
`LOCALAPPDATA`/`APPDATA`/`USERPROFILE` ins Scratchpad, Testabzug (841
Dateien, `EXTRACT_VERSION` 11) hineinkopiert. Spielstand **eingefroren**
als Kopie: `savenow` = `NR0000.sl2` vom 14.09. 23:01:42 (SHA-256
`d7c5aefe…`, 319 Kopien) und `save1943` = Kopie aus T-244 (19:43, SHA-256
`b52d110e…`, 315 Kopien); `USERPROFILE` umgelenkt, damit der
`Path.home()`-Fallback den lebenden Spielstand nicht mitliest. Rechnungen
Qt-frei auf `tests/data/frozen_inventory.json` (314 Kopien). Fensterlauf
unter `QT_QPA_PLATFORM=windows` (Fusion, Segoe UI 9 pt, DPR 1,25,
`WA_DontShowOnScreen`), Bilder per `widget.grab()` aus dem Programmfenster
in `<scratchpad>/T-251/shots/` (kein Bildschirmabzug).

## Suite

Zielgerichtet vorab (10 Berater-Dateien, seriell): 441 passed, 1 failed
(`test_the_row_does_not_scroll_away_with_the_slots`, QA-266). Volllauf
`-n auto` mit eingefrorenem Spielstand 23:01: 1592/10/3 (Nachtrag am Ende).

## QA-266 aufgeklaert: der Spielstand, nicht Umgebung und nicht Code

Die drei Tests lesen den **lebenden Spielstand** des Nutzers (`planner`-
Fixture, `two_copies_of_one_roll`, `_scan_save` waehlt die Datei mit den
meisten Kopien; `Path.home()/AppData/Roaming` immer dabei). Zwischen 19:43
und ~21:30 hat der Nutzer im Spiel das ausgeruestete Gefaess gewechselt:
Wylder `selected` 1001 (2 Relikte) -> **1003 Soot-Covered Wylder's Urn,
leer** (ebenso Guardian 2002->2001 leer, Duchess 4002->4001 leer; 315->319
Kopien). Nachweis ohne Bisect, weil derselbe Code beides zeigt:

| Code | `save1943` (19:43) | `savenow` (23:01) |
|---|---|---|
| `47abd1e` (21:08 gruen) | 3 passed | 3 failed |
| `528ff78` | 3 passed | 3 failed |

Mechanik je Test (23:29 allein gefahren, kein fremder Prozess):
1. `test_relic_restore::…no_other_slot_was_given`: die Fixture waehlt
   Gefaess 1003 (Zeile 4); das Fenster startet jetzt **schon auf Zeile 4**
   (im Spiel ausgeruestet), `setCurrentRow(4)` ist kein Wechsel, der
   Restore laeuft nicht -> `worn == [None, None]`. Mit 19:43 startet es auf
   Zeile 2.
2. `test_advisor_bar::…does_not_scroll_away`: Startgefaess leer -> kurze
   Slotkarten -> bei 1320x560 nichts zu scrollen (`maximum() == 0`).
3. `test_save_read_in_the_background::…neither_the_window_nor_the_focus`:
   die Bestandsnotiz ist jetzt die lange Variante `The equipped Soot-Covered
   Wylder's Urn is empty in game; the others are in the list on the left.`
   -- offscreen (Fallback-Schrift ~12 px/Zeichen) 3 Zeilen = 34 px gegen
   28 px Wartezeile. **Live unter Windows:** 32 px = 2-Zeilen-Boden
   (`owned_label.minimumHeight()` 32), AK-225 haelt auf der Zielplattform.

Damit: QA-266 ist Testisolation (drei Tests haengen am Spielstand des
Rechners), kein Produktfehler, keine Umgebung; Adressat `developer`. Der
Fehlerfall bleibt reproduzierbar, solange der Nutzer mit leerem Gefaess
spielt.

## A18 -- Ausschluss (Qt-frei, frozen_inventory 314, Wylder's Chalice 0/2/4, Grundlinie 420 Ids)

Je Richtung den ersten Effekt mit Zahl im Top-Vorschlag ausgeschlossen
(`max_damage` 7080800, `min_damage_taken` 7012200, `max_attributes`
7000302 `Strength +3`); `model.compute` mitgeschrieben:
- ausgeschlossene Id erreicht **keine** Rechnung (0 von 3 Richtungen);
  keine Zeile ueber sie ausser AK-290.1 (`…: you excluded it, so it is not
  counted.`); leere Ausschlussmenge = Grundlinien-Rangfolge (3/3).
- Relikt bleibt waehlbar: `min_damage_taken` 40/40 Vorschlaege waehlen
  weiter einen Traeger (10 passende Kopien), `max_attributes` 5/40 (19
  Kopien), `max_damage` 0/40 (2 Kopien, fallen aus den Top 40).
- **OF-37/Nachweis:** Rangfolge ohne Markierung gegen `dde2efc` (Klon,
  `reading_defaults(False)` = Best case, 413 Ids) fuer 9 Fragen (3 Gefaesse
  x 3 Richtungen, je Top 40, Handles + Score): **9/9 identisch**, auch mit
  den 7 bedingten Fluechten (420). Why-Zeilen wortgleich; in 3 Fragen
  vertauschen zwei Zeilen desselben Effekts ihre Reihenfolge (`Strength -7`
  / `Dexterity -5, counted against it`), Inhalt gleich.

## A19 -- Pflicht

- Effekt in 34/40 bzw. 8/40 bzw. 28/40 freien Vorschlaegen verlangt: alle
  40 Pflicht-Vorschlaege tragen ihn (3/3 Richtungen); die gemeinsamen
  Konstellationen behalten Reihenfolge und Score der freien Suche
  (`max_damage` Praefix 34/34 exakt, `max_attributes` 28/28,
  `min_damage_taken` ab Index 7 eine Konstellation, die der freie Beam mit
  Breite 40 nicht erreichte -- Naeherung, kein Umgewichten).
- Effekt ohne Traeger (10002): 0 Vorschlaege, `unknowns` =
  `No copy you own carries Switching Weapons Boosts Attack Power, which you
  marked as required — no suggestion can meet that.` (AK-281 woertlich,
  im Why-Footer sichtbar).
- AK-291: ein roter Slot, zwei Pflicht-Effekte auf verschiedenen Kopien ->
  `No combination of the copies you own carries Improved Critical Hits +1,
  [Scholar] Continuous damage …` **alphabetisch**, woertlich.
- `SlotProblem` mit einer Id in beiden Mengen: `ValueError` (AD-036.1).
- **A6 mit Pflicht:** Median aus 3 kalten Laeufen, 5900X, Qt-frei:
  `max_damage` 377 -> 415 ms (+10 %), `min_damage_taken` 401 -> 498 ms
  (+24 %), `max_attributes` 362 -> 348 ms (-4 %). Zielgeraet nicht messbar.

## Fenster (offscreen zwei Prozesse; live Windows)

- **Persistenz ueber echten Neustart (AK-283):** Prozess A markiert im Why
  (`Strength +3` Don't include) und auf der Karte (`[Wylder] Art activation
  spreads fire in area` Must include, zwei Klicks), schliesst; Registry
  `advisor/excluded=7000302`, `advisor/required=7010500`. Prozess B liest
  `([7000302], [7010500])`, Karten zeigen `excluded`/`required ▲`, Optimize
  danach: 0 Zahl-Zeilen fuer E, 40/40 tragen R, Why-Listen `Effects you've
  excluded:` / `Effects you require:` gefuellt. Statblatt-`declared` leer
  (AK-282).
- **Drei Zustaende, Id-Bindung (AK-276/277):** zwei Why-Zeilen desselben
  Effekts und die Kartenzeilen wechseln mit einem Klick gemeinsam; Zyklus
  neutral -> `•` durchgestrichen BAD -> `▲` fett ACCENT -> neutral; drei
  Tooltips woertlich AK-277; Zeilenhoehe im Why 16 px in allen Zustaenden;
  Karte 208 px breit. Legende AK-290.3 woertlich, nur bei Markierung.
- **Zaehler-Tooltip (AK-280):** `Nothing suggested yet.  ·  1 effect
  excluded  ·  1 effect required` in 4.1 (nach Neustart), 4.6, 4.7, 4.11.
- **AK-289 live:** Optimize, nach 266 ms `WORKING_QUIETLY`, Markierung ->
  Statuszeile `The effects you marked changed while this was working out —
  use Optimize again.`, Antwort weg. 4.7-Satz fuer Deep-Wechsel
  unveraendert. Markierung im Ruhezustand: Antwort weg, `Why` weg (AK-183).
- **AK-285 live:** Zeilenminimum ohne Aktionen **338**, mit **596**,
  `_opening_width()` **1608** -- wie gemeldet. Zeilenhoehe 36.
- **AK-278:** 3 Tab-Stopps auf einer 3-Zeilen-Karte; Leertaste schaltet,
  **Enter nicht** (deckt sich mit DR-025 des ui-ux-designers).
- A8: alle neuen Saetze englisch; Namen laufen als Plain-Text-Label
  (`_plain`), Tooltip der Zeile ueber `html.escape`.

## Mutationen (OF-35)

Sechs Eintraege, je im `git archive 528ff78`-Klon angewandt, nur die
benannten Killer gefahren: `exclusive-group-counts-every-copy` 1 failed;
`baseline-dropped-from-the-ask` 1 failed
(`…leaves_no_switchable_condition_uncounted`); `exclusion-ignored` 1
failed; `feasibility-cut-removed` 3 failed; `markings-dropped-from-the-ask`
2 failed (beide benannten); `marked-line-deaf-to-the-filters` 3 failed.
Alle geloescht, `MUTATIONS = {}`; Waechter ueber das Register gruen (330
passed, 1 skipped).

## Befunde

### [P2 | Critical | Niedrig] Eine Id in beiden Speicherschluesseln legt Berater und Reliktwahl fuer jede Sitzung lahm

**Adressat:** developer
**Betroffen:** `nrplanner/effectfilters.py` `EffectFilters.__init__`/`mark`
(zwei getrennte `store()`-Schreibvorgaenge), `nrplanner/advisor/types.py:176`
`SlotProblem.__post_init__`, `advisorbar.asking_from:426`,
`relicpicker.RelicPicker._card_for`
**Umgebung:** Registry `advisor/excluded=7000302`, `advisor/required=7000302`

**Reproduktion:**
1. Beide Schluessel mit derselben Id belegen (ausserhalb der Oberflaeche
   oder: Prozessende zwischen `store(EXCLUDED)` und `store(REQUIRED)` beim
   Wechsel required -> excluded).
2. Programm starten, Spielstand lesen lassen.

**Erwartet:** die Kollision wird beim Laden aufgeloest (AD-036.1: "the
window keeps them apart").
**Tatsaechlich:** `EffectFilters` laedt beide Mengen ungeprueft;
`asking_from` wirft `ValueError` in `_the_save_has_been_read`, bei jedem
`recompute`/Gefaesswechsel und beim `RelicPicker`-Aufbau. Leiste bleibt auf
`No save was read …`, Optimize antwortet nie, Picker oeffnet nicht --
dauerhaft bei jedem Neustart, kein Weg in der Oberflaeche heraus.

**Analyse:** Die Disjunktheit gilt nur "by construction" in `mark()`; der
Store wird nicht validiert. Zwei nicht-atomare Schreibvorgaenge koennen den
Zustand erzeugen (Reihenfolge `store(EXCLUDED)` vor `store(REQUIRED)`).
**Auswirkung:** Kernfunktionen Berater und Reliktwahl unbenutzbar, bis der
Nutzer die Registry editiert. Likelihood niedrig (Absturz im ms-Fenster
oder Fremdeinwirkung), daher P2 statt P1.
**Vorschlag:** beim Laden `required -= excluded` (oder umgekehrt, eine
Zeile) und/oder `SlotProblem` nie aus einem unbereinigten Store bauen;
Testfall mit kollidierendem Store.

### [P3 | Major | Niedrig] 250-ms-Debounce nach Optimize: Aenderung in diesem Fenster wird nicht als veraltet erkannt

**Adressat:** developer
**Betroffen:** `nrplanner/advisor/worker.py` `DEBOUNCE_MS = 250`,
`advisorbar.the_build_changed` (prueft `WORKING_STATES`), `_on_ready`
(kein Abgleich mit der aktuellen Frage)

**Reproduktion (offscreen, 23:01-Spielstand):**
1. Optimize klicken; Zustand bleibt `NOTHING_YET`, bis `started` nach der
   Debounce eintrifft (gemessen 266 ms).
2. Innerhalb dieses Fensters einen Effekt markieren (oder Deep of Night
   umschalten).

**Erwartet:** AK-289- bzw. 4.7-Satz, keine Antwort auf die alte Frage.
**Tatsaechlich:** Antwort erscheint als gueltig: `Maximise offensive
attributes — 3 of 3 slots filled.` mit 6 Zeilen, die den eben
ausgeschlossenen `Strength +3` zaehlen; beim Deep-Wechsel eine 3-Slot-Antwort
unter 6 sichtbaren Slots.
**Analyse:** `the_build_changed` haelt den Lauf nur an, wenn die Leiste
schon in einem `WORKING_STATE` ist; die anstehende Frage im Controller
laeuft mit den alten Mengen weiter, `_on_ready` vergleicht nicht mit der
aktuellen Frage. Fuer Build-Aenderungen vorbestehend, fuer Markierungen
neu unter AK-289.
**Auswirkung:** Ein Vorschlag, der die Markierung ignoriert -- genau der
Fall, den AK-289 ausschliessen will; nur mit einer Aktion < 250 ms nach dem
Klick erreichbar.
**Vorschlag:** anstehende Frage beim Aendern verwerfen (Generation
hochzaehlen) oder `_on_ready` gegen `asking_from` der Gegenwart pruefen.

### [P3 | Minor | Hoch] Rohe Feldnamen als "Zahl" in Why-Zeilen: `conditionHp +40`, `physicsAttackPower -30`

**Adressat:** developer
**Betroffen:** `nrplanner/model.py` `label_for` (Fallback = Feldname),
`compute` (faltet den Schwellenwert `conditionHp` einer erklaerten Bedingung
in `build.other`), `advisor/explain._named`, `statsheet.py:846` (derselbe
Block)
**Umgebung:** frozen_inventory 314, Wylder's Chalice, Grundlinie

**Reproduktion:** Optimize `Minimise damage taken`, Why des Top-Vorschlags.
**Erwartet:** eine Zeile nennt eine Wirkung mit Anzeigename, oder sie
schweigt mit Grund (AK-167).
**Tatsaechlich:** `Slowly restore HP for self and nearby allies when HP is
low: conditionHp +40` und `Improved Damage Negation at Low HP: conditionHp
+40` (beide `modifiers` nur Schwelle + Verweis); die Gruppenzeile zaehlt sie
als "moved a number", der Score aendert sich beim Ausschluss **nicht**
(Rangfolge identisch). Zweiter Fall: `Starting armament deals magic damage:
physicsAttackPower -30, counted against it` / `magicAttackPower +33`
(QA-113-Felder seit T-246 gefaltet, ohne Label). 264 von 360 Zeilenkoerpern
der 9 Fragen bei `min_damage_taken`, 6 unterschiedliche Saetze.
**Analyse:** Vorbestehend (auf `dde2efc` Best case wortgleich), durch die
A18-Grundlinie jetzt Voreinstellung. Der Gate-Wert ist kein Beitrag.
**Auswirkung:** A7/A8: interner Bezeichner und eine falsche "Zahl" im
Hauptpfad des Why; Rangfolge unberuehrt.
**Vorschlag:** `CONDITIONAL_FIELDS` beim Falten ueberspringen; Labels fuer
die vier flachen `*AttackPower`-Felder; Waechter "kein camelCase im
Why-Text".

### [P3 | Minor | Mittel] 4.11 sagt unter unerfuellbarer Pflicht `3 slots have nothing to choose from`

**Adressat:** ui-ux-designer (Wortlaut/Zustand), developer
**Betroffen:** `advisorbar.status_line` (`SUGGESTED_WITH_AN_EMPTY_SLOT`,
`_slots_with_nothing`), AK-291.2
**Reproduktion:** Effekt ohne besessene Kopie als Must include, Optimize.
**Erwartet:** AK-291.2 -- 4.11 `0 of 3 slots filled`, Grund im Why.
**Tatsaechlich:** `Minimise damage taken — 0 of 3 slots filled  ·  3 slots
have nothing to choose from.` -- die Slots haben 53/55/214 passende Kopien;
die zweite Klausel behauptet einen falschen Grund. Der richtige steht im
Why-Footer (AK-281-Satz).
**Analyse:** `slots_without_a_choice = slots - filled` unterscheidet
leeren Pool nicht von leerem Beam.
**Auswirkung:** A7/A12 in der Statuszeile; `Why` ist einen Klick entfernt.
**Vorschlag:** zweite Klausel nur bei leerem Pool; unter Pflicht eine
Klausel, die auf die Markierung zeigt.

## Beobachtungen (keine Befunde)

Ein offener Why-Dialog behaelt nach einem Klick auf sein eigenes Bullet die
alte Zaehlzeile (`2 of its 3 effects moved a number`) neben der jetzt
durchgestrichenen Zeile, waehrend die Leiste die Antwort schon verworfen
hat. Zwei Zeilen desselben Effekts tauschen zwischen `dde2efc` und
`528ff78` die Reihenfolge. Die Karte `RelicPicker` holt die Mengen ueber
`self.slot.window().effect_filters` -- ein `RelicSlot` ohne `Planner`
als Fenster kann keinen Picker bauen.

## Offene Fragen

- **director:** GOAL A18 Satz 1 verlangt, dass die Begruendung "bei jedem
  gezaehlten bedingten Effekt seine Bedingung nennt". Die Why-Zeile eines
  gezaehlten bedingten Effekts lautet `Improved Attack Power with 3+
  Thrusting Swords Equipped: Physical Attack +20.0%` -- die Bedingung steht
  nur im Effektnamen. Kein AK deckt den Satz; Spec-Konflikt oder Absicht?

## Nicht getestet

Zielgeraet (Laptop, A6 absolut); PrintWindow-Bilder des Hauptfensters
(nur `grab()` einzelner Widgets); Deep-of-Night-Slots unter Markierung;
`Effects & chances`-Tab; Registry-Verhalten einer zweiten ORG (nur eigene);
Tastaturfokusring-Optik (AK-278, Bild nicht ausgewertet).

## Nachtrag Volllauf

`pytest -n auto` auf `528ff78` (MUTATIONS geleert, Spielstandkopie 23:01):
**1592 passed, 10 skipped, 3 failed** in 71 s -- genau das QA-266-Trio, kein
QA-249-Flackern. Register-Waechter `test_findings_tables.py` gruen.

## Urteil

**FAIL** -- A18/A19 belegt erfuellt (alle Nachweise oben), aber QA-267
(P2, Critical/Niedrig): ein kollidierender Store legt Berater und
Reliktwahl dauerhaft lahm. Mindestens zu beheben: QA-267 (Bereinigung beim
Laden). QA-268/269/270 als CONCERNS zur Entscheidung.
