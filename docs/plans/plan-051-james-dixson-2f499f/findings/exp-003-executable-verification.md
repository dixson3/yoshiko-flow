---
type: Finding
okf_spec: OKF-PLAN
id: exp-003
description: Does any SPEC `Verification:` line in this corpus actually EXECUTE today, and by what mechanism?
---

# EXP-003 — executable `Verification:` prior art

## Approach Tested

A paragraph-aware extractor over `skills/*/spec/*.md` plus root `SPEC.md` (clauses run
mid-paragraph, so a line-grep undercounts); a repo-wide grep for any code parsing the token; and
**hand-execution of ten literal Verification commands** against the live tree. Sandbox only; repo
untouched.

**Question.** Does any SPEC `Verification:` line execute today? This decides whether #165 stays in
plan-051's scope or drops back to `exclude`.

**Answer: YES — and the plan's own hypothesis was wrong.** The drafting hypothesis allowed for
"no prior art exists, so #165 drops." That escape hatch is closed by measurement: three separate
plans have independently built this mechanism, and one instance is green right now.

## Result

**measured:** the census — — 251 clauses, exactly ONE executes

Extracted paragraph-aware (clauses run mid-paragraph, so a line-grep undercounts) over
`skills/*/spec/*.md` plus root `SPEC.md`:

| Class | Count | Share |
| :-- | --: | --: |
| Total `Verification:` clauses | **251** | 100% |
| Backticked string parseable as a shell command | 29 | 11.6% |
| Prose naming a document/section | 137 | 54.6% |
| Prose asserting a property, no artifact named | 85 | 33.9% |

**30 of 251 name a `test_*.py` file** — which is *not* the same as executing, see the trap below.

**measured:** nothing parses `Verification:` generically

`grep -rn "Verification" --include='*.py' --include='*.rs' --include='*.toml' --include='*.sh'`
returns 19 hits outside `docs/plans/`. Every one is either the plan-bundle table **column header**
(`_shared/plan_template.py`, `_shared/document_types/plan.toml` — a different artifact entirely) or
English prose in a docstring. The only code reading a spec clause is
`skills/yf-plan/scripts/test_cli_enumeration.py:199`.

**No harness parses `Verification:` generically** — not CHANGE-VALIDATION, not `_shared/*.py`, not
`yf/src/`, not `tests/`. This absence is load-bearing.

**measured:** #165's thesis confirmed by EXECUTION, not inference

Ten literal Verification commands were hand-run. **Two are FALSE today, in a FULL-tier-green tree:**

| Clause | What running it does |
| :-- | :-- |
| `skills/yf-optimal-instructions/spec/integration.md:51` | `ls skills/optimal-instructions/protocols/` → **No such file or directory** (stale pre-rename path) |
| `skills/yf-research/spec/prerequisites.md:42` | `grep -r … .agents/skills/yf-research/` → **No such file or directory** |

A third (`skills/yf-plan/spec/agents.md:7`) claims a grep "returns nothing" but returns one hit,
self-described as "except the prohibition itself" — unmechanizable as written.

**measured:** the prior art — `REQ-CLI-006`, and it is the ONLY clause containing the word "executed"

`skills/yf-plan/spec/cli.md:39` — *"Verification: **executed**, not asserted —
`skills/yf-plan/scripts/test_cli_enumeration.py` … registered as CHANGE-VALIDATION id
`uv-yf-cli-enum`"*.

```
$ uv run skills/yf-plan/scripts/test_cli_enumeration.py
6 passed in 0.02s     EXIT=0
```

Registered at `CHANGE-VALIDATION.md:80`, FULL at `:130`, fired by §3 globs on **both**
`skills/yf-plan/scripts/**` and `skills/yf-plan/spec/cli.md`. Three parts are worth copying:

1. it parses the REQ's **own prose** and asserts **set equality** against the code;
2. a **vacuity guard** (`assert len(spec) > 15`) so a spec reshape fails loudly instead of silently
   checking nothing;
