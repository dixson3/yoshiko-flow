---
type: Reference
okf_spec: OKF-PLAN
id: red-prework
description: Append-only red->green observation log written by assets/redcheck.sh (Issue 0.2)
---

# Red-prework record

Append-only observation log written by `assets/redcheck.sh` (Issue 0.2). One line per
observation. The gate `verify-all` reads THIS FILE and `assets/controls.txt`; nothing else.

Record schema, comma-separated, in this order:

    verb, control, fixture, exit-code, command, utc, git-describe

`git-describe` is recorded FOR DIAGNOSIS ONLY. It makes no ordering claim: pass-7 C69
measured that check vacuous, because nothing requires the fix to be committed before
`assert-distinguishes` runs. The ordering "RED was observed before the fix landed" is carried
by the plan's `depends-on` edges, not by this file.

## Observations

record-red, ctl-182-spike, assets/fixtures/ctl-182-spike.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-051-james-dixson-2f499f bash assets/fixtures/ctl-182-spike.sh`, 2026-08-23T17:30:27Z, v0.4.0-336-g2d9e7ff

### `ctl-182-spike` — guard spike (Issue 1.1)

The fixture's own guards were spiked in a `$(mktemp -d)` before the RED was recorded (sandbox
removed, no residue). Five arms:

| Arm | Scenario | Expected | Observed |
| :-- | :-- | --: | --: |
| G1 | a double-quote character inside a literal — `pairs-found` 1 vs `grep -qF` count 2 | 2 (INCONCLUSIVE) | **2** |
| G2 | zero `grep -qF` pairs in the line | 1 (FAILURE, never a vacuous pass) | **1** |
| G3 | the line names a path that does not exist | 2 | **2** |
| G4 | fully fixed tree | 0 | **0** |
| G5 | **the dangling state** — spec retargeted, agent file not reworded (EXP-002's case) | 1 | **1** |

**G4 and G5 together are SC3's two required arms**, run on a throwaway tree: the fixed state
passes and the dangling state fails. One arm alone would be satisfied by a control that is
unconditionally non-zero, which is exactly what the plan specified before pass-1 C2. EXP-002
measured the FAST tier returning `pass, first_failure None` on the G5 state, so a criterion
resting on the tier alone would pass a broken tree.

The in-fixture self-check also reported `2 literal(s) greppable against a hand-fixed copy`
before the RED was accepted — three separate reviewers produced a false RED without that step.
assert-distinguishes, ctl-182-spike, assets/fixtures/ctl-182-spike.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-051-james-dixson-2f499f bash assets/fixtures/ctl-182-spike.sh`, 2026-08-23T17:34:28Z, v0.4.0-337-gf622b91-dirty

### `ctl-184-dispatch` — gaming spike (Issue 2.1)

R2 states the risk plainly: **a text-presence control is in principle gameable by the token it
checks for.** The five arms below were run in a `$(mktemp -d)` before the RED was recorded
(sandbox removed, no residue). The two gaming vectors are the ones pass-1 C8 measured green
against a bare-token check.

| Arm | `### Review` section contains | Expected | Observed |
| :-- | :-- | --: | --: |
| V1 | `<!-- Agent -->` — a commented-out token | 1 | **1** |
| V2 | `Do NOT use the Agent tool here.` — a **prohibition** | 1 | **1** |
| V3 | `The Agent is mentioned.` — a bare token, no dispatch form | 1 | **1** |
| V4 | `Spawn a sub-agent (\`Agent\`) that reads \`${SKILL_DIR}/agents/red-team.md\`.` | 0 | **0** |
| V5 | no `### Review` heading at all | 2 | **2** |

**The whole-file trap, measured rather than asserted.** On the un-fixed tree:

| Form | Exit | Verdict |
| :-- | --: | :-- |
| `grep -q 'Agent' skills/yf-plan/SKILL.md` (whole file) | **0** | ships **unable to fail** — `Agent` is at `SKILL.md:21` in the frontmatter `allowed-tools:` list |
| this fixture, section-scoped to `### Review` (lines 484–543) | **1** | distinguishes |

