---
name: yf-herdr
description: >
  Delegate an approved yf-plan or a gated yf-research project to a NEW herdr tab running a fresh
  session of the same agent kind, then observe that subordinate session and mine its deviations for
  process improvements.
  TRIGGER when: /yf-herdr invoked; or the operator asks to "execute the plan" / "execute the
  research" / "run it in a new session" AND this session is running inside herdr (HERDR_ENV=1) AND
  this session has recently asserted that a specific plan or research project is ready to execute.
  SKIP for: sessions not under herdr (say so and hand the command to the operator); a fresh session
  that did no planning work (execute in place — a tab buys nothing); any request to CREATE or
  APPROVE a plan (that is yf-plan) or to drive panes for unrelated reasons (that is the herdr
  skill). This skill never authors plans and never resolves a gate.
user-invocable: true
skill-group: utility
depends-on-tool: [herdr, uv]
---

# yf-herdr

Delegates execution to a subordinate session and keeps watching it. Two responsibilities, and the
second is the one that pays: **launch** correctly, then **observe** honestly.

## What this skill is for

`yf-plan` requires execution in a **new session** — the fingerprint, not conversation state, carries
eligibility across the boundary (`yf-plan` SKILL.md §4.6). `yf-research coordinate` says the same.
Left to itself that means the operator opens a terminal, starts an agent, and types the command.
This skill does that in a herdr tab and, crucially, does not then forget about it.

## Preflight — all four must hold

Check in order and stop at the first failure. **Do not spawn a tab speculatively.**

```bash
test "${HERDR_ENV:-}" = 1                     # 1. inside a herdr-managed pane
command -v herdr >/dev/null                   # 2. CLI present
```

3. **Readiness is VERIFIED, not remembered.** The conversation may *say* a plan is ready; confirm it
   mechanically before spawning anything:

```bash
# yf-plan: status must be `approved` AND the fingerprint fresh (not stale-approved)
uv run <yf-plan>/scripts/plan_manager.py resume-scan "<plan_dir>" --json   # stale_approved:false
# yf-research: the coordinate gate must be resolvable
```

   A plan in `ready-for-approval`, in `abandoned` (deliberately stopped — it is terminal and
   not execute-eligible), or `approved` with a **stale** fingerprint, is **not** ready — it
   needs re-approval, not a session. Report that and stop.

4. **This session must be context-dirty** — it did the planning work. A fresh session has no
   boundary to cross and should run `/yf-plan execute …` **in place**; spawning a tab is pure
   overhead and splits the observer from the work for nothing.

On failure of (1): say plainly that this is not a herdr session, print the command the operator
should run, and stop. On (3) or (4): explain which condition failed rather than proceeding.

## Launch

**Match the current agent kind.** Do not assume `claude` — resolve what *this* session is:

```bash
KIND=$(herdr agent list --json | jq -r --arg p "$HERDR_PANE_ID" '.result.agents[]|select(.pane_id==$p)|.agent')
```

Create the tab in the **current workspace**, at the repo root, without stealing focus — and
**seed the parent handle** with `--env` so the subordinate can push back (REQ-HERDR-015):

```bash
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$(git rev-parse --show-toplevel)" \
  --label "<plan-id> execute" --no-focus \
  --env YF_PARENT_PANE="$HERDR_PANE_ID"            # → .result.root_pane.pane_id
herdr agent start "<short-name>" --kind "$KIND" --pane "<that pane id>" --timeout 120000
```

`--env YF_PARENT_PANE` is measured to reach the agent process **and its grandchildren**, which
is what makes the push channel work from inside a tool call. Use the **pane id**, not the agent
name: `HERDR_PANE_ID` is injected automatically and is stable, whereas a name exists only for
`agent start`-ed agents and **goes stale on rename**.

Parse every id from the JSON responses; never predict them. Give the agent a **stable short name**
(`plan-014`, `research-003`) — it is the handle every later turn uses.

### The launch prompt is a CONTRACT, not a command (REQ-HERDR-015)

A bare `herdr agent prompt "<name>" "/yf-plan execute <plan-id>"` is **non-conformant**. It was
the old recipe, and a parent following it literally produced exactly the stop-after-every-epic
behaviour this skill's own trap warns about — because the fix lived as advisory prose under
`## Observe`, read *after* the prompt was already composed.

