STATUS: teilweise
AUFTRAG: T-241d - clean-room-Lauf gegen dist/NightreignHelper.exe 1.10.0 (release-manager, Modus `clean-room`)
GELESEN: docs/tasks/T-241.md (vollstaendig); docs/legal/AUFLAGEN.md (vollstaendig, 446 Zeilen - Abschnitt T-241a/compliance-agent vom 14.09. massgeblich: heutiger Zweck GRUEN, keine Auflage ROT/offen); docs/release/ROLLOUT.md:255-322 (Ablaufplan `clean-room` und die Vorlaufbefunde zur Nicht-Reproduzierbarkeit); docs/berichte/T-241-release-manager-build.md (Ausgangspunkt: Pfad, SHA-256, Commit); docs/berichte/T-174-release-manager.md (1.9.0-Referenz, SHA A2180D5D...); README.md Abschnitte "Install" (Z. 62-91) und "Where your data lives" (Z. 480-521); nrplanner/singleinstance.py (vollstaendig - Ursache eines Befunds unten); nrdata/savefile.py Z. 697-738 `save_roots`/`find_saves` (Ursache des wichtigsten Befunds unten); CLAUDE.md Abschnitt "Datenverzeichnisse und Umlenkung"
GEÄNDERT: nichts im Repository (`git status --porcelain` vor und nach dem Lauf leer). Ausserhalb: eigenes Scratchpad-Verzeichnis `...\scratchpad\T241d-cleanroom\` (install/localappdata/appdata) angelegt, benutzt, vollstaendig geloescht; `HKCU\Software\DankYeeterCleanroom` angelegt, benutzt, vollstaendig geloescht (beides gegengeprueft). Dieser Bericht neu angelegt.
ANNAHMEN: "Neustart der Umgebung" (Schritt 4) als vollstaendiges Beenden und Neustarten aller Prozesse unter der isolierten Umlenkung ausgelegt, nicht als echter Windows-Neustart (nicht verfuegbar in dieser Sitzung) - siehe "Ungeprueft".
NÄCHSTER: director entscheidet ueber die zwei Befunde unten (machine-weite Instanzsperre kollidiert mit dem parallelen T-241d-Design; APPDATA-Umlenkung isoliert die Spielstandsuche nicht vollstaendig)
BLOCKIERT DURCH: nichts fuer diesen Lauf selbst. Keine rote Auflage (T-241a, 14.09., Ampel GRUEN fuer lokalen Bau/Eigenlauf).

---

# T-241d - clean-room 1.10.0

## Geprüfte Umgebung - wie sauber sie wirklich war

**Kein neues Konto, keine VM, kein Container** - nicht verfuegbar in dieser Sitzung. Isolierung bestand aus:
- eigenes leeres Verzeichnis ausserhalb des Repos (Scratchpad, nicht `%LOCALAPPDATA%`, nicht im Projektbaum)
- `LOCALAPPDATA` und `APPDATA` nur fuer den Kindprozess auf Wegwerf-Pfade gesetzt (`ProcessStartInfo.EnvironmentVariables`, nicht `Start-Process`/Sitzungsweit)
- `NIGHTREIGN_SETTINGS_ORG=DankYeeterCleanroom`
- `PATH` auf die vier Windows-Systempfade reduziert (kein `.venv`, kein Git, kein Python)

**Nicht isoliert, weil auf diesem Rechner nicht erreichbar:** dasselbe Windows-Benutzerkonto und dieselbe Anmeldesitzung wie der Entwicklungsrechner (kein neues Konto); `USERPROFILE`/`Path.home()` unveraendert - genau das ist Ursache von Befund 2 unten; derselbe Datentraeger, dieselbe Registry-Hive (nur der Unterschluessel war neu); kein Virenscanner-Zustand geprueft. Diese Punkte sind **ungeprueft**, nicht bestanden.

## Ergebnis je Schritt

**0. Isolierung** - bestanden, mit den oben genannten Einschraenkungen benannt.

**1. Nur die EXE, Installation nach README** - bestanden. Einzig die 59.083.369-Byte-Datei aus `dist/` in das leere Verzeichnis kopiert (Hash vorher/nachher `314CA35C...930BD` identisch). README "Install" verlangt nichts weiter als "Download and run" - kein Installer, keine Admin-Rechte, das stimmt mit dem Verhalten ueberein.

**2. Starten, schreibende Aktion, beenden, neu starten** - bestanden. Erststart: Spielordner automatisch ueber die Steam-Registry gefunden (`HKLM\...\Valve\Steam`, PATH-unabhaengig, kein Umweg noetig), Datenaufbau lief **echt neu** (kein Testabzug kopiert - bewusste Entscheidung fuer den echten Erstaufbau, siehe unten), 841 Dateien in der umgelenkten `LOCALAPPDATA` entstanden, Fenstertitel "Nightreign Helper 1.10.0" nach rund 20 s. Schreibende Aktion: **Save**-Knopf im Build-Planer per UI Automation (`InvokePattern`) betaetigt - Registry-Beleg `HKCU\Software\DankYeeterCleanroom\NightreignHelper\builds\1` mit `__schema=3` entstanden. App sauber ueber `WindowPattern.Close()` beendet (Prozess verschwindet, kein Restprozess), neu gestartet (~5 s, warmer Cache) - Build **1** stand unveraendert in der Registry, die Start-Menue-Verknuepfung (`...\appdata\...\Nightreign Helper.lnk`, 3602 B) blieb auf Platte.

**3. Update-Weg ueber 1.9.0** - **ungeprueft, wie im Auftrag vorgesehen bei Fehlen des Artefakts.** Geprueft, nicht vermutet: `gh release list` (authentifiziert als DankYeeter) zeigt als neuestes Release `v1.7.1`; **kein `v1.9.0`-Tag/Release existiert** auf GitHub. Lokal: `dist/` enthaelt nur die 1.10.0-Datei (vom `build`-Lauf ueberschrieben); eine Volltextsuche nach der 1.9.0-Pruefsumme (`A2180D5D...66EF3`, aus T-174) auf dem Rechner (`find ... -iname "*NightreignHelper*.exe"`) findet ausser der 1.10.0-Datei nur eine Scratchpad-Kopie mit anderem Hash (`05323B50...`, das ist T-241c Lauf 1, nicht 1.9.0). Auftrag: "existiert kein 1.9.0-Artefakt mehr: als ungeprueft ausweisen, nicht bauen" - **nicht gebaut**, wie verlangt. Damit auch die drei Sonderfall-Buildnamen (`/`, `|`, Grossbuchstaben) und die `__schema`-Migrationspruefung **ungeprueft**.

**4. Zweitstart nach Neustart der Umgebung** - bestanden, mit Einschraenkung (siehe "Ungeprueft": kein echter OS-Neustart). App vollstaendig beendet (`Get-Process` leer, gegengeprueft), erneut gestartet - Fenster erschien in ~5 s, Build **1** weiterhin vorhanden. Zusaetzlich die Instanzsperre selbst geprueft: ein dritter Start **derselben** Org waehrend die zweite Kopie noch lief wurde korrekt abgewiesen (`Process.HasExited=True`, kein zweites Fenster) - das Verhalten aus `singleinstance.py` funktioniert innerhalb der eigenen Umlenkung wie dokumentiert.

**5. Aufraeumen** - bestanden. `HKCU\Software\DankYeeterCleanroom` vollstaendig geloescht (`reg query` danach: "unable to find"), Scratchpad-Verzeichnis vollstaendig geloescht (`Test-Path` -> `False`), keine laufenden Prozesse aus meinem Lauf uebrig. Echte Nutzerdaten gegengeprueft und unveraendert: `%LOCALAPPDATA%\NightreignHelper` weiterhin 841 Dateien, `nightreign_data.json` `LastWriteTime` unveraendert (17.08., vor diesem Lauf); `HKCU\Software\DankYeeter\NightreignHelper` traegt weiterhin nur `builds`/`chalices`/`favourites`/`ui`, kein neuer Eintrag; echtes Start-Menue weiterhin ohne Nightreign-Verknuepfung. Der reale Spielstand (`...\Roaming\Nightreign\76561198179244962\NR0000.sl2`) hat `LastWriteTime` 13.09.2026 19:17 - **vor** diesem Lauf, also unveraendert trotz Lesezugriffs (siehe Befund 2).

## Befund 1 (Prozess, nicht Produkt): machine-weite Instanzsperre kollidiert mit dem parallelen T-241d-Design

Der Auftrag sieht vor, dass `release-manager` (clean-room), `qa-engineer` und `power-user` **gleichzeitig** dieselbe `dist/`-EXE mit **eigenen** Umlenkungen benutzen. Mein erster Startversuch (08:06 Uhr) wurde jedoch von der maschinenweiten `QSharedMemory`-Sperre (`nrplanner/singleinstance.py:32`, Kommentar im Code: *"Machine-wide"*) abgefangen: eine zu dem Zeitpunkt laufende Kopie unter `.scratch-powuser\T-241pu\app\` (power-user) hielt die Sperre, mein Prozess beendete sich sofort ohne eigenes Fenster (`Process.HasExited=True` Sekunden nach Start). Erst nachdem diese Kopie beendet war (08:25 Uhr, ~19 Min. spaeter), konnte mein Lauf tatsaechlich starten. Das ist **kein Produktfehler** - die Sperre tut genau das, wofuer sie gebaut wurde (QA-163: zwei ununterscheidbare Fenster). Es ist ein **Luecke im Testablauf**: die Umlenkung trennt Daten (LOCALAPPDATA/APPDATA/Registry-Organisation), aber nicht die Instanzsperre, die an keinen dieser Werte gebunden ist. Auf einem echten Zielrechner betrifft das nur den seltenen Fall zweier gleichzeitiger Konten in derselben Anmeldesitzung; hier hat es reale Wartezeit gekostet, weil drei Rollen im selben Windows-Konto parallel testen sollten.

## Befund 2 (wichtiger, Testmethodik-Luecke): APPDATA-Umlenkung isoliert die Spielstandsuche nicht vollstaendig

Der Auftrag ging davon aus: *"die Spielstandsuche laeuft mit umgelenktem APPDATA ins Leere"* - **das traf nicht zu.** Trotz vollstaendig umgelenktem `APPDATA` fand die App beim Erststart automatisch den echten Spielstand (`314 relics in USER_DATA000, 110 stored builds` erschien im UI, ohne dass ich einen Dialog benutzt habe). Ursache, gelesen in `nrdata/savefile.py:697-718` (`save_roots()`):

```
appdata = os.environ.get("APPDATA")
if appdata:
    roots.append(pathlib.Path(appdata))
