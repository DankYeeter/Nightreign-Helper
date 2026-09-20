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
  *(Nachtrag 13.09.2026, Nutzerfreigabe: der Spielstand hat heute **312**
  Relikte, gezaehlt in T-222/T-224; 309 bleibt die Zahl des Messfalls vom
  07.09. Nachtrag 14.09.2026, Nutzerfreigabe: **314** Kopien, gezaehlt in
  T-229 und T-239.)*
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
*(Nachtrag 13.09.2026, Nutzerfreigabe: am Spielstand mit **312** Kopien hat
T-224 gemessen: **11 Kopien** bewegen `min_damage_taken` im schlechtesten Fall,
alle mit Fluch-Id; die 8/309-Zahl fuer `max_damage` stammt vom 07.09.)*

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

---

## Nachtrag 14.09.2026 — Lesarten weg, Ausschlussfilter dazu (entschieden durch den Nutzer)

**Was der Nutzer entschieden hat**, woertlich (20:35, auf die Frage nach der
Benennung der Lesarten): *"only optimise for maximum dmg and maximum defense.
add the option that I can add 'don't include' filters to remove them from the
recommendations altogether."* Nachfrage 20:44: der **Worst/Best-Umschalter
faellt**, die drei Richtungen bleiben; ausgeschlossen werden **einzelne
Effekte**.

### A18 — Eine Rechnung statt zwei Lesarten; Effekte lassen sich ausschliessen

- **A16 ist ersetzt.** Der Berater hat keinen Umschalter Worst case / Best
  case mehr. Bedingte Effekte gehen in die Rechnung ein wie unbedingte,
  sofern der Spieler sie nicht ausgeschlossen hat; die Begruendung (A5)
  nennt bei jedem gezaehlten bedingten Effekt seine Bedingung.
- **Ausschlussfilter:** Der Spieler kann einzelne Effekte (z. B. `at low
  HP`-Varianten) als *don't include* markieren. Ein markierter Effekt zaehlt
  in keinem Vorschlag und in keiner Rangfolge des Beraters, egal welches
  Relikt ihn traegt; das Relikt selbst bleibt waehlbar, wenn seine uebrigen
  Effekte tragen. Die Markierung wird gespeichert und beim naechsten Start
  wieder angewandt.
- **Nachweis:** `qa-engineer` bestaetigt an einem Spielstand mit mindestens
  einem markierten Effekt, dass kein Vorschlag ihn zaehlt, und dass die
  Rangfolge ohne Markierung der heutigen Best-case-Rangfolge entspricht.
- **Nicht-Ziel:** Sperrliste fuer ganze Relikte, Bedingungsklassen-Schalter.

*Folgen fuer die Spec: AK-268 (Lesarten) und AK-273 (Benennung) entfallen;
AK-194/AK-05 (Leistenbreite) neu messen. Folgen fuer die Architektur:
AD-035 (zwei Lesarten) durch eine Ausschlussmenge im `AdvisorRequest`
ersetzen — der `architect` entscheidet den Schnitt.*

### A19 — Pflicht-Effekt: "mit Effekt XYZ die beste Konstellation" (Nutzer, 14.09.2026 20:48)

**Woertlich:** *"zusaetzlich zum weg filtern, auch eine option 'buff
auswaehlen'. und dann muss das programm rechnen welche konstellation mit
effekt XYZ die beste waere."*

- Der Spieler kann einen oder mehrere Effekte als **must include** markieren.
  Der Berater liefert dann nur Konstellationen, in denen mindestens ein
  gewaehltes Relikt jeden markierten Effekt traegt, und optimiert den Rest
  nach der gewaehlten Richtung. Gibt es im Besitz keine passende Kopie fuer
  die freien Slots, sagt er das (A7) statt den Filter still fallen zu lassen.
- Ausschluss (A18) und Pflicht (A19) sind zwei Listen mit derselben Bedienung
  und derselben Persistenz.
- **Nachweis:** `qa-engineer` bestaetigt an einem Spielstand, dass jeder
  Vorschlag den Pflicht-Effekt enthaelt und die Rangfolge unter den
  passenden Konstellationen der freien Optimierung entspricht.
