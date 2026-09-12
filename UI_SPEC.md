# UI_SPEC — die geltende Oberflaechenvorgabe

**Stand:** 2026-09-12 · konsolidiert im Auftrag **T-184** (`ui-ux-designer`)
**Umfang:** 255 Akzeptanzkriterien, AK-01 bis AK-255, in sieben
Oberflaechenbereichen.

## Wie diese Datei zu lesen ist

Diese Datei traegt die **heute geltende** Fassung jedes Akzeptanzkriteriums,
geordnet nach **Oberflaechenbereich** — nicht nach Datum. Wer wissen will, was
fuer den Relic Picker gilt, liest Bereich 5 und sonst nichts.

Bis zum 12.09.2026 war sie chronologisch gewachsen: ein Abschnitt je Auftrag,
spaetere Korrekturen als Nachtrag am Ende, 9639 Zeilen in 33 Abschnitten. Wer
den geltenden Stand wissen wollte, musste die Reihenfolge selbst
rekonstruieren. Genau dagegen steht diese Fassung.

Drei Dateien, drei Fragen:

| Datei | beantwortet |
|---|---|
| `UI_SPEC.md` (diese) | **Was gilt?** — der bindende Wortlaut, nach Bereich sortiert |
| `UI_SPEC_REGISTER.md` | **Wo steht es, und was hat es abgeloest?** — eine Zeile je AK-ID, alle 255 |
| `docs/archiv/ui-spec-verlauf.md` | **Warum?** — Begruendungen, Messreihen, verworfene Varianten, Streichvorschlaege, offene Fragen, in urspruenglicher Reihenfolge |

### Was hier woertlich steht — und was nicht

- **Die Kriteriumstexte sind unveraendert uebernommen.** Kein Satz ist
  umformuliert, gekuerzt oder ergaenzt. Geaendert wurde ausschliesslich die
  **Listeneinrueckung** (aus `- **AK-01** …` wurde `**AK-01** …`), damit ein
  Kriterium mit mehreren Absaetzen, Tabellen und Messreihen lesbar bleibt.
- **Keine neuen AK-Nummern, keine neuen Kriterien.** Die Nummern laufen von
  AK-01 bis AK-255 ohne Luecke. AK-28 ist zurueckgezogen und als solches
  gefuehrt.
- **Hier ist nichts gestrichen worden, nur getrennt.** Die Begruendungen,
  Messreihen, Bildnachweise, Token-Tabellen, „ausdruecklich nicht Teil dieser
  Vorgabe"-Abschnitte und die offenen Fragen der einzelnen Auftraege stehen
  vollstaendig in `docs/archiv/ui-spec-verlauf.md`.
- **Zeilenangaben** wie `A15 Z3120` meinen: Abschnitt **A15** des Verlaufs,
  Zeile **3120 des Altstands**. In der Verlaufsdatei steht dieselbe Zeile bei
  **3120 + 69 = 3189**; der Versatz kommt vom Inhaltsverzeichnis in deren
  Kopf. Die Abschnittskennungen `A01` bis `A33` sind in
  `UI_SPEC_REGISTER.md` aufgeloest.
- **Ein Kriterium, das spaeter praezisiert wurde, traegt beide Stellen:**
  zuerst die Grundfassung, darunter unter **„Dazu A… Z… — …"** den Text, der
  sie fortschreibt. Beides zusammen ist der geltende Wortlaut.
- **`<sub>Fundstelle sinngemaess…</sub>`** heisst: das Register nennt eine
  Zeile, an der die Nummer im Fliesstext faellt; abgedruckt ist der Absatz, in
  dem sie steht. Der Wortlaut ist derselbe, die Zeilennummer ist die des
  Absatzanfangs.

### Was diese Datei nicht tut

Sie **entscheidet nichts**. Sie sortiert, was entschieden ist. Wo zwei
Fassungen nebeneinander gelten koennten und der Vorrang nicht aus dem Text
hervorgeht, stehen **beide** nebeneinander mit dem Vermerk, dass die
Entscheidung aussteht — siehe den naechsten Abschnitt.

## Die sieben Bereiche

| Bereich | worum es geht | Kriterien |
|---|---|---|
| **1** | Erststart: den Spielordner und den Spielstand waehlen | AK-106 bis AK-132, AK-230 bis AK-242, AK-246 bis AK-249, AK-253 bis AK-255 |
| **2** | Der Spielstand wird im Hintergrund gelesen | AK-220 bis AK-229, AK-243 bis AK-245, AK-250 bis AK-252 |
| **3** | Build planner: die Advisor bar | AK-01 bis AK-30 |
| **4** | Build planner: Slotkarten, festgehaltene Slots und `Optimize` | AK-31 bis AK-40, AK-54 bis AK-62 |
| **5** | Der Relic Picker | AK-41 bis AK-53, AK-195 bis AK-219 |
| **6** | Die Sprache der Zahlen: Vorschlagsblock, `Why`-Dialog, Statuszeile | AK-63, AK-67, AK-133 bis AK-194 |
| **7** | Die sechs Inhalts-Tabs | AK-64 bis AK-66, AK-68 bis AK-105 |

Die Reihenfolge folgt dem Weg eines Spielers: erst das Fenster, das ihn nach
dem Spielordner fragt, dann der Spielstand, dann der Build planner mit
Berater und Picker, zuletzt die sechs Inhalts-Tabs, die er nachschlaegt.

## Drei widerspruechliche Faelle — Entscheidung des App Designers steht aus

Beim Erstellen des Registers (T-181) sind drei Kriterien aufgefallen, bei
denen zwei Fassungen nebeneinander gelten koennten und der Vorrang **nicht**
aus dem Text hervorgeht. Sie sind hier **nicht** aufgeloest. Alle drei haengen
an derselben Sache: der Startbreite **1320 px**.

**Der Ausgangspunkt.** `A14 Z2555` (Director-Nachtrag zu AK-05, 06.09.2026,
nach T-071) hebt die feste Startbreite auf: *„Die Startbreite ist keine feste
Zahl mehr."* Verbindlich ist seither die **abgeleitete** Oeffnungsbreite
(`EffectTable.width_for_full_headings()`); das Kriterium ist nicht die
Pixelzahl, sondern die Aussage „beim Startmass ist keine Spaltenueberschrift
gekuerzt". Gemessen ergab das damals 1350 x 860 auf Windows/Fusion/150 %.

| Fall | was widerspricht |
|---|---|
| **AK-05** (A01 Z344 + A14 Z2555) | Der Erstwortlaut nennt `1320 px (Startbreite)`. A14 hebt die feste Zahl auf — aber zwei **spaetere** Kriterien schreiben sie erneut vor (AK-160, AK-194). Es steht nirgends, welche Aussage gewinnt. |
| **AK-160** (A17 Z4319, T-080) | Zwei Ungereimtheiten in einer: (1) als „schlechtester Fall" ist es durch **AK-189** (A21 Z5827, T-092) ueberholt, bleibt aber als Messung seiner Umgebung gueltig; (2) sein Messfenster lautet `bei Fensterbreite 1320 px (Startbreite)` — die es laut A14 nicht mehr gibt. |
| **AK-194** (A21 Z5780, T-092) | Verlangt die Messung der Statuszeilenbreite `bei 1320 px Fensterbreite` und leitet daraus die Schranke `≥ 105 px` ab. Auch hier ist die Bezugsbreite die aufgehobene. |

**Was zu entscheiden ist** (nicht von mir, sondern vom App Designer):
gilt `1320 px` als **Messumgebung** weiter, obwohl es als **Startbreite**
aufgehoben ist? Wenn ja, gehoert die Zahl nach L-009 mit Plattform, Stil und
Skalierung ausgeschrieben und darf nicht mehr „Startbreite" heissen. Wenn
nein, brauchen AK-160 und AK-194 eine neue Bezugsbreite, und die Schranke
`≥ 105 px` aus AK-194 muss neu abgeleitet werden.

Bis dahin gilt in dieser Datei: **beide Fassungen stehen nebeneinander**, und
jedes der drei Kriterien traegt den Vermerk.

---
## Bereich 1 — Erststart: den Spielordner und den Spielstand waehlen

Der Nutzer startet das Programm zum ersten Mal — oder der gemerkte Ordner ist
verschwunden. Dieser Bereich beschreibt das Frage-Fenster, die Aufloesungskette
zum Spielordner, die Rueckfragen, wenn der aufgeloeste Ordner nicht dort liegt,
wo der Nutzer gewaehlt hat, die Wahl des Spielstands und das, was der Erststart
ueber seine eigene Dauer sagen darf.

*Herkunft im Verlauf: A15 (T-074) · A28 (T-145) · A29 (T-146) · A32 (T-163) · A33 (T-178, Teil 2)*

### 1.1 Die Aufloesungskette und das Frage-Fenster

#### AK-106
*Verlauf: A15 Z3107 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-106** *(A15, Vorgabe "der geglueckte Fall aendert sich nicht")* Findet
Schritt 1 oder 2 der Kette aus Abschnitt 2 den Spielordner, erscheint **kein**
zusaetzliches Fenster und **kein** zusaetzlicher Klick gegenueber heute.
Pruefung: ein Lauf auf einer Maschine mit Standardinstallation zeigt genau die
Fensterfolge, die er heute zeigt.

#### AK-107
*Verlauf: A15 Z3113 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-107** Die Aufloesung des Spielordners laeuft in der Reihenfolge
gemerkter Pfad → `find_game_dir()` → Panel. Pruefung: bei ungueltigem
gemerktem Pfad und gleichzeitig auffindbarer Standardinstallation erscheint
**kein** Panel.

#### AK-108
*Verlauf: A15 Z3118 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-108** Auf einer Maschine ohne auffindbares Spiel und ohne gemerkten Pfad
erscheint das Panel aus Abschnitt 3 **statt** der heutigen
`QMessageBox.critical` aus `app.py:3883`. Pruefung: die Zeichenkette
"No ELDEN RING NIGHTREIGN installation was found." aus
`datasource._no_data_message` erreicht in diesem Fall keinen Bildschirm mehr.

#### AK-109
*Verlauf: A15 Z3124 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-109** Das Fenster im Frage-Zustand hat Titelleiste, Taskleisteneintrag
und ist verschiebbar; der Bau-Zustand bleibt wie heute. Pruefung: sichtbar am
laufenden Fenster, plus die Fensterflagge im Code.

#### AK-110
*Verlauf: A15 Z3128 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-110** Der Knopf `Choose folder...` oeffnet eine **Ordner**auswahl, keine
Dateiauswahl, und startet in dem ersten existierenden Ort aus der Liste in
4.1.

#### AK-111
*Verlauf: A15 Z3132 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-111** Waehlt der Nutzer `...\ELDEN RING NIGHTREIGN` statt
`...\ELDEN RING NIGHTREIGN\Game`, wird das Spiel gefunden und angenommen.
Dasselbe fuer den `common`- und den `steamapps`-Ordner. Die Suche besucht
hoechstens 400 Verzeichnisse und dauert hoechstens 2 Sekunden; ein
Laufwerksstamm fuehrt innerhalb dieser Grenze zu einer Ablehnung, nicht zu
einer Plattensuche.

#### AK-112
*Verlauf: A15 Z3139 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-112** Angenommen wird ein Ordner nur, wenn `regulation.bin` lesbar und
nicht leer ist, mindestens eine `data*.bhd` aus `bhd5.ARCHIVE_KEYS` vorliegt
und eine DLL aus `oodle._DLL_NAMES` vorliegt. Faellt eine der drei aus,
erscheint Text E1.

#### AK-113
*Verlauf: A15 Z3144 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-113** Traegt weder der Fundordner noch eine seiner drei Elternebenen
`NIGHTREIGN` im Namen, erscheint Text W1 mit den zwei Knoepfen, und der
Standardknopf ist `Choose a different folder...` — nicht das Weitermachen.
Der Ordner wird **nicht** abgelehnt.

#### AK-114
*Verlauf: A15 Z3149 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-114** Nach einer Ablehnung bleibt das Fenster offen, nennt den versuchten
Pfad, und der Knopf heisst `Choose a different folder...`. Das Programm endet
an dieser Stelle **nie** von selbst.

#### AK-115
*Verlauf: A15 Z3153 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-115** Bricht der Nutzer die Systemauswahl ab, kehrt er in das Panel
zurueck, in genau den Zustand, in dem er es verlassen hat. Nichts wird
gespeichert, nichts wird gemeldet.

#### AK-116
*Verlauf: A15 Z3157 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-116** `Quit`, Escape und das Fensterkreuz beenden das Programm ohne
Fehlerdialog und ohne gespeicherte Angabe. Ausnahme A3: dort fuehren Escape
und Fensterkreuz zu `Continue with the data from {Datum}`.

### 1.2 Was gemerkt wird, und was ein Fehlschlag nicht loescht

#### AK-117
*Verlauf: A15 Z3161 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-117** Ein bestaetigter Ordner steht **vor** dem Beginn des Baus in
`QSettings` unter `paths/game` (Speicher `favourites.ORG`/`favourites.APP`).
Pruefung: Programm nach der Bestaetigung waehrend des Baus hart beenden, neu
starten — es fragt nicht erneut.

#### AK-118
*Verlauf: A15 Z3166 + A28 Z8004 + A29 Z8250 · zuletzt geaendert durch T-146, 2026-09-08*

*Ueberholt: nachgezogen T-145 (A28 Z8004), dann praezisiert T-146 (A29 Z8250)*

**AK-118** *(nachgezogen am 08.09.2026, T-145, dann praezisiert am selben Tag
T-146 — die Fassung unten gilt seit T-146 wieder **unveraendert fuer C1 und
C2** (Abstieg bleibt der klickfreie Regelfall, §4.2). Nur fuer den Fall, dass
der aufgeloeste Ordner den gewaehlten Baum **verlaesst** (Aufstieg,
Zweigwechsel, Verzeichnisverknuepfung), liegt die Rueckfrage C3 davor. Siehe
AK-232 bis AK-242 im Nachtrag „AK-232 nachgezogen" am Ende dieser Datei; die
alte Fassung bleibt hier stehen, damit sichtbar ist, wovon abgewichen wird.)*
Zwischen der Bestaetigung (C1/C2) und dem Beginn des Baus liegt
**kein** weiterer Klick. Das Fenster wechselt in den Fortschrittszustand,
ohne die Breite zu aendern.

**Dazu A28 Z8004 — ergaenzt:**

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A28** — Was aus dem gewaehlten Ordner wirklich passiert, und die Rueckfrage im Fall C2 (ui-ux-designer, T-145) — 2026-09-08 (T-145, 2026-09-08)  
> Verlauf Zeile **7974 bis 8318** (Altstand Z7905 bis Z8249)

**Dazu A29 Z8250 — ergaenzt:**

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A29** — AK-232 nachgezogen: gefragt wird nur, wenn der Ordner den gewaehlten Baum verlaesst (ui-ux-designer, T-146) — 2026-09-08 (T-146, 2026-09-08)  
> Verlauf Zeile **8319 bis 8550** (Altstand Z8250 bis Z8481)

#### AK-119
*Verlauf: A15 Z3177 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-119** Gemerkter Pfad ungueltig, Automatik leer, aber
`datasource.bundled_path()` existiert: Text A3 erscheint mit dem Datum des
Abzugs, und `Continue with the data from {Datum}` fuehrt in ein voll
bedienbares Fenster mit angezeigten Zahlen.

#### AK-120
*Verlauf: A15 Z3182 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-120** Gemerkter Pfad ungueltig, Automatik leer, kein Abzug: Text A2,
zwei Knoepfe, kein dritter Weg.

#### AK-121
*Verlauf: A15 Z3185 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-121** Ein einzelner Fehlschlag loescht weder `paths/game` noch
`paths/save`. Pruefung: Laufwerk trennen, starten, `Quit`, Laufwerk wieder
anstecken, starten — es wird nicht erneut gefragt.

### 1.3 Der Spielstand im Erststart-Panel

#### AK-122
*Verlauf: A15 Z3189 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-122** Fuer den Spielstand erscheint zu **keinem** Zeitpunkt ein Modal,
das der Nutzer wegklicken muss. Pruefung: ein Erststart auf einer Maschine
ohne jeden Spielstand erreicht den Build planner ohne einen einzigen Klick
mehr als heute.

#### AK-123
*Verlauf: A15 Z3194 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-123** Ist kein Spielstand geladen, steht in der Knopfzeile neben
`Rescan save` ein sichtbarer Knopf `Find my save...`. Er oeffnet eine
**Datei**auswahl mit dem Filter aus Abschnitt 5 und startet im aufgeloesten
`Nightreign`-Ordner des Roaming-Profils, falls vorhanden. Ist ein Spielstand
geladen, ist der Knopf nicht da.

#### AK-124
*Verlauf: A15 Z3200 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-124** Die drei Ausgaenge einer Spielstandwahl sind unterscheidbar und
tragen die Texte aus Abschnitt 7: Relikte gefunden → die heutige Zeile;
lesbar ohne Relikte → S3; unlesbar → S4 mit dem Spielersatz **vor** dem
technischen Grund.

#### AK-125
*Verlauf: A15 Z3205 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-125** Eine gewaehlte Spielstanddatei wird unter `paths/save` gemerkt und
beim naechsten Start bevorzugt. Existiert sie nicht mehr, faellt das Programm
**still** auf `find_saves()` zurueck; erst wenn auch das leer ist, erscheint
S5 mit dem Knopf.

#### AK-126
*Verlauf: A15 Z3210 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-126** Kein Text dieses Ablaufs zeigt den vollen Spielstandpfad. Der
Dateiname ist erlaubt, der Ordner mit der Konto-Kennung nicht; der volle Pfad
bleibt im Tooltip, wie heute in `app.py:3242`.

#### AK-127
*Verlauf: A15 Z3214 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-127** Keiner der Texte aus Abschnitt 7 enthaelt eines der dort
aufgelisteten verbotenen Woerter. Pfade erscheinen ausschliesslich
**aufgeloest**, nie als Variablenname.

#### AK-128
*Verlauf: A15 Z3218 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-128** *(A8)* Alle Texte dieses Ablaufs sind Englisch, auch die
Knopfbeschriftungen, der Fenstertitel und der Titel des Dateidialogs.

### 1.4 Skalierung, Tastatur, Geltungsbereich

#### AK-129
*Verlauf: A15 Z3221 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-129** Bei Windows-Anzeige 100 %, 125 % und 150 % sowie bei den
Programmfaktoren bis `200%` ist in allen Zustaenden kein Text abgeschnitten,
kein Knopf ausserhalb des Fensters, und es gibt keine waagerechte
Bildlaufleiste. Pfadzeilen umbrechen. **Nachweis am laufenden Fenster mit
Bildnachweis, nicht am Code** (A13-Muster).

#### AK-130
*Verlauf: A15 Z3227 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-130** Der gesamte Ablauf ist ohne Maus bedienbar: Tab erreicht jeden
Knopf, der Fokus ist sichtbar, Enter loest den Standardknopf aus.

#### AK-131
*Verlauf: A15 Z3230 · zuletzt geaendert durch T-074, 2026-09-06 (A32 Z9053 bestaetigt: keine Aenderung)*

**AK-131** Das Panel erscheint **nur** fuer den Fall "kein Spielordner".
Fehlen die Param-Definitionen (`datasource.defs_dir()` ist `None`) oder
scheitert das Lesen einer gefundenen Installation, bleiben die heutigen
Meldungen stehen — ein Ordnerdialog waere dort die falsche Antwort.

#### AK-132
*Verlauf: A15 Z3235 · zuletzt geaendert durch T-074, 2026-09-06*

**AK-132** *(NH-002, oeffentliches Repo)* Jeder Bildnachweis dieses Panels
wird aus dem **Fenster** gezogen und zeigt einen Pfad ohne echten
Windows-Benutzernamen und ohne Steam-Konto-Kennung. Wo das nicht geht, wird
der Nachweis vorher unkenntlich gemacht.

### 1.5 Die Rueckfrage C3 — wenn der aufgeloeste Ordner den gewaehlten Baum verlaesst

#### AK-230
*Verlauf: A28 Z8138 · zuletzt geaendert durch T-145, 2026-09-08*

**AK-230** *(SEC-027)* Kein Text dieses Ablaufs sagt oder legt nahe, aus dem
gewaehlten Ordner werde ausschliesslich gelesen. **A1 und W1 sagen beide, dass
das Programm etwas aus diesem Ordner ausfuehrt.** Pruefung: der gebaute
Wortlaut von A1 und W1 ist der aus §7 in der Fassung dieses Nachtrags, Wort
fuer Wort; die Zeichenkette `It is only read` kommt im gesamten
Anwendungscode **nicht** vor.

#### AK-231
*Verlauf: A28 Z8145 · zuletzt geaendert durch T-145, 2026-09-08*

**AK-231** Die drei neuen Textstellen (A1 Absatz 3, W1 Absatz 4, C3) sind
Englisch (A8, AK-128) und enthalten **keines** der in §7 aufgelisteten
verbotenen Woerter (AK-127). Pruefung: Wortliste gegen die drei Bloecke,
Gross-/Kleinschreibung egal.

#### AK-232
*Verlauf: A29 Z8382 (T-146-Fassung, Abstand 1) + A32 Z9004 (AK-246, ab Abstand 2) · zuletzt geaendert durch T-163, 2026-09-09*

*Ueberholt: T-145-Fassung (A28 Z8150) durch die T-146-Fassung - A29 Z8382; deren Satz `innerhalb = kein C3` ab zwei Ebenen Abstand durch AK-246 - A32 Z9004 (T-163)*

**AK-232** *(C3 nur beim Verlassen des Baumes, nachgezogen T-146 — seit
09.09.2026, T-163/SEC-032, gilt der Satz „liegt der aufgeloeste Ordner
innerhalb des gewaehlten, erscheint kein C3" **nur noch bis einschliesslich
einer Ebene Abstand**. Ab zwei Ebenen gilt AK-246 im Nachtrag „SEC-032
nachgezogen" am Ende dieser Datei; die Fassung unten bleibt fuer den
Abstand-1-Fall unveraendert gueltig.)* Verlaesst
der aufgeloeste Ordner den gewaehlten Baum (Aufstieg, Zweigwechsel oder eine
Verzeichnisverknuepfung, die aus dem Baum herausfuehrt), erscheint **vor** dem
Bau der Zustand C3 und zeigt **beide** Pfade vollstaendig, jeder mit seiner
Beschriftung. Liegt der aufgeloeste Ordner dagegen **innerhalb** des
gewaehlten (Abstieg, §4.2), erscheint **kein** C3. Pruefung: einen Unterordner
**innerhalb** des Ordners waehlen, der `regulation.bin` direkt enthaelt, so
dass die Aufloesung um eine Ebene nach oben steigen muss (§4.2) — C3
erscheint, der Bau beginnt nicht, keine Fortschrittsanzeige ist zu sehen.
Gegenprobe: den **Elternordner** der Installation waehlen (Abstieg,
Regelfall) — **kein** C3, C2 erscheint sofort, der Bau beginnt ohne weiteren
Klick.

**Dazu A32 Z9004 — AK-246, ab Abstand 2:**

**AK-246** *(SEC-032 — die klickfreie Zustimmung reicht nur eine Ebene weit)*
Liegt der aufgeloeste Ordner **innerhalb** des gewaehlten und ist er davon
**genau eine** Ebene entfernt, erscheint **kein** C3: sofort C2, dann der
Bau-Zustand, wie in AK-232/AK-240 beschrieben. Ist er **zwei oder mehr**
Ebenen entfernt, erscheint **C3** vor dem Bau, mit dem Wortlaut aus §3 oben.
Pruefung: einen Ordner waehlen, dessen direktes Kind `regulation.bin` traegt
(Abstand 1) — kein C3, C2 direkt.
Gegenprobe: den Elternordner davon waehlen (Abstand 2) — C3 erscheint mit
beiden Pfaden, der Bau beginnt nicht, keine Fortschrittsanzeige ist zu sehen.
Zweite Gegenprobe (Grenzfall): drei Ordnerebenen ueber der Installation waehlen
(Abstand 3, das Ende von `SEARCH_DEPTH`) — ebenfalls C3, nicht E1: der Ordner
wird gefunden, nur nicht mehr stillschweigend angenommen.

<sub>Fundstelle sinngemaess: das Register nennt Z9004; hier steht der Absatz ab Z9004 (Verlauf Z9073).</sub>

#### AK-233
*Verlauf: A28 Z8164 · zuletzt geaendert durch T-145, 2026-09-08 (A29 Z8371 und A32 Z9042: unveraendert)*

**AK-233** *(C1 unberuehrt, A15/AK-106)* Ist der aufgeloeste Ordner gleich dem
gewaehlten, erscheint **kein** C3 und **kein** zusaetzlicher Klick: C1, dann
sofort der Bau-Zustand. Pruefung: den Ordner waehlen, der `regulation.bin`
direkt enthaelt — die Fensterfolge ist die aus AK-118 in seiner alten Fassung.
*(T-146: unveraendert gueltig, siehe Nachtrag am Ende der Datei.)*

#### AK-234
*Verlauf: A28 Z8170 · zuletzt geaendert durch T-146, 2026-09-08*

*Ueberholt: T-145-Fassung nachgezogen - A28 Z8170 (T-146)*

