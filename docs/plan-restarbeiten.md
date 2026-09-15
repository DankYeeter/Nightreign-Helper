# Plan: alle offenen Punkte

Erstellt: 2026-09-03 vom Director, nach den Nutzerentscheiden zu QA-018 und
QA-061. **Auftrag des Nutzers: alle Punkte abarbeiten, nicht pausieren bis
alles fertig ist. Zwischenfragen erlaubt.**

Diese Datei ist die Reihenfolge. `qa/findings.md` und `security/findings.md`
bleiben die Wahrheit ueber den Zustand einzelner Befunde; hier steht nur, was
wann drankommt und warum.

## Die zwei Nutzerentscheide, die alles freigeben

**QA-018 — 203,4 ist richtig.** Woertlich: *"counterattack ist nur bei konter.
nicht global."* Der Buff greift nur beim Stoss-Konter; `attack_rating`
ueberschaetzt, indem es ihn als flachen Multiplikator behandelt. Die
Einschraenkung steht **nur im Beschreibungstext**, in keinem Param-Feld — die
betroffene Familie ist vollstaendig aufgezaehlt (~20 IDs, vier Namen).

**QA-061 — Lesart (a).** Woertlich: *"anforderung ist das charakter level.
sonst nichts. charaktere haben allerdings attribute und die beeinflussen wie
effektiv eine waffe auf welchem charakter ist."* Nightreign kennt **keine**
Attributsanforderungen fuer Waffen. Attribute wirken ueber die **Skalierung**,
und die ist bereits richtig. Checkbox "Meets requirements", Kachel-Dimmen,
"Requires"-Zeile und der `unmet`-Zweig sind toter Code.

---

## P1 — Die Zahlenbasis richtigstellen
*Zuerst, weil jede Rangfolge des Beraters darauf steht.*

1. **QA-018 / W6-Kern:** die vier Effektfamilien (Improved Thrusting
   Counterattack, Improved Sorceries, Improved Incantations, Improved
   Sorceries & Incantations) aus der flachen Multiplikatorschicht nehmen.
   Sie tragen kein `magicSubCategoryChange`-Feld, also braucht es eine
   benannte Liste — **und die Liste gehoert dokumentiert, nicht versteckt.**
2. **W6 vollstaendig:** `MULTIPLIERS_FOR[CANDIDATE]` setzen **plus** die
   Sortierung von `weapons.rank` auf `final_total` mit stabilem
   Zweitschluessel (Nicht-tun-Regel 29, gemessen begruendet: 584 von 7172
   Werten um 1 ULP).
3. **QA-061:** toter Code weg — Checkbox, Dimmen, "Requires"-Zeile,
   `unmet`-Zweig, der Golden-Fallname, der den Zweig verspricht (QA-019).
4. **QA-055 zweite Haelfte + AK-31 bis AK-40:** die Beschriftungen. Seit W4
   erlaubt. Dazu faellt der 60-%-Satz (der Nutzer hat ihn nie schriftlich
   belegt) — oder er kommt mit Aufbau und Datum zurueck.

## P2 — Den Fassaden-Umbau abschliessen
5. **QA-085** (vor W5): die Signalverdrahtung des Arsenal-Tabs bewachen.
6. **W5:** AD-021-Waechter scharf, `WeaponRating.total` faellt, QA-071
   (`attack_rating` ohne Produktionsleser) entscheiden, `bonus`-Kommentar auf
   die AD-024-Begruendung umschreiben.
7. **QA-086:** zwei gezielte Faelle — mehrtypige Armatur vollstaendig,
   Rarity-Filter gegen die Zaehlung.

## P3 — Der Build-Berater
*Das eigentliche Ziel. GOAL A3 bis A8.*

8. `architect`-Schritte S4 bis S11 aus AD-014 bis AD-018 und AD-023,
   UI-Spec AK-41 bis AK-62. Grenzbeitrag im Relikt-Picker, festgehaltene
   Slots, Fluechte ausgewiesen, `Optimize`-Knopf.
9. Nach P1 ist der Vorbehalt aus AD-023 **berechenbar statt pauschal** — und
   nach dem Fix zu QA-018 in den meisten Faellen **gar nicht mehr noetig**.

## P4 — Save-Lesen und Inventar
QA-032 + QA-004 (dieselbe Wurzel: stilles Ueberspringen) · QA-007
(Pruefsumme wird nie geprueft) · QA-008 · QA-010 · QA-012 (gated Effekte
umgehen die Bedingungspruefung) · QA-016 · QA-020 · QA-027 · QA-038
(doppelte Entschluesselungsschleife)

## P5 — Builds und Gefaesse

**Zuschnitt geaendert (Nutzer, 05.09.2026): ein Auftrag statt vier.** Der
Nutzer hat gefragt, ob die Registry-Randfaelle effizienter gehen. Sie gehen:
**QA-044, QA-048 und QA-054 sind nicht drei Fehler, sondern einer.**

