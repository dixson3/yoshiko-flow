---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #259 - doc_lint accepts a review verdict form that ready-check
  rejects — a review can pass the audit and be malformed to the gate'
---
# Upstream #259: doc_lint accepts a review verdict form that ready-check rejects — a review can pass the audit and be malformed to the gate

- **Number:** 259
- **Title:** doc_lint accepts a review verdict form that ready-check rejects — a review can pass the audit and be malformed to the gate
- **URL:** 
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

## The defect

**Two parsers in `yf-plan` disagree about what a review verdict line looks like, so a review file
can pass the portability audit while being unreadable to the gate that keys on it.**

- **`ready-check`** (`plan_manager.py:4881`, REQ-PLAN-071) accepts **only** a heading:
  ```python
  m = re.match(r"#{2,3}\s+Verdict:\s*([A-Za-z-]+)", line.strip(), re.IGNORECASE)
  ```
- **The portability audit's `doc_lint` check** additionally accepts a **bold** form:
  ```
  (?m)^#{1,6} +Verdict: +(APPROVE|REVISE|INVESTIGATE-MORE)\b|^\*\*Verdict:\*\* *(APPROVE|REVISE|INVESTIGATE-MORE)\b
  ```

So `**Verdict:** APPROVE` is **valid to the audit and malformed to the gate**. `audit` returns
`status: pass` with zero findings; `ready-check` returns
`malformed review: … contains no parseable verdict line`.

## Why it matters

The two verbs are *adjacent in the same flow*: SKILL.md §3 runs the portability audit and then
`ready-check` as the approval precondition. A green audit is exactly the signal an author uses to
believe the bundle is well-formed — and it is green on a file the very next step cannot read.

REQ-PLAN-071/072 went to real trouble to make a malformed review **distinguishable** from an absent
one (`(N, None, path)` vs `(None, None, None)`), specifically so it could never degrade to a silent
"no verdict" — the failure mode that hid #116. That care is undermined one layer up by an audit
that calls the malformed file clean.

## Measured on this corpus

```
review files using **Verdict:**  (bold)     19
review files using ## Verdict:   (heading) 140
```

More importantly — since `ready-check` reads only the **highest-numbered** pass per plan:

**12 plans have their LAST review malformed to `ready-check`:**

| plan | last pass | verdict it carries |
| :-- | :-- | :-- |
| plan-003 | pass-1 | REVISE |
| plan-004 | pass-1 | REVISE |
| plan-005 | pass-2 | REVISE |
| plan-010 | pass-2 | REVISE |
| plan-012 | pass-2 | REVISE |
| **plan-013** | pass-2 | **APPROVE** |
| plan-014 | pass-2 | REVISE |
| plan-015 | pass-1 | REVISE |
| plan-016 | pass-1 | REVISE |
| plan-017 | pass-1 | REVISE |
| **plan-022** | pass-2 | **APPROVE** |
| plan-023 | pass-2 | REVISE |

**The two APPROVE rows are the sharp end.** Those plans were genuinely approved, and `ready-check`
reports them as *unreadable* rather than as approved. All twelve are complete, so nothing is wedged
today — but the mechanism is live, and it bit plan-055 during drafting: all five of its review files
were authored in the bold form, the audit passed clean five times, and the divergence only surfaced
when `ready-check` ran at the approval gate.

## The class

This is another **two-parsers-one-contract** instance, the same family as
[#181](https://github.com/dixson3/yoshiko-flow/issues/181) (`doc_lint`'s `not-selected` vs
`no-such-path`), [#207](https://github.com/dixson3/yoshiko-flow/issues/207) (`resume-scan`'s
`found`), and [#256](https://github.com/dixson3/yoshiko-flow/issues/256) (the smoke's absent vs
unauthenticated). The recurring shape: **two consumers of one artifact disagree about its grammar,
and the more permissive one is the one that reports "clean".**

## Proposed fix

Pick one and make it the single source of truth:

1. **Narrow `doc_lint` to REQ-PLAN-071's canonical heading form** — the docstring already says the
   heading is canonical and that accepting `###` is *"a tolerance, not a second canonical form;
   emitting it is still non-conformant."* The bold form is not even in that tolerance. This makes the
   audit catch what the gate will reject, which is the right direction: fail early, at authoring time.
2. **Or widen `ready-check`** to accept the bold form — cheaper, but it enshrines a second canonical
   form the SPEC explicitly declines to have.

**(1) is recommended**, with a corpus sweep of the 12 files above so the historical records become
readable rather than merely unreached.

Either way the two regexes should be **derived from one shared constant**, not maintained
independently in two scripts — independent maintenance is what produced the divergence.

## Provenance

Found during plan-055 drafting: five consecutive review passes were authored as `**Verdict:** …`,
the portability audit returned `pass` with zero findings on every one, and `ready-check` then
refused the approval gate with `malformed review`. The corpus figures above were measured directly
over `docs/plans/*/reviews/`.
