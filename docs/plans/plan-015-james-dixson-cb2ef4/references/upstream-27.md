# Upstream #27: yf-change-validation: per-repo change-set validation skill (supersede static validate-cmd)

- **Number:** 27
- **Title:** yf-change-validation: per-repo change-set validation skill (supersede static validate-cmd)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Spun out of plan-011's land-the-plane follow-up (bead `beads-skills-tr0`). Forward design — not yet scoped into a plan.

## Problem

plan-011 added `validate-cmd` to `.bdplan.local.json` so yf-plan's §6.1.5 merged-state validation can run a repo-wide build/test/lint over the *merged* tree (layer b), not just the landing plan's own gate (layer a). But a static `validate-cmd` string has the **same drift failure mode that motivated `yf-drift-check`**:

- It's per-repo config an operator must hand-author and keep in sync with the repo's actual toolchain. When reality changes (new crate, cargo→just, added docs build, moved test dir), the string silently rots.
- It fails **open**: a rotted/absent command validates the wrong thing, or makes §6.1.5 emit "cross-plan regressions not checked" and proceed on plan-gate coverage only — a false green.
- It's yf-plan-specific. "Is this change-set valid?" is useful beyond bdplan: any worktree merge-back, any pre-land-the-plane upstream push, any agent about to push.

## Insight — same shape as `yf-drift-check`

Computing and keeping a per-repo validation recipe current is the same shape as drift-check: a fixed repo-agnostic engine + a per-repo manifest + a triggered verification pass, with hybrid bootstrap (infer a draft → operator approves → enforce; re-propose on divergence). drift-check applies it to doc/spec/impl **agreement**; this applies it to change-set **validity**.

## Proposal: a `yf-change-validation` skill

- **Engine (fixed):** run the repo's recorded validation recipe over a change-set / merged tree, report PASS/FAIL + the failing command.
- **Manifest (per-repo):** the validation command(s) — ideally layered fast/affected vs full — and trigger points. Seeded by inferring from the toolchain (Cargo.toml → cargo test/clippy/fmt; package.json → npm test; pyproject → pytest/ruff; just/Make targets), proposed, then re-proposed when the toolchain drifts from the manifest (the self-maintaining part).
- **Triggers:** worktree merge-back (yf-plan §6.1.5 layer b → invoke this skill); prior to any land-the-plane upstream push; on-demand `/yf-change-validation`.
- **Migration:** `.bdplan.local.json`'s `validate-cmd` seeds the manifest and remains a thin fallback; yf-plan delegates layer (b) to it when present.

## Carve against neighbors

- `yf-drift-check`: artifacts **agree** across declared edges (content agreement). Never runs the build.
- `yf-change-validation`: a change-set **is valid** by executing build/test/lint (behavioral validity). Never checks doc agreement.
- Orthogonal axes, same engine+manifest+trigger shape; could share the manifest-bootstrap machinery.

## Next step

Plan-scale — warrants its own `/yf-plan` plan (manifest schema, inference/bootstrap engine, yf-plan delegation + fallback, trigger rule). Tracked locally as bead `beads-skills-tr0` (discovered-from plan-011 epic `beads-skills-mol-r8z`).
