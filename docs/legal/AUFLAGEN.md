# Auflagen und Rechtsentscheidungen

Gefuehrt vom `director`. Quelle der Bewertungen: `compliance-agent`.
Status: offen | erfuellt | dauerhaft | zurueckgestellt

## Entscheidungen des Nutzers (App Designer), 2026-09-01

- **Keine Einnahmeabsicht.** Nightreign Helper bleibt rein privat: keine
  Spenden, keine bezahlte Version, keine Werbung. Damit fehlt der
  "geschaeftliche Verkehr" nach § 14 Abs. 2 MarkenG, und die Bewertung in
  `C-001.md` gilt unveraendert. **Aendert sich das, ist A-006 auszuloesen.**
- **Screenshots werden geprueft** — eigener Auftrag T-010.
- **EULA-Restrisiko bleibt offen.** Weder ausdruecklich akzeptiert noch
  anwaltlich geklaert. Kein Handlungsbedarf, aber auch keine Entwarnung: der
  Punkt steht bewusst unentschieden und ist bei jeder groesseren Aenderung an
  der Extraktion erneut vorzulegen.

## Entscheidungen des Directors

- **Weg A gewaehlt** fuer `tests/golden/weapon_damage.json`: Klartext bleibt im
  oeffentlichen Repo, mit den Auflagen A-001 bis A-005. Begruendung: Sechs
  Item-Namen ohne Schoepfungshoehe, kein Spieltext, kein wesentlicher Teil
  einer Datenbank. Die Datei zu verstecken, um einen zu absoluten README-Satz
  zu retten, waere der falsche Weg herum — der Satz ist das Mittel, die
  Redlichkeit der Zweck.
- **Weg B (Hashes) verworfen:** Ein Hash sagt "anders", nicht "wie anders", und
  zerstoert damit den diagnostischen Wert des Golden-Tests. IDs und Zahlen
  muessten ohnehin im Klartext bleiben.
- **Weg C (Platzhalternamen) nicht angeordnet:** rechtlich nicht erforderlich.
- Die Annahme "lokal erzeugen kostet die CI-Absicherung" war **falsch** — der
  Golden-Test ueberspringt auf GitHub ohnehin, weil dem Runner die
  Spielinstallation fehlt. Was die Datei wirklich leistet, ist die
  Beweisfunktion im PR-Diff. Festgehalten, damit das Argument nicht in
  falscher Form wiederkehrt.

## Auflagenliste

| ID | Auflage | Adressat | Faellig | Status |
|---|---|---|---|---|
| A-001 | Keine Item-Beschreibungen, Flavour-Texte oder Prosa aus dem Spiel im Fixture. Zulaessig: Item-/Figurennamen, IDs, berechnete Zahlen, projekteigener Panel-Text | developer | vor Merge | offen |
| A-002 | **Maschineller Waechter** fuer A-001 — eine Absicht allein ist beim naechsten Re-Capture vergessen | developer | vor Merge | offen |
| A-003 | README trennt "das Programm liefert keine Spieldaten aus" von "das Repo enthaelt abgeleitete Werte und Screenshots" | technical-writer | vor Merge | offen |
| A-004 | `THIRD_PARTY.md`, Abschnitt "Game data", an A-003 angleichen | technical-writer | vor Merge | offen |
| A-005 | Nicht-Verbundenheits-Hinweis bleibt im README | technical-writer | dauerhaft | erfuellt |
| A-006 | Vor jeder Monetarisierung neu klaeren | Nutzer, director | bei Bedarf | dauerhaft |
| A-007 | Fixture bleibt in der Groessenordnung "einige Dutzend Faelle" | architect, developer | dauerhaft | erfuellt |
| A-008 | `release.yml` prueft nur `nrplanner/data/`; die `tests/`-Absicherung liegt allein in `tests.yml`. Beides gehoert in den Release-Lauf | developer | vor Release | offen |
| A-009 | Bei einem Takedown erst entfernen, dann antworten | Nutzer | bei Bedarf | dauerhaft |

## Nicht geprueft

- Die Extraktion selbst (`nrdata/`) — nur das Fixture war beauftragt.
- `vendor/Paramdex` ohne eigene Lizenzangabe (Modus `lizenzen`).
- US-Recht und DMCA. Praktisch relevant: **ein Takedown gegen ein
  GitHub-Repo laeuft nach US-Verfahren**, unabhaengig von der deutschen
  Rechtslage. Die Bewertung in `C-001.md` ist deutsches Recht.
- Ob das Projekt eine Regelung im Arbeitsvertrag des Nutzers beruehrt
  (Nebentaetigkeit, Rechte an Arbeitsergebnissen). Nicht geprueft, nicht
  unterstellt — **dem Nutzer zur Kenntnis vorgelegt**.
