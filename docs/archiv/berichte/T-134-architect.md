# T-134 - Drei Punkte aus dem Waechterbau (architect)

```
STATUS: erledigt
AUFTRAG: T-134 - Drei Punkte aus dem Waechterbau (AD-028, Vertrag des AdvisorController)
GELESEN: docs/tasks/T-134.md, ~/.claude/agents/_rahmen.md, CLAUDE.md, GOAL.md (A6),
  docs/state.md (Nummernkreise, Zyklus 18), ARCHITECTURE.md (AD-028, AD-029,
  Nachtrag VIII und IX, W1-W5), docs/tasks/T-131.md (W6, W7),
  docs/berichte/T-131-developer.md (Befunde 1-3), nrplanner/advisor/worker.py
  (vollstaendig), nrplanner/advisor/run.py (slot_pool), nrplanner/app.py
  (closeEvent, shutdown_the_advisor), nrplanner/relicpicker.py (SlotAdvice),
  tests/test_picker_track_guards.py (W1, W6, W7), UI_SPEC.md (AK-211 bis AK-219),
  ls docs/research/ und docs/legal/ (kein R-/C-Lauf ist T-134 vorgeschaltet)
GEAENDERT: ARCHITECTURE.md (Nachtrag X angehaengt; zwei Zeiger in AD-028: Kopfzeile
  und W1-Punkt). Nichts committet, nichts gestaged.
ANNAHMEN: keine geraten. Eine Aussage ist hergeleitet und als solche markiert:
  dass nach shutdown() ein spaetes `ready` zustellbar ist, folgt aus dem Code
  (shutdown erhoeht die Generation nicht) und ist nicht im Feld beobachtet.
NAECHSTER: director - er erteilt U9 und U10 an den `developer` und gibt die
  AK-218-Meldung an den `ui-ux-designer`.
BLOCKIERT DURCH: nichts.
```

## Ergebnis in Kuerze

Alle drei Punkte sind entschieden, ohne neue AD-Nummer: **Nachtrag X** schreibt
AD-028 fort (`ARCHITECTURE.md`, ab Zeile 4952). Neu vergeben: **W8** (ein
Waechter), **OF-30** (eine offene Frage), **U9** und **U10** (zwei
Umsetzungsschritte). AD bleibt bei **AD-030**.

Zwei Zeiger sind in AD-028 selbst gesetzt, damit niemand den alten Wortlaut
allein liest: in der Kopfzeile der Entscheidung und am W1-Punkt. **Der alte
Wortlaut ist nirgends ueberschrieben** — beide Fassungen stehen nebeneinander.

## Punkt 1 - `shutdown()` (X-1): praezisieren **und** eine Zeile Fix

**Der Befund haelt und traegt weiter, als er gemeldet wurde.** `shutdown` ist
die einzige der unterbrechenden Stellen, die den Generationszaehler **nicht**
erhoeht (`worker.py:371-383` gegen `cancel` in `351` und `_question_from` in
`322`). Damit ist der Ausgang nach `shutdown` nicht „Schweigen", sondern
**unbestimmt**: hat der Worker sein `ready` abgeschickt, bevor er die
Unterbrechung bemerkt, liegt es in der Warteschlange des Hauptthreads,
`thread.wait()` verarbeitet sie nicht, und `_on_ready` (`444-456`) findet die
Generation unveraendert und sendet — nach `closeEvent` (`app.py:2039-2041`).

**Hergeleitet, nicht gemessen.** Ich behaupte nicht, dass es im Feld vorkommt;
ich behaupte, dass die Klasse es nicht ausschliesst. Die Folge fuer den
Auftrag ist dieselbe: **ein Waechter ueber „nach shutdown kommt nichts" waere
ohne den Fix ein Wettlauf**, also kein Waechter.

