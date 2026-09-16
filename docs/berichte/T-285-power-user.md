# T-285b — power-user am Artefakt 1.13.1 (16.09.2026)

*Vom Director abgelegt; der `power-user` hat kein `Write`.* Persona Jonas,
27, kein Technikwissen. Werkzeug: simulierte Mausklicks + Fenstertext (UIA),
keine Bildschirmabzuege.

| Ziel | Ergebnis | Haengepunkt |
|---|---|---|
| 1 Erststart bis Relikte | mit Muehe, ~2 min | Erststart lief ohne Rueckfrage durch; Wylder, 313 Relikte, 5 Chalices korrekt erkannt. "Empty slot" liess sich nicht oeffnen (2 Klicks ohne Wirkung) |
| 2 Optimize fuer Wylder | aufgegeben | "Optimize" zweimal geklickt (auch mit erzwungenem Fokus) — "Nothing suggested yet." blieb |
| 3 Effekt ausschliessen/festlegen | nicht erreicht | setzt 2 voraus |
| 4 1H/2H umschalten | nicht erreicht | Kaestchen "1H" gefunden, Klick kam nicht an |
| 5 Build speichern/wiederfinden | nicht erreicht | — |
| 6 Startmenue-Verknuepfung | teilweise | Knopf zeigte schon "✓ In Start Menu"; Tester glaubt, nie gefragt worden zu sein |

**Abbruch:** nach genau einem wirksamen Klick (Berater-Dropdown → "Maximise
damage") kam kein weiterer simulierter Klick an — Tab-Leiste, Optimize,
Filters, Empty slot, zwei Kontrollkaestchen — Zeiger nachweislich auf dem
Element, Fenster im Vordergrund.

**Director:** (a) Klickausfall = Werkzeugmuster wie T-275/QA-279 (mit
echter Maus nicht reproduziert, T-276; QA T-283a bestaetigte dieselben
Elemente per UIA am selben Artefakt) → **QA-282**, nicht releasesperrend,
kein Programmbefund belegt. (b) Startmenue: das Erststartfenster bietet die
Verknuepfung als vorausgewaehltes Kaestchen an (`firstrun.py:1052`,
`window.wants_shortcut()`, A15-Entscheidung des Nutzers 06.09.) — der Laie
hat das Kaestchen nicht wahrgenommen; A11-Hinweis, kein Fehler. (c) A11
bleibt "teilweise": dritter Lauf ohne belastbares Ergebnis; der Nutzer hat
am 15.09. selbst ingame getestet.
