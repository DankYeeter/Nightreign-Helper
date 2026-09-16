# T-265 — power-user am Artefakt 1.12.0 (15.09.2026, zwei Durchgaenge)

*Vom Director aus der Rueckmeldung abgelegt; der `power-user` hat kein `Write`.*

Durchgang 1 scheiterte an Schritt 0 (Klickversatz bei 125 % — Werkzeug,
nicht Programm; wie T-241d). Durchgang 2 mit DPI-aware-Shell: Klicks treffen.

| Ziel | Ergebnis | Haengepunkt |
|---|---|---|
| 1 Start, eigene Zahlen (319 Relikte) | erreicht | — |
| 2 Raider max. Schaden + Why | erreicht | `Why` je Relikt und Effekt ("nuetzt dir als Raider nichts") = Highlight |
| 3 Effekt sperren → weg → aufheben | erreicht | Punkt vor jeder Effektzeile, Vorher/Nachher eindeutig |
| 4 Effekt als Pflicht | **aufgegeben** | Kein Bedienelement erkannt; Rechtsklick-Menue mit zwei Eintraegen fuer UIA unlesbar; zweimal Linksklick → "neutral" (dritte Stufe nicht erkannt) |
| 5 1H/2H ablesen, Schalter | teilweise | `69 / 79 2H AR` lesbar; Schalter reagiert, **Zahl aendert sich nicht** (by design AK-293 — fuer den Laien unverstaendlich) |
| 6 Farbpunkte an Kelchen | aufgegeben | Kein Tooltip nach >1 s Verweilen (simulierte Maus, UIA liest keine Farben); AK-296-Tooltip laut QA 13/13 vorhanden — live ungeklaert |

Falsche Erwartung: `Raider's own` (Kopfzeile) fuer klickbar gehalten.

Director: Ziel 4 und 5 sind A11-Befunde (QA-274, QA-275); Ziel 6 Werkzeuggrenze,
Tooltip am echten Fenster durch den Nutzer pruefen.
