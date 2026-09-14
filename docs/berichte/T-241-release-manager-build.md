STATUS: erledigt
AUFTRAG: T-241c - Artefakt 1.10.0 bauen (release-manager, Modus `build`)
GELESEN: docs/tasks/T-241.md (vollstaendig); docs/legal/AUFLAGEN.md (vollstaendig, 321 Zeilen, selbst nachgeprueft - siehe "Pflichtlektuere" unten); docs/release/ROLLOUT.md:1-320 (Ablaufplan Zeilen 269-286 und die Vorlaufbefunde zur Nicht-Reproduzierbarkeit Zeilen 255-267); nrplanner/__init__.py (nur gelesen, Version bereits 1.10.0); NightreignHelper.spec (Kopf, Versionsquelle, `datas`); requirements.txt, requirements-dev.txt; .gitignore (`.venv/`, `dist/` beide erfasst)
GEÄNDERT: `dist/NightreignHelper.exe` (neu gebaut, zwei volle Laeufe); ausserhalb des Repositories: `.venv/` neu angelegt (fehlte auf diesem Rechner vollstaendig, siehe Befund unten) und aus den gepinnten `requirements.txt`/`requirements-dev.txt` befuellt; Scratchpad-Kopie des ersten Baus (`…\scratchpad\NightreignHelper_build1.exe`) als Vergleichsbeleg. Kein Commit, kein Code, kein Anwendungscode angefasst.
ANNAHMEN: keine ausser der im Auftrag benannten (Version 1.10.0 ist bereits gesetzt, developer-Arbeit vor diesem Lauf, nur gelesen).
NÄCHSTER: T-241d (`clean-room` + `qa-engineer` + `power-user` parallel am Artefakt)
BLOCKIERT DURCH: nichts fuer diesen Bau. Keine Auflage steht auf ROT mit Status `offen` (siehe unten). Kein Release, kein Push, kein Tag in diesem Lauf.

---

# T-241c - Bau 1.10.0

