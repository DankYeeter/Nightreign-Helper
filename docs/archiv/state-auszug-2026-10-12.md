# Auszug aus docs/state.md (12.10.2026, Zeilengrenze)

## Autonomer Lauf 22.09. 23:50 bis 23.09. ~01:45 (Budget 6 h, vorzeitig leer)

Endete, weil die Warteschlange leer lief (`director-autonom.md`), nicht am
Budget. Erledigt: QA-Fensterlauf T-329k + Retests p/s (PASS), Security T-329l
PASS, Farbrollen AK-367..371, Snapshot-Leser, `.gitignore` (SEC-051),
unsicherer Test selbsterklaerend, Ponytail-Audit (12 Funde umgesetzt, 2 mit
Leser behalten), Retrospektive (`docs/lessons.md`), discover
(`docs/product/BACKLOG.md`, P-001..004 `vorgeschlagen`). Suite `05dbfed`:
1914 passed, 9 skipped. Kein Merge, kein Release.

## HIER WEITERMACHEN

**Zyklus 27 abgeschlossen 19.09. 10:00.** T-296: README 769 → 94 Zeilen,
Guide `docs/anleitung/guide.md` (`25aa6ad`, SEC-019 geschlossen); Audit
net -421 Zeilen (`561e2ff`, `45217ef`, `122ec39`), PyInstaller nach dev;
**Pillow bleibt** (Qt-Skalierung: 820/839 Icons weichen ab). Ponytail-Debt:
1 Eintrag (`search.py:169`, bleibt). T-297 Retrospektive, T-298 umgesetzt
(NH-007 Hook-Maske `efa52fd`, NH-008 `no-window-dispatch.ps1` `b14fb4d`,
NH-009 `scripts/drive_window.ps1` `6633fca`). Kein neues Release: der
Anwendungscode seit 1.14.0 ist nur Bereinigung (Tag `v1.14.0` = `ffac292`).
**Naechster Schritt:** sync-out, PR auf `main` (Nutzer mergt). **A24** (Unterbosse, GOAL.md Nachtrag 19.09.) als naechster Zyklus: T-299 erledigt 13:05 (Bericht: beide Stufen belegt, QA-286 Extraktor liest Orte als Figuren); T-300 Entwurf AD-040/041 fertig 13:21; OF-45 (60 s) und OF-46 (nur Feld- und Nachtbosse) entschieden; T-301 gemessen 13:33 (Zusatz 21 ms bei Archiv-Wiederverwendung, Schranke eingehalten); T-302 Spec fertig 13:39 (AK-319..326, OF-47: Beispielspalte faellt); T-303 committet `3114100` 14:00 (subbosses, EXTRACT_VERSION 13, Testabzug 841 Dateien 20 913 184 B; Zaehlung single 11/group 1/ambiguous 1/unresolved 16 — Schranke INFERRED_MIN_HP); T-304 AD-042 14:15 (hoechste HP auf der Ortsroute, kein Forschungsauftrag, OF-48 Float-Kante offen); T-305 committet `25f8958` 14:29 (29/29 single, Testabzug 20 953 085 B; zwei Karten ohne Namen in den Dateien: 4654 c3252, 4688 c4021); T-306 committet `1859c57`+`7f12d5f` 14:50 (Baum, Panel HP/Beute, Beispielspalte weg, QA-144-Geometrietest entfernt, abgenickt; Suite 1797 passed); T-307 14:57: Namen belegt ueber EMEVD 90015000 (c3252 Royal Carian Knight, c4021 Royal Revenant); T-308 committet `262c7a2` 15:05 (Nachtkarten, EXTRACT_VERSION 14, Testabzug 21 012 433 B; Nachtkarten single 16/group 3/unresolved 16 — Arena-Regel zu streng, an T-309 nachgereicht); T-309 AD-043/044 15:19 (Balkenname per EMEVD mit Vorrang, Ortsregel auf allen 64 Karten, float32-Toleranz; OF-49 Nutzer-Balken offen); T-310 committet `f184b06`+`79b3ecb` 15:46 (64 single, 59 Namen, EXTRACT_VERSION 15, Testabzug 21 131 645 B, Suite 1807); T-311 Guide `e73727e`; T-312a Bau 1.15.0 `cf4c7df` (59.152.448 B, SHA E2F614F8…8405A); T-312b PASS (SEC-049/050 Niedrig, Haertung); T-312c 16:27: A24-Nachweis live bestaetigt, AK-319..326 bis auf nicht ausloesbares AK-322; QA-287 Fehldeutung (geschlossen), QA-288 P3 Beute-Toggle reagiert nicht auf UIA-Toggle; Nutzer 16:35: QA-288 fixen, dann Release; OF-49 (1) bestaetigt; T-313 fertig 16:56: a Fix `6edab2e`, b Bau `47b4330` (59.151.716 B, SHA 1D4197DF…BBDF0), c Retest PASS `8b54898`, d Notes `c536daa`; **Release 1.15.0 veroeffentlicht 17:05** (Tag `v1.15.0` auf `c536daa`, Run 35451242996, 3 Assets; Branch gepusht); naechster Schritt PR auf main (Nutzer mergt); Nebenfund: QA-286-Zeile noch "offen", Fix in `7f12d5f` — Abschlusszeile beim Zyklusende; OF-49 (drei Balken ingame) beim Nutzer; danach guide.md Abschn. 6 (technical-writer) und QA am Artefakt; AK-324.3 entschieden 13:42 (fuenf offen, Rest Toggle, seltenste zuerst). Backlog
leer laut Nutzer 19.09.; naechster Zyklus nur auf Nutzer-/Freundesbefund.


## Auszug 13.10.2026

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

