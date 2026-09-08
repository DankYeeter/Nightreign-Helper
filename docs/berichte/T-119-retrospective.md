# T-119 — Retrospektive Zyklus 16 (retrospective)

STATUS: erledigt
AUFTRAG: T-119 — Retrospektive Zyklus 16
GELESEN: docs/tasks/T-119.md · GOAL.md · docs/state.md · docs/lessons.md ·
docs/plan-restarbeiten.md · CLAUDE.md · qa/findings.md (QA-198 ff.) ·
security/findings.md · docs/legal/C-003.md, C-004.md, AUFLAGEN.md ·
docs/tasks/T-104 bis T-118 (15 Dateien) · docs/berichte/T-104 bis T-117
(14 Dateien) · docs/berichte/T-062-retrospective.md · docs/archiv/ ·
Git-Historie des Projekts (seit 2026-09-07 21:35) und des Agenten-Repos
`C:/Users/Daniel/claude-agent-team` · ~/.claude/agents/_rahmen.md und alle 15
Rollendefinitionen (Frontmatter: tools, model) · ~/.claude/commands/director.md
· ~/.claude/templates/task.md · ~/.claude/settings.json · ~/.claude/hooks/
(check-handoff.ps1, remind-rules.ps1, set-dispatch-model.ps1) ·
~/.claude/state/ (dispatch-modell.log, kontrakt-verstoesse.log,
zugschwelle.log)
GEÄNDERT: docs/lessons.md (fortgeschrieben, Zyklus-16-Abschnitt mit L-014 bis
L-018) · docs/berichte/T-119-retrospective.md (diese Datei). Sonst nichts —
keine Agentendefinition, kein Anwendungscode, nichts unter nrplanner/, tests/
oder docs/perf/.
ANNAHMEN: (1) Zyklus 16 ist das Zeitfenster 2026-09-07 21:38 (`1b00eb6`) bis
2026-09-08 09:12 (`945ddc0`); ich habe es aus den Commit-Botschaften
abgeleitet, nicht aus einer Angabe. (2) Die Protokolle unter ~/.claude/state/
tragen kein Projektfeld; Eintraege habe ich ueber Rolle und Uhrzeit zugeordnet
und nur dort verwendet, wo die Zuordnung eindeutig ist. (3) T-118
(`performance-tuner`) laeuft noch; sein Bericht ist in dieser Retrospektive
nicht enthalten.
NÄCHSTER: director — die Massnahmen L-014 bis L-018 sind Vorschlaege und
brauchen die Freigabe des Nutzers; L-014, L-015, L-017 und L-018 aendern
Dateien im Agenten-Repo, die ich nicht anfassen darf.
BLOCKIERT DURCH: nichts.

---

## 1. Antwort auf die Kernfrage

**Ja — die fuenf Statusfehler und die falsche Praemisse haben dieselbe Ursache,
und es sind nicht sechs Faelle, sondern acht.** Ich habe alle sieben Belege des
Auftrags nachgeprueft; zwei davon stimmen nicht so, wie sie dort stehen, und
dabei sind zwei weitere Faelle derselben Klasse aufgefallen.

Die Vermutung des Auftrags — "der Director fuehrt Befunde und Stand in Dateien,
die er selbst pflegt, und liest sie dann als Tatsache zurueck" — **trifft die
Form, nicht die Ursache.** Denn:

> **Die Regeln, die alle acht Faelle verhindert haetten, standen bereits
> woertlich in `~/.claude/commands/director.md`, bevor der Zyklus begann.**

- *"Ein Befundstatus wird geprueft, nicht erinnert. … Die Statuszeile in
  `qa/findings.md` ist eine Notiz, kein Messwert"* — Zeile 1019, eingefuegt
  **07.09. um 18:35** (`9b2c986` im Agenten-Repo). Zyklus 16 begann um 21:38.
  Die Regel war **drei Stunden alt** und wurde im selben Zyklus fuenfmal
  gebrochen.
