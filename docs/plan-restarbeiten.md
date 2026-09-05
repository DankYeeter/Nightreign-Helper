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

**Zuschnitt geaendert (Nutzer, 05.09.2026): ein Auftrag statt vier.** Der
Nutzer hat gefragt, ob die Registry-Randfaelle effizienter gehen. Sie gehen:
**QA-044, QA-048 und QA-054 sind nicht drei Fehler, sondern einer.**

Wurzel: der Speicher adressiert einen Build ueber einen **aus dem Namen
abgeleiteten Schluessel**, und die Ableitung ist nicht umkehrbar — deshalb
wird ein Build gelistet, den `load_build`/`delete_build` nicht finden
(QA-044), oder null mal gelistet, obwohl er in der Registry steht (QA-054).
Dazu schreibt die Migration ihren Marker (`__schema` = 3), **bevor** die
Bewegung fertig ist; danach heilt nichts mehr nach (QA-048).

**Ein Fix:** Builds ueber eine gespeicherte Kennung adressieren statt ueber
den abgeleiteten Namen, und den Migrationsmarker erst setzen, wenn die
Bewegung durch ist — oder ihn pruefen statt ihm zu glauben. **Ein Waechter**,
der alle drei kaputten Speicher synthetisch baut und zeigt, dass sie danach
listbar, ladbar und loeschbar sind. QA-047 (Testrueckstaende in
`HKCU\Software\DankYeeterTests`, nur Entwicklermaschinen) laeuft als
Dreizeiler mit.

Getrennt davon, unveraendert: QA-026, QA-028, QA-030, QA-031 (Deep-Slots,
`custom_item` ueber Gefaesswechsel, doppelte Fehlermeldung).

## P6 — Sicherheit

**Eingedampft (Nutzer, 05.09.2026): von sieben Punkten auf zwei.** Woertlich:
*"sicherheit kann weg, passt"* — als Zustimmung zum Director-Vorschlag, die
theoretischen Faelle zu streichen und die zwei mit echter Wirkung zu behalten.

**Bleibt:**
- **SEC-009** — Lieferkette der veroeffentlichten EXE (Action-Pin auf
  Commit-SHA, SHA-256-Pruefsumme). **Sperrt das Release.** Grund fuer den
  Verbleib: der Befund betrifft nicht den Nutzer, sondern jeden, der die EXE
  herunterlaedt.
- **SEC-019 + SEC-015** — als **eine** Label-Fabrik plus Waechtertest, nicht
  als 90 Einzelaenderungen. Schliesst eine Klasse zu geringen Kosten.

**Gestrichen, dokumentiert, nicht erneut vorlegen:** SEC-011, SEC-016,
SEC-017, SEC-018, SEC-020. Begruendung: jeder dieser Faelle setzt entweder
eine boesartige Spielinstallation voraus — die der Nutzer am 02.09.2026
ausdruecklich als vertrauenswuerdig eingestuft hat — oder einen Angreifer,
der das Benutzerkonto ohnehin schon kontrolliert. In beiden Faellen ist der
Befund nicht mehr das Problem.

## P7 — Waechter- und Testschulden

**Vollstaendig bestaetigt (Nutzer, 05.09.2026):** *"waechterschulden sind
sinnvoll fuer weitere anpassungen. durchfuehren."* Der Director hatte
vorgeschlagen, die Haelfte zu streichen; der Nutzer hat widersprochen, und
die Begruendung traegt — jede noch kommende Aenderung (S7 bis S11, der
Tab-Audit, P4/P5) laeuft ueber genau diese Waechter.

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

## Regel fuer den Director selbst (L-010)

Aus der Retrospektive zu Zyklus 12/13, **sieben Belege, alle beim Director**:
ein Auftrag prueft, was herauskommen soll, aber nicht, was die Rolle **lesen,
benutzen und uebergeben** kann. Drei Zeilen vor jedem Dispatch:

1. **Medium** — Rollen ohne Dateizugriff bekommen ihren Auftrag im
   **Nachrichtentext**, nicht als Pfad. Der power-user darf docs/tasks/ per
   Definition nicht oeffnen; ein Auftrag dort ist keiner.
2. **Werkzeug** — hat die Rolle die Werkzeuge, die das Abnahmekriterium
   verlangt? Fehlen sie, ist der Lauf **kein Nachweis**, und der Auftrag
   wartet, statt ein Ergebnis zu erzeugen, das nichts belegt.
3. **Quelle** — Berichte von Rollen ohne Write-Recht liegen ab, **bevor** die
   abhaengige Rolle startet. Und docs/state.md sagt "geschrieben" erst
   **danach**, nicht vorher.

## Nummernkreise der Regeln — Achtung, zwei Saetze

docs/lessons.md fuehrt projekteigene Regeln, die Agentendefinitionen fuehren
teamweite — **beide unter L-001 aufwaerts, mit verschiedenen Inhalten.** Jedes
L-Zitat aus Zyklus 12/13 meinte den **teamweiten** Satz; die Projektnummern
werden seit T-023 nicht mehr zitiert, und die einzige rein projekteigene
Regel stand dadurch in einer Datei, die niemand mehr liest — und war
gebrochen.

**Ab jetzt:** projekteigene Regeln stehen **hier** und tragen das Praefix
**NH-**. docs/lessons.md bleibt Verlauf. L-008 bis L-011 sind teamweite
Nummern aus der Retrospektive.

**NH-001 (war L-004): jede nicht-triviale Arbeit bekommt eine T-Nummer und
eine Auftragsdatei.** In Zyklus 13 zweimal gebrochen (T-060 und T-061 liefen
ohne Datei, dazu zwei Nachtraege per Nachricht).

## Zurueckgestellt, mit Grund
- **`ruff`** — dritte Erwaehnung. Ohne Linter ist "Linter sauber" aus der DoD
  unpruefbar. Eine neue Abhaengigkeit zieht `researcher` und
  `compliance-agent` (`lizenzen`) nach. Entscheidung des Nutzers, wenn P1 bis
  P3 stehen.
- **C-002** — auf Anweisung des Nutzers ignoriert, nicht erneut vorlegen.

## Regeln, die fuer jeden Schritt gelten
- **Jeder neue Waechter braucht seine toetende Mutation — und drei
  Bedingungen** (L-008, 13 gezaehlte Faelle in Zyklus 12/13): sie zaehlt erst
  als toetend, wenn sie im **Standardlauf** rot wird; der Fall bezieht seine
  Erwartung **nicht** aus der Stelle, die er bewacht; und eine **ueberlebende**
  Mutation wird als Befund berichtet, nicht stillschweigend nachgebessert.
  Verlangt keine zusaetzlichen Mutationen, nur schaerfere.
- **Jede Oberflaechenzahl nennt ihre Messumgebung** (L-009, sechs gezaehlte
  Fallen): Plattform, Stil, Skalierung, physisch oder logisch. Und jede
  Messung prueft, dass sie ihren eigenen Namen erreicht hat — ein Testfall
  "[833]", der in Wahrheit 964 misst, ist keine Messung.
- Charakterisierungen auf der **ungerundeten** Zahl, Anzeigetext getrennt.
- Die Messstrecke unter `scripts/differential/` **benutzen, nicht neu bauen**.
- Eine Zusicherung nennt ihren **Geltungsbereich** — das ist die dominante
  Fehlerklasse dieses Projekts (QA-046, 050, 052, 062, 063, 064, 070, 073,
  082, 083, 086, 087).
