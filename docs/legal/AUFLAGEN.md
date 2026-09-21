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
| A-010 | `nightlords.png` ersetzen: hoechstens eine Spiel-Beschreibungsprosa im Bild, empfohlen keine (Weg N-c) | ROT (**sperrt nicht mehr**) | developer, ui-ux-designer | vor naechstem Push nach `main` | **zurueckgestellt durch Nutzer** (C-002-Entscheid 02.09.2026, ins Register nachgezogen 09.09.2026) |
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

Gesamtampel **GELB**. ~~A-020 sperrt das Release; A-025 ist GRAU und
Nutzerentscheidung.~~ **Stand 14.09.2026 (QA-243 geschlossen):** A-020 ist
erfuellt und vom Nutzer abgenommen (09.09.), A-025 ist entschieden
(FORTSETZEN, 09.09.) — **beide sperren nicht mehr**; die Zeilen unten tragen
den Stand. Volltext, Normen und Fundstellen in `C-003.md`.
**Fortgeschrieben durch C-004 (2026-09-07):** C-003 nahm an, das erste Release
stehe bevor; tatsaechlich sind seit 2026-08-11 zwoelf Releases veroeffentlicht.
A-020, A-022 und A-025 tragen unten die Fassung aus C-004; "vor
Veroeffentlichung" in den uebrigen Zeilen heisst fuer den Bestand "so bald wie
moeglich" und fuer das naechste Release "vor dessen Veroeffentlichung".

| ID | Auflage | Ampel | Adressat | Faellig | Status |
|---|---|---|---|---|---|
| A-020 | **Sperrt.** Hinweispaket als Release-Asset neben EXE und Pruefsumme: `LICENSE`, Hinweisdatei (A-021), Volltexte LGPL-3.0 und GPL-3.0, `vendor/Paramdex/NOTICE`. Umsetzung in `release.yml` `files:` (Datei bei T-105 — Auflage, keine Aenderung). **Fassung C-004:** gilt fuer die zwoelf bestehenden Releases (Nachruestung ueber A-033) und jedes kuenftige; Heilung nach GPL-3.0 § 8 nur, wenn *alle* abrufbaren Kopien konform sind | ROT→erfuellt (QA-243, 14.09.) | developer (Workflow); release-manager (Bestand) | ~~seit 2026-08-11, laufender Verstoss~~ Verstoss beendet 08.09.2026 (A-033); bei jedem kuenftigen Release erneut | **erfuellt, abgenommen durch Nutzer 09.09.2026** |
| A-021 | Hinweisdatei mit Copyright-Vermerk und vollstaendigem Lizenztext jeder gebuendelten Komponente, Qt/PySide6-Quellfundstelle, Relink-Absatz; Vermerke aus den Wheels | GELB | technical-writer | vor Veroeffentlichung | offen |
| A-022 | Repo bleibt oeffentlich, solange ein Release abrufbar ist (heute: zwoelf); jedes Release traegt seinen Quell-Tag; PySide6-Lizenz bei jedem Upgrade neu lesen. **Fassung C-004:** bindet seit dem ersten Release und ist nach pruefbarem Ist-Zustand erfuellt (Repo oeffentlich, 12 Tags, Quellarchive) — vorbehaltlich A-036 | GELB | Nutzer, release-manager | **dauerhaft seit 2026-08-11** | erfuellt (Ist); Verlauf offen (A-036) |
| A-023 | Nicht-Verbundenheits-Hinweis und Rechteinhaber an der Download-Stelle: fester Text der Release-Beschreibung und Hinweispaket; der absolute Satz "distributes none" wird nicht wiederholt (A-003 gilt fort) | GELB | technical-writer, release-manager | vor Veroeffentlichung | offen |
| A-024 | Transparenztext: liest und entschluesselt lokale Spieldateien/Spielstand mit community-bekannten Schluesseln, schreibt nie, kein Netz — README und Release-Beschreibung | GELB | technical-writer | vor Veroeffentlichung | offen |
| A-025 | **GRAU — Fassung C-004.** Nutzer entscheidet ausdruecklich, ob er die seit 2026-08-11 laufende Verbreitung der EXE (12 Releases, 25 Downloads) **fortsetzt** und das Restrisiko aus C-003 Befund 5 (§ 95a Abs. 3 UrhG, EULA 10(i), Steam SSA 2.G) traegt, sie **beendet** (EXE-Assets entfernen, nur Quellcode) oder **anwaltlich klaeren** laesst. Die Haltung "bewusst unentschieden" (Nutzerentscheidung 2026-09-01, oben) beschreibt seit dem 11.08. keinen bestehenden Zustand mehr | GRAU→entschieden (QA-243, 14.09.) | Nutzer | ~~jetzt~~ entschieden 09.09.2026 | **entschieden: FORTSETZEN** (Nutzer 09.09.2026, Abschnitt "Nutzerentscheide, 2026-09-09" unten) — sperrt nicht mehr |
| A-026 | *Empfohlen:* SEC-023 vor dem ersten Release beheben (kein Pfad mit Steam-Konto-Id auf der Flaeche) | GRUEN | developer | vor Veroeffentlichung | offen |
| A-027 | *Empfohlen:* README-Absatz "What it reads and where it writes" inkl. Cache-Pfad und Loeschung | GRUEN | technical-writer | vor Veroeffentlichung | offen |
| A-028 | *Empfohlen:* Klartext "liest nur, schreibt nie; Sicherung empfohlen" in README und Release-Beschreibung | GRUEN | technical-writer | vor Veroeffentlichung | offen |
| A-029 | *Empfohlen:* Upstream-Issue bei Paramdex um Lizenz; Commit beim naechsten Refresh im NOTICE pinnen | GRAU | Nutzer, developer | bei Gelegenheit | offen |
| A-030 | *Empfohlen:* Waechtertest, dass `datas` in `NightreignHelper.spec` genau `icon.ico` und `Paramdex/NR/Defs` enthaelt (ergaenzt A-008) | GRUEN | developer | vor Veroeffentlichung | offen |
| A-031 | *Bedingt:* ist die EXE UPX-komprimiert, UPX-Lizenzausnahme lesen und im Hinweispaket vermerken | GELB | release-manager, technical-writer | vor Veroeffentlichung, bedingt | offen |
| A-032 | **Schwellen:** neu klaeren bei erster Netzwerkfunktion, Schreiben in Spielstand/Spiel, Monetarisierung, Bundling eines Modells, Betrieb ueber Gesellschaft, Bewerbung in Reichweite | — | Nutzer, director | bei Ereignis | dauerhaft |

## Auflagen aus C-004 (T-108, 2026-09-07) — Nachtrag: zwoelf Releases seit 2026-08-11

Sachverhalt (API, 2026-09-07): 12 Releases `v1.0.0` (2026-08-11) bis `v1.7.1`
(2026-08-24), je genau ein Asset `NightreignHelper.exe`, 25 Downloads gesamt,
kein Hinweispaket, keine Lizenz- oder Nicht-Verbundenheitszeile in den
Beschreibungen, kein LGPL-/GPL-Volltext im Quellbaum eines Tags. Ampel
unveraendert GELB/GRAU; die Lizenzverletzung **laeuft** und ist nach GPL-3.0
§ 8 heilbar (vorlaeufig sofort, endgueltig 60 Tage nach Abstellen an allen
Kopien). Die 25 heruntergeladenen Kopien sind nicht zurueckzuholen und
muessen es nicht. Volltext in `C-004.md`.

