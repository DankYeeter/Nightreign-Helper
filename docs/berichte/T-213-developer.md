STATUS: erledigt
AUFTRAG: T-213 — L-019 und L-020: zwei Waechter im Agenten-Repo
GELESEN: docs/tasks/T-213.md · docs/berichte/T-209-retrospective.md (vollstaendig) · docs/lessons.md (Abschnitte "Nummernraum", L-019, L-020 vollstaendig) · claude-agent-team: commands/director.md (Zeilen 1-90 und 835-880, sowie die Volltextsuche nach "120 Zeilen|Zyklusende|state\.md" ueber die ganze Datei) · hooks/selftest.ps1 (vollstaendig) · hooks/require-receipt.ps1 · hooks/no-root-find.ps1 · hooks/remind-sync-out.ps1 · hooks/limit-tool-calls.ps1 (als Vorbild fuer "meldet, sperrt nicht") · ~/.claude/settings.json · git status/log/diff in claude-agent-team
GEÄNDERT: **im Repo `claude-agent-team`** (nicht im Nightreign-Helper): `hooks/selftest.ps1`, `hooks/state-line-budget.ps1` (neu), `commands/director.md` — geschrieben und in drei Commits abgelegt (`9c63c37`, `a2a6f7b`, `7c7de4c` auf `main`, **ungepusht**, 3 Commits vor `origin/main`). **Im Nightreign-Helper:** `docs/berichte/T-213-developer.md` (diese Datei) — sonst nichts.
ANNAHMEN: (1) Ziel 1 verlangt laut Auftrag ausschliesslich die Ergaenzung in `hooks/selftest.ps1` — die in `docs/lessons.md` zusaetzlich vorgeschlagene Erweiterung von `require-receipt.ps1` um `CLAUDE.md` gehoert nicht zu diesem Auftrag (Beruehrte Dateien nennt sie nicht) und wurde nicht umgesetzt. (2) "Parameter mit Vorgabewert" (Vorgabe 2 zu Ziel 2) und "aus der Director-Definition lesen" sind als zwei alternative Bauformen zu verstehen, von denen ich die robustere gewaehlt habe: der Hook liest die Zahl zur Laufzeit aus `commands/director.md`, traegt aber **keinen** eigenen Zahlen-Fallback — findet er sie nicht, bleibt er still. Begruendung unten. (3) "Nur Hauptsitzung" fuer `state-line-budget.ps1` uebernommen aus dem woertlichen Kopfkommentar des L-020-Entwurfs in `docs/lessons.md:1288`, da `docs/state.md` laut `commands/director.md:71` ohnehin nur vom Director geschrieben wird.
NÄCHSTER: director
BLOCKIERT DURCH: nichts fuer die Umsetzung. Offen bleibt die Freigabe/Registrierung durch den Nutzer (Abschnitt "Registrierung" unten) sowie eine Entscheidung des Directors zu einer gefundenen Inkonsistenz in `commands/director.md` (Abschnitt "An den director" unten).

---

## Umgesetzt

### Ziel 1 — L-019: Registrierungspruefung in `hooks/selftest.ps1`

Neuer Abschnitt am Ende der Datei (vor der Zusammenfassung), committet in
`9c63c37`. Er gleicht jede `*.ps1`-Datei in `hooks/` (ausser `selftest.ps1`
selbst) gegen den Rohtext von `~/.claude/settings.json` ab und meldet die,
die nicht vorkommen. Eine `$OFFEN`-Liste (aktuell leer) ist der einzige
zulaessige Weg, einen Hook bewusst unregistriert zu lassen — mit Grund als
Kommentar, "darf nur schrumpfen".

**Gezaehlt (selbst, nicht uebernommen):** `ls hooks/*.ps1 | wc -l` ergab **13**
Dateien vor meiner Aenderung (deckt sich mit der Zahl des Directors), **14**
danach (durch `state-line-budget.ps1`), davon **13** tatsaechlich gepruefte
Hooks (`selftest.ps1` zaehlt sich nicht selbst).

**Null Zeilen Regeltext:** Der Abschnitt ist ausschliesslich Pruefcode plus
Kommentare im Hook selbst. Keine Agentendefinition und kein `_rahmen.md`
angefasst.

### Ziel 2 — L-020: `hooks/state-line-budget.ps1` (neu) + `commands/director.md:71`

Neuer Hook, `PreToolUse` auf `Write|Edit|MultiEdit`, committet in `a2a6f7b`
und `7c7de4c` (letzterer nur ein zusaetzlicher Testfall, siehe unten).

- **Nur Hauptsitzung:** Team-Agenten (`agent_type` gesetzt) werden sofort
  durchgelassen, analog zu `require-receipt.ps1`.
