# Stand

2026-09-15, **Zyklen 22-25 abgeschlossen, Artefakt 1.12.1 fuer den Eigenlauf**. Branch `docs/audit-and-advisor-design`,
`main` geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` · Befunde
`qa/findings.md` und `security/findings.md` (Tabelle; Fliesstext in den
`verlauf.md` daneben) · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 12.09. am Register): T ab **T-269** · QA ab
**QA-276** · SEC ab **SEC-048** · AK **AK-299** · AD **AD-038** · OF **OF-42**
· DR **DR-032** · R **R-009** · C **C-005** · A **A-037** (T-241a: vergeben bis A-036). **AD-027 und OF-14
wurden nie vergeben.**

## Auftragslage (Nutzer, 15.09.2026 00:19)

**Autonomer Lauf, 8 Stunden (bis ca. 08:20), alles fertig entwickeln:**
Zyklus 24 A20 Zweihand → weitere Bauphasen mit allem, was ansteht → Design-
und andere Optimierungen → Aufraeumen. **Kein Merge, kein Release, keine
Weitergabe** (12.09.). Entscheidungen 00:19: Effektname reicht in der Why-Zeile
(A18 Satz 1 erfuellt) · QA-270 Wortlaut aendern · Screenshots neu erzeugen.
**Bei Fragen annehmen, nicht anhalten** ("keine Roadblocks"); am Ende eine
Liste der Annahmen mit Alternativen zur Bestaetigung. Annahmen werden hier
unter "Annahmen des autonomen Laufs" gesammelt. Stopp nur bei kritischem
Sicherheitsbefund oder Datenverlustverdacht.

### Annahmen des autonomen Laufs (Nutzer bestaetigt am Ende)

- AN-1 Zweihand-Faktoren 1,03 (alle ausser Raider) und 1,144 (Raider) gelten
  auch fuer die nicht gemessenen Nightfarer (Ironeye, Recluse, Executor,
  Revenant, Scholar/Undertaker) — Alternative: dort 1H = 2H anzeigen bis zur
  Messung.
- AN-2 Der 1H/2H-Umschalter sitzt an der Waffenausruestung (Weapon slot),
  Voreinstellung **1H**, gespeichert je Build — Alternative: Voreinstellung 2H,
  oder nicht gespeichert.
- AN-3 (ui-ux-designer T-254a) Der Umschalter ist **ein** Build-Attribut, nicht
  einer je Waffenslot; Beschriftung `1H`/`2H` — Alternative: je Slot.
- AN-4 (developer T-254b) Kein Datenfeld fuer Zweihandbarkeit im Extrakt:
  zweihaendig = Nahkampf ausser wep_type 33; damit bekommen auch Schilde und
  Fackeln einen 2H-Wert — Alternative: Schilde/Fackeln ohne 2H-Wert.
- AN-5 (T-255b) Kachelformat `218 / 225 2H AR`; Arsenal-Typzeilen bleiben 1H,
  nur Kopfzeile traegt 2H — Alternative: `218 AR / 225 2H`, Typzeilen beidhaendig.
- AN-6 (T-255c) Die Hand liegt im Gefaess-Store (`chalices.py`, Feld `2H` nur
  bei Zweihand, Altzeilen = 1H); ein leerer Build speichert keine Hand (2H auf
  leerem Gefaess + Neustart = 1H) — Alternative: Hand auch fuer leere Builds.
- AN-7 (Director) T-255c mit 10 statt 6 Anwendungsdateien angenommen (7
  unvermeidbar, 3 geteilte Konstanten statt Duplikate).
- AN-8 (Director) AK-288 zweite Klausel (Spieldaten ohne Zweihandmodifikator)
  ist durch den Pauschalfaktor gegenstandslos; DR-030 geschlossen.

## HIER WEITERMACHEN

**Autonomer Lauf 15.09. 00:19-07:30 abgeschlossen.** Stand `bd93476`, Suite
**1697 passed / 10 skipped** (Director). **Artefakt 1.12.1**
`dist/NightreignHelper.exe` 59.119.378 B, SHA-256
`f29eb92d88ed14416a488f32f7ab655bf27fec77e2be74105782d0980904cf1b`, Commit
`3c2ff23`, im Startmenue; Sicherungen 1.11.0/1.12.0 im Scratchpad
`artefakte/`. Verlauf des Laufs (Zyklen 24-25): T-254 bis T-268 in
`docs/tasks/`, Berichte `docs/berichte/T-25x/T-26x-*.md`, CHANGELOG 1.12.0/1.12.1.

**Naechster Schritt:** Nutzer bestaetigt die Annahmen AN-1..AN-8 (oben) und
entscheidet die Restpunkte unter "Beim Nutzer — offen"; dann Merge PR #16 /
Release nach seiner Vorgabe (A-020/A-023/A-033 vor der Weitergabe).

## Stand gegen `GOAL.md` (15.09.2026 07:30, Artefakt 1.12.1)

| | | |
|---|---|---|
| A1 | Audit-Bericht, Status je Befund | laufend: Register `qa/`, `security/`, `DESIGN_REVIEW.md`; T-256-Triage: 23 Alt-P2 nachgezogen |
| A2 | kritisch/hoch behoben | **erfuellt**: QA-237 zurueckgestellt (Nutzer); SEC 0 kritisch/hoch, 0 mittel neu |
| A3-A8 | Berater, A6, A7, A8 | **erfuellt am Artefakt** (T-265d, T-268): Optimize 1358 ms Median, Hauptthread max 6,8 ms (5900X) |
| A9 | QA gegen gebautes Artefakt | **erfuellt** (T-265d PASS, T-268 Retest) |
| A10, A14 | Tab-Fragen, QA je Tab | erfuellt |
| A11 | ohne Raten ans Ziel | **teilweise**: power-user 1.12.0 3/6; QA-274/275 danach gebaut (AK-297/298) und am Artefakt bestaetigt, kein dritter power-user-Lauf |
| A12/A13 | Einheiten, nichts abgeschnitten | **erfuellt** (T-263c alle Tabs 1536/1608 px) |
| A15 | Erststart | gebaut; Spielstand-Haelfte am Artefakt nicht provozierbar (QA-255) |
| A16 | Worst/Best | **ersetzt durch A18** |
| A17 | ohne Bezugswaffe | erfuellt |
| A18/A19 | Don't/Must include | **erfuellt am Artefakt** (T-251a, T-265d) |
| A20 | Zweihand | **erfuellt am Artefakt** (6/6 Zellen, Umschalter, Persistenz; T-263a/T-265d) |

## Befunde

**275 QA**, **47 SEC**, **31 DR**. Offen P1: QA-237 (zurueckgestellt). Offen
P2 (T-256 b/c): QA-004, QA-016, QA-222, QA-241 + 5 Prozessschulden. Offen
P3 mit Programmwirkung: QA-258 (Picker 1,6 s, Kartenbau), QA-255, QA-256.
Debt: Farbkonstanten in 14 Modulen (`theme.py`-Kandidat, K-1),
`nrdata/extract.py:2851` Snapshot ohne temp+rename, `IconPack._pixmap`
cacht `None` nicht, `test_rate_pair` Hex-Vergleich tautologisch,
`measure_advisor_search.py` misst `reference=Startwaffe` (veraltet).

## Beim Nutzer — offen

1. **Annahmen AN-1..AN-8** bestaetigen oder Alternative waehlen.
2. **Zweihand-Faktor** fuer sechs ungemessene Nightfarer (AN-1): je ein
   Paar 1H/2H Lv15 Startwaffe liefern oder 1,03 belassen.
3. **A11-Rest:** dritter power-user-Lauf auf 1.12.1 oder eigener Test.
4. **Merge PR #16 / Release:** vor Weitergabe A-020 (Hinweispaket), A-023
   (Release-Text), A-033 (Abnahme), A-008 (`release.yml` ohne pytest);
   Tag `v1.12.1` auf `3c2ff23`.
5. **QA-241:** Hook `enforce-data-redirect` greift fuer Subagenten nicht —
   Team-Repo.
6. **QA-271:** `limit-tool-calls.ps1` zaehlt `grep pytest` als Volllauf —
   Team-Repo.

## Beschlossen, nicht beauftragt

- **OF-34 (13.09.):** reine Test-Umbenennungen zaehlen **nicht** gegen die
  Fuenf-Dateien-Grenze; AD-034 Schritt 3 ist ein Auftrag mit 2 Code- und 6
  Testdateien.
- **OF-35 (13.09.):** die nachgefahrenen `MUTATIONS`-Eintraege loescht der
  `qa-engineer` im Pruefphasenlauf (er hat `Edit`), der Director committet es
  mit seiner Buchfuehrung.
- **Senken-Waechter zu SEC-023:** die Pfadhaelfte haelt **nur fuer die Bauform
  des Befundtexts** (T-202), nicht als "kein Pfad erreicht die Flaeche".
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183).
- **Pruefpunkt 13** ist in T-193 eingeengt; ob die alte Zusage formal
  zurueckgezogen wird, ist offen.
