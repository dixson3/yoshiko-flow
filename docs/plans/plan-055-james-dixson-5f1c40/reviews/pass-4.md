---
type: Review
okf_spec: OKF-PLAN
id: pass-4
description: Red-team pass 4 — verdict REVISE, 13 concerns (1 high); all 12 pass-3 resolutions verified genuine
---

# Red-team pass 4

## Verdict: REVISE
> One high-severity concern, and it is cheap to fix. **If C1 is closed in the same editing session,
> no fifth cycle is warranted** — the other concerns are polish and do not need a review pass to
> confirm.

## Resolution verification — pass 3's 12 concerns

**All 12 verified genuine against current text**, including the two most likely to have silently
failed. N5's runbook is genuinely in `context.md`. N4's Epic 0 sweep holds: 0.1/0.4/0.5 name
`REQ-YF-INSTALL-007`, 0.2 names `REQ-YF-INSTALL-002`, 0.3 names `REQ-YF-MARK-006` — the three-pass
recurrence is closed.

## Strengths

- **The D-14 deletion landed cleanly, verified mechanically.** 33 issues, 22 criteria; **zero**
  dangling edges; **zero** cycles; every criterion's `Discharged-by` resolves; every issue discharges
  at least one criterion; `5.4` dominates the entire graph. No 4.1–4.5 reference survives as an edge.
- **0.8's re-basing claim is correct as measured.** `ck_tree()` from `scripts/checks/` resolves to the
  repo root, making `plan_id` the repo name and `.worktrees/yoshiko-flow` a path that never exists —
  it silently returns the primary tree. The prescribed fix is right and the described failure mode
  ("fail closed but unrunnably") is exactly what would happen.
- **The COPY decision is right and the evidence backs it.** plan-054's SC18 executes the smoke at the
  bundle path; a move genuinely would have broken a completed plan's record.
- **The Objective survives the deferral intact**, and no upstream disposition is inflated by it.
- **Vacuity is closed.** 17 of 22 criteria run a failable command; the 5 `manual:` entries each state
  why no predicate exists.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | **high** | **Four user-visible behaviors ship with NO SPEC requirement, and SC1 is structurally unable to notice.** 5.2a's reversible quarantine apply, 3.3's override-mismatch warning, 4.8's `yf doctor` pi-trust axis, and 4.9's project-scope warning are all outside Epic 0's `{INSTALL-002, INSTALL-007, MARK-006}`. AGENTS.md is unambiguous and D-6 claims the plan honors it. **Repo precedent settles 4.8**: `SPEC.md` carries `REQ-YF-DOCTOR-001…006` — one REQ per doctor axis. **5.2a is sharpest**: 1.4 ships an `apply` that deletes and 5.2a converts it to a move later, so the tree transiently carries an irreversible destructive verb with no governing requirement. **SC1 says "every SPEC id this plan touches"** — the plan touches no id for these four, so SC1 passes green while four behaviors land un-specified. The cannot-fail class, one level above where passes 1–3 hunted it |
