---
type: Reference
okf_spec: OKF-PLAN
id: comment-165-draft
disposition: deferred
target: https://github.com/dixson3/yoshiko-flow/issues/165
status: DRAFTED — NOT POSTED (operator gated)
---

# Draft comment for #165 — SPEC `Verification:` lines are prose shaped like commands

**Disposition: DEFERRED — this issue was in Epic 7, which plan-047 descoped. #165 stays OPEN.**

The plan's original triage marked #165 `include`, with Issue 7.2 fixing the four measurably
false clauses and Issue 7.5 adding a grammar linter. **Epics 6–10 were descoped at the D-13
split gate**, so none of that landed and this comment claims none of it.

What the investigation measured, recorded here so the finding is not lost:

- only **5.9%** of 226 `Verification:` clauses are even command-shaped;
- of the 13 runnable ones, **4 are already FALSE** when executed, and 2 more pass only from the
  skill directory;
- **265 of 312** testable requirements (85%) sit under no executing gate at all, because
  `coverage.rs` parses the root `SPEC.md` only — per-skill `REQ-*` families are out of its reach.

That last bound is the one worth stating plainly whenever #165 is eventually closed: fixing the
false clauses would still leave the large majority of testable requirements ungated, so a fix
must not be described as making `Verification:` lines trustworthy in general.

An unrelated instance of the same class turned up **inside plan-047's own new code** and was
fixed there: a test that passed only from `skills/yf-plan/scripts/` and failed from the repo
root, caught by the FULL tier.
