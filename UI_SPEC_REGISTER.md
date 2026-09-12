# UI_SPEC_REGISTER — welche Fassung jedes Akzeptanzkriteriums heute gilt

**Erstellt:** 2026-09-12 · **Rolle:** `ui-ux-designer` · **Auftrag:** T-181
**Gemessener Stand:** `UI_SPEC.md` auf Commit `e06386c` — 9639 Zeilen,
50 physische `## `-Zeilen, **33 logische Abschnitte**, 255 Akzeptanzkriterien.

## Wozu diese Datei

`UI_SPEC.md` ist chronologisch gewachsen: ein Abschnitt je Auftrag, spaetere
Korrekturen als Nachtrag am Ende. Wer wissen will, was fuer ein Kriterium
**heute** gilt, musste bisher die ganze Datei lesen und die Reihenfolge selbst
rekonstruieren. Dieses Register nimmt ihm das ab. Es **entscheidet nichts** —
es zeigt nur, wo die geltende Fassung steht und welche Fassung sie abgeloest
hat.

## Wie die Spalten zu lesen sind

| Spalte | Bedeutung |
|---|---|
| **AK-ID** | die Nummer, wie sie in `UI_SPEC.md`, `qa/findings.md` und den Berichten zitiert wird |
| **worum es geht** | maschinell aus dem Kriteriumstext gezogener Kurztext — **keine** Vorgabe, nur ein Wegweiser |
| **geltende Fundstelle** | wo der heute bindende Text steht. Mehrere Orte mit `+`, wenn Grundfassung und Aenderung getrennt stehen |
| **zuletzt geaendert durch** | T-Nummer und Datum des Abschnitts, der zuletzt an diesem Kriterium gearbeitet hat |
| **ueberholt durch** | welche Fassung von welchem Nachtrag abgeloest wurde. **Leer heisst: die Erstfassung gilt unveraendert** |

**Zeilennummern** (`Z1234`) beziehen sich auf `UI_SPEC.md` im Stand `e06386c`,
also auf den Text, der unveraendert nach `docs/archiv/ui-spec-verlauf.md`
gewandert ist. Der Versatz zwischen beiden Dateien steht im Kopf der
Verlaufsdatei.

**Abschnittskennungen** `A01` bis `A33` sind in diesem Register vergeben und
in der Tabelle unten aufgeloest. Sie sind **nicht** die `§`-Nummern aus dem
Fliesstext von `UI_SPEC.md` — die bezeichnen Unterabschnitte innerhalb eines
Auftragsabschnitts.

## Befund zur Zaehlung: 255 Kriterien, nicht 256

Der Auftrag nennt 256 AK-IDs, gemessen mit
`grep -oE 'AK-[0-9]+' UI_SPEC.md | sort -u | wc -l`. Nachgezaehlt sind es
**255**. Die 256. Zeichenkette ist `AK-2` in Zeile 9461 — sie steht dort als
Teil eines Suchmusters (`grep -rn "AK-2[45][0-9]"`) und ist kein
Akzeptanzkriterium. Die Nummern laufen von AK-01 bis AK-255 **ohne Luecke**.

**Nachtrag 12.09.2026 (T-192):** acht Kriterien sind dazugekommen, **AK-256
bis AK-263**. Sie stehen in `UI_SPEC.md` §5.4 und **nicht** im Verlauf — sie
sind dort entstanden. Ihre Fundstelle-Spalte nennt deshalb `UI_SPEC §5.4`
statt einer `A..`-Kennung. Der Bestand ist damit **263**.

## Die 33 Abschnitte von UI_SPEC.md

| Kennung | Zeilen | Auftrag | Datum | Ueberschrift |
|---|---|---|---|---|

| **A01** | 14-471 | T-004 | 2026-09-01 | Build Advisor (T-004) — 2026-09-01 |
| **A02** | 472-1180 | T-024 | 2026-09-02 | Die Sprache der Zahlen, und der Relic Picker (T-024) — 2026-09-02 |
| **A03** | 1181-1220 | T-035 | 2026-09-03 | Nachtrag zu AK-34: Fassung B fuer den heutigen Einzelsatz (T-035) — 2026-09-03 |
| **A04** | 1221-1268 | T-037 | 2026-09-03 | Nachtrag zu AK-47: das Wort `unverified` entfaellt (Director, T-037) — 2026-09-03 |
| **A05** | 1269-1383 | T-052 | 2026-09-05 | Nachtrag zu QA-116: keiner der beiden Wortlaute — der Vorbehalt wird datengetrieben (ui-ux-designer, T-052) — 2026-09-05 |
| **A06** | 1384-1437 | T-052 | 2026-09-05 | Nachtrag zu AK-34/QA-121: der Uebergangssatz braucht eine dritte Zeile, seit Katalysatoren im selben Raster stehen (ui-ux-designer, T-052) — 2026-09-05 |
| **A07** | 1438-1497 | T-052 | 2026-09-05 | Nachtrag zu QA-117: Anzeigeschwellen bleiben absolut, wandern nicht mit dem Kalibrierungsfaktor (ui-ux-designer, T-052) — 2026-09-05 |
| **A08** | 1498-1548 | T-052 | 2026-09-05 | Nachtrag zu QA-119: die Fremdzeile wird gefiltert, nicht durch eine Id unterscheidbar gemacht (ui-ux-designer, T-052) — 2026-09-05 |
| **A09** | 1549-1675 | T-052 | 2026-09-05 | Nachtrag zu OF-20, QA-108 und QA-113: die drei Saetze in `SlotPool.unknowns` (ui-ux-designer, T-052-Nachtrag) — 2026-09-05 |
| **A10** | 1676-2446 | T-056 | 2026-09-05 | Die sechs Inhalts-Tabs: welche Frage jeder beantwortet, und woran ein Spieler das abliest (ui-ux-designer, T-056) — 2026-09-05 |
| **A11** | 2447-2480 | Director | 2026-09-05 | Nachtrag des Directors zu AK-81, AK-82 und AK-88 — 2026-09-05 |
| **A12** | 2481-2517 | T-058 | 2026-09-05 | Nachtrag des Directors zu AK-75, AK-77 und AK-97 — 2026-09-05 (nach T-058) |
| **A13** | 2518-2554 | T-068 | 2026-09-06 | Nachtrag des Directors zu AK-82 — 2026-09-06 (nach T-068) |
| **A14** | 2555-2578 | T-071 | 2026-09-06 | Nachtrag des Directors zu AK-05 — 2026-09-06 (nach T-071) |
| **A15** | 2579-3279 | T-074 | 2026-09-06 | Der Erststart mit Ordnerauswahl (ui-ux-designer, T-074) — 2026-09-06 |
| **A16** | 3280-3864 | T-078 | 2026-09-06 | Die Sprache des Beraters: eine Zeile je Zahl, und die Fluche, auf die keine Zahl passt (ui-ux-designer, T-078) — 2026-09-06 |
| **A17** | 3865-4385 | T-078 | 2026-09-06 | Nachtrag zu T-078: der stumme Effekt bekommt seinen Namen, und der schlechteste Fall einer Slotkarte ist gemessen statt geschaetzt (ui-ux-designer, T-080) — 2026-09-06 |
| **A18** | 4386-4426 | T-078 | 2026-09-06 | Director-Korrektur zu T-078/T-080 — 06.09.2026, entschieden vom App Designer |
| **A19** | 4427-4859 | T-084 | 2026-09-07 | Nachtrag zu AK-63, 4.7, `budget_note` und der Grenze (c)/(d): vier Wortlaute und eine Zaehlgrenze vor S10b/S10c (ui-ux-designer, T-084) — 2026-09-07 |
| **A20** | 4860-5234 | T-086 | 2026-09-07 | (ui-ux-designer, T-086) — 2026-09-07 |
| **A21** | 5235-5913 | T-092 | 2026-09-07 | Schlechtester und bester Fall, und die Zahl ohne Waffe (ui-ux-designer, T-092) — 2026-09-07 |
| **A22** | 5914-5980 | Director | 2026-09-07 | Director-Korrektur zum Relic Picker — 2026-09-07, entschieden vom App Designer |
| **A23** | 5981-6530 | T-124 | 2026-09-08 | Der Picker oeffnet vor seinen Zahlen (ui-ux-designer, T-124) — 2026-09-08 |
| **A24** | 6531-7093 | T-127 | 2026-09-08 | Leeres Raster bis zur Antwort (ui-ux-designer, T-127) — 2026-09-08 |
| **A25** | 7094-7277 | T-135 | 2026-09-08 | AK-218 nachgezogen: die Antwort, die schon bekannt war (ui-ux-designer, T-135) — 2026-09-08 |
| **A26** | 7278-7885 | T-141 | 2026-09-08 | Der Spielstand wird im Hintergrund gelesen — der dritte Fensterzustand, der Rueckfallsatz und das Praefix davor (ui-ux-designer, T-141) — 2026-09-08 |
| **A27** | 7886-7904 | T-141 | 2026-09-08 | Nachtrag: F-R ist entschieden (ui-ux-designer, T-141) — 2026-09-08 |
| **A28** | 7905-8249 | T-145 | 2026-09-08 | Was aus dem gewaehlten Ordner wirklich passiert, und die Rueckfrage im Fall C2 (ui-ux-designer, T-145) — 2026-09-08 |
| **A29** | 8250-8481 | T-146 | 2026-09-08 | AK-232 nachgezogen: gefragt wird nur, wenn der Ordner den gewaehlten Baum verlaesst (ui-ux-designer, T-146) — 2026-09-08 |
| **A30** | 8482-8717 | T-148 | 2026-09-09 | drei Praezisierungen an AK-220 bis AK-229 (ui-ux-designer, T-148) — 2026-09-09 |
| **A31** | 8718-8881 | T-154 | 2026-09-09 | AK-244 nachgezogen: die Regel statt der Liste, und der Widerspruch bei S5 (ui-ux-designer, T-154) — 2026-09-09 |
| **A32** | 8882-9063 | T-163 | 2026-09-09 | SEC-032 nachgezogen: Ab zwei Ebenen Abstand wird gefragt (ui-ux-designer, T-163) — 2026-09-09 |
| **A33** | 9064-9640 | T-178 | 2026-09-09 | Die Gesamtzahl der Relikte, und der Erststart ohne Zeitversprechen (ui-ux-designer, T-178) — 2026-09-09 |

