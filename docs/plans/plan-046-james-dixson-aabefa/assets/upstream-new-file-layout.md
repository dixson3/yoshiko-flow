TITLE: yf-plan README.md File Layout block is stale — 29 omissions including SPEC.md, OKF-EXTENSION.md, and test-harness/

BODY:
Split out of #118 by plan-046 Issue 5.4. Same file, different defect — folding it into #118 would have made #118 unreviewable.

#118 was about `README.md` still naming `README.md` as the plan-folder orientation surface (fixed). **This** is the skill-dir **File Layout** block at `skills/yf-plan/README.md:106-138`, which purports to be a complete listing of the skill directory and is not.

**Measured** (walk of `skills/yf-plan`, excluding dotfiles and `__pycache__`):

| measure | value |
| :-- | --: |
| files actually in `skills/yf-plan/` | **70** |
| filenames listed in the File Layout block | 23 |
| **omitted** | **29** |
| of which under `scripts/` | **24** |
| `scripts/` top-level files on disk | 23 |

**Named omissions that matter most:**
- **`SPEC.md`** — the skill's own specification is absent from its file layout.
- **`OKF-EXTENSION.md`** — the OKF-PLAN member definition (`REQ-OKF-FAM-003` resolves it by convention at this exact path).
- **`test-harness/`** — an entire top-level directory (3 files), unlisted.
- **`README.md`** — the file does not list itself.
- **`okf.py`** — the vendored OKF engine, one of the four copies `_shared/sync.py` regenerates.
- **`close_cascade.py`**, **`repair_dangling_epics.py`**, **`bootstrap.sh`**, **`smoke.sh`**, `BASELINE.json`, `MANIFEST.json`, `ci-release-completion.md`, and **17 `test_*.py` files**.

The block lists exactly three `scripts/` entries (`plan_manager.py`, `test_worktree.py`, `manifest_update.py`) against 23 on disk.

**Why this is worth its own issue rather than a quiet edit.** `DRIFT-CHECK.md` declares an `e-readme-layout` edge whose contract is `field-set-equal`: *"the skill README file-layout fence lists exactly the files `find skills/<skill> -type f` reports."* The edge exists, the manifest is approved, and the block is nonetheless 29 files short — so this is also evidence about **that edge's** firing or scope, not only about the README. Whoever fixes the listing should check why the edge did not catch it, or this recurs.

Found while executing plan-046 (`docs/plans/plan-046-james-dixson-aabefa/`), which fixed the four #118 sites in the same file. Tracker: #167.
