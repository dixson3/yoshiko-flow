---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #392 - META: ''declared in prose, acted on by code''
  — one class behind #388, #389, #266, #387 and yf-z6xt; the remedy is DERIVED-not-transcribed
  plus negative controls'
---
# Upstream #392: META: 'declared in prose, acted on by code' — one class behind #388, #389, #266, #387 and yf-z6xt; the remedy is DERIVED-not-transcribed plus negative controls

- **Number:** 392
- **Title:** META: 'declared in prose, acted on by code' — one class behind #388, #389, #266, #387 and yf-z6xt; the remedy is DERIVED-not-transcribed plus negative controls
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

**Thesis:** a large share of this repo's recurring defects sit at one seam — **a fact declared in
prose, acted on by code that never reads that prose.** The two halves drift, and nothing executes
to notice.

This is a companion to #263 (*"two facts, one signal"*), not a duplicate. #263 is about a **signal
that cannot distinguish two states**. This is about a **declaration and its enforcement living in
different media**. They overlap — a prose declaration with no enforcement often *presents* as a
green signal — but the remedies differ: #263 wants a richer signal, this wants the declaration and
the action to share a source.

## Instances, all measured

| # | Declared in prose | Acted on by | Result |
| :-- | :-- | :-- | :-- |
| #388 | `plan.md`: `### Reconcile Gate / - Type: auto` | a `SKILL.md` snippet an agent transcribes, which writes **no metadata** | gate treated as `human`; §6.4 deadlocks **after** the push |
| #388 | `SKILL.md` §5.2a: *"carry `gate_type`… as metadata fields"* | `SKILL.md`'s **own** reconcile-gate snippet, 60 lines later | the document contradicts itself; nothing executes to catch it |
| #389 | commit subject: `do NOT close #349/#353` | GitHub's keyword scanner, which reads `close #349` and ignores negation | a `partial` disposition silently inverted; issue closed on push |
| #266 (P0) | `plan.md` Gates grammar | `plan_extract.py`, whose regex has no `test_class`/`cwd` | every capability gate defaults to a class the sweep never runs |
| #387 | `yf-herdr` `SKILL.md:69`: `herdr agent list --json` | `herdr`, which accepts **no options** on that subcommand | agent-kind resolution silently yields empty |
| `yf-z6xt` | review files written `**Verdict: X**` | `doc_lint` **accepts** it; `ready-check` **rejects** it | a review passes the audit and is malformed to the gate |
| — | `plan.md` Success Criteria Verification cells, written as prose | `recheck-criteria`, which parses a clause grammar | **0 of 16** criteria evaluated; verdict INCONCLUSIVE → `warn`; the completion gate contributed nothing |
| — | `SKILL.md` §6.4's close chain, as an ordered prose list | `_land_l8_to_l15_close_chain`, a separate implementation | two enumerations of one sequence, free to drift |

## The refinement that matters: DERIVED, not merely SCRIPTED

Moving a declaration into a script is **not** the fix by itself. plan-068's red-team found the same
hand-written helper list short in **three consecutive passes** (3 members missing, then 3 more).
Putting that list in a Python constant would have changed nothing — it is the same transcription in
a new medium.

What actually fixed it: **computing the set by AST call-graph closure from its real source**, landing
it as `LAND_CTXLESS_HELPERS`, and adding a test that pins the constant to the SPEC text so the two
cannot drift. Same for `stubbed_steps`, which named three labels while hiding five L-numbers — the
fix was deriving it from `LAND_EXECUTOR`.

> **At a transition point, compute the thing from its source. Never restate it.**
> A script that restates a declaration is prose with better syntax.

## The failure mode this must not become

Mechanical checks go vacuous quietly, and this repo has measured instances:

- **#334's test passed against a stub that ignored `allow_list` entirely.** The fallback added to
  make the test runnable is exactly what made it measure nothing.
- **`recheck-criteria` evaluated 0 of 16** and returned a non-halting warn — a gate that cannot
  distinguish *"passed"* from *"never ran"*.
- **`doc_lint` and `ready-check` disagree** about a format rule (`yf-z6xt`) — two mechanical checks,
  still drifting, because neither derives from the other.

So: **every mechanical check added under this issue needs a negative control** — a fixture that
must make it fail. plan-068's AST check shipped with four, which is the standard to hold.

## Why the prose-only review path cannot close this class

plan-068 ran six red-team cycles. Passes 1–3 were prose-only and returned 14, 14 and 9 concerns.
Passes 4 and 5 ran code, and **every defect they found had been read past by all three earlier
passes** — including a requirement that would have been false the moment it landed, a sandbox
escape that would have run `git branch -d` in the real checkout, and a SPEC-first ordering check
that was green by construction at the point it is evaluated.

Pass 4 stated the conclusion directly: a further *reading* pass had **negative value**. That is the
strongest available evidence that this class is not reachable by more review — only by execution.

## Proposed organizing use

Rather than a single fix, use this as a **backlog lens**. For each candidate defect, ask: *is a fact
declared in one medium and enforced in another?* If yes, the durable remedy is to make the enforcing
code read the declaration — or to generate the declaration from the code — plus a negative control.

Known members today: #388, #389, #266, #387, `yf-z6xt`, the criteria-grammar gap, and the §6.4
double-enumeration. #390 records two authoring-side instances of the same root (an inference
recorded as a measurement; pipeline-masked exit codes).

Raised after landing plan-068 (#386), where the class produced two landing-blocking defects within
minutes of each other.

