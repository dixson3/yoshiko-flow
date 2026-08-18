---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-attempt-counter-storage
plan: plan-045-james-dixson-9899e1
created: '2026-08-17'
---

# exp-002 — Where a per-bead attempt counter can live (D-3)

**Question:** Where can a "consecutive failed resolution attempts" counter live so it is mechanical, persistent, and crash-safe?
**Method:** `bd update --help`, full key enumeration across 1245 records of `.beads/issues.jsonl`, empirical probes against a **throwaway** `bd` repo (prefix `mdt`) in the scratchpad, plus source reads of `_resume_scan` and `coordinator.md`. No repo file modified; no live bead mutated.

## Headline — the coordinator has no failure branch at all

The loop, quoted from `coordinator.md`:

> 3. `bd update <id> --claim --json`
> 4. `bd show <id> --json` — read metadata
> 5. If metadata specifies agent file, spawn sub-agent with that prompt. Otherwise execute directly.
> 6. `bd close <id> --reason "Completed" --json`

**The only `Fail:` branch in the entire loop is step 2, and it applies to gate beads only.** Steps
5 → 6 have no conditional — step 6 closes **unconditionally** with the hardcoded reason
`"Completed"`.

So a work bead that fails today either gets closed as "Completed" anyway, or leaves the agent to
improvise a stop — **which is precisely the arbitrary-stopping loophole this plan targets.**

> **Scope consequence:** there is **no natural increment site; the plan must create one.** The
> counter work is inseparable from adding an explicit failure branch to the loop. `bd` already
> offers the status: `invalid status "bogus" (built-in: open, in_progress, blocked, deferred,
> closed, pinned, hooked; …)`.

## `--metadata` is a MERGE, not a replace (measured — and undocumented)

Probed against a bead pre-loaded with `{upstream, disposition, plan_dir}`:

```
[baseline]                        {plan_dir, upstream: '#999', disposition: 'include'}
[--metadata '{"attempts":1}']     {attempts: 1, plan_dir, upstream, disposition}   ← merged
[--set-metadata attempts=2]       {attempts: 2, plan_dir, upstream, disposition}
[--unset-metadata attempts]       {plan_dir, upstream, disposition}
```

A counter written via `--metadata` would **not** clobber `upstream`/`disposition`/`plan_dir` on bd
1.1.2. But this is **undocumented in both `bd`'s help and the repo's specs**, and every existing
yf call site writes a whole object (e.g. `--metadata '{"upstream":"#142","disposition":"include"}'`)
— behavior consistent with an author who *assumed* replace. Treat merge as **version-observed, not
contractual**.

**Footgun (measured):** `--metadata '{"n":null}'` does **not** delete the key — it stores a literal
JSON `null`. Only `--unset-metadata` deletes.

**Type coercion (measured):** `--set-metadata n=3` stores int `3`; `b=true` stores a bool. This
matters because `bd list --metadata-field yf_attempts=2 --json` correctly matched the int — so the
counter is directly queryable, provided every write goes through the same path.

## No native counter exists

The full mutable field surface from `bd update --help` contains no attempt/retry flag. The three
`*_count` fields are graph-edge counts. `started_at` is **overwritten** on re-claim, not a history.

`.beads/interactions.jsonl` looked like a free counter but is not — measured histogram over 1109
records:

```
(in_progress -> closed): 731    (open -> closed): 376
(open -> in_progress): 1        (closed -> in_progress): 1
```

Probe isolated the cause: **`--claim` emits no `field_change` record** (line count unchanged across
a claim; +2 across an explicit `-s open` / `-s in_progress` pair). Only 1 `open -> in_progress`
record exists against 731 beads that demonstrably passed through it. The audit log cannot be mined.

## Storage decision: bd metadata key `yf_attempts`

| Location | Verdict | Why |
| :-- | :-- | :-- |
| `.yf/plan/*.json` | **reject** | The codebase declares it a **discardable cache** — *"State is a gitignored cache, so a failure here is never fatal … the caller simply starts cold."* `YF_DIR` is **cwd-relative**, and `coordinator.md` runs sub-agent beads with cwd = `.worktrees/<plan-id>` while `bd` stays primary-side → **silent split-brain** between two `.yf/` dirs |
| File in `plan_dir` | **reject** | `docs/plans/` is git-tracked → commit churn, merge conflicts, counter leaks into the published bundle |
| `notes` / `close_reason` | **reject** | Unstructured; needs a regex; `close_reason` only exists post-close |
| **bd metadata** | **accept** | Durable in Dolt, address-space independent (INV-2 resolves from anywhere), survives the `-s open` sweep, exported to JSONL, queryable, **already read at loop step 4 and by `_resume_scan`** |

