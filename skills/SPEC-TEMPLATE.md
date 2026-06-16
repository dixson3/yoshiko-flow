# SPEC — <Skill Title> (`yf-<skill>`)

> Per-skill SPEC template. Copy to `skills/<skill>/SPEC.md` and fill in. The root `SPEC.md`
> (macro spec) composes every per-skill SPEC by reference; keep `REQ-<KEY>-NNN` ids unique to this
> skill (`<KEY>` = the short uppercase key from the root SPEC §4 catalog). Requirements use
> RFC-2119 "shall"; mark each verifiable one *(testable)*.

## 1. Purpose & scope

<One paragraph: what this skill does and the boundary of its responsibility. Pull the intent from
the skill's `SKILL.md` description; do not restate the whole trigger block.>

## 2. Requirements (`REQ-<KEY>-NNN`)

- **REQ-<KEY>-001** *(testable)* <a single, checkable behavior the skill shall exhibit>.
- **REQ-<KEY>-002** <…>.

> Group related requirements with sub-headings if the skill is large (e.g. `REQ-<KEY>-CLI-*`,
> `REQ-<KEY>-DATA-*`). Skills with topical design docs under `spec/*.md` SHOULD reference them
> instead of duplicating design detail.

## 3. Interfaces

- **CLI / scripts:** <any `scripts/*.py` subcommands, their inputs/outputs, JSON shape — or "none">.
- **Companion rule:** <the `protocols/<RULE>.md` this skill installs + its `manifest.json`
  versioning — or "none">.
- **Config / state:** <`.<skill>.local.json` keys, `.yf/<skill>/` state — or "none">.

## 4. Guardrails (`GR-<KEY>-NNN`) — optional

- **GR-<KEY>-001** *Drift:* <the tempting overreach>. *Rule:* <what the skill shall not do>.
  *Why:* <rationale>.

## 5. Verification

<How each *(testable)* requirement is checked — existing tests, the skill's own `check`, or a
plan-010 Epic 6 integration test naming the REQ id.>

## 6. References

- `skills/<skill>/SKILL.md`
- `skills/<skill>/spec/*.md` (topical design docs, if any)
- Root `SPEC.md` §4 (catalog entry) and `GUARDRAILS.md`.
