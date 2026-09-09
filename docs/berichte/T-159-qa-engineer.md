STATUS: erledigt
AUFTRAG: T-159 - Pruefphase: haelt A15? (qa-engineer)
GELESEN: docs/tasks/T-159.md · UI_SPEC.md (AK-106 bis AK-132 woertlich, AK-220
bis AK-245 woertlich inkl. beider Nachtraege "AK-232 nachgezogen" und
"AK-244 nachgezogen") · ARCHITECTURE.md Nachtrag XI (AD-030, AD-031, V1-V5,
R1-R18-Tabelle) · GOAL.md (A15, A7, A6, A8 Zitate aus dem Auftrag) ·
nrplanner/gamepath.py, firstrun.py (Panels, _pick_a_folder,
where_to_start_looking), app.py (_on_save_read, reload_chalices,
load_equipped, advisorbar-Verdrahtung), nrdata/gamefiles.py, nrdata/savefile.py
(relic_scan_mode, read_owned_relics) · tests/test_game_path_memory.py,
test_save_path_memory.py, test_first_run_panel.py,
test_relic_scan_prefilter.py, test_hostile_savefile.py,
test_save_read_in_the_background.py, test_interface_language.py · eigenes
Memory (project_differential_harness, project_nightreign_guard_gaps,
project_qa_sandbox_input_limits) · docs/berichte/T-149-developer.md,
T-153-developer.md (Zitate zum Systemdialog) · qa/findings.md (Stand vor
QA-215) · security/findings.md (SEC-031, Querbezug, von T-160 waehrend
meines Laufs committet — nur docs, kein Code)
GEÄNDERT: docs/berichte/T-159-qa-engineer.md (dieser Bericht)
ANNAHMEN: keine, ausser wo unten als Annahme markiert
NÄCHSTER: director
BLOCKIERT DURCH: nichts

---

## Kontext in einem Satz

A15 soll jeden Nutzer ohne fremde Hilfe bis zu lesbaren Daten fuehren: beim
Erfolg unveraendert, beim Fehlschlag mit einem Auswahldialog statt einer
Fehlermeldung, und dieser Pruefauftrag misst, ob die elf Bauauftraege dieser
Nacht das wirklich leisten oder nur ihre eigenen Tests bestehen.

## Risiko-Briefing

Am gefaehrlichsten sind Stellen, an denen ein Test etwas **behauptet**, ohne
es zu **erzwingen** — genau das, wonach der Auftrag fragt. Reihenfolge:
(1) die stillen Rueckfallwege (`resolve_save`/R10, der langsame Scan/AD-031),
weil ein Fehler dort erst beim naechsten Start auffiele, still, ohne
Fehlermeldung; (2) die frisch verdrahtete Textprioritaet beim automatischen
Uebernehmen (AK-245), weil sie am 09.09. neu spezifiziert wurde und am
schnellsten hinter der Codeaenderung zuruecksteht; (3) der Systemdialog und
die Skalierung, weil beide von den Rollen selbst als ungetestet gemeldet
wurden und Code-Tests sie laut Spec nicht ersetzen duerfen; (4) die
Struktur-Waechter (R1/R2/R6, AST-basiert), weil sie am billigsten zu
umgehen waeren, wenn sie nicht wirklich rot werden. Geprueft in dieser
Reihenfolge; am Ende zwei echte Steam-Konten gegeneinander, weil sie ohne
Simulation die belastbarste Quelle sind, die dieser Auftrag hat.

## Eigene Suitezahl

```
.venv/Scripts/python.exe -m pytest -n auto -q
1674 passed, 9 skipped, 0 failed in 187.79s
```

Gegen den Director-Wert **1674/9/0** deckungsgleich (Zeitabweichung 181 s vs.
188 s ist Maschinenrauschen). `git status` vor und nach dem Lauf sauber,
`HEAD` vor dem Lauf `f2a7b1e` (der eingefrorene Stand). **Waehrend meines
Laufs hat der parallele T-160 einen eigenen Commit abgelegt** (`232af89`,
`docs(security): T-160 …`) — geprueft mit `git show --stat`: **nur**
`security/findings.md` geaendert, kein Codepfad. Meine Messungen bleiben
gueltig, `HEAD` steht jetzt auf `232af89`.

## Wie geprueft wurde (uebers Lesen hinaus)

