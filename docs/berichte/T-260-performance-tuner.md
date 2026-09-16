# T-260 — Picker öffnen und Arsenal-Neuberechnung (performance-tuner)

```
STATUS: erledigt (Optimierung 1), Optimierung 2 als Spec an developer
AUFTRAG: T-260 - Messszenario Picker oeffnen und Arsenal-Neuberechnung
  (performance-tuner)
GELESEN: qa/findings.md (QA-258, Zeile ~318); nrplanner/relicpicker.py (ganz);
  nrplanner/weapons.py (rate, rank, evaluate_curve via model.py); nrplanner/
  damage.py (rank_candidates, _rate, _scaled, _other_hand, _answer);
  nrplanner/arsenaltab.py (recalculate); tests/test_relic_picker_advisor.py
  (ganz, 1905 Zeilen); tests/test_relic_picker_geometry.py; scripts/
  measure_picker_cards.py; scripts/measure_advisor_picker.py; CLAUDE.md
GEÄNDERT: nrplanner/relicpicker.py (`RelicPicker._card_cache`, siehe Diff);
  tests/test_relic_picker_advisor.py (drei neue Waechter); docs/perf/
  baselines.md (Abschnitt S11-L neu); docs/berichte/T-260-performance-tuner.md
  (diese Datei)
ANNAHMEN: (1) Das im Auftrag genannte Zielszenario ("Picker oeffnen") ist
  QA-258s eigener Fall -- weisser Slot, ~206-211 Kandidaten -- und nicht ein
  gefaerbter Slot mit deutlich weniger Karten; beide Engpaesse (Kartenbau,
  weapons.rate) treffen jeden Slot anteilig, aber nur der weisse liegt ueber
  der 100-ms-Untergrenze. (2) "ohne Verhaltensaenderung" schliesst eine
  Umstrukturierung von `weapons.rate`s Innerem (bit-genaue ULP-Historie,
  AD-019/AD-024) aus dem eigenmaechtigen Zugriff dieser Rolle aus -- das ist
  unten als Spec an den `developer` begruendet, nicht als eigene Optimierung
  umgesetzt.
NÄCHSTER: director (Freigabe Optimierung 2 an developer), developer (Spec
  Abschnitt 5)
BLOCKIERT DURCH: nichts fuer Optimierung 1 (erledigt, verifiziert). Optimierung
  2 wartet auf eine Entscheidung des director, ob die Spec an developer geht.
```

---

## 1. Scope, Messszenario, Umgebung

Zwei vom `director` benannte Engpässe, beide am HEAD `468f65c` gemessen,
niemand parallel am Baum (`git status` vor und nach jedem Messlauf geprüft).

**Szenario A — Picker öffnen (QA-258).** `Executor`, `Deep of Night` an,
weißer Slot (Farbe 4), 211 Kandidaten. Reales Fenster
(`QT_QPA_PLATFORM=windows`), frisches `Planner`-Fenster je Wiederholung
(n=5), damit der Cache des Picker-Tracks keinen zweiten Bau überspringt.
Redirection: `NIGHTREIGN_SETTINGS_ORG=DankYeeterT-260`, eigenes
`LOCALAPPDATA`/`APPDATA`, Testabzug kopiert (841 Dateien, `EXTRACT_VERSION`
11, unverändert gültig).

**Szenario B — Arsenal-Neuberechnung (T-254b-Nebenfund).** `Wylder`, Stufe
15, kein Relikt, `damage.rank_candidates` bei `+4` — der Aufruf, den
`ArsenalTab.recalculate()` synchron im Hauptthread bei jeder
Stufen-/Helden-/Relikt-Änderung macht.

**Umgebung beider Messungen:** AMD Ryzen 9 5900X, 12 Kerne (dieselbe
Maschine wie QA-258), Energieplan `Balanced`, Windows 11 10.0.26200, Python
3.12.10 (`.venv`). Rechenlastprobe (3 Mio. `x += i*i`): Median 214,9 ms
(Spanne 210,8–216,1 ms, n=5) — schneller als die in `docs/perf/baselines.md`
hinterlegte Ryzen-7-5800H-Reihe (1102 MHz Quiet Mode); beide Szenarien liegen
deshalb in einem eigenen Abschnitt der Baseline-Datei (S11-L) statt in einer
bestehenden Zeile.

Messwerkzeuge liegen außerhalb des Produktivbaums im Scratchpad
(`measure_picker_open2.py`, `measure_rank_candidates.py`,
`profile_rank_candidates.py`) und werden nicht ausgeliefert.

---

## 2. Baseline und Signifikanzschwelle

