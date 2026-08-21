---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #179: yf-plan: the start-gate wrapper task is orphaned at pour and blocks cascade-close

- **Number:** 179
- **Title:** yf-plan: the start-gate wrapper task is orphaned at pour and blocks cascade-close
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The start-gate wrapper task is orphaned at pour, and blocks cascade-close

`SKILL.md` §5.2a pours a gate-type formula step that yields **two** beads: a task wrapper
(`plan-execute.start-gate`, what downstream tasks `--deps` reference) and the real gate
(`plan-execute.gate-start-gate`, what `bd gate resolve` targets).

At execute start the skill resolves the **gate**. **Nothing ever closes the wrapper task.** It stays
open for the whole run, and at §6.4 `close_cascade.py` correctly refuses to close a container with a
non-terminal child — so completion halts on a bead the pour created and the skill never closes.

### Measured

plan-048 hit exactly this. Its executor had to close `yf-mol-d92` by hand before cascade-close would
pass, and recorded it as a yf-plan pour-lifecycle gap. This will recur on **every** plan, because the
wrapper is created unconditionally by the formula.

### Proposed fix

Close the wrapper task in the same atomic step that resolves the gate (§5.2a), or teach
`close_cascade.py` to treat a start-gate wrapper whose paired `gate-*` bead is resolved as terminal.
The first is simpler and keeps the cascade's "an unsatisfied gate is a genuine open child" rule
intact.

### Related

- plan-048 `plan-retrospective.md`
- `skills/yf-plan/scripts/close_cascade.py`

