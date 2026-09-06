# T-071 — developer

```
STATUS: erledigt
AUFTRAG: T-071 — Bedienbarkeit ueber die Bedienungshilfen (QA-161), Startbreite,
         zweite Instanz (QA-163), Zeigermarke (QA-164)
GELESEN: GOAL.md · docs/state.md · docs/plan-restarbeiten.md (Regeln) ·
         docs/berichte/T-070-qa-engineer.md (vollstaendig) ·
         docs/berichte/T-068-developer.md · qa/findings.md (QA-157, QA-161 bis
         QA-164) · UI_SPEC.md (AK-05, AK-71, AK-77) · CLAUDE.md ·
         nrplanner/{app,bosstab,cardgrid,chalices,effectstab,favourites,
         relicpicker,weaponslots}.py · tests/{conftest,rendered,
         test_nightlord_selection,test_differential_track}.py ·
         scripts/differential/mutate.py · scripts/make_screenshots.py ·
         .claude/agent-memory/developer/ (alle Eintraege).
         Keine Auftragsdatei docs/tasks/T-071.md vorhanden — der Auftragstext
         des Directors ist die Quelle.
GEÄNDERT: nrplanner/pressable.py (neu) · nrplanner/singleinstance.py (neu) ·
         nrplanner/bosstab.py · nrplanner/app.py · nrplanner/effectstab.py ·
         scripts/differential/mutate.py · tests/test_card_is_pressable.py (neu) ·
         tests/test_pointer_mark_follows_the_layout.py (neu) ·
         tests/test_opening_width.py (neu) · tests/test_single_instance.py (neu) ·
         docs/screenshots/2026-09-06-T071/ (zwei Bilder, neu) ·
         docs/berichte/T-071-developer.md (diese Datei).
         Sechs Commits, ab1eab3 bis 3a8dd9b auf `docs/audit-and-advisor-design`.
         Kein push/pull/fetch/merge/rebase/checkout/branch/reset/revert/stash.
         Fremde ungespeicherte Dateien (UI_SPEC.md, docs/plan-restarbeiten.md,
         docs/state.md, qa/findings.md, die Berichte anderer Rollen,
         docs/tasks/T-067.md) sind unveraendert und ungestaged geblieben.
ANNAHMEN: (1) Der Fokusrahmen darf der des Stils sein — der Auftrag verlangt
         Tastaturbedienung, sagt aber nichts ueber ihre Sichtbarkeit, und eine
         vierte eigene Farbe waere eine Gestaltungsentscheidung. Abweichung
         unten an den ui-ux-designer. (2) "Startbreite" heisst Breite; die
         Hoehe bleibt bei 860 (AK-71 unberuehrt). (3) Der Zugriff auf die
         Bedienungshilfen-Schnittstelle geht ueber Qts eigene Bruecke; ein
         echter Bildschirmleser ist damit nicht geprueft, nur ein UIA-Klient.
NÄCHSTER: qa-engineer
BLOCKIERT DURCH: nichts
```

---

## 0. Messumgebung — jede Zahl unten gilt hierfuer (L-009)

| | |
|---|---|
| Betriebssystem | Windows 10 Home 19045 |
| Qt-Plattform | **`windows`** fuer alle Handpruefungen und beide Bilder; **`offscreen`** fuer die Suite. Beide ausgelesen ueber `qapp.platformName()` |
| Stil / Palette | **`fusion`** + dunkle Palette, ueber `appmod.apply_appearance(qapp)` — derselbe Aufruf, den `main()` macht |
| Skalierung | **150 %**, `devicePixelRatio` **1.5**, `QT_SCALE_FACTOR` nicht gesetzt |
| Bildschirm | **1 707 x 1 067 logische px** (verfuegbar 1 707 x 1 027), **2 560 x 1 600 physisch**. Unter `offscreen`: 800 x 800 logisch, dpr 1.0 |
| Schrift | `Segoe UI 9` unter `windows`, `Sans Serif 9` unter `offscreen` — die beiden sind der Grund, warum unten keine Zahl fest im Code steht |
| Einheiten | Alle Zahlen sind **logische** px, ausser wo ausdruecklich "physisch" steht |
| Datensatz | `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`, `extract_version` **11** = `extract.EXTRACT_VERSION` **11** |
| Einstellungen | Handpruefungen in eigenen Speichern `DankYeeterProbe/<zweck>`; die Suite in `DankYeeterTests-<pid>`. Der Nutzerspeicher `DankYeeter/NightreignHelper` wurde in diesem Lauf **nie** beschrieben |
| Fenster | Wo eine Fensterbreite genannt ist, hat `win.width()` sie **erreicht**; sonst steht es als nicht erreicht da |

**Suite:** `-m "not slow"` **860 passed, 9 skipped, 5 deselected** in 433,28 s
(vorher 815/9/5) · `-m "slow"` **5 passed, 869 deselected** in 49,41 s.

---

## 1. Umgesetzt

### QA-161 — eine Nightlord-Karte ist ohne Maus bedienbar

**Neu: `nrplanner/pressable.py`.** `PressableFrame` gibt einer Karte alle vier
Dinge auf einmal, weil der Befund nicht war, dass einer Karte eines davon
fehlte, sondern dass einer ganzen Kartenform alle vier fehlten:

- **einen Namen** (`setAccessibleName`) und eine Beschreibung,
- **die Rolle `Button`** statt `Border` — ueber eine `QAccessibleWidget`-
  Ableitung (`CardAccessible`), die ueber eine Fabrik registriert wird. Die
  Fabrik installiert sich im Konstruktor selbst, damit kein Einstiegspunkt sie
  vergessen kann,
- **eine echte Zugriffsaktion `Press`**, die auf `press()` geht — dieselbe
  Methode, die `mousePressEvent` aufruft. Der Ausloeser haengt damit an
  derselben Stelle wie der Mausklick, nicht daneben,
- **Tastatur**: `Qt.StrongFocus` (Tab-Reihenfolge) und `keyPressEvent` fuer
  Return, Enter und Leertaste, plus den Fokusrahmen des Stils in `paintEvent`.

`bosstab.BossCard` erbt davon und implementiert `press()` (`clicked.emit`).
`mousePressEvent` ist entfallen — es gibt jetzt genau einen Weg nach innen.

**Nachweis am laufenden Fenster** (`windows`, Fusion, 150 %, .NET
`UIAutomationClient` ueber PowerShell, wie in T-070):

```
window: Nightreign Helper 1.7.1
elements: 90
named Fulghor: type=ControlType.Button class=BossCard invoke=2
named Fulghor: type=ControlType.Text  class=QLabel   invoke=1
INVOKE_OK
detail panel after Invoke: 'Fulghor'
```

Vorher (T-070, derselbe Weg): die Karte war `ControlType.Custom` **ohne Namen**,
`Invoke` meldete `INVOKE_OK` und die Detailtafel blieb auf
`Select a Nightlord`. Das Urteil kommt aus dem Zustand, den das Programm selbst
fuehrt, nicht aus dem Rueckgabewert — genau darum, weil der Rueckgabewert das
war, was gelogen hat.

### Startbreite — aus den Spaltenbreiten abgeleitet

**`EffectTable.width_for_full_headings()`** (in `effectstab.py`) gibt die
schmalste Sichtbereichsbreite, bei der die Kopfzeile so gut liest, wie sie
ueberhaupt lesen kann. Hergeleitet, nicht gewaehlt:

1. `_label_room(column, section)` nimmt jetzt eine Schnittbreite entgegen, so
   dass derselbe Stil, mit demselben Sortierpfeil, zu einer *hypothetischen*
   Breite befragt werden kann.
2. `headings_as_drawn(widths)` gibt die Kopfzeile, wie sie bei diesen
   Spaltenbreiten gezeichnet wuerde — durch dieselbe `elidedText`-Regel, die
   `_elide_headings` anwendet. Eine Regel, zwei Aufrufer.
3. `width_for_full_headings()` startet bei der breitesten Breite, die die
   Tabelle je annimmt (beide Boeden plus was jede andere Spalte, gedeckelt,
   verlangt) und geht **pixelweise zurueck, solange die Kopfzeile Wort fuer
   Wort gleich bleibt**.

Das Ergebnis ist **in beide Richtungen dicht**: ein Pixel breiter bringt dem
Leser nichts, ein Pixel schmaler nimmt ihm etwas weg. Beides steht als
Waechter.

**`Planner.showEvent`** setzt die Groesse auf dem Weg zum Schirm, und nur wenn
`WA_Resized` nicht gesetzt ist — Qt schickt das Show-Ereignis, **bevor** es das
Fenster abbildet, also blinkt nichts, und ein Aufrufer, der selbst eine Breite
gesetzt hat, behaelt sie. `self.resize(1320, 860)` in `__init__` ist entfallen.

**`_width_around_the_effect_table()`** rechnet die Fensterbreite aus. **Jeder
Term ausser dem Seiteneinzug kommt aus einem Stil oder einem Layout, nicht aus
einem gelayouteten Rechteck** — siehe Abschnitt 3, das war ein Fehler, den erst
die Handpruefung gefunden hat.

Zwei Schranken danach: der verfuegbare Schirm, dann die Mindestbreite des
Fensters (760 auf Windows, unveraendert).

**Gemessen (Windows, Fusion, 150 %, `Segoe UI 9`, Datensatz oben):**

| | vorher | jetzt |
|---|---|---|
| Fenster beim ersten Oeffnen | 1 320 x 860 | **1 350 x 860** |
| Sichtbereich der Effekttabelle | 1 272 | **1 302** |
| gekuerzte Ueberschriften | 1 (`Comes with c…`) | **0 von 11** |

Herleitung der 1 350 (L-001): `width_for_full_headings()` **1 302** + 2
(Tabellenrahmen, `frameWidth` 1 je Seite) + 14 (`verticalScrollBar().sizeHint()`)
+ 28 (Layoutraender des Tabs, 14 je Seite) + 4 (Seiteneinzug des `QTabWidget`,
2 je Seite) = **1 350**. Die 1 302 sind ihrerseits gemessen dicht: bei 1 301
kuerzt sich `Comes with curse`.

Unter `offscreen` sagt dieselbe Rechnung **1 650**, und das Fenster oeffnet
trotzdem bei 988 — der Schirm der Plattform ist 800 px breit und der
Fensterboden 988. Das ist die Schranke, die greift, und sie ist richtig so.

Bild: `docs/screenshots/2026-09-06-T071/effects-01-opening-width-every-heading-whole.png`.

### QA-163 — zweite Instanz

