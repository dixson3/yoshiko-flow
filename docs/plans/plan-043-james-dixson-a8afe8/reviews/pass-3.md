---
type: Review
okf_spec: OKF-PLAN
id: pass-3
plan: plan-043-james-dixson-a8afe8
created: '2026-08-16'
verdict: REVISE
status: resolved
---

# Review pass 3 — adversarial (red-team)

## Verdict: REVISE

**0 high, 2 medium, 2 low — all single-line edits.** Reviewer's framing: *"This is a
verification pass, not a redesign — no further review cycle is warranted after these two lines
land."*

## The finding that matters most

**C22 caught a resolution asserted in pass-2's table that did not land in the plan body.** This
is exactly the failure mode pass-1 of plan-041 established and that this reviewer was
explicitly asked to hunt. The cause was mundane and worth recording: the target string wrapped
across a line break, so two successive replacements silently matched nothing while the
resolutions table was updated as if they had. **The lesson is that a resolution is not resolved
until it is grepped**, and that is now how this bundle's fixes are verified.

## Verification of cycle-2 resolutions (checked against the body, not the table)

| # | Claimed | Landed? |
| :-- | :-- | :-- |
| C16 | Gate `Blocks: 1.3, 2.2`; Instructions name 1.1/2.1 | **PARTIAL** — `Blocks` fixed; **Instructions still said `(1.1/2.2)`** |
| C17 | `#140` → 2.1; `#136` → 1.1 | **YES**, consistent in both directions |
| C18 | 0.3 enumerates every invocation + exempt list | **PARTIAL** — landed in 0.3, **not propagated to SC2 or D10** |
| C19 | 3.1/3.2/3.3 tests; 4.1 depends-on | **YES** |
| C20 | 4.4 inlines the answer | **YES** |
| C21 | Row placement | **YES** |

Repo premises re-measured and still true.

## Dependency graph — traced, resolves, acyclic

20 issues; every `depends-on` target exists; 0.1 the sole root; every edge strictly decreases in
ordinal, so **no cycle is possible**. 4.1's three new edges all resolve.

## Gate Assessment

**No cycle, reachable.** The condition is produced by 0.1/0.2; `Blocks = {1.3, 2.2}` contains
neither. *"`Blocks` now correctly targets the two wiring issues, closing C16's actual hole."*
The 4th test clause remains inert (noted at pass-2, accepted).

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| C22 | **The C16 off-by-one survived inside the gate's own Instructions** — *"the gate now contradicts itself, naming a blocked issue as an unblocked one."* Machine-authoritative `Blocks` was correct so operational risk was bounded, but *"this is precisely the failure mode the caller flagged, and renumbering errors clustering is exactly why it matters."* | medium |
| C23 | **C18's fix did not propagate to SC2 or D10.** Issue 0.3 required enumerating every invocation, but SC2 — *the criterion checked at close* — still specified the superseded capture-only key. An implementer building capture-only enumeration would **satisfy SC2 and D10 while violating Issue 0.3**, leaving R8 unmitigated by the exact mechanism C18 identified. | medium |
| C24 | **Issue 0.3's exempt list included `worktree teardown`, which is in §6.2, not §6.4.** A harmless superset, but it left the block boundary ambiguous for the implementer. | low |
| C25 | **`set-deliverable-class` appears only inside a `#` comment** in the live §6.4 block, not as an executed line. An enumerator stripping comments will miss it; one that does not will see a phantom step. The audit's D7 position was specified relative to that comment. | low |

## Strengths (verbatim)

- **The C19 fix is structurally complete, not cosmetic** — each Epic-3 issue names the SC it
  satisfies, and 4.1's extended `depends-on` actually routes those tests into both
  CHANGE-VALIDATION tiers. *"The precondition C19 flagged is genuinely met, not asserted."*
- **C20's inlining is the strongest single edit in this pass** — #145 can now inherit rather
  than re-derive, which was pass-1's central upstream objection.
- **The `Resolved By` ↔ `resolves-upstream` pair is consistent in both directions** — load
  bearing, since Epic 1's new verb parses that exact table.
- **The gate's `Blocks` set is now semantically right**: it gates the mutating wiring steps and
  leaves the verb implementations free to produce its condition. *"That is the correct gate
  shape."*

## Missing

Nothing new. *"Both open items are edits to text that already exists; no new investigation,
finding, or issue is required."*

## Upstream Assessment

Unchanged and sound. Five rows, all dispositions justified against findings. No `supersede`
dispositions to scrutinize.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C22 | Gate Instructions off-by-one survived | medium | Fixed and **verified by grep** (`grep -c "1.1/2.2"` → 0). Now reads *"Blocks the two **wiring** issues (1.3, 2.2), not the verb implementations (1.1/2.1)"*. The two prior replacements failed because the string wraps across a line break — a silent no-op that pass-2's table nonetheless recorded as resolved. | resolved |
| C23 | C18 not propagated to SC2/D10 | medium | Fixed. SC2 now requires enumerating **every script invocation in the documented §6.4 block**, each *"envelope-capturing or on the named exempt list"*. D10 rewritten to match, carrying a `(superseded at pass-2, C18 — the capture-only key was circular)` note in the D5 strikethrough convention. | resolved |
| C24 | `worktree teardown` is §6.2, not §6.4 | low | Fixed. Removed from the exempt list, and Issue 0.3 now states the enumerator's boundary explicitly: **from the `### 6.4` heading to the next `###`**. | resolved |
| C25 | `set-deliverable-class` is comment-only | low | Fixed. Issue 0.3 must state its comment-handling rule; Issue 2.2's placement now anchors to the **`classify-deliverable` block** (an executed line) rather than to the comment. | resolved |
