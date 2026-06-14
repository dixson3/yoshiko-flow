# Finding INV-4: concurrent-merge regression / acceptance model

**Date:** 2026-06-14 · **Method:** read bdplan gate/RECONCILE model + WebSearch on merge-queue prior art

## Result

**Q1 — The gap ("test-the-merge, not-the-branch").** Per-plan gates validate the plan branch
against its **fork-point** base. Between fork (T0) and merge-back (T1) other changes land on
base; the gate proves nothing about `base@T1 + plan`. Two failure classes:
**(a) merge conflicts** (git-level, textual, loud, easy) and **(b) semantic regression** (clean
merge, each side individually green, integrated result broken — e.g. plan A renames `foo()`,
plan B adds a call to `foo()`; no textual conflict, `base+A+B` fails). Class (b) is what
per-plan gates structurally cannot catch.

**Q2 — Prior art (all solve (b) by testing the prospective merged state):** Bors / "Not Rocket
Science Rule" (merge into up-to-date staging, test, then fast-forward — avoids "merge skew");
GitHub merge queue (test base+PRs-ahead+this-PR, eject on fail); GitLab merge trains (merged-
results pipelines); Zuul (speculative dependent pipeline). **Transferable principles:**
(1) validate the merged state, not the branch; (2) serialize landings, keep base always-green;
(3) eject-and-fix on failure. Speculative parallelism is a contributor-*volume* optimization —
**over-engineering for a single developer**; principle 2 collapses to a trivial mutex.

**Q3 — v1 validation contract (run after merge-back, before push):**
- **Layer (a)** — re-run the plan's own Gate `Test:` commands **against the merged state**. In
  scope (reuses existing structure).
- **Layer (b)** — project-level suite via a **configured `validate-cmd` in
  `.bdplan.local.json`** (zero-magic, existing config surface). Unset → warn + run layer (a)
  only (absence is valid; don't block — mirrors bdplan's grandfather/warn posture). In scope.
- **Layer (c)** — replay OTHER active plans' gates: **over-engineering for v1**; the serialized-
  landing + project suite already covers cross-plan regressions. Defer as a v2 lever.

**Q4 — Factoring (key output): embed in bdplan RECONCILE (option A) with a (C)-shaped seam;
do NOT build a separate skill for v1.** New step **6.1.5 "Validate merged state"** runs layers
(a)+(b) after merge, before push. The "what is green" knowledge lives behind ONE indirection
(`validate-cmd` resolved from config) — the future extraction point. Trade-offs: (A) RECONCILE
already owns "pre-push tests → git handoff," lowest cost, ships fastest; (B) worktree skill is
the wrong altitude (it should *perform* the merge and report conflicts (a), not own the
semantic acceptance suite (b)); (C) distinct skill is cleanest/reusable but disproportionate
for a v1 whose job is `$(validate-cmd); echo $?`. **Rule: extract the skill only on the second
independent caller** (rule-of-three). **Feed INV-5/D1: embed-with-seam, extract-on-second-use.**

**Q5 — Serialization protocol.** Serialize merge-backs with a **single local landing lock**
(`.state/bdplan/landing.lock`, PID + plan-id). Per landing, in the lock: bring base current →
merge/rebase plan onto current base (conflict → stop, report) → run layers (a)+(b) on merged
tree → fail → fix before releasing lock; pass → base green → push handoff. Next plan validates
against the now-advanced base. **Lock: yes** (guards against two worktrees racing base);
**queue daemon / speculative parallel: no** (v1).

**Q6 — Conservative-push interaction (requires REORDERING Phase 6).** Today 6.1 "tests pass"
runs BEFORE the `git pull --rebase` in 6.2 — i.e. tests the pre-pull branch (the bug). New
order: bring base current → merge-back → **validate merged state (6.1.5)** → only on green,
propose operator-authorized push. TOCTOU: remote may advance between local validate and push →
on push rejection (non-ff), require `git pull --rebase` + **re-validate** before retry (never
push an unvalidated merged state, including after a forced rebase). Full auto rebase-revalidate
loop is v1.1; v1 essential = don't push unvalidated.

## Implications for Plan
- Phase 6 must be **reordered**, not just appended to (validate after base-update + merge,
  before push).
- The `validate-cmd` config seam is the highest-value v1 artifact (layer (b) mechanism AND the
  D1/INV-5 extraction point).
- Carry deferred items (layer c, speculative parallelism, auto rebase-revalidate loop) as
  explicit v2 notes so the red-team doesn't read their absence as oversight.
- New artifact: `.state/bdplan/landing.lock` for the serialization guarantee.
