---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #114: yf-plan: verify the PREMISES a plan rests on, not just its internal consistency (measurement vs inference)

- **Number:** 114
- **Title:** yf-plan: verify the PREMISES a plan rests on, not just its internal consistency (measurement vs inference)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Split out of #113 as a distinct axis. #113 covers **structural** correctness — does the DAG hold together, is each precondition available when its step runs. This issue covers **factual** correctness — is the finding the plan is built on actually true. The two share no implementation and should not be bundled.

## The failure

In `d3-pxe` plan-014, an investigation (EXP-001) measured a guest whose telemetry agent was stopped and concluded:

> the CT **rebooted** at 03:48 UTC and the agent never came back

That came from one command, `uptime -s`. The plan then built on it:

| Artifact | What it assumed |
| :-- | :-- |
| Issue 1.2 | "fix the boot-start defect" |
| Issue 3.3 | reboot the guest — justified as *"the only test that actually exercises the 1.2 fix"* |
| A capability gate | authorising a **production database restart** |
| Risk R3 | high — that reboot was a known-unpredictable scenario that had previously caused a gateway outage |
| SC9 | a success criterion requiring the reboot |

At execution, the first diagnostic issue refuted the premise in one command. `journalctl --list-boots` returns **exactly one boot**. It was a **first boot** — the container had been rebuilt. The unit was installed 22 minutes *after* that boot and never started, so `WantedBy=multi-user.target` had never once been evaluated.

**There was no boot defect.** Five plan artifacts rested on a misreading, and one of them would have restarted a production database to test a bug that did not exist.

## Why no existing pass caught it

The plan was **internally consistent throughout**: acyclic DAG, every precondition satisfied where needed, the gate blocking the right issue, the criterion verifiable. It passed conformance and **two** red-team cycles — both of which found other real defects, so they were not asleep.

They missed this because every pass reasons about the plan's **internal coherence** and none re-tests the factual claim underneath. `agents/red-team.md` comes closest with *"Feasibility: are findings sufficient for the chosen approach?"* — but *sufficient* is not *true*. A finding can be perfectly sufficient and wrong.

## The distinction that matters: measurement vs inference

`uptime -s` **measures** "when did this kernel start."
"The CT rebooted" is an **inference** — and it is wrong, because a first boot and a reboot are indistinguishable from uptime alone.

The finding recorded the inference with the confidence of a measurement, and nothing downstream could tell them apart. The current finding template does not separate:

- **measurements** — a command ran, this was its output;
- **inferences** — what the author concluded from it.

Only the second class can be wrong while looking rigorous, and it is precisely the class that propagates into epics, gates and success criteria.

## Proposed change — two prompt additions, no new pass

### 1. `agents/investigator.md`

Require findings to mark load-bearing conclusions as **measured** or **inferred**, and require any **inference the plan will build on** to be corroborated by a second independent signal.

In this case four independent signals each settle it — `journalctl --list-boots`, the rootfs birth time, the ZFS creation timestamp, and the hypervisor's task index. **Any one** would have prevented the error. The cost of corroboration was one command; the cost of not corroborating was five plan artifacts and a proposed production restart.

### 2. `agents/red-team.md` — add to *Evaluate*

> **Premise check.** For each finding an epic, gate or success criterion depends on: is it a **measurement** or an **inference**? If inferred, is it corroborated by an independent signal? **What would falsify it, and was that checked?**

The falsification prompt is the highest-value part. *"What one command would prove this wrong?"* is answerable by an investigator in seconds and askable by a reviewer with no domain expertise — which is exactly the property a review-checklist item needs.

## Relationship to #113

Orthogonal, and deliberately separate:

| | #113 (rehearsal pass) | This issue (premise check) |
| :-- | :-- | :-- |
| Axis | structural reachability | factual correctness |
| Catches | tool-before-use, unreachable gate conditions, self-invalidating output | a plan correctly built on a false finding |
| Remedy | new script — topological DAG walk carrying running state | two prompt additions |
| Effort | substantial; may need a `requires:` schema change | small |

Bundling them would delay the cheap fix behind the expensive one.

## Caveat

**n=1** for this specific class, against #113's 4-of-4. The remedy is cheap enough that acting on a single occurrence is defensible — two prompt lines, no new machinery — but it should not displace #113, which has the stronger evidence.

Filed at operator request, splitting the discussion from #113 ([comment](https://github.com/dixson3/yoshiko-flow/issues/113#issuecomment-5276171143)).
