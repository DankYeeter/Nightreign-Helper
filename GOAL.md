# GOAL — Nightreign Helper

Status: FREIGEGEBEN durch den Nutzer am 2026-09-01
Erstellt: 2026-09-01

## Ziel

Nightreign Helper ist ein Windows-Desktop-Werkzeug, das ausschliesslich aus der
eigenen Spielinstallation liest und dem Spieler beim Planen von Relikt-Builds
hilft. In diesem Vorhaben kommen zwei Dinge dazu: ein vollstaendiger Audit des
bestehenden Programms (Korrektheit, Sicherheit, Struktur, Bedienbarkeit,
Releasefaehigkeit), und ein **Build-Berater**, der aus den Relikten, die der
Spieler tatsaechlich besitzt, algorithmisch Vorschlaege errechnet — etwa
"so maximierst du Schaden" oder "so minimierst du erlittenen Schaden".

Die Rechnung laeuft im Hintergrund; der Spieler sieht nur das Ergebnis und
eine kurze Begruendung.

## Abnahmekriterien

- **A1** Ein schriftlicher Audit-Bericht liegt vor, der Korrektheit,
  Sicherheit, Architektur und Bedienbarkeit abdeckt, mit priorisierten
  Befunden. Jeder Befund hat Status (offen / behoben / zurueckgestellt).
- **A2** Alle Befunde der Prioritaet "kritisch" und "hoch" sind behoben oder
  vom Nutzer ausdruecklich zurueckgestellt.
- **A3** Der Build-Berater liefert fuer jeden Nightfarer und jedes bekannte
  Kelch-Layout mindestens zwei benannte Zielrichtungen (Schaden maximieren,
  erlittenen Schaden minimieren) und schlaegt je Slot ein konkretes Relikt
  aus dem Besitz des Spielers vor.
- **A4** Die Vorschlaege respektieren die bestehenden Regeln des Programms:
  Slot-Farben des Kelchs, Stacking-Regeln (nicht stapelbare Effekte werden
  nicht doppelt gezaehlt), Deep-of-Night-Kennzeichnung.
- **A5** Jeder Vorschlag nennt eine nachvollziehbare Begruendung in
  Nutzersprache (welche Effekte den Ausschlag gaben).
- **A6** Die Berechnung blockiert die Oberflaeche nicht: sie laeuft im
  Hintergrund, das Fenster bleibt bedienbar, und bei grossen Relikt-Bestaenden
  bleibt die Antwortzeit im gemessenen Budget — eine **Slot-Frage des Beraters
  ist im Median unter 500 ms** beantwortet, ein **Gesamtlauf (`Optimize`) unter
  6 s**, und **keine Beraterrechnung haelt den Hauptthread laenger als 50 ms
  an**. Messfall: 309 Relikte, 110 gespeicherte Builds, `Wylder's Chalice` mit
  Deep of Night, sechs freie Slots, Zielgeraet und Messumgebung nach
  `docs/perf/baselines.md`.
  *(Die drei Zahlen gesetzt vom `performance-tuner` in S11/T-118, uebernommen
  am 08.09.2026, freigegeben durch Nutzer. Sie schliessen QA-203.)*
- **A7** Wo die Spieldateien eine Bewertung nicht hergeben, sagt das Programm
  das, statt zu raten — die bestehende Hausregel gilt auch fuer den Berater.
- **A8** Alle Texte in der Oberflaeche sind Englisch (bestehende Projektregel).
- **A9** Ein `qa-engineer`-Durchlauf bestaetigt A3 bis A8 gegen ein gebautes
  Artefakt, nicht nur gegen den Quellstand.

## Nicht-Ziele

- Kein Auslesen oder Schreiben in laufende Spielprozesse. Der Save bleibt
  read-only.
- Kein Netzwerkzugriff, keine Wiki-Daten, keine Telemetrie.
- Keine Optimalitaetsgarantie: der Berater ist ein Heuristik-Ratgeber, kein
  Loeser mit Beweis.
- Keine Mehrsprachigkeit.
- Kein Umbau auf ein anderes UI-Framework in diesem Vorhaben.

## Rahmen

- Zielsystem: Windows 10/11, Python 3.11+, PySide6/Qt, PyInstaller-Artefakt.
  (Korrektur 2026-09-01: der Entwurf nannte faelschlich Tkinter.)
- Repo: github.com/DankYeeter/Nightreign-Helper (public), `main` ist geschuetzt
  — jede Aenderung geht ueber einen Pull Request.
