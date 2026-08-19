---
type: Reference
okf_spec: OKF-PLAN
id: comment-135-draft
disposition: deferred
target: https://github.com/dixson3/yoshiko-flow/issues/135
status: DRAFTED — NOT POSTED (operator gated)
---

# Draft comment for #135 — a measured literal in plan.md goes stale

**Disposition: DEFERRED — Issue 7.3 was in the descoped Epic 7. #135 stays OPEN.**

plan-047 planned to restate five hardcoded counts as self-consistency assertions; Epics 6–10
were descoped at the D-13 split gate, so that did not land.

One datum worth adding: **plan-047 produced a live specimen of this class during its own
drafting** — D-13's text said "67 issues" while the parsed value was 68, and by execution the
true count was 78. A hand-maintained count in an authored document went stale twice inside a
single plan, which is the strongest available argument that the linter rule is worth having.
