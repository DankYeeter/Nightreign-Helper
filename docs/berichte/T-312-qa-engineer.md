STATUS: erledigt
AUFTRAG: T-312c - qa-engineer, A24-Nachweis und AK-319..326 adversarial am
Artefakt 1.15.0 (`dist\NightreignHelper.exe`, 59.152.448 B, SHA-256
`E2F614F8...8405A`), Erstlauf gegen die 60-s-Schranke (OF-45)
GELESEN: docs/tasks/T-312.md (vollstaendig); docs/berichte/T-312-release-manager.md;
UI_SPEC.md Abschn. 7.4/7.6 (AK-319..326 Volltext, Z. 5404-5697); GOAL.md A24;
qa/findings.md (Tabellenkopf + Endstand, letzte Nummer QA-286);
ARCHITECTURE.md Z. 6900-7980 (Belegketten-Regel `single`/`group`/`ambiguous`/
`unresolved`, die fuenf namenlosen Karten 4890/4918/4930/5211/5212,
`PLAYER_GROUPS`/`DepthsTab` = Tab "Red variants", nicht "Deep of Night");
docs/perf/baselines.md Abschn. S13 (Grundlinie `extract.build()` 33,91 s,
OF-45-Herleitung); scripts/drive_window.ps1 (Volltext); nrplanner/firstrun.py
Z. 630-689 (`_Builder.run`: zwei Phasen, `write_snapshot` + `iconbuild.build`);
nrdata/iconbuild.py Git-Historie (`git log`, letzte Aenderung `8e1ea80`,
ausserhalb des Diffs `ffac292..79b3ecb`)
GEAENDERT: nichts im Arbeitsbaum. `docs/berichte/T-312-qa-engineer.md` (dieser
Bericht, neu). `qa/findings.md` angehaengt (QA-287, QA-288). Scratchpad:
`<Scratchpad>/T-312/qa-engineer/` (Screenshots, drei isolierte LOCALAPPDATA-
Ordner, einer davon mit dem Testabzug bestueckt)
ANNAHMEN: "Deep-of-Night-Tab ohne Beispielspalte" im Auftragstext meint die
Klasse `DepthsTab` (Datei `depthstab.py`, PLAYER_GROUPS/AK-325/326) - das ist
in der Oberflaeche der Tab **"Red variants"**, nicht der gleichnamige Tab
"Deep of Night" (Klasse `DeepTab`, andere Datei `deeptab.py`, AK-95..97).
Geprueft wurde der tatsaechliche Ort der Funktion (Red variants).
NAECHSTER: director (Gesamturteil, OF-45-Frage an performance-tuner: S13 auf
den vollen Erstlauf inkl. `iconbuild.build()` erweitern oder OF-45 als
Funktionsdefinition praezisieren)
BLOCKIERT DURCH: nichts

---

# T-312c - qa-engineer: A24-Nachweis + AK-319..326 + Erstlauf-Schranke

## Risiko-Briefing

Am riskantesten ist die Erstlaufzeit (OF-45, 60-s-Schranke): die Grundlinie
in `docs/perf/baselines.md` S13 misst nur `extract.build()` (33,9 s) und sagt
selbst, das sei "der limitierende Faktor" - eine Annahme, die nie am vollen
Fensterlauf (inkl. `iconbuild.build()`, zweite Phase in `firstrun.py`)
nachgemessen wurde. Zweitens die Baumlogik (AK-319/321/322): Gruppierung,
Sortierung bei Gleichstand, `key`-Auswahl bei doppeltem Namen und die
Sonderfaelle `ambiguous`/`unresolved` - hier lag beim letzten Architekturstand
0 Karten in diesen beiden Ketten, die Pfade sind also am Artefakt nicht
erreichbar und nur pruefbar, wo `confidence` echt greift. Drittens die
Beute-Sortierung (AK-324, Rundungs-/Tiebreak-Fehler sind erfahrungsgemaess
die haeufigste Klasse). Reihenfolge: Erstlauf zuerst (Blocker-Potential fuer
den Bericht insgesamt), dann A24-Kernnachweis, dann AK-Adversarial.

