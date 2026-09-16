# T-244 -- Relic picker: findet die Effektsuche jeden Treffer? (qa-engineer)

Datum 14.09.2026, Quellstand `4a063bf` (Auftrag genannt `7cac47e`/`b80b446`;
dazwischen T-243 `70bbe3d`, nur Kartenbreite -- `git diff b80b446..HEAD` auf
`relicpicker.py`/`search.py`/`relicslots.py` beruehrt `_candidates`,
`search.parse`, `effect_names` an 0 Zeilen). Arbeitsbaum sauber, keine
Projektdatei ausser diesem Bericht und `qa/findings.md` geaendert.

## Suchpfad (was verglichen wird, wie)

`RelicPicker._candidates()` (`nrplanner/relicpicker.py:1292`):
`search.parse(self.search.text())` liefert ein Praedikat, das je Kopie auf
`slot.effect_names(item)` angewendet wird -- das sind **nur die
Anzeigenamen der `effect_ids`** (`relicslots.py:556`). Nicht durchsucht:
Fluchnamen (`curse_ids`, obwohl die Karte sie als `✦ ...` zeigt),
Reliktname, Beschreibungstext.

`nrplanner/search.py`: Tokenisierung an Whitespace (`"..."` haelt eine
Phrase zusammen), alles `lower()`, Vergleich als **Teilstring** gegen den
Blob `" ".join(effect_names).lower()` -- also ueber alle Effekte der Karte
hinweg, ohne Wortgrenzen. Leerzeichen = AND, Woerter `and/&/&&/+` = AND,
`or/|/||` = OR, `not/-/!` = NOT, fuehrendes `-` an einem Token = NOT dieses
Tokens. Bindestrich/Apostroph/Klammern/`+5` innerhalb eines Tokens sind
Literale. Besteht die Eingabe nur aus Operatoren, ist das Praedikat `None`
und alles wird gezeigt.

## Bodenwahrheit

Spielstand `...\76561198179244962\NR0000.sl2`, **nur gelesen**. Das Spiel
lief waehrend des Auftrags (`nightreign.exe` PID 28120), die Datei wurde
19:20:52, 19:42:28 und 19:43:11 geschrieben; die erste Zaehlung ergab 334
Kopien, das Fenster sechs Minuten spaeter 315. Deshalb eingefroren: Kopie
im Scratchpad, SHA-256 `b52d110e...4bf14` (identisch mit dem Original um
19:43:22), dem Fenster ueber `gamepath.remember_save()` (Schluessel
`paths/save`, Org `DankYeeterT-244`) untergeschoben, `resolve_save()`
zurueckgelesen. Ergebnis: **315 Kopien, 314 unterschiedliche Rolls**
(Auftrag nannte 314); Basis 211 Kopien / 210 Rolls, Deep 104 / 104; 76
Kopien mit Fluch (alle Deep); 298 verschiedene Effektnamen, 24 nur als
Fluch vorkommende Namen; 238 Kopien mit drei Effekten.

Erwartung je Begriff, unabhaengig vom Programm berechnet: Begriff (lower,
Anfuehrungszeichen entfernt) als Teilstring **in einem einzelnen
Effektnamen** einer Kopie; getrennt gezaehlt: Treffer nur im Fluchnamen.
Gezaehlt in unterschiedlichen Rolls, weil der Picker Duplikate zusammenlegt
(`favourites.distinct`, QA-021).

## Weg