- **Klarstellung zu Debuffs (Nutzerfrage 20:48):** Negativa innerhalb eines
  Effekts (`Reduced Faith`) gehen heute in die Attributsumme ein; Fluechte
  werden nach F3/OF-13 gegengerechnet und genannt, zielfremde Fluechte nur
  genannt (A7). Daran aendert A18/A19 nichts.

### A20 — Zweihand-Angriffskraft (Nutzer, 14.09.2026 20:58: "dann brauchen wir 2haendig drinnen. hinzufuegen.")

- Jede Angriffskraft-Anzeige (Kachel, Werteblatt, Arsenal, Berater-Zeile)
  kennt den Zweihandwert neben dem Einhandwert, wo die Waffe zweihaendig
  gefuehrt werden kann; Effekte mit Bedingung *when Two-Handing*
  (`8300000-2`, `7006000-1`) rechnen auf den Zweihandwert.
- **Messpunkte (Spiel, Lv15, keine Relikte):** Raider Great Stars uncommon
  188 → **216** zweihaendig; Wylder Great Stars 147 → **151**. Die Regel,
  die beide trifft, ist die des Programms; trifft keine, sagt es das (A7).
- Welche Richtung die Rangfolge des Beraters nutzt (Einhand, Zweihand,
  Maximum), entscheidet der Nutzer nach dem Entwurf des `architect`.
- Ersetzt QA-259 (zurueckgestellt) durch ein Ziel.

*Nachtraege 14.09.2026 21:15 (Nutzer): **OF-37** — bedingte Fluechte zaehlen
in der Grundlinie wie alle bedingten Effekte, solange sie nicht
ausgeschlossen sind. **OF-41/A20** — welche Hand der Berater rankt, folgt
einem neuen **Umschalter 1H/2H an der Waffenausruestung**; die Rangfolge
nutzt die dort gewaehlte Hand. Die vier Zweihand-Messzellen (Wylder, Raider,
Guardian, Duchess: Startwaffe Lv15, 1H und 2H) liefert der Nutzer.*

*A20-Messzellen (Nutzer, 14.09.2026 21:22; Lv15, Startwaffe, keine Relikte,
Einhand → Zweihand): Duchess 72 → 74 · Wylder 122 → 125 · Raider 158 → 180 ·
Guardian 107 → 110. Dazu Great Stars uncommon: Raider 188 → 216, Wylder
147 → 151.*

*A20-Messzellen II (Nutzer, 15.09.2026 08:58/09:14; Lv15, Startwaffe bzw.
genannte Waffe uncommon, keine Relikte, Einhand → Zweihand): Ironeye 66 → 66
(Bogen, kein 2H) · Recluse 135 → 135 (Stab, kein 2H) · Executor 94 → 97 ·
Revenant Siegel 159 → 159 (kein 2H), Revenant mit Revenant's Cursed Claws
88 → **68** (Korrektur 15.09.: Revenant selbst, nicht Wylder) · Scholar 63 → 64 · Undertaker 91 → 93. **Paarwaffen:** Wylder
Ornamental Straight Sword 161 → 124 · Wylder Twinblade 108 → 54 · Wylder
Caestus 93 → 71 · Wylder Hookclaws 80 → 62 · Raider Twinblade 99 → 49 ·
Revenant Hookclaws 59 → 46. Nutzer: Paarwaffen zaehlen zweihaendig als zwei
Waffen; der Schadens-Split je Typ soll wie in Elden Ring aus den Daten
kommen. AN-5 geaendert: Weapons-Tab zeigt auch die Typzeilen beidhaendig;
AN-6 bestaetigt (leere Builds speichern keine Hand).*

### A21 — Effektfilter als eigenes Fenster (Nutzer, 15.09.2026 12:25)

**Woertlich:** *"mir gefaellt nicht wie es eingebunden ist. liefer ein Filter
Symbol und darin dann Favourite und Avoid marker. eine liste nur von
effekten die ich habe. nicht gruppiert pro relikt oder so. curses ebenfalls"*

