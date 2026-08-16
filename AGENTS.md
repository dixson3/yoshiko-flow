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
artifacts, and the gap is silent.

**Default land-the-plane step.** Once changes are pushed to `main`, sync local user scope:

```bash
yf self install --from-build --build   # 1. rebuild + promote the binary to ~/.local/bin/yf
yf skills install                      # 2. deploy skills → ~/.claude/skills/
yf harness tune                        # 3. deploy always-loaded rules + align config
```

**All three are required, in that order.** Step 2 is easy to omit and its absence is silent —
REQ-YF-SELF-005 auto-refreshes skills only after a **vendor update**, and states explicitly that
*"a from-build install shall NOT auto-refresh"* (verified: a probe file promoted into the binary
did not appear in `~/.claude/skills/`). Step 3 is separate because rules and config are not
skills. Order matters: step 2 must run from the **freshly promoted** binary, and `tune` reads the
skill contracts step 2 installed.

**Verify, do not assume** (#137 — the promote path can ship a stale embedded tree):

```bash
yf --version                                                    # git hash must equal HEAD
                                                                # (a `-dirty` suffix just means
                                                                #  uncommitted files; the hash
                                                                #  itself is what must match)
diff ~/.claude/skills/yf-plan/scripts/plan_manager.py \
     ./skills/yf-plan/scripts/plan_manager.py                   # must be empty
```

A stale sync is **silent**: `cargo build` exits 0, `self install` reports `status: ok`, and only
the version stamp betrays it. If the hash lags `HEAD`, force a re-embed and repeat:

```bash
touch yf/src/embed.rs && yf self install --from-build --build --force
```

**Why** (measured, see #137): `skills/` sits outside the `yf/` package and `yf/build.rs`
deliberately emits no `rerun-if-changed`, so an **incremental release rebuild does not observe
`skills/` edits**. Release bakes the tree at compile time; debug reads it from disk at runtime
(no `debug-embed` feature), so `./target/debug/yf` is always current and `--release` is the
exposed path.

**Never run step 2 on its own** to pick up local changes. `yf` on `PATH` deploys whatever tree
*its* binary embeds, so without step 1 first it will quietly overwrite newer skills with older
ones. Step 2 is safe only because step 1 precedes it. To deploy without promoting a binary, run
`./target/debug/yf skills install` explicitly — debug reads `skills/` from disk, so it is always
current.

## Upstream Tracking

- **Source / repo / tool:** github · `dixson3/yoshiko-flow` · `gh issue`
- **Granularity:** coarse (default). File ONE tracking issue per plan-scale effort (e.g. per `/yf-plan` plan), linking the plan + epic — NOT one per execution bead. At land-the-plane, create/update that single coarse issue; do NOT push granular sub-beads upstream unless explicitly asked. Precedent: #13 (plan-005), #14 (plan-006), #16 (plan-007).
- **Notes:** Issues filed against the published skill repo; this working directory (`beads-skills`) is the same codebase.
