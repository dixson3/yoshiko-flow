# yf-plan Tier-2 test harness

Self-contained smoke harness for validating changes to the **yf-plan** skill against
the *reworked* lifecycle (plan-021). It exists because the repo source of the skill
is **decoupled** from the copy that actually runs.

## The two-copies / decoupling model

There are two distinct copies of every skill:

1. **Repo source** — `skills/yf-plan/` in this checkout. What you edit.
2. **Installed skill** — `~/.claude/skills/yf-plan/`. What `/yf-plan` actually runs.

Skills reach the resolver through `yf skills install`, which copies them out of the `yf`
binary's view of `skills/` (`yf/src/embed.rs` carries `#[folder = "../skills"]`). **Where
that view comes from depends on the build profile**, and the difference matters here:

- **Debug** (`cargo build`, the default and what this harness uses) — `rust-embed` is
  declared **without** `debug-embed`, so the binary reads `skills/` **from disk at runtime**.
  `./target/debug/yf` is therefore **always current**: a repo edit under `skills/` needs no
  rebuild to be deployed.
- **Release** (`cargo build --release`, what ships) — the tree is **baked in at compile
  time**. A repo edit needs a rebuild to reach the binary. The opt-in `embed-in-debug`
  feature turns debug into this mode so tests can exercise the shipping path.

Consequences for this harness:

- Editing `skills/yf-plan/` does **not** hot-swap an **already-installed** skill — the
  resolver reads the deployed copy under `<HOME>/.claude/skills`, not the repo.
- To exercise a repo edit, **re-install** (`yf skills install`) — then run the skill. A
  `cargo build` is needed only when `yf`'s own Rust code changed, **not** for skill edits.

## The resolver-shadowing hazard (RT2-1)

The skill resolves its own directory with (from `SKILL.md`):

```bash
SKILL_DIR=$(find ~/.claude/skills ~/.agents/skills \
  "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" \
  .claude/skills .agents/skills -maxdepth 1 -name yf-plan -type d 2>/dev/null | head -1)
```

`~/.claude/skills` is searched **first** and `head -1` wins. If the operator already
has `~/.claude/skills/yf-plan` installed (they do), then dropping a modified copy at a
scratch `<scratch>/.claude/skills/yf-plan` is **shadowed** — the resolver returns the
OLD installed copy and a smoke would silently validate the wrong skill.

### Fix: sandboxed HOME (primary route)

Set `HOME=<scratch-home>` for **every** step. Then `~` expands to the sandbox, so the
re-embedded/re-installed modified skill *is* the resolver's first hit:

```bash
HOME=<scratch-home> cargo build --manifest-path <repo>/yf/Cargo.toml   # re-embed ../skills
HOME=<scratch-home> <built-yf> skills install                          # → <scratch-home>/.claude/skills/yf-plan
HOME=<scratch-home> <run the smoke>                                     # resolver's 1st hit = modified copy
```

`bootstrap.sh` implements exactly this and **asserts** the resolved path is the sandbox
copy before proceeding.

### Alternatives (weaker — documented for completeness)

- **Shadow-aside the user install** — temporarily move `~/.claude/skills/yf-plan` out of
  the way so the scratch copy is the first hit. Mutates the operator's real home; easy to
  leave in a bad state. Avoid.
- **`yf skills install --target <scratch>/.claude/skills`** — installs the modified copy to
  an explicit dir, but that dir is **still after** `~/.claude/skills` in the resolver order,
  so it stays **shadowed unless HOME is also sandboxed**. Only safe when combined with the
  sandboxed HOME, at which point the plain default install already lands correctly — so the
  `--target` flag buys nothing here.

The sandboxed HOME is the only route that is both correct and non-destructive.

## The promotion boundary (Epic 0.3 / RT2-2)

"Promotion" = making the reworked skill the operator's **live** skill via
`cargo build` → `yf skills install` into the real `~/.claude`.

- plan-021's own execution runs **normally** on the operator's *current* installed skill,
  because — per the decoupling model — repo edits are **inert** with respect to the running
  skill until a rebuild+install. Editing `skills/yf-plan/` during the plan changes nothing
  live.
