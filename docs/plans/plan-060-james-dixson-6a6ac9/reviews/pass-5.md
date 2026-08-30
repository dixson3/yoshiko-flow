---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 5 — VERDICT REVISE. One high, at the exact site of pass 4''s high and found the same way: by RUNNING the prescribed command instead of reading it. Three lows. All four resolved.'
---
# Review pass 5 — adversarial (red-team)

## Verdict: REVISE

One **high**, at the exact site of pass 4's high — *"and found the same way pass 4 found it: by
running the prescribed command instead of reading it."* Three lows. **All 4 concerns resolved** by
the main session.

**Date:** 2026-08-29
**Dispatched as:** sub-agent (REQ-AGENT-049), read-only with respect to the repository under review.
**Subject:** plan.md after the pass-4 revision (7 epics, 49 issues, 86 edges, 41 criteria).

The reviewer's own framing: *"Everything else is verified landed and mechanically green; if C1 is
folded in, this plan is done."*

## Verification of pass-4's resolutions

| | Landed? |
| :-- | :-- |
| C1 tracked-ness / presence split | **partially** — see C1 below |
| C2 four sites, per-site recovery | **yes** — Issue 3.5 carries four sites and names `restore` wrong for L16; Issue 0.2 names all four states |
| C3 SC31 five cases + rename | **yes** — the two "four"s now denote the same set |
| C4 duplicated paragraph | **yes** |
| C5 31 -> 32 | **yes** — measured 32 rows, 32 distinct names, 0 duplicates |

## Strengths

- **The C2 propagation sweep came back clean.** Every Approach claim was checked against its
  implementing issue and criterion — conflict sites, journal state set, the L6-not-L7 boundary, L5's
  advisory-in-verdict-not-in-execution, the stop-class-1 halt, strategy-aware prune, `#301 closed as
  amended`, redeploy-iff-`skills/`. **The pass-3-C1 / pass-4-C2 pattern did not recur.**
- **Gate reachability and frontloading both hold.** The redeploy gate's instructions require a pushed
  green merge — under this plan's L-order the merge (L6) precedes reconcile (L7), so the condition is
  satisfiable at its anchor and cannot be hoisted earlier.
- **Round-5 vacuity sweep clean.** Every runnable criterion reproduces its recorded value under
  `bash -c`. SC34's negative half is load-bearing (`${MERGE_TARGET}"...HEAD` occurs once today,
  `HEAD^1..HEAD` zero times). No new unsatisfiable criterion.
- **Bidirectional integrity** at 49 / 41 / 86 / 18: zero dangling in either direction, zero forward
  references, zero issues discharging nothing.
- **The failure model degrades correctly** — because `predicted_tree` and `resolved_target_tip` are
  digest-covered and §3 re-derives every fact, a dry-run/apply divergence surfaces as a **halt**
  rather than a wrong write. *"This is what keeps C1 from being catastrophic."*
- **Mechanically green:** `doc_lint` PASS 0/0, `gate_consistency` PASS 5 gates 0 findings, `audit` all
  checks passed.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **The C1 fix replaced tracked-blindness with gitignore-blindness *in the plumbing itself*, and Issue 1.9 carries a measurement that is false from one of the two checkouts it spans.** 1.9 prescribed, for presence-on-disk, `git ls-files --others --exclude-standard`, `git status --porcelain=v2`, or a scoped listing — but **`--exclude-standard` IS "honour `.gitignore`"**. Measured from the **primary checkout** over the same bundle: `ls-files --others --exclude-standard .worktrees` -> **0**; `status --porcelain=v2 -- .worktrees` -> **0**; `check-ignore -v .worktrees` -> `.gitignore:31:/.worktrees/`. The 37 result holds **only** with `git -C <worktree>`, which 1.9 carries on the *tracked-ness* branch and **drops** on the presence-on-disk branch. `land` spans both checkouts and **`--apply` runs primary-side**, so the designed path is the one returning zero. Two of three prescribed tools return **0 for the exact artifact class the issue names**, and *"an omission from enumeration is silent"* is 1.9's own sentence. **SC10b does not bind**: it pins **no cwd for the enumerating process**, so a test author enumerating with `-C <worktree>` makes the word "gitignored" vacuous and passes with defective code — the same shape as pass 4's finding, one layer over. **This is the third consecutive round in which the enumeration prescription carried the same blindness class.** | State that `--exclude-standard` and `git status` are themselves gitignore-honouring, must run via `git -C <worktree>` or a non-git scoped listing, and that from the primary checkout both return 0; qualify the "37" with the checkout it was measured from. **Pin SC10b's enumerating cwd to the primary checkout.** Correct `criteria-validation.md`: gitignore-blindness is *not* only a shell artifact. |
