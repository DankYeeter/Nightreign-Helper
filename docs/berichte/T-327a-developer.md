# T-327a developer — A27 Bau: Weapon art und Spell damage im Schadensblock

**STATUS: teilweise** — die Umsetzung ist fertig, getestet und committet; offen
geblieben ist allein der ausfuehrliche Commit-Body (die Zugschwelle hat die
langen Kommandos abgewiesen, die Kurzfassung ist committet) und die
Werkzeuggrenze beim Fensterlauf (unten, Befund an den director).

## Kontraktblock

| Feld | Wert |
|---|---|
| Commit | `7d1e216` (Basis `8d54281`, Schritt 0 wie beauftragt gesetzt) |
| Worktree-Branch | `worktree-agent-a713dbe8e68d6724a` (Worktree `.claude/worktrees/agent-a713dbe8e68d6724a`), kein Push |
| Suite | `pytest -n auto`: **1891 passed, 9 skipped** (21.09.2026, nach der Golden-Neuaufnahme) |
| Gezielt | `tests/test_damage_spell.py` 9 passed; `tests/test_stat_sheet_art_and_spell.py` 10 passed; `tests/test_weapon_damage_golden.py` 37 passed |
| Umlenkung | `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-327a`, eigenes `LOCALAPPDATA`/`APPDATA` im Scratchpad, Testabzug v16 hineinkopiert; positiv belegt: `paths.cache_dir()` zeigt auf das Testverzeichnis, `snapshot_path().is_file()` True |
| NH-004 | vor dem Lauf `NightreignHelper` 0 Prozesse (tasklist), nach dem Lauf 0; Registry-Zweig `HKCU\Software\DankYeeterT-327a` geloescht, `reg query` danach "unable to find" |

## Umgesetzt

**`nrplanner/damage.py`**
- `SpellRating.bare_per_type` + `bare_figure` (und `_asked`, damit Zahl und
  Grundlinie nie von zwei Regeln ausgewaehlt werden). `spell()` fragt den
  Katalysator zusaetzlich unter `Question.BARE` — die Spell Power auf den
  Stufenattributen, ohne Raten und ohne Kunstfaktor (AK-359).
- Auswahl des Bezugsobjekts aus `advisor/goals.py` hergezogen (AK-357/AD-019):
  `GENUS_OF_CATALYST`, `start_catalyst(hero, data)`,
  `spell_thrown(build, data, catalyst, *, damage_type="")`, dazu das private
  `_record_by_id`/`_base_damage`. Docstrings samt Messwerten mitgenommen.

**`nrplanner/advisor/goals.py`** — nur Import-Umzug: `_spell_cell` ruft jetzt
`damage.start_catalyst`, `damage.GENUS_OF_CATALYST`, `damage.spell_thrown`.
95 Zeilen weniger, kein Verhalten geaendert (77 Tests der Zieldatei gruen).

**`nrplanner/statsheet.py`**
- `_weapon_art_row`: zweiter `damage.equipped(..., art=model.SKILL_ART)`,
  Grauwert ist die Gesamtzeile darueber, Delta dagegen (AK-354/355), mit
  Zweihand-Zwilling; auf Katalysator der Satz `ART_ON_A_CATALYST` (AK-356),
  Beschriftung aus `model.ART_LABELS[SKILL_ART]` (AK-363).
- `_spell_damage_rows`: Zeile nur bei Start-Katalysator und nur auf der
  rechten Starthand oder der Kachel des Katalysators (AK-353.2/AK-358),
  `weapons.MIN_UPGRADE`, `damage_type=""`, ohne Zweihand (AK-359); fetter
  Endwert ist ein Link auf `SPELL_BREAKDOWN_KEY`.
- `_spell_breakdown_text`: Grundlinie, Ratenzeilen mit Reliktnamen, Endwert,
  genau ein Satz (`reason or SPELL_DAMAGE_UNCALIBRATED`) — AK-361.
- `_rate_rows` aus `_ar_breakdown_text` herausgezogen (zwei Aufrufer, keine
  zweite Formatierung derselben Prozentzahl), `_rate_label` benennt einen
  Kunst-Schluessel aus `ART_LABELS`.
