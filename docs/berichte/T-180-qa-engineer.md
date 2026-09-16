STATUS: erledigt
AUFTRAG: T-180 — Die Befundregister wieder zur Wahrheit machen (qa-engineer)
GELESEN: docs/tasks/T-180.md; qa/findings.md (2754 Zeilen, vollstaendig);
security/findings.md (595 Zeilen, vollstaendig); docs/state.md (Stand
09.09.2026); docs/archiv/berichte/T-124-ui-ux-designer.md (Fundstelle des
"verlorenen" QA-210); tests/test_hostile_savefile.py,
tests/test_game_dir_recognition.py, tests/test_game_path_memory.py,
tests/test_first_run_panel.py, tests/test_save_read_in_the_background.py
(Code-Gegenprobe zu SEC-023/031/032/035, QA-215); nrplanner/inventory.py,
nrdata/gamefiles.py, .github/workflows/tests.yml (Code-Gegenprobe)
GEAENDERT: qa/findings.md (umgebaut: Kopf + eine Tabelle, 224 Zeilen);
qa/verlauf.md (neu: Verlauf + Abschnittsverzeichnis); security/findings.md
(umgebaut: Kopf + eine Tabelle, 35 Zeilen); security/verlauf.md (neu:
Verlauf + Abschnittsverzeichnis); docs/berichte/T-180-qa-engineer.md (dieser
Bericht). Nicht committet (Vorgabe).
ANNAHMEN: Sortierreihenfolge der Tabelle numerisch nach ID (mit Buchstaben-
suffix nach der reinen Zahl) gewaehlt, da der Auftrag keine Reihenfolge
vorschreibt und die Ursprungstabelle grossteils numerisch war. "Spalten
unveraendert lassen" so gelesen, dass die 8-Spalten-Form fuer QA und die
5-Spalten-Form fuer SEC verbindlich sind — drei vorgefundene Zeilen im
6-Spalten-Kurzformat (QA-101/113/114) wurden dafuer umgebaut, siehe Befund
unten. Wo Sev/Adressat im Fliesstext nicht benannt waren (QA-090 bis
QA-093), wurde "unklar" statt einer Schaetzung eingetragen.
NAECHSTER: director
BLOCKIERT DURCH: nichts

# T-180 — Bericht

## Ergebnis in Kuerze

Beide Register sind jetzt Kopf + eine Tabelle; aller chronologische Text
steht unverkuerzt in `qa/verlauf.md` bzw. `security/verlauf.md`, mit
Abschnittsverzeichnis (Ueberschrift + Zeilennummer) am Kopf. Alle 36 QA- und
9 der 10 SEC-Nummern (siehe "keine Zeile, weil" unten) sind jetzt Tabellen-
zeilen mit dem Status, den der Fliesstext traegt. Jede Statuszelle beginnt
mit einem der sieben Woerter, kleingeschrieben, ohne Fettung. Dabei sind
sechs Befunde aufgetaucht, zwei davon P1/P2-relevant.

**Gemessene Zahlen (12.09.2026, Commit `e06386c` + meine Aenderungen,
ungecommittet):**

```
grep -oE '^\| QA-[0-9]+' qa/findings.md | sort -u | wc -l        -> 221
grep -oE '^\| QA-[0-9]+' qa/findings.md | sort | uniq -d         -> "| QA-099"  (siehe Befund 3, kein echtes Duplikat)
grep -oE '^\| SEC-[0-9]+' security/findings.md | sort -u | wc -l -> 35
grep -oE '^\| SEC-[0-9]+' security/findings.md | sort | uniq -d  -> (leer)
grep -cE '^\| (QA|SEC)-[0-9]+[A-Za-z]? .*\| (offen|teilweise|behoben|geschlossen|zurueckgestellt|waived|unklar)' qa/findings.md       -> 224 (= Zeilenzahl der Tabelle)
grep -cE '^\| (QA|SEC)-[0-9]+[A-Za-z]? .*\| (offen|teilweise|behoben|geschlossen|zurueckgestellt|waived|unklar)' security/findings.md -> 35  (= Zeilenzahl der Tabelle)
wc -l qa/findings.md qa/verlauf.md             -> 243 + 2680 = 2923  (>= 2754 Altstand)
wc -l security/findings.md security/verlauf.md -> 53 + 612 = 665    (>= 595 Altstand)
```

