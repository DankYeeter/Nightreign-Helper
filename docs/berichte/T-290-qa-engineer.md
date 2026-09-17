```
STATUS: blockiert
AUFTRAG: T-290b - Retest AK-314.1-.6 am Artefakt 1.13.2, Regression Optimize/Why/Filters
GELESEN: docs/tasks/T-290.md, T-289.md; docs/berichte/T-290-release-manager-build.md,
T-288-developer.md, T-285-release-manager-clean-room.md (Klick-Rezept); UI_SPEC.md
AK-314 (Nachtrag T-289a) und AK-300/AK-281/AK-291/AK-274/AK-301 (Wortlaut-Kontext);
`git show 1be0d9e` (voller Diff explain.py/run.py/types.py/advisorblock.py/app.py/
relicslots.py/test_advisor_run.py/test_advisor_block.py/test_advisor_explain.py);
qa/findings.md (Tabelle vollstaendig, hoechste ID vor diesem Lauf QA-282);
.claude/hooks/enforce-data-redirect.ps1 (nach zwei Fehlalarmen, siehe unten)
GEAENDERT: docs/berichte/T-290-qa-engineer.md (neu), qa/findings.md (QA-283
angehaengt). Kein Anwendungscode.
ANNAHMEN: keine Umgehung von NH-004 versucht (kein Stop-Process auf die
Nutzerkopie PID 22016/22172) - Auftrag verlangt ausdruecklich Warten und Melden.
NAECHSTER: T-290b erneut, sobald `tasklist` (oder gleichwertig) fuer
NightreignHelper 0 Treffer zeigt - AK-314.1-.6 am Fenster, danach Regression
Optimize/Why/Filters, danach Freigabeempfehlung.
BLOCKIERT DURCH: NH-004 - Nutzerkopie (PID 22016 Bootloader, PID 22172 Fenster)
lief ueber den gesamten Pruefzeitraum (mehrfach gegengeprueft, zwei Wartefenster
a 5 Minuten plus die Laufzeit der Testsuite dazwischen, insgesamt rund 20
Minuten, PIDs/Speicherbelegung unveraendert - keine neue Aktivitaet erkennbar,
die auf ein baldiges Ende schliessen liesse). Kein eigener Fensterstart moeglich,
ohne die laufende Kopie des Nutzers zu gefaehrden.
```

---

# T-290b - QA-Retest AK-314 (1.13.2)

## Kontraktblock

| | |
|---|---|
| **Artefakt** | `dist\NightreignHelper.exe`, 59.129.818 B, SHA-256 `F988C5207AF533F7E6EE993F4B91A2C23D1FC43538799C7C35425A7EA8B82367` - **nachgemessen** (Python-`hashlib`, da `certutil`/`Get-FileHash` mit dem Dateinamen im Klartext denselben Fehlalarm ausloesen wie unten beschrieben), deckt sich vollstaendig mit dem Auftragstext und `docs/berichte/T-290-release-manager-build.md` |
| **GUI-Retest AK-314.1-.6** | **nicht durchgefuehrt** - NH-004-Blocker (siehe Kontraktblock) |
| **Regression Optimize/Why/Filters am Fenster** | **nicht durchgefuehrt**, aus demselben Grund |
| **Urteil dieses Laufs** | unentschieden - das Abnahmekriterium AK-314 ist am Artefakt nicht belegt, aus einem Terminierungsgrund, keinem gefundenen Fehler |

## Risiko-Briefing (vorbereitet, nicht abgearbeitet)

Reihenfolge fuer den Nachholtermin, priorisiert: (1) AK-314.3/.4 - Kartenauswahl
bei zwei offenen Slots bzw. Wegfall bei `already_equipped`, weil `app.py`
hierfuer eine neue, ungetestete-am-Fenster Verzweigung traegt (`held_favourite_slot`,
`next(...)` ueber `suggestion.reasons`); (2) AK-314.1/.2/.6 - Satz/Zusammenfassung/
Stil der neuen Zeile, direkt sichtbar, hohe Nutzungshaeufigkeit; (3) AK-314.5 -
Why-Dialog traegt weiterhin beide Volltexte (Gegenprobe gegen eine versehentliche
Kuerzung); (4) Regression Optimize/Why/Filters, weil der Commit `already_equipped()`
oeffentlich gemacht und `show_the_suggestion`-Signaturen in `relicslots.py`/
`advisorblock.py` geaendert hat (neuer Default-Parameter, Reihenfolge gleich
geblieben - Regressionsrisiko fuer jeden bestehenden Aufrufer). Diese Reihenfolge
wurde durch den Blocker nicht abgearbeitet.