roots.append(pathlib.Path.home() / "AppData" / "Roaming")   # <- zusaetzlicher, fest verdrahteter Fallback
```

Der Docstring begruendet das ausdruecklich fuer den echten Nutzer (Ordnerumleitung, OneDrive-Profile, Unternehmensprofile). Fuer die Testisolierung heisst das: `Path.home()` haengt an `USERPROFILE`, das meine Umlenkung nicht gesetzt hat (und ein Setzen waere riskant - Windows-APIs verlassen sich an vielen Stellen darauf) - der zweite Suchpfad zeigt deshalb weiterhin auf den echten `C:\Users\Daniel\AppData\Roaming`, unabhaengig vom gesetzten `APPDATA`. Die im Auftrag verlangte Handlung ("dann den Dialog benutzen und ... NR0000.sl2 waehlen") **war dadurch nicht noetig und wurde nicht ausgefuehrt** - die Automatik fand den Spielstand von selbst. Die Datei blieb nachweislich unveraendert (`LastWriteTime` vor dem Lauf), also kein Schreibzugriff, aber die Isolierung war an dieser einen Stelle luecken­haft.

**Tragweite:** `CLAUDE.md` fuehrt `APPDATA` nur fuer `nrplanner/shortcut.py` als umzulenkende Stelle - `nrdata/savefile.py` liest `APPDATA` zwar auch, hat aber zusaetzlich diesen nicht dokumentierten `Path.home()`-Fallback. Jeder kuenftige Test, der sich fuer eine *echte* Trennung von der Spielstand-Suche auf die in `CLAUDE.md` genannten drei Variablen verlaesst, bekommt trotzdem den echten Spielstand zu sehen. Das ist harmlos, solange nur gelesen wird (wie hier, wie es das Programm laut README auch immer tut), aber es widerspricht der Grundannahme "eigene Umlenkung = eigene Daten" an dieser einen Stelle.

## Artefakt

Unveraendert aus T-241c: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`, 59.083.369 Byte, SHA-256 `314CA35C9AFA9BD71C6FAE9928BC0E1E4ABDBE19814BBB099CCA11A04A3930BD`, Commit `9e8933d`. In diesem Lauf nicht neu gebaut, nur kopiert und gestartet; Hash vor und nach dem Test gegengeprueft, identisch.

