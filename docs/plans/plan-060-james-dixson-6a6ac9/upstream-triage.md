---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: plan-landing capability: land verb + lander agent

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #305 — gate_consistency.py: on the INCONCLUSIVE path --json is not honoured at all (plain text on stderr, empty stdout), and a caller error is indistinguishable from an absent plan
Labels: priority::medium, type::bug
> Two defects in one invocation, found while running the conformance pass for **plan-060**. Surfaced
by the observer session; reproduced and extended here.

Both are instances of [#263](https://github.c...

**Disposition:** exclude
**Notes:** Found by this plan's conformance pass and filed for follow-up, but `gate_consistency.py`'s stream and classification defects are not landing behaviour. plan-060 consumes the instrument and does not modify it. Recorded here so the provenance is not lost.

## #304 — The self-authorization residue #301 does not close: the lander cannot forge the ARTIFACT, but the main session still causes the ACT
Labels: type::bug, priority::high
> Filed by **plan-060** (the `land` verb) from EXP-005, so that
[#301](https://github.com/dixson3/yoshiko-flow/issues/301) is not closed claiming a fix it does not
deliver. This is the same **collapsed-...

**Disposition:** partial
**Notes:** Filed BY this plan from EXP-005, so #301 cannot close claiming a fix it does not deliver. plan-060 ships three honestly-labelled mitigations — withhold the verb from the session, a pure-POSIX controlling-terminal gate, a route record. The off-machine lever (GitHub branch protection) stays open.

## #303 — yf-plan §6.4: CHANGED is structurally EMPTY post-merge — classify-deliverable's 'path-backed' evidence is unreachable at the one binding documented to produce it
Labels: priority::medium, type::bug
> ## The defect

`skills/yf-plan/SKILL.md:1662` computes the merged-tree changed paths for the §6.4 reconcile-time
deliverable-class re-confirm as:

```bash
CHANGED=$(git diff --name-only "${MERGE_TARGE...

**Disposition:** partial
**Notes:** Found by this plan's EXP-004 spike. `land` computes `HEAD^1..HEAD` internally, and Issue 5.4 fixes the SKILL.md prose for the hand-run path. This plan also found that its OWN first attempt to verify the fix used a grep pattern that could never match — recorded on the issue.

## #302 — yf-plan: plan-folder location and plan NUMBER are both unenforced claims — 'stays primary-side' is false in a worktree, and get_next_index() is count-based so numbers collide across checkouts
Labels: type::bug, priority::high
> Two measured defects in the same layer — **plan-folder identity and location** — found by observation
of plan-060's own drafting worktree. Both are instances of the class
[#301](https://github.com/dix...

**Disposition:** partial
**Notes:** Only **B3** — landing-time collision detection — is in scope. A spike measured that two `plan-NNN-*` bundles differing only by hash suffix merge CLEANLY, exit 0, no conflict, no failing check. The counter fix (B1/B2) and the primary-side claim (A) stay open.

## #301 — yf-plan: the close chain stops at 'complete' — merge-back, pruning, reconcile writes, bead mirroring and redeploy are all manual
Labels: type::feature, priority::high
> ## The close chain ends at `update-status complete`. Everything after it is manual.

`test_close_contract.py --list-steps` enumerates **12** steps — `audit-close`, `retrospective-report`, `judgement-n...

**Disposition:** include
**Notes:** The plan of record. Delivers the three-layer split. NOTE: this plan deliberately DEVIATES from the issue's six-step order — EXP-004 measured that steps 1-3 are not sequential, that its ordering constraint contradicts REQ-COMPLETE-001, that putting the FULL tier at step 4 leaves a red tier with nothing to fail closed onto, and that a conflict at its merge step is unrecoverable. Closed **as amended**, not as written (Issue 4.4).

## #295 — plan-057 follow-on: 8 unresolved backfill halts (SC19) and 4 ungranted reconcile comments (SC24)
Labels: type::task, priority::medium
> ## Deferred from plan-057: two criteria left FALSE by operator decision

plan-057 is `status: complete` at 28 of 30 criteria. The two outstanding are **not defects** — each needs an operator judgement...

**Disposition:** exclude
**Notes:** plan-057's residue is the MOTIVATING EVIDENCE for this plan, not work it performs.

## #293 — A Type: human consent gate can be closed by the executor asserting its own authorization
Labels: type::bug, priority::high
> ## A consent gate can be closed by the executor writing its own authorization

`Type: human` capability gates exist to spend operator attention before an irreversible or destructive act. Measured duri...

**Disposition:** partial
**Notes:** Structural answer for the LANDING case only. EXP-005 measured that this eliminates #293's specific ARTIFACT (a free-text close reason) but not the ACT; the general `Type: human` gate mechanism is out of scope and stays open.

## #287 — INVESTIGATION: bead/issue state drift is one-directional in reporting — 17 issues are CLOSED upstream with beads still open, and nothing surfaces it

> > **This is an investigation, not a bug report.** The observation is measured; whether it represents
> a problem, and which direction is authoritative, are open questions. Noticed while dogfooding
> `...

**Disposition:** exclude
**Notes:** Four live readings, two of them 'do nothing'. `land` must not encode a guess.

## #280 — yf-beads-upstream: detect_followons' `narrow` auto-eligible set has been permanently empty since it was written

> `detect_followons` in `skills/yf-beads-upstream/scripts/upstream.py` resolves a dependency
edge's target as:

```python
d.get("depends_on_id") or d.get("target") or d.get("to")
```

But its `deps_for`...

**Disposition:** exclude
**Notes:** A `yf-beads-upstream` defect. NOTE: its deferral is NOT neutral for L17 — Issue 4.7 makes residual mirroring propose-only unless the batched grant covers it, and R10 carries the risk.

## #276 — yf-plan: the portability audit checks files on DISK, not git-TRACKED-ness — a gitignored evidence file passes the audit and is invisible to a cold reader

> > Found during plan-058's intake. The plan's first commit **silently dropped two evidence
> transcripts** and the portability audit passed anyway.

## The defect

`plan_manager.py audit` verifies that...

**Disposition:** exclude
**Notes:** Adjacent — L18's prune precondition asserts `origin` tracked-ness — but the audit itself is untouched.

## #270 — yf-plan: plan-review.formula.toml has NEVER been poured — the only structural mid-burn review gate in yf has not fired in 27 review passes

> > Found by the `yf-judgement` design investigation (EXP-001, plan-059), while surveying yf for a
> trigger point that fires reliably. Verified independently before filing.

## The defect

`skills/yf-p...

**Disposition:** exclude
**Notes:** Unrelated to landing.

## #266 — CRITICAL: the plan.md Gates grammar cannot express test_class or cwd, so every capability gate defaults to a class that is never run
Labels: type::bug, priority::critical
> Plan: plan-056-james-dixson-473dba | Bundle: docs/plans/plan-056-james-dixson-473dba (repo-relative)

A capability gate declared in `plan.md` cannot say which class it belongs to, and the default is t...

**Disposition:** exclude
**Notes:** `land` reads gate STATE, not gate grammar.

## #263 — META: 'two facts, one signal' is one architectural gap with 11+ instances — investigate the class before fixing another instance
Labels: type::bug, priority::high
> ## The class

**A signal that can mean two different things, reported through a channel that cannot express the
difference — and where the more permissive consumer is the one that says "clean".**

Thi...

**Disposition:** partial
**Notes:** Applied, not fixed: every `land` verdict is three-valued and no refusal is reported at exit 0. Issue 0.9 additionally records where this plan's OWN criteria layer collapses INCONCLUSIVE — `recheck-criteria`'s binary clause grammar — rather than leaving it unremarked. Issue 1.9 adds a third instance: an enumeration that reports 0 where the answer is 37 is the same two-facts-one-signal shape. The class-wide investigation stays open.

## #255 — Cut the v0.5.0 release: push the tag (deferred from plan-054, everything else staged and green)

> **The tag push is the only remaining work.** plan-054 completed everything else and deliberately
descoped Issue 6.8 so the operator could verify the harnesses manually under a real `HOME`
before an ir...

**Disposition:** exclude
**Notes:** Release-cut mechanics, unrelated.

## #235 — yf-beads-hygiene reconcile: linked_plan_complete cannot distinguish DELIVERED work from a deliberately-parked ONGOING obligation — proposes closing the very issues filed to outlive the plan
Labels: priority::medium
> Found in `dixson3/rc-files` running `/yf-beads-hygiene` immediately after plan-004 completed. Reported by operator decision. Sibling of #234 (same session, different layer).

## What reconcile propose...

**Disposition:** exclude
**Notes:** `yf-beads-hygiene` engine, a different surface.

## #230 — bd close REFUSES and EXITS 0 when the bead is blocked by an open dependency
Labels: bug, priority::high
> Found by plan-053 during its own execution. **This is the defect class plan-053 exists to
close, occurring in the tool plan-053 is tracked with.**

## The defect

`bd close <id>` on a bead with an ope...

**Disposition:** partial
**Notes:** Caller-side only: close-out verifies every close STRUCTURALLY by read-back and never branches on `bd close`'s exit code. The `bd` fix is upstream.

## #222 — yf-plan: the phase model has no slot for post-merge/post-teardown work, yet 6.2 teardown predictably invalidates worktree-rooted artifacts
Labels: priority::medium
> Filed by operator decision from the **plan-004** session in `dixson3/rc-files` (CLIProxyAPI local model gateway). Three instances, one root cause, all measured on a live machine.

## The class

**A be...

**Disposition:** partial
**Notes:** `land` steps L16-L19 are the first genuine post-merge slot, the structural gap #222 names. Authoring-time guidance toward out-of-tree deferred beads is NOT in scope.

## #204 — yf-herdr: no teardown contract — a completed plan's subordinate tab is never closed, and only harvest-before-prune makes closing safe

> Filed by operator decision from the **plan-051** session. Related: #198 (the harvest→prune hazard, same ordering constraint), #203 (structural verification of an operation's result).

## The gap, meas...

**Disposition:** partial
**Notes:** Step L18 implements harvest-before-prune mechanically and, because tab provenance is **unanswerable** (D-7), PROPOSES the close by default; an actual close needs an explicitly supplied tab id and is verified by reading back the agent list. The `REQ-HERDR-*` teardown contract is a yf-herdr deliverable.
