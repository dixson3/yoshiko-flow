---
type: Review
okf_spec: OKF-PLAN
id: pass-3
plan: plan-045-james-dixson-9899e1
created: '2026-08-18'
verdict: APPROVE
status: resolved
---

# Red-Team Pass 3 — plan-045-james-dixson-9899e1

**Date:** 2026-08-18

## Verdict: APPROVE

Every pass-2 concern verified **by command or by quoting plan.md** — never from the Operator
Resolutions table, which was the artifact under suspicion. Eight of nine fully landed; one (F, low)
half-landed. No high-severity defect remains.

## Verification record (pass-2 A–I)

| # | Method | Result |
| :-- | :-- | :-- |
| A | `audit` → `status: pass`, 0 non-pass. `ready-check` → `audit_status: pass`, `review_pass: 2`, not-ready **only** on "last verdict is REVISE". `log.md` 2 bullets / `reviews/` 2 files | **Fixed, by command** |
| B | SC3 verbatim now enumerates five classes and five mechanisms. `grep -ri "four stop\|fourth stop\|four-class"` → only the two review files, **zero in plan.md** | Fixed |
| C | 2.4a states `len(glob('reviews/pass-*.md'))`; `_plan_review_line_count` survives only as an explicit negative — **stronger than deletion**. Escalation exit and no-auto-reset both stated | Fixed |
| D | `grep -c "three edits, not one"` → **4**, at 2.10, 3.8, 4.6, 5.6 | Fixed, count verified |
| E | 3.1 defines `probe` as cheap AND self-cleaning, with the `consent` boundary | Fixed |
| F | Edge present in `plan.md`; **absent from `upstream-triage.md`** | Half-landed |
| G | Risk table reads 45; mechanical count 45 | Fixed |
| H | Gate Instructions: failed gate bead **left OPEN as the record** | Fixed |
| I | `index.md` carries the `scope-answers.md` deferral note | Fixed |

Pass-1 spot-checks (3, 4, 15) independently re-verified: five classes now in **both** D-2 and SC3;
registration in all four authoring issues with 1.3 no longer claiming what it cannot see and 6.3
confirmation-only; `context.md`'s three sections substantive and the audit passing.

## Strengths

- **The DAG survived three passes cleanly** — 45 issues, 0 duplicates, 0 unresolved deps, 0 cycles,
  single root `0.1`, single terminal leaf `6.3`. The 2.4a insertion and four clause edits perturbed
  nothing.
- Bundle mechanically clean end to end: `audit` = pass, `okf.py check` = OK.
- **Staleness re-verified at HEAD `04f18cc`** — all eight REQ ids still free; `coordinator.md:50`
  still closes unconditionally, `:80` still says "Wait for operator"; "continue to the next bead" =
  0; "Operator Resolutions" = 0 in `.py`; `bd ready` = 14 issues, no gates. The
  `frontload|gate placement` grep returns exactly one hit, **inside a test fixture** — the "no such
  guidance exists" claim is materially accurate.
- **Concern A was handled the right way** — the over-report was recorded in `pass-2.md` rather than
  quietly corrected, and its resolution row invited this pass to check it as evidence. That is why
  this pass could verify rather than trust.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C-1 | medium | **SC11 forecloses an option Issue 1.3 authorizes.** 1.3 permits "map it **or drop the glob** and rely on 0.8's `cargo test`" — the branch the risk table calls the honest answer. SC11 asserted all three globs fire a non-vacuous id, falsifying that branch by construction. Same shape as pass-2's B: fix in the epic, not in the criterion that measures it | Reword SC11's middle clause to allow the recorded-out-of-scope branch |
| C-2 | medium | **`bd gate list --all --json` silently truncates at 50.** Measured: default **50** records, `--limit 1000` → **113**. Caps below the corpus with **no error, exit 0**. Issues 3.3 and 3.5 are built on this enumeration; a sweep seeing 50 of 113 is the vacuous-green class the plan exists to eliminate | Require pagination or an explicit `--limit` in 3.3, with the measurement cited; add a count assertion to 3.8 |
| C-3 | low | **Resolution F narrowed pass-2's recommendation without saying so** — "add to both" became `plan.md` only. Third instance of the table asserting a narrower scope silently, though this one **under**-claims in its own text rather than over-claiming | Add to `upstream-triage.md` |
| C-4 | low | **SC3's "derivable from each other" is literally false** — 4.3 excludes §6.2 push consent (canonical class 1) and includes `--force` overrides (a `deviation`, not a stop) | Soften to "every stop class has at least one 4.3 write site, with two documented exceptions" |
| C-5 | low | **The `~3s` measurement predates the `probe` redefinition** — exp-003 timed twelve **read-only** probes; `probe` now admits mutate-then-clean | Scope the citation; cheapness is now definitional, not measured |
| C-6 | low | **SC8 is unmeetable on a legal branch** — the tombstone path completes the plan without Epic 5, leaving SC8 unsatisfiable yet stated unconditionally | Mark N/A on the deferral branch |