- *"Absenz-Behauptungen brauchen eine Durchsicht, keinen Grep"* — Zeile 1038,
  seit **02.09.** Zweimal gebrochen (`AUFLAGEN.md`, "keine EXE").
- *"Eine Regel aus wenigen Beispielen ist eine Hypothese, keine Tatsache"* —
  Zeile 1047, seit **02.09.** Zweimal gebrochen (QA-198, "dreizehn Auftraege").

Die Frage ist also nicht "wo kann die Wahrheit sonst herkommen" — die Antwort
darauf steht schon da (`git log -S`, `ls`, `gh release list`, die
Rollendefinition). Die Frage ist: **warum wird eine Regel, die richtig
formuliert und richtig adressiert ist, nicht ausgefuehrt?**

**Weil sie an keinem Punkt des Ablaufs ausgeloest wird.**
`commands/director.md` ist von **355 Zeilen (01.09.) auf 1085 Zeilen (08.09.)**
gewachsen; die drei Saetze stehen in einem Fliesstextkapitel ab Zeile 1019, das
die Sitzung **einmal beim Aufruf** liest. Nichts verbindet sie mit dem Moment,
in dem der Director einen Befundstatus schreibt, `docs/state.md` fortschreibt
oder einen Auftrag verfasst.

**Der Gegenbeweis liegt im selben Repo und ist die tragende Messung dieser
Retrospektive.** Die Regel "`model: sonnet` beim QA-Retest" stand seit dem
03.09. als *"Pflicht, nicht Option"* im Fliesstext des Directors. Gemessen:

| Fassung | Wirkung |
|---|---|
| Regel im Fliesstext (bis 06.09.) | in **49** QA-Laeufen **nie** angewandt; von 21 Retest-Auftraegen trugen **13** kein `model: sonnet` |
| dieselbe Regel als Hook (`set-dispatch-model.ps1`, ab 06.09.) | **4 von 4** Retests korrekt herabgestuft — `~/.claude/state/dispatch-modell.log`. Der Director hat das Modell in **0 von 4** Faellen selbst gesetzt (zweimal "(Standard)", zweimal "opus") |

Derselbe Text, derselbe Adressat, derselbe Zweck. Der Unterschied ist
ausschliesslich der **Ort und der Ausloeser**. Daraus folgt die eine Massnahme,
die ich zuerst haette (Abschnitt 4).

## 2. Die sieben Belege des Auftrags, nachgeprueft