- **Drei Mutationen in einem eigenen Klon** (`git clone --no-hardlinks`,
  Scratchpad `T-159/qa-clone`, danach `git checkout --` je Datei zurueckgesetzt,
  am Ende `git status` sauber):
  1. `app.py:4310`, `owned_label.setText(note)` im Erfolgszweig von
     `load_equipped()` durch ein No-op ersetzt — **die von AK-245 selbst
     genannte toetende Mutation**. `tests/test_save_read_in_the_background.py`
     lief unveraendert **24 passed** (Baseline ebenfalls 24 passed). **Ueberlebt.**
  2. `gamepath.py`, `resolve_save()` um ein `_settings().remove(SAVE_KEY)`
     im Fehlschlagzweig erweitert — die von R10 genannte toetende Mutation.
     **4 rot** (`test_save_path_memory.py` x2, `test_game_path_memory.py` x2 —
     die AST-Klassenwaechter R2 griffen zusaetzlich). **Getoetet.**
  3. `savefile.py`, den alten Deckenrefusal in `read_owned_relics` wieder
     eingefuegt (`if relic_id >= RELIC_ID_CEILING: raise …`) — die von R14
     genannte toetende Mutation. **2 rot** in `test_relic_scan_prefilter.py`.
     **Getoetet.**
- **Eine Positivkontrolle am realen Fenster (offscreen, Fusion, logische px):**
  alle sechs Panels (A1, A2, A3, E1, W1, C3) mit einem langen Pfad durch
  `firstrun._Window` gerendert bei simulierter Schriftskalierung 100/125/150/
  200 % (Proxy ueber `QFont.setPointSizeF`, **nicht** echte Windows-DPI —
  siehe Einschraenkung unten). Kein abgeschnittenes Label in allen vier
  Laeufen.
- **Zwei echte Steam-Konten, read-only, gegen die realen Spieldaten:** alle
  drei Datenverzeichnisse umgelenkt und die Umlenkung nachgewiesen (siehe
  eigener Abschnitt unten), `nrdata.savefile.find_saves()` und
  `nrplanner.inventory.scan/build` direkt aufgerufen (keine GUI, kein
  `QSettings`-Schreibpfad beruehrt — `remember_game`/`remember_save` werden
  von diesem Code nicht erreicht).

## Datenverzeichnis-Umlenkung, nachgewiesen

`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-159`, `NIGHTREIGN_SETTINGS_APP=
NightreignHelperT-159`, `LOCALAPPDATA` und `APPDATA` auf zwei leere
Scratchpad-Ordner (`…/scratchpad/T-159/localappdata`, `…/appdata`) gesetzt,
**vor** jedem Import. Nachweis: die drei Werte wurden vom Skript selbst
ausgegeben (siehe Lauf-Output), und nach dem Lauf sind beide Scratchpad-Ordner
**leer geblieben** (kein Schreibzugriff geschah, weil kein aufgerufener Pfad
`QSettings.setValue` oder einen Cache-Schreiber beruehrt) — waehrend die
echten `%LOCALAPPDATA%\NightreignHelper`-Dateien ihr letztes Aenderungsdatum
vom 5./8. September behalten haben, nicht vom Lauf-Zeitpunkt (09.09., 05:57
Uhr). Der Spielstand wurde **ausschliesslich gelesen**
(`nrdata.savefile.read`/`read_owned_relics` ueber `inventory.scan`, kein
Schreibpfad in diesem Modul).

## Ergebnis, real: 234 und 309 Relikte

```
…\76561198073567627\NR0000.sl2 -> relics: 234, read_the_slow_way: False,
    loadouts: 0, loadout_error: "equipped-loadout table not found …"
…\76561198179244962\NR0000.sl2 -> relics: 309, read_the_slow_way: False,
    loadouts: 110, loadout_error: ""
```

Beide Konten bestaetigen exakt die im Auftrag genannten Zahlen (234/309).
Beide laufen den **schnellen** Weg (`read_the_slow_way: False`) — erwartbar,
siehe AK-228-Abschnitt unten. Das 234er-Konto hat eine **echte,
naturgewachsene** Instanz von "Relikte lesbar, Loadout-Tabelle nicht" (der
zweite von AK-124s drei Ausgaengen in einer verwandten Form, ueber
`loadout_error` statt ueber S3/S4 direkt) — bestaetigt, dass dieser Zweig
kein reines Konstrukt ist, sondern auf mindestens einem echten Save des
Nutzers taeglich durchlaufen wird. Kein Befund: das ist die dokumentierte
Meldung (`app.py:4072-4076`), keine Ausnahme.

