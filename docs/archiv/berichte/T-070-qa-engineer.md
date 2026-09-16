# T-070 — qa-engineer

```
STATUS: erledigt
AUFTRAG: T-070 — Regressionsverdacht gegen T-068 (Nightlord-Klick, `Comes with c…`)
GELESEN: GOAL.md · docs/state.md · docs/tasks/ (T-067 als einziger offener Auftrag,
         kein T-070.md vorhanden — der Auftragstext des Directors ist die Quelle) ·
         docs/berichte/T-068-developer.md (vollstaendig) ·
         docs/berichte/T-069-power-user.md (vollstaendig; die Datei lag beim ersten
         `git status` dieses Laufs noch nicht im Baum und ist waehrend meines Laufs
         erschienen — Inhalt deckt sich mit dem Auftragstext) ·
         docs/berichte/T-066-power-user.md · docs/berichte/T-064-qa-engineer.md ·
         docs/berichte/T-065-developer.md (Abschnitt QA-151) ·
         qa/findings.md (QA-140, QA-150 bis QA-160) · UI_SPEC.md (AK-77 und der
         Director-Nachtrag vom 2026-09-05) · nrplanner/{bosstab,effectstab,app,
         cardgrid,chalices,favourites,uiscale}.py · tests/{rendered,conftest,
         test_nightlord_selection}.py · scripts/differential/mutate.py ·
         .claude/agent-memory/qa-engineer/ (nightreign-helper-qa,
         qa-qt-sichtpruefung, nightreign-tab-content, nightreign-display-guards)
GEÄNDERT: docs/berichte/T-070-qa-engineer.md (diese Datei) — sonst nichts.
         `git status` im Projekt-Repo zeigt vor und nach meinem Lauf denselben
         Bestand (` M UI_SPEC.md`, ` M docs/plan-restarbeiten.md`, ` M docs/state.md`,
         ` M qa/findings.md` und die ungetrackten Berichte); HEAD unveraendert
         46a8d24. Kein add, kein commit, kein push, kein checkout/reset/clean/stash
         im Projekt-Repo. Alle Messungen liefen in einem eigenen `git clone` und
         zwei `git archive`-Extraktionen unter dem Scratchpad.
ANNAHMEN: (1) "Die Breite, die sich das Fenster selbst gibt" = `Planner.resize(1320, 860)`
         (app.py:1319) bei leerem Einstellungsspeicher; die Fenstergeometrie wird
         nirgends persistiert (`restoreGeometry`: 0 Treffer). (2) Der `power-user`
         hat auf demselben Rechner, derselben Skalierung (150 %) und ohne gesetztes
         `QT_SCALE_FACTOR` gearbeitet — ich konnte seine Umgebung nicht auslesen,
         nur meine eigene benennen. (3) Wo ich seine Klickkoordinaten nicht kenne,
         mache ich keine Aussage darueber, wo sie lagen, sondern messe, welche
         Zugangswege das Programm bedienen und welche nicht.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

---

# Fazit vorweg

**Nein. Es liegt keine Regression durch T-068 vor — an keiner der beiden
Stellen.**

Woran ich es festmache, in einem Satz je Symptom:

1. **Nightlord-Klick:** Am laufenden Fenster oeffnen **3 510 von 3 510**
   Pruefpunkten ueber die Fulghor-Karte das Profil, und ein **echter
   OS-Klick** (`SetCursorPos` + `SendInput`) oeffnet es an Mitte, Namenszeile
   und 3 px vor der Ecke — **in `46a8d24` und in `264d328` mit identischem
   Ergebnis**. Was in **beiden** Baeumen nichts bewirkt, ist der Weg, den der
   `power-user` als zweiten benutzt hat: **`Invoke` ueber UIAutomation meldet
   Erfolg und tut nichts** — auch vor T-068 schon.
2. **`Comes with c…`:** Der Kopf war bei 1 320 px **vor T-068 genauso
   gekuerzt**, mit **byteidentischen Spaltenbreiten** in beiden Baeumen, an
   **allen zwoelf** gemessenen Fensterbreiten von 760 bis 1 700 px. Die vier
   `FilterCaption` kosten die Tabelle **0 px**. Der Tooltip erscheint am
   laufenden Fenster nach **266 ms** (Kopf) bzw. **279 ms** (Basis) und bleibt
   ueber 1,2 s stehen — die Weckverzoegerung von 175 ms stammt aus `49811a8`
   (T-065) und ist ein **Vorfahr von 264d328**, nicht Teil von T-068.

**Beide vom Director genannten Fehlerquellen tragen** — und ich habe die
zweite nachgestellt: mit zwei gestapelten Kopien des Programms landet ein
Klick, der fuer Fenster A berechnet wurde, in Fenster B; B oeffnet Fulghor, A
bleibt bei `Select a Nightlord`. Wer A ansieht, sieht genau den T-069-Bericht.

Was **nicht** in Ordnung ist und in T-069 sichtbar wurde, ist etwas anderes
als eine Regression: **das Programm ist ueber die Bedienungshilfen-Schnittstelle
an den Karten nicht bedienbar, und die Schnittstelle behauptet das Gegenteil.**
Das ist Bestand, kein neuer Schaden — aber es ist der Grund, warum dieser
Verdacht entstanden ist, und es wird beim naechsten `power-user`-Lauf wieder
zuschlagen. Vier Befunde unten, **QA-161 bis QA-164**.

---

## 0. Messumgebung — jede Zahl unten gilt hierfuer (L-009)

| | |
|---|---|
| Betriebssystem | Windows 10 Home 19045 |
| Qt-Plattform | **`windows`** (nicht `offscreen`), `qapp.platformName()` ausgelesen |
| Stil / Palette | **`fusion`** + dunkle Palette, ueber `appmod.apply_appearance(qapp)` — derselbe Aufruf, den `main()` macht; `qapp.style().objectName()` ausgelesen |
| Skalierung | **150 %**, `devicePixelRatio` = **1.5**, `QT_SCALE_FACTOR` nicht gesetzt (`uiscale.apply_to_environment()` bei leerem Speicher setzt nichts) |
| Bildschirm | **1 707 x 1 067 logische px** (verfuegbar 1 707 x 1 027), 2 560 x 1 600 physisch |
| Schrift | `Segoe UI, 9` |
| Fenster | **1 320 x 860 logische px** — die Groesse, die es sich selbst gibt; `win.width()` hat die Zahl **erreicht**, sonst haette der Lauf sie als "nicht erreicht" ausgewiesen |
| Einheiten | Alle Zahlen unten sind **logische** px, ausser wo ausdruecklich "physisch" steht. UIA-Rechtecke sind **physisch** und als solche gekennzeichnet |
| Datensatz | `%LOCALAPPDATA%\NightreignHelper\nightreign_data.json`, `extract_version` **11** = `extract.EXTRACT_VERSION` **11** des Baums |
| Einstellungen | eigener Store `DankYeeterQA-T070/<rolle>-<pid>`, am Ende jedes Laufs geleert. Der Nutzerspeicher `DankYeeter/NightreignHelper` und der Test-Store `DankYeeterTests` wurden nie beschrieben |
| Baeume | **Kopf** = `git clone` + `checkout 46a8d24`; **Basis** = `git archive 264d328 \| tar -x`. Beide im Scratchpad, beide mit demselben Skript und demselben Datensatz vermessen |

---

## 1. Risiko-Briefing (vor der Messung geschrieben)

Die riskanteste Stelle ist die **Zuordnung**, nicht der Code: zwei Symptome,
zwei Aenderungen, und die naheliegende Erzaehlung verbindet sie kreuzweise.
Ich messe deshalb zuerst das, was ein Vorher/Nachher-Vergleich **entscheiden**
kann und ein Argument nicht: die Spaltenbreiten der Effekttabelle in beiden
Baeumen bei derselben Fensterbreite (kostet die `FilterCaption` Breite, ja oder
nein — eine Zahl, kein Urteil). Danach die Trefferflaeche der Karte in beiden
Baeumen mit einem **echten** OS-Klick, weil genau der beim `power-user`
versagt hat und `qApp.notify` den Weg umgeht, um den es geht. Erst dann der
Zugangsweg, der in T-069 tatsaechlich benutzt wurde (`Invoke`), weil er
erklaeren koennte, warum zwei Rollen dasselbe Widget unterschiedlich erleben.
Zuletzt die beiden Fehlerquellen des Directors, und zwar nachgestellt statt
plausibilisiert.

---

## 2. Ausgangslage bestaetigt

Im frischen Klon auf `46a8d24`, gegen den Snapshot:

| Lauf | Ergebnis | gegen die genannte Zahl |
|---|---|---|
| `-m "not slow"` | **815 passed, 9 skipped, 5 deselected** in 383,11 s | deckungsgleich |
| `-m "slow"` | **5 passed, 824 deselected** in 51,16 s | deckungsgleich |

**Stichprobe statt Wiederholung (kein Doppel-Testen).** T-068 meldet 20
gefahrene Mutationen. Ich habe **eine** nachgefahren, und zwar die, die dem
gemeldeten Symptom am naechsten liegt:
`nightlord-card-labels-eat-the-press`. Vorgehen nach dem Rezept im
Modul-Docstring: frische `git archive 46a8d24`-Extraktion, `mutate.py` **aus
dem Klon heraus** aufgerufen mit `--tree <externer Pfad>` (nicht aus dem
mutierten Baum — dort verweigert der Selbstschutz und der Lauf saehe gruen
aus). Die Anwendung ist mechanismus-gebunden belegt: `bosstab.py:357
rewritten (+65 bytes)`, und der `diff` gegen `git show 46a8d24:...` zeigt
genau die eine Zeile `description.setAttribute(Qt.WA_NoMousePropagation, True)`.

Ergebnis im **Standardlauf**: `1 failed, 13 passed in 33.09s`, und der
Fehlertext nennt die Stelle, die er bewacht:

```
AssertionError: a press on these parts of the Adel card did not open it:
[('A colossal, crooked black frame capable of\nharboring lightning, ...', [])]
```

Der Waechter beisst, im Standardlauf, mit einem Signal, das nur dieser
Mechanismus erzeugt. Die uebrigen 19 Mutationen habe ich **nicht**
nachgefahren; siehe „Nicht getestet".

---

## 3. Frage 1 — ist `Comes with curse` gekuerzt, und war er es vorher auch?

**Ja, und ja. Identisch.**

Bei 1 320 x 860 px, der Groesse, die sich das Fenster selbst gibt, ist genau
**eine** von elf Ueberschriften gekuerzt, in **beiden** Baeumen:

```
Kopf 46a8d24 : ELIDED = ['Comes with curse']  ->  angezeigt 'Comes with c…'
Basis 264d328: ELIDED = ['Comes with curse']  ->  angezeigt 'Comes with c…'
```

Und die Spaltenbreiten sind nicht "aehnlich", sondern **gleich**:

| | Effect | Type | Tier | Copies | Colours | Relic slots | Avg ch. | Best ch. | Stacking | Comes… | What it does |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kopf | 320 | 53 | 48 | 64 | 89 | 82 | 89 | 89 | 89 | 89 | 260 |
| Basis | 320 | 53 | 48 | 64 | 89 | 82 | 89 | 89 | 89 | 89 | 260 |

Tabellen-Sichtbereich 1 272 px in beiden. Fenstermindestbreite **760 px** in
beiden (die Mindesthoehe geht 514 → 548, das sind die Kachelnamen aus
QA-155, wie T-068 es berichtet).

**Der Vollstaendigkeit halber ueber zwoelf Breiten** — jede Zeile hat ihre
Zielbreite tatsaechlich erreicht (`reached == asked`, sonst haette ich sie als
nicht gemessen ausgewiesen):

| Fensterbreite | gekuerzte Koepfe | Basis identisch? |
|---|---|---|
| 760 | 8 (`Type` bis auf `…`, dann `Co…`, `Co…`, `Re…`, `Av…`, `Be…`, `St…`, `Co…`) | ja |
| 833 | 8 | ja |
| 900 | 8 | ja |
| 1000 | 7 | ja |
| 1067 | 4 (`Relic sl…`, `Avg ch…`, `Best c…`, `Comes…`) | ja |
| 1150 | 3 | ja |
| 1250 | 1 (`Comes with…`) | ja |
| **1320 (Startmass)** | **1 (`Comes with c…`)** | **ja** |
| 1400 | **0** | ja |
| 1500 | 0 | ja |
| 1600 | 0 | ja |
| 1700 | 0 | ja |

**Damit ist die Vermutung des Directors gemessen widerlegt:** die vier neuen
`FilterCaption` kosten die Effekttabelle an **keiner** der zwoelf Breiten auch
nur ein Pixel. Bei 1 320 px zeigen sie ihre Woerter ausserdem vollstaendig
(`Colour` 35 px in 36, `Relics` 30 in 30, `Stacking` 44 in 45, `Type` 25 in
25 — keines kuerzt sich).

**Ein Nebenergebnis, das dem Director gehoert, nicht mir:** das Fenster gibt
sich 1 320 px, und die Schwelle, ab der **nichts** mehr gekuerzt ist, liegt
zwischen 1 320 und 1 400 px. Der Startzustand des Programms liegt also
**knapp** unterhalb der Breite, bei der die Tabelle vollstaendig lesbar waere.
Das ist Bestand und durch den AK-77-Nachtrag gedeckt (gekuerzt ist erlaubt,
solange der volle Text im Tooltip steht) — aber es ist der Grund, warum
**zwei aufeinanderfolgende `power-user`-Laeufe genau diese eine Spalte**
gemeldet haben. Als offene Frage unten, nicht als Befund.

---

## 4. Frage 2 — traegt der gekuerzte Kopf seinen Tooltip, und nach wie vielen ms?

**Ja, und nach rund einer Viertelsekunde — in beiden Baeumen.**

Gemessen am laufenden, sichtbaren Fenster mit `QCursor.setPos` (das ruft
dasselbe `SetCursorPos` wie ein Maustreiber und erzeugt echte `WM_MOUSEMOVE`;
`QTest.mouseMove` haette nur Qts eigene Warteschlange gefuellt und genau den
Weg umgangen, um den es geht). Der Zeiger wurde erst auf einen **anderen**
Kopf gesetzt und dann auf den gekuerzten, damit ein echter Abschnittswechsel
stattfindet.

| Baum | Stilwert `SH_ToolTip_WakeUpDelay` | `HeadingHint.delay()` | erste Sichtbarkeit | Text | nach 1,2 s noch da |
|---|---|---|---|---|---|
| **46a8d24** | 700 ms | **175 ms** | **266,2 ms** | vollstaendig | ja |
| **264d328** | 700 ms | **175 ms** | **278,5 ms** | vollstaendig | ja |

Gezeigter Text, beide Baeume wortgleich:

```
Comes with curse
Whether relics carrying this effect can also roll a curse — 'sometimes' by
relic, 'always cursed' without exception.
```

Die Differenz von 266 zu 175 ms ist meine Abfrageschleife plus OS-Overhead,
kein Programmverhalten.

**Zur Zuordnung im Auftragstext:** die Weckverzoegerung hat **nicht** T-068
gesenkt. `class HeadingHint` und `WAKE_UP_DIVISOR = 4` stammen aus Commit
`49811a8` („fix(effects): answer a shortened heading inside a brief hover"),
und `git merge-base --is-ancestor 49811a8 264d328` ist **wahr** — der
Mechanismus steht schon im Basisbaum. T-068 hat ihn nicht angefasst.

**Ein Verweilen von ueber einer Sekunde haette den Tooltip also gesehen** —
mit einem Zeiger. Warum der `power-user` nichts sah, steht in Abschnitt 6.

---

## 5. Frage 3 — oeffnet ein Klick auf eine Nightlord-Karte das Profil?

**Ja. Auf jedem gemessenen Punkt, ueber jeden gemessenen Weg, in beiden
Baeumen.**

Karte `Fulghor`, 311 x 178 logische px (dritte Spalte, zweite Zeile bei
1 320 px; die Karte ist vollstaendig im Sichtbereich, kein Scrollen noetig).

**(a) Pruefpunkt-Raster ueber `qApp.notify`**, ein Punkt je 4 logische px,
Zustellung an das Widget, das `widgetAt` an dieser Stelle meldet, damit Qts
eigene Weiterreichung entscheidet:

| Baum | Punkte | oeffnen Fulghor | tot | `widgetAt` lieferte `None` |
|---|---|---|---|---|
| 46a8d24 | 3 510 | **3 510** | **0** | 0 |
| 264d328 | 3 510 | **3 510** | **0** | 0 |

**(b) Echter OS-Klick** — `QCursor.setPos` auf den Zielpunkt, dann
`SendInput` mit `MOUSEEVENTF_LEFTDOWN/UP` an der Zeigerposition (so entfaellt
jede eigene Koordinatenumrechnung). Vor jedem Klick wird geprueft, dass unter
dem Zeiger ein Widget **dieses** Programms steht; sonst wird nicht geklickt.

| Klickstelle | Widget darunter | Kopf 46a8d24 | Basis 264d328 |
|---|---|---|---|
| Mitte der Karte | `QLabel` (Beschreibungstext) | **oeffnet Fulghor** | **oeffnet Fulghor** |
| auf der Namenszeile `Fulghor` | `QLabel` | **oeffnet Fulghor** | **oeffnet Fulghor** |
| 3 px innerhalb der linken oberen Ecke | `BossCard` | **oeffnet Fulghor** | **oeffnet Fulghor** |
| in der 8-px-Luecke zu `Libra` | `CardGrid` | oeffnet nichts | oeffnet nichts |

Die Luecke ist gemessen **8 px** in beiden Baeumen, und der Negativfall
verhaelt sich in beiden gleich: `detail_name` bleibt `Select a Nightlord`,
keine Karte wird markiert.

**(c) Wiederholung und Tempo.** Doppelklick und sechs Klicks so schnell,
wie `SendInput` sie absetzt: beide Male oeffnet Fulghor, beide Baeume, keine
Zwischenzustaende.

**(d) Verschiebt die neue Zeigermarke etwas?** Nein. Alle zehn
Kartenrechtecke sind vor, waehrend und nach dem Ueberfahren **identisch**
(`identical_before_during` und `identical_before_after` beide wahr, `moved`
leer). Der Zustand selbst greift korrekt: `hovered == ['Fulghor']`, solange
der Zeiger auf der Karte steht, `[]` danach; im Basisbaum gibt es den Zustand
nicht.

**Damit ist auch die zweite Vermutung des Directors gemessen widerlegt:** die
`enterEvent`/`leaveEvent`-Markierung sitzt zwar am selben Widget, aber sie
nimmt dem Klick nichts weg und bewegt die Karte nicht.

---

## 6. Frage 4 — reagiert die Karte auf `Invoke` ueber UIAutomation?

**Nein. Und das ist ein Mangel, kein erwartbares Verhalten eines eigenen
Widgets — weil die Schnittstelle das Gegenteil behauptet.**

Gemessen mit dem .NET-`UIAutomationClient`, den Windows mitbringt, gegen das
laufende Fenster; jede Aktion einzeln, damit das Signal zuordenbar bleibt.

Was UIA von der Kartenflaeche sieht:

- **90 Elemente** exponiert das Fenster insgesamt. **90 von 90** melden
  `InvokePatternIdentifiers.Pattern` als unterstuetzt — auch reine
  Textbeschriftungen.
- Genau **ein** Element heisst `Fulghor`: `ControlType.Text` / `QLabel`,
  physisches Rechteck `1194,594,327,27`.
- Die **Karte selbst** ist `ControlType.Custom` / `BossCard`, physisches
  Rechteck `1069,579,466,267`, und traegt **keinen Namen**.
- `ElementFromPoint` auf die Kartenmitte liefert den **Beschreibungstext**,
  nicht die Karte.

Was `Invoke` bewirkt — Urteil nicht aus dem Rueckgabewert, sondern aus dem
Zustand, den das Programm selbst protokolliert (`detail_name`-Historie):

| Ziel | Baum | Rueckgabe | `detail_history` danach | Wirkung |
|---|---|---|---|---|
| `QLabel` „Fulghor" | 46a8d24 | `INVOKE_OK` | `['Select a Nightlord']` | **keine** |
| `BossCard` (Custom) | 46a8d24 | `INVOKE_OK` | `['Select a Nightlord']` | **keine** |
| `QLabel` „Fulghor" | 264d328 | `INVOKE_OK` | `['Select a Nightlord']` | **keine** |
| `BossCard` (Custom) | 264d328 | `INVOKE_OK` | `['Select a Nightlord']` | **keine** |
| **`TabItem` „Deep of Night"** (Kontrolle, `Invoke` allein, ohne `Select`) | 46a8d24 | `INVOKE_OK` | — | **`current_tab` wechselt wirklich auf `Deep of Night`** |

Die Kontrollzeile ist der Punkt: `Invoke` **funktioniert** in diesem Programm
dort, wo dahinter eine echte Aktion liegt. An den Karten liegt keine, und die
Schnittstelle sagt es nicht — sie meldet Erfolg. Ein Klient kann „hat
gewirkt" und „hat nichts getan" nicht unterscheiden.

**Antwort auf die gestellte Frage:** Es ist ein **Mangel**, kein erwartbares
Verhalten. Erwartbar waere „`Invoke` wird nicht unterstuetzt" — dann haette
der `power-user` einen Fehler bekommen und den Weg gewechselt. **Es ist aber
Bestand**: Kopf und Basis verhalten sich Zeichen fuer Zeichen gleich. Befund
**QA-161**.

**Und dieselbe Klasse eine Etage darueber, bei der Kopfzeile.** Alle elf
Header-Elemente exponieren als `Name` den **angezeigten**, also ggf.
gekuerzten Text; Nummer 10 heisst woertlich `Comes with c…` (13 Zeichen,
letztes Zeichen U+2026). `HelpText` ist bei **allen elf leer** — in beiden
Baeumen. Der volle Name existiert fuer die Schnittstelle nur, **solange der
Tooltip auf dem Schirm steht**, und dann als Name eines **eigenen
Top-Level-Fensters** der Klasse `QTipLabel`:

```
top-level: type=Window class=QTipLabel name='Comes with curse
Whether relics carrying this effect can also roll a curse — 'sometimes' by
relic, 'always cursed' without exception.'  rect=1569,424,898,57 (physisch)
top-level: type=Pane   class=SysShadow ...
top-level: type=Window class=Planner    name='Nightreign Helper 1.7.1'
```

Wer im **Fensterbaum** des Programms nach der Erklaerung sucht, findet sie
nie — sie steht ausserhalb. Befund **QA-162**. Auch das ist Bestand: im
Basisbaum exakt dasselbe Bild.

---

## 7. Die beiden Fehlerquellen, die auszuschliessen waren

### (a) Koordinaten in der 8-px-Luecke — **traegt als Erklaerung**

Die Luecke existiert und ist tot: 8 px zwischen zwei Karten, ein echter Klick
darin oeffnet nichts, in beiden Baeumen. Zugleich oeffnen **3 510 von 3 510**
Punkten **auf** der Karte sie. Ich kenne die Koordinaten des `power-user`
nicht und behaupte deshalb nicht, dass sie dort lagen. Ich kann nur sagen:
**wenn** sie dort lagen, erklaert das den Fehlschlag vollstaendig und ohne
jede Aenderung an T-068.

Ein zweiter, ebenso ausreichender Weg in dieselbe Wirkung, gemessen: eine
UIA-Bounding-Box ist **physisch**. Nimmt ein Klickweg sie unveraendert als
logische Koordinate, landet der Zeiger bei 150 % Skalierung um den Faktor 1,5
zu weit aussen. Fuer die Namenszeile von Fulghor sind das statt (905, 405)
der Punkt **(1 358, 608)** — immer noch **im Fenster**, aber auf dem
`QFrame` des Detailbereichs. Gemessen: ein echter Klick dort laesst
`detail_name` auf `Select a Nightlord` stehen. Beide Baeume gleich. Auch das
ist eine Hypothese ueber **fremdes** Werkzeug, nicht ueber das Programm — ich
fuehre sie an, weil sie dasselbe Symptom exakt erzeugt.

### (b) Zwei Fenster und ein Geisterprozess — **traegt, und ich habe es nachgestellt**

Das Programm hat **keinen Schutz gegen eine zweite Instanz**. Drei
unabhaengige Suchmasken ueber den Quellbestand (`QSharedMemory|QLocalServer|
CreateMutex|single.instance|already running|lockfile`, dann
`only one|second copy|zweite Instanz|instance` ueber `nrplanner/`, `nrdata/`,
`run.py`, dann `instanz|instance` ueber `README.md`, `ARCHITECTURE.md`,
`UI_SPEC.md`): **0 Treffer**, die einen solchen Schutz waeren.

Nachgestellt, nicht argumentiert:

```
A pid 9068  window [60, 60, 1320, 860]  detail Select a Nightlord
B pid 16172 window [60, 60, 1320, 860]  detail Select a Nightlord
same position: True
Ziel = A's Fulghor-Mitte: logisch (868, 475) = physisch (1302, 712)
WindowFromPoint an dieser Stelle gehoert pid 16172  ->  B
NACHHER  A: Select a Nightlord   | history ['Select a Nightlord']
NACHHER  B: Fulghor              | history ['Select a Nightlord', 'Fulghor']
```

Zwei Kopien starten ohne Widerspruch, legen sich deckungsgleich uebereinander
und sind auf dem Schirm nicht auseinanderzuhalten. Ein Klick, der fuer A
berechnet wurde, wird von **B** verarbeitet. Wer A beobachtet, protokolliert
„geklickt, nichts passiert" — der T-069-Text, Wort fuer Wort.

Der `power-user` gibt an, den Geisterzustand vor dem eigentlichen Lauf
bereinigt zu haben. Ich kann das weder bestaetigen noch widerlegen; sein
Bericht ist die einzige Quelle ueber seine Umgebung. Fuer das Urteil ist es
auch nicht noetig: (a) und (b) sind **je fuer sich** ausreichend, und der
`Invoke`-Weg ist unabhaengig von beiden **beweisbar** wirkungslos.

---

# Befunde

### [P2 | Major | Mittel] Eine Nightlord-Karte ist ueber die Bedienungshilfen-Schnittstelle nicht bedienbar, und die Schnittstelle meldet Erfolg

**ID:** QA-161
**Adressat:** developer
**Betroffen:** `nrplanner/bosstab.py:295` (`BossCard`, `mousePressEvent` als
einziger Ausloeser) — dieselbe Klasse an fuenf weiteren Stellen, siehe unten
**Umgebung:** Windows, Fusion, 150 %, laufendes Fenster, UIA-Klient
(.NET `UIAutomationClient`). **Bestand: in `264d328` identisch.**

**Reproduktion:**
1. Programm starten, Reiter `Nightlords`.
2. Mit einem UIA-Klienten das Element mit `Name == "Fulghor"` suchen.
   Ergebnis: genau eines, `ControlType.Text` / `QLabel`. Die Karte selbst ist
   `ControlType.Custom` / `BossCard` und **ohne Namen**.
3. `InvokePattern.Invoke()` darauf aufrufen — und ebenso auf die Karte.
4. Rechte Seite ablesen.

**Erwartet:** Entweder oeffnet `Invoke` das Profil, oder der Aufruf schlaegt
mit „Muster nicht unterstuetzt" fehl, sodass ein Klient den Weg wechseln kann.
**Tatsaechlich:** `Invoke` liefert in **beiden** Faellen Erfolg, und das
Programm bewegt sich nicht (`detail_name`-Historie bleibt
`['Select a Nightlord']`). **90 von 90** exponierten Elementen melden
`InvokePattern` als unterstuetzt, auch reine Textbeschriftungen.

**Analyse:** Die Karte reagiert ausschliesslich auf `mousePressEvent`. Qts
Windows-UIA-Bruecke bildet `InvokePattern` auf die Zugriffsaktion „Press" ab;
ein `QFrame` und ein `QLabel` haben keine, und die Bruecke meldet das Muster
trotzdem als vorhanden. Dass die Ursache in der Bruecke liegt und nicht im
Programm, ist **Hypothese**; gemessen ist nur das Verhalten. Die
Gegenprobe steht: `Invoke` **allein** auf `TabItem "Deep of Night"` wechselt
den Reiter wirklich — die Mechanik funktioniert dort, wo eine Aktion
hinterlegt ist.

**Auswirkung:** Jeder Zugang, der nicht die physische Maus ist, kommt an den
Nightlord-Karten nicht vorbei und bekommt dabei „erfolgreich" gemeldet. Das
hat in **zwei von vier** `power-user`-Laeufen zum Abbruch von Aufgabe 3
gefuehrt (T-066 mit Muehe, T-069 aufgegeben) und in diesem Zyklus einen
vollstaendigen Regressionsverdacht ausgeloest, der keiner war. Dieselbe
Eigenschaft haben nach dem L-006-Durchgang von T-068 **fuenf weitere**
Klickflaechen (`relicpicker.py:136`, `:210`, `:253`, `weaponslots.py:200`,
`app.py:199`, dort als QA-157 gefuehrt) — die Zeigermarke wurde dort
angemahnt, die Bedienbarkeit ohne Maus bisher nirgends.

**Vorschlag:** Richtung, nicht Patch — den Karten eine echte Zugriffsaktion
geben, sodass „Press" auf demselben Weg landet wie `mousePressEvent`, und der
Karte einen Namen, damit ein Klient sie ueberhaupt findet statt nur ihre
Beschriftung. Ob das ueber `QAccessibleWidget`/`QAccessibleActionInterface`
oder ueber einen fokussierbaren Knopf als Kartenrahmen geht, ist eine
Bauentscheidung. **Ein Waechter dafuer braucht ein Signal, das nur dieser
Mechanismus erzeugt** — der Rueckgabewert von `Invoke` taugt nachweislich
nicht dafuer (er ist auch im kaputten Zustand „OK"); tragfaehig ist der
Zustandswechsel des Detailbereichs.

---

### [P3 | Minor | Mittel] Ein gekuerzter Spaltenkopf gibt der Bedienungshilfen-Schnittstelle nur den gekuerzten Text; der volle Name steht ausserhalb des Fensterbaums

**ID:** QA-162
**Adressat:** developer · **Einstufung als Mangel:** director/ui-ux-designer
(beruehrt **A12**, und QA-159 fragt dieselbe Sache aus Sichtweite)
**Betroffen:** `nrplanner/effectstab.py`, `set_headings`/`_elide_headings`
und `HeadingHint`
**Umgebung:** wie oben. **Bestand: in `264d328` identisch.**

**Reproduktion:**
1. Programm starten, Reiter `Effects & chances`, Fenster auf seiner eigenen
   Breite (1 320 px) lassen.
2. Mit einem UIA-Klienten alle Elemente vom Typ `Header` auslesen.

**Erwartet:** Der volle Name ist ueber die Schnittstelle erreichbar, so wie
ein Zeiger ihn ueber den Tooltip erreicht.
**Tatsaechlich:** `Name` ist der **angezeigte** Text, also `Comes with c…`
(13 Zeichen, letztes U+2026). `HelpText` ist bei **allen elf** Koepfen leer.
Der volle Text erscheint nur, solange der Tooltip steht, und dann als Name
eines **eigenen Top-Level-Fensters** `QTipLabel` — nicht im Baum des
Programmfensters.

**Analyse:** Der Kopftext wird per `QTableWidgetItem.setToolTip` gesetzt.
Qt bildet die Tooltip-Rolle einer Kopfzelle nicht auf UIAs `HelpText` ab
(Hypothese ueber die Ursache; gemessen ist nur, dass `HelpText` leer ist).
Die Zusicherung aus dem AK-77-Nachtrag — „jede gekuerzte Zelle traegt ihren
vollen Text als Tooltip" — traegt damit **fuer den Zeiger** (T-064 und dieser
Lauf belegen es), aber nicht fuer jeden anderen Zugang.

**Auswirkung:** Ein Leser ohne Zeiger sieht `Comes with c…` und hat keinen
Weg zum vollen Namen. Bei 833 px zeigen drei Koepfe identisch `Co…` — dort
sind `Copies`, `Colours` und `Comes with curse` ueber die Schnittstelle
**nicht auseinanderzuhalten**.

**Vorschlag:** Den vollen Namen zusaetzlich dort ablegen, wo er ohne Hover
gelesen werden kann — etwa als Zugriffsbeschreibung des Kopfabschnitts. Ein
Waechter darauf liest die Zugriffsschnittstelle, nicht `item.toolTip()`; die
vorhandenen Faelle pruefen genau die Property, die hier nicht ankommt.

---

### [P3 | Major | Niedrig] Zwei Kopien des Programms starten ohne Widerspruch, legen sich uebereinander und teilen sich einen Einstellungsspeicher

**ID:** QA-163
**Adressat:** developer · **Scope-Entscheid:** director
**Betroffen:** `nrplanner/app.py:3764` (`main`), `app.py:1415`
(`aboutToQuit -> _store_layout`)
**Umgebung:** wie oben. **Bestand, nicht neu.**

**Reproduktion:**
1. Das Programm zweimal starten.
2. Beide Fenster stehen an derselben Stelle, in derselben Groesse, mit
   demselben Titel.
3. Auf die Kartenmitte klicken, die man **im ersten** Fenster ausgemessen hat.

**Erwartet:** Entweder verweigert die zweite Kopie den Start und holt die
erste nach vorn, oder die beiden sind unterscheidbar.
**Tatsaechlich:** Beide laufen. `WindowFromPoint` an der berechneten Stelle
liefert den **zweiten** Prozess; der Klick oeffnet dort `Fulghor`, waehrend
das erste Fenster bei `Select a Nightlord` bleibt (Protokoll in Abschnitt 7b).

**Analyse:** Kein Einzelinstanz-Schutz vorhanden (drei Suchmasken, 0
Treffer). Beide Kopien schreiben ausserdem in denselben
QSettings-Bereich; nachgewiesen ist der Schreibvorgang beim Beenden
(`_store_layout` legt den Splitter-Zustand ab), also gewinnt die zuletzt
geschlossene Kopie. **Ob darueber hinaus ein gespeicherter Build verloren
gehen kann, habe ich nicht nachgestellt** — `chalices.save_build` schreibt je
Schluessel, `set_hidden` liest unmittelbar vor dem Schreiben neu; das sind
schmale, aber nicht ausgeschlossene Fenster. Siehe „Offene Fragen".

**Auswirkung:** Der sichtbare Schaden ist Verwirrung — „das Programm reagiert
nicht" —, und genau die hat in T-069 zu einem falschen Regressionsverdacht
und diesem Auftrag gefuehrt. Der stille Schaden waere die Ueberschreibung von
Nutzerzustand; er ist hier **nicht** belegt, nur nicht ausgeschlossen.

**Vorschlag:** Ein Einzelinstanz-Schutz beim Start (benanntes Systemobjekt
oder lokaler Server), der die vorhandene Kopie nach vorn holt statt eine
zweite zu oeffnen. Fuer den Speicher-Teil zuerst messen, dann bauen.

---

### [P4 | Minor | Niedrig] Die Zeigermarke wird nur durch eine Zeigerbewegung aktualisiert — nach einem Umbruch des Rasters steht sie auf der falschen Karte

**ID:** QA-164
**Adressat:** developer (Verhalten) · ui-ux-designer (ob es stoert)
**Betroffen:** `nrplanner/bosstab.py:407` (`enterEvent`), `:417` (`leaveEvent`),
`nrplanner/cardgrid.py:100` (`resizeEvent -> _apply`)
**Umgebung:** wie oben. **Neu mit T-068** (im Basisbaum gibt es die Marke
nicht).

**Ein systemisches Finding mit zwei Belegfaellen** — beide haben dieselbe
Wurzel: der Zustand haengt allein an Enter/Leave, und die kommen nur bei
Zeigerbewegung.

**Reproduktion (Fall 1 — Umbruch):**
1. Reiter `Nightlords`, Fenster 1 320 px breit (drei Spalten).
2. Zeiger auf die Karte `Fulghor` legen, liegen lassen.
3. Das Fenster auf 900 px verschmaelern, **ohne den Zeiger zu bewegen** (per
   Fensterknopf, Tastatur oder von aussen).

**Erwartet:** Die Marke steht auf der Karte, auf der der Zeiger jetzt steht —
oder auf keiner.
**Tatsaechlich:** Gemessen: `hovered == ['Fulghor']` vor dem Umbruch,
`hovered == ['Fulghor']` danach, waehrend unter dem Zeiger **gar keine Karte
mehr** liegt (Spaltenzahl 3 → 2; die Suche nach einem `BossCard`-Vorfahren
unter dem Zeiger liefert `None`). Nach der naechsten Zeigerbewegung ist
`hovered == []` — der Zustand heilt sich, aber erst dann.

**Reproduktion (Fall 2 — Karte erscheint unter einem ruhenden Zeiger):**
Fenster oeffnen, waehrend der Zeiger schon dort steht, wo eine Karte
erscheint: `hovered == []`, obwohl der Zeiger auf der Karte steht. Erst eine
Bewegung setzt die Marke.

**Analyse:** Qt liefert Enter/Leave beim naechsten Zeigerereignis, nicht beim
Umbau des Layouts. Die Marke ist deshalb nur so aktuell wie die letzte
Zeigerbewegung.

**Auswirkung:** Gering und selbstheilend, aber sie faellt in genau die
Aussage, fuer die die Marke gebaut wurde: „hier steht dein Zeiger". Kurzzeitig
sagt sie etwas Falsches.

**Vorschlag:** Den Zustand nach einem Umbruch aus der tatsaechlichen
Zeigerposition neu bestimmen, statt ihn nur fortzuschreiben.

---

## Zusammenfassung (an den director)

| Prioritaet | Anzahl |
|---|---|
| P1 | 0 |
| P2 | 1 (QA-161) |
| P3 | 2 (QA-162, QA-163) |
| P4 | 1 (QA-164) |

**Es liegt keine Regression durch T-068 vor.** Die beiden verdaechtigten
Aenderungen sind gemessen entlastet: die vier `FilterCaption` kosten die
Effekttabelle an zwoelf von zwoelf Fensterbreiten **0 px** und aendern die
Kuerzung von `Comes with curse` nicht (die gab es bei 1 320 px vorher
genauso), und die Zeigermarke nimmt dem Klick nichts weg — 3 510 von 3 510
Punkten und vier von vier echten OS-Klicks oeffnen die Karte in **beiden**
Baeumen gleich. **Releasefaehigkeit ist durch diesen Lauf nicht
verschlechtert**; die Suite steht unveraendert bei 815/9/5 und 5.

Was ich stattdessen gefunden habe, sollte den Auftragsfluss aendern, nicht den
Code-Stand blockieren: **der Zugangsweg, ueber den die `power-user`-Rolle
arbeitet, kann die Nightlord-Karten prinzipiell nicht bedienen und bekommt
dabei Erfolg gemeldet (QA-161).** Solange das so ist, wird jeder
`power-user`-Lauf Aufgabe 3 melden, und jedes Mal wird die Frage „Bug oder
Werkzeug" neu gestellt. Mindestens noetig vor dem naechsten Lauf: entweder
QA-161 beheben, oder der Rolle mitgeben, dass ein `Invoke`-Erfolg in diesem
Programm nichts beweist und ein Ergebnis nur ein beobachteter Zustandswechsel
ist. Das ist deine Entscheidung, nicht meine.

---

## Explorationsprotokoll

Was ich versucht habe und was gehalten hat:

- **Zwei Baeume, ein Skript.** Klon auf `46a8d24`, `git archive 264d328`
  daneben; jede Messung mit demselben Skript und demselben Datensatz gegen
  beide. Hat gehalten — die Unterschiede, die uebrig blieben, sind genau die
  zwei, die T-068 auch berichtet (Mindesthoehe 514 → 548, `hovered` existiert
  nur im Kopf).
- **Geometrie ueber zwoelf Breiten** statt nur bei 1 320: sollte zeigen, ob
  die Beschriftungen an irgendeiner Breite doch Platz kosten. Hat gehalten,
  Ergebnis negativ (kein Unterschied).
- **Tooltip mit `QCursor.setPos`** am sichtbaren Fenster, mit vorherigem
  Parken auf einem anderen Kopf, damit ein echter Abschnittswechsel
  stattfindet. Hat gehalten (266 / 279 ms).
- **Klick dreistufig**: `qApp.notify`-Raster, echter `SendInput`-Klick,
  Negativfall in der Luecke. Hat gehalten. **Sicherung, die gegriffen hat:**
  vor jedem echten Klick pruefe ich mit `widgetAt`, dass ein Widget dieses
  Programms unter dem Zeiger steht; sonst wird nicht geklickt.
- **UIA ueber PowerShell** (`UIAutomationClient` aus dem System, keine
  Installation). Erst ein Sammelskript, dann **eine Aktion je Lauf**, nachdem
  mir aufgefallen war, dass ein Lauf mit `Invoke` **und** `Select` auf
  denselben Reiter nicht sagt, welcher der beiden gewirkt hat.
- **Eigene Messfehler, die ich gefangen habe** (sie stehen hier, weil sie
  sonst als Programmfehler durchgegangen waeren): (1) `QCursor.setPos` auf die
  Stelle, an der der Zeiger schon steht, erzeugt **kein** `WM_MOUSEMOVE` und
  damit kein Enter — mein erster Hover-Messwert war deshalb leer und sah wie
  eine kaputte Markierung aus. (2) Ein Feld `hovered_while_on_the_card`, das
  ich erst **nach** dem Wegfahren des Zeigers gelesen habe — die Zahl war
  richtig, ihr Name war es nicht. Beide Faelle korrigiert und neu gemessen.
- **Was nichts gebracht hat:** `ElementFromPoint` auf die Kartenmitte liefert
  den Beschreibungstext, nicht die Karte — als Weg zur Karte unbrauchbar, als
  Befund aber aufschlussreich.

---

## Offene Fragen

1. **An den `ui-ux-designer` und den `director`:** Das Fenster gibt sich
   1 320 px. Ab **1 400 px** ist keine Ueberschrift der Effekttabelle mehr
   gekuerzt; bei 1 320 ist genau eine gekuerzt, und es ist die, die zwei
   `power-user`-Laeufe hintereinander gemeldet haben. Ist das Startmass
   Absicht (dann bleibt `Comes with c…` der Normalfall des ersten Blicks) oder
   ein Wert, der vor den heutigen Spaltenregeln gesetzt wurde? Der Schirm
   dieser Maschine (1 707 px) traegt 1 400 muehelos. **Ich entscheide das
   nicht** — es ist eine Breitenentscheidung mit Folgen fuer die
   Mindestmasse, und beide Lesarten sind vertretbar.
2. **An den `developer`:** Koennen zwei gleichzeitig laufende Kopien einen
   **gespeicherten Build** verlieren? Ich habe nur den Schreibvorgang beim
   Beenden belegt (Splitter-Zustand). `set_hidden` und die Migration schreiben
   ganze Listen zurueck; QSettings puffert. Das ist ein schmales Fenster, aber
   nach der Priorisierungsregel des Directors („stumm und persistiert schlaegt
   Zahl zu hoch") die teuerste Richtung. **Ich habe es nicht nachgestellt und
   melde es deshalb nicht als Befund.**
3. **An den `director`, zur Fuehrung von `qa/findings.md`:** **QA-151** steht
   dort auf `offen` mit „braucht ~750-800 ms ruhigen Hovers". Gemessen sind
   heute **175 ms** Sollwert und **266 ms** bis zur Sichtbarkeit am laufenden
   Fenster; der Mechanismus (`HeadingHint`, Commit `49811a8`) steht seit
   T-065 im Baum. Der Eintrag beschreibt einen Stand, den es nicht mehr gibt.
   Ob er auf `behoben` geht, gehoert dir — ich liefere die Messung.

---

## Nicht getestet

- **Der volle Suitelauf unter `QT_QPA_PLATFORM=windows`** (T-068 meldet
  813 passed, 11 skipped). Ich habe den Standardlauf exakt bestaetigt und die
  Windows-Plattform stattdessen dort benutzt, wo sie zaehlt: alle
  Fenstermessungen dieses Berichts liefen unter ihr. Grund fuer das
  Auslassen: ~7 Minuten fuer eine Zahl, die keine Frage dieses Auftrags
  beantwortet.
- **19 der 20 Mutationen aus T-068.** Eine Stichprobe gefahren, die dem
  Symptom am naechsten liegt; sie beisst. Kein Doppel-Testen.
- **Jede Skalierung ausser 150 %** und jede Bildschirmgroesse ausser
  2 560 x 1 600. Insbesondere die Bitte aus T-068, die zehn Kachelnamen bei
  100/125/150/200 % anzusehen — ausserhalb dieses Auftrags.
- **Tastaturbedienung** der Karten (Fokusreihenfolge, Leertaste/Return). Das
  waere der dritte Zugangsweg neben Maus und UIA und gehoert zu QA-161, ich
  habe ihn nicht gemessen.
- **Ein echter Bildschirmleser.** Gemessen ist, was ein UIA-Klient sieht und
  bewirkt; was eine Vorlesesoftware daraus zusaetzlich macht (etwa ein Klick
  auf den `clickablePoint`), ist offen.
- **Die uebrigen Befunde der Zyklen 12/13** (QA-152, QA-157 bis QA-160) —
  Retest war nicht beauftragt.
- **Das gebaute Artefakt (A9).** Weiterhin nie geprueft, in keinem Zyklus.
- **Bildnachweise:** keine erstellt. Der Auftrag verbietet Bildschirmabzuege,
  und alle Aussagen dieses Berichts sind Zahlen und Zustaende aus dem
  laufenden Programm — ein Bild haette keiner davon etwas hinzugefuegt.

---

## QA-Log — Fortschreibung fuer `qa/findings.md`

`qa/findings.md` ist nach Zyklen und Auftraegen gegliedert und rund 1 700
Zeilen lang; ich fuehre es in derselben Form fort, statt alle bisherigen
Zeilen zu wiederholen. Der Director uebertraegt — ich habe die Datei **nicht**
angefasst.

**Anzuhaengender Abschnitt:**

```markdown
## Zyklus 13, T-070: der Regressionsverdacht gegen T-068 (2026-09-06)