| # | Beleg | Ergebnis der Nachpruefung |
|---|---|---|
| 1 | fuenf falsche Befundstatus | **bestaetigt** (`1b00eb6`, `41fba5a`). Die Commit-Botschaft nennt sie selbst "dieselbe Klasse wie die Statuskorrektur nach T-095" — es ist also nicht der erste Zyklus mit dieser Klasse. `AUFLAGEN.md` liegt seit `9631cbb`, **02.09. 01:31**. |
| 2 | falsche Praemisse "keine EXE" | **bestaetigt und groesser als angegeben.** Sie steht in **vier** Auftragsdateien (T-104, T-105, T-106, T-107), nicht drei — und schon in T-095 aus Zyklus 15, dessen `qa-engineer`-Bericht sie als Tatsache uebernahm. `C-003.md` ist **867** Zeilen (im Auftrag: 850), die Nacharbeit `C-004.md` **558** Zeilen. |
| 3 | QA-198 als Tatsache geschrieben | **bestaetigt.** Die Korrektur des Directors steht vorbildlich im Befundtext — **die Ueberschrift traegt die widerlegte Aussage bis heute** ("dauert fuenfmal so lange"). Siehe L-016. |
| 4 | unvollstaendige Isolierung | **bestaetigt** (`a2980bf`). Die zwei Umlenkungen stammten aus dem T-111-Bericht; `nrplanner/shortcut.py:44-49` und die `README` nennen drei. Gleiche Klasse wie 1 und 2: Sekundaerquelle statt Primaerquelle. |
| 5 | `power-user` legte Bericht trotz Schreibrecht nicht ab | **falsch — und selbst ein Fall derselben Klasse.** `~/.claude/agents/power-user.md` fuehrt in `tools:` **kein** `Write` und **kein** `Edit`; der Fliesstext sagt "**Du schreibst keine Datei.** … abgelegt wird er vom `director`". `commands/director.md` (L-010, Pruefung 3) klassifiziert ihn selbst als Rolle ohne Write. Die Rolle hat sich **regelkonform** verhalten; der Director hat richtig gehandelt, als er den Bericht ablegte. **Die falsche Begruendung steht seit 08.09. 10:04 in `CLAUDE.md`** (`9f438f9`) — der Datei, mit der der naechste Zyklus startet. Wenn der Director ihr glaubt, legt er den naechsten `power-user`-Bericht **nicht** mehr ab, und der Bericht ist dann ganz weg. |
| 6 | `docs/state.md` sechsmal umgeschrieben, viermal fuers Zeilenbudget | **falsch, es war mehr: 10 Commits, 5 davon ausschliesslich fuers Budget** (`bc460d6`, `207257a`, `98d9740`, `732ee4c`, `93b01e9`), zusammen +278/−263 Zeilen an einer Datei von 142 Zeilen — **die das 120-Zeilen-Budget am Ende trotzdem um 22 Zeilen ueberschreitet.** Siehe L-017. |
| 7 | Netzabbruch und Wiederanlauf | **bestaetigt, und er war billig.** Verloren ging nur der erste Lauf (kein Bericht, keine Commits, `git status` sauber — vom Director **am Dateisystem** geprueft, vorbildlich und genau die Primaerquellenpruefung, die anderswo fehlte). Teuer war nicht der Abbruch, sondern die Spur, die er hinterliess: eine Verknuepfung im **echten** Start-Menue. Verkleinern wuerde ihn der feste Testabzug (E-1, 107 s bis 5 min je Artefaktstart) — **die Ersparnis ist noch nicht gemessen.** |

**Zwei zusaetzliche Faelle derselben Klasse, die ich beim Nachzaehlen gefunden
habe:** "dreizehn Auftraege (T-104 bis T-118)" — es sind **15** (`ls
docs/tasks/`), und die Zahl steht im Auftragstext dieser Retrospektive selbst;
sowie Beleg 5 oben. Damit acht Vorkommen in einem Zyklus, alle derselben Form.

## 3. Wirkungskontrolle — gezaehlt, nicht geschaetzt

**Sieben von neun geprueften Massnahmen wirken, eine wirkt nur zur Haelfte, eine
wirkt nur als Hook.** Vollstaendige Tabelle mit Belegen in `docs/lessons.md`.

- **L-008** (Gegenbau muss beissen) — **wirkt**, 1 von 1 neuen Waechtern (T-109)
  erfuellt alle drei Bedingungen ohne Aufforderung.
- **L-009** (Messumgebung) — **wirkt**; die Umgebungsspalte in QA-198 ist der
  Grund, warum die Spanne ueberhaupt als Befund sichtbar wurde.
- **L-010** (fuenf Pruefungen) — **drei wirken, eine kippt, eine ist gebrochen.**
  P1/P3/P5 gehalten. P4 (woertliches Zitat) formal erfuellt (12 von 15
  Auftragsdateien) — **und genau dieser Kanal hat die falsche Praemisse in vier
  Auftragsdateien getragen**; siehe L-015. P2 (Werkzeug) zum **vierten** Mal
  ausgefallen (T-113 ohne GUI-Automatisierung), diesmal ohne Laufverlust.
- **L-011** — kein neuer Fall dieser Bauform; bleibt ohne Massnahme.
- **L-012 / NH-002** (Bildnachweise aus dem Fenster) — **wirkt**; T-114 nutzt
  `PrintWindow` auf das eigene HWND, **0** neue Dateien unter `docs/screenshots`.
