# Review Pass 1 — plan-006-james-dixson-bf6e21

**Reviewers:** conformance (PASS), red-team (REVISE)
**Date:** 2026-06-03

## Verdict: REVISE

Well-scoped, technically sound; investigation findings independently verified accurate. No
high-severity blockers. Resolve the medium concerns (portability-contract completeness, exit-code
contract, cross-group invariant) before approval.

## Strengths

- Investigation findings verified-accurate (dep-check duplication, no check-prereqs.sh, rsync copy
  mechanism, folded-YAML frontmatter, unknown-key tolerance).
- Declarative/computed group design needs no installer edit when skills are added.
- Selection-precedence ambiguity pre-empted (skill-name args > --group > default-all).
- Behavioral-parity discipline: every existing install.sh flag + install_rules porting enumerated.
- CONSISTENCY.md cost managed by batching 8 frontmatter edits + one consolidated sweep.

## Concerns

| # | Severity | Concern | Recommendation |
|---|----------|---------|----------------|
| C1 | low | "Zero beads references" is imprecise — utility skill docs do mention beads; the true claim is no `bd` runtime dependency. | Reword Motivation to "no `bd` runtime dependency". |
| C2 | medium | `incubator` (no hard tool dep) in `beads` group has no reproducible tie-break rule in the computed-from-frontmatter model. | Issue 1.1 schema doc states the tie-break: group reflects intended-use coupling, not just hard tool deps. |
| C3 | medium | `context.md` is an unfilled template; cold reader gets no project/runtime/operator context (PLANS.md portability requirement). | Fill context.md before intake. |
| C4 | medium | "Non-zero exit summary" on the warn-anyway path silently changes install.sh's exit-0-on-success contract (breaks CI/wrappers). | Warn path exits 0; only `--strict` yields non-zero on missing tool. Add to 2.2 parity verification. |
| C5 | medium | Transitive `depends-on-skill` closure could pull cross-group skills, making Success Criterion 2 incidental not guaranteed. | Assert/check invariant: no utility skill transitively depends on a beads skill (in 1.2/2.3). |
| C6 | low | Issue 1.1 "a one-line pointer in the relevant AGENTS rule" does not name which rule. | Name the target: a short section in DOCUMENTATION.md (it owns README-sync). |

## Missing

| # | Item | Resolution |
|---|------|-----------|
| M1 | context.md substance (project env, runtime assumptions, operator authority). | Fill context.md. |
| M2 | rsync-fallback decision left as an open fork. | Decide: shell-to-rsync only; document rsync as an existing implicit prereq (already used today; no regression). |
| M3 | `--target` × `--group` interaction unspecified (used together in 2.3 verification). | State `--group` still filters under an explicit `--target`. |
| M4 | uv-absent failure mode of the bash wrapper is a raw `uv: command not found`. | Wrapper guards for `uv` and prints a helpful message. |
| M5 | No post-edit load check guaranteeing Success Criterion 5. | 2.3/3.2 explicitly load-check the edited SKILL.md files. |

## Gate Assessment

Gates minimal and appropriate. Start Gate (human/operator) sufficient. Reconcile Gate correctly
omitted (no upstream incorporated). Suggest 2.3/3.2 include an explicit post-edit load check for
Success Criterion 5 (optional given the well-evidenced finding).

## Upstream Assessment

Clean and honest. No matching upstream issue; open issues unrelated; routes to filing a fresh
tracking issue at land-the-plane (3.3). No supersedes/partials to over-claim. references/ correctly
empty.

## Operator Resolutions

| Concern | Resolution | Status |
|---------|-----------|--------|
| C1 | Motivation reworded to "no `bd` runtime dependency". | resolved |
| C2 | Issue 1.1 scope now includes the soft-dep tie-break rule. | resolved |
| C3 / M1 | context.md filled (project env, runtime assumptions, operator authority). | resolved |
| C4 | Approach + Issue 2.2 specify warn path exits 0; only `--strict` non-zero. | resolved |
| C5 | Issues 1.2 and 2.3 assert the no-utility→beads-dep invariant; new Success Criterion 7. | resolved |
| C6 | Issue 1.1 names DOCUMENTATION.md as the schema-doc home. | resolved |
| M2 | rsync-only decided; documented as existing implicit prereq in Approach. | resolved |
| M3 | Approach states `--group` filters under explicit `--target`. | resolved |
| M4 | Issue 2.2 adds a uv-presence guard in the wrapper. | resolved |
| M5 | Issue 2.3 includes a post-edit SKILL.md load check. | resolved |