Echte, eindeutige Tabellenzeilen (Buchstabensuffixe QA-099a/b/c mitgezaehlt,
per `grep -oE '^\| QA-[0-9]+[A-Za-z]?' | sort -u | wc -l`): **224 fuer QA**
(genau die Zeilenzahl — keine echten Duplikate mehr), **35 fuer SEC**.

## Vorgehen

1. Trennung zuerst (Vorgabe der Zugschwellen-Sicherheit): jede Zeile, die dem
   Muster `^\| (QA|SEC)-\d+[A-Za-z]?\s*\|` entspricht, ist eine Tabellenzeile
   und wanderte in die neue Registerdatei; jede andere Zeile wanderte
   unveraendert und in Originalreihenfolge nach `verlauf.md`. Damit landet
   **jede** Zeile aus dem Altstand in genau einer der beiden neuen Dateien
   (Vorgabe 1, "entweder/oder").
2. Fuer die 36 QA- und 10 SEC-Nummern aus dem Auftrag den Fliesstext gelesen
   (komplett, alle betroffenen Abschnitte) und je eine Tabellenzeile mit dem
   dort belegten Status gebaut. Wo eine Zahl fehlte, "unklar" eingetragen,
   nicht geraten.
3. Statuszellen aller (auch der schon vorhandenen) Zeilen mechanisch
   normiert: alle `**`-Fettung aus der Statuszelle entfernt, dann das
   fruehestmoegliche Vorkommen eines der sieben Statuswoerter (in jeder
   Gross-/Kleinschreibvariante) gesucht und als fuehrendes, kleingeschriebenes
   Wort gesetzt; der Rest der Zelle folgt nach " — ". Das ist ein reiner
   Formattransform, keine Neubewertung — ich habe keine Statusbehauptung
   geaendert, nur ihre Schreibweise.
4. Stichprobe: alle 224+35 = 259 normierten Zellen wurden in einer Vorschau
   durchgesehen (nicht nur automatisiert geprueft), bevor die Dateien
   geschrieben wurden.

## Befunde

### [P1 | Major | Mittel] Ein angeforderter QA-Befund (A7-Verstoss der Advisor-Bar) wurde nie ins Register aufgenommen — QA-210 ist keine uebersprungene Nummer, sondern ein verlorener Auftrag

**Adressat:** director (ID-Vergabe und Einordnung), developer/qa-engineer (Umsetzung/Verifikation nach Zuteilung)
**Betroffen:** `docs/archiv/berichte/T-124-ui-ux-designer.md:154-169`; potenziell `nrplanner/advisorbar.py` (`asking_from`), `nrplanner/relicpicker.py` (`SlotAdvice.ranking`), `_say_what_they_are_worth`

**Reproduktion:**
1. `grep -rn 'QA-210' --include=*.md --include=*.py .` (ausserhalb `.git/`)
   liefert drei Treffer: zwei in `docs/tasks/T-180.md` (die Behauptung, die
   Nummer sei nur uebersprungen) und einen in
   `docs/archiv/berichte/T-124-ui-ux-designer.md:154`.
2. Dort, Punkt 4: *"Neuer QA-Befund, A7, aelter als AD-028 — bitte als
   QA-210 aufnehmen:"* — mit vollstaendiger Beschreibung: Der Relikt-Picker
   zeigt den Satz *"The game's data carries no figures this goal can be
   ranked on..."* auch dann, wenn der wahre Grund ist, dass **kein
   Spielstand gelesen wurde** (`advisorbar.asking_from` gibt fuer "kein
   Save" `None` zurueck, `_say_what_they_are_worth` bildet jedes `None` auf
   `NO_FIGURES_AT_ALL` ab). Fertiger Alternativtext ist im Bericht
   vorgeschlagen.
3. `grep -n 'NO_FIGURES_AT_ALL\|no save was read\|advisorbar.asking_from'
   qa/findings.md docs/state.md` — kein Treffer. Die Beschreibung wurde
   weder unter QA-210 noch unter irgendeiner anderen ID je ins Register
   uebernommen.

**Erwartet:** Ein von einer Rolle explizit mit Zielnummer angemeldeter
Befund landet im Register.
**Tatsaechlich:** Er landet in keinem der beiden durchsuchten Dokumente.

