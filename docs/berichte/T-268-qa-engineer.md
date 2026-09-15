# T-268 Retest (qa-engineer)

STATUS: teilweise — Werkzeug-Zugschwelle (150 Aufrufe) waehrend des Laufs erreicht,
bevor A6-Wandzeit, Hauptthread-Sonde und der A18/A20-Kurzcheck begonnen wurden.
Kein Code, kein Test und keine Projektdatei wurden in diesem Lauf veraendert
(`git status --short` leer); `qa/findings.md` ist unveraendert und muss vom
naechsten Lauf fortgeschrieben werden.

## Artefakt

`dist/NightreignHelper.exe`, SHA-256 `f29eb92d88ed14416a488f32f7ab655bf27fec77e2be74105782d0980904cf1b`
(Hash lokal nachgerechnet, stimmt mit dem Auftrag), Commit `3c2ff23`, Titelzeile
"Nightreign Helper 1.12.1". Umgebung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-268qa`,
eigenes `LOCALAPPDATA`/`APPDATA`/`USERPROFILE` im Scratchpad, Testabzug (841
Dateien) hineinkopiert, eingefrorene Savekopie unter
`<scratch APPDATA>\Nightreign\76561198179244962\NR0000.sl2`. Einzige
Fensterinstanz (`tasklist` vor dem Start leer, PID 32912 danach eindeutig).

## Fertig geprueft (alle bestanden)

**AK-297 (Legende immer sichtbar, Wortlaut woertlich):** am Artefakt live
bestaetigt. Picker-Legende in der Sort-by-Reihe **vor jeder Markierung**
sichtbar, einzeilig, rechtsbuendig (kein Umbruch auf 3 Zeilen — der zweite
Commit `6560895` haelt). Why-Dialog-Legende ebenso sichtbar ohne vorherige
Markierung. Beide Texte zeichenweise identisch nachgemessen (Code-Point-Dump,
nicht nur String-Vergleich): `Click an effect's bullet to exclude it, click
again to require it (▲), and once more to clear it.` (▲ = U+25B2, per UIA
NameProperty exakt uebernommen — die anfangs leer wirkenden Klammern waren ein
Konsolen-Encoding-Artefakt meines eigenen Skripts, kein Programmfehler; mit
`[Console]::OutputEncoding = UTF8` korrekt).

**AK-298 (gewaehlte Hand betont):** am Artefakt live per PrintWindow-Bildvergleich
bestaetigt, an allen drei genannten Flaechen, mit echtem Umlegen des Schalters
(kein Neustart der Karte noetig):
- Waffenkachel (`Wylder's Greatsword`): `56` fett/ACCENT bei 1H, `58 2H`
  MUTED — nach Toggle exakt umgekehrt, sofort ohne Kartenwechsel.
