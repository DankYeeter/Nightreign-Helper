STATUS: erledigt
AUFTRAG: T-166 — Die Doku holt A15 ein
GELESEN: docs/tasks/T-166.md · README.md (vollstaendig) · docs/legal/AUFLAGEN.md
(A-024, A-027, sowie A-021/A-033 als Kontext) · docs/state.md · UI_SPEC.md,
Abschnitte 4.4, 5, 6, 7 (Wortlaut A1-A3, E1, W1, C1-C3, S1-S5), 9, 10 (AK-106
bis AK-132) sowie die Nachtraege „Was aus dem gewaehlten Ordner wirklich
passiert" (T-145, SEC-027) und „SEC-032 nachgezogen" (C2/C3-Abgrenzung), und
§11 (AK-220 bis AK-229, Hintergrundlesen) · docs/release/RELEASE_TEXT.md
(Zeilen 35-52, 85-101, nur gelesen, nicht geaendert) · nrplanner/gamepath.py,
nrplanner/paths.py, nrplanner/shortcut.py, nrplanner/favourites.py,
nrdata/oodle.py (nur gelesen, zur Verifikation der Doku-Aussagen)
GEÄNDERT: README.md (drei Stellen ergaenzt, siehe unten) ·
docs/berichte/T-166-technical-writer.md (dieser Bericht)
ANNAHMEN: docs/anleitung/ existiert nicht und hat nie existiert (siehe
Pruefung unten) — README.md ist die einzige Nutzerdokumentation dieses
Projekts. Ich habe das Verzeichnis deshalb nicht angelegt, sondern die
Aenderungen vollstaendig in README.md untergebracht, wie es der bestehende
Aufbau des Dokuments (ein durchlaufendes Handbuch mit Inhaltsverzeichnis)
bereits vorsieht.
NÄCHSTER: release-manager (Befund zu RELEASE_TEXT.md, siehe unten)
BLOCKIERT DURCH: nichts

## Was ich getan habe

### 1. `docs/anleitung/` — Bestandspruefung statt Neuanlage

`Glob docs/anleitung/*.md` liefert nichts; `git log --all --diff-filter=A
--name-only | grep -i anleitung` liefert nichts; `find . -iname "*anleitung*"`
liefert nichts. Das Verzeichnis existiert nicht und hat in der gesamten
Git-Historie nie existiert. Die Whitelist im Auftrag nennt es als moegliches
Ziel, nicht als Pflichtziel — ich habe es nicht angelegt, weil ein zweites
Dokument neben einem bereits vollstaendigen README ohne Auftrag genau die
Falle waere, vor der meine Rollenregel warnt ("du dokumentierst nichts, was
es nicht gibt"). Alle Aenderungen liegen in `README.md`.

### 2. A15 in der Anleitung — drei Stellen in `README.md`

**a) Abschnitt „Install"** — neuer Absatz „**Finding your game.**" vor „First
launch takes about a minute.": beschreibt in eigenen Worten, was der Nutzer
tut, wenn die Automatik den Spielordner nicht findet (Steam → Manage → Browse
local files), dass der gewaehlte Ordner geprueft und für jeden weiteren Start
gemerkt wird, dass ein fehlender Ordner das Panel erneut zeigt, und dass eine
Rueckfrage kommt, wenn der tatsaechlich gefundene Ordner mehr als eine Ebene
vom gewaehlten abweicht oder ausserhalb liegt (C2 bleibt stumm, C3 fragt —
UI_SPEC §4.2/§6, Nachtrag „SEC-032 nachgezogen"). Ein Satz verweist von hier
schon auf die Transparenzstelle unten, statt die Begruendung zu verdoppeln.

**b) Abschnitt „1. Build planner", Spielstand-Absatz** — zwei neue Absaetze
nach dem bestehenden `%APPDATA%\Nightreign`-Satz: `Find my save…` (Ort, Zweck,
Speicherung, die drei Ausgaenge lesbar/leer/unlesbar in eigenen Worten statt
S3/S4 woertlich zu zitieren) und ein Absatz zum Hintergrundlesen — das Fenster
steht sofort, alle Tabs sind sofort bedienbar, nur der Reliktknopf jedes Slots
wartet auf den Spielstand (AK-220/AK-221/AK-223). **Bewusst keine Millisekunden
im Text** — die 657 ms/6,1 s aus `docs/state.md` sind eine interne Messung,
keine Nutzeraussage, und Zahlen dieser Art waeren im README eine
Werbebehauptung nach der Regel „kein Marketing". Beschrieben ist nur das
beobachtbare Verhalten.

