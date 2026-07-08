# Contributing to yoshiko-flow

This repo owns the `yf-*` skills (yf-plan, yf-research, yf-change-validation,
yf-drift-check, yf-beads-*, yf-skill-authoring, yf-markdown-lint,
yf-optimal-instructions, yf-diagram-authoring, and the rest). The skills are
installed into consuming projects, so **their bugs are tracked here — not in the
project where the bug happened to surface.**

## Reporting a defect in a `yf-*` skill

### Where to file

- **`yf-*` skill defect → `dixson3/yoshiko-flow` (this repo).** The skill source
  lives here and the fix lands here.
- **Consuming-project defect → that project's repo.** A bug in the project's own
  content, config, or app code — e.g. a broken `CHANGE-VALIDATION.md` recipe the
  operator wrote — belongs to the project, even if a skill surfaced it.
- **Surfaced in a project but root-caused in a skill → file here.** Optionally
  leave a breadcrumb in the project repo if follow-up work is blocked on the skill
  fix, but the authoritative defect is the yoshiko-flow issue.

### What a good report includes

1. **Skill + entrypoint.** Which `yf-*` skill, and the offending file/function
   with a line anchor —
   e.g. `skills/yf-plan/scripts/plan_manager.py :: _change_validation_script (~L1726)`.
2. **Observed vs expected.** What the skill did vs. what it should have done. Quote
   the actual output (JSON verdict, error, or the misbehaving side effect)
   verbatim.
3. **Root cause**, when known — not just the symptom. State the incorrect
   assumption (hardcoded path, wrong scope, bad regex, missing fallback).
4. **Minimal confirmation.** The one or two shell commands that prove it — e.g. the
   path the resolver checks vs. where the file actually is.
5. **Environment / scope.** Install scope (user `~/.claude` / `~/.agents` vs.
   project `.claude` / `.agents`), skill version if available
   (`<!-- yf-skills: v=… -->` header or `manifest.json`), and `bd` version for
   beads-backed skills.
6. **Impact + blast radius.** Silent-wrong vs. crash; which invocations or repos
   are affected.
7. **Proposed fix**, if you have one — and note any shared helper that should be
   reused so two code paths don't drift. (A common `yf-*` failure mode:
   SKILL.md-side discovery logic and a script-side resolver diverging.)

### Anti-patterns

- Don't file skill bugs in the consuming project's tracker — they get lost from the
  fix.
- Don't report only the symptom (e.g. `engine: none`) without tracing it to the
  resolver.
- Don't paraphrase output; paste it. The epistemic rules the skills enforce apply
  to their own bug reports too.

### Example

[#74](https://github.com/dixson3/yoshiko-flow/issues/74) (yf-plan `validate-merged`
engine resolver) is the model report: entrypoint + line anchor, observed
`engine: none`, hardcoded-path root cause, a two-line confirmation, an install-scope
note, and a proposed fix that unifies discovery.
