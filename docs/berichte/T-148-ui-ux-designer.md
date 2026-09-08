STATUS: erledigt
AUFTRAG: T-148 — drei Praezisierungen an AK-220 bis AK-229 (Spec-Modus)
GELESEN: docs/tasks/T-148.md · UI_SPEC.md, vollstaendiger T-141-Abschnitt
(§0-§14, AK-220 bis AK-229) und die T-145-Nachtrag-Umgebung · GOAL.md (A7, A8
— T-148.md zitierte kein Abnahmekriterium und keinen Stand-Auszug, deshalb
selbst nachgelesen) · docs/state.md (Zeilen 240-253, F-S/F-T-Entscheid,
bestaetigt keinen Widerspruch zu dieser Arbeit) · Quelltext (nur gelesen,
nichts gestartet): nrplanner/app.py (rescan_save 3788-3811,
_show_the_save_is_being_read 3813-3823, _on_save_read 3830-3876,
_on_save_failed 3898-3908, load_equipped 3910-3985, reload_chalices
2718-2830), nrplanner/advisorbar.py (status_line 182-220, AdvisorBar
419-490, _ask 664-671, _resting 770-774, _show 796-821, Zustandstabelle
UI_SPEC.md Zeile 237 = 4.8), nrplanner/chalices.py (imported/set_imported
619-632), nrplanner/inventory.py (loadouts_for 141, loadout_error 104/249),
tests/test_save_read_in_the_background.py (Zeilen 1-42, 637-701, nur
gelesen) · eigene Memory-Eintraege project_save_read_third_state.md,
project_relic_picker_wait_state.md
GEÄNDERT: UI_SPEC.md (Pointer-Vermerke direkt bei AK-223, AK-224, AK-229
eingefuegt, alte Fassungen unveraendert stehen gelassen; neuer Abschnitt
"drei Praezisierungen an AK-220 bis AK-229 (ui-ux-designer, T-148) —
2026-09-09" am Dateiende angehaengt, mit AK-243 und AK-244) ·
docs/berichte/T-148-ui-ux-designer.md (dieser Bericht)
ANNAHMEN: T-148.md enthielt kein Zitat aus GOAL.md/docs/state.md — beide
selbst nachgelesen (s.o.), kein Widerspruch zum Auftrag gefunden, daher keine
Ruecksprache noetig.
NÄCHSTER: developer (baut AK-243 und AK-244; AK-229-Vermerk ist reine
Dokumentation, kein Bauauftrag)
BLOCKIERT DURCH: nichts

## Ergebnis, kurz

Alle drei vom `developer` gemeldeten Stellen sind aufgeloest, ausschliesslich
in `UI_SPEC.md`, ohne eine bestehende Kriteriumsfassung zu ueberschreiben.

**1. AK-223 (Optimize gesperrt) → AK-243.** Der `developer` hat richtig
gebaut. `AdvisorBar.optimize_button` ist im Wartezustand gesperrt, aber nicht
durch AK-221 (das Lesen), sondern durch eine **bereits an anderer Stelle
dieser Datei spezifizierte, aeltere** Bedingung: Zustand 4.8 der
Advisor-Zustandstabelle (`UI_SPEC.md` Zeile 237, `owned is None` →
`Optimize` deaktiviert). AK-223 hat diese Ueberlappung nie zitiert und
behauptet binaer „gesperrt ist genau eines" — ein Waechter, der das woertlich
umsetzt, verlangte `Optimize` waehrend des Lesens freigegeben und liesse den
irrefuehrenden Satz `No save was read, so there are no relics to choose from
— use Rescan save.` waehrend eines laufenden Lesens zu. AK-243 benennt beide
gesperrten Elemente und ihre verschiedenen Freigabebedingungen: der
Reliktknopf wird frei, sobald das Lesen endet (jedes der vier Enden aus §6);
`optimize_button` erst, sobald `owned` tatsaechlich nicht mehr `None` ist —
und bleibt deshalb nach „kein Spielstand gefunden" **dauerhaft** gesperrt,
anders als der Reliktknopf (dessen Verhalten in diesem Ende der bekannte,
unveraenderte A7-Bruch aus §12 bleibt).

**2. AK-224 (vier Enden) → AK-244.** Bestaetigt: es gibt einen fuenften
Satz. `_on_save_read` ruft nach dem Setzen der Bestandsnotiz unbedingt
`reload_chalices()`, und die kann `load_equipped()` automatisch ausloesen
(erstes Mal, dass `owned` fuer den gezeigten Nightfarer nicht `None` ist, und
sein Spielstand speichert ein Build fuer ihn). Scheitert dieser Auto-Import,
ueberschreibt `load_equipped` die gerade gesetzte Bestandsnotiz mit einem von
drei eigenen Saetzen (Ladefehler / kein ausgeruestetes Build / Vessel nicht
in der Liste). Wie gemeldet: das ist kein Nebeneffekt der Thread-Trennung,
sondern eine Folge der T-141-Entscheidung, `reload_chalices` auch beim
ersten Lesen unbedingt laufen zu lassen — auf dem synchronen Weg waere
dasselbe passiert. AK-244 fasst beide Faelle (vier alte Enden ODER drei neue)
binaer zusammen und schliesst die Luecke im *Aufbau* von AK-224 („vier
Vorrichtungen" kannte den fuenften Fall nicht).

**3. AK-229, zweite Haelfte → Vermerk, keine neue Nummer.** Der vom
`developer` gebaute Waechter (`tests/test_save_read_in_the_background.py:
637-701`) laesst genau eine benannte Ausnahme zu
(`_check_the_prefilter_can_see_every_id`) und bewacht sie mit einer
Positivkontrolle, deren eigener Docstring bereits sagt: sie muss reissen,
sobald AK-228/V4 die Ausnahme entfernt. **Das entspricht der Absicht** — der
langsame Rueckfallweg existiert im Code nicht, also kann die Id-Pruefung noch
nicht vom Werfen aufs Vermerken umgestellt werden, und eine Pruefung, die den
einen bekannten Fall stillschweigend ausliesse, waere ein Waechter, der sein
eigenes Pruefmittel misst statt die Sache. AK-229 braucht trotzdem einen
Vermerk, weil ihr woertlicher Text sonst mehr behauptet, als heute gilt: der
Waechter ist gruen, aber **fuer echte Spieler ist der Selbstwiderspruch aus
§8 vor V4 nicht behoben** — ein Spielstand, der die `RELIC_ID_CEILING`
erreicht, zeigt heute noch `Save could not be read: … nothing is wrong with
the save.` Der Vermerk haelt das fest, verbietet dem Whitelist-Eintrag zu
wachsen, und weist die Priorisierungsfrage (Risiko bis V4) ausdruecklich an
den `director` statt sie in eine neue AK-Nummer zu verpacken.

**Reichweite:** gepreuft und unveraendert gelassen: §5 (nennt `Optimize`
ohnehin nicht erschoepfend), AK-220 bis AK-222 und AK-225 bis AK-228, §9 (h).
Keine vierte Stelle betroffen.

## Pfad

`C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\UI_SPEC.md` — neuer
Abschnitt am Dateiende, Pointer-Vermerke bei AK-223 (Zeile ~7684), AK-224
(Zeile ~7693) und AK-229 (Zeile ~7751).