**Analyse:** T-124 war ein `ui-ux-designer`-Auftrag; der dort gemeldete
Befund gehoert in die Zustaendigkeit des Directors (ID-Vergabe). Er ist
zwischen "im Bericht angemeldet" und "im Register eingetragen"
verlorengegangen — vermutlich derselbe Zyklus-Uebergang, in dem laut
Auftrag "die Tabellen seit rund Zyklus 10 nicht mehr fortgeschrieben
wurden".

**Auswirkung:** Ein moeglicher, konkret beschriebener A7-Verstoss
(Programm behauptet etwas ueber Spieldateien, das eigentlich eine Aussage
ueber den Spielstand waere) ist seit T-124 unbearbeitet und unsichtbar.
Der `ui-ux-designer` hat selbst vermerkt, dass die Erreichbarkeit am Lauf
zu pruefen ist ("Der `qa-engineer` entscheidet das an einem Lauf").

**Vorschlag:** Director vergibt eine neue ID (der naechste freie QA-
Nummernkreis, laut `docs/state.md` ab QA-220 — nach diesem Bericht ab
QA-223, da 220-222 belegt sind), traegt den Befundtext aus T-124 ein und
ordnet ihn zur Verifikation ein. **Ich habe keine Zeile fuer "QA-210"
angelegt** — weder im Fliesstext von `qa/findings.md` noch in
`security/findings.md` existiert unter diesem Namen ein Befund, und
Befund-IDs vergebe ich nicht (Scope-Grenze).

---

### [P2 | Minor | Hoch] Fuenf Befunde haben Code-/Test-Belege fuer einen Fix, den der Fliesstext beider Register nicht kennt — die Register hinken dem Code hinterher

**Adressat:** security-reviewer (SEC-023/031/032/035), qa-engineer/developer (QA-215), director (Einordnung)
**Betroffen:** `qa/findings.md` (Fliesstext QA-215), `security/findings.md`
(Fliesstext SEC-023/031/032/035); `nrplanner/inventory.py::_changed_at`,
`nrdata/gamefiles.py:65-69`, `tests/test_game_dir_recognition.py:214`,
`tests/test_hostile_savefile.py:40,748,834`,
`tests/test_save_read_in_the_background.py:1088`

**Reproduktion (Muster, fuenf Einzelfaelle als Beleg):**
1. `grep -rn 'SEC-023\|SEC-031\|SEC-032\|SEC-035\|QA-215' --include=*.py
   nrplanner nrdata tests` — 17 Treffer in Code und Tests, die diese IDs
   als Grund fuer eine bestehende Schutzmassnahme zitieren.
2. Beispiel SEC-035/SEC-023: `nrplanner/inventory.py:340-361`,
   `_changed_at()` faengt `OSError` von `path.stat()` ab und zitiert
   SEC-035 woertlich im Docstring; **derselbe Aufruf** ersetzt exakt die
   Stelle, die SEC-023 am 07.09.2026 als `inventory.load:199`
   beschrieben hatte (`sorted(saves, key=_changed_at, ...)` in `scan()`,
   Zeile 418).
3. Beispiel SEC-031: `nrdata/gamefiles.py:69` zitiert "SEC-031" woertlich
   als Grund fuer den `looks_like_the_game`-Aufruf vor jeder Ladung;
   `tests/test_game_dir_recognition.py:214` — Docstring *"SEC-031, second
   half: the six bare-drive candidates are gone."*
4. Beispiel QA-215: `tests/test_save_read_in_the_background.py:1088` —
   Docstring *"Which is where the missing tooth was (QA-215): AK-245 names
   its own..."*

