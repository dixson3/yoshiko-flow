---
type: Finding
okf_spec: OKF-PLAN
description: >-
  [finding] Seam-first VALIDATED by a zero-stub spike (18 rows+halt unpatched vs 23 rows+L_DONE patched); 8 bare calls not 7, and yf-i127's 'only one cwd-less call' is refuted - L17's bd show is the second and more dangerous; REQ-LAND-037 confirmed free
id: exp-002-ctxrun-seam
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
---
# EXP-002: The `ctx.run` seam — approach VALIDATED, `yf-i127` partly REFUTED

**Question.** What is `LandingContext.run`, what do L8–L19 actually invoke, and what is the blast
radius of routing every close-chain subprocess through the seam? (#348 / beads `yf-9yb0`, `yf-i127`)

**Method.** An **AST scanner** (not grep) over every `_land_*` function, classifying each
`subprocess.*` / `os.*` / `_run_git` / `ctx.run` call by line, keyword set and `cwd` presence; a
sandbox spike applying the full patch to a copied tree and running the suite against baseline and
patched; and a **zero-stub rehearsal spike** driving `_land_execute` in both copies with the three
whole-step stubs deleted. Sandboxes removed; worktree clean.

## The seam

`plan_manager.py:9161-9169` — `self.run = self._dispatch`:

```python
def _dispatch(self, prog: str, args: list[str], cwd: Path | None = None):
    if self._runner is not None:
        return self._runner(prog, args, cwd=cwd or self.root)
    if prog == "git":
        return _run_git(args, cwd=cwd or self.root)
    return subprocess.run([prog, *args], cwd=str(cwd or self.root),
                          capture_output=True, text=True)
```

Four properties bare `subprocess.run` lacks: **cwd defaulting** (`cwd or self.root` — this *is*
`yf-i127`'s fix, mechanically); **the injection seam** (`self._runner` short-circuits the spawn, so
the *same* step functions run under test — REQ-LAND-001's "one code path"); **program as an
explicit argument** (a fake can witness *which executable* ran — the docstring records that an
earlier `_run_git`-wrapping version made L7 run `git issue comment` and L19 `git self install`,
with **every Tier-1 test passing**); and a **fixed capture mode**. It does *not* journal — that is
`_land_execute`'s job.

## Complete inventory — exactly 8 bare calls, all inside L-steps

| Step | Line | Command | `cwd`? |
| :-- | --: | :-- | :-- |
| L5 | 9354 | `uv run <plan_manager.py> recheck-criteria` | yes |
| L8–L11 | 9521 | `uv run <plan_manager.py> <verb>` — **one call site, seven launches** | yes |
| L12 | 9556 | `uv run <close_cascade.py>` | yes |
| L13 | 9579 | `uv run <plan_manager.py> complete-gate` | yes |
| **L14** | **9592** | `bd list --all --include-gates --limit 5000 --json` | **NO** |
| L14 | 9596 | `uv run <pour_fidelity.py> --strict` | yes |
| L15 | 9616 | `uv run <plan_manager.py> update-status` | yes |
| **L17** | **9759** | `bd show <bead> --json` (read-back loop) | **NO** |

All 8 carry keyword set `{capture_output, text}` ∪ optionally `{cwd}` — **nothing else**. No
`stdin`, `input=`, `Popen`, pipe, `check=`, `timeout=`, `env=`, `shell=`, or `os.system` anywhere
in the file. L1/L2/L4/L6/L7/L16/L18/L19 are already 100% on the seam.

## `yf-i127` is partly REFUTED — there are TWO cwd-less calls, and the second is worse

The bead says L14's `bd list` is *"the ONLY close-chain subprocess launched without
`cwd=ctx.root`"*. Measured: **8 bare calls, 6 with `cwd`, 2 without.** True only if "close chain"
is read narrowly as L8–L15. Read as "the landing path", **false**.

**L17's `bd show` (9759) is arguably more dangerous than L14's**, because it is the step's *only*
verification signal (REQ-LAND-019): reading the wrong database there produces "no `external_ref`"
and a halting fail on a push that actually succeeded — or the inverse.

Two further cwd-less `bd` calls sit outside the L-steps with no `ctx` in scope:
`_land_epic_from_bd:6504` and `_land_route_record_findings:6623`. Same class, different remedy.

## The seam needs to grow NOTHING structurally

All 8 shapes fit `_dispatch(prog, args, cwd=None)` unchanged; the spike applied 8/8 substitutions
with no signature change. Three limitations worth recording, none blocking:

- **No `env=`.** Not needed today, but a `recover()` test wanting to vary `CI` / `YF_NO_CONFIG_SYNC`
  around L19 has no seam parameter.
- **Program-level granularity only.** After routing, L8–L15's seven verbs all report `prog == "uv"`;
  verb-level assertions must use `FakeRunner.saw(...)` on the arg axis.
- **`cwd` cannot be *omitted*.** That is the fix, not a gap — but no future step can opt out.

## The zero-stub rehearsal spike — the decisive measurement

Same runner injected into both copies, three whole-step stubs deleted in both:

| | terminal journal | reached terminal | step rows | programs the runner saw |
| :-- | :-- | :-- | --: | :-- |
| **unpatched** | `L_RECONCILED`, halted at `l14_pour_fidelity` | `None` | 18 | **`['git']` only** |
| **patched** | `L_DONE` | `True` | **23** | `['bd', 'git', 'uv', 'yf']` |

The unpatched run proves the seam is genuinely bypassed — the injected runner **never saw a single
`uv` or `bd` call**. In the patched run the seam recorded the `bd list` invocation with `cwd=work`:
the `yf-i127` defect fixed *and observable*.

`land_rehearsal.py` (209 lines) stubs three steps wholesale at `:130/:133/:136`. Its
`stubbed_steps` record reads three labels but **hides five L-numbers** — L9, L10, L11, L13, L14 are
also unexercised, and `l14_pour_fidelity` appears in no entry at all. Whatever replaces it should be
**derived from `LAND_EXECUTOR`**, not hand-written — the same "second enumeration that can drift"
defect `spec/landing.md` forbids elsewhere.

## Blast radius — small

- **Call sites changed: 8.** All in one file, all inside `_land_l*`.
- **Existing tests broken: exactly 1 assertion** — `test_land_apply.py:1327`,
  `{"uv"}` → `{"uv", "bd"}`. It is an **improvement**: REQ-LAND-019's read-back becomes visible to
  the seam for the first time. Other 61 tests pass unchanged (baseline on `main`: 66 passed).
- **Consumers outside `_land_*`: none.**
- **`mock-fidelity` gate safe:** `PASS, checked: 35`; deleting three stubs leaves 32, and the
  vacuity guard is `checked == 0`.
- **`CHANGE-VALIDATION.md` rows already cover it** — no new rows needed.

**Refactor hazard:** `test_pour_fidelity_inconclusive_is_not_a_divergence` walks the AST for
`ast.Compare` on `f.returncode`. **Do not rename the local bindings** `f`, `g`, `s`, `bl`, `back`,
`proc` — the test would go quietly vacuous.

## SPEC-first — a NEW requirement is mandatory

`grep -rn "ctx.run|injection seam|LandingContext|runner\b" skills/yf-plan/spec/ SPEC.md` returns
**zero hits on the seam**. It is specified nowhere — it lives only in a docstring and one test.

**`REQ-LAND-037` is confirmed free** (highest allocated is 036; 027 is reserved). It should state:
*every process a landing step launches is issued through `LandingContext.run`, with `cwd` defaulted
to the checkout root* — making **both faces of #348 one normative sentence**.

Leaned on but not rewritten: REQ-LAND-001 (its "one code path" rationale becomes checkable),
REQ-LAND-019, REQ-LAND-020, REQ-LAND-030, REQ-LAND-009/011/029.

## Implications for the plan

1. **Seam-first ordering validated, and the subsumption claim confirmed by measurement:** routing
   L14 fixes `yf-i127` as a side effect of `cwd or self.root`. No separate `cwd=` edit needed.
2. **Scope the epic to all 8 call sites, not 7.** A literal "L8–L15" scope lands the refactor and
   leaves 9759 behind — one line short of the invariant the new REQ would assert.
3. **The epic is SMALL** — 8 call sites, 1 assertion, 3 stubs, 1 new REQ. Not the wide refactor
   plan-063 deferred it as; the tests turn out to be almost entirely AST-based and survive untouched.
4. **Add an AST mechanical check** (grep will not do it): no `subprocess.*` / `os.system` inside any
   `_land_l\d+_*` function. Strictly stronger than a `cwd=` presence check, and it survives the next
   step added.
5. **L14 still needs a poured bead fixture** to be genuinely exercised. A runner returning `[]` for
   `bd list` and `0` for `pour_fidelity` proves nothing about the DAG comparison — that is a stub in
   a different costume.
6. **Patch hazard:** the L8–L15 loop builds `args` starting with `"uv"`; the routed form must slice
   the program off or the seam receives `uv` twice. The one place the substitution is not a pure
   text swap.
