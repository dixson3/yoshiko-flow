---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #337 - yf-research link_normalizer.py build-sources:
  emits non-OKF-conformant sources.md frontmatter, and derives an empty slug (malformed
  YAML) from a relative research_dir'
---
# Upstream #337: yf-research link_normalizer.py build-sources: emits non-OKF-conformant sources.md frontmatter, and derives an empty slug (malformed YAML) from a relative research_dir

- **Number:** 337
- **Title:** yf-research link_normalizer.py build-sources: emits non-OKF-conformant sources.md frontmatter, and derives an empty slug (malformed YAML) from a relative research_dir
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

Two distinct defects in the same command, found packaging research 058.

## Defect 1 — the generator produces a file the conformance checker rejects

`link_normalizer.py build-sources` writes `sources.md` with frontmatter containing only
`title` / `created` / `tags`. `okf.py check` then FAILs the bundle:

```
[error] sources.md: REQ-OKF-003 — missing or empty `type`
[error] sources.md: REQ-OKF-030 — missing `okf_spec` member key
```

**Two yf-research surfaces disagree with each other.** The documented packaging step
(`link_normalizer.py all`) emits a bundle that the repo's own OKF conformance check rejects, so
*every* research bundle that follows the documented procedure inherits a failing check and needs a
hand patch. Worse, the hand patch is **clobbered on any re-run of `build-sources`** — so the repair
is not durable, which makes this a recurring tax rather than a one-time fix.

Fix: `build-sources` should emit `type`, `okf_spec` and `idx` in the frontmatter it generates.

## Defect 2 — a relative `research_dir` yields malformed YAML

Invoked with a relative `.` as the research dir, it derives an **empty topic slug** and writes:

```yaml
tags: [research, , sources]
```

which is malformed YAML. `okf.py` reports it as:

```
malformed frontmatter ... expected the node content, but found
```

Fix: resolve the directory to an absolute path (or fall back to the basename of cwd) before
deriving the slug. An empty slug should be an error at derivation time, not a malformed document
discovered two steps later by a different tool.

## Why these are filed together

Same command, same invocation, both hit on one packaging run — but they are independent and can be
fixed separately. Defect 1 is a contract mismatch between two yf-research surfaces; defect 2 is an
input-validation bug. Neither depends on the other.

## Note on the failure mode

Both defects surface *downstream* of where they originate: the generator writes something invalid,
and a different tool reports it later, in its own vocabulary. A generator that validated its own
output against `okf.py` before writing would have caught both at the source.

