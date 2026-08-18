---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #155: A file dropped from a skill lingers in the deployed tree, so that skill reports 'modified' forever — give install an opt-in --prune

- **Number:** 155
- **Title:** A file dropped from a skill lingers in the deployed tree, so that skill reports 'modified' forever — give install an opt-in --prune
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

A file **deleted or renamed inside a still-shipping skill** is never removed from the deployed tree, so that skill reports `modified` in `yf doctor` / `yf skills status` **permanently**.

`skill_health.unmodified` re-hashes the whole deployed skill tree (`REQ-YF-MARK-003`), so any leftover file makes the deployed hash diverge from `marker::embedded_tree_hash` forever. Nothing in the normal install path removes it.

## Why `upgrade` doesn't solve it in practice

`yf harness skills upgrade` **does** prune (`REQ-YF-MARK-004`, `common.rs:153-168`) — but `upgrade` is **single-destination**: it resolves via `common::dirs_for(args)` and `args.primary_harness()`, so on a multi-harness machine it silently deploys to the first harness only. An operator running `install` (multi-destination) never prunes; one running `upgrade` prunes only one harness.

## Measured blast radius

Prune walks `skills_dir/<transformed-name>` **per selected skill** — it removes files, then empty dirs. Probed against a fully-installed tree:

| Seeded artifact | Survived? |
| :-- | :-- |
| `my-custom-skill/SKILL.md` (hand-added skill dir) | **survived** |
| `README-local.md` (stray file at skills-dir root) | **survived** |
| `yf-plan/MY_NOTES.md` (hand-added file inside a yf skill) | **deleted** |
| `yf-plan/mydir/a.txt` + the emptied `mydir/` | **deleted** |

So the radius is narrow and predictable: hand-added *skill directories* and stray root files are safe; files placed *inside* a yf-owned skill directory are not.

Two things prune notably does **not** fix: a skill **removed** from the embedded set (its dir lingers — only `skills remove` deletes dirs), and a **renamed** skill (old dir lingers alongside the new one).

## Suggested fix

Give `install` an **opt-in `--prune`**, wiring the existing engine support through `install.rs:66` (currently a hardcoded `prune=false`). The engine already implements it correctly and transform-aware; this is a one-line change plus a flag.

SPEC-first: amend `REQ-YF-MARK-004` (or add a REQ) so `install` may prune opt-in, retaining `upgrade`'s assignment as the default-on case.

Worth a test pinning the blast radius above — specifically that a hand-added skill *directory* survives, since that is the case an operator would most fear.

## Minor, adjacent

`extra_deployed_files` uses `skills_dir.join(name)` **without** the harness name transform (`common.rs:173`), so `upgrade --dry-run --harness pi` under-reports the prune set. The real prune path is transform-correct, so this is a dry-run reporting bug only.

## Provenance

Split out of **plan-042** at its pass-1 red-team review (concern C10). It was scoped into that plan as decision D-P, then removed: it is orthogonal to the install-time sync, carries its own REQ amendment, and its only tie-in was one appended flag. Measured in that plan's E5 finding (`docs/plans/plan-042-james-dixson-98631b/findings/exp-005-upgrade-vs-install.md`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

