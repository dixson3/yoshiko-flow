---
title: Summary — Harness Global-Rule Minimization
type: Research Report
okf_spec: OKF-RESEARCH
research_id: 002-harness-global-rule-minimization
bead: yf-2gyv
idx: '002'
topic: harness-global-rule-minimization
---

# Can companion rules be replaced by skill triggers + settings? A per-harness minimization strategy

## Executive summary

Across all four target harnesses — Claude Code, Codex, opencode, and Pi — the same
two-tier architecture holds: an **always-loaded prose surface** (`AGENTS.md` / `CLAUDE.md`)
and an **on-demand skill surface** whose *body* loads only when its *description* matches
the task. This split is corroborated across all four clusters and is the most portable
finding in the corpus — **strongest for Claude Code, Codex, and opencode**, each anchored to
first-party (`verify`/`high_trust`) docs [S-CC-2](sources.md#s-cc-2),
[S-CX-2](sources.md#s-cx-2), [S-OC-7](sources.md#s-oc-7). The **Pi leg is the
weakest-sourced**: the Pi *skills* half of the split is first-party [S-PI-3](sources.md#s-pi-3)
(`high_trust`, 80), but the Pi always-loaded *rules* half rests only on `questionable`-tier
community sources [S-PI-4](sources.md#s-pi-4), [S-PI-6](sources.md#s-pi-6) and carries an
`[uncertain]` tag (see Q6). The practical consequence: any rule whose firing signal is a task
the model is *about to choose* can, in principle, migrate from always-loaded prose into a
richer skill `description`. The always-loaded surface should shrink to only what a description
cannot carry.

The load-bearing remainder is small and specific. A `description` cannot reliably fire when
the trigger is (a) an **event the model never narrates** — a file edit, a pre-push gate, a
close-time push; (b) an **override of a mechanism compiled into the CLI** — native plan
mode, the built-in deep-research harness; or (c) a **cross-cutting mandate no single skill
owns** — the bd-for-all-tracking and non-interactive-shell rules. **Caveat on (b) and (c):**
these two verdicts rest on the local ruleset's *own design rationale* — that "the built-in is
compiled into the CLI" and that "no single skill owns" the bd mandates are self-asserted by
S-LC-1 (the yoshiko-flow ruleset describing itself), **not independently corroborated**. The
first-party corroboration below establishes only that a description is *probabilistic and
truncatable*, not that these specific mechanisms are un-overridable or homeless. Claude Code's
own docs confirm *why* a description is insufficient (the listing is truncatable and
compliance is probabilistic) and, critically, extend the replacement set beyond the research
question's two options: on-edit triggers can move into a skill's `paths` frontmatter (probabilistic,
model-invoked) or a `FileChanged` **hook** (deterministic, shell-executed) — either of which
removes the rule from the always-loaded surface entirely [S-CC-2](sources.md#s-cc-2),
[S-CC-3](sources.md#s-cc-3), [S-CC-4](sources.md#s-cc-4).

The decisive caveat is portability. The `paths`-frontmatter and hook replacements are
documented **only for Claude Code** [S-CC-2](sources.md#s-cc-2), [S-CC-4](sources.md#s-cc-4);
the Codex, opencode, and Pi clusters establish the same rules-vs-skills split but **0 sources
attest** a path-glob auto-activation field or an on-edit hook event for skills in those
harnesses (a pure absence finding — no CC citation carries this cross-harness negative). So
the fine-grained "this rule is replaceable" verdict is Claude-Code-grounded; for a
cross-harness install, the on-edit engine rules must currently stay as always-loaded prose
(or be gated behind an opt-in marker, as `naba` does), because no attested cross-harness
mechanism replaces them. Settings/config is universally an **enforcement and visibility**
lever, never a **trigger** supplier — this is an **absence finding**: no cited source
describes a settings key that supplies a skill trigger (cluster synthesis of
[S-CC-1](sources.md#s-cc-1), [S-CC-2](sources.md#s-cc-2), whose `paths`/frontmatter quote is
about *when-to-fire* living in frontmatter, not settings).

![Per-harness two-tier model (always-loaded prose + config surface vs. on-demand description-triggered skills) and the yf rule taxonomy of what can migrate out of the always-loaded surface.](diagrams/harness-rule-minimization.png)

## Q1 — In Claude Code, how much of the always-loaded companion-rule surface is load-bearing vs. replaceable?

The `YOSHIKO_FLOW.md` aggregate folds one fenced section per rule-bearing skill's companion
protocol — eight of eighteen yf skills carry one; the other ten are description-only
[S-LC-3](sources.md#s-lc-3). Single-source count from the local inventory:

> "yf-beads-init: BEADS_INIT.md ... yf-beads-upstream: UPSTREAM_TRACKING.md ...
> yf-change-validation: CHANGE-VALIDATION-TRIGGER.md ... yf-drift-check:
> DRIFT-CHECK-TRIGGER.md ... yf-markdown-lint: MARKDOWN_LINT.md ... yf-optimal-instructions:
> INSTRUCTIONS.md ... yf-plan: PLANS.md ... yf-research: RESEARCH.md"
> [S-LC-3](sources.md#s-lc-3)

The local artifact's central claim is that certain of these cannot collapse into a
`description` because their firing signal is an event a description never sees
[S-LC-1](sources.md#s-lc-1):

> "The engine **executes** a repo's recorded validation recipe ... reports a verdict from an
> exit code — so a `description` alone cannot reliably fire it; this rule binds the on-edit
> and pre-push triggers." [S-LC-1](sources.md#s-lc-1)
> "The engine is `user-invocable: false`, so a `description` alone cannot reliably fire it."
> [S-LC-1](sources.md#s-lc-1)

Claude Code's own docs independently corroborate *why* a description is insufficient — it is
probabilistic and truncatable:

> "The listing always contains every skill name, but if you have many skills, Claude Code
> shortens descriptions ... which can strip the keywords Claude needs to match your request."
> [S-CC-2](sources.md#s-cc-2)
> "there's no guarantee of strict compliance, especially for vague or conflicting
> instructions." [S-CC-3](sources.md#s-cc-3)

**How much is replaceable in Claude Code.** More than the research question's two options
allow, because Claude Code offers two replacement surfaces beyond `description` and
`settings`. The on-edit engine rules (CHANGE-VALIDATION, DRIFT-CHECK, MARKDOWN_LINT) — which
the local artifact classifies as irreducible *as always-loaded prose* — can instead live in
the skill's own `paths` frontmatter or a `FileChanged` hook:

> "`paths` | ... Glob patterns that limit when this skill is activated ... Claude loads the
> skill automatically only when working with files matching the patterns."
> [S-CC-2](sources.md#s-cc-2)
> "If the instruction is something that must run at a specific point, such as before every
> commit or after each file edit, write it as a hook instead. Hooks execute as shell
> commands at fixed lifecycle events and apply regardless of what Claude decides."
> [S-CC-3](sources.md#s-cc-3)
> "`FileChanged` | When a watched file changes on disk." [S-CC-4](sources.md#s-cc-4)

So for Claude Code specifically, the three on-edit engine rules are *replaceable* — just not
by a `description` and not by a settings key. Either `paths` frontmatter (model-invoked,
probabilistic) or a hook (deterministic) removes them from the always-loaded surface. Both
clusters agree a description alone is insufficient and that the honest deterministic path is
a hook [S-LC-1](sources.md#s-lc-1), [S-CC-3](sources.md#s-cc-3).

**Settings can replace enforcement, not triggers.** A settings key can hard-enforce the
value a prose mandate only steers, e.g. `todoFeatureEnabled: false` enforces the bd-only
mandate BEADS_INIT carries in prose [S-LC-5](sources.md#s-lc-5). (Note: `todoFeatureEnabled`
and `disableWorkflows` are attested **only** by S-LC-5, the operator's own recommended-settings
doc — they are **not** in the first-party settings snippet captured in S-CC-1, so their
existence as real Claude Code keys is unverified against first-party docs and may be
aspirational.)

> "prose only steers the model; it does not remove the disallowed mechanism. Setting these
> keys aligns the runtime with the contracts so the model cannot reach for a mechanism a
> skill forbids." [S-LC-5](sources.md#s-lc-5)
> "a bare tool name in `permissions.deny` removes that tool's schema from the model's context
> entirely" [S-LC-5](sources.md#s-lc-5)

But settings never supply a *when-to-fire* trigger — visibility/enablement is a settings
concern; when-to-fire is a frontmatter concern; there is no settings.json key that supplies a
skill's trigger (cluster synthesis of [S-CC-1](sources.md#s-cc-1),
[S-CC-2](sources.md#s-cc-2)).

**Bottom line for Q1.** Of the eight always-loaded sections: the three on-edit engine rules
become replaceable (via `paths`/hook, Claude-Code-only); the enforcement value of the bd
mandates can be hardened into settings but their *cross-cutting trigger* stays in prose; and
the override/must-fire rules stay irreducible (Q4). See the minimization verdict table below
for the per-rule call.

## Q2 — Per-harness global-instruction/rules mechanism, and what should live there

Every harness separates an always-loaded prose surface from a JSON/TOML runtime config, and
loads skills on-demand off a `description`. The concatenation model (global scope first, then
project files walking toward cwd, all combined) is uniform across Codex, opencode, and Pi
[S-CX-1](sources.md#s-cx-1), [S-OC-3](sources.md#s-oc-3), [S-PI-4](sources.md#s-pi-4). The
one break is that Claude Code reads `CLAUDE.md`, not `AGENTS.md`, requiring an import shim:

> "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses
> `AGENTS.md` ... create a `CLAUDE.md` that imports it" [S-CC-3](sources.md#s-cc-3)

The per-harness deliverable table:

| Harness | Always-loaded prose surface | JSON/config surface | On-demand skill trigger |
|:--------|:----------------------------|:--------------------|:------------------------|
| Claude Code | `~/.claude/CLAUDE.md` (user), project `CLAUDE.md`, `.claude/rules/*.md`; reads `AGENTS.md` only via a `CLAUDE.md` `@`-import [S-CC-3](sources.md#s-cc-3) | `settings.json` — `disableBundledSkills`, `skillOverrides`, `skillListingBudgetFraction`, `permissions.deny` (first-party [S-CC-1](sources.md#s-cc-1)); `todoFeatureEnabled`, `disableWorkflows` attested only by local baseline [S-LC-5](sources.md#s-lc-5), not first-party-verified | `description` auto-activation; also `paths` frontmatter (glob) and `FileChanged`/`PreToolUse` hooks [S-CC-2](sources.md#s-cc-2), [S-CC-4](sources.md#s-cc-4) |
| Codex | `AGENTS.md` (`~/.codex/AGENTS.override.md` then `AGENTS.md` global, then project root→cwd), concatenated, later-overrides-earlier, capped at `project_doc_max_bytes` (32 KiB) [S-CX-1](sources.md#s-cx-1), [S-PI-11](sources.md#s-pi-11) | `~/.codex/config.toml` — `project_doc_max_bytes`, `CODEX_HOME` [S-CX-1](sources.md#s-cx-1) | `description`-matched SKILL.md progressive disclosure [S-CX-2](sources.md#s-cx-2), [S-CX-3](sources.md#s-cx-3) |
| opencode | `AGENTS.md` — global `~/.config/opencode/AGENTS.md` + project files, combined not a single winner; falls back to `~/.claude/CLAUDE.md` [S-OC-1](sources.md#s-oc-1), [S-OC-3](sources.md#s-oc-3) | `~/.config/opencode/opencode.json` (8-tier precedence) + the `instructions` key that pulls external rule files into context [S-OC-2](sources.md#s-oc-2), [S-OC-1](sources.md#s-oc-1) | native `skill` tool, `description` 1–1024 chars; search paths include `.claude/skills`, `~/.claude/skills`, `~/.agents/skills` [S-OC-7](sources.md#s-oc-7) |
| Pi | **`[uncertain]`** — `AGENTS.md` (or `CLAUDE.md`) from `~/.pi/agent/AGENTS.md` (global) + parent dirs + cwd, all concatenated; system prompt via `.pi/SYSTEM.md` / `APPEND_SYSTEM.md`. Rests only on `questionable`-tier community sources [S-PI-4](sources.md#s-pi-4) (58), [S-PI-6](sources.md#s-pi-6) (54); no first-party Pi source attests the always-loaded rules mechanism | `settings.json` / `permissions.json` / `mcp.json` **`[uncertain]`** [S-PI-6](sources.md#s-pi-6) (`questionable`) | implements the Agent Skills standard, loads on-demand from `~/.pi/agent/skills`, `~/.agents/skills`, `.agents/skills` [S-PI-3](sources.md#s-pi-3) (first-party, `high_trust`) |

**What should live in the prose surface.** Only broad, always-relevant policy plus the small
irreducible-trigger set (Q4). opencode's docs state the principle directly:

> "keep broad guidance global and put scoped guidance in the relevant project directory."
> [S-OC-3](sources.md#s-oc-3)

Everything scoped or on-demand should move to a skill; everything about *runtime capability*
(disabling a tool, capping doc size, permissions) belongs in the config surface, not prose
[S-CC-2](sources.md#s-cc-2), [S-CC-1](sources.md#s-cc-1).

## Q3 — The minimal per-harness always-loaded rule set, and which yf rules collapse

The minimal always-loaded set per harness is the intersection of "must be in context every
turn" with "no on-demand or config mechanism can carry it." Concretely:

- **Claude Code** (richest replacement surface): minimal set = the override rules (PLANS,
  RESEARCH) + the cross-cutting bd mandates' *trigger* text + the deterministic must-fire
  invariants. The three on-edit engine rules collapse out — into `paths` frontmatter or a
  hook [S-CC-2](sources.md#s-cc-2), [S-CC-3](sources.md#s-cc-3), [S-CC-4](sources.md#s-cc-4).
  The bd mandates' *enforcement* collapses into `settings.json`
  ([S-LC-5](sources.md#s-lc-5)), leaving only their steering text.
- **Codex / opencode / Pi**: minimal set is **larger** because no `paths`/hook replacement is
  attested. The rules-vs-skills split holds [S-CX-2](sources.md#s-cx-2),
  [S-OC-7](sources.md#s-oc-7), [S-PI-3](sources.md#s-pi-3), so description-only rules collapse
  into skill descriptions, but the on-edit engine rules have no attested on-demand home and
  must stay as always-loaded prose (or be gated behind a per-repo opt-in marker as `naba`
  does — Q5). Treat cross-harness replaceability of on-edit triggers as an **open question**,
  not a confirmed capability [S-CC-2](sources.md#s-cc-2), [S-CC-4](sources.md#s-cc-4).

**Which yf rules collapse into skill triggers or settings** (the minimization verdict). The
irreducible remainder — rules whose firing signal is an event a description never sees — is
per [S-LC-1](sources.md#s-lc-1), corroborated in class by [S-CC-3](sources.md#s-cc-3)
Findings 6–7:

| yf rule (YOSHIKO_FLOW.md section) | Firing signal | Verdict | Replacement (and portability) |
|:----------------------------------|:--------------|:--------|:------------------------------|
| PLANS (override native plan mode) | must override a compiled-in CLI mechanism | **Irreducible (self-asserted)** | none — "the built-in is compiled into the CLI" per S-LC-1's own design rationale [S-LC-1](sources.md#s-lc-1); **single-source, self-referential** — no cited source independently confirms native plan mode is compiled-in and un-overridable by a description |
| RESEARCH (override built-in deep-research) | must override a compiled-in CLI mechanism | **Irreducible (self-asserted)** | none — same class, same single-source caveat [S-LC-1](sources.md#s-lc-1) |
| BEADS_INIT — bd-for-all-tracking mandate | cross-cutting, no single skill owns it | **Partly reducible** | *enforce* via `settings.json` `todoFeatureEnabled:false` + `disableWorkflows` (Claude-Code-only, keys unverified against first-party docs) [S-LC-5](sources.md#s-lc-5); trigger text stays prose. "No single skill owns it" is self-asserted by S-LC-1 |
| BEADS_INIT — non-interactive shell flags | cross-cutting, applies to all shell use | **Irreducible (as trigger, self-asserted)** | no skill-description home per S-LC-1's own rationale; `permissions.deny` can harden individual tools but not the general rule [S-LC-1](sources.md#s-lc-1), [S-LC-5](sources.md#s-lc-5) |
| CHANGE-VALIDATION-TRIGGER (on-edit / pre-push) | file edit + pre-push gate | **Reducible (Claude-Code-only)** | `paths` frontmatter or `FileChanged` hook [S-CC-2](sources.md#s-cc-2), [S-CC-4](sources.md#s-cc-4); **0 sources attest** a path-glob or on-edit-hook analog for Codex/opencode/Pi (pure absence — no CC citation carries this negative) |
| DRIFT-CHECK-TRIGGER (on-edit) | file edit; `user-invocable:false` | **Reducible (Claude-Code-only)** | `paths` frontmatter or `FileChanged` hook [S-CC-2](sources.md#s-cc-2); **0 sources attest** an analog elsewhere (absence finding) |
| MARKDOWN_LINT (on-edit) | `**/*.md` edit (opt-in marker) | **Reducible (Claude-Code-only)** | `paths` frontmatter or `FileChanged` hook [S-CC-2](sources.md#s-cc-2), [S-CC-4](sources.md#s-cc-4); already opt-in via marker file |
| UPSTREAM_TRACKING (close-time push) | session/plan close event | **Irreducible (as trigger)** | "NOT carried in this description — it lives in the always-loaded companion rule" [S-LC-4](sources.md#s-lc-4); a close-event hook is **not attested** (the retrieved hook set [S-CC-4](sources.md#s-cc-4) — `FileChanged`, `InstructionsLoaded`, `PreToolUse` — may be non-exhaustive, so this verdict is contingent on that set, not proven impossible) |
| INSTRUCTIONS (optimal-instructions on-edit) | edit of a project-root instruction file | **Reducible (Claude-Code-only)** | `paths` frontmatter / hook on the instruction-file globs [S-CC-2](sources.md#s-cc-2); **0 sources attest** an analog elsewhere (absence finding) |
| Deterministic must-fire invariants (false-negative invariant; silent-no-op) | must fire regardless of model choice | **Irreducible via description; hook-replaceable in CC** | descriptions are probabilistic [S-CC-2](sources.md#s-cc-2), [S-CC-3](sources.md#s-cc-3); determinism needs a hook |

The through-line: **description-only rules already collapsed** (10 of 18 skills carry no
protocol [S-LC-3](sources.md#s-lc-3)); **on-edit rules collapse in Claude Code** via
`paths`/hooks but not portably; **override and cross-cutting rules are the irreducible core**
everywhere.

## Q4 (secondary) — Which rules encode triggers a description cannot fire? Are they the irreducible core?

Yes — the rules that name, in their own preamble, a trigger a description cannot carry are
exactly the irreducible core. Three classes, from [S-LC-1](sources.md#s-lc-1) corroborated by
Claude Code docs:

| Class | Example yf rules | Why a description can't carry it |
|:------|:-----------------|:---------------------------------|
| Override of a compiled-in native mechanism | PLANS, RESEARCH | "the built-in is compiled into the CLI" — a description cannot override it. **Single-source, self-referential** (S-LC-1 describing itself); no independent source confirms these are compiled-in [S-LC-1](sources.md#s-lc-1) |
| Cross-cutting mandate with no skill-description home | the two bd mandates in BEADS_INIT | no single skill owns them. **Single-source, self-referential** (S-LC-1); no independent source confirms a cross-cutting mandate has no possible skill home [S-LC-1](sources.md#s-lc-1) |
| Deterministic must-fire invariant | false-negative invariant; silent-no-op invariants | descriptions/rules are probabilistic context [S-CC-2](sources.md#s-cc-2), [S-CC-3](sources.md#s-cc-3); determinism needs a hook |

The **productive refinement** (flagged, not a contradiction): the local artifact treats the
on-edit engine rules as irreducible *as always-loaded prose*, but Claude Code shows the
on-edit trigger can live in `paths` frontmatter or a `FileChanged` hook — so those are not
part of the irreducible core *for Claude Code*, only where no such mechanism exists
[S-CC-2](sources.md#s-cc-2), [S-CC-3](sources.md#s-cc-3). The genuinely irreducible core is
the override + cross-cutting + must-fire set, which no harness can carry in a description.

## Q5 (secondary) — What does naba do for global rules, and what is transferable?

`naba` is the local reference implementation of the target end-state. Its evidence is a
single cluster of `high_trust` ground-truth primary artifacts (not a multi-cluster
consensus), so treat it as a single-source-group finding [S-LC-6](sources.md#s-lc-6),
[S-LC-7](sources.md#s-lc-7), [S-LC-8](sources.md#s-lc-8).

> "CLAUDE.md is intentionally a thin pointer. AGENTS.md is the single source of truth ...
> (optimal-instructions: AGENTS.md primary, CLAUDE.md a thin @-include)."
> [S-LC-7](sources.md#s-lc-7)
> "the generic bd workflow conventions live in your user-scope agent rules and are not
> duplicated here. naba-specific facts:" [S-LC-6](sources.md#s-lc-6)

Transferable pattern: keep generic rules at user scope (out of every repo); reduce the
project file to repo-specific facts + a thin `CLAUDE.md` → `AGENTS.md` pointer; and opt into
engine skills per-repo via marker/manifest files (`.markdown-lint-on-edit`, `DRIFT-CHECK.md`)
rather than always-loaded prose [S-LC-8](sources.md#s-lc-8). naba carries **none** of the
`YOSHIKO_FLOW.md` aggregate in-repo. **Consistency caveat:** naba still repeats the
non-interactive-shell mandate locally — an instance of the very duplication the minimization
effort targets, and evidence that the cross-cutting shell rule has no clean skill home
[S-LC-6](sources.md#s-lc-6).

## Q6 (secondary) — What is Pi, and its global-instruction/rules mechanism?

Pi (`pi.dev`, `earendil-works/pi`) is a minimal, self-extensible terminal coding agent —
MIT-licensed, ~75k stars, 1.2M weekly npm downloads, actively released
[S-PI-1](sources.md#s-pi-1), [S-PI-2](sources.md#s-pi-2), [S-PI-5](sources.md#s-pi-5):

> "Pi is a minimal agent harness. Adapt Pi to your workflows ... Customize Pi with
> extensions, skills, prompt templates, and themes." [S-PI-1](sources.md#s-pi-1)

**`[uncertain]` — Pi's always-loaded rules mechanism.** It *appears* to mirror the
cross-harness pattern: always-loaded `AGENTS.md` (or `CLAUDE.md`) concatenated from
`~/.pi/agent/AGENTS.md` (global), parent dirs, and cwd; runtime behavior in `settings.json` /
`permissions.json` / `mcp.json`; host facts in `APPEND_SYSTEM.md`. **This rests only on
`questionable`-tier community sources** [S-PI-4](sources.md#s-pi-4) (58, a config-reference
repo), [S-PI-6](sources.md#s-pi-6) (54, a personal Pi config) — **no first-party Pi source
attests the always-loaded rules-surface mechanism.** The one `high_trust` first-party Pi
source [S-PI-3](sources.md#s-pi-3) (80) covers **skills only** (loaded on-demand under
`~/.pi/agent/skills`, `~/.agents/skills`, `.agents/skills` per the Agent Skills standard), not
the rules surface. So the Pi skills half of the two-tier split is well-sourced; the Pi rules
half is the weakly-sourced half of the corpus's flagship finding.

**`[insufficient evidence]` — Pi's exact trigger model.** Whether Pi fires a skill purely off
its description (no explicit invocation) is not stated verbatim in any source; only
[S-PI-3](sources.md#s-pi-3) speaks to Pi skills and it says "on-demand" without spelling out
description-match vs. explicit invoke. Single-source, explicitly flagged as an absence. Do
**not** assume Pi matches Claude Code's auto-activation semantics.

## Q7 (secondary) — Token-cost / portability tradeoffs of always-loaded rules vs. description-triggered skills

**Token cost — mechanism is clear, quantities are largely unpublished.** The mechanism is
well-attested: skill *descriptions* are always visible but the *body* loads only on match, so
moving a rule from always-loaded prose into a skill body pays its tokens only when relevant
[S-CC-2](sources.md#s-cc-2), [S-CX-2](sources.md#s-cx-2). Claude Code caps and truncates the
listing (a `skillListingBudgetFraction`, description cap [S-CC-1](sources.md#s-cc-1),
[S-CC-2](sources.md#s-cc-2)); Codex caps AGENTS.md at 32 KiB
[S-CX-1](sources.md#s-cx-1). One `questionable` blog source gives rough figures — skills list
~2% of context (~8 KB), AGENTS.md capped at 32 KiB — but this is `[uncertain]`, blog-only and
not officially confirmed [S-CX-3](sources.md#s-cx-3). A **quantitative per-harness token cost
of always-loaded prose vs. skills is an absence finding** — not published in any cluster.

**Portability tradeoff.** Always-loaded `AGENTS.md` prose is the *most* portable substrate:
one file is read (directly or via shim) by Claude Code (via `CLAUDE.md` `@`-import
[S-CC-3](sources.md#s-cc-3)), Codex [S-CX-1](sources.md#s-cx-1), opencode
[S-OC-1](sources.md#s-oc-1), Pi ([S-PI-4](sources.md#s-pi-4), `[uncertain]` / `questionable`),
and Copilot [S-PI-12](sources.md#s-pi-12) — an open standard [S-PI-7](sources.md#s-pi-7)
across 20,000+ repos [S-PI-10](sources.md#s-pi-10). Description-triggered *skills* are also portable at the shared
`~/.agents/skills` / `~/.claude/skills` locations (see cross-harness section). But the
specific *replacements* for on-edit rules — `paths` frontmatter and hooks — are
**Claude-Code-only**, so minimizing via those trades portability for a smaller always-loaded
footprint [S-CC-2](sources.md#s-cc-2), [S-CC-4](sources.md#s-cc-4). The portable-but-larger
option is to keep on-edit rules as prose or gate them behind opt-in markers; the
minimal-but-CC-only option is `paths`/hooks. This is the core tension the minimization effort
must price.

## Cross-harness skill-tree portability (supporting finding)

A yf skill tree at user scope is directly consumable by more than one harness (medium-high
confidence, 3 sources across 2 clusters). opencode reads Claude- and agent-compatible skill
paths and falls back to Claude Code's rule files
[S-OC-7](sources.md#s-oc-7), [S-OC-1](sources.md#s-oc-1):

> "Project Claude-compatible: `.claude/skills/*/SKILL.md`; Global Claude-compatible:
> `~/.claude/skills/*/SKILL.md`; ... Global agent-compatible: `~/.agents/skills/*/SKILL.md`"
> [S-OC-7](sources.md#s-oc-7)

Pi loads skills from `~/.agents/skills/` and `.agents/skills/`
[S-PI-3](sources.md#s-pi-3). So skills placed under the shared `~/.agents/skills` /
`~/.claude/skills` locations travel across harnesses without per-harness duplication —
mirroring AGENTS.md as the portable always-loaded substrate.

**opencode's distinctive `instructions` key** (single cluster, `verify`): a config key that
pulls arbitrary files (globs, remote URLs) into always-loaded context, so existing rule files
need not be duplicated into AGENTS.md — "reuse existing rules rather than having to duplicate
them to AGENTS.md" [S-OC-1](sources.md#s-oc-1). No Claude-Code/Codex/Pi analog is attested.

## Minimization verdict (synthesis)

1. **Description-only is already the default** — 10 of 18 yf skills carry no protocol
   [S-LC-3](sources.md#s-lc-3). The minimization target is the 8 that do.
2. **Irreducible everywhere (partly self-asserted):** PLANS + RESEARCH (override compiled-in
   mechanisms); the two bd mandates' *trigger* text (cross-cutting, no skill home); the
   deterministic must-fire invariants [S-LC-1](sources.md#s-lc-1), [S-LC-4](sources.md#s-lc-4).
   The override and cross-cutting verdicts are **single-source, self-referential** — they rest
   on S-LC-1's own design rationale (the yoshiko-flow ruleset describing itself), not on
   independent corroboration. The first-party docs corroborate only that a description is
   probabilistic/truncatable [S-CC-2](sources.md#s-cc-2), [S-CC-3](sources.md#s-cc-3) — which
   supports the must-fire-invariant leg, not the "compiled-in" or "no skill home" premises. The
   deterministic must-fire leg is the best-corroborated of the three.
3. **Reducible in Claude Code only:** the four on-edit rules (CHANGE-VALIDATION, DRIFT-CHECK,
   MARKDOWN_LINT, INSTRUCTIONS) → `paths` frontmatter or `FileChanged`/`PreToolUse` hooks
   [S-CC-2](sources.md#s-cc-2), [S-CC-3](sources.md#s-cc-3), [S-CC-4](sources.md#s-cc-4). No
   attested codex/opencode/pi mechanism replaces them — cross-harness they stay prose (or
   opt-in markers, per naba [S-LC-8](sources.md#s-lc-8)).
4. **Settings enforces, never triggers:** `todoFeatureEnabled:false`, `disableWorkflows`
   (local-baseline-only, unverified first-party), bare-name `permissions.deny` harden the
   bd/tool mandates' *value* [S-LC-5](sources.md#s-lc-5); **no cited source describes** a
   settings key that supplies a *trigger* (absence finding, cluster synthesis of
   [S-CC-1](sources.md#s-cc-1), [S-CC-2](sources.md#s-cc-2)).

**Answerable vs. open.** Fully answerable for Claude Code (rich, first-party-documented
replacement surface). For Codex/opencode/Pi, the rules-vs-skills split and AGENTS.md
concatenation are confirmed, but the on-edit-replacement mechanism is **unattested (0
sources)** — a genuine open question, not a confirmed capability. Pi's exact
description-trigger semantics and any quantitative token cost remain **absence findings**.

**Limitations.**

- *Self-referential core.* The "irreducible core" verdict for the override rules (PLANS,
  RESEARCH) and the two bd mandates rests **solely on S-LC-1**, the yoshiko-flow ruleset
  describing itself — the very artifact whose minimizability this research asks about. These
  are honestly single-source, self-asserted claims: no cited source independently confirms that
  native plan mode / the deep-research harness are compiled-in and un-overridable, or that a
  cross-cutting mandate has no possible skill home. The first-party corroboration
  [S-CC-2](sources.md#s-cc-2), [S-CC-3](sources.md#s-cc-3) establishes only that descriptions
  are probabilistic. The verdict is retained (it is the local design's stated rationale) but
  should be read as self-description, not external verification.
- *Self-study bias.* All eight local (S-LC-*) sources score `bias_neutrality: 55` and are the
  operator's own files — the same corpus the research is deciding whether to minimize. The
  primary evidence for *what is irreducible in yf* is yf describing itself. This is inherent to
  the question and unavoidable, but named here explicitly.
- *Pi leg weakest-sourced.* The Pi always-loaded rules mechanism rests only on
  `questionable`-tier community sources (`[uncertain]`, see Q6); only the Pi *skills* half is
  first-party.
- *Settings keys `todoFeatureEnabled` / `disableWorkflows`* are attested only by the local
  baseline S-LC-5, not verified against first-party Claude Code settings docs.

## Sources

- **[83/100]** YOSHIKO_FLOW.md — installed aggregated always-loaded ruleset. `file://` local
  primary source (manual score). [S-LC-1](sources.md#s-lc-1)
- **[83/100]** yf SPEC.md §3.3.1 — Aggregated ruleset. Local primary. [S-LC-2](sources.md#s-lc-2)
- **[83/100]** yf skills/protocols directory inventory. Local primary. [S-LC-3](sources.md#s-lc-3)
- **[83/100]** yf-* SKILL.md frontmatter descriptions (TRIGGER/SKIP contracts). Local primary.
  [S-LC-4](sources.md#s-lc-4)
- **[83/100]** Recommended Claude Code settings.json baseline. Local primary. [S-LC-5](sources.md#s-lc-5)
- **[83/100]** naba AGENTS.md — single source of truth. Local primary. [S-LC-6](sources.md#s-lc-6)
- **[83/100]** naba CLAUDE.md — thin pointer to AGENTS.md. Local primary. [S-LC-7](sources.md#s-lc-7)
- **[83/100]** naba repo directory layout. Local primary. [S-LC-8](sources.md#s-lc-8)
- **[84/100]** Copilot coding agent now supports AGENTS.md — GitHub Changelog. [S-PI-12](sources.md#s-pi-12)
- **[80/100]** Skills — Documentation — Pi. First-party docs (`high_trust`). [S-PI-3](sources.md#s-pi-3)
- **[79/100]** Claude Code settings — Claude Code Docs (first-party; domain_authority underrated).
  [S-CC-1](sources.md#s-cc-1)
- **[79/100]** Extend Claude with skills — Claude Code Docs (first-party). [S-CC-2](sources.md#s-cc-2)
- **[79/100]** How Claude remembers your project (memory) — Claude Code Docs (first-party).
  [S-CC-3](sources.md#s-cc-3)
- **[79/100]** Hooks reference — Claude Code Docs (first-party). [S-CC-4](sources.md#s-cc-4)
- **[76/100]** AGENTS.md — An Open Format (brightcoding). [S-PI-13](sources.md#s-pi-13)
- **[72/100]** Pi Coding Agent — pi.dev (first-party). [S-PI-1](sources.md#s-pi-1)
- **[71/100]** codex-rs/core/src/agents_md.rs — openai/codex (canonical primary source).
  [S-CX-4](sources.md#s-cx-4)
- **[71/100]** earendil-works/pi — GitHub. [S-PI-2](sources.md#s-pi-2)
- **[71/100]** @earendil-works/pi-coding-agent — npm. [S-PI-5](sources.md#s-pi-5)
- **[71/100]** packages/opencode/src/config/config.ts — opencode source (canonical primary).
  [S-OC-6](sources.md#s-oc-6)
- **[71/100]** agentsmd/agents.md — standard source repo. [S-PI-8](sources.md#s-pi-8)
- **[69/100]** AGENTS.md Emerges as Open Standard — InfoQ. [S-PI-10](sources.md#s-pi-10)
- **[68/100]** Custom instructions with AGENTS.md (Codex) — ChatGPT Learn (first-party).
  [S-CX-1](sources.md#s-cx-1)
- **[68/100]** Customization (Codex) — ChatGPT Learn (first-party). [S-CX-2](sources.md#s-cx-2)
- **[68/100]** Rules — opencode (first-party docs). [S-OC-1](sources.md#s-oc-1)
- **[68/100]** Config — opencode (first-party docs). [S-OC-2](sources.md#s-oc-2)
- **[68/100]** Instructions — opencode v2 docs (first-party). [S-OC-3](sources.md#s-oc-3)
- **[68/100]** Agent Skills — opencode (first-party docs). [S-OC-7](sources.md#s-oc-7)
- **[68/100]** Commands — opencode (first-party docs). [S-OC-8](sources.md#s-oc-8)
- **[68/100]** Custom instructions with AGENTS.md — Codex / OpenAI Developers (first-party).
  [S-PI-11](sources.md#s-pi-11)
- **[63/100]** AGENTS.md — official standard site (agents.md). [S-PI-7](sources.md#s-pi-7)
- **[59/100]** The Codex CLI Instruction Stack (danielvaughan blog) — `questionable`,
  `[uncertain]` where sole source. [S-CX-3](sources.md#s-cx-3)
- **[59/100]** opencode docs-clarification Issue #9282 — `questionable`. [S-OC-4](sources.md#s-oc-4)
- **[59/100]** opencode Bug Issue #22020 (self-corrected) — `questionable`. [S-OC-5](sources.md#s-oc-5)
- **[58/100]** pi-coding-agent-config / context-files.md — `questionable` (community reference).
  [S-PI-4](sources.md#s-pi-4)
- **[58/100]** AGENTS.md — AgentPatterns.ai — `questionable`. [S-PI-9](sources.md#s-pi-9)
- **[54/100]** OrestesK/pi — personal Pi config — `questionable`. [S-PI-6](sources.md#s-pi-6)
