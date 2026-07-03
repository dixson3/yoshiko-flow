# Review Pass 2 — plan-021-james-dixson-bb3558

**Trigger:** operator correction — the plan edits the **repo source** `skills/yf-plan/`, which is
**decoupled** from the installed copy `/yf-plan` runs (rust-embed baked into the `yf` binary at build).
This reframed Epic 0 (execution-constraint → scratch-project test harness), downgraded the
self-hosting risk to test-fidelity, and changed the capability gate. Focused re-review of that surface.

**Red-team verdict:** REVISE → all concerns resolved in-place; ready to re-present for approval.

## Strengths
- Two-copy / rust-embed understanding verified correct (`embed.rs` `folder = "../skills"`; `dest.rs`
  `--target` wins). Repo edits do not hot-swap the running installed skill.
- Concern-2 (residual self-hosting) genuinely defused: plan-021's coordinator resolves `SKILL_DIR` to
  the installed copy; the only repo-copy invocation is the deliberate literal-path Tier-1 command. No
  half-edited repo script bites the running protocol. Medium downgrade justified.
- Epic 0 well-formed (0.1→0.2 wired; 0.3 doc); corrected sections internally consistent with context.md.

## Concerns & Operator Resolutions
| ID | Severity | Concern | Resolution | Status |
|:---|:---------|:--------|:-----------|:-------|
| RT2-1 | high | `SKILL_DIR` resolver searches `~/.claude/skills` first with `head -1`, so a scratch `.claude/skills/yf-plan` is **shadowed** by the installed copy — the Tier-2 smoke would silently run the *old* skill (the exact false-green the harness prevents) | Issue 0.1 now mandates **resolver isolation via a sandboxed `HOME`** (`HOME=<scratch-home> cargo build && yf skills install`, run smoke with that HOME) so the first resolver hit is the modified copy; exp-003 route claims corrected with a shadowing note | resolved |
| RT2-2 | medium | Promotion step defined (0.3) but never sequenced; also requires a `yf` rebuild (rust-embed re-embeds only at build) — plan silent on whether rebuild+promote is in scope | 0.3 + Issue 6.3 now sequence promotion as the **final in-scope land action**: after smoke passes + branch merges, `cargo build` → `yf skills install`. Noted the rework has zero live effect until then | resolved |
| RT2-3 | low | Capability-gate interim-guard overclaims Tier-1 (cannot catch SKILL.md orchestration regressions — Tier-2-only) | Gate instructions now state Epic 3's prose behavior is Tier-2-only and require a **working** Tier-2 harness before Epic 3 close | resolved |
| RT2-M1 | note | Missing statement of how the smoke isolates from `~/.claude/skills/yf-plan` | Covered by the RT2-1 sandboxed-HOME resolution in Issue 0.1 | resolved |
| RT2-M2 | note | context.md:11 still called this a "self-hosting change" (stale) | Reworded to "repo source decoupled from installed copy; not a hot-swap" | resolved |

## Missing sections
None — all required portability sections present.

## Gate Assessment
Start Gate correct. Capability Gate now validly consumes the isolated Tier-2 harness (its central
condition — "loaded from the modified repo skill, not the installed copy" — is met only with the RT2-1
sandboxed-HOME fix, now in Issue 0.1); Blocks Epic 3 close + reconcile, and a *working* Tier-2 is
required before Epic 3 close. Reconcile Gate (auto) standard; promotion sequenced into land (RT2-2).

## Upstream Assessment
Unchanged and correct: #47/#63/#64 = include (coarse single-tracker each); #62 = defer. The correction
did not touch upstream dispositions; the scratch harness is internal tooling, not a tracked deliverable.

**Final status:** all concerns resolved; frozen.
