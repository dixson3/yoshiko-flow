---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #413 - yf-markdown-lint: ship and deploy a matching .markdownlint.jsonc
  so markdownlint-based tools (pi-lens) follow yf conventions'
---
# Upstream #413: yf-markdown-lint: ship and deploy a matching .markdownlint.jsonc so markdownlint-based tools (pi-lens) follow yf conventions

- **Number:** 413
- **Title:** yf-markdown-lint: ship and deploy a matching .markdownlint.jsonc so markdownlint-based tools (pi-lens) follow yf conventions
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement, type::feature, priority::medium

## Body

## Problem

`yf-markdown-lint` enforces its GFM conventions only through its own script (`scripts/markdown_lint.py`, rules ML001–ML011). It writes no configuration that other markdown tooling reads. Any repo that uses it gets **no** `.markdownlint*` file, so every other linter runs its own defaults and reports warnings that conflict with the yf conventions, or have nothing to do with them.

pi-lens, the pi code-feedback extension, makes the gap concrete:

- On every `.md` edit it runs `markdownlint-cli2`. It also runs `markdownlint-cli2 --fix` as a default autofix, so it **rewrites files**, not only reports.
- It looks for a project config (`.markdownlint-cli2.{jsonc,yaml,yml,cjs,mjs}`, `.markdownlint.{jsonc,json,yaml,yml}`). When none exists it falls back to its own `config/markdownlint/core.json`, which is `{"MD013": false, "MD024": {"siblings_only": true}}`: every other default rule on.
- A project config **replaces** that fallback entirely; they are not merged (`configArgsWithFallback` in `clients/tool-policy.js` passes `--config <fallback>` only when no project config is found).

Observed in `dixson3/rc-files`, which opted into lint-on-edit (`.markdown-lint-on-edit`):

| Linter | `doctor.md` + `AGENTS.md` |
| :----- | :------------------------ |
| `yf-markdown-lint` (all rules) | clean, exit 0 |
| pi-lens → `markdownlint-cli2` (fallback config) | 162 warnings shown in pi's statusline |

Across the repo's 15 main `.md` files the markdownlint findings are MD049 ×70, MD060 ×44, MD036 ×39, MD031 ×17, MD032 ×14, MD034 ×10, MD025 ×8, MD040 ×6, and a few others.

Versions: pi-lens 4.2.1, markdownlint-cli2 0.23.3, markdownlint 0.41.1.

## Where the two rule sets overlap or disagree

Tested with small probe files against pi-lens's fallback config.

### A. Rules markdownlint enforces *against* yf conventions

These must be overridden, or markdownlint flags (and `--fix` may rewrite) content that yf treats as correct:

| markdownlint rule | Default behavior | yf convention | Required override |
| :---------------- | :--------------- | :------------ | :---------------- |
| MD033 no-inline-html | flags `<br>` | SKILL.md "Table authoring": `<br>` is the only portable in-cell line break | `"MD033": {"allowed_elements": ["br"]}` |
| MD045 no-alt-text | flags `![](x.png "title")` | ML011: a present title never warns (`![alt](src "title")` convention) | `"MD045": false`; ML011 owns this check with the title exception |
| MD025 single-title | a frontmatter `title:` plus an H1 counts as two H1s | OKF bundles (`index.md`, `plan.md`, `log.md`, `context.md`) carry a frontmatter `title` and an H1 | `"MD025": {"front_matter_title": ""}` |

Verified: each override clears its probe.

### B. Rules that match yf conventions and should stay on, stated explicitly

| markdownlint rule | yf equivalent | Setting |
| :---------------- | :------------ | :------ |
| MD060 table-column-style | `yf-markdown-format` `md_table_align.py` (strict padded alignment) | `"MD060": {"style": "aligned"}` |
| MD055 table-pipe-style | pipe tables only | `"MD055": {"style": "leading_and_trailing"}` |
| MD056 table-column-count | ML005 | `true` |
| MD058 blanks-around-tables | none (keeps tables parseable) | `true` |
| MD042 no-empty-links | ML006 | `true` |
| MD051 link-fragments | ML004 | `true` |
| MD024 no-duplicate-heading | none; `log.md` repeats `### Status` under each dated `##` | `{"siblings_only": true}` (carry over the pi-lens fallback) |
| MD013 line-length | none | `false` (carry over the pi-lens fallback) |

Verified: running `md_table_align.py --write` on `rc-files/doctor.md` took MD060 from 34 warnings to 0 under `{"MD060": {"style": "aligned"}}`, so formatter and linter agree once both are stated.

### C. yf rules markdownlint cannot express

ML001/ML002 (Obsidian wiki-links/embeds), ML003 (broken relative links), ML007/ML008 (explicit alignment markers on every column), ML009 (d2 fence compile), ML010 (CriticMarkup). markdownlint reports nothing on probes that `yf-markdown-lint` flags for ML001, ML002, ML008 and ML010. `yf-markdown-lint` must remain the authority for these; the generated config does not replace it.

### D. Style rules where yf has no opinion

