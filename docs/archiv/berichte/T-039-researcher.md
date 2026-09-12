STATUS: teilweise
AUFTRAG: T-039 - R-004: Woher kommt der Gesamtfaktor zwischen Elden-Ring-Angriffswert und Nightreign-Anzeige? (researcher)
GELESEN: docs/tasks/T-039.md, GOAL.md, docs/state.md, docs/research/R-001.md, R-002.md, R-003.md, nrplanner/weapons.py (vollstaendig), CLAUDE.md (Nightreign-Helper); externe Quellen siehe Belegliste in docs/research/R-004.md
GEAENDERT: docs/research/R-004.md (neu), docs/berichte/T-039-researcher.md (neu) - kein Git, kein Anwendungscode, fremde ungespeicherte Aenderungen im Arbeitsbaum unberuehrt
ANNAHMEN: (1) Fextralifes Kopfzeile "Attack Power: Physical 80" ist der Param-Grundwert der Waffe - nicht belegt, Prueftest T5 in R-004 entscheidet es. (2) Die Fextralife-Level-x-Raritaets-Tabelle bildet die Anzeige im Ausruestungsmenue ab, ohne Relikte - die Seite sagt es nicht ausdruecklich. (3) Fuer meinen Kurvenfit habe ich die Elden-Ring-Standardkurve und ein B:C-Verhaeltnis von 2:1 unterstellt; Nightreigns eigene Kurven kenne ich nicht.
NAECHSTER: director (Entscheid ueber Option A/B/C und ueber T1/T5, die ohne Spiel laufen und diesen Bericht in seinem Kern bestaetigen oder umstossen); danach qa-engineer fuer T1/T2/T5, Nutzer fuer T3/T4/T6
BLOCKIERT DURCH: nichts fuer die Recherche. Die Ursachenfrage selbst ist blockiert durch das Fehlen jeder oeffentlichen Primaerquelle zu Nightreign-Params - sie kann nur gegen die eigene regulation.bin beantwortet werden, und das ist keine Recherche-Aufgabe.

# Bericht T-039 - R-004 (researcher)

## Geschaerfte Frage

Ich habe beantwortet: *Gibt es einen einzelnen multiplikativen Faktor zwischen
`weapons.rate()` und der Anzeige im Ausruestungsmenue, haengt er von
Charakterlevel, Waffenraritaet oder Nightfarer ab, und welche Groessenordnung
hat er?*

Ich habe **nicht** beantwortet: woher dieser Faktor in den Params technisch
kommt. Dafuer gibt es keine oeffentliche Quelle. Daher STATUS teilweise: die
Abnahmebedingung "Faktor, Geltungsbereich und Unsicherheit" ist erfuellt, die
Bedingung "mindestens eine Primaerquelle (Param-Dump, Moddingwiki) oder eine
Erklaerung, warum es keine gibt" ist ueber die Erklaerung erfuellt, nicht ueber
eine Primaerquelle.

## Kurzantwort (wortgleich zu docs/research/R-004.md)

Ein Gesamtfaktor existiert, er ist **level-unabhaengig** und liegt in der
Groessenordnung **0,60** (Bandbreite 0,57-0,66; unsere Messung 0,597-0,601 fuer
Wylder/Ironeye/Raider, 0,577-0,583 fuer Guardian). Ein Faktor, der mit dem Level
waechst und bei Level 15 auf 1,0 laeuft, ist **widerlegt**: eine oeffentliche
Fan-Tabelle zeigt fuer Wylder's Greatsword (Common) von Level 12 auf 15 nur
118 -> 125 (+5,9 %), fuer Executor's Blade 92 -> 94 (+2,2 %) - ein Faktor von
0,60 auf 1,0 haette +67 % verlangt. Dieselbe Tabelle zeigt, dass die Raritaet
als **glatter Multiplikator auf die gesamte Angriffskraft** wirkt, mit den
Verhaeltnissen rund **1 : 1,25 : 1,535 : 1,74** (Common : Rare : Epic :
Legendary), auf allen 15 Leveln gleich. Daraus folgt der wichtigste Warnhinweis
dieser Recherche: **Common/Legendary = 0,574** - praktisch identisch mit dem
gemessenen Guardian-Verhaeltnis und nahe an den 0,60 der anderen Helden. Ein
Raritaets-Versatz im Vergleich (Programm rechnet Legendary, Spiel zeigt Common)
erzeugt exakt dieselbe Zahl wie ein echter Gesamtfaktor und muss zuerst
ausgeschlossen werden. **Keine** oeffentliche Quelle - weder Param-Dump noch
Moddingwiki noch Community-Rechner - dokumentiert einen solchen Faktor; die
Ursache bleibt unbelegt.

