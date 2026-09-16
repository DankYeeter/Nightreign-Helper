STATUS: erledigt
AUFTRAG: T-044 — R-006: Kennt die Community heldengebundene Waffenklassen-Boni in Nightreign? (researcher)
GELESEN: docs/tasks/T-044.md; GOAL.md; docs/research/R-004.md; docs/research/R-005.md; docs/berichte/T-038-qa-engineer.md (Abschnitte 4.3, 4.4, 5.1–5.4, 6a–6d); docs/research/ (Bestandspruefung per Glob: R-001 bis R-005 vorhanden, R-006 frei)
GEÄNDERT: docs/research/R-006.md (neu), docs/berichte/T-044-researcher.md (neu) — kein Git, nichts anderes angefasst
ANNAHMEN: (1) Die Fan-Tabelle aus T-038 wurde tatsaechlich ohne Relikte erhoben — das ist eine Angabe des Fan-Autors, keine gepruefte Tatsache, und ich fuehre die Gegenhypothese unten. (2) Die Zitate stammen aus einem rendernden Abrufwerkzeug; ich habe woertliche Wiedergabe verlangt, kann geglaettete Formulierungen aber nicht ausschliessen. (3) `wep_type` 19/23/41 = Greataxe / Great Hammer / Colossal Weapon gemaess der Elden-Ring-Zuordnung, uebernommen aus T-038, nicht selbst geprueft.
NÄCHSTER: director
BLOCKIERT DURCH: nichts

---

# T-044 — Bericht des `researcher`

## Kurzantwort (wortgleich zu docs/research/R-006.md)

**Den Claws-Effekt kennt die Community — aber als Spieltext, nicht als Zahl.**
Zwei unabhaengige Wikis geben dieselbe Item-Beschreibung woertlich wieder:
*"Only the Revenant can make proper use of this weapon, owing to her resonance
with the spiritual. For other warriors, the claw is reduced to a blunt
instrument."* Damit ist der Effekt als **gewollte Mechanik** belegt; ein
Prozentwert steht in **keiner** Quelle, die −13 % sind ausserhalb von T-038
unbelegt. **Den Raider-Effekt kennt die Community nicht** — keine Quelle nennt
einen Angriffsbonus des Raiders auf Greataxes oder Great Hammers, und die
Community erklaert Waffenpraeferenz durchgaengig als *Moveset*, nicht als
Schaden. **Der staerkste Fremdbeleg ist trotzdem amtlich:** Patch 1.02.2
fuehrt unter der Ueberschrift "Raider" den Eintrag *"Increased the Greataxe's
and Great Hammer's ability to stagger enemies with attacks."* — genau die zwei
Waffenklassen, heldengebunden, Colossal ausdruecklich nicht dabei. Das beweist,
dass das Spiel einen Raider-gebundenen, auf genau dieses Klassenpaar
zugeschnittenen Stellhebel besitzt; es belegt **Stagger, nicht Angriffskraft**.
Sicherheit: Claws-Mechanik **hoch**, Claws-Zahl **unbelegt**; Raider-Mechanik
**Indizien, kein Beleg**, Raider-Zahl **unbelegt**.

## Die fuenf tragenden Befunde

1. **Die Cursed Claws tragen den Effekt in ihrer eigenen Item-Beschreibung** —
   *"Only the Revenant can make proper use of this weapon … For other warriors,
   the claw is reduced to a blunt instrument."* Zwei unabhaengige Wikis,
   identischer Wortlaut, also mittelbar der Spieltext selbst.
   Quellen: <https://eldenringnightreign.wiki.fextralife.com/Revenant's+Cursed+Claws>,
   <https://eldenring.wiki.gg/wiki/Nightreign:Revenant%27s_Cursed_Claws>, beide
   abgerufen 2026-09-03. **Einen Prozentwert nennt keine Quelle.**

2. **Patch 1.02.2 belegt einen Raider-gebundenen Stellhebel mit genau der
   Reichweite, die T-038 in den Zahlen sieht** — unter "Raider": *"Increased
   the Greataxe's and Great Hammer's ability to stagger enemies with attacks."*
   Beide Klassen, Colossal nicht dabei. Er belegt **Stagger, nicht
   Angriffskraft**.
   Quelle (Herausgeber): <https://en.bandainamcoent.eu/elden-ring/news/elden-ring-nightreign-patch-notes-version-1022>,
   abgerufen 2026-09-03.

3. **Ein Moveset-Bonus kann den Raider-Rest nicht erklaeren.** Eldenpedia:
   *"Unlike the other Nightfarers, the Raider favors three kinds of weapons:
   greataxes, greathammers, and colossal weapons, and has a special moveset for
   all three weapon types."* — drei Klassen, der Rest betrifft zwei. Ausserdem
   veraendert ein Moveset Motion Values, nicht den Menuewert, und gemessen
   wurde der Menuewert.
   Quelle: <https://eldenring.wiki.gg/wiki/Nightreign:Raider>, abgerufen
   2026-09-03.

