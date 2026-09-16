STATUS: erledigt
AUFTRAG: T-074 - Erststart mit Ordnerauswahl (ui-ux-designer, Modus Spec)
GELESEN: docs/tasks/T-074.md; CLAUDE.md; GOAL.md (A8-A15 samt Nachtrag 06.09.2026);
UI_SPEC.md (Struktur und letzte vergebene AK-Nummer); DESIGN_REVIEW.md (DR-005, DR-006);
README.md (Voraussetzungen, Install, Speicherorte); nrplanner/firstrun.py (vollstaendig);
nrplanner/datasource.py (vollstaendig); nrplanner/paths.py; nrplanner/uiscale.py;
nrplanner/app.py (main(), apply_appearance, Farb-Token, rescan_save, Knopfzeile
1534-1556, 3200-3245, 3860-3893); nrdata/gamefiles.py; nrdata/savefile.py
(save_roots, find_saves); nrdata/dvdbnd.py (open_all); nrdata/oodle.py (load,
_DLL_NAMES); nrdata/bhd5.py (ARCHIVE_KEYS); nrplanner/inventory.py (load, _scan_save)
GEAENDERT: UI_SPEC.md (neuer Abschnitt "Der Erststart mit Ordnerauswahl (T-074)",
angehaengt, nichts ueberschrieben); docs/berichte/T-074-ui-ux-designer.md (diese Datei).
Kein Anwendungscode. Git ausschliesslich lesend, nichts gestaged, nichts committet.
Hinweis: `git status` zeigt zusaetzlich `nrplanner/effectstab.py` und
`tests/test_effects_tab_display.py` als geaendert - die stammen aus dem parallel
laufenden T-073 im selben Arbeitsbaum, nicht von mir.
ANNAHMEN: (1) Es gibt keinen hart verifizierbaren Nightreign-eigenen Dateinamen
(etwa eine .exe), an dem sich das Spiel von ELDEN RING unterscheiden liesse - der
Code kennt keinen. Deshalb Stufe 2 als weiche Rueckfrage statt harter Ablehnung.
(2) Die Grenzwerte der Ordnersuche (Tiefe 3, 2 Elternebenen, 400 Verzeichnisse,
2 Sekunden) sind gesetzt, nicht gemessen - sie decken die realen Steam-Layouts aus
gamefiles._library_paths ab und schliessen eine Plattensuche aus. (3) Der
QSettings-Speicher (favourites.ORG/APP) ist der richtige Ort fuer die beiden
gemerkten Pfade, weil ui/scale und ui/panes bereits dort liegen.
NAECHSTER: director
BLOCKIERT DURCH: nichts

---

# T-074 - Erststart mit Ordnerauswahl: Spec

## Methode und ihre Grenze

Nur Codelesung. Der Auftrag untersagt das Starten des Fensters (T-073 laeuft
parallel, T-071-Einzelkopiesperre). **Aus diesem Lauf gibt es keinen
Bildnachweis und keine Messung.** Jede Pixelangabe in der Spec ist als
Sollwert gekennzeichnet und traegt ihre Umgebung (Windows 10, Fusion, dunkle
Palette, QT_SCALE_FACTOR nicht gesetzt, Anzeige 100 %, logische Pixel) - L-009.

**Was ohne laufendes Fenster nicht entschieden werden konnte** und beim
Nachholen zu pruefen ist:

- die tatsaechliche Hoehe des Frage-Zustands bei den laengsten Texten (A2/W1)
  in den drei Skalierungen. Die Mindesthoehe 230 ist gesetzt, nicht gemessen;
- ob der Windows-Systemordnerdialog, aus dem heutigen SplashScreen-Fenster
  geoeffnet, tatsaechlich dahinter landen kann. Der Befund dazu ist aus den
  Fensterflaggen abgeleitet (kein Taskleisteneintrag, nicht verschiebbar),
  nicht beobachtet. Die Empfehlung, den Frage-Zustand als normales Fenster zu
  fuehren, steht auch ohne diese Beobachtung - ein Fenster, in dem der Nutzer
  eine Entscheidung trifft, gehoert in die Taskleiste.

## Die Entscheidungen, und warum

**1. Der Dialog ist der erste Zustand von `firstrun._Window`, nicht ein
eigenes Fenster.** Auftragsvorgabe, und sie stimmt: der Erststart ist bereits
eine Folge von Zustaenden (bauen, Startmenue-Angebot). Die Frage nach dem
Ordner ist der Zustand davor. Ein zweites Fenster haette zwei Fenstergroessen,
zwei Positionen und einen Sprung dazwischen.

