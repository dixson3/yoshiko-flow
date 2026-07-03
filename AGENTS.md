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

## Upstream Tracking

- **Source / repo / tool:** github · `dixson3/yoshiko-flow` · `gh issue`
- **Granularity:** coarse (default). File ONE tracking issue per plan-scale effort (e.g. per `/yf-plan` plan), linking the plan + epic — NOT one per execution bead. At land-the-plane, create/update that single coarse issue; do NOT push granular sub-beads upstream unless explicitly asked. Precedent: #13 (plan-005), #14 (plan-006), #16 (plan-007).
- **Notes:** Issues filed against the published skill repo; this working directory (`beads-skills`) is the same codebase.
