---
title: beads → grite gap analysis
created: 2026-10-18
tags: [grite, beads, gap-analysis]
---

# beads → grite gap analysis

Sources: [01-grite-capabilities.md](01-grite-capabilities.md) (grite 0.5.3) and
[02-yf-beads-touchpoints.md](02-yf-beads-touchpoints.md) (yf `main` @ `a9e03f1`, bd 1.3.1).
This note is the main session's synthesis. The two research notes contain the evidence.

## 1. Headline findings

1. **The gap is larger than gates and formulas.** grite 0.5.3 lacks every capability on this list:
   - issue types
   - priority
   - statuses other than open/closed
   - a ready query
   - per-issue metadata
   - an external-ref field
   - parent-child and discovered-from edges
   - dependency-enforced close
   - batch/transactional writes
   - import
   - tracker sync

   yf treats every item on that list except tracker sync as **core** (02, summary table). Every one of them would become a yf-owned convention or computation on top of labels, bodies, links and `depends_on`.
2. **grite has correctness defects that block adoption on their own.** These are not missing features:
   - A fresh clone rebuilds 0 events and reports `ok: true` (#26/#27). The 01 sub-agent reproduced this.
   - Worktrees share one actor identity (#27). This contradicts the README, and yf-plan's worktree execution model depends on worktrees.
   - The JSON shape depends on whether the daemon is running.
   - Invalid `--state` values are accepted silently.

   The upstream project has been idle since 2026-07, with two authors and one release. **A grite-viability go/no-go therefore comes before any build phase.**
3. **yf already treats beads as a substrate and keeps the semantics itself.** Gate meaning (`gate_type`, `test_class`, session-boundary release), resume, upstream mapping and close-cascade are all yf logic over bd primitives. That makes a backend swap feasible in principle. The difficulty is that the primitives are **called directly**: about 800 `bd` invocations across prose and scripts, with five independent `--json` parsers and no abstraction layer.
4. **The live corpus is large.** 2,754 beads, about 5,500 edges and 1,320 metadata-bearing beads. A data migration (`bd export` → grite replay) is its own work item, and grite has no import.

## 2. Capability mapping

Strategy key: **G** = grite-native, **C** = convention (labels/body/links), **Y** = yf-computed or yf-owned
engine, **X** = no longer needed.

| beads capability (yf criticality) | grite primitive | Strategy | Proposed design |
| :-- | :-- | :-: | :-- |
| Issue types task/epic/gate/molecule (core) | labels | C | Reserved label `type:<t>`. The tracker layer validates it, because grite does not. |
| Priority 0–4 (core-light) | labels | C | Label `priority:<n>`. Sorting happens in yf, since grite allows only one `--label` filter per query. |
| Status in_progress/blocked/deferred (core) | open/closed only | C | Label `status:<s>` on open issues. The layer removes it on transitions and on close. |
| `--parent` hierarchy (core) | none | C | `related_to` edge plus `parent:<id>` label. Children of X = query `parent:<X>`. |
| `blocks` deps + cycle detection (core) | `depends_on` + DFS | G | Native. Cycle detection is equivalent. |
| `discovered-from` (core, upstream) | none | C | `related_to` edge plus `discovered-from:<id>` label. |
| `bd ready` (core, **hard**) | `dep topo` (order only) | Y | yf computes it: open, not `status:blocked/deferred`, not `type:gate/molecule`, and every `depends_on` target closed. The exact bd semantics need to be pinned with a **live** test first. Today no test runs `bd ready` against a real DB. |
| `--claim` (core) | `assignee add`, `lock acquire` | G+C | Lock (policy `require`), then assignee, then `status:in_progress`. Atomicity is weaker than bd's, and that has to be documented. |
| Metadata JSON + per-key set/unset + `--metadata-field` query (core, **hard**) | body (LWW whole), repo `context set k v` (LWW per key) | Y/C | **Experiment needed.** Candidates: (a) a fenced metadata block in the body, which is whole-body LWW and risks clobbering on concurrent writes; (b) repo-level `context set issue/<id>/<k> <v>`, which is per-key LWW, closer to `--set-metadata`, but unknown at scale; (c) a `meta:<k>=<v>` label for queryable scalar keys only. Likely answer: (b) for storage plus (c) for queried keys (`plan`, `research_dir`, `epic`, `job`). |
| `external_ref` (core) | `link add --url --note` (append-only) | C | A link with note `external_ref`, where the latest one wins. A missing `link remove` makes re-mapping append-only. |
| `close_reason` (core) | `issue close` (no reason?) + comment | C | Close comment prefixed `close_reason:`. Parsers (tombstone `hoisted upstream to `) read the last such comment. |
| Gates + `gate resolve` + gate exclusion from ready (core) | none | Y | A gate is an issue labelled `type:gate` with `gate:human\|auto`. Dependents `depends_on` it, and resolving means closing it. The ready computation excludes `type:gate`. The bd wrapper+gate pair (`Begin:`/`Gate:`) is **dropped**: it is a bd pour artifact that yf works around, not a feature yf wants. |
| Formula `mol pour` + vars + `id_mapping` (core, **hardest**) | none | Y | A yf-owned pour engine reads the existing `.formula.toml` and emits issues, edges and labels. It returns an `id_mapping` JSON in yf's own normalized shape. The coordinator call sites already parse `id_mapping` and are re-pointed in the same phase. |
| `mol wisp` / `burn` (convenience) | none | C | Label `ephemeral`; burn = close with reason plus an optional `gc` verb. Only yf-plan §2 uses wisps. |
| `bd batch` atomic dep wiring (convenience→core) | none | Y | Sequential writes, read-back verification and a compensating rollback. grite's add/remove-set CRDT makes a partial failure re-runnable. |
| `children`, `epic status`, `dep cycles`, `swarm`, `graph` (convenience) | list + dep list | Y | Derived in the tracker layer. |
| `bd config` store (`custom.upstream.*`, `dolt.local-only`) | repo `context set` | X/Y | Move to the committed `.yf/<skill>/config.json` tier (REQ-YF-PRE-004a), which already exists. `dolt.local-only` becomes **X**. |
| `bd remember` / `prime` (convenience) | label `memory` (syncs everywhere) | X/Y | Not a tracker concern. The clone-local tier moves to an untracked `.yf/` file. Keep the harness `bd prime` hook only while beads is installed. |
| Dolt init/repair/hardening (~2.6k LOC Rust, ~20 REQ-BINIT + PRE specs) | `grite init`, `doctor`, `rebuild` | X | **Replaced, not ported.** A small `grite` verify/init is needed. The fresh-clone and `rebuild` defects make verification more important, not less. |
| Formula staging into `.beads/formulas/` (REQ-YF-PRE-011, DOCTOR-004) | — | Y | Formulas are read directly from the skill dir. Staging goes away. |
| Worktree DB sharing (INV-2, `_bd_resolves_from`) (core) | refs are shared via git-common-dir; actor is shared | G (data) / **risk** (identity) | Data visibility probably works because refs are shared, but this has to be verified. Per-agent identity needs `--actor`/`GRITE_HOME` per worktree (agent playbook). |
| Upstream hoist (gh-direct) | none native | Y | yf-beads-upstream already writes via `gh`. Only its **reads** and the `external_ref`/tombstone writes go through the tracker layer, so it ports cleanly into a backend-neutral `yf-upstream`. |
| JSONL export | `export --format json\|md` | X | Exists only to manage bd side effects. |

## 3. Shim qualification: `bd`-shaped CLI backed by grite

The question is whether a `bd`-compatible shim, so that existing prose and scripts run unchanged against grite, is worth building in phases A/B.

**Criteria and findings**

| Criterion | Finding | Shim verdict |
| :-- | :-- | :-: |
| Surface to emulate | About 30 subcommands, plus flags whose **output shape** yf parses precisely: `id_mapping` keys `<f>.gate-<step>`, `dependency_type` vs `type`, `Begin:`/`Gate:` titles, the 50-row truncation, and gate-visibility rules. | ✗ |
| Fidelity required | yf's tests pin bd behaviour from prose and measurement, with no live coverage. A shim would have to reproduce bd's quirks, including those yf already works around. | ✗ |
| Emulation work needed anyway | The conventions in §2 (types, status, metadata, ready, gates, pour) have to be built regardless. Only the **interface shape** differs. | neutral |
| Call-site migration avoided | Yes, for scripts and prose, but they keep encoding bd-isms that phase D would then have to remove. | partial ✓ |
| Coexistence for b→c | A shim swaps globally (whichever `bd` is on PATH). Per-repo backend selection needs dispatch anyway. | ✗ |
| Risk of masking divergence | High. A shim that exits 0 with subtly different semantics is exactly the failure mode AGENTS.md warns about ("exit 0 with wrong data"). | ✗ |

**Recommendation: reject the `bd`-CLI shim.** Adopt an **intent-level tracker layer** instead: `yf tracker <verb>` in the Rust kernel, or a shared Python module, or both. It needs about 15 verbs (`create`, `show`, `list`, `ready`, `claim`, `update`, `meta set/unset/query`, `dep add/rm/list`, `close`, `gate resolve`, `pour`, `burn`, `ref set`), one normalized JSON contract, and two backends (beads, grite). Phase B first routes yf through this layer **on the beads backend**, which should not change behaviour and can be verified against the current suite. Switching the backend then flips a config value per repo. This keeps the approach the shim intended (keep using yf during the transition) without copying bd's quirks.

This recommendation is provisional. The plan-level red team for phase A should re-examine it.

## 4. Threats to the migration as a whole

1. **grite viability.** The upstream defects could leave grite unusable for yf's multi-worktree, multi-agent model. Options: contribute fixes upstream, maintain a pinned fork, or stop the migration. A **no-go is an acceptable outcome** of phase 0.
2. **Semantics we have never pinned.** The `bd ready`, gate-visibility and pour behaviours yf depends on are recorded only in prose. Porting them requires **characterization tests against live bd first**. This is valuable even if the migration stops.
3. **po-* skills (panopticon package).** They also call `bd` directly and rely on label and metadata-field queries. They are out of this repo but within the blast radius, so the tracker layer has to be consumable from them.
4. **yf-plan cannot target an integration branch** (README Q1). Every plan in this migration depends on that.
