STATUS: erledigt
AUFTRAG: T-286 — Retrospektive Zyklus 26 (Part 12, Stand `c615b6c`)
GELESEN: GOAL.md, docs/state.md (`c615b6c`), docs/lessons.md (L-001..L-020, NH-003), docs/berichte/T-283-qa-engineer.md, T-285-release-manager-clean-room.md, T-285-power-user.md, T-241d/T-265/T-272/T-275-power-user.md, T-241-/T-265-release-manager-cleanroom.md, docs/tasks/T-277.md, T-281.md, T-283.md, T-284.md, qa/findings.md (QA-256, QA-279, QA-282), docs/release/ROLLOUT.md:305-318, CLAUDE.md, .claude/hooks/enforce-data-redirect.ps1, .claude/settings.json, ~/.claude/agents/_rahmen.md, power-user.md, commands/director.md, templates/task.md, hooks/limit-tool-calls.ps1, ~/.claude/settings.json, ApplicationHelper/docs/lessons.md (teamweites Register, endet L-033), git log 79664c2..c615b6c
GEÄNDERT: docs/lessons.md (Zyklus 26 angehaengt, Z. 1503-1847: Nummernraum-Befund, Gut gelaufen, Wirkungskontrolle, NH-004..NH-006, Beobachtungen), docs/berichte/T-286-retrospective.md (neu). Kein Commit.
ANNAHMEN: Der T-285-Dispatchtext liegt nicht auf Platte; "parallel mit eigener Umlenkung" stammt aus dem ANNAHMEN-Feld des clean-room-Berichts. Ob T-285b Prozess und Koordinaten gemischt hat, ist nicht belegbar (Werkzeugzeile nennt beides nicht) — die Erklaerung fuer QA-279/QA-282 ist plausibel, nicht bewiesen.
NÄCHSTER: director — die drei Vorschlaege dem Nutzer vorlegen; QA-256 Abschlusszeile anhaengen; Retrospektive-Dispatches kuenftig mit "Projektnummern NH-".
BLOCKIERT DURCH: nichts

# T-286 — Retrospektive Zyklus 26

Belege, Ursachen, Kosten und Erfolgskriterien stehen in `docs/lessons.md`
ab Z. 1506. Hier nur, was der Nutzer freigibt.

## Nummernraum (Befund, keine Massnahme noetig)

Das teamweite Register (`ApplicationHelper/docs/lessons.md`) endet bei
L-033; L-019/L-020 dieser Datei (12.09.) kollidieren mit dessen L-019/L-020
vom 06.09. Deshalb hier `NH-004..006` statt "L-Nummern fortsetzen"
(`_rahmen.md:113`). Vorschlaege, die Teamtext aendern, sind als "Kandidat
teamweit" markiert; L-034 ff. vergibt nur, wer das Register dort fortschreibt.

## Wirkungskontrolle

Acht geprueft, sechs wirken (L-031 Klon-Volllauf 1/1, OF-35 vierte Anwendung,
L-019, L-020, NH-002, NH-003), zwei nicht: **NH-001 tot** (5 von 23
Auftragsnummern seit T-263 mit Datei; T-285 mit drei Rollen ohne Datei) und
**QA-256-Prozessregel** ohne Ort, den der Director vor einem Dispatch liest.

## Vorschlag 1 — NH-004: Riegel gegen den zweiten Fensterlauf (Projekt)

**(a) `.claude/hooks/enforce-data-redirect.ps1`**, einfuegen nach Z. 78
(`if (-not ($istQuellstart -or …)) { exit 0 }`) — Codeblock woertlich in
`docs/lessons.md` Z. 1626-1645: bei laufender Kopie (`Get-Process
NightreignHelper`, oder `python`/`pythonw` mit Fenstertitel `Nightreign
Helper*`) wird ein Start abgewiesen; Meldung nennt PID und Startzeit und
verlangt `STATUS: blockiert` statt Warten. Nur fuer Startformen, in denen
die EXE das Kommando ist (neue Maske `$istExeKommando`); Hash- und
`ls`-Aufrufe bleiben frei. Wer einbaut, zeigt einmal das `deny`.

