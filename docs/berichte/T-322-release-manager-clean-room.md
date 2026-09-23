STATUS: fertig - alle fuenf Ablaufschritte bestanden, Update-Weg 1.15.0 ->
1.16.0 inklusive Sonderzeichen-Namen und Zweitstart belegt.
AUFTRAG: T-322l - clean-room-Lauf gegen dist/NightreignHelper.exe 1.16.0 mit
Update-Weg von 1.15.0 (release-manager, Modus `clean-room`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 558 Zeilen; juengster
Abschnitt "Auflagen vor der Veroeffentlichung 1.13.1", T-283c, Stand
`1f51485`, 16.09.2026: Gesamtampel GELB, **keine Auflage auf ROT, keine
sperrt Bau, Eigenlauf oder diesen Pruef-Lauf**; seither keine neue Auflagen-
Runde im Register); docs/tasks/T-322.md (vollstaendig, 65 Zeilen - der
Abschnitt "T-322l" selbst steht nicht im Dokument, der Auftrag kam
ausschliesslich aus der Aufgabenstellung dieses Laufs); docs/release/
ROLLOUT.md Z. 269-320 ("Ablaufplan fuer den `build`- und den `clean-room`-
Lauf"); docs/berichte/T-285-release-manager-clean-room.md (Methodik-Vorlage:
UI-Automation, Registry-Beweisstellen, Instanzsperren-Risiko); README.md
Z. 26-95 ("Install", "Requirements", Disclaimer); nrplanner/paths.py
(cache_dir = `%LOCALAPPDATA%\NightreignHelper`); nrplanner/favourites.py
Z. 25 (`NIGHTREIGN_SETTINGS_ORG`); scripts/drive_window.ps1 (UIA-Treiber,
uebernommen, nicht geaendert)
GEAENDERT: nichts im Repository ausser diesem Bericht (`git status` vor dem
Lauf clean bei `fd3f124`, danach nur dieser Bericht neu). Ausserhalb: eigenes
Scratchpad `...\scratchpad\T-322l\` (install/local/roaming/prev) angelegt,
benutzt, vollstaendig geloescht (`ls` auf das uebergeordnete Scratchpad-
Verzeichnis nach dem Lauf: `T-322l` nicht mehr vorhanden); Registryschluessel
`HKCU\Software\DankYeeterT-322l` (vier Test-Builds, `__schema=3`)
vollstaendig geloescht (`Test-Path` -> `False`).
ANNAHMEN: Vorversion 1.15.0 per `gh release download v1.15.0` geladen (Option
1 aus dem Auftrag), nicht die Registry-/Cache-Alternative - `gh` war
verfuegbar und das Release trug die passende EXE plus Pruefsumme. Testabzug
(841 Dateien, 21.131.645 B, `EXTRACT_VERSION` 15) unveraendert gegen die in
CLAUDE.md hinterlegte Vorlage - `nrdata/extract.py:98` steht ebenfalls auf
15, die Vorlage ist fuer diesen Lauf gueltig, kein Ersatzbau noetig.
NAECHSTER: keiner aus diesem Lauf - Freigabeentscheidung liegt beim
`director`.
BLOCKIERT DURCH: nichts.

---

# T-322l - clean-room 1.16.0, Update von 1.15.0

## Kontraktblock

| | |
|---|---|
| **Modus** | `clean-room` |
| **Artefakt** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.233.161 Byte (gemessen, `Get-Item`) - identisch mit dem im Auftrag genannten Wert und mit T-322h |
| **SHA-256 (nachgemessen)** | `51F694986D11CA1DED16B6170D552C89579C0E5C67192D78F68FFFF063E8BFC9` (`Get-FileHash`) - identisch mit dem im Auftrag genannten Wert |
| **Vorversion fuer Update-Pfad** | `NightreignHelper.exe` aus Release `v1.15.0`, 59.232.620 B, SHA-256 `59D0D4308460CD6DC6F5D9E3156A1575E40FE68CD9695719CF514C4FD0E1CCDE` (`gh release download`, Hash gegen die mitgelieferte `.sha256`-Datei und gegen die eigene Nachmessung bestaetigt) |
| **Urteil dieses Laufs** | **freigeben** - alle fuenf Ablaufschritte bestanden, kein Datenverlust beobachtet |

## Gepruefte Umgebung

**Kein neues Konto, keine VM, kein Container** - auf dieser Maschine nicht
verfuegbar, wie in jedem bisherigen Lauf. Isolierung, die erreicht wurde:
eigenes leeres Verzeichnis ausserhalb des Repos (Scratchpad `T-322l`),
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-322l`, `LOCALAPPDATA`/`APPDATA` auf
Wegwerfpfade im selben Scratchpad, gesetzt im selben PowerShell-Aufruf wie
der jeweilige Start. `PATH` nicht geleert, `.venv` bleibt technisch
erreichbar (in diesem Lauf nicht benutzt, kein `pip`/`pyinstaller`-Aufruf).
Vor dem ersten und nach dem letzten Start `Get-Process NightreignHelper`
geprueft: beide Male 0 Treffer (NH-004 eingehalten, kein zweiter Lauf
parallel beauftragt oder beobachtet).

