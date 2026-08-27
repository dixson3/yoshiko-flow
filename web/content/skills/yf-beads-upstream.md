yf beads are always local-only: the bead database is gitignored and never travels with
the repo. `yf-beads-upstream` is how work outlives a single clone. It binds a beads
workspace to an issue tracker and owns three operations: `init` to configure the
backend, a **push step** that sends open and deferred beads upstream as a land-the-plane
action, and **status/pull**, which treats the upstream tracker as the authoritative
worklist. **GitHub is the only supported backend** — the GitLab and Jira config-only
stubs were removed in plan-040.

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
| **this skill** (`upstream.py push` / `hoist`) | selected beads, as tracker issues | the GitHub issue tracker |

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

**The skill handles no auth token at all.** Writes are `gh`-direct, and `gh` owns its own
credential store — so there is nothing to pass inline and nothing that could be persisted.
Never write a token to config.

## The push step

The land-the-plane push sends open and deferred beads — blocked, descoped,
discovered-but-not-done, follow-ups — upstream. Closed beads are never pushed. The
sequence is fixed:

1. **Disabled short-circuit** — check `custom.upstream.enabled`; exit 0 if not `true`.
2. **Enumerate candidates** — list open, blocked, and deferred beads not yet mapped.
3. **Preview, then apply** — `upstream.py push --issues <csv>` renders the planned
   create/update per issue **locally, with no network round-trip**; the absent `--apply`
   *is* the dry run. Re-run with `--apply` to perform it.
4. **The write is `gh`-direct** — `bd` reads bead content, **`gh` creates or edits the
   issue**, and `bd update --external-ref` records the mapping. `bd` is read-only on the
   write path.

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

- **Route every upstream write through the skill — never hand-run the underlying
  commands.** A raw `gh issue create` looks harmless, but it skips enumeration, the
  create-vs-update decision, and the label policy, and it **records no `external_ref`** —
  leaving an issue nothing can ever map back to a bead.
- **No `bd <backend>` write command is issued at all** — not a bare `sync`, not a scoped
  `push`. `bd` is read-only on the write path; `gh` performs every upstream mutation and
  `bd update --external-ref` records it. (The prohibition originally guarded against
  `bd <backend> sync`, which is *destructive* — a bare sync re-imports every upstream
  issue as a duplicate bead. That mechanism is gone; the routing rule survives on the
  weaker-but-still-real grounds above.)
- **The skill handles no auth token at all** — `gh` owns its credential store, so there is
  nothing to pass inline and nothing to persist.
- **An exit 0 is not proof of a write.** Success is a returned issue URL on create and a
  clean exit on edit — never a scraped success line. The old check parsed `Pushed N
  issues`, which `--dry-run` also printed, so it fired when **nothing** was pushed. The
  sequences are fail-closed: an unverified write halts before any destructive follow-on.
- **Only `description` syncs** — `bd update --description` replaces rather than
  appends, and `bd show --json` returns a list, so read and verify before you write.
- **Hoist removes reversibly** — `bd close -r`, never `bd delete`.