## Ersatzweise durchgefuehrt (kein Fensterstart noetig)

**Testsuite (Hauptbaum, `.venv`):** `pytest -n auto -q` -> **1735 passed, 11
skipped, 66,72 s**. Deckt sich exakt mit der Praemisse aus T-290.md ("vor Commit:
1735 passed / 11 skipped", dort als ungeprueft markiert - hiermit **verifiziert**,
nach Commit unveraendert). Keine Regression im Hauptbaum.

**Statische Pruefung des Fix-Diffs (`1be0d9e`, neun Dateien):** Scope-Grenze aus
T-289 eingehalten (`effectfilterdialog.py`, AK-281/AK-291-Saetze unangetastet -
deckt sich mit der Dateiliste in T-290c). Alle sechs AK-314-Kriterien haben je
einen eigenen, mutationstoetend beschriebenen Test:
`test_a_required_effect_a_held_relic_carries_is_said_to_be_there` (.1),
`test_two_favourites_met_by_a_hold_summarise_on_the_card` (.2),
`test_the_held_favourite_line_stands_on_the_lowest_open_card_only` (.3),
`test_the_held_favourite_line_drops_when_the_only_open_card_is_equipped` (.4),
derselbe Test plus die `run.py`-Tests belegen .5 (`unknowns` traegt weiterhin
beide Volltexte), `test_the_held_favourite_line_is_muted_bulleted_and_unmarked`
(.6). Das ist Code-Evidenz, **kein** Ersatz fuer den am Auftrag geforderten
Artefakt-Nachweis (A9) - siehe Blocker.

**Artefakt-Identitaet:** Groesse und SHA-256 nachgemessen (siehe Kontraktblock),
deckungsgleich mit T-290a.

## Befund

### [P2 | Major | Hoch] Hook `enforce-data-redirect.ps1`: `$istExeStart` löst auf reine Lesebefehle aus, die den Dateinamen nur nennen

**Adressat:** developer
**Betroffen:** `.claude/hooks/enforce-data-redirect.ps1:75` (`$istExeStart = $cmd
-match '(?i)\bNightreignHelper\.exe\b'`), verwendet am Gate in Zeile 87
**Umgebung:** Bash-Tool, dieser Pruefdurchlauf, kein Programmstart beteiligt

