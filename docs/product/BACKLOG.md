# Produkt-Backlog

## Warteschlange (freigegeben, noch nicht gebaut) - 0 von hoechstens 3
| ID | Titel | Freigegeben am |
|---|---|---|

## Vergleichsfeld - Stand 23.09.2026

Verglichen: **relics.pro** (Web + Desktop-App) · **Y4rd13 nightreign-relic-optimizer**
(Web, Handeingabe) · **nightreign-calculator** (Web) · **Nightreignwiki Relic Build
Simulator** (Web, Beta) · **slavone Relic Probability Calculator** (Web).
Nicht aufgenommen: alfizari Save-Editor und aliig/Nightreign-Relic-Planner (README
beschreibt einen Relikt-Editor, der den Spielstand schreibt - andere Aufgabe);
mobalytics Build Planner (HTTP 403, nicht pruefbar).

| Funktion | relics.pro | Y4rd13 | calculator | Wiki-Simulator | slavone | wir | Topf |
|---|---|---|---|---|---|---|---|
| Relikte aus dem eigenen Spielstand | unbekannt | nein (Handeingabe) | nein | nein | nein | ja | vorhanden |
| Optimierer ueber den eigenen Bestand | ja | ja | nein | nein | nein | ja | vorhanden |
| Pflicht-/Ausschluss-Effekte, Slot festhalten | unbekannt | ja | nein | nein | nein | ja | vorhanden |
| Stapelregeln geprueft | unbekannt | ja | unbekannt | teilweise (Warnungen) | nein | ja | vorhanden |
| Deep of Night | unbekannt | ja | ja | unbekannt | ja | ja | vorhanden |
| Gespeicherte Builds | ja | ja | ja | nein (nur Link) | nein | ja | vorhanden |
| Wuerfelchance je Effekt | unbekannt | nein | nein | nein | ja | ja | vorhanden |
| Build-Export/-Import (Datei oder Link) | ja | ja (JSON) | ja | ja (Link) | nein | nein | A Basis |
| Gesamt-Schadensreduktion je Schadensart | unbekannt | ja (Survival-Achse) | ja | nein | nein | teilweise (nur Aenderung) | A Basis |
| Bestes Gefaess ueber alle besessenen Gefaesse | unbekannt | unbekannt | nein | nein | nein | nein | B weisser Fleck |
| Neue Relikte seit letztem Scan gegen gespeicherte Builds | unbekannt | nein | nein | nein | nein | nein | B weisser Fleck |
| Seitenvergleich zweier Builds | unbekannt | ja | nein | nein | nein | nein | C Randfall |
| Nicht besessene, erreichbare Relikte vorschlagen | ja | nein | nein | nein | nein | teilweise (Custom relic) | C Randfall |
| Overlay im Spiel | ja | nein | nein | nein | nein | nein | C Randfall |
| Timer (Nachtzyklus, Status-Stack) | ja | nein | ja | nein | nein | nein | C Randfall |
| Talismane/Verbrauchsgueter in der Rechnung | unbekannt | unbekannt | ja | nein | nein | nein | C Randfall |
| Zufallswahl Nightfarer | nein | nein | ja | nein | nein | nein | C Randfall |
| Schaden gegen bestimmten Boss / Boss-Warnungen | unbekannt | nein | ja | ja | nein | nein | Nicht-Ziel (Nutzer 19.09.) |
| Doppelte/ueberfluessige Relikte erkennen | ja | nein | nein | nein | nein | nein | Nicht-Ziel (Nutzer 19.09.) |
| Gewichtete Mischziele (Regler) | unbekannt | ja | nein | nein | nein | nein | Nicht-Ziel (A7, OF-13) |
| Community-Builds, Abstimmung | ja | nein | ja | nein | nein | nein | Nicht-Ziel (Netzwerk) |
| Mehrsprachigkeit | ja | nein | unbekannt | unbekannt | nein | nein | Nicht-Ziel (GOAL) |

