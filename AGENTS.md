# beads-skills

Beads-backed skills for Claude Code.

## Memory

Do NOT use Claude Code memory (`~/.claude/` memory directories). Two tiers:

- **Ephemeral / clone-local** → `bd remember "<insight>"`; recall with `bd memories <keyword>` / `bd recall`. Injected at `bd prime`. Project-DB-local: absent from JSONL export, never synced upstream. Never promote to durable or portable use.
- **Durable / cross-clone / behavioral** → an `AGENTS/` rule or a bead filed and pushed upstream. Anything another clone, machine, or harness must see goes here — not `bd remember`.

## Shell — this repo runs ZSH, not bash

`$SHELL` is `/bin/zsh` (5.9). Agent tool calls run under it. **Verify rather than assume** —
`echo "${ZSH_VERSION:-} ${BASH_VERSION:-}"` settles it in one line — because the difference below
is silent in both directions.

**The rule is to write constructs that behave IDENTICALLY in both shells, not to detect and
branch.** Detection yields two code paths where the inactive one is never exercised, and the
detection is itself a thing to get wrong. Know your shell to *read* a failure; write portably to
*prevent* one.

### The trap that has actually bitten (measured, plan-063)

**zsh does not word-split unquoted parameter expansions.** bash does.

```bash
m="a:1 b:2 c:3"
for x in $m; do ...; done     # bash: 3 iterations · zsh: ONE, x = the whole string
```

Under zsh the loop still runs, still exits 0, and the body still does something plausible with a
mangled value. Measured cost: a `bd update --external-ref` loop wrote **one** bead the **wrong**
issue url and skipped six. Exit code 0; caught only by reading the values back.

### Write it this way instead

| Instead of | Use |
| :-- | :-- |
| `for x in $var` over a built-up string | `printf '%s\n' "a 1" "b 2" \| while read -r k v; do …; done` |
| relying on `$(cmd)` splitting into words | `while IFS= read -r line; do …; done < <(cmd)` |
| `${arr[0]}` / bare `${#arr}` | avoid shell arrays entirely — indexing is 0-based in bash, **1-based in zsh** |
| a multi-step data transform in shell | a `python3 - <<'EOF'` heredoc |

Two more that differ and are worth knowing: `echo` flag handling is not portable — use `printf`;
and `setopt`/`shopt` are not interchangeable.

### Verify the effect, never the exit code

The failure mode above is **exit 0 with wrong data**, so a green exit proves nothing. Any loop
that writes — beads, files, upstream refs — must **read its writes back** and print what it
found. That is the same standard this repo applies to upstream writes (see Upstream Tracking:
"Verify a posted body by reading it back, not by trusting exit 0"); it applies to local shell
loops for exactly the same reason.

## SPEC-first

SPEC changes always happen **first**. Before implementing a behavior change, land (or stage
in the same change-set, ahead of code) the `SPEC.md` requirement — new `REQ-*` id, revised
wording, and living-amendment-log entry — then write code + a tagged test against it. Plans
sequence the SPEC edit before the implementation epics, never after. Rationale: the SPEC is
the source of truth the coverage gate enforces; implementation-first invites drift and
untagged requirements.

## Three artifacts, not one

Editing `skills/` does **not** change the skill this session is running. There are **three**
separate artifacts and they move independently:

| Artifact | What it is | When it changes |
| :-- | :-- | :-- |
| **Repo source** | `skills/<name>/` in this working tree | the moment you edit it |
| **Binary-embedded tree** | what `yf` carries (`rust-embed`, release builds) | on rebuild |
| **Session-installed skill** | what the running session resolved at invocation | on deploy, then next invocation |

The `SKILL_DIR` resolver is `yf skill-dir <name>` with a pure-bash fallback, and it searches
**every harness destination `yf` installs to** — `.claude/skills`, `.agents/skills`
(codex + agents), `.config/opencode/skills` and `.pi/agent/skills` under `$HOME`, their
project-scope equivalents under `$GIT_ROOT`, and the cwd-relative roots. **The repo's `skills/`
directory matches none of them** — it is unreachable by the resolver, not merely stale.

**The safety invariant that follows:** a plan or research project may freely rework the skill
it is executing under. `SKILL.md` prose, `agents/*.md` and `uv run ${SKILL_DIR}/scripts/*.py`
all resolve to the **installed** copy, so there is no self-modification hazard mid-run.

**The one real constraint: no `yf skills install` / `yf self install` mid-execution.** Deploy
at land-the-plane, after the work is merged and validated. The reason is narrow but
non-obvious: **`plan_manager.py` is re-invoked per call**, so a mid-execution deploy takes
effect in the *same* session for the scripts — unlike `SKILL.md` prose, which is loaded once at
invocation. A half-deployed session runs new scripts against old prose.

