---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #156: skills upgrade writes YOSHIKO_FLOW.md to the wrong surface for non-claude-code harnesses, unmanaged by the tune manifest and backed by no REQ

- **Number:** 156
- **Title:** skills upgrade writes YOSHIKO_FLOW.md to the wrong surface for non-claude-code harnesses, unmanaged by the tune manifest and backed by no REQ
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`yf harness skills upgrade` writes the `YOSHIKO_FLOW.md` rules aggregate to the **skills-sibling** `rules/` directory. For every harness except claude-code that is **not the surface the harness reads**, and the resulting file is **absent from the tune manifest**, so `yf harness tune --revert` cannot remove it.

The write is also backed by **no requirement**, and contradicts one.

## Measured

`skills upgrade --harness codex` and `harness tune --harness codex`, same machine, same embedded tree:

| Command | Wrote | Size | In tune manifest? |
| :-- | :-- | --: | :-: |
| `skills upgrade --harness codex` | `<root>/.agents/rules/YOSHIKO_FLOW.md` | 24,469 B (un-minimized) | **no** |
| `harness tune --harness codex` | `<root>/.codex/AGENTS.md` | 14,552 B (minimized managed block) | yes (`kind: "block"`) |

`.yf/harness-tune-manifest.json` records only `.codex/config.toml` and `.codex/AGENTS.md`. The upgrade-written file is an **orphan at a path codex does not read**, and `tune --revert` leaves it in place.

For claude-code the two agree exactly — `install --tune`, `upgrade`, and a standalone `tune` all produced sha1 `11c181f0b1053ac0cccd700b58be780614edd164`. So the defect is invisible on the harness most people use, and only bites the ones added by plan-033.

## No REQ authorizes it

`REQ-YF-FLOW-007` (`SPEC.md:675-682`), verbatim:

> `yf harness skills install` shall **no longer** write `YOSHIKO_FLOW.md`; the aggregate, its minimization, and its per-harness placement are owned by `yf harness tune` (`REQ-YF-TUNE-018..020`)…

`REQ-YF-INSTALL-008` says the same for `install`. **Neither mentions `upgrade`**, and no requirement grants it the aggregate. `status.rs:103`'s `common::install_rules_aggregate(&acted, &rules_dir, …)` is residual pre-plan-033 behavior: plan-033 relocated aggregation install→tune and declared tune the owner of *"the aggregate, its minimization, and its per-harness placement"*, but this call site was never revisited.

Note the wording — tune owns **per-harness placement**. That is precisely what `upgrade` gets wrong: it has one destination and no rule-target table.

## Suggested fix

Remove the `install_rules_aggregate` call from `status.rs:103`, making `upgrade` skills-only and consistent with `install`. Rules deployment then has exactly one owner, as `REQ-YF-FLOW-007` already says it should.

If `upgrade` should keep deploying rules, the opposite fix is to route it through tune's rule-target table and record it in the manifest — but that is re-implementing tune inside `upgrade`, and the SPEC already assigns the job elsewhere.

Either way this is a small, self-contained change. Worth a test asserting `upgrade` writes no file outside `skills_dir`.

## Why it is filed rather than fixed in plan-042

**plan-042** (install-time sync) stops calling `upgrade` — it uses `harness skills install --tune` instead, for this reason among four others. But that **routes around the defect rather than fixing it**: `upgrade` remains a public verb that any operator can run, and it will keep producing unmanaged orphans on codex/opencode/agents/pi. Flagged at that plan's pass-1 red-team review as an upstream-assessment gap.

Measured in `docs/plans/plan-042-james-dixson-98631b/findings/exp-005-upgrade-vs-install.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

