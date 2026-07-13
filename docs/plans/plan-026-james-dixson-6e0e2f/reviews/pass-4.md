# Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 4 (full whole-plan review)

**Context:** operator-requested full, fresh, whole-plan adversarial review (not delta-scoped) of
the re-scoped plan-026. All four epics + the #85 addition, with claims verified against the actual
codebase. Supersedes the delta-only pass-3 for readiness purposes.

## Verdict: REVISE

Two medium concerns three prior passes missed, both verified against real code: a SPEC-first
guardrail conflict introduced by #85, and an Epic-2 reader directive that would regress `md2pdf`.
Neither is high (both are small plan edits), but C1 is a genuine SPEC-first correctness gap and C2
is a plan-vs-code contradiction, so the plan returns for a revision pass before re-approval.

## Strengths

- **exp-001 is real, load-bearing evidence** — caught the two under-specified pandoc incantations
  (`-f gfm-strikeout`, `+implicit_figures`) and validated the caption filter through a full xelatex PDF.
- **#81 diagnosis verified against code** — `markdown_lint.py:47` `MDLINK_RE` captures dest to the
  first `)`, so `![alt](path "caption")` → dest `path "caption"` → fails to resolve at `:305-307` →
  false ML003. Real bug, correct fix direction.
- **ML009 shell-out precedent is real** (`markdown_lint.py:257-261`); `ALL_RULES` (`:49`) ends at
  ML009, so ML010/ML011/ML012 are the next free slots.
- **Epic 3 greenfield confirmed** — no `yf-markdown-html` under `skills/` today.
- **Aligner claims verified** — `d3-pxe/scripts/md_table_align.py` is stdlib-only (`unicodedata`
  east-asian width), owns exactly the three modes the plan preserves.
- **Dependency graph is sound** — SPEC-first issues gate implementation in all four epics; 1.5
  correctly depends on 1.2/1.3/1.4/1.6.

## Concerns

- **C1 — #85 reverses an explicit guardrail Issue 1.1's SPEC work does not amend — severity: medium.**
  `yf-markdown-lint/SPEC.md` §4 `GR-MDLINT-001`: *"the linter validates GFM only; it never authors,
  reformats, or aligns content. Why: table alignment/sizing is a separate concern (upstream #20/#21),
  not a lint side effect."* §1 restates "validates only — never reformats." Root `GUARDRAILS.md:68-69`
  composes it: "yf-markdown-lint never rewrites prose (only validates GFM)." #85 makes the skill own a
  `--write` in-place table-aligning autofix — a direct reversal. Issue 1.1 enumerates the §2.1 table,
  the §2.2 subset, and a new `--write` REQ, but does **not** amend the guardrail forbidding exactly
  this. A `--write` REQ landing alongside an unamended `GR-MDLINT-001` is a self-contradictory SPEC —
  what SPEC-first exists to prevent; the drift/coverage gate would flag it.
  **Recommendation:** In Issue 1.1, explicitly amend `GR-MDLINT-001` + §1 scope (and the composed
  root `GUARDRAILS.md` line) to "validates + optional strict-alignment autofix," recording that #85
  supersedes the "#20/#21 = separate concern" rationale. Encode the read-only-`markdown_lint.py` vs
  `--write`-on-standalone-script distinction in the guardrail wording so it stays consistent.

- **C2 — Epic 2 pins `-f gfm+implicit_figures`, which regresses md2pdf's actual reader — severity: medium.**
  `md2pdf.py` `convert()` (`:189-205`) builds pandoc with **no `-f`/`--from`** → default `markdown`
  reader, which **already enables `implicit_figures`**; the caption filter's `Figure` node fires with
  no reader change. exp-001 tested `gfm+implicit_figures` in isolation, not md2pdf's live invocation.
  Hardcoding `-f gfm+implicit_figures` (in Approach, Epic 2, risk table) silently swaps md2pdf from
  full pandoc-markdown to `gfm`, dropping extensions the pipeline may rely on — an unlisted behavior change.
  **Recommendation:** Keep md2pdf's current reader and just add the caption filter (implicit_figures
  already on); or if a reader change is truly wanted, treat `markdown → gfm` as its own risk with a
  regression check. Replace the hardcoded directive with "ensure the reader has `implicit_figures`
  (the current default `markdown` reader already does)."

