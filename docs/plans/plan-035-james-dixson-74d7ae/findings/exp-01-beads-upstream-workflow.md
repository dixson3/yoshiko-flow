---
type: Finding
okf_spec: OKF-PLAN
---
## Finding: EXP-01 beads/upstream workflow reality (#97)

### Approach Tested

Read-only cross-reference of the beads config model, the upstream skill, the yf-plan
worktree execution model, and the web docs, then a live probe of this repo's git/beads
posture.

Sources read:

- `skills/yf-beads-init/SKILL.md:157-177` — local-only Dolt config (`bd config set
  dolt.local-only true`, keep `bd dolt remote list` empty, **never `bd dolt push`**);
  gitignore hardening at `:110-112` and canonicalization `git rm --cached` of the
  `.beads/` runtime set at `:125-131`.
- `skills/yf-beads-upstream/SKILL.md:84-98` — the three-mechanism table (`git push`
  vs `bd dolt push` vs the `gh` issue mirror) and the load-bearing line at `:96-98`:
  "yf beads is **always local-only** — interchange is this `gh` issue mirror (and, at
  most, local worktrees sharing one Dolt server), never a shared Dolt remote."
- `skills/yf-beads-upstream/SKILL.md:236-239, :345-367` — "upstream" = push **open +
  deferred** beads to an issue tracker; coarse per-plan granularity (`:224-229`);
  follow-on **hoist** with reversible `bd close -r` **tombstone** (`:463-467`).
- `skills/yf-beads-upstream/protocols/UPSTREAM_TRACKING.md:7-24, :36-50` — close-time
  push trigger + the "route every push through the skill, never a bare `bd <backend>
  sync`" safety invariant.
- `skills/yf-plan/SKILL.md:852-877` — the §5.3 **execution address-space model**: two
  address spaces, and the pinned invariant at `:863-864`: "all **`bd`** calls (INV-2:
  the shared Dolt DB lives in the primary's `.beads/` and is reached from anywhere)."
- `skills/yf-plan/scripts/plan_manager.py:1619-1626` (INV-1/INV-2 header),
  `:1795-1802` (`_bd_resolves_from` runtime probe), `:1830-1833`
  (`_worktree_viability`: "The primary must own the shared Dolt DB (INV-2): its
  `.beads/` is the parent the worktree resolves through **git-common-dir**").
- `AGENTS.md` "Memory" (bd-local `bd remember` is "absent from JSONL export, never
  synced upstream"; durable/cross-clone → AGENTS rule or a pushed bead) and "Upstream
  Tracking" (github · coarse · one tracking issue per plan-scale effort).
- GitHub issue #97 (`gh issue view 97`) — the exact question being tracked.
- Web grep: `grep -rn -iE "multiple environment|span|multi-node|multiple
  machine|across machines|share.*bead|push.*bead" web/content/`.

Live probe of this repo:

- `git ls-files .beads/` → **empty**: not one `.beads/` file is tracked. `git
  check-ignore .beads/embeddeddolt` → **ignored**. `git ls-files .beads/issues.jsonl`
  → **untracked**. So the DB genuinely never travels via git in this repo.
