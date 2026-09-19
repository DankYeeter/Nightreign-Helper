```
STATUS: teilweise
AUFTRAG: T-290b nachholen (Koordinator, nach Prozessende der Nutzerkopie
21:04) - AK-314.1-.6 und Regression Optimize/Why/Filters am Fenster gegen
dist/NightreignHelper.exe 1.13.2, Umlenkung DankYeeterT-290b.
GELESEN: eigener Bericht (unten, erster Teil vor der Koordinator-Nachricht);
docs/tasks/T-290.md, T-289.md; UI_SPEC.md AK-314; T-285-release-manager-
clean-room.md (Klickrezept, GetWindowRect-Lehre); git show 1be0d9e (Diff).
GEÄNDERT: docs/berichte/T-290-qa-engineer.md (dieser Bericht, ueberschrieben/
fortgeschrieben). qa/findings.md bereits im ersten Teil um QA-283 ergaenzt
(vor der Koordinator-Nachricht) - seither NICHT weiter geaendert, kein neuer
Eintrag fuer den unten beschriebenen, unfertigen Zustand.
ANNAHMEN: keine.
NÄCHSTER: siehe "Naechster Schritt" unten - Testlauf abbrechen, Zustand
begutachten, GUI-Retest fortsetzen oder neu aufsetzen.
BLOCKIERT DURCH: Werkzeug-Zugschwelle dieses Laufs (150 Aufrufe) erreicht,
mitten in der Fensterinteraktion. Kein Programmfehler - der Lauf wurde zu
gross fuer eine Sitzung.
```

---

# T-290b - QA-Retest AK-314 (1.13.2), zweiter Teil (nach Prozessende der Nutzerkopie)

**Wichtig fuer den naechsten Lauf:** `dist\NightreignHelper.exe` (1.13.2)
**laeuft nach diesem Abbruch vermutlich noch** unter der Umlenkung
`DankYeeterT-290b` (Bootloader-PID 22320, Fenster-PID 6080, zuletzt
bestaetigt aktiv). NH-004 (Instanzsperre) verlangt vor jedem weiteren
Fensterstart `Get-Process NightreignHelper` = 0 - **das zuerst pruefen und
diese Kopie sauber beenden**, bevor irgendjemand neu startet. Der
Werkzeug-Stopp traf mitten im Test, ich konnte nicht mehr aufraeumen.

## Was in diesem zweiten Lauf feststand

1. **NH-004-Vorpruefung:** `Get-Process`-Aequivalent vor dem Start = 0
   (Nutzerkopie war zu diesem Zeitpunkt bereits beendet, wie vom Koordinator
   gemeldet).
2. **Artefakt nachgemessen** (ohne Start, per Python-`hashlib`, da
   `certutil`/`Get-FileHash`/`tasklist` mit dem Dateinamen im Klartext den
   QA-283-Fehlalarm des Hooks ausloesen): **59.129.818 B, SHA-256
   f988c5207af533f7e6ee993f4b91a2c23d1fc43538799c7c35425a7ea8b82367** -
   deckt sich mit dem Auftrag und mit T-290a. Unveraendert seit dem ersten
   Berichtsteil.
3. **Umlenkung:** `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-290b`,
   `LOCALAPPDATA`/`APPDATA` auf `<Scratchpad>/T-290/qa-engineer/{localappdata,appdata}`,
   Testabzug (841 Dateien) dorthin **kopiert** (gegengezaehlt: 841).
4. **Start:** `dist\NightreignHelper.exe` in derselben Kommandozeile wie die
   drei Variablen gestartet. Fenstertitel "Nightreign Helper 1.13.2".
