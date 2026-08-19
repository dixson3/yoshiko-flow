---
type: Review
okf_spec: OKF-PLAN
id: pass-1
---
# Red-team pass 1 — plan-047-james-dixson-dec9ff

## Verdict: REVISE

**Date:** 2026-08-18 · **Status:** all concerns resolved

Preceded by a conformance pass returning INCOMPLETE (6 gaps, all resolved before this review:
empty `Resolved By` column, blank `upstream-triage.md`, 31 issues discharged by no criterion, a
consent gate with no Test, R1 mitigating with prose only, `index.md` missing `findings/` and
`references/`, and 8 numeric disagreements).

## Strengths

- The 40% pour-defect headline was **independently reproduced**: `comparable: 43, clean: 26,
  dirty: 17` → 39.5%, `dropped 45, invented 20`. Exact match.
- #166 reproduced: `bd list --all` → 1290 beads / **0 gates**; `--include-gates` → 1411 / 121.
- **D-2's hash-neutral transform set is exactly right** — `_plan_content_fingerprint`
  (`:2151-2167`) does per-line `rstrip`, drops blank lines, excludes `## Upstream Issues` and the
  header preamble: precisely the four transforms D-2 names. `okf.py:1173` resolves verbatim.
- EXP-005's headline re-verified: `update_status` (`:1312`) has no enum, no gate, docstring says
  "free-form". **Issue 8.1's "zero call-site edits" claim is CORRECT** — `_audit_plan` computes
  `any_fail = any(...)`, so an appended finding propagates automatically.
- Both `CHANGE-VALIDATION.md` defects verified live; the #164 vacuous green reproduced.
- **All `file:line` citations resolve** — checked individually.
- Epic DAG clean: 68 issues, 0 dangling, 0 backward-epic edges, **0 cut violations** — nothing in
  Epics 0–4 depends on 5–9, so Epic 4 is a genuine cut line.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| H1 | **high** | **The Epic-1 gate Test is permanently unsatisfiable.** It reads `d["layer_b"]["commands"]`; `layer_b` does not exist anywhere in the repo. Executed: exit 1 today, and exit 1 on a simulated post-work success shape (KeyError). Non-vacuous only by accident — it crashes. SC3 is therefore unachievable | `d["layer_b"]["commands"]` → `d["commands"]`, then re-verify it still fails pre-work |
