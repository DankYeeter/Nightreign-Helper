# T-052 — Design-Review: was die beiden Kalibrierungen am Bildschirm angerichtet haben (ui-ux-designer)

```
STATUS: erledigt
AUFTRAG: T-052 — Design-Review der sichtbaren Folgen der 0,6-Kalibrierung
         (T-045) und der Katalysator-Kennzahl (T-046); QA-116/QA-117/QA-119/
         QA-121/QA-122 entscheiden (docs/tasks/T-052.md)
GELESEN: docs/tasks/T-052.md, GOAL.md, docs/state.md, UI_SPEC.md (komplett,
         inkl. §2.3, §3.2-3.4, AK-31 bis AK-52, Nachtrag zu AK-34/T-035,
         Nachtrag zu AK-47/T-037), DESIGN_REVIEW.md (komplett, DR-001 bis
         DR-007), qa/findings.md (Zeilen zu QA-116/117/119/121/122),
         docs/berichte/T-045-developer.md (komplett),
         docs/berichte/T-046-developer.md (komplett), ARCHITECTURE.md
         (AD-018 Umfeld, Zeile 513), nrplanner/arsenaltab.py,
         nrplanner/weaponslots.py, nrplanner/advisor/goals.py,
         nrplanner/damage.py (Auszuege); eigene Agent-Memory
         (project_nightreign_helper, feedback_headless_verification)
GEÄNDERT: UI_SPEC.md (fuenf neue Nachtrag-Abschnitte am Dateiende: QA-116/
         AK-63, QA-121/AK-34-Ergaenzung/AK-64, QA-117/AK-65, QA-119/AK-66 —
         nichts Bestehendes ueberschrieben, nur angehaengt);
         DESIGN_REVIEW.md (neuer Abschnitt „Review vom 2026-09-05" oben
         angefuegt, Findings DR-008 bis DR-012); fuenf Screenshots unter
         docs/screenshots/2026-09-05/ (build-planner-overview.png,
         arsenal-tile-spell-power-145.png, arsenal-recluses-staff-
         collision.png, weapon-slots-with-catalyst.png, weapon-slot-tile-
         wrap-zoom.png — 24 weitere Zwischenaufnahmen wieder geloescht, sie
         waren Fehlversuche/Debug-Krempel, kein Befund); eigenes
         Agent-Memory (.claude/agent-memory/ui-ux-designer/
         feedback_headless_verification.md, MEMORY.md — nicht Teil des
         Projekt-Commits im ueblichen Sinn, aber im Arbeitsbaum veraendert).
         qa/findings.md **nicht** angefasst — das Register gehoert dem
         qa-engineer, mein Auftrag nennt es nicht unter „Arbeitsbaum".
ANNAHMEN: (1) Der parallele QA-Retest laeuft auf demselben eingefrorenen
         Code-Stand; ich habe waehrend der Live-Pruefung eine Waffe in
         Slot 2 des Build-Planners eingesetzt (Carian Regal Scepter) —
         das ist Session-Zustand, laut Code-Kommentar in app.py nicht
         persistiert ("lasts the run of the program, no longer"), sollte
         also den QA-Lauf nicht beruehren, sofern QA nicht denselben
         laufenden Prozess weiterbenutzt. Ich habe den Programmprozess am
         Ende beendet. (2) Meine fuenf neuen UI_SPEC-Nachtraege beantworten
         die vier vom Auftrag genannten Fragen inhaltlich als Design-
         Entscheidung, nicht als reine Bestandsaufnahme — das ist der
         Auftrag ausdruecklich so ("Entscheide es als Vorgabe mit
         Akzeptanzkriterium"), aber ich nenne es hier nochmal explizit,
         falls der director einen kleineren Eingriff erwartet hat.
NÄCHSTER: developer (Umsetzung AK-63 bis AK-66, DR-008/DR-009), danach
         qa-engineer (Retest gegen die neuen Akzeptanzkriterien)
BLOCKIERT DURCH: nichts
```

