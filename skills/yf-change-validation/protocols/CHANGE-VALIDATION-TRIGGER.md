# Change-Validation Trigger Protocol

Always-loaded firing surface for the `yf-change-validation` skill. The engine **executes** a
repo's recorded validation recipe (build / test / lint) and reports a verdict from an exit code —
so a `description` alone cannot reliably fire it; this rule binds the on-edit and pre-push triggers.
Procedure (the 4-section `CHANGE-VALIDATION.md` schema, infer→approve→enforce, run-and-report,
fail-closed) lives in the skill's `SKILL.md` and `spec/`; this rule binds only when the engine runs.

## Manifest detection

The per-repo recipe is `CHANGE-VALIDATION.md` at the repo root. It is **approved** only if its §0
Status reads `approved: yes`; a missing manifest or an unapproved draft (`approved: no`) both count
as **no approved manifest**.

## On-edit trigger (FAST tier)

After any create or modify of a file, if the repo has an **approved** `CHANGE-VALIDATION.md` and the
changed path matches one of its **Trigger Scope** (§3) globs, run the **FAST** (affected) tier scoped
to the ids that glob selects:

```bash
uv run "<skill-dir>/scripts/change_validation.py" run --tier fast --changed <changed-path> --json
```

Act on the verdict: FAIL → resolve before proceeding; INCONCLUSIVE (a required tool absent from
`PATH`) → surface to the operator. The engine never auto-fixes — repair is the operator's job.

## Pre-push / land-the-plane trigger (FULL tier)

On a pre-push or land-the-plane gate, if the repo has an **approved** `CHANGE-VALIDATION.md`, run the
**FULL** tier (the CI ∪ repo-checks superset) over the merged tree:

```bash
uv run "<skill-dir>/scripts/change_validation.py" run --tier full --json
```

FULL is the multi-minute gate paid once per land — not on every on-edit step.

The `check-drift` re-proposal (re-read toolchain signals, diff §2 fingerprint, emit a propose-only
JSON re-proposal — never rewrites the manifest) is active as part of the self-maintaining tier.

## Silent no-op

**Unless the repo has an approved `CHANGE-VALIDATION.md`** (§0 `approved: yes`), this trigger is a
**silent no-op** — do not check, prompt, nag, or offer to bootstrap. A `run` invocation against an
absent or unapproved manifest returns a structured `§0 approved: no` clean refusal (never a stack
trace), so a delegating caller falls back without crashing. Bootstrap is offered only on explicit
invocation (`/yf-change-validation init`) or first install, never on an ordinary edit.

## Carve vs `yf-drift-check`

`yf-change-validation` and `yf-drift-check` are **orthogonal, independent triggers** — neither
invokes the other:

- **yf-change-validation** proves a change-set is BEHAVIORALLY valid by *executing* commands (exit
  code = verdict).
- **yf-drift-check** proves already-written artifacts AGREE across declared docs/spec/impl edges (a
  prose/LLM judgment).

A shared `.md` edit may fire **both** skills on their own axes; that double-fire is expected and
**non-recursive**. `yf-drift-check` has no runnable command, so it is never a §1 recipe row — the
recipe is executable-only.

For the manifest schema, lifecycle, and run-and-report semantics, see the `yf-change-validation`
`SKILL.md` and `spec/`.
