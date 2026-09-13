# Nightreign-Helper

*Nur Projektfakten. Teamregeln stehen in `~/.claude/CLAUDE.md`,
`~/.claude/agents/_rahmen.md` und `~/.claude/commands/director.md` und werden
hier nicht wiederholt. Jeder Auftrag verweist auf diese Datei.*

**Repo-Kategorie:** privat nach Herkunft (kein Firmencode, nur Daniels
Account), **das GitHub-Repository ist öffentlich** (`gh repo view`: PUBLIC,
06.09.2026) — alles Committete ist für jeden lesbar (NH-002). Erlaubtes Remote
ausschliesslich `https://github.com/DankYeeter/Nightreign-Helper.git`; der
`archivist` prüft `git remote -v` vor jedem Push, bei Abweichung wird nicht
gepusht, sondern gemeldet. Arbeitsrechtliche Grenze, Vorrang vor allem.

## Projektsprache

| wo | Sprache |
|---|---|
| Oberfläche des Programms | **Englisch** — Abnahmekriterium A8, ohne Ausnahme |
| Code, Bezeichner, Docstrings, Kommentare | Englisch |
| Commit-Messages | Deutsch, Conventional-Commits-Präfix englisch |
| Doku im Repo (`docs/`, Aufträge, Berichte, Befunde) | Deutsch |
| `README.md`, `docs/anleitung/`, `CHANGELOG.md`, Release-Texte | Englisch |

Umlaute in Doku und Commits umschrieben (`ae`, `oe`, `ue`, `ss`).

## Zielsystem

Windows 10/11 x64. Linux und macOS nie geprüft, kein Ziel. Artefakt:
PyInstaller-Einzeldatei ohne Installer.

## Testbefehl

```
pytest -n auto      # volle Suite, ~135 s (seriell 840 s); 12.09.2026: 1789 passed, 9 skipped
pytest <datei>      # gezielt, OHNE -n (1,2 s statt 4,0 s)
```

`-n auto` ist bewusst keine Voreinstellung in `pytest.ini`.

## Datenverzeichnisse und Umlenkung

Das Programm schreibt an drei Orten. `.claude/hooks/enforce-data-redirect.ps1`
(PreToolUse) sperrt jeden Programm- oder Messlauf ohne diese Umlenkung:

| Variable | ausgewertet in | umlenken auf |
|---|---|---|
| `NIGHTREIGN_SETTINGS_ORG` | `nrplanner/favourites.py` | eigener Wert je Auftrag, z. B. `DankYeeterT-###` |
| `LOCALAPPDATA` | `nrplanner/paths.py` | eigenes Testverzeichnis |
| `APPDATA` | `nrplanner/shortcut.py` | eigenes Testverzeichnis |

Der Nutzer hat 309 Relikte und rund 110 gespeicherte Builds: lesen ja,
schreiben nie. Positive Pfadauflösung (`paths.cache_dir()` zurücklesen) hält
als Nachweis; Abwesenheit hält nicht (QA-237: die Überlagerung ist
Claude-weit). Der Spielstand ist read-only und darf gelesen werden.

**Fester Testabzug:** `C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug`
(841 Dateien, 20 812 293 Bytes, `EXTRACT_VERSION` 11, gebaut von 1.9.0; spart
110 s je Lauf). In das umgelenkte `LOCALAPPDATA` **kopieren**, nicht darauf
zeigen. Nicht unter `%LOCALAPPDATA%`, nicht im Projektbaum. Ungültig, sobald
`EXTRACT_VERSION` über 11 steigt — der erste betroffene Lauf ersetzt die
Vorlage und vermerkt es in `docs/plan-restarbeiten.md`.

## Verbotene Zugriffe

- Nie in Spielstand oder Spielinstallation schreiben; kein Mod, kein
  Save-Editor.
- Kein Netzwerkzugriff im Anwendungscode, keine Telemetrie, keine Wiki-Daten.
- Keine Bildschirmabzüge (NH-002); Bildnachweise nur per `PrintWindow` aus dem
  Programmfenster.
- Keine Spieldaten ins Repository (`nightreign_data.json`, Symbole);
  `NightreignHelper.spec` zählt genau zwei Quellen, ein Wächtertest hält das.

## Besonderheiten

- Projektregeln tragen das Präfix `NH-`; `docs/plan-restarbeiten.md` führt
  Restarbeiten und Regelpflege.
- Register `qa/findings.md`, `security/findings.md`: NH-003-Wächter
  (`tests/`) prüft die Tabellenform bestehender Zeilen; neue Einträge nur
  anhängen.