## Befunde, je ein Satz

1. **Die Anzeige liegt unter dem Grundwert der Waffe, was die Elden-Ring-Formel
   nicht kann** - Wylder's Greatsword zeigt auf Level 1 58 bei Grundwert 80
   (0,725), Executor's Blade 46 bei 62 (0,742), und `AR = base x (1 + Summe>=0)`
   ist nie kleiner als `base`. Quelle:
   <https://eldenringnightreign.wiki.fextralife.com/Wylder's+Greatsword> und
   <https://eldenringnightreign.wiki.fextralife.com/Executor's+Blade>, abgerufen
   2026-09-03, Sekundaerquelle ohne Herkunftsangabe.
2. **Ein levelabhaengiger Faktor, der bei Lv15 auf 1,0 laeuft, ist widerlegt** -
   von Lv12 auf Lv15 steigt die Anzeige nur um 5,9 % bzw. 2,2 %, waehrend ein
   Lauf von 0,60 auf 1,0 zusaetzliche +67 % erzwungen haette; der Zuwachs je
   Attributpunkt faellt sogar (Softcap-Signatur). Quelle: dieselbe Tabelle plus
   <https://eldenringnightreign.wiki.fextralife.com/Level>, abgerufen 2026-09-03.
3. **Die Raritaet ist ein glatter Gesamtmultiplikator, 1 : 1,254 : 1,534 :
   1,737** - ueber alle 15 Level schwanken diese Verhaeltnisse um weniger als
   1,5 %, die Raritaet wirkt also praktisch rein auf den Grundwert. Quelle:
   Fextralife-Wylder-Tabelle, eigene Rechnung darauf, abgerufen 2026-09-03.
4. **Common/Legendary = 0,574 trifft das gemessene Guardian-Band 0,577-0,583
   fast exakt** - ein Raritaets-Versatz im Vergleich erzeugt dieselbe Signatur
   wie ein echter Gesamtfaktor (konstant ueber Waffen, konstant ueber Level, auf
   beide Summanden gleich), weil `result.scaled = base * bonus` jeden
   `base`-Fehler proportional weiterreicht. Quelle: eigene Ableitung aus
   `nrplanner/weapons.py` und der Fextralife-Tabelle.
5. **Die Datamining-Community hat dazu nichts veroeffentlicht** - der
   Nightreign-Bereich des Souls Modding Wiki fuehrt vier Seiten (Characters,
   Event Flags, Map Names, Parts) und einen leeren Abschnitt "Game Parameters",
   Zullie the Witch hat nur die Level-Statistiktabellen datenminiert, und die
   beiden gefundenen Community-Rechner (relics.pro,
   nightreign-calculator.netlify.app) nennen weder Formel noch Quellcode.
   Quellen: <http://soulsmodding.com/doku.php?id=ern-refmat:main>,
   <https://relics.pro/compendium/attack-power/>,
   <https://nightreign-calculator.netlify.app/>, abgerufen 2026-09-03.
6. **Die Formelstruktur ist als Elden-Ring-Struktur belegt, die Zahlen nicht** -
   der Quellcode von `eldenring.tclark.io` rechnet
   `attackPower = baseAttackPower * totalScaling` mit eingebackener
   Verstaerkung und eingebackenem AttackElementCorrect-Einfluss, also dieselbe
   Klammerung wie unser `base * (1 + sum(...))`. Quelle:
   <https://raw.githubusercontent.com/ThomasJClark/elden-ring-weapon-calculator/master/src/calculator/calculator.ts>,
   abgerufen 2026-09-03 - **Primaerquelle fuer die Struktur, aber Elden Ring;
   keine Zahl daraus gilt fuer Nightreign.**

