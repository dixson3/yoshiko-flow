---
type: Review
okf_spec: OKF-PLAN
id: pass-2
plan: plan-042-james-dixson-98631b
created: '2026-08-17'
verdict: REVISE
status: resolved
---

# Review pass 2 — adversarial (red-team)

## Verdict: REVISE

2 high, 4 medium, 6 low. **9 of 13 pass-1 resolutions verified as genuinely landed in the plan
body** — the reviewer checked the body rather than the table, as instructed, and found the four
that had not.

## The finding that matters most

**H1 is the third instance of this session's recurring failure**: a resolution recorded in the
table while the body still says the old thing. C4's fix landed in the **Decisions** table — D-R
was added and does say it supersedes D-C1 — but **every issue that actually implements consent
still specified the superseded `permissions.*` predicate**: Issue 3.1's text, Issue 3.6's test
cases, the Capability Gate's own Condition, the Scope section's pointer, and `context.md`.

So the gate *as an executor would have built it* was still claude-code-only, and would still
have auto-applied codex's `approval_policy = "never"` and opencode's `permission.* = "allow"`
with no consent. **The exact failure C4 identified, surviving inside the fix for C4.**

D-C1's row also carried **no superseded marker**, unlike D-P's strikethrough — so a reader
hitting it first got the wrong contract with no signal.

## Verified as landed (9 of 13)

C1/D-Q (seam is real — premise re-confirmed: `rg "rules_only|config_only"` → **zero matches**),
C2, C3 (*"a genuinely better gate than most plans ship"*), C5, C6, C7, C8, C11, C12, plus
M-A/R8, M-B/R9, M-C and U-A. The reviewer's summary: *"This is a real revision, not a
table-only one."*

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| H1 | **C4 landed in the Decisions table only.** Issues 3.1 and 3.6, the gate Condition, Scope, and `context.md` all still specified the superseded `permissions.*` predicate. D-C1 carried no superseded marker. | **high** |
| H2 | **D-R has no implementing issue and no SPEC amendment — a SPEC-first violation.** `rg consent_required` → **zero matches**; the field does not exist and no issue creates it, so Issue 3.1 consumed a field nobody writes. Worse: `REQ-YF-TUNE-001` enumerates the entry schema **exhaustively** (*"Each profile entry shall carry: a JSON path…, a recommended value, a kind…, and a one-line rationale"*), so adding a fifth field is a schema change to a testable REQ — and Epic 0 amended none. Adjacent: Issue 0.3 adds a rules-only REQ without naming **`REQ-YF-TUNE-012`**, the requirement it is an exception to. | **high** |
| M1 | **C2's fix contradicts C1's fix.** The gate blocked Issue 2.2 — the only issue wiring the sync into `self install` — while the Approach still claimed *"if Epic 3 slips, Epic 2 still closes the real gap"* and R5 was rated Low on that basis. Sharper still: the gate unblocks 1.3 *precisely because* `--rules-only` cannot write config, and 2.2 does nothing but call 1.3's routine. | medium |
| M2 | **C10 left two live `--prune` orphans.** Risk **R4** still described prune and pointed its mitigation at Issue 2.1 — now the rules-only mode, so an executor would have added prune tests to it. **SC10** still required amending `REQ-YF-MARK-004`, which left with `--prune`, making the criterion **unsatisfiable**. And `context.md`'s destructive-operations bullet still declared prune in scope. | medium |
| M3 | **Issue 3.3 declared no dependency on the mechanism that makes it possible.** It depended on 3.1 alone, reaching the rules-only *REQ* transitively but never the *implementation* — so the declared graph permitted 3.3 before 2.1, where it is unimplementable. | medium |
| M4 | **The scope reduction C10 asked for did not happen.** Count stayed at 22 (prune −2, D-Q +2), and H2 adds 2 more. The resolution's *"drops 2 issues"* was true of D-P in isolation and false of the plan. | medium |
| L1 | **Two success criteria numbered 9** — "SC9" ambiguous, and C8's resolution cites criteria by number. | low |
| L2 | Open questions still cited struck **D-P** as a resolution. | low |
| L3 | Epic 0 header still said *"Three requirements"* — true only while MARK-004 was in. | low |
| L4 | E5 summary still read prune's finding as live in-scope work. | low |
| L5 | Risk rows inserted mid-table (R1–R5, R8, R9, R6, R7). | low |
| L6 | **Gate test hides compile failure** — `--list 2>/dev/null` swallows a compile error, which then presents as "filter empty". Correct verdict, misleading diagnosis. | low |

## Gate Assessment

