# Stand

2026-09-07, **Zyklus 16 laeuft**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen — **Merge gehoert dem Nutzer.**
Verlauf: `docs/archiv/`. Reihenfolge: `docs/plan-restarbeiten.md`. Befunde:
`qa/findings.md`, `security/findings.md`. Auflagen: `docs/legal/AUFLAGEN.md`.
Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-108** · QA ab **QA-198** · SEC ab **SEC-026** ·
AK ab **AK-195** · AD ab **AD-027** · DR ab **DR-019** · R ab **R-007** ·
NH ab **NH-003** · C ab **C-004** · A (Auflagen) ab **A-033**.
**Suite:** **1256 passed, 9 skipped, 0 failed** (T-102, 07.09.). `pytest -n auto`
**127 s** statt 840 s seriell (`4431c7a`), Namensvergleich ueber 1265 Faelle ohne
Abweichung. **`-n auto` ist bewusst keine Voreinstellung** — eine einzeln
genannte Datei stiege von 1,2 auf 4,0 s, und genau die verlangt die Gegenprobe.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**; der Fragebogen
vor dem Zyklus haelt trotzdem an. **Die Pruefung im laufenden Spiel macht der
Nutzer ganz am Ende.**

## Zyklus 16 abgeschlossen, Zyklus 17 laeuft

**Zyklus 16 (Release-Weg), 08.09.2026:** A2 erfuellt (SEC-009 behoben) · **A9
geprueft** (T-114): A3, A4, A5, A7, A8 **PASS**, A6 **CONCERNS** mangels
Zielwert. 62 von 62 Modulen bytecode-identisch zum Quellstand, 440
Beraterlaeufe am **verpackten** Code ueber 10/10 Nightfarer und 74/74 Kelche,
0 Regelverstoesse. **A-033 ausgefuehrt und gegengeprueft:** 12 von 12 Releases
tragen das Hinweispaket, der Lizenzverstoss ist beendet (GPL § 8 endgueltig ab
07.11.2026). **Nichts sperrt die Veroeffentlichung mehr.**

**Artefakt:** `dist/NightreignHelper.exe`, 59 010 777 B, 1.8.0, SHA-256
`42B21AA2...F221`. Update-Weg an echtem `v1.7.1` belegt: 7 von 7 Builds
erhalten. **Nutzerentscheid 08.09.: 1.8.0 geht erst nach dem Fix-Stapel raus.**

**Zyklus 17:** **T-118** `performance-tuner` (S11) ✔ und **T-119**
`retrospective` ✔. **A6 hat seine Zahl** (S11, Abschnitt 2.2, woertlich nach
`GOAL.md` zu uebernehmen): Slot-Frage unter **500 ms** (gemessen 403 ms,
haelt) · `Optimize` unter **6 s** (5023 ms, haelt) · **Hauptthread hoechstens
50 ms — haelt nicht** (318 ms, QA-208). Entprellung **100 ms Picker / 250 ms
Gesamtlauf**, LRU **64 bedingt**. Alle fuenf Massnahmen L-014 bis L-018 sind
**angenommen und umgesetzt** (Agenten-Repo `486ac4e`, Projekt L-016).

**Der naechste Schritt ist der `architect`, nicht der `developer`:** QA-208 ist
eine Architekturentscheidung mit widerlegter Begruendung (Docstring nennt
51 ms, gemessen 318 ms). Danach `developer` mit den zwei Waechtern (QA-204,
QA-205) und dem Fix-Stapel, dann Pruefphase, dann neu bauen und ausliefern.

**Messumgebung, wichtig fuer jede kuenftige Zahl:** S11 hat gemessen, dass der
Rechner unter `Legion Quiet Mode` auf **1102 von 3201 MHz** lief. Jede Zahl aus
diesem Projekt gilt fuer diese Umgebung; wer sie vergleicht, nennt sie mit.
Genau daran scheitert der Vergleich mit D-1 (T-067 nannte keine Umgebung).
**E-1 gemessen:** der feste Testabzug spart **99,2 %** — 2,54 s Kopie gegen
293,8-310,1 s Neubau.

**Alle Projektzeilen fuer Auftraege stehen seit 08.09. in `CLAUDE.md`** —
Zielsystem, Testbefehl, die drei Umlenkungen, der feste Testabzug, Scratchpad
je T-Nummer, verbotene Zugriffe, Projektsprache. Auftraege verweisen darauf,
statt sie abzuschreiben (32-mal die Scratchpad-Regel, 7-mal die Umlenkungen).
Effizienzregeln E-1 bis E-3 in `docs/plan-restarbeiten.md`.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | weitgehend — 197 QA, 24 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt** (T-105), QA-Bestaetigung offen |
| A3-A6 | der Build-Berater | **gebaut** — Kern, Leiste, Slotkarte, `Why`-Dialog, Anwenden/Halten, Picker |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend; **QA-186 offen** |
| A8 | alles Englisch | haelt, ohne Waechter (QA-192) |
| A9 | QA gegen ein **gebautes Artefakt** | **5 von 6 PASS**, A6 offen bis S11 |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ohne Raten ans Ziel | offen (QA-173) |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | Spec liegt (AK-106-132), Umsetzung offen |

## Beschlossen, nicht beauftragt

