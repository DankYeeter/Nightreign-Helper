# T-115 - Siebter Durchgang, erstmals am gebauten Artefakt (power-user)

*Vom Director aus der Rueckmeldung des Laufs abgelegt, unveraendert. Der
`power-user` hat Schreibrecht und haette den Bericht selbst schreiben sollen;
sein Kontrakt sagt `GEAENDERT: keine Projektdateien`, die Datei existierte
nicht. **Befund fuer die `retrospective`.***

STATUS: erledigt
AUFTRAG: T-115 — Power-User-Test des Relikt-Build-Planers (NightreignHelper.exe)
GELESEN: bewusst nichts — nur der Auftragstext
GEAENDERT: keine Projektdateien. Nutzerdaten des Testlaufs liegen unter
`…\scratchpad\T-115\local` und `…\T-115\roaming` (isolierte Einstellungs- und
Konfigurationsordner, wie im Auftrag vorgegeben — dort liegt jetzt mein
gespeicherter Zustand: Startmenue-Haken gesetzt, ein Relikt-Slot testweise
belegt, Advisor-Vorschlag uebernommen).
ANNAHMEN: Ich habe angenommen, dass "meine Waffen" (Aufgabe 5) sich auf die
riesige Waffenliste im Reiter "Weapons & spells" bezieht, da ich keinen
separaten Filter fuer "nur besessene Waffen" gefunden habe — siehe Befund
dort. Technischer Zusatz: Meine Maus-Klicks ueber PowerShell trafen zunaechst
systematisch daneben, weil meine Automatisierungs-Shell nicht "DPI-aware" war
(Bildschirm laeuft mit 150 % Skalierung) — das ist ein Problem meines
Testwerkzeugs, nicht des Programms, und ich habe es vor der eigentlichen
Schritt-0-Pruefung erkannt und behoben, bevor ich eine echte Aussage ueber
ankommende Klicks getroffen habe.
NAECHSTER: director
BLOCKIERT DURCH: nichts

---

## Persona und Erwartung

Ich spiele Elden Ring Nightreign regelmaessig, kenne Nightfarer, Relikte,
Kelche und "Tiefe der Nacht" aus dem Spiel selbst, bin aber kein Programmierer.
Ich habe erwartet: Programm starten, kurz warten (laut Hinweis "eine Minute"),
dann sehe ich meinen Spielstand als Zahlen — Level, Attribute, vielleicht eine
Relikt-Liste. Fuer den ersten Start habe ich mit ein bis zwei Minuten
gerechnet.

## Schritt 0 — Faehigkeitsprobe

Bestanden, aber mit einer Komplikation: Meine ersten beiden Klicks auf eine
Checkbox kamen nachweislich nicht an (Zustand blieb unveraendert, obwohl
Cursor exakt auf dem Element sass). Ursache war eine Verzerrung zwischen den
Koordinaten, die mir das Programm fuer seine Bedienelemente meldete, und den
Koordinaten, an die mein Mauszeiger tatsaechlich gesetzt wurde
(Bildschirmskalierung). Nach Korrektur dieser Einstellung kam derselbe Klick
zuverlaessig an (Checkbox-Zustand aenderte sich sofort). Das ist eine
Einschraenkung meines Testwegs, keine Beobachtung ueber das Programm — ich
nenne sie trotzdem, damit klar ist, dass alle folgenden Klicks tatsaechlich
ankamen.

## Aufgaben-Ergebnis

| Aufgabe | Ergebnis | Schritte | Zeitgefuehl |
|---|---|---|---|
| 1. Ersteinrichtung, eigene Zahlen sehen | geschafft | Start + Warten | Setup dauerte ca. 107 Sekunden, danach sofort meine Werte sichtbar |
| 2. Relikte: welche und wie viele | mit Muehe | ca. 6 | zunaechst nur Teilzahlen gefunden, echte Gesamtzahl erst nach Neustart sichtbar |
| 3. Relikt tauschen, spuere ich Unterschied | geschafft | 4 | wenige Sekunden, Zahl direkt sichtbar |
| 4. Advisor-Vorschlag uebernehmen | geschafft | 3 | wenige Sekunden |
| 5. Haertester Waffentreffer | mit Muehe / Befund | mehrere Scroll-Versuche | lange, ohne befriedigendes Ergebnis |
| 6. Neustart, alles noch da? | geschafft (mit ueberraschendem Ergebnis: nein) | 2 | Neustart brauchte ungefragt ca. 49 Sekunden |

