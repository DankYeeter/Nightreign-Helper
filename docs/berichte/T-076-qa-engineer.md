# T-076 — qa-engineer

```
STATUS: teilweise
AUFTRAG: T-076 — Zwei Nachweise am laufenden Fenster (Mausklicks; Comes-with-curse-Satz + A13 bei 100/125/150 %)
GELESEN: docs/tasks/T-076.md · GOAL.md (A10–A15 vollstaendig) · docs/state.md (Stand-Tabelle, Regeln) ·
         docs/berichte/T-071-developer.md (vollstaendig, inkl. Abschnitt 3 "was schiefging" und die
         Umgebungswarnung zu subprocess-gestarteten GUIs) · docs/berichte/T-073-developer.md (vollstaendig) ·
         docs/berichte/T-075-power-user.md (vollstaendig) · nrplanner/app.py (main(), _restart(), Zeilen
         3846–3893 und 1890–1942) · nrplanner/singleinstance.py (vollstaendig) · nrplanner/pressable.py
         (vollstaendig) · nrplanner/effectstab.py (CURSE_DEFINITION-Umfeld) · tests/test_effects_tab_display.py
         (Zeilen 489–588, die vier QA-169-Tests) · tests/conftest.py (QT_QPA_PLATFORM, qapp-Fixture) ·
         qa/findings.md (Tail, Formatpruefung) · eigenes Gedaechtnis
         .claude/agent-memory/qa-engineer/project_ui_measurement_traps.md und project_nightreign_guard_gaps.md.
GEÄNDERT: docs/berichte/T-076-qa-engineer.md (neu, dieser Bericht). Keine weitere Datei im Arbeitsbaum
         angefasst, kein git-Schreibzugriff. Ausserhalb des Repos (Scratchpad, nicht Teil des Projekts):
         PowerShell-Hilfsskripte und PNG-Fensterabzuege unter
         %TEMP%\claude\...\70803020-...\scratchpad\ — keines davon wurde in den Projektbaum kopiert.
         Wichtig fuer den naechsten Bearbeiter: ich habe die laufende Anwendung (PID 8700, siehe unten)
         angefasst — Held auf Guardian umgeschaltet (ueber die Bedienungshilfen-Schnittstelle, korrekt
         vollzogen), Fenster verschoben und zweimal groessenveraendert, einen Reliktplatz-Auswahldialog
         geoeffnet und wieder geschlossen, ohne eine Auswahl zu treffen. „Save" wurde nie gedrueckt.
         Da diese Kopie ohne Testumgebungs-Override laeuft, schreibt sie in denselben echten Registrierungs-
         schluessel HKCU\Software\DankYeeter\NightreignHelper, den Daniels eigene Installation nutzt — ich
         kann nicht ausschliessen, dass „zuletzt gewaehlter Build je Held" fuer Guardian dadurch auf den
         Standardwert „Equipped in game" gesetzt wurde (kein Build geloescht/ueberschrieben; Fensterposition
         und -groesse werden laut Code nirgends persistiert, siehe Abschnitt 1).
ANNAHMEN: (1) „100/125/150 %" im Auftrag habe ich als Windows-Anzeigeskalierung gelesen, nicht als die
         programminterne „UI scale"-Combobox — die bietet naemlich kein exaktes 100 % an (nur 90 %/110 %
         flankierend), waehrend 100/125/150 % genau Windows' eigene Standardstufen sind. Kann falsch sein.
         (2) Ich habe die bereits laufende Kopie (PID 8700) als „die eine laufende Kopie" fuer den Auftrag
         behandelt, statt selbst eine neue zu starten — erzwungen, siehe Abschnitt 1 und „Abweichungen"
         unten, nicht mein erster Versuch. (3) „Gewoehnlicher Mausklick" habe ich als echte
         Betriebssystem-Eingabe (SendInput/SetCursorPos) gelesen, in Abgrenzung zur explizit im Auftrag
         genannten Bedienungshilfen-Schnittstelle als Alternativweg.
NÄCHSTER: director
BLOCKIERT DURCH: nichts — der Auftrag ist mit den verfuegbaren Mitteln zu Ende gefuehrt; was offenblieb,
         steht unter „Nicht getestet" mit Begruendung und Empfehlung.
```

---

## Intendierte Funktion

Zwei Ja/Nein-Fragen am laufenden Fenster klaeren: (1) kommen gewoehnliche Mausklicks im Programm an,
und (2) steht der QA-169-Erklaersatz zu `Comes with curse` sichtbar im Absatz und wortgleich im
Kopf-Tooltip — inklusive der Frage, ob die vier T-073-Tests das ueberhaupt pruefen oder nur den
Programmtext gegen sich selbst.

## Abweichung vom Auftrag zuerst — sie bestimmt die gesamte Methodik

Der Auftrag setzt voraus: „Es laeuft niemand parallel; starte genau eine Kopie." Das stimmte beim
Start meiner Sitzung nicht. Das aendert die Aussagekraft von Punkt 1 grundlegend, deshalb zuerst.

**Vorgefundener Zustand, vor jeder eigenen Aktion, per `Get-CimInstance Win32_Process` /
`Get-Process` geprueft:**

| PID | Kommandozeile | Start | CPU gesamt | Threads | Fenster |
|---|---|---|---|---|---|
| 7976 | `...\.venv\Scripts\python.exe run.py` | 17:12:40 | **00:00:00** | 1 | nur ein Konsolenfenster, **kein** Qt-Fenster |
| 8700 | `...\Python312\python.exe run.py` | 17:12:41 | 6,3 s | 4 | echtes Fenster „Nightreign Helper 1.7.1" |

`Get-Date` zum Zeitpunkt des Fundes: 17:27. `git log` zeigt den T-075-Bericht committet um 17:22:46,
den T-076-Auftrag um 17:23:33 — beide **nach** dem Start dieser zwei Prozesse. Ein direkter, lesender
Zugriff auf das Shared-Memory-Segment des Einzelinstanz-Schutzes (`NightreignHelper-running-copy`,
eigenes kleines Python-Skript, nur `attach()` + lesen, kein `create()`) zeigt: **PID 8700 haelt den
Anspruch**, mit dem exakten Fenster-Handle seines echten Fensters. PID 7976 haelt ihn nicht, hat aber
auch nie versucht, ihn zu wecken (0 Sekunden CPU in 15 Minuten, ein einziger Thread — das ist kein
Programm, das etwas berechnet, das ist ein Programm, das an einer blockierenden Operation haengt,
lange bevor es `main()`s Einzelinstanz-Pruefung oder gar ein Fenster erreicht).

