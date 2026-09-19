STATUS: erledigt
AUFTRAG: T-299 — A24 Forschung: Register der Unterbosse am frischen Abzug (developer)
GELESEN: docs/tasks/T-299.md, GOAL.md (Nachtrag A24), CLAUDE.md, nrdata/extract.py (Z. 300-620, 960-1290, 1370-1445, 1546-1610), nrdata/bossdata.py (ganz), nrdata/param.py, nrdata/paramdef.py, nrdata/regulation.py, nrdata/dvdbnd.py, nrplanner/depthstab.py (Z. 50-130), nrplanner/datasource.py (defs_dir), .claude/hooks/enforce-data-redirect.ps1, vendor/Paramdex/NR/Defs/ChaosMatchingMutationEnemyTableParam.xml, LotResultPlayAreaParam.xml, LotResultSmallBaseAndSpot.xml, LotBaseSmallBaseAndSpot.xml, LotResultMapPatternFlag.xml, LotBaseMapPatternFlag.xml, .claude/agent-memory/developer/*
GEÄNDERT: nur `docs/berichte/T-299-developer.md` (neu). Kein Anwendungscode, kein Commit. Alle Skripte und Rohtabellen im Scratchpad `.../scratchpad/T-299/`.
ANNAHMEN: Die Karten-Id-Schreibweise `mAA_BB_00_00` aus einem Zahlenwert `AABB` ist meine Lesart; sie ist dadurch belegt, dass **alle 116** Werte eine existierende MSB liefern (116/116) und dass der Paramdef das Feld in `SmallBaseAndSpotDefine` selbst `mapIdN` nennt. Die Rollenbezeichnungen "Feldboss"/"Nachtboss" ordne ich nach Fundstelle zu (Kat 120 = Ortslotterie, `LotResultPlayAreaParam` = Tag-1/2-Lotterie); die Dateien tragen dafuer keine eigenen Namen.
NÄCHSTER: architect — Stufe 1 und Stufe 2 sind beide belegt und tragen; der Extraktor braucht dafuer eine neue Leseroute (Abschnitt 7), kein Umbau der vorhandenen.
BLOCKIERT DURCH: nichts

# T-299 — Register der Unterbosse: was die Dateien hergeben

## 0. Kernbefund in drei Saetzen

1. `ChaosMatchingMutationEnemyTableParam.smallBaseId` ist **keine Figur-Id,
   sondern eine Karten-Id** (ein Ort). Die heutige Lesart in
   `nrdata/extract.py:551-597` deutet sie als `chr` und trifft damit 21 von
   116 Werten zufaellig — die Namen im `kinds`-Block und in der
   Beispielspalte des Deep-of-Night-Tabs benennen zum Teil Orte als Figuren.
2. Der vollstaendige Weg vom Ort zur Figur laeuft ueber die MSB der Karte,
   nicht ueber EMEVD: `smallBaseId` -> `m{AA}_{BB}_00_00.msb.dcx` ->
   `PARTS_PARAM_ST` -> `cNNNN` -> NpcParam. `bossdata._profile` liefert
   darauf HP, Stance, Schadens- und Statusfelder **ohne** `defeatEventFlag`.
3. Die Nachtbosse Tag 1/2 stehen nicht in Kategorie 120, sondern in einer
   bisher ungelesenen Tabelle: **`LotResultPlayAreaParam`** (520 Zeilen,
   Felder `patternId, playArea1, playArea2, bossId1, bossId2, extraBossId1,
   extraBossId2, bossModifier1..4`). Ueber `patternId` haengt daran der
   Nachtfuerst. Damit ist Stufe 2 belegt, nicht nur moeglich.

## 1. Frage 1 — Member-Liste von `regulation.bin`

Gemessen am installierten Spiel (`d:\steam\steamapps\common\ELDEN RING
NIGHTREIGN\Game\regulation.bin`), Paramdefs aus
`vendor/Paramdex/NR/Defs`.

| Kennzahl | Wert |
|---|---|
| Param-Member in `regulation.bin` | **252** |
| mit Paramdef gleichen Namens | 208 |
| Paramdef nutzbar (gleich lang oder kuerzer = Praefix) | 201 |
| Paramdef vorhanden, aber **laenger als die Zeile** (wird verworfen) | 7 |
| ohne jeden Paramdef | 44 |
| heute vom Extraktor gelesen | **31** |

### 1a. Heute gelesen (31)

| Member | Zeilen | Zeilenlaenge |
|---|---|---|
| AntiqueStandParam | 74 | 24 |
| AttachEffectFilterParam | 426 | 20 |
| AttachEffectFilterSubCategoryParam | 61 | 32 |
| AttachEffectParam | 2079 | 68 |
| AttachEffectTableParam | 22088 | 12 |
| AttackElementCorrectParam | 152 | 128 |
| CalcCorrectGraph | 82 | 80 |
| ChaosMatchingCorrectParam | 90 | 20 |
| ChaosMatchingMutationCategoryParam | 46 | 20 |
| ChaosMatchingMutationEnemyTableParam | 3067 | 48 |
| ChaosMatchingRankControlParam | 5 | 14 |
| CharaInitParam | 1740 | 320 |
| ClearCountCorrectParam | 8 | 128 |
| EquipParamAntique | 1397 | 48 |
| EquipParamCustomWeapon | 5148 | 48 |
| EquipParamWeapon | 2317 | 680 |
| HeroParam | 10 | 176 |
| HeroStatusParam | 100 | 28 |
| ItemLotParam_enemy | 2741 | 224 |
| ItemLotParam_map | 4310 | 224 |
| ItemTableParam | 34730 | 36 |
| LotResultMapPatternFlag | 5738 | 28 |
| Magic | 178 | 172 |
| NightBossMenuParam | 19 | 68 |
| NpcParam | 3016 | 848 |
| PermanentBuffParam | 123 | 24 |
| PlayerCommonParam | 1 | 760 |
| ReinforceParamWeapon | 255 | 132 |
| SessionRewardByModeRankParam | 7 | 65 |
| SpEffectParam | 13472 | 1024 |
| UserDispLogParam | 253 | 32 |

`ItemLotParam_enemy` und `ItemLotParam_map` haben **keinen eigenen** Def; der
Extraktor liest sie mit dem generischen `ItemLotParam.xml` als Praefix — das
funktioniert und ist in Abschnitt 5 nachgemessen.

### 1b. Ungelesen, Paramdef nutzbar (172)

AcrossDayCorrectParam (10), ActionButtonParam (220), AiSoundParam (235),
AssetMaterialSfxParam (45), AssetModelSfxParam (1148),
AttachEffectFilterCategoryParam (5), AutoCreateEnvSoundParam (6),
BehaviorParam (13103), BuddyParam (4), BuddyStoneParam (243), BudgetParam
(5), Bullet (12254), BulletCreateLimitParam (72), Ceremony (26),
ChaosMatchingReplaceTreasureCommon (1), ChaosMatchingReplaceTreasureTable
(397), CharMakeMenuListItemParam (218), CharMakeMenuTopParam (203),
ChrModelParam (348), ChrPhysicsVelocityChangeParam (73), CoolTimeParam (40),
CutSceneTextureLoadParam (1), CutsceneGparamTimeParam (16),
CutsceneGparamWeatherParam (16), CutsceneMapIdParam (17),
CutsceneTimezoneConvertParam (7),
CutsceneWeatherOverrideGparamConvertParam (22), DecalParam (565),
DefeatBossSoulParam (2), DirectionCameraParam (6), EnemyCommonParam (1),
EnvObjLotParam (13), EquipMtrlSetParam (365), EquipParamAccessory (136),
EquipParamGoods (433), EquipParamProtector (307), FaceParam (538),
FaceRangeParam (2), FallControlParam (20), FeTextEffectParam (68),
FootSfxParam (57), GameSystemCommonParam (1), GestureParam (56),
GparamRefSettings (2), GraphicsCommonParam (1), GraphicsConfig (9),
GrassLodRangeParam (25), GrassTypeParam (445), HeroMenuCameraParam (6),
HeroMenuParam (10), HeroOperationExplanationParam (30),
HitEffectSfxConceptParam (96), HitEffectSfxParam (218), HitMtrlParam (55),
KeyAssignMenuItemParam (50), KeyAssignParam (72), KnockBackParam (7),
KnowledgeLoadScreenItemParam (65), LegacyDistantViewPartsReplaceParam (1),
LimitedDayAssetParam (3), LoadBalancerDrawDistScaleParam (22),
LoadBalancerParam (20), LobbyMenuNpcParam (39), LobbyMenuParam (15),
LockCamParam (309), **LotBaseMapPatternFlag (254)**, **LotBaseSmallBaseAndSpot
(192)**, **LotResultPlayAreaParam (520)**, **LotResultSmallBaseAndSpot
(23830)**, MagicTableParam (2350), MainScenarioMenuParam (1),
**ManualMapPattern (2980)**, MapDefaultInfoParam (112), MapGdRegionDrawParam
(13), MapGdRegionInfoParam (59), MapGridCreateHeightLimitInfoParam (1),
MapMimicryEstablishmentParam (89), MapNameTexParam (33), MapPatternCommon
(3), MapPatternMapLotCondition (30), MapPatternSet (100), MapPieceTexParam
(50), MaterialExParam (381), MenuColorTableParam (118), MenuCommonParam (1),
MenuOffscrRendParam (13), MenuPropertyLayoutParam (1947),
MenuPropertySpecParam (717), MenuValueTableParam (133), MenuWindowParam
(109), MimicryEstablishmentTexParam (1), MissionManagementParam (22),
MixcraftMagicParam (65), MoveParam (52), MultiPlayCorrectionParam (85),
MultiSoulBonusRateParam (5), NPCBotTableParam (45), NpcAiActionParam (323),
NpcAiBehaviorProbability (518), NpcThinkParam (1322), ObjActParam (64),
OperationGuideParam (28), OverlayMaterialParam (50), PartsDrawParam (577),
PersonalScenarioParam (227), PhantomParam (63), PinTypeParam (3),
PlayAreaCreateCommonParam (3), PlayAreaCreateDefaultParam (25),
**PlayAreaCreateParam (41)**, PlayAreaGiantAssetCtrlParam (1),
PostureControlParam_Pro (12), PostureControlParam_WepLeft (134),
PostureControlParam_WepRight (128), RandomAppearParam (115),
RareMapInfoMenuParam (5), ReinforceParamProtector (17), ResistCorrectParam
(51), ResultMenuPlaySpeedParam (5), RideParam (88), RollingObjLotParam (1),
RuntimeBoneControlParam (1466), ScenarioPlacementParam (330),
ScratchedPartsParam (288), SeActivationRangeParam (181),
SeMaterialConvertParam (99), SessionRandomAssetTexReplaceParam (297),
SessionRewardCommonParam (1), SfxBlockResShareParam (1), ShopLineupParam
(3563), SignPuddleParam (163), **SmallBaseAndSpotAttachPoint (562)**,
**SmallBaseAndSpotDefine (107)**, SmallBaseEnemyLotMapCombinationParam (11),
SmallBaseMapVariationParam (362), SmallBaseSfxLodExclusionList (1),
SmallbaseInvationNpcParam (11), SortieStartingPoint (23),
SoundAssetSoundObjEnableDistParam (130), SoundAutoEnvSoundGroupParam (11),
SoundAutoReverbEvaluationDistParam (6), SoundAutoReverbSelectParam (12),
SoundChrPhysicsSeParam (13), SoundCommonIngameParam (27), SoundCutsceneParam
(25), SpEffectSetParam (571), SpeedtreeParam (169), SubstoryLinkParam (1),
SwordArtsParam (194), SwordArtsTableParam (11896), TalkParam (1878),
TextEmbedImageParam (19), ThrowCounterParam (82), ThrowDirectionSfxParam
(57), ThrowParam (1509), ToughnessParam (92), TutorialCategoryParam (6),
TutorialParam (124), WaypointParam (6), WeatherAssetCreateParam (1),
WeatherAssetReplaceParam (180), WeatherLotParam (45), WeatherLotTexParam
(25), WeatherParam (86), WepAbsorpPosParam (82), WetAspectParam (23),
WhiteSignCoolTimeParam (10), WorldMapLegacyConvParam (1), WorldMapPieceParam
(28), WorldMapPlaceNameParam (9), WorldMapPointIconParam (52),
WorldMapPointParam (1053)

Fett: die neun Tabellen, die fuer A24 tragen (Abschnitte 3-4).

### 1c. Ohne nutzbaren Paramdef (49 ungelesene + die 2 gelesenen ItemLot)

AssetEnvironmentGeometryParam (21538 Z, 320 B, def zu lang), AtkParam_Npc
(11783 Z, 464 B), AtkParam_Pc (8988 Z, 464 B), BehaviorParam_PC (10855 Z,
32 B), BonfireWarpParam (3 Z, 236 B, def zu lang), GrassTypeParam_Lv1 (71 Z,
276 B), GrassTypeParam_Lv2 (13 Z, 276 B), HPEstusFlaskRecoveryParam (45 Z,
32 B), LoadBalancerDrawDistScaleParam_ps4/ps5/xb1/xb1x/xss/xsx (je 22 Z,
128 B), LoadBalancerNewDrawDistScaleParam_ps4/ps5/win64/xb1/xb1x/xss/xsx
(1-14 Z), MPEstusFlaskRecoveryParam (45 Z), MessageBoxParamDialog (123 Z,
4 B), MessageBoxParamSystem (153 Z, 4 B), MultiHPEstusFlaskBonusParam (5 Z),
MultiMPEstusFlaskBonusParam (5 Z), NetworkMsgParam (6 Z, def zu lang),
NetworkParam (1 Z, def zu lang), PlayRegionParam (451 Z, def zu lang),
ShopLineupParam_Recipe (133 Z), SpEffectVfxParam (1937 Z, def zu lang),
WwiseValueToStrParam_* (18 Tabellen, 2-261 Z) — sowie die beiden heute
gelesenen **ItemLotParam_enemy** (2741 Z) und **ItemLotParam_map** (4310 Z),
die ueber den fremden `ItemLotParam.xml`-Praefix laufen.

Fuer A24 fehlt an dieser Stelle **nichts**: alle neun tragenden Tabellen
haben einen nutzbaren Def.

## 2. Frage 2 — Roster der Kategorien, und warum die heutige Lesart nicht traegt

### 2a. Der Beleg, dass `smallBaseId` ein Ort ist

116 verschiedene Werte kommen im Feld vor. Drei Gegenproben an denselben 116:

| Probe | Treffer |
|---|---|
| NpcParam-Zeile `value*10000 .. +9999` vorhanden | 21 / 116 |
| `/chr/c{value}.chrbnd.dcx` im dvdbnd vorhanden | 21 / 116 |
| `/map/mapstudio/m{AA}_{BB}_00_00.msb.dcx` vorhanden | **116 / 116** |
| als `mapIdN` in `SmallBaseAndSpotDefine` genannt | 100 / 116 |
| als `defaultSmallBase` in `SmallBaseAndSpotAttachPoint` genannt | 16 / 116 |

100 + 16 = 116: jeder Wert ist entweder ein Ort in einer Define-Zeile oder
der Vorgabeort eines Anhaengepunkts. Der Def nennt das Feld in
`SmallBaseAndSpotDefine` selbst `mapIdN`.

Der Zufall bricht an einer Stelle sichtbar auf: Ort `4650` ist
`m46_50_00_00`, und dort steht **kein** `c4650`; `c4650` (Nox Dragonkin
Soldier) steht in `m46_70_00_00` und `m49_23_00_00`. Die Gleichheit von
Ortszahl und Figurzahl ist also keine Regel, sondern eine Ueberschneidung
zweier Nummernraeume.

Damit ist die Prosa in `nrdata/extract.py:556-566` ("u16 at +6, where set, is
a character id ... category 160's four are the arena bosses") **widerlegt**.
Die vier Werte der Kategorie 160 sind die Karten `m46_50/60/70/80`, und in
denen stehen gemischte Besetzungen (31/20/8/7 Parts), kein einzelner Boss.

### 2b. Was die angefragten Kategorien wirklich enthalten

| Kat | Orte | Weltkarten-Symbol (`worldMapPointIconId1`) | Charakter |
|---|---|---|---|
| 101 | 28 | 3, 24, 7, 77, 10, 78 | Lager/Ruinen, 100-1500 Parts je Karte |
| 102 | 29 | 24, 3, 7, 10, 77, 78 | wie 101, ohne Gewichtszeile |
| 103 | 5 | (kein Symbol) | Haendlerorte |
| 104 | 3 | 3, 10 | drei grosse Orte (m32_20, m34_00, m52_50) |
| 110 | 28 | identisch zu 101 | **derselbe Ortssatz wie 101** |
| 120 | 45 | 28 (84x), 16 (47x) | 29 Ein-Boss-Karten + 16 Karten `m20_00..m21_50` |
| 130/131 | je 3 | – | m49_41/42/43 |
| 135 | 11 | – | m53_67..m53_91 |
| 136 | 8 | – | m53_49..m53_64 |
| 137 | 13 | – | m53_67..m53_91 (Ueberschneidung mit 135) |
| 138 | 16 | – | m53_49..m53_64 (Ueberschneidung mit 136) |
| 160 | 4 | 5 | m46_50/60/70/80, gemischte Besetzung |

`WorldMapPointIconParam` (52 Zeilen) traegt nur `iconId` und keinen Text —
die Ortsart ist im Param **nicht benennbar**, nur unterscheidbar.

Fuer 135-138 (alle in `m53_xx`) gilt: keine der Karten hat eine Ein-Boss-
Besetzung; das sind die Shifting-Earth-Orte, keine Bossplaetze.

### 2c. Der Roster, den A24 Stufe 1 braucht: Kategorie 120, 29 Ein-Boss-Karten

Jede dieser Karten hat 2-12 Parts und genau eine boss-grosse Figur. HP aus
`bossdata._profile` der NpcParam-Zeilen, die die MSB-Part-Zeile selbst nennt.

| Ort | Karte | Figur | Name (FMG) | NpcParam | HP |
|---|---|---|---|---|---|
| 4551 | m45_51 | c2130 | Fell Omen | 21300030, 21300500 | 2521 |
| 4651 | m46_51 | c3181 | Red Wolf of the King Consort | 31810010 | 1165 |
| 4652 | m46_52 | c3250 | Draconic Tree Sentinel | 32500010, 32500090 | 2324 |
| 4653 | m46_53 | c3251 | Tree Sentinel | 32510020 | 2033 |
| 4654 | m46_54 | c3252 | (unbenannt) | 32520010 | 2148 |
| 4655 | m46_55 | c3460 | Leonine Misbegotten | 34600020 | 1240 |
| 4656 | m46_56 | c3100 | Bell Bearing Hunter | 31000010, 31000020 | 2359 |
| 4657 | m46_57 | c4270 | Elder Lion | 42700010, 42700020 | 1280 |
| 4658 | m46_58 | c4500 | Flying Dragon of the Hills | 45000010 | 1518 |
| 4659 | m46_59 | c4501 | Decaying Rancor Dragon | 45010000, 45010010 | 5753 |
| 4662 | m46_62 | c4580 | Wormface | 45800010 | 1587 |
| 4663 | m46_63 | c4640 | Ulcerated Tree Spirit | 46400010, 46400020 | 2854 |
| 4664 | m46_64 | c4670 | Ancestor Spirit | 46700010 | 1882 |
| 4665 | m46_65 | c4690 | Grafted Scion | 46900010 | 1811 |
| 4666 | m46_66 | c4770 | Valiant Gargoyle | 47701210 | 1745 |
| 4667 | m46_67 | c4810 | Erdtree Avatar | 48100010 | 2321 |
| 4668 | m46_68 | c4910 | Magma Wyrm | – | 2680 |
| 4669 | m46_69 | c7100 | Ancient Hero of Zamor | – | 1418 |
| 4671 | m46_71 | c4480 | Miranda Blossom | – | 1939 |
| 4672 | m46_72 | c5011 | Golden Hippopotamus | – | 1792 |
| 4674 | m46_74 | c4980 | Death Rite Bird | – | 2264 |
| 4677 | m46_77 | c4130 | Demi-Human Queen | – | 911 |
| 4681 | m46_81 | c2100 | Black Knife Assassin | 21000020 | 904 |
| 4682 | m46_82 | c3181 | Red Wolf of the King Consort | 31810010 | 1165 |
| 4686 | m46_86 | c3460 | Leonine Misbegotten | 34600020 | 1240 |
| 4687 | m46_87 | c3100 | Bell Bearing Hunter | – | 2359 |
| 4688 | m46_88 | c4021 | (unbenannt) | – | 2279 |
| 4691 | m46_91 | c4690 | Grafted Scion | – | 1811 |
| 4695 | m46_95 | c7100 | Ancient Hero of Zamor | – | 1418 |

"NpcParam –" heisst: die Part-Zeile nennt keine Zeilen-Id, dann greift
`bossdata`s Rueckfall auf alle Zeilen der Figur (`by_chr`), und `_profile`
nimmt die Zeile mit der hoechsten HP. Das ist derselbe Weg, den der
Nightlords-Tab heute schon geht.

Die restlichen 16 Orte der Kategorie 120 (`m20_00` bis `m21_50`) sind
Karten mit 58-115 Parts, in denen genau eine Figur steht: `c4680`
Fallingstar Beast, in allen 16 dieselbe Zeile `46801010`. Das ist ein
Platzhalter, kein Boss-Roster — die 16 sind die Arena-Schalen.

### 2d. Loest `bossdata` das ohne EMEVD auf?

**Ja.** `bossdata._profile(rows)` braucht nur NpcParam-Zeilen und liefert
`hp`, `npc_row`, `damage` (acht `*DamageCutRate`), `status` (sechs
`resist_*`), `stance` (`superArmorDurability`, `superArmorRecoverCorrection`,
`toughnessRecoverCorrection`), `part_rates`, `weak_flags`, `weak_damage`,
`weak_status`, `resistant_to`. Fuer alle 29 Figuren oben ist ein Profil
entstanden.

Was fehlt, ist nur die **Einstiegsseite**: `bossdata.derive()` ist fest auf
`NightBossMenuParam.defeatEventFlag` verdrahtet (Z. 326-360) und findet die
Figur ueber EMEVD + MSB. Fuer die Unterbosse ist der Einstieg ein anderer
(Ort -> MSB), das Ziel dasselbe. Konkret wiederverwendbar, ohne Aenderung:
`_parts`, `_param_section`, `_profile`, `_ladder`, `_defence_buffs`, `_tae`,
`CREW`. Nicht wiederverwendbar: `_flag_entities`, `_flags_mentioned`,
`_event_names`, `_map_of` — die gesamte EMEVD-Haelfte entfaellt.
`_ladder`/`_defence_buffs` laufen ueber `SpEffectParam` + TAE je Figur und
sind vom Einstieg unabhaengig.

## 3. Frage 3 — Nachtbosse

### 3a. Kategorie 120 ist nicht der Nachtboss-Cast

Gegen die im Auftrag genannte Liste gehalten: Fell Omen, Tree Sentinel,
Draconic Tree Sentinel, Wormface, Ancient Hero of Zamor **sind** in Kat 120;
Centipede Demon, Gaping Dragon, Nameless King, Smelter Demon **nicht**.
Deren Figuren gibt es (`NpcName` strukturiert: c7710, c7700, c7900, c7820),
und sie stehen in Karten, die in keiner ChaosMatching-Kategorie vorkommen:
`m47_90`, `m47_80`, `m48_20`, `m48_10`.

### 3b. Wo der Cast steht: `LotResultPlayAreaParam`

Ein Wertescan ueber alle 252 Params nach den Karten-Ids `4770..4890` hat die
Tabelle gefunden. Def:

```
s32 unknown_0 | s32 patternId | s32 playArea1 | s32 playArea2
s16 bossId1 | s16 bossId2 | s16 extraBossId1 | s16 extraBossId2
s32 bossModifier1 | s32 bossModifier2 | s32 extraBossModifier1 | s32 extraBossModifier2
```

520 Zeilen, eine je Kartenmuster — dieselben 520 `patternId` wie
`LotResultMapPatternFlag` (Schnitt 520/520). `bossId1` ist die Karte des
Tag-1-Bosses, `bossId2` die des Tag-2-Bosses, beides im selben Karten-Id-Raum
wie `smallBaseId`. Beispielzeile:

```
id 2  patternId 2  playArea1 1002  playArea2 1003
      bossId1 4924 (m49_24, c3100 Bell Bearing Hunter)
      bossId2 4840 (m48_40, c2130 Fell Omen)
      bossModifier1 439  bossModifier2 400
```

35 verschiedene Bosskarten werden gezogen:

| Id | Karte | Besetzung (bis vier, nach Anzahl) |
|---|---|---|
| 4770 | m47_70 | c3500 x16 ?, c3060 x3 ?, c4950 Tibia Mariner, c4960 ? hp=1918 |
| 4780 | m47_80 | c4080 x5, c4090 x3, c2150 ? hp=5120, **c7700 Gaping Dragon hp=2950** |
| 4790 | m47_90 | c4250 x6, c4240, **c7710 Centipede Demon hp=2240**, c7711 |
| 4800 | m48_00 | c7810 x26, c3664, **c7800 The Duke's Dear Freja hp=1344** |
| 4810 | m48_10 | c3080 x4, c4260 Erdtree Burial Watchdogs, **c7820 Smelter Demon hp=3731** |
| 4820 | m48_20 | c3970, c4505 Flying Dragon, **c7900 Nameless King hp=1770**, c7910 |
| 4830 | m48_30 | c3300 x3 Nox Warriors, **c7920 Dancer of the Boreal Valley hp=1792** |
| 4840 | m48_40 | c2140 x3 Omen, **c2130 Fell Omen hp=2521** |
| 4850 | m48_50 | c4353 x6, c4363 x4, c4373 x3, **c3250 Draconic Tree Sentinel hp=1633** |
| 4860 | m48_60 | c4300 x6, c4353 x4, c4363 x4, **c3251 Tree Sentinel hp=2033** |
| 4880 | m48_80 | c3901 x2, c4386 x2, c3560 Godskin Apostle, **c3570 Godskin Noble hp=2055** |
| 4890 | m48_90 | c3662 x5, c3661 x4, c4040 x4, c4080 x4 — **kein klarer Boss** |
| 4910 | m49_10 | c3000 x3, c3010 x2, c3020, **c4750 Grafted Monarch hp=2560** |
| 4917 | m49_17 | c4373 x4, c4313 x3, c4353 x2, **c4770 Valiant Gargoyle hp=1745** |
| 4918 | m49_18 | c3950 x5 (unbenannt) — Gruppenboss |
| 4919 | m49_19 | c3970 x7 Beastmen of Farum Azula — Gruppenboss |
| 4920 | m49_20 | c4380 x3, **c3600 x2 Stoneskin Lords hp=628** |
| 4921 | m49_21 | c3500 x6, c3060 x3, **c4980 Death Rite Bird hp=2097** |
| 4923 | m49_23 | c3320 x5 Mimic Tears, c3300 x2, **c4650 Nox Dragonkin Soldier hp=2758** |
| 4924 | m49_24 | c4300 x6, c3700 x2, **c3100 Bell Bearing Hunter hp=2359** |
| 4925 | m49_25 | c3450 x4, c3451 x3, c2500 Crucible Knight, **c5011 Golden Hippopotamus hp=1600** |
| 4926 | m49_26 | c3000 x4, c3010 x3, c3020 x2, **c3050 Outland Commander hp=2834** |
| 4927 | m49_27 | c3000 x10, c3020 x4, c3010, **c3050 Outland Commander hp=2834** |
| 4928 | m49_28 | c2140 x4 Omen, **c3150 x2 Night's Cavalry hp=1006**, c3160 x2 |
| 4929 | m49_29 | c4110 x6, c4100 x5, c4101 x4, **c4130 Demi-Human Queen hp=1587** |
| 4930 | m49_30 | c4000 x8, **c4021 ? hp=2279** |
| 4990 | m49_90 | c3650 x6, **c4640 Ulcerated Tree Spirit hp=2854** |
| 5200 | m52_00 | c5900 x5, c5240 x2, c5040 Curseblade, **c5250 Horned Warrior hp=1190** |
| 5201 | m52_01 | **c4630 x2 Runebear hp=640** |
| 5202 | m52_02 | c4150 x3, c5070 x3 Death Knight, c4315 x2, **c4355 Mausoleum Knight hp=576** |
| 5203 | m52_03 | c4381 x5, c4385 x3, **c7930 Demon in Pain hp=1536** |
| 5210 | m52_10 | c4801 x8, c3470 x3, c3471 x2, **c4800 Omen hp=2304** |
| 5211 | m52_11 | c5090 x8 (unbenannt) — Gruppenboss |
| 5212 | m52_12 | c5240 x49 (unbenannt) — Gruppenboss |
| 5213 | m52_13 | c3661 x6, c4381 x6, **c7932 x3 ? hp=2880**, c7930 x2 Demon in Pain hp=2880 |

**Grenze der Automatik:** "hoechste HP" waehlt in 4 von 35 Karten die
falsche Figur (m47_80 nimmt c2150 hp=5120 statt Gaping Dragon hp=2950;
m48_90, m52_11, m52_12 haben keinen HP-Ausreisser). `bossdata` hat fuer
genau diesen Fall bereits zwei Regeln — `_tuned` (Streuung der
Schadensfaktoren >= 0,1) und die Gruppenboss-Regel (`INFERRED_GROUP_MIN`);
die muessen auf diesen Weg angewandt werden, nicht neu erfunden.

### 3c. Die anderen Kandidaten aus der Frage

| Tabelle | Zeilen | Was drin steht | traegt Bossplaetze? |
|---|---|---|---|
| `SmallBaseAndSpotDefine` | 107 | `mapId1..18` (die Orte je Ortsgruppe), Weltkarten- und Detailsymbole, `invasionWeight` | mittelbar: gruppiert Orte, nennt keine Figur |
| `SmallBaseAndSpotAttachPoint` | 562 | `areaNo/gridXNo/gridZNo`, `attachPointEntityId`, `posX/Y/Z`, `defaultSmallBase` | ja, die Plaetze — inkl. der Bossplaetze 500-519, 800-817, 1130-1133, 1180-1183 |
| `PlayAreaCreateParam` | 41 | `areaNo/gridXNo/gridZNo`, `day1Flag` (7650..), `day2Flag` (7675..), `requireModifier1/2`, `excludeModifier1/2`, `bossAttachPoint`, `extraBossAttachPoint` | ja, **wo** die Tag-1/2-Arena steht, nicht **wer** darin steht |
| `PlayAreaCreateDefaultParam` | 25 | Vorgabekoordinaten, keine Ids | nein |
| `PlayAreaCreateCommonParam` | 3 | Kreisradien und -uhrzeiten, Regen-SpEffects | nein |
| `ScenarioPlacementParam` | 330 | `charaInitParamId`, zwei Ereignis-Flags | nein (Spielerfiguren, nicht Gegner) |
| `RandomAppearParam` | 115 | 100 Ja/Nein-Schalter je Zeile, sonst nichts | nein |
| `NPCBotTableParam` | 45 | `npcParamId` 6000xxxxx, `npcThinkId`, `charaInitParamId` | nein (KI-Mitspieler) |
| `SmallBaseEnemyLotMapCombinationParam` | 11 | Dreier-Kombinationen von Ortsids (z. B. 4650/4660/4670) | nein |
| `LotResultSmallBaseAndSpot` | 23830 | `patternId, attachId, smallBaseMapId, mapIndex, variationId, modifier` | **ja — die Ortslotterie, siehe Frage 4** |
| `LotResultPlayAreaParam` | 520 | siehe 3b | **ja — die Bosslotterie Tag 1/2** |

Die Bossplaetze aus `PlayAreaCreateParam` (500-519, 800-817, 1130-1133,
1180-1183) sind Zeilen in `SmallBaseAndSpotAttachPoint`, kommen aber in
`LotResultSmallBaseAndSpot.attachId` **nie** vor (416 gezogene Plaetze,
Schnittmenge leer). Die Tag-1/2-Arena laeuft also ueber die eigene Lotterie
`LotResultPlayAreaParam`, nicht ueber die Ortslotterie — beide sauber
getrennt, beide ueber `patternId` verbunden.

## 4. Frage 4 — Zuordnung Boss -> Nachtfuerst und Tag: **belegt**

Der Weg braucht die unbenannten `modifier`-Ids **nicht**. Er laeuft ueber
`patternId`:

```
LotResultMapPatternFlag.patternId -> targetBoss  (= NightBossMenuParam-Zeilen-Id)
LotResultSmallBaseAndSpot.patternId -> attachId + smallBaseMapId   (Orte)
LotResultPlayAreaParam.patternId   -> bossId1 / bossId2            (Nacht, Tag 1/2)
```

Gemessen: 520 Muster in allen drei Tabellen, Schnitt 520/520, **0** Zeilen
aus `LotResultSmallBaseAndSpot` ohne passendes Muster (23 830 von 23 830
zugeordnet).

Ergebnis Feld-/Evergaol-Orte je Nachtfuerst (Anzahl Orte, davon Kat 120 und
Kat 160):

| Nachtfuerst | Orte | Kat 120 | Kat 160 |
|---|---|---|---|
| 0 Gladius | 146 | 36 | 4 |
| 1 Adel | 136 | 33 | 4 |
| 2 Gnoster | 141 | 29 | 4 |
| 3 Maris | 148 | 33 | 4 |
| 4 Libra | 136 | 32 | 4 |
| 5 Fulghor | 145 | 29 | 4 |
| 6 Caligo | 140 | 34 | 4 |
| 7 Heolstor | 142 | 29 | 4 |
| 8 Harmonia | 152 | 32 | 4 |
| 9 Straghess | 145 | 29 | 4 |

Ergebnis Nachtbosse je Nachtfuerst und Tag (Anzahl Muster; Auszug, die
vollen Listen in `q9_nightlot.json`):

| Nachtfuerst | Tag 1 | Tag 2 |
|---|---|---|
| Gladius | Demi-Human Queen 25, Bell Bearing Hunter 25 | Fell Omen 28, Tree Sentinel 22 |
| Gnoster | Ulcerated Tree Spirit 12, Outland Commander 11, Death Rite Bird 9, Smelter Demon 9, Centipede Demon 9 | m49_18 18, Draconic Tree Sentinel 17, Nox Dragonkin Soldier 15 |
| Fulghor | c4021 12, Night's Cavalry 11, m47_80 9, Centipede Demon 9, c3662 9 | Nameless King 22, Outland Commander 15, Nox Dragonkin Soldier 13 |
| Caligo | Grafted Monarch 12, Ulcerated Tree Spirit 11, Smelter Demon 9, Duke's Dear Freja 9, Death Rite Bird 9 | Dancer of the Boreal Valley 22, Draconic Tree Sentinel 19, Godskin Noble 9 |
| Heolstor | 14 verschiedene, je 2-6 | 13 verschiedene, je 2-5 |
| Harmonia | Horned Warrior 30, Demon in Pain 30 | Omen 30, c7932 30 |
| Straghess | Runebear 30, Mausoleum Knight 30 | c5090 30, c5240 30 |

Gladius, Harmonia und Straghess haben je genau zwei Bosse je Tag; Heolstor
zieht aus dem ganzen Feld. Das ist eine Aussage ueber die Zusammensetzung
des Musterpools, nicht ueber die Ziehwahrscheinlichkeit — dieselbe Grenze,
die `_gating` heute schon nennt (`MapPatternSet` traegt Gewichte je Muster).

Zu den `modifier`-Ids selbst: sie bleiben unbenannt, sind aber jetzt
einordnbar. Drei getrennte Raeume:

| Tabelle | Anzahl Werte | Beispielwerte |
|---|---|---|
| `LotResultMapPatternFlag.modifier` | 66 | 10-15, 120-230, 600-604, 700/701, 1100er, 11150, 110000 |
| `LotBaseSmallBaseAndSpot.modifier1/2` | 37 | 10-15, 200/210/230, 600-604, 1100-1106, 1150-1154, 1300-1304, 9000-9002, 12002/12003 |
| `LotResultSmallBaseAndSpot.modifier` / `LotResultPlayAreaParam.bossModifier*` | 30 | 400-449, 14000 |

Schnitt Pattern/Base: **35 Werte** — die Ereignis-Modifier erreichen die
Ortslose. Schnitt Pattern/Spot: **leer** — der 4xx-Raum ist ein eigener
Boss-Modifier-Raum. Der Bossplatz haengt also **nicht** am
Ereignis-Modifier, was die Frage mit "nicht ueber den Modifier, sondern
ueber `patternId`" beantwortet.

## 5. Frage 5 — Beute: `_event_drops` greift ohne Aenderung

`extract._event_drops` schluesselt nach `row.id // 10000` ueber **alle**
NpcParam-Zeilen und kennt weder Nachtfuerst noch Kategorie. 164 Figuren
haben eine Beute-Liste. Stichprobe, je Figur die erste Kettenstufe:

| Rolle | Figur | erste Kette | `_event_drops` |
|---|---|---|---|
| Evergaol m49_23 | c4650 Nox Dragonkin Soldier | 46500000 `rewardItemLot_2`=6210000 -> Kat 7 Tabelle 4200300 (20 Eintraege) | 133 Eintraege, Rune of the Strong 25,0 % |
| Evergaol m49_10 | c4750 Grafted Monarch | 47509010 `rewardItemLot_2`=6200000 -> Tabelle 4200210 (15) | 125 Eintraege, Raptor Talons 2,4 % |
| Feld m46_52 | c3250 Draconic Tree Sentinel | 32500010 `rewardItemLot_2`=6110200 -> Tabellen 3000300 (68), 2000003 (34) | 132 Eintraege, Bloody Helice 1,75 % |
| Feld m46_62 | c4580 Wormface | 45803010 `rewardItemLot_2`=6200000; 45803020 `rewardItemLot_1`=6012050 | 268 Eintraege, Raptor Talons 3,39 % |
| Nacht m48_20 | c7900 Nameless King | 79000010 `rewardItemLot_2`=6210000 | 20 Eintraege, je 5,0 % (nur Dormant Powers) |
| Nacht m47_90 | c7710 Centipede Demon | 77100000 `rewardItemLot_2`=458003010, `itemLotId_enemy`=458003000 | 15 Eintraege, je 6,67 % |

Alle sechs loesen auf. Zwei Beobachtungen, die in die Anzeige gehoeren:

- Eine Figur ohne Los gibt es (z. B. c3200: 14 NpcParam-Zeilen, 0 Eintraege).
  Die Seite muss "keine Beute in den Dateien" sagen koennen.
- Einige Lose zeigen auf `ItemTableParam`-Ids, zu denen es keine Zeile gibt
  (z. B. 200200/200300/200400 aus 458003010). `walk()` bricht dort still ab;
  das verschiebt die Prozente der uebrigen Eintraege. Kein Fehler des
  Lesens, aber eine Ungenauigkeit, die der Architekt kennen sollte.

## 6. Praemissen aus dem Auftrag, nachgeprueft

| Praemisse | Ergebnis |
|---|---|
| NightBossMenuParam traegt nur Menuedaten, 18 Zeilen = 10 + 8 | **bestaetigt** (19 Zeilen, davon eine mit `sortId == DEEP_MODE_SORT`, die der Extraktor ueberspringt) |
| Kategorie 160 = vier Arena-Bosse | **widerlegt** — vier Ortskarten `m46_50/60/70/80` mit gemischter Besetzung |
| Kategorie 120 = Nachtbosse | **widerlegt** — 45 Ortskarten: 29 Ein-Boss-Plaetze (Feldbosse) + 16 Arena-Schalen. Der Nachtboss-Cast steht in `LotResultPlayAreaParam` |
| `modifier` unbenannt, `targetBoss` = Nachtfuerst | **bestaetigt**; `modifier` bleibt unbenannt, wird fuer A24 aber nicht gebraucht |
| Eingecheckter Snapshot aelter als der Extraktor (`weights` statt `counts`, kein `kinds`) | **widerlegt** — im Repo liegt gar kein Snapshot. Fester Testabzug **und** der echte Cache des Nutzers sind beide `extract_version` 12, `data_version` 10350000, mit `kinds` (19 Kategorien) und `counts`. Beispielzeile: `{'id': 1000, 'counts': [26,26,26,26,26], 'category': 100, 'group': 10, 'varies': False}`. Ein frischer Abzug war dafuer nicht noetig |

## 7. Was das fuer die Umsetzung heisst (an den `architect`)

**Stufe 1 (Feld- und Evergaol-Bosse) traegt**, aber nicht auf dem im
GOAL skizzierten Weg. Die Leseroute ist:

```
ChaosMatchingMutationEnemyTableParam  -> Ortskarten je Kategorie
LotResultSmallBaseAndSpot             -> welcher Ort unter welchem Nachtfuersten
m{AA}_{BB}_00_00.msb.dcx PARTS_PARAM_ST -> cNNNN + NpcParam-Zeilen-Id
bossdata._profile / _ladder / _defence_buffs -> HP, Stance, Schwaeche, Resistenz
extract._event_drops[str(chr)]        -> Beute
```

**Stufe 2 (Nachtbosse Tag 1/2) traegt ebenfalls** — dieselbe Route, nur der
Einstieg ist `LotResultPlayAreaParam.bossId1/bossId2` statt der
Ortslotterie. Der Auftrag hat Stufe 2 "nur nach Befund" vorgesehen; der
Befund ist positiv.

Offen bleibt nur die Bosswahl in 4 von 35 Nachtboss-Karten und in den
Kat-160-Karten (mehrere boss-grosse Figuren je Karte). Dafuer gibt es in
`bossdata` bereits `_tuned` und die Gruppenboss-Regel; ob zusaetzlich
`LotResultSmallBaseAndSpot.variationId` / `mapIndex` die Variante waehlt,
ist **nicht geprueft** (ausserhalb dieses Auftrags).

## 8. Befunde fuer den `director`

**Debt 1 — falsche Lesart im Extraktor (P2, betrifft Ausgabe an den Nutzer).**
`nrdata/extract.py:551-597` liest `smallBaseId` als Figur-Id. Belegt
widerlegt (Abschnitt 2a). Folge: der `kinds`-Block im Snapshot und die Spalte
"Examples (any map)" im Deep-of-Night-Tab (`nrplanner/depthstab.py:57-59`,
`PLAYER_GROUPS`) zeigen fuer 21 von 116 Werten einen Figurnamen, der in
Wahrheit ein Ortsname ist — und fuer 95 Werte gar nichts, obwohl der Ort
bekannt ist. Der Kommentar in `extract.py:556-566` ("names landing on real
enemies is not something a misaligned read produces") begruendet die Lesart
mit genau den 21 Zufallstreffern. Aufwand einer Korrektur: die Ortsaufloesung
ist derselbe Code, den Stufe 1 ohnehin braucht — am billigsten zusammen mit
A24, nicht davor.

**Debt 2 — Beschriftungen im Tab (P3).** `PLAYER_GROUPS` nennt Kat 101/104/
110/135-138 "Named field enemies & minibosses", 160 "Evergaol bosses", 120
"Night bosses (unconfirmed)". Nach diesem Befund sind alle drei Zeilen
falsch beschriftet (es sind Ortsarten, und 120 sind Feldbosse). Haengt an
Debt 1; getrennt zu fixen waere doppelte Arbeit.

**Kein Sicherheitsfund.** Kein Netzzugriff, kein Schreibzugriff ausserhalb
des Scratchpads, Spielinstallation nur gelesen.

**Kein Performance-Fund** im Anwendungscode. Zur Kenntnis fuer die spaetere
Umsetzung: ein Durchlauf ueber alle 199 MSB-Karten dauert rund 4 Minuten
(einmal gemessen, T-299). Stufe 1 braucht nur die ~120 Ortskarten, Stufe 2
zusaetzlich 35 — wenn das in `extract.build` landet, waechst der
Erstlauf spuerbar. Der `performance-tuner` sollte das sehen, bevor es
eingebaut wird, nicht danach.

## 9. Nachweise

Datenumlenkung in **jeder** Kommandozeile gesetzt:
`NIGHTREIGN_SETTINGS_ORG=DankYeeterT-299`,
`LOCALAPPDATA=<Scratchpad>/T-299/local`, `APPDATA=<Scratchpad>/T-299/roaming`.
Fester Testabzug nach `<Scratchpad>/T-299/local/NightreignHelper` **kopiert**
(841 Dateien, 22 MB). Kein Programmstart, kein Qt, kein `QSettings` —
`Test-Path 'HKCU:\Software\DankYeeterT-299'` = `False` nach dem Lauf,
`HKCU:\Software\DankYeeter` unberuehrt.

Skripte und Rohtabellen in `<Scratchpad>/T-299/`:

| Datei | Zweck |
|---|---|
| `q1_members.py` / `out/q1_members.json` | Member-Liste, Def-Zustand, heute gelesen |
| `q2_roster.py` / `out/q2_roster.json` | Roster je Kategorie, NpcParam-Treffer, Beute |
| `q2b_chrcheck.py` / `out/q2b_chrcheck.json` | gibt es `/chr/cNNNN.chrbnd.dcx`? |
| `q2c_smallbase.py` / `out/q2c_smallbase.json` | Figur oder Ort: die drei Gegenproben |
| `q2d_sitemsb.py` / `out/q2d_sitemsb.json` | Besetzung je Ortskarte |
| `q3_tables.py` / `out/q3_tables.json` | Def und Proben der Kandidatentabellen |
| `q4_join.py` / `out/q4_join.json` | Muster -> Ort -> Nachtfuerst |
| `q5_rest.py` | Ortsart je Kategorie, Modifier-Raeume, Beute-Stichprobe |
| `q6_nightbosses.py` / `out/q6_nightbosses.json` | wo die vier fehlenden Nachtbosse stehen |
| `q7_allmaps.py` / `out/q7_allmaps.json` | Besetzung **aller** 199 Karten |
| `q8_findmapids.py` | Wertescan ueber alle 252 Params (fand `LotResultPlayAreaParam`) |
| `q9_nightlot.py` / `out/q9_nightlot.json` | Nachtboss Tag 1/2 je Nachtfuerst |
| `q10_drops.py` / `out/q10_drops.json` | ItemLot-Kette der sechs Stichproben |
