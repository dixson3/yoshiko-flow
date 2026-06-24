# exp-001: `_shared/` package + vendoring mechanics (#15)

## Critical correction: no `install.py`/`install.sh`

The Python installer was **retired**. Installation is the `yf` Rust binary (`yf skills
install` / `yf skills upgrade`). So "vendored at install" cannot hook a Python installer.

## How install works (yf Rust)

- **Embed (build):** `yf/src/embed.rs:30-35` — `#[derive(RustEmbed)] #[folder = "../skills"]`
  compiles the whole `skills/` tree into the binary (excludes `*.pyc`/`__pycache__`). No
  transformation at embed time.
- **Skill enumeration:** authoritative set is `frontmatter::load_skills()`
  (`yf/src/frontmatter.rs:223-234`) — **a dir counts as a skill only if it has `SKILL.md`**.
  `embed::skill_names()` is laxer (any top dir) but selection flows through `load_skills`.
- **Deploy:** `common::deploy_skill()` (`yf/src/cmd/common.rs:100-134`) writes each embedded
  file **verbatim** (`std::fs::write`), the only transformation being a `SKILL.md` integrity
  marker (`marker::inject_marker`). `upgrade --prune` (`prune_extra_files`,
  `common.rs:139-154`) **deletes deployed files not in the embedded tree** — so any vendored
  copy must exist in the embedded tree or upgrade removes it.

## Two vendoring designs

- **(A) Deploy-time fan-out** (embed `_shared/`, copy into each skill's `scripts/` during
  `deploy_skill`): requires Rust changes to `deploy_skill`, the prune logic, and the
  deployed-vs-embedded integrity hash (`marker.rs`/`common.rs:489`). Higher risk.
- **(B) Repo-time sync, committed copies** (RECOMMENDED): canonical helpers in a top-level
  `_shared/`; a repo-time sync tool copies them into each consuming skill's `scripts/` as
  **committed** files; install copies them verbatim like any other script. **Zero `yf` Rust
  changes.** Matches the existing `e-classifier-copy` precedent exactly.

## DRIFT-CHECK edge pattern (the `e-classifier-copy` precedent)

- Nodes (`DRIFT-CHECK.md:46-47`): `classifier-canonical` (fixed authority) + `classifier-copy`
  (derived). Edge `e-classifier-copy` (`:79`), contract `value-equal` (`:111`) naming the
  exact symbols that must be body-identical. Trigger rows (`:155-156`) make editing **either**
  file fan out to the edge.
- **Manifest is pairwise only** — one Source, one Derived per edge. For one canonical → N
  skill copies, add **N edges** (`e-<helper>-copy-<skill>`), one node per copy, canonical =
  fixed authority; §6: canonical path scopes to all N edges, each copy path to its own.
- The current copy is **hand-pasted** (`upstream.py:122-269`), no sync script exists —
  DRIFT-CHECK is the only thing keeping it honest. plan-014's sync tool generalizes/retires it.

## Where `_shared/` lives

- **Top-level `_shared/` (repo root, NOT under `skills/`)** for option B: outside the
  `#[folder="../skills"]` embed root, so never mistaken for a skill; usable by a repo-time
  generator. (Under `skills/_shared/` it would be embedded but needs `#[exclude]` or guards on
  `skill_names()` callers — `common.rs:316,344`.)

## Recommendation

Option **B**: top-level `_shared/active_set.py`, `_shared/manifest_bootstrap.py`, etc.; a
repo-time sync tool fans them into consuming skills' `scripts/` as committed copies; DRIFT-CHECK
adds one canonical→copy edge per consumer. Retire the hand-pasted classifier copy by sourcing it
from `_shared/`. Zero Rust changes.