## Methode

**Live, am laufenden Fenster** — zum ersten Mal seit dem 2026-09-01-Review
war das Fenster in dieser Sandbox tatsaechlich sichtbar und fokussierbar.
Gestartet mit `.venv\Scripts\python.exe run.py` (PowerShell `Start-Process`),
bedient ueber `System.Windows.Automation` (Tab-Wechsel, Textsuche,
Spinbox-Werte, Buttons, sogar den Doppelklick-Dialog einer Waffenkachel —
letzterer nur ueber eine echte `WM_LBUTTONDBLCLK`-Nachricht erreichbar, die
Accessibility-„Invoke" eines `WeaponTile`-Labels loest nur den
Einzelklick aus). Reale Spieldaten, realer Snapshot dieses Rechners.

**Wichtiger Methoden-Fund, kein Programmbefund:** Ein erster Rundgang zeigte
das dritte Panel (Waffenschaden, sechs Kacheln) und die Ecken-Werkzeugleiste
(`UI scale`, `Reset layout`) als reproduzierbar **vollstaendig verschwunden**
— bei mehreren Fenstergroessen, auch nach Betaetigen von „Reset layout". Das
sah nach einem kritischen Layout-Defekt aus, den ich beinahe als DR-Eintrag
geschrieben haette. Ursache war stattdessen die **eigene Screenshot-Methode**:
dieser Rechner laeuft mit 150 % Windows-Skalierung (physisch 2560×1600,
virtualisiert 1707×1067), und ein nicht DPI-bewusster PowerShell-Prozess
liefert ueber `CopyFromScreen` einen Ausschnitt, der den echten rechten
Fensterrand abschneidet, obwohl das Programm dort korrekt zeichnet. Nach
`SetProcessDPIAware()` verschwand der Effekt vollstaendig und blieb es bei
jeder weiteren Pruefung. Ich nenne das hier ausdruecklich, weil sonst ein
Phantombefund entstanden waere — Details und die Lehre daraus stehen in
meinem Agent-Memory, damit ein kuenftiger Durchlauf denselben Fehlschluss
nicht wiederholt.

Eine zweite, harmlosere Stoerung: eine unabhaengige, eigene Anwendung des
Nutzers ("Claude"-Desktop-Fenster) teilt sich den Desktop und hat wiederholt
den Fokus zurueckerobert, wodurch rohe Maus-Koordinatenklicks zweimal im
falschen Fenster landeten (kurz sichtbar, keine Aktion daraus abgeleitet,
keine Daten dieser fremden Anwendung im Bericht verwertet). Danach auf
Accessibility-Invoke statt Mausklick umgestellt, was zuverlaessig war.

## Was ich mir angesehen habe

Build-planner-Panel (Relic slots, das Waffenschaden-Panel rechts, alle sechs
Waffen-Slot-Kacheln — mit und ohne eingesetzten Katalysator), Arsenal-Tab
(`Weapons & spells`, Kachelraster und die Zusammenfassungszeile darunter, mit
gezielter Suche nach `Carian Regal Scepter` und `Recluse's Staff`), den
`WeaponDialog`-Auswahldialog. **Nicht erreichbar:** der Relic Picker mit
Berater-Anzeige (`UI_SPEC.md` §3) — S10 ist laut `docs/state.md` nicht
gebaut, dort gibt es nichts zu sehen; meine Antworten zu QA-116/QA-117
betreffen deshalb ausschliesslich die **Spec** fuer diesen noch nicht
gebauten Bildschirm, nicht das laufende Programm.

## Die vier Fragen aus dem Auftrag — Ergebnis

**QA-117 (Schwellen):** Bleiben absolut, wandern nicht mit 0,6 mit. Eine
Schwelle wie `>= 0.5` beschreibt die halbe kleinste darstellbare
Bildschirmeinheit, nicht eine Eigenschaft der Kalibrierung — sie mitwandern
zu lassen wuerde eine erfundene Umrechnung in die Oberflaeche selbst
einziehen, und keine neue Schwelle trifft „dieselben Faelle wie vorher"
(Rundung von Summen skaliert nicht linear mit dem Faktor, siehe T-045 §4.1).
Neues Akzeptanzkriterium AK-65 in `UI_SPEC.md`.