**c) Abschnitt „Where your data lives"** — der fehlende Satz, den der Auftrag
als wichtigsten Teil bezeichnet: ein neuer Absatz direkt nach „Nothing is
ever written back to either one" sagt, dass zum Lesen der Spielarchive ein
kleines Programm aus dem Installationsordner ausgefuehrt wird (eine
Dekompressions-Bibliothek, die mit dem Spiel selbst mitgeliefert wird),
warnt nicht, sondern erklaert die Konsequenz (dieselbe Formulierung wie im
Programmfenster: eine Kopie des Spiels waehlen, der man vertraut — fuer die
meisten die, die sie spielen). Zusaetzlich wurde die Aufzaehlung der
Registrywerte um die zwei neuen Schluessel ergaenzt: der gemerkte
Spielordner-Pfad (`paths/game`) und der gemerkte Spielstand-Pfad
(`paths/save`), beide nur vorhanden, wenn der Nutzer sie ueber das Panel bzw.
`Find my save…` selbst gesetzt hat.

**Damit sind A-024 und A-027 aus `docs/legal/AUFLAGEN.md` inhaltlich erfuellt**
(Transparenztext zur Bibliotheksausfuehrung; „What it reads and where it
writes" vollstaendig inklusive der zwei neuen gespeicherten Werte). Ich habe
`AUFLAGEN.md` selbst **nicht** angefasst — das Register fuehrt laut Kopf der
Datei der `director`, gestuetzt auf den `compliance-agent`; ich melde nur,
dass der Text jetzt existiert.

### 3. Was ich nicht dokumentiert habe, weil ich es nicht ausfuehren konnte

Ich habe das Programm mit umgelenkten Datenverzeichnissen gestartet (siehe
unten) und dabei bestaetigt, dass der **geglueckte** Fall — Automatik findet
das echte Spiel, kein Zusatzfenster — unveraendert funktioniert. Den
**Fehlschlagsfall** (Panel A1/A2/E1/W1, die Rueckfrage C3) konnte ich nicht
visuell durchspielen: dazu muesste die Automatik das echte, auf dieser
Maschine installierte Spiel *nicht* finden, was ein Verstecken oder Umbenennen
der echten Installation verlangt hätte — verboten (`CLAUDE.md`: „Nie in den
Spielstand oder die Spielinstallation schreiben"). Ich habe deshalb **kein**
Bildmaterial dieser Dialoge und keine visuelle Bestaetigung, dass der Text am
Fenster so erscheint, wie `UI_SPEC.md` ihn vorschreibt — mir standen in dieser
Sitzung ausserdem keine Bildschirmabzugs-Werkzeuge zur Verfuegung. **Diese
Passagen der Anleitung sind wortgetreu aus `UI_SPEC.md` (AK-106 bis AK-132,
Nachtraege SEC-027/SEC-032) abgeleitet, aber ungeprueft am laufenden Fenster.**

## Selbsttest

| Schritt | Ergebnis | ausgefuehrt |
|---|---|---|
| Drei Datenverzeichnisse umlenken (`LOCALAPPDATA`, `APPDATA`,`NIGHTREIGN_SETTINGS_ORG/APP` auf `T-166`-eigene Werte) | Nachweis ueber `HKCU\Software\DankYeeterT-166\...` (Registry-Baum entstand nur dort) und `%LOCALAPPDATA%` zeigte auf den Scratchpad-Pfad | ja |
| Testabzug in umgelenktes `LOCALAPPDATA\NightreignHelper` kopieren | `nightreign_data.json` (8 484 651 Byte) und `icons/` liegen im umgelenkten Ort | ja |
| Programm mit `run.py` starten, echte Installation automatisch finden lassen | Fenstertitel `Nightreign Helper 1.8.0` erscheint (per `Get-Process`), **kein** Panel-Titel `Nightreign Helper` ohne Version — die Automatik hat gegriffen, keine Rueckfrage | ja |
| `paths/game`/`paths/save` nach reinem Automatik-Lauf pruefen | Registry-Schluessel `paths` existiert **nicht** — bestaetigt `gamepath.py:104`: die Automatik schreibt nie, nur eine Bestaetigung tut das | ja |
| Programm mit leerem `APPDATA` starten (kein Spielstand auffindbar) | Fenster bleibt offen und bedienbar (kein Modal, Titel unveraendert) — konsistent mit „kein Modal fuer den Spielstand" (UI_SPEC §5) | ja |
| Panel A1/A2/E1/W1 und Rueckfrage C3 visuell pruefen | nicht moeglich ohne Verstecken der echten Installation (verboten) und ohne Bildschirmabzugs-Werkzeug | **nein — als ungeprueft markiert** |
| „Find my save…"-Knopf visuell pruefen | dieselbe Einschraenkung (kein Bildschirmabzug) | **nein — als ungeprueft markiert** |
| Registry- und Testverzeichnis-Aufraeumen nach dem Lauf | `HKCU\Software\DankYeeterT-166` entfernt (`Get-Item` liefert danach nichts); echtes `%LOCALAPPDATA%\NightreignHelper` unveraendert (nur `icons/`, `nightreign_data.json`, wie vorher) | ja |

## Was ich gestrichen habe

Nichts. Der Auftrag selbst stellt fest, dass die bestehenden Saetze nicht
falsch sind — sie fehlten nur um den Ausfuehrungssatz. Ich habe nichts aus
README.md entfernt, nur ergaenzt.

## Produktbefunde

1. **Die Unterscheidung „eine Ebene tiefer ist stumm, zwei sind eine
   Rueckfrage" ist fuer eine Anleitung schwer verlustfrei zu erklaeren, weil
   sie selbst schon eine Ausnahme von einer Ausnahme ist** (C2 vs. C3, seit
   T-146 und nochmal seit T-163/SEC-032 veraendert). Ich habe sie in einem
   Satz zusammengefasst ("more than one level away… or outside it
   altogether"), aber ein Nutzer, der wissen will, *warum* ein Level
   akzeptiert und zwei abgefragt werden, findet dafuer in der Anleitung keine
   Begruendung — die gehoert dort auch nicht hin, sie gehoert ins Produkt: die
   Schwelle selbst koennte einfacher sein (z. B. immer fragen, sobald der
   gefundene Ordner nicht exakt der gewaehlte ist), dann waere der
   Anleitungssatz eine einzige Zeile statt eines Bedingungsgeflechts. Das ist
   ein Hinweis an `ui-ux-designer`/`director`, keine Aenderung von mir.
2. **`docs/release/RELEASE_TEXT.md:41-49` und `:91-99`** tragen exakt dieselbe
   Luecke wie README:7 vorher — "It never writes to the game or to the save
   file" ohne den Ausfuehrungssatz. Das ist **nicht meine Datei** (gehoert dem
   `release-manager`); ich melde es, wie im Auftrag verlangt, statt es zu
   aendern.
3. **`docs/legal/AUFLAGEN.md`** fuehrt A-024 und A-027 noch als „offen". Der
   Text existiert jetzt in README.md; das Registerfeld selbst aendert der
   `director`/`compliance-agent`, nicht ich — reine Weiterleitung.

## Was ich nicht dokumentieren konnte

Die visuelle Erscheinung der A1/A2/A3/E1/W1/C1/C2/C3-Fenster und des `Find my
save…`-Knopfs — siehe Selbsttest-Tabelle und Abschnitt 3 oben. Die
Anleitungstexte dazu stammen wortgetreu aus `UI_SPEC.md`, sind aber am
laufenden Programm nicht bildlich bestaetigt.
