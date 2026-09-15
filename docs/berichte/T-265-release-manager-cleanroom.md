STATUS: fertig
AUFTRAG: T-265 - clean-room-Lauf gegen dist/NightreignHelper.exe 1.12.0 mit Update-Weg 1.11.0 -> 1.12.0 (release-manager, Modus `clean-room`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 525 Zeilen - "Keine Auflage steht auf ROT" Z. 267/331 bestaetigt, kein Release-Sperr-Befund fuer diesen Lauf); docs/release/ROLLOUT.md:280-315 (Ablaufplan `clean-room`); docs/berichte/T-241-release-manager-cleanroom.md (Methodik-Referenz: UI Automation InvokePattern, ProcessStartInfo/`Start-Process`-Umlenkung, bekannte Befunde 1/2); README.md "Install" (Z. 62-91) und "Where your data lives" (Z. 515-549); nrplanner/paths.py, nrdata/extract.py (EXTRACT_VERSION=11, Testabzug gueltig); nrplanner/app.py Z. 1824-1843 (`_save_build`); nrplanner/advisorblock.py (MarkButton-Zyklus None->EXCLUDED->REQUIRED); nrplanner/effectfilters.py (QSettings-Pfad `advisor/excluded`); nrplanner/chalices.py Z. 459-479 (Handedness-Kodierung, 1H-Default ohne `2H`-Suffix); CLAUDE.md Abschnitt "Datenverzeichnisse und Umlenkung"
GEAENDERT: nichts im Repository (`git status` vor und nach dem Lauf clean, wie im gitStatus-Snapshot). Ausserhalb: eigenes Scratchpad-Verzeichnis `...\scratchpad\T265\` (install/localappdata/appdata) angelegt, benutzt, vollstaendig geloescht (gegengeprueft: `Test-Path` -> False); `HKCU\Software\DankYeeterCleanroom2` angelegt, benutzt, vollstaendig geloescht (gegengeprueft: `Test-Path` -> False). Dieser Bericht neu angelegt.
ANNAHMEN: "Neustart der Umgebung" (Schritt 4/5) als vollstaendiges Prozessende + Neustart ausgelegt, kein echter Windows-Neustart (nicht verfuegbar). "Effektmarkierung setzen" ueber den Relic-Picker der Slot-Ansicht (`advisorblock.MarkedLine`, `•`-Bullet-Button), da das die einzige im Programm erreichbare Stelle fuer `Don't include` ist.
NAECHSTER: qa-engineer, power-user (beide warten auf diesen Bericht als Ausgangspunkt); director fuer die Empfehlung unten.
BLOCKIERT DURCH: nichts. AUFLAGEN.md traegt keine offene rote Auflage (Stand 15.09., Abschnitt "Keine Auflage steht auf ROT").

---

# T-265 - clean-room 1.12.0 mit Update-Weg

## Geprüfte Umgebung

**Kein neues Konto, keine VM, kein Container** - nicht verfuegbar in dieser Sitzung. Isolierung:
- eigenes leeres Verzeichnis ausserhalb des Repos (Scratchpad, nicht `%LOCALAPPDATA%`, nicht im Projektbaum)
- `NIGHTREIGN_SETTINGS_ORG=DankYeeterCleanroom2`, `LOCALAPPDATA`/`APPDATA` sitzungsweit auf Wegwerf-Pfade gesetzt (nur fuer die PowerShell-Prozessbaeume dieses Laufs, kein anderer Prozess betroffen)
- Testabzug-Kopie (nicht Verweis) in das umgelenkte `LOCALAPPDATA` (841 Dateien, `extract_version` 11, deckt sich mit `EXTRACT_VERSION 11` im aktuellen Code - Vorlage weiterhin gueltig)

