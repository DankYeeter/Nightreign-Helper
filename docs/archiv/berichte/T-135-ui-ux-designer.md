# T-135 - AK-218 ist zu eng gefasst (ui-ux-designer, Spec-Modus)

```
STATUS: erledigt
AUFTRAG: T-135 - AK-218 nachziehen, so dass der Cache-Treffer darin vorkommt (OF-30)
GELESEN: docs/tasks/T-135.md, ~/.claude/agents/_rahmen.md, CLAUDE.md,
  ARCHITECTURE.md (Nachtrag X: X-0 bis X-3 und die AK-218-Meldung ab Zeile 5250),
  docs/berichte/T-134-architect.md, UI_SPEC.md (T-124- und T-127-Abschnitt
  vollstaendig, Zeigerblock ab Zeile 835), nrplanner/advisor/worker.py
  (ask_and_answer_if_known, _question_from, _cache), nrplanner/advisor/run.py
  (ResultCache, cache_key), nrplanner/relicpicker.py (SlotAdvice.ask,
  Wartezustand, setModal), tests/picker_track.py, tests/test_picker_track_guards.py
  (W6). GOAL.md und docs/state.md nicht von vorn - der Auftrag zitiert A6 und
  den F-P-Auszug, und beide tragen ihn.
GEAENDERT: UI_SPEC.md (206 Zeilen eingefuegt, 0 geloescht: neuer Abschnitt
  "AK-218 nachgezogen ..." am Dateiende, ein Vermerk unter AK-218 in T-127 §9,
  ein Zeiger am Ende von T-127 §6);
  .claude/agent-memory/ui-ux-designer/feedback_criteria_name_the_state.md (neu)
  und MEMORY.md (eine Zeile); docs/berichte/T-135-ui-ux-designer.md (diese
  Datei). Nichts gestaged, nichts committet.
ANNAHMEN: keine geraten. Eine Aussage ist hergeleitet und unten als solche
  markiert: dass zwei Oeffnungen desselben Slots den Zwischenspeicher wirklich
  treffen (Schluessel und Vorrichtung tragen es, gefahren habe ich es nicht).
NAECHSTER: director - er erteilt U10 (W8) an den `developer`; AK-218 Fassung 2
  ist die Vorgabe, gegen die W8 gebaut wird.
BLOCKIERT DURCH: nichts.
```

## Ergebnis in Kuerze

**AK-218 hat eine Fassung 2**, verbindlich; **Fassung 1 bleibt woertlich
stehen** und traegt einen Vermerk mit Grund und Zeiger. **Keine neue
AK-Nummer** (AK-220 bleibt frei), **keine gestrichene**, kein anderes
Kriterium beruehrt. Aus dem Nachzug folgt **keine Zeile Anwendungscode** - der
gebaute Zustand war nie falsch, der Satz war es.

Der Kern in einem Satz: **Fassung 1 machte die Leitung zur Bedingung
(`ready`/`failed`/`stopped`), Fassung 2 macht den Zustand zur Bedingung
(Karten stehen).** Die Wege hinein stehen darunter und duerfen wachsen.

## AK-218, Fassung 2 - der Wortlaut

Vollstaendig in `UI_SPEC.md`, Abschnitt „AK-218 nachgezogen: die Antwort, die
schon bekannt war (ui-ux-designer, T-135) - 2026-09-08", §2. Verkuerzt:

Eine Oeffnung, die ueberhaupt eine Reliktkarte anzubieten hat, **zeigt
Karten**, auf genau einem von zwei Wegen:

- **(a) Die Antwort war beim Fragen schon bekannt.** Rueckgabewert
  (IX-1.3), **kein** Wartezustand, das Raster steht **im ersten Anstrich**
  vollstaendig; `Your relics appear here.` und der Wartesatz aus AK-214
  erscheinen **nie**. Das ist der eine Anstrich, den AK-211 erlaubt.
- **(b) Die Frage lief.** Bis zu ihrem Ende gilt AK-212; sie endet in genau
  einem von `ready`, `failed`, `stopped`, und jeder der drei fuellt das Raster
  (unveraendert aus Fassung 1, samt Kopfzeile aus AK-208 und
  `<reason>` = `the search was stopped`).

**Ein Ende, nach dem das Raster leer bleibt, ist ein Fehler - gleich ob es ein
Signal war, ein Rueckgabewert oder keines von beidem.** Das ist die Zusage;
die Aufzaehlung der Wege ist ihr nachgeordnet und waechst mit.

## Was ein Waechter daran pruefen kann, ohne Millisekunden (Frage 2 des Auftrags)

1. **Gezaehlt wird, was im Rollbereich steht, nicht welches Signal geflossen
   ist.** `cards_in(dialog)` nicht leer, `area_labels(dialog)` ohne
   `Your relics appear here.`, Kopf- und Wertzeilen nach der Tabellenzeile.
   Werkzeug vorhanden in `tests/picker_track.py`.
2. **Der Treffer braucht eine Positivkontrolle.** Eine zweite Oeffnung, die
   den Zwischenspeicher **verfehlt**, sieht am Ende genauso aus wie eine, die
   ihn trifft - Karten stehen, nur einen Anstrich spaeter. Zwei Belege, beide
   ohne Uhr: `answers.calls == 1` ueber beide Oeffnungen, und **im ersten
   Anstrich der zweiten Oeffnung stehen schon Karten** (geprueft vor jedem
   `spin`). Ohne das misst der Fall sein eigenes Pruefmittel.