Echtes `Planner`-Fenster (`QT_QPA_PLATFORM=offscreen`), Testabzug in das
umgelenkte `LOCALAPPDATA` kopiert (`paths.cache_dir()` zurueckgelesen),
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-244`, `APPDATA` umgelenkt. Weisser
Basis-Slot: Wylder's Chalice Slot 3 (Universum 210 = Bodenwahrheit 210).
Weisser Deep-Slot: Forgotten Wylder's Goblet Deep Slot 3 (104 = 104). Alle
Slots vorher geleert. Je Begriff: `dlg.search.setText()`, Events gepumpt,
`_candidates()` und die `RelicCard`-Kinder gezaehlt (stimmten in allen 120
Faellen ueberein) sowie die Kopfzeile `x of y relics matching` gelesen.
60 Begriffe x 2 Modi; Skripte `<scratchpad>/T-244/probe.py`, `picker.py`,
Rohdaten `result.json`.

## Tabelle (Auszug; erwartet = Rolls mit Begriff in einem Effektnamen)

| Begriff | Modus | erwartet | gezeigt | fehlt | zu viel |
|---|---|---|---|---|---|
| `strength` / `STRENGTH` / `  strength  ` | Basis | 24 | 24 | 0 | 0 |
| `HP` | Basis / Deep | 40 / 34 | 40 / 34 | 0 | 0 |
| `frost`, `vigor`, `holy`, `poison`, `rune`, `FP` | Basis | 12/30/7/12/8/18 | gleich | 0 | 0 |
| `stam`, `negat`, `dext` (Teilwoerter) | Basis | 21/21/19 | gleich | 0 | 0 |
| `damage negation` / `Damage NEGATION` / `"damage negation"` | Basis / Deep | 21 / 40 | 21 / 40 | 0 | 0 |
| `attack power` | Deep | 39 | 41 | 0 | 2 |
| `armament's`, `frostbite-afflicted`, `Two-Handing`, `stance-breaking` | Basis | 18/2/5/8 | gleich | 0 | 0 |
| `+1`, `+3`, `1` | Basis | 35/86/35 | gleich | 0 | 0 |
| `Arcane +3` | Basis | 5 | 10 | 0 | 5 |
| `"Arcane +3"` | Basis | 5 | 5 | 0 | 0 |
| `[Duchess]`, `(greatsword only)`, `Revenant` | Basis | 19/2/13 | gleich | 0 | 0 |
| `Spiked Cracked Tear` (nur Deep), `Poise +3`, `Intelligence +2` (Position 3) | Deep/Basis | 3/1/3 | gleich | 0 | 0 |
| `Reduced Faith` | Basis / Deep | 1 / 1 | 8 / 4 | 0 | 7 / 3 |
| `self and allies` | Basis | 2 | 13 | 0 | 11 |
| **`but not for self`** | Basis / Deep | 4 / 2 | **0 / 0** | **4 / 2** | 0 |
| **`-afflicted`** | Basis / Deep | 4 / 6 | 206 / 98 | **4 / 6** | 206 / 98 |
| `"but not for self"`, `"-afflicted"` | Basis | 4 / 4 | 4 / 4 | 0 | 0 |
| `not`, `and`, `or`, `&`, `-`, `+` (allein) | Basis | 4/67/100/4/19/148 | je 210 | 0 | Rest |
| `All Resistances Down`, `Continuous HP Loss` (nur Fluch) | Deep | 0 Effekt / 3 bzw. 1 Fluch | 0 | 3 / 1 (Fluch) | 0 |
| `strength` | Deep | 8 Effekt + 5 nur Fluch | 8 | 5 (Fluch) | 0 |
| `Lower Attack`, `Reduced Strength` | Deep | 0 / 2 Effekt, 5 / 5 nur Fluch | 0 / 8 | 5 / 5 (Fluch) | 0 / 6 |

Vollstaendige Zeilen fuer alle 60 Begriffe: `<scratchpad>/T-244/result.json`.

**Urteil zur Frage:** Fuer Begriffe, die in einem Effektnamen stehen und
kein Operatorwort enthalten, ist die Suche vollstaendig -- 0 fehlende Rolls
in 54 von 60 Begriffen je Modus. Fehlend sind Treffer genau dann, wenn der
Begriff `not` (oder `-`/`!` als Wort bzw. fuehrendes `-`) enthaelt oder der
Text nur im Fluch steht.

## Befunde

### [P3 | Major | Niedrig] QA-263 -- Begriff mit `not` oder fuehrendem `-` blendet die passenden Relikte aus statt sie zu finden

