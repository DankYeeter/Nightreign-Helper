STATUS: teilweise - Kernschritte (2-4) durch Fremdprozess blockiert, nicht bestanden und nicht nachgewiesen
AUFTRAG: T-285a - clean-room-Lauf gegen dist/NightreignHelper.exe 1.13.1 mit
Update-Weg (release-manager, Modus `clean-room`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster Abschnitt
"Auflagen vor der Veroeffentlichung 1.13.1", Stand `1f51485`, 16.09.2026:
Gesamtampel GELB, **keine Auflage auf ROT, keine sperrt Bau/Eigenlauf oder
diesen Pruef-Lauf**); docs/release/ROLLOUT.md Z. 287-322 ("Ablaufplan fuer
den `clean-room`-Lauf"); README.md "Install" (Z. 62-91); docs/release/
RELEASE_BODY.md (vollstaendig, insbesondere "How to install" Z. 46-58);
docs/berichte/T-282-release-manager-build.md (Artefaktnachweis 1.13.1);
docs/berichte/T-265-release-manager-cleanroom.md (Methodik-Vorlage: UI
Automation, Registry-Beweisstellen); nrplanner/singleinstance.py (maschinenweite
Instanzsperre, fixer Schluessel `NightreignHelper-running-copy`,
`nrdata/extract.py:84` EXTRACT_VERSION=12)
GEAENDERT: nichts im Repository (`git status` vor und nach diesem Lauf clean).
Ausserhalb: eigenes Scratchpad `...\0c1b1951.../scratchpad\T-285a\` (cleanroom/
local/roaming) angelegt, benutzt, vollstaendig geloescht (`ls` nach dem Lauf:
Ordner nicht mehr vorhanden); Registryschluessel `HKCU\Software\DankYeeterT-285a`
angelegt (leer, kein Nutzerdatum, nur durch QSettings-Initialisierung vor dem
Sperrabbruch), vollstaendig geloescht (`Test-Path` -> `False`). Dieser Bericht
neu angelegt.
ANNAHMEN: keine Umgehung der Instanzsperre versucht (kein `Stop-Process` auf
die fremden PIDs 21136/26972 - das waere ein Eingriff in die parallele
power-user-/notes-Sitzung und ausdruecklich nicht mein Auftrag). Gewartet statt
abgebrochen, weil der Auftrag "parallel mit eigener Umlenkung" ausdruecklich
vorsieht - nach rund 28 Minuten Wartezeit ohne Aenderung als Blocker gewertet,
nicht laenger verzoegert.
NAECHSTER: erneuter `clean-room`-Versuch, sobald die parallele Sitzung beendet
ist (keine neue Rolle noetig, derselbe Auftrag T-285a).
BLOCKIERT DURCH: parallele Sitzung (power-user/notes-Lauf) haelt die
maschinenweite Instanzsperre; Schritte 1 (Ausfuehrung), 2, 3, 4 des
Ablaufplans dadurch nicht durchfuehrbar.

---

# T-285a - clean-room 1.13.1

## Kontraktblock

| | |
|---|---|
| **Modus** | `clean-room` |
| **Artefakt** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.201.630 Byte (gemessen, `ls`) - deckt sich mit T-282 |
| **SHA-256 (nachgemessen)** | `71E8202980BA528119815C75818757668EA956480A918C0236D1C8E420E67E1C` (`certutil`) - identisch mit dem im Auftrag genannten und in T-282 gefuehrten Wert |
| **Vorversion fuer Update-Pfad** | `NightreignHelper-1.11.0.exe`, 59.105.391 B, SHA-256 `F23EB0F784665A8C018C19F353AD114E9809061033076311DCDF21DBB916E8E0` (nachgemessen, identisch mit T-265-Beleg) - **aelter als die im Auftrag genannte 1.13.0-Sicherung und bevorzugt eingesetzt**, weil im Scratchpad einer fremden Session vorhanden und Herkunft/Hash gegen `docs/berichte/T-265-release-manager-build.md:96` bestaetigt |
| **Urteil dieses Laufs** | **nicht freigeben-faehig anhand dieses Laufs** - die entscheidenden Schritte sind ungeprueft, nicht bestanden |

## Geprufte Umgebung

**Kein neues Konto, keine VM, kein Container** - wie in allen bisherigen
Laeufen nicht verfuegbar. Isolierung vorbereitet: eigenes leeres Verzeichnis
ausserhalb des Repos, `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-285a`,
`LOCALAPPDATA`/`APPDATA` auf Wegwerfpfade im Scratchpad, alles in derselben
Kommandozeile wie der Start. `PATH` nicht geleert, `.venv` bleibt technisch
erreichbar (nicht benutzt). Diese Einschraenkungen sind wie in fruheren
Laeufen **nicht isoliert**, aber vorher schon bekannt.

**Neu und schwerer als in fruheren Laeufen:** Dieselbe Maschine, dasselbe
Windows-Konto - und diesmal **tatsaechlich eine zweite, echte Sitzung parallel
aktiv** (zwei Prozesse `dist\NightreignHelper.exe`, PID 21136 seit 17:38:08 und
PID 26972 seit 17:38:09, letzterer mit Fenstertitel). Die Instanzsperre
(`nrplanner/singleinstance.py:32`, `QSharedMemory("NightreignHelper-running-copy")`)
ist **global fuer die Maschine**, unabhaengig von `NIGHTREIGN_SETTINGS_ORG`
oder `LOCALAPPDATA`/`APPDATA` - das war bisher nur aus dem Code und aelteren
Berichten bekannt (T-241, T-265: "Risiko"), **in diesem Lauf erstmals real
beobachtet**: mein eigener Start (`NightreignHelper.exe` aus dem umgelenkten
Testverzeichnis, Vorversion 1.11.0) erzeugte einen Prozess (PID 5140), der
ohne Fenster und ohne Fehlermeldung sofort wieder beendet war - genau das in
T-265 vorhergesagte Verhalten "kein Fenster, kein Fehlertext, der Test misst
nichts".

## Ergebnis je Schritt

**0. Isolierung** - bestanden (mit den oben genannten, bereits bekannten
Einschraenkungen).

**1. Nur die EXE in ein leeres Verzeichnis, Installation nach README** -
**teilweise**. Datei-Platzierung bestanden: 1.11.0 in ein leeres
Scratchpad-Verzeichnis kopiert (Hash gegenpgeprueft, siehe Kontraktblock).
**Ausfuehrung fehlgeschlagen**: der Start wurde durch die fremde, laufende
Instanz sofort abgefangen (siehe oben) - die Anleitung selbst wurde nicht
gegen ein lauffaehiges Programm gepruft.

**2. Starten, schreibende Aktion, beenden, neu starten** - **nicht pruefbar**.
Grund: Instanzsperre durch parallele Sitzung, siehe oben. Nach dem
fehlgeschlagenen Start ~28 Minuten gewartet (drei Wartefenster: 6, 9, 9
Minuten mit Polling `Get-Process -Name NightreignHelper`), die zwei fremden
Prozesse blieben durchgehend aktiv (`StartTime` unveraendert 17:38:08/09,
zuletzt gegengeprueft 18:06:52). Kein Fremdprozess beendet, kein zweiter
Versuch unternommen.

**3. Update-Weg 1.11.0 -> 1.13.1, Kern des Laufs** - **nicht pruefbar**, aus
demselben Grund. Weder 1.11.0 noch 1.13.1 konnten in dieser Sitzung
tatsaechlich gestartet werden; kein Build gespeichert, keine Sonderzeichen-
Namen erzeugt, `__schema` nicht abgelesen.

**4. Zweitstart nach Neustart der Umgebung** - **nicht pruefbar**, aus
demselben Grund; Schritt 2/3 sind Voraussetzung.

**5. Aufraeumen** - bestanden. Scratchpad `...\scratchpad\T-285a\` vollstaendig
geloescht (Ordner nach dem Lauf nicht mehr vorhanden, `ls` auf das
uebergeordnete Verzeichnis gegengeprueft). Registryschluessel
`HKCU\Software\DankYeeterT-285a` (leer - nur die von QSettings beim
Initialisieren angelegte, wertlose Struktur, kein Nutzerdatum) vollstaendig
geloescht (`Test-Path` -> `False`). Kein eigener Prozess mehr aktiv (PID 5140
war schon vor dem Aufraeumen beendet). Die beiden fremden Prozesse (parallele
Sitzung) wurden **nicht angefasst** - nicht mein Eingriffsbereich.

## Textvergleich README.md / RELEASE_BODY.md "How to install" (unabhaengig von der Ausfuehrung geprueft)

Beide Texte wurden gelesen und gegeneinander gehalten (dies ist der Massstab
laut Auftrag; Abweichung = Befund gegen den Text, nicht Anlass zum Abkuerzen):

- README "Install" (Z. 62-91): "Download `NightreignHelper.exe` ... und run
  it. No Python, no installer, no admin rights." Danach Ordnersuche,
  Steam-Pruefung, Ersteinrichtungsdauer.
- RELEASE_BODY.md "How to install" (Z. 46-58): dieselbe Kernaussage, zusaetzlich
  Checksummen-Empfehlung, expliziter SmartScreen-Hinweis ("More info" ->
  "Run anyway") und "No installer, no admin rights, no Python" wortgleich in
  Schritt 3.
- Beide Texte widersprechen sich nicht; RELEASE_BODY ist die ausfuehrlichere
  Fassung (zusaetzlich Checksumme, SmartScreen), README die knappere. Kein
  Befund gegen den Text - **aber**: dieser Vergleich ersetzt nicht die
  tatsaechliche Ausfuehrung nach der Anleitung, die in diesem Lauf nicht
  stattfand (Schritt 1 oben).

## Artefakt

Wie im Kontraktblock. Vom `release-manager` in diesem Lauf **nicht neu
gebaut**, nur der bestehende `dist/NightreignHelper.exe`-Hash nachgemessen
und gegen T-282 bestaetigt.

## Blocker

- **Parallele Sitzung haelt die maschinenweite Instanzsperre** - verhindert
  jede Ausfuehrung von `NightreignHelper.exe` in dieser Sitzung, solange sie
  laeuft. Kein Blocker fuer das Release selbst (die Sperre ist Absicht,
  `singleinstance.py`), aber ein Blocker fuer **diesen** `clean-room`-Nachweis:
  Schritte 2-4 sind nicht erbracht, damit ist die zentrale Frage des Modus
  ("kommt das Update ohne Datenverlust an") **fuer 1.13.1 unbeantwortet**.
  Zustaendig fuer die Aufloesung: zeitliche Neueinteilung der drei parallelen
  Rollen (nacheinander statt gleichzeitig) - das ist eine Ablaufentscheidung
  des `director`, keine Code-Aenderung.

## Risiken

- Die maschinenweite Instanzsperre (`singleinstance.py:32`) macht echte
  Parallelitaet mehrerer Rollen mit derselben `dist/`-EXE grundsaetzlich
  unmoeglich, nicht nur in diesem Lauf - unveraendert seit T-241/T-265, heute
  aber erstmals **tatsaechlich eingetreten** statt nur dokumentiert.
- Damit bleibt der Update-Pfad 1.11.0 -> 1.13.1 (bzw. 1.13.0 -> 1.13.1) seit
  T-265 (gepruft: 1.11.0 -> 1.12.0) **nicht erneut belegt** - jede
  Codeaenderung an Speicherformat, Registry-Schema oder Migrationslogik
  zwischen 1.12.0 und 1.13.1 ist damit an einem echten Artefakt ungeprueft.

## Ungeprueft

- Schritt 1 (tatsaechliche Ausfuehrung nach README/RELEASE_BODY), Schritt 2
  (schreibende Aktion, Neustart), Schritt 3 (Update-Weg, Sonderzeichen-Namen,
  `__schema`), Schritt 4 (Zweitstart nach Neustart der Umgebung) - alle vier
  durch die parallele Sitzung blockiert, siehe oben.
- Neues Benutzerkonto / VM / Container - wie in jedem bisherigen Lauf nicht
  verfuegbar.
- Verhalten des echten SmartScreen-Dialogs - nicht auszuloesen ohne
  tatsaechlichen Start.
- UPX/A-031: in diesem Lauf nicht erneut geprueft (T-283/T-282 bereits
  "entfaellt" bzw. "nicht im PATH" fuer denselben Baustand).

## An `developer`

Keine neuen Befunde am Anwendungscode. Die Instanzsperre verhaelt sich wie
dokumentiert (`singleinstance.py:32`) - kein neuer Fehler, nur der erste
tatsaechliche Konfliktfall zwischen zwei gleichzeitig beauftragten Rollen.

## An `power-user`

Dieser Lauf konnte **keinen** Ausgangspunkt liefern, der ueber T-282 hinausgeht
- Artefakt unveraendert: `dist\NightreignHelper.exe`, 59.201.630 B, SHA-256
`71E8202980BA528119815C75818757668EA956480A918C0236D1C8E420E67E1C` (siehe
T-282). Falls die parallele Sitzung bereits die des `power-user` selbst war:
bitte in seinem eigenen Bericht vermerken, ob und wie er die schreibenden
Aktionen (Build speichern, Update-Pfad) bereits abgedeckt hat - das koennte
diesen Blocker fuer den Gesamt-Auftrag entschaerfen, auch wenn es diesen
`release-manager`-Lauf selbst nicht mehr nachtraeglich bestehen laesst.

## An `director`

**Empfehlung: nicht freigeben anhand dieses Laufs** - nicht wegen eines
gefundenen Fehlers, sondern weil der Kern des Modus (Update-Pfad, echte
Schreibaktion, Zweitstart) **nicht erbracht** wurde. Frueherer Nachweis
(T-265, 1.11.0 -> 1.12.0) besteht fort, deckt aber Aenderungen bis 1.13.1
nicht ab.

1. Kein `.gitignore`-Nachtrag noetig.
2. Keine offene rote Auflage - dieser Lauf war nicht durch `AUFLAGEN.md`
   gesperrt (Stand `1f51485`, 16.09., Gesamtampel GELB).
3. **Ablaufkonflikt zur Entscheidung vorgelegt:** die drei parallel
   beauftragten Rollen (`release-manager`/`clean-room`, `power-user`,
   `notes`-Lauf) konkurrieren real um dieselbe maschinenweite Instanzsperre.
   Vorschlag: `clean-room` entweder vor oder nach der `power-user`-Sitzung
   einplanen, nicht gleichzeitig - oder mit einer eigenen Kopie der EXE unter
   anderem Prozessnamen arbeiten (das aendert Anwendungscode/Build und ist
   damit Sache des `developer`, keine Ad-hoc-Loesung von mir).
4. Kein Tag-Vorschlag (nicht `notes`-Modus).
