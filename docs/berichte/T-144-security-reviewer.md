# T-144 - security-reviewer: aendert der Auswahldialog aus A15 die Vertrauenslage?

*Abgelegt vom Director. Der `security-reviewer` hat kein `Write`; dies ist sein
Bericht im Wortlaut.*

STATUS: erledigt
AUFTRAG: T-144 — OF-31: A15 verschiebt eine Vertrauensgrenze
GELESEN: `~/.claude/agents/_rahmen.md` · `CLAUDE.md` · `docs/tasks/T-144.md` ·
`docs/berichte/T-143-architect.md` · `ARCHITECTURE.md` Nachtrag XI (5370-5680,
AD-030/AD-031, V1-V5) · `UI_SPEC.md` §0-§11 zu A15 (2596-3160, AK-106 bis
AK-132) · `security/findings.md` (vollstaendig, SEC-001 bis SEC-025) ·
`docs/plan-restarbeiten.md` P6 (93-113) · `nrdata/oodle.py` ·
`nrdata/gamefiles.py` · `nrdata/dcx.py` · `nrdata/tpf.py` · `nrdata/extract.py`
(160-210, 1554, 2805) · `nrdata/icons.py` (70-110) · `nrdata/regulation.py` ·
`nrplanner/firstrun.py` · `nrplanner/paths.py` · `nrplanner/datasource.py`
(85-175) · `git show ebc5708:nrdata/savefile.py` und `:nrplanner/inventory.py`
(weil beide im Arbeitsbaum durch den parallelen `developer` veraendert sind)
GEAENDERT: keine. Kein Commit, kein Stage, keine Datei im Scratchpad angelegt,
kein Prozess und kein Port hinterlassen. Das Programm wurde nicht gestartet;
einziger Codeaufruf war `gamefiles.find_game_dir()` plus `stat()` auf drei
Dateien der Spielinstallation — beides rein lesend, kein QSettings, keine
Schreibziele beruehrt, deshalb war die Drei-Variablen-Umlenkung nicht
ausgeloest.
ANNAHMEN: (1) SEC-030 (Reparse-Punkte in `search_from`) ist als Hypothese
gekennzeichnet — `search_from` existiert noch nicht, ich habe keine Junction
gebaut und nichts gemessen. (2) Die Zahl 1 974 720 Byte fuer `regulation.bin`
stammt aus **einer** Installation (dieser Rechner, 08.09.2026) und ist eine
Stichprobe von 1, kein Wertebereich.
NAECHSTER: director — er entscheidet die zwei Wortlautfragen aus
SEC-027/SEC-028, bevor V2 startet, und legt die Vorlage zu
SEC-006/SEC-016/017/018 dem Nutzer vor.
BLOCKIERT DURCH: nichts.

---

**Gemessen gegen `ebc5708`** (Auftragsstand, `git log -1` bestaetigt). Statisch,
plus zwei folgenlose lokale Lesevorgaenge.

## Kurzantwort auf die vier Fragen

1. **Die Herleitung trifft zu**, Datei und Zeile bestaetigt — aber der
   `architect` hat den **falschen gestrichenen Befund** benannt. Nicht
   SEC-016/017/018 tragen die Bedingung, die A15 wegnimmt, sondern **SEC-006**.
2. **Das Risiko aendert sich an genau einer Stelle:** der Weg zu "fremder Code
   laeuft in diesem Prozess" fuehrte bisher ueber Schreibrechte im
   Spielordner, kuenftig ueber einen Klick im Ordnerdialog.
3. **Verhaeltnismaessig sind drei Zeilen Text und zwei Zahlen** — kein
   Signaturpruefer, kein zusaetzlicher Klick im geglueckten Fall.
4. **Die Streichbegruendung traegt woertlich nicht mehr, im Schluss aber
   weiter** — a fortiori, und genau solange SEC-026 offen bleibt. Das ist die
   Vorlage an den Nutzer, keine Wiedereroeffnung.

**V2 muss nicht auf einen Fix warten.** Es muss aber auf **eine Entscheidung**
warten, die Minuten kostet: den Wortlaut aus SEC-027.

---

## 1. Die Herleitung, nachgeprueft

| Aussage des `architect` | Nachpruefung |
|---|---|
| "aus dem gewaehlten Ordner wird eine native DLL geladen, `ctypes.CDLL`, `oodle.py:34-46`" | **haelt.** `nrdata/oodle.py:44` `_handle = ctypes.CDLL(str(candidate))`, `candidate = game_dir / name` (`:42`). |
| "AK-112 nimmt den Ordner gerade an, *weil* sie darin liegt" | **haelt.** `UI_SPEC.md:3059-3062`: "… und eine DLL aus `oodle._DLL_NAMES` vorliegt. Faellt eine der drei aus, erscheint Text E1." |
| "bisher konnte `find_game_dir()` nur Pfade aus der Steam-Bibliothekliste liefern" | **haelt.** `gamefiles.py:48-66`, Kandidaten ausschliesslich aus `libraryfolders.vdf` plus sechs feste `<Laufwerk>:/SteamLibrary/…`-Muster. |