**Szenario A (Picker, weißer Slot, n=5):**

| Messung | Median | Spanne | 2s/Median |
|---|---|---|---|
| `_refresh()` #1 (wartender Bau) | 1151,0 ms | 1093,4–1174,0 ms | 3,3 % |
| `_refresh()` #2 (beantworteter Bau) | 1298,8 ms | 1222,5–1313,6 ms | 2,9 % |
| **Summe je Öffnung** | **2438,2 ms** | 2315,9–2466,7 ms | **4,9 %** |

Schwelle für Szenario A: **5 %** (stabile Umgebung, kein JIT/Cloud-Faktor).
Absolute Untergrenze: A6-Geist, Hauptthread < 50 ms je Block — beide Blöcke
liegen um mehr als das 20-fache darüber.

**Szenario B (Arsenal, `rank_candidates`, n=7):**

| Messung | Median | Spanne | 2s/Median |
|---|---|---|---|
| `damage.rank_candidates` | 88,4 ms | 73,9–92,9 ms | 18,8 % |

Schwelle für Szenario B: **19 %** (breitere Streuung als Szenario A —
1793 Einzelaufrufe je Lauf, empfindlicher gegen Scheduler-Jitter). Absolute
Untergrenze: Backend-p50/Interaktionsantwort 100 ms — der Median selbst
liegt knapp darunter, aber **jeder** Aufruf lief auf dem Hauptthread
(`arsenaltab.recalculate`, keine Nebenläufigkeit), und die Spitze (92,9 ms)
ist knapp am Budget.

---

## 3. Gefundene Engpässe, priorisiert

| # | Ursache | Fundort | Aufwand | Wirkung |
|---|---|---|---|---|
| 1 | `RelicPicker._refresh()` baut alle `RelicCard`-Widgets neu, zweimal je Öffnung (wartend + beantwortet) | `nrplanner/relicpicker.py:1556-1574` | niedrig (Cache, keine Schnittstellenänderung) | hoch: -43,1 % Gesamtzeit je Öffnung |
| 2 | `weapons.rate` wird je zweihandfähiger Nahkampfwaffe zweimal gerufen (1H über `weapons.rank`, 2H über `damage._other_hand`), identische `base`/`bonus`-Zwischenwerte doppelt berechnet | `nrplanner/weapons.py:383-527`, `nrplanner/damage.py:665-683,716-784` | mittel-hoch (Umbau einer ULP-sensiblen Kernfunktion) | mittel: profiliert ~29 % von `rank_candidates` |

---

## 4. Durchgeführte Optimierung: Picker-Kartenbau (Szenario A)

**Ursache.** Jede Öffnung des Pickers fragt die Advisor-Rangfolge einmal,
zeichnet aber zweimal: sofort (wartend, nur für die AK-51-Größenmessung) und
noch einmal, wenn die Antwort eintrifft (`_the_answer_arrived`). Beide
Aufrufe von `_refresh()` bauten dieselben 211 `RelicCard`-Widgets aus
denselben Relikt-Objekten neu — exakt die "zwei Blockaden" aus QA-258.