**Passt es? (live am Fenster):** Ueberwiegend ja. Die Arsenal-Kachel traegt
eine dreistellige `Spell power`-Zahl (145) ohne Umbruch und ohne Kuerzung —
siehe `docs/screenshots/2026-09-05/arsenal-tile-spell-power-145.png`. Die
Waffen-Slot-Kachel dagegen bricht die Zeile **mitten im Wort** „Spell power"
um (`Legendary · 145 Spell` / `power`), weil sie Bezeichnung und Wert zu einer
Zeichenkette verkettet statt sie wie der Arsenal-Tab in getrennte Zeilen zu
setzen — neuer Fund DR-009, mit Zoom-Beleg. Die Schadenstafel liest sich fuer
einen Katalysator korrekt (`Spell power 145 no change 145` statt `Total`).

**QA-121 (Zusammenfassungssatz):** Live bestaetigt, dass der Satz beim
Filtern auf ausschliesslich Katalysatoren nur noch die Haelfte des
Bildschirms beschreibt. Entschieden: ein zusaetzlicher Satz zwischen der
Attack-Rating-Definition und dem Zauber-Satz — *„Staves and seals show the
spell scaling the game displays for them instead of an attack rating."* —
nicht woertlich der Vorschlag des `developer` (der sagt „attack power" statt
„attack rating" und wuerde einen zweiten Namen fuer dieselbe Sache
einfuehren). Neues Akzeptanzkriterium AK-64.

**QA-119 (Namenskollision):** Live bestaetigt und mit Screenshot belegt —
zwei Karten „Recluse's Staff", identisch bis auf `Spell power 139` gegen
`92`, kein Merkmal auf der Karte erklaert den Unterschied. Entschieden, dem
Rat des `developer` folgend: die betroffene Zeile (kein Zauberplatz,
generische Reinforce-Gruppe, generische AEC — alle drei Kriterien innerhalb
der Katalysator-Familie eindeutig) wird aus jeder spielerseitigen
Waffenliste **gefiltert**, nicht durch eine sichtbare Id unterschieden. Eine
Id auf der Kachel loest das Problem nicht, sie verschiebt es nur auf den
Spieler. Neues Akzeptanzkriterium AK-66.

**QA-116 (UI_SPEC-Drift):** Bestaetigt: sechs Stellen, zwei Wortlaute, keiner
im Programmcode. Antwort: **keiner der beiden.** Beide sind seit T-046 durch
`GoalScore.unknowns` ueberholt — eine pro Zielrichtung eigene, praezisere
Satzliste, die im Code schon existiert. Ein fest verdrahteter
Attack-Rating-Satz waere fuer „Minimise damage taken" schlicht falsch
gewesen; das ist der eigentliche Fehler hinter der Drift, nicht nur ein
veralteter Text. §3.2 Zeile 4 und §3.4 Punkt 4 zeigen kuenftig die Saetze aus
`GoalScore.unknowns` der gewaehlten Zielrichtung, wortgleich. Neues
Akzeptanzkriterium AK-63. Betrifft nur den nicht gebauten Picker — kein Fund
am laufenden Programm, reine Spec-Korrektur.

## Was neu gefunden wurde und nicht im Auftrag stand

**DR-008 (Kritisch)** ist inhaltlich dieselbe Sache wie QA-119, aber ich habe
sie als eigenen, live verifizierten Fund mit Screenshot-Beleg eingetragen,
weil der Auftrag/QA sie bisher nur "unverifiziert (Code-Analyse/Messung)"
hatte — jetzt gibt es ein Bild, auf dem zwei Menschen sofort sehen wuerden,
dass hier etwas nicht stimmt. Ich stufe sie Kritisch ein (nicht nur Wichtig
wie die QA-Einordnung P2/Major): zwei ununterscheidbare Karten mit
unterschiedlichen Zahlen fuer denselben Namen verletzt A7 in der Anzeige
selbst, nicht nur in der Rechnung dahinter.