**Nicht isoliert, wie in allen bisherigen Laeufen:** dasselbe
Windows-Konto, derselbe Rechner, `PATH` unveraendert. Als **ungeprueft**
ausgewiesen, nicht als bestanden.

**Bekannter, hier erneut beobachteter Nebeneffekt:** Die App fand trotz
umgelenktem `APPDATA` den echten Spielstand (313 Relikte, 110 im Spiel
gespeicherte Loadouts laut Statuszeile) - `savefile.py`-Fallback, reiner
Lesezugriff, unveraendert seit T-241/T-265 dokumentiert, kein neuer Befund.
Die 110 "stored builds" in der Statuszeile sind die Loadouts **aus dem
Spielstand selbst** (`self.owned.loadouts`, `nrplanner/app.py:2424`), nicht
die vier QSettings-Testbuilds dieses Laufs - beide Zaehlungen sind
unabhaengig voneinander, keine Verwechslungsgefahr im Code bestaetigt.

Testabzug (841 Dateien, 21.131.645 B) in das isolierte `LOCALAPPDATA`
**kopiert**, nicht darauf verwiesen - spart die rund 110 s Erstextraktion je
Lauf (CLAUDE.md).

## Ergebnis je Schritt

**0. Isolierung** - bestanden, mit den oben genannten, bekannten
Einschraenkungen (kein Konto/keine VM, `PATH` unveraendert).

**1. Nur die EXE in ein leeres Verzeichnis, Installation nach README** -
bestanden. 1.15.0 (aus `v1.15.0`, Hash siehe Kontraktblock) in das leere
Scratchpad-Verzeichnis kopiert und ausschliesslich per Doppelklick-Aequivalent
(`Start-Process`) gestartet - kein Installer, keine Admin-Rechte, wie
README Z. 28-30 verlangt. Fenster "Nightreign Helper 1.15.0" erschien nach
rund 3 s (durch den kopierten Testabzug ohne die sonst faellige
Erstextraktion).

**2. Starten, schreibende Aktion, beenden, neu starten** - bestanden. Vier
Builds ueber den **Save**-Knopf angelegt: `CleanroomT322l1`,
`Name/WithSlash`, `Name|WithPipe`, `UPPERCASE` (dieselben drei Sonderfaelle
wie in T-265/T-285, aus denen QA-003/QA-046 und die Migration entstanden).
Registry-Beleg `HKCU\Software\DankYeeterT-322l\NightreignHelper\builds\1`:
alle vier Namen korrekt Percent-kodiert, `__schema=3`, `__order` vollstaendig,
`__selected` zeigt den zuletzt gespeicherten Build (`UPPERCASE`). App per
`WindowPattern.Close()` beendet (`Get-Process` danach 0 Treffer), neu
gestartet unter derselben Umlenkung: Build-Auswahlbox zeigte nach dem
Neustart weiterhin "UPPERCASE", Registry unveraendert.