## Widersprueche, die offen geblieben sind

- **Echter Gesamtfaktor gegen Raritaets-Versatz.** Beide erklaeren die Messung
  gleich gut. Fuer den echten Faktor spricht, dass die Anzeige auf Level 1 unter
  dem Grundwert der Waffe liegt - das ist eine Aussage innerhalb der fremden
  Quelle und kann kein Fehler unseres Vergleichs sein. Fuer den Versatz spricht,
  dass 0,574 das Guardian-Band auf 1 % trifft. Beides kann sich ueberlagern.
- **Meine Gegenprobe ist moeglicherweise nicht unabhaengig.** Wenn die
  Fextralife-Tabellen dieselbe Fan-Messung sind, auf der T-038 aufsetzt,
  bestaetigen sie nur die Rechnung, nicht die Zahl. Unberuehrt davon bleibt
  allein der Vergleich Anzeige (58) gegen Grundwert (80).
- **Kein Modell erklaert alle 15 Zeilen.** Ein konstanter Faktor mit der
  Elden-Ring-Standardkurve passt auf ~2,5 % (bester Fit 0,64), aber die
  Level-1-Zeile faellt heraus und der Hochlevelbereich taepert staerker als die
  Elden-Ring-Kurve - ein Hinweis auf abweichende Nightreign-Kurven. Fuer die
  Hauptfrage zweitrangig, weil das Programm Nightreigns eigene Kurven liest.
- **Der Guardian-Versatz von ~3 % ist unerklaert.** Eine Quelle fuer einen
  innewohnenden Guardian-Schadensmalus gibt es nicht; ich habe ausdruecklich
  danach gesucht.

## Was diese Recherche NICHT beantwortet

- Woher der Faktor in den Params kommt. Kein Kandidat aus dem Auftrag ist
  **positiv** belegt. Widerlegt sind zwei: "levelabhaengiger Multiplikator mit
  1,0 bei Lv15" und "reine Anzeigeregel" (letzteres durch die Nutzermessung an
  der Trainingspuppe vom 2026-09-03, die der Director nachgereicht hat).
- Ob Fextralifes Kopfzeile "Attack Power: 80" wirklich der Param-Grundwert ist.
  Faellt diese Annahme, faellt mein staerkster Einzelhinweis.
- Warum Guardian abweicht.
- Die absoluten Programmwerte - ich habe keinen Code ausgefuehrt und keine
  Installation gelesen; alle Vergleiche stuetzen sich auf die im Auftrag
  genannten Sondenverhaeltnisse.
- Drei potenziell datenminierte Quellen blieben unerreichbar: maxroll.gg
  (HTTP 404 auf die Waffen-URL), fromsoftwiki.org (HTTP 403), mobalytics.gg
  (HTTP 403). Ein Browser koennte sie oeffnen; das ist keine Rollengrenze,
  sondern eine Werkzeuggrenze.

## Was ich empfehle (getrennt vom Befund)

Zuerst **T1** laufen lassen - Programm, Wylder's Greatsword, Wylder-Lv12-
Attribute, vier Raritaetsstufen, Verhaeltnisse gegen 1 : 1,254 : 1,534 : 1,737.
Das braucht kein Spiel, dauert eine Viertelstunde und trennt die beiden
konkurrierenden Erklaerungen. Alles andere - insbesondere jede Entscheidung, den
Faktor 0,60 einzurechnen - danach. Wer den Faktor vorher einbaut, repariert
moeglicherweise eine Raritaetsverwechslung mit einer erfundenen Konstante.

Sechs Prueftests mit Waffe, Held, Level und Erwartung stehen ausformuliert in
`docs/research/R-004.md`, Abschnitt "Welche Messung an der Trainingspuppe
entscheidet was" (T1 bis T6; T1, T2 und T5 brauchen kein Spiel).

## Pfad

`C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\docs\research\R-004.md`
