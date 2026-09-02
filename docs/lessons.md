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

**Erfolgskriterium:** Kein Abschlussbericht eines `developer` benennt "ein Branch pro Task" künftig noch als für ihn unerfüllbare Vorgabe.

**Status:** vorgeschlagen

### L-004 — Auftragsdatei-Pflicht (Zyklus-2-Prozessfehler) wirkt weiter, hiermit formal verankert

**Belege:** Siehe Wirkungskontrolle oben. `docs/tasks/T-017.md` bis `T-020.md` existieren, im Gegensatz zu den in Zyklus 2 ohne Auftragsdatei vergebenen T-008 bis T-012 und T-016.

**Ursache:** Entfällt — keine offene Ursache, die Massnahme wirkt bereits.

**Massnahme:** Keine neue Textänderung nötig. Diese Lessons-Datei verankert die Regel erstmals formal, damit sie nicht von einer zukünftigen Retrospektive erneut "neu entdeckt" werden muss: *Jeder nicht-triviale Auftrag bekommt eine Datei unter `docs/tasks/`, bevor er dispatcht wird.*

**Erfolgskriterium:** Bleibt in den nächsten zwei Zyklen ohne Ausnahme bestehen.

**Status:** übernommen (2026-09-02, rückwirkend dokumentiert — wirkt nachweislich seit Zyklus 3)

### Beobachtungen (noch kein Muster)

- **DEBT-001, Testsockel-Behauptung ungeprüft (einmalig, 2026-09-02):** `tests/conftest.py` nahm den Snapshot-Cache, wenn er existierte — dadurch liefen `fmg`, `bnd4`, `dvdbnd`, `tpf`, `tae` in jedem grünen Lauf seit Zyklus 2 gar nicht. Die Aussage "Testsockel steht" (Zyklus-2-Abschluss, `docs/state.md`) war dadurch ungeprüft, nicht falsch — aber sie klang wie ein Beleg. Bislang ein Einzelfall. Kandidat für eine künftige Massnahme, sobald ein zweites Mal eine Abdeckungsaussage ("N Tests", "Sockel steht") auftaucht, ohne zu nennen, welche Codepfade der grüne Lauf tatsächlich durchlief: dann eine Regel, dass jede Abdeckungsaussage im Abschlussbericht/`docs/state.md` benennt, welcher Testlauf welchen Pfad wirklich ausführt — nicht nur, wie viele Tests grün sind.
- **Director-Ersteinschätzung ohne Fachbeleg, einmalig (SEC-016, 2026-09-02):** Der Director wollte SEC-016 aufgrund einer eigenen Vermutung zur Erreichbarkeit hochstufen; der `security-reviewer` widerlegte das mit zwei Fakten (von einem Savefile aus nicht erreichbar, läuft nur beim Erststart). Bewusst **kein** Muster mit den beiden anderen vom Director selbst genannten Fällen (QA-034-Vereinfachung, T-019-Restlücke) zusammengelegt — die sind andersartig (Design-Abwägung bzw. Risikorechnung, keine technische Tatsachenbehauptung). Bewertung dieser Retrospektive: Das ist die Fachrolle, die genau die Aufgabe erfüllt, für die sie da ist. Die Korrektur geschah, bevor Schaden entstand, und kostete nur eine Textzeile — gesundes Delegieren, kein Zeichen verfrühter Entscheidungen. Kein Handlungsbedarf, solange es dabei bleibt.
