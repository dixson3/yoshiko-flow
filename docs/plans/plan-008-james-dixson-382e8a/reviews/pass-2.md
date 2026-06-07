# Plan Red-Team: plan-008-james-dixson-382e8a — Pass 2

**Presented:** 2026-06-06
**Scope:** v3 (location-agnostic skill; Epic 2 expanded to skill-authoring; new Epic 3 drift-check verification)
**Conformance (pre-pass):** PASS (after Capability-Gate `Approvers:` fix)
**Status:** RESOLVED (frozen) — all concerns + missing items addressed in plan v4.

## Verdict: REVISE (resolved in plan v4)

The expansion is well-reasoned and the riskiest claim was pre-flagged as an INVESTIGATE
trigger. But there are two verifiable manifest-schema problems in Epic 3, a §6 trigger-scope
gap, and a render-freshness boundary hole. None reopen pass-1.

## Strengths
- "No new contract term" is well-targeted: `path-resolves` is the right one of the six terms;
  existing `e-agent-ref` / `e-template-ref` edges (DRIFT-CHECK.md 69-70) already do this shape.
- install.py verified: `install_skill` does `rsync -a --delete` of the whole `skills/<name>/`
  tree (167-171), so `spec/*.png` travels with install and relative `![](spec/x.png)` refs
  resolve post-install. Decision #8's "relative paths survive install" holds.
- skill-authoring's structure (SKILL.md, reference/, agents/) cleanly accommodates 2.3; it is
  the right injection point (owns skill-dir authoring).
- Dependency ordering 3.1 → 2.3 is correct (verify the convention 2.3 establishes).
- Render-freshness scope-out (owned by `render.py check-dir`) is the right lane division.
- assets/ reconciliation (2.4) and e-prereqs-union (1.4) correctly carried from pass-1.

## Concerns
- **A `.png` target has no valid node Kind — breaks REQ-SCHEMA-001 / REQ-SCHEMA-002** — severity: high
  Manifest §1 requires every node Kind ∈ {source, doc, spec}. A PNG render is a generated
  binary — none of these. REQ-SCHEMA-002 requires the edge to reference an existing §1 node,
  so 3.1 must add a node row with a Kind decision the vocabulary doesn't cleanly offer. Plan
  says "no new contract term" (true for the Contract column) but is silent on the node-Kind
  constraint (a separate axis).
  Recommendation: 3.1 explicitly classifies the PNG node as `Kind: source, Authority:
  derived, Reachability: optional` (a generated source artifact, analogous to a script).
  Confirm it doesn't violate the §7 fixed-authority policy (it won't — it's derived).

- **§6 Trigger Scope: editing/deleting a `.png` fires no check; edge not wired into README globs** — severity: high
  drift-check is on-edit and §6-scoped. The new edge must be added to the §6 rows for
  `skills/*/README.md` and `README.md`. More importantly, the most likely drift — a diagram
  renamed/moved/deleted leaving a dangling ref — is a diagram-side edit, and there is no §6
  glob for `skills/*/spec/*.png` or `docs/diagrams/*.png`, so a PNG delete fires nothing.
  Recommendation: 3.1 must (a) add the edge to the existing `skills/*/README.md` + `README.md`
  §6 rows, AND (b) add new §6 rows mapping `skills/*/spec/*.png` and `docs/diagrams/*.png` to
  the edge. State these §6 edits explicitly.

- **"No engine change needed" is an unverified INVESTIGATE-grade unknown, but 3.1 is ordinary work** — severity: medium
  drift-verifier.md + all spec/ files contain ZERO mention of markdown image syntax;
  `path-resolves` is described generically. Whether the verifier reliably recognizes
  `![](spec/x.png)` as a reference-to-resolve is untested. The plan acknowledges this but
  sequences 3.1 as normal work, not a spike.
  Recommendation: Split 3.1 — a short investigation spike (dispatch drift-verifier against a
  hand-made `![](spec/x.png)` fixture, confirm it resolves) GATES the manifest edit.
  Pre-commit the fallback: a "markdown image refs are path-resolves references" line in
  drift-verifier.md / checks.md is permitted (generic engine guidance, not repo vocabulary —
  REQ-ENGINE-006 not violated). Say so, so execution doesn't stall.

