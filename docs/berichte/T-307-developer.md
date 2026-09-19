STATUS: erledigt
AUFTRAG: T-307 — A24 Forschung: Namen der zwei namenlosen Feldbosse c3252 und c4021 (developer)
GELESEN: docs/tasks/T-307.md, CLAUDE.md, nrdata/bossdata.py (Z. 60-215, 363-500, 560-682), nrdata/extract.py (Z. 182-207, 480-528, 1435-1470), docs/berichte/T-299-developer.md, Skripte T-299/q2d_sitemsb.py und q4_join.py
GEÄNDERT: nur `docs/berichte/T-307-developer.md` (neu). Kein Anwendungscode, kein Commit. Skripte und Rohtabellen im Scratchpad `.../scratchpad/T-307/`.
ANNAHMEN: Dass Argument 5 des Gemeinschaftsereignisses 90015000 der Balkenname ist, ist meine Lesart des Aufrufs; belegt ueber alle Karten (Abschn. 4), nicht aus Spielwissen. Die Zuordnung Aufruf -> Figur laeuft ueber die Entity-Id der Part-Zeile, nicht ueber die Karte (Abschn. 2 und 6).
NÄCHSTER: architect — Name belegt fuer beide Figuren; die Leseroute ist neu (EMEVD statt FMG/Param), Vorschlag in Abschnitt 6, T-306 laeuft noch im Baum.
BLOCKIERT DURCH: nichts

# T-307 — Woher die zwei namenlosen Feldbosse ihren Namen nehmen

Gemessen am installierten Spiel (`d:\steam\steamapps\common\ELDEN RING
NIGHTREIGN\Game`), Paramdefs aus `vendor/Paramdex/NR/Defs`, Stand `afa4bbe`.

## 0. Antwort

| Figur | Karte | Name belegt | Quelle |
|---|---|---|---|
| c3252 (HP 2148) | `m46_54_00_00` | **Royal Carian Knight** | `/event/m46_54_00_00.emevd.dcx`, Aufruf `2000[6]` Ereignis 90015000, Argumente `[0, 90015000, 0, 46540800, 903253500, …]`; `NpcName[903253500] = "Royal Carian Knight"` |
| c4021 (HP 2279) | `m46_88_00_00` | **Royal Revenant** | `/event/m46_88_00_00.emevd.dcx`, `2000[6]` 90015000, `[0, 90015000, 0, 46880800, 904020540, …]`; `NpcName[904020540] = "Royal Revenant"` |

Der Name steht **nicht** an der Figur, sondern am Platz: das Ereignisskript
der Karte reicht die Name-Id als Argument herein. Deshalb hat c3252 weder
einen `903252…`-Eintrag noch eine `nameId` — es benutzt die Id aus dem Block
von c3253, und c4021 die von c4020. Beide Ids stehen als einzige ihres Blocks
in `NpcName`: `903253500` und `904020540`. Zweite Fundstelle fuer c4021:
`m46_59_00_00`, Entity 46590800, dieselbe Name-Id — beide Vorkommen sagen
dasselbe.

## 1. Frage 1 — alle NpcParam-Zeilen der beiden Figuren

`nameId` ist bei **jeder** Zeile beider Figuren `0`, und zwar nicht nur dort:
auch die benannten Nachbarn c3250, c3251, c4020 fuehren durchweg `nameId 0`.
Der `nameId`-Weg in `nrdata/extract.py:496-498` traegt in Nightreign an
keiner einzigen Zeile; alle 216 Namen kommen ueber den `90<chr><variant>`-Weg.

| Figur | Zeilen | HP | nameId | `NpcName 90<chr>xxx` |
|---|---|---|---|---|
| c3252 | 32520000, 32520010, 32520020, 32520100 | 1860 / 2148 / 2148 / 1860 | 0 | leer |
| c4021 | 40210000, 40210010, 40210020, 40210030, 40210700, 40219000 | alle 2279 | 0 | leer |
| c3250 | 5 Zeilen | 1633-2324 | 0 | 903250600 "Draconic Tree Sentinel", 903250610 "… and more" |
| c3251 | 7 Zeilen | 1454-2033 | 0 | 903251600 "Tree Sentinel", 903251610 "… and more" |
| c4020 | 5 Zeilen | 679 | 0 | 904020540 "Royal Revenant" |

