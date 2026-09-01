# QA-Befunde — Nightreign Helper

Quelle: T-002, `qa-engineer`, Zyklus 1.
Stand bei der Pruefung: `3da8428` (v1.7.1).
Geprueft gegen **echte Spieldaten** (Installation `D:\SteamLibrary`, DLC vorhanden;
Snapshot mit 2076 Effekten, 849 Relikten, 74 Kelchen) und **zwei echte Savefiles**,
sofern in der Spalte "Verifiziert" so vermerkt.
Status je Befund: offen | behoben | zurueckgestellt

## Log

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-001 | Weapons-Tab rechnet anderen Build als der Planner (Flueche, Waffeneffekte, `declared`, Waffen-Gates fehlen im zweiten `compute`-Aufruf) | P1 | Major | developer | echte Daten | offen | 2026-09-01 |
| QA-002 | Dasselbe physische Relikt in zwei Slots legbar und doppelt gezaehlt | P1 | Major | developer | echte Daten | offen | 2026-09-01 |
| QA-003 | Build-Namen ungeprueft im QSettings-Schluesselraum; Builds gehen lautlos verloren | P2 | Critical | developer | echte Daten | offen | 2026-09-01 |
| QA-004 | Mehrere Steam-Konten: das "vollste" Save gewinnt still, das Label unterscheidet nicht | P2 | Major | developer, ui-ux-designer | echte Daten | offen | 2026-09-01 |
| QA-005 | Keine automatisierten Tests; die im Code zitierten Smoke-Waechter fehlen im Repo | P2 | Major | director, developer | verifiziert | offen | 2026-09-01 |
| QA-006 | Allow-Listen-Gate fuer Scholar/Undertaker ganz uebersprungen; 38 beschraenkte Effekte zaehlen dort mit | P2 | Major | developer, director | echte Daten | **zurueckgestellt** (Nutzerentscheid "wirkt"; Waechter-Test bleibt) | 2026-09-01 |
| QA-007 | Save-Pruefsumme immer falsch; der produktive Lesepfad prueft sie gar nicht (toter Code) | P3 | Major | developer | echte Daten | offen | 2026-09-01 |
| QA-008 | "No save file found." bei vorhandenem Save ohne Relikte | P3 | Minor | ui-ux-designer, developer | Codepfad | offen | 2026-09-01 |
| QA-009 | `MIN_HEROES = 4` verlangt tatsaechlich fuenf Gruppen | P3 | Minor | developer | synthetisch | offen | 2026-09-01 |
| QA-010 | `_read_settled` wartet nicht und meldet nicht, wenn es aufgibt; README verspricht mehr | P3 | Minor | developer, ui-ux-designer | statisch | offen | 2026-09-01 |
| QA-011 | Rechenweise haengt an globalem `model.configure`-Zustand (−60 % statt +40 %) | P3 | Minor | developer | echte Daten | offen | 2026-09-01 |
| QA-012 | Gated-Effekte umgehen die Bedingungspruefung bei Resistenzen (latent, heute 0 Faelle) | P4 | Minor | developer | statisch | offen | 2026-09-01 |

## Die Kernfrage des Auftrags

**Pruefen die vorhandenen Mittel, ob das Programm richtig rechnet — oder nur,
dass es tut, was es tut?** Antwort: **weder noch.** Es gibt null automatisierte
Tests. Die einzige maschinelle Pruefung ist ein Import-Smoke-Test ueber drei
Module in `release.yml`. Die Regressionswaechter, die der Code selbst als
Absicherung zitiert (`smoke_dlc_effects.py` in Commit `ec061ff`,
`smoke_layout.py` in `app.py:1070`), existieren **in diesem Repo nicht** — sie
liegen laut Kommentar im privaten Arbeits-Repo. Der Waechter schuetzt also
nicht das, was veroeffentlicht wird.

Was das Programm heute vor falschen Zahlen schuetzt, ist die sehr sorgfaeltige,
in Kommentaren dokumentierte Handmessung des Autors — **Wissen, nicht
Mechanik**. Genau dort, wo dieses Wissen nicht hinreichte, liegen die Befunde.

## Was gehalten hat

