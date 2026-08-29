# Post-fix end-to-end timing (Issue 1.9) — the EXP-001 reproduction, re-run

The command EXP-001 ran to completion pre-fix, re-run on the fixed tree. Same command, same
repository, same bead.

```
uv run skills/yf-beads-upstream/scripts/upstream.py push --issues yf-djfx
```

| | Pre-fix (EXP-001) | Post-fix (here) |
| :-- | --: | --: |
| **Wall clock** | **334 s** | **1.17 s** |
| Exit code | 0 | 0 |
| `bd show` subprocesses | 1,801 | **0** |
| Universe size at measurement | 1,801 beads | 1,905 beads |

**~285x faster on a universe that is 6% LARGER.** The measurement was taken
2026-08-29T01:04:24Z on branch `plan-058-james-dixson-0e36fd-execute` at
`98f8d1e`.

This discharges **SC1c** — "completes in seconds, not minutes, on a >=1,800-bead universe". It is a
*measurement*, not a suite assertion, because a mocked call-count test cannot observe a wall clock;
the call-count invariant is asserted separately and permanently by SC1/SC3.

## The two secondary observations EXP-001 predicted, both confirmed

1. **`owner_claim_warning_lines()` still returns `[]` on this repository.** Grep for `WARNING` in
   the output: **0 lines**. So the 334 s bought *no output at all* — exactly as EXP-001 measured.
   The fix removes the cost; it does not change the (empty) result.
2. **The stdout-buffering symptom is gone as a practical matter, but was never a separate defect.**
   The whole run is now 1.17 s, so there is no window in which a block-buffered preview can sit
   unseen. Issue 3.6 still adds `flush=True` on the push path, because `push --apply` over N beads
   buffers through 1-2 s per `gh` write and that window does not dissolve with this fix.

## Cold-start `bd` latency against the 780 MB Dolt store (R13)

The plan recorded that **every** timing in `findings/` was warm, and that the 60 s `LOCAL_TIMEOUT_S`
therefore rested on an untested premise. Measured here, `bd list --all --json` against the live store:

| Sample | Wall clock |
| --: | --: |
| 1 | 0.299 s |
| 2 | 0.196 s |
| 3 | 0.174 s |

`.beads` is **780 MB** at time of measurement.

**The first sample is the slowest, which is the cold-start signal**, and it is 0.299 s — roughly
**200x** inside the 60 s local bound. R13 is discharged: the bound has ample headroom even cold. The
honest caveat is that this machine's page cache was not dropped between runs, so "cold" here means
"first call of this process group", not "cold from a reboot". That is a weaker claim than a true
cold start, and it is stated rather than glossed — but a true cold start would have to be ~200x
slower to threaten the bound.

## Raw output of the timed run

```
Push plan: 1 bead(s) -> GitHub (beads stay open and mirrored)
  [create] yf-djfx  -> (new issue)
             title: bd telemetry: .beads/interactions.jsonl is a cleaner transition source than 'bd history' (which is swamped by batch-flush noise)
             labels: type::task, priority::low

Preview only — nothing was written. Re-run with --apply to write.
```

stderr was empty (0 bytes).
