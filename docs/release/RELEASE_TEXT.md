# Release description — fixed text

This is the text the `release-manager` inserts into every GitHub release
description, unchanged, because `generate_release_notes` only lists commits
and covers none of the points below. Do not shorten or reorder it; the order
follows `docs/legal/C-003.md`, section "Was der `technical-writer` von mir
braucht", T2. Everything between the `---` markers is the literal text block;
the surrounding notes are for whoever pastes it in, not part of the release
description itself.

Satisfies A-023, A-024, A-028 (`docs/legal/AUFLAGEN.md`).

---

**Not affiliated.** Nightreign Helper is an unofficial fan project. It is not
affiliated with, endorsed by, sponsored by, or approved by FromSoftware, Inc.
or Bandai Namco Entertainment Inc. ELDEN RING NIGHTREIGN, its data, artwork,
text and trademarks are the property of their respective owners.

**What this program does.** It reads and decrypts, locally, the game files
and the save data of an installed copy of ELDEN RING NIGHTREIGN, using
decryption keys that have been publicly known in the modding community for
years. It never writes to the game or to the save file, and it makes no
network connection.

This executable contains no game data; it reads your own installation.

**Before you run it:** back up your save. This tool opens it read-only and
is not known to write to it, but it is provided "AS IS", under the MIT
licence, without warranty of any kind.

**Licence notices.** A notice package with the full licence text of every
bundled component — including Qt, used here through PySide6 under the
LGPL-3.0 — is attached to this release as `THIRD_PARTY.md` (plus the
`licenses/` texts and `vendor/Paramdex/NOTICE`). Read it before
redistributing this executable yourself.

**Checksum.** Verify the download against the attached
`NightreignHelper.exe.sha256` before you run it:

```
Get-FileHash NightreignHelper.exe -Algorithm SHA256
```

or, without PowerShell:

```
certutil -hashfile NightreignHelper.exe SHA256
```

The value must match the one in `NightreignHelper.exe.sha256`.

---

## Notes for whoever pastes this in (not part of the release text)

- The attachment list in the third paragraph above assumes A-020 is closed —
  today it is not (`.github/workflows/release.yml` `files:` lists only
  `dist/NightreignHelper.exe` and `dist/NightreignHelper.exe.sha256`, checked
  2026-09-07). Until the notice package is actually attached as a release
  asset, that sentence describes what should be true, not what is. Fixing
  the attachment is `developer`/`release-manager` work (A-020), not a text
  change — do not edit the sentence to make it match an unfixed workflow.
- This file intentionally contains no explanation of *why* distribution is
  legally permitted (A-019): no citation, no paragraph of reasoning. If
  someone is tempted to add one here, don't — that reasoning lives in
  `docs/legal/`, not in a release description.
