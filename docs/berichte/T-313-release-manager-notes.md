STATUS: erledigt
AUFTRAG: T-313d - CHANGELOG.md und docs/release/RELEASE_BODY.md fuer 1.15.0
nachziehen (release-manager, Modus `notes`), nach gruenem Retest T-313c
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster
Abschnitt "Auflagen vor der Veroeffentlichung 1.13.1", Stand `1f51485`,
Gesamtampel GELB, keine Auflage auf ROT); docs/tasks/T-313.md; GOAL.md A24
(Z. 486-509); docs/anleitung/guide.md Abschnitt 4 (Nightlords, Z. 308-362)
und Abschnitt 6 (Red variants, Z. 392-410); qa/findings.md QA-286/288
(Z. 473, 475, 477); `git log --oneline ffac292..6edab2e` (24 Commits seit
Tag `v1.14.0`); nrplanner/depthstab.py Z. 80-85 (Zeilennamen); Muster
docs/berichte/T-295-release-manager-build.md (Commit `4bd3a79`, Diff
CHANGELOG/RELEASE_BODY); CHANGELOG.md, docs/release/RELEASE_BODY.md
GEAENDERT: CHANGELOG.md (Abschnitt `## [1.15.0] - 2026-09-19` eingefuegt vor
1.14.0: Added Unterboss-Baum, Changed Red-variants-Spalte, Fixed
Beute-Umschalter QA-288, Note Datenversion 15); docs/release/RELEASE_BODY.md
(ein Punkt "1.15.0" an die Liste "What's new since 1.7.1" angehaengt). Neu:
docs/berichte/T-313-release-manager-notes.md (dieser Bericht).
ANNAHMEN: "Vorgehen wie bei 1.14.0" meint Form und Ort der Eintraege
(Commit `4bd3a79`), nicht den Umfang - `docs/release/ROLLOUT.md` ist im
Auftragstext T-313d nicht genannt und bleibt unangetastet.
NAECHSTER: Freigabe durch den director (Tag + Release), danach `archivist`.
BLOCKIERT DURCH: nichts.

---

# T-313d - CHANGELOG und Release-Beschreibung 1.15.0

## Kontraktblock

| | |
|---|---|
| **Version** | 1.15.0 |
| **Code-Stand** | `6edab2e` (Artefakt aus T-313b, SHA-256 `1D4197DF0F0C765B507CCA824FBA480DBCFCA76C482CF3F7A852B199CB6BBDF0`, 59.151.716 B) |
| **QA/Security** | T-312c/T-313c PASS (qa-engineer), T-312b PASS (security-reviewer) |
| **Geaendert** | `CHANGELOG.md`, `docs/release/RELEASE_BODY.md` |
| **Nicht geaendert** | `docs/release/ROLLOUT.md` (nicht Teil des Auftrags), Version in `nrplanner/__init__.py` (bereits 1.15.0 seit T-312a) |

## Inhalt der Eintraege

Aus GOAL.md A24, guide.md Abschnitt 4/6 und den 24 Commits `ffac292..6edab2e`:

- **Added:** Unterboss-Baum im Nightlords-Tab (Nachtbosse Tag 1/2,
  Feldbosse), Detailpanel mit HP und LOOT-Abschnitt (fuenf seltenste
  Beutestuecke, "Show N more"), "Multiple possible bosses"/"Not identified"
  fuer nicht eindeutig zuordenbare Karten.
- **Changed:** Red-variants-Tab verliert die Spalte "Examples (any map)"
  (QA-286-Ursache behoben durch AK-326, Commit `7f12d5f`); zwei Zeilennamen
  ("Field bosses & arena locations", "Mixed-boss arena locations").
- **Fixed:** "Show N more"-Umschalter reagiert jetzt auch auf
  assistive-Technologie-Toggle, nicht nur Mausklick (QA-288, Commit
  `6edab2e`).
- **Note:** Datenversion 15 - Cache wird beim ersten Start nach dem Update
  einmalig neu gebaut (~35 s plus Symbolpaket); danach nichts weiter noetig.
  Keine Nutzerdaten betroffen (Relikte/Builds liegen in der Registry, nicht
  im Cache) - keine Migrationsfrage offen.

## Nebenfund (kein Blocker)

`qa/findings.md` QA-286 (Z. 473) traegt weiterhin Status "offen -- Fix
zusammen mit A24 (T-300)", obwohl der Fix laut Commit `7f12d5f`
(Commit-Nachricht nennt QA-286 ausdruecklich) im Baum liegt und guide.md
Abschnitt 6 die neue Zeilenbeschriftung bereits zeigt. Keine eigene
Aenderung an `qa/findings.md` - Register gehoert dem `qa-engineer`, nur
Anhaengen erlaubt (NH-003). Meldung an den `director`.

## An `director`

**Empfehlung: freigeben mit dieser einen Einschraenkung.**

1. QA-286-Registerzeile widerspricht dem Baum (siehe Nebenfund) - vor Tag
   entweder vom `qa-engineer` nachziehen lassen oder bewusst so freigeben.
2. Kein `.gitignore`-Nachtrag noetig.
3. Keine offene rote Auflage (`docs/legal/AUFLAGEN.md`, Volltext gelesen).
4. Migration: keine - reiner Cache-Rebuild, keine Nutzerdaten betroffen.

**Tag-Vorschlag:** `v1.15.0` auf `6edab2e` - der Commit-Stand des Artefakts
aus T-313b/QA-288-Fix, gruen getestet in T-313c.
