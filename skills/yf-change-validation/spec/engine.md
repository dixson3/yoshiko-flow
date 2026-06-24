# Spec: engine behavior (no-op, lifecycle, run-and-report, fail-closed, rollback)

The fixed engine mechanism: when it stays silent, the infer→approve→enforce lifecycle, how it runs
and reports, why it fails **closed**, how it re-proposes on drift, and the `§0 approved: no`
rollback lever. Repo-agnostic. Unlike `yf-drift-check`, this engine **executes** commands (a Python
runner), so the verdict is an exit code, not an LLM judgment.

## Requirements

**REQ-ENGINE-001: No approved manifest ⇒ silent no-op / clean refusal.** A repo with
change-validation installed but no approved `CHANGE-VALIDATION.md` does nothing on an on-edit
trigger: no check, no nag, no bootstrap prompt. A `run` invocation against an unapproved or absent
manifest returns a **structured clean refusal** (a `§0 approved: no` result object) — **never a
stack trace**. Rationale: the engine must not impose on repos that have not opted in (mirrors
drift-check REQ-ENGINE-001 and the UPSTREAM_TRACKING silent-no-op clause); a clean refusal lets the
yf-plan seam fall back without crashing. Verification: with no approved manifest, an on-edit trigger
produces no output and `run --json` returns the refusal object with exit code reserved for "not
approved" (distinct from a FAIL exit).

**REQ-ENGINE-002: A manifest is inert until `§0 approved: yes`.** Bootstrap writes a draft with
`approved: no`; the draft does not drive enforcement until the operator edits §0 to `approved:
yes`. Rationale: the engine executes recorded commands — enforcing an unreviewed inferred recipe is
a code-exec risk. Verification: a draft manifest without `approved: yes` is treated as "no approved
manifest" (REQ-ENGINE-001).

**REQ-ENGINE-003: The engine follows an infer→approve→enforce lifecycle and never invents a command
at run time.** Inference (bootstrap) and drift re-proposal (`check-drift`) are the **only** points
where the engine derives commands from the toolchain, and both are **operator-gated**. At run time
the engine executes **exactly** the commands the approved manifest records — it never reads the
toolchain to synthesize a command on the fly. Rationale: separating inference (gated, propose-only)
from enforcement (executes recorded recipe) is what makes the recipe auditable; a run-time inferred
command would be an unapproved command (red-team). Verification: `run` reads only §0–§3 of the
approved manifest; it does not parse `Cargo.toml`/CI/etc.

**REQ-ENGINE-004: Run-and-report — PASS/FAIL + the failing command; never auto-fix.** `run`
executes the selected tier's commands **in row order** (each via `sh -c` in its `cwd`, bounded by
`timeout`), and returns PASS only if **every** command exits 0. On the **first** non-zero exit it
records that command as `first_failure` (with a tail of its output) and returns FAIL. The engine
**never** edits source to make a command pass. Rationale: it validates *behavioral* validity by
executing build/test/lint; repair is the operator's job (propose-not-fix posture). Verification: a
tier with one failing command returns `status: fail` naming that command; no source file is
mutated.

**REQ-ENGINE-005: Fail-closed — a missing required tool is INCONCLUSIVE, never a false PASS.** When
a command's required tool is absent from `PATH` (checked by an inlined ~10-line `tool_on_path` /
`command -v`), the engine marks that command **INCONCLUSIVE** and the tier result INCONCLUSIVE — it
does **not** skip the command and call the tier PASS. Rationale: this is the exact contrast with the
static `validate-cmd`, which **fails open** (an absent/rotted command validates nothing yet looks
green) — the failure mode #27 indicts. A false pass is worse than a known-unknown. Verification: a
tier whose command needs an absent tool returns `status: inconclusive`, distinct from `pass` and
`fail`.

**REQ-ENGINE-006: Re-propose on drift; never auto-rewrite the manifest.** `check-drift` re-reads
the toolchain signals, diffs them against the recorded §2 fingerprint, and emits a **re-proposal**
(added / removed / changed signals + the proposed tier delta) for the operator to confirm. It
**never** rewrites `CHANGE-VALIDATION.md`. Rationale: the self-maintaining property a static
`validate-cmd` lacks, kept propose-only to match the repo's propose-not-fix posture
(yf-drift-check / yf-optimal-instructions). Verification: `check-drift` writes nothing; the
re-proposal is JSON the operator applies (or not).

**REQ-ENGINE-007: `§0 approved: no` is the rollback lever.** A single edit — set §0 to `approved:
no` — drops yf-plan's §6.1.5 layer-(b) delegation **straight back** to `validate-cmd` (and then to
the verbatim not-checked notice when no `validate-cmd` either), with **no** engine command run.
Rationale: a buggy or flaky engine could otherwise wedge every land-the-plane once delegation + an
approved manifest exist; the operator needs a one-edit escape that does not require uninstalling the
skill (red-team M1). Verification: with the seam wired (D.1), flipping §0 to `no` makes
`_validate_merged` skip the engine and use the next fallback tier; the output schema is unchanged.

**REQ-ENGINE-008: Route as a skill — zero `yf` Rust changes.** The engine is a `skills/`-embedded
Python script (`scripts/change_validation.py`) plus an always-loaded protocol rule; it adds **no**
`yf` subcommand. yf-plan delegates via a **prose soft-dep** (present → delegate; absent → fallback),
**never** a frontmatter `depends-on-skill` edge. Rationale: the crate's GR-005 kernel/skill boundary
— validation logic lives in the skill layer, not the Rust kernel (exp-002). Verification: `git
grep` finds no new `yf` subcommand for this engine; the data-driven `skills/*/protocols/*`
aggregation picks up the rule with `yf preflight`/install parity green.

**REQ-ENGINE-009: The engine carries no repo vocabulary.** No repo-specific command strings, tool
names, globs, or paths appear as load-bearing references in `SKILL.md`, `spec/`, or `scripts/`; all
of that lives in the per-repo `CHANGE-VALIDATION.md`. Rationale: the engine/manifest split is what
makes the skill portable (mirrors drift-check REQ-ENGINE-006). Verification: grep the engine for
repo-specific tokens (`cargo`, `pytest`, `_shared/sync.py`, `skills/<skill>/`) → none as
load-bearing references; illustrative examples in prose are permitted but must be labelled.

## Out of scope (honest limits — REQ-ENGINE-010)

- **Auto-fix.** The engine runs and reports; it never repairs a failing command.
- **Auto-rewrite.** `check-drift` proposes; it never edits the manifest.
- **Driving `yf-drift-check`.** The recipe is executable-only; `yf-drift-check` is a prose/LLM
  trigger with no script (exp-001), fires on its own orthogonal trigger, and is **excluded** from
  every tier. The two skills are independent, non-recursive triggers (change-set validity by
  *executing* commands vs content agreement); neither invokes the other.
- **A `yf` Rust subcommand.** Routing is skill-layer only (REQ-ENGINE-008).
