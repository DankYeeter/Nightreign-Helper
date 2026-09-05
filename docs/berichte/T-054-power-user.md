# T-054 — power-user

> **Ablage durch den Director, 2026-09-05.** Der `power-user` hat seinen
> Bericht vollstaendig geliefert, aber nicht auf Platte geschrieben; die
> Ablage der Berichte von Rollen ohne Write-Recht ist ohnehin Aufgabe des
> Directors. Der Text unten ist **unveraendert** der Bericht des Agenten.
> Aufgefallen ist die fehlende Datei dem `ui-ux-designer` in T-056, der sie
> als "wichtigste Quelle" lesen sollte und stattdessen vier unabhaengige
> Suchen durchgefuehrt hat. **Folge, die bestehen bleibt:** seine Vorgaben
> stuetzen sich nirgends allein auf diesen Bericht, und A11 gilt weiterhin
> als nicht nachgewiesen.

```
STATUS: teilweise
AUFTRAG: T-054 - Power-User-Sitzung Referenz-Tabs (Effekte, Waffen,
         Nachtlords, Deep of Night, rote Varianten, Weltereignisse)
GELESEN: bewusst nichts - nur der Auftragstext (die README.md des Programms
         wurde waehrend der Sitzung als sichtbare Anleitung geoeffnet)
GEAENDERT: keine Projektdateien. Beim ersten Start hat das Programm laut
         eigener README vermutlich %LOCALAPPDATA%\NightreignHelper und einen
         Registry-Schluessel unter HKCU\Software\DankYeeter angelegt - selbst
         nicht eingesehen. Der gestartete Python-Prozess wurde am Ende nicht
         beendet.
ANNAHMEN: "mein Charakter" = der beim Programmstart vorausgewaehlte Nightfarer
         (Wylder, Stufe 1), da der Build-Planner-Tab ausgeklammert war. Als
         "ein bestimmter Nachtlord" nahm ich den zufaellig angeklickten
         (Fulghor), weil ich Portraits nicht sehen und daher keinen gezielt
         auswaehlen konnte.
NAECHSTER: director
BLOCKIERT DURCH: nichts - alle sechs Aufgaben liessen sich mit einer
         Ersatzmethode bearbeiten
```

## Wichtiger technischer Hinweis vorab

Mir standen in dieser Sitzung keine Werkzeuge zur Verfuegung, um den
Bildschirm zu sehen oder mit Maus/Tastatur wie ein normaler Spieler zu
klicken (kein Screenshot-Tool, kein Bildbetrachter war zugelassen). Ich habe
das Programm stattdessen ueber die Windows-Bedienungshilfen-Schnittstelle
"gelesen" (das, was auch ein Screenreader nutzen wuerde) und blind auf
Bildschirmkoordinaten geklickt, deren Wirkung ich anschliessend wieder ueber
dieselbe Schnittstelle als Text ablesen konnte. Das ist kein Blick in den
Quellcode — ich habe ausschliesslich das gelesen, was auf dem Bildschirm
sichtbar war, nur eben als Text statt als Bild. Es bedeutet aber: zu Bildern,
Icons, Farben und Portraits kann ich nichts sagen, weil ich sie nie gesehen
habe. Das ist eine Einschraenkung meiner Sitzung, keine Beobachtung ueber das
Programm selbst.

Die README.md musste ich lesen, um ueberhaupt herauszufinden, wie das Fenster
aufgebaut ist (Namen der Registerkarten) — ein normaler Spieler mit Augen
haette das nicht gebraucht. Das ist meiner Werkzeug-Einschraenkung
geschuldet, nicht der App.

## Erwartung vorher

Ich habe erwartet, dass die sechs Referenz-Tabs schnell ueber die
Registerkarten oben zu finden sind und dass jede Tabelle in normaler
Spielersprache beschriftet ist. Ich kenne die Begriffe "Relikt", "Nachtlord",
"Deep of Night", "rote Variante" und "Weltereignis" aus dem Spiel selbst,
aber nicht, wie eine Chance oder ein Multiplikator berechnet wird — das
wollte ich einfach nur ablesen koennen, ohne selbst zu rechnen.

## Aufgaben-Ergebnis

| Aufgabe | Ergebnis | Schritte | Zeitgefuehl |
|---|---|---|---|
| 1. Relikt-Effekte & Chancen | geschafft | 2 | schnell, ca. 2 Min |
| 2. Zwei Waffen vergleichen | mit Muehe | 4 | mittel, ca. 5 Min |
| 3. Vorbereitung auf einen Nachtlord | mit Muehe | 3 | schnell im Ablauf, aber ohne gezielte Auswahl |
| 4. Deep of Night | geschafft | 2 | schnell, ca. 2 Min |
| 5. Rote Varianten | teilweise | 2 | schnell, Kernfrage nur halb beantwortet |
| 6. Weltereignisse | geschafft | 3 | schnell, ca. 2 Min |

