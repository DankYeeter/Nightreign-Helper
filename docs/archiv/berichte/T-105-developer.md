STATUS: erledigt
AUFTRAG: T-105 - SEC-009: die Lieferkette des veroeffentlichten EXE
GELESEN: docs/tasks/T-105.md, .github/workflows/release.yml, .github/workflows/tests.yml (Grep), security/findings.md (nur das im Auftrag zitierte Fragment)
GEÄNDERT: .github/workflows/release.yml
ANNAHMEN: keine (Auftrag war vollstaendig; Zitate aus GOAL.md und docs/state.md waren im Auftrag enthalten)
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Umgesetzt

**Fähigkeitsprobe (Schritt 0):** `gh api repos/actions/checkout/git/ref/tags/v4 --jq .object.sha` lieferte
`11d5960a326750d5838078e36cf38b85af677262`. Freigabe zum Fortfahren.

**1. Alle drei `uses:`-Zeilen in `.github/workflows/release.yml` auf 40-stellige Commit-SHAs gepinnt**
(geprüft per Grep — es gibt keine weiteren `uses:`-Zeilen in dieser Datei):

| Action | vorher | Pin | entspricht Tag | abgerufen |
|---|---|---|---|---|
| `actions/checkout` | `@v4` | `11d5960a326750d5838078e36cf38b85af677262` | `v4.4.0` | 2026-09-07 |
| `actions/setup-python` | `@v5` | `a26af69be951a213d495a4c3e4e4022e16d87065` | `v5.6.0` | 2026-09-07 |
| `softprops/action-gh-release` | `@v2` | `3bb12739c298aeb8a4eeaf626c5b8d85266b0e65` | `v2.6.2` | 2026-09-07 |

Alle drei Tag-Refs zeigten laut `gh api .../git/ref/tags/<tag>` direkt auf ein Objekt vom Typ `"commit"`
(kein `"tag"`-Zwischenobjekt) — die im Auftrag beschriebene Dereferenzierung über
`git/tags/<sha>` war in keinem der drei Fälle nötig. Der konkrete Patch-Tag hinter jedem
Major-Tag wurde über `gh api repos/<owner>/<repo>/tags --jq '.[] | select(.commit.sha=="<sha>")'`
ermittelt, um den lesbaren Versionskommentar zu befüllen.

Form in der Datei: `uses: owner/repo@<sha> # vX.Y.Z`, exakt wie im Auftrag verlangt.

**2. SHA-256-Prüfsumme:** neuer Schritt `Compute SHA-256 checksum` nach `Build`, vor dem Release-Schritt.
`shell: pwsh` (== Default-Shell des `windows-latest`-Runners, hier explizit benannt, damit die
Aussage im Nachweis eindeutig ist):

```powershell
$hash = (Get-FileHash -Path dist/NightreignHelper.exe -Algorithm SHA256).Hash
"$hash  NightreignHelper.exe" | Out-File -FilePath dist/NightreignHelper.exe.sha256 -Encoding ascii -NoNewline
```

`dist/NightreignHelper.exe.sha256` geht als zweites Element in `files:` (Block-Skalar statt
Komma-String, weil `softprops/action-gh-release` `files:` zeilenweise erwartet).

Prüfbefehl für den Nutzer unter Windows, ohne Zusatzwerkzeug (für `technical-writer`):
- PowerShell: `Get-FileHash .\NightreignHelper.exe -Algorithm SHA256`
- Eingabeaufforderung: `certutil -hashfile NightreignHelper.exe SHA256`

Der Nutzer vergleicht den ausgegebenen Wert von Auge gegen den Inhalt der mitgelieferten
`.sha256`-Datei (Groß-/Kleinschreibung ist bei Hex-Hashes irrelevant, wie unten belegt).

## Nachweise (alle Befehle mit Ausgabe, siehe Tool-Aufrufe dieses Laufs)

- **YAML parst:** `python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/release.yml', encoding='utf-8'))"` → kein Fehler, `YAML OK`.
- **Jeder Pin einzeln gegen `gh api` gegengeprüft** (nicht generisch, drei getrennte Aufrufe gegen den
  konkreten Patch-Tag, nicht gegen den bewegten Major-Tag):
  - `gh api repos/actions/checkout/git/ref/tags/v4.4.0 --jq .object.sha` → `11d5960a326750d5838078e36cf38b85af677262` (== Pin)
  - `gh api repos/actions/setup-python/git/ref/tags/v5.6.0 --jq .object.sha` → `a26af69be951a213d495a4c3e4e4022e16d87065` (== Pin)
  - `gh api repos/softprops/action-gh-release/git/ref/tags/v2.6.2 --jq .object.sha` → `3bb12739c298aeb8a4eeaf626c5b8d85266b0e65` (== Pin)
