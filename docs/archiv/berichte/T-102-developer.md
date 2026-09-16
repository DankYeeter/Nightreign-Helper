# T-102 - `pytest-xdist` einbauen (developer)

```
STATUS: erledigt
AUFTRAG: T-102 - pytest-xdist einbauen
GELESEN: docs/tasks/T-102.md, docs/berichte/T-099-developer.md,
  requirements-dev.txt, requirements.txt, pytest.ini,
  .github/workflows/tests.yml, tests/conftest.py (Registrierungsschluessel,
  Zeilen 1-60), run.py, NightreignHelper.spec (Analysis/hiddenimports)
GEAENDERT: requirements-dev.txt (Zeile `pytest-xdist==3.8.0` ergaenzt,
  committet); die gemeinsame `.venv` (pytest-xdist 3.8.0 + execnet 2.1.2
  installiert, kein Git-Objekt)
ANNAHMEN: (1) "die Suite" in der Abnahme heisst der volle Lauf ohne
  `-m`-Filter, wie ihn `.github/workflows/tests.yml` faehrt
  (`python -m pytest -rs`) - nicht das um `slow` reduzierte Set aus T-099.
  Diese Maschine hat NIGHTREIGN installiert, die `slow`-Faelle laufen also
  echt statt sich zu ueberspringen; das erklaert, warum meine 1265
  Testfaelle (1256 passed + 9 skipped) exakt die Ausgangszahl treffen, aber
  von T-099s 1253 (`not slow`) abweichen. (2) Die Installation in die
  gemeinsame `.venv` sollte keine andere Rolle stoeren, da laut Auftrag
  keine parallel laeuft - bestaetigt durch `git status` (nur fremde,
  unberuehrte `docs/tasks/*.md` als untracked).
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

## Ausgangsmessung - seriell, vor jeder Aenderung

Kommando: `QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -rs -q
--junitxml=serial-1.xml` (voller Lauf, kein `-m`-Filter, Stand vor dem Commit
`4431c7a`).

```
1256 passed, 9 skipped in 839.87s (0:13:59)
real 14m15.051s
```

Trifft die im Auftrag genannte Ausgangszahl **1256 passed, 9 skipped, 0
failed** exakt.

## Installation

`pytest-xdist==3.8.0` in `requirements-dev.txt` ergaenzt (Commit `4431c7a`,
vor dem naechsten langen Lauf), danach `.venv/Scripts/python.exe -m pip
install pytest-xdist==3.8.0` gegen die gemeinsame `.venv` ausgefuehrt.
`pip list` danach: `execnet 2.1.2`, `pytest 9.1.1`, `pytest-xdist 3.8.0` -
beide neu in der gemeinsamen Umgebung, anders als beim Probelauf.
`requirements.txt` unveraendert (`git diff --stat requirements.txt` liefert
nichts).

## Parallelmessung - `-n auto`

Kommando: dasselbe, plus `-n auto --junitxml=parallel-1.xml`.

```
bringing up nodes... (2x, Controller + xdist-Ausgabe)
1256 passed, 9 skipped in 126.77s (0:02:06)
real 2m7.519s
```

Faktor **6,63** (839,87 s / 126,77 s) auf dieser Maschine, ohne Fremdlast -
in derselben Groessenordnung wie T-099s 6,93 unter Fremdlast.

## Der Namensvergleich - das ist die Abnahme

`classname::name` aus beiden JUnit-XML eingesammelt (1265 Faelle je Lauf:
1256 passed + 9 skipped):

| | Anzahl |
|---|---|
| Faelle je Lauf | 1265 |
| nur in seriell | 0 |
| nur in parallel | 0 |
| Urteilswechsel | 0 |
| uebersprungen (seriell) | 9 |
| uebersprungen (parallel) | 9 |
| Skip-Namen identisch | ja |

Dieselben neun `test_tab_geometry`-Faelle `[833]`, mit derselben Begruendung
("this platform will not give the window 833 logical px: it is 988 px wide
[...]") in beiden Laeufen.

**Gegenprobe des Vergleichs selbst** (sonst waere nur das Pruefmittel
gemessen, nicht die Sache): aus einer Kopie von `parallel-1.xml` einen Fall
entfernt (`tests.test_advisor_apply::test_a_row_with_no_answer_offers_no_
action_at_all`) und bei einem zweiten das Urteil auf `failed` gedreht
(`tests.test_advisor_search::test_two_slots_of_one_colour_are_not_offered_
the_same_pair_twice`). Der Vergleich meldet exakt diese beiden - "nur in
seriell (fehlt in mutiert)" = genau der entfernte Fall, "Urteilswechsel" =
genau der gedrehte, sonst nichts.

## Zweite Stichprobe - der einzeln genannte Testfall

Kommando: `pytest tests/test_settings_store.py` (Dateiname, kein Marker/
Filter), ohne `-n`.

| | Zeit |
|---|---|
| vor der Installation | 1,15 s (pytest), 1,616 s Wanduhr |
| nach der Installation, ohne `-n` | 1,19 s (pytest), 1,666 s Wanduhr |
| zum Vergleich: derselbe Aufruf mit `-n auto` erzwungen | 4,02 s (pytest), 4,537 s Wanduhr |

Die Installation selbst kostet den Einzelaufruf nichts (1,15 s -> 1,19 s,
Rauschen). Ein erzwungenes `-n auto` auf denselben 17 Faellen kostet das
3,4-fache allein fuer den Aufbau von 16 Workern.

## Entscheidung: `-n auto` **nicht** als Voreinstellung in `pytest.ini`

**Nicht geaendert.** Begruendung: Der obige Vergleich (1,19 s ohne `-n`
gegen 4,02 s mit erzwungenem `-n auto`) zeigt fuer denselben, kleinen
Einzelaufruf einen Faktor 3,4 zulasten der Voreinstellung - und genau diesen
Aufruf (`pytest <Datei>`, kein Marker) verlangt die Auftragsvorlage
inzwischen fuer jede Gegenprobe im Projekt, ausdruecklich weil ein Marker
57,35 s statt 0,95 s kostet. Eine `-n auto`-Voreinstellung wuerde jede
gezielte Einzeldatei-Gegenprobe im Projekt langsamer machen, nicht nur die
grosse Suite schneller. Ein Mittelweg (eigener Marker/`addopts`, je Aufruf
abschaltbar) waere zusaetzliche Infrastruktur fuer eine "kleine" Auftragsstufe
und wurde nicht gebaut - wer parallel fahren will, haengt `-n auto` an,
genau wie an diesem Auftrag selbst.

`pytest.ini` bleibt unveraendert.

## Artefakt-Bestaetigung fuer den heutigen Stand

Zwei unabhaengige Suchmasken, ganzes Repo (`git grep`, verfolgte Dateien),
je Fall case-insensitiv wiederholt, weil `git grep` ohne `-i` die
Vendor-Feldnamen verfehlt (`NearMaxDist` traegt ein grosses `D`):

| Suchbegriff | Treffer gesamt | wo |
|---|---|---|
| `xdist` (`-i`) | 5 | ausschliesslich `vendor/Paramdex/NR/Defs/*.xml`, Feldnamen (`NearMaxDist`, `FarMaxDist`, `sfxDistortion`, `otherMaxDistance`, `maxDistRecordNum`) |
| `execnet` (`-i`) | 0 | - |

`NightreignHelper.spec` und `requirements.txt`: kein Treffer fuer `xdist`
oder `execnet` (direkt gegrept).

**Importgraph, mit xdist absichtlich installiert und auf dem Pfad** (sonst
waere nur belegt, dass ein fehlendes Paket nicht importiert wird, was
nichts heisst): `import run` (sicher, weil `run.py`s `main()` nur unter
`__name__ == "__main__"` laeuft) plus alle vier `hiddenimports`
(`nrdata.extract`, `nrdata.gamefiles`, `nrdata.savefile`,
`nrdata.iconbuild`):

```
xdist package importable on sys.path: True
after importing the shipped entry point + all hiddenimports: []
positive control, after importing xdist by hand: ['pytest', 'xdist', 'xdist._version', 'xdist.plugin']
```

Der Befund aus T-099 gilt fuer den Stand, den dieser Auftrag einbaut, unveraendert: **xdist/execnet landen nicht im Artefakt.**

## Die drei Flacker-Kandidaten

`tests/test_advisor_bar.py:702`, `tests/test_advisor_worker.py:255` und
`:382` - alle drei im `-n auto`-Lauf ueberprueft (JUnit-XML nach `failure`
in den beiden Dateien durchsucht): **kein Fehlschlag.** Kein Befund, Faelle
unveraendert gelassen.

## CI - Einschaetzung ohne Aenderung

`.github/workflows/tests.yml` unveraendert gelassen, wie vorgegeben.
Einschaetzung: `-n` waere dort **eingeschraenkt sinnvoll**. Der Runner ist
`windows-latest` mit typischerweise deutlich weniger als 16 Kernen (2-4 je
nach GitHub-Kontingent, hier nicht gemessen), und die fuenf `slow`-Faelle
uebersehen sich dort ohnehin (kein NIGHTREIGN installiert) - das
`--dist loadfile`-Risiko aus T-099 (ein 40-s-Auszug wird zu fuenf) greift auf
diesem Runner also gar nicht. Der Nutzen waere kleiner als hier gemessen,
aber die Fixkosten (Prozessstart je Worker) blieben gleich - auf 2-4 Kernen
ist ein Faktor 2-3 realistischer als 6,6. Ungeprueft, weil eine andere
Kernzahl und eine andere Lastlage; das ist eine Messung, die auf dem Runner
selbst gemacht werden muesste, nicht abgeleitet werden kann.

## Commits

1. `4431c7a` `build(deps-dev): pytest-xdist fuer die parallele Suite` -
   `requirements-dev.txt`, vor der Installation und vor jedem langen Lauf
   committet.

## Definition of Done

- [x] Anforderung verstanden, Annahmen dokumentiert
- [x] Serieller Lauf gemessen, vor jeder Aenderung, trifft die Ausgangszahl
- [x] Installation in die gemeinsame `.venv`, `requirements.txt`
      unveraendert
- [x] Paralleler Lauf gemessen, Namensvergleich mit Gegenprobe
- [x] Zweite Stichprobe (Einzeldatei) vorher/nachher gemessen
- [x] `pytest.ini`-Entscheidung getroffen und begruendet (nicht geaendert)
- [x] Artefakt-Befund fuer den heutigen Stand bestaetigt (zwei Suchmasken,
      Positivkontrolle)
- [x] Drei Flacker-Kandidaten gepruft, kein Fehlschlag, keine Aenderung an
      ihnen
- [x] Kein Fenster gestartet (nur `import run`, `main()` laeuft nicht),
      keine Bildschirmabzuege
- [x] Keine Secrets, keine TODOs, kein toter Code
- Linter: das Projekt hat keinen konfiguriert - Punkt entfaellt
- **Ungeprueft:** CI-Laufzeit unter `-n` (andere Kernzahl, andere Lastlage,
  wie oben eingeschaetzt); Linux/macOS (Projekt ist Windows-only)

## Was aufgefallen ist, das nicht in den Auftrag gehoerte

Beim ersten Blick in die gemeinsame `.venv` (vor der Installation) fehlten
`pytest-xdist`/`execnet` in `pip list`; unmittelbar danach, waehrend der
serielle Lauf im Hintergrund lief, zeigte ein zweiter `pip list`-Aufruf
beide Pakete bereits als installiert, mit Verzeichnis-Zeitstempeln, die
exakt mit dem Ende des seriellen Laufs zusammenfielen - noch bevor mein
eigener `pip install`-Befehl lief (der dann "already satisfied" meldete).
Ich kann mir das nicht erklaeren; ich habe zwischen den beiden Pruefungen
keinen Installationsbefehl abgesetzt, und es lief laut Auftrag keine andere
Rolle. Ich vermute eine Verzoegerung des Verzeichnisabgleichs (das Profil
liegt unter `Desktop`, moeglicherweise cloud-synchronisiert), habe das aber
nicht verifiziert. Kein Sicherheitsrisiko, da das Ergebnis (Version 3.8.0,
Quelle PyPI ueber denselben `pip install`-Befehl) unveraendert ist - aber
ein Beleg, den ich nicht vollstaendig erklaeren kann, gehoert gemeldet statt
verschwiegen.