- **Pfadfilter, projektunabhaengig:** greift nur, wenn `tool_input.file_path`
  auf `/docs/state.md` endet. Kein Treffer in einem Projekt ohne diese Datei
  = der Hook tut nichts (Vorgabe 3 erfuellt, ohne eigene Sonderbehandlung
  noetig — die Bedingung ist bereits die Sonderbehandlung).
- **Die Zahl 120 steht nicht als Literal im Hook.** Er liest sie zur Laufzeit
  per Regex `hoechstens\s+(\d+)\s+Zeilen` aus `commands/director.md` (Pfad
  relativ zum eigenen Skriptstandort im Agenten-Repo, nicht zum Projekt des
  Write-Aufrufs — das macht ihn projektunabhaengig einsetzbar). **Findet er
  die Datei oder die Zahl nicht, bleibt er still** (kein Fallback-Literal,
  kein Fehlalarm) — als `ponytail:`-Kommentar im Hook dokumentiert. Das ist
  die schaerfere der beiden im Auftrag genannten Bauformen: eine zweite,
  unabhaengig gepflegte Zahl im Hook selbst haette exakt die Doppelung
  reproduziert, die dieses Team gerade dreimal bezahlt hat.
- **Zeilenzaehlung wie `wc -l`** (Anzahl `\n`-Zeichen im resultierenden Text),
  konsistent mit dem Erfolgskriterium aus `docs/lessons.md`, das ebenfalls mit
  `wc -l` misst.
- **Meldet, sperrt nicht:** `permissionDecision: allow` mit
  `permissionDecisionReason`, Bauform uebernommen von der Vorwarnung in
  `limit-tool-calls.ps1`.
- **`commands/director.md:71`:** Halbsatz `**geprueft einmal am Zyklusende**`
  gestrichen, ersetzt durch `(`hooks/state-line-budget.ps1` zaehlt beim
  Schreiben)`.
- **`hooks/selftest.ps1`:** fuenf neue `Check`-Faelle fuer den Hook
  (Existenz, Ueberschreitung, unter Budget, Hauptsitzungs-Filter,
  Pfad-Filter, plus nachtraeglich ein Edit-spezifischer Fall — siehe unten).

## Laeufe je Hook — Ausloeser und Durchlass

### L-019 — Registrierungspruefung

Live-Ausschnitt aus `powershell -NoProfile -ExecutionPolicy Bypass -File
./hooks/selftest.ps1` (Repo-Wurzel `claude-agent-team`), ungekuerzt aus dem
tatsaechlichen Lauf nach dem Commit:

```
PASS  block-source-read.ps1 ist in settings.json registriert
PASS  check-handoff.ps1 ist in settings.json registriert
PASS  check-reply-length.ps1 ist in settings.json registriert
PASS  count-serial-dispatches.ps1 ist in settings.json registriert
PASS  idle-guard.ps1 ist in settings.json registriert
PASS  limit-tool-calls.ps1 ist in settings.json registriert
FAIL  no-root-find.ps1 ist in settings.json registriert - nicht registriert - der Hook existiert, feuert aber nie
PASS  remind-rules.ps1 ist in settings.json registriert
FAIL  remind-sync-out.ps1 ist in settings.json registriert - nicht registriert - der Hook existiert, feuert aber nie
FAIL  require-receipt.ps1 ist in settings.json registriert - nicht registriert - der Hook existiert, feuert aber nie
PASS  set-dispatch-model.ps1 ist in settings.json registriert
FAIL  state-line-budget.ps1 ist in settings.json registriert - nicht registriert - der Hook existiert, feuert aber nie
PASS  sync-repos.ps1 ist in settings.json registriert
```

**Durchlassender Fall:** die neun bereits registrierten Hooks -> `PASS`.
**Ausloesender Fall:** die drei vorbestehenden Luecken aus dem L-019-Befund
(`require-receipt.ps1`, `no-root-find.ps1`, `remind-sync-out.ps1`) plus mein
eigener neuer `state-line-budget.ps1`, der naturgemaess noch nicht
registriert ist -> `FAIL`, mit exakt der erwarteten Meldung. **Das ist der
beabsichtigte Zustand, kein Fehler meines Codes** — genau diese vier
Zeilen sind der Befund, den L-019 sichtbar machen sollte.

Zusaetzlich separat demonstriert (weil `settings.json` auf diesem Rechner
existiert, der HINWEIS-Zweig also nicht im normalen Lauf greift): mit
`$env:USERPROFILE` auf ein leeres, eigens angelegtes Verzeichnis gesetzt und
derselbe Codeblock wie in `selftest.ps1` ausgefuehrt —
Ausgabe: `HINWEIS  Registrierungspruefung uebersprungen -
<Pfad>\.claude\settings.json nicht gefunden (settings.json liegt nicht im
Repo)`, `fails=0`. Bestaetigt: fehlende `settings.json` erzeugt keinen FAIL.

