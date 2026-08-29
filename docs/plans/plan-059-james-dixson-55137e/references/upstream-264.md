---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #264: yf-herdr: AUTONOMY clause does not survive a phase boundary — subordinate goes idle after pushing

- **Number:** 264
- **Title:** yf-herdr: AUTONOMY clause does not survive a phase boundary — subordinate goes idle after pushing
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/264
- **State:** OPEN
- **Labels:** 

## Body

## Summary

The mandatory launch contract's **AUTONOMY** element (REQ-HERDR-015a) is insufficient to keep a
subordinate running across a **phase boundary**. Observed live during `yf-research` 005: the
subordinate pushed its retrieve-wave milestone as instructed, then went `idle` and waited,
rather than continuing into the next phase. It required an explicit parent nudge to resume.

This is a **second occurrence of a known class**, not a one-off. `SKILL.md` §"The launch prompt
is a CONTRACT" already records the first: a parent following the old bare-prompt recipe
"produced exactly the stop-after-every-epic behaviour this skill's own trap warns about". The
documented fix was to promote the autonomy note out of advisory prose in `## Observe` and into
the mandatory contract. **That fix was applied and the behaviour still occurred** — so the
promotion was necessary but not sufficient, and the remaining defect is in the contract's
*wording*, not its placement.

## What happened

Launch was conformant. All three REQ-HERDR-015 elements were sent, in both the prompt and
`--append-system-prompt`:

- (a) autonomy directive — the canonical `SKILL.md` phrasing, adapted for research phases:
  `"Run the research pipeline to completion. Report at wave/phase boundaries but CONTINUE
  without waiting."`
- (b) push contract, with `--wait` forbidden and token stamps paired
- (c) parent handle, `YF_PARENT_PANE` seeded via `--env` on `tab create` and restated in prose

The subordinate honoured (b) and (c) exactly — every push landed and every token stamp was
written (`gate=done`, `tooling=done`, `corpus-reconciled=done`, `retrieve=done`). It also ran
autonomously **within** a wave, across many bead boundaries, without stopping.

It stopped at the **phase** boundary — precisely where the push occurs.

## Diagnosis

`"Report at epic boundaries but CONTINUE without waiting"` is readable two ways, and the
subordinate took the wrong one:

| Reading | Behaviour |
| :-- | :-- |
| intended | push the milestone, then immediately begin the next phase in the same turn |
| observed | push the milestone, end the turn, await acknowledgement |

"Continue without waiting" constrains *whether to block on a reply*. It does not state *when the
next phase starts*. Since a push is itself an outbound message, ending the turn after sending one
is a natural — and locally reasonable — reading. The clause never says the next unit of work
begins **in the same turn as the push**.

Note the asymmetry that makes this diagnosable: the same subordinate did **not** stop at bead
boundaries, only at boundaries where it had just pushed. The push is the trigger for the stop.

## Proposed fix

Tighten the AUTONOMY wording in the `SKILL.md` §2.2 `CONTRACT` heredoc to bind the push and the
continuation into one action:

```
AUTONOMY. Run the plan to completion. At each reporting boundary, PUSH THE MILESTONE AND
IMMEDIATELY BEGIN THE NEXT PHASE IN THE SAME TURN. A push is a report, not a checkpoint --
do not end your turn after pushing and do not await acknowledgement. Ending a turn
immediately after a push is non-conformant.
Stop ONLY at the stop classes the plan itself declares: ...
```

Two secondary points, offered as observations rather than as part of the ask:

1. `scripts/test_launch_contract.py` mechanically enforces that the three elements are
   *present*. Presence was never the failing condition here — the elements were all present and
   the behaviour still occurred. Whatever the wording becomes, a presence check cannot detect
   this class; only observing a live subordinate can.
2. REQ-HERDR-025 already says `idle`/`done` must not be read as completion without checking
   remaining beads. That REQ is what caught this — the parent polled, saw `idle` with
   `triangulation.md` absent, and correctly classified it as "waiting", not "finished". The
   detection side worked; only the prevention side failed.

## Evidence

- Session: `yf-research` 005, `docs/research/005-thrash-detection-and-operator-judgement`,
  epic `yf-mol-49u`
- Subordinate: agent `research-005`, pane `wK:p16`, kind `claude`
- Observed 2026-08-28, after the 6-cluster retrieve wave completed (228 sources merged)
- State at stop: `agent_status=idle`,
  `tokens={"corpus-reconciled":"done","gate":"done","retrieve":"done","tooling":"done"}`,
  `artifacts/triangulation.md` absent
- Resumed by explicit parent prompt restating the AUTONOMY clause; subordinate then confirmed
  `working` and proceeded normally

Affects: `REQ-HERDR-015` (element (a) wording), `SKILL.md` §2.2 launch contract.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

