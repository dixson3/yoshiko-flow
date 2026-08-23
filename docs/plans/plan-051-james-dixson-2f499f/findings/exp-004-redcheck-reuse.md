---
type: Finding
okf_spec: OKF-PLAN
id: exp-004
description: Can plan-050's driven-red control harness be reused, and can a control exist for each of this plan's three subjects?
---

# EXP-004 — harness reuse, and whether a control is possible at all

## Approach Tested

Read `redcheck.sh` (257 lines), `gate-run.sh`, `controls.txt`, `red-prework.md` and RE-005 in full.
Built a sandbox containing a synthetic `plan-051-fake/` bundle, copied both harness scripts in
**unmodified**, and drove all three verbs across 6 arms. Authored three candidate plan-051 fixtures,
ran them RED against the real repo (read-only), applied a simulated fix set to a **sandbox copy** of
`skills/yf-plan/`, and re-ran them GREEN. Probed the id-derivation against 8 id shapes. Sandbox
deleted; repo untouched.

## Result

**measured:** the harness is **plan-agnostic**. Every path derives from `$0` (`redcheck.sh:54-60`);
no plan-050 string, control id or path appears in any executable line. Dropped into a differently
named bundle at an arbitrary path, all three verbs worked with **zero edits**.

**measured:** the one coupling is `REPO_ROOT="$(cd "${PLAN_DIR}/../../.." && pwd)"` — it assumes the
`docs/plans/<plan-id>` depth. For plan-051 (a `docs/plans/` bundle) the default is correct, and every
invocation overrides it with `YF_TREE` anyway, as plan-050's own records show.

**measured:** **RE-005's subshell defect is FIXED in the shipped script** and does not travel. The fix
is a global `FIXTURE_RC` + explicit `return 2` (`:106-116`) with the reasoning preserved in comments.
Verified by spike against a nonexistent fixture:

```
record-red  <nonexistent>  → "HARNESS FAILURE — fixture does not exist"  EXIT=2
                             red-prework.md was never even created — no garbage record
assert-distinguishes       → EXIT=2
via gate-run.sh            → "gate UNRESOLVED"  EXIT=2
```

`gate-run.sh` was audited for the same shape — it uses `bash "$target"; rc=$?` in the parent shell
with explicit 126/127/128+N arms.

### The id-derivation: this plan's ids fit, but there is a live contamination hazard

**measured:** `grep -oE 'ctl-[0-9]{3}-[a-z-]+'` against 8 shapes — `ctl-182-spike`,
`ctl-184-dispatch`, `ctl-165-executable` **all fit**. Non-conforming shapes (4-digit issue numbers,
digits in the name part, caps, underscores) silently undercount: 8 declared → 4 counted.

**measured, and this is the trap:** cross-plan prose contamination. A `plan.md` naming plan-050's six
control ids derives **7** against a manifest of **1** → `verify-all` exits 1, permanently, with a
**misdiagnosed** message. This is pass-12 C123's failure in a new form. The derivation reads *only*
`plan.md`, so the same names in `findings/` are harmless — which is why they live here.

### A control IS possible for all three subjects — and this REFUTES D-8 as written

plan-050's **D-8** says #182's fix *"has no exit code and cannot have one."* That is right about
**behaviour** and **wrong about the edit set**.

| Subject | Control | Measured |
| :-- | :-- | :-- |
| #184 | `SKILL.md`'s `### Review` section names `` `Agent` `` | RED against the real repo (exit 1); GREEN against a sandbox tree with §3 step 2 rewritten |
| #182 | two conjuncts — `red-team.md` authorizes a spike, **and** every double-quoted fragment in `REQ-AGENT-043`'s `Verification:` line is verbatim-present | RED; **half-fix arm exits 1**; full fix exits 0 |
| #165 | each named new REQ's `Verification:` is a whole-line backticked command that exits 0 from the tree root | RED (no line); MIXED arm exits 1 (prose, not command); GREEN when both executable |

**The half-fix arm is the load-bearing result.** Editing `red-team.md:63` alone **breaks**
`spec/agents.md:73`, whose Verification clause pins the literal string, and the fixture catches it
with an exit code. So #182 has a genuine red→green control on **spec↔prose quote parity** — a real
assertion about the edit set's completeness, not a token-presence tautology.

**measured, and EXP-002 should absorb this:** `grep -n 'Read-only — never writes files'` returns
`red-team.md:63`, `spec/agents.md:73` **and `spec/agents.md:97`** — a **third** pinned site
(REQ-AGENT-045, for `reviewer.md`) the plan had not named.

**measured — the id space is more crowded than EXP-001's headline suggests:** `REQ-AGENT-050`, `-051`
and `-060`–`-064` all exist. Free: **`049`, `052`–`059`**. A first spike arm silently picked up the
pre-existing `-050` and reported a false RED.

### Promotion to `_shared/`: the drift is real, the contract argues against it

**measured:** `gate-run.sh` already exists in **three** copies (plan-048, -049, -050) and they have
**materially drifted** — `set -u` vs `set -uo pipefail`, `-f` vs `-e`, a dropped readability check,
and 048 collapsing the exit arms where 049/050 add distinct 126/127/128+N diagnostics. 049 vs 050
differ only in a header comment.

**inferred:** the decisive counter-argument is `spec/portability.md:5` — a cold reader *"in a
different repo … from the plan folder alone."* A bundle whose red→green evidence cannot be re-run
outside this repo is weaker than a bundle carrying a duplicated 250-line script. Uncorroborated as a
policy reading; ~10 plans referencing `_shared/` are the counter-precedent, though those reference
*engines under test*, not *the bundle's own evidence harness*.

## Implications for Plan

- **Reuse is discharged in favour of copying.** A full two-control red→green→`verify-all`=0 cycle ran
  on the unmodified scripts.
- **The approach hypothesis SURVIVES on the control axis** — a control exists for all three subjects,
  not zero or one.
- **D-8 must be narrowed, not inherited verbatim and not dropped.** Carried as written, plan-051
  would under-claim and skip a control it can actually build.
- **EXP-002's scope grows by one site** (`spec/agents.md:97`).

## Recommendations

1. **Reuse `redcheck.sh` and `gate-run.sh` AS-IS** — byte-for-byte copy, header comment only. Do not
   rebuild; do not promote to `_shared/`.
2. **Author three controls:** `ctl-182-spike`, `ctl-184-dispatch`, `ctl-165-executable`.
3. **Guard the derivation** — either keep plan-050 control names out of `plan.md` (they live in this
   finding), or tighten the pattern to `ctl-(165|182|184)-[a-z-]+`. State the choice **in the issue
   that builds the harness**: pass-12 C123's lesson is that an executor copies whatever the issue
   prints.
4. **Restate D-8 for this plan:** *#182 and #184 ship controls certifying the EDIT SET is complete and
   internally consistent. Neither certifies that a reviewer obeyed the rule; no exit code can.*
5. **Reserve `REQ-AGENT-049` and `-052`** before drafting.
6. Note the #165 control's **redundancy caveat**: if the new REQs' Verification lines *are* the
   ctl-182/ctl-184 assertions, ctl-165 green ⟺ those two green, adding only "the line parses as a
   command." Useful, but not independent evidence — do not present it as such.
