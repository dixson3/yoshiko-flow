---
type: Asset
okf_spec: OKF-PLAN
description: "Drafted upstream bodies for Issues 8.4/8.5, awaiting operator confirmation. NOTHING HAS BEEN POSTED — the Upstream write authorization gate is unresolved."
id: upstream-drafts
plan: plan-066-james-dixson-e7fadb
created: 2026-09-06
---
# Drafted upstream writes — NOT YET POSTED

The *Upstream write authorization* capability gate (`gate_type: human`, `test_class: consent`) is
**unresolved**. Every body below is a draft; **no `gh` command has been run**.

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
