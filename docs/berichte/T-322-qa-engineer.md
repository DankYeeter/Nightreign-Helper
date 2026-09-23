STATUS: erledigt
AUFTRAG: T-322e - QA am Artefakt 1.16.0 (`dist\NightreignHelper.exe`,
59.159.482 B, SHA-256 804F9E2B...25E6C, Bau T-322b `c28a7b8` auf Code
`41173d9`): Nachweis A25 woertlich, AK-335/AK-336 nach dem Fix T-322f,
Kanten aus T-321b/c
GELESEN: docs/tasks/T-322.md (vollstaendig); GOAL.md A25 (Z. 511-531);
UI_SPEC.md Abschnitt 3.7 (AK-327..AK-336, Nachtrag T-322d) und AK-271;
UI_SPEC_REGISTER.md Zeilen AK-05/AK-334; DESIGN_REVIEW.md Abschnitt T-322d
(DR-034..DR-037); `git log -3 --format=%B 41173d9`; docs/tasks/T-321.md
(dort **kein** Abschnitt "An qa-engineer" - siehe Annahme 1);
nrplanner/advisor/goals.py (`chosen_label`, `_headline_with_choice`,
`_max_damage`), nrplanner/relicpicker.py (`_chosen_damage_art`,
`_named_for_choice`, `_captions`, `_say_what_was_left_out`,
`nothing_raises`), nrplanner/advisor/explain.py (`_rating_word`),
nrplanner/model.py (`attack_arts`), nrplanner/app.py (`_set_search`,
`_opening_width`); scripts/drive_window.ps1; qa/findings.md (Kopf + Ende,
hoechste Nummer QA-288)
GEAENDERT: nichts im Arbeitsbaum ausser diesem Bericht
(`docs/berichte/T-322-qa-engineer.md`, neu) und dem Commit dazu. Kein
Eintrag in `qa/findings.md` durch mich - die zwei Zeilen stehen unten als
QA-Log zum Anhaengen. Scratchpad: `<Scratchpad>/T-322e/` (eigenes
LOCALAPPDATA/APPDATA, Testabzug 841 Dateien / 21.131.645 B hineinkopiert,
Treiberskripte, Bildnachweise)
ANNAHMEN: (1) Der Auftrag nennt Entwicklerhinweise "An qa-engineer" in
`docs/tasks/T-321.md`; die Datei enthaelt keinen solchen Abschnitt
(`grep -n "qa\|QA\|Rueckmeldung" docs/tasks/T-321.md`, 20.09.2026, Stand
`c28a7b8`: 0 Treffer). Ich habe stattdessen die Commit-Texte
`41173d9`/`78a0888` verwendet. (2) "Kopfzahl der Karte" aus AK-335 lese ich
als den Wortlaut, den `GoalScore.display` ueber `explain._rating_word` auf
die Slotkarte und in den `Why`-Dialog bringt (`Attack rating +4`) - das ist
die einzige Senke von `display` im Baum.
NAECHSTER: director (Entscheid zu QA-289/QA-290, dann Freigabe A25)
BLOCKIERT DURCH: nichts

---

# T-322e - qa-engineer: A25 am Artefakt 1.16.0

## Umgebung und Nachweis der Umlenkung

- Artefakt gegengeprueft: `Get-FileHash` 20.09.2026 ->
  `804F9E2B4A0A41289F64F4D8EE34146D99F489FDE30C679058E783F2CBF25E6C`,
  Laenge `59159482` - deckungsgleich mit dem Bericht des `release-manager`.
- `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-322e`, `LOCALAPPDATA` und `APPDATA`
  auf frische Scratchpad-Ordner; Testabzug hineinkopiert (nachgezaehlt: 841
  Dateien, 21.131.645 Bytes). Positiver Beleg der Umlenkung: nach dem Lauf
  liegen `builds\1|6|7` und `chalices\1|6` unter
  `HKCU\Software\DankYeeterT-322e\NightreignHelper`. Der Spielstand wurde
  nur gelesen (`You own 313 relics in total.`), nie geschrieben;
  `nightreign.exe` lief waehrend der Messungen nicht.
- NH-004: `Get-Process NightreignHelper` vor dem Start 0; drei Fensterlaeufe
  **nacheinander** (Hauptlauf, Neustartprobe, Nachmessung zu QA-290), nach
  jedem `Stop-Process -Force`; Endstand 20.09.2026 14:23 -> **0 Prozesse**.
- Fenstertreiber ausschliesslich `scripts/drive_window.ps1` (dot-gesourct).
  Eine Werkzeuggrenze, kein Befund: der Hold-Schalter heisst im
  eingeschalteten Zustand `Held`, `Els $m "^Hold$"` findet ihn dann nicht -
  Treffer nur mit `"^Hold$|^Held$"`.
- Bildnachweise per `PrintWindow` aus dem Programmfenster (NH-002):
  `out/bar1536.png`, `out/bar1366.png`, `out/opening.png` im Scratchpad.

## Risiko-Briefing (vor dem Testen formuliert)

Das Risiko liegt fast vollstaendig im Fix T-322f (`41173d9`), der einen Tag
alt ist und zwei Anzeigen betrifft, die vorher stumm falsch waren: die
Kopfzahl bei einer Artwahl (AK-335) und der Relic Picker (AK-336). Beides
haengt an Zustaenden, die nur zusammen auftreten - eine Artwahl **und** ein
Relikt mit `art_rate != 1,0` im gewerteten Build, bzw. eine Artwahl **und**
ein `Sort by`, das gerade nicht `Maximise damage` ist. Deshalb zuerst
AK-335 (Wylder, Skill attack, Startwaffen-Relikte), dann AK-336 (Fire,
`Sort by` auf beiden anderen Werten), dann der woertliche A25-Nachweis
(Revenant Magic/Bestial), dann die Kanten aus T-321b/c (Katalysator,
Typ ohne Vorkommen, Richtungswechsel, Neustart, AK-08, Deep, 1536 px).

## 1. AK-335 - Kopfzahl traegt den gewaehlten Namen (Wylder, Skill attack)