- **C3 — Epic 4's premise overstates the unknown; preflight already enforces `depends-on-tool` — severity: low-medium.**
  `preflight.rs` already reads `depends-on-tool` from embedded frontmatter (`:452`, `:583`) and emits
  `system_deps_missing` (`:326`, `:663`), with a passing parity test (`:1905`). The declaration is
  **not** inert for preflight; 4.3's "if inert, wire enforcement" branch is largely dead. The genuine,
  narrower gap: `yf doctor`'s axes are fixed (`REQ-YF-DOCTOR-001`, `SPEC.md:337-342`) and do not
  enumerate per-skill `depends-on-tool`, so doctor won't report a missing pandoc/xelatex — the
  "reported by yf doctor" success criterion implies a real (small) kernel + `REQ-YF-DOCTOR` change.
  **Recommendation:** Reframe Epic 4: preflight already covers per-skill deps; the actual work is
  (a) add `depends-on-tool: [uv, pandoc]` to markdown-html, (b) the md2html entrypoint guard, and
  (c) — only if the doctor half is wanted — a scoped new doctor axis + `REQ-YF-DOCTOR` line. Don't
  present it as an open "inert or not" question.

- **C4 — ML012 shell-out integration mismatch — severity: low.**
  `md_table_align.py --check` prints file-level output with **no line numbers** (`:182-189`), whereas
  `markdown_lint.py` findings are `(lineno, rule, msg)`. ML012 findings will carry a synthetic line.
  The aligner uses `#!/usr/bin/env python3`, not the `#!/usr/bin/env -S uv run --script` + PEP-723
  convention `markdown_lint.py` uses.
  **Recommendation:** In Issue 1.6, state the ML012 finding-line convention (e.g. line 1 / first
  offending table) and align the vendored shebang to the `uv run` pattern.

- **C5 — Over-ambition: a whole new skill + kernel epic in one execution — severity: low.**
  Four epics, a greenfield skill (Epic 3), and a kernel-touching epic. Epic 3 (#50) is the most
  separable (coupled to the lint work only via the CriticMarkup thread). Defensible given the coherent
  theme and two operator re-approvals; C3 also shrinks Epic 4. Flagged, no change required.

## Missing

- The guardrail amendment (C1) is the one real SPEC-first omission. Everything else is enumerated
  across Issues 1.1/1.5/1.6/3.4.
- Minor cosmetic: the Epics list orders 1.6 before 1.5 (a #85-insertion artifact); dependency edges
  are correct.

## Gate Assessment

Start gate (human/operator) appropriate. Reconcile Gate sound: requires both halves of the #46 split
(1.4 + 2.2) and binds #85 to Issue 1.6. Tied to C3: the "reported by yf doctor" success criterion is
not backed by a gate check and doctor doesn't enumerate per-skill deps today — either add the doctor
axis (C3) or soften the criterion to "preflight + entrypoint guard."

## Upstream Assessment

Dispositions all `include`, specific, consistent; the #46 partial boundary is explicit and
gate-enforced. Coarse-tracking honored — one plan-026 tracker (#82) referencing all six issues, not
granular pushes. The #85 consumer-migration note is correctly a downstream consequence, not scope.
No upstream concerns.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| C1 | #85 reverses GR-MDLINT-001; Issue 1.1 doesn't amend it | medium | | unresolved |
| C2 | Epic 2 pins `-f gfm+implicit_figures`, regressing md2pdf's default reader | medium | | unresolved |
| C3 | Epic 4 overstates the unknown; preflight already enforces depends-on-tool | low-medium | | unresolved |
| C4 | ML012 shell-out: no line numbers; shebang convention mismatch | low | | unresolved |
| C5 | Over-ambition (4 epics + new skill + kernel epic) | low | | unresolved (accept/split — operator call) |
