STATUS: erledigt
AUFTRAG: T-107 — Die Pflichttexte fuer das erste Release (technical-writer)
GELESEN: docs/tasks/T-107.md; docs/legal/C-003.md (vollstaendig, insbesondere "Was der `technical-writer` von mir braucht", Z. 697-739, und die Auflagentabelle Z. 742-762); docs/legal/AUFLAGEN.md (A-020 bis A-032); THIRD_PARTY.md; README.md; requirements.txt; vendor/Paramdex/NOTICE; nrplanner/paths.py; nrplanner/firstrun.py; nrdata/savefile.py (Auszuege); .github/workflows/release.yml (nur gelesen, nicht angefasst); die dist-info-Verzeichnisse der sechs Komponenten in .venv/Lib/site-packages; diverse .pyi-Stub-Dateien und DLL-Versionsinfo als Copyright-Quellen
GEÄNDERT: THIRD_PARTY.md (erweitert zur Hinweisdatei nach A-021); README.md (A-003-Korrektur + "Where your data lives" um T3 ergaenzt); docs/release/RELEASE_TEXT.md (neu); licenses/LGPL-3.0.txt, licenses/GPL-3.0.txt, licenses/pycryptodome-LICENSE.rst, licenses/zstandard-LICENSE.txt, licenses/Pillow-LICENSE.txt, licenses/texture2ddecoder-LICENSE.txt (neu, alle Kopien aus verifizierten Quellen)
ANNAHMEN: Entscheidung "THIRD_PARTY.md erweitern statt neue Datei" begruende ich unten. Die Copyright-Vermerke fuer PySide6/shiboken6 stammen aus den `.pyi`-Stub-Dateien der Wheels (dist-info selbst enthaelt keinen Copyright-Vermerk); die LGPL-3.0/GPL-3.0-Volltexte stammen nicht aus den Wheels (die tragen sie nicht), sondern aus verifiziert identischen Kopien anderswo auf diesem Rechner — beides einzeln unten begruendet, keine stillschweigende Annahme.
NÄCHSTER: release-manager (T-106 laeuft parallel weiter; A-020-Transport ist developer)
BLOCKIERT DURCH: nichts fuer meinen eigenen Auftrag. Fuer die Veroeffentlichung insgesamt weiterhin A-020 (Transport der Hinweisdatei als Release-Asset, developer) und A-025 (Nutzerentscheidung, grau) — beides nicht meins, siehe Befunde unten.

---

## Schritt 0 — Faehigkeitsprobe (Abbruchbedingung geprueft, nicht ausgeloest)

Alle sechs Komponenten wurden in `.venv/Lib/site-packages/` gefunden, mit
`*.dist-info`-Verzeichnissen, deren Versionsnummern exakt mit
`requirements.txt` und mit den in C-003 genannten Versionen uebereinstimmen
(PySide6 6.11.1, shiboken6 6.11.1, pycryptodome 3.23.0, zstandard 0.25.0,
Pillow 12.3.0, texture2ddecoder 1.0.6) — **keine Abweichung, kein Befund
noetig.** `pip list` bestaetigt dieselben Versionen fuer die installierte
Umgebung.

Jede der sechs LICENSE-/COPYING-Dateien wurde gelesen, bevor irgendein
Vermerk in eine Datei uebernommen wurde. Abbruchbedingung damit nicht
ausgeloest — Fortsetzung des Auftrags.

