# T-229 — Bericht ui-ux-designer (T-229c, Review)

Stand `8ce5b3b` (Code `719c46d`), `git status` sauber. Methode: live am
laufenden Fenster (Windows, Fusion/dunkle Palette, kein `offscreen`, L-009),
kein Klon — der Stand ist eingefroren, `qa-engineer`/`security-reviewer`
laufen parallel auf demselben Stand ohne Schreibzugriff auf diesen Baum
([[ui-messung-am-laufenden-fenster]]: Klon dann nicht zwingend, hier
vermerkt). Testabzug (841 Dateien, `EXTRACT_VERSION` 11) in das umgelenkte
`LOCALAPPDATA` kopiert, `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-229`, `APPDATA`
umgelenkt. Bildnachweise ausschliesslich `QWidget.grab()` (NH-002/L-012).
Fuenf Skripte im Scratchpad, real gegen den Spielstand des Nutzers gefahren
(gefunden ueber `savefile.save_roots()`s eigenen `Path.home()`-Fallback,
nicht ueber meine `APPDATA`-Umlenkung).

```
STATUS: erledigt
AUFTRAG: T-229c — Review der Oberflaeche nach A16/A30-A32 gegen UI_SPEC.md (AK-05, AK-51, AK-160, AK-182 bis AK-188, AK-194, AK-196, AK-212, AK-264 bis AK-268), am laufenden Programm, Stand 8ce5b3b/719c46d
GELESEN: docs/tasks/T-229.md vollstaendig, CLAUDE.md, UI_SPEC.md (Kopf, Widerspruchsabschnitt Z84-137, AK-05/AK-51/AK-160/AK-182-AK-194/AK-196/AK-212/AK-264-AK-268 und Umfeld), DESIGN_REVIEW.md (Review 2026-09-12 vollstaendig), Agent-Memory (Testabzug, Messrezept), nrplanner/{app.py,advisorbar.py,relicpicker.py,firstrun.py,paths.py,favourites.py,gamepath.py}, nrdata/savefile.py (save_roots/find_saves), tests/advisor_row_at_the_window.py, tests/conftest.py (wait_for_the_save)
GEÄNDERT: DESIGN_REVIEW.md (Review vom 2026-09-13 angehaengt, DR-022 bis DR-024), dieser Bericht. Keine Code-, Test- oder Spec-Aenderung. Scratchpad: C:\Users\Daniel\AppData\Local\Temp\claude\...\scratchpad\T-229\ui\ (Testabzug-Kopie, sechs Messskripte, Screenshots); design-review/2026-09-13/ (zehn PNG, Auswahl der Belege)
ANNAHMEN: (1) Kein Klon noetig — eingefrorener Stand, kein Schreibzugriff Dritter auf diesen Baum waehrend der Messung, im Rezept vorgesehene Ausnahme. (2) Realer Spielstand traegt 314 Kopien, nicht 312 (UI_SPEC/Auftragskopf) — als Hinweis an QA weitergereicht, nicht selbst nachgezaehlt (T-229a Punkt 6 ist dort). (3) AK-189s 21/22-Zeilen-Worst-Case wurde nicht am realen, laengsten Slot nachgebaut (Zeitbudget) — als Backlog-Punkt vermerkt, 4.14 hielt bei den real beobachteten (kuerzeren) Slotgruppen.
NÄCHSTER: director (buendelt mit T-229a/T-229b zu einem Fixauftrag)
BLOCKIERT DURCH: nichts
```

## Gesamturteil

**Braucht Arbeit.** Die Beraterleiste mit Lesart-Box selbst — Reihenfolge,
Beschriftung, gemeinsame Deaktivierung, die vier Nennungen der Lesart,
AK-05/AK-194 an der realen abgeleiteten Startbreite — trifft ihre eigene
Vorgabe wortgetreu, real am Spielstand des Nutzers nachgemessen. AK-264 (E1,
zwei Headlines) trifft die Vorgabe buchstabengetreu. Der Befund, der zaehlt,
liegt im Relic Picker: er faellt nach einer Entwertung des Spielstands
waehrend er offen ist **nicht** in den von AK-212/AK-267 vorgeschriebenen
Zustand zurueck, sondern zeigt einen inneren Widerspruch. Die urspruengliche
QA-247-Regression (alte Karten bleiben stehen) ist behoben; eine
Nachbar-Ursache aus derselben Familie ist an ihre Stelle getreten.

## Befunde (Prioritaet, AK-Bezug, DR-Nummer)

