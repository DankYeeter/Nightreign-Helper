# T-275 -- Retest am Artefakt 1.12.3 (qa-engineer, 15.09.2026)

Artefakt `dist/NightreignHelper.exe`, SHA-256 `1c8b4ff52286928b7fc795cc65597bf7f0a65ed40c987c7fe63d0e9e2bb4dc88`
(59 123 168 B, Commit `2907a66` -- `git log --oneline -1 2907a66` zeigt
`chore(release): Version 1.12.3`) -- Hash, Groesse und Commit vor Testbeginn
geprueft, stimmen mit dem Auftrag ueberein. Umlenkung durchgaengig
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-275qa`, `LOCALAPPDATA`/`APPDATA` auf
eigene Scratch-Verzeichnisse (LOCALAPPDATA/APPDATA aus `T-268qa` wiederverwendet:
bereits kopierter Testabzug + eingefrorener Spielstand, gleiche Herkunft,
spart die Kopierzeit).

## Risiko-Briefing

Vier Pruefpunkte, priorisiert: (1) QA-277 ist ein P1 mit `RuntimeError`
(Absturzpfad einer bereits einmal an derselben Stelle gebrochenen Regression,
QA-258 → QA-277) -- am hoechsten Risiko, zuerst und am artefakt selbst mit
echter Zeitrennstrecke (Filter waehrend des Nachbaus), nicht nur der
Waechtertest. (2) AK-299/QA-278-Format ist eine reine Anzeigefrage, aber auf
drei Stellen dupliziert (Kachel/Werteblatt/Arsenal) -- eine Stelle koennte den
Fix verpasst haben. (3) Das power-user-Ziel 3 beschreibt einen moeglichen
Vertrauensbruch (Ausschluss wirkt, aber Why verschweigt ihn) -- inhaltlich am
naechsten an einem Datenintegritaetsproblem, deshalb vor den reinen
Kurzpruefungen. (4) QA-276-Zellen und A18/A20-Persistenz zuletzt, weil beide
in T-272 bereits mit Testabzug/Suite belegt sind und hier nur eine
Stichprobe am Artefakt verlangt ist.

## 1 -- QA-277 (RelicPicker-Absturz bei Filter waehrend Fuellung)

Weisser Slot 3 (Wylder, Wylder's Chalice, 212 Kandidaten), UIA-gesteuert am
laufenden Artefakt, 3 Durchgaenge: Slot oeffnen (`Invoke` auf den
Slot-Button) → Filter `attack` **waehrend** des Nachbaus setzen → Sortierung
wechseln → nach Vollbau Kopfzeile/Kartenzahl gegenpruefen → Dialog schliessen
→ `Rescan save` anstossen. Ergebnis in allen 3 Laeufen identisch: kein
`RuntimeError`, `stderr`-Log (per `Start-Process -RedirectStandardError`)
durchgehend 0 Byte ueber die gesamte Sitzung, Kopfzeile `108 of 212 relics
matching "attack"` deckt sich mit 109 sichtbaren Kartenwidgets (108 Treffer +
1 `Custom relic`-Platzhalter) in allen 3 Laeufen, Prozess durchgehend
`Responding=True`, `Rescan save` lief jedes Mal ohne Fehler durch. Zusaetzlich
der genannte Waechtertest gezielt: `test_relic_picker_advisor.py -k
does_not_lose_a_card_the_old_grid_had` -- 1 passed in 40,2 s.

**QA-277: behoben, am Artefakt bestaetigt.**

## 2 -- AK-299/QA-278 (Format `N 1H / N 2H`, Hervorhebung, Arsenal-Wrap)

Format deckungsgleich auf allen drei Stellen: Waffenkachel
(`Common · 59 1H / 61 2H AR`), Werteblatt (`Physical 56 1H / 58 2H +3 59 1H /
61 2H`, `Total ... (+6.0%)`), Arsenal-Kachel (`AR 75 1H / 77 2H`). 1H/2H-
Schalter (`HandSwitch`, UIA-`TogglePattern`) verschiebt die Fett-/Akzent-
Hervorhebung sofort auf allen drei Stellen ohne Kartenwechsel (Screenshot
vor/nach `qa278_before.png`/`qa278_after.png`). Arsenal-Kachel
(`CARD_WIDTH = 200`, `arsenaltab.py:15`) mit dem laengsten am Artefakt
gefundenen Fall (`Starscourge Greatsword`, Stufe 15: `275 1H / 213 2H`)
bleibt einzeilig, kein Clipping. Abweichung von der Auftragsbeschreibung: ich
beobachte **keinen** Zweizeiler, weder bei Stufe 1 noch bei Stufe 15 -- die
harte Anforderung "kein Clipping" haelt trotzdem, `right.setWordWrap(True)`
(`arsenaltab.py:177`) greift nur, wenn der Text tatsaechlich nicht passt, was
bei keinem getesteten Wert eintrat. Die eigentliche QA-278-Beschwerde
(Lesbarkeit der beiden Zahlen ohne Farbe/Fett fuer einen Laien bzw. ueber
UIA) war nicht Gegenstand dieser Pruefung -- ich habe nur die AK-299/AK-298-
Mechanik erneut bestaetigt, nicht die Register-Beschwerde selbst widerlegt.

**QA-278: Format/Hervorhebung bestaetigt, urspruengliche Beschwerde offen (nicht erneut geprueft).**

## 3 -- power-user-Ziel 3 (Ausschluss + Optimize + Why)

Slot 3 mit `Low HP` gefiltert: 16 von 212 Karten, 7 Textstellen nennen
"Improved Damage Negation at Low HP" (Kartenzeilen + Kopfzeile). Bullet einer
Kopie angeklickt (`MarkButton.Invoke()`, ein Klick) → alle 4 Vorkommen dieses
Effekts auf den sichtbaren Karten zeigen sofort durchgestrichenen Text
(Screenshot `dialog_shot.png`). `Optimize` (Maximise damage) durchlaufen
(`3 of 3 slots filled`), `Why` fuer Slot 3 geoeffnet: der Ausschluss fehlt
dort **nicht** -- ein eigener Abschnitt "Effects you've excluded: Improved
Damage Negation at Low HP" steht am Ende des Dialogs. Die im Auftrag
formulierte Erwartung ("Effekt fehlt in Why") bestaetigt sich damit nicht;
das Gegenteil ist der Fall. Nach Neustart des Artefakts (sauberer Stop +
Neustart derselben Umlenkung) bleibt der Ausschluss registry-seitig erhalten
(gleicher Screenshot-Befund erneut geprueft).

**Nicht reproduziert -- kein Befund.** Falls die Beschwerde aus einer aelteren
Artefaktversion stammt, ist sie zwischenzeitlich durch die "Effects you've
excluded"-Sektion adressiert; ich habe dafuer keinen Fix-Commit gezielt
gesucht (ausserhalb des Auftragsumfangs).

## 4 -- QA-276-Zellen und A18/A20-Persistenz (kurz)

QA-276: Arsenal-Suche `Twinblade` (Stufe 1, Wylder) liefert sechs Zellen,
alle mit exaktem 0,5x-Verhaeltnis 2H/1H (73→36, 82→41, 80→40, 67→33 x3,
Rundungsdifferenzen ≤1) -- deckt sich mit `TWINBLADE_TWO_HANDED_RATE = 0.5`.
Die im Auftrag genannte konkrete Zelle "108/54" wurde nicht wortgleich
gefunden (andere Stufe/Waffe als hier gewaehlt), die zugrundeliegende Regel
haelt aber unveraendert.

A18/A20: nach hartem Neustart des Artefakts (`Stop-Process -Force` +
Neustart, gleiche Umlenkung) bleiben Hand-Schalter (2H), das manuell gewaehlte
Relikt in Slot 3 (`Grand Luminous Scene`) und der Effekt-Ausschluss aus Punkt
3 erhalten; der Stufen-Regler faellt auf 1 zurueck. Deckt sich mit T-272s
bereits dokumentierter Einordnung ("Level/Waffenslot nicht [persistiert] --
als beabsichtigt eingeordnet") -- kein neuer Befund, nur Bestaetigung.

## Explorationsprotokoll

- QA-277: 3 vollstaendige Durchgaenge am Artefakt (Filter waehrend Fuellung +
  Sortwechsel + Rescan save), `stderr`-Log 0 Byte ueber die gesamte Sitzung
  (beide Artefaktstarts), plus gezielter Waechtertest (1 passed, 40,2 s).
- QA-278/AK-299: 2 Screenshots (Schalterzustand vor/nach) bei Stufe 1, 2
  Arsenal-Screenshots (Stufe 1 und Stufe 15, laengster Zahlwert).
- power-user Ziel 3: Filterlauf, Ausschluss-Klick, Optimize-Lauf, Why-Text
  vollstaendig gelesen (alle Textknoten der UIA-Baumstruktur), Neustart-
  Gegenprobe.
- QA-276: Arsenal-Suche, 6 Zellen gegengerechnet.
- A18/A20: ein Neustart-Zyklus, 4 Zustaende verglichen (Hand, Relikt,
  Ausschluss, Stufe).
- Bestehende Tests: nur der QA-277-Waechtertest gezielt ausgefuehrt (siehe
  Punkt 1); kein Volllauf -- der Auftrag ist ein enger Artefakt-Retest ohne
  Hinweis auf breitere Codeaenderung, Retest-Modus-Kriterium fuer "kein
  allgemeines Neutesten" greift.

## Offene Fragen

- QA-278 (Register): die urspruengliche Beschwerde (Lesbarkeit ohne Farbe)
  wurde durch diesen Auftrag nicht abgedeckt -- an ui-ux-designer/director,
  ob eine gezielte Nachpruefung noch fuer diesen Zyklus noetig ist.

## Nicht getestet

- Arsenal-Wrap bei Werten > 3-stellig (kein Weapon im Datensatz mit vierstelligen
  AR-Werten gefunden) -- die "zweizeilig"-Beschreibung aus dem Auftrag bleibt
  insofern ungeklaert, wann sie eintreten wuerde.
- Rot-vorher-Mutation fuer `_rescue_cached_cards()` selbst (nur der bereits
  vorhandene Waechtertest gegen den Fix-Stand gepruefft, kein eigener
  git-archive-Vergleich gegen den Vorzustand -- Punkt 1 stuetzt sich auf die
  Artefaktbeobachtung plus den benannten Test, nicht auf eine eigene
  Mutation).
- Volle Testsuite (siehe Explorationsprotokoll).

## QA-Log

Siehe `qa/findings.md` (QA-277, QA-278 angehaengt).

## Zusammenfassung (an director)

P1: 0 offen (QA-277 am Artefakt bestaetigt behoben). P2: 0. P3: 0 neu (QA-278
bleibt mit unveraendertem Status, kein Statuswechsel durch diesen Auftrag).
P4: 0.

**Gesamturteil: PASS** -- QA-277 (P1) ist am Artefakt 1.12.3 dreifach
reproduziert bestaetigt behoben, kein neuer P1/P2-Befund. QA-278 bleibt mit
seiner urspruenglichen, hier nicht erneut geprueften Kernbeschwerde offen
(P3, bereits bekannt, kein neues Risiko).