**Nicht isoliert:** dasselbe Windows-Konto/dieselbe Anmeldesitzung (kein neues Konto); `USERPROFILE`/`Path.home()` unveraendert - der Spielstand wurde wie in T-241 Befund 2 automatisch ueber den `Path.home()`-Fallback gefunden, nicht ueber das umgelenkte `APPDATA` (nur Lesezugriff, siehe unten); `PATH` nicht geleert (kein `.venv`/Git-Einfluss beobachtet, aber nicht ausgeschlossen); kein Virenscanner-Zustand geprueft. Diese Punkte sind **ungeprueft**, nicht bestanden.

## Ergebnis je Schritt

**0. Isolierung** - bestanden, Einschraenkungen wie oben benannt.

**1. Nur die EXE, Installation nach README** - bestanden. 1.11.0 (59.105.391 B, SHA `F23EB0F7...6E8E0`, stimmt mit Auftragsangabe ueberein) in das leere Verzeichnis kopiert, README "Install" verlangt nur "Download and run" - erfuellt.

**2. Starten, mehrere Builds speichern (`/`, `|`, Grossbuchstaben), Effektmarkierung setzen, beenden** - bestanden. 1.11.0 gestartet (Fenstertitel "Nightreign Helper 1.11.0"), vier Builds ueber den **Save**-Knopf per UI Automation gespeichert: `CleanroomTest1`, `Name/WithSlash`, `Name|WithPipe`, `UPPERCASE` - alle vier in der Registry unter `HKCU\...\builds\1` mit korrektem Percent-Encoding im `__order`-Schluessel und `__schema=3`. Effektmarkierung: im Relic-Picker eines leeren Slots den `•`-Bullet-Button der Effektzeile "Improved Attack Power with 3+ Hammers Equipped" einmal geklickt (None->EXCLUDED) - Registry `HKCU\...\advisor\excluded = 7081200` bestaetigt (`effectfilters.py` KEYS-Mapping gelesen und gegen den Registry-Wert verifiziert). App sauber per `WindowPattern.Close()` beendet, kein Restprozess (`Get-Process` leer).

**3. Update-Weg 1.11.0 -> 1.12.0, der Kern des Laufs** - bestanden. 1.12.0 (59.118.289 B, SHA `89C2967A...5F59D8`, stimmt mit Auftrags- und `dist/`-Hash ueberein) ueber die 1.11.0-Datei kopiert, gestartet (Fenstertitel "Nightreign Helper 1.12.0" nach ~4 s, warmer Cache). Alle vier Builds unter ihren Namen vorhanden - im UI-Combo (`'CleanroomTest1'`, `'Name/WithSlash'`, `'Name|WithPipe'`, `'UPPERCASE'`, korrekt dekodiert) und in der Registry unveraendert (`__schema` weiterhin `3`, `__order` unveraendert). Effektmarkierung (`advisor\excluded=7081200`) ebenfalls unveraendert. **1H-Voreinstellung fuer Altbuilds:** in `chalices.py` (Z. 459-479) dekodiert ein Build ohne `2H`-Suffix als `two_handed=False` (1H) - Code gelesen und bestaetigt; ein echtes Schema-2-Altbuild stand fuer diesen Lauf nicht zur Verfuegung (kein Artefakt mehr, wie in T-241 Befund fuer 1.9.0 dokumentiert), daher **nur am Code verifiziert, nicht an echten Altdaten** - siehe "Ungeprueft".

**4. Zweitstart nach Neustart der Umgebung** - bestanden, mit Einschraenkung (kein echter OS-Neustart, siehe "Geprüfte Umgebung"). App vollstaendig beendet (`Get-Process` leer, gegengeprueft), erneut gestartet unter derselben Umlenkung - Fenster erschien nach ~4 s, alle vier Builds und die Effektmarkierung unveraendert in der Registry bestaetigt.