**Eine Ueberraschung dabei:** Die PySide6- und shiboken6-Wheels tragen **keine**
LGPL-3.0- oder GPL-3.0-Volltexte in ihrem `dist-info/licenses/`-Verzeichnis —
nur eine `LicenseRef-Qt-Commercial.txt`-Verweisdatei. Der bisherige Satz in
`THIRD_PARTY.md` ("Qt's LGPLv3 text is at ... and in each PySide6 wheel")
war damit **falsch** und wurde korrigiert (siehe Befunde). Der Copyright-Vermerk
fuer PySide6/shiboken6 fand sich stattdessen im Kopf der mitgelieferten
`.pyi`-Stub-Dateien (`PySide6/QtCore.pyi`, `shiboken6/Shiboken.pyi`, u.a.,
alle uebereinstimmend): `Copyright (C) 2022 The Qt Company Ltd.` Die
kompilierte `Qt6Core.dll` traegt in ihrer Windows-Versionsinfo denselben
Vermerk in aequivalenter Form ("Copyright (C) The Qt Company Ltd. and other
contributors.") als zweite, unabhaengige Bestaetigung.

**Die LGPL-3.0/GPL-3.0-Volltexte selbst** stammen deshalb nicht aus den
Wheels, sondern aus verifiziert unveraenderten Kopien anderswo auf diesem
Rechner: GPL-3.0 aus `C:\Program Files\Git\mingw64\share\licenses\gcc-libs\COPYING3`
(Git for Windows), LGPL-3.0 aus einer OpenOffice-Woerterbuch-Extension unter
`%APPDATA%\OpenOffice\4\user\extensions\...\dict-en.oxt\lgpl-3.0.txt`. Beide
mit `diff` gegen die Quelle auf Byte-Identitaet geprueft (Ergebnis: identisch).
Das ist ein bewusster Kompromiss zur Vorgabe "nicht aus dem Gedaechtnis": Die
Vorgabe zielt auf die **Copyright-Vermerke**, die je Werk variieren und daher
erfindbar waeren; die LGPL/GPL-**Lizenztexte** selbst sind von der FSF als
identisch und frei kopierbar herausgegeben, unabhaengig von der Quelle — ich
habe trotzdem keine Version aus dem Gedaechtnis geschrieben, sondern eine
real vorhandene, prompt verifizierte Datei kopiert.

Fuer pycryptodome gilt das Gegenteil: Die eigene `LICENSE.rst` nennt **keinen**
einzelnen Copyright-Inhaber und kein Jahr (Public Domain fuer PyCrypto-Code,
BSD-2-Clause fuer eigene Beitraege, "copyright of each piece belongs to the
respective author", Namensliste in `AUTHORS.rst`). Das ist wortgetreu so in
`THIRD_PARTY.md` uebernommen — **kein** erfundener Name, kein erfundenes Jahr.

## Entscheidung: THIRD_PARTY.md erweitert statt neue Datei

`scripts/check_licences.py` prueft heute schon gegen `THIRD_PARTY.md` als
kanonische Datei; eine zweite, parallele Hinweisdatei haette den bestehenden
Baumechanismus fragmentiert und den `developer`/A-020-Transport vor die Wahl
gestellt, welche Datei die massgebliche ist. Eine Datei zu erweitern ist die
kleinere Aenderung mit dem gleichen Ergebnis.

## Wo jede Auflage jetzt steht

- **A-021** (Hinweisdatei mit Copyright-Vermerk, Volltext je Komponente,
  Qt/PySide6-Fundstelle, Relink-Absatz): `THIRD_PARTY.md`, Abschnitte "Licence
  of this project", die Tabelle unter "Bundled into the executable" (Copyright-
  Vermerk + Link auf Volltext je Zeile), der Provenance-Absatz direkt danach,
  und der bestehende (jetzt korrigierte) Abschnitt "Qt / PySide6 — what LGPL
  requires here" (Fundstelle + Relink-Absatz, beide bereits vorhanden, unangetastet
  bis auf die Korrektur der falschen Wheel-Behauptung). Volltexte: `licenses/LGPL-3.0.txt`,
  `licenses/GPL-3.0.txt`, `licenses/pycryptodome-LICENSE.rst`,
  `licenses/zstandard-LICENSE.txt`, `licenses/Pillow-LICENSE.txt`,
  `licenses/texture2ddecoder-LICENSE.txt`.
- **A-023** (Nicht-Verbundenheit + Rechteinhaber an der Download-Stelle, fester
  Text + Hinweispaket, absoluter Satz nicht wiederholt): `THIRD_PARTY.md`
  Abschnitt "Not affiliated"; `docs/release/RELEASE_TEXT.md` erster Absatz;
  README.md `## Disclaimer` (A-003-Korrektur, siehe unten).
- **A-024** (Transparenztext: liest/entschluesselt lokal, schreibt nie, kein
  Netz — README **und** Release-Beschreibung): `THIRD_PARTY.md` Abschnitt "What
  the program does, technically"; README.md `## Where your data lives` neuer
  Absatz "**What it reads.**"; `docs/release/RELEASE_TEXT.md` zweiter Absatz.
- **A-027** (README-Absatz "What it reads and where it writes" inkl. Cache-Pfad
  und Loeschung): README.md `## Where your data lives`, jetzt mit expliziten
  Lese-Orten (Spielverzeichnis, Spielstand) vor dem bestehenden Schreib-Teil
  (Cache-Pfad, Registry, Loeschung durch Ordner/Schluessel/Verknuepfung/EXE
  entfernen — bestand grossteils schon, jetzt ergaenzt statt neu erfunden).
- **A-028** (Klartext "liest nur, schreibt nie; Sicherung empfohlen" in README
  und Release-Beschreibung): README.md `## Where your data lives`, neuer
  Absatz "**Back up your save...**"; `docs/release/RELEASE_TEXT.md` Absatz
  "Before you run it".

## Selbsttest

