---
type: Review
okf_spec: OKF-PLAN
pass: 6
---
# Red-team pass 6 — plan-048-james-dixson-ed68a5

## Verdict: REVISE

One genuine execution-blocking defect, introduced by the pass-5 H1 fix itself. Everything else is
medium or below. **The partial-landing pattern held again but at much lower amplitude** — 2 of 15
items landed in one file and not its sibling, versus 3 of 11 last pass.

## Part B — mechanical verification

5 epics, 38 issues, 60 edges, 5 gates, 26 criteria, `unparsed: []`; **no cycles**, single root `0.1`,
single leaf `4.7`. `doc_lint` exit 0 on **all 29** bundle files; `audit` pass; `okf.py check` OK;
`markdown_lint` clean on all 29. **Gate ancestry clean for the third consecutive pass.**

Re-measured independently: 150 unparsed across **33 of 48**; `files_checked` **180**, `report_only`
**610** (reproduces exactly); no `tests/fixtures/doclint/reference/` (2.1b real); the two-parser
disagreement live at `plan_manager.py:3908` vs `plan_extract.py:368`; 19 skill dirs; all 10
non-exclude upstream issues OPEN. **The R1b self-report matches an independent derivation exactly.**

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| H-A | **high, blocking** | **The `deferred` end-state contract has no producer.** `_mentions_plan_id` (`:1992`) scans only issue comments; `verify_reconcile` filters to `disposition not in ("", "exclude")` — 10 of 13 rows including all five `deferred`. **No issue posts to #140, #149, #165, #62 or #135**, so all five return `fail` at a halting step. Pass-5's H1 in a new costume: the failure moved from "unrecognised disposition" to "recognised disposition whose contract nothing satisfies". Worse, 0.2 and SC33 now state incompatible readings |
| H-B | **high, blocking** | **SC33 is unsatisfiable at its discharge point.** Discharged by 3.4a, which runs before Epic 4 — at which point #172 and #175 are OPEN (must be CLOSED → `fail`) and #113/#173/#174 carry no mention (→ `fail`). It returns `fail` however correct 3.4a is, and cannot distinguish a wrong branch from "reconcile has not happened yet". **SC33 was written without being executed** — #173 defect 1, inside the criterion added to fix #173 |
| M1 | med | **The `Resolved By` column and the `resolves-upstream` edges disagree** — the table moved #113/#174 to 4.5a; the machine-readable sub-key still sits on **4.4 (draft-only)**. This plan's own R2a would not catch it, because 4.5a exists |
| M2 | med | **D-7's literal never reaches the producer** — `SKILL.md:273`, `plan_manager.py:1011` and `README.md:15` still offer four options. Visible inside this bundle: `upstream-triage.md`'s own header offers four while five rows say `deferred` |
| M3 | med | `744` landed in plan.md but not in `findings/exp-002` (still `~700`) — the citation was corrected and the source was not, which is backwards under D-5. The plan.md cell is also malformed nested emphasis |
| M4 | med | **`47 → 48` was marked resolved and nothing changed.** The number is defensible as point-in-time; the defect is the false resolution record |
| M5 | med | **SC1's verification exits 128** — `git diff --stat docs/plans -- ':!…'` parses the path as a revision. Correct form puts everything after `--` |
| M6 | med | **Epic 3 adds a new engine mechanism with no SPEC amendment** — REQ-DATA-024 declares two schema flavours and a per-document contract; a `plan-relations` kind reasoning across sections is a third, and SPEC-first is non-negotiable |
| L1 | low | R7 reads 37 issues; measured **38** — #135's exact class, which this plan defers |
| L2 | low | D-9/D-11 bodies still read as live imperatives citing Epic 9 / `9.1 → 8.9` |
| L3 | low | 3.4a justifies preserving `tracker` by "D-2's coarse tracker relies on it" — this plan has **no** `tracker` row |

## Gate Assessment

All five gates structurally sound, verified by transitive ancestor set. No cycles, no condition
depending on its own `Blocks` set, each gate at the **first successor** of its evidence — no
frontloading miss. `gate-run.sh` correctly separates harness failure (127→2) from capability-absent.
**Third consecutive clean pass; the design is now genuinely good.** The Reconcile Gate's sentinel is
correct — the step it gates halts because of H-A, not because of the gate.

## Upstream Assessment

Still the strongest section. All 13 rows and dispositions agree across `plan.md` and
`upstream-triage.md`; both D-13 re-dispositions recorded in both files; all 10 non-exclude issues
confirmed OPEN from the vendored bodies; #173 defect 2 confirmed live in code. Two defects land here
(H-A, M1) and both are consequences of the `deferred` literal rather than of the triage — which
remains the right trade.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H-A | high | **Option (a) taken:** Issue 0.2 defines `deferred` as **OPEN, report-only — no mention requirement**, matching `tracker` in the same issue. Principled, not merely cheap: a deferral is a *non-action*, so there is nothing to attribute upstream; `deferred` earns its keep at the R2c self-test (SC9), not at reconcile | `main-session` | resolved |
| H-B | high | SC33 re-scoped to a **synthetic table fixture** exercising each literal's pass and fail case — which is what 3.4a's own text already promises. A live run over the real table is not gradeable before the posts land | `main-session` | resolved |
| M1 | med | `resolves-upstream: #113 (partial), #174 (partial)` moved from 4.4 to **4.5a** | `main-session` | resolved |
| M2 | med | Issue 0.2 extended to the three producer surfaces; SC9 asserts the offered set contains `deferred` | `main-session` | resolved |
| M3 | med | `exp-002` corrected to 744 with its derivation; the malformed plan.md cell rewritten as two clauses | `main-session` | resolved |
| M4 | med | The six `47`s changed to **48**, measured | `main-session` | resolved |
| M5 | med | Pathspec corrected to `git diff --stat -- docs/plans ':!docs/plans/plan-048-*'` | `main-session` | resolved |
| M6 | med | New **Issue 0.7** amends the SPEC to declare the `plan-relations` check kind, its `plan_extract` dependency, the R-rule family's `W` severity, and R1b's bookkeeping carve-out | `main-session` | resolved |
| L1 | low | R7's count derived from `plan_extract`, not retyped | `main-session` | resolved |
| L2 | low | D-9/D-11 reframed as "for plan-049: …" | `main-session` | resolved |
| L3 | low | 3.4a's `tracker` justification restated — other plans use it, REQ-CLI-018 specifies it; not this plan's row | `main-session` | resolved |
