# Where these defs come from

Most of this directory is **Paramdex** (`soulsmods/Paramdex`), vendored as the
project's field schemas. See `HANDOVER.md` §1a for the open licence question
about that collection — it ships no LICENSE file.

**Nine defs are not from Paramdex.** They were taken from **Smithbox**
(`vawser/Smithbox`, `src/Smithbox.Data/Assets/PARAM/NR/Defs/`, fetched
2026-08-16), which is **MIT licensed**. Paramdex has no def for any of them,
and each one was a param this project had been reading byte by byte:

    ChaosMatchingRankControlParam          (closed OPEN_QUESTIONS item 5.3)
    ChaosMatchingMutationCategoryParam
    ChaosMatchingMutationEnemyTableParam
    ChaosMatchingCorrectParam
    ChaosMatchingReplaceTreasureCommon     (not yet read)
    ChaosMatchingReplaceTreasureTable      (not yet read)
    SessionRewardByModeRankParam
    SessionRewardCommonParam               (not yet read)
    AttachEffectFilterSubCategoryParam     (not yet read)

**Their field names are not automatically trusted.** Two are demonstrably
wrong against the data and the extractor overrides them, with the reasoning
recorded at the point of use in `nrdata/extract.py`:

- `ChaosMatchingMutationEnemyTableParam.smallBaseId` is a **character** id,
  not a `SmallBaseAndSpotDefine` row (values 2000-5391 against that table's
  100-2219; 2 of 116 would resolve, against 21 that resolve as characters
  into thematically correct rosters).
- The same param's `mapUnk_1/2/3` are one packed-decimal **map tile** id
  (`60|XX|YY` -> `m60_4X_3Y`), which the def does not attempt to name.

Take the structure, verify the names. See `OPEN_QUESTIONS.md` §23.