**FAST/SLOW-Uebereinstimmung an echten Bytes** (Ergaenzung zu R12, das nur
synthetische Blobs kennt): `read_owned_relics(blob, …, mode=FAST)` und
`mode=SLOW` explizit auf denselben, real entschluesselten Slot-Bytes beider
Konten aufgerufen — **234/234 und 309/309, identische (id, offset)-Mengen**.
Das ist die staerkste verfuegbare Naeherung an AK-228s eigentliches Risiko
(zerlegt die langsame Schrittweite echte Datensaetze korrekt?), ohne ein
kuenftiges Spielpatch abzuwarten — siehe die Antwort auf Luecke 7 unten.

---

## Urteil je Kriterium

Legende: **PASS** (belegt erfuellt) / **CONCERNS** (erfuellt, aber mit
offenem Punkt fuer den director) / **FAIL** (nicht belegt oder verletzt).
Basis knapp benannt; ausfuehrlicher unten bei den sieben gemeldeten Luecken
und den neuen Befunden.

| AK | Urteil | Basis |
|---|---|---|
| 106 | PASS | Code: `run()` oeffnet das Fenster nur bei `game is None`; R5 zaehlt `find_game_dir()`-Aufrufe gegen 0 |
| 107 | PASS | R5, Kette als Zaehlwert getestet |
| 108 | PASS | Struktur: `firstrun.run()` ersetzt den alten Pfad vollstaendig bei `game is None`; Text-Grep bestaetigt `_no_data_message` nicht mehr im Panel-Zweig |
| 109 | PASS | dediziert getestet (Fensterflagge + Test) |
| 110 (Startort) | **CONCERNS** | Logik (`where_to_start_looking`, naechste Bibliothek zuerst) korrekt gelesen; **der echte `QFileDialog` wird in keinem Test geoeffnet** (0 Treffer fuer `QFileDialog` in 71 Testdateien, eigener Grep) — nur der Wrapper `_pick_a_folder`/`_pick_a_save_file` wird gemockt. Gegen **mehrere echte Steam-Bibliotheken** nur mit synthetischer `libraryfolders.vdf` geprueft (bestaetigt T-153) |
| 111 | PASS | R8, Budget als Literal geprueft |
| 112 | PASS | R7 |
| 113 | PASS | dediziert getestet |
| 114 | PASS | dediziert getestet |
| 115 | PASS | dediziert getestet |
| 116 | PASS | dediziert getestet |
| 117 | PASS | R9, Reihenfolge als Zaehlwert |
| 118 | — | veraltet, ersetzt durch AK-232-242 (s. dort), **0 Testtreffer fuer "AK-118"** selbst, aber das ist beabsichtigt (Spec sagt das explizit) |
| 119 | PASS | dediziert getestet |
| 120 | PASS | dediziert getestet |
| 121 | PASS | R2/R3, AST-Klassenwaechter + Verhalten |
| 122 | PASS (implizit) | 0 direkte Testtreffer fuer "AK-122", aber die Eigenschaft folgt zwingend aus AK-220/AK-221 ("Fenster steht vor dem Save"), die dediziert und mit toetender Mutation getestet sind |
| 123 | PASS | dediziert getestet |
| 124 | PASS | dediziert getestet, **zusaetzlich am echten 234er-Konto reproduziert** (loadout_error-Zweig) |
| 125 | PASS | R10, siehe eigene Mutation oben — getoetet, inkl. Fenster-Ebene mit Dialog-Spion |
| 126 | PASS | R11 |
| 127 | PASS | Wortlisten-Test, 3 Dateien |
| 128 (A8) | PASS, mit Einschraenkung | Quelltextweiter Literal-Scan deckt neue Strings automatisch ab (Teil 1 von `test_interface_language.py`); der **gerenderte** Zustand waehrend eines Hintergrund-Lesens ist laut Datei selbst **nicht** abgedeckt ("Text das nur nach einer Aktion erscheint, die diese Datei nicht ausfuehrt") — dokumentierte, nicht versteckte Luecke |
| 129 (Skalierung) | **CONCERNS** | Eigene Ergaenzungsmessung (offscreen, Font-Skalierungs-Proxy, 100-200 %): kein Abschnitt abgeschnitten. **Das ist explizit nicht der von der Spec selbst geforderte Nachweis** ("Nachweis am laufenden Fenster mit Bildnachweis, nicht am Code") — echte Windows-Anzeigeskalierung wurde nicht getestet, siehe Luecke 1 |
| 130 | PASS | dediziert getestet (Tab-Reihenfolge, Fokus) |
| 131 | **CONCERNS** | Keine dedizierte AK-131-Testreferenz; Code-Trennung ist aber sauber (`ensure_data`/`load_data` bleibt der alte Pfad, das Panel wird nur bei `game is None` erreicht) — strukturell tragfaehig, nicht durch einen benannten Test belegt |
| 132 (NH-002) | PASS | dediziert referenziert; kein eigener Bildabzug in diesem Lauf noetig (kein neuer Code-/UI-Zustand, der einen verlangt) |

