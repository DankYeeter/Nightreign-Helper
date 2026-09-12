# Register der Architekturentscheidungen und offenen Fragen

*Angelegt am 12.09.2026 (T-182, `architect`). Dieses Register trifft **keine**
Entscheidung und aendert **keinen** Wortlaut. Es sagt nur, wo die heute
geltende Fassung steht und welche offene Frage noch offen ist.*

**Gemessener Stand:** `ARCHITECTURE.md` mit **5972** Zeilen, **21** H2-Abschnitte,
davon **11** Nachtraege/Korrekturen, **32** AD-Nummern, **32** OF-Nummern.
Nachgemessen am Arbeitsbaum, HEAD `e06386c` (der Auftrag nennt `de710a5`; beide
Staende liefern dieselben fuenf Zahlen, `de710a5` ist Vorfahr von `e06386c`).

## Wie die Fundstellen zu lesen sind

Zeilennummern sind die der **urspruenglichen** `ARCHITECTURE.md` in der Fassung
vom 12.09.2026. Dieselbe Reihenfolge und derselbe Wortlaut stehen nach der
Konsolidierung unveraendert in `docs/archiv/architecture-verlauf.md`; dort
verschieben sich die Nummern nur um den Kopf (Inhaltsverzeichnis). Massgeblich
ist deshalb **immer die genannte Abschnittsueberschrift**, die Zeilennummer ist
der Schnellzugriff.

**Zwei Nummernkreise tragen denselben Praefix.** `UI_SPEC.md` fuehrt einen
**eigenen** OF-Kreis. `UI_SPEC` OF-16 bis OF-19 sind **andere** Fragen als die
gleichnamigen aus `ARCHITECTURE.md` (siehe Befund B-3 in
`docs/berichte/T-182-architect.md`). Dieses Register fuehrt ausschliesslich den
OF-Kreis von `ARCHITECTURE.md` / `docs/state.md`.

---

## Tabelle 1 — Architekturentscheidungen (AD)