## Ganz oben

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.083.369 Byte (56,35 MiB) - Ergebnis von Lauf 2, siehe unten |
| **SHA-256** | `314CA35C9AFA9BD71C6FAE9928BC0E1E4ABDBE19814BBB099CCA11A04A3930BD` |
| **Commit** | `9e8933d51f80adec89fb1be24bae299c6912c1bf` (Branch `docs/audit-and-advisor-design`) |
| **Dauer** | Lauf 1: 41 s. Lauf 2 (echter Kaltstart, `build/`+`dist/` vorher geloescht): 38 s |
| **UPX** | nicht im `PATH` (`where upx`: kein Treffer, exit 1) - `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`check_licences.py`** | `OK`, exit 0 - alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Pflichtlektuere: `docs/legal/AUFLAGEN.md` selbst geprueft

Volltext gelesen (321 Zeilen, Stand nach dem T-210-Pruefungslauf vom 12.09.). Kein Eintrag der gesamten Tabelle (A-001 bis A-036) traegt Ampel ROT mit Status `offen`:
- **A-010** ist ROT, aber ausdruecklich "sperrt nicht mehr" - vom Nutzer zurueckgestellt (02.09., ins Register nachgezogen 09.09.).
- **A-020, A-033** (die frueher sperrenden Punkte) sind erfuellt bzw. abgenommen.
- **A-025** (GRAU, Weitergabe der EXE) ist entschieden (FORTSETZEN, 09.09.) und sperrt ohnehin nur das Release, nicht den Bau - hier irrelevant, weil der Auftrag ausdruecklich "kein Merge, kein GitHub-Release, keine Weitergabe" ausschliesst.

Damit ist `build` nicht gesperrt. Waehrend des Laufs war `docs/legal/AUFLAGEN.md` als geaendert markiert (paralleler `compliance-agent`-Lauf, T-241a) - nicht angefasst, nur gelesen.

## Befund: `.venv` fehlte vollstaendig

Vor dem ersten Schritt (`.venv\Scripts\python.exe scripts/check_licences.py`) zeigte sich: kein `.venv`-Verzeichnis im Repo-Wurzelverzeichnis (`Get-ChildItem -Force` bestaetigt, kein versteckter Ordner uebersehen). `.venv/` ist korrekt in `.gitignore` erfasst - das ist kein Repo-Fehler, sondern eine fehlende lokale Werkzeugumgebung auf diesem Rechner zum Zeitpunkt dieses Laufs.

System-Python (`C:\Users\Daniel\AppData\Local\Programs\Python\Python312\python.exe`, 3.12.10) hatte zwar alle sechs Pakete bereits installiert, aber PyInstaller dort in **6.22.1** statt der in `requirements.txt` gepinnten **6.21.0** - deshalb nicht verwendet. Stattdessen `.venv` neu angelegt (`python -m venv .venv`, `pip install -r requirements.txt -r requirements-dev.txt`, 48,8 s) und damit exakt die gepinnten Versionen hergestellt (`pyinstaller --version` → `6.21.0` bestaetigt). Das ist Werkzeug-/Build-Umgebung, keine Abhaengigkeitsauswahl - keine Version wurde geaendert.

**Risiko fuer den Director:** ein frischer Checkout auf einem dritten Rechner ohne vorbereitetes `.venv` scheitert am selben Punkt, wenn dort kein System-Python mit den passenden Paketen bereitsteht. Der Ablaufplan (`ROLLOUT.md:279`) setzt ein existierendes `.venv` stillschweigend voraus.

## Ausgangsstand

- Vor dem ersten Bau: `git status --porcelain` zeigte `M docs/legal/AUFLAGEN.md` (paralleler `compliance-agent`-Lauf T-241a, ausdruecklich nicht anzufassen). Nach dem zweiten Bau: `M README.md` (paralleler `technical-writer`-Lauf T-241b) - AUFLAGEN.md nicht mehr geaendert markiert, offenbar zwischenzeitlich committet/zurueckgesetzt durch die parallele Rolle. Keine der beiden Dateien ist Eingabe des Builds (`NightreignHelper.spec` bindet weder `docs/` noch `README.md` ein) - die Nicht-Sauberkeit des Baums betrifft das Artefakt nicht, wird hier trotzdem gemeldet, wie die Rollenregel verlangt.
- Werkzeuge: Windows 11 Pro 10.0.26200 x64, Python 3.12.10 (neu angelegtes `.venv`), PyInstaller 6.21.0, PySide6 6.11.1 (aus `requirements.txt`).

## Bau, zwei volle Laeufe

Beide Male `build/` und `dist/` vorher vollstaendig geloescht (echter Kaltstart, kein Cache-Wiederverwendung - ein erster Versuch ohne Loeschen zeigte in 1 s "checking Analysis/PYZ/PKG" statt eines echten Neubaus und wurde verworfen).

| | Lauf 1 | Lauf 2 |
|---|---|---|
| `rc` | 0 | 0 |
| Dauer | 41 s | 38 s |
| Groesse | 59.082.416 Byte | 59.083.369 Byte |
| SHA-256 | `05323B50B4787EDE767349E0D884E8EE5F17DCC3DD7C1259629E3D30DDA96FE1` | `314CA35C9AFA9BD71C6FAE9928BC0E1E4ABDBE19814BBB099CCA11A04A3930BD` |

**Nicht bit-identisch** - kein neuer Befund, deckt sich mit der in `ROLLOUT.md:255-267` dokumentierten Ursache: `cmp` zeigt die erste Abweichung bei **Byte 273** (PE-Kopf, Baustempel), `cmp -l` zaehlt 13.468.580 abweichende Bytes von rund 59 Mio - Folge der Modulreihenfolgen-Vertauschung im `Analysis-00.toc`, nicht inhaltlicher Natur. Warnungsdatei (`warn-NightreignHelper.txt`) beide Male 37 Zeilen, ausschliesslich "missing module named"-Eintraege fuer plattform-/bedingt importierte Module (`pwd`, `grp`, `posix`, `resource`, `fcntl`, `termios`, `olefile`, `numpy`, `cffi`, `defusedxml`, `zstandard.backend_rust`, Java/VMS/Winreg-Zweige von `platform`) - keine `ERROR`-Zeile, keine Deprecation, keine unerklaerte Warnung.

Artefakt aus Lauf 2 bleibt in `dist/`; Lauf 1 liegt als Vergleichsbeleg im Scratchpad.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Frischer Rechner ohne vorbereitetes `.venv` und ohne passenden System-Python scheitert am ersten Schritt - siehe Befund oben. Betrifft nicht dieses Artefakt, aber jeden kuenftigen Bau-Lauf auf einer neuen Maschine.
- Nicht bit-identischer Bau (PE-Baustempel + Modulreihenfolge) - unveraendert, dokumentierte Ursache, kein Hinweis auf Manipulation.
- Kein UPX auf diesem Bau-Wirt.

## Ungeprueft

- Windows ARM64, Windows 8.1/aelter, Linux/macOS - kein Ziel laut `CLAUDE.md`.
- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung - das ist T-241d, nicht dieser Lauf.
- Ob der GitHub-Actions-Runner dasselbe `.venv`-Problem haette (dort wird die Umgebung pro Lauf frisch aufgesetzt, also vermutlich nicht betroffen - nicht nachgepruft, weil kein CI-Lauf ausgeloest wurde).

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` / `T-241d` (Ausgangspunkt)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.083.369 Byte (56,35 MiB)
- **SHA-256:** `314CA35C9AFA9BD71C6FAE9928BC0E1E4ABDBE19814BBB099CCA11A04A3930BD`
- **Versionsressource:** 1.10.0 (aus `nrplanner/__init__.py`, ungeprueft am Fenstertitel - kein Rauchtest in diesem Lauf, Auftrag verlangt ihn nicht)
- Fuer den Update-Test gegen 1.9.0: SHA-256 `A2180D5DB3A2B1B1AAF88028C6E7A1429087596E58EC3757469FD234E1366EF3` (T-174, 09.09.2026).
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, `APPDATA` - Testabzug kopieren, nicht darauf zeigen (`CLAUDE.md`).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu `clean-room`/`qa-engineer`/`power-user` - kein Release-Votum, das bleibt an A-025 und den Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis:
1. `.venv` fehlte auf diesem Rechner vollstaendig und wurde neu angelegt - siehe Befund oben. Kein `.gitignore`-Nachtrag noetig (`.venv/` und `dist/` bereits erfasst).
2. Kein Tag-Vorschlag - das ist `notes` (T-241e), nicht dieser Modus.