Aufbau: Wylder, Gefaess `Soot-Covered Wylder's Urn`, beide
Startwaffen-Relikte gesetzt - Slot 1 (Blau) `Delicate Drizzly Scene`
(*Starting armament deals magic damage*, einziger Treffer im 54er-Pool),
Slot 3 (Gelb) `Grand Luminous Scene` (*Starting armament deals holy
damage*, einziger Treffer im 54er-Pool). Damit die Kopfzahl ueberhaupt
einen Attributsbeitrag zu beschriften hat, wurde `Strength +3` im
Effektfilter kurzzeitig favourisiert (danach wieder entfernt, Registry
`advisor/required` zurueck auf `[]`).

| Damage type | Zeile im `Why`-Dialog | Vorschlag Slot 1 |
|---|---|---|
| `All` | `Strength +3: Strength +3  Attack rating +4` | `Grand Drizzly Scene` |
| `Skill attack` | `Strength +3: Strength +3  Skill attack rating +4` | `The Will of the Balancers` |

- Die Beschriftung wechselt auf **`Skill attack rating`**, nicht
  `Skill attack attack rating` - die Wortkollisionsregel aus AK-335 haelt am
  Artefakt.
- Die Reihung ist eine andere: unter `Skill attack` steht
  `The Will of the Balancers` (traegt *Improved Skill Attack Power +15.0%*)
  vorn, unter `All` `Grand Drizzly Scene`.
- Wertunterschied gemessen (Abschnitt 3): derselbe Kandidat traegt im
  selben Build `+1.9 AR` unter `All` und `+2.2 AR` unter `Skill attack`
  (Faktor 1,15 = der gehaltene `+15,0 %`-Skillbuff). AK-335s zweite Haelfte
  ("ihr Wert unterscheidet sich vom Wert bei All") ist damit belegt.
- Der AK-331-Satz stand in jedem geprueften Fall **genau einmal**:
  `Ranked on skill attack damage only - every other effect on a candidate
  still shows, but only this counts toward the ranking.`

**DR-034 am Artefakt behoben.**

## 2. AK-336 - Relic Picker nennt die Wahl (Fire, `Sort by` anders)

Pruefweg woertlich nachgestellt: `Fire` in der Leiste gewaehlt, `goal_box`
auf `Minimise damage taken` (Paar blendet sich aus, Wert bleibt), Picker
`Slot 2 - Blue` geoeffnet.

- `Sort by: Minimise damage taken` -> Zeile 4 traegt
  `Ranked on fire damage only - ...`; jede Karte zeigt `Damage (Fire)`.
- `Sort by: Name` -> unveraendert derselbe Satz, unveraendert
  `Damage (Fire)`.
- Gegenprobe mit `Magic` (wo tatsaechlich etwas steigt) und
  `Sort by: Maximise damage`: Chip **`BEST FOR DAMAGE (Magic)`**, Zeile
  `Damage (Magic) +4.0 AR`, Satz einmal.
- Ohne Wahl (`All`) steht die unveraenderte Zeile `Damage` und kein
  zusaetzlicher Satz.

**DR-035 am Artefakt behoben**, beide Mindestanforderungen aus AK-336.

## 3. Nachweis A25, Teilsatz fuer Teilsatz

Wortlaut GOAL.md A25: *"Revenant (Startwaffe Cursed Claws, 71,63 von 88,65
AR Magic) mit Auswahl 'Magic' bzw. 'Bestial' (Schulwahl) liefert eine andere
Reihung als 'Alle', und die Why-Zeile nennt die Art; Wylder mit beiden
Startwaffen-Relikten und Auswahl 'Skill attack' zaehlt die Konversion in die
Schadenszahl."*

| Teilsatz | Ergebnis | Nachweis |
|---|---|---|
| Revenant, `Magic`, andere Reihung als `Alle` | **belegt** | Picker `Slot 1 - Blue`, `Sort by: Maximise damage`, alle 54 Karten je Lauf ausgelesen. Zahlen aendern sich (Spitze `Delicate Drizzly Scene` +11.5 -> +19.8 AR; +2.8 -> +2.2; +8.9 -> +7.2) und die Reihenfolge auch (`The Will of the Balancers` Rang 13 -> Rang 10) |
| Revenant, `Bestial` (Schulwahl), andere Reihung als `Alle` | **belegt** | derselbe Pool: unter `Bestial` schiebt sich ein `Grand Drizzly Scene` mit **+5.3 AR** auf Rang 5, das unter `Alle` mit +4.5/+3.1 weiter hinten steht; ab Rang 33 verschiebt sich die gesamte Restliste |
| Why-Zeile nennt die Art | **belegt** | `Ranked on magic damage only - ...` bzw. `Ranked on bestial damage only - ...`, je genau einmal, in Leiste und Picker |
| Wylder, beide Startwaffen-Relikte, `Skill attack`, Konversion zaehlt in die Schadenszahl | **belegt** | Build: Slot 1 gefragt, Slot 2 `The Will of the Balancers` (+15 % Skill), Slot 3 leer. Kandidat `Delicate Drizzly Scene` (einziger wirksamer Effekt ist die Konversion) im Picker: `Damage` **+1.9 AR** unter `All`, `Damage (Skill attack)` **+2.2 AR** unter `Skill attack`, `Damage (Magic)` **+21.0 AR** unter `Magic`. Die Konversion traegt also eine Kandidatenwertung > 0 und wird von der Artwahl multipliziert |

Randnotiz ohne Befundcharakter: die Zahlen "71,63 von 88,65 AR Magic" aus
GOAL stammen aus einem hoeheren Rang; das Fenster zeigt fuer
`Revenant's Cursed Claws` bei Stufe 1 `Common - 44 1H / 34 2H AR`
(Physical 8, Magic 36). Das Verhaeltnis (Magic traegt den Grossteil) stimmt,
die absoluten Zahlen sind rangabhaengig.

## 4. Kanten aus T-321b/c

