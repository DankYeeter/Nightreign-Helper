# Design & UX Review — Nightreign Helper

## Review vom 2026-09-02 (Sicherheitszyklus T-017/T-018 — sichtbare Folgen, plus QA-029)

**Methode:** Headless, gegen echte Widgets/Funktionen und echte Spieldaten
(`QT_QPA_PLATFORM=offscreen`, `.venv` des Repos, NIGHTREIGN unter
`D:\SteamLibrary\...`, Snapshot bereits unter
`%LOCALAPPDATA%\NightreignHelper\nightreign_data.json` vorhanden, zwei echte
Saves). **Kein Mensch hat die Oberflaeche in diesem Durchlauf gesehen** — das
Fenster liess sich weiterhin nicht fokussieren/anzeigen (Bestand seit
2026-09-01, siehe `docs/state.md`). Jeder Beleg unten ist als **Widget-Abfrage**
(reale Klasse/Funktion aufgerufen, reale Daten, aber kein Rendering angesehen)
oder **Codelesung** markiert — keiner ist visuell.

**Geprüfte Bereiche:** die drei benannten sichtbaren Folgen aus T-017/T-018
(`owned_label`, `nrplanner/bosstab.py` Boss-Detail und `_stance_rank` fuer alle
zehn Nightlords inkl. Everdark-Paare, Fehlermeldungen in `nrplanner/shortcut.py`
und beim Save-/Spieldaten-Lesen), die Build-Namen-Trimm-Frage in
`nrplanner/app.py::_save_build` vs. `nrplanner/chalices.py::save_build`, sowie
ein freier Rundgang durch das, was seit Zyklus 2 an sichtbarem Text neu
dazugekommen ist. QA-029 (veraltete Funktionsnamen in dieser Datei) nachgezogen.

**Gesamturteil:** Braucht Arbeit — nicht wegen der drei angefragten Punkte
(die sind sauber), sondern weil die Recherche zu Punkt 2 eine **Klasse** von
Markup-Injektion offenlegt, die SEC-004/SEC-012 nur an zwei Stellen
(`owned_label`, `bosstab.py`) geschlossen haben, waehrend derselbe Fehler in
drei weiteren, staerker frequentierten Dateien (Relic Picker, Waffen-Slots)
unveraendert steht, und weil eine Kombination aus bestehendem Code und dem
neuen SEC-002-Fix eine echte Aussage ("ein Save existiert, ist aber kaputt")
in eine falsche verwandelt ("kein Save gefunden").

---

### Entscheidung (Punkt 1 des Auftrags): Build-Namen im Dialog trimmen — ja, beibehalten

`nrplanner/app.py:2354` (`_save_build`): `name = (name or "").strip()`.
`nrplanner/chalices.py:319-324` (`save_build`) trimmt seit T-018 bewusst
**nicht** mehr — der Name kommt exakt so zurueck, wie er gespeichert wurde.

**Aus Nutzersicht bleibt das Trimmen im Dialog richtig, die Speicherschicht
soll trotzdem nicht trimmen — beides gleichzeitig, keine Symmetrie
erzwingen:**