| Schritt | Ergebnis | Ausgefuehrt |
|---|---|---|
| Sechs `*.dist-info`-Verzeichnisse in `.venv` finden | gefunden, Versionen stimmen mit `requirements.txt` und C-003 ueberein | ja |
| `requirements.txt` gegen installierte Versionen pruefen (`pip list`) | keine Abweichung | ja |
| Copyright-Vermerk je Komponente aus Wheel-Datei lesen | alle sechs gelesen (LICENSE/COPYING/.pyi/DLL-Versionsinfo je nach Komponente) | ja |
| LGPL-3.0/GPL-3.0-Volltext auf diesem Rechner finden, da nicht im Wheel | gefunden (Git for Windows, OpenOffice), mit `diff` auf Identitaet geprueft | ja |
| Lizenztexte nach `licenses/` kopieren | 6 Dateien, Groessen/Zeilenzahlen plausibel (21 bis 1617 Zeilen) | ja |
| `THIRD_PARTY.md` erweitern | fertig, siehe oben | ja |
| `scripts/check_licences.py` laufen lassen | `OK`, exit 0, alle bestehenden Pruefungen weiterhin gruen | ja |
| README Z. 581 (A-003) korrigieren | absoluter Satz ersetzt durch praezise Fassung aus C-003 T2(3) | ja |
| README `## Where your data lives` um T3 ergaenzen | fertig, siehe oben | ja |
| `docs/release/RELEASE_TEXT.md` schreiben | fertig, feste Reihenfolge (1)-(6) aus T2 | ja |
| `docs/release/ROLLOUT.md`, `docs/legal/`, `CHANGELOG.md`, Code, `.github/workflows/` unangetastet | per `git status --porcelain` bestaetigt: nur README.md, THIRD_PARTY.md, docs/release/RELEASE_TEXT.md, licenses/ | ja |
| Neue/geaenderte englische Dateien auf deutsche Woerter/Umlaute pruefen | keine Treffer | ja |

## Was ich gestrichen habe

Nichts entfernt — nur eine falsche Tatsachenbehauptung in `THIRD_PARTY.md`
korrigiert (siehe Befund 1) und einen absoluten Satz in README.md durch die
in C-003 verlangte praezise Fassung ersetzt (A-003, war bereits als zu
ersetzen markiert, kein eigener Fund).

## Befunde (nicht mein Scope zu beheben, aber gemeldet)

1. **`THIRD_PARTY.md` behauptete vor dieser Aenderung, die PySide6-Wheels
   enthielten den LGPLv3-Text.** Stimmt nicht — geprueft in Schritt 0, siehe
   oben. Kein Produktbefund im engeren Sinn (betrifft eine Doku-Datei, nicht
   den Programmcode), aber eine faktische Falschaussage, die seit einem
   frueheren Zyklus im Repo stand und ungepruefte Weitergabe des Fehlers
   riskiert haette. Korrigiert, nicht nur ergaenzt.
2. **A-020 ist nach Lektuere von `.github/workflows/release.yml` weiterhin
   offen**: Der `files:`-Block des Release-Workflows listet heute nur
   `dist/NightreignHelper.exe` und `dist/NightreignHelper.exe.sha256`, kein
   Hinweispaket. `docs/release/RELEASE_TEXT.md` verspricht im festen Text
   ("A notice package ... is attached to this release"), dass genau dieses
   Paket beiliegt — das stimmt erst, sobald `developer`/`release-manager`
   A-020 umsetzen. Ich habe das **nicht** verschwiegen, sondern in
   `RELEASE_TEXT.md` selbst als Randnotiz unter "Notes for whoever pastes
   this in" vermerkt, mit der ausdruecklichen Anweisung, den Satz nicht
   umzuschreiben, sondern den Workflow zu reparieren. Das ist reine
   Beobachtung beim Lesen (nicht Aendern) einer fuer mich tabuisierten Datei.
3. **Kein Versions-Drift** zwischen `requirements.txt` und Installation —
   ausdruecklich vom Auftrag verlangte Pruefung, Ergebnis negativ (kein
   Befund noetig), hier trotzdem vermerkt, damit die naechste Rolle nicht
   erneut pruefen muss.
4. **Kein echter "Anleitung ist nur wegen des Produkts kompliziert"-Befund**
   in diesem Auftrag — die Aufgabe war Lizenztextpflege, keine
   Bedienungsanleitung. Der naechstliegende Kandidat waere, dass PySide6 als
   Upstream-Paket selbst keinen LGPL/GPL-Volltext mitliefert und mich zu
   einer rechnerweiten Suche gezwungen hat (Befund 1) — das ist ein
   Upstream-Packaging-Umstand, kein Nightreign-Helper-Produktbefund, daher
   hier nur als Prozessnotiz, nicht als Produktbefund gezaehlt.

## Was ich nicht dokumentieren konnte

Nichts — Schritt 0 wurde nicht abgebrochen, alle vier Textstuecke (T1-T4,
wobei T4 laut Auftrag "heute nicht erforderlich" ist und daher nicht
geschrieben wurde) sind fertig.
