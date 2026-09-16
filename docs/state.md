# Stand

2026-09-16, **Zyklus 26: 1.13.1 releasefaehig, Veroeffentlichung laeuft**.
Branch `docs/audit-and-advisor-design`, `main` geschuetzt, PR #16 offen —
**Merge gehoert dem Nutzer.** Verlauf
`docs/archiv/state-bis-2026-09-12-zyklus19.md` · Befunde `qa/findings.md`
und `security/findings.md` (Tabelle; Fliesstext in den `verlauf.md`
daneben) · Register `UI_SPEC_REGISTER.md`, `ARCHITECTURE_REGISTER.md` ·
Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 16.09. am Register): T ab **T-286** · QA ab
**QA-283** · SEC ab **SEC-049** · AK **AK-314** · AD **AD-038** · OF **OF-42**
· DR **DR-032** · R **R-009** · C **C-007** · A **A-038** (C-006: A-037
empfohlen). **AD-027, OF-14, C-005 wurden nie vergeben.**

## Auftragslage (Nutzer, 16.09.2026 16:52, Part 12)

**Fertigstellen und veroeffentlichen** — "push everything to GIT so my
friends can download it". Entschieden 16.09.: Release per Tag `v1.13.1` auf
dem Branch, `release.yml` baut; **PR #16 mergt der Nutzer selbst** · volle
Pruefkette · A21-Woerter bleiben, das Fenster erklaert die Funktion
(AK-313). Plan: `~/.claude/plans/nightreign-helper-part-12-eager-lynx.md`.

**Annahmen AN-1..AN-7 sind beantwortet** (Nutzer 15.09. 06:58/07:14, Sitzung
Part 11): AN-1 durch Messungen ersetzt (Ironeye 66/66, Recluse 135/135,
Executor 94/97, Revenant 159/159, Scholar 63/64, Undertaker 91/93; eingebaut
`4061dad`, `44171c0`) · AN-2/AN-3 passt · AN-4 vorerst so · AN-5 Typzeilen
ebenfalls zeigen (AK-299 `f2880a4`) · AN-6 ok, leere Builds speichern nichts ·
AN-7 hingenommen · AN-8/AN-9 Director/Nutzer 15.09. QA-237/241/271/258
bleiben zurueckgestellt (Nutzer 15.09.).

## HIER WEITERMACHEN

Stand 16.09. 18:25: **Artefakt 1.13.1** `dist/` 59.201.630 B, SHA-256
`71e82029…67e1c` (T-282, Code `b46641c`). Pruefung T-283: QA PASS 0 Befunde
(Suite 1727 passed / 10 skipped, gemessen T-283a), Security PASS (SEC-048
behoben `af85fbd`), Compliance GELB ohne Sperre (`docs/legal/C-006.md`).
Release-Kette T-284/T-285: `docs/release/RELEASE_BODY.md` als `body_path`
(A-023/A-024/A-037), CHANGELOG 1.13.0/1.13.1, ROLLOUT Migration 1.7.1→1.13.1,
clean-room bestanden (Update 1.11.0→1.13.1, 4 Builds erhalten), power-user
1/6 (QA-282, Werkzeug). Letztes oeffentliches Release **1.7.1 (24.08.)**.

**Veroeffentlicht 16.09. 18:28:** Tag `v1.13.1` auf `798f808`, Run
35121936228 gruen (Schritt `Tests` success = A-008 nachgewiesen), Release
https://github.com/DankYeeter/Nightreign-Helper/releases/tag/v1.13.1 mit
drei Assets: `NightreignHelper.exe` 59.209.044 B (CI-Bau, nicht der lokale),
`.sha256` 86 B, `NightreignHelper-notices.zip` 46.387 B; Beschreibung
beginnt mit Variante A (A-023/A-024/A-037 am Release erfuellt — foermlich
durch `compliance-agent` `pruefen` nachziehen). `@{upstream}..HEAD` = 0.
Retrospektive T-286 (`4b2e931`) und Umsetzung T-287 (`2ca5b00`, `d142f5f`;
Team-Repo `935233e`; `~/.claude/settings.json` Hook-Eintrag unversioniert,
liegt ausserhalb jedes Repos) erledigt. **Naechster Schritt:** Nutzer mergt
PR #16. Zyklus 26 abgeschlossen.

