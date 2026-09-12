STATUS: erledigt
AUFTRAG: T-104 - Auflagen vor der ersten Veroeffentlichung (compliance-agent, Modus `auflagen`)
GELESEN: ~/.claude/agents/_rahmen.md; docs/tasks/T-104.md; docs/legal/AUFLAGEN.md, C-001.md, C-002.md; LICENSE; THIRD_PARTY.md; requirements.txt; NightreignHelper.spec; .github/workflows/release.yml (Stand nach T-105, d92bab9) und tests.yml (Grep); scripts/check_licences.py; vendor/Paramdex/NOTICE; nrdata/keys.py, bhd5.py, regulation.py, savefile.py, dvdbnd.py (Grep); nrplanner/paths.py, firstrun.py, datasource.py, eventlore.py, __init__.py; README.md (Disclaimer/Licence, Z. 355-366, 570-607); GOAL.md (A3-A9, Nicht-Ziele); docs/state.md (A9, SEC-023); security/findings.md (SEC-023); docs/berichte/T-105-developer.md (Kopf); .git/logs/HEAD. Primaerquellen im Web (alle abgerufen 2026-09-07): Bandai-Namco-EULA (Steam-App 2622380), Steam Subscriber Agreement (2026-04-20), LGPL-3.0 § 4, GPL-3.0 §§ 1, 6, BSD-3 Kl. 2, PyInstaller COPYING, soulsmods/Paramdex, Google ToS (2026-07-30), GitHub ToS (2026-04-27) und AUP, UrhG §§ 2, 44b, 69a, 69c, 69d, 69f, 69g, 87b, 95a, 108b, StGB § 202a, MarkenG §§ 14, 23, DSGVO Art. 2, 4, DDG § 5, BGB §§ 309, 327, 521, 599, BFSG §§ 1, 2, KI-VO Art. 2, 3, Richtlinie (EU) 2024/2853 Art. 2, 4, 29, EuGH C-355/12.
GEÄNDERT: docs/legal/C-003.md (neu); docs/legal/AUFLAGEN.md (fortgefuehrt: A-010 bis A-019 aus C-002 nachgetragen, A-020 bis A-032 neu, Abschnitt "Nicht geprueft" ergaenzt); docs/berichte/T-104-compliance-agent.md (neu). Nichts committet — die Rolle hat kein Bash; der director committet.
ANNAHMEN: (1) Die Nutzerentscheidung vom 2026-09-01 (rein privat, keine Einnahmen, natuerliche Person) gilt fort. (2) Erwaegungsgrund 12 der KI-VO nimmt regelbasierte Systeme aus — aus dem Gedaechtnis, nicht abgerufen; das Ergebnis haengt nicht daran. (3) Analogie §§ 521/599 BGB auf unentgeltliche Software — gefestigte Auffassung, nicht am Urteil verifiziert. (4) EU-Exportkontrolle nimmt oeffentlich verfuegbare Kryptosoftware aus — unverifiziert, als Annahme gekennzeichnet. (5) Der Auftrag sagte, AUFLAGEN.md existiere nicht; sie existiert seit 2026-09-01 und wurde fortgefuehrt, nicht neu angelegt.
NÄCHSTER: technical-writer (T1-T4 aus C-003); parallel developer fuer A-020 (release.yml `files:`) — Reihenfolge entscheidet der director. A-025 geht an den Nutzer.
BLOCKIERT DURCH: nichts fuer diesen Auftrag. Das Release selbst ist blockiert durch A-020 (Pflicht) und A-025 (Nutzerentscheidung).

## Ergebnis

**Frage:** Darf die gebaute EXE an Dritte? **Ampel: GELB**, mit einem GRAU
(Befund 5), das nur der Nutzer entscheidet. Volltext:
`C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\docs\legal\C-003.md`.

