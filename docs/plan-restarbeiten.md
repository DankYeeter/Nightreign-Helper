# Plan: alle offenen Punkte

Erstellt: 2026-09-03 vom Director, nach den Nutzerentscheiden zu QA-018 und
QA-061. **Auftrag des Nutzers: alle Punkte abarbeiten, nicht pausieren bis
alles fertig ist. Zwischenfragen erlaubt.**

Diese Datei ist die Reihenfolge. `qa/findings.md` und `security/findings.md`
bleiben die Wahrheit ueber den Zustand einzelner Befunde; hier steht nur, was
wann drankommt und warum.

## Die zwei Nutzerentscheide, die alles freigeben

**QA-018 — 203,4 ist richtig.** Woertlich: *"counterattack ist nur bei konter.
nicht global."* Der Buff greift nur beim Stoss-Konter; `attack_rating`
ueberschaetzt, indem es ihn als flachen Multiplikator behandelt. Die
Einschraenkung steht **nur im Beschreibungstext**, in keinem Param-Feld — die
betroffene Familie ist vollstaendig aufgezaehlt (~20 IDs, vier Namen).

**QA-061 — Lesart (a).** Woertlich: *"anforderung ist das charakter level.
sonst nichts. charaktere haben allerdings attribute und die beeinflussen wie
effektiv eine waffe auf welchem charakter ist."* Nightreign kennt **keine**
Attributsanforderungen fuer Waffen. Attribute wirken ueber die **Skalierung**,
und die ist bereits richtig. Checkbox "Meets requirements", Kachel-Dimmen,
"Requires"-Zeile und der `unmet`-Zweig sind toter Code.

---

## P1 — Die Zahlenbasis richtigstellen
*Zuerst, weil jede Rangfolge des Beraters darauf steht.*

1. **QA-018 / W6-Kern:** die vier Effektfamilien (Improved Thrusting
   Counterattack, Improved Sorceries, Improved Incantations, Improved
   Sorceries & Incantations) aus der flachen Multiplikatorschicht nehmen.
   Sie tragen kein `magicSubCategoryChange`-Feld, also braucht es eine
   benannte Liste — **und die Liste gehoert dokumentiert, nicht versteckt.**
2. **W6 vollstaendig:** `MULTIPLIERS_FOR[CANDIDATE]` setzen **plus** die
   Sortierung von `weapons.rank` auf `final_total` mit stabilem
   Zweitschluessel (Nicht-tun-Regel 29, gemessen begruendet: 584 von 7172
   Werten um 1 ULP).
3. **QA-061:** toter Code weg — Checkbox, Dimmen, "Requires"-Zeile,
   `unmet`-Zweig, der Golden-Fallname, der den Zweig verspricht (QA-019).
4. **QA-055 zweite Haelfte + AK-31 bis AK-40:** die Beschriftungen. Seit W4
   erlaubt. Dazu faellt der 60-%-Satz (der Nutzer hat ihn nie schriftlich
   belegt) — oder er kommt mit Aufbau und Datum zurueck.

## P2 — Den Fassaden-Umbau abschliessen
5. **QA-085** (vor W5): die Signalverdrahtung des Arsenal-Tabs bewachen.
6. **W5:** AD-021-Waechter scharf, `WeaponRating.total` faellt, QA-071
   (`attack_rating` ohne Produktionsleser) entscheiden, `bonus`-Kommentar auf
   die AD-024-Begruendung umschreiben.
7. **QA-086:** zwei gezielte Faelle — mehrtypige Armatur vollstaendig,
   Rarity-Filter gegen die Zaehlung.

## P3 — Der Build-Berater
*Das eigentliche Ziel. GOAL A3 bis A8.*

8. `architect`-Schritte S4 bis S11 aus AD-014 bis AD-018 und AD-023,
   UI-Spec AK-41 bis AK-62. Grenzbeitrag im Relikt-Picker, festgehaltene
   Slots, Fluechte ausgewiesen, `Optimize`-Knopf.
9. Nach P1 ist der Vorbehalt aus AD-023 **berechenbar statt pauschal** — und
   nach dem Fix zu QA-018 in den meisten Faellen **gar nicht mehr noetig**.

## P4 — Save-Lesen und Inventar
QA-032 + QA-004 (dieselbe Wurzel: stilles Ueberspringen) · QA-007
(Pruefsumme wird nie geprueft) · QA-008 · QA-010 · QA-012 (gated Effekte
umgehen die Bedingungspruefung) · QA-016 · QA-020 · QA-027 · QA-038
(doppelte Entschluesselungsschleife)

## P5 — Builds und Gefaesse
QA-054 (Build verschwindet ganz) · QA-048 + Nebenlaeufigkeit der Migration
(dasselbe Fenster) · QA-044 · QA-026 · QA-028 · QA-030 · QA-031 · QA-047

## P6 — Sicherheit
SEC-016 + SEC-018 + SEC-006-Nachtrag als **ein** Auftrag (relative Schranke
statt fester Konstante) · SEC-017 · SEC-019 + SEC-015 (Label-Fabrik plus
Waechtertest, **nicht** 90 Einzelaenderungen) · SEC-020 · SEC-011

## P7 — Waechter- und Testschulden
QA-023 (der `compute`-Waechter erkennt Schreibweisen, nicht Zugriffe) ·
QA-077 (34 Tooltips ungedeckt) · QA-037 · QA-052 + QA-053 · QA-059 ·
QA-078 · QA-087 · QA-088 · QA-066 · QA-019

## P8 — Oberflaeche
DR-004 bis DR-007 · QA-029 · QA-067 · QA-089

## P9 — Releasefaehigkeit
QA-036 (Icon-Pack: in ein temporaeres Verzeichnis bauen und umbenennen) ·
SEC-009 (zwei Punkte, < 10 Zeilen YAML) · `compliance-agent` (`auflagen`) ·
`technical-writer` · `release-manager` (`build`, `clean-room`) ·
`power-user` · **GOAL A9**

## Zurueckgestellt, mit Grund
- **`ruff`** — dritte Erwaehnung. Ohne Linter ist "Linter sauber" aus der DoD
  unpruefbar. Eine neue Abhaengigkeit zieht `researcher` und
  `compliance-agent` (`lizenzen`) nach. Entscheidung des Nutzers, wenn P1 bis
  P3 stehen.
- **C-002** — auf Anweisung des Nutzers ignoriert, nicht erneut vorlegen.

## Regeln, die fuer jeden Schritt gelten
- Jeder neue Waechter braucht seine **toetende Mutation**.
- Charakterisierungen auf der **ungerundeten** Zahl, Anzeigetext getrennt.
- Die Messstrecke unter `scripts/differential/` **benutzen, nicht neu bauen**.
- Eine Zusicherung nennt ihren **Geltungsbereich** — das ist die dominante
  Fehlerklasse dieses Projekts (QA-046, 050, 052, 062, 063, 064, 070, 073,
  082, 083, 086, 087).