---

# Rebuild 0e1269f

**Auftrag:** T-241 Abschnitt T-241c, Rebuild nach QA-257-Fix. Version bleibt 1.10.0; das Artefakt vom 08:03 (Bau oben, Commit `9e8933d`) wurde nie weitergegeben.

## Pflichtlektuere: `docs/legal/AUFLAGEN.md`

Vor Buildbeginn geprueft: HEAD-Stand `83fdcdd` enthaelt `docs/legal/AUFLAGEN.md` unveraendert seit Commit `2730906` ("T-241a Auflagen GRUEN fuer lokalen Bau 1.10.0") — kein neuerer Lauf hat die Datei seither angefasst (`git log -1 -- docs/legal/AUFLAGEN.md`). Die Bewertung aus dem ersten Bau gilt unveraendert: kein Eintrag der Tabelle (A-001 bis A-036) traegt Ampel ROT mit Status `offen`. A-010 (ROT) ist ausdruecklich zurueckgestellt, A-020/A-033 erfuellt, A-025 (Weitergabe) betrifft diesen Bau nicht — Auftrag schliesst Weitergabe ausdruecklich aus. `build` ist nicht gesperrt.

## Ganz oben

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.082.953 Byte (56,35 MiB) — Ergebnis von Lauf 2, siehe unten |
| **SHA-256** | `473E109DFE32DE9982D9A21BA8FA0C04851DC188F6644EC9C4E792B767FC7283` |
| **Commit** | `83fdcdd77d1c3149aa91b021c079370549586a4e` (Branch `docs/audit-and-advisor-design`); Code-Stand `0e1269f` ("fix(model): Exklusivgruppe zaehlt genau einmal (QA-257)"), `83fdcdd` ist eine Doku-Commit darueber |
| **Dauer** | Lauf 1: 37 s. Lauf 2 (echter Kaltstart, `build/`+`dist/` vorher geloescht): 36 s |
| **UPX** | nicht im `PATH` (`where upx`: kein Treffer, exit 1) — `upx=True` im `.spec` bleibt wirkungslos, wie in jedem vorherigen Bau |
| **`check_licences.py`** | `OK`, exit 0 — alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Ausgangsstand

`git status --porcelain` vor dem ersten Schritt: leer, sauberer Arbeitsstand. `.venv` liegt aus dem vorigen Lauf bereits vor (`python --version` 3.12.10, `pyinstaller --version` 6.21.0 — deckt sich mit den gepinnten Versionen aus `requirements.txt`/`requirements-dev.txt`; nicht neu angelegt, kein erneuter `pip install`). Werkzeuge sonst unveraendert: Windows 11 Pro 10.0.26200 x64, PySide6 6.11.1.

## Bau, zwei volle Laeufe

Beide Male `build/` und `dist/` vorher vollstaendig geloescht (echter Kaltstart).

