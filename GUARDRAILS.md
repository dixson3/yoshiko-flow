# GUARDRAILS — Yoshiko Flow (`yf`)

> **Status: SEALED — Gate G0 (2026-06-14, operator).** Frozen at plan-010 INTAKE; changes require a
> new PLAN revision (no in-execution edits).

Guardrails are **counterfactuals**: the boundaries that keep this project from drifting into
adjacent domains it must not absorb. Each entry names the **tempting drift**, the **rule** that
forbids it, and **why**. Unlike `SPEC.md` (what `yf` *shall* do), GUARDRAILS state what it *shall
not become*. They are made enforceable by the `SPEC.md ↔ GUARDRAILS.md ↔ README.md` drift edge
(plan-010 Issue 5.4) and re-read against the shipped surface at land (Issue 5.3).

## Project-level guardrails

- **GR-001 — `yf` is not a general package/skill manager.** *Drift:* growing into a registry that
  installs arbitrary third-party skills/plugins. *Rule:* `yf skills` manages **only** the skills
  embedded in this binary at build time. *Why:* the embedded-payload + integrity-marker model
  (REQ-YF-EMBED, REQ-YF-MARK) is the whole safety story; arbitrary sources break it.
- **GR-002 — `yf` is not a `bd`/Dolt replacement.** *Drift:* `yf` growing issue-tracking, memory,
  or sync features. *Rule:* all issue tracking, memory, and history delegate to `bd`; `yf` only
  *verifies/repairs* the beads install (REQ-YF-PRE-006/007). *Why:* one tracker, no duplicate
  systems (per the always-loaded BEADS rule).
- **GR-003 — `yf` is not a skill *runtime*.** *Drift:* `yf` executing or interpreting skill logic.
  *Rule:* `yf` installs, verifies, and preflights skills; the **harness** (Claude Code / agents)
  runs them. *Why:* skills must stay harness-portable; a `yf`-specific runtime would lock them in.
- **GR-004 — `yf` is not a markdown / diagram / PDF engine.** *Drift:* absorbing rendering/linting
  logic into the binary. *Rule:* those are skills (`yf-markdown-lint`, `yf-markdown-pdf`,
  `yf-diagram-authoring`) invoked via their own tools (`uv`, pandoc, d2); `yf` never renders.
  *Why:* keep the binary small and the domains in their skills.
- **GR-005 — the preflight kernel is shared *mechanism*, not skill *domain logic*.** *Drift:*
  porting plan/research/etc. domain logic (init, audit, pour, worktree, index, credibility) into
  Rust. *Rule:* only tool/version/rule-hash/config/state/beads-verify move to `yf`; domain logic
  stays in each skill's Python. *Why:* this is the "shared kernel only" decision (plan-010 B); a
  deep rewrite duplicates working code and couples the binary to every skill's internals.
- **GR-006 — skills stay portable and cross-harness.** *Drift:* `yf` introducing harness-locked
  behavior or a single hard-coded surface. *Rule:* install targets both `.claude` and `.agents`
  surfaces and both user/project scopes (REQ-YF-INSTALL-002); no Claude-only persistence is required
  for a skill to function. *Why:* portability is the founding constraint of Yoshiko Flow.
- **GR-007 — no hidden network or telemetry.** *Drift:* phone-home, usage analytics, background
  fetches. *Rule:* `yf` performs no network I/O except the explicit, user-initiated distribution
  path (Homebrew/release) and whatever a skill's own tool does; no telemetry. *Why:* trust + offline
  install.
- **GR-008 — `yf` touches only its own surfaces.** *Drift:* editing arbitrary user files/repos.
  *Rule:* `yf` writes only the skill install dirs, the `rules/` surface, `.yf/<skill>/` state, and
  `.<skill>.local.json` config; user `CLAUDE.md`/content edits are surfaced for the operator, never
  auto-applied. *Why:* least surprise; the operator owns their repo.
- **GR-009 — the rename is a clean break, not a compat maze.** *Drift:* an ever-growing alias/
  forwarding layer for the old `bdplan`/`bdresearch` names. *Rule:* one clean rename to `yf-*`,
  no runtime aliases; migration is a one-time, idempotent step (REQ-YF-MIGRATE-001). *Why:* aliases
  duplicate dirs and rot.
- **GR-010 — no requirement lives only in code.** *Drift:* behavior that exists in the binary/scripts
  but in no spec. *Rule:* the macro spec is composed from per-skill specs; new behavior lands in a
  `REQ-…` first (or alongside). *Why:* tests anchor to the spec, not the code.
- **GR-011 — the binary is small and dependency-light.** *Drift:* bundling heavy runtimes, an
  embedded Python, or a plugin VM. *Rule:* `yf` shells out to `bd`/`uv`/`git`/`pandoc`/`d2` (declared
  Homebrew deps); it does not vendor them. *Why:* maintainability + transitive Homebrew install.

## Per-skill guardrails

Each skill's `SPEC.md` MAY declare skill-specific guardrails (`GR-<KEY>-NNN`) — e.g.
`yf-drift-check` never authors/auto-fixes (only reports agreement); `yf-markdown-lint` never
rewrites prose (only validates GFM). Those live with the skill and are composed here by reference,
mirroring the macro/per-skill SPEC model.

## References

- `SPEC.md` — the requirements these guardrails bound.
- `skills/SPEC-TEMPLATE.md` — where per-skill guardrails are declared.