## Register

| AK-ID | worum es geht | geltende Fundstelle | zuletzt geaendert durch | ueberholt durch |
|---|---|---|---|---|
| AK-01 | Es gibt keinen neuen Tab. Die Tab-Leiste zeigt dieselben Tabs wie in 3da8428. | A01 Z335 | T-004, 2026-09-01 | — |
| AK-02 | Die Advisor bar steht in der mittleren Spalte des Build planner zwischen der "Build"-Zeile und dem Hinweistext und scrollt nicht mit. | A01 Z337 | T-004, 2026-09-01 | — |
| AK-03 | Planner.minimumSizeHint().width() ist nicht groesser als auf 3da8428 (gleiche Umgebung, gleiche UI scale, gemessen vor dem ersten show()). | A01 Z339 | T-004, 2026-09-01 | — |
| AK-04 | Die Mindesthoehe des Fensters waechst um hoechstens 44 px gegenueber 3da8428. | A01 Z342 | T-004, 2026-09-01 | — |
| AK-05 | Bei Fensterbreite 1320 px (Startbreite) ist in der Advisor bar kein Text abgeschnitten ausser der Statuszeile, und deren voller Text steht im Tooltip. | A01 Z344 + A14 Z2555 (Startbreite abgeleitet statt 1320 px) | T-071, 2026-09-06 | **widerspruechlich** - die Pixelzahl 1320 px ist in A14 Z2555 (T-071) aufgehoben, wird aber in AK-160 (A17 Z4336) und AK-194 (A21 Z5782) danach erneut als `Startbreite` vorgeschrieben; siehe Abschnitt `Widerspruechliche Faelle` |
| AK-06 | Mit UI scale 150 % und sechs belegten Deep-of-Night-Slots samt lebendem Vorschlag entsteht in der mittleren Spalte keine horizontale Bildlaufleiste. | A01 Z347 | T-004, 2026-09-01 | — |
| AK-07 | Zu keinem Zeitpunkt sind mehr als drei Aktionsknoepfe der Advisor bar gleichzeitig sichtbar. | A01 Z350 | T-004, 2026-09-01 | — |
| AK-08 | Waehrend einer laufenden Rechnung lassen sich Nightfarer wechseln, Vessel wechseln, ein Slot oeffnen und der Tab wechseln; | A01 Z355 | T-004, 2026-09-01 | — |
| AK-09 | Eine Rechnung unter 250 ms zeigt weder Fortschrittsbalken noch Wartetext (kein Aufblitzen). | A01 Z359 (Advisor bar); fuer den Picker A24 Z6989/Z6994 | T-127, 2026-09-08 | fuer den Picker durch AK-215/AK-216 - A24 Z6989/Z6994 (T-127); fuer die Advisor bar unveraendert |
| AK-10 | Eine Rechnung ueber 250 ms zeigt Fortschrittsbalken und Wartetext, und Optimize traegt Cancel. | A01 Z361 (Advisor bar); fuer den Picker A24 Z6994 | T-127, 2026-09-08 | fuer den Picker durch AK-216 - A24 Z6994 (T-127); fuer die Advisor bar unveraendert |
| AK-11 | Cancel fuehrt binnen 200 ms nach dem Klick sichtbar in Zustand 4.5, auch wenn der Arbeiter laenger zum Beenden braucht. | A01 Z363 | T-004, 2026-09-01 | — |
| AK-12 | Aendert sich Nightfarer, Vessel, Deep of Night, Level oder eine Slot-Belegung waehrend der Rechnung, wird das Ergebnis verworfen und 4.7 angezeigt. | A01 Z365 | T-004, 2026-09-01 | — |
| AK-13 | Optimize veraendert keinen Slot: nach Optimize ohne Anwenden sind Slot-Belegung, Statblatt und der Eintrag der Build-Liste unveraendert. | A01 Z369 | T-024, 2026-09-02 (praezisiert durch AK-57) | — |
| AK-14 | Nach Apply all zeigt das Statblatt die angewendeten Relikte, und der Zustand ist derselbe, als waeren die Relikte einzeln im Picker gewaehlt worden … | A01 Z371 | T-024, 2026-09-02 (praezisiert durch AK-57) | — |
| AK-15 | Undo apply stellt die vorherige Belegung exakt wieder her, auch einen vorher leeren Slot und ein vorher dort liegendes Custom relic. | A01 Z374 | T-004, 2026-09-01 | — |
| AK-16 | Kein Vorschlag enthaelt jemals ein Custom relic oder ein Relikt, das nicht in owned steht. | A01 Z376 | T-024, 2026-09-02 (praezisiert durch AK-58) | — |
| AK-17 | Der Berater schreibt nicht in den Save und oeffnet keine Netzwerkverbindung. | A01 Z378 | T-004, 2026-09-01 | — |
| AK-18 | Jeder Slot-Vorschlag traegt genau einen Begruendungssatz in Nutzersprache, der mindestens einen konkreten Effekt beim Namen nennt (GOAL A5). | A16 Z3718 (AK-134) | T-078, 2026-09-06 | vollstaendig durch AK-134 - A16 Z3718 (T-078); der Satz `genau ein Begruendungssatz je Slot` ist aufgehoben |
| AK-19 | Traegt das vorgeschlagene Relikt Fluche, sind sie im Vorschlagsblock genannt — in CURSE und mit ✦ — bevor angewendet wird. | A01 Z386 | T-004, 2026-09-01 | — |
| AK-20 | Kann das Ziel gar nicht bewertet werden, erscheint 4.10 und kein Vorschlag. | A01 Z388 | T-004, 2026-09-01 | — |
| AK-21 | Blieben Kandidateneffekte unbewertet, weil die Spieldateien keine Zahlen tragen, sagt die Statuszeile das (4.9) und der Why-Dialog nennt die … | A16 Z3762 (AK-142) | T-078, 2026-09-06 | vollstaendig durch AK-142 - A16 Z3762 (T-078) |
| AK-22 | Beruht das Ziel auf Attack Rating, steht der Vorbehalt aus den "Known limits" genau einmal im Why-Dialog — nicht je Zeile. | A01 Z394 + A02 Z538 (Geltungsbereich eingeschraenkt) | T-024, 2026-09-02 | der Geltungsbereich `genau einmal im Why-Dialog` gilt nur noch fuer den Optimize-Lauf - A02 Z538 (T-024) |
| AK-23 | Alle vom Berater gezeigten Zeichenketten sind Englisch (GOAL A8). | A01 Z396 | T-004, 2026-09-01 | — |
| AK-24 | Der Berater respektiert Slot-Farben, Stacking-Regeln und die Deep-of-Night-Kennzeichnung: | A01 Z397 | T-004, 2026-09-01 | — |
| AK-25 | Jede Aktion des Beraters (Zielwahl, Optimize, Cancel, Apply all, Use je Slot, Why, Clear, Undo apply) ist allein mit Tab / Umschalt+Tab und Enter / … | A01 Z403 | T-004, 2026-09-01 | — |
| AK-26 | Die Tab-Reihenfolge entspricht 5.7; der Fokusring ist auf jedem neuen Bedienelement sichtbar. | A01 Z406 | T-004, 2026-09-01 | — |
| AK-27 | Der Filter im Relic Picker liefert mit lebendem Vorschlag dieselben Treffermengen wie ohne; | A01 Z408 | T-004, 2026-09-01 | — |
| AK-28 | Die Advisor-Karte im Picker traegt den Text ADVISOR PICK; | zurueckgezogen; Ersatz ist die Kennzeichnung in A01 Paragraf 3.5 | T-024, 2026-09-02 | zurueckgezogen - A02 Z532 (T-024) |
| AK-29 | Jedes vom Berater neu eingefuehrte Label, jeder Tooltip und jeder Textbereich setzt setTextFormat() ausdruecklich. | A01 Z417 | T-004, 2026-09-01 | — |
| AK-30 | Ein Relikt, dessen Name die Zeichenkette <b>x</b><img src=x>&lt; | A01 Z421 | T-004, 2026-09-01 | — |
| AK-31 | Im gesamten nrplanner/-Baum wird eine Angriffswertzahl nur mit einer dieser drei Formen beschriftet: | A02 Z989 | T-024, 2026-09-02 | — |
| AK-32 | Jede Angriffswertzahl auf dem Bildschirm laesst sich einer der drei Fragen aus damage.Basis zuordnen, ohne zu hovern und ohne aufzuklappen — … | A02 Z996 | T-024, 2026-09-02 | — |
| AK-33 | Die Kopfzeile der Zahlenliste jeder Arsenal-Kachel lautet AR at +<n> mit dem Wert der Spinbox Upgrade to +; | A02 Z1000 | T-024, 2026-09-02 | — |
| AK-34 | Die Arsenal-Zusammenfassung besteht aus zwei getrennten Labels mit dem Wortlaut aus §2.3(e). | A02 Z1003 + A03 Z1181 (Fassung B) + A06 Z1384 (dritte Zeile) | T-052, 2026-09-05 | der Uebergangs-Wortlaut ist zweimal nachgezogen - A03 Z1181 (T-035), A06 Z1384 (T-052) |
| AK-35 | Zwischen dem Waffenkachelraster und der Schadenstafel steht eine stets sichtbare Bildunterschrift mit dem Wortlaut aus §2.3(c). | A02 Z1009 | T-024, 2026-09-02 | — |
| AK-36 | Die Gesamtzeile der Schadenstafel zeigt beide Namen ohne Hovern (AR without relics <n> → AR as equipped <n>); | A02 Z1013 | T-024, 2026-09-02 | — |
| AK-37 | Keine Zeichenkette der Oberflaeche behauptet, welche Zahl richtig ist, in welchem Verhaeltnis sie zum Spiel steht, oder dass eine Rangfolge davon … | A02 Z1017 + A05 Z1360 | T-052, 2026-09-05 | beide festen Vorbehalts-Wortlaute des Pickers entfallen ersatzlos - A05 Z1360 (T-052); die Aussage gilt jetzt ueber Goal.scope/SlotPool.unknowns. Der in AK-37 selbst zitierte Picker-Satz ist damit gegenstandslos, der Arsenal-Satz bleibt |
| AK-38 | Aufbau: Slot auf Tier 3, Arsenal-Spinbox auf +1, kein Relikt ausgeruestet. Die beiden Zahlen duerfen verschieden sein; die Arsenal-Kachel nennt in … | A02 Z1024 | T-024, 2026-09-02 | — |
| AK-39 | Aufbau: ein Relikt mit Strength +1, sonst nichts. Waffenkachel und Schadenstafel zeigen fuer dieselbe Waffe dieselbe Zahl (nach W3, AD-020 Punkt … | A02 Z1029 | T-024, 2026-09-02 | — |
| AK-40 | Die Beschriftungen aus AK-31, AK-33, AK-35 und AK-36 werden nicht vor den zugehoerigen Umbauschritten ausgeliefert: | A02 Z1033 | T-024, 2026-09-02 | — |
| AK-41 | Jede Reliktkarte traegt einen Wertblock als erste Zeile des Kartenkoerpers, unter der Kopfzeile und ueber den Effektpunkten, getrennt durch eine … | A02 Z1041 | T-024, 2026-09-02 | — |
| AK-42 | Der Wertblock zeigt beide Zielrichtungen (Damage, Damage taken) auf jeder Karte, in jeder Sortierung. | A02 Z1045 + UI_SPEC §5.4 (AK-258) | T-192, 2026-09-12 | erweitert auf **eine Zeile je Zielrichtung** durch AK-258 (T-192); die Aussage „alle, in jeder Sortierung“ gilt unveraendert |
| AK-43 | Der Picker traegt ein Sort by mit genau den Eintraegen Maximise damage, Minimise damage taken, Name. | UI_SPEC §5.4 (AK-256) | T-192, 2026-09-12 | **vollstaendig ersetzt durch AK-256** (T-192) — die woertliche Aufzaehlung wird mit der dritten Zielrichtung falsch; die Zusage „eine Zielwahl im ganzen Programm“ steht als AK-256 Punkt 3 weiter |
| AK-44 | Weder auf einer Karte noch in der Kopfzeile erscheint eine Ordnungszahl, ein Rangabzeichen oder eine Formulierung, die eine strenge Reihenfolge … | A02 Z1052 | T-024, 2026-09-02 | — |
| AK-45 | Zwei Karten zeigen genau dann denselben Wert in der sortierten Zielrichtung, wenn sie dieselbe Gleichstandskennzeichnung tragen. | A02 Z1056 | T-024, 2026-09-02 | — |
| AK-46 | Jede Karte mit dem Maximalwert der sortierten Zielrichtung traegt den Textchip BEST FOR DAMAGE bzw. | A02 Z1059 + UI_SPEC §5.4 (AK-262) | T-192, 2026-09-12 | erweitert durch AK-262 (T-192): auch die vorgezogenen Spitzenkarten der nicht gelesenen Richtungen tragen ihren Chip; dritte Richtung `BEST FOR STATS` |
| AK-47 | Solange QA-018 offen ist, steht hinter dem Angriffswert jeder Karte das Wort unverified — sichtbar, nicht in einem Tooltip, nicht aufklappbar. | A02 Z1064 (zweite Haelfte) + A04 Z1221 + A05 Z1269 | T-052, 2026-09-05 | erste Haelfte gegenstandslos (QA-018 geschlossen) - A04 Z1221 (T-037); der in A04 Punkt 2 fest gebundene Satz ist durch A05 Z1269 (T-052) aufgehoben - Zeile 4 zeigt ausschliesslich Goal.scope |
| AK-48 | Bewegt der Fluch eines Relikts ein Feld, das keine der beiden Zahlen misst, steht unter dem Wertblock genau eine Zeile Its curse changes <field> … | A02 Z1067 | T-024, 2026-09-02 | — |
| AK-49 | Traegt die gewaehlte Zielrichtung keine Zahlen, steht die Zeile aus §3.7 in der Kopfzeile, jede Karte zeigt — statt einer Zahl, und die Ordnung ist … | A02 Z1072 | T-024, 2026-09-02 | — |
| AK-50 | Die beiden Textzeilen aus §3.2 (Bezugsgroesse; | A02 Z1076 + A05 Z1360 (gilt fuer drei Zeilen) | T-052, 2026-09-05 | der Umfang `zwei Zeilen` - A05 Z1360 (T-052), jetzt Zeile 3, 3b und 4 |
| AK-51 | Am Standardmass des Pickers erscheint keine waagerechte Bildlaufleiste (heute gemessen: | A02 Z1079 (erste Haelfte); zweite Haelfte A22 Z5967 (AK-196) | T-124-Vorlauf/Director-Korrektur, 2026-09-07 | zweite Haelfte durch AK-196 - A22 Z5967 (Director-Korrektur 2026-09-07) |
| AK-52 | Sort by liegt in der Tab-Reihenfolge zwischen dem Filterfeld und der ersten Karte; | A02 Z1084 | T-024, 2026-09-02 | — |
| AK-53 | Jedes im Picker neu eingefuehrte Label und jeder neue Tooltip setzt setTextFormat() ausdruecklich; | A02 Z1088 | T-024, 2026-09-02 | — |
| AK-54 | Jede RelicSlot-Karte traegt in ihrer Kopfzeile einen checkbaren Knopf mit dem Text Hold bzw. | A02 Z1097 | T-024, 2026-09-02 | — |
| AK-55 | Ein leerer Slot kann gehalten werden; er zeigt dann Held empty — Optimize will not fill this slot. und wird von Apply all nicht belegt. | A02 Z1100 | T-024, 2026-09-02 | — |
| AK-56 | Faellt ein Halt weg, weil das Relikt nicht mehr im Besitz ist, steht der Satz aus §4.3 am Slot und eine entsprechende Zeile in den unknowns des … | A02 Z1103 | T-024, 2026-09-02 | — |
| AK-57 | Nach Apply all ist der Inhalt jedes gehaltenen Slots bitgleich dem Inhalt davor — Relikt, Rolls, Fluche, und auch der Fall „gehalten und leer". | A02 Z1106 | T-024, 2026-09-02 | — |
| AK-58 | Ein gehaltener Slot darf ein Custom relic enthalten und behaelt es. | A02 Z1110 | T-024, 2026-09-02 | — |
| AK-59 | Keine Zeichenkette der Oberflaeche legt nahe, dass ein Halt einen Programmneustart ueberlebt. | A02 Z1113 | T-024, 2026-09-02 | — |
| AK-60 | Gefaess oder Nightfarer wechseln und zurueckwechseln stellt den Haltezustand wieder her; | A02 Z1115 | T-024, 2026-09-02 | — |
| AK-61 | Der Knopf heisst Optimize und steht in der Advisor bar der mittleren Spalte des Build planner. | A02 Z1121 | T-024, 2026-09-02 | — |
| AK-62 | Der Satz aus §5.3 steht sichtbar im Picker, in jeder Sortierung und in jedem Zustand, in dem Kartenwerte gezeigt werden. | A02 Z1124 | T-024, 2026-09-02 | — |
| AK-63 | Zeile 4 des Pickers (§3.2) und Punkt 4 des Why-Dialogs (§3.4) zeigen ausschliesslich die Saetze aus Goal.scope der aktuell gewaehlten Zielrichtung … | A19 Z4554 (AK-162) und Z4563 (AK-163) | T-084, 2026-09-07 | T-052-Fassung (A05 Z1346) vollstaendig durch AK-162 (erste Haelfte) und AK-163 (zweite Haelfte) - A19 Z4554/Z4563 (T-084) |
| AK-64 | Der Zusammenfassungssatz des Arsenal-Tabs (arsenaltab.py:306-311, Fassung B des Uebergangs-Nachtrags zu AK-34) enthaelt zusaetzlich den Satz … | A06 Z1415 | T-052, 2026-09-05 | — |
| AK-65 | Die Anzeigeschwellen >= 0.5 (Sichtbarkeit der Zeile From attributes und der Aenderungszelle) und > 0.05 (Farbe GOOD/MUTED der Aenderungszelle) in … | A07 Z1482 | T-052, 2026-09-05 | — |
| AK-66 | Eine Waffenzeile, die zur Katalysator-Familie gehoert (Glintstone Staff / Sacred Seal, model.weapon_class(weapon) == "catalyst") und gleichzeitig … | A08 Z1522 | T-052, 2026-09-05 | — |
| AK-67 | SlotPool.unknowns traegt fuer den heutigen Bestand bis zu drei Saetze, in dieser Reihenfolge, falls mehrere zutreffen — Handle-Zeile, dann … | A09 Z1651 | T-052, 2026-09-05 | — |
| AK-68 | Jeder der sechs Tabs zeigt beim Erstoeffnen, oberhalb jedes Bedienelements und jeder Zahl, eine _heading()-Ueberschrift und unmittelbar darunter … | A10 Z1735 | T-056, 2026-09-05 | — |
| AK-69 | Auf keinem der sechs Tabs steht eine Zahl, deren Einheit und deren Bezugsgroesse nicht entweder in ihrer eigenen Zeile oder in genau einem … | A10 Z1745 | T-056, 2026-09-05 | — |
| AK-70 | Wo die Bezugsgroesse auch im Code nicht bekannt ist, sagt der Bildschirm das, statt die Zahl kommentarlos zu zeigen oder sie wegzulassen (GOAL A7 … | A10 Z1752 | T-056, 2026-09-05 | — |
| AK-71 | Kein Tab setzt eine Mindesthoehe ueber 860 logische px (minimumSizeHint().height()), gemessen an einer echten Widget-Instanz. | A10 Z1799 | T-056, 2026-09-05 | — |
| AK-72 | Kein Kachel- oder Kartenraster hat eine feste Spaltenzahl. | A10 Z1806 | T-056, 2026-09-05 | — |
| AK-73 | Keine angezeigte Zeichenkette bricht mitten in einem Begriff um. | A10 Z1814 | T-056, 2026-09-05 | — |
| AK-74 | Jede Farbe, die auf einem der sechs Tabs eine Bedeutung traegt (und nicht nur Typografie ist), wird auf demselben Tab genau einmal benannt — in … | A10 Z1837 | T-056, 2026-09-05 | — |
| AK-75 | In keiner angezeigten Zeichenkette der sechs Tabs steht -- . | A10 Z1852 + A12 Z2497 (Geltungsbereich) | T-058, 2026-09-05 | Geltungsbereich auf die sechs Inhalts-Tabs begrenzt - A12 Z2497 (Director nach T-058) |
| AK-76 | Der Tab oeffnet mit diesen beiden Zeilen, wortgleich, oberhalb der Filterzeile. | A10 Z1868 | T-056, 2026-09-05 | — |
| AK-77 | Im Effects-Tab ist Effect die breiteste Spalte der Tabelle, bei jeder Fensterbreite. | A10 Z1900 + A12 Z2487 (Untergrenze) | T-058, 2026-09-05 | gilt nicht unterhalb von rund 1100 logischen px - A12 Z2487 (Director nach T-058) |
| AK-78 | In der Effektetabelle steht keine Spalte mehr mit der Ueberschrift Pools. | A10 Z1925 | T-056, 2026-09-05 | — |
| AK-79 | Die heutige ungewichtete Mittelung ueber Farb-/Modus-Eimer wird nicht ausgeliefert. | A10 Z1963 | T-056, 2026-09-05 | — |
| AK-80 | Der angezeigte Mittelwert ist nach Vorkommen gewichtet, nicht ueber Eimer gemittelt. | A10 Z1977 | T-056, 2026-09-05 | — |
| AK-81 | Tier und Copies werden aus dem ungefilterten Effektbestand gebildet; | A10 Z1989 + A11 Z2452 (Beispielzahlen) | Director, 2026-09-05 | die Beispielzahlen `1 of 2`/`2 of 2` - A11 Z2452 (Director); verbindlich sind `1 of 3`/`3 of 3` |
| AK-82 | Der Tab oeffnet mit diesen beiden Zeilen, wortgleich. | A13 Z2518 (Wortlaut) | T-068, 2026-09-06 | Wortlaut zweimal ersetzt - A11 Z2457 (Director, AK-68 gewinnt) und A13 Z2518 (Director nach T-068) |
| AK-83 | Beim ersten Oeffnen des Tabs ist mindestens ein Abschnitt aufgeklappt und mindestens eine Waffenkachel sichtbar, ohne dass der Nutzer etwas … | A10 Z2024 | T-056, 2026-09-05 | — |
| AK-84 | setzt AK-72 und AK-73 fuer diesen Tab um | A10 Z2031 | T-056, 2026-09-05 | — |
| AK-85 | Die Skalierungszeile nennt ihre Skala. Der Tab traegt dazu genau einen Satz, im Zusammenfassungsblock, wortgleich: Scaling is the game's own … | A10 Z2036 | T-056, 2026-09-05 | — |
| AK-86 | Die Aufbau-Zeilen (Blood Loss buildup, Poison buildup, Frost buildup, …) tragen ihren Geltungsbereich. | A10 Z2044 | T-056, 2026-09-05 | — |
| AK-87 | Die Zauberkachel benennt ihre Kosten als Kosten: | A10 Z2054 | T-056, 2026-09-05 | — |
| AK-88 | Dieselbe Groesse heisst auf demselben Bildschirm einmal. | A10 Z2058 + A11 Z2465 (Geltungsbereich) | Director, 2026-09-05 | Geltungsbereich auf angezeigten Text begrenzt - A11 Z2465 (Director) |
| AK-89 | Der Tab oeffnet mit diesen beiden Zeilen, wortgleich. | A10 Z2080 | T-056, 2026-09-05 | — |
| AK-90 | setzt AK-72 fuer diesen Tab um, eigener Befund | A10 Z2087 | T-056, 2026-09-05 | — |
| AK-91 | Das Detailpanel traegt drei Erklaerzeilen, je einmal je Abschnitt, wortgleich: | A10 Z2096 | T-056, 2026-09-05 | — |
| AK-92 | Kein Sentinel wird als Zahl gedruckt. Refills at x-1 kommt nicht vor: bei stance.recovery <= 0 entfaellt die Zeile, oder sie lautet Refills at — … | A10 Z2107 | T-056, 2026-09-05 | — |
| AK-93 | Der Abschnitt WEAKNESS SPECIAL INTERACTION erscheint, sobald der Nightlord irgendeine Schwaeche traegt — Schadensart oder Status. | A10 Z2112 | T-056, 2026-09-05 | — |
| AK-94 | Zeilen, die auf einer Sichtung beruhen und nicht in den Spieldateien stehen, tragen OBSERVED_COLOUR (#7fae72) — dieselbe Farbe, die der Tab fuer … | A10 Z2118 | T-056, 2026-09-05 | — |
| AK-95 | Der Tab oeffnet mit diesen beiden Zeilen, wortgleich; | A10 Z2142 | T-056, 2026-09-05 | — |
| AK-96 | Die beiden Zeilen des obersten Blocks nennen ihren Bezug bzw. | A10 Z2149 | T-056, 2026-09-05 | — |
| AK-97 | eigener Befund, setzt AK-71 fuer diesen Tab um | A10 Z2165 + A12 Z2493 | T-058, 2026-09-05 | — |
| AK-98 | Der Tab oeffnet mit diesen beiden Zeilen, wortgleich. | A10 Z2202 | T-056, 2026-09-05 | — |
| AK-99 | Die Spalte behauptet keinen Kartenbezug, den die Daten nicht tragen. | A10 Z2217 | T-056, 2026-09-05 | — |
| AK-100 | Die Tabelle sagt das, statt es fuenfmal zu wiederholen. | A10 Z2238 | T-056, 2026-09-05 | — |
| AK-101 | Der Tagesatz unterscheidet zwischen den Ereignissen, statt auf 11 von 11 wortgleich zu stehen. | A10 Z2258 | T-056, 2026-09-05 | — |
| AK-102 | Die Prozentzahl nennt ihren Geltungsbereich und sagt, was sie nicht ist. | A10 Z2266 | T-056, 2026-09-05 | — |
| AK-103 | Eine Dauer steht nur an einer Zeile, die einen | A10 Z2274 | T-056, 2026-09-05 | — |
| AK-104 | Herleitungs- und Quellensprache steht nicht im Fliesstext. | A10 Z2281 | T-056, 2026-09-05 | — |
| AK-105 | Scale-Bearing Merchant steht einmal in der Liste, oder die beiden Eintraege verweisen sichtbar aufeinander. | A10 Z2296 | T-056, 2026-09-05 | — |
| AK-106 | A15, Vorgabe "der geglueckte Fall aendert sich nicht" | A15 Z3107 | T-074, 2026-09-06 | — |
| AK-107 | Die Aufloesung des Spielordners laeuft in der Reihenfolge gemerkter Pfad → find_game_dir() → Panel. | A15 Z3113 | T-074, 2026-09-06 | — |
| AK-108 | Auf einer Maschine ohne auffindbares Spiel und ohne gemerkten Pfad erscheint das Panel aus Abschnitt 3 statt der heutigen QMessageBox.critical aus … | A15 Z3118 | T-074, 2026-09-06 | — |
| AK-109 | Das Fenster im Frage-Zustand hat Titelleiste, Taskleisteneintrag und ist verschiebbar; | A15 Z3124 | T-074, 2026-09-06 | — |
| AK-110 | Der Knopf Choose folder... oeffnet eine Ordnerauswahl, keine Dateiauswahl, und startet in dem ersten existierenden Ort aus der Liste in 4.1. | A15 Z3128 | T-074, 2026-09-06 | — |
| AK-111 | Waehlt der Nutzer ...\ELDEN RING NIGHTREIGN statt ...\ELDEN RING NIGHTREIGN\Game, wird das Spiel gefunden und angenommen. | A15 Z3132 | T-074, 2026-09-06 | — |
| AK-112 | Angenommen wird ein Ordner nur, wenn regulation.bin lesbar und nicht leer ist, mindestens eine data.bhd aus bhd5.ARCHIVE_KEYS vorliegt und eine DLL … | A15 Z3139 | T-074, 2026-09-06 | — |
| AK-113 | Traegt weder der Fundordner noch eine seiner drei Elternebenen NIGHTREIGN im Namen, erscheint Text W1 mit den zwei Knoepfen, und der Standardknopf … | A15 Z3144 | T-074, 2026-09-06 | — |
| AK-114 | Nach einer Ablehnung bleibt das Fenster offen, nennt den versuchten Pfad, und der Knopf heisst Choose a different folder.... | A15 Z3149 | T-074, 2026-09-06 | — |
| AK-115 | Bricht der Nutzer die Systemauswahl ab, kehrt er in das Panel zurueck, in genau den Zustand, in dem er es verlassen hat. | A15 Z3153 | T-074, 2026-09-06 | — |
| AK-116 | Quit, Escape und das Fensterkreuz beenden das Programm ohne Fehlerdialog und ohne gespeicherte Angabe. | A15 Z3157 | T-074, 2026-09-06 | — |
| AK-117 | Ein bestaetigter Ordner steht vor dem Beginn des Baus in QSettings unter paths/game (Speicher favourites.ORG/favourites.APP). | A15 Z3161 | T-074, 2026-09-06 | — |
| AK-118 | Zwischen der Bestaetigung (C1/C2) und dem Beginn des Baus liegt kein weiterer Klick. | A15 Z3166 + A28 Z8004 + A29 Z8250 | T-146, 2026-09-08 | nachgezogen T-145 (A28 Z8004), dann praezisiert T-146 (A29 Z8250) |
| AK-119 | Gemerkter Pfad ungueltig, Automatik leer, aber datasource.bundled_path() existiert: | A15 Z3177 | T-074, 2026-09-06 | — |
| AK-120 | Gemerkter Pfad ungueltig, Automatik leer, kein Abzug: | A15 Z3182 | T-074, 2026-09-06 | — |
| AK-121 | Ein einzelner Fehlschlag loescht weder paths/game noch paths/save. | A15 Z3185 | T-074, 2026-09-06 | — |
| AK-122 | Fuer den Spielstand erscheint zu keinem Zeitpunkt ein Modal, das der Nutzer wegklicken muss. | A15 Z3189 | T-074, 2026-09-06 | — |
| AK-123 | Ist kein Spielstand geladen, steht in der Knopfzeile neben Rescan save ein sichtbarer Knopf Find my save.... | A15 Z3194 | T-074, 2026-09-06 | — |
| AK-124 | Die drei Ausgaenge einer Spielstandwahl sind unterscheidbar und tragen die Texte aus Abschnitt 7: | A15 Z3200 | T-074, 2026-09-06 | — |
| AK-125 | Eine gewaehlte Spielstanddatei wird unter paths/save gemerkt und beim naechsten Start bevorzugt. | A15 Z3205 | T-074, 2026-09-06 | — |
| AK-126 | Kein Text dieses Ablaufs zeigt den vollen Spielstandpfad. | A15 Z3210 | T-074, 2026-09-06 | — |
| AK-127 | Keiner der Texte aus Abschnitt 7 enthaelt eines der dort aufgelisteten verbotenen Woerter. | A15 Z3214 | T-074, 2026-09-06 | — |
| AK-128 | (A8) Alle Texte dieses Ablaufs sind Englisch, auch die Knopfbeschriftungen, der Fenstertitel und der Titel des Dateidialogs. | A15 Z3218 | T-074, 2026-09-06 | — |
| AK-129 | Bei Windows-Anzeige 100 %, 125 % und 150 % sowie bei den Programmfaktoren bis 200% ist in allen Zustaenden kein Text abgeschnitten, kein Knopf … | A15 Z3221 | T-074, 2026-09-06 | — |
| AK-130 | Der gesamte Ablauf ist ohne Maus bedienbar: | A15 Z3227 | T-074, 2026-09-06 | — |
| AK-131 | Das Panel erscheint nur fuer den Fall "kein Spielordner". | A15 Z3230 | T-074, 2026-09-06 (A32 Z9053 bestaetigt: keine Aenderung) | — |
| AK-132 | NH-002, oeffentliches Repo | A15 Z3235 | T-074, 2026-09-06 | — |
| AK-133 | Der Vorschlagsblock zeigt keinen zusammenfassenden Begruendungssatz. | A16 Z3714 | T-078, 2026-09-06 | — |
| AK-134 | Die Zahl der in einer Slotgruppe gezeichneten Effekt- und Fluchzeilen ist gleich der Zahl der Zeilen, die das Ergebnis fuer diesen Slot traegt. | A16 Z3718 | T-078, 2026-09-06 | — |
| AK-135 | Keine gezeichnete Zeile nennt die Slotnummer oder den Reliktnamen, die im Kopf ihrer Gruppe stehen. | A16 Z3723 | T-078, 2026-09-06 | — |
| AK-136 | Jede Zeile folgt einer der Fassungen aus §2 bzw. | A16 Z3726 | T-078, 2026-09-06 | — |
| AK-137 | , counted against it steht genau an den Zeilen, deren Beitrag ihre Groesse nach model.is_better_lower schlechter macht — nie nach dem Vorzeichen … | A16 Z3730 | T-078, 2026-09-06 | — |
| AK-138 | Fuer jede vorgeschlagene Kopie gilt: die Menge der Fluchnamen in ihrer Slotgruppe ist gleich der Menge ihrer curse_ids, ueber den Datensatz in … | A16 Z3738 | T-078, 2026-09-06 | — |
| AK-139 | AdvisorResult traegt ein Feld fuer die Fluche ohne Zahl (curses_without_a_figure), getrennt von not_counted. | A16 Z3745 | T-078, 2026-09-06 | — |
| AK-140 | Kein vom Berater gezeigter Text behauptet, die Spieldateien traegen fuer einen Fluch keine Zahlen. | A17 Z4294 (AK-157, fortgeschrieben) | T-080, 2026-09-06 | — |
| AK-141 | Der Schlusssatz mit der ✦-Legende steht genau einmal je Why-Dialog und in keinem Vorschlagsblock. | A16 Z3754 | T-078, 2026-09-06 | — |
| AK-142 | not_counted enthaelt ausschliesslich konditionale Effekte nach AD-010 (Build.situational, live == False). | A16 Z3759 | T-078, 2026-09-06 | — |
| AK-143 | Die beiden Klauseln aus 4.9a und 4.9b erscheinen woertlich wie in §5, in dieser Reihenfolge, jede nur wenn ihre Menge nicht leer ist, mit richtig … | A16 Z3763 | T-078, 2026-09-06 | — |
| AK-144 | Der gesamte vom Berater gezeigte Text (Block, Why-Dialog, Statuszeile, Tooltips) enthaelt keines der Woerter field, pool, handle, beam, scorer … | A16 Z3770 | T-078, 2026-09-06 | — |
| AK-145 | Die Halte-Zeile und die data_note folgen §8 woertlich, in allen dort genannten Fuellungen. | A16 Z3775 | T-078, 2026-09-06 | — |
| AK-146 | Die Zaehlzeile im Kopf jeder Slotgruppe folgt §6 woertlich; | A16 Z3777 | T-078, 2026-09-06 | — |
| AK-147 | Kein Anzeigecode zerlegt, durchsucht oder schneidet eine Zeichenkette, die aus explain.py stammt. | A17 Z4236 (fortgeschrieben) | T-080, 2026-09-06 | — |
| AK-148 | In keiner Slotgruppe erscheint ein Fluchname zweimal. | A16 Z3790 | T-078, 2026-09-06 | — |
| AK-149 | AK-29 und AK-30 gelten unveraendert fuer jede neue Zeile: | A16 Z3792 | T-078, 2026-09-06 | — |
| AK-150 | Schlechtester gemessener Fall des developer nachgestellt — sechs belegte Slots, darunter einer mit sieben Effektzeilen und zwei Fluchzeilen … | A17 Z4319 (AK-160) | T-080, 2026-09-06 | vollstaendig durch AK-160 - A17 Z4319 (T-080); die Schaetzwerte sind durch Messwerte ersetzt |
| AK-151 | Jeder Effekt einer vorgeschlagenen Kopie, zu dem keine Zeile nach T-078 §2 entstanden ist, erscheint mit Namen in der Slotgruppe seines Slots … | A17 Z4271 | T-078, 2026-09-06 | — |
| AK-152 | Der Wortlaut jeder stummen Zeile ist einer der aus §4, woertlich, mit Punkt am Ende. | A17 Z4276 | T-078, 2026-09-06 | — |
| AK-153 | AdvisorResult traegt effects_without_a_figure getrennt von curses_without_a_figure und von not_counted. | A17 Z4281 | T-078, 2026-09-06 | — |
| AK-154 | Die stummen Zeilen der Fuellung (b) und die Liste aus 4.9b entstehen aus einer Menge (Build.situational, live == False). | A17 Z4284 | T-078, 2026-09-06 | — |
| AK-155 | In jeder Slotgruppe gilt {total} − {n} genau gleich der Zahl der gezeichneten stummen Zeilen — ohne Ausnahme, auch fuer Effekte ohne Namen im … | A17 Z4288 + A21 Z5516 (gilt in beiden Lesarten) | T-092, 2026-09-07 | — |
| AK-156 | Keine stumme Zeile benutzt ✦, CURSE/BAD, ⚠ oder eine Warnfarbe; | A17 Z4292 + A18 Z4414 (Ausnahme fuer Fuellung (a)) | Director/App Designer, 2026-09-06 | fuer Fuellung (a) durch die Director-Korrektur - A18 Z4414 (06.09.2026); fuer (a2), (b), (c), (d), (e) unveraendert |
| AK-157 | Keine stumme Zeile behauptet etwas ueber die Spieldateien; | A17 Z4296 | T-078, 2026-09-06 | — |
| AK-158 | Die Zaehlzeile aus T-078 §6 steht in jeder Slotgruppe, auch wenn jeder Effekt darunter genannt ist, und benutzt die beiden neuen Fuellungen aus §5 … | A17 Z4303 | T-078, 2026-09-06 | — |
| AK-159 | Die Menge der Fluchnamen im Vorschlagsblock einer Slotkarte ist gleich der Menge der curse_ids der vorgeschlagenen Kopie, in Namen aufgeloest — … | A17 Z4311 | T-078, 2026-09-06 | — |
| AK-160 | Ersetzt AK-150 vollstaendig. | A17 Z4319 | T-092, 2026-09-07 (AK-189 schreibt fort) | **widerspruechlich** - als schlechtester Fall ueberholt durch AK-189 (A21 Z5827, T-092); zusaetzlich schreibt sein Messfenster `1320 px (Startbreite)` vor, obwohl A14 Z2555 (T-071) die feste Startbreite aufgehoben hat |
| AK-161 | Die Zeilenzahl je Vorschlag wird nach dem Einbau neu gemessen und im Bericht genannt. | A17 Z4344 + A21 Z5537 (je Lesart getrennt) | T-092, 2026-09-07 | — |
| AK-162 | Registry-Haelfte, ersetzt die erste Haelfte von AK-63. | A19 Z4554 | T-084, 2026-09-07 (A21 Z5600: gilt unveraendert) | — |
| AK-163 | Ergebnis-Haelfte im Picker, ersetzt die zweite Haelfte von AK-63. | A19 Z4563 + A21 Z5606 | T-092, 2026-09-07 | das Rot-vorher von AK-163 - AK-190, A21 Z5606 (T-092); Regel und Pruefweg unveraendert |
| AK-164 | Ergebnis-Haelfte beim Lauf. | A19 Z4571 | T-084, 2026-09-07 (A21 Z5612: gilt unveraendert) | — |
| AK-165 | keine Chirurgie, keine Entdopplung. | A19 Z4578 | T-084, 2026-09-07 (A21 Z5613: gilt unveraendert) | — |
| AK-166 | weights_note im Picker. | A19 Z4585 | T-084, 2026-09-07 (A21 Z5614: gilt unveraendert) | — |
| AK-167 | Reihenfolge. | A19 Z4673 | T-084, 2026-09-07 (A20 Z4878: bleibt unveraendert) | — |
| AK-168 | Test von (c). | A19 Z4678 + A20 Z4880/Z5116 (praezisiert) | T-086, 2026-09-07 | seine Zahlen durch AK-180 - A20 Z5161 (T-086); Regel und Pruefweg unveraendert |
| AK-169 | Partition, mit Rezept. | A19 Z4684 + A20 Z5161 (AK-180) | T-086, 2026-09-07 | die Zahlenreihe durch AK-180 - A20 Z5161 (T-086); Regel und Pruefweg unveraendert |
| AK-170 | Solange AdvisorResult.budget_note leer ist, zeichnet die Oberflaeche dafuer nichts — keine Ueberschrift, keinen Platzhalter, keinen leeren … | A19 Z4733 | T-084, 2026-09-07 | — |
| AK-171 | Ist das Feld nicht leer, steht sein Satz im Why-Dialog als eigene Zeile unmittelbar unter den Saetzen aus Punkt 4, und nirgends in der Statuszeile. | A19 Z4738 | T-084, 2026-09-07 | — |
| AK-172 | In budget_note steht kein Satz, der in jedem Lauf zutraefe. | A19 Z4743 | T-084, 2026-09-07 | — |
| AK-173 | 4.7 lautet buchstabengetreu Your build changed while this was working out — use Optimize again., mit demselben Gedankenstrich — wie 4.8, in … | A19 Z4799 | T-084, 2026-09-07 | — |
| AK-174 | Der Satz aus 4.7 erreicht den Nutzer ungekuerzt in der Statuszeile, an der Mindestbreite des Build planner. | A19 Z4804 | T-084, 2026-09-07 | — |
| AK-175 | Keine Statuszeile des Beraters gibt dem Nutzer die Schuld: | A19 Z4812 | T-084, 2026-09-07 | — |
| AK-176 | In UI_SPEC.md bezeichnet Suggest kein heutiges Bedienelement mehr: | A19 Z4834 | T-084, 2026-09-07 | — |
| AK-177 | der Test von (c) fragt, was das Programm beantwortet hat. | A20 Z5115 | T-086, 2026-09-07 | — |
| AK-178 | wepTypeTriggerCount allein nennt keinen Hebel. | A20 Z5131 | T-086, 2026-09-07 | — |
| AK-179 | eine Schranke auf einen Waffentyp, den es nicht gibt, ist kein Armaturenfall. | A20 Z5145 | T-086, 2026-09-07 | — |
| AK-180 | Partition, Zahlen fortgeschrieben. | A20 Z5161 | T-086, 2026-09-07 | — |
| AK-181 | jede Zahl im Fliesstext nennt ihre Lesart. | A20 Z5202 | T-086, 2026-09-07 | — |
| AK-182 | eigenes Element, zwei Eintraege. | A21 Z5755 | T-092, 2026-09-07 | — |
| AK-183 | kein neuer Zustand. | A21 Z5765 | T-092, 2026-09-07 | — |
| AK-184 | nie zwei Zahlen. | A21 Z5772 | T-092, 2026-09-07 | — |
| AK-185 | genau viermal, nie je Zeile. | A21 Z5793 | T-092, 2026-09-07 | — |
| AK-186 | Voreinstellung fuer Bedingungen, nie fuer Zahlen. | A21 Z5801 | T-092, 2026-09-07 | — |
| AK-187 | die Lesarten teilen not_counted, sie erfinden nichts. | A21 Z5810 | T-092, 2026-09-07 | — |
| AK-188 | die Listen behalten ihre Saetze. | A21 Z5818 | T-092, 2026-09-07 | — |
| AK-189 | der schlechteste Fall ist laenger, und das wird gemessen. | A21 Z5827 | T-092, 2026-09-07 | — |
| AK-190 | der Satz wandert und wird umgeschrieben. | A21 Z5839 | T-092, 2026-09-07 | — |
| AK-191 | die Rangfolge haengt an keiner gefuehrten Waffe. | A21 Z5849 | T-092, 2026-09-07 | — |
| AK-192 | die Armaturenzeile nennt die Zahl, nicht den Hebel. | A21 Z5859 | T-092, 2026-09-07 | — |
| AK-193 | die Spalte nennt die Groesse, die sie zeigt. | A21 Z5869 | T-092, 2026-09-07 | — |
| AK-194 | die Breite wird gemessen, nicht geschaetzt. | A21 Z5780 | T-092, 2026-09-07 | **widerspruechlich** - schreibt die Messung `bei 1320 px Fensterbreite` vor, obwohl A14 Z2555 (T-071) die feste Startbreite 1320 px aufgehoben und durch eine abgeleitete Breite ersetzt hat |
| AK-195 | Neu, als AK-195: In beiden Zielsortierungen stehen die Karten mit dem Spitzenwert beider Zielrichtungen an der Spitze des Rasters, vor allen … | UI_SPEC §5.4 (AK-261) | T-192, 2026-09-12 | **ersetzt durch AK-261** (T-192): „beide Richtungen“ ist mit drei Richtungen unterbestimmt; alle Spitzengruppen fuehren, in fester Reihenfolge |
| AK-196 | Neu, als AK-196, und ersetzt die zweite Haelfte von AK-51: | A22 Z5967 | Director, 2026-09-07 | — |
| AK-197 | zwei Anstriche, nicht drei. | A24 Z6942 (AK-211) | T-127, 2026-09-08 | gestrichen, ersetzt durch AK-211 - A24 Z6942 (T-127); Streichliste A24 Z6915 |
| AK-198 | der erste Anstrich behauptet nichts. | A24 Z6951 (AK-212) | T-127, 2026-09-08 | gestrichen, ersetzt durch AK-212 - A24 Z6951 (T-127); Streichliste A24 Z6916 |
| AK-199 | die Ordnung ohne Antwort ist die beraterfreie. | A24 Z6951 (AK-212) und Z6967 (AK-213) | T-127, 2026-09-08 | gestrichen, ersetzt durch AK-212 und AK-213 - A24 Z6951/Z6967 (T-127); Streichliste A24 Z6919 |
| AK-200 | die Zusammenfassungszeile behauptet keine Rangfolge, die es nicht gibt. | A24 Z6977 (AK-214) | T-127, 2026-09-08 | gestrichen, ersetzt durch AK-214 - A24 Z6977 (T-127); Streichliste A24 Z6920 |
| AK-201 | die Pflichtzeilen warten nicht. | A23 Z6421 | T-124, 2026-09-08 (A24 Z6925: gilt unveraendert weiter) | — |
| AK-202 | nichts erscheint, nichts verschwindet, nichts ist gesperrt. | A24 Z6989 (AK-215) | T-127, 2026-09-08 | gestrichen, ersetzt durch AK-215 - A24 Z6989 (T-127); Streichliste A24 Z6921 |
| AK-203 | die Antwort bewegt nur, was sie bewegen muss. | A24 Z6994 (AK-216, Groesse) und Z7019 (AK-217, Fokus/Bildlauf) | T-127, 2026-09-08 | gestrichen, ersetzt durch AK-216 und AK-217 - A24 Z6994/Z7019 (T-127); Streichliste A24 Z6922 |
| AK-204 | der Zielrichtungswechsel wartet nicht. | A23 Z6443 | T-124, 2026-09-08 (A24 Z6926: gilt unveraendert weiter) | — |
| AK-205 | gezeichnet wird die gewaehlte Richtung, nicht die sortierte. | UI_SPEC §5.4 (AK-263) | T-192, 2026-09-12 | **ersetzt durch AK-263** (T-192): der tragende Satz gilt weiter, die Aufzaehlung nicht mehr — die Wertzeilen haben keine Richtung, ein Chip kann eine andere nennen |
| AK-206 | eine Frage je Oeffnung. | A23 Z6456 | T-124, 2026-09-08 (A24 Z6928: gilt unveraendert weiter) | — |
| AK-207 | die ueberholte Antwort erreicht nichts. | A23 Z6464 + A24 Z6929 | T-127, 2026-09-08 | die zweite Zusage (`eine im Wartezustand ausgewaehlte Karte wird uebernommen`) entfaellt gegenstandslos - A24 Z6929 (T-127) |
| AK-208 | der Fehlschlag hat seinen eigenen Satz. | A23 Z6469 + A24 Z6932 (erweitert durch AK-218) | T-127, 2026-09-08 | — |
| AK-209 | drei Zeichen, drei Aussagen, nie vertauscht. | A24 Z7047 (AK-219) | T-127, 2026-09-08 | gestrichen, ersetzt durch AK-219 - A24 Z7047 (T-127); Streichliste A24 Z6923 |
| AK-210 | die Zusagen des Bestands ueberleben den Umbau. | A23 Z6480 | T-124, 2026-09-08 (A24 Z6933: gilt unveraendert weiter) | — |
| AK-211 | zwei Anstriche, nicht drei — ersetzt AK-197. | A24 Z6942 | T-127, 2026-09-08 | — |
| AK-212 | das leere Raster ist ein Zustand, kein Nichts — ersetzt AK-198; dies ist der Waechter W2. | A24 Z6951 | T-127, 2026-09-08 | — |
| AK-213 | waehrend der Leere ist nichts gesperrt und nichts geht verloren — nimmt die Sort by-Zusage aus AK-199 auf. | A24 Z6966 | T-127, 2026-09-08 | — |
| AK-214 | Zeile 3 behauptet keine Rangfolge und zaehlt nichts, was nicht dasteht — ersetzt AK-200. | A24 Z6977 | T-127, 2026-09-08 | — |
| AK-215 | was erscheinen darf, und wo — ersetzt AK-202. | A24 Z6989 | T-127, 2026-09-08 | — |
| AK-216 | die Groesse steht beim ersten Anstrich, nicht bei der Antwort — ersetzt die Groessenhaelfte von AK-203; die scharfe Stelle dieser Entscheidung. | A24 Z7000 | T-127, 2026-09-08 | — |
| AK-217 | Fokus und Bildlauf — ersetzt die zweite Haelfte von AK-203. | A24 Z7019 | T-127, 2026-09-08 | — |
| AK-218 | die Leere ist nie das letzte Wort. | A25 Z7159 (Fassung 2) | T-135, 2026-09-08 | Fassung 1 (A24 Z7036) durch Fassung 2 - A25 Z7159 (T-135) |
| AK-219 | zwei Zeichen, zwei Aussagen — ersetzt AK-209. | A24 Z7047 | T-127, 2026-09-08 | — |
| AK-220 | das Fenster ist vor dem Spielstand da. | A26 Z7705 | T-141, 2026-09-08 | — |
| AK-221 | der Wartezustand ist ein Zustand, kein Nichts. | A26 Z7713 | T-141, 2026-09-08 | — |
| AK-222 | keine Zahl, die noch niemand kennt, und keine Aussage ueber einen ungelesenen Bestand. | A26 Z7723 | T-141, 2026-09-08 | — |
| AK-223 | Im Zustand aus AK-221 ist der Reliktknopf (choose_button) jeder Slotkarte gesperrt und oeffnet keinen Picker; | A26 Z7730 + A30 Z8545 (AK-243 praezisiert) | T-148, 2026-09-09 | — |
| AK-224 | Jedes Lesen endet in einem Zustand, in dem die Spielstandzeile einen der vier Saetze aus §6 traegt — die Bestandsnotiz, die Notiz mit dem Zusatz … | A26 Z7743 + A30 Z8609 (AK-244 zieht nach) | T-148, 2026-09-09 | — |
| AK-225 | die Ankunft bewegt nichts. | A26 Z7758 | T-141, 2026-09-08 | — |
| AK-226 | kein nachtraegliches Ueberschreiben. | A26 Z7775 | T-141, 2026-09-08 | — |
| AK-227 | ein Lesen zur Zeit, und es ist zu sehen. | A26 Z7789 | T-141, 2026-09-08 | — |
| AK-228 | der langsame Weg ist kein Fehlschlag. | A26 Z7795 | T-141, 2026-09-08 | — |
| AK-229 | Der Satzanfang Save could not be read: erscheint nur, wenn am Ende des Lesens kein Bestand vorliegt. Kein Text, der hinter diesem Praefix landen … | A26 Z7806 | T-141, 2026-09-08 | — |
| AK-230 | Kein Text dieses Ablaufs sagt oder legt nahe, aus dem gewaehlten Ordner werde ausschliesslich gelesen. | A28 Z8138 | T-145, 2026-09-08 | — |
| AK-231 | Die drei neuen Textstellen (A1 Absatz 3, W1 Absatz 4, C3) sind Englisch (A8, AK-128) und enthalten keines der in §7 aufgelisteten verbotenen … | A28 Z8145 | T-145, 2026-09-08 | — |
| AK-232 | (C2 → C3) | A29 Z8382 (T-146-Fassung, Abstand 1) + A32 Z9004 (AK-246, ab Abstand 2) | T-163, 2026-09-09 | T-145-Fassung (A28 Z8150) durch die T-146-Fassung - A29 Z8382; deren Satz `innerhalb = kein C3` ab zwei Ebenen Abstand durch AK-246 - A32 Z9004 (T-163) |
| AK-233 | C1 unberuehrt, A15/AK-106 | A28 Z8164 | T-145, 2026-09-08 (A29 Z8371 und A32 Z9042: unveraendert) | — |
| AK-234 | In C3 ist Use this folder der Standardknopf und wird von Enter ausgeloest; | A28 Z8170 | T-146, 2026-09-08 | T-145-Fassung nachgezogen - A28 Z8170 (T-146) |
| AK-235 | Choose a different folder... in C3 oeffnet erneut den Systemordnerdialog, dessen Startort der zuvor gewaehlte Ordner ist. Wird der Systemdialog … | A28 Z8179 | T-145, 2026-09-08 | — |
| AK-236 | nichts vor der Antwort | A28 Z8185 | T-145, 2026-09-08 | — |
| AK-237 | (hoechstens eine Rueckfrage je Wahl) | A29 Z8400 | T-146, 2026-09-08 | T-145-Fassung (A28 Z8190) nachgezogen - A29 Z8400 (T-146); A32 Z9046 bestaetigt sie fuer den neuen Ausloeser |
| AK-238 | Escape und das Fensterkreuz beenden aus C3 heraus das Programm ohne Fehlerdialog und ohne gespeicherte Angabe, wie in A1, A2, E1 und W1 (§9). | A28 Z8200 | T-145, 2026-09-08 | — |
| AK-239 | Skalierung, Nachweis am Fenster | A28 Z8203 | T-145, 2026-09-08 | — |
| AK-240 | Liegt der aufgeloeste Ordner innerhalb des gewaehlten (§4.2, Abstieg bis Tiefe 3), erscheint zwischen der Ordnerwahl und dem Bau-Zustand kein … | A29 Z8413 | T-146, 2026-09-08 | — |
| AK-241 | Der gebaute Wortlaut von C3 enthaelt fuer die zweite Pfadzeile die Beschriftung The game itself is outside that folder, in:, nicht die neutrale … | A29 Z8426 | T-146, 2026-09-08 | — |
| AK-242 | die Zeile nach C3 ist C1, nicht C2 | A29 Z8434 | T-146, 2026-09-08 (A32 Z9046: unveraendert) | — |
| AK-243 | gesperrt sind zwei, aus verschiedenen Gruenden — praezisiert AK-223 | A30 Z8545 | T-148, 2026-09-09 | — |
| AK-244 | ), eine mit einem Vermerk statt einer neuen Nummer, wie im Auftrag verlangt. | A30 Z8609 (erste Haelfte) + A31 Z8828 (AK-245 fuer die zweite) | T-154, 2026-09-09 | zweite Haelfte durch AK-245 - A31 Z8828 (T-154); erste Haelfte unveraendert gueltig |
| AK-245 | im Nachtrag „AK-244 nachgezogen — die Regel statt der Liste" am Ende dieser Datei; | A31 Z8828 | T-154, 2026-09-09 | — |
| AK-246 | SEC-032 — die klickfreie Zustimmung reicht nur eine Ebene weit | A32 Z9004 | T-163, 2026-09-09 | — |
| AK-247 | C3-Wortlaut behauptet fuer keinen seiner beiden Ausloeser die falsche Richtung | A32 Z9017 | T-163, 2026-09-09 | — |
| AK-248 | hoechstens eine Rueckfrage je Wahl, gilt auch fuer den neuen Ausloeser | A32 Z9025 | T-163, 2026-09-09 | — |
| AK-249 | SEARCH_DEPTH/SEARCH_PARENTS unveraendert | A32 Z9034 | T-163, 2026-09-09 | — |
| AK-250 | die Gesamtzahl hat eine Zeile, die ihr gehoert | A33 Z9469 | T-178, 2026-09-09 | — |
| AK-251 | die Zahl nennt Einheit und Geltungsbereich, woertlich | A33 Z9487 | T-178, 2026-09-09 | — |
| AK-252 | keine Zahl, bevor gelesen ist — und die Ankunft bewegt nichts | A33 Z9499 | T-178, 2026-09-09 | — |
| AK-253 | der Erststart verspricht keine Dauer, die er nicht halten kann | A33 Z9516 | T-178, 2026-09-09 | — |
| AK-254 | kein erfundener Fortschritt — und die gelobte Zeile bleibt | A33 Z9529 | T-178, 2026-09-09 | — |
| AK-255 | nichts ist abgeschnitten, an keiner Skalierung | A33 Z9542 | T-178, 2026-09-09 | — |
| AK-256 | das `Sort by` ist die Projektion der Richtungs-Registry, nicht eine Liste von Woertern — ersetzt AK-43 | UI_SPEC §5.4 | T-192, 2026-09-12 | — |
| AK-257 | der dritte Eintrag heisst `Maximise offensive attributes` und steht hinter den beiden bisherigen (gemessen: 183 px gegen 200 px Schranke) | UI_SPEC §5.4 | T-192, 2026-09-12 | — |
| AK-258 | drei Wertzeilen, immer — keine Zeile, die mit der Richtung kommt und geht (gemessen: +18 px Kartenhoehe) | UI_SPEC §5.4 | T-192, 2026-09-12 | — |
| AK-259 | die dritte Zeile nennt ihre Groesse und ihre Einheit: `Offensive attributes` / `pts` (A12) | UI_SPEC §5.4 | T-192, 2026-09-12 | — |
| AK-260 | die dritte Zahl wird gerundet wie jede andere — keine Rundung je Richtung | UI_SPEC §5.4 | T-192, 2026-09-12 | — |
| AK-261 | die Spitzenkarten jeder Richtung fuehren, in fester Reihenfolge — ersetzt AK-195 | UI_SPEC §5.4 | T-192, 2026-09-12 | — |
| AK-262 | jede vorgezogene Karte sagt mit ihrem Chip, warum sie vorn steht — erweitert AK-46 | UI_SPEC §5.4 | T-192, 2026-09-12 | — |
| AK-263 | was in der gelesenen Richtung gezeichnet wird und was gar keine Richtung hat — ersetzt AK-205 | UI_SPEC §5.4 | T-192, 2026-09-12 | — |


## Widerspruechliche Faelle

*Nachgetragen am 12.09.2026 in T-184. Die Zeile zu AK-05 verweist seit T-181
auf diesen Abschnitt; er fehlte, weil der T-181-Lauf unmittelbar nach dem
Schreiben der Tabelle abgebrochen ist. Hier wird nichts entschieden.*

Drei Kriterien tragen in der Spalte *ueberholt durch* den Eintrag
`widerspruechlich`: **AK-05**, **AK-160**, **AK-194**. Alle drei haengen an
derselben Sache — der Startbreite **1320 px**, die `A14 Z2555`
(Director-Nachtrag zu AK-05, 06.09.2026) als feste Zahl aufgehoben hat,
waehrend zwei spaetere Kriterien sie erneut als Bezugsbreite vorschreiben.

Der Fall ist vollstaendig beschrieben in `UI_SPEC.md`, Abschnitt
**„Drei widerspruechliche Faelle — Entscheidung des App Designers steht aus"**
(dort mit dem Wortlaut von `A14` und der Frage, die zu entscheiden ist).

**Die Entscheidung gehoert dem App Designer.** Bis sie faellt, fuehren
`UI_SPEC.md` und dieses Register beide Fassungen nebeneinander.
