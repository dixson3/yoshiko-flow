---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-pilot
description: Pilot of observing skill activation on pi and claude-code via herdr tabs; one intent, feasibility only
status: preliminary
created: '2026-09-24'
---
# EXP-001 (pilot): observing skill activation via herdr-managed interactive sessions

**Status:** preliminary. One intent, one run per harness. It checks feasibility and says nothing about fidelity.

## Approach Tested

- herdr 0.9.1, workspace `w1G`. Two new tabs, each started with `herdr agent start` in the repo cwd,
  using the operator's **real** installed skill set (no sandboxed `HOME`):
  - `cc-eval`: `--kind claude`, Claude Code 2.1.282, Opus 5.5, pane `w1G:p2`
  - `pi-eval`: `--kind pi`, pi 0.87.1, `cliproxyapi/claude-opus-5-5`, pane `w1G:p3`
- Intent (should trigger `yf-drift-check`):
  "I just changed the wording of a requirement in SPEC.md. Does the implementation and the docs
  still agree with it?"

## Result

| Harness | Activated yf-drift-check? | Evidence |
| :-- | :-- | :-- |
| pi | **yes** | session JSONL: first tool call `read ~/.agents/skills/yf-drift-check/SKILL.md` |
| claude-code | **no Skill tool call** | session JSONL: three `Bash` calls, no `Skill` tool_use. But its reply says "The repo does have an approved DRIFT-CHECK.md, so the check is ready to run", so it clearly routed toward drift-check |

**measured:** pi read `yf-drift-check/SKILL.md` as its first tool call. CC made 3 `Bash` calls and no `Skill` call (both from session JSONL).

## Implications for Plan

1. **The Claude Code result is ambiguous, not a miss.** No change existed in the tree, so CC
   investigated first and would presumably have invoked the skill after finding the edit. "Skill
   tool_use present" is the precise signal, but it undercounts routing when the intent's
   precondition isn't met. **Implication:** eval intents need a fixture state in which the
   precondition holds (here, a real SPEC.md edit in a scratch clone), or the metric has to be
   "first-action routing", scored some other way.
2. **pi warns about the five over-cap skills at startup and still loads them.** The `[Skill
   conflicts]` block lists exactly the five from #407 with the same counts. `yf-drift-check`
   (1325) triggered anyway, so on pi 0.87.1 the cap produces a warning but doesn't truncate.
3. **Reading the session transcripts is a reliable detector.** CC:
   `~/.claude/projects/<cwd-slug>/<session-id>.jsonl` `tool_use` entries. pi: the session file
   herdr reports in `agent_session.value`, `toolCall` entries. Scraping the screen with `pane
   wait-output` works for pi but is fragile.
4. **Isolation:** both sessions ran in the live repo with the operator's full global config
   (hooks, context-mode, pi-lens, 50 CC skills). That's realistic (see EXP-004), but it isn't
   reproducible across machines. Whether the eval should run under a sandboxed `HOME` is still
   open.

**inferred:** CC's routing toward drift-check comes from its reply text, not from a tool call.

## EXP-004 side observation (CC listing budget)

Asked with tools disallowed, CC reported 50 skills listed, with all six probed yf skills
carrying description text, and 5 name-only (`anthropic-skills:docx`, `import-memory`, `pdf`,
`pptx`, `xlsx`). **This is weak evidence.** It's the model reporting on its own context, which
GitHub issue anthropics/claude-code#81081 shows can be checked but is not proof. It suggests
the listing budget is already being exceeded on this machine and that yf descriptions currently
survive. Confirm by reading the request body or `/doctor`, not by asking the model.

## Recommendations

Run the full EXP-001 with fixture-state intents and read activation from the transcripts. Open questions:

- Fixture-state intents (scratch clone per intent) vs. first-action scoring.
- Per-intent session reset: `/clear` on CC, and a fresh session on pi.
- Headless `-p` vs herdr-interactive: herdr gives a manageable, observable session. `-p` is
  cheaper to script. Measure both in EXP-002.
