# Lessons Learned

Erster Eintrag dieser Datei. Es gibt keine frühere `docs/lessons.md` — die
Wirkungskontrolle unten bezieht sich deshalb auf eine informell in
`docs/state.md` (Zyklus 2) notierte Massnahme, nicht auf einen vorherigen
Lessons-Zyklus.

## Zyklus 3–4 — 2026-09-02

**Ziel des Zyklus:** Zyklus 3 = erster vollständiger Sicherheitszyklus
(SEC-001 bis SEC-020, Aufträge T-017/T-018). Zyklus 4 = Beseitigung eines in
Zyklus 3 entdeckten P1-Datenverlusts in der Build-Migration (QA-033 ff.,
Aufträge T-019/T-020, zum Zeitpunkt dieser Retrospektive noch nicht
abschliessend vom `qa-engineer` nachgeprüft — T-020 lief laut `docs/state.md`
zuletzt unter "Nachprüfung läuft").

**Gut gelaufen (schützenswert):**
- Der `qa-engineer` hat erstmals eigene Laufzeitmutationen gefahren statt
  Entwicklerbehauptungen zu übernehmen (12 von 15 Sicherheitsbefunden
  dadurch belegt, nicht nur behauptet) und dieselbe Methode in Zyklus 4
  wiederholt eingesetzt.
- SEC-001 (Release-Blocker) wurde gegen ein echtes präpariertes Save
  nachgewiesen geschlossen (Vorher: 20 s Zwangsbeendigung; nachher: 0,01 s
  Fehlermeldung, Fenster in 1,8 s bedienbar) — Beleg statt Vermutung.
- Der `developer` hat in T-017 (SEC-012) eine falsche Fundstelle im eigenen
  Auftrag erkannt, die tatsächlich erreichbare Stelle zusätzlich repariert
  und beides offen im Bericht benannt, statt formal gegen den fehlerhaften
  Auftragstext zu liefern.
- Der `developer` hat in T-019 (QA-034) einer vom Director angebotenen
  Vereinfachung widersprochen, mit einem tragfähigen Argument (ein
  bestehender, korrekter Test würde dafür rot) — der Director hat es
  übernommen, ohne Gesichtsverlust auf beiden Seiten.
- Die in Zyklus 2 als Prozessfehler notierte Regel "je nicht-trivialem
  Auftrag eine Datei unter `docs/tasks/`" hat in Zyklus 3 und 4 durchgehend
  gehalten (T-017 bis T-020 liegen alle als Dateien vor) — siehe
  Wirkungskontrolle unten.
- Restrisiken wurden wiederholt ehrlich benannt statt wegoptimiert
  (SEC-006-Deckel als akzeptiertes Restrisiko dokumentiert, SEC-016 nach
  Gegenbeweis nicht hochgestuft, QA-035s "`setValue` bestätigt nichts" als
  bewusst akzeptierte Lücke begründet — und in T-020 an der einen Stelle
  zurückgenommen, an der die Begründung nicht mehr trug).

### Wirkungskontrolle früherer Massnahmen

| ID | Massnahme | Übernommen am | Wirkung | Konsequenz |
|---|---|---|---|---|
| (informell, kein L-ID) | "Je nicht-trivialem Auftrag eine Datei unter `docs/tasks/`" (Zyklus 2, `docs/state.md`, Abschnitt "Prozessfehler dieses Zyklus"; T-008 bis T-012 und T-016 liefen ohne Auftragsdatei) | 2026-09-02, nie formal in einer `lessons.md` verankert | **Wirkt.** T-017, T-018, T-019, T-020 liegen alle als Dateien unter `docs/tasks/` vor — kein Rückfall in zwei Folgezyklen. | Hiermit erstmals formal dokumentiert (siehe L-004), sonst keine Änderung nötig. |

### L-001 — Ein Sicherheits-/Datenverlust-Fix schliesst die benannte Fundstelle, nicht die Fehlerklasse

**Belege:**
- SEC-012: Der Auftrag (T-018) benannte `PART_NAMES.get((boss["name"], label), label)` als Fundstelle. `PART_NAMES` ist ein leeres, aus Spieldaten nicht erreichbares Dict; die tatsächlich erreichbare Injektion sass in `bosstab.py::_stance_rank`. Der `developer` hat es selbst bemerkt, beide Stellen geschlossen und es im Bericht benannt (`security/findings.md`, "SEC-012 Befundtext korrigiert", 2026-09-02).
- SEC-004: An drei benannten Stellen (T-017) geschlossen und als "behoben" geführt. `ui-ux-designer` (`DESIGN_REVIEW.md`, DR-004) und danach der `security-reviewer` fanden 90 von 95 `QLabel` und 35 von 36 Tooltips derselben Klasse unverändert offen (SEC-019: "SEC-004 als Klasse offen").
- QA-033: Die Ursache "ein Altpfad wird entfernt, ohne dass das Schreiben belegt ist" wurde für den Schrägstrich-Fall behoben (T-019). Dieselbe Ursache traf im selben Modul (`_migrate_keys`) über die Registry-Längengrenze erneut zu (QA-041, T-020: "Dieselbe Wurzel wie QA-033 — entfernen, ohne dass das Schreiben belegt ist. Nur ausgeloest durch Laenge statt durch Schraegstrich").

**Ursache:** Der Auftrag benennt den Befund über konkrete Fundstellen ("die drei genannten Stellen", eine bestimmte Codezeile), nicht über die Eigenschaft, die den Fehler erzeugt. Ein Fix gilt damit als vollständig, sobald die genannten Zeilen geändert sind — unabhängig davon, ob dieselbe Eigenschaft anderswo im selben oder einem verwandten Modul weiterbesteht. Die Ausweitung auf Geschwisterstellen ist bislang Einzelinitiative des jeweiligen Agenten, nicht Auftragsbestandteil.

**Massnahme:** In jeder Auftragsdatei unter `docs/tasks/`, die einen Sicherheits- oder Datenintegritätsbefund einer konkreten Fundstelle zuordnet, ergänzt der Director im Abschnitt "Vorgaben" sinngemäss:
> "Nach dem Fix: eine Suche über den gesamten Baum nach demselben Muster fahren (nicht nur die oben genannten Zeilen) und im Bericht angeben, wie viele weitere Fundstellen es gibt, welche mitbehoben und welche bewusst zurückgestellt wurden."

Das ist keine neue Fähigkeit — T-017 tat genau das bereits einmal ("Ausweitung auf `bnd4.read_split_header` bestätigt"), aber als Ausnahme, nicht als Standardsatz. Diese Massnahme betrifft nur den Text, den der Director selbst in `docs/tasks/*.md` schreibt — keine Agentendefinition und kein `CLAUDE.md`.

**Erfolgskriterium:** In den nächsten zwei Zyklen mit Sicherheits- oder Datenintegritätsbefunden taucht kein Nachfolgebefund mehr auf, der einen bereits als "behoben" geführten Befund ausdrücklich als "dieselbe Wurzel/Klasse" wiedereröffnet.

**Status:** vorgeschlagen

### L-002 — Ein Regressionstest, der Reihenfolge/Protokoll prüft, beweist nicht, dass der Schadensfall abgefangen wird

**Belege:**
- QA-037: Die SEC-002-Wächter in `bnd4`, `dvdbnd`, `tae` sind gefixt, aber von keinem der 145 Tests bewacht — Mutation (Wächter entfernt) liefert 145 passed.
- QA-042: Der QA-033-Ordnungstest (`test_the_migration_removes_nothing_until_it_has_read_and_written`) prüft nur *wann* entfernt wird, nicht *was* entfernt werden darf. Mutation (`and path not in written` gestrichen) ergibt 26 passed, während bei einem Altbestand `Fire ice` + `Fire%20ice` echte Builds verloren gehen.
- Der Director zieht daraus im Quelltext selbst bereits die allgemeine Lehre (`qa/findings.md`, Entscheidungen Zyklus 4 nach dem Retest): "ein Test, der eine Eigenschaft misst, ersetzt nicht den Fall, der den Schaden zeigt" — und macht die Mutationsprobe für T-020 zur Abnahmebedingung statt zur Kür. Ergebnis danach, belegt: die Mutationsprobe zu `path not in written` tötet jetzt zwei Tests statt null; fünf von sechs Mutationen insgesamt fallen.

**Ursache:** Die Regressionstest-Pflichtabschnitte der Aufträge verlangten bislang nur, dass ein Fall existiert und grün ist — nicht, dass eine gezielte Deaktivierung der Schutzmassnahme den Test rot macht. Ein Test kann eine wahre, aber falsche Eigenschaft prüfen (Reihenfolge statt Inhalt) und trotzdem als hinreichender Beleg durchgehen, bis jemand ihn mutiert.

**Massnahme:** In der Vorlage für "Regressionstests (Pflicht)" in Auftragsdateien zu Sicherheits- und Datenintegritätsbefunden ergänzt der Director standardmässig (wie einmalig bereits in T-020 formuliert, jetzt als Standardsatz statt Einzelfall):
> "Mutationsprobe ist Teil der Abnahme: jede Schutzmassnahme des Fixes einzeln deaktivieren und zeigen, dass mindestens ein Test dadurch fehlschlägt. Schlägt keiner fehl, ist der Test nicht die Regressionssicherung, die dieser Auftrag verlangt."

**Kosten:** Ein zusätzlicher, expliziter Prüfschritt je Sicherheits-/Datenintegritätsfix — nicht bei jedem beliebigen Bugfix. Für den `developer` typischerweise wenige Minuten (Zeile deaktivieren, Suite laufen lassen); die Mutation ist ohnehin eine sinnvolle Selbstprüfung vor der Abgabe. Der Nutzen (kein stiller Datenverlust durch eine später als "redundant" gelesene und gestrichene Zeile) überwiegt klar. Diese Massnahme betrifft nur den Auftragstext des Directors, keine Agentendefinition.

**Erfolgskriterium:** In den nächsten zwei Zyklen mit Sicherheits-/Datenintegritätsfixes liefert kein vom `qa-engineer` eigenständig gefahrener Mutationstest 0 fehlschlagende Fälle bei einer sicherheitsrelevanten Schutzmassnahme, die der `developer` selbst schon hätte prüfen können.

**Status:** vorgeschlagen

### L-003 — "Ein Branch pro Task" widerspricht dem Verbot von `branch`/`checkout` beim `developer`

**Belege:** `developer.md` (Zeile 202-205) verbietet dem `developer` ausdrücklich `branch` und `checkout`, "damit er bei ungespeicherten Änderungen nichts verlieren kann". `archivist.md` (Zeile 62-65) verbietet dem `archivist` ebenso das Anlegen von Branches — er "operiert ausschliesslich auf dem Branch, der beim Aufruf ausgecheckt ist". In T-017 bis T-020 (vier Aufträge in Folge) landeten sämtliche Commits auf demselben Arbeitsbranch `docs/audit-and-advisor-design`. Der Director benennt das am Ende von Zyklus 4 ausdrücklich als bestehenden, nicht vom `developer` verursachten Konflikt (`qa/findings.md`, letzter Absatz): "Ihm sind `branch` und `checkout` ausdrücklich verboten ... Er committet auf den Arbeitsbranch, ich verantworte den PR-Weg. Kein Rückbau, keine Ermahnung — die Regel gehört korrigiert, nicht der Agent."

**Ursache:** Die Erwartung "ein Branch pro Task" setzt voraus, dass irgendeine Rolle vor jedem Auftrag einen neuen Branch anlegt. Weder `developer` noch `archivist` dürfen das laut ihrer eigenen Definition, und keine dritte Rolle ist dafür schriftlich benannt — die Regel und die Rechtevergabe widersprechen sich strukturell, unabhängig davon, wer den Auftrag ausführt.

**Massnahme (dem Nutzer vorzulegen — sie berührt eine teamweite Workflow-Erwartung, nicht nur dieses Repo):** Zwei Optionen, eine Entscheidung:
1. Die Erwartung wird explizit auf "ein Branch pro Auftragsgruppe/Zyklus, angelegt vom `director` selbst vor dem ersten Dispatch dieser Gruppe" geändert. Der `developer` committet weiterhin ausschliesslich auf den beim Aufruf ausgecheckten Branch, genau wie `developer.md` es schon vorschreibt — es ändert sich nur, wie oft ein neuer Branch entsteht, nicht wer ihn anlegt. In diesem Projekt ist das ohnehin schon gelebte Praxis (ein Branch pro Audit-Initiative über mehrere Tasks, ein PR) — der Vorschlag macht nur explizit, was faktisch bereits passiert, und beendet das wiederkehrende Melden eines unlösbaren Auftrags.
2. Falls "ein Branch pro Task" tatsächlich gewünscht ist, muss eine Rolle das Anlegen vor jedem Dispatch ausdrücklich übernehmen — das wäre eine neue Berechtigung für `director` oder `archivist` und damit eine Änderung von `archivist.md`, die der Nutzer freigeben müsste.

Empfehlung dieser Retrospektive: Option 1, weil sie keine Agentendefinition ändert und der gelebten Praxis entspricht.

**Entscheidung des Nutzers, 2026-09-02: Option 1.** Die Erwartung lautet ab sofort *"ein Branch pro Auftragsgruppe, angelegt vom `director` vor dem ersten Dispatch dieser Gruppe"*. `developer` und `archivist` committen weiterhin ausschliesslich auf den beim Aufruf ausgecheckten Branch — ihre Definitionen bleiben unveraendert. Offen bleibt, **wo der urspruengliche Satz "ein Branch pro Task" steht**: weder diese Retrospektive noch der `director` konnten ihn in einer Agentendefinition finden. Bis er auftaucht, gilt die neue Fassung als die geltende; wer ihn findet, zieht ihn nach.

**Erfolgskriterium:** Kein Abschlussbericht eines `developer` benennt "ein Branch pro Task" künftig noch als für ihn unerfüllbare Vorgabe.

**Status:** **uebernommen (Nutzer, 2026-09-02)** — Option 1

### L-004 — Auftragsdatei-Pflicht (Zyklus-2-Prozessfehler) wirkt weiter, hiermit formal verankert

**Belege:** Siehe Wirkungskontrolle oben. `docs/tasks/T-017.md` bis `T-020.md` existieren, im Gegensatz zu den in Zyklus 2 ohne Auftragsdatei vergebenen T-008 bis T-012 und T-016.

**Ursache:** Entfällt — keine offene Ursache, die Massnahme wirkt bereits.

**Massnahme:** Keine neue Textänderung nötig. Diese Lessons-Datei verankert die Regel erstmals formal, damit sie nicht von einer zukünftigen Retrospektive erneut "neu entdeckt" werden muss: *Jeder nicht-triviale Auftrag bekommt eine Datei unter `docs/tasks/`, bevor er dispatcht wird.*

**Erfolgskriterium:** Bleibt in den nächsten zwei Zyklen ohne Ausnahme bestehen.

**Status:** übernommen (2026-09-02, rückwirkend dokumentiert — wirkt nachweislich seit Zyklus 3)

### Beobachtungen (noch kein Muster)

- **DEBT-001, Testsockel-Behauptung ungeprüft (einmalig, 2026-09-02):** `tests/conftest.py` nahm den Snapshot-Cache, wenn er existierte — dadurch liefen `fmg`, `bnd4`, `dvdbnd`, `tpf`, `tae` in jedem grünen Lauf seit Zyklus 2 gar nicht. Die Aussage "Testsockel steht" (Zyklus-2-Abschluss, `docs/state.md`) war dadurch ungeprüft, nicht falsch — aber sie klang wie ein Beleg. Bislang ein Einzelfall. Kandidat für eine künftige Massnahme, sobald ein zweites Mal eine Abdeckungsaussage ("N Tests", "Sockel steht") auftaucht, ohne zu nennen, welche Codepfade der grüne Lauf tatsächlich durchlief: dann eine Regel, dass jede Abdeckungsaussage im Abschlussbericht/`docs/state.md` benennt, welcher Testlauf welchen Pfad wirklich ausführt — nicht nur, wie viele Tests grün sind.
- **Director-Ersteinschätzung ohne Fachbeleg, einmalig (SEC-016, 2026-09-02):** Der Director wollte SEC-016 aufgrund einer eigenen Vermutung zur Erreichbarkeit hochstufen; der `security-reviewer` widerlegte das mit zwei Fakten (von einem Savefile aus nicht erreichbar, läuft nur beim Erststart). Bewusst **kein** Muster mit den beiden anderen vom Director selbst genannten Fällen (QA-034-Vereinfachung, T-019-Restlücke) zusammengelegt — die sind andersartig (Design-Abwägung bzw. Risikorechnung, keine technische Tatsachenbehauptung). Bewertung dieser Retrospektive: Das ist die Fachrolle, die genau die Aufgabe erfüllt, für die sie da ist. Die Korrektur geschah, bevor Schaden entstand, und kostete nur eine Textzeile — gesundes Delegieren, kein Zeichen verfrühter Entscheidungen. Kein Handlungsbedarf, solange es dabei bleibt.

---

## Zyklus 12–13 — 2026-09-05

**Ziel der beiden Zyklen:** Zyklus 12 = der Rechenkern des Build-Beraters
(T-037), seine QA (T-041), die beiden Kalibrierungen Faktor 0,6 (T-045) und
Katalysator-Kennzahl (T-046), der Entwurfsnachtrag AD-025 (T-047), seine
Umsetzung (T-048), der Retest (T-051) und das Design-Review am laufenden
Fenster (T-052). Zyklus 13 = der vom Nutzer am 05.09. beauftragte Inhaltsaudit
der sechs Referenz-Tabs, `GOAL.md` A10 bis A14 (T-053 bis T-061).

**Datengrundlage dieser Retrospektive:** 17 Berichte unter `docs/berichte/`
(T-037, T-041, T-045 bis T-048, T-051 bis T-061), `qa/findings.md`
(QA-100 bis QA-149, 50 Befunde), `docs/state.md`, `GOAL.md`,
`docs/plan-restarbeiten.md`, `docs/tasks/` (52 Dateien), diese Datei, sowie
die Regelblöcke in `~/.claude/agents/{architect,developer,qa-engineer}.md`.

### Gut gelaufen (schützenswert)

- **Die Mutationskampagne ist eine Institution geworden, keine Kür.** Über
  beide Zyklen sind rund 80 Gegenbauten registriert und einzeln gefahren
  worden; die Registry in `scripts/differential/mutate.py` wuchs von 55 auf
  71 (T-058) und um weitere 14 in T-060. Jeder `developer`-Bericht trägt die
  Tabelle mit Zahlen.
- **Fremde Zahlen werden unabhängig nachgefahren, nicht übernommen.** T-041
  fuhr 15 von 15 Mutationen des `developer` in 27 eigenen Extraktionen nach:
  **0 Abweichungen**. T-059 fuhr 6 von 21 Mutationen aus T-057/T-058 nach:
  **6 von 6 exakt**, einschliesslich der Namen der fallenden Fälle. T-051
  rechnete die Golden-Datei direkt aus den Git-Blobs neu, statt `ratios.py`
  zu benutzen — Gegenprobe statt Wiederholung.
- **Rollen melden ihre eigenen Fehler unaufgefordert.** T-053: „ich habe
  DR-009 committet, bevor die volle Suite lief, und dabei zwei Golden-Fälle
  gebrochen". T-048: „Ich hatte es behauptet, ohne es gemessen zu haben; die
  Messung war zwanzig Minuten Arbeit." T-057: zwei Commits, die Formatierung
  und Logik mischen. T-060: „der Teil des Berichts, den ich am wenigsten gern
  schreibe und der am meisten sagt." T-060 hat ausserdem einen Satz
  zurückgenommen, den er selbst im selben Auftrag geschrieben hatte.
