# Stand

Stand: 2026-09-02, Ende Zyklus 4. Branch `docs/audit-and-advisor-design`,
20 Commits. **Push vom Director freigegeben** nach gruenem QA-Durchlauf.
Pull Request #16 offen — **Merge nach `main` gehoert dem Nutzer**, `main` ist
geschuetzt.

## Wo wir stehen
- Nightreign Helper, PySide6/Qt, ~17k Zeilen Python, Windows-only.
- Zyklus 1 = Audit (nur Doku). Zyklus 2 = eine Rechenstelle, nachweislich
  unveraendert. Zyklus 3 = der Sicherheitszyklus, der nie gelaufen war.
  Zyklus 4 = der Datenverlust, den Zyklus 3 selbst erzeugt hat.
- **Testsockel 78 -> 167.** Und erstmals belegt statt behauptet: der
  `qa-engineer` faehrt eigene Laufzeitmutationen statt uebernommener
  Entwicklertests. Das hat in beiden Zyklen jeweils das Entscheidende gefunden.

## Was Zyklus 3 und 4 geschlossen haben
**Zwoelf Sicherheitsbefunde**, alle mit bestandenem adversarialem Retest, kein
Fix umgehbar: SEC-001, 002, 004, 005, 006 (Deckel), 007, 008, 010, 012, 013,
014.
**Elf QA-Befunde:** QA-003, QA-005 (teilweise), QA-024, QA-033, QA-034,
QA-035, QA-039, QA-040, QA-041, QA-042, QA-043, QA-045.

Belegt gegen echte Daten, nicht gegen sich selbst:
- **SEC-001:** der Vor-Fix-Stand haengt an einem echten praeparierten Save
  (nach 20 s zwangsbeendet), der heutige meldet es in 0,01 s, Fenster in 1,8 s
  bedienbar.
- **QA-003/033/041:** 15 Namensformen ueber die echte Oberflaeche, ein
  Mischstore aus zu langem Namen, Schraegstrich, senkrechtem Strich und
  Prozentzeichen, Ketten der Laenge 2 bis 4 in beiden Reihenfolgen, und fuenf
  echte Programmstarts mit **byteweise identischem** Store-Dump.

**Die ehrliche Bilanz:** Zwei Datenverluste sind in diesem Zyklus entstanden
und wieder geschlossen worden — **beide aus dem Fix fuer QA-003, keiner aus
dem Altbestand.** Eine Migration, die Nutzerdaten anfasst, hat drei Developer-
und drei QA-Runden gebraucht, bis sie nichts mehr zerstoert.

**Nebenbefund mit Folgen:** Der Testsockel aus Zyklus 2 belegte die Parser
nicht (`conftest.py` nahm den Snapshot-Cache; fuenf Parser liefen in einem
gruenen Lauf gar nicht). Als DEBT-001 geschlossen.

## Was das Release sperrt
1. **QA-046 (P2, Critical)** — zwei Build-Namen, die sich nur in der
   Gross-/Kleinschreibung unterscheiden, teilen sich einen Speicherplatz; der
   zweite ueberschreibt den ersten still, das Loeschen des einen loescht beide.
   QSettings-Wertnamen sind auf Windows case-insensitiv, `build_key` ist
   injektiv gegen Python-Strings, **nicht gegen die Registry**. **Keine
   Regression dieses Zyklus** — galt im alten Format genauso. Braucht ein
   drittes Schluesselschema und eine erneute Wanderung.
2. **QA-036 (P2)** — die Vollstaendigkeit des Icon-Packs wird nie geprueft.
   Das Pack des Nutzers war am 2026-09-02 zu 88 % leer (105 von 839 Dateien);
   **wiederhergestellt am 2026-09-02** ueber `scripts/build_icons.py`, 840
   Dateien, ueber die Programm-API verifiziert. **Die Ursache ist offen:**
   `iconbuild.build` leert das Ziel ohne Sperre.
3. **QA-018** — Waffen-Tab 203,4 gegen Detailtafel 244,1.
4. **SEC-009**, nur zwei Punkte: Release-Action auf beweglichem Tag in einem
   Job mit `contents: write`, und keine Pruefsumme. Zusammen unter zehn Zeilen
   YAML. Signatur und `--require-hashes` sind akzeptiertes Restrisiko.
