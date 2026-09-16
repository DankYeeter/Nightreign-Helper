# T-141 — ui-ux-designer (Spec-Modus)

```
STATUS: erledigt
AUFTRAG: T-141 — Drei Zustaende rund um das Lesen des Spielstands (Spec-Modus)
GELESEN: docs/tasks/T-141.md · ~/.claude/agents/_rahmen.md · CLAUDE.md ·
  GOAL.md (A6, A7, A8, A12, A15) · ARCHITECTURE.md AD-029 vollstaendig samt
  Schnitt-Tabelle (U1-U8) · UI_SPEC.md (Inhaltsverzeichnis, T-074 Erststart,
  T-127 vollstaendig, T-135 vollstaendig) · docs/berichte/T-127-ui-ux-designer.md
  und T-135-ui-ux-designer.md (nur die Nummernkreis-Zeilen) · docs/state.md
  Zeile 164 (AK-Register) · Quellstand: nrplanner/app.py (main, Planner.__init__,
  _build_left, RelicSlot, rescan_save, load_equipped, select_hero, _apply_chalice),
  nrplanner/inventory.py (Inventory, load, _scan_save), nrdata/savefile.py
  (Vorfilter, _check_the_prefilter_can_see_every_id, read_owned_relics,
  _loadout_marker_offsets)
GEAENDERT: UI_SPEC.md (604 Zeilen eingefuegt, 0 geloescht; uncommittet)
ANNAHMEN: keine
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

## Ergebnis in einem Satz

Der dritte Fensterzustand, der Rueckfallsatz und die Praefix-Reibung stehen als
**ein** Abschnitt in `UI_SPEC.md` (§0 bis §14), mit vollstaendigem englischen
Wortlaut und **AK-220 bis AK-229**; **F-R ist geschlossen** — an der offenen
Stelle in T-127 §11 und als eigener Nachtrag am Dateiende.

## Was spezifiziert wurde

1. **Der dritte Zustand** — Start und `Rescan` als zwei Situationen einer
   Bauform. Die Asymmetrie traegt den Entwurf: beim `Rescan` gilt der vorige
   Bestand bis zur Ankunft weiter (AD-029 Form 3), es geht **nichts** verloren;
   nur beim Start gibt es ueberhaupt nichts anzuzeigen.
2. **Der Rueckfallsatz** — englischer Wortlaut, angehaengt an die
   Bestandsnotiz, nicht an eine Fehlerzeile.
3. **Die Praefix-Reibung** — geloest ohne bedingtes Praefix: der Satz nimmt
   einen anderen Weg (Feld am Ergebnis, wie `loadout_error`), das Praefix
   behaelt seine Bedeutung, und AK-229 sichert die **Eigenschaft** statt der
   Fundstelle.

## Die Kernentscheidungen, je in einer Zeile

- **Das Fenster steht vor dem Spielstand** — alles, was ihn nicht braucht, ist
  im ersten Anstrich fertig (A15). Heute erscheint waehrend des Lesens
  ueberhaupt kein Fenster (`rescan_save(initial=True)` in `__init__`,
  `window.show()` erst danach).
- **Eine Zeile sagt, was laeuft** (`owned_label`), zwei Wortlaute: Start und
  `Rescan`. Kein Balken, kein Spinner, kein Cursor, keine Zeitschwelle.
- **Leere Slotkarten sagen beim Start, warum sie leer sind** — ueber die
  vorhandene `empty_reason`/`reason_holds`-Vorrichtung, die sich selbst
  loescht. Kein neues Widget, kein neues Token.
- **Gesperrt ist genau ein Bedienelement**: der Reliktknopf. Begruendet, warum
  das AK-213 nicht widerspricht (dort kann das Element seine Arbeit noch tun,
  hier nicht) und warum es auch beim `Rescan` gilt (kein modaler Picker, dem
  der Bestand unter den Karten getauscht wird).
- **`(0 available)` erscheint nicht** waehrend des Lesens — die Zahl ist nicht
  null, sondern unbekannt (A7).
- **Der Wartesatz ist nie das letzte Wort**: vier benannte Enden, und der Satz
  steht **ueber** der Aufzaehlung, damit ein fuenftes Ende ihn nicht bricht
  (dieselbe Lehre wie AK-218 Fassung 2).
- **Kein nachtraegliches Ueberschreiben**: hat der Spieler waehrend des Lesens
  einen Slot gesetzt, wird das gespeicherte Build in dieser Sitzung nicht mehr
  von selbst uebernommen — sonst faellt es beim naechsten Nightfarer-Wechsel
  unerwartet ueber seine Arbeit her.

## Die Akzeptanzkriterien (fuer den `developer`)

- **AK-220** Das Fenster ist vor dem Spielstand da und ohne ihn bedienbar.
- **AK-221** Der Wartezustand ist ein Zustand: eine von zwei Zeilen, woertlich,
  sonst nichts; kein Wartezeichen irgendeiner Art.
- **AK-222** Keine Zahl und keine Aussage ueber einen ungelesenen Bestand.
- **AK-223** Gesperrt ist genau der Reliktknopf, sonst nichts.
- **AK-224** Jedes Lesen endet in einem der vier benannten Enden; ein Ende, nach
  dem die Zeile noch wartet, ist ein Fehler.
- **AK-225** Die Ankunft bewegt nichts — mit Messauflage (L-009) auf die Hoehe
  der Spielstandzeile.
- **AK-226** Kein nachtraegliches Ueberschreiben gesetzter Slots.
- **AK-227** Ein Lesen zur Zeit — Zaehlwert gegen ein Literal.
- **AK-228** Der langsame Weg ist kein Fehlschlag: volle Notiz plus Zusatz,
  gleiche Reliktzahl wie auf dem schnellen Weg, kein Alarmwort.
- **AK-229** Das Praefix `Save could not be read: ` behaelt seine Bedeutung —
  als Eigenschaft, mit Positivkontrolle gegen den heutigen Wortlaut.

Keines dieser Kriterien nennt eine Millisekunde; gewartet wird auf Zustaende.

## Die Texte, woertlich (A8)

```
Reading your save.
Reading your save again. Nothing changes until it is done.
Your relics appear when the save has been read.
 — read the slow way: this version of the game numbers its relics above what the quick scan looks for. Nothing is missing and nothing needs fixing.
