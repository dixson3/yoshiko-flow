# Finding INV-5: embed vs distinct `worktree` skill (resolves D1)

**Date:** 2026-06-14 · **Method:** precedent survey (plan-008, plan-006, install.py, diagram-authoring) + synthesis over INV-1..4

## Result

**Q1 — The existing soft-dependency mechanism is instruction-level PROSE, not code.** bdplan's
soft dep on diagram-authoring has **no detection code, no runtime probe, no frontmatter edge**.
`bdplan/agents/planner.md:23-28` (and `bdresearch/agents/packager.md:37-41`) name the skill and
say: *"Degrade gracefully (prose only) if the skill or `d2` is absent — **never add a
`depends-on-skill` edge for it**."* "Detection" = the LLM following the instruction; the named
skill's own TRIGGER surfaces it. plan-008 EXP-002 documents WHY: *"`install.py` has no
soft-dependency concept — every `depends-on-skill` edge is a hard, force-install edge."*

**Q2 — Frontmatter `depends-on-skill` is HARD-ONLY.** plan-006 added `skill-group`,
`depends-on-tool`, `depends-on-skill`. `install.py::resolve_install_set` computes the transitive
closure and **force-installs** every `depends-on-skill` name. There is **no `optional`/`soft`
qualifier**. So a `worktree` skill CANNOT be an optional frontmatter dep of bdplan — listing it
would force-install it (forbidden by plan-008). The only "soft" layer is instruction prose. The
worktree *capability* is already covered by bdplan's existing hard `depends-on-tool: [git]`.

**Q3 — Weighing (lifecycle concern, distinct from INV-4's validation concern):**
- (i) **Reusability:** ONE concrete consumer today (bdplan execute). bdresearch uses harness
  `isolation="worktree"` for investigators — a DIFFERENT (disposable) model, not this persistent
  one. No second consumer in hand.
- (ii) **Coupling:** the lifecycle is tightly interleaved with bdplan's phase machinery — create
  after §5.3 start-gate; re-attach IS the §5.2 resume guard (the beads-authoring resilience
  contract); merge-back/teardown entangled with the §6.1-6.2 conservative git-authority handoff;
  branch name = plan id. The genuinely generic core is small (`git worktree add/remove/prune`);
  the *policy* is bdplan-specific.
- (iii) **Precedent:** diagram-authoring is a true standalone utility (`user-invocable: true`,
  multiple consumers, independent reason to exist). A `worktree` skill has neither yet.
- (iv) **Cost:** distinct skill ≈ 2x v1 surface (new SKILL.md + frontmatter + scripts + install
  group + soft-dep prose + README/DRIFT-CHECK edits) for zero present reuse, plus the standing
  risk of the soft dep being "fixed" into a hard edge.
- (v) **Rule of three:** same maturity stage as INV-4's validation concern — don't extract first.

**Q4 — RECOMMENDATION: (C) embed-with-seam now, extract later.** Embed the worktree lifecycle in
bdplan behind a thin named seam:
- Generic, plan-agnostic git mechanics → a self-contained verb cluster in `plan_manager.py`:
  `worktree ensure <plan_dir>` (idempotent create-or-reattach), `worktree path <plan_dir>`,
  `worktree teardown <plan_dir>` — each `--json`, taking only `(repo_root, plan_id/plan_dir)`,
  modeled on `diagram-authoring/scripts/render.py`'s `add_subparsers`. A lift-and-shift unit.
- Sequencing/POLICY (when to create vs the start gate, re-attach via `resume-scan`, teardown
  before the push handoff, cwd propagation) stays inline in bdplan SKILL.md §5.2/5.3/6.1/6.2.
- **Extraction trigger (write into plan as the rule-of-three condition):** a SECOND consumer
  (bdresearch adopts persistent execution, or a standalone `/worktree` command). Then the verb
  cluster lifts into `skills/worktree/scripts/worktree.py` + SKILL.md, wired via the Q1
  instruction-prose soft-dep — **never** `depends-on-skill`.

**Interaction with INV-4:** both concerns sit in the SAME place and maturity tier — bdplan-
internal v1, each behind a named seam (validation: `validate-cmd` config; worktree:
`plan_manager.py worktree` verbs), both deferring a skill split to second-use. Orthogonal
concerns, co-located in RECONCILE, coherent posture. No tension.

**Q5 — Operator framing:** Recommend (C). Strongest FOR embed: one consumer, policy-coupled to
bdplan's phases, and no frontmatter way to declare an OPTIONAL dep (a separate skill would be
force-installed [forbidden] or reduced to prose that buys nothing for one consumer). Strongest
FOR a distinct skill now (B): only if a second consumer is *committed* (a standalone worktree
command, or bdresearch adopting the model) — then build now to avoid a later migration. Override
to (B) only on a committed second consumer; the (C) seam makes the later split cheap.

## Implications for Plan
- D1 resolves to (C). Do NOT add `worktree` to bdplan `depends-on-skill` under any circumstance.
- Concrete v1 work: `worktree {ensure,path,teardown}` verbs in `plan_manager.py`; policy wiring
  inline in §5.2/5.3/5.4/6.1/6.2; coordinator + sub-agent cwd = `.worktrees/<plan-id>`.
- Record the rule-of-three extraction trigger explicitly, co-located with INV-4's identical
  posture for validation.
