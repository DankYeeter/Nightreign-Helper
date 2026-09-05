# QA-Befunde — Nightreign Helper

Quellen: T-002 (Zyklus 1, Erstaudit) und T-007 (Zyklus 2, Erstpruefung von T-006).
Geprueft gegen echte Spieldaten (`D:\SteamLibrary`, mit DLC) und zwei echte
Savefiles. Status: offen | teilweise behoben | behoben | zurueckgestellt

## Log

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-001 | Weapons-Tab rechnet anderen Build als der Planner | P1 | Major | developer | echte Daten | **behoben** — eine `compute`-Stelle, `current_build()`, Fluch-Build gegengeprueft | 2026-09-01 |
| QA-002 | Dasselbe physische Relikt in zwei Slots legbar und doppelt gezaehlt | P1 | Major | developer | echte Daten | **behoben** — interaktiv und ueber gespeicherte Builds; Restfall bei zwei Kopien eines Rolls → QA-021 | 2026-09-02 |
| QA-003 | Build-Namen ungeprueft im QSettings-Schluesselraum | P2 | Critical | developer | echte Daten | **behoben** - Release-Blocker gefallen; Restluecken der Migration als QA-033 (P1, Datenverlust) und QA-034 neu | 2026-09-02 |
| QA-004 | Mehrere Steam-Konten: das "vollste" Save gewinnt still | P2 | Major | developer, ui-ux-designer | echte Daten | offen - **dieselbe Wurzel wie QA-032**, wird dort mitgenommen | 2026-09-02 |
| QA-005 | Keine automatisierten Tests | P2 | Major | director, developer | verifiziert | **teilweise behoben** - 145 Tests; 12 von 15 Sicherheitsbefunden mutationsbelegt, drei SEC-002-Stellen unbewacht (QA-037) | 2026-09-02 |
| QA-006 | Allow-Listen-Gate fuer Scholar/Undertaker uebersprungen | P2 | Major | developer, director | echte Daten | zurueckgestellt (Nutzerentscheid) | 2026-09-01 |
| QA-007 | Save-Pruefsumme immer falsch; Lesepfad prueft sie nicht | P3 | Major | developer | echte Daten | offen | 2026-09-01 |
| QA-008 | "No save file found." bei vorhandenem Save ohne Relikte | P3 | Minor | ui-ux-designer, developer | Codepfad | offen | 2026-09-01 |
| QA-009 | `MIN_HEROES = 4` verlangt tatsaechlich fuenf Gruppen | P3 | Minor | developer | synthetisch | offen | 2026-09-01 |
| QA-010 | `_read_settled` wartet nicht und meldet nicht, wenn es aufgibt | P3 | Minor | developer, ui-ux-designer | statisch | offen | 2026-09-01 |
| QA-011 | Rechenweise haengt an globalem `model.configure`-Zustand | P3 | Minor | developer | echte Daten | **behoben** — `compute` verweigert ohne `configure` | 2026-09-01 |
| QA-012 | Gated-Effekte umgehen die Bedingungspruefung bei Resistenzen | P4 | Minor | developer | statisch | offen | 2026-09-01 |
| QA-013 | Gemerkte Sucheingabe leert beim naechsten Relikt-Wechsel die uebrigen Slots | P1 | Critical | developer | echte Daten, Deep-Slot | **behoben** — Suche aus `populate` entfernt, Regel im Slot erzwungen | 2026-09-02 |
| QA-014 | Gefaesswechsel: Relikt aus dem alten Build verhindert die Wiederherstellung des neuen | P1 | Critical | developer | echte Daten, A/B, Rundreise | **behoben** — auch bei gleicher Slotposition und ueber 10 Rundreisen | 2026-09-02 |
| QA-015 | Alte Builds mit doppeltem Relikt: doppelt wiederhergestellt, dann still geloescht | P2 | Major | developer | echtes Save, Attributraster | **behoben** — beim Restore aufgeloest, erster Slot behaelt, Zahl sofort richtig | 2026-09-02 |
| QA-016 | Praemisse der AD-013-Abweichung am echten Save widerlegt; Offset-Zweig tot | P2 | Major | developer, architect | echte Daten | offen | 2026-09-01 |
| QA-017 | Waechter "eine `compute`-Stelle" ist Textsuche und sieht das Berater-Paket nicht | P3 | Minor | developer | statisch + probiert | **behoben** — AST + `rglob`; Restluecke als QA-023 | 2026-09-02 |
| QA-018 | Waffen-/Arsenal-Tab zeigen andere AR als die Waffentafel (203,4 gegen 244,1) | P2 | Major | developer | echte Daten | **BEHOBEN** (P1, T-033) - Nutzerentscheid: nur bei Konter. 4 Effektfamilien (~22 IDs) aus der flachen Schicht genommen. Ausgangsfall bestaetigt: 203,4 auf Kachel und Tafel. Golden-Datei neu aufgenommen | 2026-09-03 |
| QA-019 | Zwei Golden-Faelle pruefen nicht den Zweig ihres Namens; ein Zweig unabgedeckt | P3 | Minor | developer | echte Daten | **behoben** - Golden-Fall umbenannt statt geloescht ("a two-type armament with no relic effects"), keine expected-Werte veraendert | 2026-09-03 |
| QA-020 | Loadout-Fehlermeldung zeigt Leserinterna | P4 | Minor | ui-ux-designer | echte Daten | offen (aelter als T-006) | 2026-09-01 |
| QA-021 | Zwei eigene Exemplare desselben Rolls: eines geht bei jedem Restore verloren | P2 | Major | developer | **beide echten Saves, 104 Rundreisen, Deep sichtbar+verdeckt, Rollen-Fallback, veraltete Handles, handle-lose Kopien** | **behoben** | 2026-09-02 |
| QA-022 | "Already worn in Slot N" bleibt stehen, nachdem Slot N geleert oder neu belegt wurde | P3 | Minor | developer | echte Daten, 3 Wege | **behoben** | 2026-09-02 |
| QA-023 | `compute`-Waechter erkennt Schreibweisen, nicht Zugriffe; Suchraum ohne `run.py`/`scripts` | P4 | Minor | developer | probiert | offen | 2026-09-02 |
| QA-024 | "Load equipped"-Meldung nennt eine Suche, die es nicht mehr gibt | P3 | Minor | developer | echte Daten, 5 Faelle | **behoben** — Rest als QA-031 | 2026-09-02 |
| QA-025 | "Custom relic" verschwindet bei jedem Neuanwenden des Gefaesses | P2 | Major | developer | echte Daten, volle Kantenmatrix inkl. Deep-Slot und Neustart | **behoben** | 2026-09-02 |
| QA-026 | `_settle_slots` leert einen ausgeblendeten Deep-Slot; Begruendung unsichtbar | P4 | Minor | developer | echte Daten | offen — **Statuskorrektur des Directors: NICHT entschaerft.** Der Verlust wird weiterhin gespeichert, nur einen Klick spaeter (QA-030) | 2026-09-02 |
| QA-027 | `inventory.py:284` — ein nicht mehr besessenes Relikt aus der Loadout-Tabelle wird still zu `None` und ist von einem leeren Slot ununterscheidbar | P3 | Minor | developer | Codepfad | offen | 2026-09-02 |
| QA-028 | `custom_item` ueberlebt bei gleicher Slotfarbe **auch einen Gefaesswechsel** und wird im Picker eines fremden Builds angeboten | P4 | Minor | developer | echte Daten, Alt/Neu-Gegenprobe | offen — Reichweite in T-016 erweitert | 2026-09-02 |
| QA-029 | `DESIGN_REVIEW.md` verweist an drei Stellen auf `select_saved`/`select_handle` — die Namen gibt es seit T-015 nicht mehr | P4 | Minor | ui-ux-designer | verifiziert | offen | 2026-09-02 |

## Zyklus 2, zweite Runde (T-014): Fixes bestaetigt

QA-013, QA-014, QA-015 und QA-017 sind **geschlossen** — unabhaengig geprueft, nicht
uebernommen. Der alte Baum wurde ausgepackt und die heutigen Tests darueber gefahren:
genau die sechs behaupteten Tests fallen dort. **Der Fix hat diesmal keine neue P1
erzeugt** — alle fuenf vom `developer` als ungetestet gemeldeten Pfade wurden gefahren.

## Entscheidungen des Directors (2026-09-02)

- **QA-021 und QA-025 vor dem Build-Berater.** QA-021 zwingend: der Berater darf nach
  AD-013 zwei Kopien eines Rolls vorschlagen — der Planner frisst diesen Vorschlag beim
  naechsten Restore. QA-025 ebenfalls, weil "Custom relic" der Ausweg ist, den der Nutzer
  bei der QA-002-Entscheidung zugesagt bekommen hat; ein Ausweg, der einen Klick auf den
  Deep-Schalter nicht ueberlebt, ist keiner.
- **Die Aufloesung einer Doppelung wird NICHT mehr in den Speicher zurueckgeschrieben.**
  Offene Frage 1 aus T-014, entschieden: Der gespeicherte Build bleibt unangetastet, bis
  der Spieler selbst etwas aendert. Begruendung: sonst ist der Vorgang unumkehrbar und
  nach dem naechsten Klick unbelegt (QA-022). Erscheint der Hinweis bei jedem Restore
  erneut, ist das kein Fehler, sondern die ehrliche Anzeige eines Zustands, den nur der
  Spieler aufloesen kann.
- **"Custom relic" soll ueber Sitzungen und Gefaesswechsel bestehen.** Offene Frage 2 aus
  T-014, entschieden: nicht sitzungslokal machen. Der Nutzer hat freies Planen ueber
  diesen Weg zugesagt bekommen; heute wird das Relikt gespeichert und kann nie
  wiederhergestellt werden — dieser Widerspruch wird zugunsten der Persistenz aufgeloest.
- **QA-023 und QA-026 zurueckgestellt**, dokumentiert. Beim Waechter genuegt vorerst, die
  Grenze im Docstring zu benennen — statische Pruefung kann Laufzeit-Umbindung nicht
  fangen, und das ehrlich hinzuschreiben ist mehr wert als der Anschein von Vollstaendigkeit.

## Die Kernfrage von T-007: wurde bei der Extraktion doch etwas veraendert?

**Nein — und das ist unabhaengig vom Golden-Test belegt.** Vier Beweisgaenge:

1. **Textueller Abgleich** der alten Funktion (`99fe958:nrplanner/app.py:2451-2640`)
   gegen die heutige: die Formatierungshaelfte ist **byteweise identisch**, die
   Arithmetik woertlich uebernommen. Die alten Klassenkonstanten sind aus
   `app.py` entfernt — es gibt keine zweite Kopie, die driften koennte.
2. **10 000 Differentialfaelle** gegen eine woertlich transkribierte Kopie der
   alten Fassung: 10 Nightfarer x 1793 Waffen x 0–12 Effekte x 6 Level x
   6 Tiers x 6 Slots, 2500 davon mit erzwungener Startwaffe, 1109 mehrtypige
   Waffen im Pool. **0 Abweichungen** ueber drei Zufallssaaten. Alle fuenf
   Schadenstypen, alle drei Waffenklassen.
3. **Der Golden-Test ist wirklich vom alten Stand.** Der Baum `99fe958` wurde
   ausgepackt und die *heutigen* Tests darueber gefahren: alle 18 Panel-Faelle
   sind dort **gruen**.
4. **Mutationstest:** sechs gezielte Mutationen in `damage.py` — alle sechs vom
   Golden-Test gefangen (2 bis 34 Fehlschlaege je Mutation).

Die Behauptung des `developer` haelt der unabhaengigen Gegenprobe stand.

## Sind QA-001 und QA-002 geschlossen?

**QA-001 — ja.** Gegen das echte Save mit Fluch-Build liefern beide Tabs
identische Attribute, HP 240, und es ist **buchstaeblich dasselbe Objekt**,
nicht nur derselbe Wert. Die Divergenz 5/180 gegen 8/240 ist weg. QA-011 ist
damit miterledigt. Einschraenkung: der Waechter, der das offenhalten soll,
traegt nur bedingt (QA-017).

**QA-002 — nein, teilweise.** Die Regel greift interaktiv sauber (belegtes
Exemplar verschwindet aus den Nachbarslots, zwei Kopien derselben Rolle bleiben
beide legbar, "Custom relic" passt weiter mehrfach). Aber der Doppelzustand ist
ueber gespeicherte Builds weiter herstellbar (QA-015, gemessen Endurance 5 statt
4), und **der Fix hat zwei Wege eroeffnet, auf denen Relikte still
verschwinden** (QA-013, QA-014) — beide persistiert.

## Entscheidungen des Directors (2026-09-01)

- **Zyklus 2 wird nicht abgenommen.** QA-013 und QA-014 wiegen schwerer als der
  Befund, den sie ersetzen: QA-002 zaehlte etwas doppelt, diese beiden
  **loeschen** Relikte aus gespeicherten Builds — stumm, dauerhaft, auf
  alltaeglichen Pfaden. Fix vor allem Weiteren.
- **QA-015: beim Wiederherstellen aufloesen und es sagen.** Der heutige dritte
  Weg — erst falsch rechnen, dann stumm loeschen und speichern — ist nicht
  tragbar. Der Wortlaut kommt aus `DESIGN_REVIEW.md` DR-002.
- **QA-016: Picker und Berater bekommen dieselbe Identitaetsregel.** Zwei
  Antworten auf eine Frage sind genau die Fehlerklasse, wegen der QA-001
  aufgemacht wurde. Die widerlegte Praemisse wird in `copy_key`, im Commit-Text
  und in AD-013 Punkt 4 an der Messung korrigiert — die AD-Korrektur macht der
  `architect`, nicht der `developer`.
- **QA-018: die Tabs ranken ueber `damage.attack_rating`.** Begruendung: Die
  Tabelle ist die Liste, aus der der Spieler waehlt; sie muss dieselbe Zahl
  nennen wie die Detailtafel derselben Waffe. Genau das war die Beschwerde in
  QA-001. **Fallback**, falls das ueber 1793 Waffen messbar zu langsam wird:
  Spalte umbenennen, sodass sichtbar ist, dass sie ohne Angriffsmultiplikatoren
  rechnet — dann aber mit gemessener Zahl als Begruendung, nicht als Vermutung.
- **QA-017 vor dem Bau des Beraters.** Der Waechter ist eine Textsuche ueber ein
  nicht-rekursives Glob und wuerde das Berater-Paket gar nicht sehen. Er
  schuetzt heute korrekt, weil niemand ausweicht — nicht weil er Ausweichen
  erkennt.
- **QA-005 auf "teilweise behoben".** Der Sockel steht und misst nachweislich
  etwas (Mutationstest). Was fehlt: **keiner der 60 Tests fasst eine
  Wiederherstellung an** — und genau dort liegen beide neuen P1.

## Offene Frage an den `architect`

