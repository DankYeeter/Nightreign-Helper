STATUS: erledigt
AUFTRAG: T-146 — AK-232 nachziehen: fragen nur, wenn der Ordner den gewaehlten Baum verlaesst (ui-ux-designer, Spec)
GELESEN: docs/tasks/T-146.md · UI_SPEC.md (T-074-Abschnitt vollstaendig, insbesondere §2-§4.2, §7-§9, AK-106 bis AK-132; T-145-Nachtrag „Was aus dem gewaehlten Ordner wirklich passiert" vollstaendig) · security/findings.md:482 (SEC-030) · docs/berichte/T-144-security-reviewer.md (Abschnitt SEC-030)
GEÄNDERT: UI_SPEC.md · docs/berichte/T-146-ui-ux-designer.md (dieser Bericht)
ANNAHMEN: keine
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Was geaendert wurde

**Die Regel:** C3 (Rueckfrage) greift nur noch, wenn der aufgeloeste Ordner
den gewaehlten Baum **verlaesst** (Aufstieg, Zweigwechsel, Verzeichnis-
verknuepfung). Beim **Abstieg** — der aufgeloeste Ordner liegt innerhalb des
gewaehlten, der Regelfall aus §4.2 — erscheint **kein** C3 mehr: sofort C2,
dann Bau. Das nimmt die T-145-Entscheidung fuer genau den Fall zurueck, den
ich in T-145 selbst als falsch begruendet gemeldet hatte.

**AK-232 nachgezogen** (Vermerk, alte Fassung steht), neue Fassung im
Nachtrag „AK-232 nachgezogen" am Dateiende.

**Ausser AK-232 zusaetzlich beruehrt und nachgezogen** (mehr als die Task-Zeile
„AK-233 bis AK-239 pruefen" allein nahelegt, aber notwendige Folgen derselben
Regeleanderung, keine Erweiterung des Auftrags):

- **AK-234**: die Zeile, die nach `Use this folder` in C3 erscheint, war
  „C2" (`..., inside the folder you picked.`). Das ist unter der neuen Regel
  **immer falsch** — C3-Faelle sind jetzt nie mehr „innerhalb", also darf die
  Bestaetigungszeile das nicht behaupten. Korrektur: es ist **C1**
  (`Found your game in {Pfad}`, ohne Ortsbezug).
- **AK-237**: das Pruefungsbeispiel wechselte den Elternordner (das ist jetzt
  ein Abstieg und loest fuer sich genommen gar kein C3 mehr aus) — ersetzt
  durch ein Beispiel, in dem W1 **und** ein waere-C3-Fall gleichzeitig
  zutreffen, damit die Regel „hoechstens eine Rueckfrage" noch etwas belegt.
- **§3.4** (Speicherzeitpunkt): „`paths/game` wird im Fall C2 erst
  geschrieben, wenn Use this folder gedrueckt ist" hiess es — muss „im Fall
  C3" heissen, weil reiner Abstieg (C2 ohne C3) jetzt sofort speichert, wie
  C1.
- **§3.3** (Standardknopf-Begruendung): stuetzte sich auf „der Nutzer waehlt
  fast sicher den Elternordner" (§4.2) — genau der Fall, der jetzt gar kein
  C3 mehr ausloest. Begruendung korrigiert, Schlussfolgerung (Standardknopf
  bleibt `Use this folder`) unveraendert.
- **§3.2-Beschriftung**: `The game itself is in:` → `The game itself is
  outside that folder, in:` — sagt das Verlassen jetzt ausdruecklich, wie im
  Auftrag verlangt.

**AK-233, AK-235, AK-236, AK-238, AK-239 unberuehrt** — geprueft, mit Vermerk
im Bestand bestaetigt. Sie beziehen sich auf C1 oder auf Verhalten innerhalb
des C3-Zustands, unabhaengig vom Ausloeser.

**Neue Kriterien:** AK-240 (Abstieg loest kein C3 aus — die eigentliche
Korrektur der T-145-Annahme, mit eigener Pruefung), AK-241 (C3-Wortlaut
nennt das Verlassen), AK-242 (Zeile nach C3 ist C1, nicht C2).

**Offene Frage 1 aus T-145** im Dokument als beantwortet markiert
(§7 des T-145-Abschnitts), mit Verweis auf diese Entscheidung; der alte
Fragetext bleibt als Zitat stehen.

## SEC-030

**Deckt diese Praezisierung ab, aber nur zur Haelfte.** Der Offenlegungsteil
(„angenommener Ordner kann ausserhalb des Baumes liegen, den der Nutzer
gesehen hat" — die Vertrauensgrenze, um die es sicherheitlich geht) ist
geschlossen: eine Verzeichnisverknuepfung, die aus dem gewaehlten Baum
herausfuehrt, ist per Definition ein Verlassen und loest jetzt **immer** C3
aus, statt still uebernommen zu werden — das ist genau die vom
security-reviewer genannte Behebungsrichtung („Ergebnis ueber Path.resolve()
gegen den gewaehlten Baum halten"), jetzt als sichtbare UI-Bedingung. Der
Traversierungsteil (Laufzeit-/Schleifensicherheit von `search_from` beim
Betreten von Reparse-Punkten, bevor ueberhaupt ein Ergebnis vorliegt) ist
**keine Oberflaechenfrage** und bleibt ein eigener Punkt fuer V1 beim
`developer`/`security-reviewer`.

## Was ich zusaetzlich gefunden und korrigiert habe (ueber den Wortlaut des Auftrags hinaus, aber notwendig)

Die drei Punkte oben (AK-234, §3.4, §3.3) sind keine neue Ausweitung des
Auftrags — sie folgen zwingend aus der Regeländerung, die AK-232 selbst
beschreibt: sobald C3 nur noch bei „Verlassen" feuert, wird jeder Text, der
noch vom alten „C3 bei jeder Abweichung" ausgeht, falsch oder irrefuehrend.
Ich melde sie trotzdem ausdruecklich, weil der Auftrag nur AK-232 bis AK-239
nannte und diese drei Stellen (§3.3, §3.4, AK-234) nicht in dieser Liste
standen.

## Nicht angefasst

`ARCHITECTURE.md`, `security/findings.md`, `nrplanner/`, `nrdata/`, `tests/`,
`GOAL.md`, `docs/state.md`, `qa/findings.md`, `docs/tasks/`. Keine Millisekunde
gemessen — der Ablauf ist nicht gebaut (V1/V2 stehen aus), reine Textarbeit
wie im T-145-Abschnitt.

## Akzeptanzkriterien (neu bzw. veraendert)

- AK-232 (neu gefasst): C3 nur beim Verlassen des Baumes; Abstieg → kein C3.
- AK-234 (neu gefasst): nach C3-Bestaetigung erscheint C1, nicht C2.
- AK-237 (neu gefasst): Pruefungsbeispiel auf einen echten Doppelfrage-Fall
  umgestellt.
- AK-240 (neu): Abstieg loest kein C3 aus, Fensterfolge wie vor T-145.
- AK-241 (neu): C3-Beschriftung nennt das Verlassen ausdruecklich.
- AK-242 (neu): Zeile nach C3 behauptet keine „innerhalb"-Beziehung.

## Offene Fragen an den App Designer

Keine neuen. Frage 2 aus T-145 (README/Release-Text) bleibt offen, geht an
den `technical-writer` nach V3.

Pfad: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\UI_SPEC.md`
