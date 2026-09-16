# T-222 — Bericht `architect`: A16, zwei Lesarten des Beraters (AD-035)

Stand 13.09.2026, HEAD `f1fc79c`. Entwurf in `ARCHITECTURE.md` Themenbereich H
(AD-035), Registerzeile in `ARCHITECTURE_REGISTER.md`. Hier nur die Befunde.

## Befunde (Nebenfunde, nicht behoben)

| # | Titel | Fundstelle | Beleg |
|---|---|---|---|
| B-1 | **Der Spielstand hat 312 Kopien, nicht 309.** `GOAL.md` A6 (Messfall), A16 (Zahlen der Director-Korrektur) und `UI_SPEC.md` Umgebung §0 / AK-187 / AK-188 rechnen mit 309 | `GOAL.md` A6, A16; `UI_SPEC.md` AK-187, AK-188 | `inventory.load(data)` gegen den echten Save, lesend, umgelenkt nach `CLAUDE.md` (Scratchpad T-222): `len(inv.relics) == 312`, 13.09.2026. Die 27 bedingten Fluchrollen stimmen weiter; die Literale 170/197/67/42/426/323 muessen beim ersten A16-Lauf nachgezaehlt werden |
| B-2 | Zwei Felder heissen "curse" und meinen Verschiedenes: `effects[id]["curse"]` (`always`/`sometimes`/`never`, 326 Ids — ob das Relikt einen Fluchplatz traegt) gegen `effects[id]["is_curse"]` (24 Ids — der Effekt ist ein Fluch) | `nrdata/extract.py:2305-2320` | AD-035 legt `is_curse` fest; ein Docstring, der das an einer Stelle sagt, fehlt — fuer den `developer` von A16 als Kommentar an `reading_defaults` |
| B-3 | 103 von 260 bedingten Buffrollen auf dem Spielstand sind ausschliesslich waffentyp-gebunden (`triggerOnWepType`/`wepTypeTrigger`/`wepTypeTriggerCount`), 16 gemischt | Spielstand, lesend | Der Best case setzt sie als erfuellt (AK-187 verlangt es); wer das nach A17 anders will, aendert die Spec, nicht den Code — als Hinweis an den App Designer, nicht als offene Frage gefuehrt |

## Tragende Zahlen (13.09.2026, Testabzug `EXTRACT_VERSION` 11 + Spielstand)

- 24 `is_curse`-Ids, 7 davon bedingt (dieselben wie `GOAL.md`); 414 bedingte
  Nicht-Fluch-Ids; `NO_SWITCH` = {7037800}.
- Spielstand: 312 Kopien, 27 bedingte Fluchrollen, 260 bedingte Buffrollen.

## Nicht geprueft

- Kein Programmstart, keine Suite. Kein `run.run` gefahren: ob die sieben
  Fluch-Ids die Rangfolge bewegen, misst der benannte Test, nicht dieser
  Bericht.