`damage.attack_rating` multipliziert `physicsAttackRate` flach auf, auch bei
Effekten wie "Improved Thrusting Counterattack", die nur eine **Angriffsart**
betreffen. Der Code begruendet das ausdruecklich ("a buff merely *gated* on a
weapon type is not restricted at all"). Kein Bug — aber war die Begruendung auch
fuer Angriffs*arten* gedacht oder nur fuer Waffentypen? **Der Berater wird
darauf optimieren.**

## Was in T-007 gehalten hat

- "Load equipped" gegen das echte Save, **alle 10 Nightfarer**, Slot fuer Slot
  handle-gleich: 0 Abweichungen. Der Besitz-Filter stoert den Import nicht.
- Nightfarer-Wechsel hin und zurueck: Slots und Speicher identisch vor und nach
  T-006 (A/B gefahren).
- `copy_key` auf beiden echten Saves **durchgaengig eindeutig** (309/309 und
  234/234), keine doppelten Handles, keine doppelten Offsets.
- `damage.py` ist Qt-frei — importiert ohne PySide6. AD-005 erfuellt.
- QSettings-Umleitung haelt: 0 Schluessel im Teststore, echter Store unberuehrt.

## Nachmessung OF-7 (2026-09-01, Save 76561198179244962)

- Vier Farbklassen: Red 75 / Blue 83 / Yellow 81 / Green 70 (309 Relikte).
  Weiss ist **keine Relikt-Farbe**, sondern eine Eigenschaft des *Slots*.
- 101 von 309 sind Deep (32,7 %). Normal und Deep sind disjunkt.
- **Rollen-Dedup bringt fast nichts:** 309 Exemplare, 306 verschiedene Rollen,
  drei Kollisionen. Ein Picker-Eintrag steht in 99 % der Faelle fuer genau ein
  physisches Relikt — deshalb war das Doppelzaehlen die Regel, nicht die Ausnahme.
- Kostentreiber sind **weisse Slots**: 205 Kandidaten normal statt 49–54.
  20 von 74 Kelchen haben mindestens einen.

## Nicht getestet

- SEC-001..011 (eigener Zyklus), der Build-Berater (existiert nicht), das
  gebaute Artefakt (GOAL A9, Release-Zyklus).
- **Zahlenrichtigkeit gegen das laufende Spiel.** Geprueft wurde alt gegen neu,
  nicht gegen die Anzeige im Spiel. Nur der Nutzer kann das schliessen.
- **Nebenlaeufigkeit auf echten Widgets.** Alle Interaktionen liefen headless
  ueber die Modell-API, nicht ueber Mausereignisse. Doppelklick und Abbruch
  mitten im Restore sind nicht abgedeckt.
- `Rescan save` waehrend eines Spielspeichervorgangs (QA-010), Performance.


## T-015: Ursache tiefer gelegt als beauftragt (2026-09-02)

Der Auftrag nannte zwei Richtungen fuer QA-021. Der `developer` hat stattdessen
`select_saved` **ersatzlos entfernt** und durch `Planner._restore_slot_keys`
ersetzt, das in **zwei Durchgaengen ueber den ganzen Build** arbeitet: erst
Handles und Custom relics, dann Rollen. `available_items()` bleibt rollgenau —
das ist die Anzeige —, aber der Restore greift daran vorbei
(`select_copy` sucht notfalls unter allen besessenen Exemplaren des Slots,
`select_roll` ueberspringt, was ein anderer Slot schon per Handle bekam).

Damit ist auch die offene Frage zur vierten `select_saved`-Aufrufstelle
beantwortet: **Rest, nicht Absicht.** Das `False` blieb ungelesen, folgenlos
ausschliesslich durch die Reihenfolge zweier Zeilen darueber. Alle drei
Restore-Pfade gehen jetzt durch dieselbe Funktion, die selbst leert. Sie gibt
**nichts** zurueck — drei Aufrufer mussten dieselbe Konsequenz ziehen, einer tat
es nicht; die Regel wird jetzt dort ausgefuehrt, wo sie entschieden wird, statt
als Antwort verteilt zu werden.

Nachweis: 8 neue Tests, alle vorher rot (alter Baum ausgepackt, nur die neuen
Testdateien darueberkopiert: 8 failed, 7 passed). 70 → 78 Tests.
QA-021 gegen ein **echtes** Paar geprueft (`The Will of Balance`,
Handles 3229614315/3229615265).

### Entscheidungen des Directors dazu
- **QA-028: das Custom relic wird beim Restore verworfen, wenn der Build es nicht
  nennt.** Ein Angebot im Picker eines Nightfarers, das zum Build eines anderen
  gehoert, ist irrefuehrend, auch wenn nichts getragen wird.
- **QA-027 wird behoben**, weil es die Ursache dafuer ist, dass "Load equipped"
  den Grund "nicht mehr im Besitz" gar nicht melden **kann** — der `developer`
  hat den Wortlaut deshalb zu Recht auf den einzigen belegbaren Grund beschraenkt.
- **Nebenwirkung der Speicher-Sperre, bewusst akzeptiert:** solange eine
  Doppelung unaufgeloest ist, wird kein Build geschrieben — auch keiner, der
  durch Gefaess- oder Deep-Wechsel entstuende. Die Ansicht wird weiter
  gespeichert. Das ist der Preis dafuer, dass die Aufloesung umkehrbar bleibt.

| QA-030 | Doppelung in einem ausgeblendeten Deep-Slot: die Aufloesung wird bei jeder unbeteiligten Relikt-Bewegung festgeschrieben, der Hinweis war nie sichtbar | P3 | Major | developer | echte Daten + synthetisches Deep-Paar | offen (neu aus T-016) | 2026-09-02 |
| QA-031 | "Load equipped" nennt den Grund zweimal, wenn nichts platziert werden konnte | P4 | Trivial | ui-ux-designer | echte Daten | offen (neu aus T-016) | 2026-09-02 |
| QA-032 | Beschaedigtes Save wird still uebersprungen; ist es das einzige, meldet das Programm "No save file found." | P2 | Major | developer, ui-ux-designer | echtes praepariertes Save, beide Faelle | offen (neu aus T-017-Retest) - **Director-Entscheid 2026-09-02: Lesart B, der Spieler soll es erfahren** | 2026-09-02 |
| QA-033 | Migration zerstoert Alt-Builds, deren Name mit einem anderen Build-Namen plus Schraegstrich beginnt - `settings.remove(X)` loescht in Qt auch die Untergruppe `X/Y` | P1 | Critical | developer | 5 Namensmuster, deterministisch, beide Einfuegereihenfolgen | **behoben** - eigene Reproduktion des qa-engineer gruen (5 Muster + 8 Kettenvarianten). Restluecke: die zweite Schutzmassnahme ist untestet -> QA-042 | 2026-09-02 |
| QA-034 | Alt-Build mit senkrechtem Strich im Namen verliert den Versteckt-Status und hinterlaesst zwei unloeschbare Phantomnamen in `__hidden` | P4 | Minor | developer | synthetischer Altbestand | **behoben** - aufgeloest statt verworfen; Mutation faellt 2 Tests | 2026-09-02 |
| QA-035 | Zu langer Build-Name wird ohne Rueckmeldung nicht gespeichert; `__order` behaelt den toten Schluessel | P3 | Minor | developer, ui-ux-designer | 4 Laengen, Grenze bei 16 383 Schluesselzeichen gemessen | **behoben** - Grenze roh nachgemessen und exakt richtig. Die Restluecke "setValue bestaetigt nichts" schlaegt in der Migration durch -> QA-041 | 2026-09-02 |
| QA-036 | Vollstaendigkeit des Icon-Packs wird nie geprueft; das installierte Pack ist zu 88 Prozent leer und das Programm meldet nichts | P2 | Major | developer | echtes Geraet: 105 von 839 Dateien, `what_is_needed()==[]`, `available==True`, Portraits und Item-Icons `None` | offen (neu, ausserhalb T-017/T-018) - **Director: sperrt das Release, GOAL A9** | 2026-09-02 |
| QA-037 | SEC-002-Waechter in `bnd4`, `dvdbnd` und `tae` sind gefixt, aber von keinem Test bewacht | P3 | Minor | developer | Mutation: Waechter entfernt, 145 passed | offen (neu aus T-018-Retest) | 2026-09-02 |
| QA-038 | `savefile.read`/`decrypt_member` werden von niemandem benutzt; die Entschluesselungsschleife existiert zweimal in `inventory._decrypt_slots` | P4 | Minor | developer | Aufrufzaehlung ueber den vollen Lauf: 0 Aufrufe | offen (neu aus T-018-Retest) | 2026-09-02 |
| QA-039 | `delete_build` raeumt `__hidden` nicht auf: einen versteckten Build loeschen hinterlaesst seinen Namen dauerhaft im Versteckt-Satz. Dieselbe Phantomklasse wie QA-034, aber im **Normalbetrieb** statt in der Migration | P4 | Minor | developer | gemessen: `build_names` leer, `hidden_builds` enthaelt `doomed` | **behoben** - Ghost-Fall gefahren, `__hidden` und `__selected` werden mitgeraeumt | 2026-09-02 |
| QA-040 | `__order` behaelt nach der Migration tote Schluessel fuer Namen mit senkrechtem Strich - gelistet wird korrekt, aber am Ende statt am Platz, und die Leichen bleiben im Speicher. Korrektur zu QA-034: `__order` repariert die **Anzeige**, nicht den Speicher | P4 | Minor | developer | gemessen: `__order` bleibt `a\|b\|plain`, gelistet `['plain', 'a\|b']` | **behoben** - nach der Migration kein Schluessel ohne Build; Neuanlage wird angehaengt | 2026-09-02 |
| QA-041 | `_migrate_keys` entfernt den Alteintrag, ohne dass das Schreiben belegt ist: ein Alt-Build, dessen **Name** unter 16 383 Zeichen liegt, dessen **abgeleiteter Schluessel** aber darueber, wird bei der Migration still und unwiderruflich geloescht. Dieselbe Wurzel wie QA-033 | P2 | Critical | developer | 5 Namenslaengen um die Grenze, deterministisch (16 380 ueberlebt, 16 386 verloren) | **behoben** - 5 Laengen, Mischstore, 5 echte Neustarts, Falsch-Positiv-Fall eigens gebaut | 2026-09-02 |
| QA-042 | Die zweite Schutzmassnahme des QA-033-Fixes (`path not in written`) ist von keinem der 156 Tests bewacht; der Ordnungs-Test kann sie bauartbedingt nicht fangen - er misst, *wann* entfernt wird, nicht *was* entfernt werden darf | P2 | Major | developer | Mutation: Waechter entfernt -> 26 passed, dabei gehen bei `Fire ice` + `Fire%20ice` Builds verloren | **behoben** - eigene Mutation 2 failed (vorher 0); Ketten 2/3/4 in beiden Reihenfolgen | 2026-09-02 |
| QA-043 | Die Suite teilt sich einen maschinenweiten Einstellungs-Store; ein paralleler pytest-Lauf macht sie rot und sieht dabei wie eine Produktregression aus | P4 | Minor | developer | zwei Ausfaelle in `test_relic_restore.py` erzeugt und durch Isolation widerlegt | **behoben** - Prozess-ID im Store-Namen; Kehrseite als QA-047 | 2026-09-02 |
| QA-044 | Kehrseite des QA-041-Fixes: ein Alt-Build mit zu langem abgeleitetem Schluessel wird jetzt nicht mehr geloescht, aber ueber `childKeys()` am Listenende gelistet - er laedt leer und laesst sich nicht loeschen, weil `load_build` und `delete_build` beide den abgeleiteten Schluessel benutzen. Verstecken geht. Betrifft nur Stores, die so einen Build **vor** `e96a6e0` schon hatten; `save_build` laesst solche Namen seit QA-035 nicht mehr entstehen | P4 | Minor | developer, ui-ux-designer | gemessen mit 1400 Emoji: nach dem Loeschen weiterhin gelistet | offen - in T-021 erneut bestaetigt, **nicht verschlimmert**: Schema-2-Build mit 5 462 Grossbuchstaben bleibt liegen, wird mit richtigem Namen gelistet, laedt leer. Gleicher Mechanismus, groessere Namensmenge betroffen | 2026-09-02 |
| QA-045 | Der Wertvergleich der Ruecklesung in `_migrate_keys` ist von keinem Test bewacht: streicht man nur ihn und laesst `contains()` stehen, bleiben 166 Tests gruen - und ein Build wird still durch den Inhalt eines anderen ersetzt. Dieselbe Form wie QA-042 | P3 | Major | developer | Mutation im Scratchpad-Klon, voller Lauf | **behoben** - `test_an_old_path_that_is_itself_another_builds_key_is_not_removed` (Commit `998ee46`); Mutation streicht den Wertvergleich -> genau dieser Test faellt (vorher 0) | 2026-09-02 |
| QA-046 | Zwei Build-Namen, die sich nur in der Gross-/Kleinschreibung unterscheiden, teilen sich einen Speicherplatz: der zweite ueberschreibt den ersten still, und das Loeschen des einen loescht beide. QSettings-Wertnamen sind auf Windows **case-insensitiv** - `build_key` erhaelt die Schreibweise und ist damit injektiv gegen Python-Strings, **nicht gegen die Registry** | P2 | Critical | developer, director | "Bleed build" + "bleed build": `build_names` zeigt zwei, beide laden denselben Inhalt, Loeschen des einen leert die Liste | **behoben** (Commit `543f69d`, Schema 3) - 47 gegnerische Namen -> 47 Eintraege, 235 276 Namen ohne Kollision, alle 12 faltungsverdaechtigen Nicht-ASCII-Zeichen gegen die Registry geprueft, Migration 1->3 und 2->3, 26 Mutationen / 18 getoetet | 2026-09-02 |
| QA-047 | Kehrseite des QA-043-Fixes: ein abgebrochener Testlauf laesst seinen PID-Store dauerhaft in `HKCU\Software\DankYeeterTests` zurueck, und kein spaeterer Lauf raeumt ihn weg. Vorher gab es genau einen Rest, den der naechste Lauf beseitigte | P4 | Minor | developer | `os._exit(1)` nach einem Speichern, dann `reg query` | offen (neu aus T-020-Retest) - nur Entwicklermaschinen | 2026-09-02 |
| QA-048 | Eine zwischen Markerschreiben und Entfernungen abgebrochene Migration hinterlaesst den Alt-Pfad und damit dauerhaft eine doppelte Zeile in der Liste; der Speicher heilt nicht, weil `__schema` schon auf 3 steht. **Nicht durch `543f69d` erzeugt** - galt unter Schema 2 fuer jeden Namen mit einem Leerzeichen | P3 | Major | developer | echter Hard-Kill unmittelbar nach dem Markerschreiben, Nachschau aus frischem Prozess | offen (neu aus T-021) - **gehoert mit der zurueckgestellten Nebenlaeufigkeit zusammen entschieden, es ist dasselbe Fenster** | 2026-09-02 |
| QA-049 | `app.py:1175` und `:1179` bauen `QSettings` aus Literalen und umgehen damit die Umlenkung ueber `NIGHTREIGN_SETTINGS_ORG`/`_APP`: **die Testsuite liest ueber `restore_variant()` den echten Nutzerspeicher**, ein Variantenklick im Test wuerde hineinschreiben. Der Schluessel selbst ist klassensicher, der Speicher nicht | P3 | Major | developer | `fileName()` beider Speicher unter gesetzter Umlenkung verglichen; einzige zwei Literal-Stellen im Baum | **behoben** (`da42e66`) - Fundstelle vollstaendig; die **Klasse nur teilweise**, siehe QA-052 | 2026-09-02 |
| QA-050 | Die Begruendung fuer die Grossbuchstaben-Hex im `_KEY_SAFE`-Kommentar und in `543f69d` nennt einen Schutz, den sie nicht leistet: mit Kleinbuchstaben-Hex teilen sehr viele Namen den Platz ihres Alt-Pfades, die Migration verliert aber **nichts**, weil der Entfernungswaechter faltet. Die Laengenkette selbst stimmt (0 Gegenbeispiele ueber 200 000 Namen) | P4 | Minor | developer | Kodierung im Klon auf Kleinbuchstaben-Hex umgestellt, Schema-2-Migration mit 7 Namen gefahren | **behoben** (`80244e6`) - Diff mechanisch als reine Kommentaraenderung geprueft | 2026-09-02 |
| QA-051 | Zwei Waechter in `chalices.py` sterben an keiner Mutation: der Order-Filter beim Neuschreiben und die `contains`-Pruefung in `build_names`. **Sie decken einander** - fuer keinen einzeln liess sich eine erreichbare Folge messen | P4 | Minor | developer, director | je einzeln entfernt, 57 Faelle gruen | **behoben** (`57abc84`) - Zustand erreichbar (beide zusammen abgeschwaecht: 4 Ausfaelle), beide Waechter zu Recht behalten | 2026-09-02 |
| QA-052 | Der AST-Waechter aus T-022 prueft **die Schreibweise des Aufrufs, nicht den geoeffneten Speicher**: 10 von 15 store-oeffnenden Formen bleiben ungesehen (Zuweisungs-Alias `S = QSettings`, Subklasse ohne eigenes `__init__`, gleichnamige lokale `ORG`/`APP`-Literale), und die Ausnahmenliste im Docstring nennt nur drei davon. **Ein gleichnamiges Literalpaar wird sogar gruen gemeldet** | P3 | Major | developer | 15 Schreibweisen gegen den Scanner gemessen | offen (neu aus T-022) - heute folgenlos, keine dieser Formen steht im Baum | 2026-09-02 |
| QA-053 | Derselbe Waechter meldet zwei **korrekte** Schreibweisen rot: `favourites` unter Alias importiert, und die von PySide6 unterstuetzte Drei-Argument-Form mit `parent` | P4 | Minor | developer | beide Formen gemessen, Parent-Form gegen den Testspeicher verifiziert | offen (neu aus T-022) - die Sorte Rot, die jemanden dazu bringt, den Waechter zu lockern statt seinen Code zu aendern | 2026-09-02 |
| QA-054 | Verlorener Migrations-Schreibvorgang **plus Schraegstrich im Namen**: der Build wird **null** mal gelistet - der Alt-Pfad ist eine Gruppe, `childKeys()` ist dafuer blind, die Order-Liste raeumt ihn aus - und ist wegen `__schema`=3 dauerhaft unerreichbar. Die Daten stehen weiter in der Registry. Mechanisch dasselbe wie QA-044, **umgekehrte Sichtbarkeit** | P3 | Major | developer | Probe im Klon, mit zwei Kontrollen: ohne Schraegstrich einmal gelistet, ohne Schreibverlust korrekt gelistet | offen (neu aus T-022, **nicht neu im Code**) | 2026-09-02 |
| QA-055 | **Achse B, der wahrscheinlichste Alltagsfall:** Slot auf Tier 3, Tab-Spinbox auf 1, **kein einziges Relikt** - Kachel und Tafel sagen 321,4, der Waffen-Tab 203,4. Reiner Eingabeunterschied, greift ohne jeden Buff, sobald der Spieler ein Slot-Tier hochsetzt. Das Tier, an dem die Liste rechnet, ist nirgends sichtbar | P2 | Major | developer, ui-ux-designer | gemessen ueber die echten Widgets | **teilweise behoben** (W4) - das Ziel-Tier ist jetzt **Pflichtargument** und mutationsbelegt bewacht (Pruefpunkt 20). **Die zweite Haelfte steht unveraendert: das Tier ist nirgends sichtbar** - auf dem Schirm steht nur "+1", der Spieler sieht 203 neben 321 ohne Erklaerung. Das ist AK-33/AK-34, eigener Auftrag. **Director-Entscheid: nicht auf "behoben" setzen** - sonst verdeckt es genau die Haelfte, die den Spieler trifft | 2026-09-03 |
| QA-056 | **Achse C:** mit "Strength +1" zeigt die Kachel 323 (erhoehte Attribute), die linke Zahl der Tafel 321,4 (Grundattribute), der Tab 204,2 - drei Zahlen fuer dieselbe Waffe. Das ist die Beobachtung aus `DESIGN_REVIEW.md:429`, jetzt mit Ursache | P3 | Major | developer, ui-ux-designer | gemessen | **behoben** (W3, `125dc1f`) - unabhaengig nachgemessen: vorher weichen **12 903 von 25 102** Planner-Faellen zwischen Kachel und Tafel ab, nachher **0 von 25 102**, ueber alle 1793 Waffen, 4 Nightfarer, Tiers 1-4, bis zu 6 gefuellte Kacheln, Deep-Fluechte und deklarierte Konditionale. Rot-vorher-Beleg vorhanden | 2026-09-03 |
| QA-057 | `nrplanner/weaponstab.py` ist **toter Code** - von keiner Datei importiert, `app.py:1342` bindet `ArsenalTab` an `self.weapons_tab`. 140 Zeilen, die dieselbe Rangliste ein zweites Mal rendern, **und sie sind bereits gedriftet**: Spinbox `setRange(0, 25)` gegen die Tier-Semantik 1..4; bei 0 rechnet sie still wie 1, bei 5-25 wie 4 | P3 | Minor | developer | kein Importeur im Baum | **behoben** - W0, Datei geloescht (Commit `b53a7b4`), Totsein belegt statt behauptet | 2026-09-02 |
| QA-058 | Der `compute`-Waechter deckt `model.compute` ab, **nicht** `weapons.rate`. Die Waffen-Arithmetik hat zwei Schichten, und vier Anzeigestellen waehlen ihre Eingaben (Attributsatz, Tier, Multiplikatorschicht) unabhaengig. Zusaetzlich ist die Formel je Schadensart viermal ausgeschrieben (`damage.py:140`, `weaponstab.py:107`, `arsenaltab.py:368`, `app.py:2900`) | P3 | Major | developer, architect | Aufruferanalyse; drei unabhaengig gemessene Abweichungsachsen | **teilweise behoben** - W0, W1, **W1b und W2 unabhaengig abgenommen**. Bitgleichheit gegengeprueft: **1 032 768 Datensaetze** ueber zwei Strecken und drei Staende, byte-identisch; Oberflaeche 1654 Zeilen byte-identisch; Vergleicher mit 12 Mutationen geschaerft. Waechter und QA-018/055/056 offen (W3-W6) | 2026-09-02 |
| QA-059 | Die Zeile "vs standard" im Waffen-Tab ist **nicht reproduzierbar sortiert**: `arsenaltab._build_weapons` iteriert `scaling.keys() \| base_scaling.keys()` - eine **Mengenvereinigung**, deren Reihenfolge an der Hash-Saat des Prozesses haengt. Dieselbe Waffe listet ihre Skalierungsunterschiede nach jedem Programmstart anders | P4 | Minor | developer | **5 802 von 11 718 Kacheln** unterscheiden sich zwischen zwei Laeufen **desselben** Codes; verschwindet mit `PYTHONHASHSEED=0` | offen - **unabhaengig bestaetigt** (956 von 1793 Kacheln zwischen zwei Hash-Saaten; mit `PYTHONHASHSEED=0` null). **Klassenfrage geklaert: einziger Fall** - jede Mengenoperation einzeln bis zum Anzeigetext verfolgt, 369 Textbloecke unter zwei Saaten ohne Unterschied | 2026-09-02 |
| QA-060 | `WeaponRating.per_type()` (Methode) und `AttackRating.per_type` (Feld) tragen im selben Rechenweg denselben Namen; in `app.py:2892`/`:2900` stehen beide Formen acht Zeilen auseinander. Kein aktiver Fehler - beide Verwechslungen werfen heute; die **stille** Form waere `if x.per_type:`, die auf einem `WeaponRating` immer wahr ist | P4 | Minor | developer, architect | statisch, beide Aufrufformen probiert | **behoben** - W1b (`e489c1a`), Schichtpraefix umgesetzt, vierte Kollision mit erledigt, vierter Leser in `7eb3126` nachgezogen | 2026-09-02 |
| QA-061 | **Keine Waffe des Datensatzes hat je eine unerfuellte Anforderung.** 1791 von 1793 tragen ein `requires` aus lauter Nullen, die zwei uebrigen verlangen Arcane 1 - jeder Nightfarer hat auf Level 1 mindestens 10. Folge: `require_usable=True` filtert **1793 zu 1793** in allen Level/Tier-Kombinationen, die Checkbox "Meets requirements" ist wirkungslos, Kachel-Dimmen und "requirements unmet" erscheinen nie, und `weapons.rate`s Zweig `if stat in result.unmet: continue` ist auf echten Daten **unerreichbar**. Erweitert QA-019 um Bedienelement und Rechenzweig | P3 | Major | Nutzer (Absichtsfrage), dann developer | echte Daten, 1793 Waffen x 4 Tiers x 14 Attributsaetze | **BEHOBEN** (P1, T-034) - Nutzerentscheid: Anforderung ist nur das Charakterlevel. Checkbox, Dimmen, Requires-Zeile und unerreichbarer Zweig entfernt. Skalierung unangetastet. Bitgleich: 14 344 Datensaetze, 0 Abweichungen | 2026-09-03 |
| QA-062 | Der Docstring von `per_type()` verspricht "nur Typen mit Grundschaden"; der Code filtert auf **Summe ungleich Null**. Auf den heutigen Daten faellt beides zusammen (0 von 100 408 Bewertungen weichen ab), weil `rate()` `base` und `scaled` in einer Schleife fuellt. Ein handgebautes `WeaponRating` mit `scaled`-Schluessel ohne `base` liefert den Typ sehr wohl | P4 | Minor | developer, architect | synthetisch reproduziert, Datenbedingung ueber den ganzen Datensatz gemessen | **behoben** - W1b, Docstring auf das geschrieben was der Code tut, Filter unangetastet. Nachgemessen: Filter auf `base` statt Summe aendert **0 von 516 384** Datensaetzen. **Der Fall bleibt ungebunden** - wandert als Beleg in QA-063 | 2026-09-02 |
| QA-063 | Die neue Testdatei benennt sechs Eigenschaften und bindet vier: **Z1 ueber ein zusaetzliches Feld gebrochen und der Krit-Ausschluss eingerechnet lassen beide alle 232 Tests gruen.** Der Z1-Fall prueft zwei Feldnamen, die Zusicherung lautet aber "kein Total von aussen" - der Abstand dazwischen ist ein Feld mit **anderem Namen**. Fuenfte Instanz derselben Klasse wie QA-046/050/052/062 | P3 | Major | developer | 16 Mutationen gegen die volle Suite; 11 gefangen, 5 ueberlebt | **behoben** (W2b, `59562be`) - Feldmenge von `Rating` vollstaendig festgenagelt statt zwei Namen auszuschliessen; neuer Fall bindet den Krit-Ausschluss. Beide mutationsbelegt | 2026-09-02 |
| QA-064 | Drei neue Zusicherungen in `damage.py` nennen ihren Geltungsbereich nicht, plus eine, die ganz fehlt: **(a)** `rank_candidates` sagt "die Reihenfolge, die der Waffen-Tab immer gezeigt hat" - **der Tab verwirft sie** (Mutation "rank sortiert aufsteigend" aendert 0 von 1654 Oberflaechenzeilen); **(b)** `scaled_total` nennt `_accumulated` "die einzige weitere Summe", `final_total` ist eine dritte; **(c)** `tier_applied` "always max(own, requested)" - bei Anfrage 5/6 ist es 4; **(d)** `weapons.rate`s `bonus`-Schleife ist die **zweite und groessere** Stelle der sum-Klasse (48 100 von 258 192 Karten) und traegt keinen Hinweis | P3 | Minor | developer, architect | 1654 UI-Zeilen, 12 551 Tier-Kombinationen, 516 384 Differentialsaetze | **behoben** (W2b) - (a) korrigiert: die Reihenfolge ist die von `weapons.rank`, **der Tab verwirft sie**; (b) und (c) mit Geltungsbereich; (d) Kommentar an der `bonus`-Schleife. **Rest: QA-069** | 2026-09-02 |
| QA-065 | `test_ranking_answers_the_candidate_question_for_every_armament` behauptet exakte absteigende Sortierung von `final_total`, waehrend `weapons.rank` nach `WeaponRating.total` sortiert - zwei Klammerungen, die fuer rund 9 Prozent des Datensatzes um 1 ULP auseinandergehen. **Auf erreichbaren Eingaben bereits verletzt:** Wylder Lvl 1, Tier 4, Position 319/320 | P3 | Minor | developer | echte Daten, 10 Helden x 4 Level x 4 Tiers | **behoben** (W2b) - Assertion auf `weapon_rating.total` umgestellt, also auf das, was `rank` wirklich zusichert. Der `developer` hat den Fall 319/320 **selbst nachgemessen** statt ihn zu uebernehmen | 2026-09-02 |
| QA-066 | `damage.Rating` ist `frozen`, aber **nicht hashbar** (dict-Felder) - kein set, kein dict-Schluessel, kein `lru_cache`. Zusaetzlich nur flach unveraenderlich: die Typkarten sind veraenderbar und werden als dasselbe Objekt weitergereicht. **Trifft AD-018, sobald der Berater Grenzbeitraege memoisiert** | P4 | Minor | developer | acht Angriffe auf Z1, alle protokolliert | offen - fuer W6 vormerken | 2026-09-02 |
| QA-067 | Waffen-Tab: die AR-Zeile einer Kachel ist **nicht die Summe der Typzeilen darunter** - 556 von 3586 Kacheln mit mindestens zwei Schadensarten (15,5 Prozent), z. B. "AR 164" ueber "Physical 84 / Magic 81". Jede Zahl wird einzeln gerundet. **Vorbestand, keine Regression** | P4 | Trivial | ui-ux-designer | am laufenden Programm fotografiert, Reichweite ueber den ganzen Datensatz gemessen | offen - ein Spieler, der nachrechnet, findet einen Fehler, der keiner ist | 2026-09-02 |
| QA-068 | `weapons.rate` schuetzt die Tier-Obergrenze **doppelt**: einmal durch `min(upgrade, MAX_UPGRADE)`, einmal dadurch, dass die Reinforce-Tabelle fuer keine Waffe einen Eintrag darueber hinaus hat. Den Clamp **allein** zu entfernen aendert **0** Ergebnisse - erst zusammen mit der Ruecksuche wird der Test rot. **Ein kuenftiger Aufraeum-Commit, der den Clamp fuer redundant haelt, verlaesst sich danach allein auf die Datenform** | P4 | Minor | developer, architect | Mutationsprobe in W2b: Clamp allein entfernt -> 0 Aenderungen ueber 1793 Waffen x Anfragen 5/6/100 | **behoben** (W3) - Kommentar unabhaengig gegengeprueft: Clamp allein entfernt laesst 237 von 237 Tests gruen. Die Aussage stimmt, und der Kommentar ist noetig | 2026-09-03 |
| QA-069 | **In W2b sind zwei Zahlen in Code-Kommentare gewandert, die der `developer` nicht selbst gemessen hat** (48 100 von 258 192 Karten; 0 von 1654 Oberflaechenzeilen). Er hat es ausdruecklich gemeldet: Groessenordnung und Richtung sind strukturell sicher, die exakten Werte stammen aus dem QA-Bericht. Sein eigener Gegenlauf kam auf eine andere Grundgesamtheit (1432 von 23 344) | P4 | Minor | developer | Selbstmeldung, im Bericht offengelegt | **behoben** (W3) - gegengeprueft: keine der beiden nicht selbst gemessenen Zahlen steht noch irgendwo unter `nrplanner/` | 2026-09-03 |
| QA-070 | **Die Golden-Datei hat die Waffenkachel nie erfasst** - `weapon_damage_cases.run` nimmt Tafeltext und `last_ar`, von den sechs Kacheln nichts. **Das ist die Ursache dafuer, dass QA-056 so lange stehen konnte:** der Waechter, der die Zahlen einfriert, sah die Stelle nicht, an der sie auseinanderliefen. Klasse "Waechter mit unausgesprochener Reichweite", dieselbe wie QA-064 | P3 | Major | developer | in W3 gefunden und im Docstring benannt; Kachel jetzt durch das **Paar** Golden + Pruefpunkt 19 gedeckt - einzeln deckt keiner von beiden sie | **teilweise behoben** (W3) - fuer die **aktive** Kachel geschlossen und in **beiden** Richtungen mutationsbelegt (Golden allein blind, Pruefpunkt 19 allein blind). Die fuenf nicht-aktiven Kacheln und die Klick-Aufschluesselung bleiben ungedeckt -> **QA-073**. Director-Entscheid: die Zeile bleibt teilweise, damit ein "behoben" den schwereren Rest nicht verdeckt | 2026-09-03 |
| QA-071 | `damage.attack_rating`/`AttackRating` hat nach W3 **keinen Produktionsleser mehr** - Leser sind nur noch `tests/test_marginal_returns.py` (AD-018-Hauptweg) und die fensterlose Haelfte des Golden-Tests. Bewusst stehen gelassen: AD-019 laesst "bleibt oder geht in `Rating` auf" offen, und Loeschen haette einen AD-018-Test und den Golden-Test umgebaut | P4 | Minor | developer, architect | Aufruferanalyse in W3 | **ENTSCHIEDEN** (T-036) - attack_rating/AttackRating bleibt als bewusst gehaltene zweite Schnittstelle (bare Bewertung ohne Slot/Held), kein Merge in Rating. Begruendet in damage.py Docstring | 2026-09-03 |
| QA-072 | `arsenaltab.py:367` benutzt `damage` als **Schleifenvariable** und verdeckt damit das Modul gleichen Namens. In W3 hat genau das eine Testrunde gekostet (`UnboundLocalError`, der erst beim Zeichnen zuschlaegt, nicht beim Import). **W4 wird dieselbe Falle treffen**, sobald dort `from . import damage` steht | P4 | Minor | developer | in W3 am eigenen Leib erlebt und gemeldet | **behoben** (W4) - Schleifenvariable heisst `damage_type`. Der `developer` ist beim Bauen in eine **Variante** derselben Falle gelaufen (Hilfsfunktion unter ihrem Aufrufer definiert) und hat sie vor dem ersten Testlauf gefangen | 2026-09-03 |
| QA-073 | **Zwei Anzeigestellen der Waffenrechnung sind von keinem Waechter erfasst**, dieselbe Klasse wie QA-070: **(a) die fuenf nicht-aktiven Kacheln** - Pruefpunkt 19 macht jede Kachel nacheinander aktiv und prueft sie nur in diesem Zustand; **kein Test sieht je eine Kachel, waehrend eine andere aktiv ist.** Mutation "nur die aktive Kachel bekommt den fertigen Wert" aendert **36 958 Kachelziffern in 12 551 von 25 102 Faellen (50,0 Prozent)** und laesst **237 von 237 Tests gruen**. **(b) die Klick-Aufschluesselung** `_show_ar_breakdown` - die Golden-Datei friert `last_ar` ein, also ihre **Eingabe**, nie ihre Ausgabe; Mutation "base und scaled vertauscht" laesst ebenfalls 237 gruen | P2 | Major | developer | zwei ueberlebende Mutationen gegen die volle Suite, Reichweite ueber 25 102 Planner-Faelle gemessen | **behoben** (W3b) - unabhaengig nachgefahren: beide Mutationen rot. Der Invariantentest fordert **nichts Falsches**: die Unabhaengigkeit der Kachelzahl vom aktiven Slot ist **strukturell** und ueber 120 Gitter mit 0 Abweichungen gemessen. Rest in anderer Form -> QA-076/QA-077 | 2026-09-03 |
| QA-074 | **Die zweite Haelfte der W3-Bikonditionale ist rasterabhaengig, nicht programmeigen.** "Keine Kachel mit einem Multiplikator blieb stehen" wird an **gerundetem Anzeigetext** gemessen. Mit dem kleinsten Multiplikator des Datensatzes (x1,007) bleiben **68 Kacheln auf 68 verschiedenen Waffen** stehen, obwohl er wirkt - 129,559 gegen 130,466, beide Male "130". **Kein Programmfehler**, Kachel und Tafel stimmen ueberein. Die **schaerfere** Haelfte (keine Kachel bewegte sich ohne Multiplikator) ist ueber 25 102 Faelle bestaetigt | P4 | Minor | developer | 1793 Waffen x 14 Konfigurationen, Gegenbeispiele einzeln nachgerechnet | **behoben** (W3b) - die Charakterisierung ist ungerundet **und** gerundet gefuehrt | 2026-09-03 |
| QA-075 | **Die Differentialstrecke, die die Abnahmezahlen von W0 bis W3 erzeugt hat, liegt nicht im Repo.** `scripts/` enthaelt nur `capture_weapon_damage.py`; die Zahlen sind nur durch **Neubau** einer Strecke pruefbar - in dieser Abnahme geschehen, alle Klassen bestaetigt. Verstoesst gegen die eigene Regel "ein Messwert traegt sein Rezept". **Trifft W4, W5 und W6 gleichermassen**, und die Fallzahlen zweier Schritte sind ohne die Raster nicht vergleichbar ("10 276 von 19 392" gegen "38 787 von 25 102") | P3 | Minor | director, developer | Aufruferanalyse plus unabhaengiger Nachbau der ganzen Strecke | **behoben** (W3b) - Strecke im Repo, Raster als Datei. Die Eigenpruefung der Strecke ergab drei Schwaechen -> QA-079, eine Doku-Abweichung -> QA-080 | 2026-09-03 |
| QA-076 | **Die Verdrahtung `recompute` -> `last_sources` ist von nichts gehalten.** `self.last_sources = {}` laesst **259 von 259** gruen, waehrend in der laufenden Anwendung jede Klick-Aufschluesselung ihre Quellzeilen verliert. Ursache: `weapon_damage_cases.run` **setzt** diesen Zustand selbst, statt ihn ausloesen zu lassen - die neue Golden-Spalte friert damit die **Formatierung** ein, nicht die **Verdrahtung**. Dieselbe Klasse wie QA-073(b), eine Ebene hoeher, und **durch die W3b-Harness-Entscheidung neu entstanden** | P2 | Major | developer | ueberlebende Mutation gegen die volle Suite | **behoben** (W3c) - Harness-Zuweisung bleibt (Begruendung richtig), Docstring benennt die Luecke, und `test_recompute_wires_last_sources_and_last_rates_from_its_own_build` ruft `recompute()` **real** auf. Mutation `last-sources-not-assigned` toetet ihn | 2026-09-03 |
| QA-077 | **Die Klick-Aufschluesselungen ausserhalb der Waffenrechnung liest kein Test.** `_show_breakdown` baut seinen Text lokal und reicht ihn nur an `QToolTip` - angeschlossen an `rates_label`, `other_label` und die Attribut-Differenzlabels. Mutation `(value-1)*100 -> value*100` laesst **259 gruen**; **34 Tooltips mit 47 Prozentzeilen** allein ueber die 18 Golden-Builds waeren falsch ("+12,4 %" als "+112,4 %"). **Vorbestehend, keine W3b-Regression** - betrifft den ganzen Charakterbogen statt nur der Waffentafel | P2 | Major | developer | ueberlebende Mutation, Reichweite ueber die Golden-Builds gezaehlt | offen - **eigener Auftrag NACH W4**, Director-Entscheid | 2026-09-03 |
| QA-078 | **Welche Kachel den Goldring traegt, prueft kein Test - auch nicht der so benannte.** `active=False` laesst 259 gruen. `show_slot` legt `active` nur ins Stylesheet; die neue Erfassung nimmt Text, nicht Rahmen. Der Ring ist die **einzige** Zuordnung zwischen Tafel und Slot | P3 | Minor | developer | ueberlebende Mutation | offen - zurueckgestellt, dokumentiert | 2026-09-03 |
| QA-079 | **Systemisch: drei Waechter der Messstrecke pruefen schwaecher als ihr Text.** (a) die Hashseed-Verweigerung liest `os.environ`, nicht `sys.flags.hash_randomization` - nach Interpreterstart gesetzt passiert sie, waehrend die Randomisierung weiterlaeuft; (b) `mutate.py` verweigert nur den **eigenen** Checkout - ein zweiter Klon oder `git worktree` wird beschrieben, und das ist der naheliegendere Weg zum alten Baum; (c) fuer `use_tree` gibt es **keinen Nachweisweg im Repo** (wirkt, per Gegenbau belegt) | P3 | Minor | developer | drei Faelle einzeln nachgestellt | **behoben** fuer (a) und (c) - beide per Gegenbau rot bestaetigt. **(b) nur zur Haelfte belegt:** der Code verweigert `.git` als Datei, der Testkoerper prueft nur das Verzeichnis -> QA-087 | 2026-09-03 |
| QA-080 | `compare.py` druckt standardmaessig 20 Datensaetze, das Paket-Docstring nennt "prints those records in full" als **tragende** Eigenschaft. Der Rest wird angekuendigt, nicht verschwiegen | P4 | Trivial | developer | Default gegen Docstring gelesen | **behoben** (W3c) - als Doku geloest: Default 20 bleibt, das Flag steht im Docstring | 2026-09-03 |
| QA-081 | Die Quellzuordnung im Aufschluesselungstext haengt an **genau einem** Golden-Fall. Gedeckt, aber ohne zweiten Waechter - dieselbe Konstellation, die beim aktiven Slot als nicht tragfaehig eingestuft wurde. **Antwort auf die vom `developer` selbst benannte, ungemessene Luecke** | P3 | Minor | developer | Mutation plus Auszaehlung der Golden-Datei | **dokumentiert** (W3c) - der Kommentar benennt, dass genau ein Golden-Fall die klassengebundene Quellzeile deckt. **Keine Fallmengen-Erweiterung** - das waere ein Auftrag, den niemand hat | 2026-09-03 |
| QA-082 | Die Begruendung im Docstring des Invariantentests **trifft den Code nicht**: Gates kommen aus `weapons_held` (alle sechs), die Paarung aus dem **Slot-Index**, Klassenraten aus der Klasse der gerateten Waffe. Der Test selbst ist richtig; die Begruendung haelt die naechste Rolle von einer Zusicherung ab, die **heute belegbar haelt** (0 von 120 Gittern, gerundet und ungerundet) | P4 | Minor | developer | Codeanalyse plus 120 Gitter / 720 Zeichnungen | **behoben** (W3c) - falsche Begruendung ersetzt durch die tatsaechlichen Fundstellen. Die breitere Zusicherung ist als haltend vermerkt | 2026-09-03 |
| QA-083 | **Der Arsenal-Tab war von nichts bewacht - schlimmer als QA-073.** Auf dem Vor-W4-Stand liess **`rating.total * 0.5`, also jede AR-Zahl auf jeder Kachel halbiert, 264 von 264 Tests gruen**; ebenso "die Spinbox bewegt gar nichts mehr". Bewacht wurde ausschliesslich sein **Attributsatz** (`test_one_build.py`, QA-001). Keine Zeile las je eine Zahl vom Tab, keine je das Tier. Klasse "Waechter mit unausgesprochener Reichweite" wie QA-070/073 | P2 | Major | developer | zwei Mutationen gegen die volle Suite auf dem Vor-W4-Baum | **behoben** (W4) bestaetigt - beide registrierten Mutationen toeten den Waechter, und er steht auf der **gerenderten Kachel**, nicht auf `tab.ratings`. **Reichweite eingeschraenkt:** er haelt genau die AR-Zeile von vier Armaturen -> QA-086 | 2026-09-03 |
| QA-084 | **Die Summationsreihenfolge steht in keinem AD-020-Punkt**, obwohl der Wechsel von `WeaponRating.total` (`sum(base) + sum(scaled)`) auf `Rating.final_total` (`sum(base[t]+scaled[t])`) sie zwingend mitbringt. W4 hat dadurch **584 von 7172 Datensaetzen** um exakt 1 ULP verschoben - **alle auf mehrtypigen Armaturen, keine einzige einartige**. Der `developer` hat sie **gemeldet statt einsortiert**, wie beauftragt | P3 | Minor | architect | 7172 Datensaetze, groesster Absolutbetrag 5,68e-14, 424 verschiedene Armaturen | **entschieden (AD-024)**, Signatur unabhaengig bestaetigt: 871 von 7172 (Recluse, Level 1, anderes Raster), **alle exakt 1 ULP**, 863 zweitypig, 8 dreitypig, **0 von 2736 einartig**. Der Ausschluss ist **algebraisch, nicht statistisch**: `sum([x])` ist exakt | 2026-09-03 |
| QA-085 | **Systemisch: keine Signalverdrahtung des Arsenal-Tabs ist gehalten.** `upgrade.valueChanged.connect` entfernt -> **275 gruen**, die Spinbox bewegt keine Zahl mehr (AR 154 bleibt 154 statt 211). `tabs.currentChanged.connect(...recalculate)` entfernt -> **275 gruen**, der Tab bleibt auf den Attributen stehen, mit denen er gebaut wurde - **das ist QA-001 woertlich zurueck**. Beide auch fuer die Differentialstrecke unsichtbar (0 von 60), weil jeder Test und die Harness `recalculate()` **selbst** rufen: geprueft wird die Rechnung, nie der Ausloeser | P2 | Major | developer | zwei ueberlebende Mutationen, jede am laufenden Widget als wirksam belegt | **BEHOBEN, unabhaengig bestaetigt** - beide Mutationen toeten genau ihren Fall (294/296). Nebenpruefung an der Laufzeit: rarity_box und Suchdebounce korrekt an rebuild verdrahtet, usable_only existiert nicht mehr. Vollstaendig geschlossen | 2026-09-03 |
| QA-086 | **Der neue Arsenal-Waechter haelt nur die AR-Zeile.** Vier ueberlebende Mutationen, je 275 gruen: (a) Typzeilen verdoppelt ("AR 186" ueber "Physical 168 / Magic 205"); (b) "Upgraded to +4 Legendary" statt "+3 Rare"; (c) `effective_rarity` ohne `-1` - der Rarity-Filter zeigt in **jedem** Band die falschen Waffen (Band 0 bei Tier 1: 856 statt 160); (d) Zauber-FP verdoppelt. `rarity_box` und `usable_only` kommen in **keinem** Test vor, die Golden-Datei enthaelt **null** Arsenal-Bloecke. Klasse "Waechter mit unausgesprochener Reichweite" | P3 | Major | developer | vier Mutationen, Reichweite je am Widget gemessen; (a)(b)(c) faengt die Differentialstrecke, (d) faengt nichts | **BEHOBEN, unabhaengig bestaetigt** - drei neue Mutationen toeten genau ihren Fall. Zahlenkorrektur zu (c): richtig ist 696 gegen 0, nicht "856 statt 160" -> QA-092 | 2026-09-03 |
| QA-087 | Der Worktree-Fall aus QA-079(b) ist **im Code richtig, im Nachweis nicht**: der Test legt `.git` als **Verzeichnis** an, waehrend sein Docstring die `.git`-**Datei** als Grund fuer `.exists()` nennt - `.exists()` -> `.is_dir()` laesst 34 von 34 gruen. Zusaetzlich hat `use_tree` nur die **verweigernde** Richtung: "verweigert jeden Baum" laesst ebenfalls alles gruen. Klasse wie QA-082 | P4 | Minor | developer | fuenf Gegenbauten, zwei ueberlebend | offen | 2026-09-03 |
| QA-088 | **Die Arsenal-Ablesung der Messstrecke kann still das Falsche oder gar nichts messen.** (a) `run` bewegt den Level-Slider nie, also steht in jedem Datensatz eines Level-15-Laufs "at level 1" neben Level-15-Attributen - konstant, erzeugt keine Falschmeldung, **maskiert** aber jede Aenderung der Levelangabe. (b) Eine Konfiguration mit Rarity-Band unter dem Ziel-Tier zeichnet gar keine Kachel (1792 von 1793 leer), zaehlt aber voll mit; `plan.py` warnt nicht | P4 | Minor | developer | eigener Lauf ueber 7172 Datensaetze, Leerstand je Konfiguration ausgezaehlt | offen | 2026-09-03 |
| QA-089 | Der Rarity-Filter des Arsenal-Tabs **filtert die Zauber nicht mit**, und die Zaehlung mischt gefiltert und ungefiltert: "Common" meldet 856, davon **160 Zauber ohne jede Rarity**; bei Tier 4 meldet "Legendary" 1953 - den ganzen Datensatz. **Vorbestand, keine W4-Regression** | P4 | Trivial | ui-ux-designer | an der Zusammenfassung des echten Widgets ueber alle Baender und zwei Tiers abgelesen | offen | 2026-09-03 |

## T-016: die Fixes halten — und zwei meiner Aussagen waren falsch

**QA-021, QA-022, QA-024 und QA-025 sind geschlossen.** Nicht abgenickt: 104 echte
Gefaess-Rundreisen ueber **beide** Saves, der komplette Identitaetsraum (Handle,
Rolle, veraltete Handles, handle-lose Kopien, Deep sichtbar und ausgeblendet),
120 Wiederholungen ohne Listenwachstum, und **22 feindliche gespeicherte
Schluessel** (Unicode, Nullbytes, 6000-stellige Zahlen, 5000 Effekt-IDs) —
0 Abstuerze, jedes Mal ein leerer Slot und ein unbeschaedigter Nachbar.

`_restore_slot_keys` ist trotz seiner zentralen Stellung die stabilste Aenderung
der drei Runden.

**Zwei Korrekturen an meinen eigenen Aussagen:**

1. **Ich hatte QA-026 als "entschaerft" eingetragen.** Falsch. Der Verlust wird
   weiterhin gespeichert — nur einen Klick spaeter, sobald der Spieler
   irgendein anderes Relikt bewegt. Die Sperre haengt am Fenster, nicht am
   betroffenen Relikt. Fuer sichtbare Slots ist das meine Entscheidung woertlich
   umgesetzt; fuer einen ausgeblendeten Deep-Slot faellt ihre **Voraussetzung**
   weg: der Spieler hat den Hinweis nie gesehen, kann also nichts entschieden
   haben. Status zurueckgesetzt, neuer Befund QA-030.
2. **Ich hatte im Auftrag behauptet, das zweite Savefile zwinge `copy_key` auf
   den Offset-Zweig.** Widerlegt: **beide** Saves liefern 100 % Handles
   (309/309 und 234/234); unlesbar ist dort nur die *Loadout-Tabelle*, und das
   ist eine andere Struktur. Der Offset-Zweig ist mit echten Daten auf dieser
   Maschine **gar nicht erreichbar** und wurde synthetisch geprueft — er traegt,
   ist aber unbewacht.

## Entscheidungen des Directors (2026-09-02, nach T-016)

- **QA-030: die Aufloesung in einem verdeckten Slot wird sichtbar gemacht**,
  statt die Sperre pro Relikt zu fuehren. Der Deep-Schalter bekommt eine
  Markierung, und die Statuszeile sagt es. Begruendung: meine Entscheidung war
  "aufloesen und es sagen" — der Fehler liegt im *Sagen*, nicht im Sperren.
- **QA-028: ein Custom relic gehoert dem Build, nicht dem Spieler.** Es wird
  beim Restore verworfen, wenn der einlaufende Build es nicht nennt — und das
  gilt auch fuer den Gefaesswechsel, nicht nur fuer den Nightfarer-Wechsel.
- **Neue Luecke aus der dritten offenen Frage:** Leert der Spieler den
  *genannten* Slot, bleibt der gespeicherte Build doppelt, weil ein komplett
  leerer Slot-Satz nie ueber einen vorhandenen geschrieben wird. Er folgt dem
  Hinweis, und nichts aendert sich. Geht als Teil von QA-030 an den `developer`.
- **Der Bau des Build-Beraters ist freigegeben.** Auflage aus QA-023: das
  Berater-Paket muss unter `nrplanner/` liegen, sonst sieht der
  `compute`-Waechter es nicht.
- **Release bleibt gesperrt** — nicht wegen T-015, sondern wegen QA-003
  (Critical), QA-018, dem ungelaufenen Sicherheitszyklus und GOAL A9.

## Entscheidungen des Directors - Zyklus 3 (2026-09-02)

- **QA-003 ist als Release-Blocker gefallen**, belegt ueber die echte
  Oberflaeche: 15 Namensformen zeichengenau zurueckgelesen, voller
  Lebenszyklus, Neustart, Migration am echten Altbestand ohne Verlust.
  `A/B` und `A%2FB` koexistieren injektiv.
- **SEC-001 ist als Release-Blocker gefallen**, belegt gegen ein echtes
  praepariertes Save: der Vor-Fix-Stand haengt an derselben Datei (nach 20 s
  zwangsbeendet), der heutige meldet sie in 0,01 s, das Fenster ist in 1,8 s
  bedienbar. Zusaetzlich entlarvt: der Vor-Fix-Stand meldete bei
  `file_header_size = 0` glatt "OK 14" - vierzehn Member an derselben Adresse.
- **QA-033 von P3 auf P1 angehoben. Das ist Datenverlust, und er sperrt
  Push und Merge.** Der QA-Engineer ordnet ihn dem naechsten Fixdurchgang zu;
  dem widerspreche ich. Die Migration laeuft beim ersten Start nach dem Update,
  einmal, unwiderruflich, an fremden Daten - und sie ist an dieser Stelle
  schlechter als Nichtstun: vorher war der Build unsichtbar, aber noch da;
  nachher ist er weg und sein Name steht als leerer Eintrag in der Liste. Der
  Spieler klickt seinen Build an und bekommt ein leeres Gefaess, ohne
  Fehlermeldung. Ausloeser ist ein alltaegliches Namensmuster (Fire ice und
  Fire ice/v2). Ein Fix, der Nutzerdaten zerstoert, geht nicht auf einen
  Branch, den jemand mergen koennte.
- **QA-032, Spezifikationsluecke, entschieden: Lesart B - der Spieler soll
  wissen, was mit seinen Dateien ist.** Begruendung: Das Ueberspringen selbst
  ist richtig und bleibt (der Docstring begruendet es). Falsch ist, dass es
  spurlos ist. Genau das Szenario, fuer das SEC-001 Release-Blocker war -
  ein heruntergeladenes oder beschaedigtes Save - endet heute in einer
  Falschaussage ("No save file found", waehrend eine 19,5-MB-Datei gelesen
  wurde). Der Spieler sucht den Fehler dann bei seiner Installation. Drei
  Zustaende sind zu unterscheiden: kein Save gefunden / Save gefunden, keins
  lesbar (mit Grund) / gelesen, N uebersprungen. **QA-004 hat dieselbe
  Wurzel und wird im selben Auftrag mitgenommen.**
- **QA-036 sperrt das Release.** Der Befund liegt ausserhalb von T-017/T-018,
  aber er ist genau der Pfad, den GOAL A9 abdecken soll, und er ist auf dem
  Geraet des Nutzers heute kaputt: 105 von 839 Dateien, alle 713
  Item-Icons und alle 10 Portraits fehlen, `what_is_needed()` sagt leer und
  `available` sagt wahr. Ein Programm, das ohne Relikt-Icons startet und das
  nicht bemerkt, ist auf einem frisch aufgesetzten Rechner ein
  Erststart-Fehler ersten Ranges. Die tragende Massnahme ist Vorschlag (b) des
  Pruefers - in ein temporaeres Verzeichnis bauen und am Ende umbenennen,
  statt das Ziel vorher zu leeren; (a) und (c) sind Absicherung.
- **Trimmen im Dialog bleibt** (Entscheid des `ui-ux-designer`, von mir
  bestaetigt): ein Leerzeichen am Ende ist in der Liste unsichtbar, und
  "Build" neben "Build " waere eine neue Falle. Die Speicherschicht
  speichert trotzdem exakt, was ankommt - ihr Vertrag gilt fuer kuenftige
  Aufrufer. Der fuehrende-Leerzeichen-Fall in `test_build_names.py` prueft
  damit den Schichtvertrag, **nicht** Nutzerverhalten; das gehoert als
  Kommentar an den Test, sonst liest ihn der naechste als Widerspruch.
- **Die Verschaerfung bei `name_offset` hinter dem Puffer ist Absicht**
  (offene Frage 2 des Pruefers). Vorher: stiller Positionsname, Save lesbar.
  Jetzt: Datenfehler. Das ist GOAL A7. Es kann Saves unlesbar machen, die
  vorher gingen - genau deshalb ist QA-032 Bedingung dafuer, dass diese
  Verschaerfung ausgeliefert werden darf. Ohne die Meldung waere die
  Verschaerfung eine Verschlechterung.
- **`test_a_layout_bomb_is_refused_before_it_expands` bleibt, wird aber
  als nicht-tragend gekennzeichnet** (offene Frage 4). Er bleibt auch ohne die
  Entitaetensperre gruen, weil expat die Verstaerkung heute selbst begrenzt -
  er unterscheidet nichts. Loeschen waere falsch (er bewacht expats
  Verhalten), ihn fuer einen Beleg zu halten auch. Kommentar an den Test.
- **QA-005 auf "teilweise behoben" fortgeschrieben.** 145 Tests, davon sind
  12 von 15 Sicherheitsbefunden mutationsbelegt - der Pruefer hat zehn
  eigene Laufzeitmutationen gefahren, nicht die des Entwicklers uebernommen.
  Drei SEC-002-Stellen sind gefixt und unbewacht (QA-037).

## Entscheidungen des Directors - Zyklus 4 (2026-09-02)

- **QA-034 wurde aufgeloest, nicht verworfen - und das ist die bessere
  Loesung.** Ich hatte dem `developer` das Verwerfen von `__hidden` als
  vertretbare Vereinfachung angeboten. Er hat es nicht genommen, mit einem
  Argument, das ich uebernehme: Verwerfen haette den bestehenden Test
  `test_a_hidden_and_selected_build_survive_the_migration` rot gemacht, und
  der haelt einen bestaetigten, korrekten Fall fest. **Ein Test, der eine
  funktionierende Eigenschaft festhaelt, ist kein Hindernis, das man
  wegraeumt - er ist das Argument gegen die grobe Loesung.** Stattdessen wird
  jedes Fragment nur uebernommen, wenn es einen Namen bezeichnet, den es gibt.
- **Zwei Commits statt drei sind in Ordnung.** Der `developer` wollte einen je
  Befund; alle drei sitzen in derselben Funktion und derselben Testdatei, und
  `git add -p` ist in dieser Umgebung nicht verfuegbar. Der Kommentar-Commit
  ist getrennt, die drei Behebungen sind im Body einzeln benannt. Kein
  Rueckbau.
- **Der Fund des `developer` in seiner eigenen Fixrichtung wiegt schwerer als
  der beauftragte Fix.** Ein Altname `Fire%20ice` leitet sich auf
  `Fire%2520ice` ab, waehrend `Fire ice` sich auf `Fire%20ice` ableitet - ohne
  die Bedingung "ein alter Pfad, der selbst einer der eben geschriebenen
  Schluessel ist, wird nicht entfernt" haette das Aufraeumen den gerade
  geretteten Build mitgenommen. **Dieselbe Fehlerklasse, eine Ebene weiter.**
  Der Fall stand in keinem Befund; er ist beim Bauen aufgefallen. Der
  `qa-engineer` prueft ihn nach und sucht nach weiteren Ebenen der Kette.
- **QA-039 und QA-040 aufgenommen**, beide vom `developer` gemessen und
  ausserhalb seines Auftrags gemeldet, beide P4. Sie gehoeren zusammen in
  einen spaeteren Auftrag: es ist zweimal dieselbe Sache - Buchhaltungsfelder
  (`__hidden`, `__order`), die Namen behalten, zu denen es keinen Build mehr
  gibt.
- **QA-035 ist mit einer Laengenpruefung behoben, nicht mit einer
  Erfolgsbestaetigung - bewusst.** `QSettings.setValue` gibt nichts zurueck,
  und `status()` meldet den Fall nicht verlaesslich; ein Schreibfehler aus
  einem anderen Grund (Rechte, volle Hive) bleibt still. Die Luecke zu
  schliessen hiesse, nach jedem `setValue` ein `sync()` und ein `contains()`
  zu fahren - ein Registry-Schreibvorgang pro Speicherung mehr. **Akzeptierte
  Restluecke**, dokumentiert, kein eigener Befund.
- **Windows-Grenze 16 383 akzeptiert.** Auf Linux und macOS legt QSettings
  INI/plist an, dort waere der Waechter zu streng. Das Programm zielt
  ausdruecklich auf Windows (`GOAL.md`, Rahmen; `NightreignHelper.spec`), und
  der Waechter lehnt dort nichts ab, was sonst funktioniert haette.

## Entscheidungen des Directors - Zyklus 4, nach dem Retest (2026-09-02)

- **QA-033 ist gefallen**, aber der Push bleibt gesperrt. Der `qa-engineer` hat
  alle fuenf Tabellenmuster plus acht eigene Kettenvarianten gefahren, in
  beiden Einfuegereihenfolgen und **mit unterscheidbaren Werten je Build**, und
  strukturell belegt, dass es keine weitere Ebene der Prozentkette gibt: ein
  abgeleiteter Schluessel enthaelt nie einen Schraegstrich, liegt also immer
  auf Ebene 1. QA-034 und QA-035 sind belegt behoben; die Grenze 16 383 sitzt
  exakt richtig (roh nachgemessen: 16 383 ja, 16 384 nein).
- **QA-041: die in T-019 akzeptierte Restluecke wird an dieser einen Stelle
  zurueckgenommen.** Ich hatte "`setValue` bestaetigt nichts" als tragbar
  eingestuft, weil ein Ruecklesen einen Registry-Schreibvorgang je Speicherung
  kostet. Diese Rechnung gilt fuer `save_build` und **nicht** fuer
  `_migrate_keys`: dort geht ein *bestehender* Build verloren statt eines
  neuen, und die Migration laeuft **einmal je Nightfarer**, nicht bei jeder
  Speicherung. Der Preis, den ich vermeiden wollte, faellt dort gar nicht an.
  Die Minimalvariante (Pfad ueberspringen, wenn der Name nicht in den Store
  passt) ist ausdruecklich zu wenig - sie deckt nur die eine bekannte Ursache.
- **QA-042 ist der wertvollste Befund dieses Retests, obwohl der ausgelieferte
  Code korrekt ist.** Der Fix zu QA-033 besteht aus zwei unabhaengigen
  Massnahmen; getestet ist nur die erste. Die zweite ist **eine Zeile, die
  jeder spaetere Aufraeumdurchgang als redundant lesen und streichen kann,
  ohne dass etwas anschlaegt** - und das Ergebnis waere wieder stiller
  Datenverlust. Der Ordnungs-Test aus T-019 kann sie bauartbedingt nicht
  fangen. **Lehre daraus: ein Test, der eine Eigenschaft misst, ersetzt nicht
  den Fall, der den Schaden zeigt.** Die Mutationsprobe ist deshalb in T-020
  Abnahmebedingung, nicht Kuer.
- **QA-039 von P4/Minor auf P3/Major angehoben.** Gemeldet war ein Waisen-
  Eintrag ohne sichtbare Wirkung. Der `qa-engineer` hat das Symptom gefunden,
  das die Meldung nicht hergab: ein spaeter unter demselben Namen
  gespeicherter Build faellt beim naechsten Auffrischen und bei jedem Neustart
  aus der Liste. **"Ich speichere und es ist nicht da" ist die
  Fehlerbeschreibung, mit der Support-Faelle beginnen.**
- **QA-043 wird mitgenommen, obwohl es kein Produktfehler ist.** Ein rotes
  Suite-Ergebnis, das wie eine Produktregression aussieht, ist in einer
  Freigabeentscheidung teuer - beim `qa-engineer` hat es in diesem Lauf genau
  einmal Zeit gekostet. Prozess-ID in den Store-Namen, fertig.
- **`selected_build`: der Code hat recht, der Docstring luegt.** Dokumentiert
  ist "eine Sitzung setzt dort an, wo die letzte aufhoerte"; tatsaechlich setzt
  `app.py:3113` die Auswahl beim Start auf "Equipped in game" zurueck, sobald
  das Save ein Gefaess ausgeruestet hat. Der Bildschirm zeigt beim Start den
  Save-Build, also soll der Picker das auch sagen. **Docstring korrigieren,
  Verhalten nicht.**
- **Nebenlaeufigkeit der Migration** (zwei Programminstanzen auf demselben
  Store) ist vom `qa-engineer` als naechster Bruchpunkt von "lesen, schreiben,
  loeschen" benannt. Zurueckgestellt, eigener Auftrag - nicht vergessen.

## Entscheidungen des Directors - Zyklus 4, dritter Durchgang (2026-09-02)

- **QA-041 ist als Nachbedingung geloest, nicht als Ursachenliste - genau so
  war es beauftragt.** Der `developer` prueft nach `sync()` durch Ruecklesung
  aus dem Store, ob der Build unter seinem neuen Schluessel steht **und** den
  geschriebenen Wert haelt; erst dann faellt der Altpfad. Die Laengengrenze ist
  damit nur einer von beliebig vielen moeglichen Gruenden (Quota, verweigerte
  Rechte, ein Backend, das eine Namensform ablehnt), und **keiner davon steht
  im Code**. Die Fehlrichtung zeigt zur sicheren Seite: faellt die Ruecklesung
  faelschlich negativ aus, bleibt eine Leiche liegen - es gehen nie Daten
  verloren. Der ausgeschlossene Minimalfix steht nirgends im Baum.
- **Die Mutationsprobe hat gewirkt.** `path not in written` toetet jetzt zwei
  Tests; beim letzten Mal waren es null. Fuenf von sechs Mutationen fallen.
- **Der Ueberlebende ist als Testluecke akzeptiert, nicht als Beleg.**
  `settings.sync()` in `_migrate_keys` ist von keiner Mutation zu toeten, weil
  dieses Projekt nur auf Windows geprueft wird und die Registry ohnehin aus
  sich selbst antwortet. Die Zeile bleibt fuer dateibasierte Stores (Linux,
  macOS), die sonst aus ihrem eigenen Cache einen Schreibvorgang bestaetigen
  wuerden, den sie noch nicht abgelegt haben. **Wenn Linux oder macOS je
  Zielplattform werden, ist das der Punkt, an dem eine Testluecke zur
  Datenverlustluecke wird** - vermerkt, damit es dann jemand findet.
- **QA-044 aufgenommen: die Kehrseite ist der Preis, und er ist richtig
  bezahlt.** "Nichts entfernen ohne Beleg" heisst zwangslaeufig, dass etwas
  liegen bleibt, mit dem die Oberflaeche nichts anfangen kann. Ein Eintrag, der
  leer laedt und sich nicht loeschen laesst, ist aergerlich; ein geloeschter
  Build ist weg. **Die Aufloesung ist eine Produktentscheidung**, keine
  technische: entweder ein Rueckfall auf den Rohnamen in `load_build` und
  `delete_build` (widerspricht der Trennung Name/Schluessel, die QA-003 erst
  aufgeloest hat), oder ein sichtbares "kann nicht uebernommen werden" im
  Panel. Eigener Auftrag, nicht in diesem Zyklus.
- **`scripts/capture_weapon_damage.py`** setzt weiterhin den festen
  Test-Store-Namen und gehoert damit zur QA-043-Klasse. Vom `developer`
  gemeldet, ausserhalb seines Auftrags, hier vermerkt.
- **Der Regelkonflikt "ein Branch pro Task" bleibt bestehen und ist keiner des
  `developer`.** Ihm sind `branch` und `checkout` ausdruecklich verboten, damit
  er bei ungespeicherten Aenderungen nichts verlieren kann. Er committet auf
  den Arbeitsbranch, ich verantworte den PR-Weg. Kein Rueckbau, keine
  Ermahnung - die Regel gehoert korrigiert, nicht der Agent.

## Entscheidungen des Directors - Zyklus 4, Abschluss (2026-09-02)

- **PUSH FREIGEGEBEN.** Der `qa-engineer` bestaetigt QA-039 bis QA-043 als
  behoben, mit eigener Reproduktion statt uebernommener Entwicklertests:
  fuenf Namenslaengen um die Schluesselgrenze, ein Mischstore aus zu langem
  Namen, Schraegstrich, senkrechtem Strich und Prozentzeichen, Ketten der
  Laenge 2 bis 4 in beiden Einfuegereihenfolgen, und fuenf echte
  Programmstarts mit **byteweise identischem** Store-Dump. Kein
  reproduzierbarer Datenverlust ist uebrig.
- **Der Klassenbeleg zu QA-041 ist enger als der des `developer`, und er
  traegt:** Eine Ruecklesung kann einen verlorenen Schreibvorgang **nur dann**
  faelschlich als gelungen melden, wenn der Zielschluessel bereits genau den
  Wert haelt, der geschrieben werden sollte - und dann steht der Inhalt unter
  dem richtigen Schluessel, das Entfernen des Altpfads kostet nichts. Der
  `qa-engineer` hat genau diesen Fall gebaut (zwei Altpfade mit **identischem**
  Wert, ein Schreibvorgang verschluckt): beide Namen ueberleben mit richtigem
  Inhalt. **Es gibt keinen falsch-positiven Fall, der Daten kostet.**
- **QA-045 geht als Testfall in denselben PR, nicht in den naechsten Zyklus.**
  Es ist kein Codewechsel, und es ist zum zweiten Mal dieselbe Form: ein
  Waechter im Code, den keine Mutation toetet. QA-042 habe ich deshalb zum
  Blocker gemacht; QA-045 dieselbe Behandlung zu verweigern, weil der Schaden
  nur mit einem Testdoppel erreichbar ist, waere inkonsequent. Zwei Zeilen
  Testdaten.
- **QA-046 sperrt den Push nicht, aber es sperrt das Release.** Es ist
  Datenverlust im Normalbetrieb und nach meiner eigenen Gewichtungsregel
  ("loescht" schlaegt "zaehlt doppelt") die schwerste offene Sache in diesem
  Modul. Es ist aber **keine Regression dieser 19 Commits** - im alten Format
  war der Rohname der Schluessel, dieselbe Kollision; die Migration kann das
  Paar deshalb gar nicht antreffen. Ein Fix braucht ein **drittes**
  Schluesselschema (`DERIVED_KEYS = "3"`) und eine erneute Wanderung; das mit
  T-020 zu buendeln wuerde den Umfang der Migration verdoppeln, waehrend
  genau diese Migration gerade zweimal Datenverlust erzeugt hat. **Eigener
  Auftrag, naechster Zyklus, mit derselben Ruecklesungs-Nachbedingung.**
- **`build_key` war von mir in T-018 und T-020 ausdruecklich aus dem Scope
  genommen - und genau dort sitzt QA-046.** Das ist zur Kenntnis zu nehmen,
  nicht zu beschoenigen: die Ausklammerung war richtig (die Ableitung war
  geprueft und in Ordnung), aber "geprueft" hiess "injektiv gegen
  Python-Strings". Die Zusicherung im Kommentar bei `_KEY_SAFE` gilt nicht
  gegen den Store. Der Kommentar gehoert im QA-046-Auftrag korrigiert.
- **QA-047 ist die Kehrseite des QA-043-Fixes und wird nicht rueckgebaut.**
  Vorher: ein Rest, den der naechste Lauf beseitigte, dafuer eine Suite, die
  bei parallelen Laeufen rot wird und wie eine Produktregression aussieht.
  Jetzt: Muell auf Entwicklermaschinen, dafuer verlaessliche Laeufe. Der
  Tausch ist richtig herum. Aufraeumen der verwaisten PID-Schluessel beim
  Start geht in denselben spaeteren Auftrag wie
  `scripts/capture_weapon_damage.py`.
- **Drei Beobachtungen des `qa-engineer` ausdruecklich nicht als Befunde
  gefuehrt:** `keys[path] != path` ist redundant (kosmetisch, und ich wollte
  in diesem Commit nur den Test); `build_names` ohne den `contains`-Filter
  laesst alles gruen (seit QA-040 praktisch unerreichbar); doppelter
  Anzeigename nur mit Testdoppel erreichbar.

### Abschluss Zyklus 4 (2026-09-02)

- **QA-045 geschlossen, mutationsbelegt.** Suite 167. Mit gestrichenem
  Wertvergleich faellt genau der neue Test; die Diagnose zeigt, dass
  `Fire ice` komplett aus dem Store verschwindet, obwohl sein Schreibvorgang
  nie ankam. Damit ist **beide** Haelften des Ruecklesungs-Waechters bewacht.
- **Zyklusbilanz:** 20 Commits. Geschlossen in Zyklus 3 und 4: zwoelf
  Sicherheitsbefunde (SEC-001, 002, 004, 005, 006-Deckel, 007, 008, 010, 012,
  013, 014) und elf QA-Befunde (QA-003, 005 teilweise, 024, 033, 034, 035,
  039, 040, 041, 042, 043, 045). Testsockel 78 -> 167.
- **Zwei Datenverluste sind in diesem Zyklus entstanden und wieder geschlossen
  worden - beide aus dem Fix fuer QA-003, keiner aus dem Altbestand.** Das ist
  die Bilanz, die man nicht schoenreden sollte: eine Migration, die
  Nutzerdaten anfasst, hat drei Developer- und drei QA-Runden gebraucht, bis
  sie nichts mehr zerstoert. Der Grund, dass es aufgefallen ist, war jedes Mal
  dieselbe Methode - eigene Mutationen des `qa-engineer` statt uebernommener
  Entwicklertests.
- **Offen und release-sperrend:** QA-046 (Gross-/Kleinschreibung, P2, kein
  Regress dieses Zyklus), QA-036 (Icon-Pack-Vollstaendigkeit), QA-018,
  SEC-009 (zwei Punkte), GOAL A9, C-002.

## Entscheidungen des Directors - Zyklus 5 (2026-09-02)

- **QA-046 behoben, Push freigegeben.** Der `qa-engineer` hat nicht die
  Entwicklertests uebernommen: 47 gegnerische Namen durch die echte
  Speicherschicht ergeben 47 Eintraege; 235 276 verschiedene Namen ohne eine
  einzige Kollision unter `upper()` und unter `casefold()`; erschoepfend bis
  Laenge 3; Migration Schema 1 nach 3 und 2 nach 3 mit Kollisionspaar;
  Idempotenz ueber je drei echte Programmstarts mit byteweise identischem
  Dump. **26 Mutationen, 18 getoetet, kein Ueberlebender zerstoert Daten.**
- **Der Klassenschnitt nach L-001 hat sich in seinem ersten Einsatz bezahlt
  gemacht.** Der `developer` fand drei weitere Instanzen derselben Klasse, die
  im Befund nicht standen: der Entfernungswaechter verglich mit
  Python-Gleichheit statt gefaltet, `build_names` verglich den
  childKeys-Nachtrag mit doppeltem Gleichheitszeichen, und die Hidden-Marken
  verglichen Schluessel gegen Namen. Die erste haette einen Build gekostet -
  die Mutation M3 belegt es. **Den Auftrag als Klasse zu schneiden hat einen
  vierten Zyklus in derselben Datei verhindert.**
- **Die Grundwahrheit ist jetzt gemessen, nicht angenommen:** die Registry
  gleicht ausser ASCII-Gross/Klein **nichts** an. Der Pruefer hat alle zwoelf
  faltungsverdaechtigen Nicht-ASCII-Zeichen einzeln gegen ihr
  ASCII-Gegenstueck geschrieben - null Zusammenlegungen. Punktloses i,
  scharfes s gegen Doppel-s, NFC gegen NFD, Omega, Mikro, fuehrende Punkte und
  Leerzeichen bleiben getrennt. Keine Unicode-Normalisierung.
- **Die drei geaenderten Bestandstests sind eine Reparatur, keine
  Abschwaechung - und das ist gemessen, nicht argumentiert.** Der Pruefer hat
  zwei datenzerstoerende Mutationen gebaut und die Suite je zweimal gefahren,
  einmal mit der neuen und einmal mit der alten Schreibweise der Faelle. Mit
  der **alten** Schreibweise haette die ganze Datei **beide Datenverluste
  durchgelassen** (57 gruen). Die drei Faelle sind die einzigen, die sie
  fangen. Der `developer` hat fremden Testbestand angefasst und es von sich
  aus gemeldet - richtig so.
- **QA-049 ist der unangenehmste Nebenfund, und er kam aus der Klassensuche,
  nicht aus dem Befund.** Zwei Stellen in `app.py` bauen `QSettings` aus
  Literalen und umgehen die Testumlenkung: **die Suite liest heute den echten
  Speicher des Spielers.** Geschrieben wird dort noch nicht, weil kein Test
  einen Variantenklick ausloest - das ist Glueck, keine Absicherung. Geht in
  den naechsten Zyklus, zusammen mit einem Waechtertest, der den Baum nach
  literal gebauten `QSettings`-Aufrufen absucht.
- **QA-048 wird NICHT einzeln beauftragt.** Das Abbruchfenster zwischen
  Markerschreiben und Entfernungen ist dasselbe Fenster wie die
  zurueckgestellte Nebenlaeufigkeit (zwei Programminstanzen auf einem
  Speicher). Beides einzeln zu fixen hiesse, zweimal dieselbe Frage zu
  beantworten - naemlich, was ein halb migrierter Speicher ist und wer ihn
  erkennt. **Ein Auftrag, beide Faelle.**
- **QA-051: ich entscheide weder streichen noch so lassen.** Der Pruefer hat
  gezeigt, dass die beiden Waechter **einander decken** - jeder einzeln
  entfernt bleibt folgenlos. Das ist etwas anderes als ein Waechter ohne
  Wirkung. Der naechste Auftrag prueft, ob das Entfernen **beider** erreichbar
  ist: wenn ja, ein Testfall; wenn nein, einer faellt weg und der andere
  bekommt einen Kommentar, der die Redundanz benennt. Was nicht bleibt, ist
  der dritte Zustand - zwei Zeilen, von denen niemand sagen kann, wofuer sie
  da sind.
- **QA-050 bestaetigt eine Regel, die ich mitnehme:** eine Zusicherung im
  Kommentar ist so gefaehrlich wie falscher Code, wenn sie den falschen Schutz
  nennt. Die Laengenkette stimmt, die Sicherheitsfolgerung nicht - was die
  Migration schuetzt, ist der gefaltete Entfernungswaechter, nicht die
  Hex-Schreibweise. Der `_KEY_SAFE`-Kommentar hat QA-046 genau deshalb
  ueberlebt.
- **Die zurueckbleibende Alt-Schreibweise ist Absicht und wird nicht
  aufgeraeumt.** Nach einer Kollisionsmigration behaelt der Speicher fuer
  einen der beiden Eintraege die alte Schreibweise, weil die Registry einen
  bestehenden Wert nicht umbenennt. Der Pruefer hat verifiziert, dass sie
  nirgends sichtbar wird. Sie zu jagen hiesse, jeden Wert umzuschreiben, um
  ein unsichtbares Detail zu glaetten. Nein.
- **Die weggelassene Order- und Hidden-Dedupe ist vom Pruefer gedeckt.** Er
  hat keinen erreichbaren Pfad gefunden, der einen doppelten Eintrag erzeugt.
  Damit ist die Linie des `developer` bestaetigt: lieber kein Waechter als
  einer ohne Test.

## Entscheidungen des Directors - Zyklus 6 (2026-09-02)

- **Push freigegeben.** QA-049, QA-050 und QA-051 sind behoben; der
  `qa-engineer` hat alle drei selbst nachgefahren statt die Entwicklertests zu
  uebernehmen. 204 Tests, echter Spielerspeicher vor und nach dem Lauf
  byteweise identisch.
- **QA-054 bekommt eine eigene ID, nicht eine Zeile in QA-044.** Der
  Mechanismus ist derselbe (ein Alt-Pfad bleibt liegen), die **Wirkung auf den
  Spieler ist die entgegengesetzte**: QA-044 heisst "wird gelistet, laedt
  leer"; QA-054 heisst "wird gar nicht gelistet, Daten liegen unerreichbar in
  der Registry". Nach meiner eigenen Gewichtungsregel - verschwinden schlaegt
  doppelt zaehlen - ist QA-054 der schwerere Fall. Zwei Wirkungen unter einer
  ID zu fuehren heisst, dass die leichtere die schwerere verdeckt.
- **QA-049 gilt als Fundstellen-Fix mit Teilabdeckung der Klasse, nicht als
  Klassenabschluss.** Ich hatte in T-022 geschrieben, der Waechtertest sei
  "der Teil, der die Klasse schliesst". Das ist nach QA-052 nicht mehr
  haltbar, und ich korrigiere es hier statt es stehenzulassen.
- **Und damit ist es das dritte Mal in Folge dieselbe Sache.** QA-050: ein
  Kommentar sichert einen Schutz zu, den er nicht leistet. QA-046: der
  `_KEY_SAFE`-Kommentar sagte "injective", ohne den Bezugsrahmen zu nennen.
  QA-052: ein Waechtertest-Docstring sagt "There are no exempted call sites",
  waehrend fuenf Formen woertlich im Baum stehen koennten und passieren
  wuerden. **Das ist kein Zufall mehr, sondern ein Muster: eine Zusicherung
  ohne benannten Geltungsbereich ist keine Zusicherung.** Geht als Vorschlag
  an die `retrospective`.
- **Der Vorschlag des Pruefers zu QA-052 ist der richtige: den Scanner nicht
  aufblaehen, sondern die ehrliche Regel hinschreiben** und die zwei
  billigsten Loecher schliessen (Zuweisungs-Aliase, und bare `ORG`/`APP` nur
  in Modulen gelten lassen, die sie aus `favourites` importieren).
- **Zum Zwischenfall in T-022, aus dem etwas zu lernen ist:** Die
  Mutationsprobe des `developer` hat in den echten Spielerspeicher
  geschrieben, weil er die Mutation auf die **echten** Literale gesetzt hat.
  Der `qa-engineer` hat dieselbe Aussage mit einem harmlosen Fremd-Store
  gemessen und dabei sogar **mehr** Faelle fallen sehen. Die Lehre ist nicht
  "vorsichtiger sein", sondern: **eine Mutation, die einen Umgehungsfehler
  nachstellt, fuehrt ihn auch aus - sie darf deshalb nie auf das echte Ziel
  zeigen.** Geht an die `retrospective`.
- **Punkt 4 des Auftrags - Variantenwahl - ist sauber beantwortet, und zwar
  besser als ich gefragt hatte.** Ich hatte gefragt, ob es nur diesen Rechner
  trifft. Die tragende Antwort haengt nicht an einer Messung: `favourites.ORG`
  und `.APP` fallen ohne Umgebungsvariablen auf **exakt dieselben**
  Zeichenketten zurueck wie die alten Literale. Fuer jeden Spielerstart ist
  der Speicher derselbe wie vorher - es gibt keine Wanderung, also nichts zu
  verlieren. Keine vierte Runde dieser Art.

## Entscheidungen des Directors - Zyklus 7 (2026-09-02)

- **QA-018 ist erklaert, nicht behoben - und das ist das richtige Ergebnis.**
  Der Auftrag verlangte ausdruecklich, zuerst zu erklaeren statt anzugleichen.
  Der `developer` hat es getan und ist dabei auf etwas gestossen, das keine
  Codeentscheidung ist.
- **Die Ursache in einem Satz:** `damage.py` ist **nicht** die eine
  Rechenstelle, sondern die **obere Haelfte einer zweistoeckigen Rechnung**.
  Beide Pfade sind bis `weapons.rate` bitgleich; `attack_rating` legt danach
  eine Multiplikatorschicht darauf, die der Waffen-Tab nie sieht.
  203,4 x 1,2000000476837158 = 244,101... - **die QA-Messung ist exakt der
  Multiplikatorunterschied, nichts sonst.**
- **Die Annahme, die bricht,** steht woertlich in `damage.py`: *"A buff merely
  gated on a weapon type is not restricted at all - that is a flat rate and
  already counted."* Eine Einschraenkung auf eine Angriffsart wird nur erkannt,
  wenn der Effekt `magicSubCategoryChange1/2/3` traegt - das trifft auf 96 von
  175 Buffs zu und wird korrekt ausgesondert. **"Improved Thrusting
  Counterattack" traegt keines dieser Felder: seine Einschraenkung existiert
  nur im Beschreibungstext, in keinem Param-Feld.** 244,1 ist der Angriffswert
  eines Stoss-Konters, angezeigt fuer ein Greatsword, das keinen hat.
- **Keine der beiden Zahlen ist unbesehen richtig.** In diesem Fall ist 203,4
  zufaellig richtig - zufaellig, weil bei einem echten Pauschalbuff
  ("Physical Attack Up +4", +12 %) die Verhaeltnisse **umgekehrt** laegen und
  203,4 zu niedrig waere. Aus den Spieldateien ist nicht entscheidbar, welcher
  Fall vorliegt; es gibt kein Feld, das die beiden Sorten trennt. Die
  betroffene Effektfamilie ist aber klein und vollstaendig aufgezaehlt (vier
  Familien, ~20 IDs).
- **Weg A plus B, wie vom `developer` empfohlen.** A: der Nutzer macht **eine**
  Beobachtung im Spiel, die die ganze Effektklasse entscheidet. B: die Spalten
  werden umbenannt - **B bleibt unter jedem Ausgang von A richtig**, weil das
  Benennungsproblem unabhaengig davon besteht (203,4 = Grundschaden plus
  Attributskalierung, 244,1 = dasselbe plus alle Multiplikatoren; beide heissen
  heute "AR" bzw. "Total"). Weg C - die vier Effektfamilien nach
  `SCOPED_PREFIX` umleiten - **wird nicht gegangen**: er raet gegen die Params,
  und wenn der Buff doch global ist, sortiert der Berater sie faelschlich nach
  unten.
- **Der Steigungstest faellt nicht** - die Steigung des heutigen
  `damage.py`/`model.py` ist in der geforderten Richtung. Kein zweiter Befund
  an der Steigung. Drei Leitern (Wylder/STR, Ironeye/DEX, Recluse/INT), je 15
  Stuetzstellen, drei Mutationen die alle drei Zusicherungen einzeln toeten.
- **Eine Zusage aus dem Auftrag korrigiert, mit Belegen:** Ich hatte
  "abnehmender Ertrag" als streng fallenden Verlauf gedacht. Die drei von
  Waffen benutzten Kurven sind **stueckweise linear** (alle `adj`-Exponenten
  1,0); der Grenzbeitrag ist **innerhalb eines Abschnitts konstant** und
  faellt nur an den Soft Caps (Kurve 0: bei 24, 49, 74). Der Test sichert
  deshalb "steigt nie" **plus** "ist oben kleiner als unten". **Ein Test, der
  strenges Fallen verlangt, wuerde einen Fehler verlangen.** Der `developer`
  hat das gemessen statt meiner Formulierung zu folgen - richtig so.
- **Folge fuer die Oberflaeche, die sonst niemand gesehen haette:** zwei
  Kandidaten im selben Kurvenabschnitt sind **exakt gleich viel wert**. Der
  Picker muss Gleichstaende darstellen koennen und darf keine strenge
  Rangfolge behaupten. Geht an den `ui-ux-designer`.
- **QA-058 ist der eigentliche Klassenbefund** und bekommt einen eigenen
  Auftrag: der `compute`-Waechter zaehlt Zugriffe auf `model.compute`, nicht
  auf `weapons.rate`. "Eine Rechenstelle" gilt fuer die obere Schicht und fuer
  die untere nicht. Sauberer als ein zweiter Waechter waere eine gemeinsame
  Fassade, die Attributsatz, Tier und Multiplikatorschicht **einmal**
  festlegt - das gehoert vor den `architect`.
- **Ein Test, der die Abweichung einfriert (203,4 gegen 244,1), wird bewusst
  nicht gebaut**, solange Schritt 2 nicht entschieden ist. Er wuerde eine Zahl
  festschreiben, ueber die gerade nicht entschieden ist. Der `developer` hat
  die Auslassung gemeldet statt sie zu verschweigen.

## Entscheidungen des Directors - Zyklus 8, Architekturteil (2026-09-02)

- **Fassade statt zweitem Waechter (AD-019 bis AD-021), angenommen.** Die
  Begruendung ist besser als meine Neigung: der `compute`-Waechter traegt,
  weil es genau **einen richtigen Build** gibt. Bei der Waffenrechnung gibt es
  **mehr als eine richtige Frage** an dieselbe Formel. Ein Waechter auf "ein
  Aufrufer" waere entweder falsch (er erzwaenge Achse B weg) oder braeuchte
  eine Ausnahmeliste - **und die sichert die Ausnahmen nicht zu, sie
  beschreibt sie nur.** Das ist derselbe Fehler wie bei den Zusicherungen ohne
  Geltungsbereich (QA-046, QA-050, QA-052), diesmal vorher erkannt.
- **Die Fassade fuehrt drei benannte Fragen** (`EQUIPPED`, `CANDIDATE`,
  `BARE`); jede legt an genau einer Stelle Attributsatz, Tier und
  Multiplikatorschicht fest. Die Wahl der Eingaben wird damit eine **benannte
  Entscheidung** statt einer Nebenwirkung davon, welches Modul importiert
  wurde.
- **Fuenf der acht Abweichungen sind Absicht, drei sind Fehler** (AD-020).
  Genau die Unterscheidung, die ich verlangt hatte: Ziel-Tier,
  Grundattribute, Startwaffen-Paarung, klassengebundene Raten und
  Krit-Ausschluss bleiben; Kachel gegen Tafel, die vierfache Formel und die
  implizite Multiplikatorwahl fallen. **Eine Fassade, die alles
  vereinheitlicht, haette das Programm falsch statt konsistent gemacht.**
- **Die wichtigste Antwort: die Fassade muss vor den Berater - die
  Spielmessung nicht.** Der Grenzbeitrag vergleicht Kandidaten bei **fester
  Waffe**; eine flache Multiplikatorschicht skaliert ihn, dreht ihn nicht um,
  und Pruefpunkt 16 ist gegenueber diesem Faktor invariant. **Ab W5 blockiert
  die Spielmessung nur noch die angezeigte absolute Zahl, nicht mehr den
  Berater-Bau.** Scharfe Randbedingung: das gilt fuer Relikt-Rangfolgen bei
  fester Waffe; Zielrichtungen, die **Waffen gegeneinander** stellen, haengen
  an den je Waffe verschiedenen `class_rates` und duerfen erst nach W6 scharf.
- **Das Zyklus-2-Verfahren traegt nur zur Haelfte, und das ist richtig
  erkannt.** Fuer W1/W2 ja; fuer W3 bis W6 nicht - dort **sollen** sich drei
  der vier Stellen aendern, ein eingefrorener Golden-Stand wuerde den Befund
  einfrieren statt ihn zu sichern. Ersatz: der Differentialtest wandert auf
  die **untere** Schicht - `weapons.rate` bleibt ueber den ganzen Umbau
  bitgleich, abweichen darf nur, was die Fassade darueberlegt.
- **OF-17 entschieden: ja, `tests/golden/weapon_damage.json` darf bei W3/W4
  neu aufgenommen werden - aber erst, wenn Pruefpunkt 18 gruen ist**, und die
  AD-019-Begruendung gehoert in die Commit-Nachricht. Der Golden-Test erlaubt
  eine Neuaufnahme heute nur nach einem Spiel-Patch; hier ist der Grund ein
  bewusster Strukturwechsel, und der muss im Commit stehen, damit die naechste
  Rolle nicht "der Golden-Test wurde mal angepasst" liest.
- **W0 zuerst: `weaponstab.py` wird geloescht, nicht migriert** (QA-057). Es zu
  migrieren hiesse zu entscheiden, was `setRange(0, 25)` bei Tier-Semantik
  1..4 bedeutet - eine Frage ohne Antwort. Loeschen spart ein Viertel der
  Migrationsflaeche.
- **OF-18 geht an den laufenden `ui-ux-designer`**, nicht an mich: die drei
  `Basis`-Fragen koennen gleichzeitig auf dem Schirm stehen, und die
  Spaltenbenennung muss sie unterscheidbar machen. `Rating.basis` wird
  mitgeliefert, damit die Anzeige benennen **kann**, was sie zeigt.

## Entscheidungen des Directors - Zyklus 9, W0 und W1 (2026-09-02)

- **W0 abgenommen ohne eigenen QA-Lauf.** Trivialfall nach der Regel
  "developer plus Stichprobe": eine Loeschung, deren Totsein belegt statt
  behauptet wurde (Importe, Klassenname, Modulname, `tests/`, `scripts/`,
  `run.py` und die PyInstaller-`.spec` **gelesen**, nicht nur gegreppt) und
  deren Testzahl vorher wie nachher 213 ist. **Was dabei ungeprueft bleibt und
  hier stehen soll:** ob ein **gebautes** Artefakt noch laeuft. Das faellt
  unter GOAL A9 und ist ohnehin offen - ich behaupte nicht, es sei durch
  diesen Schritt gedeckt.
- **W1 abgenommen: 30 000 Differentialfaelle, 0 Abweichungen**, dazu 35 154
  Arsenal-Kacheln in sechs Konfigurationen. **Der Vergleicher wurde selbst
  mutationsgeprueft** (Skalierungsterm weg, Nullfilter weg, `DAMAGE_TYPES`
  umgedreht - alle drei gefangen). Ein Differentialtest ohne diesen Nachweis
  waere eine Zahl ohne Aussage gewesen.
- **Die drei Stellen haben arithmetisch dasselbe gerechnet.** Die Unterschiede
  waren keine Rechenunterschiede, sondern **welches** `WeaponRating` gefragt
  wird - genau die von AD-020 als Absicht eingestuften Achsen B und C.
  `per_type()` fasst sie nicht an. **Keine vierte Einstufung noetig.**
- **Der zusaetzliche Testcommit bleibt.** Der `developer` hat eine Datei mehr
  angelegt als der Auftrag woertlich nannte (`test_weapon_rating_per_type.py`,
  213 -> 218) und sie **in einen eigenen Commit** gelegt, damit ich sie ohne
  den Refactor fallen lassen kann. Das ist die richtige Art, eine
  Scope-Grenze zu behandeln, die man fuer zu eng haelt: liefern, trennen,
  melden - statt sie stillschweigend zu dehnen oder die Arbeit unfertig
  abzugeben. Die Tests sind mutationsbelegt und bleiben.
- **QA-059 aufgenommen.** Ein **Zufallswert im Anzeigetext**: dieselbe Waffe
  listet ihre Skalierungsunterschiede nach jedem Programmstart anders.
  Kosmetisch fuer den Spieler, aber es macht jeden kuenftigen
  Differentialtest an diesem Tab unbrauchbar, wenn niemand `PYTHONHASHSEED`
  festnagelt - der `developer` ist genau darueber gestolpert und hat es
  zunaechst fuer eine Regression seiner eigenen Aenderung gehalten. Eigener
  kleiner Auftrag, **nicht** in W2 mitnehmen.
- **Zwei Fragen gehen vor W2 an den `architect`**, weil sie Benennung und
  Struktur betreffen und nicht der `developer` sie entscheiden darf:
  **(a)** `damage.AttackRating.per_type` ist ein **Feld** (nach
  Multiplikatoren), `weapons.WeaponRating.per_type()` jetzt eine **Methode**
  (vor Multiplikatoren), und AD-019 sieht `Rating.per_type` als drittes vor -
  **drei Dinge gleichen Namens auf drei Schichten.**
  **(b)** Der Waffen-Tab zeigt "AR" aus `rating.total`
  (`sum(base) + sum(scaled)`), die Typzeilen darunter aus `per_type()`
  (typweise). Gleiche Summanden, andere Klammerung; **dass beide auf dieselbe
  angezeigte Ganzzahl runden, ist heute Glueck der Gleitkommaordnung, nicht
  Konstruktion.** Leitet die Fassade ihren `total` aus `per_type()` ab, ist
  das strukturell erledigt - sonst bleibt ein stiller Driftpfad genau der Art,
  die W1 gerade geschlossen hat.
- **Das Differentialwerkzeug bleibt vorerst im Scratchpad.** Es ins Repo zu
  nehmen ist ein eigener Auftrag, keine Beigabe - aber es wird fuer W3 und W4
  gebraucht, und dort **werden** Abweichungen erwartet. Vor W3 entscheiden.

## Entscheidungen des Directors - vor W2 (2026-09-02)

- **AD-022 angenommen: der Name nennt die Schicht, und `X_total` ist immer die
  Summe genau des gleichnamigen `X_per_type`.** Der `architect` hat eine
  **vierte** Kollision gefunden, die niemand gemeldet hatte und die tiefer
  sitzt: `weapons.WeaponRating.base` heisst "vor der Attributskalierung",
  `damage.AttackRating.base_total` heisst "auf den **Grundattributen**". Zwei
  Bedeutungen von `base` in zwei Modulen, die einander importieren - dieselbe
  Fehlerklasse wie QA-058, nur in der Benennung. Auch das Enum heisst jetzt
  `Question` statt `Basis`: `Basis` neben `base_*` waere dieselbe Falle noch
  einmal.
- **W1b wird ein eigener Schritt, vor W2.** Nicht Ordnungsliebe: eine reine
  Umbenennung ist **beweisbar bitgleich** und von der bestehenden
  30-000-Fall-Strecke gedeckt, ohne eine Zeile neuen Testcode. Steckt sie in
  W2, **kann der Differentialtest "umbenannt" nicht mehr von "veraendert"
  unterscheiden** - und genau diese Trennung ist das Geruest des
  Migrationspfads.
- **Zusicherung Z1 in AD-019, und sie traegt weiter als meine Frage.** Ich
  hatte die doppelte Summe als Anzeigeproblem gestellt. Der `architect`
  zeigt: **der Grenzbeitrag ist eine Differenz zweier Totals**, und bei
  unterschiedlicher Klammerung setzt nicht die Arithmetik das Rauschniveau des
  Vergleichs, sondern die Inkonsistenz - waehrend Grenzbeitraege klein sind.
  Z1 wird als **exakte** Gleichheit geprueft (`==`, kein `approx`).
- **`weapons.WeaponRating.total` bleibt bis W4 bitgleich unveraendert** - es
  ist der Bezugspunkt der Differentialpruefung, solange zwei Pfade existieren.
  Es faellt in W5, wenn kein Leser ausserhalb der Fassade mehr da ist; ab dann
  gibt es im Programm genau **eine** Summation.
- **Die `fields`-Doppelschleife nur unter Erhalt der Multiplikationsreihenfolge**
  - eine Zusammenlegung aendert die Assoziationsreihenfolge und damit
  potentiell das letzte Bit, und W2 ist als bitgleich zugesagt. Gelingt es
  nicht sauber, wandert es nach W5. **Entschieden am Differentialtest, nicht am
  Augenschein.**
- **AD-023 ist die eigentliche Verbesserung, und sie kam aus einer Korrektur an
  ihm selbst.** Der `ui-ux-designer` hatte belegt, dass sein Invarianzargument
  fuer kandidatengetragene Multiplikatoren nicht traegt. Statt es nur
  einzuraeumen, hat er es **gerechnet**: bringt ein Kandidat selbst eine Rate
  `r` mit, entsteht ein Term `m*(r-1)*S(B)`, der am **ganzen** Angriffswert
  haengt statt am Zuwachs - bei `S(B) ~ 300` und `r = 1,20` sind das 60,
  waehrend +5 Staerke `S` einstellig bewegt. **W6 entscheidet also nicht die
  Groesse, sondern welche Effektfamilie gewinnt.**
- **Folge: der Vorbehalt wird berechnet, nicht pauschal gesetzt.** Die
  Invarianz ist keine Eigenschaft der Zielrichtung, sondern des
  **Kandidatenfelds**, und exakt pruefbar: betroffen ist ein Kandidat genau
  dann, wenn einer seiner Effekte ein Feld aus `AR_RATE_FOR` traegt. Die
  Familie ist vollstaendig aufgezaehlt - **das ist ein Test, keine
  Heuristik.** Traegt kein Kandidat des Laufs ein solches Feld, ist die
  Rangfolge invariant und es braucht **gar keinen Vorbehalt**. Das ist der
  haeufige Fall.
- **Das geht an den `ui-ux-designer` zurueck:** AK-47 spezifiziert `unverified`
  auf **jeder** Karte. Nach AD-023 ist das zu grob - der Vorbehalt gehoert an
  die **betroffenen Zeilen**, nicht als Banner. Er hielt die pauschale Fassung
  ohnehin fuer den schwaecheren Weg und hat es gemeldet; jetzt gibt es einen
  Grund, ihm recht zu geben.
- **Und meine state.md-Formulierung wird zum dritten Mal praezisiert.** Was
  bleibt: Fassade vor Berater, und der **Bau** des Beraters ist ab W5 nicht
  durch die Spielmessung blockiert. Was ersetzt wird: die **Auslieferung**
  einer Rangfolge mit AR-Raten-Kandidaten ist es sehr wohl - bis W6 nur mit
  Markierung an den betroffenen Zeilen. **Pruefpunkt 16 ist auf
  Attributskandidaten formuliert und ist kein Beleg fuer die Rangfolge
  gemischter Felder.** Dass diese Passage dreimal nachgeschaerft werden musste,
  gehoert hierhin: sie ist die schwierigste Aussage des Vorhabens, und jedes
  Mal hat eine andere Rolle den Fehler gefunden.

## Entscheidungen des Directors - Abnahme W0 und W1 (2026-09-02)

- **W0 und W1 freigegeben.** Der `qa-engineer` hat ein **eigenes**
  Differential gefahren, nicht das des `developer`: 71 720 `attack_rating`-
  Faelle, 14 344 Arsenal-Kacheln, 3 642 Waffentafeln, 6 synthetische
  Randfaelle - **89 706 Vergleiche, 0 Abweichungen**, Vergleicher
  mutationsgeprueft.
- **Die W0-Luecke ist geschlossen, nicht vertagt - und das ist die beste
  Einzelleistung dieses Zyklus.** Ich hatte gesagt, wenn sie es ohne Build
  nicht entscheiden kann, bleibt es unter GOAL A9 offen. Sie hat **zwei echte
  PyInstaller-Artefakte gebaut** (Vor-W0-Stand und HEAD, beide im Scratchpad,
  Repo unberuehrt): `nrplanner.weaponstab` war **auch vorher nicht im
  Artefakt** - 0 Treffer in `PYZ-00.toc`, `Analysis-00.toc`, `xref` und im
  58-MB-EXE-Binaerstrom; Modulmenge **341 zu 341, Differenz leer in beide
  Richtungen**. Dazu die sechs Wege, auf denen ein nicht importiertes Modul
  doch im Artefakt landen koennte, einzeln geprueft. **Die Datei war nie
  drin; ihr Loeschen kann nichts aendern.**
- **Der zusaetzliche Testcommit des `developer` ist im Nachhinein der
  wichtigste Teil von W1.** Der `qa-engineer` hat eine eigene Mutation
  gefahren, die er nicht kannte: `per_type` ueber die **Einfuegereihenfolge**
  statt ueber `DAMAGE_TYPES`. Ergebnis: **die 213 alten Tests bleiben gruen,
  nichts merkt es** - nur sein neuer Reihenfolge-Fall faellt. Diese Mutation
  ist heute verhaltensgleich und morgen nicht mehr, **sobald die W2-Fassade
  ein `WeaponRating` anders zusammensetzt.** Der Test, den ich haette
  fallenlassen koennen, ist genau der Waechter, den W2 braucht.
- **Und die alten 213 binden `per_type()` wirklich** - ueber den Golden-Test
  fallen drei von vier verhaltenswirksamen Mutationen, und eine Mutation um
  Faktor 1,0001 zeigt, dass die Empfindlichkeit **unter** die Anzeigerundung
  reicht.
- **QA-061 geht an den Nutzer, nicht an den `developer`.** Es ist keine
  Codefrage: entweder kennt Nightreign keine Attributsvoraussetzungen fuer
  Waffen - dann sind Checkbox, Kachel-Dimmen, "Requires"-Zeile und ein ganzer
  Rechenzweig toter Code - oder die Extraktion liest ein leeres Feld und
  **jede Waffe wird faelschlich als tragbar angezeigt.** Im Spiel in einer
  Minute entscheidbar, und der Nutzer schaut ohnehin fuer QA-018 hinein.
  **Vor W2 entscheiden**, sonst erbt der naechste Differentialtest denselben
  blinden Fleck.
- **QA-060 ist von AD-022 bereits aufgeloest** (Schichtpraefix), Umsetzung in
  W1b. Der `qa-engineer` hat unabhaengig dieselbe Kollision gefunden wie der
  `architect` - ein gutes Zeichen fuer beide.
- **QA-062 geht in W2**, nicht davor: `test_every_type_the_rating_holds_comes_back`
  ist heute ein **Datenwaechter**, kein Codewaechter, und das wird genau dann
  relevant, wenn die Fassade `WeaponRating`s selbst zusammensetzt.
- **QA-059 bleibt der einzige Fall seiner Klasse** - der `qa-engineer` hat
  jede Mengenoperation in `nrplanner/` einzeln bis zum Anzeigetext verfolgt
  **und** 369 Textbloecke des vollen Fensters unter zwei Hash-Saaten
  verglichen (0 Unterschiede). Bis zum Fix laeuft jeder Differentiallauf an
  diesem Tab mit `PYTHONHASHSEED=0`.
- **Zur Rueckfrage des `qa-engineer`, ob die Aenderungen an `ARCHITECTURE.md`
  und `docs/state.md` waehrend seines Laufs Absicht waren: ja.** "Eingefroren"
  gilt fuer den **Code**, nicht fuer die Register und Entwurfsdokumente - die
  fuehre ich waehrend eines Prueflaufs fort, und der `architect` hat parallel
  an `ARCHITECTURE.md` gearbeitet. `nrplanner/` und `tests/` waren unberuehrt,
  und er hat das selbst nachgeprueft, statt es anzunehmen. Richtig gefragt.

## Entscheidungen des Directors - W1b und W2 (2026-09-02)

- **W1b abgenommen ohne eigenen QA-Lauf.** Reine Umbenennung, byte-identisches
  Differential ueber 14 362 Faelle, Vergleicher gegen eine dritte mutierte
  Kopie geprueft. Der eine **stille** Fehlermodus (`if x.per_type:` — auf einer
  gebundenen Methode immer wahr) wurde gezielt gesucht, auch als
  String-Literal. **Was nicht gedeckt ist und hier stehen soll:** eine
  Sichtpruefung auf UI-Ebene. Die reitet mit der W2-Abnahme mit.
- **W2: die `sum()`-Entscheidung des `developer` ist richtig, ich gewichte
  nicht anders.** Er ist auf einen Konflikt gestossen, den niemand vorhergesehen
  hat: `AttackRating.scaled_total` wurde bisher als Schleife akkumuliert, und
  **das eingebaute `sum()` summiert Floats seit Python 3.12 kompensiert**
  (Neumaier-Korrektur). Gleiche Summanden, gleiche Reihenfolge, **1 ULP
  Unterschied in 214 von 143 440 Kombinationen.** Sein erster Durchlauf war
  deshalb nicht bitgleich — 356 von 258 210 Datensaetzen.
  **Er hat nicht die Schranke gesenkt, sondern getrennt:** die Fassade
  summiert (Z1 gilt dort lueckenlos), die Sicht der Tafel behaelt ihre
  Akkumulation in `_accumulated()`, kommentiert und mit Verfallsdatum W3. Damit
  ist W2 bitgleich **und** Z1 in der Fassade vollstaendig. Die Alternative
  waere gewesen, 214 Ein-ULP-Abweichungen in einer nirgends sichtbaren
  Zwischenzahl zu akzeptieren — nicht schlimm, aber es haette die
  Bitgleichheit als Abnahmebedingung aufgeweicht, und die ist das Geruest
  dieses Migrationspfads.
- **F2 ist eine Klassenaussage ueber das ganze Repo, nicht ein Detail:**
  **jede** ausgeschriebene Summenschleife, die jemand spaeter durch `sum()`
  ersetzt oder umgekehrt, aendert unter Python 3.12 das letzte Bit — unsichtbar,
  weil jede Anzeige rundet. Das gilt fuer W3 (dort fallen beide Altsummen) und
  fuer **jeden kuenftigen Bitgleichheits-Schritt**. Geht an den `architect` als
  Randbedingung und an die `retrospective`.
- **F1 aendert den Zuschnitt von W6, und das ist wichtig.** `rank_candidates`
  sortiert ueber Schicht 1. Solange `MULTIPLIERS_FOR[CANDIDATE]` False ist,
  ist die sortierte Zahl die angezeigte Zahl — **setzt W6 den Wert auf True,
  sortiert die Liste nach einer anderen Zahl als sie anzeigt.** Gemessen: der
  Tabellenwert auf True mutiert faerbt einen Test rot. **W6 ist damit nicht
  "ein Wert und sonst nichts", sondern ein Wert plus die Umstellung der
  Sortierung auf `final_total` mit stabilem Zweitschluessel** (Regel 29). Der
  `developer` hat es nicht selbst geaendert — richtig: das haette W6
  vorweggenommen und die Reihenfolge des Waffen-Tabs geaendert, was W4 ist.
- **Die Zusammenlegung der `fields`-Doppelschleife ist der lehrreichste Teil
  des Berichts.** Seine erste Mutationsprobe ergab **0 Abweichungen** — und er
  hat das **nicht** als Freibrief genommen, sondern als blinde Probe erkannt:
  der Datensatz stellt fast nie Build-Rate und klassengebundene Rate auf
  dasselbe Feld, und mit Faktor 1,0 sind beide Klammerungen bitgleich. Er hat
  daraufhin zwei Builds von Hand gebaut, die beide Ratensaetze besetzen, und
  alles dreimal neu gefahren. Erst dann verschob die verbotene Umgruppierung
  **6 248 Datensaetze** — und erst dann bedeutete "0 Abweichungen" etwas.
  **Ohne diesen zweiten Schritt haette dort dieselbe Null gestanden und nichts
  belegt.**
- **Z1 ist strukturell durchgesetzt, nicht geprueft-und-gehofft:**
  `scaled_total` und `final_total` sind **Properties, keine Felder** — man kann
  einer `Rating` kein Total uebergeben. Der Test dazu prueft genau das
  (`dataclasses.replace(..., final_total=...)` wirft), nicht nur die
  Gleichheit: ein gespeichertes, heute zufaellig richtiges Feld waere durch
  einen blossen Vergleich gekommen.
- **Zur CI, ausdruecklich vermerkt:** alle 14 neuen Tests haengen an der
  `game_data`-Fixture und werden auf dem GitHub-Runner **uebersprungen** — wie
  der Golden-Test. Die Belege stammen samt und sonders von dieser Maschine mit
  dem echten Datensatz. Das ist dieselbe Luecke wie DEBT-001, eine Ebene
  hoeher, und sie ist noch nicht geschlossen.

## Entscheidungen des Directors - Abnahme W1b und W2 (2026-09-02)

- **W1b und W2 freigegeben.** Der `qa-engineer` hat **1 032 768 Datensaetze**
  ueber zwei unabhaengige Strecken und drei Staende gefahren, jede Zahl als
  Hex-Darstellung - byte-identisch. Dazu **1654 Oberflaechenzeilen** ueber
  Waffen-Tab, Kachel, Tafel und Tooltip, ebenfalls byte-identisch, und
  **12 Mutationen** zur Schaerfung des Vergleichers.
- **Die sum-Ursache ist bestaetigt, und die Klassenfrage hat mehr gefunden als
  den Anlass.** Die `bonus`-Schleife in `weapons.rate` ist die **zweite und
  weitaus groessere** Stelle: kompensierte Summation statt Schleife verschiebt
  **48 100 von 258 192** Karten, gegenueber 0,15 Prozent an der Stelle in
  `damage.py`. Sie traegt keinen Kommentar, waehrend die kleine Stelle einen
  zwoelfzeiligen hat. **Wer sie in W3 bis W6 aufraeumt, bricht die
  Bitgleichheit an der breitesten Stelle des Umbaus.**
- **Meine Frage zur fields-Zusammenlegung ist besser beantwortet als
  gestellt.** Der `qa-engineer` hat gemessen, dass es **keine einzige**
  klassengebundene Rate auf den Power-Feldern gibt - klassengebundene Raten
  existieren ausschliesslich auf den Attack-Feldern. Damit ist die
  Umgruppierung auf **erreichbaren Eingaben beweisbar neutral**, nicht bloss
  gemessen-neutral, und zwar aus einem strukturellen Grund: `rate` startet bei
  1,0, und die Multiplikation mit exakt 1,0 ist verlustfrei. **Die Vorsicht
  war trotzdem richtig** - ein einziger neuer Effekt mit klassengebundener
  Power-Rate kippt die Bedingung.
- **Z1 ist strukturell dicht.** Acht Angriffe: `object.__setattr__` wird
  abgewehrt, Schreiben in `__dict__` gewinnt nicht gegen die Property,
  `dataclasses.replace` wirft, es gibt keine zweite Konstruktionsstelle. Die
  zwei Wege, die funktionieren (Unterklasse, feindliches Mapping), sind die
  Python-uebliche Grenze jeder Kapselung, kein Loch.
- **QA-063 ist die fuenfte Instanz derselben Klasse, und sie sitzt jetzt im
  Waechter selbst.** `_KEY_SAFE` sagte "injective" (QA-046, **Datenverlust**);
  die Hex-Begruendung nannte einen Schutz, den sie nicht leistet (QA-050); der
  AST-Waechter sagte "no exempted call sites" (QA-052); der Docstring
  versprach eine Filterregel, die er nicht hat (QA-062); und jetzt prueft der
  Z1-Fall **zwei Feldnamen**, waehrend die Zusicherung "kein Total von aussen"
  lautet - **der Abstand dazwischen ist ein Feld mit anderem Namen, und die
  volle Suite bleibt gruen.** Ebenso der Krit-Ausschluss: eine der fuenf
  AD-020-Absichten ist nur ein Kommentar. **Das ist die dominante Fehlerklasse
  dieses Projekts** und gehoert in `docs/lessons.md`.
- **QA-064 Punkt (a) wird vor W3 behoben, nicht danach.** Er ist nicht nur
  ungenau, er ist **aktiv falsch**: `rank_candidates` sagt, seine Reihenfolge
  sei die, die der Waffen-Tab immer gezeigt hat - der Tab sortiert je Familie
  neu und verwirft sie. **W4 stellt den Tab auf `rank_candidates` um und wird
  genau diesen Satz als Begruendung lesen.**
- **W2b wird eingeschoben, vor W3.** Umfang: QA-063 (Feldmenge vollstaendig
  festnageln statt zwei Namen auszuschliessen, plus ein Fall fuer den
  Krit-Ausschluss), QA-064 (a) bis (d), QA-065. Alles Tests und Kommentare,
  kein Verhalten - und genau deshalb billig, solange es **jetzt** passiert.
- **Zur Frage, ob die Oberflaeche "kein Mensch mit Augen gesehen" hat:** die
  Zeile stimmt so nicht mehr und wird geteilt. Waffen-Tab und Waffentafel sind
  am **laufenden Fenster** gerendert und angesehen worden - mehr als headless,
  weniger als ein Nutzer. Was weiterhin **niemand** getan hat: das Programm
  als Mensch **benutzen**, mit einem Ziel, auf einem gebauten Artefakt. Das
  bleibt dem `power-user` und GOAL A9.
- **QA-067 ist ein Vorbestand und trotzdem der Befund, den ein Spieler zuerst
  bemerkt:** "AR 164" ueber "Physical 84 / Magic 81". Wer nachrechnet, findet
  einen Fehler, der keiner ist.

## Entscheidungen des Directors - W3b (2026-09-03)

- **W3b erfuellt die Abnahmebedingung: beide Mutationen sind rot.**
  `active-tile-only` von 237 gruen auf 3 rot, `breakdown-base-and-scaled-swapped`
  von 237 gruen auf 10 rot. Beide sind namentlich in
  `scripts/differential/mutate.py` hinterlegt und nachfahrbar - das ist mehr,
  als ich verlangt hatte.
- **Der `developer` hat meiner Fixrichtung widersprochen, und er hat recht.**
  Ich hatte geschrieben, die erweiterte Golden-Erfassung erledige "beide
  nicht-aktiven Faelle mit einem Schritt". **Sie erledigt (a) nur knapp:** die
  Mutation wird ueber **genau einen** der 18 Golden-Faelle gefangen - den
  einzigen mit einer gefuellten, nicht aktiven Kachel. **Ein spaeteres
  Streichen dieses Falls haette den Waechter still entfernt** - exakt die
  QA-070-Klasse, die wir gerade schliessen. Er hat zusaetzlich einen
  Invariantentest gebaut und den Mehraufwand gemeldet statt ihn zu
  verschweigen.
  **Entscheidung: der Invariantentest ist der tragende Waechter, die
  Golden-Erfassung der Regressionsteppich.** Kein zweiter Golden-Fall - eine
  Fallmengen-Erweiterung ohne Auftrag waere derselbe Fehler in der anderen
  Richtung.
- **Seine Warnung an den `qa-engineer` ist wichtiger als der Fix selbst.** Die
  naheliegende breitere Aussage - "die Kachelzahl haengt nie am aktiven Slot" -
  ist **falsch**: Startwaffen-Paarung und Waffen-Gates folgen dem aktiven
  Slot. **Ein Test, der sie fordert, waere der Fehler.** Genau die Sorte
  Zusicherung, die zu weit greift, die dieses Projekt fuenfmal Geld gekostet
  hat - diesmal vorher erkannt.
- **Der bewusst rote Zwischen-Commit (`b196266`) ist akzeptiert.** Meine
  Trennung "Codeaenderung getrennt von Neuaufnahme" war verbindlich, und
  dazwischen kennt die Golden-Datei zwei von vier Feldern. Der Preis ist ein
  Commit, bei dem `git bisect` stolpert; der Gegenwert ist, dass die
  Neuaufnahme als eigener Schritt nachvollziehbar bleibt. **Der
  Commit-Text sagt es ausdruecklich** - damit ist es dokumentierte Absicht,
  kein Unfall. **Fuer W4 bis W6 gilt dieselbe Trennung**; wer bisect faehrt,
  ueberspringt diesen einen Commit.
- **QA-075 zeigt seinen Wert sofort.** Das Raster des `developer` ist **nicht**
  das des `qa-engineer` - gleiche Groesse (1793 x 14), anderer Inhalt, darum
  weichen die Reichweitenzahlen ab (42,9 % gegen 50,0 %). **Genau deshalb
  gehoerte es ins Repo:** erst jetzt sind zwei Messungen ueberhaupt
  vergleichbar. Effekte kommen als **Abfrage** ins Raster und werden einmal zu
  IDs aufgeloest - eine auf dem zweiten Baum wiederholte Abfrage koennte
  anderes waehlen, und der Diff wuerde dann die Abfrage messen statt die
  Aenderung. Das ist die Sorte Detail, die eine Messstrecke erst belastbar
  macht.
- **QA-074-Disziplin eingehalten und richtig eingeordnet:** ungerundete und
  gerenderte Zahl fallen in seinem Raster **zusammen** - und er sagt dazu,
  dass das eine Eigenschaft des **Rasters** ist, nicht des Programms (der
  kleinste Multiplikator dieses Rasters ist gross genug, dass die Rundung
  keine Kachel verdeckt; mit x1,007 waere es anders).
- **Eine Luecke, die er selbst benennt und die ich nicht ueberlese:** ob eine
  Mutation an der **Quellzuordnung** im Aufschluesselungstext rot wird, hat er
  **nicht gemessen**. Seine Formulierung: "das ist eine Luecke, kein Beleg."
  Geht an den `qa-engineer`.
- Nicht angefasst, wie angeordnet: QA-072 (`arsenaltab.py:367` verdeckt das
  Modul `damage` - steht fuer W4 an), QA-061, QA-071 (nach W5),
  `MULTIPLIERS_FOR[CANDIDATE]`, der `compute`-Waechter, `WeaponRating.total`.

## Entscheidungen des Directors - nach der W3b-Abnahme (2026-09-03)

**Das Muster, das ich hier benennen muss: wir sind in der dritten Runde
"Waechter, die nicht bewachen", und jede Runde erzeugt neue.** QA-070 fuehrte
zu QA-073, QA-073 fuehrte zu QA-076 bis QA-082. Das ist kein Versagen der
Rollen - es ist, was passiert, wenn man anfaengt, Waechter ernsthaft zu
pruefen. Aber es ist eine Regression ins Unendliche, wenn niemand sie
abschliesst. **Ich schliesse sie hier, mit einer benannten Grenze statt mit
einem Gefuehl.**

- **W3b abgenommen und freigegeben.** Beide Abnahmemutationen rot, 36 von 36
  Golden-Werten unbewegt (dazu unbewegte Falldefinitionen und Datensatzkopf -
  strenger als verlangt), roter Zustand exakt auf `b196266` begrenzt,
  Endstand 259 gruen.
- **Ich hebe die engere Fassung auf: "die Kachelzahl haengt nicht am aktiven
  Slot" wird zur Zusicherung** (Antwort auf offene Frage 1 des
  `qa-engineer`). Begruendung: sie **haelt strukturell** - Gates ueber
  `weapons_held`, Paarung ueber den Slot-Index, Klassenraten ueber die Klasse
  der gerateten Waffe - und ist ueber 120 Gitter gerundet **und** ungerundet
  mit 0 Abweichungen gemessen. Wuerde spaeter jemand entscheiden, dass
  klassengebundene Buffs nur fuer die aktive Waffe gelten, **soll** dieser
  Test rot werden: das waere ein bewusster Bruch, kein Unfall. Genau dafuer
  sind Zusicherungen da.
