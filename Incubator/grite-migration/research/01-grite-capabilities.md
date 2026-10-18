---
title: Grite capability inventory
created: 2026-10-18
tags: [grite, beads, research]
---

> Produced by an isolated research sub-agent (2026-10-18) against grite 0.5.3 /
> neul-labs/grite@33afee0, with a sandboxed smoke session. Unedited agent output follows.

# grite capability inventory for a beads replacement

Short answer: grite 0.5.3 covers a small part of what yf uses in beads. It has issues with title, body, labels, assignees, comments, URL links, attachments, three dependency types with cycle detection, a topological sort, a JSON envelope with exit codes, and lease locks. It has no issue types, no priority, only two states (open/closed), no "ready" query, no gates, no formulas/molecules/wisps, no custom metadata fields, no external-ref field, no tracker bridges, no import, and no MCP server. Your first impression was right on every point.

I also reproduced an open data-loss-style bug: a fresh clone pulls the WAL but rebuilds **0 events** and still reports success. Several documented commands don't match what the binary accepts. On correctness alone I would not treat 0.5.3 as a substrate for multi-agent work yet.

## Version and where the evidence comes from

- **Binary tested:** `grite 0.5.3` (output of `grite --version`), the prebuilt `grite-0.5.3-aarch64-apple-darwin.tar.gz` from the only GitHub release, v0.5.3 (2026-05-07).
- **Source read:** `github.com/neul-labs/grite` at `main` = `33afee09adda9e7e5be464e846bca800da56212c` (2026-07-02). Paths below are relative to that tree (`https://github.com/neul-labs/grite/blob/33afee0/<path>`).
- **Sandbox:** everything ran in a `mktemp -d` directory with `HOME` and `GIT_CONFIG_GLOBAL` pointed inside it. I ran `--help` on every subcommand and leaf, then a smoke session: a temp repo, a bare remote, a fresh clone, a worktree, a second actor, and a daemon start/stop. Afterwards I deleted the temp dir. No grite processes were left and nothing remained in `/tmp/grite*`. `git status` in yoshiko-flow is clean.
- **Repo facts** (from `gh api`): 23 stars, 4 forks, 8 open issues/PRs, MIT license, created 2026-01-13. crates.io lists `0.3.0@2026-01-26` and `0.5.3@2026-05-09` with 115 total downloads.

## 1. Storage model

