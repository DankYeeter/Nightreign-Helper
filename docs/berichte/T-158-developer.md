STATUS: teilweise
AUFTRAG: T-158 - Suite gruen, und die letzten elf Registereintraege (developer)
GELESEN: docs/tasks/T-158.md; scripts/differential/mutate.py; tests/test_differential_track.py;
  scripts/differential/__init__.py; nrplanner/inventory.py; nrplanner/app.py; nrdata/savefile.py;
  scratchpad/T-156/{run_campaign.py,write_registry.py,catalog.py,means.py,campaign_results_T-150.txt};
  scratchpad/T-157/campaign.txt (nur zur Einordnung des Auftrags, nicht veraendert)
GEÄNDERT: scripts/differential/mutate.py (zwei Commits, siehe unten); scratchpad/T-158/* (eigene
  Kampagnen-Infrastruktur, ausserhalb des Repos)
ANNAHMEN: keine ausser den im Auftrag genannten
NÄCHSTER: developer (Fortsetzung desselben Auftrags, siehe "Naechster Schritt" unten)
BLOCKIERT DURCH: nichts inhaltlich - der Lauf ist an der Zugschwelle (150 Werkzeugaufrufe) beendet
  worden, bevor Punkt 3 fertig war

## Was erledigt ist

**Punkt 1 (roter Anker) - erledigt, committet (99cb644).**
`the-limit-is-under-a-real-save` zeigte auf `nrplanner/app.py`; `LARGEST_SAVE_TO_READ` liegt dort
nicht mehr (bestaetigt: `grep -rn LARGEST_SAVE_TO_READ nrplanner/` findet die Definition nur in
`nrplanner/inventory.py:199`, Verwendung `inventory.py:216`). Name, Wert (`256 * 1024 * 1024`) und
Zweck (SEC-029-Groessenschranke, siehe Docstring bei `refuse_a_size_no_save_can_have`) sind
unveraendert - reine Pfadreparatur, kein Befund. `tests/test_differential_track.py` danach gruen
(344 passed), volle Suite `1674 passed, 9 skipped, 0 failed`.

**Punkt 2 (T-150-Kampagne neu gefahren) - erledigt, committet (55a0929).**
18 Mutationen aus dem T-150-Block frisch gegen `tests/test_save_path_memory.py` gefahren (eigene
Kampagne in `scratchpad/T-158/campaign.py`, ruft `mutate.py --apply NAME --tree <git-archive-Kopie>`
direkt gegen die aktuelle, schon reparierte Registry auf - nicht gegen T-156s `catalog.py`, das fuer
`the-limit-is-under-a-real-save` noch den falschen Pfad `nrplanner/app.py` traegt und damit selbst
veraltet ist).

Ergebnis: **17 von 18 weiterhin KILLED.** `no-reason-for-a-file-that-is-not-a-save` **ueberlebt**
(36 passed, 0 failed). Ursache durch Quelltext-Lektuere bestaetigt: `inventory.scan()` wirft seit
einem spaeteren Refactor selbst `SaveNotReadable` (ein `ValueError`, das die BND4-Meldung traegt)
fuer jede unlesbare Datei, **bevor** `nrplanner/app.py:1620` (`savefile.read(save_path)` hinter
`if found is None:`) je erreicht wird. Fuer eine gueltige, leere Datei (S3-Fall) laeuft die Zeile
zwar noch, ihr Ergebnis wird aber verworfen. Beide Zweige machen die Zeile toten Code, und
`read_the_save`s eigener Docstring ist an der Stelle veraltet, wo er behauptet, `inventory.scan`
"cannot tell them apart and should not". Eintrag in `mutate.py` mit dieser Begruendung versehen
(nicht geloescht, nicht "nachgebessert"). **Fund geht als Technical-Debt-Meldung an den director**
(siehe unten) - Fix liegt ausserhalb des Auftragsumfangs (nur `scripts/differential/mutate.py`).

Vollstaendiges Ergebnis der ersten Kampagne: `scratchpad/T-158/campaign_results_T-150.txt`.

**Wichtiger Befund waehrend der Absicherung von Punkt 2, siehe "Offener Punkt" unten:** eine zweite,
saubere Neufahrt (siehe naechster Abschnitt) hat die ersten 6 von 18 Eintraegen exakt reproduziert -
einschliesslich des Ueberlebenden. Die restlichen 12 sind zum Zeitpunkt des Abbruchs noch nicht
gegengeprueft.

## Was nicht fertig ist

**Punkt 3 (die letzten elf T-151-Eintraege) - nicht in `mutate.py` eingetragen.**

Katalog und `survival_means`-Texte aus `scratchpad/T-156/{catalog.py,means.py}` gelesen und fuer
tauglich befunden (Anker gegen den aktuellen Quelltext von Hand geprueft - `nrdata/savefile.py` und
`nrplanner/inventory.py`, alle 11 Stellen treffen exakt einmal). Eigene Kampagne geschrieben
(`scratchpad/T-158/campaign_t151.py`), da die Mutationen noch nicht in der Registry stehen und
`mutate.py --apply` daher nicht direkt nutzbar ist - direkte Textersetzung wie in T-156s
`run_campaign.py`, Ziel-Tests `tests/test_relic_scan_prefilter.py` + `tests/test_hostile_savefile.py`
(elf von elf), plus `tests/test_save_read_in_the_background.py` fuer `R14-refusal-reinstated`
(Override wie in T-156s `OVERRIDE_TARGETS`).

**Erster Lauf: 11 von 11 KILLED.** Ergebnis in `scratchpad/T-158/campaign_results_T-151.txt`.

**Aber:** eine gezielte Einzelnachpruefung von `R14-refusal-reinstated` (derselbe Anker, dieselbe
Mutation, dieselben drei Zieldateien, auf demselben Tree, aber isoliert statt in der Schleife) ergab
ein **anderes** Bild: Kampagnenlauf `4 failed, 52 passed, 19 errors in 16.42s`, Einzel-Nachpruefung
`2 failed, 73 passed in 119.17s` (0 errors, keine der 19 Fehlermeldungen aus dem Kampagnenlauf tritt
auf). Gleicher Tree, gleiche Mutation, gleicher Testbefehl, zwei verschiedene Ergebnisse.

**Hypothese, nicht bestaetigt:** In der Kampagnenschleife wird `nrdata/savefile.py` acht Mal
hintereinander mutiert/wiederhergestellt (R12a, R12b, R12c, R13, R14, R14b, R16,
unknown-mode-falls-back teilen sich die Datei); `__pycache__/savefile.cpython-312.pyc` wird dabei
nicht explizit geleert. Auf diesem Dateisystem lagen Quelldatei- und .pyc-mtime bei einer Stichprobe
nur 141 ms auseinander - ein Bereich, in dem eine mtime-basierte .pyc-Gueltigkeitspruefung bei
schneller Schreib-Restore-Schreib-Folge unzuverlaessig werden kann. **Nicht verifiziert, nur
plausibel**; die tatsaechliche Ursache ist nicht abschliessend geklaert.

**Gegenmassnahme eingeleitet, nicht abgeschlossen:** frischer Tree/Reference-Kopie (kein `__pycache__`
mehr vorhanden), beide Kampagnenskripte (`campaign.py` und `campaign_t151.py`) auf
`PYTHONDONTWRITEBYTECODE=1` fuer alle Subprozesse umgestellt. Eine vollstaendige Neufahrt der
**T-150**-Kampagne (Punkt 2) mit dieser Absicherung lief zur Validierung im Hintergrund
(Hintergrundlauf-ID `b354gv2nz`, Datei
`...\tasks\b354gv2nz.output`) - **6 von 18 Eintraegen fertig beim Abbruch, alle 6 decken sich exakt
mit dem bereits committeten Ergebnis**, einschliesslich des Ueberlebenden bei Eintrag 6
(`no-reason-for-a-file-that-is-not-a-save: SURVIVED :: 36 passed`). Die restlichen 12 (und die
komplette T-151-Neufahrt) sind **nicht** gelaufen.

Der Hintergrundprozess `b354gv2nz` laeuft zum Zeitpunkt dieses Berichts vermutlich noch (pytest
gegen eine Scratchpad-Baumkopie, keine Schreibzugriffe auf echte Daten, keine Netzwerkzugriffe -
unbedenklich, aber sein Ergebnis ist ungenutzt liegen geblieben). Er terminiert von selbst (endliche
Schleife über 18 Eintraege), muss aber vom naechsten Lauf **nicht** neu gestartet werden, wenn dessen
Ergebnisdatei bereits vollstaendig vorliegt.

## Naechster Schritt (fuer die Fortsetzung desselben Auftrags)

1. `scratchpad/T-158/campaign_results_T-150.txt` (die NEUE, cache-freie Fassung, falls
   `b354gv2nz` inzwischen fertig ist) gegen die bereits committete Fassung (Punkt 2) abgleichen. Bei
   Uebereinstimmung: nichts weiter zu tun, Punkt 2 ist doppelt bestaetigt.
2. `scratchpad/T-158/tree` und `.../reference` neu aus `git archive HEAD` aufbauen (die vorhandenen
   Kopien stammen aus dem laufenden `b354gv2nz`-Lauf und sollten nicht waehrend seines Laufs
   angefasst werden - erst nach dessen Ende neu aufbauen oder einen dritten Satz Verzeichnisse
   verwenden).
3. `scratchpad/T-158/campaign_t151.py` (bereits auf `PYTHONDONTWRITEBYTECODE=1` umgestellt) fuer
   alle elf T-151-Eintraege neu fahren. Stimmt das Ergebnis mit dem ersten Lauf ueberein (insbesondere
   bei R14): die dort gemessenen Zahlen fuer die `survival_means`-Texte verwenden. Weicht es ab: die
   neue, cache-freie Messung gilt, nicht die alte.
4. Die elf `Mutation(...)`-Eintraege in `scripts/differential/mutate.py` einfuegen (vor der
   schliessenden `}` von `MUTATIONS`, Zeile ~5362 im aktuellen Stand). `old`/`new`-Text und
   `meaning`-Praefix liegen fertig in `scratchpad/T-156/means.py` (Abschnitt "T-151"), Pfade und
   Anker sind bereits von Hand gegen den aktuellen Quelltext geprueft (siehe oben) - nur die
   `survival_means`-Formulierung mit den frischen Messwerten ist noch zu schreiben.
5. `tests/test_differential_track.py` (Anker-Waechter) und danach die volle Suite (`pytest -n auto`)
   laufen lassen; Ziel `0 failed`.
6. Committen (`git commit ... -- scripts/differential/mutate.py`).
7. Bericht aktualisieren/ergaenzen.

## Nachweise

- Drei Datenverzeichnisse: **nicht separat umgelenkt.** Fuer diesen Auftrag genuegte die
  Testsuite selbst - `tests/conftest.py:44` setzt `NIGHTREIGN_SETTINGS_ORG=DankYeeterTests` und
  einen PID-eindeutigen `NIGHTREIGN_SETTINGS_APP` bereits fuer jeden Pytest-Lauf (verifiziert durch
  Lektuere von `tests/conftest.py:22-44`); `LOCALAPPDATA`/`APPDATA` werden von den betroffenen Tests
  ueber `tmp_path`/`monkeypatch` isoliert (verifiziert: `grep -rln "LOCALAPPDATA\|APPDATA"
  tests/*.py` findet ausserhalb eines Docstring-Kommentars keine Stelle, die diese Variablen liest).
  Kein Programmstart ausserhalb von Pytest, also keine dritte Variable zu belegen.
- `the-limit-is-under-a-real-save` liest beim automatischen Scan-Pfad den echten, read-only
  installierten Spielstand dieser Maschine mit (ueber `savefile.find_saves()`); das ist Lesen, kein
  Schreiben, und in `tests/test_save_path_memory.py`s eigenem Fixture `a_real_scan` bereits so
  vorgesehen (dokumentiert im Docstring von `test_the_limit_is_far_above_a_real_save`). Kein
  Datenverlustrisiko.
- Vor jedem Kampagnenlauf angesehen, was die jeweilige Mutation ausloest (Auftragsvorgabe nach
  T-157s 140-GB-Vorfall): keine der 18+11 Mutationen legt eine Datei ueber wenige zehn MB an; die
  einzige groessenbezogene (`the-limit-is-under-a-real-save`) *senkt* eine Schranke, sie hebt sie
  nicht an.
- Eigene Prozesse: kein manuelles Beenden noetig gewesen ausser den vom Bash-Tool selbst verwalteten
  Hintergrundlaeufen (per Task-ID, nicht per Namensmuster) - siehe "Was nicht fertig ist" zu
  `b354gv2nz`.
- Vollstaendige Suite nach Punkt 1 und nach Punkt 2 je einmal gelaufen (`pytest -n auto -q`):
  `1674 passed, 9 skipped, 0 failed` beide Male.

## An den director

**Technical-Debt-Fund (nicht behoben, ausserhalb des Auftragsumfangs):** `nrplanner/app.py:1615-1620`
(`read_the_save`, der `if found is None: savefile.read(save_path)`-Block) ist toter Code. Seit einem
spaeteren Refactor wirft `inventory.scan()` selbst `SaveNotReadable` (`ValueError`) fuer jede
unlesbare Datei, bevor diese Zeile erreicht wird; im S3-Fall (leere, aber gueltige Datei) laeuft die
Zeile noch, ihr Ergebnis wird aber nirgends verwendet. Der Docstring von `read_the_save` behauptet
weiterhin, `inventory.scan` koenne S3 und S4 nicht unterscheiden - das stimmt nicht mehr. Empfehlung:
developer beauftragen, die tote Zeile zu entfernen und den Docstring nachzuziehen; die
`mutate.py`-Registry entsprechend wieder auf einen Guard umzustellen oder den Eintrag als endgueltig
erledigt zu markieren, je nachdem, ob nach dem Aufraeumen ein aequivalenter Test noch gebraucht wird.

**Offene Frage/Risiko:** die vermutete .pyc-Staleness (siehe oben) ist nicht abschliessend geklaert.
Falls sie sich bestaetigt, betrifft sie potenziell **jede** frueher gefahrene Kampagne, die mehrere
Mutationen derselben Quelldatei sequentiell in einem Skript ohne `PYTHONDONTWRITEBYTECODE=1`
angewendet hat (T-150 bis T-157s Laeufe eingeschlossen) - allerdings deutet die bisherige
Teil-Nachpruefung (6/18 des T-150-Blocks stimmen exakt) eher darauf hin, dass der T-150-Block *nicht*
betroffen war und die Anomalie spezifisch bei T-151s R14 auftrat (moeglicherweise, weil dort acht
Mutationen dieselbe Datei in sehr kurzer Folge trafen). Kein Grund, bereits gruene Kampagnen
pauschal zu misstrauen - aber ein Grund, `PYTHONDONTWRITEBYTECODE=1` fuer kuenftige Kampagnenlaeufe
zur Regel zu machen, wenn mehrere Mutationen derselben Datei nacheinander in einem Lauf angewendet
werden.

## An qa-engineer

Nichts Neues zu testen aus diesem Auftrag selbst (reine Testinfrastruktur, keine Anwendungsaenderung).
Der oben gemeldete Technical-Debt-Fund hat keine sichtbare Auswirkung auf das Programm - S3/S4 werden
weiterhin korrekt unterschieden, nur ueber einen anderen Codepfad als der Docstring behauptet.
