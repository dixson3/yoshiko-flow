# Plan Red-Team: plan-009-james-dixson-996e44 — Pass 1

**Presented:** 2026-06-14 · **Conformance:** PASS (mechanical, run inline)

## Verdict: REVISE

Core decisions (D1=C embed-with-seam, the v1 validation contract, the Phase 6 reorder) are
defensible and evidence-backed. One high-severity correctness hole in the coordinator cwd /
plan-folder address-space model blocks approval until written down correctly. Several mediums
warrant an operator discussion pass. Findings are sufficient — no new experiment required.

## Strengths
- D1 is genuinely justified, not rationalized: INV-5 shows `install.py` has no
  optional-dep concept, so a distinct skill is force-install (forbidden) or prose-only; the
  rule-of-three seam (`plan_manager.py worktree …`, modeled on `render.py`) is a real
  lift-and-shift unit.
- INV-1/INV-2 are empirical; non-obvious findings (reject `.git/worktree/`, merge from
  primary, bd native git-common-dir DB resolution) correctly propagated.
- Deferred items carried explicitly (absence reads as decision, not oversight).

## Concerns (verbatim)
- **C1 — Coordinator cwd model inconsistent; breaks `plan_dir` resolution — severity: high.**
  `plan_dir` is relative, resolved against `Path.cwd()`; every `plan_manager.py <verb>
  "${plan_dir}"` call assumes cwd = repo root. Moving cwd into `.worktrees/<plan-id>` makes
  `docs/plans/<plan-id>` resolve under the worktree (wrong/absent tree). Also the coordinator
  is the **main session**, not a sub-agent — you cannot per-plan "set its cwd"; it would have
  to `cd`/`git -C` explicitly. Plan never separates worktree-relative (code/commit) from
  primary-relative (`plan_dir` ops, §6.1 merge, §6.2 push, `git add "${plan_dir}" .beads/`)
  operations. *Recommendation:* split into two address spaces in Issue 2.3 + coordinator.md:
  (a) code/build/commit → `git -C .worktrees/<plan-id>` / sub-agent cwd on branch `<plan>`;
  (b) `plan_dir` ops, all `plan_manager.py`, merge, push handoff → primary checkout. Do not
  blanket-set the coordinator session cwd. Make it a named design point.
- **C2 — v1 validation contract may not satisfy the stated concern — severity: medium.**
  Operator's concern is class-(b) (A renames `foo()`, B calls it). The contract is (a) this
  plan's gates + (b) `validate-cmd`. In the canonical example *plan B's* gates catch it, but
  A's may pass cleanly merged — so coverage **collapses onto layer (b)**, which is warn-skip
  when unset. Default posture (no `validate-cmd`) runs layer (a) only and leaves the core
  concern unaddressed while presenting as "validated." *Recommendation:* (1) state plainly
  the concern is satisfied only when `validate-cmd` is a project-wide suite; (2) escalate the
  unset case from silent warn to a prominent land-time notice; (3) confirm deferring layer (c)
  is acceptable given (b) is the only real net and is optional.
- **C3 — Landing lock staleness/race holes — severity: medium.** PID reuse; cross-machine
  opacity; non-atomic create (no `O_EXCL`/`mkdir`) races two landings; `.state/` sync.
  *Recommendation:* atomic acquisition (`O_EXCL`/`mkdir`); record hostname+PID+plan-id+ts;
  stale only if hostname matches AND PID dead (never auto-break another host's lock); state
  single-machine scope; add a contention unit test.
- **C4 — Bootstrapping mitigation understates chicken-and-egg — severity: medium.** Unit
  tests (1.4) cover the verb cluster only, not the SKILL.md/coordinator.md wiring or the cwd
  split. A wiring bug surfaces only on a real later worktree-mode plan, possibly corrupting a
  merge-back. *Recommendation:* make the throwaway follow-up plan a concrete named acceptance
  checklist tied to SC 1–6; consider gating the default-on flip (D2) behind that acceptance
  run passing (ship opt-in until dogfood passes, then flip default).

## Missing (verbatim)
- **M1 — Plan-folder commit semantics across the worktree boundary — severity: high
  (root cause of C1).** Plan never states where the plan folder lives during worktree
  execution or what is committed to `<plan>` vs primary. *Recommendation:* `plan_dir`
  artifacts and `.beads/` are **primary-side** (bd's shared DB already is, per INV-2); only
  code lands on `<plan>`.
- **M2 — `--no-ff` vs ff merge contradictory — severity: low.** INV-1 uses `--no-ff`; §6.1
  says only "merge." *Recommendation:* pick `--no-ff` (auditability/clean revert), state it.
- **M3 — Landing lock vs conservative push STOP — severity: medium.** §6.1.5 holds the lock
  for fix; §6.2 also halts for push authorization — a long human wait holds the global lock,
  blocking other plans. *Recommendation:* define whether the lock releases after a green
  local validate-and-merge (push as a separate primary-side step) or must span authorization.
- **M4 — No runtime fallback for bd worktree-DB precondition — severity: low.** Capability
  gate checks once at intake; runtime viability set omits "bd shared-DB resolution fails from
  this worktree." *Recommendation:* add it to the `fallback:<reason>` set.

## Gate Assessment
Start gate appropriate. Capability gate well-formed and genuinely needed, but fires once at
intake — complement with a runtime viability fallback (M4). No gate covers dogfood acceptance
of the lifecycle; consider gating the D2 default-on flip behind it (C4).

## Upstream Assessment
Disposition sound; matches AGENTS.md coarse granularity (no match → one coarse issue at land,
Issue 4.4, precedents #13/#14/#16). Nit: record the filed issue number back into plan.md at
land for cold-resume self-containment.

## Operator Resolutions
| # | Concern | Severity | Resolution | Status |
|---|---------|----------|------------|--------|
| C1 | Coordinator cwd / address-space split | high | Plan revised: explicit two-address-space model (code worktree-side; plan_dir/.beads/plan_manager/merge/push primary-side); coordinator session does NOT chdir | resolved |
| M1 | Plan-folder commit semantics | high | Plan revised: plan_dir + .beads are primary-side; only code commits to branch `<plan>` | resolved |
| C2 | Validation contract coverage | medium | Plan revised: stated concern covered only when validate-cmd is a project suite; unset → prominent land-time notice (not silent warn); layer (c) deferral confirmed at review | resolved |
| C3 | Landing lock robustness | medium | Plan revised: atomic acquisition, hostname+PID+plan-id+ts, single-machine scope, contention test | resolved |
| C4 | Bootstrapping/dogfood | medium | Plan revised: named dogfood acceptance checklist (SC 1–6); D2 default-on flip gated behind it | resolved |
| M2 | --no-ff merge | low | Plan revised: `--no-ff` stated | resolved |
| M3 | Lock vs push-STOP hold | medium | Plan revised: lock releases after green local validate+merge; push is a separate primary-side step | resolved |
| M4 | Runtime bd-DB fallback | low | Plan revised: added to runtime viability fallback set | resolved |

**Final status: all concerns resolved via plan revision (REVISE addressed in-session).**
