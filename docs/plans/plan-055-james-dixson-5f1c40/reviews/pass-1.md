---
type: Review
okf_spec: OKF-PLAN
id: pass-1
description: Red-team pass 1 — verdict REVISE, 12 concerns (5 high)
---

# Red-team pass 1

## Verdict: REVISE
## Strengths

- **The findings are unusually honest and the plan inherits them correctly in most places.** Every
  Confidence section separates measured/inferred/not-measured, and R5 correctly routes EXP-001's
  unmeasured user-scope arm into the *conservative* branch. Re-verified independently:
  `LowercaseHyphenMax64` occurs 5× in `harness_desc.rs`; the descriptor has exactly 5 rows;
  `spec_table_matches_shipped_descriptor` is a live parity test.
- **D-8's two registration defects are real, and both were re-verified.** `change_validation.py:797`
  maps any nonzero returncode to `"fail"`; §1's `fast`/`full` parse into independent lists
  (`:725-745`); `harness-smoke` is at `CHANGE-VALIDATION.md:51` in `### fast` and appears nowhere in
  `### full`; the `changed_paths and tier == "fast"` guard at `:824` confirms the row fires on an
  unscoped FAST run.
- **The migration gate is the best-constructed gate in this repo's plans** — reads an artifact its
  `Blocks` predecessor creates, pins the schema into the issue text, declares primary-side cwd, and
  fails on an empty `delete` set.
- **The premise is empirically live.** On the target machine all four roots carry the
  `v=0.5.0 tree=413dd08…` marker and 19 `yf-*` skills each, and `~/.config/opencode/skills` holds 13
  genuinely foreign directories — so conservative-keep has real work to do.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | **high** | **Ten success criteria are VACUOUS.** Measured: `cargo test -p yf --test harness_cross_e2e zz_no_such_test_name_xyz` → `running 0 tests` … `EXIT=0`. SC4, SC5, SC6, SC7, SC8b, SC9, SC10, SC11, SC16, SC16b are all `cargo test <filter>` forms; none of the ten names exists today; all are created by issues in this plan. If the issue never writes the function, the criterion passes. **plan-054 already built the guard** — `assets/checks/check-cargo-test-ran.sh`, whose header records the same measurement — and plan-055 does not use it |
| C2 | **high** | **4.6 makes SC19 unpassable without three authenticated harnesses, and 4.7 declines to fix the reason.** Moving `harness-smoke` into `### full` puts it in SC19's `--tier full`; the smoke exits 2 when a harness is absent/unauthenticated and the engine maps 2 → `fail`. The plan already made SC17 `manual:` for exactly this reason, then reintroduces the dependency as a runnable criterion. Internal contradiction, not a trade-off |
| C3 | **high** | **#238 and #239 are claimed `include` but delivered `partial`.** #238's surface-dir resolution is *warned about*, not honoured (D-13) — and 3.2, the only issue that genuinely resolves any part of it, is missing from `Resolved By`. #239 asks for test/smoke coverage of pi's trust gate; the plan ships a doctor axis and a warning. #256's `Resolved By` also lists 4.6, which is D-8's tier defect and unrelated to its state model |
| C4 | **high** | **The destructive migration has no rollback, and R4 is under-rated.** 5.2 applies the migration *then* drive-verifies. If R4 fires the private trees are already gone, with no backup, no `--restore`, and no stated recovery. The plan excludes #243 (*"tune overwrites with no backup"*) as an "adjacent hazard class" while building a second instance of the same hazard |
| C5 | **high** | **The remover's three outcomes collapse "could not determine" into "foreign."** Unreadable `SKILL.md`, malformed marker, and **symlink** all land in `no marker` → foreign, asserting a positive fact from absent evidence. Not hypothetical: `~/.agents/skills/terminal-browser` is a symlink into an app directory on the target machine. Structurally identical to #181/#207/#256 — the three precedents the plan itself cites. Separately, D-2b's conservative-keep **preserves exactly the divergent duplicate R3 exists to eliminate**; D-2b and D-2e are in unreconciled tension |
| C6 | medium | **2.4's arithmetic contradicts SC4's**, and 2.4 writes the test SC4 cites. 2.4 says "four rows → two roots"; SC4 says "four non-claude rows → one root". The descriptor has five rows: four non-claude → one, all five → two. 2.4 is false under either reading |
| C7 | medium | **DAG gaps.** 4.4 needs `test_smoke_states.py`, created by 4.3, with no edge between them. SC15's `Discharged-by` is 4.1 but its command is created by 4.3. 5.3 does not depend on 4.6 though SC19's meaning changes with it. Also: the smoke under rework lives in **plan-054's bundle** while its new tests ship into plan-055's — editing a completed plan's bundle contradicts the bundle-as-record model |
| C8 | medium | **SC1's checker cannot see the requirement 0.3 creates.** 0.3 names no `REQ-*` id, so a derivation over plan.md yields only `{INSTALL-002, INSTALL-007}` and the one genuinely new requirement goes unchecked while SC1 passes green |
| C9 | medium | **SC8 hand-enumerates one file and is blind to a stale SPEC.** `SPEC.md` spells the transform as the label `lowercase-hyphen,max64`, which the grep does not match, and `spec_table_matches_shipped_descriptor` guards the label behind `if let Some(t)`, so with the transform `None` the parity check **skips entirely** |
| C10 | medium | **The smoke's four-state vocabulary is not exhaustive** — no value for "the smoke itself could not run", which post-4.2 shares an exit with `absent`. #256's own defect one layer over. Also `consent-pending` ships probe-less and can only ever be `inferred: true` |
| C11 | low | **`test_smoke_states.py`'s failure mode is unspecified.** If an unknown `--case` exits 0, five criteria collapse into C1's vacuity by another route |
| C12 | low | Migration gate conflates a malformed artifact with a bad verdict (both exit 1); live-harness gate's `Test` is presence-only (honest, but could use one falsifiable arm); `upstream-triage.md` has blank Disposition/Notes; D-6 is out of order |

