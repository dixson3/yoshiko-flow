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

## RESOLVED — the OPERATOR accepted, 2026-09-08

### Entries for the two diagrams that did not exist when the six below were read

These are **ACCEPTANCE RECORDS, not agent reads.** Both files were created by plan-067 and were
part of the set the operator read and accepted on 2026-09-08; neither existed on 2026-09-05. They
are dated to the operator's reading and attributed to it.

#### `architecture-deps.png` — 2026-09-08 — ACCEPTED by the operator

Created by plan-067 Issue 7.0b. It carries what the layered stack sheds: the 8-token tool layer,
the `yf` subcommand paths, and all **twelve** `depends-on-skill` edges including the
workflows→utility relation `#373` names by hand. **3532 x 5080** — the best of three measured
layouts, and allowed to be tall because it is a reference, not an overview. Without this file the
restyle would have deleted 35 edges and silently reversed one of `#373`'s three named additions.

#### `formulas-map.png` — 2026-09-08 — ACCEPTED by the operator

Created by plan-067 Issue 4.4, replacing the generic `formulas.d2` ER meta-diagram that `#373`
asked to remove. It answers who owns each shipped formula and which subagent each step dispatches.
**3986 x 3662.** It also records that `planner`, `captor` and `lander` are dispatched by SKILL.md
prose rather than by a formula step — so their having no formula edge is correct, not a gap.


**The gate this file feeds (`yf-mol-a927.12`, Diagram human read) is RESOLVED, and the operator
resolved it.** Not this document, not the agent that wrote the reads above, and not the session
that executed either plan. The reads recorded above were **evidence**; the acceptance is theirs.

### What was accepted is the plan-067 RESTYLED set, not the six diagrams read above

The six 2026-09-05 reads below were performed against plan-066's own regenerated PNGs. **That set
was DECLINED on 2026-09-07** — not because any diagram made a false claim (all six were factually
correct and mechanically checked) but as a redesign request. That decline produced `#373` and
plan-067.

plan-067 then restructured the set twice: a first 20-diagram set, **also declined**, which
produced its Epic 7 restyle; and the 21-diagram restyled set, which the operator **accepted on
2026-09-08 on a single reading covering both plans** — same artifacts, same question.

So the current set is not the one described below. It is:

| | plan-066's set (read below) | **the accepted set** |
| :-- | :-- | :-- |
| Count | 6 | **21** |
| `architecture` | one crowded canvas | a layered stack, plus a sibling `architecture-deps` for the relations |
| `phase-model` + `lifecycle` | two diagrams | **combined** |
| `install-matrix` + `tune-matrix` | two diagrams | **combined** |
| `formulas` | one generic ER meta-diagram | **removed**; replaced by a map + one per shipped formula |
| per-skill | none | **11, generated** |

The acceptance covers that set. Its presentation is
`docs/plans/plan-067-james-dixson-de852a/findings/diagram-presentation.md`.

### `lifecycle.png`'s height was accepted KNOWINGLY

**8556 x 13362**, grown from 11602px. Expanding 95 sublabels into child boxes is what removed the
wordiness, and child boxes are **vertical structure** — so the fix for the first objection worked
against the aspect ratio. That regression was flagged **before** the read, on the exact dimension
an earlier read had objected to, and it was accepted anyway with the trade understood.

**A future reader should see a decision here, not an oversight**, and should not "fix" it without
asking: the shorter version is the wordy one.

### Why this matters beyond the two plans

**Three mechanically-green diagram sets were presented to this gate. Two were declined.** The
checks were not wrong on any of the three occasions — they were answering a different question
from the one that decides acceptance. That is why the gate is `gate_type: human` and why an agent
read is declared evidence rather than a discharge.

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
