# SPEC — Beads Upstream (`yf-beads-upstream`)

> **Status: Active.** Per-skill SPEC for the upstream-tracking skill. The `yf-beads-upstream` rename is complete and the
> skill is shipped; this SPEC tracks the live behavior. Requirements use RFC-2119 "shall"; composed
> by the root `SPEC.md` macro spec.

## 1. Purpose & scope

`yf-beads-upstream` binds a beads workspace to an upstream issue tracker. As a land-the-plane
step it pushes **open + deferred** beads (blocked, descoped, discovered-but-not-done,
follow-ups) to GitHub/GitLab/Jira; on status/pull it treats upstream issues as the
authoritative worklist. GitHub is the implemented, dry-run-and-live-tested backend; GitLab and
Jira ship as config-only stubs sharing the same verb shape. It is a **utility skill** — no
formula, `bd mol pour`, or coordinator loop; the work is config plus scoped CLI calls.

**In scope:** `init` (backend config), the push step (scoped, idempotent upstream push), and
status/pull (upstream worklist), plus the always-loaded close-time trigger carried by the
companion rule.

**Out of scope:** routine local `bd` operations (the `beads` skill), direct-CLI `--json` gotchas
(`yf-beads-extra`), and authoring beads-backed skills (`yf-beads-authoring`).

## 2. Requirements (`REQ-BUP-NNN`)

### 2.1 Init (see `spec/operations.md` REQ-OP-001..003)

- **REQ-BUP-001** *(testable)* `init` shall detect the git remote, propose a backend
  (`github` from `github.com`, `gitlab` from `gitlab.*`, else `none`), confirm via
  `AskUserQuestion`, and persist the choice with `bd config set` (`custom.upstream.enabled`,
  `custom.upstream.backend`, and backend keys such as `github.owner`/`github.repo`).
- **REQ-BUP-002** *(testable)* selecting backend `none` shall write an explicit opted-out
  marker (`custom.upstream.enabled=false`, `custom.upstream.backend=none`) — not merely leave
  config unset — and re-running `init` shall be able to re-enable.
- **REQ-BUP-003** *(testable)* `init` shall write **no** rule file into the target project; the
  trigger contract ships only as the installed companion rule.
- **REQ-BUP-004** *(testable)* `init` shall not flip `dolt.local-only` to `true` without
  operator confirmation when a dolt remote is already configured (`bd dolt remote list` guard);
  it skips the flip entirely for backend `none`.

### 2.2 Push step (land-the-plane) (see `spec/operations.md` REQ-OP-004..007, REQ-OP-009)

- **REQ-BUP-010** *(testable)* the push step shall short-circuit to a clean exit 0 — no
  enumeration, prompt, or upstream call — when tracking is disabled
  (`custom.upstream.enabled=false` / backend `none`).
- **REQ-BUP-011** *(testable)* the step shall push only **open + deferred** work (status
  `open,blocked,deferred`); closed beads are never pushed; epics, molecules, and gates are
  excluded as non-work (`upstream.py` `CANDIDATE_STATUSES` + type filter).
- **REQ-BUP-012** *(testable)* the step shall verify the auth token resolves before any push and
  fail fast on an empty/expired token.
- **REQ-BUP-013** *(testable)* the step shall dry-run before the real push, and on a successful
  push bd shall record the upstream issue URL on each bead as a single `External:` line.
- **REQ-BUP-014** *(testable)* re-pushing an already-mapped bead shall **not** create a
  duplicate upstream issue — the recorded `External:` mapping suppresses re-creation and the
  re-push updates the mapped issue in place (verified bd 1.0.5: a second `bd github push <id>`
  kept the upstream issue count at 1; the dry-run reads `Would update`, not `Would create`).
- **REQ-BUP-015** *(testable)* on partial-push failure the step shall re-enumerate `External:`
  mappings (`upstream.py mappings`), report pushed-vs-remaining, and surface (never swallow) the
  error; recovery is a deliberate scoped re-push of the remaining set, never a bare sync.