- **Render-freshness gap: a stale `.png` (source edited, not re-rendered) is caught by neither tool** — severity: medium
  Plan scopes freshness OUT of drift-check (good) but `check-dir` only verifies a matching
  `.png` *exists*, not that it is *current*; and it runs manually, not on edit. Edit `foo.d2`,
  forget to re-render → drift-check PASS (path resolves), check-dir PASS (png exists), stale
  diagram ships. Most likely real-world drift, nothing catches it.
  Recommendation: Either (a) `check-dir` compares mtime/hash and documents it as the freshness
  check, or (b) explicitly accept the gap in Risks. Don't imply freshness is covered when
  check-dir as specified covers only existence.

- **"six-term vocabulary" vs REQ-SCHEMA-001 "seven sections"** — severity: low
  Cosmetic. The six-term claim (REQ-SCHEMA-003) is correct; ensure 3.x reads REQ-SCHEMA-003
  (vocabulary), not REQ-SCHEMA-001 (section count), when validating "no new term."
  Recommendation: No change; just a reading note for the executor.

## Missing
- Which §1 Kind the PNG node takes (high concern above) — schema forces the choice.
- §4/§5: the PNG node should be `Reachability: optional` with NO §4 referencer row, else the
  orphan check (REQ-CHECK-004) flags every un-referenced diagram as drift. State in 3.x.
- `e-readme-layout` coupling: adding `spec/*.png` + `spec/*.d2` means those files appear in
  `find skills/<skill> -type f` and MUST be listed in that skill's README file-layout fence,
  or `e-readme-layout` (`field-set-equal`) FAILs. Unstated coupling — flag in 1.4 (the
  skill's own README) and 2.3 (any skill that gains a spec diagram).

## Gate Assessment
Capability Gate remains valid; correctly scopes render-dependent issues (1.5, 2.x, 3.x). 3.2
self-verify is genuine. Gap: 3.2 verifies only the BROKEN-ref case; a verifier that flags
everything (or nothing) as broken could pass spuriously. Add a POSITIVE case (valid ref →
PASS) alongside the negative.

## Upstream Assessment
Unchanged from pass-1 and sound. #6 supersede (carried/relocated/re-homed) is honest; #7
exclude correct. The expansion stays within the single coarse tracking-issue model (AGENTS.md,
precedent #13/#14/#16) — Epic 3 + skill-authoring are part of the same plan-scale effort, not
separate upstream issues. No new upstream issues warranted.

## Operator Resolutions
| # | Concern | Severity | Resolution | Status |
|---|---------|----------|------------|--------|
| 1 | PNG target has no valid §1 node Kind | high | Issue 3.2 now adds a §1 PNG node with `Kind: source, Authority: derived, Reachability: optional` (generated source artifact). | resolved |
| 2 | §6 trigger-scope gap (README + png globs) | high | Issue 3.2 enumerates §6 edits: add edge to existing `skills/*/README.md` + `README.md` rows AND new rows for `skills/*/spec/*.png` + `docs/diagrams/*.png` so diagram-side deletes/renames fire the check. | resolved |
| 3 | "no engine change" unverified → needs spike | medium | Epic 3 split: Issue 3.1 is now an investigation spike (verify drift-verifier resolves `![](path)` against a fixture) that GATES the 3.2 manifest edit; fallback (generic guidance line in drift-verifier.md/checks.md) pre-committed as permitted non-vocabulary engine guidance. | resolved |
| 4 | render-freshness gap (stale-but-present png) | medium | Issue 1.2 `check-dir` adds advisory mtime-staleness WARN (same-tree); freshness explicitly accepted as a residual gap in Risks, durable guard = `render-dir` regeneration discipline before commit. | resolved |
| 5 | six-term vs seven-section reading note | low | Issue 3.2 explicitly cites REQ-SCHEMA-003 (vocabulary), not REQ-SCHEMA-001 (section count). | resolved |
| M1 | PNG node optional + no §4 referencer | missing | Issue 3.2: PNG node is `Reachability: optional` with no §4 referencer row, so REQ-CHECK-004 orphan check won't flag un-referenced diagrams. | resolved |
| M2 | e-readme-layout coupling (list .d2/.png in fence) | missing | Flagged in Issue 1.4 (skill's own README) and Issue 2.3 (any skill gaining a spec diagram must list `.d2`/`.png` in its README file-layout fence). | resolved |
| M3 | 3.2 needs positive-case (valid ref → PASS) check | gate | Issue 3.3 self-verify now covers BOTH valid ref → PASS and broken ref → FAIL/INCONCLUSIVE. | resolved |
