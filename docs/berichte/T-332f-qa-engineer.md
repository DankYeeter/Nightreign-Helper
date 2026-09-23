# T-332f -- Pruefung am Quellstand (qa-engineer)

**Stand:** HEAD `bcfba9b`, Code-Stand `116f5a3` (Diff `116f5a3..bcfba9b` nur
`docs/tasks/T-332.md`). Lauf 23.09.2026 20:53-21:40, ein Fensterlauf
(`python run.py`, `scripts/drive_window.ps1`), keine andere Kopie
(`tasklist` 20:53 und 21:17). Umlenkung: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-332f`,
`LOCALAPPDATA`/`APPDATA` auf `<scratchpad>/T-332f/la1`, `ad1`. Echter
Spielstand nur gelesen (319 Relikte laut Fenster).

**Urteil: CONCERNS** -- alle vier Pruefpunkte am Fenster erfuellt; ein
Befund P4 (Testluecke), keine P1/P2.

## Befund

### [P4 | Minor | Niedrig] QA-297 Kanaltausch im Symbolbau (`iconbuild`) von keinem Test gehalten

**Adressat:** developer
**Betroffen:** `nrdata/iconbuild.py:288` (T-332c, `beebdf1`)
**Umgebung:** Klon von `116f5a3` im Scratchpad, eine Mutation

**Reproduktion:**
1. `git archive 116f5a3`, im Klon `nrdata/iconbuild.py:288`
   `, "raw", "BGRA"` entfernen (Rot und Blau vertauscht in jedem
   `variant_*.png`).
2. `pytest -n auto` im Klon.

**Erwartet:** mindestens ein Test rot (Auftrag T-332c: "nur mit Test, der
ein Pixel byte-gleich vor/nach vergleicht" -- fuer beide Aufrufer genannt).
**Tatsaechlich:** 1934 passed, 9 skipped, 1 failed -- der eine Fehlschlag
ist `test_release_spec_datas::test_the_half_written_snapshot_is_ignored_by_git`
und liegt am Klon ohne `.git`, nicht an der Mutation.

**Analyse:** Der neue Test in `tests/test_hostile_gamedata.py` schickt den
roten BC1-Block nur durch `icons.IconSource` (`icons.py:136`). Der zweite
Aufrufer, `iconbuild.build`, laeuft in keinem Test; die Suite arbeitet auf
einem fertigen Symbolpaket.

**Auswirkung:** Heute keine -- das Verhalten ist richtig (siehe Punkt 2:
frische Extraktion byte-gleich mit dem Testabzug). Ein spaeterer Eingriff an
dieser Zeile faerbte die Reliktsymbole jedes Neunutzers falsch, ohne dass
die Suite es merkt.

**Vorschlag:** Den vorhandenen Rotblock-Test auch durch den Pfad von
`iconbuild.build` schicken (ein Eintrag, ein Pixel), oder den gemeinsamen
Schritt `frombytes(..., "BGRA")` an einer Stelle halten, die beide
Aufrufer nutzen.

## Ergebnisse je Punkt, mit Pflichtaussage zur Testabdeckung

1. **Community-Vermerke.** Deep of Night, Red variants und alle 15 World-
   Events-Eintraege (11 angekuendigte, 4 nicht angekuendigte) einzeln
   angeklickt, Text per UIA gelesen, Bild per `PrintWindow`: kein
   "community-reported", kein Satz "Blue lines ...", keine blaue Zeile
   (Pixel nahe `#7fb2e5` je Bild 6 = Kantenglaettung, gleich in allen 15
   Bildern). Red-variants-Satz in Grau (`#8a8a8a` gemessen). Titel der nicht
   angekuendigten Ereignisse gold, Deep-of-Night-Ereignisse violett wie
   vorher. Alle angezeigten LORE-Felder gleich `v1.18.0` (11 + 4 Eintraege,
   0 Abweichungen). **Tests:** `test_community_material_unmarked` prueft das
   Kriterium fuer den bekannten Vermerk und die alte Farbe; die goldene
   Titelfarbe und eine andere neue Sonderfarbe prueft er nicht.
2. **Regressionen T-332c/d.** Erststart mit leerem Datenordner (Extraktion
   ~100 s aus der Spielinstallation): Ergebnis 841 Dateien, 21 139 391 Bytes,
   `diff -rq` gegen den festen Testabzug **0 Unterschiede** -- haelt
   Kanaltausch, FMG ohne 32-Bit-Zweig, `reverse_bits`, entfernte Felder.
   Symbole im Fenster farbrichtig (rote Relikte rot). Relikt-Auswahl:
   Rangfolge absteigend, Umschalten auf "Minimise damage taken" sortiert neu.
   Nightlord-Karten: UIA `Button` mit Invoke (Fabrik installiert), Enter und
   Space oeffnen das Profil, Tab wandert zur naechsten Karte.
   **Tests:** Karten (`test_card_is_pressable`) und Picker-Reihenfolge
   (`test_advisor_slot_pool`) pruefen das Kriterium; Symbolbau siehe QA-297.
3. **Gemerkter Nightfarer (T-328).** Ironeye gewaehlt, beendet, neu
   gestartet: Ironeye aktiv, gespeicherter Build samt drei Relikten zurueck.
   Undertaker (id 10, letzter Index) ebenso. **Tests:**
   `test_chosen_hero_survives_a_restart` prueft das Kriterium (zweites
   Fenster, gleiche Einstellungen).
4. **Kernablauf.** Spielstand geladen (319), Nightfarer gewechselt, Optimize
   1741 ms Wandzeit (3 von 3 Slots), Why lesbar, Apply all, Build unter
   Namen gespeichert (Registerschluessel `builds\3` geschrieben). Keine
   Ausnahme in stderr.

## Explorationsprotokoll

Gezielt 13 Testdateien seriell: 298 passed (383 s). Volle Suite nur am
Mutanten (oben). Zweite Suchmaske fuer das Stylesheet unten: 48 Dateien,
3 Treffer, 1 echter.

## Beobachtungen

- `eventstab.py:104` ist kein f-String und endet mit `}}`; Qt meldet dreimal
  "Could not parse stylesheet", zeichnet die Liste aber gleich (Probe: 0 von
  48 000 Pixeln verschieden). Seit `cec61c7` (10.08.), keine Wirkung.
- `eventstab.py:110` sagt noch "Listing those under their own label", seit
  T-332a gibt es kein eigenes Kennzeichen mehr.
- Inhaltssaetze wie "Sources disagree: Community write-ups ..." und
  "community-named event" stehen weiter auf dem Schirm; laut Auftrag Inhalt,
  kein Vermerk.

## Nicht getestet

Artefakt (entsteht nach dem letzten Fix); Guide (T-332e); Hook T-332b
(nicht Teil von T-332f).
