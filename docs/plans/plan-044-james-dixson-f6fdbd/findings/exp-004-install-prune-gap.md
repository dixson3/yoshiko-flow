---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-install-prune-gap
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
---

# exp-004 — The skills install/upgrade prune gap (#155)

**Date:** 2026-08-17
**Question:** Why does a dropped skill file pin a skill at `modified` forever, and what shape should an opt-in `install --prune` take?
**Method:** source trace of `yf/src/cmd/{install,status,common}.rs` + `marker.rs`, then a **sandbox probe** driving the real release binary against a disposable `--target` dir. No repo files or real harness dirs written.

## The asymmetry, confirmed in code

| | multi-destination? | prunes? |
| :-- | :-: | :-: |
| `install` (`install.rs`) | **yes** — `common::resolved_dests` (`:38`), loops `for d in &dests` (`:64`) | **no** — `deploy_skill(…, /*prune=*/ false, …)` at **`install.rs:66`** |
| `upgrade` (`status.rs`) | **no** — `common::dirs_for` (`:72`), *"the primary of the effective set"* (`common.rs:588-607`) | **yes** — `prune=true` at `status.rs:87-92` |

`SkillsArgs::primary_harness` (`cli.rs:425-430`) defaults to `claude-code` when empty.

**Related blindness:** `yf doctor` is hardcoded to one surface —
`common::dirs_from(Scope::User, "claude-code")` (`doctor/mod.rs:51`) — so doctor cannot see
`~/.agents/skills` at all, and its remediation string points at the single-destination verb.

## The prune engine is correct — only the call site is missing

`prune_extra_files` (`common.rs:153-168`), called from `deploy_skill` (`:119-121`) before the
write loop. Removable = any file under the deployed skill dir not in `embed::skill_files(name)`,
then `remove_empty_dirs`.

**Blast radius is narrow but real:** scoped to `skills_dir/<transformed-name>` per *selected*
skill. A foreign skill directory (`herdr/`, `naba/`) or a stray file at the skills-dir root is
never walked. It does **not** delete a dir for a de-embedded skill, nor an old dir after a rename.

**No allowlist, no provenance, no mtime check.** A hand-authored `MY_NOTES.md` inside a yf skill
dir is indistinguishable from a dropped embedded file and **is deleted** — measured below.

**Adjacent reporting bug:** `extra_deployed_files` (`common.rs:172-183`) does
`skills_dir.join(name)` with the **untransformed** name, while the real prune path
(`deploy_skill`, `:112-115`) *is* transform-aware. So `--dry-run --harness pi` **under-reports the
prune set to empty** while a real run would prune. A preview that lies is worse than no preview —
fix this in the same change-set; it is a prerequisite, not a nice-to-have.

## Sandbox probe (measured, real release `yf 0.4.0 (0d900b1)`, disposable `--target`)

1. `install yf-markdown-lint --target <sbx>` → `ok`.
2. Seeded three extras: `scripts/__pycache__/foo.cpython-314.pyc`, `DELETED_FILE.md` (a dropped
   embedded file), `MY_NOTES.md` (an operator file).
3. `status` → `up_to_date:true, complete:true, unmodified:false, state:"modified"`.
4. **Re-running `install` did not fix it** — byte-identical status. *#155 reproduced directly.*
5. `upgrade --dry-run --json` → `"pruned":[DELETED_FILE.md, MY_NOTES.md, __pycache__/foo…pyc]`
   — preview accurate, **and it includes the operator file**.
6. `upgrade` (real) → all three gone, embedded files intact, `state:"ok"`.

**The engine works; the gap is the call site and the flag. The operator-file hazard is confirmed,
not theoretical.**

## The measured residue on this machine is NOT #155's failure mode

`~/.claude/skills`: 19 skills, **1 not-ok** — `yf-plan | modified`. `~/.agents/skills`: **0 not-ok**.
Deployed-vs-embedded diff for the offender (additions only):

```
scripts/__pycache__/okf.cpython-314.pyc
scripts/.pytest_cache/{.gitignore,CACHEDIR.TAG,README.md,v/cache/nodeids}
test-harness/.scratch/sandbox.env
test-harness/topology.txt
```