## Ablauf je Aufgabe

**Aufgabe 1 — Ersteinrichtung.** Programm gestartet. Fenstertitel zunaechst
"NightreignHelper", Text "Setting up Nightreign Helper — Reading your
installation. This happens once, and takes about a minute." mit
Fortschrittsbalken (ohne Prozentzahl, nur "laeuft"). Darunter wechselnde
Statuszeilen: "Decoding artwork ...", "portraits: 10", "item icons: 713 of 786
requested", "verification: every written icon reads back", "DLC illustrations
found: 12". Nach ca. 107 Sekunden erschien das eigentliche Programmfenster mit
Titel "Nightreign Helper 1.8.0". Sofort sichtbar: mein Nightfarer "Wylder",
Level 1, Attribute (Vigor 8, Mind 4, Endurance 3, Strength 5, Dexterity 4,
Intelligence 2, Faith 2, Arcane 10), HP 240 Basis / +40 durch Relikte / 280
gesamt. Ein Satz stand da: "Loaded Wylder — 5 chalices, showing the equipped
Wylder's Goblet with 2 relics." Ich wusste zu keinem Zeitpunkt, ob das Programm
haengt — die wechselnden Texte waehrend des Wartens haben mir das genommen.
Ziel erreicht, Zahlen kamen erkennbar aus meinem Spielstand.

**Aufgabe 2 — Relikte, welche und wie viele.** Ich oeffnete die drei
Relikt-Slots per Doppelklick/Klick. Jeder Slot zeigte eine Farbe und eine Zahl,
z. B. "Slot 1 — Yellow (54 available)", "Slot 2 — Green (48 available)",
"Slot 3 — Green (49 available)". Das wirkte zunaechst wie "ich habe 54, 48 und
49 Relikte", aber das sind offensichtlich nur die zur jeweiligen Slot-Farbe
passenden Relikte, keine Gesamtzahl — und die drei Zahlen zusammenzuzaehlen
waere falsch, weil sich Relikte ueber mehrere Slot-Farben eignen koennen. Ich
habe im Reiter "Effects & chances" nach einer Gesamtzahl gesucht und dort nur
eine spielweite Statistik gefunden ("577 buffs, 75 curses" — das sind moegliche
Effekte im Spiel, nicht meine Relikte). Erst nach dem Neustart (Aufgabe 6) fand
ich beilaeufig die tatsaechliche Antwort: der Satz "309 relics in USER_DATA000,
110 stored builds" stand ploetzlich an der Stelle, wo vorher der "Loaded
Wylder ..."-Satz stand. Also: ich besitze 309 Relikte. Aber ich habe dafuer
zufaellig neu starten muessen — beim ersten Durchlauf habe ich diese Zahl
nirgends gefunden, obwohl ich aktiv danach gesucht habe.

**Aufgabe 3 — Relikt tauschen fuer mehr Ueberleben.** Slot 2 war leer. Ich
oeffnete den Picker, tippte "Vigor" in das Filterfeld, bekam "5 of 48 relics
matching 'Vigor'" und waehlte den ersten Treffer "Blessed Iron Coin". Sofort
danach: HP von 280 auf 340 gestiegen (Anzeige zeigte "240 | +100 | 340" statt
vorher "240 | +40 | 280"), Vigor von 10 auf 13. Das war eindeutig — ich sehe
die Zahl direkt vor und nach dem Tausch nebeneinander, kein Raetselraten
noetig.