4. **Die 25 Waffen sind unabhaengig bestaetigt: 11 Greataxes + 14 gelistete
   Great Hammers = 25** — genau die Menge, ueber die T-038 den Faktor misst.
   Der Effekt umfasst die beiden Klassen also vollstaendig.
   Quellen: <https://eldenringnightreign.wiki.fextralife.com/Greataxes>,
   <https://eldenringnightreign.wiki.fextralife.com/Great+Hammers>, beide
   abgerufen 2026-09-03. (Warnung: die Great-Hammer-Seite nennt in der
   Ueberschrift 15, listet 14.)

5. **Es gibt keine oeffentliche Zahlentabelle, an der sich der Raider-Rest
   nachrechnen liesse.** Fextralifes Angriffskraft-Tabellen sind fuer
   Greataxes ueber alle acht Nightfarer und alle 15 Level **leer**; zwei
   oeffentliche Rechner (relics.pro, nightreign-calculator) modellieren keinen
   helden- oder waffengebundenen Zusatzterm.
   Quellen: <https://eldenringnightreign.wiki.fextralife.com/Great+Omenkiller+Cleaver>,
   <https://relics.pro/compendium/attack-power/>, beide abgerufen 2026-09-03.

**Nebenbefund, der fuer T-042 wichtig sein duerfte:** Raider's Greataxe ist
laut Wiki eine **Colossal Weapon**, keine Greataxe — die Startwaffe des Raiders
faellt also **nicht** in die Bonusmenge. Ein Muster "Startwaffe des Besitzers"
gibt es damit auch von aussen nicht, und die beiden Faelle sind nicht zwei
Auspraegungen derselben Regel.

## Widersprueche, die offen geblieben sind

- **Relikt-Verunreinigung der Fan-Spalte ist von aussen nicht ausschliessbar.**
  Zwei klassengebundene Relikteffekte (+9 % je Waffentyp, Fextralife) ergaeben
  1,09² = **1,1881** gegen die gemessenen 1,1819 (Spanne 1,1786–1,1839) — nur
  0,5 % daneben, und die Abschneide-Rundung verzerrt das beobachtete
  Verhaeltnis systematisch nach unten. Dagegen spricht, dass die Familie
  "3+ ●● Equipped" nach R-005 *alles Getragene* hebt, die Colossal-Kontrolle
  des Raiders aber bei 1,00 liegt. Die Messung M1 entscheidet das.
- **1,18 / 1,185 / 1,1881 trennt die Lv12-Datenlage nicht sauber** (Anzeigewerte
  100–250, Abschneide-Quantisierung bis ~1 %). Ebenso bei den Claws: 0,87 und
  1/1,15 = 0,8696 sind bei Anzeigewerten 42–83 nicht unterscheidbar; **0,85
  liegt unter dem beobachteten Minimum** und ist damit unwahrscheinlich — der
  Claws-Malus ist also vermutlich *nicht* dieselbe Zahl wie die
  Startwaffen-Statusstrafe x0,85 aus R-005.
- **Skalierung der Cursed Claws: FAI S (Fextralife, Eldenpedia) gegen INT S
  (Game8).** Entscheidend fuer jeden Modellwert dieser Waffe, von aussen nicht
  aufloesbar.
- **Patch-Notes-Quellen widersprechen sich zu 1.03:** die Wiki-Sammlung fuehrt
  unter "Raider" eine Angriffsgeschwindigkeits-Aenderung, auf der
  Herstellerseite habe ich beim Abruf keinen Raider-Balanceabschnitt gefunden.
  Wahrscheinlich ein aufklappbarer Abschnitt, den ich nicht mitbekommen habe —
  ich loese es nicht auf.
- **Fextralife widerspricht sich selbst:** die Great-Hammers-Seite behauptet
  als Standardtext, alle Waffen haetten *"the same moveset … for all
  Nightfarers, without exception"*, waehrend die Raider-Seite desselben Wikis
  von einem *"custom moveset"* spricht. Wiki-Boilerplate traegt hier nichts.

## Was diese Recherche nicht beantwortet

- **Woher die beiden Effekte in den Params kommen.** Das entscheidet T-042.
  Suchhinweis aus dieser Recherche: gesucht ist eine Zeile, deren Reichweite
  Greataxe **und** Great Hammer umfasst und Colossal ausschliesst — genau die
  Reichweite, die 1.02.2 amtlich adressiert.
- **Ob der Raider-Rest ueberhaupt ein Spieleffekt ist** oder eine
  verunreinigte Fan-Spalte.
