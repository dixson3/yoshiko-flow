---
type: Review
okf_spec: OKF-PLAN
id: pass-4
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
description: >-
  [red-team pass 4] REVISE (targeted) - 9 concerns, reducing to 3 root causes. The AST seed set was
  itself short (_repo_root/_git_root), closure depth was undefined, the REQ-LAND-031 carve-out was
  an over-read, SC9 had a REPRODUCED false green at L1's down-merge, and L3/L18 could escape the
  sandbox into the real repo. Judged CONVERGING; every defect was found by RUNNING code, so a
  general pass-5 has negative value.
---
# Red-Team Pass 4 — plan-068-james-dixson-8ae0e1

## Verdict: REVISE

One targeted cycle — explicitly *not* a general pass-5.

Fourth pass, aimed at the pass-3 structural fix. Read-only.

## The convergence judgement (asked for explicitly)

**Converging in substance, not in count.** Counts read 14 → 14 → 9 → 9, which looks flat but is
not: pass-1's 14 were 14 independent causes; pass-4's nine reduce to **three root causes** — the
ctx-less-helper boundary under-specified along *depth* and *predicate* and resting on a misread
REQ (C1–C4); SC9's range expression (C5); and bookkeeping escapes from pass-3's own fixes (C6–C8).
Nothing contradicts a measurement, nothing reopens a settled design, and the DAG, counts, gates and
upstream dispositions are all clean and independently re-verified.

**Every one of C1–C5 was found by RUNNING code** — a 40-line AST script and one shell function in a
throwaway repo. **Three prose-only passes read straight past all five.** So a general pass-5 that
repeats the reading *"will find nothing and will cost a cycle"* — it has **negative value**. After
this targeted cycle, *"the residual risk is execution-surfaced, not review-surfaced."*

## Strengths

- Counts, DAG, gates and upstream dispositions all re-verified clean: 5 epics, 23 issues, 31 edges,
  5 gates, 16 criteria, 0 unparsed, no cycles, no frontloading misses.
- All four findings' Implications are otherwise fully carried — EXP-001 1–5, EXP-002 1–6,
  EXP-003 1–3, EXP-004 1–7 — with only the L2 boundary uncarried (C7).

## Concerns