| Kante | Erwartet | Gemessen |
|---|---|---|
| Typ ohne Vorkommen (Wylder, `Fire`) | Rangfolge ab 0,00, **kein** 4.10 | Leiste antwortet `Maximise damage - 3 of 3 slots filled.`, drei Vorschlaege; der Satz `The game files carry no figures ...` erscheint nicht. Jede Pickerkarte zeigt `Damage (Fire) no change`. **Siehe aber QA-289/QA-290** |
| Recluse (Katalysator) unveraendert + Satz | Reihung wie `All`, Katalysatorsatz | `All`/`Sorceries`/`Bestial`/`Fire` liefern identisch `Slot 1/2 Grand Drizzly Scene`, `Slot 3 Grand Tranquil Scene`; Satz jeweils einmal, mit dem gewaehlten Namen vorn: `Sorceries is not counted for this Nightfarer: ...`, `Bestial is not counted ...`, `Fire is not counted ...` |
| Wahl bleibt beim Richtungswechsel | bleibt stehen | `Fire` gewaehlt -> `goal_box` auf `Minimise damage taken` (Paar unsichtbar, `Damage type`-Label 0 Treffer) -> zurueck auf `Maximise damage`: Box steht wieder auf `Fire` |
| Wahl faellt beim Neustart auf `All` | `All` | Prozess beendet, neu gestartet: `goal_box` `Maximise damage`, `damage_type_box` **`All`**. In `HKCU\Software\DankYeeterT-322e\NightreignHelper` existiert kein Schluessel fuer die Schadensart |
| Box waehrend der Rechnung bedienbar (AK-08) | bedienbar | Waehrend `Working out maximise damage.` (Knopf `Cancel`): `IsEnabled` von `damage_type_box` und `goal_box` = `True`; das Popup laesst sich mitten im Lauf oeffnen und ein Eintrag waehlen. Die Wahl bricht den Lauf ab und die Zeile geht auf 4.7 (`Your build changed while this was working out - use Optimize again.`), bei stehendem Ergebnis auf 4.1 (`Nothing suggested yet.`) - AK-330 in beiden Richtungen |
| Why-Zeile genau einmal, auch bei Deep-Gefaess | einmal | Revenant, `Deep of Night` an, sechs Slots gefuellt (`Slot 1..6`), `Magic`: AK-331-Satz **1x** im `Why`-Dialog |
| Fenster 1536 px, Option B | Knoepfe bleiben, Boxen kuerzen | Bei 1536 px logischer Breite (1920 px physisch bei 125 %) und allen fuenf Knoepfen: `Filters`, `Optimize`, `Apply all`, `Why`, `Clear` vollstaendig beschriftet und klickbar (je 87 px physisch); `goal_box` gekuerzt auf `Maximis`, `damage_type_box` zeigt `Holy` voll, Statuszeile auf 33 px gedrueckt. Bildnachweis `out/bar1536.png`. Kein Steuerelement verlaesst die Leiste |

Zusaetzlich geprueft, ohne Befund:

- **AK-328** am Artefakt: `damage_type_box` traegt 24 benannte Eintraege und
  2 Trennlinien - `All` | Trenner | `Physical Magic Fire Lightning Holy` |
  Trenner | `Skill attack Sorceries Incantations` + 15 Schulen alphabetisch
  (`Bestial` ... `Thorn`). Reihenfolge und Schreibweise wortgleich zur
  Vorgabe; der Spec-Pruefweg nennt zehn Eintraege, weil er einen Datensatz
  mit genau einer Schule annimmt (DR-036-Erratum), der ausgelieferte
  Datensatz fuehrt 15.
- **AK-327**: Das Paar sitzt zwischen `goal_box` (endet x 876) und `Filters`
  (beginnt x 1158), gleiche Zeile; bei `Minimise damage taken` sind Label
  und Box ausgeblendet (`Damage type`-Treffer 0), nicht nur ausgegraut.
- **Oeffnungsbreite** 1608 px logisch (2010 px physisch), wie AK-334 sie
  nennt.
- Zielgerichtete Testdateien am Quellstand `41173d9`:
  `pytest tests/test_advisor_goals.py tests/test_relic_picker_advisor.py
  tests/test_advisor_bar.py tests/test_damage_art.py -q` -> **224 passed in
  108,68 s**, keine Fehlschlaege.

---

## Befunde

### [P3 | Minor | Mittel] Die Kopfzeile des Pickers nennt die gewaehlte Schadensart nicht

**Adressat:** ui-ux-designer
**Betroffen:** `nrplanner/relicpicker.py:339-342` (`nothing_raises`),
aufgerufen in `_say_what_they_are_worth` (Z. 1840)
**Umgebung:** Artefakt 1.16.0; Wylder, Startwaffe `Wylder's Greatsword`
(kein Feueranteil); `Damage type: Fire`; Picker `Slot 2 - Blue`,
`Sort by: Maximise damage`

**Reproduktion:**
1. Programm starten, Wylder, `Maximise damage`.
2. `Damage type` auf `Fire`.
3. Einen leeren Relikt-Slot oeffnen, Suchfeld leeren, `Sort by` auf
   `Maximise damage`.

**Erwartet:** Der Satz nennt die Einschraenkung, unter der er gilt - so wie
die Wertzeile daneben es seit AK-336 tut (`Damage (Fire)`), etwa
"Nothing you own raises fire damage in this slot."
**Tatsaechlich:** `Nothing you own raises damage in this slot.` - waehrend
jede Karte darunter `Damage (Fire)` beschriftet und Zeile 4 den
AK-331-Satz mit `fire` traegt.

**Analyse:** `nothing_raises(goal_id)` baut den Satz aus `DIRECTION_NOUNS`
allein; `_named_for_choice`, das genau fuer diesen Zweck in T-322f
entstanden ist, wird fuer Wertzeile und Chip benutzt, fuer die Kopfzeile
nicht. AK-336 zaehlt zwei Mindestanforderungen auf (Zeile 4,
Wertzeile/Chip) und nennt die Kopfzeile nicht - die Luecke ist also
vermutlich kein Bau-, sondern ein Spec-Loch derselben Familie wie DR-035.

