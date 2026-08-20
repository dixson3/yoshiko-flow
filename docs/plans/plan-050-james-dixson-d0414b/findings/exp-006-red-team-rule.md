---
type: Finding
okf_spec: OKF-PLAN
id: exp-006
status: complete
---

# Finding: Where does the red-team read-only rule live, and what is the rewrite's blast radius? (#182)

## Approach Tested

Located the rule text in the repo source and enumerated its deployed copies.

## Result

**measured:** the rule is **one line** — `skills/yf-plan/agents/red-team.md:63`:

> `- Read-only — never writes files. The main session writes reviews/pass-N.md and the phase-log
> review: line at presentation (create-on-present) ...`

Deployed copies present at `~/.claude/skills/yf-plan/agents/red-team.md` and
`~/.agents/skills/yf-plan/agents/red-team.md`.

**inferred, and it narrows #182:** the installed rule says **"never writes files"** — a statement
about *file authorship*, whose actual purpose is REQ-AGENT-043's division of labour (the agent
reviews, the main session writes `pass-N.md`). It does **not** say "may not modify the repository
under review", and it does not forbid a sandbox spike anywhere.

So the prohibition #182 objects to is **not written in the rule at all** — it is the reasonable
reading a reviewer gives to "read-only". The defect is *under*-specification, not a wrong rule:
the line is silent on the one case that matters, and silence reads as prohibition.

## Implications for Plan

This makes the fix smaller and its risk lower than the issue implies. It is not a reversal of an
existing prohibition; it is scoping a broad phrase and adding the missing authorization:

1. Scope the prohibition to what REQ-AGENT-043 actually protects — the repository under review and
   its `pass-N.md` authorship.
2. State explicitly that a spike in a sandbox **is** authorized, with the worked `mktemp -d`
   example already drafted in #182.

Blast radius: one line in one file, plus redeployment. No SPEC requirement changes meaning —
REQ-AGENT-043 is about who writes review artifacts and is untouched.

## Recommendations

- Keep REQ-AGENT-043's authorship rule verbatim; add the scope and the authorization around it.
  Rewriting the authorship clause would be scope creep into the review contract.
- **This fix has no exit code and cannot have one** — it is agent prose. Say so in the plan rather
  than pretending it is mechanically verifiable; the honest check is that the deployed copies match
  the source (a parity check, class M3), not that a reviewer obeyed it.