Topf "vorhanden": Zeile, in der wir die Funktion haben - kein Kandidat.
Topf "Nicht-Ziel": weisser Fleck oder Basis mit Warum-nicht-Antwort 3 bzw. vom
Nutzer verworfen - wird nicht vorgelegt.

Quellen, alle abgerufen 23.09.2026: https://relics.pro/ ·
https://github.com/Y4rd13/nightreign-relic-optimizer ·
https://nightreign-calculator.netlify.app/ ·
https://nightreignwiki.com/tools/relic-builder/ ·
https://slavone.github.io/nighreign_relic_calculator/ (nur Suchergebnis-Text) ·
https://github.com/aliig/Nightreign-Relic-Planner ·
https://mobalytics.gg/elden-ring-nightreign/planner/builds (403).
"wir": `docs/anleitung/guide.md` (Stand 23.09.2026). Unbekannt heisst unbekannt,
nicht nein.

## Lauf 1 - 23.09.2026 - Modus discover

### P-001 - Bestes Gefaess fuer den eigenen Bestand   [B weisser Fleck]
**Problem:** Wer einen Nightfarer mit mehreren Gefaessen spielt (eigene plus
Shared Grails; der Spielstand meldet z. B. "Loaded Revenant - 5 chalices",
T-322m), waehlt heute zuerst das Gefaess und laesst dann Optimize rechnen.
Welches Gefaess mit den eigenen Relikten das beste Ergebnis bringt, erfaehrt er
nur, indem er jedes einzeln oeffnet, Optimize drueckt und sich die Zahlen merkt.
Erkennbar daran, dass die Gefaesswahl vor der Rechnung steht, die sie
beantworten koennte.
**Vorschlag:** Der Berater beantwortet zusaetzlich die Frage "welches meiner
Gefaesse" fuer die gewaehlte Richtung: eine gereihte Liste der besessenen
Gefaesse mit ihrem Optimize-Ergebnis, von der aus man in das Gefaess samt
Vorschlaegen springt. Gehaltene Slots, Favourite/Avoid und Hit with/Damage type
gelten wie bei Optimize.
**Bei B - warum macht es niemand:** Antwort 1. Die Web-Werkzeuge kennen weder
die besessenen Gefaesse noch deren echte Slot-Farben (der Wiki-Simulator
schreibt selbst, die Layouts seien "not fully public"); nur ein Werkzeug, das
Spielstand und Spieldaten zugleich liest, kann die Frage stellen. Vorbehalt:
zwei Zellen der Tabelle sind unbekannt (relics.pro, Y4rd13).
**Abnahmekriterium:** Fuer den gewaehlten Nightfarer listet der Berater jedes
besessene Gefaess (eigene und Shared Grails, beim aktuellen Deep-of-Night-Stand)
mit dem Optimize-Ergebnis der gewaehlten Richtung, absteigend gereiht; ein Klick
auf einen Eintrag oeffnet dieses Gefaess mit genau den Vorschlaegen, die
Optimize dort liefert; das Fenster bleibt waehrend der Rechnung bedienbar
(A6-Messfall).
**Beleg:** Vergleichstabelle Zeile "Bestes Gefaess"; `guide.md` Abschnitt
Advisor (Optimize je geoeffnetem Gefaess); T-322m.
**Schnittgroesse:** ein Zyklus (Vorbehalt: Rechenbudget, offene Frage an
`architect`)
**Kosten und Risiko:** Ein neues A6-Budget fuer N Gefaesse statt eines;
Ergebnisse ueber Gefaesse sind nur vergleichbar, wenn alle dieselbe Richtung
und dieselben Filter tragen - jede kuenftige Beraterregel muss hier mitgedacht
werden.
**Status:** vorgeschlagen

