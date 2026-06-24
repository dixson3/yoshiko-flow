# Review pass-1 — plan-012

**Reviewer:** red-team (adversarial), after conformance PASS
**Date:** 2026-06-23
**Verdict:** REVISE

A strong, well-investigated plan. One factual error in a finding (the #31 engine *is*
editable in this repo) and several scoping/sequencing gaps warrant revision before approval,
but none are deep design flaws. No high-severity blockers.

## Conformance (pass)
PASS — all required sections present and non-placeholder; epics have single-deliverable
issues with acyclic intra-plan deps; all four upstream issues `include` + wired via
`resolves-upstream`; both gates declared; success criteria concrete. Cosmetic note: the
Upstream Issues "Resolved By" column reads `_epic TBD_` though wiring exists in the epics.

## Strengths
- Investigation genuinely reshaped the plan (#32 greenfield→refactor; #29 clean standalone verdict).
- DEC-1 surfaced as an explicit operator decision with a defensible recommendation.
- #29 encodes the actual false-positive regression (11-live-gate-edge case) as required test C.5.
- Epic-internal dependency chains explicit and correct.
- #31↔#30 coupling identified with a concrete mitigation.

## Concerns

| # | Severity | Concern | Recommendation |
|:--|:--|:--|:--|
| C1 | medium | exp-002's caveat is factually wrong — `yf/src/beads_init.rs` (27KB) is present/editable here: `repair()` at line 309, `bd hooks install --force` at line 349. The "compiled into kernel, not readable here" claim and Risk #2's hedge are wrong (good news: removes the "may need Rust edits, widening B" risk). | Correct Risk #2 + exp-002; re-scope B.2 as a direct edit to `beads_init.rs:349`; drop B.1's "confirm engine location" hedge. |
| C2 | medium | A.1 replaces 3 live `which` impls + 2 version parsers in a shipped binary; consumed by repair, preflight, doctor. A.1's named tests cover the helper, not the 3 migrated call sites — could silently regress `yf preflight` (which gates other skills). | A.1 acceptance must require existing `preflight` + `beads_init` suites pass post-consolidation; preserve semantics 1:1 per call site; prefer per-call-site migration over big-bang. |
| C3 | low | B.4→D.1 scopes are disjoint (#31 = project-scope hook; #30 = user-scope baseline). The "B before D" constraint is more conservative than evidence requires. | Keep the dep (cheap), but note D.1 blocks only on the entry-scoped-cleanup *decision* being recorded, not B.4 content. |
| C4 | low | DEC-1 recommendation sound, but A.4 moves doctor body to `Result<ExitCode>` while `run_repair` (doctor.rs:120) uses `anyhow::bail!`. Mixed idioms unaddressed. | A.5 should state whether `run_repair` adopts `Result<ExitCode>` or deliberately stays on `bail!` (repair failure *is* an error). |
| C5 | low | C.1 edits `yf-beads-extra` (a *different* skill than the epic delivers); triggers that skill's authoring/manifest conventions. | Note C.1 modifies yf-beads-extra; make manifest-hash refresh part of C.1's close criteria. |

## Missing
- **M1:** No `cargo test`/`cargo build` gate for the Rust-touching epics (A, B). Add a per-epic
  verification gate or success-criterion line requiring green build/test before reconcile.
- **M2:** Reconcile mechanics vs the repo's coarse upstream-tracking rule (AGENTS.md: one coarse
  issue per plan). State that #29–#32 are pre-existing discrete issues, correctly closed each on
  merits — so it doesn't look like a coarse-rule violation.
- **M3:** Out-of-scope release has no handoff bead. File a release bead (discovered-from this
  plan) at reconcile so the version bump + tag isn't stranded in prose.

## Gate Assessment
Start (human) + Reconcile (auto) are the right two types. Gap: no verification gate tying
A/B completion to green `cargo test`. "Complete" should mean tests-green for A/B,
manifest-valid for C.

## Upstream Assessment
All four dispositions `include`, well-justified, each mapped to one epic. No supersedes/partials.
#29 standalone verdict holds up. One wrinkle: reconciliation mechanics vs coarse rule (M2).

## Operator Resolutions
| # | Resolution | Status |
|:--|:--|:--|
| C1 | Corrected exp-002 verdict + Risk #2 to name `yf/src/beads_init.rs` (editable here); re-scoped B.2 as direct edit to `beads_init.rs:349`; dropped B.1 hedge. | resolved |
| C2 | A.1 acceptance now requires existing preflight + beads_init suites pass post-consolidation; per-call-site migration; 1:1 semantics. | resolved |
| C3 | D.1 note added: dep is insurance only; blocks on the cleanup *decision*, not B.4 content (scopes disjoint). | resolved |
| C4 | A.5 now states `run_repair` deliberately stays on `anyhow::bail!` (repair failure is an error), only the read-only check path uses `Result<ExitCode>`. | resolved |
| C5 | C.1 reworded to flag the yf-beads-extra edit + manifest-hash refresh in its close criteria. | resolved |
| M1 | Added "Verification Gate (per Rust epic)" — `cargo test`/`cargo build` green for A & B before reconcile; added matching success criterion. | resolved |
| M2 | Added reconcile note: #29–#32 are pre-existing discrete issues closed each on merits; consistent with coarse rule (which governs *new* tracking-issue creation, not closing existing ones). | resolved |
| M3 | Added reconcile step to file a release bead (discovered-from) so release isn't stranded. | resolved |

**Final status:** all concerns resolved; ready for operator approval.
