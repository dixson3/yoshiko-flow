# Red-Team Review — Pass 2

**Plan:** plan-027-james-dixson-a59656
**Date:** 2026-07-11

## Verdict: APPROVE

Second-cycle review after pass-1 REVISE. All 8 pass-1 resolutions verified as actually landed in
plan.md/context.md (not just claimed), and against the kernel source + the real skill corpus. Two
new MEDIUM inconsistencies surfaced from the revisions themselves (N1, N2) — non-blocking, folded
in during this pass.

## Verification of pass-1 resolutions (all 8 landed)
- **H1** — resolved and holds against the real corpus: the only three concrete runnable-fence
  tokens (`pour yf-research`, `wisp plan-investigate`, `pour plan-execute`) each have a shipped
  formula; every prose match uses `<name>`/`<formula>` placeholders the contract excludes → the
  fleet passes.
- **H2** — resolved: provenance marker bounds deletion to yf-staged-orphans; missing marker →
  deletes nothing (fail-safe).
- **M3** — resolved: Epic 3 split (FormulaCheck→`checks()` static; GC→cwd-scoped), correct against
  `mod.rs:34-37`.
- **M4** — resolved: verify-destination-every-run + destination-deleted-but-cached test.
- **M5** — resolved: 4.3 rebuild+install binary + `yf --version` gate; documented in context.md.
- **M6** — resolved: `4.1 depends-on 5.1`.
- **L7** — resolved in intent (see N2 for the mechanism gotcha, now folded).
- **context.md** — filled (kernel env, runtime assumptions, cutover assumption).

## Strengths
- HIGH resolutions are substantive, not cosmetic; H1's contract survives contact with the corpus,
  H2's marker is genuinely fail-safe.
- Dependency graph is a clean DAG — every edge resolves; new 4.1←5.1 adds no cycle (5.1 is a root).
- M3's split is architecturally correct against the source.

## Concerns (new this pass — non-blocking, folded in)
| # | Severity | Concern | Resolution |
|:--|:---------|:--------|:-----------|
| N1 | med | "GC decoupled from `--repair`" contradicted placing GC *inside* `run_repair` (which is what `--repair` calls). Marker keeps it safe, but the stated invariant violated its own design. | Folded: GC now runs behind its **own `--prune-formulas` affordance**, not plain `--repair` — true decoupling. Decision 5, Epic 3.2, risk table updated. |
| N2 | med | L7's root-`.gitignore` anchor via `ensure_scaffold` silently won't deploy to already-preflighted repos: the write short-circuits on `scaffold-ensured == SCAFFOLD_VERSION` (`preflight.rs:46,965`). | Folded: Epic 2.1 **bumps `SCAFFOLD_VERSION` 1→2**; 2.2 test asserts the anchor lands on a repo with pre-existing older scaffold state. |

## Missing (minor, noted for Epic 1.2 REQ wording)
- Fence-language / placeholder-set for the extraction contract bounded only for the current corpus
  (`<name>`/`<formula>`); a future skill with a different placeholder style could false-positive.
- Formula-basename collision across two skills — kept if *any* embedded skill declares it (one
  clarifying sentence in the REQ; folded into Epic 3.2 phrasing).

## Gate Assessment
Gates correctly placed. Start + Capability (Rust toolchain, `cargo test`) block Epics 2/3; the
pass-1 binary-embeds-staging gap is closed by the `yf --version` check in Epic 4.3. Reconcile Gate
(auto, single coarse issue) correct.

## Upstream Assessment
Correct: one coarse tracking issue at intake per AGENTS.md, no granular sub-beads, no pre-existing
upstream to reconcile.

## Operator Resolutions
| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| N1 (GC decoupling contradiction) | GC moved behind its own `--prune-formulas` affordance; plain `--repair` never GCs. | resolved |
| N2 (SCAFFOLD_VERSION bump) | Epic 2.1 bumps SCAFFOLD_VERSION 1→2; 2.2 test covers pre-existing older scaffold. | resolved |