**Aber: die Fensterart aendert sich fuer diesen Zustand.** `SplashScreen` hat
keine Titelleiste, keinen Taskleisteneintrag, ist nicht verschiebbar und nimmt
kein Escape. Das ist fuer einen Fortschrittsbalken richtig und fuer eine
Entscheidung falsch, besonders wenn daraus ein Systemdialog aufgeht. Ich habe
das als Aenderung spezifiziert (AK-109) statt es zu umgehen.

**2. Spielordner: Ordnerauswahl. Spielstand: Dateiauswahl.** Bewusst
gegenlaeufig, aus demselben Grund - jeweils das, was der Nutzer *sieht und
meint*. Beim Spiel ist es der Ordner, den Steam ihm mit *Browse local files*
oeffnet; `regulation.bin` kennt er nicht. Beim Spielstand ist es die Datei,
und bei zwei Steam-Konten ist die Dateiauswahl die einzige Form, in der er
sagen kann, welches Konto er meint.

**3. Der falsche Ordner wird nicht abgelehnt, sondern durchsucht.** Der Nutzer
waehlt `...\ELDEN RING NIGHTREIGN`, das Programm braucht `...\Game`. Gesucht
wird nach unten bis Tiefe 3 und nach oben 2 Ebenen, begrenzt auf 400
Verzeichnisse und 2 Sekunden. Tiefe 3 ist so gewaehlt, dass auch `common` und
`steamapps` noch tragen; die Grenze verhindert, dass ein Laufwerksstamm zur
minutenlangen Plattensuche wird.

**4. `regulation.bin` allein beweist nichts** - ELDEN RING hat sie auch, samt
`data*.bhd` und Oodle-DLL. Deshalb zwei Stufen: harte Strukturpruefung
(regulation.bin lesbar und nicht leer, ein data*.bhd aus `bhd5.ARCHIVE_KEYS`,
eine DLL aus `oodle._DLL_NAMES`) und eine weiche Identitaetsrueckfrage ueber
den Ordnernamen (`gamefiles.INSTALL_DIR`), die den Nutzer nicht aussperrt.
Der Fehler, den das verhindert: eine Minute Arbeit an ELDEN RING und danach
durchgehend falsche Zahlen, ohne dass irgendwer etwas merkt.

**5. Der Spielstand bekommt kein Modal.** Hier bin ich vom naheliegenden Weg
abgewichen und nenne den Grund: der Spielstand ist laut README ausdruecklich
optional, und ein Spieler, der das Spiel auf diesem PC noch nie gestartet hat,
hat schlicht keinen. Ein Auswahlfenster, das er nur wegklicken kann, waere
genau die Reibung, die A15 beseitigen soll. Stattdessen wird die Zeile
handlungsfaehig, die den Fehlschlag heute schon meldet (`app.py:3217`), mit
einem echten Knopf `Find my save...` in der vorhandenen Knopfzeile neben
`Rescan save`. Die Gegenposition ist vertretbar und steht als offene Frage 2.

**6. Ein wegfallender Spielordner blockiert nicht, wenn Daten da sind.** Ein
abgezogenes USB-Laufwerk darf kein Totalausfall sein. Text A3 bietet
`Continue with the data from {Datum}` - mit Datum, weil "alte Zahlen ohne
Hinweis" der schlechtere Zustand waere. Steht als offene Frage 3.

**7. Der gemerkte Pfad wird bei einem Fehlschlag nicht geloescht** (AK-121).
Er wird nur ersetzt. Ein Laufwerk kommt wieder.

**8. Reihenfolge gemerkt -> Automatik -> Panel** (AK-107). Der zweite Schritt
nach einem toten gemerkten Pfad ist der Grund, warum jemand, der sein Spiel
neu an den Standardort installiert, kein Fenster sieht.

## AK-Nummern

AK-106 bis AK-132, 27 Stueck, alle in `UI_SPEC.md` Abschnitt 10:

