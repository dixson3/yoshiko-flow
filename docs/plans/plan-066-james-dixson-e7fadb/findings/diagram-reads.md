---
type: Finding
okf_spec: OKF-PLAN
description: "One dated read per regenerated PNG, looking for the semantic residue no text extractor catches. Six read; five clean, one carries a known cosmetic shorthand recorded rather than silently repaired."
id: diagram-reads
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# Diagram reads — all six regenerated PNGs

## Approach Tested

**measured:** each PNG below was **opened and looked at** after the Issue 5.3 re-render
(d2 `v0.8.2`, `--theme 0 --layout elk`). What is recorded is what the rendered image shows, not
what its `.d2` source says — those are different questions, and only the first is this file's.

**What a read is for.** `check_web_counts` compares counts and enumerated member ids against
frontmatter; it cannot see **label placement, overlap, truncation, visual grouping**, or whether
the picture communicates. Those are the residue, and they are why SC11 has no command.

> **AUTHORITY NOTE, stated rather than assumed.** These reads were performed by the **executing
> agent**, which is not a human. They are evidence *for* the Diagram-human-read capability gate,
> **not** a discharge of it. That gate is `gate_type: human` and is never auto-resolved however
> green its evidence — a green test establishes that a condition holds, never that a human
> authorized something.

## Result

### `architecture.png` — 2026-09-05 — CLEAN, and the repaired defect is visibly gone

- **`embedded skills (20)`** in the container label. Correct.
- **All four groups are depicted**, including `workflows group (3)`, which was **absent
  entirely** before this plan.
- **The membership defect is visibly fixed.** `beads group (5)` now reads
  `beads-init · beads-extra · beads-authoring · beads-hygiene · beads-upstream`. It previously
  read `plan · research · incubator` — the *workflows* skills, with a count of 8. Count and
  membership were both wrong, and only the count was ever noticed.
- **`upstream tracker / GitHub Issues (via gh)`** — the Epic-4 backend repair renders correctly.
- **Residue, cosmetic, not a defect:** elk orders the group boxes `utility, workflows, markdown,
  beads`, which is neither the source order nor the size order. Legible and unambiguous; no
  change made, because pinning box order would fight the layout engine for no reader benefit.

### `formulas.png` — 2026-09-05 — CLEAN

- The inset reads **"The five shipped standard formulas"** and lists all five, each with the
  step count its `.formula.toml` actually declares: `plan-execute` 1, `plan-investigate` 0,
  `plan-review` 4, `verify-artifact` 0, `yf-research` 7.
- **`verify-artifact` is depicted with its real nature** — an **aspect**, not a molecule, woven
  at cook time over a consumer's steps. Depicting it as a sixth molecule would have been a new
  false claim while fixing an old one.
- **Residue, cosmetic:** the inset is a monospace block on a very wide canvas (8546 px), so it
  reads small when the image is scaled to page width. Unchanged — the page renders the PNG at
  full width and it is legible there.

### `install-matrix.png` — 2026-09-05 — CLEAN

- **User scope:** `claude-code -> ~/.claude/skills/`, and `codex`, `opencode`, `pi`, `agents`
  all `-> ~/.agents/skills/`. Matches `harness_desc.rs`.
- **Project scope:** the same collapse under `<root>/`. Both columns were wrong before.
- **The `(lowercase-hyphen,max64)` annotation on `pi` is gone**, as `harness_desc.rs:381`
  requires — no shipped row may carry a `name_transform`.
- **Residue, cosmetic:** within each scope box elk orders the rows
  `opencode, claude-code, codex, pi, agents` rather than alphabetically or as in the source.
  Unambiguous; left alone.

### `lifecycle.png` — 2026-09-05 — CLEAN, with ONE RECORDED SHORTHAND

- The five-step spine renders correctly and reads left to right without overlap.
- **Recorded residue, and it is a real one.** The preflight box reads
  `ok / ignored / deps-missing / rule-drift`. The actual preflight status literal is
  **`system_deps_missing`**, not `deps-missing`. EXP-004 flagged this and classed it cosmetic;
  the read confirms it is a **deliberate label shorthand** in a box where the full literal would
  wrap, not a claim that the status is spelled that way.
- **Left as-is, deliberately, and the consequence is stated:** it will **not** survive a
  literal-equality checker over preflight status values. That is a known future-checker
  interaction, filed rather than pre-emptively broken — changing it now would widen the label for
  a checker that does not exist.

### `phase-model.png` — 2026-09-05 — CLEAN

- All six phases plus the session boundary render in order; the `parked` and `stale-approved`
  overlays sit on PHASE 4 where they belong, and `ABANDONED` / `COMPLETE` are visually distinct
  as terminal statuses.
- The status literals are a subset of the phase model's declared vocabulary (EXP-004 verified 10
  of 10 against `yf-plan/SKILL.md`).
- **Residue:** the diagram is dense at 11144 px wide, but every label is legible at full size and
  no edge crosses a box. No change.

### `tune-matrix.png` — 2026-09-05 — CLEAN

- Both halves correct: the config targets (`opencode`, `claude-code`, `codex`, and `pi ->
  DEFERRED (no config profile ships)`) and the rule managed-block targets.
- **`~/.config/opencode` and `~/.pi/agent` appear here and are CORRECT** — those are
  `surface_dir` values, which the harness collapse did **not** retire. Only their `/skills`
  subpaths were. This is the exact `(scope, field)` distinction pass-2 C12 insisted on, and the
  diagram was right about it all along.
- The ownership-manifest cylinder correctly names the touched-since-tune guard.

## Implications for Plan

1. **Six of six read; five clean, one carrying a recorded shorthand.** No semantic
   mis-assignment survives the re-render.
2. **`lifecycle.d2`'s `deps-missing` shorthand is the only open residue**, and it is recorded
   with its consequence rather than silently repaired or silently ignored.
3. **The gate still needs the operator.** These are agent reads; the capability gate is human.

## Recommendations

Resolve the Diagram-human-read gate only after the operator has looked at the six images. Carry
the `deps-missing` shorthand into Issue 8.4's filings as a follow-on, since a literal-equality
checker over preflight statuses would flag it.