**Auswirkung:** Woertlich gelesen ist der Satz falsch: unter `All` heben
sehr wohl Relikte den Schaden. Der Leser braucht Zeile 4 daneben, um ihn
richtig zu verstehen. Geringe Auswirkung, weil dieser erklaerende Satz seit
AK-336 garantiert danebensteht.

**Vorschlag:** Denselben Helfer auf die Kopfzeile anwenden und AK-336 um
einen dritten Punkt ergaenzen; die Formulierung gehoert dem App Designer.

---

### [P3 | Major | Mittel] Leiste und Picker widersprechen sich, wenn die Startwaffe die gewaehlte Schadensart gar nicht traegt

**Adressat:** director (Entscheid), danach ui-ux-designer
**Betroffen:** `nrplanner/advisor/goals.py:420-432` (`_max_damage`,
`_TYPE_CHOICE`-Zweig, `value = now.final_per_type.get(key, 0.0)`) gegen
`nrplanner/relicpicker.py:1840` (`nothing_raises`)
**Umgebung:** Artefakt 1.16.0; Wylder (Greatsword, rein physisch), Build
Slot 1 `Delicate Drizzly Scene`, Slot 2 `The Will of the Balancers`,
Slot 3 leer; `Damage type: Fire`

**Reproduktion:**
1. Wylder, `Maximise damage`, `Damage type` auf `Fire`.
2. Einen leeren Slot oeffnen, Suchfeld leeren: Kopfzeile
   `Nothing you own raises damage in this slot.`, jede Karte
   `Damage (Fire) no change`, kein `BEST FOR DAMAGE`-Chip. Picker schliessen.
3. `Optimize`.

**Erwartet:** Beide Bildschirme beantworten dieselbe Frage gleich - wenn
kein Relikt die gewaehlte Art erhoeht, sagt das auch die Leiste, statt drei
Slots als Empfehlung fuer genau diese Frage zu markieren.
**Tatsaechlich:** Die Leiste antwortet `Maximise damage - 3 of 3 slots
filled.` und setzt auf alle drei Slotkarten `SUGGESTED - MAXIMISE DAMAGE`,
obwohl im selben Build und mit derselben Wahl kein Kandidat den Wert bewegt
(0,00 fuer alle).

**Analyse (zwei Lesarten, neutral):** (a) **Absicht** - der Kommentar in
`_max_damage` haelt ausdruecklich fest, ein Typ ohne Vorkommen ranke bei
0,00 und das sei "a ranking and not a fault"; AK-332, das fuer genau diesen
Fall einen eigenen Satz und Zustand 4.10 vorgesehen hatte, ist bewusst
entfallen. Dann ist das Verhalten gewollt und der Picker nur "ehrlicher".
(b) **Luecke** - beim Streichen von AK-332 war der `nothing_raises`-Satz des
Pickers nicht in der Betrachtung; seit A25 ist der Nullfall kein Randfall
mehr, sondern die Regel fuer vier der fuenf Typen bei den meisten
Nightfarern, und die Leiste ist der Ort, an dem die meisten Spieler die
Antwort lesen. Ich entscheide das nicht.

**Priorisierung:** Severity Major (die Empfehlung ist inhaltlich leer und
wird als Empfehlung praesentiert), Likelihood Mittel; trotzdem **P3**, weil
die Nullrangfolge eine dokumentierte Entscheidung ist und nur ihre
Offenlegung strittig - neu an diesem Befund ist allein der Widerspruch
zwischen den beiden Bildschirmen.

**Auswirkung:** Ein Spieler, der `Fire` waehlt und `Apply all` drueckt,
tauscht Relikte gegen Relikte, die fuer seine Frage nichts bringen. Der
Umweg ueber den Picker, der es sagt, existiert, aber niemand geht ihn, wenn
die Leiste eine Empfehlung anzeigt.

**Vorschlag:** Entweder einen Satz der Leiste fuer den Nullfall (Richtung
des gestrichenen AK-332, aber ohne eigenen Zustand), oder einen
ausdruecklichen Vermerk in Spec und Anleitung, dass eine Wahl ohne
Vorkommen bewusst eine Nullrangfolge liefert.

---

## Beobachtungen (kein Befund, keine Nummer)

- Unterhalb der 1536-px-Grenze (gemessen bei 1366 px logisch) wird auch das
  Label `Damage type` auf `Damage t` gekuerzt; die Knoepfe bleiben voll
  beschriftet. AK-271 erlaubt unterhalb 1536 px Kuerzungen, Option B nennt
  die Boxen - das Label steht in keiner der beiden Listen.
- Bei der Oeffnungsbreite (1608 px logisch) und sichtbarem `Why`/`Apply
  all`/`Clear` steht in `goal_box` bereits `Maximise d` statt
  `Maximise damage`; das ist die gemessene Folge von Option B (ungekuerzt
  erst ab 1676 px, `UI_SPEC_REGISTER.md` AK-05/AK-334) und keine Abweichung.
- Der Fliesstext von AK-271 in `UI_SPEC.md` sagt weiterhin, ab 1536 px sei
  die Zielwahl-Box "nie abgeschnitten"; die geltende Fassung steht seit
  19.09. in `UI_SPEC_REGISTER.md` (Option B). Registerfuehrung korrekt,
  Fliesstext veraltet.
- Der Suchbegriff des Pickers wird nur beim **Auswaehlen** eines Relikts
  gemerkt (`app._set_search`, aufgerufen aus `RelicPicker._pick`); wer das
  Feld leert und ohne Auswahl schliesst, findet beim naechsten Oeffnen den
  alten Begriff wieder ("0 of 53 relics matching ..."). Vorbestehend,
  ausserhalb A25.
- DR-037 (der Katalysatorsatz liest sich bei einer Schulwahl, die zur Klasse
  des Katalysators passt, widerspruechlich) ist am Artefakt wortgleich
  reproduzierbar - bereits als Nice-to-have im Design-Review gefuehrt, hier
  nicht neu gemeldet.

## Explorationsprotokoll