Quelle: `docs/berichte/T-070-qa-engineer.md`. Anlass: `docs/berichte/
T-069-power-user.md` meldet Aufgabe 3 als aufgegeben und `Comes with c…`
erneut als unerklaert.

**Ergebnis: keine Regression.** Beide verdaechtigten Aenderungen aus T-068
sind am laufenden Fenster gegen `git archive 264d328` entlastet:

- Die vier `FilterCaption` kosten die Effekttabelle an **zwoelf von zwoelf**
  Fensterbreiten (760 bis 1700 px) **0 px**; die Spaltenbreiten sind in
  beiden Baeumen byteidentisch. `Comes with curse` ist bei 1 320 px (dem
  Startmass) in **beiden** Baeumen gekuerzt und ab **1 400 px** in beiden
  vollstaendig.
- Der Tooltip erscheint am laufenden Fenster nach **266 ms** (Kopf) bzw.
  **279 ms** (Basis) und bleibt ueber 1,2 s stehen. Die 175-ms-Weckverzoegerung
  stammt aus `49811a8` (T-065) und ist Vorfahr von 264d328.
- Die Karte oeffnet sich an **3 510 von 3 510** Pruefpunkten und bei einem
  **echten OS-Klick** auf Mitte, Namenszeile und 3 px vor der Ecke — in
  beiden Baeumen. Die 8-px-Luecke ist in beiden tot. Doppelklick und sechs
  schnelle Klicks: unauffaellig. Die Zeigermarke verschiebt kein
  Kartenrechteck.

