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

## Nachtrag aus C-002 (2026-09-01), eingetragen 2026-09-07 (compliance-agent, T-104)

Das Register endete bei A-009; C-002 hatte A-010 bis A-019 definiert, sie
wurden nie uebertragen. Hier nachgetragen, damit die Nummerierung nicht
kollidiert. Bewertung und Status unveraendert aus C-002 (Volltext dort).

| ID | Auflage | Ampel | Adressat | Faellig | Status |
|---|---|---|---|---|---|
| A-010 | `nightlords.png` ersetzen: hoechstens eine Spiel-Beschreibungsprosa im Bild, empfohlen keine (Weg N-c) | ROT | developer, ui-ux-designer | vor naechstem Push nach `main` | offen |
| A-011 | Nur bei Weg N-b: README Abschnitt 4 setzt sich mit der verbliebenen Beschreibung auseinander | GELB | technical-writer | mit A-010 | offen |
| A-012 | Quellenangabe (Spiel, Rechteinhaber) an den Einbindungsstellen der Screenshots im README | GELB | technical-writer | vor naechstem Push nach `main` | offen |
| A-013 | `make_screenshots.py` legt fuer jede Registerkarte mit Detailbereich den gezeigten Eintrag im Code fest | GELB | developer | vor naechster Neuaufnahme | offen |
| A-014 | Neue oder geaenderte Registerkarten mit Spielprosa vor Veroeffentlichung gegen A-010 pruefen | GELB | developer | dauerhaft | offen |
| A-015 | *Empfohlen:* Nutzer entscheidet, ob die alte `nightlords.png` aus der Git-Historie entfernt wird | — | Nutzer, director | mit A-010 | offen |
| A-016 | Bewertung traegt nur bei Privatperson ohne Monetarisierung; sonst C-002 neu einholen | GELB | Nutzer, director | ab Einnahmeabsicht / Gesellschaft | offen |
| A-017 | Keine Spielgrafik ausserhalb des Oberflaechenkontexts (Logo, Social Preview, Icon) | GELB | developer, ui-ux-designer, technical-writer | dauerhaft | offen |
| A-018 | *Empfohlen:* kein Bild zeigt einen Katalog in nennenswertem Umfang der Gesamtliste | GELB | developer, ui-ux-designer | bei Aenderung | offen |
| A-019 | Keine Selbsterklaerung zur Rechtsgrundlage im README (kein "fair use", keine Berufung auf die Video Policy) | GELB | technical-writer | dauerhaft | offen |

## Auflagen aus C-003 (T-104, 2026-09-07) — erste Weitergabe der gebauten EXE

Gesamtampel **GELB**; A-020 sperrt das Release; A-025 ist GRAU und
Nutzerentscheidung. Volltext, Normen und Fundstellen in `C-003.md`.

