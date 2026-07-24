Documentation drifts from code the moment one changes without the other. `yf-drift-check`
catches that drift on edit. It verifies **content agreement** across a repository's declared
source-of-truth edges — implementation, docs, and spec — and reports where they disagree. It
never authors, optimizes, restructures, or auto-fixes; it reads, checks, and returns a verdict.

The engine is fixed and carries no repo vocabulary. Each repository supplies a thin markdown
**manifest** — `DRIFT-CHECK.md` at the repo root — declaring its own artifact graph: which files
are nodes, which edges connect a source to its derivatives, the per-edge contract, the
changed-path globs that scope a check, and the tie-breaker policy for a stale authority. The
engine reads that manifest, matches the changed path against its globs, dispatches a report-only
sub-agent over the scoped edges, and acts on the findings.

## When it fires

The skill is `user-invocable: false`. It fires from its always-loaded companion rule when a file
covered by the manifest changes, and on explicit request:

- **A covered file is created or modified** — the changed path matches a Trigger Scope glob in an
  approved manifest.
- **You ask to check drift** — verify the manifest is in sync, or run an on-demand sweep.
- **A manifest is being bootstrapped** — first install, or explicit invocation in a repo with no
  manifest yet.

Everything hinges on an **approved** manifest. A manifest counts as approved only if its §0 Status
reads `approved: yes`. With no approved manifest — missing, or an unapproved draft — the on-edit
trigger is a **silent no-op**. No check, no nag, no bootstrap prompt. A repo that has not opted in
is never imposed on.

## What it does not touch

`yf-drift-check` verifies that already-written artifacts agree. It never writes them. Two adjacent
skills own the writing:

| Concern | Owner |
| :-- | :-- |
| Does an already-written artifact AGREE with its declared source of truth? | **yf-drift-check** |
| Is a skill-dir instruction file written to authoring conventions? | [yf-skill-authoring](/skills/yf-skill-authoring/) |
| Is a project-root `CLAUDE.md` / `AGENTS.md` structured and tight? | [yf-optimal-instructions](/skills/yf-optimal-instructions/) |

It **never lists** `CLAUDE.md` or `AGENTS.md` as manifest nodes, so it is structurally silent on
the project-root axis. On a skill-dir file it may fire alongside `yf-skill-authoring` — that
overlap is orthogonal by design (content agreement versus authoring conventions). The per-repo
suppression lever is to omit the glob from the manifest's Trigger Scope section. It also declines
any request to fix rather than report drift.

## How it works

On a covered edit the engine runs a fixed workflow:

1. Identify the changed path or paths.
2. Read the approved `DRIFT-CHECK.md`.
3. Match each changed path against the Trigger Scope globs and collect the scoped edge IDs. A
   source-node edit fans out to every derived edge it feeds.
4. Dispatch the `drift-verifier` sub-agent over only those edges — report-only, it writes nothing.
5. Act on the returned verdicts.

The verifier is isolated and read-only. Every check item must be backed by **direct evidence** — a
file read, an identifier comparison, a contract listing, a content quote, or command output —
before it is marked PASS or FAIL. "I believe this is correct" is not evidence. A check that needs
runtime execution the verifier cannot run is marked INCONCLUSIVE.

## The four check categories

Each edge's Check Category selects one engine, and the edge's Contract term is the test:

- **cross-ref** — references in the derived node resolve into the source (`path-resolves`,
  `identifier-matches`).
- **contract** — a value or field-set the derived node assumes matches the source (`value-equal`,
  `field-set-subset`, `field-set-equal`).
- **behavioral** — logic duplicated across nodes stays equivalent (`value-equal`).
- **required-section** plus reachability — required nodes have a live referencer, and `doc` nodes
  contain their mandated sections (`section-present`).

## The four verdicts

The verifier returns one verdict per item, and the main session acts on it:

| Verdict | What it means | Action |
| :-- | :-- | :-- |
| PASS | the edge agrees, on direct evidence | continue |
| FAIL | the derived node disagrees with its source | resolve in the same pass as the change |
| INCONCLUSIVE | evidence unavailable (e.g. needs runtime) | surface to the operator; never assume |
| CONFLICT | a `fixed` authority is itself suspected stale | halt and report per the manifest's policy; never rewrite either side |

The engine itself never auto-fixes. It reports; the main session applies FAIL corrections in the
same pass, so drift is closed as it is introduced rather than accumulating.

## The manifest

The per-repo `DRIFT-CHECK.md` is markdown with exactly seven sections, in order: Artifact Nodes,
Source-of-Truth Edges, Per-Edge Contracts, Referencers, Required-Section Contracts, Trigger Scope,
and Fixed-Authority Conflict Policy. It must be referentially closed — every edge names nodes that
exist, every contract row names an edge that exists. Every Contract value is one of a fixed
six-term vocabulary; no manifest invents a new term. At least one node is declared `Authority:
fixed` — the drift tie-breaker — and the conflict policy names it.

Bootstrap is hybrid: infer, approve, enforce. On explicit invocation in a repo with no manifest,
the engine infers a draft from what exists on disk — never a hardcoded conventional filename — and
presents it. The draft is inert until you set §0 `approved: yes`. Only then does the engine enforce
it.
