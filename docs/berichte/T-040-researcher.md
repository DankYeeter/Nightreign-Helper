# T-040 — Bericht des `researcher`

STATUS: erledigt
AUFTRAG: T-040 — R-005: Wie verrechnen sich Nightreigns Schadensmultiplikatoren?
GELESEN: docs/tasks/T-040.md, docs/tasks/T-039.md, docs/tasks/T-038.md (Fan-Notizen im Wortlaut), GOAL.md, docs/state.md, docs/research/R-001.md, R-002.md, R-003.md (alle drei zu anderen Themen — keine Vorarbeit zu dieser Frage), nrplanner/damage.py (vollstaendig), nrplanner/model.py (MOVE_SCOPED_EFFECT_IDS und Umgebung, Effekt-Aufbauschleife Z. 900-999), nrplanner/stacking.py (Docstring), vendor/Paramdex/NR/Defs/SpEffectParam.xml (Feldsatz), sowie die in R-005 einzeln zitierten Web-Quellen
GEÄNDERT: docs/research/R-005.md (neu), docs/berichte/T-040-researcher.md (neu) — sonst keine; kein Git, kein Anwendungscode, die fremden ungespeicherten Aenderungen der parallelen Session nicht beruehrt
ANNAHMEN: (1) Die drei vom Auftraggeber nachgereichten Anker habe ich, soweit im Arbeitsbaum pruefbar, selbst verifiziert — model.py und stacking.py woertlich gelesen; das Commit-Datum 1b2df01 / 2026-08-11 und die Nutzeraussage zur Trainingspuppe habe ich **nicht** nachgeprueft (kein Git erlaubt, kein Zugang zum Nutzer) und als Angabe des Auftraggebers gekennzeichnet. (2) Die Messprotokolle hinter beiden Codestellen ("HANDOVER section 6/6j") existieren laut Auftraggeber nicht mehr; ich stuetze mich auf die Zusammenfassung im Code und habe nicht danach gesucht. (3) Ich habe nicht geprueft, welche Spielversion beim Nutzer installiert ist.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

---

## Kurzantwort (wortgleich zu docs/research/R-005.md)

Nightreign kombiniert Angriffsmultiplikatoren **multiplikativ**, nicht
additiv — und das ist im Projekt zweifach gemessen, nicht angenommen: zwei
+20 %-Effekte ergaben im Spiel 152 / 183 / 219 (219/152 = 1,44 = 1,20²;
additiv waeren 213), und zwei **verschiedene** Effekte mit +6 % und +9 %
ergeben x1,1554 (= 1,06 × 1,09), nicht x1,15. Damit sind gleichartige *und*
verschiedenartige Effekte belegt. Die **Einzelwerte** liegen bei etwa +4 bis
+9 % je gewoehnlichem Relikt-Effekt und bei +20 % fuer "Improved Attack Power
with 3+ ●● Equipped"; sie stehen als Multiplikatoren (z. B. 1,06) direkt in
den Params der eigenen Installation und muessen aus keinem Wiki geholt
werden. Die Statuskonversion der Startwaffe kostet **15 %**, nicht die vom
Fan-Autor geschaetzten ~20 % — drei unabhaengige Quellen nennen 0,85. **Fuer
die ±10 %-Zusage:** die Wahl additiv/multiplikativ macht bei bis zu drei
grossen Buffs unter 10 % aus, ab vier bricht sie (2,07 gegen 1,80 = 15 %);
da multiplikativ belegt und additiv unbelegt ist, ist die Zusage haltbar.
Meine Sicherheit fuer "multiplikativ": **hoch** — die verbleibende
Unsicherheit liegt nicht mehr bei der Rechenvorschrift, sondern bei einer
moeglichen **Obergrenze**, die niemand geprueft hat.

## Befunde in je einem Satz

1. **Gleichartige Effekte multiplizieren, im Spiel gemessen:** 152 / 183 /
   219 mit keinem, einem, beiden von zwei +20 %-Buffs ergibt 219/152 = 1,441
   ≈ 1,20², waehrend additiv 213 zu erwarten waere — Quelle:
   `nrplanner/model.py` ~Z. 912, gelesen 2026-09-03 (Commit 1b2df01 /
   2026-08-11 laut Auftraggeber).
2. **Verschiedene Effekte multiplizieren ebenfalls, auf fuenf Codepfaden
   gemessen:** *"two relics at +6% and +9% give x1.1554, not x1.15"* —
   Quelle: `nrplanner/stacking.py` Z. 15-18, gelesen 2026-09-03; das ist der
   Beleg, der die gefaehrlichste Luecke schliesst.
3. **Ob ein Feld addiert oder multipliziert, entscheidet sein Neutralwert,
   nicht sein Name** — *"0.0 means the field adds, 1.0 means it multiplies …
   Nine fields end in Rate and nevertheless add"* (`nrplanner/stacking.py`
   Z. 3-11, gelesen 2026-09-03); das erklaert, warum die Community
   gutglaeubig "additiv" sagt, ohne dass es fuer die Angriffsraten stimmt.
