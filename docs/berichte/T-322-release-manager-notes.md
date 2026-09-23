STATUS: erledigt
AUFTRAG: T-322j - CHANGELOG.md und docs/release/RELEASE_BODY.md fuer 1.16.0
nachziehen (release-manager, Modus `notes`), wie T-313d, nach QA T-322e/
T-322i PASS und Sicherheit T-322c PASS.
GELESEN: docs/legal/AUFLAGEN.md (vollstaendig, 559 Zeilen; juengster
Abschnitt "Auflagen vor der Veroeffentlichung 1.13.1", T-283c, Stand
`1f51485`/Commit `cc92066`, unveraendert seit T-322b/h - Gesamtampel GELB,
keine Auflage auf ROT mit sperrender Wirkung; A-010 ROT, aber ausdruecklich
"sperrt nicht mehr"); docs/tasks/T-322.md (vollstaendig, Abschnitte a-j);
GOAL.md A25 (Z. 511-531); UI_SPEC.md §3.7 (AK-327..AK-336, Nachtrag T-322d);
docs/berichte/T-322-qa-engineer.md (vollstaendig, 492 Zeilen: T-322e
CONCERNS mit QA-289/290, T-322i Retest PASS); docs/berichte/T-322-release-
manager.md (T-322b/h, Groessen und SHA); `git log --oneline ebbcec2..5b9fad9`
(21 Commits); `git show c536daa --stat` (Muster T-313d); CHANGELOG.md,
docs/release/RELEASE_BODY.md vor der Aenderung.
GEAENDERT: CHANGELOG.md (Abschnitt `## [1.16.0] - 2026-09-20` eingefuegt vor
1.15.0: Added Schadensart-Auswahl bei "Maximise damage" mit allen in A25
genannten Teilsaetzen, Fixed QA-289/QA-290); docs/release/RELEASE_BODY.md
(ein Punkt "1.16.0" an die Liste "What's new since 1.7.1" angehaengt). Neu:
docs/berichte/T-322-release-manager-notes.md (dieser Bericht).
ANNAHMEN: "Vorgehen wie T-313d" gelesen als Form und Ort der Eintraege, nicht
als Umfang - der Auftragstext nennt den Inhalt selbst vollstaendig (A25-
Teilsaetze), keine eigene Auslegung noetig. Keine Migrationsfrage, weil A25
keinen Ort, kein Format und kein Schema von Nutzerdaten aendert (Registry-
Schluessel `advisor/excluded`/`advisor/required`, Builds, Chalices bleiben
unberuehrt - `damage_type_box` ist eine Sitzungsauswahl ohne Persistenz,
UI_SPEC.md AK-328 "keine Persistenz ueber einen Neustart hinweg").
NAECHSTER: Freigabe durch den director (Tag + Release), danach `archivist`.
BLOCKIERT DURCH: nichts.

---

# T-322j - CHANGELOG und Release-Beschreibung 1.16.0

## Kontraktblock

| | |
|---|---|
| **Version** | 1.16.0 |
| **Code-Stand** | `5b9fad9` (Fix QA-290, nach `10442b2` QA-289) |
| **Artefakt** | T-322h `69fb2bf`, `dist\NightreignHelper.exe`, 59.233.161 Byte, SHA-256 `51F694986D11CA1DED16B6170D552C89579C0E5C67192D78F68FFFF063E8BFC9` |
| **QA** | T-322e (`5465491`, CONCERNS mit QA-289/290) und T-322i Retest (`1bbeee7`, PASS - beide Befunde am Artefakt bestaetigt behoben) |
| **Sicherheit** | T-322c PASS |
| **Geaendert** | `CHANGELOG.md`, `docs/release/RELEASE_BODY.md` |
| **Nicht geaendert** | `docs/release/ROLLOUT.md` (nicht Teil des Auftrags), Version in `nrplanner/__init__.py` (bereits 1.16.0 seit T-322a) |

## Pflichtlektuere `docs/legal/AUFLAGEN.md`