This is a **discoverability** note, not new policy: [TESTING.md](TESTING.md) has stated the
invariant since plan-021, but routed to it only "when developing deep/integration test plans or
test scripts" — a trigger that never fires for a planner reasoning about execution safety. See
TESTING.md for the Tier-1/Tier-2 strategy itself.

## Testing

When developing deep/integration test plans or test scripts for the **manager-script skills**
(`yf-plan` / `plan_manager.py`, `yf-research` / `research_manager.py`), follow the strategy in
[TESTING.md](TESTING.md): Tier-1 unit tests of the manager script, plus Tier-2 **mechanical
drive** of the modified skill under a sandboxed `HOME` (never trust the installed copy — it is
the old, `rust-embed`-baked skill). Do not hand-roll an interactive-agent smoke; drive the
manager verbs directly.

## Delegation to sub-agents

**The `Agent` tool is permitted — and preferred — for work that benefits from isolation from the
primary session's context.** Use it when independence is the point, not merely when the work is
large:

- **Adversarial review.** A red-team pass run by the main session is reviewing its own draft. It
  shares every assumption it is supposed to attack, so a concern the drafter cannot see is a
  concern the review cannot raise. Prefer an agent for `yf-plan`'s red-team and conformance passes.
- **Investigation.** `yf-plan` §2 experiments are designed to be able to **refute** the scoping
  decision that commissioned them. An investigator carrying the drafting conversation is primed
  toward confirming it.
- **Wide reads.** Sweeping many files to answer one question — the answer belongs in context, the
  file dumps do not.

Two constraints, both load-bearing:

- **Reviewers and investigators are read-only with respect to the repo** (REQ-AGENT-043). The agent
  returns findings; the **main session** writes `reviews/pass-N.md` and every other artifact.
- **A sandbox spike is explicitly authorized.** "Read-only" scopes the *repository under review* —
  it never forbade building something in `$(mktemp -d)` and running it. Prefer a spike whenever a
  claim is cheaper to *test* than to reason about; measured, plan-049's pass-4 spike caught a
  specification defect four prose-only passes had read past. Leave no residue.

Delegation is a judgement call, not a mandate: a single-fact lookup in a known file is faster
done directly.

## Syncing local `yf` to the repo

This repo is **both the source and a consumer** of its own skills. Editing `skills/` changes
nothing about the `yf` you are running until you rebuild and redeploy — they are separate
artifacts, and the gap used to be silent.

**Default land-the-plane step.** Once changes are pushed to `main`, sync local user scope with
**one** command:

```bash
yf self install --from-build --build   # rebuild, promote, and SYNC (skills + rules + config)
```

### Run it ONLY from local `main`, in sync with `origin`

**Preconditions, all three. Check them; do not assume them.**

```bash
git rev-parse --abbrev-ref HEAD          # must be `main` — NOT a worktree, NOT a plan branch
git status --porcelain                   # must be empty
git fetch origin && git rev-list --left-right --count origin/main...main   # must be `0	0`
```

The install **bakes whatever tree it builds into the binary** and deploys it to every detected
harness. So the binary is only ever as correct as the checkout it was built from, and the failure
is silent — a deployed skill tree that exists on no branch anyone can check out.

Each precondition rules out a distinct way to get that:

- **A worktree or plan branch** carries work that has not landed. Deploying from one installs a
  toolchain matching no published state; the next `main`-based install silently reverts it, and
  nothing records that either happened.
- **A dirty tree** bakes uncommitted edits. `yf --version` reports `-dirty`, but the *hash* still
  reads as the commit — so the stamp looks right while the tree is not.
- **`main` ahead of `origin`** deploys code no one else has. Behind, it deploys a tree already
  superseded. `--force` suppresses the staleness checks that would otherwise question either.

**`--force` does not make any of this safe — it removes the objections.** Add it only when a
re-deploy is genuinely intended and the three checks above already pass.

**Corollary for plan execution:** the redeploy is the **last** step of landing, after the merge to
`main` and after the FULL validation tier passes **on the merged tree**. A plan that redeploys from
its own execute branch has deployed something `main` does not contain.

