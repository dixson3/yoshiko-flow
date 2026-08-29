---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #247 - Drift findings no edge covers: the manifest''s
  own diagram is 22 edges stale, and install.sh/install.py do not exist'
---
# Upstream #247: Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist

- **Number:** 247
- **Title:** Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

plan-054's full 52-edge drift sweep surfaced findings that **no declared edge covers**. Each is
a gap in the manifest itself, not a failing edge.

### 1. The manifest's own diagram is 22 edges out of date

`docs/diagrams/drift-check-artifact-graph.d2` declares **30** edges; `DRIFT-CHECK.md` declares
**52**. Absent: all 14 vendored-copy edges, plan-054's two new edges and their three nodes,
`e-doclint-spec`, and the `e-okf-*` / `e-skill-page-*` families. It also still draws
`e-status-values → agent`, which plan-053 D-6 **replaced** with `status-restatement`.

`e-docs-diagram-fresh` correctly PASSES — the PNG is a faithful render of the stale `.d2`. The
point is that **nothing binds `DRIFT-CHECK.md → docs-diagram-src`**, so the manifest's own claim
at `:15-18` ("The graph **this manifest declares** … rendered") is unchecked and currently false.

**Suggested edge:** `DRIFT-CHECK.md` (source) → `drift-check-artifact-graph.d2` (derived),
`field-set-equal` over the edge-id set.

### 2. `install.sh` / `install.py` do not exist, and 17 READMEs reference them

There is no repo-root `install.sh` and no `install.py`. Yet **17** skill READMEs say "Installed
by the repo-level `install.sh` / `install.py`" — 9 of them naming `install.py`, which
`yf/src/parity.rs:2` calls "the retired `install.py`". The root `README.md:39` `install.sh` is
the *hosted vendor* installer, a different thing.

Worse: **`DRIFT-CHECK.md` §5 itself names "repo-level `install.sh` reference" as the required
source** for the mandatory Install section — the same stale-authority class the manifest's own
preamble was written to correct for `check-prereqs.sh`.

### 3. `REQ-YF-TUNE-030` says "every harness profile"; 1 of 3 carries it

`opencode.json` declares `settings_read_layers`; `claude-code.json` and `codex.json` do not.
`profile.rs` makes the field `#[serde(default)]` with a `read_layers()` fallback to
`[settings_filename]` — a deliberate and reasonable design that keeps undeclared profiles on
today's behaviour, but it does not match "**shall carry**".

Either amend the REQ to "shall declare, defaulting to the single write target", or populate all
three. **No manifest edge covers `SPEC.md ↔ yf/profiles/` or `SPEC.md ↔ yf/src/`** — that is the
underlying gap.

### 4. `web/content/pages/formulas.md` teaches the wrong TOML syntax

Says "A `[[var]]` block…" / "A `[[step]]` block…"; the shipped formulas use `[vars.<name>]` and
`[[steps]]` (`plan-execute.formula.toml:7,11,16`). Outside `e-web-formula-set`'s contract, which
covers the formula **set and count** only.

### 5. `skills/yf-beads-authoring/SKILL.md:398` references a non-existent agent

"Load `${SKILL_DIR}/agents/coordinator.md`" — `agents/` holds only `reviewer.md`. It sits inside
an **authoring template** (the `coordinate` subcommand a skill author writes), so `${SKILL_DIR}`
expands in the *authored* skill. Read literally the `e-agent-ref` contract fails; read in context
it passes. Worth an explicit carve-out in the contract so the next reader does not re-litigate it.

### 6. `skills/yf-markdown-format/README.md` calls it "the autofix side of `markdown-lint`"

Stale unprefixed skill name.

Discovered by plan-054's release-readiness drift sweep.

