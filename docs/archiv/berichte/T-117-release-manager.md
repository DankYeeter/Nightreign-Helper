STATUS: erledigt
AUFTRAG: T-117 / A-033 — die zwoelf bestehenden Releases nachruesten (release-manager)
GELESEN: docs/tasks/T-117.md, docs/release/RELEASE_TEXT.md (vollstaendig, insb. Variant B Zeile 77-108 und die Notes Zeile 112-129), docs/release/ROLLOUT.md (vollstaendig, als Kontext zum Ablaufplan der uebrigen Modi — fuer diesen `notes`-Lauf nicht handlungsrelevant), CHANGELOG.md (im gesamten Repository nicht vorhanden, per Volltextsuche `find . -iname "CHANGELOG*"` geprueft — nichts zu lesen), dist/NightreignHelper-notices.zip (Inhaltspruefung per Python `zipfile`), GitHub-API-Antworten zu allen zwoelf Releases (vor und nach dem Upload)
GEÄNDERT: keine Repository-Datei. Veraendert wurden ausschliesslich GitHub-Release-Metadaten (Assets und Beschreibungstexte) der zwoelf bestehenden Releases v1.0.0 bis v1.7.1 im Remote `github.com/DankYeeter/Nightreign-Helper` (Kategorie privat, deklariertes Remote stimmt mit `git remote -v` ueberein, keine Firmen-Grenze beruehrt). Temporaere Arbeitsdateien unter `T-117/` im Scratchpad: `backfill.py`, `v1.0.0-old.md`, `<tag>-notes.md` (12 Stueck) — reine Hilfsdateien, nicht Teil des Projekts.
ANNAHMEN: Backfill-Datum fuer alle zwoelf Releases ist `2026-09-08`, weil alle Uploads in einer Sitzung am heutigen Tag liefen (`docs/release/RELEASE_TEXT.md` Zeile 127-129 nennt das ausdruecklich einen erwartbaren Zufall, kein hartkodiertes Datum). Keine weiteren Annahmen; der Auftrag zitierte GOAL.md/state.md woertlich, beides war damit nicht separat zu lesen.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Schritt 0 — Faehigkeitsprobe "immutable releases"

Gepruefte Quelle: `gh api repos/DankYeeter/Nightreign-Helper/releases --paginate --jq '.[] | "\(.tag_name)\t\(.immutable)\t\(.id)"'`. GitHub liefert pro Release ein eigenes `immutable`-Feld. Ergebnis fuer alle zwoelf Releases: `immutable: false`. Kein Abbruch. (Ergaenzend geprueft: Repository nicht archiviert (`archived: false`), einziges aktives Ruleset betrifft den Branch `main`, keine Release-Regel.)

## Schritt 1 — Inhalt des Hinweispakets

`dist\NightreignHelper-notices.zip`, 46 448 B (Dateigroesse per `Get-Item` bestaetigt), 9 Eintraege (per Python `zipfile.infolist()` geprueft, nicht nur `unzip -l`, da der Windows-Pfad `vendor/Paramdex/NOTICE` in manchen Listing-Tools abgeschnitten dargestellt wird):

- `LICENSE` (1430 B)
- `THIRD_PARTY.md` (8255 B)
- `licenses/GPL-3.0.txt` (35147 B)
- `licenses/LGPL-3.0.txt` (7652 B)
- `licenses/Pillow-LICENSE.txt` (78016 B)
- `licenses/pycryptodome-LICENSE.rst` (2987 B)
- `licenses/texture2ddecoder-LICENSE.txt` (1083 B)
- `licenses/zstandard-LICENSE.txt` (1511 B)
- `NOTICE` (1958 B)

Neun Eintraege, Groesse stimmt exakt (46 448 B). Kein Abbruch.

