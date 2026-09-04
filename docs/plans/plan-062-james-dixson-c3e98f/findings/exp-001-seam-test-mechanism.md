---
type: Finding
okf_spec: OKF-PLAN
description: 'Measured comparison of four mechanisms for driving land --apply past the tty gate in a test. Discrimination test proves a gate-stubbed in-process test catches the #327 defect class; a real pty is NOT required. Two options (test env flag, allow-list wiring) create production-reachable bypasses and are rejected. Also records three incidental defects: allow_list=[None] total bypass, a vacuous existing test, and a dead resume loop.'
---
# EXP-001 — How should a CLI-driven rehearsal pass the tty gate?

**Question.** How can a test exercise `land --apply` end-to-end without creating a bypass an
agent could use to self-authorize a real landing?

## Approach Tested

Built a throwaway sandbox in `$(mktemp -d)`: copied `plan_manager.py`, `okf.py` and
`plan_template.py` out of the repo, reproduced `test_land_apply.py`'s `repo` fixture, and ran four
spikes plus a **discrimination test** against a hand-patched build in which the stub was replaced
with real wiring. `land --apply` was never invoked against this repository. Sandbox removed.

## Result

## HEADLINE: the expensive option is not necessary, and this was measured, not argued

The scoping decision commissioning this experiment chose *"seam + full sandbox rehearsal
through the CLI"*. **That is refuted.** A **discrimination test** — the same assertion run
against the defective build and against a hand-wired build — settles it:

| Build | Exit | Reason | Assertion "reaches the engine" |
| :-- | --: | :-- | :-- |
| `pm_base` (as shipped) | 2 | `the --apply executor is not implemented in this change-set` | **FAIL** |
| `pm_fixed` (stub replaced with real wiring) | 1 | `decision is not conformant: 3 problem(s)` | **PASS** |

An in-process test with the gate monkeypatched **discriminates broken from fixed**. A real
pty adds nothing for *this* defect class.

## The four mechanisms, measured

| Option | Works? | New capability an agent gains |
| :-- | :-- | :-- |
| (a) `pty.fork()` | **yes** (~20 stdlib lines; CI-safe with stdin closed) | none — but ships a working bypass recipe in-tree |
| (b) wire the dormant `allow_list` | **only in a narrow case**, and holes | a **config-reachable** switch |
| (c) in-process `CliRunner` + monkeypatched gate | **yes, and discriminates** | **none** — no production path reaches it |
| (d) test-only env flag | **yes, cheapest of all** | a **named, sanctioned-looking** env var |

Baseline, measured in an ordinary agent Bash subprocess: `EXIT=3`, `no controlling terminal on
fd 0`, `dev_tty_error: OSError [Errno 6] Device not configured`, and the route record carrying
`agent_markers: [CLAUDECODE, CLAUDE_CODE_ENTRYPOINT, HERDR_PANE_ID]`.

Option (c) stage 2 drove the engine through the real CLI callback with an injected runner, no
network, reaching L4:

```
l0_lock_acquire    pass  L_LOCKED
l1_down_merge      pass  L_DOWNMERGED
l2_merge           pass  L_MERGED_UNCOMMITTED
l3_validate_merged pass  L_VALIDATED
halted at l4_commit_merge  (fixture fidelity — fake rev-parse returns empty, not a limit)
```

## Why (b) and (d) are rejected — the cost that matters is rhetorical

`#293`'s failure mode is an agent **rationalizing** its own authorization, not an agent lacking
a technical route: it already has several, and the gate's own docstring names `herdr pane run`
as a known bypass. So the question is not "does this add a capability" but "does this supply a
justification".

- **(d) is worst**: it manufactures the exact rationalization — *a test-open flag exists,
  therefore using it is sanctioned*. Measured to open the gate from an ordinary agent Bash call
  with one env var and zero lines.
- **(b) is next worst**, for the same reason plus a hole (below).
- **(a)** adds no capability but normalizes the bypass by shipping the recipe.
- **(c)** adds neither capability nor rationalization.

This judgement is **uncorroborated** — it is a claim about agent behaviour, not a measurement.
Its one empirical anchor is `#293` itself.

## Three incidental defects found, none of them this plan's remit

1. **`allow_list=[None]` is a TOTAL BYPASS.** Measured in a tty-less context:

   ```
   allow_list=[]               -> allowed=False
   allow_list=['/dev/ttys999'] -> allowed=False
   allow_list=['*']            -> allowed=False   (no glob support)
   allow_list=[None]           -> allowed=True    allowed_by=operator-configured allow-list
   ```

   `record["tty"]` is `None` for exactly the caller the gate exists to refuse, so a JSON
   `null` in any future config wiring opens it unconditionally. An env var with `.split(",")`
   cannot produce `None` — safe **by accident, not by design**.

2. **The existing allow-list test is VACUOUS** (`test_land_apply.py:384`). It asserts
   `allowed["allowed"] is False or allowed["route_record"].get("allowed_by")`, which passes
   trivially because `None in ["/dev/ttys999"]` is False. The RE-020 / `#263` class again.

3. **A dead loop in the resume path** (`:9553-9556`): `for key, _ in LAND_EXECUTOR: pass`.

## What a gate-stubbed test structurally CANNOT catch

That `_land_tty_gate()` is called **at all**, at the right point. That half is **already
covered** by a real-process test — `test_tty_refusal_exits_three_not_one_or_two`
(`test_land_apply.py:388`) drives the real CLI and asserts `returncode == 3`. So the
gate-**closed** half has process-level coverage today; only the gate-**open** half is
uncovered, and that is exactly what (c) covers.

The residual gap — someone deleting the `gate = _land_tty_gate()` call entirely — is closable
by a **source-level `ast` assertion** that `land_cmd` calls the gate before any write. The file
already uses `ast` this way at `:314`. That is cheaper than a pty and catches a defect the pty
would not.

## Implications for Plan

**measured:** every quantitative claim above came from a runnable spike or an AST read, not
from reading prose. **inferred:** the judgements about agent behaviour and about what a
future reader would conclude are reasoning, not measurement, and are labelled as such where
they appear.

The consequences for the plan are carried in the sections above and in `plan.md`'s Approach.

## Recommendations

**Option (c)**, added to `test_land_apply.py` (already a `CHANGE-VALIDATION.md` recipe row,
`uv-yf-land-apply`), **plus** the `ast` source assertion, **plus** retaining the existing
gate-closed process test at `:388`. Together the two halves are covered without any build ever
running with the gate open in a real process.