**Beide vom Director genannten Fehlerquellen tragen.** Die zweite ist
nachgestellt: zwei gestapelte Kopien des Programms, ein fuer Fenster A
berechneter Klick wird von **B** verarbeitet, A bleibt bei `Select a
Nightlord`.

Suite unveraendert: `-m "not slow"` **815 passed, 9 skipped, 5 deselected`,
`-m "slow"` **5 passed**. Stichprobe der T-068-Waechter:
`nightlord-card-labels-eat-the-press` frisch angewandt -> **1 failed** im
Standardlauf, Fehlertext nennt das Beschreibungslabel.

| ID | Befund | Prio | Schwere | Adressat | Nachweis | Status | Datum |
|---|---|---|---|---|---|---|---|
| QA-161 | **Eine Nightlord-Karte ist ueber die Bedienungshilfen-Schnittstelle nicht bedienbar, und die Schnittstelle meldet Erfolg.** `Invoke` auf das einzige Element namens `Fulghor` (ein `QLabel`) und auf die Karte selbst (`ControlType.Custom`, **ohne Namen**) liefert `INVOKE_OK` und bewegt nichts; **90 von 90** exponierten Elementen melden `InvokePattern`. Gegenprobe: `Invoke` allein auf `TabItem "Deep of Night"` wechselt den Reiter wirklich. **Bestand** — in 264d328 identisch. Hat in 2 von 4 `power-user`-Laeufen Aufgabe 3 gekostet und diesen Regressionsverdacht ausgeloest | P2 | Major | developer | UIA-Klient gegen das laufende Fenster, Urteil aus der `detail_name`-Historie des Programms, beide Baeume | offen | 2026-09-06 |
| QA-162 | **Ein gekuerzter Spaltenkopf gibt der Schnittstelle nur den gekuerzten Text.** `Name` = `Comes with c…` (13 Zeichen, letztes U+2026), `HelpText` bei **allen elf** Koepfen leer. Der volle Name existiert nur, solange der Tooltip steht, und dann als Name eines **eigenen Top-Level-Fensters** `QTipLabel` ausserhalb des Programmbaums. Bei 833 px sind `Copies`, `Colours` und `Comes with curse` darueber nicht unterscheidbar. **Bestand.** Beruehrt A12 und QA-159 | P3 | Minor | developer, ui-ux-designer | UIA-Auslesung aller 11 Kopfelemente, beide Baeume | offen | 2026-09-06 |
| QA-163 | **Kein Schutz gegen eine zweite Instanz.** Drei Suchmasken, 0 Treffer. Nachgestellt: zwei Kopien starten, legen sich deckungsgleich uebereinander, `WindowFromPoint` auf die Karte von A liefert **B**, der Klick oeffnet in B und A bleibt bei `Select a Nightlord`. Beide schreiben in denselben QSettings-Bereich (belegt: `_store_layout` beim Beenden). **Ob ein gespeicherter Build verlorengehen kann, ist nicht nachgestellt** und deshalb nicht behauptet | P3 | Major | developer, director | zwei laufende Kopien, Protokoll im Bericht | offen | 2026-09-06 |
| QA-164 | **Die Zeigermarke wird nur durch Zeigerbewegung aktualisiert** — zwei Faelle, eine Wurzel: (a) nach einem Umbruch des Rasters ohne Zeigerbewegung (1320 -> 900 px, 3 -> 2 Spalten) steht `hovered == ['Fulghor']`, obwohl unter dem Zeiger keine Karte mehr liegt; (b) eine Karte, die unter einem ruhenden Zeiger erscheint, traegt keine Marke. Heilt bei der naechsten Bewegung. **Neu mit T-068** | P4 | Minor | developer, ui-ux-designer | am laufenden Fenster gemessen, `hovered` gegen den tatsaechlichen Vorfahren unter dem Zeiger | offen | 2026-09-06 |

**Statusaenderungen, die der Director zu entscheiden hat:**

| ID | bisher | Messung aus T-070 | Vorschlag |
|---|---|---|---|
| QA-151 | offen — „Tooltip braucht ~750-800 ms" | Sollwert **175 ms** (`HeadingHint`, Commit `49811a8` aus T-065), am laufenden Fenster **266 ms** bis sichtbar, > 1,2 s stehend | **behoben** — der beschriebene Stand existiert nicht mehr |
| QA-154 | behoben (T-068) | bestaetigt: 3 510/3 510 Punkte und 4/4 echte OS-Klicks oeffnen die Karte; die 8-px-Luecke bleibt tot und ist jetzt sichtbar markiert | **behoben** bleibt |
| QA-140 | behoben (T-064) | bestaetigt am laufenden Fenster: gekuerzter Kopf traegt seinen vollen Text und zeigt ihn. **Einschraenkung neu:** gilt nur fuer den Zeiger, siehe QA-162 | **behoben** bleibt, mit Verweis auf QA-162 |
```