**Abweichung, kein Abbruchgrund, aber ein Befund:** Der Auftrag (und `THIRD_PARTY.md` selbst, Zeile "and [`vendor/Paramdex/NOTICE`](vendor/Paramdex/NOTICE)") beschreibt den neunten Eintrag als `vendor/Paramdex/NOTICE`. Im tatsaechlich gebauten Zip liegt die Datei flach im Wurzelverzeichnis als `NOTICE`, nicht unter dem Unterpfad `vendor/Paramdex/`. Inhalt, Groesse und Zaehlung stimmen — nur der Pfad im Archiv weicht von dem in `THIRD_PARTY.md` verlinkten Pfad ab, wodurch der interne Link `[vendor/Paramdex/NOTICE](vendor/Paramdex/NOTICE)` innerhalb des Pakets ins Leere zeigt. Das ist Packaging-Verhalten des bereits gebauten Artefakts (`dist\NightreignHelper-notices.zip`, ausserhalb dieses `notes`-Laufs — kein Bau erlaubt) bzw. eine Textstelle in `THIRD_PARTY.md`. Siehe "An `developer`" unten.

## Schritte 2-5 — Nachruestung aller zwoelf Releases

Fuer jedes der zwoelf Releases `v1.0.0`, `v1.1.0`, `v1.2.0`, `v1.3.0`, `v1.3.1`, `v1.3.2`, `v1.4.0`, `v1.5.0`, `v1.5.1`, `v1.6.0`, `v1.7.0`, `v1.7.1` wurde ausgefuehrt:

1. `gh release upload <tag> dist\NightreignHelper-notices.zip` — Asset unter demselben, versionsunabhaengigen Dateinamen fuer alle zwoelf (T-112-Vorgabe eingehalten).
2. Bestehenden Beschreibungstext per `gh api repos/.../releases/tags/<tag>` gelesen (raw JSON, nicht `gh release view`, um keine Normalisierung durch die CLI zu riskieren).
3. Variant B (Zeile 77-108 aus `docs/release/RELEASE_TEXT.md`, wortgleich uebernommen, `<BACKFILL_DATE>` durch `2026-09-08` ersetzt) an den Anfang gesetzt, gefolgt von einer Leerzeile, dann der unveraenderte Bestandstext.
4. `gh release edit <tag> -F <notes-datei>` — nur die Beschreibung geaendert, `--draft`/`--prerelease`/`--tag`/`--target` nicht angefasst (alle zwoelf waren vorher bereits `draft:false`, `prerelease:false`, per API-Abfrage vor dem Lauf bestaetigt).
5. Asset-Liste per `gh api repos/.../releases/tags/<tag> --jq '[.assets[].name] | join(", ")'` **nach** dem Upload erneut abgefragt.

**Nachweis, Asset-Liste nach dem Upload, zwoelf Zeilen (Backfill-Datum in jeder Beschreibung: 2026-09-08):**

```
v1.0.0: NightreignHelper-notices.zip, NightreignHelper.exe
v1.1.0: NightreignHelper-notices.zip, NightreignHelper.exe
v1.2.0: NightreignHelper-notices.zip, NightreignHelper.exe
v1.3.0: NightreignHelper-notices.zip, NightreignHelper.exe
v1.3.1: NightreignHelper-notices.zip, NightreignHelper.exe
v1.3.2: NightreignHelper-notices.zip, NightreignHelper.exe
v1.4.0: NightreignHelper-notices.zip, NightreignHelper.exe
v1.5.0: NightreignHelper-notices.zip, NightreignHelper.exe
v1.5.1: NightreignHelper-notices.zip, NightreignHelper.exe
v1.6.0: NightreignHelper-notices.zip, NightreignHelper.exe
v1.7.0: NightreignHelper-notices.zip, NightreignHelper.exe
v1.7.1: NightreignHelper-notices.zip, NightreignHelper.exe
```

Ergaenzend geprueft: `NightreignHelper-notices.zip` hat auf allen zwoelf Releases die Groesse 46 448 B (identisch zum lokal geprueften Original — kein verstuemmelter Upload). Jede der zwoelf Beschreibungen beginnt jetzt mit der Zeile `**Notice package added after the fact.** The licence notice package` (per `.body | head -1` auf allen zwoelf Releases stichprobenartig, tatsaechlich vollstaendig, gegengeprueft). Der jeweils alte Text steht danach unveraendert weiter — beispielhaft an `v1.0.0` (vorher nur ein "Full Changelog"-Link) und `v1.7.1` (mehrabsaetziger Release-Text) vollstaendig gegengelesen; in beiden Faellen ist der Bestandstext byte-identisch unterhalb des neuen Blocks erhalten.