- **REQ-BUP-016** *(testable)* content that must reach an already-mapped issue's body shall be
  folded into the bead's **`description`** (the only synced field — `notes`/`design` are not
  synced) and re-pushed; `bd show --json` is read as a list (`[0]`) before a read-modify-write,
  since `bd update --description` replaces rather than appends.

### 2.3 Status / pull (see `spec/operations.md` REQ-OP-008)

- **REQ-BUP-020** *(testable)* when tracking is enabled, status/pull shall treat the upstream
  tracker as the **authoritative** worklist (enumerate open upstream issues ordered by
  labels/priority); the local bead set is a convenience view.
- **REQ-BUP-021** *(testable)* when tracking is disabled, status/pull shall fall back to the
  local worklist (`bd ready`, then `bd list --status open`) with no upstream call.

### 2.4 Safety invariant (the non-negotiable; see `spec/safety.md` REQ-SAFE-001..002)

- **REQ-BUP-030** *(testable)* the skill shall **never** issue a bare `bd <backend> sync`. Every
  push shall be `--push-only` (Jira: `--push`) **and** scoped (`--issues <ids>` or
  `--parent <id>`), with `--dry-run` first. *(Also captured as guardrail GR-BUP-001.)*
- **REQ-BUP-031** *(testable)* auth tokens shall be passed inline at call time
  (`TOKEN=$(...) bd <backend> …`) and never written to config — no `bd config set *.token`.
  *(Also captured as guardrail GR-BUP-002.)*
