# TESTING — deep/integration strategy for manager-script skills

How to validate behavior changes in the **manager-script skills** — `yf-plan`
(`plan_manager.py`) and `yf-research` (`research_manager.py`) — whose orchestration is
driven by a Python CLI of verbs. Settled on during plan-021 (yf-plan lifecycle rework).

## The core problem: repo source ≠ running skill

The repo source under `skills/<skill>/` is **decoupled** from the copy that actually runs.
Skills are `rust-embed`-baked into the `yf` binary **at build time** (`cargo build`,
`yf/src/embed.rs` `#[folder = "../skills"]`) and deployed by `yf skills install` into
`~/.claude/skills/<skill>/`. Consequences:

- Editing `skills/<skill>/…` does **not** hot-swap the running skill — so a plan/research
  executing *its own* rework is safe (no self-modification mid-run).
- But validating an edit by exercising the **installed** copy tests the **old** skill — a
  false green. You must exercise the **modified repo copy**.

## Two tiers

### Tier-1 — unit tests of the manager script (fast, per-edit)

`skills/<skill>/scripts/test_<manager>.py` imports the manager module directly (it is a
PEP-723 script, loaded via `importlib`) and asserts verb mechanics in throwaway git repos /
temp dirs, monkeypatching fragile probes (e.g. the `bd` shared-DB resolution). Run from the
repo tree:

```bash
uv run skills/yf-plan/scripts/test_worktree.py          # yf-plan
uv run skills/yf-research/scripts/test_research_manager.py
```

Tier-1 is the fast guard for pure-logic changes (branch naming, base resolution,
fingerprint hashing, status transitions, path computation). It **cannot** catch SKILL.md
orchestration regressions — those are prose the tests don't execute.

### Tier-2 — mechanical scratch integration (the modified skill, end-to-end)

Exercises the **modified** skill installed into an **isolated sandbox** and drives a real
lifecycle. Lives in `skills/<skill>/test-harness/`. For yf-plan:

```bash
skills/yf-plan/test-harness/smoke.sh gate      # one-shot: setup → drive → verify → Tier-1
```

The `gate` subcommand is the whole capability check in one run; `setup` / `drive` / `verify`
are the individual phases.

## The mechanical-drive strategy (the key idea)

The lifecycle would normally be driven by the interactive `/<skill>` skill — an **agent
walk** that is neither scriptable nor deterministic. Instead, **drive the identical
lifecycle by calling the manager script's verbs directly**, reproducing exactly what the
SKILL.md orchestration does, then assert the observable end-state.

For yf-plan (`smoke.sh drive`, feature-branch strategy):

```
init → checkout -b <id>-development → update-status approved
     → fingerprint write → commit-plan → git branch <id> (land) → checkout <id>
     → worktree ensure   (cuts <id>-execute from the pinned feature base)
```

Then `smoke.sh verify` asserts the **topology** the change is about — named per-phase
branches, execute cut from the pinned base (no branch-of-a-branch), the `**Fingerprint:**`
header — and writes a `topology.txt` acceptance artifact.

This is **deterministic, offline, and needs no Claude/LLM session**: it validates the
mechanical logic that produces the topology, which is what a manager-script change actually
touches. The agent-driven `/<skill>` walk validates only the SKILL.md prose glue — document
that as a manual checklist (see the harness README), don't try to script it.

## Sandbox isolation (non-negotiable for Tier-2)

The `SKILL_DIR` resolver searches `~/.claude/skills` **first** (`head -1`), so a scratch
`.claude/skills/<skill>` is **shadowed** by the operator's installed copy — the smoke would
silently run the *old* skill (RT2-1). The fix is a **sandboxed `HOME`**:

```bash
HOME=<sandbox> cargo build            # re-embeds the MODIFIED ../skills
HOME=<sandbox> yf skills install      # lands the modified skill at <sandbox>/.claude/skills
HOME=<sandbox> <drive + verify>       # resolver's first hit IS the modified copy
```

`bootstrap.sh` does this and **asserts** the resolved skill dir is the sandbox path (aborts
if shadowed). Note the binary is at the workspace-root `target/debug/yf` (this is a cargo
workspace), not the crate-local `yf/target/debug/yf`.

**Auth:** on macOS, Claude auth is in the login **Keychain** (per-user, not per-`HOME`), so
a sandbox `HOME` already shares it — no token file to copy, no re-login. Only `~/.claude.json`
(config) is linked in, for an *optional* interactive walk; never link the whole `~/.claude`
(it would re-shadow the modified skill).

## Promotion boundary

The rework has **zero effect** on the live environment until an explicit rebuild + promote
(`cargo build` → `yf skills install` into the real `~/.claude`). **Do not promote until the
Tier-2 scratch smoke passes.** Sequence promotion as the final land action.

## When to use which

| Change | Tier-1 | Tier-2 |
|:--|:-:|:-:|
| Manager-script pure logic (naming, hashing, path, status) | ✅ required | recommended |
| Worktree / branch / base-pinning / landing topology | ✅ | ✅ required |
| SKILL.md orchestration prose (pour placement, handoff, merge target) | — | ✅ required (+ manual walk) |
| Before promoting into the real `~/.claude` | ✅ | ✅ required |
