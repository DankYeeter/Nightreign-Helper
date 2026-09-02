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
| QA-018 | Waffen-/Arsenal-Tab zeigen andere AR als die Waffentafel (203,4 gegen 244,1) | P2 | Major | developer | echte Daten | **Ursache erklaert und gemessen (T-023), Fix haengt an einer Spielbeobachtung des Nutzers.** 203,4 x 1,2 = 244,1 - exakt der Multiplikatorunterschied. Zwei Schichten, nicht zwei Rechnungen | 2026-09-02 |
| QA-019 | Zwei Golden-Faelle pruefen nicht den Zweig ihres Namens; ein Zweig unabgedeckt | P3 | Minor | developer | echte Daten | offen | 2026-09-01 |
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
| QA-055 | **Achse B, der wahrscheinlichste Alltagsfall:** Slot auf Tier 3, Tab-Spinbox auf 1, **kein einziges Relikt** - Kachel und Tafel sagen 321,4, der Waffen-Tab 203,4. Reiner Eingabeunterschied, greift ohne jeden Buff, sobald der Spieler ein Slot-Tier hochsetzt. Das Tier, an dem die Liste rechnet, ist nirgends sichtbar | P2 | Major | developer, ui-ux-designer | gemessen ueber die echten Widgets | offen (neu aus T-023) | 2026-09-02 |
| QA-056 | **Achse C:** mit "Strength +1" zeigt die Kachel 323 (erhoehte Attribute), die linke Zahl der Tafel 321,4 (Grundattribute), der Tab 204,2 - drei Zahlen fuer dieselbe Waffe. Das ist die Beobachtung aus `DESIGN_REVIEW.md:429`, jetzt mit Ursache | P3 | Major | developer, ui-ux-designer | gemessen | offen (neu aus T-023) | 2026-09-02 |
| QA-057 | `nrplanner/weaponstab.py` ist **toter Code** - von keiner Datei importiert, `app.py:1342` bindet `ArsenalTab` an `self.weapons_tab`. 140 Zeilen, die dieselbe Rangliste ein zweites Mal rendern, **und sie sind bereits gedriftet**: Spinbox `setRange(0, 25)` gegen die Tier-Semantik 1..4; bei 0 rechnet sie still wie 1, bei 5-25 wie 4 | P3 | Minor | developer | kein Importeur im Baum | offen (neu aus T-023) - **genau die Form von Debt, die QA-001 erzeugt hat** | 2026-09-02 |
| QA-058 | Der `compute`-Waechter deckt `model.compute` ab, **nicht** `weapons.rate`. Die Waffen-Arithmetik hat zwei Schichten, und vier Anzeigestellen waehlen ihre Eingaben (Attributsatz, Tier, Multiplikatorschicht) unabhaengig. Zusaetzlich ist die Formel je Schadensart viermal ausgeschrieben (`damage.py:140`, `weaponstab.py:107`, `arsenaltab.py:368`, `app.py:2900`) | P3 | Major | developer, architect | Aufruferanalyse; drei unabhaengig gemessene Abweichungsachsen | offen (neu aus T-023) - **eigener Auftrag: zweiter Waechter oder gemeinsame Fassade** | 2026-09-02 |

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