**Lehren dieses Zyklus (fuer die Retrospektive):** clean-room, power-user
und QA nie gleichzeitig gegen dieselbe EXE — maschinenweite Instanzsperre
`singleinstance.py:32` (T-285a, 28 min verloren) · UIA `Invoke()` ist bei
diesem Qt-Build unzuverlaessig, echter Klick mit `GetWindowRect`-Koordinaten
noetig (T-285a) — erklaert QA-279/QA-282 · Bash-Heredocs, die den EXE-Namen
enthalten, sperrt der Umlenkungs-Hook; Dateiaenderungen mit `Write`.

## Stand gegen `GOAL.md` (16.09.2026 18:25, Artefakt 1.13.1)

| | | |
|---|---|---|
| A1 | Audit-Bericht, Status je Befund | laufend: Register `qa/`, `security/`, `DESIGN_REVIEW.md`; T-256-Triage: 23 Alt-P2 nachgezogen |
| A2 | kritisch/hoch behoben | **erfuellt**: QA-237 zurueckgestellt (Nutzer); SEC 0 kritisch/hoch, 0 mittel neu |
| A3-A8 | Berater, A6, A7, A8 | **erfuellt am Artefakt** (T-265d, T-268, T-283a): Optimize 1358 ms Median, Hauptthread max 6,8 ms (5900X) |
| A9 | QA gegen gebautes Artefakt | **erfuellt** (T-283a PASS am 1.13.1) |
| A10, A14 | Tab-Fragen, QA je Tab | erfuellt |
| A11 | ohne Raten ans Ziel | **teilweise**: power-user 1.12.0 3/6, 1.13.1 1/6 (QA-282 Werkzeug, kein Programmbefund); Nutzer-Ingame-Test 15.09. |
| A12/A13 | Einheiten, nichts abgeschnitten | **erfuellt** (T-263c alle Tabs 1536/1608 px) |
| A15 | Erststart | gebaut; clean-room T-285a bestanden; Spielstand-Haelfte am Artefakt nicht provozierbar (QA-255) |
| A16 | Worst/Best | **ersetzt durch A18** |
| A17 | ohne Bezugswaffe | erfuellt |
| A18/A19 | Don't/Must include | **erfuellt am Artefakt** (T-251a, T-265d) |
| A20 | Zweihand | **erfuellt am Artefakt** (6/6 Zellen, Umschalter, Persistenz; T-263a/T-265d) |
| A21 | Effektfilter-Fenster | **erfuellt am Artefakt** (T-283a: AK-300..311, AK-313 live per UIA) |

## Befunde

**282 QA**, **48 SEC**, **31 DR**. Offen P1: QA-237 (zurueckgestellt). Offen
P2 (T-256 b/c): QA-004, QA-016, QA-222, QA-241 + 5 Prozessschulden. Offen
P3 mit Programmwirkung: QA-258 (Picker 1,6 s, Kartenbau), QA-255, QA-256;
QA-282 (Werkzeug). SEC-019 offen (README "no network connections at all",
Mittel, Umformulierung). Debt: Farbkonstanten in 14 Modulen (`theme.py`-
Kandidat, K-1), `nrdata/extract.py:2851` Snapshot ohne temp+rename,
`IconPack._pixmap` cacht `None` nicht, `test_rate_pair` Hex-Vergleich
tautologisch, `measure_advisor_search.py` misst `reference=Startwaffe`
(veraltet), `upx=False` in `NightreignHelper.spec` (C-006-Nebenfund).

## Beim Nutzer — offen

1. **Merge PR #16** nach dem Release (Nutzer, 16.09.).
2. **A-033 foermliche Abnahme / A-035 Aktualisierung** (C-006): Fristende
   07.11.2026 — nur Bestaetigung noetig.
3. **QA-241:** Hook `enforce-data-redirect` greift fuer Subagenten nicht —
   Team-Repo.
4. **QA-271:** `limit-tool-calls.ps1` zaehlt `grep pytest` als Volllauf —
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
