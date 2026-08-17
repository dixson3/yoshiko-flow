# beads-skills

Beads-backed skills for Claude Code.

## Memory

Do NOT use Claude Code memory (`~/.claude/` memory directories). Two tiers:

- **Ephemeral / clone-local** → `bd remember "<insight>"`; recall with `bd memories <keyword>` / `bd recall`. Injected at `bd prime`. Project-DB-local: absent from JSONL export, never synced upstream. Never promote to durable or portable use.
- **Durable / cross-clone / behavioral** → an `AGENTS/` rule or a bead filed and pushed upstream. Anything another clone, machine, or harness must see goes here — not `bd remember`.

## SPEC-first

SPEC changes always happen **first**. Before implementing a behavior change, land (or stage
in the same change-set, ahead of code) the `SPEC.md` requirement — new `REQ-*` id, revised
wording, and living-amendment-log entry — then write code + a tagged test against it. Plans
sequence the SPEC edit before the implementation epics, never after. Rationale: the SPEC is
the source of truth the coverage gate enforces; implementation-first invites drift and
untagged requirements.

## Testing

When developing deep/integration test plans or test scripts for the **manager-script skills**
(`yf-plan` / `plan_manager.py`, `yf-research` / `research_manager.py`), follow the strategy in
[TESTING.md](TESTING.md): Tier-1 unit tests of the manager script, plus Tier-2 **mechanical
drive** of the modified skill under a sandboxed `HOME` (never trust the installed copy — it is
the old, `rust-embed`-baked skill). Do not hand-roll an interactive-agent smoke; drive the
manager verbs directly.

## Syncing local `yf` to the repo

This repo is **both the source and a consumer** of its own skills. Editing `skills/` changes
nothing about the `yf` you are running until you rebuild and redeploy — they are separate
artifacts, and the gap used to be silent.

**Default land-the-plane step.** Once changes are pushed to `main`, sync local user scope with
**one** command:

```bash
yf self install --from-build --build   # rebuild, promote, and SYNC (skills + rules + config)
```

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