- Reihenfolge: Gesamtzeile, Weapon art, Spell damage, dann Inflicts/Rally
  (AK-364); drei getrennte `<div>`-Zeilen, nie summiert (AK-362); Kacheln
  unveraendert.
- `last_spell` wird zu Beginn jedes Neuzeichnens geleert.

**Sicherheit:** Zaubername in Zeile und Tooltip `html.escape` (SEC-019,
T-324v Punkt 9) — dieser Block ist Rich Text, waehrend die Fassade ihren
Namen fuer PlainText-Senken unescaped haelt. Die Saetze der Fassade werden im
Tooltip ebenfalls escaped; `game's` erscheint dort als `game&#x27;s` im
Markup und im Fenster als Apostroph.

## Tests

- `tests/test_damage_spell.py` (+2): Grundlinie gleich der Zahl ohne Relikte;
  ein Ratenrelikt bewegt die Zahl und nicht die Grundlinie; ein Faith-Relikt
  bewegt beide auseinander (ueber die Spell Power); Grundlinie folgt derselben
  Schadensart-Auswahl wie die Zahl.
- `tests/test_stat_sheet_art_and_spell.py` (neu, 10 Faelle): Revenant mit
  7370900 (Zeile, Name, Zahl aus der Fassade, Band 500..650 als Anker an das
  A27-Kriterium), Physical-Relikt bewegt Spell- **und** Gesamtzeile, Wylder
  Skill-Buff bewegt nur die Kunstzeile und ein Physical-Relikt keine,
  Wylder ohne Zauberzeile, Recluse Satz + Pebble-Zeile, Rejection = 0 mit
  Fassadensatz im Tooltip, Tooltip mit Grundlinie/Relikt/Unkalibriert-Satz,
  gefundene Waffe ohne beide Zeilen, Siegel auf eigener Kachel traegt die
  Zauberzeile, Hand-Schalter bewegt die Zauberzeile nicht.
- **Mutationsprobe:** `bare_power = spell_power` in `damage.spell` →
  `test_the_baseline_is_the_same_product_with_nothing_equipped` faellt
  (erwartet 577,55); Datei danach aus der Kopie zurueckgeholt.

## Golden-Datei neu aufgenommen — mit Vorbeleg

`tests/golden/weapon_damage.json` friert den Blocktext ein. Neuaufnahme unter
der **zweiten** der beiden erlaubten Bedingungen (dokumentierte Entscheidung:
`UI_SPEC.md` 4.5, AK-353..AK-364). Vorher gemessen (18 Faelle):
`last_ar` 18/18 unveraendert, `tiles` 18/18, `breakdown` 18/18, und `panel`
18/18 byte-gleich, sobald die beiden neuen Zeilen herausgeschnitten sind.
Danach `scripts/capture_weapon_damage.py`; der Diff umfasst 9 geaenderte
Zeilen (9 Faelle mit neuen Zeilen, 9 ohne).

## Fensterlauf — abgelesen

Quellstand (`python run.py`-Pfad, Titel `Nightreign Helper 1.17.0`), echtes
Fenster auf dem Bildschirm, Stufe 15, Relikte ueber `RelicSlot.set_custom`
(der Weg des Pickers, kein Schreiben in den Spielstand):

| Fall | abgelesene Zeile |
|---|---|
| Revenant + 7370900 | `Total 88 1H / 68 2H no change 88 1H / 68 2H` · `Weapon art 88 1H / 68 2H no change 88` · **`Spell damage (Beast Claw) 577 no change 577`** |
| Revenant + 7370900 + `Physical Attack Up +3` (6001400) | `Total 88 +2 90 (+2.0%)` · `Weapon art 90 no change 90` · **`Spell damage (Beast Claw) 577 +61 638`**; Tooltip: `Base 577 · Physical Attack +10.5% · Physical Attack Up +3 +10.5% · Spell damage 638 · Spell damage is uncalibrated: ...` |
| Wylder + 312300 | `Total 122 1H / 125 2H no change` · **`Weapon art 122 1H / 125 2H +18 140 1H / 144 2H`** |
| Wylder + Physical-Relikt | `Weapon art ... no change` (Grundlinie ist die Gesamtzeile) |
| Recluse (Stufe 1) | `Spell power 82 no change 82` · **`Weapon art — not shown: a staff or a seal is ranked on the spell power the game shows for it, and no attack art reaches that figure.`** · `Spell damage (Glintstone Pebble) 125 no change 125` |
| Guardian | `Weapon art 53 1H / 54 2H no change`, **keine** Zauberzeile |
| Revenant ohne Relikt | `Spell damage (Rejection) 0 no change 0`, Tooltip mit `Rejection deals no damage, ...` |