| C2 | medium | **D-14 residue in 0.8 and R10** — both still reason from "five issues rewrite the smoke." After D-14 **zero** do. The whole copy-vs-move argument and R10's mitigation rest on a premise D-14 removed, and the copied smoke now has **no consumer anywhere in the plan** — it lands dormant |
| C3 | medium | **0.8's rationale for repointing `CHANGE-VALIDATION.md:51` is false under 0.8's own copy semantics.** A copy leaves the old path valid, so no FAST run is ever stale — and 4.6 deletes the row anyway. A leftover from the move-reading N2 rejected |
| C4 | medium | **4.6 leaves `CHANGE-VALIDATION.md` self-contradicting.** Lines 53–59 are a blockquote *inside* the `### fast` table asserting the smoke is "FULL-tier ONLY" and citing a completed plan's SC18. `parse_manifest` reads only `\|`-delimited rows, so a correct `check_smoke_tier.py` passes green over seven lines of false prose |
| C5 | medium | **The shared root's on-disk names become order-dependent.** `resolved_dests` dedupes by path and keeps the **first** harness's id, and `deploy_skill` derives `dir_name` from *that* harness's transform. After 2.2 collapses pi onto `.agents/skills`, whichever row is first governs the transform for every skill. **2.2/2.5 and 2.3 have no edge in either direction**, so "collapsed root, transform still present" is a legal landing order nobody reasoned about |
| C6 | low | Deferred row 302 is struck through as "moot" yet still occupies a routed follow-up cell, duplicates row 301, and mis-cites SC17 — which is now the post-migration drive-verify criterion, unrelated to the smoke |
| C7 | low | **The one disposition that changed is the one the Deferred table does not record** — no "#256 stays open as partial" row, though #238 and #239 both have one |
| C8 | low | **All nine `Disposition:`/`Notes:` fields in `upstream-triage.md` are blank**, while `index.md` advertises it as "the triage record behind plan.md's Upstream Issues table." Pass 1 declined this as cosmetic; D-14's `include → partial` flip makes that judgement weaker |
| C9 | low | **SC17b is a strict subset of SC17** and its `Discharged-by` (5.1a) does not match its subject (5.2's drive-verify) |
| C10 | low | **SC3 is the last unguarded `cargo test`** — it names a target, so a missing file errors, but it asserts nothing about the per-harness resolutions its text claims. Pass-3's N9 argument applied to the one criterion it did not reach |
| C11 | low | **The live-harness gate is a frontloading miss.** Its condition is establishable at plan start and depends on nothing any issue produces, yet it blocks the 31st of 33 issues. Passes 1 and 3 scored this "no miss" by reasoning from where the *need* sits rather than where the *evidence* is available |
| C12 | low | **5.1 names no command, no binary and no target paths.** 1.4 never names the CLI verb; 5.1 runs before 5.1a's deploy so must use `./target/debug/yf`, unstated; the schema is declared in 5.1 while the emitting CLI is specified in 1.4 |
| C13 | low | **0.7's rationale mislocates its own over-collection.** `REQ-YF-TUNE-029` is cited inside Issue 0.3 — an Epic 0 body — so the Epic-0 restriction does not exclude it; only the hand-authored list does |

## Missing

1. SPEC requirements for reversible apply, the two install-time warnings and the doctor axis, plus an SC1 restatement that can fail on their absence (C1).
2. A clause in 4.6 covering the now-false `harness-smoke` blockquote (C4).
3. An edge or stated invariant fixing name-transform ownership between 2.2/2.5 and 2.3 (C5).
4. A `#256 stays open as partial` row (C7).
5. Filled `Disposition:`/`Notes:` in `upstream-triage.md` (C8).
6. A named CLI verb for the remover and the executing binary for 5.1 (C12).

## Gate Assessment

| Gate | Reachable? | Assessment |
| :-- | :-- | :-- |
| Start Gate | n/a | The right home for C11's drivability confirmation |
| live-harness drivability | Yes | Sound; `Blocks: 5.2` correct. **Frontloading miss (C11)** |
| migration apply | Yes | **Still the strongest gate in the plan.** One residual: its schema is declared in 5.1 rather than 1.4 where the emitting CLI lives (C12) |
| Reconcile Gate | Yes | 5.4 dominates the full graph — verified |

**The gate layer is sound.** No unreachable condition, no cycle, no gate naming a script no issue creates.

## Upstream Assessment

#257 sound · #238 sound (best-written IN/OUT cell) · #239 sound · #121/#243/#240 sound · #255 sound.

**#256** — the re-disposition is correct and should not be reversed, but the note is *"accurate about
the artifact and slightly generous about the relationship"*: the tier-registration defect is not
something #256 asks for, it is an adjacent defect EXP-006 found while investigating it. **None of
#256's own state-model ask ships.**

## Recommendations

1. Add the four missing SPEC requirements and restate SC1 so it can fail on their absence (C1).
2. Strip the D-14 residue from 0.8 and R10; state the copied smoke lands dormant (C2, C3).
3. Have 4.6 delete the orphaned blockquote (C4).
4. Sequence 2.3 against 2.2 or state the merged-row invariant (C5).
5. Close C6–C13 as polish in the same session.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Concern accepted — this was a real SPEC-first violation.** `REQ-YF-MARK-006` extended to require a **reversible** (move-to-quarantine + restore) apply, so 1.4's verb is governed from the moment it ships. New **Issue 0.9** adds `REQ-YF-INSTALL-011` for both install-time warnings; new **Issue 0.10** adds `REQ-YF-DOCTOR-007` for the pi-trust axis, following the repo's one-REQ-per-axis precedent. 3.3/4.8/4.9/5.2a now depend on their covering requirement. **SC1 restated over BEHAVIOURS rather than over ids-the-plan-touches**, and 0.7 gains a second assertion over the Epic 1-5 behaviour set — so the criterion can now fail on exactly this omission, which the old wording could not | `main-session` | `resolved` |
| C2 | medium | 0.8's copy-vs-move argument no longer reasons from in-plan rewrites; it states the copied smoke lands **dormant** and is pre-positioning for the deferred follow-up. R10 re-scored `med` → `low` and rewritten | `main-session` | `resolved` |
| C3 | medium | The repoint is **dropped**, with the reason stated: under copy semantics the old path never goes stale and 4.6 deletes the row anyway | `main-session` | `resolved` |
| C4 | medium | 4.6 now explicitly deletes the orphaned blockquote at `CHANGE-VALIDATION.md:53-59`, and `check_smoke_tier.py`'s predicate gains "no residual `harness-smoke` prose claim survives in §1" — closing the gap where a row-only parser passes green over false prose | `main-session` | `resolved` |
| C5 | medium | **`2.2 depends-on: 2.1, 1.5, 2.3`** — the transform is dropped **before** the collapse rather than in an unordered sibling, with the first-row-wins name-derivation mechanism quoted in 2.2's body. 2.4 additionally asserts that every row merged onto a shared root agrees on `name_transform` | `main-session` | `resolved` |
| C6 | low | The struck-through duplicate row is **deleted**; row 301's directional word corrected | `main-session` | `resolved` |
| C7 | low | "#256 stays open as `partial`" row added to the Deferred table | `main-session` | `resolved` |
| C8 | low | **All 8 `Disposition:` / `Notes:` fields in `upstream-triage.md` filled** from plan.md's table; zero empty forms remain. Pass 1 declined this as cosmetic — D-14's `include → partial` flip made that judgement wrong | `main-session` | `resolved` |
| C9 | low | SC17b restated over the **deployment act** (5.1a's subject) rather than 5.2's verification, making it genuinely distinct from SC17 instead of a subset | `main-session` | `resolved` |
| C10 | low | SC3 routed through `check-cargo-test-ran.sh` on a named test `pi_opencode_resolve_shared_root_both_scopes`, which 2.4 now authors. **No unguarded `cargo test` remains** | `main-session` | `resolved` |
| C11 | low | Drivability confirmation frontloaded into the **Start Gate's** Instructions, at near-zero cost. The later gate stays where the need sits | `main-session` | `resolved` |
| C12 | low | 1.4 names the verb — `yf harness skills prune-private --scope user [--apply]` — and **owns the schema**, which 5.1 now references rather than re-declares. 5.1 names the binary (`./target/debug/yf`, because it runs before 5.1a's deploy) and both target paths | `main-session` | `resolved` |
| C13 | low | 0.7's rationale corrected to state precisely which guard catches which case: the Epic-0 restriction excludes `REQ-YF-MARK-001/002/003` (cited in D-2a), but **not** `REQ-YF-TUNE-029` (cited inside 0.3) — only the hand-authored list reaches that one | `main-session` | `resolved` |

**All 13 concerns resolved. This file is now FROZEN.**
