# SPEC — Beads Upstream (`yf-beads-upstream`)

> **Status: Active.** Per-skill SPEC for the upstream-tracking skill. The `yf-beads-upstream` rename is complete and the
> skill is shipped; this SPEC tracks the live behavior. Requirements use RFC-2119 "shall"; composed
> by the root `SPEC.md` macro spec.

## 1. Purpose & scope

`yf-beads-upstream` binds a beads workspace to an upstream issue tracker. As a land-the-plane
step it pushes **open + deferred** beads (blocked, descoped, discovered-but-not-done,
follow-ups) to **GitHub Issues**; on status/pull it treats upstream issues as the authoritative
worklist. Writes are **gh-direct** (REQ-BUP-057): `bd` reads bead content, `gh` writes the issue,
`bd update --external-ref` records the mapping. GitHub is the **only supported backend** — the
GitLab and Jira config-only stubs, and the `--backend` surface itself, were removed in plan-040
(REQ-BUP-040). It is a **utility skill** — no
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

- **REQ-BUP-030** *(testable, revised plan-040)* the skill shall **never** issue a bare
  `bd <backend> sync` — **and, under gh-direct (REQ-BUP-057), shall issue no `bd <backend>` write
  command at all.** `bd` is read-only on the write path: it supplies bead content and receives the
  `external_ref` write-back; `gh` performs every upstream mutation.

  **The invariant survives; its rationale changes.** It was written against a *destructive*
  mechanism — a bare `bd sync` re-imports every upstream issue as a duplicate bead **and** pushes
  the whole local DB upstream, so a single mistyped command could corrupt the local bead set. A
  raw `gh issue create` has no such blast radius: its worst case is one **unmapped duplicate
  issue**, which is untidy, not destructive. The prohibition therefore no longer rests on
  "prevent catastrophe".

  It rests instead on **routing**: `upstream.py` owns candidate enumeration, the `external_ref`
  create-vs-update decision, the REQ-BUP-056 label policy, and the fail-closed verification that
  guards the destructive follow-on stages of `hoist`/`land` (REQ-BUP-050). A hand-run `gh issue
  create` skips all four and, in particular, **writes no `external_ref`** — producing exactly the
  invisible, unmapped issue that #117/#131 exist to eliminate. Weaker consequence, same rule.

  *(Also captured as guardrail GR-BUP-001.)*
- **REQ-BUP-031** *(testable, revised plan-040)* the skill shall **never persist an auth token to
  config** — no `bd config set *.token`, and no token in any file the skill writes.

  **The auth model changes with the writer.** Under `bd <backend>` the skill had to supply the
  credential itself, inline at call time (`TOKEN=$(...) bd <backend> …`), because `bd` had no
  credential store of its own. Under gh-direct the writer is `gh`, which **owns its own
  authentication** (`gh auth login` / `gh auth status`). The skill therefore supplies **no token at
  all** on the write path: it invokes `gh` and lets `gh` resolve the credential.

  This is a **behavior and invariant change**, not a documentation detail — which is why it lands
  here in the requirements rather than in a later prose pass. The prohibition strengthens: the
  skill previously handled a token correctly, and now does not handle one at all. The remaining
  obligations are (a) never write a token to config, and (b) **verify auth resolves before any
  write** and fail fast if not (REQ-BUP-012, now satisfied by `gh auth status` rather than a token
  probe).

  `BACKEND_AUTH` — the per-backend token-variable table this requirement's inline form depended on
  — is deleted with the rest of the backend surface (REQ-BUP-040).
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

- **REQ-BUP-040** *(testable, revised plan-040)* GitHub shall be the **only supported backend**.
  GitLab and Jira are not merely "untested" — under gh-direct they are **removed from the
  surface**: the `--backend` flag and the `BACKEND_AUTH` table shall be deleted, and the write
  path shall be `gh`-only with no backend dispatch.

  **This deletes a stub surface; it does not withdraw support.** The prior wording already said
  GitLab and Jira were *unverified config-only stubs* (this requirement's own earlier text,
  `GR-BUP-004`, and `spec/backends.md` REQ-BE-001 all said so). The **stated** capability was
  therefore already zero — what existed was a flag implying a choice that led nowhere. Removing it
  makes the surface honest rather than smaller. Retaining a half-wired dispatch is exactly the
  two-mechanisms-with-different-conventions condition that produced #129.

  **Consequences, recorded rather than left to inference:**

  - **#132 is mooted, not fixed.** It reported that `BACKEND_AUTH` has no `jira` entry, so
    `--backend jira` emitted a `GITHUB_TOKEN`. Both the table and the flag cease to exist, so the
    broken entry ceases to exist along with them. The issue is closed as **superseded**, with that
    distinction stated — a reader who later finds #132 closed must not conclude the jira auth path
    was repaired.
  - **#51 / #52 / #53 are reframed, not rejected.** They stay **open**. After this change they
    mean *"add a backend to a gh-direct architecture"* — a clean feature against a single-mechanism
    write path — rather than *"finish wiring a half-present bd backend"*. That is a smaller and
    better-defined request than it was before.
  - **An existing `--backend gitlab` caller breaks.** It must fail **informatively**: a named
    error identifying the removal and pointing at #51/#52/#53, never a bare argparse
    unrecognized-argument error (REQ-BUP-059). Detecting the literal flag in argv in order to
    explain it is deliberate, and is why the acceptance check greps for `BACKEND_AUTH` and the
    `add_argument("--backend"…)` registration rather than for the string `--backend`.
