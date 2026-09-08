# T-127 — Leeres Raster statt frueher Karten: die Spec nachgezogen (ui-ux-designer, Spec-Modus)

STATUS: erledigt
AUFTRAG: T-127 — Leeres Raster statt frueher Karten: die Spec nachziehen (Spec-Modus, Nachzug an F-P)
GELESEN: `docs/tasks/T-127.md` · `CLAUDE.md` · `~/.claude/agents/_rahmen.md` (Rahmenregeln, wie im Auftrag verlangt) · `UI_SPEC.md` (T-124-Abschnitt vollstaendig, AK-197 bis AK-210; §3.8 samt Korrekturkasten; §3.2/§3.3/§3.7) · `ARCHITECTURE.md` Nachtrag IX vollstaendig (IX-0 bis IX-5, U5a–U7, Risiken, OF-28/OF-29) und AD-028 mit W1/W2 · `docs/state.md` Zeile 11 (Nummernkreise) · **Quellstand lesend, nichts veraendert, nichts gestartet:** `nrplanner/relicpicker.py`, `nrplanner/advisor/worker.py`, `nrplanner/advisorbar.py`, `nrplanner/app.py` · eigene Rollennotizen unter `.claude/agent-memory/ui-ux-designer/`
GEÄNDERT: `UI_SPEC.md` (drei Stellen, nichts geloescht: Ueberschrift und Korrekturkasten von §3.8 um den T-127-Zeiger erweitert; Hinweiskasten unter die T-124-Ueberschrift gesetzt; neuer Abschnitt „Leeres Raster bis zur Antwort (ui-ux-designer, T-127) — 2026-09-08" am Dateiende, AK-211 bis AK-219) · `docs/berichte/T-127-ui-ux-designer.md` (diese Datei) · `.claude/agent-memory/ui-ux-designer/` (eigene Rollennotiz zur F-P-Entscheidung, plus Indexzeile). **Nichts committet, nichts gestaged.** `git status` zeigt ausserdem `nrplanner/advisor/goals.py`, `nrplanner/advisor/run.py` und `tests/test_advisor_slot_pool.py` als geaendert bzw. neu — das ist der parallel laufende `developer` (T-128, U5a), **nicht von mir**; ich habe diese Dateien nicht angefasst.
ANNAHMEN: keine. Alle vier Fragen des Auftrags sind beantwortet, keine offengelassen; die eine Geschmacksfrage, die die Entscheidung neu erzeugt, steht als **F-R** im Abschnitt und unten.
NÄCHSTER: `director` — er hat drei Meldungen an den `architect` (unten Punkt 5) und eine Frage an den App Designer (F-R) einzuplanen; danach `developer` (U5b) gegen AK-211 bis AK-219.
BLOCKIERT DURCH: nichts.

---

## 1. Was spezifiziert wurde

Ein neuer Abschnitt am Ende von `UI_SPEC.md`: **„Leeres Raster bis zur Antwort
(ui-ux-designer, T-127) — 2026-09-08"**, elf Unterabschnitte, Wortlaut
vollstaendig auf Englisch (A8).

**Nachgezogen, nicht umgeschrieben.** Der T-124-Abschnitt bleibt Zeile fuer
Zeile stehen — einschliesslich seines §3.1, der die jetzt gewaehlte Option
verwirft. Darueber steht ein Kasten, der sagt, dass der App Designer F-P
gegen die Empfehlung entschieden hat und wo die geltende Fassung steht. Der
alte §3.8-Kasten (T-024-Abschnitt) zeigt jetzt auf beide Fassungen und nennt
die zweite als verbindlich.

**Die vier Fragen des Auftrags:**

1. **Was im leeren Raster steht** — eine Zeile, `Your relics appear here.`, an
   der Stelle der linken oberen Karte (nicht mittig: die erste Karte landet
   genau dort, wo die Zeile stand, das Auge wandert um Null). Kein Skelett,
   keine Platzhalterkarten, **auch nicht die Custom-Kachel** (eine einzelne
   Kachel in leerer Flaeche sieht mehr nach Fehler aus als die leere Flaeche).
   Was gerade geschieht, sagt Zeile 3 darueber; die Zaehlung `29 of 29 relics`
   faellt waehrend der Leere weg, weil sie Relikte ankuendigen wuerde, die
   nicht dastehen — und weil sie, sobald gefiltert wird, genau der
   Filtertreffer ist, dessen Verlust der App Designer in Kauf genommen hat.
2. **Die Dialoggroesse — geloest, kein Blocker.** Der Dialog misst sich beim
   ersten Anstrich an den Karten, **die er nicht zeigt**. Das geht, weil die
   Karten am Berater nicht haengen und weil die Messung schon heute eine
   Messung ausserhalb des Bildschirms ist (`_room_for_three_rows`,
   `heightForWidth` bei 190 px; der Docstring sagt es woertlich). `_sized`
   bleibt einmalig, die Aussenmasse aendern sich beim zweiten Anstrich nicht.
   **Damit faellt eine der drei Kosten weg, die die Abstimmungsvorlage genannt
   hat** („ohne Dialoggroesse") — ohne die Entscheidung anzutasten: ein
   Fenster, das sich 320 ms nach dem Oeffnen selbst vergroessert, waere die
   groesste Bewegung von allen und stuende gegen genau das, wofuer gestimmt
   wurde.
3. **Filterfeld, `Sort by`, Fokus waehrend der Leere** — alles da, alles
   freigegeben, nichts ausgegraut, kein Wartecursor (A6). Getippter Filtertext
   bleibt stehen und wirkt, sobald die Karten erscheinen; kein Anschlag geht
   verloren und keiner stellt eine zweite Frage (AK-206). Der Fokus springt
   beim Erscheinen der Karten **nicht** auf eine Karte.
4. **Der Fehlschlag** — und mehr als das: **die Leere ist nie das letzte
   Wort.** Der Controller sagt genau drei Ausgaenge zu (`ready`, `failed`,
   `stopped` — Klassen-Docstring in `worker.py`), und **jeder der drei fuellt
   das Raster**. `stopped` war unter „Karten sofort" folgenlos und ist jetzt
   der Unterschied zwischen „kurz leer" und „kaputt"; es bekommt die
   AK-208-Kopfzeile mit `<reason>` = `the search was stopped`.

## 2. Die Akzeptanzkriterien — AK-211 bis AK-219

Keine Millisekunde, alle an Zustaenden festgemacht, jede mit toetender
Mutation. Vorrichtungen: eine Spur, die nie antwortet · eine, die sofort
antwortet · eine, die `failed` meldet · eine, die `stopped` meldet.

| Id | in einem Satz |
|---|---|
| **AK-211** | Zwei Anstriche, nicht drei: **die Karten selbst**, Zahlen, Chips, Ordnung, Kopfzeile und Laufbefundzeile erscheinen gemeinsam in einem Anstrich. *(ersetzt AK-197)* |
| **AK-212** | Das leere Raster ist ein Zustand: kein Kartenwidget (auch nicht die Custom-Kachel), keine Karte per Tab erreichbar, die eine Zeile `Your relics appear here.`, Kopfzeile leer, Zeile 3 mit dem Wartesatz, die Pflichtzeilen vollstaendig. **Das ist der Waechter W2.** Ausnahme: bietet der Picker keine einzige Reliktkarte an, gibt es keinen Wartezustand. *(ersetzt AK-198)* |
| **AK-213** | Waehrend der Leere ist nichts gesperrt und nichts geht verloren: Filterfeld, `Sort by`, Bildlauf freigegeben; `Sort by` bleibt auf der gewaehlten Richtung; getippter Text bleibt und wirkt spaeter. *(nimmt die `Sort by`-Zusage aus AK-199 auf)* |
| **AK-214** | Zeile 3 traegt woertlich `Working out what each relic is worth with <slot> empty` und **nichts sonst** — keine Zaehlung, kein Filter-, Favoriten- oder Rechtsklick-Hinweis; nicht hoeher gezeichnet als die fertige Fassung (gemessen, mit Umgebung). *(ersetzt AK-200)* |
| **AK-215** | **Ausserhalb** des Rollbereichs aendert sich kein Widgetbestand (kein Balken, kein Spinner, keine Schwelle, kein Timer, nichts Gesperrtes); **innerhalb** gibt es genau **einen** Wechsel: die Wartezeile weicht den Karten. Ersetzt AK-09/AK-10 fuer den Picker. *(ersetzt AK-202)* |
| **AK-216** | **Die Groesse steht beim ersten Anstrich**, gemessen an den nicht gezeigten Karten in der beraterfreien Ordnung; `width()`/`height()` ueber den Wechsel identisch, `_sized` einmal. **Messauflage:** `wanted_height` zweimal messen (heutiger Weg gegen Wartezustand-Weg), beide Zahlen mit Umgebung nennen (L-009); **jede Differenz ausser 0 px ist ein Befund und kommt zu mir zurueck.** *(ersetzt die Groessenhaelfte von AK-203)* |
| **AK-217** | Fokus bleibt, wo er ist, springt nicht auf eine Karte; Bildlauf am Anfang; fuer jeden spaeteren Neubau gilt AK-52 unveraendert. *(ersetzt die zweite Haelfte von AK-203)* |
| **AK-218** | **Die Leere ist nie das letzte Wort:** jede Frage endet in `ready`, `failed` oder `stopped`, und **jeder der drei fuellt das Raster**; bei `stopped` ist `<reason>` = `the search was stopped`. Ein Ausgang, der leer laesst, ist ein Fehler. *(neu)* |
| **AK-219** | Zwei Zeichen statt drei: `—` und `no change`; **keine im Rollbereich stehende Karte traegt je `…` (`PENDING`)**. Die Konstante bleibt als Platzhalter beim Bau der Karte. *(ersetzt AK-209)* |

**Gestrichen aus T-124:** AK-197, AK-198, AK-199, AK-200, AK-202, AK-203,
AK-209 — jede mit Grund und Ersatz in einer Tabelle im Abschnitt (§9).
**Unveraendert weiter in Kraft:** AK-201 (jetzt zusaetzlich **Voraussetzung**
von AK-216, siehe Punkt 4), AK-204, AK-205, AK-206, AK-207 (seine zweite
Zusage entfaellt gegenstandslos — waehrend der Leere gibt es keine Karte zum
Auswaehlen), AK-208 (erweitert durch AK-218), AK-210.

**Nummernkreis geprueft, nicht uebernommen** (dieselbe Falle wie in T-124):
`AK-21[1-9]` und `AK-2[2-9][0-9]` kommen im ganzen Baum nur als Verweise auf
den freien Kreis vor; `docs/state.md` Zeile 11 steht inzwischen richtig auf
**AK ab AK-211**. Nach diesem Lauf ist der naechste freie Kreis **AK-220**;
`docs/state.md` gehoert mir nicht und ist nicht angefasst.

## 3. Was die Entscheidung tatsaechlich kostet — offen benannt

- **Sie beseitigt Bewegung nicht, sie tauscht sie.** Statt einer Umsortierung
  stehender Karten erscheint einmal das ganze Raster. Das ist die ruhigere von
  beiden (aus dem Nichts rutscht nichts unter dem Zeiger weg), aber es ist
  nicht „keine Bewegung". Das steht so im Abschnitt, damit es niemand aus dem
  Wortlaut der Abstimmung anders schliesst.
- **Die tragende Begruendung von Fassung 2 faellt.** T-124 §7 konnte sagen:
  „weil kein Element dazukommt und keines verschwindet, braucht es keine
  Zeitschwelle". Das gilt jetzt nicht mehr — im billigsten gemessenen Slot
  (32,3 ms, S11-C) ist die Wartezeile nur ganz kurz zu sehen. **Ohne Wanduhr
  ist das nicht zu beheben**, und eine Wanduhr ist ausgeschlossen (Auftrag,
  AK-215). Gemildert, nicht geheilt: stillstes vorhandenes Token, genau an der
  Stelle der ersten Karte, ohne Animation. Ich melde das als bewusst
  getragenen Preis, nicht als offene Frage — der App Designer hat „der Dialog
  wirkt kurz leer" ausdruecklich mitentschieden.
- **Zwei der drei angekuendigten Kosten treten ein** (keine Namen, keine
  Filtertreffer), **die dritte nicht** (die Dialoggroesse steht sofort).

## 4. Ein Befund am heutigen Stand, der jetzt haerter wiegt

`_chrome_height()` ueberspringt Widgets, die nicht sichtbar sind
(`isVisibleTo`), und der heutige Stand versteckt `findings` **und** `caveats`,
solange keine Rangfolge vorliegt (`_say_what_was_left_out`). **Damit misst
sich der Dialog beim ersten Anstrich zu klein, wenn AK-201 nicht gebaut
wird.** AK-201 war in T-124 eine Lesbarkeitszusage (AK-50 ab dem ersten
Anstrich); unter dieser Entscheidung ist sie zusaetzlich die Voraussetzung
dafuer, dass AK-216 ueberhaupt erfuellbar ist. Der `developer` muss beide in
demselben Schritt bauen.

## 5. Meldungen an den `director` — `ARCHITECTURE.md` habe ich nicht angefasst

**Kein Widerspruch zu AD-028 oder Nachtrag IX gefunden.** Drei Punkte
beruehren sie trotzdem und gehoeren an den `architect`:

1. **W2 ist in seiner heutigen Fassung nicht mehr baubar.** AD-028 formuliert
   ihn woertlich als *„jede Karte traegt `PENDING` in beiden Wertzeilen, und
   der Dialog steht"* (`ARCHITECTURE.md` Zeile 4168). Unter dieser
   Entscheidung gibt es im ersten Anstrich **keine Karte**; ein Test, der auf
   `PENDING` prueft, prueft einen Zustand, den es nicht gibt — er waere gruen,
   ohne etwas zu belegen (L-008b). **Ersatzfassung liegt fertig vor: AK-212.**
   Auch W5 (IX-4) nennt `PENDING` (*„trug zu keinem Zeitpunkt `PENDING`"*);
   der Satz bleibt wahr, wird aber gegenstandslos — die tragende Aussage von
   W5 ist die Zaehlung der Rasterbauten, und die haelt unveraendert.
2. **IX-1 Entscheidung C wird von einer Ersparnis zu einer Voraussetzung.**
   Beantwortet der Controller eine bereits bekannte Frage nicht im selben
   Aufruf, wird der Wartezustand auch beim Cache-Treffer betreten — bei
   gemessenen 30 % Trefferquote ueber Dialoggrenzen (S11-F) blitzte dann bei
   rund jeder dritten Oeffnung das ganze leere Raster auf. Unter „Karten
   sofort" waere das ein Zahlenwechsel gewesen. **Wer C zurueckbaut, bricht
   AK-211/AK-215** — das gehoert in AD-028 vermerkt, nicht nur hier.
3. **Es gibt keine zugesicherte Schranke gegen einen vierten Ausgang.** Der
   Klassen-Docstring von `AdvisorController` sagt „genau eines von `ready`,
   `failed`, `stopped`". Unter dieser Entscheidung haengt daran nicht mehr nur
   die Vollstaendigkeit der Zahlen, sondern die Benutzbarkeit des Dialogs:
   eine Frage, die in keinem der drei endet, laesst den Picker dauerhaft leer,
   und der Spieler kann kein Relikt mehr waehlen. **Frage an den `architect`:
   ist diese Zusage irgendwo bewacht, oder ist sie nur ein Docstring?** Mit
   Mitteln der Oberflaeche ist der Fall nur ueber eine Wanduhr zu behandeln,
   und die ist ausgeschlossen. Ich habe ihn deshalb ausdruecklich aus dem
   Geltungsbereich der Vorgabe genommen (§10).

**Weiterhin offen aus T-124, hier nur, damit es nicht verlorengeht:** der
Picker zeigt den AK-49-Satz ueber die **Spieldateien** auch dann, wenn der
wirkliche Grund „es wurde kein Spielstand gelesen" ist (`asking_from` gibt
`None`, `_say_what_they_are_worth` bildet das auf `NO_FIGURES_AT_ALL` ab).
A7-Bruch, aelter als AD-028, **nicht** von AK-208 oder AK-218 erledigt.

## 6. Offene Frage an den App Designer

- **F-R (`Sort by` = `Name`: die einzige Oeffnung, bei der nichts umsortiert
  wuerde).** **Keine Wiedervorlage von F-P** — die Entscheidung ist umgesetzt.
  Steht `Sort by` auf `Name`, ist die Kartenordnung schon die endgueltige; die
  Antwort wuerde nur Zahlen und Chips in stehende Karten setzen, umsortiert
  wuerde nichts. Diese Vorgabe laesst das Raster **trotzdem** leer, damit der
  Picker **eine** Art hat, sich zu oeffnen, statt zweier, deren Unterschied
  der Spieler nicht erklaeren kann. **Empfehlung: so lassen.** Wer haeufig in
  Namensordnung sucht und nie Zahlen braucht, wartet dafuer bei jeder
  Oeffnung; wenn das stoert, ist es eine Zeile in AK-212.

## 7. Methode und Grenzen dieses Laufs

**Kein laufendes Fenster, kein Bildnachweis, keine eigene Messung.** Der
Auftrag ist Spec-Modus, und ein zweiter Start waere nach `singleinstance`
ohnehin folgenlos gewesen (parallel laeuft T-128 im selben Baum). **Ich habe
nichts gestartet, also auch keine Datenverzeichnisse umgelenkt und keinen
Port belegt** — es gibt nichts wegzuraeumen. Jede Aussage ueber den Bestand
ist am Quelltext belegt und im Abschnitt als **(Quelltext)** gekennzeichnet;
jede Zahl ist zitiert (S11-C, S11-F) und traegt ihre Herkunft.

**Zwei Zahlen im Abschnitt stammen von mir und sind Zeichenzaehlungen, keine
Pixelzusagen** (T-084: `QT_QPA_PLATFORM=offscreen` liefert auf dieser
Maschine keine brauchbare Textbreite): Wartefassung von Zeile 3 **53 Zeichen**
gegen die fertige Fassung **103 Zeichen**, beide mit `Slot 3` eingesetzt. Der
Schluss daraus ist ein **Rang** („die kuerzere bricht nicht, wo die laengere
es nicht tut"), keine Sichtbarkeitszusage; die Messung selbst verlangt AK-214
am laufenden Fenster, mit Umgebung.
