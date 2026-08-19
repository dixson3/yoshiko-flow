---
type: Reference
okf_spec: OKF-PLAN
id: upstream-close-118
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
title: 'Draft: #118 close comment (four sites in yf-plan README)'
---

> Verbatim text of an upstream write performed at plan-046 reconcile (§6.3).
> Kept in the bundle so the upstream record is reproducible from the plan folder alone.

Fixed in plan-046 Issue 5.3. **Four things at two sites in `skills/yf-plan/README.md`**, not the two this issue named.

**The two sites this issue reported:**
1. `:97` — the portability-contract list read `` `README.md` — orientation (file map, reading order) ``. Now `index.md`, described as the OKF-reserved bundle listing that **replaces** the legacy `README.md` surface.
2. `:144` — the file-layout block read `README.md  Orientation and file map for cold readers`. Now `index.md`, with the same replacement note.

**The two omissions this issue did not name** — found by measurement: `grep -c "index\.md\|log\.md" skills/yf-plan/README.md` returned **0** for the entire file.
3. `index.md` and `log.md` were **absent from the portability-contract list** (`:95-101`). Both added, with what each replaces and the requirement that governs it (REQ-PORT-001; REQ-PORT-006 for the `review:` count-equality).
4. `index.md` and `log.md` were **absent from the layout block** (`:140-155`). Both added; `plan.md`'s description no longer claims to carry the phase log, since `log.md` now does.

**Correction to this issue's own citation.** It cites `SKILL.md:245`. Verified today: `:245` is incubator-scoping prose (*"Ask when it is genuinely ambiguous…"*); the content it means is at **`SKILL.md:262`** (the `init` scaffold description, which names `index.md` and `log.md`). The citation had drifted — recorded rather than silently followed, since a stale line reference is the same defect class this issue reports.

**Split out, deliberately:** the skill-dir **File Layout** section (`README.md:106-138`) is stale on a much larger scale — roughly 20 omissions including `SPEC.md`, `OKF-EXTENSION.md`, `test-harness/`, and 18 of 21 `scripts/` files. That is a different defect in the same file, and folding it in here would make this issue unreviewable. Filed separately as #172.

Plan: `docs/plans/plan-046-james-dixson-aabefa/`. Tracker: #167.