- **Where data lives:** README: "Grite stores issues as an append-only event log inside git refs (`refs/grite/wal`)". Each actor also gets a sled database under `.git/grite/actors/<actor_id>/sled/`, with refs `refs/grite/snapshots/<ts>` and `refs/grite/locks/<resource_hash>` (README, "Storage Layout"). Smoke run: after the first create, `git for-each-ref refs/grite` showed `refs/grite/wal`, and the sled database was created at `.git/grite/sled` (shared, not per-actor; this matches merged PR #20, "shared sled model").
- **WAL format:** "Each append creates a new commit, parented to the current WAL head… `events/YYYY/MM/DD/<chunk>.bin`", stored as CBOR chunks (`docs/git-wal.md`).
- **Sync:** `grite sync [--pull|--push] [--remote origin]`. On a non-fast-forward push it fetches, re-parents the chunk, and pushes again (`docs/git-wal.md`, "Append algorithm"). Smoke run: `refs/grite/wal` and `refs/grite/locks/...` showed up on the bare remote.
- **Merge semantics:** title, body and state are "Last-writer-wins by `(ts, actor, event_id)`". Labels, assignees and dependencies are an "Add/remove set (commutative)" (`docs/data-model.md` l.216–221).
- **Concurrency:** the daemon uses `flock` (README, "Daemon"). Lock policy is `off|warn|require`, and the default is `warn: warn on conflicts, but continue` (`docs/locking.md`).
- **Worktrees:** README says "Each worktree gets its own actor database." **The smoke run contradicts this.** From a linked worktree, `actor current` returned the main checkout's actor (`d35b3b2b…`), and `actor list` showed one actor. Issue #27 reports the same thing: "Worktrees of one clone share a single actor identity, so leases cannot distinguish agents." `docs/agent-playbook.md` tells agents sharing a `.git` to use `--data-dir`/`--actor`/`GRITE_HOME` instead.
- **Working tree:** README says "Nothing is stored in tracked files (except `AGENTS.md`)". In practice:
  - `grite export` wrote `.grite/export.json` into the working tree.
  - `install-skill` wrote `.claude/skills/grite.md`.
  - `init` created `AGENTS.md`.
- **Fresh-clone recovery is broken.** I fetched the WAL into a fresh clone with `sync` ("Pulled 14 new events"). `issue list` then showed `total: 0`, and `grite rebuild --json` returned `{"ok":true,"event_count":0,...}`. This reproduces #26 ("Issues don't sync", open since 2026-08-03) and finding 3 in #27 ("`grite rebuild` reconstructs **0 events** from a WAL holding 67, while reporting `ok: true`").
- **Daemon reads lag writes:** #27 finding 2 reports 32 acknowledged comments with only 20–23 visible until `rebuild`. I did not reproduce this.

## 2. Issue model

From the event enum in `crates/libgrite-core/src/types/event.rs`: `IssueCreated{title, body, labels}`, `IssueUpdated{title, body}`, `CommentAdded`, `LabelAdded/Removed`, `StateChanged`, `LinkAdded{url, note}`, `AssigneeAdded/Removed`, `AttachmentAdded{name, sha256, mime}`, `DependencyAdded/Removed`, `ContextUpdated`, `ProjectContextUpdated{key, value}`.

| Aspect | Finding |
| :-- | :-- |
| States | `pub enum IssueState { Open, Closed }`. Nothing else: no in_progress, blocked or deferred. |
| Types | None (no type field). The docs use labels: `--label "epic"`, `--label "subtask"` (`documentation/docs/use-cases/ai-agents.md` l.272–273). |
| Priority | None. The playbook uses the label `priority:P0` (`docs/agent-playbook.md`). A source grep for `priority` matched only tree-sitter dedup code and config-precedence prose. |
| Labels | `issue create --label` can be repeated. Add/remove via `issue label add/remove --label`. |
| Assignees | `issue assignee add/remove --user` (free text). `create` has no assignee flag. |
| Comments | `issue comment --body`. Materialized views expose only `comment_count`; comment text appears only in the `events` array of `issue show`. |
| Body | Not included in the `issue list` or `issue show` summary objects. It appears only inside the `IssueCreated`/`IssueUpdated` events. `issue show` without `--json` also printed JSON. |
| Custom metadata | No per-issue key/value fields. The only key/value store is repo-level: `context set <KEY> <VALUE>`. |
| External refs | No field. The nearest equivalent is `issue link add --url --note`, which only appends. There is no link remove command (`issue link` has only `add`). |
| IDs | 128-bit random hex. Prefixes work (`issue show e8129991` resolved). |

## 3. Dependencies

- **Edge types:** `--type <TYPE> Dependency type: blocks, depends_on, related_to [default: depends_on]` (`issue dep add --help`). There is **no parent-child edge, no discovered-from, and no hierarchical IDs**. `docs/comparison.md` l.41 lists "Hierarchical IDs (epics/subtasks)" as an area where "Beads is ahead".
- **Cycle detection:** works. Adding the reverse `depends_on` edge returned `{"ok":false,"error":{"code":"invalid_args","message":"…would create a cycle in the depends_on graph"}}`, exit 2. The roadmap says "Cycle detection (DFS) for acyclic dependency types".
- **Ready query: none.** The closest command is `issue dep topo [--state] [--label]`, which sorts the issues topologically and does not filter out blocked ones. In the smoke run it returned all three open issues, including the one whose dependency was open. The AGENTS.md template maps "What should I work on next?" to `grite issue dep topo --state open`. A source grep found no `ready` implementation.
- **No enforcement:** `issue close` on an issue whose `depends_on` target was open succeeded (`ok: true`).
- **Inspection:** `dep list <ID> [--reverse]` works. In `issue show` events, dependency targets are serialized as **raw byte arrays** (`"target":[196,93,116,…]`), not hex.

## 4. Machine interface

- **Envelope:** `{"schema_version":1,"ok":…,"data"|"error":{code,message,details}}`. The error codes are documented as "(stable)" (`docs/cli-json.md`).
- **Exit codes:** documented as 0/1/2/3/4/5 (`docs/cli-json.md` l.44). Verified: not_found → 3, cycle → 2, lock conflict → 4, missing actor → 3.
- **Gaps I found:**
  - **The JSON shape depends on whether the daemon is running.** Through the auto-spawned daemon, `issue list --json` returned bare `{"issues":[…]}` with no `schema_version`/`ok`/`data` wrapper. With `--no-daemon`, it returned the full envelope.
  - **Invalid filter values are accepted silently.** `issue list --state bogus` (also `in_progress`, `blocked`) returned all issues with exit 0.
  - **`--label` cannot be repeated on `list`:** "the argument '--label <LABEL>' cannot be used multiple times". One label filter, no boolean logic.
  - **Documented commands that don't exist:**
    - README `grite issue update <id> --label bug` → "unexpected argument '--label'".
    - README `grite issue link <a> blocks <b>`: `link` only has `add --url`.
    - Playbook `lock acquire --resource … --ttl 15m` → "unexpected argument '--resource'". In the binary, the resource is positional and the TTL is in seconds.
    - README "Export… CSV": `export --format` accepts only `json, md`.
- **Bulk create:** none. No batch or stdin intake.
- **Query language:** none. The roadmap lists "Advanced queries (search, filters, saved views)" as future work.
- **Library API:** the `libgrite-cli` crate is a "programmatic API for all CLI operations" (CHANGELOG 0.5.0).

## 5. Equivalents of beads features

Where I looked: a case-insensitive word grep over `crates/` (source), `docs/`, `documentation/` and `README.md`, plus all `--help` output.

- **Gates** (await conditions, human approval, timers): **absent.** `gate` had 0 hits in source and docs. "approval" appears only as team-process prose ("Changes require approval from primary owner"), and "timer" only as the daemon idle timer.
- **Templates / formulas / molecules / wisps:** **absent.** `formula`, `molecule` and `wisp` had 0 hits. `template` matches only the AGENTS.md template constant (`crates/grite/src/agents_md.rs`).
- **Ephemeral issues:** **absent.** No source hits. The one docs hit is unrelated.
- **Epics:** **labels only.** No source hits; the docs use `--label epic`.
- **Memories:** **convention only.** "Store learnings… with `--label memory`" (README). The roadmap's `grite_memory_store`/`grite_memory_query` items are unchecked.
- **Hooks:** **absent.** The only mention is "An optional `pre-push` hook can enforce the same policy" (`docs/locking.md`); no hook ships.
- **Import:** **absent.** The roadmap lists "Import/Migration (from GitHub Issues, Jira, etc.)" as unchecked. There is no import subcommand.
- **Export:** `export --format json|md [--since]`, written to `.grite/export.json`. It is not JSONL.
- **GitHub/GitLab/Jira sync:** **absent.** "Grite does not currently bridge to external issue trackers" (`documentation/docs/guides/comparison.md` l.83). The roadmap item "Remote collaboration (GitHub/GitLab integration)" is unchecked.
- **Locks:** grite-specific. `lock acquire/release/renew/status/gc`, plus `--lock` on write commands. A conflict across distinct actors returned exit 4. Under the default `warn` policy, locks are advisory.

## 6. Agent integration

- **MCP server:** **absent.** The roadmap calls it "In Progress": "Milestone 7: MCP Server for Claude Code", with all tasks unchecked (`docs/roadmap.md` l.96–124). No `mcp` hits in source.
- **Prime / context injection:** **absent.** There is no `prime` command. The substitute is the static `AGENTS.md` section written by `init` (`--no-agents-md` to skip) and `install-skill [--global]`, which writes a flat `.claude/skills/grite.md`. Note that this is not the `<name>/SKILL.md` layout.
- **Daemon:** `grite-daemon` starts automatically on first use and shuts down after a 300s idle timeout. The socket is `/tmp/grite-daemon-<uid>.sock`. Open PRs #28 and #29 fix daemon liveness and git-dir detection.
- **Code context:** `context index/query/show/project/set`, a tree-sitter symbol index across 10 languages. beads has no equivalent.

## 7. Maturity

- **Activity:** 126 commits on `main` from 2 authors: Dipankar Sarkar (68) and Jonathan Hult (58). Monthly commits in 2026: Jan 9, Feb 1, Mar 10, Apr 4, May 8, Jun 2, Jul 1. The last commit is docs-only (2026-07-02). Nothing has been committed for about 3.5 months.
- **Releases:** one GitHub release (v0.5.3). Two versions on crates.io.
- **CHANGELOG quality:**
  - The `[0.5.1]` header appears twice.
  - There are no entries for 0.4.x, 0.5.2 or 0.5.3.
  - Entries for 0.1.0–0.3.0 are dated 2025, but the repo was created 2026-01-13.
- **Breaking-change history:**
  - The project was renamed from "grit" to "grite" (PR #9).
  - The IPC transport changed from nng to tokio sockets (#14).
  - The storage layout moved to a shared sled (#20).
  - The hash algorithm changed to BLAKE2b (CHANGELOG 0.3.0).
- **Open issues:**
  - #27: multi-agent fleet unusable (shared actor identity, stale daemon reads, fresh-clone rebuild returns 0 events).
  - #26: fresh clone shows no issues. The reporter "ended up switching away".
  - #1: Homebrew install broken.
- **Open PRs:** #28–#30 (daemon/IPC/lock-ref sync fixes), #23, #24.

## Gaps vs beads

| beads feature | grite equivalent | notes |
| :-- | :-- | :-- |
| Dolt DB + JSONL export | git-ref WAL + sled cache | Fresh-clone rebuild returns 0 events (#26/#27; reproduced) |
| `bd ready` | none (`issue dep topo` = order only) | Blocked issues still listed; yf would need to compute readiness from `dep list` |
| Issue types (task/bug/epic/gate…) | labels | Not validated or enforced |
| Priority 0–4 | label convention (`priority:P0`) | Not sortable; one label filter per query |
| Statuses (open/in_progress/blocked/deferred/closed) | `open`, `closed` only | `--state` accepts any value without error |
| `--claim` / assignee | `assignee add`; `lock acquire issue:<id>` | No atomic claim; default lock policy is `warn` |
| parent-child, discovered-from deps | none (`blocks`, `depends_on`, `related_to`) | No hierarchy; would have to use labels or `related_to` |
| Cycle detection | yes (DFS, exit 2) | Equivalent |
| Dependency-enforced close | not enforced | Close succeeded with an open dependency |
| Gates (human/timer/await) | none | Not found in source, docs or help |
| Formulas / `bd mol pour` / wisps | none | Not found; yf would have to implement templating itself |
| Ephemeral issues | none | — |
| Metadata / custom fields | none per issue; repo-level `context set` only | yf agent metadata has nowhere to go except the body or labels |
| `--external-ref` | `link add --url` (append-only, no remove) | Mapping would be a link convention |
| `bd remember` / memories | label `memory` convention | Syncs everywhere; no clone-local memory tier |
| `bd prime` | static AGENTS.md / `install-skill` | No dynamic context injection |
| `bd batch` bulk create | none | One process per write |
| `--json` | envelope with documented exit codes | Bare JSON (no envelope) via the daemon; body/comments only in `events`; dep targets as byte arrays |
| GitHub/GitLab/Jira/Linear sync | none (roadmap) | yf-beads-upstream's gh-direct path would still work |
| Import (JSONL) | none (roadmap) | Migration needs a custom replay through the CLI or `libgrite-cli` |
| MCP server | none (roadmap, "In Progress") | — |
| Hooks | none (prose mention only) | — |
| Multi-clone / worktree | CRDT merge; worktrees share one actor | Contradicts README; `--actor`/`--data-dir` required per agent |
| Locks / leases | `lock` subcommand, TTL leases in refs | Not in beads; advisory by default |
| Code symbol index | `context index/query` | Not in beads |
| Maturity | 23 stars, 2 authors, 1 release, idle since 2026-07 | Documentation and binary disagree in several places |

For migration design, the features yf depends on most (`bd ready`, gates, `mol pour`, metadata, external refs, typed hierarchy) would all have to be rebuilt in yf on top of labels, bodies and links. The fresh-clone bug would also need to be fixed upstream first.
