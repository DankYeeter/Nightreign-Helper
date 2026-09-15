# T-069 — power-user (vierter Lauf, nach T-068)

> **Ablage durch den Director, 2026-09-06.** Der Agent kann in seinem Profil
> keine Dateien schreiben; der Text unten ist sein Bericht unveraendert.
> Reihe: `T-054` · `T-061` (abgebrochen) · `T-063` · `T-066` · dieser.
>
> **Director-Vermerk:** dieser Lauf ist an zwei Stellen **schlechter** als
> T-066, und beide liegen dort, wo T-068 gearbeitet hat. Der Verdacht auf
> eine Regression wird in **T-070** gemessen, nicht hier entschieden.

```
STATUS: teilweise
AUFTRAG: Power-User-Rundgang, sechs Aufgaben, Build planner ausgenommen
GELESEN: bewusst nichts — nur der Auftragstext
GEAENDERT: keine
ANNAHMEN: Charakter/Level standen bereits auf "Wylder" / Stufe 1 aus einer
         frueheren Sitzung — uebernommen, nicht selbst eingestellt.
NAECHSTER: director
BLOCKIERT DURCH: nichts, aber Aufgabe 3 blieb ohne Ergebnis
```

## Grenze dieser Sitzung (Selbstauskunft)

Das Fenster wurde nicht mit Maus und Auge bedient, sondern ueber die
Bedienungshilfen-Schnittstelle ausgelesen und ueber simulierte Mausklicks
bzw. programmatische `Invoke`-Aufrufe gesteuert. **Zu Farben, Icons und dazu,
ob etwas optisch abgeschnitten ist, kann ich nichts sagen** — Grenze des
Zugangswegs, keine Beobachtung ueber das Programm. Die README wurde nicht
gebraucht.

**Eigener Fehler beim Start:** ein erster Versuch lief unbemerkt doppelt an,
kurzzeitig liefen zwei Fenster und ein Geisterprozess. Bereinigt; benutzt
wurde am Ende ein sauber gestartetes Fenster (PID 8656), am Schluss
geschlossen.

## Aufgaben-Ergebnis

| Aufgabe | Ergebnis | Zeitgefuehl |
|---|---|---|
| 1. Relikt-Effekte & Wahrscheinlichkeiten | **mit Muehe** | ~3 Minuten |
| 2. Waffenvergleich | geschafft | ~4 Minuten |
| 3. Vorbereitung auf einen Nachtlord | **aufgegeben** | ~5 Minuten |
| 4. Deep of Night | geschafft | ~2 Minuten |
| 5. Rote Varianten | geschafft | ~1 Minute |
| 6. Ereignisse | geschafft | ~2 Minuten |

## Ablauf je Aufgabe

**1 — Effekte.** Grosse, gut erklaerte Tabelle. Der Absatz darueber erklaert
fast jede Spalte: *"Chance ist pro Relikt-Slot, nicht pro Relikt oder Run"*,
*"Tier markiert eine Staerkeleiter"*, *"Copies zaehlt, wie oft die gleiche
Sache getrennt in den Spieldaten steht"*. **Das hat wirklich geholfen — ich
haette sonst "Chance" fuer "Chance pro Relikt" gehalten.**

Eine Spalte blieb unklar: **die Ueberschrift `Comes with c…` ist
abgeschnitten. Ich habe die Maus dort platziert und ueber eine Sekunde
stillgehalten — kein Tooltip erschien.** Werte darunter: "sometimes" oder
leer. **Geraten haette ich "Comes with curse". Sicher weiss ich es nicht.**

**2 — Waffenvergleich.** Der Reiter zeigte sofort "Wylder at level 1, +1 —
VIG 10 MIN 4 …", also war der zuletzt genutzte Charakter aktiv. Verglichen:
`Icerind Hatchet` (AR 67) gegen `Rosus' Axe` (AR 82, Physical 47 + Magic 34).
Der Erklaertext sagt unmissverstaendlich, was AR bedeutet und dass Zauber
ihre Kosten statt Schaden zeigen — **eine faire Vorwarnung, nicht
verwirrend**.

