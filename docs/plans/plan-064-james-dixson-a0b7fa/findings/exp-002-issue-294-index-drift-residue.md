---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-002 - reproduce and characterize GitHub 294 (okf index drift enumerates build residue), find the minimal correct fix, and determine its ordering. Verdict - 294 must land before backfill --apply.'
---
# EXP-002: #294 — index drift enumerates build residue

**Verdict: the fix is ~27 hand-written LOC in the engine, and it MUST land before
`backfill --apply`.** Running the backfill first bakes residue-derived bullets into 8 committed
`index.md` files, which then become permanent `ghost` findings on *every* clone.

## Approach Tested

**measured:** Read #294 in full, then the check (`scripts/checks/check_okf_index_drift.py`) and its
delegate in `_shared/okf.py` (`reindex_check` -> `_listing_members` -> `_recursive_file_count` /
`_nested_files`). Ran the check on the working clone. Built a sandbox repository, copied a real
bundle into it, took a clean baseline, then injected `scripts/__pycache__/*.pyc`, `.DS_Store`, and an
untracked `scratch-notes.md`.

Prototyped the fix (a `_vcs_ignored()` helper threaded through the walk) and ran an equivalence and
timing sweep over all 68 live bundles, plus three edge cases: a non-git tree, a tracked-but-ignore-
matching file, and residue baked in then deleted. Traced the backfill path and the governing SPEC.

**inferred:** the clean-clone green is what makes this defect durable — it is invisible exactly where
people look for it, and only fires on a working clone that has run something.

Residue: none. Sandbox removed; `git status --porcelain` empty; drift check still exit 0.

## Result

### What is actually enumerated

The driver does **not** enumerate members. It globs **bundle roots** at depth 1 and delegates
per-bundle judgement to `okf.reindex_check()` → `_shared/okf.py:_listing_members()`, which walks
the **filesystem** with `Path.iterdir()` and filters on exactly three predicates:

```python
# _shared/okf.py:1584 (_listing_members)
    for child in sorted(bundle.iterdir()):
        if child.name in RESERVED_FILES or child.name.startswith("."):
            continue
        if is_excluded(child.name + ("/" if child.is_dir() else ""), exclude_globs) \
                or is_excluded(child.name, exclude_globs):
            continue
```

Repeated verbatim in `_recursive_file_count` (:1490) and `_nested_files` (:1511).
**There is no version-control awareness anywhere on this path** — `subprocess` is not even
imported in `_shared/okf.py`.

The driver *is* git-aware, but only at root level, on the bundle dirs it globbed:
`check_okf_index_drift.py:202` → `ignored = git_ignored(root, bundles)` — **bundles, not
members.** That is the whole defect: the gitignore-awareness stops one level above where it is
needed.

### Reproduction

Green on this clone because **no residue currently exists**, not because a fix landed:

```
$ uv run scripts/checks/check_okf_index_drift.py --min-roots 30
 "bundles_checked": 68, "with_index": 60, "no_index": 8, "drifting": 0, "verdict": "clean"
$ find docs/plans docs/research -name '__pycache__' -o -name '*.pyc' -o -name '.DS_Store'
(no output)
```

Sandbox repro — inject `scripts/__pycache__/*.pyc`, `.DS_Store`, untracked `scratch-notes.md`:

```json
{ "drifting": 1, "verdict": "drift", "exit": 1,
  "counts": { "ghost": 0, "missing": 2 },
  "findings": [ { "kind": "missing", "entry": "scratch-notes.md" },
                { "kind": "missing", "entry": "scripts/__pycache__/finding_recurrence.cpython-311.pyc" } ] }
```

Two refinements #294 does not state:

- **`.DS_Store` is already safe** — `startswith(".")` covers it at every level, as it does
  `.pytest_cache/`. What actually leaks is `__pycache__/` and `*.pyc` (non-dot names) plus any
  untracked non-dot scratch file.
- **Rule D amplifies it.** Residue counts toward the `<= K` recursive bound, so it can flip a
  `sub/` stub into a fully enumerated directory — a second, quieter drift signal.

### The producer is affected too, and worse — the defect is BIDIRECTIONAL

`reindex_write` (`_shared/okf.py:1834`) uses the same `_listing_members`:

```
$ uv run _shared/okf.py reindex docs/plans/bundle-a --write
  add-missing: scripts/__pycache__/finding_recurrence.cpython-311.pyc
$ grep -n pycache docs/plans/bundle-a/index.md
108:- [scripts/__pycache__/...pyc](scripts/__pycache__/...pyc)
```

Once that line is **committed**, deleting the residue (i.e. a fresh clone) inverts the polarity
permanently: `"counts": {"ghost": 2, "missing": 0}` — red on **every** clone, including the
clean one, until 8 `index.md` files are hand-edited.