Wurzel: der Speicher adressiert einen Build ueber einen **aus dem Namen
abgeleiteten Schluessel**, und die Ableitung ist nicht umkehrbar — deshalb
wird ein Build gelistet, den `load_build`/`delete_build` nicht finden
(QA-044), oder null mal gelistet, obwohl er in der Registry steht (QA-054).
Dazu schreibt die Migration ihren Marker (`__schema` = 3), **bevor** die
Bewegung fertig ist; danach heilt nichts mehr nach (QA-048).

**Ein Fix:** Builds ueber eine gespeicherte Kennung adressieren statt ueber
den abgeleiteten Namen, und den Migrationsmarker erst setzen, wenn die
Bewegung durch ist — oder ihn pruefen statt ihm zu glauben. **Ein Waechter**,
der alle drei kaputten Speicher synthetisch baut und zeigt, dass sie danach
listbar, ladbar und loeschbar sind. QA-047 (Testrueckstaende in
`HKCU\Software\DankYeeterTests`, nur Entwicklermaschinen) laeuft als
Dreizeiler mit.

Getrennt davon, unveraendert: QA-026, QA-028, QA-030, QA-031 (Deep-Slots,
`custom_item` ueber Gefaesswechsel, doppelte Fehlermeldung).

## P6 — Sicherheit

**Eingedampft (Nutzer, 05.09.2026): von sieben Punkten auf zwei.** Woertlich:
*"sicherheit kann weg, passt"* — als Zustimmung zum Director-Vorschlag, die
theoretischen Faelle zu streichen und die zwei mit echter Wirkung zu behalten.

**Bleibt:**
- **SEC-009** — Lieferkette der veroeffentlichten EXE (Action-Pin auf
  Commit-SHA, SHA-256-Pruefsumme). **Sperrt das Release.** Grund fuer den
  Verbleib: der Befund betrifft nicht den Nutzer, sondern jeden, der die EXE
  herunterlaedt.
- **SEC-019 + SEC-015** — als **eine** Label-Fabrik plus Waechtertest, nicht
  als 90 Einzelaenderungen. Schliesst eine Klasse zu geringen Kosten.

**Gestrichen, dokumentiert, nicht erneut vorlegen:** SEC-011, SEC-016,
SEC-017, SEC-018, SEC-020. Begruendung: jeder dieser Faelle setzt entweder
eine boesartige Spielinstallation voraus — die der Nutzer am 02.09.2026
ausdruecklich als vertrauenswuerdig eingestuft hat — oder einen Angreifer,
der das Benutzerkonto ohnehin schon kontrolliert. In beiden Faellen ist der
Befund nicht mehr das Problem.

## P7 — Waechter- und Testschulden

**Vollstaendig bestaetigt (Nutzer, 05.09.2026):** *"waechterschulden sind
sinnvoll fuer weitere anpassungen. durchfuehren."* Der Director hatte
vorgeschlagen, die Haelfte zu streichen; der Nutzer hat widersprochen, und
die Begruendung traegt — jede noch kommende Aenderung (S7 bis S11, der
Tab-Audit, P4/P5) laeuft ueber genau diese Waechter.

QA-023 (der `compute`-Waechter erkennt Schreibweisen, nicht Zugriffe) ·
QA-077 (34 Tooltips ungedeckt) · QA-037 · QA-052 + QA-053 · QA-059 ·
QA-078 · QA-087 · QA-088 · QA-066 · QA-019

## P8 — Oberflaeche
DR-004 bis DR-007 · QA-029 · QA-067 · QA-089

## P9 — Releasefaehigkeit

**Zusaetzlich, Nutzerentscheid 06.09.2026: `pyinstaller` aus den
Laufzeit-Abhaengigkeiten nehmen** — aber **hier**, nicht frueher.

Heute steht das Bauwerkzeug in `requirements.txt`. Wer das Programm nur aus
dem Quellcode starten will, installiert ein Paketierwerkzeug mit, das er nie
braucht. **Kein Defekt:** die `.spec` analysiert `run.py`, und `run.py`
importiert `pyinstaller` nicht — es landet nicht im Artefakt. Nur Unordnung.

**Warum erst hier:** `release.yml` installiert genau `requirements.txt` und
ruft danach `pyinstaller` auf. Ein Verschieben ohne Aenderung am Workflow
**bricht den Release-Build** — und dieser Workflow ist das einzige Stueck des
Projekts, das **noch nie ausgefuehrt** wurde (A9). Eine ungepruefte Pipeline
zu aendern, ohne sie danach laufen lassen zu koennen, tauscht Ordnung gegen
Risiko.

**Vorgehen:** eine eigene **`requirements-build.txt`** statt einer Verschiebung
nach `requirements-dev.txt` — das trennt "Tests" von "Paketieren", statt
beides in einen Topf zu werfen, und entspricht dem Vorgehen im
ApplicationHelper-Projekt desselben Nutzers. `release.yml` installiert dann
`requirements-build.txt`, `tests.yml` bleibt bei `requirements-dev.txt`.
**Der Waechter aus `tests.yml`** (pytest darf nicht in `requirements.txt`
stehen) wird um denselben Fall fuer `pyinstaller` erweitert.

