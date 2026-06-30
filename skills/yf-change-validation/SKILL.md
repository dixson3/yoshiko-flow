---
name: yf-change-validation
description: "Runs a repo's recorded VALIDATION RECIPE (build/test/lint) over a change-set or
  merged tree by EXECUTING the commands and reporting PASS / FAIL / INCONCLUSIVE + the first
  failing command; never auto-fixes and never auto-rewrites the manifest. Driven by a per-repo
  CHANGE-VALIDATION.md inferred from the toolchain, operator-approved, then re-proposed on
  drift. TRIGGER when: /yf-change-validation invoked; a file covered by an approved
  CHANGE-VALIDATION.md §3 glob is created or modified (run the FAST tier); a pre-push /
  land-the-plane FULL-tier validation; or a manifest is being bootstrapped on first install.
  SKIP for: repos with no approved CHANGE-VALIDATION.md (silent no-op — no nag, no bootstrap on
  every edit); any request to FIX a failing command rather than report it; checking CONTENT
  AGREEMENT across docs/spec/impl edges — that is yf-drift-check (a prose/LLM trigger), an
  orthogonal axis this engine never invokes. Distinguishing axis: yf-change-validation proves a
  change-set is BEHAVIORALLY valid by running commands (exit code = verdict); yf-drift-check
  proves already-written artifacts AGREE. Neither invokes the other."
user-invocable: true
skill-group: utility
depends-on-tool: [uv]
depends-on-skill: []
allowed-tools:
  - Read
  - Grep
  - Bash
  - Edit
title: yf-change-validation
created: '2026-06-24'
tags: []
---

# yf-change-validation

Repo-agnostic engine that runs a repo's **recorded validation recipe** (build / test / lint)
over a change-set or merged tree and reports **PASS / FAIL / INCONCLUSIVE** plus the first
failing command. Unlike `yf-drift-check` (prose + a read-only LLM sub-agent), this engine
**executes** commands via a Python runner — the verdict is an exit code, not an LLM judgment.

The engine is fixed and carries no repo vocabulary. Each repository supplies a thin **markdown
manifest** (`CHANGE-VALIDATION.md` at the repo root) — **inferred from the toolchain**,
**operator-approved**, then **re-proposed when the toolchain drifts**. The engine reads that
manifest, executes the selected tier's commands in row order, and reports the result. It never
auto-fixes a failing command and never auto-rewrites the manifest.

The contract is split in two — fixed engine, per-repo config:

| Fixed (this skill) | Per-repo (`CHANGE-VALIDATION.md`) |
|:--|:--|
| `SKILL.md` (this file), `spec/`, `scripts/change_validation.py`, the trigger rule | the recipe: §1 fast/full tiers, §2 signal fingerprint, §3 trigger-scope globs |

Authoritative behavior lives in `spec/` — `schema.md` (the 4-section manifest schema +
structured tier rows), `engine.md` (silent no-op, infer→approve→enforce lifecycle,
run-and-report, fail-closed, re-propose-on-drift, the `§0 approved: no` rollback lever),
`inference.md` (toolchain inference precedence, the PEP-723 per-file idiom, the FULL-superset
invariant, the `validate-cmd` seed). This file is the operational summary; on any discrepancy,
`spec/` wins.

## SKILL_DIR

```bash
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
SKILL_DIR=$(find ~/.claude/skills ~/.agents/skills "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" .claude/skills .agents/skills -maxdepth 1 -name yf-change-validation -type d 2>/dev/null | head -1)
[ -z "$SKILL_DIR" ] && { echo "ERROR: yf-change-validation skill directory not found"; exit 1; }
```

## Manifest detection

The per-repo manifest is `CHANGE-VALIDATION.md` at the repo root (its canonical home — it is
on-demand config, not an `@`-included rule, so it does not belong in a rules surface).

```bash
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
MANIFEST="$GIT_ROOT/CHANGE-VALIDATION.md"
```

A manifest is **approved** only if its §0 Status reads `approved: yes`. A missing manifest or
an unapproved draft (`approved: no`) both count as **no approved manifest**.

## Invocation

```
/yf-change-validation <subcommand>
```

| Subcommand | Purpose |
|:--|:--|
| `infer` (bootstrap) | infer a draft `CHANGE-VALIDATION.md` from the toolchain, present it, await operator approval (infer → approve → enforce); `--write` writes the draft to the repo root instead of stdout |
| `run --tier fast\|full [--changed <paths>]` | parse the **approved** manifest, execute a tier (affected-scoped when `--changed`), report PASS / FAIL / INCONCLUSIVE + first failure |
| `check-drift` | re-read toolchain signals, diff against the recorded §2 fingerprint, emit a JSON re-proposal — never rewrites the manifest |

All three route to `scripts/change_validation.py` (below). `run` is the enforcement surface;
`infer` and `check-drift` are the operator-gated inference surfaces.

## When this runs

Fires from the always-loaded `protocols/CHANGE-VALIDATION-TRIGGER.md`:

- **No approved manifest** → **silent no-op** (REQ-ENGINE-001). No check, no nag, no bootstrap
  prompt. A `run` invocation returns a **clean refusal** (a structured `§0 approved: no` result,
  never a stack trace) so a delegating caller falls back without crashing. Stop.
- **Approved manifest, on-edit, changed path matches a §3 glob** → run the **FAST** (affected)
  tier scoped to the matched ids.
- **Approved manifest, pre-push / land-the-plane** → run the **FULL** tier on the merged tree.

Bootstrap (below) is offered **only** on explicit invocation or first install — never on an
ordinary edit (REQ-ENGINE-003).

