# T-156 - Das Mutationsregister fertig schreiben (developer)

```
STATUS: teilweise
AUFTRAG: T-156 - 85 Mutationen aus T-137/142/147/149/150/151 ins Register
         (scripts/differential/mutate.py) nachtragen
GELESEN: docs/tasks/T-156.md; docs/berichte/T-155-developer.md (vollstaendig);
         docs/berichte/T-142-developer.md, T-147-developer.md,
         T-149-developer.md, T-150-developer.md, T-151-developer.md
         (Mutationstabellen, fuer die means.py-Texte); Scratchpad
         `…/scratchpad/T-155/` vollstaendig (catalog.py, means.py,
         write_registry.py, run_campaign.py, check_anchors.py);
         .claude/agent-memory/developer/project_mutation_registry.md,
         project_mutation_campaign_cost.md; nrplanner/paths.py,
         nrplanner/shortcut.py, tests/conftest.py (Datenverzeichnis-
         Umlenkung); nrplanner/app.py, nrplanner/inventory.py (Fundstelle
         des verschobenen Ankers)
GEÄNDERT: scripts/differential/mutate.py — vier Commits:
         78317b4 (T-142, 13 Eintraege), 8d875ea (T-147, 22 Eintraege),
         32d56e9 (T-149, 21 Eintraege), aeaab8c (T-150, 18 Eintraege,
         **ein Anker davon rot** — Details unten). T-151 (11 Eintraege)
         **nicht begonnen** — Zugschwelle.
         Ausserhalb des Repos (Scratchpad, nicht Teil dieses Felds im
         engeren Sinn, aber fuer die Fortsetzung wichtig):
         `…/scratchpad/T-156/catalog.py`, `means.py` (alle 85 Eintraege
         mit Text), `write_registry.py` (zwei Fehler aus T-155
         korrigiert, siehe unten), `run_campaign.py` (Skip-Liste fuer
         die 9 von T-155 uebernommenen Ergebnisse), `campaign_results_
         T-142.txt`, `campaign_results_T-147.txt`, `campaign_results_
         T-149.txt`, `campaign_results_T-150.txt`; `tree/`, `reference/`
         (git-archive-Kopien von HEAD vor dem ersten Commit dieses
         Laufs); `local/NightreignHelper/` (Testabzug-Kopie, 841
         Dateien).
ANNAHMEN: (1) Datenverzeichnisse fuer alle Testlaeufe umgelenkt auf
         `…/scratchpad/T-156/local` (LOCALAPPDATA), `…/appdata` (APPDATA),
         `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-156` — Nachweis unten.
         (2) `…/scratchpad/T-155/tree` und `reference` (Stand HEAD vor
         diesem Lauf) fuer T-147/149/150 weiterverwendet statt neu gebaut,
         weil kein Commit dieses Laufs deren Zieldateien (nrdata/
         gamefiles.py, nrplanner/gamepath.py, nrplanner/datasource.py,
         nrplanner/firstrun.py, nrplanner/app.py bis zum T-150-Fund,
         nrplanner/advisorbar.py) beruehrt — selbst mit `git archive
         HEAD` neu gebaut in `…/scratchpad/T-156/tree` zu Beginn, danach
         nicht neu, weil die eigenen Commits nur scripts/differential/
         mutate.py trafen. **Fuer T-151 muss der naechste Lauf selbst
         pruefen**, ob diese Annahme noch gilt (git log seit diesem
         Commit gegen nrdata/savefile.py, nrplanner/inventory.py), nicht
         von hier uebernehmen.
NÄCHSTER: developer (Fortsetzung: T-150-Ankerreparatur, T-151, Suitezahl)
BLOCKIERT DURCH: nichts inhaltlich — der Lauf endete an der
         Werkzeug-Zugschwelle (150 Aufrufe), nicht an einer offenen Frage.
```

---

## Was fertig ist

**T-142 (13), T-147 (22), T-149 (21): alle committet, Anker-Waechter fuer
jeden dieser drei Bloecke direkt danach gruen gemessen, Zieltestdateien
gruen.**

| Block | Commit | Eintraege | Anker-Waechter danach | Zielumfang danach |
|---|---|---|---|---|
| T-142 | `78317b4` | 13 (9 von T-155 uebernommen, 4 selbst gefahren) | 243 gruen | `test_save_read_in_the_background.py`: 23 gruen |
| T-147 | `8d875ea` | 22 (alle selbst gefahren) | 265 gruen | `test_game_dir_recognition.py` + `test_game_path_memory.py`: 73 gruen |
| T-149 | `32d56e9` | 21 (alle selbst gefahren) | 286 gruen | `test_first_run_panel.py`: 57 gruen; `test_save_read_in_the_background.py`: 24 gruen (eine Mutation aus T-149 laeuft gegen diese Datei) |

