---
type: Review
okf_spec: OKF-PLAN
id: pass-7
description: Red-team pass 7 — verdict APPROVE; C1 independently recomputed and confirmed closed
---

# Red-team pass 7

## Verdict: APPROVE

> **The high-severity defect is genuinely closed, and I verified it from scratch rather than from the
> table.** Two of the three claimed fixes landed; the third (C3, low) did not, and I found two more
> items of the same low-severity prose class plus one medium worth a one-clause edit. **None blocks.
> A pass-8 cycle would not earn its cost.**

## Resolution verification — pass 6's three claims

| # | Claim | Actual |
| :-- | :-- | :-- |
| C1 | Bounded `no-req-required` exemption `{4.6, 4.7}`; predicate holds for all 23 non-exempt issues | **LANDED and INDEPENDENTLY CONFIRMED** |
| C2 | Duplicated phrase deleted from `upstream-triage.md` | **LANDED** — both copies now agree in substance |
| C3 | 0.4's stranded fragment reflowed | **NOT LANDED.** Recorded `resolved`; it was not |

### C1 recomputed independently — own parser, own regex, own closure

Regex `REQ-(?:[A-Z]+-)+\d+`, which matches the three-segment ids the earlier `REQ-[A-Z]+-\d+` could
not. Predicate tested **as specified** — path to an Epic-0 issue that *names* a `REQ-*`, not to any
Epic-0 issue.

- Epic-0 issues naming a `REQ-*`: `{0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9, 0.10}`; `0.6` and `0.8` name
  none — reproduced.
- Epics 1-5: **25** issues, **23** non-exempt. **All 23 reach a naming Epic-0 issue. Zero failures.**
- `4.6 → {0.8}` and `4.7 → {4.6, 0.8}` both compute `False`. **The exemption is load-bearing, not
  decorative** — without it the check fails on exactly those two.
- **Robustness check added:** 0.7 enters the "names a REQ" set only because it *cites* ids on its own
  `cited-not-touched` list. Re-ran with 0.7 removed — **still zero failures**. The predicate holds
  under **both** readings.
- Structure re-reproduced: **35 issues, 70 edges, 0 dangling, 22 criteria.**
- 0.7's collateral claim that exactly one Epic 1-5 issue names an id — verified: it is **2.3**.

## Strengths

- **The C1 fix is substantively right, not merely textually present.** The exemption ground — "neither
  changes `yf` behaviour" — is the exact negation of what the assertion exists to catch, so it is
  semantically coherent rather than an ad-hoc patch, and every clause of its stated evidence checks out.
- **The exemption set is independently recomputable in one run**, being precisely the complement of the
  computed predicate. A reviewer never has to trust the list.
- **The DAG is clean** — 70 edges, no dangling reference, no cycle, well-defined topological order.
  Every criterion's `Discharged-by` names the issue that creates its checker; every gate `Test:` names
  a script an issue authors.
- **The ordering arguments are the strongest part of the plan and survive re-reading.** 2.2 ← 2.3;
  5.2's quarantine-before-verify; 5.2a before 5.2. **Each is derived from a measurement, not asserted.**
- **Honest scope-narrowing throughout** — R11 narrows R3's claim rather than defending it, EXP-007's
  76/76 is explicitly capped as name-keyed and structurally blind to the foreign population, and
  #256/#238/#239 all carry explicit IN/OUT.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| P1 | medium | **0.7 does not say WHERE the `no-req-required` set is declared, and the natural reading makes its tripwire inert.** One sentence earlier 0.7 says the script carries the `cited-not-touched` list — by parallel an implementer puts the exemption set in the script too. Then declared ≡ baseline always, and the tripwire compares a constant to itself: dead code that can never fire |
| P2 | low | **C3 was recorded resolved and is not fixed.** 0.4 still ends `"…governed by nothing: a per-row surface-dir override var and a three-valued precedence…"` — the clause after the colon is verbatim the pre-edit surface-column description, grafted where it does not parse. Three sentences, not the claimed two |
| P3 | low | **A second stranded fragment of C3's exact class, in 0.8**, missed by all six prior passes: `"…leaves behind. editing a completed plan's bundle…"` — lowercase start, no subject, the residue of a deleted lead-in. A grep for `\. [a-z]` returns exactly this one hit, so the class is **enumerated rather than sampled** |
| P4 | low | **"The set" is overloaded inside one paragraph of 0.7**, with two different exit-2 rules attached — the derived id set and the exemption set. A reader can apply the empty/single-element rule to the two-element exemption set and conclude the checker exits 2 unconditionally |
| P5 | low | **The Start Gate's issue count is stale by two in both numbers** — "the 31st of 33 issues" where the plan has 35 and 5.2 is the 33rd. Purely rhetorical, but a number six passes read past |

