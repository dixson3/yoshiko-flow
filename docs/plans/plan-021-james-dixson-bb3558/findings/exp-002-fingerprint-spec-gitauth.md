# EXP-2/3/4 — re-review fingerprint (#64), git-authority/auto-commit (#63), SPEC surface

**Method:** read-only map of `~/.claude/skills/yf-plan/` (`SKILL.md`, `plan_manager.py`, `SPEC.md`,
`spec/*.md`, `agents/*.md`) + repo-root `SPEC.md` and `yf/src/coverage.rs`.

## 1. Re-review fingerprint (#64)

### Self-trigger constraint (critical)
Review mutates the plan folder: writes `reviews/pass-N.md`, appends `- DATE review:` phase-log lines
(`SKILL.md:399,410`), updates the Operator Resolutions table in place, and on approve appends a
`- DATE approved:` line via `update-status`. `record-epic` adds `**Epic:**` + an `intake:` phase-log
line. **All of these — phase log, `**Status:**`, `**Epic:**`, `reviews/`, Operator Resolutions — are
process bookkeeping and MUST be excluded from the fingerprint**, or approval self-invalidates.

### Phase-log parsing (structural vs semantic)
`_plan_phase_log_lines` (`plan_manager.py:1788`); audit regexes at `:1809`
(`- DATE scoping:`) and `:1818` (`- DATE review:`, drives the REQ-PORT-006 count-equality at
`:1974`). `record-epic` uses an `intake:` prefix precisely because it matches neither regex
(`:857`) — the established pattern for non-counted phase-log lines. A fingerprint field must
likewise never live in a counted/regex-matched surface.

### Design recommendation
- **Hash surface:** the `##` body sections `## Objective` → `## Success Criteria`, excluding all
  `**Field:**` header lines and the `**Phase log:**` bullets. Reuse the audit's existing section-slice
  idiom `rf"^##\s+{name}\s*$(.*?)(?=^##\s+|\Z)"` (`plan_manager.py:1914`).
- **Normalize:** strip trailing ws, collapse blank runs, `.strip()` each section. Exclude `reviews/`,
  Operator Resolutions, phase log.
- **Store:** a `**Fingerprint:** <sha256[:N]>` header field inserted after `**Epic:**` (same mechanism
  as `record-epic:883`). Portable, out of every counted surface. `hashlib.sha256` already imported
  (`:13`).
- **Detect at command time** (no on-edit hook exists for yf-plan; the yf-change-validation /
  yf-drift-check on-edit triggers are orthogonal, own-manifest-only). Surface a `stale_approved`
  boolean from `resume-scan` (execute = **hard gate**) and advisory in `list`/`status`. Clone
  `_read_plan_epic_field` (`:1639`) for a `**Fingerprint:**` reader.
- **Semantics:** stamp fingerprint at APPROVE; on later read with status ∈ {review, approved}, if
  `hash(current) != stored` → stale-approved → require conformance → red-team → portability before
  execute. `--force` override logs a phase-log line (mirrors the portability `--force`).

## 2. SPEC surface (for SPEC-first)

- **`skills/yf-plan/SPEC.md`** = the `REQ-PLAN-NNN` / `GR-PLAN-NNN` numbered contract; it **references**
  the topical `spec/*.md` docs rather than restating them.
- **Topical `spec/*.md`:** `phases.md` (REQ-PHASE/REQ-RESUME/REQ-STATUS/REQ-SESSION), `portability.md`
  (REQ-PORT), `agents.md` (REQ-AGENT), `cli.md` (REQ-CLI), `data.md` (REQ-DATA), `prerequisites.md`
  (REQ-PREREQ).
- **Amendment log lives ONLY in the repo-root macro `SPEC.md`** (`/…/yoshiko-flow/SPEC.md:8-33`); per-skill
  files use per-requirement `Verification:` lines. So the AGENTS.md "living-amendment-log entry"
  mandate maps to a macro-SPEC line (e.g. `- **plan-019 (2026-07-02, #62-adjacent):** …`).
- **Homes for the three features:**
  - intake-at-execute → `spec/phases.md` (revise REQ-PHASE-002 / REQ-RESUME-001; new REQ-SESSION-003 /
    REQ-RESUME-004) + a `REQ-PLAN-05x` in `SPEC.md §2.6 Execute`.
  - auto-commit-at-plan → `SPEC.md §2.7` (git authority is REQ-PLAN-062 + GR-PLAN-003) — new
    `REQ-PLAN-06x` + a GR-PLAN-003 carve-out.
  - content-fingerprint re-review → `spec/portability.md` new `REQ-PORT-04x` (review invariants
    REQ-PORT-006/008 live here) + mirror `REQ-PLAN-03x` in `SPEC.md §2.4`.
  - base-pinning + landing-strategy → `spec/phases.md` or `SPEC.md §2.6`.
- **Coverage gate:** the forward REQ→test gate is **`yf`-crate-only** (`yf/src/coverage.rs`, enforces
  `REQ-YF-*` tagged in `.rs` tests). **No automated gate exists for `REQ-PLAN-*`/`REQ-PORT-*`**;
  `test_worktree.py` doesn't tag REQ ids. So add `Verification:` lines + tagged tests, but no CI forces
  them (documented gap).

## 3. Git-authority + auto-commit (#63)

- **Conservative stance is scoped to the REMOTE/push** (`SKILL.md:818`, `SPEC.md:97` REQ-PLAN-062,
  `SPEC.md:128` GR-PLAN-003 "the operator owns the remote"). Phase 6 **already** auto-runs local
  `git merge --no-ff` + `git commit` without authorization (`SKILL.md:768,805`). So a **local
  auto-commit (no push) is consistent with intent** — but GR-PLAN-003's wording lists
  auto-*committing* as drift, so it needs an explicit **carve-out** ("local commit permitted at intake;
  push remains authorized-only").
- **"Never commit to main" is NOT written anywhere** (absence finding) and there is **no branch guard
  in code** — `plan_manager.py` never reads the current branch by name (no `git branch --show-current` /
  `main` comparison). Both must be codified (SPEC requirement + real guard).
- **Auto-commit scope:** `${plan_dir}` + `.beads/` only (the two surfaces intake owns; Phase 6 already
  treats them as the change-set). Explicit pathspec `git add -- "${plan_dir}" .beads/`, **never
  `git add -A`**. Do not auto-stage sibling `CLAUDE.md`/`AGENTS.md` (project-wide, operator-owned).

## Absence findings
- No per-skill amendment log (only macro SPEC).
- No "never commit to main" rule and no branch guard in `plan_manager.py`.
- No REQ→test coverage gate for `REQ-PLAN-*`/`REQ-PORT-*`; `test_worktree.py` untagged.
- No existing fingerprint/stale-approval mechanism; no on-edit hook for yf-plan.
