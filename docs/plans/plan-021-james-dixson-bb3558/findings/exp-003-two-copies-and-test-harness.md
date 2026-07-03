# EXP-3 — repo-source vs installed skill; scratch-project test harness

**Trigger:** operator correction — this plan edits the **repo source** `skills/yf-plan/`, not the
**live installed** skill that runs when `/yf-plan` is invoked. Testing must therefore exercise the
modified repo copy in a scratch project, not the installed copy.

## Findings

### Two decoupled copies
- **Repo source:** `<git-root>/skills/yf-plan/` — what this plan edits.
- **Installed/live:** `~/.claude/skills/yf-plan/` — what an agent's `/yf-plan` invocation resolves
  (`SKILL_DIR` resolved there all session). The SKILL_DIR resolver searches, in order:
  `~/.claude/skills`, `~/.agents/skills`, `$GIT_ROOT/.claude/skills`, `$GIT_ROOT/.agents/skills`,
  `.claude/skills`, `.agents/skills`.
- **Consequence:** editing the repo copy does **not** hot-swap the running installed skill. The
  plan-019-style "protocol changes under our feet mid-execution" hazard (RT-C1) essentially evaporates
  for repo edits — it would only occur if someone runs `yf skills install` (promote) mid-flight.

### Skills are embedded in the `yf` binary at build time
- `yf/Cargo.toml:18` `rust-embed = { version = "8", … }`; `yf/src/embed.rs:30` `#[derive(RustEmbed)]`
  with `folder = "../skills"` — **the entire `skills/` tree is baked into the binary at build**
  (REQ-YF-EMBED-001/002: enumerates from the binary alone, no repo/network at install).
- `yf skills install [--target <dir>] [--force]` deploys those **embedded** bytes (rules to the
  sibling `rules/`). So a `yf skills install` reflects modified repo skills **only after a `yf`
  rebuild** re-embeds `../skills`.

### The existing test harness already runs the Python layer standalone
- `skills/yf-plan/scripts/test_worktree.py` uses a `git_repo` pytest fixture (`tmp_path`, `git init`,
  `.beads/` marker, `monkeypatch.chdir`, bd-probe monkeypatched) — it runs `plan_manager.py` logic
  **directly from the repo tree against throwaway git repos, no install needed**.

## Test strategy (two tiers)

- **Tier 1 — mechanical `plan_manager.py` (no build, no install).** Worktree base-pin,
  `landing-strategy` resolver, `commit-plan` branch guard, fingerprint compute/stale-detect: all
  unit/integration-testable via `test_worktree.py` run straight from `skills/yf-plan/scripts/` against
  tmp git repos. **Covers the bulk of the #47/#63/#64 code behavior deterministically.**
- **Tier 2 — orchestration end-to-end (the modified SKILL.md prose, followed by an agent).** Needs the
  *modified* skill loaded in a scratch project. Two routes:
  - **(a) rebuild + target-install (highest fidelity, also tests the install path):** `cargo build`
    (re-embeds `../skills`) → `yf skills install --target <scratch>/.claude/skills --force` → drive a
    throwaway plan through plan→auto-commit→execute→land in the scratch project.
  - **(b) dev-link (fast iteration, bypasses embed/install):** scratch project with
    `.claude/skills/yf-plan` symlinked/copied to the repo `skills/yf-plan`. No rebuild.

> **Resolver-shadowing correction (RT2-1).** The `SKILL_DIR` resolver searches `~/.claude/skills`
> **first** with `head -1`. Because the operator already has `~/.claude/skills/yf-plan` installed, a
> scratch `<scratch>/.claude/skills/yf-plan` (route a `--target` **or** route b dev-link) is
> **shadowed** — the resolver returns the installed *old* copy and the smoke silently tests the wrong
> skill. **Both routes must isolate the resolver**, primarily via a **sandboxed `HOME`**
> (`HOME=<scratch-home> cargo build && HOME=<scratch-home> yf skills install`, then run the smoke with
> that `HOME`) so `~/.claude/skills` *is* the scratch home's modified copy. Alternatives: shadow-aside
> the user install for the run, or drive the smoke by explicit path (weaker — bypasses the resolver).

## Implications for the plan
- **Self-hosting risk is downgraded** from "hot-swap under our feet (high)" to a **test-fidelity**
  concern (medium): the danger is validating against the installed *old* skill and getting a false
  green — mitigated by Tiers 1/2 above.
- **plan-021's own execution needs no "pinned snapshot / worktree-off / no-resume" constraint** — repo
  edits are inert w.r.t. the running installed skill. The one rule: **do not `yf skills install`
  (promote) until validated.** Promotion is a deliberate post-plan step.
- **Epic 0 becomes a real deliverable:** the scratch-project test harness (Tier-1 extension + a Tier-2
  scratch bootstrap + a scripted end-to-end smoke), which the capability gate consumes.
