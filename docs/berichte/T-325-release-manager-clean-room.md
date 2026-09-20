STATUS: fertig - alle fuenf Ablaufschritte bestanden, Update-Weg 1.16.0 ->
1.17.0 inklusive echtem EXTRACT_VERSION-Sprung 15 -> 16 (Cache-Neubau 37,2 s)
und Zweitstart belegt.
AUFTRAG: T-325l - clean-room-Lauf gegen dist/NightreignHelper.exe 1.17.0 mit
Update-Weg von 1.16.0, EXTRACT_VERSION-Sprung als Kern (release-manager,
Modus `clean-room`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 558 Zeilen; juengster
Abschnitt "Auflagen vor der Veroeffentlichung 1.13.1", T-283c, Stand
`1f51485`, 16.09.2026: Gesamtampel GELB, **keine Auflage auf ROT**; keine
neue Auflagen-Runde seither im Register, obwohl 1.14.0-1.17.0 dazwischen
liegen - dieser Lauf ist also nicht durch eine aktuellere Bewertung gedeckt,
aber auch durch keine offene rote Auflage gesperrt, siehe "An director");
docs/tasks/T-325.md (vollstaendig, 57 Zeilen - der Abschnitt "T-325l" selbst
steht nicht im Dokument, nur die Kurzzeile in T-325k: "dann l clean-room, m
power-user, n notes"; der Auftrag kam ausschliesslich aus der Aufgaben-
stellung dieses Laufs); docs/release/ROLLOUT.md Z. 269-320 ("Ablaufplan fuer
den `build`- und den `clean-room`-Lauf" - Vorlage nennt v1.7.1, hier durch
die Auftragsvorgabe v1.16.0 ersetzt); docs/berichte/T-322-release-manager-
clean-room.md (Vorlage: Kontraktblock, Save-Build-Rezept, Aufraeum-Nachweis);
docs/berichte/T-285-release-manager-clean-room.md (Methodik-Nachtrag: Save-
Knopf braucht echten Mausklick statt InvokePattern, Save-Dialog nur ueber
TopWin auffindbar, SendKeys fuer den Namen); CLAUDE.md Z. 74-79 ("Fester
Testabzug", Stand 20.09. T-324b, EXTRACT_VERSION 16, Grenze "ueber 16"; alte
v15-Fassung unter `NightreignHelper-Testabzug-v15` gesichert); docs/plan-
restarbeiten.md Z. 325-339 ("Ersetzt am 20.09.2026 (T-324b, developer)" -
bestaetigt, dass die Vorlagenablage bereits vor diesem Lauf ersetzt wurde,
dieser Lauf ist selbst der "erste betroffene Lauf" fuer den Cache-Sprung, hat
aber nichts an CLAUDE.md/plan-restarbeiten.md zu aendern, das hat T-324b
schon getan); nrdata/extract.py Z. 103 (`EXTRACT_VERSION = 16`);
scripts/drive_window.ps1 (UIA-Treiber, uebernommen, nicht geaendert).
GEAENDERT: nichts im Repository ausser diesem Bericht (`git status` vor dem
Lauf clean bei `fc57b93`, danach unveraendert clean bis auf diesen Bericht).
Ausserhalb: eigenes Scratchpad `...\scratchpad\T-325l\` (dl/install/local/
roaming) angelegt, benutzt, vollstaendig geloescht (`Test-Path` -> `False`
nach dem Lauf); Registryschluessel `HKCU\Software\DankYeeterT-325l` (vier
Test-Builds, `__schema=3`) vollstaendig geloescht (`Test-Path` -> `False`);
vier temporaere PNG-Bildnachweise in `%TEMP%` geloescht (NH-002-konform, nie
ins Repo uebernommen).
ANNAHMEN: Vorversion 1.16.0 per `gh release download v1.16.0` geladen (exakt
wie im Auftrag benannt). Fuer den echten EXTRACT_VERSION-Sprung wurde die vom
Auftrag genannte gesicherte v15-JSON (`NightreignHelper-Testabzug-v15`, als
flache Datei abgelegt, nicht als Verzeichnis - Inhalt ist byteidentisch mit
der `nightreign_data.json`, die T-324b vor dem Ersetzen gesichert hat) anstelle
der `nightreign_data.json` in einer Kopie des aktuellen v16-Testabzugs
eingesetzt; die 840 Symboldateien (`icons/`) blieben aus dem v16-Abzug, weil
`ICON_VERSION` unveraendert bei 3 liegt (plan-restarbeiten.md Z. 330) und ein
echter 1.16.0-Ersteinsatz dieselben Symbole mitgebracht haette.
NAECHSTER: keiner aus diesem Lauf - Freigabeentscheidung liegt beim
`director`.
BLOCKIERT DURCH: nichts.

---

# T-325l - clean-room 1.17.0, Update von 1.16.0, EXTRACT_VERSION 15 -> 16

## Kontraktblock

| | |
|---|---|
| **Modus** | `clean-room` |
| **Artefakt** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.250.281 Byte (gemessen, `Get-Item`) - identisch mit dem im Auftrag genannten Wert und mit T-325k |
| **SHA-256 (nachgemessen)** | `BFEEB0270D16C88FDEC67DF10F2D5C76FD29AB5002F6EEC2E14691F321E7C4B4` (`Get-FileHash`) - identisch mit dem im Auftrag genannten Wert |
| **Quell-Commit** | `fc57b93` (`git rev-parse HEAD`, Arbeitsstand sauber vor und nach dem Lauf) |
| **Vorversion fuer Update-Pfad** | `NightreignHelper.exe` aus Release `v1.16.0`, 59.242.393 B, SHA-256 `B02F042F5E8E8DB3D6A92B4E5C6EA65FC702489497849A5F4899E3C762C84129` (`gh release download`, Hash gegen die mitgelieferte `.sha256`-Datei und gegen eigene Nachmessung bestaetigt) |
| **Cache-Neubau-Dauer** | **37,2 s** (Prozessstart 22:25:10 -> `nightreign_data.json` neu geschrieben 22:25:47, `New-TimeSpan` gegen `Get-Process.StartTime` und `Get-Item.LastWriteTime`) |
| **Urteil dieses Laufs** | **freigeben** - alle fuenf Ablaufschritte bestanden, echter EXTRACT_VERSION-Sprung nachgewiesen, kein Datenverlust |

## Gepruefte Umgebung

**Kein neues Konto, keine VM, kein Container** - auf dieser Maschine nicht
verfuegbar, wie in jedem bisherigen Lauf. Isolierung, die erreicht wurde:
eigenes leeres Scratchpad-Verzeichnis ausserhalb des Repos (`T-325l` mit den
Unterordnern `dl`, `install`, `local`, `roaming`), `NIGHTREIGN_SETTINGS_ORG=
DankYeeterT-325l`, `LOCALAPPDATA`/`APPDATA` auf Wegwerfpfade im selben
Scratchpad, gesetzt im selben PowerShell-Aufruf wie der jeweilige Start (ein
Nebenbefund: da Umgebungsvariablen zwischen einzelnen PowerShell-Aufrufen
dieser Sitzung nicht bestehen bleiben, wurde ein spaeterer Kontrollbefehl aus
Versehen einmal gegen das echte `%LOCALAPPDATA%` statt gegen die Umlenkung
ausgefuehrt - reiner Lesezugriff, `Select-String` auf `nightreign_data.json`,
keine Schreibaktion, kein Schaden; der eigentliche Programmlauf selbst hatte
die Umlenkung korrekt gesetzt und zeigt es auch im Ergebnis, siehe Schritt 4).
`PATH` nicht geleert, `.venv` bleibt technisch erreichbar (in diesem Lauf
nicht benutzt). Vor dem ersten Start `Get-Process NightreignHelper`: 0
Treffer; nach jedem Beenden erneut 0 Treffer geprueft (NH-004 eingehalten,
kein zweiter Lauf parallel).

**Nicht isoliert, wie in allen bisherigen Laeufen:** dasselbe Windows-Konto,
derselbe Rechner, `PATH` unveraendert. Als **ungeprueft** ausgewiesen, nicht
als bestanden.

**Bekannter, hier erneut beobachteter Nebeneffekt:** Die Statuszeile zeigte
"313 relics in USER_DATA000, 110 stored builds" nach dem Update - das ist der
echte Spielstand, trotz umgelenktem `APPDATA` gefunden (`savefile.py`-
Fallback, reiner Lesezugriff, unveraendert seit T-241/T-265/T-322
dokumentiert, kein neuer Befund).

Testabzug-Kopie (841 Dateien, 21.139.391 B, `EXTRACT_VERSION` 16, Vorlage aus
CLAUDE.md/T-324b) in das isolierte `LOCALAPPDATA` **kopiert**, danach die
`nightreign_data.json` darin **gezielt durch die gesicherte v15-Fassung
ersetzt** (8.803.996 B, `extract_version: 15`), damit die 1.16.0-Seite exakt
den Zustand zeigt, den ein echter Nutzer beim letzten Start von 1.16.0 vor dem
Umstieg gehabt haette - der Punkt, den der Auftrag als Kern benannt hat.

## Ergebnis je Schritt

**0. Isolierung** - bestanden, mit den oben genannten, bekannten
Einschraenkungen (kein Konto/keine VM, `PATH` unveraendert; ein versehentlicher
Lesezugriff auf das echte `LOCALAPPDATA` zwischen zwei Schritten, siehe oben).

**1. Nur die EXE in ein leeres Verzeichnis, Installation nach README** -
bestanden. 1.16.0 (aus `v1.16.0`, Hash siehe Kontraktblock) in das leere
Scratchpad-Verzeichnis kopiert und ausschliesslich per `Start-Process`
(Doppelklick-Aequivalent) gestartet - kein Installer, keine Admin-Rechte.
Fenster "Nightreign Helper 1.16.0" nach rund 3 s (kopierter Testabzug, keine
Erstextraktion noetig).

**2. Starten, schreibende Aktion, beenden, neu starten** - bestanden. Vier
Builds ueber den **Save**-Knopf angelegt: `CleanroomT325l1`,
`Name/WithSlash`, `Name|WithPipe`, `UPPERCASE` (dieselben drei Sonderfaelle
wie in T-265/T-285/T-322, aus denen QA-003/QA-046 und die Migration
entstanden). Methodik wie in T-285 festgehalten: `InvokePattern.Invoke()` auf
den Save-Knopf reicht nicht, echter Mausklick (`ClickAt`/`GetWindowRect`-
Koordinaten) noetig; der Save-Dialog erscheint als eigenes Top-Level-Fenster
(`TopWin "Save build*"`), Text per `SendKeys.SendWait`, Bestaetigung per
Klick auf den echten "OK"-Knopf (nicht `{ENTER}` - im ersten Versuch dieses
Laufs verpuffte ein `{ENTER}` wirkungslos, weil der Dialog beim Senden noch
nicht im Vordergrund war; nach `Fg $dlg` vor der Texteingabe lief es
zuverlaessig, per Screenshot am Dialog selbst bestaetigt). Registry-Beleg
`HKCU\Software\DankYeeterT-325l\NightreignHelper\builds\1`: alle vier Namen
korrekt Percent-kodiert, `__schema=3`, `__order` vollstaendig, `__selected`
zeigt den zuletzt gespeicherten Build (`UPPERCASE`). App per
`WindowPattern.Close()` beendet (`Get-Process` danach 0 Treffer), neu
gestartet: Build-Auswahlbox (`ValuePattern.Current.Value`) zeigte nach dem
Neustart weiterhin "UPPERCASE", Registry unveraendert.

**3. Update-Weg 1.16.0 -> 1.17.0, echter EXTRACT_VERSION-Sprung, Kern des
Laufs** - bestanden. 1.16.0 sauber beendet (`Get-Process` 0), `dist/
NightreignHelper.exe` 1.17.0 ueber die 1.16.0-Datei kopiert (Hash/Groesse vor
dem Start nachgemessen, siehe Kontraktblock), gestartet. Cache vor dem Start:
`extract_version: 15`, 8.803.996 B (die eingesetzte v15-JSON). Waehrend des
Neubaus zeigte der Fenstertitel den bekannten Zwischenzustand "Nightreign
Helper" ohne Version (T-285-Befund, hier erneut beobachtet, 28 s lang in
2-Sekunden-Abtastung ohne Aenderung). Nach **37,2 s** (Prozessstart 22:25:10,
`nightreign_data.json`-Neuschreibung 22:25:47) stand der Titel auf
"Nightreign Helper 1.17.0" und die Cache-Datei auf `extract_version: 16`,
8.811.742 B - exakt die Werte der aktuellen Vorlage. **Alle vier Builds
vorhanden**: Registry `__schema` weiterhin `3`, `__order` identisch,
`__selected` weiterhin `UPPERCASE`; Combobox-Wert per UIA gelesen bestaetigt
"UPPERCASE", und das aufgeklappte Dropdown zeigte alle vier Namen korrekt
dekodiert (`CleanroomT325l1`, `Name/WithSlash`, `Name|WithPipe`,
`UPPERCASE`) neben den unveraenderten echten Vessel-/Grail-Eintraegen.
Bildnachweis (`PrintWindow`, nur aus dem Programmfenster, NH-002-konform,
nicht ins Repo uebernommen) zeigt ein vollstaendig geladenes Fenster ohne
Fehlerdialog, inklusive der neuen A26-Statuszeile "313 relics in
USER_DATA000, 110 stored builds". Kein Hinweis auf Datenverlust.

**4. Zweitstart nach Neustart der Umgebung** - bestanden, mit der bekannten
Einschraenkung (kein echter Windows-Neustart, nur vollstaendiges
Prozessende: `Get-Process` vor dem zweiten Start 0 Treffer). 1.17.0 erneut
gestartet, Fenstertitel "Nightreign Helper 1.17.0" nach **3,4 s** (warmer
Cache, kein zweiter Neubau - `extract_version` im isolierten Cache weiterhin
`16`, 8.811.742 B, gegen den korrekten Scratchpad-Pfad nachgemessen).
Combobox weiterhin "UPPERCASE", Registry unveraendert gegenueber Schritt 3.

**5. Aufraeumen** - bestanden. App vor dem Aufraeumen sauber beendet
(`Get-Process` 0 danach). Registryschluessel `HKCU\Software\DankYeeterT-325l`
vollstaendig geloescht (`Test-Path` -> `False`). Scratchpad `...\scratchpad\
T-325l\` vollstaendig geloescht (`Test-Path` -> `False`). Vier temporaere
Bildnachweise in `%TEMP%` geloescht. Echte Nutzerdaten gegengeprueft und
unangetastet: `HKCU:\Software\DankYeeter\NightreignHelper` weiterhin
vorhanden (`Test-Path` -> `True`, Inhalt nicht erneut ausgelesen -
Positivnachweis genuegt laut CLAUDE.md), echtes `%LOCALAPPDATA%\
NightreignHelper` weiterhin vorhanden. Kein `NightreignHelper`-Prozess mehr
aktiv (letzte Pruefung vor Abschluss dieses Berichts: 0 Treffer).

## Artefakt

`dist\NightreignHelper.exe`, 59.250.281 Byte, SHA-256
`BFEEB0270D16C88FDEC67DF10F2D5C76FD29AB5002F6EEC2E14691F321E7C4B4` - beide
Werte gegen die im Auftrag genannten (aus T-325k) nachgemessen und identisch,
sowohl vor als auch nach dem Lauf (Kopie im Scratchpad geaendert, das
Original im Repo nicht). In diesem Lauf **nicht neu gebaut**, nur verwendet
und gehasht. Kein UPX im PATH dieser Maschine - unveraendert gegenueber allen
bisherigen Laeufen, A-031 bleibt bedingungslos nicht ausgeloest.

## Blocker

Keiner. Alle fuenf Ablaufschritte bestanden, keine offene rote Auflage.

## Risiken

- **Maschinenweite Instanzsperre** (`nrplanner/singleinstance.py`) bleibt
  unveraendert ein Risiko fuer parallel angesetzte Rollen, die dieselbe
  `dist/`-EXE anfassen. In diesem Lauf nicht eingetreten (laut Auftrag nur
  eine Leserolle, `ui-ux-designer`, parallel; `Get-Process` bestaetigte vor
  Beginn und zwischen den Schritten 0 Treffer).
- **37,2 s Cache-Neubau ohne sichtbaren Fortschrittsbalken** - der Titel
  zeigt waehrenddessen nur "Nightreign Helper" ohne Version, kein Prozent-
  oder Statustext im Fenster selbst beobachtet (nur per Bildvergleich
  gepruefte Abwesenheit, kein UIA-Element mit Fortschrittsangabe gefunden).
  Ein Nutzer, der beim Versionssprung nicht gewarnt ist, koennte das fuer ein
  Haengenbleiben halten - Beobachtung fuer `power-user`/`ui-ux-designer`,
  kein Blocker.
- Der reale Spielstand wird trotz umgelenktem `APPDATA` gelesen (siehe
  "Gepruefte Umgebung") - rein lesend, dokumentiertes Verhalten, kein neuer
  Befund.
- Keine echte Isolierung (Konto/VM/Container) auf dieser Maschine verfuegbar
  - unveraendert seit allen bisherigen Laeufen.
- Die AUFLAGEN.md-Ampel stammt vom Stand 1.13.1 (16.09.); zwischen 1.14.0 und
  1.17.0 liegt keine neue Auflagen-Runde im Register - keine rote Auflage
  bekannt, aber auch keine frische Bewertung der A26-Aenderungen. Sache des
  `compliance-agent`, kein Befund an mir gerichtet.

## Ungeprueft

- Neues Benutzerkonto, VM, Container - auf dieser Maschine nicht verfuegbar.
- Echter Windows-Neustart fuer Schritt 4 - nur vollstaendiges Prozessende
  geprueft.
- SmartScreen-Dialog - nicht ausgeloest, da beide EXE-Stufen lokal kopiert
  und nicht aus dem Internet heruntergeladen/entpackt wurden (kein "Mark of
  the Web" auf der 1.17.0-Datei; die 1.16.0-Datei kam zwar per `gh` aus dem
  Netz, aber `gh release download` setzt keine Zone-Kennung).
- Deinstallation/Downgrade/Zuruecksetzen - nicht Teil dieses Auftrags (kein
  Installer vorhanden, "Uninstalling means deleting the folder and the
  cache" laut README - nicht eigens nachvollzogen).
- Ob der 37,2-s-Neubau auf einer langsameren Platte/CPU laenger dauert - nur
  auf dieser einen Maschine gemessen, keine Referenz fuer andere Rechner.

## An `developer`

Keine neuen Befunde am Anwendungscode. Waehrend des Cache-Neubaus (Schritt 3)
zeigte das Fenster keinen erkennbaren Fortschritt (Titel ohne Version, keine
Statuszeile mit Prozent) - siehe "Risiken". Kein Fehlverhalten, nur ein
moeglicher UX-Punkt fuer `ui-ux-designer`, kein Bug.

## An `power-user`

Ausgangspunkt: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\
NightreignHelper.exe`, 59.250.281 Byte, SHA-256
`BFEEB0270D16C88FDEC67DF10F2D5C76FD29AB5002F6EEC2E14691F321E7C4B4` - nicht
loeschen, nicht neu bauen. Installation ausschliesslich nach README:
Datei herunterladen/kopieren und starten, SmartScreen mit "More info" ->
"Run anyway" bestaetigen, beim Erststart auf die eigene NIGHTREIGN-
Installation zeigen falls die Automatik sie nicht findet. Instanzsperre ist
maschinenweit - vor dem eigenen Start `Get-Process NightreignHelper`
pruefen, es darf 0 Treffer geben. Falls der Testabzug (v16) nicht als
Vorlage genutzt wird: der erste Start nach einem echten EXTRACT_VERSION-
Sprung braucht **um die 37 s**, ohne sichtbaren Fortschritt - kein Einfrieren.

