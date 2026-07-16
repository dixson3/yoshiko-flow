# Plan: Fix credibility_scorer tz-naive crash + dev-tooling domain tiers (#87) and add parked-plan visibility to yf-plan intake/status (#86)

**ID:** plan-028-james-dixson-a9738b
**Author:** james-dixson
**Created:** 2026-07-15
**Status:** complete
**Epic:** yf-mol-181
**Fingerprint:** 832dd5b34e3a87acc96ef3180df330ccdbdb6310d49e6e8da05e557addad68a5
**Phase log:**
- 2026-07-15 scoping: initial scope captured
- 2026-07-15 drafting: synthesizing plan — 2 epics, no investigation needed (concrete fixes)
- 2026-07-15 review: plan v1 presented — red-team REVISE (pass-1), 4 concerns resolved
- 2026-07-15 review: plan v2 presented — red-team APPROVE (pass-2), 2 residual items folded in
- 2026-07-15 ready-for-approval: ready-check green — red-team APPROVE (pass-2) + audit pass
- 2026-07-15 approved: operator approved
- 2026-07-15 intake: epic yf-mol-181 poured
- 2026-07-15 executing: start gate resolved
- 2026-07-15 reconciling: post-execution reconciliation
- 2026-07-15 complete: plan complete — #87 and #86 resolved, merged + pushed

## Objective

Ship two small, well-specified fixes to this repo's skills, each closing one open GitHub
issue:

1. **#87 (yf-research):** `credibility_scorer.py` crashes on timezone-naive publication
   dates and mis-scores official dev-tooling documentation domains.
2. **#86 (yf-plan):** an approved-but-unexecuted plan masquerades as completed (intake
   commit subject + tracking-issue title read as shipped work) and has no visibility
   surface, so parked plans are silently forgotten.

The two issues are unrelated but bundled into one plan (precedent: plan-016, plan-023) —
both are small, both land in `skills/`, and both follow the same SPEC-first → fix → test
shape.

## Motivation

Both problems were hit live and cost real triage time:

- **#87** was found during yf-research run 272 (Git forge viability). A tz-naive ISO date
  raises `TypeError: can't subtract offset-naive and offset-aware datetimes` and **crashes
  the whole scoring batch**, forcing the caller to pre-normalize every date. Separately,
  official docs domains that came up repeatedly in that research (`docs.gitea.com`,
  `docs.github.com`, `docs.gitlab.com`, `forgejo.org`, …) fall through to the `30`
  unknown-domain score, forcing manual rubric correction on every citing pass.
- **#86** was hit during triage of the open-issue backlog: plan-026 was approved and
  intake'd on 2026-07-11 but **never executed**, yet a `git log` scan and its tracking
  issue both read as if the work shipped, nearly leading to a wrong "these issues are
  stale, close them" call. Under the intake-at-execute model, INTAKE stops at
  approved+committed+landed+tracking-issue-filed and defers the pour/execution to
  `/yf-plan execute` — which for plan-026 was simply never run. Nothing surfaced that
  parked state.

