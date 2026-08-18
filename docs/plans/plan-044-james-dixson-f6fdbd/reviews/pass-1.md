---
type: Review
okf_spec: OKF-PLAN
id: pass-1
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
verdict: REVISE
status: resolved
---

# Red-Team Pass 1 — plan-044-james-dixson-f6fdbd

**Date:** 2026-08-17
## Verdict: REVISE
**Status:** all 14 concerns resolved — plan revised, red-team re-run required (REQ-PLAN-030)

## Strengths

- Evidence base is unusually strong; all six findings are measurement-first. The two claims that
  reframed the work (#159's filed root cause is wrong; #143 is 14 not 5) are each corroborated by
  independent signals. Load-bearing code sites independently re-verified: `install.rs:66`
  `prune=false`, `status.rs:103` unconditional `install_rules_aggregate`, `common.rs:174`
  untransformed `skills_dir.join(name)`, `beads_init.rs:568-573` step label, `cli.rs:451-453`
  help text, `RULE_TARGETS` (`managed_block.rs:345`) four rows and no `agents`.
- **D-3 (reject `record-epic`) is the single best call in the plan** — exp-005 A4 traces three
  concrete cascades to specific functions.
- D-5's insistence that `--prune` alone does not deliver a green doctor is correct.
- exp-006's sequencing finding is real and correctly acted on; `CHANGE-VALIDATION.md:26` FAST id
  `cargo` = `cargo test --workspace` is exactly the coverage gate, so Issue 0.7 is the right
  instrument.
- Gate reachability is **not** circular — `cargo test -p yf --test harness_cross_e2e` exits 0 at
  HEAD, so the capability gate is satisfiable before Issue 2.3 does its work.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| 1 | **high** | **ALLOWLIST bridge mis-sequenced.** `coverage.rs:200-222` asserts `!tagged.contains(id)` — a row becomes a hard failure the instant its tag lands. Issues 2.1 (`FLOW-008`) and 2.5 (`TUNE-029`) add tags and **no issue ever removes their rows**; 2.8/2.9 remove theirs one-to-two issues late. Tree is red at 2.1, 2.5, 2.8, 2.9 — four windows, not zero. | State the invariant in 0.5: the row is removed in the **same issue and commit** that adds the tag. Add removal to 2.1, 2.5, 2.8, 2.9; drop it from 2.10; keep 4.3 as the net-clean assertion. |
| 2 | **high** | **`REQ-YF-FLOW-008` contradicts `REQ-YF-FLOW-004`** (`SPEC.md:721-723`: `remove` drops sections "unconditionally" and deletes the file at S6) with no amendment → DRIFT-CHECK §7 CONFLICT-and-halt. Behind it an unowned behavior gap: after 2.1 makes `remove` rules-neutral, **nothing drops a removed skill's section** — REQ-YF-FLOW-002 reconcile-prunes on the *embedded* set, so a later `tune` retains it too. `yf harness skills remove <skill>` would leave its rules loaded permanently. | Amend REQ-YF-FLOW-004 in 0.1 and **decide** post-removal semantics. 2.1 then implements a decision, not an audit. |
| 3 | medium | Issue 2.5's conservative-keep **is** hand-edit tolerance, which D-9 claims to avoid; leaves `tune --revert` (keeps) and `skills remove` (deletes unconditionally, `status.rs:158-164`) with opposite policies on one file. REQ-YF-TUNE-022 scopes its guard to **keys**. | Amend REQ-YF-TUNE-022 alongside the new REQ-YF-TUNE-029; record in the amendment log that FLOW-004's no-hand-edit-tolerance is scoped to the section-rewrite path, not revert. |
| 4 | **high** | **#160's most plausible cause is left live.** `beads_init.rs:456-462` runs `bd init` **before** `bd config set dolt.local-only true`, and the step label at `:461` asserts *"no remote wired at init"* — false under that hypothesis. Plan closes #160 with detection + prose only. exp-002 marked this inferred-and-unverified; the probe was never run. | Add an Epic 1 issue before 1.6 running the sandboxed `bd init`-with-git-origin probe. If confirmed, reorder `repair()` and correct the false label. If refuted, record it. |
| 5 | medium | **Issue 1.6 drops one of five sites** — `skills/yf-plan/agents/coordinator.md:114-116` is authorization-gated, not local-only-gated. Criterion 3 ("**No** land-the-plane surface…") is therefore false on completion. plan.md:89 also says "Four" where findings show five. | Add coordinator.md to 1.6; correct the count to five. |
| 6 | medium | **Criterion 7 unmeetable.** Ignore-list covers 5 of 7 measured leftovers; `test-harness/.scratch/sandbox.env` and `test-harness/topology.txt` are **not** covered. 2.10(d)'s "no `modified` skill after 2.9" will fail. Also a discipline tension: the capability gate forbids touching the real `~/.claude`, but 2.10(d)/criterion 7 assert *about* it. | Extend the ignore-list (e.g. `**/.scratch/**` + a decision on `topology.txt`), or restate criterion 7 as "after a one-time `--prune`, stable thereafter" with the `./target/debug/yf` invocation spelled out as an operator step, not a test. |
| 7 | **high** | **The `agents` harness silently loses rules entirely.** `skills upgrade` is today the *only* writer serving `agents` (`~/.agents/rules/`); `tune` exits 1 with `rules: not_applicable` and `RULE_TARGETS` has no `agents` row. After 2.1 no writer serves it. Criterion 4 is vacuous exactly where the regression is. | Make the `agents` decision explicit in Epic 0 / 2.2 — add a `RULE_TARGETS` row, or declare `agents` a skills-only bare surface and reconcile `preflight.rs:213-217`. |
| 8 | medium | **`gh`-failure-is-INCONCLUSIVE has no owning issue.** `upstream.py:85-90`'s `run()` raises `SystemExit` on any non-zero subprocess, so today a `gh` failure exits 1 and produces nothing. Delivering INCONCLUSIVE means changing a shared helper used by every verb. | Add an explicit sub-step to 3.2 for a non-raising call path, noting existing callers keep fail-fast. |
| 9 | medium | **#143 half declares no test**, yet criterion 10 asserts a three-state behavior (fail / warn / pass). 4.2's CHANGE-VALIDATION maintenance is placed after everything, so a new test script would be invisible to both tiers during Epic 3. | Give 3.8 an explicit test script (`uv-yf-*` precedent); move the three-edit CHANGE-VALIDATION step into the issue creating each script; keep 4.2 as a final audit. |
| 10 | low | **Epic 2 over-serialized.** The Approach justifies only #156-before-#154. #155's surface (`install.rs`, `common.rs`, `marker.rs`) does not intersect #154's (`revert.rs`, `RuleRecord`). | Re-point `2.7 depends-on 2.3`; same for `3.4 depends-on 3.2`. |
| 11 | medium | **The 14-bundle repair has no dry-run and no verification.** The risk row restates D-3 rather than mitigating the mass-edit risk. | Give 3.7 a `--dry-run` and a mandatory postcondition — re-run `resume-scan` across all 14, assert `total > 0`. The plan's own thesis is not applied to its riskiest step. Note `docs/plans/` is git-tracked, so blast radius is `git checkout`. |
| 12 | low | Restated-not-mitigated risk rows; the SKILL.md-sequencing mitigation is unimplementable for 1.6, which edits SKILL.md **and** `beads_hygiene.py` in one issue. No risk row for the stale-allowlist window, the `agents` loss, the `remove` orphan, or the live-DB mutations in 3.1/3.6. | Split 1.6 or drop the mitigation; add the missing rows. |
| 13 | low | Count/citation errors: "4 epics, 30 issues" (actual **5 epics, 36 issues**); `SPEC.md:864` cited for the canonical profile (server-mode invariant is **`SPEC.md:856-859`**); Epic 0 called validation-dark though 0.5 edits `coverage.rs`, which **does** fire `cargo-fmt`+`cargo`; `upstream-triage.md` has every Disposition/Notes field blank. | Correct each; fill the triage artifact. |
| 14 | low | "Epics are independent after Epic 0" holds **only if** concern #1 is fixed — independence is a consequence of allowlist discipline, not independent of it. | Reword. |

## Missing

- Any issue addressing `beads_init.rs:456-462`'s init-then-local-only ordering (the largest
  unowned gap — #160 gets closed by detection alone).
- `skills/yf-plan/agents/coordinator.md:114-116` in Issue 1.6.
- A decided outcome for `skills remove`'s rules behavior.
- An `agents`-harness rules decision.
- `test-harness/.scratch/` and `topology.txt` in the ignore-list, or a one-time prune step.
- A test for the #143 validator.
- exp-005 Part B footnote 2 (cosmetic `--surface`-absent assertion) — fine to drop, but say so.
- exp-001 recommendation 5 (consolidate `DESCRIPTORS` + `RULE_TARGETS`) — the structural cause of
  both #156 and the `agents` gap. Deferral is reasonable; silence is not.

## Gate Assessment

- **Start Gate** — appropriate.
- **Capability Gate — vacuous relative to its own Condition.** The Condition claims all five
  descriptors; the Test exits **0 at HEAD** because `surfaces()` (`harness_cross_e2e.rs:69-93`)
  `panic!`s on `"agents"` and `:111` iterates only three, with `pi` separate. It proves a
  4-descriptor capability while asserting a 5-descriptor one — and the fifth is precisely what
  Issue 2.3 adds. Not circular, but **a gate that is already green is not a gate.**
- **Reconcile Gate** — standard, fine.
- **Missing gate:** nothing gates Issue 3.7's 14-bundle mass edit.

## Upstream Assessment

Dispositions sound and each traceable to a finding. Notable: **#160** should not close on this
plan without either the probe or an explicit "cause not established; detection only" note in the
close comment. **#158 supersede** is handled correctly — exp-005 Part B is source-reading plus
pinning-test presence, *not* a green run, and Issue 4.1 makes `cargo test -p yf sync` a hard gate
before closing. Criterion 8's "35 emitted / 6 actionable" baseline matches exp-003 exactly.
`upstream-triage.md` records none of the dispositions — fill before approval.

## Operator Resolutions

| # | Concern | Resolution | Status |
| :-- | :-- | :-- | :-- |
| 1 | ALLOWLIST bridge mis-sequenced | **Accepted.** D-7 rewritten: the allowlist row is removed in the **same issue and same commit** as its tag. Removal added to Issues 1.3, 2.1, 2.6, 2.9, 2.10; dropped from 2.11. 4.3 kept as the net-clean assertion. New risk row added. | resolved |
| 2 | FLOW-008 vs FLOW-004 + `remove` orphan | **Accepted — operator decision D-10:** `skills remove` KEEPS its rules write; only `upgrade`'s is removed. Issue 0.1 amends REQ-YF-FLOW-004 to scope its clause to `remove`. Issue 2.1 explicitly leaves `status.rs:165` intact and updates its doc comment. No orphaned sections. | resolved |
| 3 | Conservative-keep is hand-edit tolerance | **Accepted.** Issue 0.1 amends REQ-YF-TUNE-022 to name the rules-side guard alongside REQ-YF-TUNE-029. D-9 now states plainly that conservative-keep IS a narrow grant of hand-edit tolerance on the revert path — amended rather than left contradicted. | resolved |
| 4 | #160 causal mechanism left live | **Accepted.** New Issue 1.6 runs the sandboxed `bd init`-with-git-origin probe. If confirmed: reorder `repair()` and correct the false `:461` label. If refuted: record it in `findings/`. New Success Criterion 4 requires the hypothesis be settled in writing either way. | resolved |
| 5 | Fifth land-the-plane site dropped | **Accepted.** `coordinator.md:114-116` added to Issue 1.7 (all five sites). plan.md corrected 'Four' → 'Five'. Criterion 3 names all five explicitly. | resolved |
| 6 | Criterion 7 unmeetable | **Accepted — operator decision:** ignore-list extended with `**/.scratch/**` and `**/test-harness/topology.txt`, covering all 7 measured leftovers. Criterion 8 splits the unit test (the gate) from the live-machine check (a recorded operator step), resolving the sandbox-discipline tension. | resolved |
| 7 | `agents` harness loses rules | **Accepted — operator decision D-11:** new Issue 2.2 adds an `agents` `RULE_TARGETS` row (`RulesDir`, `~/.agents/rules`), sequenced BEFORE the cross-harness proof. Issue 0.1 amends REQ-YF-TUNE-020. Criterion 5 requires tune to serve all five, `agents` included. | resolved |
| 8 | `gh`-failure INCONCLUSIVE unowned | **Accepted.** Issue 3.2 gains an explicit sub-step for a non-raising call path used only by the resolver; existing `run()` callers keep fail-fast. New risk row covers the shared-helper regression. | resolved |
| 9 | #143 validator has no test | **Accepted.** Issue 3.8 ships a test script covering all three states (fail/warn/pass) AND its CHANGE-VALIDATION §1 row, §3 glob and §2 fingerprint re-approval in the same issue. Issue 4.2 demoted to a final sweep. | resolved |
| 10 | Epic 2/3 over-serialized | **Accepted.** `2.8 depends-on 2.4` and `3.4 depends-on 3.2`, so the #155 and #154 sub-chains run in parallel. Approach §3 rewritten to state the justification covers only #156-before-#154. | resolved |
| 11 | 14-bundle repair unverified | **Accepted.** Issue 3.7 ships `--dry-run` as default plus a mandatory `resume-scan total > 0` postcondition across all 14, and a new human capability gate guards the apply step. Risk row now names the real risk (mis-mapping, not data loss) and that `docs/plans/` is git-tracked. | resolved |
| 12 | Restated risks; missing rows | **Accepted.** Issue 1.7 orders its edits script-then-prose so the 19 drift edges resolve in one pass. Risk rows added for the stale-allowlist window, the `agents` loss, the `remove` orphan, and the live-DB mutations in 3.1/3.6. | resolved |
| 13 | Count/citation errors | **Accepted.** Counts corrected to 5 epics / 38 issues; citation corrected to `SPEC.md:856-859`; the validation-dark claim now notes Issue 0.5 edits `coverage.rs` and does fire FAST. `upstream-triage.md` Disposition and Notes filled for all 10 issues. | resolved |
| 14 | Epic-independence claim conditional | **Accepted.** Risk row reworded: independence is a consequence of the same-commit allowlist discipline, not independent of it. | resolved |