| AD-ID | Entscheidung in einer Zeile | geltende Fundstelle | zuletzt geaendert durch | ueberholt durch |
|---|---|---|---|---|
| AD-001 | Der Berater wird ein eigenes Paket, nicht ein Modul und nicht Teil von `app.py`. | `### AD-001`, Z. 295 | — (Urfassung 2026-09-01) | nichts |
| AD-002 | `model.compute()` ist die einzige Bewertungsautoritaet; kein zweiter, schnellerer Scorer. | `### AD-002`, Z. 331 | AD-021 (Z. 1974) erweitert die Zusicherung auf „nur die Fassade rechnet" | nichts |
| AD-003 | Beam-Suche ueber die Slots — nicht Vollprodukt, nicht Greedy, nicht Solver. | `### AD-003`, Z. 376 | Korrekturnotiz zu AD-003.5, Nachtrag VII, Z. 3878 | Ausgestaltung **Punkt 5** ersetzt (Z. 3880); der Rest steht |
| AD-004 | Zielrichtungen als Registry reiner Funktionen `Build -> GoalScore`, mit ausdruecklicher Unwissensliste. | `### AD-004`, Z. 476 | Praezisierung AD-004, Nachtrag VI, Z. 3166 (die `unknowns` zerfallen, konditionale Zeile bekommt den Ort D2) | nichts; AD-025 (Z. 2921) praezisiert, hebt nicht auf |
| AD-005 | Die Attack-Rating-Rechnung wandert aus `app.py` nach `nrplanner/damage.py`, **bevor** der Berater gebaut wird. | `### AD-005`, Z. 621 | AD-019 (Z. 1687) erweitert um die gemeinsame Fassade | nichts |
| AD-006 | Hintergrundlauf ueber `QThread` + Worker-Objekt + Signale, mit kooperativem Abbruch. | `### AD-006`, Z. 660 | AD-028 (Z. 3985) praezisiert; Punkte 6.7/6.8 beruehrt von AD-029 (Z. 4213) | nichts |
| AD-007 | Ergebnis-Cache nur im Speicher (LRU), nichts auf Platte. | `### AD-007`, Z. 753 | AD-016 (Z. 1421) und AD-028 (Z. 3985) praezisieren; Schluesselform durch Nachtrag VI D3 (Z. 3257) | nichts |
| AD-008 | Das Suchproblem wird ueber die kanonisierte Slot-Farbmenge geschluesselt, nicht ueber die Gefaess-Id. | `### AD-008`, Z. 802, **zusammen mit** Nachtrag VI, Z. 3311–3319 | Praezisierung AD-016 (D3, QA-107), Nachtrag VI, Z. 3257 | **teilweise:** als **Cache-Schluessel** abgeloest (Z. 3313); als **Pruefaequivalenz** ausdruecklich **nicht** abgeloest (Z. 3319) |
| AD-009 | Testsockel headless, ohne neue Laufzeit-Dependency. | `### AD-009`, Z. 839 | Praezisierung AD-009 (D4), Nachtrag VI, Z. 3342 — die Pruefpunktnummer 18 war zweimal vergeben | Werkzeugwahl auf `pytest` geaendert (OF-2); Pruefpunktliste fortgeschrieben durch Nachtraege I–VI |
| AD-010 | Die Unwissensliste ist Teil des Ergebnisses, nicht eine Fussnote in der Oberflaeche. | `### AD-010`, Z. 914 | Praezisierung AD-010, Nachtrag VI, Z. 3226; danach AD-026, Nachtrag VII, Z. 3584 | nichts |
| AD-011 | Pruefvokabular als freie Funktionen in `binary.py`, nicht als Methoden der `Reader`-Klasse. | `### AD-011`, Z. 958 | — (vom `director` angenommen 2026-09-01) | nichts |
| AD-012 | Kein `defusedxml`; stattdessen Groessendeckel vor dem Parsen. | `### AD-012`, Z. 1046 | — (angenommen samt Neubewertungs-Bedingung) | nichts |
| AD-013 | Ein Vorschlag ist eine Menge von **Handles**, nicht von Rollen; ein belegtes Exemplar faellt aus dem Kandidatenraum. | `### AD-013`, Z. 1112 | AD-030 (Z. 5420) beruehrt es (gemerkter Pfad, Handle-Vergabe) | nichts |
| AD-014 | Ein festgehaltener Slot ist **Randbedingung** der Suche, nicht Startwert: er geht als Grundzustand in jede Bewertung ein. | `### AD-014`, Z. 1190 | AD-017 (Z. 1474) praezisiert Punkt 14.8 | nichts |
| AD-015 | Fluechte gehen als gewoehnliche Effekte in dieselbe `compute()`-Bewertung; ausgewiesen werden sie aus `Build.sources`. | `### AD-015`, Z. 1355 | Korrekturnotiz zu AD-015, Nachtrag VII, Z. 3840 | Absatz „Pflichtzeile in `unknowns` …" **ersetzt** (Z. 3842); der Rest steht |
| AD-016 | Der Haltezustand geht in Kanonisierung, Cache-Schluessel und Generationszaehler ein. | `### AD-016`, Z. 1421, **Punkte 2 und 4 jedoch** in Nachtrag VI, Z. 3297 | Praezisierung AD-016 (D3, QA-107), Nachtrag VI, Z. 3257 | **Punkt 2 und Punkt 4 ersetzt** (Z. 3297); `held_fingerprint` entfaellt |
| AD-017 | Der Haltezustand gehoert zum Paar (Nightfarer, Gefaess) und lebt im Fenster, nicht auf Platte. | `### AD-017`, Z. 1474 | — | nichts; Reichweite der Begruendung praezisiert durch AD-030, Z. 5450–5458 |
| AD-018 | Hauptweg des Beraters ist der **Grenzbeitrag je Kandidat im Picker**; der Gesamtlauf bleibt als zweite Frage bestehen. | `### AD-018`, Z. 1547 | AD-028 (Z. 3985) | **Punkt 4 und die Laufzeittabelle** (Korrekturkasten Z. 1628) durch AD-028; die Sache selbst steht |
| AD-019 | Eine gemeinsame Fassade ueber beiden Rechenschichten, kein zweiter Waechter ueber `weapons.rate`. | `### AD-019`, Z. 1687 | AD-022 (Z. 2039) praezisiert die Benennung; AD-023 (Z. 2107) korrigiert das Invarianzargument | nichts |
| AD-020 | Was die Fassade ausdruecklich **nicht** vereinheitlicht (Randbedingung von AD-019). | `### AD-020`, Z. 1902 | AD-024 (Z. 2188) ergaenzt | nichts |
| AD-021 | Der Waechter sichert nicht „ein Aufrufer", sondern „nur die Fassade rechnet" — dasselbe Werkzeug, zwei Zusicherungen. | `### AD-021`, Z. 1974 | — | nichts |
| AD-022 | Ein Name je Schicht: `scaled_*` vor der Multiplikatorschicht, `final_*` danach; Umbenennung als eigener Schritt W1b vor W2. | `### AD-022`, Z. 2039 | — | nichts |
| AD-023 | Das Invarianzargument aus Nachtrag III gilt nur fuer Multiplikatoren des Grundzustands; fuer Kandidaten mit eigener Angriffsrate kann W6 die Reihenfolge drehen. | `### AD-023`, Z. 2107, **mit** „Korrektur an Nachtrag III", Z. 2799 | — | **korrigiert Nachtrag III** (Z. 2802: die dortige Invarianzaussage ist an dieser Stelle falsch) |
| AD-024 | Summationsreihenfolge ist eine **Eindeutigkeits-**, keine Genauigkeitsentscheidung; sie wird nur geaendert, wo sie zwei Darstellungen derselben Zahl beseitigt. | `### AD-024`, Z. 2188 | — | nichts |
| AD-025 | Ein Vorbehalt gehoert entweder der Registry oder dem Ergebnis; die Frage „kann der Satz geschrieben werden, bevor der Lauf bekannt ist?" entscheidet, welchem. | `### AD-025`, Z. 2921 | — | nichts |
| AD-026 | Eine unerfuellte Waffentyp-Schranke ist eine herstellbare Bedingung und bleibt in `Build.situational`; falsch ist nicht die Rechnung, sondern der Docstring. | `### AD-026`, Z. 3584 | — | nichts |
| AD-027 | **Nie vergeben.** Die Nummer existiert in keiner Datei des Arbeitsbaums; sie bleibt eine Luecke und wird nicht neu belegt. | Buchfuehrungsnotiz Nachtrag VIII, Z. 3978 | `docs/state.md` fuehrt den Kreis seit 08.09.2026 ab AD-030 | entfaellt |
| AD-028 | Der Picker-Weg verlaesst den Hauptthread ueber eine **zweite Instanz derselben** `AdvisorController`-Klasse. | Sache und Kontext: `### AD-028`, Z. 3985. **Geltender Wortlaut** der Punkte 1–4 und von W3: Nachtrag IX, Z. 4475–4959. **Geltender Vertrag** und W1: Nachtrag X, Z. 4960–5369. | Nachtrag X (2026-09-08, T-134) | **schichtweise, jede Stelle ausdruecklich markiert:** Punkte 1–4 + W3 + U5a/U5b/U6/U7 durch Nachtrag IX (Inline-Klammern Z. 4070, 4072, 4081, 4097, 4111, 4183; U-Tabelle Z. 4382); W1 und der Controller-Vertrag durch Nachtrag X (Inline-Klammer Z. 4167, Fassung 2 in Z. 5213). **Kein Widerspruch: IX und X beruehren disjunkte Punkte.** |
| AD-029 | Das Lesen des Spielstands wird **zuerst am Lesen selbst** repariert; die Verlagerung in einen Worker ist Stufe B und haengt an einer Messung mit benanntem Ausloeser. | `### AD-029`, Z. 4213 | AD-031 (Z. 5668) | **Vertrauensgrenze Punkt 3 abgeloest** durch AD-031 (Markierung Z. 4330, Wortlaut des Abgeloesten Z. 5670); der Rest steht |
| AD-030 | Der gemerkte Pfad lebt in **zwei festen Schluesseln** des vorhandenen Speichers, und das Programm hat **einen** Ort, an dem es den Spielordner aufloest. | `### AD-030`, Z. 5420 | — (2026-09-08, Nachtrag XI) | nichts |
| AD-031 | Bricht die Id-Annahme, **waehlt** der Scan den langsamen Weg, statt zu verweigern; der langsame Weg wird dafuer wieder gebaut. | `### AD-031`, Z. 5668 | — (2026-09-08, Nachtrag XI) | nichts |
| AD-032 | **Vergeben am 12.09.2026 (T-189), Status `offen`:** worauf „Schaden maximieren" rankt, seit keine Waffe mehr in die Zahl eingeht — vier gemessene Optionen (A so lassen 26/210 · B Startarmatur des Nightfarers als feste Bezugswaffe 51/210 · C Attribute als eigene Zielrichtung 53/210, mit A zusammen 75 · D Erwartungswert ueber die Waffentypen 81/210), vorgelegt und **nicht entschieden**. Enthaelt zugleich die Empfehlung zu QA-226 (die gewuerfelten Armaturen-Buffs fallen). | `### AD-032`, Themenbereich C, unmittelbar vor `## Themenbereich D` (Stand `b8f71a8` + T-189: Z. 2936) | — (Urfassung 2026-09-12, T-189) | entfaellt — noch nichts zu ueberholen |

