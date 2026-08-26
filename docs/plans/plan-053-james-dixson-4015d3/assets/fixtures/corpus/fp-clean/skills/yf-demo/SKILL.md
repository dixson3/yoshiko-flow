---
name: yf-demo
description: A false-positive fixture tree for check_skill_script_refs. Every construct here is one the checker must NOT flag.
---

# yf-demo

This document exists to hold, in one place, every shape that a naive grep for `_shared/`
would flag and that the checker must return **zero** violations on. It is the fixture behind
EXP-003's "false-positive surface, measured to zero".

## 1-5. Prose mentions of `_shared/` — five of them, none an invocation

The vendored copy is kept byte-identical to the canonical `_shared/plan_extract.py` by
`_shared/sync.py`. Anything under `_shared/` is repository-internal. A path in `_shared/`
resolves in this working tree and nowhere else. The `_shared/` directory is not on the
install path.

**plan-050's own note, verbatim** — the single most important false positive, because it is
the note *explaining this very defect*, and a grep-based checker flags the document that
documents the bug:

> **The path is `${SKILL_DIR}/scripts/`, not `_shared/`** (plan-050 Issue 7.3). `_shared/` is
> a path inside *this repository*; the `SKILL_DIR` resolver's six roots do not include it, so
> an operator following the old line verbatim in any other repo got a file-not-found.

## 6. A NON-SHELL fence containing an invocation-shaped line

A ```python fence is a code listing, not a command listing. The line below is a Python
comment that happens to read like a shell command, and it must not be extracted:

```python
# uv run _shared/plan_extract.py "$d" --json
def main() -> int:
    return 0
```

## 7. A deliberately-external reference, ALLOW-MARKED

The marker is explicit. An inferred exemption is indistinguishable from an oversight, so the
opt-out is always stated:

<!-- skill-script-refs: allow the obsidian-lint skill is deliberately external and this repo does not ship it -->
`uv run .agents/skills/obsidian-lint/scripts/obsidian-autofix.py Incubator/<kebab>`

## 8. A legitimate, resolvable invocation

This one is real and must classify `ok` — the fixture would be vacuous if it contained no
invocation at all:

```bash
uv run ${SKILL_DIR}/scripts/demo.py --check
```
