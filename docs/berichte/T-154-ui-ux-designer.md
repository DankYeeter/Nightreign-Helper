STATUS: erledigt
AUFTRAG: T-154 — AK-244 trifft nicht zu (sechster Satz) + Widerspruch S5/§9(f)
GELESEN: docs/tasks/T-154.md · UI_SPEC.md vollstaendig an den betroffenen Stellen (T-141-Abschnitt §6/§9/§11 komplett, T-074/T-145-Abschnitt §7 komplett, T-148-Nachtrag §0-§5 komplett) · nrplanner/app.py (reload_chalices 2902-3050, load_equipped 4151-4321, NO_SAVE_FOUND 593-597) · .claude/agent-memory/ui-ux-designer/MEMORY.md
GEÄNDERT: UI_SPEC.md (drei Stellen: Vermerk an §9 (f) im T-141-Abschnitt, Vermerk am Kopf von AK-244, neuer Nachtrag „AK-244 nachgezogen: die Regel statt der Liste, und der Widerspruch bei S5" am Dateiende mit neuem Kriterium AK-245) · .claude/agent-memory/ui-ux-designer/feedback_criterion_rule_not_sentence_list.md (neu) · .claude/agent-memory/ui-ux-designer/MEMORY.md (Zeile ergaenzt)
ANNAHMEN: keine — beide Korrekturen sind am Quelltext verifiziert (app.py:595-597, 2965-2973, 4151-4321), nicht geraten. Programm nicht gestartet (Spec-Modus, reine Nachzeichnung von bereits Gebautem, keine Oberflaechenzahl betroffen, L-009 entfaellt).
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## 1. AK-244 — der sechste Satz ist keiner, es ist eine offene Familie

Nachgezaehlt, einmal vollstaendig: `load_equipped()` schreibt bei jedem
automatischen Aufruf aus `reload_chalices` (app.py:2972) am Ende **immer**
in `owned_label` — drei Fehlertexte (AK-244 kannte sie) und, bei Erfolg,
eine von vier Grundformen ("Loaded {Nightfarer} — …") mit optional ein oder
zwei angehaengten Klauseln ueber nicht platzierbare Relikte. Das sind nicht
sechs oder sieben Saetze, sondern eine offene Menge — dieselbe Bauform wie
die Bestandsnotiz selbst. Eine Liste literaler Saetze ist deshalb die
falsche Form fuer dieses Kriterium; sie faellt bei der naechsten
Textaenderung in `load_equipped` erneut aus, ohne dass sich am eigentlichen
Zustand etwas aendert.

**Entscheidung (Punkt 2 des Auftrags, zweite Lesart gewaehlt):** AK-245
ersetzt die zweite Haelfte von AK-244 durch eine Regel statt einer Liste:
loest ein Lesen das automatische Uebernehmen aus, gewinnt immer der Text, den
`load_equipped()` selbst zuletzt geschrieben hat — gleich ob Erfolg oder
Scheitern. Es gibt in `load_equipped()` keinen von diesem Aufruf aus
erreichbaren Zweig, der `owned_label` unveraendert liesse (verifiziert: jeder
Rueckgabepfad ab Zeile 4167 schreibt vor dem Return; der einzige
ungeschriebene Fall, `is_reading()`, ist zeitlich ausgeschlossen). Loest das
Lesen die automatische Uebernahme nicht aus, gilt AK-224 unveraendert. AK-244
erste Haelfte (die drei Fehlertexte) bleibt gueltig, ist ein Teilfall von
AK-245.

**Punkt 3 (soll der sechste Satz weg?):** Nein. Er erklaert dem Spieler,
warum seine Chalice-Slots gerade Inhalt bekommen haben, ohne dass er etwas
angeklickt hat — dieselbe Begruendung, die AK-224 schon fuer die
Slot-Ausnahme nennt. Reihenfolge (ersetzt statt ergaenzt) ist ebenfalls
richtig: der Bestand bleibt ueber die Slotueberschriften sichtbar, eine
kombinierte Zeile wuerde die gemessene Hoehe aus AK-225 sprengen. Keine neue
offene Frage an den App Designer — das ist eine objektiv begruendbare
Bauform-Entscheidung, kein Geschmacksfall.

## 2. S5 gegen §9 (f) — aufgeloest

S5 (Abschnitt „Der Erststart mit Ordnerauswahl", §7, T-145, 08.09.2026,
zeitlich **nach** T-141 vom selben Tag) und §9 (f) im T-141-Abschnitt
beschreiben dieselbe Zeile (`app.py:595-597`, Konstante `NO_SAVE_FOUND`) —
einmal drei-, einmal zweisaetzig. Geloest zugunsten von **S5**: der
`developer` hat danach gebaut, die Konstante im Quelltext ist dreisaetzig.
§9 (f) traegt jetzt einen Vermerk mit Verweis auf S5, die alte zweisaetzige
Fassung bleibt zur Nachvollziehbarkeit stehen (nachgezogen, nicht
umgeschrieben). Eine dritte, aehnlich lautende Fundstelle (Zeile 2611,
Kurzquote mit „…" ueber den Zustand **vor** dem Ablauf) ist kein Widerspruch
— sie erhebt keinen Vollstaendigkeitsanspruch.

## 3. Reichweite

Beide Korrekturen beruehren zusammen genau drei Stellen in UI_SPEC.md (§9(f)
im T-141-Abschnitt, der AK-244-Kopf, plus der neue Nachtrag mit AK-245) —
keine vierte, keine Aenderung an AK-222, AK-224 selbst (nur referenzierend,
nicht zitierend, daher unberuehrt) oder an Abschnitt §6.

**Parallel laufendes T-153 nicht beruehrt:** AK-228, AK-229 (langsamer
Rueckfallsatz, §7/§8 des T-141-Abschnitts) und AK-110 (Dialog-Startort, §9/§10
des T-074/T-145-Abschnitts) sind von keiner der beiden Korrekturen betroffen
— geprueft, nicht nur behauptet.

## Neues Kriterium

- **AK-245** *(load_equipped gewinnt immer, wenn es angestossen wird)* —
  ersetzt AK-244 zweite Haelfte. Volltext, Aufbau und toetende Mutation in
  UI_SPEC.md, Nachtrag „AK-244 nachgezogen: die Regel statt der Liste, und der
  Widerspruch bei S5" (ui-ux-designer, T-154) — 2026-09-09, §4.

Pfad: `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\UI_SPEC.md`
