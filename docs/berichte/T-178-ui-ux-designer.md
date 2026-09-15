# T-178 — ui-ux-designer (Spec)

STATUS: erledigt
AUFTRAG: T-178 — Die Gesamtzahl der Relikte (QA-201, A11) und der ehrliche
         Erststart-Satz (QA-198), Spec-Modus
GELESEN: `docs/tasks/T-178.md` · `~/.claude/agents/_rahmen.md` · `CLAUDE.md` ·
         `ARCHITECTURE.md` (AD-029 Kontext/Punkte 1-3, AD-031, AD-006.8,
         Abschnittsuebersicht) · `UI_SPEC.md` (T-074 §0/§2 und die Wortlaute
         W1/C1/C2, T-141 vollstaendig samt AK-220 bis AK-229, T-148, T-154,
         T-163, Abschnittsuebersicht ueber alle 9060 Zeilen) ·
         `qa/findings.md` (QA-198, QA-201, QA-222, T-177-Block, T-176-Block) ·
         `DESIGN_REVIEW.md` (Abschnitt „Positiv / beibehalten", 01.09.2026) ·
         `docs/state.md` (ID-Register Zeile 11) ·
         Quelltext: `nrplanner/app.py`, `nrplanner/inventory.py`,
         `nrplanner/firstrun.py`, `nrplanner/relicpicker.py`,
         `nrdata/iconbuild.py`, `nrdata/savefile.py` (nur gelesen)
GEÄNDERT: `UI_SPEC.md` (nur angehaengt: neuer Abschnitt „Die Gesamtzahl der
         Relikte, und der Erststart ohne Zeitversprechen", Zeilen 9061-9639;
         nichts Bestehendes ueberschrieben). **Nicht committet.**
         `docs/berichte/T-178-ui-ux-designer.md` (diese Datei).
ANNAHMEN: keine. Die Messungen lagen vor (QA-198, T-176, T-177), der
         Auftrag zitierte A11/A12/A7 und den Stand aus `docs/state.md`
         woertlich; beides trug.
NÄCHSTER: director (Freigabe der drei offenen Fragen F-U/F-V/F-W durch den
         App Designer, dann `developer`)
BLOCKIERT DURCH: nichts

---

## 1. Was spezifiziert wurde

Ein neuer Abschnitt in `UI_SPEC.md`, 579 Zeilen, mit zwei unabhaengig
baubaren Teilen und **AK-250 bis AK-255**.

**Teil 1 — die Gesamtzahl (QA-201, A11, A12).** Eine eigene Zeile im linken
Bereich des `Build planner`, unmittelbar ueber `Rescan save` /
`Load equipped`, 12 px in gewoehnlicher Textfarbe, geschrieben von **genau
einer** Funktion.

**Teil 2 — der Erststart (QA-198).** Neuer Wortlaut fuer die Erklaerzeile in
beiden Faellen und fuer den dritten Satz mit demselben Versprechen im
Frage-Zustand W1; **der Balken bekommt keinen Fuellstand**, begruendet und
festgeschrieben.

## 2. Der Befund, der den Entwurf entschieden hat

**Die Zahl steht heute schon auf dem Bildschirm** — `309 relics in
USER_DATA000, 110 stored builds` — und ist trotzdem nicht auffindbar. Drei
Gruende, der dritte ist der schwerste:

1. 10 px `MUTED`, die kleinste Schrift des Fensters.
2. `relics in USER_DATA000` liest sich als Teilmenge an einem technischen Ort.
3. **`owned_label` wird an zehn Stellen beschrieben**
   (`grep -c "owned_label.setText" nrplanner/app.py` = 10) — der erste
   `Load equipped` loescht die Zahl. QA-201 hatte das schon notiert
   (*„Eine Statuszeile, die von der naechsten Meldung ueberschrieben wird, ist
   kein Ort fuer eine Bestandszahl."*); der T-177-Lauf ist derselbe Befund ein
   zweites Mal.

**Deshalb ist die Vorgabe keine neue Zahl, sondern ein eigener Ort fuer die
vorhandene.** Die Bestandsnotiz bleibt unveraendert — ein Umbau haette AK-224,
AK-228, AK-244 und AK-245 nachgezogen.

## 3. Die Akzeptanzkriterien (Kurzform, voller Wortlaut in `UI_SPEC.md` §10)

- **AK-250** Die Besitzzahl steht in einem **eigenen** Widget, nicht in
  `owned_label`, und ueberlebt alle vier `load_equipped`-Enden mit vorhandenem
  Bestand. *Positivkontrolle:* gegen die heutige Fassung **muss** die
  Vorrichtung anschlagen (die Zahl ist dort nach dem ersten `Load equipped`
  weg).
- **AK-251** Woertlich `You own <n> relics in total.` bzw.
  `You own 1 relic in total.`, Tooltip woertlich T2 mit `html.escape()`,
  `Qt.PlainText`; `<n>` ist dieselbe Zahl wie in der Bestandsnotiz
  (Zaehlwert gegen Zaehlwert).
- **AK-252** Solange kein Bestand vorliegt: **leer** — kein `0`, kein `…`,
  kein Wartesatz (AK-222 auf das neue Widget erweitert), in allen vier
  Faellen. Die Ankunft bewegt nichts im linken Bereich (AK-225 erweitert).
  **Messauflage an den `developer`** (Hoehe mit Umgebung, L-009).
- **AK-253** Erklaerzeile woertlich W-A/W-B, Absatz W1 woertlich W-C; **kein**
  Anzeigetext in `firstrun.py` nennt eine feste Dauer. Waechter mit
  **Positivkontrolle**, die heute zweimal anschlagen muss.
- **AK-254** Der Balken bleibt unbestimmt (Minimum und Maximum 0, kein Text);
  kein Prozentwert, keine Restzeit, keine verstrichene Zeit, keine
  Schrittzaehlung; **die gelobte Statuszeile bleibt woertlich und in
  Reihenfolge**.
- **AK-255** Die Hoehe des Bau-Zustands folgt seinem Inhalt, nie kleiner als
  heute, nichts abgeschnitten bei 100/125/150 % (dieselbe Pruefung wie
  AK-129). **Messauflage an den `developer`.**

**Kreis nachgeprueft:** hoechste belegte Nummer vor diesem Lauf war
**AK-249** (`grep -rn "AK-2(4[5-9]|5[0-9])"` ueber `UI_SPEC.md`,
`qa/findings.md`, `nrplanner/`, `tests/`, `docs/`). `docs/state.md` Zeile 11
nennt `AK ab AK-250` und stimmt damit ueberein — anders als beim letzten Mal,
wo die genannte freie Nummer schon vergeben war.

**Keine Zeit und kein Prozentwert in einem Kriterium.** Die vier gemessenen
Dauern stehen in der Begruendung (§6 der Vorgabe) und werden von keinem Test
behauptet.

## 4. Die Wortlaute (woertlich, Englisch — A8)

**T1** `You own 309 relics in total.` / `You own 1 relic in total.`
(ueber `_relic_count()`, `app.py:534-537`).

**T2** (Tooltip) `Counted from your save USER_DATA000. The number beside a
relic slot counts only the relics that fit that slot.`

**W-A** (Erststart) `Reading your installation. This happens once, and takes
minutes rather than seconds — sometimes several. The line below changes as it
goes.`

**W-B** (Neuaufbau) `Re-reading your installation so the numbers are up to
date. This takes minutes rather than seconds — sometimes several. The line
below changes as it goes.`

**W-C** (W1, ein Halbsatz getauscht) `… so this may be a different game.
Reading it takes minutes, and every number would be wrong.`

## 5. Die drei Entscheidungen, die ich getroffen habe, und warum

**(a) Der Balken bekommt keinen Fuellstand.** Gezaehlt, nicht geschaetzt: die
grossen Schritte sind **zwei** und vorher bekannt (`what_is_needed`), aber ein
Zwei-Schritt-Balken steht die halbe Wartezeit auf 0; die Gewichtung der
Haelften stammt aus einem Docstring, nicht aus einer Messung; und die feinen
Schritte sind **keine feste Zahl** — sieben Meldungen kommen immer, **eine nur
mit installiertem DLC** (`iconbuild.py:238`), **je Nightfarer ohne Portraet
eine weitere** (`iconbuild.py:123`, in der Schleife). Ein Nenner daraus waere
genau in den Faellen falsch, die er erklaeren soll. **Der ehrliche Satz traegt
allein**, wie der Auftrag es fuer diesen Fall vorgesehen hat.

**(b) Der Satz nennt keine Ursache.** „on a slow drive" oder „depends on your
machine" waere **durch die Messungen widerlegt**: QA-198 haelt fest, dass die
Spanne 107 s bis 5 min **auf derselben Maschine, demselben Artefakt und
demselben Spielstand** auftrat und die Ursache ungeklaert ist. `minutes rather
than seconds — sometimes several` kann nicht wieder falsch werden und
beantwortet trotzdem seine Frage („10 Sekunden oder 5 Minuten?").

**(c) Der Ort weicht vom Vorschlag des Spielers ab.** Er wollte die Zahl
*„neben `NIGHTFARER` oder irgendwo im Kopfbereich"*; sie steht bei den
Knoepfen des Spielstands, aus dem sie kommt. Der Kopfbereich gehoert der
Identitaet des Nightfarers. **Das ist der einzige Punkt seines Wunsches, dem
ich nicht folge** — er liegt als **F-U** dem App Designer vor.

## 6. Was die Vorgabe ausserdem beruehrt — vier Stellen ausserhalb meiner
##    Schreibgrenzen

Dasselbe widerlegte Zeitversprechen steht an **drei weiteren Stellen**; ich
darf sie nicht anfassen und melde sie:

1. **`README.md:80`** — *„First launch takes about a minute."* Nutzertext auf
   Englisch. Sollte mit W-A nachgezogen werden, sonst steht die falsche Zahl
   dort, wo ein neuer Nutzer zuerst liest.
2. **`scripts/setup_check.py:234`** — *„That takes about a minute, and is only
   needed once per patch."*
3. **`nrplanner/firstrun.py:5`** (Modul-Docstring) — kein Anzeigetext,
   deshalb **nicht** von AK-253 gefordert; der `developer` sollte ihn beim
   Bauen mitnehmen.

Und eine **Selbstkorrektur**:

4. **`DESIGN_REVIEW.md`, Durchlauf 01.09.2026, „Positiv / beibehalten"** —
   dort steht, der Erststart-Dialog *„nennt eine ehrliche Zeitangabe (»about a
   minute«)"*. Das war **diese Rolle**, aus einem Bildschirmabzug geurteilt und
   nie gemessen. **Die Aussage ist widerlegt.** Die Datei liegt ausserhalb der
   Grenzen dieses Auftrags; sie gehoert in den naechsten Review-Durchlauf.

**Zwei Stellen habe ich bewusst nicht angefasst**, obwohl der `power-user`
ueber sie gestolpert ist: die Slotueberschrift `(51 available)` (das Wort
`available` ist bereits die richtige Abgrenzung und wurde frueher
ausdruecklich so gewaehlt) und die Zusammenfassungszeile des Pickers
`54 of 54 relics · …` — sie ist **woertlich** in T-024 §3.2, in der Tabelle
des T-127-Abschnitts und in AK-200 festgeschrieben, samt Tests; eine
Umformulierung zoege vier bis fuenf Kriterien nach sich. Ob die Gesamtzahl
allein die Verwechslung aufloest, misst der naechste `power-user`-Lauf
(**F-W**).

**Die Architektur beruehrt die Vorgabe nicht.** Teil 1 schreibt im
Hauptthread an der Ankunftsstelle des Bestands (AD-029 und AD-006.8
unangetastet); Teil 2 kommt ohne neues Signal und ohne Zahl ueber die
Threadgrenze aus (`progress = Signal(str)` bleibt).

## 7. Offene Fragen an den App Designer

- **F-U (Ort der Gesamtzahl).** Ueber der Knopfzeile des Spielstands statt im
  Kopfbereich. **Empfehlung: so lassen wie vorgegeben.**
- **F-V (`You own` bei mehreren Charakteren).** Das Programm liest den
  bestbestueckten Charakterslot; wer zwei Charaktere mit verschiedenen
  Bestaenden hat, sieht die Zahl des volleren, und der Tooltip nennt den
  Spielstand dazu. **Empfehlung: so lassen** — die Alternative waere eine
  Auswahl im Bauplaner, ein eigenes Vorhaben.
- **F-W (die slotbezogenen Zahlen).** Erst messen (naechster
  `power-user`-Lauf), dann entscheiden — vier bis fuenf Kriterien haengen
  daran.

## 8. Was ich nicht geprueft habe, und ein Fund am Rande

- **Nichts gestartet, nichts gemessen, kein Bildnachweis.** Der Auftrag sagt
  ausdruecklich „du entwirfst, du misst nicht"; die drei Datenverzeichnisse
  waren deshalb nicht umzulenken, und ich habe das Programm nicht angefasst.
  Keine Aussage dieser Vorgabe stuetzt sich auf ein Fenster, das ich gesehen
  haette — die Diagnose steht auf dem Quelltext und auf zwei
  `power-user`-Laeufen.
- **Kein Prozess und kein Port zurueckgelassen.** Ich habe nichts gestartet;
  eine Hintergrundsuche (`grep -rn` ueber den ganzen Baum inkl. `dist/`) lief
  in ein Zeitlimit und wurde durch eine engere Suche ersetzt — sie hat den
  Baum nur gelesen.
- **Fremde uncommittete Aenderungen im Arbeitsbaum**, nicht von mir:
  `.github/workflows/release.yml` (+19/-1) und `docs/release/RELEASE_TEXT.md`
  (+12/-2). Der Auftrag sagt „Parallel laeuft nichts", der Startschnappschuss
  meldete einen sauberen Baum. **Der `director` sollte klaeren, woher sie
  stammen, bevor jemand committet** — ich habe sie nicht angefasst und
  committe nichts.
