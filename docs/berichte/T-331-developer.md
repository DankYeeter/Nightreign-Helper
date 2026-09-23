# T-331a — Bericht developer: Ruestungs-Negation je Nightfarer

**Urteil: vorhanden.** Die Startzeilen `CharaInitParam` 90000–90009 tragen in
`equip_Helm/equip_Armer/equip_Gaunt/equip_Leg` je vier Ruestungs-IDs; in
`EquipParamProtector` traegt **nur das Bruststueck** (`equip_Armer`,
`protectorCategory` 1) Werte ungleich 1. Helm, Handschuhe und Beine stehen bei
allen zehn in allen acht `*DamageCutRate`-Feldern auf 1,0 (30 Zeilen). Das
Produkt je Schadensart ist damit gleich dem Brustwert.

Datenstand: `regulation.bin` aus `d:\steam\steamapps\common\ELDEN RING
NIGHTREIGN\Game`, sha256 `876a3ca2…c91e0268`, 1 974 720 Bytes — derselbe Stand
wie der Testabzug (`meta.regulation_sha256`, `data_version` 10350000). Gelesen
23.09.2026.

## Tabelle

IDs: Helm / Brust / Handschuhe / Beine. Werte sind Faktoren auf eingehenden
Schaden (Produkt der vier Stuecke = Brustwert); Negation = 1 − Faktor.

| Nightfarer | Zeile | Ruestungs-IDs | neutral | slash | blow | thrust | magic | fire | thunder | dark |
|---|---|---|---|---|---|---|---|---|---|---|
| Wylder | 90000 | 5000000 / 5000100 / 5000200 / 5000300 | 0,81 | 0,80 | 0,81 | 0,80 | 0,81 | 0,81 | 0,80 | 0,83 |
| Guardian | 90001 | 5001000 / 5001100 / 5001200 / 5001300 | 0,722 | 0,7125 | 0,722 | 0,76 | 0,729 | 0,774 | 0,765 | 0,747 |
| Ironeye | 90002 | 5002000 / 5002100 / 5002200 / 5002300 | 0,81 | 0,85 | 0,86 | 0,85 | 0,81 | 0,86 | 0,80 | 0,83 |
| Duchess | 90003 | 5003000 / 5003100 / 5003200 / 5003300 | 0,81 | 0,85 | 0,86 | 0,85 | 0,72 | 0,78 | 0,78 | 0,77 |
| Raider | 90004 | 5004000 / 5004100 / 5004200 / 5004300 | 0,76 | 0,75 | 0,76 | 0,85 | 0,86 | 0,76 | 0,85 | 0,83 |
| Revenant | 90005 | 5005000 / 5005100 / 5005200 / 5005300 | 0,86 | 0,90 | 0,86 | 0,90 | 0,72 | 0,71 | 0,71 | 0,80 |
| Recluse | 90006 | 5006000 / 5006100 / 5006200 / 5006300 | 0,86 | 0,90 | 0,86 | 0,90 | 0,71 | 0,76 | 0,75 | 0,75 |
| Executor | 90007 | 5007000 / 5007100 / 5007200 / 5007300 | 0,76 | 0,75 | 0,76 | 0,80 | 0,86 | 0,81 | 0,85 | 0,78 |
| Scholar | 90008 | 5008000 / 5008100 / 5008200 / 5008300 | 0,81 | 0,83 | 0,85 | 0,80 | 0,73 | 0,75 | 0,76 | 0,91 |
| Undertaker | 90009 | 5009000 / 5009100 / 5009200 / 5009300 | 0,82 | 0,88 | 0,82 | 0,88 | 0,80 | 0,83 | 0,80 | 0,74 |

Feldnamen: `CharaInitParam.equip_Helm/equip_Armer/equip_Gaunt/equip_Leg` →
`EquipParamProtector.neutral/slash/blow/thrust/magic/fire/thunder/darkDamageCutRate`
(f32, Paramdef-Voreinstellung 1).

## Weitere Befunde

- **Garbs aendern die Werte nicht.** Von 307 `EquipParamProtector`-Zeilen haben
  78 einen Wert ungleich 1. 64 davon sind Nightfarer-Bruststuecke und tragen
  exakt eines der zehn Tupel oben, jeweils das des eigenen Nightfarers (6–8
  Zeilen je Nightfarer, z. B. Wylder 5000100, 5010100, 5020100, 5030100,
  5050100, 5060100). Die uebrigen 14 (IDs 30000–50300, 1000000–1000300) sind
  keine Nightfarer-Zeilen (Werte 0,876–0,985). Loest den Widerspruch "Garbs vs.
  Ruestung" aus R-011: beides stimmt.
- **Zeilenwahl robust.** Die Familien 50x00, 60x00, 61x00 nennen fuer alle zehn
  dieselben vier IDs wie 90000–90009.
- **Resident-SpEffects der Ruestung tragen keine Schnittrate.** Alle
  `residentSpEffectId/2/3` der 40 Zeilen zeigen auf `SpEffectParam`-Zeilen mit
  allen acht `*DamageCutRate` = 1,0.
- **Guardian faellt aus dem Raster:** vierstellige Werte (0,7125, 0,722 …), die
  anderen neun zweistellig. Passt rechnerisch zu "zweistelliger Wert × 0,95
  bzw. × 0,9" und damit zu Patch 1.03.2 ("Increased damage negation") —
  **Vermutung**, ohne Altstand nicht belegt.
- **Einheit gegengeprueft nur an der Datenform:** Paramdef-Anzeige
  "…ダメージ倍率" (Schadensfaktor), Wertebereich 0,71–0,91. Ob das
  Statusmenue genau diese Negation zeigt (etwa Wylder slash 20,0), ist nicht
  geprueft — Messpunkt ingame bleibt beim Nutzer (R-011 offene Frage 3).

## Defense (R-011 Punkt 2)

**Nicht gefunden.** `EquipParamProtector` hat `defensePhysics/Slash/Blow/
Thrust/Magic/Fire/Thunder/Dark`; in allen 40 Nightfarer-Zeilen stehen sie auf 0
(tabellenweit: 265 Zeilen alles 0, 41 nur `defenseDark` = 100, eine Zeile mit
100ern). Die Pruefung schlaegt an — sie findet die 42 Zeilen ungleich 0 — nur
nicht bei den Nightfarern. Weiter gesucht wurde nicht (kein Umweg).

## Lesegang

1. `regulation.load_params` + `param.read` mit `vendor/Paramdex/NR/Defs` (wie
   `extract.build`), keine Extraktor-Aenderung, kein Programmstart.
2. `CharaInitParam` 90000+i → vier IDs → `EquipParamProtector` acht Felder,
   dazu `defense*` und die drei `residentSpEffectId` → `SpEffectParam`.
3. Gegenprobe: alle 307 Schutzzeilen nach Werte-Tupel gruppiert (Garbs).
   Skripte: Scratchpad `T-331/lese.py`, `T-331/garbs.py`.
