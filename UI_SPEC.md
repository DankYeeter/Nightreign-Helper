# UI_SPEC — Nightreign Helper

Verbindliche Oberflaechen-Vorgaben, gegen die der `developer` baut und der
`qa-engineer` prueft. Ein `##`-Abschnitt je Auftrag, mit Datum. Bestehende
Abschnitte werden nie ueberschrieben — eine spaetere Korrektur bekommt einen
eigenen Nachtrag mit Begruendung.

Dokumentsprache ist Deutsch wie `GOAL.md` und `docs/state.md`. **Jede
Zeichenkette, die im Programm erscheint, steht hier woertlich auf Englisch**
und ist so zu uebernehmen (Projektregel, GOAL A8).

---

## Build Advisor (T-004) — 2026-09-01

### 0. Grundlage

Gelesen: `docs/tasks/T-004.md`, `GOAL.md`, `docs/state.md`, `README.md`,
`nrplanner/app.py`, `relicpicker.py`, `effectstab.py`, `arsenaltab.py`,
`firstrun.py`, `inventory.py`, `stacking.py`, `uiscale.py`, `effecttext.py`
sowie die Screenshots unter `docs/screenshots/` (angesehen: `build_planner.png`,
`effects.png`).

**Korrektur zur Auftragsbeschreibung:** T-004 und `GOAL.md` nennen die
Oberflaeche "Tkinter". Das Programm benutzt **PySide6 6.11.1 / Qt Widgets**
(`requirements.txt`, `app.py`); `tkinter` kommt im Quellbaum nicht vor. Alle
Vorgaben hier sind Qt-Widget-Vorgaben. Der Director hat den Irrtum am
2026-09-01 bestaetigt und zieht `GOAL.md` nach; "kein UI-Framework-Wechsel"
heisst also: bei Qt bleiben.

**Nicht live gesehen.** PySide6 ist im System-Python (3.12) nicht installiert
und es liegt kein Daten-Snapshot im Benutzer-Cache; ein Start haette eine
Abhaengigkeitsinstallation und einen Erstlauf-Build gegen die Spielinstallation
erfordert — beides Seiteneffekte auf einer Arbeitskopie, auf der zeitgleich
drei andere Rollen arbeiten. Grundlage sind daher Quelltext und die im Repo
mitgelieferten Screenshots. Kontrastwerte sind aus den Farbkonstanten in
`app.py` gerechnet, nicht vom Bildschirm gemessen.

---

### 1. Zweck & Nutzerziel

Der Spieler besitzt Hunderte Relikte (im Beleg-Screenshot: 292) und kann nicht
ueberblicken, welche Kombination ein benanntes Ziel am besten bedient. Der
Build Advisor beantwortet in einem Schritt: *"Welche Relikte aus meinem Besitz
fuellen die Slots dieses Kelchs am besten fuer `<Ziel>`, und warum?"* — ohne
dass etwas veraendert wird, bis der Spieler zustimmt.

---

### 2. Entscheidung: wo der Berater lebt

Drei Wege standen zur Wahl.

**(a) Eigener Tab "Advisor" — verworfen.**
Der Berater braucht Nightfarer, Vessel, Deep-of-Night-Schalter und Level als
Eingabe. Alle vier leben in der linken Spalte des Build planner. Ein eigener
Tab muesste sie entweder duplizieren (zwei Wahrheiten ueber denselben Zustand)
oder auf einen anderen Tab verweisen (der Spieler wechselt hin und her, um ein
Ergebnis anzuwenden). Zudem ist das Ergebnis eine Belegung genau der Slots, die
im Build planner sichtbar sind — es zwei Tabs entfernt anzuzeigen erzwingt das
Vergleichen aus dem Gedaechtnis. Achter Tab in der Leiste ohne Gegenwert.

**(b) Nur Markierung im Relic Picker — verworfen als alleiniger Weg.**
Der Picker (`relicpicker.RelicPicker`) ist ein **modaler Dialog pro Slot**.
Eine Empfehlung, die nur dort sichtbar ist, hat drei Bruchstellen: sie ist erst
zu sehen, nachdem der Spieler einen Slot geoeffnet hat — also nachdem er die
Entscheidung, die der Berater abnehmen soll, schon selbst getroffen hat; sie
kann keine Aussage ueber die **Menge** treffen, obwohl Ziel, Stacking-Regeln
und Slot-Farben nur ueber alle Slots zusammen sinnvoll sind (GOAL A3/A4); und
Warten, Fehler sowie "hierzu schweigt das Spiel" haetten in sechs modalen
Dialogen nacheinander erscheinen muessen. Als *alleiniger* Ort untauglich.

**(c) Gewaehlt: schmale Leiste im Build planner + Vorschlag im Slot +
Markierung im Picker.**
Genau eine Steuerstelle, das Ergebnis dort, wo es wirkt, und die Markierung im
Picker als Echo fuer den, der doch selbst waehlt.

| Ort | Traegt |
|---|---|
| **Advisor bar** — eine Zeile in der mittleren Spalte, oberhalb der Slots, nicht mitscrollend | Zielwahl, Ausloeser, Wartezustand, Ergebniszusammenfassung, Anwenden/Rueckgaengig, Zugang zur Begruendung |
| **Vorschlagsblock im Slot** — in jeder `RelicSlot`-Karte, nur solange ein Vorschlag lebt | Vorgeschlagenes Relikt, seine Effekte, seine Fluche, ein Satz Begruendung, "Use" fuer diesen einen Slot |
| **Karte im Relic Picker** — bestehende `RelicCard` | Kennzeichen "ADVISOR PICK", Karte fuehrt das Raster an |

Der Wunsch des Nutzers ("empfohlene Relikte direkt in der Relikt-Uebersicht
markieren") ist damit erfuellt, **aber eine Ebene frueher** als vorgeschlagen:
markiert wird zuerst im Slot selbst — dort steht das aktuell Bestueckte direkt
darueber, der Vergleich ist ein Blick — und zusaetzlich im Picker.

---

### 3. Aufbau

#### 3.1 Advisor bar

Position: mittlere Spalte des Build planner, **zwischen der Zeile "Build …"
und dem Hinweistext "Open a slot to choose a relic …"**, ausserhalb der
`QScrollArea` (der Wartezustand darf nicht wegscrollen).

Eine einzige Zeile, in dieser Reihenfolge:

```
ADVISOR  [ Maximise damage   v ]  [ Optimize ]   <status …>   [ Apply all ] [ Why ] [ Clear ]
```

- `ADVISOR` in der Schrift von `app._heading` (8 pt, fett, +1.2 Sperrung,
  `MUTED`), inline statt als Blockzeile.
- Zielwahl: `QComboBox`, `setSizeAdjustPolicy(AdjustToContents)`,
  `setMaximumWidth(200)`. Eintraege in dieser Reihenfolge:
  `Maximise damage`, `Minimise damage taken`. Bewusst eine Combobox und nicht
  zwei Knoepfe, damit weitere Ziele ohne Layoutaenderung dazukommen koennen.
- `Optimize`: `QPushButton`. Waehrend der Rechnung traegt derselbe Knopf
  `Cancel`.
- Statusbereich: `QLabel`, **darf zur Breite der Leiste nichts beitragen**
  (horizontal `QSizePolicy.Ignored`, Text bei Platzmangel per `QFontMetrics`
  auf `…` gekuerzt, ungekuerzter Text immer als Tooltip). Rechts daneben, nur
  waehrend der Rechnung, ein `QProgressBar` mit `setRange(0, 0)`,
  `setTextVisible(False)`, `setFixedHeight(6)`, `setMinimumWidth(0)` —
  dasselbe Muster wie `firstrun._Window`.
- Aktionsknoepfe rechts, **nie mehr als drei gleichzeitig sichtbar**:
  - kein Vorschlag: keiner
  - Vorschlag lebt: `Apply all`, `Why`, `Clear`
  - nach dem Anwenden: `Undo apply`, `Why`, `Clear`

Vertikales Budget: **hoechstens 32 px Inhaltshoehe bei UI scale "Automatic" auf
einem 100-%-Bildschirm**, plus 6 px Abstand oben und unten. Das ist der gesamte
Flaechenpreis des Beraters ausserhalb der scrollenden Slots.

#### 3.2 Vorschlagsblock im Slot

Erscheint innerhalb der `RelicSlot`-Karte unter `rolled_label`, **nur solange
ein Vorschlag lebt**. Rahmen `1px dashed ACCENT`, Radius 5, Hintergrund
`PANEL`, Innenabstand 8. Der gestrichelte Rahmen ist bewusst derselbe Griff,
den `CustomRelicCard` schon benutzt — gestrichelt heisst in diesem Programm
bereits "hypothetisch, noch nicht real".

```
SUGGESTED — MAXIMISE DAMAGE                                   [ Use ]
The Will of the Balancers
• Improved Melee Attack Power
• Improved Skill Attack Power
• Continuous FP Recovery
✦ <Fluchname>                                       (rot, nur wenn vorhanden)
Chosen for +15.0% Skill Attack Power and +6.0% all damage — the largest gain
of any Blue relic you own.
```

- Kopfzeile im `_heading`-Stil, `MUTED`; das Ziel wird mitgenannt, damit der
  Block auch nach dem Wegscrollen der Leiste fuer sich steht.
- Relikt- und Effektzeilen genau so formatiert wie im bestehenden
  `_sync_mode` — dieselben Aufzaehlungszeichen, dieselbe Farbe, dasselbe `⚠`
  fuer nicht stapelnde Effekte.
- **Fluche werden im Vorschlag genannt**, in `CURSE`, mit `✦`, mit demselben
  Tooltip wie `curse_tooltip`. Ein Vorschlag, dessen Preis erst nach dem
  Anwenden sichtbar wird, ist eine Falle.
- Begruendungssatz: **ein** Satz, `MUTED`, 11 px, `setWordWrap(True)`,
  hoechstens 160 Zeichen, in der Sprache des Statblatts (dieselben Feldnamen
  und Zahlenformate wie in `MULTIPLIERS` / `FLAT BONUSES`).
- `Use` wendet nur diesen einen Slot an.
- Ist der Vorschlag identisch mit dem, was bereits im Slot liegt, entfaellt
  alles ausser einer Zeile: `Already equipped — nothing to change here.`

#### 3.3 Markierung im Relic Picker

`RelicCard` bekommt einen optionalen Chip in der Kopfzeile, rechts neben dem
Namen: Text `ADVISOR PICK`, 10 px, Farbe `ACCENT`, kein Rahmen. Die Karte wird
im Raster **vor** die Favoriten sortiert, solange fuer diesen Slot ein
Vorschlag lebt.

**Kein vierter Rahmenfarbzustand.** Rahmen bedeuten im Picker bereits
"ausgewaehlt" (`ACCENT`) und "Favorit" (`FAVOURITE`); eine dritte Bedeutung
darauf zu legen macht die drei ununterscheidbar. Der Chip traegt Text, ist also
auch ohne Farbwahrnehmung lesbar.

Die Zusammenfassungszeile des Pickers bekommt einen Zusatz:

- normal: `  ·  the advisor's pick leads the grid`
- wenn der Filter die Karte ausblendet:
  `  ·  the advisor's pick is hidden by your filter`

#### 3.4 Dialog "Why"

Modaler `QDialog`, Titel `Why this build — <Ziel>`, `resize(640, 620)` wie
`CustomRelicDialog`, einziger Knopf `Close`. Inhalt in dieser Reihenfolge:

1. Kopf: Ziel, Nightfarer, Vessel, Deep of Night an/aus, wie viele Relikte
   betrachtet wurden.
2. Je Slot: Reliktname, darunter die Effekte, die den Ausschlag gaben, mit
   ihrem Beitrag im Format des Statblatts (`+15.0%`, `+1`).
3. Abschnitt `What could not be ranked` — Effekte ohne Zahlen (siehe 4.9).
4. Vorbehaltszeile, wo das Ziel auf Attack Rating beruht (README, "Known
   limits"): `Attack rating has not been verified against an in-game number.`

Kein `Apply` in diesem Dialog. Anwenden hat genau zwei Orte — die Leiste und
den Slot; ein dritter macht die Handlung unauffindbar statt zugaenglicher.

#### 3.5 Rich-Text-Sicherheit (Nachtrag Director, 2026-09-01)

Der `security-reviewer` hat im Bestand eine Markup-Injektion gefunden: Labels
laufen auf Qt-Voreinstellung `Qt.AutoText`, und Zeichenketten aus Save- und
Spieldateien werden per f-String ungefiltert in Rich Text interpoliert. Der
Berater fasst genau solche Zeichenketten an — Reliktnamen, Effektnamen,
Fluchnamen, den Nightfarer-Namen in 4.10, den Farbnamen in 4.11 — und wuerde
die Luecke sonst ein zweites Mal einbauen. Deshalb verbindlich:

- **Jedes** neue Label, jeder neue Tooltip und jeder Textbereich des Beraters
  setzt sein Format ausdruecklich: `setTextFormat(Qt.PlainText)`, wo keine
  Auszeichnung noetig ist, `setTextFormat(Qt.RichText)` nur dort, wo der Block
  seine Auszeichnung selbst erzeugt. Die `AutoText`-Heuristik entscheidet
  nirgends.
- In jedem `RichText`-Block wird **jede** aus Save- oder Spieldateien
  stammende Zeichenkette vor der Interpolation durch `html.escape()` geführt —
  Reliktname, Effektname, Fluchname, Vessel-Name, Nightfarer-Name,
  Fehlergrund. Auch dann, wenn sie heute harmlos aussieht.
- Tooltips zaehlen mit. Qt erkennt auch dort Rich Text selbsttaetig; ein
  Fluch-Tooltip aus `curse_tooltip` ist derselbe Weg.
- Wo Rich Text nur wegen Farbe oder Fettdruck gewaehlt wuerde, ist einfacher
  Text mit Stylesheet vorzuziehen. Der Vorschlagsblock braucht Rich Text nur
  fuer die Effektzeilen, die `_sync_mode` nachbilden.

---

### 4. Zustaende — vollstaendig

Jeder Zustand hat genau einen sichtbaren Ort: die Statuszeile der Leiste, bei
slot-spezifischen Aussagen zusaetzlich den Vorschlagsblock.

| # | Zustand | Statuszeile (woertlich) | Sonst |
|---|---|---|---|
| 4.1 | Ruhe, nie gerechnet | `Nothing suggested yet.` | Tooltip auf `Optimize`: `Fills every slot from the relics in your save. Nothing changes until you apply it.` |
| 4.2 | Rechnet, < 250 ms | *nichts* | keine Progressanzeige, kein Aufblitzen |
| 4.3 | Rechnet, ≥ 250 ms | `Working out maximise damage…` | Progressbar sichtbar, `Optimize` heisst `Cancel` |
| 4.4 | Rechnet, ≥ 3 s | `Working out maximise damage — 292 relics, 6 slots.` | Zahlen nur, wenn der Scorer sie liefert; sonst bleibt 4.3 stehen |
| 4.5 | Abgebrochen | `Stopped. Nothing was changed.` | Vorschlagsbloecke verschwinden |
| 4.6 | Ergebnis | `Maximise damage — 6 of 6 slots filled.` | Vorschlagsbloecke in allen Slots; `Apply all` / `Why` / `Clear` |
| 4.7 | Ergebnis veraltet (Nightfarer, Vessel, Deep, Level oder eine Slot-Belegung hat sich waehrend der Rechnung geaendert) | `Your build changed while this was working out — use Optimize again.` *(T-084, ersetzt `… working out. Optimize again.`)* | Ergebnis wird **verworfen**, nicht angezeigt |
| 4.8 | Kein Save gelesen (`owned is None`) | `No save was read, so there are no relics to choose from — use Rescan save.` | Zielwahl und `Optimize` deaktiviert |
| 4.9 | Teilweise stumm | `Maximise damage — 6 of 6 slots filled  ·  some effects carry no numbers.` | im `Why`-Dialog: `The game files carry no numbers for these, so they counted for nothing:` gefolgt von den Effektnamen |
| 4.10 | Ziel gar nicht bewertbar | `The game files carry no figures this goal can be ranked on for <Nightfarer>, so there is nothing to suggest.` | kein Vorschlagsblock; `Why` bleibt erreichbar und erklaert es lang |
| 4.11 | Keine Relikte fuer eine Slot-Farbe | `Maximise damage — 3 of 4 slots filled  ·  1 slot has nothing to choose from.` | betroffener Slot: `No <colour> relic in your save fits this slot.` |
| 4.12 | Rechnung schlug fehl | `Could not work that out — <kurzer Grund>.` | kein Stacktrace in der Oberflaeche |
| 4.13 | Angewendet | `Applied. Undo puts your slots back as they were.` | `Apply all` wird zu `Undo apply` |
| 4.14 | Sehr lange Reliktnamen, sehr viele Effekte | — | jede neue Beschriftung `setWordWrap(True)`; nichts wird abgeschnitten, nichts erzwingt Breite |

**4.9 und 4.10 sind nicht dasselbe** und duerfen nicht in einen Text
zusammenfallen: einmal schweigt das Spiel so, dass gar nichts gesagt werden
kann, einmal so, dass ein Teil der Kandidaten unbewertet blieb. Die Hausregel
(GOAL A7) verlangt beide Male eine Aussage, aber verschiedene.

---

### 5. Interaktion, Tastatur, Nebenlaeufigkeit

1. **Nichts aendert sich ohne Zustimmung.** `Optimize` schreibt in keinen Slot.
   Erst `Apply all` bzw. `Use` belegen Slots.
2. **Anwenden geht durch den bestehenden Weg**, den auch der Picker benutzt
   (`RelicSlot.relic_box.setCurrentIndex` → `_on_relic_changed` → `recompute`).
   Damit gelten Persistenz je Kelch, Neuberechnung des Statblatts und der
   Zustand der Build-Liste unveraendert weiter — der Berater erfindet keinen
   zweiten Weg, ein Relikt in einen Slot zu bekommen.
3. **`Undo apply` stellt die vorherige Slot-Belegung exakt wieder her**,
   einschliesslich eines vorher dort liegenden Custom relic und eines vorher
   leeren Slots. Verfuegbar, solange der Vorschlag lebt.
4. **Die Oberflaeche bleibt waehrend der Rechnung vollstaendig bedienbar**:
   kein modaler Dialog, kein `WaitCursor` ueber dem Fenster, kein Deaktivieren
   von Slots, Tabs, Nightfarer- oder Vessel-Auswahl. Muster: `QThread` +
   `moveToThread` wie in `firstrun.ensure_data`, aber ohne die dortige
   `processEvents`-Schleife — die gehoert zum Erstlauf-Fenster, nicht ins
   Hauptfenster.
5. **Ein ueberholtes Ergebnis wird nie angewendet** (4.7).
6. **Nur Relikte aus dem Besitz.** Nie "Custom relic", nie ein Relikt, das der
   Save nicht hergibt (GOAL A3).
7. **Tab-Reihenfolge**: Zielwahl → `Optimize`/`Cancel` → `Apply all`/`Undo
   apply` → `Why` → `Clear` → erster Slot. Innerhalb eines Slots liegt `Use`
   direkt hinter dem Reliktknopf des Slots.
8. Jede Aktion des Beraters ist ohne Maus erreichbar; jedes fokussierte
   Bedienelement zeigt den Fokus sichtbar (der Qt-Standardring genuegt, er darf
   nicht per Stylesheet entfernt werden).
9. **Die Suche bleibt unberuehrt.** `search.parse` und das Filterfeld des
   Pickers arbeiten unveraendert; die Advisor-Karte unterliegt demselben Filter
   wie jede andere und wird nicht davon ausgenommen.

---

### 6. Verwendete Token

Alles aus dem Bestand (`app.py`, `relicpicker.py`) — **kein neuer Farbwert,
keine neue Schriftgroesse.**

| Token | Wert | Verwendung im Berater | Kontrast auf `PANEL` |
|---|---|---|---|
| `ACCENT` | `#c8a45c` | Chip `ADVISOR PICK`, gestrichelter Rahmen des Vorschlags | 6,99:1 |
| `MUTED` | `#8a8a8a` | Kopfzeilen, Statuszeile, Begruendungssatz | 4,77:1 |
| `CURSE` / `BAD` | `#d1655f` | Fluche im Vorschlag | 4,50:1 |
| `GOOD` | `#6fbf73` | positive Betraege in der Begruendung, sofern verwendet | 7,35:1 |
| `PANEL` / `BORDER` | `#1e1f23` / `#2e2f35` | Flaeche und Rahmen | — |
| `_heading()` | 8 pt fett, +1.2 Sperrung | `ADVISOR`, `SUGGESTED — <Ziel>` | — |
| Fliesstext | 11 px | Effektzeilen, Begruendung | — |

Anmerkung fuer den `developer`: `CURSE` auf `PANEL` liegt mit 4,50:1 **exakt**
auf der WCAG-AA-Grenze. Fluchtext im Berater darf diese Farbe nicht abdunkeln
und nicht unter 11 px gesetzt werden. (Werte aus den Hex-Konstanten gerechnet,
nicht vom Bildschirm gemessen.)

---

### 7. Plattformkonventionen und kleine Bildschirme

Zielsystem Windows 10/11, Qt Widgets, dunkle Palette. Maus- und
Tastaturbedienung, keine Touch-Ziele.

Release 1.7.1 wurde von genau einem Fehler ausgeloest: **eine nicht umbrechende
Beschriftung setzte eine Mindestbreite von ~3900 px auf das ganze Fenster**
(Commit 7bf1f7e). Der Berater darf das nicht wiederholen. Daraus:

- Jede neue `QLabel` mit variablem Text: `setWordWrap(True)`.
- Kein neues Widget mit fester oder Mindestbreite ueber 200 px.
- Die Statuszeile traegt **nichts** zur Mindestbreite bei (siehe 3.1).
- Die Advisor bar darf die Mindestbreite der mittleren Spalte nicht ueber die
  der bestehenden "Build"-Zeile hinaus vergroessern.
- Die Vorschlagsbloecke liegen in der bestehenden `QScrollArea` der mittleren
  Spalte und wachsen deshalb nur in die Scrollhoehe, nicht in die
  Fenstermindesthoehe.
- Bei UI scale 125 % und 150 % (Werte aus `uiscale.CHOICES`) gilt alles Obige
  unveraendert; es wird kein Pixelwert hart gegen eine Skalierung gerechnet.

---

### 8. Akzeptanzkriterien

Pruefbar, binaer, vom `qa-engineer` gegen ein gebautes Artefakt (GOAL A9).

**Platzierung und Layout**

- **AK-01** Es gibt keinen neuen Tab. Die Tab-Leiste zeigt dieselben Tabs wie
  in 3da8428.
- **AK-02** Die Advisor bar steht in der mittleren Spalte des Build planner
  zwischen der "Build"-Zeile und dem Hinweistext und scrollt nicht mit.
- **AK-03** `Planner.minimumSizeHint().width()` ist nicht groesser als auf
  3da8428 (gleiche Umgebung, gleiche UI scale, gemessen vor dem ersten
  `show()`).
- **AK-04** Die Mindesthoehe des Fensters waechst um hoechstens 44 px
  gegenueber 3da8428.
- **AK-05** Bei Fensterbreite 1320 px (Startbreite) ist in der Advisor bar
  kein Text abgeschnitten ausser der Statuszeile, und deren voller Text steht
  im Tooltip.
- **AK-06** Mit UI scale 150 % und sechs belegten Deep-of-Night-Slots samt
  lebendem Vorschlag entsteht in der mittleren Spalte keine horizontale
  Bildlaufleiste.
- **AK-07** Zu keinem Zeitpunkt sind mehr als drei Aktionsknoepfe der Advisor
  bar gleichzeitig sichtbar.

**Verhalten und Nebenlaeufigkeit**

- **AK-08** Waehrend einer laufenden Rechnung lassen sich Nightfarer wechseln,
  Vessel wechseln, ein Slot oeffnen und der Tab wechseln; kein Bedienelement
  ausserhalb der Advisor bar ist deaktiviert, es erscheint kein modaler Dialog
  und kein Wartecursor ueber dem Fenster.
- **AK-09** Eine Rechnung unter 250 ms zeigt weder Fortschrittsbalken noch
  Wartetext (kein Aufblitzen).
- **AK-10** Eine Rechnung ueber 250 ms zeigt Fortschrittsbalken und Wartetext,
  und `Optimize` traegt `Cancel`.
- **AK-11** `Cancel` fuehrt binnen 200 ms nach dem Klick sichtbar in Zustand
  4.5, auch wenn der Arbeiter laenger zum Beenden braucht.
- **AK-12** Aendert sich Nightfarer, Vessel, Deep of Night, Level oder eine
  Slot-Belegung waehrend der Rechnung, wird das Ergebnis verworfen und 4.7
  angezeigt. Es wird nie ein Vorschlag zu einem Zustand gezeigt, der nicht mehr
  gilt.
- **AK-13** `Optimize` veraendert keinen Slot: nach `Optimize` ohne Anwenden sind
  Slot-Belegung, Statblatt und der Eintrag der Build-Liste unveraendert.
- **AK-14** Nach `Apply all` zeigt das Statblatt die angewendeten Relikte, und
  der Zustand ist derselbe, als waeren die Relikte einzeln im Picker gewaehlt
  worden — Persistenz je Kelch inbegriffen.
- **AK-15** `Undo apply` stellt die vorherige Belegung exakt wieder her, auch
  einen vorher leeren Slot und ein vorher dort liegendes Custom relic.
- **AK-16** Kein Vorschlag enthaelt jemals ein Custom relic oder ein Relikt,
  das nicht in `owned` steht.
- **AK-17** Der Berater schreibt nicht in den Save und oeffnet keine
  Netzwerkverbindung.

**Aussage und Hausregel**

- **AK-18** Jeder Slot-Vorschlag traegt genau einen Begruendungssatz in
  Nutzersprache, der mindestens einen konkreten Effekt beim Namen nennt
  (GOAL A5).
- **AK-19** Traegt das vorgeschlagene Relikt Fluche, sind sie im
  Vorschlagsblock genannt — in `CURSE` und mit `✦` — bevor angewendet wird.
- **AK-20** Kann das Ziel gar nicht bewertet werden, erscheint 4.10 und **kein**
  Vorschlag. Es wird nie eine Rangfolge gezeigt, die auf fehlenden Daten beruht
  (GOAL A7).
- **AK-21** Blieben Kandidateneffekte unbewertet, weil die Spieldateien keine
  Zahlen tragen, sagt die Statuszeile das (4.9) und der `Why`-Dialog nennt die
  betroffenen Effekte namentlich.
- **AK-22** Beruht das Ziel auf Attack Rating, steht der Vorbehalt aus den
  "Known limits" genau einmal im `Why`-Dialog — nicht je Zeile.
- **AK-23** Alle vom Berater gezeigten Zeichenketten sind Englisch (GOAL A8).
- **AK-24** Der Berater respektiert Slot-Farben, Stacking-Regeln und die
  Deep-of-Night-Kennzeichnung: ein Vorschlag enthaelt kein Relikt, das der
  Picker fuer denselben Slot nicht anbieten wuerde (GOAL A4).

**Tastatur und Suche**

- **AK-25** Jede Aktion des Beraters (Zielwahl, Optimize, Cancel, Apply all, Use
  je Slot, Why, Clear, Undo apply) ist allein mit Tab / Umschalt+Tab und
  Enter / Leertaste erreichbar und ausloesbar.
- **AK-26** Die Tab-Reihenfolge entspricht 5.7; der Fokusring ist auf jedem
  neuen Bedienelement sichtbar.
- **AK-27** Der Filter im Relic Picker liefert mit lebendem Vorschlag dieselben
  Treffermengen wie ohne; die Advisor-Karte ist nicht vom Filter ausgenommen,
  und wird sie ausgefiltert, sagt die Zusammenfassungszeile das.
- **AK-28** Die Advisor-Karte im Picker traegt den Text `ADVISOR PICK`; die
  Rahmenfarben fuer "ausgewaehlt" und "Favorit" bleiben unveraendert und
  bekommen keine dritte Bedeutung.

**Rich-Text-Sicherheit**

- **AK-29** Jedes vom Berater neu eingefuehrte Label, jeder Tooltip und jeder
  Textbereich setzt `setTextFormat()` ausdruecklich. Kein neues Textelement
  laeuft auf `Qt.AutoText`. Pruefbar per Grep ueber die neuen Widgets: zu jedem
  `setText(` auf einem neuen Element existiert ein `setTextFormat(`.
- **AK-30** Ein Relikt, dessen Name die Zeichenkette
  `<b>x</b><img src=x>&lt;` enthaelt, erscheint im Vorschlagsblock, im
  `Why`-Dialog, in der Statuszeile und im Tooltip **buchstabengetreu** — kein
  Fettdruck, kein verschluckter Teil, keine geladene Ressource. Dasselbe fuer
  einen praeparierten Effekt- und Fluchnamen. (Testweg: manipulierter
  Snapshot-Eintrag; der `qa-engineer` legt den Testfall an.)

---

### 9. Ausdruecklich nicht Teil dieser Vorgabe

- **Die Scoring-Algorithmen.** Was "maximise damage" rechnet, legt der
  `architect` fest (T-001). Diese Vorgabe schreibt nur vor, in welcher Form das
  Ergebnis, seine Begruendung und sein Schweigen erscheinen.
- **Antwortzeit-Budgets.** Die 250-ms- und 3-s-Schwellen sind Anzeigeregeln,
  keine Leistungszusagen. Das Rechenbudget setzt der `performance-tuner`
  (GOAL A6).
- **Escape als Abbruch** waehrend der Rechnung — nicht spezifiziert, weder
  gefordert noch verboten.
- Weitere Ziele ueber die zwei geforderten hinaus.
- Ein Merken der zuletzt gewaehlten Zielrichtung ueber Programmstarts hinweg.
- Aenderungen an anderen Tabs. Der Berater erzwingt keine.

---

### 10. Offene Fragen an den App Designer

- **F1 — Slots festhalten.** `Apply all` ueberschreibt auch Slots, die der
  Spieler bewusst von Hand belegt hat. `Undo apply` faengt das auf, aber der
  eigentliche Wunsch waere oft "rechne die uebrigen Slots um diesen einen
  herum". Soll ein Slot festgehalten werden koennen (kleines Schloss in der
  Slot-Kopfzeile), oder bleibt es bei Alles-oder-Rueckgaengig? Produkt-
  entscheidung mit Folgen fuer den Algorithmus, deshalb nicht hier entschieden.
- **F2 — Anwenden oder Vorschau.** Soll `Apply all` sofort belegen (so
  spezifiziert), oder soll das Statblatt den Vorschlag *vorher* rechnen und
  neben den aktuellen Werten zeigen? Letzteres beantwortet "lohnt es sich?"
  ohne Umweg, kostet aber eine zweite Zahlenspalte im rechten Statblatt und
  damit Flaeche, die 1.7.1 gerade erst geordnet hat.
- **F3 — Fluche als Ausschlusskriterium.** Soll der Berater verfluchte Relikte
  grundsaetzlich mitbewerten (so spezifiziert: ja, mit sichtbarem Fluch), oder
  soll es einen Schalter "ohne Fluche" geben?
- **F4 — Name.** `Advisor` ist gesetzt, weil kurz und in der Leiste tragbar.
  Alternativen waeren `Suggest a build` oder `Build advisor`. Reine
  Geschmacksfrage, aber sie steht dauerhaft auf dem Bildschirm.
  *(T-084, 07.09.2026: hier geht es um den Namen des **Bereichs**, nicht um
  den Knopf. Der Knopf heisst seit T-024 §5.1 `Optimize` — die beiden Woerter
  `Suggest a build` oben sind ein verworfener Bereichsname, keine
  Knopfbeschriftung. AK-176.)*

---

## Die Sprache der Zahlen, und der Relic Picker (T-024) — 2026-09-02

### 0. Grundlage, Methode, und was davon **gesehen** ist

Gelesen: `docs/tasks/T-024.md`, `GOAL.md` (F1–F4, OF-12/13/15), `docs/state.md`
(Fassung vom 2026-09-02, einschliesslich des waehrend dieser Arbeit
nachgezogenen Abschnitts zu AD-019), `ARCHITECTURE.md` **AD-014 bis AD-021**,
`qa/findings.md` QA-018/055/056/058, `DESIGN_REVIEW.md` (DR-001 bis DR-007),
sowie `nrplanner/relicpicker.py`, `arsenaltab.py`, `weaponslots.py`,
`damage.py`, `weapons.py` und `app.py` (`RelicSlot`,
`_refresh_weapon_damage`, `_show_ar_breakdown`).

**Der `architect` hat AD-019 bis AD-021 waehrend dieser Spec veroeffentlicht.**
Teil 1 ist daraufhin **neu geschrieben** worden; ein erster Entwurf, der die
heutigen Rechenschichten benannt haette (`AR before attack buffs` fuer die
Waffenkachel), waere nach Schritt W3 falsch gewesen, weil die Kachel dann
dieselbe Frage beantwortet wie die Tafel. Die Benennung unten folgt der
`Basis`-Aufzaehlung aus AD-019 und benennt **Fragen**, nicht Schichten.

**Methode — und zum ersten Mal in diesem Vorhaben mit Bild.** Die Widgets
wurden offscreen (`QT_QPA_PLATFORM=offscreen`, zusaetzlich
`QT_QPA_FONTDIR=C:/Windows/Fonts`; ohne das zweite rendert Qt nur
Tofu-Kaesten) gegen die echte Snapshot-Datei des Nutzers gebaut und per
`QWidget.grab()` als PNG abgezogen. Kein Anwendungscode wurde angefasst; die
Skripte lagen im Scratchpad, die Bilder liegen unter
`design-review/2026-09-02/`.

**Visuell belegt** (angesehen, nicht erschlossen):

| Beleg | Was daraus feststeht |
|---|---|
| ![Relic Picker, Ist-Zustand](design-review/2026-09-02/picker-before.png) | Kartenraster 5 Spalten, Karte 190×145–181 px, Zeilenabstand 161 px; Effektzeilen brechen regelmaessig auf zwei Zeilen um; Fluchzeilen in Rot; die Custom-Karte fuehrt; **am Standardmass des Dialogs erscheint eine waagerechte Bildlaufleiste** |
| ![Arsenal-Tab, Ist-Zustand](design-review/2026-09-02/arsenal-before.png) | Die Zusammenfassung ist **ein** dichter Prosablock, in dem Held, Level, Tier („+1"), Attribute, Trefferzahl, AR-Definition, 60-%-Vorbehalt und Zauberhinweis hintereinander stehen |
| ![Beschriftungsprobe Arsenal-Kachel](design-review/2026-09-02/tile-label-fit.png) | Die gepruefen Zeilenbeschriftungen — darunter **`AR at +1`** — passen **einzeilig** in die 200-px-Kachel, ohne Umbruch und ohne den Wert zu beschneiden |

**Gemessen, nicht geschaetzt:** Sichtbereich des Picker-Rasters 988 px gegen
1000 px Inhalt — **12 px zu breit**, daher die Bildlaufleiste. Sichtbar sind
am Standardmass rund 19 Karten (3,8 Zeilen à 5).

**Nicht visuell belegt, ausdruecklich:**
- **Die Farben im Arsenal-Beleg.** Das dunkle Stylesheet haengt an der
  `QApplication` in `app.py`; im isolierten Aufbau fehlt es, das Bild ist
  hell. Ueber Farbe sagt dieser Beleg **nichts**.
- Der Build-planner-Bildschirm als Ganzes, die sechs Waffenkacheln, die
  Schadenstafel darunter und die Advisor bar (letztere existiert noch nicht).
  Alle Aussagen dazu sind **Codelesung**.
- **Die Schriftmasse.** Offscreen laeuft eine Ersatzschrift, nicht Segoe UI.
  Segoe UI ist breiter. Alle Zeichenbreiten sind deshalb **Untergrenzen**;
  verbindlich sind die Umbruch- und Elidierregeln, nicht die Pixelzahlen.
- Kein Kontrastwert ist vom Bildschirm gemessen; alle sind aus den
  Hex-Konstanten gerechnet (Werte unveraendert gegenueber §6 oben).

---

### 1. Nachtrag zu T-004: was aus der Vorgabe vom 2026-09-01 herausfaellt

Der Nutzer hat am 2026-09-02 die Fragestellung verworfen, gegen die §2 bis §4
oben geschrieben wurden (GOAL F2). Die betroffenen Stellen werden **nicht
geloescht**, sondern hier eingeschraenkt:

- **§3.3 und AK-28 (`ADVISOR PICK`-Chip) werden zurueckgezogen.** Sie waren
  das Echo eines Gesamtvorschlags im Picker. Der Picker traegt jetzt selbst
  Zahlen; ein Chip, der nur „der Berater meint das hier" sagt, waere neben
  einer Zahl, die das begruendet, redundant — und er behauptete genau die
  strenge Rangfolge, die es laut T-024 nicht gibt. Ersatz ist die
  gleichstandsfaehige Kennzeichnung in §3.5.
- **Geltungsbereich von AK-22 eingeschraenkt** (keine Neudefinition, nur eine Einschraenkung der bestehenden Nummer): „Der Vorbehalt steht genau
  einmal im `Why`-Dialog, nicht je Zeile" gilt weiter **fuer den
  `Optimize`-Lauf und seinen `Why`-Dialog**. Fuer den Picker gilt er nicht:
  dort steht neben jeder Karte eine eigene Zahl, und eine Zahl ohne ihren
  Vorbehalt ist eine Behauptung. **Meine eigene Vorgabe war hier zu grob** —
  sie kannte nur eine Bauform des Ergebnisses.
- **§3.1 bleibt**, mit einer Aenderung: der Knopf heisst `Optimize` statt
  `Suggest` (GOAL F4), und die Zielwahl der Leiste ist ab jetzt die
  **einzige** Zielwahl des Programms (§5.2).
- **§3.2 (Vorschlagsblock im Slot) bleibt** — er gehoert zum
  `Optimize`-Ergebnis, nicht zum Picker.

---

### 2. Teil 1 — drei Fragen, drei Namen

#### 2.1 Warum nicht „drei Schichten"

Der Textvorschlag des `developer` (`"AR"` → `"Base AR"` im Arsenal-Tab) haette
den Widerspruch **verlegt statt aufgeloest**: das Wort `Base` ist im Programm
bereits vergeben — die Aufschluesselung in `_show_ar_breakdown`
(`app.py:2817`) nennt so die Zahl an den **Grundattributen**, waehrend der
Arsenal-Tab an den **erhoehten** Attributen rechnet. Zwei Groessen, ein Wort.

Und eine Benennung nach Rechenschichten (`… before attack buffs`) waere nach
**W3/W4 aus AD-019 falsch**: dort wird die Waffenkachel auf dieselbe Frage
umgestellt wie die Tafel (`Basis.EQUIPPED`, AD-020 Punkt 6), und ob die
Multiplikatorschicht zum Arsenal-Tab gehoert, ist bis **W6** offen
(`MULTIPLIERS_FOR[Basis.CANDIDATE]`).

Deshalb wird nach **Fragen** benannt, nicht nach Schichten. Eine Frage aendert
sich durch die Spielmessung nicht — nur ihre Antwort. Das ist die Auflage aus
T-024 („benennt, *was* eine Zahl misst, nicht dass sie stimmt"), und es ist
zugleich die einzige Benennung, die die Spielmessung **unter beiden
Ausgaengen** ueberlebt.

#### 2.2 Die Benennung (verbindlich)

Eins zu eins auf `damage.Basis` aus AD-019 — der `developer` hat nichts zu
uebersetzen:

| `Basis` | Die Frage | Name in der Oberflaeche (woertlich) |
|---|---|---|
| `BARE` | Was traegt die Waffe an den Attributen deines Levels, ohne alles Ausgeruestete? | **`AR without relics`** |
| `EQUIPPED` | Was traegt **diese** Waffe in **diesem** Slot, so wie sie steht? | **`AR as equipped`** |
| `CANDIDATE` | Was traege **irgendeine** Waffe, wenn du sie auf `+N` braechtest und anlegtest? | **`AR at +N`** (z. B. `AR at +1`) |

Drei Eigenschaften, die diese Namen haben und die Schichtnamen nicht haetten:
- Kein Name behauptet Richtigkeit oder ein Verhaeltnis zum Spiel.
- Kein Name wird durch W6 falsch. Aendert sich
  `MULTIPLIERS_FOR[Basis.CANDIDATE]`, aendert sich der **Wert** hinter
  `AR at +1`, nicht sein Name.
- **`AR at +N` traegt sein Tier im Namen.** Damit ist QA-055 an der Kachel
  selbst geschlossen, nicht in einer Zusammenfassung drei Bildschirmhoehen
  weiter oben. Visuell belegt, dass es passt: `tile-label-fit.png`.

#### 2.3 Wo welcher Name steht

**(a) Arsenal-Kachel** (`arsenaltab.py:366`). Die Kopfzeile der Zahlenliste
heisst `AR at +1` und folgt der Spinbox `Upgrade to +`. Die Zeilen `Rarity`
und `Upgraded to` bleiben unveraendert — der Tier steht jetzt in der
Kopfzeile, es braucht keine weitere Zeile.

**(b) Waffenkachel im Build planner** (`weaponslots.py:228`). Text
unveraendert: `Common +1 · 203 AR · 2 effects`. **Nach W3 ist das zulaessig**,
weil Kachel und Tafel dann dieselbe Frage beantworten und dieselbe Zahl zeigen
(AD-020 Punkt 6) — ein bloßes `AR` ist im Build planner dann eindeutig. Die
Detailzeile ist bei sechs Kacheln in einer schmalen Spalte ohnehin zu eng fuer
den vollen Namen (Codelesung: 3×2-Raster, 10 px, `setWordWrap(True)`).

**Verbindliche Reihenfolge:** Diese Beschriftung darf **erst mit W3**
ausgeliefert werden. Vorher zeigt die Kachel eine andere Zahl als die Tafel,
und ein unqualifiziertes `AR` waere dann genau die Behauptung, die QA-018
ausmacht.

**(c) Bildunterschrift im Build planner**, `MUTED`, 11 px,
`setWordWrap(True)`, zwischen dem Kachelraster und der Schadenstafel, stets
sichtbar, **kein** Tooltip, **nicht** aufklappbar:

> `Your armaments as you have them equipped, each at its own upgrade. The Arsenal tab rates every armament at one chosen upgrade instead.`

Zwei Saetze, zwei Aufgaben: der erste benennt die Frage dieses Bildschirms,
der zweite verhindert, dass der Wechsel auf den Arsenal-Tab als Widerspruch
gelesen wird.

**(d) Schadenstafel.** Die Gesamtzeile traegt beide Namen sichtbar, ohne
Hovern:

> `AR without relics  321   →   AR as equipped  323   (+2, +0.6%)`

Die Differenz bleibt der anklickbare Verweis auf die Aufschluesselung
(`AR_BREAKDOWN_KEY`). Dort heissen erste und letzte Zeile genauso; `Base` wird
zu `AR without relics`, `From attributes` zu
`What your relics add to your attributes`, `Total` zu `AR as equipped`.

**(e) Arsenal-Zusammenfassung.** Aus einem Prosablock werden **zwei** Labels.

Label 1 — Kontext, scannbar:

> `Wylder at level 1 · every armament rated at +1 · VIG 8  MIN 4  END 3  STR 5  DEX 4  INT 2  FAI 2  ARC 10 · 1953 shown`

Label 2 — was die Zahl ist und was sie nicht ist. Der mittlere Satz hat **zwei
zugelassene Fassungen**, und welche gilt, entscheidet nicht der Text, sondern
`MULTIPLIERS_FOR[Basis.CANDIDATE]`:

> `AR at +1 — every armament rated as if you took it to +1 and put it on, at your attributes including what your relics add to them.`
> **Fassung A** (`MULTIPLIERS_FOR[Basis.CANDIDATE] is False`): `The +% attack effects your relics grant are not counted here; the Build planner counts those for what you have equipped.`
> **Fassung B** (`… is True`): `The +% attack effects your relics grant are counted here as well.`
> `A buff that lifts only one weapon class can change the order between classes. Not checked against the game's own attack-power display. Spells carry no damage figures in the game's data, so they show their costs instead.`

Das ist die Stelle, an der die Spielmessung in der Oberflaeche ankommt: **ein**
Satz wechselt, weil **eine** Konstante wechselt. Nichts anderes.

#### 2.4 Der 60-%-Satz: **faellt weg**

Heute (`arsenaltab.py:308-311`): *„The in-game panel has been seen showing
about 60% of these figures (under investigation); the ranking between weapons
is unaffected."* Beide Haelften gehen, aus verschiedenen Gruenden:

- **„about 60% … (under investigation)"** behauptet eine Verhaeltniszahl, die
  das Projekt nicht belegen kann — `docs/state.md` haelt fest, dass gegen das
  laufende Spiel nichts verifiziert ist. Sie behauptet ausserdem, der Versatz
  sei **bekannt und konstant**; nach T-023/AD-019 ist er das nachweislich
  nicht, er haengt an drei unabhaengigen Achsen zugleich (Tier, Attributsatz,
  Multiplikatorschicht). Das verstoesst gegen A7 in der schaerferen Richtung:
  nicht Schweigen, sondern eine unbelegte Zahl.
- **„the ranking between weapons is unaffected"** ist **falsch**, belegbar aus
  dem eigenen Code: `damage.py` liest `build.class_rates` ueber
  `model.WEAPON_CLASS_PREFIX`, und AD-020 Punkt 4 haelt ausdruecklich fest,
  dass klassengebundene Raten **je Waffe verschieden** sind. DR-003 hatte das
  schon benannt. Ersatz ist die wahre, engere Aussage in Label 2.

Uebrig bleibt eine Aussage ueber Unwissen statt ueber eine Groesse:
`Not checked against the game's own attack-power display.` Eine Zahl kommt
zurueck, sobald eine Messung mit Aufbau, Datum und Ergebnis aufgeschrieben ist
— nicht als „has been seen".

**Das ist eine Entscheidung ueber eine Beobachtung des Nutzers** und steht
deshalb zusaetzlich in §9 als offene Frage.

---

### 3. Teil 2 — der Relic Picker als Hauptweg des Beraters

#### 3.1 Zweck

Der Picker beantwortet: *„Was bringt mir **dieses** Relikt **jetzt**, in
**diesem** Slot, so wie mein Build gerade steht?"* Der Wert ist der
Grenzbeitrag aus AD-018.1. Der abnehmende Ertrag, nach dem der Nutzer gefragt
hat, ist keine eigene Anzeige — er **ist** die Zahl, weil sie an einer
konkaven Kurve gemessen wird.

#### 3.2 Aufbau, von oben nach unten

Die bestehende Ordnung bleibt; es kommen eine Steuerzeile und eine Textzeile
dazu, beide **ausserhalb** der `QScrollArea` (sie duerfen nicht wegscrollen).

```
[●] [ Filter by effect…                                  ] [ Empty slot ]
Sort by [ Maximise damage        v ]
29 of 29 relics  ·  ranked against your build with Slot 3 empty  ·  right-click a relic to favourite it
One slot at a time — some relics only pay off together; Optimize on the Build
planner looks for those. Attack rating has not been checked against the game,
so these figures may be wrong.
──────────────────────────────────────────────────────────────  (Raster)
```

- **Zeile 3** ist die heutige Zusammenfassung, um die **Bezugsgroesse**
  erweitert. Ohne sie ist „+12.4" bedeutungslos: sie sagt, dass gegen den
  aktuellen Build **mit geleertem Slot** gerechnet wird — auch fuer das
  Relikt, das gerade drinsteckt (AD-018.1).
- **Zeile 4** ist die Pflichtzeile aus AD-018.3 in Nutzersprache, plus der
  Attack-Rating-Vorbehalt in voller Laenge. `MUTED`, 11 px,
  `setWordWrap(True)`, **nicht** aufklappbar, **kein** Tooltip-Ersatz, nie
  elidiert.

#### 3.3 Die Wertspalte auf der Karte

Erste Zeile des Kartenkoerpers, **unter** der Kopfzeile (Icon, ★, Name),
**ueber** den Effektpunkten, abgetrennt durch dieselbe Haarlinie, die die
Arsenal-Kachel schon benutzt (`QFrame.HLine`, 1 px, `BORDER`).

```
Damage         +12.4 AR
Damage taken   −18
```

- Linke Beschriftung `MUTED` 11 px, Wert rechtsbuendig, fett, 12 px.
- **Beide Zielrichtungen stehen immer da**, unabhaengig von der Sortierung.
  Das ist die Entscheidung nach AD-018.2, und sie hat einen sachlichen Grund,
  nicht nur den, dass sie nichts kostet: **OF-13 verlangt eine Darstellung
  fuer „kostet dich etwas, aber nicht bei diesem Ziel", die nicht wertet.**
  Zwei nebeneinanderstehende Zahlen sind genau das — sie nennen den Preis in
  seiner eigenen Einheit, statt ihn in eine fremde umzurechnen, die es in den
  Spieldateien nicht gibt (A7, AD-015).
- Null heisst `no change`, nicht `+0.0`. Bei stueckweise linearen Kurven ist
  Null der haeufigste Wert; `+0.0` liest sich wie ein gerundetes Etwas.
- **`unverified` entfaellt.** Die Auflage aus T-024 galt "solange QA-018
  offen ist"; QA-018 ist am 03.09.2026 durch eine Messung des Nutzers
  geschlossen. Das Wort kommt auf keiner Karte mehr vor — siehe den Nachtrag
  zu AK-47 am Ende dieser Datei. Der Vorbehalt selbst bleibt, aber als **ein**
  Satz ausserhalb der Karten (Zeile 4 in §3.2), nicht als Marke je Zeile.
- **Die Einheit steht am Wert. Abhaengigkeit, die nicht meine ist:** ob die
  Zielrichtung „Schaden maximieren" ihren Wert in AR ausdrueckt, legt AD-004
  fest, nicht diese Vorgabe. Ist die Zielpunktzahl **einheitenlos**, entfaellt
  der Zusatz `AR` — und mit ihm `unverified`, das sich auf den Angriffswert
  bezieht. Der Fall ist im Bericht an den `director` benannt.
- **Platz wird reserviert.** Der Block ist vom ersten Anstrich an da; solange
  gerechnet wird, steht `…` an der Stelle der Zahl. Die Kartenhoehe darf sich
  beim Eintreffen der Werte **nicht** aendern — sonst springt bei 29 Karten
  das ganze Raster.

**Preis, gemessen:** der Block kostet rund 34 px Kartenhoehe; der
Zeilenabstand steigt von 161 auf ~195 px, sichtbar sind statt ~19 noch ~16
Karten am Standardmass. Vertretbar, weil die Zahl der Grund ist, warum dieser
Bildschirm jetzt existiert.

#### 3.4 Sortierung

`Sort by`, `QComboBox`, `setMaximumWidth(220)`, Eintraege in dieser
Reihenfolge:

1. `Maximise damage`
2. `Minimise damage taken`
3. `Name`

- Die ersten beiden tragen woertlich dieselben Namen wie die Zielwahl der
  Advisor bar (§3.1 oben) — und sie sind **dieselbe Einstellung**, nicht eine
  zweite. Im Picker umgestellt heisst in der Leiste umgestellt und umgekehrt.
  Zwei Zielwahlen waeren der vierte widerspruechliche Ort, den dieser Auftrag
  gerade verhindern soll.
- Bei `Name` gilt die heutige Ordnung unveraendert, Favoriten voran.
- Bei einer Zielsortierung fuehrt der **Wert**, nicht der Favoritenstern. Der
  Stern bleibt auf der Karte, damit ein Favorit auffindbar bleibt.
- Die Custom-Karte fuehrt das Raster weiterhin in jeder Sortierung und wird
  nie ausgefiltert (Bestand, ausdruecklich bestaetigt: sie ist die Antwort auf
  „nichts davon passt").

#### 3.5 Gleichstaende

Gemessen, nicht vermutet: die Waffenkurven sind stueckweise linear, zwei
Kandidaten im selben Abschnitt sind **exakt** gleich viel wert. Die
Darstellung darf keine Ordnung behaupten, die es nicht gibt.

1. **Keine Ordnungszahlen.** Nirgends `1.`, `#2`, „Top 3", kein Rang-,
   Medaillen- oder Sternchenrang. Die Zahl ist der Rang.
2. **Die Sortierung ist stabil.** Bei gleichem Wert bleibt die Ordnung, die
   ohne Berater gaelte (Favoriten, dann Name). Zweimal derselbe Zustand ergibt
   zweimal dieselbe Reihenfolge; nichts wackelt zwischen zwei Oeffnungen.
3. **Gleichheit wird an der angezeigten Genauigkeit entschieden.** Zwei Karten
   zeigen genau dann denselben Wert, wenn sie dieselbe
   Gleichstandskennzeichnung tragen. Sonst entstuende der schlimmste Fall:
   zwei sichtbar gleiche Zahlen, von denen nur eine gekennzeichnet ist.
4. **Kennzeichnung des Spitzenwerts:** jede Karte, deren Wert in der
   sortierten Zielrichtung dem Maximum entspricht, traegt in der Kopfzeile den
   Chip `BEST FOR DAMAGE` bzw. `BEST FOR SURVIVAL` — 10 px, `ACCENT`, ohne
   Rahmen, **Text, nicht nur Farbe**. Tragen ihn fuenf Karten, tragen ihn
   fuenf Karten. Genau das ist die Aussage.
5. **Kein Chip, wenn der Spitzenwert `no change` oder negativ ist.** Zwanzig
   Karten mit `BEST FOR DAMAGE` bei durchgehend Null waeren eine Luege in
   Fettschrift. Stattdessen sagt es die Kopfzeile einmal:
   `Nothing you own raises damage in this slot.`

#### 3.6 Fluechte, die zum Ziel nicht passen (OF-13)

Der Fluch steht auf der Karte schon heute mit Namen, in `CURSE`, mit `✦` — das
bleibt unveraendert. Zwei Faelle liegen daneben:

- **Der Fluch bewegt ein Feld, das die *andere* Zahl misst.** Dann steht er
  dort, als negative Zahl. Es braucht keinen Satz; die Darstellung zeigt den
  Preis in seiner eigenen Einheit, ohne ihn zu verrechnen.
- **Der Fluch bewegt ein Feld, das *keine* der beiden Zahlen misst** (etwa
  Item Discovery). Dann, und nur dann, steht unter der Wertspalte eine Zeile
  in `MUTED`, 11 px:

  > `Its curse changes <field>, which neither figure counts.`

  Das nennt, ohne zu werten, und ohne einen Umrechnungskurs zu erfinden, den
  die Spieldateien nicht hergeben (AD-015, A7). Der Feldname kommt aus
  `model.label_for()` und wird vor der Interpolation escaped.

#### 3.7 Wenn nicht gerankt werden kann (A7)

Traegt die gewaehlte Zielrichtung fuer diesen Nightfarer keine Zahlen:
- Kopfzeile: `The game's data carries no figures this goal can be ranked on, so these relics are in name order.`
- Auf jeder Karte steht an der Stelle der Zahl `—`, nicht `0` und nicht nichts.
- Die Ordnung faellt auf `Name` zurueck; die `Sort by`-Auswahl bleibt sichtbar
  auf der gewaehlten Zielrichtung stehen, damit die Aussage nicht wandert.

#### 3.8 Warten *(ueberholt am 08.09.2026 — ersetzt durch „Der Picker oeffnet vor seinen Zahlen" am Ende dieser Datei, T-124)*

> **Korrektur vom 08.09.2026 (T-124, aus AD-028), ersetzt den Absatz
> darunter — der Absatz bleibt stehen, damit sichtbar bleibt, dass hier
> einmal anders entschieden wurde und woran.**
>
> **Die `~51 ms` waren nie gemessen.** AD-018 hat sie aus „205 Kandidaten mal
> 0,25 ms je Bewertung" **gerechnet**; die 0,25 ms stammten aus einer
> Bewertung vom 01.09.2026 ohne protokollierte Umgebung. **Gemessen sind
> 318,1 ms** (Median, n=25, Spanne 289,6–358,9; `docs/perf/baselines.md`
> S11-C, Slot 2 weiss, 206 Kandidaten; Ryzen 7 5800H bei 1102 von 3201 MHz
> unter `Legion Quiet Mode`, CPython 3.12.10, Commit `76f1887`) — Faktor 6,3,
> und **oberhalb** der 250-ms-Schwelle, unter der dieser Absatz seine ganze
> Begruendung hatte.
>
> **Was faellt:** der Schluss „unter der Schwelle, also nichts zu zeigen".
> **Was bleibt:** kein Fortschrittsbalken und kein Wartecursor — aber aus
> einem anderen Grund, und nicht mehr „kein Aufblitzen, also gar nichts".
> **Was dazukommt:** der Dialog oeffnet jetzt **vor** seinen Zahlen (AD-028),
> also gibt es einen Zustand, den es vorher nicht gab. Der Generationszaehler
> aus AD-006.3, den dieser Absatz fuer gegenstandslos hielt, gilt jetzt auch
> hier.
>
> Verbindlich ist der Abschnitt **„Der Picker oeffnet vor seinen Zahlen
> (ui-ux-designer, T-124) — 2026-09-08"** am Ende dieser Datei, AK-197 bis
> AK-210.

AD-018 misst den teuersten Picker-Lauf mit ~51 ms, also unter der
250-ms-Schwelle aus AK-09. Deshalb: **kein Fortschrittsbalken, kein
Wartecursor, kein Aufblitzen** im Picker. Nur das `…` aus §3.3, und das auch
nur, wenn beim ersten Anstrich noch nichts vorliegt. Wird waehrend der
Rechnung der Grundzustand veraendert (Filter, ein anderer Slot, Level), gilt
der Generationszaehler aus AD-006.3: das ueberholte Ergebnis wird verworfen,
nie angezeigt.

---

### 4. Festgehaltene Slots (GOAL F1, AD-014, AD-016, AD-017, OF-15)

#### 4.1 Bedienelement

Ein **checkbarer `QToolButton` mit Text** in der Kopfzeile jeder
`RelicSlot`-Karte, links neben dem Farbchip (`app.py:520-526`).

- unmarkiert: `Hold` — `MUTED`, kein Rahmen
- markiert: `Held` — `ACCENT`, 1 px `ACCENT`-Rahmen
- Tooltip (`Qt.PlainText`), woertlich:
  > `Optimize leaves this slot alone. You can still change it yourself. Holds are forgotten when the program closes.`

**Kein Schloss-Symbol allein.** Ein Schloss heisst „du kannst das nicht
aendern", und genau das ist falsch: ein Halt bindet den **Berater**, nicht den
Spieler. Der zweite Satz im Tooltip ist deshalb kein Beiwerk, sondern die
eigentliche Bedeutung — er muss stehen.

#### 4.2 Ein festgehaltener leerer Slot

Zulaessig (AD-014.7) und heisst „bleibt leer". Der Slot zeigt dann in
`rolled_label`, `MUTED`:
> `Held empty — Optimize will not fill this slot.`

#### 4.3 Ein Halt, der wegfaellt

Ist das gehaltene Relikt nicht mehr im Besitz (Neu-Scan, Einschmelzen), faellt
der Halt weg und **wird genannt** — an **zwei** Orten, weil es zwei Fragen
sind:

- Am Slot selbst, ueber den bestehenden `empty_reason`-Weg:
  > `A relic you were holding is no longer in your inventory, so this slot was released.`
- Im Ergebnis des naechsten `Optimize`-Laufs, in `unknowns` (AD-017.3).

Stillschweigen waere hier der Fall, der einen falschen Vorschlag erzeugt.

#### 4.4 Was die Oberflaeche **nicht** verspricht

Der Haltezustand lebt am `Planner`, geschluesselt ueber `(Held, Gefaess,
Deep)`, und ueberlebt keinen Programmneustart (AD-017, OF-15). Daraus folgt
eine Auflage an den Text: **keine Zeichenkette darf Dauerhaftigkeit
nahelegen** — kein „saved", kein „remembered", kein Schloss-Symbol, das nach
Werk aussieht. Der Tooltip sagt die Grenze ausdruecklich. Nach einem Neustart
ist nichts gehalten; das ist kein Fehler, den die Oberflaeche erklaeren muss —
aber sie darf ihn auch nicht vorher bestritten haben.

---

### 5. `Optimize` — die zweite Frage

#### 5.1 Ort und Beschriftung

`Optimize` ist der Knopf der Advisor bar (§3.1 oben), der in der Fassung vom
01.09.2026 noch `Suggest` hiess — umbenannt. Er bleibt in der mittleren Spalte
des Build planner, ueber den Slots, ausserhalb der `QScrollArea`.
*(Nachgezogen T-084, 07.09.2026: „der heutige `Suggest`-Knopf" war seit dem
Tag der Umbenennung falsch. Der Knopf heisst **ueberall** `Optimize`; das Wort
`Suggest` steht hier nur noch als Verlauf. AK-176.)*

**Warum nicht in den Picker:** Der Picker ist ein modaler Dialog **je Slot**.
Ein Knopf, der ueber **alle** Slots rechnet und mehrere davon veraendert,
gehoert nicht in ein Fenster, das genau einen Slot bearbeitet — er verstecke
die Aenderung an fuenf Slots hinter einer Auswahl fuer den sechsten. Der
Nutzer hat sich bei der Platzierung ausdruecklich flexibel gezeigt (GOAL F4);
dies ist die Begruendung, mit der ich entschieden habe.

#### 5.2 Eine Zielwahl, zwei Orte

Die `QComboBox` der Advisor bar und das `Sort by` des Pickers zeigen und
setzen **dieselbe** Einstellung (§3.4).

#### 5.3 Die Pflichtzeile

Der Satz aus AD-018.3 steht im **Picker** (§3.2, Zeile 4), nicht am
`Optimize`-Knopf: er ist eine Warnung vor dem slotweisen Waehlen, und
slotweise gewaehlt wird im Picker. Nutzersprachliche Fassung, woertlich:

> `One slot at a time — some relics only pay off together; Optimize on the Build planner looks for those.`

#### 5.4 `Apply all` und der Haltezustand

- `Apply all` fasst einen gehaltenen Slot **nicht** an — weder um ihn zu
  belegen noch um ihn zu leeren. Ein Halt ist Randbedingung der Suche
  (AD-014), das Ergebnis darf ihn also gar nicht enthalten.
- Ein gehaltenes `Custom relic` ist eine **Eingabe**, kein Vorschlag. AK-16
  („kein Vorschlag enthaelt je ein Custom relic") gilt unveraendert fuer die
  **vorgeschlagenen** Slots und wird hier klargestellt, nicht aufgeweicht.
- `Undo apply` stellt ebenfalls nur die nicht gehaltenen Slots wieder her — es
  gibt nichts anderes zurueckzunehmen.

---

### 6. Token

Kein neuer Farbwert, keine neue Schriftgroesse. Werte aus den Hex-Konstanten
gerechnet, nicht vom Bildschirm gemessen:

| Token | Wert | Neue Verwendung | Kontrast auf `PANEL` |
|---|---|---|---|
| `ACCENT` | `#c8a45c` | `BEST FOR …`-Chip, `Held`-Knopf | 6,99:1 |
| `MUTED` | `#8a8a8a` | Wertbeschriftungen, `unverified`, alle neuen Saetze | 4,77:1 |
| `CURSE` | `#d1655f` | Fluchzeilen (Bestand) | 4,50:1 |
| `GOOD` | `#6fbf73` | positiver Grenzbeitrag, sofern eingefaerbt | 7,35:1 |
| `FAVOURITE` | `#a86fe0` | Stern (Bestand) | 4,72:1 |

**Auflage:** Farbe traegt nirgends allein eine Aussage. Positiver und
negativer Grenzbeitrag unterscheiden sich am **Vorzeichen**; wird eingefaerbt,
kommt die Farbe zum Vorzeichen dazu, sie ersetzt es nicht.

---

### 7. Akzeptanzkriterien

Fortlaufend ab **AK-31**. Pruefbar, binaer, vom `qa-engineer` gegen ein
gebautes Artefakt (GOAL A9).

**Teil 1 — die Benennung**

- **AK-31** Im gesamten `nrplanner/`-Baum wird eine Angriffswertzahl nur mit
  einer dieser drei Formen beschriftet: `AR without relics`, `AR as equipped`,
  `AR at +<n>`. Die Beschriftungen `Base`, `Base AR`, `Total` und ein
  alleinstehendes `AR` **als Beschriftung** kommen nicht mehr vor. Ausnahme,
  ausdruecklich: das Suffix `AR` in der Waffenkachel des Build planner
  (`203 AR`), zulaessig **nur zusammen mit** der Bildunterschrift aus AK-35
  und **erst ab** Schritt W3.
- **AK-32** Jede Angriffswertzahl auf dem Bildschirm laesst sich einer der drei
  Fragen aus `damage.Basis` zuordnen, ohne zu hovern und ohne aufzuklappen —
  entweder ueber ihre eigene Beschriftung oder ueber eine stets sichtbare
  Bildunterschrift im selben Sichtblock.
- **AK-33** Die Kopfzeile der Zahlenliste jeder Arsenal-Kachel lautet
  `AR at +<n>` mit dem Wert der Spinbox `Upgrade to +`; sie aendert sich mit
  der Spinbox und bricht bei Kachelbreite 200 px nicht um.
- **AK-34** Die Arsenal-Zusammenfassung besteht aus zwei getrennten Labels mit
  dem Wortlaut aus §2.3(e). Der Multiplikator-Satz entspricht dem Wert von
  `MULTIPLIERS_FOR[Basis.CANDIDATE]` (Fassung A bei `False`, Fassung B bei
  `True`). Die Zeichenketten `60%`, `under investigation` und
  `ranking between weapons is unaffected` kommen im gesamten Baum nicht mehr
  vor.
- **AK-35** Zwischen dem Waffenkachelraster und der Schadenstafel steht eine
  stets sichtbare Bildunterschrift mit dem Wortlaut aus §2.3(c). Sie ist kein
  Tooltip, nicht aufklappbar, und sie scrollt mit den Kacheln, nicht von ihnen
  weg.
- **AK-36** Die Gesamtzeile der Schadenstafel zeigt beide Namen ohne Hovern
  (`AR without relics <n> → AR as equipped <n>`); die Aufschluesselung
  (`_show_ar_breakdown`) benutzt in erster und letzter Zeile dieselben zwei
  Namen und dazwischen die Zeile `What your relics add to your attributes`.
- **AK-37** Keine Zeichenkette der Oberflaeche behauptet, welche Zahl richtig
  ist, in welchem Verhaeltnis sie zum Spiel steht, oder dass eine Rangfolge
  davon unberuehrt bleibt. Die einzigen Aussagen zur Verifikation sind
  `Not checked against the game's own attack-power display.` (Arsenal-Tab) und
  `Attack rating has not been checked against the game, so these figures may
  be wrong.` (Picker) — je Bildschirm genau einmal, im Picker zusaetzlich der
  Kartenmarker aus AK-46.
- **AK-38 (QA-055-Regression)** Aufbau: Slot auf Tier 3, Arsenal-Spinbox auf
  +1, kein Relikt ausgeruestet. Die beiden Zahlen duerfen verschieden sein;
  die Arsenal-Kachel nennt in ihrer Kopfzeile `AR at +1`, der Build planner
  nennt in der Bildunterschrift „each at its own upgrade", und keine
  Beschriftung behauptet, es sei dieselbe Frage.
- **AK-39 (QA-056-Regression)** Aufbau: ein Relikt mit `Strength +1`, sonst
  nichts. Waffenkachel und Schadenstafel zeigen fuer dieselbe Waffe **dieselbe**
  Zahl (nach W3, AD-020 Punkt 6); die davon abweichende linke Tafelzahl traegt
  sichtbar `AR without relics`.
- **AK-40 (Reihenfolge)** Die Beschriftungen aus AK-31, AK-33, AK-35 und AK-36
  werden nicht vor den zugehoerigen Umbauschritten ausgeliefert: die
  Kachel-/Tafel-Fassung nicht vor W3, die Arsenal-Fassung nicht vor W4. Ein
  Zwischenstand, in dem Kachel und Tafel verschiedene Zahlen zeigen und beide
  `AR as equipped` heissen, ist unzulaessig.

**Teil 2 — der Picker**

- **AK-41** Jede Reliktkarte traegt einen Wertblock als erste Zeile des
  Kartenkoerpers, unter der Kopfzeile und ueber den Effektpunkten, getrennt
  durch eine 1-px-Haarlinie in `BORDER`. Die Hoehe jeder Karte ist vor und
  nach dem Eintreffen der Werte identisch (Messung: Differenz 0 px).
- **AK-42** Der Wertblock zeigt **beide** Zielrichtungen (`Damage`,
  `Damage taken`) auf jeder Karte, in jeder Sortierung. Ein Wert von Null
  erscheint als `no change`, nie als `+0.0`.
- **AK-43** Der Picker traegt ein `Sort by` mit genau den Eintraegen
  `Maximise damage`, `Minimise damage taken`, `Name`. Eine Aenderung dort
  aendert die Zielwahl der Advisor bar und umgekehrt; es existiert im ganzen
  Programm nur eine Zielwahl-Einstellung.
- **AK-44** Weder auf einer Karte noch in der Kopfzeile erscheint eine
  Ordnungszahl, ein Rangabzeichen oder eine Formulierung, die eine strenge
  Reihenfolge behauptet. Zweimaliges Oeffnen des Pickers bei unveraendertem
  Zustand liefert **dieselbe** Kartenreihenfolge.
- **AK-45** Zwei Karten zeigen genau dann denselben Wert in der sortierten
  Zielrichtung, wenn sie dieselbe Gleichstandskennzeichnung tragen. Es gibt
  keinen Fall mit gleichem angezeigten Wert und verschiedener Kennzeichnung.
- **AK-46** Jede Karte mit dem Maximalwert der sortierten Zielrichtung traegt
  den Textchip `BEST FOR DAMAGE` bzw. `BEST FOR SURVIVAL`, auch wenn es
  mehrere sind. Ist der Maximalwert `no change` oder negativ, traegt **keine**
  Karte den Chip, und die Kopfzeile sagt
  `Nothing you own raises damage in this slot.`
- **AK-47** Solange QA-018 offen ist, steht hinter dem Angriffswert **jeder**
  Karte das Wort `unverified` — sichtbar, nicht in einem Tooltip, nicht
  aufklappbar. Ist QA-018 geschlossen, kommt das Wort nirgends mehr vor.
- **AK-48** Bewegt der Fluch eines Relikts ein Feld, das **keine** der beiden
  Zahlen misst, steht unter dem Wertblock genau eine Zeile
  `Its curse changes <field>, which neither figure counts.`; misst eine der
  beiden Zahlen das Feld, steht diese Zeile **nicht** da. Ein Fluch wird
  nirgends als Grund fuer eine schlechtere Platzierung dargestellt.
- **AK-49** Traegt die gewaehlte Zielrichtung keine Zahlen, steht die Zeile aus
  §3.7 in der Kopfzeile, jede Karte zeigt `—` statt einer Zahl, und die Ordnung
  ist Namensordnung. Es wird nie eine Rangfolge gezeigt, die auf fehlenden
  Daten beruht.
- **AK-50** Die beiden Textzeilen aus §3.2 (Bezugsgroesse; slotweise plus
  Attack-Rating-Vorbehalt) stehen ausserhalb der `QScrollArea`, sind ohne
  Interaktion sichtbar und werden nie gekuerzt oder elidiert.
- **AK-51** Am Standardmass des Pickers erscheint **keine** waagerechte
  Bildlaufleiste (heute gemessen: Sichtbereich 988 px gegen 1000 px Inhalt),
  und es sind mindestens **drei vollstaendige Kartenzeilen** sichtbar. Wird
  eine der beiden Bedingungen durch die neuen Inhalte verletzt, wird das
  Standardmass des Dialogs vergroessert — nicht der Inhalt gekuerzt.
- **AK-52** `Sort by` liegt in der Tab-Reihenfolge zwischen dem Filterfeld und
  der ersten Karte; jede Karte ist per Tab erreichbar und per Enter oder
  Leertaste auswaehlbar; der Fokusring ist auf jedem neuen Bedienelement
  sichtbar und wird nicht per Stylesheet entfernt.
- **AK-53** Jedes im Picker neu eingefuehrte Label und jeder neue Tooltip setzt
  `setTextFormat()` ausdruecklich; jeder aus Save- oder Spieldateien stammende
  Text (Reliktname, Effektname, Fluchname, Feldname aus `model.label_for`)
  laeuft vor der Interpolation durch `html.escape()`. Ein Relikt mit dem Namen
  `<b>x</b><img src=x>&lt;` erscheint auf der Karte und in jedem neuen Satz
  buchstabengetreu (Erweiterung von AK-29/AK-30 auf die neuen Elemente).

**Teil 3 — festgehaltene Slots**

- **AK-54** Jede `RelicSlot`-Karte traegt in ihrer Kopfzeile einen checkbaren
  Knopf mit dem Text `Hold` bzw. `Held` (kein icon-only-Schloss) und dem
  Tooltip-Wortlaut aus §4.1.
- **AK-55** Ein leerer Slot kann gehalten werden; er zeigt dann
  `Held empty — Optimize will not fill this slot.` und wird von `Apply all`
  nicht belegt.
- **AK-56** Faellt ein Halt weg, weil das Relikt nicht mehr im Besitz ist,
  steht der Satz aus §4.3 am Slot **und** eine entsprechende Zeile in den
  `unknowns` des naechsten Laufs. Kein Halt faellt stillschweigend weg.
- **AK-57 (praezisiert AK-13, AK-14)** Nach `Apply all` ist der Inhalt jedes
  gehaltenen Slots bitgleich dem Inhalt davor — Relikt, Rolls, Fluche, und auch
  der Fall „gehalten und leer". `Optimize` allein veraendert weiterhin keinen
  einzigen Slot.
- **AK-58 (praezisiert AK-16)** Ein gehaltener Slot darf ein `Custom relic`
  enthalten und behaelt es. Kein **vorgeschlagener** Slot enthaelt je ein
  `Custom relic` oder ein Relikt ausserhalb von `owned`.
- **AK-59** Keine Zeichenkette der Oberflaeche legt nahe, dass ein Halt einen
  Programmneustart ueberlebt. Nach einem Neustart ist kein Slot gehalten.
- **AK-60** Gefaess oder Nightfarer wechseln und zurueckwechseln stellt den
  Haltezustand wieder her; die Slot-Kopfzeilen zeigen ihn unmittelbar danach
  richtig an.

**Teil 4 — `Optimize`**

- **AK-61** Der Knopf heisst `Optimize` und steht in der Advisor bar der
  mittleren Spalte des Build planner. Im Relic Picker gibt es **keinen** Knopf,
  der mehr als den geoeffneten Slot veraendert.
- **AK-62** Der Satz aus §5.3 steht sichtbar im Picker, in jeder Sortierung und
  in jedem Zustand, in dem Kartenwerte gezeigt werden.

---

### 8. Ausdruecklich nicht Teil dieser Vorgabe

- **Welche der Zahlen richtig ist.** Diese Vorgabe benennt Fragen; sie
  entscheidet nichts ueber Korrektheit. Das kann nur die Messung im laufenden
  Spiel (`docs/state.md`, „Die Messung im Spiel"), und sie aendert nach AD-019
  genau eine Konstante plus einen Satz (§2.3(e)).
- **Die Einheit der Zielpunktzahlen.** Legt AD-004 fest. §3.3 verlangt nur,
  dass die Einheit am Wert steht, wenn es eine gibt.
- **Die Auswahlgeste im Picker.** Ein Linksklick waehlt und schliesst — das
  bleibt unveraendert. Die Werte sind ohne Interaktion lesbar, der Vergleich
  braucht also keine neue Geste.
- **Ein Schalter „ohne Fluche"** (AD-015 laesst ihn offen). Mit zwei sichtbaren
  Zahlen je Karte ist der Preis eines Fluchs ablesbar; ein Filter waere
  Bequemlichkeit, kein Erkenntnisgewinn, und er verbaerge Kandidaten.
- **Ein Vorschlag fuer das Gefaess.** Nicht-Ziel.
- **Eine bedienbare Gewichtung der acht Schadensarten.** Sie ist fest, benannt
  und im Ergebnis ausgewiesen (Vorgabe T-024).
- **Antwortzeitbudgets.** Setzt der `performance-tuner` (S11).
- **Die waagerechte Bildlaufleiste als Bestandsfehler.** AK-51 verlangt ihre
  Abwesenheit im Zielzustand; ob sie vorher als eigener Befund gefuehrt wird,
  entscheidet der `director`.

---

### 9. Offene Fragen an den App Designer

- **OF-16 — der 60-%-Satz.** Ich habe ihn entfernt (§2.4), weil er eine
  Verhaeltniszahl behauptet, die das Projekt nicht belegen kann, und weil seine
  zweite Haelfte („ranking … unaffected") aus dem eigenen Code widerlegbar ist.
  **Er stammt aber aus einer Beobachtung des Nutzers im Spiel** — die
  verschwindet damit aus der Oberflaeche. Soll sie zurueckkommen, sobald sie
  mit Aufbau, Datum und Ergebnis aufgeschrieben ist, oder ganz entfallen?
- **OF-17 — Vorgabe-Sortierung des Pickers.** Ich habe die Zielsortierung als
  Standard gesetzt. Das aendert einen vertrauten Bildschirm bei **jedem**
  Oeffnen. Alternative: `Name` bleibt Standard, die Zahlen stehen trotzdem auf
  jeder Karte, und der Spieler sortiert bewusst um. Produktfrage — wie stark
  soll sich der Berater aufdraengen?
- **OF-18 — zwei Zahlen je Karte oder eine.** Ich habe zwei entschieden (§3.3),
  weil OF-13 sonst nur mit Prosa zu erfuellen waere. Der Preis ist Dichte: 29
  Karten mit je zwei Werten plus `unverified`, und rund drei sichtbare Karten
  weniger. Falls das zu voll wirkt, ist der Rueckfallweg definiert — nur die
  sortierte Zahl zeigen und die Zeile aus §3.6 **immer** zeigen statt nur im
  Restfall.
- **OF-19 — `unverified` auf jeder Karte.** T-024 verlangt den Vorbehalt an
  jeder Picker-Zeile, und so ist es spezifiziert. Ich halte die Wiederholung
  ueber 29 Karten fuer den schwaecheren von zwei Wegen (Wiederholung stumpft
  ab); der staerkere waere die eine dauerhaft sichtbare Zeile ueber dem Raster,
  die ohnehin schon dasteht (§3.2, Zeile 4). Entscheidung des Nutzers, ob der
  Kartenmarker bleibt.

---

## Nachtrag zu AK-34: Fassung B fuer den heutigen Einzelsatz (T-035) — 2026-09-03

**Grundlage:** `docs/tasks/T-035.md` Teil 1, `docs/tasks/T-033.md`, AK-34 oben.

**Praezisierung, keine Neufassung von AK-34.** AK-34 verlangt fuer den
**Zielzustand** (nach der noch ausstehenden AK-31-bis-AK-40-Umstellung) zwei
getrennte Labels mit dem Wortlaut aus §2.3(e). `nrplanner/arsenaltab.py`
traegt diese Umstellung heute noch **nicht** — die Zusammenfassung ist dort
weiterhin **ein** Prosasatzblock. Fassung A/B aus §2.3(e) passt deshalb nicht
woertlich auf den heutigen Satz; dieser Nachtrag liefert die Formulierung fuer
genau diesen Uebergangszustand, in derselben Begrifflichkeit wie §2.3(e)
(„+% attack effects"), damit beide Stellen spaeter ohne Bruch zusammenfallen.

Der bisherige Satz (Fassung A, beschrieb `MULTIPLIERS_FOR[Basis.CANDIDATE] =
False`):

> `Attack rating is base damage plus what your stats add to it.`

**Fassung B, faellig seit T-033 (`MULTIPLIERS_FOR[Basis.CANDIDATE] = True`),
woertlich:**

> `Attack rating is base damage, plus what your stats add to it, plus the +% attack effects your equipped relics grant.`

Der daran anschliessende Satz *„The in-game panel has been seen showing about
60% of these figures (under investigation); the ranking between weapons is
unaffected."* entfaellt ersatzlos, wie in AK-34 bereits gefordert (die
Zeichenketten `60%`, `under investigation` und
`ranking between weapons is unaffected` duerfen im Baum nicht mehr vorkommen);
dieser Nachtrag fuehrt dafuer **keinen** Ersatzsatz ein — eine dauerhafte
Verifikationsaussage fuer diesen Bildschirm (`Not checked against the game's
own attack-power display.`) ist bereits Teil von §2.3(e)/AK-37 und gehoert in
die AK-31-bis-AK-40-Umstellung, nicht in diesen Uebergangs-Fix. Der Satz
`Spell damage is not in the game's data, so spells show their costs instead.`
bleibt unveraendert stehen.

Betroffene Akzeptanzkriterien: **AK-34** (Wortlaut jetzt vollstaendig
spezifiziert, auch fuer den Uebergangszustand vor der Label-Umstellung).

---

## Nachtrag zu AK-47: das Wort `unverified` entfaellt (Director, T-037) — 2026-09-03

**Grundlage:** AK-47 selbst, `qa/findings.md` QA-018, `docs/state.md`,
`docs/berichte/T-037-developer.md` Abschnitt 4(g).

**Keine Neufassung, ein eingetretener Fall.** AK-47 war von Anfang an
zweiteilig formuliert: *"Solange QA-018 offen ist, steht hinter dem
Angriffswert jeder Karte das Wort `unverified` … Ist QA-018 geschlossen,
kommt das Wort nirgends mehr vor."* QA-018 ist am 03.09.2026 durch eine
Messung des Nutzers geschlossen ("counterattack ist nur bei konter, nicht
global"); Waffen-Tab und Detailtafel nennen fuer den Ausgangsfall dieselbe
Zahl. Damit ist die zweite Haelfte von AK-47 in Kraft.

**Verbindlich fuer die Umsetzung des Pickers:**

1. Das Wort `unverified` erscheint **nirgends** — nicht auf einer Karte,
   nicht in einem Tooltip, nicht in einer Kopfzeile. Der Codeblock und der
   Aufzaehlungspunkt in §3.3 sind entsprechend nachgezogen.
2. **Der Vorbehalt selbst bleibt.** Er steht als **ein** Satz in Zeile 4 von
   §3.2, ausserhalb der `QScrollArea`, nicht aufklappbar, nie elidiert:
   `Attack rating has not been checked against the game, so these figures may
   be wrong.` AK-37 zaehlt ihn als eine der beiden erlaubten Aussagen ueber
   Verifikation, und AK-50 haelt seine Platzierung fest. Beide bleiben
   unveraendert gueltig.
3. Der Grund fuer 2 ist **nicht** QA-018, sondern die noch nicht erfolgte
   Messung des Programmwerts gegen die Angriffsanzeige des Spiels. Die
   beiden Fragen sind verschieden: QA-018 war ein Widerspruch **zwischen zwei
   eigenen Anzeigen**, der Vorbehalt ist eine Aussage ueber den Abstand zum
   **Spiel**. Der erste ist geschlossen, der zweite nicht.
4. **Es wird keine Marke je Kandidat gebaut**, die anzeigt, ob ein Kandidat
   ein AR-Ratenfeld traegt. AD-023 beschreibt diese Unterscheidung als
   rechnerischen Sachverhalt; als Anzeige verlangt sie niemand mehr, seit
   AK-47 seine erste Haelfte verloren hat. Wer sie doch bauen will, braucht
   vorher eine Entscheidung des App Designers.

**Betroffene Akzeptanzkriterien:** AK-47 (zweite Haelfte in Kraft, erste
gegenstandslos), §3.3 (Codeblock und Aufzaehlungspunkt nachgezogen). AK-37,
AK-42 und AK-50 sind **unberuehrt**.

**Offen und ausdruecklich nicht hier entschieden:** welcher der beiden
Wortlaute ausgeliefert wird — `Attack rating has not been verified against an
in-game number.` (AD-004, steht heute in `advisor/goals.py` in `unknowns`)
oder `Not checked against the game's own attack-power display.` (nach
T-024/DR-003 beschlossen). Das ist eine Frage an den `ui-ux-designer`; zwei
Saetze fuer dieselbe Sache duerfen nicht beide ausgeliefert werden.

---

## Nachtrag zu QA-116: keiner der beiden Wortlaute — der Vorbehalt wird
## datengetrieben (ui-ux-designer, T-052) — 2026-09-05

**Korrektur 2026-09-05 (T-052-Nachtrag, `ARCHITECTURE.md` Nachtrag VI,
AD-025, OF-19).** Die urspruengliche Fassung dieses Abschnitts (unten,
unveraendert stehen gelassen, damit sichtbar bleibt, was korrigiert wurde)
nannte **eine** Quelle (`GoalScore.unknowns`) fuer beide Anzeigeorte. Der
`architect` hat am selben Tag AD-025 beschlossen: es gibt **zwei** Klassen
von Vorbehalten mit **zwei** verschiedenen Wohnorten — ein **Verfahrenssatz**
(vor dem Lauf feststehend, z. B. der Geltungsbereich der Angriffsrechnung)
wohnt in `Goal.scope`; ein **Laufbefund** (braucht den Lauf, traegt oft eine
Anzahl, z. B. „3 copies had no readable handle") wohnt im Ergebnis
(`GoalScore.unknowns`, `SlotPool.unknowns`). `GoalScore.unknowns` traegt nach
AD-025 nur noch die zweite Sorte — die erste zieht nach `Goal.scope` um. Eine
Vorgabe, die nur `GoalScore.unknowns` liest, wuerde nach dieser Trennung den
Verfahrenssatz **verlieren**, nicht nur umziehen — genau der Regressionsfall,
den der `architect` als einzigen A7-relevanten Punkt seines Nachtrags
benannt hat. Die urspruengliche Antwort auf die Frage „welcher Wortlaut"
bleibt richtig (keiner der beiden alten Saetze); **welche Quelle** das
ersetzt, war falsch benannt und wird hier nachgezogen. Nur „Verbindlich",
„AK-63" und „Betroffene Akzeptanzkriterien" unten sind ersetzt; Grundlage und
die Analyse, warum ein fester Einzelsatz falsch waere, bleiben unveraendert
gueltig und stehen weiter unten in diesem Abschnitt.

**Grundlage:** `qa/findings.md` QA-116, die offene Frage oben (Zeile
1220-1225), `docs/berichte/T-046-developer.md` §9, `nrplanner/advisor/goals.py`
(`_ATTACK_RATING_UNKNOWNS`, `_DAMAGE_TAKEN_UNKNOWNS`), `ARCHITECTURE.md`
Nachtrag VI (AD-025), OF-19.

**Antwort auf die offene Frage: keiner der beiden.** Beide Wortlaute sind
seit T-046 durch eine bessere Loesung ueberholt, die im Programm bereits
steht: pro Zielrichtung eine **eigene**, genauer gefasste Satzliste
(`_ATTACK_RATING_UNKNOWNS`, vier Saetze mit Geltungsbereich — welche
Raritaeten gemessen sind, was ein Katalysator zeigt, dass Zauber gar nicht
bewertet werden; `_DAMAGE_TAKEN_UNKNOWNS`, vier andere Saetze zur
Ueberlebens-Zielrichtung). Ein fest verdrahteter Einzelsatz wie Wortlaut A
oder B waere fuer die Zielrichtung „Minimise damage taken" schlicht falsch —
dort geht es nie um Attack Rating. Der Fehler in UI_SPEC ist also nicht nur
ein veralteter Wortlaut, sondern eine falsche Annahme: dass der Picker immer
nur eine Zielrichtung (Schaden) haette. **Nach AD-025** sind diese acht
Saetze durchweg Verfahrenssaetze (vor dem Lauf schreibbar, unabhaengig vom
Bestand) und wandern nach `Goal.scope`; sie sind **nicht** die einzige
Quelle, die Zeile 4 bzw. Punkt 4 speist (siehe unten).

**Verbindlich, ersetzt §3.2 Zeile 4/Zeile 3 und §3.4 Punkt 4 — zwei Quellen,
zwei Orte:**

- **Der Verfahrenssatz** (`Goal.scope` der gewaehlten Zielrichtung, nach
  AD-025 nie leer) steht **einmal je Bildschirm, ausserhalb der Karten** —
  das ist unveraendert AK-50s Auftrag. Im Picker ist das weiterhin Zeile 4
  von §3.2: Satz 1 bleibt die feste AD-018.3-Pflichtzeile (*"One slot at a
  time — some relics only pay off together; Optimize on the Build planner
  looks for those."*), danach folgen die Saetze aus `Goal.scope` der
  gewaehlten Zielrichtung, der Reihe nach, wortgleich. Im Why-Dialog ist das
  §3.4 Punkt 4: dieselben `Goal.scope`-Saetze, einmal, im Dialogkopf-Kontext.
  Fuer „Name" (keine Zahlen, AK-49) entfaellt die Zeile ganz.
- **Der Laufbefund** (`SlotPool.unknowns` des offenen Slots — heute die
  Handle-Zeile aus QA-108 und die konditionale Zeile aus OF-20/D2, beide
  unten in eigenen Nachtraegen festgelegt) **wohnt beim Pool, nicht bei der
  Zielrichtung**, und erscheint deshalb **nicht** in Zeile 4, sondern
  unmittelbar bei der Pool-Zusammenfassung: als eigene, neue **Zeile 3b** in
  §3.2, direkt unter der bestehenden Zeile 3 (`29 of 29 relics · ranked
  against your build with Slot 3 empty · …`), gleiche Formatierung wie Zeile
  4 (`MUTED`, 11 px, `setWordWrap(True)`, ausserhalb der `QScrollArea`,
  AK-50 gilt sinngemaess auch fuer sie). Zeile 3b **entfaellt vollstaendig**,
  wenn `SlotPool.unknowns` leer ist (der Normalfall: 0 von 309 Relikten ohne
  Handle heute) — leer ist nach AD-025 selbst eine gueltige Aussage, keine
  Luecke. Im Why-Dialog erscheint derselbe Laufbefund **je Slot-Abschnitt**
  (§3.4 Punkt 2, direkt nach den Effekten dieses Slots), nicht einmalig im
  Dialogkopf — weil er eine Aussage ueber **diesen Pool** ist, nicht ueber
  die Zielrichtung insgesamt, und ein anderer Slot einen anderen Laufbefund
  (oder gar keinen) tragen kann.
- Damit zeigt **kein** Bildschirm zwei verschiedene Saetze fuer dieselbe
  Sache, und **keine** Sache verliert ihren Ort: Verfahrenssaetze stehen
  einmal, ausserhalb der Karten, gebunden an die Zielrichtung; Laufbefunde
  stehen beim Pool bzw. beim Slot, gebunden an den Lauf.

**AK-63** Zeile 4 des Pickers (§3.2) und Punkt 4 des Why-Dialogs (§3.4) zeigen
ausschliesslich die Saetze aus `Goal.scope` der aktuell gewaehlten
Zielrichtung, wortgleich, in Tupel-Reihenfolge — nirgends ein zusaetzlicher,
fest im UI-Code verdrahteter Vorbehaltssatz daneben oder anstelle davon.
**Zusaetzlich, neu gegenueber der urspruenglichen Fassung dieses
Akzeptanzkriteriums:** jeder String in `SlotPool.unknowns` des offenen Slots
erscheint wortgleich in der neuen Zeile 3b von §3.2 bzw. im zugehoerigen
Slot-Abschnitt von §3.4 Punkt 2 — und **nirgends sonst**. Ein Test, der
`advisor/goals.py` um einen fuenften `Goal.scope`-Satz erweitert, findet
diesen Satz danach in beiden Anzeigeorten der Zielrichtung wieder, ohne dass
ein UI-String angefasst wurde; ein Test, der `SlotPool.unknowns` fuer einen
Pool leert, findet dort **keine** Zeile 3b mehr, waehrend Zeile 4 unveraendert
stehen bleibt.

**Betroffene Akzeptanzkriterien:** AK-37 (beide bisherigen Wortlaute
entfallen ersatzlos; die Aussage „keine Zeichenkette behauptet, welche Zahl
richtig ist" gilt jetzt ueber `Goal.scope`/`SlotPool.unknowns` statt ueber
einen festen Satz), AK-50 (gilt jetzt fuer **drei** Zeilen statt zwei — 3, 3b,
4 —, alle ausserhalb der `QScrollArea`, keine gekuerzt; Zeile 3b ist die
einzige der drei, die leer sein darf), der Nachtrag zu AK-47 oben (dessen
offene Frage ist hiermit beantwortet: **keiner** der beiden dort genannten
Wortlaute wird ausgeliefert).

**ARCHITECTURE.md:513 und UI_SPEC.md:192** (§3.4 Punkt 4 selbst, oben in
dieser Datei) zitieren weiterhin den alten Wortlaut A als Beispieltext einer
frueheren Fassung dieser Sektion — das ist jetzt die **historische**
Begruendung fuer diesen Nachtrag, nicht mehr die geltende Vorgabe. Wer §3.4
Punkt 4 liest, liest ihn im Licht dieses Nachtrags.

**Nicht Teil dieser Entscheidung:** ob `_ATTACK_RATING_UNKNOWNS`,
`_DAMAGE_TAKEN_UNKNOWNS` oder ein `SlotPool.unknowns`-Eintrag inhaltlich
richtig oder vollstaendig sind — das ist die Rechnung selbst (AD-004,
AD-025), nicht die Anzeige. Der genaue Wortlaut der beiden heutigen
`SlotPool.unknowns`-Saetze (Handle-Zeile, konditionale Zeile) steht in den
beiden folgenden Nachtraegen.

---

## Nachtrag zu AK-34/QA-121: der Uebergangssatz braucht eine dritte Zeile,
## seit Katalysatoren im selben Raster stehen (ui-ux-designer, T-052) — 2026-09-05

**Grundlage:** `qa/findings.md` QA-121, `nrplanner/arsenaltab.py:306-311`,
`docs/berichte/T-046-developer.md` §8.2 (Vorschlagstext des `developer`),
der Nachtrag zu AK-34 oben (T-035).

**Live bestaetigt (Screenshot):** Sucht man im Arsenal-Tab nach
`Recluse's Staff`, zeigt das Raster ausschliesslich zwei Katalysator-Karten
(`Spell power 139` / `Spell power 92`) — und die Zusammenfassungszeile
darunter sagt trotzdem nur: *"Attack rating is base damage, plus what your
stats add to it, plus the +% attack effects your equipped relics grant."*
Der einzige Satz, der erklaert, was die Zahl auf dem Bildschirm bedeutet,
handelt von einer Groesse, die auf keiner der sichtbaren Karten steht.
Beleg: `docs/screenshots/2026-09-05/arsenal-recluses-staff-collision.png`.

**Entscheidung, nah am Vorschlag des `developer` (T-046 §8.2), stilistisch an
den Rest des Satzblocks angeglichen.** Der bestehende Satzblock
(`arsenaltab.py:307-310`) bekommt **einen zusaetzlichen Satz in der Mitte**,
zwischen der Attack-Rating-Definition und dem Zauber-Satz:

> `Attack rating is base damage, plus what your stats add to it, plus the +% attack effects your equipped relics grant. Staves and seals show the spell scaling the game displays for them instead of an attack rating. Spell damage is not in the game's data, so spells show their costs instead.`

Nicht der Vorschlagswortlaut selbst (*"For staves and seals the game shows a
spell scaling instead of an attack power, so that is what their tiles
show."*) — dieser Text erklaert die Kachel, nicht die Zusammenfassungszeile,
und wiederholt "attack power" statt des im restlichen Satz benutzten "attack
rating" (Terminologie-Bruch). Die hier gewaehlte Fassung nennt das Wort in
derselben Form wie Satz 1, damit der Leser nicht zwei Namen fuer dieselbe
Sache lernen muss.

**AK-64** Der Zusammenfassungssatz des Arsenal-Tabs (`arsenaltab.py:306-311`,
Fassung B des Uebergangs-Nachtrags zu AK-34) enthaelt zusaetzlich den Satz
*"Staves and seals show the spell scaling the game displays for them instead
of an attack rating."*, an der Stelle zwischen der Attack-Rating-Definition
und dem Zauber-Satz, wortgleich. Ein Aufbau, bei dem der sichtbare
Kachelraster nur Katalysatoren zeigt (z. B. Suche nach einem Stab- oder
Siegel-Namen), zeigt diesen Satz **immer** — er ist nicht an die aktuelle
Trefferliste gebunden, weil die Zusammenfassungszeile heute ohnehin fuer das
ganze Arsenal gilt, nicht nur fuer den gefilterten Ausschnitt.

**Verhaeltnis zu AK-34 selbst:** Sobald die AK-31-bis-AK-40-Umstellung auf
zwei getrennte Labels (§2.3(e)) ausgeliefert wird, entfaellt dieser
Uebergangssatz ohnehin zugunsten der endgueltigen Fassung — §2.3(e) nennt fuer
Katalysatoren dort schon keinen eigenen Satz, weil Label 1 (Kontext) und
Label 2 (Definition) je Basisgroesse getrennt sind. Dieser Nachtrag gilt nur
fuer den heutigen Uebergangszustand (ein Prosablock), wie der Nachtrag zu
AK-34 selbst.

**Betroffene Akzeptanzkriterien:** AK-34 (Uebergangs-Wortlaut ergaenzt, siehe
AK-64), QA-121 (damit geschlossen).

---

## Nachtrag zu QA-117: Anzeigeschwellen bleiben absolut, wandern nicht mit
## dem Kalibrierungsfaktor (ui-ux-designer, T-052) — 2026-09-05

**Grundlage:** `qa/findings.md` QA-117, `docs/berichte/T-045-developer.md`
§4.2 und OF-3 (offene Frage an den `ui-ux-designer`), `nrplanner/app.py`
(`abs(from_attributes) >= 0.5`, `abs(diff) >= 0.5`, `diff > 0.05`).

**Die Frage:** Seit die 0,6-Kalibrierung eingezogen ist, faellt die Zeile
`From attributes` 89-mal weg (vorher `|scaled - base| >= 0,5`, jetzt
`< 0,5`) und 66 Aenderungszellen `+1` werden `—`. Sollen die Schwellen mit
0,6 mitskaliert werden (≈ 0,83 statt 0,5), damit dieselben *Faelle* wie vorher
eine Zeile zeigen?

**Entscheidung: nein, die Schwellen bleiben, wo sie sind.** Begruendung, mit
Akzeptanzkriterium:

1. **Die Schwelle beschreibt die Anzeige, nicht das Spiel.** `0,5` ist die
   halbe kleinste **darstellbare** Einheit einer auf null Nachkommastellen
   gerundeten bzw. abgeschnittenen Ganzzahl (`f"{x:+.0f}"` /
   `damage.displayed`) — sie sagt „diese Aenderung ist auf dem Bildschirm
   nicht von 0 zu unterscheiden", nicht „diese Aenderung ist im Spiel
   bedeutungslos". Die Anzeige selbst hat sich durch die Kalibrierung nicht
   veraendert: sie zeigt immer noch ganze Zahlen, gerundet auf dieselbe Art,
   in derselben Schriftgroesse. Eine Schwelle, die mitwandert, wuerde eine
   Eigenschaft der **Kalibrierung** (0,6) in eine Eigenschaft der **Anzeige**
   (wann eine Zeile erscheint) uebersetzen — genau die Art von erfundener
   Umrechnung, die A7 fuer Spielgroessen verbietet, hier auf die Oberflaeche
   selbst angewandt.
2. **Mitwandern loest das Kernproblem nicht, es verschiebt nur die Kante.**
   Jede feste Schwelle hat Faelle direkt daneben; 0,6 x 0,5 = 0,3 wuerde die
   89 auf eine andere, nicht kleinere Menge von Grenzfaellen abbilden (Faelle
   zwischen 0,3 und 0,5 waeren dann neu betroffen). Es gibt keine Schwelle,
   die „dieselben Faelle wie vorher" UND „konsistent mit der neuen Zahl"
   gleichzeitig erfuellt, weil die Rundungsregel selbst nicht linear mit dem
   Faktor mitskaliert (T-045 §4.1: Summen aus mehreren gerundeten Schadensarten
   verhalten sich nicht wie eine einzelne skalierte Zahl).
3. **Der Fall ist bereits eine Anzeige-Wahrheit, keine verschwiegene
   Information.** Zeile 4.9/AK-32-Nachbarschaft (§4 der Datei) verlangt schon,
   dass eine Null als `no change` erscheint statt als `+0.0` — dieselbe Logik
   gilt hier: unter der Rundungsschwelle **ist** die angezeigte Aenderung 0,
   nicht "class="verschwiegen"". Der Spieler verliert keine echte Information,
   die er vorher hatte; er sieht dieselbe Ehrlichkeitsregel auf kleinere
   Zahlen angewandt.

**AK-65** Die Anzeigeschwellen `>= 0.5` (Sichtbarkeit der Zeile
`From attributes` und der Aenderungszelle) und `> 0.05` (Farbe GOOD/MUTED der
Aenderungszelle) in `nrplanner/app.py` bleiben **absolute, an der
Bildschirmeinheit gemessene Konstanten** und werden **nicht** mit einem
Kalibrierungsfaktor multipliziert, auch nicht bei einer kuenftigen
Neukalibrierung. Ein Test, der die 0,6-Konstante veraendert (z. B. auf 0,5
oder 0,7), darf die Zahl der betroffenen Faelle bewegen, aber keine der
beiden Schwellenkonstanten selbst.

**Was das nicht heisst:** Diese Entscheidung bewertet nicht, ob 89 bzw. 66
verschwundene Zeilen an sich zu viele sind — das waere eine Frage an die
Rundungsregel/Anzeigepraezision selbst (z. B. eine Nachkommastelle zeigen),
nicht an die Schwelle, und ist nicht Teil dieses Auftrags.

---

## Nachtrag zu QA-119: die Fremdzeile wird gefiltert, nicht durch eine Id
## unterscheidbar gemacht (ui-ux-designer, T-052) — 2026-09-05

**Grundlage:** `qa/findings.md` QA-119, `docs/berichte/T-046-developer.md`
§7 (Kriterien) und §8.1 (Empfehlung des `developer`),
`docs/screenshots/2026-09-05/arsenal-recluses-staff-collision.png` (live
bestaetigt: zwei Karten `Recluse's Staff`, `Common · Upgraded to +4
Legendary` auf beiden, unterscheidbar nur durch `Spell power 139` gegen
`Spell power 92` — kein Merkmal auf der Karte selbst sagt, welche die
„echte" ist).

**Entscheidung: filtern, nicht kennzeichnen — dem Rat des `developer`
folgend.** Eine Id auf der Kachel (Alternative aus T-046 §8.1) loest das
Problem nicht, sie verschiebt es: der Spieler muesste wissen, **welche** Id
richtig ist, um sie zu nutzen, und die Kollision beruht nicht auf einer
legitimen Spielunterscheidung (zwei echte Varianten desselben Namens), sondern
auf einer **Datenzeile, die kein Spieler je ausruesten kann** — Kriterium aus
T-046 §7, gemessen: 33770000 traegt `equippedSpell_R1/R2 == -1` (kein
Zauberplatz), `reinforceTypeId == 0` (generische Gruppe) und
`attackElementCorrectId == 10000` (generische AEC), alle drei **innerhalb der
Katalysator-Familie eindeutig** auf diese eine Zeile. Ein Katalysator ohne
Zauberplatz ist kein Katalysator, den ein Spieler in der Hand haben kann — er
ist ein Artefakt der Extraktion, keine Wahlmoeglichkeit.

**AK-66** Eine Waffenzeile, die zur Katalysator-Familie gehoert (Glintstone
Staff / Sacred Seal, `model.weapon_class(weapon) == "catalyst"`) und
gleichzeitig `equippedSpell_R1 == -1 and equippedSpell_R2 == -1` traegt
(keinen Zauberplatz), erscheint **nirgends** in einer spielerseitigen
Waffenliste — nicht im Arsenal-Tab, nicht im `WeaponDialog`-Auswahldialog,
nicht in einer kuenftigen Berater-Kandidatenliste. Der Filter greift **nur**
innerhalb der Katalysator-Familie (T-046 §7: ausserhalb ist „kein Zauberplatz"
der Normalfall fuer ein Schwert und sagt nichts). Damit sinkt die Zahl der
sichtbar gefuehrten Katalysatoren um genau die eine betroffene Zeile
(33770000); alle anderen Namen (`Finger Seal`, `Scholar's Thrusting Sword`)
sind von diesem Kriterium nicht betroffen (T-046 §7: beide Kollisionen dort
sind zahlengleich bzw. kosmetisch, kein Betrugsfall).

**Warum keine Id auf der Kachel als Zusatzloesung:** AK-33/AK-41-Stil dieser
Datei haelt Kachel-Kopfzeilen bewusst kurz und ohne technische Kennungen; eine
Id waere die erste Zahl dieser Art auf einer Waffenkachel und muesste dann
konsequent ueberall stehen, wo Namenskollisionen prinzipiell moeglich sind
(auch bei den zahlengleichen Kollisionen), fuer keinen erkennbaren Gewinn,
wenn die eigentliche Ursache (eine nicht ausruestbare Zeile) stattdessen
verschwinden kann.

**Betroffene Akzeptanzkriterien:** keine bestehende AK widerspricht; neu:
AK-66. QA-119 gilt mit dieser Vorgabe als entschieden, nicht als geschlossen —
die Umsetzung liegt beim `developer`.

---

## Nachtrag zu OF-20, QA-108 und QA-113: die drei Saetze in `SlotPool.unknowns`
## (ui-ux-designer, T-052-Nachtrag) — 2026-09-05

**Korrektur 2026-09-05, zweiter Nachtrag desselben Tages.** Dieser Abschnitt
hiess urspruenglich „die beiden Saetze in `SlotPool.unknowns`" und AK-67
nannte eine Obergrenze von zwei. Seit QA-113 (vier Relikte, „Starting
armament deals magic/fire/lightning/holy damage", tragen eine echte
Umwandlung von physischem in elementaren Schaden, die das Programm mit
exakt 0 bewertet) ist ein **dritter** Laufbefund desselben Feldes dazu-
gekommen. Der `developer` hat richtig gehandelt und keinen Wortlaut
erfunden, sondern `[wording pending: QA-113]` stehen lassen — hier
nachgezogen: dritter Wortlaut unten, Obergrenze auf drei angehoben,
Titel und Kopftext entsprechend erweitert. Nichts an den ersten beiden
Wortlauten oder an AK-63 (Erscheinungsort) aendert sich.

**Grundlage:** `ARCHITECTURE.md` Nachtrag VI, AD-025 (Punkt 38 der
Verbotsliste; OF-20; die Tabelle „Anwendung auf den heutigen Bestand", die
QA-113s Blindstelle bereits als zweigeteilt vorwegnimmt), `qa/findings.md`
QA-108 und QA-113, `nrplanner/advisor/candidates.py::_without_a_handle_line`,
der Nachtrag zu QA-116 oben (Zeile 3b, wo alle drei Saetze erscheinen), die
Coordinator-Nachricht vom 2026-09-05 zu QA-113. Alle drei sind Laufbefunde
(`SlotPool.unknowns`, AD-025), alle drei tragen eine Anzahl, alle drei sind
Aussagen ueber Unwissen — kein Warnhinweis-Ton, keine Ausrufezeichen, keine
Wertung, keine behauptete Groesse oder Richtung einer Abweichung.

### Die konditionale Zeile (D2, OF-20)

AD-004 verlangt sinngemaess „N of your relics" — gezaehlt ueber die
Kandidaten **dieses Pools** (also nach Farbe/Deep bereits gefiltert, dieselbe
Grundgesamtheit wie die Handle-Zeile unten), nicht ueber den gesamten
Besitzstand. Endgueltiger Wortlaut, ersetzt die im Code als Platzhalter
benannte Fassung („die den gezaehlten Bestand beschreibt, nicht 'your
relics'", AD-025 Punkt 38):

> Einzahl: `1 of your relics carries an effect that only applies under a condition. It was not counted.`
> Mehrzahl: `{n} of your relics carry effects that only apply under a condition. They were not counted.`

Bewusst **ohne** Beispiel in Klammern (etwa „only below half HP"): eine
Auswahl von Beispielen muesste fuer jedes betroffene Relikt stimmen oder
waere selbst eine Lücke, die A7 wieder aufreisst — welche Bedingung genau
gemeint ist, steht ohnehin schon je Relikt in seiner Effektzeile.
„Not counted" statt „ignored" oder „skipped", weil es die neutralste der drei
Notizen ist — die beiden anderen klingen nach einem Fehler des Programms,
nicht nach einer Grenze der Daten.

### Die Handle-Zeile (QA-108) — ein Muster, zwei Fuellungen

Die heutige Zeile nennt **immer** „of this colour", auch am weissen Slot, wo
sie falsch ist: `inventory.relics_for` liefert dort Kandidaten **jeder**
Farbe (`model.COLOUR_NAMES[4] = "White"` ist die Karte, kein Farbwert, den
ein Relikt selbst tragen kann), also faellt bei einem weissen Slot potenziell
eine Kopie **jeder** Farbe durch dieselbe Handle-Luecke — „of this colour"
behauptet dort eine Eingrenzung, die es nicht gibt. Die Anzahl selbst war nie
falsch (sie summiert schon ueber alles, was der Slot tatsaechlich anbietet);
falsch ist nur die Beschreibung, was gezaehlt wurde. Loesung: **ein**
Satzgeruest, **zwei** Fuellungen fuer die eine Stelle, die sich unterscheidet
— ausgewaehlt danach, ob `slot.colour` der Wert ist, dessen Name in
`model.COLOUR_NAMES` „White" lautet (heute `4`; es gibt noch keine eigene
Konstante dafuer, der `developer` waehlt die Pruefung):

> Farbiger Slot, Einzahl: `1 owned relic of this colour is not offered: this save carries no handle for it, so one copy cannot be told from another and a suggestion naming one could not be applied to a slot.`
> Farbiger Slot, Mehrzahl: `{n} owned relics of this colour are not offered: this save carries no handle for them, so one copy cannot be told from another and a suggestion naming one could not be applied to a slot.`
> Weisser Slot, Einzahl: `1 owned relic of any colour is not offered: this save carries no handle for it, so one copy cannot be told from another and a suggestion naming one could not be applied to a slot.`
> Weisser Slot, Mehrzahl: `{n} owned relics of any colour are not offered: this save carries no handle for them, so one copy cannot be told from another and a suggestion naming one could not be applied to a slot.`

Einzige Aenderung gegenueber dem Bestand: `this` → `any` an der einen
Stelle, die die Reichweite benennt — kein zweiter Satzbau, kein neuer Fall
fuer Singular/Plural, den es nicht schon gaebe.

### Die QA-113-Zeile (dritter Laufbefund, neu)

Vier Relikte tragen einen Effekt „Starting armament deals magic/fire/
lightning/holy damage", der in den Spieldaten eine echte Umwandlung von
`physicsAttackPower` in ein elementares `*AttackPower`-Feld ist — `model.
compute` hat fuer flache `*AttackPower`-Felder kein Fach (QA-113) und bewertet
die Umwandlung deshalb mit exakt 0, waehrend die Effektkarte selbst Zahlen
nennt. **Die Hoehe der Abweichung ist unbekannt und wird hier nicht
geraten** — das kann erst eine Ablesung im laufenden Spiel entscheiden (siehe
`docs/state.md`, Frage F-F). Der Satz benennt ausschliesslich die
Blindstelle, ohne Richtung oder Betrag zu behaupten:

> Einzahl: `1 of your relics changes what damage type your starting armament deals (to magic, fire, lightning, or holy). This figure does not count that change.`
> Mehrzahl: `{n} of your relics change what damage type your starting armament deals (to magic, fire, lightning, or holy). This figure does not count that change.`

Die vier Elemente in Klammern sind die vollstaendige, abgeschlossene Liste
aus QA-113 (nicht ein Beispiel aus einer offenen Menge wie bei der
konditionalen Zeile oben) — deshalb hier ausgeschrieben, ohne A7-Risiko: es
gibt keinen fuenften Fall, der die Aufzaehlung falsch machen koennte, solange
QA-113 bei vier Relikten bleibt. „This figure does not count that change"
statt einer Zahl oder eines Vorzeichens, weil genau das die einzige wahre
Aussage ist, die wir haben.

**Ein Relikt kann in mehr als einer der drei Zeilen mitzaehlen** — Vorgabe
des `director`: 16 der 21 konditionalen Effekte mit flachem `*AttackPower`
sind zugleich konditional, und beide Zaehlungen bleiben bestehen, weil sie
verschiedene Fragen beantworten (*"wird dieser Effekt gerade angerechnet"*
gegen *"kann diese Art Effekt ueberhaupt angerechnet werden"*). Das ist
**keine sichtbare Dopplung**: keine der drei Zeilen nennt ein Relikt beim
Namen, jede ist eine Pool-weite Summe — ein Spieler sieht zwei unabhaengige
Zahlen, nie zweimal denselben Reliktnamen. Eine Anzeigeentscheidung, die das
verhindern muesste, ist deshalb nicht noetig.

**AK-67** `SlotPool.unknowns` traegt fuer den heutigen Bestand **bis zu drei**
Saetze, in dieser Reihenfolge, falls mehrere zutreffen — Handle-Zeile, dann
konditionale Zeile, dann QA-113-Zeile (steigende Beteiligung an der Rechnung:
nie im Pool → im Pool, aber gegen eine Bedingung auf 0 gesetzt → im Pool,
aber durch eine fehlende Rechnungsart auf 0 gesetzt). Alle drei folgen den
Wortlauten oben, wortgleich, mit `{n}` ersetzt durch die tatsaechliche Anzahl
und Singular/Plural korrekt gewaehlt; die Handle-Zeile nennt „of this
colour" ausschliesslich, wenn `slot.colour` nicht der weisse Platzhalter ist,
sonst „of any colour". **Keine Obergrenze unter drei**: faellt ein vierter
Fall dieser Art je an, braucht er eine eigene AK, keine Kuerzung der
bestehenden drei. Alle zutreffenden Saetze stehen **in derselben Zeile 3b**
(bzw. demselben Slot-Abschnitt in §3.4 Punkt 2), durch ein Leerzeichen
getrennt, als ein einziger flexibel umbrechender Textblock — Zeile 3b war
nie ein festes Zeilenraster, sondern ein wachsender Fliesstext wie Zeile 4
selbst (dort schon bis zu fuenf Saetze fuer eine Zielrichtung); ein dritter
Satz verlangt deshalb keine neue Struktur, nur mehr Zeilenumbruch in
derselben `QLabel`.

**Betroffene Akzeptanzkriterien:** AK-63 (Erscheinungsort, unveraendert),
AK-67 (Wortlaut, Reihenfolge und Obergrenze — von zwei auf drei Saetze
erweitert). QA-108, OF-20 und QA-113 gelten mit dieser Vorgabe als
entschieden — Umsetzung liegt beim `developer`.

---

## Die sechs Inhalts-Tabs: welche Frage jeder beantwortet, und woran ein
## Spieler das abliest (ui-ux-designer, T-056) — 2026-09-05

**Geltungsbereich:** `Effects & chances`, `Weapons & spells`, `Nightlords`,
`Deep of Night`, `Red variants`, `World Events`. **Nicht** `Build planner`
(GOAL: „der erste passt"), **nicht** der Berater.

### 0. Grundlage, Methode und Beweisklassen

**Grundlage:** `GOAL.md` A10 bis A14 · `docs/berichte/T-055-qa-engineer.md`
(QA-125 bis QA-139) · `docs/tasks/T-056.md` · eigene Sichtpruefung am
laufenden Fenster am 05.09.2026, Screenshots unter
`docs/screenshots/2026-09-05-T056/`.

**Fehlende Quelle, ausdruecklich:** `docs/berichte/T-054-power-user.md`
**existiert nicht** — weder im Arbeitsbaum, noch untracked, noch in einem
Commit ueber alle Refs, noch im Stash (geprueft: `find`, `git ls-files
--others`, `git log --all -- "*T-054*"`, `git stash list`). `docs/state.md`
fuehrt T-054 als „geschrieben". Alles, was in dieser Vorgabe auf den
`power-user` zurueckgeht, stammt **aus zweiter Hand** aus den drei Zitaten in
`docs/tasks/T-056.md` und ist unten als solches gekennzeichnet. Die Vorgabe
steht trotzdem, weil sie an jeder Stelle **zusaetzlich** durch eine Messung
des `qa-engineer` oder durch einen eigenen Screenshot getragen wird — an
keiner Stelle allein durch das Zitat.

**Beweisklassen**, je Aussage unten mitgefuehrt:

- *(visuell)* — am laufenden Fenster gesehen, Screenshot liegt bei.
- *(gemessen)* — headless am echten Widget gemessen, Zahl im Text.
- *(QA)* — Messung des `qa-engineer` aus T-055, nicht selbst nachgefahren.
- *(zweiter Hand)* — Zitat aus T-056 ueber einen Bericht, der nicht vorliegt.

**Messumgebung:** Fenster `Nightreign Helper 1.7.1`, `.venv\Scripts\python.exe
run.py`, Bildschirm 2560x1600 physisch bei 150 % Windows-Skalierung
(= 1707x1067 logisch), Fensterbreiten 1250 / 1600 / 2100 physisch.
Headless-Messungen mit `QT_QPA_PLATFORM=offscreen` gegen
`%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`.

---

### 1. Was fuer alle sechs Tabs gilt

#### 1.1 Das Kopfmuster (A10)

Drei der sechs Tabs haben es bereits und tragen es gut (`Deep of Night`,
`Red variants`, `World Events`), drei nicht (QA-138). Es wird das Muster
**aller sechs**:

1. **Zeile 1 — Ueberschrift.** `_heading(...)` in der bestehenden Form:
   `color: #c8a45c; font-size: 12px; font-weight: bold; letter-spacing: 1px`,
   Text in GROSSBUCHSTABEN. Die Ueberschrift ist **die Frage oder das Ziel**,
   nicht der Bestand.
2. **Zeile 2 — Fragesatz.** Ein `QLabel`, `color: #8a8a8a; font-size: 11px`,
   `setWordWrap(True)`, direkt darunter. Er sagt in einem Satz, welche Frage
   der Tab beantwortet, und wo noetig, welche er **nicht** beantwortet.
3. **Erst danach** Filterzeile, Bestandszaehlung und Inhalt. Die heutige
   Bestandszaehlung (`577 buffs (blue) then 75 curses (red). …`) bleibt, aber
   sie ist nie das Erste, was der Leser trifft.

**AK-68** Jeder der sechs Tabs zeigt beim Erstoeffnen, **oberhalb jedes
Bedienelements und jeder Zahl**, eine `_heading()`-Ueberschrift und
unmittelbar darunter genau einen Fragesatz-Absatz in `#8a8a8a`/11 px mit
`setWordWrap(True)`. Die Wortlaute stehen in §2 bis §7 und sind wortgleich zu
uebernehmen. Ein Test, der den ersten sichtbaren Textknoten jedes der sechs
Tab-Widgets ausliest, findet dort die Ueberschrift — auf keinem Tab eine
Zahl, einen Filter oder eine Bestandszeile.

#### 1.2 Keine Zahl ohne Bezugsgroesse (A12, QA-128)

**AK-69** Auf keinem der sechs Tabs steht eine Zahl, deren Einheit **und**
deren Bezugsgroesse nicht entweder in ihrer eigenen Zeile oder in genau einem
Erklaersatz desselben Abschnitts benannt ist. Die zehn heute offenen Stellen
sind in §2 bis §7 einzeln mit ihrem verbindlichen Wortlaut aufgefuehrt; ein
Test, der die zehn Zeichenketten sucht, findet zu jeder den zugehoerigen
Erklaersatz auf demselben Tab.

**AK-70** Wo die Bezugsgroesse **auch im Code nicht bekannt** ist, sagt der
Bildschirm das, statt die Zahl kommentarlos zu zeigen oder sie wegzulassen
(GOAL A7, ausgedehnt auf die Anzeige). Der Wortlaut fuer diesen Fall ist je
Stelle unten festgelegt und enthaelt immer die Formel *„the files do not
say"*. Betroffen heute: `Reward multiplier` (§5), `Refills at` (§4),
`… buildup` (§3), `stamina recovery speed +5` (§7).

#### 1.3 Nichts abgeschnitten, nichts halb da (A13)

Drei eigene Befunde am laufenden Fenster, alle *(visuell)* und *(gemessen)*:

- **Der `Nightlords`-Tab zeigt bei 1600 px Fensterbreite acht von zehn
  Nightlords.** Das Kartenraster ist auf `COLUMNS = 4` fest verdrahtet
  (`bosstab.py:35`), das Detailpanel daneben auf `setFixedWidth(330)`
  (`bosstab.py:288`), und beide sitzen in einer `QHBoxLayout` — also
  **nicht** in einem verschiebbaren Splitter. Spalte 3 (Gnoster, Caligo)
  bricht mitten im Satz ab, Spalte 4 (**Maris** und **Harmonia**) ist
  vollstaendig unsichtbar, waehrend die Kopfzeile „10 Nightlords" behauptet.
  Bei 2100 px erscheinen beide Karten — der Beweis, dass es Layout ist und
  nicht Daten.
  Belege: `docs/screenshots/2026-09-05-T056/tab3-nightlords.png` (acht) gegen
  `…/tab3-nightlords-wide2100.png` (zehn, Maris und Harmonia in Spalte 4).
  Die waagerechte Bildlaufleiste, ueber die man Spalte 4 theoretisch
  erreichte, sitzt an der Unterkante des Tabs — und die liegt auf diesem
  Bildschirm hinter der Taskleiste (siehe dritter Punkt).
  Beleg: `…/zoom-nightlords-bottom.png`.
- **Der `Weapons & spells`-Tab schneidet die letzte Kachelspalte ab**, und
  weil die Werte rechtsbuendig stehen, verschwinden **die Zahlen zuerst**:
  auf der abgeschnittenen Kachel steht `AR`, `Physical`, `Magic` — ohne einen
  einzigen Wert. Ursache: `COLUMNS = 5` fest (`arsenaltab.py:15`) bei
  `CARD_WIDTH = 200`. Reproduziert bei 1600 px (5. Spalte) und bei 1250 px
  (4. Spalte).
  Belege: `…/zoom-tile-clipped.png`, `…/tab2-weapons-narrow1250.png`.
- **Das Fenster passt auf diesem Bildschirm nicht ueber die Taskleiste.**
  Gemessen: die Mindesthoehe des Fensters betraegt **1606 physische px**
  (getestet mit `MoveWindow` auf 500/700/1000/1300 — das Fenster bleibt bei
  1606). Der Bildschirm ist 1600 hoch, die Arbeitsflaeche nach Taskleiste
  ~1552. Verursacher ist **ein einziger Tab**: `Deep of Night` meldet
  `minimumSizeHint().height() = 949` logische px, alle anderen fuenf melden
  111 bis 443. `deeptab.py` hat **keine** `QScrollArea` und setzt vier
  Tabellen per `setFixedHeight`. Folge: die beiden letzten Erklaerzeilen des
  Tabs (*„The cursed-relic rates do not move with depth."*, *„Read from the
  game's own depth table."*) sind auf diesem Bildschirm nie sichtbar und
  **nicht scrollbar erreichbar**.
  Belege: `…/tab4-deep.png` (unten abgeschnitten) gegen
  `…/zoom-deep-bottom.png` (dieselbe Stelle, Fenster nach oben geschoben).

**AK-71** Kein Tab setzt eine Mindesthoehe ueber **860 logische px**
(`minimumSizeHint().height()`), gemessen an einer echten Widget-Instanz. Wo
der Inhalt hoeher ist, ist er in einer `QScrollArea` mit
`setWidgetResizable(True)`. Ein Test, der die sechs Tab-Widgets baut und ihre
`minimumSizeHint()` abfragt, findet **keinen** Wert ueber 860; der heutige
Ausreisser ist `Deep of Night` mit 949.

**AK-72** Kein Kachel- oder Kartenraster hat eine feste Spaltenzahl. Die
Spaltenzahl folgt aus der verfuegbaren Breite (`max(1, breite //
(kartenbreite + abstand))`), und es wird **nie eine Kachel teilweise
gezeichnet**. Ein Test, der `BossTab` bzw. `ArsenalTab` auf 1250, 1600 und
2100 logische px setzt, findet bei jeder Breite: alle Karten vollstaendig
sichtbar, `horizontalScrollBar().isVisible()` **False**, und im
`Nightlords`-Tab alle **zehn** Kartennamen im ausgelesenen Text.

**AK-73** Keine angezeigte Zeichenkette bricht mitten in einem Begriff um.
Verbindlich fuer die Wertzeilen der Waffenkachel: ein Wert aus mehreren
`·`-getrennten Gruppen bricht **nur zwischen zwei Gruppen** um, nie
innerhalb einer. Der heutige Bruch `STR -7 · ARC +45 · DEX` / `-7` ist damit
ausgeschlossen. Beleg des Ist-Zustands: `…/zoom-tile-wrap.png`.

> **Korrektur an meiner eigenen Vorgabe.** `DESIGN_REVIEW.md`, T-052,
> Abschnitt „Positiv / beibehalten", hat die Arsenal-Kachel als Vorbild
> gegen DR-009 gelobt („Bezeichnung und Wert in getrennten, gestapelten
> Zeilen"). Das galt fuer den damals geprueften Fall (`Spell power` / `145`,
> ein kurzer Wert). Fuer die langen Skalierungswerte trifft dasselbe
> Muster denselben Fehler wie DR-009 — nur eine Zeile tiefer. Das Lob bleibt
> fuer den Einzelfall richtig und **taugt nicht als allgemeine Regel**;
> AK-73 ersetzt es als Regel.

#### 1.4 Farbrollen brauchen eine Legende (A12)

Der `Nightlords`-Tab benutzt heute **drei** Farbrollen ohne jede Legende
*(visuell,* `…/tab3-nightlords-gladius.png`*)*: gruen fuer die Schwaeche in
der Schadenstafel, gruen fuer die leichtesten Statuswerte, und ein
abweichendes Gruen (`OBSERVED_COLOUR`) fuer im Spiel Gesehenes. QA-131 nennt
denselben Mangel.

**AK-74** Jede Farbe, die auf einem der sechs Tabs eine **Bedeutung** traegt
(und nicht nur Typografie ist), wird auf demselben Tab genau einmal benannt —
in einem Satz oder einer Legendenzeile, nicht nur in einem Tooltip.
Betroffen: gruen im `Nightlords`-Tab (zwei Bedeutungen, siehe §4), blau/rot
im `Effects`-Tab, blau als „community-reported" im `Red variants`- und im
`World Events`-Tab (dort heute schon korrekt benannt — das ist das Vorbild).

#### 1.5 Ein Gedankenstrich, nicht zwei Bindestriche

*(gemessen)* In den sieben Modulen der sechs Tabs enthalten **23**
String-Literale ` -- ` und **24** ein `—`; darunter sind angezeigte
Zeichenketten beider Sorten, teils nebeneinander (`depthstab.py:87` zeigt
*„individual empowered enemies -- the same enemy"*, waehrend der Nachbartab
*„Lasts the rest of the expedition — not consumed"* zeigt).

**AK-75** In keiner **angezeigten** Zeichenkette der sechs Tabs steht ` -- `.
Der Gedankenstrich ist `—` (U+2014), mit Leerzeichen davor und danach.
Docstrings und Kommentare sind ausgenommen. Ein Test, der den sichtbaren Text
aller sechs Tabs einsammelt, findet **0** Vorkommen von ` -- `.

---

### 2. `Effects & chances`

#### 2.1 Die Frage, und wo sie steht

> **Ueberschrift:** `WHAT A RELIC CAN ROLL, AND HOW OFTEN`
>
> **Fragesatz:** `Every effect a relic can carry, how likely you are to roll
> it, and whether carrying a second copy is worth anything.`

**AK-76** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich, oberhalb der
Filterzeile. Die heutige Bestandszeile (`577 buffs (blue) then 75 curses
(red). …`) rutscht darunter und behaelt ihren Stil.

#### 2.2 Die Tabelle: Breite folgt Bedeutung

*(gemessen, headless, `EffectsTab` auf drei Breiten)* — die zwei Spalten, die
die Frage beantworten, bekommen heute nur, was die anderen neun uebriglassen:

| Tabellenbreite | `Effect` | `What it does` | zusammen | Rest (9 Spalten) |
|---|---|---|---|---|
| 1516 px | **22 px** | **21 px** | 43 px (2,8 %) | 1473 px |
| 1856 px | 192 px | 191 px | 383 px (21 %) | 1473 px |
| 2356 px | 442 px | 441 px | 883 px (37 %) | 1473 px |

Bei 1516 px sind **652 von 652** Effektnamen und **652 von 652**
Beschreibungen breiter als ihre Zelle; selbst bei 2356 px sind es noch
333 bzw. 457. *(visuell, `…/tab1-effects.png`)*: vier aufeinanderfolgende
Zeilen lesen sich als `Successful …`, `Successful …`, `Successful …`,
`Successful …` und sind voneinander nicht zu unterscheiden.

Die 1473 px gehen an Spalten mit sehr wenig Information *(gemessen)*:
`Colours` 295 px fuer **10** verschiedene Zeichenketten (491 von 652 Zeilen
zeigen dieselbe: `Red, Blue, Yellow, Green`), `Stacking` 343 px fuer 9,
`Comes with curse` 214 px fuer 4 (302 davon leer), `Copies` 94 px fuer eine
Spalte, die in 638 von 652 Zeilen `1` zeigt, `Type` 70 px fuer 2 Werte, die
die Textfarbe bereits sagt.

Ursache *(gemessen)*: `refresh()` ruft `resizeColumnsToContents()` und setzt
danach nur Spalte 0 und Spalte 10 auf `QHeaderView.Stretch` — Stretch bekommt
per Definition, was uebrig ist, und uebrig ist bei 1516 px nichts.

**AK-77** Im `Effects`-Tab ist `Effect` die breiteste Spalte der Tabelle, bei
jeder Fensterbreite. Verbindlich: `Effect` bekommt mindestens **320**
logische px und `What it does` mindestens **260**, bevor irgendeine andere
Spalte mehr als ihre Kopfzeilenbreite bekommt; die uebrigen Spalten sind
`ResizeToContents` mit einer Obergrenze, die kleiner ist als die Breite von
`Effect`. Ein Test, der die Tabelle auf 1516 logische px setzt, findet
`sectionSize(0) >= 320` und `sectionSize(0) > sectionSize(i)` fuer alle
i != 0. Ein Effektname von 40 Zeichen ist bei 1516 px vollstaendig lesbar.

#### 2.3 `Pools` — die Zahl, die ihren eigenen Namen widerlegt

**Befund (QA-125, zwei unabhaengige Belege):** die Spalte zaehlt keine Pools,
sondern (Relikt x Effektplatz)-Vorkommen. Die Identitaet
`333 167 + 5 760 = 338 927` geht exakt auf; das Spiel definiert laut
Direktlesung nur **598** Pool-Tabellen, waehrend die Spalte bis **1 110**
zeigt *(gemessen: Wertebereich der Spalte heute 0 bis 1 110)*. Der eigene
Tooltip erklaert zusaetzlich, dass die Spalte die Frage nicht beantwortet:
*„More pools does not mean more likely — the two chance columns say that."*
*(zweiter Hand)* Der `power-user` nannte die Zahl fuer etwas, das er sich als
Ziehtoepfe vorstellte, „riesig".

**Entscheidung:** Der Zustand „steht da und heisst falsch" endet. Ich
**schlage die Streichung der Spalte vor** (§8) und lege fuer beide Ausgaenge
fest, was gilt:

**AK-78** In der Effektetabelle steht **keine** Spalte mehr mit der
Ueberschrift `Pools`.

- *Ausgang A (mein Vorschlag, Streichung):* Die Spalte entfaellt. Ihre
  einzige heute tragende Funktion — die `0` als Signal „unter diesen Filtern
  nicht erreichbar" — wandert vollstaendig in die Chance-Zellen, die dafuer
  bereits einen Tooltip haben; die Chance-Zelle zeigt in diesem Fall `—` und
  traegt den Tooltip `No relic effect slot can roll this under the current
  colour and mode filters. It exists as a rung of its ladder; other filters
  may reach it.` Die Zahl selbst bleibt als Teil des Chance-Tooltips
  erhalten, korrekt benannt: `{n} of the game's relic effect slots can roll
  this.`
- *Ausgang B (der App Designer behaelt sie):* Die Spalte heisst
  `Relic slots`, und ihr Kopf-Tooltip lautet wortgleich: `How many of the
  game's relic effect slots can roll this effect, counted over every relic
  and every slot on it. It is not a count of loot pools, and more slots does
  not mean more likely — the chance column says that.`

In **beiden** Ausgaengen gilt: die Zeichenkette `A pool is one of the lists a
relic's effects are drawn from` kommt im Baum nicht mehr vor.

#### 2.4 `Avg chance` und `Best chance` — erst die Definition

**Befund (QA-126):** die Spalte ist ein **ungewichtetes** Mittel ueber
(Farbe x Modus)-Eimer. Sie entspricht weder dem Tooltip (*„averaged over
every pool"*) noch der Zusammenfassung (*„how likely an effect is on one
roll"*) — beide stehen gleichzeitig auf demselben Bildschirm und sagen
Verschiedenes. **129 von 616** Effekten aendern ihre Prozentzahl bei
Gewichtung nach Vorkommen; der schlimmste Fall zeigt **20,4 %** statt
**0,91 %** (Faktor 22,3).

Dazu ein zweiter, unabhaengiger Mangel derselben Zusammenfassungszeile
*(visuell, `…/tab1-effects.png`)*: sie sagt *„on one roll of the selected
colour and mode"*, waehrend die Voreinstellung `All colours` ist — es ist gar
keine Farbe gewaehlt.

**Was ich entscheide, weil es objektiv ist:**

**AK-79** Die heutige ungewichtete Mittelung ueber Farb-/Modus-Eimer wird
nicht ausgeliefert. Auf dem Bildschirm steht zu den Chance-Zahlen **genau
eine** Definition, an **genau einer** Stelle, und sie nennt (a) die
Bezugsgroesse „per relic effect slot", (b) dass die aktuellen Filter darin
stecken, und (c) dass die Zahl **nicht** die Wahrscheinlichkeit pro Relikt
oder pro Lauf ist. Verbindlicher Wortlaut des einen Satzes:
`Chance is per relic effect slot, over every slot that can roll the effect
under the filters above — not per relic and not per run.`
Der heutige Tooltip-Satz *„averaged over every pool that can produce it"* und
der heutige Zusammenfassungs-Halbsatz *„how likely an effect is on one roll
of the selected colour and mode"* kommen im Baum nicht mehr vor. Ein Test,
der den sichtbaren Text des Tabs einsammelt, findet die Zeichenkette
`per relic effect slot` **genau einmal**.

**AK-80** Der angezeigte Mittelwert ist nach Vorkommen gewichtet, nicht ueber
Eimer gemittelt. Pruefbar an dem in QA-126 aufgeschluesselten Einzelfall:
`[Wylder] Improved Mind, Reduced Vigor` zeigt **0,91 %**, nicht 20,4 %.

**Was ich nicht entscheide** — siehe §10, Frage 1: ob der Tab nach der
Korrektur **zwei** Zahlenspalten behaelt (gewichteter Mittelwert + bester
Fall) oder **eine** Spannenspalte (`0.5 – 100 %`). Beide sind nach AK-79 und
AK-80 ehrlich; die Wahl ist eine Frage der Tabellendichte und gehoert dem App
Designer.

#### 2.5 `Tier` und `Copies` (QA-127)

**AK-81** `Tier` und `Copies` werden aus dem **ungefilterten** Effektbestand
gebildet; die Filter bestimmen nur, welche Zeilen sichtbar sind. Pruefbar:
`Continuous HP Recovery` traegt bei `All colours` `1 of 2` / `2 of 2` und
traegt dieselbe Leitersprosse auch bei Farbfilter `Red`, statt eine leere
Zelle zu zeigen.

---

### 3. `Weapons & spells`

#### 3.1 Die Frage, und wo sie steht

> **Ueberschrift:** `WHICH ARMAMENT HITS HARDEST FOR YOUR BUILD`
>
> **Fragesatz:** `Every armament and spell in the game, rated for the
> Nightfarer, level and upgrade set above. Spell damage is not in the game's
> data, so spells show what they cost you instead.`

**AK-82** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich. Die heutige
Zusammenfassung (`Wylder at level 1, +1 — VIG 10 … 1952 shown. …`) rutscht
darunter; ihr letzter Satz (*„Spell damage is not in the game's data, so
spells show their costs instead."*) entfaellt dort, weil er jetzt im
Fragesatz steht — er darf nicht zweimal auf demselben Bildschirm stehen.

#### 3.2 Der Erstzustand ist heute leer

*(visuell, `…/tab2-weapons.png`)* Beim ersten Oeffnen zeigt der Tab drei
zugeklappte Ueberschriften — `Weapons (1792)`, `Sorceries (67)`,
`Incantations (93)` — und darunter **rund 95 % leere schwarze Flaeche**.
Ursache: `Section.toggle.setChecked(False)` (`arsenaltab.py:139`);
aufgeklappt wird nur bei einer Suche mit hoechstens 60 Treffern
(`arsenaltab.py:302`). Der Kommentar dort benennt das Problem bereits fuer
den Suchfall (*„which made searching feel broken"*), zieht aber den
Erstzustand nicht nach.

**AK-83** Beim ersten Oeffnen des Tabs ist mindestens ein Abschnitt
aufgeklappt und mindestens eine Waffenkachel sichtbar, ohne dass der Nutzer
etwas anklickt oder tippt. Ein Test, der `ArsenalTab` baut und die sichtbaren
`Tile`-Widgets zaehlt, findet **> 0**.

#### 3.3 Die Kachel

**AK-84** *(setzt AK-72 und AK-73 fuer diesen Tab um)* Bei 1250, 1600 und
2100 logischen px ist jede gezeichnete Kachel vollstaendig sichtbar,
einschliesslich ihrer rechtsbuendigen Werte; kein `AR`, `Physical` oder
`Magic` steht ohne seine Zahl.

**AK-85** Die Skalierungszeile nennt ihre Skala. Der Tab traegt dazu genau
einen Satz, im Zusammenfassungsblock, wortgleich:
`Scaling is the game's own per-stat figure behind the letter grade it shows
in menus. Compare these figures with each other; the files do not say which
letter a figure earns.`
Ein Test findet diesen Satz genau einmal, und er steht auf dem Tab, auf dem
`Scaling ` auf 1 792 Kacheln erscheint.

**AK-86** Die Aufbau-Zeilen (`Blood Loss buildup`, `Poison buildup`,
`Frost buildup`, …) tragen ihren Geltungsbereich. Wo der Extraktor die
Bezugsgroesse kennt, steht sie in der Zeile; wo er sie nicht kennt, steht im
selben Zusammenfassungsblock wortgleich:
`Buildup figures come straight from the game's weapon data. The files do not
say what they are counted against, so use them to compare armaments, not as a
number of hits.`
AK-70 verlangt genau diesen Fall; welche der beiden Fassungen greift,
entscheidet der Kenntnisstand des Extraktors, nicht der Geschmack.

**AK-87** Die Zauberkachel benennt ihre Kosten als Kosten: `FP` heisst
`FP cost`, `Stamina` heisst `Stamina cost`. Die Zeile `Slots` entfaellt (§8)
oder heisst `Spell slots` — sie zeigt heute auf 160 von 160 Zauberkacheln `1`.

**AK-88** *(QA-139)* Dieselbe Groesse heisst auf demselben Bildschirm einmal.
Auf der Kachel steht `Spell power`; der Zusammenfassungssatz aus AK-64 sagt
heute *„the spell scaling the game displays for them"*. **Entscheidung:
`spell power` gewinnt**, weil dieser Ausdruck auf bis zu 1 792 Kacheln stehen
kann und der Satz nur einmal. Der Satz aus AK-64 lautet ab jetzt wortgleich:
`Staves and seals show the spell power the game displays for them instead of
an attack rating.` Die Zeichenkette `spell scaling` kommt im Baum nicht mehr
vor. **Betroffenes Akzeptanzkriterium: AK-64** — nur dieses eine Wort
geaendert, Stellung und Rest des Satzes unveraendert.

---

### 4. `Nightlords`

#### 4.1 Die Frage, und wo sie steht

> **Ueberschrift:** `HOW TO HURT EACH NIGHTLORD`
>
> **Fragesatz:** `What each Nightlord takes extra damage from, what breaks
> its stance, and what it does to you once it is broken. Click a card for the
> full profile.`

**AK-89** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich. Die heutige
Zeile (`10 Nightlords · 8 also have an Everdark Sovereign … click a card for
damage taken, status buildup and more`) rutscht darunter und verliert ihren
Klick-Hinweis, weil er jetzt im Fragesatz steht.

#### 4.2 Alle zehn Karten

**AK-90** *(setzt AK-72 fuer diesen Tab um, eigener Befund)* Bei 1250, 1600
und 2100 logischen px sind **alle zehn** Nightlord-Karten vollstaendig
sichtbar und ihre Blurb-Texte vollstaendig lesbar. Ein Test, der den
sichtbaren Text des Kartenbereichs bei 1600 px einsammelt, findet die Namen
`Maris` und `Harmonia`. Beleg des Ist-Zustands: `…/tab3-nightlords.png`
(acht) gegen `…/tab3-nightlords-wide2100.png` (zehn).

#### 4.3 Die Zahlen im Detailpanel

**AK-91** *(QA-128 Punkte 4 bis 6, AK-74)* Das Detailpanel traegt drei
Erklaerzeilen, je einmal je Abschnitt, wortgleich:

- unter `DAMAGE TAKEN`: `Bars compare this Nightlord's damage types with each
  other, not with another Nightlord. Green marks the type it is weak to.`
- unter `STATUS BUILDUP`: `How much status you have to apply before it lands
  — lower is easier. Green marks this Nightlord's easiest statuses.`
- unter `STANCE`: `Bar to break is in the game's own stance points. The
  refill figure is the rate the files give; they do not say what it is per,
  so compare it between Nightlords rather than reading it as a speed.`

**AK-92** *(QA-130)* Kein Sentinel wird als Zahl gedruckt. `Refills at x-1`
kommt nicht vor: bei `stance.recovery <= 0` entfaellt die Zeile, oder sie
lautet `Refills at — not in the game's files` (A7). Pruefbar an Maris, dem
einzigen der zehn mit `recovery = -1.0`.

**AK-93** *(QA-131)* Der Abschnitt `WEAKNESS SPECIAL INTERACTION` erscheint,
sobald der Nightlord **irgendeine** Schwaeche traegt — Schadensart **oder**
Status. Pruefbar an Adel: sein Panel zeigt den Abschnitt und die dafuer
hinterlegte Notiz (*„Phase 1 only — the poison stagger is gone in phase 2 and
in the Everdark version."*), statt direkt mit `DAMAGE TAKEN` zu beginnen.

**AK-94** *(QA-129, Herkunft)* Zeilen, die auf einer Sichtung beruhen und
nicht in den Spieldateien stehen, tragen `OBSERVED_COLOUR` (`#7fae72`) —
dieselbe Farbe, die der Tab fuer `WEAKNESS_NOTE` bereits benutzt. Betroffen
sind heute `Debuff x2.0 damage taken`, `Debuff x0.8 attack power` und
`Stacks: yes — repeats compound`. Ein Test, der die Textfarbe dieser drei
Zeilen liest, findet `#7fae72` und nicht die Farbe der extrahierten Werte.
*(Ob die Zahlen selbst richtig sind und ob `ladder.down` zusaetzlich gezeigt
wird, ist der Rechenteil von QA-129 und gehoert dem `developer` — diese
Vorgabe regelt nur, dass man einer Zahl ansieht, woher sie kommt.)*

---

### 5. `Deep of Night`

Dieser Tab ist gestalterisch der beste der sechs und bleibt das Vorbild fuer
die anderen fuenf: Ueberschrift, Tabelle, Erklaernote, Herkunftszeile. Er
bekommt nur ein Dach und drei Bezugsgroessen.

> **Ueberschrift (neu, ueber den vier vorhandenen):** `DEEP OF NIGHT`
>
> **Fragesatz:** `What a deeper run pays you, what it costs you, and how your
> Depth rating moves. All figures compare a Deep of Night run with a normal
> expedition.`

**AK-95** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich; die vier
bestehenden Ueberschriften (`WHAT EACH DEPTH IS WORTH`, `HOW MUCH TOUGHER
ENEMIES GET`, `WHAT MOVES YOUR RATING`, `WHAT ELSE CHANGES WITH DEPTH`)
bleiben unveraendert darunter. Der zweite Satz des Fragesatzes ist zugleich
die Bezugsgroesse fuer die Skalierungstabelle (QA-128 Punkt 9) und wird nicht
zusaetzlich unter der Tabelle wiederholt.

**AK-96** *(QA-128 Punkte 7 und 8, AK-70)* Die beiden Zeilen des obersten
Blocks nennen ihren Bezug bzw. sagen, dass er nicht bekannt ist. Verbindlich,
als Note unter der ersten Tabelle:

- `Reward multiplier: the game's own multiplier for this Depth. The files do
  not say what it multiplies, so it is shown as a comparison between Depths
  and nothing more.`
- `Sovereign Sigil: the figure comes from the depth table. That the item is
  the Sovereign Sigil was identified in game, not read from a link in the
  files.`

Dazu erscheint der bereits geladene, heute nie gezeigte Satz aus
`deep_of_night.sigil_info` (*„rays of everdark used for bartering in the
Roundtable Hold"*) einmal unter der ersten Tabelle. Das ist **keine neue
Funktion**: das Feld wird heute geladen und weggeworfen.

**AK-97** *(eigener Befund, setzt AK-71 fuer diesen Tab um)* Der Inhalt des
Tabs liegt in einer `QScrollArea`; die vier Tabellen setzen keine feste
Hoehe mehr, die das ganze Fenster bindet. Ein Test findet
`DeepTab().minimumSizeHint().height() <= 860` und erreicht die letzte
Erklaerzeile (`Read from the game's own depth table.`) bei einer
Fensterhoehe von 900 logischen px durch Scrollen.

---

### 6. `Red variants`

#### 6.1 Erst die Frage, dann der Inhalt

**Geprueft, ob die Daten die Frage „was ist an einer roten Variante anders"
hergeben** *(gemessen, am Datensatz)*: `deep_of_night.mutations` traegt je
Eintrag genau `id`, `counts` (fuenf Tiefen), `category`, `group`, `varies` —
**keine Staerkefaktoren, keine HP- oder Schadenszahlen**.
`deep_of_night.kinds` traegt Roster (`rows`, `chrs`, `tiles`) **ohne
Kartendimension** (das ist zugleich die Wurzel von QA-132). Die Daten sagen
also **nicht**, um wie viel staerker eine rote Variante ist.

Was sie sagen, steht heute schon da — aber an der falschen Stelle. Der
Intro-Absatz enthaelt die Antwort im Nebensatz (*„the same enemy, stronger,
never a different one"*), und die community-berichtete Zeile darunter enthaelt
den handfesten Teil (*„red enemies always drop a weapon, and red mini-bosses
are guaranteed a unique-tier armament"*). *(zweiter Hand)* Der `power-user`
fand die Antwort nicht und nannte den Tab den ueberfluessigsten der sechs —
was zu einer Ueberschrift passt, die `RED VARIANTS BY DEPTH` heisst und damit
Stueckzahlen ankuendigt.

> **Ueberschrift:** `RED VARIANTS: WHAT THEY ARE, AND HOW MANY`
>
> **Fragesatz:** `A red variant is the same enemy made stronger — never a
> different enemy. The game's files do not say by how much. What they do say
> is how many of each sort a run places on a map, and that is the table
> below.`

**AK-98** Der Tab oeffnet mit diesen beiden Zeilen, wortgleich. Der heutige
Intro-Absatz verliert seinen ersten Nebensatz (er steht jetzt im Fragesatz)
und behaelt den Rest; die `COMMUNITY-REPORTED`-Zeile bleibt unveraendert und
steht direkt darunter, weil sie den zweiten Teil derselben Antwort traegt.
Der Satz `The figures are how many red variants of each sort a run puts on
the selected map.` bleibt an der Tabelle — er ist heute die vorbildlichste
Bezugsgroessen-Zeile der sechs Tabs und wird nicht angefasst.

#### 6.2 Die Spalte `For example` (QA-132)

*(visuell, `…/tab5-redvariants.png`)* Die Spalte ist die **breiteste** der
Tabelle (~870 physische px), ist fuer die **groesste** Zeile (`Ordinary
enemies in camps & ruins`, 32 von 87) leer, und zeigt auf allen sechs Karten
dieselben Namen, obwohl die Tabelle daneben *„on the selected map"* sagt.

**AK-99** Die Spalte behauptet keinen Kartenbezug, den die Daten nicht
tragen. Zwei zulaessige Ausgaenge, beide pruefbar:

- *Ausgang A:* Die Namen werden an die Kartengruppe gebunden (falls die
  Rosterdaten das je hergeben) — dann aendert sich der Zellinhalt beim
  Kartenwechsel.
- *Ausgang B (heute der einzig moegliche):* Die Spalte heisst
  `Examples (any map)` und ihr Kopf-Tooltip lautet wortgleich:
  `Named members of this group anywhere in the game. The files do not list
  them per map, so these names are not tied to the map selected above.`

In **beiden** Ausgaengen gilt fuer die zwei Zeilen ohne benannte Mitglieder
(`Ordinary enemies in camps & ruins`, `Unidentified enemies`): die Zelle
bleibt nicht leer, sondern traegt `— the files name none` (A7). Und die
Spalte ist **nie breiter** als die Spalte `What can be red`.

#### 6.3 Die doppelten Tiefenspalten

*(QA, visuell bestaetigt)* Fuer alle sechs Karten und in 22 von 22
Datenzeilen gilt Depth 2 = Depth 3 und Depth 4 = Depth 5.

**AK-100** Die Tabelle sagt das, statt es fuenfmal zu wiederholen. Die
Spaltenkoepfe lauten `Depth 1`, `Depth 2–3`, `Depth 4–5`, solange die Daten
das hergeben; weichen sie fuer irgendeine Karte ab, faellt die Tabelle
automatisch auf fuenf Einzelspalten zurueck. Ein Test, der eine Zeile mit
fuenf verschiedenen Werten einspeist, findet danach fuenf Spaltenkoepfe.

---

### 7. `World Events`

Dieser Tab beantwortet seine Frage bereits und sagt sie auch. Er bekommt
fuenf Praezisierungen.

> **Ueberschrift:** `WORLD EVENTS` *(unveraendert)*
>
> **Fragesatz** *(der heutige Absatz, unveraendert — er erfuellt AK-68
> bereits):* `Events that can interrupt an expedition: where each one can
> appear, what happens, what you win and what you lose. Blue lines are
> community-reported; everything else is the game's own data.`

**AK-101** *(QA-134)* Der Tagesatz unterscheidet zwischen den Ereignissen,
statt auf 11 von 11 wortgleich zu stehen. Er nennt die Verteilung, die im
Datensatz liegt und heute verworfen wird — Beispiel `Judgment`: 19 Day-1-
gegen 1 Day-2-Muster. Verbindliches Muster:
`Can fire on Day 1 or Day 2 — {d1} of the {n} map patterns that carry it are
Day 1.` Ein Test findet fuer `Judgment` und `Fire-Summoning Beasts`
**verschiedene** Zeichenketten an dieser Stelle.

**AK-102** *(QA-134, A12)* Die Prozentzahl nennt ihren Geltungsbereich und
sagt, was sie **nicht** ist. Der Satz lautet wortgleich:
`The percentage is how much of that Nightlord's map pool carries the event.
The pool is drawn with weights, so it is not the chance of seeing it on a
given run.` Die Allaussage `Every other Nightlord: never.` bleibt, bekommt
aber ihren Beleg: `Every other Nightlord: never — across every map pattern
in the game's data.`

**AK-103** *(QA-133)* Eine Dauer steht nur an einer Zeile, die einen
**Zustand** beschreibt. Eine Zeile, die einen Betrag gewaehrt, traegt keine.
Pruefbar an drei Stellen: `10,000 runes` (ohne `for 1s`),
`restores 100 stamina` (ohne `for 0.3s`), `invulnerable for 5s` (mit, weil
das ein Zustand ist). Eine Dauer von `0.0` ist keine Angabe und wird nicht
als `for 0s` gedruckt.

**AK-104** *(QA-135)* Herleitungs- und Quellensprache steht nicht im
Fliesstext. Die Regel des Modulkopfs von `eventstab.py` (*„Everything about
how any of it was derived stays in the project's documents — none of it
belongs on screen."*) **bleibt in Kraft** — das ist meine Antwort auf die
offene Frage 4 aus T-055. Konkret: die Zeichenketten `fextralife`, `game8`,
`Eldenpedia`, `thefifthmatt`, `pattern modifier` und
`the row this project had wrong` kommen in keinem angezeigten Text vor. Was
bleibt, ist die Aussage, die den Spieler angeht — `Sources disagree: {was}` —
und, falls der App Designer die Quellen sehen will, das strukturierte Feld
`sources` als eigene, ruhige Zeile unter dem Absatz, nicht im Absatz. Der
heute geladene und nie gezeigte `rune_scaling`-Text beziffert die einzige
unbezifferte Behauptung des Tabs (*„rises the more expeditions you have
cleared"*) und erscheint an genau dieser Zeile — auch das ist **keine neue
Funktion**, sondern ein geladenes Feld.

**AK-105** *(QA-136)* `Scale-Bearing Merchant` steht einmal in der Liste,
oder die beiden Eintraege verweisen sichtbar aufeinander. Ein Test, der die
Listeneintraege zaehlt, findet den Namen **einmal** — oder findet im Text des
einen Eintrags einen Verweis auf den anderen.

---

### 8. Streichvorschlaege je Tab

**Ich schlage vor, ich entscheide nicht** (GOAL A10). Jeder Eintrag mit dem
Satz, was ein Spieler verliert. Reihenfolge: staerkster Vorschlag zuerst.

**Effects & chances**

1. **Spalte `Pools`** (AK-78, Ausgang A). *Wenn das weg ist, verliert ein
   Spieler* nichts Benutzbares — ihr eigener Tooltip sagt das. Das 0-Signal
   wandert in die Chance-Zelle.
2. **Spalte `Copies`.** 638 von 652 Zeilen zeigen `1` *(gemessen)*. *Wenn das
   weg ist, verliert ein Spieler* die Information, dass 14 Effekte mehrfach
   definiert sind — was an keiner Rolle etwas aendert.
3. **Spalte `Type`.** Zwei Werte, die die Textfarbe bereits sagt *(gemessen:
   2 verschiedene Zeichenketten auf 652 Zeilen)*. *Wenn das weg ist, verliert
   ein Spieler* die Sortierung, die heute Buffs und Fluche gruppiert. **Nur
   streichen, wenn die Gruppierung anders erhalten bleibt** — sonst ist der
   Verlust groesser als der Gewinn.
4. **Spalte `Colours` auf eine Kurzform** (vier Farbpunkte statt
   `Red, Blue, Yellow, Green`). 491 von 652 Zeilen zeigen dieselbe
   Zeichenkette in 295 px *(gemessen)*. *Wenn das weg ist, verliert ein
   Spieler* nichts: die Information bleibt, die Breite geht an `Effect`.

**Weapons & spells**

1. **Die Wiederholung der Kopfzahl bei einschichtigen Waffen** — 655 von
   1 792 Kacheln drucken `AR 49` und darunter `Physical 49` *(QA)*. *Wenn das
   weg ist, verliert ein Spieler* nichts; die Typzeile verdient ihren Platz
   ab zwei Schadensarten.
2. **Zeile `Slots` auf Zauberkacheln.** 160 von 160 zeigen `1` *(QA)*. *Wenn
   das weg ist, verliert ein Spieler* nichts — bis das Spiel je einen Zauber
   mit zwei Plaetzen bekommt.
3. **Nicht streichen: `vs standard`.** Die einzige Zeile, die den Unterschied
   zur Standardfassung beziffert.

**Nightlords**

1. **Der Klammerzusatz `(smallest Harmonia 75, largest Caligo 160)`** auf
   allen zehn Panels. *Wenn das weg ist, verliert ein Spieler* die Skala fuer
   `Bar to break` — also einmal an den Tabkopf, nicht zehnmal ins Panel.
2. **`Stacks: yes — repeats compound` und `harder to stagger`.** Auf jedem
   Boss identisch, ersteres ohne Datengrundlage *(QA)*. *Wenn das weg ist,
   verliert ein Spieler* die Aussage, dass Buffs sich stapeln — die gehoert
   einmal in den Tabkopf.
3. **Abschnitt `BODY PARTS`, solange `PART_NAMES` leer ist.** *Wenn das weg
   ist, verliert ein Spieler* die Information, dass ein Boss gepanzerte
   Stellen hat — die er ohne Koerperteilnamen ohnehin nicht anwenden kann.
   Der Abschnitt wird wertvoll, sobald `PART_NAMES` gefuellt ist.
4. **Nicht streichen: der `EVERDARK`-Block.** Die Behauptung „identisch" ist
   geprueft und wahr fuer 8 von 8 *(QA)*.

**Deep of Night**

1. **Die Zeile `Win` mit fuenf identischen `+200`.** *Wenn das weg ist,
   verliert ein Spieler* nichts — ein Satz sagt dasselbe und sagt
   zusaetzlich, dass es nicht von der Tiefe abhaengt.
2. **`Cursed relic — Uncommon` / `— Rare` aus der Tiefentabelle.** *Wenn das
   weg ist, verliert ein Spieler* zwei echte Zahlen — also **verschieben**,
   nicht loeschen.
3. **`Map concealed` und `Nightlord obscured` als zwei Zeilen.** *Wenn das
   weg ist, verliert ein Spieler* die Unterscheidung, welches von beidem
   passiert — die ist relevant. Eine Zeile plus die vorhandene Note sagt mehr
   auf weniger Platz.

**Red variants**

1. **Spalte `For example` in ihrer heutigen Form** (AK-99). *Wenn das weg
   ist, verliert ein Spieler* nichts Korrektes — sie ist fuer die groesste
   Zeile leer und fuer die uebrigen kartenblind.
2. **Zwei der fuenf Tiefenspalten** (AK-100). *Wenn das weg ist, verliert ein
   Spieler* die Moeglichkeit, „Depth 3" direkt nachzuschlagen — deshalb
   **zusammenfassen statt streichen**.
3. **Nicht streichen: `Night bosses (unconfirmed)`.** Zahlen fuer etwas, das
   nie gesichtet wurde, mit genau diesem Wort im Titel — das ist A7, wie es
   aussehen soll.

**World Events**

1. **`Can fire on Day 1 or Day 2.` in seiner heutigen Form** (AK-101). *Wenn
   das weg ist, verliert ein Spieler* nichts — er verliert erst dann etwas,
   wenn auch die Tagesverteilung wegbleibt, die heute schon verworfen wird.
2. **Die Quellennamen in den `Sources disagree`-Bloecken** (AK-104). *Wenn
   das weg ist, verliert ein Spieler* nichts, was er benutzen kann; „hier
   widersprechen sich die Quellen" bleibt.
3. **Nicht streichen: `Every other Nightlord: never.`** *Wenn das weg ist,
   verliert ein Spieler* die Zusicherung, dass die Liste vollstaendig ist —
   die ist wertvoll, aber nur mit ihrem Geltungsbereich (AK-102).
4. **Nicht streichen: `WHAT THE DEMON CAN DO`.** Der einzige Ort im Programm,
   an dem eine Spielentscheidung mit sieben Ausgaengen vollstaendig
   aufgelistet ist.

---

### 9. Ausdruecklich nicht Teil dieser Vorgabe

- **Die Rechnungen selbst.** Ob `ladder.down` gezeigt wird, ob
  `DEBUFF_ON_BREAK` und `ladder.down` derselbe Mechanismus sind (QA-129), ob
  die Kartenbindung der Roster ueberhaupt herstellbar ist (QA-132) — das sind
  Daten- und Rechenfragen des `developer` bzw. des `director`. Diese Vorgabe
  regelt, **was der Bildschirm ueber die Herkunft einer Zahl sagt**, nicht,
  welche Zahl richtig ist.
- **QA-137** (Testabdeckung der fuenf Tabs). Testschuld ohne Designanteil,
  laut T-056 direkt an den `developer`.
- **Neue Inhalte.** Jede Zeile oben ist entweder eine Umbenennung, eine
  Umstellung, eine Streichung oder ein bereits geladenes, heute
  weggeworfenes Feld (`sigil_info`, `rune_scaling`, Tagesverteilung). Kein
  Punkt verlangt eine neue Extraktion.
- **`Build planner`** und der Berater (S7 bis S11).
- **Die Fensterbreite unter 1250 physischen px.** Dort wird die Tab-Leiste
  selbst scrollbar *(visuell,* `…/tab2-weapons-narrow1250.png`*)*. Das ist
  ein Befund des ganzen Fensters, nicht der sechs Tabs, und gehoert in einen
  eigenen Auftrag.

---

### 10. Offene Fragen an den App Designer

1. **`Avg chance`: eine Zahl oder eine Spanne?** Nach AK-79 und AK-80 ist die
   Rechnung ehrlich; offen bleibt die Darstellung. *(a)* Zwei Spalten wie
   heute — gewichteter Mittelwert und bester Fall. *(b)* Eine Spalte mit der
   Spanne (`0.5 – 100 %`), weil die Streuung real ist (Faktor bis 22 im
   gemessenen Einzelfall) und ein einzelner Mittelwert wieder eine Zahl
   waere, die man ueberliest. Ich empfehle **(b)**: eine Spalte weniger auf
   einer Tabelle, die heute ihren Effektnamen auf 22 px zusammendrueckt. Die
   Wahl ist Tabellendichte gegen Genauigkeit und deshalb seine.
2. **`Pools`: streichen oder umbenennen?** AK-78 legt beide Ausgaenge
   verbindlich fest; welcher gilt, ist eine Streichung und damit seine
   Entscheidung. Ich empfehle die Streichung (Ausgang A).
3. **Die uebrigen Streichvorschlaege in §8** — dreizehn Vorschlaege, jeder
   mit dem Satz, was verloren geht.
4. **Zaehlt ein roter Haendler als „red variant"?** Die Intro definiert rote
   Varianten als *„individual empowered enemies"*; die Zeile `Merchants`
   (4 bis 6 je Karte) geht in `Total red variants on the map` ein. Der
   `qa-engineer` hat die Frage in T-055 an den `director` gestellt und
   ausdruecklich nicht als Befund gemeldet; sie ist eine Inhaltsentscheidung
   und wird hier weitergereicht, nicht beantwortet.
5. **Will er die Quellenangaben ueberhaupt sehen?** AK-104 haelt die Regel
   des Moduls aufrecht und verbannt die Wiki-Namen aus dem Fliesstext. Ob sie
   als eigenes, ruhiges Element (`sources`) darunter erscheinen sollen oder
   gar nicht, ist Geschmack — beides ist mit AK-104 vertraeglich.


---

## Nachtrag des Directors zu AK-81, AK-82 und AK-88 — 2026-09-05

Drei Stellen, an denen die Vorgabe im Kontakt mit dem Code nicht aufgeht. Der
`developer` hat sie in T-057 gemeldet statt sie stillschweigend auszulegen.
Ich entscheide sie hier, damit der naechste Lauf sie nicht erneut erbt.

**AK-81 — die Beispielzahlen sind die falschen.** AK-81 verbietet, gefilterte
Werte als Beispiel zu nennen, und nennt dann selbst `1 of 2` / `2 of 2` —
genau die **gefilterten**. Ungefiltert lauten sie **`1 of 3` / `3 of 3`**.
Verbindlich sind die ungefilterten. Der Rest von AK-81 bleibt unveraendert.

**AK-82 gegen AK-68 — AK-68 gewinnt.** AK-82s Fragesatz sagt "set above",
waehrend AK-68 die beiden Eroeffnungszeilen **ueber** die Bedienelemente
stellt. Beides woertlich ist nicht gleichzeitig erfuellbar. **AK-68 ist die
Ordnung**, AK-82s Wortlaut zieht nach. Grund: AK-68 gilt fuer alle sechs
Tabs, AK-82 fuer einen — die allgemeinere Regel bricht die speziellere nur
dann, wenn die speziellere ohne eigenen Grund abweicht, und den nennt AK-82
nicht.

**AK-88 — gilt fuer angezeigten Text, nicht fuer den Baum.** Woertlich
genommen truege AK-88 eine Umbenennung an 31 Stellen in Kommentaren und
Feldprosa quer durch Extraktor und Fassade, **ohne dass ein Nutzer etwas
davon saehe**. Der Geltungsbereich ist ab jetzt: **jede Zeichenkette, die auf
dem Bildschirm erscheint** — Beschriftungen, Tooltips, Kopfzeilen,
Aufklapp-Texte. Kommentare und interne Feldnamen sind ausdruecklich nicht
gemeint.

Davon **nicht** gedeckt und weiterhin offen: `nrplanner/advisor/goals.py:108`
zeigt `spell scaling` in einem `Goal.scope`-Satz — das **ist** angezeigter
Text und faellt damit unter AK-88. Geht in den naechsten Auftrag.


---

## Nachtrag des Directors zu AK-75, AK-77 und AK-97 — 2026-09-05 (nach T-058)

Der `developer` hat drei Vorgaben gemeldet, die im Kontakt mit dem Code nicht
aufgehen, und jeweils eine Lesart gewaehlt statt sie stillschweigend zu
beugen. Ich bestaetige alle drei.

**AK-77 gilt nicht unterhalb von rund 1100 logischen px.** Dort gibt der
Code die beiden Untergrenzen auf, statt eine Spalte hinter den rechten Rand
zu schieben. Grund, und er ist zwingend: die Bildlaufleiste, die eine
abgeschobene Spalte wieder erreichbar machen wuerde, ist **genau die, die
hinter der Taskleiste liegt** (DR-015). Eine erzwungene Untergrenze braeuchte
bei 833 px eine 883 px breite Tabelle in einem 780-px-Sichtbereich — die
Vorgabe waere formal erfuellt und der Inhalt unerreichbar. **Bedingung:**
jede gekuerzte Zelle traegt ihren vollen Text als Tooltip. Diese Zusicherung
traegt den Kompromiss; ohne sie faellt er.

**AK-97, erster Halbsatz: die vier Tabellen behalten ihre feste Hoehe.** Ohne
sie bekaeme jede eine eigene Bildlaufleiste — vier Leisten auf einem Tab sind
schlechter als eine.

**AK-75 gilt nur fuer die sechs Inhalts-Tabs.** Vier angezeigte Literale mit
` -- ` bleiben ausserhalb (`datasource.py:173`, `model.py:889`,
`model.py:1058`, `weapons.py:221`). Sie liegen im `Build planner`, den der
Nutzer ausdruecklich ausgenommen hat ("der erste passt"). Als Schuld
vermerkt, nicht als Befund.

**Ausserhalb der Spec, hier festgehalten, weil es sonst verlorengeht:**
vier fest verdrahtete Spaltenzahlen stehen weiterhin im `Build planner` und
im Relikt-Picker (`relicpicker.py:16` und `:31`, `weaponslots.py:59`,
`app.py:1416`). Der Picker ist groessenveraenderlich — wer ihn schmaler
zieht, bekommt DR-016a erneut. `CardGrid` liegt fertig vor. **Der Befund ist
nicht geschlossen** und wird mit S10 gezogen, weil der Picker dort ohnehin
umgebaut wird.


---

## Nachtrag des Directors zu AK-82 — 2026-09-06 (nach T-068)

**Der Fragesatz des Waffen-Tabs ist geaendert, und das ist beabsichtigt.**

AK-82 hat den alten Wortlaut woertlich gebunden. Der `developer` hat ihn in
T-068 dennoch ersetzt und die Abweichung gemeldet statt sie zu verschweigen —
richtig so, denn **der alte Satz war an genau der Stelle falsch, um die es
geht**: er sagte, der Nightfarer werde "above" eingestellt, waehrend dort nur
das Upgrade eingestellt wird. Ein `power-user` ist dieser Angabe gefolgt, hat
den Charakterwaehler nicht gefunden und ihn erst durch Durchklicken aller
Reiter im `Build planner` entdeckt (QA-155).

**Verbindlich ab jetzt:**

1. Der Satz nennt **beide** Orte getrennt: wo das Upgrade eingestellt wird
   (hier) und wo Nightfarer und Level eingestellt werden (`Build planner`).
   Gebauter Wortlaut: `…rated at the upgrade you set here, for the Nightfarer
   and level you set on the Build planner tab.`
2. Der zweite Satz (Zauber) bleibt **unveraendert**.
3. **Es kommt kein zweiter Charakterwaehler in den Waffen-Tab.** Das waere
   eine neue Funktion und ein zweiter Ort fuer denselben Zustand — die Klasse,
   die dieser Audit gerade beseitigt hat. Ob dort spaeter einer hingehoert,
   ist eine Produktfrage und liegt beim App Designer.

**Betroffen:** AK-82 (Wortlaut ersetzt), §3.1. AK-68 und die uebrigen
Kriterien des Waffen-Tabs sind unberuehrt.

**Offen und ausdruecklich nicht hier entschieden:** der Farbwert der neuen
Zeigermarke. Gebaut ist `#33343c` (WCAG 1,331 gegen eine unmarkierte Karte;
die Auswahlmarke erreicht 1,440). Gemessene Alternativen liegen im
T-068-Bericht — zwei davon reichen weiter, bringen aber einen neuen Farbton
auf einen Tab, auf dem der Kartenrand schon etwas bedeutet. **Das ist eine
Entscheidung des `ui-ux-designer`**, die Zahlen liegen bei.


---

## Nachtrag des Directors zu AK-05 — 2026-09-06 (nach T-071)

**Die Startbreite ist keine feste Zahl mehr.** AK-05 nannte **1320 px**; das
war der Wert, bei dem der Spaltenkopf `Comes with curse` beim **ersten Blick**
gekuerzt war — in drei von vier `power-user`-Laeufen ein Aergernis, und
niemand hatte je entschieden, dass 1320 richtig ist.

**Verbindlich ab jetzt:** die Oeffnungsbreite wird **aus den Spaltenbreiten
abgeleitet** (`EffectTable.width_for_full_headings()`), nicht gesetzt. Das
Kriterium ist nicht eine Pixelzahl, sondern die Aussage: **beim Startmass ist
keine Spaltenueberschrift gekuerzt.** Gemessen ergibt das heute 1350 x 860 auf
Windows/Fusion/150 %/Segoe UI 9 — auf einer anderen Maschine eine andere Zahl,
und das ist der Sinn der Ableitung (L-001, L-009).

Zwei Schranken, in dieser Reihenfolge: **der verfuegbare Schirm** geht vor dem
Wunsch, danach das Layout-Minimum von **760 px**.

**Offen und ausdruecklich nicht hier entschieden:** die Fokusmarke der
Tastaturbedienung liegt im selben warmen Farbkanal wie die Auswahlmarke. Ein
Bild liegt im T-071-Bericht bei. **Das ist eine Entscheidung des
`ui-ux-designer`.**

---

## Der Erststart mit Ordnerauswahl (ui-ux-designer, T-074) — 2026-09-06

### 0. Grundlage, Methode, und was davon **nicht** gesehen ist

**Modus:** Spec. Diese Vorgabe beschreibt einen Ablauf, den es heute **nicht
gibt**, und gegen den spaeter geprueft wird.

**Methode:** ausschliesslich Codelesung. Der Auftrag T-074 untersagt das
Starten des Fensters (parallel laufendes T-073, Einzelkopie-Sperre aus T-071).
**Kein Bildnachweis, keine Messung** aus diesem Lauf. Jede Pixelangabe unten
ist ein **Sollwert**, keine Messung, und traegt ihre Umgebung (L-009).

**Belegte Ausgangslage** (gelesen, nicht behauptet):

- `nrdata/gamefiles.py:48 find_game_dir()` sucht ueber die Steam-Registry, die
  Bibliothekliste `libraryfolders.vdf` und die Laufwerke C bis H nach
  `.../ELDEN RING NIGHTREIGN/Game/regulation.bin`. Ergebnis ist der Ordner,
  der `regulation.bin` **direkt** enthaelt, also `...\Game`.
- `nrdata/savefile.py:391 save_roots()` sucht nur unter `%APPDATA%\Nightreign`
  und `~/AppData/Roaming/Nightreign`; `find_saves()` (Zeile 415) sammelt daraus
  `*.sl2`.
- `nrplanner/app.py:3873` ruft `firstrun.ensure_data(find_game_dir())`. Ist der
  Rueckgabewert `None`, baut `firstrun.what_is_needed(None)` nichts, und
  `load_data()` faellt in `datasource.py:152` auf `raise FileNotFoundError(
  _no_data_message())`. Das landet in `app.py:3883` als `QMessageBox.critical`
  — **die heutige Sackgasse**.
- **Es gibt im gesamten Anwendungscode keinen Datei- oder Ordnerdialog.**
  Geprueft mit zwei unabhaengigen Begriffen ueber das ganze Repo:
  `QFileDialog` und `getExistingDirectory|getOpenFileName` finden Treffer
  ausschliesslich unter `.venv/` (Bibliothekscode), keinen einzigen in
  `nrplanner/`, `nrdata/` oder `scripts/`.
- Ein fehlender **Spielstand** ist heute keine Sackgasse, sondern eine stille
  Minderung: `app.py:3217` schreibt `"No save file found. Relic slots stay
  empty; ..."` in `owned_label` und geht weiter. Es gibt keinen Weg, eine Datei
  anzugeben.
- Der Ablauf, in den das hier gehoert, ist `nrplanner/firstrun.py:152
  _Window` — ein `Qt.WindowType.SplashScreen`, feste Groesse `460 x 190`
  (Erststart) bzw. `460 x 150`, Titel, Erklaerzeile, unbestimmter
  Fortschrittsbalken, Statuszeile, und auf dem Erststart das Angebot
  `"Add to my Start Menu"`.

**Messumgebung fuer alle Zahlen dieser Vorgabe (L-009):** Windows 10,
Qt-Stil `Fusion` mit der dunklen Palette aus `app.apply_appearance`,
`QT_SCALE_FACTOR` nicht gesetzt (Einstellung `Automatic`), Windows-Anzeige
100 %, **logische** Pixel. Bei 125 % und 150 % gelten dieselben logischen
Werte; geprueft wird dort nicht die Zahl, sondern dass nichts abgeschnitten
ist (AK-129).

### 1. Zweck & Nutzerziel

Ein Spieler, dessen Spiel oder Spielstand an einem Ort liegt, den die
Automatik nicht kennt, kommt **ohne fremde Hilfe** bis zu angezeigten Zahlen
(GOAL A15). Er muss dafuer keinen Dateinamen, keinen Ordnernamen und keine
Konto-Kennung kennen — nur den Weg, den er in Steam ohnehin schon kennt.

**Nicht-Ziel:** eine Einstellungsseite fuer Pfade. Der Ablauf ist eine
Reparatur, kein Konfigurationsbereich.

### 2. Wann das Panel kommt — die Aufloesungskette

Beides, Spielordner und Spielstand, folgt derselben Kette. **Der Dialog ist
das letzte Glied, nie das erste.**

**Spielordner**, in dieser Reihenfolge, beim Start vor allem anderen:

1. **Gemerkter Pfad.** Liegt einer vor und enthaelt er `regulation.bin`, wird
   er genommen. Kein Fenster, kein Klick.
2. **Automatik.** `find_game_dir()` wie heute. Findet sie etwas, wird es
   genommen und **als gemerkter Pfad hinterlegt**. Kein Fenster, kein Klick.
3. **Panel.** Erst wenn 1 und 2 leer ausgehen.

Die Reihenfolge 1 vor 2 ist bewusst: die Angabe des Nutzers schlaegt die
Vermutung des Programms. Die Reihenfolge 2 nach einem **ungueltig gewordenen**
1 ist ebenso bewusst: wer sein Spiel neu an den Standardort installiert, soll
kein Fenster sehen, obwohl sein alter gemerkter Pfad tot ist.

**Spielstand**, beim Aufbau des Build planner:

1. Gemerkte Datei, wenn sie existiert und lesbar ist.
2. `find_saves()` wie heute (mehrere Funde: der relikreichste gewinnt,
   `inventory.py:179-201` — unveraendert).
3. **Kein Panel, kein Modal.** Stattdessen wird die Zeile, die den Fehlschlag
   heute schon meldet, handlungsfaehig (Abschnitt 5).

### 3. Aufbau: ein Fenster, zwei Zustaende

Das Panel ist **kein zweites Fenster neben** `firstrun._Window`, sondern
dessen erster Zustand. Reihenfolge im Erststart: *fragen* → *bestaetigen* →
*bauen* → *fertig*. Der `"Add to my Start Menu"`-Haken bleibt unveraendert im
Bau-Zustand, wo er heute steht.

**Aenderung an der Fensterart, mit Begruendung.** Der heutige
`SplashScreen`-Typ ist fuer den Bau-Zustand richtig und fuer den Frage-Zustand
falsch: er hat keine Titelleiste, keinen Eintrag in der Taskleiste, ist nicht
verschiebbar und nimmt keine Escape-Taste. Sobald aus dem Panel heraus ein
**Ordnerdialog des Betriebssystems** geoeffnet wird, ist das ein Fehler mit
Folgen: der Systemdialog kann hinter dem Panel liegen, und ein Nutzer, der das
Programm dann in der Taskleiste sucht, findet es nicht. Deshalb:

- **Frage-Zustand:** normales Fenster mit Titelleiste (`Nightreign Helper`),
  Taskleisteneintrag, verschiebbar, Escape belegt (AK-109/AK-116).
- **Bau-Zustand:** wie heute.

**Masse (Sollwerte, Umgebung siehe 0):** Breite `460` logische px wie heute,
damit Frage und Fortschritt gleich breit sind und das Fenster beim Uebergang
nicht springt. Hoehe **inhaltsabhaengig**, Mindesthoehe `230`; Pfadzeilen
umbrechen, statt die Breite zu sprengen. Raender wie heute `28/24/28/24`,
Abstand `10`.

**Reihenfolge von oben nach unten**, in allen Frage-Faellen gleich:

1. Ueberschrift (fett, `+3` Punkt gegenueber der Grundschrift — das Muster aus
   `firstrun._Window`).
2. Erklaerung, ein bis zwei Saetze.
3. **Der Weg**, den der Nutzer gehen soll — der Steam-Satz.
4. Der zuletzt versuchte Pfad, wenn es einen gibt (eigene Zeile, umbruchfaehig).
5. Beruhigung: dass nichts angefasst wird (`MUTED`).
6. Knopfzeile, rechtsbuendig, Standardknopf rechts aussen.
7. Fusszeile (`MUTED`, klein): was das Schliessen bedeutet.

### 4. Der Spielordner

#### 4.1 Ordner, nicht Datei

Gewaehlt wird ein **Ordner**. Grund: der Name `regulation.bin` ist dem Spieler
unbekannt, der Ordner dagegen ist genau das, was Steam ihm oeffnet, wenn er
*Manage → Browse local files* waehlt. Eine Dateiauswahl wuerde ihn zwingen,
eine Datei zu erkennen, die er nie gesehen hat.

**Startort des Systemdialogs:** der erste existierende aus dieser Liste —
gemerkter Pfad, dessen Elternordner, Steams `common`-Ordner aus der
Bibliothekliste, `C:\Program Files (x86)\Steam\steamapps\common`, sonst
"Dieser PC". Der Nutzer soll moeglichst nah an seinem Ziel aufwachen.

#### 4.2 Der falsche Ordner — gesucht wird nach unten und nach oben

Der Nutzer waehlt fast sicher `...\ELDEN RING NIGHTREIGN`, nicht
`...\ELDEN RING NIGHTREIGN\Game`. Eine Ablehnung waere hier reine Schikane:
das Programm steht einen Ordner neben dem Ziel.

**Regel:** aus dem gewaehlten Ordner wird gesucht

- **nach unten** bis **Tiefe 3** (der gewaehlte Ordner ist Tiefe 0). Damit
  traegt `...\ELDEN RING NIGHTREIGN` (1), der `common`-Ordner (2) und
  `steamapps` (3) noch;
- **nach oben** bis **2 Elternebenen**, falls jemand in einem Unterordner des
  Spiels gelandet ist;
- **begrenzt**: hoechstens **400 besuchte Verzeichnisse** und hoechstens
  **2 Sekunden**. Wird die Grenze erreicht, gilt der Ordner als nicht erkannt.
  Ein Laufwerksstamm darf **nicht** zu einer Volltextsuche ueber die Platte
  fuehren; der Nutzer wartet sonst minutenlang auf ein Nein.

**Ergebnis** ist immer der Ordner, der `regulation.bin` direkt enthaelt — also
dieselbe Form, die `find_game_dir()` liefert. Mehrere Treffer: der
**flachste** gewinnt, bei Gleichstand der zuletzt geaenderte. Weicht das
Ergebnis vom gewaehlten Ordner ab, sagt die Bestaetigung das (Abschnitt 7).

#### 4.3 Woran erkannt wird, dass es das Richtige ist

**Zwei Stufen, weil `regulation.bin` allein nicht reicht.** ELDEN RING hat
ebenfalls eine `regulation.bin`, ebenfalls `data*.bhd`-Archive und ebenfalls
eine Oodle-DLL — die Struktur unterscheidet die beiden Spiele nicht.

- **Stufe 1, Annahmebedingung (hart):** `regulation.bin` vorhanden, lesbar und
  nicht leer; mindestens eine Datei `data*.bhd` aus `bhd5.ARCHIVE_KEYS`
  vorhanden; eine der DLLs aus `oodle._DLL_NAMES` vorhanden. Faellt eine davon
  aus, wird abgelehnt (Abschnitt 7, Text E1).
- **Stufe 2, Identitaet (weich):** enthaelt weder der Fundordner noch eine
  seiner drei Elternebenen `NIGHTREIGN` im Namen (Gross-/Kleinschreibung egal,
  Konstante `gamefiles.INSTALL_DIR`), wird **nicht abgelehnt**, sondern
  rueckgefragt (Text W1). Grund: eine Umbenennung ist erlaubt und kommt vor;
  eine Minute Arbeit an ELDEN RING mit anschliessend falschen Zahlen ist der
  teurere Fehler.

*Nicht geprueft in diesem Lauf:* ob es eine `nightreign.exe` o. ae. gibt, an
der die Identitaet **hart** haengen koennte. Der Code kennt keinen solchen
Namen. Verifiziert jemand ihn an einer echten Installation, ist er die
bessere Stufe 2, und Text W1 entfaellt.

#### 4.4 Was gespeichert wird

Der bestaetigte Ordner wird **sofort** gespeichert, vor dem Bau — sonst
kostet ein Absturz waehrend der Minute die Angabe. Ablage im vorhandenen
`QSettings`-Speicher (`favourites.ORG` / `favourites.APP`), Schluessel
`paths/game`, passend zu `ui/scale` und `ui/panes`. **Keine neue Datei, kein
neues Format.**

Aus dem Spielordner wird nichts verschoben, kopiert oder geloescht. Der
Datenabzug entsteht wie heute unter `paths.cache_dir()`, und dieser Ort ist
**nicht** waehlbar.

### 5. Der Spielstand

**Entscheidung: kein Modal.** Der Spielstand ist laut README ausdruecklich
optional ("Without one the relic slots stay empty and every other tab works in
full"). Ein Spieler, der das Spiel auf diesem PC noch nie gestartet hat, hat
keinen — ihm beim Erststart ein Auswahlfenster vorzusetzen, das er nur
wegklicken kann, waere genau die Reibung, die A15 beseitigen soll.

**Stattdessen wird der Ort handlungsfaehig, an dem der Fehlschlag heute schon
gemeldet wird.** `owned_label` in `app.py:3217` sagt bereits "No save file
found"; daneben stehen bereits die Knoepfe `Rescan save` und `Load equipped`
(`app.py:1534-1537`). Genau dort kommt ein dritter Knopf `Find my save…` hinzu.

- Sichtbar **nur**, wenn kein Spielstand geladen ist — im geglueckten Fall
  aendert sich an dieser Zeile nichts (AK-106).
- Der Knopf ist ein echter `QPushButton` in der Knopfzeile, **nicht** ein Link
  in der 10-px-`MUTED`-Zeile. Ein Angebot, das der Nutzer uebersieht, loest
  A15 nicht.

**Auswahl: Datei, nicht Ordner.** Umgekehrt zum Spielordner, und aus
demselben Grund: hier ist die Datei das, was der Nutzer sieht und meint, und
bei **mehreren Steam-Konten** ist die Dateiauswahl die einzige Form, in der er
sagen kann, *welches* Konto er will. Der Automatik-Weg (relikreichster
Spielstand gewinnt) bleibt unveraendert und wird durch die Wahl nur
ueberstimmt.

- Filter: `Nightreign save (NR*.sl2)`, dann `Save file (*.sl2)`, dann
  `All files (*)`. Der dritte Eintrag ist noetig, weil `find_saves()`
  ausdruecklich auch umbenannte Sicherungen zulaesst.
- **Startort:** der **aufgeloeste** Pfad des Ordners `Nightreign` im
  Roaming-Profil, wenn es ihn gibt, sonst das aufgeloeste Roaming-Profil
  selbst. Dieser Startort ist die eigentliche Hilfe — der Nutzer kann die
  Umgebungsvariable nicht tippen und soll es auch nicht muessen.
- Die Variablenschreibweise erscheint **nirgends** in einem Text fuer den
  Nutzer (AK-127); nur der aufgeloeste Pfad.

**Drei Ausgaenge nach der Wahl:**

1. Lesbar, mit Relikten → die vorhandene Zeile `"{n} relics in {source}"` wie
   heute, voller Pfad wie heute nur im Tooltip.
2. Lesbar, ohne Relikte → Text S3. Kein Fehler; der Nutzer sieht, dass er
   das falsche Konto erwischt haben koennte, und kann erneut waehlen.
3. Unlesbar → Text S4: ein Satz in Spielersprache **vor** dem technischen
   Grund. Das ist dieselbe Regel, die DESIGN_REVIEW DR-006 fuer den
   Erststart-Fehlerdialog fordert; sie gilt hier von Anfang an.

**Speicherung:** Schluessel `paths/save` im selben `QSettings`-Speicher.
Verschwindet die gemerkte Datei, wird **still** auf `find_saves()`
zurueckgefallen; erst wenn auch das leer ausgeht, erscheint die Zeile mit dem
Knopf wieder. Der gemerkte Pfad wird dabei nicht geloescht (AK-121).

**Vertraulichkeit.** Der Spielstandordner ist nach der Steam-Konto-Kennung
benannt; `app.py:3236-3242` haelt sie deshalb bewusst aus jedem sichtbaren
Text heraus und zeigt sie nur im Tooltip. Diese Entscheidung gilt hier
unveraendert weiter: **keine Bestaetigungszeile dieses Ablaufs druckt den
vollen Spielstandpfad**, nur den Dateinamen (AK-126).

### 6. Beim naechsten Start

**Gemerkter Spielordner gueltig** → nichts passiert, kein Fenster.

**Gemerkter Spielordner ungueltig** (Spiel deinstalliert, verschoben,
externes Laufwerk nicht angesteckt) → erst die Automatik (Abschnitt 2). Erst
wenn auch die leer ausgeht, entscheidet der Datenbestand:

- **Ein brauchbarer Datenabzug liegt vor** (`datasource.bundled_path()`
  existiert): **nicht blockieren.** Das Programm kann arbeiten; ein
  abgezogenes USB-Laufwerk darf keinen Totalausfall bedeuten. Panel-Text A3
  mit zwei Knoepfen: `Choose folder…` und `Continue with the data from
  {Datum}`. Das Datum stammt aus der Aenderungszeit des Abzugs und ist die
  einzige ehrliche Angabe darueber, wie alt die Zahlen sind.
- **Kein Abzug** → blockieren, Panel-Text A2.

**Der gemerkte Pfad wird bei einem Fehlschlag nicht geloescht.** Er wird nur
ersetzt, wenn ein neuer Ordner bestaetigt wurde. Ein Laufwerk kommt wieder.

**Ein heute stiller Fall, der hierher gehoert und den ich melde statt ihn zu
loesen:** faellt der Spielordner weg, waehrend der Abzug von einer **aelteren**
Programmfassung stammt, liefert `datasource._load_data` den veralteten Abzug
kommentarlos zurueck (`datasource.py:129-153`: `_regulation_matches` ist
`False`, die Live-Extraktion scheitert an `game is None`, und der Abzug wird
trotzdem gereicht). Der Nutzer sieht dann alte Zahlen ohne jeden Hinweis. Das
ist kein Teil dieser Vorgabe, aber Text A3 nennt aus genau diesem Grund ein
Datum.

### 7. Wortlaut — alle Texte, Englisch (A8)

Fenstertitel im Frage-Zustand: `Nightreign Helper`

**A1 — Erststart, nichts gefunden**

```
Where is ELDEN RING NIGHTREIGN installed?

Nightreign Helper reads every number it shows out of your own copy of the
game, and it could not find one on this PC.

In Steam, right-click ELDEN RING NIGHTREIGN in your library and choose
Manage, then Browse local files. Pick the folder that opens.

Nothing in that folder is changed, moved or deleted. It is only read.

[ Quit ]  [ Choose folder... ]

You can close this and come back later. It will ask again.
```

**A2 — spaeterer Start, gemerkter Ordner weg, keine Daten da**

```
Your game is not where it was last time.

Nightreign Helper last read it from:
{Pfad}

That folder is not there now. If the game was moved or reinstalled, or if it
sits on a drive that is not plugged in right now, point this at the new place.

[ Quit ]  [ Choose folder... ]

You can close this and come back later. It will ask again.
```

**A3 — spaeterer Start, gemerkter Ordner weg, Daten von frueher da**

```
Your game is not where it was last time.

Nightreign Helper last read it from:
{Pfad}

You can carry on with what was read on {Datum}. Those numbers stay right
until the game is updated.

[ Continue with the data from {Datum} ]  [ Choose folder... ]
```

**E1 — gewaehlter Ordner nicht erkannt**

```
That folder does not hold a copy of the game.

You picked:
{Pfad}

Nothing inside it looked like an installed game. Pick the folder the game
itself is in: in Steam that is Manage, then Browse local files.

[ Quit ]  [ Choose a different folder... ]
```

**W1 — Struktur passt, Name passt nicht**

```
This does not look like ELDEN RING NIGHTREIGN.

There is an installed FromSoftware game here:
{Pfad}

Its folder is not named after ELDEN RING NIGHTREIGN, so this may be a
different game. Reading it takes about a minute, and every number would be
wrong.

[ Use this folder anyway ]  [ Choose a different folder... ]
```

**C1 — bestaetigt, gleicher Ordner** (`GOOD`, dann sofort der Bau-Zustand)

```
Found your game in {Pfad}
```

**C2 — bestaetigt, tiefer gefunden als gewaehlt**

```
Found your game in {Pfad}, inside the folder you picked.
```

**S1 — Erklaerung am Spielstand-Knopf** (Tooltip von `Find my save…`)

```
Your save is a file called NR0000.sl2, in a folder named Nightreign under
your Windows user profile. This opens there.
```

**S2 — Titel des Datei-Dialogs**

```
Choose your Nightreign save file
```

**S3 — gewaehlter Spielstand lesbar, aber leer**

```
That save has no relics in it yet. If you play on more than one Steam
account, this may be the wrong one.
```

**S4 — gewaehlter Spielstand unlesbar**

```
That file is not a Nightreign save this can read.
{technischer Grund}
```

**S5 — Ersatz fuer die heutige Zeile `app.py:3217`**

```
No save file found. Relic slots stay empty; the Effects and Weapons tabs
still work in full. If your save is somewhere else, use Find my save.
```

**Verbotene Woerter in allen Texten dieses Ablaufs** (AK-127):
`regulation.bin`, `steamapps`, `libraryfolders.vdf`, die Dateiendung `.sl2`
ausserhalb von S1 und dem Dateifilter, jede Umgebungsvariable in
Prozentschreibweise, `AppData`, `Steam ID`, `account id`, `snapshot`, `cache`,
`param`, `extract`.

### 8. Token

Keine neuen. Verwendet werden ausschliesslich die vorhandenen aus
`nrplanner/app.py:108-113`:

| Rolle | Token | Wo |
|---|---|---|
| Bestaetigung | `GOOD` `#6fbf73` | C1, C2 |
| Ablehnung, Warnung | `BAD` `#d1655f` | Kopfzeile von E1 und W1 |
| Nebentext, Fusszeile | `MUTED` `#8a8a8a` | Beruhigungs- und Fusszeile |
| Grundschrift, Ueberschrift `+3` fett | wie `firstrun._Window` | Ueberschrift |

`MUTED` `#8a8a8a` wird fuer die **Fusszeile** und Nebensaetze benutzt, wie im
ganzen Programm. Fuer die **Pfadzeile** gilt das nicht: sie ist das, was der
Nutzer pruefen soll, und steht in der normalen Textfarbe (AK-129).

### 9. Plattform, Tastatur, Skalierung

- **Fluent/WinUI-Konvention:** der bestaetigende Knopf steht rechts, der
  abbrechende links davon; der Standardknopf ist der bestaetigende. Auslassung
  in den drei Punkten (`Choose folder...`), weil ein weiterer Dialog folgt.
- **Der Ordnerdialog ist der Systemdialog** (Qt-Standard, nicht
  `DontUseNativeDialog`). Er kommt in der hellen Windows-Gestaltung, waehrend
  das Programm dunkel ist. Das ist **kein Befund**: der Systemdialog ist das,
  was der Nutzer aus jedem anderen Programm kennt, und ein nachgebauter
  dunkler Dialog verliert Schnellzugriffe, Netzlaufwerke und OneDrive.
- **Tastatur:** der ganze Ablauf ohne Maus. Tab erreicht jeden Knopf, der
  Fokus ist sichtbar, Enter loest den Standardknopf aus.
- **Escape** bedeutet "aus dieser Frage heraus, mit dem geringsten Verlust":
  in A1/A2/E1/W1 ist das `Quit`, in A3 `Continue with the data from {Datum}`.
  Dasselbe gilt fuer das Schliessen ueber das Fensterkreuz. Die Fusszeile sagt
  in A1/A2, was das Schliessen bedeutet.
- **Skalierung:** 100 %, 125 % und 150 % (Windows-Anzeige) und zusaetzlich die
  programmeigenen Faktoren aus `uiscale.CHOICES` bis `200%` — nichts
  abgeschnitten, keine waagerechte Bildlaufleiste, kein Knopf ausserhalb des
  Fensters.

### 10. Akzeptanzkriterien

**AK-106** *(A15, Vorgabe "der geglueckte Fall aendert sich nicht")* Findet
Schritt 1 oder 2 der Kette aus Abschnitt 2 den Spielordner, erscheint **kein**
zusaetzliches Fenster und **kein** zusaetzlicher Klick gegenueber heute.
Pruefung: ein Lauf auf einer Maschine mit Standardinstallation zeigt genau die
Fensterfolge, die er heute zeigt.

**AK-107** Die Aufloesung des Spielordners laeuft in der Reihenfolge
gemerkter Pfad → `find_game_dir()` → Panel. Pruefung: bei ungueltigem
gemerktem Pfad und gleichzeitig auffindbarer Standardinstallation erscheint
**kein** Panel.

**AK-108** Auf einer Maschine ohne auffindbares Spiel und ohne gemerkten Pfad
erscheint das Panel aus Abschnitt 3 **statt** der heutigen
`QMessageBox.critical` aus `app.py:3883`. Pruefung: die Zeichenkette
"No ELDEN RING NIGHTREIGN installation was found." aus
`datasource._no_data_message` erreicht in diesem Fall keinen Bildschirm mehr.

**AK-109** Das Fenster im Frage-Zustand hat Titelleiste, Taskleisteneintrag
und ist verschiebbar; der Bau-Zustand bleibt wie heute. Pruefung: sichtbar am
laufenden Fenster, plus die Fensterflagge im Code.

**AK-110** Der Knopf `Choose folder...` oeffnet eine **Ordner**auswahl, keine
Dateiauswahl, und startet in dem ersten existierenden Ort aus der Liste in
4.1.

**AK-111** Waehlt der Nutzer `...\ELDEN RING NIGHTREIGN` statt
`...\ELDEN RING NIGHTREIGN\Game`, wird das Spiel gefunden und angenommen.
Dasselbe fuer den `common`- und den `steamapps`-Ordner. Die Suche besucht
hoechstens 400 Verzeichnisse und dauert hoechstens 2 Sekunden; ein
Laufwerksstamm fuehrt innerhalb dieser Grenze zu einer Ablehnung, nicht zu
einer Plattensuche.

**AK-112** Angenommen wird ein Ordner nur, wenn `regulation.bin` lesbar und
nicht leer ist, mindestens eine `data*.bhd` aus `bhd5.ARCHIVE_KEYS` vorliegt
und eine DLL aus `oodle._DLL_NAMES` vorliegt. Faellt eine der drei aus,
erscheint Text E1.

**AK-113** Traegt weder der Fundordner noch eine seiner drei Elternebenen
`NIGHTREIGN` im Namen, erscheint Text W1 mit den zwei Knoepfen, und der
Standardknopf ist `Choose a different folder...` — nicht das Weitermachen.
Der Ordner wird **nicht** abgelehnt.

**AK-114** Nach einer Ablehnung bleibt das Fenster offen, nennt den versuchten
Pfad, und der Knopf heisst `Choose a different folder...`. Das Programm endet
an dieser Stelle **nie** von selbst.

**AK-115** Bricht der Nutzer die Systemauswahl ab, kehrt er in das Panel
zurueck, in genau den Zustand, in dem er es verlassen hat. Nichts wird
gespeichert, nichts wird gemeldet.

**AK-116** `Quit`, Escape und das Fensterkreuz beenden das Programm ohne
Fehlerdialog und ohne gespeicherte Angabe. Ausnahme A3: dort fuehren Escape
und Fensterkreuz zu `Continue with the data from {Datum}`.

**AK-117** Ein bestaetigter Ordner steht **vor** dem Beginn des Baus in
`QSettings` unter `paths/game` (Speicher `favourites.ORG`/`favourites.APP`).
Pruefung: Programm nach der Bestaetigung waehrend des Baus hart beenden, neu
starten — es fragt nicht erneut.

**AK-118** Zwischen der Bestaetigung (C1/C2) und dem Beginn des Baus liegt
**kein** weiterer Klick. Das Fenster wechselt in den Fortschrittszustand,
ohne die Breite zu aendern.

**AK-119** Gemerkter Pfad ungueltig, Automatik leer, aber
`datasource.bundled_path()` existiert: Text A3 erscheint mit dem Datum des
Abzugs, und `Continue with the data from {Datum}` fuehrt in ein voll
bedienbares Fenster mit angezeigten Zahlen.

**AK-120** Gemerkter Pfad ungueltig, Automatik leer, kein Abzug: Text A2,
zwei Knoepfe, kein dritter Weg.

**AK-121** Ein einzelner Fehlschlag loescht weder `paths/game` noch
`paths/save`. Pruefung: Laufwerk trennen, starten, `Quit`, Laufwerk wieder
anstecken, starten — es wird nicht erneut gefragt.

**AK-122** Fuer den Spielstand erscheint zu **keinem** Zeitpunkt ein Modal,
das der Nutzer wegklicken muss. Pruefung: ein Erststart auf einer Maschine
ohne jeden Spielstand erreicht den Build planner ohne einen einzigen Klick
mehr als heute.

**AK-123** Ist kein Spielstand geladen, steht in der Knopfzeile neben
`Rescan save` ein sichtbarer Knopf `Find my save...`. Er oeffnet eine
**Datei**auswahl mit dem Filter aus Abschnitt 5 und startet im aufgeloesten
`Nightreign`-Ordner des Roaming-Profils, falls vorhanden. Ist ein Spielstand
geladen, ist der Knopf nicht da.

**AK-124** Die drei Ausgaenge einer Spielstandwahl sind unterscheidbar und
tragen die Texte aus Abschnitt 7: Relikte gefunden → die heutige Zeile;
lesbar ohne Relikte → S3; unlesbar → S4 mit dem Spielersatz **vor** dem
technischen Grund.

**AK-125** Eine gewaehlte Spielstanddatei wird unter `paths/save` gemerkt und
beim naechsten Start bevorzugt. Existiert sie nicht mehr, faellt das Programm
**still** auf `find_saves()` zurueck; erst wenn auch das leer ist, erscheint
S5 mit dem Knopf.

**AK-126** Kein Text dieses Ablaufs zeigt den vollen Spielstandpfad. Der
Dateiname ist erlaubt, der Ordner mit der Konto-Kennung nicht; der volle Pfad
bleibt im Tooltip, wie heute in `app.py:3242`.

**AK-127** Keiner der Texte aus Abschnitt 7 enthaelt eines der dort
aufgelisteten verbotenen Woerter. Pfade erscheinen ausschliesslich
**aufgeloest**, nie als Variablenname.

**AK-128** *(A8)* Alle Texte dieses Ablaufs sind Englisch, auch die
Knopfbeschriftungen, der Fenstertitel und der Titel des Dateidialogs.

**AK-129** Bei Windows-Anzeige 100 %, 125 % und 150 % sowie bei den
Programmfaktoren bis `200%` ist in allen Zustaenden kein Text abgeschnitten,
kein Knopf ausserhalb des Fensters, und es gibt keine waagerechte
Bildlaufleiste. Pfadzeilen umbrechen. **Nachweis am laufenden Fenster mit
Bildnachweis, nicht am Code** (A13-Muster).

**AK-130** Der gesamte Ablauf ist ohne Maus bedienbar: Tab erreicht jeden
Knopf, der Fokus ist sichtbar, Enter loest den Standardknopf aus.

**AK-131** Das Panel erscheint **nur** fuer den Fall "kein Spielordner".
Fehlen die Param-Definitionen (`datasource.defs_dir()` ist `None`) oder
scheitert das Lesen einer gefundenen Installation, bleiben die heutigen
Meldungen stehen — ein Ordnerdialog waere dort die falsche Antwort.

**AK-132** *(NH-002, oeffentliches Repo)* Jeder Bildnachweis dieses Panels
wird aus dem **Fenster** gezogen und zeigt einen Pfad ohne echten
Windows-Benutzernamen und ohne Steam-Konto-Kennung. Wo das nicht geht, wird
der Nachweis vorher unkenntlich gemacht.

### 11. Ausdruecklich nicht Teil dieser Vorgabe

- Der Zielort des Datenabzugs. Er bleibt `paths.cache_dir()` und wird nicht
  waehlbar (Festlegung des Directors).
- Eine Einstellungsseite, auf der die beiden Pfade nachtraeglich geaendert
  werden koennen, **ohne** dass etwas fehlschlaegt. Der Spielordner ist
  danach nur ueber den Fehlerfall erreichbar; ob das reicht, ist offene
  Frage 1.
- Die Auswahl **zwischen mehreren gefundenen** Spielstaenden im geglueckten
  Fall. `inventory.load` entscheidet wie heute nach Relikanzahl.
- Der stille veraltete Datenabzug aus Abschnitt 6 (gemeldet, nicht geloest).
- DR-006 (Spielersprache vor technischen Fehlern im Bau-Fehlerdialog). Fuer
  die **neuen** Texte gilt die Regel hier bereits (S4).
- Die Deinstallation, QA-158/159/160/162 und die Fokusmarke aus T-071.

### 12. Offene Fragen an den App Designer

1. **Soll der Spielordner auch dann aenderbar sein, wenn nichts kaputt ist?**
   Diese Vorgabe zeigt das Panel nur im Fehlerfall — so hat der Nutzer es
   entschieden. Wer zwei Installationen hat (etwa eine zweite Kopie zum
   Testen), kann dann nicht umschalten. Eine Zeile mit Knopf im Hauptfenster
   waere die kleine Loesung; sie kostet einen sichtbaren Bedienknopf mehr.
2. **Soll der Spielstand beim Erststart aktiv angeboten werden?** Ich habe
   mich dagegen entschieden (Abschnitt 5): kein Modal, dafuer ein Knopf an der
   Stelle, an der die Frage entsteht. Die Gegenposition ist vertretbar — eine
   Karte am Ende des Erststarts mit `Find my save...` und
   `Skip, I do not have one` wuerde das Angebot garantiert sichtbar machen,
   kostet aber jeden Spieler ohne Spielstand einen Klick.
3. **Ist `Continue with the data from {Datum}` (A3) der richtige Ausweg,
   oder soll ein fehlender Spielordner immer blockieren?** Weiterarbeiten mit
   alten Zahlen ist bequem und ehrlich beschriftet; blockieren ist strenger
   und verhindert, dass jemand monatelang veraltete Werte liest, ohne es zu
   merken.
4. **Der Wortlaut "Manage, then Browse local files".** Er nennt die englischen
   Steam-Menuepunkte. Bei einem Spieler mit deutschem Steam heissen sie
   anders. Die Alternative ist eine allgemeinere Formulierung ohne Menuenamen,
   die dafuer weniger fuehrt.

---

## Die Sprache des Beraters: eine Zeile je Zahl, und die Fluche, auf die
## keine Zahl passt (ui-ux-designer, T-078) — 2026-09-06

**Grundlage:** `docs/tasks/T-078.md` · `docs/berichte/T-067-developer.md`
(Abschnitt 2 mit der Beispielzeile, Abschnitt 5 Punkt 3 mit der Messung ueber
240 Vorschlaege, Abschnitt 7 D-2, Abschnitt 6 D-3, Abschnitt 9 mit den vier
Wortlauten) · `nrplanner/advisor/explain.py` (alle sechs Funktionen und
`_line`, `_named`, `_amount`, `_is_a_cost`) · `nrplanner/advisor/types.py`
(`Candidate`, `Suggestion`, `AdvisorResult`) · `nrplanner/advisor/goals.py`
(`_ATTACK_RATING_SCOPE`, `_DAMAGE_TAKEN_SCOPE`) · `nrplanner/model.py`
(`Build.sources`, `Build.qualitative`, `Build.situational`, `label_for`,
`is_better_lower`, `collapse_by_label`, `compute_qualitative`) ·
`nrplanner/app.py` (`_show_breakdown`, `_sync_mode`, Zeilen 664-742: `•`,
`✦`, `⚠`, `CURSE`) · `ARCHITECTURE.md` AD-010, AD-015, AD-025 (Nachtrag VI,
insbesondere 25.5 und 25.6) · `UI_SPEC.md` §3.2, §3.4, 4.9, AK-18 bis AK-22,
AK-29/AK-30, T-024 §3.3, §3.6, §4.1, §5.1, den Nachtrag zu OF-20/QA-108/
QA-113, §1.2 bis §1.5 des T-056-Abschnitts · `GOAL.md` A5, A7, A8, A11, A12,
A13, F3, OF-13.

**Methode und was davon nicht gesehen ist.** Der Berater hat noch keine
Oberflaeche (S10 fehlt), das Fenster wurde auf Weisung des Auftrags **nicht**
gestartet, und im selben Arbeitsbaum arbeitet der `qa-engineer`. Diese Vorgabe
ist deshalb **vollstaendig aus Bericht, Spec und Quelltext** gearbeitet; keine
Zeile davon ist am laufenden Programm gesehen. Alle Zahlen ueber die heutige
Ausgabe (10 bis 43 Zeilen je Vorschlag, Median 21, bis zu sieben Zeilen je
Slot, laengste Zeile 142 Zeichen, 36 von 309 Relikten mit stummem Fluch)
stammen aus der Messung des `developer` in T-067 und sind hier **nicht
nachgemessen**. Wo unten eine Hoehe oder eine Breite zugesichert wird, steht
sie als **Pruefauftrag mit Messumgebung** (L-009), nicht als Befund.

---

### 1. Die Formfrage: §3.2 gegen §3.4 — entschieden zugunsten der Zeilen

**Der Konflikt.** §3.2 verlangt fuer den Vorschlagsblock **einen** Satz je
Slot, hoechstens 160 Zeichen (`Chosen for +15.0% Skill Attack Power and +6.0%
all damage — the largest gain of any Blue relic you own.`). §3.4 Punkt 2
verlangt im `Why`-Dialog je Slot den Reliktnamen und **darunter die Effekte
mit ihrem Beitrag**. Gebaut ist die zweite Form.

**Entscheidung: die zweite Form gilt, an beiden Orten. §3.2s Einzelsatz wird
aufgehoben — ersatzlos, nicht gekuerzt.** Drei Gruende, der erste ist der
zwingende:

1. **Der Einzelsatz ist nicht ehrlich schreibbar.** Er behauptet in jeder
   denkbaren Fassung eine Rangfolge unter den Beitraegen ("chosen **for** X",
   "the largest gain"). Eine solche Rangfolge gibt es nicht: ein Prozentsatz
   und ein flacher Bonus lassen sich ohne einen Umrechnungskurs nicht
   vergleichen, den die Spieldateien nicht hergeben — dieselbe Grenze, die
   AD-023 und OF-13 schon fuer den Fluch gezogen haben und die `explain.py`
   in seinem Docstring ausdruecklich benennt. Der Satz aus §3.2 ist damit ein
   **A7-Verstoss meiner eigenen Vorgabe**. Er faellt.
2. **Ein Auszug braeuchte einen Nenner, und der Nenner kostet mehr als die
   Zeilen.** Jede Kuerzung ("and 3 more") muesste nach A7/L-013 sagen, wovon
   sie ein Teil ist, und der Spieler muesste danach doch den `Why`-Dialog
   oeffnen. Zwei Formen derselben Aussage an zwei Orten ist genau die
   Fehlerklasse, die dieses Projekt zweimal getroffen hat (QA-082, QA-087)
   und gegen die AD-024 entschieden hat.
3. **Der Platz gibt es her.** §3.2 zeigt heute schon **eine
   Aufzaehlungszeile je Effekt** (`• Improved Melee Attack Power`, aus
   `_sync_mode`). Die neue Form **ersetzt** diese Zeilen, sie kommt nicht zu
   ihnen dazu: aus `• <Effektname>` wird `• <Effektname>: <Groesse> <Zahl>`.
   Der gemessene Median ist 21 Zeilen auf sechs Slots, also **rund 3,5 Zeilen
   je Slot** — ungefaehr die Zahl der Aufzaehlungszeichen, die dort ohnehin
   stehen. Teurer wird nur der schlechteste Slot (sieben statt drei Zeilen),
   und die Slots scrollen (§3.1: die Leiste steht ausserhalb der
   `QScrollArea`, die Karten stehen darin).

**Was dadurch entfaellt:** der Begruendungssatz aus §3.2 und mit ihm die
160-Zeichen-Grenze; AK-18 in seiner heutigen Fassung. **Was bleibt:** A5 und
F3 unveraendert — sie werden von den Zeilen erfuellt, jede nennt einen Effekt
beim Namen mit dem, was er bewegt hat, und die Negativa sind darunter
ausgewiesen.

---

### 2. Die Zeilengrammatik (verbindlich, Englisch, A8)

**Eine Zeile ist ein Effekt und eine Groesse, die er bewegt hat.** Bewegt ein
Effekt zwei Groessen, die `model.collapse_by_label` nicht zusammenfasst, sind
das zwei Zeilen — das ist die heutige, gebaute Form und sie bleibt.

```
{effect name}: {figure label} {amount}
{effect name}: {figure label} {amount}, counted against it
{effect name}: {amount}
```

- **`{effect name}`** ist der Name aus dem Datensatz, wie ihn `Build.sources`
  fuehrt.
- **`{figure label}`** ist `model.label_for`, bei einem auf eine Waffenklasse
  beschraenkten Buff mit dem Zusatz `, {class} armaments only` — beides
  Bestand aus `explain.py::_field_label` und unveraendert.
- **`{amount}`** ist das Format des Statblatts: `+15.0%` fuer einen
  Multiplikator, `+1` fuer alles, was addiert (`explain.py::_amount`,
  identisch mit `app.py::_show_breakdown`). **Keine typografischen
  Minuszeichen** — das Statblatt schreibt ASCII, und eine zweite Schreibweise
  waere eine zweite Regel.
- **Die dritte Fassung ohne `{figure label}`** gilt genau dort, wo die
  Beschriftung der Groesse dem Effektnamen gleicht — ein Buff, den das Spiel
  auf eine Bewegung beschraenkt, traegt seinen eigenen Namen als
  Feldbezeichnung. `Improved Skill Attack Power: Improved Skill Attack Power
  +15.0%` waere die laengere Art, nichts zu sagen. **Uebernommen wie gebaut**
  (`explain.py::_named`).
- **`, counted against it`** steht genau dann, wenn der Beitrag seine Groesse
  **schlechter** macht, entschieden ueber `model.is_better_lower` und nie
  ueber das Vorzeichen. **Uebernommen wie gebaut**, Wortlaut bestaetigt: er
  sagt, dass gegengerechnet wurde, ohne zu behaupten, wie viel es gekostet
  hat — genau die Auskunft, die F3 verlangt.

**Was aus der Zeile verschwindet: `Slot 4, ` und der Reliktname.** Beide
stehen im Kopf der Gruppe, unter der die Zeile haengt (§6). Die heutige Zeile

```
Slot 4, Deep Grand Burning Scene — Physical Attack Up +4: Physical Attack +12.0%
```

wiederholt auf bis zu sieben aufeinanderfolgenden Zeilen dieselben rund 35
Zeichen. Das ist die Antwort auf die vierte Frage des Auftrags: **die
Slotnummer ist doppelt und faellt aus der Zeile**, nicht aus dem Kopf. Der
Reliktname faellt aus demselben Grund mit. Ergebnis: die laengste Zeile sinkt
von gemessenen 142 auf rund 105 Zeichen.

**Satzzeichen.** Eine Zeile, die auf einer Zahl oder auf `counted against it`
endet, traegt **keinen** Punkt — sie ist ein Wert, kein Satz, und das
Statblatt setzt dort auch keinen. Eine Zeile, die auf einem vollstaendigen
Satz endet (§3, Fuellung ii und iii), traegt einen.

**Reihenfolge innerhalb einer Slotgruppe:** erst die Effekte in der Ordnung,
in der sie auf dem Relikt stehen (die Ordnung, die auch der Picker zeigt),
danach die Fluche. So ist es gebaut, und es ist die richtige Reihenfolge: der
Preis steht am Ende, nicht dazwischen.

---

### 3. Die Fluchzeilen — drei Fuellungen, eine Familie

Heute zerfaellt ein Fluch auf bis zu drei Orte: eine Zeile in `reasons`, eine
inhaltsgleiche in `curses`, und im Fall von AD-015 zusaetzlich ein eigener
Satz in `unknowns`. Ein Spieler soll einen Fluch **einmal** lesen, an der
Stelle, an der das Relikt steht. Deshalb: **eine Zeile je Fluch und Groesse,
mit `✦` und in `CURSE`, in der Gruppe ihres Slots**, in einer von drei
Fuellungen.

**(i) Der Fluch bewegt eine Zahl, die diese Zielrichtung zaehlt.**

> `✦ {curse name}: {figure label} {amount}, counted against it`

(ohne den Zusatz, wenn er die Groesse ausnahmsweise besser macht). Kein Satz
sagt, das Relikt sei **wegen** des Fluchs schlechter platziert — der Preis
steht in seiner eigenen Einheit, das Verrechnen bleibt dem Spieler (OF-13,
AD-023).

**(ii) Der Fluch bewegt eine Zahl, die diese Zielrichtung nicht zaehlt.**

> `✦ {curse name}: {figure label} {amount} — this figure does not count it.`

Das ist die AD-015-Pflichtzeile, **umgebaut von zwei Zeilen auf eine**. Heute
steht dieselbe Sache zweimal da: die Zahl in `reasons`/`curses` und daneben
`A curse on <relic> changes <field>, which this goal does not rank.` in
`unknowns`. Beide Haelften gehoeren in einen Satz, und der Reliktname darin
ist ueberfluessig, weil die Gruppe ihn traegt. Der Wortlaut folgt der
Familie, die im Picker schon steht (T-024 §3.6: `Its curse changes <field>,
which neither figure counts.`) und der QA-113-Zeile (`This figure does not
count that change.`) — "figure" ist in diesem Programm das Wort fuer die
Rankingzahl, und der Spieler liest es dort schon.

*Geltungsbereich, unveraendert aus `explain.py`:* die Frage wird **je Fluch**
gestellt und **an der Rankingzahl** beantwortet (dieselbe Belegung ohne
diesen einen Fluch noch einmal bewertet). Ein Fluch, der zwei Groessen bewegt
und davon eine gezaehlte, bewegt die Zahl und bekommt Fuellung (i) — er ist
im Ranking sichtbar, und genau dafuer gibt es (ii) nicht.

**(iii) Der Fluch bewegt hier gar keine Zahl** (D-2, Abschnitt 4).

> `✦ {curse name}: no number here shows what this costs.`

**Kein Wort ueber die Spieldateien.** Der Satz sagt, was wahr ist — in diesem
Block steht keine Zahl dazu —, und behauptet **nicht**, dass es keine gaebe.
Bei drei der betroffenen Relikte gibt es sie (`All Resistances Down` senkt
sieben Widerstandswerte um je 80); nur die Rechnung des Beraters fuehrt sie
nirgends. Ein Satz wie "the game files carry no numbers for these" waere dort
schlicht falsch — er steht heute in 4.9 und wird in Abschnitt 5 entfernt.

**Der Schlusssatz, genau einmal je `Why`-Dialog**, unter allen Slotgruppen,
`MUTED`, 11 px:

> `✦ marks a curse. A cost with no number beside it is still a cost — weigh it before you apply.`

Er ist zugleich die Legende fuer `✦` (§1.4 des T-056-Abschnitts: eine
Farbrolle braucht eine Legende) und die einzige Stelle, an der die
Aufforderung steht. **Nicht je Zeile und nicht je Slot** — sechs Slots
wuerden ihn sechsmal tragen, und das ist das Rauschen, gegen das AK-50
geschrieben ist.

---

### 4. Das neue Feld: Fluche ohne Zahl (D-2, Director-Entscheidung)

**Der Befund** (Messung des `developer`, T-067 Abschnitt 7, hier nicht
nachgemessen): **36 von 309** besessenen Relikten tragen einen Fluch, den das
Ergebnis in **keinem** Feld nennt — 33 mit reinen Engine-Feldern
(`Taking Damage Causes Madness Buildup` und Verwandte, sie landen in
`Build.qualitative`, das kein Feld von `AdvisorResult` fuehrt) und 3 mit
`All Resistances Down`, das echte Zahlen bewegt, aber weder in `sources` noch
in `qualitative` steht. §3.2 sagt dazu: *"Ein Vorschlag, dessen Preis erst
nach dem Anwenden sichtbar wird, ist eine Falle."*

**Vorgabe:** `AdvisorResult` bekommt ein **eigenes Feld** —
`curses_without_a_figure` — und **nicht** eine Verbreiterung von
`not_counted` (D-3, Abschnitt 5). Der Name sagt das Kriterium: Fluche der
**vorgeschlagenen** Kopien, zu denen die Rechnung keine Zahl gefuehrt hat.

**Kriterium, in einem Satz:** ein Fluch einer vorgeschlagenen Kopie, der
keine Zeile nach §2 erzeugt hat. Nicht "ohne Zahlen in den Spieldateien",
nicht "konditional" — schlicht: die Rechnung hat nichts zu ihm
aufgeschrieben.

**Warum das Kriterium so und nicht enger:** es ist **vorwaertskompatibel**.
Schreibt `model.compute_resistances` eines Tages nach `sources` (Empfehlung
an den `director`, Abschnitt 11), wandern die drei
`All Resistances Down`-Relikte von selbst aus Fuellung (iii) in Fuellung (i)
oder (ii) — ohne dass hier ein Satz oder eine Zahl nachgezogen wird. Eine
Vorgabe, die "die 36" festschreibt, waere am naechsten Datensatz falsch.

**Was das Feld traegt:** je Fluch **einen** Eintrag, in derselben Zuordnung
zu einem Slot wie die uebrigen Zeilen (§6). Der gezeigte Text ist Fuellung
(iii). **Kein Zaehlfeld daneben** — die Anzahl ist die Laenge, wie bei
`not_counted` (`types.py` sagt das dort schon).

**Die Statuszeile nennt es** (§5): `· {n} curses carry no number.`

---

### 5. Korrektur an 4.9 (D-3, Director-Entscheidung)

**4.9 vermischt heute zwei Mengen.** Der Zustand heisst "Teilweise stumm" und
sagt `· some effects carry no numbers.`, der `Why`-Dialog dazu `The game
files carry no numbers for these, so they counted for nothing:`. Gemeint war
einmal "Effekte ohne Zahlen"; `not_counted` traegt nach AD-010 aber
**konditionale** Effekte, und das sind zwei verschiedene Dinge: ein
konditionaler Effekt traegt Zahlen, ein Fluch ohne Zahlen ist nicht
konditional. **`not_counted` behaelt die Bedeutung aus AD-010.** 4.9 wird
geteilt.

**4.9 neu — zwei Klauseln, die unabhaengig voneinander auftreten koennen.**
Sie haengen mit `  ·  ` an den Ergebnissatz aus 4.6 an, in dieser Reihenfolge
(erst der Preis, dann das Weggelassene), und der ungekuerzte Text steht wie
jeder Statuszeilentext im Tooltip (§3.1):

| Fall | Klausel (woertlich) |
|---|---|
| 4.9a — Fluche ohne Zahl (das neue Feld) | Einzahl `1 curse carries no number.` · Mehrzahl `{n} curses carry no number.` |
| 4.9b — konditionale Effekte (`not_counted`) | Einzahl `1 effect was left out: it only applies under a condition.` · Mehrzahl `{n} effects were left out: they only apply under a condition.` |

Beispiel mit beidem:
`Maximise damage — 6 of 6 slots filled  ·  2 curses carry no number.  ·  3 effects were left out: they only apply under a condition.`

**Im `Why`-Dialog** erscheinen die beiden Mengen an **verschiedenen** Orten,
weil es zwei verschiedene Fragen sind:

- **4.9a steht bei seinem Relikt**, als Fuellung (iii) in der Slotgruppe. Ein
  Preis gehoert an das Ding, das ihn kostet; eine Sammelliste am Ende des
  Dialogs verlangt vom Spieler, den Namen zurueckzusuchen.
- **4.9b steht als eigener Abschnitt** unter den Slotgruppen, mit dieser
  Ueberschrift, danach die Namen aus `not_counted`, einer je Zeile:

  > `These effects only apply under a condition, so this ranking did not count them:`

  Der alte Satz `The game files carry no numbers for these, so they counted
  for nothing:` **entfaellt ersatzlos** — er beschreibt keine der beiden
  Mengen richtig.

**Duplikate bleiben stehen** (zwei Relikte mit derselben ungezaehlten
Bedingung sind zwei ungezaehlte Effekte; `types.py` begruendet das dort
bereits). 4.9 und 4.10 bleiben getrennt wie bisher.

---

### 6. Der Kopf einer Slotgruppe, und was die Anzeige nicht selbst herausfinden darf

**Der Kopf.** Jede Slotgruppe traegt zwei Zeilen, danach die Zeilen aus §2
und §3:

```
Slot 4 — Deep Grand Burning Scene        (nur im Why-Dialog; im Block steht
                                          nur der Reliktname)
3 of its 5 effects moved a number in this build.
```

Die zweite Zeile ist `MUTED`, 11 px, und sie ist **kein Schmuck**: ohne sie
verschwindet ein Effekt, der nichts bewegt hat, spurlos, und der Spieler
sucht ihn. Mit ihr traegt der Auszug seinen Nenner (L-013). Fuellungen,
woertlich:

| Fall | Wortlaut |
|---|---|
| keiner von mehreren | `None of its {total} effects moved a number in this build.` |
| einige von mehreren | `{n} of its {total} effects moved a number in this build.` |
| alle von mehreren | `All {total} of its effects moved a number in this build.` |
| genau ein Effekt, er bewegte nichts | `Its one effect moved no number in this build.` |
| genau ein Effekt, er bewegte etwas | `Its one effect moved a number in this build.` |

`{total}` sind die Effekte der **Kopie** ohne ihre Fluche
(`Candidate.effect_ids`); `{n}` sind die davon, die mindestens eine Zeile
nach §2 erzeugt haben — **Effekte gezaehlt, nicht Zeilen**: ein Effekt, der
zwei Groessen bewegt, ist einer.

**Strukturelle Auflage — die Anzeige liest keinen Satz.** Alle Zeilen kommen
heute als flache `tuple[str, ...]` und tragen ihren Slot **im Text**. Sobald
die Zeilen je Slot gruppiert gezeichnet werden — und §3.2 verlangt genau das,
denn der Block sitzt in der Slotkarte —, muesste das Fenster den Satz
zerlegen, um zu wissen, wohin er gehoert. **Das ist verboten.** Ein
Anzeigecode, der eine Zeichenkette aus `explain.py` nach `Slot `, `—` oder
`: ` durchsucht, ist genau die Kopplung, an der dieses Projekt schon einmal
haengengeblieben ist (QA-107), und sie bricht am ersten Reliktnamen, der
einen Gedankenstrich enthaelt.

Verbindlich ist deshalb die **Eigenschaft**, nicht ihre Bauart — die
Datenform entscheiden `architect` und `developer`:

1. Jede Zeile erreicht die Anzeige **mit ihrer Slotnummer** (nullbasiert im
   Datenweg, weil sie einen Slot adressiert; einsbasiert erst im gezeichneten
   Kopf, wie das Fenster zaehlt).
2. Jede Zeile erreicht die Anzeige **mit der Auskunft, ob sie ein Fluch ist**.
   Ohne sie kann das Fenster `✦` und `CURSE` nicht setzen, ohne den Text zu
   durchsuchen.
3. Je Slot erreichen die Anzeige die **beiden Zaehlungen** `{n}` und
   `{total}` aus dem Kopf. Beide entstehen in `explain.py` beilaeufig; im
   Fenster waeren sie nur durch Zerlegen zu bekommen.
4. **`reasons` und `curses` werden nie beide gezeichnet.** `curses` ist heute
   die fluchtragende **Teilmenge** von `reasons` (beide entstehen aus
   `_attributed`); wer beide Listen zeichnet, zeigt jeden Fluch zweimal. Das
   Feld bleibt, weil AD-010 es verlangt — gezeichnet wird `reasons`, und die
   Fluchzeilen darin sind markiert.

---

### 7. Der Vorschlagsblock (§3.2 neu) und der `Why`-Dialog (§3.4 neu)

**§3.2 neu — Vorschlagsblock in der Slotkarte.** Rahmen, Radius, Farbe,
Innenabstand, Kopfzeile, `Use`-Knopf und der Sonderfall
`Already equipped — nothing to change here.` bleiben **unveraendert**. Neu
ist der Rumpf:

```
SUGGESTED — MAXIMISE DAMAGE                                   [ Use ]
The Will of the Balancers
3 of its 5 effects moved a number in this build.
• Improved Melee Attack Power: Physical Attack +12.0%
• Improved Skill Attack Power: +15.0%
• Continuous FP Recovery: FP restored per second +1
✦ Ultimate Art Charging Impaired: Ultimate Art auto-charge speed -15.0%, counted against it
✦ Taking Damage Causes Madness Buildup: no number here shows what this costs.
```

- Aufzaehlungszeichen `•` fuer Effekte, `✦` fuer Fluche, `CURSE` fuer die
  Fluchzeilen, `⚠` fuer nicht stapelnde Effekte — alles Bestand aus
  `_sync_mode`, unveraendert.
- **Keine Slotnummer** (die Karte **ist** der Slot) und **kein**
  Begruendungssatz mehr.
- Jede Zeile `setWordWrap(True)`, nichts wird elidiert (4.14 gilt fort).

**§3.4 neu — `Why`-Dialog.** Titel, Groesse, `Close`-Knopf und das Verbot
eines `Apply` bleiben unveraendert. Inhalt in dieser Reihenfolge:

1. **Kopf:** Ziel, Nightfarer, Vessel, Deep of Night an/aus, wie viele
   Relikte betrachtet wurden (unveraendert).
2. **Die Halte-Zeile**, wenn es eine gibt (§8) — sie erklaert, warum
   moeglicherweise nicht sechs Gruppen folgen, und gehoert deshalb **vor**
   sie.
3. **Je Slot eine Gruppe:** Kopf `Slot {n} — {Reliktname}`, Zaehlzeile,
   Effektzeilen, Fluchzeilen. Slots in ihrer eigenen Ordnung, nicht nach
   Beitrag sortiert.
4. **`These effects only apply under a condition, so this ranking did not
   count them:`** mit den Namen aus `not_counted`, wenn es welche gibt
   (4.9b).
5. **Der Schlusssatz mit der `✦`-Legende** (§3), wenn mindestens eine
   Fluchzeile der Fuellung (ii) oder (iii) im Dialog steht.
6. **Fusszeile, `MUTED`:** die Verfahrenssaetze der gewaehlten Zielrichtung
   (`Goal.scope`, einmal je Bildschirm nach AD-025 und AK-50) und darunter die
   `data_note` (§8). Der Vorbehalt zum Angriffswert steckt seit T-046 in
   `_ATTACK_RATING_SCOPE` und wird damit von AK-22 ("genau einmal, nicht je
   Zeile") weiterhin erfuellt — er wird hier nicht ein zweites Mal
   hingeschrieben.

---

### 8. Die Halte-Zeile und die `data_note`

**Halte-Zeile — uebernommen, mit einer Korrektur am dritten Fall.** Der
`developer` hat sie richtig gebaut: sie traegt ihren Nenner, sie benutzt
`held`, also genau das Wort, das der Knopf in der Slotkopfzeile traegt
(T-024 §4.1: `Hold` / `Held`), und sie erklaert die Folge statt nur den
Zustand.

> Einzahl: `1 of {slots} slots is held, so only the other {rest} were filled.`
> Mehrzahl: `{held} of {slots} slots are held, so only the other {rest} were filled.`
> Alle: `All {slots} slots are held, so there was nothing to search — this is your build as it stands, with its figure.`

Geaendert ist allein der letzte Fall. Gebaut ist heute `…, so nothing was
searched: this is the build as it stands, scored.` — "scored" steht dort als
alleinstehendes Partizip am Satzende und ist die Sorte Verkuerzung, bei der
ein nicht-technischer Spieler raten muss (A11). "with its figure" nennt
stattdessen das, was er auf dem Schirm sieht, in dem Wort, das der Rest des
Beraters dafuer benutzt. `the build` → `your build`, weil es seiner ist.

**`data_note` — uebernommen, mit einer Korrektur am Wort `snapshot`.**

> Mit Version, gespeichert: `Ranked on game data version {version}, read from your game files earlier and kept since.`
> Mit Version, frisch gelesen: `Ranked on game data version {version}, read from your game files just now.`
> Ohne Version: `Ranked on game data read from your game files {earlier and kept since | just now}. It does not say which game version it is from, so these figures cannot be tied to a patch.`

**Warum `snapshot` faellt:** das Wort steht in AK-127 auf der Verbotsliste des
Erststarts — ein Spieler weiss nicht, was ein "stored snapshot" ist, und es
gibt keinen Grund, dasselbe Wort auf einem anderen Schirm doch zu benutzen.
Die Auskunft, auf die es ankommt, ist nicht der Speicherort, sondern der
**Zeitpunkt**: sind das die Zahlen meiner heutigen Installation oder aeltere?
Genau das sagen `earlier and kept since` und `just now`.

Die Versionsnummer bleibt ungeschmueckt stehen (`version 10350000`): sie ist
die Kennung des Spiels selbst, und der Satz nennt ihren Geltungsbereich
("game data version"), was A12 verlangt.

---

### 9. Akzeptanzkriterien

Fortlaufend ab **AK-133**. Pruefbar, binaer. Wo eine Pruefung das laufende
Fenster braucht, ist sie als solche benannt; alle uebrigen sind am Ergebnis
oder am Quelltext pruefbar, also auch ohne Spielinstallation.

**Form**

- **AK-133** Der Vorschlagsblock zeigt **keinen** zusammenfassenden
  Begruendungssatz. Die Zeichenkette `Chosen for` kommt im Programm nicht
  vor, und keine gezeigte Zeile endet auf eine Kuerzungsformel (`and {n}
  more`, `…` am Zeilenende ausserhalb der Statuszeile).
- **AK-134** Die Zahl der in einer Slotgruppe gezeichneten Effekt- und
  Fluchzeilen ist gleich der Zahl der Zeilen, die das Ergebnis fuer diesen
  Slot traegt. Keine wird ausgelassen, keine zusammengefasst. *Ersetzt
  AK-18*, dessen "genau ein Begruendungssatz je Slot" mit §1 aufgehoben ist;
  A5 und AK-19 gelten unveraendert weiter.
- **AK-135** Keine gezeichnete Zeile nennt die Slotnummer oder den
  Reliktnamen, die im Kopf ihrer Gruppe stehen. Die Slotnummer erscheint
  **einsbasiert** und **nur** im Kopf der Gruppe im `Why`-Dialog.
- **AK-136** Jede Zeile folgt einer der Fassungen aus §2 bzw. §3, woertlich,
  einschliesslich der Satzzeichenregel: eine Zeile, die auf einer Zahl oder
  auf `counted against it` endet, traegt keinen Punkt; eine Zeile, die auf
  einem Satz endet, traegt einen.
- **AK-137** `, counted against it` steht genau an den Zeilen, deren Beitrag
  ihre Groesse nach `model.is_better_lower` schlechter macht — nie nach dem
  Vorzeichen entschieden. Pruefweg: ein Fall mit einem Feld, das kleiner
  besser ist (FP-Kosten), und eine Senkung darin; die Zeile traegt den Zusatz
  **nicht**.

**Fluche**

- **AK-138** Fuer jede vorgeschlagene Kopie gilt: die Menge der Fluchnamen in
  ihrer Slotgruppe ist **gleich** der Menge ihrer `curse_ids`, ueber den
  Datensatz in Namen aufgeloest. Kein Fluch fehlt, keiner steht doppelt, und
  jeder steht in genau einer der drei Fuellungen aus §3. Pruefweg: die
  Aufloesung laeuft unabhaengig von `explain.py` ueber `ctx.data["effects"]`
  — derselbe Weg, den `test_the_reasons_name_only_effects_the_suggestion_brought`
  schon geht.
- **AK-139** `AdvisorResult` traegt ein Feld fuer die Fluche ohne Zahl
  (`curses_without_a_figure`), getrennt von `not_counted`. Es enthaelt genau
  die Fluche der vorgeschlagenen Kopien, zu denen keine Zeile nach §2
  entstanden ist — gepruefte Gegenrichtung: ein Fluch mit einer Zeile ist
  **nicht** darin.
- **AK-140** Kein vom Berater gezeigter Text behauptet, die Spieldateien
  traegen fuer einen Fluch keine Zahlen. Die Zeichenketten `carry no numbers`
  und `carries no numbers` kommen im Berater nicht vor. (Grund: bei
  `All Resistances Down` waere die Behauptung falsch.)
- **AK-141** Der Schlusssatz mit der `✦`-Legende steht **genau einmal** je
  `Why`-Dialog und in **keinem** Vorschlagsblock.

**4.9 und die Statuszeile**

- **AK-142** `not_counted` enthaelt ausschliesslich konditionale Effekte nach
  AD-010 (`Build.situational`, `live == False`). Der Satz `The game files
  carry no numbers for these, so they counted for nothing:` erscheint
  nirgends mehr. *Ersetzt AK-21.*
- **AK-143** Die beiden Klauseln aus 4.9a und 4.9b erscheinen woertlich wie
  in §5, in dieser Reihenfolge, jede nur wenn ihre Menge nicht leer ist, mit
  richtig gewaehltem Singular/Plural. Der ungekuerzte Statuszeilentext steht
  im Tooltip.

**Sprache (A11, A12)**

- **AK-144** Der gesamte vom Berater gezeigte Text (Block, `Why`-Dialog,
  Statuszeile, Tooltips) enthaelt keines der Woerter `field`, `pool`,
  `handle`, `beam`, `scorer`, `source`, `snapshot`, `slot_index`,
  `not_counted`, `contribution`. Pruefweg: der ausgelesene Text eines Laufs
  gegen eine Wortliste.
- **AK-145** Die Halte-Zeile und die `data_note` folgen §8 woertlich, in
  allen dort genannten Fuellungen.
- **AK-146** Die Zaehlzeile im Kopf jeder Slotgruppe folgt §6 woertlich;
  `{n}` zaehlt **Effekte**, nicht Zeilen. Pruefweg: ein Effekt, der zwei
  nicht zusammenfassbare Groessen bewegt, ergibt zwei Zeilen und erhoeht
  `{n}` um eins.

**Struktur und Sicherheit**

- **AK-147** Kein Anzeigecode zerlegt, durchsucht oder schneidet eine
  Zeichenkette, die aus `explain.py` stammt. Pruefbar per Grep ueber den
  S10-Code: auf den Ergebnisfeldern mit Zeilen (`reasons`, `curses`, das Feld
  aus AK-139, `unknowns`) kein `.split(`, `.startswith(`, `.find(`,
  `.index(`, kein `re.`, kein `in`-Test auf Teilzeichenketten. Slot,
  Fluch-Eigenschaft und die beiden Zaehlungen kommen aus der Datenform (§6).
- **AK-148** In keiner Slotgruppe erscheint ein Fluchname zweimal.
  Insbesondere zeichnet die Oberflaeche nicht `reasons` **und** `curses`.
- **AK-149** AK-29 und AK-30 gelten unveraendert fuer jede neue Zeile: jedes
  neue Textelement setzt `setTextFormat()` ausdruecklich, und ein Relikt-,
  Effekt- oder Fluchname mit `<b>x</b><img src=x>&lt;` erscheint in Block,
  Dialog, Statuszeile und Tooltip buchstabengetreu.

**Am laufenden Fenster (A13), mit Messumgebung nach L-009**

- **AK-150** Schlechtester gemessener Fall des `developer` nachgestellt —
  sechs belegte Slots, darunter einer mit **sieben** Effektzeilen und
  **zwei** Fluchzeilen, laengster Reliktname des Spielstands: in der
  mittleren Spalte des Build planner entsteht **keine waagerechte**
  Bildlaufleiste, keine Zeile ist abgeschnitten, keine bricht mitten in einem
  Begriff (AK-73), und jede ist durch senkrechtes Scrollen erreichbar. Zu
  messen bei Fensterbreite 1320 px (Startbreite) und UI scale `Automatic`
  **sowie** 150 %, auf einem 100-%-Bildschirm, unter dem Qt-Stil, mit dem das
  Programm ausgeliefert wird. **Die Messung nennt Plattform, Stil,
  Skalierung und ob die Zahlen physisch oder logisch sind** — ohne diese
  Angaben zaehlt sie nicht.

---

### 10. Ausdruecklich nicht Teil dieser Vorgabe

- **Die Oberflaeche des Beraters insgesamt (S10).** Hier steht die Sprache
  und die Form der Bloecke, nicht die Anordnung der Leiste, nicht die
  Nebenlaeufigkeit, nicht das Anwenden.
- **Die Datenform, in der die Zeilen reisen.** §6 nennt vier Eigenschaften,
  die sie haben muss. Ob das ein Tupel von Tupeln, ein zweites Feld auf
  `Suggestion` oder ein eigener Datensatz je Slot wird, entscheiden
  `architect` und `developer`.
- **Ob `model.compute_resistances` nach `sources` schreiben soll.**
  Empfehlung in Abschnitt 11, Entscheidung beim `director`; diese Vorgabe
  funktioniert in beiden Faellen.
- **Die Reihenfolge der Vorschlaege untereinander** und alles, was mehr als
  einen Vorschlag gleichzeitig zeigt.
- **Die Formatierung einer Differenz** (OF-21) — sie gehoert zum Picker,
  nicht hierher.
- **Effekte ohne Zahl, die keine Fluche sind.** Sie sind in der Zaehlzeile
  (§6) als Differenz sichtbar, bekommen aber keine eigene Zeile. Siehe
  Abschnitt 11, Frage 2.

---

### 11. Offene Fragen an den App Designer

1. **Wie viel Fluch vertraegt die Slotkarte?** Diese Vorgabe zeigt jeden
   Fluch eines vorgeschlagenen Relikts im Block, auch den, zu dem es keine
   Zahl gibt. Bei einem Relikt mit drei Fluchrollen sind das drei rote Zeilen
   in einer Karte, die sonst vier Zeilen hat. Die Gegenposition waere: im
   Block nur die Fluche mit Zahl, die stummen erst im `Why`-Dialog. Ich habe
   mich dagegen entschieden (§3.2: der Preis darf nicht erst nach dem
   Anwenden sichtbar werden), aber es ist eine Geschmacks- und
   Vertrauensfrage, keine, die die Daten beantworten.
2. **Soll ein Effekt ohne Zahl im Block genannt werden, so wie ein Fluch ohne
   Zahl?** Heute sagt die Zaehlzeile `3 of its 5 effects moved a number in
   this build.` und schweigt darueber, welche zwei nichts bewegt haben. Sie
   beim Namen zu nennen waere ehrlicher, kostet aber je Slot bis zu zwei
   weitere Zeilen fuer Information, die niemanden vor einer Falle bewahrt.
3. **`Optimize` gegen `Suggest`.** ~~Die Zustandstabelle 4.1-4.14 und mehrere
   AK sprechen noch vom Knopf `Suggest`~~; T-024 §5.1 hat ihn in `Optimize`
   umbenannt. Diese Vorgabe benutzt `Optimize`. Falls der Name doch wieder
   `Suggest` heissen soll, ist das eine Ersetzung an rund einem Dutzend
   Stellen — besser jetzt als nach S10.

   **BEANTWORTET (Director, GOAL F4; nachgezogen T-084, 07.09.2026):** der
   Knopf heisst `Optimize`, dauerhaft. Die Zustandstabelle 4.1-4.14 ist seit
   Commit `bafc3e1` durchgehend nachgezogen, die letzte Fliesstextstelle
   (§5.1, „der heutige `Suggest`-Knopf") mit diesem Nachtrag. Die Frage wird
   **nicht geloescht**, weil die Begruendung von damals — der Preis einer
   spaeteren Umbenennung — der Grund war, sie vor S10 zu stellen. AK-176.

---

## Nachtrag zu T-078: der stumme Effekt bekommt seinen Namen, und der
## schlechteste Fall einer Slotkarte ist gemessen statt geschaetzt
## (ui-ux-designer, T-080) — 2026-09-06

**Grundlage:** `docs/tasks/T-080.md` (die beiden Antworten des App Designers
und die Gegenpruefung des `director` am Datensatz) · der T-078-Abschnitt
dieser Datei, insbesondere §2 (Zeilengrammatik), §3 (die drei Fluchfuellungen),
§4 (`curses_without_a_figure`), §5 (4.9a/4.9b), §6 (Kopf der Slotgruppe und
die Strukturauflage), §7 (Block und `Why`-Dialog), §9 (AK-133 bis AK-150),
§11 (die beiden Fragen) · `nrplanner/advisor/explain.py` (`_attributed`,
`_effect_name`, `reasons`, `curses`, `not_counted`) · `nrplanner/model.py`
(`compute_qualitative` mit den `why`-Texten, `Situational`, `Build.sources`,
`Build.qualitative`, `compute_resistances`) · `nrplanner/effecttext.py`
(`name`, `owner`, `works_for`) · `GOAL.md` A5, A7, A8, A11, A12, F3 ·
`ARCHITECTURE.md` AD-010, AD-015, AD-023, AD-025.

**Was dieser Nachtrag aendert:** er ergaenzt T-078 um die stumme Effektzeile,
haelt die Entscheidung zu Frage 1 fest und **ersetzt AK-150**. Alles uebrige
aus AK-133 bis AK-149 gilt woertlich weiter.

---

### 0. Messumgebung (L-009) — diesmal ist gemessen, nicht geschaetzt

Der T-078-Abschnitt musste seine Zahlen aus dem Bericht des `developer`
uebernehmen. Fuer diesen Nachtrag ist **selbst gemessen**, headless und ohne
das Fenster zu starten. Jede Zahl unten stammt aus dieser einen Umgebung:

- **Datensatz:** `nightreign_data.json` aus dem Nutzerverzeichnis,
  `data_version` **10350000**, 849 Relikte, 2076 Effekte, 252 davon Deep.
- **Spielstand:** der eigene Spielstand des App Designers, **309 besessene
  Relikte**, gelesen ueber `nrplanner.inventory.load` — nur lesend.
- **Rechenumgebung:** Nightfarer **Wylder**, **Stufe 15**, seine
  Startwaffe als Bezugswaffe **und** als einzige gefuehrte Waffe, **keine**
  Bedingung als erfuellt erklaert, `weighting=goals.DEFAULT_WEIGHTING`.
- **Verfahren:** je besessenem Relikt **ein** `Candidate` in Slot 0 gegen
  einen Grundzustand ohne Reliktwirkung, ausgewertet mit **`explain.reasons`
  und `explain.curses` selbst** — kein Nachbau der Zeilenlogik. Windows,
  Python aus `.venv`, 06.09.2026.
- **Wiederholrezept:** `paths.snapshot_path()` laden, `model.configure`,
  `inventory.load`, je Relikt `model.compute(hero, 15, [seine Effekt- und
  Fluchrecords], curves, weapon=Startwaffe, weapons_held=[Startwaffe])`,
  daraus `explain.reasons([candidate], base, built, ctx)`. Der Aufbau steht in
  `scripts/measure_advisor_picker.py` bis auf die letzten drei Zeilen schon da.

**Grenzen dieser Messung, ausdruecklich:** sie sieht **einen** Nightfarer und
**eine** Stufe. Ein Effekt, der nur fuer Ironeye arbeitet, ist hier stumm und
waere es auf Ironeye nicht. Sie sieht **ein Relikt je Gruppe**; Effekte, die
sich ueber mehrere Slots nicht stapeln, kann sie nicht zeigen. Und sie ist
**keine Messung am Fenster**: alle Angaben sind Zeilen und Zeichen, **keine
Pixel**. Wo unten eine Karte "16 Zeilen" traegt, sind das 16 Zeilen vor dem
Umbruch — was daraus auf dem Schirm wird, ist AK-160 und noch offen.

---

### 1. Frage 1 ist entschieden und wird nicht wieder aufgemacht

**Jeder Fluch einer vorgeschlagenen Kopie steht im Vorschlagsblock, mit
Namen — auch der, zu dem es keine Zahl gibt.** Der `Why`-Dialog zeigt
dieselben Zeilen, nicht mehr und nicht weniger. Entschieden vom App Designer
am 06.09.2026; T-078 §3 und §7 bleiben damit unveraendert in Kraft.

Die Sorge um die Kartenhoehe aus T-078 §11 Frage 1 ist **entkraeftet**, und
zwar durch die Daten: ein Relikt traegt **hoechstens drei** Fluche (§2), nicht
sieben, und drei Fluchrollen gibt es nur dort, wo ohnehin drei Effektrollen
stehen. Die Zeilenzahl bleibt trotzdem der Punkt, an dem diese Vorgabe am
Fenster scheitern kann — deshalb §9 und AK-160.

---

### 2. Was auf einem Relikt ueberhaupt stehen kann (Spielwissen, belegt)

Spielwissen des App Designers, hier am Datensatz nachgezaehlt:

> Auf Relikten gibt es 1-3 positive Effekte und dann 1-3 Fluche. Fluche gibt
> es nur bei Deep-of-Night-Relikten und auch nur, wenn der Effekt gut genug
> fuer einen Fluch ist.

**Nachgezaehlt ueber alle 849 Relikte des Datensatzes:**

| Aussage | Befund |
|---|---|
| Fluche nur auf Deep-Relikten | **0 von 597** nicht-Deep-Relikten traegt einen Fluch — kein einziges |
| Fluche pro Deep-Relikt | 108 ohne, **72 mit einem, 48 mit zwei, 24 mit drei** — nie mehr |
| Effektrollen pro Relikt | 230 mit einer, 267 mit zwei, 349 mit drei, **3 mit keiner** |

**Nachgezaehlt ueber die 309 besessenen Relikte des Spielstands:**
6 Relikte mit einem Effekt, 70 mit zwei, 233 mit drei; 233 ohne Fluch, 46 mit
einem, 24 mit zwei, **6 mit drei**. Der Fall "drei plus drei" ist also nicht
theoretisch — er liegt im Inventar.

**Die drei Relikte ohne jede Effektrolle** heissen `Murk`, `Sovereign Sigil`
und `Scenic Flatstone` (alle rot, alle nicht Deep). Sie sind der Grund, warum
die Zaehlzeile aus T-078 §6 eine Fuellung fuer `{total} == 0` braucht, die
dort fehlt — nachgetragen in §5 unten.

**Zwei Beispiele in T-078 sind damit unmoeglich und werden hier berichtigt:**
`{total}` ist hoechstens **3**, nie 5. Der Beispielkopf in T-078 §6 (`3 of its
5 effects moved a number in this build.`) und der Beispielblock in T-078 §7
(`The Will of the Balancers` mit fuenf Effekten) zeigen ein Relikt, das es im
Spiel nicht gibt. Die **Wortlaute** dort gelten unveraendert; nur die Zahl im
Beispiel ist falsch. Der Ersatz steht in §3 unten und ist eine echte Kopie aus
dem Spielstand.

**Wovon diese Grenze nichts sagt: von der Zahl der Zeilen.** Ein Effekt kann
mehrere Groessen bewegen und dann mehrere Zeilen erzeugen. Gemessen ueber die
483 Effekte, die auf einem Relikt ueberhaupt rollen koennen: einer erzeugt bis
zu **fuenf** Zeilen, ein fluchfaehiger bis zu **vier**. Auf dem Spielstand
erzeugt das echte Relikte mit **neun** Effektzeilen und **vier** Fluchzeilen.
**"Drei plus drei" begrenzt die Namen, nicht die Zeilen** — wer daraus eine
Kartenhoehe ableitet, rechnet um den Faktor drei zu klein.

---

### 3. Der stumme Effekt bekommt seinen Namen (Antwort auf Frage 2)

**Entscheidung des App Designers:** ein Effekt der vorgeschlagenen Kopie, zu
dem keine Zeile nach T-078 §2 entstanden ist, wird **beim Namen genannt** —
nicht nur als Differenz in der Zaehlzeile.

**Wie oft das vorkommt** (Messumgebung §0): von 309 besessenen Relikten
tragen **272 mindestens einen** stummen Effekt — 149 einen, 92 zwei, 31 alle
drei. **49 Relikte haben ueberhaupt keinen Effekt, der eine Zahl bewegt.** Das
ist kein Randfall, das ist der Normalfall, und genau deshalb ist die
Zaehlzeile allein zu wenig gewesen: sie sagt "3 von 5" und laesst den Spieler
raten, welche zwei.

**Er ist kein Fluch und wird nicht wie einer gezeigt.** Kein `✦`, kein
`CURSE`, keine Warnfarbe, kein `⚠` (das bleibt, was es ist: die Marke fuer
Effekte, die sich nicht stapeln). Er kostet nichts, er bringt hier nur nichts.

**Form und Ort — eine Zeile in der Slotgruppe, wie die uebrigen:**

- Aufzaehlungszeichen **`•`**, dasselbe wie bei jedem anderen Effekt.
- **In der Ordnung des Relikts**, zwischen den Zeilen mit Zahl, **nicht** ans
  Ende der Effekte sortiert. Die Ordnung ist die, die auch der Picker zeigt,
  und ein Spieler soll die dritte Zeile der dritten Rolle zuordnen koennen.
  Die Fluche bleiben trotzdem zuletzt (T-078 §2, unveraendert): der Preis
  steht am Ende.
- **Farbrolle `MUTED`** (`#8a8a8a`, 4,77:1 auf `PANEL` — reicht fuer
  Fliesstext), **11 px wie jede andere Effektzeile**. Keine neue Farbe, keine
  neue Groesse.
- **Die Farbe traegt keine Information.** Was die Zeile sagt, steht in ihren
  Worten; nimmt man ihr die Farbe, bleibt die Aussage vollstaendig. `MUTED`
  ist Betonung, nicht Bedeutung (AK-156).
- **Gleiche Zeilen in Block und `Why`-Dialog.** Zwei Formen derselben Aussage
  an zwei Orten ist die Fehlerklasse aus QA-082/QA-087, gegen die T-078 §1
  schon entschieden hat.

**So sieht eine Slotkarte damit aus.** Kein erfundenes Beispiel: das ist die
Kopie von `Deep Grand Drizzly Scene` mit dem Handle `3229614356` aus dem
Spielstand des App Designers, in der Umgebung aus §0 ausgerechnet und in der
Ordnung, in der die Rollen auf ihr stehen:

```
SUGGESTED — MAXIMISE DAMAGE                                   [ Use ]
Deep Grand Drizzly Scene
2 of its 3 effects moved a number in this build.
• Partial HP Restoration upon Post-Damage Attacks +2: Regain — HP won back by attacking after a hit +35.0%
• Improved Damage Negation at Low HP: only applies under a condition, so no number here.
• Physical Attack Up +3: Physical Attack +10.5%
✦ Taking Damage Causes Poison Buildup: no number here shows what this costs.
✦ All Resistances Down: no number here shows what this costs.
```

Drei Dinge, die dieses eine echte Beispiel zeigt und ein erfundenes verdeckt
haette: die stumme Zeile steht **mitten** zwischen den Zahlzeilen, weil sie
dort auf dem Relikt steht; **beide** Fluche sind stumm (der zweite ist
`All Resistances Down` aus §8, dessen Zahlen es sehr wohl gibt); und die
erste Zeile enthaelt einen **Gedankenstrich mitten im Feldnamen** —
`model.RATE_LABELS["regainRate"]` heisst woertlich `Regain — HP won back by
attacking after a hit`. Anzeigecode, der eine Zeile an `—` zerlegt, bricht
also **heute** und nicht erst an einem hypothetischen Reliktnamen (AK-147).

---

### 4. Der Wortlaut — sechs Fuellungen, in dieser Reihenfolge geprueft

Die Grammatik ist die von T-078 §2: **Name, Doppelpunkt, was zu sagen ist.**
Ein Spieler liest in einer Slotgruppe immer dasselbe Muster.

Warum nicht **eine** Fuellung fuer alles: der Grund, warum ein Effekt stumm
ist, steht bereits berechnet in `Build.qualitative` und `Build.situational`,
und er ist fuer den Spieler **verschieden viel wert**. Gemessen ueber die 426
stummen Effekte der 309 besessenen Relikte: **150** davon arbeiten fuer einen
anderen Nightfarer und sind auf dieser Figur **totes Gewicht**, waehrend
**170** nur auf eine Bedingung warten und jederzeit zaehlen koennen. Diese
beiden in einen Satz zu werfen waere die bequeme Ungenauigkeit, die A11
verbietet.

**Genau eine Fuellung je Zeile. Die erste zutreffende gewinnt, in dieser
Reihenfolge** — die staerkste Nachricht zuerst:

*(Nachgezogen T-086, 07.09.2026: **die Reihenfolge unten ist ersetzt** — sie
lautet seit AK-167 (a), (a2), **(c)**, **(b)**, (d), (e). Ebenso sind die
Zahlen in den Klammern der einzelnen Fuellungen ersetzt: sie stammen aus der
**gebauten** Lesart und aus einer Rechnung, in der sich (b) und (c)
ueberschnitten. Verbindlich sind die Zahlen aus **AK-180** — in Umgebung A
(Wylder, `Wylder's Greatsword`, Stufe 15, 309 Kopien, 845 Effektrollen)
150 / 0 / 144 / 38 / 94 / 0 = 426. **Die Wortlaute selbst sind unveraendert
gueltig**; ersetzt sind nur die Reihenfolge, der Test von (c) (AK-177 bis
AK-179) und die Zahlen. AK-180, AK-181.)*

**(a) Der Effekt gehoert einem anderen Nightfarer** — `effecttext.works_for`
sagt Nein (150 von 426 gemessen):

> `{effect name}: works only for {owner}, and you are {hero}.`

Kennt der Datensatz keinen Besitzer und schliesst nur die Erlaubnisliste die
Figur aus:

> `{effect name}: works only for another Nightfarer, not for {hero}.`

**Abgrenzung, die niemand einebnen darf:** ein Effekt, dessen Besitzer die
**eigene** Figur ist (`[Wylder] …` auf Wylder, 15 Faelle gemessen),
funktioniert — er bekommt **nie** Fuellung (a), sondern (d).

**(a2) Eine andere Kopie hat ihn schon beigetragen** (`model.NON_ACCUMULATING`,
im Fenster heute mit `⚠` markiert):

> `{effect name}: another copy of it is already counted, so this one adds nothing.`

Dieser Fall kann nur ueber mehrere Slots auftreten; die Messung aus §0 rechnet
ein Relikt je Gruppe und sieht ihn nicht — **Haeufigkeit unbekannt, nicht
gemessen**. Er steht hier, weil er sonst stillschweigend in (d) landen wuerde
und dort das Falsche saegte: die Zahl gibt es, sie steht nur in einer anderen
Slotgruppe. **Traegt** das Ergebnis diese Auskunft nicht, faellt der Fall auf
(d) — das ist zulaessig und behauptet nichts Falsches.

**(b) Der Effekt wartet auf eine Bedingung, in der der Spieler sein kann** —
er steht als `Situational` mit `live == False` im Build, also in derselben
Menge, aus der `not_counted` gespeist wird (170 von 426):

> `{effect name}: only applies under a condition, so no number here.`

Woertlich dieselben Worte wie die Ueberschrift aus T-078 §5 (`These effects
only apply under a condition, …`), damit ein Spieler die Zeile und die Liste
am Ende des Dialogs als **dieselbe** Sache erkennt.

**(c) Der Effekt haengt an den Armaturen** — die Gattung, die
`Build.qualitative` mit "only with a matching weapon type", "needs several of
that weapon equipped" oder "changes the armament's skill" begruendet (58 von
426), und die nach QA-104 ausdruecklich **nicht** in `not_counted` gehoert:

> `{effect name}: it depends on the armaments you carry, so no number here.`

**(d) Alles Uebrige** — er wirkt, laesst sich hier aber auf keine Zahl bringen
(48 von 426: reine Engine-Wirkung, "Wylder-specific", Zeitfenster, und die 33
Widerstandseffekte aus §8):

> `{effect name}: no number here shows what this adds.`

Dieselbe Familie wie die Fluchfuellung (iii) aus T-078 §3 — **ein** Wort
anders: `costs` dort, `adds` hier. **Kein Wort ueber die Spieldateien**
(AK-140 gilt fort): der Satz sagt, dass hier keine Zahl steht, und nicht, dass
es keine gaebe. Bei den 33 Widerstandseffekten gaebe es sie.

**(e) Der Datensatz kennt den Effekt nicht** — `_effect_name` gibt `None`, es
gibt also **keinen Namen**, den man hinschreiben koennte:

> `One of its effects is not in your game data, so it has no name here and counted for nothing.`

Auf dem heutigen Spielstand kommt dieser Fall **null Mal** vor (309 Relikte,
alle Effekt- und Fluch-Ids im Datensatz aufloesbar). Er ist trotzdem
spezifiziert: `explain._effect_name` hat diesen Zweig, QA-004/QA-032 sind
genau dieser Fall, und ohne die Zeile verschwaende ein Effekt spurlos aus der
Rechnung der Zaehlzeile — der stille Fehler, den A7 verbietet.

**Laenge, gemessen:** die laengste stumme Zeile, die dieser Spielstand
erzeugen kann, ist **rund 150 Zeichen** — der Effektname
`[Wylder] Standard attacks enhanced with fiery follow-ups when using Character
Skill (greatsword only)` ist allein 101 Zeichen lang. Das ist **laenger als
alles, was T-078 kannte** (142 Zeichen in der alten Form, ~106 in der neuen).
Die Zeile bricht um, sie wird nicht gekuerzt (4.14, AK-160).

---

### 5. Die Zaehlzeile bleibt — und wird dadurch nachrechenbar

Sie bleibt woertlich wie in T-078 §6, aus drei Gruenden:

1. Sie traegt den Nenner (L-013). `{total}` ist die Zahl der Effektrollen der
   Kopie, und die steht nirgends sonst.
2. Sie ist jetzt **pruefbar gegen das, was darunter steht**: `{total} − {n}`
   muss genau die Zahl der stummen Zeilen sein. Aus einer Behauptung wird eine
   Rechnung, die ein Test nachvollziehen kann (AK-155).
3. Eine Regel mit Ausnahme ("die Zeile entfaellt, wenn alle Effekte genannt
   sind") kostet mehr, als die eine Zeile spart, die sie einspart.

**Zwei Fuellungen kommen dazu**, die T-078 §6 fehlen:

| Fall | Wortlaut |
|---|---|
| die Kopie hat **keine** Effektrolle (`Murk`, `Sovereign Sigil`, `Scenic Flatstone`) | `This relic carries no effects of its own.` |
| **kein** Effekt und **kein** Fluch der Kopie hat eine Zahl bewegt | `Nothing on this relic moved a number in this build — it fills the slot without changing the figure.` |

Die zweite ersetzt in diesem Fall die Fuellung `None of its {total} effects
moved a number in this build.` und beantwortet die Frage, die ein Spieler dann
zu Recht stellt: warum schlaegt es mir das dann vor? Die ehrliche Antwort ist
die, die dort steht — der Slot wird gefuellt, die Zahl bewegt sich nicht. Ein
Satz ueber die Suche ("das Beste, was deine Farben hergeben") waere eine
Behauptung ueber den Suchlauf, die diese Zeile nicht belegen kann.

Bewegt zwar kein Effekt, aber ein **Fluch** eine Zahl, bleibt es bei `None of
its {total} effects moved a number in this build.` — die Fluchzeile spricht
dann fuer sich, und "nothing moved a number" waere schlicht falsch.

**49 der 309 besessenen Relikte** fallen in diese Gegend (kein Effekt mit
Zahl); wie viele davon je vorgeschlagen werden, ist **nicht gemessen** — dafuer
braucht es einen vollstaendigen Lauf des Beraters, den es ohne S9/S10 noch
nicht gibt.

---

### 6. Verhaeltnis zur Liste 4.9b — beide bleiben, aus einer Menge

170 der 426 stummen Effekte sind konditional und stehen damit **auch** in der
Liste, die T-078 §5 unter die Slotgruppen setzt (`These effects only apply
under a condition, so this ranking did not count them:`). Ein Name kann also
zweimal im `Why`-Dialog stehen.

*(Nachgezogen T-086, 07.09.2026, auf Meldung des `architect` aus T-085 §6.3.
**Der Satz oben zaehlt die Liste, nicht die Fuellung** — und beide Zahlen
gelten gleichzeitig. Die **170** ist die Zahl der stummen Zeilen, deren Effekt
in `Build.situational` mit `live == False` steht, also in der Menge, aus der
diese Liste und `not_counted` gespeist werden; sie haengt **nicht** an der
Pruefreihenfolge der Fuellungen und aendert sich durch AK-167/168 und
AK-177/178 nicht. Die **124** in der Tabelle des T-084-Abschnitts und die
**144** in der Tabelle des T-086-Abschnitts sind etwas anderes: die Zahl der
Zeilen, die Fuellung (b) **bekommen**. Sie ist kleiner, weil (a), (a2) und (c)
in der Reihenfolge nach AK-167 vorher zugreifen und die Zeile aus der
**Fuellung** nehmen, nicht aus der **Liste**. Beide Zahlen sind in Umgebung §0
des T-084-Abschnitts gemessen — Wylder, `Wylder's Greatsword`, Stufe 15, 309
Kopien, 845 Effektrollen; in Umgebung B des T-086-Abschnitts lauten sie 174
und 149 von 434. AK-181.)*

**Das bleibt so, und die Liste wird nicht gekuerzt.** Sie ist **buildweit** —
sie deckt auch gehaltene Slots, die gar keine Slotgruppe haben; wer sie auf
"was in keiner Gruppe steht" zusammenstreicht, nimmt ihr den Nenner und
schafft eine dritte Menge, die niemand erklaeren kann. Die Slotgruppe
beantwortet "was tut dieses Relikt fuer mich", die Liste beantwortet "was hat
die Rechnung ausgelassen". Detail und Sammelblick, nicht zwei Fassungen
derselben Aussage.

**Was verhindert wird, ist das Auseinanderlaufen:** beide Ansichten muessen
aus **einer** Menge entstehen — den `Situational`-Eintraegen mit
`live == False` —, die eine ueber die Zuordnung `Situational.effect_id` zu
`Candidate.effect_ids` gefiltert, die andere ungefiltert. Zwei getrennte
Ermittlungen desselben Sachverhalts sind QA-082/QA-087, und die kosten dieses
Projekt zum dritten Mal Zeit (AK-154).

Die Statuszeilenklausel 4.9b bleibt buildweit und unveraendert.

---

### 7. Was das Ergebnis tragen muss (Fortschreibung von T-078 §6)

`AdvisorResult` bekommt neben `curses_without_a_figure` ein zweites Feld,
**`effects_without_a_figure`**, mit demselben Kriterium und derselben
Begruendung: ein Effekt einer **vorgeschlagenen** Kopie, zu dem die Rechnung
**keine** Zeile nach T-078 §2 aufgeschrieben hat. Nicht "ohne Zahlen in den
Spieldateien", nicht "konditional" — schlicht: es ist keine Zeile entstanden.
Kein Zaehlfeld daneben; die Anzahl ist die Laenge.

Die vier strukturellen Auflagen aus T-078 §6 gelten fuer diese Zeilen
unveraendert weiter, mit zwei Ergaenzungen:

5. **Jede stumme Zeile erreicht die Anzeige mit ihrer Fuellung** (a, a2, b, c,
   d, e) **als eigener Auskunft** und mit den einzusetzenden Namen
   (`{owner}`, `{hero}`). Das Fenster darf die Fuellung **nicht** aus dem Text
   erschliessen — kein Suchen nach `works only for`, kein Vergleich von
   Zeichenketten. Das ist AK-147, hier fortgeschrieben.
6. **Die Fuellung kommt aus derselben Rechnung, die `Build.qualitative` und
   `Build.situational` fuellt** (AD-015: keine zweite Meinung ueber denselben
   Effektsatz). `explain.py` liest sie ab, es liest den Effektsatz nicht ein
   zweites Mal.

---

### 8. Nebenbefund fuer den `director`: die Widerstandsluecke ist groesser als
### T-078 wusste

T-078 §4 nannte drei besessene Relikte mit `All Resistances Down`, deren
Zahlen weder in `sources` noch in `qualitative` stehen, weil
`model.compute_resistances` nirgendwohin schreibt, was `explain.py` liest.

**Gemessen: es sind nicht nur die Fluche.** Von den 426 stummen **positiven**
Effekten sind **33** Widerstandseffekte (`Improved Poison Resistance`,
`Improved Frost Resistance` und ihre `+1`-Varianten) — sie stehen in
`Build.qualitative` **nicht** und in `sources` **nicht**. Sie sind heute die
einzige Gruppe stummer Effekte, fuer die das Programm **keinen** Grund kennt,
und sie bekommen deshalb Fuellung (d), obwohl es die Zahl gibt.

Das aendert an dieser Vorgabe **nichts** — sie ist vorwaertskompatibel
gebaut: schreibt `compute_resistances` eines Tages nach `sources`, wandern
diese 33 Effekte und die drei `All Resistances Down`-Fluche von selbst in
gewoehnliche Zeilen nach T-078 §2. Es erhoeht aber das Gewicht der Empfehlung
aus T-078 §11: die Luecke betrifft **36 Zeilen auf einem einzigen
Spielstand**, nicht drei.

---

### 9. Akzeptanzkriterien (ab AK-151)

**Der stumme Effekt**

- **AK-151** Jeder Effekt einer vorgeschlagenen Kopie, zu dem keine Zeile nach
  T-078 §2 entstanden ist, erscheint **mit Namen** in der Slotgruppe seines
  Slots, **genau einmal**, mit `•`, in der Ordnung des Relikts. Gegenrichtung
  geprueft: ein Effekt **mit** Zahlzeile bekommt **keine** stumme Zeile. Gilt
  im Vorschlagsblock **und** im `Why`-Dialog, mit identischem Text.
- **AK-152** Der Wortlaut jeder stummen Zeile ist einer der aus §4, woertlich,
  mit Punkt am Ende. Die Fuellung wird in der dort genannten Reihenfolge
  bestimmt (a → a2 → b → c → d → e), und ein Effekt, dessen Besitzer die
  gespielte Figur **ist**, bekommt nie Fuellung (a). Pruefweg: ein
  `[Wylder]`-Effekt ohne Zahl ergibt auf Wylder (d), auf Duchess (a).
- **AK-153** `AdvisorResult` traegt `effects_without_a_figure` getrennt von
  `curses_without_a_figure` und von `not_counted`. Es enthaelt genau die
  Effekte der vorgeschlagenen Kopien ohne Zeile nach T-078 §2.
- **AK-154** Die stummen Zeilen der Fuellung (b) und die Liste aus 4.9b
  entstehen aus **einer** Menge (`Build.situational`, `live == False`).
  Pruefweg: dieselbe Bedingung als erfuellt erklaeren — der Effekt
  verschwindet in **demselben** Lauf aus beiden, oder aus keinem.
- **AK-155** In jeder Slotgruppe gilt `{total} − {n}` **genau** gleich der
  Zahl der gezeichneten stummen Zeilen — ohne Ausnahme, auch fuer Effekte
  ohne Namen im Datensatz (Fuellung e). Pruefweg: ein Ergebnis mit einer
  Effekt-Id, die der Datensatz nicht kennt.
- **AK-156** Keine stumme Zeile benutzt `✦`, `CURSE`/`BAD`, `⚠` oder eine
  Warnfarbe; die einzige verwendete Farbrolle ist `MUTED`, die Schriftgroesse
  ist die der uebrigen Effektzeilen (11 px). Pruefweg: der Text der Zeile ohne
  jede Formatierung gelesen sagt vollstaendig, was sie sagt.
- **AK-157** Keine stumme Zeile behauptet etwas ueber die Spieldateien; die
  Zeichenketten `carry no numbers` und `carries no numbers` kommen im Berater
  weiterhin nicht vor (AK-140 fortgeschrieben), und keines der Woerter aus
  AK-144 erscheint in ihr.

**Die Zaehlzeile**

- **AK-158** Die Zaehlzeile aus T-078 §6 steht in **jeder** Slotgruppe, auch
  wenn jeder Effekt darunter genannt ist, und benutzt die beiden neuen
  Fuellungen aus §5 in genau den dort genannten Faellen. Pruefweg: eine Kopie
  ohne Effektrollen (`Murk`) und eine Kopie, deren Effekte und Fluche alle
  stumm sind.

**Die Fluche (Entscheidung zu Frage 1, festgehalten)**

- **AK-159** Die Menge der Fluchnamen im **Vorschlagsblock** einer Slotkarte
  ist gleich der Menge der `curse_ids` der vorgeschlagenen Kopie, in Namen
  aufgeloest — nicht nur im `Why`-Dialog. Verglichen werden **Namen, nicht
  Zeilen**: ein Fluch, der zwei Groessen bewegt, steht in zwei Zeilen und ist
  ein Name. (Das ist AK-138 fuer den Block; beide gelten.)

**Am laufenden Fenster (A13), mit Messumgebung nach L-009 — ersetzt AK-150**

- **AK-160** *Ersetzt AK-150 vollstaendig.* Der schlechteste Fall ist
  **gemessen**, nicht geschaetzt, und er ist groesser als AK-150 annahm:

  | Groesse | AK-150 nahm an | gemessen (Umgebung §0) |
  |---|---|---|
  | Zeilen je Slotgruppe | 7 Effekt- + 2 Fluchzeilen = 9 | **14** gezeichnete Zeilen |
  | schlimmstes Relikt | unbenannt | `Deep Grand Tranquil Scene`: 3 Effekte → **9** Zahlzeilen, 3 Fluche → **4** Zahlzeilen + **1** stumme |
  | dazu je Gruppe | — | Reliktname + Zaehlzeile = **16 Zeilen** in einer Karte |
  | laengste Zahlzeile | ~105 Zeichen geschaetzt | **106** Zeichen (`[Wylder] Improved Intelligence and Faith, Reduced Strength and Dexterity: Dexterity -5, counted against it`) |
  | laengste Zeile ueberhaupt | nicht bedacht | **rund 150** Zeichen: ein stummer Effekt mit 101-Zeichen-Namen plus Fuellung (b) |
  | laengster Reliktname | "laengster des Spielstands" | `Deep Polished Tranquil Scene`, 28 Zeichen |

  **Zu pruefen:** sechs belegte Slots, darunter die Kopie von `Deep Grand
  Tranquil Scene`, die diese 14 Zeilen erzeugt. In der mittleren Spalte des
  Build planner entsteht **keine waagerechte** Bildlaufleiste, keine Zeile ist
  abgeschnitten, keine bricht mitten in einem Begriff (AK-73), jede ist durch
  senkrechtes Scrollen erreichbar, und die 150-Zeichen-Zeile **bricht um**,
  statt elidiert zu werden (4.14). Zu messen bei Fensterbreite **1320 px**
  (Startbreite) und UI scale `Automatic` **sowie** 150 %, auf einem
  100-%-Bildschirm, unter dem Qt-Stil, mit dem das Programm ausgeliefert wird.
  **Die Messung nennt Plattform, Stil, Skalierung und ob die Zahlen physisch
  oder logisch sind** — ohne diese Angaben zaehlt sie nicht (L-009).
- **AK-161** Die Zeilenzahl je Vorschlag wird nach dem Einbau **neu gemessen**
  und im Bericht genannt. Die Zahlen aus T-067 (10 bis 43 Zeilen je Vorschlag,
  Median 21) sind **vor** den stummen Zeilen entstanden und tragen nicht mehr;
  ein Vorschlag kann jetzt bis zu sechs Slotgruppen mit je bis zu 16 Zeilen
  haben.

---

### 10. Ausdruecklich nicht Teil dieses Nachtrags

- **Ob der Berater ein Relikt vorschlagen soll, dessen Effekte allesamt stumm
  sind.** Das ist eine Frage an die Rangfolge, nicht an die Sprache. Diese
  Vorgabe sagt nur, wie es dasteht, wenn es passiert.
- **Ob `model.compute_resistances` nach `sources` schreibt** (§8) —
  Entscheidung beim `director`, diese Vorgabe funktioniert in beiden Faellen.
- **Die Oberflaeche des Beraters (S10)**, die Zustandstabelle 4.1-4.14 und der
  Name des Knopfes.
- **Pixel.** §0 misst Zeilen und Zeichen. Was daraus auf dem Schirm wird,
  entscheidet AK-160 am laufenden Fenster.

---

### 11. Offene Fragen an den App Designer

1. **Der Effekt, der auf dieser Figur totes Gewicht ist — reicht ihm
   `MUTED`?** Fuellung (a) trifft **150 der 426** stummen Effekte auf dem
   eigenen Spielstand, und sie ist die einzige, die sagt: dieser Effekt tut
   hier **nie** etwas. Der Rest des Programms zeigt genau das auf den
   Slotkarten als `NOT WORKING` mit Durchstreichung. Im Vorschlagsblock steht
   er nach dieser Vorgabe still und grau wie die anderen Fuellungen — weil der
   App Designer gesagt hat: keine Warnfarbe, er kostet nichts. Das ist
   richtig, solange man "kostet" als Rechengroesse liest. Als **Slotplatz**
   kostet er sehr wohl. Soll Fuellung (a) die Behandlung bekommen, die der
   Rest des Programms ihr gibt?
2. **Sollen die stummen Zeilen im Vorschlagsblock stehen, oder nur im
   `Why`-Dialog?** Diese Vorgabe zeigt sie an beiden Orten, weil zwei Formen
   an zwei Orten die Fehlerklasse aus QA-082 sind. Der Preis ist Hoehe: die
   Karte waechst im gemessenen schlimmsten Fall auf 16 Zeilen, und eine davon
   ist 150 Zeichen lang. Die Gegenposition waere: im Block nur die Zeilen mit
   Zahl und die Fluche, die stummen Effekte erst im Dialog — anders als beim
   Fluch waere das kein verstecktes Risiko, denn ein stummer Effekt ist keine
   Falle.

---

## Director-Korrektur zu T-078/T-080 — 06.09.2026, entschieden vom App Designer

Der App Designer hat entschieden, nachdem der gemessene Schlechtfall
(14 gezeichnete Zeilen plus zwei Kopfzeilen, AK-160) vorlag. Beide Punkte
gehen den Vorgaben oben vor.

**1. Stumme Zeilen stehen nur im `Why`-Dialog.** AK-151s letzter Satz ("Gilt
im Vorschlagsblock **und** im `Why`-Dialog, mit identischem Text") wird
ersetzt: die stummen Effektzeilen erscheinen **ausschliesslich im
`Why`-Dialog**. Im Vorschlagsblock steht davon nur die Zaehlzeile (AK-155,
AK-158).

Begruendung, die auch die Abgrenzung traegt: **ein Fluch ist eine Falle, ein
stummer Effekt nicht.** Der Preis muss vor dem Anwenden sichtbar sein, das
Nichts nicht. **AK-159 bleibt daher unveraendert** — jeder Fluch der
vorgeschlagenen Kopie steht weiterhin einzeln im Block, auch der ohne Zahl.

Folge fuer AK-160: der Schlechtfall des **Blocks** faellt entsprechend
kleiner aus als dort gemessen; die 14 Zeilen gelten fuer den **Dialog**.
AK-161 (nach dem Einbau neu messen) gilt fuer beide Orte getrennt.

**2. Fuellung (a) wird dargestellt wie im uebrigen Programm.** Ein Effekt,
der einer anderen Figur gehoert, ist im Programm bereits als
`NOT WORKING` mit Durchstreichung gezeichnet (`nrplanner/effecttext.py`,
`nrplanner/app.py:3767` und `:3786`). Die stumme Zeile dieser Fuellung
uebernimmt **diese Darstellung**, nicht `MUTED`. Zwei Darstellungen fuer
dieselbe Sache waeren die Inkonsistenz, die sich ein Spieler merken muesste;
es ist mit 150 von 426 der haeufigste Fall ueberhaupt.

**Der Wortlaut bleibt der aus §4 (a)** — `{effect name}: works only for
{owner}, and you are {hero}.` Er nennt den Besitzer, was der bestehende Text
`NOT WORKING -- another Nightfarer only` nicht tut. Uebernommen wird die
**Darstellung**, nicht der Satz.

**AK-156 gilt unveraendert fuer alle uebrigen Fuellungen** (a2, b, c, d, e):
kein `✦`, kein `CURSE`/`BAD`, kein `⚠`, keine Warnfarbe, nur `MUTED`.
Fuellung (a) ist die benannte Ausnahme, und sie ist keine Warnung, sondern
dieselbe Aussage, die das Programm anderswo schon macht.

---

## Nachtrag zu AK-63, 4.7, `budget_note` und der Grenze (c)/(d):
## vier Wortlaute und eine Zaehlgrenze vor S10b/S10c
## (ui-ux-designer, T-084) — 2026-09-07

**Grundlage:** `docs/tasks/T-084.md` · `ARCHITECTURE.md` Nachtrag VI (AD-025,
Pruefpunkte 29-33, OF-19, die Risikozeile bei Zeile 3393) und AD-010 ·
der Nachtrag zu QA-116 oben (T-052, Zeile 1229 ff., aus dem AK-63 stammt) und
der Nachtrag zu OF-20/QA-108/QA-113 (AK-67, Zeile 1509 ff.) ·
`nrplanner/advisor/goals.py` (`_ATTACK_RATING_SCOPE`, `_DAMAGE_TAKEN_SCOPE`,
`_NO_ARMAMENT`, `_NO_ARMAMENT_NOTE`, `EVEN_WEIGHTING`) ·
`nrplanner/advisor/types.py` (`Goal`, `GoalScore`, `Baseline`, `SlotPool`,
`AdvisorResult`, die sechs `SILENT_*`-Marken) ·
`nrplanner/advisor/explain.py` (`_silent_effect`, `_ARMAMENT_GATES`,
`reasons`, `not_counted`) · `nrplanner/advisor/run.py` (Modul-Docstring zu
`budget_note`) · `nrplanner/model.py` (`GATE_FIELDS`, `satisfied_by_weapon`,
`is_conditional`, `compute_qualitative`) · `qa/findings.md` QA-104, QA-108 ·
der T-078- und der T-080-Abschnitt dieser Datei.

**Was dieser Nachtrag ist:** vier fehlende Nutzertexte und eine falsch
angeschriebene Zaehlgrenze, geschlossen **bevor** die Oberflaeche gebaut wird.
Er fuegt keinen Zustand und kein Bedienelement hinzu. Neue
Akzeptanzkriterien: **AK-162 bis AK-176**.

---

### 0. Messumgebung (L-009) — woran die Zahlen unten gemessen sind

Alle Zaehlungen in §2 stammen aus **einer** Umgebung und gelten nur fuer sie:

| | |
|---|---|
| Datensatz | `paths.snapshot_path()`, der gebaute Abzug dieser Maschine, nur gelesen |
| Bestand | der Spielstand des App Designers, **309** besessene Kopien, **845** Effektrollen darauf |
| Nightfarer | Wylder, Stufe 15 |
| Armatur | `Wylder's Greatsword` als Bezugs- **und** einzige gefuehrte Waffe |
| Bedingungen | keine als erfuellt erklaert (`declared` leer) |
| Aufbau | **ein** Relikt je Slotgruppe, Slot 0, kein gehaltener Slot |
| Gerechnet mit | `explain.reasons` selbst, nicht mit einer Nachbildung der Zeilenlogik |

**Was diese Zahlen nicht decken:** einen anderen Nightfarer (Fuellung (a) ist
eine Wylder-Zahl), eine andere Waffengattung (die Grenze in §2 haengt an
`satisfied_by_weapon`, also am gefuehrten Waffentyp), einen Lauf ueber mehrere
Slots (Fuellung (a2) bleibt ungemessen, wie in T-080) und jede Pixelbreite
(kein Fenster gestartet, siehe §4).

---

### 1. AK-63 neu: die Anzeige liest **zwei** Quellen (OF-19)

**Der Fehler, den das verhindert.** AD-025 hat die Vorbehalte in zwei Klassen
geteilt: der **Verfahrenssatz** wohnt in der Registry (`Goal.scope`, nie
leer), der **Laufbefund** im Ergebnis (`Baseline.unknowns`,
`Baseline.weights_note`, `SlotPool.unknowns`, `AdvisorResult.unknowns`,
`AdvisorResult.weights_note`). Die Fassung von AK-63 aus T-052 nennt fuer den
Picker nur `Goal.scope` (Zeile 4) und `SlotPool.unknowns` (Zeile 3b). Die
**dritte** Haelfte — die Laufbefunde der Zielrichtung — hat bis heute keinen
Ort. Wer AK-63 spec-treu umsetzt, laesst im Lauf **ohne** Referenzwaffe den
Satz `No armament selected — ranked on attack multipliers only, without
weapon scaling.` (`goals._NO_ARMAMENT`) ersatzlos verschwinden. Das ist genau
der A7-Rueckschritt, vor dem die Risikozeile in `ARCHITECTURE.md` warnt, und
er faellt auf dem Hauptweg des Beraters an (AD-018).

**Verbindlich, ersetzt die AK-63-Fassung aus T-052** (die dortige Begruendung
bleibt gueltig und bleibt stehen; ersetzt wird nur, **welche Felder** gelesen
werden):

**(1) Die Registry-Haelfte — Zeile 4 des Pickers, Punkt 4 des `Why`-Dialogs.**
Unveraendert gegenueber T-052: im Picker zuerst die feste
AD-018.3-Pflichtzeile, danach die Saetze aus `Goal.scope` der gewaehlten
Zielrichtung, wortgleich, in Tupel-Reihenfolge, vollstaendig. Fuer `Name`
(AK-49) entfaellt die Zeile ganz. Im `Why`-Dialog dieselben Saetze, einmal, im
Dialogkopf.

**(2) Die Ergebnis-Haelfte im Picker — Zeile 3b, jetzt mit zwei Quellen.**
Zeile 3b traegt **alle** Laufbefunde des angezeigten Ergebnisses, in **einem**
umbrechenden Textblock, Saetze mit `  ·  ` getrennt (AK-67 gilt fort), in
dieser Reihenfolge:

1. die Saetze aus `Baseline.unknowns` **der Zielrichtung, nach der der Pool
   geordnet ist** (`SlotPool.rank_by`) — heute genau `_NO_ARMAMENT`, und nur
   ohne Referenzwaffe;
2. danach die Saetze aus `SlotPool.unknowns` — heute die bis zu drei Saetze
   aus AK-67.

Reihenfolge und Grund: der erste Satz betrifft die **Zahl** auf jeder Karte,
der zweite den **Bestand**, aus dem die Karten stammen. Der Spieler liest die
Zahl zuerst.

Zeile 3b **entfaellt vollstaendig**, wenn beide Quellen leer sind — der
Normalfall mit gewaehlter Waffe (0 von 309 Kopien ohne Handle, `unknowns` der
Zielrichtung leer). Leer ist nach AD-025.2 eine Aussage, keine Luecke.

**(3) `weights_note` erscheint im Picker nicht, solange es kein Bedienelement
fuer die Gewichtung gibt (OF-3).** Grund, und er ist kein Platzargument: bei
`Minimise damage taken` ist `Baseline.weights_note` **nie** leer
(`EVEN_WEIGHTING.note`), und er beginnt mit denselben acht Woertern wie der
zweite Satz aus `MIN_DAMAGE_TAKEN.scope` in Zeile 4 — *"The game data gives no
relative frequency of damage types, so …"*. Zwei Zeilen untereinander, die
gleich anfangen und verschieden enden, liest niemand als zwei Aussagen; er
liest sie als Wiederholung und ueberspringt beide. Der Satz steht deshalb im
`Why`-Dialog (siehe (4)). **Sobald** OF-3 ein Bedienelement fuer die
Gewichtung bringt, gehoert er neben dieses Bedienelement — dann sagt er,
welche Wahl gerade gilt, und ist keine Wiederholung mehr.

**(4) Die Ergebnis-Haelfte beim `Optimize`-Lauf — `Why`-Dialog, Punkt 4.**
Unter den `Goal.scope`-Saetzen, in dieser Reihenfolge, jeder Teil nur wenn
nicht leer:

1. die Saetze aus `AdvisorResult.unknowns`,
2. danach `AdvisorResult.weights_note` als eigene Zeile.

Die gleichlautenden Felder der `Baseline`-Eintraege desselben Ergebnisses
werden **nicht zusaetzlich** gezeichnet — sie tragen dieselbe Auskunft je
Zielrichtung, und zweimal gezeichnet ist es die Fehlerklasse aus AK-148
(`reasons` **und** `curses`). `SlotPool.unknowns` bleibt beim Slot (§3.4
Punkt 2, T-052 unveraendert).

**(5) Was gilt, wenn beide Haelften etwas zu sagen haben:** beide werden
gezeichnet, jede an ihrem Ort, keine unterdrueckt die andere, und die Anzeige
vergleicht die beiden Listen **nicht**. Ein Satz, der in beiden Klassen steht,
ist ein Fehler der Rechnung (AD-025.4, Pruefpunkt 30) und wird sichtbar
gemacht, nicht weggefiltert: eine Anzeige, die entdoppelt, versteckt genau den
Fehler, gegen den der Pruefpunkt geschrieben ist. Das ist AK-147, hier
fortgeschrieben.

**Akzeptanzkriterien**

- **AK-162** *(Registry-Haelfte, ersetzt die erste Haelfte von AK-63.)*
  Zeile 4 des Pickers und Punkt 4 des `Why`-Dialogs zeigen die Saetze aus
  `Goal.scope` der gewaehlten Zielrichtung wortgleich, in Tupel-Reihenfolge,
  vollstaendig — daneben kein im UI-Code verdrahteter Vorbehaltssatz.
  Pruefweg: `advisor/goals.py` um einen sechsten `scope`-Satz erweitern; er
  steht danach an beiden Orten, ohne dass eine UI-Zeichenkette angefasst
  wurde. *Rot-vorher:* eine Umsetzung, die den Attack-Rating-Vorbehalt als
  Konstante in den Picker schreibt, bleibt bei `Minimise damage taken` auf dem
  falschen Satz stehen.
- **AK-163** *(Ergebnis-Haelfte im Picker, ersetzt die zweite Haelfte von
  AK-63.)* Zeile 3b traegt zuerst jeden String aus `Baseline.unknowns` der
  Zielrichtung aus `SlotPool.rank_by`, danach jeden String aus
  `SlotPool.unknowns`, jeweils wortgleich und in Tupel-Reihenfolge, in einem
  Block; sie entfaellt genau dann, wenn beide leer sind. *Rot-vorher:* die
  heutige AK-63-Fassung liest nur `SlotPool.unknowns` — ein Lauf **ohne**
  Referenzwaffe zeigt dann keine einzige Zeile darueber, dass ohne Waffe
  gerechnet wurde, obwohl `goals.py` den Satz liefert.
- **AK-164** *(Ergebnis-Haelfte beim Lauf.)* Punkt 4 des `Why`-Dialogs zeigt
  unter den `Goal.scope`-Saetzen `AdvisorResult.unknowns` und danach
  `AdvisorResult.weights_note`, wortgleich, jeweils nur wenn nicht leer; die
  `unknowns`/`weights_note` der `Baseline`-Eintraege desselben Ergebnisses
  werden nicht zusaetzlich gezeichnet. *Rot-vorher:* eine Umsetzung, die ueber
  `result.baseline` iteriert **und** `result.unknowns` zeichnet, zeigt
  `No armament selected — …` zweimal untereinander.
- **AK-165** *(keine Chirurgie, keine Entdopplung.)* Kein Anzeigecode
  vergleicht, filtert, sortiert oder entdoppelt die Saetze der beiden
  Haelften; er zeichnet sie in der gelieferten Reihenfolge. Pruefbar per Grep
  ueber den S10-Code: auf `scope`, `unknowns`, `weights_note` kein `set(`,
  kein `sorted(`, kein `if … not in …`. *Rot-vorher:*
  `for s in dict.fromkeys(scope + unknowns)` — sieht sauber aus und macht
  Pruefpunkt 30 blind.
- **AK-166** *(`weights_note` im Picker.)* Solange es kein Bedienelement fuer
  die Gewichtung gibt, kommt der Text von `EVEN_WEIGHTING.note` im Picker
  **nicht** vor. Pruefweg: ausgelesener Text des Pickers gegen die
  Zeichenkette. *Rot-vorher:* eine Umsetzung, die `weights_note` an Zeile 3b
  haengt, zeigt bei `Minimise damage taken` zwei Zeilen untereinander, die mit
  *"The game data gives no relative frequency of damage types"* anfangen.

---

### 2. Die Grenze zwischen Fuellung (c) und (d) — gezaehlt, und sie lag woanders als vermutet

**Der Befund zuerst, weil er die Frage des Auftrags berichtigt.** Der Auftrag
geht davon aus, die Grenze liege **innerhalb** der 106 Zeilen, die heute (c)
und (d) tragen, und die Summe 106 sei deshalb unveraendert. Gezaehlt am
Bestand stimmt das nicht: die Grenze liegt zwischen **(b) und (c)**, und
(c)+(d) waechst von 106 auf 152. Die Summe ueber **alle** Fuellungen bleibt
426.

**Warum die 48 aus T-080 nie gemessen waren.** Die Tabelle in
`docs/berichte/T-080-ui-ux-designer.md` §3 nennt 150 / 170 / 58 / 48. Die
ersten drei sind gemessen, die vierte ist ein **Rest**: 426 − 150 − 170 − 58.
Diese Rechnung setzt voraus, dass die vier Toepfe sich nicht ueberschneiden —
und genau das tun sie. **46 der 58 armaturgebundenen Effekte stehen zugleich
in den 170**, weil eine unerfuellte Waffentyp-Schranke den Effekt nach
`Build.situational` bringt (`model.compute_qualitative`) und Fuellung (b) ihn
in der angeschriebenen Reihenfolge **vor** (c) abfaengt. Der echte Rest ist
94, nicht 48. Der Fehler steckte in der Reihenfolge, nicht in der Zaehlung.

**Die Zahlen, beide Lesarten, eine Grundgesamtheit** (Umgebung §0;
Grundgesamtheit: 845 Effektrollen auf 309 Kopien, davon **426** stumme
Effektzeilen — Fluchzeilen zaehlen nicht mit):

| Fuellung | **(b) vor (c)** — heute angeschrieben und heute gebaut | **(c) vor (b)** — diese Vorgabe |
|---|---|---|
| (a) anderer Nightfarer | 150 | 150 |
| (a2) anderswo gezaehlt | 0 (bei einem Relikt je Gruppe nicht herstellbar) | 0 |
| (b) Bedingung | **170** | **124** |
| (c) Armaturen | **13** | **58** |
| (d) Rest | **93** | **94** |
| (e) nicht im Datensatz | 0 | 0 |
| **Summe** | **426** | **426** |
| (c) + (d) | 106 | **152** |

**Die Regel, neu angeschrieben — zwei Aenderungen an §4 des T-080-Abschnitts:**

**(i) Die Pruefreihenfolge ist (a), (a2), (c), (b), (d), (e).** Fuellung (c)
wird **vor** (b) geprueft. Grund: fuer einen Effekt, dessen Schranke die
Armatur ist, ist *"it depends on the armaments you carry"* die staerkere
Nachricht — sie nennt den Hebel (eine andere Waffe fuehren), waehrend *"only
applies under a condition"* den Spieler auf die Suche nach einer Bedingung
schickt. Das ist dieselbe Begruendung, mit der (a) vor allem anderen steht. Es
ist ausserdem die Lesart, die der Rest des Systems bereits behauptet:
`explain.not_counted` sagt in seinem eigenen Docstring, ein Effekt an einer
nicht gefuehrten Armatur sei *nicht* in `not_counted`, unter Berufung auf
QA-104 — und der T-080-Text zu (c) sagt denselben Satz.

**(ii) Der Test von (c) fragt nach der unerfuellten Schranke, nicht nach dem
Feld.** Fuellung (c) trifft zu, wenn der Effekt eines der vier
Armaturenfelder traegt — `triggerOnWepType`, `wepTypeTrigger`,
`wepTypeTriggerCount`, `startSwordArtsId` — **und** `model.satisfied_by_weapon`
fuer dieses Feld gegen die gefuehrten Waffentypen falsch ist. Die heutige
Fassung fragt nur, ob das Feld vorhanden ist, und schreibt deshalb an genau
einer Stelle des Bestands etwas Falsches: `HP Restoration upon Greatsword
Attacks` bekommt bei gefuehrtem `Wylder's Greatsword` die Zeile *"it depends
on the armaments you carry"*, obwohl der Spieler den Greatsword traegt und die
Armaturenfrage beantwortet ist. Diese eine Zeile faellt mit (ii) nach (d), wo
sie hingehoert: sie ist stumm, weil sie beim Angriff ausloest
(`atkOccurrenceSpEffectId`), nicht wegen der Waffe.

**Die Wortlaute (b), (c) und (d) aendern sich nicht** — nur, welche Zeile
welchen bekommt.

**Was diese Verschiebung nicht anfasst: 4.9b und `not_counted`.** Die Liste
unter den Slotgruppen und die Statuszeilenklausel 4.9b bleiben
`Build.situational, live == False` (AK-142 unveraendert, AD-010 unveraendert).
Fuellung (c) nimmt einen Effekt aus der **Zeile**, nicht aus der **Liste**:
die Zeile beantwortet *"warum steht bei diesem Effekt keine Zahl"*, die Liste
beantwortet *"wie viel hat die Rangfolge weggelassen"*. Beide Antworten sind
wahr, und die Ueberschrift der Liste (*"These effects only apply under a
condition, …"*) bleibt fuer einen waffengebundenen Effekt richtig — sie ist
nur allgemeiner als die Zeile. **AK-154 gilt fort mit dieser Praezisierung:**
die Fuellungen (b) und (c) entstehen weiterhin aus **einer** Rechnung, und der
dort genannte Pruefweg haelt fuer beide — dieselbe Bedingung als erfuellt
erklaert, und der Effekt verschwindet in demselben Lauf aus der Liste **und**
aus den stummen Zeilen.

**Akzeptanzkriterien**

- **AK-167** *(Reihenfolge.)* Die sechs Fuellungen werden in der Reihenfolge
  (a), (a2), (c), (b), (d), (e) geprueft, erste zutreffende gewinnt.
  *Rot-vorher:* die heute gebaute Reihenfolge gibt in der Umgebung §0 **46**
  Zeilen `… : only applies under a condition, so no number here.` fuer
  Effekte, deren einziger Grund eine nicht gefuehrte Waffengattung ist.
- **AK-168** *(Test von (c).)* Fuellung (c) trifft genau dann zu, wenn der
  Effekt eines der vier Armaturenfelder traegt **und** `satisfied_by_weapon`
  fuer dieses Feld gegen die gefuehrten Waffentypen falsch ist. *Rot-vorher:*
  die heutige Fassung fragt nur nach dem Vorhandensein des Feldes und sagt in
  der Umgebung §0 fuer `HP Restoration upon Greatsword Attacks` bei
  gefuehrtem Greatsword *"it depends on the armaments you carry"*.
- **AK-169** *(Partition, mit Rezept.)* Die sechs Fuellungen sind eine
  **Partition** der stummen Effektzeilen: jede stumme Zeile traegt genau eine,
  und die Summe der sechs ist die Zahl der stummen Zeilen. Pruefweg: ueber den
  Bestand zaehlen, mit `explain.reasons` selbst; in der Umgebung §0 ergibt das
  150 / 0 / 124 / 58 / 94 / 0 = **426** von 845 Effektrollen auf 309 Kopien.
  *Rot-vorher:* die Tabelle aus T-080 §3 (150 / 170 / 58 / 48) ist **keine**
  Partition — 46 Zeilen sind doppelt gezaehlt, und die 48 ist ein Rest aus
  einer Subtraktion, kein Messwert.

---

### 3. `AdvisorResult.budget_note` — kein Satz jetzt, und warum das Feld trotzdem bleibt

**Entscheidung: das Feld bekommt jetzt keinen Wortlaut, bleibt leer, und die
Oberflaeche zeichnet fuer ein leeres Feld nichts.** Es wird **nicht**
gestrichen.

**Warum kein Satz.** Eine Budgetnotiz sagt, dass dieser Lauf seine Suche
**vorzeitig beendet** hat. Die Groesse, an der sich das entscheidet, setzt der
`performance-tuner` erst in S11; ein Text, der heute eine Breite oder eine
Zahl nennt, verspricht eine Groesse, die niemand gemessen hat, und das ist
genau der Fall, den A12 ausschliesst.

**Warum auch kein zahlenfreier Ersatzsatz.** Der naheliegende Ausweg waere ein
Satz ohne Zahl — etwa *"Not every combination was tried."* Der ist wahr, aber
er ist in **jedem** Lauf wahr, und ein Satz, der jeden Lauf ueberlebt, ist
nach AD-025 ein **Verfahrenssatz** und gehoert in die Registry, nicht ins
Ergebnis (Pruefpunkt 31 wuerde ihn dort rot faerben). Die Aussage ist
ausserdem schon getragen: AD-025.5 haelt `Best found` und `Top suggestions`
als verbindliche Nutzersprache fest und verbietet `Optimal` und
`Best possible`. Es geht heute also nichts verloren.

**Warum das Feld bleibt.** AD-010 verlangt es, der Fall, fuer den es da ist,
kommt in S11 wirklich, und `run.py` sagt in seinem Docstring bereits, dass es
leer bleibt, bis der Satz existiert. Ein Feld zu streichen und drei Wochen
spaeter wieder einzubauen kostet mehr als eine leere Zeichenkette. **Das ist
kein Befund an den `architect`** — die Vorgabe des Auftrags fuer diesen Fall
("dann wird das Feld entfernt") greift nicht, weil die Antwort nicht "gar
nicht" lautet, sondern "noch nicht".

**Der Ort, fuer den Tag, an dem der Satz existiert:** der `Why`-Dialog, als
eigene Zeile unmittelbar unter den Saetzen aus Punkt 4 — **nicht** die
Statuszeile. Grund: die Statuszeile kuerzt (§3.1), und eine Aussage darueber,
was die Suche **nicht** versucht hat, waere die letzte im Satz und damit die
erste, die verschwindet. Was der Nutzer dort verpasst, ist genau die
Einschraenkung, um derentwillen der Satz geschrieben wurde.

**Akzeptanzkriterien**

- **AK-170** Solange `AdvisorResult.budget_note` leer ist, zeichnet die
  Oberflaeche dafuer **nichts** — keine Ueberschrift, keinen Platzhalter,
  keinen leeren Aufzaehlungspunkt, kein `—`. *Rot-vorher:* ein `Why`-Dialog,
  der eine Zeile `Search budget: —` oder einen leeren Absatz zeigt, weil das
  Feld bedingungslos gezeichnet wird.
- **AK-171** Ist das Feld nicht leer, steht sein Satz im `Why`-Dialog als
  eigene Zeile unmittelbar unter den Saetzen aus Punkt 4, und **nirgends** in
  der Statuszeile. *Rot-vorher:* eine dritte Klausel `  ·  the search was cut
  short.` an 4.6 — sie faellt bei der gemessenen Statuszeilenlaenge als erste
  der Kuerzung zum Opfer.
- **AK-172** In `budget_note` steht kein Satz, der in jedem Lauf zutraefe.
  Pruefweg: zwei herstellbare Laeufe derselben Zielrichtung; ein Satz, der in
  beiden dasteht, gehoert nach `Goal.scope` (AD-025, Pruefpunkt 31).
  *Rot-vorher:* `budget_note = "Not every combination was tried."` als feste
  Zuweisung in `run.py`.

---

### 4. Die Statuszeile 4.7 — die Aussage wird bestaetigt, ihre Form nicht

**Heute in der Tabelle:** `Your build changed while this was working out.
Optimize again.` Die zweite Haelfte hat der `developer` in T-082 selbst
formuliert, weil keine vorlag.

**Die Aussage ist richtig und bleibt.** Der Nutzer muss zwei Dinge erfahren:
dass das Ergebnis verworfen wurde, und dass ein neuer Lauf es zurueckholt.
`Optimize again.` sagt das zweite und ist keine Ruege — der Berater schreibt
ohnehin in keinen Slot ohne Zustimmung (§5.1), es ist also nichts kaputt
gegangen, das der Nutzer verursacht haette.

**Die Form aendert sich.** `Optimize again.` ist in der ganzen Tabelle
4.1-4.14 der **einzige** nackte Imperativ. Der Weg nach vorn wird sonst als
Angebot mit dem Namen des Bedienelements gegeben (4.8: `… — use Rescan
save.`) oder als Feststellung (4.13: `Applied. Undo puts your slots back as
they were.`). Ein Imperativ nach einem Satz, der eine Stoerung beschreibt,
liest sich als Zuweisung; dieselbe Auskunft im Hausmuster liest sich als
Angebot. **Verbindlich, 4.7 lautet:**

> `Your build changed while this was working out — use Optimize again.`

**Zur Breite, ehrlich gesagt: nicht in Pixeln gemessen.** Die Advisor bar
existiert zur Zeit dieses Nachtrags nicht (T-083 baut sie parallel), und eine
Offscreen-Messung waere hier wertlos: `QApplication.font()` liefert unter
`QT_QPA_PLATFORM=offscreen` auf dieser Maschine eine Ersatzschrift mit **exakt
12,0 px je Zeichen** ueber alle 17 gemessenen Statustexte — ein Artefakt der
Ersatzschrift, keine Messung (L-009), und `Segoe UI` wird dorthin substituiert
statt geladen. Was ohne Fenster belastbar ist, ist der **Vergleich in
Zeichen** gegen die bereits abgenommenen Statustexte:

| Statuszeile | Zeichen |
|---|---|
| 4.9, beide Klauseln | 131 |
| 4.10 | 102 |
| 4.11 | 76 |
| 4.8 | 74 |
| 4.9, eine Klausel | 72 |
| **4.7 neu** | **67** |
| 4.7 heute | 62 |

4.7 bleibt damit kuerzer als vier bereits abgenommene Zustaende und traegt
**kein neues** Kuerzungsrisiko in die Leiste. Das ist eine Aussage ueber die
Rangfolge, **nicht** ueber die Sichtbarkeit: ob der Satz an der Mindestbreite
ungekuerzt ankommt, entscheidet erst das laufende Fenster (AK-174).

**Akzeptanzkriterien**

- **AK-173** 4.7 lautet buchstabengetreu `Your build changed while this was
  working out — use Optimize again.`, mit demselben Gedankenstrich `—` wie
  4.8, in Statuszeile, Tooltip und `Why`-Dialog gleich. *Rot-vorher:* der heutige Wortlaut mit dem
  nackten `Optimize again.` — der einzige Imperativ ohne Nennung des
  Bedienelements unter den vierzehn Zustaenden.
- **AK-174** Der Satz aus 4.7 erreicht den Nutzer **ungekuerzt in der
  Statuszeile**, an der Mindestbreite des Build planner. Reicht der Platz
  nicht, gibt die Anordnung der Leiste nach (schmalere Zielwahl, weniger
  Abstand), nicht der Satz. Gemessen wird am laufenden Fenster mit
  Messumgebung nach L-009 (Stil, Skalierung, physisch oder logisch).
  *Rot-vorher:* eine Umsetzung, bei der `— use Optimize again.` als erstes
  elidiert und die Handlungsanweisung nur noch im Tooltip steht — eine
  Aussage, die nur im Tooltip ankommt, ist keine.
- **AK-175** Keine Statuszeile des Beraters gibt dem Nutzer die Schuld: keine
  Zeile enthaelt `you changed`, `you must`, `please`, `try again` oder ein
  Ausrufezeichen. Pruefweg: der ausgelesene Text aller vierzehn Zustaende
  gegen diese Wortliste. *Rot-vorher:* `You changed your build while this was
  working out!`

---

### 5. `Suggest` im Fliesstext — je Stelle einzeln entschieden

Der Knopf heisst `Optimize` (GOAL F4, Director). Die Zustandstabelle 4.1-4.14
ist seit `bafc3e1` nachgezogen. Die sechs verbliebenen Stellen:

| Stelle | Befund | Getan |
|---|---|---|
| §5.1 ("`Optimize` ist der heutige `Suggest`-Knopf") | **geltende Vorgabe, falsch** — "heutige" behauptet einen Knopf, den es nicht gibt | umgeschrieben auf "der in der Fassung vom 01.09.2026 noch `Suggest` hiess", mit Datumsvermerk |
| F4 der T-004-Fragen ("Alternativen waeren `Suggest a build`") | **Historie**, und sie meint den Namen des **Bereichs**, nicht den Knopf | stehen gelassen, Zusatz angehaengt, der die Verwechslung ausschliesst |
| T-024 §1 ("der Knopf heisst `Optimize` statt `Suggest`") | **geltende Vorgabe, richtig** — das ist die Umbenennung selbst | unveraendert |
| offene Frage 3 des T-078-Abschnitts | **offene Frage, beantwortet** | als beantwortet markiert, nicht geloescht; die Begruendung von damals bleibt |
| T-078 "Grundlage" (`Candidate`, `Suggestion`, …) | **Typname**, kein Bedienelement | unveraendert |
| T-078 "nicht Teil dieser Vorgabe" (`Suggestion` als Datenform) | **Typname** | unveraendert |

- **AK-176** In `UI_SPEC.md` bezeichnet `Suggest` kein heutiges Bedienelement
  mehr: jede verbleibende Fundstelle ist entweder ein Typname (`Suggestion`)
  oder ausdruecklich als Verlauf gekennzeichnet. Pruefweg: Volltextsuche nach
  `Suggest`, jede Fundstelle einer der beiden Klassen zuordenbar.
  *Rot-vorher:* §5.1 in der Fassung vor diesem Nachtrag — wer nur dort liest,
  baut einen Knopf, der zwei Namen hat.

---

### 6. Was dieser Nachtrag ausdruecklich **nicht** entscheidet

- **Ob `explain.not_counted` seinen eigenen Docstring einhaelt.** Er sagt, ein
  Effekt an einer nicht gefuehrten Armatur sei nicht darin (unter Berufung auf
  QA-104); gemessen sind **46 von 170** es doch. Entweder der Docstring oder
  die Rechnung ist falsch — das ist AD-010 und gehoert dem `architect`, nicht
  der Anzeige. Diese Vorgabe funktioniert in **beiden** Faellen: §2 verschiebt
  nur die **Zeile**, nicht die Liste.
- **Die Formatierung einer Differenz je Zielrichtung** (OF-21). Unberuehrt.
- **Der Wortlaut, wenn OF-3 ein Bedienelement fuer die Gewichtung bringt.**
  §1 Punkt (3) sagt nur, wohin `weights_note` dann gehoert, nicht wie das
  Bedienelement aussieht.
- **Die dreizehn Streichvorschlaege je Tab (§8)** und die vier gesammelten
  Fragen an den App Designer (F-B, F-C, F-F, F-G). Unberuehrt.

---

## (ui-ux-designer, T-086) — 2026-09-07

**Grundlage:** `docs/tasks/T-086.md` · `docs/berichte/T-085-architect.md`
(AD-026 und die zwei Befunde daraus, Umgebung Ironeye/Bow) ·
`ARCHITECTURE.md` Nachtrag VII (nur gelesen) · der T-084-Abschnitt dieser
Datei (§0, §2, AK-167 bis AK-169) und §4/§6 des T-080-Abschnitts · gegen den
Commit `fd9f2bc` gelesen und gemessen: `nrplanner/model.py`
(`CONDITIONAL_FIELDS`, `WEAPON_TYPE_GATES`, `satisfied_by_weapon`,
`is_conditional`, `GATE_FIELDS`, `ENGINE_FIELDS`),
`nrplanner/advisor/explain.py` (`_ARMAMENT_GATES`, `_silent_effect`,
`reasons`, `not_counted`), `evaluate.py`, `goals.py`, `types.py`,
`nrplanner/inventory.py`.

**Was dieser Nachtrag ist:** eine Praezisierung von AK-168 und eine
Zahlenangabe im Fliesstext. **Kein neuer Zustand, kein neues Bedienelement,
kein geaenderter Nutzertext** — die sechs Fuellungen behalten ihren Wortlaut
Buchstabe fuer Buchstabe; es aendert sich nur, welche Zeile welchen bekommt.

- **AK-167 bleibt unveraendert.** Die Pruefreihenfolge (a), (a2), (c), (b),
  (d), (e) ist richtig und traegt.
- **AK-168 wird praezisiert, nicht ersetzt.** Sein Test — die *unerfuellte*
  Schranke statt des blossen Feldes — ist richtig; er ist nur **zu weit
  gefasst**. AK-177 und AK-178 ziehen die Grenze nach.
- **AK-169 behaelt seine Regel** (die Fuellungen sind eine Partition, mit
  Rezept); **seine Zahlen sind durch AK-180 fortgeschrieben** und dort als
  ersetzt gekennzeichnet.

Neue Akzeptanzkriterien: **AK-177 bis AK-181**.

---

### 0. Messumgebung (L-009) — woran die Zahlen unten gemessen sind

Zwei Umgebungen, beide erschoepfend ausgezaehlt. **Keine Stichprobe, also
kein Stichprobenfehler und kein Sicherheitsabstand**; die Unsicherheit liegt
in der Grundgesamtheit — ein Spielstand, ein Datenabzug, zwei von zehn
Nightfarern. Alle Zahlen sind **Zeilen im `Why`-Dialog**, nicht Effekt-Ids und
nicht Pixel.

| | **Umgebung A** | **Umgebung B** |
|---|---|---|
| Nightfarer | Wylder, Stufe 15 | Ironeye, Stufe 15 |
| Armatur | `Wylder's Greatsword` (`wep_type` 5), Bezugs- **und** einzige gefuehrte Waffe | `Ironeye's Bow` (`wep_type` 51), dito |
| Datenabzug | `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`, `meta.extract_version` 11, `meta.data_version` 10350000, 2076 Effekte, 1793 Waffen — **nur gelesen** | derselbe |
| Bestand | Spielstand des App Designers, **309** besessene Kopien, **845** Effektrollen | derselbe |
| Bedingungen | keine als erfuellt erklaert (`declared` leer) | dito |
| Aufbau | **ein** Relikt je Slotgruppe, Slot 0, kein gehaltener Slot | dito |
| Zielrichtung / Gewichtung | `max_damage`, `EVEN_WEIGHTING` | dito |
| Gerechnet mit | `explain.reasons` selbst, nicht mit einer Nachbildung | dito |
| Codestand | `fd9f2bc`; `model.py`, `inventory.py`, `effecttext.py` und das ganze `advisor/`-Paket sind byteweise `fd9f2bc` (einzeln mit `git diff --quiet` geprueft) — im Arbeitsbaum weichen nur `advisorbar.py` und `app.py` ab (T-083), und keines davon wird hier importiert | dito |
| stumme Effektzeilen | **426** von 845 | **434** von 845 |

Messskripte im Scratchpad, auftragsgemaess nicht im Repo; das Rezept steht in
Prosa in §1.2. **Kein Fenster gestartet, kein Bildnachweis** (NH-002).

*(Nachtrag am Ende desselben Tages, ehrlichkeitshalber: waehrend dieser
Vorgabe hat ein `developer` den Docstring von `explain.not_counted` nach
AD-026 ersetzt — die Datei weicht seitdem von `fd9f2bc` ab. Die Aenderung ist
**ausschliesslich Docstring** (9 Zeilen ein, 4 aus, alle innerhalb der
Zeichenkette), aendert also keinen der Zahlen oben. Zum Zeitpunkt der Messung
war die Datei byteweise `fd9f2bc`.)*

---

### 1. Fuellung (c) trifft nur noch dort, wo das Programm die Armaturenfrage wirklich beantwortet hat

#### 1.1 Der Befund — und er ist groesser als die Meldung

Der `architect` meldet (T-085 §2d): von den 46 Zeilen, die AK-167/168 in
Umgebung A von (b) nach (c) verschieben, haengen **28 an
`wepTypeTriggerCount`**, einem Feld, das `satisfied_by_weapon` nicht
beantworten kann — *"wechsle die Waffe"* loest sie nicht.

**Nachgezaehlt, in beiden Umgebungen: die 28 stimmen. Sie zerfallen aber in
zwei Haelften, die nicht dasselbe Problem haben.**

| Zeilen mit unerfuellter Armaturenschranke, Fuellung (c) nach AK-167/168 | **A** | **B** |
|---|---|---|
| nur `triggerOnWepType` unerfuellt — echte Typschranke, Hebel vorhanden | 18 | 19 |
| `wepTypeTrigger` **und** `wepTypeTriggerCount` unerfuellt — z. B. `Improved Attack Power with 3+ Bows Equipped`; der Typ ist pruefbar und unerfuellt, der Effektname nennt die Anzahl selbst | 8 | 6 |
| **nur `wepTypeTriggerCount` unerfuellt** | **20** | **22** |
| `startSwordArtsId` — der Effekt tauscht die Waffenkunst der passenden Armatur | 12 | 0 |
| **Summe Fuellung (c)** | **58** | **47** |

Die 28 des `architect` sind die zweite plus die dritte Zeile (8 + 20 = 28 in
A, 6 + 22 = 28 in B — in beiden Umgebungen dieselbe Summe aus einer anderen
Mischung). **Nur die dritte Zeile ist das Problem**, und sie ist schlimmer,
als die Meldung sagt. Aufgeschluesselt nach dem Wert, den
`wepTypeTriggerCount` traegt:

| Wert | A: Zeilen / verschiedene Effekte | B: Zeilen / verschiedene Effekte | wie die Effekte heissen |
|---|---|---|---|
| 256 | 9 / 6 | 9 / 6 | `Crimsonburst Crystal Tear in possession at start of expedition`, `Stonesword Key in possession …` |
| 512 | 9 / 6 | 9 / 6 | `Fire Pots in possession at start of expedition`, `Starlight Shards in possession …` |
| 1024 | 1 / 1 | 1 / 1 | `Poisonbone Darts in possession at start of expedition` |
| **3** | **1 / 1** | **3 / 2** | `Improved Attack Power with 3+ Daggers Equipped` |

**19 der 20 Zeilen in A und 19 der 22 in B gehoeren zu Effekten, die mit
Armaturen ueberhaupt nichts zu tun haben.** Sie geben dem Spieler einen
Gegenstand zu Beginn der Expedition. Die heutige Fuellung (c) wuerde ihnen
*"it depends on the armaments you carry"* anschreiben — das ist nicht vage,
das ist **falsch**, und es ist derselbe A7-Bruch, den AK-167/168 schliessen
sollten, nur eine Ebene tiefer.

**Belegt, ohne eine Vermutung ueber die Spieldateien** (AK-140/AK-157): im
Abzug tragen **alle 51** `wepTypeTriggerCount`-Effekte mit einem anderen Wert
als 3 **zugleich `startGoodsId`**, und **alle 31** mit dem Wert 3 tragen es
**nicht** — eine saubere Trennung, 82 von 82. `GATE_FIELDS` beschriftet
`startGoodsId` selbst mit *"grants an item at the start of an expedition"*.
Was 256, 512, 768 und 1024 in diesem Feld **bedeuten**, sagt der Abzug nicht,
und dieser Nachtrag behauptet es auch nicht.

**Genau ein Effekt im ganzen Abzug** (2076 Effekte) ist eine echte
Waffen*anzahl* ohne pruefbares Typfeld: `Improved Attack Power with 3+
Daggers Equipped` (7080000). Die uebrigen 30 Effekte mit Wert 3 tragen
zusaetzlich `wepTypeTrigger`, das pruefbar ist.

**Der latente zweite Fall, unabhaengig nachgemessen:** von den 144
`triggerOnWepType`-Effekten tragen **72** einen Wert, den keine der 1793
Waffen des Abzugs als `wep_type` fuehrt (**70** auf 256, **2** auf 512; der
Vorrat umfasst 34 Waffentypen). Kein Armaturenwechsel erfuellt sie je. Auf
diesem Spielstand ist **keiner** davon besessen (0 von 314 entdoppelten
besessenen Effekt-Ids, 0 Zeilen in beiden Umgebungen). `wepTypeTrigger` hat
diesen Fall nicht (0 von 30).

#### 1.2 Die Entscheidung

**Fuellung (c) trifft nur noch zu, wenn das Programm die Armaturenfrage
gestellt und mit Nein beantwortet bekommen hat.** Das sind genau zwei Faelle:

1. Der Effekt traegt ein Feld aus `model.WEAPON_TYPE_GATES` —
   `triggerOnWepType` oder `wepTypeTrigger` —, `model.satisfied_by_weapon`
   ist dafuer gegen die gefuehrten Waffentypen **falsch**, **und** der
   verlangte Wert ist der `wep_type` mindestens einer Waffe des Datenabzugs.
2. Der Effekt traegt `startSwordArtsId`. Er tauscht die Waffenkunst der
   passenden Armatur; dass es an der Armatur haengt, steht in seinem eigenen
   Namen (`Changes compatible armament's skill to …`, 20 von 20 Effekten des
   Abzugs).

**`wepTypeTriggerCount` allein schickt keine Zeile mehr nach (c).** Eine
Zeile, deren einzige unerfuellte Armaturenschranke dieses Feld ist, faellt
auf **(b)** — sie steht als `Situational` mit `live == False` im Build, also
genau dort, wo (b) hingehoert, und bekommt

> `{effect name}: only applies under a condition, so no number here.`

Das ist wahr, deckungsgleich mit der Liste 4.9b, in der derselbe Effekt
steht, und es verspricht keinen Hebel. **Die Klassenfrage wird damit nicht
wieder aufgemacht** (AD-026 steht): der Effekt bleibt konditional, bleibt in
`not_counted`, behaelt seinen Schalter. Es geht ausschliesslich um den
**Wortlaut der Zeile**.

**Das Rezept, mit dem die Zahlen unten entstanden sind** (Umgebung §0,
gerechnet mit `explain.reasons`, nicht nachgebaut):

1. `data = json.loads(paths.snapshot_path().read_text())`,
   `model.configure(data)`, `owned = inventory.load(data)`.
2. `ctx = types.GoalContext(data, hero, level=15,
   reference=ReferenceArmament(Startwaffe des Nightfarers, tier=1,
   slot_index=0), weighting=goals.DEFAULT_WEIGHTING,
   weapons_held=(dieselbe Waffe,))`.
3. Je besessener Kopie: `problem = SlotProblem(slots=(Slot(0, colour, deep),),
   held=())`, `base = evaluate(problem, (), ctx)`,
   `built = evaluate(problem, (cand,), ctx)`,
   `groups = explain.reasons(problem, (cand,), base, built, ctx,
   goals.GOALS["max_damage"])`.
4. Gezaehlt werden die `ReasonLine`, die weder `is_curse` noch
   `silence == CARRIES_A_FIGURE` sind. Die Zeile wird ueber den Namensanfang
   `f"{name}: "` ihrem Effekt zugeordnet.
5. Fuellung (c) wird je Zeile nach der Regel aus 1.2 neu bestimmt; (a), (a2)
   und (e) gewinnen weiterhin **vor** (c) (AK-167).

#### 1.3 Die Zahlen nach der neuen Regel

| Fuellung | A gebaut | A nach AK-167/168 | **A nach AK-177/178** | B gebaut | B nach AK-167/168 | **B nach AK-177/178** |
|---|---|---|---|---|---|---|
| (a) anderer Nightfarer | 150 | 150 | **150** | 159 | 159 | **159** |
| (a2) anderswo gezaehlt | 0 | 0 | **0** | 0 | 0 | **0** |
| (b) Bedingung | 170 | 124 | **144** | 174 | 127 | **149** |
| (c) Armaturen | 13 | 58 | **38** | 0 | 47 | **25** |
| (d) Rest | 93 | 94 | **94** | 101 | 101 | **101** |
| (e) nicht im Datensatz | 0 | 0 | **0** | 0 | 0 | **0** |
| **Summe** | **426** | **426** | **426** | **434** | **434** | **434** |

**Zwei Unterschiede zwischen A und B sind erklaerungsbeduerftig und
erklaert:**

- **(c) ist in B um 13 kleiner als in A.** Das sind die zwoelf
  `startSwordArtsId`-Zeilen plus eine: fuer Ironeye sagt
  `effecttext.works_for` bei allen zehn besessenen
  `Changes compatible armament's skill to …`-Effekten **Nein**, sie bekommen
  also Fuellung (a) und erreichen (c) gar nicht. In A gilt das nicht.
- **Die Verschiebung ist in beiden Umgebungen dieselbe Groesse:** 20 Zeilen
  in A, 22 in B wandern von (c) nach (b). Die Regel haengt nicht am
  Nightfarer und nicht an der Waffengattung.

**Der Preis, ausdruecklich benannt** (A12: was diese Zusicherung nicht
deckt):

- **1 Zeile in A und 3 in B verlieren die konkrete Auskunft**, obwohl sie
  wirklich an einer Waffenanzahl haengen (`Improved Attack Power with 3+
  Daggers Equipped`, in B zusaetzlich `… with 3+ Bows Equipped`). Sie
  bekommen (b) statt (c). **Der Spieler verliert dabei nichts**, weil der
  Effektname selbst *"with 3+ Daggers Equipped"* sagt — die Auskunft steht
  bereits vor dem Doppelpunkt.
- **Wer einer (c)-Zeile folgt und die Waffe anlegt, kann auf (b) landen.**
  Umgebung B zeigt es: `Improved Attack Power with 3+ Bows Equipped` bekommt
  fuer Wylder (c), fuer den bogenfuehrenden Ironeye aber (b), weil dann nur
  noch die Anzahl fehlt. Das ist kein Widerspruch und keine Luege — die
  zweite Zeile ist nur schwaecher als die erste. Eine Fuellung, die *"you
  need three of them"* sagt, waere eine Aussage ueber die Spieldateien, die
  der Abzug fuer den Wert 3 nicht hergibt; sie wird deshalb **nicht**
  geschrieben.
- **Nicht gemessen:** wie oft eine dieser Zeilen in einem **vollen Lauf** des
  Beraters wirklich vor dem Spieler steht. Der `architect` hat fuer die
  benachbarte Frage 1 von 176 Laeufen gemessen (T-085 §2c); die Zahlen hier
  beschreiben die **Kandidatenmenge** des Pickers, nicht den Vorschlag.

#### 1.4 Verworfene Wege, und warum

- **Eine siebte Fuellung, die die Anzahl benennt** (der erste Weg des
  Auftrags). **Verworfen, und die Messung ist der Grund:** ein Satz wie
  *"you need several of that weapon equipped"* waere auf 19 der 20 Zeilen
  **neu falsch** — `Stonesword Key in possession at start of expedition` hat
  keine Waffenanzahl. Der Weg setzt voraus, dass der Feldname sagt, was der
  Effekt tut, und genau das tut er hier nicht. Zusaetzlich haette er AK-169
  aufgemacht und die Zahl der Fuellungen um eine erhoeht, ohne einen Fall
  sauber zu treffen.
- **(c) vager umformulieren, sodass ein Satz beide Faelle traegt** (der
  zweite Weg). **Verworfen:** kein Satz ueber Armaturen ist fuer
  `Fire Pots in possession at start of expedition` wahr, auch kein vager. Der
  Weg haette ausserdem den 26 Zeilen in A (18 + 8) die konkrete Auskunft
  genommen, bei denen der Hebel wirklich existiert — er zahlt den Preis
  zweimal und behebt den Fehler nicht.
- **Die 28 nach (d)** (der dritte Weg). **Verworfen aus zwei Gruenden.**
  Erstens ist er so nicht herstellbar: (d) ist die letzte Fuellung, und diese
  Zeilen sind `Situational live == False`, fallen also auf (b), sobald (c)
  sie nicht mehr faengt — nach (d) kaeme man nur mit einer zusaetzlichen
  Ausnahme. Zweitens waere (d) (*"no number here shows what this adds"*) die
  schwaechere Auskunft: (b) sagt zutreffend, dass eine Bedingung im Weg
  steht, und stimmt mit der Liste 4.9b ueberein, in der derselbe Effekt
  aufgefuehrt ist. Ein Effekt, der in der Liste unter *"only apply under a
  condition"* steht und in der Zeile *"no number here shows what this adds"*
  liest, laesst den Spieler zwei Antworten auf eine Frage sehen.
- **8 der 28 in (c) belassen** ist keine Ausnahme, sondern folgt aus der
  Regel: sie tragen `wepTypeTrigger`, das pruefbar und unerfuellt ist. Fuer
  sie ist *"it depends on the armaments you carry"* wahr.
- **`wepTypeTriggerCount` auswertbar machen** ist ausdruecklich nicht Teil
  dieser Vorgabe (Scope T-086, und `ARCHITECTURE.md` fuehrt es unter
  „Bewusst nicht getan"). Wird die Zahl der gefuehrten Waffen eines Typs
  eines Tages bekannt, aendert sich diese Vorgabe; bis dahin beschreibt sie,
  was das Programm **weiss**.

#### 1.5 Akzeptanzkriterien

- **AK-177** *(der Test von (c) fragt, was das Programm beantwortet hat.)*
  **Praezisiert AK-168, ersetzt es nicht.** Fuellung (c) trifft genau dann
  zu, wenn (1) der Effekt ein Feld aus `model.WEAPON_TYPE_GATES` traegt,
  `model.satisfied_by_weapon` dafuer gegen die gefuehrten Waffentypen falsch
  ist **und** der verlangte Wert der `wep_type` mindestens einer Waffe des
  Datenabzugs ist, **oder** (2) der Effekt `startSwordArtsId` traegt.
  Pruefweg: ueber den Bestand zaehlen, mit `explain.reasons` selbst; in
  Umgebung §0 ergibt (c) **38** (A) bzw. **25** (B).
  *Rot-vorher:* eine Umsetzung nach dem Wortlaut von AK-168 — also
  `_ARMAMENT_GATES` unveraendert als Trigger von (c) — gibt in Umgebung A
  **20** Zeilen und in B **22** Zeilen
  `… : it depends on the armaments you carry, so no number here.`, von denen
  je **19** zu Effekten gehoeren, die einen **Gegenstand** zu Beginn der
  Expedition geben (`Stonesword Key in possession at start of expedition`)
  und keine Armatur verlangen.

- **AK-178** *(`wepTypeTriggerCount` allein nennt keinen Hebel.)* Traegt eine
  stumme Zeile als einzige unerfuellte Armaturenschranke
  `wepTypeTriggerCount`, so lautet sie
  `{effect name}: only applies under a condition, so no number here.`
  (Fuellung (b), Wortlaut unveraendert) und enthaelt **nirgends** die
  Zeichenfolge `armaments you carry`. Pruefweg: ueber den Bestand alle
  stummen Zeilen erzeugen und die Teilmenge pruefen; in Umgebung §0 sind das
  **20** Zeilen (A) bzw. **22** (B), und (b) waechst von 124 auf **144** (A)
  bzw. von 127 auf **149** (B).
  *Rot-vorher:* dieselbe Umsetzung wie bei AK-177 — die Zeile
  `Stonesword Key in possession at start of expedition: it depends on the
  armaments you carry, so no number here.` ist der einzelne Fall, an dem es
  sichtbar wird.

- **AK-179** *(eine Schranke auf einen Waffentyp, den es nicht gibt, ist kein
  Armaturenfall.)* Eine Zeile bekommt Fuellung (c) nur, wenn der von der
  Schranke verlangte Wert der `wep_type` mindestens einer Waffe des
  Datenabzugs ist. Trifft das nicht zu, faellt sie auf (b). Pruefweg: den
  Wertevorrat `{w["wep_type"] for w in data["weapons"]}` bilden (in Umgebung
  §0: **34** Werte ueber 1793 Waffen) und jede (c)-Zeile dagegen halten.
  **Dieses Kriterium bewegt auf dem heutigen Spielstand null Zeilen** (0 von
  426 bzw. 0 von 434) — es bewacht einen Fall, der im Abzug existiert und im
  Bestand nicht: **72 von 144** `triggerOnWepType`-Effekten tragen 256 oder
  512, was kein Waffentyp ist.
  *Rot-vorher:* eine Umsetzung ohne diese Bedingung schreibt, sobald der
  Spieler eine Kopie mit einem dieser 72 Effekte findet,
  *"it depends on the armaments you carry"* an eine Schranke, die **keine
  Waffe des Spiels** erfuellen kann — nachstellbar, indem man dem Test einen
  Effekt mit `triggerOnWepType = 256` unterschiebt.

- **AK-180** *(Partition, Zahlen fortgeschrieben.)* **Ersetzt die Zahlenreihe
  in AK-169; dessen Regel und Pruefweg bleiben unveraendert gueltig.** Die
  sechs Fuellungen sind eine Partition der stummen Effektzeilen: jede stumme
  Zeile traegt genau eine, und die Summe der sechs ist die Zahl der stummen
  Zeilen. In Umgebung §0 ergibt das **150 / 0 / 144 / 38 / 94 / 0 = 426**
  (A) und **159 / 0 / 149 / 25 / 101 / 0 = 434** (B), jeweils in der
  Reihenfolge (a) / (a2) / (b) / (c) / (d) / (e).
  *Rot-vorher:* die Zahlenreihe aus AK-169 (150 / 0 / 124 / 58 / 94 / 0)
  summiert sich zwar ebenfalls auf 426, verteilt aber 20 Zeilen auf die
  falsche Fuellung; die Summe allein ist deshalb **kein** ausreichender
  Waechter.

**Was dieser Nachtrag ausdruecklich nicht anfasst:** die Liste 4.9b und
`not_counted` bleiben `Build.situational, live == False` (AK-142
unveraendert, AD-010 und AD-026 unveraendert). Die Wortlaute aller sechs
Fuellungen bleiben Buchstabe fuer Buchstabe stehen. AK-154 gilt fort mit der
Praezisierung aus dem T-084-Abschnitt.

---

### 2. §6 des T-080-Abschnitts — welche Zahl zu welcher Lesart gehoert

Der `architect` meldet (T-085 §6.3), dass der Satz *„170 der 426 stummen
Effekte sind konditional …"* neben einer Tabelle steht, die an derselben
Stelle 124 nennt, und sich deshalb wie eine Aussage ueber diese Tabelle
liest. Der Satz ist **richtig**, aber er beschreibt die **Liste**, nicht die
**Zeile**:

- **170** ist die Zahl der stummen Zeilen, deren Effekt in
  `Build.situational` mit `live == False` steht — also derselben Menge, aus
  der die Liste 4.9b und `not_counted` gespeist werden. **Nachgemessen in
  Umgebung §0, unabhaengig von jeder Fuellungsreihenfolge: 170 (A), 174
  (B).** Diese Zahl aendert sich durch AK-167/168 und AK-177/178 **nicht**.
- **124** bzw. **144** ist die Zahl der Zeilen, die Fuellung (b)
  *bekommen*. Sie ist kleiner, weil (a), (a2) und (c) in der Reihenfolge
  nach AK-167 vorher zugreifen — sie nehmen die Zeile aus der **Fuellung**,
  nicht aus der **Liste**.

Der Satz in §6 ist deshalb **nicht korrigiert, sondern mit einem Nachtrag
angeschrieben** worden, der beide Zahlen ihrer Lesart zuordnet.

- **AK-181** *(jede Zahl im Fliesstext nennt ihre Lesart.)* Wo `UI_SPEC.md`
  eine Zahl ueber die stummen Effektzeilen nennt, steht dabei, ob sie die
  **Liste** (`Build.situational`, `live == False`) oder eine **Fuellung**
  (die Zeile im `Why`-Dialog) zaehlt. Die Messumgebung darf dabei auf den
  §0-Abschnitt des eigenen Nachtrags verweisen; sie darf nicht fehlen.
  Pruefweg: Volltextsuche nach `426` und `434` in dieser Datei, jede
  Fundstelle einer der beiden Lesarten zuordenbar.
  *Rot-vorher:* der Satz in §6 des T-080-Abschnitts vor diesem Nachtrag — wer
  ihn neben der Tabelle des T-084-Abschnitts liest, haelt 170 und 124 fuer
  zwei Messungen derselben Groesse und eine davon fuer falsch.

---

### 3. Was dieser Nachtrag ausdruecklich **nicht** entscheidet

- **Ob `wepTypeTriggerCount` auswertbar gemacht wird.** Scope-Grenze des
  Auftrags; `ARCHITECTURE.md` fuehrt es unter „Bewusst nicht getan".
- **Was 256, 512, 768 und 1024 in den Waffenfeldern bedeuten.** Der Abzug
  sagt es nicht, und AK-140/AK-157 verbieten die Vermutung. Diese Vorgabe
  braucht die Antwort nicht: sie fragt, ob ein Wert im Waffentyp-Vorrat des
  Abzugs vorkommt, und das ist eine Nachschau, keine Deutung.
- **Die Beschriftungen in `model.GATE_FIELDS`**, die im Build planner unter
  `Conditional & situational` stehen. Dort steht heute *"needs several of
  that weapon equipped"* an 51 Effekten, die einen Gegenstand geben, und
  *"only with a matching weapon type"* an 72 Effekten mit einem Wert, den
  keine Waffe traegt. Das ist **eine andere Oberflaeche** als die Zeile im
  `Why`-Dialog und als Befund gemeldet
  (`docs/berichte/T-086-ui-ux-designer.md`), nicht hier entschieden.
- **Die vier Fragen an den App Designer** (F-B, F-C, F-F, F-G) und die
  dreizehn Streichvorschlaege je Tab. Unberuehrt.

---

## Schlechtester und bester Fall, und die Zahl ohne Waffe
## (ui-ux-designer, T-092) — 2026-09-07

**Grundlage:** `docs/tasks/T-092.md` · `GOAL.md` Nachtrag 07.09.2026 (A16 und
A17, woertlich zitiert im Auftrag) · `docs/state.md` vom 07.09.2026 · in
dieser Datei: §3.1, §3.2, §3.3, §3.4 und §4 des T-004-Abschnitts, §3.2/§3.3/
§3.4 des T-024-Abschnitts (Picker), §2 bis §6 des T-078-Abschnitts, §4 bis §6
des T-080-Abschnitts, §1 des T-084-Abschnitts (AK-162 bis AK-166), der ganze
T-086-Abschnitt (AK-177 bis AK-181). **Gelesen und gemessen gegen den Commit
`84623a4`**: `nrplanner/model.py`, `nrplanner/inventory.py`,
`nrplanner/damage.py`, `nrplanner/effecttext.py` und das ganze
`nrplanner/advisor/`-Paket sind byteweise `84623a4` (je Datei mit
`git diff --quiet` geprueft). Im Arbeitsbaum weichen nur
`nrplanner/advisorbar.py` und `tests/test_advisor_bar.py` ab (T-091 laeuft
parallel); `advisorbar.py` wurde **gelesen, nicht importiert** — jede Zahl
unten stammt aus dem `advisor/`-Paket und ist von T-091 unberuehrt.

**Was dieser Nachtrag ist:** die Vorgabe fuer zwei Nutzerentscheidungen, die
noch nicht gebaut sind (A16, A17), plus **eine** wieder aufgemachte Vorgabe
aus T-086 (Fuellung (c), §4 unten) — der Auftrag erlaubt genau diese eine.

Neue Akzeptanzkriterien: **AK-182 bis AK-194**.

---

### 0. Messumgebung (L-009) — woran die Zahlen unten gemessen sind

Alle Zahlen sind **mit den Produktionsfunktionen selbst erzeugt**
(`model.compute` ueber `advisor.evaluate.evaluate`, `explain.reasons`,
`explain.curses_without_a_figure`, `explain.effects_without_a_figure`,
`explain.not_counted`, `goals.GOALS[...].score`) — keine Nachbildung. Kein
Fenster gestartet, kein Bildnachweis (NH-002). Messskripte im Scratchpad,
auftragsgemaess nicht im Repo; das Rezept steht in Prosa unter jeder Tabelle.

| | **Umgebung A** | **Umgebung B** |
|---|---|---|
| Nightfarer | Wylder, Stufe 15 | Ironeye, Stufe 15 |
| Armatur | `Wylder's Greatsword` (`wep_type` 5), Bezugs- und einzige gefuehrte Waffe — ausser wo ausdruecklich „ohne Bezugswaffe" steht | `Ironeye's Bow` (`wep_type` 51), dito |
| Datenabzug | `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`, `meta.extract_version` 11, `meta.data_version` 10350000, 2076 Effekte, 1793 Waffen, 849 Relikte — **nur gelesen** | derselbe |
| Bestand | Spielstand des App Designers, **309** besessene Kopien mit Handle, **845** Effektrollen, **112** Fluchrollen | derselbe |
| Bedingungen | keine vom Spieler erklaert (`declared` leer), ausser wo eine Lesart sie setzt | dito |
| Aufbau | **ein** Relikt je Slotgruppe, Slot 0, kein gehaltener Slot | dito |
| Zielrichtung / Gewichtung | `max_damage`, `EVEN_WEIGHTING`, ausser wo `min_damage_taken` dabeisteht | dito |
| Codestand | `84623a4`, `advisor/`-Paket byteweise sauber | dito |
| stumme **Effekt**zeilen (Lesart „Fuellung", AK-181) | **426** von 845 | **434** von 845 |
| stumme **Fluch**zeilen | **67** von 142 gezeichneten Fluchzeilen | **67** von 142 |

**Gegenprobe, dass dieses Rezept dasselbe misst wie T-086:** die Umgebung
reproduziert AK-180 Zahl fuer Zahl — Fuellung (b) **144** (A) / **149** (B),
Fuellung (c) **38** (A) / **25** (B), stumme Effektzeilen **426** / **434**.
Die Zahlen unten sind also mit den T-086-Zahlen vergleichbar und nicht mit
einer zweiten Rechnung erzeugt.

**Der Fluch-Zensus, den A16 zitiert — nachgezaehlt, und er ist groesser als
die Meldung.** Rezept: ueber `inventory.load(data).relics`, Feld `curse_ids`
je Kopie, gegen `model.is_conditional(effect, wep_type)`.

| | Zahl | Lesart |
|---|---|---|
| verschiedene Fluch-Ids auf den Relikten des Spielstands | **24** | Ids, nicht Zeilen — das ist die Zahl aus `GOAL.md` A16 |
| **Fluchrollen** auf den 309 Kopien | **112** | Rollen; eine Kopie kann mehrere tragen |
| davon **konditional** | **27 Rollen** auf **23 Kopien**, **7** verschiedene Ids | die sieben Namen aus A16, ausgezaehlt |
| gezeichnete Fluchzeilen heute | **142** | Zeilen; ein Fluch, der zwei Groessen bewegt, ist zwei Zeilen (T-078 §2) |

**Das ist der erste Befund dieses Nachtrags und er berichtigt eine Annahme des
Auftrags:** die „7 Flueche" sind **7 Ids / 27 Rollen / 23 betroffene Kopien**,
nicht 7 Zeilen. Beide Lesarten sind wahr, sie zaehlen nur Verschiedenes
(AK-181 gilt hier fort).

---

### 1. Punkt 1 — das Bedienelement fuer die zwei Lesarten (A16)

#### 1.1 Entscheidung

**Ein eigenes Bedienelement, keine Erweiterung der Zielwahl.** Eine zweite
`QComboBox` mit genau zwei Eintraegen, **zwischen** der Zielwahl und
`Optimize`:

```
ADVISOR  [ Maximise damage v ] [ Worst case v ]  [ Optimize ]   <status …>   [ Apply all ] [ Why ] [ Clear ]
```

- Eintraege, in dieser Reihenfolge: **`Worst case`**, **`Best case`**.
  Voreinstellung ist **`Worst case`** — die Zahl, auf die man sich verlassen
  kann, ist die, die ein Spieler ungefragt bekommen soll; A16 nennt sie so.
- `setSizeAdjustPolicy(AdjustToContents)`, `setMaximumWidth(140)`.
- Tooltip (Englisch, A8), **der einzige Ort, an dem beide Lesarten erklaert
  stehen**:

  > `Which conditions this ranking assumes. Worst case: every conditional curse counts, every conditional buff does not. Best case: the other way round. Conditions you have declared yourself are used as declared either way.`

- **Es ist kein Aktionsknopf.** AK-07 (`nie mehr als drei gleichzeitig
  sichtbar`) zaehlt die Knoepfe rechts, die etwas **tun** — `Apply all`,
  `Undo apply`, `Why`, `Clear`. Dies ist eine Einstellung links, in derselben
  Klasse wie die Zielwahl. **Grenze, damit die Ausnahme keine Tuer ist:
  links von `Optimize` stehen hoechstens zwei Einstellungen.** Eine dritte
  (etwa OF-3, die Gewichtung) verlangt eine neue Layoutentscheidung und nicht
  ein weiteres Kaestchen.

#### 1.2 Warum nicht in die Zielwahl

Vier Eintraege in einer Liste (`Maximise damage (worst case)` …) waeren
billiger. Verworfen, aus drei Gruenden:

1. **Es ist ein Kreuzprodukt.** Zwei Ziele mal zwei Lesarten sind vier
   Eintraege, ein drittes Ziel macht sechs. `advisor/goals.py` sagt im
   Modul-Docstring ausdruecklich zu, dass ein drittes Ziel *"one function and
   one registry entry"* ist; eine Kreuzprodukt-Liste bricht diese Zusage in
   der Oberflaeche, ohne sie im Code zu brechen — der teuerste Ort dafuer.
2. **Die Zielwahl ist im Picker dieselbe Einstellung wie in der Leiste**
   (T-024 §3.4, ausdruecklich: *"Zwei Zielwahlen waeren der vierte
   widerspruechliche Ort"*). Die Kartenspalte des Pickers zeigt **beide**
   Zielrichtungen gleichzeitig (T-024 §3.3, AD-018.2) — eine Lesart, die in
   der Zielwahl steckt, waere fuer die zweite Spalte nicht gesetzt. Die
   Lesart gilt fuer **beide** Zahlen einer Karte, die Zielwahl fuer keine.
3. A16 sagt „**zwei Lesarten derselben Rechnung**". Ein Listeneintrag
   `Maximise damage (worst case)` behauptet eine andere Zielrichtung.

#### 1.3 Warum diese Woerter

Der Auftrag warnt zu Recht, dass `Worst case` / `Best case` die Frage des
Spielers („worauf kann ich mich verlassen?") nicht beantwortet. **Die Antwort
gehoert aber nicht in die Beschriftung, sondern neben die Zahl** — und dort
steht sie: im Tooltip (1.1) und im Kopf des Vorschlagsblocks und des
`Why`-Dialogs (§2). Die Beschriftung hat eine andere Pflicht: **sie muss
dasselbe Wort tragen wie alles andere im Projekt.** `GOAL.md` A16, der
Auftrag, die Berichte und die kuenftigen Testnamen sagen „schlechtester Fall /
bester Fall". Eine Leiste, die dazu `Safe` / `Risky` sagt, gibt einer Sache
zwei Namen — die Fehlerklasse, die dieses Projekt unter D-11 fuehrt, nur in
Woertern statt in Zahlen.

Verworfen und warum:

- **`Safe` / `Risky`** — die Woerter des Nutzers, und die kuerzesten. Sie
  benennen aber die **Haltung des Spielers**, nicht die **Annahme der
  Rechnung**; „safe" neben `Maximise damage` liest sich als „sicherer
  Schaden". Sie kommen im Tooltip vor, nicht auf dem Element.
- **Ein Kaestchen `Assume the worst`** — ein Haken nennt genau eine Lesart;
  die andere haette dann keinen Namen, und der ungehakte Zustand sagt nicht,
  was gilt. A16 verlangt, dass **jede** Zahl sagt, welche Lesart gerade gilt.
- **Zwei einrastende Knoepfe (`[ Worst | Best ]`)** — ein Schalter waere
  schoener zu bedienen, kostet aber die Breite beider Beschriftungen
  gleichzeitig; die Combobox kostet die Breite der laengeren. Bei einer
  Statuszeile von 158 px ist das der Unterschied, der entscheidet.
- **`Assume the worst` / `Assume the best`** — selbsterklaerend, aber 16
  Zeichen statt 10, und sie fuehren ein drittes Vokabular ein.

#### 1.4 Der Preis in Breite — Rangaussage, keine Pixelzusage

Eine Pixelbreite ist hier **nicht messbar**: unter `QT_QPA_PLATFORM=offscreen`
liefert dieser Rechner fuer jede Zeichenkette exakt 12,0 px je Zeichen
(T-084 §0), und ein laufendes Fenster startet dieser Auftrag nicht. Deshalb
eine **Rangaussage** gegen Zeichenketten, die diese Datei bereits akzeptiert
hat:

| Zeichenkette | Zeichen |
|---|---|
| `Minimise damage taken` (laengster Eintrag der Zielwahl, `maximumWidth(200)`) | 21 |
| `Worst case` (laengster Eintrag der Lesart) | 10 |
| `Best case` | 9 |

Die neue Combobox traegt also rund **die Haelfte** des Textes der bestehenden,
plus einmal Rahmen und Pfeil. **Das ist ein Rang und keine
Sichtbarkeitszusage** — was davon auf dem Schirm wird, entscheidet AK-194 am
laufenden Fenster.

---

### 2. Punkt 2 — was die Zahl ueber sich sagt (A16, A12)

#### 2.1 Vier Orte, je einmal — und die Statuszeile ist keiner davon

Die Lesart wird **genau viermal** genannt, nie je Zeile und nie je Slot
(dieselbe Ueberlegung wie AK-22 und AK-50):

1. **Das Bedienelement selbst** (§1). Es steht dauerhaft im Blick und sagt,
   was gerade gilt.
2. **Der Kopf des Vorschlagsblocks** auf der Slotkarte (§3.2 des
   T-004-Abschnitts): `SUGGESTED — MAXIMISE DAMAGE` wird zu
   **`SUGGESTED — MAXIMISE DAMAGE, WORST CASE`**. Die Begruendung steht schon
   dort: der Kopf nennt das Ziel, *"damit der Block auch nach dem Wegscrollen
   der Leiste fuer sich steht"* — fuer die Lesart gilt derselbe Satz
   woertlich. Der Kopf bricht um (4.14), er wird nicht gekuerzt.
3. **Der `Why`-Dialog**: Titel `Why this build — Maximise damage, worst case`
   und im Kopf (§3.4 Punkt 1) eine eigene Zeile, je nach Lesart eine von
   diesen beiden:

   > `Worst case: every conditional curse counts, every conditional buff does not. Conditions you have declared yourself are used as declared.`
   >
   > `Best case: every conditional buff counts, every conditional curse does not. Conditions you have declared yourself are used as declared.`

4. **Die Zusammenfassungszeile des Relic Pickers** (Zeile 3 in T-024 §3.2,
   die schon die Bezugsgroesse nennt) bekommt den Zusatz
   **`  ·  worst case`** bzw. **`  ·  best case`**. Der Picker bekommt
   **kein zweites Bedienelement** — dieselbe Regel wie fuer die Zielwahl in
   T-024 §3.4. Grund, und er ist der staerkere: die Karte zeigt **beide**
   Zielrichtungen; eine Lesart gilt fuer beide Zahlen, also gehoert sie in
   die Zeile ueber dem Raster und nicht auf 300 Karten.

**Die Statuszeile der Leiste traegt die Lesart nicht.** Zwei Gruende, und der
zweite ist der wichtigere: erstens steht das Bedienelement daneben und sagt
dasselbe; zweitens haette der Zusatz `, worst case` in 4.3, 4.4, 4.6, 4.9 und
4.11 zu stehen — fuenf Zeilen laenger in einer Zeile, die bei 1320 px
**158 px** hat (gemessen in T-089, Plattform `windows`). Die Lesart wird dort
genannt, wo eine **Zahl** ohne die Leiste im Blick gelesen wird; die
Statuszeile ist ein Zustandsbericht, keine Zahl.

#### 2.2 Umschalten verhaelt sich wie ein Zielwechsel — kein neuer Zustand

`advisorbar._goal_chosen` sagt heute: *"A direction is a different question,
so the old answer goes"*, und ruft `the_build_changed()`. **Die Lesart tut
genau dasselbe**: ein lebender Vorschlag wird verworfen (die Zeile geht auf
4.1 `Nothing suggested yet.` zurueck), ein laufender Lauf wird abgebrochen und
zeigt 4.7. **Kein neuer Zustand in §4, kein neuer Wortlaut, keine neue Zeile.**

Das ist zugleich die Antwort auf die Auflage des Auftrags zu **D-11 (zwei
Zahlen fuer dieselbe Sache):** es stehen **nie zwei Zahlen nebeneinander**.
Zu jedem Zeitpunkt lebt hoechstens ein Ergebnis, und es gehoert zu genau der
Lesart, die das Bedienelement zeigt. Auseinanderlaufen kann nichts, weil es
nichts Zweites gibt. Gestuetzt wird das im Bestand: `declared` ist Teil des
Anfrage-Schluessels (`advisor/run.py:269`), eine Lesart kann also keinen alten
Wert unter neuem Namen ausliefern.

**Nicht gebaut wird ein Nebeneinander beider Zahlen.** Es waere die
naheliegende Bequemlichkeit („beide sehen") und genau die Fehlerklasse aus
D-11/QA-082; ausserdem verlangte es eine zweite Rechnung je Kandidat, deren
Kosten (S11, Budget noch offen) niemand gemessen hat.

#### 2.3 Was die Lesart setzt — und was sie nie setzt

**Sie setzt Bedingungen, nie Zahlen** (A16, AD-023, OF-13). Der Weg ist der
gebaute: `model.compute(declared=…)` ueber `GoalContext.declared`, das Feld,
mit dem der Spieler heute von Hand eine Bedingung erklaert.

- **Schlechtester Fall:** jede **konditionale Fluchwirkung** der betrachteten
  Kopien gilt als erfuellt; konditionale Buffwirkungen bleiben, wie sie heute
  sind (aussen vor).
- **Bester Fall:** jede **konditionale Buffwirkung** gilt als erfuellt;
  konditionale Fluchwirkungen bleiben aussen vor.
- **Die Erklaerungen des Spielers gewinnen ueber beide.** Hat der Spieler eine
  Bedingung selbst erklaert, gilt seine Angabe — die Lesart ist eine
  **Voreinstellung fuer die Bedingungen, die er nicht beantwortet hat**. Alles
  andere waere eine Annahme gegen ein Wissen (A7), und die Zahl wuerde vom
  Statblatt daneben abweichen, ohne dass jemand es sagt (QA-001-Klasse).
- **Keine Gewichte werden angefasst.** `Weighting` bleibt `EVEN_WEIGHTING`,
  `weights` bleibt unberuehrt. Eine Lesart, die ein Gewicht aendert, ist
  gebaut falsch.

#### 2.4 Wie sich die Listen und Zaehlzeilen unter jeder Lesart verhalten

**Gemessen** (Umgebung A, Rezept: je besessene Kopie ein Ein-Relikt-Problem,
`explain.reasons` / `explain.not_counted` /
`explain.curses_without_a_figure` / `explain.effects_without_a_figure`
selbst, Summe ueber alle 309 Kopien):

| | heute | schlechtester Fall | bester Fall |
|---|---|---|---|
| `not_counted` (speist 4.9b) | **197** | **170** | **27** |
| `curses_without_a_figure` (speist 4.9a) | **67** | **42** | **67** |
| `effects_without_a_figure` | **426** | **426** | **323** |
| gezeichnete Zeilen insgesamt | 1164 | 1281 | 1354 |
| Fuellung (b) `only applies under a condition` | 144 | 144 | **0** |
| Fuellung (c) `armaments you carry` | 38 | 38 | 23 |

**Die Zahlen sagen genau das, was A16 verspricht, und sie sind
nachrechenbar:** `170 + 27 = 197`. Der schlechteste Fall nimmt aus
`not_counted` **genau** die 27 konditionalen Fluchrollen heraus und ruehrt die
Buffseite nicht an; der beste Fall nimmt **genau** die konditionalen
Buffrollen heraus und laesst die 27 Fluchrollen stehen. Jede Lesart bewegt
**eine** Seite. Nichts wird erfunden, nichts verschwindet: die Eintraege
wandern von einer Liste in eine Zeile mit Zahl.

**Daraus folgt fuer den Wortlaut: nichts.** 4.9a und 4.9b behalten ihre Saetze
Buchstabe fuer Buchstabe (AK-143 unveraendert), die Ueberschrift des
4.9b-Abschnitts im `Why`-Dialog bleibt, die Zaehlzeile aus T-078 §6 bleibt.
Es aendern sich **nur die Zahlen**, und sie bleiben in sich stimmig: ein
Fluch, der im schlechtesten Fall zaehlt, hat eine Zahl und steht deshalb
weder unter „was nicht gezaehlt wurde" noch unter `curses_without_a_figure`
— gemessen, nicht angenommen (67 → 42).

**AK-155 haelt in beiden Lesarten**: `{total} − {n}` ist weiterhin genau die
Zahl der stummen Zeilen, weil die Lesart Zeilen zwischen „mit Zahl" und
„stumm" verschiebt und keine erzeugt.

#### 2.5 Der Preis, ausdruecklich benannt: der schlechteste Fall ist laenger

**Gemessen, Umgebung A, dieselbe Rechnung.** Der Block zaehlt nach der
Director-Korrektur vom 06.09.: Zeilen mit Zahl plus alle Fluchzeilen plus die
Zaehlzeile; stumme Zeilen stehen nur im `Why`-Dialog.

| | heute | schlechtester Fall | bester Fall |
|---|---|---|---|
| laengste Slotgruppe im `Why`-Dialog | **14** Zeilen | **21** Zeilen | 15 |
| laengster Vorschlagsblock | **15** Zeilen | **22** Zeilen | 16 |
| meiste Fluchzeilen auf **einer** Kopie | 5 | **15** | 5 |

Grund: ein konditionaler Fluch, der stumm **eine** Zeile war
(`✦ {name}: no number here shows what this costs.`), wird als erfuellte
Bedingung zu **einer Zeile je bewegter Groesse** — die
Damage-Negation-Flueche bewegen acht Felder. Die 14 Zeilen aus **AK-160**
sind damit **nicht mehr der schlechteste Fall**; AK-160 bleibt als Messung
seiner Umgebung gueltig und wird durch AK-189 fortgeschrieben. **AK-161
(nach dem Einbau neu messen) gilt fuer beide Lesarten getrennt.**

---

### 3. Punkt 3 — der Satz zur fehlenden Waffe wird der Normalfall (A17)

#### 3.1 Entscheidung: `Goal.scope`, und der Satz beschreibt eine Absicht

Nach AD-025 entscheidet die Frage *„laesst sich der Satz schreiben, bevor der
Lauf bekannt ist?"*. Unter A17 rankt der Berater **immer** ohne Bezugswaffe —
nicht „in der Voreinstellung, mit Umschaltmoeglichkeit":

- A17s Abnahme (*„Die Rangfolge einer Zielrichtung aendert sich nicht, wenn
  eine andere Waffe gefuehrt wird"*) ist nur pruefbar, wenn sie **immer**
  gilt. Eine Umschaltung macht sie zu einer Aussage ueber eine Einstellung.
- Fuer eine Umschaltung ist in der Leiste kein Platz (§1.1: hoechstens zwei
  Einstellungen links).
- Das Statblatt und das Waffenpanel des Build planners bleiben unberuehrt —
  A16 sagt das fuer das Statblatt ausdruecklich, und fuer die Bezugswaffe gilt
  dasselbe: sie bleibt genau das, was sie heute im Waffenpanel ist.

Damit ist der Satz **vor jedem Lauf schreibbar** und wandert aus
`GoalScore.unknowns` in **`MAX_DAMAGE.scope`**. Und er wird umgeschrieben:
der heutige Wortlaut liest sich als Mangel („No armament selected — …"),
unter A17 beschreibt er eine Absicht.

**Neu, Englisch (A8), zwei Saetze in `MAX_DAMAGE.scope`, an den Anfang des
Tupels:**

> `This ranks what stays with you between expeditions — attack multipliers, attributes and passives. Armaments are not part of the figure.`
>
> `With no armament in the figure there is nothing to scale, so the five attack multipliers are averaged with equal weight.`

**Was der Satz bewusst nicht sagt:** dass Waffen pro Runde ausgewuerfelt sind.
Das ist Spielwissen des App Designers und steht so in keinem Datenabzug;
AK-140 und AK-157 verbieten Saetze, die etwas ueber die Dateien behaupten, und
dieselbe Zurueckhaltung gilt fuer Behauptungen ueber das Spiel. Der Satz sagt,
**was die Zahl ist** — nachpruefbar an `goals._attack_multiplier_mean` — und
laesst den Spieler das Warum aus seiner eigenen Erfahrung mitbringen.

Der zweite Satz ist der heutige `_NO_ARMAMENT_NOTE` mit **einer** Aenderung
(`chosen` → `in the figure`): seine Praezision ist gut, nur sein Rahmen war
ein Mangel.

#### 3.2 Was aus den beiden Feldern wird

- **`_NO_ARMAMENT` (heute `GoalScore.unknowns`)** — entfaellt als Laufbefund.
  Sein Inhalt steht in `MAX_DAMAGE.scope`.
- **`_NO_ARMAMENT_NOTE` (heute `GoalScore.weights_note`)** — entfaellt als
  Laufbefund. Sein Inhalt steht in `MAX_DAMAGE.scope`.
- **Der Zweig mit Bezugswaffe.** Bleibt er im Code stehen, **muss** er einen
  Laufbefund tragen, der die Waffe nennt — sonst zeigt ein Lauf mit
  Bezugswaffe den `scope`-Satz „Armaments are not part of the figure", waehrend
  die Zahl genau daran haengt. Das ist der A7-Bruch, den AD-025.4 und
  Pruefpunkt 30 suchen. Vorschlag fuer den Wortlaut:
  > `This run was ranked against {armament}, so the figure moves when you carry something else.`

#### 3.3 Nachziehen von AK-162 bis AK-166 (T-084 §1)

Die Aufteilung „Registry-Haelfte / Ergebnis-Haelfte" bleibt **unveraendert
richtig**; es wandert nur ein Satz von der einen in die andere:

- **AK-162 gilt unveraendert.** Zeile 4 des Pickers und Punkt 4 des
  `Why`-Dialogs zeichnen `Goal.scope` vollstaendig — jetzt einschliesslich
  der zwei neuen Saetze. Der Pruefweg („einen sechsten `scope`-Satz
  einbauen") funktioniert unveraendert.
- **AK-163 gilt unveraendert in seiner Regel, verliert aber seinen einzigen
  heutigen Inhalt.** Zeile 3b liest weiterhin zuerst `Baseline.unknowns`,
  dann `SlotPool.unknowns`; `Baseline.unknowns` ist unter A17 fuer
  `max_damage` **leer**, weil der einzige Satz darin nach `scope` gewandert
  ist. Zeile 3b entfaellt dann genau so, wie AK-163 es beschreibt, wenn beide
  Quellen leer sind. **Das Rot-vorher von AK-163 ist damit erledigt und wird
  durch AK-190 ersetzt:** die Gefahr ist nicht mehr, dass der Satz
  verschwindet, sondern dass er an **zwei** Orten steht.
- **AK-164 gilt unveraendert.**
- **AK-165 gilt unveraendert** (keine Chirurgie, keine Entdopplung).
- **AK-166 gilt unveraendert.** `EVEN_WEIGHTING.note` kommt im Picker weiterhin
  nicht vor, denn es gibt weiterhin kein Bedienelement fuer die **Gewichtung**
  (OF-3). Die Lesart aus A16 ist ein Bedienelement fuer eine **andere**
  Annahme; ihr erklaerender Satz steht nach der Regel, die AK-166 im letzten
  Satz selbst formuliert, **neben seinem Bedienelement** (Tooltip, §1.1) und
  im `Why`-Dialog (§2.1) — nicht auf den Karten.

#### 3.4 Der Befund, der A17s Abnahme heute noch scheitern laesst

**Die Bezugswaffe wegzulassen genuegt nicht.** `model.compute` erfuellt
Waffentyp-Schranken aus **`weapons_held`**, nicht aus der Bezugswaffe — die
gefuehrte Waffe bleibt also ein Hebel auf die Rangfolge, auch ohne Bezug.

**Gemessen** (Umgebung A, `reference=None`, `max_damage`, Rangfolge ueber alle
309 Kopien nach marginalem Beitrag, Rezept: `goals.GOALS["max_damage"].score`
auf `evaluate(problem, (cand,), ctx)` minus `evaluate(problem, (), ctx)`):

| Vergleich | Kopien mit anderer Zahl | Rangfolge |
|---|---|---|
| Greatsword gefuehrt gegen Bogen gefuehrt | **2 von 309** | unterscheidet sich **ab Rang 0** |
| Greatsword gefuehrt gegen nichts gefuehrt | **1 von 309** | unterscheidet sich ab Rang 0 |

Die beiden Kopien und ihr Grund, namentlich: `Deep Polished Drizzly Scene`
mit `Improved Greatsword Attack Power` (`triggerOnWepType` 5): **+0,09** mit
Greatsword, **0,00** sonst · `Grand Luminous Scene` mit
`Improved Bow Attack Power` (`triggerOnWepType` 51): **+0,06** mit Bogen,
**0,00** sonst. Von den 845 Effektrollen des Bestands tragen **20**
`triggerOnWepType` und **8** `wepTypeTrigger`.

**Empfehlung, ausdruecklich als Empfehlung und nicht als Vorgabe** (der
Mechanismus gehoert dem `architect`, die Zielsetzung dem Nutzer): der Berater
rechnet mit `reference=None` **und** `weapons_held=()`. Erst dann gilt A17s
Abnahme woertlich. Nach A17s eigener Begruendung ist das folgerichtig — ein
waffentypgebundener Buff ist genau so wenig „zwischen Runden fest" wie die
Bezugswaffe.

**Gemessene Folgen dieser Empfehlung** (A / B):

- Fuellung (c) waechst von **38 / 25** auf **40 / 28** Zeilen; Fuellung (b)
  bleibt bei **144** (A) und geht von 149 auf **147** (B).
- Die Zahl der stummen Effektzeilen steigt um **1** (A: 426 → 427).
- Die Rangfolge wird von der gefuehrten Waffe unabhaengig — per Konstruktion,
  nicht per Zufall.
- **Preis, benannt:** die Zahl des Beraters weicht damit bewusst von der
  Zahl des Statblatts daneben ab, das die gefuehrten Waffen sehr wohl zaehlt.
  Der `GoalContext`-Docstring nennt genau diese Abweichung heute als
  Fehlerklasse (*"QA-001 in a new place"*). Unter A17 ist sie **gewollt** und
  muss deshalb dastehen — das leistet der erste `scope`-Satz aus §3.1.

#### 3.5 Was A17 im Picker sonst noch anfasst

Ohne Bezugswaffe ist die Zielpunktzahl **einheitenlos**
(`GoalScore.unit == ""`, `display` = `Attack multipliers ×1.09`). T-024 §3.3
hat den Fall vorgesehen: *"Ist die Zielpunktzahl einheitenlos, entfaellt der
Zusatz `AR`"*. Damit stuende auf der Karte

```
Damage         +0.09
```

und das verletzt A12: `+0.09` **wovon**? Die linke Beschriftung muss die
Groesse nennen, die die Zahl ist. Vorgabe: solange die Zielrichtung ohne
Armatur rankt, lautet die linke Beschriftung der ersten Zeile
**`Attack multipliers`** statt `Damage`, ohne Einheit am Wert. Sie folgt damit
demselben Wort, das `GoalScore.display` fuehrt — eine Quelle, nicht zwei.

*Nicht entschieden und als Frage an den App Designer gestellt (§6):* ob diese
Zahl stattdessen als Prozentwert gezeigt werden soll.

---

### 4. Punkt 4 — die Armaturenzeile: sie bleibt, mit einem geaenderten Ende

#### 4.1 Entscheidung

Fuellung (c) **bleibt**, und ihr erster Teil bleibt Wort fuer Wort. Ihr Ende
aendert sich:

| | Wortlaut |
|---|---|
| **ersetzt** (T-080 §4, Test nach T-086) | `{effect name}: it depends on the armaments you carry, so no number here.` |
| **neu, ab A17** | `{effect name}: it depends on the armaments you carry, which this figure leaves out.` |

#### 4.2 Warum sie nicht faellt

Der Auftrag fragt, was der Spieler damit anfangen kann. Zwei Dinge, und
beide bleiben unter A17 wahr:

1. **Der Startarmatur-Teil ist nicht ausgewuerfelt.** Jeder Nightfarer
   beginnt jede Expedition mit seiner eigenen Armatur; das Programm rechnet
   diese Paarung an anderer Stelle sogar aus
   (`damage.is_starting_armament`, Slot 1). Ein Relikt mit
   `Improved Greatsword Attack Power` ist fuer Wylder deshalb etwas anderes
   als fuer Ironeye. Ein Satz, der das verschweigt, waere bequem und falsch.
2. **Die Zeile erklaert eine Null.** Ohne sie steht neben dem Effekt nichts,
   und der Spieler haelt das Relikt fuer wertlos, statt zu wissen, dass diese
   Zahl seine Frage nicht beantwortet.

**Was sich wirklich geaendert hat, ist nicht die Wahrheit der Zeile, sondern
der Hebel dahinter:** heute bewegt sich die Zahl, wenn der Spieler die passende
Waffe anlegt (gemessen: +0,09 bzw. +0,06 auf zwei Kopien, §3.4). Unter A17
bewegt sie sich nicht mehr. Der alte Schluss `so no number here` liest sich
dann als Aufforderung, an einem Hebel zu ziehen, der nichts mehr bewegt. Der
neue Schluss `which this figure leaves out` sagt genau das, was gilt, und
steht in derselben Familie wie die Saetze, die diese Datei schon fuehrt:
T-078 §3 Fuellung (ii) `— this figure does not count it.`, T-024 §3.6
`which neither figure counts.`, QA-113 `This figure does not count that
change.` **„figure" ist in diesem Programm das Wort fuer die Rankingzahl**,
und der Spieler liest es an drei anderen Stellen bereits.

**Verworfen: die Zeile faellt und die Zeilen gehen nach (b).** Sie wuerden
`only applies under a condition, so no number here.` lesen — die schwaechere
Auskunft, und T-086 §1.4 hat denselben Weg fuer dieselben Zeilen schon einmal
mit derselben Begruendung verworfen. Ausserdem naehme (b) damit Zeilen auf,
die **nicht** in der Liste 4.9b stehen (QA-104: Armaturenfaelle gehoeren nicht
in `not_counted`) — der Spieler saehe eine Zeile „only applies under a
condition" und faende den Effekt in der Liste der bedingten Effekte nicht
wieder.

#### 4.3 Wie viele Zeilen es betrifft — gemessen

| | A (Wylder) | B (Ironeye) |
|---|---|---|
| (c) heute, Bezugswaffe gefuehrt | 38 | 25 |
| (c) ohne Bezugswaffe, Waffe weiter gefuehrt | 38 | — |
| (c) ohne Bezugswaffe, **nichts** gefuehrt (Empfehlung §3.4) | **40** | **28** |
| (c) im **besten** Fall | 23 | 11 |

Im besten Fall schrumpft (c), weil eine erfuellte Bedingung eine Zahl
erzeugt; im schlechtesten Fall bleibt (c) unveraendert bei 40 / 28, weil der
beste Fall die Buffseite bewegt und der schlechteste die Fluchseite.
**Fuellung (b) faellt im besten Fall auf 0** (A und B) — dort bleibt keine
Bedingung mehr uebrig, die nicht erklaert waere. Das ist keine Luecke,
sondern die Aussage der Lesart.

---

### 5. Akzeptanzkriterien (ab AK-182)

**Das Bedienelement**

- **AK-182** *(eigenes Element, zwei Eintraege.)* Die Leiste traegt eine
  zweite `QComboBox` zwischen Zielwahl und `Optimize` mit genau den
  Eintraegen `Worst case` und `Best case`, in dieser Reihenfolge,
  `Worst case` voreingestellt; die Zielwahl behaelt genau ihre zwei
  Eintraege. Links von `Optimize` stehen hoechstens zwei Einstellungen.
  Pruefweg: ausgelesene Eintraege beider Comboboxen. *Rot-vorher:* eine
  Umsetzung mit vier Eintraegen in der Zielwahl
  (`Maximise damage (worst case)` …) bricht die Zusage aus dem
  `goals.py`-Docstring, dass ein drittes Ziel ein Registry-Eintrag ist — sie
  braucht dann sechs.
- **AK-183** *(kein neuer Zustand.)* Eine Aenderung der Lesart verwirft einen
  lebenden Vorschlag und laesst die Statuszeile 4.1 sagen; ein laufender Lauf
  wird abgebrochen und zeigt 4.7 — dasselbe Verhalten und derselbe Code-Pfad
  wie bei einer Aenderung der Zielwahl. §4 bekommt **keine** neue Zeile.
  *Rot-vorher:* eine Umsetzung, die bei Umschaltung selbsttaetig neu rechnet,
  startet eine Suche, deren Kosten (S11) niemand gemessen hat, ohne dass der
  Spieler `Optimize` gedrueckt haette (§5.1).
- **AK-184** *(nie zwei Zahlen.)* Zu keinem Zeitpunkt zeigt die Oberflaeche
  fuer dieselbe Kopie zwei Zahlen unter verschiedenen Lesarten. Die Lesart
  reist in der Anfrage und erreicht den Anfrage-Schluessel, so dass ein
  Ergebnis nie unter einer anderen Lesart beschriftet werden kann.
  Pruefweg: zwei Anfragen, die sich nur in der Lesart unterscheiden, ergeben
  verschiedene Schluessel (`run.py` fuehrt `declared` bereits mit).
  *Rot-vorher:* ein Nebeneinander „worst / best" auf der Slotkarte ist die
  Fehlerklasse D-11/QA-082, und die zweite Zahl haette keinen Erzeuger.
- **AK-194** *(die Breite wird gemessen, nicht geschaetzt.)* Nach dem Einbau
  wird am **laufenden Fenster** gemessen, wie breit die Statuszeile bei
  1320 px Fensterbreite noch ist, mit Messumgebung nach L-009 (Plattform,
  Qt-Stil, Skalierung, physisch oder logisch). Sie muss mindestens **zwei
  Drittel** ihrer heutigen 158 px behalten (**≥ 105 px**; Zielwert aus einer
  einzigen gemessenen Zahl abgeleitet, selbst kein gemessener Wert). Wird er
  unterschritten, heissen die Eintraege `Worst` und `Best`. *Rot-vorher:*
  eine Umsetzung, die die Breite aus der Zeichenzahl in §1.4 herleitet, hat
  keine Messung — 12,0 px je Zeichen liefert dieser Rechner offscreen fuer
  **jede** Zeichenkette (T-084 §0).

**Was die Zahl ueber sich sagt**

- **AK-185** *(genau viermal, nie je Zeile.)* Die Lesart wird genannt: im
  Bedienelement, im Kopf des Vorschlagsblocks, im `Why`-Dialog (Titel und
  Kopf) und in der Zusammenfassungszeile des Pickers. In keiner Effekt-,
  Fluch- oder Zaehlzeile und auf keiner Reliktkarte kommt sie vor.
  Pruefweg: ausgelesener Text je Ort, Vorkommen von `worst case` /
  `best case` zaehlen. *Rot-vorher:* eine Umsetzung, die jeder Zeile
  `(worst case)` anhaengt, erzeugt auf der laengsten Slotgruppe 21
  Wiederholungen — das Rauschen, gegen das AK-50 geschrieben ist.
- **AK-186** *(Voreinstellung fuer Bedingungen, nie fuer Zahlen.)* Die Lesart
  wirkt ausschliesslich ueber `GoalContext.declared`. Eine vom Spieler selbst
  erklaerte Bedingung bleibt so, wie er sie erklaert hat; kein Gewicht,
  keine Zahl und kein Feld ausser `declared` wird von der Lesart beruehrt.
  Pruefweg: zwei Laeufe mit derselben Belegung, einer mit einer vom Spieler
  erklaerten Bedingung — der erklaerte Wert steht in beiden Lesarten im
  Ergebnis. *Rot-vorher:* eine Umsetzung, die `declared` je Lesart neu
  aufbaut, wirft die Angabe „ich fuehre 3 Boegen" weg, und die Zahl des
  Beraters widerspricht dem Statblatt daneben, ohne dass es jemand sagt.
- **AK-187** *(die Lesarten teilen `not_counted`, sie erfinden nichts.)* Im
  schlechtesten Fall enthaelt `not_counted` genau die heutigen Eintraege ohne
  die konditionalen Flueche; im besten Fall genau die konditionalen Flueche.
  In Umgebung §0 sind das **170** bzw. **27** gegen heute **197**, und
  `170 + 27 = 197`. Pruefweg: Summe von `len(explain.not_counted(built))`
  ueber die 309 Ein-Relikt-Probleme, je Lesart. *Rot-vorher:* eine Umsetzung,
  die im schlechtesten Fall auch Buffbedingungen setzt (oder umgekehrt),
  ergibt eine Summe, die diese Identitaet verletzt — sie ist der Waechter.
- **AK-188** *(die Listen behalten ihre Saetze.)* 4.9a, 4.9b, die Ueberschrift
  des 4.9b-Abschnitts und die Zaehlzeile aus T-078 §6 bleiben woertlich
  unveraendert; unter beiden Lesarten aendern sich nur ihre Zahlen. In
  Umgebung §0: `curses_without_a_figure` **67 → 42** im schlechtesten Fall,
  `effects_without_a_figure` **426 → 323** im besten. AK-155 gilt in beiden
  Lesarten. *Rot-vorher:* eine Umsetzung, die fuer den schlechtesten Fall
  einen eigenen Satz schreibt („counted as if it were active"), gibt
  derselben Sache einen zweiten Wortlaut und laesst 4.9b und die Zeile
  auseinanderlaufen.
- **AK-189** *(der schlechteste Fall ist laenger, und das wird gemessen.)*
  **Schreibt AK-160 fort, ersetzt es nicht.** In Umgebung §0 waechst die
  laengste Slotgruppe des `Why`-Dialogs von **14** auf **21** Zeilen und der
  laengste Vorschlagsblock von **15** auf **22** Zeilen; die meisten
  Fluchzeilen auf einer Kopie steigen von 5 auf 15. Nach dem Einbau wird
  beides nach AK-161 **je Lesart getrennt** neu gemessen. *Rot-vorher:* eine
  Slotkarte, die auf den 14 Zeilen aus AK-160 ausgelegt ist, schneidet im
  schlechtesten Fall ab oder waechst ueber den Bildschirm — 4.14 verlangt
  Umbruch, nicht Kuerzung.

**Die Zahl ohne Waffe**

- **AK-190** *(der Satz wandert und wird umgeschrieben.)* Die beiden Saetze
  aus §3.1 stehen in `MAX_DAMAGE.scope`; `_NO_ARMAMENT` und
  `_NO_ARMAMENT_NOTE` erscheinen in keinem `GoalScore` mehr, und der alte
  Wortlaut `No armament selected — ranked on attack multipliers only, without
  weapon scaling.` kommt in der Oberflaeche nicht mehr vor. Bleibt der Zweig
  mit Bezugswaffe erhalten, traegt **er** einen Laufbefund, der die Armatur
  nennt. Pruefweg: Volltextsuche im ausgelesenen Text von Picker und
  `Why`-Dialog. *Rot-vorher:* eine Umsetzung, die den Satz in `scope`
  schreibt **und** als `unknowns` stehen laesst, zeigt ihn im `Why`-Dialog
  zweimal untereinander — die Fehlerklasse aus AK-164.
- **AK-191** *(die Rangfolge haengt an keiner gefuehrten Waffe.)* Zwei
  Laeufe, die sich nur in der gefuehrten Armatur unterscheiden, ergeben
  dieselbe Rangfolge und dieselben Zahlen — fuer beide Zielrichtungen.
  Pruefweg: ueber den Bestand ranken, einmal mit Greatsword, einmal mit
  Bogen. *Rot-vorher, gemessen:* wird nur die **Bezugswaffe** weggelassen und
  `weapons_held` weiter gefuellt, aendern in Umgebung A **2 von 309** Kopien
  ihre Zahl und die Rangfolge unterscheidet sich **ab Rang 0** —
  `Deep Polished Drizzly Scene` (`Improved Greatsword Attack Power`, +0,09
  mit Greatsword, 0,00 mit Bogen) und `Grand Luminous Scene`
  (`Improved Bow Attack Power`, +0,06 mit Bogen, 0,00 mit Greatsword).
- **AK-192** *(die Armaturenzeile nennt die Zahl, nicht den Hebel.)* Fuellung
  (c) lautet
  `{effect name}: it depends on the armaments you carry, which this figure
  leaves out.` Die Zeichenfolge `armaments you carry, so no number here`
  kommt nirgends mehr vor. Der Test von (c) bleibt AK-177 bis AK-179
  unveraendert. In Umgebung §0 sind das **40** Zeilen (A) und **28** (B),
  wenn nichts gefuehrt wird, und **23** (A) / **11** (B) im besten Fall.
  *Rot-vorher:* der heutige Wortlaut raet unter A17 zu etwas, das die Zahl
  nicht mehr bewegt — der Spieler legt die Waffe an und die Rangfolge bleibt,
  wo sie war.
- **AK-193** *(die Spalte nennt die Groesse, die sie zeigt.)* Solange die
  Zielrichtung ohne Armatur rankt, traegt die erste Zeile der Wertspalte im
  Picker die Beschriftung `Attack multipliers` und der Wert keine Einheit;
  das Wort kommt aus derselben Quelle wie `GoalScore.display`. *Rot-vorher:*
  `Damage  +0.09` — eine Zahl ohne Groesse und ohne Einheit, also A12
  gebrochen; `+12.4 AR` waere zusaetzlich falsch, weil kein Angriffswert mehr
  gerechnet wird.

---

### 6. Offene Fragen an den App Designer

- **F-K (A17, Darstellung der Zahl).** Ohne Armatur ist die Zielpunktzahl ein
  Mittel aus fuenf Angriffsmultiplikatoren; auf der Karte steht dann etwa
  `Attack multipliers +0.09`. Soll sie stattdessen als Prozentwert gezeigt
  werden (`+9 %`)? **Empfehlung: nein** — die Umrechnung eines *Unterschieds
  zweier Mittelwerte* in einen Prozentsatz behauptet einen Anteil am Schaden,
  den die Zahl nicht traegt. Geschmacks- und Verstaendlichkeitsfrage,
  deshalb hier.
- **F-L (A17, gefuehrte Waffen).** §3.4 zeigt gemessen, dass A17s Abnahme
  erst haelt, wenn der Berater auch **ohne gefuehrte Waffen** rechnet. Das
  entkoppelt die Zahl des Beraters bewusst von der Zahl des Statblatts
  daneben. Ist das gewollt? **Empfehlung: ja** — es folgt A17s eigener
  Begruendung, und der erste `scope`-Satz sagt es dem Spieler.

---

### 7. Was dieser Nachtrag ausdruecklich **nicht** entscheidet

- **Das Statblatt und das Waffenpanel des Build planners.** Unberuehrt, A16
  sagt das ausdruecklich.
- **Der Relic Picker als Ganzes** (AK-41 bis AK-53, S10c). Nur die drei
  Stellen, an denen A16 oder A17 ihn beruehren: die Zusammenfassungszeile
  (§2.1), Zeile 3b / Zeile 4 (§3.3) und die Beschriftung der Wertspalte
  (§3.5).
- **Ob `wepTypeTriggerCount` auswertbar gemacht wird**, und was 256/512/768/
  1024 in den Waffenfeldern bedeuten. Unveraendert Scope-Grenze aus T-086.
- **Der Mechanismus, mit dem die Lesart in `declared` landet**, und ob dafuer
  ein Registry-Typ neben `Weighting` entsteht. Das gehoert dem `architect`;
  diese Vorgabe sagt nur, **was** gelten muss (§2.3, AK-186).
- **Die vier Fragen an den App Designer** (F-B, F-C, F-F, F-G) und die
  dreizehn Streichvorschlaege je Tab. Unberuehrt.

---

## Director-Korrektur zum Relic Picker — 2026-09-07, entschieden vom App Designer

Der App Designer hat den gebauten Picker am laufenden Fenster gesehen und
zwei Dinge entschieden. Beide gehen den Vorgaben oben vor.

**1. Die beiden Spitzenreiter stehen oben.** Woertlich: *"zeig mir aber immer
den top pick für dmg und survival als erstes. in beiden varianten."*

Bisher fuehrte bei einer Zielsortierung der **Wert** (§3.4), und der
Spitzenwert war nur durch den Chip `BEST FOR …` gekennzeichnet (AK-46). Wer
nach Schaden sortierte, fand das beste Ueberlebensrelikt irgendwo weiter
unten. Genau das war der Punkt: **beide Zahlen stehen auf jeder Karte, aber
nur eine ordnete das Raster.**

Neu, als **AK-195**: In beiden Zielsortierungen stehen die Karten mit dem
Spitzenwert **beider** Zielrichtungen an der Spitze des Rasters, vor allen
uebrigen. Es sind genau die Karten, die nach AK-46 einen `BEST FOR …`-Chip
tragen — die Anordnung sagt damit nichts, was der Chip nicht schon sagt, sie
macht es nur auffindbar.

- **Reihenfolge an der Spitze:** die Custom-Karte fuehrt wie bisher das Raster
  in jeder Sortierung (Bestand). Danach die Spitzenreiter der **sortierten**
  Zielrichtung, danach die der anderen. Eine Karte, die fuer beide
  Spitzenreiter ist, steht einmal, an der ersten dieser Stellen.
- **Gleichstaende bleiben Gleichstaende.** Tragen fuenf Karten den Chip,
  stehen fuenf Karten oben, in der Ordnung, die ohne Berater gaelte
  (Favoriten, dann Name). **Keine Ordnungszahl, kein Rangabzeichen** — AK-44
  gilt unveraendert.
- **Ist der Spitzenwert einer Richtung `no change` oder negativ**, wird fuer
  diese Richtung **nichts** vorgezogen — dieselbe Bedingung, unter der AK-46
  keinen Chip vergibt. Zwanzig vorgezogene Karten bei durchgehend Null waeren
  dieselbe Luege wie zwanzig Chips.
- **Bei `Sort by` = `Name`** wird **nichts** vorgezogen. Diese Sortierung
  existiert, um ein bestimmtes Relikt zu finden; zwei vorgezogene Karten
  wuerden die alphabetische Ordnung genau dort brechen, wo sie der einzige
  Zweck ist. *Director-Entscheidung, nicht vom App Designer gesagt — seine
  Formulierung "in beiden varianten" liest der Director als die beiden
  Zielsortierungen. Widerspricht er, ist das eine Zeile.*
- **Die Ordnung bleibt stabil** (AK-44): zweimal derselbe Zustand ergibt
  zweimal dieselbe Reihenfolge.

**Rot-vorher:** Nach Schaden sortieren; die Karte mit dem hoechsten
`Damage taken`-Wert steht nicht in den ersten Positionen hinter der
Custom-Karte.

**2. AK-51 ist unerfuellbar geschrieben und wird auf das Messbare
zurueckgenommen.** Der `developer` hat in T-093 nachgemessen: drei ganze
Kartenzeilen brauchen **1122 px**, verfuegbar sind **1027 px** auf dem
Bildschirm des Nutzers. Breiter oeffnen macht es schlechter (1148 / 1213 /
1213 px bei sechs, sieben, acht Spalten). **Die Bedingung war schon vor dem
Wertblock verletzt**, mit nur zwei Textzeilen ueber dem Raster — sie ist also
keine Folge des Beraters.

Neu, als **AK-196**, und **ersetzt die zweite Haelfte von AK-51**: Am
Standardmass des Pickers erscheint **keine waagerechte Bildlaufleiste**, und
es sind mindestens **zwei vollstaendige Kartenzeilen** sichtbar. Die erste
Haelfte von AK-51 (keine waagerechte Bildlaufleiste; im Konfliktfall das
Standardmass vergroessern statt den Inhalt zu kuerzen) gilt unveraendert.

*Begruendung der Zahl:* zwei Zeilen sind das, was auf dem einzigen Bildschirm,
auf dem gemessen wurde, mit dem vorgegebenen Inhalt erreichbar ist. Drei waren
eine Zusicherung ohne Messung. Wer sie zurueckhaben will, muss Inhalt ueber
dem Raster streichen — das ist eine Frage an den App Designer, keine an die
Umsetzung.

---

## Der Picker oeffnet vor seinen Zahlen (ui-ux-designer, T-124) — 2026-09-08

**Ersetzt §3.8 des T-024-Abschnitts.** Der alte Absatz bleibt an seinem Platz
stehen, mit einem Korrekturkasten davor; hier steht, was gilt.

### 0. Grundlage, Methode, und was davon **gesehen** ist

**Gelesen:** `docs/tasks/T-124.md` · `ARCHITECTURE.md` (Nachtrag VIII ganz —
AD-028, AD-029, U1–U8, Risiken, OF-25 bis OF-27; dazu AD-018 mit dem
nachgezogenen Punkt 4 und der korrigierten Laufzeittabelle, AD-006) ·
`docs/berichte/T-122-architect.md` · `UI_SPEC.md` §3.2 bis §3.8, AK-08 bis
AK-13, AK-41 bis AK-53, AK-165/166, AK-195/AK-196 · `CLAUDE.md` · `GOAL.md`
A6/A7/A8/A12 in der Fassung, die der Auftrag woertlich zitiert.

**Am Quellstand gelesen** (lesend, nichts veraendert, nichts gestartet):
`nrplanner/relicpicker.py`, `nrplanner/advisorbar.py`,
`nrplanner/advisor/candidates.py`, `nrplanner/advisor/types.py`.

**Nicht gesehen:** kein laufendes Fenster, kein Bildnachweis, keine eigene
Messung. Der Auftrag sagt „du entwirfst, du misst nicht"; jede Zahl unten ist
zitiert, mit Fundstelle. Aussagen, die nur aus dem Quelltext stammen, sind als
**(Quelltext)** gekennzeichnet — sie sind pruefbar, aber nicht am laufenden
Programm bestaetigt.

**Nummernkreis, korrigiert.** Der Auftrag nennt **AK-195** als freien Kreis;
`docs/state.md` Zeile 11 ebenfalls. **Beide sind ueberholt:** AK-195 und
AK-196 sind am 07.09.2026 in der „Director-Korrektur zum Relic Picker"
vergeben, AK-195 ist in `ea3d016` gebaut und wird von fuenf Testfaellen in
`tests/test_relic_picker_advisor.py` gehalten. Diese Vorgabe beginnt deshalb
bei **AK-197**. `docs/state.md` gehoert nicht mir und ist nicht angefasst; die
Korrektur steht im Bericht.

### 1. Was faellt, was gilt — beide Zahlen

| | Zahl | Herkunft |
|---|---|---|
| **alt, widerlegt** | **~51 ms** fuer den teuersten Picker-Lauf | **gerechnet**, nicht gemessen: 205 Kandidaten x 0,25 ms je Bewertung; die 0,25 ms aus einer Bewertung vom 01.09.2026 **ohne protokollierte Umgebung** (AD-028) |
| **neu, gemessen** | **318,1 ms** (Median, n=25, Spanne 289,6–358,9) | `docs/perf/baselines.md` S11-C — Slot 2 weiss, 206 Kandidaten, Ryzen 7 5800H bei 1102 von 3201 MHz unter `Legion Quiet Mode`, CPython 3.12.10, `76f1887` (L-009) |

Faktor **6,3**. Die alte Zahl lag unter der 250-ms-Schwelle und begruendete
damit, dass der Picker **keinen** Wartezustand zeigt; die gemessene liegt
darueber. Dieselbe gerechnete Zahl stand in drei Dateien
(`ARCHITECTURE.md`, `UI_SPEC` §3.8, `relicpicker.py:276-281`) und keine der
drei sagte, dass sie gerechnet war (OF-27). Die ersten beiden sind
richtiggestellt, die dritte ist Sache des `developer` in U5b.

**Die alte Zahl wird nicht geloescht.** Wer sie nur entfernt, laesst den
naechsten Leser glauben, es habe hier nie eine Entscheidung gegeben — und
genau so ist der Fehler drei Dateien weit gewandert.

**Bandbreite, die mitentscheidet** (S11-C, ueber die Slots): der billigste
Slot kostet **32–82 ms**, der teuerste **318,1 ms**; ein Treffer im
Ergebnis-Cache (LRU 64 nach AD-028.1, gemessen 30 % ueber Dialoggrenzen
hinweg) kostet **nichts**. Ein Entwurf, der nur den teuersten Fall bedient,
laesst im billigsten etwas aufblitzen. Deshalb ist unten **kein Element**
vorgesehen, das erscheint und wieder verschwindet.

### 2. §3.8 neu — Warten im Picker

> **Der Dialog oeffnet sofort und ohne Zahlen.** Die Rechnung laeuft in der
> Picker-Spur des Beraters (AD-028); der Dialog wartet nicht auf sie, bevor
> er sich zeigt. Es gibt **genau zwei Anstriche** je Oeffnung: den ohne
> Antwort und den mit ihr. Alles, was an der Antwort haengt — Zahlen, Chips,
> Ordnung, Laufbefunde — wechselt in **einem** davon, nie in zweien
> nacheinander.
>
> **Kein Fortschrittsbalken, kein Wartecursor, kein zweiter Dialog, kein
> deaktiviertes Bedienelement.** Ein 6-px-Balken, der nach einem Drittel
> einer Sekunde wieder verschwindet, ist genau das Aufblitzen, das AK-09
> verbietet; und der Picker hat etwas Besseres als einen Balken: **29
> Platzhalter, die an der Stelle stehen, an der die fehlende Information
> landen wird.** Ein Balken sagt „es passiert etwas", die Platzhalter sagen
> „hier, und hier, und hier".
>
> **Der Wartezustand besteht aus genau zwei Dingen**, beide vom ersten
> Anstrich an da, beide ohne eigenes Widget:
> 1. In beiden Wertzeilen jeder Karte steht `…` statt einer Zahl (§3.3, im
>    Code `PENDING`). Der Block ist ohnehin gebaut, die Kartenhoehe aendert
>    sich nicht (AK-41).
> 2. In der Zusammenfassungszeile (§3.2, Zeile 3) steht **statt** des
>    Bezugsgroessen-Satzes der Wartesatz aus §6 unten. Es kommt keine Zeile
>    dazu und es faellt keine weg — **ein Nebensatz wechselt seinen
>    Wortlaut**.
>
> **Es gibt keine Zeitschwelle und keinen Verzoegerungstimer.** Der
> Wartezustand wird betreten, wenn beim Bau des Rasters keine Antwort
> vorliegt, und verlassen, wenn sie vorliegt — sonst nichts. Das ist
> moeglich, **weil nichts erscheint und nichts verschwindet**: ein Glyph wird
> zur Zahl, ein Nebensatz zu einem anderen. Damit gibt es auch bei 32 ms
> nichts, was blitzen koennte, und die Vorgabe ist ohne Wanduhr pruefbar
> (Vorgabe 7 des Auftrags).
>
> **Liegt die Antwort schon beim Bau des Rasters vor** (Cache-Treffer), wird
> der Wartezustand **nicht** betreten: dann gibt es einen einzigen Anstrich,
> wie heute.
>
> **Was der Wartezustand nicht behauptet:** kein `BEST FOR …`-Chip, keine
> vorgezogene Karte (AK-195), kein Satz `Nothing you own raises … in this
> slot.` und kein Satz `The game's data carries no figures …`. Alle vier sind
> Aussagen ueber ein Maximum oder ueber die Spieldateien; ohne Antwort gibt
> es weder das eine noch das andere (A7).
>
> **Der Dialog bleibt modal** (Bestand, AD-028 unberuehrt). Diese Vorgabe
> ruehrt nicht daran. Daraus folgt eine Vereinfachung, die tragend ist: der
> Grundzustand kann sich waehrend einer Oeffnung **nicht** aendern — der
> Spieler kommt an Nightfarer, Vessel, Level und die uebrigen Slots nicht
> heran. Deshalb genuegt **eine** Frage je Oeffnung (§4).
>
> **Kein `Cancel`.** AK-10 verlangt fuer die Advisor bar, dass `Optimize`
> waehrend des Laufs `Cancel` traegt. Der Picker bekommt kein Gegenstueck:
> Abbrechen heisst hier den Dialog schliessen, und das geht seit jeher mit
> Esc. Ein `Cancel`, das den Dialog stehen laesst, hinterliesse einen Picker,
> der nie Zahlen zeigen kann — ein totes Ende mit einem Knopf davor.
>
> **Der Generationszaehler aus AD-006.3 gilt jetzt auch hier** (AD-028.4).
> Eine Antwort, die nach dem Schliessen eintrifft, fasst kein Widget an. Der
> Fall, den der alte Absatz fuer unmoeglich hielt, ist der Normalfall
> geworden.

**AK-09 und AK-10 gelten weiter — fuer die Advisor bar.** Sie sind im
T-004-Abschnitt fuer **einen** Statusstreifen mit **einer** Statuszeile und
**einem** Knopf geschrieben; der Picker hat 29 bis 55 Karten mit je zwei
Wertzeilen und keinen Knopf. AK-197 bis AK-202 sind das Gegenstueck fuer den
Picker und **verdraengen AK-09/AK-10 dort**, nicht anderswo. Der Zweck von
AK-10 — ueber 250 ms wird das Warten gezeigt — ist erfuellt, nur mit anderen
Mitteln als einem Balken.

### 3. Ordnung, Kopfzeile, Chips — die eigentliche Frage

Das ist der Punkt, den AD-028 (b) ausdruecklich offen gelassen hat: heute
entstehen Ordnung, Kopfzeile und Chips beim Bauen des Rasters aus der
Rangfolge; liegt die Rangfolge erst 320 ms spaeter vor, muss etwas geschehen.

**Entschieden: die Karten stehen sofort da, in der beraterfreien Ordnung, und
das Raster ordnet sich genau einmal um, wenn die Antwort kommt.**

#### 3.1 Warum nicht die Alternative

Die naheliegende Gegenoption — **das Raster bleibt leer, bis die Antwort da
ist** — bewegt nichts und ist trotzdem verworfen:

- **Die Karten haengen am Berater nicht.** Welche Relikte in diesen Slot
  passen, ihre Namen, Effekte, Fluche, Favoriten und Symbole stehen ohne jede
  Beraterrechnung fest (Quelltext: `slot.available_items()` fragt den
  Bestand, nicht den Berater). Bekanntes zurueckzuhalten, um eine unbekannte
  Ordnung zu schuetzen, ist die falsche Richtung — und sie steht gegen die
  Hausregel dieses Programms, zu zeigen was man weiss und zu sagen was man
  nicht weiss (A7).
- **Der haeufigste Weg braucht die Zahlen gar nicht.** Wer ein bestimmtes
  Relikt sucht, tippt in das Filterfeld und liest Namen. Fuer ihn waere ein
  leeres Raster ein Drittel einer Sekunde reiner Verlust.
- **Die Dialoggroesse haengt an den Karten** (Quelltext: `_fit_to_three_rows`
  misst die Karten und vergroessert den Dialog **einmal**). Ein leeres Raster
  beim ersten Anstrich hiesse, dass der Dialog seine Groesse erst bei der
  Antwort findet — ein Fenster, das sich 320 ms nach dem Oeffnen selbst
  vergroessert, ist eine groessere Bewegung als jede Umsortierung darin.

Die dritte Gegenoption — **die Namensordnung bleibt die ganze Oeffnung ueber
stehen, es wird nie umsortiert** — ist verworfen, weil sie AK-195 auf der
wichtigsten Oeffnung ausser Kraft setzt. Der App Designer hat woertlich
verlangt, den Spitzenreiter beider Richtungen zuerst zu sehen; eine Ordnung,
die diese Zusage nur ab der zweiten Sortieraenderung einloest, bricht sie.

#### 3.2 Was beim ersten Anstrich steht

- **Ordnung:** Favoriten zuerst, dann Name — genau die Ordnung, die
  `Sort by` = `Name` ergibt und die das Raster ohne Berater ohnehin haette
  (§3.4). Sie ist keine zweite Rangfolge und behauptet keine; sie ist die
  Ordnung, die dieser Bildschirm hat, wenn niemand rechnet.
- **`Sort by`** steht unveraendert auf der gewaehlten Zielrichtung. Es wird
  nicht auf `Name` umgestellt — die Einstellung gilt programmweit (AK-43),
  und sie im Picker still umzulegen waere eine Aenderung an der Advisor bar,
  die der Spieler nicht vorgenommen hat.
- **Dass die Ordnung noch nicht die sortierte ist, sagt der Wartesatz** in
  Zeile 3. Das ist der Grund, warum dieser Satz mehr traegt als „es rechnet":
  er ist die Stelle, an der die Zusammenfassungszeile sonst **behauptet**,
  gegen den Build gerankt zu haben (`ranked against your build with Slot 3
  empty`). Diese Behauptung darf nicht dastehen, solange nichts gerankt ist
  (A7, A12).
- **Kein Chip, keine Vorziehung, keine Kopfzeile.**
- **Die beiden Textzeilen ueber dem Raster stehen vollstaendig** — die
  Pflichtzeile aus AD-018.3 und die `scope`-Saetze der Zielrichtung. Beide
  brauchen keine Rechnung: die erste ist eine Konstante, die zweite kommt aus
  der Registry (Quelltext: `advisor_goals.GOALS[goal_id].scope`). **Heute
  werden beide ausgeblendet, solange keine Rangfolge vorliegt** (Quelltext:
  `_say_what_was_left_out` versteckt `findings` **und** `caveats`, wenn
  `ranking is None`). Bliebe das so, verschwaende der Attack-Rating-Vorbehalt
  fuer 320 ms und erschiene dann — das ist ein Bruch von AK-50 waehrend des
  Wartens und, schlimmer, ein Hoehensprung ueber dem Raster, der das ganze
  Raster nach unten schiebt. **Das ist die groessere Bewegung, nicht die
  Umsortierung.** Beide Zeilen stehen vom ersten Anstrich an.

#### 3.3 Was beim zweiten Anstrich geschieht

In **einem** Anstrich, gemeinsam: die Zahlen ersetzen die `…`, die Chips
erscheinen, das Raster nimmt seine sortierte Ordnung samt AK-195-Vorziehung
an, die Kopfzeile erscheint falls AK-46 sie verlangt, und die Laufbefunde
(Zeile 3b) erscheinen, falls es welche gibt.

Was dabei **nicht** geschieht:

- **Der Bildlauf wandert nicht.** Der sichtbare Ausschnitt bleibt an
  derselben Stelle. Wer beim Oeffnen nichts getan hat, steht oben und sieht
  genau die vorgezogenen Spitzenreiter, um die es AK-195 geht; wer bereits
  gescrollt hat, wird nicht dorthin zurueckgerissen.
- **Der Tastaturfokus wandert nicht.** Er bleibt auf demselben Bedienelement;
  liegt er auf einer Reliktkarte, liegt er danach auf der Karte **desselben
  Relikts**, auch wenn sie inzwischen woanders steht. Das Raster wird
  vollstaendig neu gebaut (Quelltext), also muss der Fokus ausdruecklich
  wiederhergestellt werden — sonst faellt er beim Warten auf den Dialog
  zurueck und AK-52 gilt nur bis zur 320. Millisekunde.
- **Der Dialog aendert seine Aussenmasse nicht.**
- **Die Kartenhoehe aendert sich nicht** (AK-41, Bestand).

#### 3.4 Die eine Bewegung, die bleibt — und ihre Grenze

Zwei Dinge bewegen sich, und beide sind gewollt:

1. **Die Karten nehmen ihre Ordnung ein.** Das ist die Antwort selbst; ohne
   sie gaebe es keine Rangfolge. Angekuendigt ist sie durch den Wartesatz.
2. **Die Laufbefund-Zeile (3b) erscheint, falls es Befunde gibt**, und
   schiebt die Oberkante des Rasters nach unten. Sie ist die **einzige**
   Anzeige ueber dem Raster, die ohne Antwort nicht existieren kann
   (Quelltext: sie kommt aus `pool.unknowns` und `baseline.unknowns`).

**Auflage zu Punkt 2, weil der Dialog sich nur einmal misst:** Der
`developer` misst am gebauten Stand, um wie viele Pixel die Oberkante des
Rasters wandert, wenn die Befundzeile im schlechtesten realen Fall erscheint
(Bestand des Nutzers, Standardmass des Pickers), und nennt die Zahl **mit
Umgebung** (L-009) im Bericht. Bleibt danach weniger als zwei vollstaendige
Kartenzeilen sichtbar, ist **AK-196 verletzt** und die Loesung ist nicht der
Wortlaut, sondern der Platz der Zeile — dann kommt die Frage zu mir zurueck.
Geschaetzt wird hier nichts.

### 4. Der Zielrichtungswechsel im offenen Dialog

AD-028 fuehrt `relicpicker.py:1169-1171` als **zweiten** Fall, der 318 ms
kostet: der offene Dialog rechnet neu, wenn der Spieler `Sort by` umstellt.
Der Auftrag fragt, ob dieser Fall denselben Wartezustand bekommt.

**Antwort: er bekommt gar keinen — weil er nichts zu rechnen hat.**

**Belegt am Quelltext, nicht vermutet:**

| Beleg | Fundstelle |
|---|---|
| „Every goal in `goals` is scored for every candidate, whichever one `rank_by` names." | `advisor/candidates.py:254-259`, Docstring von `pool` |
| Jeder Kandidat traegt `marginals` fuer **jedes** Ziel, gebaut in einer Schleife ueber `goals.items()` | `advisor/candidates.py:316-320` |
| `baseline` traegt je Ziel Wert, Einheit, `unknowns` und `weights_note` — beide Richtungen | `advisor/candidates.py:328-330` |
| `candidates` ist die **vollstaendige** Liste `measured`, nicht gekuerzt | `advisor/candidates.py:331` |
| Die Anzeige liest ohnehin ueber Handles nach und sortiert selbst um | `relicpicker.py` `Ranking.gain`, `_in_the_chosen_order` |
| Der Grundzustand haengt am Slot, nicht an der Richtung | `candidates.base_state_for(problem, slot_index)` |

Ein Pool, der fuer `max_damage` gerechnet wurde, traegt also **alles**, was
die Anzeige fuer `min_damage_taken` braucht. Richtungsabhaengig sind nur die
Ordnung, die Chips, die Kopfzeile und die `scope`-Saetze — und die drei
ersten rechnet die Anzeige selbst, den vierten liest sie aus der Registry.
Weil der Dialog modal ist, kann sich der Grundzustand waehrend einer Oeffnung
ausserdem nicht aendern.

**Daraus die Vorgabe:** eine Oeffnung des Pickers stellt **eine** Frage. Ein
Wechsel der Zielrichtung im offenen Dialog stellt **keine zweite**; er ordnet
um, setzt die Chips neu und tauscht die `scope`-Saetze — sofort, in einem
Anstrich, **ohne** `…` und ohne Wartesatz. Auch der Filter, der Bildlauf und
die Favoritenvergabe stellen keine Frage.

**Die Falle dabei, ausdruecklich benannt:** `SlotPool.rank_by` sagt, in
welcher Richtung der Pool **sortiert wurde** — nicht, in welcher der Spieler
gerade liest. Heute liest die Anzeige ihre Richtung aus genau diesem Feld
(Quelltext: `Ranking.goal_id` gibt `pool.rank_by` zurueck). Wird ein Pool
weiterverwendet, muss die Richtung aus der **einen** Zieleinstellung des
Programms kommen (AK-43), nicht aus dem Feld. Sonst zeigt der Picker still
die alte Richtung an — genau der Fehler, gegen den D-4 dieses Feld
eingefuehrt hat, und der in T-077 unbemerkt 10,2 % eines Angriffswerts
gekostet hat.

**Wechselt der Spieler die Richtung, waehrend die Antwort noch unterwegs
ist**, wird **nicht** neu gefragt und der Wartezustand **nicht** neu
begonnen. Es ist dieselbe eine Antwort; sie wird gezeichnet in der Richtung,
die in dem Moment gewaehlt ist, in dem sie eintrifft.

**`Sort by` = `Name` waehrend des Wartens:** die Ordnung ist damit schon die
endgueltige, also ordnet der zweite Anstrich nichts um — die Zahlen kommen
nur in die Spalten. Der Wartezustand bleibt bis dahin bestehen, denn die
Zahlen fehlen weiterhin.

**Rueckweg, falls die Belege oben nicht tragen.** Stellt der `developer` in
U5b fest, dass ein Pool die andere Richtung doch nicht vollstaendig bedient
(etwa weil `goals` beim Bau nicht beide Richtungen enthielt), dann — und nur
dann — bekommt der Zielrichtungswechsel **denselben** Wartezustand wie das
Oeffnen, mit denselben Regeln aus §2 und §3.3, mit einem Unterschied: die
bereits stehende Ordnung bleibt waehrend des Wartens stehen, sie faellt nicht
auf Namensordnung zurueck. Das ist **ein Befund und wird berichtet**, nicht
stillschweigend gebaut (L-008c).

### 5. Was in der Zahlenspalte steht — drei Zeichen, drei Aussagen

Der Auftrag fragt, ob das `…` aus §3.3 noch traegt, seit die Wartezeit benannt
ist. **Es traegt** — unter einer Bedingung: die drei Zustaende duerfen sich
nie vermischen.

| steht da | heisst | wann |
|---|---|---|
| `…` | **noch nicht gemessen** — die Frage laeuft | Wartezustand, beide Wertzeilen jeder Karte |
| `—` | **nichts gemessen** — es gibt keine Zahl zu dieser Richtung, und es wird auch keine kommen | AK-49 (§3.7) und der Fehlerfall aus §6 |
| `no change` | **gemessen, und es kam nichts dabei heraus** | AK-42 (Bestand) |

- **`…` und nicht ein Wort.** Ein `working…` in der rechtsbuendigen,
  fettgesetzten Wertspalte einer 190 px breiten Karte (`CARD_WIDTH`,
  logische Pixel, Quelltext) waere breiter als jede
  Zahl, die dort je stehen wird, und wuerde die Spalte beim Eintreffen der
  Zahlen schmaler machen — eine Bewegung in 29 Karten gleichzeitig. Die Worte
  gehoeren in die Zusammenfassungszeile, wo Platz fuer sie ist und wo sie
  einmal statt 58-mal stehen.
- **A12 ist erfuellt, aber nicht vom Zeichen.** `…` nennt weder Einheit noch
  Geltungsbereich — es ist auch keine Zahl. Einheit und Geltungsbereich
  stehen in derselben Zeile, in der sie auch fuer die fertige Zahl stehen:
  die Beschriftung links (`Damage`, `Damage taken`) und der Bezugssatz in
  Zeile 3. Der Wartesatz aus §6 nennt den Slot ausdruecklich mit, damit der
  Geltungsbereich waehrend des Wartens nicht ausfaellt.
- **A7 ist erfuellt, weil der Platzhalter nichts behauptet.** Das war die
  Sorge des Auftrags („kein Platzhalter, der wie eine Aussage aussieht"). Ein
  `0`, ein `+0.0` oder ein leeres Feld waere eine; drei Punkte sind es nicht.
- **Der Name `PENDING` ist ein Codename, kein Anzeigetext.** Der `architect`
  hat ihn in W2 als Platzhalter benutzt und die Entscheidung mir ueberlassen:
  **die Konstante heisst weiter `PENDING`, der Text bleibt `…`.** W2 ist an
  der Konstante zu schreiben, nicht am Wort.

### 6. Der Wortlaut — vollstaendig, Englisch (A8)

Woertlich, damit nichts erfunden werden muss. Jeder dieser Texte ist
`Qt.PlainText`; jeder interpolierte Wert aus Save- oder Spieldateien laeuft
vorher durch `html.escape()` (AK-53 gilt unveraendert).

**(a) Zeile 3 waehrend des Wartens** — ersetzt **nur** den mittleren
Nebensatz, die Zeile behaelt Zaehlung, Favoritenhinweis und Rechtsklick-Satz:

```
29 of 29 relics  ·  working out what each is worth with Slot 3 empty  ·  right-click a relic to favourite it
```

Der wechselnde Nebensatz, isoliert:

| Zustand | Nebensatz |
|---|---|
| Warten | `working out what each is worth with <slot> empty` |
| Antwort da (Bestand, unveraendert) | `ranked against your build with <slot> empty` |

`<slot>` ist `slot.slot_name()`, dieselbe Quelle wie heute. Die beiden
Fassungen sind absichtlich gleich gebaut und fast gleich lang (mit
`Slot 3` eingesetzt: 48 gegen 43 Zeichen), damit die Zeile beim Wechsel nicht
umbricht.

**(b) Wertspalte waehrend des Wartens:** `…` — die Konstante `PENDING`,
unveraendert.

**(c) Kopfzeile waehrend des Wartens:** leer, keine.

**(d) Der Fehlerfall — die Frage ist gestellt worden und fehlgeschlagen.**
Den gibt es erst, seit die Rechnung in einer Spur laeuft (AD-028; heute kann
ein direkter Aufruf nur durchschlagen). Er darf **nicht** mit AK-49 verwechselt
werden — der Satz dort behauptet etwas ueber die **Spieldateien**, und das
waere bei einem Fehlschlag der Spur falsch (A7). Kopfzeile, woertlich:

```
Could not work out what these are worth — <reason>. They are in name order below.
```

`<reason>` ist der Grund, den die Spur meldet, escaped. Die Karten zeigen dann
`—` in beiden Wertzeilen, kein Chip, Namensordnung — dieselbe Darstellung wie
AK-49, aber mit dieser Kopfzeile statt jener. Der Satz folgt dem Hausmuster
der Advisor bar (`Could not work that out — {reason}.`).

**(e) Unveraendert und hier nur zur Vollstaendigkeit**, weil sie im
Wartezustand **nicht** erscheinen duerfen:

```
Nothing you own raises damage in this slot.
Nothing you own raises survival in this slot.
The game's data carries no figures this goal can be ranked on, so these relics are in name order.
```

### 7. Token

**Kein neuer Farbwert, keine neue Schriftgroesse, kein neues Widget.** Der
Wartesatz steht in derselben Zusammenfassungszeile wie heute (`MUTED`, 11 px);
`…` steht in derselben Wertzeile wie die Zahl, die es ersetzt (fett, 12 px).
Die Kopfzeile des Fehlerfalls benutzt das vorhandene `headline`-Label.

Das ist die Begruendung, aus der der ganze Entwurf haengt: **weil kein Element
dazukommt und keines verschwindet, braucht es keine Zeitschwelle** — und ohne
Zeitschwelle ist die Vorgabe ohne Wanduhr pruefbar.

### 8. Akzeptanzkriterien (ab AK-197)

Pruefbar, binaer, an **Zustaenden** festgemacht und nicht an Millisekunden
(Vorgabe 7 des Auftrags). „Eine Spur, die nie antwortet" und „eine Spur, die
sofort antwortet" sind die beiden Vorrichtungen, mit denen fast alles davon
zu stellen ist.

- **AK-197** *(zwei Anstriche, nicht drei.)* Je Oeffnung des Pickers gibt es
  hoechstens zwei Zustaende der Anzeige: ohne Antwort und mit ihr. Alles, was
  an der Antwort haengt — die Zahlen beider Wertzeilen, die `BEST FOR …`-Chips,
  die Kartenordnung samt AK-195-Vorziehung, die Kopfzeile und die
  Laufbefundzeile — wechselt gemeinsam. Es gibt keinen Zwischenzustand, in
  dem eine Karte eine Zahl traegt und eine andere `…`, oder in dem die
  Ordnung sortiert ist und die Zahlen fehlen.
  *Toetende Mutation:* Zahlen und Ordnung in zwei Schritten setzen.
- **AK-198** *(der erste Anstrich behauptet nichts.)* Wird der Picker mit
  einer Spur geoeffnet, die nie antwortet, so gilt dauerhaft: beide
  Wertzeilen **jeder** Karte tragen `…`; **keine** Karte traegt einen
  `BEST FOR …`-Chip; **keine** Karte ist vorgezogen; die Kopfzeile ist leer;
  und der Dialog steht bedienbar (Filter, `Sort by`, Bildlauf, Auswahl einer
  Karte). Dies ist der Waechter **W2** aus AD-028.
  *Toetende Mutation:* die Rechnung wieder synchron vor dem Oeffnen — die
  Karten tragen Zahlen. Kein Zeitmass.
- **AK-199** *(die Ordnung ohne Antwort ist die beraterfreie.)* Im Zustand
  aus AK-198 steht das Raster in der Ordnung „Favoriten, dann Name" — Karte
  fuer Karte dieselbe Liste wie bei `Sort by` = `Name` im selben Zustand. Die
  `Sort by`-Auswahl selbst steht dabei unveraendert auf der gewaehlten
  Zielrichtung und wird nicht umgestellt.
- **AK-200** *(die Zusammenfassungszeile behauptet keine Rangfolge, die es
  nicht gibt.)* Solange die Zahlen fehlen, traegt Zeile 3 den Nebensatz
  `working out what each is worth with <slot> empty`; der Nebensatz
  `ranked against your build with <slot> empty` erscheint **nicht**, bevor
  die Zahlen auf den Karten stehen. Die Zeile hat in beiden Zustaenden
  dieselbe Anzahl gezeichneter Zeilen am Standardmass des Pickers — gemessen,
  mit Umgebung genannt (L-009); ist sie es nicht, wird die **Warte**fassung
  gekuerzt, nicht die fertige.
- **AK-201** *(die Pflichtzeilen warten nicht.)* Im Zustand aus AK-198 stehen
  die beiden Textzeilen aus §3.2 vollstaendig: die Pflichtzeile
  `One slot at a time — …` und die `scope`-Saetze der gewaehlten
  Zielrichtung, sichtbar, ungekuerzt, nicht elidiert (AK-50 gilt ab dem
  ersten Anstrich). Einzige Anzeige ueber dem Raster, die auf die Antwort
  warten darf, ist die Laufbefundzeile (3b).
  *Toetende Mutation:* das heutige Ausblenden beider Zeilen bei fehlender
  Rangfolge stehen lassen.
- **AK-202** *(nichts erscheint, nichts verschwindet, nichts ist gesperrt.)*
  Zwischen dem ersten und dem zweiten Anstrich kommt kein Widget hinzu und
  faellt keines weg — kein Fortschrittsbalken, kein Wartetext als eigene
  Zeile, kein Wartecursor, kein zweiter Dialog, kein deaktiviertes
  Bedienelement, keine Zeitschwelle und kein Verzoegerungstimer. **Ersetzt
  AK-09 und AK-10 fuer den Picker**, nicht fuer die Advisor bar.
- **AK-203** *(die Antwort bewegt nur, was sie bewegen muss.)* Ueber den
  Wechsel vom ersten zum zweiten Anstrich hinweg sind identisch: der
  Bildlaufwert der `QScrollArea`, die Aussenmasse des Dialogs und die Hoehe
  jeder einzelnen Karte (AK-41). Das Bedienelement mit dem Tastaturfokus
  behaelt ihn; lag er auf einer Reliktkarte, liegt er danach auf der Karte
  desselben Relikts.
  *Toetende Mutation:* das Raster nach der Umsortierung nach oben scrollen
  lassen; den Fokus nicht wiederherstellen.
- **AK-204** *(der Zielrichtungswechsel wartet nicht.)* Steht eine Antwort,
  und der Spieler wechselt `Sort by` zwischen den beiden Zielrichtungen, so
  traegt zu **keinem** Zeitpunkt eine Karte `…`, und Zeile 3 traegt zu keinem
  Zeitpunkt den Wartesatz. Ordnung, Chips, Kopfzeile und `scope`-Saetze
  wechseln in einem Anstrich.
  *Toetende Mutation:* beim Wechsel erneut fragen.
- **AK-205** *(gezeichnet wird die gewaehlte Richtung, nicht die sortierte.)*
  Die Richtung, in der Wertspalten, Chips, Kopfzeile und `scope`-Saetze
  gezeichnet werden, ist die eine Zieleinstellung des Programms (AK-43) und
  **nicht** `SlotPool.rank_by`. Aufbau: eine Antwort, die fuer die eine
  Richtung sortiert wurde, wird in der anderen gelesen — Chips und Ordnung
  gehoeren zur gelesenen.
  *Toetende Mutation:* die Richtung aus `pool.rank_by` nehmen.
- **AK-206** *(eine Frage je Oeffnung.)* Vom Oeffnen bis zum Schliessen
  erreicht die Spur hoechstens **eine** Anfrage. Filtern, Bildlauf,
  Favoritenvergabe, ein Wechsel der Zielrichtung und ein Wechsel auf `Name`
  loesen keine weitere aus. Wechselt der Spieler die Richtung, waehrend die
  Antwort noch aussteht, wird weder neu gefragt noch der Wartezustand neu
  begonnen; die eintreffende Antwort wird in der dann gewaehlten Richtung
  gezeichnet.
  *Toetende Mutation:* im offenen Dialog ein zweites Mal fragen.
- **AK-207** *(die ueberholte Antwort erreicht nichts.)* Wird der Picker
  geschlossen, waehrend eine Antwort unterwegs ist, schliesst er sofort; die
  spaeter eintreffende Antwort fasst kein Widget an, wirft nichts und
  veraendert die Slot-Belegung nicht. Eine im Wartezustand ausgewaehlte Karte
  wird uebernommen wie sonst auch. Zusammen mit **W3** aus AD-028.
- **AK-208** *(der Fehlschlag hat seinen eigenen Satz.)* Meldet die Spur
  einen Fehlschlag, steht in der Kopfzeile woertlich
  `Could not work out what these are worth — <reason>. They are in name order below.`;
  die Karten tragen `—`, keinen Chip, und stehen in Namensordnung. Der Satz
  `The game's data carries no figures …` erscheint in diesem Fall **nicht**.
  *Toetende Mutation:* den Fehlschlag auf den AK-49-Satz abbilden.
- **AK-209** *(drei Zeichen, drei Aussagen, nie vertauscht.)* `…`, `—` und
  `no change` bedeuten „laeuft noch", „nicht gemessen" und „gemessen, ohne
  Wirkung" und stehen nie fuereinander: keine Karte zeigt `…`, nachdem ihre
  Zahlen eingetroffen sind; keine Karte zeigt `—` oder `no change`, solange
  die Frage laeuft.
- **AK-210** *(die Zusagen des Bestands ueberleben den Umbau.)* Nach dem
  zweiten Anstrich gilt unveraendert: AK-41 (0 px Hoehenunterschied), AK-42
  (beide Richtungen auf jeder Karte), AK-44 (keine Ordnungszahl; zweimal
  derselbe Zustand ergibt zweimal dieselbe Reihenfolge — gemessen am
  **zweiten** Anstrich, denn der erste ist keine Rangfolge), AK-45, AK-46,
  AK-50, AK-52 und AK-195/AK-196.

### 9. Ausdruecklich **nicht** Teil dieser Vorgabe

- **Die Modalitaet des Pickers.** Sie bleibt, wie sie ist. Diese Vorgabe
  ruehrt nicht daran — sie **stuetzt sich** darauf (§2, §4). Wollte jemand den
  Dialog nichtmodal machen, faellt die Begruendung „eine Frage je Oeffnung"
  weg, und die Frage geht an den `architect`, nicht in diese Datei.
- **Wie die Spur gebaut ist.** Zweite Instanz, Entprellung, Cachegroesse,
  Generationszaehler, Abhaengigkeitsrichtung — alles AD-028, alles
  `architect`.
- **Der `Optimize`-Weg.** Er hat seinen Wartezustand (AK-09 bis AK-11), und
  dieser Abschnitt aendert ihn nicht.
- **`inventory.load` und der Erststart** (AD-029 Stufe B). Faellt die Stufe,
  braucht das Fenster einen dritten Zustand („wird gelesen"); das ist eine
  eigene Vorgabe und nicht diese.
- **Der Satz fuer „kein Spielstand" im Picker.** Heute zeigt der Picker den
  AK-49-Satz ueber die **Spieldateien** auch dann, wenn der wirkliche Grund
  „es wurde kein Spielstand gelesen" ist (Quelltext: `asking_from` gibt
  `None` fuer „kein Save", `_say_what_they_are_worth` bildet das auf
  `NO_FIGURES_AT_ALL` ab). Das ist ein A7-Bruch, aelter als AD-028 und **kein
  Teil dieses Auftrags**; er ist im Bericht als Befund an den `director`
  gemeldet, mit fertigem Wortlaut. Hier steht er nur, damit ihn niemand
  versehentlich als von AK-208 erledigt ansieht — das ist er nicht.
- **Die uebrigen Tabs, die Streichliste aus §8, A16/A17.** Unberuehrt.

### 10. Offene Fragen an den App Designer

- **F-P (Bewegung gegen fruehe Inhalte).** Diese Vorgabe zeigt die Karten
  sofort und ordnet sie rund ein Drittel einer Sekunde spaeter einmal um. Die
  Gegenoption waere ein leeres Raster, bis die Zahlen da sind: **gar keine
  Bewegung**, dafuer eine drittel Sekunde ohne Namen, ohne Filtertreffer und
  ohne Dialoggroesse. **Empfehlung: so wie hier vorgegeben** — die Namen
  haengen am Berater nicht, und wer ein bestimmtes Relikt sucht, braucht die
  Zahlen nie. Der App Designer hat den Picker am laufenden Fenster gesehen und
  ist der Einzige, der weiss, wie er ihn benutzt; wenn ihn Bewegung mehr
  stoert als Warten, ist das eine Zeile.
- **F-Q (`Sort by` beim Durchtippen).** Der Zielrichtungswechsel kostet nach
  §4 nichts mehr. Damit ordnet sich das Raster bei jedem Schritt durch die
  `Sort by`-Liste sofort um — mit Pfeiltasten also auch fuer die Eintraege,
  bei denen der Spieler gar nicht stehen bleiben will. **Empfehlung: so
  lassen** (sofort ist ehrlicher als „erst bei Enter", und es kostet nichts).
  Reine Geschmacksfrage, deshalb hier.
