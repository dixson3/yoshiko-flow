---
type: Review
okf_spec: OKF-PLAN
id: pass-5
status: complete
---

# Red-team pass 5

## Verdict: REVISE

Third independent pass, dispatched via `Agent`, with a sandbox spike executed against
`change_validation.py`, `plan_manager.py`, `beads_hygiene.py`'s SPEC, `DRIFT-CHECK.md` and live
`bd` data. Nine of pass-4's seventeen resolutions hold cleanly. **Eight introduced at least one new
defect, three of them high.**

## THE PRE-REGISTERED MEASUREMENT — the delegation did NOT help

`pass-4.md` recorded, **before** the resolution agent returned anything: baseline injection was
**4 defects across 11 resolutions ≈ 36%**; materially below → file the methodology upstream; at or
above → do not file, and say so.

| Classification | Concerns | Count |
| :-- | :-- | --: |
| **INJECTED** | C38, C39, C40, C41, C42, C43, C45, C46, C47, C48, C50 | **11** |
| PRE-EXISTING | C44, C49, C51 | 3 |
| NEW-CLASS | — | 0 |

- **Defects per resolution: 11 / 17 ≈ 65%** — directly comparable to the pre-registered 36%.
- Resolutions injecting ≥1 defect: **8 / 17 ≈ 47%**.

**Result: at or above baseline on either framing. Per the pre-registered response, the
`SKILL.md` §3 resolution-delegation change is NOT filed.** Recorded here rather than quietly
dropped, because a pre-registration that only publishes favourable outcomes is worthless.

Two caveats, neither of which rescues the result, both from the reviewer:

- The denominator cuts both ways — 17 resolutions is a larger, harder surface than 11, but three
  of pass-4's concerns were themselves injected by the prior round, so the sub-agent inherited a
  cleaner baseline on those.
- **Detection sensitivity differed.** C40, C41, C43 and C47 are all "the resolution asserts a
  runtime contract the named engine does not implement" — invisible to reading, visible only under
  execution. Pass 4 also built detectors, so this is a difference of degree, not kind; it belongs
  in the write-up, not in a footnote.

**The signal worth acting on is orthogonal to the delegation question.** Two defect classes
**survived a change of actor**, which is stronger evidence about where these defects come from than
the rate is:

- **Stale symbol/line references** — 8 (pass 3), then 3 (pass 4), then 1 (pass 5). Three rounds,
  three actors, same class.
- **plan.md-vs-satellite figure divergence** — exp-001's 163/101, then index.md's exp-002 line, now
  plan.md's exp-002 row. Three consecutive rounds.

Nothing mechanical catches either. `audit`, `doc_lint` and `plan_extract` were green through all
three.

## Strengths

- **C21 holds behaviorally.** Empty universe → exit 1; one-open → exit 1; all-closed → exit 0.
- **C22 holds.** 3.2a is an ancestor of 3.4, 6.1, 6.4; no cycles, no dangling `depends-on`, and
  `Discharged-by` closure is total in both directions.