- **Die Warnung des `developer` war also gut gemeint und faktisch falsch**
  (QA-082). Das ist kein Vorwurf - er hat vor einem Test gewarnt, der zu weit
  greift, und das ist die richtige Reflexhaltung in diesem Projekt. Hier greift
  er nicht zu weit, und der `qa-engineer` hat es gemessen statt es zu glauben.
- **QA-076 wird vor W4 behoben. Er ist der einzige der sieben, der das muss.**
  Grund: `weapon_damage_cases.run` **setzt** `last_sources` selbst, statt es
  ausloesen zu lassen. Die neue Golden-Spalte sieht deshalb aus, als hielte sie
  die Verdrahtung, und haelt nur die Formatierung. **W4 fasst genau diese
  Schicht an** - das ist dieselbe Verwechslung, die QA-070 und QA-073 erzeugt
  hat, diesmal vor dem Umbau bekannt.
- **QA-079 wird mitbehoben, weil es das Messinstrument selbst betrifft.** Ein
  Instrument, das still danebenmisst, ist schlimmer als keines - und dieses
  traegt ab jetzt jede Abnahme von W4 bis W6. Besonders (a): die
  Hashseed-Verweigerung liest die **Umgebungsvariable** statt
  `sys.flags.hash_randomization`, also die Meldung statt des Signals. Das ist
  woertlich die Klasse, die dieses Projekt fuenfmal Geld gekostet hat, diesmal
  im Werkzeug.