| # | Severity | Concern | Resolution |
| :-- | :-- | :-- | :-- |
| C1 | high | **The AST seed set was itself short, so the structural fix relocated the defect rather than curing it.** Seeding on `{subprocess, _run_git, _run_shell, _run_change_validation}` misses **`_repo_root`** and **`_git_root`** — both bare `subprocess.run(["git","rev-parse","--show-toplevel"])` with **no `cwd`**, falling back to `Path.cwd()`/`Path(".")`. And **closure depth was undefined**: the declared SIX is the depth-1 frontier while REQ-LAND-037 says "reachable" (transitive = **ten**), so a derived constant of ten against a SPEC quoting six makes 0.3's own pinning test **fail on arrival** | **Verified in source.** 0.3 now mandates seeding on **process-launch primitives only** (`subprocess.*`, `os.system`/`popen`/`spawn*`, `pty.*`), never a hand-picked helper seed, and requires the **closure depth to be normative text** rather than an implicit choice of the computing script |
| C2 | high | **0.3's declared-helper clause was FALSE for two of the six it declared.** `_validate_merged(plan_dir)` and `_worktree_teardown(plan_dir, force)` take **no root/cwd parameter** — they resolve from ambient process cwd. A constant of names cannot detect this; the class assignment was still hand-written | Resolved by C3: both gain a `runner=`, so the predicate becomes true rather than being reworded |
| C3 | high | **The `REQ-LAND-031` carve-out was an OVER-READ.** Quoted verbatim, it mandates *"call `_worktree_teardown` with `force=False` in **keyword** form … and **branch on the returned `status`**"* — it constrains the **call**, not how the callee launches. `_worktree_teardown(ctx.plan_dir, force=False, runner=ctx.run)` satisfies it verbatim while on the seam. EXP-001 recorded L18 as "deliberately off-seam"; the finding over-read the requirement and v3 adopted it unchecked | **Verified against `landing.md:464` and the L16 precedent** `_dirty_outside_plan_dir(ctx.plan_dir, root=ctx.root, runner=ctx.run)`. Carve-out **retired**. Target state is now *"everything is on the seam"*, not "six declared exceptions" — which collapses C1's depth question, C2's false predicate and C4's escape at once |
| C4 | high | **Sandbox escape in Issue 2.5.** With 1.5's stubs removed and the carve-out in force, L3's `_validate_merged` → `_repo_root()` and L18's `_worktree_teardown` → `_git_root()` resolve to the **real yoshiko-flow checkout** unless the test `os.chdir()`s. L3 would run the real repo's FULL tier; **L18 would run `git worktree remove` / `git branch -d plan-068-…-execute` / `git worktree prune` in the real repo — against the branch Issue 0.1 just cut.** The runner contract cannot prevent it: neither call reaches `ctx.run` | Closed by C3's `runner=`, now stated in Issue 1.1 as a **safety fix, not tidiness**, with the escape spelled out |
| C5 | high | **SC9 had a REPRODUCED false green.** The merge-aware form assumed one parent orientation, but **L1's down-merge produces the opposite** (HEAD^1 = execute tip, HEAD^2 = target tip), so the range reads the *target's* commits and excludes the plan's work. Measured on a violating branch: with an unrelated `spec/` commit on main → **exit 0**; with main moved → exit 2. The landing creates this commit one step *before* the orientation pass-3 tested | **Replaced with an orientation-independent range pinned to the recorded execute base** (`assets/execute-base.txt`, written by Issue 0.1). Re-verified across **nine** cases: all four violating orientations → 1; all three compliant orientations → 0; empty range → 2 |
| C6 | medium | **The id budget was wrong a THIRD time — now over-claiming.** 0.2 listed `REQ-LAND-018` and `REQ-LAND-036` as amendments this plan makes; **no Epic 0 issue amends either**, and Issue 3.3 + plan-069 both assign them to plan-069. Pass-3's C8 fix contradicted its own C6 fix | Both removed from 0.2's list with a note that they are plan-069's. **SC9b made bidirectional** — the one-directional form could never catch an over-claim |
| C7 | medium | **A FIFTH dropped item, created by pass-3's own C7 fix.** 0.4 routed L2's in-place work "to plan-069 or a follow-on", but plan-069 contained nothing about it; 3.3's checklist and SC12 both omitted it. Identical escape class to pass-2 C6 | L2's in-place boundary written into plan-069's "do not drop these again" section, added to 3.3's checklist, and **SC12 is now eight items** |
| C8 | medium | **Issue 1.5 is five monkeypatches but SIX disabled steps.** `land_rehearsal.py:120` also skips **L19** via a decision-level `"l19_redeploy": "skip:…"` adjudication, which SC3's monkeypatch-keyed wording is structurally blind to — and Issue 2.5 explicitly requires reaching L19 | 1.5 restated as "six steps via five monkeypatches plus one decision-level skip"; **SC3 widened** to any step disabled by *either* a `pm.*` monkeypatch *or* a non-`enable` adjudication, with `stubbed_steps` derived from both |
| C9 | low | Issue 1.3's check text was a token list (`subprocess.*` / `os.system`); measured, `os.system` occurs **zero** times in the module — the same hand-written-enumeration shape 0.3 just retired | 1.3 now keys on the **derived** launcher set from 0.3's closure. One derivation, one enumeration |

## Upstream Assessment

Sound; #349/#353 `partial`-and-do-not-close remains correct. One addition adopted: Issue 3.1's
correction (b) said `yf-i127`'s "only cwd-less call" claim is wrong because there are **two** —
measured, there are **four**, adding `_repo_root` and `_git_root`. Correction (b) widened.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 seed short + depth undefined | high | Seed on launch primitives only; depth normative | `main-session` | `resolved` |
| C2 predicate false for two helpers | high | Collapsed by C3's `runner=` | `main-session` | `resolved` |
| C3 REQ-LAND-031 carve-out over-read | high | Verified against the SPEC text; carve-out retired; target state is "everything on the seam" | `main-session` | `resolved` |
| C4 sandbox escape into the real repo | high | Closed by C3; stated in 1.1 as a safety fix | `main-session` | `resolved` |
| C5 SC9 false green at L1 down-merge | high | Orientation-independent base-pinned range; re-verified across 9 cases | `main-session` | `resolved` |
| C6 id budget over-claim | medium | Two ids removed; SC9b bidirectional | `main-session` | `resolved` |
| C7 fifth dropped item (L2 boundary) | medium | Written into plan-069; 3.3 checklist; SC12 → eight items | `main-session` | `resolved` |
| C8 sixth disabled step (L19) | medium | 1.5 restated; SC3 covers decision-level skips | `main-session` | `resolved` |
| C9 1.3 token list | low | Keys on the derived set | `main-session` | `resolved` |

**Final status: all concerns resolved.** Re-verified — 5 epics, 23 issues, 5 gates, 16 criteria,
9 risks, zero `unparsed`, zero dangling, zero cycles, zero undischarged; all 14 `REQ-*` ids extract.

**Next step per this pass's own recommendation:** a **targeted verification** pass that *executes*
the fixes (the closure, SC9's base-pinned range, the `runner=` change), **not** a general reading
pass — which this review judges to have negative value.
