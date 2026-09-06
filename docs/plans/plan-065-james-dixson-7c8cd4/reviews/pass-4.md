---
type: Review
okf_spec: OKF-PLAN
description: 'Review pass-4 - plan-065 red-team cycle 4, verdict APPROVE, 10 concerns none high, converged'
---

# Review pass-4 — plan-065 (cycle 4)

## Verdict: APPROVE

Three cycles of remediation have converged. Nothing found this pass risks the corpus, blocks a
criterion, or repeats the pass-2 data-loss class. **No high-severity concern. Approve; fix the
mediums before intake.**

## Strengths

- **DAG mechanically clean**, verified by hand and by extraction: 37 issues / 48 edges / 5 gates /
  15 criteria — matching the plan's own claim exactly. Zero duplicates, dangling refs, self-edges,
  cycles, **zero forward dependencies**; exactly one leaf (`6.2`), two roots. All of C7's new edges
  verified by ancestor computation.
- **The consolidation cost nothing in coverage.** All ten subcommands checked against pass-3's ten
  scripts: every assertion survived, including the three load-bearing ones. Coverage went **up**
  (SC15). The single-point-of-failure worry is answered structurally — the script is proven by
  `negative-controls` before any of it is trusted.
- **The `--input` + exit-2 contract is the right answer to the `FileNotFoundError` problem.**
  Measured: all ten subcommands exit **2** today (script absent), making "instrument absent"
  mechanically distinguishable from "condition false".
