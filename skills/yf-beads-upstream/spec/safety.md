# Spec: Safety invariants

Non-negotiable constraints. A change that violates one of these is a defect, not a trade-off.

## Requirements

- **REQ-SAFE-001 (revised plan-040):** The skill issues **no `bd <backend>` write command at all** —
  not a bare `sync`, not a scoped `push`. Writes are **gh-direct**: `bd` reads bead content, `gh`
  creates or edits the issue, `bd update --external-ref` records the mapping. Every write is scoped
  to an explicit bead set and **previewed first** (absent `--apply` renders the planned actions
  locally). — *Rationale:* **the rule outlived its original reason and is retained on a new one.**
  It was written against a *destructive* mechanism: a bare sync re-imports all upstream issues as
  duplicate beads and pushes the entire local DB upstream. A raw `gh issue create` has no such blast
  radius — its worst case is one unmapped duplicate issue. What still justifies the prohibition is
  **routing**: a hand-run write skips enumeration, the `external_ref` create-vs-update decision, the
  label policy, and the fail-closed guard on the destructive `hoist`/`land` close stage — and
  records **no `external_ref`**, producing exactly the invisible unmapped issue #117/#131 exist to
  eliminate. — *Verify:* SKILL.md Safety invariants § + Push step; protocols/UPSTREAM_TRACKING.md;
  SPEC.md REQ-BUP-030/057.

- **REQ-SAFE-002 (revised plan-040):** Auth tokens are **never written to config**, and under
  gh-direct the skill supplies **no token at all** on the write path — `gh` owns its own credential
  store (`gh auth login` / `gh auth status`). The pre-write check is `gh auth status`, not a token
  probe. — *Rationale:* tokens must not land in a version-controlled config store, and the surest
  way not to mishandle a credential is never to hold one. — *Verify:* SKILL.md init + Push step;
  absence of any `bd config set *.token` and of a `BACKEND_AUTH` table; SPEC.md REQ-BUP-031.

- **REQ-SAFE-003:** Re-pushing an already-mapped bead must not create a duplicate upstream issue;
  the recovery story depends on the recorded `External:` mapping suppressing re-push. — *Rationale:*
  partial-failure recovery re-runs the scoped push; it must be idempotent. — *Verify:* push step 5
  (verified live, bd 1.0.5: re-push kept upstream issue count at 1).

- **REQ-SAFE-004:** When tracking is disabled (`none`), the close-time rule trigger is a silent
  no-op — no enumeration, prompt, or upstream call. — *Rationale:* opted-out projects are never
  nagged. — *Verify:* protocols/UPSTREAM_TRACKING.md no-op clause; REQ-OP-004.

- **REQ-SAFE-005:** `init` does not flip `dolt.local-only` to `true` without operator confirmation
  when a dolt remote is already configured. — *Rationale:* the operator may run a dolt remote
  intentionally. — *Verify:* SKILL.md init step 4 (`bd dolt remote list` guard).

## Verification note

`External:` mapping format and idempotency (REQ-SAFE-003) were verified live on bd 1.0.5 against a
throwaway repo on 2026-06-01: `bd github push <id>` records `External: …/issues/N`; a second push
of the same bead left the upstream count at 1.

**Updated plan-040.** GitLab/Jira are no longer "unverified stubs to be live-tested" — they are
**removed from the surface** (REQ-BE-001), so there is nothing left to claim REQ-SAFE-003 for. The
idempotency contract itself is unchanged and now rests on `external_ref` directly: #133 measured
that the create-vs-update decision was **always** driven by that one field and never by a hidden
sync table — a bead mapped **by hand** to an issue `bd` had never pushed still read as
*"Would update"*. Moving the writer from `bd` to `gh` therefore does not change what prevents
duplicates.