All 7 are **runtime residue** (pycache, pytest cache, test-harness scratch) — because this is the
dev machine that runs the skills' own harness. `~/.agents` is clean precisely because nothing
executes from there.

**`embed.rs:48-50` excludes `*.pyc`/`__pycache__/**` from the *embed*, but skills run `uv run`
from the *deployed* dir, which regenerates them there.** `marker.rs:105-125 walk_files` has **no
ignore list of any kind** — no `__pycache__`, `.pyc`, `.pytest_cache`, `.DS_Store`, dotfile
handling. So the hash counts them.

> **Consequence for the success criterion:** `--prune` would clear these, and they would come
> **straight back** on the next `uv run`. If the plan's criterion is *"`yf doctor` stays green"*,
> the flag alone does not deliver it — that needs an ignore-list REQ (or #153's
> `PYTHONPYCACHEPREFIX`). `--prune` is a one-shot; the residue regenerates.

## Design surface

- **Flag parse:** `SkillsArgs` (`cli.rs:331-405`) is **shared by all four `skills` subcommands**;
  adding `--prune` exposes it on `status`/`remove` (inert) and `upgrade` (redundant). Two test
  literals must gain the field (`install.rs:347-364`, `common.rs:815-832`).
- **Fan-out is one line** at `install.rs:66`. Because install already loops `resolved_dests`,
  prune becomes multi-destination **for free** — that is the whole reason to hang it on install
  rather than fix upgrade.
- **Safety gate, report-first:** compute `extra_deployed_files` per destination *before* writing
  and emit as `"pruned"`; install's `--dry-run` block (`:134-154`) computes **no** extras today,
  so `--prune --dry-run` would report nothing. Fix the transform bug first.
- **Precedent for a destructive opt-in with preview — three exist:** `upgrade --dry-run`
  (measured to agree exactly with the real run); **`yf doctor --prune-formulas`** (`cli.rs:461`,
  `doctor/mod.rs:216-282`) — *"its OWN affordance, distinct from `--repair`"*, **provenance-gated
  by a yf-owned staged marker**, no-op when the marker is absent (the strongest precedent, and the
  pattern that would properly close the `MY_NOTES.md` hazard); and `--allow-permissions-write`'s
  per-key delta.
- **Do NOT wire `--prune` into the install-time sync** (`self_cmd/sync.rs:156-175`) in the same
  change-set — it would silently delete operator files on every `yf self install`. Ship opt-in
  first; decide sync adoption separately.

## SPEC

Existing: REQ-YF-MARK-001 (`SPEC.md:724-726`, hash over every file, **no exclusion clause** —
which is why `__pycache__` counts), REQ-YF-MARK-003 (`:729-731`), REQ-YF-MARK-004 (`:732-733`,
prune assigned to `upgrade` **only**), REQ-YF-INSTALL-001 (`:617-621`, *"writes skill bodies
only"* — **silent on removal**; the gap is a SPEC gap first), REQ-YF-INSTALL-002 (`:622-629`,
the dedupe-by-resolved-path guarantee `--prune` inherits).

Proposed:

- **New `REQ-YF-INSTALL-010`** — `install --prune` shall, for **every** resolved destination,
  remove deployed files absent from the embedded tree and then newly-empty dirs, using the same
  engine as REQ-YF-MARK-004. **Off by default.** Scoped to selected skills' dirs only.
  `--dry-run --prune` shall report the exact set, **transform-correct** (REQ-YF-INSTALL-007).
- **Amend REQ-YF-MARK-004** — prune is default-on for `upgrade`, opt-in for `install`, one impl.
- **Optional `REQ-YF-MARK-005`** — exclude tool-generated paths (`__pycache__/**`, `*.pyc`,
  `.pytest_cache/**`, `.DS_Store`) from the tree hash. **This is the only requirement that
  actually fixes this machine's measured state.** Must apply symmetrically to
  `extra_deployed_files`/`prune_extra_files` or prune and hash disagree.

**Tests to pin** (extend `yf/src/marker_tests.rs`, which already holds
`req_yf_mark_004_prune_removes_stray_keeps_embedded` `:124-165`): (a) a hand-added **skill
directory** survives a `--prune` install; (b) prune fans out to **both** destinations of a
two-harness install; (c) `extra_deployed_files --harness pi` reports the transformed path.