## Bestehende Tests

`pytest -n auto`: **1807 passed, 9 skipped in 136,59 s** - keine Fehlschlaege,
keine Regression gegenueber dem Registerstand vom 15.09. (1718/9). Deckt laut
Dateisuche auch `ambiguous`/`unresolved`-Rendering und das `days=[1,2]`-
"also Day X"-Suffix strukturell ab (`test_nightlord_panel_display.py`,
`test_nightlord_selection.py`) - beide Pfade sind auf dem aktuellen Testabzug
(EXTRACT_VERSION 15) durch keine echte Karte auslösbar (s. u.), die
Unit-Tests sind hier die einzige Absicherung.

## Erstlauf gegen die 60-s-Schranke (OF-45) - Befund

**Ueberschritten, dreifach reproduziert.** Methode: `Start-Process` auf das
Artefakt mit leerem `LOCALAPPDATA` (drei frische, nie benutzte Ordner
nacheinander), Stoppuhr bis das Nightlords-Tab per UIA auffindbar ist
(vollstaendig geladenes Hauptfenster).

| Lauf | LOCALAPPDATA | Gesamt |
|---|---|---|
| 1 | `localappdata_cold` (leer) | **66,65 s** |
| 2 | `localappdata_cold2` (leer) | **65,42 s** |
| 3 | `localappdata_cold3` (leer, mit Phasenprotokoll) | **63,40 s** |
| Kontrolle | `localappdata_warm` (Testabzug kopiert) | 3,30 s |

Phasenprotokoll aus Lauf 3 (Textinhalte der Erstlauf-Fortschrittszeile, per
UIA mitgeschnitten):

- 0-3,08 s: Fensteraufbau, "Reading the game's data tables ..." beginnt.
- 3,08-37,66 s (**34,58 s**): Phase 1 (`extract.write_snapshot`) - deckt sich
  mit der S13-Grundlinie (33,91 s), **keine Abweichung hier**.
- 37,66-59,36 s (**21,70 s**): Phase 2 "Decoding artwork ..." /
  `iconbuild.build` (Portraits, Verifikation, DLC-Illustrationen) - **diese
  Phase steht in keiner Grundlinie**; S13 misst ausdruecklich nur
  `extract.build()`.
- 59,36-63,40 s: restlicher Fensteraufbau (Build-planner-Tab mit echten
  Nutzerdaten, 313 Relikte / 110 Builds, real aus dem Spielstand gelesen -
  read-only, CLAUDE.md erlaubt das).

**Ursache (Hypothese, durch Codelesen gestuetzt):** `firstrun.py:642-689`
(`_Builder.run`) fuehrt zwei Schritte aus, `extract.write_snapshot` **und**
`iconbuild.build`. Die S13-Messung (`docs/perf/baselines.md` Z. 624-666)
misst nur den ersten und schliesst daraus, `build()` sei "der limitierende
Faktor fuer den Erstlauf" - diese Aussage ist an diesem Artefakt widerlegt:
die zweite Phase kostet mit rund 22 s beinahe so viel wie die erste. `git log
-- nrdata/iconbuild.py` zeigt die letzte Aenderung bei `8e1ea80`, ausserhalb
des Diffs `ffac292..79b3ecb` dieses Auftrags - **die Kosten sind nicht neu
durch A24 entstanden**, sondern ein bereits vor T-312 bestehender, nie am
vollen Fensterlauf gegengeprueften Teil des Erstlaufs.

### [P2 | Major | Hoch] Erstlauf mit leerem Cache ueberschreitet die 60-s-Schranke aus OF-45