- **QA-080 und QA-082 gehen mit** - beides Doku, beides Zusicherungen, die
  ihren Geltungsbereich nicht nennen. Zusammen mit QA-076 und QA-079 sind das
  vier Zeilen Arbeit.
- **QA-077 wird NACH W4 beauftragt, nicht davor.** Er ist vorbestehend, deutlich
  groesser (der ganze Charakterbogen statt der Waffentafel), und ihn jetzt
  mitzunehmen wuerde die Charakterisierung von W4 verwaessern - genau der
  Fehler, den die Trennung von W1b und W2 vermieden hat. **Zurueckgestellt,
  nicht vergessen.**
- **QA-078 und QA-081 werden dokumentiert zurueckgestellt.** QA-078 (der
  Goldring) ist eine Zeile im vorhandenen Invariantentest und kann mit dem
  naechsten Anlass mitgehen. QA-081 bekommt einen Satz im Docstring, der die
  Ein-Fall-Abhaengigkeit benennt - **keine Fallmengen-Erweiterung ohne
  Auftrag**, das waere derselbe Fehler in der anderen Richtung.
- **Die Grenze, die ich ziehe:** nach W3c gehen wir zu W4, auch wenn die
  naechste Pruefung wieder Waechterluecken findet. Was ab dann gefunden wird,
  wird **dokumentiert und eingeplant**, nicht sofort geschlossen - ausser es
  betrifft die Schicht, an der der naechste Schritt arbeitet. Das ist das
  Kriterium, nicht die Prioritaet: **ein blinder Winkel dort, wo gerade
  gearbeitet wird, ist teurer als ein groesserer anderswo.**