**Adressat:** director (Spec: Operatorsyntax gewollt, aber ohne Hinweis im
Feld); Umsetzung developer
**Betroffen:** `nrplanner/search.py` (`NOT_WORDS`, `token.startswith("-")`),
`nrplanner/relicpicker.py:1292`
**Umgebung:** eingefrorener Spielstand 315 Kopien, weisser Slot, alle Slots leer

**Reproduktion:**
1. Relic picker eines weissen Basis-Slots oeffnen.
2. `but not for self` tippen (Text von der Karte `Raised stamina recovery for nearby allies, but not for self`).
3. Alternativ `-afflicted` tippen.

**Erwartet:** 4 Rolls (Handles 3229614193, 3229614365, ...) bzw. 4 Rolls mit
`...-afflicted enemy`.
**Tatsaechlich:** `0 of 210 relics matching "but not for self"`; bei
`-afflicted`: 206 gezeigt, genau die 4 passenden fehlen. Mit
Anfuehrungszeichen (`"but not for self"`, `"-afflicted"`) 4 / 4 -- der
Workaround existiert, das Feld (`Filter by effect…`, kein Tooltip) nennt
ihn nicht; README §Searching beschreibt die Syntax.

**Analyse:** `not` wird zum NOT-Operator (`but AND NOT for AND self`; jeder
Treffer enthaelt `for` und faellt), `-afflicted` zu `NOT afflicted`. Kein
Zufall, deterministisch. 2 der 298 Effektnamen enthalten ` not `; das ist
die einzige echte Luecke, die der Auftrag suchen sollte -- ausserhalb der
Operatorwoerter fehlt nichts.

**Auswirkung:** Wer einen Effekttext von der Karte abtippt, der `not`
enthaelt, sieht 0 Treffer und schliesst auf eine unvollstaendige Suche;
beim fuehrenden `-` sieht er 206 falsche.

**Vorschlag:** Entweder Operatoren nur in Grossschreibung (`NOT`, `OR`) und
Kleinschreibung als Literal; oder ein Tooltip/Placeholder mit der Syntax.
Entscheidung director.

---

### [P3 | Minor | Mittel] QA-264 -- Fluchtext steht auf der Karte, wird aber nicht durchsucht

**Adressat:** director (Spec-Frage: Lesart A "Filter by effect" meint nur
Effekte, Fluch ist keiner -- Verhalten korrekt; Lesart B alles, was auf der
Karte steht, ist filterbar, README-Beispiel `poise NOT curse` setzt das
voraus -- Verhalten fehlt)
**Betroffen:** `nrplanner/relicslots.py:556` (`effect_names` ohne
`curse_ids`), `relicpicker.py:1300`

**Reproduktion:** Deep-Modus, weisser Deep-Slot (Forgotten Wylder's Goblet
Deep Slot 3), `All Resistances Down` tippen.
**Erwartet (Lesart B):** 3 Rolls, deren Karte `✦ All Resistances Down`
zeigt. **Tatsaechlich:** `0 of 104`. Ebenso `strength`: 8 gezeigt, 5
weitere Karten mit `✦ Reduced Strength and ...` fehlen (Handles 3229614301,
3229614281, 3229614302, ...). Basis-Modus nicht betroffen (alle 76
Fluchkopien sind Deep).

**Auswirkung:** 76 von 315 Kopien. `poise NOT curse` aus der README
schliesst nichts aus (kein Effektname enthaelt `curse` ausser dem
Executor-Schwert-Effekt); wer Fluechen ausweichen will, kann es ueber die
Suche nicht.

**Vorschlag:** Entscheidung, dann entweder `curse_ids`-Namen in den
Haystack (ggf. mit Praefix, damit `NOT` sie ausschliessen kann) oder
README-Zeile korrigieren.

---

### [P3 | Minor | Hoch] QA-265 -- Mehrwortbegriff ohne Anfuehrungszeichen wird als AND ueber alle Effekte der Karte gelesen; Kopfzeile zaehlt die Ueberschuesse als `matching`