**Adressat:** developer (Ursache/Fix), performance-tuner (Grundlinie S13
unvollstaendig), director (Releasefrage zu OF-45)
**Betroffen:** `nrplanner/firstrun.py:642-689` (`_Builder.run`,
`iconbuild.build`-Phase); `docs/perf/baselines.md` Abschn. S13
(Messumfang); `ARCHITECTURE.md` Z. 7663 (Folgerung "weit innerhalb der
60-s-Schranke" ist am vollen Fensterlauf nicht belegt)
**Umgebung:** Artefakt 1.15.0, leeres `LOCALAPPDATA` (kein Testabzug), echte
Spielinstallation dieser Maschine, `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-312c`

**Reproduktion:**
1. `LOCALAPPDATA`/`APPDATA` auf einen frischen, leeren Ordner umlenken,
   `NIGHTREIGN_SETTINGS_ORG` setzen.
2. `dist\NightreignHelper.exe` starten, Zeit bis zum voll geladenen
   Hauptfenster (Nightlords-Tab abrufbar) stoppen.
3. Wiederholen mit zwei weiteren frischen leeren Ordnern.

**Erwartet:** Erstlauf unter 60 s (OF-45, wortgleich im Auftrag T-312c und in
`ARCHITECTURE.md` als Schranke fuer Stufe 1+2 genannt).
**Tatsaechlich:** 66,65 s / 65,42 s / 63,40 s (n=3, Mittel 65,2 s) - 5-7 s
(8-11 %) ueber der Schranke, bei jedem der drei Laeufe.

**Analyse:** Die dokumentierte Grundlinie (33,9 s) misst nur
`extract.write_snapshot`/`extract.build()`; der tatsaechliche Erstlauf fuehrt
danach `iconbuild.build()` aus (rund 22 s zusaetzlich), das in keiner
Perf-Messung dieses Projekts vorkommt. Die S13-Schlussfolgerung "der
limitierende Faktor... ist build() selbst" ist damit unvollstaendig, nicht
falsch gemessen - sie hat schlicht nie den zweiten Schritt eingeschlossen.

**Auswirkung:** Jeder neue Nutzer durchlaeuft den Erstlauf genau einmal - das
ist der Hauptpfad, keine Randbedingung. Eine Schranke, die im GOAL/UI_SPEC
als Abnahmekriterium (OF-45) benannt ist, wird beim einzigen bislang
existierenden End-zu-End-Nachweis verfehlt. Kein Datenverlust, kein Absturz,
die App bleibt nach dem Warten voll bedienbar (`Responding=True`, korrekte
Daten in allen drei Laeufen) - daher Major statt Blocker/Critical.

**Vorschlag:** Entweder `iconbuild.build()` beschleunigen (Kandidat:
Parallelisierung der Portrait-Dekodierung, oder ein Fortschritt, der bereits
frueher nutzbare Teile freigibt), oder OF-45 przisieren (60 s fuer welchen
Schritt genau?) und `docs/perf/baselines.md` S13 um eine Zeile fuer
`iconbuild.build()` sowie den vollen Fensterlauf ergaenzen, damit die naechste
Messung nicht wieder nur die Haelfte des Erstlaufs sieht.

## A24-Nachweis (GOAL.md, Nutzerentscheidung OF-46: Feldboss statt Evergaol)

Am Nightlords-Tab, Nachtfuerst Gladius, Baum unter den Kacheln:

- **Feldboss** (Fell Omen, 4551): Rollenzeile "Field boss"; VITALS (HP
  2521); WEAKNESS SPECIAL INTERACTION; DAMAGE TAKEN-Balken, STATUS BUILDUP,
  STANCE - dieselbe Diagrammform wie ein Nachtfuerst-Profil (Gladius
  gegengeprueft, identische Abschnittsnamen/Balkenfarben); LOOT: fuenf offen
  (`All Resistances Up` .. `Ice Storm Surge Sprint`, alle 5 %, bei
  Gleichstand alphabetisch - AK-324.3 Tiebreaker bestaetigt), Knopf
  "Show 15 more" -> per echtem Mausklick 20 Eintraege, Knopf wird
  "Show fewer", weiterhin alphabetisch bei 5 % (A,C,F,F,I×9,L,P,R). Notiz
  unter der Liste wortgleich mit AK-324.4.
- **Nachtboss mit Tag-Kennung**: `Outland Commander` erscheint unter
  Heolstor the Nightlord zweimal (Day 1 10 %, Day 2 8 %) - Auswahl der einen
  Zeile markiert nur diese (Rollenzeile "Night boss · Day 1" bzw. "· Day 2"),
  die andere bleibt unmarkiert (AK-321.2, `key`- statt `name`-Auswahl
  bestaetigt, auch ohne die im Auftrag genannten konkreten Ids 4926/4927 -
  der Mechanismus ist derselbe). Zusaetzlich `Fell Omen`/`Demi-Human Queen`
  je einmal Day 1 und Day 2 unter verschiedenen Nachtfuersten beobachtet.
- **Filter wechselt mit dem Nachtfuersten**: Gladius, Adel und Heolstor the
  Nightlord zeigen drei sichtbar unterschiedliche Night-Boss-Listen (z. B.
  Gladius Day 1 nur `Bell Bearing Hunter`/`Demi-Human Queen`; Adel Day 1
  `Gaping Dragon`/`Night's Cavalry`/`The Duke's Dear Freja`/`Valiant
  Gargoyle`/`Not identified`; Heolstor 15 Zeilen inkl. zwei `Not identified`).
- **Karten ohne Namen** (4890/4918/4930/5211/5212, Beleg aus
  `ARCHITECTURE.md` Z. 7834): live unter Adel Day 1 eine Zeile `Not
  identified` mit Anteilswert (18 %) statt einer leeren Zeile; Detailpanel
  zeigt trotz fehlendem Namen volle Werte (HP 556, WEAKNESS SPECIAL
  INTERACTION, DAMAGE TAKEN) - das ist laut Architektur die korrekte Antwort
  fuer `confidence="single"`/`"group"` ohne aufloesbaren Namen, **nicht**
  dasselbe wie `ambiguous`/`unresolved` (AK-322.4/5 gelten nur fuer die
  beiden echten Unsicherheits-Ketten, s. u.).

## AK-319..326 adversarial

- **AK-319** (Struktur/Reihenfolge/Spalten): drei Gruppen wortgleich
  ALL-CAPS, alphabetisch je Gruppe, `Not identified`-Zeilen ans Ende (nach
  Id sortiert, nicht ueberprueft, da Id in der UI nicht sichtbar - Reihenfolge
  selbst stimmt); keine eigene Bildlaufleiste am Baum (eine Leiste fuer den
  ganzen Tab, in zwei Nachtfuersten-Ansichten mit >60 Zeilen bestaetigt).
- **AK-319.5** (`days=[1,2]`, "also Day X"-Zusatz): **an keiner der 10
  Nachtfuersten-Ansichten auf diesem Testabzug auslösbar** (0 Treffer fuer
  "also Day" ueberall) - durch Unit-Test abgedeckt
  (`test_nightlord_panel_display.py`), am Artefakt nicht nachstellbar, weil
  keine Karte diese Kombination traegt.
- **AK-319.7 / Tab-Reihenfolge**: von einer Kachel aus durchlaeuft Tab alle
  10 Kacheln, dann den Baum (erste Station eine Gruppenzeile), dann
  **direkt** die Tab-Leiste ("Nightlords") - das Detailpanel wird beim
  Tabben uebersprungen, wie AK-321.3 verlangt ("nur lesend, nicht
  fokussierbar"). Pfeil-runter im Baum bewegt den Fokus zeilenweise, Enter
  waehlt (Detailpanel + Hervorhebung aktualisiert) - beides live bestaetigt.
- **AK-320** (Leerzustand): vor jeder Kachelwahl exakt die eine Zeile "Select
  a Nightlord above to see which field and night bosses can appear for it."
  wortgleich.
- **AK-321** (Auswahlkonsistenz, `key` bei Doppelname): Outland-Commander-
  Fall oben, live bestaetigt.
- **AK-322/323/324**: Rollenzeile, VITALS, LOOT wie oben; `ambiguous`
  ("Multiple possible bosses") und `unresolved` ("Not derivable for this
  fight.") sind auf diesem Artefakt/Testabzug **strukturell nicht
  erreichbar** - `ARCHITECTURE.md` Z. 7832-7837 nennt die Erwartung nach
  AD-044 explizit als `single 64, group 0, ambiguous 0, unresolved 0`;
  beide Pfade sind nur durch Unit-Tests abgedeckt
  (`test_nightlord_panel_display.py`), nicht live nachgewiesen.
- **AK-325/AK-326**: bestaetigt, aber am Tab **"Red variants"**
  (`DepthsTab`/`depthstab.py`), nicht am gleichnamigen Tab "Deep of Night"
  (`DeepTab`/`deeptab.py`) - der Auftragstext verweist auf den Dateinamen,
  nicht den Tabnamen (Annahme oben). Kopfzeile "What can be red" einzige
  Textspalte, Zeilen wortgleich ("Ordinary enemies in camps & ruins",
  "Named minibosses", "Mixed-boss arena locations", "Field bosses & arena
  locations", "Merchants", "Unidentified enemies"), keine
  "Examples (any map)"-Spalte mehr, Depth-Spalten "Depth 1"/"Depth 2-3"/
  "Depth 4-5".

## Testbarkeit - Beobachtung (kein Produktfehler)

### [P3 | Minor | Niedrig] `TogglePattern.Toggle()` loest den Beute-Umschalter "Show N more" nicht aus - nur ein echter Mausklick

**Adressat:** developer
**Betroffen:** `bosstab.py` (Loot-Umschalter, AK-324.3), `QToolButton`
(checkable)

**Reproduktion:**
1. Feldboss mit >5 Beute-Eintraegen waehlen (z. B. Fell Omen).
2. Per UI-Automation `TogglePattern.Toggle()` auf den Knopf "Show 15 more"
   aufrufen (kein echter Mausklick).
3. Beschriftung/Liste aendern sich nicht.
4. Derselbe Knopf per echtem `SetCursorPos`+`mouse_event`-Klick: Liste
   erweitert sich sofort auf 20 Eintraege, Beschriftung wird "Show fewer".

**Erwartet:** Ein Umschalter, der auf Toggle-Zustand reagiert, sollte auch
programmatisches Umschalten ueber die Standard-UIA-Pattern anstossen (wie
von assistiven Technologien erwartet).
**Tatsaechlich:** Nur ein echter Klick loest die Aktualisierung aus.

**Analyse (Hypothese):** Der Knopf ist vermutlich an `clicked` statt
`toggled` gebunden, oder das Qt-Accessibility-Bridge-`Toggle()` ruft
`setChecked()` ohne das Signal auszuloesen, das `show_detail` erneut
aufruft.

**Auswirkung:** Reine Tastatur-/Screenreader-Bedienung ueber UI-Automation
koennte an dieser Stelle hängen bleiben; mit echter Maus oder echter
Tastatur (Leertaste im Fokus, nicht getestet) vermutlich unbetroffen -
daher Minor/Niedrig, kein Blocker.

**Vorschlag:** Pruefen, ob der Knopf auf `toggled(bool)` statt `clicked()`
reagieren sollte, oder ob QAccessible fuer diesen `QToolButton`-Typ
grundsaetzlich `click()` statt `toggle()` erwartet.

## Nicht getestet

- Windows-Textskalierung (System-DPI/Schriftgroesse) fuer die Baumhoehe:
  bewusst nicht veraendert - ein Eingriff in die Systemumgebung der
  Nutzermaschine, ausserhalb des Testfensters. Ersatzweise die App-eigene
  "UI scale"-Dropdown angetestet, liess sich per simuliertem Klick nicht
  zuverlaessig oeffnen (Werkzeuggrenze, keine weitere Zeit investiert).
- Nachtboss `5201 Runebear Tag 1` namentlich - der Tag-Mechanismus wurde
  stattdessen an `Outland Commander`/`Fell Omen`/`Demi-Human Queen` bestaetigt
  (gleicher Code, gleiches Verhalten); keine gezielte Suche nach Runebear
  unternommen.
- `ambiguous`/`unresolved`-Panelinhalt live (kein Datensatz mit dieser Kette
  auf dem aktuellen Testabzug, s. o.) - nur Unit-Test-Beleg.
- `AK-319.5` ("also Day X") live - siehe oben.
- Effects & chances, Weapons & spells, World Events, Build planner im Detail
  - nur ueber die volle Testsuite (gruen) und den Erstlauf-Endbildschirm
  (Build planner korrekt befuellt) mitgeprueft, kein eigener Adversarial-Lauf,
  da ausserhalb des A24-Diffs und ohne erkennbares Risiko aus T-312b/dem
  Sicherheitsdiff.
- Sicherheitsaspekte des neuen EMEVD-/MSB-Lesers - T-312b (security-reviewer),
  eigener Auftrag.

## Zusammenfassung (an director)

**1×P2, 1×P3.** P2: Erstlauf mit leerem Cache 63,4-66,7 s (n=3), ueber der
60-s-Schranke aus OF-45 - die dokumentierte Grundlinie deckt nur die Haelfte
des tatsaechlichen Erstlaufs ab. P3: UIA-`Toggle()` auf dem Beute-Umschalter
wirkungslos, nur Mausklick funktioniert. A24-Kernnachweis (Feldboss mit
Diagrammen/HP/Beute, Nachtboss mit Tag-Kennung, Filter je Nachtfuerst,
namenlose Karten mit Werten) sowie AK-319..326 (soweit am Artefakt
erreichbar) **bestaetigt**. Testsuite 1807/9 gruen, keine Regression.

**Gesamturteil: FAIL** - P2-Befund (Erstlauf-Schranke OF-45 verfehlt, dreifach
reproduziert). Mindestens zu klaeren, bevor freigegeben wird: entweder
`iconbuild.build()` beschleunigen, bis der volle Erstlauf unter 60 s bleibt,
oder OF-45 im GOAL/UI_SPEC neu fassen (Schranke gilt nur fuer
`extract.build()`, nicht den vollen Erstlauf) und diese Praezisierung im
Register/Architektur nachtragen. Der Befund ist nicht neu durch A24
verursacht (iconbuild.py seit `8e1ea80` unveraendert) - das ist eine
Vorbedingung, die bislang nie am vollen Fensterlauf gegen OF-45 geprueft
wurde, kein Regressions-Vorwurf an T-303..T-310.

## Explorationsprotokoll

Fensterlauf ueber `scripts/drive_window.ps1` (UIA + echte Klicks/Tastatur),
drei isolierte LOCALAPPDATA-Ordner (einer mit dem Testabzug 841 Dateien/
21 131 645 B bestueckt, zwei leer fuer die Erstlaufmessung), eigener
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-312c`. Fenster zeitweise maximiert
(UIA-Bildschirmkoordinaten unterhalb der Fensterhoehe waren sonst nicht
klickbar - Werkzeugbeobachtung, kein Produktfehler, `ClickAt`s eigene
Pid-Wache hat das korrekt verhindert statt einen falschen Klick abzusetzen).
Ein Bash-Lauf brach durch einen API-Fehler der Umgebung ab (16:04, kein
eigener Befund); Fortsetzung mit derselben laufenden Instanz, keine
Datenluecke.