## Rueckgabe an den `developer`

Vier neue Akzeptanzkriterien in `UI_SPEC.md` (AK-63 bis AK-66, jeweils mit
Begruendung im zugehoerigen Nachtrag-Abschnitt) und zwei live verifizierte
Layout-Findings (DR-008, DR-009) mit Screenshot-Belegen in
`docs/screenshots/2026-09-05/`. Kein Anwendungscode von mir geaendert.

## Rueckgabe an den `qa-engineer`

QA-116, QA-117, QA-119, QA-121 sind mit Begruendung entschieden (siehe
`UI_SPEC.md`-Nachtraege) — Status-Aenderung in `qa/findings.md` ist eure
Sache, ich habe das Register nicht angefasst. QA-122 gilt aus meiner Sicht
als erledigt: die Oberflaeche wurde gesehen, mit Screenshots belegt.

---

## Gesamturteil

Braucht Arbeit an einer konkreten, jetzt bebilderten Stelle (DR-008/QA-119)
und einer kleineren (DR-009), sonst sind beide Kalibrierungen optisch
unauffaellig eingezogen. Details, alle Belege und die vollstaendige
Fund-Liste (DR-008 bis DR-012, plus Positiv-Abschnitt) stehen im neuen
Abschnitt „Review vom 2026-09-05" in `DESIGN_REVIEW.md`.

---

## Nachtrag (Coordinator-Auftrag nach Abgabe): AK-63-Korrektur nach AD-025,
## plus OF-20/QA-108 — 2026-09-05

```
STATUS: erledigt
AUFTRAG: Nachtrag zu T-052, vom director/coordinator direkt beauftragt
         (Nachricht "Zwei Nachtraege zu T-052..."): (1) AK-63 nach AD-025
         nachziehen (zwei Vorbehalts-Klassen brauchen zwei Wohnorte), (2)
         Wortlaut der konditionalen Zeile (OF-20/D2) und QA-108 (Wortlaut
         "of this colour" ist am weissen Slot falsch) festlegen
GELESEN: die Coordinator-Nachricht selbst; ARCHITECTURE.md Nachtrag VI
         (AD-025, Zeilen 2867-3018 und die Verbotsliste/OF-19/OF-20 ab
         Zeile 3400), nrplanner/advisor/candidates.py (komplett,
         `_without_a_handle_line`, `pool()`), nrplanner/advisor/types.py
         (`GoalScore`, `Goal`, `Baseline`, `SlotPool` — Auszuege, um zu
         pruefen, dass `Baseline.unknowns` noch nicht existiert und meine
         Vorgabe sich nur auf tatsaechlich vorhandene Felder stuetzt),
         nrplanner/model.py (`is_conditional`, `COLOUR_NAMES` — bestaetigt
         "White" = Index 4, kein Farbwert, den ein Relikt selbst traegt),
         qa/findings.md QA-108-Zeile, meinen eigenen T-052-Bericht/UI_SPEC-
         Stand von vorhin
GEÄNDERT: UI_SPEC.md — den Abschnitt "Nachtrag zu QA-116" **korrigiert**
         (Verbindlich/AK-63/Betroffene-AK-Teile ersetzt, mit sichtbarem
         Korrektur-Vermerk am Abschnittsanfang; Grundlage/Analyse-Text
         inhaltlich stehen gelassen, nur um einen AD-025-Satz ergaenzt) —
         AK-63 nennt jetzt zwei Quellen (`Goal.scope` fuer Zeile 4/Punkt 4,
         `SlotPool.unknowns` fuer eine neue Zeile 3b bzw. je Slot-Abschnitt
         in Punkt 2 des Why-Dialogs); neuer Abschnitt "Nachtrag zu OF-20 und
         QA-108" am Dateiende mit den Wortlauten (neu: AK-67). DESIGN_REVIEW.md
         — DR-011 um einen Korrektur-Absatz ergaenzt, der auf AK-67 und die
         AK-63-Korrektur verweist; nichts geloescht. Dieser Bericht (Nachtrag
         angehaengt, keine neue Datei). qa/findings.md weiterhin nicht
         angefasst.
ANNAHMEN: (1) `Baseline.unknowns`, das AD-025s "Wohnt-in"-Tabelle nebenbei
         nennt, existiert im heutigen Code nicht (geprueft: `Baseline` hat
         nur `goal_id`/`value`) und taucht in AD-025s eigener "Anwendung auf
         den heutigen Bestand"-Tabelle auch nicht auf — ich habe meine
         Vorgabe deshalb nur auf `Goal.scope` und `SlotPool.unknowns`
         gestuetzt, beide dort konkret belegt, und `Baseline.unknowns` nicht
         erwaehnt, um kein Feld vorzuschreiben, das (noch) nicht existiert.
         (2) Reihenfolge der beiden SlotPool-Saetze (Handle-Zeile vor
         konditionaler Zeile) ist meine eigene Entscheidung, im Auftrag nicht
         vorgegeben — Begruendung (steigende Rechenbeteiligung) steht im
         neuen UI_SPEC-Abschnitt, ist aber Geschmack/Ordnung, kein A7-Zwang;
         falls der `architect` oder `director` eine andere Reihenfolge fuer
         zwingend haelt, ist das eine offene Frage, keine von mir behauptete
         Notwendigkeit.
NÄCHSTER: developer (setzt AK-63/AK-64/AK-65/AK-66/AK-67 um; der Berater-Teil
         AK-63/AK-67 betrifft denselben parallel laufenden developer-Auftrag
         am Rechenkern, AK-64/65/66 die Oberflaeche), danach qa-engineer
BLOCKIERT DURCH: nichts
```

