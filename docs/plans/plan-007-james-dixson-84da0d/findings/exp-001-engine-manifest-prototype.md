# Finding: exp-001 — Engine/manifest prototype + regression parity

**Question:** Can the engine of `AGENTS/CONSISTENCY.md` + `AGENTS/DOCUMENTATION.md` be
generalized into a portable `drift-check` utility skill driven by a per-repo **markdown**
manifest, such that an isolated verification sub-agent can reproduce — from the manifest
alone — the same drift checks the two original files perform on this repo?

**Verdict:** Viable. The mechanism is cleanly engine-resident (no repo vocabulary); the
graph (nodes/edges/contracts/globs/required-sections/fixed-authority) is cleanly
manifest-resident. The markdown-manifest choice is vindicated. Two honest scope limits
identified (L1, L2). The port also uncovered a latent bug in the source rules (E4).

## Result summary

- **Engine/manifest boundary is clean.** The cascade principle, isolated sub-agent, dispatch
  prompt skeleton, evidence standard, the 4 check-category engines, orphan/reachability,
  report format, INCONCLUSIVE/conflict handling, and the hybrid-bootstrap *pattern* are all
  ENGINE (fixed, repo-agnostic). The node set, edge set, per-edge contracts, changed-path
  globs, required-section tables, and fixed-authority nodes are all MANIFEST (repo config).
- **Markdown manifest vindicated.** Limit L1 shows the per-edge `Contract` column carries
  semantic assertions (`field-set-subset`) that a rigid TOML/JSON schema could not express
  without inventing a DSL — and the engine already relies on sub-agent judgment for those, so
  prose is the right fidelity.
- **Hybrid bootstrap = the existing spec-bootstrap pattern**, lifted to the manifest. Reuse
  only the *draft → approve → enforce* half; exclude the *author-a-spec* half (L2).
- **E4 discovered a real latent bug.** `DOCUMENTATION.md` names `scripts/check-prereqs.sh` as
  the prerequisites source-of-truth three times (L27/L55/L68). `find skills -name
  check-prereqs.sh` → empty; `optimal-instructions/README.md:18` says "no check-prereqs.sh".
  The actual source moved to `plan_manager.py check` + frontmatter `depends-on-tool`. The
  source rule is itself drifted. The ported manifest (artifact C) is *more correct than the
  file it replaces*. → discovered work: correct the prereqs source-of-truth.

## Artifact A — Engine/manifest boundary (condensed)

| Concept | Classification |
|---|---|
| Cascade principle, isolated sub-agent, dispatch skeleton, evidence standard, post-return handling | ENGINE |
| 4 check categories (cross-ref / contract / behavioral / orphan-reachability) | ENGINE mechanism; specific references/values/dirs are MANIFEST |
| Component graph table, source-of-truth hierarchy | MANIFEST (the edge set + direction) |
| Required-section tables (skill README, project README), frontmatter contract | MANIFEST |
| Changed-path triggers | MANIFEST globs + ENGINE glob-match dispatch |
| Spec-compliance *enforcement* (fixed-authority node halts on conflict) | ENGINE mechanism + MANIFEST (which node is fixed) |
| Hybrid-bootstrap *pattern* | ENGINE (reused for manifest bootstrap) |
| Spec *authoring* (REQ-ID/Rationale/Verification drafting) | OUT OF SCOPE (L2) — content authoring, not drift detection |

## Artifact B — Manifest schema (markdown template)

Sections: (1) Artifact Nodes — `Node ID | Glob | Kind(source/doc/spec) | Authority(fixed/
derived) | Reachability(required/optional)`; (2) Source-of-Truth Edges — `Edge ID | Source
Node | Derived Node | Check Category(cross-ref/contract/behavioral/required-section)`;
(3) Per-Edge Contracts — `Edge ID | Contract | Verification(probe)`; (4) Referencers (orphan
check) — `Required Node | Valid Referencers`; (5) Required-Section Contracts per doc node —
`Required Section | Source Node | Source detail`; (6) Trigger Scope — `Changed-Path Glob |
Scopes To`; (7) Fixed-Authority Conflict Policy. Full template captured in the dispatch
record; reproduce verbatim when scaffolding `templates/manifest.md`.

**Fixed contract vocabulary** (recommendation 4): `path-resolves`, `identifier-matches`,
`value-equal`, `field-set-subset`, `field-set-equal`, `section-present`.

## Artifact C — This repo's manifest (regression instance)

