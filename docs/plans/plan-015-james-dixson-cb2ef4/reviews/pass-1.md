# Red-Team Review — pass 1

**Plan:** plan-015-james-dixson-cb2ef4
**Date:** 2026-06-24
**Verdict:** REVISE

## Strengths

- Findings are concrete and verified against code: the `acceptance` extraction comment at
  `plan_manager.py:879-884` mandating a prose soft-dep; the `{plan_dir, validate_cmd_configured,
  layer_b, notice, status}` schema + exit-3 contract; CI runs cargo-only (FULL⊇CI superset is true);
  `.yf-plan.local.json` does not exist in this repo (the plan-014 false-green gap is real and
  standing).
- Trust model honestly addressed — code-exec risk named, mitigated by approved-gate, trust surface
  identical to the already-operator-authored `validate-cmd`.
- Fail-closed posture directly answers the issue it indicts (INCONCLUSIVE-on-missing-tool,
  notice-on-absent-manifest).
- Zero-Rust claim structurally grounded (data-driven `protocols/` aggregation via `flow.rs`,
  GR-005 boundary) with a discovered-bead escape hatch.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | medium | 6 epics / ~17 issues is large; Epic E bundles dogfood + unrelated #25 docs + drift-coverage + reconcile. #25 (E.2) has no real code dep on the engine — its D.2 dep is artificial sequencing. | Mark A–D as the MVP capability boundary and E as reconcile/dogfood; drop the artificial E.2→D.2 dep (or split #25 to a standalone follow-on). |
| C2 | medium | The self-maintaining `check-drift` re-proposal (B.3 + §2 fingerprint + on-edit drift trigger) is the most speculative machinery; justified mainly by one standing example (CI omits pytest) which is a bootstrap-time augmentation, not actual drift. | Don't cut — **stage** it: ship B.1/B.2 (infer + run) + manifest as MVP; sequence B.3 + drift trigger last, independently reviewable, deferrable to follow-on if review shows the drift case is thin. Make the staging explicit in Risks. |
| C3 | medium | Manifest schema gaps for a code-executing engine: no per-command timeout, no working-directory (the recipe needs `cd website && npm ...`), no shell-vs-argv semantics, and no defined `--changed`→§3-glob→FAST-subset resolution (conflates trigger-scope with affected-scoping). | A.1 `schema.md` must specify per-command shape (`cmd`, optional `cwd`, optional `timeout`, run-via-shell) and define §3 glob→FAST-subset precisely (does a changed path prune FAST, or just select the tier?). |
| C4 | low | Capability-gate ordering reads circular: the gate blocks E.1 close, but E.1 *is* "author+approve the manifest." The `Test:` command errors until the manifest exists/approved. | Reword the condition to make the sequence explicit ("after E.1 authors + operator-approves, FULL passes"); confirm the `Test:` returns a clean refusal (not a stack trace) pre-approval (already in B.2 scope). |
| C5 | low (but real design gap) | Carve overlap: FULL tier lists "yf-drift-check full" and FAST lists drift-check on §6 glob — but exp-001 establishes drift-check is **prose + LLM sub-agent, no Python/script**, so a Python engine **cannot** mechanically `run` "yf-drift-check full" as a shell command. Also a single `.md` edit could fire two on-edit triggers (drift-check's own + change-validation's FAST re-invoking it). | A.1/C.2 must state how the engine represents the one validation step that is **not** a shell command (drift-check is an LLM dispatch, not a runnable command). Resolve the double-trigger interaction. |

## Missing

- No rollback/disable lever called out (the mechanism — set `§0 approved: no` to fall back to
  validate-cmd/notice — exists but isn't named as the operator escape).
- No FULL-tier runtime budget statement for land-the-plane (multi-minute gate on every land); confirm
  acceptable or that FULL is pre-push-only, not every merge-back.
- The seam comment names an `acceptance` skill; this plan builds `yf-change-validation` (same thing)
  — reconcile the naming so a future reader doesn't hunt for a separate skill.
- #27's explicit **migration clause** ("`validate-cmd` seeds the manifest") is not wired into any
  issue — disposition is `include` but the migration sub-requirement is dropped.

## Gate Assessment

Start Gate (human/operator) and Reconcile Gate (auto → E.4) are standard and correct. The
Capability Gate (dogfood FULL green) is the right gate — the plan's central success claim made
executable — but reword to remove the circular reading and assert the pre-approval refusal path.

## Upstream Assessment

Both dispositions reasonable. #27 (include, driver) — full-skill scope matches the issue's own
"plan-scale" framing; but the **migration clause is silently dropped** (see Missing). #25 (include,
bundled docs) — fine, but the bundling creates the artificial-dependency concern (C1). Reconcile via
E.4 (coarse single-issue update per AGENTS.md) is correct.

## Operator Resolutions

**Final status: RESOLVED** — all concerns addressed in plan v2 (in-place revision, no re-pour;
plan still in `review` pending operator approval).

| Concern | Resolution | Status |
| :-- | :-- | :-- |
| C1 (scope/staging + artificial #25 dep) | Approach now marks A–D as the MVP boundary, E as dogfood/reconcile; E.2 (#25) de-coupled — depends only on the start gate (the artificial D.2 dep removed). Full scope kept per operator decision. | resolved |
| C2 (stage check-drift) | Approach "Staging" para + B.3/C.2 explicitly marked as the staged self-maintaining tier (sequenced last, deferrable to a follow-on). | resolved |
| C3 (manifest schema gaps) | A.1 now specifies per-command shape (`cmd`/`cwd`/`timeout`/`id`, run-via-shell) and the §3 glob→FAST-subset affected-scoping resolution. | resolved |
| C4 (capability-gate circularity) | Gate condition reworded as an explicit sequence ("after E.1 authors + operator-approves… FULL passes"); Test asserted to return a clean `§0 approved: no` refusal pre-approval. | resolved |
| C5 (drift-check not a runnable command) | Approach "Executable-only recipe" para + A.1 + E.1: tiers contain only runnable shell commands; `yf-drift-check` excluded (prose/LLM, orthogonal trigger); double-fire addressed in C.2 carve. | resolved |
| M1 (rollback lever) | New Risks bullet + engine.md (A.1) + trigger rule (C.2): `§0 approved: no` is the one-edit rollback to validate-cmd/notice. | resolved |
| M2 (FULL runtime budget) | Approach "Runtime budget" para: FULL is pre-push/land-the-plane only (not per coordinator step); FAST is the on-edit tier. | resolved |
| M3 (acceptance↔yf-change-validation naming) | Approach "Naming" para + D.1/D.2: update the `plan_manager.py:879-884` seam comment so `acceptance` == `yf-change-validation`. | resolved |
| M4 (#27 migration clause dropped) | A.1 inference.md + B.1: `infer` seeds the FULL tier from an existing `validate-cmd` when present. | resolved |
