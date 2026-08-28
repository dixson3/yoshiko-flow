---
type: Plan
okf_spec: OKF-PLAN
id: plan-055-james-dixson-5f1c40
author: james-dixson
created: '2026-08-27'
status: executing
deliverable_class: standard
fingerprint: 8fd392119a135a82d6ddaf0ddab07d275aa2dce9a53323671af31d223721c5a9
epic: yf-mol-xga
---
# Plan: Deploy skills once to the shared .agents/skills root for every harness that reads it; keep only config/hooks/extensions/rules harness-specific

**ID:** plan-055-james-dixson-5f1c40
**Author:** james-dixson
**Created:** 2026-08-27
**Status:** executing
**Deliverable-class:** standard
**Epic:** yf-mol-xga
**Fingerprint:** 8fd392119a135a82d6ddaf0ddab07d275aa2dce9a53323671af31d223721c5a9

## Objective
Deploy skills once to the shared .agents/skills root for every harness that reads it; keep only config/hooks/extensions/rules harness-specific

## Motivation

`yf` deploys a **private, per-harness copy** of every skill: `~/.claude/skills`,
`~/.agents/skills`, `~/.config/opencode/skills` and `~/.pi/agent/skills`. Two of those
harnesses — **pi** and **opencode** — read `.agents/skills` with no configuration, so the
private copy buys nothing and creates a shadowing hazard.

It is not hypothetical. Running the plan-054 skew test in a real opencode session with a
distinct marker planted in each tree measured:

```
~/.config/opencode/skills/yf-plan  -> OPENCODE      <- where yf deploys FOR opencode
~/.agents/skills/yf-plan           -> AGENTS-codex  <- what opencode ACTUALLY loaded
```

opencode resolved `SKILL_DIR=/Users/james/.agents/skills/yf-plan`. **yf's opencode-specific
deployment is shadowed** on any machine that also has `.agents/skills` populated — which is
every machine with codex installed. pi, by contrast, loaded its own `~/.pi/agent/skills`.

**EXP-002 corrected the mechanism, and it is worse than #257 records.** The issue reasons from
"opencode PREFERS `.agents`" and asks whether that preference is stable. It is **not a preference
at all**. With one skill planted in three roots simultaneously, opencode's winner was measured
across five identical runs as `.config/opencode` four times and `.agents` once — the loader
processes matches with unbounded concurrency and **overwrites on collision**, so the winner is
whichever async read finishes last. It is a **coin flip, per process start**. pi, by contrast, is
deterministic first-wins.

That reframes the whole motivation. Today the race is harmless **only because** every tree comes
from a single `yf self install` and is byte-identical. The moment two copies diverge — a fix
deployed to `.config/opencode` while `.agents` lags — an operator gets a **nondeterministic choice
between two versions of the same skill**, silently, with nothing reporting it. That is materially
worse than "the wrong one always wins", and it is a direct argument for deploy-once rather than a
tolerable status quo.