- In der Berater-Leiste ein **Filter-Symbol**; es oeffnet ein Fenster mit
  **einer flachen Liste aller Effekte und Fluechte, die der Spieler
  besitzt** (je Effekt eine Zeile, nicht je Relikt), jede Zeile mit zwei
  Markern **Favourite** (= Must include, A19) und **Avoid** (= Don't
  include, A18). Suchfeld, Zaehler, Persistenz wie A18/A19.
- Die Begriffe im Programm heissen ab jetzt **Favourite** und **Avoid**
  (Legende, Tooltips, Why-Zeilen, Leiste).
- Nachweis: power-user findet und benutzt beide Marker ohne Hilfe; QA: die
  Liste zaehlt genau die Effekt-/Fluch-Ids der 31x eigenen Kopien.

*Nutzerentscheid 12:30: die Punkte an den Effektzeilen im Picker und im
Why-Dialog **entfallen komplett**; das Filterfenster ist der einzige Weg
(AK-276-278, AK-297 damit gegenstandslos).*

## Nachtrag 17.09.2026 — Attribute rechnen, Familien vermeiden (entschieden durch den Nutzer, 20:13-20:20)

*Anlass: Ingame-Test von 1.13.2 auf Duchess. Bild: Vorschlag "Deep Grand
Tranquil Scene" mit vier Fluchzeilen "Reduced Intelligence and Dexterity:
Dexterity -3 — this figure does not count it." Nutzer: "diese negativen
muessen mit eingerechnet werden." Und: "ich will 'familys' avoiden koennen.
Einzelne davon kann ich mit favourite durchwinken … aber das wuerde
favourite entwaessern."*

### A22 — Attribut-Aenderungen zaehlen in die Schadenszahl (beide Richtungen)

- Ein Effekt oder Fluch, der ein Attribut aendert (Vigor, Mind, Endurance,
  Strength, Dexterity, Intelligence, Faith, Arcane, ±n), wird ueber die
  Skalierung der gewaehlten Waffe in die Angriffskraft gerechnet — Flueche
  senken, Buffs heben die Zahl. Damit ist OF-13 fuer Attribute aufgehoben;
  fuer Attribute gilt sie nicht mehr als "zielfremd". Die Umrechnung stammt
  aus den Spieldaten (Skalierungskurven, wie A20), nicht aus einer
  erfundenen Gewichtung (A7 bleibt).
- Nachweis: Ein Build mit Dex -3 auf einer Dex-skalierenden Waffe zeigt
  eine kleinere Angriffskraft als ohne, und die Why-Zeile nennt den Betrag
  ("Dexterity -3: Attack -X, counted against it"). Ein Messpunkt des
  Nutzers ingame (Startwaffe Lv15, ein Relikt mit Attribut-Fluch) bestaetigt
  die Zahl.

### A23 — Familien vermeiden, Mitglieder ausdruecklich erlauben

- **Familie** = gleicher Effektname ohne Stufe und Variante (z. B.
  "Improved Affinity Attack Power" umfasst +1/+2/+3 und Magic/Fire/
  Lightning/Holy; "Increased Dagger Attack Power" ist eine eigene Familie).
  Den Schluessel legt der `architect` fest, abgeleitet aus dem Namen.
- Das Filterfenster (A21) zeigt je Familie eine Kopfzeile mit **Avoid**.
  Unter einer vermiedenen Familie tragen die Mitglieder ein drittes Kaestchen
  **Allow**: das Mitglied darf in Vorschlaege, muss aber nicht. **Favourite**
  bleibt "muss rein" und wird nicht als Ausnahmemechanik benutzt.
- Nachweis: Duchess, Familie "Increased Attack Power" (o. ae.) vermieden,
  "Increased Dagger Attack Power" und "Increased Attack Power with 3+
  Daggers" auf Allow → Optimize schlaegt nur diese beiden aus der Familie
  vor, ohne sie zu erzwingen.

*Reihenfolge (Nutzer 20:13): Release 1.13.2 zuerst, A22/A23 als 1.14.0 mit
eigener Pruefkette.*

## Nachtrag 19.09.2026 — Unterbosse im Nightlords-Tab (entschieden durch den Nutzer, 12:28-12:40)