- Arbeitskopie: C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper
- Datenquelle: die Spielinstallation des Nutzers. NIGHTREIGN ist auf diesem
  Rechner installiert (Nutzer bestaetigt 2026-09-01) — Tests gegen echte
  Spieldaten sind moeglich und werden verlangt.

## Praezisierungen des Zielbilds (Nutzer, 2026-09-02)

Vom Nutzer entschieden; das Ziel selbst bleibt unveraendert. Grund: der
Build-Berater war seit Zyklus 2 durch vier offene UI-Fragen blockiert.

- **F1 — Slots festhalten: JA.** Der Spieler kann einzelne Slots festhalten,
  und der Berater optimiert nur den Rest. Begruendung des Nutzers: "Ich will
  immer vom aktuellen Stand aus optimieren koennen" — etwa um ein bestimmtes
  Relikt herum bauen, auch wenn dieses Relikt fuer sich genommen nicht optimal
  ist.
  **Folge fuer A3:** Ein festgehaltener Slot ist eine **Randbedingung der
  Suche**, kein Startwert. "Optimiere um dieses Relikt herum" ist ein anderes
  Suchproblem als "optimiere frei" — das beruehrt AD-002 und die Beam-Suche
  und geht vor dem UI-Entwurf an den `architect`.
- **F2 — der Nutzer hat die Fragestellung verworfen, und das ist die
  groesste Aenderung am Zielbild.** Er will **keine** Mechanik "Vorschlag
  erzeugen, dann anwenden". Woertlich: *"Ich will im Relikte-Auswahlfenster
  Vorschlaege haben. Diese Vorschlaege sollen immer schon die Berechnung
  machen vom aktuellen Build aus. Wenn ich 2 gewisse Relikte haben will, soll
  es mir die naechsten basierend auf denen und ihren Benefits und Curses schon
  anzeigen. Z.B. macht ein +Staerke weniger viel aus, wenn ich schon sehr viel
  Staerke habe, weil der Schaden dann weniger stark steigt."*

  **Folge fuer A3 und A5:** Der Hauptweg des Beraters ist die **Bewertung je
  Kandidat im Relikt-Picker**, nicht ein Gesamtvorschlag. Der Wert eines
  Kandidaten ist sein **Grenzbeitrag** gegenueber dem aktuellen Build —
  `compute(Grundzustand + Kandidat) - compute(Grundzustand)`. Der abnehmende
  Ertrag, nach dem der Nutzer fragt, faellt daraus **von selbst** heraus, weil
  die Formel des Spiels ihn hergibt; es braucht keine zweite Rechnung und
  keine erfundenen Gewichte. Der `architect` hat diesen Lauf bereits als
  Nebenertrag bemessen (alle anderen Slots gehalten, ~0,28 s) — er wird jetzt
  der Hauptweg. Der "Optimize"-Button ueber alle freien Slots bleibt, ist aber
  moeglicherweise nur eine zweite Ansicht derselben Rechnung.

  **Offenes Risiko, ausdruecklich benannt:** `compute()` ist nicht gegen das
  laufende Spiel verifiziert. **QA-018** ist genau dieser Verdacht (Waffen-Tab
  203,4 gegen Detailtafel 244,1 fuer dieselbe Waffe). Die Vorschlaege koennen
  in der richtigen Reihenfolge stehen und trotzdem falsche Zahlen zeigen. Das
  kann nur eine Pruefung gegen das laufende Spiel schliessen — durch den
  Nutzer.

