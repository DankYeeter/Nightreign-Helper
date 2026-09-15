STATUS: erledigt
AUFTRAG: T-249 - Artefakt 1.10.1 bauen (release-manager, Modus `build`)
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 446 Zeilen, selbst nachgeprueft - siehe unten); docs/berichte/T-241-release-manager-build.md (vollstaendig, als Vorlage fuer den Ablauf); nrplanner/__init__.py (Version 1.10.1 bestaetigt); NightreignHelper.spec (unveraendert gegenueber T-241); .gitignore (`dist/`, `build/` beide erfasst)
GEAENDERT: `dist/NightreignHelper.exe` (neu gebaut, ein Lauf). Kein Commit, kein Code, kein Anwendungscode angefasst.
ANNAHMEN: keine ausser der im Auftrag benannten (Version 1.10.1 ist bereits gesetzt, developer-Arbeit vor diesem Lauf, nur gelesen). Ein Lauf statt zwei, wie im Auftrag verlangt - Nicht-Bit-Identitaet ist in T-241 bereits dreifach dokumentiert (Byte-273-PE-Baustempel, Modulreihenfolge).
NAECHSTER: qa-engineer / power-user (clean-room), sofern vom director angestossen. Kein Programmstart in diesem Lauf.
BLOCKIERT DURCH: nichts fuer diesen Bau - siehe Pflichtlektuere unten.

---

# T-249 - Bau 1.10.1