**AK-234** *(nachgezogen am 08.09.2026, T-146 — die Zeile, die nach `Use this
folder` erscheint, ist seit der Praezisierung **nicht** mehr die Zeile C2:
deren Wortlaut „inside the folder you picked" ist fuer einen Verlassen-Fall
falsch. Neue Fassung im Nachtrag am Ende der Datei; die alte bleibt hier
stehen.)*
In C3 ist `Use this folder` der Standardknopf und wird von Enter
ausgeloest; danach erscheint die vorhandene Zeile C2 und der Bau beginnt
**ohne weiteren Klick**. Pruefung: C3 nur ueber die Tastatur beantworten.

#### AK-235
*Verlauf: A28 Z8179 · zuletzt geaendert durch T-145, 2026-09-08*

**AK-235** `Choose a different folder...` in C3 oeffnet erneut den
Systemordnerdialog, dessen Startort der **zuvor gewaehlte** Ordner ist. Wird
der Systemdialog abgebrochen, steht wieder C3 mit denselben zwei Pfaden.
Pruefung: zweimal hintereinander abbrechen — das Fenster bleibt in C3, und es
wird nichts gemeldet und nichts gespeichert. *(T-146: unveraendert gueltig.)*

#### AK-236
*Verlauf: A28 Z8185 · zuletzt geaendert durch T-145, 2026-09-08*

**AK-236** *(nichts vor der Antwort)* Solange C3 offen ist, ist `paths/game`
unveraendert. Pruefung: in C3 das Programm hart beenden und neu starten — es
fragt erneut, und ein zuvor gemerkter Pfad steht noch auf seinem alten Wert.
*(T-146: unveraendert gueltig.)*

#### AK-237
*Verlauf: A29 Z8400 · zuletzt geaendert durch T-146, 2026-09-08*

*Ueberholt: T-145-Fassung (A28 Z8190) nachgezogen - A29 Z8400 (T-146); A32 Z9046 bestaetigt sie fuer den neuen Ausloeser*