**Neu: `nrplanner/singleinstance.py`.** `RunningCopy` haelt einen benannten
`QSharedMemory`-Bereich. Wer ihn anlegen kann, ist die laufende Kopie und
schreibt sein Fenster-Handle hinein; wer ihn schon vorfindet, liest das Handle,
holt jenes Fenster nach vorn (`ShowWindow`/`SetForegroundWindow` ueber
`ctypes`, in einer eigenen Funktion und nur dort) und beendet sich.

Warum das Handle und nicht der Fenstertitel: **zwei Kopien tragen denselben
Titel**, ein Klient koennte sie nicht auseinanderhalten. Warum Shared Memory:
Windows gibt den Bereich frei, wenn der letzte Halter geht — auch beim Absturz,
also sperrt eine abgestuerzte Kopie die naechste nicht aus.

`main()` nimmt den Anspruch **vor** `firstrun.ensure_data`, vor dem Laden der
Daten und vor jedem Fenster. Eine zweite Kopie, die bis dahin kaeme, haette
schon die Dateien des Spielers angefasst.

Jeder Fehlschlag ausser "gibt es schon" wird mit Starten beantwortet — ein
Programm, das nicht startet, weil ein Shared-Memory-Bereich nicht angelegt
werden konnte, waere ein schlimmerer Fehler als der verhinderte.

**Handpruefung, ganzer Weg:**

```
first copy claimed: True
first copy window handle: 0x14004e6  pid 12924
second copy exit code: 0
foreground handle after the second copy: 0x14004e6 -- is the first copy's window: True
windows still open for this process: 1
```

Die zweite Kopie ist das echte `run.py`, so gestartet, wie eine Verknuepfung es
startet. Sie oeffnet kein Fenster, endet mit 0, und danach ist das Fenster der
ersten Kopie im Vordergrund.

### QA-164 — die Zeigermarke

Die Marke wird jetzt aus der tatsaechlichen Zeigerposition neu bestimmt, wo
immer sich die Geometrie ohne Zeigerereignis aendert:

- `BossCard.moveEvent`, `resizeEvent`, `showEvent` → `follow_the_pointer()`,
- `BossTab`: `scroll.verticalScrollBar().valueChanged` → alle Karten neu.
  **Das Scrollen kann keine Karte fuer sich bemerken**: der Halter bewegt sich,
  die Karten behalten ihren Platz darin, also bekommt keine ein Move-Ereignis.

`_pointer_is_here()` fragt `QApplication.widgetAt(QCursor.pos())` — die Frage,
um die es geht, und sie bringt Beschneidung und Fensterstapel mit: eine
weggescrollte oder von einem fremden Fenster verdeckte Karte beansprucht den
Zeiger nicht.

Gemessen, `offscreen`, Fenster 1 250 → 900 px, Zeiger unbewegt:
`hovered` geht von `['Libra']` auf `['Maris']`, und `Maris` ist geometrisch die
Karte unter dem Zeiger. Nach dem Scrollen: `['Libra']` → `['Harmonia']`,
geometrisch bestaetigt. Beim Zurueckwechseln auf den Reiter mit ruhendem
Zeiger: `[]` → `['Libra']`.

**Der Scroll-Fall stand nicht im Befundtext** (QA-164 nennt Umbruch und
"Karte erscheint"). Ich habe ihn mitgemacht, weil er dieselbe Wurzel und
dieselbe Aussage betrifft ("hier steht dein Zeiger") und das
Abnahmekriterium des Befunds sonst nicht haelt. Er ist ein eigener Waechter und
eine eigene toetende Mutation.

---

## 2. L-006-Durchgang: dieselbe Eigenschaft, mit Trefferzahlen

Gesucht wurde die **Eigenschaft**, nicht die Fundstelle: *eine Flaeche, die
anklickbar aussieht, deren einziger Ausloeser die Maus ist, und die ohne Namen,
ohne Rolle, ohne Tab-Stopp und ohne Zugriffsaktion dasteht.*

**Maske 1 — Quelltext, Mausbehandlung.**
`def mousePressEvent|def mouseReleaseEvent|def mouseDoubleClickEvent|mousePressEvent =`
ueber `nrplanner/` → **6 Treffer**: `app.py:201`, `bosstab.py:421`,
`relicpicker.py:136`, `relicpicker.py:210`, `weaponslots.py:200`,
`weaponslots.py:206`.

**Maske 2 — Quelltext, "sieht anklickbar aus".** `PointingHandCursor` ueber
`nrplanner/` → **7 Treffer**: `app.py:204`, `app.py:1338`, `bosstab.py:320`,
`relicpicker.py:57`, `relicpicker.py:162`, `relicpicker.py:253`,
`weaponslots.py:180`. (Unabhaengig von Maske 1: sie findet `app.py:1338`, das
Maske 1 nicht hat, und uebersieht `weaponslots.py:206`.)

**Maske 3 — am laufenden Programm.** Jedes Widget mit Zeigerhand ueber alle
sieben Reiter und den Relikt-Waehler, gefragt ueber
`QAccessible.queryAccessibleInterface`: Rolle, Name, Fokusregel, Aktionen.
**395 Widgets** insgesamt. Davon tragen **61** die Eigenschaft:

| Ort | Anzahl | Rolle | Name | Fokus | Aktionen |
|---|---|---|---|---|---|
| `weaponslots.WeaponTile` (`weaponslots.py:200`) | **6** | `Border` | `''` | `NoFocus` | keine |
| `relicpicker.RelicCard` (`relicpicker.py:136`) | **54** | `Border` | `''` | `NoFocus` | keine |
| `relicpicker.CustomRelicCard` (`relicpicker.py:210`) | **1** | `Border` | `''` | `NoFocus` | keine |
| `bosstab.BossCard` **nach dieser Aenderung** | 10 | `Button` | der Nightlord | `StrongFocus` | `Press`, `SetFocus` |

**Was ich nicht mitbehoben habe, und warum es eine andere Aenderung waere:**

- **`RelicCard` (54) und `CustomRelicCard` (1).** Die Karte ist unerreichbar,
  **aber in ihr sitzt ein echter `QToolButton`**: Rolle `Button`, `TabFocus`,
  `Press`+`SetFocus` — gemessen, 54 + 1 Stueck. Diesen Karten fehlt also nicht
  der Ausloeser, sondern der **Name** (der Knopf ist reines Symbol, `Name` ist
  `''` bei 54 von 55; nur der `+`-Knopf heisst `'+'`). Die Karte selbst
  drueckbar zu machen, verdoppelt die Tab-Stopps im Waehler von 55 auf 110 —
  das ist eine Gestaltungsfrage, keine Wiederholung derselben Aenderung.
  **Empfehlung:** dem Knopf den Reliktnamen geben (`setAccessibleName`), eine
  Zeile, mit einem Waechter; Entscheid ueber die Tab-Stopps beim
  `ui-ux-designer`.
- **`WeaponTile` (6).** Gleiche Form wie `BossCard`, aber **drei Gesten**:
  Linksklick macht die Kachel aktiv, Rechtsklick leert sie, Doppelklick oeffnet
  den Waffendialog. Eine einzelne `Press`-Aktion kann nur eine davon sein, und
  die wichtigste (den Dialog oeffnen) ist gerade nicht die Linksklick-Geste.
  Das braucht eine Entscheidung, welche Aktion `Press` ist und ob es eine
  zweite Zugriffsaktion gibt — anderer Zuschnitt, deshalb gemeldet.
- **`app.py:201`** (`self.title.mousePressEvent = lambda ...` in
  `SituationalRow`) ist ein **anderer Fall**: das Label doppelt eine `QCheckBox`,
  und die ist von Haus aus tastatur- und schnittstellenbedienbar. Zu pruefen
  waere dort ihr Name, nicht ihr Ausloeser. **Nicht gemessen:** im
  Ausgangszustand des Programms existiert kein `SituationalRow` (0 Instanzen im
  Standardaufbau), der Quelltext-Treffer steht also, eine Laufzeitmessung habe
  ich nicht.
- **`relicpicker.py:253`** ist ein echter `QToolButton` im Favoritenmenue mit
  Tooltip-Namen; Menues sind von Haus aus tastaturbedienbar. Kein Treffer der
  Eigenschaft.
- **`app.py:1338`** ist der Start-Menue-Knopf, ein `QToolButton`. Kein Treffer.

---

## 3. Was schiefging und wie es gefunden wurde

Drei Sachen sahen richtig aus und waren es nicht. Alle drei hat **nicht** die
gruene Suite gefunden.

**(a) Die Startbreite haing davon ab, welcher Reiter vorn war.** Gefunden von
Hand am laufenden Fenster: das Programm startet auf `Build planner`, und ein
Reiter, der nicht vorn ist, hat nie die Breite einer Seite bekommen — seine
Tabelle meldet 640 px und ihr Sichtbereich 638, also 2 px "Rahmen" statt der
16, die sie hat (die Bildlaufleiste steht noch nicht). Gemessen: **1 350 px mit
dem Effekte-Reiter vorn, 1 802 px — vom Schirm auf 1 707 gekappt — mit dem
Build planner vorn, aus demselben Code.** Alle meine Faelle oeffneten zuerst den
Effekte-Reiter und waeren auf beiden gruen gewesen. Behoben, indem jeder Term
ausser dem Seiteneinzug aus Stil oder Layout kommt; eigener Fall
(`test_the_opening_width_does_not_depend_on_which_tab_is_in_front`) und eigene
Mutation.

**(b) Zwei Gegenbauten haben ueberlebt, weil sie nichts aendern** (L-008 c).
`pointer-mark-that-waits-for-the-pointer` (nur `moveEvent`) und
`pointer-mark-missing-on-a-card-that-appears` (nur `showEvent`) liefen beide
**gruen** — `3 passed in 7,3 s` bzw. `7,5 s`. Grund: die drei Ereignisse
ueberlappen bei jedem Umbruch, den die Suite herstellen kann, also ist keines
davon fuer sich noetig. Ich habe **die drei Haken behalten** (sie decken
prinzipiell verschiedene Ereignisse: eine Verschiebung ohne Groessenaenderung,
ein Erscheinen ohne beides) und die beiden Registereintraege durch einen
mechanismusgebundenen ersetzt — `pointer-mark-left-to-enter-and-leave`, der
`follow_the_pointer` selbst stilllegt und **alle drei** Faelle rot macht.
**Das ist ein Befund und keine stille Nachbesserung:** wer die Haken einzeln
anfasst, bekommt von der Suite kein Signal. Wenn der `director` sie auf einen
reduzieren will, ist das eine Vereinfachung, die ich nicht eigenmaechtig mache.