## Ablauf je Aufgabe

**1. Relikt-Effekte & Chancen.** Tab "Effects & chances" geoeffnet. Sofort
eine grosse Tabelle mit 577 Buffs und 75 Curses, dazu ein Erklaertext direkt
darueber. Ich sah z. B.: "Vigor +3" hat 2,2 % durchschnittliche und 100 %
beste Chance, "Wraiths While Walking" nur 0,20 %. Beantwortet meine Frage
vollstaendig.

Nicht verstanden: die Spalte "Pools" zeigt bei manchen Effekten Werte wie
864, 240 oder 1105, bei anderen nur 6 oder 1. Ich habe keine Ahnung, was
diese Zahl konkret bedeutet — eine Zahl wie 864 als "Pools" wirkt riesig fuer
etwas, das ich mir als "Ziehtoepfe" vorstelle. Geraten habe ich, dass es eine
interne Zaehlgroesse ist, sicher bin ich nicht. Auch die Spalte "Tier" war
fast immer leer und nur bei wenigen Effekten mit "1 of 2"/"2 of 2" gefuellt —
ohne den Erklaertext darueber haette ich das nicht verstanden.

**2. Zwei Waffen vergleichen.** Tab "Weapons & spells" geoeffnet, oben stand
"Wylder at level 1 ... 1952 shown". Ohne Suchbegriff war fuer mich zunaechst
nichts Konkretes greifbar. Erst nach Eingabe von "Zweihander" ins Suchfeld
wurden Kachelinhalte fuer mich lesbar: Zweihander AR 73 (rein physisch),
Feuer-Variante AR 71 (36 physisch + 35 Feuer), Blitz-Variante ebenfalls
AR 71, dazu Cold Zweihander (AR 58, 29 physisch + 28 Magie + 68
Frost-Aufbau), Poison Zweihander (AR 66) und Blood Zweihander (AR 66). Damit
konnte ich zwei Waffen (Standard- vs. Cold-Zweihander) nach Angriffswert und
Skalierung vergleichen.

Stoerend: bei den ersten fuenf Kacheln (Grundinfusionen: Standard, Feuer,
Blitz, Heilig, Magie) stand kein Name ueber der Kachel, nur "AR 73" bzw.
"AR 71" direkt untereinander. Ich musste raten, dass die erste Spalte die
unveraenderte Waffe ist, aus der Reihenfolge und dem "vs standard"-Hinweis
daneben.

**3. Vorbereitung auf einen Nachtlord.** Tab "Nightlords" geoeffnet —
Beschreibungstext "10 Nightlords ... click a card for damage taken, status
buildup and more". Da ich Portraits nicht sehen konnte, klickte ich blind auf
die erste Kachel und bekam Fulghor. Das Detailfeld war sehr ausfuehrlich:
"WEAKNESS SPECIAL INTERACTION - Pile on Lightning damage. It builds a hidden
meter, and filling it breaks the boss's stance and opens it up for a
critical." Dazu Schadensverlauf pro Element (Holy x0.7, Lightning x1.2, Rest
x1), Status-Aufbau (154 bei den meisten, Madness "immune"), Stand-Balken
("Bar to break 155", "Refills at x1.385", "9 of 10 for bar size") und
Selbst-Buff ("x1.25 attack, stacks - repeats compound"). Beantwortet meine
Frage vollstaendig — vorausgesetzt ich haette den Boss gezielt waehlen
koennen. Das eigentliche Problem hier liegt an meiner Sitzung (kein
Bildschirm), nicht sicher am Programm — ein sehender Spieler haette das
Portrait erkannt.

**4. Deep of Night.** Vier klar ueberschriebene Tabellen direkt sichtbar:
"WHAT EACH DEPTH IS WORTH" (Rating-Schwelle, Belohnungsmultiplikator x1.47
bis x2.41, Sovereign-Sigil-Anzahl, Relikt-Stufe je Tiefe), "HOW MUCH TOUGHER
ENEMIES GET" (Gegner-HP/-Angriff je Tiefe mit Spanne), "WHAT MOVES YOUR
RATING" (Gewinn +200, Verlust je nach Tiefe/Tag) und "WHAT ELSE CHANGES WITH
DEPTH" (Cataclysm-Chance, verdeckte Karte/Boss, verfluchte Relikte). Jede
Tabelle mit Erklaersatz darunter, inklusive ehrlicher Kennzeichnung, was
"community-reported" vs. aus dem Spiel gelesen ist. Klarste Ansicht der
ganzen Sitzung.

