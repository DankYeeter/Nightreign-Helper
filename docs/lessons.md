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
