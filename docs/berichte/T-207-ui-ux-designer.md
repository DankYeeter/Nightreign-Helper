STATUS: erledigt
AUFTRAG: T-207 — UI-Review auf dem Stand `9cb8bae` (Review-Modus)
GELESEN: docs/tasks/T-207.md; DESIGN_REVIEW.md (vollstaendig, DR-001 bis
  DR-018); UI_SPEC.md §5.4 (AK-256 bis AK-263, Messumgebung, Tabelle
  „was die dritte Zeile kostet"); qa/findings.md (QA-228 bis QA-241,
  insbesondere QA-229, QA-230, QA-237, QA-239, QA-241); .claude/agent-memory
  /ui-ux-designer/MEMORY.md + beide Projekt-Memories; nrplanner/relicpicker.py,
  nrplanner/advisorbar.py, nrplanner/app.py (Planner, RelicSlot, _open_picker),
  nrplanner/favourites.py, nrplanner/paths.py (Umlenkungspfade);
  tests/test_relic_picker_geometry.py
GEÄNDERT: DESIGN_REVIEW.md (neuer Abschnitt „Review vom 2026-09-12",
  DR-019 bis DR-021); UI_SPEC.md (Zeile 2230, Nachtrag zu QA-239);
  design-review/2026-09-12/*.png (3 Bilder, aus QWidget.grab(), nicht vom
  Bildschirm); .claude/agent-memory/ui-ux-designer/MEMORY.md,
  project_ui_messung_rezept.md, project_testabzug_fehlt.md (aktualisiert);
  docs/berichte/T-207-ui-ux-designer.md (dieser Bericht).
  Kein Anwendungscode geaendert.
ANNAHMEN: Der Auftrag nennt „vierwertiges Urteil" — ich lese das als das
  STATUS-Feld dieses Kontraktblocks (vier erlaubte Werte), nicht als eine
  vierte Kategorie im Gesamturteil von DESIGN_REVIEW.md (das die
  Rollendefinition dreiwertig fuehrt: ship-ready/fast fertig/braucht
  Arbeit). Falls „vierwertig" etwas anderes meinte, bitte przisieren.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

## Was geprueft wurde

Live, am echten `Planner`+`RelicPicker`, mit dem Spielstand des Nutzers und
dem festen Testabzug (841 Dateien, `EXTRACT_VERSION` 11) — **kopiert in**
das umgelenkte `LOCALAPPDATA`, alle drei Variablen vor dem ersten
`nrplanner`-Import gesetzt und einzeln nachgewiesen (`favourites._settings()
.fileName()` → `HKEY_CURRENT_USER\Software\DankYeeterT-207\...`, `paths
.cache_dir()` → Scratchpad-Pfad, `data.meta.extract_version` → 11). Stil
`fusion` mit dunkler Palette, kein `QT_QPA_PLATFORM=offscreen`. Bildnachweise
ausschliesslich `QWidget.grab()` auf das eigene Dialogobjekt — kein
Bildschirmabzug, strenger als `PrintWindow`. Details, Skripte und
Positivkontrolle stehen im neuen `DESIGN_REVIEW.md`-Abschnitt.

Zwei Schwerpunkte laut Auftrag (Relic Picker, drei Richtungen; QA-229/230),
plus die verlangte Nachmessung von QA-239. Die sechs Inhalts-Tabs
(DR-013 bis DR-018, Review 2026-09-05) wurden **nicht** erneut geprueft —
nichts an ihnen hat sich seit damals geaendert, der Auftrag nennt sie nicht,
und sie stehen in `qa/findings.md` nirgends als behoben. Sie gelten
unveraendert offen.

## Ergebnis in Kuerze

**Gesamturteil: fast fertig.** Der Bau der dritten Zielrichtung
(AK-256–AK-263) trifft seine eigene Vorgabe ungewoehnlich praezise — jede
nachgemessene Zahl (sechs fuehrende Karten in der Aufteilung 2/1/3, drei
staendige Wertzeilen, Chip auf jeder fuehrenden Karte, Chipbreiten 91/95/76 px
gegen 79 px Streifen) stimmt mit `UI_SPEC.md` exakt ueberein. Kein Kritisch-
Befund. Was offen bleibt, ist nicht der neue Bau selbst:

- **QA-229** (Chip-Abschneidung) bleibt offen, unveraendert in der Zahl,
  aber **exponierter**: jetzt stehen bei Favoriten drei Chips im selben Bild,
  von denen einer (der neue, `BEST FOR STATS`) sauber lesbar ist und zwei
  mitten im Wort abbrechen — der Kontrast macht den Fehler sichtbarer, und
  mit sechs statt vormals bis zu drei vorgezogenen Karten ist die Flaeche
  groesser, auf der ein Spieler ihn trifft.
- **QA-239**: die eigene `UI_SPEC.md`-Zahl (1136 px) ist nach einer zweiten,
  unabhaengigen Messung nicht einfach durch eine neue Einzelzahl ersetzbar —
  ich habe **selbst zwei widerspruechliche Werte** gemessen (1151 px
  berechnet, 1061 px tatsaechliche Dialoghoehe, 90 px Differenz), zusaetzlich
  zu T-199s 1121 px. Die Tabellenzeile ist entsprechend korrigiert (keine
  einzelne Zahl mehr, sondern ein Nachtrag mit allen vier Werten und Verweis).
  AK-196 haelt bei jeder der vier Zahlen — kein Nutzerschaden heute.
- **Eine neue, echte Design-Frage** (DR-021, an den App Designer): drei der
  sechs vorgezogenen Karten tragen denselben Relikt-Namen (`Grand Luminous
  Scene`, echter Dreifach-Gleichstand). Ob das die Vorziehung fuer den
  Spieler schwerer scanbar macht, ist eine Geschmacksfrage, keine von mir
  entscheidbare.

## Befunde (Details in `DESIGN_REVIEW.md`, Review vom 2026-09-12)

- **DR-019** (Nice-to-have) — `wanted_height()` berechnet 1151 px, der
  ungezwungene `dialog.height()` erreicht nur 1061 px im selben Lauf; drei
  Messlaeufe auf derselben Maschine ergaben drei verschiedene Werte fuer
  dieselbe Groesse. Kein Nutzerschaden (AK-196 haelt), aber ein
  Dokumentations-/Testluecken-Befund: der existierende Test erzwingt die
  Groesse von Hand und kann die Abweichung nicht sehen.
- **DR-020** (bestaetigt QA-229, P2/Major bleibt bei `developer`) — Chip-
  Abschneidung unveraendert in der Zahl (91/95 px gegen 79 px Streifen),
  aber sichtbar exponierter durch die dritte, funktionierende Richtung im
  selben Bild und durch mehr vorgezogene, favoriten-verdaechtige Karten.
- **DR-021** (Offene Frage an den App Designer, keine Vorgabe) — drei
  gleichnamige Karten in der Attributs-Spitzengruppe, echte Scanbarkeitsfrage.

## Was gut ist (beibehalten)

AK-261, AK-262, AK-258, AK-259 halten alle Zahl fuer Zahl gegen die
Vorgabe — der `developer` hat hier ungewoehnlich genau gegen `UI_SPEC.md`
gebaut, das verdient die ausdrueckliche Nennung im Positiv-Abschnitt.

## Fuer den Director

- **Registryschluessel bereinigt** (`HKCU:\Software\DankYeeterT-207` nach
  Abschluss geloescht, mit `Test-Path` gegengeprueft: `False`).
- **Kein Python-/Qt-Prozess mehr aktiv** (`tasklist` nach Abschluss leer).
- Die Korrektur an `UI_SPEC.md:2230` ist keine neue Vorgabe, sondern die vom
  Auftrag verlangte Nachmessung der eigenen Zahl — bewusst **ohne**
  Einzelwert an Stelle des durchgestrichenen, weil zwei unabhaengige eigene
  Messungen nicht uebereinstimmen; das ist im Nachtrag begruendet.