**Key naming:** 202 beads carry metadata; keys in use are `upstream` (91), `disposition` (89),
`agent` (69), `context` (69), `plan_dir` (40), `cluster` (17), `research_dir` (4), plus five
one-off ad-hoc keys. **No `attempts`-like key exists.** `yf-beads-authoring` SPEC states
*"consumer-specific keys are namespaced"*, so a `yf_`-prefixed key is convention-compliant.

**Write discipline: always `--set-metadata yf_attempts=<n>`, never `--metadata '{...}'`** — merge
is measured-true but undocumented; `--set-metadata` states per-key intent in the flag and is immune
to a future semantics change. Clear with `--unset-metadata`.

## Structural fit with the existing sweep

`_resume_scan`'s stuck detector is **status-based and stateless**:

```python
# A claimed bead lands in `in_progress` (bd update --claim sets status + owner),
_STUCK_STATUSES = ("in_progress",)
```

It **cannot distinguish a first crash from a fifth.** The counter is exactly that missing
dimension, and it rides along free: `-s open` preserves metadata (measured), and `_resume_scan`
already carries each bead's `metadata` dict in memory — surfacing `yf_attempts` in the `stuck`
records is a one-line change.

## Increment / reset points

- **Increment** on a *detected failure* of step 5, reading the current value from the step-4
  `bd show --json` already in hand (no extra call). Write `yf_attempts=<n+1>` plus a
  `yf_last_failure` string, set `-s blocked` or `-s open`, and **continue the loop**.
- **Reset** immediately **before** step 6's close (`--unset-metadata`), so a later-reopened bead
  starts clean.
- **Escalate** only when `yf_attempts >= N` *after* the increment. Below N the loop **must
  re-queue, not stop.**
- **Surface** `yf_attempts` in `_resume_scan`'s `stuck` records so a resume escalates rather than
  blindly resetting a bead on its Nth cycle.

## Four ways this produces a FALSE escalation

1. **Crash-vs-failure conflation (highest risk).** Incrementing at *claim* time for crash-safety
   would make Ctrl-C, OOM, context exhaustion, and reboots each count as a "failed attempt" — N
   infrastructure crashes would escalate as "scope ambiguity" on a bead nobody attempted. Hence
   increment **on detected failure**, accepting the mirror cost: a crash between failure and the
   metadata write undercounts by one. **Prefer the undercount** — it delays escalation rather than
   fabricating it.
2. **Cross-resume accumulation.** The counter is durable and survives the sweep. A bead
   legitimately revisited across sessions (deferred → upstream fix → dependency landed) accumulates
   increments. **Mitigation:** reset when the bead's *blocking cause* changes; only a same-cause
   failure increments. "The bead didn't close this pass" is too broad a predicate.
3. **Double-count on re-claim.** `--claim` is idempotent and emits no audit record (measured), so
   it is invisible. Increment exactly once per **dispatch**, at the failure site — never keyed to a
   claim call.
4. **Query type mismatch.** Int `2` written via `--set-metadata` matches
   `--metadata-field yf_attempts=2`; a string `"2"` written via a JSON blob likely would not
   (untested, but the coercion asymmetry is real). Keep every write on one path.

**Fifth gap (not a false positive):** nothing resets the counter when a bead is closed by a path
other than step 6 — the cascade-close or a manual operator close. A stale `yf_attempts` would sit
on a closed bead and be live again if reopened. Cheap fix: make the reset unconditional on any
transition into `closed`.

## No existing precedent to imitate

Grep of `yf-beads-extra` / `yf-beads-authoring` for `scratch|counter|increment|attempt` returns
only an unrelated bd 1.0.x corruption note and two hits restating the *refusal* to have such a
signal (REQ-ORCH-010): *"There is no reliable bd-state signal separating disposable scratch from
real work… No bead is ever auto-closed."* **plan-045 would establish the first pattern.** The
nearest precedent is the `agent`/`context` metadata convention (REQ-ORCH-001, attached post-pour
via `bd update --metadata`).