**Drei Aufrufer laden**, nicht einer: `extract.py:181`, `icons.py:82`,
`bossdata.py:320` — jeweils `oodle.load(game_dir)` **unbedingt** als erste
Zeile der Extraktion, nicht erst beim ersten KRAK-Mitglied.

**Was der Bericht nicht sagt und die Lage schaerfer macht:** Die Ladung
passiert **nicht** einmalig bei der Wahl. Sie passiert bei jedem
Datenneuaufbau — `firstrun.ensure_data` beim Erststart, **und**
`datasource._load_data → extract.build(game, defs)` (`datasource.py:141-147`)
an jedem spaeteren Start, an dem `_regulation_matches` `False` sagt, also nach
jedem Spielpatch und nach jedem `EXTRACT_VERSION`-Sprung. Der Nutzer waehlt
einmal; der Code aus diesem Ordner laeuft Monate spaeter erneut, ohne Fenster
und ohne Klick.

---

## 2. Die Befunde

### [Mittel | Mittel — Wirkung Kritisch | Niedrig] SEC-026 — A15 entzieht der **Annahme von SEC-006** ihre Begruendung

**Betroffen:** `nrdata/oodle.py:34-46` (`load`, `ctypes.CDLL` in `:44`) ·
Annahmebedingung `UI_SPEC.md:3059-3062` (AK-112) · Aufloesung
`ARCHITECTURE.md:5555-5578` (AD-030, Punkt 4) · Ladepunkte
`nrdata/extract.py:181`, `nrdata/icons.py:82`, `nrdata/bossdata.py:320`

**Vertrauensgrenze:** *Herkunft des Spielordners.* Bisher: eine Menge von rund
vierzehn Pfaden, die Steam geschrieben hat. Kuenftig: jeder Ordner, den ein
Mensch benennt.

**Angriffspfad:** Ein Angreifer legt einen Ordner mit **drei** Dateien an —
eine nichtleere `regulation.bin`, eine `data0.bhd`, eine praeparierte
`oo2core_9_win64.dll` — und bringt den Nutzer dazu, ihn zu waehlen ("Datenpaket
fuer Nutzer ohne Steam-Installation", ein Issue-Thread im **oeffentlichen**
Repo, ein Modpack). AK-112 nimmt den Ordner an; AK-113 fragt nur zurueck, wenn
der Ordnername kein `NIGHTREIGN` traegt, lehnt aber **nicht** ab
(`UI_SPEC.md:3064-3067`) — und der Angreifer benennt den Ordner richtig.
`extract.write_snapshot` ruft `oodle.load`, `LoadLibrary` fuehrt `DllMain` aus.