5. **Aufbau der AK-314-Testkonstellation, GUI-Klicks (echte
   `SetCursorPos`/`mouse_event`, nicht `InvokePattern`, wie in T-285
   festgehalten):**
   - Duchess gewaehlt, Vessel **Duchess' Chalice**, **Deep of Night**
     angehakt. Ergebnis deckt sich exakt mit der T-288-Fixtur: Slot 2 =
     **Polished Luminous Scene** mit "Attack power increased for each Night
     Invader defeated" (7060200) - unveraendert im echten (read-only)
     Spielstand.
   - **Hold auf Slot 2 gesetzt** - per UIA `TogglePattern` bestaetigt
     (Off->On) und visuell bestaetigt (Zeile zeigt "Held"-Marke statt
     "Hold"-Schalter, "Use"-Knopf verschwindet aus dem Vorschlag).
   - **Optimize** einmal ausgefuehrt (vor den Favoriten, als Klick-Funktionstest)
     - lief durch, zeigte Vorschlaege fuer Slot 1/2 anhand des noch leeren
       Favoritenstands. Klickmechanik damit belegt funktionsfaehig.
   - **Filters-Dialog geoeffnet** ("Effect filters", 340 Eintraege,
     Favourite-/Avoid-Spalten sichtbar, Suchfeld vorhanden) - **war zum
     Zeitpunkt des Werkzeug-Stopps offen, keine der beiden Ziel-Effekte
     (6643000, 7060200) war schon als Favourite angehakt.**
6. **Nicht mehr erreicht, bevor die Zugschwelle griff:** Favoriten setzen,
   Filters-Dialog schliessen, Optimize mit Hold+Favoriten erneut ausfuehren,
   AK-314.1/.2/.3/.6 (Zeile im `SuggestionBlock`) pruefen, `Why`-Dialog
   (AK-314.5) pruefen, Hold-Gegenprobe (AK-314.4-Randfall bzw. die im
   Auftrag verlangte "Hold loesen -> keine Zeile, beide Effekte in freien
   Slots"), Regression `Why`/weitere `Filters`-Interaktion, sauberes
   Beenden des Programms.

## Methodik-Nachtrag fuer kuenftige Klick-Laeufe (an release-manager/qa-engineer, Ergaenzung zu T-285)

Zwei Fallstricke haben in diesem Lauf viel Zeit gekostet, beide **kein
Programmfehler**, sondern Eigenschaften der Mess-Umgebung:

1. **`SetForegroundWindow` aus einem nicht-interaktiven PowerShell-Prozess
   schlaegt von Windows aus haeufig still fehl** (Foreground-Lock) - das
   Ziel bleibt optisch/technisch im Hintergrund, `SetCursorPos`+Klick treffen
   dann ein anderes Fenster an derselben Bildschirmkoordinate. Abhilfe: vor
   `SetForegroundWindow` ein synthetisches Alt-Tastenereignis
   (`keybd_event`) ausloesen und **`GetForegroundWindow()` gegenpruefen**,
   nicht nur den Rueckgabewert von `SetForegroundWindow` selbst vertrauen
   (der ist unzuverlaessig).
2. **Der "Effect filters"-Dialog ist ein eigenstaendiges Top-Level-Fenster**
   (eigenes `HWND`, eigenes `GetWindowRect`), kein Kind des Hauptfensters -
   `PrintWindow` auf das Hauptfenster zeigt ihn nicht, und Klicks auf
   vermeintliche Hauptfenster-Koordinaten treffen ihn nicht. Kuenftige
   Skripte muessen das jeweils aktive Fenster (`GetForegroundWindow`) fuer
   Screenshot *und* Klick verwenden, sobald ein Dialog offen ist.

Beide Punkte gehoeren in die Werkzeugkiste, nicht ins Produkt - kein
QA-Befund gegen die Anwendung.

## Naechster Schritt

1. `Get-Process NightreignHelper` pruefen; falls noch aktiv, die Kopie
   dieses Laufs (Umlenkung `DankYeeterT-290b`) sauber beenden.
2. T-290b in einem neuen, eigenen Lauf fortsetzen: Filters-Dialog erneut
   oeffnen (oder die begonnene Sitzung uebernehmen, falls sie noch steht),
   6643000 + 7060200 als Favourite anhaken, Optimize, AK-314.1/.2/.3/.6 im
   `SuggestionBlock` und AK-314.5 im `Why`-Dialog pruefen, Hold auf Slot 2
   loesen und erneut optimieren (Gegenprobe: keine Zeile, beide Effekte in
   freien Slots), danach Regression `Why`/`Filters` an mindestens einer
   weiteren, unbeteiligten Slotkonstellation.
3. Erst danach QA-Log/Gesamturteil zu T-290b abschliessen.

## QA-Log

Keine Aenderung gegenueber dem ersten Berichtsteil (QA-283, Hook-Fehlalarm
`$istExeStart`, bereits angehaengt). Kein neuer Eintrag fuer den hier
abgebrochenen GUI-Retest - das Ergebnis steht noch aus.