**5. Rote Varianten.** Tabelle mit Zeilen "Ordinary enemies", "Named field
enemies & minibosses", "Evergaol bosses", "Night bosses (unconfirmed)",
"Merchants", "Unidentified enemies" und Summenzeile, je Spalte pro Tiefe 1-5.
Ich konnte ablesen, wie viele rote Gegner es gibt und dass Evergaol-/
Nachtboss-Varianten erst ab Tiefe 2 dazukommen. Nicht gefunden: eine Angabe,
um wie viel staerker (HP/Schaden) eine rote Variante gegenueber der normalen
Version desselben Gegners ist — nur Stueckzahlen, nicht was inhaltlich anders
ist. Das war der Kern meiner Frage und blieb unbeantwortet. Die Zeile
"Unidentified enemies" (1 bei Tiefe 1, 2 ab Tiefe 2) habe ich mir angesehen
und dann ignoriert, weil nirgends erklaert wurde, was damit gemeint ist.

**6. Weltereignisse.** Liste mit 15 Ereignissen. Erstes angeklickt ("Fell
Omen / Morgott Invasion"): "Announced as 'A Fell Omen arrives'",
Prozentangaben pro Nachtlord ("Adel 18% · Gnoster 10% · ..."), "WHAT
HAPPENS", "WIN" (z. B. "+2% attack power ... up to +10 stacks", "Runes:
3,750-7,500 base") und "LOSE" ("+20% damage taken ... for the rest of the
expedition"). Zweitklarste Ansicht nach Deep of Night.

## Abbruchpunkte

Kein vollstaendiger Abbruch. Bei Aufgabe 5 habe ich nach der Tabelle keine
weitere Stelle gefunden, die beantwortet, was sich an einer roten Variante
inhaltlich aendert (nicht nur wo/wie viele) — ich habe die ganze sichtbare
Tabelle gelesen, die Antwort war schlicht nicht da.

## Falsche Erwartungen

Bei "rote Varianten" hatte ich erwartet zu erfahren, WARUM sie gefaehrlicher
sind (staerker, mehr Leben o. ae.), bekam aber nur WO und WIE VIELE es gibt.

## Was gut lief

- Effekte-Tabelle, Deep-of-Night-Tabellen und Weltereignis-Liste waren
  durchgehend in klarer Spielersprache beschriftet, mit erklaerenden Saetzen
  direkt bei den Zahlen statt nackten Werten.
- Ehrliche Kennzeichnung, welche Zahlen "confirmed in game" und welche
  "community-reported" sind — schafft Vertrauen.
- Waffenkacheln zeigten "vs standard: STR -9 · FAI +29 · DEX -4" — genau das,
  was ich zum Abwaegen einer Infusion brauche, ohne selbst zu rechnen.
- Der Nachtlord-Text erklaerte den Stance-Mechanismus in einem Satz, den ich
  sofort verstanden habe, obwohl mir vorher nie klar war, wie "Stance
  brechen" genau funktioniert.

## Nicht erreicht

Ich konnte bei den Nightlords-Kacheln keinen selbst gewaehlten Nachtlord
gezielt ansteuern — reines Zufallsergebnis durch blindes Klicken. Ob die App
selbst (Tooltip, Titel vor dem Klick) einen Namen zusaetzlich zum Portrait
anbietet, konnte ich nicht pruefen, weil ich das Portrait nicht sehen konnte.
Das sollte jemand mit echter Bildschirmansicht nachpruefen.

## Meine drei groessten Aergernisse

1. Bei "rote Varianten" nur Stueckzahlen bekommen, aber keine Antwort auf die
   Kernfrage, was an einer roten Variante inhaltlich anders ist als an der
   normalen Version desselben Gegners.
2. In der Effekte-Tabelle die Spalte "Pools" mit Zahlen wie 864 oder 1105 —
   ich konnte mir nicht erschliessen, was diese Zahl fuer mich als Spieler
   bedeutet.
3. Bei den Waffenkacheln standen die ersten fuenf Eintraege (Grundinfusionen)
   als reine Zahlen ("AR 73", "AR 71") ohne Namen direkt daran — ich musste
   mir aus der Reihenfolge zusammenreimen, welche Zahl zu welcher
   Waffe/Infusion gehoert.

## Abschluss

Von den sechs Bereichen war "Deep of Night" fuer mich am nuetzlichsten (vier
klare, sofort verstaendliche Tabellen mit ehrlicher Kennzeichnung der
Datenherkunft), am ueberfluessigsten wirkte fuer mich in dieser Sitzung "rote
Varianten" — nicht weil die Zahlen falsch waeren, sondern weil sie meine
eigentliche Frage nicht trafen. Ich wuerde das Programm einem Mitspieler
empfehlen, mit dem Hinweis, dass man bei den Effekt- und Waffenlisten
notfalls die Suche benutzen sollte, statt in der vollen Liste zu blaettern.
