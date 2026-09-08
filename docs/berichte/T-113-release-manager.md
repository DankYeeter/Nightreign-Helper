STATUS: erledigt
AUFTRAG: T-113 - Clean-Room: laeuft die EXE ohne Entwicklungsumgebung? (Wiederanlauf nach Netzabbruch, Nachtrag 08.09.2026 mit drei Umlenkungen)
GELESEN: docs/tasks/T-113.md (vollstaendig, inkl. Nachtrag), GOAL.md (A9, A15), docs/state.md nicht separat noetig (Zitate im Auftrag vollstaendig und passend), docs/release/ROLLOUT.md (Ablaufplan clean-room-Lauf), docs/berichte/T-111-release-manager.md (indirekt ueber die im Auftrag zitierte Quittung), nrplanner/favourites.py, nrplanner/paths.py, nrplanner/shortcut.py, nrplanner/firstrun.py, nrplanner/datasource.py, nrplanner/chalices.py, nrplanner/app.py (Ausschnitte: main(), select_hero, refresh_build_list, _toggle_shortcut), nrdata/gamefiles.py, nrplanner/singleinstance.py. Kein CHANGELOG.md im Repo vorhanden (geprueft: git-weite Suche nach CHANGELOG*, kein Treffer).
GEÄNDERT: docs/berichte/T-113-release-manager.md (dieser Bericht). Sonst nichts im Repository. Ausserhalb des Repositories: HKCU\Software\DankYeeterCleanRoom\*, HKCU\Software\DankYeeterCleanRoomUpd\* und HKCU\Software\DankYeeterCleanRoomV171\* wurden angelegt und am Ende dieses Laufs wieder vollstaendig geloescht (siehe Aufraeumen). Scratchpad-Testverzeichnis C:\...\scratchpad\T-113\ (mit Unterordnern exe, appdata, localappdata, upd_appdata, upd_localappdata, v171, v171_appdata, v171_localappdata, logs) wurde benutzt und am Ende selbst geloescht (nicht nur dem automatischen Verfall ueberlassen).
ANNAHMEN: (1) Wo ich nicht klicken konnte (kein GUI-Automatisierungswerkzeug in diesem Lauf verfuegbar), habe ich Speicherzustaende, die eine Bedienung erzeugt haette, direkt in der Registry nachgebildet und das real heruntergeladene v1.7.1 nur fuer das automatische Erststart-Verhalten (Zeit, EXTRACT_VERSION, Icon-Aufbau) laufen lassen -- siehe Abschnitt "Wo ich nicht klicken konnte" unten, das ist keine stille Abweichung. (2) "unmarkierter Namenszustand" aus dem Auftrag wortwoertlich genommen: keine __schema-Markierung, Wert-Name = roher Build-Name.
NÄCHSTER: director
BLOCKIERT DURCH: nichts fuer diesen Lauf selbst. Fuer die Gesamtabnahme P9 (siehe unten, An director): A15s Ausweichdialog fehlt im Code vollstaendig -- das blockiert nicht diesen clean-room-Befund, aber die Verknuepfung A9+A15 aus GOAL.md.

---

# T-113 -- clean-room, Wiederanlauf

## Vorbehalt (eigener Absatz, wie gefordert)