**Abnahme:** derselbe `release-manager`-Lauf, der ohnehin `build` und
`clean-room` faehrt. Bricht er, ist die Aenderung dort und sofort sichtbar.

QA-036 (Icon-Pack: in ein temporaeres Verzeichnis bauen und umbenennen) ·
SEC-009 (zwei Punkte, < 10 Zeilen YAML) · `compliance-agent` (`auflagen`) ·
`technical-writer` · `release-manager` (`build`, `clean-room`) ·
`power-user` · **GOAL A9**

## Regel fuer den Director selbst (L-010)

Aus der Retrospektive zu Zyklus 12/13, **sieben Belege, alle beim Director**:
ein Auftrag prueft, was herauskommen soll, aber nicht, was die Rolle **lesen,
benutzen und uebergeben** kann. Drei Zeilen vor jedem Dispatch:

1. **Medium** — Rollen ohne Dateizugriff bekommen ihren Auftrag im
   **Nachrichtentext**, nicht als Pfad. Der power-user darf docs/tasks/ per
   Definition nicht oeffnen; ein Auftrag dort ist keiner.
2. **Werkzeug** — hat die Rolle die Werkzeuge, die das Abnahmekriterium
   verlangt? Fehlen sie, ist der Lauf **kein Nachweis**, und der Auftrag
   wartet, statt ein Ergebnis zu erzeugen, das nichts belegt.
3. **Quelle** — Berichte von Rollen ohne Write-Recht liegen ab, **bevor** die
   abhaengige Rolle startet. Und docs/state.md sagt "geschrieben" erst
   **danach**, nicht vorher.

## Nummernkreise der Regeln — Achtung, zwei Saetze

docs/lessons.md fuehrt projekteigene Regeln, die Agentendefinitionen fuehren
teamweite — **beide unter L-001 aufwaerts, mit verschiedenen Inhalten.** Jedes
L-Zitat aus Zyklus 12/13 meinte den **teamweiten** Satz; die Projektnummern
werden seit T-023 nicht mehr zitiert, und die einzige rein projekteigene
Regel stand dadurch in einer Datei, die niemand mehr liest — und war
gebrochen.

**Ab jetzt:** projekteigene Regeln stehen **hier** und tragen das Praefix
**NH-**. docs/lessons.md bleibt Verlauf. L-008 bis L-011 sind teamweite
Nummern aus der Retrospektive.

**NH-002: Nachweise werden aus dem Qt-Fenster gezogen, nie vom Bildschirm.**
Am 05.09.2026 lagen vier volle Desktop-Abzuege (2560x1600 = Bildschirm-
aufloesung) im **oeffentlichen** Repo — mit Desktop-Symbolen, Taskleiste,
einem fremden Fenstertitel und einem Wetter-Widget mit Ortsbezug. Aufgefallen
ist es nur, weil ein spaeterer Lauf demselben Fehler aufsass, ihn **selbst
bemerkte** und vor dem Commit meldete. Entfernt in `264d328`; das Restrisiko
ueber die alte Commit-Kennung hat der Nutzer ausdruecklich akzeptiert.

Verbindlich: `grab()`/`render()` auf dem Widget oder `PrintWindow` auf dem
eigenen HWND — **kein** Bildschirmabzug, auch nicht zugeschnitten. Ein
Zuschnitt kann sich erweitern; ein Fensterabzug kann nichts einfangen, was
nicht zum Programm gehoert. Wer ein Bild ablegt, prueft vorher seine
Abmessungen gegen die Bildschirmaufloesung.

**NH-001 (war L-004): jede nicht-triviale Arbeit bekommt eine T-Nummer und
eine Auftragsdatei.** In Zyklus 13 zweimal gebrochen (T-060 und T-061 liefen
ohne Datei, dazu zwei Nachtraege per Nachricht).

## Zurueckgestellt, mit Grund
- **`ruff` / Linter — entschieden am 06.09.2026, Option B: kein Linter.**
  Der Nutzer hat die Abnahmezeile abgeschafft statt das Werkzeug zu
  beschaffen. Begruendung: der tote Code, den dieses Projekt tatsaechlich
  gefunden hat (QA-061, QA-071, QA-038), liegt auf **Modulebene** — genau
  das findet `ruff` in der Grundeinstellung **nicht**. Die Funde kamen aus
  Aufruferanalysen und Mutationslaeufen, nicht aus einem Linter. Die
  DoD-Zeile ist im Agenten-Repo bedingt gemacht: ohne konfigurierten Linter
  **entfaellt der Punkt**, und das ist **keine Luecke**. Wird nicht erneut
  vorgelegt.
- **C-002** — auf Anweisung des Nutzers ignoriert, nicht erneut vorlegen.