## Entscheidungen des Directors - W3c (2026-09-03)

- **W3c erledigt, jeder Punkt mit Rot-vorher-Beleg.** Der `developer` hat fuer
  (a), (b) und (c) jeweils die alte Fassung kurz zurueckgesetzt, den neuen
  Test fallen sehen und danach exakt zurueckgestellt - mit sha256-Vergleich
  vorher/nachher als Beleg, dass nichts haengengeblieben ist.
- **Die schaerfste Beobachtung des Laufs betrifft (c):** der Nachweis fuer
  `use_tree` musste in einen **Subprozess**, weil der Testprozess `nrplanner`
  bereits importiert hatte - der `sys.modules`-Cache haette die Pruefung sonst
  maskiert. Ein Test, der im selben Prozess laeuft, waere gruen gewesen und
  haette nichts belegt. **Das ist dieselbe Klasse wie QA-079(a) selbst** -
  ein Nachweis, der die Meldung statt des Signals prueft - und er hat sie beim
  Bauen des Fixes fuer genau diese Klasse erkannt.
- **QA-076 geloest, ohne die gute Entscheidung zurueckzunehmen.** Die
  Harness-Zuweisung bleibt (die Begruendung war und ist richtig), aber der
  Docstring benennt die Luecke, und ein eigener Waechter ruft `recompute()`
  **real** auf und prueft gegen `current_build()`. Nicht-Vakuitaet geprueft.