**(c) Ein Gegenbau ueberlebte, weil der Fall sich selbst uebersprang.**
`opening-size-that-overrules-the-caller` lief gruen: der Fall las die Breite
**nach** `show()`, und eine ueberschriebene Breite sieht genau aus wie eine
Plattform, die die verlangte Breite nicht gibt — also `skip` statt `fail`.
Die Pruefung steht jetzt **vor** `show()`, wo sie eine Aussage ueber das Layout
ist und nicht ueber das Ergebnis. Danach toetet die Mutation.
(Derselbe Griff, den mein Gedaechtnis unter "Skip-Label statt Signal" fuehrt —
er hat trotzdem wieder zugeschlagen.)

**Eine vierte Falle, die auffiel und keine Aenderung brauchte:** der
Fokusrahmen von Fusion wird **nur** gezeichnet, wenn das Fenster
`WA_KeyboardFocusChange` traegt, also nach einer Tastatur-Fokusaenderung. Ein
Fall, der `setFocus()` aufruft, misst deshalb nichts. Der Fall drueckt jetzt
Tab und laesst Qt den Fokus setzen — was zugleich das Verhalten ist, das ein
Leser hat.

---

## 4. Tests

**Neu, 45 Faelle** (860 gegen vorher 815):

| Datei | Faelle | was sie behaupten |
|---|---|---|
| `tests/test_card_is_pressable.py` | 10 | Name, Rolle `Button`, `Press` bewegt die Detailtafel, jede angekuendigte Taste drueckt wirklich, Tab erreicht die naechste Karte, eine Nicht-Drueck-Taste tut nichts, der Fokus ist am Bild sichtbar und genau eine Karte aendert sich |
| `tests/test_pointer_mark_follows_the_layout.py` | 3 | Umbruch, Scrollen, Karte erscheint — die Marke steht, wo der Zeiger steht |
| `tests/test_opening_width.py` | 7 | die abgeleitete Breite ist in beide Richtungen dicht; das Fenster oeffnet so breit, dass mehr Breite nichts brachte; unabhaengig vom vorderen Reiter; nicht breiter als der Schirm; nie unter dem Layout-Minimum; `showEvent` setzt sie; ein Aufrufer, der eine Groesse gesetzt hat, behaelt sie |
| `tests/test_single_instance.py` | 7 | die erste Kopie bekommt den Anspruch, die zweite nicht; er wird wieder frei; das Handle geht ueber den Anspruch; 0 ist eine Antwort; eine abgewiesene Kopie schreibt nicht; ein Nicht-Fenster wirft nicht |

Jeder Fall liest den Zustand, den das Programm fuehrt, oder das Bild, das es
zeichnet — nie einen Rueckgabewert. Das ist die Lehre aus QA-161 selbst.

**Mutationskampagne: 18 Eintraege, 18 toetend, alle rot im Standardlauf.**
Angewandt auf frische Baumkopien ausserhalb des Checkouts, je gegen die Datei,
der der Waechter gehoert (dieselbe Auswahl, die der Standardlauf faehrt).
Zusaetzlich drei verworfene Gegenbauten, siehe Abschnitt 3.

```
KILLED nightlord-card-without-a-name                       1 failed, 9 passed
KILLED nightlord-card-is-furniture-not-a-control           1 failed, 9 passed
KILLED nightlord-card-press-that-reports-and-does-nothing  1 failed, 9 passed
KILLED nightlord-card-out-of-the-tab-order                 2 failed, 8 passed
KILLED nightlord-card-keys-that-do-nothing                 4 failed, 6 passed
KILLED nightlord-card-focus-nobody-can-see                 1 failed, 9 passed
KILLED pointer-mark-left-to-enter-and-leave                (alle drei Faelle)
KILLED pointer-mark-that-misses-a-scroll                   1 failed, 2 passed
KILLED window-opens-at-a-width-set-by-hand                 1 failed, 5 passed
KILLED window-opening-width-that-forgets-its-chrome        1 failed, 5 passed
KILLED opening-width-measured-off-a-tab-that-is-not-in-front
KILLED window-opening-width-that-ignores-the-desktop       2 failed, 4 passed
KILLED window-that-never-takes-its-opening-size
KILLED opening-size-that-overrules-the-caller
KILLED heading-width-that-stops-at-the-widest-it-could-be  1 failed, 5 passed
KILLED second-copy-let-in                                  4 failed, 3 passed
KILLED second-copy-that-cannot-find-the-window             2 failed, 5 passed
KILLED copy-that-stood-down-and-wrote-anyway               1 failed, 6 passed
```

`tests/test_differential_track.py` prueft alle **159** Anker gegen den echten
Quelltext: gruen. Der Anker von `effect-headings-drawn-whole-or-not-at-all`
wurde nachgezogen, weil die Kuerzungsregel einen eigenen Namen bekommen hat
(nicht gelockert — er zeigt weiter auf genau eine Zeile).

**Nicht getestet, ausdruecklich:**

- **Die Verdrahtung in `main()`** — weder der Einzelinstanz-Zweig noch der
  `announce`-Aufruf haben einen Fall. `main()` baut eine `QApplication`, macht
  den Erststart-Check und laedt die Spieldaten; das in der Suite zu fahren
  waere ein anderer Auftrag. **Das ist eine Luecke, kein Beleg** — belegt ist
  sie nur von Hand (Abschnitt 1, QA-163).
