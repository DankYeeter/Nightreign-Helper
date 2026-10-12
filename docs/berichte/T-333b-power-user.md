# T-333b power-user — Laientest Exe 1.19.0 (12.10.2026)

Vom Director aus der Agentenantwort uebertragen (Rolle ohne Write).
Werkzeug: `drive_window.05143d2.ps1 -Real`, UIA lesen, echte Klicks.

| Ziel | Ergebnis |
|---|---|
| Einrichtung | geschafft, 0 Klicks, ~50 s trotz Testabzug |
| 1 Wylder waehlen | geschafft mit Vorbehalt (aus Spielstand vorgewaehlt, Klick ohne Rueckmeldung) |
| 2 Vorschlag, verstehen, speichern | mit Muehe, 7 Aktionen, ~1 min, kein Abbruch |

Befunde → `qa/findings.md` QA-298 (Undertaker-Relikt fuer Wylder, Apply all
ohne Warnung), QA-299 (3+ Hammers bei Greatsword), QA-300 (Why-Fenster
ueberladen, zwei Why-Knoepfe, Zielwahl ohne Namen), QA-301 (Speichern ohne
Bestaetigung, Einrichtung 50 s).

Gut: Einrichtung mit Fortschritt in Worten; Spielstand erkannt in einem Satz;
Optimize liefert sofort drei Vorschlaege; Why-Zahlen ("Strength +3 →
Attack rating +4") verstaendlich; Vorher/Nachher 56/58 → 62/64.

Nicht erreicht: andere Ziele, Filters, Hold, Picker, Build laden, andere
Nightfarer. Nebenbei: "✓ In Start Menu" ohne Klick (Haekchen voreingestellt,
umgelenktes `APPDATA`).