## Regeln, die fuer jeden Schritt gelten
- **Jeder neue Waechter braucht seine toetende Mutation — und drei
  Bedingungen** (L-008, 13 gezaehlte Faelle in Zyklus 12/13): sie zaehlt erst
  als toetend, wenn sie im **Standardlauf** rot wird; der Fall bezieht seine
  Erwartung **nicht** aus der Stelle, die er bewacht; und eine **ueberlebende**
  Mutation wird als Befund berichtet, nicht stillschweigend nachgebessert.
  Verlangt keine zusaetzlichen Mutationen, nur schaerfere.
- **Jede Oberflaechenzahl nennt ihre Messumgebung** (L-009, sechs gezaehlte
  Fallen): Plattform, Stil, Skalierung, physisch oder logisch. Und jede
  Messung prueft, dass sie ihren eigenen Namen erreicht hat — ein Testfall
  "[833]", der in Wahrheit 964 misst, ist keine Messung.
- Charakterisierungen auf der **ungerundeten** Zahl, Anzeigetext getrennt.
- Die Messstrecke unter `scripts/differential/` **benutzen, nicht neu bauen**.
- Eine Zusicherung nennt ihren **Geltungsbereich** — das ist die dominante
  Fehlerklasse dieses Projekts (QA-046, 050, 052, 062, 063, 064, 070, 073,
  082, 083, 086, 087).

---

# Arbeitsweise: drei Ineffizienzen, abgestellt am 08.09.2026

*Auf Anweisung des Nutzers ("bessere die Ineffizienzen aus"). Alle drei ohne
Codeaenderung, also ohne den eingefrorenen Stand von Zyklus 16 anzufassen.*

## E-1 — Der Datenabzug wird nicht mehr je Lauf neu gebaut

**Das Problem, gemessen.** Jeder Lauf am gebauten Artefakt bekommt ein eigenes
umgelenktes `LOCALAPPDATA` und baut darin den Datenabzug samt Symbolvorrat neu
auf: **107 s im `power-user`-Lauf, rund 5 min im `clean-room`-Lauf** (QA-198).
In Zyklus 16 wurde das **viermal** bezahlt, fuer denselben Abzug aus derselben
Spielinstallation.

**Die Loesung.** Ein einmal gebauter Abzug liegt fest unter

```
C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug
```

**841 Dateien, 19,8 MB**, `nightreign_data.json` 8 484 651 B, gebaut am
08.09.2026 08:04 von Programmfassung **1.8.0** (`EXTRACT_VERSION` 11). Er
stammt aus dem `power-user`-Lauf T-115 und wurde aus dem Scratchpad
herausgehoben, damit er Sitzungen ueberlebt.

**So benutzt ihn ein Auftrag.** Vor dem ersten Start des Artefakts den Abzug in
das umgelenkte `LOCALAPPDATA` **kopieren** (nicht darauf zeigen lassen — das
Programm schreibt hinein):

```
Copy-Item "C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug" `
          "<dein LOCALAPPDATA>\NightreignHelper" -Recurse
```

**Wann er nicht mehr gilt** — und das gehoert in jeden Auftrag, der ihn
benutzt: der Abzug wird ungueltig, sobald das **Spiel gepatcht** wird
(`regulation.bin` aendert sich) oder `EXTRACT_VERSION` **ueber 11** steigt.
Dann baut das Programm ihn ohnehin neu; der erste Lauf, dem das passiert,
**ersetzt die Vorlage** und vermerkt es hier.

**Nicht ins Repository.** Der Abzug ist aus der Spielinstallation gewonnen —
NH-002 und die Zusage aus A-003 verbieten das. Er liegt bewusst ausserhalb des
Projektbaums, nicht bloss in `.gitignore`.

**Ersparnis gemessen (S11, T-118, 08.09.2026): 99,2 %.** Neubau
**293,8-310,1 s** gegen Kopie **2,54 s**. Der Neubau ist inhaltsgleich zur
Vorlage — gleicher Fingerabdruck, 841 Dateien; bis dahin war das eine Annahme,
jetzt ist es geprueft.

## E-2 — Am Artefakt wird nur geprueft, was das Fenster wirklich braucht

Die drei Pruefungen am Artefakt in Zyklus 16 kosteten **41 min**
(`clean-room`), **25 min** (`power-user`) und ueber 40 min (`qa-engineer`).
Klicken ist langsam, daran aendert kein Modell etwas — der Hebel ist, **was**
durch die Oberflaeche geht.

**Regel fuer jeden kuenftigen Pruefauftrag am Artefakt:** die Kriterien werden
vorher geteilt.
- **Ohne Fenster pruefbar:** A8 (alle Texte Englisch) und grosse Teile von A4
  (Stacking, Slot-Farben, Deep-of-Night) — am entpackten Bundle bzw. an den
  mitgelieferten Daten.
- **Braucht das Fenster:** A3 (je Nightfarer zwei Zielrichtungen), A5 (die
  Begruendung in Nutzersprache), A6 (die Oberflaeche blockiert nicht), A7 an
  den Stellen, an denen der Text im Fenster steht.

Der Auftrag benennt die Teilung, statt sie der Rolle zu ueberlassen.

## E-3 — Zwei Gewohnheiten des Directors

- **`docs/state.md` wird einmal je Zyklus geschrieben**, am Ende, auf das
  Zeilenbudget. In Zyklus 16 wurde sie **sechsmal** umgeschrieben, davon
  viermal nur, um das Budget zu treffen. Das ist verschwendete Arbeit an einer
  Datei, deren Zweck Uebergabe ist, nicht Aktualitaet im Minutentakt.
- **Der Bericht ist Teil des Auftrags, nicht sein Nachklang.** Der
  `power-user` hat in T-115 **kein** Schreibrecht gehabt (`tools:` in
  `agents/power-user.md` nennt weder `Write` noch `Edit`, nachgezaehlt am
  08.09.2026), und seine Definition untersagt ihm das Schreiben ausdruecklich.
  Der Director hat seinen Bericht abgelegt, und **das war richtig so.**
  Kuenftig steht in jedem Auftrag an eine Rolle **mit** `Write` der Satz:
  *"Der Auftrag gilt erst als erledigt, wenn
  `docs/berichte/T-###-<rolle>.md` auf der Platte liegt."*

  *Hier stand bis zum 08.09.2026 das Gegenteil — die dritte Fundstelle
  derselben widerlegten Aussage. Zwei wurden am selben Tag korrigiert
  (`CLAUDE.md`, Kopf des T-115-Berichts), diese blieb stehen und wurde von
  `fable` gefunden. Genau das beschreibt L-016: eine Korrektur schliesst die
  **Fundstelle**, nicht die **Aussage** — und die Regel hat am Tag ihrer
  eigenen Annahme nicht gegriffen.*

