# exp-002 — yf preflight/doctor per-skill dependency axis

**Issue:** 4.2 (Epic 4) · **Date:** 2026-07-15 · **Method:** code read of `yf/src/`

## Question

Confirm whether `yf preflight` already enforces a skill's `depends-on-tool`, and scope
whether `yf doctor` should gain a per-skill dependency axis (shape, slot, worth-it).

## Findings

### preflight already enforces `depends-on-tool` (premise pass-4 C3 confirmed)

`yf preflight` reads the skill's `depends-on-tool` list from embedded frontmatter
(`preflight.rs:452`) and, when a listed tool is absent from `PATH`, returns
`status: "system_deps_missing"` with a non-empty `missing` array
(`preflight.rs:326`, `:663`; parity test `preflight_parity_system_deps_missing`,
`:1905`). The declaration is **not inert** — declaring `depends-on-tool: [uv, pandoc]`
on a skill makes preflight fail closed at invocation for free. **No "wire preflight
enforcement" work exists**; Issue 4.3's declaration is the whole preflight-side change.

### yf doctor has no per-skill dependency axis

`yf doctor`'s checks are a fixed registry (`yf/src/cmd/doctor/checks.rs`), each a `Check`
impl: `VersionCheck`, `BinCheck` (git/bd/uv — probes `PATH`), `HomebrewShadowCheck`,
`SkillCheck` (per-skill **marker** health via `skills:<name>` axis), `RuleCheck`
(companion-rule presence/hash). None enumerates a skill's `depends-on-tool`, so
`yf doctor` will **not** report a missing `pandoc`/`xelatex` for a markdown skill. The
existing `skills:<name>` axis checks marker health, a different concern.

## Decision

**Add a scoped per-skill `depends-on-tool` doctor axis (YES).**

Rationale: the fit is clean and low-cost — the `Check` trait + registry already exist, and
`BinCheck` already encapsulates the "probe `PATH`, ok/fail with remediation" logic the new
axis reuses. A new `Check` that iterates embedded skills, reads each `depends-on-tool`, and
reports a missing tool (with an install hint matching `md2pdf`'s message format) turns
`yf doctor` into a single holistic "is my environment ready for every installed skill"
surface — the proactive complement to preflight's fail-at-invocation. This satisfies the
operator's explicit "dependency guarding" request beyond the per-invocation guard.

Scope guardrails (keep it minimal):
- One new `Check` in the fixed registry; slots after the existing `SkillCheck` axes.
- Reuses `BinCheck`'s PATH probe; no new probing logic.
- One scoped `REQ-YF-DOCTOR-*` SPEC line + coverage entry (Issue 4.1).
- Report is `warn`/`fail` per tool; does not change existing axes.

**Consequences for downstream issues:**
- Issue 4.1: author the `REQ-YF-DOCTOR-*` line for the new axis (in addition to md2html's
  entrypoint guard REQ under REQ-MDHTML-*).
- Issue 4.3: markdown-html declares `depends-on-tool: [uv, pandoc]` **and** the new doctor
  axis is added so `yf doctor` reports a missing pandoc with an install hint.
- Issue 4.4: md2html entrypoint guard (independent of the doctor decision).