| ID | Auflage | Ampel | Adressat | Faellig | Status |
|---|---|---|---|---|---|
| A-020 | **Sperrt.** Hinweispaket als Release-Asset neben EXE und Pruefsumme: `LICENSE`, Hinweisdatei (A-021), Volltexte LGPL-3.0 und GPL-3.0, `vendor/Paramdex/NOTICE`. Umsetzung in `release.yml` `files:` (Datei bei T-105 — Auflage, keine Aenderung) | ROT bis erfuellt | developer | vor Veroeffentlichung | offen |
| A-021 | Hinweisdatei mit Copyright-Vermerk und vollstaendigem Lizenztext jeder gebuendelten Komponente, Qt/PySide6-Quellfundstelle, Relink-Absatz; Vermerke aus den Wheels | GELB | technical-writer | vor Veroeffentlichung | offen |
| A-022 | Repo bleibt oeffentlich, solange ein Release abrufbar ist; jedes Release traegt seinen Quell-Tag; PySide6-Lizenz bei jedem Upgrade neu lesen | GELB | Nutzer, release-manager | dauerhaft ab erstem Release | offen |
| A-023 | Nicht-Verbundenheits-Hinweis und Rechteinhaber an der Download-Stelle: fester Text der Release-Beschreibung und Hinweispaket; der absolute Satz "distributes none" wird nicht wiederholt (A-003 gilt fort) | GELB | technical-writer, release-manager | vor Veroeffentlichung | offen |
| A-024 | Transparenztext: liest und entschluesselt lokale Spieldateien/Spielstand mit community-bekannten Schluesseln, schreibt nie, kein Netz — README und Release-Beschreibung | GELB | technical-writer | vor Veroeffentlichung | offen |
| A-025 | **GRAU.** Nutzer entscheidet vor dem ersten Tag ausdruecklich, ob er das Restrisiko aus C-003 Befund 5 (§ 95a Abs. 3 UrhG, EULA 10(i), Steam SSA 2.G) traegt oder anwaltlich klaeren laesst | GRAU | Nutzer | vor Veroeffentlichung | offen |
| A-026 | *Empfohlen:* SEC-023 vor dem ersten Release beheben (kein Pfad mit Steam-Konto-Id auf der Flaeche) | GRUEN | developer | vor Veroeffentlichung | offen |
| A-027 | *Empfohlen:* README-Absatz "What it reads and where it writes" inkl. Cache-Pfad und Loeschung | GRUEN | technical-writer | vor Veroeffentlichung | offen |
| A-028 | *Empfohlen:* Klartext "liest nur, schreibt nie; Sicherung empfohlen" in README und Release-Beschreibung | GRUEN | technical-writer | vor Veroeffentlichung | offen |
| A-029 | *Empfohlen:* Upstream-Issue bei Paramdex um Lizenz; Commit beim naechsten Refresh im NOTICE pinnen | GRAU | Nutzer, developer | bei Gelegenheit | offen |
| A-030 | *Empfohlen:* Waechtertest, dass `datas` in `NightreignHelper.spec` genau `icon.ico` und `Paramdex/NR/Defs` enthaelt (ergaenzt A-008) | GRUEN | developer | vor Veroeffentlichung | offen |
| A-031 | *Bedingt:* ist die EXE UPX-komprimiert, UPX-Lizenzausnahme lesen und im Hinweispaket vermerken | GELB | release-manager, technical-writer | vor Veroeffentlichung, bedingt | offen |
| A-032 | **Schwellen:** neu klaeren bei erster Netzwerkfunktion, Schreiben in Spielstand/Spiel, Monetarisierung, Bundling eines Modells, Betrieb ueber Gesellschaft, Bewerbung in Reichweite | — | Nutzer, director | bei Ereignis | dauerhaft |

## Nicht geprueft

- Die Extraktion selbst (`nrdata/`) — nur das Fixture war beauftragt.
- `vendor/Paramdex` ohne eigene Lizenzangabe (Modus `lizenzen`).
- US-Recht und DMCA. Praktisch relevant: **ein Takedown gegen ein
  GitHub-Repo laeuft nach US-Verfahren**, unabhaengig von der deutschen
  Rechtslage. Die Bewertung in `C-001.md` ist deutsches Recht.
- Ob das Projekt eine Regelung im Arbeitsvertrag des Nutzers beruehrt
  (Nebentaetigkeit, Rechte an Arbeitsergebnissen). Nicht geprueft, nicht
  unterstellt — **dem Nutzer zur Kenntnis vorgelegt**.
- Seit C-003 (2026-09-07) zusaetzlich: 17 U.S.C. § 1201 (US-Anti-Umgehung,
  Plattform GitHub); UPX-Lizenz (nur falls A-031 greift); Exportkontrolle fuer
  Kryptografie (Annahme: oeffentlich verfuegbare Software ausgenommen —
  unverifiziert). `vendor/Paramdex` ist seit C-003 bewertet (GRAU, A-029).
