---
type: Finding
okf_spec: OKF-PLAN
description: 'exp-003 - restore --apply after the backfill is committed causes silent total loss, a fourth data-loss path'
---

# exp-003: `restore --apply` on a committed backfill is silent total loss

## Approach Tested

Discovered by red-team pass 2 and **independently reproduced in the main session**. The sequence is
the one a pass-1 remediation created: commit a base, run `backfill --apply --record`, **commit the
backfill**, then run `restore --record --bundle <one> --apply`. A control ran the identical
sequence *without* the intermediate commit.

Sandbox only (`mktemp -d` + `git init` + commit). The real corpus was never touched.

## Result

**measured:** the committed path reports success and destroys the bundle.

| Step | Bundle contents |
| :-- | :-- |
| before | `context.md findings plan.md README.md references reviews upstream-triage.md` |
| after `backfill --apply` | `context.md findings index.md log.md plan.md references reviews upstream-triage.md` |
| after commit + `restore --apply` | `context.md findings plan.md references reviews upstream-triage.md` |

`restore` returned **`verdict: pass`, `exit: 0`**. The bundle ends with **no `README.md`, no
`index.md`, no `log.md`** — every artifact carrying the bundle's orientation is gone.

**measured:** the control — same sequence, no intermediate commit — restores `README.md` correctly
and returns the bundle to its original file set. **The defect is created precisely by the commit.**

### Mechanism

Verified by reading `skills/yf-okf-hygiene/scripts/okf_hygiene.py:1362-1372`:

1. Committing the backfill removes `README.md` from `HEAD` and adds `index.md`/`log.md` to it.
2. `_tracked_at_head` still finds `plan.md` (kind `modified`) at `HEAD`, so `recoverable` is
   non-empty and **REFUSAL 2 does not fire** — the guard that exists for exactly this class.
3. The `created` unlink pass (`:1367`) deletes `index.md` and `log.md`.
4. `git checkout -- README.md` (`:1371-1372`) **fails**, because `README.md` is no longer in
   `HEAD` — and the call is `subprocess.run(..., capture_output=True)` whose **return code is
   never checked**.

Step 4 is what makes it silent. The reversal reports success because nothing ever asked whether it
worked.

## Implications for Plan

- This is a **fourth** silent data-loss path in `restore`, distinct from the three plan-064
  repaired. The engine is less trustworthy than its post-plan-064 state suggested.
- It is reachable **only** through the commit-then-restore ordering, which is why plan-064's
  rehearsals never saw it: they restore an uncommitted tree.
- **The plan's response is ordering, not an engine change** (SC12 forbids engine edits here):
  Issue 4.4 runs `restore` on the uncommitted post-apply tree; Issue 4.5 commits afterwards.
- **Post-commit, the reversal verb is `git revert`** (D5) — never `restore`.
- It also invalidated a criterion: the first draft of Issue 0.4d asserted pre- and post-reversal
  tree hashes were **equal**, which is what a **no-op** restore produces. That checker would have
  reported green on exactly this failure.

## Recommendations

1. Order Issue 4.4 before Issue 4.5 — done.
2. Assert the real round-trip invariant in 0.4d: `post_backfill == post_reapply` and
   `post_reversal == pre_backfill` and `post_reversal != post_backfill` — done.
3. File the unchecked `git checkout` return code as a fourth engine defect (Issue 6.1). The
   narrow fix is to check the return code and fail loudly; the broader one is to make REFUSAL 2
   require that **every** `deleted`-kind path be recoverable, not merely that some path is.