**(b) `CLAUDE.md`**, Abschnitt "Datenverzeichnisse und Umlenkung", nach
dem Absatz "Plattformgrenze (QA-241 …)":

> **Ein Fensterlauf je Zeitpunkt (QA-256, NH-004):** Die Instanzsperre ist
> maschinenweit (`nrplanner/singleinstance.py`, `KEY`); ein zweiter Start
> endet stumm, der Hook weist ihn ab, solange eine Kopie laeuft.
> `qa-engineer` am Artefakt, `power-user` und `release-manager` `clean-room`
> stehen im Auftrag in einer Reihenfolge, nie unter `Parallel: ja`;
> `notes`, `security-reviewer`, `compliance-agent` duerfen parallel.

**Streichung:** QA-256 bekommt eine Abschlusszeile; `ROLLOUT.md:309-312`
auf "siehe CLAUDE.md" kuerzen. **Verworfen:** ein vierter Grund in
`commands/director.md:235` — kein Beleg ausserhalb dieses Projekts, und die
Liste ist abschliessend formuliert (Begruendung in lessons.md).

## Vorschlag 2 — NH-005: Klickrezept in `~/.claude/agents/power-user.md` (Kandidat teamweit)

Z. 186-189 ersetzen durch:

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

**Streichung dafuer**, Z. 93-97 ("**Belegt am 06.09.2026:** … blieb
offen.") wird zu: "(Belegt 06.09.2026: ein voller Durchgang, sechs Ziele,
kein angekommener Klick.)" Netto +5 Zeilen. Grund, warum nur dort: der
Director darf dem `power-user` laut `director.md:194-195` nichts als
Persona, Ziele, Zugang geben, und der `power-user` traegt keinen Kontext
in den naechsten Lauf — die Definition ist die einzige Datei, die er liest.

## Vorschlag 3 — NH-006: Waechter statt NH-001 (Team-Repo)

Neuer Hook `~/.claude/hooks/require-task-file.ps1`, `PreToolUse`, Matcher
`Agent|Task`, registriert in `~/.claude/settings.json`: hoechste `T-###` im
Dispatch-Prompt; fehlt `docs/tasks/T-###.md` (und existiert `docs/tasks/`),
`deny` mit Vorlagenbefehl `cp ~/.claude/templates/task.md docs/tasks/T-###.md`.
Dispatch ohne Nummer passiert. **Streichung:** `docs/plan-restarbeiten.md:205-207`
(NH-001-Prosa) wird zur Einzeile "NH-001: Waechter `require-task-file.ps1`".

## Beobachtungen (kein Muster, keine Massnahme)

Heredoc mit EXE-Namen vom Umlenkungs-Hook gesperrt — **zweites Vorkommen**
(Director 16.09., diese Retrospektive beim Anhaengen); die engere Maske aus
Vorschlag 1 (a) wuerde den Fehlalarm beheben, wenn sie auch die Umlenkung
prueft — beim dritten Mal die Massnahme. Werkzeugbefunde im QA-Register
(QA-241/256/271/279/282). T-285a pollte 28 min statt `blockiert`
(zweites Vorkommen nach T-241). UIA fand Heldenkacheln nicht (T-283a).

## Gut gelaufen, schuetzen

88 min von AK-313 bis Release-Run mit voller Pruefkette (SEC-048 gefunden
und in 12 min behoben) · T-285a beendete keinen fremden Prozess (QA-256-
Nachtrag hielt) und schrieb sein Werkzeugrezept auf · T-283a erklaerte
1729 → 1727 exakt · der Director nannte seinen Planungsfehler im Commit und
legte die Lehren in `docs/state.md` ab · L-031 trug beim ersten Einsatz.
