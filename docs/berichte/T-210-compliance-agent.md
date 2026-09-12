# T-210 — Compliance-Pruefung: erfuellt der Stand `7c3a260` seine Auflagen?

```
STATUS: erledigt
AUFTRAG: T-210 — Compliance: erfuellt der Stand 7c3a260 seine Auflagen? (Modus pruefen)
GELESEN: docs/tasks/T-210.md; ~/.claude/agents/_rahmen.md; docs/legal/AUFLAGEN.md (vollstaendig); docs/legal/C-002.md (Z. 1-716); .claude/hooks/enforce-data-redirect.ps1; .claude/settings.json; THIRD_PARTY.md; requirements.txt; requirements-dev.txt; README.md (vollstaendig); licenses/ (Verzeichnisliste); licenses/texture2ddecoder-LICENSE.txt; design-review/2026-09-12/ (alle drei PNG als Bild); .github/workflows/release.yml; .github/workflows/tests.yml; docs/release/RELEASE_TEXT.md; scripts/make_screenshots.py; tests/golden/weapon_damage.json (Kopf + Zaehlung); vendor/Paramdex/NOTICE; NightreignHelper.spec (upx-Zeilen); security/findings.md (SEC-023-Umfeld); Volltextsuchen: requirements-dev (repo-weit), SEC-023 (repo-weit), fair use/Video Policy/distributes none (README), Daniel/C:\Users (.claude/), Testabzug (docs/legal/), prose/flavour/A-001/Beschreibung/caption (tests/, scripts/)
GEÄNDERT: docs/legal/AUFLAGEN.md (fortgeschrieben: Pruefsektion 2026-09-12, A-033-Datumsfeld nachgetragen); docs/berichte/T-210-compliance-agent.md (dieser Bericht). Kein Commit — kein Commit-Recht, Aenderungen liegen im Baum.
ANNAHMEN: (1) GitHub-`windows-latest`-Runner bringen kein UPX mit — ungeprueft, traegt nur die Dringlichkeitseinschaetzung zu A-031, nicht das Ergebnis "Bedingung ungeklaert". (2) Die UrhG-Fundstellen aus C-002 (abgerufen 01.09.2026) gelten unveraendert; nicht neu abgerufen, weil dieser Lauf keine neue Ampel auf neue Normen stuetzt, sondern den C-002-Massstab anwendet. (3) A-023-Bestand und A-034 nach Aktenlage (Director-Nachweis 08.09. per gh) — diese Rolle hat kein git/gh und kann beides heute nicht am Remote nachpruefen.
NÄCHSTER: director
BLOCKIERT DURCH: nichts
```

**Dies ist keine Rechtsberatung im rechtlichen Sinn.** Es ist eine belegte
Einschaetzung mit offengelegten Quellen und offengelegter Unsicherheit; die
Einschraenkung gilt fuer den ganzen Bericht.

---

## Antwort in drei Zeilen

**Frage:** Was muesste erfuellt sein, bevor der Stand `7c3a260` raus darf — und was davon ist es heute?
**Ampel:** **GELB, keine Auflage auf ROT.** Von 36 Auflagen sind 21 erfuellt/eingehalten (Feststellung), 8 offen oder teilweise, 4 dauerhafte Schwellen ohne Ereignis, 3 zurueckgestellt/ruhend/entschieden.
**Auflagen in einem Satz:** Vor einem Release fehlen konkret: A-002 (Prosa-Waechter fuers Fixture), A-008 (tests/-Waechter in den Release-Lauf), A-012 (Quellenangabe an den README-Bildern), A-031 (Feststellung, ob die EXE UPX-gepackt ist), die Nutzer-Abnahme von A-021/A-033 — und beim Release selbst das Einfuegen von RELEASE_TEXT Variante A (A-023).

---

## Die vorgelegte Frage: sind die drei PNG unter `design-review/2026-09-12/` Spieldaten?

### [GELB] Programmfenster-Abzuege mit echten Spieldaten im oeffentlichen Repo

