# Upstream #65: plan-019: Preflight yf self-update offer + preflight cache version-invalidation

- **Number:** 65
- **Title:** plan-019: Preflight yf self-update offer + preflight cache version-invalidation
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Coarse tracking issue for **plan-019** (one issue per plan, per the repo upstream convention). Landed to `main` — implementation, tests, and coverage gate all green.

**Plan:** `docs/plans/plan-019-james-dixson-eea8e7/` · **Epic:** `yf-mol-99w` (18 beads, all closed) · **Merge:** `baa9379`

## What shipped

- **REQ-YF-PRE-008** — `preflight.json` stamped with the generating `yf` version; a mismatch/absent stamp is a full cache miss that **overwrites** state to drop `prereqs-present`+`scaffold-ensured` (never a merge — red-team C1), re-probes deps+bd, and re-runs the scaffold ensure.
- **REQ-YF-PRE-009** — cache-only, vendor-only, **dirty-build-bypassed** self-update offer folded into the preflight `ok` path (both return points). No network; eventually consistent with the `yf version`/`doctor` nudge cache. Dirty build (`YF_GIT_DIRTY`, `git status --porcelain`) is the first short-circuit.
- **REQ-YF-SELF-007** — `yf self update` invalidates preflight *via* the PRE-008 stamp (new binary → new VERSION → stale stamp); no explicit clear in `update.rs`.
- Build-time dirty capture (`build.rs` → `YF_GIT_DIRTY` + `-dirty` `VERSION_LINE` suffix); shared network-free cache helpers extracted to `update_check.rs` (nag nudge unchanged).

## Validation

`cargo test --workspace` (214+2) · fmt · clippy · SPEC coverage gate (PRE-008/009 + SELF-007) · full CHANGE-VALIDATION tier (pytest rows + `_shared` sync) — all pass over the merged tree.

Related spun-off future work: #62 (yf-spec skill — excluded from this plan's scope).

_Precedent: #13 (plan-005), #14 (plan-006), #16 (plan-007)._
