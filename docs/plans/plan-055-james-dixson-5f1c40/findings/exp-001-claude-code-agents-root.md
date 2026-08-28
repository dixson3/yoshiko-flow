---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-claude-code-agents-root
description: Does claude-code read .agents/skills with no additional configuration? (D-4's hinge)
---

# EXP-001 — claude-code against the shared `.agents/skills` root

**Answer: NO.**

## Approach Tested

Two independent axes, both against the installed binary — no docs site consulted.

1. **Static.** The installed CLI is `~/.local/bin/claude` → `~/.local/share/claude/versions/2.1.247`,
   a 222 MB Mach-O arm64 executable with the JS bundle embedded. `claude --version` =
   **`2.1.247 (Claude Code)`**. Raw-byte search (`LC_ALL=C grep -ao`) for `.agents/skills`,
   `agents/skills`, `.agents/`, `.claude/skills`, the skills-root construction, and skill env vars.
2. **Empirical.** A sandbox at `/tmp/zzprobe-9f3a` (outside the repo, removed on completion) holding a
   probe skill in **only** `.agents/skills/zz-probe-agents/` plus a positive control in
   `.claude/skills/zz-probe-claude/`. Ran `claude -p` with cwd = sandbox, twice, with differently
   worded prompts.

## Result

**measured.** `grep -ao '.\{0,40\}\.agents/.\{0,40\}'` over the binary returns **zero matches**. The
string `.agents/` does not occur anywhere in the 222 MB artifact. The only `agents/skills` hits are
unrelated prose — a docs URL and a marketplace-manifest sentence.

**measured.** The skills-directory auto-load constant is hardcoded, verbatim:

```js
jss=[".claude/skills",".claude/commands"]
```

**measured.** The skill-root prefix table enumerates exactly two roots, verbatim:

```js
prefix:"/.claude/skills/"},{dir:F(j(_n(),".claude","skills")),prefix:"~/.claude/skills/"}];
```

(`_n()` = homedir; project-scope entry first, user-scope second.) Skill-root → relative-path
normalization hardcodes `.claude` as well.

**measured.** Headless run, cwd = sandbox, both probes present. Full stdout:

```
zz-probe-claude
```

A second run with a re-worded prompt returned the identical single line. `zz-probe-agents` **never
appeared**. `claude plugin list` from the sandbox emits no `zz-probe` entry; the binary's own label
string is `Skills-directory plugins (.claude/skills/*):` — note the `.claude` glob.

**measured.** **No environment variable can add a skills root.** The complete set of
`CLAUDE_*SKILL*` vars in the binary is ten names, all disable/telemetry switches
(`CLAUDE_CODE_DISABLE_BUNDLED_SKILLS`, `CLAUDE_CODE_SYNC_SKILLS`, …). **None is a path.**

**Q3 (resolution order) is not applicable as posed** — there is no `.claude` vs `.agents` shadowing
question, because only one root family is read.

**Secondary, and relevant to plan design.** An alternate *configured* route exists: plugin manifests
carry a `skills` field that adds arbitrary skill directories
(`if(o?.skills)for(let d of typeof o.skills==="string"?[o.skills]:o.skills)`), fed also by
`--plugin-dir` and marketplace entries. So `.agents/skills` could be **made** visible to claude-code
via a plugin manifest — but that is additional configuration, which this experiment's bound excluded.

## Implications for Plan

- **D-4 resolves to "claude-code KEEPS its private `.claude/skills` root."** The shared-root
  simplification **cannot be made universal**, and the private-root case in `harness_desc.rs` must
  remain.
- **plan-055 does not shrink on this axis.** The deploy matrix stays two-shaped: a shared
  `.agents/skills` root for the harnesses that read it, plus a claude-code-specific `.claude/skills`
  root.
- **The `SKILL_DIR` resolver's dual search is correct and load-bearing**, not redundancy to prune.
  This matters — a plan aiming at "one root" could plausibly have decided to simplify the resolver.
- **Version-scoped.** All three positive signals are bundle internals of **2.1.247**. Re-run if the
  plan lands against a materially later CLI.

## Recommendations

1. Record D-4 as **decided: no**, with this finding as the evidence. Do not open an epic to remove
   the private-root case.
2. **Pin the version in the plan artifact** so a future reader knows the shelf life.
3. If a single universal root is still wanted, the **only** no-fork route measured is the
   plugin-manifest `skills` field pointing at `.agents/skills`. That is a genuinely different design
   — ship a yf plugin manifest rather than copy a tree — and should be scoped as its own decision,
   not folded into D-4. **Untested; treat as a hypothesis.**

## Confidence

- **measured:** the zero-occurrence result for `.agents/` across the whole binary; the `jss` constant;
  the two-entry root prefix table; the `.claude`-hardcoded normalization; the headless probe finding
  the control and not the `.agents` probe, reproduced twice; `plugin list` showing nothing; the
  complete `CLAUDE_*SKILL*` env-var set containing no path variable.
- **inferred:** that **user-scope** `~/.agents/skills` is equally invisible. Corroborated by two
  static signals — the hardcoded `join(homedir(), ".claude", "skills")` root and the total absence of
  any `.agents/` string — but **not measured by a run**.
- **not measured, stated plainly:** the user-scope arm. The sandboxed-`HOME` run was refused by the
  investigator's worktree-isolation guard, and modifying the operator's real `~/.agents` was out of
  scope. A user-scope-only discovery path would have to exist with **no string evidence whatsoever**
  in the binary, which is why the inference is rated strong — but it remains an inference.
- **untested:** the plugin-manifest route (recommendation 3).
