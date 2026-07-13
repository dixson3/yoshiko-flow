# Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 6 (delta: convert_wikilinks lint→format move)

**Context:** delta review of the one change since pass-5 APPROVE — moving `convert_wikilinks.py`
out of `yf-markdown-lint` into the new `yf-markdown-format` skill (Epic 5), reframing that skill as
"the autofix side of the linter." Claims verified against real code.

## Verdict: REVISE

The refactor is architecturally sound — the flag-side/fix-side split holds, the dep graph is
SPEC-first-correct, there is no code coupling, and the DRIFT-CHECK `script` node is auto-covered by
the generic glob. **But the Issue 5.3 de-list list is materially incomplete** — it enumerates three
lint surfaces and misses ≥3 more in-repo references that trip named `required` DRIFT-CHECK edges.
Small to fix, but blocking (would fail the merged-state drift check at execution).

## Strengths

- **Core claims verified.** `convert_wikilinks.py` is a genuine in-place rewriter
  (`convert_wikilinks.py:364` `p.write_text`), a standalone argparse CLI (`main()` :369), with **no
  in-repo importer** (no `import convert_wikilinks`) and **no test** (`scripts/` holds only
  `test_markdown_lint.py`). Every factual premise of the refactor holds.
- **Flag-side/fix-side split accurate.** ML001 flags `[[wikilinks]]` / `convert_wikilinks` rewrites;
  ML008 flags missing alignment markers / `md_table_align` reflows. The pre-existing guardrail
  tension is real: `SPEC.md:9` + `GR-MDLINT-001` (`SPEC.md:60-62`, "never authors, reformats, or
  aligns content") in the same skill that ships an in-place rewriter — moving it out makes the
  guardrail honest.
- **Dep graph sound, SPEC-first honored.** 5.1→{5.2,5.3}; {5.4,5.5}→5.2,5.3; 5.6→5.4. 5.3 depends
  on 5.1 (the migration `REQ-MDFMT-*` must land before the script moves). 5.3's "independent of
  Epic 1" claim checks out (disjoint file sections).
- **DRIFT-CHECK `script` node correctly handled.** `convert_wikilinks.py` is caught only by the
  generic `skills/*/scripts/*.{sh,py}` glob (`DRIFT-CHECK.md:35`), no per-file row, so the same glob
  matches the new path with no per-file edit. `e-skill-script-cli` auto-applies.
- **Untested-script risk pre-empted.** 5.3 adds the missing tests as part of the move.

## Concerns

- **C1 — the de-list list misses ≥3 in-repo references — severity: medium (blocking).** Issue 5.3 /
  Approach Epic 5 item 3 enumerate only SKILL.md, SPEC.md §3, and the protocol. Grep finds uncovered
  references the move will strand:
  - **`skills/yf-markdown-lint/README.md:40`** (the usage command) **and `:61`** (the file-layout
    tree entry) → trip **`e-readme-usage`** (`DRIFT-CHECK.md:82`) and **`e-readme-layout`** (`:123`),
    both `required` edges → hard DRIFT-CHECK FAIL.
  - **Root `README.md:365`** — the yf-markdown-lint skills-index row ("Ships `convert_wikilinks.py`
    …") → trips **`e-index-desc`** (`:128`). Plan 5.5 adds a new format row but never edits the lint row.
  - **`skills/yf-skill-authoring/SKILL.md:228`** — "run `yf-markdown-lint`'s
    `scripts/convert_wikilinks.py` …" — a cross-skill path pointer that becomes wrong (prose, not a
    checked edge; lower severity, but misdirects authors).
  **Recommendation:** replace the enumerated de-list list with a grep-complete instruction —
  "de-list **every** in-repo reference (`grep -rn convert_wikilinks`), specifically: lint
  SKILL.md/SPEC.md/protocol/**README.md** (usage cmd + file-layout tree), the **root README
  skills-index row** (drop the 'Ships convert_wikilinks.py' clause), and the **yf-skill-authoring**
  pointer — and add the mirror entries to yf-markdown-format's README + root index row."

- **C2 — "fix-side of what lint flags" is slightly loose for tables — severity: low.**
  `md_table_align.py` pads/reflows cell widths, which the linter never checks (ML008 only checks
  *presence* of alignment markers). The aligner does strictly more than "fix a lint finding." The
  framing is defensible (general GFM conformance); just don't oversell a 1:1 flag↔fix mapping in the
  new SKILL.md. No plan change required.

## Missing

- The skill's own `README.md` in the de-list list (the most consequential miss — a `required`
  file-layout edge). Folded into C1.

## Gate Assessment

Unchanged and sound. Reconcile Gate binds #85 to Issue 5.2; the convert_wikilinks move (5.3) is a
non-upstream refactor with no `resolves-upstream`, correctly carrying no gate obligation.

## Upstream Assessment

No change. The move is an internal refactor with no upstream disposition — correctly not added to
the Upstream Issues table; coarse tracker #82 needs no new entry.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| C1 | De-list list misses lint README.md (usage + file-layout), root README skills-index row, and yf-skill-authoring pointer — would hard-FAIL e-readme-usage/e-readme-layout/e-index-desc | medium (blocking) | Issue 5.3 rewritten to a **grep-complete** de-list ("de-list every `convert_wikilinks` reference") explicitly naming lint README.md (usage cmd + file-layout tree); Issue 5.5 now edits the **lint root-README skills-index row** (drop the "Ships convert_wikilinks.py" clause) + adds the format mirror; the yf-skill-authoring pointer repoint added to 5.3 | resolved |
| C2 | "fix-side of what lint flags" slightly loose for table reflow | low | Accepted — plan wording ("ML005/ML008 flag structure / format reflows") is close enough; SKILL.md (5.4) will not claim a 1:1 flag↔fix mapping | resolved (accepted) |
