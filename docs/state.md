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

## Zyklus 16 - der Release-Weg (Nutzerentscheid 07.09.2026)

Ziel **A9 und A2**. **A2 ist seit T-105 erfuellt** - SEC-009 behoben und
gegengeprueft; kein Hoch-Befund mehr offen, Bestaetigung durch den
`security-reviewer` steht aus.

**Falsche Praemisse, korrigiert 07.09.2026:** "es gibt bis heute keine EXE"
war falsch - **12 Releases, juengstes `v1.7.1` vom 24.08., 25 Downloads**.
A9 blieb offen (nie lief ein `qa-engineer` gegen ein Artefakt), aber der
Risikoweg ist das **Update**, nicht die Erstinstallation. Hergang im Verlauf.

**Gelaufen:** T-104 `compliance-agent` · T-105 `developer` (SEC-009) ·
T-106 `release-manager` `plan` · T-107 `technical-writer` · T-108
`compliance-agent` (C-004) · T-109 `developer` (1.8.0, A-020-Transport,
A-030-Waechter) · T-110 `archivist` `sync-out` · T-111 `build` · T-112
`technical-writer` · T-113 `clean-room` **CONCERNS, Artefakt freigegeben** ·
T-115 `power-user`. **T-114 `qa-engineer` laeuft - das ist A9 selbst.**

**Das Artefakt:** `dist/NightreignHelper.exe`, 59 010 777 B, SHA-256
`42B21AA2...F221`, `VersionInfo` 1.8.0. **Der Stand ist eingefroren, solange
T-114 laeuft.**

**Update-Weg belegt (T-113):** echtes `v1.7.1` von GitHub geladen und
gestartet, dann 1.8.0 darueber - `EXTRACT_VERSION` 8 auf 11, `__schema` auf 3,
**7 von 7 Builds namentlich erhalten**. Echte Nutzerdaten unangetastet.

**Isolierung fuer jeden Lauf am Artefakt - drei Umlenkungen, nicht zwei:**
`NIGHTREIGN_SETTINGS_ORG` (`favourites.py:25`) · `LOCALAPPDATA`
(`paths.py:20`) · **`APPDATA`** (`shortcut.py:44-49`). Am 07.09. fehlte die
dritte, und eine Verknuepfung landete im echten Start-Menue des Nutzers
(entfernt). QA-195 ist die Klasse dahinter.

**Stehende `power-user`-Messreihe, ab jetzt unveraendert kopiert:** Erststart
ohne Vorwissen · Spielstand finden lassen · im Build planner ein Relikt
tauschen · den Beratervorschlag anwenden · eine Zahl im Arsenal-Tab deuten ·
beenden und neu starten. Wortlaut in `docs/tasks/T-115.md`.

**Was die Veroeffentlichung noch sperrt:** nur **A-033** (Hinweispaket an alle
zwoelf Bestandsreleases, Text B aus `docs/release/RELEASE_TEXT.md`).
Nutzerentscheidung 07.09.: **W1**, fortsetzen und nachruesten; das Restrisiko
aus Paragraf 95a traegt der Nutzer bewusst, A-025 ist als GRAU geschlossen.

**Effizienz, erkannt 08.09. - noch nicht beauftragt:** jeder Lauf am Artefakt
baut den Datenabzug neu (107 s bis 5 min, viermal bezahlt), weil jede Rolle
ein eigenes umgelenktes `LOCALAPPDATA` bekommt. **Ein einmal gebauter,
schreibgeschuetzter Abzug fuer alle Leselaeufe** ist der groesste Hebel.
Zweiter: A8 und Teile von A4 sind am Artefakt auch ohne Fenster pruefbar -
nur A3, A5, A6 brauchen wirklich den Bildschirm.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | weitgehend — 197 QA, 24 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt** (T-105), QA-Bestaetigung offen |
| A3-A6 | der Build-Berater | **gebaut** — Kern, Leiste, Slotkarte, `Why`-Dialog, Anwenden/Halten, Picker |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend; **QA-186 offen** |
| A8 | alles Englisch | haelt, ohne Waechter (QA-192) |
| A9 | QA gegen ein **gebautes Artefakt** | **T-114 laeuft**; Artefakt gebaut und freigegeben |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ohne Raten ans Ziel | offen (QA-173) |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | Spec liegt (AK-106-132), Umsetzung offen |

## Beschlossen, nicht beauftragt

- **D-1** `performance-tuner` auf `model.compute` (94 % der 941,6 ms) — S11,
  Erstlauf im Projekt, also opus. · **D-11** doppeltes Zahlenformat: Waechter
  nach AK-136.
- **`compute_resistances`** — Zurueckstellung wieder offen: T-080 zaehlt 36
  stumme Zeilen auf einem Spielstand. Vor der Bestaetigung nachmessen.
- **QA-185, Klassenmassnahme:** vor der naechsten Aenderung entscheiden, ob
  `sources` durchgaengig ueber Ids gefuehrt wird. Latent (0 von 456 Paaren).
- **A16/A17**, spezifiziert in AK-182 bis AK-194, **nicht gebaut**. Zyklus 17.

## Buchfuehrung des Directors

**Drei Fehler am 07.09.**, alle gleicher Art — eine Notiz statt einer Messung:
SEC-022/SEC-024/QA-194 standen faelschlich auf "offen" · `AUFLAGEN.md` galt als
nicht vorhanden und existiert seit dem 01.09. · "keine EXE" (oben). Hergang im
Verlauf. **QA-196/QA-197 sind geklaert** und stehen in der Rollendefinition.

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
