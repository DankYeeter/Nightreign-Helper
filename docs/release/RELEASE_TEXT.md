# Release description — fixed text

This file now holds **two** variants of the text the `release-manager`
inserts into a GitHub release description. They are not interchangeable —
read the heading before you copy anything.

- **Variant A** is for every release from here on (`v1.8.0` and later): the
  `release.yml` workflow already attaches the notice package
  (`NightreignHelper-notices.zip`) and computes a checksum, so Variant A
  keeps both.
- **Variant B** exists only because of `docs/legal/C-004.md` (Auflage A-033):
  the twelve releases `v1.0.0`–`v1.7.1` were published between 2026-08-11 and
  2026-08-24 **without** a notice package. Variant B is the text for
  backfilling those twelve — and only those twelve. It differs from
  Variant A in exactly two ways: no checksum paragraph (the old
  `NightreignHelper.exe` assets have no `.sha256` file, and nothing here
  should imply one exists), and one added, dated sentence at the top saying
  the notice package was attached after the fact. Everything else is
  identical wording to Variant A.

Neither variant should be shortened or reordered internally; the order
follows `docs/legal/C-003.md`, section "Was der `technical-writer` von mir
braucht", T2. In both variants, everything between the `---` markers is the
literal text block; the surrounding notes are for whoever pastes it in, not
part of the release description itself.

Satisfies A-023, A-024, A-028 (`docs/legal/AUFLAGEN.md`) for both variants;
Variant B additionally satisfies the T2 half of A-033.

---

## Variant A — every release from `v1.8.0` onward (unchanged asset flow)

---

**Not affiliated.** Nightreign Helper is an unofficial fan project. It is not
affiliated with, endorsed by, sponsored by, or approved by FromSoftware, Inc.
or Bandai Namco Entertainment Inc. ELDEN RING NIGHTREIGN, its data, artwork,
text and trademarks are the property of their respective owners.

**What this program does.** It reads and decrypts, locally, the game files
and the save data of an installed copy of ELDEN RING NIGHTREIGN, using
decryption keys that have been publicly known in the modding community for
years. To open the game's own archives it also runs a small decompression
program out of that installation folder — a library that ships with the game
itself, not something this project adds. On first run it asks you to point it
at a copy of the game you trust, which for almost everyone is simply the one
they play. It never writes to the game or to the save file, and it makes no
network connection.

This executable contains no game data; it reads your own installation.

**Before you run it:** back up your save. This tool opens it read-only and
is not known to write to it, but it is provided "AS IS", under the MIT
licence, without warranty of any kind.

**Licence notices.** A notice package with the full licence text of every
bundled component — including Qt, used here through PySide6 under the
LGPL-3.0 — is attached to this release as `NightreignHelper-notices.zip`
(it contains `THIRD_PARTY.md`, the `licenses/` texts, `LICENSE`, and
`vendor/Paramdex/NOTICE`). Read it before redistributing this executable
yourself.

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

## Variant B — backfill for `v1.0.0`–`v1.7.1` only (A-033)

---

**Notice package added after the fact.** The licence notice package
(`NightreignHelper-notices.zip`) and this description text were attached to
this release on <BACKFILL_DATE>. The `NightreignHelper.exe` file attached to
this release is unchanged from the original upload.

**Not affiliated.** Nightreign Helper is an unofficial fan project. It is not
affiliated with, endorsed by, sponsored by, or approved by FromSoftware, Inc.
or Bandai Namco Entertainment Inc. ELDEN RING NIGHTREIGN, its data, artwork,
text and trademarks are the property of their respective owners.

**What this program does.** It reads and decrypts, locally, the game files
and the save data of an installed copy of ELDEN RING NIGHTREIGN, using
decryption keys that have been publicly known in the modding community for
years. To open the game's own archives it also runs a small decompression
program out of that installation folder — a library that ships with the game
itself, not something this project adds. On first run it asks you to point it
at a copy of the game you trust, which for almost everyone is simply the one
they play. It never writes to the game or to the save file, and it makes no
network connection.

