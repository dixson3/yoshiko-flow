---
type: Review
okf_spec: OKF-PLAN
plan: plan-046-james-dixson-aabefa
pass: 4
verdict: REVISE
created: '2026-08-18'
status: resolved
---

# Red-Team Pass 4 — plan-046-james-dixson-aabefa

## Verdict: REVISE

1 high, 3 medium, 3 low. **A near-approve.** All 13 of pass 3's resolutions landed — verified by execution, not by reading. The single HIGH is a one-sentence enumeration omission of the same family as pass 3's H1, **not** a recurrence of the over-stated-resolution defect.

## Verification of pass 3's resolutions — all 13 landed

| Row | Verified how | Status |
| :-- | :-- | :-- |
| **H1** blast list | Ran `grep -rn "okf_version" skills/ _shared/` (63 hits) and SC3's grep (**16** hits). **All 16 assigned**: 5 constants + 3 test + 3 prose → 2.5; 3 fixed-authority → **2.4a**; `OKF-BASELINE.md:4,166` → 2.3. Sequencing 2.4→2.4a→2.5 correct. | RESOLVED |
| **H2** 4.2(c) | `plan.md:220` states **emit only for directories that EXIST** with both disqualifying reasons inline. No either/or survives. | RESOLVED |
| **M1** `no-index` | Five sites unified; exit codes coherent 0/1/2 everywhere; zero surviving `n/a`. | RESOLVED |
| **M2/M4** 4.0 + split | Chain traced node by node — **strictly linear and acyclic**, no numbering damage from three insertions. | RESOLVED |
| **M3** 3.2 | Contradiction gone; fixture provenance stated; over-correction recorded as such. | RESOLVED |
| **M6/M5/L3/L4** | SC4 section-map-shaped; SC7 names both producers; single-level glob everywhere; `set -o pipefail` present. | RESOLVED |
| **L2** SC9 | Landed *as a grep* — but the grep does not discharge. See M1. | PARTIAL |

**Re-measured:** gate exits **1** today; 50 bundles / 19 indexes; 25 ML003; `upstream-triage.md` unlisted in exactly 8 of 19.

## Strengths

- **The dependency graph survived three rounds of surgery intact.** Inserting 2.4a, 4.0 and splitting 4.2/4.3 into a/b pairs is exactly where plans acquire cycles and orphans; still a single clean chain.
- **The blast list is a real corpus grep and verifies exhaustively** — 16 hits, 16 assignments, zero unassigned. Closed properly, not narratively.
- **`plan.md:220` is the model for closing an either/or**: decision, both disqualifying reasons, and an explicit note that the reason is inline *because* pointing at a review file failed once.
- The gate remains the strongest artifact in the bundle.

## Concerns

### HIGH

**H1 — Issue 2.3's "three places claiming OKF is silent on log ordering" names two, and the third is a fixed-authority spec node assigned to no issue.** `plan.md:154` says *"the three places … (§4, §7a bullet 1)"* — a count of three against contents of two, both inside `OKF-BASELINE.md`. The third is named in this plan's own finding (`exp-002:50`): **`OKF-YF-EXTENSIONS.md` §3** — i.e. `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md:84`, *"OKF reserves `log.md` as 'update history' but demonstrates **no format and no ordering**"* — a `spec` node, **fixed authority**. Under v0.2 §9 that premise is false, and yf's rule at `:89` stops being an extension decision and becomes baseline conformance. No issue owns it: 2.6 records five unrelated mapping rows; 2.7 fixes L37 only. **There is no `spec`→`spec` edge in `DRIFT-CHECK.md`**, so nothing detects it — the plan would ship a fixed-authority spec asserting something false about the very thing Epic 2 exists to reconcile.

Second half, self-correcting but unbudgeted: the blast list greps `okf_version`, so **bare `OKF v0.1` prose claims are unassigned**. `DRIFT-CHECK.md:81` scopes `skills/*/spec/*.md` → `e-spec-compliance`, so Issue 2.3's edit will fire a drift FAIL on `SKILL.md` mid-Epic-2 — recoverable, but unplanned.

### MEDIUM

**M1 — SC9's `grep -c` does not discharge, and I ran it.** Executed: `"projection delivery mode"` → plan.md **2**, triage **1**; `"round-trip"` → **3**/**1**; `"yf-research and yf-incubator"` → **1**/**0**. There are no three literal phrases — wording varies by site, and D-1 interrupts each phrase with bold markers so the literal grep misses it entirely. **Pass 3 closed L2 by *naming* a command without running it.** The substance holds; the criterion does not.

**M2 — Issue 4.0's yf-research half has no named target.** Precise for yf-plan (amend `REQ-PORT-001` at `portability.md:19`), vague for the other: *"allocate the yf-research counterpart."* `skills/yf-research/spec/portability.md` `REQ-PORT-009:38` specifies the reserved-file split but **enumerates no listing members**, so there is no analogous clause to amend and no stated next-free id. 4.2b would land a producer change with no SPEC-first basis — the exact gap 4.0 was added to close.

