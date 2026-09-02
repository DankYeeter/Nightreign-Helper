# Stand

Stand: 2026-09-02, Ende Zyklus 7. Branch `docs/audit-and-advisor-design`,
31 Commits. Testsockel 187 -> 213. **Push vom Director freigegeben** nach gruenem QA-Durchlauf.
Pull Request #16 offen — **Merge nach `main` gehoert dem Nutzer**, `main` ist
geschuetzt.

## Wo wir stehen
- Nightreign Helper, PySide6/Qt, ~17k Zeilen Python, Windows-only.
- Zyklus 1 = Audit (nur Doku). Zyklus 2 = eine Rechenstelle, nachweislich
  unveraendert. Zyklus 3 = der Sicherheitszyklus, der nie gelaufen war.
  Zyklus 4 = der Datenverlust, den Zyklus 3 selbst erzeugt hat. Zyklus 5 =
  ein Schluessel, der im Speicher nicht eindeutig war.
- **Testsockel 78 -> 187.** Und erstmals belegt statt behauptet: der
  `qa-engineer` faehrt eigene Laufzeitmutationen statt uebernommener
  Entwicklertests. Das hat in jedem der drei Zyklen das Entscheidende gefunden.

## Was Zyklus 3 bis 5 geschlossen haben
**Zwoelf Sicherheitsbefunde**, alle mit bestandenem adversarialem Retest, kein
Fix umgehbar: SEC-001, 002, 004, 005, 006 (Deckel), 007, 008, 010, 012, 013,
014.
**Dreizehn QA-Befunde:** QA-003, QA-005 (teilweise), QA-024, QA-033, QA-034,
QA-035, QA-039, QA-040, QA-041, QA-042, QA-043, QA-045, **QA-046**.

Belegt gegen echte Daten, nicht gegen sich selbst:
- **SEC-001:** der Vor-Fix-Stand haengt an einem echten praeparierten Save
  (nach 20 s zwangsbeendet), der heutige meldet es in 0,01 s, Fenster in 1,8 s
  bedienbar.
- **QA-003/033/041:** 15 Namensformen ueber die echte Oberflaeche, ein
  Mischstore aus zu langem Namen, Schraegstrich, senkrechtem Strich und
  Prozentzeichen, Ketten der Laenge 2 bis 4 in beiden Reihenfolgen, und fuenf
  echte Programmstarts mit **byteweise identischem** Store-Dump.

**Die ehrliche Bilanz:** Zwei Datenverluste sind in diesem Zyklus entstanden
und wieder geschlossen worden — **beide aus dem Fix fuer QA-003, keiner aus
dem Altbestand.** Eine Migration, die Nutzerdaten anfasst, hat drei Developer-
und drei QA-Runden gebraucht, bis sie nichts mehr zerstoert.

**Nebenbefund mit Folgen:** Der Testsockel aus Zyklus 2 belegte die Parser
nicht (`conftest.py` nahm den Snapshot-Cache; fuenf Parser liefen in einem
gruenen Lauf gar nicht). Als DEBT-001 geschlossen.

## Was das Release sperrt
1. **QA-036 (P2)** — die Vollstaendigkeit des Icon-Packs wird nie geprueft.
   Das Pack des Nutzers war am 2026-09-02 zu 88 % leer (105 von 839 Dateien);
   **wiederhergestellt am 2026-09-02** ueber `scripts/build_icons.py`, 840
   Dateien, ueber die Programm-API verifiziert. **Die Ursache ist offen:**
   `iconbuild.build` leert das Ziel ohne Sperre.
2. **QA-018** — Waffen-Tab 203,4 gegen Detailtafel 244,1. **Seit 2026-09-02
   nicht mehr nur Release-Blocker, sondern Vorbedingung des Berater-Hauptwegs**
   — siehe unten.
3. **SEC-009**, nur zwei Punkte: Release-Action auf beweglichem Tag in einem
   Job mit `contents: write`, und keine Pruefsumme. Zusammen unter zehn Zeilen
   YAML. Signatur und `--require-hashes` sind akzeptiertes Restrisiko.
