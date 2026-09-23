# T-312b — Sicherheitsdurchsicht `ffac292..79b3ecb` (security-reviewer, 19.09.2026)

*Abgelegt vom director; der Reviewer hatte in diesem Lauf kein Schreibwerkzeug. Wortlaut unveraendert.*

**Vertrauensgrenze:** Der ganze Diff liegt in einer Grenze — Spielinstallation
(regulation.bin, FMG, jetzt zusaetzlich 64 MSB + 64 EMEVD ueber `dvdbnd`) →
Extraktor → Snapshot in `%LOCALAPPDATA%` → Oberflaeche. Kein Save, kein Netz,
keine Registry, kein Subprozess: Suche ueber alle `+`-Zeilen nach
`open(|write|mkdir|urllib|requests|socket|subprocess|eval|pickle` = 0 Treffer.

**Befunde:** SEC-049 (`_healthbar_names` quadratisch mit EMEVD-Groesse),
SEC-050 (Part-Record x25 im Ganzzahl-Decode) — beide Niedrig, Haertung,
Randbedingung praeparierte Datei innerhalb der Spielinstallation (Freigabe
05.09.2026, SEC-016/017/018; SEC-026 traegt). Wortlaut im Register
`security/findings.md`.

**Positiv belegt:** verkuerzte/fremde Dateien — 5 Faelle (kein Archiv, MSB
12 B, MSB Muell, `arc.read` wirft, EMEVD 3 B) ergeben alle
`confidence=unresolved`, `primary=None`, keine Ausnahme entkommt; `_entity_of`
gibt bei 5 Grenzfaellen (kurz, `at=0`, `at=2^64-1`, negativ) 0. Neue
Textsenken: Kartenname → `QLabel` PlainText (`bosstab.py:826`) und
`QTreeWidgetItem`, Beutename → `html.escape(..., quote=False)`
(`bosstab.py:1461`); `depthstab` verliert seine Namensspalte — keine neue
SEC-019-Instanz. `_subbosses`-Fehler kostet nur die Sub-Bosse und meldet den
Klassennamen (A8). `param.read(strict)` hatte auch bei `ffac292` keinen Aufrufer.

**SEC-019 Wortlauthaelfte** nachgeprueft: "makes no network connections at all"
0 Treffer in ausgeliefertem Text.

**Votum:** Kritisch 0 · Hoch 0 · Mittel 0 · Niedrig 2 → **PASS**.
**Nicht geprueft:** Laufzeit am Artefakt (T-312c), 60-s-Schranke,
`nrplanner/advisor/*`, Snapshot-Integritaet gegen denselben Nutzer.
