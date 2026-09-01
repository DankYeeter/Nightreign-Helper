# GOAL — Nightreign Helper

Status: FREIGEGEBEN durch den Nutzer am 2026-09-01
Erstellt: 2026-09-01

## Ziel

Nightreign Helper ist ein Windows-Desktop-Werkzeug, das ausschliesslich aus der
eigenen Spielinstallation liest und dem Spieler beim Planen von Relikt-Builds
hilft. In diesem Vorhaben kommen zwei Dinge dazu: ein vollstaendiger Audit des
bestehenden Programms (Korrektheit, Sicherheit, Struktur, Bedienbarkeit,
Releasefaehigkeit), und ein **Build-Berater**, der aus den Relikten, die der
Spieler tatsaechlich besitzt, algorithmisch Vorschlaege errechnet — etwa
"so maximierst du Schaden" oder "so minimierst du erlittenen Schaden".

Die Rechnung laeuft im Hintergrund; der Spieler sieht nur das Ergebnis und
eine kurze Begruendung.

## Abnahmekriterien

- **A1** Ein schriftlicher Audit-Bericht liegt vor, der Korrektheit,
  Sicherheit, Architektur und Bedienbarkeit abdeckt, mit priorisierten
  Befunden. Jeder Befund hat Status (offen / behoben / zurueckgestellt).
- **A2** Alle Befunde der Prioritaet "kritisch" und "hoch" sind behoben oder
  vom Nutzer ausdruecklich zurueckgestellt.
- **A3** Der Build-Berater liefert fuer jeden Nightfarer und jedes bekannte
  Kelch-Layout mindestens zwei benannte Zielrichtungen (Schaden maximieren,
  erlittenen Schaden minimieren) und schlaegt je Slot ein konkretes Relikt
  aus dem Besitz des Spielers vor.
- **A4** Die Vorschlaege respektieren die bestehenden Regeln des Programms:
  Slot-Farben des Kelchs, Stacking-Regeln (nicht stapelbare Effekte werden
  nicht doppelt gezaehlt), Deep-of-Night-Kennzeichnung.
- **A5** Jeder Vorschlag nennt eine nachvollziehbare Begruendung in
  Nutzersprache (welche Effekte den Ausschlag gaben).
- **A6** Die Berechnung blockiert die Oberflaeche nicht: sie laeuft im
  Hintergrund, das Fenster bleibt bedienbar, und bei grossen Relikt-Bestaenden
  bleibt die Antwortzeit im gemessenen Budget (Zielwert wird vom
  performance-tuner gesetzt).
- **A7** Wo die Spieldateien eine Bewertung nicht hergeben, sagt das Programm
  das, statt zu raten — die bestehende Hausregel gilt auch fuer den Berater.
- **A8** Alle Texte in der Oberflaeche sind Englisch (bestehende Projektregel).
- **A9** Ein `qa-engineer`-Durchlauf bestaetigt A3 bis A8 gegen ein gebautes
  Artefakt, nicht nur gegen den Quellstand.

## Nicht-Ziele

- Kein Auslesen oder Schreiben in laufende Spielprozesse. Der Save bleibt
  read-only.
- Kein Netzwerkzugriff, keine Wiki-Daten, keine Telemetrie.
- Keine Optimalitaetsgarantie: der Berater ist ein Heuristik-Ratgeber, kein
  Loeser mit Beweis.
- Keine Mehrsprachigkeit.
- Kein Umbau auf ein anderes UI-Framework in diesem Vorhaben.

## Rahmen

- Zielsystem: Windows 10/11, Python 3.11+, PySide6/Qt, PyInstaller-Artefakt.
  (Korrektur 2026-09-01: der Entwurf nannte faelschlich Tkinter.)
- Repo: github.com/DankYeeter/Nightreign-Helper (public), `main` ist geschuetzt
  — jede Aenderung geht ueber einen Pull Request.
- Arbeitskopie: C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper
- Datenquelle: die Spielinstallation des Nutzers. NIGHTREIGN ist auf diesem
  Rechner installiert (Nutzer bestaetigt 2026-09-01) — Tests gegen echte
  Spieldaten sind moeglich und werden verlangt.
