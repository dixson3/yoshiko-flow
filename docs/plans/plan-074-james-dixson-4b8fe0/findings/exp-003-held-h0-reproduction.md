---
type: Finding
okf_spec: OKF-PLAN
description: A portable 18-node H0 snapshot reproduces exit 1 solely on the extra wrapper gate count; installed and source scripts match.
---
# EXP-003 — Held H0 reproduction and artifact provenance

## Finding: Compatibility failure remains distinct from start fallback and packaging

### Approach Tested
Read PIM plan-012 and its original/round-4 completion reviews, packaging relocation report and mapping, and retained execution-epic mapping. Ran only ordinary tracker reads after PIM beads preflight returned ok (embedded-storage profile warning retained, no repair). Captured `bd list --all --include-gates --limit 5000 --json` (283 records), selected the exact root plus recursive parent descendants into a portable 18-record fixture without altering any selected object, and captured default `bd children` output. Copied original plan, execution mapping and historical fidelity bytes. No real DB was a probe target.

Ran the unchanged installed comparator against those files; ran only AST-extracted `_find_start_gate_pair` with in-memory snapshot lookups, never the mutating resolve verb.

### Result
**measured:** Bundle-relative `assets/fixtures/pim-h0/reproduced-fidelity.json` records exit 1: 8 issues/IDs, 7 edges and 4 epics match, but declared gates 3 versus observed 4. The root `pim-mol-vp2` has plan-dir metadata; wrapper `pim-mol-3pg` blocks real human gate `pim-mol-0u3`. Both are direct children, gate-typed, closed. Only the actual gate has `await_type=human`. Saved PIM mapping independently identifies these roles. The original approved fingerprint is `2dd5d32c657cac2a4b15027285cf62f1760181494fbd3b46aa6b143aa05d2db7`.

**measured:** Bundle-relative `assets/fixtures/pim-h0/resolver-snapshot-result.json` reports no wrapper task even when the resolver is fed gate-inclusive direct children. Default `bd children` additionally omits both gates. This establishes two discovery boundaries, not just a type-filter edit.

**measured:** Bundle-relative `assets/fixtures/provenance.json` pins source commit, binary versions and exact digests. Source and installed manager, comparator and extractor are byte-identical at measurement. Binary reports `yf 0.5.0 (5677780-dirty)` although source main is `8c97581e85fd48ebdfac45866b03fd213b9a783a`; do not infer binary/source equality from that stamp. Read-only bundle-relative `assets/fixtures/installed-status.json` separately reports installed yf-plan complete, unmodified, up-to-date and matching embedded hash `102f7e724659a611cc236027d7c47c787d3582c45c018b394b33258eeaa668e9`.

**measured:** Existing issue #417 covers both failures, and no matching open plan was found. #445 seeks a standing waiver and #414 broader landing ordering; neither grants authority here. Scoped `yf-beads-upstream push --issues yf-05k1` preview then `--apply` preserved #417's original body and title and appended only a bounded planning note. Readback verified OPEN and exact external-ref. Raw before/after receipts are in assets/fixtures.

**inferred:** The PIM mapping is historical executor evidence, not the native raw three-key pour response or a cryptographic provenance token. Its role claims are corroborated by the graph and native EXP-001 results. A new checked binding must label that evidence honestly and cannot infer human consent from a closed wrapper.

### Implications for Plan
Do not patch PIM types/dependencies or replay historical workarounds. Preserve all snapshots as immutable inputs in `assets/fixtures/**`; copied plans and scripts inside that subtree are archival inputs, not active plans or runnable instructions. Later regression harnesses copy inputs to owned scratch and supply explicit paths. No sibling checkout is necessary to reproduce the archived mismatch.

### Recommendations
Use the held graph as a regression fixture, but keep a new post-deployment read-only live verification separate from frozen evidence. Require identity-bound mapping evidence, actual gate state, and explicit consent checks. Source changes, binary rebuild, installed deployment and fresh-session invocation remain separate acceptance events.