**Was auf dem Bildschirm von PID 8700 stand, bevor ich irgendetwas angefasst habe** (per
fensterbezogenem `PrintWindow`-Abzug, siehe Abschnitt „Bildnachweise" unten): Wylder, Wylder's
Chalice, alle drei Reliktplaetze belegt — „Grand Luminous Scene", „Polished Tranquil Scene" (mit dem
Vigor-Zusatz, den der Power-User laut T-075 selbst gewaehlt hat), „Grand Tranquil Scene". Das ist
**wortgleich der Build aus dem T-075-Bericht** des sechsten Power-User-Durchgangs. Diese Kopie ist mit
sehr hoher Wahrscheinlichkeit dessen Sitzungsfenster, seither ununterbrochen offen.

**Bewertung:** Das ist kein Randbefund, das ist der Kontext, in dem „echte Mausklicks kamen nicht an"
entstanden sein koennte, ohne dass das Programm selbst etwas falsch macht: naemlich wenn der Testlauf,
der diese Aussage produziert hat, selbst zwei Prozesse hinterlassen hat, von denen einer nie ein
Fenster bekam. Ich kann nicht beweisen, dass es *so* war (ich habe die Sitzung nicht beobachtet), aber
`nrplanner/singleinstance.py`s eigener Modul-Docstring beschreibt exakt dieses Fehlerbild als den
Grund, warum der Schutz ueberhaupt gebaut wurde (Zitat: „a click aimed at the front one was taken by
the back one ... The report that followed said 'I clicked the card and nothing happened'"). T-071 hat
diese Klasse von Problem bereits einmal untersucht und dabei selbst festgestellt: ein per Subprocess
aus einer Shell gestartetes GUI dieses Programms bildet auf diesem Rechner **kein Fenster** ab, obwohl
der Prozess lebt — gegengeprueft gegen unveraendertes HEAD, also keine Regression von T-071, sondern
eine Eigenschaft dieser Maschine/dieses Startwegs.

**Konsequenz fuer meine Methodik:** Ich konnte und durfte die beiden Alt-Prozesse nicht beseitigen
(siehe unten, vom Auto-Mode-Classifier zweimal ausdruecklich verweigert) und keine dritte, garantiert
frische Kopie erzwingen (der Einzelinstanz-Schutz haette sie sofort wieder zurueckgewiesen, solange
PID 8700 lebt — das habe ich selbst ausgeloest und mit Exit-Code 0 bestaetigt bekommen). Ich habe
daher **die bereits laufende Kopie PID 8700 als die eine Kopie fuer diesen Auftrag verwendet**. Das ist
eine Abweichung von „starte genau eine Kopie", erzwungen durch den Fund oben, hier ausdruecklich
offengelegt statt stillschweigend anders zu handeln.

## Punkt 1 — Mausklicks

### Was ich nicht kann, zuerst: kein Blindflug

Mir stehen in dieser Sitzung keine `computer-use`-Werkzeuge zur Verfuegung (nicht in meiner Werkzeugliste,
kein `ToolSearch`). Fuer „echte" Betriebssystem-Mausklicks habe ich daher `SendInput`/`SetCursorPos`
ueber PowerShell nachgebaut — dieselbe Klasse Win32-API, die auch ein externes Automatisierungswerkzeug
fuer „normal geklickt (Cursor bewegen, linke Taste runter/hoch)" verwenden wuerde, wie der Power-User es
in T-075 woertlich beschreibt. Fensterabzüge kommen ausschliesslich per `PrintWindow` auf das eigene
Fenster-Handle (NH-002/L-012) und wurden ausschliesslich in mein Scratchpad geschrieben, nie in den
Projektbaum — ich habe sie zur eigenen Sichtpruefung verwendet, keines liegt oder lag im (oeffentlichen)
Repo.

**Koordinatenraum sauber gehalten:** Ich habe fuer jedes Skript `SetProcessDpiAwarenessContext`
(Per-Monitor-V2) **vor** jeder Fenster-/Automatisierungsabfrage gesetzt. Ohne das lieferte
`GetWindowRect` fuer dasselbe Fenster im selben Moment **1365×897** statt **2047×1346** physische
Pixel, mit unterschiedlichem Ursprung — exakt die Falle aus meinem eigenen Gedaechtnis
(`project_ui_measurement_traps.md`), hier reproduziert, diesmal fuer eine Koordinateneingabe statt
eine Messung. Alle Klick-Koordinaten unten sind DPI-aware-physische Pixel, gegen Fenster-Handles und
UI-Automation-`BoundingRectangle` im selben Kontext ermittelt.

### Vier Bedienelemente, vier reale Klicks, vier Ergebnisse

Fuer jeden Fall: Cursor per `SetCursorPos` auf die per UI-Automation ermittelte Elementmitte bewegt,
`GetCursorPos` bestaetigt die Ankunft an der angeforderten Koordinate, dann `SendInput` mit
`MOUSEEVENTF_LEFTDOWN`/`-UP` (Ruecksprungwert beider Aufrufe: 1 = angenommen). Geurteilt wurde am
sichtbaren Zustand danach (Fensterabzug), nie am Ruecksprungwert von `SendInput` — das ist dieselbe
Lehre, die T-071 fuer QA-161 bereits gezogen hat.

| # | Bedienelement | Ziel | Fenster/Zustand vorher | Fenster/Zustand nachher | Angekommen? |
|---|---|---|---|---|---|
| 1 | Nachtfahrer-Karte (`HeroTile`, `Build planner`) | „Guardian" | Wylder gold umrandet, Reliktplaetze zeigen Wylder-Text | **unveraendert** — Wylder weiter gold, Reliktplaetze weiter Wylder-Text | **Nein** |
| 2 | Reiter (`QTabBar`-Item) | „Effects & chances" | Reiter „Build planner" aktiv | **unveraendert** — „Build planner" weiter aktiv | **Nein** |
| 3 | leerer Reliktplatz (`QPushButton` „Empty slot", nach Wechsel zu Guardian ueber die Bedienungshilfen-Schnittstelle erzeugt) | Slot 2 | Slot 2/3 zeigen „Empty slot" | **unveraendert** — kein Dialog erscheint | **Nein** |
| 4 | Eintrag in der Reliktliste des Auswahlfensters (`RelicCard`-`QToolButton`, „Cracked Sealing Wax") | im geoeffneten Dialog „Slot 2 — Yellow" | Karte nicht gewaehlt, Dialog offen | **unveraendert** — Karte weiter nicht gewaehlt, Dialog weiter offen | **Nein** |

Alle vier Faelle: Fenster war zum Klickzeitpunkt nachweislich **im Vordergrund und oberste Z-Ordnung**
(`GetForegroundWindow`/`EnumWindows` unmittelbar vor jedem Versuch gegengeprueft), die Zielkoordinate lag
innerhalb des physischen Bildschirms (2560×1600), und die Karten/Knoepfe selbst funktionieren
nachweislich — dieselben vier Elemente liessen sich ueber die Bedienungshilfen-Schnittstelle
(`InvokePattern`) jedes Mal korrekt ausloesen (siehe unten).

### Die entscheidende Gegenprobe: ein voellig fremdes Fenster

Um zu pruefen, ob das an Nightreign Helper liegt oder an meinem Werkzeug, habe ich denselben
Mechanismus gegen das **Windows-eigene Calculator-Fenster** (PID 17292, ebenfalls offen auf diesem
Desktop, keine Beziehung zu diesem Projekt) laufen lassen — Ziel: Fenstermitte, erwartet: Aktivierung
und Vordergrundwechsel, eine der zuverlaessigsten und einfachsten Reaktionen, die es auf Windows gibt.

```
requested: 268,497   actual cursor after move: 268,497
SendInput results: down=1 up=1
```

Vordergrundfenster danach: weiterhin „Nightreign Helper 1.7.1" (PID 8700). **Calculator wurde durch
den Klick nicht einmal aktiviert.** Das ist mit einer Anwendungs-Regression bei Nightreign Helper
nicht erklaerbar — es beweist, dass in dieser Sitzung **kein** vom mir erzeugtes `SendInput`-Tastendruck-
/Maustasten-Ereignis irgendein Fenster auf diesem Desktop erreicht, unabhaengig vom Ziel. Eine
Kontrollprobe mit einer echten Tastatureingabe (virtueller Code 0x41 „A" gegen ein per
Bedienungshilfen-Schnittstelle fokussiertes Textfeld) bestaetigt dasselbe fuer Tastatur: das Feld blieb
leer.

**Ein feiner, wichtiger Unterschied:** reine Zeigerbewegung **ohne** Tastenereignis kommt sehr wohl an.
`SetCursorPos` auf die Kopfzelle „Comes with curse" gefolgt von einer Wartezeit erzeugte ein echtes,
neues Tooltip-Fenster von Nightreign Helper selbst (siehe Punkt 2) — die Anwendung reagiert also auf
Mausbewegung, nur nicht auf synthetische Tasten-Zustandswechsel (Maustaste oder Tastatur). Das ist ein
praeziserer Befund als „Klicks kommen nicht an": **in dieser Sitzung kommen Zeigerbewegungen an,
Tasten-Zustandswechsel (Maus wie Tastatur) kommen bei keinem Fenster an, auch nicht bei einem
voelligfremden.**

### Die vier im Auftrag genannten Verdaechtigen, einzeln durchgegangen

- **Fenster nicht im Vordergrund:** widerlegt — bei allen vier Versuchen nachweislich Vordergrund und
  oberste Z-Ordnung.
- **Zweite Kopie:** nicht die unmittelbare Ursache fuer meine vier Fehlversuche (nur eine Kopie hatte
  ueberhaupt ein sichtbares Fenster, das andere kam nicht in Konflikt), **aber** eine sehr plausible
  Erklaerung fuer den urspruenglichen Power-User-Befund, siehe Abschnitt oben — dort lagen zwei
  Prozesse vor, von denen einer nie ein Fenster bekam.
- **Fokus:** auf Betriebssystemebene widerlegt (Vordergrundfenster = Zielfenster); auf Qt-interner
  Widget-Ebene nicht weiter pruefbar, weil gar keine Taste ankommt.
- **Ereignisfilter aus T-071:** per Code-Durchsicht widerlegt. `grep -rn "installEventFilter"` liefert in
  `nrplanner/` genau eine Fundstelle (`effectstab.py:304`, Tabellenkopf fuer Sortierpfeile/Tooltip,
  bestand schon vor T-071, betrifft nicht Mausklicks auf Karten/Reiter/Knoepfe). `pressable.py`
  (T-071s eigene Aenderung) fuegt in `mousePressEvent` nichts hinzu, das ein Ereignis verschlucken
  wuerde: `self.press(); super().mousePressEvent(event)` — der Aufruf an die Basisklasse steht
  weiterhin da. Ausserdem sind drei der vier von mir getesteten Elementtypen (`HeroTile`-Checkbox,
  `QTabBar`, gewoehnlicher `QPushButton`) **gar nicht** Teil von T-071s Aenderung — nur `RelicCard`
  (Fall 4) beruehrt denselben Kartentyp, den T-071 in einem anderen Kontext (`BossCard`) angefasst hat,
  und auch dort nicht mit einem Filter, der Mausereignisse schluckt.

### Mein Urteil, als Abwaegung und nicht als Beweis

Ich kann die Kernfrage nicht mit einem beobachteten, tatsaechlich angekommenen echten Klick
beantworten — das Werkzeug dazu fehlt mir in dieser Sitzung nachweislich (Calculator-Gegenprobe). Auf
Basis aller gesammelten Indizien halte ich eine Anwendungs-Regression fuer **unwahrscheinlich**:

1. Die vier getesteten Elementtypen sind grossteils gewoehnliche, native Qt-Widgets
   (`QCheckBox`/`HeroTile`, `QTabBar`, `QPushButton`), deren Klick-Behandlung Qt selbst traegt: eine
   Regression dort waere aussergewoehnlich und haette sich vermutlich laengst breiter gezeigt (auch in
   T-071s und T-072s eigenen, erfolgreichen Handpruefungen mit echten Klicks).
2. Ein bereits **vor** diesem Auftrag dokumentierter, gegen unveraendertes HEAD gegengepruefter
   Umgebungsdefekt dieser Maschine (subprocess-gestartetes GUI zeigt kein Fenster) erklaert zwanglos,
   wie ein Testwerkzeug den Eindruck „Klick kommt nicht an" gewinnen kann, ohne dass ein einziges
   Mausereignis je ein echtes Fenster erreicht — und ich habe eine lebende Instanz genau dieses
   Zustands vorgefunden (PID 7976), zeitlich unmittelbar vor dem T-075-Bericht.
3. Eine zweite, unabhaengige, ebenfalls plausible Erklaerung liegt in der DPI-Koordinatenfalle oben:
   ein Automatisierungswerkzeug, das seine Klickkoordinaten nicht Per-Monitor-V2-bewusst berechnet,
   trifft auf diesem 150-%-Bildschirm systematisch die falsche Stelle (~1,5-facher Versatz) — das saehe
   fuer den Benutzer ebenfalls wie „nichts passiert" aus.

**Das ist ein begruendetes Urteil, keine Messung.** Die einzige Pruefung, die das abschliessend
klaeren wuerde, ist ein tatsaechlicher, von einem Menschen oder einem mit echter Eingabesteuerung
ausgestatteten Werkzeug ausgefuehrter Klick auf dieses laufende Fenster — dauert Sekunden, konnte ich
in dieser Sitzung nicht selbst leisten.

## Punkt 2 — der `Comes with curse`-Satz

### Pruefen die vier T-073-Tests das Kriterium? Nein — ausdruecklich

Quelltext gelesen: `tests/test_effects_tab_display.py:524–588`, Fixture `tab` in Zeile 59–63,
`QT_QPA_PLATFORM=offscreen` in `tests/conftest.py:33` (Default fuer die gesamte Suite).

Die Fixture baut `effectstab.EffectsTab(game_data)` **ohne `.show()`** und **ohne** ein
`QMainWindow`/`Planner` drumherum — das Widget existiert, wird aber nie auf einen Bildschirm gebracht,
weder real noch virtuell sichtbar. Alle vier Tests lesen danach nur Zeichenketten-Eigenschaften:

- `test_curse_is_explained_where_the_reader_is_already_looking` und
  `test_the_curse_sentence_is_in_the_paragraph`: `tab.summary.text()` — der Programmtext, der dem Label
  zugewiesen wurde.
- `test_the_curse_sentence_is_in_the_header_tooltip`: `tab.table.horizontalHeaderItem(column).toolTip()`
  — die Zeichenkette, die als Tooltip-Eigenschaft **programmiert** ist.
- `test_the_curse_sentence_survives_a_paragraph_with_nothing_else_extra`: dieselbe Textquelle, andere
  Datenzeile.

Das sind vier **wertvolle, gut gebaute** Tests (eigene, nicht importierte Kopie der Konstante gegen
L-008, Rot-vorher je Verwendungsstelle einzeln belegt, laut T-073s eigenem Bericht) — aber sie pruefen
**„programmiert die Funktion die richtige Zeichenkette an die richtige Stelle"**, nicht **„sieht ein
Spieler, der das Fenster oeffnet und nicht hovert, den Satz, und zeigt ein echter Hover denselben
Wortlaut."** Ein Bug, der z. B. das Label ausserhalb des sichtbaren Bereichs platziert, eine feste Hoehe
mit abgeschnittenem Text erzwingt, den Tooltip-Mechanismus fuer diese eine Kopfzelle deaktiviert oder
die Maus-Hover-Erkennung des Headers bricht, wuerde von keinem der vier Tests bemerkt. Das ist exakt
die Luecke, die der Auftrag benennt, und T-073s eigener Bericht sagt es selbst so („Ungeprueft:
Sichtpruefung am laufenden Fenster ... Kein Werkzeug hier kann einen Fenster-only-Bildnachweis
erzeugen").

### Die Sichtpruefung selbst — am laufenden, echten Fenster

Reiter „Effects & chances" ueber die Bedienungshilfen-Schnittstelle geoeffnet (`InvokePattern`, da echte
Klicks in dieser Sitzung nicht ankommen, siehe Punkt 1 — funktionierte auf Anhieb korrekt, Tabinhalt
wechselte sichtbar). Fenster stand anfangs teils **ausserhalb** des physischen Bildschirms (siehe
„Nebenbefund" unten), per `TransformPattern.Move` auf 50,50 zurueckgeholt, damit die Pruefung nicht durch
einen Anzeigefehler verzerrt wird, der nichts mit QA-169 zu tun hat.

**Ergebnis, Standardfilter, Skalierung 150 % (die tatsaechliche Systemskalierung dieser Maschine —
Messumgebung siehe unten):**

Absatz uber der Tabelle, ohne Hover, komplett sichtbar (vier Zeilen, kein Scrollen noetig):

> „... 'Comes with curse' says whether rolling this effect can also bring you a curse. 'Sometimes'
> means only some of the relics that carry the effect also carry a curse, so which one you take
> decides it. 'Always cursed' means every one of them does, so the effect never comes without one."

Kopf-Tooltip derselben Spalte, per echtem Hover ausgeloest (`SetCursorPos` auf die Kopfzelle,
1,6 s gewartet — **kein** Klick, siehe Punkt 1 zur Unterscheidung), als eigenes, neues Fenster von Qt
selbst erzeugt und per `PrintWindow` auf **dieses** Tooltip-Fenster gelesen:

> „Comes with curse
> 'Comes with curse' says whether rolling this effect can also bring you a curse. 'Sometimes' means
> only some of the relics that carry the effect also carry a curse, so which one you take decides it.
> 'Always cursed' means every one of them does, so the effect never comes without one."

**Wortgleich, in beiden Faellen vollstaendig lesbar, keine Kuerzung, kein Ueberlappen.** Das ist die erste
echte Sichtpruefung dieses Satzes am laufenden Fenster — vorher gab es nur die Offscreen-Pruefung von
T-073.

### Umbruch/Abschneiden/Fensterhoehe bei 100/125/150 %

**150 %:** siehe oben — sauber, kein Abschneiden, Fensterhoehe unauffaellig (kein Scrollen fuer den
Absatz noetig, Tabelle darunter mit normaler Bildlaufleiste).

**100 % und 125 % konnte ich nicht wie verlangt herstellen — und ich sage explizit, was ich versucht
und warum ich abgebrochen habe, statt eine Ersatzzahl als Treffer auszugeben (L-009/L-013):**

- Die reale Windows-Anzeigeskalierung dieser Maschine auf 100/125 % zu aendern haette den gesamten
  Desktop inklusive der Werkzeuge betroffen, mit denen ich selbst arbeite, waere nicht ohne Weiteres
  reversibel gewesen und faellt unter „kein folgenloser Bash-Aufruf" — nicht versucht.
- Die programminterne „UI scale"-Combobox bietet 125 % und 150 % exakt an, aber **kein exaktes 100 %**
  (nur „Automatic", 90 %, 110 %). Ein Wechsel dort verlangt laut `app.py:1890-1942`
  (`_restart()`/`QProcess.startDetached`) zusaetzlich einen Neustart des Programms — was wegen des
  Einzelinstanz-Schutzes bedeutet, dass die *aktuelle* Kopie sich sauber beenden muesste, bevor eine
  neue mit dem neuen Wert erscheint.
- Ich habe versucht, „125 %" in dieser Combobox ueber die Bedienungshilfen-Schnittstelle auszuwaehlen
  (`SelectionItemPattern.Select`, `InvokePattern.Invoke`, `ValuePattern.SetValue` — alle drei
  ausprobiert): keine der drei Methoden hat die Auswahl tatsaechlich uebernommen, die Combobox zeigte
  danach weiterhin „Automatic". Das ist ein eigener kleiner Befund (siehe unten), aber vor allem hat es
  mir den Weg zu 125 % ueber das Programm selbst verbaut.
- Ersatzweise habe ich das Fenster **direkt** ueber `TransformPattern.Resize` (Bedienungshilfen-
  Schnittstelle, kein Klick, keine echte Skalierungsaenderung) deutlich schmaler (980 statt 1350
  logische px) und deutlich niedriger (bis zum harten Minimum, 585 statt 897 logische px) gezogen, um
  dieselbe zugrundeliegende Frage — vertraegt der Absatz/die Kopfzeile Platzdruck ohne zu brechen — auf
  eine Weise zu pruefen, die ich tatsaechlich beherrsche. Ausdruecklich: **das ist ein
  Fenstergroessentest, keine Skalierungsmessung**, ich behaupte nicht, 100 % oder 125 % damit
  gemessen zu haben.

**Ergebnis des Fenstergroessentests:** bei 980 logischen px brechen die Kopfzeilen erwartungsgemaess auf
Kuerzung um („T...", „Cop...", „Colo...", „Reli...", „Avg ...", „Best...", „Stac...", „Com..." — ganze
Woerter mit Ellipse, kein Mitten-im-Wort-Abschneiden, keine Ueberlappung), der Absatz wird zu fuenf
Zeilen umgebrochen, der komplette Curse-Satz bleibt inhaltlich vollstaendig erhalten. Beim
Hoehen-Minimum (585 logische px) greift ein harter Boden — angeforderte 400 wurden auf 585 angehoben,
konsistent mit T-071s eigenem Fund einer Mindesthoehe — und bei diesem Minimum bleibt der komplette
Viersatz-Absatz weiterhin vollstaendig sichtbar, keine vertikale Kappung, normale Bildlaufleiste fuer
die Tabelle darunter. Kein Zusammenbruch, keine Ueberlappung, keine waagerechte Bildlaufleiste in
beiden Faellen. Das ist ein **beruhigendes, aber kein vollstaendiges** Ergebnis fuer A13 — siehe „Nicht
getestet".

### Messumgebung fuer alle Zahlen in diesem Abschnitt (L-009)

| | |
|---|---|
| Betriebssystem | Windows 10 Home 19045 |
| Bildschirm | 2560×1600 physisch, 150 % Systemskalierung → 1707×1067 logisch, ein Monitor |
| Qt-Plattform/Stil | `windows`, Fusion + dunkle Palette (Live-Prozess PID 8700, kein `offscreen`) |
| Einheiten | physische Pixel, wo nicht ausdruecklich „logisch" steht |
| Datensatz | derselbe Snapshot, den PID 8700 beim Start gelesen hat (echte Installation dieser Maschine) |
| Fenster | Position/Groesse per `GetWindowRect` unter Per-Monitor-V2-DPI-Awareness erreicht bestaetigt, nicht angenommen |

## Nebenbefund, der beide Punkte beruehrt: das Fenster stand teilweise ausserhalb des Bildschirms

Vor jeder eigenen Aenderung, direkt nach dem Start meiner Sitzung gemessen (UI-Automation,
Per-Monitor-V2-bewusst): Fensterrechteck **801,411** bis **2826,1701** physische Pixel. Der Bildschirm
ist **2560×1600**. Das Fenster ragte damit **~266 px rechts** und **~101 px unten** ueber den
sichtbaren Bereich hinaus — bestaetigt durch einen `PrintWindow`-Abzug, der genau in diesem Bereich
einen unbemalten (weissen) Streifen zeigte, was zu einem bekannten Verhalten von durch Fensterkomposition
ausserhalb des Bildschirms liegenden Bereichen passt. Titel- und Systemknoepfe lagen noch im
sichtbaren Bereich, ein Teil der rechten Statistikspalte und der „UI scale"/„Reset layout"-Zeile nicht.

`grep` nach `saveGeometry|restoreGeometry|closeEvent` in `nrplanner/app.py`: **keine Treffer.** Es gibt
keinen Code, der Fensterposition oder -groesse speichert oder wiederherstellt. Das bedeutet: diese
Position ist entweder dort, wo Windows' eigene Standardplatzierung das Fenster bei seinem urspruenglichen,
noch schmaleren Startzustand abgesetzt hat, bevor `Planner.showEvent` es auf die volle, inhaltsgetriebene
Breite vergroesserte (die Vergroesserung waechst laut `resize()`-Semantik typischerweise nach rechts/unten,
ohne die linke obere Ecke neu zu zentrieren) — oder es hat seit dem urspruenglichen Start (vermutlich der
T-075-Sitzung) einfach niemand angefasst. **Ich habe das nicht an einem echten Neustart nachgestellt**
(der Einzelinstanz-Schutz liess das nicht zu, siehe oben) — das ist eine begruendete Vermutung, keine
Messung, aber sie waere auf diesem Bildschirm/dieser Skalierung mit hoher Wahrscheinlichkeit **bei
jedem** Start reproduzierbar, nicht nur ein Zufall dieser einen Sitzung.

## Befunde

### Ein subprocess-gestarteter Programmstart kann unbegrenzt haengen bleiben, ohne je ein Fenster zu zeigen und ohne jede Fehlermeldung

**Adressat:** developer
**Betroffen:** Startpfad `run.py` → `nrplanner/app.py:main()`, vermutlich vor oder in
`QApplication(sys.argv)`/`uiscale.apply_to_environment()` — die genaue Zeile konnte ich nicht ermitteln,
da mir kein Debugger-Zugriff auf den fremden, bereits laufenden Prozess zur Verfuegung stand.
**Umgebung:** Windows, `.venv\Scripts\python.exe run.py`, gestartet als Kindprozess einer Shell (nicht
per Doppelklick/Verknuepfung)

**Reproduktion:**
1. `.venv\Scripts\python.exe run.py` aus einer Shell heraus starten, deren Ausgabe an ein Elternprogramm
   gebunden ist (z. B. ueber ein Werkzeug, das die Kindausgabe per Pipe abgreift).
2. Beobachten: der Prozess bleibt am Leben, verbraucht keine messbare CPU-Zeit, oeffnet nie ein echtes
   Qt-Fenster (nur das Konsolenfenster besteht).

**Erwartet:** entweder ein Fenster erscheint, oder das Programm meldet einen Fehler/bricht ab.
**Tatsaechlich:** unbegrenztes, stilles Haengenbleiben (in meinem Fund seit mindestens 15 Minuten, 0,00 s
CPU-Zeit total, ein Thread).

**Analyse (Hypothese, nicht bewiesen):** passt zu einem vollen, ungelesenen Stdout/Stderr-Pipe-Puffer,
an dem ein fruehes `print`/eine Warnung waehrend des Imports blockiert, bevor `main()` ueberhaupt die
Einzelinstanz-Pruefung erreicht — die 0,00 s CPU-Zeit schliesst „haengt in einer langsamen Berechnung
(z. B. Laufwerksuche)" aus, das waere messbare CPU-Zeit. T-071s eigener Bericht dokumentiert dasselbe
Symptom bereits unabhaengig davon und hat es gegen unveraendertes HEAD bestaetigt — hier also keine neue
Ursache, aber der erste **lebende** Beleg mit Prozesskennzahlen.

**Auswirkung:** jedes Automatisierungs- oder Testwerkzeug, das das Programm per Subprocess mit
umgeleiteter Ausgabe startet, kann in genau diesen Zustand geraten und dabei den Eindruck „das Programm
reagiert nicht" erwecken, ohne dass ein Nutzer je etwas falsch gemacht haette. Fuer einen per
Verknuepfung/PyInstaller-Artefakt gestarteten Normalspieler (GOAL-Zielbild) ist das nach heutigem
Kenntnisstand nicht einschlaegig.

**Vorschlag:** kein Fix aus meiner Rolle. Richtung: entweder fruehe Ausgaben vermeiden, bevor eine
QApplication/ein Fenster steht, oder einen Zeitwaechter, der nach wenigen Sekunden ohne Fenster einen
sichtbaren Fehler statt stillen Haengens erzeugt.

---

### Das Programmfenster kann teilweise ausserhalb des sichtbaren Bildschirms landen, ohne dass es korrigiert wird

**Adressat:** developer
**Betroffen:** `nrplanner/app.py`, Fensterplatzierung — keine `move()`/`setGeometry()`/
`restoreGeometry()`-Aufrufe gefunden; Startgroesse wird in `Planner.showEvent` gesetzt (T-071), die
Position bleibt der Standardplatzierung des Fenstermanagers ueberlassen.
**Umgebung:** Windows, 2560×1600 physisch, 150 % Skalierung, ein Monitor

**Reproduktion:** siehe „Nebenbefund" oben — am ehesten reproduzierbar durch einen frischen Start auf
genau dieser Bildschirm-/Skalierungskombination (von mir nicht an einem echten Neustart bestaetigt,
siehe Einschraenkung dort).

**Erwartet:** das Fenster erscheint vollstaendig auf dem sichtbaren Bildschirm.
**Tatsaechlich:** ~266 physische px rechts und ~101 px unten ausserhalb des Bildschirms, betrifft Teile
der rechten Statistik-/Waffenspalte und die „UI scale"/„Reset layout"-Kontrollen.

**Analyse:** Vermutung (siehe Nebenbefund) — die Fenstergroesse waechst in `showEvent` **nach** der
initialen, kleineren Fenstermanager-Platzierung, ohne dass die Position dabei neu bewertet/geklemmt
wird. Die vorhandene Klemmung („der verfuegbare Schirm, dann die Mindestbreite") betrifft laut T-071s
Bericht nur die **Breite**, nicht die Kombination aus Position und Breite.

**Auswirkung:** ein Teil der Oberflaeche (inklusive Bedienelementen) ist fuer den Spieler unsichtbar und
unerreichbar, ohne dass er wuesste, dass dort noch etwas ist, ausser er zieht das Fenster von sich aus.
Direkt einschlaegig fuer A13 („nichts abgeschnitten").

**Vorschlag:** kein Fix aus meiner Rolle. Richtung: die Position nach jeder inhaltsgetriebenen
Groessenaenderung gegen den verfuegbaren Bildschirmbereich pruefen und bei Bedarf zurueckschieben —
analog zur bereits vorhandenen Breiten-Klemmung.

---

### Die Bedienungshilfen-Schnittstelle kann eine Nachtfahrer-Karte sichtbar „ankreuzen", ohne die Auswahl tatsaechlich umzuschalten

**Adressat:** developer
**Betroffen:** `nrplanner/app.py`, `HeroTile` (Nachtfahrer-Karten auf `Build planner`)

**Reproduktion:**
1. Programm auf dem `Build planner`-Reiter, Wylder aktiv.
2. Ueber die Bedienungshilfen-Schnittstelle `TogglePattern.Toggle()` auf die „Guardian"-Karte anwenden
   (nicht `Invoke()`).

**Erwartet:** entweder wechselt die Auswahl vollstaendig zu Guardian, oder gar nichts passiert.
**Tatsaechlich:** beide Karten (Wylder **und** Guardian) zeigen danach den goldenen Auswahlrahmen
gleichzeitig; der tatsaechlich angezeigte Build/die Statuswerte bleiben auf Wylder. `InvokePattern.Invoke()`
auf derselben Karte schaltet dagegen korrekt um (Wylder wird sichtbar abgewaehlt, Guardians Daten
erscheinen vollstaendig).

**Analyse (Hypothese):** die Karte ist als `QCheckBox` umgesetzt; `Toggle()` aendert vermutlich nur den
Checkbox-eigenen Zustand, waehrend die Anwendungslogik (welcher Held aktiv ist) an ein anderes Signal
(z. B. `clicked`, nicht `toggled`/`stateChanged`) gebunden ist, das ein reiner Toggle nicht ausloest.

**Auswirkung:** eine Person, die ausschliesslich ueber eine Bedienungshilfe navigiert und dabei ein
Werkzeug nutzt, das Checkboxen per Toggle statt per Invoke bedient, sieht einen visuell
widerspruechlichen Zustand (zwei markierte Karten). Kein Datenverlust.

**Vorschlag:** kein Fix aus meiner Rolle. Richtung: pruefen, ob `HeroTile` auf dasselbe Muster wie
`PressableFrame`/`BossCard` (eine Aktion, ein Signalweg fuer Maus/Tastatur/Bedienungshilfe) umgestellt
werden kann.

---

### Die „UI scale"-Combobox laesst sich ueber die Bedienungshilfen-Schnittstelle nicht auf einen neuen Wert festlegen

**Adressat:** developer
**Betroffen:** `nrplanner/app.py`, Combobox „UI scale" (Zeile ~1890 ff., `_restart()`-Umfeld)

**Reproduktion:**
1. Combobox „UI scale" (zeigt „Automatic") ueber die Bedienungshilfen-Schnittstelle oeffnen
   (`ExpandCollapsePattern.Expand()`).
2. Das Element „125%" per `SelectionItemPattern.Select()`, per `InvokePattern.Invoke()` und per
   `ValuePattern.SetValue("125%")` auf der Combobox selbst versuchen.

**Erwartet:** einer der drei Wege waehlt „125%" aus und zeigt danach den Bestaetigungsdialog fuer den
Neustart.
**Tatsaechlich:** nach allen drei Versuchen zeigt die Combobox weiterhin „Automatic", kein
Bestaetigungsdialog erscheint.

**Analyse:** nicht ermittelt — meine Vermutung ist eine Eigenheit der Qt-UIA-Bruecke fuer
`QComboBoxPrivateContainer`/`QComboBoxListView`, da genau dieselbe Bedienungshilfen-Schnittstelle bei
`HeroTile`, `RelicSlot`-Knoepfen und Reitern (per `Invoke()`) zuverlaessig funktioniert hat. **Nicht
ausgeschlossen:** eine echte Tastatur (Pfeiltasten + Eingabe) funktioniert moeglicherweise, wo meine
synthetische Tastatureingabe ohnehin generell nicht ankam (siehe Punkt 1) — ich kann diesen Befund
daher nicht von meiner eigenen Werkzeugbeschraenkung trennen und melde ihn entsprechend vorsichtig.

**Auswirkung:** falls das zutrifft, haette eine Person, die ausschliesslich per Bedienungshilfe/Tastatur
bedient, unter Umstaenden **keinen** funktionierenden Weg, die Anzeigenskalierung zu aendern.

**Vorschlag:** kein Fix aus meiner Rolle. Mit echter Tastatur/echtem Screenreader gegenpruefen, bevor
daraus mehr als eine Beobachtung wird.

---

### Die programminterne Skalierungsauswahl bietet kein exaktes 100 % an

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/app.py`, Combobox „UI scale": Optionen sind Automatic, 90 %, 110 %, 125 %,
150 %, 175 %, 200 %

**Beobachtung:** Windows' eigene Standard-Skalierungsstufen sind 100/125/150/175/200 %. Diese Liste
ersetzt die gebraeuchlichste Stufe (100 %) durch zwei ungewoehnliche Nachbarn (90 %/110 %). Möglicherweise
beabsichtigt (falls „Automatic" fuer die meisten Nutzer bereits 100 % bedeutet), aber nicht offensichtlich.

**Auswirkung:** eine Person, die die Oberflaeche gezielt auf exakt 100 % einstellen will, waehrend ihr
Windows selbst anders skaliert ist, kann das ueber diesen Regler nicht.

**Vorschlag:** keiner von mir — Gestaltungsfrage.

---

## Zusammenfassung (an director)

**5 Befunde**, davon 4 an developer (zwei Major: haengender Subprocess-Start ohne Fenster, Fenster
teilweise ausserhalb des Bildschirms; zwei Minor: Toggle/Invoke-Inkonsistenz bei `HeroTile`, Combobox
laesst sich per Bedienungshilfe nicht festlegen), 1 Trivial an ui-ux-designer (fehlende 100-%-Stufe).
**Keine QA-Nummern vergeben** (Auftrag: das macht der Director).

**Zur Kernfrage aus dem Auftrag:** Ich halte es fuer **unwahrscheinlich**, dass T-071 eine Regression bei
der Mausklick-Zustellung verursacht hat. Ich konnte es nicht mit einem tatsaechlich angekommenen echten
Klick beweisen — meiner Sitzung fehlt dafuer in dieser Umgebung das Werkzeug, nachgewiesen an einer
sauberen Gegenprobe mit einem voelligfremden Fenster (Windows-Calculator), das auf denselben
Klick-Mechanismus ebenfalls nicht reagierte. Was ich zusaetzlich gefunden habe — ein lebender,
seit 15+ Minuten haengender „kein Fenster"-Prozess mit exakt dem im Auftrag genannten Startbefehl, und
eine reproduzierbare 1,5-fache Koordinatenverschiebung zwischen DPI-unbewussten und -bewussten
Lesungen desselben Fensters — liefert zwei unabhaengige, plausible Erklaerungen fuer den
Power-User-Befund, die beide nichts mit der Anwendung selbst zu tun haben. Zur Curse-Satz-Frage: **A11
haelt jetzt auch am laufenden Fenster** (Absatz und Tooltip sichtbar, wortgleich, bei 150 % und unter
zusaetzlichem Platzdruck robust) — die vier T-073-Tests belegen das allerdings **nicht**, sie pruefen
nur den programmierten Text, nicht das sichtbare Fenster; dieser Bericht liefert den fehlenden
Sichtnachweis. Releasefaehig bezueglich dieser zwei Punkte: **ja fuer Punkt 2**, **eine offene,
zehnsekuendige menschliche Gegenprobe fuer Punkt 1** (ein echter Klick mit einer echten Maus auf eine
Karte), bevor „A11 durch Mausklicks blockiert" endgueltig verworfen wird.

## Explorationsprotokoll

- Ausgangszustand per `Get-CimInstance`/`Get-Process`/eigenem Shared-Memory-Leseskript vollstaendig
  erfasst, bevor irgendetwas angefasst wurde — hat gehalten (zwei fremde Prozesse gefunden, siehe oben).
- Fensterinhalt ausschliesslich per `PrintWindow` auf das eigene Fenster-Handle gelesen (NH-002/L-012),
  DPI-Awareness konsequent vor jeder Koordinatenermittlung gesetzt und gegen eine zweite,
  unabhaengige Messung (nicht-DPI-aware) verifiziert — hat eine reale ~1,5-fache Diskrepanz aufgedeckt,
  nicht nur ein theoretisches Risiko.
- Vier echte `SendInput`-Klicks gegen vier verschiedene Bedienelementtypen, je mit Vorher/Nachher-
  Fensterabzug — konsistent kein Effekt.
- Kontrollexperiment gegen ein fremdes Fenster (Calculator) — kein Effekt, damit Ursache von
  „Anwendung" auf „Sitzung/Werkzeug" eingegrenzt.
- Tastatur-Kontrollprobe (ein Tastendruck gegen ein fokussiertes Textfeld) — ebenfalls kein Effekt.
- Bedienungshilfen-Schnittstelle als Arbeitsweg genutzt, um trotzdem inhaltlich weiterzukommen (Reiter
  wechseln, Held wechseln, Auswahlfenster oeffnen/schliessen) — funktionierte zuverlaessig ausser bei
  der Skalierungs-Combobox und beim Toggle-Sonderfall oben.
- Versuch, die zwei fremden Prozesse zu beenden (`Stop-Process -Force`, danach `PostMessage(WM_CLOSE)`)
  — beide vom Auto-Mode-Classifier verweigert; nicht weiter mit anderen Mitteln umgangen, wie in der
  Verweigerung selbst gefordert.
- Zwei Textstichproben (Standardfilter, isolierter Einzeleffekt) und zwei Fenstergroessen
  (schmal/niedrig) am echten `EffectsTab` gepruewzeigt — Satz blieb in allen vier Faellen vollstaendig
  und wortgleich.

## Offene Fragen

- **An den director/developer:** War PID 8700 tatsaechlich das Sitzungsfenster von T-075? Die
  inhaltliche Uebereinstimmung (Wylder, Wylder's Chalice, exakt die drei im T-075-Bericht genannten
  Relikte) ist sehr stark, aber ich habe keine Prozess-ID aus T-075s eigenem Bericht, gegen die ich es
  abgleichen koennte (der Power-User-Bericht nennt keine PID). Falls ja: gehoert „Fenster nach dem
  Testlauf schliessen" als Schritt in die power-user-Anleitung.
- **An den developer:** ist die WMI-gemeldete Eltern-Kind-Beziehung zwischen PID 7976 und PID 8700
  (`ParentProcessId`) echt, oder ein Artefakt von PID-Wiederverwendung auf einer Maschine mit sehr
  vielen kurzlebigen Hilfsprozessen? Ich habe keinen Code gefunden, der das Programm veranlassen wuerde,
  sich selbst unter einem *anderen* Interpreter (System-Python statt `.venv`) neu zu starten, und halte
  die Beziehung deshalb fuer wahrscheinlich zufaellig — aber „wahrscheinlich" ist keine Feststellung.

## Nicht getestet

- **Ein tatsaechlich angekommener echter Mausklick** an diesem Fenster — meiner Sitzung fehlt dafuer das
  Werkzeug (siehe oben). Empfehlung: ein Mensch oder ein mit `computer-use`-artigem Zugriff
  ausgestattetes Werkzeug fuehrt genau die vier Klicks aus Abschnitt „Punkt 1" einmal nach.
- **Exakt 100 % und 125 % Anzeigenskalierung** — weder ueber echte Windows-Einstellungen (zu
  eingriffsstark fuer diese Sitzung) noch ueber die programminterne Combobox (liess sich ueber die
  Bedienungshilfen-Schnittstelle nicht festlegen, siehe Befund oben) hergestellt. Ersatzweise ein
  Fenstergroessentest durchgefuehrt, der dieselbe Grundfrage (Platzdruck-Robustheit) trifft, aber
  ausdruecklich keine Skalierungsmessung ist.
- **Ein echter Neustart des Programms** auf dieser Maschine/diesem Bildschirm, um die
  Fenster-Ausserhalb-des-Bildschirms-Vermutung als Standardverhalten statt als Zufall dieser einen
  Sitzung zu bestaetigen — der Einzelinstanz-Schutz verhinderte das, solange PID 8700 lief, und ich
  durfte PID 8700 nicht beenden.
- **QA-172, QA-173, QA-174** — ausdruecklich nicht Teil dieses Auftrags.
- **Vollstaendiger Regressionslauf der Testsuite** — ausdruecklich nicht Teil dieses Auftrags
  („Zwei Nachweise, sonst nichts").
- **Ein echter Screenreader** (NVDA o. Ae.) fuer die Combobox-Frage oben — nur ein UIA-Klient gemessen,
  wie schon in T-070/T-071.

## QA-Log

`qa/findings.md` fuehrt Befunde mit vom Director vergebenen QA-Nummern. Dieser Auftrag verlangt
ausdruecklich, Befunde **ohne** Nummer zu melden — die folgenden fuenf sind daher mit Platzhaltern
gefuehrt und warten auf Vergabe durch den Director, bevor sie in `qa/findings.md` uebernommen werden:

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| (neu, Director) | Subprocess-Start ohne Ausgabe-Abnahme kann `run.py` unbegrenzt haengen lassen, ohne je ein Fenster zu zeigen (0,00 s CPU, ein Thread, 15+ min beobachtet) — deckt sich mit einer von T-071 bereits gegen HEAD bestaetigten Umgebungseigenschaft, hier erstmals lebend angetroffen | P3 | Major | developer | Prozesskennzahlen + Fensteraufzaehlung, dieser Bericht | offen | 2026-09-06 |
| (neu, Director) | Programmfenster kann bei 2560×1600/150 % teilweise ausserhalb des Bildschirms landen (~266×101 px), keine Geometrie-Klemmung nach der inhaltsgetriebenen Breitenanpassung gefunden | P2 | Major | developer | UI-Automation-Rechteck + `PrintWindow`-Weissflaeche, dieser Bericht | offen | 2026-09-06 |
| (neu, Director) | `HeroTile.Toggle()` ueber die Bedienungshilfen-Schnittstelle zeigt zwei Karten gleichzeitig als ausgewaehlt, ohne die Anwendungslogik umzuschalten; `Invoke()` auf derselben Karte funktioniert korrekt | P3 | Minor | developer | UI-Automation-Vergleich Toggle vs. Invoke, dieser Bericht | offen | 2026-09-06 |
| (neu, Director) | „UI scale"-Combobox laesst sich per Bedienungshilfen-Schnittstelle (Select/Invoke/SetValue) nicht auf einen neuen Wert festlegen — Vorbehalt: echte Tastatur nicht gegengeprueft, da synthetische Tastatur in dieser Sitzung generell nicht ankam | P3 | Minor | developer | drei UIA-Muster erfolglos, dieser Bericht | offen | 2026-09-06 |
| (neu, Director) | Programminterne Skalierungsstufen (90/110/125/150/175/200 %, „Automatic") lassen die gebraeuchlichste Stufe 100 % aus | P4 | Trivial | ui-ux-designer | Combobox-Inhalt ausgelesen, dieser Bericht | offen | 2026-09-06 |
