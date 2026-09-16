STATUS: erledigt
AUFTRAG: T-209 — Retrospektive zu Zyklus 20
GELESEN: docs/tasks/T-209.md · GOAL.md · docs/state.md (beide Fassungen dieses Laufs, `7c3a260` und `98cdf61`) · CLAUDE.md **von der Platte** (159 Zeilen, `HEAD:CLAUDE.md` gegengeprueft — die Fassung in meinem Kontext war zwei Commits alt) · docs/lessons.md (L-001 bis L-018 vollstaendig) · docs/plan-restarbeiten.md (P10, Korb 1/2, Bilanzabschnitte, "Regeln fuer jeden Schritt", "Nummernkreise") · qa/findings.md (QA-224 bis QA-243) · security/findings.md (SEC-036 bis SEC-042) · DESIGN_REVIEW.md (DR-019 bis DR-021) · die 12 Berichte docs/berichte/T-196 bis T-208 · die 13 Auftragsdateien docs/tasks/T-196 bis T-208 · docs/tasks/T-210.md · docs/archiv/berichte/T-119-retrospective.md · ~/.claude/agents/_rahmen.md · ~/.claude/agents/{architect,developer,qa-engineer,performance-tuner,researcher,security-reviewer,ui-ux-designer,retrospective}.md · ~/.claude/commands/director.md · ~/.claude/hooks/*.ps1 (Koepfe, selftest.ps1 im Detail) · ~/.claude/settings.json · ~/.claude/settings.json.bak-bootstrap · claude-agent-team (Repo-Wurzel, git log) · git log/git show beider Repositorien · tests/ (Suche nach .md-Pfadliteralen) · scripts/ (QT_QPA_PLATFORM)
GEÄNDERT: docs/lessons.md (angefuegt, Abschnitt "Zyklus 20 — 2026-09-12", **uncommittet im Baum**) · docs/berichte/T-209-retrospective.md (diese Datei). Keine Agentendefinition, keine CLAUDE.md, kein Code, kein Commit, kein Git-Zustand veraendert.
ANNAHMEN: (1) L-019 und L-020 sind als **teamweite** Nummern gemeint — der Auftrag sagt "Massnahmen ab L-019", die projekteigene Reihe in docs/lessons.md endet bei L-018, und im teamweiten Satz (Rollendefinitionen) ist nach L-013 alles frei; beide Nummern kollidieren mit nichts. (2) Die dritte Massnahme ist projekteigen und traegt deshalb **NH-003**, nicht L-021 — so verlangt es der NH-Beschluss vom 05.09. in docs/plan-restarbeiten.md. (3) Als Zyklus 20 habe ich T-196 bis T-208 gerechnet (13 Auftraege, 12 Berichte), wie der Auftrag es vorgibt.
NÄCHSTER: director
BLOCKIERT DURCH: nichts. Drei Freigaben liegen beim Nutzer (L-019, L-020 beruehren das Agenten-Repo; NH-003 ist projekteigen und beauftragbar).

---

# Retrospektive Zyklus 20

## 1. Wirkungskontrolle zuerst — das wichtigste Ergebnis

**Neun Massnahmen geprueft. Vier wirken unverkuerzt, zwei wirken an der
Fundstelle und nicht an der Klasse, zwei wirken nicht durchgaengig, eine hat
ihren Ausloeser erreicht und wird faellig.** Die vollstaendige Tabelle mit
Belegen steht in `docs/lessons.md`, Abschnitt "Zyklus 20". Die zwei, nach
denen der Auftrag ausdruecklich gefragt hat:

**L-009 wirkt — und der Beleg ist staerker, als der Auftrag annimmt.** Die
Beobachtung 7 lautet, L-009 sei "wieder aufgelaufen". Die Quellen sagen etwas
anderes: die **Falle** trat wieder auf, der **Fehler** nicht. T-199 hat sie
selbst erkannt (erster Lauf offscreen 278/271/278 px und `wanted_height` 1203,
zweiter Lauf nativ 228 px und die Vorgabe exakt), hat die Umgebungszeile
geliefert und schreibt den Satz, auf den es ankommt: *"Ohne diese Gegenprobe
haette ich eine falsche Zahl gemeldet."* **Der Auftrag war daran unbeteiligt** —
`docs/tasks/T-199.md` nennt L-009 **null** Mal, der Bericht **drei** Mal; die
Regel steht in `agents/developer.md:356`. Auch die zweite Haelfte der
Beobachtung traegt nicht: L-009 erscheint in **2 von 12** Auftragsdateien des
Zyklus (T-201, T-207), nicht "ab T-201 in jedem". **Offen ist die mechanische
Haelfte:** T-060 hat `tests/conftest.py` an `apply_appearance` gebunden, nicht
die Messskripte — **fuenf** Dateien setzen `QT_QPA_PLATFORM=offscreen` als
Vorgabe, drei davon messen Geometrie, und `measure_picker_cards.py` ruft
`apply_appearance` **und** laeuft offscreen. Stil geschlossen, Plattform offen.

**L-016 wirkt an der Fundstelle und verfehlt ihr eigenes Erfolgskriterium —
durch die Korrekturen selbst.** Beide Textaenderungen sind umgesetzt (die
QA-198-Ueberschrift, der `CLAUDE.md`-Absatz). Und in vier Tagen gibt es vier
Wiederholungen derselben Klasse, drei davon **in** den Korrekturen:

| # | Wo | Was |
|---|---|---|
| a | der **neue** Wortlaut aus L-016 (a) | fuehrte den `qa-engineer` unter den Rollen ohne `Write` — falsch, korrigiert erst am 12.09. (`de710a5`) |
| b | L-018s Umsetzung | gab drei Hook-Kommentaren das Praefix `Nightreign-Helper`, obwohl `L-022` bis `L-026` hier nicht existieren |
| c | `qa/findings.md` | am Tag der Reparatur von vier kaputten Zeilen ist eine fuenfte entstanden (QA-240, Zeile 263) |
| d | `docs/tasks/T-205.md`, 21:30 | *"der Bericht liegt ab"* — `docs/berichte/T-205-archivist.md` existiert nicht |

L-016 wird **nicht zurueckgenommen** (die Textaenderungen waren richtig). Die
Klasse bekommt statt weiteren Regeltexts einen Adressaten: L-019 und NH-003.

## 2. Die Frage des Auftrags — war es Zufall oder fehlt eine Regel?

**Der Satz "Widersprich, wenn der Auftrag nicht stimmt" ist als Beleg
wertlos — nicht falsch, sondern ohne Kontrast.** Er steht in **12 von 12**
Auftragsdateien des Zyklus und seit T-180 in **30 von 30** aufeinanderfolgenden
Auftraegen (`grep -ci`, je Datei einzeln). Es gibt im Zyklus keinen Fall ohne
ihn; "in allen vier Faellen stand er im Auftrag" gilt damit genauso fuer die
acht Faelle **ohne** Korrektur. Gegenprobe nach unten: T-140 bis T-179 tragen
ihn in 4 von 40 Dateien, und aus dieser Strecke liegen mehrere Berichte vor,
die dem Auftrag widersprechen — die Klasse ist aelter als der Satz. **Er
bleibt, weil er eine Zeile kostet; Ursache ist er nicht.**

**Was die vier Korrekturen wirklich erzeugt hat, sind vier Messpflichten der
Rollendefinitionen:** nachzaehlen (T-197 — `grep`: 15 Treffer, davon zehn
`pytest.raises(ValueError)`, die Director-Aufstellung hatte Zeile 277/283
uebersehen), an der Primaerquelle lesen (T-204 — `goals.py:56` macht
`from . import types`, also Zirkelimport), den Angriffspfad messen (T-202 F6),
am Fenster nachmessen (T-207 — 1121 statt geschaetzter 1136 px). Alle vier
binden die Rolle **unabhaengig vom Auftragstext**.

**Und keine dieser vier Pflichten bindet den Director.** Das ist nicht neu —
es steht wortwoertlich in der Wirkungskontrolle zu L-013 vom 08.09.: *"Der
Unterschied ist nicht Sorgfalt, sondern Ort."* Damals war die Antwort L-014
(`remind-rules.ps1`, registriert und wirksam) und, schaerfer,
`require-receipt.ps1`. **Der ist nicht registriert.** Das ist die fehlende
Regel — und sie fehlt nicht als Text, sie fehlt als Anschluss.

## 3. Die drei Massnahmen

Alle drei stehen ausformuliert mit Wortlaut, Ort, Kosten und Erfolgskriterium
in `docs/lessons.md`. Hier die Kurzfassung mit Ort und Bilanz:

| ID | Muster | Ort (Tabelle der Director-Definition) | Was entfaellt |
|---|---|---|---|
| **L-019** *(teamweit)* | Waechter sind gebaut, geprueft und zum Teil nicht angeschlossen: `require-receipt.ps1`, `no-root-find.ps1`, `remind-sync-out.ps1` liegen als Datei, werden von `selftest.ps1` geprueft und stehen in **keiner** Registrierung | **Hook** — Registrierungspruefung mit `OFFEN`-Liste in `hooks/selftest.ps1`, dazu `CLAUDE.md` in den Wachbereich von `require-receipt.ps1` | nichts, und der Bestand waechst um **null Zeilen Regeltext** — L-019 ist nur Pruefcode |
| **L-020** *(teamweit)* | Das Zeilenbudget von `docs/state.md` haengt an "Zyklusende", einem Moment, den ein autonomer Lauf nicht erkennt: dreimal ueber Budget committet, viermal nachgezogen, **zwei der vier Korrekturen selbst falsch** | **Hook** (`hooks/state-line-budget.ps1`, `PreToolUse` auf `Write|Edit`) + Streichung in der **Director-Definition** | `commands/director.md:71`, der Halbsatz *"geprueft einmal am Zyklusende"* — der Teil, der nachweislich nicht getragen hat |
| **NH-003** *(projekteigen)* | Die Befundtabellen haben keinen Waechter, und die reparierte Klasse ist am Reparaturtag wiedergekommen | **Belegdatei/Test im Projekt** (`tests/test_findings_tables.py`) + ein Spiegelstrich in `docs/plan-restarbeiten.md` | nichts; ein Spiegelstrich — es ist der **erste** Test dieses Projekts, der eine Markdown-Datei anfasst |

**L-019 ist die einzige der drei, die ich als dringend bezeichne**, und zwar
aus einem Grund, der nicht meiner ist: `require-receipt.ps1` ist der Waechter
gegen genau die Bauform der **sechs** Eigenfehler dieses Zyklus, sein eigener
Kopf sagt *"Ein Hook, der ERINNERT, ist Fliesstext mit hoeherer Frequenz.
Dieser hier SPERRT"*, und er hat in diesem Zyklus kein einziges Mal gefeuert,
weil ihn nichts aufruft. `docs/tasks/T-205.md` (*"der Bericht liegt ab"*, Datei
existiert nicht) ist ein Write in eine Auftragsdatei mit einer
Bestandsbehauptung ohne Quittung — genau der Fall, auf den er `deny` antwortet.

**Reihenfolge: L-019 vor L-020.** Ein neuer Hook, der vor der
Registrierungspruefung angelegt wird, landet mit einiger Wahrscheinlichkeit in
derselben Schublade wie die drei, die dort schon liegen.

**Teamweit gegen projekteigen:** L-019 und L-020 sind **Vorschlaege fuer das
Agenten-Repo** (`hooks/selftest.ps1`, `hooks/require-receipt.ps1`, neuer
`hooks/state-line-budget.ps1`, `~/.claude/settings.json`,
`commands/director.md:71`) — nichts davon ist an diesem Projekt spezifisch,
und eine im Projekt angenommene Teamregel ist beim naechsten Projekt wieder
weg. NH-003 ist projekteigen, weil es zwei Dateinamen dieses Projekts nennt.

## 4. Eine Massnahme, die ich verworfen habe — und warum das ein Ergebnis ist

Die L-015-Wirkungskontrolle hat eine Zahl geliefert, die nach einer Massnahme
schreit: in den `GELESEN`-Zeilen der 12 Berichte steht `docs/state.md` **5**
Mal, `GOAL.md` **3** Mal, `CLAUDE.md` **5** Mal — bei drei Dateien, die der
Uebergabe-Kontrakt als Pflicht fuehrt. Die Korrelation zum Auftragstext ist
fast vollstaendig: von den 6 Auftraegen, die `state.md` nennen, nennen 5
Berichte sie; von den 5, die sie nicht nennen, nennt **kein** Bericht sie
(11 von 12).

**Ein Hook, der `GELESEN` gegen diese Dateien prueft, ist verworfen.** Er
pruefte ein Wort, das die bewachte Partei selbst schreibt — dieselbe Bauform,
die L-008 (b) verbietet und die SEC-038 im selben Zyklus als zahnlos belegt hat
(5 von 5 Fundstellen gestubbt). Er erzwaenge die Nennung und sagte ueber das
Lesen nichts; danach waere "12 von 12" kein Messwert mehr, sondern eine
Formalie — und die Zahl, mit der diese Retrospektive L-015 gemessen hat, waere
zerstoert.

**Der belastbare Teil bleibt als Beobachtung:** ein Lauf arbeitet mit dem
Regelsatz, den seine **Rollendefinition** traegt (L-009 hat ohne jede
Erwaehnung im Auftrag gegriffen) plus dem, was sein **Auftrag** nennt. Dateien,
die nur im Uebergabe-Kontrakt stehen, erreichen ihn in weniger als der Haelfte
der Faelle. Wer das aendern will, aendert den Auftrag oder die
Rollendefinition, nicht die Berichtsform.

## 5. Wo ich dem Auftrag widerspreche

Der Auftrag hat sieben Beobachtungen als Material uebergeben und verlangt, sie
gegen die Quellen zu pruefen. **Fuenf halten, zwei tragen nicht, zwei brauchen
eine Praezisierung.**

**Beobachtung 3 — ohne Kontrast, siehe Abschnitt 2.** Der Satz steht in 12 von
12 Faellen; eine Korrelation mit Varianz null erklaert nichts.

**Beobachtung 6 trifft nicht zu.** "Derselbe Sachverhalt, zwei
entgegengesetzte Reaktionen" — die Berichte sagen das Gegenteil. T-196 hat den
Rueckleseversuch **nicht** als Nachweis gemeldet: `STATUS: teilweise`,
`BLOCKIERT DURCH: eine Bestaetigung, dass der kopierte Abzug am realen Zielpfad
tatsaechlich lesbar ist — meine Tools koennen das nicht zeigen`, dazu ein
eigener Abschnitt *"Offener Punkt, nicht geloest"*, der die Ursache eingekreist
hat (jeder Leseversuch scheitert, auch auf einer eigens angelegten Testdatei,
im Scratchpad dagegen nicht). T-203 hat es genauso gemacht. **Beide Rollen
haben gleich und richtig reagiert.** Die Asymmetrie steht im Befundtext:
QA-237 schreibt *"T-196 hat … den Abzug zurueckgelesen … und genau das hat
T-196 als Nachweis gemeldet"*, und das widerspricht T-196s Bericht. Die Frage
"woran lag der Unterschied" hat keine Antwort, weil es den Unterschied nicht
gibt. **Der Befund QA-237 selbst bleibt unberuehrt richtig** — nur seine
Zuschreibung an T-196 nicht.

**Beobachtung 1 — Inhalt haelt, die Verhaeltniszahl nicht.** Drei widerlegte
Punkte (Archive, Register, `StrEnum`), 1,4 % gemessen, zwei bestaetigte
Strukturbefunde, QA-234 als Selbstbeleg: alles belegt. Die **120 000** dagegen
kommen im ganzen Repo nur an drei Stellen vor (`docs/state.md:29`,
`docs/plan-restarbeiten.md:564`, `docs/tasks/T-209.md`) und nirgends mit
Herleitung; P10 nennt gemessen 23 916 Quellzeilen und 113 477 Markdown-Zeilen.
Die Schlagzeile "-37 gegen 120 000" stellt **Quellzeilen** gegen ueberwiegend
**Markdown**zeilen — zwei Grundgesamtheiten in einem Bruch. Die Lehre des
Abschnitts ist davon unberuehrt und gut belegt: *"wo er Zeilen gezaehlt und
daraus auf Redundanz geschlossen hat, lag er daneben; wo er eine Struktur
benannt hat, lag er richtig."*

**Beobachtung 7 — siehe Abschnitt 1.** L-009 ist nicht aufgelaufen, L-009 hat
gegriffen.

**Beobachtung 2 hat eine Antwort, und sie ist die wichtigste des Laufs.** Die
Frage war, ob die Reihenfolge Glueck war. Sie war **kein** Glueck, sondern ein
Ausloeser, der seit dem 06.09. vorab benannt in `docs/lessons.md` stand:
L-011 wurde damals **bewusst ohne Massnahme** beschlossen, mit dem Satz, ab
wann daraus doch eine wird — *"ein Fall, in dem eine falsche Begruendung eine
Entscheidung bis zum Ende traegt … in einer **Nutzerentscheidung** landet"*.
Genau das ist passiert: die Freigabe fuer 35 154 Zeilen stand auf der
Audit-Praemisse *"Vollkopien, deren Vorfassungen git ohnehin haelt"*, und
`UI_SPEC.md:239-241`, `:1017-1019`, `:881-883` und sieben weitere Stellen sagen
woertlich, dass der geltende Wortlaut **nur** im Verlauf steht. Die Freigabe
war erteilt. **Gerettet hat es eine Pruefung danach, und das ist der
Unterschied zwischen einem gefangenen und einem eingetretenen Fehler.**
L-011s Ausloeser ist damit erreicht, und die von L-011 vorab benannte Massnahme
existiert bereits gebaut — `require-receipt.ps1`. Sie ist nicht angeschlossen.

**Grenze, die ich ausdruecklich nenne:** `require-receipt.ps1` bewacht
`Write`/`Edit`. Die teuerste Aussage des Zyklus reiste als **Nachricht an den
Nutzer**, nicht als Dateischreibung. Dafuer deckt L-019 nichts, und ich
schlage dafuer auch nichts vor — jede Bauform, die mir dazu eingefallen ist
(Stop-Hook auf Freigabefragen), erkennt den Moment nur ueber Textmuster und
waere damit genau die Sorte Waechter, die ich in Abschnitt 4 verworfen habe.
**Das ist eine offene Luecke und keine Massnahme.**

## 6. Was gut lief und geschuetzt werden soll

- **Vier sachliche Korrekturen des Directors, alle vier richtig, alle vier
  angenommen** — und in `plan-restarbeiten.md` vermerkt statt geglaettet, bis
  hin zum Satz *"Mein Wortlaut war zu grob, nicht seine Umsetzung."*
- **T-199 hat die L-009-Falle ohne Erinnerung im Auftrag gefangen** und die
  Gegenprobe dokumentiert.
- **T-196 hat einen strukturell unmoeglichen Nachweis als unmoeglich gemeldet**
  (`STATUS: teilweise`, `BLOCKIERT DURCH`, eigener Abschnitt zur Grenze) statt
  ein Ergebnis zu erzeugen, das nichts belegt. Daraus wurde QA-237.
- **T-203 hat einen Fehler in seiner eigenen ersten Fassung gefunden** und die
  Werkzeuggrenze seines Waechters gemeldet (QA-241).
- **T-206 hat die groesste Behauptung des Audits gemessen und gegen sie
  entschieden** — 1,4 %, mit Positivkontrolle, und der Empfehlung, aufzuhoeren.
- **Die Pruefung zwischen Freigabe und Loeschbefehl.** Nichts wurde geloescht.
- **Der Director fuehrt seine eigenen Fehler in `docs/state.md`** und hat die
  Liste waehrend dieses Laufs von fuenf auf sechs erweitert. **Ohne diesen
  Abschnitt waere dieser Lauf nicht moeglich gewesen. Keine Massnahme dieses
  Berichts darf ihn unattraktiv machen** — L-019 und L-020 sind deshalb so
  gebaut, dass sie beim *Schreiben* melden und nicht das Protokollieren
  bestrafen.

## 7. Beobachtungen ohne Muster (Auszug — vollstaendig in `docs/lessons.md`)

- **Die `CLAUDE.md` in meinem Kontext war zwei Commits alt.** Sie beschrieb den
  Testabzug als *"existiert nicht"*; die Datei auf der Platte nennt seit
  `f110dd4` den Pfad unter `…\Desktop\ClaudeCode\`, Version 1.9.0 und die
  Bestaetigung durch den Nutzer. `git status` sauber, `HEAD:CLAUDE.md` 159
  Zeilen. Ich habe von der Platte gelesen. Erstes Vorkommen, keine Massnahme.
- **Die QA-237-Falle hat mich selbst erwischt.** Ich fand
  `%LOCALAPPDATA%\NightreignHelper-Testabzug` mit 841 Dateien und war eine
  Zeile davon entfernt, QA-231 fuer falsch zu erklaeren. Nach QA-237 ist diese
  Sicht **kein Beleg** — der Leseversuch darin scheitert mit `Permission
  denied`, dasselbe Symptom, das T-196 beschrieben hat. QA-231 ist ohnehin
  behoben (T-200, Nachweis durch den Nutzer am echten System).
- **Der T-205-Bericht existiert nicht** (drei unabhaengige Pruefungen plus
  Volltextsuche). Der `archivist` hat kein `Write`; sein Bericht existierte nur
  als Nachricht. Das Ergebnis (23 Commits, `a4f275d..de420b6`) steht nur noch
  in der nachgetragenen Auftragsdatei.
- **Das Statusfeld in `docs/lessons.md` ist nicht mehr die Wahrheit:** L-009
  steht dort als *"vorgeschlagen"* und ist seit dem 06.09. in fuenf
  Rollendefinitionen in Kraft. Zweites Vorkommen der Klasse "zwei Regelsaetze,
  ein Nummernraum"; beim dritten wird es ein Muster.
- **`docs/state.md` wurde waehrend dieses Laufs zweimal fortgeschrieben.** Zwei
  meiner Zwischenbefunde waren beim Schreiben bereits behoben. Hinweis fuer die
  naechste Retrospektive: eine Aussage ueber `docs/state.md` braucht die
  Commit-Kennung daneben.

## 8. Codeprobleme, nicht meine Sache — fuer den `director`

1. **Fuenf Skripte setzen `QT_QPA_PLATFORM=offscreen` als Vorgabe**
   (`scripts/measure_picker_cards.py:60`, `measure_display_thresholds.py:53`,
   `measure_advisor_block.py:287`, `capture_weapon_damage.py:33`,
   `scripts/differential/capture.py:77`); drei messen Geometrie. Fundstelle der
   L-009-Falle aus T-199.
2. **`qa/findings.md:263` (QA-240) rendert mit neun statt acht Spalten** —
   unmaskiertes `|` im Codespan, die einzige Abweichung in 291 Tabellenzeilen
   beider Befunddateien.

## 9. Methode und Grenzen dieses Laufs

- **Jede Zahl in diesem Bericht ist gezaehlt**, nicht geschaetzt: die
  Auftrags- und Berichtszaehlungen mit `grep -c` je Datei, die
  `docs/state.md`-Zeilenzahlen mit `git show <c>:docs/state.md | wc -l` ueber
  zwanzig Commits, die Spaltenzahlen der Befundtabellen mit einem Skript, das
  maskierte `\|` entfernt und gegen die Kopfzeile stellt.
- **Jede Abwesenheits-Behauptung hat zwei unabhaengige Pruefungen**: die
  Hook-Registrierung ueber JSON-Parsing **und** `grep` in zwei Dateien; das
  fehlende `.md`-Pfadliteral in `tests/` ueber zwei verschiedene Masken; der
  fehlende T-205-Bericht ueber `ls`, `find`, `git log --all` und eine
  Volltextsuche.
- **Nicht geprueft:** die Protokolle unter `~/.claude/state/` (tragen laut
  Beobachtung vom 08.09. kein Projekt, bei parallelen Sitzungen ist die
  Zuordnung Raten); ob `require-receipt.ps1` scharf geschaltet in der Praxis
  falsch positiv meldet (das kann nur ein Lauf mit registriertem Hook zeigen);
  die `EXTRACT_VERSION` im Testabzug (Lesezugriff scheitert, QA-237).
- **Nicht getan, weil nicht meine Rolle:** kein Commit (der Auftrag entzieht es
  ausdruecklich), keine Aenderung an einer Agentendefinition oder `CLAUDE.md`,
  kein Code, keine Befund-ID vergeben.
