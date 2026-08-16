---
type: Plan
okf_spec: OKF-PLAN
id: plan-040-james-dixson-1cabe4
author: james-dixson
created: '2026-08-16'
status: approved
deliverable_class: standard
fingerprint: bab20550855b8b7b8416bf7248376ff113b206797a5578fab0b3552f189fed62
---
# Plan: Replace bd-backend push with gh-direct issue creation across push/hoist/land, and close the coarse-tracker visibility gap

**ID:** plan-040-james-dixson-1cabe4
**Author:** james-dixson
**Created:** 2026-08-16
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** bab20550855b8b7b8416bf7248376ff113b206797a5578fab0b3552f189fed62

## Objective

Change the upstream write mechanism to **`bd` reads bead content, `gh` writes issues,
`bd update --external-ref` records the mapping**, across all three write paths (`push`, `hoist`,
`land`) — and, on the same `external_ref` mechanism, close the loop on the read side so finished
upstream issues can actually be found and proposed for closure.

Three sides of one mechanism, which is why they are one plan:

| Side | What it does with `external_ref` | Issue |
| :-- | :-- | :-- |
| write | gh-direct creates/updates the issue, then records the mapping | [#133](https://github.com/dixson3/yoshiko-flow/issues/133) |
| read | `closable` groups beads by mapping to propose closures | [#117](https://github.com/dixson3/yoshiko-flow/issues/117) |
| coverage | `yf-plan` stamps the coarse tracker so it is mapped at all | [#131](https://github.com/dixson3/yoshiko-flow/issues/131) |

Out of scope, deliberately: adding GitLab/Jira/Linear **support** (#51/#52/#53) — this plan
demotes them rather than fixing them; and #111 (beads alternatives), which is a different
question entirely.

## Motivation

**The write path depends on a mechanism nobody chose.** Every upstream write shells out to
`bd github push` (≡ `bd github sync --push-only --issues`). #133 establishes that this was never
justified anywhere in the repo — `SPEC.md` presupposes it (REQ-BUP-030/031) without arguing for
it. It was inherited because bd 1.0.5 happened to ship the feature.

Three measured consequences, from #133:

- **The one capability that would justify the dependency is forbidden.** What `sync` uniquely
  offers over a `gh` call is bidirectional sync with conflict resolution. The skill's central
  safety invariant, **GR-BUP-001** (REQ-BUP-030), is *"never run a bare `bd <backend> sync`"* — so the dependency
  is retained and then deliberately disabled from doing the only thing that justifies it.
- **The mapping is already ours to write.** Bead `yf-uz5k` was mapped to #92 **by hand**; bd had
  never pushed it, yet `bd github push --dry-run` reported *"Would **update**"*, not *"Would
  create"*. The create-vs-update decision is driven by the `external_ref` field alone — there is
  no hidden sync table to desynchronize.
- **#129 was an artifact of bd's CLI surface.** `sync --issues` takes comma-separated ids;
  `push` takes positional space-separated ids. Translating between them produced a command
  matching zero beads at exit 0, which then tombstoned beads locally.

**The read path is worse than reported.** `closable` shipped in plan-038 to propose closures —
but it **does not complete on this repo** (EXP-002): 991 sequential `bd show` subprocesses to
read a field `bd list --all --json` already returns. Meanwhile coarse plan trackers are
structurally invisible to it, because `yf-plan` files them with a bare `gh issue create` and
records the URL on no bead. Five have now gone stale and been closed by hand — #103, #95, #96,
#98, and #134 (this session).

Who is affected: anyone using `yf-beads-upstream` in any repo. What triggered it: plan-038 made
`upstream.py push` the single documented write path, so there is now **exactly one place** the
mechanism lives — the cheapest moment to swap the implementation underneath it.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#133](https://github.com/dixson3/yoshiko-flow/issues/133) | replace `bd <backend> push` with gh-direct across push/hoist/land | include | The core swap. All four of its open decisions resolved at scoping — see Approach | 2.1–2.7, 3.1–3.4 |
| [#117](https://github.com/dixson3/yoshiko-flow/issues/117) | push is write-only — no verb proposes CLOSING finished issues | include | Marked *"#117 partial"* in REQ-BUP-052: the per-bead signal shipped, the coarse signal did not. #131's stamp closes it **without** the per-plan `plan.md`-status signal #117 proposed, avoiding a `plans-root` coupling | 4.1–4.3 |
| [#131](https://github.com/dixson3/yoshiko-flow/issues/131) | stamp the coarse tracker URL onto the plan epic | include | One line in `yf-plan` §4.5. Independent of the swap — it writes `external_ref`, the one mechanism #133 preserves — so no rework risk | 4.3 |
| [#132](https://github.com/dixson3/yoshiko-flow/issues/132) | `BACKEND_AUTH` has no jira entry — `--backend jira` emits `GITHUB_TOKEN` | supersede | **Mooted by the GitHub-only decision.** `BACKEND_AUTH` and the whole `--backend` surface are removed, so the broken jira entry ceases to exist rather than being fixed | 2.4, 5.2a, 5.2b |
| [#138](https://github.com/dixson3/yoshiko-flow/issues/138) | plan-040 execution tracking | tracker | The coarse plan-level tracker, filed at intake. Not a work item. **Issue 4.3's stamp applies to this plan too** — once 4.3 lands, plan-040's own epic carries this URL, making it the first tracker `closable` can see | 4.3 |
| [#51](https://github.com/dixson3/yoshiko-flow/issues/51) | Add GitLab upstream tracking support | exclude | Reframed, not rejected. After 2.4 these become "add a backend to a gh-direct architecture", not "fix a half-wired bd backend". Left open with a note | — |
| [#52](https://github.com/dixson3/yoshiko-flow/issues/52) | Add Jira upstream tracking support | exclude | As #51 | — |
| [#53](https://github.com/dixson3/yoshiko-flow/issues/53) | Add Linear upstream tracking support | exclude | As #51 | — |
| [#60](https://github.com/dixson3/yoshiko-flow/issues/60) | mutually-exclusive `requires:<platform>` labels in worklist filtering + hoist | exclude | Touches label *semantics* in `enumerate`/`hoist`, adjacent to this plan's label mapping but a separate feature. Deferring avoids widening an already-large plan | — |
| [#111](https://github.com/dixson3/yoshiko-flow/issues/111) | Investigate `br` / `ticket-rs` as beads alternatives | exclude | Different question. Note it is mildly *informed* by this plan: gh-direct reduces the bd surface area a replacement would have to match | — |

## Investigation Findings

Two experiments, both against the live repo. Marked **[measured]** / **[inferred]** per
REQ-AGENT-021.

### EXP-001 — what gh-direct must actually reimplement ([findings](findings/exp-001-label-mapping-gap.md))

- **The label mapping exists nowhere in this repo** **[measured]** — no match for `type::` /
  `priority::` in `upstream.py`, `SKILL.md`, or `SPEC.md`. `upstream.py` never constructs a
  label. The convention is known only from *observed output*.
- **The repo's label set does not cover the bead space** **[measured]**. Types in use:
  `task` 753, `epic` 182, `molecule` 42, `feature` 9, `chore` 2, `bug` 2, `decision` 1.
  Labels that exist: `type::{bug,epic,feature,task}` only — **`type::molecule`, `type::chore`,
  `type::decision` are missing**, as is any label for the one P4 bead.
- **[inferred]** `gh issue create --label X` fails when `X` does not exist, whereas bd evidently
  creates labels on demand (the repo carries bd-made `upstream-followup` / `plan-033-followon`).
  **This specific claim is not measured** — verifying it needs a real outward-facing write, so it
  is Issue 1.1, the plan's first execution step, with a falsification test.
- **[inferred]** So "~20 lines" understates the work: the mapping must be reverse-engineered and
  **specified for the first time**, and the missing-label policy is a real decision.

### EXP-002 — `closable` does not complete ([findings](findings/exp-002-closable-n-plus-1.md))

- **`closable` produced zero output in 4 minutes and was killed** **[measured]**. From an
  operator's seat, indistinguishable from a hang.
- **Cause is a removable N+1** **[measured]**: `cmd_closable` loads all rows in one
  `bd list --all --json`, then calls `external_for(id)` per row — a fresh `bd show` subprocess
  each — across **991 beads**.
- **The data is already in hand** **[measured]**: `bd list --all --json` returns all 991 beads
  *and carries `external_ref`*; only **20** beads have one. 991 subprocesses → 0.
- **[inferred]** #131 as filed would ship a stamp feeding a verb nobody can run, so the perf fix
  is a prerequisite, not an optimization.

## Approach

**One mechanism, three sides.** `external_ref` is the whole mapping (#133 Measurement 1). This
plan makes the write side own it (`gh` + `bd update --external-ref`), the read side use it
efficiently (`closable` reads the field it already has), and the coverage side populate it for
coarse trackers (`yf-plan` stamps the epic). Splitting these across plans would mean touching one
field three times under three separate reviews.

**Scoping decisions, all four of #133's plus two from investigation:**

| Decision | Resolution |
| :-- | :-- |
| **1. Non-GitHub backends** | **GitHub only; demote the others explicitly.** gitlab/jira are removed from the supported surface rather than left as broken stubs implying support. Single mechanism, no coexistence — the exact condition #133 identifies as having produced #129. Moots #132; reframes #51/#52/#53 |
| **2. GR-BUP-001 rewording** | **Reword, not delete.** (#133 and `SPEC.md:165` both misname this `GR-BUP-002`, which is the *token/inline-auth* guardrail (REQ-BUP-031); the never-bare-sync invariant is **GR-BUP-001** (REQ-BUP-030). Corrected here and fixed in-repo by Issue 2.3.) The invariant exists because a raw `bd sync` is *destructive* — it re-imports every upstream issue as a duplicate bead. A raw `gh issue create` is not; worst case is an unmapped duplicate. The rationale changes, so `protocols/UPSTREAM_TRACKING.md` must be revised **and re-stamped in the same commit** (hash-pinned in `protocols/manifest.json`) |
| **3. Dry-run replacement** | **Locally-rendered preview + structural verification.** Absent `--apply` renders the exact planned actions (create vs update, per issue, with resolved title/body/labels). Verification becomes "did each create return an issue URL" rather than parsing `Pushed N issues` — structural, not textual. Also removes a network round-trip |
| **4. `Pushed N issues` parse** | Replaced by the structural check in (3). REQ-BUP-050's fail-closed *contract* is preserved; only its *evidence* changes, from a scraped string to a returned URL |
| **5. Missing-label policy** (new, EXP-001, **revised at review**) | **Restrict-and-drop:** emit only labels that exist; skip unknown ones. Originally decided as ensure-label-before-use on an EXP-001 figure that overstated the gap ~5× — `CONTAINER_TYPES = {epic, molecule, gate}` means `candidate_filter` drops those from the push path, so the 42 `molecule` and 182 `epic` beads were never candidates. The **real** uncovered population is `chore` (2), `decision` (1) and one P4 bead — **3 of 991**. Ensure-label-before-use would buy labels on 0.3% of beads at the cost of label-write token scope and an API call per unseen label. Exception, stated rather than implicit: an explicit `hoist --issues <epic-id>` bypasses `candidate_filter`, so epics *can* reach the write path — `type::epic` already exists, so that case stays covered |
| **6. `closable` performance** (new, EXP-002) | **Fix in this plan**, as a prerequisite to #131's stamp |

**SPEC-first**, per the repo mandate: the field mapping and the reworded invariant land as
`REQ-BUP-*` amendments ahead of implementation.

**The riskiest assumption is tested first.** Issue 1.1 falsifies the `gh`-fails-on-unknown-label
claim before anything depends on it. If it fails, decision 5 collapses and Epic 2 simplifies.

## Epics

### Epic 1: Falsify the load-bearing assumption

- **Issue 1.1:** Test whether `gh issue create --label <nonexistent>` fails or silently succeeds,
  and whether `gh label create` is idempotent. Use a **scratch issue in this repo**, closed and
  deleted immediately, or a throwaway private repo — record which. Write the verbatim output to
  `references/gh-label-behavior.md`.

  **Falsify BOTH halves of the premise, not one** (pass-1 C5). Decision 5's original rationale was
  "matching bd's apparent behavior" — which rests on a *second* inferred claim, that bd creates
  labels on demand, corroborated only by the existence of `upstream-followup` /
  `plan-033-followon` (circumstantial: those could equally have been hand-made). So on the same
  authorized scratch write, also push one bead of an unmapped type (`chore` or `decision`) via the
  **current** `bd github push` path and record which side actually creates the label.

  Four outcomes, each with a consequence to record before proceeding:

  | `gh` fails? | `bd` creates? | Consequence |
  | :-: | :-: | :-- |
  | no | — | the label concern collapses entirely; restrict-and-drop is a no-op |
  | yes | yes | restrict-and-drop is a **deliberate divergence** from bd — say so in 2.2 |
  | yes | no | restrict-and-drop is **parity**; the plan's framing is confirmed |
  | yes | untestable | record it as untested rather than assuming |

  Report the result before proceeding — do not assume the expected answer.
  - depends-on: — (entry issue)

### Epic 2: SPEC-first — specify what has only ever been observed

- **Issue 2.1:** Probe and record the **`bd` version floor** this plan depends on — the minimum
  version for `bd update --external-ref` and for `bd list --all --json` returning `external_ref`
  (SC15). If it cannot be determined by probing, declare **1.1.2 a floor because it is the only
  version verified**, and say so — an assertion labelled as one, not a measurement (pass-2
  Missing). Then specify the **bead→issue field mapping** in `skills/yf-beads-upstream/SPEC.md`
  as a new `REQ-BUP-*`: `title`→title verbatim; `description`→body verbatim; `issue_type`→
  `type::<t>`; `priority`→`priority::<level>` (state the numeric→word table explicitly, including
  the currently-unmapped P4); bead labels passed through; `external_ref` written back. Record
  explicitly that `notes` and `design` do **not** sync, and whether that remains intended.
  This mapping has never existed in writing (EXP-001) — reverse-engineer it from observed output
  and from bead `yf-1656` → issue #132.
  - depends-on: 1.1
- **Issue 2.2:** Specify the **missing-label policy** per decision 5 (restrict-and-drop),
  conditional on 1.1's result. Specify that **a dropped label is reported, not silent** — it
  appears on the push preview naming the bead and the skipped label. That report is what R6
  relies on as its revisit trigger, so without it R6's mitigation has no producer (pass-2 D4).
  No token-scope clause is needed: restrict-and-drop writes no labels.
  - depends-on: 2.1
- **Issue 2.3:** Reword **GR-BUP-001** and the `REQ-BUP-030` family for a non-destructive write
  path: the invariant survives, its rationale changes. Revise
  `skills/yf-beads-upstream/protocols/UPSTREAM_TRACKING.md` **and re-stamp
  `protocols/manifest.json` in the same commit** — the rule is hash-pinned, so a revision without
  a re-stamp is a preflight `rule_drift` failure for every consumer. Also fix `SPEC.md:165`'s
  existing misreference to `GR-BUP-002`. **Scope boundary with 2.6:** this issue owns
  **GR-BUP-001 / REQ-BUP-030** (never-bare-sync); **2.6** owns **GR-BUP-002 / REQ-BUP-031**
  (the auth model). They must not both edit the same guardrail — pass-2 D1.
  - depends-on: 2.2
- **Issue 2.4:** Specify **GitHub as the only supported backend** (decision 1): amend
  `REQ-BUP-040`, and mark the `--backend` flag and `BACKEND_AUTH` table for removal. State that
  #132 is mooted rather than fixed, and that #51/#52/#53 become "add a backend" against the new
  architecture.
  - depends-on: 2.3
- **Issue 2.5:** Specify the **preview + structural verification** contract (decisions 3/4):
  absent `--apply` renders planned actions locally; verification asserts a returned issue URL per
  create and a success status per update. Amend `REQ-BUP-050` so the fail-closed contract is
  preserved while its evidence changes from a scraped string to a structured return.
  - depends-on: 2.4
- **Issue 2.6:** Amend the requirements the swap **invalidates**, which pass-1 C3 found uncovered —
  without these, Epic 3 would implement against requirements that still mandate the deleted
  behavior:
  - **REQ-BUP-051** — mandates the dry-run-first / inline-auth push shape that Issue 3.2 deletes,
    while SC4 requires `BACKEND_AUTH` to grep to zero;
  - **REQ-BUP-031 / GR-BUP-002** — the **auth model** changes from inline `TOKEN=$(...)` to `gh`'s
    own credential store. This is a behavior and invariant change, so it lands **here**, not in
    Issue 5.1's documentation pass where the v1 draft had quietly put it;
  - **REQ-BUP-041** — the scoped-push translation table becomes dead;
  - **REQ-BUP-052** — Epic 4 changes `closable`'s contract (the one-`bd list` invariant, mapped-bead
    filtering), which needs its own amendment.
  - depends-on: 2.5
- **Issue 2.7:** Update the two **sibling spec files** written entirely in `bd <backend>` terms and
  never named as edit targets in the v1 draft (pass-1 C3): `spec/safety.md` (REQ-SAFE-001/002) and
  `spec/backends.md` (REQ-BE-001/002). Per pass-1's upstream assessment, REQ-BE-001 already states
  GitLab/Jira are unverified config-only stubs, so 2.4's demotion is **deleting a stub surface**,
  not withdrawing support — word it that way.
  - depends-on: 2.6

### Epic 3: Implement gh-direct across all three write paths

Do all three or none — migrating only `push` leaves two mechanisms with different failure modes
and separator conventions, the exact condition that produced #129.

- **Issue 3.1:** Implement the gh-direct core in `upstream.py`: `create_or_update(bead)` keyed on
  `external_ref` (present → `gh issue edit`; absent → `gh issue create` then
  `bd update <id> --external-ref <url>`), the field mapping from 2.1, the label policy from 2.2,
  and the structural verification from 2.5. Idempotency on `external_ref` is what prevents
  duplicates.
  - depends-on: 2.7
- **Issue 3.2:** Route **`cmd_push`, `cmd_hoist`, and `cmd_land`** through the 3.1 core, replacing
  `plan_push()`'s emitted `bd <backend> push` command strings at all three call sites. Delete
  `BACKEND_AUTH`, the `--backend` flag, and the dry-run/real command-pair construction. Preserve
  `hoist`'s local-close and `land`'s follow-on semantics unchanged — this issue swaps the write
  mechanism only.
  - depends-on: 3.1
- **Issue 3.3:** Re-validate the **third skill** that consumes this write path (pass-1 C4).
  `yf-beads-hygiene` shells out to `upstream.py hoist --issues <id> --dest <dest> --apply`
  (`beads_hygiene.py:551/579`), pins that contract across 14 references in its own `SPEC.md`, and
  asserts the argv in `test_beads_hygiene.py`. **Its tests mock the runner**, so an argv-compatible
  but semantically divergent `hoist` would pass them silently. Verify the contract end to end
  against the real `hoist`, and update `yf-beads-hygiene`'s SPEC/SKILL wording wherever it
  describes the `bd <backend>` mechanism rather than the delegation.
  - depends-on: 3.2
- **Issue 3.4:** Port and extend the test suite: fixture tests for create-vs-update on
  `external_ref`, the field/label mapping, the restrict-and-drop path (**asserting the drop is
  reported in the preview**, per 2.2), the preview rendering, the live-population `external_ref`
  check (SC13), and the fail-closed verification. Assert **no `bd <backend> push` string is emitted anywhere** — a
  grep-level guard mirroring the existing `check_prescriptive_push.py`. Wire into
  `CHANGE-VALIDATION.md`.
  - depends-on: 3.3
  - resolves-upstream: [#133](https://github.com/dixson3/yoshiko-flow/issues/133) (include, with 2.1–2.7, 3.1–3.3)

### Epic 4: Close the read/coverage side on the same mechanism

- **Issue 4.1:** Fix `closable`'s N+1 (EXP-002): source `external_ref` from the rows
  `load_universe_rows()` already returns; **stop calling `external_for` from `cmd_closable`**.
  Do **not** delete the helper — it has two other live callers (`upstream.py:460`, `:495`) and is
  monkeypatched by three existing tests (pass-2 D7). Reconcile
  `load_universe_rows()`'s docstring (*"All non-closed beads"*) with its actual `bd list --all`
  call, or filter to mapped beads directly.
  - depends-on: 2.7
  - Note: deliberately **not** chained behind Epic 3 (pass-1 C15). Epic 4 is a read-side fix on a
    field the write swap preserves; the file-level overlap with Epic 3 is small. Epic 4 runs in
    parallel with Epic 3 so the small high-value fix is not hostage to the large risky one.
- **Issue 4.2:** Add a **scale regression test** asserting `closable` issues exactly **one
  `bd list`** invocation and **zero per-bead `bd show`** invocations, independent of universe
  size — an invariant, not a wall-clock threshold, so it cannot silently regress as the DB grows.
  Record in `references/closable-after.md` **which copy of the skill produced the run** (repo vs
  `~/.claude/skills/`), per SC16 — context.md flags the divergence and it is load-bearing for the
  SC8/SC9 evidence.
  (Not "exactly one `bd` invocation": `upstream_enabled()` → `_config_get` → `bd config get` is a
  second subprocess this plan does not remove, so that phrasing would fail on correct code —
  pass-1 C7.) Re-run `closable` on the live repo and record the completion
  time in `references/closable-after.md` as the evidence #131 needs.
  - depends-on: 4.1
- **Issue 4.3:** Stamp the coarse tracker onto the plan epic (#131) — **in Phase 5, not §4.5**.

  #131 as filed says to stamp "in Phase 4.5, after creating the tracking issue". **That is
  impossible** (pass-1 C2): §4.5 runs at INTAKE, §4.6 states *"No pour happened at intake"*, and
  §5.2 owns the pour — §4.5's own text says the issue links the plan folder and *"(once poured)"*
  its epic. There is no epic id to stamp.

  Correct placement: **§5.2a, immediately after `record-epic`**, where the epic id is first known
  and the plan↔epic linkage is already written atomically. Make it idempotent and run it on the
  **§5.2b resume** branch too, so a plan whose tracker was filed late (or whose stamp failed) is
  repaired on the next execute rather than staying invisible forever. Where no tracker exists,
  skip with a note — never fail the pour.

  Add the corresponding `REQ-PLAN-*` to `skills/yf-plan/spec/`, and note in `yf-beads-upstream`'s
  SPEC that #117's coarse signal is discharged by this stamp rather than by a per-plan
  `plan.md`-status reader — no `plans-root` coupling in either direction.

  **Forward-looking only.** Existing unstamped trackers stay invisible; 4.4 handles those.
  - depends-on: 4.2
  - resolves-upstream: [#131](https://github.com/dixson3/yoshiko-flow/issues/131) (include)
- **Issue 4.4:** One-off backfill of the existing population. **First derive the plan→tracker
  map** — nothing in the v1 draft produced it (pass-1 C10), and these trackers are by definition
  the beads-unmapped population, so it cannot be read off `external_ref`:

  ```bash
  gh issue list --state all --search 'execution tracking in:title' --json number,title
  # cross-reference against docs/plans/*/plan.md `**Epic:**` fields
  ```

  Write the derivation to `references/tracker-backfill-map.md`, **including plans whose tracker
  cannot be identified** — the population is the ~40 completed plans, of which at least five
  (#103, #95, #96, #98, #134) are already closed and need no stamp. An unidentifiable tracker is
  recorded as such, not silently skipped.

  Then stamp each identified epic, run `closable`, and report — **propose only, close nothing.**
  Closing upstream issues is outward-facing and gated.
  - depends-on: 4.3
  - resolves-upstream: [#117](https://github.com/dixson3/yoshiko-flow/issues/117) (include, with 4.1–4.3)

### Epic 5: Documentation and migration

- **Issue 5.1:** Update `skills/yf-beads-upstream/SKILL.md` end to end for gh-direct: the Push
  step, the auth section (inline `GITHUB_TOKEN` → `gh`'s own auth), the removed `--backend`
  surface, and the preview/verification contract. Remove the `bd <backend>` command examples that
  2.3's reworded invariant no longer describes. Also document the **removed `--backend` flag** so
  an existing caller gets a named error rather than a bare argparse failure (SC14).
  - depends-on: 3.4, 4.4
- **Issue 5.2a:** **Draft** the upstream comments — for #51/#52/#53 the reframe (they now mean
  "add a backend to a gh-direct architecture"), for #111 the note that gh-direct narrows the bd
  surface a replacement must match, and for #132 the supersede rationale (the `--backend` surface
  was removed, so the broken jira entry ceased to exist rather than being fixed). Write each to
  `references/comment-<n>.md`. **No `gh` call.**
  - depends-on: 5.1
- **Issue 5.2b:** **Publish** the 5.2a drafts: `gh issue comment` on #51/#52/#53/#111, leaving all
  four **open**; `gh issue comment` + `gh issue close` on #132.
  - depends-on: 5.2a
  - resolves-upstream: [#132](https://github.com/dixson3/yoshiko-flow/issues/132) (supersede)

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

### Capability Gate: Scratch write for the label test

- Type: human
- Condition: operator authorizes Issue 1.1 to perform a **real** `gh` write (a scratch issue,
  closed and deleted immediately, or a throwaway repo) in order to falsify the
  unknown-label behavior.
- Test (**smoke check only** — it proves read access, NOT that a write was authorized; the
  `Condition` is the contract. Never treat a green test here as consent, pass-1): `gh auth status >/dev/null 2>&1 && gh repo view dixson3/yoshiko-flow --json name -q .name`
- Blocks: 1.1
- Instructions: The claim cannot be tested without an outward-facing write — that is why it is
  `[inferred]` in EXP-001 rather than measured. Authorizing this gate is authorizing a
  deliberately small, reversible one. Ungated alternative: skip 1.1 and adopt **restrict-and-drop** unverified,
  accepting that 1.1's outcome-table rows are recorded as untested and that the plan therefore
  cannot say whether restrict-and-drop is parity with bd or a deliberate divergence (pass-2 D6).

### Capability Gate: Upstream write

- Type: human
- Condition: operator has read the drafted comments in `references/comment-*.md` (produced by
  **5.2a**, which this gate does not block) and the `closable` proposals from 4.4, and authorizes
  publishing against `dixson3/yoshiko-flow`.
- Test (repo-root-relative — §6.1.5 runs gate tests against the merged checkout at repo root, not the plan dir; pass-1 C8): `gh auth status >/dev/null 2>&1 && test -s docs/plans/plan-040-james-dixson-1cabe4/references/closable-after.md && ls docs/plans/plan-040-james-dixson-1cabe4/references/comment-*.md >/dev/null 2>&1`
- Blocks: 5.2b
- Instructions: Gated on the **mutating** step only. The evidence the condition needs is produced
  by **5.2a** and **4.2** (which writes `closable-after.md` — the v1 draft credited it to 4.4),
  both outside the `Blocks` set, so the condition is reachable from the state the gate creates
  (REQ-AGENT-046). **4.4 proposes closures and closes nothing** — those `gh issue
  close` commands are operator-run.
- Note: the v1 draft of this plan blocked `5.2` while its condition required comments drafted
  *inside* 5.2 — the exact cycle #112 reports, reproduced here and caught by the conformance
  pass that plan-039 added. Recorded rather than silently fixed.

### Reconcile Gate

- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The plan's central premise is one [inferred] claim.** If `gh` does not fail on unknown labels, decision 5 and Issue 2.2's label-policy work are unnecessary. | high | Issue 1.1 falsifies it **first**, behind its own gate, before any dependent work. The plan is explicitly structured so a negative result *shrinks* Epic 2 rather than invalidating the plan. |
| R2 | **Reverse-engineering the field mapping may miss a field.** The mapping has never been written down (EXP-001); observed output on one bead is a sample, not a specification. | high | 2.1 specifies from observed output **and** names the known gaps (`notes`, `design`) explicitly. 3.4's fixture tests pin each mapped field. A missed field surfaces as a diff on the next push, not silently — but it is a real possibility and the reason 2.1 precedes 3.1. |
| R3 | **`protocols/manifest.json` re-stamp is easy to forget.** The rule is hash-pinned; revising `UPSTREAM_TRACKING.md` without re-stamping is a preflight `rule_drift` failure for every consuming repo. | high | 2.3 names the re-stamp in the same issue and the same commit. A success criterion checks the hash matches. |
| R4 | **Losing bd's push means losing anything else bd's push did.** #133 measured the output shape on one bead; bd may do something on push that was never observed. | medium | The three write paths are migrated together with fixture tests (3.4), and `hoist`/`land` semantics are explicitly held constant in 3.2. The prior behavior remains in git history for comparison. |
| R5 | **GitHub-only removes a `--backend` flag and a `BACKEND_AUTH` row.** | low | Softened at review (pass-1 upstream assessment): REQ-BUP-040, GR-BUP-004 and `spec/backends.md` REQ-BE-001 **already** state GitLab/Jira are unverified config-only stubs, so the *stated* capability was already zero. This deletes a stub surface rather than withdrawing support. 2.4/2.7 word it that way; 5.2a/5.2b reframe #51/#52/#53 rather than closing them. Residual: an existing `--backend gitlab` caller gets a hard argparse error — 5.1 must document the removal. |
| R6 | **Restrict-and-drop silently loses labels on future bead types.** Today the uncovered set is 3 beads (`chore` 2, `decision` 1, one P4); a new bead type would join it unnoticed. | medium | Accepted deliberately at review, after EXP-001's gap was corrected from ~45 beads to 3 (pass-1 C6). 2.2 specifies that a dropped label is **reported, not silent**, so the operator sees it on the push preview. Revisit if the uncovered set grows — the trigger is a report line, not a memory. |
| R7 | **Epic 4 was chained behind Epic 3 for review coherence, not necessity.** | low | **Resolved at review** (pass-1 C15): the `4.1 → 3.3` edge is cut. Epic 4 now depends only on 2.7 and runs in parallel with Epic 3, so the small high-value read-side fix is not hostage to the large write-side swap. |
| R8 | **This plan is large** — 5 epics, **19 issues**, touching **three** skills (`yf-beads-upstream`, `yf-plan`, `yf-beads-hygiene`), a hash-pinned protocol, and three spec files. | medium | Grew at review: pass-1 C3 added 2.6/2.7, C4 added 3.3, C15 split Epic 4 off the chain. The shape is falsify → specify → (implement ‖ close-the-loop) → document, with Epics 3 and 4 now parallel. Each epic has a distinct deliverable class, so a REVISE in one does not force rework in the others. |

## Success Criteria

| # | Criterion | Verification |
| :-- | :-- | :-- |
| SC1 | The unknown-label behavior is **measured**, not assumed | `references/gh-label-behavior.md` exists and records verbatim command output plus a verdict; Issue 2.2's policy cites it |
| SC2 | The field mapping is specified for the first time | `grep -c '^- \*\*REQ-BUP-' skills/yf-beads-upstream/SPEC.md` returns **≥ 36** (baseline **35**, measured at plan time — pass-1 C11: "increases" with no recorded baseline is not checkable), and the new REQ names `type::`, `priority::`, and `external_ref` |
| SC3 | No `bd <backend> push` remains anywhere | `grep -rn 'bd github push\|bd gitlab push\|<backend> push' skills/yf-beads-upstream/` returns only historical/prose references, and the 3.4 guard script exits `0` |
| SC4 | The `--backend` surface is gone **as a functional option** | `grep -c 'BACKEND_AUTH' skills/yf-beads-upstream/scripts/upstream.py` returns `0` (baseline 7 for the combined pattern), and no `add_argument("--backend"…)` remains in the argparse spec. **Deliberately not** a blanket `--backend` grep: SC14 requires detecting the literal flag in argv to emit a named error, which a blanket grep would forbid — the two were mutually unsatisfiable as first written (pass-2 D2) |
| SC5 | The hash-pinned protocol is re-stamped | `uv run skills/yf-beads-upstream/scripts/manifest_update.py skills/yf-beads-upstream/protocols --dry-run` reports `no changes (all hashes match)` — the positional is **required**; without it the command exits 2 (pass-2 D3), and `yf preflight yf-beads-upstream --json` returns `rule.outcome: ok`. (`--check` does not exist — the v1 draft's "(or equivalent)" hedge pushed the decision to execution on the criterion guarding R3, pass-1 C9.) |
| SC6 | Push is idempotent on `external_ref` | Fixture test: a bead with an `external_ref` produces an **update**, one without produces a **create** — the behavior `yf-uz5k`→#92 demonstrated |
| SC7 | Verification is structural, not textual | Fixture test asserts a create with no returned URL **fails closed**; no test parses `Pushed N issues` |
| SC8 | `closable` completes, and cannot silently regress | `references/closable-after.md` records a completion time on the live 991-bead repo; the 4.2 test asserts **one `bd list`** invocation and **zero per-bead `bd show`** invocations, independent of universe size (pass-1 C7 — "one `bd` invocation" is false: `upstream_enabled()` shells `bd config get`) |
| SC9 | Coarse trackers are visible to `closable` | After 4.3, a newly-filed plan tracker appears in `closable` output; after 4.4, at least one previously-invisible completed-plan tracker appears |
| SC10 | The new suite runs in CI | The gh-direct test id appears in **both** the `fast` and `full` tiers of `CHANGE-VALIDATION.md`. (The v1 draft also grepped for `check_prescriptive_push`, which **already passes today** and proves nothing — dropped, pass-1 C11.) |
| SC11 | The reframed issues are recorded and left open | #51/#52/#53/#111 each carry a plan-040 comment; `gh issue view <n> --json state -q .state` is `OPEN` for all four |
| SC11b | Every upstream write is drafted before it is published | `ls references/comment-51.md references/comment-52.md references/comment-53.md references/comment-111.md references/comment-132.md` all exist |
| SC12 | #132 is superseded, not silently dropped | #132 is closed with a comment stating the `--backend` surface was removed rather than the jira entry fixed |
| SC13 | The 20 already-mapped beads survive the swap | Issue 3.4 includes a **live-population** check: every existing `external_ref` value resolves to a form `gh issue edit` accepts, and a stale/deleted-issue ref fails closed with a named reason rather than creating a duplicate (pass-1 Missing) |
| SC14 | The removed `--backend` flag fails informatively | `uv run skills/yf-beads-upstream/scripts/upstream.py push --issues x --backend gitlab` exits non-zero with a message naming the removal and pointing at #51/#52/#53 — not a bare argparse error (pass-1 Missing) |
| SC15 | The `bd` version floor is stated | `skills/yf-beads-upstream/SPEC.md` records the minimum `bd` version for `bd update --external-ref` and for `bd list --all --json` returning `external_ref`; `context.md` marks 1.1.2 as a floor, not just an observation (pass-1 Missing) |
| SC16 | Epic 4's live evidence names which copy of the skill produced it | `references/closable-after.md` states whether the run used the repo copy or `~/.claude/skills/` — the divergence `context.md` itself flags, load-bearing for SC8/SC9 (pass-1 Missing) |