This executable contains no game data; it reads your own installation.

**Before you run it:** back up your save. This tool opens it read-only and
is not known to write to it, but it is provided "AS IS", under the MIT
licence, without warranty of any kind.

**Licence notices.** A notice package with the full licence text of every
bundled component — including Qt, used here through PySide6 under the
LGPL-3.0 — is attached to this release as `NightreignHelper-notices.zip`
(it contains `THIRD_PARTY.md`, the `licenses/` texts, `LICENSE`, and
`vendor/Paramdex/NOTICE`). Read it before redistributing this executable
yourself.

---

## Notes for whoever pastes this in (not part of either release text)

**Which variant goes where.** Variant A for the thirteenth release and every
one after it. Variant B for each of the twelve existing releases
(`v1.0.0`–`v1.7.1`) — paste it at the very **start** of that release's
existing description; do not remove or edit whatever GitHub-generated notes
are already there below it (`generate_release_notes` output, prior manual
edits). Per A-033 this goes together with uploading
`NightreignHelper-notices.zip` as an asset to that same release.

**`<BACKFILL_DATE>` (Variant B only).** Replace with the date you actually
run the upload/edit for *that* release, in `YYYY-MM-DD` format (e.g.
`2026-09-10`). Each of the twelve releases gets the date you touch it, not
one shared date and not the release's original 2026-08 date — C-004 is
explicit that backdating is out (Befund 2, "Kein Rückdatieren"). If you do
all twelve in one sitting the date will likely be identical across all of
them; that is a coincidence of timing, not an instruction to hardcode one
value.

**Where A-020's asset actually lives (corrected 2026-09-07).** The prior
version of this file had a note here saying the "attached ... as
`THIRD_PARTY.md`" sentence described "what should be true, not what is",
because A-020 (the workflow step that builds and attaches the package) was
still open. It has since been closed by T-109
(`.github/workflows/release.yml`, step "Package licence notices"): the
asset is a zip named `NightreignHelper-notices.zip`, not a bare
`THIRD_PARTY.md`. Both variants above already say so. That note is now
obsolete and has been removed rather than left to contradict the text next
to it.

**T1 naming — checked, nothing to change (T-112).** `docs/legal/C-004.md`
asks whether the notice package needs a version-independent name, since one
package is now attached to twelve different releases plus every future one.
Checked both places this could go wrong:

- The asset itself, `NightreignHelper-notices.zip` (set by `developer` in
  T-109), carries no version number in its name — it already works
  unchanged as an attachment to any release, old or new.
- `THIRD_PARTY.md`'s own text never claims to belong to one specific release
  version; it describes "the notice package for the released executable" in
  general terms and lists *component* versions (PySide6 6.11.1 and so on),
  not a project release version.

So: **nothing to change** in either file for version-independence — neither
one holds itself out as belonging to a single version.

One related thing this file does **not** do, on purpose: C-004's T1
requirement (section "Anforderungen an T1 bis T4") also suggests adding a
sentence to the notice package itself along the lines of "applies to
releases v1.0.0 through v1.7.1 and later; the bundled components and
versions are the same in all these builds" — conditional on the
`release-manager` confirming that's actually true. C-004's own "nicht
geprüft" list says the built `.exe` files themselves were never opened, only
the source trees at two of the twelve tags (`v1.0.0`, `v1.7.1`); the
identical-versions claim rests on the assumption that each build followed
its own `requirements.txt` exactly. Writing that sentence into
`THIRD_PARTY.md` as settled fact is not something this role can stand
behind without that verification, and it belongs in `THIRD_PARTY.md`
content, which is `developer`/`release-manager` territory once there is
something to verify against, not a rewording call. If the `release-manager`
does confirm the twelve builds matched, that sentence can be added then —
this file does not block it, and does not pre-empt it.