- **`raise_window()` selbst.** Der Aufruf nach Windows hinein ist ueber den
  `activate`-Parameter herausgezogen, so dass die Faelle pruefen koennen, *mit
  welchem Handle* er gerufen wird; dass Windows das Fenster wirklich hebt, ist
  nur von Hand belegt.
- **Ein echter Bildschirmleser.** Gemessen ist, was ein UIA-Klient sieht und
  bewirkt. Was NVDA oder der Windows-Sprachausgabe daraus zusaetzlich macht,
  ist offen — wie schon in T-070.
- **Andere Skalierungen als 150 %** und andere Bildschirmgroessen.
- **Das gebaute Artefakt (A9).**

---

## 5. Die Frage aus QA-163: kann ein gespeicherter Build verlorengehen?

Der `qa-engineer` hat es ausdruecklich offen gelassen. Ich habe es
nachgestellt, nicht argumentiert.

**Versuch:** zwei echte Prozesse, derselbe Einstellungsspeicher, je 60 Builds
fuer denselben Nightfarer gespeichert und je 60 `set_hidden`-Umschaltungen, 1 ms
Abstand, gleichzeitig.

```
expected 120  found 120
MISSING (a saved build that is gone): []
EXTRA: []
WRONG PAYLOAD: []  count 0
order list length: 3        (von 120)
hidden list length: 34      (von 60 erwartet)
```

**Antwort: nein, ein gespeicherter Build geht nicht verloren.** Jeder Build ist
ein eigener Registry-Wert; zwei Kopien schreiben verschiedene Werte und treten
sich nicht auf die Fuesse. Was rettet: `build_names()` liest fehlende Eintraege
ueber `childKeys()` nach, wenn sie aus `__order` gefallen sind.

**Aber zwei Dinge gehen sehr wohl verloren, und beide still:**

1. **Die Reihenfolge.** `__order` ist ein Lesen-Aendern-Schreiben ueber eine
   ganze Liste: **3 von 120** Eintraegen ueberlebten. Die Builds sind da, ihre
   gespeicherte Reihenfolge ist es nicht.
2. **Die "versteckt"-Marken.** `__hidden` ist dieselbe Bauart: **34 von 60**
   ueberlebten, **26 Marken fielen weg**. Ein Build, den der Spieler
   ausgeblendet hatte, steht wieder da.

**Und ein dritter Weg, der Namen zerstoert.** `_migrate_keys` ist gegen einen
veralteten Schema-Lesevorgang nicht idempotent. Nachgestellt (deterministisch,
Interleaving simuliert): ein Altspeicher mit `Bleed build`, `Fire ice`,
`Poison`; Kopie A migriert; danach faehrt eine Kopie, die den Schema-Marker vor
A gelesen hat, ueber denselben Speicher:

```
A migriert    -> ['Bleed build', 'Fire ice', 'Poison']
danach        -> ['%42leed%20build', '%46ire%20ice', '%50oison']
Schluessel    -> builds/7/%2542leed%2520build  (doppelt kodiert)
load('%42leed%20build') -> Bleed build         (Daten intakt)
```

Die Daten ueberleben, **die Namen nicht**, und das Programm kann sie nicht
zurueckrechnen. Der Ausloeser braucht (a) einen Speicher, der noch nie
migriert wurde — also ein Upgrade von vor Schema 3 — und (b) zwei gleichzeitig
gestartete Kopien.

**Einordnung:** Punkt 1 bis 3 sind **Bestand**, nicht Teil dieses Fixes (so vom
Director angeordnet), und der Einzelinstanz-Schutz **entzieht allen dreien den
Ausloeser**, solange niemand ihn umgeht. Sie stehen unten als eigene Befunde.

**Ehrlichkeitsvorbehalt:** die Migrations-Reproduktion **simuliert** das
Interleaving (Schema-Marker nach A entfernt, dann `_migrate_keys` erneut). Ich
habe kein echtes Rennen zwischen zwei Prozessen gewonnen. Der reproduzierte
Zustand ist genau der, in dem eine zweite Kopie steht, die den Marker vor A
gelesen und `allKeys()` nach A gelesen hat.

---

## 6. Bildnachweise (L-012)

`docs/screenshots/2026-09-06-T071/`, beide ueber `window.grab()` auf das
Fenster des Programms — **kein Bildschirmabzug, auch kein zugeschnittener**:

- `effects-01-opening-width-every-heading-whole.png` — der Effekte-Reiter bei
  der Startbreite, alle elf Ueberschriften ganz, `Comes with curse` lesbar.
- `nightlords-02-keyboard-focus-on-a-card.png` — nach einem Tab-Druck; der
  Fokusrahmen steht auf `Adel`.

Beide **2 025 x 1 290 physische px** bei einem Fenster von 1 350 x 860
logischen px und einem Schirm von 2 560 x 1 600 physisch — vor dem Ablegen
geprueft, das Skript bricht ab, wenn ein Bild so gross wie der Schirm waere.
Keines zeigt den `Build planner`, also ist kein Save-Inhalt darauf.

---

## An den qa-engineer

**Was zu pruefen ist:**

1. **QA-161 am gebauten Fenster, mit drei Zugaengen**: Maus, Tab+Enter/Leertaste,
   UIA-`Invoke`. Das Urteil kommt aus der Detailtafel, nie aus dem
   Rueckgabewert — der war auch im kaputten Zustand `INVOKE_OK`.