**AK-237** *(hoechstens eine Rueckfrage je Wahl, nachgezogen T-146 — die
Garantie gilt seit 09.09.2026, T-163, unveraendert auch fuer den neuen
C3-Ausloeser „Abstand ≥ 2 Ebenen" aus AK-246; siehe AK-248 im Nachtrag
„SEC-032 nachgezogen".)* Wurde W1
mit `Use this folder anyway` beantwortet, erscheint **kein** C3, auch wenn der
aufgeloeste Ordner den gewaehlten Baum verlaesst. Pruefung: einen umbenannten
Spielordner ueber einen seiner **eigenen Unterordner** waehlen (der
Namenscheck in Stufe 2 schlaegt fehl **und** die Aufloesung muss aufsteigen,
also waere ohne W1 zusaetzlich C3 faellig) — es kommt genau **ein**
Frage-Zustand (W1), nicht zwei.

#### AK-238
*Verlauf: A28 Z8200 · zuletzt geaendert durch T-145, 2026-09-08*

**AK-238** Escape und das Fensterkreuz beenden aus C3 heraus das Programm ohne
Fehlerdialog und ohne gespeicherte Angabe, wie in A1, A2, E1 und W1 (§9).

#### AK-239
*Verlauf: A28 Z8203 · zuletzt geaendert durch T-145, 2026-09-08*

**AK-239** *(Skalierung, Nachweis am Fenster)* Bei Windows-Anzeige 100 %,
125 % und 150 % sowie bei den Programmfaktoren bis `200%` ist in A1, W1 und C3
kein Text abgeschnitten, kein Knopf ausserhalb des Fensters, und es gibt keine
waagerechte Bildlaufleiste; die beiden Pfadzeilen in C3 brechen um, statt die
Breite von `460` logischen px zu sprengen. **Nachweis am laufenden Fenster,
aus dem Fenster gezogen** (AK-129/AK-132-Muster, NH-002).

#### AK-240
*Verlauf: A29 Z8413 · zuletzt geaendert durch T-146, 2026-09-08*

**AK-240** *(Abstieg loest kein C3 mehr aus — die Korrektur der T-145-Annahme
— **eingeschraenkt am 09.09.2026, T-163/SEC-032**: „Abstieg bis Tiefe 3"
loest hier noch pauschal kein C3 aus; seit AK-246 gilt das nur noch fuer
Abstand 1. Ein Abstieg auf Abstand 2 oder 3 loest seither C3 aus, siehe den
Nachtrag „SEC-032 nachgezogen". Die Fassung unten bleibt fuer den
Abstand-1-Fall unveraendert gueltig.)*
Liegt der aufgeloeste Ordner innerhalb des gewaehlten (§4.2, Abstieg bis Tiefe
3), erscheint **zwischen** der Ordnerwahl und dem Bau-Zustand **kein**
zusaetzliches Fenster und **kein** zusaetzlicher Klick gegenueber der Fassung
vor T-145 — die Fensterfolge ist die aus AK-118 in seiner alten Fassung.
Pruefung: den Elternordner der Installation waehlen (`...\common` statt
`...\common\NIGHTREIGN`) — C2 erscheint direkt, kein C3 dazwischen.

#### AK-241
*Verlauf: A29 Z8426 · zuletzt geaendert durch T-146, 2026-09-08*

**AK-241** *(C3 nennt das Verlassen ausdruecklich — **Wortlaut seit
09.09.2026, T-163/SEC-032, erneut geaendert**, siehe AK-247 im Nachtrag
„SEC-032 nachgezogen"; die hier genannte Fassung war von T-146 bis T-163
gueltig.)* Der gebaute Wortlaut von
C3 enthaelt fuer die zweite Pfadzeile die Beschriftung `The game itself is
outside that folder, in:`, nicht die neutrale Fassung aus dem T-145-Abschnitt.
Pruefung: Wortlautvergleich gegen §2 dieses Nachtrags.

#### AK-242
*Verlauf: A29 Z8434 · zuletzt geaendert durch T-146, 2026-09-08 (A32 Z9046: unveraendert)*

**AK-242** *(die Zeile nach C3 ist C1, nicht C2)* Nach `Use this folder` in C3
erscheint der Wortlaut `Found your game in {Pfad}` ohne den Zusatz `, inside
the folder you picked.`. Pruefung: den in AK-240 beschriebenen Aufstiegsfall
ausloesen, C3 mit `Use this folder` bestaetigen — der angezeigte Satz behauptet
an keiner Stelle, der Fund liege innerhalb des gewaehlten Ordners.

### 1.6 SEC-032 — ab zwei Ebenen Abstand wird gefragt

#### AK-246
*Verlauf: A32 Z9004 · zuletzt geaendert durch T-163, 2026-09-09*

**AK-246** *(SEC-032 — die klickfreie Zustimmung reicht nur eine Ebene weit)*
Liegt der aufgeloeste Ordner **innerhalb** des gewaehlten und ist er davon
**genau eine** Ebene entfernt, erscheint **kein** C3: sofort C2, dann der
Bau-Zustand, wie in AK-232/AK-240 beschrieben. Ist er **zwei oder mehr**
Ebenen entfernt, erscheint **C3** vor dem Bau, mit dem Wortlaut aus §3 oben.
Pruefung: einen Ordner waehlen, dessen direktes Kind `regulation.bin` traegt
(Abstand 1) — kein C3, C2 direkt.
Gegenprobe: den Elternordner davon waehlen (Abstand 2) — C3 erscheint mit
beiden Pfaden, der Bau beginnt nicht, keine Fortschrittsanzeige ist zu sehen.
Zweite Gegenprobe (Grenzfall): drei Ordnerebenen ueber der Installation waehlen
(Abstand 3, das Ende von `SEARCH_DEPTH`) — ebenfalls C3, nicht E1: der Ordner
wird gefunden, nur nicht mehr stillschweigend angenommen.

#### AK-247
*Verlauf: A32 Z9017 · zuletzt geaendert durch T-163, 2026-09-09*

**AK-247** *(C3-Wortlaut behauptet fuer keinen seiner beiden Ausloeser die
falsche Richtung)* Der gebaute Wortlaut von C3 enthaelt fuer die zweite
Pfadzeile die Beschriftung `The game itself is not directly in that folder.
It is in:`, nicht mehr `outside that folder, in:` aus der T-146-Fassung.
Pruefung: Wortlautvergleich gegen §3 dieses Nachtrags — sowohl im
Verlassen-Fall (Aufstieg) als auch im Abstand-≥-2-Fall (Abstieg) steht exakt
derselbe Text.

#### AK-248
*Verlauf: A32 Z9025 · zuletzt geaendert durch T-163, 2026-09-09*

**AK-248** *(hoechstens eine Rueckfrage je Wahl, gilt auch fuer den neuen
Ausloeser)* Faellt der Namenscheck (Stufe 2, W1) mit einem Abstand ≥ 2
zusammen, gewinnt weiterhin W1: wird es mit `Use this folder anyway`
beantwortet, erscheint **kein** zusaetzliches C3, obwohl der Abstand das ohne
W1 ausloesen wuerde. Pruefung: einen umbenannten Installationsordner ueber
seinen **Elternordner** (Abstand 2, Name ohne `NIGHTREIGN`) waehlen — es
kommt genau **ein** Frage-Zustand (W1), nicht zwei. Erweitert AK-237 um den
neuen Ausloeser, ersetzt ihn nicht.

#### AK-249
*Verlauf: A32 Z9034 · zuletzt geaendert durch T-163, 2026-09-09*

**AK-249** *(`SEARCH_DEPTH`/`SEARCH_PARENTS` unveraendert)* Diese Entscheidung
aendert keine Konstante in `nrdata/gamefiles.py`: `SEARCH_DEPTH` bleibt `3`,
`SEARCH_PARENTS` bleibt `2`. Was sich aendert, ist ausschliesslich, ab welchem
Ergebnis der Suche das Fenster fragt statt still zu uebernehmen. Pruefung:
Diff dieses Nachtrags beruehrt keine Zeile in `nrdata/gamefiles.py`.

### 1.7 Der Erststart verspricht keine Dauer, die er nicht halten kann

#### AK-253
*Verlauf: A33 Z9516 · zuletzt geaendert durch T-178, 2026-09-09*

**AK-253** *(der Erststart verspricht keine Dauer, die er nicht halten kann)*
Die Erklaerzeile des Bau-Zustands traegt woertlich **W-A** (Erststart) bzw.
**W-B** (Neuaufbau), und der Absatz W1 traegt woertlich **W-C** (§8). **Kein**
Text, der in `nrplanner/firstrun.py` auf den Bildschirm kommt, nennt eine
feste Dauer.
*Waechter:* Suche ueber die Anzeigetexte des Moduls nach `about a minute`,
`takes a minute` und einer Ziffer unmittelbar vor `second`, `minute` oder
`hour` — **kein** Treffer.
*Positivkontrolle:* dieselbe Suche gegen den **heutigen** Wortlaut **muss**
zweimal anschlagen (Erklaerzeile und W1) — sonst sammelt sie die Texte nicht
ein, die sie zu sammeln vorgibt.
*Toetende Mutation:* „about a minute" wieder einsetzen.

#### AK-254
*Verlauf: A33 Z9529 · zuletzt geaendert durch T-178, 2026-09-09*

**AK-254** *(kein erfundener Fortschritt — und die gelobte Zeile bleibt)* Der
Balken des Bau-Zustands hat Minimum und Maximum **beide 0** und keinen
sichtbaren Text. Im Fenster steht kein Prozentwert, keine Restzeit, keine
verstrichene Zeit und keine Schrittzaehlung. Jede Meldung, die der Bau abgibt,
erscheint weiter **woertlich und in derselben Reihenfolge** in der Zeile unter
dem Balken.
*Aufbau:* ein Bau mit einer Vorrichtung, die die heutigen Meldungen der Reihe
nach abgibt; die Zeile traegt sie in dieser Reihenfolge — **Zaehlwert gegen
ein Literal**: so viele Meldungen abgegeben wie angezeigt.
*Toetende Mutation:* dem Balken einen Bereich geben und ihn aus der
Schrittliste treiben — er steht dann fuer den groesseren Teil der Wartezeit
auf 0 und springt.

#### AK-255
*Verlauf: A33 Z9542 · zuletzt geaendert durch T-178, 2026-09-09*

**AK-255** *(nichts ist abgeschnitten, an keiner Skalierung)* Die Hoehe des
Bau-Zustands folgt seinem Inhalt bei `PANEL_WIDTH` und ist nie kleiner als
heute (Erststart bzw. Neuaufbau, zuzueglich der Bestaetigungszeile wie
bisher). Bei 100 %, 125 % und 150 % Anzeigeskalierung ist die Erklaerzeile
vollstaendig zu lesen — dieselbe Pruefung, die **AK-129** fuer die
Frage-Zustaende verlangt.
*Messauflage an den `developer` (L-009):* er nennt die gemessene Hoehe beider
Bau-Zustaende mit ihrer Umgebung (Qt-Stil, Anzeigeskalierung, physisch oder
logisch).
*Toetende Mutation:* die festen Hoehen stehen lassen — der laengere Satz wird
unten abgeschnitten.

---

## Bereich 2 — Der Spielstand wird im Hintergrund gelesen

Das Fenster ist vor dem Spielstand da. Dieser Bereich beschreibt den dritten
Fensterzustand — das Warten —, was in ihm gesperrt ist und was nicht, welche
Saetze die Spielstandzeile am Ende eines Lesens tragen darf, und wie die
Gesamtzahl der besessenen Relikte angezeigt wird.

*Herkunft im Verlauf: A26 (T-141) · A27 (T-141) · A30 (T-148) · A31 (T-154) · A33 (T-178, Teil 1)*

### 2.1 Warten, Ankommen, Rueckfallsaetze

#### AK-220
*Verlauf: A26 Z7705 · zuletzt geaendert durch T-141, 2026-09-08*

**AK-220** *(das Fenster ist vor dem Spielstand da.)* Wird das Programm mit
einem Lesen gestartet, das nie antwortet, so steht das Hauptfenster
trotzdem: sichtbar, mit Titel, in der Taskleiste; und Nightfarer-Liste,
Stufe, Kelchliste, `Deep of Night` sowie **jeder Tab ausser dem Reliktteil
des `Build planner`** sind vollstaendig gefuellt und bedienbar. Kein
Anstrich des Fensters wartet auf den Spielstand.
*Toetende Mutation:* das Lesen wieder vor `window.show()` legen — es
erscheint dann kein Fenster.

#### AK-221
*Verlauf: A26 Z7713 · zuletzt geaendert durch T-141, 2026-09-08*

**AK-221** *(der Wartezustand ist ein Zustand, kein Nichts.)* Waehrend eines
Lesens, das nie antwortet, gilt dauerhaft: die Spielstandzeile traegt
**woertlich** einen der beiden Saetze aus §9 (a)/(b) und **nichts sonst** —
beim Start (a), sonst (b); beim Start traegt jede **leere** Slotkarte die
eine Zeile aus §9 (c); und im ganzen Fenster gibt es keinen
Fortschrittsbalken, keinen Wartecursor, keinen Spinner, keine animierten
Punkte, keinen zweiten Dialog, keine Statusleiste, keine Zeitschwelle und
keinen Verzoegerungstimer.
*Toetende Mutation:* die Zeile waehrend des Lesens leer lassen — dann ist
der Zustand von „kein Spielstand" nicht zu unterscheiden.

#### AK-222
*Verlauf: A26 Z7723 · zuletzt geaendert durch T-141, 2026-09-08*

**AK-222** *(keine Zahl, die noch niemand kennt, und keine Aussage ueber
einen ungelesenen Bestand.)* Solange kein Bestand vorliegt, traegt keine
Slotueberschrift die Klammer `(n available)`; nirgends im Fenster steht eine
Zaehlung von Relikten, eine Rangfolge, ein `BEST FOR …`-Chip, einer der
Saetze `Nothing you own raises …` oder der Satz aus §9 (f). Mit der Ankunft
des Bestands steht die Zaehlung in jeder Slotueberschrift.
*Toetende Mutation:* die Klammer waehrend des Lesens mit `0` stehen lassen.

#### AK-223
*Verlauf: A26 Z7730 + A30 Z8545 (AK-243 praezisiert) · zuletzt geaendert durch T-148, 2026-09-09*

**AK-223** *(gesperrt ist genau eines — nachgezogen am 09.09.2026, T-148:
in Wahrheit sind es zwei, aus verschiedenen Gruenden. Siehe **AK-243** im
Nachtrag „drei Praezisierungen" am Ende dieser Datei; die alte Fassung
bleibt hier stehen, damit sichtbar ist, wovon abgewichen wird.)* Im Zustand
aus AK-221 ist der
Reliktknopf (`choose_button`) jeder Slotkarte gesperrt und oeffnet keinen
Picker; **jedes andere** Bedienelement des Fensters ist freigegeben
(`isEnabled()`) und nicht ausgegraut — namentlich Nightfarer-Liste, Stufe,
Kelchliste, `Deep of Night`, `Hold`, `Rescan save`, `Load equipped`, die
Bereichsteiler und jeder Tab. Der Reliktknopf ist freigegeben, sobald der
Bestand da ist. Das Fenster traegt keinen Wartecursor.
*Toetende Mutation:* das ganze `Build planner`-Feld sperren; oder den
Reliktknopf offen lassen — dann oeffnet sich ein Picker ohne Relikte.

**Dazu A30 Z8545 — AK-243 praezisiert:**

**AK-243** *(gesperrt sind zwei, aus verschiedenen Gruenden — praezisiert
AK-223)* Im Zustand aus AK-221 sind zwei Bedienelemente gesperrt: der
Reliktknopf (`choose_button`) jeder Slotkarte — wie AK-223 es beschreibt —
und `AdvisorBar.optimize_button` (`nrplanner/advisorbar.py:484`, im
Reliktteil des `Build planner`). Beide sind `isEnabled() == False`; jedes in
AK-223 „namentlich" genannte uebrige Bedienelement bleibt freigegeben, wie
dort beschrieben. Der Reliktknopf wird frei, sobald das Lesen endet, gleich
auf welchem der vier Wege aus §6. `optimize_button` wird frei, sobald `owned`
zum ersten Mal seit dem letzten Verlust nicht mehr `None` ist — das schliesst
das Ende „kein Spielstand gefunden" **aus**: dort bleibt `optimize_button`
gesperrt, solange kein Bestand vorliegt, auch nachdem das Lesen laengst zu
Ende ist. Die Statuszeile der Advisor-Leiste traegt in diesem Fenster
`4.1`/`4.8` unveraendert nach eigener Spezifikation und ist nicht Gegenstand
dieses Kriteriums.
*Aufbau:* dieselben fuenf Vorrichtungen wie AK-221 (nie antwortendes, sofort
antwortendes, langsames, scheiterndes, kein-Spielstand-Lesen); zusaetzlich
`optimize_button.isEnabled()` in jedem Endzustand gepruef, nicht nur waehrend
des Lesens.
*Toetende Mutation:* `optimize_button` waehrend AK-221 freigeben — ein Druck
zeigt dann `No save was read, so there are no relics to choose from — use
Rescan save.`, waehrend tatsaechlich gerade gelesen wird.

<sub>Fundstelle sinngemaess: das Register nennt Z8545; hier steht der Absatz ab Z8545 (Verlauf Z8614).</sub>

#### AK-224
*Verlauf: A26 Z7743 + A30 Z8609 (AK-244 zieht nach) · zuletzt geaendert durch T-148, 2026-09-09*

**AK-224** *(der Wartesatz ist nie das letzte Wort — nachgezogen am
09.09.2026, T-148: es gibt einen fuenften Satz, der beim ersten
erfolgreichen Lesen die Bestandsnotiz ueberschreiben kann. Siehe **AK-244**
im Nachtrag „drei Praezisierungen" am Ende dieser Datei; die alte Fassung
bleibt hier stehen, damit sichtbar ist, wovon abgewichen wird.)* Jedes Lesen
endet in
einem Zustand, in dem die Spielstandzeile **einen der vier Saetze aus §6**
traegt — die Bestandsnotiz, die Notiz mit dem Zusatz aus §9 (d), den Satz
„kein Spielstand" oder `Save could not be read: <reason>`. **Ein Ende, nach
dem die Zeile noch einen Wartesatz traegt, ist ein Fehler** — gleich auf
welchem Weg es geendet ist; die Aufzaehlung der Enden ist diesem Satz
nachgeordnet und waechst mit.
*Aufbau:* vier Vorrichtungen, je eine je Ende.
*Toetende Mutation:* den Fehlerfall nicht behandeln — die Zeile bleibt beim
Wartesatz stehen.

**Dazu A30 Z8609 — AK-244 zieht nach:**

**AK-244** *(der Wartesatz ist nie das letzte Wort — und manchmal ist es ein
fuenftes. **Zweite Haelfte nachgezogen am 09.09.2026, T-154:** der `developer`
hat in T-149 belegt (`app.py:4079` seinerzeit, heute `load_equipped`s
Erfolgszweig bis `app.py:4320`), dass die Behauptung „scheitert das
automatische Uebernehmen nicht, bleibt die Bestandsnotiz stehen" **nicht
zutrifft** — es gibt einen sechsten, tatsaechlich eine offene Familie von
Saetzen, die auch der **gelungene** Weg ueber die Notiz schreibt. Siehe

<sub>Fundstelle sinngemaess: das Register nennt Z8609; hier steht der Absatz ab Z8609 (Verlauf Z8678).</sub>

#### AK-225
*Verlauf: A26 Z7758 · zuletzt geaendert durch T-141, 2026-09-08*

**AK-225** *(die Ankunft bewegt nichts.)* Ueber den Wechsel vom
Wartezustand zur Bestandsnotiz hinweg sind `width()` und `height()` des
Fensters identisch, die Bereichsbreiten sind identisch, und das
Bedienelement mit dem Tastaturfokus behaelt ihn. Die Spielstandzeile schiebt
dabei nichts nach unten: sie ist im Wartezustand mindestens so hoch wie die
Bestandsnotiz, die sie abloest.
*Messauflage an den `developer` (L-009):* er misst die Hoehe der
Spielstandzeile im Wartezustand und mit der gewoehnlichen Bestandsnotiz an
der **Vorgabebreite des linken Bereichs** und nennt **beide Zahlen mit ihrer
Umgebung** (Qt-Stil, Windows-Anzeigeskalierung, physisch oder logisch,
Bestand des Nutzers). Ist die Wartefassung niedriger, wird ihre Hoehe auf die
groessere gesetzt — der Text wird nicht verlaengert.
*Ausdrueckliche Ausnahme:* die beiden langen Enden — der Zusatz aus §9 (d)
und der Fehlersatz — duerfen hoeher ausfallen; sie sind heute schon die
hoechsten Faelle dieser Zeile.
*Toetende Mutation:* die Wartefassung auf eine Zeile festnageln, waehrend
die Notiz zwei braucht.

#### AK-226
*Verlauf: A26 Z7775 · zuletzt geaendert durch T-141, 2026-09-08*

**AK-226** *(kein nachtraegliches Ueberschreiben.)* Hat der Spieler zwischen
dem ersten Anstrich und der Ankunft des Bestands einen Slot selbst
veraendert, so steht nach der Ankunft in jedem Slot **das**, was er
hineingetan hat; das im Spielstand gespeicherte Build wird dann in dieser
Sitzung **weder bei der Ankunft noch bei einem spaeteren Wechsel des
Nightfarers** von selbst uebernommen. Hat er nichts veraendert, steht nach
der Ankunft dasselbe wie nach einem synchronen Lesen.
*Aufbau:* zwei Vorrichtungen mit einem Spielstand, der ein gespeichertes
Build hat — eine, in der zwischen Anstrich und Ankunft ein Slot gesetzt
wird, und eine ohne Eingriff; in der ersten danach zusaetzlich einmal den
Nightfarer wechseln und zurueck.
*Toetende Mutation:* die Uebernahme bei der Ankunft ueberspringen, ohne sie
als erledigt zu vermerken — sie faellt dann beim naechsten
Nightfarer-Wechsel unerwartet ueber die Slots her.

#### AK-227
*Verlauf: A26 Z7789 · zuletzt geaendert durch T-141, 2026-09-08*

**AK-227** *(ein Lesen zur Zeit, und es ist zu sehen.)* Wird `Rescan save`
waehrend eines laufenden Lesens gedrueckt, aendert sich nichts auf dem
Bildschirm: die Zeile traegt weiter denselben Satz, die Slots stehen
unveraendert, und es laeuft kein zweites Lesen — **Zaehlwert gegen ein
Literal**: der Spielstand ist genau **einmal** gelesen worden.
*Toetende Mutation:* je Druck ein Lesen starten.

#### AK-228
*Verlauf: A26 Z7795 · zuletzt geaendert durch T-141, 2026-09-08*

**AK-228** *(der langsame Weg ist kein Fehlschlag.)* Meldet das Lesen, dass
es auf dem alten Weg gelesen hat, so steht in der Spielstandzeile die
**vollstaendige Bestandsnotiz** und daran der Zusatz aus §9 (d), woertlich;
die Reliktzahl ist dieselbe, die derselbe Spielstand auf dem schnellen Weg
ergibt; kein Slot ist leer, der es sonst nicht waere; und im ganzen Fenster
erscheint dabei **kein** Dialog, kein Ausrufezeichen, keine Farbe ausser
`MUTED` und keines der Woerter `error`, `failed`, `warning`, `corrupt`.
*Aufbau:* dieselben Spielstanddaten zweimal gelesen, einmal auf jedem Weg;
die Reliktzahl beider Laeufe wird gegeneinander gestellt.
*Toetende Mutation:* die Id-Pruefung wieder werfen lassen — die Zeile traegt
dann den Fehlersatz statt der Notiz, und die Relikte fehlen.

#### AK-229
*Verlauf: A26 Z7806 · zuletzt geaendert durch T-141, 2026-09-08*

**AK-229** *(das Praefix behaelt seine Bedeutung — eine Eigenschaft, keine
Fundstelle. **Vermerk 09.09.2026, T-148:** bis AK-228 gebaut ist, gilt diese
Eigenschaft mit einer benannten, befristeten Ausnahme — siehe den Vermerk im
Nachtrag „drei Praezisierungen" am Ende dieser Datei. Keine neue AK-Nummer,
keine Aenderung des Textes unten.)* Der Satzanfang `Save could not be read: ` erscheint **nur**,
wenn am Ende des Lesens kein Bestand vorliegt. Kein Text, der hinter diesem
Praefix landen kann, sagt, dass mit dem Spielstand alles in Ordnung sei oder
dass nichts fehle.
*Aufbau:* alle Texte einsammeln, die auf diesem Weg in die Zeile geraten
koennen, und gegen eine Wortliste stellen (`nothing is wrong`,
`nothing is missing`, `nothing needs fixing`).
*Positivkontrolle, ohne die der Waechter nur sein eigenes Pruefmittel
misst:* dieselbe Pruefung gegen den **heutigen** Wortlaut der Id-Pruefung
(`… nothing is wrong with the save.`) **muss** anschlagen — sonst sammelt
die Vorrichtung die Texte nicht ein, die sie zu sammeln vorgibt.
*Toetende Mutation:* den Rueckfallsatz wieder als Ausnahme werfen.

### 2.2 Das zweite gesperrte Element und der fuenfte Satz

#### AK-243
*Verlauf: A30 Z8545 · zuletzt geaendert durch T-148, 2026-09-09*

**AK-243** *(gesperrt sind zwei, aus verschiedenen Gruenden — praezisiert
AK-223)* Im Zustand aus AK-221 sind zwei Bedienelemente gesperrt: der
Reliktknopf (`choose_button`) jeder Slotkarte — wie AK-223 es beschreibt —
und `AdvisorBar.optimize_button` (`nrplanner/advisorbar.py:484`, im
Reliktteil des `Build planner`). Beide sind `isEnabled() == False`; jedes in
AK-223 „namentlich" genannte uebrige Bedienelement bleibt freigegeben, wie
dort beschrieben. Der Reliktknopf wird frei, sobald das Lesen endet, gleich
auf welchem der vier Wege aus §6. `optimize_button` wird frei, sobald `owned`
zum ersten Mal seit dem letzten Verlust nicht mehr `None` ist — das schliesst
das Ende „kein Spielstand gefunden" **aus**: dort bleibt `optimize_button`
gesperrt, solange kein Bestand vorliegt, auch nachdem das Lesen laengst zu
Ende ist. Die Statuszeile der Advisor-Leiste traegt in diesem Fenster
`4.1`/`4.8` unveraendert nach eigener Spezifikation und ist nicht Gegenstand
dieses Kriteriums.
*Aufbau:* dieselben fuenf Vorrichtungen wie AK-221 (nie antwortendes, sofort
antwortendes, langsames, scheiterndes, kein-Spielstand-Lesen); zusaetzlich
`optimize_button.isEnabled()` in jedem Endzustand gepruef, nicht nur waehrend
des Lesens.
*Toetende Mutation:* `optimize_button` waehrend AK-221 freigeben — ein Druck
zeigt dann `No save was read, so there are no relics to choose from — use
Rescan save.`, waehrend tatsaechlich gerade gelesen wird.

#### AK-244
*Verlauf: A30 Z8609 (erste Haelfte) + A31 Z8828 (AK-245 fuer die zweite) · zuletzt geaendert durch T-154, 2026-09-09*

*Ueberholt: zweite Haelfte durch AK-245 - A31 Z8828 (T-154); erste Haelfte unveraendert gueltig*

**AK-244** *(der Wartesatz ist nie das letzte Wort — und manchmal ist es ein
fuenftes. **Zweite Haelfte nachgezogen am 09.09.2026, T-154:** der `developer`
hat in T-149 belegt (`app.py:4079` seinerzeit, heute `load_equipped`s
Erfolgszweig bis `app.py:4320`), dass die Behauptung „scheitert das
automatische Uebernehmen nicht, bleibt die Bestandsnotiz stehen" **nicht
zutrifft** — es gibt einen sechsten, tatsaechlich eine offene Familie von
Saetzen, die auch der **gelungene** Weg ueber die Notiz schreibt. Siehe

**Dazu A31 Z8828 — AK-245 fuer die zweite:**

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A31** — AK-244 nachgezogen: die Regel statt der Liste, und der Widerspruch bei S5 (ui-ux-designer, T-154) — 2026-09-09 (T-154, 2026-09-09)  
> Verlauf Zeile **8787 bis 8950** (Altstand Z8718 bis Z8881)

#### AK-245
*Verlauf: A31 Z8828 · zuletzt geaendert durch T-154, 2026-09-09*

**AK-245** *(load_equipped gewinnt immer, wenn es angestossen wird — ersetzt
die zweite Haelfte von AK-244)* Loest ein Lesen das automatische Uebernehmen
des ausgeruesteten Builds aus (Bedingung wie AK-244/§2 oben), so traegt die
Spielstandzeile am Ende **den Text, den `load_equipped()` selbst zuletzt in
`owned_label` geschrieben hat** — nie den Wartesatz, nie eine
Bestandsnotiz-Grundform aus §9 (e), nie eine Mischung, nie einen leeren Text.
Das gilt **unabhaengig davon, ob das Uebernehmen gelingt oder scheitert.**
Loest das Lesen das automatische Uebernehmen **nicht** aus, gilt AK-224
unveraendert.
*Aufbau:* wie AK-244 (drei Vorrichtungen fuer die scheiternden Zweige aus
§2 des T-148-Nachtrags), zusaetzlich **eine vierte** mit einem tatsaechlich
uebernehmbaren Build — dort darf `owned_label` am Ende **nicht** die
Bestandsnotiz zeigen, sondern muss mit `"Loaded "` beginnen.
*Toetende Mutation:* im Erfolgszweig `self.owned_label.setText(note)`
(`app.py:4320`) durch ein No-op ersetzen — die Bestandsnotiz bliebe dann
stehen, und ein Waechter, der nur die drei Fehlertexte aus AK-244 erwartet,
faende den Fehler nicht.

### 2.3 Die Gesamtzahl der Relikte

#### AK-250
*Verlauf: A33 Z9469 · zuletzt geaendert durch T-178, 2026-09-09*

**AK-250** *(die Gesamtzahl hat eine Zeile, die ihr gehoert)* Im
`Build planner` steht die Besitzzahl in einem **eigenen** Widget des linken
Bereichs, oberhalb der Knopfzeile `Rescan save` / `Load equipped`, **nicht**
in `owned_label`. Nachdem eine der Meldungen gelaufen ist, die heute die
Spielstandzeile ueberschreiben, traegt diese Zeile **unveraendert** dieselbe
Zahl.
*Aufbau:* ein Fenster mit gelesenem Bestand; nacheinander die vier
`load_equipped`-Enden mit vorhandenem Bestand ausloesen —
`Loaded <hero> — …`, `This save's stored builds could not be read: …`,
`This save stores no equipped loadout for <hero>.` und
`<hero> has vessel <id> equipped, which is not in this list.`; die Zahl der
eigenen Zeile jedes Mal **gegen ein Literal** stellen.
*Positivkontrolle, ohne die der Waechter nur sein eigenes Pruefmittel misst:*
dieselbe Vorrichtung gegen die **heutige** Fassung — die Zahl steht dort in
`owned_label` und **muss** nach dem ersten `Load equipped` verschwunden sein.
Schlaegt das nicht an, loest die Vorrichtung die Meldungen nicht wirklich aus.
*Toetende Mutation:* die Zahl wieder in `owned_label` schreiben.

#### AK-251
*Verlauf: A33 Z9487 · zuletzt geaendert durch T-178, 2026-09-09*

**AK-251** *(die Zahl nennt Einheit und Geltungsbereich, woertlich)* Die Zeile
traegt woertlich `You own <n> relics in total.` bzw. bei genau einem Relikt
`You own 1 relic in total.`; ihr Tooltip traegt woertlich T2 aus §4 mit dem
Namen des gelesenen Spielstands, und der Name laeuft durch `html.escape()`.
Das Widget ist `Qt.PlainText`. `<n>` ist **dieselbe** Zahl, die die
Bestandsnotiz in derselben Sitzung nennt (`<n> relics in <source>`).
*Aufbau:* ein Bestand mit einem Relikt und einer mit mehreren; beide Zahlen
im selben Fenster auslesen und gegeneinander stellen.
*Toetende Mutation:* die Zahl aus `available_items()` eines Slots nehmen statt
aus dem Bestand — sie weicht dann von der Notiz ab, sobald ein Relikt in einem
Slot liegt.

#### AK-252
*Verlauf: A33 Z9499 · zuletzt geaendert durch T-178, 2026-09-09*

**AK-252** *(keine Zahl, bevor gelesen ist — und die Ankunft bewegt nichts)*
Solange kein Bestand vorliegt, ist die Zeile **leer**: kein `0`, kein `…`,
kein Wartesatz, kein Platzhalter. Das gilt in **allen vier** Faellen: waehrend
eines Lesens, das nie antwortet; bei `No save file found…`; bei
`Save could not be read: …`; und bei einem gewaehlten Spielstand ohne
Relikte. Ueber den Wechsel von leer zu gefuellt hinweg sind `width()` und
`height()` des Fensters identisch, die Bereichsbreiten identisch, und **kein
Bedienelement des linken Bereichs aendert seine Lage oder seine Hoehe** — die
Gefaessliste eingeschlossen.
*Messauflage an den `developer` (L-009):* er misst die Hoehe der gefuellten
Zeile an der Vorgabebreite des linken Bereichs und nennt sie **mit ihrer
Umgebung** (Qt-Stil, Windows-Anzeigeskalierung, physisch oder logisch, welcher
Bestand); die leere Zeile bekommt mindestens diese Hoehe, vom ersten Anstrich
an. Der Text wird dafuer nicht verlaengert.
*Toetende Mutation:* die Zeile bei fehlendem Bestand verstecken
(`setVisible(False)`) — bei der Ankunft ruecken Knopfzeile und Notiz.

---

## Bereich 3 — Build planner: die Advisor bar

Der Berater sitzt als Leiste in der mittleren Spalte des `Build planner`.
Dieser Bereich beschreibt, wo sie steht und wie gross sie werden darf, wie sie
sich waehrend einer laufenden Rechnung verhaelt, was sie aussagen darf und was
sie verschweigen muss, wie sie mit der Tastatur bedient wird und wie sie mit
praepariertem Text umgeht.

*Herkunft im Verlauf: A01 (T-004) · A16 (T-078) und A17 (T-080) fuer AK-18 und AK-21*

### 3.1 Platzierung und Layout

#### AK-01
*Verlauf: A01 Z335 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-01** Es gibt keinen neuen Tab. Die Tab-Leiste zeigt dieselben Tabs wie
in 3da8428.

#### AK-02
*Verlauf: A01 Z337 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-02** Die Advisor bar steht in der mittleren Spalte des Build planner
zwischen der "Build"-Zeile und dem Hinweistext und scrollt nicht mit.

#### AK-03
*Verlauf: A01 Z339 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-03** `Planner.minimumSizeHint().width()` ist nicht groesser als auf
3da8428 (gleiche Umgebung, gleiche UI scale, gemessen vor dem ersten
`show()`).

#### AK-04
*Verlauf: A01 Z342 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-04** Die Mindesthoehe des Fensters waechst um hoechstens 44 px
gegenueber 3da8428.

#### AK-05
*Verlauf: A01 Z344 + A14 Z2555 (Startbreite abgeleitet statt 1320 px) · zuletzt geaendert durch T-071, 2026-09-06*

*Ueberholt: **widerspruechlich** - die Pixelzahl 1320 px ist in A14 Z2555 (T-071) aufgehoben, wird aber in AK-160 (A17 Z4336) und AK-194 (A21 Z5782) danach erneut als `Startbreite` vorgeschrieben; siehe Abschnitt `Widerspruechliche Faelle`*

**AK-05** Bei Fensterbreite 1320 px (Startbreite) ist in der Advisor bar
kein Text abgeschnitten ausser der Statuszeile, und deren voller Text steht
im Tooltip.

**Dazu A14 Z2555 — Startbreite abgeleitet statt 1320 px:**

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A14** — Nachtrag des Directors zu AK-05 — 2026-09-06 (nach T-071) (T-071, 2026-09-06)  
> Verlauf Zeile **2624 bis 2647** (Altstand Z2555 bis Z2578)

> **Widerspruechlich — die Entscheidung steht beim App Designer aus.**
> Beide Fassungen stehen oben bzw. an den genannten Stellen nebeneinander;
> dieser Abschnitt loest den Vorrang **nicht** auf.

#### AK-06
*Verlauf: A01 Z347 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-06** Mit UI scale 150 % und sechs belegten Deep-of-Night-Slots samt
lebendem Vorschlag entsteht in der mittleren Spalte keine horizontale
Bildlaufleiste.

#### AK-07
*Verlauf: A01 Z350 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-07** Zu keinem Zeitpunkt sind mehr als drei Aktionsknoepfe der Advisor
bar gleichzeitig sichtbar.

### 3.2 Verhalten und Nebenlaeufigkeit

#### AK-08
*Verlauf: A01 Z355 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-08** Waehrend einer laufenden Rechnung lassen sich Nightfarer wechseln,
Vessel wechseln, ein Slot oeffnen und der Tab wechseln; kein Bedienelement
ausserhalb der Advisor bar ist deaktiviert, es erscheint kein modaler Dialog
und kein Wartecursor ueber dem Fenster.

#### AK-09
*Verlauf: A01 Z359 (Advisor bar); fuer den Picker A24 Z6989/Z6994 · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: fuer den Picker durch AK-215/AK-216 - A24 Z6989/Z6994 (T-127); fuer die Advisor bar unveraendert*

**AK-09** Eine Rechnung unter 250 ms zeigt weder Fortschrittsbalken noch
Wartetext (kein Aufblitzen).

#### AK-10
*Verlauf: A01 Z361 (Advisor bar); fuer den Picker A24 Z6994 · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: fuer den Picker durch AK-216 - A24 Z6994 (T-127); fuer die Advisor bar unveraendert*

**AK-10** Eine Rechnung ueber 250 ms zeigt Fortschrittsbalken und Wartetext,
und `Optimize` traegt `Cancel`.

#### AK-11
*Verlauf: A01 Z363 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-11** `Cancel` fuehrt binnen 200 ms nach dem Klick sichtbar in Zustand
4.5, auch wenn der Arbeiter laenger zum Beenden braucht.

#### AK-12
*Verlauf: A01 Z365 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-12** Aendert sich Nightfarer, Vessel, Deep of Night, Level oder eine
Slot-Belegung waehrend der Rechnung, wird das Ergebnis verworfen und 4.7
angezeigt. Es wird nie ein Vorschlag zu einem Zustand gezeigt, der nicht mehr
gilt.

#### AK-13
*Verlauf: A01 Z369 · zuletzt geaendert durch T-024, 2026-09-02 (praezisiert durch AK-57)*

**AK-13** `Optimize` veraendert keinen Slot: nach `Optimize` ohne Anwenden sind
Slot-Belegung, Statblatt und der Eintrag der Build-Liste unveraendert.

#### AK-14
*Verlauf: A01 Z371 · zuletzt geaendert durch T-024, 2026-09-02 (praezisiert durch AK-57)*

**AK-14** Nach `Apply all` zeigt das Statblatt die angewendeten Relikte, und
der Zustand ist derselbe, als waeren die Relikte einzeln im Picker gewaehlt
worden — Persistenz je Kelch inbegriffen.

#### AK-15
*Verlauf: A01 Z374 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-15** `Undo apply` stellt die vorherige Belegung exakt wieder her, auch
einen vorher leeren Slot und ein vorher dort liegendes Custom relic.

#### AK-16
*Verlauf: A01 Z376 · zuletzt geaendert durch T-024, 2026-09-02 (praezisiert durch AK-58)*

**AK-16** Kein Vorschlag enthaelt jemals ein Custom relic oder ein Relikt,
das nicht in `owned` steht.

#### AK-17
*Verlauf: A01 Z378 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-17** Der Berater schreibt nicht in den Save und oeffnet keine
Netzwerkverbindung.

### 3.3 Aussage und Hausregel

#### AK-18
*Verlauf: A16 Z3718 (AK-134) · zuletzt geaendert durch T-078, 2026-09-06*

*Ueberholt: vollstaendig durch AK-134 - A16 Z3718 (T-078); der Satz `genau ein Begruendungssatz je Slot` ist aufgehoben*

**AK-134** Die Zahl der in einer Slotgruppe gezeichneten Effekt- und
Fluchzeilen ist gleich der Zahl der Zeilen, die das Ergebnis fuer diesen
Slot traegt. Keine wird ausgelassen, keine zusammengefasst. *Ersetzt
AK-18*, dessen "genau ein Begruendungssatz je Slot" mit §1 aufgehoben ist;
A5 und AK-19 gelten unveraendert weiter.

<sub>Fundstelle sinngemaess: das Register nennt Z3718; hier steht der Absatz ab Z3718 (Verlauf Z3787).</sub>

#### AK-19
*Verlauf: A01 Z386 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-19** Traegt das vorgeschlagene Relikt Fluche, sind sie im
Vorschlagsblock genannt — in `CURSE` und mit `✦` — bevor angewendet wird.

#### AK-20
*Verlauf: A01 Z388 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-20** Kann das Ziel gar nicht bewertet werden, erscheint 4.10 und **kein**
Vorschlag. Es wird nie eine Rangfolge gezeigt, die auf fehlenden Daten beruht
(GOAL A7).

#### AK-21
*Verlauf: A16 Z3762 (AK-142) · zuletzt geaendert durch T-078, 2026-09-06*

*Ueberholt: vollstaendig durch AK-142 - A16 Z3762 (T-078)*

**AK-142** `not_counted` enthaelt ausschliesslich konditionale Effekte nach
AD-010 (`Build.situational`, `live == False`). Der Satz `The game files
carry no numbers for these, so they counted for nothing:` erscheint
nirgends mehr. *Ersetzt AK-21.*

<sub>Fundstelle sinngemaess: das Register nennt Z3762; hier steht der Absatz ab Z3759 (Verlauf Z3828).</sub>

#### AK-22
*Verlauf: A01 Z394 + A02 Z538 (Geltungsbereich eingeschraenkt) · zuletzt geaendert durch T-024, 2026-09-02*

*Ueberholt: der Geltungsbereich `genau einmal im Why-Dialog` gilt nur noch fuer den Optimize-Lauf - A02 Z538 (T-024)*

**AK-22** Beruht das Ziel auf Attack Rating, steht der Vorbehalt aus den
"Known limits" genau einmal im `Why`-Dialog — nicht je Zeile.

**Dazu A02 Z538 — Geltungsbereich eingeschraenkt:**

**Geltungsbereich von AK-22 eingeschraenkt** (keine Neudefinition, nur eine Einschraenkung der bestehenden Nummer): „Der Vorbehalt steht genau
einmal im `Why`-Dialog, nicht je Zeile" gilt weiter **fuer den
`Optimize`-Lauf und seinen `Why`-Dialog**. Fuer den Picker gilt er nicht:
dort steht neben jeder Karte eine eigene Zahl, und eine Zahl ohne ihren
Vorbehalt ist eine Behauptung. **Meine eigene Vorgabe war hier zu grob** —
sie kannte nur eine Bauform des Ergebnisses.

#### AK-23
*Verlauf: A01 Z396 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-23** Alle vom Berater gezeigten Zeichenketten sind Englisch (GOAL A8).

#### AK-24
*Verlauf: A01 Z397 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-24** Der Berater respektiert Slot-Farben, Stacking-Regeln und die
Deep-of-Night-Kennzeichnung: ein Vorschlag enthaelt kein Relikt, das der
Picker fuer denselben Slot nicht anbieten wuerde (GOAL A4).

### 3.4 Tastatur und Suche

#### AK-25
*Verlauf: A01 Z403 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-25** Jede Aktion des Beraters (Zielwahl, Optimize, Cancel, Apply all, Use
je Slot, Why, Clear, Undo apply) ist allein mit Tab / Umschalt+Tab und
Enter / Leertaste erreichbar und ausloesbar.

#### AK-26
*Verlauf: A01 Z406 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-26** Die Tab-Reihenfolge entspricht 5.7; der Fokusring ist auf jedem
neuen Bedienelement sichtbar.

#### AK-27
*Verlauf: A01 Z408 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-27** Der Filter im Relic Picker liefert mit lebendem Vorschlag dieselben
Treffermengen wie ohne; die Advisor-Karte ist nicht vom Filter ausgenommen,
und wird sie ausgefiltert, sagt die Zusammenfassungszeile das.

#### AK-28
*Verlauf: zurueckgezogen; Ersatz ist die Kennzeichnung in A01 Paragraf 3.5 · zuletzt geaendert durch T-024, 2026-09-02*

*Ueberholt: zurueckgezogen - A02 Z532 (T-024)*

**Zurueckgezogen.** zurueckgezogen; Ersatz ist die Kennzeichnung in A01 Paragraf 3.5

Der urspruengliche Wortlaut steht unveraendert in
`docs/archiv/ui-spec-verlauf.md`.

### 3.5 Rich-Text-Sicherheit

#### AK-29
*Verlauf: A01 Z417 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-29** Jedes vom Berater neu eingefuehrte Label, jeder Tooltip und jeder
Textbereich setzt `setTextFormat()` ausdruecklich. Kein neues Textelement
laeuft auf `Qt.AutoText`. Pruefbar per Grep ueber die neuen Widgets: zu jedem
`setText(` auf einem neuen Element existiert ein `setTextFormat(`.

#### AK-30
*Verlauf: A01 Z421 · zuletzt geaendert durch T-004, 2026-09-01*

**AK-30** Ein Relikt, dessen Name die Zeichenkette
`<b>x</b><img src=x>&lt;` enthaelt, erscheint im Vorschlagsblock, im
`Why`-Dialog, in der Statuszeile und im Tooltip **buchstabengetreu** — kein
Fettdruck, kein verschluckter Teil, keine geladene Ressource. Dasselbe fuer
einen praeparierten Effekt- und Fluchnamen. (Testweg: manipulierter
Snapshot-Eintrag; der `qa-engineer` legt den Testfall an.)

---

## Bereich 4 — Build planner: Slotkarten, festgehaltene Slots und `Optimize`

Drei Fragen, drei Namen: wie die Zahlen auf den Slot- und Waffenkacheln heissen
und welche Zahl welche Frage beantwortet; wie ein Slot festgehalten wird und was
ein Halt zusichert; was `Optimize` tut und was es nicht anfasst.

*Herkunft im Verlauf: A02 (T-024) · A03 (T-035) · A05 (T-052)*

### 4.1 Drei Fragen, drei Namen — die Benennung

#### AK-31
*Verlauf: A02 Z989 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-31** Im gesamten `nrplanner/`-Baum wird eine Angriffswertzahl nur mit
einer dieser drei Formen beschriftet: `AR without relics`, `AR as equipped`,
`AR at +<n>`. Die Beschriftungen `Base`, `Base AR`, `Total` und ein
alleinstehendes `AR` **als Beschriftung** kommen nicht mehr vor. Ausnahme,
ausdruecklich: das Suffix `AR` in der Waffenkachel des Build planner
(`203 AR`), zulaessig **nur zusammen mit** der Bildunterschrift aus AK-35
und **erst ab** Schritt W3.

#### AK-32
*Verlauf: A02 Z996 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-32** Jede Angriffswertzahl auf dem Bildschirm laesst sich einer der drei
Fragen aus `damage.Basis` zuordnen, ohne zu hovern und ohne aufzuklappen —
entweder ueber ihre eigene Beschriftung oder ueber eine stets sichtbare
Bildunterschrift im selben Sichtblock.

#### AK-33
*Verlauf: A02 Z1000 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-33** Die Kopfzeile der Zahlenliste jeder Arsenal-Kachel lautet
`AR at +<n>` mit dem Wert der Spinbox `Upgrade to +`; sie aendert sich mit
der Spinbox und bricht bei Kachelbreite 200 px nicht um.

#### AK-34
*Verlauf: A02 Z1003 + A03 Z1181 (Fassung B) + A06 Z1384 (dritte Zeile) · zuletzt geaendert durch T-052, 2026-09-05*

*Ueberholt: der Uebergangs-Wortlaut ist zweimal nachgezogen - A03 Z1181 (T-035), A06 Z1384 (T-052)*

**AK-34** Die Arsenal-Zusammenfassung besteht aus zwei getrennten Labels mit
dem Wortlaut aus §2.3(e). Der Multiplikator-Satz entspricht dem Wert von
`MULTIPLIERS_FOR[Basis.CANDIDATE]` (Fassung A bei `False`, Fassung B bei
`True`). Die Zeichenketten `60%`, `under investigation` und
`ranking between weapons is unaffected` kommen im gesamten Baum nicht mehr
vor.

**Dazu A03 Z1181 — Fassung B:**

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A03** — Nachtrag zu AK-34: Fassung B fuer den heutigen Einzelsatz (T-035) — 2026-09-03 (T-035, 2026-09-03)  
> Verlauf Zeile **1250 bis 1289** (Altstand Z1181 bis Z1220)

**Dazu A06 Z1384 — dritte Zeile:**

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A06** — Nachtrag zu AK-34/QA-121: der Uebergangssatz braucht eine dritte Zeile, seit Katalysatoren im selben Raster stehen (ui-ux-designer, T-052) — 2026-09-05 (T-052, 2026-09-05)  
> Verlauf Zeile **1453 bis 1506** (Altstand Z1384 bis Z1437)

#### AK-35
*Verlauf: A02 Z1009 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-35** Zwischen dem Waffenkachelraster und der Schadenstafel steht eine
stets sichtbare Bildunterschrift mit dem Wortlaut aus §2.3(c). Sie ist kein
Tooltip, nicht aufklappbar, und sie scrollt mit den Kacheln, nicht von ihnen
weg.

#### AK-36
*Verlauf: A02 Z1013 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-36** Die Gesamtzeile der Schadenstafel zeigt beide Namen ohne Hovern
(`AR without relics <n> → AR as equipped <n>`); die Aufschluesselung
(`_show_ar_breakdown`) benutzt in erster und letzter Zeile dieselben zwei
Namen und dazwischen die Zeile `What your relics add to your attributes`.

#### AK-37
*Verlauf: A02 Z1017 + A05 Z1360 · zuletzt geaendert durch T-052, 2026-09-05*

*Ueberholt: beide festen Vorbehalts-Wortlaute des Pickers entfallen ersatzlos - A05 Z1360 (T-052); die Aussage gilt jetzt ueber Goal.scope/SlotPool.unknowns. Der in AK-37 selbst zitierte Picker-Satz ist damit gegenstandslos, der Arsenal-Satz bleibt*

**AK-37** Keine Zeichenkette der Oberflaeche behauptet, welche Zahl richtig
ist, in welchem Verhaeltnis sie zum Spiel steht, oder dass eine Rangfolge
davon unberuehrt bleibt. Die einzigen Aussagen zur Verifikation sind
`Not checked against the game's own attack-power display.` (Arsenal-Tab) und
`Attack rating has not been checked against the game, so these figures may
be wrong.` (Picker) — je Bildschirm genau einmal, im Picker zusaetzlich der
Kartenmarker aus AK-46.

**Dazu A05 Z1360 — ergaenzt:**

**Betroffene Akzeptanzkriterien:** AK-37 (beide bisherigen Wortlaute
entfallen ersatzlos; die Aussage „keine Zeichenkette behauptet, welche Zahl
richtig ist" gilt jetzt ueber `Goal.scope`/`SlotPool.unknowns` statt ueber
einen festen Satz), AK-50 (gilt jetzt fuer **drei** Zeilen statt zwei — 3, 3b,
4 —, alle ausserhalb der `QScrollArea`, keine gekuerzt; Zeile 3b ist die
einzige der drei, die leer sein darf), der Nachtrag zu AK-47 oben (dessen
offene Frage ist hiermit beantwortet: **keiner** der beiden dort genannten
Wortlaute wird ausgeliefert).

#### AK-38
*Verlauf: A02 Z1024 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-38 (QA-055-Regression)** Aufbau: Slot auf Tier 3, Arsenal-Spinbox auf
+1, kein Relikt ausgeruestet. Die beiden Zahlen duerfen verschieden sein;
die Arsenal-Kachel nennt in ihrer Kopfzeile `AR at +1`, der Build planner
nennt in der Bildunterschrift „each at its own upgrade", und keine
Beschriftung behauptet, es sei dieselbe Frage.

#### AK-39
*Verlauf: A02 Z1029 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-39 (QA-056-Regression)** Aufbau: ein Relikt mit `Strength +1`, sonst
nichts. Waffenkachel und Schadenstafel zeigen fuer dieselbe Waffe **dieselbe**
Zahl (nach W3, AD-020 Punkt 6); die davon abweichende linke Tafelzahl traegt
sichtbar `AR without relics`.

#### AK-40
*Verlauf: A02 Z1033 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-40 (Reihenfolge)** Die Beschriftungen aus AK-31, AK-33, AK-35 und AK-36
werden nicht vor den zugehoerigen Umbauschritten ausgeliefert: die
Kachel-/Tafel-Fassung nicht vor W3, die Arsenal-Fassung nicht vor W4. Ein
Zwischenstand, in dem Kachel und Tafel verschiedene Zahlen zeigen und beide
`AR as equipped` heissen, ist unzulaessig.

### 4.2 Festgehaltene Slots

#### AK-54
*Verlauf: A02 Z1097 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-54** Jede `RelicSlot`-Karte traegt in ihrer Kopfzeile einen checkbaren
Knopf mit dem Text `Hold` bzw. `Held` (kein icon-only-Schloss) und dem
Tooltip-Wortlaut aus §4.1.

#### AK-55
*Verlauf: A02 Z1100 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-55** Ein leerer Slot kann gehalten werden; er zeigt dann
`Held empty — Optimize will not fill this slot.` und wird von `Apply all`
nicht belegt.

#### AK-56
*Verlauf: A02 Z1103 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-56** Faellt ein Halt weg, weil das Relikt nicht mehr im Besitz ist,
steht der Satz aus §4.3 am Slot **und** eine entsprechende Zeile in den
`unknowns` des naechsten Laufs. Kein Halt faellt stillschweigend weg.

#### AK-57
*Verlauf: A02 Z1106 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-57 (praezisiert AK-13, AK-14)** Nach `Apply all` ist der Inhalt jedes
gehaltenen Slots bitgleich dem Inhalt davor — Relikt, Rolls, Fluche, und auch
der Fall „gehalten und leer". `Optimize` allein veraendert weiterhin keinen
einzigen Slot.

#### AK-58
*Verlauf: A02 Z1110 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-58 (praezisiert AK-16)** Ein gehaltener Slot darf ein `Custom relic`
enthalten und behaelt es. Kein **vorgeschlagener** Slot enthaelt je ein
`Custom relic` oder ein Relikt ausserhalb von `owned`.

#### AK-59
*Verlauf: A02 Z1113 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-59** Keine Zeichenkette der Oberflaeche legt nahe, dass ein Halt einen
Programmneustart ueberlebt. Nach einem Neustart ist kein Slot gehalten.

#### AK-60
*Verlauf: A02 Z1115 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-60** Gefaess oder Nightfarer wechseln und zurueckwechseln stellt den
Haltezustand wieder her; die Slot-Kopfzeilen zeigen ihn unmittelbar danach
richtig an.

### 4.3 `Optimize`

#### AK-61
*Verlauf: A02 Z1121 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-61** Der Knopf heisst `Optimize` und steht in der Advisor bar der
mittleren Spalte des Build planner. Im Relic Picker gibt es **keinen** Knopf,
der mehr als den geoeffneten Slot veraendert.

#### AK-62
*Verlauf: A02 Z1124 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-62** Der Satz aus §5.3 steht sichtbar im Picker, in jeder Sortierung und
in jedem Zustand, in dem Kartenwerte gezeigt werden.

---

## Bereich 5 — Der Relic Picker

Der Picker ist der Hauptweg des Beraters. Dieser Bereich beschreibt den
Wertblock jeder Reliktkarte, die Sortierung und was sie ueber sich behaupten
darf, den Filter, das leere Raster vor der Antwort und was sich bewegen darf,
wenn die Zahlen eintreffen.

Die Bezugsgroesse in **Zeile 4** des Pickers gehoert zur Sprache der Zahlen und
steht in Bereich 6 (AK-63, AK-162 bis AK-166).

*Herkunft im Verlauf: A02 (T-024) · A04 (T-037) · A05 (T-052) · A22 (Director) · A23 (T-124) · A24 (T-127) · A25 (T-135)*

### 5.1 Wertblock, Sortierung, Filter

#### AK-41
*Verlauf: A02 Z1041 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-41** Jede Reliktkarte traegt einen Wertblock als erste Zeile des
Kartenkoerpers, unter der Kopfzeile und ueber den Effektpunkten, getrennt
durch eine 1-px-Haarlinie in `BORDER`. Die Hoehe jeder Karte ist vor und
nach dem Eintreffen der Werte identisch (Messung: Differenz 0 px).

#### AK-42
*Verlauf: A02 Z1045 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-42** Der Wertblock zeigt **beide** Zielrichtungen (`Damage`,
`Damage taken`) auf jeder Karte, in jeder Sortierung. Ein Wert von Null
erscheint als `no change`, nie als `+0.0`.

#### AK-43
*Verlauf: A02 Z1048 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-43** Der Picker traegt ein `Sort by` mit genau den Eintraegen
`Maximise damage`, `Minimise damage taken`, `Name`. Eine Aenderung dort
aendert die Zielwahl der Advisor bar und umgekehrt; es existiert im ganzen
Programm nur eine Zielwahl-Einstellung.

#### AK-44
*Verlauf: A02 Z1052 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-44** Weder auf einer Karte noch in der Kopfzeile erscheint eine
Ordnungszahl, ein Rangabzeichen oder eine Formulierung, die eine strenge
Reihenfolge behauptet. Zweimaliges Oeffnen des Pickers bei unveraendertem
Zustand liefert **dieselbe** Kartenreihenfolge.

#### AK-45
*Verlauf: A02 Z1056 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-45** Zwei Karten zeigen genau dann denselben Wert in der sortierten
Zielrichtung, wenn sie dieselbe Gleichstandskennzeichnung tragen. Es gibt
keinen Fall mit gleichem angezeigten Wert und verschiedener Kennzeichnung.

#### AK-46
*Verlauf: A02 Z1059 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-46** Jede Karte mit dem Maximalwert der sortierten Zielrichtung traegt
den Textchip `BEST FOR DAMAGE` bzw. `BEST FOR SURVIVAL`, auch wenn es
mehrere sind. Ist der Maximalwert `no change` oder negativ, traegt **keine**
Karte den Chip, und die Kopfzeile sagt
`Nothing you own raises damage in this slot.`

#### AK-47
*Verlauf: A02 Z1064 (zweite Haelfte) + A04 Z1221 + A05 Z1269 · zuletzt geaendert durch T-052, 2026-09-05*

*Ueberholt: erste Haelfte gegenstandslos (QA-018 geschlossen) - A04 Z1221 (T-037); der in A04 Punkt 2 fest gebundene Satz ist durch A05 Z1269 (T-052) aufgehoben - Zeile 4 zeigt ausschliesslich Goal.scope*

**AK-47** Solange QA-018 offen ist, steht hinter dem Angriffswert **jeder**
Karte das Wort `unverified` — sichtbar, nicht in einem Tooltip, nicht
aufklappbar. Ist QA-018 geschlossen, kommt das Wort nirgends mehr vor.

**Dazu A04 Z1221 — ergaenzt:**

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A04** — Nachtrag zu AK-47: das Wort `unverified` entfaellt (Director, T-037) — 2026-09-03 (T-037, 2026-09-03)  
> Verlauf Zeile **1290 bis 1337** (Altstand Z1221 bis Z1268)

**Dazu A05 Z1269 — ergaenzt:**

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A05** — Nachtrag zu QA-116: keiner der beiden Wortlaute — der Vorbehalt wird datengetrieben (ui-ux-designer, T-052) — 2026-09-05 (T-052, 2026-09-05)  
> Verlauf Zeile **1338 bis 1452** (Altstand Z1269 bis Z1383)

#### AK-48
*Verlauf: A02 Z1067 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-48** Bewegt der Fluch eines Relikts ein Feld, das **keine** der beiden
Zahlen misst, steht unter dem Wertblock genau eine Zeile
`Its curse changes <field>, which neither figure counts.`; misst eine der
beiden Zahlen das Feld, steht diese Zeile **nicht** da. Ein Fluch wird
nirgends als Grund fuer eine schlechtere Platzierung dargestellt.

#### AK-49
*Verlauf: A02 Z1072 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-49** Traegt die gewaehlte Zielrichtung keine Zahlen, steht die Zeile aus
§3.7 in der Kopfzeile, jede Karte zeigt `—` statt einer Zahl, und die Ordnung
ist Namensordnung. Es wird nie eine Rangfolge gezeigt, die auf fehlenden
Daten beruht.

#### AK-50
*Verlauf: A02 Z1076 + A05 Z1360 (gilt fuer drei Zeilen) · zuletzt geaendert durch T-052, 2026-09-05*

*Ueberholt: der Umfang `zwei Zeilen` - A05 Z1360 (T-052), jetzt Zeile 3, 3b und 4*

**AK-50** Die beiden Textzeilen aus §3.2 (Bezugsgroesse; slotweise plus
Attack-Rating-Vorbehalt) stehen ausserhalb der `QScrollArea`, sind ohne
Interaktion sichtbar und werden nie gekuerzt oder elidiert.

**Dazu A05 Z1360 — gilt fuer drei Zeilen:**

**Betroffene Akzeptanzkriterien:** AK-37 (beide bisherigen Wortlaute
entfallen ersatzlos; die Aussage „keine Zeichenkette behauptet, welche Zahl
richtig ist" gilt jetzt ueber `Goal.scope`/`SlotPool.unknowns` statt ueber
einen festen Satz), AK-50 (gilt jetzt fuer **drei** Zeilen statt zwei — 3, 3b,
4 —, alle ausserhalb der `QScrollArea`, keine gekuerzt; Zeile 3b ist die
einzige der drei, die leer sein darf), der Nachtrag zu AK-47 oben (dessen
offene Frage ist hiermit beantwortet: **keiner** der beiden dort genannten
Wortlaute wird ausgeliefert).

<sub>Fundstelle sinngemaess: das Register nennt Z1360; hier steht der Absatz ab Z1360 (Verlauf Z1429).</sub>

#### AK-51
*Verlauf: A02 Z1079 (erste Haelfte); zweite Haelfte A22 Z5967 (AK-196) · zuletzt geaendert durch T-124-Vorlauf/Director-Korrektur, 2026-09-07*

*Ueberholt: zweite Haelfte durch AK-196 - A22 Z5967 (Director-Korrektur 2026-09-07)*

**AK-51** Am Standardmass des Pickers erscheint **keine** waagerechte
Bildlaufleiste (heute gemessen: Sichtbereich 988 px gegen 1000 px Inhalt),
und es sind mindestens **drei vollstaendige Kartenzeilen** sichtbar. Wird
eine der beiden Bedingungen durch die neuen Inhalte verletzt, wird das
Standardmass des Dialogs vergroessert — nicht der Inhalt gekuerzt.

#### AK-52
*Verlauf: A02 Z1084 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-52** `Sort by` liegt in der Tab-Reihenfolge zwischen dem Filterfeld und
der ersten Karte; jede Karte ist per Tab erreichbar und per Enter oder
Leertaste auswaehlbar; der Fokusring ist auf jedem neuen Bedienelement
sichtbar und wird nicht per Stylesheet entfernt.

#### AK-53
*Verlauf: A02 Z1088 · zuletzt geaendert durch T-024, 2026-09-02*

**AK-53** Jedes im Picker neu eingefuehrte Label und jeder neue Tooltip setzt
`setTextFormat()` ausdruecklich; jeder aus Save- oder Spieldateien stammende
Text (Reliktname, Effektname, Fluchname, Feldname aus `model.label_for`)
laeuft vor der Interpolation durch `html.escape()`. Ein Relikt mit dem Namen
`<b>x</b><img src=x>&lt;` erscheint auf der Karte und in jedem neuen Satz
buchstabengetreu (Erweiterung von AK-29/AK-30 auf die neuen Elemente).

### 5.2 Spitzenwert und Bildlauf — vom App Designer entschieden

#### AK-195
*Verlauf: A22 Z5928 · zuletzt geaendert durch Director, 2026-09-07*

**1. Die beiden Spitzenreiter stehen oben.** Woertlich: *"zeig mir aber immer
den top pick für dmg und survival als erstes. in beiden varianten."*

Bisher fuehrte bei einer Zielsortierung der **Wert** (§3.4), und der
Spitzenwert war nur durch den Chip `BEST FOR …` gekennzeichnet (AK-46). Wer
nach Schaden sortierte, fand das beste Ueberlebensrelikt irgendwo weiter
unten. Genau das war der Punkt: **beide Zahlen stehen auf jeder Karte, aber
nur eine ordnete das Raster.**

Neu, als **AK-195**: In beiden Zielsortierungen stehen die Karten mit dem
Spitzenwert **beider** Zielrichtungen an der Spitze des Rasters, vor allen
uebrigen. Es sind genau die Karten, die nach AK-46 einen `BEST FOR …`-Chip
tragen — die Anordnung sagt damit nichts, was der Chip nicht schon sagt, sie
macht es nur auffindbar.

<sub>Fundstelle sinngemaess: das Register nennt Z5928; hier steht der Absatz ab Z5919 (Verlauf Z5988).</sub>

#### AK-196
*Verlauf: A22 Z5967 · zuletzt geaendert durch Director, 2026-09-07*

Neu, als **AK-196**, und **ersetzt die zweite Haelfte von AK-51**: Am
Standardmass des Pickers erscheint **keine waagerechte Bildlaufleiste**, und
es sind mindestens **zwei vollstaendige Kartenzeilen** sichtbar. Die erste
Haelfte von AK-51 (keine waagerechte Bildlaufleiste; im Konfliktfall das
Standardmass vergroessern statt den Inhalt zu kuerzen) gilt unveraendert.

*Begruendung der Zahl:* zwei Zeilen sind das, was auf dem einzigen Bildschirm,
auf dem gemessen wurde, mit dem vorgegebenen Inhalt erreichbar ist. Drei waren
eine Zusicherung ohne Messung. Wer sie zurueckhaben will, muss Inhalt ueber
dem Raster streichen — das ist eine Frage an den App Designer, keine an die
Umsetzung.

<sub>Fundstelle sinngemaess: das Register nennt Z5967; hier steht der Absatz ab Z5967 (Verlauf Z6036).</sub>

### 5.3 Der Picker oeffnet vor seinen Zahlen

#### AK-197
*Verlauf: A24 Z6942 (AK-211) · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: gestrichen, ersetzt durch AK-211 - A24 Z6942 (T-127); Streichliste A24 Z6915*

**AK-211** *(zwei Anstriche, nicht drei — ersetzt AK-197.)* Je Oeffnung des
Pickers gibt es hoechstens zwei Zustaende der Anzeige: den ohne Antwort
(leeres Raster) und den mit ihr. Alles, was an der Antwort haengt — **die
Karten selbst**, die Zahlen beider Wertzeilen, die `BEST FOR …`-Chips, die
Ordnung samt AK-195-Vorziehung, die Kopfzeile und die Laufbefundzeile —
erscheint in **einem** Anstrich. Es gibt keinen Zwischenzustand, in dem
Karten ohne Zahlen stehen, in dem ein Teil der Karten steht, oder in dem die
Wartezeile neben Karten steht.
*Toetende Mutation:* Karten und Zahlen in zwei Schritten setzen.

#### AK-198
*Verlauf: A24 Z6951 (AK-212) · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: gestrichen, ersetzt durch AK-212 - A24 Z6951 (T-127); Streichliste A24 Z6916*

**AK-212** *(das leere Raster ist ein Zustand, kein Nichts — ersetzt AK-198;
dies ist der Waechter **W2**.)* Wird der Picker mit einer Spur geoeffnet,
die nie antwortet, so gilt dauerhaft: im Rollbereich steht **kein**
Kartenwidget — keine Reliktkarte und auch nicht die Custom-Kachel —, kein
Reliktname, keine Zahl, kein Chip; keine Karte ist mit Tab erreichbar; an
der Stelle der linken oberen Karte steht die eine Zeile
`Your relics appear here.`; die Kopfzeile ist leer; Zeile 3 traegt den
Wartesatz aus AK-214; die beiden Textzeilen aus AK-201 stehen vollstaendig;
und der Dialog ist bedienbar nach AK-213.
*Toetende Mutation:* die Rechnung wieder synchron vor dem Oeffnen — die
Karten stehen sofort. Kein Zeitmass.
*Ausnahme, ausdruecklich:* bietet der Picker beim ersten Anstrich keine
einzige Reliktkarte an (leerer Slot, oder ein voreingestellter Filter ohne
Treffer), gibt es keinen Wartezustand und keine Wartezeile; der Dialog
zeichnet einmal.

#### AK-199
*Verlauf: A24 Z6951 (AK-212) und Z6967 (AK-213) · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: gestrichen, ersetzt durch AK-212 und AK-213 - A24 Z6951/Z6967 (T-127); Streichliste A24 Z6919*

**AK-212** *(das leere Raster ist ein Zustand, kein Nichts — ersetzt AK-198;
dies ist der Waechter **W2**.)* Wird der Picker mit einer Spur geoeffnet,
die nie antwortet, so gilt dauerhaft: im Rollbereich steht **kein**
Kartenwidget — keine Reliktkarte und auch nicht die Custom-Kachel —, kein
Reliktname, keine Zahl, kein Chip; keine Karte ist mit Tab erreichbar; an
der Stelle der linken oberen Karte steht die eine Zeile
`Your relics appear here.`; die Kopfzeile ist leer; Zeile 3 traegt den
Wartesatz aus AK-214; die beiden Textzeilen aus AK-201 stehen vollstaendig;
und der Dialog ist bedienbar nach AK-213.
*Toetende Mutation:* die Rechnung wieder synchron vor dem Oeffnen — die
Karten stehen sofort. Kein Zeitmass.
*Ausnahme, ausdruecklich:* bietet der Picker beim ersten Anstrich keine
einzige Reliktkarte an (leerer Slot, oder ein voreingestellter Filter ohne
Treffer), gibt es keinen Wartezustand und keine Wartezeile; der Dialog
zeichnet einmal.

<sub>Fundstelle sinngemaess: das Register nennt Z6951; hier steht der Absatz ab Z6951 (Verlauf Z7020).</sub>

**Dazu A24 Z6967 — AK-213:**

**AK-213** *(waehrend der Leere ist nichts gesperrt und nichts geht
verloren — nimmt die `Sort by`-Zusage aus AK-199 auf.)* Im Zustand aus
AK-212 sind Filterfeld, `Sort by`, Bildlaufleiste und jedes andere
Bedienelement des Dialogs freigegeben (`isEnabled()`), keines ist
ausgegraut, und der Dialog traegt keinen Wartecursor. `Sort by` steht
unveraendert auf der gewaehlten Zielrichtung und wird nicht auf `Name`
umgestellt. Text, den der Spieler waehrend der Leere in das Filterfeld
tippt, steht danach unveraendert im Feld und wirkt auf die Karten, sobald
sie erscheinen; er loest keine zweite Frage aus (AK-206). Esc schliesst den
Dialog.
*Toetende Mutation:* Filterfeld oder `Sort by` waehrend der Leere sperren.

<sub>Fundstelle sinngemaess: das Register nennt Z6967; hier steht der Absatz ab Z6966 (Verlauf Z7035).</sub>

#### AK-200
*Verlauf: A24 Z6977 (AK-214) · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: gestrichen, ersetzt durch AK-214 - A24 Z6977 (T-127); Streichliste A24 Z6920*

**AK-214** *(Zeile 3 behauptet keine Rangfolge und zaehlt nichts, was nicht
dasteht — ersetzt AK-200.)* Solange keine Karte steht, traegt Zeile 3
woertlich `Working out what each relic is worth with <slot> empty` und
**nichts sonst**: keine Zaehlung `x of y relics`, keinen Filterhinweis,
keinen Favoritenhinweis, keinen Rechtsklick-Satz. Der Nebensatz
`ranked against your build with <slot> empty` erscheint nicht, bevor die
Karten stehen. Die Wartefassung wird am Standardmass des Pickers **nicht
hoeher gezeichnet** als die fertige — gemessen, mit Umgebung genannt
(L-009: Stil, Skalierung, physisch oder logisch); ist sie es doch, wird die
**Warte**fassung gekuerzt, nicht die fertige.
*Toetende Mutation:* den Zaehlteil der Zeile waehrend der Leere stehen
lassen.

<sub>Fundstelle sinngemaess: das Register nennt Z6977; hier steht der Absatz ab Z6977 (Verlauf Z7046).</sub>

#### AK-201
*Verlauf: A23 Z6421 · zuletzt geaendert durch T-124, 2026-09-08 (A24 Z6925: gilt unveraendert weiter)*

**AK-201** *(die Pflichtzeilen warten nicht.)* Im Zustand aus AK-198 stehen
die beiden Textzeilen aus §3.2 vollstaendig: die Pflichtzeile
`One slot at a time — …` und die `scope`-Saetze der gewaehlten
Zielrichtung, sichtbar, ungekuerzt, nicht elidiert (AK-50 gilt ab dem
ersten Anstrich). Einzige Anzeige ueber dem Raster, die auf die Antwort
warten darf, ist die Laufbefundzeile (3b).
*Toetende Mutation:* das heutige Ausblenden beider Zeilen bei fehlender
Rangfolge stehen lassen.

#### AK-202
*Verlauf: A24 Z6989 (AK-215) · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: gestrichen, ersetzt durch AK-215 - A24 Z6989 (T-127); Streichliste A24 Z6921*

**AK-215** *(was erscheinen darf, und wo — ersetzt AK-202.)* Zwischen dem
ersten und dem zweiten Anstrich aendert sich **ausserhalb** des Rollbereichs
kein Widgetbestand: kein Fortschrittsbalken, kein Wartetext als eigene
Zeile, kein Wartecursor, kein Spinner, keine animierten Punkte, keine
Laufschrift, kein zweiter Dialog, kein gesperrtes Bedienelement, keine
Zeitschwelle, kein Verzoegerungstimer. **Innerhalb** des Rollbereichs gibt
es genau **einen** Wechsel: die Zeile `Your relics appear here.` weicht den
Karten. **Ersetzt AK-09 und AK-10 fuer den Picker**, nicht fuer die Advisor
bar.
*Toetende Mutation:* einen Fortschrittsbalken oder eine
Verzoegerungsschwelle einbauen.

#### AK-203
*Verlauf: A24 Z6994 (AK-216, Groesse) und Z7019 (AK-217, Fokus/Bildlauf) · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: gestrichen, ersetzt durch AK-216 und AK-217 - A24 Z6994/Z7019 (T-127); Streichliste A24 Z6922*

**AK-215** *(was erscheinen darf, und wo — ersetzt AK-202.)* Zwischen dem
ersten und dem zweiten Anstrich aendert sich **ausserhalb** des Rollbereichs
kein Widgetbestand: kein Fortschrittsbalken, kein Wartetext als eigene
Zeile, kein Wartecursor, kein Spinner, keine animierten Punkte, keine
Laufschrift, kein zweiter Dialog, kein gesperrtes Bedienelement, keine
Zeitschwelle, kein Verzoegerungstimer. **Innerhalb** des Rollbereichs gibt
es genau **einen** Wechsel: die Zeile `Your relics appear here.` weicht den
Karten. **Ersetzt AK-09 und AK-10 fuer den Picker**, nicht fuer die Advisor
bar.
*Toetende Mutation:* einen Fortschrittsbalken oder eine
Verzoegerungsschwelle einbauen.

<sub>Fundstelle sinngemaess: das Register nennt Z6994; hier steht der Absatz ab Z6989 (Verlauf Z7058).</sub>

**Dazu A24 Z7019 — AK-217, Fokus/Bildlauf:**

**AK-217** *(Fokus und Bildlauf — ersetzt die zweite Haelfte von AK-203.)*
Beim Erscheinen der Karten behaelt das Bedienelement mit dem Tastaturfokus
ihn; der Fokus springt **nicht** auf eine Karte, und der Bildlauf steht
danach am Anfang. Fuer jeden **spaeteren** Neubau des Rasters in derselben
Oeffnung — Filteranschlag, Zielrichtungswechsel, Favoritenvergabe — gilt
unveraendert AK-52: der Bildlaufwert bleibt, und lag der Fokus auf einer
Reliktkarte, liegt er danach auf der Karte desselben Relikts.
*Toetende Mutation:* den Fokus beim Erscheinen der Karten auf die erste
Karte legen.

#### AK-204
*Verlauf: A23 Z6443 · zuletzt geaendert durch T-124, 2026-09-08 (A24 Z6926: gilt unveraendert weiter)*

**AK-204** *(der Zielrichtungswechsel wartet nicht.)* Steht eine Antwort,
und der Spieler wechselt `Sort by` zwischen den beiden Zielrichtungen, so
traegt zu **keinem** Zeitpunkt eine Karte `…`, und Zeile 3 traegt zu keinem
Zeitpunkt den Wartesatz. Ordnung, Chips, Kopfzeile und `scope`-Saetze
wechseln in einem Anstrich.
*Toetende Mutation:* beim Wechsel erneut fragen.

#### AK-205
*Verlauf: A23 Z6449 · zuletzt geaendert durch T-124, 2026-09-08 (A24 Z6927: gilt unveraendert weiter)*

**AK-205** *(gezeichnet wird die gewaehlte Richtung, nicht die sortierte.)*
Die Richtung, in der Wertspalten, Chips, Kopfzeile und `scope`-Saetze
gezeichnet werden, ist die eine Zieleinstellung des Programms (AK-43) und
**nicht** `SlotPool.rank_by`. Aufbau: eine Antwort, die fuer die eine
Richtung sortiert wurde, wird in der anderen gelesen — Chips und Ordnung
gehoeren zur gelesenen.
*Toetende Mutation:* die Richtung aus `pool.rank_by` nehmen.

#### AK-206
*Verlauf: A23 Z6456 · zuletzt geaendert durch T-124, 2026-09-08 (A24 Z6928: gilt unveraendert weiter)*

**AK-206** *(eine Frage je Oeffnung.)* Vom Oeffnen bis zum Schliessen
erreicht die Spur hoechstens **eine** Anfrage. Filtern, Bildlauf,
Favoritenvergabe, ein Wechsel der Zielrichtung und ein Wechsel auf `Name`
loesen keine weitere aus. Wechselt der Spieler die Richtung, waehrend die
Antwort noch aussteht, wird weder neu gefragt noch der Wartezustand neu
begonnen; die eintreffende Antwort wird in der dann gewaehlten Richtung
gezeichnet.
*Toetende Mutation:* im offenen Dialog ein zweites Mal fragen.

#### AK-207
*Verlauf: A23 Z6464 + A24 Z6929 · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: die zweite Zusage (`eine im Wartezustand ausgewaehlte Karte wird uebernommen`) entfaellt gegenstandslos - A24 Z6929 (T-127)*

**AK-207** *(die ueberholte Antwort erreicht nichts.)* Wird der Picker
geschlossen, waehrend eine Antwort unterwegs ist, schliesst er sofort; die
spaeter eintreffende Antwort fasst kein Widget an, wirft nichts und
veraendert die Slot-Belegung nicht. Eine im Wartezustand ausgewaehlte Karte
wird uebernommen wie sonst auch. Zusammen mit **W3** aus AD-028.

**Dazu A24 Z6929 — ergaenzt:**

**AK-207** (die ueberholte Antwort erreicht nichts — die zweite Zusage,
*„eine im Wartezustand ausgewaehlte Karte wird uebernommen"*, entfaellt
gegenstandslos: waehrend der Leere gibt es keine Karte zum Auswaehlen),

#### AK-208
*Verlauf: A23 Z6469 + A24 Z6932 (erweitert durch AK-218) · zuletzt geaendert durch T-127, 2026-09-08*

**AK-208** *(der Fehlschlag hat seinen eigenen Satz.)* Meldet die Spur
einen Fehlschlag, steht in der Kopfzeile woertlich
`Could not work out what these are worth — <reason>. They are in name order below.`;
die Karten tragen `—`, keinen Chip, und stehen in Namensordnung. Der Satz
`The game's data carries no figures …` erscheint in diesem Fall **nicht**.
*Toetende Mutation:* den Fehlschlag auf den AK-49-Satz abbilden.

**Dazu A24 Z6932 — erweitert durch AK-218:**

**AK-208** (der Fehlschlag hat seinen eigenen Satz — erweitert durch AK-218),

#### AK-209
*Verlauf: A24 Z7047 (AK-219) · zuletzt geaendert durch T-127, 2026-09-08*

*Ueberholt: gestrichen, ersetzt durch AK-219 - A24 Z7047 (T-127); Streichliste A24 Z6923*

**AK-219** *(zwei Zeichen, zwei Aussagen — ersetzt AK-209.)* Auf einer Karte
bedeuten `—` „nicht gemessen" und `no change` „gemessen, ohne Wirkung"; sie
stehen nie fuereinander. Ein drittes Zeichen fuer „laeuft noch" gibt es auf
dem Bildschirm nicht mehr: **keine im Rollbereich stehende Karte traegt je
`…` (`PENDING`)** — solange die Frage laeuft, steht keine Karte da. Die
Konstante selbst bleibt als Platzhalter beim Bau der Karte (§3.3, AK-41).
*Toetende Mutation:* das Raster waehrend der Leere mit Karten fuellen, die
`…` tragen — das ist die T-124-Fassung, und sie muss rot werden.

#### AK-210
*Verlauf: A23 Z6480 · zuletzt geaendert durch T-124, 2026-09-08 (A24 Z6933: gilt unveraendert weiter)*

**AK-210** *(die Zusagen des Bestands ueberleben den Umbau.)* Nach dem
zweiten Anstrich gilt unveraendert: AK-41 (0 px Hoehenunterschied), AK-42
(beide Richtungen auf jeder Karte), AK-44 (keine Ordnungszahl; zweimal
derselbe Zustand ergibt zweimal dieselbe Reihenfolge — gemessen am
**zweiten** Anstrich, denn der erste ist keine Rangfolge), AK-45, AK-46,
AK-50, AK-52 und AK-195/AK-196.

#### AK-211
*Verlauf: A24 Z6942 · zuletzt geaendert durch T-127, 2026-09-08*

**AK-211** *(zwei Anstriche, nicht drei — ersetzt AK-197.)* Je Oeffnung des
Pickers gibt es hoechstens zwei Zustaende der Anzeige: den ohne Antwort
(leeres Raster) und den mit ihr. Alles, was an der Antwort haengt — **die
Karten selbst**, die Zahlen beider Wertzeilen, die `BEST FOR …`-Chips, die
Ordnung samt AK-195-Vorziehung, die Kopfzeile und die Laufbefundzeile —
erscheint in **einem** Anstrich. Es gibt keinen Zwischenzustand, in dem
Karten ohne Zahlen stehen, in dem ein Teil der Karten steht, oder in dem die
Wartezeile neben Karten steht.
*Toetende Mutation:* Karten und Zahlen in zwei Schritten setzen.

#### AK-212
*Verlauf: A24 Z6951 · zuletzt geaendert durch T-127, 2026-09-08*

**AK-212** *(das leere Raster ist ein Zustand, kein Nichts — ersetzt AK-198;
dies ist der Waechter **W2**.)* Wird der Picker mit einer Spur geoeffnet,
die nie antwortet, so gilt dauerhaft: im Rollbereich steht **kein**
Kartenwidget — keine Reliktkarte und auch nicht die Custom-Kachel —, kein
Reliktname, keine Zahl, kein Chip; keine Karte ist mit Tab erreichbar; an
der Stelle der linken oberen Karte steht die eine Zeile
`Your relics appear here.`; die Kopfzeile ist leer; Zeile 3 traegt den
Wartesatz aus AK-214; die beiden Textzeilen aus AK-201 stehen vollstaendig;
und der Dialog ist bedienbar nach AK-213.
*Toetende Mutation:* die Rechnung wieder synchron vor dem Oeffnen — die
Karten stehen sofort. Kein Zeitmass.
*Ausnahme, ausdruecklich:* bietet der Picker beim ersten Anstrich keine
einzige Reliktkarte an (leerer Slot, oder ein voreingestellter Filter ohne
Treffer), gibt es keinen Wartezustand und keine Wartezeile; der Dialog
zeichnet einmal.

#### AK-213
*Verlauf: A24 Z6966 · zuletzt geaendert durch T-127, 2026-09-08*

**AK-213** *(waehrend der Leere ist nichts gesperrt und nichts geht
verloren — nimmt die `Sort by`-Zusage aus AK-199 auf.)* Im Zustand aus
AK-212 sind Filterfeld, `Sort by`, Bildlaufleiste und jedes andere
Bedienelement des Dialogs freigegeben (`isEnabled()`), keines ist
ausgegraut, und der Dialog traegt keinen Wartecursor. `Sort by` steht
unveraendert auf der gewaehlten Zielrichtung und wird nicht auf `Name`
umgestellt. Text, den der Spieler waehrend der Leere in das Filterfeld
tippt, steht danach unveraendert im Feld und wirkt auf die Karten, sobald
sie erscheinen; er loest keine zweite Frage aus (AK-206). Esc schliesst den
Dialog.
*Toetende Mutation:* Filterfeld oder `Sort by` waehrend der Leere sperren.

#### AK-214
*Verlauf: A24 Z6977 · zuletzt geaendert durch T-127, 2026-09-08*

**AK-214** *(Zeile 3 behauptet keine Rangfolge und zaehlt nichts, was nicht
dasteht — ersetzt AK-200.)* Solange keine Karte steht, traegt Zeile 3
woertlich `Working out what each relic is worth with <slot> empty` und
**nichts sonst**: keine Zaehlung `x of y relics`, keinen Filterhinweis,
keinen Favoritenhinweis, keinen Rechtsklick-Satz. Der Nebensatz
`ranked against your build with <slot> empty` erscheint nicht, bevor die
Karten stehen. Die Wartefassung wird am Standardmass des Pickers **nicht
hoeher gezeichnet** als die fertige — gemessen, mit Umgebung genannt
(L-009: Stil, Skalierung, physisch oder logisch); ist sie es doch, wird die
**Warte**fassung gekuerzt, nicht die fertige.
*Toetende Mutation:* den Zaehlteil der Zeile waehrend der Leere stehen
lassen.

#### AK-215
*Verlauf: A24 Z6989 · zuletzt geaendert durch T-127, 2026-09-08*

**AK-215** *(was erscheinen darf, und wo — ersetzt AK-202.)* Zwischen dem
ersten und dem zweiten Anstrich aendert sich **ausserhalb** des Rollbereichs
kein Widgetbestand: kein Fortschrittsbalken, kein Wartetext als eigene
Zeile, kein Wartecursor, kein Spinner, keine animierten Punkte, keine
Laufschrift, kein zweiter Dialog, kein gesperrtes Bedienelement, keine
Zeitschwelle, kein Verzoegerungstimer. **Innerhalb** des Rollbereichs gibt
es genau **einen** Wechsel: die Zeile `Your relics appear here.` weicht den
Karten. **Ersetzt AK-09 und AK-10 fuer den Picker**, nicht fuer die Advisor
bar.
*Toetende Mutation:* einen Fortschrittsbalken oder eine
Verzoegerungsschwelle einbauen.

#### AK-216
*Verlauf: A24 Z7000 · zuletzt geaendert durch T-127, 2026-09-08*

**AK-216** *(die Groesse steht beim ersten Anstrich, nicht bei der Antwort —
ersetzt die Groessenhaelfte von AK-203; die scharfe Stelle dieser
Entscheidung.)* Der Dialog nimmt seine Aussenmasse beim **ersten** Anstrich
an, und zwar dieselben, die er mit denselben Karten in der beraterfreien
Ordnung annaehme; ueber den Wechsel zum zweiten Anstrich hinweg sind
`width()` und `height()` identisch, und er misst sich kein zweites Mal
(`_sized`). Die Hoehe jeder einzelnen Karte ist unveraendert (AK-41).
*Aufbau:* derselbe Slot zweimal geoeffnet, einmal mit einer Spur, die nie
antwortet, einmal mit einer, die sofort antwortet — beide Male dieselben
Aussenmasse.
*Toetende Mutation:* die Groesse erst beim Eintreffen der Antwort bestimmen
(der Dialog waechst nach dem Oeffnen); `_sized` beim zweiten Anstrich
zuruecksetzen.
*Messauflage an den `developer` (L-009):* er misst `wanted_height` fuer
dieselbe Kartenliste zweimal — einmal auf dem heutigen Weg (Karten im
Raster) und einmal auf dem Weg des Wartezustands — und nennt **beide Zahlen
mit ihrer Umgebung** (Qt-Stil, Skalierung, physisch oder logisch, Bestand
des Nutzers, Standardmass des Pickers). **Jede Differenz ausser 0 px ist ein
Befund und kommt zurueck zu mir**, nicht in eine Nachbesserung.

#### AK-217
*Verlauf: A24 Z7019 · zuletzt geaendert durch T-127, 2026-09-08*

**AK-217** *(Fokus und Bildlauf — ersetzt die zweite Haelfte von AK-203.)*
Beim Erscheinen der Karten behaelt das Bedienelement mit dem Tastaturfokus
ihn; der Fokus springt **nicht** auf eine Karte, und der Bildlauf steht
danach am Anfang. Fuer jeden **spaeteren** Neubau des Rasters in derselben
Oeffnung — Filteranschlag, Zielrichtungswechsel, Favoritenvergabe — gilt
unveraendert AK-52: der Bildlaufwert bleibt, und lag der Fokus auf einer
Reliktkarte, liegt er danach auf der Karte desselben Relikts.
*Toetende Mutation:* den Fokus beim Erscheinen der Karten auf die erste
Karte legen.

#### AK-218
*Verlauf: A25 Z7159 (Fassung 2) · zuletzt geaendert durch T-135, 2026-09-08*

*Ueberholt: Fassung 1 (A24 Z7036) durch Fassung 2 - A25 Z7159 (T-135)*

**AK-218** *(die Leere ist nie das letzte Wort — Fassung 2, T-135; ersetzt
Fassung 1 aus T-127 §9, die dort woertlich stehen bleibt.)*

Eine Oeffnung des Pickers, die ueberhaupt eine Reliktkarte anzubieten hat,
**zeigt Karten**. Sie kommt auf genau einem von zwei Wegen dorthin, und
welcher es war, sieht der Spieler nur an der Wartezeile:

**(a) Die Antwort war beim Fragen schon bekannt.** Sie kommt als
Rueckgabewert (Nachtrag IX-1.3), es entsteht **kein** Wartezustand, und das
Raster steht **im ersten Anstrich** vollstaendig: Karten in der sortierten
Ordnung, beide Wertzeilen, Chips, Kopfzeile, Zeile 3 in der fertigen
Fassung. Die Zeile `Your relics appear here.` und der Wartesatz aus AK-214
erscheinen dabei **nie**, auch nicht fuer einen Anstrich. Das ist der eine
Anstrich, den AK-211 mit „hoechstens zwei Zustaende" ausdruecklich erlaubt —
ein Regelfall, kein Sonderfall.

**(b) Die Frage lief.** Bis zu ihrem Ende gilt AK-212 (das leere Raster als
Zustand). Sie endet in genau einem von drei Ausgaengen — `ready`, `failed`,
`stopped` —, und **jeder der drei fuellt das Raster**: `ready` mit der
sortierten Ordnung; `failed` und `stopped` mit der Namensordnung, `—` in
beiden Wertzeilen, ohne Chip, unter der Kopfzeile aus AK-208, bei `stopped`
mit `<reason>` = `the search was stopped`.

**Ein Ende, nach dem das Raster leer bleibt, ist ein Fehler** — gleich ob es
ein Signal war, ein Rueckgabewert oder keines von beidem. Das ist der Satz,
an dem diese Entscheidung haengt; die Aufzaehlung der Wege ist ihm
nachgeordnet und **waechst mit**, wenn ein dritter Weg hinein gebaut wird.

*Nicht Gegenstand dieses Kriteriums, je mit der Stelle, die es regelt:* die
Oeffnung, die keine einzige Reliktkarte anzubieten hat (Ausnahme in AK-212);
die Frage, **solange** sie laeuft (AK-212); die Antwort einer frueheren
Oeffnung (AK-207); und das Schliessen des Hauptfensters waehrend des Dialogs
— der Picker ist modal (`relicpicker.py`, `setModal(True)`), und wo kein
Dialog mehr steht, ist kein Raster zu fuellen. `shutdown` ist deshalb eine
Ausnahme des **Vertrags** (Nachtrag X-0), aber kein Fall dieses Kriteriums.

*Aufbau:* vier Vorrichtungen — eine Spur, die sofort antwortet; eine, die
`failed` meldet; eine, die `stopped` meldet; und **dieselbe Spur ein zweites
Mal fuer denselben Slot geoeffnet**, ohne dass sich dazwischen etwas
geaendert hat (Weg (a)).

*Toetende Mutationen:* `stopped` nicht behandeln — das Raster bleibt leer;
und den Treffer ausschalten, so dass `ask_and_answer_if_known` immer `None`
liefert — die zweite Oeffnung zeigt dann eine Wartezeile, und Weg (a) wird
rot.

#### AK-219
*Verlauf: A24 Z7047 · zuletzt geaendert durch T-127, 2026-09-08*

**AK-219** *(zwei Zeichen, zwei Aussagen — ersetzt AK-209.)* Auf einer Karte
bedeuten `—` „nicht gemessen" und `no change` „gemessen, ohne Wirkung"; sie
stehen nie fuereinander. Ein drittes Zeichen fuer „laeuft noch" gibt es auf
dem Bildschirm nicht mehr: **keine im Rollbereich stehende Karte traegt je
`…` (`PENDING`)** — solange die Frage laeuft, steht keine Karte da. Die
Konstante selbst bleibt als Platzhalter beim Bau der Karte (§3.3, AK-41).
*Toetende Mutation:* das Raster waehrend der Leere mit Karten fuellen, die
`…` tragen — das ist die T-124-Fassung, und sie muss rot werden.

---

## Bereich 6 — Die Sprache der Zahlen: Vorschlagsblock, `Why`-Dialog, Statuszeile

Jede Zahl, die der Berater zeigt, nennt ihre Bezugsgroesse und ihre Lesart; und
jeder Effekt, zu dem keine Zahl passt, bekommt trotzdem seine Zeile, statt zu
verschwinden. Dieser Bereich beschreibt die Wortlaute des Vorschlagsblocks, des
`Why`-Dialogs, der Statuszeile und der Zeile 4 im Picker.

*Herkunft im Verlauf: A09 (T-052) · A16 (T-078) · A17 (T-080) · A18 (Director) · A19 (T-084) · A20 (T-086) · A21 (T-092)*

### 6.1 Die Bezugsgroesse in Zeile 4 und im `Why`-Dialog

#### AK-63
*Verlauf: A19 Z4554 (AK-162) und Z4563 (AK-163) · zuletzt geaendert durch T-084, 2026-09-07*

*Ueberholt: T-052-Fassung (A05 Z1346) vollstaendig durch AK-162 (erste Haelfte) und AK-163 (zweite Haelfte) - A19 Z4554/Z4563 (T-084)*

**AK-162** *(Registry-Haelfte, ersetzt die erste Haelfte von AK-63.)*
Zeile 4 des Pickers und Punkt 4 des `Why`-Dialogs zeigen die Saetze aus
`Goal.scope` der gewaehlten Zielrichtung wortgleich, in Tupel-Reihenfolge,
vollstaendig — daneben kein im UI-Code verdrahteter Vorbehaltssatz.
Pruefweg: `advisor/goals.py` um einen sechsten `scope`-Satz erweitern; er
steht danach an beiden Orten, ohne dass eine UI-Zeichenkette angefasst
wurde. *Rot-vorher:* eine Umsetzung, die den Attack-Rating-Vorbehalt als
Konstante in den Picker schreibt, bleibt bei `Minimise damage taken` auf dem
falschen Satz stehen.

**Dazu A19 Z4563 — AK-163:**

**AK-163** *(Ergebnis-Haelfte im Picker, ersetzt die zweite Haelfte von
AK-63.)* Zeile 3b traegt zuerst jeden String aus `Baseline.unknowns` der
Zielrichtung aus `SlotPool.rank_by`, danach jeden String aus
`SlotPool.unknowns`, jeweils wortgleich und in Tupel-Reihenfolge, in einem
Block; sie entfaellt genau dann, wenn beide leer sind. *Rot-vorher:* die
heutige AK-63-Fassung liest nur `SlotPool.unknowns` — ein Lauf **ohne**
Referenzwaffe zeigt dann keine einzige Zeile darueber, dass ohne Waffe
gerechnet wurde, obwohl `goals.py` den Satz liefert.

<sub>Fundstelle sinngemaess: das Register nennt Z4563; hier steht der Absatz ab Z4563 (Verlauf Z4632).</sub>

### 6.2 Die drei Saetze in `SlotPool.unknowns`

#### AK-67
*Verlauf: A09 Z1651 · zuletzt geaendert durch T-052, 2026-09-05*

**AK-67** `SlotPool.unknowns` traegt fuer den heutigen Bestand **bis zu drei**
Saetze, in dieser Reihenfolge, falls mehrere zutreffen — Handle-Zeile, dann
konditionale Zeile, dann QA-113-Zeile (steigende Beteiligung an der Rechnung:
nie im Pool → im Pool, aber gegen eine Bedingung auf 0 gesetzt → im Pool,
aber durch eine fehlende Rechnungsart auf 0 gesetzt). Alle drei folgen den
Wortlauten oben, wortgleich, mit `{n}` ersetzt durch die tatsaechliche Anzahl
und Singular/Plural korrekt gewaehlt; die Handle-Zeile nennt „of this
colour" ausschliesslich, wenn `slot.colour` nicht der weisse Platzhalter ist,
sonst „of any colour". **Keine Obergrenze unter drei**: faellt ein vierter
Fall dieser Art je an, braucht er eine eigene AK, keine Kuerzung der
bestehenden drei. Alle zutreffenden Saetze stehen **in derselben Zeile 3b**
(bzw. demselben Slot-Abschnitt in §3.4 Punkt 2), durch ein Leerzeichen
getrennt, als ein einziger flexibel umbrechender Textblock — Zeile 3b war
nie ein festes Zeilenraster, sondern ein wachsender Fliesstext wie Zeile 4
selbst (dort schon bis zu fuenf Saetze fuer eine Zielrichtung); ein dritter
Satz verlangt deshalb keine neue Struktur, nur mehr Zeilenumbruch in
derselben `QLabel`.

### 6.3 Form, Fluche und Sprache des Vorschlagsblocks

#### AK-133
*Verlauf: A16 Z3714 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-133** Der Vorschlagsblock zeigt **keinen** zusammenfassenden
Begruendungssatz. Die Zeichenkette `Chosen for` kommt im Programm nicht
vor, und keine gezeigte Zeile endet auf eine Kuerzungsformel (`and {n}
more`, `…` am Zeilenende ausserhalb der Statuszeile).

#### AK-134
*Verlauf: A16 Z3718 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-134** Die Zahl der in einer Slotgruppe gezeichneten Effekt- und
Fluchzeilen ist gleich der Zahl der Zeilen, die das Ergebnis fuer diesen
Slot traegt. Keine wird ausgelassen, keine zusammengefasst. *Ersetzt
AK-18*, dessen "genau ein Begruendungssatz je Slot" mit §1 aufgehoben ist;
A5 und AK-19 gelten unveraendert weiter.

#### AK-135
*Verlauf: A16 Z3723 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-135** Keine gezeichnete Zeile nennt die Slotnummer oder den
Reliktnamen, die im Kopf ihrer Gruppe stehen. Die Slotnummer erscheint
**einsbasiert** und **nur** im Kopf der Gruppe im `Why`-Dialog.

#### AK-136
*Verlauf: A16 Z3726 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-136** Jede Zeile folgt einer der Fassungen aus §2 bzw. §3, woertlich,
einschliesslich der Satzzeichenregel: eine Zeile, die auf einer Zahl oder
auf `counted against it` endet, traegt keinen Punkt; eine Zeile, die auf
einem Satz endet, traegt einen.

#### AK-137
*Verlauf: A16 Z3730 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-137** `, counted against it` steht genau an den Zeilen, deren Beitrag
ihre Groesse nach `model.is_better_lower` schlechter macht — nie nach dem
Vorzeichen entschieden. Pruefweg: ein Fall mit einem Feld, das kleiner
besser ist (FP-Kosten), und eine Senkung darin; die Zeile traegt den Zusatz
**nicht**.

#### AK-138
*Verlauf: A16 Z3738 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-138** Fuer jede vorgeschlagene Kopie gilt: die Menge der Fluchnamen in
ihrer Slotgruppe ist **gleich** der Menge ihrer `curse_ids`, ueber den
Datensatz in Namen aufgeloest. Kein Fluch fehlt, keiner steht doppelt, und
jeder steht in genau einer der drei Fuellungen aus §3. Pruefweg: die
Aufloesung laeuft unabhaengig von `explain.py` ueber `ctx.data["effects"]`
— derselbe Weg, den `test_the_reasons_name_only_effects_the_suggestion_brought`
schon geht.

#### AK-139
*Verlauf: A16 Z3745 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-139** `AdvisorResult` traegt ein Feld fuer die Fluche ohne Zahl
(`curses_without_a_figure`), getrennt von `not_counted`. Es enthaelt genau
die Fluche der vorgeschlagenen Kopien, zu denen keine Zeile nach §2
entstanden ist — gepruefte Gegenrichtung: ein Fluch mit einer Zeile ist
**nicht** darin.

#### AK-140
*Verlauf: A17 Z4294 (AK-157, fortgeschrieben) · zuletzt geaendert durch T-080, 2026-09-06*

**AK-156** Keine stumme Zeile benutzt `✦`, `CURSE`/`BAD`, `⚠` oder eine
Warnfarbe; die einzige verwendete Farbrolle ist `MUTED`, die Schriftgroesse
ist die der uebrigen Effektzeilen (11 px). Pruefweg: der Text der Zeile ohne
jede Formatierung gelesen sagt vollstaendig, was sie sagt.

<sub>Fundstelle sinngemaess: das Register nennt Z4294; hier steht der Absatz ab Z4292 (Verlauf Z4361).</sub>

#### AK-141
*Verlauf: A16 Z3754 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-141** Der Schlusssatz mit der `✦`-Legende steht **genau einmal** je
`Why`-Dialog und in **keinem** Vorschlagsblock.

#### AK-142
*Verlauf: A16 Z3759 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-142** `not_counted` enthaelt ausschliesslich konditionale Effekte nach
AD-010 (`Build.situational`, `live == False`). Der Satz `The game files
carry no numbers for these, so they counted for nothing:` erscheint
nirgends mehr. *Ersetzt AK-21.*

#### AK-143
*Verlauf: A16 Z3763 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-143** Die beiden Klauseln aus 4.9a und 4.9b erscheinen woertlich wie
in §5, in dieser Reihenfolge, jede nur wenn ihre Menge nicht leer ist, mit
richtig gewaehltem Singular/Plural. Der ungekuerzte Statuszeilentext steht
im Tooltip.

#### AK-144
*Verlauf: A16 Z3770 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-144** Der gesamte vom Berater gezeigte Text (Block, `Why`-Dialog,
Statuszeile, Tooltips) enthaelt keines der Woerter `field`, `pool`,
`handle`, `beam`, `scorer`, `source`, `snapshot`, `slot_index`,
`not_counted`, `contribution`. Pruefweg: der ausgelesene Text eines Laufs
gegen eine Wortliste.

#### AK-145
*Verlauf: A16 Z3775 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-145** Die Halte-Zeile und die `data_note` folgen §8 woertlich, in
allen dort genannten Fuellungen.

#### AK-146
*Verlauf: A16 Z3777 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-146** Die Zaehlzeile im Kopf jeder Slotgruppe folgt §6 woertlich;
`{n}` zaehlt **Effekte**, nicht Zeilen. Pruefweg: ein Effekt, der zwei
nicht zusammenfassbare Groessen bewegt, ergibt zwei Zeilen und erhoeht
`{n}` um eins.

#### AK-147
*Verlauf: A17 Z4236 (fortgeschrieben) · zuletzt geaendert durch T-080, 2026-09-06*

5. **Jede stumme Zeile erreicht die Anzeige mit ihrer Fuellung** (a, a2, b, c,
 d, e) **als eigener Auskunft** und mit den einzusetzenden Namen
 (`{owner}`, `{hero}`). Das Fenster darf die Fuellung **nicht** aus dem Text
 erschliessen — kein Suchen nach `works only for`, kein Vergleich von
 Zeichenketten. Das ist AK-147, hier fortgeschrieben.
6. **Die Fuellung kommt aus derselben Rechnung, die `Build.qualitative` und
 `Build.situational` fuellt** (AD-015: keine zweite Meinung ueber denselben
 Effektsatz). `explain.py` liest sie ab, es liest den Effektsatz nicht ein
 zweites Mal.

<sub>Fundstelle sinngemaess: das Register nennt Z4236; hier steht der Absatz ab Z4232 (Verlauf Z4301).</sub>

#### AK-148
*Verlauf: A16 Z3790 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-148** In keiner Slotgruppe erscheint ein Fluchname zweimal.
Insbesondere zeichnet die Oberflaeche nicht `reasons` **und** `curses`.

#### AK-149
*Verlauf: A16 Z3792 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-149** AK-29 und AK-30 gelten unveraendert fuer jede neue Zeile: jedes
neue Textelement setzt `setTextFormat()` ausdruecklich, und ein Relikt-,
Effekt- oder Fluchname mit `<b>x</b><img src=x>&lt;` erscheint in Block,
Dialog, Statuszeile und Tooltip buchstabengetreu.

### 6.4 Der stumme Effekt und die Zaehlzeile

#### AK-150
*Verlauf: A17 Z4319 (AK-160) · zuletzt geaendert durch T-080, 2026-09-06*

*Ueberholt: vollstaendig durch AK-160 - A17 Z4319 (T-080); die Schaetzwerte sind durch Messwerte ersetzt*

**AK-160** *Ersetzt AK-150 vollstaendig.* Der schlechteste Fall ist
**gemessen**, nicht geschaetzt, und er ist groesser als AK-150 annahm:

| Groesse | AK-150 nahm an | gemessen (Umgebung §0) |
|---|---|---|
| Zeilen je Slotgruppe | 7 Effekt- + 2 Fluchzeilen = 9 | **14** gezeichnete Zeilen |
| schlimmstes Relikt | unbenannt | `Deep Grand Tranquil Scene`: 3 Effekte → **9** Zahlzeilen, 3 Fluche → **4** Zahlzeilen + **1** stumme |
| dazu je Gruppe | — | Reliktname + Zaehlzeile = **16 Zeilen** in einer Karte |
| laengste Zahlzeile | ~105 Zeichen geschaetzt | **106** Zeichen (`[Wylder] Improved Intelligence and Faith, Reduced Strength and Dexterity: Dexterity -5, counted against it`) |
| laengste Zeile ueberhaupt | nicht bedacht | **rund 150** Zeichen: ein stummer Effekt mit 101-Zeichen-Namen plus Fuellung (b) |
| laengster Reliktname | "laengster des Spielstands" | `Deep Polished Tranquil Scene`, 28 Zeichen |

**Zu pruefen:** sechs belegte Slots, darunter die Kopie von `Deep Grand
Tranquil Scene`, die diese 14 Zeilen erzeugt. In der mittleren Spalte des
Build planner entsteht **keine waagerechte** Bildlaufleiste, keine Zeile ist
abgeschnitten, keine bricht mitten in einem Begriff (AK-73), jede ist durch
senkrechtes Scrollen erreichbar, und die 150-Zeichen-Zeile **bricht um**,
statt elidiert zu werden (4.14). Zu messen bei Fensterbreite **1320 px**
(Startbreite) und UI scale `Automatic` **sowie** 150 %, auf einem
100-%-Bildschirm, unter dem Qt-Stil, mit dem das Programm ausgeliefert wird.
**Die Messung nennt Plattform, Stil, Skalierung und ob die Zahlen physisch
oder logisch sind** — ohne diese Angaben zaehlt sie nicht (L-009).

#### AK-151
*Verlauf: A17 Z4271 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-151** Jeder Effekt einer vorgeschlagenen Kopie, zu dem keine Zeile nach
T-078 §2 entstanden ist, erscheint **mit Namen** in der Slotgruppe seines
Slots, **genau einmal**, mit `•`, in der Ordnung des Relikts. Gegenrichtung
geprueft: ein Effekt **mit** Zahlzeile bekommt **keine** stumme Zeile. Gilt
im Vorschlagsblock **und** im `Why`-Dialog, mit identischem Text.

#### AK-152
*Verlauf: A17 Z4276 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-152** Der Wortlaut jeder stummen Zeile ist einer der aus §4, woertlich,
mit Punkt am Ende. Die Fuellung wird in der dort genannten Reihenfolge
bestimmt (a → a2 → b → c → d → e), und ein Effekt, dessen Besitzer die
gespielte Figur **ist**, bekommt nie Fuellung (a). Pruefweg: ein
`[Wylder]`-Effekt ohne Zahl ergibt auf Wylder (d), auf Duchess (a).

#### AK-153
*Verlauf: A17 Z4281 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-153** `AdvisorResult` traegt `effects_without_a_figure` getrennt von
`curses_without_a_figure` und von `not_counted`. Es enthaelt genau die
Effekte der vorgeschlagenen Kopien ohne Zeile nach T-078 §2.

#### AK-154
*Verlauf: A17 Z4284 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-154** Die stummen Zeilen der Fuellung (b) und die Liste aus 4.9b
entstehen aus **einer** Menge (`Build.situational`, `live == False`).
Pruefweg: dieselbe Bedingung als erfuellt erklaeren — der Effekt
verschwindet in **demselben** Lauf aus beiden, oder aus keinem.

#### AK-155
*Verlauf: A17 Z4288 + A21 Z5516 (gilt in beiden Lesarten) · zuletzt geaendert durch T-092, 2026-09-07*

**AK-155** In jeder Slotgruppe gilt `{total} − {n}` **genau** gleich der
Zahl der gezeichneten stummen Zeilen — ohne Ausnahme, auch fuer Effekte
ohne Namen im Datensatz (Fuellung e). Pruefweg: ein Ergebnis mit einer
Effekt-Id, die der Datensatz nicht kennt.

**Dazu A21 Z5516 — gilt in beiden Lesarten:**

**AK-155 haelt in beiden Lesarten**: `{total} − {n}` ist weiterhin genau die
Zahl der stummen Zeilen, weil die Lesart Zeilen zwischen „mit Zahl" und
„stumm" verschiebt und keine erzeugt.

#### AK-156
*Verlauf: A17 Z4292 + A18 Z4414 (Ausnahme fuer Fuellung (a)) · zuletzt geaendert durch Director/App Designer, 2026-09-06*

*Ueberholt: fuer Fuellung (a) durch die Director-Korrektur - A18 Z4414 (06.09.2026); fuer (a2), (b), (c), (d), (e) unveraendert*

**AK-156** Keine stumme Zeile benutzt `✦`, `CURSE`/`BAD`, `⚠` oder eine
Warnfarbe; die einzige verwendete Farbrolle ist `MUTED`, die Schriftgroesse
ist die der uebrigen Effektzeilen (11 px). Pruefweg: der Text der Zeile ohne
jede Formatierung gelesen sagt vollstaendig, was sie sagt.

**Dazu A18 Z4414 — Ausnahme fuer Fuellung (a):**

**AK-156 gilt unveraendert fuer alle uebrigen Fuellungen** (a2, b, c, d, e):
kein `✦`, kein `CURSE`/`BAD`, kein `⚠`, keine Warnfarbe, nur `MUTED`.
Fuellung (a) ist die benannte Ausnahme, und sie ist keine Warnung, sondern
dieselbe Aussage, die das Programm anderswo schon macht.

#### AK-157
*Verlauf: A17 Z4296 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-157** Keine stumme Zeile behauptet etwas ueber die Spieldateien; die
Zeichenketten `carry no numbers` und `carries no numbers` kommen im Berater
weiterhin nicht vor (AK-140 fortgeschrieben), und keines der Woerter aus
AK-144 erscheint in ihr.

#### AK-158
*Verlauf: A17 Z4303 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-158** Die Zaehlzeile aus T-078 §6 steht in **jeder** Slotgruppe, auch
wenn jeder Effekt darunter genannt ist, und benutzt die beiden neuen
Fuellungen aus §5 in genau den dort genannten Faellen. Pruefweg: eine Kopie
ohne Effektrollen (`Murk`) und eine Kopie, deren Effekte und Fluche alle
stumm sind.

#### AK-159
*Verlauf: A17 Z4311 · zuletzt geaendert durch T-078, 2026-09-06*

**AK-159** Die Menge der Fluchnamen im **Vorschlagsblock** einer Slotkarte
ist gleich der Menge der `curse_ids` der vorgeschlagenen Kopie, in Namen
aufgeloest — nicht nur im `Why`-Dialog. Verglichen werden **Namen, nicht
Zeilen**: ein Fluch, der zwei Groessen bewegt, steht in zwei Zeilen und ist
ein Name. (Das ist AK-138 fuer den Block; beide gelten.)

#### AK-160
*Verlauf: A17 Z4319 · zuletzt geaendert durch T-092, 2026-09-07 (AK-189 schreibt fort)*

*Ueberholt: **widerspruechlich** - als schlechtester Fall ueberholt durch AK-189 (A21 Z5827, T-092); zusaetzlich schreibt sein Messfenster `1320 px (Startbreite)` vor, obwohl A14 Z2555 (T-071) die feste Startbreite aufgehoben hat*

**AK-160** *Ersetzt AK-150 vollstaendig.* Der schlechteste Fall ist
**gemessen**, nicht geschaetzt, und er ist groesser als AK-150 annahm:

| Groesse | AK-150 nahm an | gemessen (Umgebung §0) |
|---|---|---|
| Zeilen je Slotgruppe | 7 Effekt- + 2 Fluchzeilen = 9 | **14** gezeichnete Zeilen |
| schlimmstes Relikt | unbenannt | `Deep Grand Tranquil Scene`: 3 Effekte → **9** Zahlzeilen, 3 Fluche → **4** Zahlzeilen + **1** stumme |
| dazu je Gruppe | — | Reliktname + Zaehlzeile = **16 Zeilen** in einer Karte |
| laengste Zahlzeile | ~105 Zeichen geschaetzt | **106** Zeichen (`[Wylder] Improved Intelligence and Faith, Reduced Strength and Dexterity: Dexterity -5, counted against it`) |
| laengste Zeile ueberhaupt | nicht bedacht | **rund 150** Zeichen: ein stummer Effekt mit 101-Zeichen-Namen plus Fuellung (b) |
| laengster Reliktname | "laengster des Spielstands" | `Deep Polished Tranquil Scene`, 28 Zeichen |

**Zu pruefen:** sechs belegte Slots, darunter die Kopie von `Deep Grand
Tranquil Scene`, die diese 14 Zeilen erzeugt. In der mittleren Spalte des
Build planner entsteht **keine waagerechte** Bildlaufleiste, keine Zeile ist
abgeschnitten, keine bricht mitten in einem Begriff (AK-73), jede ist durch
senkrechtes Scrollen erreichbar, und die 150-Zeichen-Zeile **bricht um**,
statt elidiert zu werden (4.14). Zu messen bei Fensterbreite **1320 px**
(Startbreite) und UI scale `Automatic` **sowie** 150 %, auf einem
100-%-Bildschirm, unter dem Qt-Stil, mit dem das Programm ausgeliefert wird.
**Die Messung nennt Plattform, Stil, Skalierung und ob die Zahlen physisch
oder logisch sind** — ohne diese Angaben zaehlt sie nicht (L-009).

> **Widerspruechlich — die Entscheidung steht beim App Designer aus.**
> Beide Fassungen stehen oben bzw. an den genannten Stellen nebeneinander;
> dieser Abschnitt loest den Vorrang **nicht** auf.

#### AK-161
*Verlauf: A17 Z4344 + A21 Z5537 (je Lesart getrennt) · zuletzt geaendert durch T-092, 2026-09-07*

**AK-161** Die Zeilenzahl je Vorschlag wird nach dem Einbau **neu gemessen**
und im Bericht genannt. Die Zahlen aus T-067 (10 bis 43 Zeilen je Vorschlag,
Median 21) sind **vor** den stummen Zeilen entstanden und tragen nicht mehr;
ein Vorschlag kann jetzt bis zu sechs Slotgruppen mit je bis zu 16 Zeilen
haben.

**Dazu A21 Z5537 — je Lesart getrennt:**

Grund: ein konditionaler Fluch, der stumm **eine** Zeile war
(`✦ {name}: no number here shows what this costs.`), wird als erfuellte
Bedingung zu **einer Zeile je bewegter Groesse** — die
Damage-Negation-Flueche bewegen acht Felder. Die 14 Zeilen aus **AK-160**
sind damit **nicht mehr der schlechteste Fall**; AK-160 bleibt als Messung
seiner Umgebung gueltig und wird durch AK-189 fortgeschrieben. **AK-161
(nach dem Einbau neu messen) gilt fuer beide Lesarten getrennt.**

<sub>Fundstelle sinngemaess: das Register nennt Z5537; hier steht der Absatz ab Z5532 (Verlauf Z5601).</sub>

### 6.5 Registry, `budget_note` und der Satz 4.7

#### AK-162
*Verlauf: A19 Z4554 · zuletzt geaendert durch T-084, 2026-09-07 (A21 Z5600: gilt unveraendert)*

**AK-162** *(Registry-Haelfte, ersetzt die erste Haelfte von AK-63.)*
Zeile 4 des Pickers und Punkt 4 des `Why`-Dialogs zeigen die Saetze aus
`Goal.scope` der gewaehlten Zielrichtung wortgleich, in Tupel-Reihenfolge,
vollstaendig — daneben kein im UI-Code verdrahteter Vorbehaltssatz.
Pruefweg: `advisor/goals.py` um einen sechsten `scope`-Satz erweitern; er
steht danach an beiden Orten, ohne dass eine UI-Zeichenkette angefasst
wurde. *Rot-vorher:* eine Umsetzung, die den Attack-Rating-Vorbehalt als
Konstante in den Picker schreibt, bleibt bei `Minimise damage taken` auf dem
falschen Satz stehen.

#### AK-163
*Verlauf: A19 Z4563 + A21 Z5606 · zuletzt geaendert durch T-092, 2026-09-07*

*Ueberholt: das Rot-vorher von AK-163 - AK-190, A21 Z5606 (T-092); Regel und Pruefweg unveraendert*

**AK-163** *(Ergebnis-Haelfte im Picker, ersetzt die zweite Haelfte von
AK-63.)* Zeile 3b traegt zuerst jeden String aus `Baseline.unknowns` der
Zielrichtung aus `SlotPool.rank_by`, danach jeden String aus
`SlotPool.unknowns`, jeweils wortgleich und in Tupel-Reihenfolge, in einem
Block; sie entfaellt genau dann, wenn beide leer sind. *Rot-vorher:* die
heutige AK-63-Fassung liest nur `SlotPool.unknowns` — ein Lauf **ohne**
Referenzwaffe zeigt dann keine einzige Zeile darueber, dass ohne Waffe
gerechnet wurde, obwohl `goals.py` den Satz liefert.

**Dazu A21 Z5606 — ergaenzt:**

**AK-163 gilt unveraendert in seiner Regel, verliert aber seinen einzigen
heutigen Inhalt.** Zeile 3b liest weiterhin zuerst `Baseline.unknowns`,
dann `SlotPool.unknowns`; `Baseline.unknowns` ist unter A17 fuer
`max_damage` **leer**, weil der einzige Satz darin nach `scope` gewandert
ist. Zeile 3b entfaellt dann genau so, wie AK-163 es beschreibt, wenn beide
Quellen leer sind. **Das Rot-vorher von AK-163 ist damit erledigt und wird
durch AK-190 ersetzt:** die Gefahr ist nicht mehr, dass der Satz
verschwindet, sondern dass er an **zwei** Orten steht.

#### AK-164
*Verlauf: A19 Z4571 · zuletzt geaendert durch T-084, 2026-09-07 (A21 Z5612: gilt unveraendert)*

**AK-164** *(Ergebnis-Haelfte beim Lauf.)* Punkt 4 des `Why`-Dialogs zeigt
unter den `Goal.scope`-Saetzen `AdvisorResult.unknowns` und danach
`AdvisorResult.weights_note`, wortgleich, jeweils nur wenn nicht leer; die
`unknowns`/`weights_note` der `Baseline`-Eintraege desselben Ergebnisses
werden nicht zusaetzlich gezeichnet. *Rot-vorher:* eine Umsetzung, die ueber
`result.baseline` iteriert **und** `result.unknowns` zeichnet, zeigt
`No armament selected — …` zweimal untereinander.

#### AK-165
*Verlauf: A19 Z4578 · zuletzt geaendert durch T-084, 2026-09-07 (A21 Z5613: gilt unveraendert)*

**AK-165** *(keine Chirurgie, keine Entdopplung.)* Kein Anzeigecode
vergleicht, filtert, sortiert oder entdoppelt die Saetze der beiden
Haelften; er zeichnet sie in der gelieferten Reihenfolge. Pruefbar per Grep
ueber den S10-Code: auf `scope`, `unknowns`, `weights_note` kein `set(`,
kein `sorted(`, kein `if … not in …`. *Rot-vorher:*
`for s in dict.fromkeys(scope + unknowns)` — sieht sauber aus und macht
Pruefpunkt 30 blind.

#### AK-166
*Verlauf: A19 Z4585 · zuletzt geaendert durch T-084, 2026-09-07 (A21 Z5614: gilt unveraendert)*

**AK-166** *(`weights_note` im Picker.)* Solange es kein Bedienelement fuer
die Gewichtung gibt, kommt der Text von `EVEN_WEIGHTING.note` im Picker
**nicht** vor. Pruefweg: ausgelesener Text des Pickers gegen die
Zeichenkette. *Rot-vorher:* eine Umsetzung, die `weights_note` an Zeile 3b
haengt, zeigt bei `Minimise damage taken` zwei Zeilen untereinander, die mit
*"The game data gives no relative frequency of damage types"* anfangen.

#### AK-167
*Verlauf: A19 Z4673 · zuletzt geaendert durch T-084, 2026-09-07 (A20 Z4878: bleibt unveraendert)*

**AK-167** *(Reihenfolge.)* Die sechs Fuellungen werden in der Reihenfolge
(a), (a2), (c), (b), (d), (e) geprueft, erste zutreffende gewinnt.
*Rot-vorher:* die heute gebaute Reihenfolge gibt in der Umgebung §0 **46**
Zeilen `… : only applies under a condition, so no number here.` fuer
Effekte, deren einziger Grund eine nicht gefuehrte Waffengattung ist.

#### AK-168
*Verlauf: A19 Z4678 + A20 Z4880/Z5116 (praezisiert) · zuletzt geaendert durch T-086, 2026-09-07*

*Ueberholt: seine Zahlen durch AK-180 - A20 Z5161 (T-086); Regel und Pruefweg unveraendert*

**AK-168** *(Test von (c).)* Fuellung (c) trifft genau dann zu, wenn der
Effekt eines der vier Armaturenfelder traegt **und** `satisfied_by_weapon`
fuer dieses Feld gegen die gefuehrten Waffentypen falsch ist. *Rot-vorher:*
die heutige Fassung fragt nur nach dem Vorhandensein des Feldes und sagt in
der Umgebung §0 fuer `HP Restoration upon Greatsword Attacks` bei
gefuehrtem Greatsword *"it depends on the armaments you carry"*.

**Dazu A20 Z4880 — praezisiert:**

**AK-168 wird praezisiert, nicht ersetzt.** Sein Test — die *unerfuellte*
Schranke statt des blossen Feldes — ist richtig; er ist nur **zu weit
gefasst**. AK-177 und AK-178 ziehen die Grenze nach.

#### AK-169
*Verlauf: A19 Z4684 + A20 Z5161 (AK-180) · zuletzt geaendert durch T-086, 2026-09-07*

*Ueberholt: die Zahlenreihe durch AK-180 - A20 Z5161 (T-086); Regel und Pruefweg unveraendert*

**AK-169** *(Partition, mit Rezept.)* Die sechs Fuellungen sind eine
**Partition** der stummen Effektzeilen: jede stumme Zeile traegt genau eine,
und die Summe der sechs ist die Zahl der stummen Zeilen. Pruefweg: ueber den
Bestand zaehlen, mit `explain.reasons` selbst; in der Umgebung §0 ergibt das
150 / 0 / 124 / 58 / 94 / 0 = **426** von 845 Effektrollen auf 309 Kopien.
*Rot-vorher:* die Tabelle aus T-080 §3 (150 / 170 / 58 / 48) ist **keine**
Partition — 46 Zeilen sind doppelt gezaehlt, und die 48 ist ein Rest aus
einer Subtraktion, kein Messwert.

**Dazu A20 Z5161 — AK-180:**

**AK-180** *(Partition, Zahlen fortgeschrieben.)* **Ersetzt die Zahlenreihe
in AK-169; dessen Regel und Pruefweg bleiben unveraendert gueltig.** Die
sechs Fuellungen sind eine Partition der stummen Effektzeilen: jede stumme
Zeile traegt genau eine, und die Summe der sechs ist die Zahl der stummen
Zeilen. In Umgebung §0 ergibt das **150 / 0 / 144 / 38 / 94 / 0 = 426**
(A) und **159 / 0 / 149 / 25 / 101 / 0 = 434** (B), jeweils in der
Reihenfolge (a) / (a2) / (b) / (c) / (d) / (e).
*Rot-vorher:* die Zahlenreihe aus AK-169 (150 / 0 / 124 / 58 / 94 / 0)
summiert sich zwar ebenfalls auf 426, verteilt aber 20 Zeilen auf die
falsche Fuellung; die Summe allein ist deshalb **kein** ausreichender
Waechter.

<sub>Fundstelle sinngemaess: das Register nennt Z5161; hier steht der Absatz ab Z5161 (Verlauf Z5230).</sub>

#### AK-170
*Verlauf: A19 Z4733 · zuletzt geaendert durch T-084, 2026-09-07*

**AK-170** Solange `AdvisorResult.budget_note` leer ist, zeichnet die
Oberflaeche dafuer **nichts** — keine Ueberschrift, keinen Platzhalter,
keinen leeren Aufzaehlungspunkt, kein `—`. *Rot-vorher:* ein `Why`-Dialog,
der eine Zeile `Search budget: —` oder einen leeren Absatz zeigt, weil das
Feld bedingungslos gezeichnet wird.

#### AK-171
*Verlauf: A19 Z4738 · zuletzt geaendert durch T-084, 2026-09-07*

**AK-171** Ist das Feld nicht leer, steht sein Satz im `Why`-Dialog als
eigene Zeile unmittelbar unter den Saetzen aus Punkt 4, und **nirgends** in
der Statuszeile. *Rot-vorher:* eine dritte Klausel `  ·  the search was cut
short.` an 4.6 — sie faellt bei der gemessenen Statuszeilenlaenge als erste
der Kuerzung zum Opfer.

#### AK-172
*Verlauf: A19 Z4743 · zuletzt geaendert durch T-084, 2026-09-07*

**AK-172** In `budget_note` steht kein Satz, der in jedem Lauf zutraefe.
Pruefweg: zwei herstellbare Laeufe derselben Zielrichtung; ein Satz, der in
beiden dasteht, gehoert nach `Goal.scope` (AD-025, Pruefpunkt 31).
*Rot-vorher:* `budget_note = "Not every combination was tried."` als feste
Zuweisung in `run.py`.

#### AK-173
*Verlauf: A19 Z4799 · zuletzt geaendert durch T-084, 2026-09-07*

**AK-173** 4.7 lautet buchstabengetreu `Your build changed while this was
working out — use Optimize again.`, mit demselben Gedankenstrich `—` wie
4.8, in Statuszeile, Tooltip und `Why`-Dialog gleich. *Rot-vorher:* der heutige Wortlaut mit dem
nackten `Optimize again.` — der einzige Imperativ ohne Nennung des
Bedienelements unter den vierzehn Zustaenden.

#### AK-174
*Verlauf: A19 Z4804 · zuletzt geaendert durch T-084, 2026-09-07*

**AK-174** Der Satz aus 4.7 erreicht den Nutzer **ungekuerzt in der
Statuszeile**, an der Mindestbreite des Build planner. Reicht der Platz
nicht, gibt die Anordnung der Leiste nach (schmalere Zielwahl, weniger
Abstand), nicht der Satz. Gemessen wird am laufenden Fenster mit
Messumgebung nach L-009 (Stil, Skalierung, physisch oder logisch).
*Rot-vorher:* eine Umsetzung, bei der `— use Optimize again.` als erstes
elidiert und die Handlungsanweisung nur noch im Tooltip steht — eine
Aussage, die nur im Tooltip ankommt, ist keine.

#### AK-175
*Verlauf: A19 Z4812 · zuletzt geaendert durch T-084, 2026-09-07*

**AK-175** Keine Statuszeile des Beraters gibt dem Nutzer die Schuld: keine
Zeile enthaelt `you changed`, `you must`, `please`, `try again` oder ein
Ausrufezeichen. Pruefweg: der ausgelesene Text aller vierzehn Zustaende
gegen diese Wortliste. *Rot-vorher:* `You changed your build while this was
working out!`

#### AK-176
*Verlauf: A19 Z4834 · zuletzt geaendert durch T-084, 2026-09-07*

**AK-176** In `UI_SPEC.md` bezeichnet `Suggest` kein heutiges Bedienelement
mehr: jede verbleibende Fundstelle ist entweder ein Typname (`Suggestion`)
oder ausdruecklich als Verlauf gekennzeichnet. Pruefweg: Volltextsuche nach
`Suggest`, jede Fundstelle einer der beiden Klassen zuordenbar.
*Rot-vorher:* §5.1 in der Fassung vor diesem Nachtrag — wer nur dort liest,
baut einen Knopf, der zwei Namen hat.

### 6.6 Welche Zahl zu welcher Lesart gehoert

#### AK-177
*Verlauf: A20 Z5115 · zuletzt geaendert durch T-086, 2026-09-07*

**AK-177** *(der Test von (c) fragt, was das Programm beantwortet hat.)*
**Praezisiert AK-168, ersetzt es nicht.** Fuellung (c) trifft genau dann
zu, wenn (1) der Effekt ein Feld aus `model.WEAPON_TYPE_GATES` traegt,
`model.satisfied_by_weapon` dafuer gegen die gefuehrten Waffentypen falsch
ist **und** der verlangte Wert der `wep_type` mindestens einer Waffe des
Datenabzugs ist, **oder** (2) der Effekt `startSwordArtsId` traegt.
Pruefweg: ueber den Bestand zaehlen, mit `explain.reasons` selbst; in
Umgebung §0 ergibt (c) **38** (A) bzw. **25** (B).
*Rot-vorher:* eine Umsetzung nach dem Wortlaut von AK-168 — also
`_ARMAMENT_GATES` unveraendert als Trigger von (c) — gibt in Umgebung A
**20** Zeilen und in B **22** Zeilen
`… : it depends on the armaments you carry, so no number here.`, von denen
je **19** zu Effekten gehoeren, die einen **Gegenstand** zu Beginn der
Expedition geben (`Stonesword Key in possession at start of expedition`)
und keine Armatur verlangen.

#### AK-178
*Verlauf: A20 Z5131 · zuletzt geaendert durch T-086, 2026-09-07*

**AK-178** *(`wepTypeTriggerCount` allein nennt keinen Hebel.)* Traegt eine
stumme Zeile als einzige unerfuellte Armaturenschranke
`wepTypeTriggerCount`, so lautet sie
`{effect name}: only applies under a condition, so no number here.`
(Fuellung (b), Wortlaut unveraendert) und enthaelt **nirgends** die
Zeichenfolge `armaments you carry`. Pruefweg: ueber den Bestand alle
stummen Zeilen erzeugen und die Teilmenge pruefen; in Umgebung §0 sind das
**20** Zeilen (A) bzw. **22** (B), und (b) waechst von 124 auf **144** (A)
bzw. von 127 auf **149** (B).
*Rot-vorher:* dieselbe Umsetzung wie bei AK-177 — die Zeile
`Stonesword Key in possession at start of expedition: it depends on the
armaments you carry, so no number here.` ist der einzelne Fall, an dem es
sichtbar wird.

#### AK-179
*Verlauf: A20 Z5145 · zuletzt geaendert durch T-086, 2026-09-07*

**AK-179** *(eine Schranke auf einen Waffentyp, den es nicht gibt, ist kein
Armaturenfall.)* Eine Zeile bekommt Fuellung (c) nur, wenn der von der
Schranke verlangte Wert der `wep_type` mindestens einer Waffe des
Datenabzugs ist. Trifft das nicht zu, faellt sie auf (b). Pruefweg: den
Wertevorrat `{w["wep_type"] for w in data["weapons"]}` bilden (in Umgebung
§0: **34** Werte ueber 1793 Waffen) und jede (c)-Zeile dagegen halten.
**Dieses Kriterium bewegt auf dem heutigen Spielstand null Zeilen** (0 von
426 bzw. 0 von 434) — es bewacht einen Fall, der im Abzug existiert und im
Bestand nicht: **72 von 144** `triggerOnWepType`-Effekten tragen 256 oder
512, was kein Waffentyp ist.
*Rot-vorher:* eine Umsetzung ohne diese Bedingung schreibt, sobald der
Spieler eine Kopie mit einem dieser 72 Effekte findet,
*"it depends on the armaments you carry"* an eine Schranke, die **keine
Waffe des Spiels** erfuellen kann — nachstellbar, indem man dem Test einen
Effekt mit `triggerOnWepType = 256` unterschiebt.

#### AK-180
*Verlauf: A20 Z5161 · zuletzt geaendert durch T-086, 2026-09-07*

**AK-180** *(Partition, Zahlen fortgeschrieben.)* **Ersetzt die Zahlenreihe
in AK-169; dessen Regel und Pruefweg bleiben unveraendert gueltig.** Die
sechs Fuellungen sind eine Partition der stummen Effektzeilen: jede stumme
Zeile traegt genau eine, und die Summe der sechs ist die Zahl der stummen
Zeilen. In Umgebung §0 ergibt das **150 / 0 / 144 / 38 / 94 / 0 = 426**
(A) und **159 / 0 / 149 / 25 / 101 / 0 = 434** (B), jeweils in der
Reihenfolge (a) / (a2) / (b) / (c) / (d) / (e).
*Rot-vorher:* die Zahlenreihe aus AK-169 (150 / 0 / 124 / 58 / 94 / 0)
summiert sich zwar ebenfalls auf 426, verteilt aber 20 Zeilen auf die
falsche Fuellung; die Summe allein ist deshalb **kein** ausreichender
Waechter.

#### AK-181
*Verlauf: A20 Z5202 · zuletzt geaendert durch T-086, 2026-09-07*

**AK-181** *(jede Zahl im Fliesstext nennt ihre Lesart.)* Wo `UI_SPEC.md`
eine Zahl ueber die stummen Effektzeilen nennt, steht dabei, ob sie die
**Liste** (`Build.situational`, `live == False`) oder eine **Fuellung**
(die Zeile im `Why`-Dialog) zaehlt. Die Messumgebung darf dabei auf den
§0-Abschnitt des eigenen Nachtrags verweisen; sie darf nicht fehlen.
Pruefweg: Volltextsuche nach `426` und `434` in dieser Datei, jede
Fundstelle einer der beiden Lesarten zuordenbar.
*Rot-vorher:* der Satz in §6 des T-080-Abschnitts vor diesem Nachtrag — wer
ihn neben der Tabelle des T-084-Abschnitts liest, haelt 170 und 124 fuer
zwei Messungen derselben Groesse und eine davon fuer falsch.

### 6.7 Schlechtester und bester Fall, und die Zahl ohne Waffe

#### AK-182
*Verlauf: A21 Z5755 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-182** *(eigenes Element, zwei Eintraege.)* Die Leiste traegt eine
zweite `QComboBox` zwischen Zielwahl und `Optimize` mit genau den
Eintraegen `Worst case` und `Best case`, in dieser Reihenfolge,
`Worst case` voreingestellt; die Zielwahl behaelt genau ihre zwei
Eintraege. Links von `Optimize` stehen hoechstens zwei Einstellungen.
Pruefweg: ausgelesene Eintraege beider Comboboxen. *Rot-vorher:* eine
Umsetzung mit vier Eintraegen in der Zielwahl
(`Maximise damage (worst case)` …) bricht die Zusage aus dem
`goals.py`-Docstring, dass ein drittes Ziel ein Registry-Eintrag ist — sie
braucht dann sechs.

#### AK-183
*Verlauf: A21 Z5765 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-183** *(kein neuer Zustand.)* Eine Aenderung der Lesart verwirft einen
lebenden Vorschlag und laesst die Statuszeile 4.1 sagen; ein laufender Lauf
wird abgebrochen und zeigt 4.7 — dasselbe Verhalten und derselbe Code-Pfad
wie bei einer Aenderung der Zielwahl. §4 bekommt **keine** neue Zeile.
*Rot-vorher:* eine Umsetzung, die bei Umschaltung selbsttaetig neu rechnet,
startet eine Suche, deren Kosten (S11) niemand gemessen hat, ohne dass der
Spieler `Optimize` gedrueckt haette (§5.1).

#### AK-184
*Verlauf: A21 Z5772 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-184** *(nie zwei Zahlen.)* Zu keinem Zeitpunkt zeigt die Oberflaeche
fuer dieselbe Kopie zwei Zahlen unter verschiedenen Lesarten. Die Lesart
reist in der Anfrage und erreicht den Anfrage-Schluessel, so dass ein
Ergebnis nie unter einer anderen Lesart beschriftet werden kann.
Pruefweg: zwei Anfragen, die sich nur in der Lesart unterscheiden, ergeben
verschiedene Schluessel (`run.py` fuehrt `declared` bereits mit).
*Rot-vorher:* ein Nebeneinander „worst / best" auf der Slotkarte ist die
Fehlerklasse D-11/QA-082, und die zweite Zahl haette keinen Erzeuger.

#### AK-185
*Verlauf: A21 Z5793 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-185** *(genau viermal, nie je Zeile.)* Die Lesart wird genannt: im
Bedienelement, im Kopf des Vorschlagsblocks, im `Why`-Dialog (Titel und
Kopf) und in der Zusammenfassungszeile des Pickers. In keiner Effekt-,
Fluch- oder Zaehlzeile und auf keiner Reliktkarte kommt sie vor.
Pruefweg: ausgelesener Text je Ort, Vorkommen von `worst case` /
`best case` zaehlen. *Rot-vorher:* eine Umsetzung, die jeder Zeile
`(worst case)` anhaengt, erzeugt auf der laengsten Slotgruppe 21
Wiederholungen — das Rauschen, gegen das AK-50 geschrieben ist.

#### AK-186
*Verlauf: A21 Z5801 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-186** *(Voreinstellung fuer Bedingungen, nie fuer Zahlen.)* Die Lesart
wirkt ausschliesslich ueber `GoalContext.declared`. Eine vom Spieler selbst
erklaerte Bedingung bleibt so, wie er sie erklaert hat; kein Gewicht,
keine Zahl und kein Feld ausser `declared` wird von der Lesart beruehrt.
Pruefweg: zwei Laeufe mit derselben Belegung, einer mit einer vom Spieler
erklaerten Bedingung — der erklaerte Wert steht in beiden Lesarten im
Ergebnis. *Rot-vorher:* eine Umsetzung, die `declared` je Lesart neu
aufbaut, wirft die Angabe „ich fuehre 3 Boegen" weg, und die Zahl des
Beraters widerspricht dem Statblatt daneben, ohne dass es jemand sagt.

#### AK-187
*Verlauf: A21 Z5810 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-187** *(die Lesarten teilen `not_counted`, sie erfinden nichts.)* Im
schlechtesten Fall enthaelt `not_counted` genau die heutigen Eintraege ohne
die konditionalen Flueche; im besten Fall genau die konditionalen Flueche.
In Umgebung §0 sind das **170** bzw. **27** gegen heute **197**, und
`170 + 27 = 197`. Pruefweg: Summe von `len(explain.not_counted(built))`
ueber die 309 Ein-Relikt-Probleme, je Lesart. *Rot-vorher:* eine Umsetzung,
die im schlechtesten Fall auch Buffbedingungen setzt (oder umgekehrt),
ergibt eine Summe, die diese Identitaet verletzt — sie ist der Waechter.

#### AK-188
*Verlauf: A21 Z5818 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-188** *(die Listen behalten ihre Saetze.)* 4.9a, 4.9b, die Ueberschrift
des 4.9b-Abschnitts und die Zaehlzeile aus T-078 §6 bleiben woertlich
unveraendert; unter beiden Lesarten aendern sich nur ihre Zahlen. In
Umgebung §0: `curses_without_a_figure` **67 → 42** im schlechtesten Fall,
`effects_without_a_figure` **426 → 323** im besten. AK-155 gilt in beiden
Lesarten. *Rot-vorher:* eine Umsetzung, die fuer den schlechtesten Fall
einen eigenen Satz schreibt („counted as if it were active"), gibt
derselben Sache einen zweiten Wortlaut und laesst 4.9b und die Zeile
auseinanderlaufen.

#### AK-189
*Verlauf: A21 Z5827 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-189** *(der schlechteste Fall ist laenger, und das wird gemessen.)*
**Schreibt AK-160 fort, ersetzt es nicht.** In Umgebung §0 waechst die
laengste Slotgruppe des `Why`-Dialogs von **14** auf **21** Zeilen und der
laengste Vorschlagsblock von **15** auf **22** Zeilen; die meisten
Fluchzeilen auf einer Kopie steigen von 5 auf 15. Nach dem Einbau wird
beides nach AK-161 **je Lesart getrennt** neu gemessen. *Rot-vorher:* eine
Slotkarte, die auf den 14 Zeilen aus AK-160 ausgelegt ist, schneidet im
schlechtesten Fall ab oder waechst ueber den Bildschirm — 4.14 verlangt
Umbruch, nicht Kuerzung.

#### AK-190
*Verlauf: A21 Z5839 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-190** *(der Satz wandert und wird umgeschrieben.)* Die beiden Saetze
aus §3.1 stehen in `MAX_DAMAGE.scope`; `_NO_ARMAMENT` und
`_NO_ARMAMENT_NOTE` erscheinen in keinem `GoalScore` mehr, und der alte
Wortlaut `No armament selected — ranked on attack multipliers only, without
weapon scaling.` kommt in der Oberflaeche nicht mehr vor. Bleibt der Zweig
mit Bezugswaffe erhalten, traegt **er** einen Laufbefund, der die Armatur
nennt. Pruefweg: Volltextsuche im ausgelesenen Text von Picker und
`Why`-Dialog. *Rot-vorher:* eine Umsetzung, die den Satz in `scope`
schreibt **und** als `unknowns` stehen laesst, zeigt ihn im `Why`-Dialog
zweimal untereinander — die Fehlerklasse aus AK-164.

#### AK-191
*Verlauf: A21 Z5849 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-191** *(die Rangfolge haengt an keiner gefuehrten Waffe.)* Zwei
Laeufe, die sich nur in der gefuehrten Armatur unterscheiden, ergeben
dieselbe Rangfolge und dieselben Zahlen — fuer beide Zielrichtungen.
Pruefweg: ueber den Bestand ranken, einmal mit Greatsword, einmal mit
Bogen. *Rot-vorher, gemessen:* wird nur die **Bezugswaffe** weggelassen und
`weapons_held` weiter gefuellt, aendern in Umgebung A **2 von 309** Kopien
ihre Zahl und die Rangfolge unterscheidet sich **ab Rang 0** —
`Deep Polished Drizzly Scene` (`Improved Greatsword Attack Power`, +0,09
mit Greatsword, 0,00 mit Bogen) und `Grand Luminous Scene`
(`Improved Bow Attack Power`, +0,06 mit Bogen, 0,00 mit Greatsword).

#### AK-192
*Verlauf: A21 Z5859 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-192** *(die Armaturenzeile nennt die Zahl, nicht den Hebel.)* Fuellung
(c) lautet
`{effect name}: it depends on the armaments you carry, which this figure
leaves out.` Die Zeichenfolge `armaments you carry, so no number here`
kommt nirgends mehr vor. Der Test von (c) bleibt AK-177 bis AK-179
unveraendert. In Umgebung §0 sind das **40** Zeilen (A) und **28** (B),
wenn nichts gefuehrt wird, und **23** (A) / **11** (B) im besten Fall.
*Rot-vorher:* der heutige Wortlaut raet unter A17 zu etwas, das die Zahl
nicht mehr bewegt — der Spieler legt die Waffe an und die Rangfolge bleibt,
wo sie war.

#### AK-193
*Verlauf: A21 Z5869 · zuletzt geaendert durch T-092, 2026-09-07*

**AK-193** *(die Spalte nennt die Groesse, die sie zeigt.)* Solange die
Zielrichtung ohne Armatur rankt, traegt die erste Zeile der Wertspalte im
Picker die Beschriftung `Attack multipliers` und der Wert keine Einheit;
das Wort kommt aus derselben Quelle wie `GoalScore.display`. *Rot-vorher:*
`Damage  +0.09` — eine Zahl ohne Groesse und ohne Einheit, also A12
gebrochen; `+12.4 AR` waere zusaetzlich falsch, weil kein Angriffswert mehr
gerechnet wird.

#### AK-194
*Verlauf: A21 Z5780 · zuletzt geaendert durch T-092, 2026-09-07*

*Ueberholt: **widerspruechlich** - schreibt die Messung `bei 1320 px Fensterbreite` vor, obwohl A14 Z2555 (T-071) die feste Startbreite 1320 px aufgehoben und durch eine abgeleitete Breite ersetzt hat*

**AK-194** *(die Breite wird gemessen, nicht geschaetzt.)* Nach dem Einbau
wird am **laufenden Fenster** gemessen, wie breit die Statuszeile bei
1320 px Fensterbreite noch ist, mit Messumgebung nach L-009 (Plattform,
Qt-Stil, Skalierung, physisch oder logisch). Sie muss mindestens **zwei
Drittel** ihrer heutigen 158 px behalten (**≥ 105 px**; Zielwert aus einer
einzigen gemessenen Zahl abgeleitet, selbst kein gemessener Wert). Wird er
unterschritten, heissen die Eintraege `Worst` und `Best`. *Rot-vorher:*
eine Umsetzung, die die Breite aus der Zeichenzahl in §1.4 herleitet, hat
keine Messung — 12,0 px je Zeichen liefert dieser Rechner offscreen fuer
**jede** Zeichenkette (T-084 §0).

> **Widerspruechlich — die Entscheidung steht beim App Designer aus.**
> Beide Fassungen stehen oben bzw. an den genannten Stellen nebeneinander;
> dieser Abschnitt loest den Vorrang **nicht** auf.

---

## Bereich 7 — Die sechs Inhalts-Tabs

`Effects & chances`, `Weapons & spells`, `Nightlords`, `Deep of Night`,
`Red variants`, `World Events` — welche Frage jeder Tab beantwortet und woran
ein Spieler das abliest. `ArsenalTab` ist der Tab `Weapons & spells`; die drei
Nachtraege aus T-052 zu Arsenal- und Waffenzeilen stehen deshalb in 7.3.

*Herkunft im Verlauf: A06 · A07 · A08 (alle T-052) · A10 (T-056) · A11 · A12 · A13 (Director)*

### 7.1 Was fuer alle sechs Tabs gilt

#### AK-68
*Verlauf: A10 Z1735 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-68** Jeder der sechs Tabs zeigt beim Erstoeffnen, **oberhalb jedes
Bedienelements und jeder Zahl**, eine `_heading()`-Ueberschrift und
unmittelbar darunter genau einen Fragesatz-Absatz in `#8a8a8a`/11 px mit
`setWordWrap(True)`. Die Wortlaute stehen in §2 bis §7 und sind wortgleich zu
uebernehmen. Ein Test, der den ersten sichtbaren Textknoten jedes der sechs
Tab-Widgets ausliest, findet dort die Ueberschrift — auf keinem Tab eine
Zahl, einen Filter oder eine Bestandszeile.

#### AK-69
*Verlauf: A10 Z1745 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-69** Auf keinem der sechs Tabs steht eine Zahl, deren Einheit **und**
deren Bezugsgroesse nicht entweder in ihrer eigenen Zeile oder in genau einem
Erklaersatz desselben Abschnitts benannt ist. Die zehn heute offenen Stellen
sind in §2 bis §7 einzeln mit ihrem verbindlichen Wortlaut aufgefuehrt; ein
Test, der die zehn Zeichenketten sucht, findet zu jeder den zugehoerigen
Erklaersatz auf demselben Tab.

#### AK-70
*Verlauf: A10 Z1752 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-70** Wo die Bezugsgroesse **auch im Code nicht bekannt** ist, sagt der
Bildschirm das, statt die Zahl kommentarlos zu zeigen oder sie wegzulassen
(GOAL A7, ausgedehnt auf die Anzeige). Der Wortlaut fuer diesen Fall ist je
Stelle unten festgelegt und enthaelt immer die Formel *„the files do not
say"*. Betroffen heute: `Reward multiplier` (§5), `Refills at` (§4),
`… buildup` (§3), `stamina recovery speed +5` (§7).

#### AK-71
*Verlauf: A10 Z1799 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-71** Kein Tab setzt eine Mindesthoehe ueber **860 logische px**
(`minimumSizeHint().height()`), gemessen an einer echten Widget-Instanz. Wo
der Inhalt hoeher ist, ist er in einer `QScrollArea` mit
`setWidgetResizable(True)`. Ein Test, der die sechs Tab-Widgets baut und ihre
`minimumSizeHint()` abfragt, findet **keinen** Wert ueber 860; der heutige
Ausreisser ist `Deep of Night` mit 949.

#### AK-72
*Verlauf: A10 Z1806 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-72** Kein Kachel- oder Kartenraster hat eine feste Spaltenzahl. Die
Spaltenzahl folgt aus der verfuegbaren Breite (`max(1, breite //
(kartenbreite + abstand))`), und es wird **nie eine Kachel teilweise
gezeichnet**. Ein Test, der `BossTab` bzw. `ArsenalTab` auf 1250, 1600 und
2100 logische px setzt, findet bei jeder Breite: alle Karten vollstaendig
sichtbar, `horizontalScrollBar().isVisible()` **False**, und im
`Nightlords`-Tab alle **zehn** Kartennamen im ausgelesenen Text.

#### AK-73
*Verlauf: A10 Z1814 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-73** Keine angezeigte Zeichenkette bricht mitten in einem Begriff um.
Verbindlich fuer die Wertzeilen der Waffenkachel: ein Wert aus mehreren
`·`-getrennten Gruppen bricht **nur zwischen zwei Gruppen** um, nie
innerhalb einer. Der heutige Bruch `STR -7 · ARC +45 · DEX` / `-7` ist damit
ausgeschlossen. Beleg des Ist-Zustands: `…/zoom-tile-wrap.png`.

> **Korrektur an meiner eigenen Vorgabe.** `DESIGN_REVIEW.md`, T-052,
> Abschnitt „Positiv / beibehalten", hat die Arsenal-Kachel als Vorbild
> gegen DR-009 gelobt („Bezeichnung und Wert in getrennten, gestapelten
> Zeilen"). Das galt fuer den damals geprueften Fall (`Spell power` / `145`,
> ein kurzer Wert). Fuer die langen Skalierungswerte trifft dasselbe
> Muster denselben Fehler wie DR-009 — nur eine Zeile tiefer. Das Lob bleibt
> fuer den Einzelfall richtig und **taugt nicht als allgemeine Regel**;
> AK-73 ersetzt es als Regel.

#### AK-74
*Verlauf: A10 Z1837 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-74** Jede Farbe, die auf einem der sechs Tabs eine **Bedeutung** traegt
(und nicht nur Typografie ist), wird auf demselben Tab genau einmal benannt —
in einem Satz oder einer Legendenzeile, nicht nur in einem Tooltip.
Betroffen: gruen im `Nightlords`-Tab (zwei Bedeutungen, siehe §4), blau/rot
im `Effects`-Tab, blau als „community-reported" im `Red variants`- und im
`World Events`-Tab (dort heute schon korrekt benannt — das ist das Vorbild).

#### AK-75
*Verlauf: A10 Z1852 + A12 Z2497 (Geltungsbereich) · zuletzt geaendert durch T-058, 2026-09-05*

*Ueberholt: Geltungsbereich auf die sechs Inhalts-Tabs begrenzt - A12 Z2497 (Director nach T-058)*

**AK-75** In keiner **angezeigten** Zeichenkette der sechs Tabs steht ` -- `.
Der Gedankenstrich ist `—` (U+2014), mit Leerzeichen davor und danach.
Docstrings und Kommentare sind ausgenommen. Ein Test, der den sichtbaren Text
aller sechs Tabs einsammelt, findet **0** Vorkommen von ` -- `.

**Dazu A12 Z2497 — Geltungsbereich:**

**AK-75 gilt nur fuer die sechs Inhalts-Tabs.** Vier angezeigte Literale mit
` -- ` bleiben ausserhalb (`datasource.py:173`, `model.py:889`,
`model.py:1058`, `weapons.py:221`). Sie liegen im `Build planner`, den der
Nutzer ausdruecklich ausgenommen hat ("der erste passt"). Als Schuld
vermerkt, nicht als Befund.

### 7.2 `Effects & chances`

#### AK-76
*Verlauf: A10 Z1868 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-76** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich, oberhalb der
Filterzeile. Die heutige Bestandszeile (`577 buffs (blue) then 75 curses
(red). …`) rutscht darunter und behaelt ihren Stil.

#### AK-77
*Verlauf: A10 Z1900 + A12 Z2487 (Untergrenze) · zuletzt geaendert durch T-058, 2026-09-05*

*Ueberholt: gilt nicht unterhalb von rund 1100 logischen px - A12 Z2487 (Director nach T-058)*

**AK-77** Im `Effects`-Tab ist `Effect` die breiteste Spalte der Tabelle, bei
jeder Fensterbreite. Verbindlich: `Effect` bekommt mindestens **320**
logische px und `What it does` mindestens **260**, bevor irgendeine andere
Spalte mehr als ihre Kopfzeilenbreite bekommt; die uebrigen Spalten sind
`ResizeToContents` mit einer Obergrenze, die kleiner ist als die Breite von
`Effect`. Ein Test, der die Tabelle auf 1516 logische px setzt, findet
`sectionSize(0) >= 320` und `sectionSize(0) > sectionSize(i)` fuer alle
i != 0. Ein Effektname von 40 Zeichen ist bei 1516 px vollstaendig lesbar.

**Dazu A12 Z2487 — Untergrenze:**

**AK-77 gilt nicht unterhalb von rund 1100 logischen px.** Dort gibt der
Code die beiden Untergrenzen auf, statt eine Spalte hinter den rechten Rand
zu schieben. Grund, und er ist zwingend: die Bildlaufleiste, die eine
abgeschobene Spalte wieder erreichbar machen wuerde, ist **genau die, die
hinter der Taskleiste liegt** (DR-015). Eine erzwungene Untergrenze braeuchte
bei 833 px eine 883 px breite Tabelle in einem 780-px-Sichtbereich — die
Vorgabe waere formal erfuellt und der Inhalt unerreichbar. **Bedingung:**
jede gekuerzte Zelle traegt ihren vollen Text als Tooltip. Diese Zusicherung
traegt den Kompromiss; ohne sie faellt er.

#### AK-78
*Verlauf: A10 Z1925 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-78** In der Effektetabelle steht **keine** Spalte mehr mit der
Ueberschrift `Pools`.

#### AK-79
*Verlauf: A10 Z1963 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-79** Die heutige ungewichtete Mittelung ueber Farb-/Modus-Eimer wird
nicht ausgeliefert. Auf dem Bildschirm steht zu den Chance-Zahlen **genau
eine** Definition, an **genau einer** Stelle, und sie nennt (a) die
Bezugsgroesse „per relic effect slot", (b) dass die aktuellen Filter darin
stecken, und (c) dass die Zahl **nicht** die Wahrscheinlichkeit pro Relikt
oder pro Lauf ist. Verbindlicher Wortlaut des einen Satzes:
`Chance is per relic effect slot, over every slot that can roll the effect
under the filters above — not per relic and not per run.`
Der heutige Tooltip-Satz *„averaged over every pool that can produce it"* und
der heutige Zusammenfassungs-Halbsatz *„how likely an effect is on one roll
of the selected colour and mode"* kommen im Baum nicht mehr vor. Ein Test,
der den sichtbaren Text des Tabs einsammelt, findet die Zeichenkette
`per relic effect slot` **genau einmal**.

#### AK-80
*Verlauf: A10 Z1977 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-80** Der angezeigte Mittelwert ist nach Vorkommen gewichtet, nicht ueber
Eimer gemittelt. Pruefbar an dem in QA-126 aufgeschluesselten Einzelfall:
`[Wylder] Improved Mind, Reduced Vigor` zeigt **0,91 %**, nicht 20,4 %.

#### AK-81
*Verlauf: A10 Z1989 + A11 Z2452 (Beispielzahlen) · zuletzt geaendert durch Director, 2026-09-05*

*Ueberholt: die Beispielzahlen `1 of 2`/`2 of 2` - A11 Z2452 (Director); verbindlich sind `1 of 3`/`3 of 3`*

**AK-81** `Tier` und `Copies` werden aus dem **ungefilterten** Effektbestand
gebildet; die Filter bestimmen nur, welche Zeilen sichtbar sind. Pruefbar:
`Continuous HP Recovery` traegt bei `All colours` `1 of 2` / `2 of 2` und
traegt dieselbe Leitersprosse auch bei Farbfilter `Red`, statt eine leere
Zelle zu zeigen.

**Dazu A11 Z2452 — Beispielzahlen:**

**AK-81 — die Beispielzahlen sind die falschen.** AK-81 verbietet, gefilterte
Werte als Beispiel zu nennen, und nennt dann selbst `1 of 2` / `2 of 2` —
genau die **gefilterten**. Ungefiltert lauten sie **`1 of 3` / `3 of 3`**.
Verbindlich sind die ungefilterten. Der Rest von AK-81 bleibt unveraendert.

### 7.3 `Weapons & spells` (ArsenalTab)

#### AK-64
*Verlauf: A06 Z1415 · zuletzt geaendert durch T-052, 2026-09-05*

**AK-64** Der Zusammenfassungssatz des Arsenal-Tabs (`arsenaltab.py:306-311`,
Fassung B des Uebergangs-Nachtrags zu AK-34) enthaelt zusaetzlich den Satz
*"Staves and seals show the spell scaling the game displays for them instead
of an attack rating."*, an der Stelle zwischen der Attack-Rating-Definition
und dem Zauber-Satz, wortgleich. Ein Aufbau, bei dem der sichtbare
Kachelraster nur Katalysatoren zeigt (z. B. Suche nach einem Stab- oder
Siegel-Namen), zeigt diesen Satz **immer** — er ist nicht an die aktuelle
Trefferliste gebunden, weil die Zusammenfassungszeile heute ohnehin fuer das
ganze Arsenal gilt, nicht nur fuer den gefilterten Ausschnitt.

#### AK-65
*Verlauf: A07 Z1482 · zuletzt geaendert durch T-052, 2026-09-05*

**AK-65** Die Anzeigeschwellen `>= 0.5` (Sichtbarkeit der Zeile
`From attributes` und der Aenderungszelle) und `> 0.05` (Farbe GOOD/MUTED der
Aenderungszelle) in `nrplanner/app.py` bleiben **absolute, an der
Bildschirmeinheit gemessene Konstanten** und werden **nicht** mit einem
Kalibrierungsfaktor multipliziert, auch nicht bei einer kuenftigen
Neukalibrierung. Ein Test, der die 0,6-Konstante veraendert (z. B. auf 0,5
oder 0,7), darf die Zahl der betroffenen Faelle bewegen, aber keine der
beiden Schwellenkonstanten selbst.

#### AK-66
*Verlauf: A08 Z1522 · zuletzt geaendert durch T-052, 2026-09-05*

**AK-66** Eine Waffenzeile, die zur Katalysator-Familie gehoert (Glintstone
Staff / Sacred Seal, `model.weapon_class(weapon) == "catalyst"`) und
gleichzeitig `equippedSpell_R1 == -1 and equippedSpell_R2 == -1` traegt
(keinen Zauberplatz), erscheint **nirgends** in einer spielerseitigen
Waffenliste — nicht im Arsenal-Tab, nicht im `WeaponDialog`-Auswahldialog,
nicht in einer kuenftigen Berater-Kandidatenliste. Der Filter greift **nur**
innerhalb der Katalysator-Familie (T-046 §7: ausserhalb ist „kein Zauberplatz"
der Normalfall fuer ein Schwert und sagt nichts). Damit sinkt die Zahl der
sichtbar gefuehrten Katalysatoren um genau die eine betroffene Zeile
(33770000); alle anderen Namen (`Finger Seal`, `Scholar's Thrusting Sword`)
sind von diesem Kriterium nicht betroffen (T-046 §7: beide Kollisionen dort
sind zahlengleich bzw. kosmetisch, kein Betrugsfall).

#### AK-82
*Verlauf: A13 Z2518 (Wortlaut) · zuletzt geaendert durch T-068, 2026-09-06*

*Ueberholt: Wortlaut zweimal ersetzt - A11 Z2457 (Director, AK-68 gewinnt) und A13 Z2518 (Director nach T-068)*

Hier zeigt das Register auf einen **ganzen Abschnitt**, nicht auf einen
Absatz. Der geltende Wortlaut steht deshalb nicht hier, sondern in
`docs/archiv/ui-spec-verlauf.md`:

> **A13** — Nachtrag des Directors zu AK-82 — 2026-09-06 (nach T-068) (T-068, 2026-09-06)  
> Verlauf Zeile **2587 bis 2623** (Altstand Z2518 bis Z2554)

#### AK-83
*Verlauf: A10 Z2024 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-83** Beim ersten Oeffnen des Tabs ist mindestens ein Abschnitt
aufgeklappt und mindestens eine Waffenkachel sichtbar, ohne dass der Nutzer
etwas anklickt oder tippt. Ein Test, der `ArsenalTab` baut und die sichtbaren
`Tile`-Widgets zaehlt, findet **> 0**.

#### AK-84
*Verlauf: A10 Z2031 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-84** *(setzt AK-72 und AK-73 fuer diesen Tab um)* Bei 1250, 1600 und
2100 logischen px ist jede gezeichnete Kachel vollstaendig sichtbar,
einschliesslich ihrer rechtsbuendigen Werte; kein `AR`, `Physical` oder
`Magic` steht ohne seine Zahl.

#### AK-85
*Verlauf: A10 Z2036 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-85** Die Skalierungszeile nennt ihre Skala. Der Tab traegt dazu genau
einen Satz, im Zusammenfassungsblock, wortgleich:
`Scaling is the game's own per-stat figure behind the letter grade it shows
in menus. Compare these figures with each other; the files do not say which
letter a figure earns.`
Ein Test findet diesen Satz genau einmal, und er steht auf dem Tab, auf dem
`Scaling ` auf 1 792 Kacheln erscheint.

#### AK-86
*Verlauf: A10 Z2044 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-86** Die Aufbau-Zeilen (`Blood Loss buildup`, `Poison buildup`,
`Frost buildup`, …) tragen ihren Geltungsbereich. Wo der Extraktor die
Bezugsgroesse kennt, steht sie in der Zeile; wo er sie nicht kennt, steht im
selben Zusammenfassungsblock wortgleich:
`Buildup figures come straight from the game's weapon data. The files do not
say what they are counted against, so use them to compare armaments, not as a
number of hits.`
AK-70 verlangt genau diesen Fall; welche der beiden Fassungen greift,
entscheidet der Kenntnisstand des Extraktors, nicht der Geschmack.

#### AK-87
*Verlauf: A10 Z2054 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-87** Die Zauberkachel benennt ihre Kosten als Kosten: `FP` heisst
`FP cost`, `Stamina` heisst `Stamina cost`. Die Zeile `Slots` entfaellt (§8)
oder heisst `Spell slots` — sie zeigt heute auf 160 von 160 Zauberkacheln `1`.

#### AK-88
*Verlauf: A10 Z2058 + A11 Z2465 (Geltungsbereich) · zuletzt geaendert durch Director, 2026-09-05*

*Ueberholt: Geltungsbereich auf angezeigten Text begrenzt - A11 Z2465 (Director)*

**AK-88** *(QA-139)* Dieselbe Groesse heisst auf demselben Bildschirm einmal.
Auf der Kachel steht `Spell power`; der Zusammenfassungssatz aus AK-64 sagt
heute *„the spell scaling the game displays for them"*. **Entscheidung:
`spell power` gewinnt**, weil dieser Ausdruck auf bis zu 1 792 Kacheln stehen
kann und der Satz nur einmal. Der Satz aus AK-64 lautet ab jetzt wortgleich:
`Staves and seals show the spell power the game displays for them instead of
an attack rating.` Die Zeichenkette `spell scaling` kommt im Baum nicht mehr
vor. **Betroffenes Akzeptanzkriterium: AK-64** — nur dieses eine Wort
geaendert, Stellung und Rest des Satzes unveraendert.

**Dazu A11 Z2465 — Geltungsbereich:**

**AK-88 — gilt fuer angezeigten Text, nicht fuer den Baum.** Woertlich
genommen truege AK-88 eine Umbenennung an 31 Stellen in Kommentaren und
Feldprosa quer durch Extraktor und Fassade, **ohne dass ein Nutzer etwas
davon saehe**. Der Geltungsbereich ist ab jetzt: **jede Zeichenkette, die auf
dem Bildschirm erscheint** — Beschriftungen, Tooltips, Kopfzeilen,
Aufklapp-Texte. Kommentare und interne Feldnamen sind ausdruecklich nicht
gemeint.

Davon **nicht** gedeckt und weiterhin offen: `nrplanner/advisor/goals.py:108`
zeigt `spell scaling` in einem `Goal.scope`-Satz — das **ist** angezeigter
Text und faellt damit unter AK-88. Geht in den naechsten Auftrag.

### 7.4 `Nightlords`

#### AK-89
*Verlauf: A10 Z2080 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-89** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich. Die heutige
Zeile (`10 Nightlords · 8 also have an Everdark Sovereign … click a card for
damage taken, status buildup and more`) rutscht darunter und verliert ihren
Klick-Hinweis, weil er jetzt im Fragesatz steht.

#### AK-90
*Verlauf: A10 Z2087 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-90** *(setzt AK-72 fuer diesen Tab um, eigener Befund)* Bei 1250, 1600
und 2100 logischen px sind **alle zehn** Nightlord-Karten vollstaendig
sichtbar und ihre Blurb-Texte vollstaendig lesbar. Ein Test, der den
sichtbaren Text des Kartenbereichs bei 1600 px einsammelt, findet die Namen
`Maris` und `Harmonia`. Beleg des Ist-Zustands: `…/tab3-nightlords.png`
(acht) gegen `…/tab3-nightlords-wide2100.png` (zehn).

#### AK-91
*Verlauf: A10 Z2096 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-91** *(QA-128 Punkte 4 bis 6, AK-74)* Das Detailpanel traegt drei
Erklaerzeilen, je einmal je Abschnitt, wortgleich:

#### AK-92
*Verlauf: A10 Z2107 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-92** *(QA-130)* Kein Sentinel wird als Zahl gedruckt. `Refills at x-1`
kommt nicht vor: bei `stance.recovery <= 0` entfaellt die Zeile, oder sie
lautet `Refills at — not in the game's files` (A7). Pruefbar an Maris, dem
einzigen der zehn mit `recovery = -1.0`.

#### AK-93
*Verlauf: A10 Z2112 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-93** *(QA-131)* Der Abschnitt `WEAKNESS SPECIAL INTERACTION` erscheint,
sobald der Nightlord **irgendeine** Schwaeche traegt — Schadensart **oder**
Status. Pruefbar an Adel: sein Panel zeigt den Abschnitt und die dafuer
hinterlegte Notiz (*„Phase 1 only — the poison stagger is gone in phase 2 and
in the Everdark version."*), statt direkt mit `DAMAGE TAKEN` zu beginnen.

#### AK-94
*Verlauf: A10 Z2118 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-94** *(QA-129, Herkunft)* Zeilen, die auf einer Sichtung beruhen und
nicht in den Spieldateien stehen, tragen `OBSERVED_COLOUR` (`#7fae72`) —
dieselbe Farbe, die der Tab fuer `WEAKNESS_NOTE` bereits benutzt. Betroffen
sind heute `Debuff x2.0 damage taken`, `Debuff x0.8 attack power` und
`Stacks: yes — repeats compound`. Ein Test, der die Textfarbe dieser drei
Zeilen liest, findet `#7fae72` und nicht die Farbe der extrahierten Werte.
*(Ob die Zahlen selbst richtig sind und ob `ladder.down` zusaetzlich gezeigt
wird, ist der Rechenteil von QA-129 und gehoert dem `developer` — diese
Vorgabe regelt nur, dass man einer Zahl ansieht, woher sie kommt.)*

### 7.5 `Deep of Night`

#### AK-95
*Verlauf: A10 Z2142 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-95** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich; die vier
bestehenden Ueberschriften (`WHAT EACH DEPTH IS WORTH`, `HOW MUCH TOUGHER
ENEMIES GET`, `WHAT MOVES YOUR RATING`, `WHAT ELSE CHANGES WITH DEPTH`)
bleiben unveraendert darunter. Der zweite Satz des Fragesatzes ist zugleich
die Bezugsgroesse fuer die Skalierungstabelle (QA-128 Punkt 9) und wird nicht
zusaetzlich unter der Tabelle wiederholt.

#### AK-96
*Verlauf: A10 Z2149 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-96** *(QA-128 Punkte 7 und 8, AK-70)* Die beiden Zeilen des obersten
Blocks nennen ihren Bezug bzw. sagen, dass er nicht bekannt ist. Verbindlich,
als Note unter der ersten Tabelle:

#### AK-97
*Verlauf: A10 Z2165 + A12 Z2493 · zuletzt geaendert durch T-058, 2026-09-05*

**AK-97** *(eigener Befund, setzt AK-71 fuer diesen Tab um)* Der Inhalt des
Tabs liegt in einer `QScrollArea`; die vier Tabellen setzen keine feste
Hoehe mehr, die das ganze Fenster bindet. Ein Test findet
`DeepTab().minimumSizeHint().height() <= 860` und erreicht die letzte
Erklaerzeile (`Read from the game's own depth table.`) bei einer
Fensterhoehe von 900 logischen px durch Scrollen.

**Dazu A12 Z2493 — ergaenzt:**

**AK-97, erster Halbsatz: die vier Tabellen behalten ihre feste Hoehe.** Ohne
sie bekaeme jede eine eigene Bildlaufleiste — vier Leisten auf einem Tab sind
schlechter als eine.

### 7.6 `Red variants`

#### AK-98
*Verlauf: A10 Z2202 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-98** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich. Der heutige
Intro-Absatz verliert seinen ersten Nebensatz (er steht jetzt im Fragesatz)
und behaelt den Rest; die `COMMUNITY-REPORTED`-Zeile bleibt unveraendert und
steht direkt darunter, weil sie den zweiten Teil derselben Antwort traegt.
Der Satz `The figures are how many red variants of each sort a run puts on
the selected map.` bleibt an der Tabelle — er ist heute die vorbildlichste
Bezugsgroessen-Zeile der sechs Tabs und wird nicht angefasst.

#### AK-99
*Verlauf: A10 Z2217 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-99** Die Spalte behauptet keinen Kartenbezug, den die Daten nicht
tragen. Zwei zulaessige Ausgaenge, beide pruefbar:

#### AK-100
*Verlauf: A10 Z2238 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-100** Die Tabelle sagt das, statt es fuenfmal zu wiederholen. Die
Spaltenkoepfe lauten `Depth 1`, `Depth 2–3`, `Depth 4–5`, solange die Daten
das hergeben; weichen sie fuer irgendeine Karte ab, faellt die Tabelle
automatisch auf fuenf Einzelspalten zurueck. Ein Test, der eine Zeile mit
fuenf verschiedenen Werten einspeist, findet danach fuenf Spaltenkoepfe.

### 7.7 `World Events`

#### AK-101
*Verlauf: A10 Z2258 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-101** *(QA-134)* Der Tagesatz unterscheidet zwischen den Ereignissen,
statt auf 11 von 11 wortgleich zu stehen. Er nennt die Verteilung, die im
Datensatz liegt und heute verworfen wird — Beispiel `Judgment`: 19 Day-1-
gegen 1 Day-2-Muster. Verbindliches Muster:
`Can fire on Day 1 or Day 2 — {d1} of the {n} map patterns that carry it are
Day 1.` Ein Test findet fuer `Judgment` und `Fire-Summoning Beasts`
**verschiedene** Zeichenketten an dieser Stelle.

#### AK-102
*Verlauf: A10 Z2266 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-102** *(QA-134, A12)* Die Prozentzahl nennt ihren Geltungsbereich und
sagt, was sie **nicht** ist. Der Satz lautet wortgleich:
`The percentage is how much of that Nightlord's map pool carries the event.
The pool is drawn with weights, so it is not the chance of seeing it on a
given run.` Die Allaussage `Every other Nightlord: never.` bleibt, bekommt
aber ihren Beleg: `Every other Nightlord: never — across every map pattern
in the game's data.`

#### AK-103
*Verlauf: A10 Z2274 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-103** *(QA-133)* Eine Dauer steht nur an einer Zeile, die einen
**Zustand** beschreibt. Eine Zeile, die einen Betrag gewaehrt, traegt keine.
Pruefbar an drei Stellen: `10,000 runes` (ohne `for 1s`),
`restores 100 stamina` (ohne `for 0.3s`), `invulnerable for 5s` (mit, weil
das ein Zustand ist). Eine Dauer von `0.0` ist keine Angabe und wird nicht
als `for 0s` gedruckt.

#### AK-104
*Verlauf: A10 Z2281 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-104** *(QA-135)* Herleitungs- und Quellensprache steht nicht im
Fliesstext. Die Regel des Modulkopfs von `eventstab.py` (*„Everything about
how any of it was derived stays in the project's documents — none of it
belongs on screen."*) **bleibt in Kraft** — das ist meine Antwort auf die
offene Frage 4 aus T-055. Konkret: die Zeichenketten `fextralife`, `game8`,
`Eldenpedia`, `thefifthmatt`, `pattern modifier` und
`the row this project had wrong` kommen in keinem angezeigten Text vor. Was
bleibt, ist die Aussage, die den Spieler angeht — `Sources disagree: {was}` —
und, falls der App Designer die Quellen sehen will, das strukturierte Feld
`sources` als eigene, ruhige Zeile unter dem Absatz, nicht im Absatz. Der
heute geladene und nie gezeigte `rune_scaling`-Text beziffert die einzige
unbezifferte Behauptung des Tabs (*„rises the more expeditions you have
cleared"*) und erscheint an genau dieser Zeile — auch das ist **keine neue
Funktion**, sondern ein geladenes Feld.

#### AK-105
*Verlauf: A10 Z2296 · zuletzt geaendert durch T-056, 2026-09-05*

**AK-105** *(QA-136)* `Scale-Bearing Merchant` steht einmal in der Liste,
oder die beiden Eintraege verweisen sichtbar aufeinander. Ein Test, der die
Listeneintraege zaehlt, findet den Namen **einmal** — oder findet im Text des
einen Eintrags einen Verweis auf den anderen.

---

