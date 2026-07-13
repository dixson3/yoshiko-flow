# Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 5 (delta verification of the pass-4 REVISE)

**Context:** pass-4 (full whole-plan review) returned REVISE with 5 concerns; the plan was revised
(C1: #85 moved out of yf-markdown-lint into a new Epic 5 / `yf-markdown-format` skill; C2/C3/C4/C5
addressed). This pass verifies the revisions against real code and confirms internal consistency.

## Verdict: APPROVE

All five pass-4 concerns are genuinely resolved and verified. The C1 restructure introduces no
dangling references, dep-graph breaks, or gate mismatches. One low-medium completeness gap (a §4
Guardrails section for the write-capable new skill) — non-blocking, folded in below.

## Strengths

- **C1 fully resolved, verified.** `yf-markdown-lint/SPEC.md:60-62` `GR-MDLINT-001` ("never
  authors, reformats, or aligns content") is genuinely untouched; the plan adds no ML012 / no
  `--write` REQ to lint (plan.md:79,207,339 explicitly negate them). The composed root line
  `GUARDRAILS.md:68-69` stays true with no amendment — a cleaner resolution than pass-4's
  amend-the-guardrail path.
- **No dangling ML012 / Issue 1.6 scheme.** Surviving `ML012` mentions are the historical phase-log
  line + explicit negations; `1.6` has zero references; Epic 1 is now 1.1–1.5 in correct order.
- **C2 verified.** `md2pdf.py convert()` (`:189-205`) passes no `-f`/`--from` → default `markdown`
  reader (implicit_figures on). Issue 2.2 + risk row + Approach say "do NOT change the reader" + add
  a guard test — sound.
- **C3 verified.** `preflight.rs` reads `depends-on-tool` (`skill_tools`, `:452`) and emits
  `system_deps_missing` (`:326`,`:663`). Epic 4's reframing matches reality; 4.1–4.4 and the
  softened "if adopted, yf doctor also reports" criterion resolve pass-4's gate tie-in.
- **C4/C5 addressed.** d3-pxe aligner confirmed (stdlib-only, east-asian-aware, `#!/usr/bin/env
  python3`, three modes) — matching Epic 5's re-shebang (5.2) + finding-output convention (5.3).
  Epic 5 (5.1–5.5) is coherent + SPEC-first with correct dep edges. C5 accepted (operator kept #85
  in-plan as Epic 5).
- **Reconcile Gate consistent** with the 5-epic structure: #46 partial split binds 1.4+2.2; #85
  binds 5.2; "auto — all execution beads closed" ensures 5.3/5.4/5.5 also close.

## Concerns

- **C6 — new-skill SPECs omit a `§4 Guardrails` section — severity: low-medium.**
  Every existing skill SPEC carries one (`GR-MDPDF-001/002/003` at `yf-markdown-pdf/SPEC.md:115-123`),
  composed by `GUARDRAILS.md:65-70`. Epic 5 Issue 5.1 says only "author `SPEC.md` with `REQ-MDFMT-*`"
  and Epic 3 Issue 3.1 only "`REQ-MDHTML-*`" — neither authors `GR-MDFMT-*` / `GR-MDHTML-*`. Pointed
  for `yf-markdown-format`: it is the fleet's one write-in-place skill — exactly the footgun a
  guardrail should bound (mirroring `GR-MDPDF-002` "renders; never lints"). Root-wiring Issues
  5.4/3.4 enumerate README/SPEC§4/DRIFT-CHECK but not `GUARDRAILS.md` composition.
  **Recommendation:** add guardrail-authoring to Issue 5.1 (`GR-MDFMT-*`: aligns tables only, opt-in
  per repo, idempotent, never rewrites non-table prose) and Issue 3.1 (`GR-MDHTML-*`), and a
  `GUARDRAILS.md` compose-by-reference line to Issues 5.4/3.4.

## Missing

- Nothing blocking. The guardrail-section point (C6) is the one SPEC-first completeness item the
  restructure did not carry forward. All other new-skill wiring surfaces exist and are correctly
  named: root `SPEC.md` §4 catalog, `DRIFT-CHECK.md` `e-index-table`, `README.md` skills index.

## Gate Assessment

Sound and consistent with the 5-epic structure. Start gate appropriate. Reconcile Gate binds the
#46 partial split (1.4+2.2) and #85 (5.2); "auto — all beads closed" covers the remaining Epic 5
wiring beads. Pass-4's unbacked "reported by yf doctor" criterion is resolved by making it conditional.

## Upstream Assessment

No concerns. All six dispositions `include`, specific, consistent; #46 partial boundary explicit;
#85 → Epic 5 with the consumer-migration note (5.5) correctly scoped as a downstream consequence.
Coarse-tracking honored (single plan-026 tracker #82).

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| C6 | New-skill SPECs (5.1 yf-markdown-format, 3.1 yf-markdown-html) omit a §4 Guardrails section; root-wiring omits GUARDRAILS.md composition | low-medium | Issue 5.1 now authors `GR-MDFMT-*` (aligns tables only / opt-in per repo / idempotent / never rewrites non-table prose); Issue 3.1 authors `GR-MDHTML-*`; Issues 5.4 + 3.4 add the `GUARDRAILS.md` compose-by-reference line | resolved |