- **Commit-Hygiene: akzeptiert, kein Rueckbau.** Der QA-081-Kommentar ist
  versehentlich im QA-076-Commit mitgelaufen, weil beide Aenderungen in
  derselben Datei lagen. Der `developer` hat es von sich aus gemeldet.
  Funktional korrekt; Historie umzuschreiben kostet mehr als der Gewinn.
- **QA-080 als Doku geloest statt als Verhaltensaenderung** - Default 20
  bleibt, das Flag steht jetzt im Docstring. Der kleinere Eingriff, und beide
  Wege waren zugelassen.
- **Neue Debt, gemeldet und nicht behoben:** der Kommentar in `mutate.py`
  behauptet, `app.py` sei CRLF im Arbeitsbaum - gemessen ist es LF
  (`.gitattributes` erzwingt es). Das **Verhalten** ist richtig
  (`newline_of()` erkennt zur Laufzeit), nur die Kommentierung ist veraltet.
  Wieder dieselbe Klasse, diesmal harmlos. Geht mit dem naechsten Anlass mit.
- **W3c bekommt keinen eigenen QA-Lauf.** Es sind Doku und Waechter, jeder mit
  eigenem Rot-vorher-Beleg des `developer`. **Die Pruefung reitet mit der
  W4-Abnahme mit** - und zwar zwingend, weil der `qa-engineer` das
  Messinstrument dort ohnehin benutzt: waere es kaputt, faellt es genau dann
  auf, wenn es zaehlt. Das ist die Anwendung der Grenze, die ich nach der
  W3b-Abnahme gezogen habe.

## Entscheidungen des Directors - AD-024, Summationsreihenfolge (2026-09-03)

- **Meine Lesart war falsch, und der `architect` hat sie praezise widerlegt.**
  Ich hatte vorgeschlagen: "die Klammerung je Schadensart ist die richtige,
  die alte war der Fehler, die 584 ULP sind die Korrektur." Das behauptet, eine
  der beiden Summationen sei **genauer** - und das ist nicht belegbar. Beide
  sind gleich gute Naeherungen, und **gegen das Spiel ist keine von beiden
  geprueft.** Wer es so festschreibt, laedt ein, die Frage spaeter mit
  Genauigkeitsargumenten wieder aufzumachen.
- **Seine Fassung, die ich uebernehme:** *Der Fehler war nie einer der beiden
  Werte - der Fehler war, dass es zwei gab.* Die Klammerung je Schadensart ist
  verbindlich, **weil Z1 sie festlegt**, nicht weil sie besser ist. Die 584 ULP
  sind der **Preis** der Vereinheitlichung, nicht ihre Korrektur - und die
  Messung des `developer` belegt genau das, wofuer man sie braucht: der Preis
  ist unsichtbar (0 von 7172 Anzeigetexten).
- **Die Regel, die beide Stellen entscheidet - und sie entscheidet sie
  entgegengesetzt:**
  > Die Summationsreihenfolge wird nur geaendert, wenn die Aenderung **zwei
  > Darstellungen derselben Zahl auf eine reduziert**. Eine Aenderung, die nur
  > "genauer" verspricht, wird nicht vorgenommen.
  Arsenal-Tab erfuellt sie (zwei Darstellungen verschwinden) -> gemacht.
  Die `bonus`-Schleife erfuellt sie **nicht** - dort gibt es nur **eine**
  Darstellung, eine Umstellung waere eine einseitige Genauigkeitsaenderung ohne
  Konsistenzgewinn, bei 48 100 von 258 192 Karten. **Sie bleibt dauerhaft eine
  Schleife, nicht "bis W5".**
  **Das Kriterium ist nicht die Groessenordnung, sondern ob eine
  Doppeldarstellung verschwindet.** Dieselbe Klasse, entgegengesetzte Antwort.
- **Folge: der Kommentar an der `bonus`-Schleife sagt das Falsche.** Er bindet
  sie an die Bitgleichheit **eines Schrittes**; richtig ist die
  AD-024-Begruendung, die dauerhaft gilt. Geht als kleiner Punkt in W5 mit -
  kein eigener Auftrag.
- **Ort: weder AD-020 noch AD-022, sondern AD-024** mit einem **Verweis** als
  AD-020 Punkt 9. Begruendung, die ich uebernehme: AD-020 trennt Absicht von
  Fehler bei **semantischen** Unterschieden - welche Frage eine Anzeige stellt.
  Die Klammerung stellt keine andere Frage, sie beantwortet dieselbe mit einem
  anderen letzten Bit. Als neunter gleichrangiger Punkt wuerde sie verwischen,
  wofuer die Liste da ist.
- **W5: die Frage verschwindet nicht mit `WeaponRating.total`.** Z1 wird
  innerhalb der Fassade trivial wahr, aber die **Regel** muss stehen bleiben,
  sonst schreibt die naechste Anzeige `sum(base) + sum(scaled)` erneut hin.
  Teilsummen sind erlaubt, **Vergleiche gegen `final_total` nicht**.
- **Nicht-tun-Regel 29 ist jetzt gemessen begruendet statt vorsorglich:** nach
  dem Wegfall von `WeaponRating.total` sortiert `rank` auf der abgeleiteten
  Summe, und 584 von 7172 Werten verschieben sich um 1 ULP - **nahe
  Gleichstaende koennen die Plaetze tauschen.** Stabiler Zweitschluessel
  `(-summe, weapon["id"])`.
- **Und er hat nachgesehen statt zu warnen.** Er war kurz davor, ein
  CPython-Versionsrisiko fuer den Golden-Stand zu melden - und hat es geprueft:
  `rounded()` rundet auf sechs Nachkommastellen, 5,68e-14 liegt **acht
  Groessenordnungen darunter**. Ein Versionswechsel kann die Golden-Datei nicht
  rot faerben. Steht jetzt in AD-024, damit es niemand erneut prueft. **Eine
  gepruefte Nicht-Gefahr ist wertvoller als eine gemeldete Vermutung.**

## Entscheidungen des Directors - W4-Abnahme (2026-09-03)

- **W4 freigegeben.** Der `qa-engineer` hat eine eigene Strecke mit **anderem
  Nightfarer, anderem Level, anderen Bedienelementen** gefahren: 871 von 7172
  gegen seine 8,1 %. Kein Widerspruch - beide Zahlen tragen ihr Raster, und
  genau dafuer liegt es seit QA-075 im Repo.
- **Die Signatur ist algebraisch geschlossen, nicht statistisch - das ist der
  Unterschied, auf den es ankommt.** `sum([x])` ist exakt (Startwert 0.0,
  Korrekturterm 0), also fallen bei **einer** Schadensart beide Klammerungen
  bitgenau zusammen, unabhaengig von den Werten. Die **2736 einartigen
  Datensaetze sind die Gegenprobe mit Zaehlbeleg: eine einzige Abweichung dort
  haette die Erklaerung widerlegt.** Es gab keine.
- **QA-085 ist der Befund, der vor W5 muss.** Keine Signalverdrahtung des
  Arsenal-Tabs ist gehalten: `connect`-Zeile streichen -> 275 gruen, die
  Bedienung bewegt nichts mehr. Und der zweite Fall ist **QA-001 woertlich
  zurueck** - der Tab rangiert gegen Attribute, denen das Datenblatt nebenan
  widerspricht. **Auch die Differentialstrecke ist blind**, weil jeder Test und
  die Harness `recalculate()` selbst rufen: geprueft wird die Rechnung, nie der
  Ausloeser. **W5 fasst genau diese Datei an.**
- **Zwei offene Fragen des `qa-engineer`, beide von mir entschieden:**
  1. **Die Zauber-Sektionen bekommen jetzt keine Waechter** - sie zeigen Zahlen
     direkt aus dem Datensatz, ohne Rechnung. **Aber der Grund gehoert
     hingeschrieben**, sonst ist es genau die unausgesprochene Reichweite, die
     dieses Projekt sechsmal Geld gekostet hat: *"diese Zahlen sind
     ungerechnet; wird eine davon je gerechnet, braucht sie einen Waechter."*
     Eine Zusicherung, die ihren Geltungsbereich nennt - das ist die Lehre,
     angewandt auf eine Nicht-Handlung.
  2. **Dass der Rarity-Filter die Zauber nicht filtert, ist vertretbar** -
     Rarity ist eine Waffeneigenschaft. **Die gemischte Zaehlung ist der
     Fehler** und bleibt als QA-089 beim `ui-ux-designer`.
- **QA-086 wird gezielt ergaenzt, nicht verbreitert.** Der Waechter soll nicht
  jede Zeile jeder Kachel halten - das waere unbegrenzt. Zwei Faelle genuegen:
  eine mehrtypige Armatur vollstaendig gegen `damage.candidate`, und der
  Rarity-Filter gegen die Zaehlung in der Zusammenfassung. **(c) ist der
  eigentliche Schaden:** bei Tier 1 verschwinden 696 Waffen aus "Common", der
  Spieler waehlt ein Band und bekommt ein anderes.
- **QA-055 bleibt "teilweise", jetzt unabhaengig belegt.** Die Arsenal-Kachel
  traegt die Beschriftung `AR` **allein**, ohne Tier; 203 steht neben 321, und
  die einzige Stelle, die das Tier nennt, ist die Spinbox plus ein `+1` mitten
  im Fliesstext. Genau der Zustand, den AK-31, AK-33 und AK-38 beheben - und
  den AK-40 ausdruecklich **nach** W4 erlaubt.
- **QA-087 ist die Klasse im Nachweis statt im Code**, und der `qa-engineer`
  hat den Unterschied sauber getrennt: der Code verweigert die Worktree-Form
  tatsaechlich (nachgestellt), nur der Testkoerper prueft die falsche Variante,
  waehrend sein Docstring die richtige benennt. **Dieselbe Klasse wie QA-082,
  eine Ecke schaerfer.**
- **Und noch eine gepruefte Nicht-Gefahr:** die vom `developer` genannte Falle
  mit mehrdeutigen Waffennamen (4x "Scholar's Thrusting Sword") **beisst
  heute nicht** - alle vier Waechter-Armaturen tragen eindeutige Namen,
  insgesamt sind nur 8 Armaturen auf 3 Namen betroffen. Gemessen statt
  vermutet.


## Entscheidungen des Directors - T-033/T-034, P1 abgeschlossen (2026-09-03)

- **QA-018 GESCHLOSSEN.** Nutzerentscheid: "counterattack ist nur bei konter,
  nicht global." Vier Effektfamilien (~22 IDs) aus der flachen
  Multiplikatorschicht genommen, in `model.py` als `MOVE_SCOPED_EFFECT_IDS`
  mit vollstaendiger Begruendung (nur Counterattack gemessen, die drei
  Zauberfamilien abgeleitet und so markiert). **Ausgangsfall bestaetigt:**
  Wylder's Greatsword + Improved Thrusting Counterattack zeigt jetzt 203,4 auf
  **Kachel und Tafel** - vorher 244 gegen 203. Golden-Datei neu aufgenommen
  (3 von 18 Faellen bewegt, alle drei mit den betroffenen Relikten).
- **W6 vollstaendig:** `MULTIPLIERS_FOR[CANDIDATE]` gesetzt, `weapons.rank`
  auf `final_total` mit stabilem Zweitschluessel umgestellt (Regel 29). Der
  `developer` hat dabei einen eigenen Waechter zunaechst **leer** laufen
  lassen (284 gruen, 0 Kills) und ihn auf einen echten AD-024-Gleichstand
  umgestellt, statt die gruene Zahl zu nehmen - genau das Verhalten, das
  dieses Projekt seit Zyklus 3 verlangt.
- **AD-023-Vorbehalt hat nach W6 keinen Fall mehr** - er hedgte eine
  unentschiedene Frage, die jetzt entschieden ist. Ein **neuer, engerer**
  Vorbehalt bleibt fuer die drei abgeleiteten Zauberfamilien (18 der 22 IDs),
  falls eine Messung sie widerlegt - nicht implementiert, nur benannt.
- **QA-061 GESCHLOSSEN.** Nutzerentscheid: "Anforderung ist das
  Charakterlevel, sonst nichts." Checkbox "Meets requirements", Kachel-Dimmen,
  "Requires"-Zeile, `unmet`/`meets_requirements` und der auf echten Daten
  unerreichbare `weapons.rate`-Zweig entfernt. **Skalierung unangetastet.**
  Bitgleich bestaetigt: 14 344 Datensaetze, 0 Abweichungen.
- **QA-019 aufgeloest, nicht gestrichen.** Der `developer` hat den
  betroffenen Golden-Fall nachgemessen statt geloescht: die Waffe traegt zwei
  Schadensarten und ist die einzige "ohne Relikte"-Baseline mit dieser
  Eigenschaft. Umbenannt auf das, was er wirklich prueft
  ("a two-type armament with no relic effects"), keine `expected`-Werte
  veraendert.
- **Zwei Fundstellen, die der `developer` nicht anfassen durfte und die jetzt
  anstehen:** (1) Die Arsenal-Zusammenfassung sagt seit W6 "Attack rating is
  base damage plus what your stats add to it" - **das ist seit
  `MULTIPLIERS_FOR[CANDIDATE]=True` falsch**, AK-34 sieht Fassung B fuer genau
  diesen Fall vor. (2) `ARCHITECTURE.md` nennt noch die alte
  `rank_candidates(..., require_usable)`-Signatur.
- Suite 275 -> 285 (T-033: +12, T-034: -2 durch Streichung eines Tests fuer
  den entfernten Zweig).


## AD-019-Umbau ABGESCHLOSSEN (2026-09-03)
W0 bis W6 vollstaendig. Suite 78 -> 296. QA-085/086 (letzte blinde Winkel im Arsenal-Tab) geschlossen. WeaponRating.total entfernt, rank() sortiert auf scaled_per_type()-Summe mit stabilem Zweitschluessel. AD-021-Waechter scharf (nur damage.py ruft weapons.rate/rank). attack_rating bleibt bewusst als zweite Schnittstelle fuer bare Bewertungen (AD-018-Grenzbeitrag, Golden-Test).

**Fuer den Berater (P3) wichtig:** `test_marginal_returns.py` nutzt noch `attack_rating()` statt der vorgesehenen `candidate()`-Fassade (AD-021). Kein Fehler, aber der Berater selbst MUSS `candidate()`/`rank_candidates()` verwenden - der AD-021-Waechter erzwingt das automatisch, sobald `nrplanner/advisor/` existiert.


## QA-Retest T-036 nachgereicht (2026-09-03, nach Session-Pause)

Der ausstehende Retest ist zurueckgekommen, NACHDEM bereits gepusht wurde
(siehe QA-094). Ergebnis: QA-085 und QA-086 sind unabhaengig bestaetigt, kein
Codefund faellt weg. Fuenf neue Kleinbefunde, drei davon Praezision an
Nachweisen (dieselbe Klasse wie immer: Zahl ohne Reichweite):