**5. Aufraeumen** - bestanden. Scratchpad-Verzeichnis `...\scratchpad\T265\` vollstaendig geloescht (`Test-Path` -> `False`), `HKCU\Software\DankYeeterCleanroom2` vollstaendig geloescht (`Test-Path` -> `False`), keine laufenden Prozesse aus diesem Lauf uebrig. Echte Nutzerdaten gegengeprueft und unveraendert: `%LOCALAPPDATA%\NightreignHelper` weiterhin 841 Dateien, `nightreign_data.json` `LastWriteTime` 14.09. 17:43 (vor diesem Lauf); `HKCU\Software\DankYeeter\NightreignHelper` traegt weiterhin nur `builds`/`chalices`/`favourites`/`ui`, kein neuer Eintrag.

## Nebenbefund: A-031 (UPX)

`dist\NightreignHelper.exe` enthaelt keine `UPX0`/`UPX1`-Sektionen und keinen `UPX!`-Magic-String an der erwarteten Stelle (Python-Bytesuche negativ, `upx` nicht im `PATH`). **A-031 (UPX-Lizenzausnahme) entfaellt** - die Bedingung "ist die EXE UPX-komprimiert" trifft nicht zu.

## Artefakt

`C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`, 59.118.289 B, SHA-256 `89C2967ACAAAAAC8CA108935CAC0A79C8292D2C7EC0E77831755A15B295F59D8` - unveraendert in diesem Lauf (nur kopiert/gestartet), Hash vor und nach dem Test gegengeprueft, identisch. Vorversion `NightreignHelper-1.11.0.exe`, 59.105.391 B, SHA `F23EB0F784665A8C018C19F353AD114E9809061033076311DCDF21DBB916E8E0`, unveraendert.

## Blocker

Keiner. Keine rote Auflage offen (AUFLAGEN.md, Stand 15.09.).

## Risiken

- Bekannter Befund aus T-241 (Instanzsperre maschinenweit, `singleinstance.py:32`): qa-engineer und power-user muessen zeitlich nacheinander mit derselben `dist/`-EXE arbeiten, sonst faengt die Sperre den Zweitstart ab (kein Fenster, kein Fehlertext).
- Bekannter Befund aus T-241 (`savefile.py` `Path.home()`-Fallback): die APPDATA-Umlenkung isoliert die Spielstandsuche nicht vollstaendig - harmlos, da nur Lesezugriff, aber relevant fuer kuenftige Tests, die bewusst "kein Spielstand" simulieren wollen.
- 1H-Default fuer Altbuilds ist nur am Code, nicht an echten Schema-2-Daten verifiziert (kein Artefakt mehr verfuegbar).

## Ungeprueft

- Echter Windows-Neustart (nur vollstaendiges Prozessende simuliert).
- Neues Benutzerkonto / VM / Container.
- 1H-Voreinstellung an einem echten Schema-2-Altbuild (nur am Code verifiziert, kein Testdatensatz vorhanden).
- Verhalten bei aktivem Virenscanner/SmartScreen (kein Dialog in dieser nicht-interaktiven Sitzung beobachtbar).

## An `developer`

Keine neuen Befunde im Anwendungscode. Update-Weg, Sonderzeichen-Buildnamen, `__schema`-Bestand und Effektmarkierung verhalten sich wie dokumentiert.

## An `power-user`

Ausgangspunkt: `dist/NightreignHelper.exe`, Hash/Commit wie oben - **nicht loeschen, nicht neu bauen**. Vor eigenem Start pruefen, ob noch eine andere Kopie laeuft (`Get-Process NightreignHelper`) - die Instanzsperre ist maschinenweit (siehe Risiken).

## An `director`

**Empfehlung: freigeben mit benannten Einschraenkungen.** Alle fuenf Ablaufschritte bestanden, inklusive des zuvor in T-241 ungeprueften Update-Wegs (diesmal mit Vorversion moeglich). Kein Blocker. A-031 entfaellt (kein UPX). Zwei bekannte Testmethodik-Luecken aus T-241 bestehen unveraendert fort (Instanzsperre, Spielstand-Fallback) - keine neue Entscheidung noetig, nur zur Kenntnis. Kein `.gitignore`-Nachtrag noetig. Kein Tag-Vorschlag (das ist `notes`, nicht dieser Modus).
