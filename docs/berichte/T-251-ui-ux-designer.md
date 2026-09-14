# T-251c — ui-ux-designer — AK-276-291 auf `528ff78` (14.09.2026)

```
STATUS: teilweise
AUFTRAG: T-251c - AK-276-291 am laufenden Fenster pruefen, developer-Fragen klaeren
GELESEN: docs/tasks/T-251.md; docs/berichte/T-248d-developer.md; UI_SPEC.md
  §6.8 (AK-276-291) volltext; nrplanner/advisorblock.py, advisorbar.py
  (Auszuege), relicpicker.py (RelicCard-Kopf), explain.py (_marked_line),
  pressable.py, singleinstance.py; tests/test_relic_picker_advisor.py
  (AK-277-Test); Commit-Nachrichten 115dd4e, 528ff78
GEAENDERT: UI_SPEC.md (Nachtrag nach AK-291), UI_SPEC_REGISTER.md (Zeilen
  AK-277/AK-290), DESIGN_REVIEW.md (neuer Abschnitt oben) — kein Code
ANNAHMEN: keine neuen
NAECHSTER: qa-engineer (T-251a) fuehrt den Livelauf, den ich nicht fahren
  konnte, mit nach — AK-285-Breiten (596/338/1608) selbst nachmessen, nicht
  nur aus 528ff78 uebernehmen
BLOCKIERT DURCH: `singleinstance.RunningCopy` (QSharedMemory-Schluessel
  maschinenweit, nicht je NIGHTREIGN_SETTINGS_ORG gescopet) — zwei fremde
  dist/NightreignHelper.exe-Prozesse (PID 10580 seit 18:01:17, ohne
  Umlenkung in der Kommandozeile) hielten die Sperre, mein Prozess trat
  sofort zurueck (exit 0, kein Fenster). Nicht beendet — fremder, nicht von
  mir gestarteter Prozess, ausserhalb meines Auftrags.
```

## Methode

Umlenkung vorbereitet (`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-251ux`, eigenes
`LOCALAPPDATA`/`APPDATA` im Scratchpad, Testabzug 841 Dateien/22 MB
hineinkopiert), Start scheiterte am Sperrmechanismus oben. Nach Schritt 0.4
("Start unmoeglich → Code-Analyse dokumentieren") auf Code-Analyse
ausgewichen: Quelltext gelesen, `test_a_card_is_the_same_height_with_the_
control_as_with_a_label` als automatisierten AK-277-Beleg zitiert, die
Commit-Nachricht `528ff78` (developer, eigener Fensterlauf) fuer AK-285/
Why-Gruppenhoehe uebernommen — **nicht selbst nachgemessen**, als Luecke im
Bericht vermerkt. Kein Screenshot entstanden.

## Ergebnis je developer-Frage

1. **Enter drueckt den `QToolButton` nicht (AK-278 "oder"):** bestaetigt,
   Code-Fund. `MarkedLine.mark` ist ein nackter `QToolButton`, `Key_Return`/
   `Key_Enter` loesen bei Qt ohne `autoDefault` kein `click()` aus, nur
   `Key_Space`. `pressable.py` hat das Muster (drei Tasten) bereits im
   Projekt. → DR-025, Wichtig.
2. **Tooltip "Click to include it again" fuehrt zu Must include:**
   bestaetigt, eigener Spec-Fehler in AK-277. `NEXT_MARK` geht von
   `Don't include` zu `Must include`, nicht zu neutral zurueck. UI_SPEC.md
   korrigiert (Nachtrag nach AK-291): `"... Click to require it instead."`
   → DR-026, Wichtig.
3. **`_marked_line` als Codename in UI_SPEC Z. 4135/4148:** bestaetigt,
   reiner Doku-Drift. `_excluded_line` wurde in `115dd4e` (T-250a) zu
   `_marked_line` umbenannt; UI_SPEC.md korrigiert, Wortlaut der Saetze
   unveraendert. → DR-027, Nice-to-have, sofort behoben.

## Why-Gruppenhoehe (+4 px bei 21 Zeilen) — abgenommen

`528ff78` misst live 332→336 px. Kein Budget verletzt: AK-04 bindet nur die
Hauptfenster-Mindesthoehe, `WhyDialog` ist ein eigenes, scrollendes
`QDialog` (`resize(640, 620)`, `QScrollArea`). Keine Massnahme noetig.

## Backlog (ungeprueft, fuer den naechsten Livelauf)

Warscheinliche Schriftgroessen-Inkonsistenz: markierte, sonst stille Zeilen
im `WhyDialog` rendern nicht in der 11-px-`MUTED`-Groesse ihrer stillen
Nachbarzeilen (`_styled()` setzt `small` nicht fuer `EXCLUDED`/`REQUIRED`).
Auf der Karte unsichtbar (`size` dort fest 11 px), im Dialog potenziell
sichtbar — ohne Bild nicht bestaetigt.

**Dateien:** `DESIGN_REVIEW.md`, `UI_SPEC.md`, `UI_SPEC_REGISTER.md`.
