---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #205: Close-out is manual and the closable signal is wrong in BOTH directions — make verify-then-close a mechanical step at land-the-plane / tab-teardown / deploy

- **Number:** 205
- **Title:** Close-out is manual and the closable signal is wrong in BOTH directions — make verify-then-close a mechanical step at land-the-plane / tab-teardown / deploy
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Filed at operator direction after a hand sweep of the backlog closed #200, #164 and #153 — three issues that a mechanical close-out step should have surfaced, and that between them expose the whole defect.

## The complaint

Land-the-plane, herdr tab teardown (#204) and `yf self install` are the three points where a plan is *actually finished*. At every one of them, closing the upstream tracking issues and the beads is **still a thing the operator has to ask for by hand**, in a separate turn, after the fact. It should be a step with an exit code.

## What exists today

`upstream.py closable` is the only mechanism, and it is **propose-only by contract** (`REQ-BUP-052`) — it emits `gh issue close` commands and stops. It has already been hardened once in this direction: plan-044 Issue 3.3 (`REQ-BUP-060/064`) annotates each row with the real upstream state and emits no command for a non-OPEN issue, cutting a run from 35 emitted commands / 6 actionable down to 6.

What it is **not** is bound to any of the three trigger points, and what it does not have is a trustworthy signal.

## The signal is wrong in both directions — measured, this week

`closable_candidates()` groups beads by `external_ref` and marks an issue closable when **every mapped bead is closed**. Beads with no `external_ref` are ignored entirely.

**Direction 1 — FALSE NEGATIVE (documented, deliberate, unmitigated).** The docstring is explicit that this is the price of `REQ-BUP-052`'s zero-coupling choice, and `CLOSABLE_CAVEAT` says it out loud:

> Hand-filed coarse plan trackers carry NO bead mapping and are invisible to this signal — a clean run does NOT mean nothing needs closing.

Measured on this repo right now: **1553 beads, 62 mapped, 1491 unmapped.** So the signal sees ~4% of the tracker.

Worked instance: **#164** was fixed by `14fa498` (plan-047) and carried no bead. It stayed open for days after the defect was gone, and was found only because a human read the backlog.

**Direction 2 — FALSE POSITIVE (undocumented, and the dangerous one).** A closed bead is treated as proof the work is done. It is not.

Worked instance: **#153**. Its mapped bead `yf-sklq` was closed while the substance — wiring `PYTHONPYCACHEPREFIX` out of `skills/` — **was never delivered**. `git grep PYTHONPYCACHEPREFIX` outside plan bundles returns two hits, **both comments**. `closable` duly proposed closing it during plan-051's land-the-plane. The proposal was refused **only because a human went and checked**.

That is the part that matters: had close-out been automated on today's signal, #153 would have been closed as `completed` three days ago, and the record would carry a falsehood. **Auto-closing the current signal is strictly worse than the manual sweep it replaces.**

## What is actually being asked for

Not "remove the confirmation" — closing an upstream issue is an outward-facing write and the confirm contract is load-bearing. The ask is that **confirming should be one keystroke rather than a research task**, and that it should happen *at* the trigger rather than in a follow-up conversation three days later.

Three parts:

**(a) Bind it to the triggers.** Make `closable` a declared step at land-the-plane, at herdr tab teardown (#204), and after `yf self install` — with an exit code, not a paragraph an agent may skip. This is the same shape as #197's complaint about formula aspects and #196's about `prevention:` fields: a process rule that nothing executes.

**(b) Fix the false negative by CONSTRUCTION, not by caveat.** plan-051 already demonstrated the fix: its tracker #200 was filed **through** `/yf-beads-upstream`, so it carries bead `yf-mol-3he` and `closable` can see it — the first coarse tracker that was ever visible to the signal. That was a plan-specific achievement (SC12b), not an enforced contract. Make it one: a coarse tracker filed any other way is invisible by construction, and the caveat is the only thing standing between that and a silent miss.

**(c) Fix the false positive — the hard part, and the reason this is not a one-line change.** `bead closed` is a weak proxy for `work done`. A stronger close-out predicate would require the closing bead to name **evidence**: a commit that touched the relevant paths, a green recipe row, a discharged success criterion. That ties directly to #199 (nothing re-checks `plan.md` Success Criteria at completion — a criterion discharged mid-plan rots silently) and #190 (require plans to ship tests for code they write). Absent that, the honest fallback is that a `closable` proposal must **render the evidence** it is proposing on, so the operator confirms against something rather than against an issue number.

## Precedent for the authorization model

Do not invent one. `custom.upstream.auto_hoist_followons` already establishes the shape: **default propose-with-confirm**; a no-prompt path available only behind an explicit config key, and even then restricted to a **narrow, well-typed signal** while the broad signal stays gated. An unattended close should sit behind the same kind of key and the same kind of narrowing — and should be gated on (c) landing, not shipped before it.

## Explicitly NOT proposed

- **No auto-close on the current per-bead signal.** #153 is the counterexample and it is three days old.
- **No closing of issues this repo did not file.**
- **No weakening of `REQ-BUP-052`.** The default stays propose-only; this issue makes the proposal complete and evidence-bearing, and fires it at the right moment.

## Related

#204 (herdr teardown — the sibling gap, and already carries the harvest-before-prune ordering constraint that close-out needs too), #199, #190, #197, #196, #203.