## P10 — Der Ueberbau-Audit vom 12.09.2026 (Korb 3)

*Herkunft: ein Ueberbau-Audit des Directors ueber den ganzen Baum,
12.09.2026, vom Nutzer in drei Koerbe sortiert. Korb 1 (kleine Eingriffe)
laeuft in diesem Zyklus, Korb 2 (Loeschungen) liegt beim Nutzer. **Hier steht
Korb 3: zwei strukturelle Umbauten, die keine Nebenarbeit sind.** Der Nutzer
hat ausdruecklich verlangt, dass sie als regulaere Aufgaben laufen — Entwurf
durch den `architect`, dann `developer`, dann QA — und nicht als
Hauruck-Aktion neben etwas anderem.*

**Gemessene Ausgangslage** (`wc -l`, Arbeitsbaum, HEAD `5989f97`,
12.09.2026): `nrplanner/` + `nrdata/` 23 916 Zeilen · `tests/` 35 236 ·
Markdown im Baum 113 477. Von den 23 916 Quellzeilen sind 3 785 Kommentar-
und 5 761 Docstring-Zeilen (`ast`-Zaehlung), 3 239 leer — also rund 11 100
Zeilen ausfuehrbarer Code.

### P10-1 — `class Planner` ist 3 318 Zeilen

`nrplanner/app.py:1836` bis `1:5154` (`main()`). Eine Klasse traegt damit
knapp ein Drittel des gesamten Quellcodes. Die Tabkoerper liegen schon in
eigenen Modulen (`bosstab.py`, `effectstab.py`, `arsenaltab.py`); der Schnitt
existiert also bereits und ist nur fuer die Verdrahtung nicht gezogen.

**Reihenfolge:** `architect` (Modulschnitt entlang der bestehenden Naht, mit
AD-Nummer) → `developer` → QA-Regressionslauf. **Nicht** als Teil eines
Feature-Auftrags. Der Umbau beruehrt jede Tab-Verdrahtung gleichzeitig und
sprengt damit die Fuenf-Dateien-Grenze; die Teilung gehoert in den Entwurf,
nicht in den Bauauftrag.

### P10-2 — Die Mutations-Registry haelt 5 300 Zeilen kopierten Quelltext

`scripts/differential/mutate.py:44` bis `5368` sind handgeschriebene
Mutationsliterale — je Mutation der exakte alte und der exakte neue
Quelltext. Darunter liegen rund 100 Zeilen Logik (`newline_of`, `apply`,
`guard_the_own_tree`, `main`). `tests/test_differential_track.py` bewacht die
Anker gegen den echten Quelltext, das heisst: **jedes Refactoring am
Anwendungscode macht diese Datei rot**, und P10-1 macht das sicher.

**Deshalb laeuft P10-2 vor oder mit P10-1, nicht danach.** Zwei Richtungen
sind zu entwerfen, nicht schon entschieden: die Mutationen aus ihren Ankern
zur Laufzeit erzeugen, oder die Registry auf die Mutationen einkuerzen, die je
etwas gefangen haben. **Welche, entscheidet der `architect`** — dazu gehoert
die Frage, ob der Differenzial-Track ueberhaupt noch traegt, was er kosten
soll.

### Nicht in Korb 3, sondern schon entschieden

