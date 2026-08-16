Closing this after re-testing it against the full plan corpus in plan-039. The short
version: **the mechanism you described is real, but the path that would display it is
unreachable, so the symptom does not occur.** Closing on that distinction rather than
silently — the code observation was correct and is worth keeping on record.

## The mechanism claim is code-true

`stale_approved` is computed and rendered with no status filter, exactly as reported.

`_enumerate_plans()` (`skills/yf-plan/scripts/plan_manager.py:1022-1023`):

```python
fp_status = _fingerprint_status(d)
stale = fp_status.get("stale_approved", False)
```

`list_plans()` (`plan_manager.py:1069`):

```python
stale_tag = "  ⚠ STALE-APPROVED (re-review before execute)" if p.get("stale_approved") else ""
```

Neither site consults `status`. Nothing in the code prevents a `complete` plan from
carrying the tag.

## The symptom does not reproduce — 0 of 38

Running `plan_manager.py list --json-output` over the corpus and tabulating
`(status, stale_approved)`:

```
  status=complete      stale_approved=False  n=38
  status=investigating stale_approved=False  n=1
complete plans showing stale: []
```

Every completed plan reports `stale_approved: false`. No plan displays the tag — not one,
ever, across the whole corpus.

## Why the branch is unreachable

Nothing written *after* approval perturbs the fingerprint:

- the fingerprint excludes all `**Field:**` header lines, so `update-status`'s status flip
  to `complete` is outside it;
- the phase log now lives in a separate `log.md`, so completion entries are outside it too.

A plan that completes normally therefore keeps `stored == current`, and the
status-independent branch is never reached. The status filter you identified as missing is
missing — it simply has nothing to filter, because the flag it would guard is always false
by the time status could matter.

## Residual exposure

This is **latent, not absent**. The branch becomes reachable if a completed plan's *content*
is edited after the fact — specifically a post-completion edit to the fingerprinted section
bodies, which today requires an explicit `--force` to land. In that case a `complete` plan
would display `⚠ STALE-APPROVED (re-review before execute)`, which is misleading advice: a
finished plan does not need re-review before execute, because it will not be executed again.

If that is ever observed in practice, this issue is the record of why, and the fix is the
one-line status filter originally proposed. Reopening it at that point would be
appropriate. Closing now because the reported symptom is not reachable through any normal
workflow.

Evidence: plan-039 `findings/exp-003-109-nonreproduction.md`.