5. **GOAL A9** — noch nichts gegen ein gebautes Artefakt geprueft.
6. **C-002** (`nightlords.png`, Ampel ROT) — Entscheidung des Nutzers.

## Naechster Zyklus (Zyklus 5), geordnet
1. **QA-046** — eigener Auftrag, mit derselben Ruecklesungs-Nachbedingung wie
   T-020, und der Kommentar bei `_KEY_SAFE` gehoert korrigiert ("injective"
   gilt nicht gegen den Store).
2. **QA-032 + QA-004** — beschaedigtes Save wird still uebersprungen;
   entschieden ist Lesart B, der Spieler soll es erfahren. Drei Zustaende:
   kein Save / Save gefunden, keins lesbar (mit Grund) / gelesen, N
   uebersprungen.
3. **QA-036** — in ein temporaeres Verzeichnis bauen und am Ende umbenennen.
4. **SEC-019-Klasse** — Label-Fabrik plus Waechtertest, **nicht** 90
   Einzelaenderungen; mit SEC-015 und DR-004.
5. **SEC-006/016/018 als EIN Nachtrag** — relative Schranke aus der
   komprimierten Nutzlast statt gemessener Konstante.
6. Klein und dokumentiert: QA-037, QA-038, QA-044, QA-047, SEC-017, SEC-020,
   DR-005 bis DR-007, `scripts/capture_weapon_damage.py`.

Zurueckgestellt, nicht vergessen: **Nebenlaeufigkeit der Migration** (zwei
Programminstanzen auf einem Store — vom `qa-engineer` als naechster
Bruchpunkt von "lesen, schreiben, loeschen" benannt); `ruff` als
Entwicklungsabhaengigkeit (zieht `researcher` und `compliance-agent` nach).

## Entscheidungen des Nutzers
- **Die eigene Spielinstallation gilt als vertrauenswuerdig** (2026-09-02).
  SEC-015 bis SEC-018 auf Niedrig, SEC-019 von Hoch auf Mittel — sperrt das
  Release nicht mehr. Grenze A (heruntergeladenes Save) bleibt scharf.
  **Die README-Zusage "kein Netzwerkzugriff" muss trotzdem umformuliert
  werden**, bevor etwas veroeffentlicht wird: SEC-019 ist gemessen, nicht
  vermutet.

## Offen beim Nutzer
- **UI F1-F4** — blockiert den Berater-Bau: Slots festhalten? Statblatt-
  Vorschau vor dem Anwenden? Flueche mitbewerten? Name des Features?
  Empfehlungen: nein / nein / ja / offen.
- **`nightlords.png`** (C-002, ROT) und ob die Git-Historie umgeschrieben wird.
- **PR #16** mergen.
- **L-003** aus `docs/lessons.md`: "ein Branch pro Task" widerspricht dem
  Verbot von `branch`/`checkout` beim `developer` und beim `archivist`; keine
  dritte Rolle ist benannt. Empfehlung: Erwartung auf "ein Branch pro
  Auftragsgruppe, angelegt vom Director" aendern — aendert keine
  Agentendefinition und entspricht der gelebten Praxis.
- **QA-044**: die Aufloesung ist eine Produktentscheidung — Rueckfall auf den
  Rohnamen (widerspricht der Trennung Name/Schluessel) oder ein sichtbares
  "kann nicht uebernommen werden" im Panel.

## Was niemand geprueft hat, und das bleibt so
- **Die Oberflaeche hat kein Mensch mit Augen gesehen.** Alle Belege headless
  ueber die echten Widgets. Schliesst erst der `power-user` auf einem
  gebauten Artefakt.
- **Zahlenrichtigkeit gegen das laufende Spiel.** Nur der Nutzer kann das
  schliessen, und fuer den Berater waere es die wertvollste Pruefung.
- Linux und macOS: dort legt QSettings INI/plist an; `settings.sync()` in
  `_migrate_keys` ist von keiner Mutation zu toeten, weil nur Windows geprueft
  wird. **Wuerden sie je Zielplattform, ist das der Punkt, an dem eine
  Testluecke zur Datenverlustluecke wird.**
- Bekannte CVEs der sieben Abhaengigkeiten (SEC-011).
- Die vermutete 4-GiB-Allokation in `dvdbnd._read_entry` — Hypothese, nicht
  ausgeloest.