- **OF-12 — Haltezustand: gehoert zum Gefaess.** Der Nutzer hat eine dritte
  Option gewaehlt, die weder "verfaellt" noch "wandert mit" war. Woertlich:
  *"Die Relikte selbst verfallen beim Wechsel, wenn man zurueck auf das
  Gefaess oder den Nightfarer springt soll es aber noch da sein. Also
  persistent in dem Gefaess selbst, sonst flexibel."* Gefaess wechseln blendet
  den Haltezustand aus, zurueckwechseln bringt ihn wieder. Das widerspricht
  der urspruenglichen Anweisung des `architect` ("Haltezustand nicht
  persistieren") und wird dort nachgezogen.

- **OF-13 — zielfremde Fluechte: nennen, nicht abwerten.** Ein Relikt wird
  nach seinem Beitrag zur gewaehlten Zielrichtung gerankt, der Fluch aber
  sichtbar ausgewiesen. Eine Abwertung braeuchte eine Umrechnung zwischen
  Schaden und Ueberleben, die die Spieldateien nicht hergeben — sie waere
  erfunden und verstiesse gegen A7.
- **F3 — Fluechte mitbewerten: JA**, und im Ergebnis sichtbar ausweisen.
  Begruendung des Nutzers: "Falls meine negativen auf Relikten meine Benefits
  vernichten, muss ich das wissen."
  **Folge fuer A5:** Die Begruendung in Nutzersprache nennt nicht nur, welche
  Effekte den Ausschlag gaben, sondern auch, welche Negativa gegengerechnet
  wurden.
- **F4 — Name und Ort: Button "Optimize".** Der Nutzer schlaegt Vorschlaege
  je Slot im Relikt-Picker vor und ist bei der Platzierung flexibel.
  Director-Anmerkung fuer die Spec: Vorschlaege im Picker beantworten "was
  passt in **diesen** Slot", ein Button am Build beantwortet "was ist
  insgesamt das Beste" — zwei verschiedene Fragen. Der `ui-ux-designer`
  entscheidet das im Spec-Modus, mit dem Vorschlag des Nutzers als
  Ausgangspunkt, nicht als Vorgabe.

## Weitere Nutzerentscheidungen (2026-09-02)

- **Die eigene Spielinstallation gilt als vertrauenswuerdig.** SEC-015 bis
  SEC-018 auf Niedrig, SEC-019 von Hoch auf Mittel — kein Release-Blocker.
  Ein heruntergeladenes Save bleibt eine scharfe Vertrauensgrenze.
- **C-002 (`nightlords.png`) wird ignoriert.** Ausdruecklicher Entscheid des
  Nutzers; die Frage wird nicht erneut vorgelegt. Der Befund bleibt in
  `docs/legal/` dokumentiert, sperrt aber nichts mehr.
- **PR #16** wird hochgeladen, sobald die jetzigen Ziele erreicht sind;
  danach ist der PR-Stand die Arbeitsgrundlage.

- **OF-15 — Haltezustand ueberlebt keinen Programmneustart** (Nutzer,
  2026-09-02). Er lebt am `Planner`, gebunden an (Held, Gefaess, Deep):
  Gefaess wechseln und zurueck traegt, ein Neustart faengt frei an. Damit
  entsteht **kein neuer persistenter Zustand** — nach drei Datenverlusten im
  QSettings-Schluesselraum (Zyklus 4 und 5) ist das die tragende Begruendung,
  nicht die Bequemlichkeit. Ein Halt verweist ausserdem auf einen Handle, und
  Handles werden beim Einschmelzen neu vergeben; ein ueber den Neustart
  geretteter Halt waere genau der Fall, gegen den AD-013 gebaut ist.



## Erweiterung des Zielbilds (Nutzer, 2026-09-05)

**Grund:** Der Nutzer hat den Audit auf die Inhalte der Tabs ausgedehnt.
Woertlich: *"mach einen audit aller tabs ausser dem ersten. der erste passt.
aber die effekte, waffen, world events etc.. alles. was macht dort sinn?
verwende den power-user und den QA tester dafuer. Erst wenn alles was da
steht qualitativ hochwertig, verstaendlich fuer den auto-normal-verbraucher/
gamer, schoen formattiert und designed ist ist die aufgabe fertig."*

**Geltungsbereich: sechs Tabs.** `Effects & chances`, `Weapons & spells`,
`Nightlords`, `Deep of Night`, `Red variants`, `World Events`.
**`Build planner` ist ausdruecklich ausgenommen** ("der erste passt").

- **A10 — Jeder dieser Tabs beantwortet eine benennbare Spielerfrage**, und
  ein Spieler kann sie am Tab selbst ablesen, ohne sie erraten zu muessen.
  Ein Abschnitt, der keine Frage beantwortet, wird zur Streichung
  **vorgeschlagen** — die Entscheidung darueber trifft der App Designer,
  nicht das Team.
- **A11 — Ein nicht-technischer Spieler erreicht auf jedem Tab sein Ziel
  ohne fremde Hilfe.** Nachweis: `power-user`-Berichte, in denen kein
  "ich habe nicht verstanden, was das bedeutet" und kein "ich habe geraten"
  mehr steht. Das ist das haerteste der neuen Kriterien und das einzige,
  das nicht am Code messbar ist.
- **A12 — Jede Zahl und jede Beschriftung auf diesen Tabs nennt ihre
  Einheit und ihren Geltungsbereich.** Das ist A7, ausgedehnt von der
  Rechnung auf die Anzeige: keine Zahl ohne Bezugsgroesse, keine
  Zusicherung ohne die Angabe, was sie **nicht** deckt.
- **A13 — Die sechs Tabs sind unter sich gestalterisch konsistent** und in
  sich fehlerfrei: gleiche Typografie, Abstaende, Farbrollen und
  Spaltenausrichtung; nichts abgeschnitten, kein Wortumbruch mitten im
  Begriff, keine waagerechte Bildlaufleiste am Standardmass. Nachweis am
  **laufenden Fenster** mit Screenshots, nicht am Code.
- **A14 — Der `qa-engineer` bestaetigt A10 bis A13 je Tab einzeln.** Eine
  Sammelaussage ueber "die Tabs" zaehlt nicht.

**Nicht-Ziel, ausdruecklich:** neue Funktionen auf diesen Tabs. Der Auftrag
ist "was dort steht, soll gut sein" — nicht "es soll mehr dort stehen". Neue
Inhalte gehen ueber den `product-strategist` und die Freigabe des Nutzers.

**Verhaeltnis zu A9:** Der `power-user`-Lauf fuer A11 startet die
Entwicklungsfassung. Der Lauf gegen ein **gebautes Artefakt** (A9) bleibt
davon unberuehrt in P9 stehen — er beantwortet eine andere Frage
(Installation, Erststart, Paketierung).

---

## Nachtrag 06.09.2026 — Erstinstallation (entschieden durch den Nutzer)

**Grund:** Findet die automatische Suche den Spielordner oder den Spielstand
nicht, endet der Erststart heute in einer Fehlermeldung — der Nutzer kann den
Pfad **nicht von Hand angeben**. Damit ist die Installation fuer jeden mit
einem ungewoehnlichen Speicherort eine Sackgasse. Der Nutzer verlangt einen
Erststart, der "mehr oder weniger seamless" ist.

- **A15 — Der Erststart fuehrt jeden Nutzer bis zu lesbaren Daten, ohne
  fremde Hilfe.** Findet die Automatik den Spielordner oder den Spielstand,
  merkt der Nutzer nichts — der Ablauf bleibt wie heute. Findet sie ihn
  nicht, erscheint **statt der Fehlermeldung** ein Auswahldialog; der
  gewaehlte Pfad wird geprueft, behalten und beim naechsten Start wieder
  benutzt. Nachweis: ein `power-user`-Lauf auf einem **gebauten Artefakt**,
  bei dem die Automatik nachweislich ins Leere laeuft, und der Nutzer
  trotzdem ohne Abbruch bis zu angezeigten Zahlen kommt.

**Zwei Festlegungen des Directors dazu:** Aus dem Spielordner wird **nichts
verschoben und nichts entfernt** — das Programm merkt sich den Pfad und baut
daraus wie bisher seinen Datenabzug unter `%LOCALAPPDATA%\NightreignHelper`.
Und der Zielort dieses Abzugs bleibt fest; er wird nicht zur dritten
Einstellung.

**Umfang:** Spielordner **und** Spielstand. Der Spielstand wird heute genauso
blind gesucht — bei zwei Steam-Konten oder verschobenem Speicherort steht der
Nutzer vor demselben Problem.

**Verhaeltnis zu A9:** A15 ist der Inhalt, A9 die Pruefumgebung. Beide werden
in P9 zusammen abgenommen, im selben `clean-room`- und `power-user`-Durchgang.

---

## Nachtrag 07.09.2026 — zwei Praezisierungen des Beraters (entschieden durch den Nutzer)

**Grund:** Beim Durchsprechen des gebauten Beraters hat der Nutzer zwei
Annahmen widerlegt, auf denen die Rangfolge bisher stand. Das Ziel selbst
bleibt unveraendert; A3 und A5 bekommen einen praeziseren Gegenstand.

### A16 — Der Berater zeigt den schlechtesten **und** den besten Fall

**Was der Nutzer entschieden hat**, woertlich: *"beim optimieren / berater
will ich zwischen worst-case und best-case unterscheiden koennen. dann kann
ich auf nummer sicher gehen oder die risiko variante waehlen."*

**Anlass.** Ein Fluch wird heute wie jeder andere Effekt in die Rechnung
gegeben — es gibt keinen Fluch-Malus und keinen Sonderzweig. Ein Fluch **mit
Bedingung** faellt aber wie jeder bedingte Effekt heraus, bis der Spieler die
Bedingung erklaert. Gemessen am Spielstand des Nutzers (07.09.2026, 309
Kopien): **24 Fluch-Ids im Datensatz, alle 24 auf seinen Relikten, davon 7 mit
Bedingung** — darunter `Lower Attack When Below Max HP`,
`Poison Buildup When Below Max HP`, `Rot Buildup When Below Max HP`,
`Near Death Reduces Max HP` und drei rund um Ausweichen und Flaschentrinken.
**Korrektur des Directors, 07.09.2026 (T-092):** Die Zahlen oben zaehlen
**Ids**, nicht Vorkommen — der Director hat sie so gemessen und so
weitergegeben, was sich als "sieben Flueche auf deinen Relikten" liest und
das nicht ist. Nachgezaehlt vom `ui-ux-designer`: **112 Fluchrollen**, davon
**27 konditional auf 23 Kopien**, **142 gezeichnete Fluchzeilen**. Und die
Wirkung ist kleiner als der Director sie dargestellt hat: im schlechtesten
Fall aendern **8 von 309 Kopien** ihre `max_damage`-Zahl und **11** ihre
`min_damage_taken`-Zahl. Das Kriterium bleibt erfuellbar und die Entscheidung
richtig — der Spieler bekommt eine Zahl, auf die er sich verlassen kann —,
aber "greifen im Kampf fast immer" war eine Behauptung ueber die Spielpraxis,
die keine Messung stuetzt.

**Was daraus folgt.** Der Berater bekommt zwei Lesarten derselben Rechnung:

- **Schlechtester Fall** — jede bedingte Fluchwirkung gilt als aktiv, jede
  bedingte Buffwirkung als inaktiv. Die Zahl, auf die man sich verlassen kann.
- **Bester Fall** — umgekehrt. Die Zahl, die erreichbar ist, wenn alles passt.

Beide Lesarten sind **Voreinstellungen fuer die Bedingungen**, keine zweite
Rechnung und keine erfundenen Gewichte: das Feld, mit dem der Spieler eine
Bedingung heute von Hand erklaert, wird dafuer gesetzt. Damit bleibt A7
gewahrt — angenommen wird die **Bedingung**, nie die Zahl.

**Abnahme:** Der Spieler kann im Berater zwischen beiden Lesarten wechseln,
jede Zahl sagt, welche gerade gilt, und die sieben bedingten Flueche seines
Spielstands bewegen im schlechtesten Fall die Rangfolge nachweislich.

**Nicht-Ziel:** Das Statblatt im Build planner bleibt unberuehrt. Die zwei
Lesarten gehoeren dem Berater.

### A17 — "Schaden maximieren" rankt ohne Bezugswaffe

**Was der Nutzer entschieden hat**, woertlich: *"wir optimieren die stats und
passiven am besten weil nur die fix sind. waffen und deren buffs sind alle in
der runde RNG-basiert."*

**Anlass.** `_max_damage` rankt heute nach dem, was die **Bezugswaffe** trifft
(`blurb`: "Ranks by what your reference armament hits for."). Sind Waffen und
ihre Buffs pro Runde ausgewuerfelt, optimiert das auf eine Waffe, die der
Spieler in der Runde nicht hat.

**Was daraus folgt.** Die Zielrichtung rankt in der Voreinstellung **ohne**
Bezugswaffe, also nach Angriffsmultiplikatoren, Attributen und Passiven — dem,
was zwischen Runden fest bleibt. Der Weg dafuer ist gebaut: `_max_damage`
behandelt `ctx.reference is None` bereits und sagt den zugehoerigen Satz
(`_NO_ARMAMENT`, `_NO_ARMAMENT_NOTE`).

**Abnahme:** Die Rangfolge einer Zielrichtung aendert sich nicht, wenn eine
andere Waffe gefuehrt wird; die Zahl nennt ihren Geltungsbereich (A12).

**Offen und ausdruecklich nicht mitentschieden:** ob die Zeile "es haengt an
den Armaturen, die du fuehrst" (Fuellung (c), 38 Zeilen auf dem Spielstand
des Nutzers) unter dieser Annahme noch nuetzlich ist. Sie ist wahr, aber sie
raet zu etwas, das in der Runde nicht in der Hand des Spielers liegt. Gehoert
in den S10-Review.