Das ist kein Beiwerk, sondern der Grund, warum die Befundzahl den Zustand
schlechter aussehen laesst, als er ist:

- Voller Durchlauf **10 Nightfarer x 11 Kelche** gegen das echte Save:
  0 Abweichungen. Zweiter und dritter Lauf in derselben Sitzung und ein Lauf
  in neuer Sitzung mit persistierten Einstellungen: ebenfalls 0. **Kein
  Zustandsleck zwischen Nightfarern oder Kelchen** — die Klasse, die vier
  Releases lang nachgebessert wurde, haelt jetzt.
- **110 von 110 Loadouts** exakt gegen das Save reproduziert.
- `find_loadout_table` auf synthetischen Saves: 8x3, 10x3, 10x4, 0 Grails,
  12 Grails und **pro Nightfarer verschiedene Breiten** — alle korrekt. Die
  1.3.1/1.3.2-Fehlerklasse ist fuer diese Faelle geschlossen.
- Robustheit: leere, abgeschnittene, genullte, magic-zerstoerte und bis zu
  5000 Byte verfaelschte Saves fuehren zu sauberem Abbruch oder unveraenderten
  korrekten Zahlen — keine Abstuerze.
- Vollstaendiger Betrieb **ohne Savefile**: keine Ausnahme.
- 220 Kombinationen Hero x Kelch x Deep x Level auf unplausible Zahlen
  (NaN, Inf, Attribute ausserhalb 1–200, negative abgeleitete Werte):
  **0 Treffer**.
- Attribut-Minimum bei 20-fach gestapeltem Fluch korrekt auf 1 geklemmt, mit
  Warnung.

## Entscheidungen des Directors

- **QA-001 und QA-002 werden vor dem Build-Berater terminiert**, nicht danach.
  Begruendung: Der Berater wird die **dritte** Aufrufstelle von
  `model.compute` — ohne die Konsolidierung aus QA-001 driftet er wie der
  Weapons-Tab. Ohne die Handle-Regel aus QA-002 verletzt er GOAL A4 (er
  schlaegt dasselbe Exemplar mehrfach vor).
- **QA-006 ist durch den Nutzerentscheid vom Tisch** (Status quo "wirkt") und
  faellt aus dem Fix-Zyklus heraus. Was bleibt, ist der Waechter-Test.
- **Kein Release**, solange QA-001 und QA-002 offen sind: beide erzeugen
  falsche Zahlen im Hauptpfad, beide ohne jeden Hinweis an den Nutzer.
- **QA-005** ist als Abnahmekriterium nicht direkt in `GOAL.md` abgebildet,
  aber A9 verlangt eine QA-Bestaetigung gegen ein Artefakt. Der Aufbau einer
  minimalen Testbasis wird im Fix-Zyklus mitbeauftragt — der `qa-engineer` hat
  die fuenf wichtigsten Testfaelle bereits als Text geliefert.

## Offene Fragen

- **QA-006 — ENTSCHIEDEN durch den Nutzer am 2026-09-01: "wirkt" (Status quo).**
  Die Zahlen bleiben wie heute; das Gate fuer Scholar und Undertaker bleibt
  uebersprungen. Damit ist QA-006 **kein Fix-Auftrag mehr**, sondern nur noch
  der Waechter aus QA-005: ein Test, der anschlaegt, sobald ein Spiel-Patch
  Allow-Flags fuer die DLC-Paare mitbringt — dann ist die Annahme widerlegt und
  die Entscheidung neu zu treffen. Status: **zurueckgestellt (bewusst)**.
  Die urspruengliche Frage zur Nachvollziehbarkeit: Wirken die 38 per Allow-Liste
  beschraenkten Effekte auf Scholar und Undertaker? Zwei gleich vertretbare
  Lesarten: (a) die Flags stammen aus der Zeit vor der Erweiterung und das
  Spiel prueft die DLC-Paare anders — dann ist "wirkt" richtig; (b) die
  Beschraenkung ist inhaltlich gemeint und gaelte fuer Scholar genauso — dann
  zaehlt das Programm falsch. **Die Dateien entscheiden das nicht.** Nach der
  Hausregel (A7) muesste das Programm die Unsicherheit aussprechen; das tut es
  in keine Richtung. Vorgelegt am 2026-09-01.
