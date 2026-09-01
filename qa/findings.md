# QA-Befunde — Nightreign Helper

Quellen: T-002 (Zyklus 1, Erstaudit) und T-007 (Zyklus 2, Erstpruefung von T-006).
Geprueft gegen echte Spieldaten (`D:\SteamLibrary`, mit DLC) und zwei echte
Savefiles. Status: offen | teilweise behoben | behoben | zurueckgestellt

## Log

| ID | Titel | Prio | Sev | Adressat | Verifiziert | Status | Letzte Pruefung |
|----|-------|------|-----|----------|-------------|--------|----------------|
| QA-001 | Weapons-Tab rechnet anderen Build als der Planner | P1 | Major | developer | echte Daten | **behoben** — eine `compute`-Stelle, `current_build()`, Fluch-Build gegengeprueft | 2026-09-01 |
| QA-002 | Dasselbe physische Relikt in zwei Slots legbar und doppelt gezaehlt | P1 | Major | developer | echte Daten | **behoben** — interaktiv und ueber gespeicherte Builds; Restfall bei zwei Kopien eines Rolls → QA-021 | 2026-09-02 |
| QA-003 | Build-Namen ungeprueft im QSettings-Schluesselraum | P2 | Critical | developer | echte Daten | offen — **Release-Blocker** | 2026-09-01 |
| QA-004 | Mehrere Steam-Konten: das "vollste" Save gewinnt still | P2 | Major | developer, ui-ux-designer | echte Daten | offen | 2026-09-01 |
| QA-005 | Keine automatisierten Tests | P2 | Major | director, developer | verifiziert | **teilweise behoben** — 70 Tests, Restore-Pfade abgedeckt; `load_equipped` und Custom relic weiter unabgedeckt | 2026-09-02 |
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
| QA-018 | Waffen-/Arsenal-Tab zeigen andere AR als die Waffentafel (203,4 gegen 244,1) | P2 | Major | developer | echte Daten | offen — **Release-Blocker** | 2026-09-01 |
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