- **REQ-BUP-032** *(testable, #57)* the companion rule's (`UPSTREAM_TRACKING.md`) close-time
  **Safety invariant** shall be **routing-primary**: the guardrail's operative instruction is to
  invoke `/yf-beads-upstream` (which performs the scoped, dry-run-first, inline-auth push of
  REQ-BUP-030/031), **not** a standalone hand-CLI recipe. The invariant's `--push-only` / scoped /
  `--dry-run` / inline-auth clauses shall be framed as **constraints the skill's push satisfies**
  (what `/yf-beads-upstream` guarantees), so that a raw `bd <backend> push --dry-run` typed by
  hand does **not** read as the compliant path — it bypasses the routing sentence that the
  invariant exists to protect. The observed failure this closes: an agent satisfying the guardrail
  with a raw `bd github push --dry-run` while skipping the invoke-the-skill routing. Verified by a
  rule-content check that the Safety invariant leads with the invoke-`/yf-beads-upstream` routing
  and does not present a bare `bd <backend>` push as the operator's action.

### 2.5 Backends & trigger split (see `spec/backends.md`)

- **REQ-BUP-040** *(testable)* GitHub shall be the only backend presented as tested; GitLab and
  Jira are config-only stubs and shall not be presented as verified.
- **REQ-BUP-041** *(testable)* the scoped-push translation shall reflect the real CLI:
  `--issues`/`--parent`/`--dry-run` are present on `bd github|gitlab|jira sync`; Jira diverges by
  using `--push`/`--pull` (not `--push-only`) and `--create-only`.
- **REQ-BUP-042** intent triggers (`init`, `status`/pull, "set up upstream tracking", "push
  beads upstream") shall live in the SKILL `description`; the procedural close-time /
  land-the-plane push trigger shall live **only** in the always-loaded companion rule, never in
  the description. **Mid-session intent (#61):** the description shall additionally fire on
  explicit mid-session phrasing — "push/sync upstream", "sync issues upstream", "mirror this bead
  upstream", "file/hoist this as a GitHub issue" — and shall **disambiguate this `gh`-based issue
  mirror from `bd dolt push`** (Dolt DB replication): the two are orthogonal paths and an agent
  must not reach for `bd dolt push` on "push upstream" intent. This mid-session trigger is distinct
  from the close-time land-the-plane trigger (which stays in the companion rule only).
- **REQ-BUP-043** *(implemented)* the granularity of upstream pushes shall be
  operator-configurable via `custom.upstream.granularity` (`coarse` | `granular`); unset or any
  unrecognized value defaults to `coarse`. Under `coarse` (the formalized existing default) one
  tracking issue is filed per plan-scale effort; under `granular` one issue is filed per hoisted
  bead. Read inspects the config text for the `(not set)` sentinel — never the exit code
  (false-negative invariant). `coarse` is the **tested happy path**; `granular` is implemented but
  not the tested-happy-path. The two coexist: flipping `coarse`→`granular` leaves existing coarse
  trackers intact, because hoist is create-or-map via the bd `External:` dedup mapping — already-
  mapped beads update their tracker in place rather than re-creating (`upstream.py` `granularity`,
  `hoist_issue_count`).
- **REQ-BUP-044** *(testable)* the unattended land-the-plane no-prompt hoist path shall be
  gated by `custom.upstream.auto_hoist_followons` (default-deny: enabled only on the literal
  string `true`; unset/empty/`false`/any other value resolves disabled, mirroring the
  `custom.upstream.enabled` short-circuit). When disabled, land-the-plane follow-on hoist is
  propose-with-confirm only (`upstream.py` `auto_hoist_followons`).
- **REQ-BUP-045** *(testable)* the `hoist` operation shall ensure an upstream issue per
  granularity (create-or-map via `External:`), **dry-run the push first** (REQ-BUP-013 /
  REQ-SAFE-001), then remove the bead locally with `bd close -r "<destination>"` — a reversible
  tombstone recording the upstream destination, **never** `bd delete`. Hoist honors the
  never-bare-sync (scoped `--issues`) and inline-auth invariants (`upstream.py` `plan_hoist`,
  `cmd_hoist`).
- **REQ-BUP-046** *(testable)* land-the-plane follow-on detection shall distinguish a **narrow**
  signal (a `discovered-from` edge into the plan subtree **AND** non-active status — auto-eligible)
  from a **broad** signal (created under the subtree after intake — gated-proposal-only, since it
  may catch a bead still being worked). The no-prompt path (REQ-BUP-044) is restricted to the
  narrow set; the broad set is never auto-hoisted (`upstream.py` `detect_followons`,
  `plan_land_hoist`).
- **REQ-BUP-047** *(testable)* a wrongly-hoisted bead shall be restorable via `un-hoist`:
  `bd update <id> --status open` reopens it from its `close_reason` tombstone (the upstream issue
  stays); a `--record` file supports batch round-trip (`upstream.py` `plan_unhoist`, `cmd_unhoist`).
- **REQ-BUP-048** *(testable, #61)* `enumerate` shall support an **owner-on-create** knob for repos
  where `bd create` auto-assigns an owner. Default-off (`custom.upstream.owner_on_create` resolves
  true only on the literal string `true`, mirroring REQ-BUP-043/044's `(not set)`-sentinel read).
  When **on**, enumerate shall not treat *owner alone* as the `claimed`/active signal — a bead that
  is `open` with an owner but is neither `in_progress` nor an ancestor of an `in_progress` bead is a
  valid push candidate, not active work. **The shared plan-013 active-set glossary
  (`_shared/active_set.py` `classify_active` / `ACTIVE_CLAIMED`) shall NOT change** (it stays
  byte-identical across its two consumers, `upstream.py` and `yf-beads-hygiene`): the knob is
  applied **locally in `enumerate_candidates`** by blanking the `owner` field on a copy of the
  bead universe before classification, so `in_progress` and ancestor-of-active propagation are
  preserved while owner-only "claims" fall through to candidacy. When **off** (default), enumerate
  behavior is byte-for-byte as before. *Why (#61):* in owner-on-create repos every open bead reads
  as claimed→active→excluded, so land-the-plane candidate discovery silently finds zero candidates.
- **REQ-BUP-049** *(testable, #105)* `enumerate` shall **never silently exclude** owner-claimed
  beads. When `owner_on_create` is **off** and at least one non-closed bead would be a candidate
  under `ignore_owner_claim=True` but is excluded under the effective setting, enumerate shall emit
  a warning naming the excluded **count** and the remedy
  (`custom.upstream.owner_on_create true`). The trigger is `excluded_owner_claimed > 0`, **not**
  `len(candidates) == 0` — a run may return a plausible non-zero candidate list while still
  dropping most of the universe, and that case must warn too. The warning goes to **stderr** in
  both human and `--json` modes, so `stdout` remains a pure JSON array for pipeline consumers and
  the signal survives a `| jq`. Detection reuses the REQ-BUP-048 mechanism — classify twice and
  diff the candidate sets — so the shared glossary still does not change. *Why (#105):* observed
  live in `dixson3/yoshiko-flow` — with `owner_on_create` unset and `bd` auto-assigning owners,
  enumerate reported `1 candidate(s)` while silently dropping ~36 open beads. A bare `0` at least
  invites suspicion; a plausible small non-zero does not, so a zero-keyed guard would not have
  fired. The silent path previously led to a hand-run `bd github push`, the exact anti-pattern
  GR-BUP-002 forbids.

### 2.6 Push-command construction, the `push` verb, and `closable` (plan-038)

- **REQ-BUP-050** *(testable, #129)* every emitted `bd <backend> push` command shall separate
  bead ids with **spaces** — they are positional arguments, not a comma-separated value. A
  comma-joined id list is matched by `bd` to **zero** beads while the process still **exits 0**
  (measured on bd 1.1.2: `bd github push yf-m78m yf-252c --dry-run` → `✓ Pushed 2 issues`;
  `bd github push yf-m78m,yf-252c --dry-run` → no `✓ Pushed` line, exit 0). Furthermore, any
  emitted sequence containing a **destructive follow-on stage** (`hoist`/`land`'s per-bead
  `bd close -r` tombstone) shall be **fail-closed**: the sequence shall **verify the push
  succeeded for the expected number of beads** before that stage runs, and shall **halt** —
  non-zero, with the destructive stage unexecuted — when the push is unverified. *Why:* without
  both halves, a multi-bead `hoist --apply` / `land --apply` tombstones every bead with a
  `close_reason` asserting an upstream hoist that never happened — silent data loss whose every
  visible step looks correct. Single-bead hoist was unaffected (a one-element join has no comma),
  which is why the defect survived.
  - **Verification-mechanism assumption (bd-version-dependent).** The fail-closed check is
    implemented by parsing the push command's output for bd's success line and the count it
    reports (the `Pushed N issues` shape measured on bd 1.1.2). This is an assumption about a
    **human-readable string emitted by a third-party binary**, not a stable API: a future `bd`
    release that rewords, re-cases, or restructures that line will break the check. It is
    recorded here so the breakage has a documented home. The failure mode is **safe by
    construction** — an unrecognized output parses as *unverified*, which halts the sequence
    rather than proceeding to the destructive stage. The parse is pinned by the REQ-BUP-050
    contract tests; re-verify it per bd binary alongside the §5 idempotency checkpoint.

- **REQ-BUP-051** *(testable, #106)* the skill shall expose a first-class **`push`** verb —
  `upstream.py push --issues <csv> [--apply]` — as **the** documented push path, so that
  following `SKILL.md` never requires hand-running a `bd <backend>` command (the action the
  companion rule's Safety invariant forbids). It shall: always emit the **dry-run push first**
  (REQ-BUP-013 / REQ-SAFE-001); be **scoped** via `--issues`, never a bare `sync`
  (REQ-BUP-030); use **inline auth** via `BACKEND_AUTH`, never config-persisted (REQ-BUP-031);
  construct ids space-separated and fail-closed per REQ-BUP-050; and match the existing
  `--apply`-only idiom — there is **no `--dry-run` flag**, because *absent `--apply` is the dry
  run* (as with `hoist`/`land`/`unhoist`). It is `plan_hoist` stages 1–2 **without** stage 3:
  a plain push leaves the bead **open and mirrored**, where `hoist` removes it locally with a
  reversible tombstone. `push` shall additionally surface the REQ-BUP-049 owner-claimed
  exclusion warning **inline in its own output** (#105 residual): the shipped warning is
  stderr-only, so an agent piping `--json` to `jq` misses it, and `push` is now the routed path.

- **REQ-BUP-052** *(testable, #117 partial)* the skill shall expose a **`closable`** verb
  proposing which upstream issues can be closed, on the **per-bead signal**: an issue is
  `closable` when **every** bead carrying an `External:` mapping to it is closed; any open
  mapped bead makes it `not-closable` with that bead named as the reason. It shall be
  **propose-only** — it emits the `gh issue close` commands for operator confirmation and
  **never closes anything itself** (closing an upstream issue is outward-facing and gets the
  same confirm contract as a push) — and shall honor the shared default-deny short-circuit
  (REQ-BUP-010): a clean exit 0 with no upstream call when tracking is disabled.
  - **Known gap (recorded, not fixed).** The per-bead signal is deliberately **zero-coupled** to
    `yf-plan`'s configurable `plans-root`, and the price is that it is **forward-looking only**.
    `yf-plan` §4.5 files coarse plan trackers with a direct `gh issue create`, so **no bead ever
    maps to them** and `closable` cannot see them. It would **not** have caught any of the four
    stale trackers (#103, #95, #96, #98) that motivated #117. The prose shall state this plainly
    so a clean `closable` run is never read as "nothing needs closing", and **#117 stays open**
    with the gap recorded. The zero-coupling remedy is `yf-plan`-side: stamping the coarse
    tracker URL onto the plan epic would make future trackers visible to this signal.

- **REQ-BUP-053** *(testable, #106)* the operator-facing **procedure** in `SKILL.md` shall not
  instruct a raw `bd <backend>` push, while **explanatory** and **invariant-stating** mentions
  are **expected and shall survive verbatim** — the Safety invariant quotes the command *in
  order to forbid it*, and the dated empirical verification blockquotes are provenance. The
  procedure/explanation boundary is defined **mechanically**, so the guardrail is checkable:
  **fenced ` ```bash ` blocks inside the Push step and Backend generalization sections are
  procedure**; all prose, tables, and blockquotes are explanation. A check asserting *zero*
  occurrences of `bd github push` anywhere in the skill is therefore **wrong by construction**
  and shall not be written — it would fail on the invariant statements themselves, pressuring a
  future editor into deleting the very rule this requirement enforces.
  *(Also captured as guardrail GR-BUP-005.)*

## 3. Interfaces

- **CLI / scripts:** `scripts/upstream.py` — `enumerate [--json]` (non-active push candidates via
  the shared active-set classifier, flagging those already carrying an `External:` mapping;
  defensive `--json` parse per `yf-beads-extra`; honors the `custom.upstream.owner_on_create` knob
  per REQ-BUP-048, applied locally without mutating the shared classifier), `mappings --issues <csv> [--json]` (report each
  bead's `External:` URL or null), `granularity`/`config [--json]` (report the
  `custom.upstream.granularity` and `custom.upstream.auto_hoist_followons` knobs),
  `followons --parent <id> --intake <ts> [--json]` (narrow vs broad follow-on detection),
  `hoist --issues <csv> --dest <d> [--apply]` (ensure issue per granularity → reversible
  `bd close -r`, dry-run-first), `land --parent <id> --intake <ts> --dest <d> [--apply]`
  (land-the-plane follow-on hoist; propose-with-confirm default), and
  `unhoist (--issues <csv> | --record <file>) [--apply]` (reopen from tombstone),
  `push --issues <csv> [--apply]` (**the** documented push path — dry-run first, scoped, inline
  auth, space-separated ids, fail-closed; REQ-BUP-050/051), and
  `closable [--json]` (propose-only upstream-issue closure on the per-bead `External:` signal;
  never closes — REQ-BUP-052).
  `scripts/manifest_update.py` restamps the companion-rule manifest hash. Upstream pushes use bd's
  first-class `bd github|gitlab|jira push <ids>` (≡ scoped `sync --push-only`).
- **Companion rule:** `protocols/UPSTREAM_TRACKING.md` (+ `protocols/manifest.json`,
  sha256 + semver, currently `1.3.0`) — the always-loaded close-time/land-the-plane trigger contract,
  carrying the silent-no-op-when-disabled clause and the safety invariant. After editing the
  rule, restamp via `manifest_update.py`.
- **Config / state:** beads config under `custom.upstream.*` (`enabled`, `backend`,
  `granularity` [coarse|granular, REQ-BUP-043], `auto_hoist_followons` [default-deny, REQ-BUP-044])
  and `github.*`/`gitlab.*`/`jira.*` (no token); `dolt.local-only`. Per-skill operator config moves to the canonical
  short-name `.yf/beads-upstream/config.local.json` (with the legacy root dotfile `.yf-beads-upstream.local.json`
  as a read-time fallback) and runtime state to `.yf/beads-upstream/` under the macro preflight kernel; legacy
  `.beads-upstream.local.json` / `.state/beads-upstream/` migrate to the canonical layout via macro
  `REQ-YF-MIGRATE-001` (`yf migrate`; preflight does not auto-migrate).
  Preflight/config moves to `yf` per macro `REQ-YF-PRE-*`.

## 4. Guardrails (`GR-BUP-NNN`)

- **GR-BUP-001** *Drift:* a bare `bd <backend> sync` to "just sync everything." *Rule:* never a
  bare sync — always `--push-only` (Jira `--push`) + scoped `--issues`/`--parent`, `--dry-run`
  first (REQ-BUP-030). *Why:* a bare sync re-imports every upstream issue as a duplicate bead
  **and** pushes the whole local DB (closed epics, gates, dupes) upstream.
- **GR-BUP-002** *Drift:* persisting a token to config for convenience. *Rule:* auth is
  inline-only, never `bd config set *.token` (REQ-BUP-031). *Why:* tokens must not land in a
  version-controlled config store.
- **GR-BUP-003** *Drift:* nagging an opted-out project. *Rule:* when disabled (`none`), push and
  status no-op cleanly and the close-time rule trigger is a silent no-op (REQ-BUP-010,
  REQ-BUP-021). *Why:* disabling is a supported configuration, not an error state.
- **GR-BUP-004** *Drift:* presenting GitLab/Jira as working. *Rule:* only GitHub is tested; the
  others are config-only stubs (REQ-BUP-040). *Why:* honesty about coverage.
- **GR-BUP-005** *Drift:* documenting a hand-run `bd <backend> push` **as the procedure**, so an
  operator or agent that follows `SKILL.md` faithfully violates the companion rule's never-hand-run
  Safety invariant. *Rule:* prescriptive steps route through `upstream.py push` (REQ-BUP-051);
  explanatory and invariant-stating mentions stay verbatim; the boundary is the mechanical one in
  REQ-BUP-053 (fenced ` ```bash ` blocks in the Push step and Backend generalization sections are
  procedure). *Why:* this is the observed #106 failure — the skill's own documented path was the
  non-compliant one, and it stayed that way because nothing checked it. The counter-drift is equally
  real: a global "zero occurrences" grep would delete the invariant statements, so the check is
  **scoped to fenced procedure blocks**, never global.
- **GR-BUP-006** *Drift:* trusting a `bd` push that exited 0, then running a destructive stage on
  it. *Rule:* verify the push matched the expected number of beads before any `bd close`; an
  unverified push **halts** the sequence (REQ-BUP-050). *Why:* `bd` exits 0 on a push that matched
  **zero** beads, so exit code alone is not evidence of a push — the same false-negative shape as
  the beads-init `bd status` invariant.
- **GR-BUP-007** *Drift:* a test that asserts an emitted command equals an expected string. *Rule:*
  emitted-command tests assert a **contract** (ids are space-separated; *no comma appears between
  ids*; the close stage does not run on an under-count) — never a restatement of what the code
  produces. *Why:* the pre-existing fixture tests compared emitted strings against expected strings
  containing the same comma defect, so a passing suite documented #129 rather than catching it.

## 5. Verification

- **REQ-BUP-011** is checked by `upstream.py enumerate` over a fixture bead set asserting only
  open/blocked/deferred non-container beads appear. **REQ-BUP-014** and the `External:` format
  were verified live on bd 1.0.5 against a throwaway repo (2026-06-01: re-push kept the upstream
  issue count at 1; 2026-06-07: `--description` carried content into the body, `--notes` did
  not) — these must be re-verified per binary before relied upon (push step §5 idempotency
  checkpoint). The never-bare-sync and inline-auth invariants (REQ-BUP-030/031) are asserted by
  grepping the skill for the absence of any bare `bd <backend> sync` and any `bd config set
  *.token`. GitLab/Jira are unverified and must be live-tested before REQ-BUP-014 is claimed for
  them. Each *(testable)* requirement maps to a plan-010 Epic 6 integration test naming the
  REQ id.
- **REQ-BUP-050** is checked by contract tests over `plan_hoist`/`plan_push` asserting the id
  segment of the emitted push command is space-separated and that **no comma appears between
  ids**, plus a test that the destructive close stage does **not** run when the push stage
  reports fewer than the expected count. These assert the contract, never the emitted string
  (GR-BUP-007). The `Pushed N issues` parse is a bd-version-dependent assumption recorded under
  REQ-BUP-050 and must be re-verified per bd binary.
- **REQ-BUP-051** is checked by contract tests: the dry-run command always precedes the real
  push; the emitted commands are scoped (`push <ids>`) and contain no bare `sync`; inline auth
  matches `BACKEND_AUTH` per backend; absent `--apply` executes nothing; and the REQ-BUP-049
  owner-claimed warning appears inline in `push` output. All `bd` interaction is faked.
- **REQ-BUP-052** is checked by fixture tests: all mapped beads closed → `closable`; any mapped
  bead open → `not-closable` naming it; an issue with no mapped bead is absent from the report;
  the disabled short-circuit is a clean no-op; and no `gh issue close` is ever executed. A
  caveat-survival test asserts the coarse-tracker limitation is still stated in `SKILL.md`.
- **REQ-BUP-053** is checked by the scoped acceptance check: no prescriptive raw `bd <backend>`
  push survives inside fenced ` ```bash ` blocks within the Push step and Backend generalization
  sections. It is **deliberately not** a global grep — prose, tables, and blockquotes are out of
  scope, and the check passes on the invariant statements and dated verification blockquotes.

## 6. References

- `skills/yf-beads-upstream/SKILL.md` (operations, backend table, safety invariants).
- `skills/yf-beads-upstream/spec/operations.md`, `spec/backends.md`, `spec/safety.md` (topical
  design docs; REQ-OP-*, REQ-BE-*, REQ-SAFE-* map into the requirements above).
- `protocols/UPSTREAM_TRACKING.md` + `protocols/manifest.json` (close-time trigger).
- Root `SPEC.md` §4 (BUP), §3.5 (`REQ-YF-PRE-*` preflight kernel), §3.8 (rename), §3.9
  (`REQ-YF-MIGRATE-001`), and `GUARDRAILS.md`.
