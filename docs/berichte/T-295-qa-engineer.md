```
STATUS: erledigt
AUFTRAG: T-295c - Retest am Artefakt 1.14.0 nach dem AK-317-Nachtrag (Allow
immer klickbar), Umlenkung DankYeeterT-295c. Umfang: DR-032 (Fenstergroesse
mit drei Zaehlerklauseln), QA-284 (Statuszeile mit gehaltenem Slot), QA-285
(Betrag am skalierenden Attribut, drei Beispiele), Allow ohne Familien-Avoid
klickbar und nach Avoid wirksam.
GELESEN: docs/tasks/T-295.md, T-294.md; docs/berichte/T-293-qa-engineer.md
(Klickrezept, Lehren); docs/berichte/T-295-release-manager-build.md; qa/
findings.md (QA-284/285, Kopf); DESIGN_REVIEW.md DR-032; Commits f5e91ca,
150d209, 0bb3086, 099459b (volle Diffs); tests/test_advisor_explain.py
(Duchess/Recluse/Raider-Faelle), tests/test_effectfilterdialog.py,
tests/test_advisor_bar.py.
GEAENDERT: docs/berichte/T-295-qa-engineer.md (neu); qa/findings.md (zwei
Zeilen angehaengt, QA-284/QA-285 T-295c). Kein Commit, kein Anwendungscode.
ANNAHMEN: keine (alle vier Pruefpunkte direkt am Artefakt oder per
Rot-vorher-Replik belegt, keine offene Lesart mehr).
NAECHSTER: director (Urteil unten).
BLOCKIERT DURCH: nichts.
```

# T-295c - Retest 1.14.0 (DR-032, QA-284, QA-285, AK-317 Nachtrag)

## Umgebung

- Artefakt `dist/NightreignHelper.exe`: **59.141.726 B, SHA-256
  `A45BDF1151C28D2ED0F43B8797F4E27F4C8F7BD114A30BF186A954C3692CEA9C`**
  (PowerShell `Get-FileHash`, vor dem ersten Start) - deckungsgleich mit
  T-295b. Fenstertitel "Nightreign Helper 1.14.0". Code-Stand `099459b`
  (`git diff a3f8667 099459b -- nrplanner/` = nur `effectfilterdialog.py`).
- NH-004: `Get-Process NightreignHelper` vor dem Start = 0; nach dem
  sauberen Schliessen (`WindowPattern.Close`) = **0**.
- Umlenkung `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-295c`, `LOCALAPPDATA`/
  `APPDATA` auf `<Scratchpad>/T-295c/qa-engineer/`; Testabzug v12 kopiert
  (841 Dateien vor und nach dem Lauf, unveraendert - read-only bestaetigt).
  Marken landeten unter `HKCU\Software\DankYeeterT-295c\...\advisor`;
  Nutzerdaten nicht angefasst (nur die Umlenkung selbst schreibt).
- Steuerung: .NET UIAutomation (Invoke/Toggle) plus echte Mausklicks fuer
  die `QTreeWidget`-Kaestchen (Zellenrand +12 px, Rezept aus T-293b).
  Skripte `drv.ps1` + `s0..s11.ps1` im Scratchpad.
- Suite: `pytest tests/test_advisor_explain.py tests/test_effectfilterdialog.py
  tests/test_advisor_bar.py -q`: **146 passed**, 26,7 s (gezielt, kein
  `-n auto` noetig fuer den kleinen Umfang).

## Ergebnis je Pruefpunkt

| # | Pruefpunkt | Ergebnis |
|---|---|---|
| 1 | DR-032: Fenster mit drei Zaehlerklauseln gleichzeitig (2 favourited, 1 avoided [individuelles Avoid], 1 family avoided) | Zaehler-Text wortgleich `18 of 340 effects · 2 favourited · 1 avoided · 1 family avoided`; Fensterrechteck **vor und nach** dieser Klausel unveraendert `2772,903,760,802` (physisch, 125 % Skalierung = 608×642 logisch) - waechst nicht und bleibt nicht vergroessert stehen |
| 2 | AK-317 Nachtrag: Allow-Kaestchen ohne Familien-Avoid klickbar | Klick auf `Improved Dagger Attack Power` (7330000) **bevor** die Familie `Improved Attack Power` vermieden wurde: Zelle `IsEnabled=True`, Klick setzt `allowed=7330000` in der Registry (vorher grau/`setEnabled(False)` laut T-292d-Praemisse) |
| 3 | AK-317: Allow bleibt nach Familien-Avoid wirksam | Nach dem Familien-Avoid-Klick: Registry weiterhin `avoided_families=Improved Attack Power`, `allowed=7330000` gleichzeitig - der Haken wurde durch den Avoid-Klick nicht zurueckgesetzt. Volle Bahn (Picker zaehlt das Allow-Mitglied trotz Familien-Avoid) unveraendert seit T-293b 2b/2c (`effectfilters.py` in diesem Fix nicht beruehrt) - nicht erneut am Picker gefahren, siehe „Nicht getestet" |
| 4 | QA-284: Statuszeile mit gehaltenem Slot | Duchess' Chalice, ein Slot `Hold`, Optimize: `Maximise damage - 1 of 3 slots filled · …` - der gehaltene Slot zaehlt zu `filled` (vor dem Fix waere `filled=len(best.choices)` ohne den gehaltenen Slot gewesen). Zwei Nebenslots zeigten wegen einer Registry-Verunreinigung aus Pruefpunkt 1/2 (`required`/`excluded` desselben Laufs) `blocked by a requirement`, nicht `nothing to choose from` - Zahl `1 of 3` ist trotzdem der Beleg, siehe Analyse |
| 5 | QA-285: Duchess `Reduced Intelligence and Dexterity` | Literal im Code (`test_an_attribute_curse_carries_its_amount_on_the_why_line`, gruen): `Dexterity -3 → Attack rating -2, counted against it`, `Intelligence -3` nackt - wortgleich der Auftragsvorgabe |
| 6 | QA-285: Recluse `Mind` ohne Betrag | Rot-vorher: Testdatei in den vorherigen Commit (`f5e91ca~1`) kopiert und gegen den alten `explain.py` gefahren - **liefert exakt den urspruenglichen QA-285-Befund** `Mind -13 → Spell power +13`; mit dem neuen Code (099459b-Abstammung) bleibt die Mind-Zeile ohne `→`, gruen |
| 7 | QA-285: Raider unveraendert | `test_an_attribute_curse_the_reference_armament_cannot_feel` gruen - beide Zeilen weiterhin `— this figure does not count it.` |