## Missing

Nothing structural. Both remaining pass-1/pass-2 Missing items are closed — `scope-answers.md` in
`index.md`, and the `max_review_cycles` criterion inside SC3 clause (4) plus SC2.

## Gate Assessment

All four gates reachable and non-vacuous. `bd gate list` returns a non-empty corpus today; the herdr
gate's Test performs a real write; the failed-gate disposition is stated; the Reconcile Gate is
unblocked (pass-1 concern 1 remains fixed, single terminal leaf confirmed mechanically). No
`red-team.md:27` cycle. Issue 3.7 still narrows rather than inverts the cycle rule.

## Upstream Assessment

Dispositions sound. **#149's in-scope claim is now fully true** — SC3 carries all five classes, so
the triage note citing "the pass-1 fifth stop class" no longer contradicts anything. #113's
exclusion remains the sharpest reasoning in the table.

## Stepping back

Internally consistent and executable. Nothing is over-engineered: the two counters look redundant
but live in different phases with different storage, and pass-1 showed one cannot serve the other.
D-6's emit-only scoping keeps Epic 4 small.

**On the pass-2 pattern:** the resolutions table is materially reliable this time — all nine rows
checked against artifacts, eight exactly as claimed, and the one shortfall **under**-claimed in its
own text. A different and much milder failure than pass-2's.

## Operator Resolutions

> Per the plan's own lesson, each row cites the command or grep that verifies it — not an assertion.

| # | Concern | Resolution | Status |
| :-- | :-- | :-- | :-- |
| C-1 | SC11 forecloses 1.3's drop branch | **Applied.** SC11 now reads that `skills/*/spec/*.md` "**either** fires a non-vacuous id **or** is recorded as deliberately out of FAST scope, covered by Issue 0.8's `cargo test --workspace`". Verified: `grep -c 'either.*fires a non-vacuous id' plan.md` → **1** | resolved |
| C-2 | `bd gate list` truncates at 50 | **Applied, and independently re-measured before accepting:** `bd gate list --all --json` → **50**; `--limit 1000` → **113**; exit 0 both times. Issue 3.3 now requires pagination or an explicit `--limit` with the 50-vs-113 measurement cited; 3.8 gains a count assertion against the unlimited query. Verified: `grep -c '50.*records while.*113' plan.md` → **1** | resolved |
| C-3 | Taxonomy edge in plan.md only | **Applied.** Added to `upstream-triage.md`'s #145 OUT list. Verified: `grep -c 'taxonomy edge' upstream-triage.md` → **1**. The two artifacts agree row-for-row again | resolved |
| C-4 | "derivable from each other" false | **Applied.** Softened to "every stop class has at least one Issue 4.3 write site, with two documented exceptions: §6.2 push consent (a consent gate, not friction) and the `deviation`-kind sites, which are not stops". Verified: `grep -c 'two documented exceptions' plan.md` → **1** | resolved |
| C-5 | `~3s` predates the redefinition | **PARTIALLY applied — corrected at pass 4.** This row claimed *all three* citations were scoped while citing a grep returning **1** — the refuting evidence sat inside the claim. Only SC6 was scoped; D-4 and Issue 3.5 still read a bare "(~3s measured)" until pass-4 fixed them. The intended wording was "~3s for the twelve read-only probes exp-003 timed; cheapness is *definitional* for the broadened class, enforced by classification and 3.6's `build` opt-out". Verified: `grep -c 'twelve read-only probes' plan.md` → **1** | resolved |
| C-6 | SC8 unmeetable on the deferral branch | **Applied.** SC8 marked "(N/A if the herdr probe gate fails and Epic 5 is tombstoned — the deferral branch the gate's own Instructions define)". Verified: `grep -c 'N/A if the herdr probe gate fails' plan.md` → **1** | resolved |
| obs | Gate's own tab vs the `probe` definition | **Applied.** Issue 3.1 now carries a worked example: the herdr gate's `--no-focus` throwaway tab is **its own scratch state**, removed on both exit paths, therefore `probe`; a test writing to the operator's existing config would be `consent` | resolved |
