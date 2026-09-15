STATUS: erledigt
AUFTRAG: T-176 - clean-room: laeuft 1.9.0 auf einem fremden System? (release-manager)
GELESEN: docs/tasks/T-176.md, docs/release/ROLLOUT.md, docs/state.md, docs/legal/AUFLAGEN.md, README.md, nrplanner/gamepath.py, nrdata/gamefiles.py, nrplanner/shortcut.py, nrplanner/firstrun.py (Ausschnitt), nrplanner/app.py (Ausschnitt, shortcut-Zeilen)
GEÄNDERT: docs/berichte/T-176-release-manager.md (neu). Sonst nichts im Repo — dist/NightreignHelper.exe und dist/NightreignHelper-notices.zip nur gelesen/gehasht, nicht veraendert (SHA-256 vor und nach dem Lauf identisch). Erzeugte Testumgebung lag ausschliesslich unter dem Scratchpad `…/scratchpad/T-176/` (isoliertes LOCALAPPDATA/APPDATA, zwei Registry-Organisationen `DankYeeterT176Fresh` und `DankYeeterT176Update`) — vollstaendig aufgeraeumt, siehe unten.
ANNAHMEN: keine — AUFLAGEN.md wurde vor Beginn gelesen, keine offene rote Auflage (A-020/A-033 erfuellt, A-025 vom Nutzer entschieden „fortsetzen", A-010 zurueckgestellt/sperrt nicht). Der Auftrag enthielt GOAL- und State-Zitate; keine Nachlese noetig.
NÄCHSTER: power-user
BLOCKIERT DURCH: nichts

## Kopfantwort

**1.9.0 ist auf einem System ohne Entwicklungswerkzeuge installierbar und lauffaehig.** Nur die EXE in ein leeres Verzeichnis kopiert, nach README gestartet — sie laeuft, baut ihre Daten auf, speichert, ueberlebt Neustart und Zweitinstanz-Versuch.

**Das Update von v1.7.1 erhaelt die Nutzerdaten.** Drei Builds mit den kritischen Namen (`Fire / Ice`, `Fire | Ice`, `FIRE ICE MAX`) wurden unter v1.7.1 angelegt, die EXE anschliessend durch 1.9.0 ersetzt — alle drei sind nach der automatischen Migration vorhanden, korrekt benannt und in der laufenden Oberflaeche auswaehlbar. Ein kleiner Bookkeeping-Fund dazu unten (kein Datenverlust, siehe „An den developer").

**A15-Dialog konnte ich auf dieser Maschine nicht ausloesen** — dazu unten mehr, das ist ein wichtiger Befund gegen die Auftragsannahme, nicht ein Scheitern meines Laufs.

## Geprüfte Umgebung — und was an Isolierung nicht erreicht wurde

Kein Zugriff auf VM, Container oder ein zweites Windows-Konto in dieser Sitzung — alles lief auf demselben Windows-10-Rechner, demselben Benutzerkonto, das auch die Entwicklung traegt. Was isoliert wurde:

- **Zwei komplett getrennte Testverzeichnisse** unter dem Scratchpad, je mit leerem `LOCALAPPDATA`, leerem `APPDATA` und eigener `NIGHTREIGN_SETTINGS_ORG` (`DankYeeterT176Fresh` fuer den Erststart-Test, `DankYeeterT176Update` fuer den Update-Weg). Vor jedem Start per `$env:` gesetzt und im selben Aufruf sofort geloggt — nachgewiesen, nicht behauptet.
- **Nachgewiesen, dass die echten Nutzerdaten unberuehrt blieben:** `HKCU\Software\DankYeeter\NightreignHelper\builds\1` enthaelt keinen der Testnamen, `%LOCALAPPDATA%\NightreignHelper` traegt Zeitstempel von vor dieser Sitzung (5./8./9. September, keine Aenderung durch diesen Lauf), das echte Startmenü enthaelt nur die Steam-Verknuepfung des Spiels, keine `NightreignHelper.lnk`. Der feste Testabzug (`NightreignHelper-Testabzug`) wurde nicht angefasst — wie vorgeschrieben nicht kopiert.
- **Nicht isoliert:** Es ist derselbe Rechner, dasselbe Konto, dieselbe reale Steam-Installation. Kein PATH-Kahlschlag, keine Kontrolle darüber, dass „kein Python erreichbar" waere — bei einer PyInstaller-Einzeldatei ist das aber ohnehin irrelevant fuer die Lauffaehigkeit: die EXE bringt ihre eigene Python-Laufzeit mit und ruft nichts vom System-PATH ab (das war Gegenstand des `build`-Laufs, hier nicht erneut geprueft).
- **UI-Interaktion:** Kein Computer-Use-Werkzeug in dieser Sitzung verfuegbar. Interaktion erfolgte ueber Windows UI Automation (`System.Windows.Automation`) per PowerShell — Fenster/Buttons/Textfelder programmatisch gefunden und bedient, keine Bildschirmabzuege (NH-002 ohnehin eingehalten, da kein Screenshot gemacht wurde). Das ist ein legitimes, aber blindes Verfahren: ich sehe keine Pixel, nur den Accessibility-Baum. Wo das nicht ausreichte, steht es unter „Ungeprüft".

## Ablauf und Ergebnisse

### 0. Artefaktpruefung — bestanden

`dist/NightreignHelper.exe`: 59.062.648 B, SHA-256 `a2180d5db3a2b1b1aaf88028c6e7a1429087596e58ec3757469fd234e1366ef3` — identisch zur Angabe des Directors. `FileVersion`/`ProductVersion` der Ressource: `1.9.0`, `CompanyName DankYeeter`. `dist/NightreignHelper-notices.zip`: 46.480 B, SHA-256 `51a0b7cb8ed3aa1eced1c2e1868380ecdf778950eb3881329ee46ec25f334419`, Ordnerstruktur per `unzip -l` bestaetigt (`licenses\`, `vendor\Paramdex\NOTICE`, `LICENSE`, `THIRD_PARTY.md` — nicht alles auf einer Ebene).

### 1. Erstinstallation (frische Isolierung, v1.9.0) — bestanden

Nur die EXE in ein leeres Verzeichnis, gestartet exakt wie im README beschrieben („Download … and run it"). Fenster erscheint als **zwei Prozesse** (PyInstaller-Bootloader + eigentliche App — normal fuer diese Bauform, README erwaehnt es nicht, ist aber kein Fehlverhalten). Hauptfenstertitel nach Abschluss: `Nightreign Helper 1.9.0`.

**Automatische Spielerkennung erfolgreich, kein A15-Dialog.** Auf diesem Rechner liegt Nightreign in einer Steam-Bibliothek auf `D:`, korrekt in `libraryfolders.vdf` eingetragen. `nrdata/gamefiles.py:find_game_dir()` liest Registry + `libraryfolders.vdf` und findet den Ordner direkt — **ohne** den entfernten Laufwerks-Rueckfall `C:`–`H:` zu brauchen. Der Auftrag ging davon aus, dass genau hier „der Fall" liege, den der `power-user` dann sieht — **das stimmt auf dieser Maschine nicht**: `paths/game` und `paths/save` wurden nicht geschrieben (`remember_game()` wird laut Quelltext nur bei manueller Bestaetigung aufgerufen, nicht bei automatischem Erfolg), und in der Registry existiert kein `paths`-Schluessel. Siehe „Ungeprüft" unten.

**Erstaufbau gemessen:** Prozessstart 12:24:59, `nightreign_data.json` fertig 12:27:42 → **163,3 s**. Icon-Pack wuchs im Hintergrund weiter (779 Dateien nach weiteren ~10 s, 816 nach ~60 s) waehrend das Hauptfenster bereits reagierte (`Responding=True`, Titel gesetzt) — **A6 (Oberflaeche blockiert nicht) bestaetigt**, aber die Angabe „takes about a minute" im Fortschrittsdialog trifft nicht zu: gemessene Dauer ist **2,7×** die genannte Zeit, liegt aber innerhalb der von QA-198 berichteten Spanne (107 s – 5 min). Siehe „An den developer".

**Startmenue-Verknuepfung:** entstand automatisch im **isolierten** `APPDATA` (`…\Start Menu\Programs\Nightreign Helper.lnk`), weil die Checkbox „Add to my Start Menu" im Fortschrittsdialog **standardmaessig angehakt** ist (`nrplanner/firstrun.py:871`) — kein Bug, README-Wortlaut „offers" trifft es sinngemaess (Angebot mit Vorauswahl, keine Ja/Nein-Abfrage danach).

**Schreibende Aktion:** Build `Fire / Ice T-176` unter der Chalice „Wylder's own" gespeichert (UI Automation: Save-Button → Eingabefeld „Name this build:" → OK). In der Registry (`HKCU\Software\DankYeeterT176Fresh\NightreignHelper\builds\1`) korrekt unter Schema 3 mit prozent-kodiertem Schluessel abgelegt, `__schema = 3`.

**Neustart:** Prozess beendet, EXE erneut gestartet — Fenster in **2 s** wieder da (Cache aktuell, kein Neuaufbau), Build `Fire / Ice T-176` im Auswahlfeld korrekt zurueckgelesen.

**Zweitinstanz:** Wahrend die erste Instanz lief, ein zweiter Start versucht — zwei zusaetzliche Prozesse erschienen kurz und beendeten sich innerhalb von ~10 s von selbst, ohne zweites Fenster. Einzelinstanz-Sperre (`nrplanner/singleinstance.py`) funktioniert.

### 2. Update-Weg v1.7.1 → 1.9.0 — bestanden, mit einem Bookkeeping-Fund

`gh release download v1.7.1` in eigenes Downloadverzeichnis (58.827.005 B, passt zur ROLLOUT.md-Angabe), in **eigene** isolierte Umgebung (`DankYeeterT176Update`) kopiert und gestartet.

**Erstaufbau v1.7.1:** Start 12:35:01, `nightreign_data.json` fertig 12:37:47 → **166 s**; der Fortschrittsdialog selbst („Setting up Nightreign Helper … takes about a minute", inkl. Icon-Verifikation und DLC-Illustrationen) schloss erst um 12:39:44 → **283 s (4:43) bis zum nutzbaren Hauptfenster**, nahe der oberen Grenze von QA-198s Spanne. Fenstertitel danach: `Nightreign Helper 1.7.1`.

**Drei Builds angelegt**, je unter einer anderen Chalice, mit den drei kritischen Namensfaellen:
- `Fire / Ice` (Slash)
- `Fire | Ice` (Pipe)
- `FIRE ICE MAX` (Grossbuchstaben)

**Registry vor dem Update** (`HKCU\Software\DankYeeterT176Update\NightreignHelper\builds\1`) zeigt genau das erwartete alte Verhalten: `Fire | Ice` und `FIRE ICE MAX` als flache Werte, aber `Fire / Ice` wurde vom `/` in der Registry **als Pfadtrenner interpretiert** — es entstand ein **Unterschluessel** `builds\1\Fire ` (mit Leerzeichen) mit dem Wert `Ice` darin. Das ist exakt der Fehlerfall, den QA-003/QA-046 und die Schema-3-Migration adressieren, hier live reproduziert.

**Update ausgefuehrt:** EXE in der Update-Umgebung durch `dist/NightreignHelper.exe` (1.9.0, Hash geprueft identisch) ersetzt, gestartet. Dialog „Refreshing your game data / Re-reading your installation so the numbers are up to date." erschien (anderer Text als beim Erststart, kein Zeitversprechen darin) und lief von 12:42:34 bis ca. 12:45:26 → **~172 s** fuer den erzwungenen Neuaufbau (EXTRACT_VERSION-Sprung ueber 1.8.0 hinweg).

**Migration bestaetigt:** `__schema = 3`, alle drei Werte unter prozent-kodierten Schluesseln vorhanden (`Fire / Ice`, `Fire | Ice`, `FIRE ICE MAX` — Sonderzeichen korrekt dekodiert). Ueber UI Automation den Dropdown der gespeicherten Builds geoeffnet: **alle drei Namen erscheinen korrekt und unverstuemmelt** in der Liste (`Fire / Ice`, `FIRE ICE MAX`, `Fire | Ice`, neben den Standardeintraegen). Kein Datenverlust.

**Ein Fund dabei, keine Sperre:** Der Registry-Wert `__order` fuehrt nach der Migration nur zwei der drei Schluessel (`Fire / Ice` und `FIRE ICE MAX`), `Fire | Ice` fehlt in dieser Reihenfolge-Liste — obwohl der Wert selbst da ist und in der Oberflaeche sichtbar/waehlbar bleibt (die Anwendung baut die angezeigte Liste offenbar nicht ausschliesslich aus `__order`). Funktional kein Verlust, aber ein Hinweis, dass die Migration den Ordnungs-String nicht vollstaendig nachfuehrt. Siehe „An den developer".

**Leerer Alt-Schluessel bleibt liegen:** `builds\1\Fire ` (der durch das `/`-Splitting von v1.7.1 entstandene Unterschluessel) existiert nach der Migration weiterhin, jetzt leer. Laut Moduldokumentation in `gamepath.py`/der Migrationslogik ist „nie `remove` aufrufen" **Absicht**, nicht Versehen — genannt zur Vollstaendigkeit, kein Fehlverhalten.

**Neustart nach Update:** Fenster in ~15 s wieder da (Cache jetzt aktuell), gespeicherter Build weiterhin korrekt geladen.

**Zweitinstanz nach Update:** wie oben — zusaetzliche Prozesse beendeten sich selbst, kein zweites Fenster.

**`paths/game`/`paths/save` auch hier nicht geschrieben** — dieselbe automatische Erkennung griff waehrend des gesamten Update-Laufs, kein A15-Dialog.

### 3. Aufraeumen — durchgefuehrt

- `reg delete HKCU\Software\DankYeeterT176Fresh /f` und `…T176Update /f` — beide bestaetigt geloescht (Nachkontrolle: Schluessel nicht mehr auffindbar).
- Scratchpad-Verzeichnis `…\scratchpad\T-176\` (213 MB: zwei EXE-Kopien, zwei isolierte LOCALAPPDATA/APPDATA-Baeume inkl. der Test-Verknuepfung, das heruntergeladene v1.7.1) vollstaendig geloescht.
- Repository unveraendert bis auf diesen Bericht (`git status` vor und nach identisch: nur die zwei bereits vor meinem Lauf veraenderten Dateien `.github/workflows/release.yml` und `docs/release/RELEASE_TEXT.md`, **nicht von mir** — ich habe sie nicht angefasst, nicht committet, nicht gepusht).
- **Nichts bleibt liegen**, das dem `power-user` seine Ausgangslage verderben koennte: kein gemerkter Pfad, kein Datenabzug, keine Verknuepfung — alles lag ausschliesslich im geloeschten Scratchpad, die echten Nutzerpfade wurden nie berührt.

## Artefakt

`C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` — 59.062.648 B, SHA-256 `a2180d5db3a2b1b1aaf88028c6e7a1429087596e58ec3757469fd234e1366ef3`, Version 1.9.0, Commit `0716911` (laut Auftrag; von mir nicht neu gebaut, nur geprueft). Reproduzierbarkeit war nicht Gegenstand dieses Laufs (siehe T-106/ROLLOUT.md: dort bereits als **nicht bit-identisch** dokumentiert). Dazu `NightreignHelper-notices.zip`, 46.480 B, SHA-256 `51a0b7cb8ed3aa1eced1c2e1868380ecdf778950eb3881329ee46ec25f334419`.

## Blocker

Keiner. 1.9.0 installiert und laeuft auf einem System ohne Entwicklungswerkzeuge (im Rahmen der erreichten Isolierung), der Update-Weg von v1.7.1 erhaelt die Nutzerdaten.

## Risiken (verhindern kein Release, treffen aber Nutzer)

- **Zeitangabe „about a minute" ist auf dieser Maschine falsch.** Gemessen 163 s (Erstinstallation 1.9.0), 283 s (Erstinstallation v1.7.1), 172 s (erzwungener Neuaufbau nach Update). Alle drei liegen zwischen dem Zweieinhalb- und Vierfachen der genannten Zeit. QA-198s Spanne (107 s – 5 min) bleibt damit **bestaetigt aktuell**, die UI-Formulierung nicht.
- **SmartScreen/Virenscanner** (aus ROLLOUT.md T-106 bereits benannt, hier nicht erneut geprueft, da diese Maschine kein frischer SmartScreen-Ruf ist — der Rechner kennt die Datei schon aus fruaheren Bauten).
- **`__order` fuehrt nicht alle migrierten Builds** — siehe Fund oben, kein Datenverlust, aber ein Hinweis auf unvollstaendige Nachfuehrung.

## Ungeprüft

- **A15-Auswahldialog selbst (der zweite Teil, den der `power-user` als A11/A15-Nachweis fuehren soll):** Auf dieser Maschine findet die Automatik das Spiel ueber Steams eigene Registry+`libraryfolders.vdf` zuverlaessig, ganz ohne den entfernten Laufwerks-Rueckfall. Der Dialog erschien in keinem der beiden Laeufe. **Der Auftrag ging davon aus, dass genau das hier der Normalfall waere — das war empirisch nicht der Fall.** Damit bleibt A15s Dialogpfad auf dieser Maschine vollstaendig ungetestet; der `power-user` braucht entweder eine Umgebung ohne registrierte Steam-Installation (kein `HKCU\Software\Valve\Steam`-Schluessel bzw. das Spiel nicht in `libraryfolders.vdf`) oder muss den Ordner manuell entfernen/verstecken, um den Dialog ueberhaupt zu sehen. Ich habe die reale Steam-Registrierung **nicht** angefasst, um das zu erzwingen — das waere ein Eingriff in echte Systemkonfiguration ausserhalb meines Auftrags und haette das reale Konto veraendert.
- **Downgrade/Deinstallation:** nicht Teil dieses Auftrags (clean-room deckt nur Erstinstallation + Update ab).
- **Reproduzierbarkeit des Baus:** nicht erneut geprueft, siehe ROLLOUT.md.
- **Echte Fremdmaschine / anderes Konto / Virenscanner-Fehlalarm:** wie in jedem bisherigen Lauf nicht verfuegbar.
- **UPX-Zustand des Artefakts:** nicht erneut geprueft, das war Sache des `build`-Laufs.

## An den `developer`

1. **`__order`-Eintrag nach der Schema-3-Migration unvollstaendig:** Nach dem Update ueber v1.7.1 fehlte in `HKCU\...\builds\1\__order` einer von drei migrierten Schluesseln (`Fire | Ice`), obwohl der Wert selbst korrekt vorhanden und in der UI sichtbar/waehlbar war. Kein Datenverlust in diesem Test, aber die Ordnungsliste ist nicht vollstaendig nachgefuehrt — bitte pruefen, ob `_migrate_keys` (`chalices.py`) `__order` in jedem Fall aktualisiert.
2. **Zur Kenntnis, kein Fehler:** Der leere Alt-Schluessel `builds\1\Fire ` (durch `/`-Splitting unter v1.7.1 entstanden) bleibt nach der Migration bestehen — laut Quelltextkommentar Absicht („nie `remove`"), hiermit am echten Migrationsfall bestaetigt.
3. **Zur Kenntnis:** Fenstertitel unterscheiden sich zwischen Versionen (`NightreignHelper` ohne Leerzeichen waehrend des v1.7.1-Fortschrittsdialogs, `Nightreign Helper 1.7.1`/`1.9.0` im Hauptfenster) — kein Fehlverhalten, nur als Beobachtung, falls das fuer Fenster-Erkennung (Automatisierung, Screenreader) relevant ist.

## An den `power-user`

Ausgangspunkt: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` (1.9.0, Hash oben) plus `dist\NightreignHelper-notices.zip`. Installation ausschliesslich nach README (`## Install`): EXE in ein leeres Verzeichnis, starten, fertig — kein Installer, keine Adminrechte.

**Deine Aufgabe ist der A15-Dialog, den ich nicht sehen konnte.** Auf meiner Maschine findet die Automatik das Spiel ueber die normale Steam-Registrierung, ganz ohne Dialog. Damit dein Lauf den Auswahldialog ueberhaupt zeigt, brauchst du entweder eine Umgebung, in der Steam nicht registriert ist bzw. das Spiel nicht in `libraryfolders.vdf` steht, oder du musst selbst dafuer sorgen, dass die Automatik ins Leere greift — **wie, ist bewusst nicht meine Entscheidung**, das ist genau der Ablauf, den du unverfaelscht als Mensch erleben sollst. Ich habe ihn nicht vorweggenommen und keine Pfade/Verknuepfungen hinterlassen.

Vorwarnung aus meinem Lauf: **SmartScreen** beim ersten Start einer unsignierten EXE ist wahrscheinlich (auf meiner Maschine nicht erneut ausgeloest, weil die Datei bereits bekannt war — bei dir vermutlich frisch). **Erstaufbau dauert laut meiner Messung eher 2,5–5 Minuten als „about a minute"** — nicht abbrechen, das Fenster bleibt bedienbar waehrend im Hintergrund weitergebaut wird.

## An den `director`

- **Empfehlung: freigeben mit einer benannten Einschraenkung** — die Einschraenkung betrifft nicht die Lauffaehigkeit (die ist bestanden), sondern die Vollstaendigkeit der Pruefung: **A15s Dialogpfad ist bislang durch niemanden am gebauten Artefakt gesehen worden**, weder von mir noch bisher vom `power-user` (der erst jetzt startet). Ohne diesen Nachweis ist A11/A15 laut `docs/state.md` weiterhin „offen — braucht `power-user`".
- **Korrektur der Auftragsannahme:** Die im Auftrag formulierte Erwartung „das ist genau der Fall, den du hier siehst" (A15-Dialog auf dieser Maschine) hat sich **nicht bestaetigt** — die Automatik findet das Spiel hier weiterhin zuverlaessig ueber Steams eigene Registry/VDF-Mechanik, unabhaengig vom entfernten Laufwerks-Rueckfall. Das ist eine gute Nachricht fuer die Mehrheit der Steam-Nutzer (Standardfaelle funktionieren ohne Dialog), bedeutet aber, dass der Dialog-Pfad eine gezielt praeparierte Umgebung braucht, um getestet zu werden.
- **Update-Weg v1.7.1 → 1.9.0 bestanden**, inklusive des kritischen Falls (Build-Name mit `/`, der unter v1.7.1 die Registry-Struktur aufspaltet). Kein Datenverlust.
- **Keine fehlenden `.gitignore`-Eintraege** — ich habe nichts ins Repository geschrieben.
- **Kein Tag-Vorschlag** — das gehoert in den `notes`-Lauf nach dem `power-user`, nicht in diesen.
- **Offene Entscheidung fuer dich/den Nutzer:** ob der leichte `__order`-Bookkeeping-Fund vor dem naechsten Release noch behoben werden soll oder als bekannte Kleinigkeit mitgeht — er verhindert nichts, aber er ist ein echter Abweichungsfund gegen die Spezifikation der Migration.
