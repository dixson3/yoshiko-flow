---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #255: Cut the v0.5.0 release: push the tag (deferred from plan-054, everything else staged and green)

- **Number:** 255
- **Title:** Cut the v0.5.0 release: push the tag (deferred from plan-054, everything else staged and green)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

**The tag push is the only remaining work.** plan-054 completed everything else and deliberately
descoped Issue 6.8 so the operator could verify the harnesses manually under a real `HOME`
before an irreversible act.

## State, measured in the primary checkout

| Fact | Value |
| :-- | :-- |
| `main` HEAD | `1eba35d` |
| Unpushed commits | **0** |
| `yf/Cargo.toml` | `0.5.0` |
| `Cargo.lock` (`yf`) | `0.5.0` |
| `CHANGELOG.md` | released `## v0.5.0` heading, no `Unreleased` above it |
| `web/pelicanconf.py` | `YOSHIKOFLOW_RELEASE = "v0.5.0"` |
| FULL validation tier | **51/51 pass** |
| `v0.5.0` tag | **does not exist** |

`yf 0.5.0 (1eba35d)` is installed and synced to all five harnesses (claude-code, agents, codex,
opencode, pi); the consent gate did not fire.

## Why this was not done autonomously

Pushing the tag is **irreversible** *and* **auto-publishes the website** — there is no
fix-it-afterwards window. That is a class-1 outward-facing write, and plan-054's own gate
structure put it behind a human decision by design.

## Two gates must be satisfied FIRST — afresh

Both were **descoped, not resolved**, when plan-054 closed. They were closed rather than
resolved deliberately: resolving would have asserted evidence that does not exist, and the second
is an authorization no test can stand in for.

1. **Live harness regression green.** The headless smoke must pass under **both pi and opencode
   against the DEPLOYED tree**, including a resolver check under an isolated `HOME`. An
   **INCONCLUSIVE blocks** — this is the last gate before an auto-publishing tag, and a gate that
   tolerates its own failure is not a gate.

   *Existing evidence, which is an INPUT to that decision and not a substitute for it:*
   `docs/plans/plan-054-james-dixson-535968/assets/harness-smoke-transcript.md` records a live
   **pi 0.84.1 + opencode 1.18.23** run against the deployed tree with all five arms passing —
   including the isolated pi-only-`HOME` arm with `yf` unreachable, and the **divergent-tree**
   test proving the Issue 6.10 install-time stamp resolves each harness to its own tree.

2. **Release authorization.** The operator authorizes the push. A green test establishes that a
   *condition holds*; it can never establish that a *human authorized* something.

## When both are satisfied

```bash
git tag -a v0.5.0 -m "yf v0.5.0"
git push origin v0.5.0        # irreversible; auto-publishes the website
```

Then verify the published site reflects `v0.5.0` and that the release artifacts built.

## Context

- Coarse tracker for the work already done: #236
- The release notes state two known limitations a user meets immediately: `--harness pi` tunes
  rules and skills only (#121), and on a symlinked rule surface `tune` / `--revert` edit the
  link's **target**, so a dotfiles repo comes back dirty by design.

Successor to plan-054 Issue 6.8.

