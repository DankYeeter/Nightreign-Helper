"""The differential track: ask two trees the same question and diff the answers.

A developer tool, not part of the test suite. It was rebuilt from scratch five
times between AD-019 W0 and W3 -- three times by the `developer`, twice by the
`qa-engineer` -- and every rebuild produced numbers nobody else could re-run
(QA-075). It lives here now so that a figure in a report carries its recipe.

Four steps, four scripts, and they are separate because each one is a
different kind of failure:

* `plan.py`     a raster file -> concrete cases, ids resolved **once**
* `capture.py`  a plan -> what the three display layers say, one tree
* `compare.py`  two captures -> what moved, and everything it cannot place
* `mutate.py`   one named edit to a tree, to show a guard has teeth

The raster is a **file** (`rasters/*.json`), not a constant inside a script.
That is the part that makes two runs comparable: "38 787 of 25 102" and
"10 276 of 19 392" cannot be reconciled unless the grid behind each number can
be read. The plan the raster expands to carries its own case count, so a
report can name the raster and the number is reproducible.

Why the ids are resolved once, in `plan.py`, and not per tree: a query like
"the two lowest-numbered effects that move the physical attack rate" is
answered by the code being measured. Re-running it on the second tree could
pick something else, and the diff would then be measuring the query rather
than the change.

## Running it

Outside pytest, by its own entry points -- deliberately, not by a marker:

1. a sweep over every armament costs minutes, and pytest markers are opt-out
   by convention here (`-m "not slow"`), which is the wrong default for a
   tool that is never part of an acceptance run;
2. it needs **two trees**, and the second one is not the tree pytest was
   started in. `capture.py --tree` puts a different tree on `sys.path` and
   checks that it really imported from there -- inside a pytest process the
   tree under test is already imported and that check could not hold;
3. `PYTHONHASHSEED` has to be set before the interpreter starts. Without it
   the comparison lies: the same tree in two processes came back with 5 802
   of 11 718 armament tiles differing, purely from set iteration order
   (measured 2026-09-02). `capture.py` refuses to run without it rather than
   producing a plausible wrong number -- and the refusal reads `sys.flags.
   hash_randomization`, the interpreter's own record of how it started,
   never `os.environ`. The environment variable can still be poked after the
   interpreter has already started unseeded, and a check that trusted it
   would pass in exactly that state (QA-079 a).

A full run, old tree against new:

    git archive <old-rev> | tar -x -C /tmp/old
    export PYTHONHASHSEED=0
    python scripts/differential/plan.py \
        scripts/differential/rasters/tiles_and_panel.json -o /tmp/plan.json
    python scripts/differential/capture.py /tmp/plan.json -o /tmp/new.jsonl
    python scripts/differential/capture.py /tmp/plan.json -o /tmp/old.jsonl \
        --tree /tmp/old
    python scripts/differential/compare.py /tmp/old.jsonl /tmp/new.jsonl

`compare.py` exits non-zero when anything differs in a field that was not
named as expected, and prints those records in full. That property -- it
spits out everything it cannot place -- is what made the W3 measurement
usable, and it is the one thing not to trade away for a tidier report.
"""