- **L-013** (Absenz traegt ihren Nenner) — **wirkt bei den Rollen, nicht beim
  Director.** T-113: "Kein CHANGELOG.md (geprueft: git-weite Suche nach
  CHANGELOG*, kein Treffer)". Director: zwei Absenz-Behauptungen ohne Nenner,
  beide falsch. Der Unterschied ist der **Ort**: L-013 steht in den
  Rollendefinitionen und in `_rahmen.md` — und `_rahmen.md` bindet den Director
  nicht (`commands/director.md:520` verweist andere darauf, uebernimmt es nicht).
- **NH-001** (Auftragsdatei je Auftrag) — **wirkt, 15 von 15**, auch bei den
  zwei kleinsten Auftraegen.
- **Parallele Pruefphase** — **wirkt**: drei gleichzeitige Paare, kein
  gemeldeter Verlust, ein korrekt gemeldeter Fremdprozess (T-114).
- **`model: sonnet` beim Retest** — **wirkt nur als Hook** (4 von 4 gegen 0 von
  4 durch den Director). In Zyklus 16 gab es keinen Retest, also keinen neuen
  Datenpunkt; die Zahlen stammen vom 06./07.09.

## 4. Massnahmen — fuenf, getrennt nach Ort

**Die eine, die ich zuerst haette: L-014.** Sie ist eine geaenderte Zeile in
einer Datei, die bei jedem Prompt ausgefuehrt wird, sie kostet nichts, und die
Bauform ist im selben Repo bereits belegt (0 von 21 als Text, 4 von 4 als Hook).
Alle anderen kosten mehr und wirken weniger.

### Teamweit — Agenten-Repo `claude-agent-team`, Freigabe durch den Nutzer

| ID | Zieldatei | Was | Wer liest es wann |
|---|---|---|---|
| **L-014** | `hooks/remind-rules.ps1` (`$rules`) | Die Sorgfaltspflicht des Directors wandert aus dem Fliesstext (Zeile 1019 ff.) in den `UserPromptSubmit`-Hook: Notiz ≠ Messung, Primaerquelle nennen, Absenz braucht eine genannte Suche, eine Beobachtung ist keine Regel. **Exakter Textvorschlag in `docs/lessons.md`.** | Der Director, bei **jedem** Prompt des Nutzers. Einzige Stelle, die er oefter als einmal je Sitzung liest. |
| **L-015** | `commands/director.md`, Pruefung 4 ("Zitat") | Ein angehaengter Absatz: Zitierte **Tatsachenbehauptungen ueber den Bestand** tragen ihre Quittung in Klammern (Befehl + Datum). Ohne Quittung ist es eine Annahme und wird als solche gekennzeichnet, mit ausdruecklichem Widerspruchsrecht der Rolle. | Der Director unmittelbar vor jedem Dispatch — Pruefung 4 ist eine Checkliste im Ablaufteil, nicht Fliesstext. |
| **L-017** | `agents/_rahmen.md`, neuer Abschnitt "Regeln pflegen" | Jede neue Regel nennt ihren **Ausloeser**; ohne Ausloeser gehoert sie in Vorlage, Checkliste oder Hook. Wer eine Regel einfuegt, nennt die, die dafuer entfaellt. Dazu die konkrete Textaenderung: Zeilenbudget fuer `docs/state.md` wird **einmal am Zyklusende** geprueft (`commands/director.md:76` und `:113`). | Der, der gerade eine Regel schreibt — er hat die Datei in dem Moment offen. Ehrliches Risiko: der Abschnitt teilt die Schwaeche, die er beschreibt; deshalb ist die messbare Haelfte als Textaenderung darin. |
| **L-018** | `agents/_rahmen.md` (im selben Abschnitt) + 3 Hook-Kommentare | L-Zitate nennen ihre Herkunft. Ohne Praefix = teamweiter Satz; projekteigen = Projekt-Praefix (`NH-001`); fremd = Projekt davor (`bt-codec L-005`). Heute stehen `L-022` bis `L-026` ohne Praefix in `check-handoff.ps1:109`, `limit-tool-calls.ps1:90`, `selftest.ps1:376` und zeigen auf die `lessons.md` eines anderen Projekts. | Jede Rolle liest `_rahmen.md`; entscheidend ist der Moment des Zitierens. |

