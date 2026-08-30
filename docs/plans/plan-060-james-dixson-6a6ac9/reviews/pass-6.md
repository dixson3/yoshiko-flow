---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 6 — VERDICT REVISE. First pass to review the final revision, on an operator-granted bound raise. One high: --others is itself a tracked-ness filter, the FIFTH incarnation of the enumeration blindness, exposed by the operator''s own mid-review commit. All six resolved.'
---
# Review pass 6 — adversarial (red-team)

## Verdict: REVISE

One **high**, plus a resolution recorded as landed that had not. **All 6 concerns resolved** by the
main session.

**Date:** 2026-08-29
**Dispatched as:** sub-agent (REQ-AGENT-049), read-only with respect to the repository under review.
**Subject:** the final revision, on an operator-granted `--max-review-cycles 6` (ESC-001). **This is
the first pass to review the final revision** — the reason the operator spent the raise.

The reviewer's own framing: *"I ran the prescriptions rather than reading them, from both checkouts
and in a clean sandbox fixture. Pass-5's C1 fix is correct on the axis it names and still incomplete
on a fourth axis, and the falsifying event is inside this bundle's own history."*

## Strengths

- **The WHERE-not-which-flag reframing is right, and every number in it was confirmed.**
- **SC10b's cwd pin binds on the axis it was written for** — spiked in a clean fixture, a naive
  `--exclude-standard` from a primary cwd sees nothing under the gitignored worktree.
- **Round-6 vacuity sweep clean; round 6 added no criterion.** 41 criteria, 41 distinct names, zero
  duplicates; every runnable command reproduces its recorded value. `check-pytest-ran.sh` is
  non-vacuous in both directions. SC34's negative half is still load-bearing.
- **Bidirectional integrity holds at 49 / 41 / 86 / 18** — zero dangling either way, zero forward
  references, **zero cycles (DFS)**, zero issues discharging nothing, zero annotation asymmetries.
- **`doc_lint` PASS 0/0 on `plan.md` and all 20 other lintable documents individually**, including
  the two new ones. `gate_consistency` PASS. `audit` all checks passed.
- **ESC-001's `on_no_answer` correction is verifiably true** — `a5664e7` is 39 files, the branch
  carried zero commits before it. *"The correction states a fact I re-measured, and it states it
  against its own author's interest."*

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **`--others --exclude-standard` is itself a TRACKED-NESS filter, so Issue 1.9's presence-on-disk prescription silently omits every TRACKED file — the fifth incarnation of the same class, and this bundle's own history falsifies it.** The worked example gave `git -C <worktree> ls-files --others --exclude-standard` -> **37**; that held **only because the bundle happened to be untracked**. After the operator's mid-review commit, that exact command returns **0** while the answer is **40**. Sandbox-spiked on a clean fixture (one tracked draft + one untracked + `plan.md`): the prescribed branch returns **1 of 3**, omitting the tracked draft; a scoped listing returns **3 of 3**; the union returns **3**. `--others` is the exact complement of `ls-files` — **neither alone is a presence fact**, and 1.9 states only the first half of that. The named consumer is `upstream.rows[].draft_present`, and its premise — *"untracked BY CONSTRUCTION at `--dry-run` time"* — is **refuted by this very bundle**, whose `assets/` are committed pre-landing; `commit-plan` exists to do exactly that. 1.9's own closing sentence applies: an omission from enumeration is silent. | Mandate the scoped listing, or the explicit union, via `git -C <worktree>`. Retire the "untracked BY CONSTRUCTION" premise and replace it with the measured counter-example. Re-measure the 37s. |
| C2 | medium | **SC10b's fixture cannot discriminate C1's defect, so the criterion is satisfiable by defective code.** The cwd is pinned — the axis pass 5 fixed — but the fixture carries only an *untracked* draft, which an `--others`-only implementation enumerates completely. **Pass-5's own warning shape, one axis over.** | Extend the fixture to carry **both** a tracked and an untracked draft, and require both to be returned. |
| C3 | medium | **The positive-control entry claims more than any artifact in this bundle can carry, and it is the one self-favourable unfalsifiable claim in a bundle whose thesis is that such claims are the defect.** `ESC-001.answer` is **free text written by the session** recording what the operator decided — structurally #293's artifact class, not its contrast. Nothing distinguishes "the operator answered and the session recorded it" from "the session wrote the answer itself". `asked_of` is empty; `push_batch` has no verifiable upstream trace. | Keep the entry, scope the claim to what the artifact proves — the session halted and did not pass `--max-review-cycles` itself — and state that the *answer* is a first-party record with no resolver identity, so it is a positive control on the **behaviour**, not the **artifact**. |
| C4 | low-medium | **A pass-5 resolution is recorded as landed and did not land.** Pass-5 C4's cell claims a forward-pointer was added at the superseded paragraph; there is none, and the retired tracked-only prescription still reads as current. Only the count half landed. | Add the pointer and correct pass-5's Resolutions cell. |
| C5 | low | **Four cited figures are now false, all from the same event, and one names a fixture that no longer exists.** The 36/37s are now 40/0, and *"the cheapest possible fixture for SC10b is sitting in the repository right now"* is false — the bundle is 40 tracked / 0 untracked. **R12 / Issue 0.10's class caught live.** | Re-measure and qualify; replace the fixture claim with a constructed one. |
| C6 | low | **REQ-PORT-052's fencing rule is missed in three evidence cells** — an unfenced verbatim `SKILL.md` quote and several unfenced paths. `doc_lint` is green with all three present. | Backtick the quoted sentence and the paths. |

