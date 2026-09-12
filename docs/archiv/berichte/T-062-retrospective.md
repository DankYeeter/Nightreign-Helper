# T-062 — retrospective

```
STATUS: erledigt
AUFTRAG: T-062 — Retrospektive Zyklus 12 und 13: die drei vom Director
  vermuteten Muster nachzaehlen, die Wirkung von L-001 bis L-007 pruefen,
  weitere director-verursachte Faelle suchen
GELESEN: docs/lessons.md · GOAL.md · docs/state.md ·
  docs/plan-restarbeiten.md (Abschnitt "Regeln, die fuer jeden Schritt
  gelten") · qa/findings.md (QA-100 bis QA-149) · docs/tasks/ (52 Dateien,
  Bestandspruefung per `ls`) · docs/berichte/T-037-developer.md,
  T-041-qa-engineer.md, T-045-developer.md, T-046-developer.md,
  T-047-architect.md, T-048-developer.md, T-051-qa-engineer.md,
  T-052-ui-ux-designer.md, T-053-developer.md, T-054-power-user.md,
  T-055-qa-engineer.md, T-056-ui-ux-designer.md, T-057-developer.md,
  T-058-developer.md, T-059-qa-engineer.md, T-060-developer.md — dazu
  **T-061-power-user.md**, das nicht in der Leseliste stand und das Muster
  L-010 mittraegt · ~/.claude/agents/{architect,developer,qa-engineer,
  ui-ux-designer,retrospective}.md (Abschnitt "Projektuebergreifende Regeln",
  weil L-005 bis L-007 in keiner Projektdatei stehen)
GEAENDERT: docs/lessons.md (angehaengt, nichts ueberschrieben — Abschnitt
  "Zyklus 12-13", L-008 bis L-011) · docs/berichte/T-062-retrospective.md
  (diese Datei). Kein Code, keine Agentendefinition, keine CLAUDE.md, keine
  Git-Operation ausser lesenden.
ANNAHMEN: (1) "Zyklus 12 und 13" umfasst T-037 bis T-061; T-038 bis T-040,
  T-042 bis T-044 und T-049 stammen aus der parallelen Scaling-Session und
  sind nur ueber Zitate in den gelesenen Berichten eingegangen, nicht selbst
  gelesen. (2) Die Angaben der Berichte ueber ihre eigenen Laeufe (Suite-
  Zahlen, Mutationsergebnisse) habe ich nicht nachgefahren — das ist die
  Arbeit des `qa-engineer`, und T-041 und T-059 haben sie fuer 21 Mutationen
  bereits geleistet. Nachgeprueft habe ich am Dateisystem: die Auftragsdateien
  unter `docs/tasks/`, die Abwesenheit von L-005 bis L-007 in allen
  Projektdateien, und die Herkunft der zitierten L-Nummern in den
  Agentendefinitionen.
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

---

## 1. Wirkungskontrolle in einer Zeile

**Von sieben frueheren Massnahmen wirken fuenf, eine ist gebrochen, eine ist
mangels Anwendungsfall ungeprueft — und alle sieben zusammen gehoeren zwei
verschiedenen Regelsaetzen an, die sich denselben Nummernraum teilen.**

Das ist der Befund, der die ganze Frage veraendert. `docs/lessons.md` fuehrt
L-001 bis L-004; die Agentendefinitionen von `architect`, `developer` und
`qa-engineer` fuehren unter "Projektuebergreifende Regeln" **ebenfalls** L-001
bis L-004 sowie L-006 und L-007 — mit anderen Inhalten. Zwei davon stammen
ausdruecklich aus diesem Projekt: teamweites L-006 nennt als Herkunft
"Nightreign-Helper L-001", teamweites L-007 nennt "Nightreign-Helper L-002".

Ich habe **jedes** L-Zitat der Zyklen 12 und 13 geprueft (T-037, T-041, T-045,
T-046, T-048, T-053, T-055, T-057, T-058, T-059, T-060, `qa/findings.md`
QA-115/QA-118): **jedes meint den teamweiten Satz, keines den Projektsatz.**
Die Nummern der Projektdatei werden seit `docs/tasks/T-023.md` nicht mehr
zitiert. **L-005 existiert in keinem der beiden Saetze.**

| ID | Wirkung |
|---|---|
| **L-001 Projekt** (Klasse statt Fundstelle), wirksam als teamweites L-006 | **wirkt** — sieben Berichte in Folge mit Suchbeleg und Trefferzahl; T-058 fand dabei vier Stellen, die kein Auftrag genannt hatte, und meldete sie |
| **L-002 Projekt** (Mutationsprobe), wirksam als teamweites L-007 | **wirkt formal zu 100 %, genuegt inhaltlich nicht** → L-008 |
| **L-003 Projekt** (Branch je Auftragsgruppe) | **wirkt**, Erfolgskriterium erfuellt; die offene Frage "wo steht der urspruengliche Satz?" ist beantwortet: **in keiner Datei** |
| **L-004 Projekt** (Auftragsdatei-Pflicht) | **gebrochen** — T-060 und T-061 haben keine, dazu zwei per Nachricht beauftragte T-052-Nachtraege. 23 von 26 |
| **L-001 teamweit** (Zahlen tragen ihr Rezept) | **wirkt**, mit einem Ausfall (QA-115, `dump_rate.py` existierte nie), den die Regel selbst gefunden hat |
| **L-003 teamweit** (mechanismus-gebundenes Signal) | **wirkt**, viermal zitiert und jedesmal ausschlaggebend |
| **L-004 teamweit** (Bau-Konfiguration) | **ungeprueft** — das Projekt hat keine Bau-Konfiguration, keinen Linter (F-A) und kein je geprueftes Artefakt (A9) |
| **L-005** | **existiert nicht** |
| **L-006 / L-007 teamweit** | wie L-001 / L-002 Projekt oben |

Vollstaendige Tabelle mit Belegen in `docs/lessons.md`, Abschnitt
"Wirkungskontrolle frueherer Massnahmen".

**Eine Konsequenz daraus, die keine Massnahme ist, sondern eine
Aufraeumentscheidung fuer den Nutzer:** Die Kollision hat bisher
nachweislich niemanden fehlgeleitet. Der heutige Schaden ist ein anderer —
**die einzige Regel, die nur das Projekt fuehrt und die der teamweite Satz
nicht kennt, ist L-004 (Auftragsdatei-Pflicht), und genau die ist gebrochen.**
Sie steht in einer Datei, die seit T-023 niemand mehr zitiert. Vorschlag:
(a) die zwei projekteigenen Regeln nach `docs/plan-restarbeiten.md`
verschieben — dorthin, wo `docs/state.md` die Arbeitsregeln ohnehin verortet
und wo jede Rolle sie liest; (b) kuenftige Projektnummern mit `NH-`
praefixen; (c) `docs/lessons.md` bleibt Verlauf, nicht Regelwerk. Kosten: eine
Textverschiebung.

---

## 2. Die drei vermuteten Muster — traegt es, oder war es eine Regel aus
## wenigen Faellen?

### (a) Waechter, die nichts bewachen — **traegt, deutlich: 13 Faelle, nicht 5**

Nachgezaehlt und einzeln belegt in `docs/lessons.md` L-008. Kurzfassung:
Pruefpunkt 13 (T-041/QA-100) · der Fingerabdruck-Waechter (QA-107) · der erste
Farb-Gegenbau zu `ratios.py` (T-045) · `test_move_scoped_effects.py`
(QA-118) · der Katalysator-Stub (T-046) · `arsenal_reading()` fuer sechs
Waffen (QA-123) · `"at level 1"` in `"at level 15"` (T-048) ·
`test_display_thresholds.py` (T-053) · fuenf ganze Tabs ohne Test (QA-137) ·
`test_every_type_row_..._match_the_facade` (QA-142) · zwei ueberlebende
Mutationen und ein falscher Registry-Eintrag (T-060 §9).

**Zwei Praezisierungen an deiner Beobachtung:**

1. **"Jedes Mal hat es nur der Mutationslauf gefunden" stimmt fuer 8 von 13.**
   Vier Faelle fand etwas anderes: eine Hash-/Gleichheitsprobe (QA-107), der
   Lauf einer **alten Testfassung gegen neuen Code** (QA-118), eine
   **vollstaendige Auszaehlung** ueber 1793 Waffen (QA-123), und der Vergleich
   **zweier Prozesse mit verschiedenen Hashseeds** (QA-142). Das ist wichtig,
   weil eine Massnahme "mehr Mutationen" diese vier nicht gefunden haette.
2. **Deine vier Mechanismen sind alle belegt, ein fuenfter fehlte:** eine
   registrierte Mutation, die **ueberlebt** (T-060 zweimal) oder deren Eintrag
   den falschen toetenden Fall nennt (T-060 einmal).

**Reicht die bestehende Regel?** Nein — und der Grund ist unbequem: sie wird
**vollstaendig eingehalten**. Rund 80 Gegenbauten sind in zwei Zyklen
registriert und einzeln gefahren worden; jeder `developer`-Bericht traegt die
Tabelle mit Zahlen; T-041 und T-059 haben 21 davon unabhaengig nachgefahren
mit null Abweichungen. Die Regel ist nicht schwach befolgt, sie ist
unvollstaendig formuliert: sie verlangt, dass eine Mutation existiert und
toetet, und sagt nichts darueber, **woher der Fall seine Erwartung nehmen
darf**, **unter welcher Auswahl die Mutation rot werden muss**, und **was ein
Ueberleben bedeutet**.

**Praezisierung, vorgeschlagen als Ersatz des ersten Spiegelstrichs in
`docs/plan-restarbeiten.md`, Abschnitt "Regeln, die fuer jeden Schritt
gelten":**

> - Jeder neue Waechter braucht seine **toetende Mutation**. Sie zaehlt erst
>   als toetend, wenn (1) sie **im Standardlauf** rot wird — nicht nur unter
>   einer Breite, Plattform oder Auswahl, die der Standardlauf ueberspringt;
>   (2) der rot gewordene Fall seine Erwartung **nicht** aus der Stelle
>   bezieht, die er bewacht — nicht aus derselben Konstante, nicht aus
>   demselben Prozess, und nicht als Teilzeichenkette einer Zeichenkette,
>   deren Wortschatz er nicht selbst setzt. **Ueberlebt eine registrierte
>   Mutation, ist das ein Befund ueber den Waechter**: er gehoert mit seiner
>   Ursache in den Bericht, nicht stillschweigend ersetzt.

Sie verlangt **keine** zusaetzlichen Mutationen. Sie verlangt, dass die
vorhandenen zaehlen. Kosten: eine Lesart beim Schreiben des Falls, plus ein
Berichtsabsatz statt eines stillen Austauschs.

### (b) Die drei Messfallen — **traegt, und es sind sechs, nicht drei**

Neben deinen dreien (physisch/logisch, Offscreen-Schrift, Qt-Stil) stehen:
die DPI-Falle im Screenshot, die T-052 beinahe einen Phantombefund gekostet
haette; die Offscreen-Mindestbreite von 964 px, wegen der der Testfall `[833]`
dort **964** misst und 833 in den Namen schreibt (T-059); und `processEvents`
statt eines echten Timers, das T-059 uebereinander gezeichnete Attributzeilen
zeigte, die es nicht gibt. Dazu als siebte Auspraegung derselben Ursache:
`SE_HeaderLabel` liefert unter Fusion 2 px Rand, unter windowsvista 4 —
weshalb ein frisch reparierter Spaltenkopf in T-060 als `y.` herauskam.

**Ja, es gibt eine Regel, die alle sechs gefangen haette**, und sie hat zwei
Haelften — die erste faengt 1, 2, 3, 4 und 7, die zweite faengt 5 und 6:

> - **Eine Zahl ueber die Oberflaeche nennt die Umgebung, in der sie
>   entstanden ist** — Plattform (`offscreen` / `windows`), Qt-Stil und
>   Palette, Skalierung, und ob die Pixel physisch oder logisch sind. **Und
>   jede Messung prueft, dass sie den Zustand wirklich erreicht hat, den ihr
>   Name behauptet**; erreicht sie ihn nicht, ueberspringt sie mit der
>   erreichten Zahl in der Meldung, statt zu messen. Die Testumgebung wird aus
>   **derselben Funktion** gebaut wie das laufende Programm.

**Das ist zum groessten Teil Ratifizierung, nicht Neubau.** T-060 hat den
mechanischen Teil schon gebaut: `apply_appearance(app)`, von `main()` **und**
von `conftest.qapp` gerufen, und ein `laid_out`, das ueberspringt statt still
danebenzumessen. Offen ist die Haelfte, die die **Berichtsprosa** betrifft —
und die haben T-058 §12.6 und T-059 ausdruecklich fuer `docs/lessons.md`
angemeldet ("der Befund mit der laengsten Halbwertszeit aus diesem Auftrag";
"ich schreibe dort nicht hinein"). Ich habe ihn hiermit eingetragen.

Der Preis ist sichtbar und schon bezahlt: seit T-060 meldet die Suite 9 bzw.
10 uebersprungene Faelle je Lauf, und wer alle fuenf Breiten sehen will, faehrt
sie zweimal (`759 + 9 = 758 + 10 = 768`). Die Regel schreibt das fest, damit es
niemand als "frueher war das gruen" zurueckdreht.

### (c) "Richtiger als ihre Begruendung" — **kein Zufall: zehn Faelle** — und
### trotzdem ausdruecklich **ohne Massnahme**

Zu deinen dreien (QA-101, D3, QA-115) kommen sieben weitere: `copy_key`s
Begruendung, die den Code nicht trifft und auf der deine eigene A/B/C-Vorlage
zu AD-013.4 stand (QA-112) · `effect_ids_of`s Reihenfolgebehauptung (QA-109) ·
`newline_of`s CRLF-Begruendung, deren **Korrektur** ihrerseits halb falsch war
(T-057 §5) · die Herleitung der Waffen-Id 34750000 ("Endung 750000 = Startwaffe",
T-046 §7) · die Farblegende, die T-060 sich selbst widerlegte · deine
Begruendung fuer "zieh die vier Spaltenzahlen nach" ("sie sind sichtbar, jetzt,
im Auslieferungszustand" — gemessen wahr fuer eine, falsch fuer drei) · und die
Zuschreibung, was QA-141 geschlossen hat (T-060 §9a: nicht die Herleitung der
Oeffnungsbreite, sondern `CardGrid`).

**Ursache:** In diesem Projekt wird die **Entscheidung** gemessen und die
**Begruendung** nicht. Mutation, Differentiallauf und Auszaehlung belegen das
Verhalten, nie den Satz daneben — und der Satz bleibt im Repo stehen
(`survival_means`, Docstring, `Goal.scope`, Kommentar) und wird von der
naechsten Rolle als belegt gelesen.

**Warum ich trotzdem keine Massnahme vorschlage** — das ist eine Empfehlung,
kein Versaeumnis:

1. **Es faengt sich.** In allen zehn Faellen hat eine spaetere Rolle die
   falsche Begruendung gefunden, meist im naechsten Auftrag, und in **keinem**
   ist daraus eine falsche Entscheidung geworden. Der schaerfste Fast-Schaden
   (QA-101) wurde gemessen, **bevor** du entschieden hast.
2. **Die schaedliche Haelfte hat schon eine Regel.** Zahlen ohne Rezept sind
   teamweites L-001, und die Regel hat QA-115 selbst gefunden.
3. **Die Kosten traefen das Beste am Projekt.** Eine Regel "jede Begruendung
   braucht ihre Messung" legt Beweislast auf die Prosa eines Projekts, das
   seine Begruendungen ausdruecklich in den Docstrings fuehrt. Teure Saetze
   werden kurze Saetze.

Auf die Beobachtungsliste kommt der **Ausloeser**: der erste Fall, in dem eine
falsche Begruendung eine Entscheidung **bis zum Ende traegt** — in einen
umgesetzten Fix, eine freigegebene Spec oder eine Nutzerentscheidung. Dann
wird daraus eine Massnahme.

---

## 3. Wo du als Director selbst die Ursache warst

Deine zwei bekannten Faelle sind belegt und bestaetigt:

- **T-054 lag in einer Datei, die die Rolle per Definition nicht liest.** Sein
  Bericht beginnt mit "GELESEN: bewusst nichts — nur der Auftragstext".
- **Der Relikt-Picker als "latent" eingestuft.** QA-141 und T-060 §2 messen
  es: **11 von 55 Karten** angeschnitten bei **1030 px**, der Breite, die sich
  der Dialog **selbst gibt**. Kein Zutun des Nutzers noetig; die Ursache waren
  die rund 20 px Standard-Innenraender des `QGridLayout`, die in
  `CARD_WIDTH * COLUMNS + 80` niemand mitgerechnet hatte.

**Fuenf weitere, die du noch nicht genannt hast:**

3. **T-060 und T-061 liefen ohne Auftragsdatei** — geprueft mit `ls
   docs/tasks/`: T-030 bis T-059 lueckenlos, T-060 und T-061 fehlen. T-060
   sagt es im eigenen Kopfblock. Dazu die zwei per Nachricht beauftragten
   T-052-Nachtraege, die AK-63 korrigiert und AK-67 sowie AK-105 hervorgebracht
   haben — nicht trivial. Das ist **L-004 gebrochen**, und zwar ausgerechnet
   beim groessten Einzelauftrag des Zyklus (T-060: 10 Befunde, 17 Commits, 14
   Mutationen) und bei dem, der danach abbrach.
4. **T-056 wurde gestartet, bevor du seine wichtigste Quelle abgelegt hattest.**
   Der `ui-ux-designer` hat mit vier unabhaengigen Zugriffen belegt, dass
   `T-054-power-user.md` nicht existierte, und **38 Akzeptanzkriterien auf
   Zitaten zweiter Hand** gebaut. T-057 fand die Datei spaeter (13:39) auf
   Platte. Dazu: **`docs/state.md:64` fuehrte T-054 als "geschrieben", waehrend
   die Datei nicht existierte** — ein Statuswort, das dem Dateisystem
   vorauslief.
5. **Der `power-user` wurde zweimal ohne die Werkzeuge beauftragt, die sein
   eigenes Abnahmekriterium verlangt.** A11 verlangt einen Bericht ohne "ich
   habe geraten". T-054 hatte kein Screenshot-Werkzeug, klickte blind auf
   Koordinaten und **musste die README lesen, um die Namen der Registerkarten
   zu erfahren**; T-061 kannte den Umweg nicht und meldete **blockiert** ohne
   eine einzige Aussage. Du hast es fuer T-061 selbst richtig eingeordnet —
   "ein Befund gegen meinen Auftrag, der Ausweg gehoert in den Auftrag". Er
   gehoert auch in den vorigen, und A11 ist deshalb bis heute unbeantwortet,
   waehrend zwei Rollen darauf warten.
6. **Der Zuschnitt T-057/T-058 wurde an "Geometrie" gezogen, und zwei Vorgaben
   fielen dazwischen.** DR-017/AK-83 und DR-018/AK-75 liegen im
   ausgeschlossenen Bereich, sind aber keine Geometrie; T-057 hat sie
   ausdruecklich liegen lassen und vorgelegt, T-058 hat sie eine Runde spaeter
   erledigt. Ebenso: der QA-113-Wortlaut kreuzte drei Auftraege (T-048 baut den
   Platzhalter, T-053 muss ihn umbenennen, weil OF-20 inzwischen beantwortet
   ist, T-057 ersetzt ihn) — die Rolle, die den Wortlaut entscheidet, wurde
   zweimal **nach** der Rolle beauftragt, die ihn braucht.
7. **Du warst in zwei der zehn (c)-Faelle selbst der Autor der Begruendung, die
   nicht trug** — D3 (der `architect` hat sie ersetzt und die Entscheidung
   behalten) und die Begruendung fuer "zieh die vier Spaltenzahlen nach", die
   T-060 fuer drei von vier Stellen widerlegt hat. Beide Male hat die Fachrolle
   korrigiert, ohne die Entscheidung anzutasten. Das ist der Mechanismus, der
   funktioniert — ich nenne es nur, weil du gefragt hast.

Die Punkte 3 bis 6 haben **eine** Ursache, und sie ist als **L-010** aufgenommen:
*der Auftrag wird aus dem Ergebnis heraus geschrieben, das er erzeugen soll,
und nicht aus den Voraussetzungen der Rolle.* Die Massnahme ist eine
Drei-Zeilen-Pruefung vor dem Dispatch (Medium — Werkzeug — Quelle), sie kostet
eine Minute und aendert **keine** Agentendefinition.

---

## 4. Die vorgeschlagenen Massnahmen, mit Zieldatei

Alle drei betreffen **nur** Text, den der Director bzw. das Projekt selbst
fuehrt. Keine Agentendefinition, keine `CLAUDE.md`, kein Code.

| ID | Muster | Zieldatei | Was |
|---|---|---|---|
| **L-008** | Waechter, die nichts bewachen (13 Faelle) | `docs/plan-restarbeiten.md`, Abschnitt "Regeln, die fuer jeden Schritt gelten" — **Ersatz** des ersten Spiegelstrichs; zusaetzlich in den Abschnitt "Regressionstests (Pflicht)" der Auftragsdateien | drei Bedingungen, wann eine Mutation als toetend zaehlt, plus: eine ueberlebende Mutation ist ein Befund |
| **L-009** | Die Testumgebung misst eine andere Maschine (6 Faelle) | `docs/plan-restarbeiten.md`, **neuer** Spiegelstrich | jede Oberflaechenzahl nennt ihre Umgebung; jede Messung prueft, dass sie ihren Namen erreicht hat |
| **L-010** | Der Auftrag prueft das Ergebnis, nicht die Voraussetzungen der Rolle (7 Faelle) | `docs/plan-restarbeiten.md`, **neuer** Spiegelstrich, gerichtet an den Director | drei Zeilen vor jedem Dispatch: Medium — Werkzeug — Quelle |
| **L-011** | "Richtiger als ihre Begruendung" (10 Faelle) | — | **verworfen mit Begruendung**, mit benanntem Ausloeser auf der Beobachtungsliste |

Dazu die Aufraeumentscheidung aus Abschnitt 1 (zwei Regelsaetze, ein
Nummernraum) — sie ist keine neue Regel, sondern das Verschieben zweier
vorhandener an den Ort, an dem sie gelesen werden.

**Warum nur drei.** Vier Muster sind belegt, drei bekommen eine Massnahme. Das
vierte (L-011) faengt sich nachweislich selbst, und eine Regel dafuer wuerde
die Prosa verteuern, die in diesem Projekt die eigentliche Dokumentation ist.

---

## 5. Was gut lief und geschuetzt gehoert

- **Die Mutationskampagne ist eine Institution.** ~80 Gegenbauten in zwei
  Zyklen, jeder einzeln gefahren, jeder mit Zahl im Bericht. Sie hat viermal
  etwas gefunden, das eine gruene Suite nie gezeigt haette. **L-008 darf das
  nicht schwaechen** — die Praezisierung verlangt keine zusaetzlichen
  Mutationen, sondern schaerft die vorhandenen.
- **Fremde Zahlen werden unabhaengig nachgefahren.** T-041: 15 von 15, null
  Abweichungen, in 27 eigenen Extraktionen. T-059: 6 von 6 exakt, samt den
  Namen der fallenden Faelle. T-051 hat die Golden-Datei aus den Git-Blobs neu
  gerechnet statt `ratios.py` zu benutzen — Gegenprobe statt Wiederholung.
- **Rollen melden ihre eigenen Fehler, unaufgefordert und ohne Beschoenigung.**
  T-053 ("ich habe committet, bevor die Suite lief"), T-048 ("ich hatte es
  behauptet, ohne es gemessen zu haben"), T-057 (zwei unsaubere Commits),
  T-060 ("der Teil des Berichts, den ich am wenigsten gern schreibe und der am
  meisten sagt"). **Das ist der Grund, warum diese Retrospektive ueberhaupt
  13 Faelle zaehlen konnte** — sie stehen alle in den Berichten selbst.
- **Falsche eigene Befunde werden verworfen statt gemeldet.** T-052 hat einen
  Phantombefund als eigenen Methodenfehler erkannt; T-059 fuehrt drei
  verworfene unter "Was nicht gehalten hat — an mir, nicht am Programm".
- **Niemand erfindet eine Zahl.** T-057 entfernte die handgetippten
  Debuff-Zahlen ersatzlos; T-048 liess QA-113s Einbauhoehe offen; T-046
  kennzeichnete 28 Referenzzahlen als "Abschrift einer Abschrift"; T-053 liess
  einen Platzhalter stehen und beschriftete ihn ehrlicher.
- **Auftragsgrenzen halten auch gegen eine Anweisung.** T-060 hat eine von
  vier Stellen nachgezogen, fuer drei gemessen, dass die Begruendung nicht
  traegt, und beides offen berichtet.

---

## 6. Was ich nicht geprueft habe

- Die Berichte T-038 bis T-040, T-042 bis T-044 und T-049 (parallele
  Scaling-Session) — nicht in der Leseliste, nur ueber Zitate eingegangen.
  Sollten sie eigene Prozessbefunde tragen, fehlen sie in dieser Zaehlung.
- Die Suite- und Mutationszahlen der Berichte habe ich **nicht** nachgefahren.
  Fuer 21 Mutationen haben T-041 und T-059 das bereits getan, mit null
  Abweichungen; fuer die uebrigen stuetze ich mich auf die Berichte.
- `DESIGN_REVIEW.md`, `UI_SPEC.md` und `ARCHITECTURE.md` habe ich nur ueber
  die Zitate der Berichte gelesen, nicht selbst. Aussagen ueber AK- und
  DR-Nummern stammen deshalb aus zweiter Hand und sind im Text als solche
  erkennbar.
- Ob die Kollision der beiden L-Nummernraeume je einen Agenten fehlgeleitet
  hat, kann ich nur fuer die Zitate der Zyklen 12/13 verneinen — fruehere
  Zyklen habe ich dafuer nicht durchgesehen.

---

## 7. Ablage

`docs/lessons.md` — fortgeschrieben, nichts ueberschrieben; neuer Abschnitt
"Zyklus 12–13 — 2026-09-05" mit Wirkungskontrolle, L-008 bis L-011 und vier
Beobachtungen. Absoluter Pfad:
`C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\docs\lessons.md`
