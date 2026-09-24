---
type: Finding
okf_spec: OKF-PLAN
id: exp-004
description: Claude Code's skill-listing budget is already exceeded on the operator's machine (33313 chars vs a 30000 budget); yf descriptions are about half of it
status: complete
created: '2026-09-24'
---
# EXP-004: Claude Code skill-listing budget

## Approach Tested

`claude -p "Reply ok." --debug-file /tmp/cc-dbg.log` (Claude Code 2.1.282, Opus 5.5 with a 1M
context), run from the scratch clone with the operator's real global config and no
`skillListingBudgetFraction` / `skillListingMaxDescChars` / `skillOverrides` set. This
replaces the pilot's model self-report, which was weak evidence, with the harness's own log
line.

## Result

**measured:** debug log line 236:

```text
[WARN] Skill listing over budget: 50 skills, 33313 chars > 30000 budget — descriptions will be truncated.
```

**measured:** the 20 yf skills contribute 16,898 chars (name + description) of that 33,313, which is 51%.

## Implications for Plan

1. **The budget matters on Claude Code today.** The listing is 3,313 chars over. The yf corpus
   is half the listing, and the five over-cap skills alone are 6,172 chars. Trimming yf
   descriptions toward 600 is the change that brings the listing under budget on this
   machine. It's also measurable, since the WARN line either appears or it doesn't.
2. **Which descriptions get dropped depends on the machine.** Per anthropics/claude-code#81081,
   CC drops descriptions starting with the least-used skills. So an eval run on one machine can
   see a description that another machine's listing dropped. The eval must record whether this
   WARN fired for the run, or a CC pass can't be interpreted.
3. **The 30000 budget is ~3% of the 980K effective window**, not the documented 1%. This is
   **inferred:** from the numbers. It doesn't change the plan, but it's a reason to read the
   budget from the log rather than compute it.

## Recommendations

- Add a success criterion: after the trims and redeploy, the CC debug log shows no
  `Skill listing over budget` line on the operator's machine. Scope it to that machine, since
  other installs carry other skills.
- The eval harness captures this line per CC run, via `--debug-file`, next to the activation
  result.
