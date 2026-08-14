---
type: Finding
okf_spec: OKF-PLAN
---
# Experiment 3: What importing `yf-herdr` into the repo actually touches

**Question.** `~/.claude/skills/yf-herdr/` exists only in user scope. What must change in
the repo for it to be a first-class skill, and what breaks if any of it is missed?

## What already conforms

The hand-authored skill is in better shape than expected. `SKILL.md` frontmatter already
carries the full repo convention:

```yaml
name: yf-herdr
description: >
  Delegate an approved yf-plan or a gated yf-research project to a NEW herdr tab ...
  TRIGGER when: ... SKIP for: ...
user-invocable: true
skill-group: utility
depends-on-tool: [herdr, uv]
depends-on-skill: [herdr]
```

Name, TRIGGER/SKIP-structured description, `user-invocable`, and a valid `skill-group` are
all present. Content is `README.md` 31 / `SKILL.md` 148 / `SPEC.md` 102 lines. It is
unstamped, confirming it was never installed from the repo.

## What is free — no work needed

Two mechanisms that looked like they would need per-skill registration turn out to be
glob/tree based, so `yf-herdr` is covered automatically the moment the directory exists:

- **rust-embed.** `yf/src/embed.rs` embeds `folder = "../skills"` wholesale; "the first path
  segment of any embedded relpath is its skill name." No registry, no enumeration.
- **DRIFT-CHECK.md.** Every relevant edge is glob-scoped — `skills/*/SKILL.md`,
  `skills/*/README.md`, `skills/*/SPEC.md`, `web/content/skills/*.md`. The `e-skill-page-*`
  edges added by plan-036 and the `e-readme-*` / `e-frontmatter` / `e-skillspec-skillmd`
  family all pick up a new skill with **no manifest edit**.

This removes what was assumed to be the bulk of the epic.

## What is required — and fails loudly if missed

### 1. `yf/src/testdata/install-parity.json` (blocking)

A **FROZEN GOLDEN** fixture enumerating all 18 skills: `skill_group` (per-skill group
mapping), `groups`, `group_members`, and transitive `closures`. `yf/src/parity.rs` asserts
the live tree matches it (REQ-YF-INSTALL-003/004). Adding a 19th skill without updating this
fixture is a **test failure**, not a silent gap.

Its `_comment` says the generator `install.py` is deleted and must not be run at test time,
so the golden must be **hand-updated**: add `yf-herdr` to `skill_group` (→ `utility`), to the
`group:utility` closure and `group_members`, and give it its own closure entry.

### 2. `depends-on-skill: [herdr]` must be dropped (blocking)

`yf/src/frontmatter.rs` documents `depends-on-skill` as "bare **in-repo** skill names this
skill requires," and `parity.rs` resolves transitive closures over it. `herdr` is a
third-party skill (it ships with the herdr binary), **not** in `skills/`. Importing the file
as-is points a closure edge at a non-existent in-repo skill.

The correct form is the soft-dep pattern this repo already uses — yf-plan's SKILL.md states
it plainly for `yf-change-validation`: *"This is a prose soft-dep: present → delegate, absent
→ fallback. NEVER add `yf-change-validation` to this skill's frontmatter `depends-on-skill`
— that is force-install, the wrong coupling."* So:

- **keep** `depends-on-tool: [herdr, uv]` — the binary genuinely is required;
- **drop** `depends-on-skill: [herdr]`, and express the skill relationship in prose.

### 3. `web/content/pages/architecture.md` counts (drift-check enforced)

The `e-web-skill-counts` edge asserts the page's claims equal the real frontmatter tallies.
Current text: "`yf` ships **18 skills**" with "workflows (3) / beads (5) / utility (6) /
markdown (4)". Adding a `utility` skill makes that **19 skills** and **utility (7)**. The
drift-check treats a mismatch as the *web page* drifting, so this FAILs the manifest until
updated.

### 4. `web/content/skills/yf-herdr.md` (plan-036 convention)

Every one of the 18 skills has an authored page. The hybrid model from plan-036: authored
prose is the page body; the "At a glance" block, `/skills/` index, and `SKILL_NAV` are
generated from frontmatter. The page must be VOICE.md-governed and is then guarded by the
three `e-skill-page-{desc,readme,spec}` edges — which, being globs, start enforcing the
moment the file exists.

### 5. SPEC-first ordering (AGENTS.md)

The repo mandates the SPEC edit lands ahead of implementation. `yf-herdr/SPEC.md` exists but
was authored outside the repo's REQ-* discipline; it needs review for REQ-id conformance and
the living-amendment-log convention before the rest of the import lands on top of it.

## Residual risk

`yf-herdr` depends on a third-party binary (`herdr`) that CI almost certainly does not have.
Its `SKILL.md` is gated on `HERDR_ENV=1`, so it should be inert rather than failing, but the
FULL-tier validation over the merged tree is the place this would surface. The plan carries
this as a risk with the `depends-on-tool` declaration as the mitigation, not as a solved
problem.