- **QA-002 — ENTSCHIEDEN durch den Nutzer am 2026-09-01: Besitz erzwingen.**
  Ein bereits belegtes Exemplar (Handle) wird in den uebrigen Slots nicht mehr
  angeboten. Freies Planen bleibt ueber "Custom relic" moeglich. Der Berater
  erbt die Regel dadurch automatisch (GOAL A4).
- **An den developer:** `chalices.save()` ueberschreibt den uebergebenen
  `deep`-Parameter mit `any(slots[3:6])` (begruendet), `save_build()` uebernimmt
  ihn unveraendert. Absicht oder Unachtsamkeit? Keine Auswirkung reproduzierbar.
  Ebenso die zwei parallelen `__last`-Schluessel in `chalices/` und `builds/`.

## Nicht getestet

- **Das gebaute Artefakt (PyInstaller-EXE).** Der Auftrag prueft den Quellstand;
  GOAL A9 verlangt ausdruecklich einen Lauf gegen ein Artefakt. Erststart,
  Startmenue-Eintrag, Icon-Pack-Bau und Verhalten in `Program Files` bleiben
  offen. → gehoert in den Release-Zyklus (`release-manager` build/clean-room,
  danach `power-user`).
- **Save-Lesen waehrend eines echten Speichervorgangs des Spiels** (QA-010).
  Die Hypothese zur verzoegerten NTFS-mtime ist unbelegt.
- **Zahlenrichtigkeit gegen das laufende Spiel.** Geprueft wurde gegen die
  Spieldateien und gegen sich selbst, nicht gegen das, was das Spiel anzeigt.
  Der README-Vorbehalt "Attack rating has not been verified against an in-game
  number" bleibt offen. **Das ist die eine Pruefung, die nur der Nutzer im
  Spiel machen kann — und fuer den Build-Berater waere sie die wertvollste.**
- Performance und Speicher (gehoert zum `performance-tuner`). Beobachtet, nicht
  bewertet: Extrahieren ~41 s, voller Kelch-Durchlauf ohne merkliche Verzoegerung.


## Nachmessung OF-7 (2026-09-01, gegen Save 76561198179244962)

Auf Nachfrage des Directors gemessen statt abgeleitet:

- **Vier Farbklassen**, gleichmaessig verteilt: Red 75 / Blue 83 / Yellow 81 /
  Green 70 (309 Relikte). Weiss ist **keine Relikt-Farbe**, sondern eine
  Eigenschaft des *Slots* — ein weisser Slot nimmt jede Farbe.
- **101 von 309 sind Deep** (32,7 %). Normal und Deep sind disjunkte
  Kandidatenraeume.
- **Rollen-Dedup bringt fast nichts: 309 Exemplare → 306 verschiedene Rollen
  (1,0 % Ersparnis).** Auf 306 Rollen kamen genau drei Kollisionen. Drei
  Effekte aus einem grossen Pool kollidieren selten.
- **Der eigentliche Kostentreiber sind weisse Slots:** 205 Kandidaten normal
  bzw. 101 deep gegenueber 49–54 bzw. 21–30 bei einem farbigen Slot — das
  Vierfache. **20 von 74 Kelchen** haben mindestens einen weissen Slot, das ist
  kein Randfall. Ungeuenstigster realer Fall `Wylder's Chalice` mit Deep:
  roher Produktraum **8,18 Mrd.** ueber 6 Slots.

**Rueckwirkung auf QA-002:** Bei 306 verschiedenen Rollen auf 309 Exemplaren
steht in **99 %** der Faelle ein Picker-Eintrag fuer genau ein physisches
Relikt. Wer denselben Eintrag zweimal waehlt, waehlt fast immer dasselbe
Exemplar zweimal — das Doppelzaehlen ist die Regel, nicht die Ausnahme. P1
bleibt, die Begruendung wird staerker. Fuer den Berater heisst das: er muss
ueber **Handles** arbeiten; Rollen-Identitaet ersetzt Exemplar-Identitaet nicht.