**Dirty clone → `missing`. Residue baked in, then cleaned → `ghost`, forever.** This is the
load-bearing fact for the ordering decision.

### Ignored, not untracked — and the distinction picks the fix

Strictly neither: the code has no git awareness at all, so it enumerates *every* filesystem
entry. But the two candidate fixes are **not** equivalent:

- `scratch-notes.md` in the repro is **untracked and not ignored**, and the check **correctly**
  flagged it. A tracked-files-only fix (`git ls-files`) would suppress it — and would break
  ordinary authoring, because the FAST tier fires **on edit**, when a newly authored
  `findings/foo.md` is by definition untracked. Filtering on tracked-ness makes the check
  structurally unable to see the drift it exists to catch.
- Filtering on **ignored** removes exactly the residue and nothing else.

The SPEC is imprecise the same way and should be corrected in passing: REQ-OKF-CHK-004 says
"gitignore-aware, so an **untracked** scratch directory is never enumerated" — the mechanism is
*ignored*, not *untracked*.

### The fix (prototyped and measured)

Engine-side, **not** driver-side. In `_shared/okf.py`, computed **once per bundle** at the top
of `_listing_members` and threaded into `_recursive_file_count`/`_nested_files` so the count arm
and the enumerate arm agree:

```python
def _vcs_ignored(bundle: Path) -> frozenset:
    """Bundle-relative posix paths under `bundle` that version control IGNORES."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(bundle), "ls-files", "-o", "-i", "--exclude-standard", "-z",
             "--", "."], capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            return frozenset()
        return frozenset(x for x in proc.stdout.split("\0") if x)
    except Exception:
        return frozenset()          # FAIL-OPEN
```

**`git ls-files -o -i --exclude-standard`, not the issue's proposed `git check-ignore`:** `-o`
(others) means a **tracked** file can never appear, so a deliberately committed member is
structurally undroppable — and it is one call per bundle, not a per-path query.

| Property | Measurement |
| :-- | :-- |
| Fixes the defect | `missing` `2 → 1`; survivor is `scratch-notes.md` (untracked, not ignored) — the correct discrimination |
| No-op on the clean corpus | over all **68** live bundles, `set(old) ^ set(new)` differed in **0** |
| Cost | `0.070s → 1.324s` for 68 bundles (~18 ms/bundle, one `git` fork each) |
| Tracked file matching an ignore pattern | force-added `scripts/deliberate.pyc` → still a member |
| Outside a git work tree | `frozenset()` → members still include the pyc; **fail-open** |

**Rejected alternatives.** An explicit exclude list is forbidden by `OKF-EXTENSION.md` §3b's own
text — "These are the fixture carve-outs, and NOTHING ELSE. … Adding a row to silence a finding
on a live bundle member converts the conformance check into a record of what someone did not
want to look at." Keep only a tiny **hardcoded floor** (`__pycache__/`, `*.pyc`, ~4 LOC) to
cover the fail-open non-git case — defense in depth, not a substitute, and **not** in §3b.

**Size:** 1 hand-edited file (`_shared/okf.py`: +1 import, +18 helper, ~8 threading ≈ **+27
LOC**), then `uv run _shared/sync.py` regenerates the 5 vendored copies. With test + SPEC,
~9 files / ~60 LOC. **`check_okf_index_drift.py` itself needs no change.**

### Why #294 must land FIRST — three measured mechanisms

1. **`backfill --apply` regenerates the index through the defective enumerator.**
   `okf_hygiene.py:486`: `for member in okf._listing_members(bundle):` inside
   `_render_backfilled_index`. And `:539`: `shutil.copytree(bundle, j.staging)` — a **full**
   copy, residue included.
2. **The 8 targets are currently INVISIBLE to the check, and the backfill makes them visible.**
   They are exactly the driver's `"no_index": 8`; today they short-circuit at
   `verdict: no-index` before any member walk. Writing an `index.md` enters them into the judged
   set for the first time.
3. **The damage is durable, not transient** — the `ghost` inversion above. Backfilling first
   converts a machine-local nuisance into a committed corpus defect.

The backfill's own new artifacts are safe: `index.md`/`log.md` are in `RESERVED_FILES` and
skipped as members.

### Adjacent hazard found while measuring

`okf_hygiene`'s scaffolding lives at `docs/plans/.okf-hygiene-staging/` and
`.okf-hygiene-journal/` — **inside** the `docs/plans/*` root glob. `pathlib.Path.glob('*')`
**does** match dotted names (measured: `pathlib → ['.hidden','normal']` vs `glob.glob →
['normal']`). `Journal.clear()`'s own docstring records this already cost `64 → 66` enumerated
bundles. On a **halt or crash the scaffolding survives**, and it is untracked-**but-not-ignored**,
so the driver's root-level `git_ignored()` filter will not drop it either. Add `.okf-hygiene-*`
to `.gitignore` alongside this work.