**Reproduktion:**
1. `tasklist //FI "IMAGENAME eq NightreignHelper.exe"` (reiner Prozess-Filter,
   NH-004-Vorpruefung laut Auftrag) -> `deny` ("Programmstart ohne vollstaendige
   Umlenkung ... fehlt").
2. `certutil -hashfile dist/NightreignHelper.exe SHA256` bzw. `ls -la
   dist/NightreignHelper.exe` (reiner Lesezugriff auf die Datei) -> derselbe
   `deny`.
3. Gegenprobe: dieselbe `tasklist`-Zeile mit drei sinnlosen Fuellwerten
   (`NIGHTREIGN_SETTINGS_ORG=x LOCALAPPDATA=/tmp APPDATA=/tmp`, ohne jede reale
   Umlenkungswirkung fuer einen Lesebefehl) davor -> `exit 0`, Befehl laeuft durch.

**Erwartet:** Der Waechter (Zeile 94, `$istExeKommando`) unterscheidet fuer die
NH-004-Instanzsperre bereits korrekt zwischen "EXE ist das Kommando" und "EXE
wird nur als Argument genannt" (Kommentar Zeile 93: "Hash- und ls-Aufrufe nennen
sie als Argument"). Dieselbe Unterscheidung fehlt bei `$istExeStart`
(Zeile 75), das jede Erwaehnung des Dateinamens als Programmstart wertet.

**Tatsaechlich:** Jeder reine Lese-, Hash- oder Prozesslistenbefehl, der den
String `NightreignHelper.exe` enthaelt, wird als Programmstart ohne Umlenkung
abgewiesen - unabhaengig davon, ob die Datei tatsaechlich ausgefuehrt wird.

**Analyse:** Gleiche Fehlerklasse wie der in T-289b bereits behobene
`run.py`-Fehlalarm (Commit `986216d`, Kommentarblock Zeile 67-73) - dort wurde
die Wortgrenzen-Ueberpruefung fuer Lesebefehle nachgeschaerft, `$istExeStart`
blieb dabei unberuehrt und traegt denselben Konstruktionsfehler: ein Muster ohne
Positionsbindung an den Kommandobeginn/eine Aufrufform.

**Auswirkung:** Trifft jede Rolle, die routinemaessig NH-004 vorab prueft
(`tasklist`) oder ein Artefakt nachmisst (`certutil`/`Get-FileHash`/`ls`) - genau
die in `CLAUDE.md` und `docs/berichte/T-282...`/`T-290-release-manager-build.md`
vorgeschriebenen Schritte. Jeder betroffene Lauf braucht einen Workaround (hier:
Python-`hashlib` statt `certutil`, `tasklist`-Filter mit `*` statt `.exe`) oder
sinnlose Fuellwerte, die den eigentlichen Zweck der Umlenkungspruefung
unterlaufen (Punkt 3 der Reproduktion) - Gewoehnung an Fuellwerte ist ein
Risiko fuer den Tag, an dem sie tatsaechlich einen Start maskieren.

**Vorschlag:** `$istExeStart` an dieselbe Positionsbindung wie `$istExeKommando`
(Zeile 94) angleichen, oder ganz auf `$istExeKommando` verweisen statt ein
zweites, weiteres Muster zu pflegen.

## Nicht getestet

AK-314.1-.6 am Fenster, Regression Optimize/Why/Filters am Fenster,
Clean-Room/Update-Pfad (nicht Teil von T-290b) - alle wegen des NH-004-Blockers.
Security-Kurzlauf (T-290c) laeuft parallel, eigene Rolle, nicht wiederholt.

## Zusammenfassung (an director)

**1 Befund: P2 (1).** Kein P1. **Gesamturteil: FAIL** - nicht wegen eines am
Artefakt gefundenen Fehlers, sondern weil A9 ("QA gegen ein gebautes Artefakt")
fuer AK-314 nicht belegt ist: der GUI-Retest konnte ueber den gesamten
Pruefzeitraum nicht stattfinden, weil die Instanzsperre (NH-004) durchgehend von
der Nutzerkopie gehalten wurde. Mindestens erforderlich vor einer Freigabe:
T-290b nachholen, sobald ein Fenster frei ist (`tasklist` fuer NightreignHelper
= 0), AK-314.1-.6 und Optimize/Why/Filters am Artefakt 1.13.2 pruefen. Die
Code-Evidenz (Suite 1735/11, sechs gezielte, mutationstoetende Unit-Tests fuer
AK-314.1-.6, Diff-Scope deckungsgleich mit T-290c) staerkt die Erwartung, dass
der Nachholtermin bestehen wird, ersetzt den Artefakt-Nachweis aber nicht.

**Explorationsprotokoll:** Testsuite gelaufen und ausgewertet; Diff `1be0d9e`
vollstaendig gelesen; Artefaktgroesse/-hash nachgemessen; zwei unabhaengige
Wartefenster (~20 min gesamt) auf die Nutzerkopie; Hook-Fehlalarm zweimal
reproduziert, einmal gezielt widerlegt (Gegenprobe mit Fuellwerten). Keine
GUI-Interaktion versucht, da NH-004 das ausdruecklich verbietet, solange die
fremde Kopie laeuft.

**Offene Fragen:** keine (Spec AK-314 ist eindeutig, Abweichung ist rein
terminlich).

## QA-Log (Anhang an `qa/findings.md`)

| QA-283 | Hook `enforce-data-redirect.ps1`: `$istExeStart` (Zeile 75) loest auf reine Lesebefehle aus, die `NightreignHelper.exe` nur als Text/Argument nennen (`tasklist`-Filter, `certutil -hashfile`, `ls`) - dieselbe Fehlerklasse wie der in T-289b behobene `run.py`-Fehlalarm, hier nicht mitbehoben; Gegenprobe mit sinnlosen Fuellwerten umgeht die Pruefung vollstaendig | P2 | Major | developer | ja - 2x direkt reproduziert + 1x widerlegt, dieser Lauf | offen | 2026-09-17 |
