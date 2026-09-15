# T-202 — security-reviewer

*Abgelegt vom Director am 12.09.2026. Die Rolle hat kein Schreibrecht im
Projekt; der Bericht ist unveraendert aus ihrer Antwort uebernommen.*

```
STATUS: erledigt
AUFTRAG: T-202 — Pruefphase, Sicherheit: der eingefrorene Stand b33461d
GELESEN: ~/.claude/agents/_rahmen.md, CLAUDE.md, docs/tasks/T-202.md,
  security/findings.md (54 Zeilen, alle 36 Befunde), nrdata/gamefiles.py,
  nrdata/binary.py, nrdata/dcx.py, nrdata/oodle.py,
  nrplanner/firstrun.py (120-220, 440-550, 570-645, 1020-1030),
  nrplanner/errortext.py, nrplanner/shortcut.py (36-154),
  tests/test_exception_text_is_english.py (1-270),
  tests/test_game_dir_recognition.py (195-250),
  git diff 28dc45c..b33461d (71 Dateien), git log 28dc45c..b33461d (56 Commits)
GEÄNDERT: keine Datei im Projekt. Kein Commit, kein Stage, kein Git-Zustand
  angefasst (`git status` leer, verifiziert). Ausserhalb des Projektbaums
  angelegt: .claude/agent-memory/security-reviewer/MEMORY.md und
  project_localappdata_overlay.md (Agenten-Gedaechtnis, nicht Projektcode).
  Scratchpad .../scratchpad/T-202/ angelegt und restlos entfernt (geprueft).
ANNAHMEN: (1) Die Sprachhaelfte von F3 ist Hypothese — diese Maschine laeuft
  PowerShell unter en-GB, ein lokalisierter Wortlaut ist hier nicht
  reproduzierbar; die Pfadhaelfte ist gemessen. (2) Die Prozessgrenze als
  Grenze der QA-237-Ueberlagerung ist Hypothese, als solche gekennzeichnet,
  aus einer Beobachtung belegt und nicht gegengeprueft. (3) `C:\Program
  Files (x86)\Steam` existiert hier nicht — gemessen ist die geerbte ACL des
  Elternordners, nicht die, die Steams Installer setzen wuerde.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

## Widerspruch zum Auftrag: keiner sachlich, eine Korrektur am Stand

`HEAD` war bei Beginn `ce716da` und wanderte während meines Laufs auf
`8ee4c29` (parallele Doku-Commits). **Der geprüfte Code ist byteidentisch mit
`b33461d`**: `git diff --stat b33461d HEAD -- nrplanner/ nrdata/ tests/` ist
leer, alle drei Commits seither sind `docs/`. Der Auftrag stimmt.

**Eine Formulierung im Auftrag widerspreche ich** — die Director-Notiz „sonst
ist SEC-036 formal zu und sachlich offen". Siehe F6: sie ist zu stark, und der
tragende Grund ist ein anderer als der, den der `developer` genannt hat.

---

## Vertrauensgrenzen des geprüften Bereichs

| Grenze | herein | heraus |
|---|---|---|
| **G1 Spielinstallation → Programm** | `regulation.bin`, `*.bhd`/`*.bdt`, Oodle-DLL, MSB/TPF/DDS/FMG-Inhalte | Fenstertext, Icons, Snapshot-Cache |
| **G2 Save → Programm** | `NR****.sl2`, BND4-Mitglieder, Reliktdatensätze | Fenstertext, Slotkarte |
| **G3 Dateisystem/Umgebung → Programm** | Registry `SteamPath`, `libraryfolders.vdf`, `%APPDATA%`, `%LOCALAPPDATA%`, `%SystemRoot%`, vom Nutzer gewählter Ordner | `.lnk` im Start-Menü, Cache, Einstellungen |
| **G4 Programm → Nutzer (Fläche)** | — | Panel-, Warn- und Fehlertexte (A8-Zusage: englisch; AK-126: kein Konto-Pfad) |
| **G5 Kindprozess** | PowerShell-`stderr`/`stdout`, Rückgabewert | `.lnk`-Schreibvorgang, Pfade über `env` |

Kein Netzwerk im Anwendungscode (zweite Maske über den Diff: 0 Treffer für
`urlopen|requests|socket`). **G1 gilt seit A15 nicht mehr als
vertrauenswürdig** — das ist der Kern von F1.

---

## Befunde

### F1 [Mittel | Mittel | Mittel] Die Freigabebedingung von SEC-016, SEC-017 und SEC-018 beschreibt das Programm nicht mehr

**Betroffen:** `nrdata/dcx.py:38-40` (SEC-016), `nrdata/dcx.py:42` (SEC-018),
`nrdata/tpf.py:25-53` (SEC-017); Auslöser ist `nrplanner/firstrun.py:1025`
(`run`) über `_Builder.run:600-633`

**Vertrauensgrenze:** G1 — und genau die ist verschoben

**Angriffspfad:** Der Nutzer hat die drei am 05.09.2026 geschlossen, wörtlich
*„setzt eine boesartige Spielinstallation oder ein bereits uebernommenes
Benutzerkonto voraus; nicht erneut vorlegen"*. A15 hat danach eine Route
ausgeliefert, in der der Nutzer **einen beliebigen Ordner zeigt**. Ein
entpacktes Archiv aus dem Netz ist weder eine bösartige *Installation* noch
ein übernommenes *Konto* — es ist ein dritter Fall, den der Freigabesatz nicht
kennt. `looks_like_the_game` (`gamefiles.py:153-185`) prüft nur, dass drei
Dateien da sind, und alle drei füllt der Angreifer selbst. Danach läuft
`extract` über die mitgelieferten Archive in `dcx.decompress`:
`max_output_size=uncompressed_size` kommt aus einem `>I` der Datei (bis 4 GiB),
und der `DFLT`-Zweig ist `zlib.decompress(payload)` **ohne jeden Deckel**.

**Auswirkung:** Speichererschöpfung des Fensterprozesses über einen Weg, den
der Freigabesatz nicht abdeckt. Kein Codeausführungsgewinn.

**Behebungsrichtung:** **Kein Fix, eine Entscheidung.** Ich lege die drei nicht
erneut vor — der Nutzer hat „nicht erneut vorlegen" geschrieben, und
akzeptiertes Restrisiko ist seine Sache. Was ich melden muss, ist, dass die
**Randbedingung der Annahme gewechselt hat**. Zwei Wege: den Freigabetext auf
den heutigen Wortlaut nachziehen („ein Ordner, den der Nutzer bestätigt hat"
statt „die eigene Installation"), oder die Deckel nachziehen, weil sie klein
sind. Gehört zu SEC-026, nicht dagegen.

**Nachweis:** `dcx.py:38-40` und `:42` am Stand `b33461d` unverändert
(gelesen); Freigabetext aus `security/findings.md:34,35,36`; die A15-Route in
`firstrun.py:521-541`.

> **Antwort auf die Falle im Auftrag.** „Wer härtet, macht SEC-016/017/018
> wieder scharf" gilt **nicht** gleichmässig — es hängt an der Bauform der
> Härtung: Härtung über **Herkunft** (nur Registry/`libraryfolders.vdf`) stellt
> die Vertrauensannahme *wieder her*, die Schliessung trägt weiter. Härtung
> über **Zustimmung** (ein C3-Klick auf einen Ordner unbekannter Herkunft)
> trägt sie nicht — ein Klick ist keine Herkunftsprüfung. Und der schärfere
> Punkt: die Bedingung ist **schon bei `b33461d` abgelaufen**, vor jeder
> Härtung.

### F2 [Mittel | Mittel | Mittel] Der Wächter zu SEC-036 kann an der festen Wurzel nicht rot werden

**Betroffen:** `tests/test_game_dir_recognition.py:143-156`
(`_the_only_candidate`) und `:212-236`; bewacht `nrdata/gamefiles.py:32-35`

**Vertrauensgrenze:** G3

**Angriffspfad:** Kein eigener — dies ist die fehlende Bindung des
SEC-036-Pfads. SEC-036s eigene Behebungsnotiz verlangt, dass der Wächter „die
**echte** Kandidatenliste messen" muss. Das tut er nicht, und ich habe den
Nenner dazu: über `test_game_dir_recognition.py`, `test_first_run_panel.py` und
`test_steam_library_start_folder.py` (**110 Tests, alle grün**) lief der
**echte** `_steam_roots`-Körper **26-mal** und gab jedes Mal
`['d:\steam', 'C:\Program Files (x86)\Steam', 'C:\Steam']` zurück — **beide
feste Wurzeln sind drin**. Alle **5** `_steam_roots`-Fundstellen in `tests/`
sind `monkeypatch.setattr`-Stubs; **0** binden den Rückgabewert, und **kein**
Testfile enthält das Literal `Program Files` oder `C:\Steam`. Unsichtbar sind
die Wurzeln nur, weil **keine der beiden auf dieser Maschine existiert** (`ls`
auf beide: nicht gefunden) und `find_game_dir:78` sie per
`if not root.exists()` wegwirft — gefiltert durch Zufall der Maschine, nicht
durch Bau. Auf einem Rechner, auf dem ein zweites Konto `C:\Steam` angelegt
hat, wäre die Suite genauso grün.

**Auswirkung:** Der Fix zu SEC-036 kann eingebaut, wieder entfernt oder um eine
neue feste Wurzel ergänzt werden, ohne dass ein Test das merkt.

**Behebungsrichtung:** Ein Fall, der `_steam_roots()` **aufruft statt zu
ersetzen**, die Registry-Hälfte fälscht (nicht die Funktion) und die
Rückgabeliste gegen ein **Literal** hält. Rote Phase: eine feste Wurzel
hinzufügen, der Fall muss brechen.

**Nachweis:** Eigenes pytest-Plugin im Scratchpad, das den echten
`_steam_roots` zählend umhüllt: `real _steam_roots body executed 26 time(s)`,
`roots returned: ['d:\steam', 'C:\Program Files (x86)\Steam', 'C:\Steam']`,
`110 passed`.

### F3 [Niedrig | Niedrig | Niedrig] `shortcut.create()` gibt PowerShells `stderr` wörtlich auf die Fläche — zwei Zeilen unter der Stelle, die QA-211 geschlossen hat

**Betroffen:** `nrplanner/shortcut.py:138-140`

**Vertrauensgrenze:** G5 → G4

**Angriffspfad:** QA-211 hat „den Start-Menü-Knopf" als eine der fünf Senken
benannt. Geschlossen wurde die **Ausnahme**-Hälfte in `shortcut.py:132-136`
(`errortext.in_english(exc)`, mit Kommentar auf A8). Zwei Zeilen tiefer steht
die **Kindprozess**-Hälfte derselben Funktion, im selben Rückgabewert, auf
derselben Fläche:
`detail = (result.stderr or result.stdout or "").strip().splitlines(); return detail[0]`.
Das ist nie eine Ausnahme, also sieht kein Wächter es — der AST-Scan liest
`except`-Blöcke.

**Auswirkung:** Gemessen trägt PowerShells `stderr` den **vollen `.lnk`-Pfad**:
`Unable to save shortcut "C:\Users\Daniel\...\Nightreign Helper.lnk".` Der
echte Pfad liegt unter `%APPDATA%\Microsoft\Windows\Start Menu\Programs` und
enthält den Windows-Benutzernamen. Dazu zwei Nebenwirkungen: PowerShell
**bricht die Zeile bei 128 Zeichen um**, `detail[0]` liefert also einen *mitten
im Pfad abgeschnittenen* Satz (A7), und auf einem lokalisierten Windows ist der
Satz nicht englisch (A8). Kein Vertrauensgrenzübertritt nach aussen — der
Nutzer sieht seinen eigenen Namen auf seinem eigenen Schirm —, daher Niedrig.

**Behebungsrichtung:** Dieselbe Behandlung, die die Ausnahmehälfte bekam: den
Ausgang des Kindes auf einen Satz dieses Repositorys abbilden. Ein `returncode`
ist eine Zahl und spricht keine Sprache; `stderr` gehört auf die Konsole
(`traceback.print_exc()`-Präzedenz), nicht in den Rückgabewert.

**Nachweis:** Lokal gemessen mit absichtlich ungültigem Ziel im Scratchpad (es
wurde **nichts** geschrieben, geprüft): `stderr` =
`Unable to save shortcut "C:\Users\Daniel\...\...\does-not-exist-dir\Nightreign Helper.lnk".`
über zwei Zeilen. `CurrentUICulture` dieser Maschine: `en-GB` — die
Sprachhälfte ist hier daher **Hypothese**, die Pfadhälfte gemessen.

### F4 [Niedrig | Niedrig | — ] Härtung: der SEC-023-Wächter deckt den reinen Pfadträger `exc.filename` nicht

**Betroffen:** `tests/test_exception_text_is_english.py:77`
(`WORDING_ATTRIBUTES`)

**Vertrauensgrenze:** G3 → G4

**Angriffspfad:** Heute keiner — **0 Fundstellen** von `.filename`/`.filename2`
in `nrplanner/` und `nrdata/` (zwei Masken). Deshalb Härtung, kein Befund mit
Pfad. Aber die Achse ist die: `WORDING_ATTRIBUTES` enthält `strerror` — das ist
laut der **eigenen Docstring derselben Datei** (Zeile 11-12) „the half of it
that carries **no** path". Und `filename`, das die Docstring in Zeile 53-55
ausdrücklich als Pfadträger benennt (*„an `OSError` carries it in `str(exc)`
and in `filename`"*), fehlt. Der Wächter deckt den **Sprach**träger und lässt
den **reinen Pfad**träger offen — bei einem Befund, dessen Gegenstand der Pfad
ist.

**Auswirkung:** Die nächste hinzugefügte Zeile `say(exc.filename)` trägt den
vollen Save-Pfad samt Steam-Konto-Kennung (AK-126) auf die Fläche, und nichts
schlägt an.

**Behebungsrichtung:** `filename` und `filename2` in `WORDING_ATTRIBUTES`. Die
zwei anderen gemessenen Lücken (Alias `kept = exc`; Ablegen-dann-zitieren
`self._last = exc` … `str(self._last)`) sind eine grössere Bauform —
Datenflussverfolgung statt Musterabgleich. **Ich empfehle sie nicht:** Aufwand
deutlich über dem Nutzen, solange die Bauform im Bestand nicht vorkommt. Als
bekannte Decke im Docstring nennen.

**Nachweis:** Positivkontrolle gegen die Scanfunktion selbst:
`places_that_quote_an_exception` gibt für `say(exc.filename); say(exc.filename2)`
**`[]`** zurück, ebenso für die Alias- und die Ablegen-Form — während die drei
abgedeckten Formen korrekt anschlagen (`test_the_scan_really_fires` grün).

### F5 [Niedrig | Niedrig | Niedrig] Härtung: T-193 hat `binary.magic` über die Zitatgrenze geschoben — 4 Byte Dateiinhalt erreichen die Fläche wörtlich

**Betroffen:** `nrdata/binary.py:91-94`

**Vertrauensgrenze:** G1/G2 → G4

**Angriffspfad:** Vor T-193 warf `magic()` ein blankes `ValueError`;
`errortext.in_english` **bildet** das ab. Gemessen, beide Fassungen: vorher
`"Something went wrong that this program has no sentence for (ValueError)."` —
bei `b33461d` `expected magic b'BND4' at 0, got b'<img'`, die Angreiferbytes
**wörtlich**. T-193 hat die Stelle also aus dem abbildenden in den zitierenden
Zweig verschoben.

**Auswirkung:** **Begrenzt auf 4 Byte.** `magic()` liest `len(expected)`, und
beide Aufrufstellen (`bnd4.py:91` `b"BHF4"`, `bnd4.py:141` `b"BND4"`) übergeben
4 Byte. Eine holende Marke braucht mindestens `<img src=x>` = 11 Zeichen, also
**keine SEC-019-Eskalation**. Der Deckel ist aber eine Eigenschaft von **zwei
Aufrufstellen**, nicht des zitierenden Codes: eine dritte Stelle mit längerer
Magic verschiebt ihn, und nichts sagt es.

**Behebungsrichtung:** Die Absage braucht die Bytes nicht — `got={got!r}`
fallen lassen, oder im `raise` selbst begrenzen. Alternativ die Grenze dort
hinschreiben, wo sie gilt.

**Nachweis:** Beide Fassungen in-process gemessen (siehe oben);
`grep -rn "\.magic("` über `nrdata/` + `nrplanner/`: genau 2 Fundstellen, beide
4 Byte.

### F6 [Niedrig | Niedrig | — ] Härtung und Korrektur: `STEAM_COMMON` ist nicht der Angreifer von SEC-036

**Betroffen:** `nrplanner/firstrun.py:153`, benutzt in `:486`

**Vertrauensgrenze:** G3

**Angriffspfad:** **Keiner für SEC-036s Angreifer — und das ist gemessen, nicht
geschlossen.** `icacls C:\` bestätigt SEC-036s Prämisse:
`NT AUTHORITY\Authenticated Users:(AD)`, jedes authentifizierte Konto darf
`C:\Steam` anlegen. `icacls "C:\Program Files (x86)"` zeigt dagegen für
`BUILTIN\Users` nur `(RX)`; schreibberechtigt sind TrustedInstaller, SYSTEM und
Administratoren. **Ein zweites unprivilegiertes lokales Konto — die
Voraussetzung, aus der SEC-036 seine eigene ID bekam — kann
`C:\Program Files (x86)\Steam\steamapps\common` nicht füllen.** Dazu kommt die
Wirkungsgrenze: `STEAM_COMMON` erreicht nur `where_to_start_looking`, also den
**Startordner des Dialogs** — kein `looks_like_the_game`, kein `read_bytes`,
kein `CDLL`, ohne Klick nichts.

**Auswirkung:** Keine für den Befundangreifer.

**Behebungsrichtung:** Mit dem SEC-036-Fix mitnehmen, aber **als Aufräumen
(Niedrig), nicht als Teil der Schliessung**.

> **Antwort auf Frage 1 des Auftrags, mit Widerspruch.** Die Director-Notiz
> „sonst ist SEC-036 formal zu und sachlich offen" ist **zu stark**. Richtig
> wäre: *sachlich zu gegen den Angreifer des Befundtexts; `STEAM_COMMON` bleibt
> eine Härtung.* **Randbedingung, die ich mitnenne:** gemessen am 12.09.2026
> auf **einer** Maschine, und `C:\Program Files (x86)\Steam` existiert hier
> **nicht** — gemessen ist die geerbte ACL des Elternordners, nicht die, die
> Steams Installer setzen würde. Läuft das Programm als Administrator, oder
> lockert Steam die ACL, kippt die Aussage.
>
> **Und der Punkt, den der `developer` nicht genannt hat und der wichtiger ist
> als seine Einordnung:** `where_to_start_looking:485` fragt
> `gamefiles.steam_common_folders()` **vor** `STEAM_COMMON` — und
> `steam_common_folders()` läuft über **dasselbe** `_steam_roots()`, `C:\Steam`
> inbegriffen. Die Dialog-Startfläche wird also von der SEC-036-Wurzel selbst
> mitgespeist. **Ein Fix an `_steam_roots` schliesst beides**: die klicklose
> `find_game_dir`-Route *und* den Dialogstart. Seine Einordnung „niedriger als
> SEC-036" trifft zu, sein Grund ist nicht der tragende — der tragende ist die
> ACL.

---

## Beobachtungen (ohne Angriffspfad, ohne Priorität)

- **Der Diff selbst ist sauber.** `28dc45c..b33461d` fügt in `nrplanner/` und
  `nrdata/` **keine** neue Vertrauensgrenzüberschreitung hinzu. Zwei unabhängig
  formulierte Masken über die hinzugefügten Zeilen: (1)
  `subprocess|eval(|exec(|pickle|os.system|ctypes|urlopen|requests|socket|write_text|write_bytes|.unlink|shutil|CDLL`
  → 2 Treffer, beide `errortext.py`s Import von `subprocess` als
  **Klassenreferenz** für die `TimeoutExpired`-Abbildung, kein Start; (2)
  `environ|json.|.load|pathlib|os.path|decode(` → **0** Treffer. Alle neuen
  Importe sind projektintern (`errortext`, `binary`, `gamepath`, `paths`,
  `shortcut`) oder stdlib für die Fehlertabelle (`errno`, `struct`).
  `relicpicker.py` (+174) und `advisor/goals.py` (+176) rechnen auf bereits
  geladenen Daten; kein neuer Rich-Text-Sink
  (`setToolTip|setText|setTextFormat|RichText|setHtml` über hinzugefügte
  Zeilen: 0).
- **Die `NotWhatItClaims`-Zusage steht in einer Docstring und wird in 2 von 11
  Modulen gehalten.** Die Klassen-Docstring (`binary.py:21-26`) trifft eine
  tragende Unterscheidung, auf die `errortext` handelt: dateigetriebene Absage
  ⇒ `NotWhatItClaims` (zitiert), Programmfehler ⇒ blankes `ValueError`
  (abgebildet). T-193 hat `binary.py` und `savefile.py` umgestellt. Weiterhin
  blankes `ValueError` für offenkundig **dateigetriebene** Fälle: `dcx.py:26,53`,
  `dds.py:67,69,80,105,110`, `dvdbnd.py:39,48,56,73,87`, `fmg.py:35,40,57`,
  `tpf.py:25`, `bnd4.py:51`, `extract.py:1529,1542`, `paramdef.py:94,110` —
  **gezählt: 22 Fundstellen in 9 Modulen**. Die Wirkung ist **fail-closed** (ein
  echter Dateifehler erscheint als der allgemeine Satz statt als der eigene),
  also A7/Verständlichkeit, **nicht** Sicherheit. Genau deshalb ist es hier eine
  Beobachtung und kein Befund. Die Zahl gehört dem `director`, nicht mir.
- **Die Gegenzahl zu T-197s zwei Verengungen.**
  `tests/test_hostile_gamedata.py`: 8× `pytest.raises(ValueError)`, 2×
  `NotWhatItClaims`. `tests/test_hostile_savefile.py`: **21× `ValueError`, 0×
  `NotWhatItClaims`** — obwohl T-193 `savefile.py` **vollständig** umgestellt
  hat. Weil `NotWhatItClaims ⊂ ValueError`, bleiben diese 21 grün, wenn eine
  Absage über feindliche Saves zu einem blanken `ValueError` zurückfällt — was
  nach dem neuen Klassenvertrag „ein Fehler im Programm" heisst. Das ist der
  **unverengte Rest** auf genau der Achse, die der Auftrag genannt hat.

---

## Antworten auf die vier Auftragsfragen, knapp

**1. SEC-036 / `STEAM_COMMON`** → F6. Sachlich zu nach dem Fix; `STEAM_COMMON`
ist Härtung, weil sein Wurzelordner admin-schreibgeschützt ist (gemessen). Die
Director-Notiz ist zu stark. Der Fix muss trotzdem an `_steam_roots` ansetzen,
weil das den Dialogstart mitschliesst. Dazu F2: der Wächter bindet das Ergebnis
nicht.

**2. SEC-023, Pfadhälfte** → **Sie hält für die Bauform, die SEC-023
beschreibt** (eine gefangene `OSError`, an einer Senke zitiert), **und sie
trägt nicht als allgemeine Zusicherung, dass kein Pfad die Fläche erreicht.**
Der Wächter ist überdurchschnittlich gut gebaut — Positivkontrolle,
schrumpf-nur-`STILL_QUOTING` (2 Einträge), Veraltungs-Selbstprüfung, 80 Tests
grün. Was er nicht sieht: `exc.filename` (F4), Alias, Ablegen-dann-zitieren,
und — die Modelllücke — **`raise`-Stellen eigener Klassen**. Belegt:
`oodle.py:58-61` interpoliert `game_dir`, und `errortext.in_english` gibt den
Pfad **wörtlich mit Backslashes** zurück (gemessen). **Das ist trotzdem kein
Leck** und ich führe es nicht als Befund: es ist der *Spiel*ordner, nicht der
Save-Ordner (kein AK-126-Konto-Id), und A2/A3 zeigen den Spielpfad absichtlich
als `PATH`-Zeile (AK-129). Der Satz „die Pfadhälfte ist drin" ist also wahr —
er darf nur nicht als „kein Pfad erreicht die Fläche" weiterzitiert werden.

**3. `texture2ddecoder` / Angriffsmodell** → **Das Modell stimmt weiter, und
T-197s zwei Verengungen haben es strikt gestärkt** (`NotWhatItClaims ⊂
ValueError`, beide Tests fordern jetzt mehr). Verifiziert: `texture2ddecoder
1.0.6` importierbar aus `site-packages`, `nrdata`/`nrplanner` aus dem
Arbeitsbaum (nicht aus einer installierten Kopie). **80 passed in 39,33 s**
über `test_hostile_gamedata.py` + `test_exception_text_is_english.py` +
`test_game_dir_recognition.py`. Zwei Dinge auf derselben Achse stimmen nicht:
F5 (T-193 hat `binary.magic` über die Zitatgrenze geschoben, 4 Byte) und die 21
unverengten Erwartungen in `test_hostile_savefile.py` (Beobachtung).

**4. QA-237 / die Überlagerung** → **Sie entkräftet keine der vier.** Keine
ruht auf einem Schreibnachweis: SEC-016/017/018 sind Dekompressionsbomben, ihr
Beleg ist **gemessener Spitzenhaufen** (3,2 GiB; Faktor 1029) — eine
In-Process-RAM-Messung, die eine Dateisystem-Überlagerung nicht berührt; ihre
**Schliessung** ruht auf einem Vertrauensargument des Nutzers. SEC-026 ist
`ctypes.CDLL`, also **lesen und ausführen**, kein Schreiben.

Entkräftet ist ein **anderer** Satz, und das Projekt sollte ihn nicht mehr
sagen: *„dieser Lauf hat nicht in Nutzerdaten geschrieben."* Die Trennlinie,
die überlebt, entscheidet, was künftige Läufe behaupten dürfen:

- **Positive Pfadauflösungs-Nachweise halten** und sind die zu benutzende Form
  — ich habe `paths.cache_dir()` aus dem Prozess zurückgelesen und den
  Scratchpad erhalten. Das ist eine Aussage darüber, *welchen Pfad der Code
  berechnet*; die Überlagerung berührt sie nicht.
- **Abwesenheits-Nachweise halten nicht** — der Blick geht durch dieselbe
  Überlagerung wie der Schreibvorgang.

Die CLAUDE.md-Regel („weist jede Umlenkung nach") bleibt also **erfüllbar, aber
nur in ihrer positiven Form** — das sollte dort stehen, sonst produziert jeder
Lauf weiter die unbeweisbare Hälfte.

**Zur Gegenbeobachtung, die ich nicht wegerkläre: sie lokalisiert die Grenze,
und es ist die Prozessgrenze.** `shortcut.create()` schreibt die `.lnk` **nicht
aus Python**. Sie startet `powershell.exe` (`subprocess.run`, `:126-131`), das
den **prozessexternen** COM-Server `WScript.Shell` zum `Save()` bringt; der
einzige Python-seitige Schreibvorgang dort ist `path.parent.mkdir(...)` in
`:125`. Die eine dokumentierte Flucht ging also durch den einen Codepfad des
Programms, dessen Schreibvorgang ein **Kindprozess** ausführt. Hypothese, als
solche gekennzeichnet und billig zu prüfen: *die Überlagerung fängt die
Dateiaufrufe dieses Prozesses und folgt keinem Kind.* Hält sie, dann gilt: die
`APPDATA`-Umlenkung schützt das Start-Menü weiterhin, weil `start_menu_dir()`
`APPDATA` **in Python** liest und den Wert über `env` (`:116`) an das Kind gibt
— am 07.09.2026 waren nur **zwei von drei** Variablen umgelenkt, Mechanismus
und Vorfall stimmen überein. Aber: **jeder künftige
Kindprozess-Schreibvorgang liegt aussen**, die Überlagerung ist kein
Sicherheitsnetz, und die Drei-Variablen-Umlenkung ist die **einzige**
Absicherung der 309 Relikte und ~110 Builds. Das sollte so dastehen statt als
„die Überlagerung hat es ohnehin gefangen".

---

## Geprüft / nicht geprüft

**Geprüft:** Diff `28dc45c..b33461d` (13 Codedateien, +685/-136, zwei
unabhängige Masken); `gamefiles.py` vollständig; `firstrun.py` in vier
Abschnitten; `errortext.py` vollständig; `binary.py` vollständig; `dcx.py`
vollständig; `oodle.py:25-93`; `shortcut.py:36-154`; der SEC-023-Wächter mit
eigener Positivkontrolle; der SEC-036-Wächter mit Ausführungszählung; ACLs von
`C:\` und `C:\Program Files (x86)`; PowerShell-`stderr`-Form; 80 + 110 Tests.

**Nicht geprüft, und warum:** Kein Fensterlauf — QA-231 (fester Testabzug
fehlt) ist laut `CLAUDE.md` **vor** der Baurunde zu beheben, und ein Neuaufbau
kostet ~107 s plus ein `Planner`-Absturz an alter `extract_version`; für alle
Befunde hier genügte der Quelltext plus In-Process-Messung. **Keine
Volllaufzahl** — mein Auftrag ist eine Prüfung, kein Regressionslauf, und der
`qa-engineer` fährt denselben Stand parallel (T-201); seine Zahl gegen 1257/9/0
ist verbindlich, nicht meine. **SEC-019/SEC-021** (AutoText-Klasse) nicht neu
vermessen — vom Nutzer auf Mittel gesenkt, und der Diff fügt keinen Sink hinzu
(gemessen: 0). **SEC-026 selbst** nicht neu bewertet — liegt beim Nutzer.
**`C:\Program Files (x86)\Steam`** ACL nicht messbar (existiert nicht). **Die
Prozessgrenzen-Hypothese zu QA-237** nicht gegengeprüft — das wäre ein
Schreibversuch aus einem Kindprozess in einen echten Nutzerpfad, und den führe
ich nicht aus.

---

## Sicherheits-Log — Inhalt für `security/findings.md`

Bestehende Datei gelesen (54 Zeilen, SEC-001…SEC-036). **Fortführung, keine
Neuanlage.** IDs vergibt der `director` — die neuen Zeilen tragen keine.

**Statusfortschreibung an bestehenden Zeilen:**

| ID | Änderung | Letzte Prüfung |
|---|---|---|
| SEC-016 | Zusatz: *Code unverändert bei `b33461d` (`dcx.py:38-40`). **Die Freigabebedingung vom 05.09.2026 beschreibt das Programm nicht mehr** — A15 liefert eine Route über einen frei gezeigten Ordner, der weder „boesartige Installation" noch „uebernommenes Konto" ist. Nicht erneut vorgelegt; die Randbedingung der Annahme ist gewechselt, Entscheidung beim Director/Nutzer (T-202)* | 2026-09-12 |
| SEC-017 | Zusatz: *wie SEC-016. Beleg ist gemessener Spitzenhaufen, eine In-Process-Messung — **von QA-237 nicht berührt** (T-202)* | 2026-09-12 |
| SEC-018 | Zusatz: *wie SEC-016; `dcx.py:42` weiterhin `zlib.decompress(payload)` ohne Deckel und ohne `bufsize`, unverändert bei `b33461d` (T-202)* | 2026-09-12 |
| SEC-023 | Zusatz: *Pfadhälfte hält **für die Bauform des Befundtexts** (eine gefangene `OSError`, an einer Senke zitiert); Wächter mit Positivkontrolle, Schrumpf-Liste und Veraltungsprüfung, 80 Tests grün. **Nicht** allgemein: `exc.filename` ungedeckt (0 Fundstellen heute), Alias und Ablegen-dann-zitieren ungedeckt, `raise`-Stellen eigener Klassen ungedeckt (`oodle.py:58` trägt den Spielpfad wörtlich — kein Leck, A2/A3 zeigen ihn absichtlich). **Nicht als „kein Pfad erreicht die Fläche" weiterzitieren** (T-202)* | 2026-09-12 |
| SEC-026 | Zusatz: *Falle präzisiert: Härtung über **Herkunft** stellt die Vertrauensannahme von SEC-016/017/018 wieder her und hält sie geschlossen; Härtung über **Zustimmung** (ein Klick) tut das nicht. Unabhängig davon ist die Bedingung schon bei `b33461d` abgelaufen (T-202)* | 2026-09-12 |
| SEC-036 | Zusatz: *Prämisse am System bestätigt (`icacls C:\` → `Authenticated Users:(AD)`). **Korrektur der Director-Notiz:** „sonst sachlich offen" ist zu stark — `C:\Program Files (x86)` gibt `BUILTIN\Users` nur `(RX)`, SEC-036s Angreifer (zweites unprivilegiertes Konto) kann `STEAM_COMMON` nicht füllen; es ist Härtung. Randbedingung: eine Maschine, 12.09.2026, und `C:\Program Files (x86)\Steam` existiert dort nicht. **Der Fix muss an `_steam_roots` ansetzen** — `where_to_start_looking:485` speist den Dialogstart über `steam_common_folders()` aus derselben Wurzel (T-202)* | 2026-09-12 |

**Neue Zeilen (IDs offen):**

| ID | Titel | Prioritaet | Status | Letzte Pruefung |
|---|---|---|---|---|
| *(neu)* | Freigabebedingung von SEC-016/017/018 abgelaufen: A15 liefert einen frei gezeigten Ordner, der weder bösartige Installation noch übernommenes Konto ist; `looks_like_the_game` prüft nur drei Dateien, die der Angreifer selbst füllt; danach `dcx.decompress` mit `max_output_size` aus der Datei und `DFLT` ohne Deckel (`dcx.py:38-40/42`, `tpf.py:25-53`, Auslöser `firstrun.py:1025`) | Mittel | offen — keine Codeänderung, eine Entscheidung: Freigabetext nachziehen oder Deckel nachziehen. Nutzerentscheid „nicht erneut vorlegen" respektiert, nur die gewechselte Randbedingung gemeldet | 2026-09-12 |
| *(neu)* | Der Wächter zu SEC-036 kann an der festen Wurzel nicht rot werden: `tests/test_game_dir_recognition.py:143-156` stubbt `_steam_roots`; gemessen über 3 Testdateien / 110 Tests lief der echte Körper 26× und gab beide feste Wurzeln zurück, 5/5 Fundstellen in `tests/` sind Stubs, 0 binden die Liste, 0 Testdateien nennen `Program Files` oder `C:\Steam`. Unsichtbar nur, weil beide auf dieser Maschine nicht existieren | Mittel | offen — Behebung: ein Fall, der `_steam_roots()` aufruft, die Registry-Hälfte fälscht und die Liste gegen ein Literal hält | 2026-09-12 |
| *(neu)* | `shortcut.create():138-140` gibt PowerShells `stderr` wörtlich zurück — zwei Zeilen unter der von QA-211 geschlossenen Ausnahmehälfte, und kein Wächter sieht es (es ist keine Ausnahme). Gemessen: `stderr` trägt den vollen `.lnk`-Pfad (Benutzername), `detail[0]` schneidet ihn am 128-Zeichen-Umbruch mitten im Pfad ab; Sprachhälfte Hypothese (diese Maschine `en-GB`) | Niedrig | offen — Behebung: Ausgang des Kindes auf einen Satz dieses Repositorys abbilden; `returncode` ist eine Zahl und spricht keine Sprache | 2026-09-12 |
| *(neu)* | Härtung: `WORDING_ATTRIBUTES` (`test_exception_text_is_english.py:77`) deckt `strerror` (den Sprachträger) und **nicht** `filename`/`filename2` (den reinen Pfadträger) — obwohl die eigene Docstring derselben Datei `filename` als Pfadträger benennt. Heute 0 Fundstellen; Alias- und Ablegen-Form ebenfalls ungedeckt (Positivkontrolle: Scan gibt `[]`) | Niedrig | offen — `filename`/`filename2` aufnehmen; Alias/Ablegen als bekannte Decke dokumentieren statt bauen | 2026-09-12 |
| *(neu)* | Härtung: T-193 hat `binary.magic` (`binary.py:91-94`) aus dem abbildenden in den zitierenden `errortext`-Zweig verschoben; 4 Byte Dateiinhalt erreichen die Fläche wörtlich (gemessen vorher/nachher). Deckel = `len(expected)` der zwei Aufrufstellen (`bnd4.py:91/141`, je 4 Byte), keine SEC-019-Eskalation möglich (holende Marke braucht ≥11 Zeichen) — aber der Deckel ist Eigenschaft der Aufrufstellen, nicht des zitierenden Codes | Niedrig | offen — `got={got!r}` fallen lassen oder im `raise` begrenzen | 2026-09-12 |
| *(neu)* | Härtung: `firstrun.STEAM_COMMON` (`:153`, benutzt `:486`) ist nach einem SEC-036-Fix die letzte feste Wurzel, aber **nicht** der Angreifer von SEC-036 — Wurzelordner admin-schreibgeschützt (gemessen), Wirkung nur Dialogstartordner, kein Lesen ohne Klick. Mit dem Fix mitnehmen als Aufräumen | Niedrig | offen — Härtung, nicht Teil der SEC-036-Schliessung | 2026-09-12 |

---

## Zusammenfassung an director

**Befunde je Priorität:** Kritisch 0 · Hoch 0 · **Mittel 2** (abgelaufene
Freigabebedingung SEC-016/017/018; SEC-036-Wächter bindet nicht) · **Niedrig 4**
(PowerShell-`stderr` auf der Fläche; `exc.filename` ungedeckt; `binary.magic`
4 Byte; `STEAM_COMMON`) · Beobachtungen 3.

**Gesamturteil: CONCERNS.**

Der Diff selbst ist die beste Nachricht: +685 Zeilen Code und **keine** neue
Vertrauensgrenzüberschreitung, mit zwei unabhängigen Masken belegt. Die Befunde
sitzen alle an den Stellen, die du vorgelegt hast — und zweimal einen Schritt
weiter auf der Achse, als der Befundtext sie beschrieb (F2: der Wächter zu
SEC-036 *stubbt* genau die Zeilen, für die er zitiert wird; F3: QA-211 hat den
Start-Menü-Knopf geschlossen und zwei Zeilen tiefer dieselbe Fläche offen
gelassen).

**Drei Entscheidungen liegen bei dir, nicht bei mir:**

1. **Die abgelaufene Randbedingung von SEC-016/017/018.** Der Nutzer hat „nicht
   erneut vorlegen" geschrieben, und ich lege sie nicht vor — aber der Satz, auf
   dem die Freigabe ruht, beschreibt das Programm seit A15 nicht mehr. Entweder
   Text nachziehen oder Deckel nachziehen; beides ist klein.
2. **Ob F2 vor oder nach dem SEC-036-Fix gebaut wird.** Ich empfehle
   **vorher**: sonst hat der Fix keine rote Phase.
3. **SEC-027 liegt ausserhalb meines Bereichs und ist im Register Hoch/offen**
   („Panel-Text A1 verspricht `It is only read`", Wortlaut vor V2). Mein
   CONCERNS gilt für `28dc45c..b33461d` plus deine vier Fragen; nach der
   Vierwerte-Regel hält ein offenes Hoch das Release-Tor zu, und diese Zeile ist
   es. Das ist dein Entscheid, nicht meiner — ich sage nur, dass mein
   PASS-Nachbar daran hängt und nicht an meinen Befunden.

**Was ich dir für die nächste Runde mitgebe, auch wenn es nicht mein Auftrag
war:** die CLAUDE.md-Zeile „weist jede Umlenkung nach" ist nach QA-237 nur noch
in ihrer **positiven** Form erfüllbar (Pfadauflösung aus dem Prozess
zurücklesen — so habe ich es gemacht). Steht das nicht dort, produziert jeder
Lauf weiter die unbeweisbare Hälfte und meldet sie als Nachweis. Und: die
Überlagerung ist **kein** Sicherheitsnetz — die eine dokumentierte Flucht ging
durch den einen Kindprozess-Schreibvorgang des Programms, also ist die
Drei-Variablen-Umlenkung die einzige Absicherung der 309 Relikte.

**Messwerte dieses Laufs:** 80 passed in 39,33 s (`test_hostile_gamedata.py` +
`test_exception_text_is_english.py` + `test_game_dir_recognition.py`); 110
passed in 2,25 s (die drei Steam-/Firstrun-Dateien, mit Zählplugin). Kein
Volllauf — der gehört T-201. Kein Server gestartet, also kein Port zu prüfen.
Scratchpad `.../scratchpad/T-202/` angelegt und restlos entfernt, geprüft.
`git status` leer.
