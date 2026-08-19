---
type: Note
okf_spec: OKF-PLAN
---

# `nested-reach` — the glob-depth regression fixture (Issue 2.2)

`bad.md` sits one directory deeper than a `findings/*.md` glob can reach. It exists so the
single-level-glob regression is caught **by test**, not by inspection.

A single-level `docs/plans/*/findings/*.md` reaches **0** of the 45 nested
`okf-migration-samples/**` files, which meant the carve-out being tested was never exercised:
`control_fired: false` was the right answer for the wrong reason. Reverting the glob to its
single-level form must make `test_doc_lint.py` fail on the assertions below.
