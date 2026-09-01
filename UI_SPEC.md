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
ADVISOR  [ Maximise damage   v ]  [ Suggest ]   <status …>   [ Apply all ] [ Why ] [ Clear ]
```

- `ADVISOR` in der Schrift von `app._heading` (8 pt, fett, +1.2 Sperrung,
  `MUTED`), inline statt als Blockzeile.
- Zielwahl: `QComboBox`, `setSizeAdjustPolicy(AdjustToContents)`,
  `setMaximumWidth(200)`. Eintraege in dieser Reihenfolge:
  `Maximise damage`, `Minimise damage taken`. Bewusst eine Combobox und nicht
  zwei Knoepfe, damit weitere Ziele ohne Layoutaenderung dazukommen koennen.
- `Suggest`: `QPushButton`. Waehrend der Rechnung traegt derselbe Knopf
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
| 4.1 | Ruhe, nie gerechnet | `Nothing suggested yet.` | Tooltip auf `Suggest`: `Fills every slot from the relics in your save. Nothing changes until you apply it.` |
| 4.2 | Rechnet, < 250 ms | *nichts* | keine Progressanzeige, kein Aufblitzen |
| 4.3 | Rechnet, ≥ 250 ms | `Working out maximise damage…` | Progressbar sichtbar, `Suggest` heisst `Cancel` |
| 4.4 | Rechnet, ≥ 3 s | `Working out maximise damage — 292 relics, 6 slots.` | Zahlen nur, wenn der Scorer sie liefert; sonst bleibt 4.3 stehen |
| 4.5 | Abgebrochen | `Stopped. Nothing was changed.` | Vorschlagsbloecke verschwinden |
| 4.6 | Ergebnis | `Maximise damage — 6 of 6 slots filled.` | Vorschlagsbloecke in allen Slots; `Apply all` / `Why` / `Clear` |
| 4.7 | Ergebnis veraltet (Nightfarer, Vessel, Deep, Level oder eine Slot-Belegung hat sich waehrend der Rechnung geaendert) | `Your build changed while this was working out. Suggest again.` | Ergebnis wird **verworfen**, nicht angezeigt |
| 4.8 | Kein Save gelesen (`owned is None`) | `No save was read, so there are no relics to choose from — use Rescan save.` | Zielwahl und `Suggest` deaktiviert |
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

1. **Nichts aendert sich ohne Zustimmung.** `Suggest` schreibt in keinen Slot.
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
7. **Tab-Reihenfolge**: Zielwahl → `Suggest`/`Cancel` → `Apply all`/`Undo
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
  und `Suggest` traegt `Cancel`.
- **AK-11** `Cancel` fuehrt binnen 200 ms nach dem Klick sichtbar in Zustand
  4.5, auch wenn der Arbeiter laenger zum Beenden braucht.
- **AK-12** Aendert sich Nightfarer, Vessel, Deep of Night, Level oder eine
  Slot-Belegung waehrend der Rechnung, wird das Ergebnis verworfen und 4.7
  angezeigt. Es wird nie ein Vorschlag zu einem Zustand gezeigt, der nicht mehr
  gilt.
- **AK-13** `Suggest` veraendert keinen Slot: nach `Suggest` ohne Anwenden sind
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

- **AK-25** Jede Aktion des Beraters (Zielwahl, Suggest, Cancel, Apply all, Use
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