| | Lauf 1 | Lauf 2 |
|---|---|---|
| `rc` | 0 | 0 |
| Dauer | 37 s | 36 s |
| Groesse | 59.081.952 Byte | 59.082.953 Byte |
| SHA-256 | `B471D23D7BF960AF1EF1868B51FFC0231ABACB4F5935B5850F60C2C84BEAB5E2` | `473E109DFE32DE9982D9A21BA8FA0C04851DC188F6644EC9C4E792B767FC7283` |

**Nicht bit-identisch** — deckt sich mit dem im ersten Bau dokumentierten Befund (`ROLLOUT.md:255-267`): `cmp` zeigt die erste Abweichung bei **Byte 273** (PE-Kopf, Baustempel), 13.468.512 von rund 59 Mio Bytes weichen ab. Kein neuer Befund. Warnungsdatei (`warn-NightreignHelper.txt`) beide Male 37 Zeilen, ausschliesslich Erklaertext und "missing/excluded module named"-Eintraege (u. a. `_frozen_importlib`, `pwd`, `grp`, `posix`, `resource`, `fcntl`, `termios`) — keine `ERROR`-Zeile, keine unerklaerte Warnung, identisch zum ersten Bau.

Artefakt aus Lauf 2 bleibt in `dist/`; Lauf 1 liegt als Vergleichsbeleg im Scratchpad dieser Sitzung.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Nicht bit-identischer Bau (PE-Baustempel + Modulreihenfolge) — unveraendert, dokumentierte Ursache, kein Hinweis auf Manipulation.
- Kein UPX auf diesem Bau-Wirt — unveraendert.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung, QA/Power-User-Verifikation des QA-257-Fix am Artefakt — das ist T-241d, nicht dieser Lauf.

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` / `T-241d` (Ausgangspunkt)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.082.953 Byte (56,35 MiB)
- **SHA-256:** `473E109DFE32DE9982D9A21BA8FA0C04851DC188F6644EC9C4E792B767FC7283`
- **Versionsressource:** 1.10.0 (aus `nrplanner/__init__.py`, ungeprueft am Fenstertitel — kein Rauchtest in diesem Lauf)
- Dieses Artefakt ersetzt das vom 08:03 (SHA `314CA35C…`), das nie weitergegeben wurde — bei der Pruefung dieses hier verwenden.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, `APPDATA` — Testabzug kopieren, nicht darauf zeigen (`CLAUDE.md`).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu `clean-room`/`qa-engineer`/`power-user` — kein Release-Votum, das bleibt an A-025 und den Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis: keine neuen Punkte gegenueber dem ersten Bau. Das Artefakt vom 08:03 (SHA `314CA35C…`) ist damit ueberholt und sollte nicht mehr verwendet werden.

---

# Rebuild 1b36238

**Auftrag:** T-241c, zweiter Rebuild. Anlass: AK-272 Textfix (Klammerzusatz aus Exklusivgruppen-Warnung entfernt), Version bleibt 1.10.0 unveraendert. Gleicher Ablauf wie die zwei vorstehenden Laeufe; ein Lauf genuegt — Nicht-Bit-Identitaet ist bereits zweimal dokumentiert (Byte-273-PE-Baustempel, Modulreihenfolge). Kein Commit, kein Programmstart in diesem Lauf. Niemand laeuft parallel (`git status` vor und nach dem Bau leer).

## Pflichtlektuere: `docs/legal/AUFLAGEN.md`

Vor Buildbeginn geprueft: letzter Commit auf der Datei ist unveraendert `2730906` ("T-241a Auflagen GRUEN fuer lokalen Bau 1.10.0"), HEAD (`1b36238`) hat sie seither nicht angefasst. Bewertung aus den beiden vorigen Bauten gilt unveraendert: kein Eintrag der Tabelle (A-001 bis A-036) traegt Ampel ROT mit Status `offen`. A-010 (ROT) bleibt zurueckgestellt, A-020/A-033 erfuellt, A-025 (Weitergabe) betrifft diesen Bau nicht — der Auftrag schliesst Weitergabe ausdruecklich aus. `build` ist nicht gesperrt.

## Ganz oben

| | |
|---|---|
| **Pfad** | `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe` |
| **Groesse** | 59.083.751 Byte (56,35 MiB) |
| **SHA-256** | `11F5EECD3BE4DBC2583AD1DCA82DDA0F78D54F84B205A4AB6F060F028792158` |
| **Commit** | `1b36238609c0da450c0bfa3ca945ab49f0029602` ("fix(model): AK-272 - Klammerzusatz aus Exklusivgruppen-Warnung entfernen"), Branch `docs/audit-and-advisor-design`, HEAD zum Zeitpunkt dieses Laufs |
| **Dauer** | 37 s (echter Kaltstart, `build/`+`dist/` vorher geloescht — beide waren bereits leer/nicht vorhanden) |
| **UPX** | nicht im `PATH` (`where upx`: kein Treffer, exit 1) — unveraendert |
| **`check_licences.py`** | `OK`, exit 0 — alle drei Pflichtdateien und alle sechs Bibliotheken erfasst |

## Ausgangsstand

`git status --porcelain` vor dem Schritt: leer, sauberer Arbeitsstand — HEAD entspricht exakt dem beauftragten Stand `1b36238` (`git log -1` bestaetigt). `.venv` liegt aus den vorigen Laeufen vor: `pyinstaller --version` → `6.21.0` (gepinnte Version aus `requirements.txt`), Python 3.12.10 — nicht neu angelegt. Werkzeuge sonst unveraendert: Windows 11 Pro 10.0.26200 x64, PySide6 6.11.1.

## Bau, ein Lauf

| | Lauf |
|---|---|
| `rc` | 0 |
| Dauer | 37 s |
| Groesse | 59.083.751 Byte |
| SHA-256 | `11F5EECD3BE4DBC2583AD1DCA82DDA0F78D54F84B205A4AB6F060F028792158` |

Zweiter Lauf entfallen (Auftrag: "ein Lauf genuegt — Nicht-Bit-Identitaet ist dokumentiert"). Warnungsdatei (`warn-NightreignHelper.txt`) 37 Zeilen — gleiche Anzahl wie in beiden Vorlaeufen; keine `ERROR`- oder `Deprecation`-Zeile (`grep -iE "error|deprecat"` liefert keinen Treffer).

Dieses Artefakt ist gegenueber dem Rebuild `0e1269f` (SHA `473E109D…`) nicht bit-identisch erwartbar — dieselbe dokumentierte Ursache (PE-Baustempel + Modulreihenfolge, `ROLLOUT.md:255-267`) gilt weiter, hier nicht erneut per `cmp` verglichen, da der Zwei-Lauf-Vergleich in diesem Auftrag entfaellt.

## Blocker

Keiner fuer diesen Bau.

## Risiken

- Nicht bit-identischer Bau gegenueber fruehen Bauten (PE-Baustempel + Modulreihenfolge) — unveraendert, dokumentierte Ursache, kein Hinweis auf Manipulation.
- Kein UPX auf diesem Bau-Wirt — unveraendert.
- Nur ein Lauf in diesem Auftrag: die interne Reproduzierbarkeit dieses konkreten Artefakts (zwei Laeufe desselben Commits, identisch bis auf Baustempel) wurde hier nicht erneut nachgewiesen, sondern aus den beiden Vorlaeufen uebernommen.

## Ungeprueft

- Clean-Room-Installation, Update-Pfad, Rauchtest mit Datenumlenkung, Verifikation des AK-272-Fix am Artefakt — das ist T-241d, nicht dieser Lauf.
- Fensterstart/Programmstart — Auftrag verlangt ausdruecklich keinen Programmstart in diesem Lauf.

## An `developer`

Keine neuen Befunde im Anwendungscode.

## An `power-user` / `T-241d` (Ausgangspunkt)

- **Pfad:** `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\dist\NightreignHelper.exe`
- **Groesse:** 59.083.751 Byte (56,35 MiB)
- **SHA-256:** `11F5EECD3BE4DBC2583AD1DCA82DDA0F78D54F84B205A4AB6F060F028792158`
- **Versionsressource:** 1.10.0 (aus `nrplanner/__init__.py`, unveraendert; ungeprueft am Fenstertitel — kein Rauchtest in diesem Lauf)
- Dieses Artefakt ersetzt den Rebuild `0e1269f` (SHA `473E109D…`) — bei der Pruefung dieses hier verwenden.
- Drei Umlenkungen zwingend beim Start: `NIGHTREIGN_SETTINGS_ORG`, `LOCALAPPDATA`, `APPDATA` — Testabzug kopieren, nicht darauf zeigen (`CLAUDE.md`).

## An `director`

**Empfehlung: freigeben mit benannter Einschraenkung** (fuer den Weiterlauf zu `clean-room`/`qa-engineer`/`power-user` — kein Release-Votum, das bleibt an A-025 und den Nutzerauftrag "keine Weitergabe" gebunden).

Zu entscheiden/zur Kenntnis: keine neuen Punkte gegenueber den beiden vorigen Bauten. Das Artefakt aus dem Rebuild `0e1269f` (SHA `473E109D…`) ist damit ueberholt und sollte nicht mehr verwendet werden.