**Auswirkung:** Codeausfuehrung im Nutzerkontext, ohne Adminrechte, ausgeloest
zu einem Zeitpunkt, den der Nutzer nicht kontrolliert (naechster Spielpatch).
**Verstaerker, gemessen an der installierten Python-Fassung:**
`ctypes.CDLL.__init__` setzt bei einem Pfad mit `\` zusaetzlich
`nt._LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR` (Python 3.12.10, `inspect.getsource`
ausgefuehrt) — die **Abhaengigkeiten** der gewaehlten DLL werden ebenfalls aus
dem gewaehlten Ordner aufgeloest.

**Warum das ein neuer Befund ist und nicht SEC-006:** SEC-006 ist am 02.09.2026
mit dieser Begruendung angenommen worden (`security/findings.md:100-102`,
woertlich): *"Eine Herkunftspruefung der DLL ist nicht vorgesehen — **wer dort
schreiben kann, hat den Nutzerkontext ohnehin**. Akzeptiertes Restrisiko."*
**Genau dieser Satz faellt mit A15.** Nach A15 braucht der Angreifer keine
Schreibrechte im Spielordner mehr; er braucht eine Ordnerwahl. Der `architect`
hat SEC-016/017/018 als die Befunde benannt, deren Bedingung sich verschiebt —
die schaerfere Fundstelle liegt einen Schritt weiter auf derselben Achse: es
ist **SEC-006**, der die DLL-Ladung besitzt, und seine Annahmebegruendung ist
die einzige im Register, die A15 woertlich widerlegt.

**Warum Schwere Mittel und nicht Kritisch — offen begruendet, damit der
`director` widersprechen kann:** die **Wirkung** ist Codeausfuehrung, also
Kritisch. Der **Defekt** ist es nicht: der Mechanismus ist unvermeidbar (ohne
die Oodle-DLL des Spiels sind die Archive nicht lesbar), er ist bekannt,
dokumentiert und vom Nutzer angenommen. Was heute fehlt, ist die
Tiefenverteidigung und die **Aktualitaet der Annahme** — die Skala fuehrt das
unter Mittel. Wer die Wirkung fuer massgeblich haelt, kommt auf Kritisch und
damit auf FAIL; das ist eine Entscheidung des `director`, und ich lege sie
offen statt sie durch die Einstufung zu treffen.

**Behebungsrichtung:** **keine Herkunftspruefung der DLL** — siehe die Auflage
unten, sie wuerde SEC-016/017/018 wieder scharf machen. Was bleibt: die
Entscheidung des Nutzers informiert machen (SEC-027) und den Ordner, aus dem
geladen wird, vor dem Bau sichtbar (Beobachtung B1).

**Nachweis:** `oodle.py:44` · `UI_SPEC.md:3059-3062` · `extract.py:181` ·
`datasource.py:141-147` · `security/findings.md:100-102` · Suche ueber
`nrdata/`, `nrplanner/`, `scripts/`, `tests/` nach
`CDLL|WinDLL|LoadLibrary|ctypes.util|PyDLL`: **2 Treffer, beide in `oodle.py`**
(Zeile 14 Typannotation, Zeile 44 der Aufruf). Zweite, unabhaengig formulierte
Maske `authenticode|winverifytrust|signtool|signature|publisher|trusted|verify`
ueber `nrdata/` und `nrplanner/`: **14 Treffer, kein einziger eine Pruefung
einer geladenen Bibliothek** (Kommentare zu Waffen, Speicher, Pruefsummen).
**Es gibt keine Herkunftspruefung — Nenner genannt.**

---

### [Hoch | Mittel | Mittel] SEC-027 — Der Panel-Text verspricht das Gegenteil dessen, was der Code tut

**Betroffen:** `UI_SPEC.md:2870` (Text A1), Zeile woertlich:
`Nothing in that folder is changed, moved or deleted. It is only read.` —
zu bauen in **V2**, `nrplanner/firstrun.py`.

**Vertrauensgrenze:** die Entscheidung des Nutzers selbst. Sie ist die einzige
Schranke, die A15 zwischen einen fremden Ordner und `DllMain` stellt.

**Angriffspfad:** Der Nutzer liest den Satz, schliesst "das ist ein
Lesevorgang, das kann nichts anrichten", und waehlt einen heruntergeladenen
Ordner, den er per Doppelklick nie gestartet haette. Die einzige
Sicherheitsfunktion des Ablaufs ist eine informierte Zustimmung — und der Text
macht sie uninformiert. Danach: SEC-026.

**Auswirkung:** Der Angreifer gewinnt keine Rechte, die der Nutzer nicht selbst
haette geben koennen. Er gewinnt, **dass der Nutzer nicht weiss, dass er sie
gegeben hat.** Genau das ist bei einem Einzelplatzwerkzeug die ganze Substanz
des Befunds.

**Warum Prioritaet ueber Schwere:** der Text wird in **V2** geschrieben.
Danach steht er in der Oberflaeche und beruehrt A8, AK-127 und AK-128 — jede
spaetere Korrektur ist eine Textaenderung mit drei Nachpruefungen statt einer
Zeile im Auftrag. Und es ist die billigste Vorkehrung im ganzen Bericht.

**Behebungsrichtung:** einen Satz in A1 (und sinngemaess in W1), in
Spielersprache, ohne verbotene Woerter aus `UI_SPEC.md:2982-2986`. Sinn, nicht
Wortlaut — der gehoert dem `ui-ux-designer`: *dass das Programm ein Stueck
Software aus diesem Ordner benutzt, um die Daten des Spiels zu oeffnen, und man
deshalb nur auf einen Ordner zeigen soll, dem man auch das Spiel selbst
zutraut.* Der Satz "Nothing in that folder is changed, moved or deleted"
**bleibt richtig** und darf stehen; falsch ist allein "It is only read".

**Nachweis / Praezedenzfall im Haus:** `security/findings.md:268-270`,
Nutzerentscheid 02.09.2026 zu "kein Netzwerkzugriff": *"Eine Zusage, die der
Code nicht haelt, wird nicht dadurch richtig, dass der Ausloeser
unwahrscheinlich ist."* Dieselbe Regel, derselbe Ablauf, dieselbe Loesung.

---

### [Mittel | Niedrig | Mittel] SEC-028 — AK-112 nimmt `regulation.bin` ohne Obergrenze an, und liest sie danach bei **jedem** Start ganz

**Betroffen:** Annahmebedingung `UI_SPEC.md:3059-3060` ("lesbar und nicht
leer") · `nrplanner/firstrun.py:31` `hashlib.sha256(path.read_bytes())` ·
`nrplanner/datasource.py:106` dieselbe Zeile · `nrdata/regulation.py:16`
`raw = pathlib.Path(path).read_bytes()`

**Vertrauensgrenze:** gewaehlter Ordner → Speicher des Prozesses.

**Angriffspfad:** Der gewaehlte Ordner traegt eine `regulation.bin` von
mehreren Gigabyte. Die Annahmepruefung fragt nur "lesbar und nicht leer" und
nimmt an. `firstrun.what_is_needed` hasht die Datei danach bei **jedem** Start
vollstaendig (`:62`, innerhalb des `try`, also still). Der Nutzer hat keinen
Weg zurueck ausser dem Fehlerfall, der ihn erneut fragt.

**Auswirkung:** Verfuegbarkeit — Speicherdruck und Startverzoegerung bei jedem
Start, still. Kein Datenabfluss.
Nebenwirkung: `datasource.py:104` prueft `st_size` **vor** dem Hashen und
kuerzt den Weg dort ab, `firstrun.py:31` und `regulation.py:16` tun das nicht.

**Behebungsrichtung:** eine Obergrenze **in dieselbe Funktion**, die AK-112
prueft (`looks_like_the_game`, V1) — nicht drei Deckel an drei Lesestellen. Die
Schranke traegt ihr Rezept: gemessen auf dieser Installation **1 974 720 Byte**
(08.09.2026, `stat().st_size`, Stichprobe 1); der Docstring in
`firstrun.py:48-49` nennt unabhaengig davon "Hashing 2 MB". Eine Grenze von
64 MiB laesst Faktor **34** Luft — grosszuegiger als der bereits akzeptierte
`MAX_UNCOMPRESSED_SIZE` (2 GiB gegen 937 MiB gemessen, Faktor 2,2) — und weist
eine 20-GiB-Datei mit Text E1 ab, also **laut**, in der Form, die der Nutzer bei
SEC-006 angenommen hat.

**Nachweis:** Fundstellen ueber zwei Masken: `regulation.bin` in `nrdata/` und
`nrplanner/` → 20 Treffer, davon **4 Lesevorgaenge** (`extract.py:2805`,
`datasource.py:106`, `firstrun.py:31`, `regulation.py:16`); Maske
`st_size|MAX_[A-Z_]*SIZE|too (large|big)` → 9 Treffer, **kein einziger** auf
`regulation.bin` vor dem Lesen (`datasource.py:104` vergleicht gegen den
Abzugswert, das ist keine Schranke).

---

### [Mittel | Niedrig | Mittel] SEC-029 — `Find my save…` macht jede Datei der Maschine in einem Klick zur Eingabe eines ungedeckelten `read_bytes()`

**Betroffen:** `UI_SPEC.md:2796-2798` (Filter `All files (*)`) ·
`nrplanner/inventory.py:194` (`_read_settled`, `blob = path.read_bytes()`) ·
`:214` `_decrypt_slots`

**Vertrauensgrenze:** heruntergeladener Spielstand → Programm. Die Grenze, die
der Nutzer am 02.09.2026 ausdruecklich scharf gelassen hat
(`security/findings.md:259-261`).

**Angriffspfad:** Der Filter laesst jede Datei zu. Der Nutzer waehlt (aus
Versehen oder auf Zureden) ein Plattenabbild von 30 GB; `_read_settled` liest
es vollstaendig in den Speicher, bevor irgendeine Pruefung greift. Die
Ausnahme faengt `_scan_save` (`:245`, `except Exception`), aber erst **nach**
der Allokation.

**Auswirkung:** Verfuegbarkeit. **Die Haerte der Save-Abwehr aendert sich
nicht** — ich habe sie am committeten Stand nachgesehen und sie traegt:
`MIN_BYTES_PER_RELIC_RECORD = 64` (`savefile.py:173`, Deckel in `:263/296`),
`MIN_BYTES_PER_LOADOUT_TABLE` (`:377/454/464`), zweiter Deckel
`Inventory._refuse_a_density_no_save_can_have` (`inventory.py:111`, gerufen in
`relics_for:166`). Was sich aendert, ist die **Erreichbarkeit**, und die
Luecke liegt genau **vor** dem ersten Deckel.

**Behebungsrichtung:** ein `stat().st_size` vor dem `read_bytes()` in
`_read_settled`, mit Ausgang **S4** (`UI_SPEC.md:2968-2973`) statt eines
Speicherbergs. Der echte Save dieser Installation liegt laut SEC-022-Messung
bei ~19 MB; eine Grenze im dreistelligen MiB-Bereich schneidet nichts weg und
faellt laut aus. Gehoert in **V3/V4**, nicht in V2.

**Zweite Stichprobe zur ersten:** die Zeile ist **nicht** neu und trifft heute
schon den Automatikweg (`find_saves()` glob `*/*.sl2`) — dort muss der
Angreifer die Datei aber erst ins Roaming-Profil legen. A15 ersetzt "Datei
ablegen" durch "Datei anklicken". Der Befund gilt fuer beide Wege; der Fix
sitzt an einer Stelle.

---

### [Niedrig | Niedrig | Niedrig] SEC-030 — `search_from` hat noch keine Regel zu Reparse-Punkten *(Hypothese, nicht gemessen)*

**Betroffen:** `UI_SPEC.md:2713-2734` (§4.2) · `ARCHITECTURE.md:5591`
(`search_from(p)`, **V1**, noch nicht gebaut)

**Vertrauensgrenze:** gewaehlter Ordner → gesuchter Ordner.

**Angriffspfad (Hypothese):** Der gewaehlte Ordner enthaelt eine
Verzeichnisverknuepfung (Junction/Symlink). Die Spec begrenzt die Suche auf
Tiefe 3, 2 Elternebenen, 400 Verzeichnisse und 2 Sekunden — das begrenzt
**Zeit und Zahl**, nicht das **Ziel**. Der angenommene Ordner kann damit
ausserhalb des Baumes liegen, den der Nutzer gesehen hat.

**Auswirkung:** gering und mittelbar — sie faellt mit SEC-026 zusammen, statt
eigenstaendig zu wirken. Deshalb Niedrig auf allen drei Achsen.

**Behebungsrichtung:** beim Abstieg keine Reparse-Punkte betreten und das
Ergebnis ueber `Path.resolve()` gegen den gewaehlten Baum halten. Kostet eine
Zeile, solange V1 noch nicht geschrieben ist; danach ist es ein Nachtrag.

**Nachweis:** keiner am Code — **die Funktion existiert nicht.** Gegenprobe
gefahren: `grep -rn "search_from\|looks_like_the_game\|is_named_nightreign"`
ueber `nrdata/` und `nrplanner/` → **0 Treffer**; zweite Maske
`getExistingDirectory|QFileDialog` → 0 Treffer ausserhalb `.venv`. Das deckt
sich mit dem Stand "A15: null Zeilen gebaut". **Als Hypothese gekennzeichnet,
nicht als Befund am Bestand.**

---

## 3. Frage 2 — was sich am Risiko wirklich aendert

**Was sich aendert:** genau **eine** Sache. Der Weg zu "fremder nativer Code
laeuft in diesem Prozess" fuehrte bisher ueber **Schreibrechte im
Spielordner** — und wer die hat, hat den Nutzerkontext ohnehin, weshalb SEC-006
angenommen wurde. Kuenftig fuehrt er ueber **eine Ordnerwahl**. Das ist die
ganze Verschiebung, und sie ist echt.

**Was sich nicht aendert:**

- **Kein Rechtegewinn.** Der Code laeuft als derselbe Nutzer, der ihn gewaehlt
  hat. Wer den Ordner unterschieben kann, koennte dem Nutzer ebenso gut eine
  `.exe` unterschieben. Der Angreifer gewinnt **Tarnung**, nicht Rechte.
- **Kein anonymer Ausloeser.** Ohne eine Handlung des Nutzers passiert nichts.
  Kein Netzweg, kein Dienst, kein zweiter Benutzer auf der Maschine.
- **Die Save-Abwehr.** Sie ist gemessen und steht (SEC-022/SEC-024 behoben,
  am committeten Stand nachgesehen, Fundstellen oben). Erreichbarkeit steigt,
  Haerte bleibt — die Einschaetzung des `architect` ist hier richtig, mit der
  einen Luecke aus SEC-029 davor.
- **Die eigene Spielinstallation.** Waehlt der Nutzer seinen eigenen Ordner —
  der Normalfall, und der einzige, den A15 ueberhaupt bedienen will —, gilt der
  Entscheid vom 02.09.2026 unveraendert. **A15 macht die eigene Installation
  nicht unsicherer. Es fuegt einen zweiten Fall hinzu.**

---

## 4. Frage 3 — was verhaeltnismaessig ist

### Muss

| # | Was | Wo | Kosten |
|---|---|---|---|
| **M1** | Der Satz "It is only read" faellt oder wird qualifiziert. Der Text darf nicht behaupten, es passiere nur ein Lesevorgang. | `UI_SPEC.md:2870` (A1), sinngemaess W1 → **V2** | ein Satz |
| **M2** | AK-112 bekommt eine Obergrenze fuer `regulation.bin`, in **derselben** Funktion, die die Annahme prueft. | `looks_like_the_game` → **V1** | eine Zeile plus Rezept |
| **M3** | Der Waechter zu R1–R6 haelt die zwei Invarianten aus AD-030 als **sicherheitstragend** fest, nicht nur als Ordnung: `paths/game` wird **nur** aus einer Nutzerbestaetigung geschrieben (nie aus einem Automatikfund), und die Gueltigkeitspruefung beim Start ist **dieselbe** Funktion wie die Annahmepruefung. | **V1/V2**, `qa-engineer` | im Entwurf bereits vorgesehen |

M3 ist keine neue Forderung — AD-030 verlangt beides bereits
(`ARCHITECTURE.md:5562-5565`, `5569-5572`). Neu ist die Begruendung: solange
das gilt, kann kein Codeweg dem Programm einen Ordner unterschieben, den der
Nutzer nie bestaetigt hat. Faellt eine der beiden, faellt die einzige Schranke
aus SEC-026. **Die toetende Mutation dazu gehoert in R1–R6.**

### Sollte

- **S1** — Weicht der aufgeloeste Ordner vom gewaehlten ab (Fall **C2**), ihn
  **vor** dem Bau bestaetigen lassen. Heute liegt zwischen C1/C2 und dem Bau
  ausdruecklich kein Klick (**AK-118**, `UI_SPEC.md:3086-3088`), und C1/C2
  gehen "sofort" in den Bau-Zustand (`:2936`). Im Fall **C1** aendert sich
  damit nichts — **AK-106 und A15 bleiben unberuehrt**; der Klick kostet nur
  dort, wo das Programm einen anderen Ordner nimmt als der Mensch gezeigt hat.
  Das ist eine **Spec-Aenderung an AK-118** und gehoert dem `ui-ux-designer`
  und dem `director`, nicht mir.
- **S2** — Groessenpruefung vor `read_bytes()` beim **gewaehlten** Spielstand
  (SEC-029), Ausgang S4. V3/V4.
- **S3** — Reparse-Punkte in `search_from` ausschliessen (SEC-030). V1,
  solange die Funktion noch nicht existiert.
- **S4** — Ein Waechtertest haelt fest, dass `ctypes.CDLL` **genau einmal** im
  Baum vorkommt und **nur** mit einem absoluten, aus dem aufgeloesten
  Spielordner gebauten Pfad gerufen wird. Heutiger Stand als `OFFEN`-Liste:
  **leer, 1 Fundstelle, absolut**. Er bindet gegen den Rueckfall, den niemand
  absichtlich baut: ein blosser DLL-**Name** wuerde die Standard-Suchreihenfolge
  von Windows benutzen und damit `PATH` und Arbeitsverzeichnis mit einbeziehen.

### Ueberzogen

- **Signatur-, Herausgeber- oder Hashpruefung der `oo2core*.dll`.** Es gibt
  keinen Vertrauensanker dafuer, die DLL-Fassungen wechseln mit dem Spiel, und
  ein falsches Nein macht den Erststart wieder zur Sackgasse — **das waere
  A15 gebrochen statt gesichert.** Und: es wuerde SEC-016/017/018 scharf machen
  (siehe Auflage unten).
- **Getrennter Prozess, Sandkasten, Integritaetsstufen** fuer die Extraktion.
  Ein privates Einzelplatzwerkzeug.
- **Eine Rueckfrage beim Start**, ob der gemerkte Ordner noch gewollt ist.
  Bricht AK-106 und ist genau die Reibung, die A15 beseitigt.
- **SEC-016/017/018 jetzt bauen.** Siehe naechster Abschnitt.

---

## 5. Frage 4 — traegt die Streichbegruendung noch? (Vorlage an den Nutzer)

**Der Wortlaut der Streichung** (`docs/plan-restarbeiten.md:107-112`,
`security/findings.md:26-28`): *"setzt entweder eine boesartige
Spielinstallation voraus — die der Nutzer am 02.09.2026 ausdruecklich als
vertrauenswuerdig eingestuft hat — oder einen Angreifer, der das Benutzerkonto
ohnehin schon kontrolliert."*

**Woertlich: traegt nicht mehr.** Unter A15 ist die boesartige
"Spielinstallation" weder die eigene noch ein uebernommenes Konto, sondern ein
Ordner, auf den der Nutzer zeigt. Beide genannten Voraussetzungen entfallen.

**Im Schluss: traegt weiter — a fortiori.** Der Angreifer, der einen Ordner
liefern kann, liefert **dieselbe Datei-Sammlung**: er kontrolliert die Archive
*und* die DLL. Wer eine Entpackbombe in `dcx.py` (SEC-016: `max_output_size` =
u32 aus der Datei, `dcx.py:39`), `dcx.py:42` (SEC-018: `zlib.decompress` ohne
`bufsize`) oder `tpf.py:37/53` (SEC-017: `file_count` gegen nichts geprueft —
am Code nachgesehen, **alle drei Stellen unveraendert**) unterbringen kann,
kann ebenso eine praeparierte `oo2core_9_win64.dll` unterbringen. Das eine
kostet Speicher, das andere gibt Codeausfuehrung. **Solange SEC-026 offen ist,
fuegen die drei Befunde dem Angreifer nichts hinzu.**

**Meine Empfehlung: die drei bleiben gestrichen.** Ich lege sie nicht erneut
vor. Ich lege dem Nutzer **eine** Frage vor, und zwar die, die er 05.09.2026
nicht gestellt bekommen konnte:

> Die Streichbegruendung nennt eine Voraussetzung, die A15 wegnimmt — und
> dieselbe Voraussetzung traegt die Annahme von **SEC-006** ("wer dort
> schreiben kann, hat den Nutzerkontext ohnehin"). Soll die Annahme in der
> neuen Fassung weitergelten, mit dem Zusatz **"… oder der Nutzer hat auf den
> Ordner gezeigt"** — oder soll die DLL-Seite geprueft werden?

**Auflage mit ihrer Randbedingung — und sie richtet sich gegen meinen eigenen
Bericht:** Die Dominanz-Begruendung oben (SEC-016/017/018 fuegen nichts hinzu)
gilt **ausschliesslich**, solange die DLL ungeprueft aus dem gewaehlten Ordner
geladen wird. Entscheidet der Nutzer sich fuer eine Herkunftspruefung, dann
sind die drei Entpackbomben der **verbleibende** Weg und muessen neu bewertet
werden. Deshalb steht in meiner Behebungsrichtung zu SEC-026 **ausdruecklich
keine** DLL-Pruefung — ich darf einen Mechanismus nicht in einem Befund
eingeschraenkt beschreiben und ihn in einer Auflage als allgemein wirksam
voraussetzen. **Eine Vorkehrung, drei Folgen: wer die DLL haertet, oeffnet
SEC-016/017/018.** Das gehoert in dieselbe Entscheidung, nicht in die naechste.

---

## 6. Muss V2 warten?

**Nein — V2 wartet auf keinen Fix.** Alle fuenf Befunde koennen parallel oder
spaeter behoben werden; keiner steht dem Bau im Weg.

| Befund | landet in | blockiert V2? |
|---|---|---|
| SEC-026 | keinem Bauschritt (Vorlage an den Nutzer) | nein |
| **SEC-027** | **V2 selbst** — der Text ist das, was V2 schreibt | **nein, aber siehe unten** |
| SEC-028 | V1 (`looks_like_the_game`) — liegt **vor** V2 | nein |
| SEC-029 | V3/V4 | nein |
| SEC-030 | V1 | nein |

**Die eine Bedingung:** **V2 darf nicht mit dem heutigen §7-Wortlaut starten.**
Nicht weil ein Fix fehlt, sondern weil V2 diesen Satz **baut**. Startet V2 mit
`UI_SPEC.md:2870` unveraendert, steht der falsche Satz danach in der
Oberflaeche, und die Korrektur kostet eine zweite Textrunde samt A8-, AK-127-
und AK-128-Nachweis statt einer Zeile im Auftrag.

Das ist eine **Entscheidung des `director`** (Wortlaut vom `ui-ux-designer`),
keine Bauarbeit. Dazu gehoert die zweite offene Entscheidung: **S1 / AK-118** —
ob der C2-Fall einen Klick bekommt. Auch die gehoert **vor** V2, weil V2 den
Uebergang C1/C2 → Bau-Zustand baut; danach ist sie ein Umbau.

**Zusammengefasst: V2 wartet auf zwei Saetze, nicht auf mich.**

---

## 7. Vertrauensgrenzen-Skizze des geprueften Bereichs

```
[ Steam-Bibliothekliste ]--(heute, ~14 feste Kandidaten)--\
                                                           >--> game_dir
[ Ordnerdialog: JEDER Ordner ]--(neu mit A15, 1 Klick)----/       |
                                                                  |
   Grenze 1 (VERSCHOBEN):   Herkunft des Spielordners             |
                            frueher: von Steam geschrieben        |
                            kuenftig: vom Menschen benannt        |
                                                                  v
                                       +--------------------------+-------------------------+
                                       |                          |                         |
                          ctypes.CDLL(game_dir/oo2core*.dll)   read_bytes(regulation.bin)  data*.bhd/bdt
                          -> DllMain laeuft im Prozess         -> ohne Obergrenze          -> dcx/tpf/bnd4
                             (SEC-026, SEC-006s Annahme)          (SEC-028)                   (SEC-016/17/18,
                             + Abhaengigkeiten aus demselben                                   gestrichen,
                               Ordner (DLL_LOAD_DIR)                                           dominiert von
                                                                                               SEC-026)

[ %APPDATA%\Nightreign\*.sl2 ]--(heute: Datei ablegen)---\
                                                          >--> save blob --> SEC-022/024-Deckel: HALTEN
[ Dateidialog, Filter All files (*) ]--(neu, 1 Klick)----/            ^
                                                                     |
   Grenze 2 (UNVERAENDERT SCHARF, Erreichbarkeit steigt)      SEC-029 sitzt DAVOR
                                                             (read_bytes ohne st_size)

   Grenze 3 (unveraendert): QSettings HKCU -- wer dort schreibt, hat den Kontext ohnehin.
                            paths/game wird NUR aus einer Nutzerbestaetigung geschrieben (AD-030).
```

---

## 8. Beobachtungen (kein Angriffspfad, keine Prioritaet)

- **B1 — Zwischen der Wahl und dem Codeladen liegt kein einziger Klick.**
  AK-118 verbietet ihn ausdruecklich; C1/C2 gehen "sofort" in den Bau
  (`UI_SPEC.md:2936/3086-3088`). W1 ist die einzige Rueckfrage und greift nur
  bei falschem **Namen** — den ein Angreifer richtig setzt. Der Ablauf hat
  damit **genau eine** Nutzerentscheidung, und die faellt im Systemdialog.
  Daraus folgt S1.
- **B2 — `oodle.load` laedt unbedingt**, nicht erst beim ersten
  KRAK-Mitglied (`extract.py:181`, `icons.py:82`, `bossdata.py:320`). Ein
  "laedt nur, wenn gebraucht" gibt es nicht und waere auch keine Abwehr.
- **B3 — `datasource._load_data` verschluckt jede Ausnahme der
  Live-Extraktion** (`:147-148`, `except Exception: pass`). Ein feindlicher
  Ordner, der beim Extrahieren scheitert, faellt **still** auf den alten Abzug
  zurueck. Das ist heutiges Verhalten und dokumentiert, wird mit A15 aber
  haeufiger erreichbar.
- **B4 — Der Ladeflag-Nebeneffekt** (`LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR`) ist
  kein Defekt des Projekts, sondern CPython-Verhalten seit 3.8. Genannt, weil
  er die Angriffsflaeche von "eine DLL" auf "diese DLL und ihre
  Abhaengigkeiten" erweitert.
- **B5 — `oodle._handle` ist global und wird nur einmal gesetzt** (`:37-38`).
  Waehlt der Nutzer in derselben Sitzung einen zweiten Ordner, bleibt die DLL
  des ersten geladen. Ohne Wirkung fuer die Sicherheit, aber es erklaert, warum
  ein Wechsel "ohne Neustart" nie ganz sauber ist.

---

## 9. Geprueft / nicht geprueft

**Geprueft:** die DLL-Ladekette (`oodle.py`, drei Aufrufer) · AK-106 bis
AK-132 gegen den Code · AD-030 Punkte 1–4 und der Aufloesungspunkt ·
`gamefiles.find_game_dir` vollstaendig · `firstrun.py` vollstaendig ·
`paths.py` vollstaendig · `datasource.py:85-175` · `dcx.py` vollstaendig ·
`tpf.read` · die Save-Abwehr am **committeten** Stand `ebc5708` ·
`security/findings.md` vollstaendig · `plan-restarbeiten.md` P6.

**Nicht geprueft, mit Grund:**

- **Der Arbeitsbaum-Stand von `nrplanner/app.py`, `nrplanner/inventory.py` und
  `tests/`** — dort arbeitet der parallele `developer`
  (`git status`: 6 geaenderte Dateien, 1 neue). Ich habe fuer diese Dateien
  **ausschliesslich `git show ebc5708:` gelesen**, damit meine Zeilenangaben
  gegen den Auftragsstand gelten und nicht gegen einen halbfertigen Umbau.
  **Ergibt sich aus dessen Aenderungen etwas an SEC-029, faellt es dort auf,
  nicht hier.**
- **`search_from`, `looks_like_the_game`, `is_named_nightreign`,
  `gamepath.py`** — existieren nicht (0 Treffer, zwei Masken). SEC-030 ist
  deshalb Hypothese, kein Befund.
- **Der Wortlaut der Ersatzsaetze zu SEC-027** — das ist `ui-ux-designer`
  und `technical-writer`, nicht meine Rolle. Ich nenne den Sinn, nicht den
  Satz.
- **Ein Junction-Versuch gegen `search_from`** — nichts zu messen.
- **Ausloesen irgendeines Pfades mit einer praeparierten DLL oder Datei** —
  Richtlinie, und der Angriffspfad ist am Code belegt.
- **`vendor/Paramdex`** — unveraendert vom Auftrag ausgeschlossen.
- **A-024/A-027 (Transparenztext, README "What it reads and where it writes")**
  — der `architect` hat bereits gemeldet, dass A15 zwei gespeicherte Werte
  hinzufuegt. **Ich ergaenze:** derselbe Text muss nach SEC-027 auch sagen, dass
  eine Bibliothek aus dem gewaehlten Ordner geladen wird — SEC-006s
  Nutzerentscheid vom 02.09.2026 verlangt dafuer schon heute *"ein ehrlicher
  Satz im README"* (`security/findings.md:99-101`). Das gehoert dem
  `technical-writer`, nach V3, und steht in keinem Auftrag.

---

## 10. Zusammenfassung an den `director`

| Prioritaet | Anzahl | Befunde |
|---|---|---|
| Hoch | 1 | SEC-027 (Panel-Text) |
| Mittel | 3 | SEC-026, SEC-028, SEC-029 |
| Niedrig | 1 | SEC-030 *(Hypothese)* |
| Beobachtungen | 5 | B1–B5, ohne Prioritaet |

### Gesamturteil: **CONCERNS**

**Begruendung, und was dagegen spricht — damit du widersprechen kannst:**
Kein Befund ist ohne eine Handlung des Nutzers ausloesbar, kein Befund gibt
Rechte, die der Nutzer nicht selbst haette geben koennen, und die Save-Grenze
haelt gemessen. Was offen ist, ist **eine Nutzerentscheidung** (traegt SEC-006s
Annahme unter A15 weiter?) und **zwei Saetze Text**. Das ist die Lage, fuer die
CONCERNS gemacht ist.

**Die Gegenposition, ausdruecklich:** wer die **Wirkung** von SEC-026 fuer
massgeblich haelt — Codeausfuehrung —, kommt auf Schwere Kritisch und damit
mechanisch auf **FAIL**. Ich habe SEC-026 als Mittel eingestuft, weil der
Mechanismus unvermeidbar, dokumentiert und bereits angenommen ist und heute
allein die **Annahmebegruendung** veraltet ist. Diese Einstufung ist ein
Urteil, kein Messwert. **Wenn du sie anders siehst, ist FAIL vertretbar** —
dann wartet V2 auf den Nutzerentscheid statt nur auf den Wortlaut.

**WAIVED vergebe ich nicht.** Falls du SEC-026 stillegen willst, braucht es
Eigentuemer, Geltungsbereich und Ablaufdatum von dir — und der Geltungsbereich
muss den Satz enthalten: *gilt nur, solange die DLL ungeprueft aus dem
gewaehlten Ordner geladen wird.*

### Was als Naechstes geschieht

1. **Vor V2** (Minuten, keine Bauarbeit): Wortlaut zu SEC-027 entscheiden
   (`ui-ux-designer`), und AK-118/S1 entscheiden (C2-Klick ja/nein).
2. **In V1**: SEC-028 (Groessenschranke in `looks_like_the_game`), SEC-030
   (Reparse-Punkte), M3 als toetende Mutation in R1–R6.
3. **Vorlage an den Nutzer**, eine Frage, nicht drei: gilt SEC-006s Annahme in
   der neuen Fassung? Ausgang bestimmt, ob SEC-016/017/018 gestrichen bleiben.
4. **Spaeter**: SEC-029 in V3/V4, A-024/A-027 nach V3 (`technical-writer`).