Nebenbefund zur Praemisse des Auftrags: c4020 ist in Nightreign **nicht** der
Black Knife Assassin, sondern `NpcName[904020540] = "Royal Revenant"`.

`NpcParam` hat neben `nameId` nur `roleNameId`; ein `think`-Feld gibt es im
Def nicht, `NpcThinkParam` ist von `NpcParam` aus also nicht erreichbar.
Skript: `q1_npcrows.py`, Rohdaten `out/q1_npcrows.json`.

## 2. Frage 2 — die MSB-Part-Zeile

`m46_54_00_00` hat 2 Parts, davon einen `c3252_9000` (992 Byte);
`m46_88_00_00` ebenso einen `c4021_9000`. Die Zeile fuehrt **keine**
Namens- oder Variantenid. Sie fuehrt zweierlei, was traegt:

- die genaue NpcParam-Zeile (`32520010` bzw. `40210030`) — das ist der Weg,
  den `bossdata.derive_places` schon geht;
- die **Entity-Id** an fester Stelle: der `u64` bei Byte 96 der Part-Zeile ist
  ein Offset (hier 608), und dort steht der `i32` der Entity — 46540800 bzw.
  46880800. Gegenprobe ueber 3400 Parts aus sechs Karten: 126 Entity-Ids der
  eigenen Karte, 3273 leer (0/-1), 1 abweichend (`c0100_9002` in `m30_00`
  traegt 37900200, eine fremde Karte). Skript `q8_entity.py`.

Diese Entity-Id ist das Bindeglied zum Ereignisskript.

## 3. Frage 3 — die uebrigen FMG-Tabellen

Alle 54 Tabellen (97 Eintraege mit den `::dlc`-Haelften) wurden nach Schluesseln mit
`3252` oder `4021` durchsucht. Treffer nur in Gegenstandstabellen —
`AntiqueName 1004021` "Polished Burning Scene", `MagicName 4021` "Comet",
`WeaponName 14021000/14021100`, `GoodsName 40210` "Dawn", `BloodMsg`,
`TutorialTitle 402100` — keiner davon ist ein Figurname. In `EventTextForMap`,
`EventTextForTalk`, `TalkMsg` und `CL_MenuText`: **kein** Treffer.
`NpcName` hat 264 Schluessel, davon 216 im `90…`-Block ueber 125 Figuren. Die
48 ausserhalb sind die acht Spielerklassen samt Nebenrollen (100000 "Wylder"
bis 140010) und ein Block 912000xxx mit Gruppennamen ("Fallen Mercenaries",
"Erdtree Avatar"); keiner davon nennt 3252 oder 4021.
Skript `q2_parts_fmg.py`, Rohdaten `out/q3_fmg_hits.json`, `out/q3_npcname.json`.

## 4. Frage 5 — wie es die benannten Verwandten machen, und die Gegenprobe

Die Frage "welche Instruktion fuehrt ueberhaupt eine NpcName-Id als Argument"
ueber jedes vorhandene Ereignisskript (`bossdata._event_names`) beantwortet:

| Instruktion | Vorkommen mit NpcName-Argument |
|---|---|
| `2000[6]` (Gemeinschaftsereignis aufrufen) | 555 |
| `2003[102]` | 134 |
| `2003[11]` | 121 |
| `2003[100]` | 10 |
| `2004[91]` | 6 |
| `2000[0]` | 2 |

Die Aufrufe des Ereignisses 90015000 haben durchweg die Form
`[0, 90015000, 0, <Entity>, <NameId>, <float>, 0, 0]`: Entity und Name-Id
stehen nebeneinander. Gegenprobe ueber alle Karten, Entity aus der MSB
aufgeloest (Abschn. 2):

| Ergebnis | Faelle |
|---|---|
| Name-Id gehoert zur platzierten Figur | 90 |
| Name-Id gehoert zu einer **anderen** Figur | 40 |
| Entity in keiner MSB gefunden | 118 |