**What the control does not claim (R3).** It is a claim about the TEXT, not about conduct.
That a reviewer actually obeyed the rule has no exit code, and nothing here pretends otherwise.
record-red, ctl-184-dispatch, assets/fixtures/ctl-184-dispatch.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-051-james-dixson-2f499f bash assets/fixtures/ctl-184-dispatch.sh`, 2026-08-23T17:37:04Z, v0.4.0-339-gb6857db
assert-distinguishes, ctl-184-dispatch, assets/fixtures/ctl-184-dispatch.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-051-james-dixson-2f499f bash assets/fixtures/ctl-184-dispatch.sh`, 2026-08-23T17:37:58Z, v0.4.0-340-g3ace676

### `ctl-165-executable` — guard spike and the RED's cause (Issue 3.1)

Six arms in a `$(mktemp -d)` (removed, no residue):

| Arm | `Verification:` value | Expected | Observed |
| :-- | :-- | --: | --: |
| W1 | prose — `red-team.md Rules: "Read-only" + the SKILL.md section.` (**the #165 defect itself**) | 1 | **1** |
| W2 | prose **with inline code spans** — looks like a command | 1 | **1** |
| W3 | a whole-line command that exits non-zero — `` `false` `` | 1 | **1** |
| W4 | a whole-line command that exits 0 — `` `true` `` | 0 | **0** |
| W5 | a REQ with no `Verification:` line at all | 2 | **2** |
| W6 | only **two** of the three REQs present — the vacuity guard | 2 | **2** |

W2 is the arm that matters for shape: an inner backtick means the value is *prose containing
code spans*, not a single command, and is rejected.

#### Which of the two declared causes is live — measured, not assumed

Issue 3.1 declares the RED has **two independent causes**: the named test does not exist, **and**
the retargeted 043/045 commands grep for phrases the agent files do not carry until 1.2/1.2a.
An earlier draft claimed the RED came *solely* from the missing test; pass 3 measured that false
**in the plan's own favour**, which is the direction that matters. So it is measured here rather
than asserted:

| Cause | Check | Result |
| :-- | :-- | :-- |
| 1 — the named test is absent | `ls skills/yf-plan/scripts/test_review_agent_contract.py` | **absent** → each command exits **2** |
| 2 — the grep conjuncts | run verbatim from the tree root, all three REQs | **exit 0** — already satisfied |
| 2 — the same grep at `main` | `git show main:…/red-team.md \| grep -qF 'A sandbox spike is authorized'` | **exit 1** — it *was* a live cause on the pre-plan tree |

**In this execution order the RED comes from cause 1 alone**, because Epic 1 landed before
Epic 3 rather than concurrently. Cause 2 was real and is demonstrated against `main`; it was
discharged by 1.2/1.2a before this fixture first ran. Recording which cause was live — rather
than repeating the plan's two-cause sentence unexamined — is the point of D-5.

**The limitation stands.** Because Issue 0.1 already fixed the line's SHAPE, this control never
observes the *"prose shaped like a command"* defect #165 names in the wild; W1/W2 above
demonstrate it *could*, on a synthetic tree. And the redundancy caveat holds: with the two
amended REQs' lines being Epic 1's and Epic 2's assertions, this control green ⟺ those green,
plus the one added property that **the line parses as a command and runs**.
record-red, ctl-165-executable, assets/fixtures/ctl-165-executable.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-051-james-dixson-2f499f bash assets/fixtures/ctl-165-executable.sh`, 2026-08-23T17:40:54Z, v0.4.0-341-g6f92ef2
assert-distinguishes, ctl-165-executable, assets/fixtures/ctl-165-executable.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-051-james-dixson-2f499f bash assets/fixtures/ctl-165-executable.sh`, 2026-08-23T17:46:38Z, v0.4.0-343-gf8d9e00
