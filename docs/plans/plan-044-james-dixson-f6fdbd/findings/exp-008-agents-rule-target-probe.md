# exp-008 — What does the `agents` surface actually load? (D-11 probe)

**Issue:** 2.2 · **Plan:** plan-044 · **Date:** 2026-08-17 · **Upstream:** #156

## Question

Removing `skills upgrade`'s rules write (Issue 2.1) removes the **only** writer serving the
`agents` surface. Before deciding whether `yf harness tune` should take that over, D-11 requires
**measuring** what `agents` loads — because `SPEC.md:1251-1254` binds: *a rule target shall NOT be
a compiled-in guess*. An unevidenced `RULE_TARGETS` row would commit `tune` to writing an unread
file forever.

Two candidate outcomes:

- **A** — `agents` is a real rule-loading surface → add a `RULE_TARGETS` row with evidence.
- **B** — `agents` is a **skills-only bare surface** → say so, and stop pretending otherwise.

## Evidence

| # | Observation | Source |
| :-- | :-- | :-- |
| 1 | `agents` is **absent from the `PROBES` detection table** — it is never auto-detected, and is reachable only by an explicit `--harness agents` or the deprecated `--surface agents` | `harness_detect.rs` `PROBES` |
| 2 | `detect_project_scope`'s own comment calls it *"the shared `.agents` dir (codex + the **`agents` alias**)"* — the code already treats it as an alias, not a product | `harness_detect.rs` |
| 3 | `agents` and `codex` carry **identical** `user_subpath`/`project_subpath` (`.agents/skills`) | `harness_desc.rs` `DESCRIPTORS` |
| 4 | `agents` originates as a **`--surface` value**, mapped through `surface_alias()` — a surface name, not a harness | `harness_desc.rs` |
| 5 | **codex** — the actual harness installing skills to `.agents/skills` — reads rules from `~/.codex/AGENTS.md`, its own `RULE_TARGETS` row. The rules for that skills location are already served elsewhere | `managed_block.rs` `RULE_TARGETS` |
| 6 | There is **no `agents` binary**. `AGENTS.md` is a vendor-neutral convention; nothing installs an "agents" runtime that could read `~/.agents/rules/` | — |
| 7 | On this live machine `~/.agents/` contains `skills/` and `.skill-lock.json` — **no `rules/` dir and no `AGENTS.md`** | measured, `ls ~/.agents/` |
| 8 | No non-claude harness loads `.agents/rules/` | exp-001 |

## Verdict — OUTCOME B

**`agents` is a skills-only bare surface.** It is an alias naming *where skills go* under the
vendor-neutral AGENTS.md convention, not a harness that loads a rules file. No `RULE_TARGETS` row
is added.

Observation 7 is the direct measurement the decision turns on, and it cuts against **both**
candidate targets: neither `~/.agents/rules/` nor `~/.agents/AGENTS.md` exists on a machine that
has been running `yf` and installing skills to `~/.agents/skills/`. Had `agents` been a loading
surface, the removed `upgrade` write would have left `~/.agents/rules/YOSHIKO_FLOW.md` behind —
and it did not.

Observation 5 is what makes B safe rather than a loss: the skills installed at `.agents/skills`
are used by **codex**, whose rules are already deployed to `~/.codex/AGENTS.md`. Declaring
`agents` skills-only removes a write that served nothing; it does not orphan a real consumer.

## Consequences taken

1. **SPEC** — `REQ-YF-FLOW-008` gains the `agents`-is-skills-only wording (the Issue 0.1
   deferral, now discharged with evidence). `REQ-YF-TUNE-020`'s destination enumeration is
   **unchanged** — under B there is no new destination.
2. **`RULE_TARGETS` unchanged**, so `doc_agreement.rs`'s `RULE_TARGETS` iteration requires no new
   subpath and `tune_matrix_agrees_with_profiles_and_rule_targets` is unaffected.
3. **Config verdict unchanged.** `tune --harness agents` keeps returning
   `Refused{unknown-harness}`. The flip to `Deferred` was a consequence of outcome **A** only;
   naming it here so its *absence* is also on the record.
4. **Doc drift corrected.** `web/content/pages/harness-tune.md` claimed agents *"receive skills
   and rules"* — false under B, and it was **already false before this plan**, since agents has no
   `RULE_TARGETS` row and never did.
5. **`~/.agents/rules` dropped** from the preflight rule-candidate list. Fallout is Issue 2.3's.

## What would overturn this

First-party evidence that some tool reads `~/.agents/rules/` or `~/.agents/AGENTS.md` as an
always-loaded surface. That would be an **A** row — and per the SPEC precedent it would need to
carry that evidence, exactly as pi's row does.