## Bootstrap (infer → approve → enforce)

On explicit `init` in a repo with no approved manifest:

1. **Infer a draft** — run `change_validation.py infer` to read the toolchain signals (CI
   `run:` steps, `justfile` / `Makefile` targets, `Cargo.toml` / `pyproject.toml` /
   `package.json`, `test_*.py` PEP-723 headers, repo `--check` scripts), construct the `fast`
   and `full` tiers + the §2 fingerprint, and emit a draft `CHANGE-VALIDATION.md` (filling
   `templates/manifest.md`). FULL is built as **CI ∪ repo-checks** (the superset invariant); an
   existing `validate-cmd` in `.yf-plan.local.json` seeds FULL (the #27 migration clause).
2. **Present** the draft to the operator. It is **inert until approved** (`§0 approved: no`) —
   it does not drive enforcement.
3. **Operator approves** → set §0 `approved: yes`. The engine enforces it thereafter.

Never enforce an unapproved draft; the engine **never invents a command at run time** — at run
time it executes exactly the commands the approved manifest records.

## Dispatch / engine call

Resolve `SKILL_DIR` (above), then invoke the Python engine via `uv run` (PEP-723 inline deps):

```bash
uv run "$SKILL_DIR/scripts/change_validation.py" run --tier fast --changed <paths> --json
uv run "$SKILL_DIR/scripts/change_validation.py" run --tier full --json
uv run "$SKILL_DIR/scripts/change_validation.py" infer
uv run "$SKILL_DIR/scripts/change_validation.py" check-drift --json
```

`run --json` returns `{tier, status: pass|fail|inconclusive, commands:[{id, cmd, ok,
returncode, output_tail}], first_failure}` and exits non-zero on FAIL (a reserved exit code
distinguishes the `§0 approved: no` clean refusal from a real FAIL).

## Run-and-report semantics

- **PASS** — every command in the tier exited 0.
- **FAIL** — the first non-zero exit; the engine records it as `first_failure` (with an output
  tail) and stops reporting that tier failed. It **never** edits source to make a command pass.
- **INCONCLUSIVE** (fail-closed) — a required tool is absent from `PATH`; the engine marks the
  command and the tier INCONCLUSIVE rather than skipping it and calling the tier PASS. This is
  the deliberate contrast with a static `validate-cmd`, which **fails open**.
- **`§0 approved: no` refusal** — an unapproved or absent manifest yields a structured clean
  refusal, never a stack trace.

Setting **`§0 approved: no`** is the **rollback lever**: it drops yf-plan's §6.1.5 layer-(b)
delegation straight back to `validate-cmd` (then the not-checked notice) in a single edit, with
no engine command run.

## Carve vs yf-drift-check

The two skills are **orthogonal, independent triggers** — neither invokes the other:

| Concern | Owner |
|:--------|:------|
| Is a change-set BEHAVIORALLY valid? (run build/test/lint — exit code = verdict) | **yf-change-validation** |
| Do already-written artifacts AGREE across declared docs/spec/impl edges? | yf-drift-check |

`yf-drift-check` is a prose/LLM trigger with no runnable command, so it is **excluded from every
tier** — it never appears as a §1 row. A shared `.md` edit may fire **both** skills on their own
orthogonal axes; that double-fire is expected and **non-recursive** (change-set validity vs
content agreement). The recipe is **executable-only**.

## File layout

Some files are created by sibling beads of plan-015 — forward references are fine.

```
skills/yf-change-validation/
├── SKILL.md                          # engine: this file (operational summary)
├── README.md                         # human-facing overview
├── SPEC.md                           # the requirement-numbered (REQ-CHGVAL-*) per-skill spec
├── spec/
│   ├── schema.md                     # the 4-section CHANGE-VALIDATION.md schema + structured tier rows (REQ-SCHEMA-*)
│   ├── engine.md                     # no-op, infer→approve→enforce, run-and-report, fail-closed, re-propose, rollback (REQ-ENGINE-*)
│   └── inference.md                  # toolchain inference precedence, PEP-723 per-file idiom, FULL-superset, validate-cmd seed (REQ-INFER-*)
├── scripts/
│   └── change_validation.py          # the Python engine: infer / run / check-drift (PEP-723, uv run --script)
├── templates/
│   └── manifest.md                   # the blank CHANGE-VALIDATION.md draft (inert approved: no)
└── protocols/
    └── CHANGE-VALIDATION-TRIGGER.md  # always-loaded on-edit (FAST) + pre-push (FULL) firing surface
```

## Route as a skill (zero Rust)

The engine adds **no `yf` Rust subcommand** — it is a `skills/`-embedded Python script plus an
always-loaded protocol rule (the crate's GR-005 kernel/skill boundary). yf-plan delegates to it
via a **prose soft-dep** (approved manifest present → delegate; absent → `validate-cmd`
fallback), **never** a frontmatter `depends-on-skill` edge.

## Rules

- The engine carries **no repo vocabulary** — all commands / tools / globs / paths live in the
  per-repo `CHANGE-VALIDATION.md`. Illustrative prose examples are fine; load-bearing references
  are not.
- **Run and report, never fix.** The engine reports PASS / FAIL / INCONCLUSIVE; the operator
  applies any correction.
- **Fail closed.** A missing required tool is INCONCLUSIVE, never a false PASS.
- **Silent no-op** without an approved manifest. Bootstrap only on explicit invoke / first
  install; `run` returns a clean refusal.
- **Inference is gated and propose-only.** `infer` and `check-drift` never enforce and never
  rewrite the manifest; the operator approves.
- `spec/` is authoritative; if this file and `spec/` disagree, `spec/` wins.