3. **„Ohne Millisekunden" heisst: keine Frist, an deren Ablauf eine Behauptung
   haengt.** `spin(qapp, until)` wartet auf einen Zustand, seine Frist ist eine
   Sicherung und kommt in keiner Behauptung vor. Drei Formulierungen, die W8
   nicht benutzen darf: „innerhalb von X ms gefuellt", „die Leere dauert
   hoechstens X ms", und - schon fachlich falsch - „der Dialog zeichnet
   zweimal" (bei Weg (a) zeichnet er einmal).
4. **Bauform: Tabelle „Weg hinein -> was die Oberflaeche danach zeigt",
   Mengengleichheit in beide Richtungen** - dieselbe Form, die X-2 fuer die
   unterbrechenden Stellen gewaehlt hat. Heute zwei Zeilen. Ein dritter Weg
   ohne Zeile macht W8 rot, und genau das haette den heutigen Fall am Tag
   seiner Entstehung (U5b) gefunden.
5. **W6 bleibt richtig** - er faehrt Weg (b). Ihm fehlt nur eine Zeile fuer
   Weg (a), und das ist W8s Gegenstand.

## Was ich nicht geprueft habe, und was daraus folgen kann

- **Nichts gestartet, nichts gemessen.** Keine Datenverzeichnisse umgelenkt,
  weil nichts lief. Der Abschnitt enthaelt keine Zahl ueber die Oberflaeche
  und braucht deshalb keine Messumgebung (L-009); die 30 % sind aus S11-F
  zitiert.
- **Die Vorrichtung fuer Weg (a) habe ich nicht gefahren.** Getragen ist sie
  von zweierlei, das ich nachgesehen habe: `cache_key` nimmt die Generation
  aus dem Schluessel heraus (`advisor/run.py`, `ResultCache.get`), zwei
  Oeffnungen desselben Slots koennen sich also treffen; und
  `tests/picker_track.py:a_track` nimmt einen Zwischenspeicher entgegen, ein
  Fall kann ihn auch vorbelegen. **Trifft er in der Praxis trotzdem nicht, ist
  das ein Befund und kommt zurueck** (L-008c) - er waere dann groesser als
  dieses Kriterium, weil die 30 % aus S11-F an derselben Mechanik haengen.
- **Kein Test der Suite gefahren**, keine Zahl gegen die 1257/1323 zu nennen.

## Beruehrt der Nachzug mehr als AK-218?

**Drei Stellen in `UI_SPEC.md`, alle rein additiv** (`git diff --numstat`:
206 eingefuegt, **0 geloescht**):

| Stelle | was |
|---|---|
| Dateiende | der neue Abschnitt mit Fassung 2 |
| T-127 §9, unter AK-218 | Vermerk: dies ist Fassung 1, Grund, Zeiger auf Fassung 2 |
| T-127 §6, am Ende | Zeiger: dieser Abschnitt kennt nur einen von zwei Wegen |

**Warum die dritte Stelle.** §6 ist die Begruendung, aus der AK-218
hervorgegangen ist, und zitiert den alten Docstring, den X-0 gerade ersetzt.
Wer den Nachzug nicht dort findet, liest die zu enge Fassung an der Stelle,
an der man sie zuerst liest. Der Text selbst ist unangetastet - nur ein
Kasten darunter, in derselben Form wie die Zeiger, mit denen der `architect`
AD-028 versehen hat.

**Nicht angefasst und ausdruecklich nicht noetig:** AK-211 (sie erlaubt den
einen Anstrich seit T-127, „hoechstens zwei Zustaende"), AK-212 samt Ausnahme,
AK-207, AK-208, der Zeigerblock ab Zeile 835 (er verweist auf den
T-127-Abschnitt, und dort steht jetzt der Vermerk - die Kette bleibt heil).

## Textpflege am Code - kein Auftrag aus diesem Nachzug

Sieben Stellen zitieren AK-218 in Code und Tests
(`nrplanner/relicpicker.py:133,140,228,388,913,1377,1439`,
`tests/test_picker_track_guards.py:28,515`). **Alle bleiben inhaltlich
richtig** - sie beschreiben Weg (b). Bei der naechsten Beruehrung sollte der
Zeiger auf **Fassung 2, Weg (b)** lauten. **Daraus folgt keine
Verhaltensaenderung und kein eigener Auftrag**; wer U10 baut, kann es
mitnehmen.

## Offene Fragen an den App Designer

**Keine neue.** Dieser Nachzug hat keine Geschmacksentscheidung in sich - der
gebaute Zustand ist der bessere, der Satz war zu eng.

**Unveraendert offen aus T-127: F-R** (`Sort by` = `Name` - die einzige
Oeffnung, bei der nichts umzusortieren waere; Empfehlung weiterhin: so lassen).
Der Nachzug beruehrt sie nicht.

## Was der Auftrag noch nennt

- **Committet ist nichts**, wie beauftragt. Im Arbeitsbaum stehen ausserdem
  `ARCHITECTURE.md` (T-134), `nrdata/savefile.py` und
  `tests/test_relic_scan_prefilter.py` (T-133, laeuft parallel) - **nicht
  gelesen ausser Nachtrag X, nicht angefasst.**
- **Nummernkreise:** AK unveraendert ab **AK-220**. OF ab **OF-31** (OF-30 ist
  mit diesem Lauf beantwortet und kann geschlossen werden).
