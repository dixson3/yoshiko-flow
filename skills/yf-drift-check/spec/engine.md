# Spec: engine behavior (bootstrap, no-op, dispatch, conflict)

The fixed engine mechanism: how the manifest is acquired, when the engine stays silent, how it
dispatches, and how it handles a fixed-authority conflict. Repo-agnostic.

## Requirements

**REQ-ENGINE-001: No approved manifest ⇒ silent no-op.** A repo with drift-check installed but
no approved `DRIFT-CHECK.md` does nothing on edit: no check, no nag, no bootstrap prompt.
Rationale: the engine must not impose on repos that have not opted in (mirrors the
UPSTREAM_TRACKING "silent no-op when disabled" clause). Verification: with no approved manifest,
an on-edit trigger produces no output.

**REQ-ENGINE-002: A manifest is inert until an approval marker is present.** Bootstrap writes a
draft; the draft does not drive enforcement until the operator approves it (an explicit marker
in the file or a recorded operator confirmation). Rationale: an inferred draft may be wrong;
enforcing it unreviewed would generate false drift reports. Verification: a draft manifest
without the approval marker is treated as "no approved manifest" (REQ-ENGINE-001).

**REQ-ENGINE-003: Bootstrap is offered only on explicit invocation or first install — never on
every subsequent edit.** Hybrid bootstrap: infer a draft manifest from repo structure (present
files, frontmatter, directory shape) → operator approves → engine enforces the approved
manifest thereafter. Bootstrap infers source/prereq nodes from **what exists on disk**, never a
hardcoded conventional filename (the exp-001 E4 lesson). Rationale: reuses the skill's existing
"draft a spec if none exists → approve → enforce" pattern, lifted to the artifact graph itself;
re-offering on every edit would be the nag REQ-ENGINE-001 forbids. Verification: bootstrap path
fires on explicit invoke / first install only.

**REQ-ENGINE-004: A fixed-authority conflict halts; the engine never edits the authority.** When
a derived node conflicts with a `fixed` node, the engine reports the derivative as drifted and
stops; it does not propose changing the authority to fit the derivative. If the conflict is
instead that the **authority itself is suspected wrong** (the exp-001 E4 case — the source rule
named a file that does not exist), the engine reports the conflict to the operator and waits;
it never silently "fixes" by rewriting either side. Rationale: drift resolution needs a stable
tie-breaker, but a drifted authority is a real finding, not something to paper over.

**REQ-ENGINE-005: The engine dispatches an isolated, report-only sub-agent; the main session
acts.** The engine (main session) reads the manifest, matches the changed path against §6,
and spawns the verifier (`agents/drift-verifier.md`) with the scoped edge/node IDs and the
evidence standard. The verifier returns findings; the main session resolves FAILs, surfaces
INCONCLUSIVEs, and halts on conflicts. Rationale: isolation keeps verification uncontaminated
by repair intent (the original CONSISTENCY "dedicated sub-agent" rationale). Verification: the
verifier writes nothing; only the main session mutates files.

**REQ-ENGINE-006: The engine carries no repo vocabulary.** No node IDs, edge IDs, globs, tool
names, or paths specific to any repo appear in `SKILL.md`, `spec/`, or `agents/`. All of that
lives in the per-repo `DRIFT-CHECK.md`. Rationale: this is the engine/manifest split that makes
the skill portable. Verification: grep the engine for repo-specific tokens (`bd`, `SKILL.md` as
a node, `skills/<skill>/`, `install.sh`, formula names) → none as load-bearing references
(illustrative examples in prose are permitted but must be labelled as examples).

**REQ-ENGINE-008: Dispatching a node-level Reachability check (the mechanism REQ-CHECK-008
authorizes).** A §6 *Scopes To* entry may name a **node ID**. When a changed path matches such a
row, the engine performs `REQ-CHECK-004(a)` over that node, in four declared steps:

1. **Resolve the two sets from the manifest, never from a hand-list.** *Set A* is every artifact
   the §4 Referencers row declares must exist (expanded from the referencer's own glob). *Set B*
   is the node's §1 glob, expanded. Both are computed at dispatch time; neither is enumerated in
   the manifest, because a hand-maintained list is a second source of truth that drifts.
2. **Apply SET DIFFERENCE, not intersection.** `A \ B` is the finding set — the required
   artifacts with no live counterpart. `B \ A` is reported separately as **orphans** and is
   advisory, not a FAIL: an extra derived artifact is not an unreferenced required one.
3. **Route by decidability (REQ-CHECK-008(c)).** If the manifest declares a runnable checker for
   this node, the engine **runs it and takes its exit code as the verdict**; the report-only
   sub-agent of REQ-ENGINE-005 is not dispatched for this check. Only where the predicate is not
   mechanically decidable does the node-level check fall to the prose verifier.
4. **Carry a vacuity floor.** A run in which *Set A* or *Set B* expands to fewer members than the
   node declares as its floor is **INCONCLUSIVE**, never PASS. A set-difference check over an
   empty set is vacuously green, which is the failure mode this whole requirement exists to
   remove.

**Why the set operator is stated normatively rather than left to the implementation.** Edge
pairing — the operator every other check in this engine uses — computes the **intersection** of
two globs. That is structurally why no edge could ever have seen this class of drift: an artifact
missing from one side simply drops out of the pairing, taking its own absence with it. Measured
(plan-066 EXP-002): with `skill-page` reachability unenforced, the two sets stood at 20 and 19,
the intersection at 19, and the one-element difference — the skill shipping with no page — was
reported by nothing. Naming the operator is what prevents an implementer from reaching for the
familiar one.

**§4 is what a node-keyed §6 row BINDS TO.** A node named in §6 with no §4 Referencers row has
nothing to compute *Set A* from, so the engine reports **INCONCLUSIVE** and names the missing
row — it does not silently pass. Rationale: the two sections are halves of one mechanism, and a
half-configured node must fail loudly rather than certify nothing.

## Out of scope (honest limits — REQ-ENGINE-007)

- **Spec authoring.** The engine keeps only the *enforce-when-a-fixed-authority-node-exists*
  half of the original spec-compliance subsystem. Drafting new spec REQ-IDs/Rationale is content
  authoring, excluded (exp-001 L2).
- **Auto-fix.** The engine reports; it never repairs drift.
- **Semantic-contract perfection.** `field-set-subset`/`field-set-equal` comparisons inherit the
  original's reliance on sub-agent judgment (exp-001 L1) — parity preserved, not a regression.
