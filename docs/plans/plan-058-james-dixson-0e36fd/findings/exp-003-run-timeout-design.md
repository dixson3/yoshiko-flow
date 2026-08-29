---
type: Finding
okf_spec: OKF-PLAN
id: EXP-003
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# EXP-003: Bounding `run()` — the independent defect

**Question.** #268 direction 3: `run()` passes no `timeout=`, which turned a slow path into a
silent hang. Design the fix. Scope it as its own defect even though the fan-out fix makes this
instance moot.

## Approach Tested

1. Enumerated every `subprocess.*` and `run(...)` call site by grep, then **read the constructing
   code** for each `run(["bash","-c",c])` to learn what those command strings actually are.
2. Timed every command that flows through those sites (5x/3x reps) against the live repo — all
   read-only.
3. Built a sandbox spike (full copy of the skill, `git init`, `uv run --with pytest`), established
   a green 107-test baseline, then applied two candidate patch shapes and re-ran the suite.
4. Drove `run()`, `apply_write()`, `cmd_hoist(..., apply=True)`, `run_unchecked()` and
   `existing_labels()` against a deliberately timing-out subprocess to observe the real error
   surface and whether the destructive stage is reached. Sandbox removed; repo untouched.

## Result

A bound is warranted, cheap and test-neutral — **but it must be applied inside the primitive,
never at a call site**, and it does **not** close #268.

### The finding that reframes this epic

**measured: a per-call timeout would NOT have caught #268.** The fan-out is 1,801 individually-*fast*
calls (0.186 s each). No per-call bound short of an absurd 0.2 s fires. This epic buys
**diagnosability for the next unbounded call**, not a fix for this one — and the plan must say so
plainly rather than letting the reader infer that bounding closes the issue.

### Three spawning primitives, all unbounded

| # | Site | Carries |
| :-- | :-- | :-- |
| S1 | `upstream.py:87-92` `run(cmd)` | 14 call sites: `bd`, `git`, `bash -c`, and **3 `gh`** (2 of them WRITES) |
| S2 | `upstream.py:99-115` `run_unchecked(cmd)` | exactly one: `gh issue list --state all --limit 1000 --json ...` |
| S3 | `upstream.py:185` `_config_get(key)` | `bd config get custom.upstream.*` |

All four `run(["bash","-c",c])` sites are **local `bd` one-liners**, verified by reading the
builders: `hoist_close_commands` (`:946`) emits `bd close <id> -r "..."`; `plan_unhoist` (`:967`)
emits `bd update <id> --status open`. No `bash -c` carries a network command.

### Measured latencies (this repo: 1,801 beads, 268 issues)

| med | max | command |
| --: | --: | :-- |
| 0.29 s | 0.29 s | `bd list --all --json` (3.1 MB stdout) — the slowest local call |
| 0.16 s | 0.16 s | `bd show <id> --json` |
| 0.18 s | 0.19 s | `bd config get ...` |
| 0.02 s | 0.02 s | `git rev-parse --show-toplevel` |
| 0.42 s | 0.74 s | `gh label list --limit 500 --json name` |
| **1.56 s** | **2.38 s** | `gh issue list --state all --limit 1000 --json number,state` |

### Measured bounds

```python
LOCAL_TIMEOUT_S = 60      # 200x the slowest measured local call
NETWORK_TIMEOUT_S = 120   # 50x the slowest measured gh call
NETWORK_COMMANDS = frozenset({"gh"})
```

Repo precedent: `plan_manager.py:2138` `_GH_TIMEOUT_S = 30`; `beads_hygiene.py:139` `timeout=120`
for every `bd` call; `verify_beads.py:62` `timeout=120`. **Do not adopt 30 s for `gh`** — the
paginated list already measures 2.4 s on a fast link and scales with issue count; and two of the
three `gh` commands are writes, where a spurious abort costs more than a slow success.

Two tiers rather than one are justified less by the 5-8x latency gap than by **diagnostic value**:
a `bd` call exceeding 60 s means something is structurally wrong, and a bound that says so beats
one generous enough to hide it.

### The constraint that is NOT cosmetic: bound inside the primitive

Measured in a sandbox spike against the real test suite:

| variant | result |
| :-- | :-- |
| baseline | **107 passed** |
| A: `def run(cmd, *, timeout=None)`, resolved internally from `cmd[0]` | **107 passed** |
| B: pass `timeout=NET` at the 3 `gh` call sites | **3 failed** |