2. **Der Fokusweg**: Tab durch die zehn Karten, dann Enter. Achte darauf, ob der
   Fokusrahmen von der Auswahlmarkierung unterscheidbar ist (siehe unten an den
   `ui-ux-designer`); wenn nicht, ist das ein Befund und keiner, den ich
   entscheiden darf.
3. **Startbreite**: 1 350 x 860 auf diesem Schirm. Auf einem schmaleren Schirm
   muss der Schirm gewinnen und die Mindestbreite 760 halten. **Bitte auf einem
   zweiten Schirmmass gegenpruefen** — ich habe nur diesen einen.
4. **QA-164 alle drei Wege**: Umbruch, Scrollen, Reiterwechsel mit ruhendem
   Zeiger. Und einen vierten, den ich nicht herstellen konnte: das Fenster
   minimieren und wiederherstellen, waehrend der Zeiger auf einer Karte liegt.
5. **QA-163**: zweimal starten; die zweite Kopie darf kein Fenster oeffnen und
   muss die erste nach vorn holen. **Zusatzfall, den ich nicht pruefen konnte:**
   die erste Kopie minimiert oder hinter anderen Fenstern — `SetForegroundWindow`
   darf von Windows verweigert werden, wenn der rufende Prozess kein
   Vordergrundrecht hat; dann endet die zweite Kopie trotzdem, aber der Spieler
   sieht nichts passieren.

**Randfaelle, die ich fuer heikel halte:**

- Zwei Kopien **gleichzeitig** starten (Doppelklick-Doppelklick): beide koennten
  im selben Moment `create()` versuchen. Einer gewinnt; der andere liest
  moeglicherweise ein Handle `0` (Fenster noch nicht da) und endet, ohne etwas
  nach vorn zu holen. Das ist absichtlich so und in `running_handle()`
  dokumentiert — aber es sieht fuer den Spieler aus wie "nichts passiert".
- Die zweite Kopie **nach** dem Beenden der ersten: der Anspruch muss frei sein.
- Ein Fenster, das ueber `Reset layout` oder die UI-Skalierung neu aufgebaut
  wird: die Startbreite darf dabei nicht erneut zuschlagen (`WA_Resized` steht
  dann).

**Umgebungswarnung, die dich Zeit kosten kann:** ein per `subprocess` aus einer
Shell gestartetes GUI dieses Programms bildet auf diesem Rechner **kein Fenster
ab** — `EnumWindows` findet nichts, der Prozess lebt. Ich habe das gegen den
**unveraenderten Baum bei HEAD** gegengeprueft: dort genauso. Es ist die
Umgebung, nicht die Aenderung. Meine Handpruefung faehrt die erste Kopie
deshalb im eigenen Prozess und nur die zweite als Unterprozess.

---

## An den ui-ux-designer

**Abweichung, die eine Entscheidung braucht.** Die Tastaturbedienung braucht
eine sichtbare Fokusmarke, und das Nightlord-Raster hat seine drei Kanaele
schon vergeben (Auswahl: warme Fuellung + Goldrand · Zeiger: neutrale Fuellung ·
Everdark: violetter Rand). Ich habe **keine vierte eigene Farbe erfunden**,
sondern den Fokusrahmen des Stils genommen (`PE_FrameFocusRect`, Fusion, inset
4 px).

**Die Folge, die du beurteilen musst:** Fusion zeichnet ihn mit
`palette.highlight()` als duenner Rand plus sehr blasse Fuellung — und die
Highlight-Farbe dieses Programms ist das Gold. Auf dem Bild
`nightlords-02-keyboard-focus-on-a-card.png` liegt die Fokusmarke damit im
selben warmen Kanal wie die Auswahlmarkierung. Sie sind unterscheidbar (die
Auswahl hat zusaetzlich den Goldrand und die kraeftigere Fuellung), aber sie
sind sich naeher, als dein Drei-Kanal-Schema vorsieht.

Zwei Auswege, falls dir das zu nah ist: (a) den Fokus mit einem eigenen,
kuehlen Rand zeichnen, (b) die Highlight-Farbe der Palette fuer diesen Zweck
ueberschreiben. Beides ist deine Entscheidung, nicht meine.

**Zweites, kleiner:** die Karten stehen jetzt in der Tab-Reihenfolge, also
laeuft Tab durch zehn Karten, bevor es weitergeht. Auf dem Relikt-Waehler waeren
es 55 (siehe L-006 oben) — ein Grund mehr, dort nicht dieselbe Aenderung zu
machen.

---

## An den director

### Sicherheitsfunde