**Entschieden (X-1 Option D):** Docstring bekommt die praezise Fassung aus X-0,
und `shutdown` erhoeht den Zaehler vor dem Unterbrechen. **Verworfen:** nur den
Text praezisieren (Zusage mit „meistens" ist keine); `shutdown` sendet
`stopped` (das Signal ist nach `UI_SPEC` 4.5 / AK-11 ein Satz an den Spieler
und zeichnet Zustand 4.5 in ein Fenster, das verschwindet); die Ausgaenge im
privaten Unterbrecher buendeln (Architektur auf Vorrat bei vier Stellen).

## Punkt 2 - `search.Cancelled` (X-2): es sind **vier** Aufrufer, nicht drei

`_Worker.work` schluckt `Cancelled` (`186-187`) — und `slot_pool` kann es
tatsaechlich ausloesen, es reicht `should_cancel` an die Vorsortierung durch
(`run.py:463-464`, geworfen in `search.py:327`). Der Weg ist auf **beiden**
Spuren offen.

**Nachgezaehlt am Stand `0128971`:** `_interrupt_the_running_worker` wird an
**vier** Stellen gerufen — `worker.py:309` (`ask_and_answer_if_known`,
Cache-Treffer), `334` (`_wait_for`), `354` (`cancel`), `380` (`shutdown`). Die
vierte ist nicht tot: der Picker ruft `ask_and_answer_if_known` bei jeder
Oeffnung (`relicpicker.py:413-415`), Trefferquote gemessen 30 % (S11-F). Sie
stand seit `1a2cc5b` (U5b) im selben File; `worker.py` ist seither unveraendert
(`git log 61a3f2c..0128971 -- nrplanner/advisor/worker.py` ist leer).

**Antwort auf die gestellte Frage: nein**, „haelt ueber drei Aufrufer" ist als
Verhaltenszusage **nicht bewachbar** — sie behauptet etwas ueber das
Komplement einer Menge von Aufrufstellen, und kein abspielbarer Fall zeigt die
Abwesenheit einer Stelle, die niemand geschrieben hat. Der Beleg ist die
Aussage selbst: sie war am Tag ihrer Niederschrift falsch gezaehlt.

**Bewachbar ist sie als Struktur** — deshalb **W8**: eine Tabelle der
unterbrechenden Stellen **im Test** (Methodenname → welchen Ausgang die
abgehende Frage hoert), Mengengleichheit in beide Richtungen, zwei toetende
Mutationen (fuenfte Stelle einsetzen; Aufruf in `cancel` entfernen). W8 prueft
**Vollstaendigkeit** der Waechter W3 und W6, nicht Verhalten — das steht
ausdruecklich im Nachtrag.

**Verworfen:** `_Worker.work` sendet `stopped` auf `Cancelled`. Nach `cancel()`
haette die Frage dann zwei `stopped` — „genau einer der drei" waere gebrochen,
um „genau einer der drei" herzustellen.

## Punkt 3 - W1 (X-3): **so ist es gemeint**, der Wortlaut wird nachgezogen

Die drei Stellen sind am Quellstand belegt und richtig. Fassung 2 ist
verbindlich, Fassung 1 bleibt woertlich stehen. Drei Aenderungen:

1. **„nennt" statt „ruft auf"** — der gebaute Waechter zaehlt Nennungen; das
   ist strenger und richtig (eine Referenz ist ein Aufruf einen Schritt
   spaeter). Fassung 1 war hier zu **schwach**, nicht zu streng.
2. **Die Pool-Funktion heisst jetzt `run.slot_pool`.**
3. **Vierte Zeile: `candidates.pools` (Mehrzahl), erlaubt nur in
   `advisor/run.py`** (`run.py:379`). Kein Vorrat: IX-5 hatte genau diesen Weg
   als Vorschlag auf dem Tisch (`candidates.pools()` beim Oeffnen des Build
   planners, 610,7 ms im Hauptthread, S11-C). Ohne die Zeile bewacht W1 die
   naechstgelegene Umgehung seiner selbst nicht.

**Die Alternative des `developer` ist verworfen** (die Antwortfunktion der
Picker-Spur ueber `worker.py` benennen): sie machte Fassung 1 woertlich wahr
und kostete den Kern von Option D — `worker.py` wuesste dann, welche Spur
welche ist, waehrend sein eigener Docstring zu Recht sagt *„Nothing here asks
which track it is"*. **Kein Auftrag an den `developer` fuer `app.py`.**

**Randbedingung, die bisher nirgends stand:** W1 haengt an
`test_one_build.call_sites` und damit an Modulkurzname plus Funktionsname. Eine
Rechnung, die unter einem **anderen Namen** in den Hauptthread kaeme, sieht er
nicht. Das ist seine Grenze, keine Luecke — sie gehoert in den Docstring der
Tabelle (Teil von U10).

## Meldung: AK-218 ist enger als der gebaute Zustand (`UI_SPEC.md` nicht angefasst)

AK-218 verlangt fuer **jede** Frage einer Oeffnung einen der drei Ausgaenge.
Der Cache-Treffer erfuellt das nicht — er endet im **Rueckgabewert** von
`ask_and_answer_if_known` (`relicpicker.py:413-417`, `worker.py:288-290`), so
von IX-1.3 entschieden und von AK-211 („hoechstens zwei Zustaende")
vorausgesetzt. Betroffen ist nur der **Wortlaut**; die Sache („ein Ausgang, der
das Raster leer laesst, ist ein Fehler") gilt weiter. Formulierungsvorschlag
steht in Nachtrag X. **Das ist OF-30**, Adressat `ui-ux-designer`.

*Warum W6 es nicht gefunden hat:* seine fuenf Vorrichtungen fahren alle ueber
`ask` (`tests/test_picker_track_guards.py:436-506`); den zweiten Weg hinein
kennt keine davon.

## Beobachtung nebenbei, ohne Auftrag: der W-Kreis ist doppelt belegt

**`W6` bedeutet in `ARCHITECTURE.md` zwei verschiedene Dinge** — die
Fassaden-Kette aus AD-019 (`W0`-`W6`, Zeilen 1835 und 2662) und die Waechter
der Picker-Spur (`W1`-`W7`). Die Kollision besteht seit T-131. Ein Praefix
(`AW-1` fuer die Waechter) waere die Loesung; sie beruehrt Testnamen und
Berichte und ist **eine Entscheidung des `director`**, nicht meine. Im Nachtrag
steht sie unter „bewusst nicht getan".

## Umsetzung - direkt als Auftraege verwendbar

| # | Rolle | Inhalt | Dateien |
|---|---|---|---|
| **U9** | `developer` | `shutdown` erhoeht den Generationszaehler vor dem Unterbrechen; Klassen-Docstring `worker.py:198-216` auf die Fassung aus X-0; **sechster W6-Fall** „the window is closing", erwartete Ausgangsliste **leer** als Literal | `nrplanner/advisor/worker.py`, `tests/test_picker_track_guards.py` |
| **U10** | `developer` | **W8** neu (Tabelle der vier unterbrechenden Stellen, zwei Mutationen); **W1** um `candidates.pools` → `advisor/run.py` erweitert und um die Randbedingung im Docstring der Tabelle | nur `tests/` |

U9 und U10 haengen an nichts und nicht aneinander; sie beruehren dieselbe
Testdatei und sollten deshalb **nicht gleichzeitig** laufen.

**Die Vorrichtung des sechsten W6-Falls, damit er nicht versehentlich gruen
wird:** Antwortfunktion festhalten (`picker_track.StatedAnswers(..., hold=True)`),
**eine** Frage ueber `ask`, warten bis `answers.calls == 1`,
`track.shutdown(timeout_ms=0)`, **danach** freigeben, Schleife ausdrehen,
erwartete Ausgangsliste **leer** (Literal, nicht aus `shutdown` gerechnet,
L-008b). *Toetende Mutation:* die Zaehlererhoehung aus `shutdown` entfernen →
die freigegebene Antwort traegt die gueltige Generation → `ready` → rot.
**Ueberlebt sie, ist das ein Befund und wird berichtet** (L-008c) — dann stellt
die Vorrichtung ihren Fall nicht her.

## Was der `developer` ausdruecklich **nicht** tun soll

- `shutdown` **kein** Signal senden lassen, auch nicht bedingt.
- `_Worker.work` auf `search.Cancelled` **nichts** senden lassen.
- `_interrupt_the_running_worker` **keine** Signatur geben (X-1 Option C).
- `app.py` **nicht** anfassen, um Fassung 1 von W1 woertlich wahr zu machen.
- `UI_SPEC.md` **nicht** anfassen — AK-218 gehoert dem `ui-ux-designer`.
- Entprellung, Cache-Groessen und Antwortformen **nicht** beruehren (IX-1,
  IX-3, U7).

## Offene Fragen

- **OF-30** (an den `director`, Adressat `ui-ux-designer`): AK-218 im Wortlaut
  gegen den gebauten Zustand — siehe oben. **Nummernkreis danach: OF ab OF-31.**
- **Nicht neu, aber offen und beruehrt:** OF-25 (Ueberlappung zweier Spuren),
  OF-26, OF-28 (Groesse eines Picker-Cache-Eintrags) gehen unveraendert an den
  `performance-tuner` (U7).

## Was ich nicht geprueft habe

- **Nichts gestartet, nichts gemessen** (Auftrag: „Lesen ja, starten nein").
  Keine Suite gefahren; die Zahl **1323 passed, 9 skipped, 0 failed** stammt
  unveraendert aus T-131 und ist nach dessen eigenem Befund 3 erst stabil, wenn
  T-132 committet hat.
- **Ob der sechste W6-Fall in der Praxis rot wird**, ist nicht ausprobiert —
  das ist U9s Nachweis, und der Nachtrag verlangt ihn als Befund, falls die
  Mutation ueberlebt.
- `nrdata/savefile.py` und `tests/test_relic_scan_prefilter.py` stehen im
  Arbeitsbaum geaendert bzw. neu (T-133 laeuft parallel). **Ich habe sie nicht
  gelesen, nicht angefasst und nicht committet.**