Kein Release ist fehlgeschlagen. Alle zwoelf tragen jetzt Asset und Text.

## Grenzen eingehalten

- Kein neues Release, kein Tag, kein Bau — `dist\NightreignHelper.exe` unangetastet, `v1.8.0` nicht beruehrt.
- Kein EXE-Asset entfernt — jedes der zwoelf Releases traegt weiterhin sein urspruengliches `NightreignHelper.exe` (Groesse je Release ungleich, das ist erwartungsgemaess: es ist jeweils der ursprungliche Build dieser Version, nicht das v1.8.0-Artefakt).
- Beschreibungen nur ergaenzt, kein Zeichen des Bestandstexts entfernt oder umformuliert.
- Kein Anwendungscode, keine Workflow-Datei, kein `CHANGELOG.md` angefasst — `git status` im Arbeitsverzeichnis vor und nach dem Lauf: "nothing to commit, working tree clean", keine einzige lokale Datei veraendert.

## An `developer`

Der interne Verweis in `THIRD_PARTY.md` (Zeile "and [`vendor/Paramdex/NOTICE`](vendor/Paramdex/NOTICE)...") zeigt auf einen Pfad, den das gebaute Paket `dist\NightreignHelper-notices.zip` nicht hat — dort liegt die Datei flach als `NOTICE` im Wurzelverzeichnis. Wer die Datei aus dem entpackten Hinweispaket heraus liest und dem Link folgt, findet nichts unter `vendor/Paramdex/`. Entweder der Packaging-Schritt (Ziel des `developer`/Build-Konfiguration — je nachdem, wo der Pfad gesetzt wird) sollte die Verzeichnisstruktur nachbilden, oder `THIRD_PARTY.md` sollte den flachen Pfad `NOTICE` nennen. Beides ist Anwendungscode- bzw. Content-Aenderung, liegt also nicht in meiner Zustaendigkeit — ich melde nur. Kein Blocker fuer diesen Lauf, da Inhalt/Groesse/Zaehlung der neun Eintraege exakt wie im Auftrag beschrieben vorlagen.

## An `power-user`

Nicht einschlaegig fuer diesen Lauf — es wurde nichts gebaut oder installiert, nur bestehende GitHub-Releases um Assets/Text ergaenzt. Kein neuer Ausgangspunkt fuer eine Installationssitzung.

## An `director`

- **Empfehlung: freigeben.** Alle zwoelf bestehenden Releases (`v1.0.0`-`v1.7.1`) tragen jetzt das Hinweispaket als Asset und den vorgeschriebenen Variant-B-Text am Anfang ihrer Beschreibung. Nach Massgabe von T-117/C-004 ist damit A-033 erfuellt und der fortdauernde LGPL-3.0/BSD-3-Verstoss fuer alle abrufbaren Kopien beendet — die 25 bereits heruntergeladenen Kopien bleiben wie im Auftrag festgehalten unheilbar (GPL-3.0 § 8, letzter Absatz), das ist keine Frage an mich.
- Kein neuer Tag-Vorschlag noetig — dieser Lauf hat keinen neuen Commit und kein neues Release erzeugt, nur Metadaten der zwoelf Bestandsreleases geaendert.
- Keine fehlenden `.gitignore`-Eintraege festgestellt (kein Build-Artefakt neu abgelegt).
- Offene Entscheidung, nicht meine: der oben gemeldete `vendor/Paramdex/NOTICE`-vs-`NOTICE`-Pfadbefund an `developer` — bitte einplanen, ist kein Release-Blocker, aber ein kleiner Content-Fehler im bereits oeffentlichen Hinweispaket.
- Rechtliches ausserhalb C-004: keines gefunden.