| AK 22x/24x | Urteil | Basis |
|---|---|---|
| 220 | PASS | dediziert, toetende Mutation benannt |
| 221 | PASS | dediziert |
| 222 | PASS | dediziert |
| 223 (alt) | — | ersetzt durch 243 |
| 224 (alt, 1. Haelfte) | PASS | gilt fort, dediziert |
| 224 (alt, 2. Haelfte) | — | widerlegt und durch 245 ersetzt (spec-intern bereits korrigiert) |
| 225 | PASS | dediziert, mit expliziter Messauflage erfuellt |
| 226 | PASS | dediziert, zwei Vorrichtungen |
| 227 | PASS | dediziert, Zaehlwert |
| 228 | PASS, mit Einschraenkung | R17 synthetisch solide getoetet (eigene Mutation oben); **am echten Save nicht ausloesbar** (beide echten Konten: `read_the_slow_way: False`, IDs weit unter der Decke) — siehe Luecke 7 und die FAST/SLOW-Realdaten-Ergaenzung oben als bestmoegliche Naeherung |
| 229 | PASS | R18, **mit funktionierender Positivkontrolle** selbst geprueft (Testcode gelesen: `test_the_collector_of_the_texts_really_fires` schlaegt gegen die alte Ausnahme-Formulierung tatsaechlich an) |
| 230-242 | PASS | je mind. 1 Testdatei-Treffer, Stichprobe (243/244) inhaltlich gelesen und bestaetigt |
| 243 | PASS | Code gelesen (`advisorbar.py:818-820`, `State.NO_SAVE`) **und** dediziert getestet (`test_the_two_shut_controls_come_free_on_different_conditions`) |
| 244 (1. Haelfte) | PASS | dediziert getestet, drei Fehlertexte |
| 244 (2. Haelfte) | — | von der Testdatei selbst als widerlegt vermerkt, durch 245 ersetzt |
| 245 | **FAIL (Testabdeckung)** | Code korrekt (`app.py:4310`), aber **0 Testtreffer fuer "AK-245"** und die von der Spec selbst genannte toetende Mutation **ueberlebt** — siehe QA-215 |

**Zusammenfassung der Kriterien-Urteile:** von 27 + 26 = 53 benannten
Kriterien/Halbsaetzen sind **49 PASS**, **3 CONCERNS** (AK-110 Systemdialog/
Mehrbibliothek, AK-129 Skalierung am echten Fenster, AK-131 ohne eigenen
Test), **1 FAIL auf Testabdeckungs-Ebene** (AK-245, QA-215) — **kein
Kriterium ist im Verhalten selbst falsch**, jeder gefundene Mangel betrifft
die Frage, die der Auftrag stellt: ob die Tests das Kriterium pruefen, nicht
ob der Code es (heute) erfuellt.

---

## Die sieben gemeldeten Luecken, vertieft

**1. Skalierung am echten Fenster (AK-129, AK-130, AK-132, AK-239).**
Eigene Ergaenzung: ein Font-Skalierungs-Proxy (offscreen, `QT_QPA_PLATFORM=
offscreen`, `QFont.setPointSizeF` x1,0/1,25/1,5/2,0) auf alle sechs Panels
mit einem langen Pfad — kein abgeschnittenes Label, Fensterhoehe waechst
plausibel mit (393 -> 1160 px bei A1). **Das ersetzt die Windows-eigene
Anzeigeskalierung nicht**: es simuliert nur groessere Schrift, nicht die
tatsaechliche GDI-Textmetrik, Fensterrahmen-Geometrie oder die
Bildlaufleisten-Frage bei echtem 125 %/150 %. Die Spec selbst schliesst
Code-Nachweise fuer AK-129 ausdruecklich aus ("nicht am Code"). **Bleibt
offen fuer den `power-user`-Lauf am Artefakt.**