- Ein Build-Name ist fuer den Spieler ausschliesslich das, was in der
  Dropdown-Liste (`build_box`) steht. Ein Leerzeichen am Ende ist dort in den
  allermeisten Schriftbildern **unsichtbar** — ein Spieler, der "Build" tippt,
  spaeter aus Versehen "Build " (Leerzeichen am Ende, z. B. durch Copy-Paste
  oder verrutschten Cursor) speichert, saehe zwei Eintraege, die identisch
  aussehen und sich nicht unterscheiden lassen, ausser durch Ausprobieren.
  Das ist keine Funktion, die sich irgendjemand wuenscht — es ist eine Falle,
  die die Namens-/Schluessel-Trennung aus T-018 (bewusst, korrekt: Namen
  koennen jetzt `/`, `\`, Unicode, fuehrende Leerzeichen tragen) als
  Nebenwirkung neu eroeffnet.
- Waere das Trimmen entfernt, koennte genau der Fall entstehen, den die
  Aufgabenstellung selbst nennt: "Build" und "Build " als zwei Eintraege —
  nur dass das nicht wie eine bewusste Namensgebung wirkt (ein Spieler, der
  zwei *sichtbar* verschiedene Namen fuer zwei Builds waehlt, weiss, was er
  tut), sondern wie ein Karteikarten-Duplikat, das das Programm haette
  verhindern sollen.
- Die Speicherschicht **soll** trotzdem nicht trimmen: sie ist die einzige
  Stelle, die weiss, was exakt gespeichert wurde, und ihr Vertrag ("der Name
  kommt zurueck, wie er reinging") ist wertvoll unabhaengig davon, ob der
  einzige heutige Aufrufer vorher schon normalisiert. Ein kuenftiger zweiter
  Aufrufer (z. B. eine Import-Funktion, die Namen aus einer Datei uebernimmt)
  soll sich nicht auf eine Trimm-Regel verlassen muessen, die nur zufaellig
  in `_save_build` sitzt.
- Der Dialog sollte also **weiterhin** trimmen, aber das ist eine UI-Regel
  ("was der Spieler als Namen zu erkennen glaubt"), keine Speicherregel.

**Kein Code geaendert** (nicht meine Aufgabe) — dies ist die angeforderte
Leitentscheidung an den `developer`: **Trimmen im Dialog bleibt.** Kleinerer
Folgepunkt, keine eigene Finding-Nummer wert: `if not ok or not name: return`
(Zeile 2355) bricht bei einem rein aus Leerzeichen bestehenden Namen lautlos
ab, ohne Hinweis, dass eingegeben wurde. Das ist Bestand (nicht durch T-018
veraendert) und niedrigste Prioritaet — Erwaehnung, damit es nicht verloren
geht, kein DR-Eintrag.

---

### Kritisch

- **DR-004 [`nrplanner/relicpicker.py:89`, `nrplanner/weaponslots.py:173-176`
  und `:208-221`, `nrplanner/app.py:416/434` (`show_slots`), `:614`
  (`curse_tooltip`)]** SEC-004/SEC-012 sind **als Klasse nicht geschlossen** —
  das steht in `security/findings.md` (SEC-012-Log-Zeile) schon so, aber die
  Suche nach "welche Dateien haben ueberhaupt `setTextFormat`" zeigt, wie
  gross die Luecke tatsaechlich ist: **im gesamten Baum stehen genau vier
  Aufrufe** (`app.py:1465` `owned_label`, `app.py:1665` `qual_heading`,
  plus zwei in `bosstab.py`). `nrplanner/relicpicker.py`,
  `nrplanner/weaponslots.py`, `nrplanner/effectstab.py` und
  `nrplanner/arsenaltab.py` haben **keinen einzigen**. Zwei belegte, konkrete
  Stellen (Widget-/Codeabfrage, mit echten Namen aus dem geladenen Snapshot
  gegengeprueft):
  - `RelicCard` (der Karten-Titel im Relic Picker, dem am meisten genutzten
    Bildschirm des Programms nach eigener Beschreibung in `UI_SPEC.md`, "292
    Relikte"): `title = QLabel(item.name)` — `item.name` ist ein
    Reliktname aus den Spieldaten, `title` traegt kein `setTextFormat`, bleibt
    also auf `Qt.AutoText`. Dieselbe Fehlerklasse wie die urspruengliche
    SEC-004-Reproduktion ("ein Slotname mit `<img src=...>` wird als Bild
    gerendert statt als Name gezeigt"), nur nicht im Save-Datenpfad, sondern
    im Reliktnamen-Pfad — beide sind laut dem eigenen Nachtrag in
    `UI_SPEC.md` §3.5 ausdruecklich dieselbe Kategorie ("Save- **und**
    Spieldateien").
  - Waffen-Slot-Kachel (`WeaponTile.show_slot`, `weaponslots.py:220-221`):
    `self.title.setText(f"<span style='color:{colour}'>{slot.weapon['name']}"
    f"</span>")` — der Waffenname wird **per Konkatenation in eine
    Rich-Text-Zeichenkette eingesetzt**, exakt das Muster, das SEC-012 in
    `bosstab.py::_stance_rank` schon als Befund kannte und dort mit
    `html.escape()` schloss. Hier fehlt das Escaping vollstaendig, und
    `self.title` traegt ebenfalls kein `setTextFormat` — das umgebende
    `<span>` zwingt es ohnehin auf Rich-Text-Rendering.
  - Zusaetzlich, niedrigere Ausnutzbarkeit, aber dieselbe Ursache:
    `curse_tooltip()` (app.py:638-651) baut einen Tooltip-Text aus
    Effekt-/Fluchnamen (`effecttext.name`, aus Spieldaten) ohne Escaping;
    Tooltips erkennen Rich Text immer automatisch (dasselbe Argument, mit
    dem SEC-013 fuer `owned_label`s Tooltip begruendet wurde). Ebenso
    `show_slots` (app.py:416, 434): `tile.setToolTip(getattr(owned, "name",
    "") or "empty slot")` fuer die Kelch-Vorschau-Kacheln der Heldenkarten.

  **Nicht mein Befund als Sicherheitsurteil** — das ist Sache des
  `security-reviewer`, der eine SEC-Nummer und eine Ausnutzbarkeitsbewertung
  vergeben muss (insbesondere: Reliktnamen stammen aus dem Spiel, nicht aus
  dem Save selbst, das Bedrohungsmodell "von einem Freund geschenktes Save"
  greift hier also schwaecher als bei `owned_label`; das Bedrohungsmodell
  "manipulierte/gemoddete Spielinstallation" dagegen genauso wie bei
  SEC-004/SEC-012 Boss-Namen). Ich melde es hier, weil es exakt das ist, was
  Punkt 2 des Auftrags verlangt hat ("sichtbare Folgen der Sicherheitsfixes
  pruefen") und weil es sonst zwischen den drei parallelen Pruefspuren
  verloren geht.

  **Loesungsrichtung:** dieselben zwei Muster, die das Projekt sich bereits
  selbst vorgeschrieben hat (`UI_SPEC.md` §3.5, dort fuer den noch nicht
  gebauten Advisor formuliert, aber inhaltlich unabhaengig vom Advisor
  richtig) auf die vier genannten Dateien ausdehnen:
  `setTextFormat(Qt.PlainText)` auf jedem `QLabel`, das nur Namen zeigt, und
  `html.escape()` auf jedem in `<span>`/`<b>`-Markup eingesetzten Namen. Fuer
  Tooltips (die kein `setTextFormat` kennen) bleibt nur `html.escape()`.

### Wichtig

- **DR-005 [`nrplanner/inventory.py:204-213` (`_scan_save`),
  `nrplanner/app.py:2997-3011` (`rescan_save`)]** Verifiziert durch direkten
  Aufruf der Produktionsfunktion mit einer synthetisch beschaedigten
  BND4-Struktur (Beleg unten). Die neue, laute Fehlerbehandlung aus SEC-002
  (`savefile._members` wirft jetzt `ValueError`, statt eine Vier-Milliarden-
  Schleife zu versuchen) erreicht den Spieler **nie**: `_scan_save` faengt
  jede Exception pro Save-Kandidat ab und liefert einfach `best` weiter — bei
  genau einem, kaputten Save also `None`. `rescan_save` unterscheidet das
  nicht von "kein Save vorhanden" und zeigt:

  ```
  No save file found. Relic slots stay empty; the Effects and Weapons tabs
  still work in full.
  ```

  Das ist eine **falsche Tatsachenaussage**, kein Fall von "die Daten geben
  keine Antwort her" — ein Save existiert, er ist nur nicht lesbar. Das
  verstoesst gegen GOAL A7 in genau der Weise, die der Sicherheitszyklus
  eigentlich beheben sollte: statt eines Einfrierens (SEC-001) oder einer
  Allokation (SEC-002) bekommt der Spieler jetzt eine ruhige, aber falsche
  Antwort. Verwandt mit dem bereits offenen **QA-008** ("No save file found."
  bei vorhandenem Save ohne Relikte) — dieselbe Nachricht, dritte
  unterschiedliche wahre Ursache, aber die schwerwiegendste bisher: hier wird
  eine erkannte Sicherheitsverletzung stillschweigend geschluckt, nicht nur
  eine leere Inventarliste.

  Beleg (Widget-/Funktionsaufruf, `.venv`, echte `inventory.load`):
  ```
  raised as expected: ValueError save container claims 4000000000 members of
  24 bytes each, which do not fit in 100 bytes
  inventory.load result: None
  ```

  **Loesungsrichtung:** `_scan_save` soll den Grund festhalten statt ihn zu
  verschlucken (Muster existiert bereits: `Inventory.loadout_error`, das
  fuer genau diesen Zweck bei gespeicherten Builds gebaut wurde — derselbe
  Mechanismus fuer die Save-Erkennung selbst). `rescan_save` unterscheidet
  dann "keine Datei gefunden" von "eine Datei gefunden, aber unlesbar: …" —
  fuer Letzteres taugt exakt der Ton, den `owned_label` an anderer Stelle
  schon benutzt (`"Save could not be read: {exc}"`).

- **DR-006 [`nrdata/savefile.py:61-65`, `nrplanner/app.py:3003`,
  `nrplanner/app.py:3654-3656` (`firstrun`-Fehlerdialog)]** Wo eine
  SEC-001/002/005/010/014-Fehlermeldung tatsaechlich beim Spieler ankommt
  (First-Run-/Rebuild-Fehlerdialog "Could not read your game:\n\n{error}"; im
  Prinzip auch `owned_label`, dort aber durch DR-005 praktisch unerreichbar),
  ist der Text Englisch (A8 erfuellt) und ehrlich (kein Raten), aber **nicht
  verstaendlich fuer einen Spieler ohne Technikhintergrund** und **ohne
  naechsten Schritt**: `"save container claims 4000000000 members of 24
  bytes each, which do not fit in 100 bytes"` oder `"a DDS header is 128
  bytes, this file is 45"` sind Parser-interne Groessen, keine Spieler-
  Sprache. Die einbettende Zeile ("Could not read your game:") ist gut, der
  Rest liest sich wie eine Stacktrace-Zeile.
  Nicht kritisch, weil der Zustand selbst (statt Einfrieren/Abstuerzen) schon
  der Fortschritt ist, und weil er in der Praxis fast nur bei einer
  manipulierten Installation eintritt — aber es lohnt sich, bevor ein Spieler
  das je zu Gesicht bekommt: eine Zeile in Spielersprache **vor** dem
  technischen Detail, z. B. "The game's own files look damaged or modified,
  so this could not be read safely." — technischer Rest bleibt als Beleg
  dahinter stehen, muss aber nicht die erste Zeile sein.

### Nice-to-have

- **DR-007 [`nrplanner/shortcut.py:118-120`]** Verifiziert per Codelesung.
  Die Meldung, wenn Windows PowerShell nicht am erwarteten Ort liegt:
  `"Windows PowerShell was not found where Windows keeps it
  (%SystemRoot%\System32\WindowsPowerShell\v1.0), so the shortcut cannot be
  written."` — Englisch (A8 erfuellt), ehrlich, nennt die Konsequenz. Fuer
  einen Spieler ohne Technikhintergrund ist `%SystemRoot%\...\v1.0` trotzdem
  Fachjargon, und es fehlt ein naechster Schritt (weil es faktisch keinen
  gibt — PowerShell fehlt auf einem Standard-Windows praktisch nie). Sehr
  niedrige Prioritaet: der Pfad ist fuer die Fehlersuche wertvoll, koennte
  aber in Klammern/Tooltip statt im Fliesstext stehen, damit der erste Satz
  ohne Windows-Interna auskommt.

### Backlog (geparkt)

- `Could not parse stylesheet of object QListWidget(...)` (aus dem
  2026-09-01-Durchlauf) — nicht erneut geprueft, unveraendert im Backlog.

---

### Positiv / beibehalten

- **Boss-Tab-Escaping haelt, gegen alle zehn Nightlords inkl. Everdark-Paare
  geprueft (Widget-Abfrage gegen den echten, geladenen Snapshot dieses
  Rechners).** `_stance_rank()` (`bosstab.py:445-468`) escaped `other["name"]`
  fuer beide genannten Bosse in jeder der zehn Zeilen; da kein Nightlord-Name
  (auch nicht "Heolstor the Nightlord") ein Zeichen traegt, das `html.escape`
  veraendert, ist der sichtbare Text vor und nach dem Fix identisch — keine
  `&amp;`-Artefakte, keine Regression. `detail_name`/`detail_text` stehen
  beide auf `Qt.PlainText` und zeigen `boss["name"]`/`boss["description"]`
  unveraendert.
- **`owned_label` verliert durch `Qt.PlainText` keine Formatierung** — per
  Git-Historie geprueft (`4c55860`, vorher/nachher): das Label hat nie
  eingebettetes Rich Text (Fettung, Farbe, Link) benutzt, nur zusammengesetzte
  Klartext-Saetze. Der aktuelle Text ist ohne Auszeichnung ausreichend; nichts
  geht verloren.
- **`_migrate_keys`/`build_key` (T-018, QA-003) sind sauber injektiv gebaut**
  (`%`-Zeichen wird mitkodiert, kein Name kann die Kodierung eines anderen
  erzeugen) — die Namens-/Schluessel-Trennung selbst ist eine gute Grundlage;
  siehe Entscheidung oben zum Trimmen, die genau darauf aufbaut.
- Die im 2026-09-01-Durchlauf bestaetigte Handle-Regel (QA-002-Kernfix) ist
  laut `qa/findings.md` inzwischen auch fuer den Restore-Pfad geschlossen
  (QA-021, T-015) — siehe Nachtrag oben.

### Offene Fragen an den App Designer

*(keine neuen in diesem Durchlauf — Punkt 1 war eine dem Designer
zugeschobene Frage, aber der Auftrag selbst nennt sie eine Nutzerfrage, die
hier mit einer Begruendung beantwortet wird, keine Geschmacksfrage ohne
objektiv richtig/falsch.)*

**Hinweis an den Director:** DR-004 sollte parallel beim
`security-reviewer` ankommen (SEC-Nummer, Ausnutzbarkeit, Prioritaet) — ich
kann das als UX-Befund nur benennen, nicht sicherheitstechnisch einordnen.

---

## Review vom 2026-09-01 (T-008 — sichtbare Auswirkungen von T-006)

> **Nachtrag 2026-09-02 (QA-029):** `select_saved` und `select_handle`, an
> drei Stellen unten genannt, gibt es seit T-015 nicht mehr — ersetzt durch
> `RelicSlot.select_copy` (handle-genau) und `RelicSlot.select_roll`
> (Roll-Fallback). Die Stellen sind unten in eckigen Klammern korrigiert,
> nicht stillschweigend umgeschrieben, damit der historische Befundtext
> nachvollziehbar bleibt. **DR-002 ist behoben** ✔ 2026-09-02 — siehe Marke
> bei der Fundstelle und den neuen Durchlauf oben.

**Methode:** Gemischt. Ein echter Start gelang (Screenshot unten, First-Run-Dialog,
`design-review/2026-09-01/00-startup.png`), danach liess sich das App-Fenster in
dieser Umgebung wiederholt nicht mehr sichtbar/fokussierbar machen — mehrere
Neustarts blieben bei 0 % CPU und ohne erzeugtes Qt-Top-Level-Fenster stehen
(nur die Konsole war als Fenster auffindbar), vermutlich ein Artefakt der
Session/Fenster-Fokus-Regeln dieser Sandbox, kein Befund am Programm selbst.
Die drei konkret angefragten Punkte und die weiteren T-006-Auswirkungen sind
daher **Code-Analyse**, ergänzt um ein bereits im Repo vorhandenes,
mitgeliefertes Referenz-Screenshot (`docs/screenshots/build_planner.png`,
Stand vor T-006, aber für den betroffenen Codepfad unverändert — siehe DR-003).
Alle Befunde unten sind entsprechend als **unverifiziert (Code-Analyse)**
markiert, mit exakten Zeilenverweisen, damit qa-engineer sie gegen ein
laufendes Artefakt leicht nachstellen kann.

**Geprüfte Bereiche:** `RelicSlot`-Kopfzeile und -Kartenkörper
(`nrplanner/app.py`), `RelicPicker`-Zusammenfassungszeile
(`nrplanner/relicpicker.py`), Waffen-Slot-Kacheln (`nrplanner/weaponslots.py`)
und das Waffenschaden-Panel (`Planner._refresh_weapon_damage`,
`nrplanner/app.py:2472+`), Restore-Pfade (`select_saved` [seit T-015:
`select_roll`], `select_handle` [seit T-015: `select_copy`],
`_apply_saved_state`/Kelchwechsel um `app.py:2040-2059`).

**Gesamturteil:** Fast fertig, aber nicht ship-ready — die Handle-Regel selbst
(T-006, QA-002) ist sauber umgesetzt und die Wortwahl der Kopfzeile ist richtig;
das offene Problem ist, dass ihre Auswirkung an zwei Stellen für den Spieler
unsichtbar bleibt: einmal harmlos (Picker nennt keinen Grund), einmal mit
echtem Vertrauensschaden (ein wiederhergestellter alter Build zählt eine
Duplikat-Relikt kurzzeitig doppelt und verliert sie dann kommentarlos).

---

### Kritisch

- **DR-002 ✔ behoben 2026-09-02 (QA-021, T-015) [`nrplanner/app.py:676-747`,
  `:2040-2059`, `:2362-2372`]** Ein
  **wiederhergestellter alter Build** (Kelchwechsel-Restore, `select_saved`
  [seit T-015: `select_roll`]/`select_handle` [seit T-015: `select_copy`])
  mit einem physisch doppelt besessenen Relikt in zwei Slots
  zeigt **beide Slots korrekt befüllt und beide Werte im Statblatt gezählt**
  — die Handle-Regel greift beim Restore nicht, weil der Restore-Pfad
  `recompute()` aufruft, nicht `_relic_changed()`, und `populate()` (welches
  filtert) deshalb nicht erneut läuft (Code-Beleg: `_apply_saved_state`-artiger
  Block `app.py:2040-2059` endet in `self.recompute()`, nicht in
  `self._relic_changed()`). Erst wenn der Spieler danach **irgendeinen**
  Slot ändert, läuft `_relic_changed()` → `populate()` für alle Slots, und
  genau der Slot mit dem **niedrigeren Index** der beiden Duplikat-Halter
  verliert sein Relikt (nachvollzogen über `available_items()`,
  `app.py:693-702`: beim iterativen Repopulate sieht der zuerst behandelte
  Slot das Relikt noch beim anderen Slot als "belegt" und wird geleert; der
  danach behandelte Slot findet es frei und behält es — deterministisch nach
  Slot-Reihenfolge, nicht zufällig).

  **Zwei Probleme in einem:**
  1. Direkt nach dem Restore ist das Statblatt für genau diesen Fall wieder
     falsch (derselbe Fehlerklasse wie QA-002, nur im Restore-Pfad
     überlebend) — ohne jeden Hinweis.
  2. Der spätere, durch eine unabhängige Handlung ausgelöste Verlust des
     Relikts in einem der beiden Slots ist **lautlos**: die Kopfzeilenzahl
     sinkt, der Slot zeigt "Empty slot", nirgends steht warum.

  Das widerspricht der eigenen Hausregel des Projekts (GOAL A7 — Unsicherheit/
  Änderung wird ausgesprochen, nicht verschwiegen) und dem Muster, das QA-002
  ursprünglich als P1/Major eingestuft hat ("plausible Zahl, keine Warnung").

  **Empfohlene Lösung, zwei Teile:**
  - **Zeitpunkt vorziehen:** Die Bereinigung sollte **beim Restore selbst**
    laufen (z. B. `populate()` für alle Slots nach dem `select_saved`-Loop
    [seit T-015: `select_roll`/`select_copy`] vor
    `recompute()`, statt erst beim nächsten fremden Slot-Wechsel) — dann ist
    das Statblatt nie kurzzeitig falsch, und die Erklärung kann sofort stehen,
    statt auf eine zufällige Folgeaktion zu warten.
  - **Text am betroffenen Slot**, sobald er dadurch geleert wird — nicht nur
    stillschweigend "Empty slot". Vorschlag, im Ton des Programms (vgl.
    `"Already equipped — nothing to change here."` aus der bestehenden
    `UI_SPEC.md` §3.2, `"No save was read, so there are no relics to choose
    from — use Rescan save."` aus §4.8):

    ```
    Already worn in Slot 2 — pick another relic for this slot.
    ```

    Platzierung: dort, wo bei einem leeren Slot heute nichts steht —
    `rolled_label` wird bei `item is None` aktuell komplett geleert und
    versteckt (`_sync_mode`, `app.py:523-530`). Der Text passt in dieselbe
    Fläche (`MUTED`, `setWordWrap(True)`, bereits vorhanden), erfordert also
    keinen neuen Bereich — nur dass der Slot sich merkt, *warum* er geleert
    wurde, und das dem generischen "leer, nie befüllt" vorzieht.

  **Empfehlung an den Director:** Das ist inhaltlich ein Wiederauftauchen von
  QA-002 in einem Pfad, den T-006 nicht abgedeckt hat. Ob das QA-002 wieder
  öffnet oder eine neue QA-Nummer bekommt, entscheidet der `qa-engineer` — ich
  liefere hier nur die Nutzeraussage, nicht die Priorisierung der zugrunde
  liegenden Rechenkorrektheit.

  **Behoben-Vermerk 2026-09-02:** `qa/findings.md` fuehrt QA-021 (T-015) als
  "behoben" — "beim Restore aufgeloest, erster Slot behaelt, Zahl sofort
  richtig" — und QA-002 selbst als "behoben ... interaktiv und ueber
  gespeicherte Builds". Der Wortlautvorschlag oben ("Already worn in Slot
  2 — pick another relic for this slot.") ist laut `qa/findings.md` Zeile
  111-113 tatsaechlich der Wortlaut, den QA-015 fuer den Hinweis nach dem
  Aufloesen uebernommen hat. Ich habe das **nicht selbst erneut nachgetestet**
  (ausserhalb des Auftrags 2026-09-02, Status aus dem QA-Register
  uebernommen) — bei Zweifel gilt `qa/findings.md` als Quelle, nicht diese
  Zeile.

---

### Wichtig

- **DR-001 [`nrplanner/app.py:738-746` (Kopfzeile), `nrplanner/relicpicker.py:479-492`
  (Picker-Zusammenfassung)]** Die vom `developer` vorgelegte Umbenennung
  **"N owned" → "N available" ist korrekt und wird bestätigt** — die Zahl zählt
  jetzt tatsächlich, was dieser Slot bekommen kann, und "available" ist dafür
  das richtige Wort (kein neuer Begriff nötig, keine Kollision mit anderer
  Verwendung von "available" im UI-Text geprüft). **Kein Wortlautwechsel
  empfohlen.**

  Was fehlt, ist nicht das Wort, sondern die **Begründung dahinter**: Die Regel
  "ein physisches Relikt kann nicht in zwei Slots liegen" steht heute nur im
  README (Commit `2766229`), nirgends im Programm selbst. Zwei Stellen, an
  denen ein Spieler auf die Regel stösst, ohne sie erklärt zu bekommen:
  - Die Kopfzeile selbst — kein Tooltip auf `self.title` (`app.py:478-480`;
    `setToolTip` kommt im ganzen `RelicSlot` nirgends vor).
  - Der Picker — ein Relikt, das der Spieler besitzt, aber gerade in einem
    anderen Slot trägt, ist in der Liste **restlos abwesend**, und die
    Zusammenfassungszeile ("N of N relics", `relicpicker.py:487-492`) sagt
    nichts dazu, dass die Gesamtzahl bereits um solche Relikte reduziert ist.
    Ein Spieler, der ein bekanntes Relikt sucht und es nicht findet, hat
    keinen Anhaltspunkt, ob es fehlt, weil es nirgends passt, oder weil es
    schon anderswo liegt.

  **Lösungsrichtung:** Tooltip auf die Slot-Kopfzeile, wörtlich aus dem README
  übernommen (Konsistenz zur bereits verifizierten Prosa):

  ```
  A relic already in a slot is not offered in the others — you own one of
  it, and it can only be worn once.
  ```

  Im Picker genügt niedrigere Priorität: entweder derselbe Tooltip auf der
  Zusammenfassungszeile, oder — falls das zu teuer zu ermitteln ist, wie viele
  Relikte aus diesem Grund fehlen — zumindest ein Verweis auf "Custom relic"
  als Ausweg, wenn die Trefferliste für eine Farbe ungewöhnlich kurz ausfällt.
  Das ist eine kleinere Ergänzung als DR-002 und blockiert nichts.

- **DR-003 [`nrplanner/weaponslots.py:227-228` vs. `nrplanner/app.py:2527-2538`]**
  Bestätigt, **Bestand, nicht durch T-006 verursacht** — aber neu relevant, weil
  T-006 die Rechnung genau der Zahl, die fehlt, nach `nrplanner/damage.py`
  zentralisiert hat (`attack_rating()`), was die Behebung jetzt deutlich
  billiger macht als vorher.

  Die sechs Waffen-Slot-Kacheln zeigen `rating.total` aus `weapons.rate()`
  (reine Attributskalierung, **ohne** Relikt-/Fluch-Multiplikatoren,
  `weaponslots.py:227-228`: `f"<b style='color:{ACCENT}'>{rating.total:.0f}</b> AR"`).
  Das Panel für den aktiven Slot rechnet mit `damage.attack_rating()` **inklusive**
  aller Multiplikatoren und zeigt `Total {base} → {final}` (`app.py:2530-2538`).
  Für dieselbe Waffe stehen dadurch zwei verschiedene Zahlen gleichzeitig auf dem
  Bildschirm. Am mitgelieferten Referenz-Screenshot (kein Fluch-Fall, aber
  derselbe Mechanismus, Code-Pfad seit T-006 unverändert) belegt:
  Kachel "Wylder's Greatsword — Common · **203 AR**", Panel darunter
  "Total 203 +12 **216** (+6.0%)" — 6,4 % Differenz zwischen den beiden
  gleichzeitig sichtbaren Zahlen für dieselbe Waffe.

  ![Kachel 203 AR vs. Panel Total 216](docs/screenshots/build_planner.png)

  Relevanz für den kommenden Build-Berater: `UI_SPEC.md` AK-24 verlangt, dass
  der Berater "Schaden maximieren" konsistent mit dem bewertet, was das
  Programm sonst als Wahrheit ausweist — das ist eindeutig die Panel-Zahl
  (die einzige mit vollem Multiplikatorsatz). Bleibt die Kachel bei der
  unmultiplizierten Zahl, kann ein Spieler beim manuellen Waffenvergleich zu
  einer anderen Reihenfolge kommen als der Berater, ohne dass der Widerspruch
  irgendwo benannt wird — insbesondere weil klassengebundene Multiplikatoren
  (`model.WEAPON_CLASS_PREFIX`) Waffen unterschiedlich stark verschieben
  können, die Kachel-Reihenfolge also nicht einmal proportional zur echten
  ist.

  **Lösungsrichtung (bevorzugt):** Kacheln auf dieselbe `damage.attack_rating()`
  umstellen, die das Panel schon nutzt — durch die T-006-Extraktion technisch
  jetzt eine einzige zusätzliche Aufrufstelle, kein Duplikat einer Rechnung
  mehr. **Fallback**, falls das an fehlendem Build-Kontext beim Kachel-Rendern
  scheitert: Kachel-Beschriftung von "AR" auf "Base AR" ändern, damit die
  beiden Zahlen als unterschiedliche Grössen erkennbar sind, statt als
  Widerspruch zu wirken.

---

### Nice-to-have

*(keine eigenen Punkte in diesem Durchlauf — Backlog unten)*

---

### Backlog (geparkt)

- `Could not parse stylesheet of object QListWidget(...)` erscheint bei jedem
  Start in `stderr` (beobachtet während der Startversuche). Nicht geprüft, ob
  T-006-bezogen oder älter; kein sichtbarer UI-Schaden erkennbar, aber ein
  Stylesheet, das Qt nicht parsen kann, ist meist ein totes CSS-Fragment.
  Für den `developer` zum Aufräumen bei Gelegenheit, keine Priorität hier.

---

### Positiv / beibehalten

- Die Handle-Regel selbst (QA-002-Fix) ist im Kern richtig gebaut:
  `available_items()` schliesst korrekt nur das *physische* Duplikat aus
  (`copy_key`), nicht die Rolle, und lässt den eigenen Slot unangetastet
  (`taken_elsewhere` überspringt `asking`). "Custom relic" bleibt unangetastet
  von der Regel, exakt wie in `UI_SPEC.md` gefordert.
- Die Wortwahl "N available" statt "N owned" ist präziser als vorher und
  stimmt jetzt mit der Picker-Zusammenfassung überein (beide zählen über
  `available_items()`) — die alte Diskrepanz "50 owned" vs. "49 of 49" ist
  behoben.
- Der First-Run-Dialog (`design-review/2026-09-01/00-startup.png`) ist klar,
  nennt eine ehrliche Zeitangabe ("about a minute") und lässt während der
  Wartezeit nichts rätseln.

---

### Offene Fragen an den App Designer

*(keine — beide Entscheidungen in diesem Durchlauf sind fachlich eindeutig:
Wortlaut bestätigt in DR-001, Timing/Text in DR-002 sind UX-Notwendigkeiten,
keine Geschmacksfragen.)*

**Hinweis an den Director:** DR-002 berührt möglicherweise, ob QA-002 als
"geschlossen" gelten darf (GOAL A2: kein Release, solange QA-001/QA-002 offen
sind) — das ist eine Priorisierungsfrage für `qa-engineer`/Director, keine
Design-Frage, aber sie sollte nicht zwischen den Berichten verloren gehen.