- **QA-090** (P3): die W5-"0 von 7172"-Charakterisierung kann Reihenfolge
  konstruktiv nicht sehen - unabhaengig gemessen: Layer-eins-Ordnung bewegt
  sich in 23 von 80 Kombinationen, die ANGEZEIGTE Ordnung in 0 von 80. W5
  bleibt folgenlos, aber aus einem anderen Grund als die zitierte Zahl zeigt.
- **QA-091** (P3): achte Umgehung des AD-021-Waechters - Sternimport
  (`from .weapons import *`) laesst 296/296 gruen, obwohl eine zweite
  Rechenstelle entsteht. Relevant fuer P3 (Build-Berater): der Waechter soll
  ihn zwingen, die Fassade zu nutzen.
- **QA-092** (P4): Zahlen im Mutationsregister zu QA-086(c) reproduzieren
  nicht (856/160 statt korrekt 696/0) - der Waechter selbst ist in Ordnung.
- **QA-093** (P4): Zweitschluessel-Test nennt sich "der einzige Fall, an dem
  es sichtbar ist" - es sind 25 von 160 gepruefte Kombinationen. Mechanismus
  bestaetigt, Titelzeile zu stark.
- **QA-094 (P2, Prozessbefund gegen den Director):** der Code war waehrend
  der Nachpruefung NICHT eingefroren, und der Push ging rein, bevor das
  QA-Ergebnis da war - weil die Session mitten in der Nachpruefung fuer den
  Handover pausiert wurde und der Director-Sync-out nicht wusste, dass ein
  Retest noch offen lief. **Inhaltlich folgenlos** (nur Doku-Commits dazwischen,
  kein Codefund faellt weg), aber die Reihenfolge "QA-Ergebnis vor Push" war
  hier nicht gehalten. Lehre fuer kuenftige Sessions: vor einem
  Handover-Sync-out pruefen, ob noch ein Pruefagent laeuft, und dessen
  Ergebnis abwarten oder den Push-Status explizit als vorlaeufig kennzeichnen.

**Fuer die naechste Session:** QA-085/086 sind jetzt vollstaendig
bestaetigt - kein weiterer Retest noetig, P3 kann direkt beginnen. QA-090
bis QA-094 sind neue P7-Kandidaten (Waechter-/Testschulden), niedrige
Prioritaet, koennen mit P7 mitlaufen.

## T-038 (2026-09-03, parallele Session "Scaling Questions"): Angriffskraft gegen das Spiel gemessen

