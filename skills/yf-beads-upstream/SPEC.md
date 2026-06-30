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

### 2.5 Backends & trigger split (see `spec/backends.md`)

- **REQ-BUP-040** *(testable)* GitHub shall be the only backend presented as tested; GitLab and
  Jira are config-only stubs and shall not be presented as verified.
- **REQ-BUP-041** *(testable)* the scoped-push translation shall reflect the real CLI:
  `--issues`/`--parent`/`--dry-run` are present on `bd github|gitlab|jira sync`; Jira diverges by
  using `--push`/`--pull` (not `--push-only`) and `--create-only`.
- **REQ-BUP-042** intent triggers (`init`, `status`/pull, "set up upstream tracking", "push
  beads upstream") shall live in the SKILL `description`; the procedural close-time /
  land-the-plane push trigger shall live **only** in the always-loaded companion rule, never in
  the description.
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

## 3. Interfaces

- **CLI / scripts:** `scripts/upstream.py` — `enumerate [--json]` (non-active push candidates via
  the shared active-set classifier, flagging those already carrying an `External:` mapping;
  defensive `--json` parse per `yf-beads-extra`), `mappings --issues <csv> [--json]` (report each
  bead's `External:` URL or null), `granularity`/`config [--json]` (report the
  `custom.upstream.granularity` and `custom.upstream.auto_hoist_followons` knobs),
  `followons --parent <id> --intake <ts> [--json]` (narrow vs broad follow-on detection),
  `hoist --issues <csv> --dest <d> [--apply]` (ensure issue per granularity → reversible
  `bd close -r`, dry-run-first), `land --parent <id> --intake <ts> --dest <d> [--apply]`
  (land-the-plane follow-on hoist; propose-with-confirm default), and
  `unhoist (--issues <csv> | --record <file>) [--apply]` (reopen from tombstone).
  `scripts/manifest_update.py` restamps the companion-rule manifest hash. Upstream pushes use bd's
  first-class `bd github|gitlab|jira push <ids>` (≡ scoped `sync --push-only`).
- **Companion rule:** `protocols/UPSTREAM_TRACKING.md` (+ `protocols/manifest.json`,
  sha256 + semver `1.0.0`) — the always-loaded close-time/land-the-plane trigger contract,
  carrying the silent-no-op-when-disabled clause and the safety invariant. After editing the
  rule, restamp via `manifest_update.py`.
- **Config / state:** beads config under `custom.upstream.*` (`enabled`, `backend`,
  `granularity` [coarse|granular, REQ-BUP-043], `auto_hoist_followons` [default-deny, REQ-BUP-044])
  and `github.*`/`gitlab.*`/`jira.*` (no token); `dolt.local-only`. Per-skill operator config moves to `.yf-beads-upstream.local.json`
  and runtime state to `.yf/yf-beads-upstream/` under the macro preflight kernel; legacy
  `.beads-upstream.local.json` / `.state/beads-upstream/` migrate via macro `REQ-YF-MIGRATE-001`.
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

## 6. References

- `skills/yf-beads-upstream/SKILL.md` (operations, backend table, safety invariants).
- `skills/yf-beads-upstream/spec/operations.md`, `spec/backends.md`, `spec/safety.md` (topical
  design docs; REQ-OP-*, REQ-BE-*, REQ-SAFE-* map into the requirements above).
- `protocols/UPSTREAM_TRACKING.md` + `protocols/manifest.json` (close-time trigger).
- Root `SPEC.md` §4 (BUP), §3.5 (`REQ-YF-PRE-*` preflight kernel), §3.8 (rename), §3.9
  (`REQ-YF-MIGRATE-001`), and `GUARDRAILS.md`.
