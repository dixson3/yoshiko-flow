# Review pass-1 — plan-014

**Verdict:** REVISE
**Date:** 2026-06-24
**Reviewer:** red-team (adversarial), after conformance PASS

## Strengths

- Option-B vendoring correctly grounded (verified `deploy_skill` verbatim copy, `prune_extra_files`,
  embed root `../skills`; top-level `_shared/` needs zero Rust changes). "No install.py" correction real.
- yf-plan delegation seam precisely located (`_validate_merged` `:1316-1343`); JSON contract +
  exit-3 real; the `:879-884` extraction trigger genuinely anticipates this second consumer.
- The active-set classifier copy (`upstream.py:122-269`) is real, hand-pasted, DRIFT-CHECK-policed;
  retiring it via a sync tool is a real improvement.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | The "reusable machinery in yf-drift-check" **does not exist as code** — drift-check has no `scripts/`/`.py`; its discovery/approved-gate/state-machine/glob/validators are **LLM prose**, not functions. So Epic A is **net-new library work modeled on prose**, not "factoring/moving." And that machinery would have **exactly one consumer** (change-validation) — drift-check won't import Python — so it isn't "shared." The only proven duplication is the active-set classifier. | Rewrite Epic A + Approach to state `_shared/` machinery is net-new, not extracted. Descope: `_shared/` = the genuinely-shared active-set classifier; let change-validation keep its own manifest/bootstrap helpers (one consumer ≠ shared). |
| C2 | medium | Option B relocates duplication: N committed copies + N drift edges — the same keep-in-sync mode the plan indicts `validate-cmd` for. `--check` mitigates only if wired to an enforcement point, which the plan leaves vague ("for CI/drift"). | State exactly where `--check` runs (CI gate / pre-commit / DRIFT-CHECK trigger). Acknowledge the N-copy tradeoff in Risks. |
| C3 | medium (safety) | The runner **executes** arbitrary approved recipe commands. A PR can edit the recipe AND flip `approved: yes` in one change; the engine then runs it on the maintainer's machine at land-the-plane. drift-check is bounded by a read-only sub-agent; this isn't. No re-approval-on-recipe-change gate. | Require that a change to the manifest's recipe commands re-enters the unapproved state (or surfaces a recipe-diff for re-confirm) before the runner executes new commands. |
| C4 | medium | Toolchain inference is net-new + unbounded — 5 parsers (Cargo/package.json scripts/pyproject/just/Make), each ambiguous (which npm script/Make target "validates"?). B.3 treats it as one issue; D1 gate only de-risks cargo+uv. | Bound v1 to Cargo + pyproject (what this repo + D1 actually cover); defer package.json/just/Make to follow-on beads. Align B.8 fixtures + success criteria. |
| C5 | medium | 5 epics / 22 issues conflates 3 loosely-coupled deliverables (#15, #25, #27). #15 is independently valuable + riskier (touches 2 shipped skills). If Epic A is bigger than scoped (see C1), the whole plan stalls. | Consider splitting #15/Epic A into its own plan that lands first and unblocks B; at minimum sequence A to a reviewable landing before B. |
| C6 | low | Layer (a)/(b) carve underspecified: when the recipe runs the full suite it overlaps yf-plan §6.1.5 layer (a). Plan doesn't say if delegation subsumes or duplicates (a). | In Epic D state delegation owns only layer (b); layer (a) coordinator prose untouched (or call out a deliberate subsume). |

## Missing

- No `depends-on-tool` frontmatter / version-floor story for the new skill (policed by `e-readme-prereqs`).
- No budget for DRIFT-CHECK manifest-consistency work: N canonical→copy edges = N nodes + N §3 rows + §6 glob rows; a half-updated `approved: yes` manifest itself FAILs drift-check.
- No statement that authority inverts: today `classifier-canonical` = the hygiene file; under `_shared/` the canonical becomes `_shared/active_set.py` and **both** skill files become derived. A.3/A.4 must redefine authority or a drift FAIL blames the wrong copy.
- No rollback / partial-landing story for a 22-issue plan whose Epic A is now known to be larger.

## Gate Assessment

Start (human) + Reconcile (auto) fine. Capability D1 (auto, cargo+uv test) genuinely needed and
correctly blocks B.3/B.5 — but it only de-risks 2 toolchains while B.3 claims 5 and B.8 promises
per-toolchain fixtures. Add fixtures (and a gate they exist) or cut to what D1 validates.

## Upstream Assessment

Dispositions sound (#27 driver, #25 sub-req, #15 mechanism → epics; E.4 reconciles all three;
coarse one-plan-tracker convention respected). Gap: E.4's "hoist any follow-on" should name the
likely descopes (deferred toolchains) as explicit follow-on targets now.

## Operator Resolutions

| # | Resolution | Status |
| :-- | :-- | :-- |
| C1 | Re-scoped: `_shared/` holds only the active-set classifier (the one proven 2-consumer duplication). No generic manifest/bootstrap library (drift-check is prose, single Python consumer). Framing corrected to "lift classifier", not "extract from drift-check". | resolved |
| C2 | Enforcement point pinned: the yf-drift-check on-edit trigger over the canonical→copy edges (fires on any edit, FAILs on divergence); `--check` is a CI/manual backstop. Copies are generated by the sync tool, not hand-edited. Documented in glossary + Risks + `_shared/README.md` (C.1). | resolved |
| C3 | Out of scope — no executing runner in this plan. Deferred to the #27 follow-on (which will add the recipe-change re-approval gate). | resolved |
| C4 | Out of scope — no toolchain inference in this plan. Deferred to the #27 follow-on (bounded to Cargo+pyproject there). | resolved |
| C5 | Split per operator: this plan = #15 (`_shared/` + classifier retirement) only, lands first; #27+#25 = follow-on plan depending on it. 3 small epics now. | resolved |
| C6 | Out of scope — no yf-plan delegation in this plan. Deferred to the #27 follow-on. | resolved |
| Missing | Authority inversion (`_shared/active_set.py` = fixed authority; both skill files derived) + the full DRIFT-CHECK nodes↔edges↔§3↔§6 consistency pass are now explicit in B.3/B.4. depends-on-tool/rollback were #27-runner concerns → follow-on. | resolved |

**Status:** resolved — plan re-scoped to #15 only and split; all concerns addressed or deferred-with-owner to the #27 follow-on. Re-review (pass-2) follows.
