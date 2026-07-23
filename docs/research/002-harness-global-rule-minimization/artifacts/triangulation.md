---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Triangulation — harness global-rule minimization

Cross-references the 5 retrieval clusters (S-LC local-codebase, S-CC claude-code-docs,
S-CX codex-cli, S-OC opencode, S-PI pi-and-cross-harness) against the core question:
**which of the always-loaded companion-rule surface (`YOSHIKO_FLOW.md` aggregate) is
irreducible vs. replaceable by (a) richer per-skill SKILL.md description triggers or
(b) settings.json keys — per harness (claude-code, codex, opencode, pi)?**

Retrieved 2026-07-22. Findings are grouped by theme; each carries a confidence level, direct
quotes from supporting sources, and an explicit consensus/contradiction note. Findings with
fewer than 3 independent agreeing sources and no consensus are marked `[insufficient evidence]`.

## Method note on credibility scores

Web sources were scored with `credibility_scorer.py batch` (method: `script`). The scorer's
`domain_authority` component is keyword-based and **systematically underrates first-party
documentation and primary-source repositories** — official `opencode.ai`, `learn.chatgpt.com`
(Codex), and canonical GitHub source/repo URLs all receive `domain_authority = 30` despite being
authoritative primary sources, dragging their `overall` into the `verify`/`questionable` bands.
Where this report weights consensus, it therefore leans on the retrieval clusters' qualitative
credibility labels and cross-corroboration, not the raw numeric band alone. The 8 local `S-LC-*`
sources are `file://` paths the scorer cannot process; they were scored **manually** (method:
`manual`) as `high_trust` (overall 83) because they are the ground-truth artifacts of the system
under study (installed rules, `SPEC.md`, actual repo layout).

Distribution across all 37 sources: `high_trust` 10 · `verify` 21 · `questionable` 6 · `avoid` 0.

## Theme 1 — The universal always-loaded-prose vs. on-demand-skill split

**Confidence: high (consensus — all 5 clusters).** The recurring cross-cluster claim to test —
"every harness (claude-code, codex, opencode, pi) shares an always-loaded-prose
(AGENTS.md/CLAUDE.md) vs. on-demand-skill split" — is **corroborated by every independent
cluster**, and is the strongest finding in the corpus.

- Claude Code:
  > "In a regular session, skill descriptions are loaded into context so Claude knows what's
  > available, but full skill content only loads when invoked." [S-CC-2]
  > "Rules load into context every session or when matching files are opened. For task-specific
  > instructions that don't need to be in context all the time, use skills instead, which only
  > load when you invoke them or when Claude determines they're relevant." [S-CC-3]
- Codex — frames the exact split this research is about, and calls the two **complementary**:
  > "AGENTS.md ... gives Codex durable project guidance ... applies before the agent starts
  > work." [S-CX-2]
  > "It starts with metadata (name, description) for discovery ... It loads SKILL.md only when a
  > skill is chosen." [S-CX-2]
  > "complementary, not competing" [S-CX-2]
- opencode:
  > "Agent skills let OpenCode discover reusable instructions ... loaded on-demand via the native
  > `skill` tool—agents see available skills and can load the full content when needed." [S-OC-7]
  contrasted with the always-loaded `AGENTS.md` [S-OC-1].
- pi:
  > "Always-loaded policy starts in `AGENTS.md` ... Runtime behavior comes from `settings.json`
  > ..." [S-PI-6]; Pi "implements the Agent Skills standard" and "loads skills on-demand" [S-PI-3].
- Cross-harness standard framing:
  > "The AGENTS.md standard is the portable substrate for always-loaded prose; the Agent Skills
  > standard ... is the portable substrate for on-demand/description-triggered behavior." (cluster
  > synthesis of [S-PI-7], [S-PI-13])

**Consensus note:** 4 harnesses + the cross-harness standard cluster independently attest the same
two-tier architecture. No source contradicts it. This is the architectural premise on which the
whole minimization strategy rests, and it holds universally.

