---
type: Review
okf_spec: OKF-PLAN
plan: plan-046-james-dixson-aabefa
pass: 5
verdict: APPROVE
created: '2026-08-18'
status: resolved
---

# Red-Team Pass 5 — plan-046-james-dixson-aabefa

## Verdict: APPROVE

Cycle 5 of 5. All 7 of pass 4's resolutions landed, each verified **by execution, not by reading**. No HIGH survives, and no claim in pass 4's resolutions table is false. The trajectory **5 → 5 → 2 → 1 → 0** high is real, not narrative.

## Verification run

| Check | Method | Result |
| :-- | :-- | :-- |
| Widened blast grep | `grep -rniE "okf_version.*0\.1\|OKF v0\.1" skills/ _shared/` | **30 hits / 17 files — all 30 assigned** |
| `OKF v0.1`-only subset | same, narrowed | **16 hits / 8 files** — matches the plan |
| Third log-ordering site | `sed -n '80,92p' OKF-YF-EXTENSIONS.md` | line **84** confirmed verbatim; `exp-002:50` names all three |
| SC9 | grepped all three canonical phrases | plan.md **5/4/4**, upstream-triage.md **1/1/1** — **discharges** |
| `REQ-PORT-010` | id sweep of `yf-research/spec/portability.md` | uses `001…009`; `010` **genuinely next-free** |
| Engine gate | re-executed verbatim | `{"status":"pass","commands":[]}` → **EXIT=1**, non-vacuous today |
| Corpus | — | 50 bundles / 19 indexes; ML003 = 25; `upstream-triage.md` unlisted in 8 of 19 — all plan numbers hold |
| `spec`→`spec` edge | `DRIFT-CHECK.md` edge table | **still absent** — H1's premise correct |

**Blast-list assignment, all 30:** 5 × `okf.py:48` constants + `test_okf.py:504` + `test_worktree.py:1179,1296` + `captor.md:44` + `SKILL.md:43` + `README.md:84` → **2.5**; 16 bare-prose hits → **2.5**; 5 × `OKF-BASELINE.md` → **2.3**; `portability.md:19`, `OKF-YF-EXTENSIONS.md:33`, `yf-okf/SPEC.md:201` → **2.4a**. **Zero unassigned.**

## Strengths

- **H1 closed completely, and wider than reported.** The third site is named, assigned to 2.6, with an explanation of *why nothing would have caught it* (no `spec`→`spec` edge, confirmed), and the expected mid-Epic-2 `e-spec-compliance` FAIL is **budgeted** rather than left a surprise.
- **SC9 is dischargeable, and I discharged it.** The normalization is already applied in the bundle. The parenthetical explaining why the forbidden variants are *not* quoted inside the criterion is the right fix for the self-counter-example problem.
- **The gate remains the strongest artifact** — EXIT=1 today, `pipefail` present, predicate in the exit code, evidence produced inside Epic 1. Reachable, non-vacuous, earliest legal position.
- **Dependency chain intact after four rounds of surgery.** 1.1 and 1.2 are roots; a single linear chain to 5.7 with one join. Acyclic, no orphans, no numbering damage from 2.4a, 4.0, 4.2a/b, 4.3a/b.
- **All four upstream dispositions honest**, including #140's `partial` justified by *"the title's own nouns are all in the OUT column"*.

## Concerns

All LOW. **None changes what an executor does.** *(Four were fixed in-place after this verdict rather than deferred — see Resolutions.)*

- `plan.md:170`'s "16 hits" described the increment, not the printed command's 30.
- SC3 greps the narrow pattern, so no criterion checks the 16 bare-prose sites 2.5 was widened to cover.
- SC9's pointer to `reviews/pass-4.md` for the forbidden variants — pass-4 records counts, not literals.
- Issue 2.6 does not itself mention the `OKF-YF-EXTENSIONS.md:84` fix that 2.3 assigns to it; a per-bead executor could miss it.
- `plan.md:156` cites `DRIFT-CHECK.md:81`; the row is at `:80`.
- Issue 1.1 has no dependents, though its text claims it clears the way for 2.2's allocations. Benign — none of 2.2's ids is the `-034` 1.1 resolves.