### Was inhaltlich korrigiert wurde

**AK-63 (Kern des Nachtrags):** Meine urspruengliche Fassung liess §3.2
Zeile 4 und §3.4 Punkt 4 ausschliesslich aus `GoalScore.unknowns` speisen.
Der `architect` hat parallel AD-025 beschlossen: `GoalScore.unknowns` traegt
kuenftig **nur noch** Laufbefunde, der Geltungsbereich (die acht Saetze aus
`_ATTACK_RATING_UNKNOWNS`/`_DAMAGE_TAKEN_UNKNOWNS`) zieht nach `Goal.scope`
um. Eine Vorgabe, die nur die alte Quelle liest, haette **nichts verloren**
fuer den Geltungsbereich (der zieht ja nur um), aber **den Ort fuer die
Laufbefunde vergessen** — Zeile 3 des Pickers ist schon die Pool-Zusammen-
fassung, nicht der richtige Platz fuer einen zusaetzlichen, unterschiedlich
langen Satz, und Zeile 4 ist an die Zielrichtung gebunden, nicht an den
Pool. Ich habe deshalb eine neue Zeile 3b eingefuehrt (gleiche Formatierung
wie Zeile 4, aber leer erlaubt und an den Pool statt an die Zielrichtung
gebunden) und im Why-Dialog die Laufbefunde in den Slot-Abschnitt verschoben
statt in den Dialogkopf — weil ein Laufbefund wie die Handle-Zeile eine
Aussage ueber **diesen** Pool ist, nicht ueber die Zielrichtung insgesamt.

**OF-20 (konditionale Zeile):** Wortlaut festgelegt, bewusst ohne
Beispiel-Bedingung in Klammern (die Effektzeile des einzelnen Relikts nennt
die Bedingung schon konkret; ein zweites, allgemeines Beispiel koennte fuer
den falschen Fall stehen und waere selbst eine kleine A7-Luecke).