**M3 — SC7 imposes assertions on 4.2b that 4.2b never instructs.** SC7 requires each throwaway bundle to assert *"no ghost entry for a presence-optional file and no entries for absent subdirectories"*, but 4.2b scopes the research producer to the `plan.yaml`/`sources.json` omissions only. Whether `index_manager.py` has those defects is **unmeasured**. Either 4.2b is under-specified or SC7 over-specified.

### LOW

**L1** — `log.md:6` still reads `review: plan v1 presented` rather than naming pass 1; stray blank line at `:9`. Cosmetic, producer-owned.
**L2** — Annotation accretion is real but tolerable: Issue 3.2 is five paragraphs around a one-sentence instruction; 4.1 buries its deliverable behind a correction narrative. In both the instruction *is* the first sentence, so extraction works — but 39 issues at this density is near the readability limit.
**L3** — SC3's carve-out is dead text: it greps `skills/ _shared/` then excludes `references/` and the plan-029 fixtures, neither of which that root can reach.

## Missing

- Assignment for `OKF-YF-EXTENSIONS.md:84` and for the bare `OKF v0.1` prose claims (H1). **The only genuine gap.**

## Gate Assessment

| Gate | Cycle-4 status |
| :-- | :-- |
| Start Gate | Sound. |
| Engine gate green | **Re-executed: exits 1 today.** `pipefail` present, so a crash is distinguishable from a false predicate. No cycle — 1.3 produces the evidence and sits inside Epic 1. Clean. |
| Backfill review | Clean. No cycle. |
| Reconcile Gate | Unchanged. |

No frontloading misses. All four gates at their earliest legal position.

## Upstream Assessment

| Issue | Assessed |
| :-- | :-- |
| #141 | **Sound**, unchanged across four cycles. |
| #140 | **Sound.** IN/OUT inlined and consistent. |
| #92 | **Sound in substance, weak in verification** — carve-outs semantically identical at all five sites; SC9's mechanical check does not run (M1). |
| #118 | **Sound.** |

**Reviewer's own note:** *"M1–M3 and all three LOWs are things a competent executor absorbs without harm. H1 is not — the `OKF-YF-EXTENSIONS.md:84` omission has no detector anywhere in the plan or in `DRIFT-CHECK.md`, and its failure mode is silent."*

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 third log-ordering site + bare v0.1 prose | high | **Upheld, and MY re-measurement found MORE than reported.** `OKF-YF-EXTENSIONS.md:84` confirmed verbatim. And `grep -rniE "OKF v0\.1" skills/ _shared/` returns **16 hits across 8 files** — including three `OKF-EXTENSION.md` files (yf-plan, yf-research, yf-incubator) the review did not list. Issue 2.3 now names the third site and assigns it to 2.6 (which already edits that file); Issue 2.5's blast-list command widened to `grep -rniE "okf_version.*0\.1\|OKF v0\.1"` with all 8 files enumerated; the expected mid-Epic-2 `e-spec-compliance` drift FAIL on `SKILL.md` is now **budgeted** in 2.3 rather than a surprise. | `main-session` | resolved |
| M1 SC9 grep does not discharge | medium | **Upheld — I ran it and confirmed all three phrase counts disagree.** This is the fifth over-stated resolution, and its shape is now familiar: pass 3 closed L2 by *naming* a command without running it. SC9 restated to require the three carve-out names be **byte-identical** at all five sites (a real, achievable normalization), with the grep counts then required equal — and Issue 5.5 now owns the normalization. | `main-session` | resolved |
| M2 4.0's research half untargeted | medium | **Upheld — verified.** `yf-research/spec/portability.md` uses `REQ-PORT-001…009`; `REQ-PORT-009:38` governs reserved files but enumerates no listing members. 4.0 now names the file and allocates **`REQ-PORT-010`** (next free, measured) for the research listing-member enumeration. | `main-session` | resolved |
| M3 SC7 over-specified vs 4.2b | medium | **Upheld.** 4.2b now **measures the research scaffold's output first**, then scopes; SC7's ghost/absent-dir assertions are scoped to whichever producer actually emits them, rather than asserted of both in advance. | `main-session` | resolved |
| L1 log.md wording | low | **Accepted, not fixed.** `log.md` is producer-owned and the entry is the scaffold's own wording; rewriting it by hand is the class of drift this plan exists to remove. Count-equality (4 ↔ 4) holds. | `main-session` | accepted |
| L2 annotation accretion | low | **Accepted with a mitigation.** The instruction is the first sentence of every issue; a note to that effect is added at the head of the Epics section so an executor knows the pass-N annotations are provenance, not instruction. | `main-session` | resolved |
| L3 SC3 dead carve-out | low | Carve-out removed — the grep root cannot reach `references/` or the fixtures, so the exclusion was protection that never operated. | `main-session` | resolved |