- **REQ-BUP-041** *(superseded plan-040)* — the scoped-push **translation table is dead**. It
  existed to map a backend-generic push onto each backend's divergent `bd` sync flags (Jira's
  `--push`/`--pull`/`--create-only` versus GitHub/GitLab's `--push-only`). Under gh-direct
  (REQ-BUP-057) there is no `bd <backend>` sync call to translate and, per REQ-BUP-040, no backend
  to dispatch on.

  Retained as a superseded entry rather than deleted: the divergence it documents was **real and
  measured**, and a future "add a backend" (#51/#52/#53) will need to know that backend CLIs do not
  share a flag vocabulary. It is history, not a live requirement — nothing shall be implemented
  against it.
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
  **GR-BUP-001** forbids. *(Corrected plan-040: this line read `GR-BUP-002`, which is the
  token/inline-auth guardrail (REQ-BUP-031) and has nothing to do with hand-run pushes. #133
  inherited the same misnaming.)*

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

  **Revised plan-040 — the verb survives, its mechanism does not.** `push --issues <csv>
  [--apply]` remains **the** documented push path, and the `--apply`-only idiom is unchanged
  (absent `--apply` *is* the preview). What changes is everything underneath:

  | Clause as originally written | Under gh-direct |
  | :-- | :-- |
  | emit the dry-run `bd` push first | render the **preview locally** (REQ-BUP-057) — no round-trip |
  | scoped `--issues`, never a bare `sync` | no `bd <backend>` command at all (REQ-BUP-030) |
  | inline auth via `BACKEND_AUTH` | `gh` owns the credential; `BACKEND_AUTH` deleted (REQ-BUP-031/040) |
  | ids constructed space-separated | no id string is constructed — `gh` is called per bead |
  | fail-closed per REQ-BUP-050 | **unchanged in contract**, structural evidence (REQ-BUP-057) |

  The space-separated-ids clause is **retired as an implementation constraint** while REQ-BUP-050's
  *reason* for it stands: #129 arose from translating a comma-separated `--issues` into positional
  arguments, and gh-direct removes that translation entirely rather than performing it correctly.
  The one clause that must not be read as relaxed is **fail-closed** — `hoist`/`land` still have a
  destructive `bd close -r` stage, and it still must not run on an unverified write.

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
  - **Revised plan-040 — the gap is closed and the read is bulk.** Two amendments:
    1. **One `bd list`, no per-bead `bd show`.** `closable` shall source `external_ref` from the
       rows the single universe query already returns, and shall **not** issue a per-bead lookup.
       This is a correctness requirement, not a performance note: on this repo the shipped
       implementation issued **991 sequential `bd show` subprocesses** and produced **zero output
       in four minutes before being killed** — from an operator's seat, indistinguishable from a
       hang. A verb nobody can run proposes nothing. The invariant is **scale-independent**
       (exactly one universe query, zero per-bead queries), never a wall-clock threshold, so it
       cannot silently regress as the DB grows. The bound is on `bd list`/`bd show` specifically,
       **not** on total `bd` invocations: `upstream_enabled()` shells `bd config get`, which this
       requirement does not remove.
    2. **The coarse-tracker gap is discharged `yf-plan`-side.** `yf-plan` now stamps the tracker
       URL onto the plan epic as `external_ref` (`REQ-PLAN-073`), so coarse trackers become
       **ordinary mapped beads** and this verb sees them with no new signal, no `plan.md`-status
       reader, and no `plans-root` coupling in either direction. The "forward-looking only" caveat
       is **narrowed, not removed**: newly-stamped trackers are visible, pre-existing unstamped
       ones remain invisible until backfilled. `SKILL.md` shall still state plainly that a clean
       `closable` run is not proof nothing needs closing, because that stays true for any
       unstamped tracker.

- **REQ-BUP-059** *(testable, #132/#133)* the removed `--backend` flag shall fail
  **informatively**: an invocation carrying the literal flag shall exit non-zero with a message
  naming the removal, stating that GitHub is now the only supported backend, and pointing at
  #51/#52/#53 — **never** a bare argparse `unrecognized arguments` error.

  Detecting the flag in `argv` in order to explain it is deliberate, and is why the acceptance
  check greps for the deleted per-backend auth table and for an argparse registration of the flag
  rather than for the bare string `--backend`: a blanket grep would forbid the very code that makes
  the removal legible. As first written those two criteria were mutually unsatisfiable (pass-2 D2).

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

### 2.7 The bead→issue field mapping and the `bd` version floor (plan-040)

- **REQ-BUP-054** *(testable, #133)* the bead→issue **field mapping** shall be specified here
  rather than inferred from observed output. Under gh-direct (REQ-BUP-057) the skill constructs
  the issue itself, so the mapping is a contract it owns, not a behavior it inherits:

  | Bead field | Issue field | Rule |
  | :-- | :-- | :-- |
  | `title` | title | **verbatim**, no prefix or id decoration |
  | `description` | body | **verbatim**; the only synced body source (REQ-BUP-016) |
  | `issue_type` | label `type::<t>` | one label, lowercased type name |
  | `priority` | label `priority::<level>` | per the numeric→word table below |
  | bead labels | labels | passed through unchanged, alongside the two derived labels |
  | *(the issue's URL)* | → bead `external_ref` | **written back** after a successful create |

  The **priority numeric→word table**, stated explicitly because only three of its rows have ever
  existed as labels:

  | `priority` | Label | Exists in `dixson3/yoshiko-flow` |
  | :-: | :-- | :-- |
  | 0 | `priority::critical` | no |
  | 1 | `priority::high` | yes |
  | 2 | `priority::medium` | yes |
  | 3 | `priority::low` | yes |
  | 4 | `priority::backlog` | no |

  P0 and P4 are the **unmapped rows**: no such label exists, so under the REQ-BUP-056
  restrict-and-drop policy a P0 or P4 bead is pushed with its priority label **dropped and
  reported**. Naming the labels here does not create them.

  **Not synced, and intended:** `notes` and `design` do **not** reach the issue body. This is the
  REQ-BUP-016 contract, restated as a mapping row rather than left implicit — content that must
  reach an issue body is folded into `description`. It remains intended: `notes` is a scratch
  field with no upstream audience, and syncing it would make every local annotation an outward
  push. There is **no bead-id backreference in the issue body** — `external_ref` on the bead is
  the entire link, in one direction (measured, below).

  *Provenance.* The mapping had never been written down anywhere in this repo (plan-040 EXP-001:
  no match for `type::` / `priority::` in `upstream.py`, `SKILL.md`, or `SPEC.md`; `upstream.py`
  never constructs a label). It is reverse-engineered from **two** independent measured samples —
  bead `yf-1656`→#132, and the plan-040 Issue 1.1 scratch push `yf-nzdv`→#139 (a `chore`/P2 bead
  rendering as exactly `type::chore` + `priority::medium`, body verbatim, no assignee, labels
  created at `color: ededed` with empty description). Two samples are a corroborated sample, **not
  a proof of completeness** — plan-040 risk R2 records that a field present on neither sample could
  still be missed, which is why the §5 fixture tests pin each mapped field individually.

- **REQ-BUP-055** *(assertion, not a measurement)* the skill shall record **bd 1.1.2** as its
  version floor for the two `external_ref` capabilities it now depends on: `bd update
  --external-ref <url>` (writing the mapping) and `bd list --all --json` carrying `external_ref`
  (reading it in bulk, REQ-BUP-058).

  **This is a floor because it is the only version verified, not because 1.1.1 was shown to
  fail.** Both capabilities were confirmed present on bd 1.1.2 (`bd update --help` lists
  `--external-ref string`; `bd list --all --json` returned 21 of 1019 beads carrying a non-empty
  `external_ref`). No older binary was available to bisect against, and bd ships no changelog the
  probe could read. The claim is therefore an **assertion labelled as one** — a consumer on an
  older bd may well work, and a consumer that does not will fail against a stated floor rather
  than a silent assumption.

  **Serialization caveat (measured, load-bearing for REQ-BUP-058).** `external_ref` is emitted
  **omitempty**: the key is *absent* from rows that have no mapping, not present-and-null. A
  bulk reader shall therefore use a defaulting read (`row.get("external_ref")`), never
  `row["external_ref"]` and never a key-presence test — on this repo the key is missing from the
  first row and from 998 of 1019 rows.

  - **Amendment (plan-058, #268) — the floor extends to `dependencies[]`.** REQ-BUP-071 makes
    `collect_parent_edges` and `detect_followons` read dependency edges from the rows
    `bd list --all --json` already returns, so the floor now covers a **third** capability:
    `bd list --all --json` (and `bd list --parent <pid> --all --json`) carrying a
    **`dependencies[]`** array whose elements expose **`depends_on_id`** and **`type`**.

    **Recorded as an assertion, not a measurement, exactly as the parent requirement is.** The
    version actually verified is **bd 1.2.2** (`bd version` → `bd version 1.2.2 (Homebrew)`), on
    which `bd list --all --json` returned rows whose `dependencies[]` elements carry the keys
    `created_at, created_by, depends_on_id, issue_id, metadata, type`. No older binary was
    available to bisect against, so 1.2.2 is **the version verified, not the version below which
    it breaks**.

    **Reconciliation with the 1.1.2 floor above.** The two do not conflict and the floor is not
    raised to 1.2.2 for the whole skill: 1.1.2 remains the floor for the `external_ref`
    capabilities, and 1.2.2 is the version at which the `dependencies[]` capability was verified.
    A consumer on a bd between the two may well have both; nothing here establishes that it does
    not. Stating one floor per capability is what keeps each claim as strong as its evidence.

    **The same `omitempty` caveat applies, and it means the OPPOSITE of truncation.** The
    `dependencies` key is *absent* from rows with no dependency edges — measured, missing from
    **138 of 1,905** rows on this repository (the plan recorded 122 of 1,801 when it was drafted;
    the universe grew, the proportion did not move). An absent key means **no dependencies**, not
    a truncated or partial response. A bulk reader shall therefore use a defaulting read
    (`row.get("dependencies") or []`), never `row["dependencies"]` and never a key-presence test
    treated as an error signal.

    **The target-id field name differs BY SOURCE, and both must keep being handled.** `bd show`
    embeds the full target bead and carries the id as **`id`**; `bd list`'s `dependencies[]` uses
    **`depends_on_id`**. The `depends_on_id or id or target` chain in `collect_parent_edges` is
    what makes the function source-agnostic and shall not be narrowed to whichever field the
    current source happens to emit.

- **REQ-BUP-056** *(testable, #133)* the missing-label policy shall be **restrict-and-drop**: on a
  write, the skill shall emit only labels that **already exist** in the target repo, and shall
  **skip** any label that does not. It shall **never create a label**.

  **A dropped label shall be reported, not silent.** Each drop appears on the push preview as a
  line naming **the bead** and **the skipped label** — e.g.
  `yf-abcd: dropping label 'type::decision' (does not exist upstream)`. The report is not a
  courtesy: it is the sole producer of the signal guardrail **GR-BUP-008** relies on. A policy
  that dropped labels silently would have no revisit trigger at all, and the uncovered set could
  grow without anyone noticing.

  **This is a deliberate divergence from `bd`, not parity — measured, not assumed.** plan-040
  Issue 1.1 falsified both halves of the premise behind a scratch-write capability gate:

  | Probe | Result |
  | :-- | :-- |
  | `gh issue create --label <nonexistent>` | **fails**, exit 1, **atomically** — no issue created |
  | `bd github push` on a bead of an unmapped type | **creates the label on demand** |

  So `bd`'s behavior *was* ensure-label-before-use, and gh-direct deliberately declines to match
  it. The reason is proportionality, and the numbers are the argument: `CONTAINER_TYPES = {epic,
  molecule, gate}` means `candidate_filter` already drops those from the push path, so the 42
  `molecule` and 182 `epic` beads were never candidates. The genuinely uncovered population is
  `chore` (2), `decision` (1), and one P4 bead — **3 of 991**. Ensure-label-before-use would buy
  labels on 0.3% of beads at the cost of taking **label-write token scope** the skill otherwise
  never needs, plus an API call per unseen label. Restrict-and-drop needs **no token-scope clause
  at all**, because it writes no labels.

  **Stated exception, rather than left implicit.** An explicit `hoist --issues <epic-id>` bypasses
  `candidate_filter`, so epics *can* reach the write path. `type::epic` already exists, so that
  case stays covered — but it is covered by luck of the existing label set, not by the filter.

  **Failure shape.** Because `gh` rejects an unknown label *before* creating the issue
  (REQ-BUP-054 provenance), a drop that was wrongly skipped would surface as a hard create
  failure, never as a half-created issue. There is no compensating-delete path to specify.

  - **Amendment (plan-058, #268) — a FAILED READ is not an ABSENT LABEL.** The drop report above
    is only as true as the label list it is computed against. `existing_labels()` currently
    renders a **failed read** of the repo's label set identically to a successful read that
    returned nothing — so every label is reported as
    `dropping label 'X' (does not exist upstream)`, which is **untrue**: nothing was established
    about whether `X` exists.

    The requirement is amended so the reporting distinguishes the two. On a failed label read the
    skill shall report the read failure as such and shall **not** assert that any label is absent
    upstream. The three states — *label absent* / *label present* / *label set UNKNOWN* — are
    distinct, and collapsing the third into the first is the same silent-absence class REQ-BUP-063
    rejects for an unparseable `external_ref` and REQ-BUP-064 rejects for an unresolvable one.

    **Pre-existing, but in scope here because REQ-BUP-072 adds a new route into it**: a bounded
    `run` makes a *timeout* a second way for that read to fail, so the false report becomes
    reachable by a path this plan creates. It also matters to **GR-BUP-008** directly — the
    guardrail's revisit trigger *is* that report line, so a line that fires on a read failure
    inflates the very number the guardrail watches.

- **GR-BUP-008** *Drift:* the uncovered-label set grows past the three beads that justified
  restrict-and-drop, and nobody notices because the drops are silent. *Rule:* every dropped label
  is reported on the push preview naming the bead and the label (REQ-BUP-056); **the revisit
  trigger is that report line, not anyone's memory**. *Why:* the policy was chosen on a measured
  population of 3 of 991. That ratio is the whole argument, and it is not self-maintaining — a new
  bead type joins the uncovered set the moment it is introduced. Restrict-and-drop is a decision
  contingent on a number, so the number must stay visible.

- **REQ-BUP-057** *(testable, #133)* upstream writes shall be **gh-direct**: `bd` reads bead
  content, `gh` writes the issue, and `bd update --external-ref <url>` records the mapping. The
  core is a single `create_or_update(bead)` keyed on `external_ref`:

  | `external_ref` | Action | Mapping write |
  | :-- | :-- | :-- |
  | present | `gh issue edit <ref>` | none — already mapped |
  | absent | `gh issue create` | `bd update <id> --external-ref <url>` |

  **`external_ref` is the entire mapping — there is no sync table.** This is the measured fact the
  whole design rests on (#133 Measurement 1): bead `yf-uz5k` was mapped to #92 **by hand**, `bd`
  had never pushed it, and `bd github push --dry-run` nonetheless reported *"Would **update**"*.
  The create-vs-update decision was always driven by that one field, so moving the writer from
  `bd` to `gh` changes who writes the issue and nothing about how duplicates are prevented.
  Idempotency on `external_ref` is what prevents duplicates (REQ-BUP-014 is preserved verbatim in
  contract, only its implementation moves).

  **Preview replaces dry-run, and is rendered locally.** Absent `--apply` the skill shall render
  the **exact planned actions** — per issue: create-vs-update, the resolved title, body, and label
  set, and any REQ-BUP-056 label drops. This is a **local** rendering, not a round-trip: the
  previous mechanism asked `bd` to ask GitHub what it *would* do. Removing that call removes a
  network dependency from the preview path and makes the preview readable without credentials.

  **Verification shall be structural, not textual.** Success is evidenced by a **returned issue
  URL** on a create and a **success status** on an edit — never by scraping a human-readable
  success line. A create that returns no parseable URL shall **fail closed**.

  *Why this is a correctness fix, not a tidying.* REQ-BUP-050 recorded the `Pushed N issues` parse
  as a bd-version-dependent assumption about a third-party binary's human-readable output.
  plan-040 Issue 1.1 measured something worse: **`bd github push --dry-run` also prints
  `✓ Pushed 1 issues`** — the success string is emitted when nothing was pushed at all. A parser
  keyed on it cannot distinguish a real push from a dry run by that line alone. REQ-BUP-050's
  fail-closed **contract is preserved unchanged**; only its **evidence** changes, from a scraped
  string to a structured return.

- **REQ-BUP-060** *(testable, #142)* upstream state shall be resolved via **one bulk query**
  (`gh issue list --state all --json number,state`) rather than a per-issue round trip. A mapped
  ref **absent from the bulk result** is `UNRESOLVABLE` at **zero extra cost** — a deleted issue
  and a typo'd ref are indistinguishable by this signal and shall both classify that way.
- **REQ-BUP-061** *(testable, #144)* the skill shall expose a **`reconcile`** verb proposing
  `bd close -r "<upstream #N closed>"` for each non-closed bead whose upstream issue is CLOSED.
  Its authority is **asymmetric by design**: the **local** half is `--apply`-able (a `bd close -r`
  tombstone is reversible, as is `unhoist`), while the **upstream** half remains **propose-only,
  with no `--apply`** (`REQ-BUP-052` and the always-loaded safety invariant). Closing an upstream
  issue is outward-facing and keeps the same confirmation a push requires.
- **REQ-BUP-062** *(testable)* `external_ref` shall be **normalized to an issue number at the read
  boundary**, so the URL-only reader and the any-string reader **agree** on every input. Two
  readers disagreeing about what a ref means is the defect: a bead written `"gh-91"` is mapped by
  one and invisible to the other, so it is silently omitted from exactly the sweep meant to catch
  it.
- **REQ-BUP-063** *(testable)* an **unparseable** `external_ref` shall be **reported**, never
  silently dropped. A ref the tooling cannot interpret is a finding for a human, not an absence.
- **REQ-BUP-064** *(testable)* the skill shall **never auto-close a bead on an `UNRESOLVABLE`
  ref**, and a `gh` failure shall yield **`INCONCLUSIVE`** — never a falsely-clean proposal. This
  is the load-bearing asymmetry of a verb whose proposal requires a **network read** (unlike
  `push`, whose preview is local): when the read fails, the correct output is "I could not tell",
  because an empty proposal is indistinguishable from "nothing to do" and reads as success.

### 2.8 Hoist-tombstone suppression and evidence-bearing close-out (plan-052)

- **REQ-BUP-070** *(testable, #205)* `closable` shall **not** propose closing an upstream issue
  whose only closed mapped beads are **hoist tombstones**. The follow-on hoist closes a bead
  locally with a reversible `bd close -r` tombstone precisely **because the work moved
  upstream and is still open there**; counting that closure as evidence of completion inverts
  its meaning, so REQ-BUP-052's per-bead signal reads a hoisted issue as fully discharged at
  the exact moment it became least discharged.

  The suppressed row shall be **ANNOTATED, never dropped**. A dropped row is
  indistinguishable from "no such issue", which is the same silent-absence failure
  REQ-BUP-064 rejects for an unresolvable ref; an annotated `not-closable` row naming the
  tombstone tells the operator *why*.

- **REQ-BUP-070a** *(testable)* `closable` shall accept a **`--fixture <path>`** flag reading a
  pinned JSON bead snapshot in place of live `bd` state. It does not exist today — `closable
  --help` shows `[-h] [--json]` only — and without it every control over this verb is written
  against live machine state, which is not a control at all. An **absent** fixture file is
  **exit 1** (a real negative); a present-but-**malformed** one is **exit 2** (the instrument
  failed).

- **REQ-BUP-070b** *(testable)* **every** proposal `closable` emits shall render its mapped
  beads, each bead's **`close_reason`**, **and the plan Success Criteria those beads
  discharge**. A present-but-**empty** key does not discharge this requirement — an empty
  `close_reasons` array renders as "evidence supplied" while supplying none, which is the
  silent-green class this requirement exists to close.
  Rationale: #205. A close-out proposal is an outward-facing recommendation the operator is
  asked to authorize; without the reasons and the discharged criteria it asks for consent to a
  claim whose evidence lives somewhere the operator would have to reconstruct by hand.
  Verification: `ctl-205-tombstone` asserts no close proposal is emitted for an issue whose only
  closed beads are hoist tombstones; `ctl-205-fixture-flag` asserts `--fixture` EXISTS;
  `ctl-205-promote` asserts the `plan-relations` R1/R2a promotion binds at the CLOSE-OUT binding
  only, leaving authoring-time severity unchanged. Each is driven against a **pinned fixture
  snapshot**, never live `bd` state, and each RED is a **real negative (exit 1)** — never an
  argparse exit 2 from the not-yet-existing flag.


### 2.9 The no-per-bead-subprocess invariant (plan-058, #268)

> **Living amendment log — plan-058 (#268).** Four SPEC changes landed ahead of implementation,
> in plan order:
>
> | Change | Requirement | What it records |
> | :-- | :-- | :-- |
> | 0.1 | **REQ-BUP-071** *(new)* | generalizes REQ-BUP-052 amendment 1 from `closable` to every verb; names the three live call sites |
> | 0.1b | **REQ-BUP-055** *(amended)* | extends the bd version floor to `bd list`'s `dependencies[]`; records bd 1.2.2 as the version *verified*, one floor per capability |
> | 0.2 | **REQ-BUP-072** *(new)* | every subprocess bounded, inside the primitive; four timeout sub-clauses; states it does **not** close #268 |
> | 0.3 | **REQ-BUP-073** *(new)* | mechanical enforcement with paired controls, because the prose prohibition already failed here |
>
> A fifth change amends **REQ-BUP-056** (below) for the `existing_labels()` false report that
> Epic 2 adds a new route into.

- **REQ-BUP-071** *(testable, #268)* **no verb shall resolve a per-row field with a per-bead
  subprocess when the bulk query already carries it.** Where a `bd list` already returns a field
  on every row, the skill shall read it from that row; it shall **not** spawn a `bd show`, a
  second `bd list`, or a `bd dep list` per bead to obtain the same value.

  This **generalizes REQ-BUP-052's amendment 1** rather than inventing an unrelated requirement.
  That amendment stated the invariant for exactly one verb (`closable`), and the generalization is
  not speculative: the identical defect was already live at **three** other call sites in the same
  file when this requirement was written —

  | Call site | Per-bead subprocess | Bulk source that already carries the field |
  | :-- | :-- | :-- |
  | parent-edge collection (`collect_parent_edges` → `deps_for_show`) | `bd show <id> --json` per bead | `bd list --all --json` rows carry `dependencies[]` |
  | `cmd_enumerate`'s `external_ref` loop | `external_for(bid)` → `bd show <id> --json` per bead | the same rows carry `external_ref` (`external_from_row`) |
  | `detect_followons`' dependency loop (`cmd_followons`, `cmd_land`) | `bd dep list <id> --json` per subtree bead | `bd list --parent <pid> --all --json` rows carry `dependencies[]` |

  The first of these walked the **entire closed universe** — 1,801 beads on this repository, a
  measured **334 s** for a command whose useful output was an empty list — on the path
  `UPSTREAM_TRACKING.md` **mandates** for every upstream write. That is the correctness claim, not
  a performance note: a verb nobody can run within an operator's patience performs no writes, and
  the rule forbids the hand-run alternative.

  **The invariant is scale-independent, never a wall-clock threshold** (REQ-BUP-052 amendment 1's
  own formulation): the count of `bd` subprocesses a verb issues shall not grow with the size of
  the bead universe. A wall-clock bound would silently regress as the DB grows; a call-count
  bound cannot.

  **The claim is bounded to `bd list` / `bd show` / `bd dep list` specifically**, and deliberately
  **not** to total `bd` invocations. `upstream_enabled()` shells `bd config get`, which this
  requirement does not remove and does not forbid.

  **What this requirement does NOT assert.** It does not claim the three sites above are the
  complete set. REQ-BUP-073 exists precisely because a prose prohibition of this shape has already
  failed once here: `external_for`'s docstring carries the explicit words *"NEVER call this in a
  loop over the whole universe"*, and `cmd_enumerate` called it in a loop over the whole universe
  anyway.


- **REQ-BUP-072** *(testable, #268)* **every subprocess spawn shall be bounded.** No call into
  `subprocess.run` shall be made without a timeout, and the bound shall be resolved **inside the
  spawning primitive** — not passed at each call site.

  **Resolving it inside the primitive is a measured constraint, not a style preference.** Passing
  `timeout=` at call sites fails three existing tests whose `run` stubs take a single positional
  argument, and `apply_write`'s broad exception handler then masks the resulting `TypeError` as a
  `gh` failure — converting a wiring error into a false report about the upstream service.
  Bounding inside the primitive passes the suite unchanged.

  Four sub-clauses, each of which is a distinct failure mode:

  1. **A timeout shall raise a DIAGNOSABLE error naming the command and the bound.** A bare
     `TimeoutExpired` traceback names neither, and the operator's next question is always which
     command and how long it waited.

  2. **A timeout on a WRITE path shall be treated as UNVERIFIED and shall halt before any
     destructive stage.** This is REQ-BUP-050's fail-closed contract reached by a new route: a
     timed-out `gh issue create` may or may not have created the issue, so it is exactly the
     unverified-write case, and the `bd close -r` tombstone stage must not run behind it.

  3. **A timeout on a CONFIG READ shall never be reported as "upstream tracking disabled."** The
     default-deny short-circuit (REQ-BUP-010) makes an empty config read indistinguishable from a
     deliberate opt-out, so a transient `bd` hiccup would silently convert a **mandated** upstream
     write into a success-shaped no-op. The verb shall exit **non-zero** reporting the state as
     **UNDETERMINED**, naming the config read as the cause. The operator has no compliant
     fallback here — `UPSTREAM_TRACKING.md` forbids hand-running the underlying commands — so a
     silent no-op leaves them with no route at all.

  4. **A timeout shall not bypass an existing INCONCLUSIVE verdict.** `TimeoutExpired` is **not**
     an `OSError`, so a handler catching `OSError` to produce REQ-BUP-064's INCONCLUSIVE verdict
     does not catch it and emits a traceback instead. Bounded calls on that path shall wrap the
     timeout into the error type that path already handles.

  **This requirement does NOT close #268, and the SPEC states so rather than letting a reader
  infer it.** The #268 hang was 1,801 individually-*fast* subprocesses (0.186 s each); no
  defensible per-call bound trips on any of them. REQ-BUP-072 buys **diagnosability for the next
  unbounded call**. What closes #268 is REQ-BUP-071. An **aggregate** wall-clock deadline is a
  different mechanism from a per-call bound and is deliberately out of scope here.


- **REQ-BUP-073** *(testable, #268)* the REQ-BUP-071 invariant shall be enforced by a **mechanical
  check with a negative control**, not by prose.

  **The prose route has already been tried here and it failed.** `external_for`'s docstring
  carries the explicit prohibition *"NEVER call this in a loop over the whole universe"*, and
  `cmd_enumerate` called it in a loop over the whole universe anyway — in the same file, below
  the docstring stating the rule. REQ-BUP-052's amendment 1 likewise fixed the instance it was
  filed against (`closable`) without sweeping for siblings, leaving three. A requirement whose
  only enforcement is a sentence a future author must read is not enforced.

  The check shall satisfy four properties:

  1. **It shall match CONSTRUCTS, not text.** A token- or substring-scanner fails in **both**
     directions on this codebase, measured: the established `check_gh_direct.py` idiom blanks
     every `STRING` token before matching, so `run(["bd", "dep", "list", ...])` becomes
     `run([ , , , ])` and the needle can never fire (**under-match**); while a raw-source scan
     matches `edge_type()`'s **docstring**, making the check red on correctly-fixed code and
     leaving an executor no escape but deleting documentation the idiom's own design forbids
     erasing (**over-match**). An AST check is blind to comments and prose and sees the call.

  2. **It shall cover the HELPER-MEDIATED form.** Measured: neither `bd show` argv site is
     lexically inside a loop — both sit inside a helper that a loop calls. A rule matching only a
     literal argv inside a `for` would not have fired on the #268 defect, would not fire on its
     reintroduction, and would ship green over an unenforced invariant.

  3. **Every rule shall carry BOTH a negative and a positive control.** A **negative** control (a
     fixture containing the banned construct, asserted to exit non-zero) catches a rule that
     **cannot fire**. Only a **positive** control (the rule asserted green against the intended
     post-fix source) catches a rule that **fires on correct code** — the failure mode that makes
     a gate permanently unpassable. Two review cycles of this plan produced one failure of each
     kind, which is why neither control alone discharges this requirement.

  4. **No rule shall presuppose work sitting behind a human consent gate.** A rule that is red
     until a gated issue lands becomes permanently red if the operator legitimately **declines**,
     rendering that gate unpassable and the plan unclosable on a legal answer. Rules with such a
     precondition ship separately, downstream of the gated work.

  **Scope, stated rather than implied (R9).** The check matches a **fixed set of AST constructs**,
  not every possible N+1. It is not a completeness claim. It is strictly better than the prose
  prohibition that already failed, and that is the whole of what it asserts.


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
  `scripts/manifest_update.py` restamps the companion-rule manifest hash. Upstream **writes are gh-direct** —
  `gh issue create` / `gh issue edit`, with `bd update --external-ref` recording the mapping; no
  `bd <backend>` write command is issued (REQ-BUP-030/057).
- **Companion rule:** `protocols/UPSTREAM_TRACKING.md` (+ `protocols/manifest.json`,
  sha256 + semver, currently `1.5.0`) — the always-loaded close-time/land-the-plane trigger contract,
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

- **GR-BUP-001** *(revised plan-040)* *Drift:* reaching for a `bd <backend>` write — a bare `sync`
  to "just sync everything", or a hand-run `gh issue create` now that `gh` is the writer. *Rule:*
  the skill issues **no `bd <backend>` write command at all**, and every upstream mutation routes
  through `upstream.py` (REQ-BUP-030). *Why:* the original reason was **blast radius** — a bare
  sync re-imports every upstream issue as a duplicate bead and pushes the whole local DB (closed
  epics, gates, dupes) upstream. Under gh-direct that reason is gone: a stray `gh issue create`
  costs one unmapped duplicate. The rule stands on a **different** reason — a hand-run write skips
  enumeration, the `external_ref` create-vs-update decision, the label policy, and the fail-closed
  guard on `hoist`/`land`'s destructive stage, and above all **records no `external_ref`**, which
  is precisely the invisibility #117/#131 exist to remove. A guardrail whose rationale silently
  expires is worse than one that never existed, so the new rationale is stated rather than
  inherited.
- **GR-BUP-002** *(revised plan-040)* *Drift:* persisting a token to config for convenience — or,
  under gh-direct, re-introducing token handling the skill no longer needs. *Rule:* never
  `bd config set *.token`; the write path delegates authentication to `gh`'s own credential store
  and the skill handles **no token at all** (REQ-BUP-031). *Why:* tokens must not land in a
  version-controlled config store, and the safest way to not mishandle a credential is to never
  hold one.
- **GR-BUP-003** *Drift:* nagging an opted-out project. *Rule:* when disabled (`none`), push and
  status no-op cleanly and the close-time rule trigger is a silent no-op (REQ-BUP-010,
  REQ-BUP-021). *Why:* disabling is a supported configuration, not an error state.
- **GR-BUP-004** *(revised plan-040)* *Drift:* presenting GitLab/Jira as working — or, now,
  re-introducing a backend dispatch that implies a choice the write path cannot honor. *Rule:*
  GitHub is the only supported backend; there is no `--backend` flag and no `BACKEND_AUTH` table
  (REQ-BUP-040). *Why:* honesty about coverage. A flag offering three backends where one works is
  a less honest surface than no flag at all, and keeping two half-wired mechanisms side by side is
  the condition that produced #129.
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
  *.token`. (GitLab/Jira previously carried a "unverified, must be live-tested" caveat here; they
  were removed from the surface entirely in plan-040, so there is nothing left to claim
  REQ-BUP-014 for.) Each *(testable)* requirement maps to a plan-010 Epic 6 integration test naming the
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

- **REQ-BUP-070 / 070a / 070b** are checked by fixture tests over a pinned bead snapshot: an
  issue whose only closed mapped beads are hoist tombstones yields a `not-closable` row
  **annotated with the tombstone reason** rather than an absent row; `closable --help` lists
  `--fixture`; an absent fixture exits 1 and a malformed one exits 2; and every emitted proposal
  carries non-empty `close_reasons` and `discharges` arrays. No `gh issue close` is executed.

- **REQ-BUP-071 is checked** by call-count tests over a `_counting_run` fixture, never by a
  wall clock: `cmd_enumerate` and `push` issue **zero** `bd show` subprocesses, and the number of
  `bd list` calls each issues is **equal at 10 beads and at 1,000** — scale-independence asserted
  directly, in the idiom `test_closable_issues_one_bd_list_and_zero_bd_show` already established.
  The tests are **named explicitly** (`test_push_zero_bd_show`, `test_enumerate_zero_bd_show`,
  `test_enumerate_scale_independence`) because a bare `-k zero_bd_show` selector is already
  satisfied by the pre-existing `closable` test and would pass without the new work existing.
  `collect_parent_edges` additionally carries direct unit tests over rows-shaped fixtures —
  `dependencies` present, absent, and carrying a non-parent-child type — and a runtime cross-check
  asserts that rows carrying a non-empty `parent` with **zero** derived parent-child edges produce
  a loud warning **on stdout**, which is the failure shape a future `bd` dropping `dependencies[]`
  would otherwise take silently.
- **REQ-BUP-072 is checked** by tests that a bounded `run` on a deliberately-slow command raises
  an error **naming both the argv and the bound**; that `run_unchecked` yields
  `UpstreamQueryError` so `resolve_upstream_states` reports INCONCLUSIVE rather than a traceback;
  that a timed-out `_config_get` makes `cmd_push` exit **non-zero as UNDETERMINED** and never
  "disabled"; that `timeout_for` classifies `gh` as network and `bd`/`bash` as local; and — the
  fail-closed assertion — that `hoist --apply` with a timing-out create returns 1, prints that no
  bead was closed, and **never invokes `bd close` or `bash`**, asserted by trapping those stubs
  rather than by reading output.
- **REQ-BUP-073 is checked** by `test_check_no_universe_fanout.py`, which exercises **both**
  controls **rule for rule**: a **negative** control per rule (a fixture containing that rule's
  banned construct, asserted to exit non-zero) proving the rule can fire, and a **positive**
  control per rule (that rule asserted green against the intended post-fix source) proving it does
  not fire on correct code. Negative-only would admit a rule that is red on clean code; the check
  is additionally wired into the repo's FAST validation tier so it runs on every edit under
  `skills/yf-beads-upstream/scripts/`.

## 6. References

- `skills/yf-beads-upstream/SKILL.md` (operations, backend table, safety invariants).
- `skills/yf-beads-upstream/spec/operations.md`, `spec/backends.md`, `spec/safety.md` (topical
  design docs; REQ-OP-*, REQ-BE-*, REQ-SAFE-* map into the requirements above).
- `protocols/UPSTREAM_TRACKING.md` + `protocols/manifest.json` (close-time trigger).
- Root `SPEC.md` §4 (BUP), §3.5 (`REQ-YF-PRE-*` preflight kernel), §3.8 (rename), §3.9
  (`REQ-YF-MIGRATE-001`), and `GUARDRAILS.md`.