**Charakterwechsel gesucht:** auf diesem Reiter keine sichtbare Auswahl. Ich
musste zurueck zum `Build planner` — dort sitzt links die Liste der zehn
Nightfarer. **Nicht auf den ersten Blick klar**, weil dieser Bereich auf
keinem der anderen fuenf Reiter sichtbar ist, obwohl die Auswahl auf den
Waffenvergleich wirkt.

**3 — Nachtlord.** Zehn Kreis-Karten mit Namen, Titel, Kurztext. Ich habe
`Fulghor / Darkdrift Knight` bewusst gewaehlt, weil ich den Kampf gut kenne.
Der Hinweistext sagt ausdruecklich *"Click a card for the full profile."*

**Zweimal angeklickt — einmal per Mausklick auf berechnete Koordinaten,
einmal per programmatischem `Invoke` auf das Element selbst. Beide Male blieb
die rechte Seite bei "Select a Nightlord".** Zwei ernsthafte Anlaeufe, kein
Ergebnis. Ob mein Klickweg ungeeignet war oder im Programm nichts passiert,
kann ich aus meiner Position nicht unterscheiden — **der erlebte Effekt ist:
Karte anklicken hat nichts sichtbar veraendert.**

**4 — Deep of Night.** Vier klar beschriftete Tabellen mit Fliesstext
darunter. Sehr verstaendlich. Mein Fazit, **weil die Zahlen nebeneinander
stehen**: bis Tiefe 2-3 lohnt der Belohnungsfaktor (x1.78-x2.09) klar; ab
Tiefe 4 steigt der gegnerische Angriffswert (x2.66-x3.11) staerker als die
Belohnung (x2.3-x2.41).

**5 — Rote Varianten.** *"A red variant is the same enemy made stronger —
never a different enemy."* Tabelle je Kategorie und Tiefe. Nichts unklar.

**6 — Ereignisse.** 15 Eintraege; beim ersten (`Fell Omen / Morgott
Invasion`) ein ausfuehrliches Profil mit Ankuendigungstext, Auftrittschance je
Nachtlord, Gewinn und Verlust. Blaue Zeilen sind "community-reported", der
Rest Spieldaten — **dieser Unterschied war mir wichtig und stand klar da.**

## Abbruchpunkte

**Aufgabe 3: aufgegeben.** Nach zwei ernsthaften Klickversuchen auf die Karte
`Fulghor` hat sich das Profil nicht geoeffnet. Kein Nachtlord-Profil gesehen.

## Falsche Erwartungen

Ich hatte erwartet, den Charakter direkt im Waffenvergleich wechseln zu
koennen, weil dort steht, fuer welchen Charakter gerechnet wird.

## Was gut lief

Die Erklaertexte ueber und unter den Tabellen waren **durchgehend
ungewoehnlich gut** — sie beantworten fast jede Frage, die mir beim Betrachten
einer Zahl gekommen waere, bevor ich sie stellen musste. Die Kennzeichnung
"community-reported" gegen Spieldaten fand ich vertrauensbildend. Aufgaben 4,
5 und 6 liefen **ohne jede Unsicherheit** durch.

## Meine drei groessten Aergernisse

1. **Die Nachtlord-Karte hat sich auf keinen meiner beiden Klickversuche
   geoeffnet**, obwohl der Text ausdruecklich "Click a card for the full
   profile" sagt — genau der Bereich, den ich fuer Aufgabe 3 brauchte.
2. **`Comes with c…` ist abgeschnitten, und laengeres Verweilen zeigte keine
   Erklaerung** — bei einer Tabelle, die sonst vorbildlich alles erklaert,
   ist genau diese Luecke aufgefallen.
3. Der Charakter laesst sich nur auf einem **anderen** Reiter aendern.

## Empfehlung

Ja, mit Einschraenkung — fuer Nachschlagefragen sehr nuetzlich und
ungewoehnlich gut erklaert. Nuetzlichster Bereich: **Deep of Night**. Am
wenigsten gebracht hat **Nightlords**, weil ich nicht ueber die
Kartenuebersicht hinauskam.