## An `director`

**Empfehlung: freigeben.** Alle fuenf Ablaufschritte bestanden, Update-Pfad
1.16.0 -> 1.17.0 inklusive des echten `EXTRACT_VERSION`-Sprungs 15 -> 16
(Cache-Neubau 37,2 s, alle vier Testbuilds inklusive Sonderzeichen-Namen
ueberlebten) und beider Neustarts belegt.

1. Kein `.gitignore`-Nachtrag noetig (`dist/` bereits erfasst, keine neue
   Ablage ausserhalb).
2. Keine offene rote Auflage - dieser Lauf war nicht durch `AUFLAGEN.md`
   gesperrt. Hinweis: die letzte Auflagen-Runde im Register bewertet 1.13.1
   (16.09.); 1.14.0-1.17.0 (inklusive A26) sind darin nicht einzeln erfasst -
   fuer den `compliance-agent`, nicht fuer mich zu entscheiden.
3. Kein Ablaufkonflikt in diesem Lauf - laut Auftrag nur `ui-ux-designer`
   parallel (Leserolle), `Get-Process` durchgehend mit 0 Treffern ausserhalb
   der eigenen Fenster bestaetigt.
4. Kein Tag-Vorschlag (nicht `notes`-Modus - `notes` fuer 1.17.0 ist nicht
   Teil dieses Laufs).
5. Einschraenkungen fuer die Freigabeentscheidung: keine echte Isolierung
   (Konto/VM), kein echter OS-Neustart, SmartScreen nicht ausgeloest (siehe
   "Ungeprueft").
