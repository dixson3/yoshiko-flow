---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #102: .markdown-lint-on-edit -> .yf/markdown-lint-on-edit: gitignore semantics + migrate.rs rename

- **Number:** 102
- **Title:** .markdown-lint-on-edit -> .yf/markdown-lint-on-edit: gitignore semantics + migrate.rs rename
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary
Move the markdown-lint opt-in marker `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit`, to consolidate under the `.yf/` sidecar. **No compiled code consumes the marker** (grep: zero hits in `markdown_lint.py` and `yf/src/*`) — it lives only in rule/SKILL/SPEC prose — so the move is mostly a rule/doc edit **plus** two decisions this issue must resolve.

## Two complications that MUST be addressed
1. **Gitignore commit semantics.** `.markdown-lint-on-edit` is a **committed** opt-in (shared with the repo). `.yf/` is gitignored via a single `/.yf/` anchor (`yf/src/preflight.rs:51-54`). Moving the marker under `.yf/` makes it gitignored unless a `!.yf/markdown-lint-on-edit` negation is added — otherwise the opt-in stops being shared. Decide and specify the intended commit semantics.
2. **Automatic migration.** To move an operator's existing root marker, add a `yf migrate` entry (analogous to the `SKILL_MAP` handling in `migrate.rs:35-49,88-121`) renaming `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit`. This **is** new code in `migrate.rs`. Preflight does not auto-migrate, so without it the move is manual.

## Requested change
(a) Update the four prose surfaces — `yf-markdown-lint/protocols/MARKDOWN_LINT.md`, `SKILL.md`, `SPEC.md`, `README.md` (+ the cross-ref in `yf-markdown-format/SKILL.md`/`SPEC.md`) and `web/content/pages/managed-files.md` — to the new path; (b) decide + implement the gitignore commit semantics; (c) add the `migrate.rs` rename entry for automatic migration.

## Refs
`docs/plans/plan-035-james-dixson-74d7ae/findings/exp-02-yf-layout-reality.md` (marker section). Epic-3 output of plan-035 (#99).