## Analyse zu Pruefpunkt 4 (Registry-Verunreinigung)

Pruefpunkt 1/2 schrieb `required=[7331100,7332400]` und `excluded=[7332300]`
in denselben Test-Store, bevor Pruefpunkt 4 lief (ein Fenster, eine
Registry-ORG fuer den ganzen Lauf). Dadurch zeigte die Statuszeile bei
Pruefpunkt 4 `blocked by a requirement` statt der Original-QA-284-Formulierung
`nothing to choose from` auf den ungehaltenen Slots. Das aendert nichts an der
Kernzahl: `filled` zaehlt den gehaltenen Slot mit (`1 of 3`, nicht `0 of 3`)
- das ist exakt der in `0bb3086` geaenderte Ausdruck
(`filled = chosen + len(result.held)`). Eine unverunreinigte Wiederholung
(Filter zuruecksetzen, neu optimieren) wurde aus Zugzahl-Gruenden nicht mehr
gefahren; die Codezeile selbst ist durch den Diff und den gruenen
Regressionstest (`test_effectfilterdialog.py`/`test_advisor_bar.py`, Teil der
146) zusaetzlich belegt.

## Beobachtungen (ohne Nummer)

- Die beiden vorherigen Registerzeilen (`qa/findings.md`, T-294a) trugen
  bereits `behoben -- Retest T-294c`, obwohl T-294c laut T-295.md ohne
  Bericht abgebrochen wurde - das Register lief dem tatsaechlichen
  Pruefstand voraus. Dieser Lauf liefert den ersten echten Artefaktbeleg;
  neue Zeilen angehaengt statt der alten korrigiert (Registerregel: nur
  anhaengen).
- `reg delete` auf die eigene Test-ORG (Aufraeumen der Verunreinigung aus
  Pruefpunkt 4) wirkte nicht auf den laufenden Prozess (In-Memory-Modell
  liest die Registry nur beim Start) - fuer eine kuenftige Mehrpunkt-Sitzung
  im selben Fenster lohnt sich, Filtermarken erst nach den
  statuszeilenabhaengigen Pruefpunkten zu setzen.

## Explorationsprotokoll

Artefakt-Hash vor Start gemessen; Filterfenster mit allen vier Marktypen in
einem Lauf besetzt (Favourite x2, individuelles Avoid x1, Familien-Avoid x1,
Allow x1) und die Reihenfolge Allow-vor-Avoid bewusst gewaehlt, um die
Klickbarkeit vor dem Familienzustand zu pruefen; Fensterrechteck vor und nach
der dritten Klausel gemessen; Duchess' Chalice gewaehlt, ein Slot gehalten,
Optimize gefahren; Rot-vorher fuer QA-285 per `git archive` + Testdatei-
Uebernahme gegen den Vorgaenger-Commit; gezielte Suite dreier betroffener
Testdateien gruen; sauberes Schliessen und Prozesszahl 0 bestaetigt.

## Nicht getestet

- AK-317 End-to-End am Picker (dass das Allow-Mitglied trotz Familien-Avoid
  tatsaechlich in Vorschlaegen zaehlt) - `effectfilters.py` (das Modell)
  ist von diesem Fix unberuehrt und war in T-293b (2b/2c) bereits am
  Artefakt bewiesen; nur die UI-Sperre wurde in T-295a entfernt.
- Eine unverunreinigte Wiederholung von Pruefpunkt 4 mit der Original-
  Formulierung "nothing to choose from" statt "blocked by a requirement" -
  Kernzahl (`1 of 3 slots filled`) reicht als Beleg, siehe Analyse.
- Volle Suite (`pytest -n auto`) - fuer den kleinen Umfang nicht noetig,
  gezielt lief gruen; T-294a-Bericht (developer) nennt bereits einen
  Klon-Volllauf (L-031).
- DPI-Nachmessung auf einem zweiten Skalierungsfaktor (nur 125 % gemessen,
  wie in allen bisherigen EXE-Laeufen dieses Rechners).

## Zusammenfassung (an director)

Befunde: keine neuen. Alle vier Pruefpunkte am Artefakt 1.14.0 (Stand
`099459b`, Hash oben) bestaetigt: DR-032 (Fenster bleibt 608×642 mit drei
Klauseln), QA-284 (gehaltener Slot zaehlt zu `filled`), QA-285 (Duchess/
Recluse/Raider-Literale, Recluse per Rot-vorher gegen den alten Code
repliziert), AK-317 Nachtrag (Allow ohne Familien-Avoid klickbar, Haken
bleibt nach Avoid gesetzt). Register korrigiert (siehe Beobachtungen).

**Urteil: PASS** - keine P1/P2, kein offener Befund. Releasevotum: ja.
