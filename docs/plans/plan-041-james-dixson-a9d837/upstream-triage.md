---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: Fix stale embedded skills tree in yf self install --from-build (#137)

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

Triage complete — 2 issues reviewed, 1 include, 1 exclude.

## #137 — yf self install --from-build can promote a binary with a STALE embedded skills tree (release profile, incremental rebuild)

> ## Summary

`yf self install --from-build --build` defaults to `--release`. A **release** incremental rebuild does not observe changes under `skills/`, because that tree lives outside the `yf/` packag...

**Disposition:** include

**Notes:** The plan's whole subject; resolved by Issue 1.1 (`resolves-upstream: #137`).

Investigation **partially refuted the issue's own root-cause analysis**, so the fix differs
from every direction the issue proposes:

- The issue says an incremental release rebuild "does not observe changes under `skills/`".
  Measured (E2, E3): modifications and deletions **are** observed; only **additions** are
  missed, because `rust-embed` is a proc macro that emits no `rerun-if-changed` and
  `include_bytes!` dep-info tracks file *content*, never the *directory listing*.
- The issue conflates two defects. Its `5c747c0-dirty` evidence is **version-stamp**
  staleness (which occurs on every skills-only change), not **embed** staleness (additions
  only).
- **Direction 1 as written is not implementable** — the proposed `rerun-if-changed=../skills`
  "in addition to the existing no-narrowing behavior" is not something cargo permits;
  emitting any `rerun-if-changed` disables the implicit whole-package watch. Measured to
  regress the REQ-YF-PRE-009 dirty flag.
- **Direction 1 repaired is adopted** (D1, D2): `rerun-if-changed=../skills` **plus**
  `rerun-if-changed=.`. The second line restores the package watch and is what makes the
  first safe.
- **Direction 2** (`--build` forces the re-embed) was initially selected, then superseded on
  evidence (D1) — it fixes only the `self install` path, leaving bare `cargo build --release`
  and CI broken.
- **Direction 3** (fail-loud post-promote hash comparison) declined by the operator; see
  Scope → Out of scope. E1 confirms nothing exists to reuse.

Issue 4.4 posts this correction upstream so the rejected one-liner is not retried later.

## #41 — yf-owned `_shared/`: make yf the install-time vendoring engine (embed `_shared/`, fan into consumers)

> Proposes making `yf` the install-time vendoring engine for shared Python helpers by
> embedding `_shared/` and fanning it into consumer skills at deploy time.

**Disposition:** exclude

**Notes:** Adjacent — it touches the same `rust-embed` embedding machinery this plan edits —
but it is a separate design decision, and is paired with **#40** (PEP-723 micro-package
route) as a **competing alternative**. Choosing between #40 and #41 is a prerequisite that
this plan does not undertake and does not need: the `build.rs` fix in Epic 1 is agnostic to
which vendoring model wins, and in fact benefits either (a `_shared/` fan-out would add files
under `skills/`, i.e. exactly the **addition** case Epic 1 fixes). Not resolved here.
