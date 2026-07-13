# Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 7 (verify pass-6 C1 fix)

**Context:** focused re-verification that the pass-6 REVISE concern (C1: incomplete `convert_wikilinks`
de-list list) is fully resolved with no new gap. Grep-complete check against the repo.

## Verdict: APPROVE

Pass-6 C1 is fully resolved. Every in-repo `convert_wikilinks` reference is now covered by an
explicit de-list instruction, both DRIFT-CHECK claims check out, and no new gap was introduced.

## Strengths

- **Grep-complete coverage, verified.** All 7 in-repo references (excluding the script,
  `__pycache__`, `docs/plans/`) are explicitly de-listed:
  - `README.md:365` (root skills-index row, "Ships convert_wikilinks.py") → Issue 5.5.
  - `yf-markdown-lint/SKILL.md:92,97` (Migration helper §) → Issue 5.3(a).
  - `yf-markdown-lint/README.md:40,61` (usage cmd + file-layout tree) → Issue 5.3(c), both cited.
  - `yf-markdown-lint/SPEC.md:52` (§3 Interfaces) → Issue 5.3(b).
  - `yf-skill-authoring/SKILL.md:228` (cross-skill mention) → Issue 5.3(e), repointed.
- **Over-covers the soft reference.** `protocols/MARKDOWN_LINT.md:44` ("the migration helper") has
  no literal `convert_wikilinks` yet 5.3(d) still removes it — correct, since the SKILL.md § it
  points to is deleted.
- **DRIFT-CHECK claim (a) verified.** DRIFT-CHECK.md §1 has only the generic `script` node
  `skills/*/scripts/*.{sh,py}` (:35), no per-file `convert_wikilinks` row, so the new path matches
  automatically — Issue 5.5's "no per-file edit" is correct.
- **DRIFT-CHECK claim (b) verified.** `e-readme-layout` (:123), `e-readme-usage` (:125),
  `e-index-desc` (:128) all exist and mean what the plan says; the symmetric removals keep them
  consistent.

## Concerns

- **C1 (pass-7) — destination README must ADD both moved scripts — severity: low (non-blocking).**
  The new `yf-markdown-format/README.md` file-layout fence + Usage must include `convert_wikilinks.py`
  (and `md_table_align.py`) — the destination side of the `e-readme-layout` `field-set-equal`
  invariant. Implicitly covered by Issue 5.4 authoring the README from scratch, but not called out.
  Recommendation: add a one-clause reminder to Issue 5.4.

## Missing

Nothing. The revision closed the exact gap pass-6 C1 flagged.

## Gate Assessment

Dependency ordering coherent: 5.3 (move) → 5.1; 5.5 (root-README + wiring) → 5.2,5.3, so the de-list
lands before the wiring that references the new location. No dep-graph break.

## Upstream Assessment

Unchanged. Coarse single-issue-per-plan tracking (#82) unaffected by the C1 revision.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| C1 (p7) | Destination `yf-markdown-format/README.md` file-layout fence + Usage must list the moved `convert_wikilinks.py` (and `md_table_align.py`) — e-readme-layout destination side | low | Issue 5.4 amended: the new README's file-layout fence + Usage section explicitly include both `scripts/md_table_align.py` and `scripts/convert_wikilinks.py` | resolved |
