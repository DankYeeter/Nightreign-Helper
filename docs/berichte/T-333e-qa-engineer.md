# T-333e qa-engineer — QA-298/QA-299 nachgestellt (12.10.2026)

**Urteil: CONCERNS.** Kein Fehler im Code; beide Beobachtungen folgen aus
A18/AD-036.6. Offen: Spec-Frage an den `director` (seit T-265d, 15.09.).

## Umgebung

Quellstand `05143d2`, Anwendungscode gleich `7fc3e43` (`git diff --stat
7fc3e43 HEAD -- nrplanner nrdata run.py` leer). `NIGHTREIGN_SETTINGS_ORG=
DankYeeterT-333e`, `LOCALAPPDATA`/`APPDATA` auf Scratchpad `T-333e/`,
Testabzug kopiert, `paths.cache_dir()` zurueckgelesen. Spielstand
eingefroren (sha256 `7b856a70…` gleich, mtime 11.10. 16:46), per
`remember_save`. 320 Relikte, Wylder Stufe 1, drei Slots (blau, blau,
gelb), `max_damage`, nichts gehalten, `data_version` 10350000. Weg:
`Planner` offscreen → `advisorbar.asking_from` → `run.run`. Vorschlag
deckt sich mit T-333b (Slot 3 "Grand Luminous Scene", "Strength +3 →
Attack rating +4"). Kein Fensterlauf (wiederholte nur T-333b).

## Frage 1 — QA-298: zaehlt die tote `[Undertaker]`-Wirkung?

Nein. Vorschlag 1: 90,2265 ("Attack rating 90").

| Gegenprobe | Wert | Differenz |
|---|---|---|
| ohne Slot 3 | 75,1887 | +15,0378 |
| ohne `[Undertaker] Contact with allies…` (7037300) | 90,2265 | +0,000000 |
| ohne `3+ Great Hammers` (7081300) | 75,1887 | +15,0378 |
| ohne `Stamina Recovery upon Landing Attacks` | 90,2265 | +0,000000 |

Die Wahl traegt allein 7081300. Naechstbester Kandidat Slot 3 (andere
fest, 55 Kandidaten): 82,7076 (`Grand Luminous Scene` mit `[Ironeye]…`,
Frostbite-Angriff, Poise +1). Filter `effecttext.works_for` in
`nrplanner/model.py:1207-1211` haelt; Why sagt "works only for Undertaker,
and you are Wylder." "Apply all" ohne Warnung verletzt keine Vorgabe.

## Frage 2 — QA-299: geht "3+ Hammers" in die Zahl ein?

Ja, 7081200 (Slot 1) und 7081300 (Slot 3), je x1,20:
`nrplanner/model.py:284-286` (`configure` sammelt 420 bedingte Ids, darunter
alle 82 `wepTypeTriggerCount`) → `:301-310` `advisor_defaults()` setzt sie
erfuellt → `nrplanner/advisorbar.py:525` Zusammenfuehrung → `model.py:1180`
FORCED → `:1261` nicht uebersprungen. Ohne beide Vorbelegungen 62,6573
statt 90,2265 (= 1,2²); das Undertaker-Relikt faellt dann aus der Spitze
fuer Slot 3 (Spitze 68,9230, Ironeye-Relikt).

Vorgabe: A18/AD-036.6; Bedingung im Effektnamen genuegt (Nutzer 15.09.,
UI_SPEC Nachtrag T-254a); T-325 fuehrte denselben Fall als "Vorgabe, kein
Befund". Der State-Entscheid 23.09. betrifft nur die stumme Zeile "depends
on the armaments you carry".

## Spec-Frage an den director (aus T-265d, unbeantwortet)

Die Vorbelegung zaehlt Bedingungen, die zusammen unerfuellbar sind: 3+
Hammers + 3+ Great Hammers + Bezugswaffe Wylder's Greatsword (`wep_type` 5)
= 7 Waffen, Waffenplaetze 6 (`model.py:802`).
- (a) A18 woertlich: jede bedingte Wirkung zaehlt — Verhalten richtig.
- (b) A17 sinngemaess ("waffen … sind alle in der runde RNG-basiert"): eine
  Rangfolge darf nicht auf einer Waffenannahme beruhen — Waffenzahl-
  Bedingungen nicht oder hoechstens eine vorbelegen.

Bei Entscheid "Fehler": **P2 | Major | Hoch** (Hauptpfad Wylder/Optimize,
erster Vorschlag mit einer Zahl, die im Spiel nicht erreichbar ist; 44 %
ueber dem Wert ohne Waffenzahl-Vorbelegung). Richtung fuer den
`developer`: `wepTypeTriggerCount`-Ids in `model.py:284` aus der
Vorbelegung nehmen oder je Vorschlag hoechstens eine Waffenzahl-Bedingung.

## Registerzeilen (anhaengen)

```
| QA-298 | *(Nachstellung T-333e, 12.10.2026, qa-engineer)* Tote `[Undertaker]`-Wirkung zaehlt 0,000000 (Ausschluss-Gegenprobe); Slot-3-Wahl getragen allein von `3+ Great Hammers` (+15,0378 von 90,2265), naechstbester Kandidat 82,7076; `works_for`-Filter `model.py:1207-1211` haelt. Kein Fehler; Ursache der Wahl siehe QA-299 | - | - | developer | ja - Modell am Quellstand 05143d2, eingefrorener Spielstand | geschlossen -- kein Fehler, nachgestellt | 2026-10-12 |
| QA-299 | *(Nachstellung T-333e, 12.10.2026, qa-engineer)* 7081200/7081300 gehen je x1,2 in die Zahl ein: `advisor_defaults()` (`model.py:301`, Menge `:284`, alle 82 `wepTypeTriggerCount`-Ids) -> `advisorbar.py:525` -> FORCED `model.py:1180/1261`; ohne beide 62,6573 statt 90,2265. Vorgabe A18/AD-036.6, Bedingung im Namen = Nutzerentscheid 15.09. (UI_SPEC T-254a). Spec-Frage an director (seit T-265d offen): gemeinsam unerfuellbare Waffenzahl-Bedingungen (3+3 + Bezugs-Greatsword = 7 > 6 Plaetze); bei Entscheid "Fehler" P2 Major Hoch | - | - | director | ja - Modell am Quellstand 05143d2, eingefrorener Spielstand | offen -- Spec-Entscheid director | 2026-10-12 |
```

## Explorationsprotokoll, nicht getestet, Reste

Gelesen: 7 Vorschlaege mit Why-Zeilen (alle tragen beide Hammer-Wirkungen),
Ausschluss-Gegenprobe je Wirkung, 55 Slot-3-Kandidaten mit und ohne
Waffenzahl-Vorbelegung, `build.sources`/`situational` beider Wirkungen.
Nicht getestet: Fensterlauf `-Real`, andere Nightfarer/Stufen, Wylder's
Chalice mit sechs Slots. Hinterlassen: Registry-Org `DankYeeterT-333e`
(`paths/save` auf Scratch-Kopie), Scratchpad `T-333e/` (`r1.py`, `r1.out`).
