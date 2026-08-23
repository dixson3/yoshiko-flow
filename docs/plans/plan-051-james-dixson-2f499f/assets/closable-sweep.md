---
type: Reference
okf_spec: OKF-PLAN
id: closable-sweep
description: Propose-only closable sweep at land-the-plane — nothing was closed
---

# `closable` sweep — PROPOSE-ONLY

`upstream.py closable` reports which upstream issues have all their mapped beads closed. It
**proposes** and never closes: closing an upstream issue is outward-facing and needs the same
authorization a push does.

## plan-051's own tracker

```
[not-actionable] https://github.com/dixson3/yoshiko-flow/issues/200  [OPEN]  (still open: yf-mol-3he)
```

This line is **SC12b's second clause discharged**: `closable` can *see* #200 at all. A tracker
filed with a bare `gh issue create` records no `external_ref` and is structurally invisible to
this signal — which is how five earlier trackers went stale. #200 is an ordinary mapped bead, and
it is correctly `not-actionable` because its molecule is still open at the time of the sweep.

## Proposed elsewhere — adjudicated AT SOURCE, and one proposal was WRONG

The sweep proposed closing three issues that are not plan-051's. Each was investigated **at
source** rather than accepted on the per-bead signal. **Two were correct; one was not.**

| Issue | `closable` said | Verdict | Basis |
| :-- | :-- | :-- | :-- |
| [#176](https://github.com/dixson3/yoshiko-flow/issues/176) | closable | **CLOSE — correct** | plan-048's `plan.md` is `status: complete` and its tracker bead `yf-mol-541` is closed. Same class as #193 |
| [#152](https://github.com/dixson3/yoshiko-flow/issues/152) | closable | **CLOSE — correct** | the substance shipped: `yf/profiles/claude-code.json` declares both `disableWorkflows` and `todoFeatureEnabled` as managed paths, applied by `yf harness` under the consent gate |
| [#153](https://github.com/dixson3/yoshiko-flow/issues/153) | closable | **DO NOT CLOSE — the signal is WRONG** | **not wired.** See below |

### #153 — a closed bead standing in for undelivered substance

**This is the exact hazard the propose-only contract exists for**, caught in the wild.

Measured repo-wide (bundles excluded, since they are records rather than surfaces):

```bash
git grep -n PYTHONPYCACHEPREFIX -- ':!docs/plans' ':!docs/research'
```

returns **exactly two hits, and both are PROSE**:

| Hit | Kind |
| :-- | :-- |
| `yf/build.rs:91` | a `//` comment |
| `yf/tests/embed_watch_drift.rs:105` | text inside a test's assertion message |

**Nothing sets the variable.** There is no `.cargo/config.toml`, no `cargo:rustc-env` emission,
and no shell export anywhere in the tree.

`build.rs:91` sits under a heading that says so itself — *"KNOWN COSTS, documented rather than
over-promised"* — and describes the tax as *"fully eliminable from the other side"*. The measured
cost is **5.23 s where a 0.20 s no-op is expected**, and it is **still being paid**.

So the bead that closed **documented the cost**; the issue's substance is the **wiring**, which
does not exist. Closing #153 on the bead signal would have marked delivered a thing nobody built.

### Why this is a class, not a one-off

Named here rather than filed as an isolated curiosity, because two open issues describe the same
defect from other angles:

- **[#199](https://github.com/dixson3/yoshiko-flow/issues/199)** — nothing re-checks criteria at
  completion. plan-051 hit this itself: `SC4b` was green when discharged and false two epics later
  (`RE-003`).
- **[#173](https://github.com/dixson3/yoshiko-flow/issues/173)** — criteria and dispositions are
  never checked against the engine that enforces them.

**#153 is that same class seen from the `closable` side:** a bead's *closure* is being read as
evidence about the *world*, and no mechanism re-tests the world at the moment the claim is made.
The per-bead signal is a claim about bookkeeping, not about delivery.

**No comment was posted on #153.** That write was not authorized; this bundle record is the
record.

## The stated blind spot, carried verbatim

> Hand-filed coarse plan trackers carry NO bead mapping and are invisible to this signal — a
> clean run does NOT mean nothing needs closing.

So this sweep is a lower bound on what needs closing, never a clearance.
