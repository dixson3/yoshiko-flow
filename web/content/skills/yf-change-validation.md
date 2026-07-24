`yf-change-validation` runs a repository's recorded validation recipe — its build,
test, and lint commands — over a change-set or a merged tree, and reports **PASS**,
**FAIL**, or **INCONCLUSIVE** plus the first failing command. It **executes** commands
through a Python runner, so the verdict is an exit code, not a judgment. It never
auto-fixes a failing command and never auto-rewrites its own manifest.

The engine is fixed and carries no repo vocabulary. Each repository supplies a thin
markdown manifest, `CHANGE-VALIDATION.md` at its root, that is inferred from the
toolchain, operator-approved, then re-proposed when the toolchain drifts. Fire it by
invoking `/yf-change-validation`, or let it fire automatically: on edit of a file its
manifest scopes, and at pre-push or land-the-plane. If a repo has no approved manifest
the skill is a **silent no-op** — no check, no nag, no bootstrap on every edit.

## What it is not

This skill proves a change-set is *behaviorally* valid by running commands. Proving
that already-written artifacts *agree* across declared docs, spec, and implementation
edges is a different axis owned by `yf-drift-check`, a prose and LLM trigger with no
runnable command. The two are orthogonal and independent — neither invokes the other,
and `yf-drift-check` is excluded from every validation tier. A shared `.md` edit may
fire both on their own axes; that double-fire is expected and non-recursive.

## The manifest

`CHANGE-VALIDATION.md` lives at the repo root, read by the engine section by section:

| Section | Holds |
| :------ | :---- |
| §0 Status | the `approved: yes\|no` gate — inert until `approved: yes` |
| §1 Tiers | a `fast` and a `full` ordered command list, each a table of structured rows |
| §2 Signal Fingerprint | the toolchain signals the recipe was inferred from |
| §3 Trigger Scope | each changed-path glob mapped to the FAST command ids it selects |

A manifest is approved only if §0 reads `approved: yes`. A missing manifest and an
unapproved draft both count as no approved manifest. FULL is always built as the
superset of CI commands and repo checks.

## When it runs, and which tier

The trigger contract fires from an always-loaded companion rule:

- **No approved manifest** → silent no-op. A `run` invocation returns a structured
  `§0 approved: no` clean refusal — never a stack trace — so a delegating caller falls
  back without crashing.
- **On edit, changed path matches a §3 glob** → the **FAST** tier, scoped to the
  affected command ids that glob selects. This is the fast, per-edit check.
- **Pre-push or land-the-plane** → the **FULL** tier over the merged tree. This is the
  multi-minute gate paid once per land, not on every edit.

## Run-and-report semantics

The engine executes the selected tier's commands in row order and reports one verdict:

- **PASS** — every command in the tier exited 0.
- **FAIL** — the first non-zero exit, recorded as `first_failure` with an output tail.
  The engine stops there and never edits source to make a command pass.
- **INCONCLUSIVE** — a required tool is absent from `PATH`. The engine marks the
  command and the tier inconclusive rather than skipping it and calling the tier PASS.

That last case is deliberate. The engine **fails closed**: a missing tool is never a
false PASS. This is the contrast with a static validation command, which fails open.

## Infer, approve, enforce

Bootstrap happens only on explicit invocation or first install, never on an ordinary
edit. On `init` in a repo with no approved manifest:

1. **Infer a draft** — read the toolchain signals (CI `run:` steps, `justfile` or
   `Makefile` targets, `Cargo.toml` / `pyproject.toml` / `package.json`, PEP-723 test
   headers, repo `--check` scripts), construct the FAST and FULL tiers plus the §2
   fingerprint, and emit a draft manifest.
2. **Present** the draft. It is inert until approved — `approved: no` drives no
   enforcement.
3. **Operator approves** — set §0 to `approved: yes`, and the engine enforces it
   thereafter.

Inference is gated and propose-only throughout. The `check-drift` verb re-reads the
toolchain signals, diffs them against the recorded fingerprint, and emits a JSON
re-proposal — it never rewrites the manifest. Setting §0 back to `approved: no` is the
one-edit rollback lever that drops enforcement in a single change with no command run.
