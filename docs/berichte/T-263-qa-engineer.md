# T-263a — Pruefphase Zyklus 24 (qa-engineer), 15.09.2026 03:58-04:25

Code `478101c` (HEAD `97b0d9a`), eingefroren. Umlenkung
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-263qa`, `LOCALAPPDATA`/`APPDATA`/
`USERPROFILE` ins Scratchpad `T-263/`, Testabzug (841 Dateien) hineinkopiert,
`paths.snapshot_path()` zurueckgelesen. Spielstand: frozen_inventory (314),
`savefile.save_roots` auf leeres Verzeichnis. Kein `nightreign.exe` aktiv
(`tasklist`, 03:58). Fensterlauf 04:14 nach Vorliegen von
`docs/berichte/T-263-ui-ux-designer.md`; alle Zahlen am Fenster: Windows,
DPR 1,25, logisch, `WA_DontShowOnScreen` + `grab()` (NH-002).

## Urteil: FAIL (ein P2, QA-272)

| | Zahl |
|---|---|
| Suite (2 Vollaeufe, `-n auto`) | 1681 passed / 9 skipped, 73,7 s und 78,8 s, 0 rot |
| Teillauf Flacker-Klasse (7 Dateien, 3x) | 239 passed, 3x gruen |
| Mutationen | 6 von 6 getoetet, Registry geleert (OF-35) |
| A20 Messzellen | 6/6 an Kachel, Werteblatt und Arsenal (offscreen und `windows`) |
| Neue Befunde | 1 P2, 0 sonst |

## Befund

### [P2 | Major | Hoch] QA-272 Hand-Schalter des vorigen Nightfarers landet im Spielstand-Build des neuen

**Adressat:** developer
**Betroffen:** `nrplanner/app.py` `reload_chalices` Z. 1518-1525 (Import-Zweig
`not chalices.imported(hero)` → `load_equipped()` → `recompute()` →
`_store_chalice()` Z. 1700-1705) laeuft **vor** `_set_two_handed(two_handed)`
Z. 1554; zweiter Fall `reset_chalice` Z. 1890-1915 (kein `_set_two_handed`).
**Umgebung:** frozen 314, Registry leer, Wylder erster Held.

**Reproduktion:**
1. Wylder, Goblet, `2H` klicken (Store: `2H`, korrekt).
2. Guardian erstmals waehlen.
3. Schalter zeigt `2H`; `chalices.load(2, 2002)[3] is True` — der aus dem
   Spielstand importierte Guardian-Build ist mit `2H` gespeichert, ohne dass
   der Spieler ihn angefasst hat. Gleiches fuer Ironeye, Duchess, Revenant,
   Executor, Scholar, Undertaker (alle mit Spielstand-Build); Raider/Recluse
   (ohne Build) bleiben `1H`-los. Neustart: Guardian oeffnet mit `2H`.
4. Zweiter Fall: Wylder Chalice `2H`, `Reset Chalice` → springt auf Wylder's
   Urn (Store `1H`), Schalter bleibt `2H`; der naechste Slot-Wechsel schreibt
   `2H` auf den Urn-Build.

**Erwartet:** AN-3/AK-292: eine Hand je Build; der Schalter folgt beim
Wechsel dem Store des Ziel-Builds, nie umgekehrt.
**Tatsaechlich:** Beim ersten Besuch eines Nightfarers (einmal je Held, dann
`imported`) und nach `Reset Chalice` schreibt der Store den Schalterstand des
zuvor gezeigten Builds. Ablauf per `chalices.save`-Trace belegt:
`select_hero:1255 > reload_chalices:1524 > load_equipped:2644 > recompute:3061 >
_store_chalice:1700` mit `2H=True`.
**Gegenprobe:** Zweiter Besuch (Guardian `2H`, Wylder `1H`, zurueck zu
Guardian) haelt beide Haende korrekt — der Restore-Zweig setzt die Hand vor
dem Store. Gefaesswechsel innerhalb eines Helden ebenfalls korrekt.

**Auswirkung:** Wer im ersten Lauf frueh `2H` setzt und dann die Helden
durchklickt, bekommt bis zu neun fremde Builds dauerhaft als `2H`
gespeichert; der Berater rankt sie fortan zweihaendig (AK-293). Workaround:
je Held zuruecksetzen.
**Vorschlag:** Vor `load_equipped()` im Import-Zweig und in `reset_chalice`
die Hand aus dem Store des Ziel-Builds setzen (bzw. `1H` bei fehlendem
Record), oder `_store_chalice` waehrend `_restoring`/Import nicht aus dem
Schalter lesen. Wächter: Test mit zwei Helden, erster Besuch nach `2H`.

## A20 am Fenster

Sechs Zellen (Lv15, Relikte leer, `declared` leer), je Kachel / Werteblatt
(`Physical`, `Total`) / Arsenal-Kachel: Wylder Greatsword `122 / 125 2H AR`,
Raider Greataxe `158 / 180`, Guardian Halberd `107 / 110`, Duchess' Dagger
`72 / 74`, Great Stars uncommon Raider `188 / 216`, Wylder `147 / 151` —
6/6 OK, Format AN-5/AK-286 (`X / Y 2H AR`, NBSP-gebunden). Bilder im
Scratchpad `T-263/img/` (nicht im Repo). Schalter `1H`/`2H` 38x23 px
logisch, Tooltip `HAND_TOOLTIP`. Persistenz mit gefuelltem Build: Klick →
Store `2H` → Neustart `2H`, Nachbargefaess bleibt `1H`. Berater:
`asking_from(...).ctx.two_handed`/`request.two_handed` folgen dem Schalter.
Schalterwechsel in `WORKING_QUIETLY` → `OUTDATED`, Satz 4.7 `Your build
changed while this was working out — use Optimize again.`

## A18/A19-Regression

`mark(6001400, EXCLUDED)` → im `problem.excluded`, Registry `advisor/excluded`;
Umstellen auf `REQUIRED` entfernt aus excluded; unerfuellbare Pflicht →
`blocked_by_a_requirement=True`, Satz `No copy you own carries Physical Attack
Up +3, which you marked as required — no suggestion can meet that.`; nach
Neustart `required` erhalten. OK.

## Retests (Zeilen im Register)

QA-172, 186, 099a, 175, 036, 173, 269, 270 (Mischfall siehe Offene Fragen),
249, 238 **behoben**; QA-258 **teilweise** (1471 ms Median, n=5); DR-029 auf
`test_arsenal_same_name_tiles.py` (2 gruen, beide Vollaeufe) gestuetzt, nicht
eigenstaendig wiederholt.

## Mutationen (Klone aus `git archive 478101c`, nur Killer-Dateien)

| Mutation | rot | Abweichung zur Vorhersage |
|---|---|---|
| two-handed-rate-neutralised | 6 failed / 17 | keine |
| raider-two-handed-rate-neutralised | 4 / 19 | zusaetzlich `test_the_popup_names_the_factor_and_where_it_is_from`, `..._factors_are_the_measured_ones` |
| two-handing-buff-left-on-the-scoped-line | 2 / 26 | keine |
| hand-switch-ignored-by-the-mean | 2 / 12 | keine |
| hand-forgotten-by-the-store | 3 / 11 | zusaetzlich `test_one_handed_is_stored_exactly_as_every_build_before...` |
| hand-left-out-of-the-cache-key | 1 / 13 | keine |

`MUTATIONS` geleert (88 Zeilen), Literale in git `f4b43ed`;
`test_differential_track.py` 40 passed / 1 skipped, `--list` leer, pyflakes 0.

## A2-A8

A2: Register (letzte Zeile je ID) 9 P1/P2 nicht behoben — QA-004/016/077/
094/196/197/222/237/241, alle vorbestehend, T-256-triagiert (Prozess/klein) —
plus QA-272 neu. A3: 9 Richtungen liefern Vorschlaege (6/6 Slots, Wylder's
Chalice Deep). A4/A5: Why-Zeilen ohne Rohschluessel (QA-269), Stacking-Test
QA-257 in der Suite. A6: Optimize kalt 1693/1627/1813 ms, Hauptthread-Luecken
max 32 ms, 0 von 575 ueber 50 ms (5900X, nicht Zielgeraet). A7: 4.11-Klausel
nach Ursache, Faktorquelle im Popup (`test_the_popup_names_the_factor`). A8:
alle neuen Texte englisch (Tooltips, Gate-Wortlaute, 4.7/4.11).

## Beobachtungen

- Der Kommentar `effectstab.py:78` und die T-257a-Registerzeile nennen "23
  von 1064" widerspruechliche Identitaeten; nach `effectstab.identity` sind es
  12 (beide Datenquellen), 23 entsteht mit dem Anzeigeschluessel des Tests.
- `grab()` des Werteblatts zeigt gestapelte Zahlen in BASE STATS/ATTRIBUTES —
  Klasse DR-028 (verborgene Labels, T-259 belegt), kein Produktbefund.
- QA-258: der Kartencache lebt im Picker-Objekt; jede Oeffnung baut neu.

## Offene Fragen

- **director/ui-ux-designer:** QA-270-Mischfall (Leerpool + Pflicht) nennt nur
  die Pflicht. Reicht die tragende Ursache, oder beide Klauseln?
- **director (AN-6):** Slots leeren, `2H` setzen, Gefaess wechseln und zurueck
  → gespeicherter Build kehrt mit `1H` zurueck (leerer Build schreibt nicht).
  Wie AN-6 beschreibt, aber fuer den Spieler ueberraschend. Absicht?
- **developer:** `Load equipped` auf demselben Helden uebernimmt den aktuellen
  Schalter in den importierten Build — beabsichtigt?

## Nicht getestet

Zielgeraet (5800H); echte Maus/Doppelklick am Fenster (QA-222-Klasse);
Update-Weg/Artefakt (kein Build in diesem Auftrag); DR-029-Ueberschriften
eigenstaendig; A20 auf den nicht gemessenen Nightfarern (AN-1, keine
Referenz).
