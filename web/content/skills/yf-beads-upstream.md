yf beads are always local-only: the bead database is gitignored and never travels with
the repo. `yf-beads-upstream` is how work outlives a single clone. It binds a beads
workspace to an issue tracker — GitHub, GitLab, or Jira — and owns three operations:
`init` to configure a backend, a **push step** that sends open and deferred beads
upstream as a land-the-plane action, and **status/pull**, which treats the upstream
tracker as the authoritative worklist. GitHub is fully implemented and dry-run-and-live
tested; GitLab and Jira ship as config-only stubs sharing the same verb shape.

Invoke it when you set up upstream tracking, when you want to push beads to the tracker
mid-session ("push open work to GitHub", "mirror this bead upstream"), or when you ask
for project status and tracking is configured. Routine local `bd` operations use the
canonical `beads` skill; direct-CLI scripting gotchas use
[`yf-beads-extra`](/skills/yf-beads-extra/).

## Three kinds of "push" — this is not `bd dolt push`

The word "push" is overloaded across three orthogonal mechanisms. On any "push/sync
upstream" intent, this skill's tracker-issue mirror is the target — never `bd dolt
push`.

| Mechanism | What it moves | Destination |
| :-------- | :------------ | :---------- |
| `git push` | repo content — code, docs, the plan folder | the git remote (`origin`) |
| `bd dolt push` | the Dolt DB itself (versioned bead replication) | a Dolt remote |
| **this skill** (`bd <backend> push` / `hoist`) | selected beads, as tracker issues | the GitHub/GitLab/Jira issue tracker |

The three are independent. A local-only repo holds no Dolt remote — a stray one wedges
`bd` 1.1.0's remote-migrate gate. So "push these upstream" means this skill's `gh`-based
issue mirror, and nothing else.

## Two triggers, two surfaces

The skill deliberately routes its triggers to two places. **Intent triggers** — `init`,
status/pull, and explicit mid-session push language — live in this skill's description,
because the user states the intent and description-matching catches it. The
**land-the-plane push** — pushing deferred work as a session closes — is not something
anyone phrases out loud, so it is bound by an always-loaded companion rule that is in
context every turn. All procedure lives in the skill; the rule carries only the
close-time trigger, one safety invariant, and a pointer here.

## Default-deny

Upstream is enabled only when `custom.upstream.enabled` is the literal string `true`.
Anything else — the key absent, empty, `false`, or `none` — resolves to disabled. So a
repo that never ran `init` fails closed, and every push or status call no-ops cleanly
with "upstream tracking disabled" and exit 0. No enumeration, no prompt, no upstream
call. Configuring `init` writes the backend keys; declining writes an explicit `none`
marker so the one-shot preflight offer stays silent forever.

Auth is always passed inline and never persisted:
`GITHUB_TOKEN=$(gh auth token) bd github …`.

## The push step

The land-the-plane push sends open and deferred beads — blocked, descoped,
discovered-but-not-done, follow-ups — upstream. Closed beads are never pushed. The
sequence is fixed:

1. **Disabled short-circuit** — check `custom.upstream.enabled`; exit 0 if not `true`.
2. **Auth pre-flight** — resolve the token before any push; fail fast if empty.
3. **Enumerate candidates** — list open, blocked, and deferred beads not yet mapped.
4. **Dry-run, then scoped push** — `bd github push <ids> --dry-run` to confirm the
   intended beads, then the real push. After success, `bd` records the new issue URL on
   each bead as a single `External:` line.

That `External:` mapping is what suppresses duplicate creation on re-push. A re-push of
an already-mapped bead updates its existing issue in place rather than creating a
second — verified live on `bd` 1.0.5. Only a bead's `description` field syncs to the
issue body; `notes` and `design` do not. Content that must reach the tracker goes in
`description`.

## Hoist, land, and un-hoist

At land-the-plane, follow-on beads created during the session can be **hoisted**
upstream and removed locally, so the local DB stays "active work only". Removal is a
reversible `bd close -r` tombstone recording the destination — never `bd delete`.

- **`land`** detects follow-ons under a plan subtree. It is **propose-with-confirm** by
  default: the whole batch is emitted as a proposal requiring one explicit
  confirmation. An unattended no-prompt path runs only when
  `custom.upstream.auto_hoist_followons` is `true`, and even then only for the narrow
  signal (`discovered-from` into the subtree and non-active). A bead still being worked
  is never auto-hoisted.
- **`hoist`** ensures an upstream issue for explicit beads per the configured
  granularity — `coarse` files one tracker per plan-scale effort, `granular` one per
  bead — then closes each locally.
- **`unhoist`** reopens a wrongly-hoisted bead from its tombstone; the upstream issue
  stays put.

## Status and pull

When tracking is enabled, the upstream tracker is the authoritative worklist and the
local bead set may be stale. Status enumerates open upstream issues ordered by label
and priority, and treats local beads as a convenience view over that list. When
tracking is disabled it falls back to the local worklist — `bd ready`, then
`bd list --status open` — with no upstream calls.

## Safety invariants

- **Never a bare `bd <backend> sync`.** A bare sync re-imports every upstream issue as
  a duplicate bead and pushes the entire local DB upstream. Always `--push-only`,
  scoped to `--issues` or `--parent`, and `--dry-run` first.
- **Auth is inline-only** — never written to config.
- **Only `description` syncs** — `bd update --description` replaces rather than
  appends, and `bd show --json` returns a list, so read and verify before you write.
- **Hoist removes reversibly** — `bd close -r`, never `bd delete`.
