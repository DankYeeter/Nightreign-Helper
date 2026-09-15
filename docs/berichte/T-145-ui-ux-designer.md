# T-145 - ui-ux-designer: zwei Saetze vor V2 (Spec-Modus)

STATUS: erledigt
AUFTRAG: T-145 — SEC-027 (Panel-Text A1/W1) und AK-118 (Rueckfrage im Fall C2)
GELESEN: `~/.claude/agents/_rahmen.md` · `CLAUDE.md` · `docs/tasks/T-145.md` ·
`docs/berichte/T-144-security-reviewer.md` (vollstaendig, insbesondere
Abschnitt 2 zu SEC-026/SEC-027, Abschnitt 4 mit M1-M3 und S1-S4, Abschnitt 8
mit B1-B5) · `UI_SPEC.md` Abschnitt „Der Erststart mit Ordnerauswahl" (T-074)
vollstaendig (§0 bis §12, AK-106 bis AK-132) plus die Nachtrags-Konventionen
der uebrigen Datei · `ARCHITECTURE.md` Nachtrag XI, AD-030 (Kontext,
Aufloesungspunkt, Kette 1-5) und die Bauschritt-Tabelle V1-V5 (nur gelesen) ·
`docs/release/RELEASE_TEXT.md` 38-52 und `README.md` (Suche nach derselben
Zusage) · `nrplanner/app.py:100-120` aus `git show 84cf70e:` (Farbtoken, weil
der Arbeitsbaum durch T-142 veraendert ist)
GEAENDERT: `UI_SPEC.md` (einzige Projektdatei, **nicht** committet, nicht
gestaged) · `docs/berichte/T-145-ui-ux-designer.md` (dieser Bericht) ·
`.claude/agent-memory/ui-ux-designer/feedback_reassurance_lines_need_a_code_check.md`
(neu) und `.claude/agent-memory/ui-ux-designer/MEMORY.md` (eine Zeile) —
Rollengedaechtnis, kein Spec-Inhalt
ANNAHMEN: (1) Die Rueckfrage im Fall C2 ist ein **Frage-Zustand desselben
Fensters**, kein zweites Fenster und kein Modal — das folgt aus §3 („kein
zweites Fenster neben `firstrun._Window`"), steht aber so nicht im Auftrag.
(2) Trifft W1 mit C2 zusammen, entfaellt C3; der Auftrag sagt dazu nichts, und
zwei Rueckfragen fuer eine Wahl waeren die teurere Lesart. (3) Escape in C3
bedeutet `Quit`, wie in A1/A2/E1/W1 — eine Fortschreibung von §9, keine neue
Regel.
NAECHSTER: director — er erteilt V2 mit dem Wortlaut aus §7 in der neuen
Fassung und den Kriterien AK-230 bis AK-239; die zwei offenen Fragen unten
gehen an den App Designer.
BLOCKIERT DURCH: nichts.

---

**Gemessen gegen `84cf70e`** (`git log -1` im Arbeitsbaum, der im Auftrag
genannte Stand). **Modus: Spec.** Das Programm wurde **nicht** gestartet, kein
Datenverzeichnis beruehrt, keine Umlenkung noetig, kein Prozess und kein Port
hinterlassen. **Kein Bildnachweis** aus diesem Lauf — der Ablauf ist noch
nicht gebaut (V1 und V2 stehen aus), es gibt nichts zu fotografieren. Der
Scratchpad `…/scratchpad/T-145/` ist geleert.

## 1. Was geschrieben wurde

Alles in `UI_SPEC.md`, an vier Stellen:

| Stelle | Art | Was |
|---|---|---|
| §7, Text **A1** | ersetzt | `It is only read.` → der Satz, der sagt, dass ein Programm aus dem Ordner laeuft. Erster Satz unveraendert. Vermerk mit Datum darunter. |
| §7, Text **W1** | ergaenzt | neuer vierter Absatz, sinngemaess derselbe Satz, eine Spur fester. Vermerk darunter. |
| §7, Text **C3** | **neu** | die Rueckfrage im Fall C2, voller Wortlaut. C2 selbst bleibt Wort fuer Wort und steht jetzt hinter C3. |
| **AK-118** | Vermerk davor | alte Fassung bleibt stehen, gilt unveraendert fuer C1; fuer C2 zeigt der Vermerk auf AK-232 bis AK-239. |
| Dateiende | **neu** | Nachtrag „Was aus dem gewaehlten Ordner wirklich passiert, und die Rueckfrage im Fall C2 (ui-ux-designer, T-145) — 2026-09-08", 7 Abschnitte, mit AK-230 bis AK-239. |

**Nichts umgeschrieben.** Kein bestehendes Kriterium hat einen anderen
Wortlaut bekommen, keine AK-Nummer wurde neu vergeben oder gestrichen.

## 2. Der Wortlaut

**A1**, dritter Absatz, neu:

```
Nothing in that folder is changed, moved or deleted. To read the game's
files, Nightreign Helper runs a small program out of that folder, so pick a
copy of the game you trust — normally the one you play.
```

**W1**, neuer vierter Absatz:

```
To read it, Nightreign Helper runs a small program out of this folder, so
only carry on with a copy of the game you installed yourself.
```

**C3**, neuer Frage-Zustand:

```
Is this your game?

You picked:
{gewaehlter Pfad}

The game itself is in:
{aufgeloester Pfad}

That is the folder Nightreign Helper will read from.

[ Choose a different folder... ]  [ Use this folder ]
```

Die Begruendung je Formulierung (Handelnder genannt, an den Ordner gebunden,
Folge genannt, keine Angst, Spielersprache, verbotene Woerter) steht im
Nachtrag §1; sie hier zu wiederholen waere die Doppelung, die der Rahmen
verbietet.

## 3. Die Rueckfrage C3 — Kurzfassung

- **Wann:** nur wenn der aufgeloeste Ordner vom gewaehlten abweicht (C2). Nach
  E1 nie; nach einem mit `Use this folder anyway` beantworteten W1 nie
  (hoechstens eine Rueckfrage je Wahl). Bei C1 aendert sich **nichts**.
- **Was gezeigt wird:** beide Pfade vollstaendig, je mit Beschriftung, in
  normaler Textfarbe, umbruchfaehig; ein Satz, welcher der beiden gilt.
- **Wie beantwortet:** `Use this folder` ist der Standardknopf und liegt
  rechts (Fluent), Enter loest ihn aus. Bewusst **anders als AK-113**: W1
  fragt nach einem Verdacht, C3 nach einer Selbstverstaendlichkeit.
- **Ablehnung:** `Choose a different folder...` oeffnet den Systemdialog
  erneut, Startort ist der **zuvor gewaehlte** Ordner; ein Abbruch dort fuehrt
  unveraendert nach C3 zurueck (AK-115-Muster).
- **Escape / Fensterkreuz:** `Quit`, ohne gespeicherte Angabe.
- **Speichern:** `paths/game` wird erst nach `Use this folder` geschrieben,
  weiterhin **vor** dem Bau. AK-117 bleibt woertlich gueltig; es verschiebt
  sich nur, wann „bestaetigt" im Fall C2 eintritt.

## 4. Die dritte beruehrte Stelle — gemeldet, nicht still umgebaut

Der Auftrag nennt zwei Stellen; der neue Satz zieht **eine dritte** nach:

**§3 Reihenfolge Punkt 5 und §8 Tokentabelle.** Punkt 5 hiess „Beruhigung:
dass nichts angefasst wird (`MUTED`)". Der Block ist jetzt **Einordnung**,
nicht mehr nur Beruhigung, und er steht in der **normalen Textfarbe** statt
`MUTED`. **Begruendung liegt im Bestand:** AK-129 nimmt die Pfadzeile aus
demselben Grund aus `MUTED` heraus — „weil sie das ist, was der Nutzer pruefen
soll". Der Grund ist **nicht** der Kontrast: `MUTED` `#8a8a8a` gegen `PANEL`
`#1e1f23` rechnet sich aus den zwei Hexwerten zu rund **4,8:1** und liegt
ueber AA. **Das ist eine Rechnung, keine Messung** — der Frage-Zustand ist
nicht gebaut, und ob `firstrun._Window` ueberhaupt `PANEL` als Grund hat, ist
damit nicht gezeigt. **Kein neues Token**, die Fusszeile bleibt `MUTED`.

Ausserdem fortgeschrieben, weil ein neuer Zustand es verlangt: die
Escape-Aufzaehlung in §9 nennt jetzt auch C3. Das ist ein Zustand mehr in
einer Liste, keine geaenderte Regel.

## 5. Was ich melde, statt es zu entscheiden

**C2 ist der Regelfall, nicht die Ausnahme.** §4.2 sagt woertlich: *„Der
Nutzer waehlt fast sicher `...\ELDEN RING NIGHTREIGN`, nicht
`...\ELDEN RING NIGHTREIGN\Game`."* Genau diese Wahl **ist** C2. Die
Begruendung der Director-Entscheidung — *„der Klick kostet nur dort, wo das
Programm einen anderen Ordner nimmt als gezeigt"* — trifft damit fast jeden,
der das Panel ueberhaupt sieht; klickfrei bleibt nur, wer den `Game`-Ordner
selbst trifft. **Ich habe die Entscheidung wie erteilt ausgeschrieben** und
melde die Zahl dahinter. Drei Dinge federn es ab: das Panel sieht nur, wessen
Spiel die Automatik nicht findet (AK-106); der Standardknopf ist der
bestaetigende, ein Enter genuegt; und C3 ist die erste Stelle, an der der
Nutzer ueberhaupt erfaehrt, **welchen** Ordner das Programm nimmt.

Wer den Klick auf die seltenen Faelle begrenzen will: nur den **Aufstieg**
(§4.2, bis zwei Elternebenen) und den Wechsel in einen anderen Zweig
zurueckfragen, den Abstieg nicht. Das steht als offene Frage 1 im Nachtrag.
**Empfehlung: erst so lassen wie erteilt** und nach dem ersten
`power-user`-Lauf entscheiden.

**Hoehenzuwachs in A1.** Der neue Satz ist laenger; bei 460 logischen px
Breite rechne ich mit **rund zwei Zeilen mehr**. Das ist eine Schaetzung aus
der Zeichenzahl, **keine Messung**. Die Hoehe ist inhaltsabhaengig
(Mindesthoehe 230), der Nachweis ist AK-129/AK-239 und gehoert an das
laufende Fenster.

## 6. Die Eigenschaft, nicht die Fundstelle — was die Nachsuche fand

Zwei unabhaengig formulierte Masken ueber `*.md` und `*.py` ausserhalb
`.venv/`:

1. `only read` → **15 Treffer** ohne diesen Bericht (mit ihm 19, nachgezaehlt
   je Datei). Nach der Aenderung stammt **kein einziger** aus einem
   Oberflaechentext: **6** sind Befund- und Auftragsprosa
   (`T-144-security-reviewer.md` 3, `docs/tasks/T-145.md` 2,
   `security/findings.md:479` 1), **4** sind meine eigenen Vermerke in
   `UI_SPEC.md`, **4** sind Kommentare ueber ganz andere Dinge (`app.py:1717`,
   `scripts/differential/mutate.py` 2, `test_loadout_table_prefilter.py`), und
   **1** steht in einer Agenten-Gedaechtnisdatei.
2. `never writes|read-only|only reads|does not run|nothing is changed` →
   Treffer in Auftrags- und Regeltexten, und **zwei nutzersichtbare Stellen**:

- **`docs/release/RELEASE_TEXT.md:41-49` und `:91-99`** (zwei Fassungen
  desselben Textes): *„It reads and decrypts, locally, the game files … It
  never writes to the game or to the save file"* und *„it reads your own
  installation"*. **Falsch ist davon nichts** — geschrieben wird tatsaechlich
  nicht. Unvollstaendig ist es in derselben Weise wie A1: von der Bibliothek,
  die aus dem Ordner **ausgefuehrt** wird, steht dort nichts, und mit A15 wird
  aus „your own installation" ein Ordner, auf den jemand zeigt.
- **`README.md:7`**: *„reads your own game install"* — dasselbe eine Stufe
  kuerzer.

**Beides ist nicht mein Auftrag und nicht meine Datei.** Es deckt sich mit
dem, was der `security-reviewer` unter A-024/A-027 an den `technical-writer`
gegeben hat (SEC-006, Nutzerentscheid 02.09.2026, *„ein ehrlicher Satz im
README"*). **Es steht in keinem Auftrag** — der `director` muss es erteilen,
sonst faellt es hinten herunter. Reihenfolge: nach V3.

## 7. Gegenproben zu meinen eigenen Behauptungen

- **„AK-230 ist frei."** Nicht aus dem Auftrag uebernommen, sondern gegen
  `UI_SPEC.md` geprueft: hoechste belegte Nummer **AK-229**. **Positivkontrolle
  der Suche:** dieselbe Maske `AK-2[0-9][0-9]` findet AK-230 sehr wohl — in
  `docs/tasks/T-145.md:76` und `docs/berichte/T-141-ui-ux-designer.md:146`.
  Die Suche schlaegt also an, wenn es etwas zu finden gibt. (Diese Probe steht
  hier, weil derselbe Griff in T-141 einmal danebengegangen ist: die im
  Auftrag genannte „freie" Nummer war damals bereits vergeben.)
- **„Keines der verbotenen Woerter."** Die Liste aus §7 einzeln gegen die
  drei neuen Bloecke gehalten. Kritisch waren `extract`, `param`, `cache`,
  `snapshot` als Teilzeichenketten — keines kommt vor, auch nicht in einem
  laengeren Wort.
- **„Nichts anderes angefasst."** `git diff --stat` nennt fuer meinen Anteil
  genau eine Datei: `UI_SPEC.md`, **339 Zeilen**. Die uebrigen sechs
  geaenderten Dateien (`nrplanner/app.py`, `nrplanner/inventory.py`,
  `tests/…`) stammen aus dem parallel laufenden T-142 und sind von mir weder
  gelesen noch beruehrt worden — ausser `app.py:100-120` **aus
  `git show 84cf70e:`**, also aus dem committeten Stand, nicht aus dem
  Arbeitsbaum.
- **Nicht geprueft, mit Grund:** ob der neue A1-Text in der gebauten
  Oberflaeche ohne Abschneiden passt (das Fenster existiert nicht), und ob
  `firstrun._Window` `PANEL` als Hintergrund benutzt (Codestelle liegt im
  Arbeitsbaum des parallelen `developer`; die Kontrastzahl oben ist deshalb
  ausdruecklich eine Rechnung aus Token, kein Messwert).

## 8. Akzeptanzkriterien fuer V2 (Kurzliste, Volltext im Nachtrag §6)

- **AK-230** Kein Text sagt oder legt nahe, es werde nur gelesen; A1 und W1
  sagen beide, dass etwas aus dem Ordner ausgefuehrt wird. `It is only read`
  kommt im Anwendungscode nicht vor.
- **AK-231** Die drei neuen Bloecke sind Englisch (A8) und frei von den in §7
  verbotenen Woertern (AK-127).
- **AK-232** Weicht aufgeloest von gewaehlt ab, kommt C3 **vor** dem Bau und
  zeigt beide Pfade vollstaendig.
- **AK-233** Ist aufgeloest gleich gewaehlt, kommt **kein** C3 und kein
  zusaetzlicher Klick (A15, AK-106).
- **AK-234** `Use this folder` ist Standardknopf, Enter loest ihn aus, danach
  C2 und der Bau ohne weiteren Klick.
- **AK-235** `Choose a different folder...` oeffnet den Systemdialog erneut,
  Startort ist der zuvor gewaehlte Ordner; Abbruch fuehrt nach C3 zurueck.
- **AK-236** Solange C3 offen ist, ist `paths/game` unveraendert (harter
  Abbruch in C3, Neustart: es fragt erneut, alter Wert steht).
- **AK-237** Nach einem bestaetigten W1 kommt kein C3 — hoechstens eine
  Rueckfrage je Wahl.
- **AK-238** Escape und Fensterkreuz in C3 beenden ohne gespeicherte Angabe.
- **AK-239** 100/125/150 % und Programmfaktoren bis `200%`: nichts
  abgeschnitten, Pfadzeilen brechen um; Nachweis **aus dem Fenster** gezogen
  (NH-002).

**Keine Millisekunde in den Kriterien** — nachgezaehlt: null Zeitangaben in
AK-230 bis AK-239.

## 9. Offene Fragen an den App Designer

1. **Soll C3 auch beim Abstieg kommen** (`...\ELDEN RING NIGHTREIGN` →
   `...\Game`), also im Regelfall? So ist es erteilt und so ist es
   ausgeschrieben. Gegenoption: nur beim Aufstieg und beim Zweigwechsel
   zurueckfragen — dann bleibt der Regelfall klickfrei.
   **Empfehlung: so lassen und nach dem ersten `power-user`-Lauf entscheiden.**
2. **Soll dieselbe Auskunft auch ausserhalb des Erststarts stehen** — im
   README bzw. im Release-Text (siehe Abschnitt 6)? Diese Vorgabe sagt sie
   genau einmal, im Moment der Entscheidung.

**Nicht meine Frage und ausdruecklich nicht beantwortet:** ob die geladene
Bibliothek geprueft wird, und ob SEC-016/017/018 gestrichen bleiben. Der neue
Text behauptet **keine** Pruefung.