**3. Update-Weg 1.15.0 -> 1.16.0, Kern des Laufs** - bestanden. 1.15.0 sauber
beendet (`Get-Process` 0), `dist/NightreignHelper.exe` 1.16.0 ueber die
1.15.0-Datei kopiert, gestartet. Fenster "Nightreign Helper 1.16.0" nach
3,7 s (kein spuerbarer Migrations-Zwischenschritt, da `EXTRACT_VERSION`
zwischen dem Testabzug und dem aktuellen Code unveraendert bei 15 liegt -
anders als in fruheren Laeufen mit Versionssprung). **Alle vier Builds
vorhanden**: Registry `__schema` weiterhin `3`, `__order` identisch,
`__selected` weiterhin `UPPERCASE`; Combobox-Wert per UIA gelesen bestaetigt
"UPPERCASE". Bildnachweis (`PrintWindow`, nur aus dem Programmfenster,
NH-002-konform, nicht ins Repo uebernommen) zeigt ein vollstaendig geladenes
Fenster ohne Fehlerdialog. Kein Hinweis auf Datenverlust.

**4. Zweitstart nach Neustart der Umgebung** - bestanden, mit der bekannten
Einschraenkung (kein echter Windows-Neustart, nur vollstaendiges
Prozessende: `Get-Process` vor dem zweiten Start 0 Treffer). 1.16.0 erneut
gestartet, Fenster nach 3,2 s (warmer Cache), Combobox weiterhin
"UPPERCASE", Registry (`__schema`, `__order`, `__selected`) unveraendert
gegenueber Schritt 3.

