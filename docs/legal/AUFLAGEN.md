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

Gesamtampel **GELB**; A-020 sperrt das Release; A-025 ist GRAU und
Nutzerentscheidung. Volltext, Normen und Fundstellen in `C-003.md`.
**Fortgeschrieben durch C-004 (2026-09-07):** C-003 nahm an, das erste Release
stehe bevor; tatsaechlich sind seit 2026-08-11 zwoelf Releases veroeffentlicht.
A-020, A-022 und A-025 tragen unten die Fassung aus C-004; "vor
Veroeffentlichung" in den uebrigen Zeilen heisst fuer den Bestand "so bald wie
moeglich" und fuer das naechste Release "vor dessen Veroeffentlichung".

| ID | Auflage | Ampel | Adressat | Faellig | Status |
|---|---|---|---|---|---|
| A-020 | **Sperrt.** Hinweispaket als Release-Asset neben EXE und Pruefsumme: `LICENSE`, Hinweisdatei (A-021), Volltexte LGPL-3.0 und GPL-3.0, `vendor/Paramdex/NOTICE`. Umsetzung in `release.yml` `files:` (Datei bei T-105 — Auflage, keine Aenderung). **Fassung C-004:** gilt fuer die zwoelf bestehenden Releases (Nachruestung ueber A-033) und jedes kuenftige; Heilung nach GPL-3.0 § 8 nur, wenn *alle* abrufbaren Kopien konform sind | ROT bis erfuellt | developer (Workflow); release-manager (Bestand) | **seit 2026-08-11, laufender Verstoss** — so bald wie moeglich | **erfuellt, abgenommen durch Nutzer 09.09.2026** |
| A-021 | Hinweisdatei mit Copyright-Vermerk und vollstaendigem Lizenztext jeder gebuendelten Komponente, Qt/PySide6-Quellfundstelle, Relink-Absatz; Vermerke aus den Wheels | GELB | technical-writer | vor Veroeffentlichung | offen |
| A-022 | Repo bleibt oeffentlich, solange ein Release abrufbar ist (heute: zwoelf); jedes Release traegt seinen Quell-Tag; PySide6-Lizenz bei jedem Upgrade neu lesen. **Fassung C-004:** bindet seit dem ersten Release und ist nach pruefbarem Ist-Zustand erfuellt (Repo oeffentlich, 12 Tags, Quellarchive) — vorbehaltlich A-036 | GELB | Nutzer, release-manager | **dauerhaft seit 2026-08-11** | erfuellt (Ist); Verlauf offen (A-036) |
| A-023 | Nicht-Verbundenheits-Hinweis und Rechteinhaber an der Download-Stelle: fester Text der Release-Beschreibung und Hinweispaket; der absolute Satz "distributes none" wird nicht wiederholt (A-003 gilt fort) | GELB | technical-writer, release-manager | vor Veroeffentlichung | offen |
| A-024 | Transparenztext: liest und entschluesselt lokale Spieldateien/Spielstand mit community-bekannten Schluesseln, schreibt nie, kein Netz — README und Release-Beschreibung | GELB | technical-writer | vor Veroeffentlichung | offen |
| A-025 | **GRAU — Fassung C-004.** Nutzer entscheidet ausdruecklich, ob er die seit 2026-08-11 laufende Verbreitung der EXE (12 Releases, 25 Downloads) **fortsetzt** und das Restrisiko aus C-003 Befund 5 (§ 95a Abs. 3 UrhG, EULA 10(i), Steam SSA 2.G) traegt, sie **beendet** (EXE-Assets entfernen, nur Quellcode) oder **anwaltlich klaeren** laesst. Die Haltung "bewusst unentschieden" (Nutzerentscheidung 2026-09-01, oben) beschreibt seit dem 11.08. keinen bestehenden Zustand mehr | GRAU | Nutzer | **jetzt**, vor dem naechsten Release und unabhaengig davon | offen |
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
wiederhergestellt, sofern keine Anzeige einging. **Datum: —**

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

**Was jetzt noch die Veroeffentlichung sperrt:** nur A-033 (Nachruestung des
Bestands). Der Transport des Hinweispakets ist seit T-109 gebaut, der Inhalt
seit T-107 fertig.

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