4. **GOAL A9** — noch nichts gegen ein gebautes Artefakt geprueft.
5. **C-002** (`nightlords.png`, Ampel ROT) — Entscheidung des Nutzers.

**QA-046 ist in Zyklus 5 gefallen** (Schema 3, Commit `543f69d`) — zwei
Build-Namen, die sich nur in der Gross-/Kleinschreibung unterschieden, teilten
sich einen Speicherplatz. Die Lehre bleibt stehen: `build_key` war injektiv
gegen Python-Zeichenketten, **nicht gegen die Registry**. Eine Zusicherung
ohne Bezugsrahmen ist keine.

## QA-018 ist erklaert - und wartet jetzt auf DICH

**Der Fix haengt an einer Beobachtung im laufenden Spiel, die nur der Nutzer
machen kann.** Fuenf Minuten, zwei Relikte.

Ursache: `damage.py` ist nicht die eine Rechenstelle, sondern die **obere
Haelfte einer zweistoeckigen Rechnung**. Beide Pfade sind bis `weapons.rate`
bitgleich; `attack_rating` legt danach eine Multiplikatorschicht darauf, die
der Waffen-Tab nie sieht. 203,4 x 1,2 = 244,1 - exakt der Unterschied.

Die Annahme, die bricht: eine Einschraenkung auf eine **Angriffsart** wird nur
erkannt, wenn der Effekt `magicSubCategoryChange1/2/3` traegt. "Improved
Thrusting Counterattack" traegt keines davon - **seine Einschraenkung steht nur
im Beschreibungstext, in keinem Param-Feld.**

### Zwei Messungen im Spiel — beide in derselben Sitzung erledigt

**Messung 1 — QA-018 (welche Zahl stimmt):**

> **Wylder, Wylder's Greatsword (Common, Slot 1), sonst nichts ausgeruestet.**
> Angriffswert im Spielmenue notieren. Dann **genau ein** Relikt mit
> "Improved Thrusting Counterattack (Physical Attack +20 %)" einsetzen und
> denselben Wert erneut ablesen.
> - **Steigt er um 20 %** -> der Buff ist global, **244,1 ist richtig**, der
>   Waffen-Tab ist unvollstaendig.
> - **Bleibt er stehen** -> der Buff greift nur beim Stoss-Konter,
>   **203,4 ist richtig**, und `damage.attack_rating` ueberschaetzt.

Zweite, unabhaengige Probe im selben Aufbau: statt dessen ein Relikt mit
"Improved Sorceries +2 (+11 %)". Bewegt sich der Angriffswert des Greatswords,
traegt das Feld wirklich pauschal.

**Messung 2 — QA-061 (haben Waffen ueberhaupt Anforderungen?):**