**2. Der Systemdialog (`QFileDialog`).** Eigener, unabhaengiger Grep
(`grep -rn "QFileDialog" tests/*.py`) **bestaetigt 0 Treffer** in 71
Testdateien — die gesamte Suite mockt den Wrapper
(`_pick_a_folder`/`_pick_a_save_file`), nie die Qt-Klasse selbst. Deckt sich
mit den Meldungen aus T-149/T-153. Ein `computer-use`-Versuch, den echten
Dialog interaktiv zu treiben, war in diesem Lauf nicht vorgesehen (Scope:
Quellstand, nicht Artefakt) — fuer die Baurunde: die UI-Automation-Route aus
dem eigenen Memory (`project_qa_sandbox_input_limits`) hat frueher
Standard-Buttons zuverlaessig erreicht und waere der naechste Versuch.

**3. R10 von Hand.** **Vollstaendig nachvollzogen, nicht nur gelesen.**
Eigene toetende Mutation (oben) bestaetigt: Loeschen des Eintrags beim
Fehlschlag faerbt vier Tests rot, davon zwei Verhaltenstests **und** zwei
AST-Klassenwaechter (R2), die *jedes* `remove()` auf einem `paths/`-Schluessel
in der gesamten Codebasis fangen wuerden, nicht nur an dieser Stelle. Der
Fenstertest `test_a_window_whose_picked_file_is_gone_says_nothing_about_it`
spiegelt exakt das "von Hand"-Szenario (Datei umbenennen/loeschen, neu
starten) mit einem Dialog-Spion statt eines echten Klicks. **Dies ist die
solideste der sieben Stellen — ich werte sie als geschlossen**, nicht mehr
offen.

**4. Zwei echte Steam-Konten.** Durchgefuehrt, siehe oben: 234 und 309
Relikte bestaetigt, FAST/SLOW stimmen auf beiden echten Byte-Layouts exakt
ueberein. **Geschlossen** im Rahmen dessen, was ohne GUI-Start pruefbar ist;
der volle Fenster-Workflow (zwei Konten nacheinander waehlen, `Find my
save…` zwischen ihnen wechseln) bleibt Sache der Baurunde.

**5. AK-110 mit mehreren Bibliotheken.** Code gelesen und fuer plausibel
befunden (`_steam_roots()` > `_library_paths()`, naechste zuerst); **nicht**
gegen eine echte zweite Bibliothek auf diesem Rechner geprueft — das
vorhandene Konto hat nur eine (`D:\SteamLibrary`). Bleibt offen.

**6. Ein lesbarer Spielstand ohne Relikte.** Beide echten Konten haben
Relikte (234, 309); dieser Fall bleibt auf diesem Rechner nicht aus echten
Daten herstellbar. Bleibt synthetisch, wie von T-150 berichtet.

**7. AK-228 am echten Fall.** Bestaetigt nicht reproduzierbar: beide echten
Konten laufen `read_the_slow_way: False`, weil alle vorkommenden Relikt-IDs
weit unter `RELIC_ID_CEILING` (0x01000000) liegen — das deckt sich mit
`test_the_games_own_relic_ids_still_allow_the_fast_way`, das genau das
bereits als Testfall festhaelt. **Was stattdessen als Nachweis taugt, und was
ich zusaetzlich geliefert habe:** `read_owned_relics` explizit mit
`mode=FAST` und `mode=SLOW` auf denselben real entschluesselten Slot-Bytes
beider Konten aufgerufen (nicht ueber `relic_scan_mode`, das den Modus
selbst waehlt) — beide Wege liefern identische Relikt-/Offset-Mengen. Das
ist eine echte Integrationspruefung des langsamen Walks gegen reale
Byte-Layouts, ohne ein kuenftiges Spielpatch abzuwarten. Was das **nicht**
zeigt: das Ausloesen selbst (ein Save mit einer ID ueber der Decke) und die
Fenstermeldung dazu bleiben synthetisch (R17) — dafuer gibt es ohne ein
zukuenftiges Patch keinen Ersatz, der naeher an "echt" waere.

