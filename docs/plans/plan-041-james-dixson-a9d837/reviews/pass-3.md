---
type: Review
okf_spec: OKF-PLAN
id: pass-3
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
verdict: APPROVE
status: resolved
---

# Review pass 3 — adversarial (red-team)

## Verdict: APPROVE

Four low concerns, none blocking. All resolved anyway.

Cycle 3 re-verified every cycle-2 resolution **against the artifacts**, applying the
skepticism pass-2 earned by catching C18 (a pass-1 resolution asserted but never landed).

## Strengths (verbatim)

- **The C18-class failure did not recur.** Every cycle-2 resolution has a locatable body
  change; the two partials are cosmetic residue of the resolution *prose*, not absent
  substance.
- **C11 was resolved with the right instinct.** The plan does not just retarget — it explains
  *why* the earlier draft was wrong (a code comment promoted to a SPEC requirement) and
  preserves the real PRE-009 linkage as a constraint. `REQ-YF-EMBED-004` closes the actual
  SPEC-first hole.
- **C13's fix is the sharpest change in this cycle.** Requiring the guard test be observed
  RED closes the same false-pass trap C2 closed one level up.
- **Honest under-claiming throughout.** Objective, SC2, SC5, and Issue 3.2 all state what the
  fix does *not* cover. *"Rare and valuable."*
- **The split is fully signposted** — a cold reader cannot mistake relocation for loss.

## Independently re-verified facts

- **`REQ-YF-EMBED-004` is genuinely a free id** — `SPEC.md` §3.2 defines only `-001`/`-002`/`-003`.
- **The plan's new PRE-009 framing is accurate, not a second mis-citation.** PRE-009 does
  consume `YF_GIT_DIRTY` as its first short-circuit, so "the build.rs comment cites PRE-009
  because narrowing would break the dirty flag PRE-009 consumes" holds.
- **Graph re-derived from scratch: acyclic, fully resolving, no dangling targets.** The C19
  edge removal orphaned nothing — 1.2a still reaches the graph via 1.2. **Capability Gate
  reachable**: 1.2 ∉ Blocks, and no member of Blocks is an ancestor of 1.2.

## Concerns (all low, all now fixed)

| # | Concern | Resolution | Status |
| :-- | :-- | :-- | :-- |
| N1 | Approach said "Three active workstreams" while naming four epics — C16's claimed reconciliation had not landed | Corrected to "Four active workstreams". | resolved |
| N2 | Two pass-2 resolution rows over-reported where the fix landed (U-a claimed the Upstream Issues row carried the 4.4 ordering; M-b claimed Objective §1 carried the profiles note) — *"the pass-1 C18 pattern in miniature and worth not normalizing"* | Ordering language added to the #137 Upstream Issues row. The profiles note stays in Issue 0.5 only, which is where an executor reads it; N3 rewords it there. | resolved |
| N3 | The `yf/profiles/` blind-spot claim is an **inference, not a measurement** — the root is real (`harness/profile.rs:26`, `#[folder = "profiles"]`, 3 JSON files) but neither E2 nor E3 probed it | Issue 0.5 now says "believed — not yet measured", names the unprobed status explicitly, and requires a one-minute add-a-file probe before the claim reaches the SPEC. | resolved |
| N4 | **`cargo test --workspace --features embed-in-debug` is not a valid invocation** — the root `Cargo.toml` is a **virtual manifest** (`[workspace] members = ["yf"]`), where cargo rejects a bare `--features`. Issue 3.2 and SC5 both used that literal string | Verified independently. Changed to `--features yf/embed-in-debug` in Issue 3.2 and SC5, with the `-p yf --features embed-in-debug` equivalent and the reason noted inline. | resolved |

## Missing

**Nothing.** All four cycle-2 missing items are addressed (M-a via Issue 0.6, M-b in 0.5,
M-c in 0.4, M-d correctly deferred to plan-042's intake as not this plan's defect).

## Gate Assessment

- **Start Gate (human):** appropriate.
- **Capability Gate: now fully sound.** Reachable, acyclic, keyed to the only property that
  distinguishes a working fix from a typo'd path, and — with C13 — its condition is no longer
  only ever observed green. The demotion of the version grep to a secondary signal with the
  commit-ordering caveat is correct. The pass-2 residual (the gate protects *claims*, not
  *artifacts*) is acceptable and is stated in the gate's own Instructions.
- **Reconcile Gate:** fine.

## Upstream Assessment

- **#137 (include):** closable by this plan alone — `4.1a → 1.1` only, no plan-042 dependency
  anywhere on the closing path.
- **#41 (exclude):** unchanged, still justified.
- **Coarse-granularity convention:** satisfied; plan-042 carries its own tracking issue.

**Bottom line (verbatim):** *"the one high and all five mediums from cycle 2 are genuinely
closed against the artifacts, not merely asserted. The graph resolves, the gate is reachable,
and the SPEC-first rule is now satisfied with a verified-free requirement id. Nothing
remaining rises above cosmetic. This plan is ready to execute."*