**QA-108:** Die Diagnose des `director`/`architect` ist praeziser als meine
eigene erste Vermutung im Ursprungsbericht haette sein koennen — ich hatte
QA-108 nicht selbst nachgemessen, sondern nur zitiert. Jetzt geprueft: die
Anzahl war nie falsch (der Pool zaehlt schon ueber alles, was er anbietet,
Farbe inklusive), nur die Beschreibung "of this colour" unterschlaegt am
weissen Slot, dass mehrere Farben betroffen sein koennen. Fix ist ein
Ein-Wort-Austausch ("this" → "any") im selben Satzbau, keine neue Struktur.

### Rueckgabe

Vier neue/korrigierte Akzeptanzkriterien in `UI_SPEC.md` (AK-63 korrigiert,
AK-67 neu), alles Wortlaut-/Formfragen, keine Zahl und keine Zielfunktion
angefasst — wie AD-025 selbst verlangt ("keine Zahl, keine Zielfunktion,
kein Schwellenwert"). Kein Anwendungscode von mir geaendert.

---

## Zweiter Nachtrag (Coordinator-Auftrag): QA-113 als dritter Laufbefund in
## `SlotPool.unknowns`, AK-67-Obergrenze — 2026-09-05

```
STATUS: erledigt
AUFTRAG: Zweiter Nachtrag zu T-052, coordinator-beauftragt: (1) Wortlaut fuer
         den dritten SlotPool.unknowns-Satz (QA-113, vom developer als
         `[wording pending: QA-113]` freigehalten), (2) AK-67s Obergrenze
         „hoechstens zwei" pruefen/entscheiden (drei Saetze zulassen oder
         zusammenfassen, ohne eine der drei Aussagen zu verlieren)
GELESEN: die Coordinator-Nachricht selbst; meinen eigenen UI_SPEC-Stand vom
         ersten Nachtrag (Nachtrag zu OF-20/QA-108, AK-67); QA-113-Zeile in
         qa/findings.md; docs/state.md (F-F, die offene Frage zur Einbauhoehe
         von QA-113, "eine Ablesung im Spiel entscheidet"); ARCHITECTURE.md
         Nachtrag VI, AD-025, Tabelle "Anwendung auf den heutigen Bestand"
         (dort ist QA-113 als zweigeteilter Fall — Verfahrenssatz **und**
         Laufbefund — bereits vorgedacht; dieser Nachtrag deckt nur die vom
         Coordinator angefragte Laufbefund-Haelfte in `SlotPool.unknowns`,
         nicht die `Goal.scope`-Haelfte, die nicht Teil des Auftrags war)
GEÄNDERT: UI_SPEC.md — Abschnitt umbenannt in "Nachtrag zu OF-20, QA-108 und
         QA-113", mit sichtbarem Korrektur-Vermerk am Anfang; neuer
         Unterabschnitt "Die QA-113-Zeile" mit dem festgelegten Wortlaut
         (Einzahl/Mehrzahl) und der Begruendung, warum die vier Elemente
         ausgeschrieben werden duerfen (abgeschlossene Liste, kein
         Beispiel aus einer offenen Menge); AK-67 neu gefasst (bis zu drei
         Saetze statt zwei, Reihenfolge Handle → konditional → QA-113,
         explizite Klarstellung "keine Obergrenze unter drei" und "alle drei
         in derselben Zeile 3b als ein Fliesstext"); Absatz zur
         Doppelzaehlung (ein Relikt kann in mehreren der drei Zeilen
         mitzaehlen, keine Anzeigeentscheidung noetig, weil keine Zeile
         Relikte namentlich nennt). DESIGN_REVIEW.md — DR-011 um einen
         zweiten Korrektur-Absatz ergaenzt. Dieser Bericht (angehaengt).
         qa/findings.md, ARCHITECTURE.md, GOAL.md, docs/plan-restarbeiten.md,
         security/findings.md, docs/state.md zeigen sich im Arbeitsbaum
         ebenfalls veraendert — **nicht durch mich**, das sind die parallel
         laufenden Rollen (developer/power-user/qa-engineer), wie in der
         Nachricht angekuendigt. Kein Anwendungscode angefasst, keine
         laufende Instanz gestartet oder beruehrt (Vorgabe eingehalten:
         "fass die Oberflaeche nicht an, solange die beiden messen").
ANNAHMEN: (1) Der Auftrag bezieht sich ausschliesslich auf die
         Laufbefund-Haelfte von QA-113 (`SlotPool.unknowns`); die in
         AD-025s eigener Tabelle zusaetzlich vorgesehene Verfahrenssatz-
         Haelfte ("flache *AttackPower-Felder gehen in diese Zahl nicht
         ein", fuer `Goal.scope`) ist nicht beauftragt und wurde von mir
         nicht ergaenzt — falls sie noch fehlt, ist das eine offene Stelle,
         kein von mir uebersehener Teil dieses Auftrags. (2) Reihenfolge der
         drei SlotPool-Saetze (Handle → konditional → QA-113) folgt derselben
         "steigende Rechenbeteiligung"-Logik wie beim ersten Nachtrag; das
         ist meine Systematisierung, keine ausdrueckliche Vorgabe des
         Coordinators. (3) Die Entscheidung des `director`, dieselbe Relikt-
         Kopie in mehreren Zaehlungen zuzulassen, wird uebernommen und nicht
         in Frage gestellt (ausdruecklich so verlangt); ich habe lediglich
         begruendet, warum daraus keine Anzeigeentscheidung folgt.
NÄCHSTER: developer (uebernimmt den festgelegten dritten Wortlaut anstelle
         des Platzhalters, passt die Obergrenze/Reihenfolge in seiner
         Implementierung an), danach qa-engineer/power-user (laufen bereits,
         nicht von mir unterbrochen)
BLOCKIERT DURCH: nichts
```

### Der festgelegte dritte Wortlaut

> Einzahl: `1 of your relics changes what damage type your starting armament deals (to magic, fire, lightning, or holy). This figure does not count that change.`
> Mehrzahl: `{n} of your relics change what damage type your starting armament deals (to magic, fire, lightning, or holy). This figure does not count that change.`

Begruendung kurz: sagt, dass eine Umwandlung existiert und dass die Zahl sie
nicht zaehlt — keine Richtung, kein Betrag, weil beides erst eine
Spielmessung (F-F) hergeben kann. Die vier Elemente sind ausgeschrieben,
weil QA-113 sie als abgeschlossene Liste von genau vier Relikten nennt, nicht
als Beispiel einer offenen Menge (anders als die konditionale Zeile, wo ich
bewusst kein Beispiel genannt hatte).

### Die Obergrenze

Entschieden: **drei Saetze sind erlaubt**, keine Zusammenfassung. Zwei
Gruende: (1) Zeile 3b war schon im ersten Nachtrag als wachsender
Fliesstext angelegt (wie Zeile 4, die fuer manche Zielrichtungen bereits vier
bis fuenf Saetze traegt), nicht als festes Zeilenraster — ein dritter Satz
ist deshalb kein Strukturbruch, nur mehr Umbruch in derselben `QLabel`. (2)
Zusammenfassen haette genau das Risiko, vor dem die Director-Entscheidung
zur Doppelzaehlung warnt: eine der drei Aussagen wuerde verschwinden oder
undeutlich werden, sobald sie mit einer anderen in einem Satz verschmolzen
wird. Die vom Coordinator erwaehnte Anzeigeentscheidung (zwei Zeilen ueber
ein Relikt vermeiden) brauche ich nicht zu treffen, weil sie am Bildschirm
gar nicht vorkommt: alle drei Saetze sind Pool-weite Summen ohne Reliktnamen,
also sieht ein Spieler nie denselben Namen zweimal, nur zwei unabhaengige
Zahlen, die zufaellig teilweise dieselben Kopien zaehlen.