**The three-step ritual is retired** (plan-042, #157). `yf self install --from-build` now runs
the **install-time sync** itself (`REQ-YF-SELF-005`): after promoting the binary it execs the
**freshly promoted** copy once per detected harness, deploying skills, the rules aggregate, and
— subject to the consent gate below — harness config. `yf self update` does the same on the
end-user path, through the same single implementation. The former steps 2 (`yf skills install`)
and 3 (`yf harness tune`) still work and remain the manual recovery path, but they are no longer
required, and their absence is no longer silent.

### The consent gate (read this before the first run)

The sync will **not** write harness config without explicit authorization. On a machine with no
config file — or when the change set touches an entry the harness profile declares
`consent_required: true` — it prints the **per-key delta** and refuses, exiting non-zero on the
sync alone while skills and the rules aggregate still deploy:

```bash
yf self install --from-build --build --allow-permissions-write   # authorize the config half
```

The gate exists because the claude-code profile applies `permissions.defaultMode:
"bypassPermissions"` and `skipDangerousModePermissionPrompt: true`, **creating** `settings.json`
where none exists. The same class of lever is `approval_policy = "never"` on codex and
`permission.* = "allow"` on opencode — which is why the predicate is **profile-declared**
(`consent_required`) rather than a `permissions.*` key-path match that would only ever have
caught claude-code.

`--allow-permissions-write` is **distinct from `--yes`**, which keeps its existing meaning
(bypass the multi-harness fan-out prompt) and never authorizes a config write.

**Rollback is asymmetric — do not assume "just revert".** `yf harness tune --revert` restores
**config** precisely: it is manifest-driven and per-key, with a touched-since-tune guard, and is
sound. The **rules aggregate** is a different story: per
[#154](https://github.com/dixson3/yoshiko-flow/issues/154), revert **deletes** `YOSHIKO_FLOW.md`
rather than restoring its pre-tune content. That is why the consent gate is the *primary*
control rather than a backstop.

### Opting out

- `--no-sync` on both commands skips the sync entirely (`--binary-only` is retained as a
  documented alias on `yf self update`).
- Under `CI` — or with `YF_NO_CONFIG_SYNC` — the **config half only** is suppressed, while
  skills and the rules aggregate still deploy. The consent gate cannot be satisfied on an
  unattended runner, so without this the sync would hard-fail there.

**One sanity check remains** — for a residue the sync does *not* cover:

```bash
yf --version   # git hash should equal HEAD (a `-dirty` suffix just means uncommitted files;
               # the hash itself is what must match)
```

`yf/build.rs` declares `cargo:rerun-if-changed=../skills` and `cargo:rerun-if-changed=.`, so an
incremental build observes additions under `skills/` and re-stamps the version on any change
under `yf/` or `skills/` (plan-041, #137). But `HEAD` moving for any *other* reason — a
docs-only commit, a `SPEC.md` commit, a `git checkout`, a rebase — touches nothing watched and
can still leave an incremental build carrying a stale hash. This one line is the only detector
for that case. Ordering caveat when reading it by hand: `git commit` moves `HEAD` without
touching a watched file, so a no-op rebuild legitimately shows the pre-commit hash.

**Why the #137 fix was needed** (measured): `skills/` sits outside the `yf/` package, and
`rust-embed` is a **proc macro** — it cannot emit `rerun-if-changed`, and its only staleness
signal is `include_bytes!` dep-info, which tracks file **content** but never **the directory
listing**. So an incremental release rebuild missed **additions** under `skills/` specifically —
content edits, deletes and renames always propagated correctly. A second, separate defect shared
the cause: `build.rs` never re-ran on a skills-only change, so the **version stamp** went stale
even when the embed was fresh.

Release bakes the tree at compile time; debug reads it from disk at runtime (the `embed-in-debug`
feature is opt-in), so `./target/debug/yf` is always current and `--release` is the exposed path.

**A bare `yf skills install` is still not a shortcut.** `yf` on `PATH` deploys whatever tree
*its* binary embeds, so running it without promoting a new binary first will quietly overwrite
newer skills with older ones. To deploy without promoting a binary, run
`./target/debug/yf skills install` explicitly — debug reads `skills/` from disk, so it is always
current.

## Upstream Tracking

- **Source / repo / tool:** github · `dixson3/yoshiko-flow` · `gh issue`
- **Granularity:** coarse (default). File ONE tracking issue per plan-scale effort (e.g. per `/yf-plan` plan), linking the plan + epic — NOT one per execution bead. At land-the-plane, create/update that single coarse issue; do NOT push granular sub-beads upstream unless explicitly asked. Precedent: #13 (plan-005), #14 (plan-006), #16 (plan-007).
- **Notes:** Issues filed against the published skill repo; this working directory (`beads-skills`) is the same codebase.
- **Composing bodies:** always `--body-file -` fed by a **quoted** heredoc (`<<'EOF'`), never
  `--body '...'`. Issue and PR bodies are markdown full of backticks and backslashes; a
  single-quoted `--body` passes backslashes through literally (`\`abc\`` renders as typed) and
  an unquoted one lets the shell expand `` ` `` and `$`. The heredoc form is the only one that
  survives both. Same rule for `gh issue comment` and `gh pr create`. Verify a posted body by
  reading it back (`gh issue view N --comments`), not by trusting exit 0.