Volltext gelesen (559 Zeilen). Juengster Abschnitt weiterhin "Auflagen vor
der Veroeffentlichung 1.13.1" (T-283c, Stand `1f51485`), letzter aendernder
Commit `cc92066` - unveraendert seit den beiden Bau-Laeufen T-322b/h dieses
Auftrags. Gesamtampel GELB, keine Auflage steht auf ROT mit sperrender
Wirkung: A-010 ist ROT, aber ausdruecklich "sperrt nicht mehr" (Nutzer-
Rueckstellung 02.09., Abnahme 09.09.). Dieser `notes`-Lauf schreibt nur
Text in zwei Repo-Dateien, gibt nichts weiter - `notes` ist ebenso wenig
gesperrt wie `build` es war.

## Inhalt der Eintraege

Aus dem Auftragstext (A25 woertlich), GOAL.md A25, UI_SPEC.md §3.7 und den
21 Commits `ebbcec2..5b9fad9`:

- **Added:** Schadensart-Auswahl unter "Maximise damage" - All / Physical /
  Magic / Fire / Lightning / Holy / Skill attack (nur Weapon Arts) /
  Sorceries / Incantations / je eine Zauberschule (z. B. Bestial). Reihung,
  Why-Zeile, Karten-Kopfzeile ("Skill attack rating") und Relikt-Picker
  ("Damage (Fire)") folgen der Wahl; ein Stab oder Siegel bleibt unberuehrt
  und sagt das selbst; Startwaffen-Konversionsrelikte zaehlen in die Zahl;
  unterhalb 1676 px Fensterbreite duerfen die beiden Boxen gekuerzt sein.
- **Fixed:** QA-289 (Picker-Kopfzeile nennt die gewaehlte Art jetzt wie
  Wertzeile und Chip) und QA-290 (eine Wahl ohne Vorkommen fuellt keinen
  Slot mehr - Leiste und Picker antworten auf dieselbe Frage gleich).

Keine **Note** zu Migration/Cache-Version - A25 aendert keine Datenversion
(anders als 1.15.0); `damage_type_box` ist reine Sitzungsauswahl.

## Migration von Nutzerdaten

**Keine.** A25 fuehrt kein neues Format, kein neues Schema und keinen neuen
Ablageort ein. Die Schadensart-Auswahl (`damage_type_box`) ist eine
Sitzungseinstellung ohne Persistenz ueber einen Neustart hinweg (UI_SPEC.md
AK-328, am Artefakt in T-322e/i bestaetigt: "jedes Mal bei Programmstart
erneut ausgewaehlt"). Relikte, Builds, Chalices, Favourite/Avoid-Filter
(Registry-Schluessel `advisor/excluded`, `advisor/required`) bleiben in Ort
und Format unveraendert. Kein Cache-Rebuild wie bei 1.15.0 (Datenversion
unveraendert). **Ohne offene Migrationsfrage.**

## Nebenfund (kein Blocker)

`qa/findings.md` fuehrt QA-289/QA-290 laut T-322-qa-engineer.md bereits mit
den Retest-Zeilen ("behoben -- am Artefakt bestaetigt") direkt hinter den
Ursprungszeilen - Register-Konsistenz war schon beim Anhaengen durch den
`qa-engineer` hergestellt, keine eigene Aenderung noetig oder erlaubt
(NH-003, Register gehoert dem `qa-engineer`).

## An `director`

**Empfehlung: freigeben.**

1. Keine offene rote Auflage (`docs/legal/AUFLAGEN.md`, Volltext gelesen,
   unveraendert seit T-322b/h).
2. Kein `.gitignore`-Nachtrag noetig.
3. QA: CONCERNS (T-322e) wurde durch den Retest (T-322i) zu PASS; Sicherheit
   PASS (T-322c). Beide Voraussetzungen des Auftrags erfuellt.
4. Migration: keine - reine Sitzungsauswahl, kein Format-/Schemawechsel,
   kein Cache-Rebuild.
5. `README.md`/`docs/anleitung/guide.md` werden parallel vom
   `technical-writer` gepflegt - nicht Teil dieses Laufs, nicht angefasst.

**Tag-Vorschlag:** `v1.16.0` auf `5b9fad9` - der Commit-Stand des Artefakts
aus T-322h (Fixe QA-289/QA-290), gruen retestet in T-322i.
