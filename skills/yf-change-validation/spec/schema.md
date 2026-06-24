# Spec: manifest schema

The fixed, repo-agnostic contract for a repo's `CHANGE-VALIDATION.md` manifest. The engine parses
a manifest conforming to this schema **mechanically**; nothing here names a repo-specific command,
tool, or path. Mirrors `DRIFT-CHECK.md`'s "markdown the engine reads by section" model, but the
recipe is **executable** (shell commands whose exit code is the verdict), not prose.

## Requirements

**REQ-SCHEMA-001: A manifest is markdown with exactly four sections, in order.**
The four `##` sections are §0 Status, §1 Tiers, §2 Signal Fingerprint, §3 Trigger Scope. Rationale:
a fixed, ordered, named section set lets the engine read each by heading with no DSL. Verification:
the four headings below are present in order; the engine reads each by name.

The four sections:

0. **Status** — the `approved: yes|no` gate. The engine is a **silent no-op** on an on-edit
   trigger, and `run` returns a **clean refusal** (a structured `§0 approved: no` result, never a
   stack trace), unless this reads `approved: yes` (REQ-ENGINE-001/002).
1. **Tiers** — the `fast` and `full` ordered command lists, each a table of structured command rows
   (REQ-SCHEMA-002/003/004).
2. **Signal Fingerprint** — `source-path | parsed-value-or-hash` rows; the per-signal `{source,
   hash}` fingerprint of the toolchain signals the recipe was inferred from (REQ-SCHEMA-005).
3. **Trigger Scope** — `changed-path glob | FAST command ids` rows; the affected-scoping map
   (REQ-SCHEMA-006/007).

**REQ-SCHEMA-002: §1 defines a `fast` and a `full` ordered command list; each command is a
structured row.** Each tier is a markdown table; the row order **is** the run order. Columns:

| Column | Required | Meaning |
|:--|:-:|:--|
| `id` | optional | a short stable identifier referenced by §3 (affected-scoping). Omit for FULL-only rows that no §3 glob selects. |
| `cmd` | **yes** | the shell command string. Run **via shell** (`sh -c`) so the PEP-723 two-idiom (`uv run --script` vs project pytest) and the `cd website && …` cases work as written. |
| `cwd` | optional | working directory the `cmd` runs in (relative to repo root); defaults to repo root. |
| `timeout` | optional | seconds; the engine kills the command after this and marks it FAIL — a hung test must not wedge land-the-plane. |

Rationale: a structured row (not a bare string) lets the engine scope by `id`, set a working
directory, and bound runtime. Running via shell keeps the recipe author's exact invocation intact.
Verification: every §1 table row has a non-empty `cmd`; `id`/`cwd`/`timeout` parse as
identifier/path/positive-integer when present.

Example table shape (illustrative — values are repo-specific, supplied by inference, not by this
spec):

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
| `<id>` | `<shell command>` | `<dir or blank>` | `<seconds or blank>` |

**REQ-SCHEMA-003: The recipe is executable-only — every §1 row is a runnable shell command.**
`yf-drift-check` (and any other prose/LLM trigger) **never** appears as a row: it is not a shell
command, it fires on its own orthogonal trigger, and listing it would create a double-fire on a
shared `.md` edit. Rationale: the engine's verdict **is** the exit code; a non-command row has no
exit code (exp-001; red-team C5). Verification: no row's `cmd` names `yf-drift-check` or another
non-executable trigger; every `cmd` is a shell string the engine can `sh -c`.

**REQ-SCHEMA-004: FULL is a superset of CI ∪ repo-checks.** The FULL tier must not omit a suite
that CI runs **or** a repo-check that CI omits (e.g. a pytest suite or a `--check` script CI does
not run). Rationale: a CI-only FULL tier reproduces the plan-014 false-green gap (CI omitted the
pytest suites and the vendoring `--check`); FULL is the cross-plan safety net and must be complete
(exp-003). Verification: at inference time, the constructed FULL row set ⊇ the CI `run:` step set ∪
the discovered repo-check set (REQ-INFER-005).

**REQ-SCHEMA-005: §2 records a per-signal `{source-path, parsed-value-or-hash}` fingerprint.**
One row per toolchain signal the recipe was inferred from; the value is either the parsed value
(e.g. workspace `members`) or a stable hash (e.g. of extracted CI `run:` steps). Reading and
comparing the fingerprint is **pure file-read + parse** — no command execution — so `check-drift`
is cheap enough for an on-edit trigger. Rationale: drift detection mirrors drift-check's firing
model (read, don't run). Verification:

| source-path | parsed-value-or-hash |
|:--|:--|
| `<signal source>` | `<parsed value or hash>` |

each row's source-path resolves; the value is reproducible by re-parsing the source.

**REQ-SCHEMA-006: §3 maps each changed-path glob to the subset of FAST command ids it selects.**
Affected-scoping: `run --tier fast --changed <paths>` runs only the **union** of the ids every
matched glob selects; with **no** `--changed`, `run --tier fast` runs the **whole** FAST tier.
Rationale: on-edit checks must be cheap and local; only the affected subset runs (exp-003).
Verification:

| changed-path glob | scopes to (FAST ids) |
|:--|:--|
| `<glob>` | `<id>[, <id> …]` |

a changed path matching `<glob>` selects exactly the listed FAST ids.

**REQ-SCHEMA-007: The manifest is referentially closed — every §3 id names a §1 FAST row that
exists.** Rationale: a §3 glob selecting a non-existent id would silently scope to nothing (a
false-green affected run). Verification: cross-check every §3 id against §1 FAST row `id`s.

**REQ-SCHEMA-008: A manifest is inert until approved.** Inference/bootstrap drafts a manifest with
`§0 approved: no`; an unapproved draft must not drive enforcement. Rationale: the engine executes
recorded commands — running an unreviewed inferred recipe is a code-exec risk. Verification: see
`engine.md` REQ-ENGINE-001/002 (the §0 gate).
