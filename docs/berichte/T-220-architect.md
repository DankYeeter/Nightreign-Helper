# T-220 — Bericht `architect`: P10-2 (Mutations-Registry) und P10-1 (`Planner`-Schnitt)

Stand 13.09.2026, HEAD `83cfed8`, Branch `docs/audit-and-advisor-design`.
Entwurf in `ARCHITECTURE.md` Themenbereich G (AD-033, AD-034, OF-34, OF-35),
Registerzeilen in `ARCHITECTURE_REGISTER.md`. Hier nur die Befunde.

## Befunde (Nebenfunde, nicht behoben)

| # | Titel | Fundstelle | Beleg |
|---|---|---|---|
| B-1 | `VariantDialog` hat keinen Aufrufer | `nrplanner/app.py:1363-1435` (73 Zeilen) | `grep -rn VariantDialog nrplanner/ tests/`: nur die Klassenzeile, 13.09.2026. Toter Code; AD-034 Schritt 1 zieht ihn mit oder streicht ihn — Entscheidung des Directors |
| B-2 | Auftrag nennt "160 Methoden" fuer `class Planner`; gezaehlt sind **94** | `docs/tasks/T-220.md:55` | `awk 'NR>=1836 && NR<5154' nrplanner/app.py \| grep -c "^    def "` = 94; die 160 zaehlen Dekoratoren und die ganze Datei |
| B-3 | `pytest tests/test_differential_track.py` dauert hier **59,9 s**, nicht 1,2 s | `docs/tasks/T-220.md:72` | 344 passed in 59.86 s, 13.09.2026; die `game_data`-Fixture laedt den Abzug |
| B-4 | `ARCHITECTURE.md:42` sagte "naechste freie AD-Nummer AD-032" — seit T-189 belegt | `ARCHITECTURE.md:42` | Nachtragsklammer gesetzt (T-220); Register fuehrt AD-035 als naechste freie |
| B-5 | Vier `app.py:`-Zeilenzitate in `UI_SPEC.md` (3242, 3883 je 1, 4079 2, 4320 3) — nur 3883 wandert mit Schritt 3 | `UI_SPEC.md` | `grep -oE "app\.py:[0-9]+" UI_SPEC.md`; fuer den `ui-ux-designer`, QA-240 fuehrt Zeilenzitate ohnehin als ungeprueft |
| B-6 | `docs/plan-restarbeiten.md` P10-2 "5 300 Zeilen" — gezaehlt 5 325 Literalzeilen (Z. 44-5368) und 96 Zeilen Logik | `docs/plan-restarbeiten.md:357-362` | `sed -n 44,5368p \| wc -l`; die Aussage haelt |

## Tragende Zahlen (alle 13.09.2026 gezaehlt)

- 289 Mutationen, 42 davon in `app.py`, 35 Dateien bewacht; 0 seit der
  Pruefphase `b33461d` hinzugekommen.
- Ertrag einer **wiederholten** Kampagne in der ganzen Geschichte: **1**
  (T-158 → QA-214, P4). Beim Eintragen/Nachfahren dagegen ≥ 7 Funde und
  laut L-008 8 von 13 Waechter-Befunden — der Vorgang bleibt, der
  Dauerbestand geht.
- 69 Commits auf `mutate.py`, 7 reine Anker-Nachzieher.
- AD-034 bricht 6 + 6 + 3 = **15** Anker; nach AD-033 Punkt 2 ist die
  Registry leer und der Waechter hat 0 Faelle.

## Nicht geprueft

- Kein Programmstart, keine volle Suite (nicht beauftragt).
- Die Zeilenschaetzung nach dem Schnitt (`Planner` ~2 620, `app.py`
  ~3 100) ist gerechnet, nicht gemessen — sie steht so markiert in AD-034.