## Theme 2 — AGENTS.md is the portable always-loaded substrate; global + project files concatenated

**Confidence: high (consensus — 4 independent clusters).**

- Codex: global then project, concatenated, later-overrides-earlier:
  > "Codex concatenates files from the root down, joining them with blank lines. Files closer to
  > your current directory override earlier guidance because they appear later in the combined
  > prompt." [S-CX-1]
  > "In your Codex home directory (defaults to `~/.codex` ...), Codex reads `AGENTS.override.md` if
  > it exists. Otherwise, Codex reads `AGENTS.md`." [S-PI-11]
- opencode: global + project **combined, not a single winner**:
  > "The files are combined rather than selecting a single winner. They are rendered in this
  > order: global, then project files from the Location toward the project root. OpenCode does not
  > resolve conflicts ... keep broad guidance global and put scoped guidance in the relevant
  > project directory." [S-OC-3]
  > "You can also have global rules in a `~/.config/opencode/AGENTS.md` file. This gets applied
  > across all opencode sessions." [S-OC-1]
- pi: global + walk-up, concatenated:
  > "Pi loads `AGENTS.md` (or `CLAUDE.md`) at startup from: `~/.pi/agent/AGENTS.md` (global);
  > Parent directories ...; Current directory ... All matching files are concatenated." [S-PI-4]
- Cross-harness adoption/standard: "One AGENTS.md works across many agents" [S-PI-7]; 20,000+
  repos [S-PI-10]; nested files scope to subtrees [S-PI-12].

**Consensus note:** Codex, opencode, and pi independently implement the same
global-scope + project-walk concatenation model — this is the portable pattern for keeping generic
rules at global/user scope and repo-specific facts in the project file, which is exactly what
`../naba` does locally (Theme 6).

**Contradiction (flagged): Claude Code does NOT read AGENTS.md directly.** The one break in the
"one AGENTS.md works everywhere" claim [S-PI-7]:

> "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` ...
> create a `CLAUDE.md` that imports it" [S-CC-3]

