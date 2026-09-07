# Bericht T-096 — Sicherheitspruefung Build-Berater und SEC-021

*Vom `security-reviewer` geliefert, vom Director unveraendert abgelegt
(die Rolle hat kein Write-Recht im Arbeitsbaum). 2026-09-07.*

```
STATUS: erledigt
AUFTRAG: T-096 - Sicherheitspruefung des Beraters und Bestaetigung von SEC-021
GELESEN: docs/tasks/T-096.md; security/findings.md; nrplanner/app.py (Abschnitte
  580-900, 1090-1220, 1380-1470, 1690-1710, 1925-1960, 2060-2085, 3400-3520,
  3660-3890); nrplanner/advisorbar.py; nrplanner/advisorblock.py;
  nrplanner/relicpicker.py (Abschnitte 370-520, 560-760, 795-905);
  nrplanner/inventory.py; nrplanner/datasource.py; nrplanner/paths.py;
  nrplanner/effecttext.py; nrplanner/chalices.py (39-110, 264-330);
  nrplanner/firstrun.py (100-150); nrplanner/advisor/ (worker.py, run.py,
  search.py, candidates.py vollstaendig bzw. ab 150); nrdata/savefile.py
  (41-205, 415-432); nrdata/binary.py (read_cstring); nrdata/extract.py (2845-2860);
  tests/conftest.py (Fixtureliste), tests/advisor_cases.py, tests/test_hostile_savefile.py
  (Testliste); requirements.txt; git log/blame auf relicpicker.py
GEAENDERT: keine (nur Lesezugriffe im Arbeitsbaum; drei Messskripte und eine
  probe.png ausschliesslich im Scratchpad ausserhalb des Repos)
ANNAHMEN: Auftrag war vollstaendig - GOAL-Zitat (A2), state.md-Auszug und die
  Nutzerentscheidung vom 02.09. standen woertlich in T-096.md. Die
  Hochrechnungen auf 19-MiB-Saves sind als Hochrechnung gekennzeichnet und
  linear aus gemessenen 1 und 4 MiB abgeleitet; ich habe keinen grossen Save
  gebaut und keinen in ein Save-Verzeichnis gelegt.
NAECHSTER: director
BLOCKIERT DURCH: nichts
```

---

## Punkt 1 — SEC-021: bestaetigt als Fundstelle, **widerlegt als Angriffspfad**

### Die `<img src=…>`-Frage, ausdruecklich beantwortet

Gemessen auf PySide6 6.11.1 / Qt 6.11.1, `QT_QPA_PLATFORM=offscreen`, kein
Fenster gezeigt, kein Netzverkehr ausgeloest. Rezept: ein `QLabel` bekommt den
Text, danach `sizeHint()`; eine Bilddatei von genau 137x59 px liegt im
Scratchpad.

| Was im `src` steht | `QLabel.sizeHint()` | Urteil |
|---|---|---|
| kein Bild, `"hello"` | 60x14 | Referenz |
| `file:///…/probe.png` (existiert) | **137x59** | **geladen** — genau die Masse der Datei |
| `file:///C:/does/not/exist_zz.png` | 16x16 | Platzhalter, nicht geladen |
| `data:image/png;base64,…` (w=90 h=40) | **90x40** | **geladen** |
| `http://127.0.0.1:9/nope.png` | 16x16, in 0,023 s | **nicht geladen** — Qt hat keinen Netz-Loader im `QTextDocument` |
| `qrc:/nope.png` | 16x16 | nicht geladen |
| relativer Pfad ohne Schema | 16x16 | nicht geladen |
| dasselbe Label **auf `AutoText`** (Voreinstellung) mit `A relic <img …> name` | 293x59 | **geladen** — die Voreinstellung reicht, es braucht kein `setTextFormat(RichText)` |

Antwort: **Ja, Qt laedt in dieser Fassung eine Ressource** — aber nur ueber
`file:`, `data:` und lokale Pfade, **nicht** ueber `http(s)`. Damit ist der
Ausleitungsweg nicht HTTP, sondern der Windows-UNC-Umweg:
`QUrl("file://SOMEHOST/share/x.png").toLocalFile()` liefert
`//somehost/share/x.png`, also einen UNC-Pfad, den `QFile` als SMB-Ziel
oeffnet. Diese letzte Kette habe ich **nicht ausgeloest** (Richtlinie: keine
Netzverbindung); gemessen sind der Ladevorgang selbst und die Pfadableitung,
der SMB-Schritt stuetzt sich auf dokumentiertes Windows-Verhalten. Das deckt
sich mit SEC-019 und ergaenzt es um die Negativkontrolle: `http://` waere kein
Weg gewesen.

Nebenbefund zur Ausloesbarkeit: `Qt.mightBeRichText("<img src=\"x.png\">")`
ist `True`, `Qt.mightBeRichText("Tarnished's Wizened Finger")` ist `False`.
Ein Tooltip ohne Textformat rendert also genau dann Markup, wenn welches
drinsteht — es gibt keinen zweiten Schalter.