Die 40 Abweichungen sind kein Fehler der Lesart, sondern ihr Sinn: das Skript
benennt den Balken, nicht die Figur. Beispiele (je erstes Vorkommen):
c2140 -> "Omen", c3450 -> "Beastly Brigade", c3970 -> "Beastmen of Farum
Azula", c4351 -> "Lordsworn Captain", c4420 -> "Frost Crayfish", c7560 ->
"Equilibrious Beast", c7620 -> "Balancers" — dazu unsere beiden. Sieben der
zehn haben einen eigenen `NpcName`-Eintrag und werden trotzdem anders
benannt; das Skript hat also Vorrang vor dem Figurnamen, nicht nur Ersatz.
Skripte `q4_emevd.py`, `q5_rule.py`.

## 5. Frage 4 — SpEffect und NpcThinkParam: nichts

`SpEffectName` hat zu **keiner** der SpEffect-Ids beider Figuren einen
Eintrag, und die Ids sind Familien, keine Kennzeichen: c3252 nutzt 5324 (4
Figuren), 5364 (3), 5400 (188), 7750 (43), 7758 (9); c4021 nutzt 5360 (102),
5401 (109), 7740 (56), 7743 (23), 7745 (9), 7755 (17). c3250 und c3251 teilen
dieselben Ids. `NpcThinkParam` ist ueber `NpcParam` nicht erreichbar (kein
`think`-Feld im Def). Skript `q6_rest.py`.

## 6. Vorschlag fuer den Extraktor — nicht umgesetzt

Deckung, gegen den T-299-Ortsbestand gerechnet: von 116 Orten sind 90 benannt,
26 nicht. Von diesen 26 gewinnen ueber die Ereignisroute **genau zwei** einen
Namen — `m46_54` und `m46_88`. Die uebrigen 24 haben entweder gar keinen
90015000-Aufruf in ihrer Karte oder nur Aufrufe zu **anderen** Entities
(`m50_10` hat fuenf, unter anderem "Chief Bloodfiend" und "Death Knight", von
denen keiner die dortige Figur c3200 ist). Die Route darf deshalb **nur** ueber
die Entity-Id der eigenen Part-Zeile binden, nie ueber die Karte.
Skript `q7_unnamed.py`, Rohdaten `out/q7_unnamed.json`.

Diff-Skizze, zwei Stellen:

```
# nrdata/bossdata.py — derive_places(), in der Part-Schleife
   placements[chr_id] = placements.get(chr_id, 0) + 1
+  # Entity-Id der Part-Zeile: u64 bei Byte 96 zeigt auf den i32 der Entity.
+  off = struct.unpack_from("<Q", record, 96)[0]
+  if off and off + 4 <= len(record):
+      entity = struct.unpack_from("<i", record, off)[0]
+      if entity > 0:
+          entities.setdefault(chr_id, []).append(entity)
   ...
   entry: dict[str, Any] = {
       "map": map_name,
+      "entities": {str(c): v for c, v in entities.items()},

# nrdata/bossdata.py — neu, neben _flag_entities()
+def healthbar_names(archives, map_name: str) -> dict[int, int]:
+    """entity id -> NpcName id, aus den 90015000-Aufrufen dieser Karte.
+
+    Der Name am Lebensbalken steht am Platz, nicht an der Figur: c3252 und
+    c4021 haben keinen eigenen NpcName-Eintrag und werden vom Skript ueber
+    die Id einer Nachbarfigur benannt (T-307).
+    """
+    ... Instruktionen lesen wie _flag_entities, (bank, index) == (2000, 6),
+    args[1] == 90015000, dann {args[3]: args[4]}

# nrdata/extract.py — _subbosses(), nach dem chr_names-Nachschlag
-  "name": chr_names.get(chr_id, "") if chr_id is not None else "",
+  "name": _place_name(chr_id, entry, chr_names, npc_names, archives),
```

wobei `_place_name` zuerst die Ereignisroute fragt (Entity der Figur aus
`entry["entities"]`, Name-Id aus `healthbar_names`, Text aus `NpcName`) und
erst danach auf `chr_names` zurueckfaellt. Vorrang der Ereignisroute deckt
sich mit Abschnitt 4: wo beide etwas sagen, gilt das Skript.

Kosten: ein zusaetzlicher EMEVD-Lesevorgang je Ort (116 Karten). Die Skripte
liegen im selben Archiv, das `derive` fuer die Ereigniskette ohnehin oeffnet;
ob `derive` und `derive_places` sich den Lesevorgang teilen koennen, ist eine
Frage an den `architect` und nicht in dieser Skizze entschieden.
