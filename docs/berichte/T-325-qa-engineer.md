# T-325h — qa-engineer, A26 am Artefakt 1.17.0

**STATUS: teilweise** (Zugschwelle 150 Werkzeugaufrufe erreicht, bevor die
Restliste abgearbeitet war). Urteil unten ist vorlaeufig und bezieht sich nur
auf das Geprueefte.

## Kontraktblock

| Feld | Wert |
|---|---|
| Artefakt | `dist\NightreignHelper.exe`, 59 249 345 B |
| SHA-256 | `D136FB2DCAA9F4C44C9D23557F05ED2206C75BBF7D71128EA47F4065BA120101` (nachgerechnet, deckungsgleich mit dem Auftrag) |
| Version im Fenstertitel | `Nightreign Helper 1.17.0` |
| Bau | T-325f `6474474` auf Code `f24376b` |
| Umlenkung | `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-325h`, `LOCALAPPDATA`/`APPDATA`/`USERPROFILE` in den Scratchpad (`...\scratchpad\T-325h\{LOCALAPPDATA,APPDATA,HOME}`) |
| Datensatz | Testabzug v16 **kopiert** (841 Dateien, 21 139 391 B, `meta` v16) in `<LOCALAPPDATA>\NightreignHelper\` |
| Spielstand | eingefrorene Kopie, `sha256 a4ec107c634b6d905ab968e38af2ad751574673f6bdf64984ddc906de59f2312`, unter dem umgelenkten `APPDATA`; Fenster meldet **313 Relikte** (= Zaehlung aus derselben Kopie) |
| Fensterlaeufe | 6 Starts nacheinander, nie zwei zugleich; Instanzsperre hat zweimal korrekt geblockt (QA-256-Verhalten bestaetigt) |
| Suite | **nicht ausgefuehrt** (QA am Artefakt; letzter bekannter Stand `f24376b`: 1877 passed, 9 skipped) |
| Bildnachweis | keiner (PrintWindow-Aufnahme war der naechste Schritt, blieb aus) |

**NH-004-Abschluss NICHT ausgefuehrt** (Sperre): eine Instanz laeuft noch
(gestartet 21:34 aus `dist\`), Fensterbreite steht wieder auf 2448 px physisch;
der Registry-Testzweig `HKCU\Software\DankYeeterT-325h` ist noch da. Beides
muss der naechste Lauf (oder der Nutzer) erledigen:
`...\scratchpad\T-325h\close.ps1` und `reg delete HKCU\Software\DankYeeterT-325h /f`.

## Urteil

**FAIL** (vorlaeufig, Lauf unvollstaendig). Grund ist genau ein Punkt: die
erste Nachweiszeile aus `GOAL.md` A26 ist am Artefakt **nicht woertlich**
belegbar (QA-291). Alle uebrigen geprueften Punkte haben gehalten; kein
Funktionsfehler gefunden. Mindestbedingung: der `director` entscheidet
QA-291 (Wortlaut `GOAL.md` A26 nachziehen — das ist der Weg, den OF-58 fuer
denselben Absatz schon offen haelt — oder Verhalten aendern), danach ist nur
noch die Restliste unter „Nicht getestet" nachzuholen.

## Nachweis A26, Teilsatz fuer Teilsatz

| Teilsatz (GOAL A26) | Ergebnis |
|---|---|
| Revenant *Incantations x All*, **Faith** steigt | **belegt** — Kartenwerte `+9.9` (Faith +2), `+14.8` (Faith +3) |
| Revenant *Incantations x All*, **Improved Incantations** steigt | **nicht belegt** — die Gattungsbuffs (330400, 6611300..302, 8330100..102, 8330103/104, 8851200/250) liegen **0-mal** im Spielstand; ueber ein Custom-Relikt nicht zu Ende gefuehrt |
| Revenant *Incantations x All*, **Bestial** steigt | **widerlegt** — `Improved Bestial Incantations` zeigt unter `Incantations` `no change`; erst unter der Schulwahl `Bestial` `+42.1` (Gegenprobe offline: 577,5545 → 577,5545 bzw. → 646,8611) |
| Revenant *Incantations x All*, **Klauen-Relikte fallen** | **belegt** im Sinne „zaehlen nicht": Suche `Claw Attack` → `no change` |
| Nachtrag: Revenant mit **7370900 (Beast Claw)** | **belegt** — ohne Tauschrelikt Satz `Rejection deals no damage, so this is 0.00. …`; das Relikt (`Grand Drizzly Scene`, blau) steht als `BEST FOR DAMAGE (Incantations)` mit **+350.5** (deckt den T-324g-Wert) |
| Nachtrag: physische Buffs zaehlen, Holy nicht | **belegt** — unter `Bestial x Physical`: `Physical Attack Up` `+21.0`, `Holy Attack Power Up` `no change` (die eine Holy-Karte mit `+9.9` traegt zusaetzlich `Faith +2`) |
| Revenant *Bestial x Physical* | **belegt** (siehe Zeile darueber); Schulfaktor sichtbar: `Improved Bestial Incantations` `+42.1` |
| Wylder *Weapon art x Fire* mit Startwaffen-Konversion Fire | **belegt, qualitativ** — Konversionsrelikt `Night of the Beast` `+19.8 AR`; danach im Build: `Improved Skill Attack Power` `+1.8 AR`, ein Feuer-Effekt `+12.0 AR`, `Physical Attack Up` `no change`. Die **multiplikative Zerlegung** (Skill x Fire x Konversion als eine Zahl) ist am Artefakt nicht einzeln nachgerechnet |
| Recluse *Sorceries x Magic* | **belegt** — Satz vorhanden, `Magic Attack Power Up` `+5.6`, `Intelligence +3` `+5.3`, Klassenrate `Improved Melee Attack Power` `no change` (Zauber ist kein Schwung einer Waffenklasse) |

## Kanten, je Ergebnis

| Punkt | Ergebnis am Artefakt |
|---|---|
| AK-344.1 Guardian *Sorceries* | **belegt, wortgleich**: `This Nightfarer starts with neither a staff nor a seal, so Sorceries is not counted: there is no spell of this build's own to rank.` |
| AK-344.2 Revenant *Sorceries* | **belegt, wortgleich**: `Sorceries is not counted for this Nightfarer: Finger Seal casts incantations, …` |
| AK-344.2 Recluse *Incantations* | **belegt, wortgleich**: `… Recluse's Staff casts sorceries, …` |
| AK-344.4 Recluse *Weapon art* | **belegt, wortgleich** (`Weapon art is not counted for this Nightfarer: a staff or a seal …`) — die Umbenennung AK-338 ist im Satz angekommen |
| Recluse *Weapon* x *All* | **belegt**: kein Zusatzsatz (AD-053.5) |
| Schule ohne Zugehoerigkeit (`Dragon Cult` bei Beast Claw) | **belegt**: Zahl ohne Schulfaktor (`Improved Bestial Incantations` `no change`, Faith weiter `+9.9/+14.8`), Beschriftung `Damage (Dragon Cult)` |
| AK-345 zwei Tauschrelikte | **belegt**: Satz steht **zusaetzlich** zum Unkalibriert-Satz und nennt den gerechneten Zauber je Schadensart — `All`/`Physical` → `Beast Claw`, `Lightning` → `Lightning Spear` |
| AK-341 Wahl waehrend Optimize | **belegt, teilweise**: Wechsel der `damage_type`-Box waehrend `Working out maximise damage.` → Antwort wird verworfen (`Nothing suggested yet.`), kein Absturz, beide Boxen bleiben bedienbar. Nicht geprueft: ob in dem Fenster ein *veralteter* Vorschlag stehen bleiben kann (QA-268-Nachbarschaft) |
| AK-347 Persistenz | **belegt**: `hit_with=skill`, `damage_type=Physics` ueberleben Neustart (Boxen oeffnen auf `Weapon art` x `Physical`); beide Schluessel flach, ohne `/` |
| AK-347 Rueckfall `art:family:110` | **belegt**: Box oeffnet auf `Weapon`, `damage_type` bleibt `Physical` |
| AK-347 Rueckfall unbekannt (`family:999999`) | **belegt**: dito |
| AK-347 alter Schluessel `damage_art` | **belegt**: `damage_art=type:Fire` wird ignoriert, `hit_with` faellt auf `Weapon`, `damage_type` kommt aus dem eigenen Schluessel |
| Charged nicht in der Box | **belegt**: `hit_with_box` = Weapon / Weapon art / Sorceries / Incantations / Trennlinie / 14 Schulen (Bestial … Thorn) — kein `Charged`, genau **eine** Trennlinie (Bestaetigung AK-338 aus dem T-325a-Nachtrag) |
| AK-339 | **belegt**: `All` / Trennlinie / Physical, Magic, Fire, Lightning, Holy = 6 Eintraege + 1 Linie |
| AK-342 Kopfzeilen | **belegt** fuer die Zauberzeile: `Faith +3: Faith +3  Physical spell damage (Beast Claw) +16` (Schadensart erdient, Schule nicht, weil kein Bestial-Buff im Build) und `… Spell damage (Lightning Spear) +16` (nichts erdient). Fuer die Waffenzeile: `Strength +3: Strength +3  Physical attack rating +4` — die Regel stimmt, die Zeichenkette `Fire Weapon art attack rating` ist **nicht** erzeugt worden (siehe „Nicht getestet") |
| AK-343 Unkalibriert-Satz | **belegt, wortgleich**, in jeder Zauberzelle mit Zahl; weicht dem spezifischeren Satz, wo der Zauber keinen Schaden traegt |
| AK-346 Picker-Vererbung | **belegt**: `Damage (Incantations)`, `Damage (Physical Bestial)`, `Damage (Magic Sorceries)`, `Damage (Fire Weapon art)`, Chip `BEST FOR DAMAGE (…)` — Damage type vor Hit with |
| AK-350/352 Breite am Desktop | **belegt**: verfuegbare Breite 4096 logische px (5120 physisch / 1,25); Fenster oeffnet **2448 px physisch = 1958,4 logische px** (UIA-`BoundingRectangle`; DWM-Rahmen 2451 → 1960,8; `GetWindowRect` 2467 enthaelt die unsichtbaren Anfasser). Deckungsgleich mit Bedarf 1959 px |
| AK-350/351 Tooltips der drei Boxen | **belegt, wortgleich** (echtes Qt-Tooltipfenster, Hover): `goal_box` „Chooses what the Advisor ranks your build for."; `hit_with_box` der volle AK-340-Satz; `damage_type_box` „Restricts Maximise damage to one kind of damage." |
| AK-351 Kuerzungsreihenfolge | **belegt** bei 1714 logischen px (manuell verschmalert, Vorschlag sichtbar): Statuszeile Breite 0, `goal_box` 228→97 und `hit_with_box` 170→98 px elidiert, Aktionsknoepfe praktisch unveraendert (100→97/98 physisch). Darunter siehe QA-292 |
| Arsenal-Satz | **belegt, wortgleich**: „… A spell tile here still shows what it costs you, not its damage; the Advisor's Hit with box works spell damage out for a ranking instead." |

## Befunde

### [P2 | Minor | Hoch] `GOAL.md` A26, erste Nachweiszeile ist am gebauten Stand nicht woertlich einloesbar

**Adressat:** director (Eigentuemer des Abnahmekriteriums)
**Betroffen:** `GOAL.md` Z. 559-565 gegen `ARCHITECTURE.md` AD-054 (N4) /
Kombinationstabelle Zeile 5 und `nrplanner/damage.py::_art_of` /
`model.art_factor`
**Umgebung:** Artefakt 1.17.0, Spielstand des Nutzers (313 Relikte), Revenant,
`Revenant's Chalice`, Beast-Claw-Tauschrelikt im Build

**Reproduktion:**
1. Revenant waehlen, `hit_with` = `Incantations`, `damage_type` = `All`.
2. Beast-Claw-Tauschrelikt (`Grand Drizzly Scene`, blau) in Slot 1 legen.
3. Picker eines freien Slots oeffnen, nach `Improved Bestial Incantations`
   suchen.

**Erwartet** (GOAL A26): „Relikte mit Faith, Improved Incantations und Bestial
steigen".
**Tatsaechlich:** Faith steigt (`+9.9`/`+14.8`); ein Bestial-Relikt zeigt
`no change`; Gattungsbuffs („Improved Incantations", 10 Ids) besitzt der
Nutzer nicht, sie waren am Artefakt nicht pruefbar. Unter der Schulwahl
`Bestial` steigt dasselbe Relikt um `+42.1`.

**Analyse:** Das ist kein Rechenfehler, sondern der Entwurf: eine Schulrate
zaehlt nur, wenn die Frage die Schule nennt (Kombinationstabelle Zeile 5,
AD-054 N4, offline gegengerechnet: 577,5545 unveraendert unter
`incantations`, 646,8611 unter `family:23`). Der GOAL-Satz stammt aus der
Zeit der **einen** Box und ist mit der Zwei-Felder-Frage nicht mehr deckungs-
gleich. OF-58 haelt fuer denselben Absatz bereits fest, dass entweder der
Nachweis mit Relikt zu fahren oder der Wortlaut nachzuziehen ist.

**Auswirkung:** Das Abnahmekriterium A26 ist in seiner ersten Zeile nicht
belegbar; jeder spaetere Pruefer stolpert an derselben Stelle. Fuer den
Spieler aendert sich nichts.

**Vorschlag:** Zwei Lesarten, eine Entscheidung des `director`: (a) GOAL A26
Nachweiszeile 1 auf den gebauten Entwurf ziehen („Faith steigt; Schul- und
Gattungsbuffs steigen unter der jeweiligen Wahl") — dann ist der Punkt
erledigt; (b) das Verhalten aendern (Schulbuff zaehlt auch unter der Gattung,
wenn der Zauber der Schule angehoert) — dann faellt AD-054 N4 und die
Kombinationstabelle mit. Vorschlag: (a), zusammen mit OF-58.

### [P4 | Minor | Niedrig] Unterhalb der Programm-Startbreite schrumpfen auch die drei Aktionsknoepfe

**Adressat:** ui-ux-designer (Wortlaut AK-05/AK-351.3), Entscheid director
**Betroffen:** `nrplanner/advisorbar.py` Zeilenlayout / `UI_SPEC.md` AK-351
Punkt 3 („Keine Stufe dieser Liste darf jemals einen Aktionsknopf
verkleinern, kuerzen oder ausblenden")
**Umgebung:** Artefakt 1.17.0, Vorschlag sichtbar (`Apply all`/`Why`/`Clear`),
Fenster von Hand verschmalert (`SetWindowPos`, entspricht Ziehen am Rand)

**Reproduktion:**
1. Optimize laufen lassen, bis die drei Aktionsknoepfe stehen.
2. Fenster auf 2160 / 1920 / 1800 px physisch (1714 / 1522 / 1426 logisch)
   ziehen.

**Erwartet:** Statuszeile 0, Boxen elidiert, Aktionsknoepfe unveraendert.
**Tatsaechlich (gemessene Breiten, physisch):**
1714 logisch — Boxen 97/98/97, `Optimize` 98, `Apply all` 98, `Clear` 97,
Status 0 (spec-konform);
1522 logisch — Boxen 70/70/71, `Optimize` 70, `Apply all` 71, `Clear` 70;
1426 logisch — Boxen 58/58/58, `Optimize` 57, `Apply all` 58, `Clear` 57.

**Analyse (Hypothese, nicht zu Ende belegt):** Bei 57-71 px physisch
(46-57 logisch) liegt die Beschriftung `Apply all` nach der projekteigenen
Definition von „cut" (`fontMetrics().horizontalAdvance(caption) >
width - 2 x PM_ButtonMargin`, `tests/advisor_row_at_the_window.py`) ueber dem
Platz — der Bildnachweis dazu fehlt (Lauf abgebrochen). AK-351 ist fuer die
**Startbreite** geschrieben; das Fenster laesst sich von Hand unter den
AK-271-Boden (1536 px) ziehen, und dort greift die Reihenfolge nicht mehr.

**Auswirkung:** Nur bei bewusstem Schmalziehen; an keiner Breite, die das
Programm selbst waehlt. Kein Datenverlust.

**Vorschlag:** Entweder AK-05/AK-351.3 um „ab der Untergrenze AK-271" ergaenzen
(dann ist das Verhalten spec-konform), oder dem Fenster eine Mindestbreite
geben, die die Knoepfe traegt. Entscheidung gehoert dem `director`.

## Beobachtungen (keine Befunde, keine Prioritaet)

- **„Improved Attack Power with 3+ Hammers Equipped" (T-324g-Gegenprobe):
  Vorgabe, kein Befund.** Am Artefakt reproduziert: fuer Recluse *Sorceries x
  Magic* steht das Relikt `Grand Drizzly Scene` als `BEST FOR DAMAGE (Magic
  Sorceries)` mit **+25.0**; das `Why` nennt „Physical/Magic/Fire/Lightning/
  Holy Attack +20.0%". Die Kette ist vollstaendig dokumentiert: AD-026 (eine
  unerfuellte Waffentyp-Schranke bleibt eine herstellbare Bedingung, die Rate
  ist flach), AD-036.6 (`advisor_defaults()` = Best case fuer alle 420
  bedingten Buff-Ids; 7081200 ist darin enthalten) und die A26-Praemisse
  (ungescopte `*AttackRate` erreichen jeden Treffer ihrer Schadensart, also
  auch einen Zauber). Offline gegengerechnet: ohne Vorbelegung 206,1327, mit
  `advisor_defaults()` 247,3593 = genau x1,2.
- Der Satz aus der Kombinationstabelle „Schule, der der Bezugszauber nicht
  angehoert → Zahl ohne Schulfaktor **plus Satz, welcher Zauber gerechnet
  wurde**" hat im Picker keine Entsprechung: dort steht nur der
  Unkalibriert-Satz; den Zauber nennt erst die Kartenkopfzeile im `Why`
  (AK-342). Frage an `ui-ux-designer`, ob das so gemeint ist.
- Der Suchbegriff des Pickers bleibt nach dem Ziehen eines Relikts stehen und
  das naechste Oeffnen zeigt `0 of N matching` (bekanntes Verhalten,
  `app._set_search`, kein neuer Befund).
- Im Custom-Relikt-Dialog liefert die Suche `Improved Sorceries` in einem
  blauen Slot **0** Eintraege (Farbbindung des Effekts vermutet, nicht
  nachgeprueft) — damit war der einzige Weg zu den nicht besessenen
  Gattungsbuffs versperrt.
- Die Instanzsperre hat zweimal genau wie beschrieben geblockt, als noch eine
  eigene Kopie lief; der Hook nennt die PIDs und verweigert den ganzen Befehl
  (auch das Schreiben der Skriptdatei im selben Aufruf — beim naechsten Lauf
  Schliessen und Starten in getrennte Aufrufe legen).

## Explorationsprotokoll (was versucht wurde und gehalten hat)

- 6 Fensterlaeufe am Artefakt, alle umgelenkt, nie zwei zugleich; Treiber
  `scripts/drive_window.ps1` plus eigene Hilfsfunktionen im Scratchpad
  (`lib.ps1`: `SetCombo` ueber ExpandCollapse + echten Klick, `OpenSlot`,
  `CardVals`, `Panel`, `RegAdvisor`).
- Offline-Gegenrechnung ohne Fenster (`ground2.py`, Testabzug v16 + tests/
  `advisor_cases`): alle Zellenwerte, die im Fenster als Delta erscheinen,
  gegen die Fassade nachgerechnet (Revenant 577,5545 / 612,2078 / 646,8611;
  Recluse 206,1327 / 247,3593; Zwei-Tausch-Fall 542,4545 unter Thunder).
- Registry als zweite, unabhaengige Spur fuer jede Boxwahl gelesen
  (`hit_with`, `damage_type`, `damage_art`) statt nur der Boxbeschriftung zu
  glauben.
- Tooltips ueber `EnumWindows` auf die Qt-Tooltipklasse gelesen (UIA kennt
  keinen ToolTip-Typ), Wortlaut Zeichen fuer Zeichen mit
  `advisorbar.HIT_WITH_TOOLTIP`/`DAMAGE_TYPE_TOOLTIP`/`GOAL_BOX_TOOLTIP`
  verglichen.
- Effektfilter-Markierungen (Faith +3, Beast-Claw-Tausch, Strength +3,
  Improved Skill Attack Power) wurden gesetzt, benutzt und **wieder
  geloescht**; `advisor/required` steht am Ende leer (nachgelesen).

## Nicht getestet

1. **AK-337** Sichtbarkeitsregel (beide Paare verschwinden, wenn `goal_box`
   nicht auf `Maximise damage` steht) — nicht angefasst.
2. **AK-348** Tastatur/Tab-Reihenfolge — nicht angefasst.
3. **AK-352** Zeilen `room=1920`/`2560` am Artefakt — nur die Desktop-Zeile
   (4096) gemessen; die beiden Referenzbildschirme liegen als Waechter des
   `developer` vor (`test_advisor_apply.py`), darauf habe ich mich verlassen.
4. Die Zeichenkette **`Fire Weapon art attack rating`**: zweimal versucht
   (Strength +3 favorisiert; zusaetzlich Improved Skill Attack Power
   verlangt), beide Male ohne Attribut-Zeile im `Why` — unter `Fire` bewegt
   kein Attribut die Zahl, weil die Feueranteile aus der flachen Konversion
   kommen. Regel selbst ist ueber zwei andere Kopfzeilen belegt.
5. **Gattungsbuffs** („Improved Sorceries/Incantations") — im Spielstand nicht
   vorhanden, Custom-Relikt-Weg nicht zu Ende gefuehrt.
6. **Bildnachweis** der schmalen Leiste (QA-292) — Aufnahme war der naechste
   Schritt.
7. Suite, Startzeit, Speicher, Erstlauf — nicht Teil dieses Auftrags.
8. NH-004-Abschluss (Instanz schliessen, Registry-Zweig loeschen) — siehe
   Kontraktblock, **offen**.

## Naechster Schritt (konkret)

1. `powershell -File <scratchpad>\T-325h\close.ps1` (schliesst die laufende
   Instanz sauber, meldet `processes: 0`), danach
   `reg delete HKCU\Software\DankYeeterT-325h /f`.
2. QA-291 dem `director` vorlegen (GOAL-Wortlaut vs. AD-054 N4, zusammen mit
   OF-58).
3. Restliste 1-6 oben in einem zweiten, kurzen Fensterlauf (Schaetzung: ein
   Start, ~20 Aufrufe).

## Register-Zeilen fuer `qa/findings.md` (anhaengen, nicht eingetragen)

Die Datei ist von mir **nicht** geaendert worden (Zugschwelle). Anzuhaengen:

```
| QA-291 | GOAL A26 Nachweiszeile 1 am Bau nicht woertlich einloesbar (Bestial/Improved Incantations unter der Gattungswahl) | P2 | director | offen | 2026-09-20 |
| QA-292 | Unter der Programm-Startbreite schrumpfen auch Apply all / Why / Clear (AK-05/AK-351.3) | P4 | ui-ux-designer | offen | 2026-09-20 |
```

Hoechste vergebene QA-Id nach diesem Lauf: **QA-292**.
