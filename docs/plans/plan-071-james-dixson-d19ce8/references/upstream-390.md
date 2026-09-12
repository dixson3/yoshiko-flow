---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #390 - process: an inference recorded as a measurement
  survived six review passes; and pipeline-masked exit codes produced two false defect
  claims'
---
# Upstream #390: process: an inference recorded as a measurement survived six review passes; and pipeline-masked exit codes produced two false defect claims

- **Number:** 390
- **Title:** process: an inference recorded as a measurement survived six review passes; and pipeline-masked exit codes produced two false defect claims
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Two small process defects observed while planning and landing plan-068. Both are single instances
with cheap prompt-level fixes; filing together because they share a root — **an unevidenced claim
that reads like an evidenced one**.

## 1. An inference recorded as a measurement survived six red-team passes

plan-068's pass-4 review recorded a cross-plan coupling as fact:

> *Issue 2.5's end-to-end test can only clear the consent gate because `_land_tty_gate(allow_list=[None])`
> opens unconditionally — precisely what plan-069 fixes.*

It was an **inference from reading**, never measured. Execution refuted it (plan-068 Issue 3.3),
and the claim was corrected in plan-069.

What makes it worth filing is that it **survived passes 4, 5 and 6** — all three read that line and
none challenged it. The reason is structural: it sat in a table beside genuine measurements, and
every neighbouring claim carried its evidence inline (`measured`, a command, an exit code) while
this one carried none. **The absence of evidence was invisible because absence has no marker.**

This is the deviation class `yf-herdr`'s own table names — *"A finding's premise is refuted at
execution → investigation recorded an inference as a measurement, uncorroborated"* — appearing in a
**review artifact** rather than a finding.

**Suggested fix.** `red-team.md` and `planner.md` already require findings to distinguish
`measured:` from `inferred:`. Extend that requirement to **cross-plan and cross-artifact coupling
claims specifically**: a claim about how another plan's code behaves must either carry its command
and output, or be explicitly labelled a prediction. A prediction is a legitimate thing to record —
it just must not be indistinguishable from a measurement.

## 2. Pipeline-masked exit codes produced two false claims in one session

Twice I reported a tool as "exit 0 on error" when it exits correctly:

| Reported | Reality |
| :-- | :-- |
| `herdr agent list --json` exits 0 on a usage error | exits **2** |
| `_shared/test_doc_lint.py` exits 0 with a failure | exits **1** |

Both came from the same construct — `cmd 2>&1 \| tail -N` — where the pipeline's status is
`tail`'s, not `cmd`'s. In both cases I nearly filed a defect against working software; the second
one I caught only because I re-ran the command without the pipe.

This is the **same class as the defects plan-068 exists to fix** (`land`'s L16 laundering a failed
count into `0`, `bd close` refusing at exit 0): a failed measurement rendered indistinguishable
from a green one. Here the launderer was my own shell.

**Suggested fix**, for `AGENTS.md`'s Shell section, which already carries "Verify the effect, never
the exit code" for zsh loops:

> **A pipeline's exit status is the LAST command's.** `cmd | tail` reports `tail`'s success, not
> `cmd`'s. When the exit code is the thing being judged, capture it before piping:
> `out=$(cmd 2>&1); rc=$?; echo "$out" | tail -20; echo "exit=$rc"`.

That repo rule exists precisely because exit-0-on-failure is this codebase's recurring defect
class; the shell idiom that manufactures it locally belongs in the same section.

---

Both found during plan-068 (tracker #386). Neither blocks anything.