Collapsing to one shared root makes the divergence **unrepresentable** rather than merely
detected, cuts the install work to one deployment, and shrinks the surface the
per-destination `SKILL_DIR_INSTALLED_AT` stamp (#248) has to disambiguate. The stamp stays —
it is still load-bearing for claude-code, which has its own root.

Who is affected: every operator running more than one harness, and every future fix whose
deployment could land in a shadowed tree.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #257 | Deploy skills ONCE to `.agents/skills` for every harness that reads it | include | The plan's primary deliverable | 2.2, 5.2 |
| #238 | `yf` ignores `XDG_CONFIG_HOME` / `CODEX_HOME` / `OPENCODE_CONFIG_DIR` when resolving harness directories | partial | **IN:** skills-root env-immunity for codex/pi/opencode, `CLAUDE_CONFIG_DIR` followed for claude-code skills (3.2), and an install-time warning. **OUT:** surface-dir resolution — yf still writes config/hooks/rules to the `$HOME`-derived path and merely *narrates* the mismatch (D-13). Calling this `include` would claim more than ships. Same descriptor table and same resolution function as #257; landing separately edits `harness_desc.rs` twice. #257 also **narrows** it — once skills leave the harness-private roots, `OPENCODE_CONFIG_DIR` governs config only | 0.4, 3.1, 3.2, 3.3 |
| #239 | pi's project-trust gate is unexercised by any test or smoke | partial | **IN:** a `yf doctor` axis and an install-time warning. **OUT:** the test/smoke coverage the issue actually asks for — neither 4.8 nor 4.9 exercises pi loading under an untrusted project. This ships VISIBILITY, not COVERAGE. #257 must prove pi loads from `.agents/skills`; the trust gate is the precondition under which pi loads anything | 4.8, 4.9 |
| #256 | `check-harness-smoke`: the state model is missing 'installed but consent-gated' | partial | **IN:** the tier-registration defect (4.6) — the row fires on the cheap tier and never on the land gate. **OUT:** the state-vocabulary rework itself, deferred with 4.1-4.5. Calling this `include` would claim a state model that no longer ships. | 4.6 |
| #121 | Pi config tuning re-verification | exclude | Config surface, which this plan explicitly leaves harness-specific. No shared code path | — |
| #243 | harness tune OVERWRITES a pre-existing rules aggregate with no backup | exclude | Rules surface, not skills. Adjacent hazard class, no shared code path | — |
| #240 | codex budget check models ONE `AGENTS.md` | exclude | Rules surface | — |
| #255 | Cut the v0.5.0 release: push the tag | deferred | Sequencing only. This plan lands **before** the tag because it changes what "multi-harness support" means in the release notes — cheaper to decide before the tag than to caveat after | — |

## Scoping Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | **Roll in #238, #239 and #256**; exclude #121/#243/#240 | Operator decision. The three included issues touch the descriptor table, the pi load path, or the harness smoke — all of which this plan rewrites anyway. The three excluded ones live on the config/rules surface this plan deliberately does not move |
| D-2 | **Migration = ownership-checked removal.** Deploy to the shared root and delete the now-unread private trees, but only copies `yf` can prove it authored and that are unmodified | Operator decision. Leaving them makes them exactly the stale shadowing copies this plan exists to eliminate; removing unconditionally would delete a skill an operator placed by hand |
| D-2a | **The ownership token is the per-copy MARKER, not the tune manifest** — EXP-004 measured that no ownership manifest covers the skills surface and none ever has | **Amends D-2's mechanism, preserving its intent exactly.** `SurfaceRecord` carries only `config` and `rules`; `grep -i skill` over `manifest.rs` returns one hit and it is a comment; over `revert.rs`, zero. The skills install path writes no ownership record at all. The operator's intent — never delete what yf did not author — is unchanged and is *implementable* via the deployed `SKILL.md`'s `<!-- yf-skills: … -->` marker plus a recomputed marker-stripped tree hash, which `status` already computes and `REQ-YF-MARK-001/002/003` already specifies |
| D-2b | **FOUR removal outcomes, defaulting to dry-run:** `owned-and-unmodified` → delete; `owned-but-modified` → **keep and report**; `no-marker` → keep and report as **foreign**; `undetermined` → keep and report as **unjudgeable** | Mirrors `REQ-YF-TUNE-029`'s conservative-keep posture. **The fourth outcome is not padding — collapsing it into `foreign` asserts a positive fact ("an operator placed this") from an ABSENCE of evidence**, which is the #181 / #207 / #256 defect class this plan cites three times. Three distinct facts land there: an unreadable `SKILL.md`, a malformed marker, and a **symlink** — the last is live on the target machine (`~/.agents/skills/terminal-browser` points into an app directory, so a tree-hash walk that follows it hashes someone else's tree) |
| D-2f | **Conservative-keep and race-elimination are in TENSION, and the plan resolves it explicitly rather than silently** | D-2b keeps an `owned-but-modified` copy; D-2e removes the old root to stop opencode's measured 4:1 race. A kept modified copy in a private root **is** the divergent duplicate R3 exists to eliminate. Resolution: keeping is still correct (never destroy operator edits), but the dry-run report must **flag any kept directory whose skill name also exists in the shared root as a live divergence hazard**, and the operator decides per directory. Silent keeping would let this plan re-create the exact hazard it is written to remove |
| D-2c | **Do NOT reuse `yf harness skills remove` for migration; file its behaviour as a defect** | EXP-004 measured it deleting a hand-placed operator directory — `SKILL.md` plus `OPERATOR-DATA.txt`, no yf marker — reporting `"removed":[…]` with no warning. It is a bare `remove_dir_all` on name match (`status.rs:249-254`). Shelling migration out to it *is* the unchecked deletion D-2 rejects. It also joins the raw name rather than `transform_skill_name`, so it is already wrong for pi |
| D-2d | **The migration is its own epic, sequenced AHEAD of the descriptor change** | One primitive is genuinely missing: a **directory walk**. `status` is name-keyed and blind to directories outside the embedded set, so a skill yf deployed and later renamed or dropped is invisible to every existing enumeration. Honest sizing: a SPEC requirement, the enumerator, a three-outcome classifier over existing `marker` helpers, a dry-run/apply surface, and tests — more than "delete the private trees", less than "build a manifest" |
| D-2e | **Migration must be a MOVE, not an ADD** | Independently corroborated from a second direction by EXP-002: because opencode's collision resolution is *racy*, leaving the old copy in place is not a safe fallback — it is a per-process coin flip between two possibly-divergent copies. Removal must happen in the same operation that writes the new root |
| D-3 | **Apply the single-root rule to BOTH user and project scope**, without gating on a measurement | Operator decision, taken knowingly. The stated concern — that project-scope behaviour is unmeasured — is mitigated rather than dismissed: EXP-002 stands up the harnesses for user scope anyway, so it additionally **reports** project-scope resolution at near-zero marginal cost. The measurement informs; it does not block |
| D-4 | **DECIDED: claude-code KEEPS its private `.claude/skills` root.** The shared root is **not** universal | EXP-001 measured claude-code **2.1.247**: the string `.agents/` occurs **zero times** in the 222 MB binary; the auto-load constant is a hardcoded `[".claude/skills",".claude/commands"]`; the root prefix table enumerates exactly two `.claude` roots; and a headless probe with a skill in `.agents/skills` and a control in `.claude/skills` returned **only the control**, twice. No env var can add a root — all ten `CLAUDE_*SKILL*` vars are disable/telemetry switches, none a path. #257 raised this as an open question and refused to assume; the answer is **no**, so the private-root case in `harness_desc.rs` stays and the plan does not shrink on this axis. **The `SKILL_DIR` resolver's dual `.claude`/`.agents` search is therefore correct and load-bearing, not redundancy to prune** |
| D-4a | **A universal single root remains possible only via a genuinely different design, which is OUT OF SCOPE here** | EXP-001 found one configured route: claude-code plugin manifests carry a `skills` field that adds arbitrary directories. Pointing it at `.agents/skills` would work — but that is *shipping a yf plugin manifest* rather than *copying a tree*, a separate architectural decision, and it is **untested**. Recorded as a hypothesis, not folded into D-4 |
| D-5 | **Config, hooks, extensions and the rules aggregate stay harness-specific** | The whole point of the split: the descriptor conflates two concerns. A skills root is shared where the harness agrees to read it; a surface dir never is |
| D-7 | **Drop pi's `NameTransform::LowercaseHyphenMax64`** from the descriptor (or explicitly re-scope it as belt-and-braces) | EXP-002 measured pi 0.84.3 loading directories named `Zz_Probe_Name` and `Zz_Probe_Shared_NoName` — name validation is warn-only; only a missing `description` is fatal. The transform is the **only** thing that would force pi a separate tree from codex/agents, and it is measurably not a pi requirement — though the drop is best read as **belt-and-braces removal on a 0.84.3-scoped measurement**, since EXP-002 grades "safe for *all* future skill names" as *inferred* and the `max64` arm specifically was never exercised (2.3's tests add a >64-character probe). **Inverse asymmetry found:** opencode is the stricter harness — it takes the skill name *only* from frontmatter and silently skips a `SKILL.md` with no `name:`, ignoring the folder name entirely. A shared tree must therefore keep `name:` in every `SKILL.md` (yf already does); the folder name is free |
| D-8 | **Fold in the two harness-smoke REGISTRATION defects** EXP-006 found, since the row is being rewritten anyway | Both make the gate green-by-accident: (a) `change_validation.py` maps any nonzero row exit to `fail`, so the smoke's deliberate exit 2 is reported as FAIL, contradicting `CHANGE-VALIDATION.md:53`'s own prose; (b) the row sits in the `### fast` table while its note says "FULL-tier ONLY". Verified directly against the engine: `fast` and `full` parse to **independent lists** and `full` is not a superset, so the row **never runs at FULL** — and *does* run on any unscoped `--tier fast`. The expensive real-model-call check fires on the cheap tier and never on the land gate it was written for |
| D-9 | **The descriptor's env override attaches to the SURFACE column by default, and to the SKILLS column only for claude-code** | EXP-003 measured `.agents/skills` as **env-immune on three of four harnesses**: codex reads `$HOME/.agents/skills` and `CODEX_HOME` does *not* move it; pi's `~/.agents/skills` survives `PI_CODING_AGENT_DIR`; opencode loaded it under all four override combinations. So moving skills to the shared root removes the skills-root env sensitivity for codex, pi and opencode **outright**. claude-code is the exception in both directions — it cannot read the shared root (D-4) and its `.claude/skills` *is* moved by `CLAUDE_CONFIG_DIR` |
| D-10 | **The precedence column is THREE-valued — `replace` / `additive` / `none` — never a boolean** | EXP-003 measured opencode as the odd one out: `XDG_CONFIG_HOME` **replaces** its config root while `OPENCODE_CONFIG_DIR` **adds** one (7 roots vs 8, default retained; the two vars are orthogonal, not competing). Any yf logic shaped "if `$VAR` set, install there *instead*" would **under-install for opencode and over-install for the other three** |
| D-11 | **`XDG_CONFIG_HOME` is honoured by opencode ONLY** | Measured dynamically and statically. codex's occurrences are vendored `gix` git-config code; claude-code's 25 are git discovery, fish completions, ripgrep docs and an env-scrubbing deny-list; **pi references it zero times anywhere**. Treating it as a general fallback would be wrong for three of four harnesses |
| D-12 | **opencode's current user-scope skills subpath is the WORST available choice, independently of this plan** | `.config/opencode/skills` is the one opencode path `XDG_CONFIG_HOME` relocates, while opencode also reads `~/.agents/skills` and `~/.opencode/skills`, both env-immune. The collapse to `.agents/skills` therefore fixes a pre-existing latent defect rather than merely tidying — and `codex → .agents/skills` was already the measurably correct row |
| D-13 | **Ship an install-time WARNING for the replace-semantics vars, not a full `dest.rs` env resolver** | EXP-003 measured the concrete #238 failure: with `CODEX_HOME` / `PI_CODING_AGENT_DIR` / `CLAUDE_CONFIG_DIR` exported, yf's `$HOME`-relative install writes where the harness no longer reads — a **silent** no-op, because the default dir still exists and looks correct on disk. After D-9 only `CLAUDE_CONFIG_DIR` still needs the resolver to actually follow it; a per-harness "your override disagrees with the default" warning covers the rest at a fraction of the cost |
| D-14 | **DEFER Epic 4's smoke rework (4.1-4.5) to a follow-up plan blocked on 4.7; keep 4.6, 4.8 and 4.9** | Operator decision, taken on red-team pass 3's N8. Nine issues and five criteria were rewriting a script that — by this plan's own Deferred table — **no recipe invokes after 4.6**, whose only automated exercise drives SEEDED states, and whose live path is blocked on an upstream fix this plan deliberately does not make. Deferring drops ~5 issues and 5 criteria **without weakening a single measured claim**. What stays is independent of the smoke: 4.6 is a live, measured tier-registration defect (the expensive check fires on the cheap tier and never on the land gate), and 4.8/4.9 are the #239 visibility work. #256 re-dispositions from `include` to `partial` as a direct consequence — what ships is the registration fix, not the state model |
| D-6 | **SPEC-first.** `REQ-YF-INSTALL-002`, `REQ-YF-INSTALL-007` and the `harness_cross_e2e` per-harness dest assertions encode the one-root-per-harness model and are amended before any implementation issue lands | AGENTS.md mandates it, and `spec_table_matches_shipped_descriptor` is a live parity test that fails the moment code and SPEC disagree — so the ordering is enforced mechanically, not merely by convention |

