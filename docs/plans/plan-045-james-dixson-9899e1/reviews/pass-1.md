---
type: Review
okf_spec: OKF-PLAN
id: pass-1
plan: plan-045-james-dixson-9899e1
created: '2026-08-18'
verdict: REVISE
status: resolved
---

# Red-Team Pass 1 — plan-045-james-dixson-9899e1

**Date:** 2026-08-18

## Verdict: REVISE

## Strengths

- The two-sided thesis is the plan's best feature. exp-007 is a genuine n=4 pattern, and D-8 is the
  correct generalization of `REQ-YF-DOCTOR-006`. **Most autonomy plans ship half of this.**
- **D-4 was revised *against* its own evidence** — exp-003 refuted the scoped design and the plan
  changed rather than rationalized.
- SPEC-first ordering is mechanically justified, not policy-cited (`DRIFT-CHECK.md` §7).
- **Staleness check: every load-bearing claim survives plan-044**, re-verified against the current
  tree — `coordinator.md:50` still closes unconditionally and `:80` still says "Wait for operator";
  `bd ready` returns 14 beads, no gates; "Operator Resolutions" is **zero** in `.py`; REQ-CLI-021/022,
  REQ-PLAN-078, REQ-AGENT-064, REQ-HERDR-015/026, REQ-PORT-051, REQ-RESUME-005 all free; the 5x /
  0x / zero-hits diagnostic counts are all accurate.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| 1 | **high** | **Epic 5 is not droppable.** `6.3 depends-on 5.6`, and 5.6←…←5.1←(herdr gate). If the gate fails, 5.1–5.6 stay open forever, `bd ready` never returns 6.3, and the Reconcile Gate (`auto — all execution beads closed`) can never fire. **The plan cannot complete.** Prose says droppable; the DAG says the opposite — verbatim the #149 defect the plan cites as its thesis | Add an explicit deferral **mechanism** to the gate Instructions: on FAIL, `bd close -r` tombstone 5.1–5.6 so 6.3 resolves, plus a `stop_class: environment` retrospective entry. Or drop 5.6 from 6.3 and have 6.3 assert Epic-5 status |