| ID | Auflage | Ampel | Adressat | Faellig | Status |
|---|---|---|---|---|---|
| A-033 | **Bestand nachruesten:** an jedes der 12 Releases das Hinweispaket (T1, versionsunabhaengig benannt) als Asset hochladen und die Bestandsvariante von T2 (mit Datum der Nachruestung, kein Rueckdatieren) an den Anfang der Beschreibung setzen; vorher pruefen, ob "immutable releases" aktiv ist (dann melden). Nachweis: Asset-Liste je Release. Entfaellt fuer Releases, deren EXE der Nutzer nach A-025 loescht | GELB | release-manager (Ausfuehrung); technical-writer (T1, T2-Bestandsvariante) | mit oder vor dem naechsten Release, sobald T1 vorliegt | offen |
| A-034 | Tags `v1.0.0`–`v1.7.1` nie loeschen, verschieben oder umschreiben, solange eine EXE abrufbar ist (A-015 betrifft nur die Datei, nicht die Tags) | GELB | archivist, release-manager | dauerhaft seit 2026-08-11 | erfuellt (12 Tags vorhanden) |
| A-035 | Nutzer teilt mit, ob seit 2026-08-11 eine Beanstandung einging (GitHub, DMCA, Rechteinhaber, Bibliotheksautor, Steam). Ja → sofort `klaeren`, A-009 greift. Nein → 60-Tage-Frist aus GPL § 8 laeuft ab Abschluss von A-033 | — | Nutzer | jetzt | offen |
| A-036 | Nutzer bestaetigt, dass das Repo seit 2026-08-11 durchgehend oeffentlich war; sonst Zeitraum nennen (dann war A-022 in diesem Zeitraum verletzt und ist mit der Wiederveroeffentlichung geheilt — nur Registereintrag) | — | Nutzer | jetzt | offen |

Nach Abschluss von A-033: Datum der letzten nachgeruesteten Kopie hier
eintragen; 60 Tage spaeter ist die Qt-Lizenz nach GPL § 8(b) endgueltig
wiederhergestellt, sofern keine Anzeige einging. **Datum: 2026-09-08**
(Nachweis: T-117, vom Director je Tag mit `gh release view` gegengeprueft;
60-Tage-Ende **2026-11-07**, sofern keine Beanstandung eingeht — nachgetragen
2026-09-12, T-210, das Feld stand seit dem Nachweis leer).

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
- Seit C-004 (2026-09-07) zusaetzlich: die Tags `v1.1.0`–`v1.7.0` einzeln
  (nur `v1.0.0` und `v1.7.1` gelesen — identisch); die ausgelieferten EXEs
  selbst (gebuendelte Versionen, UPX); der Sichtbarkeitsverlauf des Repos
  (A-036); ob "immutable releases" aktiv ist (release-manager); GPL-3.0
  § 6(b); Heilungsklauseln der Bandai-Namco-EULA.

---

## Nutzerentscheidungen 2026-09-07, vom Director eingetragen

Vorgelegt an der Stufengrenze vor Bau und Release, auf der Entscheidungs-
vorlage aus `docs/legal/C-004.md`.

| Auflage | Entscheidung des Nutzers | Folge |
|---|---|---|
| **A-025** | **W1 — fortsetzen und den Bestand nachruesten.** Der Nutzer traegt das Restrisiko aus § 95a Abs. 3 UrhG und EULA 10(i) **bewusst**. Die faktisch durch Handeln gefallene Entscheidung ist damit ausdruecklich bestaetigt. | GRAU **geschlossen**. Kein Anwalt, kein Rueckzug. Der `release-manager` fuehrt A-033 als Nachruestung **aller zwoelf** Releases aus — kein Ausduennen. |
| **A-035** | **Keine Beanstandung eingegangen** seit dem 11.08.2026 — kein GitHub-Hinweis, keine DMCA-Notice, keine Nachricht eines Rechteinhabers oder Bibliotheksautors, nichts von Steam. | **erfuellt.** Die 60-Tage-Frist aus GPL-3.0 § 8 laeuft ab Abschluss von A-033 ungestoert; die Heilung greift vorlaeufig sofort. A-009 kommt nicht zum Tragen. |
| **A-036** | **Das Repository war seit dem 11.08.2026 durchgehend oeffentlich.** | **erfuellt.** A-022 ist seit dem ersten Release eingehalten, keine Massnahme. |

**Ausdruecklich nicht beauftragt** (Nutzer, 07.09.2026): US-Recht
(17 U.S.C. § 1201) · Pruefung des Arbeitsvertrags (seit C-001 offen) ·
Bewerbung des Releases. Alle drei bleiben offen im Register, ohne Auftrag.
Die Wahrscheinlichkeitsaussagen in C-003 und C-004 gelten damit weiter fuer
den gemessenen Stand: 1 Stern, 1 Fork, 25 Downloads in 27 Tagen.

**Was jetzt noch die Veroeffentlichung sperrt:** ~~nur A-033 (Nachruestung des
Bestands)~~ — A-033 ausgefuehrt 08.09.2026 (Abschnitt unten); Stand 14.09.:
**nichts Rotes** (QA-243 geschlossen). Der Transport des Hinweispakets ist
seit T-109 gebaut, der Inhalt seit T-107 fertig.

## A-033 ausgefuehrt am 08.09.2026 — Nachweis

