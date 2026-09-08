# Stand

2026-09-08, **Zyklus 18 laeuft**. Branch `docs/audit-and-advisor-design`.
`main` ist geschuetzt, PR #16 offen, 411 Commits gegen `origin/main`
(`gh pr view 16` / `git rev-list --count`, 08.09.) — **Merge gehoert dem
Nutzer.** Verlauf: `docs/archiv/`. Reihenfolge: `docs/plan-restarbeiten.md`.
Befunde: `qa/findings.md`, `security/findings.md`. Auflagen:
`docs/legal/AUFLAGEN.md`. Berichte: `docs/berichte/T-###-<rolle>.md`.

**Nummernkreise:** T ab **T-129** · QA ab **QA-212** · SEC ab **SEC-026** ·
AK ab **AK-211** · AD ab **AD-030** · OF ab **OF-30** · DR ab **DR-019** ·
R ab **R-007** · NH ab **NH-003** · C ab **C-004** · A (Auflagen) ab **A-033**.
*AK stand bis 08.09. auf AK-195 — falsch, AK-195/196 sind am 07.09. vergeben
und AK-195 ist in `ea3d016` gebaut, von fuenf Testfaellen gehalten. Gefunden
vom `ui-ux-designer`, fuenfte Falschaussage des Directors an einem Tag.*
**Suite:** **1257 passed, 9 skipped, 0 failed** (T-109, unabhaengig bestaetigt
in T-111 und T-114 im frischen Klon). *Bis 08.09. stand hier 1256 aus T-102.*
Testbefehl und die Begruendung gegen `-n auto` als Voreinstellung: `CLAUDE.md`.

## Auftragslage (Nutzer)

Alle offenen Punkte abarbeiten, autonom, **erst zurueckkommen bei einer echten
Frage oder wenn alles fertig ist**. Fragen werden **gesammelt**; der Fragebogen
vor dem Zyklus haelt trotzdem an. **Die Pruefung im laufenden Spiel macht der
Nutzer ganz am Ende.**

## Zyklus 18 — was laeuft und woran er endet

Beauftragt am 08.09.2026, parallel, disjunkte Dateilisten:

- **T-122 `architect`** (opus) — AD-028 zu **QA-208** (der Picker-Weg des
  Beraters rechnet im Hauptthread, AD-018 ist an einer widerlegten Zahl
  gescheitert: Docstring 51 ms, gemessen 318 ms) und AD-029 zu **QA-209**
  (Spielstand-Lesen 6,15 s im Hauptthread, Gegenentwurf mit Faktor 45
  gemessen). Beruehrt nur `ARCHITECTURE.md`.
- **T-123 `developer`** — die zwei Waechter, `4d1955d` und `ad291e6`.
  **T-126 QA-Retest: CONCERNS** — QA-205 geschlossen (Mutation unabhaengig im
  eigenen Klon unter `pytest -n auto` rot), QA-204 nur teilweise, Rest als
  **QA-211** eingeplant. Suite **1264 passed, 9 skipped, 0 failed**.
- **T-124 `ui-ux-designer`** (Spec) — AK-197 bis AK-210, keine Millisekunde
  darin. **Muss nachgezogen werden**, F-P ging gegen seine Empfehlung.
- **T-125 `architect`** — AD-028 fortgeschrieben (Nachtrag IX): Picker-Spur
  **0 ms** Entprellung, bekannte Antwort im selben Aufruf, kanonische
  Zielrichtung im Cache-Schluessel. **Vorwaermen abgelehnt** (`pools()`
  rechnet gegen einen anderen Grundzustand). Damit bleibt der Wartezustand,
  und das leere Raster aus F-P wird gebaut.
  Naechste Schritte: **U5a** (haengt an nichts) → U5b → U6 → U7; **U1** (der
  Vorfilter aus AD-029) haengt ebenfalls an nichts.

**Erfolgreich**, wenn beide AD-Entscheidungen stehen, die zwei Waechter mit
belegter toetender Mutation laufen und die Suite gruen bleibt. Danach:
`ui-ux-designer` (nur falls AD-028 sichtbar wird) → `developer` (Fix-Stapel)
→ Pruefphase → Neubau → Release.

## Fuenf Nutzerentscheide vom 08.09.2026

1. **A6 hat seine Zahlen** — woertlich aus T-118 nach `GOAL.md` uebernommen:
   Slot-Frage im Median **unter 500 ms**, `Optimize` **unter 6 s**,
   **Hauptthread hoechstens 50 ms**. Damit ist **QA-203 geschlossen** und A6
   entscheidbar. Die 50-ms-Zeile ist heute verletzt (318 ms) — das ist QA-208.