Damit ist das A27-Kriterium woertlich gelesen: 577 statt der im `GOAL.md`
genannten 578 — das ist die Abschneidung von `damage.displayed`
(577,55), keine Abweichung der Rechnung.

## Befund an den director (Werkzeuggrenze)

`scripts/drive_window.ps1` konnte **nicht** benutzt werden: in dieser
Worktree-isolierten Sitzung weist die Bash-Schranke **jeden**
PowerShell-Aufruf ab ("runs powershell in a plain command ... Refusing to
run it"), auch `powershell -NoProfile -Command "1+1"`. Ebenso abgewiesen:
Heredocs mit vorangestellten Umgebungsvariablen und lange `git commit`-
Kommandos. Ersatzweise wurde das Fenster mit einem Python-Skript im
Scratchpad gestartet und ueber die Fenstermethoden (`select_hero`,
`recompute`, `RelicSlot.set_custom`) getrieben — echtes Fenster, echter
Renderer, aber **keine** UIA-Klicks und kein `PrintWindow`-Bildnachweis.
Wer einen Klicknachweis braucht (qa-engineer), muss den Lauf in einer
Sitzung ohne diese Schranke fuehren.

## Offene Punkte

1. **Commit-Body:** Der Commit traegt nur die Kopfzeile; Begruendung,
   Golden-Vorbeleg und Fensterzahlen stehen in diesem Bericht. Ein
   `git commit --amend` mit vollem Body steht dem naechsten Lauf frei.
2. **Zeilenenden:** Die vier per Python neu geschriebenen Dateien liegen im
   Arbeitsbaum mit CRLF; `.gitattributes` (`* text=auto eol=lf`) normalisiert
   beim Einchecken, der Commit-Inhalt ist LF (git meldet das als Warnung,
   der Diff umfasst nur die geaenderten Zeilen). Ein
   `git add --renormalize` ist nicht noetig, raeumt aber die Warnung weg.
3. **Nicht beruehrt:** `ARCHITECTURE.md`/`UI_SPEC.md` (keine Entscheidung
   geaendert), `docs/state.md`, CHANGELOG — Sache des director bzw. der
   Folgeschritte T-327b/c.

## An qa-engineer

- Zu pruefen am Fenster: die drei Zeilen unter der Gesamtzeile in der
  Reihenfolge Total → Weapon art → Spell damage → Inflicts/Rally; Klick auf
  den fetten Zauberwert oeffnet den Tooltip (Klick auf die Gesamtzeile
  unveraendert).
- Kanten: Startwaffe auf eine andere Kachel geschoben (beide Zeilen wandern
  mit); Siegel auf eine Kachel gelegt (nur Zauberzeile); Zweihand-Schalter
  (Zauberzeile darf sich nicht bewegen, Kunstzeile schon); Recluse (Satz
  statt Zahl); acht Nightfarer ohne Katalysator (gar keine Zauberzeile);
  Revenant ohne Tauschrelikt (`0` mit Satz im Tooltip).
- Schmale Fensterbreiten: der Block wird laenger als zuvor; die
  DR-028-Faelle liefen gruen, aber nur mit Wylder als Vorgabebuild.

## An ui-ux-designer

Eine Abweichung von AK-355: die Differenz der Zeile *Weapon art* ist ein
**gefaerbter Text, kein Link**. AK-361 nennt ausdruecklich "einen zweiten
Link-Schluessel neben `AR_BREAKDOWN_KEY`" (den der Zauberzeile), und fuer
einen dritten ist kein Tooltipinhalt vorgegeben; ein Link auf die
AR-Aufschluesselung wuerde dort die Zahl *ohne* den Kunstfaktor zeigen. Wenn
die Kunstzeile einen eigenen Klick bekommen soll, braucht sie eine eigene
AK mit Inhalt.