**Eine der 32 AD-Nummern ist keine Entscheidung** (AD-027 nie vergeben), und
**eine ist eine vorgelegte, noch nicht getroffene** (AD-032). Getroffene
Entscheidungen: **30**.
**`widerspruechlich`-Faelle: 0** — jede Ueberholung ist an ihrer Stelle
ausdruecklich markiert.

**AD-032 ist die erste Zeile dieses Registers mit Status `offen`.** Sie wird
zur normalen Zeile, sobald der App Designer eine der vier Optionen waehlt;
bis dahin ist die geltende Fassung der **gebaute** Zustand, also Option A.

---

## Tabelle 2 — Offene Fragen (OF)

**Stand-Werte:** `beantwortet durch …` nur, wo eine Fundstelle die Antwort
belegt · `offen`, wo keine Antwort im Bestand steht · `unklar`, wo eine
Aussage die Frage beruehrt, sie aber nicht entscheidet.

| OF-ID | offene Frage | Stand (offen / beantwortet durch …) | Fundstelle |
|---|---|---|---|
| OF-1 | Tkinter oder PySide6? | **beantwortet** — Fehler in der Auftragsdatei; es ist PySide6, AD-006 steht auf Qt-Grundlage. | `ARCHITECTURE.md` Z. 2417 (Erledigt-Tabelle); `GOAL.md` Rahmen („Korrektur 2026-09-01") |
| OF-2 | Welches Testwerkzeug? | **beantwortet** — `pytest` freigegeben, ausschliesslich als Entwicklungs-Abhaengigkeit. | `ARCHITECTURE.md` Z. 2418; AD-009 Kopf, Z. 839 |
| OF-3 | Gewichtung der acht Schadensarten fuer `min_damage_taken` — welche Werte, und bekommt der Spieler ein Bedienelement? | **offen** — beim Nutzer ueber `director`. Der Director-Nachtrag vom 01.09.2026 fuehrt sie ausdruecklich als „noch beim Nutzer"; keine spaetere Entscheidung im Bestand. `UI_SPEC` fuehrt den Wortlaut fuer diesen Fall weiter als unberuehrt. | `ARCHITECTURE.md` Z. 564 und Z. 2428; `UI_SPEC.md` „Der Wortlaut, wenn OF-3 ein Bedienelement … bringt" (Z. 4852); `qa/findings.md` QA-105 |
| OF-4 | Soll der Berater auch das Gefaess vorschlagen? | **beantwortet** — nein, Entscheidung des Nutzers; als Nicht-Ziel aufgenommen. | `ARCHITECTURE.md` Z. 2419, Nicht-getan-Eintrag Z. 2398 |
| OF-5 | `max_damage` ohne Referenzwaffe — verweigern oder rechnen? | **beantwortet** — gekennzeichneter Rueckfall, nicht verweigern. | `ARCHITECTURE.md` Z. 558 (Director-Beschluss) und Z. 2420; verschaerft durch `GOAL.md` A17 |
| OF-6 | Ist `GOAL.md` freigegeben? | **beantwortet** — erteilt, A1–A9 bindend. | `ARCHITECTURE.md` Z. 2421; `GOAL.md` Kopf („FREIGEGEBEN … 2026-09-01") |
| OF-7 | Echte Bestandszahlen statt Schaetzungen. | **beantwortet** — vom `qa-engineer` gemessen: 309 Relikte, weisse Slots als Slot-Eigenschaft, Dedup wertlos. | `ARCHITECTURE.md` Z. 50 und Z. 2422; `qa/findings.md` „Nachmessung OF-7", Z. 153 |
| OF-8 | `defusedxml` aufnehmen? | **beantwortet** — nein; Groessendeckel, mit Neubewertungs-Bedingung (AD-012). | `ARCHITECTURE.md` Z. 2423; AD-012, Z. 1046 |
| OF-9 | Auf die Pruefung durch den `security-reviewer` warten? | **beantwortet** — nein; der `director` gibt die Deckelwerte direkt in den Auftrag. | `ARCHITECTURE.md` Z. 2424 |
| OF-10 | Braucht ein **weisser** Slot ein eigenes, hoeheres K? (K=20 behaelt dort nur ~10 % von 205 Kandidaten.) | **offen** — an den `performance-tuner` fuer S11. Volltextsuche ueber `docs/perf/baselines.md`, `qa/findings.md` und alle Berichte: ausserhalb von `ARCHITECTURE.md` kein einziger Treffer, also auch keine Messung. Im Entwurf selbst als „schaerfste bekannte Schwaeche des Verfahrens" gefuehrt. | `ARCHITECTURE.md` Z. 2436; Risikozeilen Z. 2349 und Z. 2508; AD-014, Z. 1270 |
| OF-11 | Wie viele der 309 Kopien haben `OwnedItem.handle is None` und fallen damit aus dem Kandidatenraum? | **offen** — an den `qa-engineer`. Ausserhalb von `ARCHITECTURE.md` kein Treffer im ganzen Repository. | `ARCHITECTURE.md` Z. 2444; AD-013, Z. 1112 |
| OF-12 | Ueberlebt der Haltezustand den Wechsel von Gefaess, Nightfarer oder Deep-Schalter? | **beantwortet durch den Nutzer (02.09.2026)** — anders als vorgeschlagen: persistent **im Gefaess**, sonst flexibel; umgesetzt in AD-017. | Frage: `ARCHITECTURE.md` Z. 2540. Antwort: Nachtrag II, Z. 2572, und AD-017, Z. 1476; Nutzerwortlaut in `GOAL.md` „OF-12 — Haltezustand: gehoert zum Gefaess" |
| OF-13 | Zielfremde Fluechte: nennen, abwerten oder ausschliessen? | **beantwortet durch den Nutzer (02.09.2026)** — nennen, nicht abwerten; eine Abwertung braeuchte erfundene Gewichte und verstiesse gegen A7. | Frage: `ARCHITECTURE.md` Z. 2549. Antwort: Nachtrag II, Z. 2570; `GOAL.md` „OF-13 — zielfremde Fluechte" |
| OF-15 | Soll der Haltezustand einen **Programmneustart** ueberleben? | **beantwortet durch den Nutzer (02.09.2026)** — nein; er lebt am `Planner`, gebunden an (Held, Gefaess, Deep). **Randbedingung nachtraeglich praezisiert:** AD-030 zeigt, dass OF-15s Begruendung „kein neuer persistenter Zustand" fuer den Haltezustand galt und den A15-Pfadspeicher nicht deckt. | Frage: `ARCHITECTURE.md` Z. 2631. Antwort: `GOAL.md` „OF-15 — Haltezustand ueberlebt keinen Programmneustart". Reichweite: AD-030, Z. 5427–5458 |
| OF-16 | Die Spielmessung zu QA-018, die `MULTIPLIERS_FOR[Basis.CANDIDATE]` bestimmt — sie blockiert ab W5 die angezeigte Zahl. | **offen** — sie kann nur der Nutzer am laufenden Spiel schliessen; `GOAL.md` fuehrt QA-018 unveraendert als offenes Risiko. **Nicht verwechseln** mit `UI_SPEC` OF-16 (der 60-%-Satz) — anderer Nummernkreis, andere Frage. | `ARCHITECTURE.md` Z. 2744; `GOAL.md` F2 „Offenes Risiko"; `UI_SPEC.md` Z. 564, 588, 641 fuehren den Fall nach Fassung A/B, ohne die Messung zu ersetzen |
| OF-17 | Darf `tests/golden/weapon_damage.json` bei W3/W4 neu aufgenommen werden? | **beantwortet durch den `director`** — ja, aber erst wenn Pruefpunkt 18 gruen ist, und die AD-019-Begruendung gehoert in die Commit-Nachricht. | Frage: `ARCHITECTURE.md` Z. 2750. Antwort: `qa/findings.md` Z. 794 („OF-17 entschieden: ja …") |
| OF-18 | Machen die Spaltennamen die drei Fragen `Basis.EQUIPPED` / `CANDIDATE` / `BARE` unterscheidbar? | **offen** — vom `director` an den `ui-ux-designer` weitergereicht, aber keine Stelle im Bestand fuehrt OF-18 als entschieden. `UI_SPEC` legt Wortlaute **fuer den CANDIDATE-Fall** fest (Fassung A/B), nicht die Unterscheidbarkeit der drei. **Nicht verwechseln** mit `UI_SPEC` OF-18 (zwei Zahlen je Karte). | `ARCHITECTURE.md` Z. 2756; Weitergabe `qa/findings.md` Z. 804; `UI_SPEC.md` Z. 641–646, Z. 1005 |
| OF-19 | `UI_SPEC` AK-63 nennt eine Quelle fuer Zeile 4, wo es nach AD-025 zwei gibt — Spec nachziehen, bevor S10 gebaut wird? | **beantwortet durch T-084 (`ui-ux-designer`, 2026-09-05)** — AK-63 ersetzt durch AK-162 bis AK-166; die Luecke lag noch dazu an einer dritten Stelle (`Baseline.unknowns`/`weights_note`). | Frage: `ARCHITECTURE.md` Z. 3485, Risikozeile Z. 3431. Antwort: `docs/archiv/berichte/T-084-ui-ux-designer.md` §1 („Entschieden."); `DESIGN_REVIEW.md` Z. 330–345 |
| OF-20 | Wortlaut der konditionalen Zeile („N of your relics …"). | **beantwortet** — AK-67 legt den Wortlaut der `SlotPool.unknowns`-Saetze fest; der Platzhalter `[wording pending OF-20]` wurde deshalb umbenannt und spaeter ersetzt. | Frage: `ARCHITECTURE.md` Z. 3498 (auch Z. 3220, Z. 3459). Antwort: `DESIGN_REVIEW.md` Z. 342 (AK-67); Beleg fuer den Abschluss: `docs/lessons.md` Z. 417 („weil OF-20 inzwischen beantwortet war") |
| OF-21 | Wo gehoert die Formatierung einer **Differenz** je Zielrichtung hin (`+12.4 AR` gegen `−18`)? | **offen** — `UI_SPEC` fuehrt sie an zwei Stellen ausdruecklich als **unberuehrt**. | Frage: `ARCHITECTURE.md` Z. 3505 (auch Z. 3162, Z. 3443). Stand: `UI_SPEC.md` Z. 3827 und Z. 4851 („Unberuehrt.") |
| OF-22 | AD-008s zweites Argument (Pruefaequivalenz, 26 bzw. 47 kanonische Probleme) — bleibt es nach D3 unberuehrt? | **offen** — der `architect` liest es als unberuehrt und hat das in Nachtrag VI so aufgeschrieben; eine **Bestaetigung des `director`** steht nirgends. Faellt sie anders aus, ist der Pruefumfang fuer A3 neu zu bemessen. | Frage: `ARCHITECTURE.md` Z. 3511 (auch Z. 3322). Lesart des `architect`: Z. 3319 |
| OF-23 | `GATE_FIELDS["triggerOnWepType"]` beschriftet 72 Effekte mit „only with a matching weapon type", obwohl kein Waffentyp diesen Wert traegt. | **offen** — der `ui-ux-designer` hat die Zahl in T-086 unabhaengig bestaetigt und ausdruecklich festgehalten, dass AK-177 bis AK-179 diese Oberflaeche **nicht** anfassen. Auf dem heutigen Spielstand latent (0 von 197 bzw. 201 `not_counted`). | Frage: `ARCHITECTURE.md` Z. 3940 (auch Z. 3725). Bestaetigung ohne Entscheidung: `docs/archiv/berichte/T-086-ui-ux-designer.md` Z. 330–344 |
| OF-24 | Der Befund aus T-084 nennt „46 von 170" — Anteil woran, und haengt Prioritaet eines Auftrags daran? | **unklar** — sachlich richtiggestellt (Anteil an der Kandidatenmenge; Statuszeile 4.9b bewegt sich in 175 von 176 Laeufen um null), aber der `director` hat die Folge fuer Prioritaet oder Reihenfolge nirgends beantwortet. `UI_SPEC` fuehrt den Docstring-Widerspruch weiter als offen. | Frage: `ARCHITECTURE.md` Z. 3951. Richtigstellung: ebd. und `docs/archiv/berichte/T-085-architect.md` Z. 152, 329. Weiterhin offen in `UI_SPEC.md` Z. 4845–4850 |
| OF-25 | Haelt A6s 6-s-Schranke fuer `Optimize`, wenn gleichzeitig eine Picker-Frage rechnet (GIL)? | **beantwortet durch den `performance-tuner` (T-140, 08.09.2026)** — keine Verlangsamung ueber der Signifikanzschwelle: Differenz der Mediane 101,3 ms = 1,9 %, `Optimize` bei 5383,9 ms mit 10,3 % Luft. Kein GIL-Engpass gefunden. | Frage: `ARCHITECTURE.md` Z. 4442 (auch Z. 4201, 4853). Antwort: `docs/perf/baselines.md` S11-K, Z. 421–452 |
| OF-26 | Wie gross ist der **Hauptthread-Rest** einer Beraterfrage (Anfragebau, `frozen_inventory`, `inventory_fingerprint`)? | **beantwortet durch den `performance-tuner` (T-140, 08.09.2026)** — 6,2–8,0 ms von 50 ms Budget = 12–16 %, auf beiden Wegen fast gleich; zusammen mit S11-I rund 7,5 ms Gesamtaufenthalt. | Frage: `ARCHITECTURE.md` Z. 4453 (auch Z. 4576). Antwort: `docs/perf/baselines.md` S11-J, Z. 379–418 |
| OF-27 | Muss eine Zahl, die in einem Entwurfstext eine Entscheidung traegt, kuenftig ihre Herkunft mitfuehren (gemessen oder gerechnet, mit Datum und Quelle)? | **offen** — Entscheidung des `director`, ob das als Regel aufgeschrieben wird. In `docs/lessons.md` steht keine solche Regel; L-001 deckt Testschranken und Architekturkennwerte, nicht Entwurfstexte allgemein. | Frage: `ARCHITECTURE.md` Z. 4462 (dritte Fundstelle der Zahl: Z. 4884). Vorgemerkt in `docs/archiv/tasks/T-130.md` Z. 62 |
| OF-28 | Wie gross ist ein Picker-Cache-Eintrag **in der Antwortform, die AD-028 der Picker-Spur gibt**? Solange das fehlt, ist die 64 eine gesetzte Zahl ohne gueltige Herleitung. | **offen** — der `performance-tuner` hat es in T-140 ausdruecklich **nicht** gemessen und selbst als offene Luecke gemeldet. | Frage: `ARCHITECTURE.md` Z. 4937, Schranke und Rueckweg in IX-3.2 (Z. 4714 ff.). Bestaetigt offen: `docs/berichte/T-140-performance-tuner.md` Z. 397–399 |
| OF-29 | Muss ein Feld, das nur unter einer Randbedingung bedeutet, was sein Name sagt, diese Bedingung im **Typ** tragen statt im Docstring daneben? | **offen** — Entscheidung des `director`, ob das als Regel aufgeschrieben wird; ein Umbau der Datenformen ist es nicht. Zweiter Fall derselben Art nach `SlotPool.rank_by` (D-4/T-077). | Frage: `ARCHITECTURE.md` Z. 4944. Vorgemerkt in `docs/archiv/tasks/T-130.md` Z. 62; Fall dazu in `docs/archiv/berichte/T-128-developer.md` Z. 289 |
| OF-30 | AK-218 ist im Wortlaut enger als der gebaute Zustand — der Cache-Treffer endet im Rueckgabewert, nicht in einem der drei Ausgaenge. | **beantwortet durch T-135 (`ui-ux-designer`, 08.09.2026)** — AK-218 in `UI_SPEC.md` nachgezogen (206 Zeilen eingefuegt, 0 geloescht); der Bericht fuehrt OF-30 ausdruecklich als schliessbar. | Frage: `ARCHITECTURE.md` Z. 5356, Meldung Z. 5258. Antwort: `docs/archiv/berichte/T-135-ui-ux-designer.md`, Kopf und Z. 152 |
| OF-31 | A15 verschiebt die Vertrauensgrenze an zwei Stellen (DLL aus dem gewaehlten Ordner; Streichungsgrund von SEC-016/017/018 gilt fuer den neuen Fall nicht; Save-Dialog mit `All files (*)`). | **beantwortet durch den `security-reviewer` (T-144, 08.09.2026), mit Rest beim Nutzer** — Gesamturteil CONCERNS, neue SEC-Befunde ab `security/findings.md` Z. 473. **Offen bleibt daraus:** zwei Wortlautfragen (SEC-027/SEC-028) beim `director` und die Neubewertung von SEC-006/SEC-016/017/018 beim Nutzer. | Frage: `ARCHITECTURE.md` Z. 5931 (auch Z. 5654, Risikozeile Z. 5897). Antwort: `docs/berichte/T-144-security-reviewer.md`; `security/findings.md` Z. 473 ff. |
| OF-32 | Die Gueltigkeitspruefung des gemerkten Pfades laeuft vor dem ersten Fenster; auf einem toten UNC-Ziel kann `stat` zweistellige Sekunden kosten. Frist bauen, bevor jemand sie gemessen hat? | **offen** — an den `performance-tuner`, nach V1. Empfehlung des `architect`: erst messen. Auf diesem Rechner ohne Freigabe nicht messbar. | `ARCHITECTURE.md` Z. 5952; `docs/berichte/T-143-architect.md` Z. 209 |
| OF-33 | **Nicht vergeben.** Nur als naechster freier Kreis genannt („OF ab OF-33"); `docs/state.md` fuehrt inzwischen „OF ab OF-34". | entfaellt | `ARCHITECTURE.md` Z. 5970; `docs/state.md` Z. 10–12 |

### Zaehlung der offenen Fragen

Die Tabelle hat **32** Zeilen — eine je OF-Nummer, die in `ARCHITECTURE.md`
vorkommt. Jede Zeile zaehlt in genau eine Klasse.

| Stand | Anzahl | IDs |
|---|---|---|
| **beantwortet**, Fundstelle belegt | **17** | OF-1, OF-2, OF-4, OF-5, OF-6, OF-7, OF-8, OF-9, OF-12, OF-13, OF-15, OF-17, OF-19, OF-20, OF-25, OF-26, OF-30 |
| **beantwortet mit benanntem Rest** | **1** | OF-31 (Rest: SEC-027/SEC-028 beim `director`, Neubewertung SEC-006/016/017/018 beim Nutzer) |
| **offen** | **12** | OF-3, OF-10, OF-11, OF-16, OF-18, OF-21, OF-22, OF-23, OF-27, OF-28, OF-29, OF-32 |
| **unklar** | **1** | OF-24 (sachlich richtiggestellt, die Folge fuer Prioritaet nie beantwortet) |
| **nie vergeben** | **1** | OF-33 (nur als naechster freier Kreis genannt) |
| **Summe** | **32** | |

**OF-14 taucht in der Tabelle nicht auf, weil es die Nummer nicht gibt.**
Volltextsuche ueber alle `*.md` des Arbeitsbaums mit zwei Schreibweisen
(`OF-14` und `\bOF-[0-9]+` mit anschliessender Sortierung): **0 Treffer**.
Der OF-Kreis springt von OF-13 auf OF-15 — eine Luecke wie AD-027, kein
verlorener Vorgang. Genau darum sind es 32 OF-Nummern und nicht 33.

### Wer auf welche Antwort wartet

| Adressat | wartende OF |
|---|---|
| **App Designer / Nutzer** | OF-3 (Gewichtung), OF-16 (Spielmessung QA-018), aus OF-31 die Neubewertung von SEC-006/016/017/018 |
| **`director`** | OF-22, OF-24, OF-27, OF-29; aus OF-31 die Wortlautfragen SEC-027/028 |
| **`performance-tuner`** | OF-10, OF-28, OF-32 |
| **`qa-engineer`** | OF-11 |
| **`ui-ux-designer`** | OF-18, OF-21, OF-23 |

---

## Was dieses Register nicht leistet

- Es **entscheidet nichts**. Wo der Bestand keine Antwort belegt, steht
  `offen` — auch dort, wo eine Antwort naheliegt.
- Es **ersetzt den Verlauf nicht**. Die Begruendungen, die verworfenen
  Alternativen und die Zwischenstaende stehen vollstaendig in
  `docs/archiv/architecture-verlauf.md`.
- Es **fuehrt keinen zweiten Nummernkreis**. `UI_SPEC.md` hat einen eigenen
  OF-Kreis; `AK-`, `QA-`, `SEC-`, `DR-` stehen in ihren eigenen Dateien.