Quelle: Fan-Messung Lv12 (310 Waffen x 8 Nightfarer) und RPS-Skalierungsbuchstaben; Bericht `docs/berichte/T-038-qa-engineer.md`, Recherchen R-004/R-005. IDs QA-095 bis QA-099 vergeben (Nummernkreis laut `docs/state.md`). Zwei Nebenbefunde ohne eigene ID: (1) `weapons.rate` hat keinen Einhaengepunkt fuer eine Kalibrierung und keinen Charakterisierungstest gegen eine Spielzahl - Teil des Fixes zu QA-095; (2) die Elden-Ring-Buchstabenschwellen gelten in Nightreign nicht (S >= 73, A 60-70, B 45-58, C 30-44, D 16-29, E 7-13, Grenzen 45 und 30 scharf), nur relevant, falls je Buchstaben angezeigt werden.

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-095 | **Die Angriffskraft des Programms ist um den Faktor 1/0,6 zu hoch.** Spiel = `floor(0,6 x weapons.rate)`, exakt: Intervallschnitt ueber 9 skalierungsfreie Waffen x 8 Nightfarer ergibt k in [0,5993, 0,6009), Rundung statt Abschneiden ist ausgeschlossen (leere Schnittmenge). Modell trifft 1965 von 2256 Anzeigewerten ganzzahlig exakt (97,5 % ohne die unbrauchbare Duchess-Spalte). Faktor trifft Grundschaden und Skalierung gleich, ist level-unabhaengig (Lv 1/12/15) und steht in keinem gelesenen Param (Hypothesen a-f einzeln widerlegt, T-038 Abschn. 6). Trainingspuppe: realer Schaden = Anzeige (Nutzer 03.09.2026). Rangfolge unberuehrt, jede absolute Zahl falsch. **Fix-Richtung:** Kalibrierkonstante einmal in `weapons.rate`, benannt mit Geltungsbereich; Abschneiden nur an der Anzeige (QA-074); README Known limits nachziehen; Charakterisierungstest gegen die gemessenen Spielwerte mit toetender Mutation 0,6 -> 1,0 und floor -> round (Soldier's Crossbow 88 vs 89) | P1 | Major | director (A7-Entscheid), developer | echte Spieldaten + Fan-Messung Lv12, 310 Waffen x 8 Helden; RPS-Buchstaben als unabhaengige Quelle: 387/387 Zellen im Band ihres Buchstabens | offen - Entscheid des App Designers (F4) | 2026-09-03 |
| QA-096 | **Raider trifft mit Greataxe und Great Hammer (wep_type 19/23) x1,1819 haerter** als das Programm rechnet - 25 Waffen, Spanne 1,1786-1,1839, nur beim Raider, nur dort (Kolossal 0,998-1,003; Wylder/Executor auf denselben Waffen 0,996-1,003). Zeilenversatz, Zweihaendigkeit (STR x1,5) und der Passivtext des Raiders einzeln ausgeschlossen. Ursache unbekannt, ordnungsrelevant fuer den Berater. **Nachtrag T-042:** Faktor per Intervallschnitt **exakt 1,18** (m in [1,179733; 1,180116), `floor(0,6 x 1,18 x rate)` trifft 25/25; 1,1819 war ein Median ueber abgeschnittene Werte). Params-Suche **negativ mit Nenner**: 252 Tabellen, 257 912 Zeilen, 6,66 Mio. Gleitkommazellen inkl. undefinierter Bytes; nur EquipParamWeapon und SpEffectParam koennen einen Waffentyp nennen, dort symmetrisch (max x1,09 je Typ); kein heldenseitiges Angriffsfeld. **Der float32-Wert 1,18 existiert als spielererreichbarer Multiplikator nur als Relikt-Effektstufe** ("Improved Attack Power when Two-Handing", "Attack Up when Wielding Two Armaments") - zwei Lesarten gleichberechtigt: Klassenregel des Raiders oder Fan-Ablesung mit aktivem 1,18-Relikt. **Beobachtung, keine Spielregel**, bis Lv15-Messung (T-042 Abschn. 7: Raider reliktfrei, einhaendig, Greataxe 15000000 -> 141 ohne / 166 mit Regel) | P2 | Major | director (Frage F2 an App Designer), developer | echte Spieldaten, 25 Waffen, Kontrollen negativ; T-042 Negativliste | offen - nicht einbauen, solange ohne Quelle (A7) | 2026-09-03 |
| QA-097 | **Revenant's Cursed Claws (id 21750000): x0,87 fuer jeden Nightfarer ausser dem Revenant** (Besitzer 0,9994; sieben andere 0,865-0,887). Keine allgemeine Startwaffenregel: die sieben uebrigen Startwaffen liegen bei jedem Helden bei 0,951-0,999. Nutzer 03.09.2026: jeder Nightfarer kann die Claws fuehren, eigenes Moveset - die Zellen sind Messungen. R-006: Item-Text belegt die Absicht ("Only the Revenant can make proper use of this weapon ... reduced to a blunt instrument"), keine Zahl in der Community. **Nachtrag T-042:** Faktor **0,88** exakt (m in [0,877440; 0,882700), 8/8; 0,87 verfehlt vier Helden um je 1). Params-Suche negativ (siehe QA-096); jede Zeile mit 0,88 haengt an einem unreferenzierten Eintrag. Lv15-Messung: Recluse mit Claws 87 / 76 / 75 trennt die Lesarten | P3 | Minor | director (Frage F3 erledigt; Einbau erst mit Quelle) | echte Spieldaten, 8 Helden, Gegenprobe ueber alle 8 Startwaffen; T-042 | offen - belegte Absicht, unbelegte Zahl | 2026-09-03 |
| QA-098 | **Fan-Messung (Nightreign Weapon Scaling.xlsx): zwei der acht Spalten stehen nicht auf Level 12.** Guardian durchgehend Level 11 (265 von 271 Waffen; erklaert die 'Guardian-Anomalie' der Director-Sonde vollstaendig), Duchess blockweise gemischt (198 auf L11, 69 auf L12, nach Zeilennummer) und als Beleg unbrauchbar. Kontrollspalten eindeutig L12 (83-89 % innerhalb 0,5 AP). Quellenbefund, kein Codefehler - gilt fuer jede Weiterverwendung der Tabelle | P3 | Major | director | 271 Waffen je Spalte, Level 8-15 je Spalte gefittet | offen - Quelle mit Einschraenkung fuehren | 2026-09-03 |
| QA-099 | **Staebe und Siegel: das Programm zeigt die physische AR (~27-68), das Spiel die Zauber-/Anrufungsskalierung (78-237).** Herkunft in **T-043 gefunden**: `Anzeige = floor(90 x ReinforceParamWeapon.unknown_1 x (1 + Kurve16(INT bzw. FAI)/100))` - trifft **84 von 84** Fan-Zellen und **28 von 28** RPS-Zahlen exakt. `unknown_1` (Offset 128, f32, letztes Feld; Paramdef deckt die Zeile exakt) liest `extract.py` nicht; 53 von 2317 Waffen sitzen auf einer Gruppe mit Wert != 1,0, **alle** Katalysatoren. K = 90 aus Intervallschnitt [89,9982, 90,0147]; `round`, Einfluss 0,9 in der Klammer und 81 von 82 Kurven ergeben je eine **leere** Schnittmenge. Herkunft der 90 offen (Motorkonstante oder correct x Einfluss/100, an den Daten nicht trennbar; fuer die Reihenfolge folgenlos). Nur die Basisraritaet ist belegt. **Fehlreihung bestaetigt** (Rotten Crystal Staff 67,8 vor Carian Regal Scepter 37,1; Spiel 182 vs 237). Die Aussage aus T-038 Abschn. 8 "C steht in keinem Param" ist **widerrufen** | P2 | Major | developer, ui-ux-designer, director (A7, Anzeige ersetzen oder daneben) | 28 Katalysatoren x 3 Zauberer + RPS-Liste; alle 252 Param-Tabellen durchsucht; `docs/berichte/T-043-qa-engineer.md` | offen - umsetzbar, Auftrag folgt | 2026-09-03 |
| QA-099a | **Zwei verschiedene Waffen heissen `Recluse's Staff`** (33750000 = Startwaffe der Recluse, Kennzahl 76,5; 33770000 = Fremdzeile ohne Zauberplatz, `equippedSpell_R1/R2 = -1`, 42 von 268 Feldern verschieden). Ebenso `Finger Seal` (34000000/34750000, zahlengleich) und `Scholar's Thrusting Sword` (4 Zeilen). Namensbasierte Zuordnung und Anzeige sind mehrdeutig. *(ID-Nachtrag zu QA-099, weil der Nummernkreis der Scaling-Session voll ist; der Audit-3-Director darf eine regulaere ID vergeben)* | P2 | Major | developer, ui-ux-designer, director | echte Spieldaten, Feldvergleich (T-043 7.2) | offen | 2026-09-03 |
| QA-099b | **Korrektur an T-038 Abschn. 8:** die Fan-Zeile `Recluse Staff` wurde ueber die Fuzzy-Stufe auf 33770000 statt 33750000 gelegt; genau diese Zeile hat die Herkunftssuche in T-038 scheitern lassen. Mehrdeutige Kandidaten muessen als Nichttreffer gemeldet werden statt einer Aehnlichkeitsstufe ueberlassen. Uebrige 308 Zuordnungen unberuehrt | P3 | Major | director, qa | `assignment.json`, Stufe `fuzzy` (T-043 7.3) | offen - Messstreckenregel | 2026-09-03 |
| QA-099c | **`unknown_1` ist ein Platzhaltername und wird tragend.** `values.get("unknown_1", 1.0)` macht ein vom Paramdex umbenanntes Feld ununterscheidbar vom Vorgabewert - alle 28 Katalysatoren fielen still auf 90 zurueck. Beim Einlesen pruefen: Feld vorhanden **und** mindestens eine Gruppe != 1,0, sonst laut scheitern | P3 | Minor | developer, architect | `param.read`: row_size 132 = def 132, `def_is_prefix=False` (T-043 7.4) | offen - gehoert in den Fixauftrag zu QA-099 | 2026-09-03 |

## Zyklus 12, T-041: Erstdurchlauf gegen den Rechenkern des Beraters (2026-09-03)

Quelle: `docs/berichte/T-041-qa-engineer.md`. Grundlage: T-037 (`developer`),
Commit 690db5f/6ab589a auf `docs/audit-and-advisor-design`. Nachweisweg: 27
frische `git archive`-Extraktionen, 26 volle Suitelaeufe. Die 15 Mutationen
des `developer` sind unabhaengig nachgefahren — **0 Abweichungen**. Neun
eigene Gegenbauten gegen `advisor/evaluate.py`, davon vier ueberlebend.
Regression am Fenster ueber 18 Konfigurationen: 0 Unterschiede.

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-100 | **Pruefpunkt 13 faengt keinen seiner eigenen Gegenbauten; vier der sieben `model.compute`-Argumente des Beraters sind ungewacht.** `weapons_held=[]`, `weapon=None`, `ctx.level→1` und `ctx.hero→heroes[0]` lassen je **398 passed** stehen. Ursache: der Testzustand ist entkernt (Level 1, eine Waffe = die Referenz, keine Waffeneffekte, `declared={}`, Deep aus, Wylder ist `heroes[0]`). Der Fall ist lebendig (Relikteffekte entfernt → rot), sieht aber genau das nicht, wofuer er gebaut ist. Klasse QA-070/073/083/086 | P1-Kandidat, eingestuft **P2** (Wirkung erst ab S9) | Major | developer | 9 Gegenbauten, je volle Suite im eigenen Baum; Planner-Zustandssonde | offen | 2026-09-03 |
| QA-101 | **„Die Rangfolge waere bei `candidate` dieselbe" ist widerlegt.** Drei Effekte (7120400/500/600) tragen die Startwaffen-Strafe ×0,85 selbst; ein Kandidat kann sie mitbringen. Gemessen: R0 `[7120400, 6001400]` → d(equipped) −12,36 gegen d(candidate) +21,36, R1 +0,83 in beiden → **Reihenfolge gedreht**. 10 von 309 Relikten des Saves betroffen. Die Entscheidung `equipped` ist damit **richtiger**, die Begruendung falsch — und sie steht als `survival_means` in `mutate.py` | P2 | Major | director, developer | Gegenbeispiel-Kandidatensatz, Effekt- und Bestandsauszaehlung | offen — Entscheid des Directors (Vorbehalt aus `docs/state.md` aufgeloest) | 2026-09-03 |
| QA-102 | **Der `SlotPool` — das Ergebnis des Hauptwegs — traegt keine A7-Zeile der Zielrichtungen.** `pool()` nimmt von `GoalScore` nur `.value`; `unknowns`, `weights_note`, `unit`, `display` fallen an der Poolgrenze weg. AD-004s gemeinsame Zeile ueber nicht gezaehlte konditionale Effekte existiert nirgends (zwei Suchen). Spec-Konflikt AD-010 (Pflichtfeld im Ergebnis) gegen `UI_SPEC` AK-50 (fester Satz ausserhalb der Karten) — nicht vom `qa-engineer` zu entscheiden | P2 | Major | director, developer | Codelesung + Pool-Ausgabe | offen | 2026-09-03 |
| QA-103 | **Annahme 6 („eine Durchlassrate ist nie null") steht nur im Docstring.** Gemessen: 0,0 → nackter `ZeroDivisionError`; −0,5 → still `Effective HP 700` statt 1120; 1e-12 → still `Effective HP 1,4e14`, was jede Rangliste anfuehrt und die gemessene Regel („non-positive 0") **nicht verletzt**. Einzige der sechs Annahmen, die A7 nicht erfuellt | P3 | Major | developer, director | drei Randwerte einzeln gefahren | offen | 2026-09-03 |
| QA-104 | **Ohne Referenzwaffe zaehlt ein klassengebundener Angriffsbuff exakt 0, und keine Zeile sagt es.** Gemessen: derselbe Effekt 0,000000000 ohne Waffe, +14,27 mit passender `ranged`-Waffe. 8 solcher Effekte im Datensatz. `_NO_ARMAMENT_NOTE` nennt den Geltungsbereich zu eng | P3 | Minor | developer, ui-ux-designer | Messung mit und ohne Referenzwaffe | offen | 2026-09-03 |
| QA-105 | **Systemisch: die Vorbedingungspruefungen des Beraters nennen ihren Umfang zu weit.** Der Docstring sagt „die zwei Vorbedingungen, die ein Aufrufer falsch machen kann"; es sind mehr: Gewichtssumme 0 → `ZeroDivisionError` (2 Faelle), negatives Gewicht → still falsche Zahl, unbekannter Feldname → still neutral 1.0, doppelte Schluessel → still verworfen, `Budget(0)` ungeprueft, `pools` prueft `rank_by` ohne freie Slots nicht. OF-3 (Bedienelement fuer die Gewichte) macht daraus einen Nutzerpfad | P3 | Minor | developer | sieben Faelle einzeln nachgestellt | offen | 2026-09-03 |
| QA-106 | **Auf einem Runner ohne Spielinstallation prueft keiner der 107 neuen Faelle eine Zahl des Beraters.** Gemessen (conftest im Klon entschaerft): 61 laufen, 46 ueberspringen — und die 61 sind 46 Formpruefungen, 1 Registry-Pruefung und 14 Tests des Messwerkzeugs. Pruefpunkt 13 ueberspringt zweifach. Die Zahl 398 traegt dort fast nichts vom Berater | P3 | Major | director, developer | Runner-Simulation, Faelle je Datei gezaehlt | offen | 2026-09-03 |
| QA-107 | **`held_fingerprint` ist positionsunabhaengig, der als Cache-Schluessel benannte `AdvisorRequest` ist es nicht.** Gemessen: Fingerabdruck gleich, Request und Hash verschieden. Der Wächter `test_where_a_relic_is_held_does_not_change_the_fingerprint` prueft damit eine Eigenschaft, die der Schluessel nicht hat; AD-016s Begruendung fuer die Positionsunabhaengigkeit tritt nicht ein. Klasse QA-082/QA-087 | P3 | Minor | developer, architect | Hash-/Gleichheitsprobe | offen | 2026-09-03 |
| QA-108 | **Bestand ohne Handles: jeder Pool leer, Zeile sagt „of this colour" auch am weissen Slot.** Synthetisch gebaut: 0 Kandidaten je Slot plus eine `unknowns`-Zeile (also nicht still, aber sechsmal dieselbe Teilausfall-Formulierung fuer einen Totalausfall). Am weissen Slot ist „of this colour" falsch — gemessen: zwei weggefallene rote Kopien, angeboten rot **und** blau. Latent (0 von 309 ohne Handle) | P3 | Minor | ui-ux-designer, director | synthetischer Bestand, zwei Faelle | offen | 2026-09-03 |
| QA-109 | `effect_ids_of` behauptet „the same three sources `Planner._rebuild` gathers, **in the same order**"; gemessen: gleiche Multimenge, **verschiedene Reihenfolge**. Ohne Wirkung auf eine Zahl (sources/warnings/attributes im Messzustand identisch), aber `Build.sources` ist per AD-015 die Quelle fuer S8 — und Pruefpunkt 13 schliesst mit `figures()` genau `warnings` und `sources` aus | P4 | Trivial | developer | Reihenfolgenvergleich am echten Planner | offen | 2026-09-03 |
| QA-110 | Pruefpunkt 18 („kein `QSettings` im Berater-Pfad") hat keinen Wächter: `test_no_source_opens_a_settings_store_of_its_own` prueft die **Namen** des Stores, nicht seinen **Ort** — ein `QSettings(favourites.ORG, favourites.APP)` unter `advisor/` passiert ihn. Eigenschaft haelt heute (zwei Suchen, 0 Treffer) | P4 | Minor | developer | Wächterlesung + zwei Suchen | offen | 2026-09-03 |
| QA-111 | **A8 („alle nutzersichtbaren Zeichenketten Englisch") hat repo-weit keinen Wächter** (zwei unabhaengige Suchen ueber `tests/`, 0 einschlaegige Treffer). Bestand in Ordnung: AST-Durchgang ueber `nrplanner/advisor/` findet nur Englisch, die von AD-010 verbotenen Woerter kommen nicht vor. Vorbestand, hier gemeldet, weil `advisor/` das erste Paket mit deutschen Kommentaren und englischen Ausgaben in derselben Datei ist | P4 | Minor | director, developer | AST-Durchgang + zwei Suchen | offen | 2026-09-03 |
| QA-112 | `inventory.copy_key`s Begruendung trifft den Code nicht (vom `developer` gemeldet, hier unabhaengig verifiziert): `read_relic_handles` liest aus dem **Relikt-Datensatz**, nicht aus der Loadout-Tabelle. Die zwei realen Wege zu `handle=None` stehen nirgends: (i) `read_relic_handles` schluesselt nach Handle, kollidierende Datensaetze kollabieren; (ii) `off < 0` wird uebersprungen. Gemessen: 0 handle-lose und 0 kollidierende Handles auf diesem Save. Klasse QA-082 | P4 | Trivial | developer | drei Stellen gelesen, Save nachgemessen | offen | 2026-09-03 |

**Bestaetigt, kein Befund (T-041):** die 15 Mutationen des `developer`
reproduzieren exakt; der AD-021-Wächter reicht wirklich in `advisor/`; die
Regression am Fenster ist null (18 Konfigurationen, 297 Zeilen, 0
Unterschiede); Pruefpunkt 15 ist ueber Objektidentitaet gesichert; die
Hashbarkeit ist auf der **Erzeugerseite** belegt; Farbregel und
Deep-Trennung sind an `inventory.relics_for` delegiert statt dupliziert;
`0 von 309` Relikten ohne Handle unabhaengig nachgemessen; die `slow`-Faelle
sind gruen (5 passed, alle in `test_extraction.py`, keiner beruehrt den
Berater); volle Suite mit `slow`: **403 passed**.


## Zyklus 12, T-049 (Scaling-Session, read-only): Startwaffen-Konversion (2026-09-03)

IDs vom Director vergeben. Quelle: `docs/berichte/T-049-qa-engineer.md`, Klon auf 0dc54a6.

Die Datei bestand bereits und wird fortgefuehrt; ich lege sie nicht selbst an.
**Zeile QA-101 ersetzen durch:**

| ID | Titel | Prio | Adressat | Status | Letzte Pruefung |
|---|---|---|---|---|---|
| QA-101 | **"Die Rangfolge waere bei `candidate` dieselbe" ist widerlegt.** Drei Effekte (7120400/500/600) tragen die Startwaffen-Strafe x0,85 selbst; ein Kandidat kann sie mitbringen. Gemessen: R0 `[7120400, 6001400]` → d(equipped) −12,36 gegen d(candidate) +21,36, R1 +0,83 in beiden → **Reihenfolge gedreht**. 10 von 309 Relikten des Saves betroffen. **Nachtrag T-049 (2026-09-03, Commit `0dc54a6`): auf dem Stand nach der 0,6-Kalibrierung ziffernweise reproduziert (Level 15 / Tier 1: 203,4176 / −12,3576 / +21,3589 vor der Kalibrierung; 122,0506 / −7,4146 / +12,8153 danach), Rangfolge dreht auf Level 1, 12 und 15. Ausserdem geprueft und bestaetigt: die drei Effekte tragen laut Params **nur** x0,85 (12 Zeilen im ganzen Spiel mit diesem Muster) und keine Schadensart-Umwandlung; Differenz Programm gegen Param-Lesart 0,000000 je Schadensart. Die Fan-Behauptung "~40-50 % AP werden umgewandelt" gehoert nicht zu ihnen — siehe QA-113.** | P2 | director, developer | offen — Entscheid des Directors | 2026-09-03 |

**Neue Zeile anhaengen (ID vom Audit-3-Director zu vergeben, Vorschlag QA-113):**

| ID | Titel | Prio | Adressat | Status | Letzte Pruefung |
|---|---|---|---|---|---|
| QA-113 | **Vier "Starting armament deals magic/fire/lightning/holy damage"-Relikte (7120000/100/200/300) bewegen die Angriffskraft um exakt 0.** Die Params tragen eine echte Umwandlung `physicsAttackPower −30/−40/−50/−60` mit `<element>AttackPower +33/+44/+55/+66`; die flachen `*AttackPower`-Felder haben in `model.compute` kein Fach und erscheinen im ganzen `nrplanner/` nur als Beschriftung (`effecttext.py` Z. 116-120) — drei unabhaengige Suchen. Gemessen Wylder Lv12: Programm 0,000000, Param-Lesart +1,80 (vor der 0,6-Kalibrierung) bzw. +3,00 (danach), Physics −18/−30 gegen Fire +19,8/+33. Auf dem Save 3 von 309 Relikten (`Night of the Beast`, `Delicate Drizzly Scene`, `Grand Luminous Scene`); in den Wuerfelpools 40 Eintraege je Effekt, genauso viele wie fuer die drei modellierten Geschwister. Rangfolge gedreht: 21 bzw. 75 echte Ueberholvorgaenge, 348/402 diskordante Paare von 47 586. Die Effektkarte nennt die Zahlen, die Angriffskraft nicht → beruehrt A3, A5 und A7. Kein Test im Repo nennt ein flaches `*AttackPower`. Einbauhoehe erst nach einer Ablesung im Spiel entscheidbar (drei Lesarten, 91 / 116 / 117 bei Grundwert 114) | P2 | developer, director | offen | 2026-09-03 |

| ID | Titel | Prio | Adressat | Status | Letzte Pruefung |
|---|---|---|---|---|---|
| QA-114 | `damage.py` Z. 61-63 (wortgleich `tests/weapon_damage_cases.py` Z. 163-166) nennt `*AttackPowerRate` "carried by exactly three effects — the 'Starting armament inflicts ...' relics" und verschmilzt damit die Feldaussage (richtig: 3 Effekte, 12 Zeilen) mit der Familienaussage (falsch: die Familie hat 7 Mitglieder, `stateInfo 2101` → genau 7 Zeilen im ganzen Spiel). Wirkung belegt: R-005 hat die Fan-Notiz zur Konversion auf diese drei bezogen und die vier Geschwister nicht gesehen | P4 | developer | offen | 2026-09-03 |

---


## Zyklus 12, T-045/T-050: die 0,6-Kalibrierung und ihr Beleg (2026-09-05)

Quelle: `docs/berichte/T-045-developer.md`. Vergleichslauf 89015aa gegen HEAD
ueber beide Raster, `PYTHONHASHSEED=0`, 115 839 exakte Zahlen und 589 840
Bildschirmzahlen. IDs vom Director vergeben.

**Bestaetigt, kein Befund:** 97 745 Zahlen um 0,6 mitgezogen (<= 1 ULP);
17 224 bitgleich stehengeblieben und **jede davon ein Multiplikator**;
0 von 589 840 Bildschirmzahlen ausserhalb von Abschneiden oder Runden;
0 von 121 924 gerenderten Gesamtzahlen widersprechen ihrer Quellzahl;
beide Mutationen selbst gefahren und rot (60 bzw. 26 failed).

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| QA-115 | **Eine Zahl im Quelltext ist nicht nachfahrbar — Verstoss gegen die eigene Hausregel (L-001).** Der Kommentar in `nrplanner/weapons.py` begruendet die Klammerung des Faktors mit "574 von 350 160 Werten kommen 2 ULP daneben heraus"; das Skript `dump_rate.py`, das die Zahl belegt, **existiert nicht** (`find`, `grep -rn`, `git log --all` je null Treffer). **Folge:** die **per-Typ**-Aussage der Klammerung ist unbelegt — der Vergleichslauf aus T-050 nimmt nur **Summen** auf und kann sie nicht stuetzen. Die Klammerung selbst ist dadurch nicht falsch, nur unbegruendet | P3 | Major | developer | drei unabhaengige Suchen, je 0 Treffer | offen | 2026-09-05 |
| QA-116 | **Der ueberholte Attack-Rating-Vorbehalt steht noch an sechs Stellen in zwei Wortlauten**, die eine Suche nach dem einen Satz nicht beide findet: `ARCHITECTURE.md:513`, `UI_SPEC.md:192, 1221-1222` (Wortlaut A) und `UI_SPEC.md:696, 981, 1201` (Wortlaut B). AK-37 und AK-50 binden damit Zeichenketten, die es im Programm nicht mehr gibt. **Entwarnung: keiner der beiden Wortlaute steht im Programmcode** — reine Dokumentenschuld | P4 | Minor | architect, ui-ux-designer | Volltextsuche ueber beide Wortlaute | offen | 2026-09-05 |
| QA-117 | **Die Anzeigeschwellen sind absolute Grenzen auf einer jetzt 0,6-mal kleineren Zahl.** Gemessen als Nebenwirkung der Kalibrierung: 89-mal faellt die Zeile `From attributes` weg (Schwelle `>= 0.5`, fuer alle 89 aus den Aufnahmen nachgerechnet), 66-mal wird eine Aenderungszelle `+1` zu `—`, einmal wechselt eine Farbe GOOD->MUTED (Schwelle `> 0.05`, armament 5050900). **Kein falscher Wert** — aber eine sichtbare Aenderung fuer den Nutzer, die niemand entschieden hat | P3 | Minor | ui-ux-designer, director | Skelettvergleich ueber `tiles_and_panel`, je Fall nachgerechnet | offen | 2026-09-05 |
| QA-118 | **`tests/test_move_scoped_effects.py` wurde in `99ed022` mitgeaendert, sichert aber nichts.** Seine **alte** Fassung ist gegen das **neue** Programm gruen (5 passed, auch der einzeln nachgefahrene Fall). Die Aenderung war richtig, ist aber keine Regressionssicherung — der Test haette den Faktor auch dann nicht bemerkt, wenn er falsch eingezogen worden waere. Klasse L-007 | P4 | Minor | developer | alte Fassung gegen neues Programm gefahren | offen | 2026-09-05 |


## Zyklus 12, T-046: Katalysator-Kennzahl (2026-09-05)

Quelle: `docs/berichte/T-046-developer.md`. 84/84 Fan-Zellen und 28/28
RPS-Zahlen exakt, fuenf toetende Mutationen gefahren, Messstrecke ueber beide
Raster: **0 Nicht-Katalysator-Datensaetze mit geaendertem Wert**, groesste
Abweichung 0 ULP. Suite 438 -> 563. IDs vom Director vergeben.

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| QA-119 | **QA-099a verschaerft: die Namenskollision Recluse's Staff ist jetzt sichtbar falsch.** Der Arsenal-Tab zeigt zwei gleichnamige Eintraege mit **128 und 151**, ununterscheidbar; vorher standen beide bei ~25 AR und fielen nicht auf. Die Id ist nur im Auswahldialog sichtbar. Drei unabhaengige Kriterien zeigen auf dieselbe Fremdzeile 33770000 (je 1 von 30). **Geltungsbereich des ersten Kriteriums:** nur *innerhalb* der Katalysator-Familie - 1 764 von 1 793 Waffen haben keinen Zauberplatz | P2 | Major | ui-ux-designer, developer | drei Kriterien je 1 von 30, am echten Datensatz | offen | 2026-09-05 |
| QA-120 | **Die Golden-Datei friert zwei ungemessene Aufstiegszahlen ein** (236, 184). Belegt ist ausschliesslich die **Basisraritaet**; catalyst_scaling waechst je Aufstiegsstufe monoton, die Stufenlogik ist ungeprueft. Eine Charakterisierung darf das - aber sie sagt es heute nicht, und der naechste Leser haelt eine eingefrorene Zahl fuer eine belegte | P3 | Minor | developer | Golden-Neuaufzeichnung gegen den Geltungsbereich aus T-043 | offen | 2026-09-05 |
| QA-121 | **Der Zusammenfassungssatz des Arsenal-Tabs (arsenaltab.py:306) definiert nur noch eine der beiden gezeigten Kennzahlen.** Seit Katalysatoren "Spell power" statt physischer AR zeigen, beschreibt der Satz die eine Haelfte des Bildschirms. AK-34 regelt diese Zeichenkette, deshalb vom developer **nicht** angefasst - Vorschlagstext liegt in seinem Bericht | P3 | Minor | ui-ux-designer | Codelesung gegen AK-34 | offen | 2026-09-05 |
| QA-122 | **Die Oberflaeche hat niemand gesehen.** Alle Qt-Laeufe dieses Zyklus waren offscreen. Ob "Spell power 237" in die 200-px-Arsenal-Kachel passt, ist ungeprueft - zusammen mit QA-117 (89 weggefallene From-attributes-Zeilen, 66 Strich-Zellen, ein Farbwechsel) ist das die erste Aenderung dieses Projekts, die den Bildschirm sichtbar umbaut, ohne dass jemand hingesehen hat. Luecke, kein Beleg | P2 | Major | ui-ux-designer | Selbstmeldung des developer, vom Director uebernommen | offen | 2026-09-05 |


## Zyklus 12, T-051: Retest der beiden Kalibrierungen (2026-09-05)

Quelle: `docs/berichte/T-051-qa-engineer.md`. **Alle 4 Abnahmepunkte aus
T-045 und alle 6 aus T-046 erbracht**, je mit unabhaengig reproduzierter Zahl
(Mutationslaeufe in frischen Klonen, Golden-Verhaeltnis von Grund auf neu
gerechnet, direkte Sonden an der Oberflaeche). Der zuvor offene Punkt ist
geschlossen: Wylder Lv12 / Dagger zeigt **74** auf Kachel ("Common - 74 AR"),
Tafel ("Total 74") und Arsenal-Tab ("AR 74") - gemessen an einer echten
headless `Planner`-Instanz. QA-118 gegen vier weitere mitgeaenderte
Testdateien geprueft: **Einzelfall, keine Klasse**. QA-115 bestaetigt: mit den
vorhandenen Werkzeugen **nicht** pruefbar, braucht ein neues Skript. QA-120
bestaetigt ueber das `left_out`-Feld der Datendatei selbst.

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| QA-123 | **Die Arsenal-Messstrecke ist fuer sechs Waffen blind.** Die Aufnahme wird ueber die Suche getrieben; bei sechs von 1793 Waffen ist die Familie groesser als die Auto-Aufklapp-Schwelle des Tabs, die Kachel wird nie gezeichnet und der Datensatz zaehlt trotzdem voll mit. Verwandt mit QA-088(b) | P4 | Minor | developer | 6 von 1793 ausgezaehlt, Kachel erzwungen gegengeprueft | offen | 2026-09-05 |
| QA-124 | **`arsenaltab.recalculate()` liest das angezeigte Level aus dem Slider-Widget statt aus dem Build.** In der Produktion harmlos (beide stimmen ueberein), fuer Testwerkzeug eine Falle: ein headless gesetzter Build ohne Sliderbewegung misst gegen ein anderes Level, als er zu messen glaubt. Genau die Wurzel von QA-088(a) | P4 | Minor | developer | Sonde mit abweichendem Slider- und Build-Level | offen | 2026-09-05 |


## Zyklus 13, T-055: Inhaltsaudit der sechs Tabs (2026-09-05)

Quelle: `docs/berichte/T-055-qa-engineer.md`. Grundlage GOAL A10 bis A14.
Alle Zahlen an headless instanziierten Tabs ausgelesen; zwei Belege aus einer
Direktlesung von `regulation.bin`. Suite vor und nach dem Lauf: 622 passed,
5 deselected. Kein Blocker. Keine Doppelmeldung zu DR-008..012,
QA-116/117/119/121/122/123/124.

**Bestaetigt, kein Befund:** die Everdark-Behauptung „identical figures"
(8 von 8 Paaren byteweise gleich) · die Begruendung, die fuenf elementaren
Deep-Raten zu einer Zeile zusammenzulegen (0 Abweichungen ueber 25 Profile x
5 Tiefen) · die beiden Erklaernoten zu Kataklysmen und Verschleierung
(Gewichte summieren zu 100) · `Avg > Best` in 0 von 652 Zeilen · die
Summenbildung im Red-variants-Tab ueber alle 6 Karten.

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| QA-125 | **Effects & chances: die Spalte `Pools` zaehlt keine Pools.** Der Tooltip sagt "How many of the game's loot pools can produce this effect"; die Zahl ist die Summe der (Relikt x Effektplatz)-Vorkommen. Zwei unabhaengige Belege: Identitaet 333 167 + 5 760 = **338 927** exakt aufgegangen; und das Spiel definiert nur **598** verschiedene Pool-Tabellen, waehrend der Tab bis **1 110** anzeigt | P2 | Major | developer, ui-ux-designer | Snapshot-Identitaet + Direktlesung `EquipParamAntique` | offen | 2026-09-05 |
| QA-126 | **Effects & chances: `Avg chance` ist ein ungewichtetes Mittel ueber Farb-/Modus-Eimer** und entspricht weder dem Tooltip ("averaged over every pool") noch der Zusammenfassung ("how likely … on one roll"). **129 von 616** Effekten aendern die angezeigte Zahl bei Gewichtung nach Vorkommen; schlimmster Fall `[Wylder] Improved Mind, Reduced Vigor` **20,4 % gegen 0,91 %** (Faktor 22,3) | P2 | Major | developer, ui-ux-designer | Nachrechnung ueber alle Effekte, Einzelfall aufgeschluesselt | offen | 2026-09-05 |
| QA-127 | **Effects & chances: `Copies` und `Tier` sind filterabhaengig**, obwohl beide Tooltips sie als Eigenschaft der Spieldaten beschreiben. Gemessen gegen "All colours": 25-39 Namen mit anderer `Copies`-Liste, 17-31 Namen, deren Leitersprosse verschwindet. **Entwarnung: keine Umnummerierung, 0 Faelle** ueber vier Farben und beide Modi | P3 | Major | developer | Filterdurchlauf ueber alle Farben und Modi | offen | 2026-09-05 |
| QA-128 | **Systemisch (A12): Zahlen ohne Bezugsgroesse auf fuenf der sechs Tabs.** 10 Belegstellen, u. a. `Scaling STR 50` auf **allen 1 792** Waffenkacheln (Einheit und Skala unbenannt; das Spiel zeigt hier Buchstabengrade), `Refills at x0.846` (Rate ohne Zeitbasis), `STATUS BUILDUP 542` (Richtung und Farblegende fehlen), `Reward multiplier x1.47` (**Bezugsgroesse auch im Code unbekannt -> A7-Fall**), `Enemy HP x1.30` (Vergleichsbasis fehlt) | P2 | Major | ui-ux-designer, developer, director | Belegliste mit Umfang je Stelle | offen | 2026-09-05 |
| QA-129 | **Nightlords: die Debuff-Zahlen stehen bei den falschen Bossen.** `DEBUFF_ON_BREAK` zeigt "x2.0 damage taken / x0.8 attack power" bei Gladius (Daten: 0,815), Caligo (**keine** Down-Stufe) und Heolstor (**keine**) - und **nicht** bei Harmonia und Straghess, deren Daten exakt 0,8 sagen. `ladder["down"]` wird fuer **7 von 10** Bossen nie gezeigt. Die Zeilen tragen die Typografie extrahierter Werte, obwohl der Tab fuer Sichtungen eine eigene Farbe fuehrt | P2 | Major | developer, ui-ux-designer | `ladder.down` aller 10 Bosse gegen die Konstantenliste | offen | 2026-09-05 |
| QA-130 | **Nightlords: Maris zeigt `Refills at x-1`.** `stance.recovery = -1.0` ist ein Sentinel und wird als Multiplikator gedruckt; die uebrigen neun liegen zwischen 0,154 und 1,462. Derselbe Waechter existiert im selben Modul fuer `>= 999` ("immune"), nur nicht fuer dieses Feld | P3 | Major | developer | Wert am Widget und im Datensatz | offen | 2026-09-05 |
| QA-131 | **Nightlords: Adels Schwaechen-Abschnitt erscheint nie.** Er ist der einzige Boss mit leerem `weak_damage` (Schwaeche liegt auf vier Status), und `if weak:` umschliesst auch `WEAKNESS_NOTE['Adel']` - die dafuer geschriebene Sichtung erreicht den Bildschirm nicht. Die gruene Markierung der Statusliste hat **keine Legende**; der einzige Ort, der "weakness" erklaert, ist der fehlende Abschnitt | P3 | Major | developer, ui-ux-designer | alle 10 Panels ausgelesen, `weak_status` gegengeprueft | offen | 2026-09-05 |
| QA-132 | **Red variants: `For example` ignoriert die gewaehlte Karte und ist fuer die groesste Zeile leer.** Identische Beispielnamen auf allen sechs Karten (die Rosterstruktur hat keine Kartendimension); `Ordinary enemies in camps & ruins` (32-38 von 87-134) und `Unidentified enemies` haben **0** benannte Mitglieder. Die Tabelle sagt ueber sich selbst "on the selected map" | P2 | Major | developer, ui-ux-designer | 6 Karten ausgelesen, Roster je Gruppe ausgezaehlt | offen | 2026-09-05 |
| QA-133 | **World Events: einmalige Belohnungen werden mit einer Dauer gedruckt.** `10,000 runes for 1s` (Buff 8970010, `part.duration = 1.0`) und `restores 100 stamina for 0.3s`. Beim Nachbarfall (`invulnerable for 5s`) ist dieselbe Regel richtig; der Code trennt Wirkdauer und Ausloesefenster nicht. Zusatz: beim `Judgment`-Buff steht `invulnerable` ganz ohne Dauer (`duration = 0.0`) | P2 | Major | developer | Buff-Teile aller 7 Buffs gegen den Bildschirmtext | offen | 2026-09-05 |
| QA-134 | **World Events: zwei Saetze stehen woertlich auf allen 11 Ereignissen**, und die Tagesverteilung wird dabei verworfen: `Judgment` hat 19 Day-1- gegen 1 Day-2-Muster, `Fire-Summoning Beasts` 9 gegen 21 - angezeigt wird ueberall "Can fire on Day 1 or Day 2". Dazu (A12): "Every other Nightlord: never" ist eine Allaussage ohne Geltungsbereich, und der Extraktor nennt die Prozentzahl ausdruecklich "not a spin probability" - das steht nicht auf dem Bildschirm | P3 | Minor | ui-ux-designer, developer | Gating-Daten aller 11 Ereignisse | offen | 2026-09-05 |
| QA-135 | **World Events: Herleitungssprache auf dem Bildschirm, gegen die Regel des eigenen Modulkopfs.** Wiki-Namen (fextralife, game8, Eldenpedia, thefifthmatt), "pattern modifier 230", "the row this project had wrong". Gleichzeitig werden `self.unknowns` und `self.rune_scaling` geladen und **nie** angezeigt - letzteres beziffert genau die auf dem Bildschirm stehende Behauptung "rises the more expeditions you have cleared" | P3 | Minor | ui-ux-designer, developer | Bildschirmtext gegen Modul-Docstring, Feldnutzung | offen | 2026-09-05 |
| QA-136 | **World Events: der `Scale-Bearing Merchant` steht zweimal in der Liste** - einmal als eigener community-berichteter Eintrag, einmal als Aufloesung von `Curse of the Demon` ("It is the Scale-Bearing Merchant"), ohne Verweis aufeinander | P4 | Minor | ui-ux-designer, director | Listeninhalt und beide Detailtexte | offen | 2026-09-05 |
| QA-137 | **Fuenf der sechs Tabs haben keinen Test, der Unsinn bemerken wuerde.** Sieben Anzeigemutationen gleichzeitig (u. a. Prozente zehnfach, Boss-Debuff x9.9, `WIN_RATING` 999, vertauschte Deep-Zeilen, falsches Tages-Gating) -> **622 passed, 5 deselected, unveraendert**. Kontrollmutation im Arsenal-Tab -> **6 failed**: die Strecke funktioniert. Suchbelege: Modulnamen 0 Treffer, Klassennamen 0 Treffer in `tests/`. **Herabgestuft von P1 auf P2**, weil kein Nutzer den Befund selbst ausloest - er ist die Ursache von QA-125 bis QA-136 | P2 | Major | developer, director | 7 Mutationen + 1 Kontrollmutation in frischen Klonen | offen | 2026-09-05 |
| QA-138 | **Drei der sechs Tabs sagen nicht, welche Frage sie beantworten** (A10). Deep of Night, Red variants und World Events oeffnen mit Ueberschrift und Erklaerabsatz; Effects & chances, Weapons & spells und Nightlords oeffnen mit einer Bestandszaehlung in Grau, 11 px | P3 | Minor | ui-ux-designer | Erstoeffnung aller sechs Tabs | offen | 2026-09-05 |
| QA-139 | **Derselbe Wert heisst auf einem Bildschirm zweimal anders:** die Kachel sagt `Spell power`, die Zusammenfassung sechs Zeilen darueber sagt "the **spell scaling** the game displays for them". Kein Widerspruch, ein Bezeichnungswechsel - entstanden beim Schliessen von QA-121/DR-010 aus zwei Richtungen (T-046 Kachel, T-053 Satz). AK-34 stellt diese Zeichenkette unter Wortlautkontrolle | P4 | Trivial | ui-ux-designer | Bildschirmtext beider Stellen | offen | 2026-09-05 |
```

**Beobachtung ohne eigene Nummer (gehört an QA-119):** der Auslöser aus QA-119
ist auf dem heutigen Datensatz nicht reproduzierbar — `Recluse's Staff` kommt
genau einmal vor (id 33750000, `Spell power 139`), auf allen vier
Aufstiegsstufen. Die Klasse besteht weiter: `Scholar's Thrusting Sword` (4×)
und `Finger Seal` (2×) tragen denselben Namen mehrfach, diesmal mit
**identischen** Zahlen. Ob QA-119 damit geschlossen ist oder sich nur der
Datensatz geändert hat, entscheidet der director.


## Statusfortschreibung des Directors, 2026-09-05 (nach T-053)

**Geschlossen durch T-053** (Commits 217796a bis 30a98bc, Suite 592 -> 622,
acht Mutationen gefahren und alle tot):

- **QA-119 / DR-008** — die nicht ausruestbare zweite `Recluse's Staff`-Zeile
  ist gefiltert. Erkennungsfeld `equipped_spells` neu, `EXTRACT_VERSION` 9->10.
  Geltungsbereich im Docstring von `model.is_unequippable_catalyst`: 1 von 30
  Katalysatoren, 1 von 1793 Waffen, 1764 ohne Zauberplatz. **Nebenbefund des
  developer, der im Review nicht stand:** bei Tier 1 stand die tote Zeile mit
  110 gegen 93 (Wylder) bzw. 151 gegen 128 (Recluse) **ueber** der echten
  Waffe und bewegte sich beim Aufstieg nie. Der `qa-engineer` hat in T-055
  gemeldet, dass der Ausloeser auf dem heutigen Datensatz nicht mehr
  reproduzierbar ist — **das ist die Wirkung des Fixes, kein Widerspruch.**
- **QA-121 / DR-010** — Arsenal-Zusammenfassungssatz nach AK-64 ersetzt.
- **QA-122 / DR-009, DR-012** — die Oberflaeche ist gesehen worden: zehn
  Screenshots vom gezeigten Fenster unter `docs/screenshots/2026-09-05/` und
  `.../2026-09-05-T053/`. Wortumbruch behoben, Schwellen benannt und gemessen.
- **QA-116** — ueberholter Vorbehalt in `UI_SPEC.md` nachgezogen
  (ui-ux-designer, zwei Nachtraege vom 05.09.).
- **QA-117** — Schwellen bleiben, sind aber jetzt benannt und ihre Wirkung ist
  gemessen statt geschaetzt (AK-65).

**Offen und ausdruecklich stehengelassen:** QA-113 (Einbauhoehe wartet auf die
Nutzermessung, Blindstelle ist benannt), QA-115 (mit **544** statt 574
geschlossen, siehe T-048), QA-120, QA-123, QA-124.


## Zyklus 13, T-059: Abnahme des Tab-Audits gegen A10 bis A14 (2026-09-05)

Quelle: `docs/berichte/T-059-qa-engineer.md`. Gemessen unter **beiden**
Plattformen und bei fuenf Fensterbreiten. **Urteil: A10 erfuellt (6 von 6),
A12 erfuellt fuer 4 von 6 Tabs, A13 fuer 3 von 6, A14 = dieser Bericht,
A11 offen** (braucht den zweiten `power-user`-Lauf). Von QA-125 bis QA-139
sind **13 behoben, 2 teilweise** — nachgemessen, nicht uebernommen. Sechs von
sechs nachgefahrenen Mutationen bestaetigen die berichteten Zahlen genau.
Build planner bei 513 px Fensterhoehe: **kein Befund**.

**Die Zusicherung, die den AK-77-Kompromiss traegt, haelt fuer die Zellen** —
26 949 gekuerzte Zellen ueber elf Kombinationen, **null** ohne vollen Text im
Tooltip. Sie haelt **nicht fuer die Spaltenkoepfe**: QA-140.

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| QA-140 | **Effects: Spaltenkoepfe mitten im Wort beschnitten; `vg chanc` gegen `est chanc` bei 1067 px** | P3 | Major | developer, ui-ux-designer | Screenshot + `sectionSize` bei 5 Breiten x 2 Plattformen | offen | 2026-09-05 |
| QA-141 | **Relic picker schneidet die 5. Kartenspalte schon bei seiner eigenen Startbreite an (11 von 55 Karten)** | P2 | Major | developer, director | Screenshot + gerenderte Rechtecke bei 1030/900/700 px | offen | 2026-09-05 |
| QA-142 | **`vs standard` ordnet seine Gruppen bei jedem Programmstart anders (`set`-Iteration)** | P3 | Minor | developer | 4 Hashseeds, 4 Reihenfolgen | offen | 2026-09-05 |
| QA-143 | **Weapons: Suche mit mehr als 60 Treffern zeigt wieder die leere Flaeche aus DR-017** | P3 | Minor | ui-ux-designer, director | Widget, 6 Sucheingaben | offen | 2026-09-05 |
| QA-144 | **Red variants: `Examples (any map)` bei 833 px breiter als `What can be red` (AK-99)** | P3 | Minor | developer | `sectionSize` bei 5 Breiten | offen | 2026-09-05 |
| QA-145 | **Nightlords: drei Bedeutungen auf `#6fbf73`, dazu `#7fae72` ohne Legende (AK-74)** | P3 | Minor | ui-ux-designer | gerendertes HTML, 10 Panels | offen | 2026-09-05 |
| QA-146 | **Waechter und Berichtszahlen messen unter `windowsvista`, das Programm laeuft unter `fusion` (bis 58 px Unterschied); offscreen kann 833 px gar nicht darstellen** | P3 | Minor | developer, director | dieselbe Messung unter 4 Kombinationen | offen | 2026-09-05 |
| QA-147 | **Nightlords bei 833 px: leeres Detailpanel haelt 330 von 833 px** | P4 | Minor | ui-ux-designer | Screenshot | offen | 2026-09-05 |
| QA-148 | **World Events: Runen-Leiter ohne Bezugspunkte, Satzrest nach dem Entfernen des Param-Namens** | P4 | Trivial | developer, ui-ux-designer | Bildschirmtext gegen Datensatz | offen | 2026-09-05 |
| QA-149 | **Nightlords: `IT BUFFS ITSELF` und `BODY PARTS` ohne Bezugsgroesse, die Nachbarabschnitte mit** | P4 | Minor | ui-ux-designer | 10 Panels | offen | 2026-09-05 |
