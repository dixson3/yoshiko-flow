---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #197: formula aspects: make the classify -> lint -> verify obligation a bead that must be closed, not a paragraph an agent may skip

- **Number:** 197
- **Title:** formula aspects: make the classify -> lint -> verify obligation a bead that must be closed, not a paragraph an agent may skip
- **URL:** 
- **State:** OPEN
- **Labels:** type::feature, priority::medium

## Body

UNVERIFIED PREMISE — stated as such. beads.gascity.com/workflows/formulas lists "Aspects:
cross-cutting transformations applied to matching steps" among formula constructs. It was
NOT confirmed against installed bd 1.1.2, and a companion issue records that this docs
site already describes at least two dependency types the installed binary lacks. FIRST
STEP for anyone taking this up is to confirm aspects exist at all (`bd formula show` /
`bd cook --dry-run` against an aspect-bearing formula). If they do not, close this.

THE GAP, which is real regardless. Several always-loaded rules describe a uniform
per-artifact verification obligation executed purely by agent discipline:

- doc_lint: classify -> lint -> resolve every E finding, on any edit under the typed roots
- yf-change-validation: FAST tier on any path matching an approved manifest's §3 globs
- yf-drift-check: report-only dispatch on any path matching an approved manifest's §6 globs

Each is a paragraph. None is a thing that must be CLOSED.

EVIDENCE THAT THE PARAGRAPH FORM FAILS. plan-050 RE-006: a retrospective append reported
exit 0, the file was never re-read, and the Issue 0.2 commit message asserted "Recorded as
RE-002" — a claim wrong on both the fact AND the id. The append had not landed. Detected
only because the operator asked for the entry to EXIST with evidence rather than be
mentioned. A verification bead is a thing that must be closed; a prose instruction is a
thing that can be believed to have been followed.

PROPOSAL. If aspects exist: attach a `verify` child to every plan-execute step whose
declared output matches a glob, so the verification obligation is a bead in the DAG
rather than a rule an agent is trusted to have honored. If aspects do not exist, the same
effect is reachable at injection time in SKILL.md §4.3 — at higher cost and with the
obligation still expressed in a script rather than the formula.

RELATED. #165 (SPEC Verification: lines are prose shaped like commands) is the same
defect one layer up: an obligation written in a form nothing runs.