**Erwartet:** Ein Fix, der im Code steht und von einem Test gehalten wird,
zieht die Statuszeile im Register nach.
**Tatsaechlich:** Der Fliesstext beider Register (meine einzige zulaessige
Quelle fuer die Statusspalte, Vorgabe 4) nennt fuer keinen der fuenf Faelle
eine Schliessung. Ich habe sie deshalb **als `offen` eingetragen** — mit
einem Verweis auf den Code-Fund in der Erlaeuterungsspalte, damit die
Diskrepanz sichtbar bleibt, statt sie durch eine eigene Neubewertung
stillschweigend zu schliessen (Scope-Grenze: "Kein Befund wird neu
bewertet").

**Analyse:** Dieselbe Klasse, die T-180 ueberhaupt ausgeloest hat — nur
eine Ebene tiefer. Die Tabelle hinkte dem Fliesstext hinterher; jetzt zeigt
sich, dass der Fliesstext selbst schon hinter dem Code hinterherhinkt.

**Auswirkung:** Wer sich auf `security/findings.md`/`qa/findings.md`
verlaesst, haelt fuenf tatsaechlich (mutmasslich) geschlossene Befunde fuer
offen — das verzerrt A2/A1-Aussagen nach oben (mehr offene Hoch/Mittel-
Befunde als tatsaechlich vorhanden) und kostet bei der naechsten
Sicherheitspruefung erneuten Aufwand fuer etwas, das schon gebaut ist.

**Vorschlag:** `security-reviewer` bestaetigt SEC-023/031/032/035 am Code
(die Fundstellen oben sind ein Anfang, kein vollstaendiger Nachweis) und
zieht die Statuszeilen nach; ebenso QA-215 fuer `developer`/`qa-engineer`.
Da ich fuer T-180 keine Befunde neu bewerten darf, tue ich das hier
ausdruecklich nicht selbst.

---

### [P3 | Minor | Mittel] Die Abnahme-Greps des Auftrags koennen wegen QA-099a/b/c nie "leer" werden, ohne echte Befunde zu verschmelzen

**Adressat:** director
**Betroffen:** `docs/tasks/T-180.md:26` (Behauptung "QA-099 ... stehen ...
zweimal"), Abnahmekriterium `grep -oE '^\| QA-[0-9]+' ... | uniq -d`

**Reproduktion:**
1. `grep -n '^| QA-099 |' qa/findings.md` (Altstand) — genau **ein** Treffer
   (Zeile 1444). Es gibt keine zweite Zeile mit der *exakten* ID `QA-099`.
2. `grep -n '^| QA-099a |\|^| QA-099b |\|^| QA-099c |' qa/findings.md` —
   drei weitere, **eigenstaendige** Befunde (eigener Titel, eigene
   Prioritaet, eigenes Datum), begruendet im Text selbst: *"ID-Nachtrag zu
   QA-099, weil der Nummernkreis der Scaling-Session voll ist"*.
3. `grep -oE '^\| QA-[0-9]+' qa/findings.md | sort | uniq -c | awk
   '$1>1'` (Altstand) zeigt **4x "| QA-099"** — das ist der Regex, der bei
   `QA-099a` nur `QA-099` matcht (kein Wortende-Anker), nicht eine echte
   Vervierfachung.
4. Mit korrigiertem Muster (`^\| QA-[0-9]+[a-z]?`) sind es **188** echte,
   eindeutige IDs im Altstand statt 185, und die einzige *echte* Dublette
   ist `QA-101` (zwei Zeilen mit identischem Text-Praefix, siehe unten) —
   nicht `QA-099`.

**Erwartet:** Der Auftrag sagt, "QA-099 und QA-101 stehen je zweimal als
Tabellenzeile" und verlangt danach `uniq -d` leer.
**Tatsaechlich:** Nur QA-101 ist eine echte Dublette. QA-099 erscheint nur
einmal; die "Vervierfachung" ist ein Artefakt der Buchstabensuffixe
QA-099a/b/c, die selbst gueltige, unterschiedliche Befunde sind und nicht
zusammengefuehrt werden duerfen, ohne Inhalt zu verlieren (Vorgabe 1).

**Analyse:** Solange QA-099a/b/c als eigene Zeilen bestehen (das verlangt
Vorgabe 1 ausdruecklich), bleibt `grep -oE '^\| QA-[0-9]+' | uniq -d` in
jeder zukuenftigen Pruefung "| QA-099" zeigen — das Kriterium aus dem
Auftrag ("muss leer sein") ist mit dem in Vorgabe 1 verlangten
Erhaltungsgebot **nicht gleichzeitig erfuellbar**, ohne die Buchstaben-IDs
zu verlieren.

**Auswirkung:** Der Director wuerde beim Nachrechnen mit dem im Auftrag
genannten Befehl faelschlich einen offenen Befund sehen.

**Vorschlag:** Abnahme-Grep auf `'^\| (QA|SEC)-[0-9]+[A-Za-z]?'` erweitern
(dann leer, siehe Zahlen oben), oder den Sonderfall QA-099a/b/c im
Abnahmeprotokoll explizit als bekannte, gewollte Nicht-Dublette vermerken.

---

### [P4 | Trivial | Hoch] Drei Tabellenzeilen im Altstand nutzten ein 6-Spalten-Kurzformat ohne Sev/Verifiziert

**Adressat:** developer/director (kuenftige Konsistenz), keine Aenderung am Befundinhalt
**Betroffen:** `qa/findings.md` Altstand, Zeilen 1490-1504 (QA-101-Zweitfassung, QA-113, QA-114)

**Reproduktion:** `awk -F'|' '/^\| (QA|SEC)-[0-9]/ {if (NF!=10) print NF,
$2}' qa/findings.md` (Altstand) zeigt drei Zeilen mit 8 statt 10 Feldern
(= 6 statt 8 Spalten): die T-049-Ersatzzeile fuer QA-101 sowie QA-113 und
QA-114, alle explizit im Format `ID | Titel | Prio | Adressat | Status |
Letzte Pruefung` angelegt (Kommentar im Text: *"Die Datei bestand bereits
und wird fortgefuehrt; ich lege sie nicht selbst an."*).

**Erwartet:** Vorgabe 7 verlangt die 8-Spalten-Form unveraendert.
**Tatsaechlich:** Drei Alt-Zeilen hatten nie 8 Spalten.

**Analyse:** Vermutlich eine punktuelle Verkuerzung durch die damalige
Rolle, nie korrigiert.

**Auswirkung:** Ohne Eingriff waere die neue, einheitliche Tabelle an
diesen drei Stellen fehlausgerichtet (Spaltenversatz in jedem Markdown-
Renderer).

**Vorschlag (bereits umgesetzt, hier nur dokumentiert):** Auf 8 Spalten
gebracht. Fuer QA-101 wurden Sev ("Major") und Verifiziert
("Gegenbeispiel-Kandidatensatz, Effekt- und Bestandsauszaehlung") aus der
**ersten**, laengeren Fassung derselben ID uebernommen (dort vorhanden,
inhaltlich nicht widersprochen) und das im Zellentext vermerkt
("aus der ersetzten Erstfassung uebernommen"). Fuer QA-113/QA-114, wo es
keine fruehere Fassung zum Uebernehmen gibt, wurde wortwoertlich
`(fehlt in der Quelle)` eingetragen statt eine Schwere/Verifikation zu
erfinden.

---

## Muster / systemische Beobachtung

Befund 2 (Registerstatus hinter dem Code) und Befund 1 (verlorener
Auftrag) haben dieselbe Wurzel: **Meldungen aus Berichten/Code erreichen
das Register nicht zuverlaessig, wenn die Rolle, die den Fix baut, nicht
auch die ID kennt oder die Statuszeile zieht.** Das ist genau das
Symptom, das T-180 beheben sollte — es geht offenbar auf der naechsten
Ebene weiter (Bericht -> Register, Code -> Register). Eine strukturelle
Abhilfe waere ausserhalb meines Scopes (das ist eine Verfahrensfrage fuer
den Director), aber die Wiederholung des Musters ist selbst meldenswert.

## Beobachtungen

Der urspruengliche Kopf beider Dateien (Titel, Quellen-Zeile, alte
Statuswortliste) wurde nicht geloescht, sondern als erster Abschnitt in die
jeweilige `verlauf.md` verschoben, waehrend `findings.md` einen neu
formulierten, kuerzeren Kopf bekam — das ist Auslegungssache der
Formulierung "kurzer Kopf" in Vorgabe 2, keine inhaltliche Aenderung, da
der alte Kopf vollstaendig erhalten bleibt.

## Explorationsprotokoll

- Gesamten Fliesstext beider Dateien gelesen (nicht nur die 46 fraglichen
  Abschnitte), um Statusaktualisierungen an anderer Stelle (Statuskorrektur-
  Tabellen) nicht zu verpassen — das hat die Schliessungen fuer QA-194,
  QA-203, QA-205, QA-191(teilweise), SEC-022, SEC-024 gefunden, die sonst
  als "offen" haetten stehenbleiben koennen.
- Trennung Tabellenzeile/Fliesstext ueber ein Skript (Python, im
  Scratchpad, nicht im Projektbaum) statt manuell — bei 3.349 Zeilen/259
  Tabellenzeilen war Handarbeit weder genau noch budgetierbar; jede
  Statuszelle wurde danach in einer Vorschau durchgesehen (nicht blind
  automatisiert uebernommen), drei Nachbesserungen daraus (siehe
  Vorgehen Punkt 3-4: Fettungsreste, drei Zellen ohne eines der sieben
  Woerter, zwei Fuellwoerter "Deckel"/"neu,").
- Fuer die fuenf "Register hinkt Code hinterher"-Faelle gezielt im Code und
  in Tests nach den ID-Zitaten gesucht (zwei unabhaengige Suchmasken:
  `grep -rn 'SEC-0..'` und Docstring-Lesung an den Fundstellen), nicht nur
  vermutet.
- QA-210 unabhaengig von der Auftragsbehauptung nachgesucht: zuerst wie im
  Auftrag vorgeschlagen (`qa/ docs/state.md`), dann repo-weit ueber `*.md`
  und `*.py` (Nenner: gesamter Baum ausser `.git/`) — das hat die
  T-124-Fundstelle gebracht, die die engere Suche nicht gefunden haette.
- Keinen Server gestartet, keine Suite gelaufen (Vorgabe: reine
  Dokumentenarbeit) — nichts aufzuraeumen.

## Offene Fragen

- **An den director:** Soll QA-210 als neue ID mit dem Inhalt aus T-124
  vergeben werden, oder gilt der Befund durch Zeitablauf/Architekturwandel
  (AD-028 wird im Bericht als juenger genannt) als ueberholt? Ich habe den
  Inhalt nicht gegen den heutigen Code geprueft (ausserhalb des
  Auftragsscopes, reine Dokumentenarbeit).
- **An security-reviewer/director:** Sind SEC-023, SEC-031, SEC-032,
  SEC-035 tatsaechlich durch die zitierten Code-/Testfundstellen
  geschlossen, oder decken diese Tests nur einen Teilaspekt? Ich habe nur
  gelesen, nicht mutationsgepr ueft.

## Nicht getestet

- Ob die 224 QA- bzw. 35 SEC-Tabellenzeilen inhaltlich korrekt sind (das
  war nie Teil des Auftrags — "Kein Befund wird neu bewertet").
- Rendering der Markdown-Tabellen in einem echten Viewer (nur strukturell
  gegen Spaltenzahl und Zeilenumbrueche geprueft, s. o.).
- Der Wahrheitsgehalt der fuenf "Register hinkt Code hinterher"-Vermutungen
  (Befund 2) am Code selbst — nur Fundstellen benannt, keine Mutationsprobe.

## QA-Log

`qa/findings.md` existiert jetzt als reines Register (keine
Fliesstext-Historie mehr in dieser Datei); die folgende Tabelle fasst nur
die in **diesem** Bericht neu gefundenen/erhoehten Punkte zusammen, nicht
die 224+35 Einzelbefunde des Registers selbst (die stehen vollstaendig in
`qa/findings.md`/`security/findings.md`).

| ID | Titel | Prioritaet | Adressat | Status | Datum letzter Pruefung |
|---|---|---|---|---|---|
| (neu, director vergibt) | QA-210 aus T-124 nie ins Register uebernommen (Advisor-Bar A7-Verstoss) | P1 | director | offen | 2026-09-12 |
| (kein neuer Fund, Registerhinweis) | SEC-023/031/032/035, QA-215: Register hinter Code-Fix zurueck | P2 | security-reviewer, developer | offen | 2026-09-12 |
| (kein neuer Fund, Verfahrenshinweis) | Abnahme-Grep des Auftrags kann wegen QA-099a/b/c nie leer werden | P3 | director | offen | 2026-09-12 |
| (kein neuer Fund, bereits behoben in dieser Aenderung) | Drei Alt-Zeilen im 6-Spalten-Kurzformat | P4 | developer/director | behoben (in diesem Umbau) | 2026-09-12 |

## Zusammenfassung (an director)

**Befunde:** 1x P1, 1x P2, 1x P3, 1x P4 (Zaehlung s. o.; die vier
Registerbefunde selbst, QA-090 bis QA-222 und SEC-021 bis SEC-035, sind
Datenuebernahme aus dem Fliesstext, keine neuen QA-Befunde in diesem
Sinne).

**Gesamturteil: CONCERNS.** Das Abnahmekriterium dieses Auftrags (zwei
Register = Kopf + eine vollstaendige, greppbare Tabelle; Verlauf
abgetrennt; nichts geloescht) ist erfuellt und mit den geforderten Zahlen
belegt. Der P1-Fund (verlorener QA-210) ist kein Mangel an dieser Arbeit,
sondern eine Entdeckung *durch* sie — genau das, wofuer der Auftrag da war.
Er sollte vor der naechsten Baurunde entschieden werden (ID vergeben oder
bewusst verwerfen), aber er blockiert T-180 selbst nicht.