1. **DR-022 [Kritisch, AK-212/AK-267/A7]** Ein bereits offener Relic Picker
   zeigt nach `Rescan save` ohne Fund `0 of 0 relics · ranked against your
   build with Slot 1 empty, worst case · …` samt weiterhin sichtbarer
   Custom-Kachel, statt AK-212s vorgeschriebenem Zustand (leere Kopfzeile,
   keine Kachel, `Your relics appear here.`) plus AK-265s Satz `No save was
   read, so there is nothing to rank these against — use Rescan save.`
   Ursache: `relicpicker.py:1006` verbindet `stock_replaced` nur mit
   `_refresh()`, nie mit einem Reset von `self.ranking`; `_refresh()` liest
   also ein Ranking-Objekt aus der Zeit vor der Entwertung gegen einen jetzt
   leeren Kandidatenpool. **Antwort auf die Auftragsfrage („entspricht das
   AK-212?"): nein.**
2. **DR-023 [Wichtig, Accessibility-Luecke neben AK-05/AK-194]** Die
   Statuszeile ist bei der abgeleiteten Startbreite nur per Maus-Hover
   vollstaendig lesbar: `_ElidingLabel` hat `focusPolicy() == Qt.NoFocus` und
   leeren `accessibleName()` (faellt bei Qt auf den elidierten `text()`
   zurueck) — Tastaturnutzer und Screenreader erreichen `whole_text()` nie.
   Die Breiten-Entscheidung selbst (A31/A32) wird **nicht** in Frage
   gestellt und haelt: real 67 px, > 0, in beiden Zustaenden.
3. **DR-024 [Nice-to-have]** Bei 67 px bleibt von der Statuszeile nur ein
   Wort plus Ellipse — der Auf-einen-Blick-Zweck der Zeile geht verloren,
   ohne dass ein AK verletzt wird. Vorschlag (keine Umsetzungspflicht): ein
   breitenunabhaengiges Erfolgs-/Fehler-Symbol neben `Optimize`.

## Positiv / beibehalten (Auszug, vollstaendig in DESIGN_REVIEW.md)

AK-182 (Reihenfolge/Voreinstellung), AK-183 (Verwerfen bei Lesartwechsel),
AK-184/185/186 (genau vier Nennungen, keine doppelte Zahl, `declared`
unangetastet — real am Optimize-Lauf mit 314 Relikten geprueft), AK-268
(alle drei Bedienelemente gemeinsam deaktiviert ohne Spielstand), AK-264
(beide E1-Headlines wortgleich), AK-51/AK-196/AK-266 (keine waagerechte
Bildlaufleiste, drei volle Zeilen am realen Bestand), AK-05/AK-194
(1608 px reale Startbreite, 67 px Statuszeile — deckt sich exakt mit
A32/T-225, keine Regression).

## Vorschlag zu AK-160

Der Director hat die Messfenster-Frage bereits entschieden: Bezugsbreite
folgt AK-05 (abgeleitete Startbreite, am laufenden Fenster gemessen, keine
feste Zahl). Das loest die zweite Ungereimtheit (die feste `1320 px`) aus
demselben Grund, aus dem sie AK-05 und AK-194 geloest hat. Die erste
Ungereimtheit — AK-160 als „schlechtester Fall" ist durch AK-189 (21/22
Zeilen statt 14/15, je Lesart getrennt) ueberholt — ist bereits im Text
selbst als *„bleibt als Messung seiner Umgebung gueltig, wird durch AK-189
fortgeschrieben"* vermerkt und braucht keine weitere Entscheidung, nur eine
redaktionelle Klarstellung.

**Konkreter Vorschlag (Redaktion, nicht in diesem Lauf ausgefuehrt):**

- AK-160s Messfenster-Satz *„Zu messen bei Fensterbreite 1320 px
  (Startbreite) und UI scale Automatic sowie 150 %"* wird ersetzt durch *„Zu
  messen bei der abgeleiteten Startbreite (A14, am laufenden Fenster, wie
  AK-05) und UI scale Automatic sowie 150 %"*.
- Der Vermerk *„Widerspruechlich — die Entscheidung steht beim App Designer
  aus"* entfaellt ersatzlos; an seine Stelle tritt ein Verweis auf AK-189
  (*„der schlechteste Fall wird durch AK-189 fortgeschrieben, diese Tabelle
  bleibt als Umgebungsmessung — laengster Name, laengste Zeile —
  gueltig"*), wortgleich mit der bereits vorhandenen Formulierung bei
  AK-161.
- Der Abschnitt „Drei widerspruechliche Faelle" (Z84-137) wird auf „Alle drei
  entschieden" aktualisiert, mit demselben Verweis.

Das ist eine Textaenderung ohne neue Messzahl und ohne Verhaltensaenderung —
ich habe sie nicht selbst ausgefuehrt (Auftrag: „nicht aendern"), sie liegt
als Vorschlag beim Director/App Designer.

## Offene Fragen an den App Designer

Keine neuen — DR-024 ist eine Anregung, kein Entscheidungsbedarf; die
314-vs-312-Abweichung ist eine Zaehlfrage an QA, keine Geschmacksfrage.

## Pfade

- `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\DESIGN_REVIEW.md`
  (Review vom 2026-09-13, DR-022 bis DR-024)
- `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\design-review\2026-09-13\`
  (zehn Screenshots)
- `C:\Users\Daniel\AppData\Local\Temp\claude\C--Users-Daniel-Desktop-ClaudeCode-Nightreign-Helper\944e515e-121f-4a1d-be61-0ce5bd032585\scratchpad\T-229\ui\`
  (Messskripte, vollstaendiger Screenshot-Satz)