Gefahren und gehalten: AK-335 im positiven Zweig (Artwahl mit wirksamem
`art_rate`); AK-336 mit `Sort by` auf `Name`, `Minimise damage taken` und
`Maximise damage`; AK-330 ueber Richtungswechsel, Heldenwechsel und Abbruch
mitten im Lauf; AK-08 mit geoeffnetem Popup waehrend der Rechnung;
Deep-Gefaess mit sechs Slots; Katalysator mit Typ- **und** Artwahl;
Neustart; zwei Fensterbreiten unterhalb der Oeffnungsbreite;
Effektfilter-Favourit gesetzt und wieder entfernt (Registry vorher/nachher
`[]`); der 54-Karten-Pool viermal vollstaendig ausgelesen und gegeneinander
verglichen. Kein Absturz, kein haengender Zustand, keine verwaiste
Registry-Spur.

## Offene Fragen

- An den **director**: gilt die Nullrangfolge bei einer Schadensart ohne
  Vorkommen als vollstaendig beantwortet (AK-332 entfallen), oder braucht
  die Leiste den Satz, den der Picker schon hat? (QA-290)
- An den **ui-ux-designer**: soll AK-336 einen dritten Punkt fuer die
  Kopfzeile des Pickers bekommen? (QA-289)

## Nicht getestet

- **Tooltip AK-329** am Fenster. Qt-Tooltips brauchen ein Vordergrundfenster
  und echte Mausbewegung (T-276); der Wortlaut ist in T-322d gegen den Code
  und in `tests/test_advisor_bar.py` abgesichert - ein vierter Fensterlauf
  war dafuer nicht verhaeltnismaessig.
- **Tastatur AK-333** (Tab-Reihenfolge, Pfeiltasten, Fokusring). Nicht im
  Auftragsumfang; in T-322d sichtbarkeitsbasiert im Code bestaetigt.
- **Volle Testsuite** `pytest -n auto`. Der Auftrag begrenzt den Umfang auf
  das Artefakt; T-321d nennt 1827 passed / 9 skipped, ich habe die vier
  einschlaegigen Dateien selbst laufen lassen (224 passed).
- **Negativer AK-335-Zweig am Fenster** (Artwahl ohne wirksamen `art_rate`,
  Kopfzahl bleibt `Attack rating`): geprueft ist er durch
  `tests/test_advisor_goals.py` Z. 515 (gruen), nicht von mir am Artefakt.
- **Andere Nightfarer als Wylder, Revenant, Recluse.**

## Zusammenfassung (an director)

- P1: 0 - P2: 0 - **P3: 2** (QA-289, QA-290) - P4: 0
- **Gesamturteil: CONCERNS.** Das Abnahmekriterium A25 ist in allen vier
  Teilsaetzen am Artefakt 1.16.0 belegt, DR-034 und DR-035 sind behoben, und
  keine der Kanten aus T-321b/c ist gebrochen. Offen bleiben zwei
  Offenlegungsfragen zum Fall "gewaehlte Art kommt in der Startwaffe nicht
  vor" - keine davon macht eine Zahl falsch, beide sollten vor dem Release
  entschieden werden. Die Entscheidung liegt beim `director`.

## QA-Log - an `qa/findings.md` anhaengen

| QA-289 | **T-322e (20.09.2026, qa-engineer, Artefakt 1.16.0, SHA-256 804F9E2B...25E6C): Picker-Kopfzeile nennt die gewaehlte Schadensart nicht** -- bei `Damage type: Fire` (Wylder, Startwaffe ohne Feueranteil) steht ueber dem Raster `Nothing you own raises damage in this slot.`, waehrend jede Karte darunter seit AK-336 `Damage (Fire)` beschriftet und Zeile 4 den AK-331-Satz mit `fire` traegt. `relicpicker.nothing_raises` baut den Satz aus `DIRECTION_NOUNS` allein und benutzt `_named_for_choice` nicht; AK-336 nennt nur Zeile 4 und Wertzeile/Chip, die Kopfzeile fehlt in der Vorgabe | P3 | Minor | ui-ux-designer | ja - am Artefakt, Picker Slot 2 Blue, Sort by Maximise damage | offen | 2026-09-20 |
| QA-290 | **T-322e (20.09.2026, qa-engineer, Artefakt 1.16.0): Leiste und Picker widersprechen sich bei einer Schadensart ohne Vorkommen** -- Wylder mit `Fire`: der Picker sagt fuer denselben Slot und denselben Build `Nothing you own raises damage in this slot.` (jede Karte `Damage (Fire) no change`, kein `BEST FOR DAMAGE`-Chip), die Leiste antwortet nach `Optimize` `Maximise damage - 3 of 3 slots filled.` und markiert alle drei Slots `SUGGESTED - MAXIMISE DAMAGE`, obwohl kein Kandidat den Wert bewegt. Zwei Lesarten: Absicht (Nullrangfolge dokumentiert, AK-332 entfallen) oder Luecke (beim Streichen von AK-332 war der `nothing_raises`-Satz nicht betrachtet). Kein falscher Zahlenwert; Entscheid beim director. Severity Major, Einstufung P3 wegen der dokumentierten Entscheidung | P3 | Major | director / ui-ux-designer | ja - am Artefakt, beide Bildschirme im selben Build | offen | 2026-09-20 |
| QA-289 | **Retest T-322i (20.09.2026, qa-engineer, Artefakt 1.16.0, SHA-256 51F69498...E8BFC9): behoben** -- Picker-Kopfzeile liest jetzt `Nothing you own raises damage in this slot. (Fire)`, Fix `10442b2` wendet `_named_for_choice` auch auf `nothing_raises` an. Regressionstest `test_nothing_raises_names_the_chosen_kind` gruen, `test_relic_picker_advisor.py` in der Sammelsuite | P3 | Minor | ui-ux-designer | ja - am Artefakt, Slot 1 Blue, Wylder Fire | behoben -- am Artefakt bestaetigt | 2026-09-20 |
| QA-290 | **Retest T-322i (20.09.2026, qa-engineer, Artefakt 1.16.0, SHA-256 51F69498...E8BFC9): behoben** -- Leiste faellt jetzt auf `Maximise damage - 0 of 3 slots filled … 3 slots have nothing to choose from.` zurueck, keine `SUGGESTED`-Chips mehr; Fix `5b9fad9` verwirft die beste Zusammenstellung in `run.run()`, wenn ihr Wert unter Art-/Typwahl exakt dem Grundzustand entspricht. Regressionstest `test_a_chosen_type_the_build_carries_none_of_earns_no_suggestion` gruen | P3 | Major | director / ui-ux-designer | ja - am Artefakt, gleicher Slot/Build wie QA-290 | behoben -- am Artefakt bestaetigt | 2026-09-20 |