Variant B fails *worse than loudly*: all 17 `monkeypatch.setattr(up, "run", ...)` stubs in
`test_upstream.py` take a single positional parameter, so a `timeout=` kwarg raises `TypeError` —
which `apply_write`'s broad `except (Exception, SystemExit)` (`:883/:892/:905`) then **masks as a
legitimate gh failure**:

```
assert 'DUPLICATE' in "a: gh issue create failed: ..._run() got an
  unexpected keyword argument 'timeout'"
```

### Fail-closed is preserved by construction — verified, not assumed

Spiked with a booby-trapped `bd close`: `cmd_hoist(..., apply=True)` with a timing-out create
returned `rc=1`, printed `No bead was closed`, and **the destructive tombstone stage was never
reached**. `subprocess.TimeoutExpired`'s MRO is `TimeoutExpired -> SubprocessError -> Exception`,
so `apply_write`'s existing handler catches it. REQ-BUP-050/057 needs no new machinery — but it
needs a **test asserting** this, which does not exist today.

### Two sites where a naive `timeout=` is actively harmful

- **`run_unchecked`** — `resolve_upstream_states` (`:164`) catches `(UpstreamQueryError, OSError)`.
  **`TimeoutExpired` is not an `OSError`**, so an unwrapped timeout bypasses the REQ-BUP-064
  INCONCLUSIVE verdict and escapes as a traceback. Must wrap into `UpstreamQueryError`.
- **`_config_get`** — has **no handler at all**. Recommended `except TimeoutExpired: return ""`;
  an empty string contains no `(not set)` and is not `"true"`, so every consumer falls to its
  default-deny branch. Fail-safe by construction — plus a stderr warning so it is not silent.

Also worth fixing while here: `existing_labels()` (`:805`) turns any failure into `set()`, which
`render_plan` then reports to the operator as *"dropping label X (does not exist upstream)"* — a
**false statement** when the cause was a failed read. Pre-existing, but a timeout adds a new route
into it.

### No knob

`grep -rni timeout skills/yf-beads-upstream/` returns **zero matches** — no requirement, no knob,
no prior art in this skill. `upstream.py` does not `import os`. The dominant repo convention for
this class of value is a **module constant** (`_GH_TIMEOUT_S`, `DETECT_TIMEOUT_SEC`). If a knob is
ever demanded the repo-consistent form is a **CLI flag**, and explicitly **not** `bd config get` —
`_config_get` is itself one of the calls being bounded, so that would be circular.

## Implications for Plan

- This epic must be labelled, in the plan text, as **not closing #268**. Left unstated, a reader
  reasonably infers that "we added timeouts" fixed the hang, and the real fix looks optional.
- The epic is genuinely independent of the fan-out fix and can proceed in parallel or after it.
- **inferred:** because there is no `REQ-*` covering subprocess bounding anywhere in this skill
  (zero `timeout` matches), the SPEC-first mandate makes a new requirement a prerequisite rather
  than a nicety.
- The fail-closed contract needs **no new machinery**, but it currently rests on an untested
  property of an exception hierarchy. That deserves an explicit regression test.

## Recommendations

1. **Bound inside the primitive, keyed off `cmd[0]`** — module constants plus a `timeout_for(cmd)`
   classifier. Do **not** add `timeout=` to any call site.
2. Keep the signature caller-invisible: `def run(cmd, *, timeout=None)` resolving `None ->
   timeout_for(cmd)`. Measured: 107/107 tests pass unchanged.
3. Wrap `run_unchecked`'s timeout into `UpstreamQueryError` and give `_config_get` a handler
   returning `""` — both are sites where a naive `timeout=` is actively harmful (above).
4. Fix `existing_labels()`'s false "does not exist upstream" report while here.
5. **No knob.** Module constants match the dominant repo convention; if one is ever demanded the
   repo-consistent form is a CLI flag, and explicitly not `bd config get` (circular — `_config_get`
   is itself one of the bounded calls).
6. Add the four tests listed above, including the REQ-BUP-050 assert-trap regression guard.

## Evidence

- `skills/yf-beads-upstream/scripts/upstream.py:87`, `:99`, `:185`, `:804`, `:882`, `:891`, `:946`, `:967`, `:1483`
- `skills/yf-plan/scripts/plan_manager.py:2138`, `:341`, `:2828`; `skills/yf-beads-hygiene/scripts/beads_hygiene.py:139`, `:729`
- Sandbox spike (removed; repo untouched): 107-test baseline, variant A/B runs, and the
  fail-closed hoist trap described above