### SPEC governance: a requirement exists, and is already half-implemented

`skills/yf-okf/SPEC.md:355` (REQ-OKF-CHK-004), verbatim:

> **The exclusion source is REQ-OKF-CHK-003's §3b**, not a second list. The driver shall
> additionally be **gitignore-aware**, so an untracked scratch directory is never enumerated.

Implemented **only at root granularity**; the member walk it delegates to has none. The
requirement is scoped to "the driver" while the defective code is the **engine**
(`_listing_members`, governed by **REQ-OKF-012(a)**, `skills/yf-okf/SPEC.md:518`, which says
nothing about version control). SPEC-first therefore needs an amendment that:

- extends **REQ-OKF-012(a)** so rule D's recursive walk skips VC-ignored paths at every level,
  binding **producer and checker** to one predicate — the code's own warning at `okf.py:1571`:
  *"Producer and checker must agree on this predicate or the producer's correct output reads as
  `missing` here"*; and
- corrects REQ-OKF-CHK-004's "**untracked**" → "**ignored**".

### Tests that prove it

- **`_shared/test_okf.py`** (75 tests; rule-D arms at :1300–:1362). Add a `tmp_path` test that
  `git init`s, ignores `__pycache__/`, creates `scripts/__pycache__/x.pyc` **and** an
  untracked-not-ignored `scratch.md`, and asserts **both halves**: the pyc is absent **and**
  `scratch.md` is present. *Asserting only the first half is satisfied by the wrong fix.* Plus
  arms for fail-open (outside a work tree) and a force-added `.pyc`.
- **`scripts/checks/check-drift-driver-contract.sh`** (REQ-OKF-CHK-004; 3 arms today,
  `grep -n 'ignore'` → **no matches**). Add **arm 4**: on the `git init`ed `${FIX}` fixture, drop
  a `__pycache__/x.pyc` into `corpus/bundle-a/` and assert the driver still exits 0. The driver's
  contract check has **no gitignore arm at all**, which is why "shall be gitignore-aware" could
  be half-implemented undetected.

**Residue:** none. Sandbox removed; `git status --porcelain` empty; drift check still exit 0.

## Implications for Plan

**Ordering is not free: #294 must land before `okf_hygiene.py backfill --apply`.** The two are
coupled through `_listing_members`, and running the backfill first writes residue-derived bullets
into 8 committed `index.md` files that later become permanent `ghost` findings on every clone,
including a clean one.

- The fix is **engine**-side, not driver-side, so it lands in `_shared/okf.py` and needs a
  `_shared/sync.py` run — one hand edit fans out to 6 files mechanically.
- It is **SPEC-first work**: the governing requirement exists but under-specifies the member walk, so
  an amendment sequences ahead of the code.
- Risk is low: the prototype is a **measured no-op** across all 68 live bundles. The only behavioural
  asymmetry is the deliberate fail-open outside a git work tree.
- Cost is a real but small FAST-tier regression (~1.25 s over the corpus, ~18 ms/bundle).

## Recommendations

1. **Land #294 first, in this order:** SPEC amendment (REQ-OKF-012(a) plus the REQ-OKF-CHK-004
   "untracked" -> "ignored" correction) -> `_shared/okf.py` `_vcs_ignored()` and threading ->
   `uv run _shared/sync.py` -> tests -> *then* any `backfill --apply`.
2. **Use `git ls-files -o -i --exclude-standard -z`, not `git check-ignore`** (the issue's proposal):
   one call per bundle, and `-o` makes a tracked member structurally undroppable.
3. **Fail open, backed by a tiny hardcoded floor** (`__pycache__/`, `*.pyc`) so a bundle copied
   outside a work tree — the OKF portability case the engine explicitly supports — is still
   protected. Do **not** put these in `OKF-EXTENSION.md` §3b; that section's own text reserves it for
   fixture carve-outs.
4. **Test both halves** — ignored residue is dropped **and** untracked-but-not-ignored members are
   still flagged. A one-sided test passes for the wrong fix.
5. **Add arm 4 to `check-drift-driver-contract.sh`.** The driver's contract check has no gitignore arm
   at all, which is why "shall be gitignore-aware" could be half-implemented undetected.
6. **Sweep the corpus for residue immediately before any `--apply`**, and add `.okf-hygiene-staging/`
   and `.okf-hygiene-journal/` to `.gitignore` — they sit inside the `docs/plans/*` root glob, survive
   a halt, and are untracked-but-not-ignored, so the driver's root filter misses them.