Three elements are **mandatory**. Send them in the prompt **and** in
`-- --append-system-prompt`, so they survive the subordinate's context compaction (measured
free: 3.016s with, 3.061s control):

```bash
read -r -d '' CONTRACT <<EOF
AUTONOMY. Run the plan to completion. Report at epic boundaries but CONTINUE without waiting.
Stop ONLY at the stop classes the plan itself declares: an outward-facing or irreversible
write; a capability gate whose Test exits non-zero; a destructive local operation; a
mechanical counter threshold; or a declared mechanical check that fails.

PUSH MILESTONES TO ME, do not stop for them:
  herdr agent prompt "\$YF_PARENT_PANE" "<one line>"
at each EPIC COMPLETION, each BLOCKER or FAILED GATE, and at PLAN COMPLETION OR ABORT.
Never per bead. Never pass --wait.

PARENT HANDLE. YF_PARENT_PANE is seeded in your environment.
EOF

herdr agent prompt "<short-name>" "/yf-plan execute <plan-id>

$CONTRACT"
```

A launch omitting any of the three is non-conformant, not merely sub-optimal. This is
mechanically enforced by `scripts/test_launch_contract.py`.

**Record the delegation** in the conversation: agent name, pane id, what was launched. A later turn
must be able to find the subordinate without re-deriving it.

## Observe — push-primary, polling as the fallback

**The subordinate pushes; you poll only when it hasn't.** The old framing — "a turn-based agent
cannot watch continuously" — is true of **pull** and was mistaken for a law of observation as
such. There is indeed no execution between your turns, so *your polling* happens at turn
boundaries and on demand. But the child can speak, and under the launch contract it does.

### Push triggers (REQ-HERDR-026)

The subordinate pushes at exactly **three** trigger classes:

| Trigger | Why it is a push |
| :-- | :-- |
| **Epic completion** | The natural progress checkpoint — a report, not a stop |
| **Blocker, failed gate, or halt** | The parent may be able to resolve it from approved plan content |
| **Plan completion or abort** | The terminal event |

**Never per bead.** A plan-sized DAG would emit tens of messages and flood the parent's context,
which is the failure mode that makes a parent stop reading them.

**`--wait` is forbidden.** It reintroduces the lockstep the push channel exists to remove. And
`--wait --until idle` is measurably *wrong* for a claude subordinate: a claude turn settles at
`done` and **never** at `idle`, so the wait times out at 120s on a turn that in fact completed.

### Pair every push with a token stamp (REQ-HERDR-026, D-8)

**`agent_prompted` acknowledges INJECTION, NOT SUBMISSION.** One measured push returned success
and was never submitted. So a push alone is an unverified claim of delivery — exactly the
self-report-vs-verification defect this repo keeps rediscovering.

```bash
# Idempotent, on the CHILD'S OWN pane.
herdr pane report-metadata "$HERDR_PANE_ID" --source "<plan-id>" --token "epic-3=done"
```

**Two CLI gotchas, both verified against the binary rather than the usage string:**

- **`<PANE_ID>` must come FIRST.** The usage string reads
  `report-metadata [OPTIONS] --source <ID> <PANE_ID>`, but passing the pane id last fails with
  `unknown option: <source-value>` — the parser consumes the following token as an option
  value. Pane id first exits 0.
- **`--token` takes `NAME=VALUE`, not a bare value**, and **`--source <ID>` is required**.

Read it back with `pane get` / `agent get` / `agent list`; the stamp surfaces as a `tokens`
object on the pane (verified: `"tokens":{"epic-3":"done"}`). A push costs the parent a turn; a
token write costs nothing — which is what turns the polling path into a genuine **backstop**
rather than a second, competing mechanism.

### Polling — the fallback

Poll when the subordinate has **gone silent**, reads `blocked`, or you want corroboration:

```bash
herdr agent get <name>                                  # agent_status
herdr agent read <name> --source visible                # while working; alternate-screen safe
herdr agent read <name> --source recent-unwrapped --lines 60   # once idle
```

