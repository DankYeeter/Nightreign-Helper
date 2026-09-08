# Nightreign-Helper

## Repo-Kategorie

**Kategorie: privat** — das bezieht sich auf die **Herkunft**, nicht auf die
Sichtbarkeit: kein Firmencode, keine Firmendaten, ausschliesslich Daniels
persoenlicher Account. **Das GitHub-Repository selbst ist oeffentlich**
(`gh repo view`: `PUBLIC`, geprueft 06.09.2026). Beides gilt gleichzeitig und
hat schon zu einem gemeldeten Widerspruch gefuehrt. Fuer die Arbeit heisst
das: **alles, was hier committet wird, ist fuer jeden lesbar** — daher
NH-002 (keine Bildschirmabzuege) und die Regel, dass Bildnachweise nur aus
dem Programmfenster stammen.

Erlaubte Remotes: ausschließlich der persönliche GitHub-Account
`github.com/DankYeeter`.

Dieses Projekt enthält keinen Firmencode und keine Firmendaten. Es wird
niemals in ein Firmen-Remote gepusht.

Deklariertes Remote: `https://github.com/DankYeeter/Nightreign-Helper.git`

Der `archivist` prüft vor jedem Push `git remote -v` gegen diese Angabe.
Weichen Remote und Kategorie voneinander ab, wird **nicht** gepusht,
sondern gemeldet. Das ist eine arbeitsrechtliche Grenze und hat Vorrang
vor jeder anderen Regel.

---

## Projektsprache

**Aus der Praxis dieses Repos aufgeschrieben, nicht neu festgelegt**
(Director, 08.09.2026 — bis dahin stand hier nichts, und die Regel fehlte
damit in jedem Auftrag):

| wo | Sprache |
|---|---|
| **Oberflaeche des Programms** | **Englisch** — Abnahmekriterium **A8**, ohne Ausnahme |
| Code, Bezeichner, Docstrings, Kommentare | Englisch |
| Commit-Messages | Deutsch, Conventional-Commits-Praefix englisch (`docs(state): …`) |
| Doku im Repo (`docs/`, Auftraege, Berichte, Befunde) | Deutsch |
| `README.md`, `docs/anleitung/`, `CHANGELOG.md`, Release-Texte | **Englisch** — sie richten sich an die Nutzer |
| Chat mit dem App Designer | Deutsch |

Umlaute werden in Doku und Commits **umschrieben** (`ae`, `oe`, `ue`, `ss`).

## Projektzeilen fuer jeden Auftrag

*Diese Angaben gehoeren laut Director-Definition in **jeden** Auftrag und
stehen in keiner Rollendefinition. Bis zum 08.09.2026 hat der Director sie von
Hand abgeschrieben: 32 Auftragsdateien wiederholen die Scratchpad-Regel, 7 die
Umlenkungen, 4 den Testbefehl. **Ab jetzt genuegt der Verweis auf diesen
Abschnitt** — plus das, was fuer den einzelnen Auftrag davon abweicht.*

### Zielsystem

Windows 10/11 x64. Linux und macOS sind **nie geprueft** und kein Ziel.
Das ausgelieferte Artefakt ist eine PyInstaller-Einzeldatei ohne Installer.

### Testbefehl

```
pytest -n auto      # volle Suite, rund 127 s (seriell 840 s)
pytest <datei>      # eine einzeln genannte Datei OHNE -n; mit -n stiege sie
                    # von 1,2 auf 4,0 s, und genau die verlangt die
                    # Gegenproben-Regel
```

`-n auto` ist **bewusst keine Voreinstellung** in `pytest.ini`.
Stand 08.09.2026: **1257 passed, 9 skipped, 0 failed**. Wer die Suite laufen
laesst, nennt seine Zahl gegen diese.

### Datenverzeichnisse — und die Sperre davor

Das Programm schreibt an **drei** Orten. Wer es zu Test- oder Messzwecken
startet, lenkt **alle drei** um und **weist jede Umlenkung nach**:

| Variable | ausgewertet in | umlenken auf |
|---|---|---|
| `NIGHTREIGN_SETTINGS_ORG` | `nrplanner/favourites.py:25` | eigener Wert je Auftrag, z. B. `DankYeeterT-###` |
| `LOCALAPPDATA` | `nrplanner/paths.py:20` | das eigene Testverzeichnis |
| `APPDATA` | `nrplanner/shortcut.py:44-49` | das eigene Testverzeichnis |

**Der Nutzer hat 309 Relikte und rund 110 gespeicherte Builds im Programm.
Lesen ja, schreiben nie.** In Zyklus 4 und 5 sind auf diesem Weg **drei
Datenverluste** entstanden (QA-195); am 07.09.2026 landete eine Verknuepfung
im echten Start-Menue, weil nur zwei der drei Variablen umgelenkt waren.
**Gelingt ein Nachweis nicht, wird der Lauf abgebrochen und nur das gemeldet.**

Der **Spielstand selbst ist read-only** und darf gelesen werden — er ist die
einzige realistische Datengrundlage.

### Fester Testabzug statt Neubau

```
C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug
```

841 Dateien, 19,8 MB, gebaut von 1.8.0 (`EXTRACT_VERSION` 11). **In das
umgelenkte `LOCALAPPDATA` kopieren**, nicht darauf zeigen lassen — das
Programm schreibt hinein. Spart je Lauf den Neuaufbau des Datenabzugs
(gemessen 107 s bzw. rund 5 min, QA-198).

**Ungueltig**, sobald das Spiel gepatcht wird oder `EXTRACT_VERSION` ueber 11
steigt. Der erste Lauf, dem das passiert, **ersetzt die Vorlage** und vermerkt
es in `docs/plan-restarbeiten.md` (E-1).

**Nicht ins Repository** — er stammt aus der Spielinstallation, NH-002 und
A-003 verbieten das. Er liegt deshalb ausserhalb des Projektbaums, nicht bloss
in `.gitignore`.

### Scratchpad

Der Scratchpad ist **pro Sitzung** segmentiert, **nicht pro Rolle** — jede
gleichzeitig laufende Rolle sieht dieselben Dateien und kann sie loeschen.
Am 07.09.2026 wurde so ein Messbaum mitten im Messstapel geleert, zwei von
sechs Messungen mussten wiederholt werden.

**Jeder Auftrag bekommt ein eigenes Unterverzeichnis, benannt nach seiner
T-Nummer** (`…/scratchpad/T-###/`). Nichts ausserhalb davon anfassen.

### Verbotene Zugriffe

- **Nie** in den Spielstand oder die Spielinstallation schreiben. Der Save ist
  read-only, das Programm ist kein Mod und kein Save-Editor.
- **Kein Netzwerkzugriff** im Anwendungscode, keine Telemetrie, keine
  Wiki-Daten. Das ist ein Nicht-Ziel aus `GOAL.md`.
- **Keine Bildschirmabzuege** (NH-002). Bildnachweise stammen ausschliesslich
  aus dem Programmfenster (`PrintWindow`), weil das Repository oeffentlich ist.
- **Keine Spieldaten ins Repository** — weder `nightreign_data.json` noch
  Symbole. `NightreignHelper.spec` zaehlt genau zwei Quellen auf
  (`nrplanner/data/icon.ico`, `vendor/Paramdex/NR/Defs`); ein Waechtertest
  haelt das fest.
- **`git commit` immer mit Pfad hinter `--`**, nie `-a`, nie `add -A`, nie
  `add .`. Vier Vorfaelle, bei denen fremde Dateien in fremde Commits geraten
  sind; beim vierten wurde die Regel woertlich eingehalten und trotzdem
  gerissen, weil `commit` **ohne** Pfad den ganzen Index nimmt.

### Der Bericht ist Teil des Auftrags

Eine Rolle **mit** Schreibrecht gilt erst als fertig, wenn
`docs/berichte/T-###-<rolle>.md` auf der Platte liegt. Am 08.09.2026 hat der
`power-user` seinen Bericht trotz Schreibrecht nicht abgelegt; der Director
musste ihn von Hand nachtragen.
