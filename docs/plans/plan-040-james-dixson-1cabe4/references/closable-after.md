---
type: Reference
okf_spec: OKF-PLAN
---
# `closable` after the N+1 fix — live evidence

Produced by **plan-040 Issue 4.2**. Evidence for **SC8** (completes, cannot silently regress) and
**SC16** (names which copy of the skill produced the run).

## Which copy produced this run (SC16)

**The repo copy**, `skills/yf-beads-upstream/scripts/upstream.py` — invoked by explicit path, not
via the installed skill.

This is load-bearing, not bookkeeping. `context.md` flags that **this repo is both the source and
a consumer of its own skills**, and the two artifacts were confirmed divergent at measurement time:

```console
$ diff -q skills/yf-beads-upstream/scripts/upstream.py \
          ~/.claude/skills/yf-beads-upstream/scripts/upstream.py
Files … differ          # repo carries the fix; the installed copy does not
```

So a run made through `~/.claude/skills/` at this moment would have exercised the **old, N+1**
code and produced the four-minute hang, not the numbers below. The installed copy catches up only
after the AGENTS.md land-the-plane sync (`touch yf/src/embed.rs` → `yf self install --from-build
--build` → `yf skills install` → `yf harness tune`), which has **not** run at the time of this
measurement.

## Environment

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-16 -->

- `bd` 1.1.2 (Homebrew), `uv` 0.12.3, Python 3.14.2
- Repo `dixson3/yoshiko-flow` at `6987834` (plan-040 execute branch, pre-merge)
- Universe: **1019** beads, of which **21** carry a non-empty `external_ref`

The universe has grown since plan time (991 → 1019) because plan-040's own DAG was poured into it.
The ratio that matters is unchanged: ~2% of beads are mapped, so the old code spent ~98% of its
subprocesses discovering `None`.

## Before (EXP-002, measured at plan time)

| | |
| :-- | :-- |
| Result | **zero output in 4 minutes, killed** |
| Cause | 991 sequential `bd show` subprocesses, one per bead, via `external_for` |
| Operator experience | indistinguishable from a hang |

## After

```console
$ time uv run skills/yf-beads-upstream/scripts/upstream.py closable
…
19 mapped upstream issue(s); 7 closable:
…
real 1.20s        # first run, human output

$ for i in 1 2 3; do /usr/bin/time -p uv run … closable --json >/dev/null; done
real 0.81
real 0.73
real 0.75
```

**~0.8 s steady-state, against >240 s killed.** The remaining time is process startup and the two
`bd` subprocesses, not per-bead work.

`closable` now produces a usable proposal — 19 mapped issues, 7 closable:

```
gh issue close 11
gh issue close 12
gh issue close 139
gh issue close 17
gh issue close 19
gh issue close 27
gh issue close 28
```

Propose-only, as REQ-BUP-052 requires — nothing was closed.

## Why the regression test asserts an invariant, not this number

The timings above are **evidence that the fix works**, not the regression guard. A wall-clock
threshold would pass on a small DB and rot as the DB grows — the exact shape of the original
defect, which was invisible until the universe reached ~991 beads.

The guard (Issue 4.2, `test_upstream.py`) therefore asserts a **scale-independent invariant**:
exactly **one** `bd list`, **zero** per-bead `bd show`, plus a second test running universes of 10
and 1000 and asserting the bd-call count is *identical*.

The bound is on `bd list`/`bd show` specifically — **not** on total `bd` invocations.
`upstream_enabled()` shells `bd config get`, a second subprocess this plan does not remove, so
"exactly one `bd` invocation" would fail on correct code (pass-1 C7).

## Two incidental findings

**#139 in the closable list is a deleted issue.** It is the Issue 1.1 scratch issue: created,
measured, then deleted, while bead `yf-nzdv` kept the `external_ref` pointing at it. `closable`
proposes closing an issue that no longer exists — harmless here (it only *proposes*), but it is a
**live stale-ref fixture for SC13**, which requires a stale/deleted-issue ref to fail closed with a
named reason rather than create a duplicate. Issue 3.4 should use it rather than synthesizing one.

**The caveat still applies and is still needed.** Every issue in this report is visible because
some bead maps to it. The coarse plan trackers remain invisible until 4.3 stamps new ones and 4.4
backfills the old — the run below is *not* evidence that nothing else needs closing:

```
NOTE: Hand-filed coarse plan trackers carry NO bead mapping and are invisible to this
signal — a clean run does NOT mean nothing needs closing.
```