> Im Spiel eine **schwere Waffe** ansehen, die ein Nightfarer mit niedrigen
> Attributen nicht tragen koennen sollte — ein Greathammer, ein Colossal
> Sword oder ein Katalysator bei einem Nightfarer mit wenig Intelligenz.
> **Zeigt das Spiel dort eine Attributsanforderung an (rot markiert, "Requires
> STR 30" oder aehnlich), oder gibt es so etwas in Nightreign gar nicht?**
> - **Es gibt Anforderungen** -> unsere Extraktion liest ein leeres Feld, und
>   das Programm zeigt **jede** Waffe faelschlich als tragbar an. Echter
>   Befund.
> - **Es gibt keine** -> Nightreign kennt keine Waffenanforderungen. Dann sind
>   die Checkbox "Meets requirements", das Kachel-Dimmen, die "Requires"-Zeile
>   und ein ganzer Rechenzweig **toter Code** und gehoeren weg.

Gemessen: 1791 von 1793 Waffen tragen ein `requires` aus lauter Nullen, die
zwei uebrigen verlangen Arcane 1 — und jeder Nightfarer hat auf Level 1
mindestens 10. Der Filter "Meets requirements" filtert deshalb **1793 zu
1793**. Das ist zu auffaellig, um Zufall zu sein, und zu wichtig, um es zu
raten.

---

Betroffen (Messung 1) ist eine **vollstaendig aufgezaehlte** Effektfamilie
(~20 IDs):
Improved Thrusting Counterattack, Improved Sorceries, Improved Incantations,
Improved Sorceries & Incantations. Die Zauber-Buffs heben ausweislich der Daten
`physicsAttackRate` mit - sie erhoehen also den physischen Angriffswert eines
Greatswords um bis zu 11 %. Ob das Spiel das wirklich tut, sagen die Dateien
nicht.

**Die Spielmessung blockiert den Berater TEILWEISE — Korrektur vom
2026-09-02.** Ich hatte hier geschrieben, sie blockiere ihn nicht mehr. Das war
zu stark, und der `ui-ux-designer` hat es beim Schreiben der Spec bemerkt.

Das Argument des `architect` (eine flache Multiplikatorschicht skaliert den
Grenzbeitrag und dreht ihn nicht um) traegt fuer Multiplikatoren des
**Grundzustands**. Es traegt **nicht** fuer Multiplikatoren, die der
**Kandidat selbst mitbringt** — und die strittige Effektfamilie aus T-023
(Improved Thrusting Counterattack, Improved Sorceries, Improved Incantations)
ist genau das: **reliktgetragene** Angriffsmultiplikatoren.

**Folge:** Ein Picker-Ranking, in dem ein solches Relikt vorkommt, kann durch
die Spielmessung die **Reihenfolge** wechseln, nicht nur die Groesse. Der
Vorbehalt auf den Karten ist deshalb bewusst schwach formuliert ("may be
wrong") statt "die Reihenfolge haelt" — das waere eine Zusicherung ohne Beleg
gewesen, und genau davon hatten wir in diesem Vorhaben schon drei.

Was weiterhin gilt: Zielrichtungen, die **Waffen gegeneinander** stellen,
haengen an den je Waffe verschiedenen `class_rates` und duerfen erst nach W6
scharf gestellt werden.

**Nachgeschaerft am 2026-09-02 (AD-023) — dritte und letzte Fassung.** Der
`architect` hat es gerechnet statt eingeraeumt. Bringt ein Kandidat **selbst**
eine Rate `r` mit, entsteht ein Term `m*(r-1)*S(B)`, der am **ganzen**
Angriffswert haengt statt am Zuwachs: bei `S(B) ~ 300` und `r = 1,20` sind das
60, waehrend +5 Staerke den Wert einstellig bewegt. **W6 entscheidet also
nicht die Groesse, sondern welche Effektfamilie gewinnt.**

**Der Vorbehalt wird deshalb berechnet, nicht pauschal gesetzt.** Betroffen ist
ein Kandidat genau dann, wenn einer seiner Effekte ein Feld aus `AR_RATE_FOR`
traegt — die Familie ist vollstaendig aufgezaehlt, das ist ein **Test, keine
Heuristik**. Traegt kein Kandidat des Laufs ein solches Feld, ist die Rangfolge
invariant und es braucht **gar keinen Vorbehalt**; das ist der haeufige Fall.
Sonst: Markierung an den **betroffenen Zeilen**, nicht als Banner.

**Was bleibt:** Fassade vor Berater; der **Bau** des Beraters ist ab W5 nicht
durch die Spielmessung blockiert. **Was ersetzt wird:** die **Auslieferung**
einer Rangfolge mit AR-Raten-Kandidaten ist es sehr wohl. Pruefpunkt 16 ist auf
**Attributskandidaten** formuliert und ist kein Beleg fuer die Rangfolge
gemischter Felder.

*(Diese Passage musste dreimal nachgeschaerft werden — sie ist die
schwierigste Aussage des Vorhabens, und jedes Mal hat eine andere Rolle den
Fehler gefunden.)*

**Parallel laeuft Weg B** (Spalten umbenennen), weil er unter jedem Ausgang
richtig bleibt. Weg C (die Effektfamilien nach `SCOPED_PREFIX` umleiten) wird
**nicht** gegangen - er raet gegen die Params.

## Die Prioritaetsaenderung vom 2026-09-02

Der `architect` hat beim Nachziehen der Nutzerentscheide (AD-017, AD-018)
einen Zusammenhang belegt, der die Reihenfolge des Vorhabens aendert:

**Ein konstanter Versatz kuerzt sich in einer Differenz heraus — eine falsche
Steigung nicht.** Der Hauptweg des Beraters ist der Grenzbeitrag
`compute(Build + Kandidat) - compute(Build)`. Der abnehmende Ertrag, den der
Nutzer sehen will, **ist** die Steigung der Schadenskurve. QA-018 (203,4 gegen
244,1 fuer dieselbe Waffe) ist ein gemessener Widerspruch in genau dieser
Rechnung.

**Folge: QA-018 wird vor den Berater-Bau gezogen.** Andernfalls entstuende ein
Berater, der Relikte in einer plausibel aussehenden, aber falschen Reihenfolge
vorschlaegt — und das faellt erst auf, wenn der Nutzer im Spiel nachrechnet.
Der Test, der es aufdeckt, steht in ARCHITECTURE.md als Pruefpunkt 16:
derselbe +Staerke-Kandidat muss bei hohem Staerkewert einen **kleineren**
Grenzbeitrag haben. Faellt er, liegt die Ursache in `damage.py`/`model.py`,
nicht im Berater.

Solange QA-018 offen ist, traegt jede Picker-Zeile den
Attack-Rating-Vorbehalt sichtbar.

## Naechster Zyklus (Zyklus 6), geordnet
1. **QA-049** (P3) — zwei Stellen in `app.py` bauen `QSettings` aus Literalen
   und umgehen die Testumlenkung; **die Suite liest heute den echten Speicher
   des Spielers.** Dazu ein Waechtertest, der den Baum nach literal gebauten
   `QSettings`-Aufrufen absucht. Klein, und es schliesst die Klasse.
   Im selben Auftrag: **QA-050** (Kommentar nennt den falschen Schutz) und
   **QA-051** (pruefen, ob das Entfernen **beider** Waechter erreichbar ist —
   wenn ja ein Testfall, wenn nein faellt einer weg).
2. **QA-048 + die zurueckgestellte Nebenlaeufigkeit als EIN Auftrag** — beide
   sitzen im selben Fenster: was ist ein halb migrierter Speicher, und wer
   erkennt ihn?
3. **QA-018 Weg B** (`ui-ux-designer` Spec, dann `developer`): Spalten
   benennen, was sie messen. **Weg A wartet auf die Spielmessung des Nutzers.**
   Im selben Zug QA-055 (Tier) und QA-056 (Attributsatz) - dieselben drei
   Zahlen, dieselbe Wurzel.
4. **QA-058 / AD-019-Umbau, sieben Schritte** — der Entwurf steht:
   **W0** `weaponstab.py` loeschen (QA-057) · **W1** `WeaponRating.per_type()`
   · **W2** Fassade mit den **heutigen** Werten · **W3** Kachel und Tafel auf
   `damage.equipped()` · **W4** `arsenaltab` auf `rank_candidates()` mit
   explizitem `target_tier` · **W5** Waechter AD-021 scharf · **W6** wartet auf
   die Spielmessung. W0 bis W2 sind bitgleich, W3 und W4 aendern bewusst.
   **Die Fassade muss vor den Berater.**
5. **`ui-ux-designer` Spec fuer den Picker** — danach der Berater.
6. **QA-032 + QA-004** — beschaedigtes Save wird still uebersprungen;
   entschieden ist Lesart B, der Spieler soll es erfahren. Drei Zustaende:
   kein Save / Save gefunden, keins lesbar (mit Grund) / gelesen, N
   uebersprungen.
7. **QA-036** — in ein temporaeres Verzeichnis bauen und am Ende umbenennen.
8. **SEC-019-Klasse** — Label-Fabrik plus Waechtertest, **nicht** 90
   Einzelaenderungen; mit SEC-015 und DR-004.
9. **SEC-006/016/018 als EIN Nachtrag** — relative Schranke aus der
   komprimierten Nutzlast statt gemessener Konstante.
10. Klein und dokumentiert: QA-052, QA-053, QA-054, QA-057 (toter Code
    `weaponstab.py`, bereits gedriftet), QA-037, QA-038, QA-044, QA-047, SEC-017, SEC-020,
   DR-005 bis DR-007, `scripts/capture_weapon_damage.py`.

Zurueckgestellt, nicht vergessen: **Nebenlaeufigkeit der Migration** (zwei
Programminstanzen auf einem Store — vom `qa-engineer` als naechster
Bruchpunkt von "lesen, schreiben, loeschen" benannt); `ruff` als
Entwicklungsabhaengigkeit (zieht `researcher` und `compliance-agent` nach).

## Entscheidungen des Nutzers
- **Die eigene Spielinstallation gilt als vertrauenswuerdig** (2026-09-02).
  SEC-015 bis SEC-018 auf Niedrig, SEC-019 von Hoch auf Mittel — sperrt das
  Release nicht mehr. Grenze A (heruntergeladenes Save) bleibt scharf.
  **Die README-Zusage "kein Netzwerkzugriff" muss trotzdem umformuliert
  werden**, bevor etwas veroeffentlicht wird: SEC-019 ist gemessen, nicht
  vermutet.

## Beantwortet am 2026-09-02 (Details in GOAL.md)
F1 Slots festhalten = ja. F2 = Vorschlaege im Relikt-Picker, gerechnet vom
aktuellen Build aus (keine Anwenden-Mechanik). F3 Fluechte mitbewerten = ja.
F4 = Button "Optimize", Ort entscheidet der `ui-ux-designer`.
OF-12 = Haltezustand gehoert zum Gefaess. OF-13 = Fluechte nennen, nicht
abwerten. OF-15 = ueberlebt keinen Neustart.
**C-002 wird ignoriert** — ausdruecklicher Entscheid, nicht erneut vorlegen.
**PR #16** wird hochgeladen, sobald die jetzigen Ziele erreicht sind.
**L-003** = Option 1.

## Offen beim Nutzer
- **DIE SPIELMESSUNG ZU QA-018** — konkrete Anleitung oben. Sie entscheidet
  eine ganze Effektfamilie und blockiert den letzten Schritt vor dem Berater.
  Der Steigungstest ist bestanden; was fehlt, ist diese eine Beobachtung.
- **QA-044** (Randfall, gegenstandslos im Speicher des Nutzers) —
  zurueckgestellt, bis es jemand meldet. Nicht erneut vorlegen.

## Was niemand geprueft hat, und das bleibt so
- **Die Oberflaeche hat kein Mensch mit Augen gesehen.** Alle Belege headless
  ueber die echten Widgets. Schliesst erst der `power-user` auf einem
  gebauten Artefakt.
- **Zahlenrichtigkeit gegen das laufende Spiel.** Nur der Nutzer kann das
  schliessen, und fuer den Berater waere es die wertvollste Pruefung.
- Linux und macOS: dort legt QSettings INI/plist an; `settings.sync()` in
  `_migrate_keys` ist von keiner Mutation zu toeten, weil nur Windows geprueft
  wird. **Wuerden sie je Zielplattform, ist das der Punkt, an dem eine
  Testluecke zur Datenverlustluecke wird.**
- Bekannte CVEs der sieben Abhaengigkeiten (SEC-011).
- Die vermutete 4-GiB-Allokation in `dvdbnd._read_entry` — Hypothese, nicht
  ausgeloest.