2. **QA-207** (toter Verweis im Hinweispaket): **nur nach vorn reparieren.**
   Die zwoelf bereits veroeffentlichten Pakete bleiben unangetastet; A-021
   verlangt die Beilage, nicht einen Pfad, der Verstoss bleibt beendet.
3. **QA-209 kommt in den Fix-Stapel vor 1.8.0**, nicht danach — ein Neubau
   statt zwei. Verzoegert das Release um etwa einen Zyklus.

4. **F-P, gegen die Empfehlung des `ui-ux-designer` (Nutzer, 08.09.2026):**
   Der Relikt-Picker zeigt **ein leeres Raster bis zur Antwort** — keine
   Karten, keine Namen, keine Filtertreffer, waehrend der Berater rechnet.
   Keine Bewegung um den Preis einer kurzen Leere. **AK-197 bis AK-210 sind
   auf der Gegenoption geschrieben und muessen nachgezogen werden.**
5. **F-Q (Nutzer, 08.09.2026):** `Sort by` ordnet weiter bei **jedem** Schritt
   sofort um, auch beim Durchtippen mit Pfeiltasten. Bleibt wie gebaut.

## Stand gegen `GOAL.md`

| | | |
|---|---|---|
| A1 | Audit mit priorisierten Befunden | weitgehend — 209 QA, 25 SEC |
| A2 | kritisch/hoch behoben oder zurueckgestellt | **erfuellt** (T-105), QA-Bestaetigung offen |
| A3-A5 | der Build-Berater | **gebaut**, in T-114 am Artefakt bestaetigt |
| A6 | Oberflaeche blockiert nicht | **Zahl gesetzt**, dritte Zeile verletzt (QA-208) |
| A7 | sagen, wo die Daten nichts hergeben | weitgehend; **QA-186 offen** |
| A8 | alles Englisch | Waechter steht (`4d1955d`), **QA-211 offen** |
| A9 | QA gegen ein **gebautes Artefakt** | **5 von 6 PASS**, A6 wieder offen |
| A10 | jeder Tab nennt seine Frage | erfuellt, 6 von 6 |
| A11 | ohne Raten ans Ziel | offen (QA-173) |
| A12 | jede Zahl nennt Einheit und Bezug | 4 von 6 Tabs |
| A13 | Gestaltung, nichts abgeschnitten | 3 von 6 Tabs |
| A14 | QA bestaetigt je Tab einzeln | erfolgt (T-059) |
| A15 | Erststart fuehrt zu Daten | Spec liegt (AK-106-132), Umsetzung offen |

**Artefakt (Zyklus 16):** `dist/NightreignHelper.exe`, 59 010 777 B, 1.8.0,
SHA-256 `42B21AA2...F221`. Update-Weg an einem echten `v1.7.1` belegt.
**1.8.0 geht erst nach dem Fix-Stapel raus.**

## Beschlossen, nicht beauftragt

- **D-11** doppeltes Zahlenformat: Waechter nach AK-136.
- **`compute_resistances`** — Zurueckstellung wieder offen: 36 stumme Zeilen
  auf einem Spielstand (T-080). Vor der Bestaetigung nachmessen.
- **QA-185, Klassenmassnahme:** vor der naechsten Aenderung entscheiden, ob
  `sources` durchgaengig ueber Ids gefuehrt wird. Latent (0 von 456 Paaren).
- **A16/A17**, spezifiziert in AK-182 bis AK-194, **nicht gebaut**.

## Buchfuehrung des Directors

**Acht falsche Bestandsaussagen am 07./08.09.**, alle derselben Bauform: eine
Notiz wurde fuer eine Messung gehalten (`referenz/director-belege.md` B-22).
*Hier stand bis zum 08.09. "zwoelf" — die neunte derselben Bauform.* Die
Gegenmassnahmen sind **live**: `require-receipt.ps1`, `no-root-find.ps1`,
`remind-rules.ps1` (L-014), Pruefung 4 mit Quittung (L-015), "Regeln pflegen"
in `_rahmen.md` (L-017, L-018). Neu: **die fuenf Pruefungen stehen jetzt in
`templates/task.md`** — am 08.09. beschlossen, nie ausgefuehrt gewesen.

## Offen aus Zyklus 15 bis 17

QA-181 · QA-182 · QA-184 · **QA-186** · QA-188 · QA-190 · QA-191 · QA-193 ·
QA-195 · **QA-198 bis QA-202** · **QA-204 bis QA-209** · **SEC-025**.
Wortlaut, Adressat und Status je Befund in `qa/findings.md` bzw.
`security/findings.md` — **dort nachsehen, nicht hier**; diese Liste ist ein
Zeiger, kein Messwert. Reihenfolge: `docs/plan-restarbeiten.md`.