---

STATUS: erledigt
AUFTRAG: T-322i - Retest QA-289/QA-290 am neuen Artefakt 1.16.0
(`dist\NightreignHelper.exe`, 59.233.161 B, SHA-256
51F69498...E8BFC9, Bau T-322h `69fb2bf` auf Code `5b9fad9`; Fixes
`10442b2`, `5b9fad9`)
GELESEN: docs/tasks/T-322.md (Abschnitt T-322i); docs/berichte/
T-322-qa-engineer.md (eigener Abschnitt T-322e, Pruefwege QA-289/QA-290);
`git show 10442b2`, `git show 5b9fad9` (Diff + Tests); qa/findings.md
(Kopf + Ende)
GEAENDERT: nichts im Arbeitsbaum ausser diesem Bericht (Abschnitt T-322i
angehaengt). Kein Eintrag in `qa/findings.md` durch mich - die zwei
Retest-Zeilen stehen oben im QA-Log zum Anhaengen. Scratchpad:
`<Scratchpad>/T-322i/` (eigenes LOCALAPPDATA/APPDATA, Testabzug 841
Dateien / 21.131.645 B hineinkopiert; Registry-Testschluessel
`HKCU\Software\DankYeeterT-322i` nach dem Lauf wieder entfernt)
ANNAHMEN: keine
NAECHSTER: director (Freigabe A25/1.16.0), release-manager (falls
Freigabe erteilt)
BLOCKIERT DURCH: nichts

---

# T-322i - qa-engineer: Retest QA-289/QA-290 am Artefakt 1.16.0

## Umgebung und Nachweis der Umlenkung

- Artefakt gegengeprueft: `Get-FileHash` 20.09.2026 ->
  `51F694986D11CA1DED16B6170D552C89579C0E5C67192D78F68FFFF063E8BFC9`,
  Laenge `59233161` - deckungsgleich mit dem Auftrag.
- `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-322i`, `LOCALAPPDATA` und `APPDATA`
  auf frische Scratchpad-Ordner; Testabzug hineinkopiert (nachgezaehlt:
  841 Dateien, 21.131.645 Bytes). Positiver Beleg der Umlenkung: nach dem
  Lauf `builds\1|6` und `chalices\1|6` unter
  `HKCU\Software\DankYeeterT-322i\NightreignHelper`; der Schluessel wurde
  danach geloescht (eigenes Testverzeichnis, folgenlos). Der Spielstand
  wurde nur gelesen, nie geschrieben.
- NH-004: `Get-Process NightreignHelper` vor dem Start 0; ein Fensterlauf,
  niemand parallel; nach `Stop-Process -Force` erneut 0 Prozesse.
- Fenstertreiber ausschliesslich `scripts/drive_window.ps1`
  (dot-gesourct). Neue Werkzeuggrenze, kein Befund: die Relikt-Slots
  reagieren auf Doppelklick der Kopfzeile nicht zuverlaessig genug fuer
  UIA-Timing (zwei `ClickAt`-Aufrufe liegen mit den eingebauten Pausen
  weit ueber der Windows-Doppelklickzeit); der Knopf `Empty slot` unter
  jedem Slot oeffnet den Picker mit einem einzigen Klick zuverlaessig.

## Retest QA-289 - Picker-Kopfzeile nennt die gewaehlte Schadensart

**Reproduktion (wie im Ursprungsbefund):** Wylder, `Maximise damage`,
`Damage type` auf `Fire`, Slot 1 (`Empty slot`) geoeffnet.

**Ergebnis:** Kopfzeile liest `Nothing you own raises damage in this
slot. (Fire)` - jede der 54 Karten weiterhin `Damage (Fire) no change`,
Zeile 4 traegt weiterhin den AK-331-Satz mit `fire`. Der Satz nennt die
Einschraenkung jetzt wie Wertzeile und Chip.

**Urteil: behoben.** Fix `10442b2` wendet `_named_for_choice` auf
`nothing_raises` an; der Regressionstest
`test_nothing_raises_names_the_chosen_kind` deckt genau diesen Fall ab
und ist gruen.

## Retest QA-290 - Leiste und Picker widersprechen sich

**Reproduktion (wie im Ursprungsbefund):** Wylder, `Maximise damage`,
`Damage type` auf `Fire`, leerer Build (keine Relikte gehalten),
`Optimize` geklickt.

**Ergebnis:** Statuszeile liest `Maximise damage - 0 of 3 slots filled
… 3 slots have nothing to choose from.` - kein `SUGGESTED`-Chip auf
irgendeinem Slot, keine Fuellung der drei freien Slots. Der Picker fuer
Slot 1 sagt fuer denselben Build weiterhin `Nothing you own raises
damage in this slot. (Fire)`. Beide Bildschirme antworten jetzt gleich.

**Urteil: behoben.** Fix `5b9fad9` verwirft in `run.run()` die beste
Zusammenstellung, wenn ihr Wert unter einer Art-/Typwahl exakt dem
Grundzustand entspricht, und faellt auf den bestehenden
"nothing to choose from"-Zustand zurueck (UI_SPEC 4.11); der
Regressionstest `test_a_chosen_type_the_build_carries_none_of_earns_no_suggestion`
ist gruen. Die Director-Entscheidung selbst (Nullrangfolge unter `All`
bleibt eine Rangfolge, nur unter Art-/Typwahl wird sie verworfen) ist im
Commit dokumentiert und wird hier nicht neu bewertet.

## Stichprobe Revenant/Magic (unveraendert)