## Investigation Findings

**All seven experiments returned.** Each was measured against **installed binaries**, never a docs
site, per the repo's verify-against-the-binary rule (#195). Versions are pinned in every finding
because the whole root-resolution result set is version-scoped (R4).

| Id | Question | Outcome | Finding |
| :-- | :-- | :-- | :-- |
| EXP-001 | Does **claude-code** read `.agents/skills`? | **NO** — `.agents/` occurs **zero times** in the 222 MB binary; the auto-load constant is a hardcoded `[".claude/skills",".claude/commands"]`; a headless probe returned only the `.claude` control, twice. **D-4 decided: keep the private root** | [exp-001](findings/exp-001-claude-code-agents-root.md) |
| EXP-002 | Do **pi** and **opencode** read `.agents/skills` in both scopes? Does pi need its name transform? | **YES to both scopes, both harnesses** — the plan's premise, confirmed. **The transform is NOT required.** And the plan-054 "shadowing" is a **RACE**, not a preference: 4:1 across five runs, overwrite-on-collision under unbounded concurrency | [exp-002](findings/exp-002-pi-opencode-agents-root.md) |
| EXP-003 | What do `CODEX_HOME` / `OPENCODE_CONFIG_DIR` / `XDG_CONFIG_HOME` do? (#238) | **`.agents/skills` is ENV-IMMUNE on three of four harnesses**, so the collapse deletes three-quarters of #238. `OPENCODE_CONFIG_DIR` is **additive** where the other three **replace**; `XDG_CONFIG_HOME` is honoured by **opencode only** | [exp-003](findings/exp-003-harness-env-vars.md) |
| EXP-004 | Does an ownership manifest cover the skills surface? | **NO, and it never has** — `SurfaceRecord` carries `config` and `rules` only. The substitute is the per-copy marker + tree hash. **`yf harness skills remove` is a blind `remove_dir_all`** that deleted an unmarked operator directory in the sandbox | [exp-004](findings/exp-004-skills-ownership-and-dedup.md) |
| EXP-005 | What does **pi** do with skills in an untrusted project? (#239) | **User scope loads unconditionally; project scope is gated and fails SILENTLY** — no stderr, no event, exit 0 under `-p`/`--mode json`. So the core move is trust-neutral; project-scope deployment is not | [exp-005](findings/exp-005-pi-trust-gate.md) |
| EXP-007 | Does a **live deployed** copy actually classify `owned-and-unmodified`? (pass-2 M7 falsifier) | **Falsifier REFUTED** — `yf harness skills status` across all four roots: **76 of 76** copies `ok` / `unmodified: true`. Deployment residue does not escape the ignore-list, so the `delete` set is non-empty and the migration gate's empty-set failure will not fire spuriously | [exp-007](findings/exp-007-live-tree-classification.md) |
| EXP-006 | What states does `check-harness-smoke.sh` model? (#256) | Exits **0/1/2**, drives **only pi and opencode**, and the contract is shared by the whole check family — so the fix is a **payload, not widened exits**. Two registration defects found: the engine maps exit 2 to `fail`, and the row is in the **wrong tier table** | [exp-006](findings/exp-006-smoke-state-model.md) |

### What the findings changed

- **The plan did not shrink.** EXP-001 was D-4's hinge; a `yes` would have made the shared root
  universal. The answer was no, so the deploy matrix stays two-shaped and the `SKILL_DIR` resolver's
  dual `.claude`/`.agents` search is **correct and load-bearing, not redundancy to prune**.
- **The plan grew one epic.** EXP-004 turned "delete the private trees" into "build the enumerator
  that can see them" — Epic 1, sequenced ahead of the descriptor change.
- **#257's own reasoning was corrected.** It argues from a *preference* that EXP-002 measured to be a
  *race*, which is worse than filed and argues harder for the change.
- **One falsifier was killed cheaply.** EXP-007 was commissioned by red-team pass 2, which asked whether a live deployed copy really classifies `owned-and-unmodified` — if deployment residue escaped the ignore-list, every directory would classify `owned-but-modified`, the delete set would be empty, and the migration gate would hard-block the plan at its own evidence step. Measuring cost one command; discovering it at the gate would have cost an execution session. **Note the scope honestly:** `status` is name-keyed against the embedded set, so 76/76 covers the 19 embedded skills per root and is **structurally incapable** of seeing a foreign or unjudgeable directory — which is precisely why Epic 1 exists.
- **Two experiments met.** EXP-002 found pi's project-scope trust gate while measuring roots;
  EXP-005 characterized it. EXP-003 flagged a possible name-transform collision in a shared tree;
  EXP-002 had already refuted the transform's necessity.

### Method notes worth carrying forward

- **pi must be verified against `dist/bundle/chunks/*`, never `dist/core/*.js`.** The latter is stale,
  unused, and mentions only `.pi` — a source-only read of it refutes the premise incorrectly.
- **A FIFO is not a usable probe file.** EXP-003's first attempt used FIFOs, which fail `isFile()` and
  are skipped by every loader, producing a uniform false negative. It was discarded and rerun with
  real files — recorded rather than hidden.

## Approach

**One shared skills root where the harness reads it; a private root only where it does not.** The
harness descriptor conflates two concerns today — where skills land and where config/hooks/rules
land. This plan splits them, then collapses the skills column to `.agents/skills` for the three
harnesses measured to read it, leaving `surface_dir` untouched and harness-specific.

The sequencing is forced by two findings rather than chosen:

1. **The migration primitive comes FIRST.** EXP-004 measured that no ownership record exists for the
   skills surface and that the existing `yf harness skills remove` is a blind `remove_dir_all`. Until
   a marker-gated, directory-walking removal exists, the descriptor collapse would strand private
   trees that opencode may *racily* prefer (EXP-002) — turning a tidy-up into a live hazard. So
   Epic 1 builds and tests the remover before Epic 2 changes a single subpath.
2. **SPEC edits precede every implementation epic.** `spec_table_matches_shipped_descriptor` parses
   `REQ-YF-INSTALL-007`'s table out of `SPEC.md` and asserts equality with the shipped rows, so a
   code-first change fails the FAST tier immediately. AGENTS.md mandates SPEC-first; here it is also
   mechanically enforced.

`#238` rides along because EXP-003 measured that the collapse **deletes three-quarters of it**:
`.agents/skills` is env-immune under `CODEX_HOME`, `PI_CODING_AGENT_DIR` and every opencode override
combination. What remains is a surface-column override table plus one install-time warning — far
smaller than the resolver rewrite #238 contemplates.

`#256` and `#239` ride along because the harness smoke is being rewritten for the single-root model
regardless, and both are defects *in that script's state model*.

**Explicit non-goals.** No change to config, hooks, extensions or the rules aggregate. No plugin
manifest for claude-code (D-4a). No `dest.rs` full env resolver (D-13). No `bd`/upstream convention
changes. The v0.5.0 tag (#255) stays deferred.


## Epics

### Epic 0: SPEC-first amendments and shared check infrastructure
- Issue 0.1: Amend `REQ-YF-INSTALL-007` to split the descriptor's conflated concerns into `skills_root` and `surface_dir`, and restate the table with the collapsed skills values. Update the prose row-count wording the parity test reads.
- Issue 0.2: Amend `REQ-YF-INSTALL-002` so destination resolution is expressed over `skills_root`, preserving the existing resolved-path dedup guarantee.
  - depends-on: 0.1
- Issue 0.3: Add **`REQ-YF-MARK-006`** for **marker-gated skills-tree removal**: a directory walk with **four** outcomes — `owned-and-unmodified` delete; `owned-but-modified` keep-and-report; `no-marker` keep-and-report-as-foreign; **`undetermined`** keep-and-report-as-unjudgeable (unreadable `SKILL.md`, malformed marker, symlink; the walk must not follow symlinks) — defaulting to a dry-run preview, **and requiring `apply` to be REVERSIBLE — a move to timestamped quarantine with a documented restore, never an unlink.** Reversibility belongs in the requirement, not only in Issue 5.2a: 1.4 ships the `apply` verb and 5.2a converts it, so without this clause the tree transiently carries an irreversible destructive verb governed by nothing. **Four, not three: collapsing `undetermined` into `no-marker` asserts a positive fact from an absence of evidence**, the #181/#207/#256 class. In a SPEC-first repo the requirement is the source of truth, so it must carry the same arity as the implementation. Cite `REQ-YF-TUNE-029`'s conservative-keep as the governing precedent.
- Issue 0.4: Add **both** env-override columns to **`REQ-YF-INSTALL-007`** — the per-row *surface-dir* override **and the *skills-root* override, which applies to claude-code alone**. D-9's second half ("attaches to the SKILLS column only for claude-code") is the behaviour Issue 3.2 ships and SC10 asserts; covering only the surface column would leave a change to *where files land* governed by nothing: a per-row surface-dir override var and a three-valued precedence (`replace` / `additive` / `none`), with opencode encoded as two vars. Record `XDG_CONFIG_HOME` as opencode-only.
  - depends-on: 0.1
  - resolves-upstream: #238 (partial)
- Issue 0.5: Amend **`REQ-YF-INSTALL-007`**'s `NameTransform` clause, recording that pi 0.84.3 does not require it and that opencode's frontmatter-`name` rule is the binding constraint on a shared tree.
  - depends-on: 0.1
- Issue 0.6: Add a SPEC entry to the living amendment log covering every id touched by 0.1-0.5 and 0.9-0.10, in one bullet per id. **Sweep all of Epic 0 in one pass and confirm every issue names its `REQ-*` id explicitly** — the unnamed-id defect recurred three times across three review passes, moving one issue over each time (0.3, then 0.5, then 0.4). Patching the next instance is what produced the recurrence; the fix is the sweep.
  - depends-on: 0.1, 0.2, 0.3, 0.4, 0.5, 0.9, 0.10
- Issue 0.8: **COPY the shared check harness from plan-054's bundle into `scripts/checks/`** — **copy, never move** — `_common.sh`, `check-cargo-test-ran.sh`, `check-harness-smoke.sh` — **and author `check-migration-dryrun.sh`** (read by the migration-apply gate: exits 2 on a missing or unparseable artifact, 1 on a non-empty `undetermined` or a `delete` entry that is not `owned-and-unmodified`, 1 on an EMPTY `delete` set, 0 otherwise). **Copy semantics are load-bearing, and both alternatives are defective.** plan-054's `plan.md` references `assets/checks/` at **34 lines** (SC9/SC10 cite `check-cargo-test-ran.sh`, SC18 cites the smoke, and 0.6's `verify-red-checks` iterates the directory). A **move** would make 34 criteria in a completed plan unrunnable and would violate the bundle-as-record principle this issue invokes. So: copy, and **declare plan-054's `assets/checks/` frozen as a RECORD, not a live instrument** — divergence is expected and is explicitly *not* the R3 class, because nothing executes the frozen copy. **After D-14 the copied smoke lands DORMANT**: no issue in this plan rewrites it and 4.6 removes its only recipe row, so the copy is **pre-positioning for the deferred follow-up** rather than a response to in-plan edits. Saying so matters — the copy-vs-move argument was originally reasoned from five in-plan rewrites that no longer exist. **This is also a re-basing, not a plain copy.** Measured in a sandbox spike: `_common.sh`'s `ck_tree()` derives the tree from `${BASH_SOURCE[0]}/../..` and prefers `<root>/.worktrees/<plan_id>`; at `scripts/checks/` that probe never matches and `ck_tree` returns the **primary** repo root. Every `check-cargo-test-ran.sh` criterion would then grep the primary tree — where this plan's new test functions do not exist — and fail closed but *unrunnably*. So 0.8 must re-base `ck_tree`/`ck_plan_dir` on `git rev-parse --show-toplevel` plus an explicit `YF_PLAN_ID`/`--plan-dir`, and re-base the smoke's `TRANSCRIPT` path on an explicit argument. **It does NOT repoint `CHANGE-VALIDATION.md:51`.** Under copy semantics the old path stays valid, so no FAST run is ever stale — and 4.6 removes that row outright. An edit on a line another issue deletes, justified by a hazard the chosen semantics preclude, is exactly the kind of leftover a move-reading leaves behind. A move is also wrong on principle, because editing a **completed plan's** bundle contradicts the OKF bundle-as-record model and splits one artifact across two plans. This also gives every criterion in this plan a stable path to reference.
- Issue 0.9: Add **`REQ-YF-INSTALL-011`** requiring an install-time warning whenever a harness's replace-semantics env override is set and disagrees with the `$HOME`-derived default, and whenever yf creates a project-scope `.agents/skills` that makes the repo trust-requiring for pi. Both warnings are user-visible behaviour shipped by 3.3 and 4.9 and neither was covered by any requirement — SPEC-first is a mandate here, not a convention.
  - depends-on: 0.1
- Issue 0.10: Add **`REQ-YF-DOCTOR-007`** for the pi project-trust axis. The repo's precedent is decisive rather than a granularity judgement: `SPEC.md` already carries one REQ per doctor axis (`REQ-YF-DOCTOR-001` … `-006`), so a seventh axis with no requirement would be the only unspecified one.
  - depends-on: 0.1
- Issue 0.7: Write `scripts/check_amendment_log.py`, asserting that every `REQ-*` id this plan's SPEC issues touch carries an amendment-log bullet. The id set is **derived from the bodies of Epic 0 issues only**, never hand-enumerated and never from the whole document — a whole-file derivation over-collects `REQ-YF-TUNE-029`, `REQ-YF-MARK-001/002/003` and others this plan **cites but must not amend**, so SC1 would fail for the wrong reason. The script carries an explicit `cited-not-touched` exclusion list. **Why a script rather than a three-line grep, stated rather than assumed:** it is a reusable instrument every future SPEC-first plan inherits, and the amendment-log-vs-implementation gap is a recurring class here. **Its limitation is equally explicit** — the exclusion list is hand-authored, so the check is only as sound as a list a human maintains, which is the property it exists to remove from the loop. **It carries a SECOND assertion, over a COMPUTABLE predicate:** every issue in Epics 1-5 has a `depends-on` path to at least one Epic-0 issue that names a `REQ-*`, **except a declared `no-req-required` set — currently exactly `{4.6, 4.7}`**. Those two are exempt on a stated ground rather than by convenience: **neither changes `yf` behaviour.** 4.6 edits `CHANGE-VALIDATION.md` and authors a repo check script; 4.7 files an upstream defect. Both reach only 0.8, which names no requirement because promoting a check harness is not a behaviour change either. **The exemption is bounded, and WHERE each half is declared is what makes the bound mean anything:** the `no-req-required` set is declared **in this issue's body in `plan.md` and parsed from there**, while the script **hardcodes the baseline `{4.6, 4.7}`** and exits 2 (INCONCLUSIVE) on any parsed member outside that baseline carrying no reason string. Putting both halves in the script would make the comparison a constant against itself — dead code that can never fire. The mutable list belongs in the reviewed artifact and the immutable one in the instrument; that arrangement degrades honestly to "makes visible in review" rather than silently to "nothing at all". Measured over the current DAG, the predicate holds for all 23 non-exempt issues in Epics 1-5. This is derivable from the plan text alone. The earlier wording — "every issue that ships user-visible behaviour must *name* a covering `REQ-*`" — was not runnable: exactly **one** of the 25 issues in Epics 1-5 names an id, and the plan supplies no predicate for "ships user-visible behaviour", so the check would have degenerated into a second hand-authored list — the very property 0.7 exists to remove from the loop. **The checker exits 2 (INCONCLUSIVE), not 0, when the DERIVED ID SET is empty or single-element** (distinct from the exemption-set tripwire above — two different sets, two different rules, so they are named rather than both called "the set") — a check over an empty set certifies vacuously, which is the `check-criteria-scripts-exist.sh` precedent. This is why 0.3 names `REQ-YF-MARK-006` explicitly: an issue that says only "add a new requirement" is invisible to the derivation, so the one genuinely new id would go unchecked while SC1 passed green.
  - depends-on: 0.6

### Epic 1: Marker-gated removal (the migration primitive)
- Issue 1.1: Record the RED baseline: a fixture skills tree containing one yf-authored unmodified copy, one yf-authored modified copy, one foreign hand-placed directory and one unjudgeable member (symlink), with the current absence of any enumerator that can see the last two. **Also re-record the live-tree classification measured by EXP-007** — 76 of 76 deployed copies across the four roots classify `ok` / `unmodified: true` — since the migration gate's deliberate empty-`delete`-set failure is only correct if the live population is genuinely deletable. Re-measure rather than inherit: an operator with hand-edited skills legitimately gets a different distribution. **And do not over-read the figure** — `status` is name-keyed against the embedded skill set, so 76/76 speaks only to the 19 embedded skills per root and says nothing about foreign or unjudgeable directories, which is the population the enumerator exists to find.
  - depends-on: 0.3
- Issue 1.2: Implement the **directory-walk enumerator** over a skills root. This is the one primitive the codebase lacks: `status` is name-keyed against the embedded set and is blind to directories outside it.
  - depends-on: 1.1
- Issue 1.3: Implement the **four-outcome** classifier over the existing `marker` helpers (marker presence plus a recomputed marker-stripped tree hash equal to `marker_hash`). `undetermined` covers an unreadable `SKILL.md`, a malformed marker, and a symlinked directory; the walk must **not follow symlinks**. The report additionally flags any kept directory whose skill name also exists in the shared root (D-2f).
  - depends-on: 1.2
- Issue 1.4: Add the CLI surface as **`yf harness skills prune-private --scope user [--apply]`** — dry-run is the default and `--apply` is the only path that mutates. It emits the machine-readable verdict per directory, whose schema is fixed here (5.1 references it rather than re-declaring it): `{"delete": [{"path","outcome"}], "kept": [{"path","outcome","reason","shadows_shared_root"}], "undetermined": [{"path","reason"}]}`. The schema lives beside the emitting CLI because `check-migration-dryrun.sh` is written against it two epics away.
  - depends-on: 1.3
- Issue 1.5: Tests covering all **four** outcomes plus the empty-root, unreadable-root, unreadable-**member**, malformed-marker and **symlinked-member** cases, driven under a sandboxed HOME. Names the test functions SC5/SC6/SC7 cite: `marker_gated_removal_four_outcomes`, `remover_default_is_dry_run`, `enumerator_sees_foreign_directory`.
  - depends-on: 1.4, 0.8
- Issue 1.6: File the pre-existing `yf harness skills remove` defect upstream — blind `remove_dir_all` on name match, measured deleting an unmarked operator directory, plus the co-located raw-name join that makes it wrong for pi. Do NOT fix it here; this plan routes around it.
  - depends-on: 1.1

### Epic 2: Descriptor split and skills-root collapse
- Issue 2.1: Split `HarnessDescriptor` into `skills_root` and `surface_dir`, keeping every currently-shipped value identical. A pure refactor with no behaviour change, landed separately so Issue 2.2's diff is legible.
  - depends-on: 0.1, 0.2
- Issue 2.2: Collapse the skills column: `pi` and `opencode` move to `.agents/skills` at user scope and to the project-scope shared root, joining `codex` and `agents`. `claude-code` retains `.claude/skills` per D-4. **Depends on 2.3, and the edge is load-bearing.** `resolved_dests` dedupes by resolved path and keeps the **first** harness's id; `deploy_skill` then derives every skill's on-disk `dir_name` from *that one harness's* `transform_skill_name`. Since pi is the only row carrying a transform, collapsing pi onto the shared root while the transform still exists makes the shared root's on-disk names **order-dependent on descriptor row order**. Benign only incidentally today (yf names are already lowercase-hyphen and under 64 chars), and D-7 grades "safe for all future names" as *inferred* — so the transform is dropped **before** the collapse rather than in an unordered sibling.
  - depends-on: 2.1, 1.5, 2.3
  - resolves-upstream: #257 (include)
- Issue 2.3: Drop pi's `NameTransform::LowercaseHyphenMax64` and its parity-test assertions, **and remove the `lowercase-hyphen,max64` label text from `SPEC.md`**. Tests include a **>64-character skill-name probe**, the one arm EXP-002 never exercised. Ships `scripts/checks/check-transform-gone.sh`, which greps `yf/` for the enum name and **`REQ-YF-INSTALL-007`'s stanza only** for the label. **Whole-file is wrong and would make SC8 unsatisfiable:** `lowercase-hyphen,max64` also occurs inside the **living amendment log** (a `plan-033` entry), which 0.6 treats as append-only — so a whole-file grep matches forever. 2.3 also removes SPEC's separate clause requiring the transform be *validated against long skill names*, which is the live requirement text a table-only edit would leave stranded. A single-file grep is blind here: `spec_table_matches_shipped_descriptor` guards the label behind `if let Some(t) = d.name_transform`, so with the transform set to `None` the parity test **skips the check entirely** and a stale SPEC passes both SC8 and SC2.
  - depends-on: 2.1, 0.5
- Issue 2.4: Update `harness_cross_e2e`'s per-harness dest-resolution assertions to the collapsed model, including cases `pi_opencode_resolve_shared_root_both_scopes` and `distinct_skills_roots_per_scope` asserting that **all five** descriptor rows resolve to exactly **two** distinct skills roots per scope, that the **four non-claude** rows resolve to **one**, and that **every row merged onto a shared root agrees on `name_transform`** — the invariant that makes the merge's first-row-wins name derivation safe. **That last assertion is a regression guard against a FUTURE transform, not evidence about this change:** once 2.3 lands every non-claude row is `None`, so it holds trivially. It is worth keeping for the next harness added, and worth not mistaking for a check on the collapse. (The descriptor has five rows — `claude-code, codex, opencode, pi, agents` — so "four rows → two roots" is false under either reading.)
  - depends-on: 2.2, 0.8
- Issue 2.5: Dedupe the `self install` sync fan-out by resolved skills path, so one land-the-plane sync writes the shared root once rather than once per detected harness. Adds `sync_dedupes_shared_skills_root` to `install_sync_e2e`.
  - depends-on: 2.2, 0.8

### Epic 3: Env overrides and the silent-no-op warning
- Issue 3.1: Add the env-override fields to the descriptor rows per Issue 0.4, with the three-valued precedence.
  - depends-on: 2.1, 0.4
  - resolves-upstream: #238 (partial)
- Issue 3.2: Teach skills-root resolution to follow `CLAUDE_CONFIG_DIR` for claude-code only, since after the collapse it is the sole harness whose skills root an env var relocates.
  - depends-on: 3.1, 0.4
  - resolves-upstream: #238 (partial)
- Issue 3.3: Emit an install-time warning when a harness's replace-semantics override is set and disagrees with the `$HOME`-derived default, naming the directory the harness will actually read.
  - depends-on: 3.1, 0.9
  - resolves-upstream: #238 (partial)
- Issue 3.4: Tests for all three precedence values, including the opencode additive case that a boolean model would get backwards. Names the functions SC9/SC10/SC11 cite: `env_precedence_additive_and_replace`, `skills_root_env_override_claude_only`, `install_warns_on_override_mismatch`.
  - depends-on: 3.2, 3.3, 0.8

### Epic 4: Tier registration and pi-trust visibility
- Issue 4.6: Fix the registration by **removing** the `harness-smoke` row from the `### fast` table — where it fires on any unscoped FAST run, spending real model calls on the cheap tier — and **author** `scripts/checks/check_smoke_tier.py`, registering it in `### full` in its place. Its predicate: `harness-smoke` appears in **no** `###` tier table, **no residual `harness-smoke` prose claim survives in §1**, AND `check_smoke_tier` appears in `### full`; it exits 2 if `CHANGE-VALIDATION.md` is unparseable. **It also deletes the orphaned blockquote that sits INSIDE the `### fast` table** (`CHANGE-VALIDATION.md:53-59`), which asserts the smoke is "FULL-tier ONLY" and cites a completed plan's SC18. After the row is removed that prose is false, and it is invisible to `check_smoke_tier.py` — `parse_manifest` reads only `|`-delimited rows, so a correct checker would pass green over seven lines of false prose. **Do NOT move the smoke itself into `### full` yet.** SC19 runs `--tier full`; the smoke exits 2 when a harness is absent or unauthenticated, and `change_validation.py:797` maps any nonzero to `fail` — so moving it would give the repo's land gate a hard dependency on three live authenticated harnesses and real model calls. That is the same dependency SC17 was made `manual:` to avoid, and re-adding it as a runnable criterion would be an internal contradiction rather than a trade-off. **Re-adding the smoke to `### full` is explicitly BLOCKED on 4.7's upstream fix** and is recorded as a follow-up, not shipped here.
  - depends-on: 0.8
- Issue 4.7: File the `change_validation.py` exit-2 mapping defect upstream — a recipe row's exit 2 is reported as `fail`, contradicting `CHANGE-VALIDATION.md`'s prose. Out of scope to fix here; it is a `yf-change-validation` SPEC change.
  - depends-on: 4.6
- Issue 4.8: Add a `yf doctor` axis reporting when the repo has trust-requiring project resources and no applicable pi trust decision, computed locally from `trust.json` with no pi invocation. Adds `doctor_pi_trust_axis`.
  - depends-on: 2.2, 0.8, 0.10
  - resolves-upstream: #239 (partial)
- Issue 4.9: Warn at install time when yf creates `<repo>/.agents/skills`, since doing so makes the repo trust-requiring for pi and silently drops those skills under headless pi. Adds `warns_project_scope_makes_repo_trust_requiring`.
  - depends-on: 4.8, 0.8, 0.9
  - resolves-upstream: #239 (partial)

### Epic 5: Migrate, validate, reconcile
- Issue 5.1: Run `./target/debug/yf harness skills prune-private --scope user` (debug, because 5.1 runs **before** 5.1a's deploy) against this machine's private trees — `~/.pi/agent/skills` and `~/.config/opencode/skills` — and write the per-directory verdicts to `assets/migration-dryrun.json` in the schema 1.4 fixes. The migration-apply gate's `Test:` reads this exact file, so the path and schema are part of the issue's contract, not an implementation detail — and the gate is contracted to fail on a non-empty `undetermined`, which it cannot do against a schema that declares no such key. `shadows_shared_root` carries D-2f's divergence flag.
  - depends-on: 1.5, 2.2, 0.8, 0.3
- Issue 5.2a: Build the **timestamped quarantine + one-line restore** mechanism in the remover — `apply` moves rather than unlinks. An `apply` that cannot be undone is the #243 hazard (*"harness tune overwrites with no backup"*), which this plan excludes on surface grounds while otherwise building a second instance of it on the skills surface. Ships `scripts/checks/check-quarantine-restore.sh`, which seeds a directory, quarantines it, restores it and asserts byte-equality — so "reversible" is measured, not asserted. **This ships BEFORE any real removal happens** (5.2 depends on it): a reversibility mechanism that lands after the irreversible act is not a mitigation.
  - depends-on: 1.5, 2.2, 0.8
- Issue 5.1a: **Deploy the built binary to this machine** (`./target/debug/yf skills install`, or `yf self install --from-build --build` once the work is merged) so the drive-verify in 5.2 measures THIS plan's deployment rather than the pre-existing one. **This knowingly takes AGENTS.md's one real execution constraint, and says so rather than colliding with it silently.** AGENTS.md forbids `yf skills install` / `yf self install` mid-execution because `plan_manager.py` is re-invoked per call — a mid-run deploy takes effect for *scripts* in the same session while `SKILL.md` *prose* stays loaded from invocation, so a half-deployed session runs new scripts against old prose. It is unavoidable here: SC17 requires the resolved tree to carry the **post-collapse** stamp, so something must be deployed before the drive-verify. Mitigation: deploy as late as possible (immediately before 5.2), prefer `./target/debug/yf skills install` scoped as narrowly as the verb allows, and **do not re-invoke skill prose afterward expecting the pre-deploy copy** — finish 5.2/5.3 in the session that deployed. **Also close the window this opens:** between Epic 2 landing and 5.2's quarantine the private trees are still populated, so a routine land-the-plane sync — which `AGENTS.md` names as the DEFAULT step — writes only `.agents` and `.claude` and leaves the two private trees **stale and divergent**, manufacturing exactly the R3 coin flip at the moment the operator is most likely to run it. No bare `yf self install` may be run in that window without proceeding immediately to 5.2.
  - depends-on: 5.1, 2.5
- Issue 5.2: Execute the migration in the only order the measurements permit — **quarantine-move -> drive-verify -> commit-or-restore.** (1) Move each private tree's `delete` set to quarantine. (2) Drive pi, opencode and codex and confirm each resolves this skill to the shared `.agents/skills` root, by DRIVING rather than by asking `yf`. (3) On green, commit and drop the quarantine; on red, run the one-line restore and halt. **Verifying BEFORE the move is impossible, not merely inconvenient** — EXP-002 measured that with the private trees still present pi resolves `~/.pi/agent/skills` **3/3** (deterministic first-wins) and opencode picks `.config/opencode` **4 times in 5** (a race). A pre-move verification would therefore fail by construction on a correctly built plan. Quarantining first is what makes the verification *meaningful*; the restore is what makes it *safe*.
  - depends-on: 5.1a, 5.2a
- Issue 5.3: Run the FULL validation tier over the merged tree.
  - depends-on: 5.2, 3.4, 2.5, 4.9, 4.6, 2.3, 2.4, 0.7
- Issue 5.4: Re-run the criteria re-check and reconcile every upstream row to the end state its disposition requires.
  - depends-on: 5.3, 1.6, 4.7

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator
- Instructions: **Also confirm live-harness drivability here, at plan start.** pi, opencode and codex must be installed, authenticated and drivable headlessly. That condition depends on nothing any issue produces, so it is establishable now at near-zero cost — while the gate that *needs* it blocks one of the last three issues. An operator who cannot authenticate codex should learn it before the build, not after. The later gate stays where it is (it is where the need sits); this is the frontloading half.

### Capability Gate: live-harness drivability
- Type: human
- Condition: pi, opencode and codex are installed, authenticated, and drivable headlessly on this machine
- Test: `command -v pi >/dev/null && command -v opencode >/dev/null && codex login status >/dev/null 2>&1`
- Blocks: 5.2
- Instructions: The Test now carries **one genuinely falsifiable arm** — EXP-006 measured `codex login status` returning exit 1 when unauthenticated, so the gate is no longer pure presence. The pi and opencode arms remain presence-only. Authentication and consent are the operator's to establish — EXP-006 measured codex reaching a wrong-reason INCONCLUSIVE when unauthenticated, and no test may substitute for a human clicking through a trust dialog. Authorize only after confirming each harness accepts a headless prompt.

### Capability Gate: migration apply (destructive, local)
- Type: human
- Condition: the dry-run verdicts from 5.1 have been reviewed and every directory proposed for deletion is `owned-and-unmodified`
- Test: `bash scripts/checks/check-migration-dryrun.sh docs/plans/plan-055-james-dixson-5f1c40/assets/migration-dryrun.json`
- Blocks: 5.2
- Instructions: This is a declared destructive local operation (stop class 3). Read `assets/migration-dryrun.json` (written by 5.1) and confirm no `owned-but-modified` or `no-marker` directory appears in `delete`. EXP-004 measured the pre-existing `yf harness skills remove` destroying an unmarked operator directory; this gate is the control that this plan does not repeat it. **The Test runs primary-side (cwd: repo-root)** because the plan bundle lives in the primary checkout, not the execution worktree — a worktree-relative path would exit 127 and read as a failed gate rather than an unreachable one. **The Test also fails on an EMPTY delete set**, so a remover that silently found nothing cannot present as a green gate. **It exits 2 (INCONCLUSIVE), not 1, when the artifact is missing or unparseable** — "the evidence could not be read" and "the evidence says something bad is in the delete set" are different facts, and the earlier one-liner collapsed both into a failed gate. It also **fails when `undetermined` is non-empty** (D-2b), so an unjudgeable directory blocks the apply rather than being silently kept.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The migration deletes something the operator authored.** EXP-004 measured the existing `skills remove` doing exactly this — a hand-placed directory with no marker, gone, reported as success | high | Epic 1 builds a marker-gated remover with a keep-and-report default for anything not provably yf-authored-and-unmodified; the apply step sits behind a human gate reading per-directory dry-run verdicts (5.1). **The gate also hard-fails on a non-empty `undetermined` set** — so an unjudgeable directory nobody has looked for blocks the apply rather than being silently kept or silently deleted |
| R2 | **Project-scope deployment makes this repo trust-requiring for pi**, and headless pi then drops those skills with no diagnostic whatsoever — measured: no stderr, no event, exit 0 | high | D-3 is the operator's decision, taken with this cost stated. 4.8 adds a `yf doctor` axis and 4.9 warns at the moment yf creates the directory; yf-driven headless pi invocations pass `--approve` |
| R3 | **A stranded private tree is preferred RACILY by opencode.** Measured 4:1 across five runs, overwrite-on-collision under unbounded concurrency — so a partial migration yields a per-process coin flip between two skill versions | high | D-2e makes migration a MOVE, not an ADD: removal happens in the same operation that writes the shared root. 5.2 verifies by driving each harness rather than by asking `yf` |
| R4 | **The plan's core premise is version-scoped.** Every root-resolution finding is measured against pi 0.84.3, opencode 1.18.23, codex 0.150.1, claude-code 2.1.247 | high | Versions are pinned in every finding. 5.2 re-verifies by driving the installed harnesses at execution time, so a version drift surfaces as a failed verification rather than a silent regression |
| R5 | **claude-code's user-scope arm is an inference, not a run** — the investigator's worktree guard refused a sandboxed HOME | low | The inference feeds the CONSERVATIVE branch (keep the private root), so being wrong costs a missed simplification, not a broken install. Corroborated independently by EXP-003's atime sweeps |
| R6 | **A boolean env-precedence model silently inverts opencode.** `OPENCODE_CONFIG_DIR` adds a root where the other three vars replace one | med | D-10 fixes the column as three-valued at the SPEC layer (0.4) before any code reads it; 3.4 tests the additive case specifically |
| R7 | **The harness smoke cannot fail in the way it claims to.** Its exit 2 is remapped to `fail` by the engine, and the row sits in the wrong tier table | med | 4.6 fixes the tiering inside this plan; 4.7 files the engine mapping upstream rather than fixing a `yf-change-validation` SPEC surface from inside this plan |
| R8 | **Epic 1 is the only genuinely new code** and is a hard dependency of Epic 2 | med | Sequenced first and gated on its own tests (1.5) before 2.2 consumes it, so it fails early if it is going to |
| R9 | **The migration applies cleanly and the verification then fails** — mechanically successful, semantically wrong. R3 covers a PARTIAL migration; nothing covered a COMPLETE migration to a root the harness turns out not to read | high | **5.2 quarantines BEFORE verifying — the only order EXP-002's measurements permit** (with the private trees present, pi resolves its own root 3/3 and opencode picks `.config/opencode` 4 times in 5, so a pre-move verification fails by construction). A failed drive-verify is therefore detected before any irreversible act and is undone by 5.2a's one-line restore |
| R10 | **The shared check harness is copied out of a COMPLETED plan's bundle**, so two copies of `check-harness-smoke.sh` exist on disk | low | 0.8 copies rather than moves (a move would break 34 criteria in plan-054's record) and **declares plan-054's copies frozen as a record, not a live instrument**. After D-14 no issue in this plan rewrites the smoke, so the copy lands dormant and the two cannot diverge under anything this plan does |
| R11 | **Thirteen genuinely foreign directories remain in `~/.config/opencode/skills` after migration** (measured: `cloudflare`, `wrangler`, `sandbox-*`), so opencode keeps reading a half-populated private root and R3's "divergence becomes unrepresentable" is stronger than what ships | med | The claim is narrowed rather than defended: divergence becomes unrepresentable **for yf-authored skills**, which is the set this plan owns. The dry-run report enumerates every kept directory (D-2f), so the residue is recorded rather than discovered later |

## Deferred and follow-ups

Everything this plan knowingly leaves open, in one place — so a reader does not have to reconstruct
it from issue bodies.

| Item | Why it is deferred | Where it goes |
| :-- | :-- | :-- |
| `yf harness skills remove`'s blind `remove_dir_all` | Measured deleting an unmarked operator directory. This plan **routes around** it rather than fixing it, so the fix is not load-bearing here | filed upstream by 1.6 |
| `change_validation.py` maps a recipe row's exit 2 to `fail` | A `yf-change-validation` SPEC change; fixing it from inside this plan would edit another skill's spec surface | filed upstream by 4.7 |
| **Re-adding `harness-smoke` to `### full`** | Blocked on 4.7. Until exit 2 survives the engine, moving it gives the land gate a live-harness dependency (C2) | follow-up, blocked-by 4.7 |
| **The smoke's state-model rework (former 4.1-4.5)** | D-14. Deferred as one unit with the re-add row above — same blocker (4.7), same artifact. Carries the `undetermined` fifth state, the pre-drive auth probe, the `_common.sh` sourcing fix, the codex target and the transcript-provenance fix | follow-up, blocked-by 4.7 |
| **Mid-execution abandonment leaves the machine migrated** | If 5.3 fails and the branch is abandoned, `main`'s binary still targets the private roots, so the next `yf self install` re-creates them and re-establishes R3's divergence. Recovery: run 5.2a's restore, then reinstall from `main` | operator runbook, recorded in this row **and** in `context.md` |
| #238's surface-dir resolution | D-13: yf warns rather than resolves. Only `CLAUDE_CONFIG_DIR` is followed, and only for skills | #238 stays open as `partial` |
| **#256 stays open as `partial`** | Only the tier-registration defect ships (4.6). None of #256's own state-model ask does | #256 stays open as `partial` |
| #239's trust-gate test/smoke coverage | This plan ships visibility (doctor axis + warning), not coverage | #239 stays open as `partial` |
| A claude-code plugin manifest pointing at `.agents/skills` | D-4a — a genuinely different design (ship a manifest, not copy a tree), and **untested**. Recorded as a hypothesis | future plan |
| The 13 foreign directories in `~/.config/opencode/skills` | Not yf's to delete. R11 narrows the divergence claim rather than defending it | recorded in the 5.1 dry-run report |

## Success Criteria

**Every `Verification` cell below is either a runnable command judged by exit code, or an explicit
`manual:` with the reason no predicate exists.** Prose shaped like a command is the defect #165 and
#232 name, and a criterion whose check cannot fail is worse than no criterion. Where a command is
named, **the issue in `Discharged-by` is the issue that creates it** — a criterion naming a test
nothing writes is the same unreachable-gate defect the conformance pass caught in the migration gate.

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | **Every BEHAVIOUR this plan ships is covered by a `REQ-*`**, each amended before the implementation issue that depends on it closed, and each carrying an amendment-log bullet. Stated over *behaviours*, not over *ids the plan happens to touch* — the earlier wording could not fail on a behaviour shipped with no requirement at all, which is exactly what four issues were doing | `uv run scripts/check_amendment_log.py --plan plan-055-james-dixson-5f1c40` -> exit 0 | 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9, 0.10 |
| SC2 | The shipped descriptor exposes `skills_root` and `surface_dir` as distinct fields, and the SPEC parity test passes against the amended table | `bash scripts/checks/check-cargo-test-ran.sh spec_table_matches_shipped_descriptor` -> exit 0 | 0.1, 0.8, 2.1 |
| SC3 | `pi` and `opencode` resolve their skills root to `.agents/skills` at BOTH scopes, and `claude-code` still resolves to `.claude/skills` | `bash scripts/checks/check-cargo-test-ran.sh pi_opencode_resolve_shared_root_both_scopes` -> exit 0 | 0.8, 2.2, 2.4 |
| SC4 | The four non-claude harness rows resolve to exactly ONE distinct skills root per scope | `bash scripts/checks/check-cargo-test-ran.sh distinct_skills_roots_per_scope` -> exit 0 | 0.8, 2.4 |
| SC5 | **The remover never deletes a directory it cannot prove yf authored AND left unmodified.** A modified copy, a foreign directory, and an UNJUDGEABLE one (unreadable / malformed marker / symlink) are all KEPT and reported, each under its own distinct outcome | `bash scripts/checks/check-cargo-test-ran.sh marker_gated_removal_four_outcomes` -> exit 0 | 0.8, 1.3, 1.5 |
| SC5b | The RED baseline was recorded BEFORE any remover code existed, and it demonstrates the enumeration gap rather than asserting it | manual: a before/after ordering claim over a fixture; the fixture is re-runnable but "was recorded first" is a git-history property with no stable predicate | 1.1 |
| SC6 | The remover's default invocation performs NO deletion | `bash scripts/checks/check-cargo-test-ran.sh remover_default_is_dry_run` -> exit 0 | 0.8, 1.4, 1.5 |
| SC7 | The directory-walk enumerator sees a directory that is NOT in the embedded skill set — the case `status` is structurally blind to | `bash scripts/checks/check-cargo-test-ran.sh enumerator_sees_foreign_directory` -> exit 0 | 0.8, 1.2, 1.5 |
| SC8 | pi's `NameTransform` is gone from the descriptor **and** the `lowercase-hyphen,max64` label is gone from `SPEC.md` | `bash scripts/checks/check-transform-gone.sh` -> exit 0 | 0.8, 2.3 |
| SC8b | One land-the-plane sync writes the shared skills root ONCE, not once per detected harness | `bash scripts/checks/check-cargo-test-ran.sh sync_dedupes_shared_skills_root` -> exit 0 | 0.8, 2.5 |
| SC9 | Env-override precedence is three-valued, and the opencode ADDITIVE case is asserted distinctly from the three replace cases | `bash scripts/checks/check-cargo-test-ran.sh env_precedence_additive_and_replace` -> exit 0 | 0.8, 0.4, 3.1, 3.4 |
| SC10 | `CLAUDE_CONFIG_DIR` relocates claude-code's skills root, and no other harness's skills root responds to any env var | `bash scripts/checks/check-cargo-test-ran.sh skills_root_env_override_claude_only` -> exit 0 | 0.8, 3.2, 3.4 |
| SC11 | An install run with a replace-semantics override set and disagreeing with the default EMITS A WARNING naming the directory the harness will actually read | `bash scripts/checks/check-cargo-test-ran.sh install_warns_on_override_mismatch` -> exit 0 | 0.8, 3.3, 3.4 |
| SC14 | The `harness-smoke` row appears in NO tier table, and the static `check_smoke_tier.py` is registered in `### full` — so the expensive check no longer fires on the cheap tier, and the land gate acquires no live-harness dependency | `uv run scripts/checks/check_smoke_tier.py` -> exit 0 | 0.8, 4.6 |
| SC16 | `yf doctor` reports the pi-trust condition when the repo has trust-requiring resources and no applicable decision, computed with NO pi invocation | `bash scripts/checks/check-cargo-test-ran.sh doctor_pi_trust_axis` -> exit 0 | 0.8, 4.8 |
| SC16b | Creating `<repo>/.agents/skills` emits a warning naming pi's trust consequence | `bash scripts/checks/check-cargo-test-ran.sh warns_project_scope_makes_repo_trust_requiring` -> exit 0 | 0.8, 4.9 |
| SC17b | **The post-collapse binary was deployed to this machine BEFORE the drive-verify ran** — so SC17's stamp check measures this plan's deployment rather than the pre-existing one. Stated over the DEPLOYMENT act (5.1a's subject), which is what makes it distinct from SC17 rather than a subset of it | manual: requires a live driven harness session; the same authentication constraint that makes SC17 manual applies, and a close-time re-run would fail on an unauthenticated machine rather than on a regression (#221) | 5.1a |
| SC17 | After migration, each of pi, opencode and codex resolves this skill to the shared root **and the resolved tree carries the `SKILL_DIR_INSTALLED_AT` stamp written by the POST-COLLAPSE build** — established by DRIVING each harness, not by asking `yf`. The stamp clause is what distinguishes this plan's change from a bare `rm -rf` of two directories, which would satisfy the root claim on its own | manual: requires three authenticated live harness sessions and real model calls; the live-harness gate is human for the same reason, and a close-time re-run would fail on an unauthenticated machine rather than on a regression (#221) | 5.2 |
| SC18b | The removal is REVERSIBLE — every removed directory lands in a timestamped quarantine, and the documented restore command puts it back | `bash scripts/checks/check-quarantine-restore.sh` -> exit 0 | 5.2a |
| SC18 | Zero private skills trees remain for pi and opencode on the migrated machine, except directories the remover deliberately kept and reported | manual: asserts a fact about THIS machine's $HOME, which no repo-portable command can check; 5.1's asset records the per-directory verdicts a reader compares against | 5.1, 5.2 |
| SC19 | The FULL validation tier passes over the merged tree | `uv run skills/yf-change-validation/scripts/change_validation.py run --tier full` -> exit 0 | 5.3 |
| SC20 | Every upstream row reached the end state its disposition requires, and the two out-of-scope defects are filed with their measurements | `uv run skills/yf-plan/scripts/plan_manager.py verify-reconcile docs/plans/plan-055-james-dixson-5f1c40 --json` -> exit 0 | 1.6, 4.7, 5.4 |
