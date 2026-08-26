---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #210: pour_fidelity.py is not shipped to the skill dir — SKILL.md 6.4's completion fidelity gate is unrunnable in every repo but this one

- **Number:** 210
- **Title:** pour_fidelity.py is not shipped to the skill dir — SKILL.md 6.4's completion fidelity gate is unrunnable in every repo but this one
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/210
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

## Summary

`SKILL.md` §6.4 runs the completion pour-fidelity gate as:

```bash
FIDELITY=$(uv run _shared/pour_fidelity.py /tmp/yf-beads.json "${plan_dir}" --strict --plan "${plan_id}")
```

`_shared/` is a path inside **this repository**, not inside an installed skill. `pour_fidelity.py` is not shipped to the skill directory, so **in any repo other than `dixson3/yoshiko-flow` the §6.4 fidelity gate cannot run at all.**

This is exactly the defect class **plan-050 Issue 7.3** fixed for `plan_extract.py` — `SKILL.md` was corrected to `${SKILL_DIR}/scripts/` with the note that *"`_shared/` is a path inside this repository; the SKILL_DIR resolver's six roots do not include it, so an operator following the old line verbatim in any other repo got a file-not-found."* `pour_fidelity.py` has the same problem and was not covered by that fix.

## Measured

In `dixson3/astrospike` at plan-001 completion:

```
$ uv run /Users/james/.claude/skills/yf-plan/scripts/pour_fidelity.py ...
error: Failed to spawn: '.../scripts/pour_fidelity.py'
  Caused by: No such file or directory (os error 2)
RC=2

$ find /Users/james/.claude/skills/yf-plan -name pour_fidelity.py
(no output)
```

Independently confirmed from a second session:

```
$ find ~/.claude ~/.agents /opt/homebrew -name 'pour_fidelity*'
(no output)

$ grep -n 'pour_fidelity' ~/.claude/skills/yf-plan/SKILL.md
1549:FIDELITY=$(uv run _shared/pour_fidelity.py /tmp/yf-beads.json "${plan_dir}" \
```

The only copies on the machine are inside the yoshiko-flow working copy (`_shared/pour_fidelity.py`) and a plan-047 asset dir.

## Impact: a HALTING gate silently becomes a no-op

This is worse than an unavailable convenience, for three reasons.

1. **It fails in the direction of false confidence.** An executor that treats the missing instrument as "nothing to report" records a completion as fidelity-checked when nothing checked it.
2. **Either reading of exit 2 is wrong.** Read as failure, it halts a legitimate completion. Read as success, it passes an unverified one. There is no correct handling of a gate that cannot run.
3. **This gate is the specific control that would have caught #186 and #187.** In this repo, plan-001's first pour produced 35 of 35 beads with empty descriptions and masked titles, and execution proceeded until a human noticed. §6.4 exists to catch precisely that, and it has never been able to run outside this repo.

## Suggested fix

Ship `pour_fidelity.py` to the skill's `scripts/` directory alongside `plan_extract.py`, and correct `SKILL.md:1549` to `${SKILL_DIR}/scripts/pour_fidelity.py` — the same one-line change plan-050 Issue 7.3 made for the extractor.

Worth a sweep for the general case rather than a third one-off: **grep `SKILL.md` for every `_shared/` invocation** and confirm each names a file that is actually installed. A test asserting that every script path referenced in `SKILL.md` resolves under `SKILL_DIR` would close the class permanently. This is now the second instance of it.

## Workaround used

Rather than treat a missing instrument as a pass, the equivalent check was run by hand and the gate recorded as **INCONCLUSIVE, not PASS**:

```
plan issues: 35   beads mapped: 35
issues with NO bead: NONE
beads with NO issue: NONE
declared edges: 53   present: 53
edges DROPPED: NONE
edges EXTRA:   NONE
```

(Re-derived independently by a second session with its own parser; both agree.)

Note for whoever writes the fix: bead ids are **positional**, not plan issue ids — lettered issues (`1.2a`, `4.3a`) shift every bead after them, so bead `…8dq.1.9` is titled *"Issue 1.8"*. A fidelity comparator must map beads to issues by the `Issue N.M:` title prefix, not by the numeric id suffix. Mapping by suffix produces a confident, entirely wrong "12 edges missing" result — measured.

## Context

Found in `dixson3/astrospike` plan-001. Related: #206, #207, #208, #209 from the same plan; #186 / #187 are the defects this gate would have caught.