- **D-11** doppeltes Zahlenformat: Waechter nach AK-136.
- **`compute_resistances`** — Zurueckstellung wieder offen: 36 stumme Zeilen
  auf einem Spielstand (T-080). Vor der Bestaetigung nachmessen.
- **QA-185, Klassenmassnahme:** vor der naechsten Aenderung entscheiden, ob
  `sources` durchgaengig ueber Ids gefuehrt wird. Latent (0 von 456 Paaren).
- **A16/A17**, spezifiziert in AK-182 bis AK-194, **nicht gebaut**.
- **L-014, L-015, L-017, L-018** — teamweite Massnahmen der Retrospektive,
  **beim Nutzer zur Freigabe**. L-016 ist umgesetzt.

## Buchfuehrung des Directors

**Acht Fehler in Zyklus 16**, alle derselben Form: eine Notiz wurde fuer eine
Messung gehalten. Fuenf falsche Befundstatus · die Praemisse "es gibt keine
EXE" (es gab zwoelf Releases) · ein Befund als Tatsache aus einer Messung
(QA-198) · eine falsche Aussage ueber Rollenrechte in `CLAUDE.md`. **Die
Regeln dagegen standen alle bereits woertlich in `commands/director.md`** —
die Ursache ist ihr Ort, nicht ihr Fehlen (L-014, belegt in T-119).
Alle drei Korrekturen des Zyklus kamen von **Rollen**, keine aus dem Bestand.

## Offen aus der Pruefphase (Zyklus 15)

QA-181 · QA-182 · QA-184 · **QA-186** · QA-188 · QA-190 · QA-191 · QA-192 ·
QA-193 · QA-195 · **SEC-025**. Wortlaut je Befund in `qa/findings.md` bzw.
`security/findings.md`.

**Neu aus Zyklus 16, alle am Artefakt gefunden:** **QA-198** (Erstaufbau sagt
"etwa eine Minute", gemessen 107 s bzw. 5 min - die Spanne ist der Befund) ·
**QA-199** (kein Weg, den Spielpfad von Hand anzugeben; dasselbe Loch wie
QA-171 von der anderen Seite) · **QA-200** (Arbeit geht beim Schliessen
verloren, ohne Warnung - am Code bestaetigt, `app.py:2000`; Entwurfsfrage an
den `ui-ux-designer`) · **QA-201** (die eigene Reliktzahl ist nicht auffindbar)
· **QA-202** (zweiter Start liest erneut ein, ungeklaert). **QA-170 ist mit dem
siebten Durchgang reproduziert** - zwei Laeufe, dasselbe Aufgeben.

## Der Rest — in dieser Reihenfolge

1. **Zyklus 16** (laeuft): der Release-Weg, A9. 2. **Zyklus 17**: der
Fix-Stapel oben, zwei parallele `developer` mit disjunkten Dateilisten, dann
parallele Pruefphase. 3. **A16/A17** (AK-182-194). 4. **A11** ueber QA-173.
5. **A15** mit QA-171, **S11** Budget. 6. **P4** · **P5** · **P7**.
Ausfuehrlich in `docs/plan-restarbeiten.md`.

## Beim Nutzer — offen

**Vor dem ersten Release zu entscheiden (C-003, 07.09.2026).** Ich lege sie
gebuendelt an der Stufengrenze vor Bau und Release vor; sie halten den
laufenden Zyklus **nicht** auf, weil Bauen und Pruefen keine Weitergabe ist.
- **A-025, GRAU:** Die EXE traegt die bekannten Entschluesselungsschluessel.
  Privatgebrauch ist straflos, **mit dem ersten Release-Asset wird aus Nutzung
  Verbreitung** (§ 95a Abs. 3 UrhG, EULA 10(i)). Risiko tragen oder vorher
  anwaltlich klaeren? Alternative ohne das Risiko: Quellcode statt EXE.
- Bleibt das Repo dauerhaft oeffentlich (LGPL haengt daran, A-022)? · Soll das
  Release beworben werden? · Beruehrt die Weitergabe deinen Arbeitsvertrag
  (seit C-001 offen)? · Eigener Auftrag zu US-Recht (17 U.S.C. § 1201)?

**Aus dem Audit, Messung im Spiel:** **F-B QA-096** Raider x1,18 auf
Greataxe/Great Hammer, keine Param-Quelle · **F-C QA-097** Cursed Claws x0,88
fuer alle ausser dem Revenant · **F-F QA-113** vier Relikte wandeln
Schadensart um, das Programm bewegt **exakt 0** (Grundwert 114, drei Lesarten
sagen 91 / 116 / 117).
- **F-G QA-170** Sortierung ueber Waffenkategorien hinweg waere eine **neue
  Funktion** · **Streichliste je Tab** (13 Vorschlaege, `UI_SPEC` §8).

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008 bis L-013;
projekteigen NH-001, NH-002. Neu 07.09. im Rahmenblock: **kein Hintergrundlauf,
auf dessen Ende der Agent wartet** · **ein Feldname ist keine Beschreibung**
(drei Gegenproben vor jedem Nutzertext an einem Datenfeld, Anlass QA-186).

**Nie geprueft:** Linux/macOS · eine echte Fremdinstallation.
