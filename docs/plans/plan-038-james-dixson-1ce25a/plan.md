---
type: Plan
okf_spec: OKF-PLAN
id: plan-038-james-dixson-1ce25a
author: james-dixson
created: '2026-08-14'
status: reconciling
deliverable_class: standard
fingerprint: f1c212431f7a1462de0c7133f5c991a666192bc0ddc4d47cac26633399b896f2
epic: yf-mol-g83
---
# Plan: Make yf-beads-upstream enforce its own never-hand-run invariant

**ID:** plan-038-james-dixson-1ce25a
**Author:** james-dixson
**Created:** 2026-08-14
**Status:** reconciling
**Deliverable-class:** standard
**Epic:** yf-mol-g83
**Fingerprint:** f1c212431f7a1462de0c7133f5c991a666192bc0ddc4d47cac26633399b896f2

## Objective

Make `yf-beads-upstream` trustworthy in both senses the skill currently fails: fix the
silent-data-loss defect in its own push machinery (#129), then make its documented procedure obey
the safety invariant its companion rule declares, by giving the skill a first-class `push` verb
and routing every prescriptive step through it (#106). Finally close the write-only gap with a
`closable` verb that proposes which upstream issues can be closed (#117).

The end state is that **following the skill is compliant by construction and the machinery
underneath it is correct** — the invariant stops being prose the reader must remember, and the
routed path stops being one that can silently do nothing.

### Why #129 sequences first

Routing every push through the skill is the right goal, but it is only safe once the skill's own
push machinery works. Today `plan_hoist()` emits comma-separated bead ids that `bd` matches to
**zero** beads while exiting 0, then closes every bead locally with a tombstone claiming it was
hoisted upstream. Multi-bead `hoist`/`land` can therefore remove beads that were never pushed.

The irony is instructive and worth stating: in the session that produced this plan, the
**non-compliant** hand-run push (space-separated) succeeded, while the **compliant** in-skill path
would have silently failed. Routing everything through the skill remains correct — but doing it
before fixing #129 would route work onto a broken path.

## Motivation

The always-loaded companion rule states:

> **Route every upstream push through `/yf-beads-upstream` — do not hand-run `bd <backend>` push
> commands.** … If `/yf-beads-upstream` is unavailable, stop and report — do not substitute a
> hand-run push.

`SKILL.md` Push step §3 then documents the hand-run command as *the* procedure. An operator or
agent that follows the skill violates the rule. There is no in-skill wrapper for the push step —
`hoist` and `land` wrap it for their own flows, but the plain push has none.

This is not theoretical. In the session that produced this plan, pushing 11 orphaned beads was
done with a hand-run `bd github push` **because the skill said to**. Nothing broke, which is
exactly why the defect persists: it fails silently, producing a non-compliant action that looks
correct at every step.

The second half is the mirror problem. Every verb the skill owns pushes *up*; none proposes
closing an upstream issue whose work is finished. Four coarse trackers (#103, #95, #96, #98) were
found still open for plans at `status: complete`, each discovered by an ad-hoc human sweep. Issue
closure currently depends on someone remembering, and the record shows that does not happen.

## Investigation Findings

Three experiments; detail in `findings/`.

**The 20 `bd <backend>` mentions in SKILL.md are two different things, and the fix depends on
telling them apart.** Six are **prescriptive** — they instruct the reader to run the command
(§3's dry-run and real push, §3's subtree form, §4's failure handling, §6's re-push, and the
backend translation table's scoped-push row plus its Jira note). Fourteen are **descriptive** —
provenance, the three-mechanism `bd dolt push` disambiguation, the inline-auth statement, two
dated empirical verification blockquotes, and **the safety invariants themselves**, which quote
the command in order to forbid it. A find-replace over all 20 would mangle the very rule this
plan enforces. An acceptance check greping for zero occurrences of `bd github push` would be
wrong for the same reason.

**The executor already exists, so `push` is a factoring-out rather than new capability.**
`plan_hoist()` builds an exact command sequence with the dry-run first and no execution;
`cmd_hoist(..., apply)` prints it and, with `--apply`, executes via `run(["bash","-c",c])`.
`BACKEND_AUTH` already maps inline auth per backend. So `push` is `plan_push()` + `cmd_push()`
mirroring that proven pure-planner/thin-executor pair. (An earlier reading of this scope claimed
the executor was missing; that was wrong, and the scope is correspondingly smaller.)

**`hoist` does not already cover the plain-push case — verified, not assumed.** `plan_hoist()` is
three stages: dry-run push, real push, then **`bd close` per bead**. That third stage is the
difference: `hoist` removes the bead locally with a reversible tombstone; a plain push must leave
it open and mirrored. So `push` is genuinely `plan_hoist` stages 1–2 without stage 3. This premise
was flagged by the red-team as asserted-but-unmeasured; measuring it both confirmed the premise
and exposed #129.

**#129: the emitted push command matches zero beads and exits 0.** `plan_hoist` builds
`",".join(bead_ids)`, but `bd <backend> push` takes space-separated positional ids — as SKILL.md
itself documents. Measured on bd 1.1.2:

| Command | Result |
|:--|:--|
| `bd github push yf-m78m yf-252c --dry-run` | `✓ Pushed 2 issues` |
| `bd github push yf-m78m,yf-252c --dry-run` | *(no `✓ Pushed` line)*, exit **0** |

Because stage 3 then runs unconditionally, a multi-bead `hoist --apply` or `land --apply`
tombstones every bead with a reason asserting an upstream hoist that never happened. Three call
sites (`upstream.py:709`, `:729`, `:750`). Single-bead hoist is unaffected — a one-element join has
no comma — which is likely why it survived. The fixture tests missed it because they assert the
*shape* of the emitted command against an expected string that itself contains the commas: a test
documenting the implementation rather than the contract.

**`closable` with the chosen per-bead signal is forward-looking only.** An issue is closable when
every bead carrying an `External:` mapping to it is closed — zero coupling to `yf-plan`'s
configurable `plans-root`. But `yf-plan` §4.5 files coarse plan trackers with a direct
`gh issue create`, so **no bead ever maps to them**. `closable` therefore would **not** have
caught any of the four sweeps that motivated #117. That is the price of zero coupling, and this
plan states it rather than implying #117 is fully closed.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:--|:--|:--|:--|:--|
| #129 | `plan_hoist` emits comma-separated ids that bd matches to ZERO beads — multi-bead hoist/land tombstones beads it never pushed | include | Silent data-integrity defect found while red-teaming this plan's premise. Sequenced **first**: routing work onto broken machinery would be worse than not routing it. | Issues 2.1–2.4 |
| #106 | SKILL.md Push §3 instructs hand-running `bd github push` — contradicts the never-hand-run invariant | include | The core defect. Fixed by adding `push` and rewriting the prescriptive sites. | Issues 3.1–3.5 |
| #117 | push is write-only — no verb proposes CLOSING upstream issues whose work is done | partial | **In scope:** the `closable` verb on the per-bead signal, propose-only. **Out of scope:** detecting hand-filed coarse plan trackers, which the per-bead signal structurally cannot see. #117 stays **open** with that gap recorded. | Issues 4.1–4.5 |
| #105 | enumerate silently returns 0 when bd auto-assigns an owner | include | Already shipped (`3fb5367`), but left a residual: the warning is stderr-only, so an agent piping `--json` to `jq` misses it. The new `push` verb surfaces it inline. | Issue 3.4 |
| #102 | `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit` | exclude | Unrelated marker; needs `migrate.rs` work. |  |
| #60 | yf-beads-upstream: mutually-exclusive `requires:<platform>` labels in worklist filtering + hoist | exclude | Same skill, different axis (label semantics). Would widen this plan without sharing any code path. |  |

All other open issues reviewed and out of scope.

## Approach

Five epics. Two orderings are forced: the machinery must be correct before work is routed onto it,
and prose cannot call a verb that does not exist yet.

**Epic 1 lands the SPEC.** Per AGENTS.md, the `REQ-BUP-*` requirements for the separator/fail-closed
fix, the `push` verb, the `closable` verb, and the strengthened guardrail land before any code.

**Epic 2 fixes #129.** The separator bug plus a fail-closed guard so no subsequent stage runs on an
unverified push. Highest severity in the area and a prerequisite for routing work through the skill.

**Epic 3 builds `push` and rewrites the prescriptive sites.** Built fail-closed from the start
rather than inheriting `plan_hoist`'s pattern of trusting an unverified stage. The rewrite is not
mechanical: §4 (failure handling) and §6 (re-push) describe recovering from a raw `bd` invocation
that will no longer be what the reader ran, so they need re-derivation rather than substitution.

**Epic 4 adds `closable`.** Independent of Epics 2–3 — no shared code path — so it can run in
parallel. Propose-only, never auto-closing: closing an upstream issue is outward-facing and gets
the same confirm contract as a push.

**Epic 5 hardens so the contradiction cannot silently recur.** A scoped acceptance check plus the
companion-rule update. Without it, the next SKILL.md edit can reintroduce a prescriptive raw push
and nothing notices.

Ordering: Epic 1 → Epic 2 → Epic 3. Epic 4 parallel to Epics 2–3. Epic 5 depends on all.

### What "enforce" does and does not mean here

The invariant becomes enforced in the sense that **the documented path is compliant** and a
scoped check fails if a prescriptive raw invocation reappears. It does **not** mean the skill can
prevent an operator from typing `bd github push` directly — nothing in a prose-plus-script skill
can. Stating this boundary is deliberate: an enforcement claim that overreaches is worse than a
modest one, because it invites the reader to stop paying attention.

### Testing the contract, not the implementation

#129 survived because the fixture tests compare emitted command strings against expected strings
that contain the same defect. Every test this plan adds must assert a **contract** — that the
emitted ids are space-separated, that a push reporting fewer issues than requested halts the
sequence — rather than re-stating what the code happens to produce.

## Epics

### Epic 1: SPEC-first — declare the fix, the verbs, and the guardrail

- **Issue 1.1: Add `REQ-BUP-050` (push-command construction + fail-closed).** Specify that emitted
  `bd <backend> push` commands use **space-separated** positional ids, and that any sequence with a
  destructive follow-on stage (e.g. `hoist`'s local close) must **verify the push succeeded for the
  expected number of beads** before that stage runs. Fail-closed: an unverified push halts the
  sequence.
- **Issue 1.2: Add `REQ-BUP-051` (the `push` verb).** `upstream.py push --issues <csv> [--apply]`,
  matching the existing `--apply`-only idiom (`cmd_hoist` has no `--dry-run` flag; absent `--apply`
  *is* the dry run). Always emits the dry-run push first; scoped `--issues` only, never a bare
  `sync`; inline auth via `BACKEND_AUTH`. Declare it **the** documented push path.
  - depends-on: 1.1
- **Issue 1.3: Add `REQ-BUP-052` (the `closable` verb).** The per-bead signal (an issue is closable
  when every bead with an `External:` mapping to it is closed), propose-only with **no auto-close**,
  and the shared default-deny short-circuit. **Must record the known gap**: hand-filed coarse
  trackers carry no bead mapping and are undetectable by this signal.
  - depends-on: 1.2
- **Issue 1.4: Strengthen the guardrail (`GR-BUP-*`) with a checkable contract.** State that
  operator-facing *procedure* must not instruct a raw `bd <backend>` push, while *explanatory* and
  *invariant-stating* mentions are expected. Define the boundary mechanically so Epic 5's check has
  a contract: **fenced ```bash blocks inside the Push step and Backend generalization sections** are
  procedure; prose, tables, and blockquotes are explanation.
  - depends-on: 1.3

### Epic 2: Fix #129 — the separator defect and the unverified-push hazard

- **Issue 2.1: Fix the separator in `plan_hoist()`.** Emit space-separated ids. Verify the emitted
  command matches beads by running it with `--dry-run` against the live repo and confirming a
  `✓ Pushed N issues` line with the expected N.
  - depends-on: Epic 1
- **Issue 2.2: Make the hoist/land sequence fail-closed.** The local-close stage must not run on an
  unverified push. Either parse the push output for the expected count, or restructure so the
  executor checks each stage before proceeding — the SPEC (1.1) states the requirement; this issue
  chooses the mechanism and records why.
  - depends-on: 2.1
- **Issue 2.3: Audit the other emitted-command builders for the same assumption.** `plan_unhoist`
  and any other command constructor — confirm none carries a separator or
  unverified-destructive-stage bug.
  - depends-on: 2.1
- **Issue 2.4: Contract tests for #129.** Assert the emitted push command separates ids with spaces
  and that **no comma appears between ids**; assert the close stage does not run when the push
  stage reports fewer than the expected count. These must test the contract, not restate the
  emitted string.
  - depends-on: 2.2, 2.3
  - resolves-upstream: #129 (include)

### Epic 3: Implement `push` and route the prescriptive sites through it

- **Issue 3.1: Implement `plan_push()`.** Pure; `plan_hoist` stages 1–2 without the local close.
  Inherits the Epic-2 separator fix and fail-closed contract by construction.
  - depends-on: Epic 2
- **Issue 3.2: Implement `cmd_push()` + argparse wiring.** Mirrors `cmd_hoist`: print the sequence,
  `--apply` executes via the existing `run(["bash","-c",c])`. No `--dry-run` flag — absent
  `--apply` is the dry run, matching the existing idiom.
  - depends-on: 3.1
- **Issue 3.3: Re-derive the prescriptive site list from the sections, then rewrite.** Read the Push
  step (§1–§8) and Backend generalization **end to end** rather than trusting a grep — a
  prescriptive instruction phrased without the literal backend token would be missed. Rewrite each
  to call `upstream.py push`. Keep the `≡ sync form` table column as **descriptive**: it documents
  what the verb emits, which is exactly the explanation that must survive.
  - depends-on: 3.2
- **Issue 3.4 (#105 residual): surface the owner-claimed warning inline in `push`.** The stderr
  warning shipped in `3fb5367` is missed by an agent piping `--json` to `jq`. Now that `push` is the
  routed path, it prints the exclusion warning in its own output.
  - depends-on: 3.2
  - resolves-upstream: #105 (include)
- **Issue 3.5: Re-derive §4 (failure handling) and §6 (re-push).** Not find-replace: both describe
  recovering from a raw invocation the reader will no longer have run. §4's "non-zero exit" becomes
  the verb's failure surface; §6's re-push becomes a `push` call, while its `Would update in GitHub`
  vs `Would create` mapping-lost tripwire **must be preserved** — it is now doubly important, since
  #129 showed a push can report nothing at all.
  - depends-on: 3.3
  - resolves-upstream: #106 (include)
- **Issue 3.6: Tests for `push`.** Contract tests: dry-run always first; scoped `--issues` never a
  bare `sync`; per-backend inline auth; propose-vs-`--apply`; the 3.4 inline warning. All `bd`
  interaction faked.
  - depends-on: 3.5, 3.4

### Epic 4: Add the `closable` verb (#117, partial)

- **Issue 4.1: Implement `closable_candidates()`.** Pure: given beads and their `External:`
  mappings, group by issue and report those where every mapped bead is closed.
  - depends-on: Epic 1
- **Issue 4.2: Implement `cmd_closable()` + argparse wiring.** Report `closable` / `not-closable`
  with a reason per issue; human and `--json` forms; default-deny short-circuit. **Never closes.**
  Emits the proposed `gh issue close` commands for operator confirmation.
  - depends-on: 4.1
- **Issue 4.3: Document `closable` in SKILL.md with its limitation stated.** Add it to the verb list
  and the land-the-plane flow. The prose must say plainly that hand-filed coarse trackers are not
  detected, so a clean `closable` run is never read as "nothing needs closing."
  - depends-on: 4.2
- **Issue 4.4: Tests, including a caveat-survival assertion.** All-mapped-beads-closed → closable;
  any open → not; unmapped issue → absent; disabled short-circuit → clean no-op. Plus an assertion
  that the limitation caveat is still present in SKILL.md — cheap insurance on the plan's most
  misreadable output.
  - depends-on: 4.3
- **Issue 4.5: Update #117 and file the gap-closing follow-up.** Comment on #117 with the explicit
  in/out split and **leave it open**. Separately file a `yf-plan` issue: have Phase 4.5 stamp the
  coarse tracker URL onto the plan epic (`bd update <epic> --external-ref <url>`), which would make
  future coarse trackers visible to the per-bead signal **with no coupling**. File only —
  implementing it is `yf-plan`'s scope.
  - depends-on: 4.4
  - resolves-upstream: #117 (partial)

### Epic 5: Harden so the contradiction cannot silently return

- **Issue 5.1: Add the scoped acceptance check.** Per the 1.4 contract, assert no prescriptive raw
  `bd <backend>` push survives in **fenced ```bash blocks within the Push step and Backend
  generalization sections**. Prose, tables, and blockquotes are out of scope — the invariant
  statements and dated verification blockquotes legitimately contain the string, and a global grep
  would fail on them or pressure someone into deleting them.
  - depends-on: Epic 3, Epic 4
- **Issue 5.2: Update `protocols/UPSTREAM_TRACKING.md` and restamp the manifest.** The rule should
  name the concrete verb now that one exists. Requires
  `uv run <skill-dir>/scripts/manifest_update.py <skill-dir>/protocols`, with rule and
  `manifest.json` **committed together** — a drifted hash makes every dependent skill's preflight
  report `rule_drift`.
  - depends-on: 5.1
- **Issue 5.3: Full-tier validation.** Whole `test_upstream.py` suite green (48 existing + new),
  markdown lint on edited `.md` files, and drift-check across the SPEC↔SKILL↔protocols edges.
  - depends-on: 5.2

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: the emitted push command actually matches beads
- Type: auto
- Condition: after the #129 separator fix, the command `plan_hoist()` emits must match the expected
  number of beads — the property whose absence *is* #129. Blocks all downstream work, because
  routing the skill's procedure onto an unverified push is the failure this plan exists to prevent.
- Test:
  ```bash
  # Two known-mapped beads; the dry-run must report exactly 2.
  GITHUB_TOKEN=$(gh auth token) bd github push yf-m78m yf-252c --dry-run 2>&1 | grep -q 'Pushed 2 issues'
  ```
- Blocks: Epic 3, Epic 5
- Instructions: complete Issues 2.1 and 2.4, then run the test. A missing `✓ Pushed N` line means
  the ids are not matching — the exact #129 signature.

### Capability Gate: `push` verb exists before the prose points at it
- Type: auto
- Condition: `upstream.py push` is registered and runnable before any SKILL.md rewrite claims it —
  the inverse of the bug being fixed (documentation referencing a non-existent verb).
- Test: `uv run skills/yf-beads-upstream/scripts/upstream.py push --help >/dev/null 2>&1`
- Blocks: Issues 3.3, 3.4, 3.5
- Instructions: complete Issues 3.1 and 3.2, then run the test.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| Risk | Mitigation |
|:--|:--|
| The #129 fix is applied to `plan_hoist` but a sibling builder keeps the same separator assumption. | Issue 2.3 audits every emitted-command builder, not just the one that failed. |
| The fail-closed guard (2.2) is implemented by parsing push output, which is a fragile contract with `bd`. | 1.1 states the *requirement*; 2.2 chooses the mechanism and records why. If output-parsing is chosen, the parse is the thing 2.4's tests pin. |
| A find-replace strips the descriptive mentions, destroying the skill's explanatory value — including the invariant statements that quote the forbidden command. | `findings/exp-01` classifies every site; 1.4 defines the procedure/explanation boundary mechanically; 5.1's check is scoped to fenced bash blocks in two named sections. |
| The prescriptive site list is trusted from a grep and misses an instruction phrased without the literal backend token. | Issue 3.3 re-derives the list by reading the sections end to end. Success Criterion 3 is stated against the sections, not a fixed count. |
| The §4/§6 rewrite is treated as mechanical and breaks the recovery story — particularly §6's `Would update` vs `Would create` tripwire. | Issue 3.5 states it is a re-derivation and names the tripwire as must-preserve. #129 makes it more load-bearing, not less: a push can now be known to report nothing at all. |
| `closable` is read as fully closing #117, and the four motivating trackers assumed handled. | Disposition is **partial**; the gap is in the SPEC (1.3), the prose (4.3), a test (4.4), and #117's own update (4.5). |
| The `closable` limitation caveat is softened or dropped during execution, so a clean run reads as "nothing to close". | Issue 4.4 asserts the caveat string is present in SKILL.md. |
| Editing `protocols/UPSTREAM_TRACKING.md` without restamping breaks every dependent preflight with `rule_drift`. | Issue 5.2 names the restamp command and requires rule + `manifest.json` in one commit. |
| New tests repeat #129's mistake — asserting the emitted string rather than the contract. | Called out in the Approach and in Issues 2.4 and 3.6. 2.4 specifically asserts *no comma appears between ids*, which the old-style test could not have caught. |
| The plan overstates enforcement — nothing stops an operator typing `bd github push` directly. | The Approach states the boundary explicitly: the documented path is compliant and regressions are checked; the command is not made impossible. |
| Scope creep into the wider upstream backlog (#60, #51/52/53, #102). | All excluded with reasons. Epic 4's follow-up is **filed, not implemented**. |

## Success Criteria

1. **#129 is fixed and proven**: emitted push commands use space-separated ids, a dry-run over two
   known beads reports `✓ Pushed 2 issues`, and the local-close stage cannot run on an unverified
   push.
2. `upstream.py push --issues <csv> [--apply]` exists, always dry-runs first, is scoped — never a
   bare `sync` — and matches the existing `--apply`-only idiom.
3. **Every prescriptive site in the Push step and Backend generalization sections routes through
   the verb**, and all descriptive mentions — the dated verification blockquotes, the
   three-mechanism disambiguation, and the safety-invariant statements — survive verbatim. (Stated
   against the sections, not a fixed count, because the count came from a grep.)
4. Following SKILL.md end to end performs a compliant push with no hand-run `bd <backend>` command.
5. `closable` reports per-bead-terminal upstream issues, proposes `gh issue close` commands, and
   **never closes anything itself**.
6. #129, #106, and #105 close. **#117 stays open**, updated with the coarse-tracker gap; the
   `yf-plan` epic-stamping follow-up is filed.
7. Issue 5.1's check fails if a prescriptive raw push is reintroduced into a fenced procedure block,
   and passes on the descriptive mentions.
8. `test_upstream.py` fully green (48 existing plus new), markdown lint clean, drift-check PASS, and
   the protocols manifest hash restamped in the same commit as the rule edit.
9. One coarse upstream tracking issue for this plan.
