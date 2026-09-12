# T-184 — UI_SPEC konsolidiert (ui-ux-designer)

```
STATUS: erledigt
AUFTRAG: T-184 — UI_SPEC konsolidieren, das Register steht schon
GELESEN: ~/.claude/agents/_rahmen.md · docs/tasks/T-184.md · docs/tasks/T-181.md ·
         CLAUDE.md · UI_SPEC.md (Altstand, 9639 Zeilen) · UI_SPEC_REGISTER.md ·
         nrplanner/app.py Z2000-2062 (Tab-Namen, fuer die Einsortierung von
         AK-64 bis AK-66)
GEAENDERT: UI_SPEC.md (neu aufgebaut, 3392 Zeilen) ·
           docs/archiv/ui-spec-verlauf.md (neu, 9708 Zeilen) ·
           UI_SPEC_REGISTER.md (ein fehlender Abschnitt nachgetragen, 342 -> 361) ·
           docs/berichte/T-184-ui-ux-designer.md (diese Datei).
           Nichts committet, nichts gestaged.
ANNAHMEN: Die Zuordnung der 255 Kriterien auf sieben Oberflaechenbereiche ist
          meine Ordnung, nicht die des Registers. Grundlage sind die
          Abschnittsthemen A01-A33 und die Ueberschriften der Quellabschnitte;
          kein Kriterium wurde dabei umformuliert, verschoben oder gestrichen.
NAECHSTER: director
BLOCKIERT DURCH: nichts. Offen bleibt eine Entscheidung des App Designers
                 (drei widerspruechliche Faelle, unten).
```

## Urteil

Beide Lieferungen stehen. `UI_SPEC.md` ist von einer chronologischen
Auftragsfolge in ein nach Oberflaechenbereich geordnetes Nachschlagewerk
umgebaut, der vollstaendige Verlauf liegt unveraendert daneben. Alle sieben
Bereiche sind fertig; keiner fehlt.

## Was gebaut wurde

**Schritt 1 — der Verlauf.** `docs/archiv/ui-spec-verlauf.md`, 9708 Zeilen.
Kopiert mit der Shell (`cp`), nicht durch ein Schreibwerkzeug. Der Kopf
(69 Zeilen) traegt ein Inhaltsverzeichnis mit allen 33 Abschnitten, je mit
Zeilenbereich im Altstand **und** in der neuen Datei, sowie dem Versatz `+69`.
Der Koerper ab Zeile 70 ist **bytegleich** zum Altstand (`diff -q`, zweimal
geprueft — direkt nach dem Kopieren und nach der gesamten Arbeit).

**Schritt 2 — `UI_SPEC.md`.** 3392 Zeilen, Bereich fuer Bereich angehaengt.
Nach jedem Bereich war die Datei in sich lesbar; ein Abbruch haette den
fertigen Teil stehen gelassen.

| Bereich | Inhalt | Kriterien | Zeilen |
|---|---|---|---|
| 1 | Erststart: Spielordner und Spielstand waehlen | AK-106..132, 230..242, 246..249, 253..255 | 521 |
| 2 | Der Spielstand wird im Hintergrund gelesen | AK-220..229, 243..245, 250..252 | 336 |
| 3 | Build planner: die Advisor bar | AK-01..30 | 266 |
| 4 | Build planner: Slotkarten, Halte-Funktion, `Optimize` | AK-31..40, 54..62 | 200 |
| 5 | Der Relic Picker | AK-41..53, 195..219 | 619 |
| 6 | Die Sprache der Zahlen | AK-63, 67, 133..194 | 841 |
| 7 | Die sechs Inhalts-Tabs | AK-64..66, 68..105 | 504 |

Dazu 105 Zeilen Kopf: wie die Datei zu lesen ist, die Bereichstabelle, und die
drei widerspruechlichen Faelle.

## Gemessene Abnahme

| Kriterium aus dem Auftrag | Ergebnis |
|---|---|
| Zeilen zusammen nicht < 9639 | **13 100** (3392 + 9708) |
| keine Nachtrags-Ueberschriften mehr (`grep -cE '^## (Nachtrag|Director-Korrektur)'`) | **0** |
| alle 255 AK-IDs vorhanden (`grep -cE '^#### AK-[0-9]+$'`) | **255**, Dubletten **0**, `comm` gegen das Register **leer** |
| Bereiche fertig / fehlend | **7 von 7 fertig**, keiner fehlt |
| `widerspruechlich`-Faelle gefuehrt | **3** (AK-05, AK-160, AK-194) |