## Missing

1. A rollback/recovery section (C4).
2. A risk row for "migration applies cleanly, verification then fails" — R3 covers a *partial* migration only.
3. A risk row for editing plan-054's bundle (C7).
4. Any statement of what happens to the **13 foreign directories** measured in `~/.config/opencode/skills`.
5. A `Deferred / follow-ups` section collecting 1.6, 4.7 and D-4a.

## Gate Assessment

| Gate | Reachable? | Assessment |
| :-- | :-- | :-- |
| Start Gate | n/a | Standard |
| live-harness drivability | Yes | Presence-only and can only exit 0 once installed — but the Instructions say so and place authentication with the human. Honest, if weak. `Blocks: 5.2, 4.5` correctly positioned; **no frontloading miss** |
| migration apply | Yes | **The strongest gate in the plan.** No cycle; fails on an empty `delete` set; declares primary-side cwd. Gaps: cannot distinguish a malformed artifact from a bad verdict; does not gate on C5's `undetermined` class |
| Reconcile Gate | Yes | Standard |

No gate's `Condition` depends on evidence produced inside its own `Blocks` set, and no gate names a script no issue creates — **the conformance pass's defect does not recur. The vacuity migrated from the gates into the success criteria (C1).**

## Upstream Assessment

| Issue | Stated | Should be |
| :-- | :-- | :-- |
| #257 | include → 2.2 | **include**, add 5.2 — resolved on a machine only once the private trees are gone |
| #238 | include → 0.4, 3.1, 3.3 | **partial**, add 3.2 |
| #239 | include → 4.8, 4.9 | **partial** — visibility shipped, coverage requested |
| #256 | include → 4.2, 4.6 | **include**, drop 4.6 |
| #121, #243, #240 | exclude | **exclude — sound**, but stop calling #243 merely "adjacent" |
| #255 | deferred | **deferred — sound**, sequencing rationale correct |

## Risk-rating audit

R1 correct · R2 correct (best-evidenced) · R3 correct on the risk, **incomplete on the mitigation** ·
**R4 should be `high`** · R5 correct, honesty exemplary · R6 correct · R7 correct as filed but
understated in consequence · R8 correct.