- `.beads/.gitignore` ignores `dolt/`, `embeddeddolt/` (via the engine top-up),
  `redirect` ("Must not be committed as paths would be wrong in other clones"),
  `push-state.json`/`sync-state.json`/`export-state/` (all commented "local-only,
  per-machine", "machine-specific and should not be shared across clones").

### Result

**The accurate workflow.**

1. **The bead DB is LOCAL to one repo clone.** It is a Dolt database under `.beads/`,
   configured local-only (`bd config set dolt.local-only true`,
   `beads-init/SKILL.md:157-161`) with **no Dolt remote**. The DB directory
   (`embeddeddolt/` / `dolt/`) is gitignored and `git rm --cached`-ed
   (`beads-init/SKILL.md:125-131`), so it is **never committed and never pushed via
   git**. Confirmed live: `git ls-files .beads/` is empty here.
   beads-concepts.md:113-117 already states this correctly: "yf **never pushes beads
   via git** as the way to share work. Two agents on two clones do not see each other's
   in-flight beads — and that is by design."

2. **The DB is shared ONLY across git worktrees of that same clone** — never across
   machines. This is INV-2: `plan_manager.py:1621-1622` — "the worktree shares the
   primary's single Dolt DB via **git-common-dir**"; `:1830-1833` — the primary owns
   the DB and the worktree resolves into it through git-common-dir; `:1795-1802`
   runtime-probes `bd list` from inside the worktree to confirm resolution.
   yf-plan §5.3 (`SKILL.md:863-864`) pins every `bd` call to that one shared DB
   "reached from anywhere" — but "anywhere" means any worktree of the one clone, on the
   one machine. The two address spaces are (a) the **primary** checkout (holds the
   `.beads/` DB + the plan folder) and (b) the disposable `.worktrees/<plan-id>`
   worktree (holds only the code the plan edits). Both live on the same filesystem.

3. **"Upstream" does NOT mean DB replication.** It is a `gh`/`glab`/Jira **issue-tracker
   mirror**, explicitly orthogonal to `bd dolt push`
   (`yf-beads-upstream/SKILL.md:84-98`; three-mechanism table). At land-the-plane the
   skill pushes **open + deferred** beads (blocked, descoped, discovered-but-not-done,
   follow-ups) to the tracker (`SKILL.md:236-239`), at **coarse** granularity — one
   tracking issue per plan-scale effort linking the plan + epic, **not** one issue per
   execution bead (`AGENTS.md` Upstream Tracking; `SKILL.md:224-229`;
   beads-concepts.md:119-126). Pushes are scoped, `--push-only`, `--dry-run`-first, and
   routed through the skill — never a bare `bd <backend> sync`
   (`UPSTREAM_TRACKING.md:47-49`).

4. **The capability-blocked → upstream-issue → re-hydrate flow.** A capability gate
   (`yf-plan/SKILL.md:385-390`) is a first-class bead that blocks the tasks needing a
   platform/capability the current machine lacks, while other work proceeds. When work
   must move to a capable machine, the transfer medium is **git-versioned artifacts +
   the coarse tracking issue**, NOT the bead DB:
   - the **plan folder** (`plan.md`, gates, epics-as-prose) is committed and `git
     push`ed — this is the durable, portable description of the work;
   - a **coarse GitHub issue** referencing that plan is filed at land-the-plane
     (`AGENTS.md`: precedent #13/#14/#16; issue #97 is itself this pattern — "the coarse
     upstream tracker for this thread", hoisted from local bead `yf-5p9x`).
   On the capable clone, the beads are **re-created locally** by re-pouring the plan's
   formula / re-executing yf-plan against the committed `plan.md` (yf-plan pours the
   molecule from the plan, `beads-concepts.md:87-90`) — i.e. bead state is **rehydrated
   from the plan + issue**, never copied from a shared DB. The local `bd remember`
   memory tier is explicitly excluded from any of this ("absent from JSONL export, never
   synced upstream", `AGENTS.md` Memory).

### The real capability & limitation

**What multi-environment ACTUALLY means today:** yf work is portable **because its
durable state is git-versioned files (the plan folder) plus a coarse issue-tracker
mirror**, not because bead state replicates. A second machine gets the *plan* (via `git
pull`) and the *tracking issue* (via the tracker) and reconstructs its own local beads.
Resumption "across sessions" is fully real **on the same clone** (the local Dolt DB
survives crash/new-session; the coordinator re-attaches the worktree and drains the
DAG). Resumption "across machines" is real only at the granularity of the committed
plan + the coarse upstream issue — the operator re-pours/re-executes locally.

**What it does NOT mean:** there is **no live, shared bead state across machines**. Two
clones do not see each other's in-flight beads, ready-frontier, claims, or gate
resolutions. Pushing the repo does **not** carry the bead DB (it is gitignored). The
`bd dolt push` mechanism that *could* replicate a Dolt DB is deliberately unused: yf
configures every repo local-only with no Dolt remote, and a stray remote actively wedges
bd 1.1.0's migration gate (`beads-init/SKILL.md:163-170`).

**Edge test — is there ANY real mechanism today for two machines to share LIVE bead
state? No.** The two candidate mechanisms both fail the "two machines" bar:

- `bd dolt push` / Dolt-remote replication — a genuine bd capability that *would* share
  the DB, but yf **never** enables it (local-only, no remote, never `bd dolt push`:
  `beads-init/SKILL.md:161`, `upstream/SKILL.md:92,96-98`). Not part of the model.
- Worktrees sharing one Dolt DB via git-common-dir (INV-2) — real and used, but it is
  **intra-clone / same-machine** (a shared on-disk parent `.beads/`), not cross-machine.

So the only cross-machine transfer is the git-committed plan folder + the coarse
GitHub issue; live bead state is re-created locally on each clone, never shared.

### Doc corrections needed (per file)

| web/ file | Misleading sentence (grep line) | Corrected framing |
|:--|:--|:--|
| `web/content/pages/why.md` | `:6` "real work rarely fits in one session on one machine. It spans days, environments, and people" | Keep as motivation, but ensure the body clarifies that yf achieves cross-environment portability via **git-versioned plan artifacts + a coarse upstream issue**, not shared live state. |
| `web/content/pages/why.md` | `:31-34` heading "Resumable across sessions and machines" + "Push the repo, and someone on the right platform … picks up exactly where the gate left off." | **Core inaccuracy.** Pushing the repo does **not** carry the beads (the DB is gitignored). Reword: pushing the repo carries the **plan folder**; a capable machine reconstructs the work by re-pouring/re-executing the plan locally, coordinated via the **coarse upstream tracking issue**. The gate is described in `plan.md`, not transferred as live bead state. Consider retitling to "Resumable across sessions (same clone) — and handed off across machines via the plan + upstream issue." |
| `web/content/pages/beads-concepts.md` | `:8` "so work survives a crash, a new session, or **a different machine**" | Split the claim: crash + new session survive via the **local** DB on the same clone; "a different machine" survives only via the git-committed plan folder + coarse upstream issue (re-hydrated locally), **not** via the bead DB. |
| `web/content/pages/architecture.md` | `:62` "Beads is the reason `/yf-plan` and `/yf-research` can span multiple **sessions**" | **Accurate — keep.** Multiple *sessions* on one clone is exactly what the local DB delivers. No change. |
| `web/content/pages/beads-concepts.md` | `:41` "span multiple sessions and recover cleanly" | **Accurate — keep.** |
| `web/content/pages/lifecycle.md` | `:71` "pushes **open + deferred** beads upstream to the issue tracker" | **Accurate — keep.** Correctly describes the `gh` issue mirror. |
| `web/content/pages/beads-concepts.md` | `:50, :113-133` "The DB is local / never pushes beads via git / upstream strategy / tombstone" | **Already accurate — keep as the canonical reference.** These sections are the correct model; the corrections above should be made *consistent with* this page. |

### Implications for Plan

- The fix is **documentation-only** in `web/` — no code or skill behavior is wrong. The
  implementation (local-only DB, worktree-shared via git-common-dir, `gh` issue mirror,
  tombstone hoist) is internally consistent and already correctly described on
  `beads-concepts.md`. The drift is confined to `why.md` and one line of
  `beads-concepts.md:8`.
- `beads-concepts.md` "The upstream strategy" section is the **source of truth** to
  reconcile the other pages against — cite it rather than re-authoring the model.
- Any edit to `web/content/` may fire `yf-drift-check` / `yf-markdown-lint` on their own
  axes; expect that and resolve in-pass.

### Recommendations

1. Reword `why.md:31-34` so "push the repo → someone picks up where the gate left off"
   is honest: the repo push carries the **plan**, and the capable machine **re-pours /
   re-executes** the plan's beads locally, coordinated through the coarse upstream issue
   — the live bead DB does not travel.
2. Qualify `beads-concepts.md:8`'s "a different machine" to distinguish local-DB
   resumption (same clone) from cross-machine handoff (plan folder + upstream issue).
3. Add one explicit sentence (best on `beads-concepts.md` "The DB is local", or a short
   note on `why.md`) stating plainly: **there is no live shared bead state across
   machines; `bd dolt push` is deliberately unused; cross-machine work moves via the
   git-committed plan + the coarse upstream issue.** This directly answers #97's "note
   on the real capability/limitation."
4. Leave the accurate claims (`architecture.md:62`, `beads-concepts.md:41`,
   `lifecycle.md:71`, `beads-concepts.md:113-142`) untouched.
5. Close #97 by referencing the corrected pages once landed.