- **Falsche eigene Befunde werden verworfen statt gemeldet.** T-052 hat einen
  Phantombefund („das dritte Panel verschwindet") als eigenen Methodenfehler
  erkannt (fehlendes `SetProcessDPIAware()`) und benannt statt eingetragen.
  T-059 nennt drei verworfene Befunde unter der Überschrift „Was nicht
  gehalten hat — an mir, nicht am Programm".
- **Niemand erfindet eine Zahl, wenn die Dateien sie nicht hergeben.** T-057
  hat die beiden handgetippten Debuff-Zahlen ersatzlos entfernt und die
  Sichtung als Sichtung stehen lassen. T-048 hat die Einbauhöhe von QA-113
  benannt statt geraten. T-046 kennzeichnet die 28 RPS-Zahlen ausdrücklich als
  „Abschrift einer Abschrift" und als den einen Punkt der Beweiskette ohne
  Primärquelle. T-053 hat einen Platzhalter stehen lassen und ihn ehrlicher
  beschriftet, statt einen Wortlaut zu erfinden.
- **Der `qa-engineer` misst am laufenden Programm, nicht an der Fassade.**
  T-051 hat Wylder Lv12 / Dagger = 74 an einer echten headless
  `Planner`-Instanz auf Kachel, Tafel **und** Arsenal-Tab abgelesen und dafür
  eine Sektion programmatisch aufklappen müssen. T-059 hat 26 949 gekürzte
  Zellen über elf Konfigurationen gezählt.
- **Rollen korrigieren ihre eigenen früheren Vorgaben.** T-056 §3 nimmt das
  Lob zurück, das derselbe `ui-ux-designer` in T-052 der Arsenal-Kachel
  ausgestellt hatte — „für den damals geprüften Fall richtig und als
  allgemeine Regel falsch".
- **Auftragsgrenzen halten unter Druck.** T-060 hat gegen eine ausdrückliche
  Anweisung („zieh die vier Stellen nach") **eine** Stelle nachgezogen, für
  die anderen drei gemessen, dass die Begründung der Anweisung nicht trägt,
  und beides offen berichtet.

### Wirkungskontrolle früherer Massnahmen

**Vorbemerkung, die für die ganze Tabelle gilt: es gibt zwei Regelsätze mit
demselben Nummernraum.** `docs/lessons.md` führt L-001 bis L-004 (Projekt);
die Agentendefinitionen `architect.md`, `developer.md` und `qa-engineer.md`
führen unter „Projektübergreifende Regeln" ebenfalls L-001 bis L-004 sowie
L-006 und L-007 — mit **anderen Inhalten**. Zwei davon sind ausdrücklich aus
diesem Projekt hervorgegangen: teamweites L-006 nennt als Herkunft
„Nightreign-Helper L-001", teamweites L-007 nennt „Nightreign-Helper L-002".
Geprüft an allen L-Zitaten der Zyklen 12 und 13 (T-037, T-041, T-045, T-046,
T-048, T-053, T-055, T-057, T-058, T-059, T-060 sowie `qa/findings.md`
QA-115/QA-118): **jedes einzelne meint den teamweiten Satz, keines den
Projektsatz.** Die Nummern dieser Datei werden seit `docs/tasks/T-023.md`
nicht mehr zitiert. Konsequenz unten.

| ID | Massnahme | Übernommen am | Wirkung | Konsequenz |
|---|---|---|---|---|
| **L-001** (Projekt) — Fix schliesst die Fehlerklasse, nicht die Fundstelle | nie formal übernommen (Status blieb „vorgeschlagen"), aber **teamweit als L-006 in Kraft** | 2026-09-03 (als L-006) | **Wirkt, am stärksten von allen.** Sieben Berichte in Folge tragen den Suchbeleg mit Trefferzahl: T-045 §7 (vier Masken, fand den überholten Vorbehalt an **sechs** Stellen in zwei Dateien, darunter `ARCHITECTURE.md`, das kein Auftrag genannt hatte), T-046 §9 (drei Masken), T-053 §1.3 (zwei Masken, fand die vier ungefilterten Leser), T-055, T-057 §6, T-058 §9 (fand **vier weitere** feste Spaltenzahlen und meldete sie, statt sie zu verschweigen), T-060 §5 (zwei Masken, 53+25 Treffer, sechs einzeln verfolgt). | Keine. Das Erfolgskriterium aus Zyklus 3–4 („kein Nachfolgebefund eröffnet einen geschlossenen als dieselbe Klasse") ist **formal verfehlt** — QA-141 ist DR-016a im Picker, QA-144 der Rest von QA-132, QA-148/149 der Rest von QA-128. Inhaltlich ist es erfüllt: **in jedem dieser Fälle hat die von der Regel verlangte Suche den Rest selbst gefunden und im selben Bericht benannt.** Die Wiedereröffnungen entstehen an **Auftragsgrenzen des Directors** („Build planner ausgenommen"), nicht an der Regel. Kriterium wird hiermit auf diese Lesart präzisiert. |
| **L-002** (Projekt) — Mutationsprobe ist Abnahmebedingung | nie formal übernommen, aber **teamweit als L-007** in Kraft und als Arbeitsregel in `docs/plan-restarbeiten.md` | 2026-09-03 | **Wirkt formal zu 100 %, inhaltlich nicht ausreichend.** Sie hat in beiden Zyklen viermal etwas gefunden, das eine grüne Suite nie gezeigt hätte (T-046 selbstbezüglicher Stub, T-048 Teilzeichenkette, T-053 selbstbezügliche Schwellen, T-060 zwei zahnlose Wächter). **Und trotzdem sind in denselben zwei Zyklen 13 Wächter dokumentiert, die nichts bewachten.** | **Präzisierung nötig — siehe L-008.** Die Regel verlangt, dass eine Mutation existiert und tötet; sie sagt nichts darüber, woher der Fall seine Erwartung nimmt, unter welcher Auswahl die Mutation rot werden muss, und was ein Überleben bedeutet. |
| **L-003** (Projekt) — „ein Branch pro Auftragsgruppe, angelegt vom `director`" | **übernommen (Nutzer, 2026-09-02), Option 1** | 2026-09-02 | **Wirkt.** T-037, T-045, T-046, T-048, T-053, T-057, T-058, T-060 committen alle auf `docs/audit-and-advisor-design`; **kein** Bericht nennt „ein Branch pro Task" noch als unerfüllbare Vorgabe. Erfolgskriterium erfüllt. | Die 2026-09-02 offen gelassene Frage „wo steht der ursprüngliche Satz?" ist hiermit beantwortet: **er steht in keiner Datei.** Die Agentendefinitionen verbieten `branch`/`checkout`, sie verlangen nirgends einen Branch je Task. Der Satz war eine Erwartung ohne Fundstelle. Punkt geschlossen. |
| **L-004** (Projekt) — je nicht-trivialem Auftrag eine Datei unter `docs/tasks/` | **übernommen (2026-09-02)** | 2026-09-02 | **Gebrochen, und zwar am Ende von Zyklus 13.** `ls docs/tasks/` zeigt T-030 bis T-059 lückenlos — und **keine Datei für T-060 und T-061**. T-060 sagt es im Kopfblock selbst („keine Datei unter docs/tasks/ — dort liegt nichts zu T-060, geprüft mit `ls docs/tasks/`"). Dazu zwei Nachträge zu T-052, per Nachricht beauftragt, die AK-63 korrigiert und AK-67 sowie AK-105 hervorgebracht haben — nicht trivial. **23 von 26 Aufträgen eingehalten.** | Keine neue Regel. Bemerkenswert ist **wo** sie brach: bei T-060, dem grössten Einzelauftrag des Zyklus (10 Befunde, 17 Commits, 14 Mutationen), und bei T-061, dessen Lauf danach abbrach. Die Ausnahme traf die zwei Aufträge, die eine Auftragsdatei am nötigsten gehabt hätten. Erfolgskriterium **nicht** erfüllt; Regel bleibt, Ursache ist Zyklusende-Druck, nicht die Regel. |
| **L-001 (teamweit)** — Zahlen tragen ihr Rezept | Nutzer, 2026-09-02 | 2026-09-02 | **Wirkt, mit einem belegten Ausfall, den die Regel selbst gefunden hat.** Wirkt: `scripts/measure_advisor_picker.py` (T-037), `scripts/differential/ratios.py` (T-045: „ohne ein Skript wäre die zentrale Zahl dieses Berichts eine Behauptung"), die Herleitung von `CATALYST_DISPLAY_RATE = 90.0` als Intervallschnitt über 84 Zellen (T-046), `scripts/measure_display_thresholds.py` (T-053), `scripts/bracketing_residue.py` (T-048). Ausfall: **QA-115** — der Kommentar in `weapons.py` begründete die Klammerung mit „574 von 350 160", belegt durch `dump_rate.py`, das **nie existierte** (drei unabhängige Suchen, je 0 Treffer). | Keine. Der Ausfall stammt aus dem am Wochenlimit abgebrochenen ersten T-045-Lauf, wurde von der Regel gefunden, und T-048 hat die Messung nachgebaut: **544 statt 574** — und die eigentliche Aussage dabei **schärfer** als behauptet (0 von 350 160 statt „höchstens 1 ULP"). Genau so soll die Regel wirken. |
| **L-003 (teamweit)** — mechanismus-gebundenes Signal | Nutzer, 2026-09-02 | 2026-09-02 | **Wirkt, viermal ausdrücklich zitiert und jedesmal ausschlaggebend.** T-041 §7 hat einem leeren `git diff` nicht getraut und zusätzlich 18 Konfigurationen über beide Bäume gefahren (297 Zeilen, 0 Unterschiede). T-045 §5 belegt mit dem Assertion-Text („the game shows 88, this program shows 148") statt mit einem Exitcode. T-055 hat eine **Kontrollmutation** mitlaufen lassen, damit „622 grün" nicht „Harness kaputt" heissen kann. T-057 schreibt den Platzhalter-Marker als Literal in die Mutation, weil ein `NameError` „rot aus dem falschen Grund" wäre. | Keine. |
| **L-004 (teamweit)** — Bau-Konfiguration gehört zum Nachweisweg | Nutzer, 2026-09-02 | 2026-09-02 | **Nicht anwendbar in diesen Zyklen, deshalb ungeprüft.** Das Projekt hat ausser `pytest.ini` keine Bau-Konfiguration und **keinen Linter** (Frage F-A, seit vier Zyklen offen — jeder `developer`-Bericht trägt deshalb einen unquittierbaren DoD-Punkt). Ein **gebautes Artefakt (GOAL A9) ist bis heute von niemandem geprüft worden.** | Keine Massnahme. Aber: solange A9 offen ist, hat teamweites L-004 in diesem Projekt keine Fläche, und „Linter sauber" bleibt in jeder DoD unbelegbar. Das ist eine Nutzerentscheidung (F-A), keine Teamregel. |
| **L-006 (teamweit)** — Eigenschaft statt Fundstelle | Nutzer, 2026-09-03 | 2026-09-03 | siehe L-001 (Projekt) oben — **wirkt**. | siehe dort. |
| **L-007 (teamweit)** — Rot-vorher nennt die brechende Änderung | Nutzer, 2026-09-02/03 | 2026-09-03 | **Wirkt formal, deckt eine Lücke nicht.** Wirkt: T-053 §8 listet je Wächter die Änderung, die ihn heute bräche; T-048 belegt den Rot-vorher-Zustand mit SHA-256 vor und nach dem Rückbau; QA-118 ist überhaupt nur ein Befund, weil jemand die alte Testfassung gegen das neue Programm gefahren hat. Deckt nicht: die 13 Fälle unter L-008. | siehe L-008. |
| **L-005** | — | — | **Existiert in keinem der beiden Sätze.** Weder `docs/lessons.md` noch eine Agentendefinition vergibt L-005; kein Bericht zitiert sie. | Loch in einer Nummerierung, die laut Vorgabe durchläuft. Keine Massnahme, aber siehe die Konsequenz unten. |

**Konsequenz aus der Wirkungskontrolle (Entscheidung des Nutzers nötig, keine
eigene Massnahme):** Zwei Regelsätze teilen sich einen Nummernraum, in dem
L-005 fehlt und in dem diese Retrospektive gerade L-008 bis L-011 vergibt —
also genau die Nummern, die der teamweite Satz als nächste vergeben würde.
Bisher hat die Kollision **nachweislich niemanden fehlgeleitet** (jedes Zitat
der Zyklen 12/13 meint korrekt den teamweiten Satz). Der heutige Schaden ist
ein anderer: **die einzige Regel, die nur das Projekt führt und die der
teamweite Satz nicht kennt, ist L-004 (Auftragsdatei-Pflicht) — und genau die
ist gebrochen.** Sie steht in einer Datei, die seit T-023 niemand mehr
zitiert. Vorschlag, dem Nutzer vorzulegen: (a) die zwei projekteigenen Regeln
(Auftragsdatei-Pflicht, Branch je Auftragsgruppe) in den Abschnitt „Regeln,
die für jeden Schritt gelten" in `docs/plan-restarbeiten.md` übernehmen — die
Datei, die `docs/state.md` bereits als einzigen Pflegeort der Arbeitsregeln
benennt und die jede Rolle liest; (b) künftige Projekt-Nummern mit `NH-`
präfixen, damit sie nie mit dem teamweiten Satz kollidieren können; (c)
`docs/lessons.md` bleibt Verlauf, wird aber nicht mehr als Regelwerk zitiert.
Kosten: eine Textverschiebung. Nutzen: die gebrochene Regel steht dort, wo sie
gelesen wird.

---

### L-008 — Wächter, die nichts bewachen: die Mutationsregel wird eingehalten und genügt nicht

**Belege — 13 Fälle in zwei Zyklen, jeder mit Quelle und Fundweg:**

| # | Wächter / Zusicherung | Quelle | Warum er nichts belegte | Wer es fand |
|---|---|---|---|---|
| 1 | Prüfpunkt 13, `test_the_advisor_computes_the_build_the_window_shows` | T-041 §3, QA-100 | läuft im **Vorgabezustand** (Level 1, eine Waffe = die Referenz, `declared={}`, Deep aus, Wylder ist `heroes[0]`); vier der sieben `compute`-Argumente lassen sich durch Konstanten ersetzen, **398 passed** bleibt stehen | 9 eigene Gegenbauten des `qa-engineer` |
| 2 | `test_where_a_relic_is_held_does_not_change_the_fingerprint` | T-041 §10, QA-107 | prüft eine Eigenschaft des **abgeleiteten** Fingerabdrucks, die der tatsächlich benannte Schlüssel (`AdvisorRequest`) nicht hat | Hash-/Gleichheitsprobe, **keine** Mutation |
| 3 | erster Farb-Gegenbau zu `ratios.py` | T-045 §8 | `#6fbf73`/`#8a8a8a` liess die Suite grün, weil die Palette Buchstaben enthält und der Lookahead die Ziffern hält — der Wächter war unbelegt | Mutationslauf |
| 4 | `test_move_scoped_effects.py` (QA-118) | T-045 §9, T-051 §3 | die **alte** Fassung ist gegen das **neue** Programm grün, in beiden Anläufen (T-045 und T-046) | alte Fassung gegen neuen Code gefahren |
| 5 | Stub in `test_catalyst_scaling_extraction.py` | T-046 §4 | baute seine Zeilen aus `extract.CATALYST_SCALING_FIELD` — also aus genau der Konstante, nach der der Extraktor sucht; unter der Umbenennungs-Mutation blieb der positive Fall grün | Mutationslauf |
| 6 | `arsenal_reading()` für sechs Waffen (QA-123) | T-051 §4 | sucht nach dem eigenen Waffennamen; bei Dagger/Greatsword/Hammer/Greataxe/Spear/Halberd matchen über 60 Familienmitglieder, die Sektion bleibt zu, `arsenal_tiles` ist leer — **ein Vergleich zweier leerer Listen ist immer „unverändert"** (24 von 7172 Datensätzen) | vollständige Auszählung über 1793 Waffen |
| 7 | der QA-124-Fall | T-048 §5 | `"at level 1"` ist **Teilzeichenkette** von `"at level 15"` — der Fall lief gegen seinen eigenen Gegenbau grün | Mutationslauf |
| 8 | `tests/test_display_thresholds.py`, erste Fassung | T-053 §5.3 | rechnete seine beiden Bänder aus `app.VISIBLE_CHANGE` — der Konstante, um die es geht; **beide** Mutationen verschoben die Bänder mit und überlebten (620 von 622 grün) | Mutationslauf |
| 9 | die Suite über fünf der sechs Tabs (QA-137) | T-055 | **kein** Test berührt `effectstab`, `deeptab`, `depthstab`, `eventstab`, `eventlore`; sieben Anzeigemutationen gleichzeitig → **622 passed, unverändert** | 7 Mutationen + 1 Kontrollmutation |
| 10 | `test_every_type_row_and_the_upgrade_line_match_the_facade` (QA-142) | T-059 §5 | vergleicht byteweise gegen die Fassade — **beide Seiten entstehen im selben Prozess** und bekommen dieselbe `PYTHONHASHSEED`-Ordnung; der Fall kann die Unordnung nie sehen | vier Prozesse mit vier Hashseeds |
| 11 | `picker-opening-width-guessed-again` | T-060 §9a | die Mutation **überlebte** (1 failed = nur der Anker, 756 passed): was QA-141 geschlossen hat, ist `CardGrid` — nicht die Herleitung der Öffnungsbreite, die der Wächter zu bewachen behauptete | Mutationskampagne |
| 12 | `nightlord-panel-back-to-a-fixed-width` | T-060 §9b | die Mutation **überlebte**: der Wächter war auf fünf Breiten parametrisiert und biss nur bei 833 px — **der Breite, die der Standardlauf seit der QA-146-Änderung überspringt** | Mutationskampagne |
| 13 | Registry-Eintrag von `effect-headings-measured-while-elided` | T-060 §9c | nannte den falschen tötenden Fall; der wirkliche fällt nur in einer bestimmten Reihenfolge (schmal → `refresh` → breit) | Mutationskampagne |

**Zur Nachzählung, die der Auftrag verlangt: es sind 13, nicht 5 — das Muster
trägt deutlich.** Zwei Präzisierungen an der Ausgangsbeobachtung:

- **„Jedes Mal hat es nur der Mutationslauf gefunden" stimmt für 8 von 13.**
  Fall 2 fand eine Hash-/Gleichheitsprobe, Fall 4 der Lauf einer alten
  Testfassung gegen neuen Code, Fall 6 eine vollständige Auszählung über den
  Datensatz, Fall 10 der Vergleich zweier Prozesse mit verschiedenen Seeds.
  Das ist wichtig, weil eine Massnahme „mehr Mutationen" diese vier nicht
  gefunden hätte.
- Die vier im Auftrag genannten Mechanismen sind alle belegt, aber ein
  fünfter fehlte: **eine registrierte Mutation, die überlebt** (Fälle 11, 12)
  oder deren Eintrag den falschen tötenden Fall nennt (Fall 13).

**Ursache (ein Satz):** Die geltende Regel verlangt, dass je Wächter eine
Mutation existiert und tötet — sie sagt nichts darüber, **woher der Fall seine
Erwartung nehmen darf**, **unter welcher Auswahl die Mutation rot werden
muss** und **was ein Überleben bedeutet**, und deshalb kann sie formal zu
100 % eingehalten sein, während der Wächter nichts bewacht.

**Massnahme.** Zieldatei: `docs/plan-restarbeiten.md`, Abschnitt „Regeln, die
fuer jeden Schritt gelten" (der von `docs/state.md` benannte einzige
Pflegeort der Arbeitsregeln). Der bestehende erste Spiegelstrich
„Jeder neue Waechter braucht seine **toetende Mutation**." wird **ersetzt**
durch:

> - Jeder neue Waechter braucht seine **toetende Mutation**. Sie zaehlt erst
>   als toetend, wenn (1) sie **im Standardlauf** rot wird — nicht nur unter
>   einer Breite, Plattform oder Auswahl, die der Standardlauf ueberspringt;
>   (2) der rot gewordene Fall seine Erwartung **nicht** aus der Stelle
>   bezieht, die er bewacht — nicht aus derselben Konstante, nicht aus
>   demselben Prozess, und nicht als Teilzeichenkette einer Zeichenkette,
>   deren Wortschatz er nicht selbst setzt. **Ueberlebt eine registrierte
>   Mutation, ist das ein Befund ueber den Waechter**: er gehoert mit seiner
>   Ursache in den Bericht, nicht stillschweigend ersetzt.

Der Director übernimmt denselben Wortlaut in den Abschnitt „Regressionstests
(Pflicht)" seiner Auftragsdateien, wo er ihn heute schon von Fall zu Fall
formuliert (T-057 nennt ihn „die Falle, die du benannt hast" — und T-053, davor
geschrieben, fiel genau in sie).

**Kosten.** Kein zusätzlicher Lauf: die Punkte 1 und 2 sind eine Lesart beim
Schreiben des Falls, Punkt 3 macht aus einem stillen Ersetzen einen
Berichtsabsatz. T-060 hat für 14 Mutationen 75 Minuten reine Laufzeit
gebraucht und **zwei** Durchläufe, weil zwei Wächter beim ersten Mal nichts
fingen — und nennt es „das war es wert". Die Regel macht diesen zweiten
Durchlauf zur Pflicht statt zur Tugend. Sie verlangt **nicht** mehr
Mutationen; sie verlangt, dass die vorhandenen zählen.

**Erfolgskriterium.** In den nächsten zwei Zyklen: (a) kein Bericht meldet
einen Wächter, dessen Erwartung aus der bewachten Stelle stammt; (b) jede
überlebende Mutation ist im Bericht mit Ursache benannt (T-060 hat das schon
vorgemacht — das ist der Massstab, nicht die Ausnahme); (c) kein `qa-engineer`
findet einen Wächter, der nur unter einer vom Standardlauf übersprungenen
Auswahl beisst.

**Status:** vorgeschlagen

---

### L-009 — Die Testumgebung misst eine andere Maschine als die des Spielers

**Belege — sechs Fälle, alle in Zyklus 13, jeder für sich ein Zufallsfund:**

| # | Falle | Quelle | Gemessener Unterschied |
|---|---|---|---|
| 1 | **Physische gegen logische Pixel im Screenshot.** Ein nicht DPI-bewusster PowerShell-Prozess schnitt bei 150 % Skalierung den rechten Fensterrand ab | T-052, Methodenteil | Das dritte Panel und die Ecken-Werkzeugleiste schienen reproduzierbar **vollständig zu fehlen** — beinahe ein DR-Eintrag. Nach `SetProcessDPIAware()` weg |
| 2 | **Physische gegen logische Pixel in den Vorgaben.** `DESIGN_REVIEW.md` nennt physische px, `UI_SPEC.md` AK-72/84/90 verlangen logische | T-058 §1 | 1600 physisch = **1067 logisch**. „Hätte ich nur bei 1250/1600/2100 logischen px getestet, wäre DR-016a bei **keiner einzigen Breite** reproduzierbar gewesen — der Wächter wäre grün gewesen und hätte nichts belegt" |
| 3 | **Offscreen-Schrift.** `conftest.py` setzt `QT_QPA_PLATFORM=offscreen` | T-058 §1b | ein Effektname ist offscreen rund **12 px je Zeichen** breit, unter Windows rund **6**. Dieselbe Stelle: 22 px (T-056), 17 px (offscreen), 32 px (Windows) — dieselbe Ursache, drei Zahlen |
| 4 | **Qt-Stil.** `app.py:3714` setzt `Fusion` + dunkle Palette; `tests/rendered.py::laid_out` setzte keinen Stil, lief also unter `windowsvista` | T-059 §1, QA-146 | bis zu **58 px** an genau der Spalte, um die AK-77 geht; die Zahl der gekürzten Namen bei 1600 px springt von **12 auf 44** (Faktor 3,7) |
| 5 | **Die Plattform kann die Bedingung nicht herstellen.** Offscreen hat eine Fenster-Mindestbreite von 964 px | T-059 §1 | der Fall `[833]` misst dort **964** und schreibt 833 in den Namen |
| 6 | **`processEvents` statt echtem Timer.** Screenshot vor der fertigen Layoutrunde | T-059 §14 | übereinander gezeichnete Attributzeilen im `Build planner` — ein Phantombefund, den der `qa-engineer` selbst verworfen hat |

Dazu als siebte Ausprägung derselben Ursache: `QStyle.SE_HeaderLabel` liefert
unter Fusion **2 px** Rand je Seite, unter windowsvista **4** (T-060 §3) — der
Grund, warum ein frisch reparierter Spaltenkopf als `y.` herauskam.

**Ursache (ein Satz):** Eine Zahl über die Oberfläche entsteht in diesem
Projekt in einer Umgebung, die weder benannt noch mit der des Spielers
abgeglichen wird — Plattform, Qt-Stil, Palette, Skalierung und die Frage
physisch/logisch werden je Messung neu und stillschweigend gewählt.

**Gibt es eine Regel, die alle drei — tatsächlich alle sechs — gefangen
hätte?** Ja, eine mit zwei Hälften. Die erste fängt 1, 2, 3, 4 und 7, die
zweite fängt 5 und 6.

**Massnahme.** Zieldatei: `docs/plan-restarbeiten.md`, Abschnitt „Regeln, die
fuer jeden Schritt gelten", neuer Spiegelstrich:

> - **Eine Zahl ueber die Oberflaeche nennt die Umgebung, in der sie
>   entstanden ist** — Plattform (`offscreen` / `windows`), Qt-Stil und
>   Palette, Skalierung, und ob die Pixel physisch oder logisch sind. **Und
>   jede Messung prueft, dass sie den Zustand wirklich erreicht hat, den ihr
>   Name behauptet** — die angeforderte Breite, die fertige Layoutrunde;
>   erreicht sie ihn nicht, ueberspringt sie mit der erreichten Zahl in der
>   Meldung, statt zu messen. Die Testumgebung wird aus **derselben Funktion**
>   gebaut wie das laufende Programm; zwei Stellen, die dasselbe sagen
>   muessen, laufen auseinander.

**Das ist zum grössten Teil Ratifizierung, nicht Neubau.** T-060 hat den
mechanischen Teil bereits gebaut: `nrplanner.app.apply_appearance(app)` wird
von `main()` **und** von `tests/conftest.py::qapp` gerufen, und `laid_out`
überspringt mit der erreichten Breite statt still danebenzumessen. Der
Wächter dazu vergleicht nicht gegen das Literal `"Fusion"`, sondern prüft,
dass `apply_appearance` auf die laufende Anwendung angewandt nichts mehr
ändert — er hält damit „Programm und Suite messen dasselbe" und nicht „beide
messen Fusion". Offen ist nur die Hälfte, die die **Berichtsprosa** betrifft —
und genau die haben T-058 §12.6 und T-059 ausdrücklich für `docs/lessons.md`
angemeldet („der Befund mit der längsten Halbwertszeit aus diesem Auftrag",
„ich schreibe dort nicht hinein").

**Kosten.** Ein Halbsatz je Pixelzahl im Bericht; die Skip-Hälfte kostet
**Bequemlichkeit**: T-060 meldet seither 9 bzw. 10 übersprungene Fälle je
Lauf, und wer alle fünf Breiten sehen will, fährt die Suite zweimal
(`759 + 9 = 758 + 10 = 768`). Das ist der Preis, er ist bereits bezahlt, und
die Regel schreibt ihn fest, damit ihn niemand als „9 Skips, das war früher
grün" zurückdreht.

**Erfolgskriterium.** In den nächsten zwei Zyklen: keine Pixel- oder
Geometriezahl in einem Bericht, in `DESIGN_REVIEW.md` oder in `UI_SPEC.md`
ohne ihre Umgebung; kein Testfall, der eine Breite im Namen führt, die er
nicht erreicht hat; kein Phantombefund aus der Messmethode, der bis in ein
Register gelangt.

**Status:** vorgeschlagen

---

### L-010 — Der Auftrag prüft, was herauskommen soll, nicht, was die Rolle lesen, benutzen und übergeben kann

**Diese Massnahme betrifft ausschliesslich den Director. Belege:**

1. **T-054, der Auftrag lag im falschen Medium.** Der `power-user`-Auftrag
   stand in `docs/tasks/T-054.md`. Sein Bericht beginnt mit
   „GELESEN: bewusst nichts — nur der Auftragstext". Die Rolle liest per
   Definition keine Projektdateien; der Auftrag lag in einer.
2. **T-054, die Werkzeuge fehlten für das eigene Abnahmekriterium.** A11
   verlangt als Nachweis einen `power-user`-Bericht ohne „ich habe geraten".
   Der Lauf hatte **kein Screenshot-Werkzeug und keinen Bildbetrachter**; er
   las das Fenster über die Bedienungshilfen-Schnittstelle, klickte blind auf
   Koordinaten und **musste die README lesen, um die Namen der Registerkarten
   zu erfahren**. Aufgabe 3 wurde durch blindes Klicken auf eine zufällige
   Kachel „gelöst". A11 ist von diesem Lauf **nicht** beantwortbar — T-056 und
   T-059 führen es beide als offen.
3. **T-061, derselbe Werkzeugmangel, diesmal ohne Ausweg.** Der zweite Lauf
   kannte den Umweg über die Bedienungshilfen nicht, konnte das Fenster nicht
   bedienen und meldete **STATUS: blockiert** ohne eine Aussage zu einer der
   sechs Aufgaben. Der Director hat es selbst richtig eingeordnet: „kein
   Befund gegen das Programm, ein Befund gegen meinen Auftrag. **Der Ausweg
   gehört in den Auftrag**, nicht in das Glück des jeweiligen Laufs."
4. **T-056 wurde vor der Ablage seiner wichtigsten Quelle gestartet.** T-056
   nennt `docs/berichte/T-054-power-user.md` „die wichtigste Quelle dieses
   Auftrags". Der `ui-ux-designer` hat mit **vier unabhängigen Zugriffen**
   belegt, dass die Datei nicht existierte, und seine gesamte Vorgabe
   (AK-68 bis AK-105) auf Zitate zweiter Hand plus eigene Messungen gestellt.
   T-057 fand die Datei später auf Platte (05.09., 13:39) — der Director hatte
   sie abgelegt, aber **nach** dem Start der abhängigen Rolle.
5. **`docs/state.md` lief dem Dateisystem voraus.** `docs/state.md:64` führte
   T-054 als „geschrieben", während die Datei nicht existierte. T-056 hat den
   Widerspruch benannt: „Das ist mit dem Dateisystem nicht vereinbar."
6. **Der Zuschnitt zwischen T-057 und T-058 wurde an „Geometrie" gezogen, und
   zwei Vorgaben fielen dazwischen.** T-057 §7: DR-017/AK-83 und DR-018/AK-75
   liegen im für T-058 reservierten Bereich, sind aber keine Geometrie —
   „Ich habe sie nicht gemacht und lege sie dir vor." Eine Runde später hat
   T-058 sie erledigt.
7. **Der Wortlaut-Platzhalter kreuzte drei Aufträge.** T-048 baute
   `[wording pending OF-20]`, T-053 musste ihn in `[wording pending: QA-113]`
   umbenennen, weil OF-20 inzwischen beantwortet war und der Marker sonst auf
   eine erledigte Frage zeigte, T-057 ersetzte ihn. Die Rolle, die den
   Wortlaut entscheidet, wurde zweimal **nach** der Rolle beauftragt, die ihn
   braucht.

**Ursache (ein Satz):** Der Auftrag wird aus dem Ergebnis heraus geschrieben,
das er erzeugen soll, und nicht aus den Voraussetzungen der Rolle — kann sie
lesen, worauf er sie stützt; hat sie die Werkzeuge, die sein Abnahmekriterium
verlangt; liegen die Quellen, die er nennt, als Datei vor.

**Massnahme.** Zieldatei: `docs/plan-restarbeiten.md`, Abschnitt „Regeln, die
fuer jeden Schritt gelten", neuer Spiegelstrich — **er richtet sich an den
Director und ändert keine Agentendefinition**:

> - **Vor jedem Dispatch drei Zeilen pruefen.** (1) *Medium:* Kann die Rolle
>   alles lesen, worauf der Auftrag sie stuetzt? Rollen ohne Dateizugriff
>   (`power-user`) bekommen den Auftrag **im Nachrichtentext**, nie als Pfad.
>   (2) *Werkzeug:* Hat die Rolle die Werkzeuge, die das Abnahmekriterium
>   verlangt, und kennt sie den bekannten Umweg, falls einer noetig ist? Wenn
>   nein, ist der Lauf kein Nachweis, und der Auftrag wartet, statt zu
>   laufen. (3) *Quelle:* Liegen alle Berichte, die dieser Auftrag als Quelle
>   nennt, als Datei unter `docs/berichte/`? Berichte von Rollen ohne Write
>   legt der Director ab, **bevor** er die abhaengige Rolle startet — und
>   `docs/state.md` sagt „geschrieben" erst danach.

**Kosten.** Eine Minute je Dispatch. Dagegen steht, was in diesen zwei Zyklen
tatsächlich verloren ging: ein vollständig abgebrochener `power-user`-Lauf
(T-061), ein zweiter, der A11 nicht beantworten konnte (T-054), eine
Spec-Runde über 38 Akzeptanzkriterien auf Zitaten zweiter Hand (T-056), und
eine Rückrunde für AK-83/AK-75. Das Verhältnis ist eindeutig.

**Erfolgskriterium.** In den nächsten zwei Zyklen beginnt **kein** Bericht mit
„die wichtigste Quelle fehlt", **keiner** meldet ein Werkzeug, das sein
eigenes Abnahmekriterium verlangt und das er nicht hatte, und **kein**
Statuswort in `docs/state.md` steht vor der Datei, die es behauptet.

**Status:** vorgeschlagen

---

### L-011 — „Richtiger als ihre Begründung": ein Muster, und ausdrücklich ohne eigene Massnahme

**Belege — zehn Fälle, nicht drei:**

| # | Entscheidung / Code | Die Begründung, die nicht trug | Quelle |
|---|---|---|---|
| 1 | `damage.equipped` statt `candidate` (QA-101) | „Die Rangfolge wäre in beiden Fällen dieselbe, die Strafe ist ein konstanter Faktor" — **gemessen falsch**: R0 −12,36 gegen +21,36, Reihenfolge gedreht, 10 von 309 Relikten betroffen. Der Satz stand an **drei** Stellen im Repo, u. a. als `survival_means` in `mutate.py` | T-041 §5, T-048 §4 |
| 2 | Cache-Schlüssel positionsabhängig (D3) | „die Slots tragen verschiedene Farben, die Menge der freien Slots ist eine andere" — beides trägt nicht; der wirkliche Grund ist, dass die Antwort **Slotindizes** trägt und AD-016.4s Rückabbildung nie gebaut wurde. Der `architect` benennt es selbst als „dieselbe Lage wie bei QA-101" | T-047 §3.3 |
| 3 | Die Klammerung des Faktors (QA-115) | Kommentar nennt „574 von 350 160", belegt durch `dump_rate.py` — das **nie existierte**. Nachgemessen: **544**, und die eigentliche Aussage **stärker** als behauptet (0 von 350 160) | T-045 D-1/D-3, T-048 §5 |
| 4 | `inventory.copy_key` (QA-112) | „a save whose loadout table cannot be read yields no handles at all" — der Code liest den Handle aus dem **Relikt-Datensatz**; die zwei realen Wege zu `handle=None` stehen nirgends. **Auf dieser falschen Begründung stand die Abwägung zu AD-013.4, die dem Director gerade zur Entscheidung vorlag** | T-037, T-041 §6.2 |
| 5 | `effect_ids_of` (QA-109) | „the same three sources … **in the same order**" — gemessen: gleiche Multimenge, andere Reihenfolge; keine Zahl bewegt sich | T-041 §10 |
| 6 | `mutate.py::newline_of` | Begründung nennt CRLF in `app.py`; zwei Berichte erklärten sie für veraltet — und T-057 mass, dass die **Korrektur** ihrerseits halb falsch war: der Archivbaum ist LF, der Arbeitsbaum wirklich CRLF (3744/0) | T-037, T-048 §7, T-057 §5 |
| 7 | Wahl der Waffen-Id 34750000 | T-043 begründete sie mit „Endung `750000` bedeutet Startwaffe" — die zehn Startwaffen enden alle so, aber 34750000 ist keine. Die Wahl wurde behalten | T-046 §7 |
| 8 | Die neue Farblegende im Nightlord-Panel | „Everything else on this panel is read from the game's own files" — der Satz war **falsch**, zwei Sichtungszeilen stehen in der gewöhnlichen Farbe. Vom Autor selbst am eigenen Screenshot gefunden und gekürzt | T-060 §12.2 |
| 9 | „Zieh die vier festen Spaltenzahlen nach" | Der Director begründete die Anweisung mit „sie sind sichtbar, **jetzt**, im Auslieferungszustand". Gemessen: wahr für den Picker, **falsch für die anderen drei** bis hinunter zur Fenster-Mindestbreite von 760 px | T-060 §7 |
| 10 | Der Fix zu QA-141 | „Was QA-141 geschlossen hat, ist `CardGrid` — **nicht** die Herleitung der Öffnungsbreite", die der Wächter zu bewachen behauptete. Nur die überlebende Mutation zeigte es | T-060 §9a |

Dazu zwei Fälle in dieselbe Richtung, aber mit **zu schwacher** statt falscher
Begründung: DR-008 („ununterscheidbar" — tatsächlich stand die nicht
ausrüstbare Zeile bei Tier 1 **über** der echten und bewegte sich beim
Aufstieg nicht, T-053 §1.4), und QA-119, dessen Klasse besteht, während sein
genannter Auslöser auf dem heutigen Datensatz nicht mehr reproduzierbar ist
(T-055).

**Ist es Zufall?** Nein. Zehn Fälle in zwei Zyklen sind ein Muster, und es
verteilt sich über **alle** Rollen einschliesslich des Directors (Fälle 2
und 9) — es ist also keine Eigenschaft einer Rolle, sondern des Vorgehens.

**Ursache (ein Satz):** In diesem Projekt wird die **Entscheidung** gemessen
und die **Begründung** nicht — Mutation, Differentiallauf und Auszählung
belegen das Verhalten, nie den Satz daneben; der Satz bleibt im Repo stehen
(Docstring, `survival_means`, `Goal.scope`, Kommentar, Befundtext) und wird
von der nächsten Rolle als belegt gelesen.

**Massnahme: keine — bewusst verworfen.** Begründung, weil das selbst ein
Ergebnis ist:

- **Es fängt sich.** In allen zehn Fällen hat eine spätere Rolle die falsche
  Begründung gefunden, meist im nächsten Auftrag, und in **keinem** Fall ist
  daraus eine falsche Entscheidung geworden. Der schärfste Fast-Schaden
  (Fall 1: „hätte der Director auf dieser Grundlage `candidate` gewählt, wäre
  das ein A3-Fehler gewesen") wurde vor der Entscheidung gemessen.
- **Die eine Hälfte, die wirklich schadet, hat schon eine Regel.** Fälle 3
  und 7 sind Zahlen ohne Rezept — teamweites L-001. Diese Regel hat QA-115
  gefunden und T-048 zur Nachmessung gezwungen. Sie wirkt; sie braucht keine
  zweite.
- **Die Kosten wären hoch und träfen das Beste am Projekt.** Eine Regel
  „jede Begründung braucht ihre Messung" legt eine Beweislast auf die Prosa
  eines Projekts, das seine Begründungen ausdrücklich in den Docstrings führt
  (T-037: „dieses Projekt führt seine Begründungen in den Docstrings").
  Teure Sätze werden kurze Sätze. Der Schaden dieser Massnahme wäre grösser
  als der Schaden, den sie verhütet.

**Auslöser, ab dem daraus doch eine Massnahme wird** (Beobachtungsliste): ein
Fall, in dem eine falsche Begründung eine Entscheidung **bis zum Ende trägt** —
also nicht wie QA-112 kurz vor der Vorlage gefunden wird, sondern in einem
umgesetzten Fix, einer freigegebenen Spec oder einer Nutzerentscheidung
landet. Dann lautet die Massnahme: der Satz, der eine Entscheidung begründet
und im Repo stehen bleibt, nennt entweder seine Messung oder trägt das Wort,
das ihn als ungeprüft kennzeichnet.

**Status:** vorgeschlagen — **ohne Massnahme, mit Auslöser**

---

### Beobachtungen (noch kein Muster)

- **38 Akzeptanzkriterien in einem Zug, sechs innere Widersprüche
  (05.09.2026, einmalig).** T-056 hat AK-68 bis AK-105 in einem Durchgang
  vergeben. Bei der Umsetzung fielen auf: AK-81s eigene Beispielzahlen
  widersprechen AK-81s Regel (T-057 §10.5); AK-82 („set above") widerspricht
  AK-68 (Kopfzeile über die Bedienelemente) (T-057 §10.6); AK-67 deckt zwei
  Sätze, das Feld trägt drei (T-053 §6.3); AK-88 wörtlich genommen verlangte
  eine Umbenennung quer durch Extraktor und Fassade ohne sichtbaren Gewinn
  (T-057 §6); AK-99s Breitenzusicherung wurde als halb umgesetzt gemeldet und
  fiel eine Runde später (QA-144); AK-70 Punkt 10 nennt eine Stelle, für die
  §7 keinen Wortlaut festlegt. Alle sechs wurden gemeldet und in drei
  Director-Nachträgen geschlossen — das System hat funktioniert. Beobachtung,
  weil es **einmalig** ist: es gab bisher keinen zweiten Spec-Block dieser
  Grösse. Beim zweiten Mal wäre die Frage, ob eine Spec-Charge eine
  Konsistenzprüfung braucht, bevor sie in einen Auftrag geht.
- **Parallellauf: die Regel deckt Code, nicht Dokumente (mehrfach, bislang
  ohne Schaden).** `docs/state.md` sagt „sequenziell, nie zwei Agenten auf
  demselben Code". Für Dokumente gilt sie nicht, und das kostet in jedem
  Bericht einen Absatz: T-041 („`UI_SPEC.md` und `qa/findings.md` sind während
  meines Laufs von der parallelen Session geändert worden"), T-047, T-048,
  T-052, T-058 und T-060 führen alle eine Liste fremd geänderter Dateien.
  T-051 hat **+207 Zeilen in `DESIGN_REVIEW.md` und einen neuen
  Screenshot-Ordner untersuchen müssen**, um auszuschliessen, dass sie von ihm
  stammen. Bislang ist daraus kein Fehler entstanden, nur Aufwand — deshalb
  Beobachtung. Beim ersten Mal, dass zwei Rollen dasselbe Dokument
  gleichzeitig fortschreiben und eine Fassung verlorengeht, wird es ein
  Muster.
- **`ruff` (F-A), fünfte Erwähnung.** Ohne Linter ist „Linter sauber" in der
  DoD jeder Rolle unprüfbar; T-037, T-045, T-046, T-048, T-053, T-057, T-058
  und T-060 tragen deshalb je einen offenen DoD-Punkt und liefern
  Ersatzbelege (`compileall`, Zeilenbreite von Hand). Das ist keine
  Teamfrage, sondern eine offene **Nutzerentscheidung** — hier nur
  festgehalten, damit die Zahl der Erwähnungen sichtbar bleibt.
- **GOAL A9 (gebautes Artefakt) ist in 13 Zyklen von niemandem geprüft
  worden.** Jeder `developer`-Bericht führt es unter „ungeprüft ausgewiesen".
  Kein Prozessfehler — es ist bewusst in P9 geparkt —, aber es ist der Punkt,
  an dem die sonst vorbildliche Ehrlichkeit der Berichte eine Lücke seit dem
  ersten Zyklus unverändert offen hält.

---

## Zyklus 16 — 2026-09-08

**Ziel des Zyklus:** der Release-Weg. **15** Auftragsdateien (T-104 bis T-118,
gezaehlt mit `ls docs/tasks/`; die Zahl "dreizehn" im Auftrag T-119 ist falsch),
**14** Berichte auf Platte (T-104 bis T-117, T-118 laeuft noch). Erstes gebautes
und geprueftes Artefakt des Projekts. **A2 erfuellt** (SEC-009, T-105),
**A9 geprueft** (T-114, 5 von 6 PASS).

**Datengrundlage:** die 14 Berichte, 15 Auftragsdateien, `qa/findings.md`
(QA-198 bis QA-207), `security/findings.md`, `GOAL.md`, `docs/state.md`,
`docs/plan-restarbeiten.md`, `CLAUDE.md`, `docs/legal/C-003.md` und
`C-004.md`, die Git-Historie beider Repositorien (Projekt und
`claude-agent-team`), die Rollendefinitionen unter `~/.claude/agents/`,
`~/.claude/commands/director.md`, `~/.claude/settings.json`, die Hooks unter
`~/.claude/hooks/` und die Protokolle unter `~/.claude/state/`.

**Nummernraum:** L-014 bis L-018 sind als **teamweite** Nummern vergeben
(L-012/L-013 sind teamweit belegt, L-011 war die letzte hier). Projekteigene
Regeln tragen weiterhin **NH-** und stehen in `docs/plan-restarbeiten.md`.

### Gut gelaufen (schuetzenswert)

- **Die parallele Pruefphase hat gehalten.** Drei Paare liefen gleichzeitig
  (T-104/T-105, T-106/T-107, T-114/T-115); **kein** Bericht meldet verlorene
  oder ueberschriebene Arbeit. T-114 hat einen fremden Prozess
  (`pytest -q tests/test_wortwahl_oberflaeche.py`, Datei im Baum nicht
  vorhanden) bemerkt und gemeldet, statt ihn zu ignorieren.
- **Die parallele Suite ist der groesste Einzelgewinn des Tages:** 840 s → 127 s
  (`4431c7a`), Namensvergleich ueber 1265 Faelle ohne Abweichung. Sie hat den
  Volllauf zurueck in den Vordergrund geholt und damit die Klasse "Lauf stirbt
  im Hintergrundwarten" fuer dieses Projekt geschlossen.
- **Der Waechter aus T-109 erfuellt L-008 vollstaendig und ohne Aufforderung:**
  Mutation im Standardlauf rot (`AssertionError` mit genanntem Zusatzeintrag),
  Erwartung als Literal statt aus der bewachten Konstante, Ruecknahme ueber eine
  Kopie statt ueber `git checkout --`, danach `git diff` leer. Ein Waechter, ein
  vollstaendiger Nachweis.
- **Rollen widersprechen dem Auftrag mit Messung.** T-113 hat die zwei
  Umlenkungen des Auftrags gegen `nrplanner/shortcut.py` und die `README`
  geprueft und die dritte eingefordert. T-115 hat am selben Artefakt kurz nach
  T-113 eine Zahl gemessen, die den frisch eingetragenen Befund QA-198
  widerlegte — und sie berichtet, statt sie an den Bestand anzupassen.
- **Absenz-Behauptungen der Rollen tragen ihren Nachweis** (L-013): T-113
  schreibt "Kein CHANGELOG.md im Repo vorhanden (geprueft: git-weite Suche nach
  CHANGELOG*, kein Treffer)" statt "gibt es nicht".
- **NH-002/L-012 haelt:** T-114 hat seine Bildnachweise ueber `PrintWindow` auf
  dem eigenen HWND gezogen und NH-002 ausdruecklich genannt. In
  `docs/screenshots` ist im ganzen Zyklus **keine** Datei dazugekommen.
- **Der Director hat seine eigenen Fehler protokolliert**, in `docs/state.md`
  ("Buchfuehrung des Directors"), im Kopf von
  `docs/berichte/T-115-power-user.md` und in der Korrektur unter QA-198. Ohne
  diese Selbstprotokolle waere diese Retrospektive nicht moeglich gewesen.
  **Das ist die wertvollste Gewohnheit des Zyklus und darf durch keine
  Massnahme unattraktiv werden.**

### Wirkungskontrolle frueherer Massnahmen

| ID | Massnahme | Uebernommen am | Wirkung | Konsequenz |
|---|---|---|---|---|
| **L-008** (teamweit) — ein Gegenbau muss beissen | 2026-09-06 | **Wirkt.** Ein neuer Waechter im Zyklus (T-109, A-030), **1 von 1** mit allen drei Bedingungen belegt: Standardlauf rot, Erwartung als Literal, saubere Ruecknahme nachgewiesen. | Keine. |
| **L-009** (teamweit) — jede Zahl nennt ihre Messumgebung | 2026-09-06 | **Wirkt bei den Rollen.** QA-198 traegt beide Messungen mit Umgebungsspalte (5 min, "isoliertes Verzeichnis, nach einem v1.7.1-Lauf" gegen 107 s, "frisches Testverzeichnis"). Genau diese Spalte macht sichtbar, dass die Spanne der Befund ist. | Keine. |
| **L-010** (Director) — fuenf Pruefungen vor jedem Dispatch | 2026-09-06 (`commands/director.md:585`) | **Drei von fuenf wirken, eine kippt, eine ist gebrochen.** P1 *Medium*: gehalten — T-115 kam als Nachrichtentext, der Bericht sagt "GELESEN: bewusst nichts — nur der Auftragstext". P3 *Quelle*: gehalten — T-110- und T-111-Bericht lagen vor den abhaengigen Auftraegen. P5 *Beweisstelle/feste Aufgabenliste*: **wirkt** — T-115 lief mit stehender Liste, QA-170 wurde dadurch reproduziert. P4 *Zitat*: formal erfuellt (12 von 15 Auftragsdateien tragen woertliche Zitate; die 3 ohne sind T-110/T-115/T-116, reine Ausfuehrungsauftraege) — **und hat genau dadurch die falsche Praemisse in vier Auftragsdateien getragen**. P2 *Werkzeug*: **gebrochen** — T-113 hatte kein GUI-Automatisierungswerkzeug fuer einen Auftrag, der Bedienung verlangt, und hat Speicherzustaende in der Registry nachgebildet. Das ist der **vierte** Fall dieser Art (T-054, T-061, 06.09., T-113). | P4: Quittungspflicht → **L-015**. P2: kein neuer Regeltext — der Text steht seit dem 06.09. da und wurde nicht ausgefuehrt; das ist **L-014**. |
| **L-011** (teamweit) — "richtiger als ihre Begruendung", ohne Massnahme | Ausloeser: naechstes Vorkommen | **Kein neuer Fall dieser Bauform belegt.** Kein Bericht des Zyklus meldet Code, der aus einem anderen Grund richtig ist als dem angegebenen. | Bleibt ohne Massnahme, Ausloeser bleibt stehen. |
| **L-012** (teamweit) — Bildnachweise aus dem Fenster | 2026-09-06 | **Wirkt.** T-114 zieht ueber `PrintWindow` auf das eigene HWND und nennt NH-002; 0 neue Dateien unter `docs/screenshots` im Zyklus (letzter Ordner `2026-09-06-T068`). | Keine. |
| **L-013** (teamweit) — eine Absenz-Behauptung traegt ihren Nenner | 2026-09-06 | **Wirkt bei den Rollen, wirkt nicht beim Director.** Rolle: T-113s CHANGELOG-Absenz mit genannter Suche. Director: "`AUFLAGEN.md` nicht vorhanden" (die Datei liegt seit `9631cbb`, 02.09. 01:31) und "es gibt bis heute keine EXE" (12 Releases, `gh release list`) — **beide ohne Nenner, beide falsch.** Der Unterschied ist nicht Sorgfalt, sondern **Ort**: L-013 steht in den Rollendefinitionen und in `_rahmen.md`, und `_rahmen.md` bindet den Director nicht (`commands/director.md:520` verweist andere darauf, uebernimmt es nicht). | → **L-014**. |
| **NH-001** — je nicht-trivialem Auftrag eine Datei | 2026-09-06 | **Wirkt, 15 von 15.** In Zyklus 13 zweimal gebrochen, seither lueckenlos. Auch die zwei kleinsten Auftraege (T-110, T-116, je unter 50 Zeilen) haben eine Datei. | Keine. |
| **`model: sonnet` beim Retest** | 03.09. als Pflicht, 06.09. als Hook | **Wirkt — aber nur der Hook, nicht die Regel.** `~/.claude/state/dispatch-modell.log`: **4 von 4** qa-Retests am 06./07.09. wurden vom Hook herabgestuft; zweimal kam der Dispatch als "(Standard)", zweimal als "opus". Der Director hat das Modell in **0 von 4** Faellen selbst gesetzt. In Zyklus 16 gab es keinen Retest, also keinen neuen Datenpunkt. | Keine eigene — aber es ist der **Beweis der Bauform**, auf der L-014 aufsetzt: eine Regel im Fliesstext des Directors wirkte in 21 Faellen nicht, dieselbe Regel als Hook wirkt in 4 von 4. |
| **Parallele Pruefphase** | 07.09. | **Wirkt.** Drei Paare, kein gemeldeter Verlust, ein korrekt gemeldeter Fremdprozess. | Keine. |

---

### L-014 — Der Director liest seine eigenen Notizen als Messung, und die Regel dagegen stand schon da

**Belege — acht Vorkommen in einem Zyklus, alle beim Director, alle derselben
Form:**

| # | Aussage | Was sie wirklich war | Die Primaerquelle, die es gab | Quelle |
|---|---|---|---|---|
| 1 | SEC-022, SEC-024, QA-194 "offen" | Statuszeile, nach dem Fix nie nachgezogen | `git log -S` gegen den Stand | `1b00eb6` |
| 2 | SEC-009 in der Tabelle "offen" | derselbe Befund stand im Abschnitt darunter als behoben | dieselbe Datei, wenige Zeilen tiefer | `41fba5a`, gefunden vom `release-manager` |
| 3 | `docs/legal/AUFLAGEN.md` "nicht vorhanden" | Erinnerung | `ls docs/legal/` — die Datei liegt seit `9631cbb`, 02.09. 01:31 | `docs/state.md`, Abschnitt Buchfuehrung |
| 4 | "es gibt bis heute keine EXE" | eine Zeile aus `docs/state.md`, seit mehreren Zyklen | `gh release list` — **12** Releases, juengstes `v1.7.1` vom 24.08., 25 Downloads | `81547f3`, gefunden vom `release-manager` in T-106 |
| 5 | zwei Umlenkungen fuer den `clean-room` | uebernommen aus dem T-111-Bericht | `nrplanner/shortcut.py:44-49` und die `README` nennen **drei** | Nachtrag in `docs/tasks/T-113.md`, `a2980bf` |
| 6 | QA-198 "fuenfmal so lange wie angesagt" | **eine** Messung, als Regel geschrieben | eine zweite Messung; sie kam 90 min spaeter und ergab ein Drittel | QA-198 (Fliesstext seit dem 12.09.2026 in `qa/verlauf.md`) |
| 7 | "dreizehn Auftraege (T-104 bis T-118)" | geschaetzt | `ls docs/tasks/` — **15** | `docs/tasks/T-119.md:13` |
| 8 | "der `power-user` hat seinen Bericht **trotz Schreibrecht** nicht abgelegt" | Annahme ueber eine Rollendefinition | `~/.claude/agents/power-user.md`: `tools:` enthaelt **kein** `Write` und **kein** `Edit`; der Fliesstext sagt "**Du schreibst keine Datei.** … abgelegt wird er vom `director`" | `CLAUDE.md`, Abschnitt "Der Bericht ist Teil des Auftrags" (geschrieben 08.09. 10:04, `9f438f9`) |

**Was der Zyklus dafuer bezahlt hat:** Beleg 4 lief in den Fragebogen an den
Nutzer, in **vier** Auftragsdateien (T-104, T-105, T-106, T-107) und in den
Bericht an den Nutzer; `docs/legal/C-003.md` (867 Zeilen) setzte darauf auf und
musste durch `docs/legal/C-004.md` (558 Zeilen) nachgezogen werden. Beleg 5 hat
eine Verknuepfung im **echten** Start-Menue des Nutzers erzeugt. Beleg 8 steht
heute unkorrigiert in der Datei, mit der der naechste Zyklus startet — und wenn
der Director ihr glaubt, legt er den naechsten `power-user`-Bericht **nicht**
mehr ab, und der Bericht ist dann ganz weg.

**Ursache — und sie ist nicht "zu wenig Sorgfalt":** Die Regeln, die genau diese
acht Faelle verbieten, **stehen bereits woertlich in `commands/director.md`**:

- *"Ein Befundstatus wird geprueft, nicht erinnert. … Die Statuszeile in
  `qa/findings.md` ist eine Notiz, kein Messwert"* — Zeile 1019, eingefuegt
  **07.09. 18:35** (`9b2c986`), also **drei Stunden vor** dem Beginn dieses
  Zyklus. Im Zyklus fuenfmal gebrochen (Belege 1, 2).
- *"Absenz-Behauptungen brauchen eine Durchsicht, keinen Grep"* — Zeile 1038,
  eingefuegt **02.09. 20:44** (`6adba6f`). Zweimal gebrochen (Belege 3, 4).
- *"Eine Regel aus wenigen Beispielen ist eine Hypothese, keine Tatsache. …
  Was du nicht gemessen hast, gibst du nicht als gemessen aus"* — Zeile 1047,
  gleiche Herkunft. Zweimal gebrochen (Belege 6, 7).

Die Ursache ist also der **Ort**, nicht der Wortlaut: `commands/director.md` ist
von 355 Zeilen (01.09.) auf **1085 Zeilen** (08.09.) gewachsen; die drei Saetze
stehen in einem Fliesstextkapitel ab Zeile 1019, das die Sitzung **einmal beim
Aufruf** liest. An keiner Stelle des Ablaufs — Befund eintragen, `state.md`
schreiben, Auftrag verfassen — wird die Regel ausgeloest. **Der Gegenbeweis
liegt im selben Repo:** dieselbe Sorte Regel (`model: sonnet` beim Retest)
wirkte im Fliesstext in 0 von 21 Faellen und als Hook in 4 von 4.

**Massnahme.** Zieldatei: **`hooks/remind-rules.ps1`** (Agenten-Repo
`claude-agent-team`), registriert in `~/.claude/settings.json` als
`UserPromptSubmit` — geprueft, der Hook laeuft. Die Variable `$rules` wird
erweitert; der bestehende Text bleibt woertlich stehen, angehaengt wird:

> ` Director: a status line, a note in state.md or another role's report is a NOTE, not a measurement - before it goes into a task file, into state.md or into a message to the user, check the primary source (git log -S / --grep for finding status, ls or git log for "does not exist", gh release list for releases, the agent definition for what a role may do) and name it. An absence claim without a named search is a guess. One observation is a hypothesis, not a rule - a number you did not count stays out.`

**Wer liest ihn wann:** der Director, bei **jedem** Prompt des Nutzers, ohne
Zutun. Das ist die einzige Stelle im heutigen Aufbau, die der Director oefter
als einmal je Sitzung liest.

**Kosten.** Rund 60 Woerter zusaetzlicher Kontext je Nutzer-Prompt (der Hook
traegt heute rund 50). Ein `git log -S` je Befund-Id kostet Sekunden. Dagegen
stehen in **einem** Zyklus: 558 Zeilen Rechts-Nacharbeit, vier Auftragsdateien
auf falschem Sachverhalt, eine Verknuepfung im echten Nutzerprofil.

**Schaerfere, teurere Alternative** (dem Nutzer zur Wahl, nicht als Erstes
empfohlen): derselbe Text als `PreToolUse`-Hook mit Matcher `Write|Edit`, der
nur anschlaegt, wenn der Pfad auf `state.md`, `*findings.md` oder
`docs/tasks/T-*.md` zeigt. Genauer im Ausloeser, aber er feuert auch bei jedem
Subagenten und ist ein neuer Hook statt einer geaenderten Zeile.

**Erfolgskriterium.** In den naechsten zwei Zyklen steht in `docs/state.md` kein
Abschnitt "Buchfuehrung des Directors" mit einem Fehler der Bauform "Notiz statt
Messung", und keine Rolle findet eine solche Aussage in ihrem Auftrag.
Gegenprobe: mindestens **eine** Aussage je Zyklus, bei der der Director die
Primaerquelle im Auftrag mitnennt (z. B. "12 Releases, `gh release list`,
08.09.").

**Status:** **angenommen und umgesetzt am 08.09.2026** (Nutzer)

---

### L-015 — Pruefung 4 macht `docs/state.md` zur Primaerquelle jeder Rolle

**Belege:**

1. **Die falsche Praemisse reiste als woertliches Zitat.** T-104 zitiert
   `docs/state.md` im Blockzitat einschliesslich der Tabellenzeile "heute keine
   EXE"; T-105, T-106 und T-107 tragen denselben Satz. Alle vier Rollen haben
   ihn korrekt als Vorgabe behandelt — er stand ja im woertlichen Zitat.
2. **Der `compliance-agent` hat darauf 867 Zeilen aufgebaut**
   (`docs/legal/C-003.md`), weil sein Auftrag den Sachverhalt zitierte und er
   ihn per Definition nicht gegenpruefen konnte (`disallowedTools: Bash,
   PowerShell` — er kann `gh` gar nicht aufrufen). Korrektur: `C-004.md`,
   558 Zeilen.
3. **Dieselbe Mechanik hat auch die Korrektur transportiert:** T-109, T-111 und
   T-114 zitieren den Korrekturabsatz woertlich. Der Kanal ist gut; die Quelle
   ist es nicht.
4. **Die Umlenkungen von T-113** kamen aus dem T-111-Bericht in den Auftrag,
   ohne Abgleich gegen den Code und die `README`, die das Team eine Stunde
   vorher selbst geschrieben hatte.

**Ursache (ein Satz):** Pruefung 4 verlangt das woertliche Zitat und schafft
damit Verbindlichkeit — aber sie verlangt nicht, dass das Zitierte selbst eine
Primaerquelle hat, und macht so aus einer Director-Notiz in jedem Auftrag eine
Tatsache, der die Rolle nicht widersprechen kann.

**Massnahme.** Zieldatei: **`commands/director.md`**, Pruefung 4 ("Zitat") im
Abschnitt "Fuenf Pruefungen vor jedem Dispatch" — **ein** Absatz wird
angehaengt, nichts wird ersetzt:

> Ist das Zitierte eine **Tatsachenbehauptung ueber den Bestand** — ein
> Befundstatus, "existiert nicht", eine Zahl, eine Dateiliste —, schreibst du
> **die Quittung dazu**, in Klammern hinter das Zitat: den Befehl und das
> Datum, mit dem du es zuletzt geprueft hast (`gh release list`, 08.09.). Hast
> du keine, ist es keine Vorgabe, sondern eine Annahme — dann kennzeichne sie
> als solche und sag der Rolle ausdruecklich, dass sie ihr widersprechen darf.

**Wer liest ihn wann:** der Director, unmittelbar vor jedem Dispatch —
Pruefung 4 ist eine Checkliste, die er ohnehin abarbeitet, und sie steht
**nicht** im Fliesstextkapitel, sondern im Ablaufteil.

**Kosten.** Eine Klammer je zitierter Tatsachenbehauptung, etwa zwei bis vier je
Auftrag. Sie erzwingt genau die Pruefung aus L-014 an dem Punkt, an dem die
Aussage teuer wird — der Weitergabe.

**Erfolgskriterium.** In den naechsten zwei Zyklen traegt **jede** zitierte
Bestandsaussage in `docs/tasks/` entweder eine Quittung oder die Kennzeichnung
als Annahme; nachpruefbar mit einem `grep` ueber die Auftragsdateien. Und: kein
Bericht meldet, dass ein zitierter Sachverhalt nicht stimmte.

**Status:** **angenommen und umgesetzt am 08.09.2026** (Nutzer)

---

### L-016 — Eine Korrektur schliesst die Fundstelle, nicht die Aussage

**Belege:**

1. **QA-198 traegt seine widerlegte Behauptung weiter in der Ueberschrift.**
   QA-198 (Fliesstext seit dem 12.09.2026 in `qa/verlauf.md`) heisst bis heute "Der Erstaufbau dauert **fuenfmal so
   lange**, wie das Programm ansagt", waehrend zwanzig Zeilen tiefer steht, dass
   genau das eine Hypothese aus einer einzigen Messung war. Wer die Befundliste
   ueberfliegt — und das ist die uebliche Benutzung —, liest die widerlegte
   Fassung.
2. **`CLAUDE.md` enthaelt seit dem 08.09. 10:04 eine neu geschriebene falsche
   Aussage:** "Am 08.09.2026 hat der `power-user` seinen Bericht **trotz
   Schreibrecht** nicht abgelegt." Der `power-user` hat weder `Write` noch
   `Edit`, und seine Definition untersagt ihm ausdruecklich, eine Datei zu
   schreiben. Die Regel darueber ("eine Rolle **mit** Schreibrecht gilt erst als
   fertig, wenn …") ist richtig; ihre Begruendung ist falsch, und sie zeigt auf
   die falsche Rolle.
3. Zum Vergleich: fuer **Befunde** gilt teamweit L-006 (Eigenschaft statt
   Fundstelle, projektweite Suche mit zwei unabhaengigen Masken, Trefferzahl im
   Bericht) — und die Regel wirkt seit sieben Berichten. Fuer **Aussagen des
   Directors ueber den Bestand** gilt sie nicht.

**Ursache (ein Satz):** Eine widerlegte Aussage wird dort korrigiert, wo sie
widerlegt wurde, und nicht dort, wo sie sonst noch steht — obwohl das Team fuer
Befunde genau diese Suche seit dem 03.09. verbindlich fuehrt.

**Massnahme — zwei konkrete Textaenderungen in diesem Projekt, sofort:**

**(a) Zieldatei `CLAUDE.md`**, Abschnitt "Der Bericht ist Teil des Auftrags",
die beiden letzten Saetze werden ersetzt durch:

> Eine Rolle **mit** `Write` gilt erst als fertig, wenn
> `docs/berichte/T-###-<rolle>.md` auf der Platte liegt. Rollen **ohne** `Write`
> — heute `power-user`, `qa-engineer`, `security-reviewer`, `archivist`,
> `fehlerdiagnostiker` — liefern den Bericht vollstaendig in der Antwort; **der
> Director legt ihn ab, bevor die naechste Rolle startet** (L-010, Pruefung 3).
> Am 08.09.2026 wurde der `power-user`-Bericht zu T-115 vom Director
> nachgetragen; das war **richtig so** und keine Verfehlung der Rolle.

**(b) Zieldatei `qa/findings.md`**, Ueberschrift QA-198:

> `## QA-198 — Der Erstaufbau dauert unvorhersagbar lange (107 s bis 5 min), das Programm sagt "etwa eine Minute"`

**Wer liest das wann:** `CLAUDE.md` liest jede Rolle in jedem Auftrag (der
Director verweist seit `9f438f9` auf den Abschnitt "Projektzeilen fuer jeden
Auftrag"); die Befundueberschrift liest jeder, der die Befundliste ueberfliegt.

**Kosten.** Zwei Textaenderungen, zusammen unter zehn Zeilen. Kein neuer
Regeltext, keine zusaetzliche Pflicht je Auftrag.

**Erfolgskriterium.** In den naechsten zwei Zyklen enthaelt keine Ueberschrift in
`qa/findings.md` oder `security/findings.md` eine Aussage, die ihr eigener Text
widerlegt, und kein Auftrag stuetzt sich auf eine Aussage ueber Rollenrechte,
die die Rollendefinition nicht deckt.

**Status:** **angenommen und umgesetzt am 08.09.2026** (Director, Projektmassnahme)

---

### L-017 — Der Regelbestand waechst monoton, und die juengste Regel verdraengt die aeltere

**Belege:**

1. **`commands/director.md`: 355 → 1085 Zeilen in sieben Tagen** (+206 %,
   gezaehlt ueber 26 Commits seit 01.09.). Die drei Saetze, die die acht Fehler
   aus L-014 verhindert haetten, liegen ab Zeile 1019.
2. **Der gemeinsame Rahmen ist in sieben Tagen viermal umgebaut worden** —
   Fliesstext der Projekte, `templates/task.md`, fuenfzehn Rollendefinitionen,
   `_rahmen.md` —, jeder Umbau mit einer eigenen Verlustart (verfaellt, kostet
   Zuege, laeuft auseinander; drei Regeln kamen in **null** Rollen an,
   `_rahmen.md` Zeilen 6-25).
3. **Die Wirkung wird nicht gemessen, weil die Protokolle sie nicht hergeben.**
   `~/.claude/state/kontrakt-verstoesse.log` (36 Zeilen),
   `dispatch-modell.log` und `zugschwelle.log` fuehren Sitzung, Agent und Rolle,
   aber **kein Projekt** — die sieben Eintraege im Zeitfenster von Zyklus 16
   stammen erkennbar aus der parallelen Sitzung eines anderen Projekts, und
   zuordnen laesst sich das nur ueber Rolle und Uhrzeit.
4. **Eine Regel kostet mehr, als sie einbringt, und niemand rechnet nach:** das
   120-Zeilen-Budget fuer `docs/state.md` (`commands/director.md:76` und `:113`)
   hat in Zyklus 16 **10** Umschriften ausgeloest, **5** davon ausschliesslich
   fuer das Budget (`bc460d6`, `207257a`, `98d9740`, `732ee4c`, `93b01e9`),
   zusammen 278 hinzugefuegte und 263 entfernte Zeilen an einer Datei von 142
   Zeilen — **die das Budget am Ende trotzdem um 22 Zeilen ueberschreitet.**

**Ursache (ein Satz):** Regeln werden hinzugefuegt, wenn etwas schiefgeht, aber
nie gestrichen, nie an eine Stelle im Ablauf gebunden und nie auf ihre Kosten
nachgerechnet — deshalb waechst der Text schneller, als er gelesen wird.

**Massnahme.** Zieldatei: **`agents/_rahmen.md`**, ein neuer Abschnitt am Ende;
er richtet sich an **den, der Regeln pflegt** (Director und Nutzer), nicht an
die Rollen:

> ## Regeln pflegen
>
> **Jede neue Regel nennt ihren Ausloeser** — den Moment im Ablauf, in dem sie
> greift ("bevor du einen Befundstatus weitergibst", "vor jedem Dispatch"). Eine
> Regel ohne Ausloeser gehoert nicht in den Fliesstext, sondern in eine Vorlage,
> eine Checkliste oder einen Hook. Gemessen am 08.09.2026: dieselbe Regel wirkte
> als Fliesstext in 0 von 21 Faellen und als Hook in 4 von 4.
>
> **Wer eine Regel einfuegt, nennt die, die dafuer entfaellt** — oder begruendet
> in einem Satz, warum der Bestand wachsen muss. `commands/director.md` ist in
> sieben Tagen von 355 auf 1085 Zeilen gewachsen; die Regel, die den teuersten
> Fehler des Zyklus verhindert haette, stand seit drei Stunden darin.
>
> **Eine Regel, die Arbeit erzeugt, traegt ihre Rechnung.** Das Zeilenbudget
> fuer `docs/state.md` hat in einem Zyklus fuenf Umschriften erzeugt und wurde
> am Ende trotzdem gerissen. **Es wird deshalb nur noch am Zyklusende
> geprueft** — der Satz in `commands/director.md:76` und `:113` heisst ab jetzt
> "hoechstens 120 Zeilen, **geprueft einmal am Zyklusende**".

**Wer liest das wann:** `_rahmen.md` liest jede Rolle zu Beginn jedes Laufs
(erzwungen durch `hooks/selftest.ps1`); der Abschnitt richtet sich an den, der
gerade eine Regel schreibt — und das ist genau der Moment, in dem er die Datei
offen hat.

**Kosten.** Ein Satz Begruendung je neuer Regel. Ehrliches Risiko: der Abschnitt
ist selbst eine Regel im Fliesstext und teilt damit die Schwaeche, die er
beschreibt — er wirkt nur, wenn der Nutzer ihn beim Freigeben von Regeln
anwendet. Deshalb steht die messbare Haelfte (Zeilenbudget) als konkrete
Textaenderung darin.

**Erfolgskriterium.** Am Ende von Zyklus 17 ist `commands/director.md`
**nicht laenger** als heute (1085 Zeilen), und `docs/state.md` wird hoechstens
**dreimal** je Zyklus committet.

**Status:** **angenommen und umgesetzt am 08.09.2026** (Nutzer)

---

### L-018 — Vier Nummernraeume, ein Praefix: L-Zitate nennen ihre Herkunft nicht

**Belege:** In `claude-agent-team` werden heute L-Nummern aus **vier**
verschiedenen Saetzen zitiert: teamweit L-001 bis L-013 (Rollendefinitionen),
`bt-codec L-005` (`commands/director.md:562`, mit Praefix), **`L-022` bis
`L-026` ohne jedes Praefix** in drei Hook-Kommentaren
(`hooks/check-handoff.ps1:109`, `hooks/limit-tool-calls.ps1:90`,
`hooks/selftest.ps1:376` — sie meinen die `docs/lessons.md` eines anderen
Projekts, erkennbar nur an "T-112"), und projekteigen NH-001/NH-002 hier. Die am
05.09. beschlossene Massnahme (**NH-** fuer projekteigene Regeln) hat **eine**
Seite der Kollision geschlossen: die Nightreign-Nummern werden nicht mehr
verwechselt. Die andere Seite ist offen — ein `L-022` in einem teamweiten Hook
zeigt auf eine Datei, die in diesem Projekt nicht existiert.

**Ursache (ein Satz):** Praefixe wurden pro Projekt eingefuehrt, aber nicht fuer
**Zitate** verlangt, und die teamweiten Dateien zitieren am haeufigsten fremd.

**Massnahme.** Zieldatei: **`agents/_rahmen.md`**, im Abschnitt "Regeln pflegen"
aus L-017, ein Spiegelstrich:

> **Ein L-Zitat ohne Praefix meint den teamweiten Satz** (Rollendefinitionen und
> diese Datei). Jede projekteigene Regel traegt ein Projekt-Praefix (`NH-001`),
> und wer eine fremde Projektregel zitiert, nennt das Projekt davor
> (`bt-codec L-005`). Ein `L-###` ohne Praefix in einer teamweiten Datei, das im
> teamweiten Satz nicht existiert, ist ein Fehler.

Dazu drei Ein-Zeilen-Korrekturen: `L-022` bzw. `L-022 bis L-026` in den drei
genannten Hook-Kommentaren um ihr Projekt-Praefix ergaenzen.

**Wer liest das wann:** jede Rolle liest `_rahmen.md`; entscheidend ist aber
der, der eine Regel zitiert — und das ist derselbe Moment wie bei L-017.

**Kosten.** Drei Kommentarzeilen, ein Spiegelstrich. Praktisch null.

**Erfolgskriterium.** In zwei Zyklen enthaelt kein teamweiter Text ein `L-###`
ohne Praefix, das im teamweiten Satz nicht existiert (pruefbar mit einem `grep`
ueber `claude-agent-team`).

**Status:** **angenommen und umgesetzt am 08.09.2026** (Nutzer)

---

### Beobachtungen (noch kein Muster)

- **Pruefung 2 (Werkzeug) ist zum vierten Mal ausgefallen, diesmal ohne
  Schaden (08.09.2026).** T-113 hatte kein GUI-Automatisierungswerkzeug und hat
  Speicherzustaende in der Registry nachgebildet, statt zu klicken — offen
  berichtet, mit einem eigenen Abschnitt "Wo ich nicht klicken konnte". Die drei
  frueheren Faelle (T-054, T-061, 06.09.) betrafen den `power-user` und haben je
  einen Lauf gekostet; dieser nicht. **Keine eigene Massnahme, weil die Regel
  bereits existiert und nur nicht ausgefuehrt wurde — das ist L-014.** Wird beim
  naechsten Vorkommen mit Laufverlust zu einem eigenen Muster.
- **Der Netzabbruch war billig, die unvollstaendige Isolierung war es nicht
  (07./08.09.2026, einmalig).** Der erste T-113-Lauf starb nach dem 600-s-Limit
  des Stream-Waechters; der Director hat **vor** dem Wiederanlauf am
  Dateisystem geprueft (kein Bericht, `git status` sauber, Zeitstempel der
  echten Nutzerdaten unveraendert) — vorbildlich, und genau die
  Primaerquellenpruefung, die an anderer Stelle fehlte. Verloren ging nur der
  Lauf selbst; teuer war nicht der Abbruch, sondern die fehlende dritte
  Umlenkung, die er hinterliess. Was ihn haette verkleinern koennen, ist
  inzwischen beschlossen: der feste Testabzug (E-1) spart 107 s bis 5 min je
  Artefaktstart. **Die Zahl ist noch nicht gemessen** — der erste Auftrag, der
  ihn benutzt, traegt sie nach.
- **Die Protokolle unter `~/.claude/state/` tragen kein Projekt (08.09.2026).**
  Eine Wirkungskontrolle je Projekt und Zyklus laesst sich daraus nur ueber
  Rolle und Uhrzeit rekonstruieren, und bei parallel laufenden Sitzungen ist das
  Raten. Billig zu beheben (ein Feld je Zeile), aber es ist kein Muster, sondern
  eine fehlende Messmoeglichkeit — hier festgehalten, damit die naechste
  Retrospektive es nicht wieder von Hand rekonstruiert.
- **`CHANGELOG.md` existiert nicht** (T-113, git-weite Suche, kein Treffer),
  obwohl `commands/director.md:50` sie als Ergebnis des `release-manager`
  fuehrt. Erstes Vorkommen, gemeldet an den Director, keine Massnahme.


---

## Nachtrag 08.09.2026 — die Umsetzung und ihr erster Selbstwiderspruch

**Alle fuenf Massnahmen sind umgesetzt.** L-016 im Projekt (`CLAUDE.md`,
QA-198-Ueberschrift, Kopf des T-115-Berichts). L-014, L-015, L-017 und L-018
im Agenten-Repo, Commit `486ac4e`: `hooks/remind-rules.ps1` (durch Ausfuehren
geprueft, 140 Woerter statt 50), `commands/director.md` Pruefung 4,
`agents/_rahmen.md` neuer Abschnitt "Regeln pflegen", drei Hook-Kommentare.
`hooks/selftest.ps1` gruen.

**Und L-017 ist im selben Arbeitsschritt gerissen.** Sein Erfolgskriterium
lautet: *"Am Ende von Zyklus 17 ist `commands/director.md` nicht laenger als
heute (1085 Zeilen)."* Die Umsetzung von L-015 hat die Datei auf **1097**
gebracht — zwoelf Zeilen mehr, eingefuegt vom Director, der die Regel im selben
Commit angenommen hat.

Das ist kein Argument gegen L-017, sondern sein erster Beleg: der Bestand
waechst, **auch wenn man gerade beschlossen hat, dass er das nicht soll.**
L-017 verlangt in diesem Fall einen Satz Begruendung, und hier ist er:
**L-015 ersetzt nichts, sie schaerft Pruefung 4 an der Stelle, an der die
Aussage teuer wird.** Die zwoelf Zeilen sind damit belegt, aber nicht getilgt —
**in Zyklus 17 sind zwoelf Zeilen an anderer Stelle zu streichen**, sonst ist
das Erfolgskriterium von L-017 verfehlt, bevor es geprueft wird.

---

## Zyklus 20 — 2026-09-12

**Ziel des Zyklus:** die dritte Zielrichtung sichtbar bauen (A17), die
Pruefphase darauf fahren, und den Ueberbau-Audit in drei Koerben abarbeiten.

**Datengrundlage:** die Berichte T-196 bis T-208 (**12** auf Platte; zu T-205
liegt keiner, siehe unten), die **13** Auftragsdateien dazu, `qa/findings.md`
(QA-228 bis QA-243), `security/findings.md` (SEC-036 bis SEC-042),
`DESIGN_REVIEW.md` (DR-019 bis DR-021), `docs/plan-restarbeiten.md` (P10,
Korb 1/2, Bilanzabschnitte), `docs/state.md`, `CLAUDE.md` **von der Platte**
(nicht die Fassung im Kontext — siehe Beobachtungen), `GOAL.md`,
`docs/lessons.md` L-001 bis L-018, `git log` beider Repositorien,
`~/.claude/agents/*.md`, `~/.claude/commands/director.md`,
`~/.claude/hooks/*.ps1` und `~/.claude/settings.json`.

**Stand, gegen den ich gemessen habe:** `98cdf61`. `docs/state.md` ist waehrend
dieses Laufs zweimal fortgeschrieben worden (`7c3a260` → `98cdf61`); zwei meiner
Zwischenbefunde sind dadurch erledigt und stehen als solche unten.

**Nummernraum:** L-019 und L-020 sind als **teamweite** Nummern vergeben —
beide sind im teamweiten Satz frei (dort endet er bei L-013). **NH-003** ist
projekteigen und gehoert nach `docs/plan-restarbeiten.md`. Die projekteigene
Reihe dieser Datei endet weiter bei L-018 und wird nicht fortgeschrieben
(NH-Beschluss vom 05.09.).

### Gut gelaufen (schuetzenswert)

- **Vier sachliche Korrekturen des Directors, alle vier richtig, alle vier
  angenommen.** T-197 (`grep` gezaehlt: 15 Treffer, davon **zehn**
  `pytest.raises(ValueError)`; die Director-Aufstellung hatte Zeile 277/283
  uebersehen), T-204 (`StrEnum` am Zirkelimport: `goals.py:56` macht
  `from . import types`, also kann `types.py` die Registry nicht lesen),
  T-202 F6 (die SEC-036-Notiz behauptete einen Angreifer, den die Messung
  nicht stuetzt), T-207 (die `UI_SPEC.md`-Zahl 1136 px war eine Schaetzung,
  gemessen 1121). **Der Director hat in allen vier Faellen die Lesart der
  Rolle uebernommen** und das in `plan-restarbeiten.md` und den Befunden
  vermerkt, statt sie zu glaetten. Bei der Prosaregel schreibt er es
  ausdruecklich hin: *"Mein Wortlaut war zu grob, nicht seine Umsetzung."*
- **T-199 hat die L-009-Falle selbst gefangen, ohne dass der Auftrag sie
  nannte.** Erster Lauf offscreen: 278/271/278 px und `wanted_height` 1203.
  Zweiter Lauf nativ: 228 px, Vorgabe exakt getroffen. Im Bericht steht der
  Satz, auf den es ankommt: *"Ohne diese Gegenprobe haette ich eine falsche
  Zahl gemeldet."* Dazu die Umgebungszeile (`platform 'windows'`, Fusion,
  dPR 1,25, logische px).
- **T-196 hat einen strukturell unmoeglichen Nachweis als unmoeglich
  gemeldet** — `STATUS: teilweise`, `BLOCKIERT DURCH: eine Bestaetigung, dass
  der kopierte Abzug am realen Zielpfad tatsaechlich lesbar ist — meine Tools
  koennen das nicht zeigen`, dazu ein eigener Abschnitt, der die Grenze
  eingekreist hat (jeder Leseversuch scheitert, auch auf einer selbst
  angelegten Testdatei, nicht im Scratchpad). Daraus wurde QA-237.
- **T-203 hat einen Fehler in seiner eigenen ersten Fassung gefunden** (ein
  Anker auf Zeilenanfang liess `VAR=x VAR2=y python run.py` durch) und die
  Werkzeuggrenze seines Waechters gemeldet (QA-241) statt zu behaupten, er
  laufe.
- **T-206 hat die groesste Behauptung des Audits gemessen und gegen sie
  entschieden** — 20 von 1427 Prosazeilen (1,4 %), mit Positivkontrolle, und
  die Empfehlung, die restlichen 17 Dateien nicht anzufassen.
- **Die Pruefung zwischen Freigabe und Loeschbefehl.** 35 154 Zeilen waren
  freigegeben; die Pruefung der lebenden Verweise kam **danach** und hat die
  Praemisse widerlegt. Nichts wurde geloescht.
- **Der Director fuehrt seine eigenen Fehler in `docs/state.md`** und hat die
  Liste noch waehrend dieses Laufs von fuenf auf sechs erweitert. Ohne diesen
  Abschnitt waere der Lauf nicht moeglich. Das war schon in Zyklus 16 die
  schuetzenswerteste Gewohnheit und ist es weiter.

### Was ich der Aufzaehlung des Auftrags widerspreche

Der Auftrag hat sieben Beobachtungen als Material uebergeben und ausdruecklich
verlangt, sie gegen die Quellen zu pruefen. Fuenf halten, zwei tragen nicht:

1. **Beobachtung 3 ist als Beleg wertlos — nicht falsch, sondern ohne
   Kontrast.** Der Satz *"Widersprich, wenn der Auftrag nicht stimmt"* steht in
   **12 von 12** damals vorhandenen Auftragsdateien des Zyklus (`grep -ci`, je
   Datei einzeln) und seit T-180 in **30 von 30** aufeinanderfolgenden
   Auftraegen. Es gibt im Zyklus keinen Fall ohne den Satz. "In allen vier
   Faellen stand er im Auftrag" gilt damit genauso fuer die acht Faelle **ohne**
   Korrektur und trennt nichts. Gegenprobe nach unten: die Strecke T-140 bis
   T-179 traegt den Satz in 4 von 40 Dateien, und aus ihr liegen mehrere
   Berichte vor, die dem Auftrag widersprechen — die Klasse ist aelter als der
   Satz. **Der Satz bleibt, weil er eine Zeile kostet; Ursache ist er nicht.**
   Die vier Korrekturen kamen aus vier *Messpflichten* der Rollendefinitionen:
   nachzaehlen (T-197), an der Primaerquelle lesen (T-204), den Angriffspfad
   messen (T-202), am Fenster nachmessen (T-207). Alle vier binden die Rolle
   unabhaengig vom Auftragstext. **Und genau diese vier Pflichten binden den
   Director nicht** — das ist L-013s Wirkungskontrolle vom 08.09., woertlich
   wiederholt, und es ist der Kern von L-019.
2. **Beobachtung 6 trifft nicht zu.** "Derselbe Sachverhalt, zwei
   entgegengesetzte Reaktionen" — die Berichte sagen das Gegenteil. T-196 hat
   den Rueckleseversuch **nicht** als Nachweis gemeldet: `STATUS: teilweise`,
   `BLOCKIERT DURCH` nennt genau die fehlende Bestaetigung, und ein eigener
   Abschnitt *"Offener Punkt, nicht geloest"* grenzt die Ursache ein. T-203 hat
   es genauso gemacht. **Beide Rollen haben gleich und richtig reagiert; die
   Asymmetrie steht im Befundtext**, nicht in den Laeufen: QA-237 schreibt
   *"T-196 hat … den Abzug zurueckgelesen … und genau das hat T-196 als
   Nachweis gemeldet"*, und das widerspricht T-196s Bericht. Die Frage "woran
   lag der Unterschied" hat keine Antwort, weil es den Unterschied nicht gibt.

Dazu zwei Praezisierungen, die die Beobachtungen nicht umstossen:

- **Beobachtung 1: die Zahl 120 000 traegt kein Rezept und mischt zwei
  Grundgesamtheiten.** Sie kommt im ganzen Repo nur an drei Stellen vor
  (`docs/state.md:29`, `docs/plan-restarbeiten.md:564`, `docs/tasks/T-209.md`)
  und nirgends mit Herleitung; die gemessene Ausgangslage in P10 nennt 23 916
  Quellzeilen und 113 477 Markdown-Zeilen. Die Schlagzeile "-37 gegen 120 000"
  stellt **Quellzeilen** gegen ueberwiegend **Markdown**zeilen. Alles
  Inhaltliche der Beobachtung haelt (drei widerlegte Punkte, 1,4 %, zwei
  bestaetigte Strukturbefunde, QA-234 als Selbstbeleg) — nur die
  Verhaeltniszahl nicht.
- **Beobachtung 7: L-009 ist nicht "aufgelaufen", L-009 hat gegriffen.** Die
  *Falle* trat wieder auf (`scripts/measure_picker_cards.py:60` setzt
  `QT_QPA_PLATFORM=offscreen` als Vorgabe), der *Fehler* nicht — keine falsche
  Zahl hat einen Bericht verlassen. Der Auftrag war daran unbeteiligt: T-199
  nennt L-009 dreimal im Bericht, waehrend `docs/tasks/T-199.md` sie **null**
  Mal nennt; L-009 steht in `agents/developer.md:356`. Auch die zweite Haelfte
  traegt nicht: L-009 erscheint in **2 von 12** Auftragsdateien des Zyklus
  (T-201, T-207), nicht "ab T-201 in jedem".

### Wirkungskontrolle frueherer Massnahmen

| ID | Massnahme | Uebernommen am | Wirkung | Konsequenz |
|---|---|---|---|---|
| **L-009** (teamweit) — jede Oberflaechenzahl nennt ihre Messumgebung | 2026-09-06 (Rollendefinitionen), Projektfassung in `plan-restarbeiten.md` | **Wirkt, und zwar dort, wo eine Regel es am schwersten hat: ohne Erinnerung im Auftrag.** T-199 hat die Offscreen-Falle selbst erkannt, gegengemessen und die Umgebungszeile geliefert, obwohl sein Auftrag L-009 nicht nennt. T-201 hat die Fremdmessung genau deshalb als Stichprobe akzeptiert, weil die Umgebung dabeistand. **Die mechanische Haelfte hat aber ein Loch:** T-060 hat `tests/conftest.py` an `apply_appearance` gebunden, nicht die Messskripte — **fuenf** Dateien setzen `QT_QPA_PLATFORM=offscreen` als Vorgabe (`scripts/measure_picker_cards.py:60`, `measure_display_thresholds.py:53`, `measure_advisor_block.py:287`, `capture_weapon_damage.py:33`, `differential/capture.py:77`), drei davon messen Geometrie. `measure_picker_cards.py` ruft `apply_appearance` **und** laeuft offscreen: Stil geschlossen, Plattform offen. | **Kein neuer Regeltext.** Ein Punkt fuer den `developer`, Einordnung beim `director`: die drei Geometriemesser nennen ihre Plattform in jeder Ausgabezeile oder weigern sich unter `offscreen`. Der **Status "vorgeschlagen"** in dieser Datei ist falsch — die Regel steht seit dem 06.09. in fuenf Rollendefinitionen und in `plan-restarbeiten.md` und ist in Kraft. |
| **L-016** (Projekt) — eine Korrektur schliesst die Fundstelle, nicht die Aussage | 2026-09-08 | **Beide Textaenderungen sind umgesetzt, und das Erfolgskriterium ist dennoch verfehlt — durch die Korrekturen selbst.** Umgesetzt: die QA-198-Ueberschrift heisst heute *"dauert unvorhersagbar lange (107 s bis 5 min)"* (`qa/verlauf.md:1932`); der `CLAUDE.md`-Absatz ist ersetzt. **Verfehlt, vier Vorkommen in vier Tagen:** (a) der **neue** Wortlaut aus L-016 (a) fuehrte den `qa-engineer` unter den Rollen ohne `Write` — falsch, korrigiert erst am 12.09. (`de710a5`); (b) L-018s Umsetzung gab drei Hook-Kommentaren das Praefix `Nightreign-Helper`, obwohl `L-022` bis `L-026` hier nicht existieren; (c) am Tag, an dem vier kaputte Tabellenzeilen repariert wurden, ist in derselben Datei eine fuenfte entstanden (QA-240, `qa/findings.md:263`); (d) `docs/tasks/T-205.md`, geschrieben um 21:30 desselben Tages, sagt *"der Bericht liegt ab"* und nennt `docs/berichte/T-205-archivist.md` — **die Datei existiert nicht** (drei unabhaengige Pruefungen: `ls`, `find docs -iname "*205*"`, `git log --all -- "docs/berichte/T-205*"`, dazu eine Volltextsuche: `T-205` kommt nur in `docs/state.md` und den zwei Auftragsdateien vor). | **Nicht zurueckgenommen** — die Textaenderungen waren richtig. Die Klasse braucht statt weiteren Regeltexts einen Adressaten: → **L-019** (`CLAUDE.md` in den Wachbereich von `require-receipt.ps1`, und den Hook ueberhaupt registrieren) und → **NH-003** (Spaltenwaechter). |
| **L-008** (teamweit) — ein Gegenbau muss beissen | 2026-09-06 | **Wirkt nicht durchgaengig.** In Zyklus 16 war die Bilanz 1 von 1. In Zyklus 20 hat T-202 einen Waechter gemessen, der die Stelle, die er bewacht, **wegstubbt**: SEC-038, `tests/test_game_dir_recognition.py:143-156`, `monkeypatch.setattr` auf `_steam_roots`, **5 von 5** Fundstellen, waehrend der echte Koerper 26-mal lief. Gefunden hat es der `security-reviewer`, nicht der Mutationslauf. | Keine eigene Massnahme. L-008 (b) verbietet die Erwartung aus der bewachten Stelle; "die bewachte Stelle wegstubben" ist derselbe Mechanismus und vom Wortlaut gedeckt — der Fall ist ein Ausfuehrungs-, kein Formulierungsproblem. **Ein zweites Vorkommen waere ein Muster.** |
| **L-011** (teamweit) — "richtiger als ihre Begruendung", bewusst ohne Massnahme, mit Ausloeser | Ausloeser stand seit 2026-09-06 | **Der Ausloeser ist eingetreten.** Er lautete: *"ein Fall, in dem eine falsche Begruendung eine Entscheidung bis zum Ende traegt — … sondern in einem umgesetzten Fix, einer freigegebenen Spec oder einer **Nutzerentscheidung** landet."* Genau das ist Beobachtung 2: die Loeschfreigabe des Nutzers fuer 35 154 Zeilen stand auf der Audit-Praemisse *"Vollkopien, deren Vorfassungen git ohnehin haelt"*, und die war falsch — `UI_SPEC.md:239-241`, `:1017-1019`, `:881-883` und sieben weitere Stellen sagen woertlich, dass der geltende Wortlaut **nur** im Verlauf steht. Die Freigabe war erteilt; gerettet hat es eine Pruefung **danach**. In Zyklus 16 war die Bilanz noch "kein neuer Fall dieser Bauform". | **Die von L-011 vorab benannte Massnahme wird faellig** — und sie existiert bereits gebaut: `require-receipt.ps1` verlangt fuer eine Bestandsbehauptung eine genannte Quittung. Sie ist **nicht registriert** (→ **L-019**). Grenze, die ich ausdruecklich nenne: der Hook bewacht `Write`/`Edit`, die teuerste Aussage des Zyklus reiste als **Nachricht an den Nutzer** — dafuer deckt L-019 nichts, und ich schlage dafuer auch nichts vor (Begruendung unter L-020, Absatz "Was ich nicht vorschlage"). |
| **L-015** (teamweit) — `docs/state.md` ist Primaerquelle jeder Rolle (Pruefung 4) | 2026-09-08 | **Wirkt genau so weit, wie der Auftrag es sagt, und nicht weiter.** Gezaehlt an den `GELESEN`-Zeilen der 12 Berichte: `docs/state.md` in **5**, `GOAL.md` in **3**, `CLAUDE.md` in **5** von 12. Die Korrelation zum Auftragstext ist fast vollstaendig: von den 6 Auftraegen, die `state.md` nennen, nennen 5 Berichte sie; von den 5, die sie nicht nennen, nennt **kein** Bericht sie — 11 von 12. | → als Befund in **L-020** aufgenommen, **und die naheliegende Massnahme dort ausdruecklich verworfen**. |
| **L-017** (teamweit) — der Regelbestand waechst monoton | 2026-09-08 | **Wirkt.** Erfolgskriterium: `commands/director.md` am Ende von Zyklus 17 nicht laenger als 1085 Zeilen; am Tag der Annahme stand sie auf 1097. Heute: **901** Zeilen (`wc -l`). Die zwoelf Zeilen sind getilgt und 196 weitere dazu. | Keine. Gilt als erfuellt. |
| **L-018** (teamweit) — L-Zitate nennen ihre Herkunft | 2026-09-08 | **Formal umgesetzt, sachlich halb falsch.** Der Spiegelstrich steht in `agents/_rahmen.md:347-351`. Die drei Hook-Kommentare tragen jetzt ein Praefix — aber **`Nightreign-Helper`**, und in diesem Projekt existieren `L-022` bis `L-026` nicht: diese Datei endet bei L-018, und `T-112` ist hier `T-112-technical-writer.md`, keine `retrospective`. Das Erfolgskriterium ("kein `L-###` ohne Praefix, das im teamweiten Satz nicht existiert") ist wortwoertlich erfuellt und in der Sache verfehlt — jetzt zeigt ein Praefix auf eine Datei, in der die Nummer fehlt. | Eine Ein-Zeilen-Korrektur, kein Regeltext: das Projekt ermitteln, dessen `T-112` eine `retrospective` war, und die drei Kommentare darauf umschreiben. Gehoert dem Nutzer, weil es das Agenten-Repo beruehrt. |
| **NH-001** — je nicht-trivialem Auftrag eine Datei | 2026-09-06 | **In Zyklus 20 zweimal gebrochen, beide vom Director, beide selbst gemeldet und nachgetragen** (T-205 und T-208, je `archivist`/`sync-out`, Nummer im Dispatch verwendet, Datei nicht angelegt; nachgetragen um 21:30 in `98cdf61`). In Zyklus 13 ebenfalls zweimal, in Zyklus 16 lueckenlos. **Beide Brueche treffen dieselbe Sorte Auftrag** — Arbeit zwischen zwei Auftraegen, ohne Rollenwechsel. | Keine neue Regel: der Ausloeser ist bekannt, die Regel ist bekannt, und der Nachtrag hat funktioniert. **Aber der T-205-Bericht ist dabei verlorengegangen** (siehe L-016 (d) oben) — das ist die Kosten dieses Bruchs und gehoert in die Beobachtungsliste. |
| **NH-002** — Bildnachweise nur aus dem Programmfenster | 2026-09-05 | **Wirkt.** T-207 legt zwei Nachweise ab und nennt beide ausdruecklich als aus dem Programmfenster gezogen (`design-review/2026-09-12/relicpicker-forced-wanted-height-1151.png`, `-natural-height-1061.png`). | Keine. |

**Bilanz: von neun geprueften Massnahmen wirken vier unverkuerzt (L-009,
L-017, NH-002, und L-015 im Rahmen dessen, was sie ueberhaupt binden kann);
zwei wirken an der Fundstelle und nicht an der Klasse (L-016, L-018); zwei
wirken nicht durchgaengig (L-008, NH-001); eine hat ihren Ausloeser erreicht
und wird faellig (L-011).**

---

### L-019 — Die Waechter dieses Teams sind gebaut, geprueft und zum Teil nicht angeschlossen

**Belege (jeder einzeln am Bestand geprueft, 12.09.2026):**

1. **Drei Hooks liegen als Datei in `~/.claude/hooks/`, werden von
   `hooks/selftest.ps1` geprueft und stehen in keiner Registrierung:**
   `require-receipt.ps1`, `no-root-find.ps1`, `remind-sync-out.ps1`. Nachweis
   mit zwei unabhaengigen Verfahren: (a) `settings.json` nach JSON geparst und
   alle `hooks[*].hooks[*].command` aufgelistet — neun Eintraege, keiner der
   drei; (b) `grep -o` auf die drei Dateinamen in `settings.json` **und**
   `settings.json.bak-bootstrap` — kein Treffer. Die
   Projekt-`.claude/settings.json` registriert ausschliesslich
   `enforce-data-redirect.ps1`. Kein anderer Hook ruft die drei auf.
2. **Einer der drei ist in der Director-Definition als vorhanden ausgewiesen.**
   Die Ort-Tabelle (`commands/director.md:890 ff.`) fuehrt unter "Hook" den
   *"`sync-out`-Zaehler"* als Beispiel — das ist `remind-sync-out.ps1`.
3. **`selftest.ps1` bleibt gruen, weil er die falsche Frage stellt.** Er prueft
   je Hook die *Existenz* der Datei und das *Verhalten* ueber `stdin`
   (`HookAntwort`, ab Zeile 448: vier Faelle fuer `require-receipt`, drei fuer
   `no-root-find`). **Eine Registrierungspruefung gibt es nicht.** Der
   Selbsttest nennt die Luecke seit dem 08.09. in seinem eigenen Kommentar
   (Zeile 376: *"dieselbe Luecke wie bei den Hooks selbst … die Werkzeugschicht
   hat kein Register"*) — und schliesst sie fuer das Frontmatter der Rollen,
   nicht fuer die Registrierung der Hooks.
4. **Der Ort, der einen Hook wirksam macht, ist nicht versioniert.** Die Hooks
   liegen im Repo `claude-agent-team` und werden per Junction sichtbar;
   `~/.claude/settings.json` liegt **nicht** in diesem Repo (Wurzel:
   `BOOTSTRAP.md`, `CLAUDE.md`, `README.md`, `agents`, `archiv`,
   `bootstrap.ps1`, `commands`, `hooks`, `referenz`, `templates` — keine
   `settings*.json`). "Waechter gebaut" ist damit in der Git-Historie sichtbar,
   "Waechter feuert" nicht.
5. **Der inaktive Hook ist genau der gegen die Fehlerklasse dieses Zyklus.**
   `require-receipt.ps1` sperrt `Write`/`Edit` der Hauptsitzung auf
   Auftragsdateien, `docs/state.md` und Befundlisten, wenn eine
   Bestandsbehauptung ohne genannte Quittung hineingeschrieben wird — sein
   Kopf sagt: *"Ein Hook, der ERINNERT, ist Fliesstext mit hoeherer Frequenz.
   Dieser hier SPERRT."* Die **sechs** Eigenfehler aus `docs/state.md` sind
   alle von dieser Bauform, und der sechste ist waehrend dieses Laufs
   dazugekommen: eine Praemisse ohne Pruefung (Korb 2), eine Suche nach Status
   statt nach Inhalt (QA-235), zwei Strukturdefekte beim Schreiben in
   `qa/findings.md`, eine Budgetangabe ohne Zaehlung, zwei Dispatches ohne
   Auftragsdatei. Dazu `docs/tasks/T-205.md`: *"der Bericht liegt ab"* fuer eine
   Datei, die es nicht gibt — **ein `Write` in eine Auftragsdatei mit
   Bestandsbehauptung ohne Quittung, also genau der Fall, auf den der Hook
   `deny` antwortet.**

**Ursache (ein Satz):** Eine Massnahme dieses Teams gilt als umgesetzt, wenn
die Datei existiert und ihr Selbsttest gruen ist — und die Registrierung, die
sie ueberhaupt erst ausloest, ist weder versioniert noch geprueft.

**Massnahme.** Zieldatei **`hooks/selftest.ps1`** im Agenten-Repo, neuer
Abschnitt am Ende, dazu **eine Pfadangabe** in `require-receipt.ps1`:

> ```powershell
> # --- Registrierung: ein Hook, den niemand aufruft, ist kein Waechter -------
> # Herkunft: Nightreign-Helper Zyklus 20. require-receipt.ps1, no-root-find.ps1
> # und remind-sync-out.ps1 waren gebaut, hier geprueft und in settings.json
> # nicht eingetragen - einer davon ist der Waechter gegen die Fehlerklasse, die
> # im selben Zyklus sechsmal aufgetreten ist. settings.json liegt nicht im
> # Repo; genau deshalb faellt es in der Historie nicht auf.
> $OFFEN = @()   # darf nur schrumpfen. Jeder Eintrag nennt seinen Grund.
> $reg = Get-Content -Raw -LiteralPath (Join-Path $HOME '.claude/settings.json')
> foreach ($f in Get-ChildItem -LiteralPath $hooks -Filter '*.ps1' -File) {
>     if ($f.Name -in @('selftest.ps1')) { continue }
>     $drin = $reg -match [regex]::Escape($f.Name)
>     Check "$($f.Name) ist in settings.json registriert" `
>           ($drin -or ($f.Name -in $OFFEN)) `
>           'nicht registriert - der Hook existiert, feuert aber nie'
> }
> ```
>
> Und in `require-receipt.ps1` nimmt die Pfadpruefung zusaetzlich `CLAUDE.md`
> auf. Grund: zwei der vier L-016-Wiederholungen sind beim Schreiben in
> `CLAUDE.md` entstanden, und der Selbsttest haelt heute ausdruecklich fest,
> dass `README.md` **nicht** bewacht wird — `CLAUDE.md` ist keine `README`,
> sondern der Regeltext, den jede Rolle in jedem Auftrag zitiert bekommt.

**Wer liest das wann:** niemand *liest* es — `selftest.ps1` laeuft, und er ist
die Abnahme jeder Aenderung am Agenten-Repo. Das ist der Punkt: die Massnahme
haengt an keinem Vorsatz und an keinem Moment, den ein Mensch verpassen kann.

**Ort nach der Tabelle der Director-Definition:** **Hook** (bzw. der
Pruefcode, der Hooks abnimmt). Ausdruecklich **nicht** Fliesstext: die Zahl
0 von 21 gegen 4 von 4 ist der Grund, warum dieser Befund ueberhaupt zaehlt.

**Welche Regel entfaellt dafuer:** keine, und der Bestand waechst um **null
Zeilen Regeltext** — L-019 ist ausschliesslich Pruefcode plus eine Pfadangabe.
Das ist die Bauform, die `agents/_rahmen.md` fuer das zweite Auftreten einer
Fehlerklasse verlangt ("einen Waechter, keinen weiteren Regeltext").

**Kosten.** Ein Lesezugriff je Selbsttestlauf. Ein Risiko: der Selbsttest wird
rot, sobald ein Hook absichtlich unregistriert liegen soll — dafuer ist die
`OFFEN`-Liste da, und sie kostet eine Zeile mit Grund. **Ein zweites Risiko,
das ich benennen muss:** `require-receipt.ps1` sperrt. Wird er scharf
geschaltet, kann er den Director an einer Stelle aufhalten, an der seine
Aussage richtig und die Quittung nur nicht mitgeschrieben ist. Das ist der
Preis, und er ist gegen sechs Eigenfehler in einem Zyklus zu rechnen.

**Erfolgskriterium.** In zwei Zyklen: `selftest.ps1` laeuft gruen **und**
`settings.json` nennt jeden Hook ausser den in `OFFEN` begruendeten; die
`OFFEN`-Liste ist nicht gewachsen. Zweitens, inhaltlich: mindestens ein `deny`
von `require-receipt.ps1` ist belegt — feuert er in zwei Zyklen nie, ist
entweder die Klasse weg oder der Hook trifft nicht, und beides gehoert
gemessen statt angenommen.

**Status:** vorgeschlagen — **teamweit, Vorschlag fuer das Agenten-Repo**
(`hooks/selftest.ps1`, `hooks/require-receipt.ps1`, `~/.claude/settings.json`).
Freigabe nur durch den Nutzer.

---

### L-020 — Das Zeilenbudget von `docs/state.md` ist ein Vorsatz, und Vorsaetze verlieren gegen Commits

**Belege — gezaehlt mit `git show <commit>:docs/state.md | wc -l` ueber die
letzten zwanzig Commits an der Datei:**

| Commit | Datum | Zeilen | Botschaft |
|---|---|---|---|
| `1e3a955` | 09.09. | **132** | "Zyklus 18 abgeschlossen, Verlauf archiviert, **auf Budget**" |
| `5f15b7d` | 09.09. | **131** | "auf 120 Zeilen gekuerzt — der vorige Commit nannte 132 'auf Budget'" |
| `405a4ee` | 12.09. | **125** | "Zyklus 19 abgeschlossen, Verlauf archiviert, **auf Budget**" |
| `5a2d280` | 12.09. | **122** | "auf 120 Zeilen gebracht — der vorige Commit nannte 125 'auf Budget'" |
| `2f91ad6` | 12.09. | **120** | "120 Zeilen, **diesmal vor dem Commit gezaehlt**" |
| `8ed62de` | 12.09. | **149** | "Pruefphase durch, Korb 2 zurueckgezogen, vier eigene Fehler" |
| `de420b6` | 12.09. | **120** | "auf das Zeilenbudget gekuerzt — 149 auf 120" |

**Dreimal ueber Budget committet, viermal per Folgecommit nachgezogen, und zwei
der vier Korrekturen waren selbst falsch:** `5f15b7d` sagt "auf 120" und ist
**131**, `5a2d280` sagt "auf 120" und ist **122**. Genau **einmal** wurde
vorher gezaehlt, und dieser Commit sagt es ausdruecklich. Dazu der aeltere
Beleg, der schon in `agents/_rahmen.md` steht: *"Das Zeilenbudget fuer
`docs/state.md` hat in einem Zyklus fuenf Umschriften erzeugt und wurde am Ende
trotzdem gerissen."*

**Und die Massnahme, die daraus entstand, hat es nicht behoben.** Die
Konsequenz damals war "**nur noch am Zyklusende geprueft**"
(`commands/director.md:71`). Danach sind die drei Faelle oben passiert — die
Lockerung hat die Nacharbeit nicht verkleinert, sondern den Moment der Pruefung
hinter den Commit verschoben. **Das Budget selbst ist nicht das Problem:** es
hat die Datei von 337 Zeilen (`b1a2776`, 09.09.) auf 120 gebracht, und das ist
seine Rechtfertigung. Falsch ist nur sein Ausloeser.

**Ursache (ein Satz):** Die Pruefung haengt an einem Zeitpunkt ("Zyklusende"),
den in einem durchgehenden autonomen Lauf niemand erkennt — waehrend der
Commit ein Moment ist, der immer eintritt.

**Massnahme.** Ein Waechter am Schreibzeitpunkt, und der Zeitpunkt verschwindet
aus der Prosa. Zieldatei **`hooks/state-line-budget.ps1`** (neu, Agenten-Repo),
registriert auf `PreToolUse` fuer `Write|Edit`:

> ```powershell
> # state-line-budget.ps1 - PreToolUse auf Write|Edit, nur Hauptsitzung.
> # Herkunft: Nightreign-Helper Zyklus 20. Das Budget stand als Prosa in
> # commands/director.md:71 ("geprueft einmal am Zyklusende") und wurde in vier
> # Tagen dreimal ueberschritten; zwei der vier Korrekturcommits nannten selbst
> # eine falsche Zahl. Eine Zahl faellt auf, ein Vorsatz nicht.
> #
> # MELDET, SPERRT NICHT. Der Inhalt kann richtig und zu lang sein - dann
> # gehoert die Kuerzung in denselben Zug, nicht in den naechsten Commit.
> # Die Schranke steht als LITERAL, nicht gerechnet aus der Datei, die sie
> # bewacht (L-008 b).
> $BUDGET = 120
> ```
>
> Wirkung: greift nur, wenn der Zielpfad auf `docs/state.md` endet; zaehlt die
> Zeilen des geschriebenen Inhalts; bei Ueberschreitung eine Zeile Ausgabe —
> `[state-budget] 149 Zeilen, Budget 120 - kuerzen in diesem Zug, nicht im
> naechsten Commit.`

**Ort nach der Tabelle der Director-Definition:** **Hook**, plus eine
Streichung in der **Director-Definition**. Der Hook ist der Adressat, die
Director-Definition behaelt nur noch die Zahl.

**Welche Regel entfaellt dafuer:** `commands/director.md:71`, der Halbsatz
*"hoechstens 120 Zeilen, **geprueft einmal am Zyklusende**"*, wird zu
*"hoechstens 120 Zeilen (`hooks/state-line-budget.ps1` zaehlt beim
Schreiben)"*. Der Zeitpunkt "Zyklusende" verschwindet aus dem Regelbestand —
er ist der Teil, der nachweislich nicht getragen hat. Die Director-Definition
wird dadurch nicht laenger, und eine Bedingung faellt weg.

**Was ich ausdruecklich *nicht* vorschlage — und warum das auch ein Ergebnis
ist.** Die naheliegende zweite Massnahme aus der L-015-Wirkungskontrolle waere
ein Hook, der `GELESEN` gegen `GOAL.md` und `docs/state.md` prueft (heute 3
bzw. 5 von 12). **Verworfen.** Ein solcher Waechter prueft ein Wort, das die
bewachte Partei selbst schreibt — dieselbe Bauform, die L-008 (b) verbietet
und die SEC-038 im selben Zyklus als zahnlos belegt hat. Er wuerde die Nennung
erzwingen und ueber das Lesen nichts sagen; danach waere "12 von 12" kein
Messwert mehr, sondern eine Formalie, und die Zahl, mit der diese
Retrospektive L-015 gemessen hat, waere zerstoert. **Der belastbare Teil des
Befundes bleibt als Beobachtung stehen:** ein Lauf arbeitet mit dem Regelsatz,
den seine **Rollendefinition** traegt — L-009 hat ohne jede Erwaehnung im
Auftrag gegriffen — plus dem, was sein **Auftrag** nennt. Dateien, die nur im
Uebergabe-Kontrakt stehen, erreichen ihn in weniger als der Haelfte der Faelle.
Wer das aendern will, aendert den Auftrag oder die Rollendefinition, nicht die
Berichtsform.

**Kosten.** Ein Hook mehr, ein Halbsatz weniger. Der Hook meldet und sperrt
nicht; ein Fehlalarm kostet eine Zeile Ausgabe.

**Erfolgskriterium.** In zwei Zyklen: kein Commit an `docs/state.md` mit mehr
als 120 Zeilen, und **kein** Commit, dessen Botschaft die Zeilenzahl des
Vorgaengers korrigiert. Beides nachzaehlbar mit `git log --oneline --
docs/state.md` und `git show <c>:docs/state.md | wc -l`, so wie hier.

**Status:** vorgeschlagen — **teamweit, Vorschlag fuer das Agenten-Repo**
(neuer Hook, `~/.claude/settings.json`, Streichung in
`commands/director.md:71`). **Reihenfolge: nach L-019.** Ein neuer Hook, der
vor der Registrierungspruefung angelegt wird, landet mit einiger
Wahrscheinlichkeit in derselben Schublade wie die drei, die dort schon liegen.

---

### NH-003 — Die Befundtabellen haben keinen Waechter, und die reparierte Klasse ist am Reparaturtag wiedergekommen

*Projekteigene Regel. Gehoert nach `docs/plan-restarbeiten.md`, Abschnitt
"Regeln, die fuer jeden Schritt gelten" — dort stehen NH-001 und NH-002, und
die Rollen lesen diese Datei fuer die Reihenfolge.*

**Belege:**

1. **Vier Zeilen waren strukturell kaputt** (QA-211, QA-225 bis QA-227:
   doppeltes Datum, fehlende Abschlusspipe, ein Status von einem Datum
   ueberschrieben), repariert am 12.09.; `docs/state.md` kannte nur drei davon.
2. **Eine fuenfte ist am selben Tag entstanden und steht heute noch da.**
   Gemessen: je Tabellenzeile die Trenner nach Entfernen der maskierten `\|`
   gezaehlt und gegen die Kopfzeile gestellt. `qa/findings.md`: Kopf **8**
   Spalten, 247 Tabellenzeilen, **eine** Abweichung — **Zeile 263 (QA-240)**,
   neun Spalten, Ursache ein unmaskiertes `|` in
   `` `git show HEAD~1:<datei> | sed -n` ``. `security/findings.md`: Kopf **5**
   Spalten, 44 Zeilen, **0** Abweichungen. **Die Konvention existierte und war
   am 02.09. korrekt benutzt** (Zeile 59 und 78 tragen `a\|b` maskiert) — sie
   ist nicht unbekannt, sie ist unbewacht.
3. **`tests/` haelt kein `.md`-Pfadliteral.** Mit zwei unabhaengig
   formulierten Masken geprueft: (a)
   `grep -rE "(read_text|open\(|Path\()[^\n]*\.md" tests/ --include=*.py` —
   **0 Treffer**; (b) `grep -rE "glob\(|rglob\(|os\.walk" tests/ --include=*.py`
   — 10 Treffer, **alle** auf `*.py`. Die 32 Erwaehnungen von `.md` in `tests/`
   stehen ausnahmslos in Docstrings und Kommentaren. **Kein Test dieses
   Projekts liest irgendeine Markdown-Datei.**

**Ursache (ein Satz):** Die beiden Befundtabellen sind die am haeufigsten
beschriebenen strukturierten Dateien des Projekts und die einzigen
strukturierten Dateien ohne Test.

**Massnahme.** Neue Datei **`tests/test_findings_tables.py`**, und ein
Spiegelstrich in `docs/plan-restarbeiten.md`, Abschnitt "Regeln, die fuer jeden
Schritt gelten":

> - **Die Befundtabellen haben einen Waechter** (NH-003): jede Zeile von
>   `qa/findings.md` und `security/findings.md`, die mit `|` beginnt, traegt
>   nach Entfernen der maskierten `\|` genau so viele Trenner wie ihre
>   Kopfzeile. Die Erwartung steht als **Literal** — 8 Spalten fuer QA, 5 fuer
>   SEC —, nicht aus dem Kopf gerechnet. Wer ein `|` in einen Befundtext
>   schreibt, maskiert es als `\|`.

Der Test traegt seine **`OFFEN`-Liste** im Code — heute genau ein Eintrag,
`qa/findings.md:263 (QA-240)` —, und ein zweiter Test besteht darauf, dass die
Liste nur schrumpfen darf. **Rot-vorher:** ohne diesen Eintrag ist der Test
heute rot an Zeile 263, und das ist sein Nachweis; die brechende Aenderung ist
das Einfuegen einer Zeile mit unmaskiertem `|`. **Er darf nicht von der
Repo-Wurzel absuchen**, sondern nimmt die zwei Pfade beim Namen — sonst liest
er Worktrees mit (`agents/_rahmen.md`, Abschnitt Messen und Testen).

**Ort nach der Tabelle der Director-Definition:** **Belegdatei/Test im
Projekt**, plus ein Spiegelstrich in `docs/plan-restarbeiten.md`. Der Test ist
der Adressat; der Spiegelstrich sagt nur, warum er existiert.

**Welche Regel entfaellt dafuer:** keine; der Bestand waechst um einen
Spiegelstrich. Begruendung in einem Satz: **es ist der erste Test dieses
Projekts, der eine Markdown-Datei ueberhaupt anfasst**, und die Alternative
waere ein weiterer Absatz gegen eine Klasse, die am Tag ihrer Reparatur
wiedergekommen ist.

**Wer liest das wann:** niemand — `pytest` laeuft in jedem Bauauftrag.

**Kosten.** Ein Test, Laufzeit unter einer Sekunde, ohne Qt und ohne Spieldaten.
Die Maskierungspflicht kostet zwei Zeichen je Befundtext mit Pipe (bisher zwei
Vorkommen in 247 Zeilen).

**Erfolgskriterium.** In zwei Zyklen: die `OFFEN`-Liste ist leer oder kleiner,
und keine Zeile ausserhalb der Liste weicht ab. Nachzaehlbar mit demselben
Verfahren, das hier 1 von 247 gefunden hat.

**Status:** vorgeschlagen — **projekteigen**. Ratifiziert die Massnahme, die
der Director in `docs/state.md` unter "Massnahme, noch ohne Auftrag" schon
beschlossen hat, und ergaenzt, was dort fehlte: den Algorithmus, die Erwartung
als Literal, den roten Fall und den Grund, warum der Waechter nicht von der
Wurzel absuchen darf.

---

### Beobachtungen (noch kein Muster)

- **Die `CLAUDE.md`, die ein Unteragent im Kontext bekommt, kann aelter sein
  als die auf der Platte (12.09.2026, erstes Vorkommen).** Meine
  Kontextfassung beschrieb den festen Testabzug unter `%LOCALAPPDATA%` als
  *"existiert nicht"* und nannte `EXTRACT_VERSION` 11 aus 1.8.0; die Datei auf
  der Platte nennt seit `f110dd4` den Pfad
  `…\Desktop\ClaudeCode\NightreignHelper-Testabzug`, 1.9.0 und die
  Bestaetigung durch den Nutzer. `git status` sauber, `HEAD:CLAUDE.md`
  159 Zeilen, identisch mit dem Arbeitsbaum. Der Auftrag sagt *"Es gelten die
  Projektzeilen aus `CLAUDE.md`"* — eine Rolle, die dafuer die Kontextfassung
  nimmt, arbeitet unter Umstaenden gegen eine ueberholte Regel. Ich habe die
  Datei deshalb von der Platte gelesen. **Keine Massnahme:** ein Vorkommen,
  und die Ursache liegt in der Werkzeugschicht, nicht im Vorgehen. Beim
  zweiten Vorkommen waere die billige Antwort, `CLAUDE.md` in die Leseliste
  des Uebergabe-Kontrakts aufzunehmen.
- **Die QA-237-Falle hat mich selbst erwischt, und das schreibe ich hierhin,
  damit die naechste Retrospektive es nicht neu lernt (12.09.2026).** Beim
  Pruefen von QA-231 fand ich `%LOCALAPPDATA%\NightreignHelper-Testabzug` mit
  **841 Dateien** und Zeitstempel 18:46 — und war eine Zeile davon entfernt,
  daraus "der Befund ist falsch, das Verzeichnis existiert" zu machen. Nach
  QA-237 ist genau diese Sicht **kein Beleg**: wer in der Ueberlagerung sitzt,
  sieht seine eigene Schicht. Der Leseversuch auf die Datei darin scheitert mit
  `Permission denied` — dasselbe Symptom, das T-196 beschrieben hat. **Was von
  der Pruefung bleibt:** QA-231 ist laut `qa/findings.md` ohnehin **behoben**
  (T-200, Nachweis durch eine Probe des Nutzers am echten System), und
  `CLAUDE.md` ist nachgezogen; nur meine Kontextfassung sagte es anders.
- **Der T-205-Bericht existiert nicht.** `docs/tasks/T-205.md` nennt ihn
  (*"der Bericht liegt ab"*), drei unabhaengige Pruefungen finden ihn nicht
  (`ls`, `find docs -iname "*205*"`, `git log --all -- "docs/berichte/T-205*"`),
  und eine Volltextsuche nach `T-205` trifft nur `docs/state.md` und die zwei
  nachgetragenen Auftragsdateien. Der `archivist` hat kein `Write`; sein
  Bericht existierte damit nur als Nachricht — genau der Fall, vor dem
  `_rahmen.md` warnt (*"Ein Bericht, der nur als Nachricht existiert, ist nach
  der Uebergabe nur noch die Auswahl des Directors"*). **Das ist die
  eigentliche Kosten des NH-001-Bruchs** und als Einzelfall hier vermerkt: das
  Ergebnis (23 Commits gepusht, `a4f275d..de420b6`) steht nur noch in der
  Auftragsdatei, nicht in einem Bericht.
- **Der Status in dieser Datei ist nicht mehr die Wahrheit (12.09.2026).**
  L-009 steht hier als *"vorgeschlagen"* und ist seit dem 06.09. in fuenf
  Rollendefinitionen und in `docs/plan-restarbeiten.md` in Kraft. Eine
  Wirkungskontrolle, die dem Statusfeld glaubt, prueft die falschen Regeln —
  ich habe jede Nummer stattdessen im Agenten-Repo und in
  `plan-restarbeiten.md` gegengesucht. **Zweites Vorkommen der Klasse "zwei
  Regelsaetze, ein Nummernraum"** (erstes: L-018). Beim dritten wird daraus
  ein Muster, und die Massnahme waere, das Statusfeld hier zu streichen und
  nur noch den Ort zu nennen, an dem die Regel wirklich steht.
- **`L-022` bis `L-026` existieren in keinem Satz, auf den sie zeigen.** Drei
  Hook-Kommentare nennen sie mit dem Praefix `Nightreign-Helper`; diese Datei
  endet bei L-018, und `T-112` ist hier `T-112-technical-writer.md`. Gehoert
  zur L-018-Wirkungskontrolle oben, hier nur als offene Einzelkorrektur
  vermerkt.
- **`docs/state.md` ist waehrend dieses Laufs zweimal fortgeschrieben worden**
  (`7c3a260`, dann `98cdf61` um 21:30). Zwei meiner Zwischenbefunde — der
  Nummernkreis nannte "T ab T-205", waehrend T-206 bis T-210 vergeben waren,
  und die Datei war noch nicht auf Budget — waren beim Schreiben dieses
  Eintrags bereits behoben. Kein Fehler, aber ein Hinweis fuer die naechste
  Retrospektive: eine Aussage ueber `docs/state.md` braucht die Commit-Kennung
  daneben, sonst ist sie eine Stunde spaeter falsch.

---

### Nachtrag — Codeprobleme, die mir aufgefallen sind und nicht meine Sache sind

Fuer den `director`, nicht Teil der Analyse:

1. **Fuenf Skripte setzen `QT_QPA_PLATFORM=offscreen` als Vorgabe**
   (`scripts/measure_picker_cards.py:60`, `measure_display_thresholds.py:53`,
   `measure_advisor_block.py:287`, `capture_weapon_damage.py:33`,
   `scripts/differential/capture.py:77`). Drei davon messen Geometrie. Das ist
   die Fundstelle der L-009-Falle aus T-199, und der Grund, warum T-199 zwei
   Laeufe brauchte.
2. **`qa/findings.md:263` (QA-240) rendert mit neun statt acht Spalten** —
   unmaskiertes `|` in einem Codespan. Die einzige verbliebene Abweichung in
   291 Tabellenzeilen beider Befunddateien.

---

## Zyklus 26 — 2026-09-16 (Part 12, Stand `c615b6c`, T-286)

**Ziel des Zyklus:** 1.13.1 fertigstellen und veroeffentlichen — AK-313,
A-008, Bau, Pruefkette, Release-Texte, clean-room, power-user, Tag `v1.13.1`.

**Datengrundlage:** `docs/state.md` (`c615b6c`, Abschnitt "Lehren dieses
Zyklus"), `docs/berichte/T-283-qa-engineer.md`,
`T-285-release-manager-clean-room.md` (334 Zeilen, beide Laeufe),
`T-285-power-user.md`, dazu die aelteren power-user-Berichte T-241d, T-265,
T-272, T-275 und `T-241-release-manager-cleanroom.md`,
`T-265-release-manager-cleanroom.md`; `docs/tasks/T-281.md`, `T-283.md`,
`T-284.md`, `T-277.md`; `qa/findings.md` (QA-256 drei Zeilen, QA-279,
QA-282); `docs/release/ROLLOUT.md:305-318`; `CLAUDE.md`,
`.claude/hooks/enforce-data-redirect.ps1`, `.claude/settings.json`;
`~/.claude/agents/_rahmen.md`, `power-user.md`, `commands/director.md`,
`templates/task.md`, `hooks/limit-tool-calls.ps1`, `~/.claude/settings.json`;
`git log 79664c2..c615b6c` (18 Commits, 17:02-18:30); das teamweite Register
`ApplicationHelper/docs/lessons.md` (L-001 bis L-033).

**Nummernraum — zuerst geprueft, mit Befund.** Das teamweite Register liegt
in `ApplicationHelper/docs/lessons.md` und endet bei **L-033** (15.09.). Die
Eintraege **L-019 und L-020 dieser Datei** (12.09.) wurden damals "als
teamweite Nummern" vergeben, weil der teamweite Satz "bei L-013 endet" —
gemessen an den Agentendefinitionen, nicht am Register: dort standen L-019
(Absenz-Regel gespiegelt) und L-020 (Empfaenger misst nach) seit dem 06.09.
**Kollision, drittes Vorkommen der Klasse "zwei Regelsaetze, ein
Nummernraum"** (erstes L-018, zweites Beobachtung 12.09.) — und damit nach
eigener Ansage ein Muster. Konsequenz hier: **keine neuen `L-`-Nummern in
dieser Datei.** Neue Projekteintraege heissen `NH-###` (Fortsetzung von
NH-003; NH-001/002 stehen in `docs/plan-restarbeiten.md`, wo `CLAUDE.md`
die Regelpflege ansiedelt). L-019/L-020 hier bleiben stehen, weil
`selftest.ps1:497` sie mit Projektpraefix zitiert; wer sie nennt, schreibt
"Nightreign-Helper L-020". Ein Vorschlag, der teamweiten Text aendert, ist
hier ein NH-Eintrag mit dem Vermerk "Kandidat teamweit"; die Nummer L-034 ff.
vergibt nur, wer das Register in ApplicationHelper fortschreibt. Der
Auftrag sagte "L-Nummern fortsetzen" — das widerspraeche `_rahmen.md:113`
und wuerde die Kollision verlaengern; deshalb nicht befolgt, hier begruendet.

### Gut gelaufen (schuetzenswert)

- **88 Minuten von AK-313 bis zum gruenen Release-Run**, 18 Commits, mit
  voller Pruefkette: QA PASS (T-283a), Security fand SEC-048 (Token in
  `release.yml`) und der Fix lag 12 Minuten spaeter (`af85fbd`), Compliance
  empfahl `body_path` (A-037) und der Release-Text traegt ihn.
- **T-285a hat 28 Minuten gewartet und keinen fremden Prozess beendet** —
  ANNAHMEN nennt das ausdruecklich ("kein `Stop-Process` auf die fremden
  PIDs"). Das ist die QA-256-Nachtragsregel vom 14.09. (ein paralleler Lauf
  hatte damals eine fremde Instanz beendet), und sie hat gehalten. Dass das
  Warten selbst der Fehler war, steht unter NH-004; das Nichteingreifen war
  richtig.
- **T-285a hat sein Werkzeugrezept aufgeschrieben** ("Methodik-Nachtrag …
  fuer kuenftige clean-room-Laeufe festgehalten"): `Invoke()` ohne Wirkung,
  `BoundingRectangle` physisch (2010x1075) gegen `GetWindowRect`
  virtualisiert (1622x898), Dialog nicht unter `RootElement`. Das ist die
  erste Messung hinter fuenf Klickproblemen (NH-005).
- **T-283a hat die Abweichung 1729 → 1727 exakt erklaert** (zwei
  MUTATIONS-Parametrisierungen weniger) statt sie als Flattern abzutun — und
  die 9 → 10 skipped ehrlich als "nicht nachverfolgt" markiert.
- **Der Director hat seinen Planungsfehler in die Commit-Botschaft
  geschrieben** (`a0ce3f6`: "Director-Planungsfehler") und die drei Lehren in
  `docs/state.md` fuer diese Retrospektive abgelegt. Ohne diesen Abschnitt
  waere NH-004 nicht in einer Sitzung belegbar.
- **L-031 hat beim ersten Einsatz in diesem Projekt getragen** (siehe
  Wirkungskontrolle).

### Wirkungskontrolle frueherer Massnahmen

| ID | Massnahme | Uebernommen am | Wirkung | Konsequenz |
|---|---|---|---|---|
| **L-031** (teamweit) — Klon-Volllauf als feste Vorlagenzeile, Ergebnis nach der Schwelle lesbar | 2026-09-15 (`templates/task.md:52-54`, `limit-tool-calls.ps1:144`) | **Wirkt, 1 von 1.** `docs/tasks/T-281.md:63-65` traegt die Vorlagenzeile woertlich; die Zahl **1729 passed / 9 skipped (Klon)** steht im Director-Stand und als Praemisse in `T-283.md:19`; T-283a hat sie gegen seine eigene Messung gehalten und die Differenz erklaert. Kein Schwellenfall im Zyklus, also ist die Hook-Haelfte hier ungeprueft. | Keine. |
| **OF-35** (Projekt) — nachgefahrene `MUTATIONS` loescht der `qa-engineer` im Pruefphasenlauf | 2026-09-13 | **Wirkt, vierte Anwendung in Folge** (T-239, T-249, T-251, T-283a). T-283a: zwei Eintraege je in einem `git archive`-Baum nachgefahren, beide Killer rot mit der vorhergesagten Botschaft, geloescht, Director-Commit `a4e8b97`. | Keine. Als eingefahren betrachten; nicht mehr pruefen. |
| **L-019** (Nightreign-Helper, 12.09.) — Waechter registrieren | 2026-09-12 | **Wirkt.** `~/.claude/settings.json` registriert `require-receipt`, `state-line-budget`, `id-collision-guard`, `count-serial-dispatches`, `limit-tool-calls` (grep 16.09.). | Keine. |
| **L-020** (Nightreign-Helper, 12.09.) — `docs/state.md` auf Budget | 2026-09-12 | **Wirkt am Stichtag:** 111 Zeilen bei `c615b6c` (`wc -l`). | Keine. |
| **NH-001** — jede nicht-triviale Arbeit bekommt eine Auftragsdatei | 2026-09-06 | **Tot.** Gezaehlt an `ls docs/tasks`: von T-240 bis T-285 haben **18 von 46** Nummern eine Datei, seit T-263 **5 von 23** (T-263, T-277, T-281, T-283, T-284). T-282 (Bau) und **T-285 (drei Rollen: clean-room, power-user, notes)** liefen ohne Datei. **Die Kosten sind diesmal messbar:** die Vorlage traegt die Felder `Testumgebung` und `Parallel:`; im letzten Auftrag mit Fensterlauf **und** Datei (`T-277.md:52`) hat der Director die Instanzsperre selbst hineingeschrieben ("Fensterlaeufe nur in b"). T-285 hatte keine Datei, kein Feld, keine Reihenfolge — und die Sperre schlug zu. | **Zurueckgenommen als Prosa, ersetzt durch einen Waechter → NH-006.** Nach `_rahmen.md:110-112` bekommt eine Fehlerklasse beim zweiten Mal einen Waechter; dies ist das vierte Vorkommen (Zyklus 13: 2, Zyklus 20: 2, jetzt 28 Nummern). |
| **NH-002** — Bildnachweise nur aus dem Programmfenster | 2026-09-05 | **Wirkt.** T-285a: `diag1-6.png` per `PrintWindow`, nur im Scratchpad, geloescht, nicht im Repo. | Keine. |
| **NH-003** — Spaltenwaechter ueber die Befundtabellen | 2026-09-12 | **Wirkt.** `tests/test_findings_tables.py` vorhanden, Suite gruen (T-283a); QA-282 wurde angehaengt, nicht eingefuegt. | Keine. |
| **QA-256 "Prozessregel: nur ein Fensterlauf gleichzeitig"** (Adressat `director`, Status "offen — Prozessregel") | 2026-09-14 | **Wirkt nicht.** Die Regel hat genau dort gehalten, wo die Rolle sie selbst kannte (T-265d: `qa-engineer` wartete auf den clean-room-Bericht und ein leeres `Get-Process`), und dort versagt, wo sie den Director vor dem Dispatch haette erreichen muessen (T-285). Sie stand in `qa/findings.md:316` (Zeile 316 von 463) und in `ROLLOUT.md:311` — keine der beiden Dateien liest der Director, bevor er eine Pruefkette dispatcht. | → **NH-004**. |

**Bilanz: acht Massnahmen geprueft, sechs wirken (L-031, OF-35, L-019,
L-020, NH-002, NH-003), zwei nicht (NH-001 tot, QA-256-Prozessregel ohne
Ort).**

---

### NH-004 — Ein Sachverhalt, der in einem Befundregister mit Adressat "director" steht, erreicht den Director nicht vor dem naechsten Dispatch: die maschinenweite Instanzsperre hat dreimal parallele Fensterlaeufe getroffen

**Belege:**
1. **T-241d (14.09.)** — `T-241-release-manager-cleanroom.md:37-39`: Auftrag
   sieht clean-room, qa-engineer und power-user "gleichzeitig dieselbe
   `dist/`-EXE mit eigenen Umlenkungen" vor; clean-room wartete ~19 min,
   qa-engineer 23 min (QA-256 und Nachtrag, `qa/findings.md:316,319`).
   Befund als "Prozessregel: nur ein Fensterlauf gleichzeitig" an den
   `director`, Status "offen".
2. **T-265 (15.09.)** — `T-265-release-manager-cleanroom.md:50,67` wiederholt
   den Befund ("muessen zeitlich nacheinander"); T-265d haelt die Regel, weil
   der `qa-engineer` sie kennt (`qa/findings.md:434`). Kein Auftragstext.
3. **T-277 (15.09.)** — `docs/tasks/T-277.md:52`: der Director schreibt die
   Regel in einen developer-Auftrag ("die Instanzsperre ist maschinenweit
   (QA-256) — Fensterlaeufe nur in b"). Er kannte sie.
4. **T-285 (16.09.)** — kein Auftragstext auf Platte; laut
   `T-285-release-manager-clean-room.md` (ANNAHMEN) sah der Auftrag
   "parallel mit eigener Umlenkung" vor. power-user-Prozesse PID 21136/26972
   ab 17:38:08; clean-room-Start PID 5140 stumm beendet; **28 min Wartezeit**
   (17:38-18:06, drei Pollingfenster 6/9/9 min), Abbruch `a0ce3f6` 18:09,
   zweiter Lauf 18:10-18:26 nach Beenden der verwaisten Prozesse. Die
   power-user-Prozesse liefen 22 min nach dessen Bericht (`d603ae2` 17:48)
   weiter.

**Ursache:** Der Sachverhalt "diese EXE laeuft nur einmal je Maschine" ist
ein Projektfakt und stand nur in einem 463-zeiligen Befundregister und im
Ablaufplan des `release-manager` — beides Dateien, die vor einem Dispatch
niemand liest; `commands/director.md:235-238` zaehlt zudem abschliessend
drei Gruende fuer Reihenfolge auf, und "beide brauchen dasselbe exklusive
Betriebsmittel" ist keiner davon.

**Massnahme (zwei Teile, ein Mechanismus):**

(a) **Technischer Riegel, Projekt:** `.claude/hooks/enforce-data-redirect.ps1`,
einfuegen nach Zeile 78 (`if (-not ($istQuellstart -or …)) { exit 0 }`):

```powershell
# NH-004: die Instanzsperre ist maschinenweit (nrplanner/singleinstance.py,
# KEY). Ein zweiter Start endet stumm, und die Rolle wartet (T-241d 23 min,
# T-285a 28 min). Bei laufender Kopie wird der Start abgewiesen, damit die
# Rolle sofort `blockiert` meldet statt zu pollen. Nur fuer Startformen, in
# denen die EXE das Kommando ist - Hash- und ls-Aufrufe nennen sie als Argument.
$istExeKommando = $cmd -match '(?i)(^|[;&|(]\s*|Start-Process\s+(-FilePath\s+)?|&\s+)["'']?([^\s"'']*[\\/])?NightreignHelper\.exe["'']?(\s|$)'
if ($istQuellstart -or $istFensterMessskript -or $istExeKommando) {
    $laeuft = @(Get-Process -Name NightreignHelper -ErrorAction SilentlyContinue)
    $laeuft += @(Get-Process -Name python, pythonw -ErrorAction SilentlyContinue |
                 Where-Object { $_.MainWindowTitle -like 'Nightreign Helper*' })
    if ($laeuft.Count -gt 0) {
        $wer = ($laeuft | ForEach-Object { "$($_.ProcessName) PID $($_.Id) seit $($_.StartTime.ToString('HH:mm:ss'))" }) -join ', '
        $out = @{ hookSpecificOutput = @{
            hookEventName = 'PreToolUse'; permissionDecision = 'deny'
            permissionDecisionReason = "[instanzsperre] Nightreign Helper laeuft bereits ($wer); ein zweiter Start endet stumm (QA-256). Nicht warten, kein Stop-Process auf fremde PIDs: STATUS blockiert melden, der Director reiht die Fensterlaeufe." } }
        [Console]::Out.WriteLine(($out | ConvertTo-Json -Compress -Depth 5)); exit 0
    }
}
```
Grenzen, ausdruecklich: ein `cmd /c start …` und ein Quellstart ohne
Fenstertitel (Ladephase) rutschen durch — dieselbe Grenze, die der Hook
fuer seine Startformen schon nennt. Der Riegel muss beissen: wer ihn
einbaut, startet einmal bei laufender Kopie und zeigt das `deny` im Bericht
(`_rahmen.md:54-55`).

(b) **Projektfakt, `CLAUDE.md`**, Abschnitt "Datenverzeichnisse und
Umlenkung", nach dem Absatz "Plattformgrenze (QA-241 …)":

> **Ein Fensterlauf je Zeitpunkt (QA-256, NH-004):** Die Instanzsperre ist
> maschinenweit (`nrplanner/singleinstance.py`, `KEY`); ein zweiter Start
> endet stumm, der Hook weist ihn ab, solange eine Kopie laeuft.
> `qa-engineer` am Artefakt, `power-user` und `release-manager` `clean-room`
> stehen im Auftrag in einer Reihenfolge, nie unter `Parallel: ja`;
> `notes`, `security-reviewer`, `compliance-agent` duerfen parallel.

**Ersatz/Streichung:** QA-256 (drei Zeilen, "offen — Prozessregel") bekommt
eine Abschlusszeile "erledigt — Riegel im Hook, Fakt in CLAUDE.md" (haengt
der Director an). `ROLLOUT.md:309-312` (Satz zur Sperre in Schritt 4) kann
auf "siehe CLAUDE.md" verkuerzt werden. Der Zuwachs in `CLAUDE.md` (5
Zeilen) ist begruendet: es ist ein Fakt ohne Ort, keine weitere Regel.
**Wer liest es wann:** den Hook liest niemand, er feuert beim Start; die
`CLAUDE.md` liest der Director beim Sitzungsbeginn und jede Rolle ueber den
Verweis in jedem Auftrag.

**Verworfen:** ein vierter Grund in `commands/director.md:235` ("beide
starten dasselbe Programm, das nur einmal je Maschine laeuft"). Der Riegel
und der Fakt decken das Projekt; fuer andere Projekte gibt es keinen Beleg
fuer ein exklusives Betriebsmittel, und die Liste ist abschliessend
formuliert — sie zu verlaengern kostet jeden Dispatch eine Zeile Kontext
fuer einen Fall, der bisher nur hier vorkam. Als Beobachtung fuer das
teamweite Register vermerkt.

**Erfolgskriterium:** In den naechsten zwei Zyklen kein Bericht mit
Wartezeit auf eine fremde Instanz; jeder Auftrag mit zwei Fensterrollen
nennt eine Reihenfolge; der Hook hat mindestens einmal ein `deny`
ausgesprochen (sonst ist er nicht angeschlossen, L-019).

**Status:** vorgeschlagen

---

### NH-005 — Das Klickrezept des `power-user` (DPI-Einheit, Koordinatenquelle, Aufraeumen) steht in keiner Datei, die er liest, und wird in jedem Lauf neu gesucht: fuenf von fuenf Artefaktlaeufen mit Klickproblem, A11 deshalb seit drei Laeufen ohne Nachweis

**Belege (alle power-user-Laeufe am Artefakt seit 14.09.):**

| Lauf | Artefakt | Klickproblem | Kosten |
|---|---|---|---|
| T-241d (14.09.) | 1.10.0 | "Klickversatz bei 125 %" — `Save build` oeffnete sich statt Optimize | Ziele 3, 4 kontaminiert |
| T-265 (15.09.) | 1.12.0 | Durchgang 1 an Schritt 0 gescheitert (Klickversatz); Durchgang 2 mit DPI-aware-Shell traf | ein ganzer Durchgang |
| T-272 (15.09.) | 1.12.2 | "Klicks rutschten auf das Hauptfenster hinter dem Picker" | Ziel 3 aufgegeben (>20 min) |
| T-275 (15.09.) | 1.12.3 | Raider-Kachel reagierte nicht (5 Klicks) → QA-279; Retest T-276 mit echter Maus: nicht reproduzierbar | Ziel 1 aufgegeben |
| T-285b (16.09.) | 1.13.1 | nach einem wirksamen Klick kam keiner mehr an → QA-282 | 5 von 6 Zielen nicht erreicht; Prozesse liefen 22 min nach dem Bericht weiter |

Dazu die Messung aus `T-285-release-manager-clean-room.md` (zweiter Lauf):
`BoundingRectangle` liefert physische Pixel (2010x1075), `GetWindowRect` aus
einem nicht DPI-bewussten Prozess virtualisierte (1622x898); erst
`GetWindowRect`-relative Koordinaten trafen. T-276 (QA) traf mit
`SetProcessDPIAware` + `SetCursorPos`. Beides passt zusammen: **Prozess
und Koordinatenquelle muessen dieselbe Einheit haben**; gemischt liegt der
Klick bei 125 % um ein Fuenftel daneben. Ob T-285b genau so gemischt hat,
laesst sich nicht sagen — seine Werkzeugzeile nennt weder DPI-Bewusstsein
noch Koordinatenquelle; das ist Teil des Befunds.

**Ursache:** `agents/power-user.md:186-189` schreibt das Klickmittel vor
(`SetCursorPos`/`SendInput`), nicht die Einheit und die Koordinatenquelle;
`commands/director.md:194-195` verbietet, dem `power-user` im Auftrag etwas
anderes als Persona, Ziele und Zugang zu geben; der `power-user` hat kein
`Write` und beim naechsten Aufruf keinen Kontext — das Rezept kann also
**nur** in seiner Definition ueberleben, und dort fehlt es. Ein Ende-Ritual
(Programm beenden, Prozesse pruefen) fehlt ebenfalls (T-241d hinterliess
Ordner und Registryschluessel, T-285b zwei Prozesse).

**Massnahme (Kandidat teamweit), `~/.claude/agents/power-user.md`:**

Ersetzen (Z. 186-189):
> den Fensterinhalt als Text auslesen (`UIAutomation` ueber .NET, z. B.
> `[System.Windows.Automation.AutomationElement]`) und ueber
> `SetCursorPos`/`SendInput` klicken, dann die Wirkung wieder als Text ablesen.

durch:
> den Fensterinhalt als Text auslesen (`UIAutomation` ueber .NET, z. B.
> `[System.Windows.Automation.AutomationElement]`) und ueber
> `SetCursorPos`/`SendInput` klicken, dann die Wirkung wieder als Text ablesen.
> **Prozess und Koordinaten in derselben Einheit:** entweder
> `SetProcessDPIAware()` vor dem ersten Klick und physische Pixel aus
> `BoundingRectangle` — oder ohne DPI-Bewusstsein und Koordinaten relativ zu
> `GetWindowRect` des Programmfensters. Gemischt liegt der Klick bei 125 %
> um ein Fuenftel daneben, bei kleinen Elementen ins Leere und ohne
> Fehlermeldung. Nach jedem Klick, der etwas oeffnet oder verschiebt, liest
> du die Position neu. Deine Werkzeugzeile im Bericht nennt beides:
> DPI-Bewusstsein und Koordinatenquelle. Am Ende beendest du das Programm
> und pruefst, dass kein Prozess von dir uebrig ist — eine liegengebliebene
> Kopie sperrt den naechsten Lauf.

**Streichung dafuer** (Z. 93-97, der Belegabsatz zu Schritt 0):
> **Belegt am 06.09.2026:** ein sechster Durchgang lief vollstaendig durch,
> alle sechs Ziele erreicht, wirkte gelungen - und war als Nachweis wertlos,
> weil kein einziger echter Klick angekommen war. Der Lauf war bezahlt, das
> Kriterium blieb offen.

wird zu:
> (Belegt 06.09.2026: ein voller Durchgang, sechs Ziele, kein angekommener Klick.)

Netto +5 Zeilen; der Beleg bleibt als Ausloeser erhalten, die Erzaehlung
faellt. Kein Hook moeglich: der Fehler zeigt sich erst im Klick, nicht im
Kommando. **Wer liest es wann:** der `power-user` bei jedem Aufruf — es ist
die einzige Datei, die er ueberhaupt liest.

**Erfolgskriterium:** Die naechsten zwei power-user-Laeufe an diesem Projekt
nennen DPI-Bewusstsein und Koordinatenquelle in der Werkzeugzeile und
erreichen entweder mindestens vier von sechs Zielen oder brechen an
Schritt 0 ab; kein "aufgegeben wegen Klick" mehr; `Get-Process
NightreignHelper` ist beim Start der Folgerolle leer.

**Status:** vorgeschlagen

---

### NH-006 — NH-001 wird durch einen Waechter ersetzt: ein Dispatch mit T-Nummer ohne Auftragsdatei wird abgewiesen

**Belege:** Wirkungskontrolle NH-001 oben — 5 von 23 Nummern seit T-263 mit
Datei; T-285 als Fall mit messbaren Kosten (NH-004, Beleg 4). Viertes
Vorkommen der Klasse; `_rahmen.md:110-112` verlangt ab dem zweiten einen
Waechter.

**Ursache:** Die Regel adressiert die Rolle, die am Ende eines Zyklus die
meisten Dispatches in der kuerzesten Zeit schreibt, und hat keinen
Pruefpunkt — der Nachtrag "Datei spaeter" ist immer moeglich und wird
deshalb zur Regel.

**Massnahme (Kandidat teamweit, Team-Repo):** neuer Hook
`~/.claude/hooks/require-task-file.ps1`, registriert in
`~/.claude/settings.json` als `PreToolUse` mit Matcher `Agent|Task`:

> Liest `tool_input.prompt`. Existiert im Arbeitsverzeichnis kein
> `docs/tasks/`, Ende ohne Befund. Sonst: hoechste `T-\d{3}` im Prompt
> (die neue Nummer ist immer die hoechste; aeltere sind Quittungen und
> duerfen fehlen). Fehlt `docs/tasks/T-###.md`, `deny` mit:
> `[auftragsdatei] docs/tasks/T-###.md fehlt (NH-001). Vorlage:
> cp ~/.claude/templates/task.md docs/tasks/T-###.md — Felder Parallel und
> Testumgebung ausfuellen, dann dispatchen.`
> Ein Dispatch ohne T-Nummer passiert — das ist die sichtbare Ausnahme fuer
> Triviales, und `check-handoff.ps1` faengt einen Bericht mit `AUFTRAG:`
> ohne Nummer.

Der Riegel muss beissen: einmal mit fehlender Datei dispatchen und das
`deny` zeigen. Nach L-019 gilt: ohne Eintrag in `settings.json` existiert
der Hook nicht.

**Streichung:** `docs/plan-restarbeiten.md:205-207` (NH-001 als Prosa mit
Bruchbilanz) wird zu einer Zeile: "NH-001: Waechter
`require-task-file.ps1` (16.09.)". Kein weiterer Text im Director.

**Wer liest es wann:** niemand; der Hook feuert beim Dispatch.

**Erfolgskriterium:** In zwei Zyklen tragen alle T-Nummern aus den
Commit-Botschaften des Zyklus eine Datei in `docs/tasks/` (Zaehlung wie
oben); kein Commit "Auftragsdatei nachgetragen".

**Status:** vorgeschlagen

---

### Beobachtungen (noch kein Muster)

- **Bash-Heredoc mit dem EXE-Namen vom Umlenkungs-Hook gesperrt — zwei
  Vorkommen am 16.09.:** der Director bei der Buchfuehrung, und diese
  Retrospektive beim ersten Anhaengen dieses Abschnitts (Ausweg:
  Scratchpad-Datei per `Write`, dann `cat >>`). `enforce-data-redirect.ps1:67`
  haelt jede Kommandozeile mit dem EXE-Namen fuer einen Start — auch eine, die
  Doku schreibt. Fuer den Director steht die Regel schon:
  `commands/director.md:223-225` ("Dateien aenderst du mit `Edit` und
  `Write` … nicht mit Ersetzungsskripten ueber Bash"); fuer eine Rolle, die
  eine Datei nur anhaengt, ist `Write` mit Vollinhalt teuer (diese Datei:
  1502 Zeilen). **Keine Massnahme**: NH-004 (a) fuehrt ohnehin eine engere
  Startmaske `$istExeKommando` ein; wird sie auch fuer die Umlenkungspruefung
  benutzt, verschwindet der Fehlalarm. Beim dritten Vorkommen ist das die
  Massnahme.
- **Werkzeugbefunde sammeln sich im QA-Register als "zurueckgestellt —
  Werkzeug"** (QA-256 P4, QA-279 P2 geschlossen, QA-282 P3, dazu QA-241 und
  QA-271 "Team-Repo"). Das ist ApplicationHelper L-022 in Projektform
  ("Werkzeugfehler steht als Programmbefund im QA-Register"). Vorerst nur
  vermerkt: NH-004 und NH-005 loesen drei davon; bleiben nach dem naechsten
  Zyklus weitere liegen, braucht das Register eine Spalte oder einen
  eigenen Abschnitt "Werkzeug".
- **T-283a: UIA fand die Heldenkacheln nicht unter `ControlType.Button`**,
  Live-Probe fuer AK-312 abgebrochen, Quellbeleg genuegte. Dieselbe
  Werkzeugfamilie wie NH-005, andere Rolle; ein Vorkommen.
- **T-285a hat 28 Minuten gepollt statt `blockiert` zu melden** —
  `_rahmen.md:37-39` setzt 10 Minuten als Obergrenze, `_rahmen.md:102-103`
  nennt `blockiert` ein Ergebnis. Zweites Vorkommen nach T-241 (19/23 min).
  Der NH-004-Riegel macht das Warten unmoeglich; falls er nicht kommt, ist
  das beim dritten Mal ein eigenes Muster.
- **Fuer das teamweite Register:** "exklusives Betriebsmittel" als vierter
  Grund fuer Reihenfolge in `director.md:235` — hier verworfen (NH-004);
  tritt derselbe Fall in einem zweiten Projekt auf, ist der Ort dort.
- **Kollision L-019/L-020** (Kopf dieses Abschnitts): der Auftrag an diese
  Retrospektive verlangte "L-Nummern fortsetzen". Der Director liest diese
  Datei am Zyklusende; die Nummernregel steht in `_rahmen.md:113`. Ein
  Satz im Retrospektive-Dispatch ("Projektnummern NH-") wuerde reichen — er
  gehoert in den Director-Text nur, wenn es noch einmal passiert.

---

## Zyklus 27 — 2026-09-19 (Part 12, Stand `6467e06`, T-297)

**Ziel des Zyklus:** Nutzerbefund AK-314 beheben und als 1.13.2
veroeffentlichen; A22/A23 entwerfen, bauen, pruefen und als 1.14.0
veroeffentlichen; danach aufraeumen (README, Ponytail-Audit, Repo-Hygiene).
Zeitraum 17.-19.09., 54 Commits `ae474c1..6467e06`, Auftraege T-287..T-296.

**Datengrundlage:** `GOAL.md` (A22, A23), `docs/state.md` (`6467e06`, 81
Zeilen) und die Fassung `c663573~1`; `docs/tasks/T-287..T-297.md`;
`docs/berichte/T-288-developer.md`, `T-290-qa-engineer.md` (beide Fassungen:
`6f5c223` blockiert, `3b399c1` teilweise), `T-290/293/294/295-release-manager-
build.md`, `T-293-qa-engineer.md`, `T-295-qa-engineer.md`,
`T-286-retrospective.md`; `qa/findings.md` QA-282..285 (7 Zeilen dieses
Zyklus); `DESIGN_REVIEW.md` DR-032/033; `UI_SPEC.md` AK-313/314/317;
`.claude/hooks/enforce-data-redirect.ps1` (`986216d`) und
`.claude/settings.json`; `~/.claude/agents/_rahmen.md`, `qa-engineer.md`,
`power-user.md` (Z. 186-196), `release-manager.md`, `commands/director.md`,
`templates/task.md`, `hooks/require-task-file.ps1`, `hooks/limit-tool-calls.ps1`,
`~/.claude/state/zugschwelle.log`; `git log`, `git for-each-ref` (Tags),
`gh release view v1.13.2`; Scratchpad `0c1b1951/T-293/qa-engineer/drv.ps1`.

**Nummernraum — geprueft.** Teamweite Zitate im Zyklus: nur `L-031`
(5 Nennungen, Klon-Volllauf, Vorlage). Projektnummern: `NH-006` ist die
letzte, `NH-007` kommt nirgends vor (`grep -rn "NH-00[7-9]"`: nur T-297.md).
Keine Kollision; der Auftrag sagte selbst "NH ab NH-007".

### Gut gelaufen (schuetzenswert)

- **T-288 hat den Nutzerbefund am echten Bestand reproduziert, nicht
  erklaert:** 948 Advisor-Laeufe (72 + 840 + 34 + 2), read-only; die Ursache
  (a) lag ausserhalb der vier Hypothesen des Auftrags. Auftrag 18:50, Fix
  `bc4443e` 19:09, Mutation nachgefahren (1 failed / 46 passed).
- **Sicherheitsblock als Vorlauf:** T-292c lieferte fuenf Zeilen, der
  Director haengte sie an T-292d, T-293c fand 0/0/0/0 — Sicherheit vor dem
  Bau statt danach.
- **T-293b:** drei Pruefbereiche, 27 Skripte, alle Punkte am Artefakt,
  zwei Befunde; QA-285 mit zwei Lesarten **ohne eigene Entscheidung**
  gemeldet; der Director entschied Lesart B mit Begruendung in `T-294.md`.
- **T-295c** replizierte QA-285 rot-vorher gegen `f5e91ca~1` und erkannte,
  dass das Register dem Pruefstand vorauslief ("behoben -- Retest T-294c"
  ohne T-294c) — korrigiert per Anhang, wie NH-003 es verlangt.
- **Ein Baubefund wanderte ueber den Auftragstext:** T-290a fand den Bau
  gegen die globale Python-Installation; T-293a trug "Bau ueber `.venv`
  (T-290-Befund)", und T-293/294/295 melden "kein globales `python`".
- **1.14.0 in 20 Minuten mit QA am Artefakt:** Spec-Nachtrag 08:31 → Fix
  08:35 → Bau 08:39 → notes 08:42 → QA PASS 08:51 → Tag 08:51:51.
- **T-296b nutzte die Ausstiegsbedingung:** Pillow blieb, weil die
  Pixelgleichheit nicht nachweisbar war ("weicht ein Pixel ab, teilweise
  melden, nicht erzwingen"); Audit netto -421 Zeilen.
- **T-290b (Lauf 2) stellte die Warnung an den Kopf:** "EXE laeuft
  vermutlich noch, PID 22320/6080" — der Director beendete die Kopie
  (`3b399c1`), kein verwaister Prozess fuer die naechste Rolle.

### Wirkungskontrolle frueherer Massnahmen

| ID | Massnahme | Uebernommen am | Wirkung | Konsequenz |
|---|---|---|---|---|
| **NH-004** — Riegel im Hook + Fakt in CLAUDE.md | 2026-09-16 (`2ca5b00`) | **Teilweise.** Kriterium 2 erfuellt: 4 von 4 Auftraegen mit Fensterrolle (T-290, T-293, T-294, T-295) nennen eine Reihenfolge. Kriterium 3 erfuellt: `deny` gezeigt am 16.09. (T-287a) und 17.09. (`986216d`, Quellstart bei laufender Kopie). **Kriterium 1 verletzt:** T-290b wartete ~20 min auf die Nutzerkopie (`6f5c223`: "zwei Wartefenster a 5 Minuten plus die Laufzeit der Testsuite"); der Riegel sitzt am Start, der Dispatch kam trotzdem und verlangte das Warten. Nebenwirkung: die alte weite Maske `$istExeStart` blieb neben der neuen engen stehen (QA-283). | → NH-007 (Maske), NH-008 (Dispatch) |
| **NH-005** — Klickrezept in `power-user.md` | 2026-09-16 (Team-Repo `935233e`, Z. 186-196 geprueft) | **Nicht messbar:** kein power-user-Lauf im Zyklus (0 von 2 Releases). Das Rezept kam beim `qa-engineer` an — ueber die Berichtskette T-285a → T-290b → T-293b → T-295c, nicht ueber eine Datei, die er liest. | offen; → NH-009 |
| **NH-006** — Hook `require-task-file.ps1` | 2026-09-16 (registriert `~/.claude/settings.json:41`) | **Wirkt.** 10 von 10 Nummern T-288..T-297 mit Datei (`ls docs/tasks`); kein "nachgetragen"-Commit in 54 Commits. Vorher 5 von 23. | Keine; nicht mehr pruefen. |
| **L-031** (teamweit) — Klon-Volllauf | 2026-09-15 | **Wirkt:** T-288 (1728/10 Klon, `klon.txt`), T-292e (1777/11, in T-293.md als Stand zitiert), T-294a (T-295c nennt den Klonlauf). | Keine. |
| **L-020** (Nightreign-Helper) — `docs/state.md` auf Budget | 2026-09-12 | **Budget haelt:** 81 Zeilen. **Aktualitaet nicht:** 48 Commits lang unangetastet (`ba2e10c` 16.09. 18:53 → `c663573` 19.09. 09:09). Siehe Beobachtungen. | Keine. |
| **NH-002** — Bildnachweise nur `PrintWindow` | 2026-09-05 | **Wirkt:** T-293b Bilder aus dem Fenster, T-293d offscreen. | Keine. |
| **NH-003** — Spaltenwaechter Befundtabellen | 2026-09-12 | **Wirkt:** 7 Zeilen angehaengt (QA-283..285 und Folgezeilen), Suite gruen (T-293b, T-296b). | Keine; nicht mehr pruefen. |
| **OF-43** — Fuenf-Dateien-Grenze weicht bei UI-Duplikatlogik | 2026-09-17 | Einmal angewendet (T-289b, sieben Dateien, Abnahme `427b434`). Entscheidung, keine Massnahme. | — |

**Bilanz: acht geprueft, fuenf wirken (NH-006, L-031, L-020, NH-002,
NH-003), eine teilweise (NH-004), eine nicht messbar (NH-005), eine
Entscheidung (OF-43).**

---

### NH-007 — Der Umlenkungs-Hook haelt jede Nennung des EXE-Namens fuer einen Start: sieben Fehlalarme in vier Tagen, und der Fix vom 17.09. schloss nur die `run.py`-Haelfte

**Belege:**
1. 16.09. Director, Heredoc mit EXE-Name (Beobachtung Zyklus 26).
2. 16.09. Retrospektive T-286, dasselbe beim Anhaengen (Beobachtung Zyklus 26).
3./4. 17.09. developer T-288 und Director, `grep … nrplanner/advisor/run.py`
   (Kommentar `enforce-data-redirect.ps1:67-73`, Commit `986216d`).
5. T-290b Lauf 1: `tasklist //FI "IMAGENAME eq …exe"`, `certutil -hashfile`,
   `ls` → `deny`; zweimal reproduziert, einmal mit drei Fuellwerten umgangen
   (QA-283, P2, Adressat developer, **offen**).
6. T-290b Lauf 2 und T-293b: Hash per Python `hashlib` statt `Get-FileHash`,
   "da … den QA-283-Fehlalarm des Hooks ausloesen" (`T-290-qa-engineer.md:38`,
   `T-293-qa-engineer.md:27`).
7. T-294b: `Get-Process -Name NightreignHelper` "mit vollstaendiger Umlenkung
   in derselben Kommandozeile" (`T-294-release-manager-build.md:95`) — die
   Fuellwert-Gewoehnung, vor der QA-283 warnt.

Dazu die Abnahmeluecke: T-289b Punkt 2 nannte beide Startformen ("EXE oder
`python`/`pythonw` + `run.py` als Kommando"); der Fix `986216d` aenderte nur
`$istQuellstart` (Commit-Text nennt nur `run.py`), Abnahme `427b434`; QA-283
kam 50 Minuten spaeter.

**Ursache:** Zwei Masken fuer dieselbe Frage — `$istExeStart` (Z. 75, jede
Nennung) am Umlenkungs-Gate und `$istExeKommando` (Z. 94, nur
Kommandoposition) am Instanz-Gate; die enge Maske kam am 16.09. dazu, ohne
die weite zu ersetzen (Zuwachs statt Ersatz, Nightreign-Helper L-017).

**Massnahme (technischer Riegel, Projekt):** `.claude/hooks/enforce-data-redirect.ps1`
— Z. 75 (`$istExeStart = …`) streichen; den Block Z. 89-94
(Kommentar + `$istExeKommando`) vor Z. 87 ziehen; Z. 87 wird:

```powershell
if (-not ($istQuellstart -or $istExeKommando -or $istFensterMessskript)) { exit 0 }
```

Z. 95 bleibt wortgleich. Nachweis im Bericht, drei Zeilen: `ls dist/<EXE>`
und `Get-FileHash dist/<EXE>` gehen durch; `dist/<EXE>` ohne Variablen →
`deny [datenumlenkung]`; bei laufender Kopie → `deny [instanzsperre]`.
QA-283 bekommt die Abschlusszeile.

**Streichung:** `$istExeStart` samt Kommentarzeile; kein neuer Text.
**Wer liest es wann:** niemand, der Hook feuert. **Grenzen:** `cmd /c
start …` rutscht weiter durch (bekannt, Z. 57-63).

**Kosten:** keine. Ein Sonderfall: eine Kommandozeile, die die EXE **als
Argument eines Starters** nennt, den die Maske nicht kennt, wuerde jetzt
ohne Umlenkungspruefung durchgehen — dieselbe Luecke, die `$istExeKommando`
seit dem 16.09. am Instanz-Gate schon hat, und keine Startform aus einem
Bericht.

**Erfolgskriterium:** In zwei Zyklen kein Bericht mit "hashlib statt",
"Fuellwert" oder "Fehlalarm" zum Hook (`grep -l` ueber
`docs/berichte/T-3*.md` = 0); QA-283 geschlossen.

**Status:** vorgeschlagen

---

### NH-008 — Dritter Wartefall auf eine fremde Instanz: der Riegel sitzt am Start, der Dispatch kam trotzdem — und verlangte das Warten

**Belege:**
1. T-241d (14.09.): clean-room 19 min, qa-engineer 23 min (QA-256).
2. T-285a (16.09.): 28 min (NH-004 Beleg 4).
3. T-290b (17.09., `6f5c223`): "zwei Wartefenster a 5 Minuten plus die
   Laufzeit der Testsuite … rund 20 Minuten" auf die **Nutzerkopie**
   (PID 22016/22172, 20:03-21:04); ANNAHMEN: "Auftrag verlangt ausdruecklich
   Warten und Melden". Die Rolle hat nie einen Start versucht — der
   NH-004-Riegel hat deshalb nie gefeuert.

Folgekosten von Beleg 3: Lauf 2 als Fortsetzung desselben Agenten
(`director.md:214`) startete mit dem Restbudget von Lauf 1 und fiel um 21:28
an der Zugschwelle "mitten in der Fensterinteraktion" (`zugschwelle.log`,
einziger Eintrag dieses Projekts im Zyklus); EXE blieb laufen; AK-314 wurde
am Artefakt 1.13.2 nie belegt; Tag `v1.13.2` 21:57 mit QA `teilweise` —
gegen "Kein Tag ohne QA-Urteil" (`T-290.md`, Scope-Grenzen). Die
Beobachtung aus Zyklus 26 sagte: "beim dritten Mal ein eigenes Muster".

**Ursache:** NH-004 riegelt den *Start* bei laufender Kopie, nicht den
*Dispatch* einer Fensterrolle bei laufender Kopie; dort gilt nur
`_rahmen.md:37-39` (10 Minuten), und der Dispatchtext hob es auf.

**Massnahme (technischer Riegel, Projekt):** neuer Hook
`.claude/hooks/no-window-dispatch.ps1`, `PreToolUse`, Matcher `Agent|Task`,
Eintrag in `.claude/settings.json` nach dem Muster von
`require-task-file.ps1` (Prompt aus `tool_input.prompt`, Projektwurzel aus
`cwd`):

> Trifft der Prompt `(?i)qa-engineer|power-user|clean-room|Fensterlauf|am
> Artefakt|am Fenster` **und** liefert `Get-Process NightreignHelper` (oder
> `python`/`pythonw` mit Fenstertitel `Nightreign Helper*`) einen Prozess:
> `deny` mit
> `[fensterlauf] Nightreign Helper laeuft (<ProcessName> PID <n> seit
> <hh:mm:ss>) - NH-004/NH-008. Keine Fensterrolle dispatchen, solange die
> Kopie laeuft: warte selbst oder gib Arbeit ohne Programmstart (Diff,
> Suite, Spec). Kein Auftrag verlangt "warten" (_rahmen.md, 10 Minuten).`
> Sonst `exit 0`. Der Riegel muss beissen: einmal bei laufender Kopie einen
> QA-Dispatch provozieren, `deny` im Bericht.

**Streichung:** keine Textregel dazu. Begruendung: dritte Wiederholung
einer Fehlerklasse → Waechter, kein Text (`_rahmen.md:110-112`); der Hook
ersetzt die Wartezeile, die sonst in jeden Fensterauftrag muesste.
**Verworfen:** ein Satz in `director.md` "waehrend der Nutzer testet, kein
Fensterlauf" — Text ohne Waechter ist genau, was T-290b hatte: der
CLAUDE.md-Absatz NH-004 stand, der Dispatch kam trotzdem.

**Wer liest es wann:** niemand; feuert beim Dispatch.

**Kosten:** ein Fehltreffer, wenn ein Nicht-Fensterauftrag "am Artefakt"
sagt, waehrend eine Kopie laeuft — der Director formuliert um oder wartet;
Prozessabfrage unter einer Sekunde je Dispatch.

**Erfolgskriterium:** zwei Zyklen ohne Bericht mit Wartezeit auf eine
fremde Instanz und ohne `blockiert` wegen laufender Kopie; ein `deny`
gezeigt (sonst nicht angeschlossen, L-019).

**Status:** vorgeschlagen

---

### NH-009 — Das Fensterrezept lebt in Berichten und wird je Lauf neu gebaut und weggeworfen: der Treiber aus T-293b (144 Zeilen, 27 Funktionen) liegt im Scratchpad

**Belege:**
- Rezeptteile in 15 Berichten (`grep -l "SetCursorPos\|UIAutomation\|
  GetWindowRect"`: 6 unter `docs/archiv/berichte/`, 9 aktuell: T-241 x2,
  T-265d, T-268, T-276, T-285, T-290, T-293, T-295). Kein `.ps1` unter
  `scripts/` (16 `.py`, `differential/`).
- Kette dieses Zyklus: T-285a (`GetWindowRect` statt `BoundingRectangle`)
  → T-290b "Methodik-Nachtrag" (Alt-Taste vor `SetForegroundWindow`,
  `GetForegroundWindow` gegenpruefen; Filterfenster ist Top-Level) → T-293b
  (Kaestchen am Zellenrand +12 px; `drv.ps1` + `s1..s27.ps1`) → T-295c
  ("Rezept aus T-293b", `drv.ps1` + `s0..s11.ps1`). Jeder Lauf las den
  Vorgaengerbericht **aus eigenem Antrieb** — weder `T-293.md` noch
  `T-295.md` nennt ihn.
- T-290b Lauf 2 bezahlte die Entdeckung von zwei Fallstricken mit der
  Zugschwelle; T-293b und T-295c, die das Rezept kannten, kamen durch.
- `drv.ps1` existiert noch: `<Scratchpad 0c1b1951>/T-293/qa-engineer/drv.ps1`,
  144 Zeilen, 27 Funktionen (u. a. `Main`, `TopWin`, `Fg` mit Alt-Trick,
  `ClickAt`, `Click`, `Toggle-El`, `SetText`, `Shot` = `PrintWindow`,
  `Rows`/`FindRow`/`ClickCell`, `OpenFilters`, `CloseWin`, `Optimize`,
  `Blocks`). Scratchpads sind sitzungsgebunden.
- NH-005 legte das Rezept als Text in `power-user.md` — der `qa-engineer`
  liest die Datei nicht, und er hat es in diesem Zyklus gebraucht, nicht
  der `power-user`.

**Ursache:** Der `qa-engineer` darf im Arbeitsbaum nichts ablegen
(`qa-engineer.md:130-133`), der `power-user` hat kein `Write`, und keine
Regel macht den `developer` zum Eigner eines Prueftreibers — das Werkzeug
hat keinen Ort im Repo, nur in Berichten.

**Massnahme (technisch, Projekt, ein developer-Auftrag Stufe klein):**
`drv.ps1` als `scripts/drive_window.ps1` committen; Kopf mit vier Zeilen
(haengt sich an den laufenden Prozess, startet nichts; DPI per-monitor v2
und physische Pixel aus `BoundingRectangle`; Alt-Trick + `GetForegroundWindow`;
Kaestchen +12 px; `Shot` per `PrintWindow`; `CloseWin`); die
ORG in `Reg` wird Parameter statt Literal `DankYeeterT-293b`. Die
Pruefpunkt-Skripte je Lauf bleiben im Scratchpad. In `CLAUDE.md`, Abschnitt
"Testbefehl", eine Zeile nach dem Codeblock:

> Fensterlaeufe: `. scripts/drive_window.ps1` (UIA + echte Klicks; Rezept
> aus T-285/T-290b/T-293b). Nicht neu bauen; Luecken als Befund an den
> `developer`.

Der Treiber startet keinen Prozess — der Umlenkungs-Hook greift bei
Startformen, ein Attach ist keine.

**Streichung:** die "Methodik-Nachtrag"-Abschnitte in Berichten entfallen
(Befund an den developer statt Prosa). Zuwachs eine Zeile `CLAUDE.md`,
begruendet: Werkzeugverweis, keine Regel; ersetzt 15 Berichtsstellen.
**Wer liest es wann:** `qa-engineer`, `power-user`, `release-manager`
`clean-room` ueber den CLAUDE.md-Verweis in jedem Auftrag; der Director bei
Pruefung 2 der Vorlage ("hat die Rolle die Mittel").

**Kosten:** ~150 Zeilen unter `scripts/` (die Audit-Schuld
"Harness-Duplikate" waechst um eine Datei — dafuer verschwinden die
Wegwerf-Kopien); Pflege beim `developer`; Nutzen erst ab dem dritten Lauf
sicher.

**Erfolgskriterium:** die naechsten zwei Fensterlaeufe (QA oder power-user)
nennen `scripts/drive_window.ps1` in der Werkzeugzeile; kein
"Methodik-Nachtrag"; kein Fensterlauf an der Zugschwelle; ein
power-user-Lauf erreicht mindestens vier von sechs Zielen (NH-005 wird
damit messbar).

**Status:** vorgeschlagen

---

### Muster ohne eigene Massnahme — Drei Laienbefunde in vier Tagen kamen alle vom Nutzer am gebauten Artefakt, keiner aus der Pruefkette

**Belege:** AK-313 (16.09.: "Favourite" im Filterfenster = der Stern je
Relikt?; T-281 → Neubau 1.13.1) · AK-314 (17.09. 18:34: "nur einer scheint
auf"; Programm richtig, Satz fehlte; T-288/289 → **Hotfix-Release 1.13.2**)
· AK-317-Nachtrag (18./19.09.: Allow grau = kaputt; spec-konform nach
AK-316.4, die GOAL A23 "unter einer vermiedenen Familie" wortgetreu folgte;
T-295 → Neubau 1.14.0). Pruefketten dieser Releases: 1.13.2 build + QA
(blockiert/teilweise) + security; 1.14.0 build + QA + security +
design-review — kein `power-user`, kein `clean-room` (`director.md:147-150`
nennt beide); 1.13.1 hatte einen power-user-Lauf mit 1 von 6 Zielen
(QA-282). Der Ingame-Test des Nutzers stand in T-293/T-295 als Bedingung
vor dem Tag.

**Ursache:** Die einzige Rolle mit Laienblick hat in sechs Artefaktlaeufen
keinen Nachweis geliefert (fuenf am Werkzeug, einer nicht dispatcht), und
der Nutzer fuellt die Luecke selbst — nach dem Bau, also je Befund ein
Neubau, einmal ein Hotfix-Release. Weil der Nutzer kompensiert, faellt der
Ausfall der Rolle nicht auf.

**Keine eigene Massnahme:** NH-009 ist die Voraussetzung, damit
power-user-Laeufe ueberhaupt Nachweise liefern koennen. Ob der Nutzer die
Rolle danach wieder in die Kette will oder seinen Ingame-Test als A11-Gate
festschreibt (dann eine Zeile unter "Beschlossen" in `docs/state.md`, kein
Regeltext), ist seine Entscheidung — beide Wege sind billiger als ein
dritter Absatz. Vermerk fuer das teamweite Register (Kandidat, keine
Nummer): "Werkzeugausfall einer Rolle wird vom Nutzer kompensiert und
faellt deshalb nicht auf."

**Erfolgskriterium (Beobachtung):** Nutzerbefunde am Artefakt je Release in
den naechsten zwei Releases; mindestens einer je Release ohne Laienlauf
bestaetigt das Muster, null widerlegt es.

---

### Beobachtungen (noch kein Muster)

- **Tag 1.13.2 auf einem aelteren Commit** (`b0965e3`, Tag 21:57:25): 16
  Commits A22/A23 lagen zwischen Baustand und `notes` (`d92f959` 21:56);
  Release-Text nachtraeglich per `gh release edit --notes-file`. Ein
  Vorkommen — 1.13.1 und 1.14.0 tragen den Tag auf dem damaligen HEAD. Der
  Director hat das Rezept selbst notiert (`docs/state.md` "Release-Rezept",
  17.09.). **Kein Text in `director.md`.** Will der Nutzer trotzdem einen,
  ist es dieser Satz nach `director.md:150` ("`release-manager` (`notes`)"):
  "Zwischen `build` und Tag kein Commit auf dem Branch, der nicht zum
  Release gehoert; wartet das Release auf den Nutzer, laeuft Folgearbeit
  ohne Commit (Entwurf, Spec) oder im Worktree." Ein Waechter in
  `release.yml` ("`RELEASE_BODY.md` nennt die Tag-Version, sonst Abbruch")
  wurde geprueft und verworfen: er haette den Tag auf `b0965e3` blockiert
  statt geholfen; der Ausweg waere ein Release-Branch — mehr Prozess fuer
  einen Einzelfall.
- **Halber Fix abgenommen:** T-289b lieferte die `run.py`-Haelfte, nicht die
  EXE-Haelfte, Abnahme `427b434` ohne Pruefung des zweiten Punkts — Form
  Nightreign-Helper L-016 (Fundstelle statt Aussage). Hier unter NH-007
  gezaehlt; als Abnahmeluecke ein Vorkommen.
- **Fortsetzung nach `blockiert` teilt die Zugschwelle:** T-290b Lauf 2
  begann mit dem Restbudget von Lauf 1 (Suite 1735, Hook-Reproduktion,
  Register) und fiel bei 150. `director.md:214-215`: "Fortsetzen statt neu
  beauftragen … ausser nach der Zugschwelle". Ein Vorkommen in diesem
  Projekt. Beim zweiten: "nach `blockiert` mit Fensterlauf: neuer Lauf" —
  oder NH-008 macht den Fall unmoeglich.
- **`docs/state.md` 48 Commits lang unangetastet** (16.09. 18:53 → 19.09.
  09:09); die Zitate "Stand (docs/state.md, 17.09.2026)" in T-288..T-294
  stammen aus dem Kontext des Directors, nicht aus der Datei; Sitzungsende
  17.09. 22:53 ohne Stand und ohne Bericht T-294c. Kosten nicht messbar —
  der 19.09. lief ab T-295 mit richtigen Fakten an (aus `git log` und den
  Auftragsdateien, die NH-006 erzwungen hat). Budget L-020 haelt.
- **Register lief dem Pruefstand voraus:** T-294a schrieb "behoben --
  Retest T-294c" (`qa/findings.md:468-469`), bevor T-294c lief; T-295c
  korrigierte per Anhang. Ein Vorkommen; Ort waere der developer-Bericht
  ("behoben, Retest offen").
- **Kompaktform der Auftraege:** alle neun Auftraege des Zyklus lassen die
  Vorlagenabschnitte Kontext/Vorgaben/Testumgebung weg. Keine messbaren
  Kosten; der Bauhinweis (`.venv`) und die Umlenkung standen trotzdem im
  Kopf. Nur vermerkt.
- **Tag mit QA `teilweise`:** `v1.13.2` 21:57 nach T-290b Lauf 2
  (`teilweise`), `T-290.md` Scope "Kein Tag ohne QA-Urteil". Das
  Nutzerurteil nach dem Ingame-Test steht in keiner Datei (ANNAHME:
  muendlich). Ein Vorkommen; AK-314 wurde am 1.14.0 nachbelegt (T-293b 3a-3c).
- **Werkzeugbefunde im QA-Register** (Beobachtung Zyklus 26): QA-283 kommt
  dazu (P2, Adressat developer, offen seit 17.09.); NH-007 schliesst es.
  Bleibt Beobachtung.

---

## Sitzung A25-A27 — 2026-09-21 (Nutzerauftrag, Messung am Transkript-Export)

**Datengrundlage:** Export der Sitzung "Skill Attack und Spell Power
Optimierungen" (19.09. 13:35 bis 21.09. 17:39 UTC, 69 Agentenlaeufe,
3 797 Werkzeugaufrufe, 858 Agentenminuten), `~/.claude/state/*.log`,
`git log 8d8546e..8eb0517`. Zahlen sind Kontextvolumen je Lauf (cache read +
cache creation), gezaehlt je Nachrichten-ID.

### NH-010 — Die Release-Kette ist der groesste Posten, und sie lief fix statt nach Ausloeser

**Messung (458 M Kontext gesamt):** Bau A25/A26/A27 52/81/54 M (41 %);
Pruefung + Release 1.16.0 100 M (18 Teilauftraege, 3 Builds, 3
Fixschleifen), 1.17.0 84 M (14, 2 Builds), 1.18.0 12 M (6, kurze Kette auf
Nutzerwort) — zusammen 43 %; Director 69 M (206 Zuege auf Fable, davon 55
Commits, 53 Schreibvorgaenge, 15 %).

**Ursachen, je mit Beleg:**
1. `director.md` schrieb je Release sieben Rollen vor: clean-room 2x (12 M),
   power-user 2x (13 M), security 3x auf UI-Text-Diffs (7 M, alle PASS),
   technical-writer 4x (5 M), compliance-Vorlauf 2x (33 Ausgabe-Tokens).
2. QA am Artefakt (T-322e 18 M, T-325h 28 M, 159 Zuege) statt am Quellstand
   (T-327c 6 M); jeder Fix zog einen Neubau nach sich: 6 Builds, 14 M, 45 min.
3. Pruefrollen nacheinander auf drei Builds (Review, QA, power-user in
   1.16.0) statt in einer Nachricht: drei Fixschleifen, zweimal Notes,
   zweimal Guide, rund 30 M.
4. Pruefwuensche sofort gebaut (Startbreite-Ratio 16 M, AK-330 Persistenz
   14 M samt Neubau/Retest/Notes).
5. Fuenf `klein`-Fixlaeufe mit 81-131 Zuegen (67 M); T-327b in der
   Zugschwelle. Orientierung je developer-Lauf 21-52 Zuege vor dem ersten
   Edit, weil Vorgaben als Verweis auf `UI_SPEC.md` (7 516 Zeilen) und
   `ARCHITECTURE.md` (10 150) kamen.
6. `no-window-dispatch.ps1` prueft Woerter statt Rolle: researcher und 2x
   ui-ux-designer abgewiesen, T-324f 76 min Verzug bis der Nutzer seine
   Kopie schloss.
7. Kontraktblock bei 25 von 69 Laeufen fehlend; die Nachforderungsregel
   griff nie (und haette nur gekostet).
8. Nicht beeinflussbar: Netzausfall 19.09. 14:04, architect + Spec verloren
   (6 M, 28 min); Warten auf die zweite Director-Sitzung 66 min.

**Massnahmen (Nutzerentscheidung 21.09.2026, umgesetzt):**
- `commands/director.md`: Release nach Ausloeser-Tabelle (immer nur
  `build+notes` und sync-out); Pruefung am Quellstand, ein Bau nach dem
  letzten Fix, Pruefrollen in einer Nachricht; Pruefwuensche P3/P4 in den
  naechsten Zyklus; Vorlauf nur bei Ausloeser; Vorgaben woertlich im
  Auftrag; `klein` nur mit Datei:Zeile; Kontraktblock nicht nachfordern;
  ein Commit je Phase; Fragebogen mit Zeitbudget und Release-Rhythmus.
- `templates/task.md`: Vorgaben woertlich, "Vorlauf: kein Ausloeser".
- `CLAUDE.md` (Projekt): Ausloeser-Pfade je Pruefrolle.
- `.claude/hooks/no-window-dispatch.ps1`: Rolle vor Wortlaut.
- Nachtrag 21.09. (zweite Messung, ApplicationHelper B-26): Director-Kontext
  wuchs hier 77 k → 506 k je Zug ohne Compaction; `commands/director.md`
  Zyklus Schritt 8: Zyklusende ist Sessionende. Fensterlaeufe als Szenario
  vorgemerkt (`docs/plan-restarbeiten.md` E-4).

**Nutzerseitig (aus der Messung, kein Waechter):** Releases sammeln
(eine Kette statt drei haette rund 100 M gespart); Zeitbudget nennen (am
21.09. fuehrte "eine Stunde" zu Worktrees parallel und kurzer Kette);
Programm schliessen, solange Fensterlaeufe anstehen; keine zweite
Director-Sitzung auf demselben Repo; Director-Sitzung auf Opus, Fable nur
per Dispatch fuer compliance und Diagnose.

**Wirkungskontrolle beim naechsten Release:** Kontext der Pruefung +
Release je Feature unter 20 M (Massstab 1.18.0: 12 M), Builds je Release 1,
Fixschleifen je Release 1.

