---
type: Reference
okf_spec: OKF-PLAN
id: sc9-non-rottable
description: SC9 — the executable check is non-rottable, demonstrated on a throwaway tree
---

# SC9 — the executable check fails if the spec and the test drift apart

Run on a `$(mktemp -d)` copy of `skills/yf-plan/` (removed afterwards; no residue). Baseline
in the throwaway tree: **6 passed**.

| Arm | Perturbation | Expected | Observed |
| :-- | :-- | :-- | :-- |
| **A** | **RENAME** the test file | the meta-assertion fails | **3 failed, 3 passed** — every one of the three REQ cases fails, because each REQ's `Verification:` line names the old filename |
| **A2** | **DELETE** the test file | the `Verification:` command fails | **exit 2** on its first conjunct — which is what `ctl-165-executable` reads |
| **B** | **REWORD** one REQ's `Verification:` line back to prose | that REQ's case fails | **1 failed, 5 passed** — precisely `REQ-AGENT-043`, the REQ perturbed |

Arm B failing **exactly one** case is the load-bearing detail: it shows the meta-assertion is
bound per-REQ rather than globally, so a single drifted line cannot hide behind two intact ones.

## Why arm A is falsifiable at all

`_THIS_TEST` is **derived** from `Path(__file__).name`, never hardcoded. A hardcoded literal
would keep the meta-assertion **green after a rename** — the check would then be asserting that
the spec names a test which no longer exists, which is the exact rot it exists to prevent, one
level up. The first draft of this file hardcoded it; arm A is what made that visible.

## The vacuity guard earned its place on the first run

`test_the_spec_is_parseable_at_all` **failed on the very first execution** of this test file
and caught a real defect in `_req_block`: the "find the next `REQ-` line" regex matched the
REQ's **own** id line at offset 0, so every block parsed **empty**. Without that guard the
three parameterized cases would have been reading empty strings — passing their prose checks
against the agent files while silently checking nothing in the spec.

That is the vacuity failure mode this plan exists to close, occurring inside the plan's own
test, and caught by the guard the plan required. It is recorded rather than quietly fixed.
