---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-rules-aggregate-write-path
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
---

# exp-001 — The YOSHIKO_FLOW.md rules-aggregate write path (#154, #156)

**Date:** 2026-08-17
**Question:** What writes YOSHIKO_FLOW.md, to where, per harness; what does `--revert` really do; and can the aggregate become a managed-block entry with existing machinery?
**Method:** source trace of `yf/src/**` at `0d900b1`, then **mechanical drive of `./target/debug/yf`** (debug reads `skills/` from disk) under a sandboxed `HOME`, all five harnesses, both entry points, then hand-edit + `--revert`. Repo untouched; writes landed in scratchpad.

## Headline

**#154 and #156 are one defect family with one root:** the aggregate has **two writers**, only one
is manifest-tracked, and the manifest's rules record is **path-only with no content guard**.
Fixing #154 in isolation is unsafe while `upgrade` still clobbers the same path.

## The call graph — one engine, two callers

Engine: `common.rs:245 install_rules_aggregate` → `read_flow_sections` (`:206`) →
`fold_standalone_rules` (`:292`, **deletes legacy standalones**) → `flow::upsert_section` →
`flow::reconcile` → `write_flow` (`:217`) → raw **`fs::write`** (`:229`), or `remove_file` when
zero sections remain (`:221`).

| Caller | Path | Minimized? | Manifest? |
| :-- | :-- | :-: | :-: |
| `harness tune` → `compute_rules_subop` (`mod.rs:344`) → `RulesDir` branch (claude-code only) | `deploy_rules_aggregate` (`mod.rs:424`) | no | yes, `kind:"aggregate"` |
| `harness tune` → `AgentsMd`/`AppendSystem` (codex/opencode/pi) | `managed_block::deploy_block` (`:188`) | **yes** | yes, `kind:"block"` |
| **`skills upgrade`** → `status.rs:103` | `install_rules_aggregate` **unconditionally, every harness** | **no** | **no** |

`skills install` writes no rules at all (`install.rs:61`, asserted `:466`) — that is
REQ-YF-INSTALL-008 / REQ-YF-FLOW-007. **`upgrade` was missed by that relocation.**

## #156 — confirmed exactly, and broader than filed

Measured, `HOME`-sandboxed, user scope:

| harness | `skills upgrade` writes | size | manifest? | `harness tune` writes | size | kind |
| :-- | :-- | --: | :-: | :-- | --: | :-- |
| claude-code | `~/.claude/rules/YOSHIKO_FLOW.md` | 24469 | no | same path | 24469 | `aggregate` |
| codex | `~/.agents/rules/YOSHIKO_FLOW.md` | 24469 | no | `~/.codex/AGENTS.md` | 14552 | `block` |
| opencode | `~/.config/opencode/rules/YOSHIKO_FLOW.md` | 24469 | no | `~/.config/opencode/AGENTS.md` | 14552 | `block` |
| pi | `~/.pi/agent/rules/YOSHIKO_FLOW.md` | 24469 | no | `~/.pi/agent/AGENTS.md` | 14552 | `block` |
| agents | `~/.agents/rules/YOSHIKO_FLOW.md` | 24469 | no | *(nothing — `rules: not_applicable`, exit 1)* | — | — |

#156's measured table reproduces byte-for-byte. Two corrections to carry forward:

1. **The divergence is not codex-specific — it is every non-claude harness.** Upgrade writes a
   24469 B aggregate into a `rules/` dir that no non-claude harness loads.
2. **There are two independent surface tables that disagree.** `harness_desc::DESCRIPTORS`
   (`:90-121`) declares **no rules surface at all** — only skills subpaths; the rules dir is
   *derived* (`dest.rs:59`, `skills_dir.parent()/rules`). The real declaration lives in
   `managed_block.rs:345 RULE_TARGETS`, which has **four rows (no `agents`)** and different dirs.
   `.agents` vs `.codex` is exactly the divergence the two-table split let exist silently.

**Hidden coupling — "just delete upgrade's rules write" is a behavior change, not a pure removal.**
`preflight.rs:213-217` hardcodes `~/.claude/rules`, `~/.agents/rules`, `<root>/.agents/rules`,
`<root>/.claude/rules` as rule-candidate dirs, and `doctor` reads `common::installed_rule_source`.
Removing the upgrade write could flip `doctor`/`preflight` to `rule_missing` for non-claude
harnesses. Budget for it.

**No REQ backs the upgrade rules write — confirmed.** The only upgrade requirement is
REQ-YF-MARK-004 (SPEC.md:732), which covers **skill files only**. Worse, the write actively
contradicts REQ-YF-FLOW-007 ("owned by `yf harness tune`") and REQ-YF-FLOW-003. The stale comment
at `status.rs:99-102` still describes the pre-plan-033 world — this is **relocation residue**.
`status.rs:165` (`remove`) mutates the aggregate off-manifest too.

## #154 — confirmed, and stronger than filed

`revert.rs:392 revert_rules` branches on the recorded `kind`:

- `"block"` (`:399-441`) → `remove_block`, write the prose-only remainder back; `remove_file` only
  if the remainder is whitespace-only. **Surrounding prose preserved.**
