---
type: Asset
okf_spec: OKF-PLAN
description: "The authorized upstream writes for Issues 8.4/8.5, AMENDED for the partial land: only #104, #127, #363 and #322 close. #317, #247, #263 and the #372 tracker stay OPEN."
id: upstream-drafts
plan: plan-066-james-dixson-e7fadb
created: 2026-09-06
---
# Drafted upstream writes — NOT YET POSTED

The *Upstream write authorization* capability gate is **RESOLVED** — the operator authorized these
writes on 2026-09-06.

**THE DISPOSITIONS WERE AMENDED ON 2026-09-07**, after the operator declined the diagram
human-read gate. The bodies as originally drafted asserted a completion that is **no longer
true**, so four issues that were queued to close now stay open.

## The planned writes — AMENDED

| # | Action | Body | Why |
| :-- | :-- | :-- | :-- |
| #104 | comment + **CLOSE** | `104-comment.md` | scope complete, unaffected by the diagram work |
| #127 | comment + **CLOSE** | `127-comment.md` | scope complete, unaffected by the diagram work |
| #363 | comment + **CLOSE** | `363-comment.md` | scope complete, unaffected by the diagram work |
| #322 | comment + **CLOSE** | `322-comment.md` | scope complete, unaffected by the diagram work |
| **#317** | comment only, **STAYS OPEN** | `317-comment.md` | its own acceptance requires the retrospective, which is gated behind the declined diagram read |
| **#247** | comment only, **STAYS OPEN** | `247-comment.md` | partial — four Class-B gaps closed, not the whole manifest gap |
| **#263** | comment only, **STAYS OPEN** | `263-comment.md` | partial — one instance closed, not the META class |
| new | file follow-on | `followon-1-zero-byte-guard.md` | D5 — filed, not fixed |
| new | file follow-on | `followon-2-lifecycle-shorthand.md` | D5 — filed, not fixed |
| new | file follow-on | `followon-3-notchecked-membership.md` | D5 — filed, not fixed |
| **#372** | comment only, **STAYS OPEN** — post LAST | `372-comment.md` | the plan is not complete; do not close its tracker |

**Four closes, seven comment-only.** The rule applied throughout: **do not close a partial, and do
not close anything whose acceptance depends on work that has not happened.**

## What no body may claim

**No body asserts the diagrams are finished.** Each says what is true and separable: they are
**factually correct and mechanically checked** — counts, group membership, harness paths and
backend claims verified against their sources, all six re-rendered byte-identically under a pinned
`d2 v0.8.2` — **and** a redesign is pending in a follow-on plan (layered marketecture, per-skill
and per-formula diagrams, combined phase/lifecycle and install/tune matrices, plus a
`DRIFT-CHECK.md` amendment making **omissions** FAIL).

Correct-but-not-final is the honest description, and collapsing it in either direction would be a
false claim.

## The command form, and why it is not negotiable

Every body is composed with `--body-file -` fed by a **quoted** heredoc — for example
`gh issue comment 317 --body-file - <<'MARKER'`, the body, then `MARKER`.

Issue bodies here are markdown full of backticks and backslashes. A single-quoted `--body` passes
backslashes through literally, and an unquoted one lets the shell expand `` ` `` and `$`. The
quoted-heredoc form is the only one that survives both.

**Verify by reading the body back** (`gh issue view N --comments`), never by trusting exit 0.

## Routing

`gh issue create` / `comment` / `close` are outward-facing. The push of open/deferred beads routes
through `/yf-beads-upstream` rather than being hand-run, so enumeration, the create-vs-update
decision, the label policy and the `external_ref` recording all happen. A raw `gh issue create`
looks harmless but **records no `external_ref`**, leaving an issue nothing can map back to a bead.

This repository's granularity is **coarse**: one tracking issue per plan-scale effort, not one per
execution bead.

## #372 goes LAST, and it was MISSING from this table

**#372 is this plan's own coarse tracker, and an earlier revision of this file omitted it** — the
operator caught it by reading the table and noticing an absent row. A coarse tracker left open
after completion is the documented failure mode in this repository: **five** have gone stale and
been closed by hand (#103, #95, #96, #98, #134).

It is sequenced **last**, after every other write has landed *and been read back*, so its
completion comment cannot claim a reconcile that did not happen.

**Why the omission was possible at all, and it is not carelessness alone.** `stamp-tracker` runs
at pour to record the tracker URL as the epic's `external_ref`, which is what makes a tracker
visible to `upstream.py closable`. On this plan it returned:

```
skipped — no coarse tracker found in plan.md Upstream Issues (no row with disposition `tracker`)
```

This plan's Upstream Issues table carries no `tracker`-disposition row, so #372 was never stamped
and is invisible to `closable` — which reports per-bead via `external_ref` and therefore cannot
see a hand-filed tracker at all. That is exactly the caveat the `yf-beads-upstream` page now
documents: *a clean `closable` run does not mean nothing needs closing.* The stamp is repaired
locally as part of Issue 8.5 (`bd update --external-ref`, a local bead write, not an upstream
one).
