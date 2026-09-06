---
okf_version: '0.2'
---

# plan-026-james-dixson-6e0e2f

> Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention across lint+pdf (#46), document+advise CriticMarkup PDF hazard (#49), add a new markdown-html skill (#50), and add a new yf-markdown-format skill — the autofix side of the linter — absorbing the strict GFM table aligner (#85) and the existing Obsidian→GFM wiki-link migrator

This bundle is **portable** — a cold reader understands its purpose, environment and history from the files below alone, without the drafting conversation.

- [context.md](context.md) - Project Environment Context
- [findings/exp-001-pandoc-lua-filters.md](findings/exp-001-pandoc-lua-filters.md) - exp-001: Validate CriticMarkup + caption pandoc Lua filters (pandoc 3.10)
- [findings/exp-002-yf-doctor-preflight-dep-axis.md](findings/exp-002-yf-doctor-preflight-dep-axis.md) - exp-002 — yf preflight/doctor per-skill dependency axis
- [plan.md](plan.md) - Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention across lint+pdf (#46), document+advise CriticMarkup PDF hazard (#49), add a new markdown-html skill (#50), and add a new yf-markdown-format skill — the autofix side of the linter — absorbing the strict GFM table aligner (#85) and the existing Obsidian→GFM wiki-link migrator
- [references/upstream-46.md](references/upstream-46.md) - Upstream #46: markdown-lint + markdown-pdf: support alt-text (a11y) / title (print caption) image convention
- [references/upstream-48.md](references/upstream-48.md) - Upstream #48: markdown-lint: flag un-escaped inline markup constructs (CriticMarkup et al.) in prose
- [references/upstream-49.md](references/upstream-49.md) - Upstream #49: markdown-pdf: un-escaped CriticMarkup / strikeout-colliding constructs render unexpectedly in PDF
- [references/upstream-50.md](references/upstream-50.md) - Upstream #50: New skill: markdown-html — render Markdown to standalone HTML via pandoc (CriticMarkup-aware option)
- [references/upstream-81.md](references/upstream-81.md) - Upstream #81: yf-markdown-lint ML003 folds image "title" into the link target — mis-flags GFM `![alt](path "title")`
- [references/upstream-85.md](references/upstream-85.md) - Upstream #85 — yf-markdown-lint: absorb md_table_align.py (strict GFM table alignment)
- [reviews/pass-1.md](reviews/pass-1.md) - Red-Team Review — Pass 1
- [reviews/pass-2.md](reviews/pass-2.md) - Red-Team Review — Pass 2
- [reviews/pass-3.md](reviews/pass-3.md) - Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 3 (post-approval #85 delta)
- [reviews/pass-4.md](reviews/pass-4.md) - Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 4 (full whole-plan review)
- [reviews/pass-5.md](reviews/pass-5.md) - Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 5 (delta verification of the pass-4 REVISE)
- [reviews/pass-6.md](reviews/pass-6.md) - Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 6 (delta: convert_wikilinks lint→format move)
- [reviews/pass-7.md](reviews/pass-7.md) - Plan Red-Team: plan-026-james-dixson-6e0e2f — pass 7 (verify pass-6 C1 fix)
- [upstream-triage.md](upstream-triage.md) - Upstream Issue Triage: Markdown tooling improvements bundle