Die Prosakuerzung in `nrplanner/` (Korb 1) laeuft in der Variante
**"nur belegt Redundantes"** — Nutzerentscheidung 12.09.2026: gekuerzt wird,
was den Code nachspricht oder doppelt in `ARCHITECTURE.md` / `UI_SPEC.md`
steht; **jede Zeile mit QA-, AD-, AK- oder SEC-Nummer und jede Deckenangabe
bleibt woertlich stehen**, und je geloeschtem Block wird die Stelle genannt,
die dasselbe sagt. Die vom Audit genannten 9 546 Zeilen sind damit **nicht**
das Ziel; die Begruendungsdocstrings (`chalices.py:325-384` zu QA-041 und
QA-046, `model.py`) stehen an keiner zweiten Stelle im Repo.

### Korb 2 — die Loeschung ist zurueckgezogen, nichts wurde geloescht

*12.09.2026. Der Nutzer hatte drei Gruppen freigegeben (Register,
Verlaufskopien, archivierte Auftraege — 35 154 Zeilen). **Die Freigabe stand
auf einer Praemisse des Directors, und die war falsch.** Vor dem Loeschbefehl
hat eine Pruefung der lebenden Verweise sie widerlegt. Nichts ist geloescht.*

Das Audit nannte die Verlaufsdateien "Vollkopien, deren Vorfassungen git
ohnehin haelt". Sie sind keine Kopien. T-181 und T-182 haben `UI_SPEC.md` und
`ARCHITECTURE.md` **geteilt**: der geltende Wortlaut blieb, die Begruendungen
wanderten heraus. Im Arbeitsbaum stehen sie danach **nur noch** in der
Verlaufsdatei.

Drei Belege, die je allein reichen:

1. **Der bindende Wortlaut mehrerer Akzeptanzkriterien steht nur im
   Verlauf.** `UI_SPEC.md:239-241`, `:1017-1019`, `:881-883` und sieben weitere
   Stellen sagen woertlich: *"Der geltende Wortlaut steht deshalb nicht hier,
   sondern in `docs/archiv/ui-spec-verlauf.md`"* — betroffen sind unter
   anderem A28, A29 und A31. `UI_SPEC.md` ist dort ein Zeiger, kein Text.
2. **Das Register ist der erklaerte Einstieg, kein Index.**
   `ARCHITECTURE.md:26`: *"**Hier faengt man an.**"* Und `UI_SPEC.md:48-49`:
   die Abschnittskennungen `A01` bis `A33`, auf denen jede
   Verlaufs-Zeilenangabe in `UI_SPEC.md` beruht, *"sind in
   `UI_SPEC_REGISTER.md` aufgeloest"*. Ohne Register ist jeder Verweis der
   Form `A28 Z8004` nicht mehr aufloesbar.
3. **`qa/verlauf.md` und `security/verlauf.md` tragen dieselbe Teilung.**
   `qa/findings.md:5` und `security/findings.md:5`: *"abgetrennt in T-180"*.
   `docs/lessons.md:772` zitiert den QA-198-Wortlaut von dort.

**Was daraus fuer kuenftige Audits folgt:** eine Zeilenzahl sagt nicht, ob
Text doppelt vorliegt. Das Audit hat 113 477 Markdown-Zeilen **gezaehlt** und
daraus auf Redundanz **geschlossen**. Geprueft war sie nicht. Dasselbe Muster
hatte der Nutzer eine Stufe tiefer schon abgefangen (Docstrings mit QA-Bezug);
es lag eine Ebene hoeher noch einmal.

**Offen und nicht entschieden:** `docs/archiv/berichte/` (97 Dateien, 36 933
Zeilen) und `docs/archiv/tasks/` (120 Dateien, 15 468 Zeilen). Beide werden
zitiert — die Berichte 13-mal, die Auftraege ueber ihren **alten** Pfad
`docs/tasks/T-0xx`, der durch die Archivierung in `0a59a0f` bereits toter
Verweis ist (ueber 20 Nummern, ungezaehlt). Sie sind der einzige verbleibende
Kandidat, und die Frage dazu ist nicht "loeschen?", sondern erst "welche
Verweise haengen daran?".

### Korb 1 — Bilanz nach T-204 (12.09.2026)

**Zwei von drei mechanischen Punkten sind erledigt, einer ist am Bestand
gescheitert — und das Scheitern ist das wertvollere Ergebnis.**

- **`baseline_for` ist gestrichen** (`7bb927c`), einziger Aufrufer im Test
  bestaetigt und inline ersetzt. **Netto -6 Zeilen.** Suite unveraendert:
  `1781 passed, 9 skipped`.