**Was das Release heute sperrt (A-020):** Die Releases-Seite liefert nur
`NightreignHelper.exe` und `.sha256`. LGPL-3.0 § 4(a)/(b) und BSD Klausel 2
verlangen Hinweis und Lizenztexte **mit jeder Kopie** bzw. **beim**
Artefakt; eine Datei im Repo ist kein "accompany". Antwort auf die
Auftragsfrage zu `THIRD_PARTY.md`: inhaltlich zur Haelfte (Relink ueber
oeffentliches Repo traegt; Copyright-Vermerke und Volltexte fehlen), im
Transport gar nicht. Loesung billig: ein Hinweispaket als zweites Asset
(developer, release.yml) mit Inhalt nach A-021 (technical-writer).

**Was neu ist und nur der Nutzer entscheiden kann (A-025, GRAU):** Die EXE
enthaelt die AES-/RSA-Schluessel fuer `regulation.bin`, Archive und
Spielstand. Bis heute war das Privatgebrauch (§ 108b Abs. 1 UrhG straflos,
EULA nur eigene Lizenz). **Mit dem ersten Release-Asset wird aus Nutzung
Verbreitung** — § 95a Abs. 3 UrhG (Umgehungsvorrichtung) und EULA 10(i)
("distributing … unauthorized third party tools"). Ob ein reines
Leseprogramm mit seit Jahren oeffentlichen Schluesseln darunter faellt, ist
ungeklaert (C-355/12: Spiele als Ganzes geschuetzt, aber Proportionalitaet
und tatsaechliche Nutzung zaehlen). Strafbar nach Wortlaut nicht (nicht
gewerblich); zivilrechtlich Unterlassung/Takedown moeglich; Wahrscheinlichkeit
gering (R-002, Smithbox/WitchyBND). Die Haltung "bewusst unentschieden" von
2026-09-01 reicht fuer Weitergabe an Dritte nicht mehr. Alternative ohne
dieses Risiko: Quellcode statt EXE — kostet A9. Mandatsfrage steht in C-003.

**Entlastend, belegt:** keine Spieldaten in der EXE (Garantie ist die
`datas`-Liste der Spec, nicht der Workflow-Schritt — A-030); keine
DSGVO-, Impressums- oder § 327-BGB-Pflicht (Haushaltsausnahme, § 5 DDG,
kein Entgelt); Haftung von Gesetzes wegen auf Vorsatz/grobe Fahrlaessigkeit
beschraenkt, MIT passt; KI-VO greift nicht (regelbasiert, FOSS-Ausnahme);
BFSG nicht anwendbar; Marke: Hinweis gehoert an die Download-Stelle (A-023).
Paramdex ohne Lizenz: GRAU, kein Copyleft, A-029 empfohlen.

**Befunde ohne Nummer (Director vergibt IDs):** (a) `AUFLAGEN.md` endete bei
A-009; A-010 bis A-019 aus C-002 waren nie uebertragen — nachgetragen.
(b) README Z. 581 traegt weiter den absoluten Satz "distributes none of that
content" — A-003 ist offen. (c) `release.yml`-Kommentar verspricht mehr als
der Schritt "Refuse to ship game data" prueft.

**Fuer den technical-writer, getrennt in C-003 Abschnitt "Was der
technical-writer von mir braucht":** T1 Hinweispaket (Vermerke + Volltexte
aller sechs Komponenten, LGPL+GPL, Qt-Quellfundstelle), T2 fester Text der
Release-Beschreibung (Nicht-Verbundenheit, was die EXE technisch tut,
praeziser A-003-Satz, Sicherungshinweis, Verweis aufs Paket), T3 README-
Absatz "What it reads and where it writes", T4 kein In-App-Dialog noetig.

**Nicht geprueft:** US-Recht (17 U.S.C. § 1201 — Plattform GitHub),
japanisches Recht, UPX-Lizenz (nur bei A-031), Exportkontrolle, Icon auf
Aehnlichkeit, Umsetzung von A-010, Arbeitsvertrag des Nutzers.

**Nachpruefen ab:** EULA-/SSA-Aenderung (Staende 2024-09-17 / 2026-04-20);
jedem PySide6-Upgrade; 2026-12-09 (Produkthaftungsrichtlinie); jedem
Ereignis aus A-032.
