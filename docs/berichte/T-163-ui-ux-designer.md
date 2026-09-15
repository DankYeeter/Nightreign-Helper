STATUS: erledigt
AUFTRAG: T-163 — SEC-032 (Abstiegs-Ausloeser fuer C3) und AK-131 (fehlender Test)
GELESEN: docs/tasks/T-163.md · security/findings.md (SEC-032, Zeile 501-539,
Zyklus-17/18-Abschnitte) · docs/berichte/T-159-qa-engineer.md (Abschnitt zu
AK-131, Zeile 172, 396-403, 447-461) · UI_SPEC.md vollstaendig, insbesondere
§4.2/§4.3 (Zeile 2713-2769), §7 Wortlaut C1-C3 (Zeile 2952-2997), AK-106 bis
AK-132 (Zeile 3132-3226), Nachtrag „AK-232 nachgezogen" (Zeile 8212-ff., neu
8212-8302 vor meiner Aenderung) · nrdata/gamefiles.py (Konstanten Zeile
100-133, `_search_within_budget` Zeile 234-276) · nrplanner/firstrun.py
(`c3`, `found_it`, `_where_it_sits`, `look_at`, `settle_the_game_folder`,
Zeile 343-505) · nrplanner/app.py (`main()`, Zeile 5067-5123)
GEÄNDERT: UI_SPEC.md (Vermerke an sechs Bestandsstellen + neuer Nachtrag-
Abschnitt „SEC-032 nachgezogen" mit AK-246 bis AK-249 am Dateiende)
ANNAHMEN: (1) „Abstand" ist die Zahl der Verzeichnisebenen zwischen
gewaehltem und gefundenem Ordner — dieselbe Groesse, die
`firstrun._where_it_sits` bereits ueber `len(landed) - len(seen)` ablesen
kann, wenn `landed[:len(seen)] == seen`. Das ist als Hinweis auf die
billigste Umsetzung formuliert, nicht als bindende Vorgabe an den internen
Aufbau. (2) AK-131 ist wie im Auftrag vermutet der zweite Fall (pruefbar,
nur nicht geprueft) — dafuer keine UI_SPEC.md-Aenderung, siehe unten.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## 1. SEC-032 — Entscheidung: ab Abstand 2 wird gefragt, `SEARCH_DEPTH` bleibt 3

**Gewaehlter Weg (von drei angebotenen): C3 loest ab zwei Ebenen Abstand
aus, nicht erst beim Verlassen des Baumes.** `SEARCH_DEPTH`/`SEARCH_PARENTS`
bleiben unveraendert bei `3`/`2` — **keine Zahl in `gamefiles.py` aendert
sich**, das war ausdruecklich abzufragen und ist hiermit beantwortet: nein.

**Regel:**
- Abstand 0 (identisch) → C1, unveraendert.
- Abstand 1 → C2, klickfrei, unveraendert — das ist der Regelfall aus §4.2
  und exakt der Fall, den der `security-reviewer` selbst als Grenze zieht
  ("der geglueckte Fall ist ein Abstieg um eine Ebene").
- Abstand ≥ 2 (z. B. gewaehlter Ordner ist `common` oder `steamapps`) → C3,
  wie beim Verlassen des Baumes.
- Verlassen des Baumes (Aufstieg, Zweigwechsel, Verzeichnisverknuepfung) →
  C3, wie bisher.

**Warum nicht die billigere Alternative (Tiefe senken):** `common` und
`steamapps` sind in §4.2 ausdruecklich als unterstuetzte Faelle genannt
("traegt … noch"). Eine gesenkte Tiefe wuerde dort **nicht** fragen, sondern
mit E1 ("das ist nicht das Spiel") komplett ablehnen — ein haerterer
Fehlschlag als eine Rueckfrage, fuer denselben Sicherheitsgewinn (der
praeparierte Ordner aus dem SEC-032-Szenario wird so oder so nicht mehr
kommentarlos uebernommen). Eine Rueckfrage ist damit strikt die
freundlichere Antwort bei gleicher Sicherheitswirkung.

**Warum nicht "so lassen" (die dritte, im Auftrag als vertretbar genannte
Option):** waere vertretbar, wenn Abstand 2/3 reine Theorie waere. Ist es seit
T-160 nicht mehr — ein Angreifer waehlt die Zip-Struktur selbst, der Zufall
entscheidet hier nicht.

**Neuer Wortlaut C3** (einzige Textaenderung, Titel/Knopfbeschriftungen
unveraendert): die zweite Pfadzeile `The game itself is outside that folder,
in:` wird zu `The game itself is not directly in that folder. It is in:` —
eine schwaechere, aber fuer **beide** Ausloeser (Verlassen des Baumes **und**
Abstieg ≥ 2 Ebenen) wahre Aussage. Nach `Use this folder` bleibt C1
(AK-242, unveraendert gueltig).

**Neue Kriterien AK-246 bis AK-249** (voller Wortlaut in UI_SPEC.md,
Abschnitt „SEC-032 nachgezogen" am Dateiende):
- AK-246: die Kernregel, mit Pruefung, Gegenprobe und einer zweiten
  Gegenprobe am Rand (Abstand 3, `SEARCH_DEPTH`-Grenze: C3, nicht E1).
- AK-247: der neue C3-Wortlaut gilt fuer beide Ausloeser identisch.
- AK-248: "hoechstens eine Rueckfrage je Wahl" (AK-237) gilt auch fuer den
  neuen Ausloeser — W1 gewinnt weiterhin gegen ein gleichzeitiges C3.
- AK-249: `SEARCH_DEPTH`/`SEARCH_PARENTS` unveraendert, als Diff-Pruefung
  formuliert.

**Beruehrt mehr als zwei Stellen — wie angekuendigt gemeldet:** die neue
Regel widerspricht drei bestehenden Aussagen im Bestand (C2-Nachtrag Zeile
~2964, C3-Nachtrag Zeile ~2991, AK-232/AK-237/AK-240/AK-241 im
T-146-Nachtrag, die bereits beantwortete offene Frage 1 im selben
Abschnitt). Nach dem in dieser Datei etablierten Muster (siehe die
T-146- und T-148-Nachtraege) sind das **Vermerke an den Bestandsstellen**,
die auf den neuen Nachtrag verweisen — **kein** bestehender Satz wurde
umgeschrieben oder geloescht, jede alte Fassung bleibt stehen. Insgesamt
sechs Vermerkstellen plus der neue Abschnitt selbst.

## 2. AK-131 — pruefbar, nur nicht getestet. Keine Spec-Aenderung.

AK-131 ("Das Panel erscheint nur fuer den Fall 'kein Spielordner'. Fehlen die
Param-Definitionen … oder scheitert das Lesen einer gefundenen Installation,
bleiben die heutigen Meldungen stehen") ist **wie formuliert pruefbar**: zwei
konkrete, herstellbare Zustaende (`datasource.defs_dir()` liefert `None`;
eine gefundene Installation laesst sich nicht lesen), gegen die sich exakt
behaupten laesst, dass der Ordnerdialog **nicht** erscheint. Die Struktur
erzwingt das bereits sauber (`nrplanner/app.py:5095-5104`: `firstrun.run()`
entscheidet ausschliesslich ueber den Spielordner; ein `defs_dir() is None`
fuehrt in `_Builder.run()` zu einem `FileNotFoundError`, der als `first.error`
in denselben bestehenden `QMessageBox.critical`-Pfad laeuft wie heute —
niemals in ein zusaetzliches Panel).

**Das ist kein Formulierungsproblem, also keine Nachziehung in UI_SPEC.md.**
Es ist ein fehlender benannter Test, den QA (T-159, Zeile 398-403) schon
richtig so eingeordnet hat. **Auftrag an den `developer`:** zwei Faelle in
`tests/test_first_run_panel.py` oder einer Nachbardatei ergaenzen — (a)
`defs_dir()` liefert `None`, Assertion: kein Ordnerdialog-Panel wird
angefordert, die bestehende Fehlermeldung erscheint; (b) eine gefundene,
namentlich passende Installation, deren Lesen scheitert (z. B. per
gefaelschtem `regulation.bin`, das erst nach `looks_like_the_game` beim
tatsaechlichen Extrahieren bricht), Assertion: derselbe bestehende
Fehlerpfad, kein Panel.

## 3. Parallel-Kontext (zur Kenntnis, nicht Teil dieser Aenderung)

T-162 baut die erste Haelfte von SEC-031 (`find_game_dir()` durch dasselbe
Praedikat `looks_like_the_game` wie der Dialogweg) — beruehrt weder die
SEC-032-Entscheidung noch AK-131. T-161 arbeitet in app.py/inventory.py/
savefile.py, ebenfalls ohne Beruehrungspunkt.

## Offene Fragen an den App Designer

Keine — beide Punkte des Auftrags waren Entscheidungen, die der `director`
laut Auftrag mir ausdruecklich ueberlassen hat, nicht Geschmacksfragen.

Pfad: C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\UI_SPEC.md