**T-155s Ergebnisse fuer T-142 uebernommen wie verlangt.** 9 von 13 wortgetreu
aus `docs/berichte/T-155-developer.md` transkribiert (nicht neu gefahren),
markiert im Registertext als `(T-155, ...)`. Der zehnte
(`shutdown-does-not-raise-the-generation-t142`) lief bei mir erneut, weil
sein Katalogname von T-155s eigener Skip-Liste in `run_campaign.py`
abwich (die Liste nannte den Namen ohne das `-t142`-Suffix, das der
Katalog tatsaechlich traegt — gefunden und in meiner Kopie korrigiert,
siehe unten). Drei restliche T-142-Mutationen frisch gefahren
(`the-players-slot-is-overwritten`, `load-equipped-speaks-during-the-
read`, `the-stock-never-reaches-the-cards`).

**Drei Ueberlebende eingetragen, mit Begruendung, nicht nachgebessert:**

- `the-stock-never-reaches-the-cards` (T-142): `reload_chalices ->
  load_equipped -> apply_chalice -> set_owned` deckt die entfernte Zeile
  auf jedem von T-142s Faellen ab (23 passed, heute erneut gemessen).
- `empty-regulation-accepted` (T-147): "zwei Guertel, keiner allein" —
  der Read-Check faengt eine leere Datei auch ohne den Size-Check
  (73 passed, heute erneut gemessen).
- `type-str-dropped-when-reading` (T-147): dieselbe Figur fuer `type=str`
  vs. `isinstance` (73 passed, heute erneut gemessen).

## Zwei Fehler in T-155s Infrastruktur gefunden und in meiner Kopie
korrigiert (nicht im Original unter `…/scratchpad/T-155/`)

1. **`write_registry.py::safe_embed` escapte keinen Backslash.** Ein
   Katalogtext mit einem literalen `\n` (zwei Zeichen, z. B. ein
   f-string-Escape im Quelltext) wurde unescaped in die neue
   `"""..."""`-Literal geschrieben. Beim naechsten Parsen von
   `mutate.py` durch Python wurde daraus ein echter Zeilenumbruch, der
   Anker suchte dann nach Bytes, die nicht existieren — **der
   Anker-Waechter hat das gefangen** (0 statt 1 Treffer bei
   `the-failure-keeps-the-waiting-sentence`, direkt nach dem ersten
   T-142-Insert). Betroffen waren 5 der 85 Eintraege (1× T-142, 1× T-147,
   1× T-149, 2× T-150). Fix: Backslash zuerst verdoppeln, danach die
   bestehende Randfall-Behandlung fuer ein schliessendes `"`.
2. **`RENAME`-Eintrag zeigte auf einen Namen, den `MEANS` nicht kannte.**
   `("T-142", "shutdown-does-not-raise-the-generation")` gibt es im
   Katalog gar nicht (der echte Name traegt das `-t142`-Suffix) — die
   Umbenennung war also nie wirksam, aber `MEANS` hatte trotzdem einen
   Eintrag unter dem Zielnamen der toten Umbenennung stehen. Fix:
   `RENAME` geleert, `MEANS`-Schluessel auf den echten Katalognamen
   umbenannt.

Beide Fixes nur in `…/scratchpad/T-156/write_registry.py` — falls dieses
Skript ein drittes Mal wiederverwendet wird, sind sie dort und nicht im
Original unter `T-155/`.

## Was nicht fertig ist

### T-150 (18 Eintraege) — committet, aber ein Anker ROT

`aeaab8c` traegt alle 18 ein. **17 sind gruen.** Der 18.
(`the-limit-is-under-a-real-save`) hat `path="nrplanner/app.py"`, aber
`LARGEST_SAVE_TO_READ` ist seither nach `nrplanner/inventory.py`
(`refuse_a_size_no_save_can_have`) umgezogen — gleicher Name, gleicher
Wert (`256 * 1024 * 1024`), gleicher Zweck, nur ein anderer Ort. **Das
ist kein "traegt nicht mehr"** im Sinn des Auftrags (die Schranke
existiert unveraendert) — die Reparatur waere: `path` im Katalog auf
`nrplanner/inventory.py` aendern und die Mutation erneut gegen den
heutigen Checkout fahren. Das stand als naechster Schritt an, als die
Zugschwelle griff.

**Letzter Testlauf vor dem Abbruch** (direkt nach dem T-150-Insert):
`test_every_mutation_still_finds_its_anchor_in_the_real_source`:
**1 failed, 303 passed** (304 Eintraege insgesamt zu diesem Zeitpunkt:
230 + 13 + 22 + 21 + 18). Die anderen 17 T-150-Eintraege sind darin als
gruen bestaetigt.

**Ein Nebenfund beim Kampagnenlauf:** `the-two-empty-endings-are-one`
kam im automatisierten Lauf mit leerem `stdout` zurueck (Tail `"?"`,
keine Testnamen) — von Hand nachgefahren (derselbe Baum, dieselbe
Mutation): `1 failed, 31 passed in 34.42s`,
`test_a_picked_save_without_relics_says_which_account`. Kein Befund an
der Mutation selbst, vermutlich ein Ausgabe-Verschlucker im
Batch-Treiber bei genau diesem einen Lauf (keine Wiederholung bei den
anderen 17). Der reparierte Wert steht in `campaign_results_T-150.txt`
und ist bereits eingetragen.

