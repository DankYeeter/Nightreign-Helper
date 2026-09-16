# T-229 — Bericht security-reviewer

*Vom Director abgelegt (Rolle ohne `Write`), Wortlaut der Antwort vom
13.09.2026. Stand `8ce5b3b` (Code `719c46d`).*

```
STATUS: erledigt
AUFTRAG: T-229b — Retest SEC-026/036/037/038/039 und neue Flaeche auf 719c46d (HEAD 8ce5b3b; Auftrag nennt 05c6787 — seither nur docs, `git diff --stat 719c46d HEAD -- nrplanner nrdata tests scripts` leer)
GELESEN: docs/tasks/T-229.md, CLAUDE.md, _rahmen.md, security/findings.md (Z. 34-36, 44, 54-65), docs/berichte/T-202-security-reviewer.md, nrdata/{gamefiles,dcx,tpf,binary,oodle}.py vollstaendig, dds.py/icons.py/dvdbnd.py/paramdef.py/savefile.py (Fundstellen), nrplanner/shortcut.py:77-158, firstrun.py:480-510/640-660/715-735/990-1075, gamepath.py:120-136, datasource.py:60-80/105-120, app.py:5100-5135, tests/test_steam_library_start_folder.py:101-155, NightreignHelper.spec:100, git diff b33461d..719c46d (8 Codedateien)
GEÄNDERT: keine Projektdatei. Scratchpad T-229/security: drei Probeskripte, Probeordner (Junctions) restlos entfernt; kein umgelenktes LOCALAPPDATA/APPDATA wurde beschrieben.
ANNAHMEN: (1) Registry-Werte (HKCU/HKLM `SteamPath`) und `libraryfolders.vdf` liegen innerhalb der Vertrauensgrenze. (2) ACL von `C:\Program Files (x86)` gemessen am Elternordner; `...\Steam` existiert hier nicht. (3) Volle Suite nicht gefahren; 4 Sicherheits-Testdateien: 96 passed in 43,9 s.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

**Urteil: PASS.** Kritisch 0 · Hoch 0 · Mittel 0 · Niedrig 1 (neu, Haertung) · Beobachtungen 3.

## Statusvorschlag je SEC-Zeile

| ID | Vorschlag | Beleg |
|---|---|---|
| SEC-026 | **geschlossen** (Herkunft) | `looks_like_the_game:214` endet in `in_a_steam_library`; alle 4 Aufrufstellen (`gamefiles.py:85/304/320`, `gamepath.py:134`) und alle 3 `oodle.load`-Aufrufer (`bossdata:320`, `extract:182`, `icons:82`) bekommen `game_dir` nur ueber `resolve_game()`/`find_game_dir()`. Genau 1 `CDLL`-Stelle (`oodle.py:34`, zweite Maske `CDLL|WinDLL|LoadLibrary|windll`). Probe (`_steam_roots` gestubbt): Ordner in Bibliothek → True; **Junction aus `common` hinaus → False**; Bibliothek selbst als Junction → True ueber beide Schreibweisen; Registry-Wert mit `/`, `\steamapps\..`, GROSS → True (beide Seiten aufgeloest); `\\?\`-Praefix und relativer Wert → False (fail-closed) |
| SEC-036 | **geschlossen** | `_steam_roots:21-37` nur noch Registry; `C:\Steam` und `C:\Program Files (x86)\Steam` beide nicht vorhanden; echte Liste zur Laufzeit `['d:\steam']` |
| SEC-037 | **geschlossen** | ZSTD: Pruefung `:59` vor `decompress` `:61` — Anspruch 2 GiB+1 → `NotWhatItClaims` ohne Allokation. DFLT: 64-MiB-Bombe (65 238 B Nutzlast), Deckel fuer die Probe auf 1 MiB gesenkt → `NotWhatItClaims`, **Spitzenhaufen 2,22 MiB**. KRAK: Groessenpruefung `oodle.py:61` **vor** dem DLL-Handle (`:67`) |
| SEC-038 | **geschlossen** | `test_the_real_root_list_holds_nothing_the_registry_did_not_name:121` misst `_steam_roots()` gegen die Registry; Positivkontrolle: `C:\Steam` in-process angehaengt → `AssertionError`. Zweiter Fall `:134` haelt das Literal `[]` |
| SEC-039 | **geschlossen** | `shortcut.py:143-144`: Flaeche bekommt nur den Repo-Satz. Konsole: PowerShells `stderr` geht an `sys.stderr`; im Artefakt (`spec:100 console=False`) ist der `None`, `print` verwirft still (exit 0); im Quelllauf ist `available():79` False. **Liest niemand** — sicherheitsseitig verlaesst nichts den Prozess; A7-seitig ist die Diagnose verloren (Notiz an director, kein Befund) |
| SEC-016/017/018 | Freigabe **traegt wieder** | Randbedingung "boesartige Installation oder uebernommenes Konto" ist mit Herkunftshaertung wieder die einzige Route zu `dcx`/`tpf`. Hinweis: der Pfad von SEC-017 besteht unveraendert — Probe 32 KiB TPF, 1637 Mitglieder auf den ganzen Container → **51 MiB Spitze (x1645)**; die T-219-Grenzpruefung (`tpf.py:50`) schliesst Mitglieder *ueber* dem Ende, nicht Mitglieder *auf* dem ganzen Inhalt. Bleibt unter der Nutzerfreigabe |
| SEC-042 | **Niedrig, Haertung — unveraendert** | `firstrun.py:153`, benutzt `:502` als letzter Dialogstart; `icacls "C:\Program Files (x86)"`: `BUILTIN\Users:(RX)`; kein `looks_like_the_game`, kein `CDLL` |
| SEC-041 | offen, Niedrig — unveraendert (`binary.py:90`, 4 Byte); Klasse waechst um F1 |

## Befunde

### F1 [Niedrig | Niedrig | Niedrig] Haertung: T-219 hat einen dateilangen String in einen zitierten Satz gesetzt (SEC-041-Klasse, ohne 4-Byte-Deckel)

**Betroffen:** `nrdata/tpf.py:51-54` (`{name!r}`, Commit `670d879`); Nebenstelle `nrdata/dds.py:69` (`{dds[:4]!r}`, `e7f485c`, 4 Byte, `ValueError`→`NotWhatItClaims` verschoben wie SEC-041)
**Vertrauensgrenze:** G1 (Spielarchiv) → G4 (Flaeche)
**Angriffspfad:** Ein TPF-Mitgliedsname kommt aus `read_cstring`, dessen Schranke die Pufferlaenge ist (`binary.py:99-100`), nicht 4 Byte. Der Satz laeuft ueber `errortext.in_english` (zitiert, weil eigene Klasse) → `firstrun.py:648` → `app.py:5111 QMessageBox.critical` (AutoText). Gemessen: `TPF member '<img src="file://attacker/share/x.png">' claims …` erreicht die Flaeche woertlich. **Heute nicht rich-text-wirksam:** Qts Erkennung stoppt am ersten `\n`, und der Sink stellt `"Could not read your game:\n\n"` voran (QLabel-Probe: Praefix → PlainText-Breite 623 = AutoText 623; ohne Praefix 429 ≠ 623, also gerendert). Der Schutz ist eine Eigenschaft des Praefixes und des einen Sinks, nicht des Satzes. Voraussetzung ist ohnehin eine Installation in einer Steam-Bibliothek (Nutzerfreigabe).
**Auswirkung:** keine heute; die naechste Senke ohne Praefixzeile (z. B. ein Statuslabel) macht daraus SEC-019 mit UNC-Fetch.
**Behebungsrichtung:** `{name!r}` fallen lassen oder durch den Mitgliedsindex ersetzen; `dds.py:69` wie SEC-041 die Bytes streichen. Zweite Maske (`!r}` in `raise NotWhatItClaims`, 3-Zeilen-Fenster): 7 Treffer, davon 3 Dateibytes (tpf, dds, binary), 2 Konstanten (extract), 2 aus gebuendelten Paramdefs (`datasource.defs_dir`, nicht Spielordner).

## Beobachtungen (ohne Pfad, ohne Prioritaet)

- `in_a_steam_library:126-131`: ein `OSError` aus `common.resolve()` einer **beliebigen** Bibliothek bricht das `any()` ab und lehnt auch den echten Ordner ab. Gemessen heute harmlos: toter UNC-Eintrag in der vdf → `resolve()` wirft nicht (nicht-strikt), kostet 1,34 s beim ersten Mal, der echte Ordner in der zweiten Bibliothek wird weiter erkannt. Robustheit, Geschwister von T-217 Befund 2.
- `dcx.py:64-68` DFLT prueft den Header-Anspruch nicht vorab wie ZSTD `:59`: Anspruch 3 GiB, real 64 MiB → erst inflatiert (141,5 MiB Spitze), dann `ValueError` (Groessenabgleich `:78`). Innerhalb des Deckels; Konsistenz, kein Befund.
- `steam_common_folders()` liest Registry und vdf bei **jedem** `looks_like_the_game`, bis 400-mal je Suche; nur Laufzeit, Budget `:300` faengt es.

## Geprueft / nicht geprueft

Geprueft: Diff `b33461d..719c46d` in nrdata/nrplanner (8 Dateien), alle Routen zu `oodle.load`, Junction/UNC/Registry-Formen per Probe, Deckel dreier Methoden per Probe, SEC-038-Waechter mit Positivkontrolle, 4 Testdateien (96 passed). Nicht geprueft: volle Suite (qa-engineer), lokalisierte PowerShell-Ausgabe (Maschine en-GB), ACL eines real installierten `C:\Program Files (x86)\Steam`.
