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

#### 3.8 Warten

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

`Optimize` ist der heutige `Suggest`-Knopf der Advisor bar (§3.1 oben),
umbenannt. Er bleibt in der mittleren Spalte des Build planner, ueber den
Slots, ausserhalb der `QScrollArea`.

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