### T-151 (11 Eintraege) — nicht begonnen

`run_campaign.py T-151` wurde nicht gestartet. `means.py` traegt bereits
Text fuer alle 11 (`R12a`...`R16`, `unknown-mode-falls-back`,
`choice-per-slot-not-per-load`). Zieltestumfang laut
`DEFAULT_TARGETS`/`OVERRIDE_TARGETS` in `run_campaign.py`:
`tests/test_relic_scan_prefilter.py tests/test_hostile_savefile.py`,
fuer `R14-refusal-reinstated` zusaetzlich
`tests/test_save_read_in_the_background.py`.

### Suitezahl — nicht gemessen

`pytest -n auto` wurde in diesem Lauf **nicht** gefahren. Letzter
bekannter Stand vor diesem Lauf: **1595 passed, 9 skipped, 0 failed**
(T-153). Erwartete Verschiebung nach vollstaendiger Registrierung aller
85: **+85** (jeder Eintrag erzeugt genau einen Fall in
`test_every_mutation_still_finds_its_anchor_in_the_real_source`) —
**unbelegt durch einen eigenen Lauf**, nur die Anker-Waechter-Teilzahlen
oben sind gemessen.

## Datenverzeichnis-Umlenkung — Nachweis

Alle Testlaeufe in diesem Auftrag liefen mit:

| Variable | Wert |
|---|---|
| `LOCALAPPDATA` | `…\scratchpad\T-156\local` |
| `APPDATA` | `…\scratchpad\T-156\appdata` |
| `NIGHTREIGN_SETTINGS_ORG` | `DankYeeterT-156` |

Nachweis: `python -c "import os; print(...)"` zeigte die umgelenkten
Pfade vor dem ersten Testlauf. Der feste Testabzug
(`C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug`, 841 Dateien)
wurde **kopiert** nach `…\scratchpad\T-156\local\NightreignHelper`
(841 Dateien nachgezaehlt), nicht direkt referenziert. Kein Schreibzugriff
auf die echten drei Orte in diesem Lauf.

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert
- [ ] Build & Tests gruen — **teilweise**: T-142/147/149 gruen und
      committet; T-150 committet mit einem roten Anker; T-151 nicht
      begonnen; Gesamtsuite nicht gemessen
- [x] Neue Testlogik: keine eigene — das Register erzeugt seine Faelle
      ueber den bestehenden parametrisierten Waechter, `tests/` nicht
      angefasst
- [x] Kein Linter im Projekt konfiguriert — entfaellt
- [x] Keine Secrets, keine TODOs, kein toter Code in
      `scripts/differential/mutate.py`
- [ ] QA-Akzeptanzkriterien — nicht anwendbar, keine Oberflaechenaenderung
- [x] Bericht geschrieben

## An den director

1. **T-150 braucht eine kleine Reparatur, kein neuer Nachweis von
   vorn.** Nur `path` von `nrplanner/app.py` auf `nrplanner/inventory.py`
   fuer `the-limit-is-under-a-real-save` aendern (im Katalog **und**
   direkt im committeten Registereintrag, da bereits committet), dann
   einmal gegen den heutigen Checkout fahren. ~5 Minuten.
2. **T-151 ist der einzige noch nicht begonnene Block** — Katalog und
   `means.py` sind fertig, nur der Kampagnenlauf (11 Mutationen, nach
   bisheriger Rate ~10-35s je Eintrag) und das Eintragen fehlen.
3. **Zwei Fehler in T-155s Skripten gefunden, siehe oben** — beide nur
   in meiner Scratchpad-Kopie korrigiert. Falls ein Folgeauftrag wieder
   T-155s Original unter `…/scratchpad/T-155/write_registry.py` liest
   statt meiner Kopie unter `…/scratchpad/T-156/`, tritt der
   Backslash-Fehler erneut auf (traf 07.09.2026-Klasse: der Waechter
   faengt es, aber es kostet einen Zyklus). Empfehlung: den Fix ins
   Agentengedaechtnis uebernehmen (Eintrag `mutation-registry` existiert
   bereits, gehoert dort ergaenzt) oder direkt `…/scratchpad/T-155/
   write_registry.py` mit meiner Fassung ueberschreiben, falls der
   naechste Lauf ohnehin von dort liest.
4. **Kein Sicherheits- oder Datenverlustfund.** Alle Aenderungen sind
   reine Registereintraege in `scripts/differential/mutate.py`, keine
   Verhaltensaenderung am Programm.

## An qa-engineer

Nichts Neues zu pruefen — reine Testinfrastruktur, keine
Oberflaechenaenderung.