| H2 | **high** | **Epics 1 and 2 both require the Epic-3 linter, which no declared predecessor produces.** Issue 1.1 adds a §1 row naming a command that does not exist until 3.2; Issue 1.4 must inject a mutant and see the linter exit 1; Issue 2.4 must "run the prototype linter", which EXP-005 states is **not committed**. Both gates' `Instructions:` ("satisfied by completing Epic 1/2") are **false**. Epic 1 also red-lights the repo's own FAST tier for the duration of Epics 1–3 | Either add a minimal `doc_lint.py` skeleton as Issue 1.0, or re-order: engine skeleton (3.1–3.2) → carve-outs → gate wiring. Fix both `Instructions:` |
| H3 | **high** | **D-9's "140 files fail on day one" is falsified by EXP-005 in the same investigation.** EXP-004 inferred it; EXP-005 measured "automatic paths that re-audit a `complete` plan: **none**" → "a hard linter gate at INTAKE breaks **zero** existing plans." Issue 3.4 independently dissolves the residue. Cost of the unexamined inference is structural: it forces Epic 7 (10 issues + a human gate + a 46-bundle rewrite) ahead of Epic 8, which contains **Issue 8.2 — the only fix for the enforcement hole EXP-005 calls the real headline** — landing it at position 63 of 68, on the far side of the D-13 split | Re-state D-9 honestly (the 140 is binding-point (c)'s hazard, mitigated by 3.4/3.5, not INTAKE's) and **hoist 8.2+8.3 into Epic 1 or 2** |
| H4 | **high** | **Issue 4.6 / SC14's premise is false, verified by execution.** `_ci_release_scan_region` (`:1616-1644`) is **already section-scoped** — its own F1 excludes Approach, F5 strips fences. Executed: plan-026 → `signals: []`, plan-027 → `signals: ["pipeline"]`. Zero double-counting. EXP-003 inferred this from its own grep and never read the code; the plan promoted the inference to "Measured:" | Delete Issue 4.6 and SC14, or re-scope to the genuine residual with a criterion that fails today |
| H5 | **high** | **D-7/SC1's "byte-identical to `seed_plan_md`" is infeasible and self-defeating.** The seed emits `_To be determined._` bodies and no frontmatter literal; SKILL.md teaches the epic/issue/gate grammar. Byte-equality **deletes that grammar from the one place authors read it** — the grammar Issues 3.1/4.1/5.3 must derive the schema from. The two halves of D-7 contradict | Replace with structural equality on the heading + required-field set, or generate the SKILL.md block from `seed_plan_md` via `_shared/sync.py`'s marker fence, keeping the illustrative grammar outside the fence |
| H6 | **high** | **`Blocks: epic:<N>` is a form nothing parses**, introduced before the REQ that defines it, in the field the plan itself measured as weakest. Nothing parses `Blocks:` at all; the pour translates it by LLM into per-issue `dep add` lines. `epic:3, epic:5` requires expanding to 17 dep-adds, in a form occurring **0 times** in 72 historical values | Write the two gates as explicit issue-id lists — the only form the pour is documented to handle — and let 0.4 introduce `epic:<N>` for future plans |
| M1 | medium | **"45 dropped" conflates two populations.** 43 of 45 come from plans 006/007/036, exactly the three with "no recoverable plan↔bead mapping" — an artifact of missing identity, not dropped edges. Restricted figure: 2 dropped / 20 invented. Also plans 041–046 are 0/0, which Motivation does not reflect | SC28 should state a three-way decomposition and require the post-work run to report the same |
| M2 | medium | **No coarse tracker row.** AGENTS.md mandates one per plan-scale effort. `stamp-tracker` will return `skipped`, leaving the epic without an `external_ref` and **invisible to `upstream.py closable`** — the exact failure #131 exists to prevent | File the tracker at intake, add the `tracker` row + `**Coarse tracker:**` line, add an Epic-9 issue |
| M3 | medium | **Issue 8.3 contradicts its own DAG** ("before implementing 8.2" vs `depends-on: 8.2`), and the collision does not exist as stated — `update_status` has no options besides `-m`; the "existing `--force`" is a **prose convention** (SKILL.md:1540) | Flip the edge; restate 8.3 as reconciling with the three prose `--force` overrides |
| M4 | medium | **The refusal predicate is half-inert on an unmeasured axis.** Measured: `complete=46`, but `have_stored_fingerprint=25`. **21 of 46 carry no stored fingerprint**, so `stored == current` is False and the predicate does not refuse them. SC21 builds only a non-complete fixture | SC21 must exercise all three branches and the plan must state the intended behaviour for the 21 |
| M5 | medium | **The evidence for the headline number is untracked** — `exp003/*.py` is `?? exp003/` in a worktree yf-plan tears down with `worktree remove --force` | Add Issue 0.0 copying the prototypes into the bundle with the exact reproduction invocation |
| M6 | medium | **The Epic-2 gate Test checks 2 of its 3 declared carve-outs and runs no positive control** — the **vendored** carve-out, the D-11 P0, is untested. The Condition/Test divergence class Issue 1.4 exists to prevent, one gate later | Add the vendored predicate; make the positive control an executed step of the Test |
| M7 | medium | **The Upstream-write gate Test already passes** — exit 0, because `comment-113.md` exists | Assert the count matches the 7 non-exclude rows |
| M8 | medium | **Four new REQs are unallocated** (0.5–0.8 say "REQ for X" with no id), and SC2's `cargo test` clause is vacuous for them: `coverage.rs:182` reads **root SPEC.md only**, and new `REQ-DATA-*` land in `spec/data.md` | Allocate the ids now; replace SC2's clause with a grep keyed on them |
| M9 | medium | **D-13's trip condition is half-prose and Issue 9.0 has no exit code.** "reopened twice" is not mechanical — `bd` has no reopen counter. 9.0 is an ordinary bead with no gate and "otherwise a no-op": **#149's M5 sitting inside the mitigation for R1, the highest-severity risk** | Give 9.0 a runnable command emitting `{tripped, review_cycles, reopened}` and exiting non-zero when tripped; or key solely on review cycles |
| M10 | medium | **D-2a's protected set is a frozen, unenumerated count.** EXP-006 says 17 plans; an independent sweep of fully-qualified citations finds **104 occurrences across 22 plans**. If the executor restricts 17 and the real set is 22, five get blank-line collapse and break silently | 7.3 must derive the set at execution from a committed script and print it; SC22 asserts over the derived set |
| M11 | medium | **Gate `Test:` shapes are hazardous at pour** — Gate 1's is a fenced multi-line block (the class Issue 4.2 exists to handle) and all three embed single-quoted `python3 -c`, which must survive `printf` → `jq --arg` → `bd create --metadata`. The plan forbids this class while using it | Move each Test into a committed one-line script; make `Test:` a bare invocation |
| L1 | low | Stale internal count: D-13 says 67 issues, R1 says 68, parsed value is 68 — **#135's exact shape inside the plan that dispositions #135** | Fix to 68; cite as a live specimen |
| L2 | low | Issue 8.1 says "after check #9"; the docstring enumerates checks (1)–(8) | Say "appended after the existing checks" |
| L3 | low | `SKILL.md:395-412` is the wrong slice; the block runs 365–420 and D-7's argument turns on the excluded header region | Correct the citation |
| L4 | low | "the tiers are identical" is inaccurate — `full` has an empty `id` column on every row and includes `cargo clippy` | Restate |
| L5 | low | "≈73% precise" is n=11 across 2 plans, not a corpus statistic. The decision (D-5) is endorsed regardless | Label it as n=11 |