- **D2's repair verified end-to-end by spike**: with all 8 committed, default `backfill` halts 8;
  `--reconcile-objective` gives 7/1; after Epic 2's repair on plan-030, **`transformed 8, halted 0,
  exit 0`**.
- **4.4's round-trip verified byte-identical**: `post_reversal == pre_backfill` and
  `post_reapply == post_backfill`; all three `restore-roundtrip` conjuncts hold.
- Every quantitative claim reproduces. `doc_lint` exit 0, `gate_consistency` PASS, audit exit 0.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | medium | **MEASURED FALSE claim in the plan.** 4.4 said `--reconcile-objective`'s omission "was measured to HALT (`mutated 0, halted 1, exit 1`)". On the post-Epic-2 tree 4.4 actually runs on, a bare re-apply of the restored plan-030 gives `transformed 1, halted 0, exit 0`. plan-030 is **not** objective-divergent. The signature quoted belongs to an **un-repaired** plan-030; pass-3 measured a pre-Epic-2 tree and generalized to a post-Epic-2 step |
| C2 | medium | **4.3b's `git status` assertion is false by construction and fires mid-apply.** The tree also carries `plan065_checks.py`, a modified `CHANGE-VALIDATION.md`, and the plan's own `findings/*.json` — all uncommitted by design. A spurious failure at that moment tempts the executor to waive the ONLY check covering the 62 non-target bundles |
| C3 | low-medium | **Issue 0.6's registration, run at Epic 0, turns the FAST tier red for the whole execution.** §3 Trigger Scope maps globs to FAST; these two subcommands only go green after Epic 4. Also cites a "§4" that does not exist (manifest has 0-3) |
| C4 | low-medium | **The "measured (cycle 3)" paragraph is wrong again — SC9 is RED today**, `first_failure: okf-index-drift`, because `reviews/pass-3.md` is absent from `index.md`. Second cycle running this paragraph stated a colour that flipped before it was read. It also falsifies SC9's *classification* |
| C5 | low | **Four stale cross-references left by the C10 renumber**: D6's "Issue 0.6" (now 0.3), ":338"'s "Issue 0.4" (now 0.1), "Issue 0.5b" (now 0.5), and a plural `plan065_*.py` glob |
| C6 | low | **Stale `manual:` accounting** — "Four of the fourteen"; measured, fifteen criteria and exactly three prose rows (SC10, SC11, SC14). SC13 became command-form in cycle 3 |
| C7 | low | **SC15's verification is a bare substring grep** — a comment or stale line satisfies it |
| C8 | low | **4.5 and 5.4b disagree about who commits the records** |
| C9 | low | **Issue 0.4 does not say WHERE mutations happen.** A literal reading for `no-engine-edits` means editing a `skills/**/*.py`, breaching SC12 |
| C10 | low | pass-3's table used `medium-low`, off `doc_lint`'s closed vocabulary |

## Missing

Nothing structural — every gap pass-3 listed is filled. The one genuine absence: what happens if
**4.4's restore fails on the real corpus**. D5 states the pre-commit rollback route but 4.4 does
not reference it. One cross-reference.

## Gate Assessment

Five gates; `gate_consistency.py` PASS; all five reachable, **none with a condition inside its own
Blocks set**. **Sandbox rehearsal green** at its reachability floor, non-vacuity closed by 3.5.
**Corpus apply authorization** at its floor. **Upstream write authorization** — pass-3's C8 fully
resolved: Issue 5.6 sits in Epic 5, outside the Blocks set, and `5.6 ∈ anc(6.1)` verified; the gate
is now at its true floor rather than the Start Gate. **No frontloading miss remains.**

## Upstream Assessment

**The three-cycle residual on the primary issue is finally cleared.** #359's most specific criterion
— "`restore` exercised on a real bundle" — is now dischargeable, verified end-to-end by spike rather
than by reasoning. The one remaining defect on that path (C1) is a false *justification*, not a
broken command: the command as written produces a byte-identical round-trip.

SC10's expansion to four defects, naming `restore`'s unchecked `git checkout` return code inside
the criterion text, closes pass-3's outward-facing loss. **That fourth defect is the most valuable
thing this plan produces and it can no longer be the one silently dropped.** Coarse-granularity
policy respected.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | medium | **Accepted, and independently re-measured before acting**: plan-030's `README.md` `>` line and `plan.md` H1 are byte-identical, and its only halt is `phase-log-loss`. The false parenthetical is removed; the flag is retained for symmetry with 4.2 with that reason stated. The error is recorded in the plan rather than deleted — propagating a measurement from the wrong tree state is the exact class this plan exists to guard against. | `main-session` | `resolved` |
| C2 | medium | **Accepted.** 4.3b now carries an explicit allowlist (8 targets, the record, the plan bundle, `plan065_checks.py`, `CHANGE-VALIDATION.md`) and asserts nothing else appears, with a note that the allowlist is not slack — a spurious mid-apply failure would tempt a waiver of the only check covering the 62. | `main-session` | `resolved` |
| C3 | low-medium | **Accepted.** The registration moved out of Epic 0 to new Issue 5.4c (`depends-on: 4.5, 0.1`), registered FULL-tier only, so the rows never exist while they would be red. "§4" corrected to "§3 Trigger Scope"; the manifest has sections 0-3. | `main-session` | `resolved` |
| C4 | low-medium | **Accepted.** SC9's colour is no longer pinned. The paragraph now explains the structural cause — the FULL tier includes `okf-index-drift`, which goes red on every added review artifact and green after 5.2b — so SC9 is a regression criterion for the repo and a progress criterion for this bundle. "Read SC9 by running it, never by reading a claim about it." | `main-session` | `resolved` |
| C5 | low | **Accepted.** All four corrected, then swept mechanically: every `Issue N.M` mention in the plan was extracted and checked against the 37-id list — 37 distinct refs, zero unresolvable. | `main-session` | `resolved` |
| C6 | low | **Accepted.** "Three of the fifteen"; the tree-observation sentence now names SC14 only. | `main-session` | `resolved` |
| C7 | low | **Accepted.** SC15 now runs a `registered` subcommand that parses the §1 FULL tier for a row whose command names the script, rather than grepping the file. | `main-session` | `resolved` |
| C8 | low | **Accepted, resolved in 5.4b's favour.** 4.5 commits the 8 bundles ONLY — the tightest diff is the cleanest `git revert` boundary D5 wants — and 5.4b carries all `findings/*` including both records. | `main-session` | `resolved` |
| C9 | low | **Accepted.** 0.4 now states that no mutation of the live repository occurs: tree-property controls use the current tree as-is, artifact-readers use synthesized `--input` fixtures. The literal reading would have breached SC12. | `main-session` | `resolved` |
| C10 | low | **Accepted.** pass-3's four `medium-low` tokens normalised to `low-medium`. | `main-session` | `resolved` |
| Missing | low | **Accepted.** Issue 4.4 now cross-references D5's pre-commit rollback route, noting `git revert` has no boundary until 4.5. | `main-session` | `resolved` |