## Blocker

Keiner fuer diesen Lauf. Kein Release, kein Push, keine Weitergabe - wie beauftragt.

## Risiken

- Befund 1 (Instanzsperre) kostet bei kuenftigen parallelen Rollenlaeufen im selben Konto reale Wartezeit, kein Datenrisiko.
- Befund 2 (Spielstand-Fallback) macht kuenftige Isolierungs-Annahmen brüchig, wenn sich jemand nur auf `CLAUDE.md`s Drei-Variablen-Tabelle verlaesst und einen echten "kein Spielstand gefunden"-Zustand erzeugen will (z. B. fuer den power-user-A15-Test "Automatik laeuft ins Leere") - dort betrifft es den **Spielordner** (Steam-Registry), nicht den Spielstand, und ist insofern unabhaengig von Befund 2; trotzdem ist die Diskrepanz zwischen Auftragserwartung und gemessenem Verhalten hier dokumentiert, falls ein kuenftiger Lauf bewusst einen leeren Spielstand simulieren will.
- Update-Pfad (Schritt 3) bleibt vollstaendig ungeprueft fuer 1.10.0 - das ist der Schritt, an dem laut `ROLLOUT.md` echte Releases scheitern, und er ist seit dem Verlust der 1.9.0-Artefakte (T-174, versehentliches `rm -rf`) nicht mehr nachstellbar, ausser es wird gezielt neu gebaut (nicht mein Auftrag heute).