This is a genuine cross-source contradiction against the standard's portability claim, resolved by
the `CLAUDE.md` → `@AGENTS.md` import shim (which this project's own `CLAUDE.md` uses). Confidence
in the contradiction itself: high (first-party Claude Code doc [S-CC-3], `high_trust` local
corroboration [S-LC-7]).

**Intra-cluster contradiction (resolved): opencode precedence.** [S-OC-1] reads "the first
matching file wins in each category ... only `AGENTS.md` is used," which superficially conflicts
with [S-OC-3]'s "combined, not ... a single winner." Resolution attested in-cluster: winner-per-
*category*, combined-*across*-categories; a docs-clarification issue [S-OC-4] and a self-corrected
bug report [S-OC-5] ("both AGENTS.md files ARE loaded ... verified via system-prompt-logger
plugin") both confirm the additive intent. Net: not a real behavioral contradiction.

## Theme 3 — The skill `description` is the on-demand trigger surface (metadata always visible, body on match)

**Confidence: high (consensus — 4 harnesses).**

- Claude Code:
  > "the `description` helps Claude decide when to load the skill automatically." [S-CC-2]
- Codex:
  > "A skill's SKILL.md instructions enter the context only when the agent determines the current
  > task matches the skill's description." [S-CX-3]
- opencode:
  > "`description` must be 1-1024 characters. Keep it specific enough for the agent to choose
  > correctly." [S-OC-7]
- pi: implements the same Agent Skills standard, loading "on-demand" [S-PI-3].

**Consensus note:** The description-as-trigger mechanism is uniform across harnesses, which is
what makes "move the trigger phrasing into the description" a portable strategy in principle. The
important **limit** (Theme 4) is where this breaks down.

**`[insufficient evidence]` — Pi's exact trigger model.** Whether Pi fires a skill purely off its
description (no explicit invocation) is **not stated verbatim** in any source; only [S-PI-3]
speaks to Pi skills and it says "on-demand" without spelling out description-match vs. explicit
invoke. 1 source, explicitly flagged as an absence in the retrieval. Do not assume Pi matches
Claude Code's auto-activation semantics.

## Theme 4 — The irreducible core: what a `description` cannot reliably fire

**Confidence: high for the mechanism (2 independent clusters: local + claude-code-docs).** The
local artifact's central claim is that certain rules cannot collapse into a `description` because
their firing signal is an event a description never sees. Claude Code's own docs **independently
corroborate the mechanism** and, crucially, **extend the replacement set beyond descriptions**.

The local claim (the rules' own preambles, `high_trust` [S-LC-1]):

> "The engine **executes** a repo's recorded validation recipe ... reports a verdict from an exit
> code — so a `description` alone cannot reliably fire it; this rule binds the on-edit and
> pre-push triggers." [S-LC-1]
> "The engine is `user-invocable: false`, so a `description` alone cannot reliably fire it."
> [S-LC-1]
> "The close-time / land-the-plane push trigger is NOT carried in this description — it lives in
> the always-loaded companion rule." [S-LC-4]

Claude Code corroborates **why** a description is insufficient — it is probabilistic and
truncatable:

> "The listing always contains every skill name, but if you have many skills, Claude Code shortens
> descriptions ... which can strip the keywords Claude needs to match your request." [S-CC-2]
> "there's no guarantee of strict compliance, especially for vague or conflicting instructions."
> [S-CC-3]

And Claude Code **names two replacements a description cannot provide** — a third and fourth
option beyond the research question's (a) descriptions / (b) settings keys:

> "`paths` | ... Glob patterns that limit when this skill is activated ... Claude loads the skill
> automatically only when working with files matching the patterns." [S-CC-2]
> "If the instruction is something that must run at a specific point, such as before every commit
> or after each file edit, write it as a hook instead. Hooks execute as shell commands at fixed
> lifecycle events and apply regardless of what Claude decides." [S-CC-3]
> "`FileChanged` | When a watched file changes on disk." [S-CC-4]

**Productive refinement (flagged, not a contradiction):** The local artifact classifies the
on-edit engine rules (CHANGE-VALIDATION, DRIFT-CHECK, MARKDOWN_LINT) as irreducible **as
always-loaded prose**; Claude Code shows the on-edit trigger can instead live in the skill's own
`paths` frontmatter (probabilistic, model-invoked) or a `FileChanged` hook (deterministic) —
**either of which removes the rule from the always-loaded surface entirely**. So for Claude Code,
these rules are *replaceable*, just not by a `description` and not by a settings key — by
`paths` frontmatter or a hook. Both clusters agree a description alone is insufficient; they agree
the honest deterministic path is a hook.

The genuinely irreducible always-loaded remainder (per [S-LC-1], corroborated in class by
[S-CC-3] Findings 6-7):

| Class | Example yf rules | Why a description can't carry it |
|:------|:-----------------|:---------------------------------|
| Override of a compiled-in native mechanism | PLANS (native plan mode), RESEARCH (built-in deep-research) | "the built-in is compiled into the CLI" — a description cannot override it [S-LC-1] |
| Cross-cutting mandate with no skill-description home | the two bd mandates folded into BEADS_INIT (bd-for-all-tracking; non-interactive shell flags) | no single skill owns them [S-LC-1] |
| Deterministic must-fire invariant | the false-negative invariant; silent-no-op invariants | descriptions/rules are probabilistic context [S-CC-2, S-CC-3]; determinism needs a hook |

**Per-harness caveat `[insufficient evidence]` for codex/opencode/pi.** The `paths`-frontmatter
and `FileChanged`-hook replacements are documented **only for Claude Code** [S-CC-2, S-CC-4]. The
codex, opencode, and pi clusters establish the same rules-vs-skills split (Theme 1) but **do not
enumerate a path-glob auto-activation field or an on-edit hook event** for skills. So the
fine-grained "which rule is replaceable" analysis is Claude-Code-grounded; for the other three
harnesses the on-edit-replacement mechanism is unattested (0 supporting sources) — treat cross-
harness replaceability of on-edit triggers as an open question, not a confirmed capability.

## Theme 5 — Settings/config is an enforcement + visibility lever, never a trigger supplier

**Confidence: high that every harness has a JSON config surface distinct from the prose surface
(consensus — 4 harnesses). Medium/single-source on the sharper "settings can't supply a trigger"
claim.**

Each harness separates prose rules from a JSON runtime config:

- Claude Code: `settings.json` — `disableBundledSkills`, `skillOverrides`,
  `skillListingBudgetFraction`, managed `claudeMd` [S-CC-1]; recommended baseline in [S-LC-5].
- Codex: `~/.codex/config.toml` — `project_doc_max_bytes`, `CODEX_HOME` [S-CX-1].
- opencode: `~/.config/opencode/opencode.json` + the `instructions` key [S-OC-2, S-OC-6, S-OC-1].
- pi: `settings.json` / `permissions.json` [S-PI-6].

**Sharper claim — settings replace *enforcement*, not the *trigger*.** Two facets:

1. Settings CAN replace the enforcement value of a prose mandate (2 sources — Claude Code
   [S-CC-1] + local baseline [S-LC-5]):
   > "prose only steers the model; it does not remove the disallowed mechanism. Setting these keys
   > aligns the runtime with the contracts so the model cannot reach for a mechanism a skill
   > forbids." [S-LC-5]
   > "a bare tool name in `permissions.deny` removes that tool's schema from the model's context
   > entirely" [S-LC-5]
   e.g. `todoFeatureEnabled: false` hard-enforces the bd-only mandate that BEADS_INIT carries in
   prose [S-LC-5]; `disableWorkflows` + `todoFeatureEnabled: false` are named the highest-impact
   alignment keys.
2. Settings CANNOT supply a skill's *when-to-fire* trigger (1 strong source — [S-CC-2]):
   > "visibility/enablement is a settings concern; *when-to-fire* is a frontmatter
   > (`description`/`when_to_use`/`paths`) concern. There is **no settings.json key that supplies
   > a skill's trigger**." (cluster synthesis of [S-CC-1], [S-CC-2])

**Consensus note:** The prose-vs-config separation is universal (4 harnesses). The directional
claim "config enforces / never triggers" is well-evidenced for Claude Code and consistent with the
other clusters' framing (config = runtime/permissions; prose = behavior), but is not independently
re-derived in the codex/opencode/pi clusters — so it is high-confidence for Claude Code, medium
cross-harness.

**opencode's `instructions` key is a distinctive lever** (single cluster, `verify` [S-OC-1]): a
config key that pulls arbitrary files (globs, remote URLs) into the always-loaded context, so
existing rule files need not be duplicated into `AGENTS.md`:

> "This allows you and your team to reuse existing rules rather than having to duplicate them to
> AGENTS.md." [S-OC-1]

Confidence: medium (1 cluster, official docs). No claude-code/codex/pi analog is attested.

## Theme 6 — Cross-harness portability of a `~/.agents/skills` / `~/.claude/skills` tree

**Confidence: medium-high (3 sources across 2 clusters).** A yf skill tree at user scope is
directly consumable by more than one harness:

- opencode reads Claude- and agent-compatible skill paths:
  > "Project Claude-compatible: `.claude/skills/*/SKILL.md`; Global Claude-compatible:
  > `~/.claude/skills/*/SKILL.md`; ... Global agent-compatible: `~/.agents/skills/*/SKILL.md`"
  > [S-OC-7]
  and falls back to Claude Code's rule files:
  > "Global rules: `~/.claude/CLAUDE.md` (used if no `~/.config/opencode/AGENTS.md` exists)"
  > [S-OC-1]
- pi loads skills from `~/.agents/skills/` and `.agents/skills/` [S-PI-3].

**Consensus note:** 2 independent harnesses (opencode, pi) plus the standard's cross-tool framing
support that skills placed under the shared `~/.agents/skills` / `~/.claude/skills` locations
travel across harnesses without per-harness duplication. This is the portable substrate for the
on-demand tier, mirroring AGENTS.md as the portable substrate for the always-loaded tier
(Theme 2).

## Theme 7 — naba as a local reference implementation of the minimization pattern

**Confidence: high within its single cluster (`high_trust` local primary sources); not a
multi-cluster consensus.** The local cluster is the only evidence, so this is a single-source-
group finding, but the sources are ground-truth primary artifacts.

> "CLAUDE.md is intentionally a thin pointer. AGENTS.md is the single source of truth ...
> (optimal-instructions: AGENTS.md primary, CLAUDE.md a thin @-include)." [S-LC-7]
> "the generic bd workflow conventions live in your user-scope agent rules and are not duplicated
> here. naba-specific facts:" [S-LC-6]

naba demonstrates the target end-state: generic rules kept at user scope (out of every repo);
project file reduced to repo-specific facts + a thin `CLAUDE.md` → `AGENTS.md` pointer; engine
skills (drift-check, markdown-lint) opted into per-repo via marker/manifest files
(`.markdown-lint-on-edit`, `DRIFT-CHECK.md`) rather than always-loaded prose [S-LC-8]. It carries
**none** of the `YOSHIKO_FLOW.md` aggregate in-repo. Consistency note: naba still repeats the
non-interactive-shell mandate locally [S-LC-6] — an instance of the very duplication the
minimization effort targets.

## Absences and insufficient-evidence items

| Item | Status | Sources / count |
|:-----|:-------|:----------------|
| Pi skill trigger model (auto-description-match vs. explicit invoke) | `[insufficient evidence]` | 1 ([S-PI-3]); explicitly flagged absence |
| A separate always-loaded "rules" surface in Codex distinct from AGENTS.md | Absence finding (none found) | [S-CX-2], [S-CX-3]; AGENTS.md is effectively it |
| Codex `developer_instructions` config key / AGENTS.md "re-read every turn" | `[uncertain]` — blog-only, unverified vs. official | 1 ([S-CX-3], `questionable`); official [S-CX-1] says chain built once per run |
| `paths`-glob auto-activation and on-edit hook for codex/opencode/pi skills | Unattested (0 sources) | documented only for Claude Code ([S-CC-2], [S-CC-4]) |
| Quantitative per-harness token cost of always-loaded prose vs. skills | Absence finding | not cited in any cluster; noted by [S-PI] and [S-CC] clusters as unpublished |
| opencode `instructions`-key analog in other harnesses | Unattested | only [S-OC-1] |

## Summary of consensus findings (3+ independent sources / clusters)

1. **Universal rules-vs-skills split** (Theme 1) — all 5 clusters. High.
2. **AGENTS.md portable always-loaded substrate, global+project concatenated** (Theme 2) — codex,
   opencode, pi, + standard cluster. High. Contradiction: Claude Code needs the CLAUDE.md import
   shim.
3. **Description is the universal on-demand trigger** (Theme 3) — 4 harnesses. High.
4. **A description is insufficient for event/deterministic triggers; the honest deterministic path
   is a hook** (Theme 4) — local + claude-code-docs. High for mechanism; Claude-Code-grounded for
   the specific `paths`/hook replacements.
5. **Every harness separates prose rules from a JSON config surface** (Theme 5) — 4 harnesses.
   High. Sharper "config enforces, never triggers": high for Claude Code, medium cross-harness.
6. **User-scope `~/.agents`/`~/.claude` skill tree is cross-harness portable** (Theme 6) —
   opencode + pi. Medium-high.