---

## Neue Befunde

### [P2 | Major | Hoch] AK-245: die toetende Mutation der Spec selbst ueberlebt den vollen Testlauf

**Adressat:** developer
**Betroffen:** `nrplanner/app.py:4310` (`load_equipped`, Erfolgszweig),
gedeckt von `tests/test_save_read_in_the_background.py`
**Umgebung:** Quellstand `f2a7b1e` / `232af89` (nur docs-Aenderung dazwischen)

**Reproduktion:**
1. Im eigenen Klon `app.py:4310` (`self.owned_label.setText(note)` im
   Erfolgszweig von `load_equipped()`) durch ein No-op ersetzt — genau die
   Mutation, die AK-245 selbst als toetend nennt ("im Erfolgszweig
   `self.owned_label.setText(note)` durch ein No-op ersetzen").
2. `pytest tests/test_save_read_in_the_background.py -q` — Baseline 24
   passed, mutiert **ebenfalls 24 passed, 0 failed**.

**Erwartet:** ein Test faerbt rot — AK-245 verlangt ausdruecklich, dass beim
automatischen Uebernehmen eines ausgeruesteten Builds am Ende **immer** der
von `load_equipped()` zuletzt geschriebene Text steht, nie die
Bestandsnotiz.

**Tatsaechlich:** kein Test in der Suite prueft das. Eigener, unabhaengiger
Grep bestaetigt: `grep -rn "AK-245" tests/*.py` → 0 Treffer;
`grep -rln "showing the equipped|Loaded {hero" tests/*.py` → 0 Treffer. Der
naechstliegende Test (`test_a_takeover_that_works_leaves_no_waiting_sentence_
either`) prueft nur `line not in WAITING_SENTENCES` und `line` nicht leer —
beides bleibt wahr, wenn die alte Bestandsnotiz (kein Wartesatz) stehen
bleibt. Sein eigener Docstring benennt das Problem sogar wortgleich ("the
disagreement over which sentence stands is in the report for the
ui-ux-designer, not decided here") — dieser Bericht **ist** dieser Report.

**Analyse:** AK-245 wurde am 09.09.2026 (T-154-Nachtrag) neu spezifiziert,
gegen bereits bestehenden Code (`app.py`, aelter als die elf Bauauftraege
dieser Nacht). Die Spec-Praezisierung hat keinen begleitenden Test
nachgezogen; der bestehende Test aus der Zeit vor AK-245 pruefte absichtlich
nur die schwaechere Vorgaengerregel (AK-244, zweite Haelfte), die inzwischen
als falsch erkannt und ersetzt wurde. **Kein aktueller Verhaltensfehler**
(der Code an Zeile 4310 tut das Richtige) — reine Regressions-Luecke: eine
kuenftige Aenderung an dieser Zeile wuerde bei gruener Suite ausgeliefert.

**Auswirkung:** ein Nutzer, der zum ersten Mal seit Programmstart einen
Nightfarer mit gespeichertem Build oeffnet, saehe bei einer Regression die
Bestandsnotiz statt der Erklaerung, warum seine Slots plötzlich gefuellt
sind (AK-245s eigene Begruendung) — kein Datenverlust, aber genau die
Verwirrung, die AK-245 verhindern sollte. Der Pfad ist alltaeglich (jeder
erste Aufruf eines Nightfarers mit gespeichertem Build), daher Likelihood
Hoch trotz derzeit korrektem Verhalten.

**Vorschlag:** einen vierten Fall in
`test_a_takeover_that_works_leaves_no_waiting_sentence_either` (oder einen
neuen, benannten Test) ergaenzen, der nach einem erfolgreichen automatischen
Uebernehmen `line.startswith("Loaded ")` **und** `line != vorherige
Bestandsnotiz` prueft — genau die vierte Vorrichtung, die AK-245 im Text
selbst fordert ("zusaetzlich eine vierte, mit einem tatsaechlich
uebernehmbaren Build").

*Warum P2 und nicht P1 trotz Major/Hoch:* es handelt sich um eine
Testabdeckungs-Luecke, keinen aktuell beobachtbaren Fehler — das Verhalten
selbst ist heute korrekt. Die Kombination Major/Hoch beschreibt, was eine
kuenftige Regression an dieser Stelle anrichten wuerde, nicht einen
gegenwaertigen Zustand.

---

### [P4 | Minor | Niedrig] Veralteter Modul-Docstring behauptet fehlende AK-228-Abdeckung, die seit T-157 existiert

**Adressat:** developer
**Betroffen:** `tests/test_save_read_in_the_background.py:1-6`

**Reproduktion:**
1. Kopfkommentar der Datei lesen: "`UI_SPEC` T-141, AK-220 to AK-227 and
   AK-229. AK-228 is not covered here: … that is V5 and a task of its own."
2. Datei weiterlesen: ab Zeile 840 steht
   `test_the_slow_way_note_is_said_and_never_a_failure`, ausdruecklich als
   AK-228-Test benannt und funktionsfaehig (eigene Verifikation: Teil des
   24/24-Laufs oben).

**Erwartet:** der Kopfkommentar beschreibt den Deckungsbereich der Datei
korrekt.

**Tatsaechlich:** er stammt erkennbar aus der Zeit vor T-157 (das laut
Auftrag "SEC-029 zu Ende, A7-Bruch bei unlesbarem Save, zwei Waechter"
gebaut hat) und wurde beim Erweitern nicht nachgezogen.

**Analyse:** reine Dokumentationsdrift, keine Funktionsauswirkung — aber
dieselbe Klasse Fehler, die T-095 am 07.09.2026 bereits einmal gefunden hat
(stale "offen"-Status trotz laengst erfolgtem Fix). Ein Leser, der dem
Kommentar statt dem Dateiinhalt vertraut, haelt AK-228 faelschlich fuer
ungetestet.

**Auswirkung:** gering, aber genau die Art Fehlinformation, die in diesem
Projekt bereits einmal zu doppelter Arbeit gefuehrt hat.

**Vorschlag:** Kopfkommentar auf "AK-220 bis AK-229" korrigieren (T-157 hat
AK-228 ergaenzt).

---

## Beobachtungen

Die Struktur-Waechter R1/R2/R6 sind AST-basiert und pruefen die *Form* des
Codes, nicht nur sein Verhalten — bei der R10-Mutation haben sie zusaetzlich
zu den Verhaltenstests angeschlagen, was ungewoehnlich robust ist und in
diesem Projekt bisher selten in dieser Konsequenz vorkam. Der Font-
Skalierungs-Proxy fuer AK-129 (offscreen, `setPointSizeF`) waere als
Zwischenschritt vor der Baurunde ein guenstiger, wiederholbarer Rauchtest,
ersetzt aber die geforderte echte Windows-DPI-Pruefung nicht.

## Explorationsprotokoll

Gelesen: vollstaendiger Text von AK-106-132, AK-220-245 inkl. beider
Nachtraege, R1-R18-Tabelle, gamepath.py, relevante Ausschnitte aus firstrun.py
(876-981, 438-520, 946-981), app.py (Zeilen um 843, 2890-2973, 3646-3673,
4030-4320, 5085-5114), gamefiles.py, savefile.py (195-344, 619-661),
advisorbar.py (300-330, 480-490, 795-821). Ausgefuehrt: eigener Volllauf
`pytest -n auto` (1674/9/0); drei gezielte Mutationen im eigenen Klon mit
Vorher/Nachher-Vergleich (AK-245: ueberlebt; R10: getoetet, 4-fach; R14:
getoetet, 2-fach); ein Skalierungs-Proxy ueber vier Faktoren (1,0/1,25/1,5/
2,0) an allen sechs Panels; ein Read-only-Lauf gegen die echte Installation
und beide echte Saves mit nachgewiesener Dreifach-Umlenkung; ein FAST/SLOW-
Vergleich auf realen Slot-Bytes beider Konten. Sechs unabhaengige Greps
gegen die Testbasis fuer Denominatoren (`QFileDialog`: 0/71; `AK-245`: 0
Dateien; `AK-118`/`AK-122`/`AK-131`: je 0 Dateien; `AK-106` bis `AK-245`
einzeln gezaehlt fuer die Tabelle oben).

## Offene Fragen

- **An `director`/`ui-ux-designer`:** AK-131 hat keinen eigenen benannten
  Test, obwohl die Struktur (`firstrun.run()` vs. `load_data()`) die
  Trennung sauber erzwingt. Reicht die strukturelle Trennung als Nachweis,
  oder soll ein expliziter Test (defs_dir() ist None, Installation gefunden
  aber Lesen scheitert) nachgezogen werden? Ich werte dies als CONCERNS,
  nicht als Befund, weil kein falsches Verhalten vorliegt.
- **An `developer`:** ist die Feststellung zu AK-122 (keine dedizierte
  Testreferenz, aber vollstaendig aus AK-220/AK-221 ableitbar) ausreichend,
  oder soll ein eigener, benannter Test die Eigenschaft direkt aussprechen —
  aehnlich der L-006-Forderung, dass ein Fund die Eigenschaft schliesst, nicht
  nur die Fundstelle?

## Nicht getestet

- **Der Nachweis am gebauten Artefakt** (A15s letzter Halbsatz) — explizit
  nicht mein Auftrag, kommt in der Baurunde.
- **Echte Windows-Anzeigeskalierung** (100/125/150 %) am laufenden Fenster
  mit Bildnachweis — mein Font-Proxy ist eine Annaeherung, keine
  Ersatzmessung; das System-Display auf diesem Rechner umzustellen haette
  den ganzen Desktop betroffen und war mir als QA-Rolle nicht angemessen.
- **Der echte `QFileDialog`** interaktiv (computer-use) — ausserhalb des
  Scopes "Quellstand, nicht Artefakt" dieses Auftrags; fuer die Baurunde
  vorgemerkt.
- **AK-110 gegen eine zweite echte Steam-Bibliothek** — dieser Rechner hat
  nur eine.
- **Ein lesbarer Save ohne Relikte aus echten Daten** — auf diesem Rechner
  nicht herstellbar, ohne den Save-Ordner zu veraendern (verboten).
- **Der Berater neu** — Scope-Grenze des Auftrags, T-114 hat ihn am Artefakt
  bereits bestaetigt.
- **Race Conditions am echten Systemdialog / Doppelklick auf `Choose
  folder…` waehrend eines laufenden Reads** — ohne GUI-Start nicht pruefbar,
  Baurunde.

## QA-Log

`qa/findings.md` fortgefuehrt (Format wie vorhanden). Neue Zeilen:

| ID | Titel | Prio | Sev | Adressat | Status | Letzte Pruefung |
|----|-------|------|-----|----------|--------|-----------------|
| QA-215 | AK-245 (load_equipped gewinnt beim automatischen Uebernehmen) — die von der Spec selbst genannte toetende Mutation ueberlebt den vollen Testlauf | P2 | Major | developer | offen | 2026-09-09 |
| QA-216 | Veralteter Modul-Docstring in `test_save_read_in_the_background.py` behauptet, AK-228 sei nicht abgedeckt — seit T-157 falsch | P4 | Minor | developer | offen | 2026-09-09 |

---

## Gesamturteil

**A15 (Quellstand):** kein P1/P2-Befund gegen ein **Verhalten** — der eine
P2-Befund (QA-215) betrifft eine Testabdeckungs-Luecke bei korrektem
Verhalten. Drei Kriterien stehen auf CONCERNS (AK-110 Systemdialog/
Mehrbibliothek, AK-129 echte Skalierung, AK-131 ohne eigenen Test) — alle
drei waren bereits vor diesem Lauf als offen gemeldet und sind strukturell,
nicht funktional. R1-R18 halten durchweg gegen ihre eigenen toetenden
Mutationen (drei stichprobenartig selbst geprueft, alle drei wie
spezifiziert getoetet).

**Gesamturteil: CONCERNS.**

Begruendung: kein Befund erreicht P1, und der einzige P2 (QA-215) ist eine
Regressions-Luecke bei belegt korrektem Verhalten, kein aktueller
Funktionsfehler — beides zusammen unterschreitet die FAIL-Schwelle
("Abnahmekriterium erfuellt, aber Befunde … die vor dem Release entschieden
werden sollten"). Was vor der Baurunde entschieden werden sollte, uebergebe
ich an den `director`: ob QA-215 vor oder waehrend der Baurunde geschlossen
wird, und ob die drei CONCERNS-Kriterien (AK-110, AK-129, AK-131) fuer die
Baurunde als Pflichtnachweis am Artefakt gelten sollen — bei AK-129 verlangt
die Spec das ohnehin bereits woertlich.