**Woertlichkeit, maschinell geprueft.** Fuer jeden der 255 Kriteriumstexte
wurde der aus dem Altstand gezogene Block normalisiert (Weissraum kollabiert)
und in der neuen `UI_SPEC.md` gesucht: **0 fehlende Bloecke**. Geaendert wurde
ausschliesslich die Listeneinrueckung (aus `- **AK-01** …` wurde
`**AK-01** …`, Fortsetzungszeilen um zwei Leerzeichen ausgerueckt) — kein
Wort, keine Zahl, keine Tabelle.

**Rot-vorher fuer diese Pruefung.** Die erste Fassung meiner Blockregel brach
an jeder Zeile ab, die in Spalte 0 mit `**` beginnt. Gemessen: **41 von 288**
Bloecken waeren damit mitten im Satz abgeschnitten worden (belegt an AK-107,
dessen Schlusszeile `**kein** Panel.` verlorenging — der Fehler stand bereits
in der ersten geschriebenen Fassung von Bereich 1 und wurde beim Gegenlesen
gefunden). Die zweite Fassung — ein Aufzaehlungspunkt endet an der naechsten
Zeile in Spalte 0, ein Absatz an einer Leerzeile vor einer Marke — bringt
**2 von 288** Verdachtsfaelle, beide geprueft und korrekt (dort folgt
tatsaechlich ein neuer, AK-fremder Aufzaehlungspunkt).

**Positivkontrollen.** (1) Derselbe Block plus einem erfundenen Satz wird
**nicht** gefunden (False). (2) Eine Verlaufs-Ueberschrift, die bewusst nicht
nach `UI_SPEC.md` gehoert (`Streichvorschlaege je Tab`), wird **nicht**
gefunden (False). Die Pruefung misst also die Sache, nicht sich selbst.

**Kein Server, kein Programmstart, kein Bau.** Reine Dokumentenarbeit; es ist
nichts zu beenden. Arbeitsdateien liegen ausschliesslich unter
`…/scratchpad/T-184/`.

## Befunde

**1. Die Zahl 255 ist unabhaengig bestaetigt — die Korrektur im Auftrag
stimmt.** Eigene Messung am Altstand: `grep -oE '\bAK-[0-9]+'` liefert 256,
die zweite, unabhaengig formulierte Maske `\bAK-[0-9]{2,3}\b` liefert
**255**. Die ueberzaehlige Zeichenkette ist `AK-2` in Zeile 9461, Teil des
Suchmusters `grep -rn "AK-2[45][0-9]"`. Der Nummernkreis laeuft von 1 bis 255
**ohne Luecke** (nachgerechnet, Ergebnis `fehlend: []`).

**2. Das Register hatte eine haengende Verweisung — nachgetragen.** Die Zeile
zu AK-05 verweist auf einen Abschnitt `Widerspruechliche Faelle`, den es in
`UI_SPEC_REGISTER.md` nicht gab: der T-181-Lauf ist unmittelbar nach der
Tabelle gestorben. Ich habe den Abschnitt ergaenzt
(`UI_SPEC_REGISTER.md` ab Zeile 344). Er **entscheidet nichts** — er benennt
die drei Faelle und zeigt auf die ausfuehrliche Darstellung in `UI_SPEC.md`.
Das ist die einzige Aenderung am Register; die 255 Tabellenzeilen sind
unberuehrt (nachgezaehlt: 255, Dubletten 0).

**3. Neun Fundstellen zeigen auf einen ganzen Abschnitt, nicht auf einen
Absatz — fuer sechs AK-IDs steht der geltende Wortlaut deshalb nicht in
`UI_SPEC.md`.** Betroffen: AK-05 (A14), AK-34 (A03, A06), AK-47 (A04, A05),
AK-82 (A13), AK-118 (A28 Z8004, A29), AK-244 (A31). An diesen Stellen steht
statt des Textes ein praeziser Zeiger mit Abschnittstitel, Auftrag, Datum und
Zeilenbereich in der Verlaufsdatei. **Warum nicht uebernommen:** die
betroffenen Abschnitte sind 24 bis 232 Zeilen lang (A29 allein 232); sie
vollstaendig einzuruecken haette den Verlauf zurueckgeholt, den dieser Auftrag
abtrennen soll. Je Fall nur den *entscheidenden* Absatz zu waehlen, waere eine
Auswahl — und damit eine Entscheidung, die mir der Auftrag verbietet. **Das
ist ein Befund fuer den Director**, kein Mangel des Registers: soll der
Wortlaut auch dort stehen, braucht es einen Folgeauftrag, der je Fall
benennt, welcher Absatz der bindende ist.