4. **Die Statusstrafe der Startwaffe ist 15 %, nicht ~20 %:** Fextralife
   (*"Starting weapon inflicts 15% less damage and has 35 Frostbite
   buildup"*), relics.pro (*"Decreases starting weapon's damage by 15%"*) und
   die eigenen Params (x0,85, im Spiel verifiziert 2026-08-22) gegen die
   Schaetzung des Fan-Autors — alle abgerufen/gelesen 2026-09-03.
5. **Die Prozentwerte sind versionsabhaengig und vom Hersteller nirgends
   beziffert:** Patch 1.03 (03.12.2025) erhoehte "Improved ●● Attack Power"
   und "3+ ●● Equipped", Patch 1.03.2 (15.01.2026) nahm es fuer Boegen als
   Fehler zurueck — Quelle: Bandai-Namco-Patch-Notes, abgerufen 2026-09-03;
   die Notes nennen **keinen einzigen Prozentwert**, weshalb das Lesen aus
   den installierten Params der einzig haltbare Weg bleibt.

## Widersprueche, die offen geblieben sind

- **15 % gegen ~20 % bei der Statuskonversion.** Drei Quellen gegen eine
  Fan-Schaetzung mit Tilde. Ich halte 15 % fuer belegt, kann die Herkunft
  der 20 % aber nicht aufklaeren; nur eine Messung am Geraet entscheidet
  (Messung C in R-005, ein einziger Relikt-Wechsel).
- **Eine Sekundaerquelle behauptet weiterhin additiv**
  (switchbladegaming.com) — ohne Messung, mit selbst vergebener Einstufung
  "community research, Tier 4". Ich habe sie nicht unterschlagen, gewichte
  sie aber gegen zwei Eigenmessungen als unbelegt.
- **Die Rohdaten beider Eigenmessungen sind verloren.** Beide Codestellen
  verweisen auf "HANDOVER section 6/6j", die laut Auftraggeber in keinem
  Repo mehr existiert. Ich stuetze mich auf die Zusammenfassung im Code —
  rechnerisch stimmig, aber kein Protokoll.

## Was diese Recherche NICHT beantwortet

- **Gibt es eine Obergrenze fuer den Gesamtmultiplikator?** Nicht
  untersucht, in keiner Quelle erwaehnt. Nach Schliessung der Additiv-Frage
  der wichtigste offene Punkt — und er trifft genau die stark gestapelten
  Builds, die der Berater vorschlagen wird.
- **Die Element-Konversion der Startwaffe** ("converts ~40-50% AP to
  elemental"). Dazu habe ich **keine einzige Quelle** gefunden; die
  Fextralife-Seite ist ein Stub, der Steam-Thread diskutiert nur den Nutzen.
  Das ist eine andere Mechanik (Umverteilung zwischen Schadensarten, kein
  Multiplikator) und gehoert in einen eigenen Auftrag. Billigster erster
  Schritt, ganz ohne Spielmessung: pruefen, ob die Konversion die
  Infusions-Geschwisterzeilen im selben ID-Band benutzt
  (`nrplanner/weaponslots.py` Z. 119-123) — das ist `qa-engineer`-Arbeit.
- **Nightfarer-Faehigkeiten als Angriffsmultiplikator.** Keine Quelle
  gefunden; braucht eine Auswertung der Helden-SpEffects im eigenen
  Datensatz, nicht Recherche.
- **Level als Multiplikator.** Kein Fund fuer einen levelabhaengigen Faktor
  auf den Waffenschaden; alle Quellen beschreiben Level als Attributgewinn.
  Das ist ein Nicht-Fund, keine Widerlegung — T-038 misst die Gegenhypothese
  (Hypothese a) noch.
- **Welche Spielversion installiert ist.** Nicht geprueft, entscheidet aber,
  welche Prozentwerte gelten.

## Nicht erreichte Quellen (Befund, keine Luecke im Vorgehen)

- Nexus Mods "Relic Effect Statistics" — **HTTP 403**.
- Die Google-Tabelle hinter der Steam-Relikt-Uebersicht — **Timeout**.
Beides sind die naechstgelegenen Datamining-Quellen; ich habe sie nicht
gelesen und keine Zugangsbeschraenkung umgangen.

## Angemeldete Nebenfrage (R-004)

Zum Gesamtfaktor ~0,60 habe ich nichts Neues gefunden, aber zwei Hinweise
weitergegeben: (1) **Alle Messungen dieser Recherche sind Verhaeltnisse**,
in denen sich ein konstanter Gesamtfaktor herauskuerzt — R-005 ist damit
unabhaengig von R-004 gueltig, und ein Ergebnis dort entwertet es nicht.
(2) Wenn der Puppenschaden gleich der **angezeigten** Angriffskraft ist
(Nutzeraussage) und die Anzeige bei ~0,60 des Programmwerts liegt, dann
ueberschaetzt das Programm den **realen** Schaden um Faktor ~1,67 — der
Faktor waere dann keine reine Anzeigeregel, was eine der in T-039 genannten
Hypothesen ausschliesst. **Nicht von mir geprueft**, an R-004 weitergegeben.

## Anmerkung zur Rollentreue

Zwei Punkte, die mir aufgefallen sind und die ich **nicht** selbst erledigt
habe: die Docstrings in `damage.py`/`stacking.py` koennten ihre Begruendung
jetzt auf R-005 stuetzen statt auf verstreute Kommentarnotizen (das ist
`developer`-Arbeit), und die Deckelfrage waere ein sinnvoller naechster
Messauftrag an den Nutzer (das schneidet der `director`).

## Pfad

- `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\docs\research\R-005.md`
- `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\docs\berichte\T-040-researcher.md`