MD049 (emphasis `_`/`*`), MD050 (strong style), MD036 (emphasis used as heading), MD004 (list marker). These make up most of the rc-files noise, and yf defines no convention for them. Recommended default: **off**, and document it so a repo can opt in.

`"consistent"` is not a safe middle ground. It anchors on the first occurrence in a file, so a file that already mixes styles still fails, and `--fix` still rewrites it. Measured: with `"MD049": {"style": "consistent"}`, `rc-files/doctor.md` still produced 70 MD049 findings.

## Proposed change

1. **Ship a canonical markdownlint config with the skill**, e.g. `yf-markdown-lint/config/markdownlint.jsonc`. It combines the pi-lens fallback defaults with the overrides in A, B and D, and each rule carries a comment naming the ML rule or SKILL.md section it mirrors. Starting point:

   ```jsonc
   {
     // Generated by yf-markdown-lint. Mirrors yf GFM conventions for
     // markdownlint-based tools (pi-lens, editors, CI). yf-markdown-lint
     // remains authoritative for ML001-ML011; see SKILL.md.
     "default": true,

     // Carried over from pi-lens config/markdownlint/core.json. A project
     // config REPLACES that fallback, so these must be restated here.
     "MD013": false,
     "MD024": { "siblings_only": true },

     // A. yf conventions markdownlint would otherwise flag
     "MD033": { "allowed_elements": ["br"] },   // in-cell <br> (Table authoring)
     "MD045": false,                              // ML011 owns alt text (title exception)
     "MD025": { "front_matter_title": "" },       // OKF frontmatter title + H1

     // B. tables and links, agreeing with ML004-ML008 and yf-markdown-format
     "MD055": { "style": "leading_and_trailing" },
     "MD056": true,
     "MD058": true,
     "MD060": { "style": "aligned" },            // md_table_align.py --write
     "MD042": true,
     "MD051": true,

     // D. no yf convention: off (see issue section D; "consistent"
     //    still fails and --fix-rewrites files that already mix styles)
     "MD049": false,
     "MD050": false,
     "MD004": false,
     "MD036": false
   }
   ```

2. **Deploy it into opted-in repos.** When a repo opts into lint-on-edit (`.markdown-lint-on-edit`, or `.yf/markdown-lint-on-edit` after #102), `yf harness skills install`, or a `/yf-markdown-lint init` verb, writes `.markdownlint.jsonc` at the repo root. Rules:
   - Stamp it with a managed marker (the yf-core `sha256=` pattern) so re-install refreshes an unmodified copy.
   - **Never overwrite** an operator-edited or pre-existing `.markdownlint*` file. Report the drift instead.
   - Skip if the repo already has any markdownlint-cli2 config name, since markdownlint-cli2 picks one by precedence and two would conflict silently.

3. **Add a drift check** (e.g. `markdown_lint.py --check-config`) that fails when `.markdownlint.jsonc` is missing in an opted-in repo, or no longer matches the shipped canonical config. It could also run `markdownlint-cli2` with the generated config over the repo and report findings that collide with yf rules, which catches future markdownlint rule additions.

4. **Close the table gap between the two yf skills.** `yf-markdown-lint` passes files that `md_table_align.py --check` reports as not strictly aligned: rc-files passed `yf-markdown-lint` while `--check` failed on both `doctor.md` and `AGENTS.md`. Either add an ML rule for unpadded tables (optional, full-audit only), or document that `md_table_align.py --check` belongs in the full audit. Otherwise MD060 `aligned` fires on files `yf-markdown-lint` calls clean.

5. **Document the relationship** in SKILL.md: a "Compatibility with markdownlint / pi-lens" section covering the generated config, the "replaces the fallback" behavior, the A/B/C/D mapping above, and the fact that pi-lens runs `markdownlint-cli2 --fix` on edit, so the config also controls automatic rewrites.

Measured with this config on `rc-files/doctor.md` after `md_table_align.py --write`: 19 findings remain (MD034 bare URLs ×8, MD028 ×4, MD022 ×3, MD031 ×2, MD012, MD032). All are real whitespace/URL issues, and none conflict with yf conventions. Before the change there were 156.

## Acceptance

- In a repo opted into lint-on-edit, a fresh install produces `.markdownlint.jsonc` with the managed marker.
- The file content `yf-markdown-lint` generates or accepts produces **no** markdownlint findings from categories A and B. Probes: `<br>` in a table cell, `![](x.png "caption")`, an OKF bundle with frontmatter `title` + H1, and an `md_table_align.py --write`-formatted table.
- Re-running install over an operator-edited `.markdownlint.jsonc` leaves it unchanged and reports drift.
- pi-lens picks up the project config: the `effective_config` tool, or `markdownlint-cli2` run without `--config`, reads `.markdownlint.jsonc`.

## Related

- #102: marker rename to `.yf/markdown-lint-on-edit`. The config deployment should key on whichever marker is current.
- #324: ML001 false positive on `[[n]](url)`.
- #408: pi harness deploy gaps. The pi statusline is where this conflict surfaced.