**Adressat:** ui-ux-designer
**Betroffen:** `search.py` (`" ".join(haystacks)`, Leerzeichen = AND),
`relicpicker.py:1497` (Kopfzeile)

**Reproduktion:** weisser Basis-Slot, `Reduced Faith` tippen.
**Erwartet (Spielerlogik):** 1 Roll mit `[Revenant] Improved Strength,
Reduced Faith`. **Tatsaechlich:** `8 of 210 relics matching "Reduced Faith"`
-- 7 Karten enthalten `Reduced` in Effekt 1 und `Faith` in Effekt 3
(`[Undertaker] Improved Mind and Faith, Reduced Strength` + `Faith +3`).
Gleiches Muster: `Arcane +3` 10 statt 5, `self and allies` 13 statt 2,
`Reduced Strength` 6 statt 2. Mit `"..."` jeweils exakt. Nur Operatoren
(`not`, `and`, `or`, `&`, `-`, `+`) ergeben `210 of 210 relics matching
"not"`.

**Analyse:** Dokumentiertes Design (Docstring, README); kein fehlender
Treffer. Befund ist die Kommunikation: Feld ohne Syntaxhinweis, Kopfzeile
nennt Karten `matching "Reduced Faith"`, auf denen die Phrase nicht steht.

**Vorschlag:** Syntaxhinweis am Feld (Tooltip oder Placeholder) und/oder
Kopfzeile, die den geparsten Ausdruck zeigt (`reduced AND faith`). Kein
Redesign-Vorschlag von QA.

## Zusammenfassung (an director)

P1: 0 · P2: 0 · P3: 3 (QA-263, QA-264, QA-265) · P4: 0.
**Urteil: CONCERNS.** Die Suche findet jeden Treffer im Effektnamen (0
fehlende Rolls in 54/60 Begriffen, beide Modi, 314 Rolls); der
Nutzer-Eindruck "findet nicht alle" hat zwei belegte Quellen: Operatorwort
`not`/fuehrendes `-` (QA-263) und Fluchtext (QA-264). Beides ist eine
Spec-Entscheidung, keine Regression.

## Explorationsprotokoll

Gehalten: Gross/Klein, fuehrender/nachlaufender Whitespace, Teilwoerter,
Apostroph, Bindestrich innerhalb des Wortes, `+N`, Ziffer allein,
eckige/runde Klammern, Zwei-Wort-Phrasen in Anfuehrungszeichen, Begriff
nur auf Deep-Relikten, Effekt an Position 3, `Poison & Rot` (`&` als AND
faellt weg, Treffer bleibt, 1 zu viel), Kartenanzahl == `_candidates()`
== Kopfzeile in 120/120 Faellen, Picker-Universum == Bodenwahrheit in beiden
Modi (210/210, 104/104). Bestehende Suite: `tests/test_advisor_search.py`
27 passed (betrifft die Advisor-Beam-Suche, nicht `nrplanner/search.py`);
kein Test importiert `nrplanner.search` (`grep -rn "search.parse\|import
search" tests/` -> 0 Treffer ausser advisor).

## Beobachtungen

`nrplanner/search.py` hat keinen eigenen Test; die Kopfzeile `x of y`
verwendet typografische Anfuehrungszeichen, die im Konsolen-Readback als
`�` erscheinen (kein Programmfehler).

## Offene Fragen

An director: Lesart A oder B fuer QA-264? Sollen Operatorwoerter
case-sensitiv sein (QA-263)?

## Nicht getestet

Roter/blauer/gelber Slot (Farbfilter ist `relics_for`, nicht Suche; weisser
Slot deckt die Obermenge), Weapons-Tab-Suche (gleicher Parser, anderer
Haystack; nicht im Auftrag), Live-Fenster mit `QT_QPA_PLATFORM=windows`
(Filterpfad ist plattformunabhaengig), Tippgeschwindigkeit/Race beim
`textChanged` (jeder Tastendruck baut die Karten neu, kein asynchroner
Pfad in `_candidates`).