3. `test_verification_line_names_an_executing_check` — asserts the Verification line still names
   this test. **This is the reusable meta-pattern**, and it is what makes the loop non-rottable.

**measured:** two more instances, both on the AGENT-PROSE axis this plan needs

- `skills/yf-herdr/scripts/test_launch_contract.py` (CV row `uv-herdr-launch`) asserts prose
  properties of `SKILL.md` **plus** SPEC-first REQ existence — *"the SPEC is fixed authority; a test
  asserting an unwritten requirement is the drift it exists to prevent."*
- `skills/yf-plan/scripts/test_gates.py:349` asserts prose **in an agent template**
  (`agents/red-team.md`) — the exact file #182 changes.

CV §3 already routes `skills/yf-plan/agents/*.md` → `uv-yf-gates` (`:206`) and
`skills/yf-plan/agents/**` → `uv-yf-review-verdict` (`:214`). **The wiring exists.**

**measured:** the coverage gate is a DIFFERENT mechanism — do not conflate

`yf/src/coverage.rs` parses `**REQ-YF-<AREA>-<NNN>** *(testable)*` from **root `SPEC.md` only**,
walks `yf/src/**.rs` for `// REQ-YF-…` comments. Three hard limits: **REQ-YF-\* prefix only, root
SPEC.md only, Rust comments only.** The entire `skills/*/spec/*.md` corpus — including every
`REQ-AGENT-*` this plan touches — is structurally invisible to it. Its own docstring is honest:
*"This proves a test names a REQ id, not that its assertions actually verify the requirement's
intent."*

Related: `CHANGE-VALIDATION.md:210` maps `skills/*/spec/*.md` → `cargo`, which is **vacuous for
skill specs** — `cargo test` runs `coverage.rs`, which reads a file the edit did not touch, and
passes.

**measured:** there is no documented convention for the inline clause

`skills/SPEC-TEMPLATE.md` §5 defines a **section-level** "Verification" heading, not the inline
per-REQ form the corpus actually uses. `CONTRIBUTING.md`: zero hits. The inline `Verification:` line
is an **undocumented, unenforced, organically-grown convention**.

**inferred:** the mechanism plan-051 needs is **not an invention** — three independent implementations by three
  different plans, two of them on the agent-prose axis, all currently green.
**inferred, uncorroborated:** cost — ~60–100 lines of pytest plus one CV §1 row and one or two §3 glob rows, both
  file classes already globbed.

## Implications for Plan

- **#165 stays in scope at instance level.** The "no prior art → drop to `exclude`" branch of the
  approach hypothesis is **refuted**.
- **The corpus-wide audit is NOT plan-051's.** 251 clauses at 0.4% executed is #165's own scope; this
  plan ships two executable REQs as the second and third data points and says so.
- **The cheap trap: naming a `test_*.py` in a Verification line is NOT execution.** Thirty clauses
  already do that and it buys nothing mechanically — the test can be renamed, deleted, or drift with
  no signal. `REQ-CLI-006` is the only one that closes the loop.
- **Word each REQ as a set/property assertion, never a count.** `REQ-CLI-006` drifted three times as
  a count and zero times as a set equality.

## Recommendations

1. **Keep #165 in scope at instance level** — ship two executable REQs; state in the plan that
   the corpus-wide audit stays #165's.
2. **Follow `uv-yf-cli-enum` verbatim as the template**: assert the agent-template prose property the
   REQ declares, assert the REQ id exists in the spec, assert the Verification line names this test,
   and carry a vacuity guard.
3. **Wire it as a CHANGE-VALIDATION §1 `fast` row** with §3 globs on **both** the spec file and
   `skills/yf-plan/agents/*.md`, so amending either side alone is a hard failure at the point of
   change. Both globs already exist.
4. **Never word a REQ as a count.** Set/property assertions only.

## Follow-on, NOT plan-051 work

The two measured-false Verification commands above are concrete one-line evidence for #165 and cost
nothing to fix. File them against #165 rather than fixing them here.