| C2 | low | **Upstream table / annotation asymmetry — a recurrence of pass 1's C13.** Issue 1.9 carries `resolves-upstream: #263 (partial)` but the `#263` row's `Resolved By` lists only `0.9, 1.6`. The only asymmetry among 18 rows, introduced in the pass-4 revision. No mechanical check catches it — `doc_lint`, `gate_consistency` and `audit` are all green with it present. | `Resolved By: 0.9, 1.6, 1.9`; add 1.9's case to the triage notes. |
| C3 | low | **The schema reserves an `exceptional` / `exception_rationale` field that no rule governs and §3 does not list.** §3 enumerates every field as trusted-or-re-derived; `exceptional` appears in neither column, and §2 never says what it does. The schema's central claim is *"there is no field in which it can assert … that anyone authorized anything"* — **a boolean the agent sets whose effect is unspecified is precisely the shape that claim forbids.** | Delete it, or add a §3 row stating it is inert prose surfaced in the consent prompt and can never widen a step. |
| C4 | low | **`criteria-validation.md` still prescribes the retired tracked-only fix** in its §2 — the exact wording pass 4 corrected. The later section does correct the record, so the document reads as a chronology, but a reader who stops at §2 gets the superseded prescription. Same file: *"36-file bundle"* is now **37**, drifted by one review file — the derived-figure-in-prose class Issue 0.10's instrument exists to catch. | Add a forward-pointer at the superseded paragraph; re-measure or de-emphasise the count. |

## Missing

- **SC17 asserts `exit 3` for the tty refusal, and no issue allocates it.** Issue 3.3 specifies the
  predicate but not the code; Issue 0.3 commissions "the exit vocabulary" generically. Not blocking —
  0.3 is the right home — but the number should appear there rather than only in the criterion that
  tests it.
- Nothing else. The items passes 3 and 4 left standing remain accepted and are not re-raised.

## Gate Assessment

**Clean, re-verified mechanically this pass.** `gate_consistency.py` PASS, 5 gates, zero findings.
Reachability holds at every gate; both `reconcile step` gates sit at the last anchor their evidence
permits and cannot be hoisted. Issue 1.9 sits in Epic 1, outside every `Blocks` set, so C1 raises no
reachability question. **No cycles, no frontloading misses.**

## Upstream Assessment

**Sound in disposition, one bookkeeping asymmetry (C2).** Every annotation targets a listed issue and
every disposition matches its row — zero disposition conflicts across 18 rows. Dispositions remain
well-judged: `#301 -> include -> CLOSED "as amended"` is justified by D-11 rather than asserted; the
seven `partial` rows each name their in-scope half concretely; the `exclude` rows each carry a reason
that survives reading. Issue 1.9's `#263 (partial)` claim is **apt on the merits** — *"an enumeration
that reports zero where the answer is 37 is precisely two-facts-one-signal"* — which is why the table
should carry it.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 — the fix was itself gitignore-blind, primary-side | high | **Accepted; re-measured before fixing, and it is worse than stated.** From the primary checkout: `ls-files --others --exclude-standard .worktrees` -> **0**, `status --porcelain=v2` -> **0**, `ls-files --others` (no flag) -> **1** (the directory, unrecursed). Only `git -C <worktree> …` (**37**) and a non-git scoped listing (**37**) work. Issue 1.9's presence-on-disk branch is rewritten around **WHERE the enumerating process runs, not which flag it passes**, states that `--exclude-standard` and `git status` are themselves gitignore-honouring, gives both measurements with their checkout, and notes that `--apply` runs primary-side — the side that returns zero. **SC10b now pins the enumerating cwd to the PRIMARY checkout**, with the reason stated inline: *"without that pin a test author can enumerate with `git -C <worktree>` and make the word 'gitignored' vacuous, which is how this blindness survived three rounds."* `criteria-validation.md` gains a fourth section correcting its own earlier "only the first is a shell artifact" sentence, which was true and **read too narrowly, including by its author**, and a four-row table of divergences by direction and cause (shell / plumbing / plumbing / plumbing). | `main-session` | `resolved` |
| C2 — `#263` Resolved By asymmetry | low | **Accepted.** `Resolved By: 0.9, 1.6, 1.9`; the triage notes now name 1.9's enumeration case. Re-verified mechanically: **zero** annotation-to-table asymmetries across all 18 rows. | `main-session` | `resolved` |
| C3 — an ungoverned `exceptional` field | low | **Accepted, and the reasoning is the point: an unspecified boolean the agent sets is exactly the shape §2's central claim forbids.** Rather than delete it, §3's re-derivation table gains a row declaring it **INERT BY CONTRACT** — prose surfaced verbatim in the consent prompt, which can never enable a step, widen a step, satisfy a halt, or stand in for a re-derived fact. Its effect is now *specified as nothing*. | `main-session` | `resolved` |
| C4 — superseded prescription and a drifted count | low | **Accepted.** A forward-pointer is added at the superseded paragraph naming both later corrections; the bundle count is given as "36 when first measured, 37 by the next review pass" with a note that the figure drifts as review files are added and is therefore not the claim. | `main-session` | `resolved` |
| Missing — `exit 3` unallocated | — | **Accepted.** Issue 0.3 now commissions the exit vocabulary *"including that the controlling-terminal refusal is **exit 3**, the gate-signal code, not 1 or 2"*, so SC17's number has a home in the requirement rather than only in the criterion that tests it. | `main-session` | `resolved` |