### P-002 - Sicherung der eigenen Planungsdaten in eine Datei   [A Basis]
**Problem:** Gespeicherte Builds (rund 110 beim Nutzer), Favoriten,
Favourite/Avoid/Allow-Marker und versteckte Builds liegen nur in der Registry
unter `HKCU\Software\DankYeeter`. Ein Rechnerwechsel, eine Neuinstallation von
Windows oder ein Fehler im Schluesselraum loescht monatelange Planung ohne
Rueckweg. Erkennbar an den drei Datenverlusten im QSettings-Schluesselraum in
Zyklus 4 und 5 (GOAL.md, OF-15).
**Vorschlag:** Alles, was der Spieler selbst angelegt hat, laesst sich in eine
Datei sichern und aus ihr wiederherstellen. **Nicht** gemeint ist das Teilen
einzelner Builds mit anderen - das hat der Nutzer am 19.09. verworfen; er
entscheidet, ob die Sicherung davon getrennt genug ist.
**Bei A - vollstaendig heisst hier:** Sichern und Wiederherstellen beide; die
Datei enthaelt jeden gespeicherten Build samt 1H/2H und Custom relics, den
Versteckt-Zustand, Relikt-Favoriten je Nightfarer, alle Filter-Marker und die
zuletzt gewaehlte Richtung; Wiederherstellen ueberschreibt nichts still
(Namensgleichheit wird genannt); eine Sicherung aelterer Programmversion bleibt
lesbar oder sagt, warum nicht.
**Abnahmekriterium:** Sichern, Registry-Schluessel loeschen, Wiederherstellen
ergibt dieselbe Build-Liste (Anzahl, Namen, Slots, Hand, versteckt), dieselben
Favoriten und dieselben Marker wie vorher; auf einem zweiten Windows-Konto
ebenso.
**Beleg:** Vergleichstabelle Zeile "Build-Export/-Import" (4 von 5 Werkzeugen);
GOAL.md OF-15 (drei Datenverluste).
**Schnittgroesse:** ein Zyklus
**Kosten und Risiko:** Neue Dateisenke (Ausloeser `security-reviewer`); das
Dateiformat wird zur dauerhaften Pflicht - jede kuenftige Aenderung an Builds
oder Markern braucht eine Migration auch fuer Sicherungen. Naehe zum verworfenen
"Build teilen": eine Sicherungsdatei laesst sich weitergeben.
**Status:** vorgeschlagen

### P-003 - Gesamt-Schadensreduktion je Schadensart   [A Basis]
**Problem:** Wer "Minimise damage taken" waehlt, sieht, welches Relikt der
Berater vorschlaegt, aber nicht, wo er am Ende steht: der Abschnitt
Resistances zeigt laut Guide "changes, not totals". Ob ein Build gegen Feuer
40 % oder 12 % abhaelt, bleibt offen. Erkennbar daran, dass die defensive
Richtung eine Rangfolge ohne Zielgroesse liefert.
**Vorschlag:** Die Schadensreduktion je Schadensart und die Statusresistenzen
erscheinen wie Attribute: Grundwert des Nightfarers, Aenderung durch die
Relikte, Gesamtwert.
**Bei A - vollstaendig heisst hier:** jede Schadensart, die das Spiel fuehrt
(physisch samt Unterarten, falls die Daten sie trennen, und die vier Elemente),
plus Statusresistenzen; Grundwert, Aenderung, Summe; bedingte Effekte wie heute
nur per Schalter; wo der Grundwert nicht in den Dateien steht, sagt die Zeile
das (A7) - dann ist der Kandidat nur halb baubar und gehoert zurueckgestellt.
**Abnahmekriterium:** Fuer jeden der zehn Nightfarer zeigt das Werteblatt je
Schadensart Grundwert, Relikt-Aenderung und Gesamtwert; ein Relikt mit
"Improved Fire Damage Negation" hebt den Feuer-Gesamtwert um genau seinen
Betrag, und ein Messpunkt ingame bestaetigt einen Gesamtwert.
**Beleg:** Vergleichstabelle Zeile "Gesamt-Schadensreduktion" (Y4rd13,
calculator); `guide.md` Tabelle "Reading the right-hand panel".
**Schnittgroesse:** ein Zyklus (falls die Grundwerte extrahierbar sind)
**Kosten und Risiko:** Moegliche neue Extraktion (EXTRACT_VERSION steigt,
Testabzug wird ungueltig); die Stapelregel fuer Reduktion (multiplikativ oder
additiv) muss stimmen, sonst zeigt die Summe eine falsche Zahl mit dem Anschein
von Genauigkeit.
**Status:** vorgeschlagen