- Werteblatt (`Physical`-Zeile und `Total`-Zeile): dieselbe Umkehr, sofort.
- Arsenal-Kachel (`Weapons & spells`, Suche `"Wylder's Greatsword"`): zeigt
  beim Betreten des Tabs die zu diesem Zeitpunkt aktuelle Schalterstellung
  korrekt (1H- und 2H-Aufnahme beide stichprobenartig verglichen). Die im
  Commit-Kommentar genannte Einschraenkung ("Arsenal aktualisiert erst beim
  naechsten Tabaufbau") ist am Artefakt **nicht als eigenstaendiger Befund
  beobachtbar**: der Handschalter existiert nur auf dem Build-planner-Tab,
  ausserhalb des Arsenal-Tabs ist er gar nicht erreichbar — ein Nutzer kann
  also nie gleichzeitig auf das Arsenal schauen und den Schalter umlegen. Das
  AK-298-Akzeptanzkriterium ("ohne Neuaufbau/Schliessen der Karte") ist damit
  fuer die Arsenal-Kachel an jedem erreichbaren Beobachtungspunkt erfuellt.

**QA-273 (AK-281-Satz, Besitz vs. Slot-Passung):** am Artefakt exakt
reproduziert und die Korrektur bestaetigt. Wylder, Wylder's Chalice, Deep aus,
`Improved Attack Power with 3+ Daggers Equipped` ueber die Picker-Markierung
(Klick-Zyklus None → excluded → required, visuell am ▲ bestaetigt) als
`Must include` markiert (der Effekt liegt nur auf Deep-Relikten, Blau-Slot
`Deep Slot 2`, 1 von 33 Treffern) → Leiste `0 of 3 slots filled · 3 slots are
blocked by a requirement you marked.`; Why-Dialog:
`You own 2 copies carrying Improved Attack Power with 3+ Daggers Equipped,
but none fits the open slots (Deep of Night is off).` — wortgleich mit dem
Fix-Commit `ab1fbaa`, Besitzzahl (2) korrekt gegen die realen Daten.

## Nicht mehr erreicht (Zugschwelle)

- A6-Wandzeit (Klick → Antwort, Cache geleert, n=5, Zielwert ≤ 1300 ms
  gegen Vorher 1809 ms aus T-265d): **nicht gemessen.** Eine einzelne
  beilaeufige Messung beim AK-297/298-Testen (kalter Start, ungeleerter
  Cache, kein n=5) ergab 727 ms bzw. 865 ms fuer denselben einfachen Build
  (Wylder, 3 leere Slots) — deutlich unter dem alten 1809-ms-Wert, aber
  **nicht die S11-Szenario-Messbedingung** aus T-265d/T-267b und daher kein
  belastbarer A6-Beleg. Reine Beobachtung, kein Befund.
- Hauptthread-Blockade-Sonde (`SendMessageTimeout(WM_NULL)`-Kadenz waehrend
  Optimize): nicht begonnen.
- A18/A20-Persistenz-Kurzcheck: nicht begonnen. Die Handschalter-Persistenz
  wurde nur indirekt beobachtbar (Registry-Schreibpfad in diesem Lauf nicht
  gegengeprueft).
- `qa/findings.md`-Anhang (QA-273/274/275-Status, A6-Zahl): **nicht
  geschrieben** — Register ist im aktuellen Zustand belassen, siehe unten.

## Bekannter Nebeneffekt aus diesem Lauf

Die Live-Instanz (PID 32912, eigene Testumgebung `DankYeeterT-268qa`, **nicht**
der echte Nutzerspeicher) blieb mit `Improved Attack Power with 3+ Daggers
Equipped` als `Must include` markiert und Deep of Night aus stehen — der
letzte Klick, der die Markierung zuruecksetzen sollte, konnte wegen eines
Skriptfehlers (veraltetes Fenster-Handle nach Dialog-Neustart) nicht mehr
visuell bestaetigt werden, und die Zugschwelle griff vor dem Korrekturversuch.
Wirkung ausschliesslich in der eigenen Testumgebung (eigener
`NIGHTREIGN_SETTINGS_ORG`); der echte Nutzerspeicher ist nicht betroffen.
Fenster/Prozess wurden nicht beendet.

## Naechster Schritt

Neuer Lauf setzt fort mit: (1) Zustand der laufenden Instanz pruefen und ggf.
sauber beenden, (2) A6 nach T-265d-Rezept (S11-Szenario, Cache je Messung ueber
`Rescan save` geleert, n=5), (3) Hauptthread-Sonde waehrend eines Optimize-Laufs,
(4) A18/A20-Kurzcheck, (5) Register-Anhang in `qa/findings.md` (QA-273 →
behoben, QA-274/QA-275 → behoben, mit den obigen Belegen).

Verwendete Hilfsskripte (nicht Teil des Projekts, im System-Temp):
`C:\Users\Daniel\AppData\Local\Temp\uia_helpers_T268.ps1` und die
`*_T268.ps1`-Familie daneben — wiederverwendbar fuer den Fortsetzungslauf
(UIA-Fensterfindung, PrintWindow inkl. `SetProcessDpiAwarenessContext(-4)`,
Klick-Helfer). Wichtige Lektion darin bereits verankert: ohne
`SetProcessDpiAwarenessContext` vor `SetCursorPos` landen Klicks bei 125%
Skalierung neben kleinen Zielen (den 16×18-px-Markierungspunkten) und
scheitern lautlos (kein Fehler, nur Wirkungslosigkeit).

## Fortsetzung (15.09.2026): A6-Wandzeit, Hauptthread-Sonde, Slot-Frage

STATUS: erledigt. Neue Instanz (Director hatte die stehen gelassene T-268-Instanz
beendet, `tasklist` vor dem Start leer), eigene Umlenkung
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-268b`, `LOCALAPPDATA`/`APPDATA`/`USERPROFILE`
im Scratchpad, Testabzug frisch hineinkopiert (841 Dateien, 20 812 293 B, Hash
gegen die Vorlage geprueft), eingefrorene Savekopie (SHA-256 `f4940e4b…3540`,
identisch mit T-265d, 319 Relikte) hineinkopiert. Artefakt erneut lokal
nachgerechnet: `f29eb92d88ed14416a488f32f7ab655bf27fec77e2be74105782d0980904cf1b`
— stimmt mit dem Auftrag.

**Szenario S11-A** (wie T-265d/T-267b): Wylder, `Wylder's Chalice` (Rot 53 /
Gelb 55 / Weiss 212-213 verfuegbar + Deep Rot 22 / Blau 33 / Gruen 22), Deep of
Night an, Stufe 15, sechs leere Slots (`Reset Chalice` vor jedem Aufbau, dann
Kelch neu waehlen und Deep erneut anhaken — `Reset Chalice` wirft Deep und
Kelch auf den Ausgangszustand zurueck), `Maximise damage`, Umschalter 1H,
keine Markierung. Fensterlage einmalig auf `0,37` verschoben (die
Ausgangsposition lag teilweise ausserhalb des 4096×1728-Bildschirms und
machte einen Teil der Slot-Knoepfe unklickbar — reines Testartefakt der
mitgebrachten Fensterposition, kein Programmfehler).

