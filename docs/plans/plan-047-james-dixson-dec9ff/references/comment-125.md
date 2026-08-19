---
type: Reference
okf_spec: OKF-PLAN
id: comment-125-draft
disposition: include
target: https://github.com/dixson3/yoshiko-flow/issues/125
status: DRAFTED — NOT POSTED (operator gated)
---

# Draft comment for #125 — status-enum hardening for `update-status`

**Disposition: include. This issue is CLOSABLE.**

Closed by plan-047 Issue 2.5, with `REQ-DATA-028` (spec/data.md) and `REQ-CLI-024`
(spec/cli.md) as the SPEC half.

**Reproduced first.** On a bundle whose `ready-check` had just exited **3**,
`update-status <dir> approved` exited **0** and wrote the status. `update_status` was a
free-form writer by its own docstring, so the intake gate was prose obedience, not code —
nothing downstream of a failing audit could stop a plan reaching `approved`, whatever a linter
returned.

**Now:** the `approved` transition is refused unless `ready-check` is green. The refusal exits 3,
emits a structured verdict naming the reasons and the remediation, and **writes nothing** —
`plan.md` and `log.md` are byte-identical before and after, because a refusal that still writes
is not a gate.

**Override:** `--override-ready-check`, deliberately **not** a bare `--force`. `--force` already
means four different things on four other verbs (file overwrite on `capture`, stale-approval
bypass on `execute`, lock stealing on `landing-lock release`, dirty-tree override on
`worktree teardown`), and `update-status` writes nine statuses — a bare `--force` there would
not say *what* it forces, and the one thing it must never read as forcing is a status the plan
has not earned. Using it writes the status **and** records a `deviation` in the plan
retrospective **and** states the override in `log.md`.

**Scoped to `approved` alone**, deliberately: gating all nine statuses would make the first
transition unreachable, since a plan in `scoping` has no red-team verdict by construction.

**Verified by falsification:** neutering the gate makes 2 of the 5 tests in
`skills/yf-plan/scripts/test_update_status_gate.py` fail.