## Missing

Nothing new. The items passes 3–5 left standing remain accepted. Noted, not a concern:
`review-loop-check` still reports `limit: 5` — the raise is per-invocation and correctly not
persisted; `log.md` carries the operator bullet; count-equality holds.

## Gate Assessment

**Clean, re-verified mechanically.** `gate_consistency.py` PASS, 5 gates, zero findings. Reachability
holds at every gate; both `reconcile step` gates sit at the last anchor their evidence permits. **Issue
1.9 sits in Epic 1, outside every `Blocks` set, so C1 raises no reachability question — it is a
specification defect, not a gate one.** No cycles, no frontloading misses.

## Upstream Assessment

**Sound, and pass-5's bookkeeping asymmetry is fixed.** `#263` reads `0.9, 1.6, 1.9` with the triage
note naming 1.9's case. Programmatic sweep: zero annotation-without-table, zero table-without-
annotation, zero disposition conflicts across 18 rows. **C1 changes no disposition** — 1.9's
`#263 (partial)` claim is *strengthened* by it: an enumeration returning 0 where the answer is 40 is
precisely two-facts-one-signal.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 — `--others` is a tracked-ness filter | high | **Accepted; re-measured on the committed bundle before fixing:** `ls-files` -> **40**, `--others --exclude-standard` -> **0**, union -> **40**, scoped listing -> **40**. Issue 1.9 now states that `--others` is the exact **complement** of `ls-files` and therefore a tracked-ness filter too, that **neither alone is a presence fact**, and mandates a **scoped directory listing** or the **explicit union** via `git -C <worktree>`. The "untracked BY CONSTRUCTION" premise is **retired and quoted as refuted**, with the counter-example named (`commit-plan` exists to commit pre-landing, the operator invoked it, and `draft_present` would have been wrong in *both* directions depending on nothing but whether someone had committed). | `main-session` | `resolved` |
| C2 — SC10b cannot discriminate C1 | medium | **Accepted.** SC10b's fixture now requires **both a tracked and an untracked** draft inside the gitignored worktree, with both halves' purpose stated inline: the cwd pin defeats a `git -C <worktree>` shortcut, and the tracked draft defeats an `--others`-only implementation. | `main-session` | `resolved` |
| C3 — the positive-control claim overreaches | medium | **Accepted in full, and the criticism is the correct one to make of this bundle.** Two defects, both fixed: the note had also landed on **RE-001** rather than RE-002 via a mis-targeted edit, and is now moved with that recorded. The claim is rescoped to a positive control **on the BEHAVIOUR, explicitly not on the artifact** — stating that `ESC-001.answer` is free text written by this session, structurally the same artifact class as #293's close reason; that nothing distinguishes the operator answering from the session writing the answer; that `asked_of` is empty and `push_batch` unverifiable. *"Claiming the contrast is exact was the one self-favourable unfalsifiable claim in a bundle whose thesis is that such claims are the defect."* `asked_of` now says so rather than being blank. | `main-session` | `resolved` |
| C4 — a resolution recorded as landed that did not | low-medium | **Accepted, and this is #250's class in this plan's own review record.** The edit silently no-opped on an unmatched string and was recorded as done. The pointer is now applied and **verified present**, carries a note that it was missed once, and pass-5's C4 cell is corrected to say so. The proximate cause is recorded too: the edit used an unguarded `replace()`; every edit in this round is assert-guarded, and the assert caught a second mis-targeted string immediately. | `main-session` | `resolved` |
| C5 — four figures false, one fixture gone | low | **Accepted.** The 37s are marked "AT THE TIME. Now 0"; the "cheapest fixture sitting in the repository" claim is replaced with a statement that the commit destroyed it and SC10b must construct its own. Recorded as R12 / Issue 0.10's class caught live — a derived figure in prose, invalidated by an event three hours later. | `main-session` | `resolved` |
| C6 — REQ-PORT-052 fencing | low | **Accepted.** The verbatim `SKILL.md` quote and all filesystem paths in `plan-retrospective.md` and `escalations.md` are now fenced. | `main-session` | `resolved` |