## Missing

**Nothing above medium.** Re-walked the behaviour set against pass 6's closure table — no sixth
uncovered behaviour. Three fresh-defect axes all came back clean: dependency graph, criterion↔creator
wiring, and the deferred set (`4.1-4.5` appears only in D-14, the #256 row and the Deferred table,
never as a live `depends-on`).

> That six passes and 62 resolved concerns have driven the residue down to four low-severity
> prose/counting items and one one-clause specification gap **is itself the finding**. The remaining
> defects are all one class — **stale text surviving an edit** — which is a copy-editing pass, not
> another adversarial cycle.

### Scoped answer: does the bounded exemption close C1, or relocate the hand-authored-list problem?

**It closes it, and the two lists are not equivalent — but only if P1 is fixed.**

| | `cited-not-touched` | `no-req-required` |
| :-- | :-- | :-- |
| Size | unbounded — grows with every cited id | 2, bounded by an explicit tripwire |
| Derivable? | **no** — a human judgement | **yes** — the complement of the computed predicate |
| Failure direction | false PASS, invisibly | false PASS, but each addition is a visible diff in the reviewed artifact |
| Reviewer-verifiable? | only by re-reading every citation | **verified mechanically in this pass** |

L2 is a *different kind* of list: small, closed-form, checkable against the very predicate it exempts
from. The gap is that the tripwire's strength depends entirely on an unstated implementation detail.

## Gate Assessment

**Sound; re-verified independently.** Start Gate carries the frontloaded drivability confirmation —
no frontloading miss. Live-harness gate reachable, with `codex login status` a genuinely falsifiable
arm. Migration-apply gate: **no cycle** (evidence producer 5.1 is outside its `Blocks` set), and the
three-way exit discipline is right — 2 on unparseable, 1 on bad-or-**empty** `delete`, 1 on non-empty
`undetermined`. **The empty-set failure is the non-obvious correct choice, and EXP-007 was commissioned
specifically to show it will not fire spuriously.** All four reachable; none sits later than its
evidence requires.

## Upstream Assessment

**Dispositions defensible; no change recommended.** #257 `include` correctly. #238/#239/#256 all
`partial` with explicit IN/OUT stating why `include` would overclaim. #121/#243/#240 `exclude` on one
principled line — **#243's row remains the strongest in the table**, excluded on surface grounds *and*
cited as the exact hazard 5.2a's quarantine exists not to reproduce. #255 `deferred`, sequencing only.
Both out-of-scope defects route upstream with their measurements and appear in SC20's `Discharged-by`.
The reconcile loop is closed.

## Recommendations

1. Name the declaration site for the exemption set (P1).
2. Fix the two stranded fragments and the stale ordinal; name the two sets distinctly (P2-P5).
3. **Execute.**

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| P1 | medium | 0.7 now states **where each half lives**: the `no-req-required` set is declared in the issue body in `plan.md` and parsed from there; the script hardcodes the baseline `{4.6, 4.7}` and exits 2 on any parsed member outside it carrying no reason. The rationale is stated — both halves in the script makes the comparison a constant against itself | `main-session` | `resolved` |
| P2 | low | 0.4 genuinely split at the colon this time, and **pass-6.md's C3 row corrected in place** to record that it was false when written rather than leaving a wrong record | `main-session` | `resolved` |
| P3 | low | 0.8's second fragment fixed by restoring the deleted lead-in. Re-ran the `\. [a-z]` grep: 4 remaining hits, **all legitimate** — sentences correctly beginning with the lowercase binary names `pi` and `codex` | `main-session` | `resolved` |
| P4 | low | The two sets are now named distinctly — "the DERIVED ID SET" vs the exemption-set tripwire — with a parenthetical stating they are two rules over two sets | `main-session` | `resolved` |
| P5 | low | Ordinal replaced with "one of the last three issues", which cannot go stale on the next insertion | `main-session` | `resolved` |

**All 5 concerns resolved. This file is now FROZEN.**