- **Prüfsummenzeile lokal gegen eine Testdatei ausgeführt** (Windows PowerShell 5.1 via `powershell -Command`,
  im Scratchpad-Unterverzeichnis `T-105/`, danach entfernt): Datei `dist/NightreignHelper.exe.sha256` entstand
  mit Inhalt `873FAB42D7D63B3FDBA9ECD629E45354B78835477335F91B5624CA90600F08F3  NightreignHelper.exe`, und der Wert
  stimmt exakt (case-insensitive) mit dem direkten `Get-FileHash`-Aufruf und mit
  `certutil -hashfile ... SHA256` überein. **Lücke:** getestet wurde mit `powershell` (Windows PowerShell 5.1),
  nicht mit `pwsh` (PowerShell 7/Core, Default-Shell des Runners) — `pwsh` war auf diesem Rechner nicht
  installiert. `Get-FileHash` und `Out-File` sind eingebaute, plattformidentische Cmdlets in beiden
  Versionen; der Workflow selbst läuft hier nicht (siehe Auftrag), das ist also kein Beleg für exaktes
  Verhalten unter `pwsh`, sondern die bestmögliche lokale Näherung.
- **`git diff --stat` zeigt genau die erlaubte Datei:** `.github/workflows/release.yml | 16 ++++++++++++----`, sonst nichts.
- **`tests.yml` bewusst nicht angefasst**, per Auftrag.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (keine)
- [x] Nachweis in der benannten Testumgebung (Windows) erbracht wie oben; Workflow selbst nicht auslösbar (kein CI-Lauf im Auftrag verlangt)
- [ ] Kein Linter im Projekt für YAML/Workflows konfiguriert → Punkt entfällt (keine Lücke, kein Ersatzprüfung nötig)
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] Scope eingehalten: nur `.github/workflows/release.yml`, keine neue Datei unter `scripts/` nötig, kein Umbau des Bauvorgangs, keine PyInstaller-Optionen, keine neue Abhängigkeit
- [x] Doku: keine eigene Doku-Datei angefasst (nicht meine Datei); relevante Fakten (Prüfbefehle) hier für `technical-writer` benannt

## An director

- **SEC-009 wie beauftragt geschlossen:** Action-Pins + SHA-256-Prüfsumme sind umgesetzt, Codesignatur und
  `--require-hashes` bewusst ausgelassen (Restrisiko-Entscheid vom 02.09.2026 unverändert).
- **Fund, nicht behoben (auftragsgemäß):** `tests.yml` hat an den Zeilen 28/30 dieselbe Pin-Schwäche
  (`actions/checkout@v4`, `actions/setup-python@v5`, bewegliche Major-Tags). Kein Release-Pfad, also
  außerhalb dieses Auftrags — aber dieselbe Befund-Eigenschaft wie SEC-009, nur an anderer Stelle. Empfehlung:
  eigener kleiner Folgeauftrag, falls SEC-009s Muster projektweit geschlossen werden soll (L-006).
- **Erster Release-Lauf steht noch aus:** dieser Auftrag ändert die Workflow-Datei, aber kein Tag wurde
  gepusht — der beschriebene "erste EXE über die abgesicherte Kette" entsteht erst beim nächsten
  `git tag vX.Y.Z && git push origin vX.Y.Z`. Das ist außerhalb meines Auftrags, aber relevant für die
  A2-Abnahme: die Pins und der Prüfsummen-Schritt sind bisher nur statisch (YAML-Parse, SHA-Abgleich,
  lokaler Shell-Test), nicht durch einen tatsächlichen CI-Lauf verifiziert.
- **Wartungshinweis für die Pins:** SHA-Pins auf `actions/checkout`, `actions/setup-python` und
  `softprops/action-gh-release` frieren die Version ein — Dependabot/Renovate aktualisieren SHA-Pins zwar
  automatisch (falls konfiguriert), sonst muss ein Mensch künftig manuell nachziehen. Kein Blocker, nur zur
  Kenntnis, falls das Projekt später automatisierte Action-Updates einführen will.
