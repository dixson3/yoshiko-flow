---
type: Finding
okf_spec: OKF-PLAN
id: EXP-001
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# EXP-001: Is #268's ~360 s diagnosis correct? — RUN TO COMPLETION

**Question.** #268 infers ~360 s from `1801 beads x ~0.2 s`. Nobody had let it finish — every
prior observation was a kill at 30/60/90/120 s. Confirm or refute by observation, not arithmetic.

## Approach Tested

1. Read the code path first to establish the run was safe: `create_or_update` returns before any
   write when `apply` is false (`upstream.py:930`), so `push` without `--apply` writes nothing.
2. Ran the **verbatim #268 reproduction** against the live repository with a 900 s budget and
   stdin closed, timing it end to end.
3. Separately instrumented the internals in-process
   (`assets/exp001-equivalence-harness.py`): timed
   `load_universe_rows`, a 20-call `bd show` sample, then `collect_parent_edges` and
   `owner_claim_warning_lines` each to completion.

## Result

**CONFIRMED, and tighter than the estimate.** The path is a serial subprocess fan-out that *does*
terminate. It is not a deadlock, not a prompt, not a network stall.

```
$ uv run "$(yf skill-dir yf-beads-upstream)/scripts/upstream.py" push --issues yf-djfx </dev/null
Push plan: 1 bead(s) -> GitHub (beads stay open and mirrored)
  [create] yf-djfx  -> (new issue)
             title: bd telemetry: .beads/interactions.jsonl is a cleaner transition source ...
             labels: type::task, priority::low

Preview only — nothing was written. Re-run with --apply to write.
=== REPRO rc=0 elapsed=334s ===
```

| quantity | #268 (inferred) | measured |
| :-- | --: | --: |
| universe rows (`bd list --all --json`) | 1,801 | **1,801** |
| cost of that one bulk call | — | **0.80 s** |
| cost of one `bd show <id> --json` | ~0.2 s | **0.186 s** (20-call mean) |
| projected serial cost | ~360 s | **335.4 s** |
| `collect_parent_edges` to completion | — | **321.9 s** (1,648 edges) |
| `owner_claim_warning_lines` to completion | — | **336.4 s** |
| end-to-end `push --issues yf-djfx` | never completed | **334 s, rc=0** |

**measured:** end-to-end 334 s, exit 0. #268's inference was sound and ~7% high.

Three things the completion run establishes that the SIGINT traceback could not:

1. **It terminates.** A kill at 120 s cannot distinguish "slow" from "wedged". It is slow — a
   performance defect with a mechanical fix, not a concurrency defect.
2. **The warning produced ZERO lines.** `owner_claim_warning_lines()` returned `[]`. On this
   repository the 336 s buys **no output at all**; the entire cost computes that there is nothing
   to warn about. #268 called this path "a *diagnostic*" — measured, it is a diagnostic that here
   reports nothing.
3. **The "no stdout" symptom is explained and is not a separate defect.** The push plan is printed
   *before* the warning loop, yet nothing appeared until exit: Python block-buffers stdout when it
   is not a TTY, so an already-rendered preview sat in the buffer for 334 s. Under a pipe — how
   every agent invokes it — a fast, complete, correct preview is indistinguishable from a hang.

## Implications for Plan

- The diagnosis in #268 is sound and can be designed against without re-litigation.
- The 334 s is **entirely** `collect_parent_edges`; `load_universe_rows` is 0.80 s of it. Removing
  the fan-out addresses ~99.8% of runtime, so a single epic can close the issue.
- **inferred:** because the cost is one call site, no caching layer, no concurrency and no
  progress-reporting mechanism is needed — those would all be treating a symptom.
- Result 2 weakens any argument for *preserving* the warning's current scope: on this corpus it is
  pure cost. It strengthens the case for making it cheap rather than for making it conditional.
- Result 3 is worth a defensive note but **not** a code change: once the path is sub-second,
  buffering stops being observable.

## Recommendations

1. Treat the fan-out as the sole cause of the observed hang and fix it at `collect_parent_edges`.
2. Do **not** add progress output, a spinner, or `flush=True` as part of this fix — they would
   mask rather than remove the cost, and become dead weight once the path is fast.
3. Do **not** scope the warning to `--issues` as #268's direction 1 suggests. Making it cheap
   preserves REQ-BUP-049's whole-universe semantics, which are the point of the warning; scoping
   it would narrow a diagnostic to fix a cost that no longer exists.
4. Re-measure on any corpus before quoting these timings — they scale with universe size and
   machine. The *equivalence* result (EXP-002) travels; these numbers do not.

## Evidence

- Reproduction transcript above; log `assets/exp001b-repro-334s.output.txt`
- Harness `assets/exp001-equivalence-harness.py`, log `assets/exp001-equivalence-harness.output.txt`
- `skills/yf-beads-upstream/scripts/upstream.py:524` (`collect_parent_edges`), `:550`
  (`deps_for_show`), `:930` (the no-write guard), `:1168` (`owner_claim_warning_lines`), `:1231`
- Machine: darwin 25.5.0; repo `dixson3/yoshiko-flow` @ `4fcf97b`; universe 1,801 beads
