---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #442 - plan-073-james-dixson-cc76de execution tracking'
---
# Upstream #442: plan-073-james-dixson-cc76de execution tracking

- **Number:** 442
- **Title:** plan-073-james-dixson-cc76de execution tracking
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/442
- **State:** OPEN
- **Labels:** type::epic, priority::high

## Body

Coarse tracking issue for **plan-073-james-dixson-cc76de** (AGENTS.md convention: one issue per plan-scale effort). Resolves #410 and #411. Partially resolves #412.

**Plan:** `docs/plans/plan-073-james-dixson-cc76de/`. Intake commit `a9e03f1`, on `origin/main`. Fingerprint `c11fa737…`, deliverable class `standard`.

**Objective.** Prepare **yf v0.6.0** for release from the tip of `main`: everything since `v0.5.0` (plans 055–072), plus five fixes a first-run user hits.

1. **`yf doctor` is green for anyone with `bd`, `uv` and `git`.**
   - A new per-skill `optional-tool:` frontmatter key makes a missing optional tool a doctor *warning*, not a failure.
   - `herdr` (yf-herdr), `pandoc` (yf-markdown-html/pdf), `xelatex` (yf-markdown-pdf) and `d2` (yf-diagram-authoring) move to the new key.
   - v0.5.0 exits 1 on four `skill-deps:*` axes when those tools are absent.
2. **`.beads.gate.lock`:** repair tops up the project `.gitignore`, and verify reports the file when it is untracked and unignored. bd ≥ 1.3 recreates it at the repo root on every call.
3. **#410:** a per-source `quotes[]` evidence store in `sources.json`, plus a deterministic `link_normalizer.py check-quotes` that the red-team uses.
4. **#411:** `sources.md` is built at the end of synthesize, so citation anchors resolve before critique.
5. **#412 (partial):** preprint servers score Tier 4 by default, with a `--peer-reviewed` override. The `.dev` Tier-2 heuristic no longer promotes package registries or issue mirrors. The undated-source currency part stays open on #412.

**Shape.** SPEC first (Epic 0), then code against tagged tests (Epics 1–3), docs (Epic 4), and the version bump with CHANGELOG (Epic 5).
- 6 epics, 23 issues, 14 success criteria.
- Red-team: passes 1–3 REVISE (25 concerns, all resolved), pass 4 APPROVE with zero measured findings.

**Execution is gated on plan-072 (risk R10).** plan-072's landing failed its L3 FULL `trigger-eval` row on a pi cell. plan-073's landing runs the same FULL tier on a `main` that includes plan-072's code, so plan-073 executes only after plan-072 has landed green. A pi diagnostic eval for plan-072 is running now (tracker #416).

**Release.** The landing's L3 FULL run on the merged tree is the release validation. The `v0.6.0` tag push is a post-landing operator act, not a plan bead. Issue 5.2 files a follow-on bead, "Cut v0.6.0: tag + verify", carrying the procedure, which landing L17 mirrors upstream. The procedure:
- Tag on the tip of `main`.
- Require no workflow diff against `main`. This avoids the v0.5.0 `GITHUB_TOKEN` 403.
- Require that everything since the L3-validated merge is plan-folder bookkeeping.

