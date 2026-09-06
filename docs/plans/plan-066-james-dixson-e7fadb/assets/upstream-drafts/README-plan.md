---
type: Asset
okf_spec: OKF-PLAN
description: "The 13 authorized upstream writes for Issues 8.4/8.5. AUTHORIZED 2026-09-06 but NOT YET POSTED — transitively blocked behind the held Diagram human-read gate."
id: upstream-drafts
plan: plan-066-james-dixson-e7fadb
created: 2026-09-06
---
# Drafted upstream writes — NOT YET POSTED

The *Upstream write authorization* capability gate is **RESOLVED — the operator authorized these
writes on 2026-09-06.** They are nonetheless **NOT YET POSTED**, and the reason is ordering rather
than consent:

> The writes are **transitively blocked** behind the still-held *Diagram human read* gate.
> That gate blocks `8.1`; `8.3` (the retrospective) depends on `8.1`; and `8.4`/`8.5` depend on
> `8.3`. **The reconcile bodies below assert what the plan DID, and `8.3` is what establishes it**
> — posting first would publish claims the verification sweep has not yet confirmed. `SC17` is
> `FALSE` right now precisely because `8.3` has not run.

**No `gh` command has been run.**

## The planned writes

| # | Action | Body | Disposition |
| :-- | :-- | :-- | :-- |
| #317 | comment, then close | `317-comment.md` | include — the plan of record |
| #104 | comment, then close | `104-comment.md` | include |
| #127 | comment, then close | `127-comment.md` | include |
| #363 | comment, then close | `363-comment.md` | include |
| #322 | comment, then close | `322-comment.md` | include |
| #247 | comment only, **leave OPEN** | *(partial — this plan closed the four Class-B coverage gaps #317 enumerates, not all of #247's manifest gap)* | partial |
| #263 | comment only, **leave OPEN** | *(partial — the `optional`/`required` token defect is one instance of the META class; the class stays open)* | partial |
| new | file follow-on | `followon-1-zero-byte-guard.md` | D5 — filed, not fixed |
| new | file follow-on | `followon-2-lifecycle-shorthand.md` | D5 — filed, not fixed |
| new | file follow-on | `followon-3-notchecked-membership.md` | D5 — filed, not fixed |
| **#372** | **comment, then close — LAST** | `372-comment.md` | **tracker** — this plan's own coarse tracker |

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
