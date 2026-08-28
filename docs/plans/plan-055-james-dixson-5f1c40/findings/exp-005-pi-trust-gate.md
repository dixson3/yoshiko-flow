---
type: Finding
okf_spec: OKF-PLAN
id: exp-005-pi-trust-gate
description: What pi does with a skills bundle in an untrusted project directory (#239)
---

# EXP-005 — pi's project-trust gate (#239)

## Approach Tested

pi **0.84.3**, measured two ways:

1. **Static read of the installed bundle** (`dist/bundle/chunks/chunk-E5KXRMZK.js`) — the trust
   resolver, the skills-root collector, the prompt strings, and the trust store class.
2. **Live sandbox spike** — fake `HOME`, a fresh project dir with three canary skills, and a global
   `models.json` pointing an OpenAI-compatible provider at a **local capture server** that logs the
   request body. Grepping the captured **system prompt** for each canary name is a direct read of
   which skills pi actually loaded. `env -i` isolation, `PI_OFFLINE=1`, no interactive prompts driven.
   The real `~/.pi/agent/trust.json` never existed before or after.

## Result

### 1. What loads in an untrusted project

| Arm | `~/.agents/skills` (user) | `<proj>/.agents/skills` | `<proj>/.pi/skills` |
| :-- | --: | --: | --: |
| untrusted (default, headless) | **4** | 0 | 0 |
| `--approve` | 4 | **4** | **4** |
| saved trust on **parent** dir | 4 | 4 | 4 |
| `--no-approve` (overriding saved trust) | 4 | 0 | 0 |
| `trust.json` = `false` | 4 | 0 | 0 |
| `defaultProjectTrust: "always"` | 4 | 4 | 4 |

(counts = occurrences of each canary's description in the captured system prompt)

**measured.** **User-scope skills load unconditionally, regardless of trust.** Both user roots are
added *outside* the trust branch in `SettingsManager`'s resolver — `~/.pi/agent/skills` and
`$HOME/.agents/skills` alike. Project scope is gated:
`projectAgentsSkillDirs = projectTrusted ? collectAncestorAgentsSkillDirs(cwd).filter(…) : []`.

### 2. Is the failure observable? — the sharp answer to #239

**measured.** In **headless** (`--print`) and **`--mode json`**: **nothing**. Zero stderr output, no
trust-related token anywhere in stdout, exit 0, and no `trust` string in the captured system prompt.
The `--mode json` event stream carries no diagnostic event. **#239's worry is confirmed for
non-interactive pi** — a project skill that failed to load is indistinguishable from one that loaded
and had nothing to say.

In the **interactive TUI** it *is* observable, verbatim:

> `This project is not trusted. Project .pi resources and packages are ignored. Use /trust to save a
> trust decision, then restart pi.`

**inferred.** The warning names only `.pi` resources — it does **not** mention `.agents/skills`,
which is also being skipped. So it is partially misleading even where it fires. Single-source
(the bundle string); uncorroborated.

### 3. The trust prompt, verbatim

```
Trust project folder?
${cwd}

This allows pi to load .pi settings and resources, install missing project packages, and execute project extensions.
```

Options: `Trust` · `Trust parent folder (<path>)` · `Trust (this session only)` · `Do not trust` ·
`Do not trust (this session only)`. No prompt was driven interactively.

### 4. Persistence

**measured.** `ProjectTrustStore` → **`$HOME/.pi/agent/trust.json`** (overridable by
`PI_CODING_AGENT_DIR`). A flat JSON object, canonicalized absolute dir path → `true` | `false`
(`null` deletes), read under a file lock. Lookup is **nearest-ancestor** — verified live: a `true`
entry on the sandbox *parent* trusted the child project.

### 5. Headless behaviour

**measured.** `resolveProjectTrusted` ends with `if (!options.projectTrustContext.hasUI) return !1`.
Non-interactive pi **proceeds untrusted** — it does not refuse, hang, or prompt, and the exit code is
unaffected. Full precedence, measured end to end: `--approve`/`--no-approve` → a `project_trust`
extension event → saved `trust.json` (nearest ancestor) → `defaultProjectTrust` → prompt if UI, else
`false`.

### 6. What counts as "trust-requiring"

**measured** (`hasTrustRequiringProjectResources`): any of
`<cwd>/.pi/{settings.json,extensions,skills,prompts,themes,SYSTEM.md,APPEND_SYSTEM.md}`, **or** a
`.agents/skills` dir in cwd or **any ancestor** (excluding `$HOME/.agents/skills`). A bare `.pi/`
does not count. With none present, `resolveProjectTrusted` returns `true` immediately and no prompt
ever fires.

**inferred (edge case).** The two walks disagree on their stop condition:
`hasTrustRequiringProjectResources` walks to the filesystem **root**, while
`collectAncestorAgentsSkillDirs` stops at the **git repo root**. So a `.agents/skills` directory
*above* a repo root triggers the trust prompt but is never loaded even when trusted. Not constructed
live; uncorroborated.

### 7. Current-machine state

**measured.** `/Users/james/.pi/agent/trust.json` does not exist — no trust decision has been made.
`<repo>/.agents/skills` does not exist and the repo has no `.pi/` resources, so **pi in this repo is
currently not trust-requiring at all** and will not prompt.

## Implications for Plan

- **The trust gate does not threaten plan-055's core move.** `~/.pi/agent/skills` → `~/.agents/skills`
  stays on the trust-independent side of the branch in **every** measured arm, including
  `--no-approve` and `trust.json: false`. The gate was never a precondition for user-scope loading.
- **It does threaten project-scope deployment.** Today this repo has no `<repo>/.agents/skills` — but
  the moment yf creates one, **pi starts prompting for trust in that repo**, and in headless mode
  silently drops those skills. That is a behaviour change *caused by yf*, in a directory *yf creates*.
  This is a direct, measured cost of D-3's both-scopes decision and belongs in the plan's risk table.
- **#239's premise is confirmed but narrower than filed:** the silent-failure mode is real and total
  in `-p` / `--mode json` / `--mode rpc`, and does not apply to user scope at all.
- A `yf doctor` axis is **cheap and purely local** — read `trust.json`, apply nearest-ancestor lookup
  against the repo path, cross it with the trust-requiring resource list. No pi invocation, no network.

## Recommendations

1. **Do not block plan-055 on the trust gate.** The user-scope move is measurably trust-independent.
2. **Make it a `yf doctor` axis, not a harness-smoke state**, scoped to *"this repo has
   trust-requiring project resources AND no applicable trust decision"*. A smoke state would mislead:
   a user-scope smoke passes under an untrusted project and proves nothing about the gate.
3. **Guard the project-scope deployment path.** When yf writes `<repo>/.agents/skills`, warn that it
   makes the repo trust-requiring for pi, and point at `pi --approve` / `/trust`.
4. **Pass `--approve` explicitly in any yf-driven headless pi invocation** — the headless default is a
   silent `false`.
5. **Document the caveat with the exact strings above**, including that the TUI warning omits
   `.agents/skills`. That omission is the most likely way an operator misdiagnoses a missing skill.

## Confidence

- **measured:** the six-arm load table; user-scope roots being added outside the trust branch; the
  total absence of any diagnostic in headless/json modes; the verbatim trust prompt and its options;
  `trust.json`'s path, format and nearest-ancestor lookup (verified live via a parent-dir entry);
  the headless `return !1` and the full precedence chain; the trust-requiring resource list; the
  current machine having no `trust.json` and this repo not being trust-requiring.
- **inferred:** that the user-root move is trust-neutral (read from the resolver's branch structure,
  corroborated by the canary counts holding at 4 in every arm); that the TUI warning's `.pi`-only
  wording is misleading (single bundle string).
- **uncorroborated:** the above-repo-root `.agents/skills` edge case — the layout was not constructed.

## Residue

The sandbox lives under the session scratchpad; the investigator's `rm -rf` was denied by the
permission layer, so it awaits one manual removal. The repository was never written to, and no real
`~/.pi` state was created.