*"Structurally sound; semantically stale."* Graph verified by hand — all edges resolve, acyclic,
and the Capability Gate **reachable with its new Blocks set**. C2 and C3 both correctly fixed;
*"blocking 2.2 was the right call structurally, and the non-empty-filter guard closes the
vacuous-pass hole."* Two residuals: the Condition's **predicate** was the superseded one (H1),
so the gate as worded would pass on a codex/opencode machine that was never consented; and
blocking 2.2 collided with the Epic-2-independence claim (M1).

## Upstream Assessment

Clean. #154, #155, #156 all present as `exclude` with honest notes; *"#156's 'routing around is
not fixing' framing is exactly right."* One note: with `--prune` gone, Issue 4.3 is the only
upstream-filing issue and depends only on 1.2, so it can land early — fine, but the `_to file_`
coarse tracker must be filed at intake as stated rather than riding on 4.3.

## Strengths (verbatim)

- *"The skepticism was warranted and the verification was worth doing"* — 9 of 13 landed exactly
  as claimed, including all four of the hardest.
- *"D-Q is the right call and is properly threaded"* — REQ → implementation → consumer → gate
  rationale, with the premise re-confirmed.
- *"C3's fix is a genuinely better gate than most plans ship"* — proving a test filter non-empty
  before trusting its exit code is the right generalization of the R1 lesson.
- *"C8's resolution is quotably good"* — *"Fail-soft ≠ silent"* names the defect class precisely.
- *"D-P's strikethrough treatment is the correct pattern"* — H1's recommendation is simply to
  apply the same discipline to D-C1.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | Consent predicate stale in every implementing issue | high | Fixed **and grep-verified**: only three `permissions.*` occurrences remain, all deliberate (D-C1's strikethrough, D-R's rationale, and an explicit *"Do NOT use a key-path test"* prohibition in Issue 3.1). D-C1 now carries a `~~struck~~` superseded marker matching D-P's treatment, with its split preserved and only its predicate replaced. Issue 3.1 rewritten to the `consent_required` change-set test; Issue 3.6 rewritten in profile terms with the three-profile matrix moved **into** the issue; gate Condition rewritten; Scope and `context.md` repointed at D-R. | resolved |
| H2 | D-R unimplementable — no field, no REQ | high | Fixed. **Issue 0.6** amends `REQ-YF-TUNE-001` for an optional `consent_required` boolean (default false); **Issue 3.0** sets it on the four verified entries (claude-code `permissions.defaultMode` + `skipDangerousModePermissionPrompt`, codex `approval_policy`, opencode `permission.*`). Issue 3.1 now depends on 3.0; Issue 0.5 on 0.6. Issue 0.3 now names `REQ-YF-TUNE-012` as the requirement its rules-only mode is an exception to. | resolved |
| M1 | Gate blocking 2.2 contradicts Epic-2 independence | medium | Fixed by taking the reviewer's option (b) and making it precise: new **Issue 3.8** is the *single* issue that flips the exec off `--rules-only`, and **it** is what the gate blocks. 2.2 and 1.3 are unblocked because D-Q means neither can write config. pass-1 C2 is preserved — the shipping issue is still gated, it is just correctly identified. | resolved |
| M2 | Two live `--prune` orphans | medium | Fixed. R4 struck with a MOVED note (its mitigation pointed at an issue that no longer means what it said). SC10 rewritten to list the five requirements this plan actually touches, with a note that `REQ-YF-MARK-004` left with `--prune`. `context.md`'s destructive-operations bullet now reads *"none in this plan"*. | resolved |
| M3 | 3.3 lacked an edge to the rules-only implementation | medium | Fixed: `Issue 3.3 depends-on: 3.1, 2.1`, and its text now states CI suppression is implemented **by emitting `--rules-only`**, not by a second mechanism. | resolved |
| M4 | Scope did not actually shrink | medium | Accepted and stated honestly in the D-P row: 22 → 24; *"the plan is not smaller, it is differently composed"*, defensible because D-Q and D-R are review-surfaced safety work rather than creep. Recording the arithmetic rather than letting the resolution imply a reduction that did not occur. | resolved |
| L1 | Duplicate SC number 9 | low | Renumbered; criteria now run 1–11 with the deliberate `5a` sub-item. | resolved |
| L2, L3, L4 | Stale D-P / "three requirements" / E5 prune framing | low | All three corrected, with the E5 line marked historical rather than in-scope. | resolved |
| L5 | Risk rows inserted mid-table | low | Left as-is; the struck R4 row now explains the numbering gap, and renumbering rows other artifacts cite is the churn that caused H1's class of error. | resolved |
| L6 | Gate test hides compile failure | low | Fixed: dropped the `2>/dev/null` and added `echo "consent_gate tests found: $N"` so a compile failure is diagnosed rather than misreported as an empty filter. | resolved |
| U-note | `_to file_` tracker must be filed at intake, not ride on 4.3 | — | Confirmed — Phase 4.5 files it; Issue 4.3 files only the `--surface` blindness. No change needed. | resolved |