## Ungeprueft

- Echter Windows-Neustart (nur vollstaendiges Prozessende simuliert).
- Neues Benutzerkonto / VM / Container - nicht verfuegbar in dieser Sitzung.
- Update-Weg 1.9.0 -> 1.10.0 inkl. Sonderzeichen-Buildnamen (`/`, `|`, Grossbuchstaben) und `__schema`-Migration - kein 1.9.0-Artefakt mehr vorhanden (siehe Schritt 3).
- Verhalten bei aktivem Virenscanner-Eingriff / SmartScreen (kein Dialog in dieser nicht-interaktiven Sitzung beobachtbar).
- Die vom power-user zu pruefende "Automatik findet Spielordner nicht"-Sackgasse (A15) - hier fand die Automatik den Ordner anstandslos, das ist sein Auftrag, nicht dieser.

## An `developer`

Keine neuen Befunde im Anwendungscode. Die beiden Befunde oben sind Beobachtungen ueber dokumentiertes, absichtliches Verhalten (`singleinstance.py`, `savefile.py`), kein Bug.

## An `power-user`

Ausgangspunkt fuer die eigene Sitzung: `dist/NightreignHelper.exe` (Pfad, Hash, Commit wie oben, unveraendert seit T-241c) - **nicht loeschen, nicht neu bauen**, wie im Auftrag festgelegt. Zwei Hinweise aus diesem Lauf: (1) vor dem eigenen Start pruefen, ob noch eine andere Kopie laeuft (`Get-Process NightreignHelper`) - die Instanzsperre ist maschinenweit und faengt einen Zweitstart sonst ab, ohne dass es wie ein Fehlschlag aussieht (kein Fenster, kein Fehlertext, der Prozess endet einfach). (2) Fuer den geplanten A15-Test ("Automatik laeuft ins Leere", Spielordner an fremdem Ort) betrifft die eigene Umlenkung nur `LOCALAPPDATA`/`APPDATA`/Org - das reicht fuer den Spielordner-Fall (Steam-Registry-Pruefung ist unabhaengig von diesen drei Variablen), aber falls zusaetzlich ein "kein Spielstand gefunden"-Zustand gebraucht wird, reicht die APPDATA-Umlenkung allein nicht (Befund 2 oben).

## An `director`

**Empfehlung: freigeben mit benannten Einschraenkungen** - fuer den Eigenlauf des Nutzers heute Abend (kein Release-Votum, das bleibt bei A-025 und dem Nutzerauftrag "keine Weitergabe"). Kein Blocker in den vier durchgefuehrten Schritten (Installation, Schreiben+Neustart, Zweitstart, Aufraeumen); Schritt 3 (Update) bleibt ausdruecklich ungeprueft, wie der Auftrag es fuer den Fall des fehlenden 1.9.0-Artefakts vorsieht.

Zu entscheiden/zur Kenntnis:
1. **Befund 1** - die drei parallelen T-241d-Rollen im selben Windows-Konto koennen sich gegenseitig ueber die Instanzsperre blockieren; fuer kuenftige parallele Laeufe entweder zeitlich entzerren oder wissentlich in Kauf nehmen.
2. **Befund 2** - `CLAUDE.md`s Umlenkungstabelle nennt `APPDATA` nur fuer `shortcut.py`; `savefile.py` hat einen zusaetzlichen `Path.home()`-Fallback, der bei reiner APPDATA-Umlenkung weiterhin den echten Spielstand findet. Kein Sicherheitsproblem (nur Lesezugriff, geprueft unveraendert), aber eine Luecke in der Testisolierungs-Doku - Ergaenzung der Tabelle ist Sache des `director`/`technical-writer`, nicht meine.
3. Kein `.gitignore`-Nachtrag noetig (nichts Neues ausserhalb bereits erfasster Pfade erzeugt).
4. Kein Tag-Vorschlag - das ist `notes` (T-241e), nicht dieser Modus.