Der `release-manager` hat in T-117 alle zwoelf Releases nachgeruestet.
**Vom Director unabhaengig nachgeprueft** (`gh release view` je Tag,
08.09.2026): **12 von 12** tragen `NightreignHelper-notices.zip`, alle zwoelf
tragen weiterhin ihre `NightreignHelper.exe` (W1, nicht W2), und in allen
zwoelf beginnt die Beschreibung mit dem Bestandstext ("Notice package added
after the fact…"). "Immutable releases" war bei keinem aktiv.

Damit ist der fortdauernde Verstoss gegen LGPL-3.0 § 4 und BSD-3 Kl. 2
**beendet**. Nach GPL-3.0 § 8 leben die Qt-Rechte vorlaeufig sofort wieder auf;
endgueltig nach **60 Tagen ohne Anzeige**, also ab dem **07.11.2026**, sofern
bis dahin keine Beanstandung eingeht (A-035).

**Status A-020 und A-033: ausgefuehrt, Nachweis erbracht — die Abnahme setzt
der Nutzer**, nicht der Director und nicht der `release-manager`.

---

## Abnahmen durch den Nutzer, 2026-09-09

Beide Eintraege waren **Buchfuehrungsluecken, keine offenen Arbeiten** — und
beide konnte nur der Nutzer schliessen. Aufgefallen sind sie, weil der
`release-manager` in T-167 den Bau **verweigert** hat: seine Rollenregel sperrt
bei einer offenen roten Auflage auch `plan` und `build`, nicht nur die
Auslieferung. **Er hat richtig gehandelt** und ausdruecklich nicht selbst
entschieden, die beiden seien "eigentlich erledigt".

**A-020 — abgenommen, Status `erfuellt`.** Die Arbeit war getan und belegt:
T-117 hat alle zwoelf Releases nachgeruestet, T-114 hat es je Tag mit
`gh release view` gegengeprueft (12 von 12 tragen das Hinweispaket). Das
Register sagte dazu selbst: *"ausgefuehrt, Nachweis erbracht — die Abnahme
setzt der Nutzer."* Sie liegt jetzt vor.

**A-010 — zurueckgestellt, sperrt nicht mehr.** Sie stammt aus C-002, und dazu
steht in `GOAL.md` seit dem 02.09.2026: *"C-002 (`nightlords.png`) wird
ignoriert. Ausdruecklicher Entscheid des Nutzers; die Frage wird nicht erneut
vorgelegt. Der Befund bleibt in `docs/legal/` dokumentiert, **sperrt aber
nichts mehr**."* **Diese Entscheidung war nie ins Register uebertragen worden**
— ein Versaeumnis des Directors, nicht des `compliance-agent`. Die Auflage
bleibt dokumentiert, wie der Nutzer es wollte; sie blockiert nichts.

**Unveraendert offen und weiterhin Nutzersache:** **A-025** (GRAU — ob die
Verbreitung der EXE fortgesetzt, beendet oder anwaltlich geklaert wird) und
die uebrigen Punkte aus C-003. **A-025 sperrt das Release, nicht den Bau** —
Bauen und Pruefen ist keine Weitergabe.

---

## Nutzerentscheide, 2026-09-09 (zweite Runde, vor 1.9.0)

**A-025 — GRAU, entschieden: FORTSETZEN.** Der Nutzer traegt das Restrisiko
aus C-003 Befund 5 ausdruecklich (§ 95a Abs. 3 UrhG, EULA 10(i), Steam SSA
2.G). Die zwoelf bestehenden Releases bleiben abrufbar; **1.9.0 darf als EXE
folgen**. Die Haltung "bewusst unentschieden" aus C-004 ist damit ersetzt.
**Status: entschieden — sperrt nicht mehr.**

*Die beiden Alternativen lagen vor und wurden verworfen: nur Quellcode
ausliefern (haette A15 seinen Zweck genommen — der Erststart fuer Fremde ist
genau fuer die gebaut, die kein Python haben) und anwaltlich klaeren lassen.*

**SEC-026 — die Annahme von SEC-006 gilt weiter, in neuer Fassung.**
Woertlich: *"wer dort schreiben kann, hat den Nutzerkontext ohnehin — **oder
der Nutzer hat auf den Ordner gezeigt**."*

**Was diese Fassung traegt und was nicht:** Sie traegt, weil die Zustimmung
seit T-145/T-166 **informiert** ist — der Panel-Text und das README sagen
beide, dass eine Bibliothek **aus dem gewaehlten Ordner ausgefuehrt** wird.
Sie traegt **nicht** fuer den Automatikweg ohne Nutzerhandlung; genau deshalb
ist der Laufwerks-Rueckfall `C`–`H` in T-164 gefallen (SEC-031).

**Ausdruecklich nicht gewaehlt: eine Herkunftspruefung der DLL.** Der
`security-reviewer` hat die Falle selbst benannt — sie machte
**SEC-016/017/018 wieder scharf** (Entpackbomben waeren dann der verbleibende
Weg), und ein falsches Nein machte den Erststart erneut zur Sackgasse.
**Diese Randbedingung gilt fort und ist mitzuzitieren.**

**Vor der Weitergabe von 1.9.0 vorzubereiten** (alle drei vom Nutzer
beauftragt):

1. **Hinweispaket neu erzeugen** — es wurde in T-174 beim `rm -rf dist build`
   versehentlich geloescht (vom `release-manager` selbst gemeldet). Aus vier
   versionierten Quellen reproduzierbar: `LICENSE`, `THIRD_PARTY.md`,
   `licenses/`, `vendor/Paramdex/NOTICE` — alle vier vorhanden, vom Director
   nachgesehen. **Ohne es verletzt ein Release A-020**, das der Nutzer am
   selben Tag abgenommen hat.
2. **Release-Beschreibung nachziehen** (A-023, A-024):
   `docs/release/RELEASE_TEXT.md:41-49` und `:91-99` tragen dieselbe Luecke,
   die das README bis zum 09.09. hatte — **der Satz ueber die ausgefuehrte
   Bibliothek fehlt dort.**
3. **QA-207 — bestaetigt: nur nach vorn.** Die zwoelf bestehenden Pakete
   bleiben unangetastet; **das neue bekommt die richtige Ordnerstruktur**, so
   dass der Verweis in `THIRD_PARTY.md` nicht mehr ins Leere laeuft.

---

## Pruefung 2026-09-12 (compliance-agent, T-210, Modus `pruefen`, Stand `7c3a260`)

Ergebnis je Auflage — **Feststellung, keine Abnahme**; "erfuellt" und
"abgenommen" setzt nur der Nutzer. Volltext, Belege und Fundstellen in
`docs/berichte/T-210-compliance-agent.md`. **Keine Auflage steht auf ROT.**

| ID | Ampel | Pruefergebnis 2026-09-12 | Beleg / was fehlt |
|---|---|---|---|
| A-001 | GRUEN | erfuellt | `tests/golden/weapon_damage.json`: 18 Faelle, nur Namen, IDs, Zahlen, projekteigener Panel-Text; keine Spielprosa |
| A-002 | GELB | **offen** | kein maschineller Waechter gegen Spielprosa im Fixture gefunden (Suche `prose\|flavour\|A-001\|Beschreibung\|caption` in `tests/` und `scripts/`, 0 einschlaegige Treffer; `capture_weapon_damage.py` filtert nicht). Adressat developer |
| A-003 | GELB | erfuellt | README trennt: Z. 57 und Disclaimer ("The released executable contains no game data") vs. Z. 631-632 ("Screenshots in this README show the tool's own interface…"); der absolute Satz "distributes none" kommt im README nicht mehr vor (Volltextsuche 0 Treffer) |
| A-004 | GELB | erfuellt | `THIRD_PARTY.md` Abschnitt "Game data": Aussage auf das Programm/den Release-Lauf bezogen, kein absoluter Repo-Satz |
| A-005 | — | erfuellt (dauerhaft) | README-Disclaimer Z. 621-623 unveraendert vorhanden |
| A-006 | — | kein Ereignis | keine Monetarisierung beobachtet |
| A-007 | — | erfuellt | 18 Faelle (gezaehlt: `"case"`-Vorkommen), unter "einige Dutzend" |
| A-008 | GELB | **offen** | `release.yml` prueft weiterhin nur `nrplanner/data/` ("Refuse to ship game data", Z. 81-87); kein pytest-Lauf und kein tests/-Waechter (u. a. `test_release_spec_datas.py`) im Release-Lauf — die Absicherung liegt allein in `tests.yml`. Adressat developer |
| A-009 | — | kein Ereignis | kein Takedown (A-035-Auskunft 07.09.) |
| A-010 | ROT (sperrt nicht) | zurueckgestellt (Nutzer) | unveraendert; Entscheid 02.09. gilt |
| A-011 | GELB | ruht | bedingt auf Weg N-b; gegenstandslos, solange A-010 zurueckgestellt ist |
| A-012 | GELB | **offen** | keine Quellenangabe an den sieben Einbindungsstellen im README (Bilder stehen ohne Bildunterschrift); der Disclaimer-Satz am Ende ist nach C-002 keine Quellenangabe an der Zitatstelle (§ 63 Abs. 1 UrhG). Adressat technical-writer |
| A-013 | GELB | **teilweise** | Nightlords-Auswahl im Code festgelegt (`make_screenshots.py:136-142`, `bosses[0]`); World-Events-Detailkarte weiterhin nicht festgelegt — genau die Karte, vor der C-002 Befund 7 warnt ("Curse of the Demon", vollstaendig Spielprosa), kann bei der naechsten Neuaufnahme ins Bild rutschen. Faellig vor der naechsten Neuaufnahme. Adressat developer |
| A-014 | GELB | eingehalten (Ergebnis) | die drei neuen PNG unter `design-review/2026-09-12/` wurden in diesem Lauf gegen A-010 geprueft: keine Spielprosa (nur Reliknamen, funktionale Effektzeilen, eigene Zahlen). **Der Prozess lief nicht von selbst** — die Pruefung fand erst durch T-210 statt, nicht vor dem Commit |
| A-015 | — | offen (Nutzer) | alte `nightlords.png` weiterhin in der Git-Historie; Entscheidung liegt beim Nutzer |
| A-016 | GELB | gilt fort | Nutzerentscheidung 01.09. (privat, keine Einnahmen) unveraendert |
| A-017 | GELB | erfuellt, soweit pruefbar | keine Spielgrafik ausserhalb des Oberflaechenkontexts im Repo gefunden; App-Icon ist eigenerzeugt (README Z. 634-636). **Social-Preview-Bild des Repos ohne `gh` nicht pruefbar** |
| A-018 | GELB | eingehalten | kein Bild zeigt einen Katalog in nennenswertem Umfang; die Picker-PNG zeigen das eigene Inventar (55 Relikte), nicht den Effektkatalog (652) |
| A-019 | GELB | eingehalten | README: 0 Treffer fuer "fair use" / "Video Policy" (case-insensitive) |
| A-020 | ROT→erfuellt | erfuellt, abgenommen (Nutzer 09.09.) | unveraendert |
| A-021 | GELB | erfuellt (Feststellung) | `THIRD_PARTY.md` ist die Hinweisdatei: woertliche Copyright-Vermerke aus den Wheels je Komponente, Qt-Quellfundstelle, Relink-Absatz; Volltexte in `licenses/` fuer alle sechs gebuendelten Komponenten vorhanden. Abnahme setzt der Nutzer |
| A-022 | GELB | erfuellt (Ist, Aktenlage) | Repo oeffentlich (geprueft 06.09., `CLAUDE.md`); PySide6 unveraendert 6.11.1 — kein Upgrade, keine Neu-Lektuere faellig |
| A-023 | GELB | erfuellt fuer den Bestand; Restpflicht beim naechsten Release | Bestand: zwoelf Beschreibungen nachgeruestet (Nachweis Director 08.09.). Kuenftig: `RELEASE_TEXT.md` Variante A liegt fertig vor — **einfuegen muss sie der release-manager beim Release** |
| A-024 | GELB | erfuellt | README "Where your data lives" und beide Varianten in `RELEASE_TEXT.md` tragen den Transparenztext **einschliesslich des Satzes ueber die ausgefuehrte Bibliothek** (Z. 44-48 bzw. 98-102) — die Registernotiz vom 09.09. (Luecke in Z. 41-49/91-99) ist damit ueberholt |
| A-025 | GRAU→entschieden | entschieden (Nutzer 09.09.: FORTSETZEN) | laut diesem Register sperrt A-025 nicht mehr. **Hinweis:** der T-210-Auftrag/`docs/state.md` fuehrt A-025 als offen — Widerspruch der Buchfuehrung, vom Director zu klaeren; die Zeile in der C-003-Tabelle oben traegt noch "offen" |
| A-026 | GRUEN | erfuellt (Feststellung) | SEC-023 "behoben", Retest T-185 vom 12.09. (`security/findings.md` Z. 41) — mit dort dokumentierter Randbedingung (geschlossen an der Quelle, nicht an der Senke) |
| A-027 | GRUEN | erfuellt | README "Where your data lives": Cache-Pfad `%LOCALAPPDATA%\NightreignHelper` und Loeschung ("Uninstalling means deleting…") |
| A-028 | GRUEN | erfuellt | README Z. 470-473 und `RELEASE_TEXT.md` beide Varianten ("Before you run it: back up your save…", read-only, AS IS) |
| A-029 | GRAU | **offen** | was fehlt: das Upstream-Issue bei Paramdex ist nicht belegt, und `vendor/Paramdex/NOTICE` sagt selbst, der Commit sei nicht gepinnt ("Note on provenance"). Faellig bei Gelegenheit bzw. beim naechsten Refresh |
| A-030 | GRUEN | erfuellt | `tests/test_release_spec_datas.py` existiert (Waechtertest fuer `datas` in der Spec) |
| A-031 | GELB | **offen — Bedingung ungeklaert** | was fehlt: `NightreignHelper.spec:97` setzt `upx=True`; ob die ausgelieferten EXEs tatsaechlich UPX-gepackt sind, haengt davon ab, ob der Runner UPX hatte (PyInstaller ueberspringt still; ungeprueft). Feststellung am Artefakt oder `upx=False` — Adressat release-manager; falls gepackt: UPX-Lizenzausnahme fehlt im Hinweispaket (`licenses/` enthaelt keine UPX-Datei) |
| A-032 | — | kein Ereignis | kein Netz, kein Schreiben, keine Monetarisierung, kein Modell, keine Gesellschaft, keine Bewerbung beobachtet |
| A-033 | GELB | ausgefuehrt, Nachweis erbracht; **Abnahme durch den Nutzer offen** | Datum-Feld oben in diesem Lauf nachgetragen (08.09.; 60-Tage-Ende 07.11.2026) |
| A-034 | GELB | erfuellt nach letzter Pruefung (08.09.: 12 Tags) | in diesem Lauf nicht neu pruefbar (Rolle ohne git/gh-Zugriff) |
| A-035 | — | erfuellt | Nutzerauskunft 07.09.: keine Beanstandung |
| A-036 | — | erfuellt | Nutzerauskunft 07.09.: durchgehend oeffentlich |

**Befund ohne bestehende Auflage (braucht eigene Klaerung, naechste freie
Nummer ist C-005 — C-004 ist vergeben):** Die drei Programmfenster-Abzuege
unter `design-review/2026-09-12/` (und die sechs aelteren unter
`design-review/2026-09-01/` und `2026-09-02/`) sind **keine "Spieldaten" im
Sinne des Repo-Verbots** (das zielt auf extrahierte Bestaende:
`nightreign_data.json`, Icon-Pack) und **keine Bildschirmabzuege im Sinne von
NH-002** (`QWidget.grab()` greift nur das Programmfenster). Der richtige
Massstab ist C-002 — dessen foermlicher Gegenstand aber nur die sieben Dateien
unter `docs/screenshots/` waren. Inhaltlich bestehen alle drei PNG die
C-002-Kriterien (keine Spielprosa, Spielgrafik nur im Oberflaechenkontext,
kein Katalog in nennenswertem Umfang); **die foermliche Erstreckung des
C-002-Massstabs auf `design-review/` und kuenftige Bildbestaende ausserhalb
`docs/screenshots/` ist nie geklaert worden** und legt dieser Lauf
(Modus `pruefen`) nicht selbst an.

---

## Auflagen fuer ein lokal gebautes, nicht weitergegebenes Artefakt (compliance-agent, T-241a, Modus `auflagen`, Stand `29224fa`, 2026-09-14)

**Frage:** Welche der Auflagen A-001 bis A-036 gelten fuer
`dist/NightreignHelper.exe` 1.10.0, wenn sie heute nur auf dem Rechner des
Nutzers gebaut und von ihm selbst gestartet wird — und welche erst bei
Weitergabe oder Release? **Ampel fuer den heutigen Zweck: GRUEN.** Keine
Auflage steht auf ROT; keine Auflage wird durch Bau und Eigenlauf ausgeloest.

Keine Rechtsberatung im rechtlichen Sinn; belegte Einschaetzung mit
offengelegten Quellen. Keine neue Klaerung — C-003 bleibt Massstab, keine
`C-005.md` angelegt.

**Warum die Weitergabe die Schwelle ist (belegt):**

- **Lizenzpflichten reisen mit der Kopie.** GPL-3.0 § 0: *"To 'convey' a work
  means any kind of propagation that enables other parties to make or receive
  copies"*; Ausfuehren und Aendern einer privaten Kopie sind ausdruecklich
  keine Propagation (`licenses/GPL-3.0.txt` Z. 92-101,
  <https://www.gnu.org/licenses/gpl-3.0.txt>). LGPL-3.0 § 4 knuepft alle
  Hinweis- und Relink-Pflichten an *"You may **convey** a Combined Work …
  if you also do each of the following"* (`licenses/LGPL-3.0.txt` Z. 79-87,
  <https://www.gnu.org/licenses/lgpl-3.0.txt>). BSD-3/BSD-2 Kl. 2:
  *"**Redistributions** in binary form must reproduce…"*
  (`licenses/zstandard-LICENSE.txt` Z. 10, `pycryptodome-LICENSE.rst` Z. 48,
  `Pillow-LICENSE.txt` Z. 693 ff.). Abrufdatum aller drei: 2026-09-14
  (Volltexte aus dem Repo, identisch mit den Upstream-Fassungen).
  → **A-020, A-021, A-023, A-031, A-033 greifen erst bei Weitergabe.**
- **§ 95a UrhG** (<https://www.gesetze-im-internet.de/urhg/__95a.html>,
  abgerufen 2026-09-14): Abs. 3 verbietet u. a. Herstellung, Verbreitung und
  *gewerblichen Zwecken dienenden* Besitz von Umgehungsvorrichtungen nach
  Nr. 1-3; **§ 108b Abs. 1** stellt die Umgehung nur unter Strafe, *"sofern
  die Tat nicht ausschliesslich zum eigenen privaten Gebrauch … erfolgt"*,
  Abs. 2 die Herstellung nur *"zu gewerblichen Zwecken"*
  (<https://www.gesetze-im-internet.de/urhg/__108b.html>, abgerufen
  2026-09-14). Der Eigenlauf gegen die eigene Installation ist der
  privateste denkbare Fall; ob die EXE ueberhaupt eine Vorrichtung nach
  Abs. 3 Nr. 3 ist, hat C-003 Befund 5 als GRAU bewertet, und der Nutzer hat
  dieses Restrisiko am 09.09. fuer 13 veroeffentlichte Kopien ausdruecklich
  uebernommen. **Ein weiterer lokaler Bau fuegt dem nichts hinzu.**
  Ehrlichkeitshalber: "Herstellung" steht in Abs. 3 neben "Verbreitung" —
  die Schwelle liegt also nicht bei Null, sondern bei dem GRAU, das bereits
  entschieden ist.
- **In einfachen Worten:** Was Daniel auf seinem Rechner fuer sich selbst
  baut und startet, sieht niemand und bekommt niemand. Alle Pflichten, die
  das Register kennt, entstehen erst, wenn eine Kopie den Rechner verlaesst
  — oder sie betreffen das oeffentliche Repo, das vom Bau unberuehrt bleibt.

**Risiko heute:** Haftung Nutzer persoenlich / droht nichts, was nicht schon
mit den 13 Releases im Raum steht / theoretisch moeglich, praktisch nicht
relevant (kein Dritter erhaelt eine Kopie, kein Rechteinhaber sieht sie) /
**Schwelle: die erste Kopie an einen Dritten** — auch per Chat, USB-Stick
oder Testkopie an einen Freund, nicht nur ein GitHub-Release.

### Einordnung je Auflage (Stand gegen den Baum `29224fa`, 14.09.2026)

Spalte "heute": **ja** = gilt fuer Bau und Eigenlauf · **Repo** = gilt
unabhaengig vom Artefakt, weil das Repo oeffentlich ist; der Bau aendert
nichts daran · **Weitergabe** = greift erst mit der ersten Kopie an Dritte ·
**Ereignis** = greift nur bei dem genannten Ereignis.

| ID | heute | Stand 14.09. gegen Baum | Beleg |
|---|---|---|---|
| A-001 | Repo | erfuellt | Fixture 18 Faelle (`"case"` gezaehlt), nur Namen/IDs/Zahlen |
| A-002 | Repo | **offen** (developer, vor Merge) | Suche `prose\|flavour\|A-001\|description` in `test_weapon_damage_golden.py`, `weapon_damage_cases.py`, `capture_weapon_damage.py`: 0 Treffer — kein Waechter |
| A-003 | Repo | erfuellt | README Z. 626 "contains no game data" vs. Z. 631 "Screenshots … show the tool's own interface"; "distributes none" 0 Treffer. *README wird parallel vom technical-writer geaendert (T-241b) — nach dessen Lauf neu lesen* |
| A-004 | Repo | erfuellt | `THIRD_PARTY.md` Z. 106 "Game data — not third party, not distributed at all" |
| A-005 | Repo | erfuellt | README Z. 621-623 |
| A-006 | Ereignis | kein Ereignis | — |
| A-007 | Repo | erfuellt | 18 Faelle |
| A-008 | Weitergabe (Release-Lauf) | **offen** (developer) | `release.yml` Z. 81-87 prueft nur `nrplanner/data/`; `pytest` kommt in der Datei nicht vor (Suche `pytest`: 0 Treffer) |
| A-009 | Ereignis | kein Ereignis | — |
| A-010 | Repo | zurueckgestellt (Nutzer 02.09.) | unveraendert |
| A-011 | Repo | ruht | bedingt auf A-010 |
| A-012 | Repo | **offen** (technical-writer) | 7 Bildeinbindungen (`![…](docs/screenshots/…)` Z. 92-390) ohne Quellenangabe an der Stelle |
| A-013 | Repo (vor Neuaufnahme) | **teilweise** (developer) | `make_screenshots.py:136-142` legt nur Nightlords fest; World Events (Z. 47) ohne festgelegten Eintrag |
| A-014 | Repo (vor Veroeffentlichung) | eingehalten | keine neuen Registerkarten seit T-210; Chip `BEST FOR ATTRIBUTES` (T-240) ist eigener Text |
| A-015 | Ereignis | offen (Nutzer) | unveraendert |
| A-016 | Ereignis | gilt fort | Nutzerentscheid 01.09. |
| A-017 | Repo | erfuellt, soweit pruefbar | wie T-210; Social Preview ohne `gh` nicht pruefbar |
| A-018 | Repo | eingehalten | wie T-210 |
| A-019 | Repo | eingehalten | README "fair use"/"Video Policy" 0 Treffer |
| A-020 | Weitergabe | erfuellt, abgenommen (09.09.) | fuer 1.10.0 bei Release erneut: Hinweispaket als Asset |
| A-021 | Weitergabe | erfuellt (Feststellung) | `THIRD_PARTY.md` + 6 Dateien in `licenses/` (gezaehlt) |
| A-022 | Repo, dauerhaft | erfuellt (Aktenlage) | Repo PUBLIC (06.09., `CLAUDE.md`); `requirements.txt:4` PySide6==6.11.1 unveraendert — keine Neu-Lektuere faellig |
| A-023 | Weitergabe | Restpflicht beim Release | `RELEASE_TEXT.md` vorhanden; einfuegen beim Release (release-manager) |
| A-024 | Weitergabe | erfuellt | README "Where your data lives" Z. 438 ff.; `RELEASE_TEXT.md` |
| A-025 | — | entschieden (FORTSETZEN, 09.09.) | oben an der Fundstelle geschlossen (QA-243) |
| A-026 | Weitergabe (empfohlen) | erfuellt (Feststellung) | SEC-023 "behoben", `security/findings.md` Z. 41, mit Randbedingung |
| A-027 | Weitergabe (empfohlen) | erfuellt | README Z. 438 ff. |
| A-028 | Weitergabe (empfohlen) | erfuellt | README Z. 471 "Back up your save…" |
| A-029 | Ereignis (Refresh) | **offen** | `vendor/Paramdex/NOTICE` Z. 41-44 "Note on provenance … should be pinned" |
| A-030 | Weitergabe (empfohlen) | erfuellt | `tests/test_release_spec_datas.py` vorhanden |
| A-031 | Weitergabe, **bedingt** | offen — Bedingung heute pruefbar | `NightreignHelper.spec:97` `upx=True`; ROLLOUT.md Z. 88-89 und T-174 Z. 64: kein `upx` im PATH, also bisher nicht gepackt. **T-241c meldet `upx` ja/nein** — bei "ja" wird A-031 vor der Weitergabe von 1.10.0 konkret (UPX-Lizenzausnahme ins Hinweispaket) |
| A-032 | **ja** (Schwellenwaechter) | kein Ereignis | 1.10.0 neu: Steam-Herkunftspruefung liest Registry/`libraryfolders.vdf` — lokal, lesend, kein Netz; keine Schwelle beruehrt |
| A-033 | Weitergabe (Bestand) | ausgefuehrt 08.09.; Abnahme Nutzer offen | ohne `gh` nicht neu pruefbar |
| A-034 | Repo, dauerhaft | erfuellt nach letzter Pruefung (08.09.) | ohne `git`/`gh` nicht neu pruefbar |
| A-035 | Ereignis | erfuellt | Nutzerauskunft 07.09. |
| A-036 | — | erfuellt | Nutzerauskunft 07.09. |

**Ergebnis:** Fuer den heutigen Zweck gilt nur **A-032** (und die
dauerhaften Repo-Auflagen, die der Bau nicht beruehrt). **Vor der ersten
Weitergabe von 1.10.0** sind faellig: A-020 (Hinweispaket als Asset), A-023
(Release-Beschreibung), A-031 (falls UPX), A-008 (empfohlen dringend, Release-
Lauf ohne Testabsicherung), A-033-Abnahme durch den Nutzer. Offen und nicht
weitergabesperrend: A-002, A-012, A-013, A-029.

**QA-243 aufgeloest (14.09.):** Kopftext C-003-Abschnitt, Zeile A-020, Zeile
A-025 und der Satz "Was jetzt noch die Veroeffentlichung sperrt" an der
Fundstelle geschlossen (Durchstreichung, Datum, Verweis). Die spaeteren
Abschnitte bleiben als Verlauf. Volltextsuche nach der veralteten Aussage
(14.09.): "sperrt das Release" 3 Treffer — Z. 71 durchgestrichen, Z. 211
Verlauf der ersten Runde 09.09. (durch die zweite Runde direkt darunter
ueberholt, absichtlich stehen gelassen), Z. 435 dieser Satz;
"GRAU \| Nutzer \| \*\*jetzt\*\*" 0 Treffer; "ROT bis erfuellt" 0 Treffer.

**Nebenfund (Director):** `docs/state.md:12` fuehrt "A ab **A-033**"; vergeben
ist bis A-036 (C-004). Kein Handlungsbedarf fuer heute.

**Nachpruefen ab:** erste Weitergabe von 1.10.0 (dann Modus `pruefen` gegen
A-020/A-023/A-031 am Artefakt) · T-241b-Ergebnis am README (A-003, A-005,
A-019, A-024, A-027, A-028 neu lesen) · 2026-11-07 (60-Tage-Ende GPL § 8).

---

## Auflagen fuer Bau und Eigenlauf 1.12.0 und die Screenshot-Neuaufnahme (compliance-agent, Modus `auflagen`, Stand `02e0721`, 2026-09-15)

**Frage:** Gilt die T-241a-Einordnung (Bau und Eigenlauf: GRUEN) auch fuer
1.12.0, und welche Bedingung muss die heute neu erzeugte `nightlords.png`
erfuellen, damit A-010 nicht neu aufreisst? **Ampel Bau/Eigenlauf: GRUEN.
Ampel Screenshot-Neuaufnahme: GELB** — zulaessig unter den drei Bedingungen
S1-S3 unten. Keine Rechtsberatung im rechtlichen Sinn; keine neue Klaerung,
C-002 und C-003 bleiben Massstab, keine `C-005.md` angelegt. Die
T-241a-Tabelle (A-001 bis A-036) gilt unveraendert fort; nur die Zeilen
unten sind neu.

### Neu seit 1.10.0 — nichts davon beruehrt eine Auflage oder eine A-032-Schwelle

| Neuerung | Ampel | Befund | Beleg (Baum `02e0721`) |
|---|---|---|---|
| Effektmarkierung (A18/A19) | GRUEN | Zwei feste `QSettings`-Schluessel `advisor/excluded`, `advisor/required`; Inhalt ausschliesslich Effekt-IDs (Integer, kommagetrennt) im Profil des Nutzers selbst. Keine Daten Dritter, kein Netz, keine Weitergabe — Haushaltsausnahme Art. 2 Abs. 2 lit. c DSGVO (Norm wie in C-001 belegt, heute nicht neu abgerufen) | `nrplanner/effectfilters.py` Z. 34-36, 61-66 |
| Zweihand-Kalibrierungen | GRUEN | `Calibration(factor, reason)`: der Faktor ist gemessen, `reason` ist eigener Satz ("Raider two-handing", "two-handing", "Raider with a greataxe or great hammer"); kein Spieltext | `nrplanner/weapons.py` Z. 81, 133-138, 199-200; `damage.py` Z. 507-515 |
| Gefaess-Tooltip | GRUEN | Gefaessname (Item-Name, Kategorie A-001 "zulaessig"), Farbnamen, drei eigene Konstanten (`WHY_SEVERAL_VESSELS`, `WHITE_SLOT_TAKES_ANY`, "Equipped in game"); keine Spielprosa | `nrplanner/app.py` Z. 232-234, 245-265 |
| Gate-Wortlaute | GRUEN | `CONDITIONS`, `ATTACK_CONDITIONS`, `restricted_to`: eigener Text. Die Spiel-Caption (`info`) laeuft unveraendert ueber `caption()` und war schon Gegenstand von C-002 (`effects.png`, "funktionale Effektzeilen") — nicht neu | `nrplanner/effecttext.py` Z. 26-30, 74-91, 224-228 |
| Icon-Manifest-Pruefung | GRUEN | liest das lokale `manifest.json`, baut bei Abweichung neu; kein Netz, UNC-/Absolutpfade gesperrt (SEC-046) | `nrplanner/firstrun.py` Z. 86-149 |

### Screenshots — was das neue Bild erfuellen muss

**Sachverhalt (Bild und Code gelesen 15.09.):** Die heute committete
`docs/screenshots/nightlords.png` zeigt **zehn vollstaendige
Beschreibungstexte** auf den Karten und **denselben Text ein elftes Mal** im
Detailbereich (Gladius) — exakt der Zustand aus C-002 Befund 1.
`nrplanner/bosstab.py` gibt die Beschreibung weiterhin auf jeder Karte
(Z. 367) und im Detail (Z. 799) aus; `scripts/make_screenshots.py` waehlt
`bosses[0]` (Z. 136-142). **Ein Lauf des unveraenderten Skripts erzeugt also
wieder dasselbe Bild mit denselben elf Prosabloecken.**

**Bewertung:** Der Nutzerentscheid vom 02.09. ("C-002 wird ignoriert, sperrt
nichts mehr, wird nicht erneut vorgelegt") betrifft den **Befund** — zehn
Beschreibungen im Nightlords-Bild —, nicht einen Dateihash. Ein neues Bild
mit **demselben** Inhalt ist derselbe Befund und reisst A-010 nicht neu auf;
juristisch ist jeder Commit zwar eine neue Vervielfaeltigung (§ 16 UrhG,
Volltext in C-002), das Risiko aendert sich aber nicht, weil die alte Fassung
ohnehin in der Historie abrufbar bleibt (A-015). **Neu aufreissen** wuerde
A-010 nur, wenn das Bild **mehr oder andere** Spielprosa traegt als heute —
dann ist es ein neuer Sachverhalt, den der Entscheid vom 02.09. nicht deckt,
und A-014 verlangt die Vorlage. **In einfachen Worten:** Was Daniel am 02.09.
hingenommen hat, darf so bleiben; es darf nur nicht mehr werden.

**Risiko:** Nutzer persoenlich / DMCA-Takedown, theoretisch Abmahnung /
praktisch gering, unveraendert seit C-002 / Schwelle: Push nach `main`
(Repo oeffentlich); verschaerft bei Bewerbung oder weiterer Prosa.

| ID | Auflage | Ampel | Adressat | Faellig | Status |
|---|---|---|---|---|---|
| S1 (zu A-010/A-014) | Die neue `nightlords.png` zeigt **hoechstens die Spielprosa der heutigen Fassung**: die zehn Kartenbeschreibungen und einmal die Beschreibung von `bosses[0]` im Detail. Kein zusaetzlicher Prosablock (z. B. eigene Everdark-Beschreibung, weiterer Textabschnitt). Pruefung durch Anschauen des erzeugten Bildes, Zaehlung der Prosabloecke im Bericht (heute: 11) | GELB | technical-writer (Zaehlung), director (Abgleich) | heute, vor dem Commit der Bilder | offen |
| S2 (zu A-013) | Die neue `world_events.png` zeigt **nicht** die Karte "Curse of the Demon / Libra" (C-002 Befund 7: vollstaendige Spielprosa). `eventstab.py` Z. 163 waehlt Zeile 0 ("Fell Omen"), das ist heute deterministisch, aber **nicht im Skript festgelegt** — A-013 bleibt teilweise. Pruefung am erzeugten Bild | GELB | technical-writer (Pruefung); developer (A-013 im Skript, spaeter) | heute | offen |
| S3 (zu A-018) | Bildgroesse im Skript unveraendert (2156 x 1140, `make_screenshots.py` Z. 37); die Zahl sichtbarer Effektzeilen in `effects.png` bleibt in der Groessenordnung von C-002 (35 von 652). Nur zaehlen, wenn das Bild erkennbar dichter geworden ist | GRUEN (empfohlen) | technical-writer | heute | offen |
| A-012 (Stand) | **Unveraendert offen** — 7 Einbindungen ohne Quellenangabe an der Stelle (README Z. 99, 289, 316, 352, 383, 410, 431). Faellig laut C-002 "vor dem naechsten Push nach `main`", also seit 01.09. ueberfaellig. **Inhalt, den die Zeile tragen muss** (kein Fertigtext): Spieltitel ELDEN RING NIGHTREIGN, Rechteinhaber (FromSoftware / Bandai Namco Entertainment), dass Grafiken und Texte im Bild aus dem Spiel stammen — einmal ueber der Bilderfolge oder einmal je Abschnitt, § 63 Abs. 1 UrhG (Fundstelle in C-002). Der technical-writer ist heute im README; die Zeile kostet ihn eine Zeile | GELB | technical-writer | vor dem naechsten Push nach `main` | **offen, ueberfaellig** |
| A-014 (Stand) | Modul-Docstring von `make_screenshots.py` traegt die A-010-Regel weiterhin nicht (Suche `A-010\|Spielprosa\|game prose\|description text` in `scripts/`: 0 Treffer, 15.09.) | GELB | developer | bei naechster Aenderung des Skripts | offen |

**Weg N-c bleibt billig und bleibt angeboten, nicht verlangt:** die
Beschreibungslabels vor dem `grab()` auszublenden ist eine Skriptaenderung
von wenigen Zeilen; der Nutzer hat am 02.09. entschieden, das nicht zu tun.
Diese Zeile ist keine erneute Vorlage, sondern der Vermerk, dass der Weg
offen steht.

**Entscheidungsvorlage fuer den Nutzer:** keine — S1-S3 sind Pruefungen,
A-010 ist entschieden, A-012 ist eine bestehende Pflicht ohne offene Wahl.

**Anwaltlich zu klaeren:** nichts.

**Nicht geprueft:** das gebaute Artefakt 1.12.0 selbst (UPX, A-031 — meldet
der release-manager); `deep_of_night.png` und die uebrigen vier Bilder
inhaltlich (unveraenderte Registerkarten laut CHANGELOG 1.10.1-1.11.0;
`deeptab.py` Z. 272 zitiert die Spiel-Caption gekennzeichnet — die Form, die
C-002 Befund 7 als Vorlage nennt); `CHANGELOG.md` fuehrt 1.11.0 als letzte
Version, `nrplanner/__init__.py` sagt 1.12.0 — Nebenfund fuer den
technical-writer, keine Auflage.

**Nachpruefen ab:** Commit der neuen Bilder (S1-S3 am Ergebnis) · erste
Weitergabe von 1.12.0 (A-020/A-023/A-031 am Artefakt) · 2026-11-07.

---

## Auflagen vor der Veroeffentlichung 1.13.1 (compliance-agent, T-283c, Modus `auflagen`, Stand `1f51485`, 2026-09-16)

**Frage:** Darf 1.13.1 als dreizehntes Release (erstes seit `v1.7.1`) auf
GitHub erscheinen? **Gesamtampel GELB** — ja, sobald der `release-manager`
Variante A aus `docs/release/RELEASE_TEXT.md` Z. 36-77 wortgenau an den
Anfang der Release-Beschreibung setzt und die Asset-Liste drei Dateien zeigt.
Nichts steht auf ROT. Volltext, Normen, Pflichttext: `C-006.md`. Die
T-241a-Tabelle gilt fort; nur die genannten Zeilen sind neu bewertet.

| ID | Ampel | Stand 16.09. gegen `1f51485` | Beleg |
|---|---|---|---|
| A-008 | GRUEN | **erfuellt** (Baum) | `release.yml` Z. 84-94: `pip install -r requirements-dev.txt` und `python -m pytest -rs` vor dem Bau (Z. 96), bewacht mit `hashFiles('tests/**')`; `requirements-dev.txt` vorhanden; `.gitignore` schliesst `tests/` nicht aus. Wirkung im Job-Log des Tag-Laufs nachweisen (release-manager) |
| A-020 | GRUEN | erfuellt (Workflow unveraendert) | `release.yml` Z. 127-159: vier Pflichtpfade geprueft, `NightreignHelper-notices.zip` in `files:`; `licenses/` 6 Volltexte (gezaehlt). Nach dem Lauf `gh release view v1.13.1`: drei Assets |
| A-023 | GELB | Text fertig; **Einsatz beim Release offen** | `RELEASE_TEXT.md` Variante A traegt T2 (1)-(6) vollstaendig; `generate_release_notes` setzt ihn nicht ein — von Hand an den Anfang der Beschreibung (release-manager). Norm: § 23 Abs. 1 Nr. 3, Abs. 2 MarkenG (abgerufen 16.09.) |
| A-024 | GELB | Text fertig; Einsatz mit A-023 | Variante A Z. 41-51 einschliesslich Bibliothekssatz; README Z. 733-743 und "Where your data lives" unveraendert |
| A-030 | GRUEN | erfuellt | `test_release_spec_datas.py` Z. 27-30 Literal = Spec Z. 70-73; laeuft seit `c148585` auch im Release-Lauf |
| A-031 | GRUEN | Bedingung nicht eingetreten | lokal kein UPX (T-282 Z. 34); Runner-Images Windows 2022 (20260907.297.1) und 2025 (20260907.255.1) fuehren kein UPX (runner-images Readmes, abgerufen 16.09.). Nebenfund: `upx=False` in der Spec waere Absicht statt Zufall (developer, bei Gelegenheit) |
| A-033 | GRUEN | ausgefuehrt 08.09.; **foermliche Abnahme Nutzer offen** | 60-Tage-Ende 2026-11-07 laeuft; ein konformes neues Release unterbricht nichts |
| A-035 | GRUEN | erfuellt (Auskunft 07.09.) | Nutzer bestaetigt vor dem Tag kurz, dass seither nichts einging |
| A-037 | GRUEN (empfohlen) | **neu, offen** | Release-Text beim Erzeugen mitgeben (`body_path`/`append_body` in `release.yml`), damit die Download-Seite nie ohne A-023/A-024-Text oeffentlich ist — developer, vor dem uebernaechsten Release |

**Entscheidungsvorlage:** A-033 foermlich abnehmen (A-020-Abnahme vom 09.09.
deckte dieselbe Arbeit) · A-035: Beanstandung seit 07.09.? · Release-Freigabe
selbst bleibt Nutzersache (A-025 deckt die EXE-Weitergabe).

**Anwaltlich zu klaeren:** nichts. **Nicht geprueft:** Git-Tracking von
`tests/` (Rolle ohne git — Annahme aus `.gitignore`); der Tag-Lauf selbst;
Netz- und Dateizugriffe des Codes (T-283b). **Nachpruefen ab:** Tag-Lauf
`v1.13.1` (Assets, Job-Log, Text) · 2026-11-07 · Aenderung an `release.yml`,
Spec oder `RELEASE_TEXT.md`.

---

## Stand 1.18.0 (compliance-agent, T-328b, Modus `pruefen`, Baum `7955a8a`, 2026-09-21)

**Frage:** Entsteht durch die fuenf Releases 1.14.0 (`ffac292`) bis 1.18.0
(`1ae6952`) eine neue Auflage, oder wechselt eine bestehende ihren Status?
**Ergebnis: keine neue Auflage; vier Statuswechsel, alle zum Besseren
(A-012, A-023, A-024, A-037). Nichts steht auf ROT.** Feststellung, keine
Abnahme. Keine Rechtsberatung im rechtlichen Sinn. Nur Aenderungen gegen die
Tabellen T-241a und T-283c; alles nicht Genannte gilt dort unveraendert fort.
Rolle ohne git: der Diff `v1.13.1..v1.18.0` ist nicht selbst gezogen, geprueft
wurde der heutige Baum gegen den in T-283c belegten Stand `1f51485`.

| ID | Ampel | Stand 21.09. gegen `7955a8a` | Beleg |
|---|---|---|---|
| A-012 | GRUEN | **erfuellt** (war seit 01.09. ueberfaellig) | Die sieben Bildeinbindungen sind mit T-296 vom README in `docs/anleitung/guide.md` gewandert (Z. 32, 337, 364, 406, 463, 490, 511; gezaehlt); darueber steht **eine** Zeile ueber der Bilderfolge (Z. 25-28): "Every screenshot below is this tool's own interface, showing data read from a personal ELDEN RING NIGHTREIGN install. ELDEN RING NIGHTREIGN is the property of FromSoftware, Inc. and Bandai Namco Entertainment Inc." — genau der in T-267 verlangte Inhalt (Spieltitel, Rechteinhaber, Herkunft der Inhalte, einmal ueber der Folge). README traegt noch ein Bild (Z. 11) und den Rechteinhaber im Disclaimer derselben 94-Zeilen-Datei (Z. 58-62) — reicht in meiner Einschaetzung als deutliche Quellenangabe (§ 63 Abs. 1 UrhG, Fundstelle C-002); *empfohlen, nicht verlangt:* die Guide-Zeile auch unter README Z. 11 (technical-writer, eine Zeile) |
| A-023 | GRUEN | **erfuellt, dauerhaft mechanisch** (war: "Einsatz beim Release offen") | `release.yml` Z. 160 `body_path: docs/release/RELEASE_BODY.md` (eingefuehrt T-284, `docs/tasks/T-284.md:27`, also vor 1.13.2); `RELEASE_BODY.md` Z. 1-4 Nicht-Verbundenheit und Rechteinhaber, Z. 22-27 Hinweispaket. Die Handarbeit des release-managers entfaellt; `docs/state.md` Z. 28-29 fuehrt alle fuenf Releases mit dieser Beschreibung, je 3 Assets |
| A-024 | GRUEN | **erfuellt, dauerhaft mechanisch** | `RELEASE_BODY.md` Z. 6-16 Transparenztext einschliesslich Bibliothekssatz ("runs a small decompression program out of that installation folder") und "no network connection"; README Z. 64-72 wortgleich; Guide "Where your data lives" Z. 589-600 (Cache-Pfad, kein Netz, Loeschung = A-027) |
| A-037 | GRUEN | **erfuellt** (war: neu, offen) | wie A-023: `body_path` in `release.yml` Z. 160; `generate_release_notes: true` (Z. 161) haengt die Commit-Liste nur an, ersetzt den Text nicht |
| A-031 | GRUEN | Bedingung weiterhin nicht eingetreten | Spec Z. 97 weiterhin `upx=True`; `windows-latest` = Windows Server 2025, Image 20260913.261.1, kein UPX in der Werkzeugliste (<https://github.com/actions/runner-images/blob/main/images/windows/Windows2025-Readme.md>, abgerufen 21.09.2026); ROLLOUT.md Z. 498/524/545: keine UPX-Sektionen im Artefakt (T-265). Nebenfund `upx=False` bleibt Debt (`docs/state.md` Z. 64) |
| A-022 | GRUEN | unveraendert erfuellt | `requirements.txt` Z. 4 PySide6==6.11.1 — kein Upgrade seit 1.13.1, keine Neu-Lektuere faellig |
| A-020, A-021 | GRUEN | unveraendert erfuellt | `licenses/` 6 Volltexte (Glob 21.09.); `THIRD_PARTY.md` Z. 49-54 fuehrt alle fuenf Laufzeitabhaengigkeiten aus `requirements.txt` (pycryptodome, zstandard, PySide6/shiboken6, pillow, texture2ddecoder); Pillow bleibt Laufzeit (state.md Z. 36) — keine neue Abhaengigkeit in `requirements.txt` |
| A-014 | GRUEN | eingehalten | `docs/screenshots/nightlords.png` heute angesehen: 10 Kartentexte + 1 Detailtext = **11 Prosabloecke**, identisch mit der S1-Grundlage vom 15.09.; Guide Z. 408-409 sagt selbst, das Bild sei vor dem Unterboss-Baum entstanden. `world_events.png` zeigt "Fell Omen", nicht "Curse of the Demon" (S2). **S1 gilt erneut, sobald das Nightlords-Bild fuer den Unterboss-Baum neu aufgenommen wird** (Zaehlung der Bloecke im Bericht; technical-writer, director) |
| A-032 | — | kein Ereignis | Neu seit 1.13.1, nichts davon beruehrt eine Schwelle: zwei feste `QSettings`-Schluessel `hit_with`/`damage_type` (`nrplanner/advisorbar.py` Z. 137-138, 1039-1040; eigene Einstellung, Haushaltsausnahme wie Zeile "Effektmarkierung" oben); T-328a fuegt `hero` in derselben Bauform hinzu. EXTRACT_VERSION 13→16 (`nrdata/extract.py` Z. 84-103): weitere Param-Tabellen, Beute-Tabellen und Ereignisskripte (`nrdata/bossdata.py` Z. 724, 765-768) werden gelesen — **dieselben Archive, dieselben Schluessel, dieselbe spieleigene Entpackbibliothek**, kein neuer Umgehungsschritt. Kein Netz, kein Schreiben, keine Monetarisierung |

**PyInstaller nach `requirements-dev.txt` (T-296):** keine Auflage. Der
Bootloader steckt weiterhin in der EXE; die Lizenz ist GPL-2.0-or-later mit
Bootloader-Ausnahme: *"The authors give you unlimited permission to link or
embed compiled bootloader and related files into combinations with other
programs, and to distribute those combinations without any restriction
coming from the use of those files"*
(<https://raw.githubusercontent.com/pyinstaller/pyinstaller/develop/COPYING.txt>,
abgerufen 21.09.2026). `THIRD_PARTY.md` Z. 72 fuehrt ihn weiter. Hinweis,
keine Auflage: `scripts/check_licences.py` liest nur `requirements.txt`
(Z. 32-33) — die PyInstaller-Zeile in `THIRD_PARTY.md` ist damit nicht mehr
maschinell bewacht; die sechs transitiven Pins in `requirements-dev.txt`
(SEC-048) werden nicht gebuendelt (Spec analysiert `run.py`, `tests.yml`
Z. 43-53 haelt pytest aus der Laufzeit).

**Unveraendert offen, nicht weitergabesperrend:** A-002 (kein Waechter;
Suche `A-001|prose|flavour` in `tests/`, `scripts/`: nur Kommentare, kein
Fixture-Waechter), A-013 (`make_screenshots.py` Z. 141 nur `bosses[0]`,
World Events weiterhin ohne festen Eintrag), A-029 (`vendor/Paramdex/NOTICE`
Z. 41-44 "should be pinned"), A-015 (Nutzer). **Beim Nutzer:** A-033
foermliche Abnahme, A-035 Bestaetigung — 60-Tage-Ende **2026-11-07**.

**Entscheidungsvorlage:** (1) Der Nutzerentscheid vom 01.09. verlangt, das
EULA-Restrisiko "bei jeder groesseren Aenderung an der Extraktion" erneut
vorzulegen. Meine Einschaetzung: 13→16 ist keine solche — Mechanismus
unveraendert, nur mehr Tabellen; A-025 (09.09., FORTSETZEN) deckt das.
Sieht der Nutzer das anders, ist es ein `klaeren`-Auftrag, kein Register-
eintrag. (2) A-033/A-035 wie oben.

**Anwaltlich zu klaeren:** nichts. **Nicht geprueft:** der Git-Diff selbst
und die fuenf Tags (Rolle ohne git/gh — A-034 nach Aktenlage `docs/state.md`
Z. 20-26); die Job-Logs der fuenf Tag-Laeufe (A-008-Wirkung); ob das Lesen
der Ereignisskripte (`bossdata.py`) erst seit 1.15.0 besteht (Annahme: ja,
T-307); die ausgelieferten EXEs; das Social-Preview-Bild (A-017).
**Nachpruefen ab:** Neuaufnahme der Screenshots (S1/S2) · Aenderung an
`requirements.txt`, `release.yml`, Spec oder `RELEASE_BODY.md` · 2026-11-07.