Keine neuen. Der Einzelinstanz-Schutz verwendet ein **maschinenweites**
benanntes Objekt (`NightreignHelper-running-copy`); auf einem Mehrbenutzer-
rechner koennte ein anderer angemeldeter Nutzer damit die eigene Sitzung des
Spielers blockieren, wenn Windows den Namen sitzungsuebergreifend vergibt.
Qt legt den Namen ohne `Global\`-Praefix an, also ist er sitzungslokal — das
ist der gewuenschte Fall, aber ich habe es **nicht mit zwei Sitzungen
nachgestellt**.

### Befunde (Bestand, nicht von mir verursacht, nicht Teil dieses Auftrags)

1. **Zwei Kopien verlieren die Build-Reihenfolge und die "versteckt"-Marken.**
   Gemessen: `__order` 3 von 120, `__hidden` 34 von 60. Kein Build geht
   verloren. Ursache: beide Schluessel sind Lesen-Aendern-Schreiben ueber eine
   ganze Liste (`chalices.save_build`, `delete_build`, `set_hidden`). Risiko
   jetzt niedrig, weil der Einzelinstanz-Schutz den Ausloeser wegnimmt.
   Aufwand einer Behebung: mittel (je Eintrag ein eigener Schluessel statt
   einer Liste — beruehrt Migration und Formate).
2. **`_migrate_keys` ist gegen einen veralteten Schema-Lesevorgang nicht
   idempotent** und macht aus `Bleed build` den Namen `%42leed%20build`.
   Reproduktion oben, Interleaving simuliert. Braucht einen nie migrierten
   Speicher **und** zwei gleichzeitige Starts. Behebung: den Schema-Marker
   unmittelbar vor dem Schreiben noch einmal lesen, oder die Migration ueber
   den Anspruch aus `singleinstance` serialisieren. Aufwand: klein, Risiko der
   Aenderung: hoch (die Funktion traegt QA-033, QA-034, QA-040, QA-041, QA-046).
3. **`OTHER_CAP` kann eine Ueberschrift dauerhaft kuerzen.** Unter der Schrift
   der Suite braucht `Comes with curse` **196 px** Beschriftungsraum, und die
   Spalte ist auf **160** gedeckelt — keine Fensterbreite hilft. Auf Windows
   braucht sie **97 px**, also greift es dort nicht. Latent: eine Schrift mit
   etwa doppelter Laufweite von `Segoe UI 9` brachte es zurueck. Der Waechter
   ist so formuliert, dass er beides aushaelt; die Kappe selbst gehoert
   `ui-ux-designer` und AK-77.
4. **Zwei Gegenbauten ueberleben, weil drei Haken sich ueberlappen** (siehe
   Abschnitt 3 b). Kein Fehlverhalten, aber der Waechter gibt kein Signal, wenn
   jemand einen Haken einzeln entfernt. Vereinfachung waere moeglich, ist aber
   eine Entscheidung ueber Robustheit gegen Schlankheit.

### Performance-Fund

`BossCard.follow_the_pointer()` ruft `QApplication.widgetAt(QCursor.pos())` bei
**jedem** Move- und Resize-Ereignis jeder Karte — beim Ziehen des Fensterrands
also bis zu 20 Aufrufe je Bild bei zehn Karten. Ich habe es **nicht gemessen**
und es fiel im Betrieb nicht auf. **Empfehlung: `performance-tuner`
beauftragen**, wenn das Ziehen des Fensterrands je zaeh wirkt. Ich tune nicht
selbst.

### Doku-Nachtrag, den ich nicht schreiben darf

**`UI_SPEC.md` AK-05** (Zeile 344) nennt "Bei Fensterbreite 1320 px
(Startbreite)". Die Startbreite ist jetzt **1 350** auf diesem Schirm und
abgeleitet, also je nach Schirm und Schrift verschieden. AK-05 beschreibt die
Advisor-Leiste, die es noch nicht gibt — heute bricht nichts, aber die Praemisse
stimmt nicht mehr. Gehoert dem `ui-ux-designer`.

Ausserdem fuer `qa/findings.md`: QA-161, QA-163 (Schutz) und QA-164 sind aus
meiner Sicht behoben; QA-157 bleibt **offen** mit den Zahlen aus Abschnitt 2
(6 `WeaponTile`, 54 `RelicCard`, 1 `CustomRelicCard`); QA-162 habe ich nicht
angefasst (nicht beauftragt).

### Eskalationen

Keine. Der Auftrag war widerspruchsfrei und in Gaenze umsetzbar.

---

## DoD

- [x] Anforderung verstanden, Annahmen im Kopfblock dokumentiert
- [x] Build & Tests gruen: `-m "not slow"` **860 passed, 9 skipped, 5
      deselected**; `-m "slow"` **5 passed**. Zielsystem Windows 10/11 —
      Handpruefungen unter `QT_QPA_PLATFORM=windows` gefahren
- [x] Neue Tests fuer neue Logik: 45 Faelle, 18 toetende Mutationen
- [ ] **Linter sauber: nicht pruefbar.** Es gibt keinen im Projekt (F-A steht
      seit vier Zyklen offen). Ich habe die neuen Dateien gegen die
      Hausformatierung gelesen, mehr kann ich nicht behaupten
- [x] Keine Secrets, keine TODOs, kein toter Code
- [x] QA-Akzeptanzkriterien selbst durchgespielt (Abschnitt 1, je Befund am
      laufenden Fenster)
- [ ] **UX-Vorgabe: eine Abweichung, oben begruendet und an den
      `ui-ux-designer` adressiert** (Fokusmarke im warmen Kanal)
- [x] Bericht geschrieben, Bilder abgelegt, sechs Commits
- [ ] **Ungeprueft:** Skalierungen ausser 150 % · ein echter Bildschirmleser ·
      das gebaute Artefakt (A9) · die Verdrahtung in `main()` durch einen Test ·
      **Linux/macOS**, nie ausgefuehrt: `raise_window` gibt dort `False` und die
      zweite Kopie endet trotzdem, aber `QSharedMemory` haelt den Bereich auf
      Unix ueber einen Absturz hinaus — dort braeuchte der Anspruch das
      `attach`/`detach`-Aufraeumen, das unter Windows nicht noetig ist. Das
      Zielsystem ist Windows (GOAL), also ist es eine Einschraenkung und kein
      offener Punkt