## Missing

1. The **coarse tracker** (M2).
2. **An issue declaring the `references/**` structural exclusion glob** — 8.4 lists it as one of four
   mechanisms but no issue in Epics 2 or 3 creates it.
3. **A rollback path for Issue 7.8b** — no abort/revert criterion, and nothing covers 7.5 finding a
   miss after 7.8b lands.
4. **Which side of the D-13 split Issue 9.0 lands on** — it `depends-on: 4.6`, so functionally in
   the 0–4 half while structurally in Epic 9.
5. **The read-back trap on Epic 0's own deliverable** — Epic 0 edits `skills/yf-plan/SKILL.md`, but
   the executing session's prose came from the *installed* copy and was loaded once at invocation.
   Anyone verifying 0.1 mid-run reads the wrong artifact. (The `plan_manager.py` half is genuinely
   safe — the repo `skills/` tree matches none of the resolver's six roots.)
6. **Per-issue criterion coverage in Epic 5** — SC15 is one criterion for ten issues and is
   satisfiable by ten empty `.toml` files. The weakest joint in the plan's claim to satisfy its own
   bidirectional rule.

## Gate Assessment

| Gate | Ran? | Exit today | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | n/a | — | Fine |
| doclint row executes and fail-closes | **yes** | **1** (KeyError on `layer_b`) | **BROKEN** — unsatisfiable post-work too (H1); `Blocks:` unparseable (H6); `Instructions:` false (H2); fenced multi-line Test (M11) |
| carve-outs detectable | **yes** | **1** (`Failed to spawn`) | Non-vacuous, but covers 2 of 3 regions, no positive control (M6); Condition unsatisfiable at Epic 2 (H2) |
| normalizer aggregate diff | **yes** | **1** (no diff artifact) | **The best gate in the plan** — correctly separates precondition from authorization, correctly typed `human`, reachability sound. Caveat: `fingerprints_moved` is an output key of a not-yet-designed tool; pin it in 0.6 |
| Upstream write | **yes** | **0** | **VACUOUS** (M7) |
| Reconcile Gate | n/a | — | Correct form |

**Reachability:** no cycles — every Condition's evidence is produced strictly upstream of what it
Blocks. But the doclint gate is placed *earlier* than its evidence allows (the inverse of the usual
frontloading miss), and two gates' `Instructions:` misname their satisfying epic.

**Criterion falsification (30 total):** SC3 unachievable, SC14 vacuous, SC1 infeasible, SC2 vacuous
for the new REQs, SC21 tests 1 of 3 branches, SC28's baseline not comparable, SC15 satisfiable by
ten empty files. **The remaining 23 genuinely fail against the pre-work tree — above this repo's
historical bar.**

## Upstream Assessment

Dispositions verified **against the enforcing code**, not the table. `_verify_row` (`:1992-2040`):
`include` → CLOSED + plan-id mention; `partial` → **OPEN** + mention; `supersede` →
CLOSED/NOT_PLANNED; anything else → `inconclusive`, never halting. `exclude` filtered at `:2064`.

- **5 partials** all stay OPEN ✓ — SC29 matches the engine's literal requirement. #113's reasoning
  ("its own re-open trigger is not met — plan-046's escapes were claims-class, not ordering-class")
  is the strongest in the triage.
- **2 includes** must be CLOSED. #125 is squarely closed by 8.2. **#165 is the risk**: SC17 promises
  no false clause, but only 13 of 226 are executable and 6.6 defers the 85% bound. Defensible as
  `include` — the *class* is addressed — but **9.3/9.4's comment must say so explicitly or the
  closure overclaims**.
- **Gap:** no `tracker` row. `verify-reconcile` returns `inconclusive` on tracker rows and never
  fails, so **SC29 passes green with the tracker missing entirely**.

## Operator Resolutions

| # | Resolution | Status |
| :-- | :-- | :-- |
| H1 | Gate Test rewritten. `d["layer_b"]["commands"]` → `d["commands"]`, and per M11 the Test is now a committed script (`scripts/gate-doclint.sh`) rather than an inline fenced block. Verified to fail pre-work | resolved |
| H2 | **Epic order restructured** (operator-approved): minimal engine (Epic 1) → carve-outs (Epic 2) → gate wiring and falsification (Epic 3) → full engine (Epic 4). Both gates' `Instructions:` now name the epic that actually satisfies them. No §1 row points at a nonexistent script | resolved |
| H3 | **D-9 amended** to state the 140-file figure as the on-edit trigger's hazard, mitigated by Issue 4.2's status-aware promotion — not INTAKE's. **Issues 2.5/2.6 hoisted from Epic 8 to Epic 2** (operator-approved), moving the enforcement fix from position 63 of 68 to the first third | resolved |
| H4 | **Issue 4.6 and SC14 deleted.** The premise was false — `_ci_release_scan_region:1616-1644` is already section-scoped. The deletion and its reasoning are recorded inline in the Epics section rather than silently removed | resolved |
| H5 | **D-7 amended** from byte-equality to structural equality via `_shared/sync.py`'s marker fence, with the illustrative epic/gate grammar kept **outside** the fence. Issue 0.2 implements it | resolved |
| H6 | Both capability gates rewritten to explicit issue-id lists. Issue 0.4 now scopes `epic:<N>` to **future plans only**, stating that nothing parses `Blocks:` today | resolved |
| M1 | Issue 5.3 reports three populations separately; SC18 and SC37 assert the decomposition | resolved |
| M2 | Coarse tracker added to Epic 10 (Issues 10.3, 10.5) with SC39 asserting `stamp-tracker` records an `external_ref` rather than returning `skipped` | resolved |
| M3 | Edge flipped — Issue 2.6 (name the flag) now precedes 2.5 (implement it). The collision is restated accurately: `update_status` has no options besides `-m`; the overlap is with three **prose** `--force` conventions | resolved |
| M4 | Issue 8.2 states the no-fingerprint behaviour explicitly (21 of 46 plans); SC28 exercises all three branches | resolved |
| M5 | **Issue 0.0** added — copies `extract_plan.py` and `pour_fidelity.py` into `assets/` with the reproduction invocation. No dependencies, runs first | resolved |
| M6 | Epic-2 gate now covers **four** regions including the vendored carve-out, and the positive control is an executed step of the script | resolved |
| M7 | Upstream-write Test now asserts `>= 8` comment files (tracker + 7 non-exclude rows). Fails today | resolved |
| M8 | Six ids allocated (`REQ-DATA-018`…`023`). SC4 replaces the vacuous `cargo test` clause with a grep keyed on the ids, and Issue 0.9 states the `coverage.rs` root-SPEC-only bound | resolved |
| M9 | The "reopened twice" clause **dropped** — no `bd` reopen counter exists. D-13 now keys solely on `ls reviews/pass-*.md \| wc -l`; Issue 10.0 emits `{tripped, review_cycles}` and exits non-zero. SC36 verifies by forcing the condition | resolved |
| M10 | Issue 8.3 derives and prints the protected set at execution; SC29 asserts over the derived set. Both counts (17 and 22) recorded in D-2a as non-authoritative | resolved |
| M11 | Issue 3.4 added — all gate Tests become committed one-line scripts. SC12 asserts it | resolved |
| L1 | Counts now generated from the parsed document at each edit, not transcribed. Cited as a live specimen in Issue 7.3 | resolved |
| L2 | Restated as "appended after the existing checks" | resolved |
| L3 | Corrected to `SKILL.md` lines 365–420 | resolved |
| L4 | Issue 3.1 notes `full`'s empty `id` column and `cargo clippy` | resolved |
| L5 | Labelled n=11 across 2 plans in R8 | resolved |

**Additional defect found while resolving** (not raised by either reviewer): `_audit_plan` check #5
requires one `pass-N.md` per phase-log `review:` line, but a **status transition into `review`** and
a **red-team pass presentation** both emit that prefix — 2 lines, 1 file, audit fails on a correct
bundle. Filed as Issue 6.9b with SC21b.

**Blocking set H1–H6: all resolved.** Re-review required per REQ-PLAN-030.