Ported `CONSISTENCY.md` + `DOCUMENTATION.md` into schema B. Nodes: `skill-md`, `agent`,
`script`, `formula`, `template`, `spec`(fixed), `skill-readme`, `project-readme`,
`frontmatter-contract`. 17 edges incl. `e-skill-script-cli`, `e-formula-name`, `e-agent-ref`,
`e-json-contract`, `e-status-values`, `e-install-url`, `e-readme-layout`, `e-readme-prereqs`
(source = `skill-md + frontmatter(depends-on-tool)`, **not** check-prereqs.sh — the E4 fix
baked in), `e-index-table`, `e-frontmatter`. Full table in the dispatch record; this is the
artifact to materialize as the repo's `DRIFT-CHECK.md` during migration.

## Artifact D — Engine SKILL.md draft

Drafted: frontmatter `description` leading the SKIP axis with *"verifies CONTENT AGREEMENT
across declared artifact edges; never authors/optimizes/restructures; never auto-fixes"*;
`skill-group: utility`; `user-invocable: false`; SKILL_DIR resolution; manifest-location
detection (rules-surface `DRIFT-CHECK.md`); scope-vs-neighbors section; hybrid bootstrap
flow; workflow (identify change → read manifest → glob-match → dispatch → act on findings);
dispatch prompt (evidence standard verbatim, scoped node/edge IDs, report format); the 4
manifest-driven check engines; rules. Full draft in the dispatch record.

## Artifact E — Regression parity

- **E1 — script subcommands match CLI** (`e-skill-script-cli`): PASS. Caveat: §3 verification
  text must say "all `@cli.command` decorators" so the verifier enumerates the click command
  set exhaustively, not a sampled subset.
- **E2 — README file-layout matches `find`** (`e-readme-layout`): PASS. Pure command-output
  evidence; verified against `optimal-instructions/README.md` layout fence.
- **E3 — every script referenced** (orphan/`script` node): PASS. Reachability glob +
  referencer grep reproduces it.
- **E4 — README prereqs match check-prereqs.sh**: FAIL against literal text (file does not
  exist) / PASS against intent. The manifest supersedes the stale source. **Net: validates
  the model and surfaces a real bug to fix.**

## Honest limits

- **L1 — semantic contract comparison** (e.g. `e-json-contract` field-set subset) requires
  sub-agent judgment, not a mechanical diff. Parity preserved: the *original* has the
  identical reliance (CONSISTENCY L107). The markdown `Contract` column is the right home.
- **L2 — spec *authoring* subsystem is out of scope.** The engine keeps only the
  enforce-when-fixed-authority-node-exists half. Drafting new specs with REQ-IDs is content
  authoring; exclude it. Deliberate narrowing, not a silent drop.

## Trigger-collision analysis (Artifact F)

| Edit | drift-check | optimal-instructions | skill-authoring | Clean? |
|---|---|---|---|---|
| `skills/*/SKILL.md` | YES (manifest glob) | NO (SKIP: skill-dir → skill-authoring) | YES (authoring conventions) | Orthogonal axes; both legitimately fire; no contention |
| project-root `CLAUDE.md` | NO (not a manifest node) | YES | NO | Clean — single owner |
| non-instruction source/doc pair | YES (script + readme edges) | NO | maybe (PEP723 conventions on the .py) | Orthogonal; README half is drift-check-only |

**Genuine overlap, by design:** skill-dir files are claimed by both skill-authoring
(authoring conventions) and drift-check (cross-edge content agreement) — orthogonal concerns,
not a defect. Per-repo suppression lever: omit the glob from manifest §6. **No overlap with
optimal-instructions** — drift-check never lists CLAUDE.md/AGENTS.md as nodes here, so it is
structurally silent on the project-root axis.

## Recommendations (drive the plan)

1. Build the skill as drafted (D) with schema (B); engine ≈150 lines fixed prose + one
   verifier agent. Repo-specific weight all moves to `DRIFT-CHECK.md` (C).
2. Ship C as the regression instance and run it against the repo **before** deleting the two
   AGENTS files — reproduce E1–E3 (PASS) + surface E4 (FAIL) as the acceptance signal.
3. Fix the stale `check-prereqs.sh` reference during migration (manifest C already supersedes
   it). File as discovered work.
4. Make §3 `Contract` assertions an enumerable vocabulary (recommendation 4 above).
5. Lead the engine `description` SKIP with the content-agreement-vs-authoring axis.
6. Bootstrap must infer prereq/source nodes from what exists on disk (frontmatter, present
   commands), never a hardcoded conventional filename — the E4 lesson, baked into the engine.