**Aufgabe 4 — Advisor-Vorschlag uebernehmen.** Ich klickte "Optimize". Nach
kurzer Zeit erschien fuer jeden Slot ein Vorschlag mit Etikett "SUGGESTED —
MAXIMISE DAMAGE" (das Ziel "Maximise damage" stand schon vorausgewaehlt in
einem Dropdown, ich hatte es nicht bewusst gesetzt). Zu jedem Vorschlag stand
eine Begruendung, z. B. "2 of its 3 effects moved a number in this build" mit
konkreter Auflistung ("Strength +2: Strength +2", "Dexterity +3: Dexterity
+3"). Das habe ich verstanden — es zeigt, welche Effekte bei mir tatsaechlich
etwas veraendern und welche "leerlaufen". Ich klickte "Apply all", und alle
drei Slots zeigten danach "Already equipped — nothing to change here."
Uebernahme erfolgreich und nachvollziehbar begruendet.

**Aufgabe 5 — Haertester Waffentreffer.** Ich wechselte zum Reiter "Weapons &
spells". Ueberschrift: "WHICH ARMAMENT HITS HARDEST FOR YOUR BUILD".
Untertitel verriet: "Every armament and spell in the game ... 1952 shown." Das
ist die gesamte Waffenliste des Spiels, nicht erkennbar auf meinen
tatsaechlichen Besitz eingegrenzt — ich habe keinen Schalter wie "nur meine
Waffen" oder "nur was ich gefunden habe" gefunden. Ich habe ferner keine
Sortierung nach Angriffswert (AR) gefunden — keine anklickbare
Spaltenueberschrift, kein "Sort by"-Feld wie im Relikt-Picker. Die Liste ist
nach Waffenfamilien gruppiert (z. B. Icerind Hatchet und alle Elementvarianten
zusammen, dann Rosus Axe, dann Sacrificial Axe usw.), die AR-Werte springen
dabei staendig hoch und runter (81, 68, 94, 99, 91, 91, 90 ...). Beim
Durchscrollen sah ich unter anderem "Ripple Blade" mit AR 110 — den hoechsten
Wert, den ich selbst gesehen habe. Ob das wirklich die hoechste Zahl unter
allen 1952 Eintraegen ist, weiss ich nicht — ich hatte keine Moeglichkeit, das
zu pruefen, ohne die komplette Liste von Hand durchzuscrollen. Meine
eigentliche, direkt ausgeruestete Waffe stand uebrigens am Anfang von Aufgabe 1
als "Wylder's Greatsword — Common · 56 AR" im Bereich "Weapon Damage" — falls
das gemeint war mit "meine Waffe", ist die Zahl 56 (Angriffswert der aktuell
ausgeruesteten Waffe).

**Aufgabe 6 — Neustart, alles noch da?** Ich schloss das Fenster
(Schliessen-Nachricht an das Hauptfenster). Ohne dass ich irgendetwas erneut
gestartet haette, erschien kurz danach von selbst ein neues Fenster mit dem
Text "Refreshing your game data — Re-reading your installation so the numbers
are up to date." Das dauerte etwa 49 Sekunden, danach war ich wieder im
Hauptfenster. Ich hatte nicht erwartet, dass sich das Programm nach dem
Schliessen selbst neu einliest, ohne dass ich es erneut gestartet habe — das
war fuer mich der ueberraschendste Moment der ganzen Sitzung. Wichtiger: Als
ich danach die Relikt-Slots ansah, waren es nicht mehr meine drei Relikte aus
Aufgabe 3 und 4 (die gelb/gruenen Slots mit Staerke-, Geschick- und
Ausdauer-Effekten) — stattdessen standen dort drei rote Slots mit voellig
anderen Effekten ("Ultimate Art Auto Charge", "Hoarfrost Stomp" usw.). Der
"Build"-Auswahlkasten stand auf "Equipped in game" statt auf einem
gespeicherten Namen — ich hatte meine Aenderungen aus Aufgabe 3 und 4 nie ueber
den "Save"-Knopf gesichert, nur direkt im Picker ausgewaehlt bzw. "Apply all"
geklickt. Ergebnis: nein, es war nicht mehr so, wie ich es verlassen hatte. Ob
das am fehlenden Speichern lag oder am automatischen Neu-Einlesen, kann ich
nicht sicher sagen — ich weiss nur, dass meine sichtbare Arbeit weg war.

## Abbruchpunkte

Keine vollstaendigen Abbrueche. Bei Aufgabe 5 habe ich nach mehreren
erfolglosen Versuchen (Tastatur-Bildlauf, Mausrad, Suche nach Sortierung)
aufgehoert, die komplette Liste manuell durchzuscrollen, und stattdessen den
besten selbst gesichteten Wert gemeldet — das grenze ich klar als unsicheres
Ergebnis ab.

## Falsche Erwartungen

- Ich dachte, "wie viele Relikte besitze ich" waere eine einzelne, leicht
  auffindbare Zahl direkt auf dem Hauptbildschirm. Stattdessen fand ich
  zunaechst nur Teilzahlen pro Slot-Farbe, die Gesamtzahl kam zufaellig erst
  nach einem Neustart zum Vorschein.
- Ich dachte, "Schliessen und wieder oeffnen" sei zwei Handlungen, die ich
  beide selbst ausloese. Tatsaechlich schien das Schliessen einen automatischen
  Neustart mit erneutem Daten-Einlesen auszuloesen, bevor ich selbst wieder
  etwas gestartet habe.
- Ich dachte, meine im laufenden Programm vorgenommenen Relikt-Aenderungen
  waeren "mein aktueller Zustand" und wuerden beim Neustart wieder da sein. Sie
  waren es nicht, ohne dass mir irgendwo gesagt wurde, dass ich vorher haette
  speichern muessen.

## Was gut lief

- Die Zahlen zu Attributen und HP waren bei jedem Relikt-Wechsel sofort
  sichtbar aktualisiert, mit klarem Vorher/Nachher (z. B. "240 | +100 | 340").
- Der Advisor-Vorschlag war nicht nur eine Auswahl, sondern kam mit einer fuer
  mich verstaendlichen Begruendung, welche Werte sich dadurch bei mir konkret
  aendern.
- Das Filtern im Relikt-Picker per Textsuche (z. B. "Vigor") funktionierte
  sofort und zuverlaessig.
- Waehrend des ersten Setups gab es durchgehend wechselnden Text, wodurch ich
  nie den Eindruck hatte, das Programm sei eingefroren.

## Nicht erreicht

- Eine verlaessliche, einzelne Zahl "das ist meine haerteste Waffe" konnte ich
  nicht mit Sicherheit ermitteln — nur den besten selbst gesehenen Wert
  (Ripple Blade, 110 AR) aus einer 1952 Eintraege umfassenden, ungefilterten
  Liste.
- Ich konnte nicht pruefen, ob es einen Weg gibt, die Relikt-Aenderungen so zu
  sichern, dass sie einen Neustart ueberleben (z. B. ueber den "Save"-Knopf),
  da das nicht Teil meiner Aufgabenliste war und ich nach dem ueberraschenden
  Datenverlust nicht mehr zurueck zum urspruenglichen Stand konnte.

## Meine drei groessten Aergernisse

1. Nach dem Schliessen des Programms war meine Arbeit (die getauschten und vom
   Advisor uebernommenen Relikte) verschwunden, ohne dass mir irgendwann gesagt
   wurde, dass ich das haette sichern muessen.
2. Das Schliessen loeste ohne mein Zutun einen erneuten, fast einminuetigen
   Einlese-Vorgang aus — ich wollte nur zumachen, nicht neu einlesen.
3. Bei der Frage "was ist meine haerteste Waffe" wurde ich mit 1952
   unsortierten Eintraegen allein gelassen, ohne Sortierung oder Eingrenzung
   auf das, was ich tatsaechlich besitze.
