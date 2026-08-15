---
type: Finding
okf_spec: OKF-PLAN
---
# Finding: Does #109's stale-approved display defect reproduce?

**Experiment:** EXP-003 · **Date:** 2026-08-14 · **Issue:** [#109](https://github.com/dixson3/yoshiko-flow/issues/109)

Findings are marked **[measured]** / **[inferred]** per the [#114](https://github.com/dixson3/yoshiko-flow/issues/114) convention.

## Approach Tested

#109 claims `stale_approved` is computed status-independently, so completed plans display
`⚠ STALE-APPROVED (re-review before execute)` forever. The operator reported it does not
reproduce; this experiment establishes portable evidence for that, and separates the
**mechanism** claim from the **symptom** claim.

Two checks:

1. Read the computation and render sites in `skills/yf-plan/scripts/plan_manager.py`.
2. Run `plan_manager.py list --json-output` over the 39-plan corpus and tabulate
   `(status, stale_approved)`.

## Result

### The mechanism claim is code-true **[measured]**

`_enumerate_plans()` computes the flag with no status filter (`plan_manager.py:1022-1023`):

```python
fp_status = _fingerprint_status(d)
stale = fp_status.get("stale_approved", False)
```

and `list_plans()` renders it with no status filter (`plan_manager.py:1069`):

```python
stale_tag = "  ⚠ STALE-APPROVED (re-review before execute)" if p.get("stale_approved") else ""
```

Neither site consults `status`. #109's description of the code is accurate.

### The symptom does not reproduce — 0/38 **[measured]**

```
  status=complete     stale_approved=False  n=38
  status=investigating stale_approved=False  n=1
complete plans showing stale: []
```

Every completed plan in the corpus reports `stale_approved: false`. No plan displays the tag.

### Why it does not fire **[inferred]**

Nothing written after approval perturbs the fingerprint. The fingerprint excludes all
`**Field:**` header lines (so `update-status`'s status flip is outside it) and the phase log now
lives in the separate `log.md` (so completion entries are outside it too). A plan that completes
normally therefore keeps `stored == current`, and the status-independent branch is never reached.

## Implications for Plan

1. **#109 is a latent defect, not an active one.** The status-independence is real; the display
   path is unreachable in normal operation because completion cannot invalidate the fingerprint.
   "Does not reproduce" is accurate; "is not a bug" would not be.
2. **The residual exposure is narrow**: a plan whose content is edited after completion — e.g. a
   `--force`d post-hoc revision — would display the tag with no way to clear it. No such plan
   exists in the corpus.
3. **Correct disposition is close-with-evidence**, recording the mechanism/symptom split so a
   future encounter is not re-diagnosed from scratch. This plan files no execution bead for it.

## Recommendations

- Close #109 with the measurement above and the mechanism/symptom distinction stated explicitly.
- Do not silently close: the code-level claim is correct and worth preserving for whoever hits
  the narrow post-completion-edit case.
