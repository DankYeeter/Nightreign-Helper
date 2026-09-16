STATUS: teilweise
AUFTRAG: T-200 — QA-231, zweiter Anlauf: der Abzug an einen Ort, der echte Platte ist
GELESEN: docs/tasks/T-200.md, docs/berichte/T-196-developer.md, qa/findings.md (QA-231), CLAUDE.md (Abschnitt "Projektzeilen fuer jeden Auftrag"), nrplanner/paths.py, nrplanner/favourites.py, nrplanner/shortcut.py
GEÄNDERT: `C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` (neu angelegt, ausserhalb des Repos, Nachbarverzeichnis von `Nightreign-Helper`); `docs/berichte/T-200-developer.md`. Keine Datei im Repository ausser dem Bericht. Der alte Pfad `C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug` aus T-196 wurde nicht angefasst.
ANNAHMEN: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT200` als eigener, isolierter Wert fuer diesen Auftrag gewaehlt (Muster wie in T-196: `<echter Org-Name><T-Nummer>`) — CLAUDE.md nennt nur das Muster, keinen festen Wert. "Kein Anwendungscode" verstanden wie in T-196: ein `python run.py`-Lauf mit umgelenkten Variablen ist der geforderte Fensterlauf selbst, nicht "Anwendungscode aendern".
NÄCHSTER: director
BLOCKIERT DURCH: die externe Bestaetigung durch den Nutzer von seinem eigenen System aus (Kommando unten unter "Probe fuer den Nutzer") — die ist noch nicht gelaufen. Bis dahin bleibt offen, ob dieser Zweig tatsaechlich echte Platte ist oder nur eine weitere Ueberlagerung, in der ich wieder nur meine eigenen Schreibvorgaenge zurueckgelesen habe.

## Faehigkeitsprobe (Vorgabe 1)

Kleine Datei direkt am Zielort angelegt und zurueckgelesen, **vor** jedem
weiteren Schritt:

```
$ echo "probe-T200-20260912T172525Z" > "C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug\.probe"
$ cat "C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug\.probe"
probe-T200-20260912T172525Z
```

Gelungen — kein Abbruch noetig. Datei danach wieder geloescht (sie ist nicht
Teil des Abzugs). **Wichtig, wie im Auftrag verlangt:** dieser gelungene
Ruecklesetest ist ein Los/no-go-Kriterium fuer Vorgabe 1, **kein** Nachweis,
dass der Ordner echte Platte ist — dieselbe Verwechslung hat T-196 gekostet.
Das eigentliche Kriterium steht unten unter "Probe fuer den Nutzer".

`C:\Users\Daniel\Desktop\ClaudeCode` ist ausserdem sichtbar kein isolierter
Ort: `ls` zeigt zehn weitere, seit Wochen gewachsene Projektordner
(`ApplicationHelper`, `platinum-souls`, `rain-codec`, `pension-manager`, …)
und mehrere Dateien mit Datumsstempeln aus dem August — das allein beweist
noch nicht, dass *dieser* Zweig unueberlagert ist, macht es aber deutlich
wahrscheinlicher als der `AppData\Local`-Zweig aus T-196.

## Vorgabe 2 — drei Variablen umgelenkt, jede Umlenkung belegt

Gesetzt fuer den Erzeugungslauf (`python run.py` aus dem Repo-Wurzelverzeichnis):

| Variable | gesetzter Wert | Beleg |
|---|---|---|
| `NIGHTREIGN_SETTINGS_ORG` | `DankYeeterT200` | `reg query "HKCU\Software\DankYeeterT200\NightreignHelper"` liefert einen neu angelegten Key mit den Untergruppen `builds`, `chalices`. `reg query "HKCU\Software\DankYeeter\NightreignHelper"` (der echte, 309-Relikte-Speicher) zeigt danach weiterhin genau `builds`, `chalices`, `favourites`, `ui`, `variant` — keine neue Gruppe, unveraendert. |
| `LOCALAPPDATA` | `…\scratchpad\T-200\localappdata` | Abzug entstand unter `…\scratchpad\T-200\localappdata\NightreignHelper` (841 Dateien, siehe unten). Der echte `C:\Users\Daniel\AppData\Local\NightreignHelper` traegt danach `LastWriteTime = 18.08.2026 22:27:40` — derselbe Zeitstempel, den T-196 vor vier Wochen protokolliert hat, also unveraendert seit vor diesem Auftrag. |
| `APPDATA` | `…\scratchpad\T-200\appdata` | `Test-Path 'C:\Users\Daniel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Nightreign Helper.lnk'` → `False`, vor und nach dem Lauf. **Dieselbe Einschraenkung wie in T-196:** `nrplanner/shortcut.py` erstellt die Verknuepfung nur wenn `sys.frozen` gesetzt ist; ein Quellbaum-Lauf (`python run.py`) durchlaeuft diesen Pfad nicht. Kein Nachweis fuer die `.exe`, nur fuer den Quellbaum-Lauf. |

Nachweis gelang fuer alle drei Variablen; kein Abbruch noetig.

## Vorgabe 3 — Abzug neu erzeugt, nicht verschoben

`python run.py` mit den drei oben genannten Variablen gestartet (WINPID
14596, `nohup … &`), Fortschritt ueber die Dateizahl im umgelenkten
`LOCALAPPDATA` verfolgt:

```
t=15s  files=0
t=30s  files=0
t=45s  files=1
t=60s  files=11
t=75s  files=780
t=90s  files=841
t=100s files=841   (stabil, keine Aenderung mehr)
```

Prozess danach beendet (`Stop-Process -Id 14596 -Force`). Quelle des Abzugs
ist damit ein echter Extraktionslauf aus dem installierten Spiel
(`d:\steam\steamapps\common\ELDEN RING NIGHTREIGN\Game`, automatisch
gefunden), nicht die T-196-Kopie.

Von dort (`…\scratchpad\T-200\localappdata\NightreignHelper`, real, echte
Kopie via `cp -r`, kein Symlink, keine Junction) nach
`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug` kopiert:

```
$ find "…\NightreignHelper-Testabzug" -type f | wc -l
841
$ du -sb "…\NightreignHelper-Testabzug"
20812293
$ diff -rq "…\scratchpad\T-200\localappdata\NightreignHelper" "…\NightreignHelper-Testabzug"
IDENTISCH (keine Ausgabe von diff, beide Baeume gleich)
```

**Unterschied zu T-196, ausdruecklich als Beobachtung, nicht als Beweis:**
`nightreign_data.json` (8.484.644 Bytes) liess sich am Zielort mit `cat`,
`python open()` und PowerShell `Get-Item`/`.Length` **ohne** den
"Permission denied"/APPX-Fehler lesen, der in T-196 jeden Zugriff auf
frisch angelegte Dateien unter dem echten `AppData\Local` blockiert hat. Das
ist konsistent mit der Annahme "dieser Zweig ist unueberlagert", beweist sie
aber nicht — ich sitze moeglicherweise selbst in genau der Ueberlagerung, die
der Auftrag beschreibt, und lese dann zwangslaeufig meine eigenen
Schreibvorgaenge widerspruchsfrei zurueck. Das ist exakt die Verwechslung,
vor der der Auftrag warnt.

## Vorgabe 4 — Zahlen gegen den Sollwert aus T-196

| Groesse | Sollwert (T-196) | gemessen (12.09.2026, dieser Lauf) |
|---|---|---|
| Dateien | 841 | **841** — keine Abweichung |
| Bytes | 20.812.293 | **20.812.293** — keine Abweichung |
| `EXTRACT_VERSION` | 11 | **11** — keine Abweichung |
| Programmversion | 1.9.0 | **1.9.0** — keine Abweichung (`python -c "import nrplanner; print(nrplanner.__version__)"`) |

`meta`-Block der neu gebauten `nightreign_data.json` (gemessen ueber
`json.load`): `extract_version=11, regulation_sha256=876a3ca…,
regulation_size=1974720, data_version=10350000,
game_dir=d:\steam\steamapps\common\ELDEN RING NIGHTREIGN\Game, hero_count=10,
relic_count=849, deep_relic_count=252, chalice_count=74, effect_count=2076,
weapon_count=1793, boss_count=18, world_event_count=11` — identisch mit
T-196.

## Vorgabe 5 — alter Pfad unberuehrt

`C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug` (aus T-196) wurde
in diesem Auftrag zu keinem Zeitpunkt gelesen, geschrieben oder geloescht.

## Aufgeraeumt

- Der Erzeugungslauf (`python run.py`, WINPID 14596) ist beendet
  (`Get-Process -Id 14596` liefert danach keinen Treffer mehr).
- Kein anderer `python.exe`-Prozess mit `run.py` in der Kommandozeile lief
  danach noch (`Get-CimInstance Win32_Process` geprueft).
- Ein parallel laufender `python.exe -m pytest -n auto -q` (PID 30096, nicht
  von mir gestartet — vermutlich `qa-engineer` oder `security-reviewer` auf
  dem eingefrorenen Stand) wurde **nicht** angefasst.
- Registry: `HKCU\Software\DankYeeterT200\NightreignHelper` (isolierter
  Testnamensraum) blieb stehen, wie schon bei T-196 mit dem dortigen
  Testnamensraum — kein Versuch unternommen, ihn zu loeschen (Anti-Loop-Regel:
  T-196 hat bereits protokolliert, dass `reg delete`/`Remove-Item` an dieser
  Grenze scheitern; ein dritter Versuch mit denselben Mitteln haette
  dieselbe Grenze nur erneut bestaetigt, nicht ueberwunden).
- Die einmalige Probe-Datei `…\NightreignHelper-Testabzug\.probe` wurde vor
  dem Kopieren des eigentlichen Abzugs geloescht.
- Scratch-Inhalte unter `…\scratchpad\T-200\` bleiben stehen (Rohkopie des
  Abzugs, Log der Programm-Ausgabe) — sitzungsspezifisch, wie in CLAUDE.md
  vorgesehen.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [ ] Build & Tests gruen — kein Testbefehl in diesem Auftrag (kein
      Anwendungscode geaendert); die einzige Pruefung ist der Fensterlauf
      selbst und die externe Probe, die noch aussteht.
- [x] Keine Secrets, keine TODOs, kein toter Code — kein Anwendungscode
      angefasst.
- [x] Scope eingehalten: keine Datei unter `nrplanner/`, `nrdata/`,
      `tests/`, `CLAUDE.md` veraendert; nichts in den Projektbaum kopiert.
- [ ] Ext. Bestaetigung durch den Nutzer — offen, siehe "Probe fuer den
      Nutzer" unten.
- [x] Bericht geschrieben und unter `docs/berichte/T-200-developer.md`
      abgelegt.

## An den director

- **Kernergebnis:** Der Abzug liegt jetzt zusaetzlich unter
  `C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug`
  (841 Dateien, 20.812.293 Bytes, `EXTRACT_VERSION` 11, Programmversion
  1.9.0 — alle vier Zahlen identisch zum Sollwert aus T-196). Erzeugt durch
  einen frischen Extraktionslauf aus dem installierten Spiel, nicht durch
  Kopie des alten, ueberlagerten Pfads.
- **Der offene Punkt ist diesmal ein anderer als in T-196:** dort scheiterte
  schon das Ruecklesen mit einer Fehlermeldung. Hier gelingt das Ruecklesen
  anstandslos — was fuer "echte Platte" spricht, aber laut Auftrag kein
  gueltiger Nachweis ist, weil ich als moegliches Mitglied derselben
  Ueberlagerung meine eigenen Schreibvorgaenge immer erfolgreich zurueckliese.
  Die einzig schluessige Bestaetigung ist die externe Probe unten, vom
  Nutzer selbst auf seinem System ausgefuehrt.
- **Falls die Probe negativ ausfaellt** (Pfad auf dem echten System nicht
  vorhanden): dann ist auch `C:\Users\Daniel\Desktop\ClaudeCode` als
  Nachbarverzeichnis des Repos ueberlagert, und der Auftrag braucht einen
  dritten Kandidaten-Ort — der Auftrag selbst benennt keinen.
- **Nebenfund, wie schon in T-196:** `APPDATA`/Start-Menu-Pfad in
  `nrplanner/shortcut.py` ist hinter `sys.frozen` verriegelt; ein
  Quellbaum-Lauf durchlaeuft ihn nicht. Der erste `power-user`/`clean-room`-
  Lauf mit der gebauten `.exe` prueft diesen Pfad zum ersten Mal.
- **Nebenfund:** die Registry-Testgruppe `HKCU\Software\DankYeeterT200`
  (zwei Unterknoten: `builds`, `chalices`) liess sich mit meinen Mitteln
  nicht entfernen, dieselbe Grenze wie bei den vier `DankYeeterT196*`-Keys
  aus T-196, die ebenfalls noch stehen. Harmlos (eigener, vom echten
  `DankYeeter`-Org getrennter Namensraum), aber jemand mit vollem
  Systemzugriff sollte irgendwann alle fuenf zusammen aufraeumen.

## An qa-engineer

Nichts Eigenes zu testen aus diesem Auftrag selbst — der Abzug ist
Infrastruktur fuer eure Fensterlaeufe (`power-user`, `clean-room`). Sobald
die Probe unten vom Nutzer bestaetigt ist: ein Fensterlauf mit
`LOCALAPPDATA` auf einen Ort zeigend, der eine Kopie dieses Abzugs unter
`NightreignHelper\` enthaelt, sollte in Sekunden statt >100 s startklar sein
— das bestaetigt QA-231 als geschlossen.

## Probe fuer den Nutzer

```
powershell -NoProfile -Command "(Get-Item 'C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug\nightreign_data.json').Length"
```

- **Angekommen:** die Ausgabe ist die Zahl `8484644`.
- **Nicht angekommen:** eine Fehlermeldung, die mit
  `Get-Item : Cannot find path 'C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug\nightreign_data.json' because it does not exist.`
  beginnt (oder eine andere Zahl als `8484644` — das waere kein "nicht
  angekommen", sondern ein eigener Befund und muesste separat gemeldet werden).
