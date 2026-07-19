# Review pass 5 — plan-029-james-dixson-75fd34

**Reviewer:** red-team (adversarial), cycle 5 (post impact-assessment-epic addition) · **Presented:**
2026-07-18 · **Conformance:** PASS (no dangling refs after the epic renumber)

## Verdict: REVISE

## Strengths

- Renumber is clean, no regression (captor.md → 3.3, fixtures → 3.7, `_index.md` fan-out → 4.3,
  dual-write R7, SPEC-first ordering all intact; gates cite correct new numbers).
- Gate cascade coherent and acyclic: composition gate (Epic 1) → Epic 2 assessment → ratification
  gate (Epic 2) → Epics 3–5 → migrated-legacy gate (Epic 3) → 6.2. Orthogonal axes.
- Assessment dependency wiring right: 2.1/2.2 depend on 1.3 (extension drafts) + 1.4 (engine with
  `--dry-run`), gated by the composition gate; correctly not on 1.6 vendoring.
- R8/R9 plausible; R9 (descope/exempt) is the correct release valve and implicit loop bound.

## Concerns

1. **Issue 2.1/2.2 use the wrong artifact paths — would miss the vault's entire plan+research
   corpus.** severity: high
   The vault's plans/research live at `docs/plans/`, `docs/research/`, AND incubator-scoped
   `Incubator/<slug>/plans/`, `Incubator/<slug>/research/` — the two-root model the skills actually
   use — not top-level `plans/`/`research/` as 2.2 says. 2.1 mirrors the gap (omits incubator-scoped
   roots for this repo).
   **Recommendation:** Rewrite 2.1/2.2 to **discover** both roots (default + incubator-scoped) plus
   single-file/dir-form incubators, not a fixed path list.

2. **Engine assumes greenfield frontmatter, but the vault already carries Obsidian frontmatter — and
   the REVISE loop can't fix engine code.** severity: high
   Real vault plans already have `title:`/`created:`/`tags:` frontmatter. Nothing in 1.1/1.4 requires
   `write_frontmatter`/`migrate` to merge-and-preserve pre-existing keys → (a) `migrate --dry-run`
   would wrongly report "add frontmatter" (garbage into the ratification decision); (b) a real
   migration could clobber `tags`/`aliases`. And Issue 2.3's loop feeds fixes only into the spec
   `.md` docs, not `okf.py`, so an engine defect the vault exposes has no fix home.
   **Recommendation:** (i) REQ (1.1) + engine (1.4): `write_frontmatter`/`migrate`
   **merge-and-preserve** unknown keys (only add `type:`/`okf_spec:`, never drop). (ii) Broaden 2.3's
   feedback scope to include engine (`okf.py`) fixes / reopen 1.4. (iii) Add a risk row.

3. **R8 read-only guarantee is procedural, not enforced.** severity: medium
   `migrate` (non-dry-run) mutates in place; the vault is a live git repo. One fat-fingered command
   is destructive.
   **Recommendation:** Make R8 structural — snapshot the vault to a scratch copy and run ALL Epic-2
   ops (check + dry-run) against the copy.

4. **`yf-okf check` is authored in 1.5, but 2.1/2.2 depend only on 1.3, 1.4.** severity: low
   **Recommendation:** add `depends-on: 1.5` to 2.1/2.2, or state the assessment invokes the engine
   `okf.py` directly (1.4 suffices).

5. **REVISE loop (2.3 ↔ ratification gate) has no written termination lever.** severity: low
   **Recommendation:** one line in the gate Instructions naming R9 as the explicit termination lever.

## Missing

- A foreign-corpus robustness REQ: engine `check`/`migrate --dry-run` must be report-only and
  **crash-safe** on non-conforming input (1.4 tests are synthetic fixtures; a crash mid-scan aborts
  the assessment).
- 2.2 should explicitly acknowledge the vault may run a different installed yf-flow version/layout
  than this repo (surfaced as divergence, not assumed equal).

## Gate Assessment

Four gates well-placed, acyclic, correct new-numbering targets. Ratification gate correctly blocks
3.1/4.1/5.1. Caveat (gate quality, not placement): its "sample migrations apply cleanly" test is only
as trustworthy as the impact reports feeding it — Concerns 1 & 2 would currently build those reports
from wrong paths + a clobber-not-merge model. Fix 2.1/2.2 and the gate test becomes sound.

## Upstream Assessment

Unchanged and correct. #83 include; #91 exclude. No change.

## Operator Resolutions

| # | Concern (sev) | Resolution | Status |
|:--|:--|:--|:--|
| 1 | 2.1/2.2 wrong artifact paths (high) | Rewrote 2.1/2.2 to discover BOTH roots (default `docs/{plans,research}` + incubator-scoped `Incubator/<slug>/{plans,research}`) + single-file/dir-form incubators, as a discovery step not fixed paths | resolved |
| 2 | Greenfield-frontmatter assumption; no engine-fix path in loop (high) | Added merge-and-preserve REQ to Issue 1.1 + engine behavior to 1.4 (add `type:`/`okf_spec:`, never drop existing keys); broadened Issue 2.3 to feed engine (`okf.py`) fixes too; added risk R10 | resolved |
| 3 | R8 procedural not enforced (med) | R8 rewritten structural — snapshot vault to a scratch copy; ALL Epic-2 ops run against the copy | resolved |
| 4 | check surface in 1.5 but 2.1/2.2 dep only 1.3/1.4 (low) | Added `depends-on: 1.5` to 2.1/2.2 | resolved |
| 5 | REVISE loop termination lever implicit (low) | Added R9-as-termination-lever line to the ratification gate Instructions | resolved |
| 6 | Missing crash-safe REQ + version-drift note (missing) | Added report-only/crash-safe REQ to 1.1/1.4; 2.2 now notes possible vault version/layout drift | resolved |
