---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #222 - yf-plan: the phase model has no slot for post-merge/post-teardown
  work, yet 6.2 teardown predictably invalidates worktree-rooted artifacts'
---
# Upstream #222: yf-plan: the phase model has no slot for post-merge/post-teardown work, yet 6.2 teardown predictably invalidates worktree-rooted artifacts

- **Number:** 222
- **Title:** yf-plan: the phase model has no slot for post-merge/post-teardown work, yet 6.2 teardown predictably invalidates worktree-rooted artifacts
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium

## Body

Filed by operator decision from the **plan-004** session in `dixson3/rc-files` (CLIProxyAPI local model gateway). Three instances, one root cause, all measured on a live machine.

## The class

**A bead cannot do work that requires post-merge or post-teardown state, because every bead must close before either happens.**

```
SKILL.md:1277   Reconcile gate: "Auto-resolves when all execution beads close. Proceed to Phase 6."
SKILL.md:1297   "### 6.1 — Merge-back"
                 6.2 — worktree teardown, later still
```

So the ordering is: **all beads close → merge-back → teardown**. Any issue whose acceptance depends on the merged tree, or on the worktree being gone, is **structurally unsatisfiable as an in-tree bead**. It is not a scheduling problem that a `depends-on` edge can fix.

§5.3's address-space model is the reason this is easy to author by accident. It carefully routes **code edits** to the worktree and **plan-folder writes** primary-side — but says nothing about a third category: an **artifact deployed FROM the repo INTO the OS**, whose correctness is a property of the primary checkout and which the worktree is simply the wrong address space for.

## Instance 1 — a symlink asserted during worktree execution points into the worktree

plan-004 symlinks a committed config into Homebrew's prefix. Issue 3.2 asserted it correctly, from the only repo root it can see:

```
/opt/homebrew/etc/cliproxyapi.conf
  -> /Users/james/_dotfiles/rc-files/.worktrees/plan-004-.../cliproxyapi/config.d3.yaml
```

§6.2 teardown removes that directory. The symlink then **dangles** — and for this particular tool, dangling is not benign: Homebrew's `install_renamed.rb::append_default_if_different` tests `dst.file?`, which **follows symlinks**, so a dangling link causes `brew upgrade` to write the upstream default **through** the link to its source path. The upstream default binds `host: ""` — all interfaces — on a service holding a subscription OAuth credential.

Measured, in a scratch prefix: intact symlink → preserved, `.default` written beside. Dangling symlink → **written through**, 48718 bytes, `host: ""` materialised at the source path, which *re-validates* the symlink so every static detector reports healthy again.

## Instance 2 — live verification reads the primary checkout, not the worktree

plan-004's SC13/SC14 require "one live run through `pi` / `opencode` with the proxy log tailed". But:

```
~/.pi/agent/settings.json  -> <primary>/pi/settings.json
~/.config/opencode         -> <primary>/opencode
```

The live harnesses read the **primary** checkout. Epic 5 edited the **worktree** copies, which have no effect until merge-back. Verifying during Epic 5 therefore yields either a false red (traffic still goes to the old provider) or — worse — a false green, if the agent inspects worktree file *contents* instead of doing a live run.

## Instance 3 — the deadlock, which is the sharpest form

plan-004 originally had `6.1 depends-on 5.5`, where 5.5 is the post-merge E2E verification. The executing agent found this itself and re-pointed `5.5 -> 6.6`. That made the DAG acyclic — and left **both** beads unsatisfiable, because 6.6 (post-teardown symlink re-assert) has the identical defect. **Ordering two impossible things against each other does not make either possible.**

Both were in-tree, so `close_cascade.py` at §6.4 would have fail-louded and halted completion — correctly, but long after the cause.

## What we did, and why it is a workaround rather than a fix

The escape hatch **already exists** and is the right mechanism — `SKILL.md:1595`, "Filing the deferred-validation bead (option b)": a standalone, out-of-tree bead, *"never a child of `${EPIC}`, or cascade-close fail-louds on it first"*, pushed individually upstream.

We converted both to out-of-tree deferred beads (`parent=None`, no deps, `deferred-validation` label) and reworded the criteria to `manual, verified AFTER plan completion`.

But nothing in `SKILL.md` **points an author there at authoring time**. The escape hatch is documented in §6.4 as a remedy for "a real green run is not yet achievable" in the `ci-release` completion-gate context — not as the general answer to "this issue needs post-merge state". Three passes of red-team on this plan did not catch any of the three instances; the executing agent found instance 3 only when the DAG deadlocked.

## Suggested fix

1. **Name the third category in §5.3.** The address-space model should say explicitly that an artifact deployed from the repo into the OS (symlink, service registration, installed unit) is a **primary-checkout** property, and that asserting it from a worktree roots it in a path teardown will remove.
2. **Give authors a rule at authoring time**, not just a remedy at §6.4: *an issue whose acceptance requires the merged tree or a torn-down worktree cannot be an in-tree bead — file it out-of-tree per §6.4's deferred pattern.*
3. **Consider a mechanical check.** `plan_extract.py` or the conformance reviewer could flag an issue whose text matches post-merge/post-teardown intent while it sits in-tree. Cheaper than discovering it at cascade-close.
4. **A worked improvement, for the doc:** plan-004's agent later realised the symlink re-assert only needs the primary to *carry* the file — true at **merge-back**, not teardown — so it ran immediately after the merge commit and **pre-empted the dangling window** rather than repairing it. Not every post-merge item needs to be deferred; some just need the correct trigger point. Worth saying so.

## Related

- #47 (closed) — branch/worktree model. Adjacent, but that is about branch topology; this is about *when* a bead may observe the merged tree.
- #204 — yf-herdr teardown contract. Different teardown, same general blind spot around post-completion state.