### P-004 - Neue Relikte gegen gespeicherte Builds pruefen   [B weisser Fleck]
**Problem:** Nach jeder Runde kommen Relikte dazu. Wer viele gespeicherte Builds
hat, weiss nach Rescan save nicht, ob eines der neuen Relikte einen davon
verbessert - er muesste jeden Build oeffnen und jeden Slot neu befragen. Der
Nutzer hat das Ausmisten am 19.09. mit "vlt. fehlt einem einfach das passende
relikt" verworfen; die Kehrseite ist die Frage "ist das passende jetzt da?".
**Vorschlag:** Nach einem Rescan nennt das Programm fuer den gewaehlten
Nightfarer die seit dem letzten Scan neuen Relikte, die in einem seiner
gespeicherten Builds einen Slot verbessern wuerden - mit Build, Slot und
Betrag.
**Bei B - warum macht es niemand:** Antwort 1. Web-Werkzeuge mit Handeingabe
kennen keinen "letzten Scan"; es braucht Spielstand, gespeicherte Builds und
die Grenzbeitragsrechnung zugleich. relics.pro-Zelle unbekannt.
**Abnahmekriterium:** Nach Rescan save mit mindestens einem neuen Relikt, das
in einem gespeicherten Build des gewaehlten Nightfarers einen Slot nach der
gewaehlten Richtung verbessert, nennt das Programm Build, Slot, Relikt und
Betrag; ohne solches Relikt sagt es, dass keines in Frage kommt; gespeicherte
Builds bleiben unveraendert.
**Beleg:** Vergleichstabelle Zeile "Neue Relikte seit letztem Scan"; GOAL.md
Nachtrag 19.09. (Zitat oben). Kein Usability-Befund - schwach belegt.
**Schnittgroesse:** mehrere Zyklen
**Kosten und Risiko:** Neuer persistenter Zustand ("zuletzt gesehener
Bestand") im Schluesselraum, gegen den OF-15 ausdruecklich argumentiert;
Handles werden beim Einschmelzen neu vergeben (AD-013), der Vergleich muss auf
dem Roll stehen. Gespeicherte Builds tragen keine Richtung - welche gilt, ist
eine Entwurfsfrage.
**Status:** vorgeschlagen

### Streichvorschlaege 1 - mindestens drei

**Was:** Die als community-reported markierten Inhalte - Deep-of-Night-Block
"What moves your rating" (`deeptab.py:419`), die COMMUNITY-REPORTED-Zeile in
Red variants (`depthstab.py:117`), die blauen Zeilen in World Events
(`eventstab.py:101`, `:335`), dazu die Zeile, auf die `bosstab.py:206`
verweist. Suche `community-reported|community reported`, ohne Gross/Klein,
`nrplanner/`: 6 Treffer in 4 Dateien, davon 4 Oberflaechentexte in 3 Dateien.
**Warum es nicht mehr traegt:** GOAL.md fuehrt "keine Wiki-Daten" als
Nicht-Ziel, und die Hausregel des Programms ist "every value comes from the game
files". Beschriftet ist es - aber beschriftete Gemeindewerte sind trotzdem
Gemeindewerte, und sie sind die einzigen Zahlen im Programm, die bei einem
Spielpatch niemand nachziehen kann.
**Was der Verzicht kostet:** Der Rating-Block beantwortet eine echte Frage
("was kostet mich eine Niederlage"), und die Dateien geben ihn nicht her; er
fiele ersatzlos weg. `docs/legal/C-002.md` hat die Stellen gesehen und nicht
beanstandet - der Widerspruch ist einer zum Zielbild, kein Rechtsbefund.

**Was:** Die Why-Zeile "it depends on the armaments you carry, so no number
here" (`nrplanner/advisor/explain.py:635`, Fuellung (c)).
**Warum es nicht mehr traegt:** GOAL.md A17 hat die Frage selbst offen gelassen:
die Zeile ist wahr, raet aber zu etwas, das in der Runde nicht in der Hand des
Spielers liegt, weil Waffen ausgewuerfelt werden. Die A17-Zahl (38 Zeilen auf
dem Spielstand des Nutzers) ist vom 07.09. und hier nicht nachgezaehlt.
**Was der Verzicht kostet:** Der Spieler erfaehrt nicht mehr, *warum* ein
Effekt keine Zahl hat; er faellt in die allgemeine Zeile "no number here shows
what this adds". Wer gezielt eine Waffengattung spielt, verliert einen Hinweis.

**Was:** Abnahmekriterium A11, Nachweisweg "power-user-Berichte".
**Warum es nicht mehr traegt:** A11 steht seit dem 15.09. auf "teilweise", weil
der automatisierte Laie wiederholt an Klicks scheitert, die mit echter Maus
gehen (T-275, T-285b, QA-282); drei Laeufe ohne belastbares Ergebnis. Der
Freundestest liegt schon beim Nutzer (state.md, "Beim Nutzer" Punkt 3). Das
Kriterium misst so eher das Werkzeug als das Programm.
**Was der Verzicht kostet:** Es gibt dann keinen wiederholbaren Laientest mehr
je Release; ein Freundestest ist einmalig und haengt an einer Person. Die
Aenderung an GOAL.md uebertraegt nur der `director` nach Freigabe.

### Bewusst nicht vorgeschlagen (Topf C)
- Seitenvergleich zweier Builds - Y4rd13 (Compare-Tab); nur ein Werkzeug, heute ueber die Build-Liste per Umschalten loesbar.
- Nicht besessene, erreichbare Relikte vorschlagen - relics.pro; "Custom relic" deckt das Planen um Fehlendes, Wuerfelchance dazu waere ein eigener Lauf.
- Overlay im Spiel - relics.pro; nahe am Nicht-Ziel "kein Eingriff in laufende Spielprozesse".
- Timer fuer Nachtzyklus/Status-Stack - relics.pro, calculator; Werkzeug fuer waehrend der Runde, dieses Programm plant davor.
- Talismane/Verbrauchsgueter in der Rechnung - calculator; in der Runde ausgewuerfelt, gleiche Begruendung wie A17.
- Zufallswahl Nightfarer - calculator; kein Planungsproblem.

### Empfehlung
**Platz eins: P-001** - es verlaengert die fertige Optimize-Rechnung auf die
Entscheidung, die heute vor ihr steht, braucht keinen neuen persistenten
Zustand und kann nur ein Werkzeug liefern, das Spielstand und Spieldaten liest.

Offene Fragen vor einer Freigabe:
- `architect` (P-001): Passt "Optimize ueber alle Gefaesse eines Nightfarers"
  in ein A6-Budget, und welches Budget gilt dafuer?
- `researcher` (P-001, P-004): Bieten relics.pro (Desktop-App) oder Y4rd13 eine
  Gefaesswahl bzw. einen Scan-Vergleich? Beide Zellen sind unbekannt.
- `researcher` (P-003): Stehen Grundwerte der Schadensreduktion je Nightfarer
  in den Spieldaten, und wie stapelt das Spiel Reduktionen?
- `architect` (P-004): Wie haelt man "zuletzt gesehenen Bestand" ohne den
  Schluesselraum-Risiken aus OF-15?

Nebenfund (nicht Teil dieses Laufs, an `technical-writer`): `guide.md:778`
"Spell damage is unavailable - no such field exists in the data" widerspricht
A26/A27 und dem Abschnitt "Weapon art and Spell damage" derselben Datei.
