---
type: Review
okf_spec: OKF-PLAN
id: pass-2
plan: plan-043-james-dixson-a8afe8
created: '2026-08-16'
verdict: REVISE
status: resolved
---

# Review pass 2 — adversarial (red-team)

## Verdict: REVISE

1 high, 3 medium, 2 low. The reviewer's own framing: *"This is a **mechanical fix pass**, not a
redesign… No further substantive review cycle is warranted after them."*

**The high concern is a defect I introduced in the pass-1 revision**, not a pre-existing one.

## All 18 pass-1 resolutions verified in the plan body

The reviewer checked each claimed resolution against `plan.md` rather than trusting the table
(the plan-041 lesson), and re-measured the repo premises. All confirmed. Notably:

> **C5 delta dropped — "Confirmed and clean".** Grepping `baseline|fingerprint|delta`: every
> surviving hit is D5's strikethrough, R3's dissolution note, Issue 4.2's upstream deferral, or
> E3's historical finding. **No orphaned baseline artifact anywhere.** C6/C7/C8 genuinely
> dissolve — there is no stored baseline for them to attach to.

Repo re-measurement: `spec/phases.md:89` still says "fixed three-step order" (single occurrence
repo-wide); `SKILL.md:1066` still says "runs a fixed order" (single occurrence);
`_TRACKER_ROW_RE` exists at `plan_manager.py:1143`. **Premises hold.**

## Strengths (verbatim)

- **The delta excision is surgical.** *"This was the highest-risk edit (removing a deliverable
  mid-plan) and it left no dangling reference, no orphaned risk, and no renumbering damage
  inside Epic 2."*
- **D9 is a better answer than the concern that prompted it** — splitting halting from
  remediation-kind makes the contract describable in two orthogonal columns, *"which is what an
  inheriting skill can actually use."*
- **D10/R8 is intellectually honest** — *"the plan names its own thesis as a risk against itself
  and refuses to claim mitigation it hasn't earned."*
- **The dependency graph is sound** — every edge traced, 0.1 the sole root, acyclic.

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| C16 | **The Capability Gate's `Blocks` set was not renumbered when Epic 2 lost its old 2.1.** Epic 2 is now 2.1=verb, 2.2=**wiring**, 2.3=test — but the gate still said `Blocks: 1.3, 2.3`, and its Instructions still named 2.2 as a verb. Net effect: **Issue 2.2 could wire the audit into §6.4 while `REQ-COMPLETE-001` still read "fixed three-step order"** — precisely the outcome the gate exists to prevent, and a direct contradiction of the plan's stated premise. | **high** |
| C17 | **The `#140` row's `Resolved By` still pointed at Issue 2.2 while `resolves-upstream` sat on 2.1.** Same off-by-one. *"Not cosmetic: `Resolved By` is the column `reconciler.md` reads, and a mismatched mapping in this exact table is the mechanism behind #136 — the defect this plan exists to fix."* Worse, Epic 1's new verb parses this table, so the plan would ship a table its own verb disagrees with. | medium |
| C18 | **Issue 0.3's enumeration key is circular.** Parsing only `X=$(… --json)` captures can see *only steps already shaped like conformant ones*. The live §6.4 block has **two** captures alongside **four** non-capturing invocations. An author who adds a step *without* the capture idiom — the likeliest non-conformance, since it takes less effort — is invisible and passes CI. R8's mitigation covered a narrower failure mode than R8's text claimed. | medium |
| C19 | **No Epic-3 issue produces the tests SC7, SC8 and SC11 assert.** Issue 3.0 satisfied SPEC-first's *requirement* half, but `AGENTS.md` says "requirement — then code **+ a tagged test**". 3.1/3.2/3.3 specified only code, and Issue 4.1 depended only on `1.2, 2.3`, so Epic 3's tests would never reach the CHANGE-VALIDATION tiers. | medium |
| C20 | **Issue 4.4's body was weaker than D9 and SC10 require** — it still read "names its two authority classes", the pass-1 phrasing plus two words. An executor reading only the issue body would post the weak version. | low |
| C21 | **Decisions and Risks tables interleave new rows** (D9/D10 between D5 and D6; R8–R10 between R3 and R5). Harmless, but reads as an editing artifact against this repo's portability standard. | low |

## Gate Assessment

The reviewer **executed the new test verbatim** against the repo: exit 1, *"syntactically valid
and semantically correct… `!` binds to the individual pipeline inside an AND-list, so the
negations apply as intended… It correctly fails today (not vacuously satisfied) and C13's
tautology is genuinely fixed."*

One non-blocking note: the final clause `grep -qE "halting|advisory"` **already matches today**
(`phases.md:91` contains "halting" in REQ-COMPLETE-002's Verification line), so it contributes
nothing — the gate rests on the two negations plus "ordered gate chain".

Precondition cross-check: **one unmet, down from two** — Epic 3's test precondition (C19). Issue
2.2's old baseline precondition is fully dissolved.

## Upstream Assessment

Dispositions unchanged and still well-founded. **#145's `exclude` is now backed by a
discriminator that actually discriminates (D9)** — pass-1's central upstream objection — *"Issue
4.4's body just needs to say so"* (C20). The `#140` `Resolved By` cell was the only upstream
defect (C17).

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C16 | Gate `Blocks` off-by-one after renumbering | high | Fixed: `Blocks: Issue 1.3, Issue 2.2`; Instructions now read "the two **wiring** issues (1.3, 2.2), not the verb implementations (1.1/2.1)". **My error, introduced when Epic 2 was renumbered after dropping the delta** — the gate's targets did not shift with the issues. | resolved |
| C17 | `#140` `Resolved By` off-by-one | medium | Fixed: `Resolved By` → `Issue 2.1`, matching the `resolves-upstream: #140 (partial)` marker on 2.1. `#136 → Issue 1.1` re-checked and correct. | resolved |
| C18 | Enumeration key is circular | medium | Accepted — the sharpest point in this pass. Issue 0.3 now enumerates **every script invocation** in the §6.4 block, requiring each to be either envelope-capturing **or on an explicit named exempt list** (`worktree teardown`, `classify-deliverable`, `set-deliverable-class`, `update-status`). Converts the teeth from *"checks conformant steps"* to *"detects added steps"*. | resolved |
| C19 | Epic 3 has no test producers | medium | Fixed: 3.1/3.2/3.3 each now ship a `REQ`-tagged test (3.2 → SC7, 3.3 → SC8 + SC11's second clause), and Issue 4.1's `depends-on` extended to `1.2, 2.3, 3.1, 3.2, 3.3` so Epic 3's tests reach both CHANGE-VALIDATION tiers. | resolved |
| C20 | 4.4's body weaker than SC10 | low | Fixed: the answer is inlined — `halting`/`advisory` as the class axis, remediation-kind as a separate attribute, and halting+prose explicitly legal (#145's own shape). | resolved |
| C21 | Table row interleaving | low | Fixed with a clarifying parenthetical on the D9 and R8 rows explaining the placement, rather than renumbering rows other artifacts already cite. | resolved |
| — | Gate's 4th clause is inert | low | Noted, not changed. The reviewer explicitly called it acceptable given C13's framing; the gate's weight is correctly carried by the two negative assertions. | resolved |
