# Design & UX Review — Nightreign Helper

## Review vom 2026-09-01 (T-008 — sichtbare Auswirkungen von T-006)

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
`nrplanner/app.py:2472+`), Restore-Pfade (`select_saved`, `select_handle`,
`_apply_saved_state`/Kelchwechsel um `app.py:2040-2059`).

**Gesamturteil:** Fast fertig, aber nicht ship-ready — die Handle-Regel selbst
(T-006, QA-002) ist sauber umgesetzt und die Wortwahl der Kopfzeile ist richtig;
das offene Problem ist, dass ihre Auswirkung an zwei Stellen für den Spieler
unsichtbar bleibt: einmal harmlos (Picker nennt keinen Grund), einmal mit
echtem Vertrauensschaden (ein wiederhergestellter alter Build zählt eine
Duplikat-Relikt kurzzeitig doppelt und verliert sie dann kommentarlos).

---

### Kritisch

- **DR-002 [`nrplanner/app.py:676-747`, `:2040-2059`, `:2362-2372`]** Ein
  **wiederhergestellter alter Build** (Kelchwechsel-Restore, `select_saved`/
  `select_handle`) mit einem physisch doppelt besessenen Relikt in zwei Slots
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
    laufen (z. B. `populate()` für alle Slots nach dem `select_saved`-Loop vor
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
