---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #183: plan-049-james-dixson-725bc0 execution tracking

- **Number:** 183
- **Title:** plan-049-james-dixson-725bc0 execution tracking
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium

## Body


Coarse tracking issue for `plan-049-james-dixson-725bc0` — *Rewrite the historical plan corpus
so the constructs plan-048 refuses become readable, and bind the document linter at the two
enforcement points that were never wired.*

- **Plan folder:** `docs/plans/plan-049-james-dixson-725bc0/`
- **Epic:** `yf-mol-dlr`
- **Landed:** merged to `main`; FULL validation over the merged tree passed with 44 commands.

## What shipped

| Epic | Delivered |
| :-- | :-- |
| 0 | SPEC-first: `REQ-DATA-051`–`053`. `plan-relations` promotion-off was **declared in three documents and implemented in none** — now a `promote = false` schema key, bypassing `STATUS_SEVERITY` in both directions |
| 1 | `_shared/dag_guard.py` — the four-layer postcondition (L1 issues, L2 edges, **L3 raw referent tokens**, L4 gate content) under set/multiset containment, counts explicitly forbidden |
| 2 | The dark-matter grammar widening: **74 declarations, +100 edges, 0 documents modified** |
| 3 | `cell-non-empty` + `gate-completeness` (`REQ-DATA-054/055`), then the authorized 2-document corpus write |
| 4 | The enforcement binding: vendor + intake gate + on-edit rule (`REQ-DATA-056/057/058`) |
| 5 | #135 scoped: `--exclude` and the in-flight literal rule (`REQ-DATA-059/060`) |

## The result that mattered most

plan-048's declared safety postcondition was implemented **exactly as worded** and driven with
the harm it was written for — 23 emptied `depends-on:` declarations. It measured **PASS, exit
0**, with edges *up* two and residue *down* 22, so the destruction read as an improvement on
both instruments. A refused declaration contributes no edge, so emptying it destroys nothing any
parsed view ever saw. Its replacement is gated on **failing** that mutant, and the failing
implementation is pinned as a test.

## Recorded adverse outcomes

- **A declared target was missed.** Corpus `unparsed[]` is **75** against ≤73, and was **83**
  against ≤81 after the widening. The whole +2 is two `plan-010` declarations that were
  previously invisible and are now visible-and-refused; hitting the target required silently
  dropping them. The target was misderived at approval in exactly the way this plan's own
  Approach warns about.
- **The original scope was redirected twice by its own investigation** — the "16 free
  recoveries" re-measured as 7, and the primary safety control was measured passing its own
  motivating harm.
- **Three fail-louds fired during merged-state validation**, each a real consequence: an
  unclassified protocol rule, an intake binding that was re-judging history, and a README
  enumeration guard.

## Upstream dispositions

| Issue | Disposition |
| :-- | :-- |
| [#135](https://github.com/dixson3/yoshiko-flow/issues/135) | `include` — closed by this plan |
| [#140](https://github.com/dixson3/yoshiko-flow/issues/140) | `partial` — readability half only; the rest is #171 |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | `partial` — M5 closed, M9 explicitly out of scope with its measurement |
| [#113](https://github.com/dixson3/yoshiko-flow/issues/113) | `partial` — residue drops; the walk stays out of scope |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | `partial` — the binding closes more of the class; the falsification pass stays open |
| [#171](https://github.com/dixson3/yoshiko-flow/issues/171) | `deferred` |
| [#102](https://github.com/dixson3/yoshiko-flow/issues/102), [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | `exclude` |