## Beim Nutzer — offen

**Vor dem ersten Release zu entscheiden (C-003, 07.09.2026).** Gebuendelt an
der Stufengrenze vor Bau und Release; sie halten den laufenden Zyklus **nicht**
auf, weil Bauen und Pruefen keine Weitergabe ist.
- **A-025, GRAU:** Die EXE traegt die bekannten Entschluesselungsschluessel.
  Privatgebrauch ist straflos, **mit dem ersten Release-Asset wird aus Nutzung
  Verbreitung** (§ 95a Abs. 3 UrhG, EULA 10(i)). Risiko tragen oder vorher
  anwaltlich klaeren? Alternative ohne das Risiko: Quellcode statt EXE.
- Bleibt das Repo dauerhaft oeffentlich (LGPL haengt daran, A-022)? · Soll das
  Release beworben werden? · Beruehrt die Weitergabe deinen Arbeitsvertrag
  (seit C-001 offen)? · Eigener Auftrag zu US-Recht (17 U.S.C. § 1201)?

**Aus dem Audit, Messung im Spiel:** F-B QA-096 · F-C QA-097 · F-F QA-113 ·
F-G QA-170 (neue Funktion) · Streichliste je Tab (13 Vorschlaege,
`UI_SPEC` §8). Wortlaut in `qa/findings.md`.

## Regeln

Gepflegt in `docs/plan-restarbeiten.md`, nur dort. Teamweit L-008 bis L-018;
projekteigen NH-001, NH-002.

**Nie geprueft:** Linux/macOS · eine echte Fremdinstallation.

## Nachtrag 08.09., waehrend T-128 laeuft (wird beim Zyklusende eingeordnet)

- **F-R (Nutzer, 08.09.2026):** Das Raster bleibt **immer** leer bis zur
  Antwort, auch bei `Sort by` = `Name`. Eine Oeffnungsart statt zweier.
- **Director-Entscheidung statt drittem Entwurfslauf:** W2 nimmt seine Form
  aus **AK-212**, nicht aus der ueberholten `PENDING`-Fassung des `architect`
  (W5s PENDING-Satz wird gegenstandslos, seine Zaehlung haelt). Die
  Sofortantwort aus **IX-1.C** ist keine Ersparnis mehr, sondern
  **Voraussetzung** — ohne sie blitzt bei rund 30 % Cache-Treffern das leere
  Raster auf. Beides dem `architect` und dem `developer` mitgeteilt.
- **Geprueft, nicht erinnert:** die Zusage "genau eines von `ready`/`failed`/
  `stopped`" steht als Docstring in `nrplanner/advisor/worker.py:144`;
  `tests/test_advisor_worker.py` haelt Einzelfaelle fest (`stopped` genau
  einmal, kein `ready` nach Abbruch), **kein Test prueft die
  Ausschliesslichkeit als solche** (gesucht am 08.09. in dieser Datei). Wird
  Waechter **W6** im Bauauftrag U6.
- **AK ab AK-220** (T-127 hat AK-211 bis AK-219 vergeben und AK-197, 198, 199,
  200, 202, 203, 209 gestrichen).

## Nachtrag 2, 08.09. (Zyklusende einordnen)

- **Nutzerentscheid 08.09.2026 zur Id-Annahme des Vorfilters:** Bricht ein
  Spielpatch die Annahme, faellt das Programm auf den **alten, langsamen Weg
  zurueck und sagt es** — statt den Spielstand fuer unlesbar zu erklaeren
  (so ist es aus T-133 gebaut). Begruendung: benutzbar bleiben, aber nicht
  stillschweigend (A7). **Auftrag offen**, Reihenfolge: erst der Wortlaut vom
  `ui-ux-designer` (zusammen mit der Wortlaut-Reibung an `app.py:3445`, das
  jeder `ValueError` "Save could not be read: " voranstellt), dann der
  `developer`.
- **Meine Zahl war falsch:** "haelt mittelbar ueber **drei** Aufrufer" ist aus
  T-131 uebernommen und nicht nachgezaehlt. Es sind **vier**
  (`worker.py:309, 334, 354, 380`), die vierte ist der haeufige Cache-Treffer.
  Gefunden vom `architect` in T-134.
- **Mir gehoert:** `W6` bezeichnet in `ARCHITECTURE.md` zwei verschiedene
  Waechter (AD-019-Kette und Picker). Umbenennung steht aus.
- **T-133 (U1) gemessen:** `read_owned_relics` **4835,3 → 93,3 ms (51,8x)**,
  28 von 28 Slots gleich, 543 Records, beide `.sl2`. Zwoelf Mutanten, zwoelf
  tot. Suite **1336 passed, 9 skipped, 0 failed**. *Das ist der Scan, nicht
  `inventory.load` — die Nachmessung ist U3.*