**5. Aufraeumen** - bestanden. App vor dem Aufraeumen sauber beendet
(`Get-Process` 0). Registryschluessel `HKCU\Software\DankYeeterT-322l`
vollstaendig geloescht (`Test-Path` -> `False`). Scratchpad `...\scratchpad\
T-322l\` vollstaendig geloescht (`ls` auf das uebergeordnete Verzeichnis
danach: Ordner nicht mehr enthalten). Echte Nutzerdaten gegengeprueft und
unangetastet: `HKCU:\Software\DankYeeter\NightreignHelper` weiterhin
vorhanden (`Test-Path` -> `True`, Inhalt nicht erneut ausgelesen -
Positivnachweis genuegt laut CLAUDE.md), echtes `%LOCALAPPDATA%\
NightreignHelper` weiterhin vorhanden. Kein `NightreignHelper`-Prozess mehr
aktiv (letzte Pruefung vor Abschluss dieses Berichts: 0 Treffer).

## Artefakt

`dist\NightreignHelper.exe`, 59.233.161 Byte, SHA-256
`51F694986D11CA1DED16B6170D552C89579C0E5C67192D78F68FFFF063E8BFC9` - beide
Werte gegen die im Auftrag genannten (aus T-322h) nachgemessen und
identisch. In diesem Lauf **nicht neu gebaut**, nur verwendet und gehasht.
Kein UPX im PATH dieser Maschine (`which upx`: kein Treffer) - unveraendert
gegenueber allen bisherigen Laeufen, A-031 bleibt bedingungslos nicht
ausgeloest.

## Blocker

Keiner. Alle fuenf Ablaufschritte bestanden, keine offene rote Auflage.

## Risiken

- **Maschinenweite Instanzsperre** (`nrplanner/singleinstance.py`) bleibt
  unveraendert ein Risiko fuer parallel angesetzte Rollen, die dieselbe
  `dist/`-EXE anfassen (T-285-Befund). In diesem Lauf nicht eingetreten, weil
  laut Auftrag niemand parallel lief und `Get-Process` das vor Beginn
  bestaetigte.
- Der reale Spielstand wird trotz umgelenktem `APPDATA` gelesen (siehe
  "Gepruefte Umgebung") - rein lesend, dokumentiertes Verhalten, kein neuer
  Befund, aber ein wiederkehrender Punkt, den kuenftige `clean-room`-Laeufe
  wieder beobachten werden.
- Keine echte Isolierung (Konto/VM/Container) auf dieser Maschine verfuegbar
  - unveraendert seit allen bisherigen Laeufen.

## Ungeprueft

- Neues Benutzerkonto, VM, Container - auf dieser Maschine nicht verfuegbar.
- Echter Windows-Neustart fuer Schritt 4 - nur vollstaendiges Prozessende
  geprueft.
- SmartScreen-Dialog - nicht ausgeloest, da die EXE lokal kopiert und nicht
  aus dem Internet heruntergeladen wurde (kein "Mark of the Web").
- Ob die kurze Ladezeit beim Update (3,7 s) sich bei einem tatsaechlichen
  `EXTRACT_VERSION`-Sprung anders verhaelt - in diesem Lauf war die Version
  zwischen Testabzug und Code identisch (15), ein echter Migrationsfall war
  damit nicht Teil dieses Nachweises.
- Deinstallation/Downgrade/Zuruecksetzen - nicht Teil dieses Auftrags
  (kein Installer vorhanden, "Uninstalling means deleting the folder and
  the cache" laut README - nicht eigens nachvollzogen).

## An `developer`

Keine neuen Befunde am Anwendungscode. Die Statuszeile "N relics ..., M
stored builds" zaehlt zwei verschiedene Dinge (Spielstand-Loadouts vs.
QSettings-Builds dieses Programms) unter einem gemeinsamen Satz - das hat in
diesem Lauf zu keiner Fehlinterpretation gefuehrt, ist aber als Lesehinweis
fuer kuenftige Berichte festgehalten, kein Fehler.

## An `power-user`

Ausgangspunkt: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\
NightreignHelper.exe`, 59.233.161 Byte, SHA-256
`51F694986D11CA1DED16B6170D552C89579C0E5C67192D78F68FFFF063E8BFC9` - nicht
loeschen, nicht neu bauen. Installation ausschliesslich nach README
("Install", Z. 26-40): Datei herunterladen/kopieren und starten, SmartScreen
mit "More info" -> "Run anyway" bestaetigen, beim Erststart auf die eigene
NIGHTREIGN-Installation zeigen falls die Automatik sie nicht findet.
Instanzsperre ist maschinenweit - vor dem eigenen Start
`Get-Process NightreignHelper` pruefen, es darf 0 Treffer geben.

## An `director`

**Empfehlung: freigeben.** Alle fuenf Ablaufschritte bestanden, Update-Pfad
1.15.0 -> 1.16.0 inklusive der drei Sonderfall-Namen und beider Neustarts
belegt, keine offene rote Auflage in `docs/legal/AUFLAGEN.md` (Stand
`1f51485`, 16.09., Gesamtampel GELB - seither keine neue Runde).

1. Kein `.gitignore`-Nachtrag noetig (`dist/` bereits erfasst, keine neue
   Ablage ausserhalb).
2. Keine offene rote Auflage - dieser Lauf war nicht durch `AUFLAGEN.md`
   gesperrt.
3. Kein Ablaufkonflikt in diesem Lauf - niemand parallel angesetzt,
   `Get-Process` vor und nach dem Lauf mit 0 Treffern bestaetigt.
4. Kein Tag-Vorschlag (nicht `notes`-Modus - `notes` fuer 1.16.0 lief bereits
   in T-322j).
5. Einschraenkungen fuer die Freigabeentscheidung: keine echte Isolierung
   (Konto/VM), kein echter OS-Neustart, SmartScreen nicht ausgeloest, echter
   `EXTRACT_VERSION`-Sprung nicht Teil dieses Nachweises (siehe "Ungeprueft").