- **anything else** — a catch-all `_ =>` (`:444-457`), i.e. `"aggregate"` → `let existed =
  path.exists(); fs::remove_file(&path)`. **Unconditional delete. No content read, no checksum
  compare, no backup, no restore.**

Measured end-to-end (aggregate hand-edited with `OPERATOR HAND EDIT LINE` first):

```
pre-revert:  24494 B  .../.claude/rules/YOSHIKO_FLOW.md
             14575 B  .../.codex/AGENTS.md   ("# operator prose kept" prepended)

$ yf harness tune --harness claude-code --revert  → "kind":"aggregate","removed":true
$ yf harness tune --harness codex        --revert  → "kind":"block","removed":true

post-revert: claude YOSHIKO_FLOW.md → GONE (24494 B incl. the operator edit)
             codex AGENTS.md        → "# operator prose kept" survived
backups:     find -name '*.bak' -o '*.orig' -o '*backup*'  →  EMPTY
```

**There is no backup mechanism anywhere in the codebase.** Nothing is snapshotted before any
rules write. Revert deletes the file even when hand-edited, and even when it was written by
`skills upgrade` rather than by the tune being reverted — the manifest records only a path.

**REQ-YF-TUNE-022's `--revert` "restore" promise is half-implemented:** config scalars have the
touched-since-tune guard; the rules half has **no** equivalent. That gap is itself SPEC-vs-code
drift, and it is precisely what AGENTS.md's "rollback is asymmetric" note describes.

## Minimization

`minimize.rs`: `irreducible_core_bundle()` (`:182`) → `embedded_corpus()` (`:118`, the *same*
`common::embedded_rule_sections` the aggregate reads) → `build_bundle` (`:137`) applies the
hand-curated `CURATED_SELECTION` (`:89`) — 4 Keep (PLANS, RESEARCH, BEADS_INIT,
UPSTREAM_TRACKING), 4 Drop (the on-edit triggers) → `verify_agreement` (`:203`) at deploy.

Called **only** from the `AgentsMd|AppendSystem` branch (`mod.rs:367`). The `RulesDir` branch and
`skills upgrade` bypass it — hence 14552 vs 24469. Source corpus shared; minimization is not.

## Feasibility: aggregate → managed block

**Mostly yes with existing machinery — but block conversion alone does NOT satisfy #154.**

In favor: `deploy_block`/`remove_block` are path- and content-agnostic (`&Path`, `&str`);
`flow::parse` (`flow.rs:162`) is fence-driven and skips any line that is not a `<!-- yf-flow:`
open fence, so BEGIN/END wrappers parse cleanly and doctor/preflight/status/remove keep working
(*inferred* from parser structure + `remove_block` symmetry — a wrapped-file parse was not
executed); the manifest already supports `kind:"block"` with markers.

Blockers, by weight:

1. **It does not restore pre-tune content.** #154's literal ask needs a **new** backup/snapshot
   mechanism (prior sha or content in the manifest, or `.yf/backups/`). Block conversion only
   preserves *foreign prose in the same file*; a 100%-yf-written YOSHIKO_FLOW.md still hits
   `revert.rs:422`'s `out.trim().is_empty()` → `remove_file`. **Decide which semantics you want
   before scoping.**
2. **Two writers, one path** — converting only tune leaves upgrade clobbering the wrapper.
   **#156 must land before or with #154.**
3. `write_flow`'s delete-when-empty (`common.rs:219-224`) is a whole-file `remove_file`; under
   block semantics it must become `remove_block`.
4. **SPEC conflict.** REQ-YF-FLOW-001 mandates the banner as fixed header; REQ-YF-FLOW-004
   declares the aggregate "fully yf-managed… no hand-edit tolerance" — which is *why*
   delete-on-revert was written. A block implies prose may coexist. Amend before coding.
5. `fold_standalone_rules` (`common.rs:315`) **deletes operator-adjacent files** on every
   aggregate write — same blast radius, equally unbacked-up.
6. No `RULE_TARGETS` row for `agents`; the two surface tables disagree.

## Recommended sequence

1. **SPEC first:** amend REQ-YF-FLOW-004 for block placement; add a REQ making
   `skills upgrade`/`remove` rules-neutral (mirror of REQ-YF-INSTALL-008); add a REQ for a
   rules-side revert guard (content sha in `RuleRecord`, conservative-keep on mismatch — the
   exact analogue of the config touched-since-tune guard).
2. **#156:** delete `status.rs:103`, audit `status.rs:165`, add the negative assertion
   `install.rs:466` already carries, regression-test that `skills upgrade --harness codex`
   leaves `~/.agents/rules/` untouched, and handle the doctor/preflight fallout explicitly.
3. **#154 minimal + safe:** add `sha256` to `RuleRecord`; make the `aggregate` revert branch
   conservative-keep-and-report on mismatch. Small, closes the data-loss hole, no SPEC fight.
4. **#154 full:** route `write_flow` through `deploy_block`/`remove_block`, record `kind:"block"`
   — only after (2), and only if a real backup is in scope.
5. Consider consolidating `DESCRIPTORS` and `RULE_TARGETS` into one table with an explicit
   rules-surface column.
