# T-241d — power-user am Artefakt 1.10.0 (14.09.2026, 08:05-08:27)

*Vom Director aus der Rueckmeldung abgelegt; der `power-user` hat kein `Write`.*

Persona: Wylder-Spieler, kein Programmierer. Werkzeug: UI-Automation-Baum +
simulierte Klicks (SetCursorPos/mouse_event) bei 125 % Skalierung — der
Tester nennt die Koordinatenuebersetzung selbst als Stoerquelle.

| Ziel | Ergebnis | Haengepunkt |
|---|---|---|
| 1 Start bis eigene Zahlen | erreicht | "Loaded Wylder ... You own 314 relics in total." sofort — **Spielstand-Automatik traf**, obwohl `APPDATA` umgelenkt sein sollte (Director: Umlenkung im Lauf fraglich; reale Daten unveraendert, geprueft 08:30: Registry `DankYeeter` ohne "Wylder Damage", `%LOCALAPPDATA%\NightreignHelper` Stand August) |
| 2 Max. Schaden, drei Relikte + Warum | erreicht | `Why` in Laiensprache verstanden; kein Kelch heisst "Standard" — Kopfzeile `Wylder's own` nicht klickbar |
| 3 Min. Schaden + Worst/Best | **aufgegeben** | `Minimise damage taken` + Optimize → wiederholt `Nothing suggested yet.`; statt Optimize oeffnete sich mehrfach `Save build` (Klickversatz moeglich) |
| 4 Build speichern, Neustart | **aufgegeben** | `Save build` → Name → OK schliesst; Liste zeigt nur `Equipped in game`, `Unsaved build` — zweimal |
| 5 Reliktzahl + haeufigster Effekt | teilweise | 314 sofort; `Effects & chances` nicht erkennbar auf Besitz gefiltert |
| 6 Gladius-Schwaeche | erreicht | `Pile on Holy damage.`, Holy x1,35 |

Drei Aergernisse: kein Vorschlag fuer "wenig Schaden" ohne Fehlermeldung ·
gespeicherter Build nicht auffindbar · keine "Standard"-Kelch-Beschriftung.

Director: Ziele 3 und 4 sind durch das Klickwerkzeug kontaminiert (Dialog
oeffnete sich statt Optimize) und werden vom `qa-engineer` A9 am selben
Artefakt unabhaengig geprueft; Ziel 5 ist eine Produktfrage (A10-Frage
"haeufigster Effekt in meinem Besitz" — Effects-Tab zeigt Copies/Tier, QA-127).
Hinterlassen: leerer Ordner `.scratch-powuser/` im Projektbaum (Director
entfernt 08:31), Registry-Schluessel `DankYeeterT-241pu` geloescht (geprueft).
