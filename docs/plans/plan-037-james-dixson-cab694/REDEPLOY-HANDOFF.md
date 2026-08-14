---
type: Reference
okf_spec: OKF-PLAN
---
# Redeploy handoff — refreshing user scope after plan-037

**This document does not perform the redeploy.** plan-037 was deliberately scoped to the
repository only; `~/.claude/skills/` and `~/.claude/rules/` were **not modified at any point**
during its execution. Refreshing them is a separate, operator-invoked step, and this is its
written, ready-to-run instruction sheet.

Nothing here is urgent. Issue 5.2 proved the repo is now a **superset** of the install, so the
work that could have been lost is safe in git. The remaining staleness is harmless and
self-correcting — it fixes itself whenever you choose to run the commands below.

## Preconditions

1. plan-037 is merged to `main` and pushed.
2. **No plan is mid-execution.** See "The landing-lock trap" below — this is the one real
   hazard, and it is timing, not correctness.
3. You are on the machine whose `~/.claude/` you want refreshed.

## The command

The installer is the **`yf` binary**, not `install.sh`. That script no longer exists in this
repo — several older documents still reference it, and following them will simply fail.

```bash
cd /Users/james/workspace/dixson3/yoshiko-flow
git checkout main && git pull

# 1. Rebuild so the binary re-embeds the CURRENT skills/ tree.
#    The skill payload is baked in at build time (rust-embed) — an old binary
#    installs old skills no matter how current the checkout is.
cargo build --release

# 2. Preview. Always do this first.
./target/release/yf skills install --scope user --harness claude-code --dry-run

# 3. Install the skills.
./target/release/yf skills install --scope user --harness claude-code

# 4. Deploy the always-loaded rules. This is a SEPARATE operation as of plan-033
#    (REQ-YF-INSTALL-008): `skills install` is skills-only and does NOT write rules.
./target/release/yf harness tune --harness claude-code
```

## What it will change

| Surface | Change |
|:--|:--|
| `~/.claude/skills/yf-*` | All 19 skills overwritten from the repo. 18 refresh from a ~2026-07-21 snapshot; **`yf-herdr` is new** (plan-037 imported it). |
| `~/.claude/rules/YOSHIKO_FLOW.md` | Regenerated from the 8 shipped `skills/*/protocols/*.md`. |
| `~/.claude/skills/{herdr,mermaid,naba}` | **Untouched.** Third-party skills this repo does not ship. |

The one file you might expect to lose is the local `plan_manager.py` patch. It is now
**redundant rather than load-bearing**: Epic 2 landed the same capability as a repo feature
(`plans-root` / `incubator-root` via `REQ-PLAN-073`), so overwriting it loses nothing. Its
verbatim pre-import snapshot is preserved at `references/user-scope/` regardless.

## How to verify afterward

```bash
python3 docs/plans/plan-037-james-dixson-cab694/scripts/superset_check.py
```

Exit 0 means every `yf-*` artifact in user scope has a repo counterpart. After a redeploy the
`yf-herdr` files should flip from `DIVERGED` to `OK identical`, since user scope will then be a
copy of the repo rather than the pre-import original.

### Two traps this plan discovered — do not compare naively

1. **Filter the install stamp.** The installer injects
   `<!-- yf-skills: v=<version> tree=<sha> -->` into every `SKILL.md`. A raw `diff -r` reports
   **19 false positives** purely from that line. `superset_check.py` strips it; any hand-rolled
   comparison must too.
2. **Exclude `__pycache__/`, `*.pyc`, and `.DS_Store`.** They exist on one side or the other for
   reasons that have nothing to do with skill content.

A third, subtler one from `exp-01`: the stamp's `v=0.4.0` is the **Cargo version**, not the
`v0.4.0` git tag. Comparing user-scope files against the tag yields spurious "local edit"
verdicts. Compare against the commit the stamp's `tree=` sha names.

## The landing-lock trap

**Do not redeploy while a plan holds `landing.lock`.**

Epic 2 moved `plan_manager.py`'s state directory from the full-name `.yf/yf-plan/` to the
short-name `.yf/plan/` (#100), and added a migration that moves any pre-existing state across on
first use. The redeploy is the moment the **installed** skill starts using the new path.

This is not hypothetical — it happened during plan-037's own execution. The session acquired
`landing.lock` using the stale installed skill (which wrote `.yf/yf-plan/landing.lock`), then a
test run imported the *repo's* `plan_manager.py`, whose migration relocated the lock to
`.yf/plan/landing.lock`. The subsequent release call, still running the stale skill, looked in
the old location and reported **"no lock held"** while a lock file sat in the new one. Harmless
there because the merge was already complete and the stale file was removed by hand; during a
live merge-back it would mean two sessions could both believe they hold the landing lock.

So: land or abandon any in-flight plan first, confirm no `landing.lock` exists under either
`.yf/plan/` or `.yf/yf-plan/`, and only then redeploy.

## The rules-bundling question — resolved

plan-037's investigation deliberately left one question open: whether the 8 companion rules
being installed as a single concatenated `~/.claude/rules/YOSHIKO_FLOW.md`, rather than as 8
separate files, is a deliberate design choice or install drift.

**It is deliberate.** The aggregated ruleset is a specified feature — `REQ-YF-FLOW-001..007`,
introduced by plan-011 — and `SPEC.md` §3.3.1 states the intent directly: `yf` surfaces every
rule-bearing skill's protocol as **one** operator-facing file "instead of a scatter of
standalone `*.md` files". Each protocol is embedded verbatim inside an HTML-comment fenced
section carrying its own `sha256`, ordered alphabetically, under a do-not-edit banner.

Two consequences worth knowing before you redeploy:

- **Do not hand-edit `YOSHIKO_FLOW.md`.** Managed sections are regenerated to the embedded
  source on every tune (`REQ-YF-FLOW-004`); edits inside a fenced section are discarded.
- The aggregation is invoked by **`yf harness tune`**, not by `yf skills install` (`REQ-YF-FLOW-007`,
  moved by plan-033). Running only step 3 above refreshes skills and leaves the rules stale —
  which is why step 4 is a separate command rather than an optional extra.

No action is required on this axis. It is recorded because plan-037 named it an open question,
and leaving a resolved question looking open would be its own kind of drift.