Affected: anyone running yf-research (crash + manual score correction) and any operator
scanning plan/issue history (false "done" reading, forgotten parked plans).

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| [#87](https://github.com/dixson3/yoshiko-flow/issues/87) | credibility_scorer.py: tz-naive date crash + domain allowlist misses dev-tooling primaries | include | Both sub-fixes in scope; fix 2 uses allowlist + heuristic (operator decision) | Epic 1 |
| [#86](https://github.com/dixson3/yoshiko-flow/issues/86) | yf-plan: approved-but-unexecuted plans masquerade as completed; add parked-plan visibility | include | All three fixes in scope incl. optional tracking-issue title rename (operator decision) | Epic 2 |

## Investigation Findings

No investigation phase. Both issues arrived with concrete, located fixes; all target code
(`_currency_score`, `_domain_authority_score`, `TIER_2_DOMAINS`, `_commit_plan`, the `list`
command, SKILL.md Phase 4.5) was read directly during scoping. Scoping resolved the three
open design choices via operator decision (see Approach).

## Approach

SPEC-first for **both** epics (repo mandate, AGENTS.md): each epic lands its per-skill
`skills/<skill>/SPEC.md` `REQ-*` edit **before** the implementation and tagged test. The
**living amendment log lives only in the root `SPEC.md`** (one entry per plan, keyed
`plan-NNN`) — the per-skill SPECs carry only requirements — so the plan records a **single
`plan-028` amendment-log entry in root `SPEC.md`** covering both #87 and #86, alongside the
two per-skill REQ edits. The two epics touch disjoint **skill** files (`yf-research` vs
`yf-plan`), so their implementation issues are independent and parallelizable — with **one
exception**: root `SPEC.md` is a shared file. To avoid a collision on the single `plan-028`
amendment entry, **Issue 1.1 owns and authors that entry** (covering both #87 and #86);
Issue 2.1 references it rather than re-authoring, and the two SPEC-first steps **serialize on
root `SPEC.md`** (Issue 2.1's root-SPEC touch waits for 1.1). Per-skill REQ edits and all
implementation remain parallel.

**Operator scoping decisions (2026-07-15):**

- **#87 fix 2 → allowlist + heuristic.** Add the 7 named domains to `TIER_2_DOMAINS` **and**
  add a heuristic Tier-2 bump for `docs.*` hosts and `.dev` TLDs, so future vendor-doc
  domains don't need a one-off allowlist edit.
- **#86 fix 2 → both surfaces.** Surface parked (approved-but-unexecuted) plans in **both**
  `/yf-plan status` and a **land-the-plane** check.
- **#86 fix 3 → yes, rename the title.** Change the Phase 4.5 tracking-issue title to
  `plan-NNN execution tracking` (drop the past-tense-glancing "Complete execution of …").

**Portability note (#86 land-the-plane surface).** Per the repo's persistence rules, the
land-the-plane nudge is a **documented SKILL.md step that calls a `plan_manager.py` verb**,
not a Claude-harness hook or `/schedule` — it stays cross-harness portable.

## Epics

### Epic 1: #87 — credibility_scorer tz-naive fix + dev-tooling domain tiers (yf-research)

- Issue 1.1: **SPEC-first.** Revise `skills/yf-research/SPEC.md` REQ-RESEARCH-023 (or add a
  sibling `REQ-RESEARCH-024`) to require: (a) `_currency_score` normalizes tz-naive
  publication dates to UTC rather than crashing; (b) `_domain_authority_score` tiers
  official vendor-doc domains at Tier 2, via both an explicit allowlist and a `docs.*` /
  `.dev` heuristic. **Author the shared `plan-028` entry in the root `SPEC.md` living
  amendment log** (this issue owns it — the entry covers both #87 and #86; see Approach) —
  not in the per-skill SPEC, which has no amendment log.
- Issue 1.2: Fix `_currency_score` (`skills/yf-research/scripts/credibility_scorer.py`
  ~line 95): if `pub.tzinfo is None`, set `pub = pub.replace(tzinfo=timezone.utc)` before
  computing `age_days`. No more `TypeError` on naive dates.
  - depends-on: 1.1
  - resolves-upstream: #87 (include)
- Issue 1.3: Extend `_domain_authority_score` (same file, ~line 58): add
  `docs.gitea.com, forgejo.org, docs.gitlab.com, docs.github.com, docs.gocd.org,
  cli.github.com, github.blog` to `TIER_2_DOMAINS`, **and** add a heuristic Tier-2 bump
  (host starts with `docs.` or TLD is `dev`) evaluated **after** the exact-tier loop and
  **before** the unknown-domain fallback, so it never downgrades a Tier-1 match.
  - depends-on: 1.1
- Issue 1.4: Add `skills/yf-research/scripts/test_credibility_scorer.py` (Tier-1 unit test),
  mirroring the sibling `test_link_normalizer.py` **PEP-723 inline-deps + `uv run <file>`**
  invocation convention (not `python -m pytest`). Cases: tz-naive date no longer raises and
  scores by age; tz-aware / `Z` / evergreen / missing-date inputs unchanged; the 7 named
  domains + a novel `docs.*` / `.dev` host score in the Tier-2 band (70–84); unknown domains
  still score 30; Tier-1 gov/edu never downgraded. Wire it into `CHANGE-VALIDATION.md` so it
  actually runs (the existing `uv-research` recipe runs only `test_link_normalizer.py`):
  add a **command row (new fast id, e.g. `uv-research-cred`) to BOTH the §1 fast tier and the
  full tier**, add a **§3 Trigger-Scope row**
  (`skills/yf-research/scripts/test_credibility_scorer.py`), **also add the new fast id to the
  existing `skills/yf-research/scripts/**` scope row** (so an edit to `credibility_scorer.py`
  alone fires the new test in the fast tier — mirrors the `skills/yf-plan/scripts/**` →
  `uv-yf, uv-yf-cascade` two-id precedent), and update the **§2 Signal Fingerprint**.
  - depends-on: 1.2, 1.3

### Epic 2: #86 — parked-plan visibility for yf-plan (intake + status + land-the-plane)

- Issue 2.1: **SPEC-first.** Revise `skills/yf-plan/SPEC.md`: (a) amend REQ-PLAN-064's
  commit-message format so the **approved-phase** intake subject signals plan *state* (e.g.
  `plan-NNN: INTAKE approved (awaiting /yf-plan execute) — <objective>`) rather than
  restating the objective as if done; (b) add a `REQ-PLAN-0NN` for **parked-plan detection**
  — a plan is *parked* when its status is `approved` (coarse filter) **and its stored
  fingerprint is present and fresh** (`bool(stored) and stored == current`, the same signal
  execute-eligibility keys on per `plan_manager.py:828-829` — NOT the "not stale" test, which
  is also true when no fingerprint is stored). Surface it via `list` / `/yf-plan status` and a
  land-the-plane check; (c) note the Phase 4.5 tracking-issue title is
  `plan-NNN execution tracking`. The root `SPEC.md` `plan-028` amendment entry is authored by
  Issue 1.1 (shared, covers #86 too) — **reference it, do not re-author**; this issue's
  root-`SPEC.md` touch serializes after 1.1 (see Approach).
  - depends-on: 1.1
- Issue 2.2: State-signalling intake commit subject in `_commit_plan`
  (`skills/yf-plan/scripts/plan_manager.py` line 1151): when the resolved phase is
  `approved`, emit the state-signalling subject; other phases keep
  `plan-NNN: <phase> — <objective>`. Objective stays in the commit body.
  - depends-on: 2.1
  - resolves-upstream: #86 (include)
- Issue 2.3: Parked-plan classification + `/yf-plan status` surface. Add a helper that
  classifies a plan as **parked** = status `approved` (coarse filter) AND stored fingerprint
  present and fresh (`bool(stored) and stored == current`, reusing `_fingerprint_status`).
  This excludes `executing`/`complete` (fail the status filter), stale-approved (fails
  freshness — already carries the `stale_approved` tag at line 797), and `approved` plans
  with no stored fingerprint (would otherwise get a contradictory execute nudge). An
  intake'd-but-unexecuted plan carries status `approved` per the vocabulary (plan_manager.py
  ~line 824) — the classifier's premise. Expose a `parked` flag in `list --json` + a rendered
  tag alongside the stale tag, and update SKILL.md `/yf-plan status` to print the nudge:
  "N plan(s) approved but not executed — run /yf-plan execute <id>."
  - depends-on: 2.1
- Issue 2.4: Land-the-plane parked nudge. Add a `plan_manager.py parked --json` verb (or
  reuse `list` filtered to parked) that enumerates parked plans, and document a
  land-the-plane SKILL.md step that calls it and surfaces the same nudge. Portable
  (SKILL.md + script verb), no harness hook.
  - depends-on: 2.3
- Issue 2.5: Tracking-issue title rename. Update SKILL.md Phase 4.5 so the coarse tracking
  issue is titled `plan-NNN execution tracking` (not `Complete execution of plan-NNN`).
  Docs-only (the title is authored by the agent per SKILL.md, not by a script).
  - depends-on: 2.1
- Issue 2.6: Tests for the approved-phase subject builder and the parked classifier
  (`approved`+present-and-fresh fingerprint → parked; `approved`+stale → not parked, keeps
  stale tag; `approved`+no fingerprint → not parked; `executing`/`complete` → not parked).
  Prefer folding these into `skills/yf-plan/scripts/test_worktree.py` (already wired via the
  `uv-yf` recipe) so no new CHANGE-VALIDATION wiring is needed. If instead a new test file is
  added, wire it into `CHANGE-VALIDATION.md` the same way as Issue 1.4 (command row in fast +
  full tiers, §3 trigger-scope row, §2 fingerprint update).
  - depends-on: 2.2, 2.3, 2.4

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

### Reconcile Gate (upstream issues incorporated)

- Type: auto (all execution beads closed)
- Condition: both #87 and #86 are `include` dispositions
- Blocks: reconcile step (update/close #87 and #86 with resolution)

## Risks & Mitigations

| Risk | Mitigation |
|:-----|:-----------|
| `docs.*` / `.dev` heuristic over-promotes a low-quality host (e.g. a personal `docs.` subdomain) | Heuristic runs only **after** the exact-tier loop, caps at Tier 2 (70–84, not Tier 1), and Tier-2 is "official docs / major press" — a modest, bounded bump. Unit test pins the band. |
| Substring domain matching (`td in domain`) interacts with new entries | New TIER_2 entries are full hostnames; heuristic uses `startswith("docs.")` / TLD `== "dev"`, not substring — no new false-substring risk. Test covers a novel host. |
| Changing REQ-PLAN-064's commit-message format breaks an existing test asserting the old subject | Grep for tests asserting `approved —` / the subject format before editing; update them in the same change-set (SPEC-first keeps the requirement and test aligned). |
| Parked detection double-counts stale-approved plans | Classifier requires fingerprint **not** stale; stale-approved already has its own tag (line 797). The two states are mutually exclusive in the output. |
| Land-the-plane surface tempts a harness-specific hook | Explicitly a SKILL.md-documented step calling a portable `plan_manager.py` verb — no `/schedule`, no Claude hook (repo persistence rule). |

## Success Criteria

- `_currency_score` returns a score (never raises) for a tz-naive ISO date, and is
  unchanged for tz-aware / `Z` / evergreen / missing-date inputs.
- The 7 named dev-tooling domains and a novel `docs.*` / `.dev` host score in the Tier-2
  band (70–84); unknown domains still score 30; Tier-1 domains are never downgraded.
- `test_credibility_scorer.py` exists, passes, and is wired into `CHANGE-VALIDATION.md`.
- The intake commit subject for an approved plan signals awaiting-execute state, not shipped
  work; `/yf-plan status` and the land-the-plane check both surface parked plans with the
  run-`/yf-plan execute` nudge; the Phase 4.5 tracking issue is titled
  `plan-NNN execution tracking`.
- Each behavior change is backed by a landed SPEC requirement + amendment-log entry and a
  tagged test; the FULL `CHANGE-VALIDATION.md` suite passes over the merged tree.
- #87 and #86 are reconciled (updated/closed) per their `include` dispositions.
