---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #204: yf-herdr: no teardown contract — a completed plan's subordinate tab is never closed, and only harvest-before-prune makes closing safe

- **Number:** 204
- **Title:** yf-herdr: no teardown contract — a completed plan's subordinate tab is never closed, and only harvest-before-prune makes closing safe
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Filed by operator decision from the **plan-051** session. Related: #198 (the harvest→prune hazard, same ordering constraint), #203 (structural verification of an operation's result).

## The gap, measured

`skills/yf-herdr/SKILL.md` mentions closing a tab **exactly once**, at line 233:

> Do not close tabs or panes you did not create, and do not `herdr server stop`.

That is a **prohibition on closing someone else's tab**. There is no requirement, no guidance and no `REQ-HERDR-*` covering closing a tab the skill **did** create. `grep -niE 'close|cleanup|tear|prune|harvest|reap'` over `SKILL.md` returns that one line; the SPEC returns nothing for lifecycle teardown.

The result is a **lifecycle with two thirds of a contract**:

| Phase | Status |
| :-- | :-- |
| **Launch** | Mandatory contract (`REQ-HERDR-015`), three required elements, **mechanically enforced** by `scripts/test_launch_contract.py` |
| **Observe** | Specified (`REQ-HERDR-026`) — three push trigger classes, token stamps, polling fallback |
| **Teardown** | **Absent** |

## Observed twice in one session

plan-050 and plan-051 were both delegated to herdr tabs and both ran to completion. **Both tabs were closed only because the operator asked, each time.** Nothing in the skill would have closed either, and nothing would have flagged them as orphaned. A long-running operator accumulates a completed-plan tab per plan indefinitely.

## Proposed rule

**Close the subordinate tab once the delegated work is complete — and only once its context is captured.**

The trigger is the conjunction of all of:

1. plan status is `complete` (or the research project is packaged);
2. **land-the-plane is done** — merged **and pushed**, so the work is on `origin`, not merely local;
3. **upstream writes have landed** — the coarse tracker filed, comments posted, closes applied;
4. **context is captured** — see below.

## Harvest before prune — the load-bearing part

This is the ordering constraint, and it is the **same hazard #198 raises** for stage-script child sessions:

> **A pane's scrollback is the only copy of anything not written to the bundle.** Closing the tab destroys it irreversibly. If prune runs before harvest, the evidence is gone while the caller reports success.

So condition 4 must be **mechanical, not a judgement**. "All context captured" as a feeling is exactly the unbacked assertion class plan-051 exists to close. Concretely, before closing, assert:

- the plan bundle's artifacts exist **on `origin`**, not just in the working tree — `git ls-tree -r origin/main -- <plan_dir>` is non-empty and includes `plan.md`, `log.md`, the `reviews/`, the `findings/` and any `assets/`;
- `plan.md` status is `complete`;
- the retrospective is **non-empty** if the plan emits one;
- `git status --porcelain` is clean and `git rev-list --count origin/main..main` is **0**.

In this session that check ran before the close and returned 47 bundle files on `origin/main`, status `complete`, 6 retrospective entries, clean tree, 0 unpushed. **That is the shape the rule should require** — a precondition with an exit code, not a step that says "make sure you captured everything."

## Verify the close STRUCTURALLY

`herdr tab close <id>` returns `{"result":{"type":"ok"}}`. Confirm the teardown by **reading back the agent list** and asserting the pane is absent, rather than trusting the return value — the same discipline #203 argues for generally. Measured in this session: the close returned `type: ok` while the surrounding shell command exited **1** for an unrelated parsing reason. Either signal read alone would have been wrong in one direction.

## Explicitly NOT proposed

- **Do not auto-close on `agent_status: idle` or `done`.** A claude subordinate settles at `done` after every turn, and `yf-herdr`'s own observe table already warns that `idle`/`done` mid-plan "may be waiting, not finished." Closing on that signal would kill live sessions.
- **Do not close a tab the skill did not create.** Line 233 stays exactly as written; this adds an obligation for tabs the skill **did** create, it does not weaken the existing prohibition.
- **Do not close on abort.** A failed or aborted run is precisely when the scrollback has value the bundle lacks. Report the orphan and leave it for the operator.

## Suggested placement

A new `REQ-HERDR-*` plus a `## Teardown` section in `SKILL.md` after `## Observe`, symmetric with the launch contract — and, following the launch contract's own precedent, mechanically enforced by a test rather than left as advisory prose. `yf-herdr`'s history is instructive here: the autonomy guidance began life as advisory prose under `## Observe`, failed to prevent the behaviour it described, and had to be **promoted into the mandatory launch contract**. A teardown step written as a suggestion would likely repeat that.

