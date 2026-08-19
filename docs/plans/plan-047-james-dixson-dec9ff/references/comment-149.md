---
type: Reference
okf_spec: OKF-PLAN
id: comment-149-draft
disposition: partial
target: https://github.com/dixson3/yoshiko-flow/issues/149
status: DRAFTED — NOT POSTED (operator gated)
---

# Draft comment for #149 — M5/M9: process rules nothing executes

**Disposition: partial. #149 stays OPEN as a class.**

M9 is addressed: a plan now declares what it fixes in a machine-checkable form
(`REQ-DATA-018`'s `Discharged-by` column, `REQ-DATA-019`'s closed `Blocks:` alphabet), and the
linter checks it.

**M5 — "a step with no exit code is not a step" — got a direct, and uncomfortable, confirmation.**
plan-047's execution produced **six** controls that were vacuous or misclassifying, and every
one was invisible to inspection and visible only to execution:

1. two drift controls that had never been run in either direction;
2. a gate harness reporting **its own failure** as "capability absent" (exit 1) rather than
   "could not run" (exit 2);
3. a carve-out positive control whose globs were single-level and therefore reached **0 of 45**
   of the files it claimed to test — `control_fired: false` was the right answer for the wrong
   reason;
4. a gate script reading a **failing tier** as a harness failure — i.e. failing precisely when
   the thing it measures was working;
5. a newly-written test passing **cwd-dependently**, for an incidental reason, caught only by a
   repo-root FULL-tier run;
6. and, separately, #125: `update-status approved` exiting **0** on a plan whose `ready-check`
   had just exited 3.

**The proposed fix is not "author gates more carefully."** Careful authoring produced all six.
It is a **precondition**: a control must *mechanically demonstrate that it can fail* before it
is trusted to pass — before it is wired into a recipe, a gate, or a manifest. plan-047 built
that proof ad hoc for one gate (mutate the carve-out glob, watch `carved_findings` go 0 → 90 and
the gate go green → exit 1); generalising it into a standard authoring step is the actual
remediation for M5.

**Still open:** M5 as a general class, and the generalisation above.