### In diesem Projekt — sofort umsetzbar, ohne Freigabe des Agenten-Repos

| ID | Zieldatei | Was |
|---|---|---|
| **L-016 (a)** | `CLAUDE.md`, Abschnitt "Der Bericht ist Teil des Auftrags" | Die falsche Begruendung ersetzen: Rollen **ohne** `Write` (`power-user`, `qa-engineer`, `security-reviewer`, `archivist`, `fehlerdiagnostiker`) liefern in der Antwort, der Director legt ab. Der T-115-Nachtrag war **richtig**, keine Verfehlung der Rolle. **Exakter Ersatztext in `docs/lessons.md`.** |
| **L-016 (b)** | `qa/findings.md`, Ueberschrift QA-198 | "Der Erstaufbau dauert unvorhersagbar lange (107 s bis 5 min), das Programm sagt 'etwa eine Minute'" statt "dauert fuenfmal so lange". |

**Verworfen, mit Begruendung:** eine eigene Massnahme zu Pruefung 2 (Werkzeug,
vierter Ausfall). Die Regel steht seit dem 06.09. vollstaendig da, samt
Faehigkeitsprobe — sie wurde nicht ausgefuehrt. Ein sechster Regelsatz zur
selben Sache waere genau der Fehler, den L-017 beschreibt. Der Fall steht als
Beobachtung mit Ausloeser in `docs/lessons.md`.

## 5. Was gut lief und geschuetzt werden sollte

- **Die parallele Pruefphase und die parallele Suite.** 840 s → 127 s, drei
  gleichzeitige Rollenpaare ohne einen einzigen gemeldeten Verlust. Das hat den
  Volllauf zurueck in den Vordergrund geholt und die teuerste Abbruchklasse
  ("Lauf stirbt im Hintergrundwarten") fuer dieses Projekt geschlossen.
- **Rollen widersprechen dem Auftrag mit einer Messung, nicht mit einer
  Meinung.** T-113 hat die dritte Umlenkung eingefordert; T-115 hat eine Zahl
  gemessen, die einen frisch eingetragenen Befund widerlegte, und sie berichtet
  statt sie an den Bestand anzupassen; T-114 hat einen Fremdprozess gemeldet.
  **Alle drei Korrekturen dieses Zyklus kamen von Rollen, keine vom Bestand.**
- **Der Director protokolliert seine eigenen Fehler** — in `docs/state.md`
  ("Buchfuehrung des Directors"), im Kopf von `T-115-power-user.md`, in der
  Korrektur unter QA-198. **Ohne diese Selbstprotokolle waere diese
  Retrospektive nicht moeglich gewesen.** Das ist die wertvollste Gewohnheit
  des Zyklus, und keine der fuenf Massnahmen darf sie unattraktiv machen: keine
  von ihnen zaehlt Fehler, alle vier teamweiten aendern nur den **Ort** einer
  bereits beschlossenen Regel.
- **NH-001 (15 von 15), L-008 (1 von 1), L-012 (0 Bildschirmabzuege), L-013 bei
  den Rollen** — vier Regeln, die ohne Aufwand halten und nicht angefasst werden
  sollten.

## 6. Ablage

`docs/lessons.md`, Abschnitt "Zyklus 16 — 2026-09-08": Wirkungskontrolle,
L-014 bis L-018 mit exakten Textvorschlaegen, Kosten und Erfolgskriterien,
sowie vier Beobachtungen ohne Massnahme.