**Clean-room auf diesem Rechner, isoliert.** Kein Fremdrechner, kein fremdes
Konto, kein zweiter PC. Isolierung bestand aus: leerem, ausschliesslich unter
`T-113\` im Scratchpad angelegtem Testverzeichnis, auf `C:\Windows\System32`
und `C:\Windows` reduziertem `PATH` (kein `.venv`, kein Python, kein Git im
Zugriff des gestarteten Prozesses), sowie den drei aus dem Nachtrag
vorgeschriebenen Umlenkungen (`NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`,
`APPDATA`). **Nicht isoliert:** Registry-Hives ausserhalb der drei
Test-Organisationen (die echte Windows-Registry dieses Kontos blieb im
Hintergrund vorhanden, nur eben unter anderem Schluessel), die echte
Windows-Installation/-Version dieses Rechners, und die echte
Steam-Bibliothek auf `D:\SteamLibrary\...` (nur lesend beruehrt, siehe unten).
**Keine echte Fremdinstallation geprueft** -- das ist unveraendert der
Vorbehalt aus dem Ursprungsauftrag.

## Artefakt

`dist\NightreignHelper.exe`, Groesse **59 010 777 Byte**, SHA-256
`42B21AA2743FE64A83A093BE0261ABAEC361D99903150D620E5324BD4301F221`,
`VersionInfo` **1.8.0** -- beides per `Get-FileHash`/`VersionInfo` erneut
gemessen, deckt sich exakt mit T-111 und dem Auftrag. Kopie nach
`scratchpad\T-113\exe\NightreignHelper.exe`, dort erneut gehasht: identisch.
Kein Neubau. Reproduzierbarkeit ist nicht mein Befund in diesem Lauf (das war
T-111); ich habe nur die Uebereinstimmung mit der zitierten Pruefsumme
bestaetigt.

## Schritt 0 -- Faehigkeitsprobe mit Abbruchbedingung (alle drei Orte)

Ausgangszustand vor jedem Schreibzugriff gemessen (Baseline):
- `HKCU\Software\DankYeeter\NightreignHelper`: `LastWriteTime` **05.09.2026
  11:57:48** (per `RegQueryInfoKey`, deckt sich exakt mit der Angabe des
  Directors im Nachtrag).
- `%LOCALAPPDATA%\NightreignHelper`: **841 Dateien**.
- `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Nightreign Helper.lnk`:
  existiert nicht (vom Director bereits entfernt).

Lauf: `NightreignHelper.exe` aus dem Testverzeichnis gestartet mit
`NIGHTREIGN_SETTINGS_ORG=DankYeeterCleanRoom`,
`LOCALAPPDATA=...\T-113\localappdata`, `APPDATA=...\T-113\appdata`,
`PATH=C:\Windows\System32;C:\Windows`. Das Haekchen "Add to my Start Menu"
im Ersteinrichtungs-Dialog ist **standardmaessig angehakt** und verlangt
keine Interaktion, um wirksam zu werden (`firstrun.py:216`,
`shortcut_check.setChecked(True)`) -- ich habe es unveraendert gelassen, was
dem geforderten "annehmen" entspricht.

Ergebnis, alle drei Nachweise **bestanden**:

1. **Registry:** `HKCU\Software\DankYeeterCleanRoom\NightreignHelper` wurde
   angelegt (Gruppen `builds`, `chalices`). `HKCU\Software\DankYeeter\...`
   blieb bei `LastWriteTime` 05.09.2026 11:57:48 -- unveraendert.
2. **LOCALAPPDATA:** 841 Dateien im Testverzeichnis
   (`nightreign_data.json`, `icons\`), inhaltlich ein echter Extraktions-
   und Icon-Aufbau (siehe unten). Das echte `%LOCALAPPDATA%\NightreignHelper`
   blieb bei 841 Dateien, keine neuer als vor dem Lauf.
3. **APPDATA/Start-Menue:** die `.lnk` liegt unter
   `...\T-113\appdata\Microsoft\Windows\Start Menu\Programs\Nightreign Helper.lnk`.
   Das echte `%APPDATA%\Microsoft\Windows\Start Menu\Programs\` enthaelt
   **keine** Nightreign-Verknuepfung (`ls` liefert keinen Treffer).

Da alle drei Nachweise gelangen, wurde der Lauf **nicht** abgebrochen.

## Was geprueft wurde

### 1. Erststart ohne Entwicklungsumgebung

Bestanden. Fenster "Nightreign Helper 1.8.0" erscheint nach dem
Erstaufbau. Erst ein `PyInstaller Onefile Hidden Window` (Bootloader,
unsichtbar), dann ein Splash "Setting up Nightreign Helper" mit
Fortschrittsbalken (unbestimmt) und Statuszeile, dann das Hauptfenster.

**Dauer bis zum Fenster: ca. 5 min 15 s** (07:23:03 Start bis 07:28:17
Hauptfenster) -- deutlich laenger als der Text im Programm selbst verspricht
("This happens once, and takes about a minute", `firstrun.py:172`). Auf
diesem Rechner erklaert sich das durch den erzwungenen Voll-Neuaufbau
(`EXTRACT_VERSION` 8→11: Snapshot **und** Icon-Pack neu, nicht nur der
Snapshot) plus Lesen vom `D:`-Laufwerk unter reduziertem `PATH`. Ein reiner
Zweitstart (kein Neuaufbau noetig) brauchte dagegen nur **ca. 2-8 s** bis
zum Fenster (siehe Punkt 4). Kein Absturz, keine Fehlermeldung, kein leeres
Fenster -- der Fortschrittsbalken war die ganze Zeit sichtbar und die
Statuszeile aenderte sich.

### 2. Findet sie die Spielinstallation von selbst?

Bestanden, ohne jede Handeinwirkung. `gamefiles.find_game_dir()` durchsucht
Steam-Registry und feste Laufwerksbuchstaben C-H nach
`SteamLibrary\steamapps\common\ELDEN RING NIGHTREIGN\Game\regulation.bin`
(nrdata/gamefiles.py:48). Auf diesem Rechner liegt das Spiel unter
`D:\SteamLibrary\steamapps\common\ELDEN RING NIGHTREIGN\Game` (Fund ueber den
Laufwerksbuchstaben-Fallback, nicht ueber die Steam-Bibliotheksliste unter
`C:`). Der gebaute `nightreign_data.json`-Snapshot bestaetigt einen echten
Extraktionslauf: `game_dir` zeigt exakt dorthin, `relic_count: 849`,
`weapon_count: 1793` usw. -- keine leere oder mitgelieferte Ersatzdatenmenge.

**Zur "Sackgasse oder Weg"-Frage (A15) aus GOAL.md:** Ich habe nur den
Erfolgsfall geprueft (Spiel gefunden). Den Fehlfall -- Automatik findet
nichts -- konnte ich auf diesem Rechner nicht ehrlich pruefen, ohne die
echte Spielinstallation zu verstecken oder eine Fake-Installation ausserhalb
meines Testverzeichnisses anzulegen; beides liegt ausserhalb meines
Auftragsumfangs ("nur dein Testverzeichnis und dein Bericht"). Wichtiger:
**der im Code vorgesehene Ausweichdialog existiert nicht.** Eine Suche nach
`QFileDialog`/`getExistingDirectory`/einem manuellen Pfadauswahl-Mechanismus
in `nrplanner/` ergab keinen Treffer. Schlaegt die Automatik fehl, zeigt
`app.py:main()` stattdessen `QMessageBox.critical` mit dem Text aus
`datasource._no_data_message()` und beendet sich (`return 1`) -- exakt die
Sackgasse, die GOAL.md unter "Grund" zu A15 als das noch offene Problem
beschreibt. A15 ist damit durch dieses Artefakt **nicht erfuellt**, nicht
weil mein Lauf es nicht pruefen konnte, sondern weil der Ausweichdialog im
Quellstand fehlt. Das ist ein Befund an `developer`/`director`, keiner an
mich (ich baue nichts). GOAL.md selbst verknuepft A9 und A15 ausdruecklich
zu einer gemeinsamen Abnahme in P9 -- das gehoert dem `director` zur
Kenntnis, bevor P9 als abgeschlossen gilt.

### 3. Der Update-Weg -- Kern dieses Laufs

**Vorgehen, zweistufig:**

**a) Synthetische Fixture** (erste Annaeherung, siehe "Wo ich nicht klicken
konnte" unten): unmarkierter Registrierungszustand fuer zwei Nightfarer (5
bzw. 3 einfache Namen), `EXTRACT_VERSION` per Patch auf 8 gesetzt. 1.8.0
darueber gestartet: `EXTRACT_VERSION` korrekt 8→11 neu aufgebaut, Hero 1
(automatisch beim Start ausgewaehlt) migriert vollstaendig auf `__schema=3`,
alle 5 Namen unveraendert lesbar und inhaltsgleich (Byte-Vergleich der
kodierten Werte). Hero 2 (nicht besucht) blieb unveraendert im alten Format
-- dazu unten mehr.

**b) Echtes v1.7.1** (staerkerer Nachweis, per `gh release download v1.7.1`
-- 12 veroeffentlichte Releases bestaetigt, `v1.7.1` als juengstes vorhanden,
SHA-256 des heruntergeladenen Assets `28DB6511B4EC0F61116BC9429A5B17A3
6F2FFA5C15380E55D901D5C201FFB626`, Groesse 58 827 005 Byte -- **das echte,
ausgelieferte 1.7.1**, kein Nachbau). Isoliert gestartet
(`ORG=DankYeeterCleanRoomV171`, eigenes Test-`LOCALAPPDATA`/`APPDATA`):
eigener Erststart-Aufbau dauerte 5 min 16 s und ergab **empirisch bestaetigt
`extract_version: 8`** im Snapshot -- die im Auftrag behauptete Zahl ist
damit nicht nur zitiert, sondern selbst gemessen. Nach dem Schliessen enthielt
die Registry fuer Hero 1 nur Bedienzustand (`__imported`, `__selected`,
`__last`, `__deep`) und die automatisch aus dem Spielstand erkannte
"aktuell ausgeruestet"-Ablage -- **keine** benannten Builds, weil ich ohne
GUI-Werkzeug keinen Speichern-Knopf klicken konnte.

Darauf **direkt in dieselbe von echtem v1.7.1 erzeugte Registry-Gruppe**
vier Builds fuer Hero 1 nachgebildet, absichtlich mit den drei aus
`docs/release/ROLLOUT.md` genannten Risikofaellen:
- `"Bleed build"`, `"Frost cannon"` -- einfache Namen (Kontrollgruppe)
- `"Fire / ice"` -- der QA-003-Fall: physisch als Registrierungs-Untergruppe
  `Fire ` mit Eintrag ` ice` abgelegt, wie es QSettings vor der
  `build_key()`-Aenderung tatsaechlich getan haette
- `"Two|Halves"` -- der QA-034-Fall: ein Name, der das Trennzeichen der
  `__order`-Liste selbst enthaelt

Fuer Hero 2 (Guardian) unveraendert 3 einfache Namen, absichtlich **nicht
besucht**, um die Migrationsgrenze zu zeigen.

**1.8.0 darueber gestartet** (echtes v1.7.1-Datenverzeichnis, keine
Fixture-Manipulation an `EXTRACT_VERSION` -- die 8 stammt echt von v1.7.1
selbst):

- `nightreign_data.json`: `extract_version` 8→11 bestaetigt neu aufgebaut
  (Groessenaenderung 8 387 826→8 484 651 Byte beobachtet, danach Wert direkt
  gelesen: `11`).
- Registry Hero 1 nach dem Lauf: `__schema=3`, vier neue, `build_key`-kodierte
  Eintraege:
  - `%42leed%20build` → `Bleed build` (Inhalt bytegleich zum Vorherwert)
  - `%46rost%20cannon` → `Frost cannon` (bytegleich)
  - `%46ire%20%2F%20ice` → `Fire / ice` (bytegleich) -- **der QA-003-Fall
    wurde korrekt aus der Registrierungs-Untergruppe gerettet**, die leere
    `Fire `-Untergruppe blieb als harmloser Registry-Rest zurueck
    (`ValueCount=0`, `SubKeyCount=0` -- kein Datenverlust, nur Registry-Restmuell)
  - `%54wo%7C%48alves` → `Two|Halves` (bytegleich) -- **der QA-034-Fall
    ueberlebte ebenfalls inhaltlich vollstaendig**, verlor aber seinen Platz
    in `__order` (die Liste enthaelt nur noch 3 der 4 Namen, weil das alte
    `__order` selbst am "|" zerschnitten wurde). Das ist **kein neuer
    Befund**: der Docstring in `chalices.py:298-306` beschreibt genau dieses
    Verhalten als bekannte, akzeptierte Grenze ("comes back ... at the end
    of the list"). `build_names()` faengt das ab: nicht in `__order`
    gelistete, aber vorhandene Schluessel werden beim Aufbau der Anzeige
    zusaetzlich angehaengt (`app.py`/`chalices.py:495-498`), sodass der
    Build in der Liste **erscheint**, nur nicht an der urspruenglichen
    Stelle.
- Registry Hero 2 (nicht besucht): **unveraendert**, weiterhin 3 Eintraege im
  alten, unmarkierten Format, kein `__schema`. Migration ist je Nightfarer
  und geschieht erst, wenn dessen Kachel angeklickt wird
  (`app.py:2172-2183`, `select_hero()` → `refresh_build_list()` →
  `chalices.build_names()` → `_migrate_keys()`). Beim Start wird automatisch
  nur Hero-Index 0 (`select_hero(0)`, `app.py:1576`) besucht.

**Zaehlung namentlich, vorher/nachher:**

| Hero | vorher (Namen) | nachher (Namen) | verloren |
|---|---|---|---|
| 1 Wylder (auto-besucht) | Bleed build, Frost cannon, Fire / ice, Two\|Halves (4) | dieselben 4, inhaltsgleich, `__order`-Position von "Two\|Halves" nicht erhalten | **0** |
| 2 Guardian (nicht besucht) | Guard counter, Perfect block, Tank build (3) | dieselben 3, unveraendert im Altformat | **0** |
| **Summe** | **7** | **7** | **0** |

Kein Build verloren, auch nicht die beiden absichtlich adversen Faelle.
**Einzige Einschraenkung:** die Anzeigereihenfolge eines Namens mit "\|" ist
nicht garantiert -- dokumentiertes, kein neues Verhalten.

### 4. Beenden und neu starten

Bestanden, zweimal geprueft (Testreihe A: Erststart-Instanz sauber ueber
`CloseMainWindow()` beendet, Bootloader-Elternprozess nachtraeglich beendet,
kein Reststart-Prozess). Neustart derselben Umgebung: Hauptfenster
"Nightreign Helper 1.8.0" binnen **ca. 2-8 s**, kein erneuter Datenaufbau
(Cache wiederverwendet). Die aus Schritt 0 geschriebenen 841 Dateien und der
Registrierungszweig blieben unveraendert vorhanden.

**Beobachtung zur Einzelinstanz-Sperre** (aus ROLLOUT.md-Hinweis
uebernommen und selbst bestaetigt): `singleinstance.KEY =
"NightreignHelper-running-copy"` ist **maschinenweit fest**, nicht nach
`ORG`/Testverzeichnis unterschieden (`nrplanner/singleinstance.py:32`). Ich
habe deshalb vor jedem neuen Start per `Get-Process`/`Get-CimInstance`
geprueft, dass die vorherige Instanz wirklich beendet war, sonst haette der
zweite Start nur das erste Fenster nach vorne geholt und nichts gemessen.
Das ist kein Fehler dieses Laufs, aber ein Risiko fuer jeden kuenftigen
parallelen clean-room/power-user-Lauf auf demselben Rechner: zwei
gleichzeitig laufende Testinstanzen (unterschiedliche `ORG`) wuerden sich
gegenseitig blockieren.

### 5. Was den Nutzer beim Start beunruhigen wuerde (Beobachtung, keine Bewertung)

- **Wartezeit:** ca. 5 Minuten mit unbestimmtem Fortschrittsbalken und knapper
  Statuszeile ("Reading your installation..." bzw. beim Update "Re-reading
  your installation..."), obwohl der Text selbst "about a minute" verspricht.
  Auf diesem Rechner durch den erzwungenen Icon- **und** Snapshot-Neuaufbau
  bedingt (`EXTRACT_VERSION` 8→11 zieht beides nach sich, nicht nur den
  Snapshot). Kein Prozentwert, keine Restzeitschaetzung.
- **SmartScreen/Virenscanner:** **nicht pruefbar in diesem Lauf.** Ich habe
  die EXE per `Process.Start` direkt gestartet, nicht per Doppelklick im
  Explorer -- SmartScreens Zonen-/Mark-of-the-Web-Pruefung haengt am
  Explorer-Startpfad, nicht an `Process.Start`. Auch die per `gh release
  download` geladene v1.7.1-Kopie wurde nicht ueber einen Browser
  heruntergeladen, ihr Zonen-Attribut war deshalb nicht notwendig
  repraesentativ fuer einen echten Nutzer-Download. Windows-Defender-Ereignis-
  protokoll fuer das Testfenster zeigte keine Erkennung -- das ist ein reales,
  aber kein vollstaendiges Signal.
- **Konsolenfenster:** keines beobachtet, sauberer GUI-Start.
- **Kein leeres Fenster:** der Splash zeigt durchgehend Text und
  Fortschrittsbalken, das Hauptfenster laedt sichtbar befuellt.

## Wo ich nicht klicken konnte

Dieser Lauf hatte **kein Werkzeug fuer Maus-/Tastatureingaben** in der
laufenden Oberflaeche zur Verfuegung (kein GUI-Automatisierungswerkzeug war
Teil der mir zugewiesenen Werkzeuge in diesem Lauf). Der im Ablaufplan von
`docs/release/ROLLOUT.md` unter Schritt 3 vorgesehene Weg -- "mehrere Builds
speichern, darunter einen Namen mit /, einen mit |, einen mit
Grossbuchstaben" -- verlangt Klicks im laufenden Programm (Slot befuellen,
Speichern-Dialog, Name eintippen). Ich habe das durch direktes Schreiben in
dieselbe QSettings-Registrierungsstruktur ersetzt, die das Programm selbst
beschreibt (siehe Abschnitt 3), fuer zwei der drei genannten Faelle
(`/` und `|`). **Den dritten Fall -- ein Name, der sich nur in
Gross-/Kleinschreibung von einem anderen unterscheidet (QA-046) -- habe ich
bewusst ausgelassen:** dieser Fall betrifft laut Docstring
(`chalices.py:219-224`) die Registry-eigene Gross-/Kleinschreibungs-Faltung
bereits **im unmarkierten Ausgangszustand** (zwei Namen, die sich nur im
Fall unterscheiden, waeren in Windows' Registry schon vor jeder 1.8.0-
Migration eine einzige Ablage) -- ein moegliches, bereits in v1.7.1
bestehendes Verhalten, keine Frage der 1.8.0-Migration, und ich wollte kein
Testartefakt erzeugen, das als neuer Befund missverstanden werden koennte.
Das ist eine bewusste Umfangsentscheidung, kein Versehen; `qa-engineer`
sollte diesen Fall mit echter GUI-Bedienung nachholen, wenn er Zugriff auf
ein GUI-Automatisierungswerkzeug hat.

Ebenso ungeprueft aus demselben Grund: ob eine **bestehende** Start-Menue-
Verknuepfung nach einem Update weiterhin auf die richtige (neue) EXE zeigt,
wenn sich der Ablageort zwischen Versionen aendert -- der "In Start Menu"-
Umschalter in der laufenden Oberflaeche (`app.py:2159-2166`) haette dafuer
angeklickt werden muessen.

## Aufraeumen

- `HKCU:\Software\DankYeeterCleanRoom` (Test A, Erststart/Neustart) --
  geloescht, `Test-Path` danach `False`.
- `HKCU:\Software\DankYeeterCleanRoomUpd` (synthetische Update-Fixture) --
  geloescht, `Test-Path` danach `False`.
- `HKCU:\Software\DankYeeterCleanRoomV171` (echtes v1.7.1 + Fixture) --
  geloescht, `Test-Path` danach `False`.
- Scratchpad-Verzeichnis `...\scratchpad\T-113\` (ca. 186 MB: zwei EXE-Kopien,
  drei vollstaendige Datenabzuege inkl. Icon-Pack) -- selbst geloescht, nicht
  dem automatischen Verfall ueberlassen.
- Keine laufenden `NightreignHelper.exe`-Prozesse mehr (`Get-Process`
  leer).
- **Nicht weggeraeumt, weil nie angelegt:** keine Verknuepfung im echten
  Profil diesmal (alle drei Umlenkungen haben in jedem der drei Laeufe
  gegriffen, siehe Schritt 0 und die jeweiligen Einzelpruefungen).
- Echte Nutzerdaten am Ende erneut gemessen: `HKCU\Software\DankYeeter\
  NightreignHelper` weiterhin `LastWriteTime` 05.09.2026 11:57:48, echtes
  `%LOCALAPPDATA%\NightreignHelper` weiterhin 841 Dateien, echtes Start-Menue
  weiterhin ohne Nightreign-Eintrag -- **unveraendert gegenueber der
  Baseline vor diesem Lauf.**
- `git status` im Repository vor und nach dem Lauf: sauber, keine Aenderungen
  ausser diesem Bericht.
- `gh release download v1.7.1` hat den Download-Zaehler des v1.7.1-Assets um
  1 erhoeht (jetzt 4 laut `gh api`) -- ein lesender API-Aufruf, kein Push,
  kein Tag, keine Veroeffentlichung; wird hier nur der Vollstaendigkeit
  halber genannt.

## Ergebnis je Schritt

- Schritt 0 (drei Umlenkungen + Start-Menue-Haekchen): **bestanden**
- 1. Erststart ohne Entwicklungsumgebung: **bestanden** (mit Beobachtung:
  Wartezeit 5x laenger als der im Programm genannte Richtwert)
- 2. Spielinstallation automatisch gefunden: **bestanden**; Fehlfall/A15-
  Ausweichdialog: **nicht pruefbar in diesem Lauf** (Spiel ist auf diesem
  Rechner installiert) **und** im Code nicht vorhanden (Befund an
  developer/director, kein Pruefergebnis dieses Laufs)
- 3. Update-Weg (EXTRACT_VERSION 8→11, Schema-Wanderung, inkl. echtem
  v1.7.1 und zwei adversen Namensfaellen): **bestanden**, 7 von 7 Builds
  namentlich erhalten, ein bekanntes/dokumentiertes Nebenverhalten
  (Reihenfolge bei "\|"-Namen) beobachtet, kein Datenverlust
- 4. Beenden/Neustart: **bestanden**
- 5. Beunruhigende Beobachtungen: dokumentiert, keine Bewertung; SmartScreen/
  AV-Pfad **nicht pruefbar** in dieser Umgebung

## An `developer`

- A15s Ausweichdialog (manuelle Pfadwahl statt Fehlermeldung, wenn die
  automatische Spielsuche scheitert) ist im Quellstand **nicht vorhanden**
  (Suche nach `QFileDialog`/`getExistingDirectory` in `nrplanner/` ohne
  Treffer). `app.py:main()` zeigt stattdessen weiterhin
  `QMessageBox.critical` und beendet sich. Das ist kein neuer Fehler, den
  dieser Lauf ausgeloest hat, sondern die in GOAL.md unter A15 "Grund"
  beschriebene, offenbar noch offene Luecke.
- Kein sonstiger Anwendungsfehler in den geprueften Pfaden gefunden. Die
  Migration (`_migrate_keys`) verhielt sich in allen drei getesteten Faellen
  (einfacher Name, "/"-Name, "\|"-Name) genau wie im eigenen Docstring
  beschrieben.

## An `qa-engineer` und `power-user`

**Beide koennen auf diesem Artefakt starten.** `dist\NightreignHelper.exe`
(59 010 777 Byte, SHA-256
`42B21AA2743FE64A83A093BE0261ABAEC361D99903150D620E5324BD4301F221`) startet
in einer isolierten Umgebung ohne Entwicklungswerkzeuge zuverlaessig, findet
die echte Spielinstallation selbststaendig, uebersteht den Versionssprung
von einem echten v1.7.1-Zustand ohne Datenverlust und startet nach
Beenden/Neustart erneut fehlerfrei.

Fuer `power-user` als Ausgangspunkt seiner Sitzung:
- Artefakt: `dist\NightreignHelper.exe` (Pfad oben, Pruefsumme oben).
- Isolierung **zwingend mit drei** Umlenkungen, nicht zwei:
  `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, **und `APPDATA`** (der dritte
  fehlte im urspruenglichen T-113-Auftrag und fuehrte beim ersten,
  abgebrochenen Lauf zu einer echten Verknuepfung im Startmenue dieses
  Kontos).