Revenant, `Maximise damage`, `Damage type` auf `Magic`, Slot 1
(`Empty slot`) geoeffnet, `Sort by: Maximise damage`: Spitzenkarte
weiterhin `Delicate Drizzly Scene`, `Damage (Magic) +19.8 AR`, Chip
jetzt `BEST FOR DAMAGE (Magic)` (AK-336-Muster, seit T-322f unveraendert
gegenueber dem T-322e-Nachweis). Kein neuer Befund; die Zahl deckt sich
mit dem in T-322e gemessenen Wert.

## Regression im unmittelbaren Umfeld

`pytest tests/test_relic_picker_advisor.py tests/test_advisor_run.py
tests/test_advisor_goals.py tests/test_advisor_bar.py -q` ->
**269 passed in 180,84 s**, keine Fehlschlaege.

## Explorationsprotokoll

Beide Befunde am Fenster reproduziert (nicht nur an der Testsuite
geglaubt): QA-289 mit derselben Nightfarer-/Waffen-/Wahlkombination wie
im Ursprungsbefund (Wylder, Fire, leerer Slot); QA-290 mit derselben
Kombination, Statuszeile und Slot-Chips vor und nach `Optimize`
gegengeprueft. Zusaetzlich Revenant/Magic als Stichprobe gegen
Regressionen in der Ranglogik, mit der konkreten Zahl aus T-322e
verglichen statt nur "sieht plausibel aus". Vier einschlaegige Testdateien
selbst laufen lassen. Kein Absturz, keine Registry-Spur nach dem Lauf.

## Nicht getestet

- Kein voller Fensterlauf der uebrigen A25-Kanten aus T-322e (Recluse,
  Richtungswechsel, Neustart, AK-08, Deep-Gefaess, Fensterbreiten) - der
  Auftrag begrenzt den Retest auf QA-289/QA-290 plus die genannte
  Stichprobe; T-322e bleibt fuer diese Kanten der Nachweis auf demselben
  Codestand (die Fixes `10442b2`/`5b9fad9` aendern nur `relicpicker.py`
  und `run.py`, beide ausserhalb dieser Kanten).
- Volle Testsuite `pytest -n auto`. Vier gezielte Dateien um die
  geaenderten Module gruen; kein Hinweis auf breitere Auswirkung, die
  einen vollen Lauf rechtfertigt.
- Bestaetigung, dass die Director-Entscheidung zu QA-290 (Nullrangfolge
  unter `All` bleibt unveraendert) selbst richtig ist - das ist keine
  Testfrage, sie ist im Commit `5b9fad9` dokumentiert und war Gegenstand
  des Auftrags T-322g, nicht dieses Retests.

## Zusammenfassung (an director)

- QA-289: **PASS** (behoben, am Artefakt bestaetigt)
- QA-290: **PASS** (behoben, am Artefakt bestaetigt)
- P1: 0 - P2: 0 - P3: 0 - P4: 0 - keine neuen Befunde
- **Gesamturteil: PASS.** Beide vom director am 20.09. zum Fixen
  bestimmten Befunde sind am neuen Artefakt 1.16.0 (Bau T-322h) behoben,
  die Stichprobe Revenant/Magic zeigt keine Regression, die vier
  einschlaegigen Testdateien sind gruen (269 passed). Aus QA-Sicht steht
  der Freigabe von 1.16.0 nichts entgegen.

## QA-Log - an `qa/findings.md` anhaengen

Siehe die vier Zeilen weiter oben im bestehenden QA-Log-Abschnitt (zwei
Ursprungszeilen QA-289/QA-290 aus T-322e bleiben stehen, zwei neue
Retest-Zeilen T-322i wurden direkt danach eingefuegt statt an das
Dateiende, damit beide Befunde gemeinsam lesbar bleiben).

---

