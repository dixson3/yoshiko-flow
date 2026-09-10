# plan-068 — landing-hazard playbook (Issue 4.1)

**This plan lands through the UN-REPAIRED `land` it is repairing**, and that is not a figure of
speech: the `land` that runs is the **installed** copy at
`~/.claude/skills/yf-plan/scripts/plan_manager.py`, which is byte-different from this branch's
repaired one (verified at execution time). Every fix in Epics 1 and 2 takes effect at the
**next** deploy, which is the **last** step of landing.

Not speculative. The two most recent commits on `main` before this plan's base are both plan-066
landing halts:

- `2c21688` — *HALT: plan-066's close chain fails verify-reconcile on 5 of 7 rows*
- `7a84eda` — *HALT 2: plan-066 completes at LAND — Issue 8.4b's guard requires HEAD on main*

So the base rate of a clean first landing in this repository is, on recent evidence, **low**. The
point of this playbook is that each halt below has a **known recovery**, so a halt is a delay
rather than an incident.

## The four known halts, each with its recovery

### H1 — `#353`: a guaranteed digest mismatch on **any** resume at or after `L_VALIDATED`

**What happens.** `LAND_DIGEST_EXCLUDED` omits `resolved_target_tip` and `merge_preview`. L4
commits the merge on the target, so the tip **always** moves — measured, not conditional. Any
resume after that point re-derives a manifest whose digest differs from the one the decision
carries, and `_land_repreview_or_halt` halts.

**When it bites.** Only on a **resume**. A landing that runs straight through never re-derives.
So H1 is the *second-order* hazard: it converts any other halt into a two-step recovery.

**Recovery.** Re-run `land --dry-run` to produce a **fresh** manifest, re-dispatch the `lander`
for a fresh decision, and `--apply` that. Do **not** hand-edit the stored digest — that is
forging the exact check `REQ-LAND-002` exists to perform.

**Do NOT "fix" it inline.** The fix is plan-069's, its design is unsettled (EXP-003 **refuted**
the wide-exclusion remedy while confirming the premise), and a wrong exclusion converts a
correctness check into a rubber stamp.

### H2 — `#352`: `requires_mention` is never checked at dry-run

**What happens.** `land --dry-run` never verifies that a drafted upstream body satisfies
`requires_mention`. The failure therefore surfaces at **L7**, after the writes are public.

**When it bites.** Only if this landing performs upstream writes. **This plan's does not** — its
`upstream_writes` set is empty, because Issue 3.1 already published every correction by hand under
Gate 4's authorization and verified each by read-back. So **H2 is out of range for this landing**,
and that is a fact about the decision document rather than luck.

**Recovery if it fires anyway.** The write is already public. Post a correcting comment; do not
delete. Verify by read-back (`gh issue view N --comments`), never by exit code.

### H3 — `#350`: L16 launders an unreadable unpushed count into `0`

**What happens.** A **failed measurement is reported as a green number**. If the unpushed count
cannot be read, L16 reports `0` — indistinguishable from "everything is pushed".

**Why it is the most dangerous of the four.** It does not halt. It produces a **false green**, so
the landing reports success with plan-folder writes possibly unpushed.

**Recovery — and this one is a MANUAL VERIFICATION, not a reaction.** After L16, before trusting
`L_DONE`:

```bash
git status --porcelain                 # must be empty
git rev-list --left-right --count origin/main...main   # must be `0	0`
```

Treat a green L16 as **unverified** until those two lines agree. That is the whole mitigation:
the check that failed silently is replaced by one run by hand.

### H4 — the executor's own bookkeeping is outside `REQ-LAND-030`'s wrapper

**What happens.** `REQ-LAND-030` wraps **step dispatch only**. The journal write and the row-shape
access *after* a step returns are outside it, so a malformed step row surfaces as a **bare
traceback with no envelope** — no verdict, no journal state, no halt class.

**Recovery.** Read the journal directly to find where it actually stopped:

```bash
cat .yf/plan/landing-journal.json   # or wherever the journal resolved
```

The journal is fsync'd per step, so it is authoritative even when the process died without a
report. Resume from the recorded phase — via H1's fresh-manifest route.

**Do NOT re-run `--apply` from L0 after a traceback** without reading the journal first. If the
traceback happened at or after L6, the push already occurred and L0–L6 are not idempotent in the
way a fresh run assumes.

## The redeploy rule — the one step that leaves the repository

**L19 LAST, from clean `main`, in sync with `origin`, NEVER from the execute branch.**

Three preconditions, all three checked and none assumed (AGENTS.md, *"Syncing local `yf` to the
repo"*):

```bash
git rev-parse --abbrev-ref HEAD                                   # must be `main`
git status --porcelain                                            # must be empty
git fetch origin && git rev-list --left-right --count origin/main...main   # must be `0	0`
```

**Why this plan in particular must not get it wrong.** The install **bakes whatever tree it builds
into the binary** and deploys it to every detected harness. Deploying from
`plan-068-james-dixson-8ae0e1-execute` would install a toolchain matching no published state, the
next `main`-based install would silently revert it, and nothing would record that either happened.

**And the mid-execution prohibition is separate and stricter.** No `yf skills install` /
`yf self install` **during** execution. `plan_manager.py` is re-invoked per call, so a
mid-execution deploy takes effect in the *same* session for the scripts — while `SKILL.md` prose
was loaded once at invocation. A half-deployed session runs **new scripts against old prose**,
which is exactly the failure mode a plan editing `plan_manager.py`'s landing path would produce.

`--force` does not make any of this safe; it removes the objections.

## The in-place specifics for this landing

- **The execute branch was hand-cut** (Issue 0.1) from `main@42bb27dd`, recorded in
  `assets/execute-base.txt`. That is the workaround this plan exists to remove, applied one last
  time — the installed `land` still halts `execute-branch-missing` without it.
- **One address space.** In-place mode means `ctx.root` *is* the execute checkout. L2 checks out
  the merge target **in that same tree** (a declared boundary, `REQ-LAND-004` as amended), so
  between L2 and the end of the landing the working tree is `main`, not the execute branch.
- **`REQ-BRANCH-004`'s carve-out ends at L2.** Before it, the primary is deliberately left on a
  plan branch; after it, the ordinary rule applies. If the landing halts between the cut and L2,
  the checkout is on the plan branch **by design** — do not "restore" it and lose the position.

## What is NOT a hazard, recorded so it is not mistaken for one

- **L3's FULL tier was red on `main` when this plan started**, via
  `_shared/test_doc_lint.py` SC41. Cleared at Issue 3.3 — see
  `findings/exec-001-inherited-doclint-red.md`. It is listed here because a landing that halts at
  L3 should first ask whether the red is this plan's at all.
- **`#349` and `#353` staying open** is deliberate (Issue 3.2), not an incomplete landing.
- **The rehearsal's green does not cover L14's DAG comparison.** Stated in the rehearsal record's
  own `honest_scope` field. If L14 halts, the rehearsal never exercised it, and that is expected
  rather than a contradiction.