*Anlass: Ideensammlung aus Spielersicht bei leerem Backlog. Verworfen vom
Nutzer: Relikt-Ausmisten ("vlt. fehlt einem einfach das passende relikt"),
Nachtfuerst-Vorbereitung ("man weiss vor der runde kaum gegen wen man
kaempft"), Level-Kostentabelle (Kosten je Level sind fest), Build teilen,
Fortschritt aus dem Spielstand. Angenommen: "das zu ergaenzen im
Nightlords Tab und Informationen zu den Unterbossen waere spannend."*

### A24 — Unterbosse mit Kampfwerten im Nightlords-Tab

- **Umfang:** Nachtbosse Tag 1/2 sowie Feldbosse und Evergaol-Bosse. Je
  Boss: Schwaeche und Resistenz, HP und Stance, Beute, und — soweit die
  Dateien es hergeben — unter welchem Nachtfuersten er auftaucht. Alles
  aus den Spieldaten (A7); was nicht belegt ist, steht als solches auf der
  Seite, wie heute beim Bruchwert.
- **Zwei Stufen, Forschung zuerst.** Stufe 1: Evergaol- und Feldbosse
  (Roster aus den Deep-of-Night-Kategorien, Kampfwerte ueber NpcParam,
  Beute ueber die vorhandene Kreaturen-Aufloesung). Stufe 2: Nachtbosse
  Tag 1/2 und die Nachtfuerst-Zuordnung, nur nach Befund.
- **Offen vor der Umsetzung (Explore 19.09.):** kein gelesener Param
  listet Nachtbosse als benannte Menge (Kategorie 120 unbestaetigt);
  die Zuordnung Boss → Nachtfuerst haengt an unbenannten Modifier-Ids der
  Kartenmuster; ungelesene Kandidaten: SmallBaseAndSpot*,
  PlayAreaCreate*, ScenarioPlacementParam. Der eingecheckte Snapshot ist
  aelter als der Extraktor; Proben brauchen einen frischen Abzug.
- Nachweis: Ein Evergaol-Boss (z. B. Fallingstar Beast) waehlbar im
  Nightlords-Tab mit denselben Diagrammen wie ein Nachtfuerst plus HP und
  Beute; ein Nachtboss mit Tag-1/2-Kennung, falls Stufe 2 belegt wird.

*Nachtrag 19.09.2026 15:50 (Nutzer, Fragebogen R-009): "Ziel +
Schadensart-Auswahl"; Skill attack = nur Weapon Arts, Nightfarer-
Faehigkeiten bleiben generell unbeachtet; Start nach T-310/T-311/T-312.*

### A25 — Schadensart im Berater waehlbar (Element, Skill, Zauberschule)

- **Umfang:** "Maximise damage" bekommt eine Auswahl der Schadensart:
  Alle (heutiges Verhalten) / Physical / Magic / Fire / Lightning / Holy /
  Skill attack (Weapon Arts) / Sorceries / Incantations / eine
  Zauberschule (z. B. Bestial). Die heute als `scoped:` geparkten
  Multiplikatoren (Scope 112 Skills, Schulen ueber
  `magicSubCategoryChange`, R-009) zaehlen in die gewaehlte Art; die
  Startwaffen-Relikte (Konversion -30/+33 bis -60/+66, Malus 0,85)
  zaehlen in der Kandidatenwertung, nicht nur in der Anzeige.
- **Nicht Ziel:** echter Zauberschaden (AtkParam/Bullet), Nightfarer-
  Faehigkeiten (`characterSkillAttackRate`), neue Extraktion.
- **Praemisse (Nutzer 19.09.):** Scope 112/111 = Weapon Arts.
- Nachweis (OF-50, Nutzer 19.09. 16:25): Revenant (Startwaffe Cursed Claws,
  71,63 von 88,65 AR Magic) mit Auswahl "Magic" bzw.
  "Bestial" (Schulwahl, Nutzer 19.09. 18:57: Incantations am Slot leer)
  liefert eine andere Reihung als "Alle", und die
  Why-Zeile nennt die Art; Wylder mit beiden Startwaffen-Relikten und
  Auswahl "Skill attack" zaehlt die Konversion in die Schadenszahl.

*Nachtrag 20.09.2026 17:35 (Nutzer, Chat + Fragebogen): "Bestial rankt
Siegel-Spell-Power statt Klauen-AR" und "es muss moeglich sein, auf Zauber,
Incantations, regulaeren Schaden, einen Schadenstyp oder Weapon Arts zu
gehen; bufft ein Schadenstyp eine Weapon Art, muss die Kombination richtig
errechnet werden; komplett abgedeckt". Entschieden: Zauber-Angriffsdaten
extrahieren (AtkParam/Bullet); zwei Felder Womit x Schadensart. Gemessen
20.09.: CharaInitParam `equip_Wep_Left_1` — Revenant Finger Seal 34750000,
Wylder Small Shield 30750000, Guardian Greatshield 32750000; der Extraktor
liest bisher nur `equip_Wep_Right_1`.*

### A26 — Ziel = Womit x Schadensart, mit echten Zauber- und Skill-Zahlen

- **Umfang:** Der Berater fragt zwei Dinge: *Hit with* (Weapon / Weapon
  art / Sorceries / Incantations / eine Schule) und *Damage type* (All /
  Physical / Magic / Fire / Lightning / Holy). Jede Kombination hat eine
  definierte Zahl oder sagt, warum nicht. Zauber-Ziele rechnen mit dem
  Start-Katalysator (Recluse Stab rechts, Revenant Finger Seal links):
  Spell Power x Zauber-Grundwert x Faktoren (Gattung, Schule, Schadensart,
  Charged). Weapon-Art-Ziele rechnen mit der Waffenkunst der Startwaffe
  und ihren Schadensarten. Dazu liest der Extraktor die linke Starthand,
  die Zauber-Angriffsdaten (Schadensart und Grundwert je Zauber) und die
  Skill-Daten der Startwaffen.
- **Nicht Ziel:** Nightfarer-Faehigkeiten (`characterSkillAttackRate`),
  Zauber ausserhalb der Startausruestung als Bezugsobjekt (die Rangfolge
  gilt fuer "eine Incantation dieser Schule", nicht fuer einen bestimmten
  Zauber), Statusaufbau.
- **Praemissen:** Elementraten wirken auf jeden Treffer ihrer Schadensart
  (Waffe, Skill, Zauber) — ER-Mechanik, in Nightreign unvermessen;
  Scope 112/111 = Weapon Arts (Nutzer 19.09.).
- Nachweis (QA-291, Director 20.09. 21:45 nach AD-054 N4): Revenant,
  *Incantations* x *All*: Faith und Improved Incantations steigen, ein
  Bestial-Relikt erst unter der Schulwahl *Bestial*, Klauen-Relikte fallen; Revenant,
  *Bestial* x *Physical*: Improved Physical Attack Power zaehlt, Holy
  nicht; Wylder, *Weapon art* x *Fire* mit Startwaffen-Konversion Fire:
  Skill-Buff x Fire-Buff x Konversion in einer Zahl; Recluse, *Sorceries*
  x *Magic*: Spell Power x Sorcery-Buff x Magic-Buff.

*Nachtrag 20.09.2026 17:40 (Nutzer): "Wenn ich einen Starting Spell
auswaehle, soll Maximise damage direkt auf diesen Spell rechnen."*
Gemeint sind die Relikt-Effekte "Changes compatible armament's sorcery /
incantation to <Zauber> at start of expedition" (10 im Datensatz, Ids
73606xx..73715xx, z. B. 7370900 Beast Claw). Ergaenzung A26: liegt ein
solcher Effekt im Build (gehalten oder vorgeschlagen), rechnet ein Zauber-
Ziel mit genau diesem Zauber (Grundwert, Schadensart, Schule aus den
extrahierten Zauberdaten) statt mit dem Standardzauber des Katalysators;
ohne einen solchen Effekt gilt der Standardzauber des Start-Katalysators.
Nachweis: Revenant mit 7370900 (Beast Claw) unter *Incantations* x *All*
zeigt die Beast-Claw-Zahl, physische Buffs zaehlen, Holy nicht.
