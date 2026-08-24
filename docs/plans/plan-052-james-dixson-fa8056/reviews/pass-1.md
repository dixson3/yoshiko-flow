---
type: Review
okf_spec: OKF-PLAN
id: pass-1
description: Red-team pass 1 (first independent, dispatched via Agent) — REVISE, 7 high / 10 medium / 6 low
---

# Red-team pass 1

## Verdict: REVISE

7 high, 10 medium, 6 low. **ALL 23 RESOLVED** (see Resolutions). First independent pass, dispatched as a sub-agent
per REQ-AGENT-049. Written at presentation, before any concern was resolved.

## Strengths (all verified by execution, not by reading)

- **The 96.3% class-(a) claim is TRUE** — independently recounted: 27 criteria, 26 clause-form, 1
  `manual:`. Scope figures also true (27 issues, 41 edges, `unparsed: []`).
- **The Reconcile Gate is sound and its title-prefix exclusion is load-bearing** — the reviewer ran
  the exact `jq` against live `bd` (substituting plan-051): exits 0. Confirmed `bd list` returns a
  top-level array, `metadata` is only object-or-null (so `.metadata.plan` cannot type-error), and
  plan-050/051 reconcile beads *do* carry `metadata.plan` — **so without the exclusion the gate
  would count the step it blocks. plan-051's defect is genuinely fixed.**
- **The `red-prework` Blocks-set claim checks out against the actual DAG** — control-builders
  1.1/1.3/2.1/3.1/4.1 depend only on {0.1, 0.2, 0.3}; none is in Blocks. No cycle, reachable.
- **Four `jq` paths verified against real output** — SC19/SC20/SC11b/SC12 will not die on a wrong key.
- **The honour-the-findings check passes on all four tested** — D-19, D-25, D-2, D-23.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| H1 | high | **The plan fails the repo's own mechanical intake gate right now.** `audit` exit 1, `ready-check` exit 3. Five `[fail]`: three unedited `context.md` template sections, and missing `references/upstream-113.md` / `upstream-192.md` (both added at D-27/D-29 without their reference files) |
| H2 | high | **SC1 is guaranteed to fail when re-run.** Spiked: on the merged tree `main..HEAD` is empty, so it exits 1. And the command does not decide its claim — it inspects one commit subject for `Issue 0.1`; a REQ landed *after* an implementation commit is undetectable. Class-(a)-shaped prose |
| H3 | high | **8 of 13 controls are asserted but never built.** Epics 5 and 6 have no control issue at all. `assets/controls.txt` — the `red-prework` Condition's own artifact — is produced by no node. If it lists 13 the gate is unsatisfiable; if 5, it is green while 8 controls have no RED |
| H4 | high | **SC6/SC7 make `recheck-criteria` recurse into itself.** They are class-(a) clauses whose command is `recheck-criteria` on the same `plan_dir`. Unbounded; no guard declared. One run also executes the FULL tier, the whole harness, and `yf --version` — cost and isolation unstated |
| H5 | high | **The `upstream-write` consent gate cannot fail.** It tests a *mechanically generated proposal* rather than the operator's authorization; `test -f` passes on `touch`; the tested file has no producer; and it discards the existing `grant --check assets/upstream-authorization.txt` round-trip in favour of a new filename and a weaker test |
| H6 | high | **SC21 waives a checkable claim into `manual:`** — its own text admits the count is checkable. And "eight" is not derivable: D-13(1) + D-18(4) + D-26(2) = **7**. The same unverified-count class as the R8 defect already corrected |
| H7 | high | **SC18 demands a green from a check with no input.** `grep -c '^\s*- touches:' plan.md` → **0**. Signal S1 *is* declared paths, so `ownership-report` must exit 2 by the plan's own stated rule. The plan dogfoods the `Verification` grammar but **not** the `touches` grammar it also ships |
| M1 | med | **The grammar is two-valued; D-4 mandates 0/1/2.** `→ exit non-zero` cannot separate 1 from 2. SC3 therefore PASSES when the harness is broken and exits 2 — the thesis inverted inside its own grammar |
| M2 | med | **9 of 26 commands contain a table-escaped `\|`** with no unescaping rule declared. If 1.2's extractor hands the raw cell to a shell, all nine die on a syntax error — indistinguishable from real failure under the two-valued grammar |
| M3 | med | **SC10 is a grep for a literal string against prose.** Writing `RECHECK_RC=$?` into `SKILL.md` discharges it. §6.4 is agent-followed prose, so 2.3 may have no executable caller at all |
| M4 | med | **`.coverage` is overloaded** across SC6/SC7 (class-(a) fraction) and R2/R3 (corpus/evaluated fraction). SC7's threshold is meaningless until pinned |
| M5 | med | **SC11b and SC12 are near-vacuous and depend on live state.** SC12 passes on key-presence with an empty array; SC11b needs a live tombstone and evaporates if #147 is resolved |
| M6 | med | **4.2's "mechanical predicate" is never specified** and `ctl-113-gate` has one fixture, so a `grep` for plan-050's wording would discharge SC13 |
| M7 | med | **SC23 fails after 7.5's own commit**, per AGENTS.md's documented docs-only-commit caveat |
| M8 | med | **D-15 is orphaned** — no issue, no criterion. And plan-052 has **no `tracker` row**, reproducing exactly the plan-051 condition D-15 diagnosed |
| M9 | med | **The plan names vendored copies, not canonical `_shared/`.** 1.2/1.4/3.4 all edit byte-identical pairs; drift is caught only at 7.1 |
| M10 | med | **No `CHANGE-VALIDATION` row for the new spine**, so SC19 green exercises nothing this plan ships |
| L1 | low | `red-prework` is one all-or-nothing barrier — 1.2 waits on 4.1's control; tensions with R8 severability |
| L2 | low | Two control invocation conventions; the direct `assets/ctl-*.sh` form bypasses the harness's 0/1/2 contract |
| L3 | low | "signals S1+S3" is defined only in `findings/exp-007` |
| L4 | low | `index.md` lists neither `findings/` nor `assets/` |
| L5 | low | R8's severability omits that severing also requires editing 7.1's `depends-on` and deleting SC14–SC17 |
| L6 | low | Issue 0.1 enumerates no `REQ-*` ids, so its own completion is not decidable |