**Änderung.** `nrplanner/relicpicker.py`, Klasse `RelicPicker`:
`self._card_cache: dict[int, RelicCard]` (Schlüssel `id(item)`) hält eine
Karte über beide Aufrufe einer Öffnung hinweg; `_refresh()` fragt den Cache
ab, bevor `_card_for` neu gerufen wird. Zwei gezielte Invalidierungen:
`_open_favourites` wirft nur die eine umgeschaltete Karte,
`_the_stock_was_replaced` den ganzen Cache (der Spielstand hinter den
`id()`-Schlüsseln ist gegangen, die Methode beginnt die Öffnung ohnehin "als
wäre sie jetzt geöffnet worden"). Keine öffentliche Schnittstelle berührt,
keine Signatur geändert.

**Warum das Verhalten gleich bleibt:** `MarkedLine` (das Häkchen je
Effektzeile) zeichnet über das `changed`-Signal der `EffectFilters` live
nach, unabhängig davon, welcher `_refresh()`-Aufruf die Karte gebaut hat —
eine wiederverwendete Karte zeigt denselben Stand wie eine neu gebaute. Die
Auswahl (`current`) kann sich vor dem ersten `_pick()` nicht ändern (das
schließt den Dialog). Die Favoriten-Sterne sind der einzige am Konstruktor
gebundene, veränderliche Zustand — dafür die gezielte Invalidierung oben.

| Metrik | Vorher | Nachher | Delta | Messmethode |
|---|---|---|---|---|
| `_refresh()` #1 (wartend) p50 | 1151,0 ms | 1033,7 ms | -10,2 % | Monkeypatch-Stoppuhr um `_refresh`, n=5, `QT_QPA_PLATFORM=windows` |
| `_refresh()` #2 (beantwortet) p50 | 1298,8 ms | 368,8 ms | **-71,6 %** | dito |
| Summe je Öffnung p50 | 2438,2 ms | 1386,2 ms | **-43,1 %** | dito |
| `_card_for`-Aufrufe je Öffnung | 422 (211×2) | 211 | -50 % | Aufrufzähler (`test_the_answer_arriving_does_not_rebuild_the_waiting_paints_cards`) |
| Peak Memory | nicht gemessen | nicht gemessen | — | — |
| DB-Queries | entfällt | entfällt | — | — |
| Bundle / Payload | unverändert | unverändert | — | — |

*Peak Memory nicht gemessen: der Cache hält zusätzlich bis zu 211
`RelicCard`-Objekte je offenem Dialog (vorher: kurzzeitig dieselbe Zahl
während des wartenden Baus, dann verworfen) — ein Trade-off (siehe unten),
dessen absolute Größe hier nicht beziffert ist.*

**Risiko: niedrig.** Interne Cache-Ergänzung einer privaten Klasse, keine
Schnittstellenänderung, keine neue Nebenläufigkeit (der Cache lebt nur auf
dem Hauptthread, dieselbe Reihenfolge-Garantie wie vorher).

**Trade-off:** mehr Speicher (bis zu 211 zusätzliche `QWidget`-Objekte,
solange der Dialog offen ist) gegen deutlich weniger Hauptthread-Zeit. Die
Karten werden mit dem Dialog freigegeben (`self._card_cache` ist eine
Instanzvariable, keine Modul- oder Fensterebene) — keine Cache-Invalidierung
über die Öffnung hinaus nötig.

**Verifikation.** Drei neue Waechter in `tests/test_relic_picker_advisor.py`:
`test_the_answer_arriving_does_not_rebuild_the_waiting_paints_cards`
(Aufrufzähler, keine Zeitschranke),
`test_the_cards_shown_after_the_answer_are_the_ones_built_while_waiting`
(Objektidentität), `test_a_favourite_toggle_rebuilds_only_that_one_card`
(gezielte Invalidierung über den echten `_open_favourites`-Pfad, `exec`
gestubbt statt eines echten Modals). Volle Nachbarschaft grün: `pytest
tests/test_relic_picker_advisor.py tests/test_relic_picker_geometry.py
tests/test_picker_track_guards.py tests/test_search.py
tests/test_custom_relic.py tests/test_relic_restore.py` → **137 passed**
(156,3 s, ohne `-n`).

---

## 5. Nicht umgesetzt: `weapons.rate` zweimal je Waffe (Szenario B) — Spec für `developer`

**Messung.** `damage.rank_candidates` (n=7): Median 88,4 ms (Spanne
73,9–92,9 ms). `cProfile` über 5 Läufe: `weapons.rate` 17 645 Aufrufe,
342 ms kumulativ von 585 ms Gesamt (58 %); davon 8 960 Aufrufe (51 %) über
`damage._other_hand` für die Zweihand-Bewertung. `evaluate_curve` allein
trägt nur 9 % bei — die Kurvenauswertung ist **nicht** der dominante Anteil,
die Dopplung liegt in `rate()`s ganzem Inneren (rund 62 `dict.get`-Aufrufe
je Aufruf, 1,1 Mio. insgesamt).

**Ursache.** `_other_hand` ruft `weapons.rate(weapon, attributes, data,
tier, nightfarer, two_handed=True)` für jede zweihandfähige Waffe (1736 von
1793 im Datensatz) zusätzlich zu dem 1H-Aufruf, den `weapons.rank` intern
schon macht. Beide Aufrufe bekommen dieselben `weapon`/`attributes`/`data`
und berechnen `base` und `bonus` je Schadensart bitgleich noch einmal — nur
`display_rate` (Kalibrierung × `hand.factor`) unterscheidet die beiden
Hände. `base`/`bonus` einmal zu berechnen und für beide Hände
wiederzuverwenden wäre bitgenau identisch zum heutigen Ergebnis (deterministische
Multiplikation, keine geänderte Klammerung — beide Endausdrücke bleiben
`base * display_rate` bzw. `base * bonus * display_rate`, nur `base`/`bonus`
kommen aus einer gemeinsamen Berechnung statt zweien).

**Warum nicht selbst umgesetzt.** `weapons.rate` ist der am genauesten
dokumentierte Code dieses Projekts in Sachen Fließkomma-Verhalten
(AD-019/AD-024, "544 kamen 2 ULP daneben", explizite Klammerungsbegründung
in jeder Zeile der Schadensschleife). Ein Umbau — und sei er bitgenau
gedacht — ist eine strukturelle Änderung an einer Kernfunktion mit
dokumentierter Historie von genau dieser Art Fehler; das ist eine
Entscheidung für `architect`/`developer`, nicht ein einseitiger Eingriff
dieser Rolle (Rollenregel: strukturelle Änderungen gehen als Spec weiter).

**Spec (Vorschlag, keine Umsetzung):**
1. In `nrplanner/weapons.py`: den Teil von `rate()` bis einschließlich der
   `bonus`-Schleife (Zeilen ~407–488, vor der `display_rate`-Anwendung) in
   eine private Funktion extrahieren, die `(applied, catalyst_scaling,
   per_damage: dict[str, tuple[base, bonus]])` zurückgibt. `rate()` selbst
   ruft sie einmal und bleibt sonst unverändert (gleiche Signatur, gleiches
   Ergebnis, golden-file-geprüft).
2. Eine neue, private Funktion (z. B. `weapons._rate_pair`) ruft diese
   Extraktion einmal und baut daraus sowohl die 1H- als auch (wenn
   `can_two_hand`) die 2H-`WeaponRating` — mit genau denselben Endausdrücken
   wie `rate()` heute, nur ohne die gemeinsame Vorarbeit doppelt zu tun.
3. `damage._rate`/`damage.rank_candidates` rufen `_rate_pair` statt
   `_scaled` + `_other_hand` mit zwei separaten `weapons.rate`-Aufrufen.
   Öffentliche Signaturen von `damage.equipped`, `damage.candidate`,
   `damage.rank_candidates`, `weapons.rate`, `weapons.rank` bleiben
   unverändert.
4. Test: ein Golden-Vergleich über den **gesamten** Datensatz (nicht nur die
   bestehenden Golden-Fälle), der `_rate_pair`s Ausgabe hex-genau
   (`float.hex()`) gegen zwei unabhängige `weapons.rate`-Aufrufe prüft — das
   deckt mehr Fälle ab, als `test_weapon_damage_golden.py` heute hält, und
   ist die Absicherung, die eine ULP-Änderung an dieser Stelle bräuchte.

**Erwarteter Gewinn (nicht gemessen, aus dem Profil abgeleitet):** rund
50 % der 51 % Anteil, den `_other_hand`-Aufrufe an `rate()`s Gesamtzeit
tragen — grob 25-30 ms von 88,4 ms Median, aber **erst nach Umsetzung zu
verifizieren**, nicht als Zusage zu lesen.

**Bedingung für Reaktivierung:** sobald `developer` diesen Umbau umsetzt und
die golden-file-Absicherung steht, ist ein Nachmess-Lauf gegen S11-L (Szenario
B, sobald dort eine Baseline-Zeile steht) fällig.

---

## 6. Verworfene Optimierungen

**`evaluate_curve`-Memoisierung allein (ohne den Umbau aus Abschnitt 5).**
Verworfen: `evaluate_curve` trägt nur 9 % der `rank_candidates`-Zeit (54 von
585 ms über 5 Läufe), die Dopplung darin wäre nur die Hälfte davon — unter
5 % Gesamtwirkung, an der Grenze der Signifikanzschwelle (19 %) für dieses
Szenario und nicht der Mühe eines Cache-Eingriffs in eine reine, aber
unhashbare (`curve: dict`) Funktionssignatur wert. **Lohnt sich erneut**,
falls Abschnitt 5 umgesetzt wird und die verbleibende Zeit dann so weit
sinkt, dass 9 % wieder ins Gewicht fallen.

---

## 7. Fehlerfunde

Keine. Das Profiling deckte keinen neuen Fehler auf (nur die bereits
gemeldeten QA-258/T-254b-Befunde, die dieser Auftrag bearbeitet hat).

---

## 8. Baseline-Ablage

`docs/perf/baselines.md`, Abschnitt **S11-L** (neu): Vorher/Nachher-Zeilen
für Szenario A, Budget-Zeile auf die neue Summe (1386,2 ms) gesetzt. Szenario
B hat noch keine Baseline-Zeile (nur der Vorher-Wert aus diesem Bericht) —
die legt der nächste Lauf an, sobald Abschnitt 5 umgesetzt ist, damit vorher
und nachher in derselben Tabelle stehen.