**No severity inflation found (the #252 pattern); if anything R4 is under-rated.**

## Bottom line

> The investigation is excellent and the architecture is sound. The plan fails on its
> **verification layer**, not its reasoning: ten of twenty-four criteria cannot fail if the work is
> not done, and the fix for that exact defect is already sitting in the previous plan's bundle,
> unused. Fix C1–C5, and this is an APPROVE.

## Recommendations

1. Route all ten `cargo test <filter>` criteria through plan-054's existing `check-cargo-test-ran.sh` (C1).
2. Do not move `harness-smoke` into `### full` while 4.7's engine fix is deferred (C2).
3. Re-disposition #238 and #239 to `partial` with explicit IN/OUT notes (C3).
4. Raise R4 to `high`; make the migration reversible and verify before destroying (C4).
5. Add a fourth `undetermined` outcome, distinct from `foreign` (C5).
6. Fix 2.4's row arithmetic; add the missing DAG edges; give 0.3 a real REQ id (C6, C7, C8).
7. Widen SC8 to the SPEC label; add a fifth smoke state; pin the `--case` contract (C9, C10, C11).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Confirmed by re-measurement** (`0 passed; 15 filtered out`, exit 0) and `check-cargo-test-ran.sh` verified present in plan-054's bundle. All ten criteria (SC4/5/6/7/8b/9/10/11/16/16b) now run `bash scripts/checks/check-cargo-test-ran.sh <fn>`, which greps for `fn <name>` first and asserts a non-zero passed count. SC3's unfiltered `--test` form kept as-is | `main-session` | `resolved` |
| C2 | high | 4.6 no longer moves the smoke into `### full`. It **removes** the row from `### fast` (the real defect — an expensive check on the cheap tier) and registers the static `check_smoke_tier.py` in `### full` instead. Re-adding the smoke is explicitly **blocked on 4.7** and recorded in the new Deferred section. SC14 restated | `main-session` | `resolved` |
| C3 | high | #238 and #239 changed to **`partial`** with explicit IN/OUT notes; 3.2 added to #238's `Resolved By`; 4.6 dropped from #256's and replaced with 4.3; 5.2 added to #257's | `main-session` | `resolved` |
| C4 | high | R4 raised to **`high`**. 5.2 restructured to **drive-verify BEFORE removing** (D-2e is satisfied by the old copy not persisting, which either ordering achieves). New Issue 5.2a removes to a **timestamped quarantine** with a documented restore, plus SC18b and `check-quarantine-restore.sh` measuring byte-equality after restore. New risk R9 covers "applies cleanly, verification then fails" | `main-session` | `resolved` |
| C5 | high | Fourth outcome **`undetermined`** added (unreadable `SKILL.md`, malformed marker, symlink), kept-and-reported distinctly from `foreign`; the walk must not follow symlinks; the migration gate now fails when `undetermined` is non-empty. New **D-2f** names the D-2b/D-2e tension explicitly and requires the dry-run report to flag any kept directory whose skill name also exists in the shared root as a live divergence hazard. 1.5 extended to unreadable-member, malformed-marker and symlinked-member cases | `main-session` | `resolved` |
| C6 | medium | 2.4 restated: **all five** rows → **two** roots per scope, and the **four non-claude** rows → **one**. Both halves now asserted | `main-session` | `resolved` |
| C7 | medium | `4.3` added to 4.4's `depends-on`; `4.6` added to 5.3's; SC15 → `4.1, 4.3`, SC12b → `4.3, 4.4`, SC13b → `4.3, 4.5`, SC14 → `0.8, 4.6`. New **Issue 0.8** promotes `_common.sh`, `check-cargo-test-ran.sh` and `check-harness-smoke.sh` into `scripts/checks/` before Epic 4 edits them, with risk **R10** covering the bundle-as-record violation | `main-session` | `resolved` |
| C8 | medium | 0.3 now names **`REQ-YF-MARK-006`** explicitly, so the derivation can see the one genuinely new id. `check_amendment_log.py` must exit **2 (INCONCLUSIVE)** on an empty or single-element derived set, per the `check-criteria-scripts-exist.sh` precedent | `main-session` | `resolved` |
| C9 | medium | SC8 restated to cover the SPEC label, and now runs `check-transform-gone.sh`, which greps `yf/` for the enum name **and** `SPEC.md` for `lowercase-hyphen,max64`. 2.3 extended to remove the label text. The `if let Some(t)` skip-when-`None` hole is named in the issue body | `main-session` | `resolved` |
| C10 | medium | Fifth state **`undetermined`** added to the smoke vocabulary for "the check itself could not run", and 4.2 now records that `consent-pending` is **inference-only** at these versions. SC12 restated to five values | `main-session` | `resolved` |
| C11 | low | 4.3's text now fixes the contract: an unrecognised `--case` exits **2**, and a bare invocation runs every case | `main-session` | `resolved` |
| C12 | low | Migration gate's Test moved into `check-migration-dryrun.sh`, which exits **2** on a missing/unparseable artifact (distinct from 1 for a bad verdict) and fails on non-empty `undetermined`. Live-harness gate gained a falsifiable arm (`codex login status`, measured exit 1 unauthenticated). D-6 ordering and the blank `upstream-triage.md` fields noted as cosmetic, not changed | `main-session` | `resolved` |

**All 12 concerns resolved. This file is now FROZEN.**