## Missing

- A specified predicate for 4.2 and an escaping rule for 1.2 — the two places the plan hands an
  implementer a prose noun where the point is an exit code.
- A recursion/isolation model for `recheck-criteria`.
- Producing nodes for `assets/controls.txt` and `assets/upstream-grant-proposal.md`.
- A criterion covering 1.4's `touches[]` on real plan documents (only the fixture is covered).
- How the `Verification` grammar interacts with `plan-relations` R1b once 3.4 promotes severities —
  3.4 changes the grading of the very document being graded.

## Gate Assessment

| Gate | Reachable? | Verdict |
| :-- | :-- | :-- |
| Start Gate | n/a | fine |
| `red-prework` | **Yes** — verified against the DAG | Reachability sound; **Condition rests on `assets/controls.txt`, which no node produces (H3)** |
| `upstream-write` | **No / vacuous** | **Cannot fail (H5)** |
| Reconcile Gate | **Yes** — `jq` executed against live `bd` | **Sound. plan-051's self-blocking defect is genuinely fixed** |

Frontloading: no misses. `upstream-write` correctly late; `red-prework` at its earliest legal position.

## Upstream Assessment

Dispositions are unusually well-evidenced — #194's `exclude` carries a measurement and three named
reopen conditions. Three problems: #113/#192 have no reference file (H1); no `tracker` row (M8); and
`Resolved By: EXP-002` on the #194 row is not an issue id — tolerated today at `severity = "W"`, but
**Issue 3.4 promotes R1/R2a to gating**, so the plan may promote a rule its own table then trips.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | `context.md` §Project environment / §Operator identity / §Runtime assumptions all written with real content (the runtime section records the eight measured bd 1.1.2 limits this plan depends on). `references/upstream-113.md` and `upstream-192.md` generated from `gh`. **`audit` now exits `pass`** — verified | `main-session` | `resolved` |
| H2 | high | SC1 replaced: it now asserts every `REQ-*` id EXISTS on the merged tree via `ctl-req-landed`, which is true post-merge. The ordering claim is split out as **SC1c `manual:`**, stating why no git command can decide it (`main..HEAD` is empty; a squash erases the evidence). 0.1 now ENUMERATES the four REQ ids (also L6) | `main-session` | `resolved` |
| H3 | high | **All 13 controls now have a building issue.** Added 0.4a, 5.0, 6.0; extended 0.3, 2.1, 3.1. `assets/controls.txt` is named as a 0.2 deliverable. SC2 now asserts all 13 with Discharged-by naming all 10 builders, and the count is derived from `controls.txt` rather than asserted | `main-session` | `resolved` |
| H4 | high | 2.2 ships a `YF_RECHECK_DEPTH` guard that **REFUSES any clause naming `recheck-criteria`**, asserted by new **SC6b**. SC6 repointed at a fixture plan (`ctl-199b-fields`); SC7 repointed at `ctl-class-a-fraction`, which reads `plan_extract` output directly and never invokes the verb. Recursion is structurally impossible | `main-session` | `resolved` |
| H5 | high | Gate Test replaced with the existing round-trip: `plan_manager.py grant … --check assets/upstream-authorization.txt --json`, which exits non-zero naming every uncovered action — so a `touch`ed empty file FAILS. Condition reworded to the operator's authorization. 7.2 (outside Blocks) generates the PROPOSAL; only the operator writes the AUTHORIZATION | `main-session` | `resolved` |
| H6 | high | Split into **SC21a** (class-(a): count derived from `assets/deferred-defects.md` via `ctl-deferred-count`) and **SC21b** (`manual:`, substance only, with the split stated as deliberate). Count corrected **8 → 7** and enumerated explicitly in 7.2: 3 bd defects + `REQ-PLAN-073` collision + 2 instrumentation + 1 run-record | `main-session` | `resolved` |
| H7 | high | **`- touches:` added to all 30 issues — measured 30/30 = 100%.** New **SC5c** asserts >= 80% coverage. SC18 split: SC18 now asserts the INCONCLUSIVE-on-no-input contract (`ctl-ownership-inconclusive`), SC18b the report-only property. The plan now dogfoods BOTH halves of Epic 1 | `main-session` | `resolved` |
| M1 | med | Grammar is now THREE-valued — `→ exit 0`, `→ exit 1`, `→ exit 2`, with `→ exit non-zero` permitted only where 1 and 2 are equivalent for the claim. **SC3 restated to `→ exit 1`**, so a harness broken into INCONCLUSIVE no longer passes the criterion asserting it is not a silent green | `main-session` | `resolved` |
| M2 | med | 1.2 now ships the GFM unescape rule (`\|` → `|`, `\\` → `\`) explicitly, stated in the Approach grammar note. 1.1's fixture MUST include a piped command, asserted by SC5's third clause. Added **R9** naming the 9 affected clauses | `main-session` | `resolved` |
| M3 | med | SC10 restated against **observed behaviour** — `ctl-199b-halt` drives a fixture where the re-check fails and the close chain is shown to stop. 2.3 reworded: the VERB exits non-zero (as `verify-reconcile` does at `plan_manager.py`), not a prose instruction to read `$?` | `main-session` | `resolved` |
| M4 | med | Two distinct fields named in 2.2: **`class_a_fraction`** and **`evaluated_fraction`**. SC6 asserts both are reported as distinct numbers; SC7/R3 use `class_a_fraction`; R2 uses `evaluated_fraction` | `main-session` | `resolved` |
| M5 | med | SC12 now uses `all(.issues[]; (.beads|length)==0 or ((.close_reasons|length) > 0))` — a present-but-empty key no longer passes. SC11b and SC11 repointed at a **pinned fixture** (`assets/closable-fixture.json`, built by 3.1), so the control cannot evaporate when #147 is resolved | `main-session` | `resolved` |
| M6 | med | Predicate stated mechanically in 4.2: *no issue listed in a gate's `Blocks` is also named in that gate's `Condition`, `Test` or `Instructions` as producing the gate's own evidence*. 4.1 now requires **two positive and two negative fixtures**, with the note that one fixture is grep-satisfiable and proves nothing alone | `main-session` | `resolved` |
| M7 | med | 7.5 reworded to rebuild-then-verify **after the final commit**, and SC24 (was SC23) is asserted via `ctl-deploy-stamp` which encodes that ordering. AGENTS.md's docs-only-commit caveat is the stated reason | `main-session` | `resolved` |
| M8 | med | 7.3 now explicitly records the `tracker` row, with the honest note that the row **cannot exist before the issue is filed** — which is why new **SC23** asserts the END STATE (the epic carries an `external_ref`) rather than the `stamp-tracker` route that returns `skipped`. This is D-15, now scoped rather than orphaned | `main-session` | `resolved` |
| M9 | med | 1.2, 1.4 and 3.4 now name **canonical `_shared/`** first with the vendored copy synced, in both the issue text and the `touches:` lists | `main-session` | `resolved` |
| M10 | med | 7.1 now LANDS the `CHANGE-VALIDATION.md` recipe rows and trigger-scope globs before running FULL, and SC19 is restated via `ctl-cv-rows` to assert the rows are present — *a green that exercises nothing is not a green* | `main-session` | `resolved` |
| L1 | low | `red-prework` split into **`red-prework-core`** (Epics 0-4) and **`red-prework-ext`** (Epics 5-6). Epic 1 no longer waits on an Epic 5 control, and the split reinforces R8's severability | `main-session` | `resolved` |
| L2 | low | Every control now runs through `gate-run.sh run <ctl-id>`; the direct `assets/ctl-*.sh` form is gone, so all 13 inherit the harness's 0/1/2 contract | `main-session` | `resolved` |
| L3 | low | 1.5 now defines the signals inline — shared declared paths (S1) and DRIFT-CHECK edges (S3) — and names the excluded ones with their measurements (S2 p=0.85, S4 fired 0 times), to be recorded in a code comment | `main-session` | `resolved` |
| L4 | low | `index.md` updated to list `findings/` and `assets/` | `main-session` | `resolved` |
| L5 | low | R8 now states severing requires **three** edits: remove 5.x/6.1 from 7.1's `depends-on`, delete SC14–SC17, and drop the `red-prework-ext` gate | `main-session` | `resolved` |
| L6 | low | 0.1 enumerates its four REQ ids — `REQ-DATA-070`, `REQ-DATA-071`, `REQ-PLAN-080`, `REQ-BUP-070` — so its completion is decidable | `main-session` | `resolved` |