### Die Fundstelle

Die Zeilennummern des Befundtexts stimmen nicht mehr. `RelicSlot._sync_mode`
steht heute in **`nrplanner/app.py:734-778`**, die Markup-Zeilen sind **752,
768-770, 772, 774**, `curse_lines` **780-799**, `curse_tooltip` **835-848**.
Inhaltlich stimmt die Beschreibung: `rolled_label` (app.py:653-656) setzt
**kein** Textformat, steht also auf `AutoText`, bekommt `<div>`-Markup und
darin per f-String `effecttext.name(eff)` und `effecttext.owner(eff)`
**ungefiltert**; `curse_tooltip` baut denselben Text ohne `html.escape` und
ohne Rich-Text-Umschlag und geht in `setToolTip` (app.py:777).

Der Kontrast ist scharf und liegt in einer Datei: **dieselbe** Zeichenkette
aus `curse_tooltip` geht ueber `_suggested_curse_tooltip` (app.py:822-833) in
den Berater und wird dort in `advisorblock.as_a_tooltip` escaped und
umschlossen — und ueber app.py:777 in den Bestand und dort nicht.

### Was den Befund umwirft

**Der Reliktname kommt nicht aus dem Save.** Belegt an der Primaerquelle:

- `nrplanner/inventory.py:237` — `name=meta["name"].strip()`, und `meta`
  stammt aus `relic_meta = {r["id"]: r for r in data["relics"]}`
  (inventory.py:194), also aus dem Datenabzug.
- Der Save liefert an dieser Stelle ausschliesslich Ganzzahlen, und alle drei
  werden vorher gegen den Abzug geprueft:
  `relic_id not in valid_relic_ids → continue` (savefile.py:181), Effekt-Ids
  `if value in valid_effect_ids` (190), **Fluch-Ids ebenso**
  `if value in valid_effect_ids` (198).
- Damit ist auch der Fallback `f"<{eid}>"` / `f"<{cid}>"` (app.py:759, 792,
  844) aus einem Save nicht erreichbar; und selbst erreicht waere der Wert ein
  `int` aus `struct.unpack`, den `mightBeRichText` nicht als Tag liest (Ziffer
  nach `<`).

Der Text an dieser Stelle stammt also **vollstaendig aus dem Datenabzug**, und
der Abzug wird aus der eigenen Spielinstallation gebaut
(`datasource.bundled_path` → `paths.snapshot_path()`, geschrieben allein von
`firstrun._Builder.run` ueber `extract.write_snapshot`, firstrun.py:133).

### [P3 | Niedrig | anonym nicht, nur bei manipulierter Spielinstallation] SEC-021 — Slotkarte interpoliert Spieltext ungefiltert in Rich Text und Tooltip

**Betroffen:** `nrplanner/app.py:752, 768-772, 774` (`_sync_mode`), `793`
(`curse_lines`), `844, 846-847` (`curse_tooltip`); Senken sind `rolled_label`
(app.py:653, ohne `setTextFormat`) und dessen Tooltip (app.py:777).

**Vertrauensgrenze:** **Spielinstallation → Anzeige.** *Nicht* die
Save-Grenze — das ist die Korrektur an SEC-021.