## Kontraktblock

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.089.432 Byte (56,36 MiB) |
| **SHA-256** | `DFDEADC42475707241B6764904E7A791A536FB25B65494460F2CEA560676A558` (64 Zeichen, `sha256sum` und `certutil -hashfile … SHA256` stimmen ueberein) |
| **Commit** | `dde2efcb16f1d8cd5b81b2ff9374531f4f13175a` ("chore(release): Version auf 1.10.1 angehoben"), Branch `docs/audit-and-advisor-design` |
| **Dauer** | 1 Min 15 s (`time pyinstaller …`) |
| **UPX** | nicht im `PATH` (`where upx`: "Could not find files for the given pattern(s)", exit 1) - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`check_licences.py`** | `OK`, exit 0 - alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md` selbst geprueft

Volltext gelesen (446 Zeilen, Stand nach dem T-241a-Auflagen-Lauf vom 14.09. und der QA-243-Aufloesung). Kein Eintrag der gesamten Tabelle (A-001 bis A-036) traegt Ampel ROT mit Status `offen`:
- **A-010** ist ROT, aber ausdruecklich "sperrt nicht mehr" - vom Nutzer zurueckgestellt (02.09., Abnahme 09.09.).
- **A-020, A-033** sind erfuellt/abgenommen bzw. ausgefuehrt mit noch ausstehender Nutzer-Abnahme des Bestands - beides sperrt laut Register nicht den Bau.
- **A-025** (GRAU, Weitergabe der EXE) ist entschieden (FORTSETZEN, 09.09.) und sperrt ohnehin nur das Release, nicht den Bau - der Auftrag T-249 schliesst Weitergabe ohnehin aus (kein Commit, kein Programmstart durch mich).
- Der eigens fuer "lokal gebaut, nicht weitergegeben" gefuehrte Abschnitt (Z. 325-445) kommt fuer den heutigen Zweck auf **GRUEN**: nur A-032 (Schwellenwaechter, kein Ereignis) greift, alles andere ist Repo- oder Weitergabe-gebunden.

Damit ist `build` nicht gesperrt. `git log -1 -- docs/legal/AUFLAGEN.md` zeigt keinen Aenderungs-Commit nach HEAD `dde2efc` - die Datei war waehrend dieses Laufs nicht in Bearbeitung.

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, sauberer Arbeitsstand. HEAD `dde2efc` entspricht exakt dem beauftragten Stand ("Version auf 1.10.1 angehoben"). `.venv` liegt aus fruehreren Laeufen vor: Python 3.12.10, `pyinstaller --version` -> `6.21.0` (gepinnte Version aus `requirements.txt`), PySide6 6.11.1 - unveraendert, nicht neu angelegt.

## Befund: `dist/` konnte nicht komplett geloescht werden - qa-engineer haelt eine Fensterinstanz

Der Auftrag nennt ausdruecklich: "kein Programmstart (der qa-engineer haelt die Fensterinstanz)". `tasklist` bestaetigt vor und nach dem Bau zwei laufende `NightreignHelper.exe`-Prozesse (PID 16064, 10580), unveraendert durch diesen Lauf.

Der erste Schritt zum echten Kaltstart (`rm -rf dist build`) scheiterte mit "Device or resource busy" auf `dist` (das Verzeichnis selbst, nicht eine einzelne Datei - vermutlich ein offener Verzeichnis-Handle, z. B. weil ein Prozess dort sein Arbeitsverzeichnis hat). `build/` liess sich problemlos loeschen. `dist/` war zu diesem Zeitpunkt bereits **leer** (`ls -la` zeigte keine Datei) - die vom qa-engineer gehaltene Instanz laeuft folglich nicht von der aktuell in `dist/` liegenden Datei, sondern von einer eigenen Kopie ausserhalb dieses Pfads. `rm -f dist/NightreignHelper.exe` bestaetigte das (`rc=0`, da die Datei bereits nicht existierte).

**Abweichung vom Referenzablauf (T-241):** Statt `dist/` zu loeschen und neu anzulegen, wurde direkt in das bereits leere `dist/`-Verzeichnis gebaut (PyInstaller legt `build/` und den Inhalt von `dist/` ohnehin neu an). Das ist inhaltlich ein Kaltstart (keine Cache-Wiederverwendung, `build/` war komplett geloescht, `dist/` war leer), nur das Verzeichnis-Objekt selbst wurde nicht neu angelegt. Die laufenden qa-engineer-Prozesse wurden durch den Bau nicht beruehrt (Tasklist vor/nach identisch).

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 |
| Dauer | 1 Min 15 s |
| Groesse | 59.089.432 Byte |
| SHA-256 | `DFDEADC42475707241B6764904E7A791A536FB25B65494460F2CEA560676A558` |

Zweiter Lauf entfallen, wie im Auftrag verlangt ("Gleicher Ablauf wie deine drei Laeufe" - dort ist Nicht-Bit-Identitaet bereits dreifach belegt: Byte-273-PE-Baustempel, Modulreihenfolgen-Vertauschung im `Analysis-00.toc`, `ROLLOUT.md:255-267`). Hier nicht erneut per zweitem Lauf/`cmp` nachgewiesen.

Warnungsdatei (`build/NightreignHelper/warn-NightreignHelper.txt`) 37 Zeilen - gleiche Anzahl wie in allen drei T-241-Bauten; `grep -iE "error|deprecat"` liefert 0 Treffer.

Dauer 1 Min 15 s liegt deutlich ueber den 36-41 s der T-241-Laeufe. Einzige erkennbare Ursache: Antivirus-/Indexer-Scan auf den neu geschriebenen `build/`-Baum oder allgemeine Rechnerlast durch den parallel laufenden qa-engineer-Prozess (2 offene NightreignHelper.exe-Instanzen) - nicht weiter eingegrenzt, da der Auftrag keinen zweiten Lauf zum Vergleich vorsieht. Kein Hinweis auf einen fehlerhaften Build (Groesse und Warnungszahl passen zu den Vorlaeufen).

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Dauer fast doppelt so lang wie in T-241 (1 Min 15 s statt 36-41 s), Ursache nicht eingegrenzt (siehe oben) - fuer den director als Beobachtung, nicht als Fehlerbefund.
- `dist/`-Verzeichnis liess sich nicht als Ganzes loeschen (Verzeichnis-Handle offen, vermutlich durch einen anderen Prozess) - fuer kuenftige Baulaeufe zu beachten: ein aktiver `NightreignHelper.exe`-Prozess kann `dist/` blockieren, auch wenn er nicht aus dem aktuellen `dist/`-Inhalt laeuft.
- Kein UPX auf diesem Bau-Wirt - unveraendert gegenueber allen bisherigen Laeufen.
- Nur ein Lauf: die interne Reproduzierbarkeit dieses konkreten Artefakts wurde in diesem Auftrag nicht erneut per Zwei-Lauf-Vergleich nachgewiesen, sondern aus T-241 (drei Vorlaeufe, alle nicht bit-identisch mit dokumentierter Ursache) uebernommen.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung - nicht Teil dieses Auftrags (`kein Programmstart`).
- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- Ob die laengere Bauzeit ein wiederholbares Muster ist oder ein Einzelfall dieses Laufs - kein Vergleichslauf ohne parallele qa-engineer-Instanz durchgefuehrt.

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` (Ausgangspunkt, falls angefordert)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.089.432 Byte (56,36 MiB)
- **SHA-256:** `DFDEADC42475707241B6764904E7A791A536FB25B65494460F2CEA560676A558`
- **Versionsressource:** 1.10.1 (aus `nrplanner/__init__.py`, ungeprueft am Fenstertitel - kein Rauchtest in diesem Lauf, Auftrag verlangt ihn nicht)
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen (`CLAUDE.md`).
- Achtung: parallel laeuft moeglicherweise noch eine qa-engineer-Instanz (zwei `NightreignHelper.exe`-Prozesse zum Zeitpunkt dieses Laufs) - vor eigenem Start pruefen, nicht verwechseln.

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu qa-engineer/power-user - kein Release-Votum, das bleibt an A-025 und den Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis:
1. `dist/`-Verzeichnis war waehrend des Baus nicht vollstaendig loeschbar (Verzeichnis-Handle offen durch einen anderen Prozess) - Build wurde trotzdem sauber in das leere Verzeichnis geschrieben, siehe Befund oben. Kein Blocker, aber ein Hinweis fuer parallele Laeufe.
2. Bauzeit fast doppelt so lang wie in den drei T-241-Laeufen - Ursache nicht eingegrenzt, kein Fehlerbefund.
3. Kein `.gitignore`-Nachtrag noetig (`dist/`, `build/` bereits erfasst).