STATUS: erledigt
AUFTRAG: T-322p - Retest AK-330-Nachtrag (Schadensart-Persistenz und
Why-Klarstellung) am Artefakt 1.16.0 (`dist\NightreignHelper.exe`,
59.233.451 B, SHA-256 FE7DB4B9...61CDED2, Bau T-322o `21e0f92` auf Code
`9f95de0`)
GELESEN: docs/tasks/T-322.md (Abschnitt T-322n); `git show 9f95de0`
(Diff + Tests `test_advisor_bar.py`, `test_advisor_goals.py`);
docs/berichte/T-322-power-user.md (Punkt 1 und 3, Einordnung Director
20.09.); nrplanner/advisorbar.py (`DAMAGE_ART_KEY`, `_settings`,
`_show_the_damage_types`, `_damage_type_chosen`); nrplanner/advisor/goals.py
(`_RANKED_ON_ONE_ART`); scripts/drive_window.ps1
GEAENDERT: nichts im Arbeitsbaum ausser diesem Bericht (Abschnitt T-322p
angehaengt). Kein Eintrag in `qa/findings.md` - kein Befund, Register bleibt
unveraendert. Scratchpad/Testordner
`C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-T322p\` (eigenes
LOCALAPPDATA/APPDATA, Testabzug 842 Eintraege hineinkopiert, nach dem Lauf
geloescht); Registry-Zweig `HKCU\Software\DankYeeterT-322p` nach dem Lauf
geloescht
ANNAHMEN: keine
NAECHSTER: director (Freigabe 1.16.0)
BLOCKIERT DURCH: nichts

---

# T-322p - qa-engineer: Retest AK-330-Nachtrag am Artefakt 1.16.0

## Umgebung und Nachweis der Umlenkung

- Artefakt gegengeprueft: `Get-FileHash` ->
  `FE7DB4B966FC9FA39100CBC6016BC330733A0905DCE763B6ADF51240761CDED2`,
  Laenge `59233451` - deckungsgleich mit dem Auftrag.
- `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-322p`, `LOCALAPPDATA`/`APPDATA` auf
  einen frischen Ordner ausserhalb des Projektbaums und ausserhalb
  `%LOCALAPPDATA%`; Testabzug hineinkopiert. Vor dem ersten Start existierte
  `HKCU\Software\DankYeeterT-322p` nicht (`Test-Path` false) - sauberer
  Ausgangspunkt. Positiver Beleg der Umlenkung: nach dem ersten Lauf trug
  derselbe Schluessel `damage_art`. Der Spielstand wurde nicht angefasst.
- NH-004: kein anderer Lauf parallel; vier Programmstarts, jeweils per
  `WindowPattern.Close()` sauber beendet, `Get-Process` dazwischen und am
  Ende 0. Registry-Zweig `HKCU\Software\DankYeeterT-322p` nach dem letzten
  Lauf geloescht.
- Fenstertreiber ausschliesslich `scripts/drive_window.ps1` (dot-gesourct),
  unveraendert gegenueber T-322e/i.

## Pruefweg (a) - Schadensart und Schulwahl ueberleben den Neustart

1. Wylder (Standardcharakter), `damage_type_box` auf `Fire` gestellt ->
   Registry sofort `damage_art = type:Fire`. Fenster sauber geschlossen
   (0 Prozesse), neu gestartet: `damage_type_box` steht auf `Fire`.
2. Auf Revenant gewechselt, `damage_type_box` auf `Bestial` (Schulwahl)
   gestellt -> Registry `damage_art = art:family:23`. Fenster sauber
   geschlossen, neu gestartet: `damage_type_box` steht auf `Bestial`
   (die Artliste ist datensatzweit, nicht nightfarerabhaengig -
   `model.attack_arts` liest ueber alle Effekte, nicht ueber den aktiven
   Charakter; die Nightfarer-Wahl selbst faellt beim Neustart wie bisher
   auf Wylder zurueck, das ist ausserhalb dieses Nachtrags).
**PASS** fuer beide Haelften.

## Pruefweg (b) - gemerkter Schluessel, den die Box nicht kennt

Bei geschlossenem Programm `damage_art` von Hand auf `art:family:999`
gesetzt (kein Eintrag der aktuellen Box). Neustart: `damage_type_box`
steht auf `All`, `Get-Process` liefert die erwarteten zwei Prozesse
(Bootloader + App, normales Bild bei der Einzeldatei), kein Absturz, keine
Fehlermeldung. **PASS** - die Validierung gegen `findData` haelt am
Artefakt.

## Pruefweg (c) - Why-Zeile unter Incantations und unter Fire

Unter `Incantations` (Wylder) `Optimize` gelaufen, `Why`-Dialog eines
gefuellten Slots gelesen: Zeile 4 genau einmal
"Ranked on incantations damage only - every other effect on a candidate
still shows, but only this counts toward the ranking. It scales the
armament's attack rating - spell damage itself is not in the game data."
- erster Satz unveraendert, zweiter Satz wie im Diff angefuegt. Unter
`Fire` (derselbe Build, 0 Vorschlaege) derselbe Aufbau, wortgleich bis auf
"fire" statt "incantations", ebenfalls genau einmal. **PASS.**

## Pruefweg (d) - Stichprobe QA-289/QA-290 unveraendert

Wylder, `Fire`, `Maximise damage`: Leiste "0 of 3 slots filled - 3 slots
have nothing to choose from." Picker Slot 1 (Blue, 54 von 54): Kopfzeile
"Nothing you own raises damage in this slot. (Fire)", Zeile 4 traegt den
AK-331-Satz samt Nachtrag. Beide Fixes aus T-322h/i halten unveraendert am
neuen Artefakt. **PASS.**

## Regression

`pytest tests/test_advisor_bar.py tests/test_advisor_goals.py -q`:
136 passed in 65,4 s (kein `-n auto` bei Einzeldateien, CLAUDE.md). Kein
Hinweis auf breitere Auswirkung; die volle Suite war fuer diesen Retest
nicht angezeigt (Aenderung beschraenkt auf `advisorbar.py`/`goals.py`,
Fixes T-322n greifen nur in die zwei genannten Dateien plus deren Tests).

## Zusammenfassung (an director)

- Pruefweg (a): PASS - Pruefweg (b): PASS - Pruefweg (c): PASS -
  Pruefweg (d): PASS
- P1: 0 - P2: 0 - P3: 0 - P4: 0 - keine neuen Befunde
- **Gesamturteil: PASS.** AK-330-Nachtrag (Persistenz der Schadensart samt
  Validierung gegen einen unbekannten Schluessel) und die Why-Klarstellung
  aus T-322n halten am Artefakt 1.16.0 (Bau T-322o); die Stichprobe
  QA-289/QA-290 zeigt keine Regression. Aus QA-Sicht steht der Freigabe
  von 1.16.0 nichts entgegen.

## Explorationsprotokoll

Vier Programmstarts (Fire setzen, Neustart pruefen; Bestial setzen,
Neustart pruefen; ungueltigen Schluessel von Hand setzen, Neustart pruefen;
Incantations/Fire Why-Dialog) plus Picker-Stichprobe im letzten Lauf, alle
am selben Artefakt. Alle vier Pruefwege reproduziert, keiner schlug fehl.

## Offene Fragen

Keine.

## Nicht getestet

- Parallelzugriff zweier Instanzen auf denselben Registry-Schluessel
  (NH-004 schliesst zwei gleichzeitige Laeufe ohnehin aus - kein Pfad, auf
  dem ein Nutzer das erreicht).
- Alle Kanten aus T-321b/c ausserhalb der vier genannten Pruefwege
  (Katalysator, Richtungswechsel, AK-08, Deep-Gefaess, Fensterbreiten) -
  der Auftrag begrenzt den Retest auf T-322n; diese Kanten aendert der
  Fix nicht (er beruehrt nur den Konstruktor- und den Auswahlpfad der
  Box, nicht die Rechnung selbst).
- Nightfarer-Wahl selbst als Persistenzkandidat - ausserhalb des Auftrags,
  in Pruefweg (a) nur als Randbeobachtung notiert (kein Befund: unveraendert
  gegenueber dem Bestand vor T-322n).

## QA-Log - an `qa/findings.md` anhaengen

Keine neue Zeile - dieser Retest fand keinen Befund.