- **`StrEnum` ist abgelehnt, begruendet.** `nrplanner/advisor/goals.py:56` macht
  `from . import types`; `types.py` importiert nur `model`. **Die Richtung ist
  eindeutig** (vom Director am Quelltext nachgeprueft, nicht aus dem Bericht
  uebernommen): `types.py` kann die Zielrichtungs-Registry nicht lesen, ohne
  einen Zirkelimport zu bauen. Die einzige Alternative waere, die drei Goal-Ids
  ein zweites Mal in `types.py` hart zu schreiben — zwei Orte statt einem,
  gegen das Muster des Moduls selbst, und bei einer vierten Richtung bricht
  jeder gewoehnliche Aufruf mit `ValueError`, wo er heute nur ungeprueft
  durchlaeuft. **Der Audit hat die Klassen gesehen und die Importrichtung
  nicht.**
- **Offen und ausdruecklich nicht mit erledigt:** der Kommentarsatz
  *"enforced rather than hoped for"* (`types.py:225`) ist weiterhin ungenau,
  unabhaengig von der `StrEnum`-Frage — eine leere `str`-Unterklasse erzwingt
  nichts. Gehoert in die Prosakuerzung oder einen eigenen Punkt.
- **Wenn `StrEnum` trotzdem gewollt ist**, ist es **kein** Formsache-Auftrag
  mehr, sondern ein `architect`-Schnitt gegen den Zirkelimport. Nicht
  beauftragt, und ich empfehle es nicht: der Nutzen ist Typdisziplin an drei
  Werten, die Kosten sind ein Modulschnitt.

**Nachzuziehen, nicht meine Datei:** `ARCHITECTURE.md:2459` sagt woertlich
*"`baseline_for(pool, goal_id) -> float` bleibt unveraendert gueltig und liest
weiterhin `.value`"* — die Funktion existiert seit `7bb927c` nicht mehr
(Fundstelle vom Director geprueft). **Gehoert dem `architect`** und laeuft mit
dem naechsten seiner Auftraege (P10 braucht ihn ohnehin). Bis dahin ist es eine
bekannte Altstelle und kein Versehen.

### Was vom Audit nach dem Kontakt mit dem Bestand uebrig ist

*Stand 12.09.2026, damit die naechste Runde nicht denselben Bogen laeuft.*

| Punkt des Audits | Ergebnis |
|---|---|
| 69 207 Zeilen Archive loeschen | **widerlegt** — keine Kopien, die Spec wurde geteilt |
| Register loeschen (533) | **widerlegt** — `ARCHITECTURE.md:26` nennt es den Einstieg |
| 146 Berichte loeschen | **zurueckgestellt** — 13-mal aus lebenden Dateien zitiert |
| `StrEnum` statt zweier `str`-Klassen | **widerlegt** — Zirkelimport |
| `baseline_for` inlinen | **erledigt**, -6 Zeilen |
| Kopf von `requirements-dev.txt` | laeuft in T-203 |
| Prosakuerzung (11 402 Zeilen) | laeuft als **Pilot** auf drei Dateien, T-206 |
| `Planner`, 3 318 Zeilen | **bestaetigt** als echte Schuld, P10-1 |
| Mutations-Registry, 5 300 Zeilen | **bestaetigt** — und QA-234 hat die Kopplung noch am selben Tag bewiesen, P10-2 |

**Die Lehre ist nicht "der Audit war falsch".** Seine zwei groessten
strukturellen Befunde haben gehalten, und einer hat sich binnen Stunden von
selbst belegt. Falsch war durchgaengig dasselbe: **wo er Zeilen gezaehlt und
daraus auf Redundanz geschlossen hat, lag er daneben; wo er eine Struktur
benannt hat, lag er richtig.** Ein Zeilenzaehler sieht keine Importrichtung und
keine geteilte Datei.

### T-206 hat die groesste Audit-Behauptung gemessen — und sie faellt

**Ausbeute: 20 Prosazeilen von 1427. 1,4 %.** Sieben Bloecke von 175, jeder mit
benannter Ersatzstelle. Suite unveraendert (`1781 passed, 9 skipped`), und der
Nur-Prosa-Beleg ist selbst gebaut: `ast.dump` ohne Docstrings vor und nach
identisch, dazu jede Diffzeile gegen Docstring-Spanne und Kommentarmenge
geprueft — **mit Positivkontrolle**, ein eingebautes `math.floor` → `int`
schlaegt in beiden Pruefungen an.

**Das Muster laeuft dem Audit entgegen.** `explain.py`, die nach Anteil
dichteste der drei ("fast reiner Docstring", 49 %), lieferte **eine** Zeile:
58 % ihrer Bloecke tragen eine Befundnummer und sind damit vor jedem Urteil
geschuetzt. `model.py`, die kommentarlastige, lieferte 15. **Prosadichte sagt
nichts ueber Kuerzbarkeit** — wer nach Anteil auswaehlt, waehlt falsch, und ich
habe die drei Dateien genau so ausgewaehlt.

Von 175 Bloecken waren **98 (56 %) durch "bleibt ohne Ermessen" geschuetzt**,
bevor irgendein Urteil faellig war. Von den 77 uebrigen waren sieben kuerzbar.

