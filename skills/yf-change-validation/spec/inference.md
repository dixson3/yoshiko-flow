# Spec: toolchain inference (bootstrap + drift re-proposal)

How the engine derives a draft recipe from the toolchain at **bootstrap** (`infer`) and detects
drift at **`check-drift`**. Both are operator-gated (the draft is inert until `§0 approved: yes`;
the re-proposal is propose-only). Repo-agnostic — the worked examples below are labelled examples,
not part of the contract.

## Requirements

**REQ-INFER-001: Precedence is CI `run:` steps > runner targets (just/make) > manifest defaults.**
When two sources describe the same check, the higher-precedence source wins on **flags**, and the
glob-scan wins on **what exists**:

- **CI `run:` steps win on flags.** `.github/workflows/*.yml` `run:` steps record exactly what the
  maintainer gates on, with precise flags — adopt them **verbatim**.
- **Runner targets** (`justfile` / `Makefile` `test`/`lint`/`check`/`build` targets) are the next
  source when CI is silent on a check.
- **Manifest-derived defaults** (the per-ecosystem mapping below) are the floor.
- **Glob-scan wins on what exists.** A suite or repo-check that *exists on disk* but **no** CI job
  runs (e.g. a pytest suite CI omits) is still inferred into FULL — CI's flags do not override the
  existence of an un-CI'd check.

Rationale: CI is the highest-fidelity record of intended flags, but it is frequently *incomplete*
(exp-003) — so existence, not CI, governs membership. Verification: where CI runs a check, the
inferred command matches the CI `run:` step; where a check exists but CI omits it, the inferred FULL
tier still contains it.

Per-ecosystem default mapping (the floor source, illustrative):

| Signal | Inferred commands |
|:--|:--|
| `Cargo.toml` (`[workspace]` ⇒ `--workspace`) | fmt `--check` · clippy `-D warnings` · test |
| `package.json` scripts | `npm ci` + the `test` / `build` / `lint` scripts present |
| `pyproject.toml` | project `pytest` · `ruff` (when configured) |
| `test_*.py` without `pyproject.toml` | per-file PEP-723 idiom (REQ-INFER-002) |
| `justfile` / `Makefile` | enumerated `test` / `lint` / `check` / `build` targets |
| repo `--check` scripts | the documented invocation, adopted verbatim |
| markers (e.g. opt-in lint) | wire the corresponding skill's check |

**REQ-INFER-002: PEP-723 per-file idiom.** A `test_*.py` carrying a **PEP-723 inline header** is
inferred to run **per-file** via `uv run` (`uv run <f>` when the header declares `dependencies`;
`uv run --with pytest python3 -m pytest <f> -q` / `uv run --script` for a header without inline test
deps). A `test_*.py` **without** a header runs via the **project pytest** idiom (a single
project-level pytest invocation). The engine **reads each header** — it cannot assume one pytest
command for the repo. Rationale: a repo can mix both idioms (exp-003 found two in this repo); a
single assumed command would mis-invoke half the suites. Verification: `infer` against fixtures with
and without PEP-723 headers emits the per-file vs project idiom accordingly.

**REQ-INFER-003: Skip disabled and tag-only CI jobs.** Inference **skips** any CI job/step that is
`if: ${{ false }}` (double-disabled) or runs only on tags (`on: [v*]` / tag filters) — these are
publish/opt-in jobs, not the change-validation gate. Rationale: adopting a disabled or
release-only job would put a never-run (or wrong-context) command in the recipe (exp-003: this
repo's `docs-deploy.yml` is double-disabled, `release.yml` is publish-only). Verification: `infer`
against a workflow fixture with an `if: false` job and a tag-only job omits both.

**REQ-INFER-004: Seed the FULL tier from an existing `validate-cmd` (the #27 migration clause).**
When `.yf-plan.local.json` contains a `validate-cmd`, `infer` seeds the FULL tier **from it** —
the existing operator-authored command becomes a FULL row (then augmented by the inferred CI ∪
repo-checks per REQ-INFER-005). Rationale: #27 supersedes the static `validate-cmd`; a clean
migration must not silently drop the validation the operator already configured. Verification:
`infer` with a `validate-cmd` present produces a FULL tier containing that command.

**REQ-INFER-005: FULL ⊇ CI ∪ repo-checks (the superset invariant, enforced at inference).** The
constructed FULL row set is the **union** of: the inferred CI `run:` steps (minus skipped jobs), the
discovered repo-checks (suites/`--check` scripts that exist on disk, including those CI omits), and
any seeded `validate-cmd`. FULL must not omit a member of CI **or** of repo-checks. Rationale: this
is REQ-SCHEMA-004 enforced at the point of construction; a CI-only FULL reproduces the plan-014
false-green (exp-003: this repo's `ci.yml` runs only cargo and omits the 6 pytest suites +
`_shared/sync.py --check`, the canonical standing example). Verification: the inferred FULL set ⊇
(CI step set ∪ discovered repo-check set).

## §2 fingerprint signals (what `check-drift` re-reads)

`infer` records, and `check-drift` re-parses, a per-signal `{source-path, parsed-value-or-hash}`
fingerprint (REQ-SCHEMA-005). Pure file-read + parse — no command execution. On any mismatch,
`check-drift` re-proposes the affected tier (operator-confirmed; never auto-rewrite —
`engine.md` REQ-ENGINE-006). Illustrative signal set:

| Signal | Cheap diff |
|:--|:--|
| Workspace members | recorded `members` vs current parse |
| CI `run:` steps | hash of extracted steps (skip `if:false`/tag-only) vs recorded |
| Test-suite set | `glob('**/test_*.py')` set-diff vs recorded |
| PEP-723 headers | per-file `requires-python` / `dependencies` presence diff (idiom flips) |
| Runner migration | presence-set diff of `justfile` / `Makefile` / `pyproject.toml` |
| `package.json` scripts | `scripts` keys diff |
| Markers | existence bit per opt-in marker |
| Repo `--check` scripts | discovered check-command set diff |

The recorded "FULL omits the suites CI omits" delta (REQ-INFER-005) is the canonical worked example
of a **standing** re-proposal — true the moment the manifest is seeded from a CI-only inference,
which is why seed-then-augment + re-propose is necessary, not speculative (exp-003).
