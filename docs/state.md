# Stand

Stand: 2026-09-01, Zyklus 1 (Audit) abgeschlossen.

## Wo wir stehen
- Repo geklont von github.com/DankYeeter/Nightreign-Helper, Stand 3da8428 (v1.7.1).
- ~16.7k Zeilen Python, **PySide6/Qt** (nicht Tkinter — Korrektur im Zyklus).
- `GOAL.md` vom Nutzer freigegeben. PR #15 gemerged (CLAUDE.md, Repo-Kategorie
  privat) — noch nicht in die Arbeitskopie gezogen, steht beim naechsten sync-in an.
- Spiel installiert (`D:\SteamLibrary`, mit DLC), zwei echte Savefiles vorhanden.
  QA hat gegen echte Daten geprueft.

## Zyklus 1 — Audit: fertig
| Task | Rolle | Ergebnis |
|---|---|---|
| T-001 | architect | `ARCHITECTURE.md`, AD-001..AD-013, 11 Umsetzungsschritte; nach QA-Nachmessung korrigiert |
| T-002 | qa-engineer | 12 Befunde → `qa/findings.md` (2x P1) |
| T-003 | security-reviewer | 10 Befunde → `security/findings.md` (4x Hoch, 0 kritisch) |
| T-004 | ui-ux-designer | `UI_SPEC.md`, AK-01..AK-30 |
| T-005 | researcher | `docs/research/R-001.md` — SEC-005 bestaetigt |

## Kernbefund des Zyklus
Die Rechnung selbst ist sorgfaeltig gegen das Spiel gemessen und haelt. Die
Fehler liegen in den **Naehten**: eine zweite Rechenstelle, die driftet
(QA-001), eine Regel, die fuer Effekte gilt und fuer physische Relikte nicht
(QA-002), Nutzertext in einem Schluesselraum (QA-003). Dazu drei
Sicherheitsbefunde desselben Musters: Zahlen aus fremden Dateien steuern
Schleifen und Allokationen ohne Groessenpruefung (SEC-001, SEC-002, SEC-005).
**Null automatisierte Tests** ist die Ursache dahinter.

## Entscheidungen des Directors
- QA-001, QA-002, QA-006 **vor** dem Build-Berater. Der Berater wird sonst die
  dritte driftende Rechenstelle und verletzt A4 und A7 bauartbedingt.
- Kein Release, solange QA-001, QA-002 und SEC-001 offen sind.
- AD-011 (freie Prueffunktionen in `binary.py` statt Reader-Methode):
  angenommen — die Reader-Methode haette nur 2 von 5 Fundstellen erreicht.
- AD-012 (kein `defusedxml`): angenommen, mit der im AD genannten
  Neubewertungs-Bedingung.
- `pytest` als **Entwicklungs-Abhaengigkeit** freigegeben (nicht im Artefakt).
- OF-5: `max_damage` ohne Referenzwaffe faellt auf eine benannte, im Ergebnis
  ausgewiesene Annahme zurueck, statt zu verweigern — A7 ist erfuellt, solange
  die Annahme dasteht.

## Naechster Zyklus (Zyklus 2) — Fix vor Feature
S1 Testsockel → S2 Golden-Test der Schadensrechnung → S3 AR-Extraktion nach
`nrplanner/damage.py` → QA-001 (eine Rechenstelle) → QA-002 (Handle-Regel).
Sicherheitsstrang X1 (SEC-001/002/005) laeuft unabhaengig daneben.

## Nutzerentscheidungen vom 2026-09-01
- QA-006: **"wirkt"**, Status quo. Faellt aus dem Fix-Zyklus, Waechter-Test bleibt.
- QA-002: **Besitz erzwingen**. Handle-Regel, freies Planen ueber "Custom relic".
- SEC-007 fixen, SEC-006 dokumentieren (Deckel ja, Herkunftspruefung nein).
- Berater schlaegt **kein Gefaess** vor — Nicht-Ziel.
- **OF-3: feste Annahme**, kein Bedienelement. Genau eine Gewichtung der acht
  Schadensarten, als `DEFAULT_WEIGHTING` im `GoalContext`. Zwei Auflagen aus
  der Hausregel A7, die beim Bau des Beraters gelten: die Annahme ist
  **benannt** und im Ergebnis **sichtbar** ("weighted against ..."), und sie
  wird aus den Spieldaten hergeleitet, soweit die Dateien das hergeben —
  wo nicht, sagt der Berater es. Der Weg zum Bedienelement bleibt offen, weil
  Gewichte Daten sind und keine Konstanten in der Zielfunktion; er wird jetzt
  nicht gebaut.

## Noch offen beim Nutzer (blockiert Zyklus 2 nicht)
- **UI F1-F4**: Slots festhalten, Statblatt-Vorschau, Flueche mitbewerten, Name
  des Features. Blockiert erst den Berater-Bau, nicht den Fix-Zyklus.

## Bestaetigt durch Nachmessung (2026-09-01)
Die Beam-Suche haelt auch im ungueenstigsten realen Fall: `Wylder's Chalice`
mit weissem Slot und Deep of Night, 6 Slots, **0,46 s** bei K=20/W=40 —
einschliesslich Vorsortierung und erzwungener Exemplar-Eindeutigkeit. Die
Suchkosten sind `Slots x W x K` und damit **unabhaengig von der Poolgroesse**:
`Wylder's Chalice` (Pool 208) und `Wylder's Urn` (Pool 56) brauchen exakt
gleich viele Bewertungen (3929). Der weisse Slot vervierfacht den Produktraum
und laesst die Suchkosten unberuehrt.

Der Beleg fuer die Handle-Regel (AD-013) ist der schaerfste Einzelbefund des
Zyklus: ohne sie sind bei `Wylder's Urn` (Slotfarben Rot/Rot/Blau)
**40 von 40** Vorschlaegen unbrauchbar — und zwar auf die unauffaelligste Art:
Punktzahl plausibel, alle Relikte im Besitz, nur liegt eines zweimal.
Deshalb prueft AD-009 Testpunkt 4 gegen `Wylder's Urn`, nicht gegen ein
gutmuetiges Gefaess.
