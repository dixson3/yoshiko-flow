---
type: Finding
okf_spec: OKF-PLAN
description: >-
  [finding] 'Zero coverage' REFUTED as stated (61.4%, all happy-path plus one refusal, 17 uncovered statements all refusal bodies); the preamble has nine steps not six; #334's bypass and its test's vacuity both CONFIRMED by spike and by line data; yf-pyqn confirmed with two extra sites
id: exp-004-preamble-coverage
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
---
# EXP-004: Preamble coverage — "zero" REFUTED, `#334` and `yf-pyqn` CONFIRMED

**Question.** What does the suite actually cover for the `--apply` preamble, `recover()`'s
four-way branch, and `_land_tty_gate`? Is the `#334` test vacuous? Does a drivable rehearsal
harness exist? (#349, #334 / beads `yf-acrn`, `yf-pyqn`)

**Method.** Coverage run over **all 34 `test_*.py`** files, one process each (a whole-dir run hits
`INTERNALERROR> SystemExit` from the self-executing check scripts). One CLI test drives
`plan_manager.py` in a **`uv run` subprocess**, invisible to ordinary coverage — a pytest plugin
re-routed it through `coverage run -a` and the results are the **union**. Two sandbox spikes:
`#334`'s bypass + its test's vacuity, and `yf-pyqn`'s bookkeeping residue driven through the real
`_land_execute` with a synthetic one-row `LAND_EXECUTOR`. Repo untouched.

## The preamble has NINE steps, not six — the bead's list has drifted

| # | Step | Line | Req | Refusal exit |
| --: | :-- | --: | :-- | --: |
| 0 | mode-exclusivity check; `_land_manifest` | 8405, 8413 | — | 2 |
| 1 | `_land_assert_primary_checkout()` | 8483 | REQ-LAND-010 | 1 |
| 2 | `_land_assert_outside_tree(...)` — **path half** | 8495 | REQ-LAND-035 | 1 |
| 3 | `_land_tty_gate()` | 8504 | REQ-LAND-014 | 3 |
| 4 | decision-file existence | 8522 | — | 2 |
| 5 | `json.loads(...)` parse | 8529 | — | 2 |
| 6 | `_land_assert_outside_tree(...)` — **`body_path` half** | 8540 | REQ-LAND-035 | 1 |
| 7 | `recover()` + four-way branch | 8551–8571 | REQ-LAND-009 | 0 / 2 |
| **8** | **`_land_repreview_or_halt`** — digest re-check | **8577** | **REQ-LAND-002/-011** | **1** |
| 9 | `LandingContext(...)` construction | 8588 | — | unguarded raise |

`yf-acrn`'s six-item list maps to 1–7 but **omits step 8** — even though *the same issue body*
calls the digest re-check "exactly the uncovered frame that produced the `halt_class 5` halt".
The numbered list and the issue's own prose disagree; the list is the drifted one. Sizing the test
epic off six items **under-scopes it by ~20%**.

## "Zero coverage" is REFUTED as stated — the substance holds

`plan_manager.py` overall: **2562 / 3912 statements (65.5%)**.

| Region | Stmts | Covered | Missed | % |
| :-- | --: | --: | --: | --: |
| **`--apply` PREAMBLE** (8483–8598) | 44 | 27 | **17** | **61.4** |
| `_land_assert_primary_checkout` | 6 | 5 | 1 | 83.3 |
| `_land_tty_gate` | 24 | 18 | 6 | 75.0 |
| `LandingJournal.recover` | 20 | 19 | 1 | 95.0 |
| `_land_repreview_or_halt` | 39 | 38 | 1 | 97.4 |

**The 17 missed preamble statements are, without exception, the REFUSAL BODIES** — primary-checkout,
containment ×2, no decision document, bad JSON, `recover→done` (exit 0), `recover→halt` (exit 2),
and the digest-stale refusal.

The suite has exactly **two** `land --apply` drive sites: a subprocess test that executes only
`[8483, 8484, 8495, 8496, 8504–8511]` and stops at the tty refusal; and an in-process `CliRunner`
whose three consumers all call `_open_the_gate(monkeypatch)`, **stubbing the primary-checkout and
tty gates open** and stubbing `_land_execute`.

**The honest claim:** *61.4% statement coverage, all of it happy-path plus exactly one refusal
(the tty gate, exit 3); 17 of 17 uncovered statements are gate-refusal bodies; and there is **no
"no write occurred" assertion anywhere in the file**.*

`_land_assert_primary_checkout` is worse than its 83.3% suggests: five references in tests,
**none behavioral** — one monkeypatch and four AST/source-text assertions. Its refusal return is
never executed. The `--validate-decision` CLI branch (8457–8476) is **entirely uncovered**.

## `recover()` — the action that can re-push is tested only against a spy

Unit-level coverage is good: `test_journal_recovery_every_state` writes and recovers **all 17
states**. CLI-level branch coverage is the gap: `start` and `resume` are exercised **but with
`_land_execute` stubbed**, so "start ⇒ fresh landing ⇒ can re-push" is asserted nowhere. `done`
(exit 0) and `halt` (exit 2) are **never executed**.

**A latent re-push path:** the CLI fall-through at 8571 is
`resume_from = rec.get("resume_after") if action == "resume" else None`, so an action outside
`{start, done, halt, resume}` silently yields `resume_from=None` → a fresh landing from L0,
**re-running `l6_push_one` and `l7_reconcile_writes`**. `recover()` is total today, so this is a
guard against a future edit — but it is the single line standing between an unhandled action and a
re-push.

## `#334` — BOTH claims confirmed, and the test is provably vacuous

```python
allowed = record["has_tty"] and dev_tty_openable
if not allowed and allow_list and record.get("tty") in allow_list:
    allowed = True
    record["allowed_by"] = "operator-configured allow-list"
```

Spike: `allow_list=[None]` → `True`, `allowed_by = "operator-configured allow-list"`.

The test (`test_land_apply.py:384-385`):

```python
allowed = pm._land_tty_gate(allow_list=[g["route_record"]["tty"] or "/dev/ttys999"])
assert allowed["allowed"] is False or allowed["route_record"].get("allowed_by")
```

`tty` is `None`, so `None or "/dev/ttys999"` builds `["/dev/ttys999"]`, which **cannot match
`None`**. The gate refuses, the first disjunct is `True`, and the allow-list test is never reached.
**Vacuity probe: the identical assertion passes against a stub gate that ignores `allow_list`
entirely.** The `or "/dev/ttys999"` fallback added to make the test runnable is exactly what makes
it measure nothing.

**Independently corroborated at line level:** the missed set includes 8728/8729 (the escape body)
and 8731/8732 (the `allowed: True` return) — so across the **entire suite** `_land_tty_gate`
**never once returns `allowed: True`, by any route**.

Fix: `record.get("tty") is not None and record["tty"] in allow_list`. Two tests — a matching entry
that **does** open the gate (the only way to ever cover 8732) and `allow_list=[None]` that must not.

## The rehearsal harness cannot reach the preamble

`land_rehearsal.py` works — run under coverage: exit 0, `L_DONE`, all 15 verdicts `pass`, real refs
pushed to a fake bare origin. But:

```
land_cmd lines executed by the rehearsal: [8388]   # the `def` only
_land_tty_gate lines executed: [8683, 8760, 8766]
```

It calls `pm._land_execute(ctx)` **directly** — never a `CliRunner`, never `--apply`, never
`land_cmd`. **Zero of the 44 preamble statements.** Its `_build_sandbox` is reusable as-is.

**The real blocker is the whole-function stubs.** L8/L12/L13–L15 contain **11 raw `subprocess.run`
sites and zero `ctx.run` calls**, so the rehearsal must replace whole functions — precisely the
`#340` stub-fidelity hazard. **This independently corroborates the seam-first decision:** routing
those sites replaces five whole-function stubs with one injected runner.

Also: the two tests consuming the rehearsal **read a committed JSON artifact**; the harness is
**never executed by pytest**.

## `yf-pyqn` CONFIRMED — residue is wider than the bead states

The wrapper covers **line 10143 and nothing else**. Spike, real `_land_execute`:

```
[A raises (inside wrapper)] NO EXCEPTION -> halted=True, verdict inconclusive
[B returns None]           BARE TRACEBACK: AttributeError: 'NoneType' has no attribute 'get'
[C row missing 'verdict']  BARE TRACEBACK: KeyError: 'verdict'
[D bad journal phase]      BARE TRACEBACK: ValueError: 'L_INVENTED' is not one of the 17 states
```

B/C/D **return** rather than raise, so the wrapper never sees them. Vulnerable bookkeeping: 10166,
10171, 10172, 10173, 10189 — **plus two sites the bead omits**: the skip-path journal write at
**10106** and `_land_resume_done` at **10075**. And `land_cmd:8589` is a bare
`out = _land_execute(...)` with **no outer `try`**, so any of these reaches the operator as a raw
traceback with no envelope, halt class, or remediation — the exact `#340` shape.

Option (b) from the issue — a second narrow guard around the loop body — handles all of them;
option (a) handles B/C/D but not 10106 or 10189.

## Absences

| Absence | Command |
| :-- | :-- |
| **No pytest/coverage config anywhere** — no `pytest.ini`, `pyproject.toml`, `conftest.py`, `.coveragerc`. Tests are PEP-723 self-running scripts | `cat pytest.ini setup.cfg pyproject.toml tox.ini` → empty |
| **No test asserts "no write occurred" after a refusal** | `grep -n "no write\|nothing was written\|unchanged" test_land_apply.py` → **0 hits** |
| **No behavioral test of `_land_assert_primary_checkout`** | 5 refs, all monkeypatch or AST |
| **`_land_tty_gate` never returns `allowed: True`** anywhere | missed set includes 8731/8732 |
| **The rehearsal harness is never run by pytest** | tests read a committed artifact |
| **`ctx.run` used zero times in L8–L15** | `awk ... \| grep -c "ctx.run"` → `0` |

## Implications for the plan

1. **`yf-acrn`'s headline must be restated or a red-team pass will refute it in one coverage run.**
   Use the measured figures, which are equally damning.
2. **Correct the bead's step list to 8–9 items**, adding `_land_repreview_or_halt`.
3. **RED baseline for the preamble epic: 17 statements, 8 refusal cases.** One test per case,
   each asserting the exit code **and** that no ref moved / no journal was written.
4. **Reuse `land_rehearsal.py:_build_sandbox` verbatim.** Do not write a second sandbox builder.
5. **Add a "no write occurred" helper.** Its total absence is why the preamble's whole safety
   property is currently checked only by a test that reads the *source text*.
6. **Make the CLI's `recover()` fall-through fail-closed** — an unrecognised action should exit 2,
   not silently become a fresh landing.
7. **The coverage-gate mechanism needs an explicit decision.** The suite's only real-CLI test runs
   in a `uv run` subprocess and is invisible to ordinary coverage; a naive gate would report the new
   preamble tests as uncovered and mislead the next reader exactly as it nearly misled this one.
