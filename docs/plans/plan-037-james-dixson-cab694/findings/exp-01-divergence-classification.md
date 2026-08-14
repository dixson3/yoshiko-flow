---
type: Finding
okf_spec: OKF-PLAN
---
# Experiment 1: Classify every user-scope ↔ repo divergence

**Question.** Which user-scope `yf-*` differences are genuine local patches (must be
upstreamed) and which are staleness (repo already ahead, safe to overwrite)? A blind
reinstall is only safe if no stale-side file hides a local edit.

**Method.** Three passes over `~/.claude/skills/yf-*` vs `skills/*`:

1. Raw `diff -rq` per skill.
2. Re-diff with the install stamp line filtered out.
3. For each remaining differing file, search **every historical version** of that path in
   `git log` for a blob that matches the user-scope content exactly (stamp-stripped). An
   exact match at some commit proves the file is an unmodified older release; no match
   proves a genuine local edit.

## Result 1 — the install stamp is pure noise

All 19 user-scope `SKILL.md` files differ from the repo by exactly one injected line:

```
<!-- yf-skills: v=0.4.0 tree=<sha256> -->
```

Any comparison that does not filter this line reports 19 false positives. After filtering,
22 files have real content differences.

## Result 2 — 21 of 22 differing files are stale-only

Every file below matches an exact historical commit, so the user-scope copy is an
unmodified older release:

| File | Matches commit | Dated |
|:--|:--|:--|
| `yf-beads-authoring/SKILL.md` | `bbfeec39` | 2026-07-11 |
| `yf-beads-init/SPEC.md` | `6b8e3256` | 2026-07-05 |
| `yf-beads-upstream/SPEC.md` | `6b8e3256` | 2026-07-05 |
| `yf-incubator/SKILL.md` | `aaf2b6c4` | 2026-07-19 |
| `yf-incubator/SPEC.md` | `aaf2b6c4` | 2026-07-19 |
| `yf-plan/README.md` | `2a8e4f00` | 2026-07-05 |
| `yf-plan/SKILL.md` | `0b0cc78c` | 2026-07-20 |
| `yf-plan/SPEC.md` | `0b0cc78c` | 2026-07-20 |
| `yf-plan/spec/phases.md` | `0b0cc78c` | 2026-07-20 |
| `yf-plan/spec/cli.md` | `0b0cc78c` | 2026-07-20 |
| `yf-plan/spec/data.md` | `0b0cc78c` | 2026-07-20 |
| `yf-plan/spec/prerequisites.md` | `2a8e4f00` | 2026-07-05 |
| `yf-research/README.md` | `2a8e4f00` | 2026-07-05 |
| `yf-research/SKILL.md` | `aaf2b6c4` | 2026-07-19 |
| `yf-research/SPEC.md` | `aaf2b6c4` | 2026-07-19 |
| `yf-research/spec/cli.md` | `aaf2b6c4` | 2026-07-19 |
| `yf-research/spec/data.md` | `aaf2b6c4` | 2026-07-19 |
| `yf-research/spec/prerequisites.md` | `2a8e4f00` | 2026-07-05 |
| `yf-skill-authoring/SKILL.md` | `c7196e6b` | 2026-07-15 |
| `yf-skill-authoring/SPEC.md` | `cc4071ca` | 2026-06-30 |
| `yf-skill-authoring/reference/SURFACE_CONVENTION.md` | `47f80844` | 2026-07-21 |

Every match is each file's most-recent version as of roughly 2026-07-21/22, so the install
is one coherent snapshot taken then — not an accreted mix. The content axis is uniform:
these copies predate the `.yf/<short>/` canonical-layout rework (they still describe
`.state/<skill>/` and `.<skill>.json` root dotfiles) and the `skill-group: beads` →
`workflows` regroup.

**Finding: no stale-side file hides a local edit. A refresh of these 21 files is safe and
loses nothing.**

Note the `v=0.4.0` in the stamp is the Cargo package version (`yf/Cargo.toml`), *not* the
`v0.4.0` tag (`dc664b2`). Comparing against the tag is the wrong baseline and produces
false "local edit" verdicts — the install snapshot postdates the tag.

## Result 3 — exactly one genuine local patch

`yf-plan/scripts/plan_manager.py` matches **none** of its 11 historical versions. Diffed
against its closest ancestor (`0b0cc78c`), the local delta is a single self-contained
28-line hunk replacing two module constants; the rest of the file is stale-only. See
`exp-02` for the isolated patch. A `plan_manager.py.pre-incubator-root.bak` sits beside it,
independently confirming a hand-edit.

## Result 4 — one user-scope-only skill and a rules-surface deviation

- `~/.claude/skills/yf-herdr/` (`README.md`, `SKILL.md`, `SPEC.md`; 281 lines total) is
  **unstamped** — hand-authored, never installed from the repo — and appears nowhere in
  `skills/`. See `exp-03`.
- The 8 companion rules are installed as **one concatenated**
  `~/.claude/rules/YOSHIKO_FLOW.md` bundling all 8 protocols, rather than 8 separate files.
  All 8 sections are stale against `skills/*/protocols/*.md`. Whether the bundling is a
  deliberate harness choice or install drift is **not resolved by this experiment** and is
  carried into the plan as an open question, not an assumption.

## Consequence for the plan

The three buckets need three different treatments, and conflating them would be the main
way this work goes wrong:

- Bucket 1 (21 files) — **refresh**, nothing to upstream. Verified safe.
- Bucket 2 (1 file, 28 lines) — **upstream**, re-implemented on the current idiom.
- Bucket 3 (yf-herdr) — **import**, new repo content.