- **T-136 vor U3 gezogen** (Director): derselbe Walk steckt in
  `find_loadout_table`, **365 ms**, groesser als die 250-ms-Schwelle, an der
  AD-029 Stufe B haengt. U3 wuerde sonst einen Wert messen, den T-136 sofort
  verschiebt.

## Autonomer Lauf ab 08.09.2026 abends

**Auftrag des Nutzers:** *"Pruefe in welcher Reihenfolge die Aufgaben am besten
gehen. Dann arbeite alle nacheinander ab. Nimm dir die ganze Nacht Zeit. Mach
es fertig."*

**Warteschlange** (alle aus `GOAL.md`, keine selbst erfundenen Kriterien):
1. Zyklus 18 schliessen — U8 (AD-029 Stufe B), die zwei fehlenden U7-Messungen,
   Pruefphase (`qa-engineer` + `security-reviewer` parallel).
2. **A15** Erststart — spezifiziert AK-106 bis AK-132, **null Zeilen gebaut**
   (geprueft 08.09.: kein `QFileDialog`/`getExistingDirectory` in `nrplanner/`).
3. **A16/A17** — spezifiziert AK-182 bis AK-194, nicht gebaut (geprueft:
   kein `worst_case`/`best_case` in `nrplanner/`).
4. **A12/A13** — die restlichen Tabs.
5. Eine **einzige** Bau- und Pruefrunde: `compliance-agent` (`auflagen`) →
   `technical-writer` → `release-manager` (`build`, `clean-room`) →
   `power-user` → `notes`. A9, A11, A13 und der A15-Nachweis haengen alle am
   Artefakt; vier Runden dafuer waeren genau die Verschwendung aus E-2.

**Obergrenze:** die Nacht. Sie ersetzt "Stopp nach drei Zyklen"; **alle
uebrigen Stoppregeln gelten unveraendert.**

**Woran der Lauf endet:** an der Release-Schwelle. Bauen und Pruefen ist keine
Weitergabe; **das Release selbst haengt an den fuenf Rechtsfragen des Nutzers**
(A-025 GRAU und die vier daneben, C-003). Dort wird angehalten und vorgelegt.
Sofortiger Stopp ausserdem bei kritischem Sicherheitsbefund, Verdacht auf
Datenverlust, oder wenn zwei Zyklen in Folge kein Kriterium messbar naeher
bringen.

**Kein Merge.** Der Lauf endet pausiert auf `docs/audit-and-advisor-design`,
PR #16 bleibt beim Nutzer.

## Nutzerentscheid 08.09.2026 abends — Streichliste freigegeben

**Woertlich:** *"streiche alles doppelte und unnötige. verschiebe was nötig
ist. im nightlords bereich will ich keine kopfzeile. kann gern pro boss-karte
derselbe satz stehen. oder gar nicht da sein. mich interessiert ja nicht das
label der mit der 5. höchsten poise (oder so) ist."*

**Damit ist GOAL A10 erfuellt** — die Streichungen sind vom App Designer
entschieden, nicht vom Team. Die dreizehn Vorschlaege aus `UI_SPEC` §8 sind
freigegeben, samt der drei "verschieben statt loeschen". **Die fuenf
ausdruecklichen "nicht streichen" bleiben** — sie sind weder doppelt noch
unnoetig.

**Zusatzvorgabe Nightlords, enger als die Streichliste:** **keine Kopfzeile.**
Was auf jeder Boss-Karte identisch waere, steht entweder **auf jeder Karte**
oder **gar nicht** — nicht einmal oben. Der `ui-ux-designer` entscheidet je
Fall.

**Director-Auslegung, in den Auftrag zu schreiben:** der Zusatz
`(smallest Harmonia 75, largest Caligo 160)` faellt ersatzlos — sein einziger
Zweck ist der Vergleich der Bosse untereinander, und genau den nennt der Nutzer
uninteressant. `Stacks: yes — repeats compound` faellt ebenfalls: die
Streichliste vermerkt ihn als **ohne Datengrundlage**, und A7 verbietet eine
Aussage, die die Daten nicht hergeben.

**Zwei Fragen des `ui-ux-designer` aus T-141, ohne Rueckfrage nach seiner
Empfehlung entschieden** (der Nutzer schlaeft, beide sind klein und tragen
seine Empfehlung): **F-S** Rueckfallsatz **dauerhaft**, nicht einmal je Start ·
**F-T** Reliktknopf auch beim `Rescan` gesperrt. **Am Morgen vorzulegen.**