| 2 | **high** | **The review-loop grant (2.4) has no mechanical threshold, and D-3's counter structurally cannot supply one.** `yf_attempts` lives in **bd metadata**, incremented in the **coordinator loop** — but 2.4 grants unbounded autonomy in **Phase 3, before intake, before the pour, before any bead exists.** So the headline change ships with no counter, no cap, no exit code — the exact shape D-8 forbids. Walking D-8: 2.6→2.7 ✓, 3.5→never-auto-resolve ✓, 5.2→5.4 ✓, **2.4→nothing.** 2.10's count-equality is an *invariant* test, not a postcondition; it passes identically on cycle 3 and cycle 300 | Add a Phase-3-scoped `max_review_cycles`, resolved by the same 2.1/2.2 machinery, using `count(reviews/pass-*.md)` — **already on disk and already counted** by `_plan_review_line_count`. Escalate at N. Add the 2.10 assertion and a success criterion |
| 3 | **high** | **D-2's four-class stop set is contradicted by the plan's own Issue 4.3**, and Success Criterion 3 ("the **only** paths that halt") is falsified by it. 4.3 lists audit/ready-check failure, dirty worktree, §6.1.5 validation FAIL and §6.4 chain halts — **none fit the four classes.** Also unenumerated: merge conflict at §6.1, corrupted bead DB. (Operator interrupt / context exhaustion **is** handled — 0.2's REQ-RESUME-001 amendment defaults to resume) | Add a fifth class: *a declared mechanical check that fails* — validation, audit/ready-check, merge conflict, dirty worktree, corrupted bead DB. It is an exit code, so it costs the thesis nothing. Rewrite Criterion 3 to five classes, derivable from 4.3's write-site list |
| 4 | medium | **Issue 1.3 cannot do what it says where it sits.** It registers "every test script this plan adds" at `depends-on: 1.2`, but scripts land in 2.10, 3.8, 4.6, 5.6 — all later. 6.3 only *confirms*. So four scripts get authored and nothing adds their §1 rows; 6.3 discovers the gap and halts | Fold the §1/§3/§2 registration into each authoring issue (matching 1.3's own "three edits, not one" lesson), or add a late registration issue with 6.3 as confirmation |
| 5 | medium | **Issue 1.1 adds §3 globs naming no FAST id**, and the only new id comes from 1.2 which depends on it. No existing id meaningfully validates a `spec/*.md` edit — `frontmatter` is the vacuous one 1.1 itself warns about | Swap 1.1/1.2 order; state explicitly which id `skills/*/spec/*.md` maps to, or drop that glob and rely on 0.8's `cargo test` (already the honest answer in the risk table) |
| 6 | medium | **Three of exp-004's five registration items are unassigned:** `spec/data.md` REQ-DATA-002 (bundle layout — spec drift on a fixed-authority node), `_INDEX_MEMBERS` (without it `index.md` never lists the new file, violating the plan's own cold-reader contract), and the `DRIFT-CHECK.md` taxonomy edge #145 proposes | Add REQ-DATA-002 to 0.3 and `_INDEX_MEMBERS` to 4.1. Defer the DRIFT-CHECK edge explicitly if unwanted — silently dropping a finding's recommendation is the drift this plan is about |
| 7 | medium | **Both capability gates are green today** (ran both: `bd gate list` passes with **0 open gates**; herdr probe passes). So the frontloading machinery is never exercised by its own instance. Worse, the herdr gate's **Condition exceeds its Test** — Condition says a tab "can be created and closed", Test only runs `agent list`, a read. **This is verbatim the SMOKE-CHECK-ONLY defect exp-003 documented and 3.5 exists to prevent** | Narrow the Condition to match the Test, or extend the Test to actually create/close a `--no-focus` tab. For the bd gate, 0 open gates means green does not establish its Condition — test `length > 0` |
| 8 | medium | **The Motivation's "one empirical control" is n=1 and recorded in no finding.** No counterfactual exists (no plan-044 without the clause). The plan is scrupulous elsewhere (exp-007 self-labels n=1) — this claim is not held to that standard | Downgrade to "one corroborating observation (n=1, uncontrolled)"; drop "differing only in that one instruction", which is not knowable. The four textual causes stand without it |
| 9 | medium | **0.4 misses REQ-CLI-006's `Verification:` line**, which greps `@cli.command` for a count. `config resolve` as a **group + subcommand** would not be counted — the amended count and its verification disagree by construction. plan-044 also just added a note to this REQ recording that it added no subcommand | Amend the Verification line and pick the shape: flat `config-resolve` (keeps the grep) vs a group (needs a new predicate). exp-001 notes `yf` has no `config` subcommand either, so nothing forces the group |
| 10 | medium | **Self-modification during execution is unaddressed, though probably safe.** Worktree mode + the installed-skill indirection isolate it — but a resume after §6.1 merges Epic 2 and before Epic 3 lands picks up a continue-instead-of-stopping coordinator **without** the gate-enumeration fix it assumes. 0.2's default-to-resume makes crossing that window *more* likely | Add a "Reflexivity" note to the Approach stating the worktree + installed-skill isolation, and a constraint that no `yf self install` runs mid-execution — deployment at §6.2 only |
| 11 | low | `upstream-triage.md` has empty `**Disposition:**` for all four issues while plan.md records them | Backfill dispositions and notes |
| 12 | low | "~39 messages" (D-5 / 5.3) is sourced to no finding — exp-005 measured mechanics, not volume | Cite the bead count or soften |
| 13 | low | **exp-006's next-free table has a verified error** — `REQ-PHASE-*` next free is 006, not 008. The plan consumes no REQ-PHASE so no direct harm, but it relies on the same table elsewhere (independently re-verified free) | Note in Epic 0 that each id is grep-verified at authoring time |
| 14 | low | exp-003 says *"at least three"* historical gates; D-4 and the risk table both state a flat "3" | Restore "at least three" |
| 15 | low | `context.md` "Project environment", "Runtime assumptions", "Operator identity → authority scope" are template placeholders — load-bearing given two environment-predicate gates | Fill Runtime assumptions before intake |

## Missing

- **A bound on the autonomous review loop** (concern 2) — the single most important omission.
- **A deferral mechanism for a failed capability gate** (concern 1).
- **A fifth stop class** covering mechanical-check failures (concern 3).
- **Registration of the four new test scripts** into CHANGE-VALIDATION §1/§2/§3 (concern 4).
- **`spec/data.md` REQ-DATA-002 and `_INDEX_MEMBERS`** for the retrospective (concern 6).
- **A `yf-beads-init` routing rule** for a corrupted bead DB mid-autonomous-run — the always-loaded
  beads rule requires verification before relying on `bd`; an autonomous coordinator hitting a
  wedged DB has no described behavior.
- **No `scope-answers.md`** — `agents/red-team.md` §Inputs names it. Not fatal (the D-table carries
  the decisions) but the reviewer contract expects it.

## Gate Assessment

| Gate | Reachable? | Non-vacuous? | Verdict |
| :-- | :-: | :-: | :-- |
| Start Gate (human) | yes | yes | Sound; correctly `human`, REQ-SESSION-001 untouched |
| herdr probe surface | yes | **no — green today** | Condition exceeds Test (concern 7); failure unrecoverable via concern 1 |
| bd gate corpus readable | yes | **no — green today, 0 open gates** | Does not establish its stated Condition |
| Reconcile Gate (auto) | **NO if the herdr gate fails** | yes | **Blocked by concern 1 — the plan's most serious structural defect** |

Neither capability gate exhibits the `red-team.md:27` cycle — both are pure environment probes
evaluated before their blocked work. It is the **enforceability of the failure branch**, not
reachability, that is broken.

**Reflexive note:** Issue 3.7 proposes reconciling `red-team.md`'s *"gate the mutating step"* line —
the line just used to evaluate these gates. It is correct for **cycle-avoidance** and only conflicts
with frontloading when read as a *placement* rule. 3.7 already says "keep the cycle rule as the
constraint" — make sure the edit **narrows scope rather than inverting**, or future red-teams lose
the cycle check.

## Upstream Assessment

Dispositions are well-reasoned with unusually specific in/out boundaries — **the strongest section
of the plan.** #110's exclusion of multi-harness fan-out is correct precisely because exp-005's own
honest limit says the queuing is Claude Code TUI behavior and a non-claude `--kind` is untested.
#145 emit-only is right and answers its Open question 1. #113's exclusion reasoning is the sharpest
in the table.

**One caveat:** #149's in-scope half is **not actually delivered as claimed** while concerns 2 and 3
stand — the review loop has no exit code and four halt paths are unenumerated. Do not mark #149
satisfied until those close. And exp-004's DRIFT-CHECK taxonomy edge is silently dropped (concern 6).

## Operator Resolutions

| # | Concern | Resolution | Status |
| :-- | :-- | :-- | :-- |
| 1 | Epic 5 not droppable; reconcile gate wedged | **Applied.** The herdr gate's Instructions now carry a *mechanism*, not an intention: on FAIL, `bd close -r "descoped: herdr unavailable"` tombstones 5.1–5.6 so 6.3's dependency resolves and the auto Reconcile Gate can still fire, plus a `stop_class: environment` retrospective entry. The text states explicitly that without the tombstone the plan cannot complete. | resolved |
| 2 | Review loop has no mechanical threshold | **Applied.** New **Issue 2.4a** adds a Phase-3-scoped `max_review_cycles`, resolved by the same 2.1/2.2 machinery and counted by `count(reviews/pass-*.md)` — already on disk, already computed by `_plan_review_line_count`. Escalates at N to stop class 4. 2.10 gains the escalation assertion and now depends on 2.4a. D-8's claim is true as written again. | resolved |
| 3 | Stop set contradicted by Issue 4.3 | **Applied.** D-2 is now **five** classes; class 5 is *a declared mechanical check that fails* — validation, audit/ready-check, merge conflict, dirty worktree, corrupted bead DB. It is an exit code, so the thesis is unchanged. Success Criterion 3 rewritten to five and reconciled against Issue 4.3's write-site list. | resolved |
| 4 | Test-script registration unowned | **Applied.** Registration folded into the authoring issues — 2.10 now carries its own §1 row, §3 glob and §2 re-approval ("three edits, not one"), and 6.3 remains confirmation-only. | resolved |
| 5 | §3 globs name no FAST id | **Applied.** Epic 1 reordered: 1.1 authors the test, 1.2 lands the §1 row and §3 globs **naming that id**, 1.3 decides `skills/*/spec/*.md` explicitly — map it or drop it and rely on 0.8's `cargo test`, never leave it on the vacuous `frontmatter`. | resolved |
| 6 | Three exp-004 registration items unassigned | **Applied.** `spec/data.md` REQ-DATA-002 added to Issue 0.3; `_INDEX_MEMBERS` added to Issue 4.1. The DRIFT-CHECK taxonomy edge is **explicitly deferred to #145** in the Upstream Issues Notes rather than silently dropped. | resolved |
| 7 | Both gates green; Condition exceeds Test | **Applied.** Both Tests strengthened to establish their Conditions — the herdr probe now creates and closes a real `--no-focus` throwaway tab (write, not read); the bd probe asserts a **non-empty** corpus. An honest-scope note records that both were green when authored, so the frontloading machinery is not exercised by its own instance on this machine. | resolved |
| 8 | "Empirical control" is n=1, unrecorded | **Applied.** Downgraded to *"one corroborating observation (n=1, uncontrolled)"*, with the absence of a counterfactual stated and "differing only in that one instruction" removed. The four textual causes are noted as standing without it. | resolved |
| 9 | REQ-CLI-006 Verification line + verb shape | **Applied.** Issue 0.4 now specifies the **flat `config-resolve`** form (keeps the existing `@cli.command` grep), amends REQ-CLI-006's `Verification:` line as well as its enumeration, and reconciles plan-044's no-subcommand note. Also records that each id is **grep-verified at authoring time** (folds in C13). | resolved |
| 10 | Self-modification during execution unaddressed | **Applied.** New **Reflexivity** section in the Approach states the worktree + installed-skill isolation explicitly and adds the constraint that **no `yf self install` runs mid-execution** — deployment at §6.2 only. It also names the specific hazard window (Epic 2 merged, Epic 3 not yet) that 0.2's default-to-resume makes more likely. | resolved |
| 11 | upstream-triage.md dispositions empty | **Applied.** All four dispositions and notes backfilled into `upstream-triage.md`; zero empty fields remain. | resolved |
| 12 | "~39 messages" unsourced | **Applied.** Softened to "tens of messages for a plan-044-sized DAG" in both D-5 and Issue 5.3. | resolved |
| 13 | exp-006 next-free table error | **Applied.** Issue 0.4 now requires each REQ id to be grep-verified at authoring time rather than taken from exp-006's table, with the known error noted. | resolved |
| 14 | "at least three" flattened to "3" | **Applied.** Restored to "at least three" in D-4 and the risk table. | resolved |
| 15 | context.md placeholders | **Applied.** `context.md` §Project environment, §Operator identity and §Runtime assumptions all filled. Portability audit now **passes** (0 non-pass findings). Runtime assumptions record the direnv cwd hazard, the git-excluded `.beads/`, the local-only constraint, and the no-mid-execution-install rule. | resolved |
