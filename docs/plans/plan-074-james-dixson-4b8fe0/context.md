---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

## Project environment
Yoshiko Flow is a Rust CLI distributing Python manager scripts and markdown skills. Repo source, binary-embedded tree and session-installed skill are three independent artifacts. This plan repairs the yf-plan/native-bd gate-step seam; it does not repair PIM or its H0 implementation.

## Tool inventory
<!-- snapshot: host=d3-mbp-m5.local date=2026-10-29 -->
- Source: clean main `8c97581e85fd48ebdfac45866b03fd213b9a783a`, origin synchronized at start.
- Installed yf: `0.5.0 (5677780-dirty)`; bd: `1.3.1 (Homebrew)`.
- Native historical positive control: bd `1.1.0 (8e4e59d39)`, release checksum verified in owned scratch.
- uv: `0.13.3`; Python through uv only. Shell tools actually ran Bash 3.2 despite interactive zsh conventions; commands must work in both.
- Beads and plan preflights passed. PIM read-only preflight passed with an embedded-mode profile warning; no mode repair was attempted.
- Resolved YF defaults: autonomy autonomous; max-attempts 3; max-review-cycles 5; landing main; execute.worktree false from local config. Do not silently change any default or borrow PIM's local max-attempts=10.
- Read-only embedded/installed status and file SHA-256 pins are [archived](assets/fixtures/provenance.json); binary stamp alone is not equality proof.

## Paths
Primary-side plan: `docs/plans/plan-074-james-dixson-4b8fe0`. Planning branch/worktree: `plan-074-james-dixson-4b8fe0-development` / `.worktrees/plan-074-james-dixson-4b8fe0-development`. Planning commits are on that branch, while the primary copy remains readable without merging into main. No implementation branch is authorized now.

Installed skill used by this session: `$HOME/.agents/skills/yf-plan`, explicitly pinned at invocation. Immutable captured absolute paths occur only in `assets/fixtures/**`; those describe historical captures and must not be executed in place. Active reproducibility uses bundle-relative files and new owned scratch roots, never sibling-repo absolute paths.

## Operator identity
Git attribution: james-dixson. Planner: `yf-plan-gatefix`, cpa/gpt-6-astra. Only the OPERATOR in master approves. Master drafting permission permits an unapproved bootstrap proposal, not adoption or live action. Future execution uses a fresh cpa/claude-opus-5-5 session after approval; master owns validated plain-terminal landing. All subagents are read-only and return only to the planner; no Herdr pushes or metadata authority is delegated.

## Runtime assumptions
macOS evidence is not cross-platform proof. Real bd is required for the sandbox matrix. Every native experiment has an owned HOME/git/store, scrubbed ambient path selection, no credentials, and no link to operator stores. Network was used only for upstream reads and the authorized scoped #417 update. No tool installation, production store mutation, or code merge/push occurred.

## Adjacent-concept glossary
- Wrapper: formula step node used by entry-task dependencies. It may be task- or gate-typed, but has no native wait semantics.
- Actual human gate: separate gate node with await_type=human; closing its wrapper does not establish consent.
- Role receipt: proposed identity binding between native pour/create outputs and reviewed plan/root, not a cryptographic authenticity or consent proof.
- Fidelity: comparison of declared versus observed graph; it is distinct from gate-consistency and resolver fallback.
- Bootstrap exception: proposed one-plan early promotion between sessions; currently UNAPPROVED.

## Additional context
Investigation wisp: `yf-wisp-1nf`. Reused coarse defect mirror: `yf-05k1` → GitHub #417. Init's count-based numeric allocator selected occupied 073; only this newly created bundle was renamed to unused 074. That allocator defect and AST-measured landing journal regression are follow-up candidates, not implementation scope.