### L-020 — `state-line-budget.ps1` (eigenstaendige Laeufe, JSON auf stdin)

Fall 1 — Write, 130 Zeilen Inhalt (129 `\n`), Pfad endet auf
`docs/state.md` -> **AUSLOESEND**:
```
{"hookSpecificOutput":{"permissionDecision":"allow","hookEventName":"PreToolUse","permissionDecisionReason":"[state-budget] 129 Zeilen, Budget 120 - kuerzen in diesem Zug, nicht im naechsten Commit."}}
```

Fall 2 — Write, 40 Zeilen, gleicher Pfad -> **DURCHLASSEND** (leere Ausgabe).

Fall 3 — Write, 130 Zeilen, Pfad `docs/tasks/T-500.md` -> **DURCHLASSEND**
(Pfadfilter greift, leere Ausgabe).

Fall 4 — Write, 130 Zeilen, Pfad `docs/state.md`, aber `agent_type:
developer` gesetzt -> **DURCHLASSEND** (Hauptsitzungs-Filter greift, leere
Ausgabe).

Fall 5 — Edit auf eine echte Datei (115 Zeilen Basis unter
`<tmp>/docs/state.md`), `old_string`/`new_string` haengt 20 Zeilen an ->
**AUSLOESEND**:
```
{"hookSpecificOutput":{"permissionDecision":"allow","hookEventName":"PreToolUse","permissionDecisionReason":"[state-budget] 134 Zeilen, Budget 120 - kuerzen in diesem Zug, nicht im naechsten Commit."}}
```
Belegt, dass der Edit-Zweig korrekt gegen den vorhandenen Dateiinhalt rechnet
(anders als Write kennt er den "Vorher"-Zustand nur durch Lesen der Datei).

Alle fuenf Faelle sind zusaetzlich dauerhaft in `hooks/selftest.ps1`
verankert (Commits `a2a6f7b` fuer die ersten vier, `7c7de4c` fuer den
Edit-Fall, den ich nachtraeglich ergaenzt habe, weil die urspruenglichen vier
Faelle nur den Write-Zweig abdeckten und der Edit-Zweig eine eigene
Rechenlogik ist — "neue Logik ohne Test ist unfertig").

## Ergebnis von `hooks/selftest.ps1` (Endstand)

```
101 PASS, 4 FAIL, exit 1
```

Die vier `FAIL` sind ausschliesslich die Registrierungsluecken aus dem
Abschnitt oben (drei vorbestehend + `state-line-budget.ps1` neu, weil noch
nicht registriert). **Kein FAIL geht auf einen Fehler meiner Aenderung
zurueck** — jede meiner neuen Check-Zeilen (state-line-budget: 5 Faelle,
`director.md` unter 950 Zeilen: 901, B-Verweise: alle belegt) steht auf
`PASS`. Der Selbsttest wird erst gruen, sobald der Nutzer die Registrierung
vornimmt (siehe unten) oder die drei vorbestehenden Luecken bewusst in
`$OFFEN` eingetragen werden — Letzteres ist keine Entscheidung, die mir
zusteht.

## An den director

**Eine zweite, verwandte Stelle in `commands/director.md` wird durch meine
Aenderung inhaltlich falsch, und der Auftrag hat mich ausdruecklich auf
genau einen Halbsatz beschraenkt ("dort nur den einen Halbsatz").** Ich habe
sie nicht angefasst, sondern melde sie:

`commands/director.md:850-853` (im Abschnitt zu B-24, "Eine Datei, die ein
Test bewacht, pruefst du VOR dem Commit gegen ihren Waechter"):

> *Fuer `docs/state.md` gilt das ausdruecklich **nicht**: ihr Zeilenbudget
> wird **einmal am Zyklusende** geprueft (Nutzerentscheidung 08.09.2026), und
> ein Test, der sie bewacht, existiert nicht — nachgesehen am 08.09.2026 in
> `tests/`.*

Das ist eine zweite, unabhaengig formulierte Kopie derselben
"Zyklusende"-Aussage, gefunden ueber eine vom Auftrag unabhaengige
Volltextsuche (`grep -n "120 Zeilen|Zyklusende|state\.md"` ueber die ganze
Datei). Sie behauptet zusaetzlich woertlich, dass **kein Test** `docs/state.md`
bewacht — das stimmt nach dieser Aenderung nicht mehr:
`hooks/state-line-budget.ps1` ist genau so ein Waechter, nur eben einer, der
meldet statt sperrt. Die Stelle war 08.09. ausdruecklich als
**Nutzerentscheidung** markiert (Ausnahme von B-24) und nicht nur als
Beobachtung — ich korrigiere Nutzerentscheidungen nicht eigenmaechtig. Drei
Optionen: (a) die Nutzerentscheidung erneut einholen, ob die B-24-Ausnahme
fuer `docs/state.md` mit dem neuen Hook entfaellt, (b) den Text redaktionell
an den neuen Stand anpassen (z. B. "ihr Zeilenbudget wird beim Schreiben
gemeldet, nicht gesperrt — B-24 gilt hier bewusst nicht als Sperre"), (c) die
Stelle bewusst so stehen lassen, weil B-24 von *sperrenden* Waechtern
spricht und ein meldender keiner ist. Ich empfehle (b), entscheide es aber
nicht.

## Tests

Abgedeckt: alle Verzweigungen von `state-line-budget.ps1` (Ueberschreitung,
Einhaltung, Hauptsitzungs-Filter, Pfad-Filter, Edit- statt Write-Zweig) sowie
beide Zustaende der Registrierungspruefung (Datei registriert/nicht
registriert, `settings.json` vorhanden/fehlend) — alle als dauerhafte
`Check`-Faelle in `hooks/selftest.ps1` verankert, nicht nur ad hoc gezeigt.
Bewusst nicht abgedeckt: `MultiEdit` auf `state-line-budget.ps1` (die
Codepfad-Logik ist identisch zu `Edit`, nur mit einer Schleife ueber
`tool_input.edits` — im Vorbild `require-receipt.ps1` ebenfalls nicht separat
getestet).

## DoD

- [x] Anforderung verstanden, Annahmen dokumentiert (drei, oben)
- [x] `hooks/selftest.ps1` laeuft (101 PASS, 4 FAIL — die vier sind der
      erwartete, gemeldete Befund, kein technisches Versagen)
- [x] Neue Tests fuer neue Logik (fuenf Check-Faelle fuer den neuen Hook,
      Registrierungspruefung selbst durch den Lauf oben belegt). Kein Linter
      im Repo konfiguriert — Punkt entfaellt, keine Luecke.
- [x] Keine Secrets, keine TODOs, kein toter Code. `~/.claude/settings.json`
      nicht angefasst (harte Grenze eingehalten).
- [x] Registrierungs-Schnipsel geliefert (unten), da ich `settings.json`
      selbst nicht aendere.
- [ ] Ungeprueft: die tatsaechliche Live-Wirkung von `state-line-budget.ps1`
      als registrierter Hook in einer echten Sitzung (QA-241 gilt auch hier —
      ein Hook, der mitten in der Sitzung registriert wird, feuert in dieser
      Sitzung nicht). Das kann erst NACH der Registrierung durch den Nutzer
      in einer neuen Sitzung geprueft werden.

## Offene Fragen

An den **director**: die Inkonsistenz in `commands/director.md:850-853`
(Abschnitt oben) — Entscheidung (b) empfohlen. Ausserdem: die drei
vorbestehenden `FAIL`-Zeilen (`require-receipt.ps1`, `no-root-find.ps1`,
`remind-sync-out.ps1`) sind nicht Teil dieses Auftrags und bleiben rot, bis
der Nutzer/Director sie registriert oder bewusst in `$OFFEN` eintraegt.

## Registrierung — fuer den Nutzer

`~/.claude/settings.json` habe ich nicht geaendert (harte Grenze dieses
Auftrags). Der Hook liegt bereits unter `~/.claude/hooks/state-line-budget.ps1`
(Junction auf `claude-agent-team/hooks`, geprueft — kein manueller
Sync-Schritt noetig). Zum Registrieren folgenden Eintrag in das
`hooks.PreToolUse`-Array einfuegen (z. B. neben dem Eintrag fuer
`limit-tool-calls.ps1`):

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"C:/Users/Daniel/.claude/hooks/state-line-budget.ps1\"",
      "shell": "powershell",
      "timeout": 15
    }
  ]
}
```

Wirkt laut QA-241 erst in einer **neu gestarteten** Sitzung, nicht in der
laufenden. Nach der Registrierung schliesst ein Lauf von `hooks/selftest.ps1`
den entsprechenden `FAIL` (`state-line-budget.ps1 ist in settings.json
registriert`).

Die drei uebrigen aus L-019 gefundenen Luecken (`require-receipt.ps1`,
`no-root-find.ps1`, `remind-sync-out.ps1`) sind **nicht** Teil dieses
Auftrags und bleiben bewusst unregistriert, bis eine eigene Entscheidung
dazu vorliegt — `docs/lessons.md` fuehrt sie bereits mit "Freigabe nur durch
den Nutzer".