- **Epic 4's premise is measured and true**, including something nobody had verified: `bd list
  --all --json` (0.7 s, 1481 beads) carries the `dependencies` array with `discovered-from` **and**
  both `created_at` fields. The 7-hour skew reproduced independently — bead `…T23:54:35Z` vs edge
  `…T16:54:35Z`.
- **C28's recorded invocation is exact** — `git archive fb79b44 | grep -h '^| SC' | wc -l` → 167.
- **SC14b is genuinely RED today**: the pinned span exists, contains 3 role files, and `Agent`
  appears **0** times. Arm (a) passes, arm (b) fails.
- **REQ-AGENT-046 exists** (`spec/agents.md:75`) and is the gate-reachability rule — which makes
  C38/C39 first-class SPEC violations, not style notes.

## Concerns

| # | Sev | Class | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C38 | **high** | INJECTED | **The gate contradicts four of the seven issues it blocks.** C25 moved the zero-on-GREEN observation onto the fix issues, but 1.4/2.4/3.4/4.5 — all inside `Blocks` — still say *they* record it (issue texts byte-unchanged from fb79b44). Under the issue reading the gate's evidence is produced inside its own Blocks set (a REQ-AGENT-046 cycle); under the Condition reading four Blocks members are no-ops | Keep the Condition; rewrite 1.4/2.4/3.4/4.5 as *verification* issues that consume the evidence rather than produce it |
| C39 | **high** | INJECTED | **Epic 5's gate membership is an unconditional cycle.** Epics 1-4 each have a dedicated GREEN re-run issue in `Blocks`; Epic 5 has none, so 5.2/5.4 — the issues that **build** the controls — were put in `Blocks` instead. Issue 5.0 says "assert **5.2's check** exits non-zero", and neither check exists. Per 0.2's contract a missing control is **2 = could not run**, which leaves the gate UNRESOLVED. **Deadlock: Issue 5.0's four fixture halves are not observable RED today** | Mirror Epics 1-4: drop 5.2/5.4 from `Blocks`, add Issue **5.5** (GREEN re-run, `depends-on: 5.2, 5.4`) and block on that; retarget the Condition's Epic-5 producer to 5.2/5.4; reword 5.0 to spike a stub |
| C40 | **high** | INJECTED | **Issue 4.3's exit-2 INCONCLUSIVE contract is false against the engine it names.** `change_validation.py:776-802`: `inconclusive` fires **only** when the first token of `cmd` is not on `PATH`; a command's own return code maps `0 → pass`, **everything else → fail**. Since the row's `cmd` starts with `uv`, a `.beads/`-less clone/worktree/CI gets **FAIL**, and `cmd_run` breaks the tier. This is the load-bearing premise of the C31 resolution, accepted without executing against the engine | Either exit 0 with a recorded `skipped` reason when `.beads/` is absent, or file upstream for a returncode→status map — and delete the exit-2 language rather than assert a contract the host cannot express |
| C41 | medium | INJECTED | **Issue 0.1's seven-id list omits the REQ for Epic 4's load-bearing half.** `beads_hygiene` has its own SPEC (key HYG, REQ-HYG-001..016) and REQ-HYG-011 governs a subcommand by name, so `attribution-audit` needs one. The only Epic-4 id enumerated covers Issue **4.4** — the half the plan itself calls "supporting, not load-bearing". SC1 checks that list and passes anyway. The exact failure an enumerated list invites: it looks exhaustive | Add `REQ-HYG-017` for `attribution-audit` and one for 5.2's parity check; update SC1's count |
| C42 | medium | INJECTED | **The C37 deviation put a SPEC edit inside an implementation issue and under-measured its blast radius.** The ordering instinct was right, the destination wrong: the token amendment touches `spec/agents.md`, so under SPEC-first it belongs in 0.1. And "both surfaces" is an undercount — `review:` appears in **REQ-PORT-006** (`portability.md:43,48,65,66,67`, its primary normative home) and **REQ-CLI-012** (`cli.md:68`). Meanwhile `plan_manager.py:3781` already keys on `REVIEW_PASS_TOKEN` with a legacy fallback | Move the amendment into 0.1; enumerate REQ-PORT-006 and REQ-CLI-012; note the implementation is already correct — this is spec-catches-up |
| C43 | medium | INJECTED | **0.1's `e-spec-compliance` justification is unverified inference.** `DRIFT-CHECK.md:138` scopes that edge to `spec` → `skill-md`; there is **no declared edge** between `spec/*.md` and `agents/*.md`. The un-retargeted `Verification:` would fail nothing. Asserted a mechanical consequence without measuring it — in a plan whose D-5 exists to forbid that | Restate as "so the citation stays true", or file the missing spec↔agents edge as the real gap |
| C44 | medium | PRE-EXISTING | **Epic 5's two checks have no named runnable host** — `grep CHANGE-VALIDATION` returns three hits, all Epic 4. Issue 4.3 states the rule: "A check with no host is the M5 vacuity this plan exists to end" | Add a §1 `fast` row and §3 glob for both Epic-5 checks in the issue that builds them |
| C45 | medium | INJECTED | **SC14's non-emptiness assertion converts "cannot run here" into FAIL** — the opposite of what 4.2 got in the same round. Two adjacent controls, opposite policies | Give 5.2 the three-valued contract (0 match / 1 differs / **2 no copies**) and have SC14 assert exit **2** on the empty set |
| C46 | medium | INJECTED | **plan.md's EXP-002 row contradicts both the finding and index.md.** `plan.md:114` still says "each with a **different** improvised reason"; the finding and index.md say **29 distinct**, and index.md even says pass-3 C20 corrected it. Third consecutive round to produce a plan.md-vs-satellite divergence | Change `plan.md:114` to "29 distinct improvised `close_reason` values" |
| C47 | medium | INJECTED | **SC8 is not runnable without network and `gh` auth.** `_verify_row` calls `_gh_issue_view` unconditionally as its first act; on failure it returns `inconclusive` **before consulting any table**, so pre- and post-mutation verdicts are identical and SC8 fails for a reason unrelated to the property | Add "with `_gh_issue_view` stubbed to a fixed payload", and name the disposition the mutation targets |
| C48 | low | INJECTED | **`plan_manager.py:1404` is a wrong line reference, in two files.** The regex is at 1403, the `def` at 1408, the `.search()` at 1415; 1404 is the middle of a string literal. Third consecutive round to produce a stale reference | Cite `:1415` (the `.search()` carrying first-match semantics), or drop line numbers for symbol names |
| C49 | medium | PRE-EXISTING | **`upstream-triage.md` is 47/49 blank.** Every one of the twelve rows the plan acts on has an empty `**Disposition:**`, while `index.md` calls the file "the triage record behind plan.md's Upstream Issues table". Pass 4's C29 flagged #183's blank and missed that the whole document is blank — a spotlight on one row inside an empty room. `audit` passes | Fill the twelve from plan.md's Notes, or narrow index.md's claim |
| C50 | low | INJECTED | **SC10's "Two of the six are REAL rows" undercounts** — `include`, `partial`, `deferred`, `exclude` are all real and `tracker` becomes real via 6.3. **Five of six**; only `supersede` is synthetic | Restate as five, naming `supersede` as the synthetic one |
| C51 | low | PRE-EXISTING | **Issue 0.2a's "817 unfiltered" is already stale** — measured 820 now. The excluded figure (**757**) reproduces exactly, which is the point of self-exclusion | Delete the unfiltered figure; keep only the excluded one |

## Deviation assessment

- **C29 (#183 `exclude`, not `tracker`): CORRECT.** `.search()` is first-match-wins, so a #183
  tracker row would stamp plan-050's epic with plan-049's URL; and `supersede` requires CLOSED as
  `NOT_PLANNED`, false of a completed plan. Independently confirmed. The reviewer added a check the
  deviation did not claim: `verify-reconcile` filters `exclude` before `_verify_row`, so SC17 is
  unaffected. **Sub-agent right, pass 4 wrong.** Only defect is the line number (C48).
- **C37 (token fix folded into 5.1): HALF RIGHT.** Ordering instinct correct, destination wrong
  (SPEC edit belongs in 0.1), blast radius undercounted (C42).

## Missing

- No Epic-5 GREEN re-run issue — the direct cause of C39.
- No `REQ-HYG-*` for `attribution-audit`; no REQ for 5.2's parity check (C41).
- No named runnable host for either Epic-5 check (C44).
- **No success criterion for the assert-distinguishes / zero-on-GREEN half at all** — SC2 covers
  `record-red` only, so the half the C25 rewrite created is uncovered.
- No stub/offline seam for `_gh_issue_view`, which SC8 now depends on (C47).
- `upstream-triage.md` dispositions for the twelve acted-on rows (C49).

## Gate Assessment

Four gates, all parsing. Start Gate and Upstream-write conformant — and `grep` confirms **zero**
remaining `Issue 3.2` verb references, so C27 is fully resolved including the third the resolution
agent found itself. **The Reconcile Gate is fixed**, behaviorally re-verified on three inputs.

**The driven-red gate is worse than at pass 4, not better.** Structurally it looks clean — no
cycles, every named producer outside `Blocks`. But structural reachability is not evidence
reachability, and on evidence it fails twice: the Condition and the blocked issues disagree about
who records the GREEN observation (C38), and Epic 5 is an unconditional deadlock because the
control-builders were put inside `Blocks` (C39). **Widening `Blocks` is the specific move that
broke it.**

## Upstream Assessment

14 rows, all parse; every `include`/`partial` names a resolver that resolves in the DAG. C30 is
resolved across all eight sites. Three problems: the triage record is empty for every acted-on row
(C49); #183's `exclude` is right but its line citation is wrong (C48); SC10 understates coverage
(C50). #149's `partial` is well-founded — but **its named host does not honour the contract 4.3
claims for it** (C40), which is the single change to make before approval.

## Resolutions

**Operator decision: SPLIT (D-9).** Epics 4 (M9/#149) and 5 (#182/#184) go to **plan-051**; this
plan lands the four mechanical fixes. Six of the fourteen concerns leave with the deferred epics —
including two of the three highs, both of which pass 5 judged structural rather than patchable.

| Concern | Sev | Class | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| C38 | high | INJECTED | Issues 1.4, 2.4, 3.4 rewritten as **verification** issues that *consume* the evidence; the gate Condition now says so explicitly. The Condition/issue-text contradiction is gone in the direction that removes the REQ-AGENT-046 cycle | `main-session` | resolved |
| C39 | high | INJECTED | **Left with the split.** Epic 5's deadlock was structural — the control-builders sat inside the gate's own `Blocks` set | — | deferred to plan-051 |
| C40 | high | INJECTED | **Left with the split**, and independently confirmed at source first: `change_validation.py:776-802` produces `inconclusive` only when the first token is off `PATH`; a command's own returncode maps `0 → pass`, everything else → `fail`. Recorded as plan-051's starting evidence | `main-session` | deferred to plan-051 |
| C41 | med | INJECTED | Inverted by the split: Issue 0.1 now enumerates **four** ids, and the M9/Epic-5 ids left with their epics. An enumerated list that silently retains ids for descoped work is the same defect, and 0.1 says so | `main-session` | resolved |
| C42 | med | INJECTED | **Left with the split** (Issue 5.1 is deferred) | — | deferred to plan-051 |
| C43 | med | INJECTED | The unverified `e-spec-compliance` claim is gone from 0.1 with the Epic-5 REQs | `main-session` | resolved |
| C44 | med | PRE-EXISTING | **Left with the split** (Epic 5's hostless checks) | — | deferred to plan-051 |
| C45 | med | INJECTED | **Left with the split** (SC14) | — | deferred to plan-051 |
| C46 | med | INJECTED | `plan.md`'s EXP-002 row now reads **29 distinct** — plan.md, the finding and index.md finally agree. Third consecutive round to produce this class | `main-session` | resolved |
| C47 | med | INJECTED | SC8 now specifies `_gh_issue_view` **stubbed to a fixed payload**, names the `include` entry as the mutation target, and records why: `_verify_row` returns `inconclusive` before consulting any table | `main-session` | resolved |
| C48 | low | INJECTED | Both citations now name **`_TRACKER_ROW_RE.search()`** — the symbol carrying first-match semantics — instead of a line number. Line numbers went stale in three consecutive rounds | `main-session` | resolved |
| C49 | med | PRE-EXISTING | All **14** acted-on triage rows filled from plan.md; `index.md`'s claim narrowed to the truth — the file is the candidate pool, plan.md's table is authoritative, and the 33 unscored rows are deliberately blank | `main-session` | resolved |
| C50 | low | INJECTED | SC10 now says **five of six** are real, naming `supersede` as the only synthetic one | `main-session` | resolved |
| C51 | low | PRE-EXISTING | The unfiltered figure is deleted; only the excluded **757** remains, with the reason (817 → 820 drifted within the drafting session; the excluded figure reproduced exactly) | `main-session` | resolved |

## Post-split state

5 epics (0-3, 6 — gap deliberate), 22 issues, 30 edges, 4 gates, 17 criteria, 14 upstream rows,
**0 unparsed, 0 dangling**; `doc_lint` PASS 0 findings; `audit` pass; markdown-lint clean.

The driven-red gate is back inside its own scope: Condition covers Epics 1-3, `Blocks` is
`1.4, 2.4, 3.4`, and every named producer is an ancestor of a blocked issue and outside the Blocks
set. `SC2b` was added — pass 5 found the assert-distinguishes half had **no criterion at all**.