**Angriffspfad:** Wer Effekt- oder Fluchnamen in `regulation.bin` bzw. im
daraus gebauten Abzug setzen kann (modifizierte Spieldateien,
Uebersetzungspaket, oder direkt die Datei unter
`%LOCALAPPDATA%\NightreignHelper\`), setzt einen Namen
`X<img src="file://host/share/a.png">`; beim Zeichnen der Slotkarte oeffnet Qt
den UNC-Pfad. Wer den Abzug schreiben kann, hat allerdings bereits
Schreibrecht im Benutzerkontext — derselbe Vorbehalt, unter dem der Nutzer
SEC-016/017/018/020 gestrichen hat.

**Auswirkung:** Anzeigeverfaelschung; bei UNC-Ziel eine SMB-Verbindung samt
NTLMv2-Antwort des Windows-Kontos. Wirkung wie SEC-019, Wahrscheinlichkeit des
Ausloesers wie SEC-015.

**Behebungsrichtung:** dieselbe wie im Befundtext — `html.escape` an den fuenf
Interpolationsstellen, `rolled_label.setTextFormat` ausdruecklich setzen,
`curse_tooltip` durch `advisorblock.as_a_tooltip` schicken statt roh. Die
Vorlage steht im Haus. **Aber**: als Einzelfix schliesst das die Fundstelle,
nicht die Eigenschaft — die Klassenloesung steht seit 02.09. im Register
(gemeinsame Label-Fabrik plus Waechtertest ueber `findChildren(QLabel)`), und
diese Fundstelle ist ein weiteres Argument dafuer und keines fuer die 91.
Einzelaenderung.

**Nachweis:** `inventory.py:237` gegen `savefile.py:181/190/198`; die
Messreihe oben fuer das Laden.

**Empfehlung an den Director:** SEC-021 **nicht als Major/P3 fuehren, sondern
als Instanz von SEC-019 auf Niedrig**, so wie SEC-012 und SEC-015 gefuehrt
werden. Die Zeile im Befundtext „und der Reliktname kommt aus dem Save" ist
falsch und sollte korrigiert werden, sonst traegt der Eintrag eine Grenze, die
er nicht hat. **A2 wird von SEC-021 nicht verletzt.**

**Randbedingung dieser Herabstufung, ausdruecklich:** Sie haelt nur, solange
(a) `inventory.py` den Namen aus `relic_meta` nimmt und nicht aus dem Save,
und (b) `read_owned_relics` Effekt- **und** Fluch-Ids gegen den Abzug prueft.
Faellt eine der beiden — etwa durch einen im Save gespeicherten Spitznamen
oder durch eine roh angezeigte unbekannte Id — steht der Befund wieder auf der
Save-Grenze und die Einstufung wechselt zurueck.

---

## Punkt 2 — der neue Code

### Die Behauptung „6 von 6 escaped, 0 auf AutoText" — nachgeprueft

**Fuer den Code, den der Berater hinzugefuegt hat: zutreffend.** Jede Stelle
einzeln:

| Stelle | Senke | Schutz |
|---|---|---|
| `advisorblock.line_markup` 95-104 | `_rich()`-Label, `Qt.RichText` (149) | `html.escape(line.text)` vor allen vier Zweigen |
| `advisorblock.as_a_tooltip` 112-129 | Tooltip | `html.escape` **und** `<html>`-Umschlag — die einzige Form, die `<b>` buchstabengetreu zeigt |
| `advisorblock` relic_name / count_line / already_equipped / conditional / legend / footer / head / group title | `_plain()` (134-135) | `Qt.PlainText` |
| `advisorblock.heading` 195-196 | Label | `Qt.PlainText` ausdruecklich gesetzt, obwohl `_heading` aus app.py auf AutoText liefert |
| `advisorbar._ElidingLabel` 387-406 | Statuszeile + ihr Tooltip | `Qt.PlainText`; Tooltip `html.escape` + `<span>`-Umschlag |
| `relicpicker` Wertblock 376-382, `Sort by` 828-829, `headline`/`summary`/`findings`/`caveats` 850-883, `chip` 457-458 | Labels | ueberall `Qt.PlainText` |

`advisorbar.py` konstruiert kein einziges nacktes `QLabel` (Zaehlung: 0
Treffer auf `QLabel(` bei 848 Zeilen); die eine Textsenke ist die Unterklasse,
die ihr Format im Konstruktor setzt.

**Als Aussage ueber die beruehrten Dateien: nicht zutreffend.**
`nrplanner/relicpicker.py` hat 21 `QLabel(`-Konstruktionen, davon 8 mit
erklaertem Format. Von den 13 ohne Format tragen sechs Text aus dem Abzug:

- 466 `QLabel(item.name)`, 484 `QLabel(f"• {name}")`,
  493 `QLabel(f"✦ {curse_name}")`, 503, 582 `QLabel(f"• {name}")`
- 692/744 `self.picked` — **ausdruecklich Markup**,
  `f"<b>{…}</b> " + ", ".join(names)` mit ungeescapten Effektnamen

`git blame`: alle sechs stammen aus `cec61c7` (Ursprungscommit), keine aus
T-091 oder T-093 (`6aa9a63` liefert 376-384 und setzt dort korrekt
`PlainText`). Sie sind damit Bestand und Instanzen von SEC-019 — **kein neuer
Befund**, aber die Meldung „0 Elemente auf `Qt.AutoText`" gilt fuer den
Zuwachs und nicht fuer die Datei. Das gehoert in den Bericht, weil ein
Retest, der die Datei prueft statt den Zuwachs, sonst rot wird und niemand
weiss warum.

### Schreibt etwas in den Save? — Nein

Zwei unabhaengige Masken ueber `nrplanner/` (32 Dateien) und `nrdata/` (21
Dateien):

- Maske A (Dateisystem: `open(` mit w/a/x, `write_text`, `write_bytes`,
  `.write(`, `os.remove`, `unlink`, `shutil.`, `rename`, `mkdir`, `makedirs`):
  **8 Treffer**, davon in `nrplanner/` genau drei — `firstrun.py:127`
  (`cache_dir().mkdir`), `shortcut.py:123/145` (`.lnk` im eigenen Startmenue).
  In `nrdata/`: `extract.py:2856-2857` (Abzug), `iconbuild.py:110/113/267`
  (Iconpaket). **Kein Schreibaufruf auf einem `.sl2`-Pfad im ganzen Baum.**
- Maske B (`advisor/`, 9 Dateien, 3 054 Zeilen): Suche nach `open(`, `Path(`,
  `pathlib`, `os.`, `.read_`, `.write_`, `io` → **0 Treffer**; zusaetzlich die
  vollstaendige Importliste ausgelesen (24 verschiedene Importzeilen) — kein
  I/O-Modul darunter, ausser `PySide6.QtCore` in `worker.py`.

Der Berater erreicht den Save ueberhaupt nicht: er bekommt in
`run.frozen_inventory` eine Wertkopie (`OfferedCopy`, run.py:59-76) und liest
sonst nur `ctx.data` im Speicher. **AK-17, Save-Haelfte: gehalten.**

### Oeffnet etwas eine Netzwerkverbindung? — Nein, auf Programmebene

- Maske A (Modulnamen:
  `socket|ssl|urllib|http|requests|ftplib|smtplib|telnetlib|asyncio|xmlrpc`,
  dazu `QtNetwork`, `QNetworkAccessManager`, `QTcpSocket`, `QUdpSocket`,
  `QDesktopServices`, `webbrowser`) ueber nrplanner+nrdata: **1 Treffer** —
  `chalices.py:24 import urllib.parse`, reine Zeichenkettenverarbeitung fuer
  die Schluesselableitung, kein I/O.
- Maske B (Aufrufmuster: `urlopen`, `connect((`, `create_connection`,
  `getaddrinfo`, `openUrl`, `setOpenExternalLinks`, `.get("http`, Literale
  `http(s)://`): **4 Treffer**, alle vier URLs in einem
  Quellenverzeichnis-Docstring in `eventlore.py:31-35`.

Unveraendert gueltig bleibt der Vorbehalt aus SEC-019, jetzt praeziser: die
Qt-Rich-Text-Darstellung oeffnet `file:`/`data:`-Ressourcen, die im
angezeigten Text benannt sind, **nicht** aber `http(s)`. Die umzuformulierende
Zusage bleibt offen — der Berater macht sie nicht schlechter.

### Der Datenabzug unter `%LOCALAPPDATA%\NightreignHelper`

Gelesen von `datasource._snapshot` (`read_text`). **Der einzige Schreiber im
ganzen Baum ist `nrdata/extract.write_snapshot`, aufgerufen von genau einer
Stelle: `nrplanner/firstrun.py:133`**, und nur wenn `"snapshot"` unter den
noetigen Schritten steht (kein Abzug vorhanden, oder `extract_version`
veraltet, oder `regulation.bin` hat sich geaendert —
`datasource._regulation_matches`). Zur Laufzeit sonst nur gelesen; der
Fallback in `datasource._load_data:145` baut den Abzug **im Speicher** und
schreibt nichts. Der Berater liest ihn ausschliesslich ueber `ctx.data`.
Verzeichnis: `paths.cache_dir()`, `%LOCALAPPDATA%\NightreignHelper` —
Standard-ACL des Benutzerprofils, keine eigene Rechtevergabe.

### QSettings — der Haltezustand wird nicht persistiert, und der Berater schreibt dort nicht

- `self._holds` (app.py:1455) ist ein Dict im Fenster. Alle Zugriffe: 3677
  (lesen), 3693/3699-3700 (setzen/verwerfen), 3731/3739-3741/3748-3750
  (zeichnen und aufraeumen). **Keiner davon beruehrt QSettings.** OF-15
  stimmt.
- 20 `setValue`-Stellen im ganzen `nrplanner/`; **null** davon in
  `advisorbar.py`, `advisorblock.py` oder `advisor/`.
- Was der Berater beim Anwenden ausloest, ist der bestehende Pfad:
  `_apply_the_answer_to` (3767ff) schreibt `chalices.slot_key(copy)` in eine
  Schluesselliste und uebergibt sie an `_restore_slot_keys`;
  `_put_these_keys_in_the_slots` endet auf `_store_chalice()` →
  `chalices.save` → `setValue(f"{GROUP}/{hero_id}/{vessel_id}", …)`. Der
  Schluessel besteht aus zwei Ganzzahlen aus dem Abzug; der Wert ist Handle
  plus Roll. **Kein Fremdtext im Schluesselraum.**
- **`_migrate_keys` wird vom Berater nicht beruehrt.** Alle sieben Aufrufer
  (chalices.py:480, 524, 540, 564, 586, 608, 615) sitzen im Namensbau der
  benannten Builds (`BUILDS`). Der Anwendungs-Pfad laeuft ueber
  `chalices.save` (79-87), das `_migrate_keys` nicht aufruft. Der
  `%42leed%20build`-Pfad bleibt aussen vor.
- `Undo apply` (3818) schreibt ueber denselben Weg zurueck. Kein zweiter
  Mechanismus, keine zweite Schluesselform.

### Abhaengigkeiten

`git log -- requirements.txt` gibt genau einen Commit aus: `cec61c7`
(Ursprung). Sieben gepinnte Pakete, unveraendert. **In diesem Zyklus ist keine
dazugekommen.**

---

## Punkt 3 — der Rechenkern

Der Kern ist gegen *falsch geformte Absichten* auffallend gut abgesichert:
`_refuse_a_request_that_asks_about_another_run` (run.py:245-286) vergleicht
acht Felder, `_refuse_pools_that_are_not_the_free_slots`,
`_refuse_pools_ranked_by_another_direction`,
`_refuse_a_budget_that_searches_nothing` (search.py:241-298),
`FrozenInventory.relics_for` wirft statt still leer zu antworten. Fehlende
Felder und unerwartete Typen enden als `KeyError`/`ValueError`,
`_Worker.work` faengt jede Ausnahme und meldet sie als eine Zeile
(worker.py:132-134) an ein `PlainText`-Label mit escaptem Tooltip. Das ist in
Ordnung.

Gegen *Menge* ist er nicht abgesichert, und das ist der Befund.

### [P1 | Hoch | Nutzer legt eine fremde Save-Datei in sein Save-Verzeichnis] Reliktdatensaetze aus einem Save sind unbegrenzt — Start friert ein, Speicher unbegrenzt

**Betroffen:** `nrdata/savefile.py:165-203` (`read_owned_relics`, Schleife
`for off in range(0, len(slot_data) - 24, 4)`, kein Deckel),
`nrplanner/inventory.py:228-267` (ein `OwnedItem` je Datensatz,
`inv.relic_count = len(inv.relics)`), Ausloeser `nrplanner/app.py:1575`
(`rescan_save(initial=True)`). Verstaerker:
`nrplanner/advisor/candidates.py:297-311` (`evaluate` je angebotenem Relikt,
je freiem Slot) in Verbindung mit `nrplanner/advisor/run.py:370-372`
(`should_cancel` wird **erst nach** `candidates.pools` gefragt).

**Vertrauensgrenze:** **heruntergeladenes Save → Programm.** Das ist die vom
Nutzer am 02.09. ausdruecklich scharf gelassene Grenze.

**Angriffspfad:**
1. Der Angreifer baut eine `.sl2`-Datei. Der AES-Schluessel ist eine
   oeffentliche Konstante (`savefile.SAVE_KEY`), und `inventory._decrypt_slots`
   (165-176) ruft **nicht** `decrypt_member` auf — die MD5-Pruefsumme des
   Members wird auf diesem Weg **nie geprueft**. Es genuegt also, den Inhalt
   mit dem bekannten Schluessel zu verschluesseln.
2. Der Member wird mit der verdoppelten Relikt-Id gefuellt, die
   `read_owned_relics` sucht.
3. Der Nutzer legt die Datei in sein Save-Verzeichnis — als „Build eines
   anderen zum Ansehen", oder als Backup neben dem echten Save. `find_saves`
   (savefile.py:415-432) sucht mit den Mustern `*/NR*.sl2`, `NR*.sl2` **und
   `*/*.sl2`**: der Dateiname ist gleichgueltig.
4. Beim naechsten Start scannt `inventory.load` **jede** gefundene Datei, und
   die Regel „der bestbefuellte Save gewinnt" (inventory.py:289) sorgt dafuer,
   dass die praeparierte Datei den echten Save verdraengt.

**Gemessen** (Rezept: `read_owned_relics` direkt auf einem selbst gebauten
entschluesselten Member, echter Abzug als Gueltigkeitsmenge, 849 gueltige
Relikt-Ids, `tracemalloc`):

| Muster | Membergroesse | Datensaetze | Zeit | Spitzenspeicher |
|---|---|---|---|---|
| gleichfoermig gefuellt | 1 MiB | 131 069 | 3,31 s | +41,0 MB |
| gleichfoermig gefuellt | 4 MiB | 524 285 | 13,66 s | +164,1 MB |
| 12-Byte-Muster | 1 MiB | 87 379 | 1,97 s | +28,7 MB |
| 12-Byte-Muster | 4 MiB | 349 523 | 8,62 s | +114,8 MB |

**131 069 Datensaetze je MiB**, linear. Zum Vergleich der echte Fall aus dem
Quelltextkommentar: 284 Relikte in einem ~19 MB grossen Save — Faktor
**8 800**.

Hochgerechnet (linear, nicht gemessen): ein Save gewoehnlicher Groesse von
19 MiB ergibt rund **2,5 Mio. Datensaetze**, etwa **63 s** allein im Scan und
rund **780 MB** allein fuer die `OwnedRelic`-Liste, bevor `inventory.py`
daraus 2,5 Mio. `OwnedItem`-Objekte baut. Eine groessere Datei skaliert
weiter; `_read_settled` liest mit `path.read_bytes()` ohne Obergrenze.

**Verstaerkung durch den Berater, ebenfalls gemessen** (Rezept: echter Abzug,
Wylder, Ziel `max_damage`, drei freie rote Slots, synthetische Kopien,
`candidates.pools`):

| Relikte | `pools()` | je Relikt und freiem Slot |
|---|---|---|
| 100 | 0,025 s | 0,0835 ms |
| 300 | 0,075 s | 0,0831 ms |
| 1 000 | 0,245 s | 0,0816 ms |
| 3 000 | 0,757 s | 0,0841 ms |

Linear, **0,084 ms je Relikt je freiem Slot**. Bei 2,5 Mio. Relikten und sechs
freien Slots sind das rund **21 Minuten** — und `run.run` fragt
`should_cancel` **erst nach** diesem Schritt, der Docstring sagt das
ausdruecklich („The pre-sort is not cut in two"). `Cancel` erreicht diesen
Lauf also nicht. Beim Schliessen wartet `AdvisorController.shutdown` 2 000 ms
und gibt den noch laufenden `QThread` dann auf.

**Auswirkung:** Der Planer ist nach dem Start minutenlang bis dauerhaft
unbenutzbar; bei ausreichend grosser Datei endet er im Speicherfehler. Kein
Datenabfluss, keine Rechteausweitung, kein Verlust gespeicherter Builds (der
Lauf haengt, bevor geschrieben wird). Reine Verfuegbarkeit — aber ohne
Nutzerinteraktion nach dem Ablegen der Datei, an einer als scharf erklaerten
Grenze, und in derselben Form wie SEC-001, den der Director damals als
Release-Sperre gefuehrt hat („Ausloeser ohne Nutzerinteraktion beim Start,
Wirkung ist ein dauerhaftes Einfrieren").

**Warum Prioritaet Hoch bei Schwere Hoch und mittlerer Ausnutzbarkeit:** Der
Nutzer muss eine fremde Datei ablegen — das ist eine Handlung. Aber es ist
genau die Handlung, fuer die der Nutzer die Grenze am 02.09. scharf gelassen
hat, und das Programm sucht die Datei mit `*/*.sl2` von sich aus. Ich stufe
deshalb nicht ab.

**Behebungsrichtung:** Ein Deckel auf die Zahl der Datensaetze, laut
ausfallend statt still kuerzend — dieselbe Form, die SEC-002 im selben Modul
bereits verwendet und die der Nutzer bei SEC-006 als „lauter Fehlerfall"
angenommen hat. Die tragfaehige Schranke ist **relativ**, nicht geraten: mehr
als etwa ein Datensatz je 64 Byte Member ist keine Spielerinventar-Dichte
mehr. Ein zweiter, unabhaengiger Deckel gehoert an die Anzeige/Berechnung
(`inventory.relics_for` bzw. `candidates.pool`), damit die Klasse auch dann zu
bleibt, wenn ein kuenftiger Leser die erste Grenze umgeht. Zusaetzlich:
`should_cancel` **in** die Vorsortierschleife, nicht nur davor — sonst bleibt
jeder grosse Lauf unabbrechbar, unabhaengig von dieser Ursache.

**Nachweis:** die vier Messzeilen oben; `savefile.py:176` (Schleife ohne
Deckel), `inventory.py:289` (der befuelltere Save gewinnt), `savefile.py:428`
(`*/*.sl2`), `inventory.py:165-176` gegen `savefile.py:87-104` (MD5 nicht
geprueft auf diesem Weg), `app.py:1575` (Ausloeser beim Start),
`run.py:370-372` (Abbruchpruefung zu spaet).

**Pruefmittel-Gegenprobe:** Dieselbe Suche findet an einem echten Save 284
Datensaetze, nicht 2,5 Millionen — die Messung misst die Dichte des
Eingabemusters und nicht mein Werkzeug. Und meine erste Erwartung war falsch:
ich hatte aus `seen_offsets.add(off + 4)` auf **einen** Datensatz je
gleichfoermig gefuelltem Bereich geschlossen. Die Messung sagt 131 069 je MiB,
weil der `continue`-Zweig den Offset nicht nachtraegt. Die Zahl steht, weil
sie gemessen ist, nicht weil ich sie hergeleitet haette.

### [P3 | Niedrig | jeder, der auf den Bildschirm sieht] Save-Pfad mit Steam-Konto-Id kann auf der Fensterflaeche landen

**Betroffen:** `nrplanner/app.py:3413` —
`self.owned_label.setText(f"Save could not be read: {exc}")`.

**Vertrauensgrenze:** keine Programm-Grenze; die Grenze ist die zum Betrachter
des Bildschirms bzw. eines Bildnachweises (NH-002, oeffentliches Repository).

**Angriffspfad:** `inventory.load` sortiert die gefundenen Saves mit
`key=lambda p: p.stat().st_mtime` (inventory.py:199) **ausserhalb** des `try`
von `_scan_save`. Verschwindet oder sperrt eine Datei zwischen `glob` und
`stat` — das Spiel schreibt den Save im Betrieb neu —, propagiert ein
`FileNotFoundError`/`PermissionError`, dessen Text den vollen Pfad
einschliesslich `…\Steam\userdata\<Konto-Id>\…` traegt. Der landet in der
Zeile, die app.py:3434-3436 ausdruecklich freihaelt: „The folder is named
after the Steam account id, so it is offered on hover rather than printed
where every screenshot would carry it."

**Auswirkung:** Die Steam-Konto-Id steht in jedem Bildschirmabzug und jedem
Fehlerbericht. Kein Angreifergewinn, ein Bruch einer Zusage, die der Code an
einer Stelle einhaelt und an der Nachbarstelle nicht.

**Behebungsrichtung:** dieselbe Behandlung wie `owned.folder` — die Ausnahme
auf ihre Klasse und eine eigene Formulierung abbilden, den Pfad in den
Tooltip. Nicht `str(exc)` auf die Flaeche.

**Nachweis:** app.py:3413 gegen app.py:3434-3442; inventory.py:199 (`stat()`
ausserhalb des `try`).

**Ehrlich dazu:** Ich habe das Rennen **nicht** ausgeloest, sondern die Senke
und den einzigen ungefangenen Pfad dorthin am Code gezeigt. Wahrscheinlichkeit
gering; der Sinn der Meldung ist, dass sie einen Einzeiler kostet und die
Zusage sonst nur zufaellig haelt.

---

## Beobachtungen (kein Angriffspfad, keine Prioritaet)

- **Der Bestand von `relicpicker.py`** hat sechs Labels mit Abzugstext ohne
  erklaertes Format und ein bewusst als Rich Text gebautes `self.picked` mit
  ungeescapten Effektnamen (466, 484, 493, 503, 582, 692/744) — alle aus
  `cec61c7`, alle Instanzen von SEC-019, kein neuer Befund.
- **Tooltip-Zaehlung mit Nenner:** 43 `setToolTip`-Aufrufe in `nrplanner/`; 22
  davon mit nicht-literalem Argument; **drei** davon escapt
  (`advisorbar.py:406`, `advisorblock.py:251`, `app.py:3442`). Die restlichen
  19 reichen Abzugstext roh an Qt. Das ist SEC-019s Klasse, nicht neu, aber
  die alte Zahl im Register (35 von 36) beschrieb einen anderen Stand.
- **`_heading` (app.py:161-169) ist eine AutoText-Fabrik.** Der Berater hat
  das gesehen und setzt hinterher `PlainText` (advisorblock.py:196). Das ist
  genau die Stelle, an der eine gemeinsame Label-Fabrik ansetzen wuerde: eine
  Fabrik, die AutoText liefert, macht jeden Aufrufer zum Pruefall.
- **Lange Zeichenketten: geprueft, nichts gefunden.** Ich habe die Achse
  „Laenge" am Save-kontrollierten Text gemessen (der BND4-Membername aus
  `read_cstring` hat keinen Laengendeckel und geht in `owned_label`, das
  `setWordWrap(True)` traegt). Ein `PlainText`-Label mit Umbruch kostet bei
  100 000 Zeichen 0,053 s als ununterbrochenes Wort und 0,055 s mit
  Leerzeichen — **linear, kein quadratischer Einbruch**. Der Fall, den ich
  erwartet hatte, ist nicht scharf; ich nenne ihn, damit niemand ihn ein
  zweites Mal sucht.
- **`traceback.print_exc()`** in `worker.py:133` und `firstrun.py:146`
  schreibt auf stderr. In der ausgelieferten EXE ohne Konsole geht das ins
  Leere; kein sensibler Inhalt festgestellt, aber es ist die einzige Stelle,
  an der ein Lauf mehr sagt als eine Zeile.
- **Kein Fenster gestartet, kein Planer gebaut.** Ich habe bewusst darauf
  verzichtet, den Widget-Baum zu bauen und ihn ueber `findChildren(QLabel)` zu
  zaehlen — das haette ueber `QSettings(favourites.ORG, favourites.APP)` den
  echten `HKCU`-Schluesselraum des Nutzers beruehrt, in dem dieses Projekt
  drei Datenverluste hatte. Die Zaehlung ist deshalb statisch. **Der
  laufzeitseitige Waechtertest ist Sache des `qa-engineer` in seinem eigenen
  Klon** — dort ist er auch richtig aufgehoben, und er ist die einzige Form,
  die die Eigenschaft schliesst statt der Fundstellen.
- **Ablage im Gedaechtnis unterblieben:** meiner Rolle ist `Write` entzogen;
  ich habe unter `.claude/agent-memory/security-reviewer/` nichts angelegt.
  Falls das erwuenscht ist, muss es eine Rolle mit Schreibrecht tun.

---

## Vertrauensgrenzen-Skizze des geprueften Bereichs

```
[Spielinstallation: regulation.bin, Texturen]  -- VERTRAUENSWUERDIG (Nutzer, 02.09.)
        |  nrdata/extract  (nur bei firstrun)
        v
[Datenabzug %LOCALAPPDATA%\NightreignHelper\nightreign_data.json]  -- vertrauenswuerdig,
        |  datasource: read_text                                       Schreibrecht = Benutzerkontext
        v
   ctx.data  ---> advisor/  (Qt-frei ausser worker.py; 0 Datei-, 0 Netz-, 0 QSettings-Zugriffe)
        |                        |
        |                        v
        |                   AdvisorResult (nur Zeichenketten + Handles)
        v                        |
[Qt-Anzeige]  <------------------+
   Berater: PlainText / html.escape  -> zu
   Bestand: AutoText / roh          -> offen (SEC-019, SEC-021)
   Qt laedt daraus: file:, data:, UNC -- NICHT http(s)

=== SCHARFE GRENZE =========================================================
[heruntergeladenes Save *.sl2 im Save-Verzeichnis]  -- NICHT VERTRAUENSWUERDIG
        |  find_saves: */*.sl2, jede Datei, beim Start
        |  _decrypt_slots: oeffentlicher AES-Schluessel, MD5 NICHT geprueft
        v
   read_owned_relics: nur Ganzzahlen, alle gegen den Abzug geprueft  -> kein Text
                      ABER: Anzahl der Datensaetze unbegrenzt        -> Befund P1
        |
        v
   BND4-Membername (echter Fremdtext) -> owned_label: PlainText, Tooltip escapt  -> zu

[QSettings HKCU]  <-- chalices.save, ganzzahlige Schluessel; Haltezustand NICHT persistiert
```

---

## Zusammenfassung an director

| Prioritaet | Anzahl | |
|---|---|---|
| Kritisch | 0 | |
| **Hoch** | **1** | Reliktdatensaetze aus einem Save sind unbegrenzt — Start friert ein, Speicher unbegrenzt (neu) |
| Mittel | 0 | |
| Niedrig | 2 | SEC-021 (herabgestuft, Fundstelle bestaetigt, Angriffspfad widerlegt); Save-Pfad mit Steam-Konto-Id auf der Fensterflaeche |

**Gesamturteil: FAIL.**

Begruendung in einem Satz: A2 verlangt, dass kein Befund der Prioritaet „hoch"
offen ist, und der Mengenbefund an der Save-Grenze ist neu, gemessen und ohne
Nutzerinteraktion nach dem Ablegen der Datei ausloesbar. **Nicht** wegen
SEC-021 — der sperrt nichts und sollte herabgestuft werden.

Was der Director entscheiden muss:
1. **SEC-021 korrigieren statt beheben lassen:** Der Befundtext behauptet die
   Save-Grenze; sie haelt nicht. Fuehrung als Instanz von SEC-019 auf Niedrig,
   wie SEC-012/SEC-015.
2. **Der neue Befund braucht eine Id** und geht an den `developer`. Der Fix
   ist klein (relative Schranke, lauter Fehlerfall) und liegt in
   `nrdata/savefile.py` plus einer Abbruchpruefung in `advisor/candidates.pool`.
3. **SEC-009** ist von diesem Lauf nicht beruehrt — ich habe keine Zeile der
   Lieferkette angefasst und keinen Grund gefunden, an der Einschaetzung des
   Registers zu zweifeln.
4. **SEC-015 bis SEC-019:** kein Widerspruch zur Bewertung des Nutzers. Eine
   Praezisierung: `http(s)` ist kein Ladeweg, nur `file:`, `data:` und UNC.
   Das aendert die Einstufung nicht, aber es gehoert in den Audit-Bericht nach
   A1, damit die umformulierte Netzzusage stimmt.

---

## Geprueft / nicht geprueft

**Geprueft:** `advisorbar.py`, `advisorblock.py` vollstaendig;
`relicpicker.py` an allen Label-, Tooltip- und Markup-Stellen; `app.py` an den
Beraterstellen, der Slotkarte, dem Haltezustand, dem Anwenden/Rueckgaengig und
dem Save-Anschluss; `advisor/` vollstaendig auf I/O, Netz, QSettings und
Abbruchverhalten; `inventory.py`, `datasource.py`, `paths.py`, `firstrun.py`
an den Schreibstellen; `savefile.py` an der Save-Leseseite; `chalices.py` am
Schluesselraum; `requirements.txt`.

**Nicht geprueft, mit Grund:**

- **Der laufende Widget-Baum.** Keine `findChildren(QLabel)`-Zaehlung, weil
  das den echten `HKCU`-Schluesselraum des Nutzers beruehrt haette und der
  Nutzer eine Kopie offen hat. Gehoert zum `qa-engineer` (T-095).
- **Der letzte Schritt der UNC-Kette** (SMB-Verbindung, NTLM-Antwort) —
  Richtlinie, unveraendert seit Zyklus 3.
- **`explain.py` und `goals.py` zeilenweise** — an den Ausgabestellen gelesen;
  sie erzeugen Zeichenketten aus Abzugstext und Zahlen, deren einzige
  Rich-Text-Senke `line_markup` ist, und die escapt.
- **Die sechs Inhalts-Tabs** — der Berater beruehrt sie nicht (kein Import aus
  `advisorbar`/`advisorblock` in `bosstab`, `effectstab`, `eventstab`,
  `depthstab`, `deeptab`, `arsenaltab`).
- **`nrdata/extract.py`, `iconbuild.py`, `dvdbnd.py`, `dcx.py`, `tpf.py`** —
  vom Auftrag nicht umfasst, Stand des Registers unveraendert.
- **Bekannte CVEs der sieben Abhaengigkeiten** — kein Netzzugriff im
  Pruefauftrag. Bleibt unter „nicht geprueft", nicht unter „in Ordnung".
- **Git-Historie auf Secrets** — zuletzt am 02.09. ueber 79 Commits geprueft,
  in diesem Lauf nicht wiederholt.