- **Ob der Claws-Malus ein flacher Multiplikator oder eine Schadensart-Aenderung
  ist.** Meine Ableitung (die Konstanz ueber sieben Helden mit sehr
  verschiedenen Attributen) sagt flach, steht aber auf fremden Zahlen.
- **r/Nightreign ist ungeprueft.** `reddit.com` ist fuer meinen Suchzugang
  gesperrt (Fehlermeldung des Suchdienstes, 2026-09-03), `site:`-Umwege
  lieferten keine Reddit-Treffer. Der im Auftrag ausdruecklich genannte Kanal
  fehlt damit. Ebenfalls nicht erreichbar: mobalytics.gg (403),
  fromsoftwiki.org (403), maxroll.gg (404 auf beide versuchten URLs). Ein
  YouTube-Test mit Zahlen wurde nicht gefunden — Nicht-Fund, kein Beleg fuer
  Abwesenheit.
- **Scholar und Undertaker sind nie geprueft worden** — weder von T-038 (nicht
  in der Fan-Quelle) noch von mir. Beide haben laut Quellen eigene
  Waffenpraeferenzen. Ob es dort dritte und vierte Faelle gibt, ist offen.

## Fuer die Entscheidung, ohne sie zu treffen

Der Unterschied zu R-004 ist der entscheidungsrelevante Punkt: der dortige
Gesamtfaktor ~0,60 kuerzt sich aus jeder Rangfolge und jedem Grenzbeitrag
heraus (GOAL F2). **Diese beiden Effekte tun das nicht** — sie verschieben die
Waffenrangfolge innerhalb eines Helden. Wer R-004 mit "Rangfolge genuegt"
abgelegt hat, kann diese beiden nicht mit derselben Begruendung ablegen. Die
drei Optionen (beide als datierte Kalibrierung fuehren / nur den besser
belegten Claws-Fall fuehren / bis T-042 nichts einrechnen) stehen mit Vor- und
Nachteilen in R-006, Abschnitt "Konsequenz fuer uns".

## Messvorschlag Level 15 mit Relikten — Kurzfassung

Vollstaendig in R-006, Abschnitt "Messvorschlag". Der tragende Kunstgriff:
**zwei Waffen nacheinander im selben, unveraenderten Zustand ablesen** — dann
kuerzen sich der globale Faktor aus R-004 **und** das Produkt aller flachen
Relikt-Angriffsraten vollstaendig heraus. Die Relikte muessen also nicht
abgelegt werden, und Level 15 ist sogar der *bessere* Messpunkt, weil die
groesseren Anzeigewerte die Abschneide-Unsicherheit unter 0,4 % druecken.

- **M1 (Raider):** Level 15, unveraenderte Relikte. Greataxe, Great Hammer und
  eine Colossal Weapon (z. B. Raider's Greataxe) nacheinander ablesen;
  q = (AR_Waffe / AR_Colossal) / (P_Waffe / P_Colossal). **q ≈ 1,18** →
  bestaetigt; **q ≈ 1,00** → widerlegt; **q ≈ 1,09** → ein klassengebundener
  Relikteffekt war doch aktiv, Lauf verwerfen. Kontrolllauf mit Wylder:
  Erwartung q ≈ 1,00 fuer alle drei.
- **M2 (Claws):** je Held Claws und eine Referenzwaffe ablesen;
  Q = (AR_Claws / AR_Ref) / (P_Claws / P_Ref). **Q_Revenant ≈ 1,00 und
  Q_andere ≈ 0,87** → bestaetigt; **beide ≈ 1,00** → kein Malus in der
  Angriffskraft; **beide ≈ 0,87** → Modellfehler auf dieser Waffe, erster
  Verdaechtiger das Skalierungsattribut.
- **Gefaehrlichste Falle, ausdruecklich:** ein "Starting armament …"-Relikt
  legt **nur den Revenant** um x0,85 tiefer (fuer ihn sind die Claws die
  Startwaffe) und kann das gesuchte Muster **umkehren**. Ebenso auszuschliessen:
  waffenklassenabhaengige Relikteffekte, bewegungsgebundene Effekte und
  angriffskrafttragende Waffen-Passiven.
- **M3 (kein Spiel, vor M2):** Skalierungsattribut und `wep_type` der Cursed
  Claws aus der eigenen Installation lesen — loest den Wiki-Widerspruch.
  Zustaendig: `qa-engineer` in T-042.
- **M4 (kein Spiel):** installierte Spielversion feststellen. 1.02.2 hat den
  Raider auf genau diesen Waffenklassen angefasst; ohne die Version hat keine
  Messung einen Geltungsbereich. Zustaendig: der Nutzer.

## Ablage

- `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\docs\research\R-006.md`
- `C:\Users\Daniel\Desktop\ClaudeCode\Nightreign-Helper\docs\berichte\T-044-researcher.md`
