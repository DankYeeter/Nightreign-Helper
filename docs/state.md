# Stand

2026-09-19, **Zyklus 27: Aufraeumen nach Release 1.14.0**. Branch
`docs/audit-and-advisor-design` (PR #16 gemerged 16.09. `ae474c1`; seither
weiter auf dem Branch, `main` haengt hinterher — naechster PR am Zyklusende).
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` und Sitzung Part 12
(16.-19.09.) in `docs/tasks/T-281..T-296` · Befunde `qa/findings.md`,
`security/findings.md` · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (nachgezaehlt 19.09.): T ab **T-309** · QA ab **QA-287**
· SEC ab **SEC-049** · AK **AK-327** · AD **AD-040** · OF **OF-45** · DR
**DR-034** · R **R-009** · C **C-007** · A **A-038**. AD-027, OF-14, C-005
nie vergeben.

## Veroeffentlicht

| Version | Tag auf | Run | Assets | Inhalt |
|---|---|---|---|---|
| 1.13.1 | `798f808` | 35121936228 | 3 | A21 Effektfilter-Fenster, AK-312/313, A-008 Tests im Release-Lauf |
| 1.13.2 | `b0965e3` | 35267925982 | 3 | AK-314 Favorit auf gehaltenem Relikt genannt (T-288/289) |
| 1.14.0 | `ffac292` | 35427762335 | 3 | A22 Attribute ueber Startwaffe in die Schadenszahl (AD-038, AK-315/318), A23 Familien vermeiden + Allow (AD-039, AK-316/317), DR-032, QA-284/285 |

Beschreibung je Release aus `docs/release/RELEASE_BODY.md` (`body_path`,
A-023/A-024/A-037). Download: `releases/latest`.

## HIER WEITERMACHEN

**Zyklus 27 abgeschlossen 19.09. 10:00.** T-296: README 769 → 94 Zeilen,
Guide `docs/anleitung/guide.md` (`25aa6ad`, SEC-019 geschlossen); Audit
net -421 Zeilen (`561e2ff`, `45217ef`, `122ec39`), PyInstaller nach dev;
**Pillow bleibt** (Qt-Skalierung: 820/839 Icons weichen ab). Ponytail-Debt:
1 Eintrag (`search.py:169`, bleibt). T-297 Retrospektive, T-298 umgesetzt
(NH-007 Hook-Maske `efa52fd`, NH-008 `no-window-dispatch.ps1` `b14fb4d`,
NH-009 `scripts/drive_window.ps1` `6633fca`). Kein neues Release: der
Anwendungscode seit 1.14.0 ist nur Bereinigung (Tag `v1.14.0` = `ffac292`).
**Naechster Schritt:** sync-out, PR auf `main` (Nutzer mergt). **A24** (Unterbosse, GOAL.md Nachtrag 19.09.) als naechster Zyklus: T-299 erledigt 13:05 (Bericht: beide Stufen belegt, QA-286 Extraktor liest Orte als Figuren); T-300 Entwurf AD-040/041 fertig 13:21; OF-45 (60 s) und OF-46 (nur Feld- und Nachtbosse) entschieden; T-301 gemessen 13:33 (Zusatz 21 ms bei Archiv-Wiederverwendung, Schranke eingehalten); T-302 Spec fertig 13:39 (AK-319..326, OF-47: Beispielspalte faellt); T-303 committet `3114100` 14:00 (subbosses, EXTRACT_VERSION 13, Testabzug 841 Dateien 20 913 184 B; Zaehlung single 11/group 1/ambiguous 1/unresolved 16 — Schranke INFERRED_MIN_HP); T-304 AD-042 14:15 (hoechste HP auf der Ortsroute, kein Forschungsauftrag, OF-48 Float-Kante offen); T-305 committet `25f8958` 14:29 (29/29 single, Testabzug 20 953 085 B; zwei Karten ohne Namen in den Dateien: 4654 c3252, 4688 c4021); T-306 committet `1859c57`+`7f12d5f` 14:50 (Baum, Panel HP/Beute, Beispielspalte weg, QA-144-Geometrietest entfernt, abgenickt; Suite 1797 passed); **T-307** Namensforschung und **T-308** Schritt 4 Nachtbosse laufen parallel; danach guide.md Abschn. 6 (technical-writer) und QA am Artefakt; AK-324.3 entschieden 13:42 (fuenf offen, Rest Toggle, seltenste zuerst). Backlog
leer laut Nutzer 19.09.; naechster Zyklus nur auf Nutzer-/Freundesbefund.

## Stand gegen `GOAL.md` (19.09.2026, Artefakt 1.14.0)

| | | |
|---|---|---|
| A1, A2 | Audit, kritisch/hoch | erfuellt (Register; QA-237 zurueckgestellt) |
| A3-A9 | Berater, A6, A7, A8, QA am Artefakt | **erfuellt** (T-293b/T-295c am 1.14.0) |
| A10-A14 | Tabs, A11 Laie | A11 **teilweise** (power-user-Werkzeug, QA-282); Nutzer-Ingame-Tests 15.-19.09. |
| A15 | Erststart | erfuellt (clean-room T-285a) |
| A17-A21 | Bezugswaffe, Filter, Zweihand, Filterfenster | erfuellt am Artefakt |
| A22 | Attribute in die Schadenszahl | **erfuellt** (T-293b: Duchess 72 → 70, Why-Betrag; Nutzer "passt" 19.09.) |
| A23 | Familien + Allow | **erfuellt** (T-293b/T-295c; Allow immer klickbar AK-317 Nachtrag) |

## Befunde

**285 QA**, **48 SEC**, **33 DR**. Offen P1: QA-237 (zurueckgestellt).
Offen P2: QA-004, QA-016, QA-222, QA-241 + Prozessschulden. Offen P3:
QA-258, QA-255, QA-256 (geschlossen T-287a), QA-282/283 (Werkzeug/Hook).
SEC: 0 offen ausser Klassenbeobachtung SEC-019 (behoben T-296a, Retest im
naechsten Release-Lauf). Debt: Farbkonstanten in 14 Modulen (`theme.py`),
`nrdata/extract.py:2851` Snapshot ohne temp+rename, `IconPack._pixmap`
cacht `None` nicht, `upx=False` in der Spec (C-006), Audit-`shrink`-Liste
(Harness-Duplikate `scripts/`, Fixture-Duplikate `tests/`,
`_settings()`-Kopien) — bewusst liegen gelassen 19.09.

## Beim Nutzer — offen

1. **PR auf `main`** nach Zyklusende (Director erstellt, Nutzer mergt).
2. **A-033/A-035** (C-006): Fristende 07.11.2026 — Bestaetigung.
3. **QA-241, QA-271** — Team-Repo.
4. **A11-Rest:** ein Freund testet 1.14.0 — Rueckmeldung waere der Nachweis.

## Beschlossen, nicht beauftragt

- **OF-43 (17.09.):** Fuenf-Dateien-Grenze weicht, wenn die Alternative
  Duplikat-Logik in der UI-Schicht ist (T-289b, sieben Dateien).
- **OF-34, OF-35 (13.09.):** Test-Umbenennungen zaehlen nicht; `MUTATIONS`
  loescht der `qa-engineer` im Pruefphasenlauf.
- **Senken-Waechter zu SEC-023:** nur Bauform des Befundtexts (T-202).
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183).
- **Pruefpunkt 13** in T-193 eingeengt; formaler Rueckzug offen.
- **Release-Rezept:** Tag auf dem Baustand (Commit mit Bericht), nie auf
  einem HEAD mit spaeterer Arbeit; `RELEASE_BODY.md` vorher nachziehen,
  sonst `gh release edit --notes-file` (17.09.).