**Sachverhalt:** Drei per `QWidget.grab()` erzeugte PNG des Relic-Pickers,
committet und damit oeffentlich abrufbar. Alle drei angesehen. Sie zeigen:
Reliknamen ("Grand Luminous Scene", "Cracked Sealing Wax"), funktionale
Effektzeilen ("Fire Attack Power Up +2", "[Revenant] Improved Strength,
Reduced Faith"), projekteigene Erklaertexte und errechnete Zahlen, dazu kleine
Relikt-Symbole (Spielgrafik) im Oberflaechenkontext. **Keine
Beschreibungsprosa des Spiels in keinem der drei Bilder.**

**Einschlaegig:** Der Massstab aus C-002 (dort mit Volltext-Fundstellen,
abgerufen 01.09.2026): § 2 Abs. 1 Nr. 1, Nr. 4, Abs. 2 UrhG; § 51 UrhG;
§ 87b Abs. 1 UrhG. Projektregeln: NH-002 (Bildschirmabzuege), A-003
(README-Trennung; von `CLAUDE.md` als "keine Spieldaten im Repo"
paraphrasiert), A-014, A-017, A-018.

**Bewertung:**

1. **Kein Bildschirmabzug im Sinne von NH-002.** `QWidget.grab()` greift nur
   das Programmfenster — genau die Bauform, die NH-002/`CLAUDE.md` als
   zulaessig benennt ("Bildnachweise stammen ausschliesslich aus dem
   Programmfenster").
2. **Keine "Spieldaten" im Sinne des Repo-Verbots.** Das Verbot in
   `CLAUDE.md`/A-003-Kontext zielt auf extrahierte Bestaende
   (`nightreign_data.json`, Symbole als Dateien, den Testabzug). Ein
   Fensterbild ist keine extrahierte Datendatei. A-003 selbst ist eine
   README-Trennungs-Auflage und **setzt sogar voraus**, dass das Repo
   "abgeleitete Werte und Screenshots" enthaelt.
3. **Der richtige Massstab ist C-002**, und daran gemessen bestehen alle
   drei Bilder: Reliknamen sind wie die Item-Namen in C-001 Befund 1 keine
   Sprachwerke; die Effektzeilen sind funktionale Kurzbezeichnungen wie in
   C-002 Befund 2/3 ("Etikettierung einer Zahl", kein Gestaltungsspielraum);
   die Relikt-Symbole sind kleine Spielgrafik im Oberflaechenkontext, fuer
   die die § 51-/§ 57-Logik aus C-002 Befund 2/4 traegt — zumal die
   design-review-Berichte, zu denen die Bilder gehoeren, gerade Aussagen
   ueber diese Oberflaeche belegen (Belegzweck). Kein Katalog in
   nennenswertem Umfang: gezeigt wird das **eigene Inventar** (55 Relikte),
   nicht der Effektkatalog (652); sichtbar sind rund 20 Karten.
4. **Aber:** C-002s foermlicher Gegenstand waren die **sieben Dateien unter
   `docs/screenshots/`**. `design-review/` ist ein zweiter, seit 01.09.
   wachsender Bildbestand (heute 9 PNG), auf den die Klaerung nie foermlich
   erstreckt wurde. Der Modus `pruefen` legt keine neue Klaerung an — das
   ist daher ein **Befund mit Klaerungsvermerk**, kein neues C-Dokument.

**In einfachen Worten:** Die Bilder sind erlaubt gebaut (aus dem
Programmfenster) und zeigen nichts, was nach der bestehenden Bewertung
verboten waere — keine Spieltexte in Prosa, nur Namen, Zahlen und winzige
Symbole in der Oberflaeche. Was fehlt, ist nicht ein anderes Bild, sondern
ein Satz Papier: die alte Screenshot-Klaerung gilt offiziell nur fuer den
README-Ordner, nicht fuer den Design-Review-Ordner.

**Risiko:** Wer haftet: Daniel persoenlich. Was droht: theoretisch
DMCA-Takedown wegen der Symbole; praktisch nach C-002/R-003 gering. Wie
wahrscheinlich: theoretisch, nicht praktisch relevant — dieselbe Lage wie
`build_planner.png`. Ab wann kippt es: sobald ein design-review-Bild
**Spielprosa** zeigt (Nightlords-/World-Events-Detail, Effekt-Spalte "What
it does") oder Spielgrafik ausserhalb des Fensterkontexts verwendet wird —
dann greift das A-010-Muster, und niemand prueft diesen Ordner heute.

**Was genau fehlt (der eine Satz):** Die foermliche Erstreckung des
C-002-Massstabs auf `design-review/` und kuenftige Bildbestaende ausserhalb
`docs/screenshots/` — als eigene Klaerung (naechste freie Nummer **C-005**,
siehe Widerspruch W2 unten) oder als Nutzerentscheid, plus eine Zustaendigkeit
dafuer, dass neue Bilder **vor dem Commit** gegen A-010/A-017/A-018 geprueft
werden (heute geschah das erst durch diesen Lauf — A-014 hat im Ergebnis
gehalten, aber nicht als Prozess).

**Sicherheit:** ueberwiegend belegt — Bildinhalt selbst angesehen (alle
drei), Massstab aus C-002 uebernommen statt neu hergeleitet; die
UrhG-Fundstellen wurden fuer diesen Lauf nicht neu abgerufen.

---

## Die vier weiteren Aenderungen seit der letzten Pruefung

### [GRUEN] 1. Der versionierte Waechter-Hook enthaelt nichts, was nicht oeffentlich sein duerfte

**Sachverhalt:** `.claude/hooks/enforce-data-redirect.ps1` (79 Zeilen) und
`.claude/settings.json`, beide committet.

**Bewertung:** Beide Dateien vollstaendig gelesen und `.claude/` per Grep
(`Daniel`, `C:\Users`, `C:/Users`) durchsucht: **0 Treffer. Der Auftrag irrt
— der Hook nennt keine Pfade dieser Maschine** (Widerspruch W1 unten).
`settings.json` verwendet die Variable `$CLAUDE_PROJECT_DIR`. Der Hook nennt
die Zahlen "309 Relikte, rund 110 Builds" — die stehen bereits im
committeten, oeffentlichen `CLAUDE.md` und sind kein Personenbezug ueber das
hinaus, was das Repo ohnehin offenlegt (GitHub-Konto des Nutzers). Keine
Zugangsdaten, keine Kontokennungen, keine Dritt-Daten. Lizenzseitig faellt
der Hook unter die MIT-Lizenz des Repos — unproblematisch.

**Risiko:** keines festgestellt. **Sicherheit:** belegt (Primaerquelle,
zwei unabhaengige Suchbegriffe).

### [GRUEN] 2. `texture2ddecoder==1.0.6` — Lizenznennung vollstaendig

**Sachverhalt:** Neu installiert (T-197); stand schon als ausgelieferte
Laufzeit-Abhaengigkeit in `requirements.txt`.

**Bewertung:** `THIRD_PARTY.md` Tabelle "Bundled into the executable" fuehrt
`texture2ddecoder | 1.0.6 | MIT | Copyright (c) 2020 K0lb3 — from the
wheel's LICENSE`; der Volltext liegt unter
`licenses/texture2ddecoder-LICENSE.txt` (gelesen: MIT, K0lb3, 2020).
`scripts/check_licences.py` existiert und laeuft im Release-Workflow
(`release.yml` Z. 62-64), bricht also, wenn eine `requirements.txt`-Zeile in
der Tabelle fehlt. **Keine offene Auflage aus diesem Punkt.** MIT verlangt
Vermerk + Lizenztext beim Vertrieb — beides faehrt im Hinweispaket mit.

### [GRUEN] 3. Der gestrichene `requirements-dev.txt`-Kopf laesst keine Auflage ins Leere zeigen

**Bewertung:** Repo-weite Suche nach `requirements-dev`: **kein Dokument
unter `docs/legal/` hat je auf den Kopf als Nachweis gezeigt** (0 Treffer
dort). Die Trennung "pytest wird nicht ausgeliefert" ist dreifach anderswo
belegt, davon einmal maschinell: README Z. 541 ("Nothing in
`requirements-dev.txt` reaches the packaged EXE"), `tests.yml` Z. 43-53
(Workflow-Schritt, der den Lauf bricht, wenn pytest in `requirements.txt`
steht oder die Spec `tests` referenziert), `ARCHITECTURE.md` F8/OF-2. Der
maschinelle Beleg ist staerker als der geloeschte Prosa-Kopf.

### [GRUEN] 4. Der neue Ort des Testabzugs wahrt die Auflagenlage

**Sachverhalt:** `C:\Users\Daniel\Desktop\ClaudeCode\NightreignHelper-Testabzug`
— 841 Dateien aus der Spielinstallation, **ausserhalb** des Projektbaums
(Schwesterverzeichnis des Repos), vom `archivist` in T-208 gegen den Push
geprueft.

**Bewertung:** `docs/legal/` (einschliesslich `AUFLAGEN.md`) nennt den
Testabzug an keiner Stelle (Suche `Testabzug`,
`NightreignHelper-Testabzug`: 0 Treffer) — **keine Auflage veraltet durch
den Umzug**. Die Lage zu Spieldaten ist gewahrt, solange der Abzug nicht
committet wird; ausserhalb des Baums kann ihn kein `git add` versehentlich
erfassen. **Hinweis an den Director (keine Rechtsfrage):** `CLAUDE.md`
nennt weiterhin den alten Pfad
`C:\Users\Daniel\AppData\Local\NightreignHelper-Testabzug` — vor der
Baurunde (QA-231) nachziehen, sonst baut der naechste Fensterlauf am
falschen Ort.

---

## Ampel je Auflage

Die vollstaendige Tabelle mit Belegen steht als Sektion **"Pruefung
2026-09-12"** in `docs/legal/AUFLAGEN.md` (fortgeschrieben, nicht
ueberschrieben). Kurzfassung:

- **Erfuellt/eingehalten (Feststellung — Abnahme setzt der Nutzer):**
  A-001, A-003, A-004, A-005, A-007, A-014 (im Ergebnis), A-017 (soweit
  pruefbar), A-018, A-019, A-020 (abgenommen), A-021, A-022, A-023
  (Bestand), A-024, A-026, A-027, A-028, A-030, A-034 (Stand 08.09.),
  A-035, A-036 — **21**.
- **Offen/teilweise — je einer der Satz, was fehlt:**
  - **A-002:** ein maschineller Waechter, der Spielprosa im Golden-Fixture
    erkennt — heute existiert keiner (developer).
  - **A-008:** ein Schritt im Release-Lauf, der die tests/-Waechter
    ausfuehrt — `release.yml` prueft weiterhin nur `nrplanner/data/`
    (developer).
  - **A-012:** die Quellenangabe (Spiel, Rechteinhaber) an den sieben
    Bild-Einbindungsstellen im README — der Disclaimer am Ende genuegt nach
    C-002 nicht (§ 63 Abs. 1 UrhG) (technical-writer).
  - **A-013:** die Festlegung der gezeigten World-Events-Karte in
    `make_screenshots.py` — Nightlords ist festgelegt, World Events nicht,
    und dort liegt die Prosa-Falle aus C-002 Befund 7 (developer, vor der
    naechsten Neuaufnahme).
  - **A-015:** die Nutzerentscheidung zur alten `nightlords.png` in der
    Git-Historie.
  - **A-029 (GRAU):** die Lizenzantwort von Paramdex-Upstream und der
    Commit-Pin im NOTICE — beides fehlt, das NOTICE sagt es selbst
    (Nutzer/developer, bei Gelegenheit).
  - **A-031:** die Feststellung, ob die ausgelieferte EXE tatsaechlich
    UPX-gepackt ist — `NightreignHelper.spec:97` setzt `upx=True`, ob der
    Runner UPX hatte, ist ungeprueft; falls ja, fehlt die
    UPX-Lizenzausnahme im Hinweispaket (release-manager).
  - **A-033:** nur noch die Abnahme durch den Nutzer — ausgefuehrt und
    nachgewiesen ist sie seit 08.09.
- **Dauerhafte Schwellen ohne Ereignis:** A-006, A-009, A-016, A-032 — 4.
- **Zurueckgestellt/ruhend/entschieden:** A-010 (Nutzer, sperrt nicht),
  A-011 (ruht mit A-010), A-025 (entschieden 09.09.: FORTSETZEN — siehe W3).

**ROT: keine.** GRAU offen: nur A-029 (empfohlen, keine Sperre).

---

## Widersprueche zum Auftrag (verlangt: "Widersprich, wenn der Auftrag nicht stimmt")

- **W1 — "Er nennt Pfade dieser Maschine" (Hook):** stimmt nicht. Grep ueber
  `.claude/` nach `Daniel`, `C:\Users`, `C:/Users`: 0 Treffer; beide Dateien
  vollstaendig gelesen.
- **W2 — "der naechste freie Kreis ist C-004":** stimmt nicht.
  `docs/legal/C-004.md` existiert (Nachtrag zwoelf Releases, 07.09.). Die
  naechste freie Nummer ist **C-005**.
- **W3 — A-025 als "offen beim Nutzer":** `AUFLAGEN.md` dokumentiert unter
  "Nutzerentscheide, 2026-09-09" die Entscheidung **FORTSETZEN — sperrt
  nicht mehr**; der Auftrag (aus `docs/state.md`) fuehrt A-025 als offen.
  Einer der beiden Staende ist veraltet — vermutlich `state.md` oder die
  nie nachgezogene Zeile in der C-003-Tabelle. **Ich habe die Frage
  auftragsgemaess nicht neu aufgerollt**; die Buchfuehrung muss der
  Director angleichen.

---

## Entscheidungsvorlage fuer den Nutzer

Nur Punkte, die kein Agent entscheiden kann — als Fragen:

1. Soll der C-002-Massstab foermlich auf `design-review/` erstreckt werden
   (kleine Klaerung C-005), oder genuegt dir die hier dokumentierte
   Feststellung plus eine Prueftpflicht vor dem Commit neuer Bilder?
2. Nimmst du A-021 (Hinweisdatei) und A-033 (Bestand nachgeruestet) ab? Die
   Arbeit ist getan und belegt; das Register wartet nur auf dein Wort.
3. A-015: soll die alte `nightlords.png` aus der Git-Historie entfernt
   werden, oder bleibt sie? (Zurueckstellen ist eine gueltige Antwort —
   dann bitte als Entscheidung eintragen lassen, nicht als Schwebe.)
4. Kenntnisnahme W3: `state.md` und Register widersprechen sich bei A-025.
   Gilt deine Entscheidung vom 09.09. (FORTSETZEN) unveraendert?

## Anwaltlich zu klaeren

**Nichts Neues aus diesem Lauf.** Es bleibt bei den offenen, ausdruecklich
nicht beauftragten Punkten aus C-003/C-004 (Arbeitsvertrag, US-Recht
17 U.S.C. § 1201) — unveraendert, ohne neuen Anlass.

## Geprueft / nicht geprueft

**Geprueft:** alle 36 Registereintraege gegen den Arbeitsbaum bei `7c3a260`;
die fuenf Aenderungen aus dem Auftrag; alle drei neuen PNG als Bild.
**Nicht geprueft:** das GitHub-Remote (Releases, Tags, Social Preview,
Sichtbarkeit) — Rolle ohne git/gh; Aussagen dazu nach Aktenlage vom 08.09.
Die ausgelieferten EXEs selbst (UPX-Frage A-031). C-003/A-025 inhaltlich
(ausdruecklich nicht Auftrag). US-Recht. Der Arbeitsvertrag. Die
`retrospective`-Dateien (`docs/lessons.md`, laeuft parallel).

## Nachprüfen ab

- **2026-11-07:** Ende der 60-Tage-Frist aus GPL-3.0 § 8(b) — geht bis dahin
  keine Beanstandung ein, ist die Qt-Lizenz endgueltig wiederhergestellt
  (A-035-Auskunft vorausgesetzt).
- **Vor dem naechsten Release:** A-002, A-008, A-012, A-031 sowie das
  Einfuegen von RELEASE_TEXT Variante A (A-023) — das ist die eigentliche
  Restliste dieses Berichts.
- **Vor der naechsten Screenshot-Neuaufnahme:** A-013 (World-Events-Karte).
- **Bei jedem PySide6-Upgrade:** A-022 (Lizenz neu lesen) — heute nicht
  faellig, 6.11.1 unveraendert.