**4. 17 Fundstellen liegen 1 bis 9 Zeilen neben dem Absatzanfang.** Das
Register nennt die Zeile, in der die AK-Nummer im Fliesstext faellt; der
Absatz beginnt ein paar Zeilen frueher. Abgedruckt ist der ganze Absatz, und
die Stelle traegt den Vermerk `<sub>Fundstelle sinngemaess …</sub>` mit beiden
Zeilennummern. Kein Wortlaut ist davon betroffen, nur die Zeilenangabe.
Betroffen: AK-18, AK-21, AK-50, AK-63, AK-140, AK-147, AK-161, AK-169,
AK-195, AK-196, AK-199 (zweimal), AK-200, AK-203, AK-223, AK-224, AK-232.

**5. AK-28 ist zurueckgezogen** (Register: *„zurueckgezogen; Ersatz ist die
Kennzeichnung in A01 Paragraf 3.5"*). In `UI_SPEC.md` als solches gefuehrt,
mit Zeiger auf den urspruenglichen Wortlaut im Verlauf. Die Nummer bleibt
belegt, der Nummernkreis hat keine Luecke.

**6. `ArsenalTab` ist der Tab `Weapons & spells`** — belegt an
`nrplanner/app.py:2037` (`self.weapons_tab = ArsenalTab(...)`, direkt gefolgt
von `tabs.addTab(self.weapons_tab, "Weapons && spells")`). Deshalb stehen
AK-64 bis AK-66 (die T-052-Nachtraege zu Arsenal- und Waffenzeilen) in
Bereich 7.3 und nicht in einem eigenen Bereich. Geprueft, nicht geraten.

**7. Ein Werkzeug ohne versionierten Ort.** Der Aufbau laeuft ueber neun
kleine Python-Skripte (`lib.py`, `p0.py` bis `p7.py`) im Scratchpad. Wer
`UI_SPEC.md` spaeter erneut aus Register und Verlauf erzeugen will, braucht
sie; der Scratchpad ist ein Temp-Verzeichnis. **Vorschlag an den Director:**
wenn der Umbau wiederholbar sein soll, gehoeren sie nach `scripts/`. Ich habe
sie nicht dorthin gelegt — das waere ausserhalb der Dateiliste dieses
Auftrags.

## Offene Fragen an den App Designer

**Eine Frage, drei Faelle: gilt `1320 px` als Messumgebung weiter, obwohl es
als Startbreite aufgehoben ist?**

`A14 Z2555` (Director-Nachtrag zu AK-05, 06.09.2026, nach T-071) hebt die
feste Startbreite auf: verbindlich ist seither die abgeleitete
Oeffnungsbreite (`EffectTable.width_for_full_headings()`), und das Kriterium
ist nicht die Pixelzahl, sondern die Aussage „beim Startmass ist keine
Spaltenueberschrift gekuerzt". Zwei **spaetere** Kriterien schreiben die Zahl
trotzdem erneut vor:

- **AK-160** (A17 Z4319, T-080): Messfenster „bei Fensterbreite **1320 px**
  (Startbreite)". Zusaetzlich ist AK-160 als *schlechtester Fall* durch
  AK-189 (A21 Z5827, T-092) ueberholt, bleibt aber als Messung seiner
  Umgebung gueltig — auch das steht nirgends entschieden.
- **AK-194** (A21 Z5780, T-092): Messung der Statuszeilenbreite „bei
  **1320 px** Fensterbreite", daraus die Schranke `>= 105 px`.
- **AK-05** selbst traegt die Zahl im Erstwortlaut.

Es steht nirgends, welche Aussage gewinnt. **Wenn 1320 px als Messumgebung
bleibt**, gehoert die Zahl nach L-009 mit Plattform, Qt-Stil und Skalierung
ausgeschrieben und darf nicht mehr „Startbreite" heissen. **Wenn nicht**,
brauchen AK-160 und AK-194 eine neue Bezugsbreite, und die Schranke
`>= 105 px` aus AK-194 muss neu abgeleitet werden — sie stammt aus einer
einzigen gemessenen Zahl (158 px) bei genau dieser Breite.

Bis zur Entscheidung fuehren `UI_SPEC.md` und `UI_SPEC_REGISTER.md` beide
Fassungen nebeneinander, jeweils mit dem Vermerk, dass der Vorrang offen ist.