**Entscheidung: die restlichen siebzehn Dateien werden nicht gekuerzt.**
Erwartung 1-3 %, also 100-300 Zeilen von rund 10 000, gegen einen Opus-Lauf je
drei Dateien und je Zeile ein Leseurteil. Der `developer` hat es so empfohlen,
und die Zahl traegt die Empfehlung. **Korb 1 ist damit abgeschlossen** bis auf
T-203.

**Regelkorrektur fuer eine etwaige Folgerunde.** Meine zwei Regeln kollidierten
an `damage.py:22`: "jede Zeile mit AD-Nummer bleibt woertlich" gegen "der
Verweis bleibt, der Wortlaut geht". Der `developer` hat die Kollision vorgelegt
statt sie zu verstecken. **Ich habe seine Lesart uebernommen** — die Nummer
bleibt, der nacherzaehlende Satz geht. Kuenftig heisst die Regel: *jede AD-,
QA-, AK- oder SEC-Nummer bleibt; der Satz, der sie nacherzaehlt, darf gehen.*
Mein Wortlaut war zu grob, nicht seine Umsetzung.

### Drei Funde aus T-206, die nicht die Prosa betreffen

1. **`scripts/differential/mutate.py:175-183` verankert eine Mutation in vier
   Kommentarzeilen** (`# Thrusting Counter.`, `# Sorceries`, …). Wer die
   kuerzt, entwaffnet `move-scope-constant-emptied`, und der Mutationslauf
   meldet **nichts**. **Das schaerft P10-2:** die Registry haengt nicht nur am
   Quelltext, sondern auch am Kommentartext — eine Kopplung, die das Audit
   nicht gesehen hat und die jede Prosaarbeit an diesen Dateien vorher
   entschaerfen muesste.
2. **Sechs Zeilennummern-Zitate innerhalb der drei Dateien waren schon vor der
   Aenderung falsch** (belegt mit `git show HEAD~1:… | sed -n`), und die
   Kuerzung verschiebt sie um weitere 4 bis 15 Zeilen. **Kein Test prueft sie.**
   Gefuehrt als QA-240.
3. **`ARCHITECTURE.md:783-784` (AD-020 Punkt 4) zitiert einen Code-Kommentar
   als seine Quelle** (`damage.py:502-505`). Dort ist das Dokument **nicht** die
   Ersatzstelle, sondern das Abgeleitete. **Die Richtung des Belegs ist je Fall
   zu pruefen** — "steht auch in ARCHITECTURE.md" heisst nicht immer, dass der
   Code-Kommentar der entbehrliche Teil ist.

### T-203 schliesst Korb 1 — mit einer Einschraenkung, die zum Muster passt

**Der Waechter steht:** `.claude/hooks/enforce-data-redirect.ps1`, registriert
in einem neuen `.claude/settings.json` auf `PreToolUse` fuer `Bash|PowerShell`.
Die Decke steht als `ponytail:`-Kommentar **im Hook** (Zeile 44) und nicht als
Absatz in der Doku — eine unbekannte Startform rutscht durch, und der Kommentar
sagt, wo man sie ergaenzt. `CLAUDE.md` 160 → **159** Zeilen, also gekuerzt wie
verlangt, obwohl die Positiv-/Abwesenheits-Unterscheidung neu hinzukam.
`requirements-dev.txt` hat seinen zehnzeiligen Begruendungskopf verloren.

**Der `developer` hat in seiner eigenen ersten Fassung einen Fehler gefunden
und behoben:** ein Anker auf Zeilenanfang liess
`VAR=x VAR2=y python run.py` mit fehlenden Variablen durch. Meine Gegenprobe
bestaetigt, dass dieser Fall jetzt abgewiesen wird.

**Die Einschraenkung ist QA-241** und sie ist dieselbe Klasse, die den Hook
ueberhaupt noetig gemacht hat: er ist in der Sitzung seiner Installation
**wirkungslos**, weil Einstellungen beim Sitzungsstart gelesen werden. Der
`developer` hat das als offenen Punkt gemeldet statt zu behaupten, es laufe;
der Director hat es live gegengeprueft (durchgelassen) und gegen die
stdin-Schnittstelle (abgewiesen). **Die Logik ist korrekt, die Ladezeit ist das
Problem.** Bis zum Neustart schreibt der Director die drei Umlenkungen weiter
woertlich in jeden Auftrag.

**Korb 1 ist abgeschlossen.** Bilanz: `baseline_for` gestrichen (-6 Zeilen),
`requirements-dev.txt`-Kopf gestrichen (-10), Prosa 20 Zeilen in drei Dateien
und **bei 1,4 % gestoppt**, `StrEnum` am Zirkelimport abgelehnt, `CLAUDE.md`
-1. **Summe rund -37 Quellzeilen** gegen die 120 000, die der Audit in
Aussicht gestellt hat — und dazu ein Waechter, den es vorher nicht gab, zwei
bestaetigte strukturelle Schulden (P10) und sieben neue Befunde. **Der Wert
dieses Korbs lag nicht in den geloeschten Zeilen.**