**A6, `Optimize` Invoke bis Antwort sichtbar** (UIA `InvokePattern.Invoke`,
Cache vor jedem der n=5 Laeufe per `Rescan save` geleert, Wartezeit auf `You own
319 relics in total.` vor dem naechsten Lauf): 1317 / 1330 / 1358 / 1363 / 1406 ms,
**Median 1358 ms**. Vorher T-265d 1809 ms → **-25 %**, Zielwert ≤ 1300 ms
**knapp verfehlt** (+58 ms). Passt zur Quellstand-Zahl aus dem T-268a-Commit
(`0f1ea0f`, headless S12 1291,9 ms) — der Post-Beam-Anteil (UIA-Latenz,
`WAIT_VISIBLE_MS`) macht auch nach dem Fix noch rund 60-80 ms des
Restabstands aus.

**Hauptthread-Blockade-Sonde waehrend `Optimize`** (`SendMessageTimeout`
mit `WM_NULL`, `SMTO_ABORTIFHUNG`, Kadenz durch die Laufzeit der Probe selbst
bestimmt, ~15-16 ms typischer Takt, alle drei Umlaeufe zusaetzlich ein
Antwort-Text-Check): ueber die 5 Laeufe 87-93 Probes je Lauf, **0 von ~450
Umlaeufen ≥ 50 ms**, maximaler Einzelwert 6,8 ms. Der einzelne T-265d-Ausreisser
(62,1 ms, erster Kaltlauf nach Programmstart) trat in keinem der 5 Laeufe auf.

**Slot-Frage, weisser Slot 3 (212-213 Kandidaten), Dialog sichtbar** (Klick auf
den Slot-Knopf, Kelch/Deep vor jedem Lauf per `Reset Chalice` + Neuaufbau
zurueckgesetzt, damit der Slot wieder leer ist; Fund per UIA-Fensterelement
als Nachfahre des Hauptfensters, `WindowPattern.Close()` nach jeder Messung):
1585 / 1624 / 1627 / 1643 / 1663 ms, **Median 1627 ms**. Vorher T-265d 1747 ms
→ **-7 %**, weiterhin weit ueber dem 500-ms-Budget aus S11. QA-258 bleibt fuer
den Kartenbau selbst bestehen — der T-260-Fix (`e164a25`) wirkt auf die
Bewertungsschicht, nicht auf den hier gemessenen Anteil.

**Randbeobachtung (kein Befund):** Relikt-Slot-Knoepfe (`QPushButton`,
`relicslots.py:311`) reagieren auf einen simulierten `mouse_event`-Linksklick
zuverlaessig erst, wenn `SetCursorPos` unmittelbar vor dem Klick aufgerufen
wird und der UIA-Baum unmittelbar davor neu abgefragt wird — ein
zwischengespeichertes `BoundingRectangle` aus einem vorherigen Dump traf das
falsche Element (Layoutzeilen verschieben sich bei jedem Optimize-Suchvorschlag
um bis zu 300 px, weil vorgeschlagene Relikte als Button mit Effektliste an
derselben Stelle wie der leere Slot-Knopf erscheinen). Reines Testskript-Risiko,
kein Programmverhalten.

**qa/findings.md:** vier Zeilen angehaengt — QA-258 (Nachtrag mit den A6-Zahlen
oben, Status weiterhin `teilweise`), QA-273 (`behoben -- Retest bestanden`),
QA-274 und QA-275 (beide `behoben -- Retest T-268 bestanden`, AK-297/298 laut
Hauptteil dieses Berichts bestaetigt). Kein Commit.

**Aufraeumen:** eigene Prozesse (`NightreignHelper.exe` PID 32268/35616,
gestartet aus diesem Lauf) am Ende beendet, `tasklist` danach leer.