- **AK-106** geglueckter Fall bleibt klickfrei
- **AK-107** Aufloesungsreihenfolge gemerkt -> Automatik -> Panel
- **AK-108** Panel statt der heutigen QMessageBox aus `app.py:3883`
- **AK-109** Frage-Zustand mit Titelleiste, Taskleiste, verschiebbar
- **AK-110** Ordnerauswahl, definierter Startort
- **AK-111** Elternordner werden erkannt; Suchgrenzen 400 Verzeichnisse / 2 s
- **AK-112** harte Strukturpruefung vor Annahme
- **AK-113** weiche Identitaetsrueckfrage, Standardknopf ist das Zurueck
- **AK-114** nach Ablehnung bleibt das Fenster offen, Programm endet nie selbst
- **AK-115** Abbruch der Systemauswahl aendert nichts
- **AK-116** Quit / Escape / Fensterkreuz: sauberes Ende ohne Fehlerdialog
- **AK-117** Pfad wird vor dem Bau gespeichert (`paths/game`)
- **AK-118** kein Klick zwischen Bestaetigung und Bau
- **AK-119** kein Spielordner, aber Datenabzug: nicht blockieren, Datum nennen
- **AK-120** kein Spielordner, kein Abzug: blockieren, Text A2
- **AK-121** ein Fehlschlag loescht keinen gemerkten Pfad
- **AK-122** fuer den Spielstand nie ein Modal
- **AK-123** Knopf `Find my save...`, Dateiauswahl, Startort
- **AK-124** drei unterscheidbare Ausgaenge der Spielstandwahl
- **AK-125** `paths/save`, stiller Rueckfall auf die Automatik
- **AK-126** kein voller Spielstandpfad im sichtbaren Text (Konto-Kennung)
- **AK-127** keine verbotenen Woerter, Pfade nur aufgeloest (A11)
- **AK-128** alle Texte Englisch (A8)
- **AK-129** 100/125/150 % und Programmfaktoren bis 200 %, nichts abgeschnitten
- **AK-130** vollstaendig ohne Maus bedienbar
- **AK-131** das Panel erscheint nur fuer "kein Spielordner", nicht fuer
  fehlende Param-Definitionen oder Lesefehler
- **AK-132** Bildnachweise ohne echten Benutzernamen und ohne Konto-Kennung
  (NH-002, oeffentliches Repo)

## Was mir aufgefallen ist und nicht in den Auftrag gehoerte

**Ein stiller veralteter Datenabzug.** Faellt der Spielordner weg, waehrend
der Abzug von einer aelteren Programmfassung stammt, liefert
`datasource._load_data` (Zeilen 129-153) den veralteten Abzug kommentarlos
zurueck: `_regulation_matches` ist `False`, die Live-Extraktion scheitert an
`game is None`, und der Abzug wird am Ende trotzdem gereicht. Der Nutzer sieht
alte Zahlen ohne jeden Hinweis. Kein Befund dieser Spec - aber der Grund,
warum Text A3 ein Datum nennt. Ein eigener Auftrag waere sinnvoll.

**DR-006 beruehrt diesen Ablauf.** Die Regel "ein Satz in Spielersprache vor
dem technischen Grund" habe ich fuer die neuen Texte gleich mitgeschrieben
(S4). Der bestehende Bau-Fehlerdialog (`app.py:3875-3877`) bleibt davon
unberuehrt und offen.

**Ein Nebeneffekt, den der developer kennen sollte:** wird `paths/game` beim
geglueckten Automatiklauf mitgeschrieben (AK-107, Schritt 2), gewinnt der
gemerkte Pfad ab dann gegenueber der Automatik. Das ist gewollt, hat aber eine
Folge: wer zwei Installationen hat, bleibt an der ersten haengen. Das ist
genau der Grund fuer offene Frage 1.

**Der Systemdialog kommt hell, das Programm ist dunkel.** Ich habe das
ausdruecklich als kein Befund festgehalten, damit es nicht in einem spaeteren
Review als Inkonsistenz wieder aufschlaegt: der Systemdialog ist das, was der
Nutzer aus jedem anderen Programm kennt, und ein nachgebauter dunkler Dialog
verliert Schnellzugriffe, Netzlaufwerke und OneDrive.

## Offene Fragen an den App Designer

1. Soll der Spielordner auch aenderbar sein, wenn nichts kaputt ist? Diese
   Spec zeigt das Panel nur im Fehlerfall - so hat der Nutzer entschieden. Wer
   zwei Installationen hat, kann dann nicht umschalten.
2. Soll der Spielstand beim Erststart aktiv angeboten werden (Karte mit
   `Find my save...` / `Skip, I do not have one`)? Ich habe mich dagegen
   entschieden; die Karte waere sichtbarer, kostet aber jeden Spieler ohne
   Spielstand einen Klick.
3. Ist `Continue with the data from {Datum}` der richtige Ausweg, oder soll
   ein fehlender Spielordner immer blockieren?
4. Der Satz "Manage, then Browse local files" nennt die englischen
   Steam-Menuepunkte. Bei deutschem Steam heissen sie anders. Alternative:
   allgemeiner formulieren, dafuer weniger fuehren.