**L1/L2 acceptance is sound, not a dodge.** `log.md` is producer-owned, its 4 review lines match the 4 pass files, and hand-editing scaffold output is precisely the assert-what-nothing-generates failure this plan exists to remove — accepting it is consistent with the plan's own thesis. The L2 reading-note mitigation landed, confirmed by sampling 3.2, 4.1, 4.2a: the instruction really is the first sentence in each.

## Missing

**Nothing.** Every issue's deliverable is extractable from its first sentence; every gate is reachable and non-vacuous; every success criterion resolves to a command (SC1, SC3, SC6, SC7, SC8, SC10) or an explicit read-and-confirm against a named table (SC4 vs Issue 2.3's section map, SC5's five labelled rows, SC9's verbatim-presence check).

## Gate Assessment

| Gate | Status |
| :-- | :-- |
| Start Gate | Human/operator. Sound. |
| Engine gate green | **Re-executed: EXIT=1.** Non-vacuous; evidence produced by 1.3/1.4 inside Epic 1 — no cycle. Clean. |
| Backfill review | Consent-class, blocks 4.3b only; 4.3a explicitly ungated. Clean. |
| Reconcile Gate | Auto. Clean. |

No frontloading misses. All four gates at their earliest legal position.

## Upstream Assessment

| Issue | Assessed |
| :-- | :-- |
| #141 | **Sound**, unchanged across five cycles. Resolved by 2.9. |
| #140 | **Sound.** IN/OUT inlined identically in `plan.md`, `upstream-triage.md`, and 4.5's close comment. |
| #92 | **Sound, and now mechanically verifiable.** 5.6's *"correct the bullet, do not claim the trigger fired"* distinction remains the most careful thing in the bundle. |
| #118 | **Sound.** Four sites, not two; File Layout split to 5.4. |

## Residual risk ACCEPTED

1. **Verification asymmetry in Epic 2** — *resolved post-verdict*: SC3 now uses 2.5's widened pattern.
2. **One cross-issue assignment (2.3 → 2.6)** depended on the executor reading the epic rather than only the bead — *resolved post-verdict*: 2.6 now restates it.
3. **Two stale line references** — *resolved post-verdict*.

**What remains accepted:** Issue 1.1's dangling self-justification (benign), `log.md`'s producer-owned wording, and annotation density across 39 issues. None makes a competent executor do the wrong thing.

> The plan stands alone: `index.md` orients, `context.md` snapshots the environment with tool versions, `findings/` carries the four experiments with their refutations flagged in the index entry, `references/` inlines all four issue bodies plus the OKF v0.2 spec, `reviews/` carries the full adversarial history, and `log.md` matches. **A cold reader in a different repo can execute this.**

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| SC3 narrow grep | low | **Fixed.** SC3 now uses the same widened `okf_version.*0\.1\|OKF v0\.1` pattern as Issue 2.5. | `main-session` | resolved |
| 2.6 missing the 2.3 assignment | low | **Fixed.** 2.6 restates the `OKF-YF-EXTENSIONS.md:84` fix so a per-bead executor cannot miss it. | `main-session` | resolved |
| `DRIFT-CHECK.md:81` → `:80` | low | **Fixed.** | `main-session` | resolved |
| 2.5's "16 hits" vs the command's 30 | low | **Fixed** — now states 30/17 total, of which 16/8 are the newly-caught bare-prose subset. | `main-session` | resolved |
| SC9's dangling pointer | low | **Fixed** — now points at pass-4's M1 row and says what it actually records. | `main-session` | resolved |
| Issue 1.1 has no dependents | low | **Accepted.** Benign; none of 2.2's allocated ids is the `-034` that 1.1 resolves. | `main-session` | accepted |
| L1 `log.md` wording / L2 annotation density | low | **Accepted**, per the reviewer's own assessment that acceptance here is consistent with the plan's thesis. | `main-session` | accepted |

*(The five `resolved` rows above are mechanical, reviewer-recommended, single-line edits applied after the APPROVE verdict. None changes scope, sequencing, a gate, or a success criterion's meaning — SC3 and SC9 were made **stricter**, never weaker. Recorded here so the post-verdict edit is auditable rather than silent.)*