```

Unveraendert bleiben die Bestandsnotiz, `No save file found. …` und
`Save could not be read: <reason>`.

## Befunde, die groesser sind als diese Vorgabe (ohne Nummer, L-008c)

1. **Den langsamen Weg gibt es im Code nicht mehr.** Zwei unabhaengig
   formulierte Suchen ueber `nrdata/savefile.py` (`range(0, len(slot_data)` und
   `fallback|Rueckfall|every fourth|four-byte`) finden genau **einen**
   Versatz-Erzeuger fuer Relikte (`_relic_id_offsets`, Zeile 209). Der
   Nutzerentscheid „faellt auf den alten, langsamen Weg zurueck" verlangt, dass
   dieser Weg **wieder gebaut** wird. Das steht in keinem Auftrag und ist
   Voraussetzung von AK-228.
2. **AD-029 Vertrauensgrenze Punkt 3 ist ueberholt.** Der Code setzt die
   Id-Annahme heute als **Verweigerung** um (`_check_the_prefilter_can_see_
   every_id`, Docstring *„Refuse to scan at all rather than scan half the
   ids"*). Der Entscheid vom 08.09.2026 verlangt den Rueckfall. Gehoert dem
   `architect`.
3. **Der heutige Wortlaut widerspricht sich schon jetzt auf dem Bildschirm** —
   `Save could not be read: … nothing is wrong with the save.` Das ist keine
   Folge von Stufe B, sondern seit T-133 im Bestand. Es verschwindet mit §7.
4. **Der A7-Bruch „kein Spielstand" im Picker** (seit T-124 offen) wird von
   AK-223 nur **umgangen**, nicht behoben.

## Offene Fragen an den App Designer

- **F-S — der langsame Weg, dauerhaft oder einmalig?** Die Vorgabe zeigt den
  Rueckfallsatz bei jedem Start und jedem `Rescan`, solange der Zustand
  anhaelt. Gegenoption: nur beim ersten Mal je Programmstart.
  **Empfehlung: dauerhaft** — der Zustand haelt an, also haelt die Aussage an,
  und sonst erklaert nichts mehr das langsame `Rescan`.
- **F-T — der gesperrte Reliktknopf beim `Rescan`?** Beim Start ist die Sperre
  zwingend, beim `Rescan` eine Vorsichtsmassnahme fuer den Bruchteil einer
  Sekunde. **Empfehlung: so lassen.** Entscheidet die Architektur, den
  Bestandstausch bis zum Schliessen eines offenen Dialogs zurueckzustellen,
  entfaellt die Frage.

## Methode und Nummernkreise

**Nichts gestartet, nichts gemessen, kein Bildnachweis, kein Server, kein
Prozess hinterlassen.** Keine der drei Datenverzeichnis-Variablen musste
umgelenkt werden, weil das Programm nicht gestartet wurde. Alle Aussagen ueber
das heutige Verhalten sind **Quelltextlesungen** und im Abschnitt als
**(Quelltext)** mit Zeilen belegt. Die drei genannten Zahlen (6147,6 ms,
657,2 ms, 250 ms) sind aus S11-E/T-140 bzw. AD-029 zitiert und stehen
ausschliesslich in der Begruendung.

**AK-220 vor der Vergabe geprueft** (Lehre aus T-124): Suche ueber alle `*.md`
und `*.py` nach `AK-220` — sieben Treffer, alle sagen „frei" (zwei Berichte,
`docs/state.md`, `docs/tasks/T-141.md`, zwei Stellen in `UI_SPEC.md`); dazu
eine Bereichssuche `AK-2[0-9][0-9]` ueber denselben Baum, hoechste vergebene
Nummer **AK-219**. **Nach diesem Lauf ist der naechste freie Kreis AK-230.**
Offene Fragen: **F-S** und **F-T** vergeben (F-R geschlossen).

**Scratchpad:** `…/scratchpad/T-141/`, nach dem Anhaengen geleert.

**Nicht committet** (Auftrag). `git status`: `M UI_SPEC.md`, sonst nichts.