- Erststart braucht auf einem Rechner mit installiertem Spiel real **ca. 5
  Minuten**, nicht die im Programm genannte "eine Minute" -- als Erwartung
  in die eigene Sitzung einplanen.
- A15 (manuelle Pfadwahl bei nicht gefundenem Spiel) ist **nicht
  implementiert**; ein Testlauf dazu wuerde heute auf eine Fehlermeldung
  treffen, kein Auswahldialog.
- Der QA-046-Fall (Gross-/Kleinschreibungs-Kollision bei Build-Namen) und ob
  eine bestehende Start-Menue-Verknuepfung nach einem Update weiter auf die
  richtige EXE zeigt, sind aus diesem Lauf **offen** (siehe "Wo ich nicht
  klicken konnte").

## An `director`

**Urteil: CONCERNS.** Empfehlung: freigeben mit benannten Einschraenkungen.

Das Artefakt ist clean-room-tauglich fuer das, was ich pruefen konnte: echter
Erststart, echte automatische Spielerkennung, echter Update-Weg von einem
real heruntergeladenen v1.7.1 ohne Datenverlust (auch nicht bei den beiden
historisch heikelsten Namensformen), sauberer Neustart. Die
Datenschutzsperre hat in allen drei Laeufen gehalten, mehrfach nachgemessen.

Einschraenkungen, die ich nicht selbst schliessen kann oder darf:
1. **A15 ist im Code nicht vorhanden** (siehe An developer). GOAL.md
   verknuepft A9 und A15 ausdruecklich zu einer gemeinsamen P9-Abnahme --
   das ist eine Entscheidung fuer dich, nicht fuer mich: entweder P9 wartet
   auf A15, oder A9 wird gesondert als Teilabnahme gefuehrt.
2. Der QA-046-Fall (Gross-/Kleinschreibung) und die Verknuepfungs-
   Aktualisierung bei einer bestehenden Start-Menue-Verknuepfung sind
   mangels GUI-Automatisierung in diesem Lauf ungeprueft geblieben.
3. SmartScreen/Virenscanner-Verhalten beim echten Download-und-Doppelklick
   ist in dieser Umgebung strukturell nicht pruefbar (kein Browser-Download,
   kein Explorer-Start).
4. Keine echte Fremdinstallation (siehe Vorbehalt oben).

Kein `.gitignore`-Nachtrag noetig (Testartefakte lagen ausschliesslich im
Scratchpad, nicht im Repository). Kein Tag-Vorschlag -- das ist nicht mein
Auftrag in diesem Lauf (Modus `clean-room`, nicht `notes`).
