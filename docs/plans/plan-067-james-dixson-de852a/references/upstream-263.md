---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #263 - META: ''two facts, one signal'' is one architectural
  gap with 11+ instances — investigate the class before fixing another instance'
---
# Upstream #263: META: 'two facts, one signal' is one architectural gap with 11+ instances — investigate the class before fixing another instance

- **Number:** 263
- **Title:** META: 'two facts, one signal' is one architectural gap with 11+ instances — investigate the class before fixing another instance
- **URL:** 
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

## The class

**A signal that can mean two different things, reported through a channel that cannot express the
difference — and where the more permissive consumer is the one that says "clean".**

This is not a bug. It is one architectural gap with, at time of filing, **at least eleven open or
closed instances** across `yf`, `yf-plan`, `yf-change-validation`, `yf-beads-*` and `bd` itself.
Each has been found the same way — a human noticing that something reported success while nothing
happened — and each has been fixed in isolation. **The isolated fixes are why it keeps recurring:
nothing in this repo names the class, so every new consumer of every artifact re-invents the
conflation.**

## Instances

### Closed — fixed one at a time, no shared remedy

| # | The two facts collapsed | Reported as |
| :-- | :-- | :-- |
| [#181](https://github.com/dixson3/yoshiko-flow/issues/181) | `not-selected` vs `no-such-path` | a silent green |
| [#207](https://github.com/dixson3/yoshiko-flow/issues/207) | pointer *recorded* vs pointer *live* (`found: true` on a burned epic) | permanently unexecutable |
| [#208](https://github.com/dixson3/yoshiko-flow/issues/208) | valid status vs out-of-vocabulary status | accepted silently |
| [#186](https://github.com/dixson3/yoshiko-flow/issues/186) / [#187](https://github.com/dixson3/yoshiko-flow/issues/187) | present-but-masked vs absent | emitted as absent |

### Open

| # | The two facts collapsed | Reported as |
| :-- | :-- | :-- |
| [#256](https://github.com/dixson3/yoshiko-flow/issues/256) | harness `absent` vs `not-authenticated` vs `consent-pending` | all exit 2, or exit 1 |
| [#259](https://github.com/dixson3/yoshiko-flow/issues/259) | verdict-line grammar: `doc_lint` accepts what `ready-check` rejects | audit passes, gate refuses |
| [#262](https://github.com/dixson3/yoshiko-flow/issues/262) | `INCONCLUSIVE` vs `FAIL` | any nonzero → `fail` |
| [#230](https://github.com/dixson3/yoshiko-flow/issues/230) | closed vs **refused-because-blocked** | exit 0 |
| [#212](https://github.com/dixson3/yoshiko-flow/issues/212) | a gate step vs a plain task | poured as a task, no diagnostic |
| [#211](https://github.com/dixson3/yoshiko-flow/issues/211) | substituted vs **substituted nothing** | exit 0 |
| [#202](https://github.com/dixson3/yoshiko-flow/issues/202) | burned vs **cancelled** | exit 0 |
| [#235](https://github.com/dixson3/yoshiko-flow/issues/235) | delivered vs **deliberately parked** | `linked_plan_complete` |
| [#166](https://github.com/dixson3/yoshiko-flow/issues/166) | no ready work vs **whole categories excluded** | an empty `bd ready` |
| [#224](https://github.com/dixson3/yoshiko-flow/issues/224) | criterion holds vs **criterion cannot fail** (`grep -qv` under ugrep) | green |
| [#165](https://github.com/dixson3/yoshiko-flow/issues/165) | executed vs **prose shaped like a command** | a green FULL tier |

## Why isolated fixes have not worked

Measured across the corpus, the class has three recurring shapes:

1. **Two parsers, one artifact.** #259 is the clearest: `doc_lint`'s regex and `ready-check`'s
   parser are maintained independently, so a review file can be *valid to the auditor and malformed
   to the gate*. Twelve plans currently carry a last-review the gate cannot read, two of them
   holding `APPROVE` verdicts.
2. **A two-valued channel carrying a three-valued fact.** `0/1` cannot express "could not run".
   #262, #230, #211, #202 are all this. Where an `INCONCLUSIVE` exists (#262) a boundary crossing
   destroys it.
3. **Absence read as a positive fact.** #181, #235, #166 and plan-055's own `undetermined`-vs-`foreign`
   design decision are all "I found nothing" being reported as "there is nothing".

## The remedy this issue proposes

Not eleven fixes. **One rule, one helper, one check.**

- **A rule on the always-loaded surface** stating the invariant plainly: *a signal that can mean two
  things must distinguish them; an exit code that cannot carry the distinction must not be the only
  channel; and "found nothing" must never be emitted as "there is nothing".*
- **A shared three-valued vocabulary** — `PASS | FAIL | INCONCLUSIVE` already exists in
  `REQ-DATA-024` and in the plan-054 check family's `0/1/2` contract. It is *not* used consistently,
  and where it is used it is destroyed at boundaries (#262). Make it the default shape for any check
  this repo ships, and make a boundary that cannot carry it a declared defect rather than an
  accident.
- **A grammar shared by construction, not by convention.** Where two consumers parse one artifact,
  the pattern must come from a single shared constant. #259 exists purely because two regexes are
  maintained in two files.

## What this issue asks of the linked issues

Each instance above is left **open on its own merits** — this is not a request to close them. It
asks that **the class be investigated first, and each instance be fixed as an application of the
shared remedy rather than in isolation.** A fix that adds a twelfth bespoke distinction is a fix
that guarantees a thirteenth instance.

## Provenance

Assembled during plan-055's land-the-plane review of 80 open issues. plan-055 itself hit the class
three times while *being written*: ten success criteria that could not fail (`cargo test` with a
zero-match filter exits 0); a resolution recorded as done and never written to `plan.md`, twice
([#250](https://github.com/dixson3/yoshiko-flow/issues/250)); and a migration that reported exit 0
while migrating nothing, caught only because a human ran it. The plan's own remedy —
a fourth `undetermined` outcome distinct from `foreign` — is the shape this issue proposes
generalising.