Escalate **in that turn's reply**, not silently:

| Signal | Meaning | Action |
| :-- | :-- | :-- |
| `blocked` | a question or approval UI is open | Read it. Answer only if it is settled by existing plan content; otherwise bring it to the operator |
| a gate is reported | needs operator authority | Surface it with what authorising actually accepts. **Never resolve a gate on the operator's behalf** |
| `idle`/`done` mid-plan | may be waiting, not finished | Check remaining beads before reporting completion |
| an error or refusal | | Report verbatim; do not paper over |

**Two traps, both observed live:**

- A prompt sent to a **`blocked`** agent is consumed by the open dialog and silently lost. Check
  `agent_status` before prompting; if `blocked`, resolve the dialog first, then prompt.
- A push into a **`blocked` parent** is swallowed by the same mechanism — the trap is stated
  child-ward but applies symmetrically. The **token stamp is the mitigation**: it survives a
  swallowed push, so a parent that was blocked can still reconstruct what happened by reading
  the child's pane metadata.

*(The old note here — "subordinates often stop after each epic when told to report back; if
autonomy is wanted, say so explicitly" — has been **promoted into the mandatory launch
contract** above. It was advisory prose in the wrong section: read after the prompt was already
composed, which is why it did not prevent the behaviour it described.)*

## Mine deviations for process improvements

This is the skill's real payload. When execution **diverges from what the plan assumed**, that is
evidence about the *planning* workflow, and it is only visible from the outside. Watch for:

| Deviation observed | Likely upstream defect |
| :-- | :-- |
| A finding's premise is refuted at execution | Investigation recorded an **inference as a measurement**, uncorroborated → `yf-plan` investigator / red-team premise check |
| A gate's condition cannot be satisfied | Gate blocks the issue that produces its own evidence → gate **reachability** |
| An issue needs a tool/artifact authored later | Precondition not checked against DAG order → execution-rehearsal gap |
| Bead count at pour ≠ issue count in plan.md | Pour step mis-read the plan |
| Plan content edited mid-execution | Scope was wrong at approval, or the plan encoded a guess |
| A success criterion proves unachievable, or two contradict | Criteria never checked against each other |
| The same class of defect recurs across plans | The **fix belongs upstream**, not in this plan |

For each: record what was observed, what it implies about the process, and which skill owns the fix
(`yf-plan`, `yf-research`, or a transitive skill). Distinguish a **one-off** from a **class** — a
single occurrence may still be worth a cheap prompt-level fix, but say which it is.

**Report; file only on the operator's say-so.** Surface deviations and proposed improvements in
conversation. File upstream (`dixson3/yoshiko-flow`) only when the operator approves. Do not
auto-file: transient blips generate noise and duplicates, and the operator is the one who knows
whether a pattern is real.

## Rules

- **Never resolve a capability gate.** Gates exist to spend operator attention; a delegating skill
  resolving one defeats the whole mechanism.
- **Never spawn a second tab for the same plan.** Re-use the recorded agent name; a duplicate
  subordinate means two sessions racing the same bead DAG.
- Do not close tabs or panes you did not create, and do not `herdr server stop`.
- Verify readiness mechanically every time. A conversational assertion of readiness is a claim,
  not a fact — that distinction is the same one this skill teaches the operator to look for.

## Relationship to the `herdr` skill (prose soft-dep)

CLI semantics — pane/agent primitives, id handling, lifecycle states — live in the **`herdr`**
skill. That skill is **third-party and not shipped by this repo**, so it is deliberately *not*
listed in this skill's `depends-on-skill` frontmatter: that field takes bare **in-repo** skill
names, and naming a skill the repo does not ship would be a force-install of something the
installer cannot provide. The dependency is expressed here, in prose, exactly as `yf-plan` treats
`yf-change-validation` (SKILL.md §6.1.5): **present → delegate to it; absent → say so plainly and
hand the command to the operator.**

The hard requirement is the **tool**, declared as `depends-on-tool: [herdr, uv]`. Without the
`herdr` binary the preflight's four conditions cannot hold, so this skill is inert rather than
broken (REQ-HERDR-040/041).

See `SPEC.md` for requirements.