- **The one rule: do NOT promote (`yf skills install` into the real HOME) until the scratch
  smoke passes.** Validate in the sandbox first.
- Promotion is the **final land action**, sequenced at reconcile: rebuild (`cargo build`)
  then `yf skills install`. Until that rebuild+promote, the rework has **zero effect** on
  the live environment.

## Files

| File | Purpose |
| :-- | :-- |
| `bootstrap.sh` | Install the MODIFIED skill into an isolated sandbox HOME (building `yf` only if its Rust code changed); assert the resolver's first hit is the sandbox copy. |
| `smoke.sh` | `setup` a sandbox + throwaway bd-initialized git project; `verify` the new-lifecycle post-conditions and write `topology.txt`. |
| `topology.txt` | Acceptance artifact: observed `git branch -vv` + `git worktree list` + verdict. Consumed by the capability gate. Generated by `smoke.sh verify`. |

## Usage

```bash
# 1. Build the modified skill into a sandbox HOME and set up the scratch project.
skills/yf-plan/test-harness/smoke.sh setup            # default: mktemp sandbox HOME
#   → prints the sandbox HOME, the scratch project path, and the operator checklist.

# 2. Run the operator checklist (below) in a Claude Code session under that HOME.

# 3. Verify the lifecycle and capture topology.
skills/yf-plan/test-harness/smoke.sh verify <project-dir>
#   → writes skills/yf-plan/test-harness/topology.txt and prints PASS/FAIL.
```

`bootstrap.sh` is sourceable (`source bootstrap.sh <home>`) and leaves
`YF_SANDBOX_HOME` / `YF_SANDBOX_BIN` / `YF_SANDBOX_SKILL` in the environment.

## Operator checklist (the agent-driven walk)

The plan → execute → land walk needs the interactive `/yf-plan` skill (an agent) and is
**not** scriptable. `smoke.sh setup` prepares everything up to this point; run these steps
in a Claude Code session whose `HOME` is the sandbox printed by `setup`, then run
`smoke.sh verify`.

1. `export HOME="<sandbox-home>"` and `cd "<sandbox-home>/project"` (both printed by
   `setup`). This guarantees the **modified** skill fires, not the real `~/.claude` copy.
2. `/yf-plan smoke: trivial no-op plan` — drive intake through planning. Confirm the
   planning branch **`<plan-id>-development`** is created (not a bare `<plan-id>`).
3. Approve the plan. At APPROVE the skill must:
   - write a **`**Fingerprint:**`** header field into `plan.md`, and
   - **auto-commit** locally, scoped to `${plan_dir}` + `.beads/`, refusing on the
     default branch (so the commit lands on `<plan-id>-development`).
   (A later content edit to `plan.md` should then read as *stale-approved* vs. the
   fingerprint — spot-check if exercising that path.)
4. Land the plan per the configured `landing-strategy` in `.yf-plan.local.json`:
   - **`feature-branch`** → the planning branch lands onto feature branch `<plan-id>`.
   - **`main`** → it lands onto `main`.
5. `/yf-plan execute` — the execute worktree/branch **`<plan-id>-execute`** must be cut
   from the **pinned base** (`main` by default, or feature `<plan-id>`), **never** from
   `<plan-id>-development` (no branch-of-a-branch).
6. Drive the trivial epic to done and land it.
7. Back in a normal shell: `smoke.sh verify "<sandbox-home>/project"`.

### Post-conditions `smoke.sh verify` asserts (machine-checked)

- planning branch `<plan-id>-development` exists;
- execution branch `<plan-id>-execute` exists;
- `<plan-id>-execute` does **not** descend from `<plan-id>-development` (pinned base, no
  branch-of-a-branch);
- `landing-strategy` key present in `.yf-plan.local.json`; under `feature-branch`, the
  feature branch `<plan-id>` exists and is the ancestor (pinned base) of `<plan-id>-execute`;
- `plan.md` carries a `**Fingerprint:**` header;
- `topology.txt` records `git branch -vv`, `git worktree list`, and the verdict.
