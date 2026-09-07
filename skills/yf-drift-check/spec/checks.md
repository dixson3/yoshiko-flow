# Spec: check categories + evidence standard

The four manifest-driven check engines and the evidence standard the verifier enforces. These
are the repo-agnostic generalization of the original `CONSISTENCY.md` four checks; the specific
nodes/edges/values are supplied by the manifest, not here.

## Check categories

**REQ-CHECK-001: Cross-references valid (`cross-ref`).** For each `cross-ref` edge, every
reference the derived node makes into the source node resolves to a real target. Generalizes
"file paths exist, script subcommands match, formula names match filenames, agent/template
refs exist." Contracts: `path-resolves`, `identifier-matches`. Rationale: a dangling reference
is the most common and cheapest-to-detect drift.

**REQ-CHECK-002: Contracts consistent (`contract`).** For each `contract` edge, a value or
field-set the derived node assumes matches what the source node actually produces/declares.
Generalizes "output schemas match scripts, status values match the phase model, agent I/O
matches." Contracts: `value-equal`, `field-set-subset`, `field-set-equal`. Rationale: silent
contract drift (a renamed JSON key, a dropped status) breaks consumers without a dangling ref.

**REQ-CHECK-003: Behavioral alignment (`behavioral`).** For each `behavioral` edge, logic
duplicated across nodes produces equivalent results (e.g. an ID format, a URL, a prereq list
stated in two places). Contracts: `value-equal`. Rationale: duplicated logic drifts when one
copy is edited; this is the "same fact in two files" check.

**REQ-CHECK-004: No orphaned components (`required-section` + Reachability).** Two halves,
**and they are dispatched differently** — see REQ-CHECK-005 and REQ-CHECK-008:

- **(a) Reachability — a NODE-LEVEL, WHOLE-CORPUS check.** Every `required` node (§1
  Reachability) has a live referencer per §4. Its operator is a **set difference** over two
  whole globs, so it is not an edge check and has no edge to be scoped by.
- **(b) Required sections — an EDGE check.** Every `required-section` edge's §5 sections are
  present in the derived node. Contract: `section-present`.

Rationale: an unreferenced required artifact, or a doc missing a mandated section, is drift even
when every existing reference resolves.

**AMENDED (plan-066).** The two halves were previously stated as one undifferentiated
requirement, which put (a) in direct contradiction with REQ-CHECK-005: §6 maps changed-path
globs to **edges**, so a node-level check with no edge to be scoped by had **no firing surface
at all**. Measured (plan-066 EXP-002): `skill-page` is a `required`-class artifact whose absence
— `skills/yf-okf-hygiene/` shipping with no `web/content/skills/yf-okf-hygiene.md` — was
detected by nothing in this engine. Edge pairing computes the **intersection** of the two globs,
which is structurally why it can never see a set difference. The remedy already existed in the
repository, in the wrong artifact: `web/plugins/skill_pages.py` implements exactly this
predicate, but its verdict is a Pelican **build crash** rather than a drift FAIL.

**REQ-CHECK-005: The verifier runs only the EDGE checks scoped by the changed path (§6).**
Scope: REQ-CHECK-001, -002, -003 and **-004(b)**. Rationale: on-edit checks must be cheap and
local; a full-graph sweep is reserved for explicit invocation. Verification: the dispatch passes
the matched edge IDs; the verifier checks no others.

**AMENDED (plan-066).** The words "the edges scoped by" were read as covering *every* check the
engine performs, which silently swallowed REQ-CHECK-004(a). This requirement now names the
checks it governs, and REQ-CHECK-008 governs the one it does not.

**REQ-CHECK-008: Node-level Reachability checks are dispatched by a NODE-KEYED §6 row, and
where the predicate is mechanically decidable they shall be realized as a runnable checker.**
Three obligations:

- **(a) Dispatch.** A §6 row MAY name a **node ID** in its *Scopes To* cell in addition to edge
  IDs. A changed path matching that row dispatches REQ-CHECK-004(a) over the named node's whole
  glob. Without this, a node-level check is unreachable by construction.
- **(b) The source-side trigger is MANDATORY, not advisory.** A node-level existence check MUST
  be reachable from a §6 row matching the **source** side of the predicate, not only the derived
  side. Rationale, measured: **an absent file is never edited and can never fire its own on-edit
  check.** A derived-side-only trigger cannot fire on the commit that creates the gap — plan-066
  measured commit `75a5796`, which added a twentieth skill and broke the site build while
  touching **zero** files on the derived side.
- **(c) Mechanical realization.** Where the predicate is a set difference or another decidable
  comparison, the check SHALL be realized as a **runnable checker** registered in the repository's
  validation recipe, and the manifest edge SHALL declare that it is so realized. An
  LLM-prose-judged edge is permitted only where the predicate is not mechanically decidable.
  Rationale, measured: a well-specified prose edge that is never dispatched has a catch rate
  indistinguishable from having no edge at all — plan-066 EXP-002 measured `e-skill-page-desc`
  at **4 firing opportunities, 0 catches**, and the edge was *fully capable* when dispatched by
  hand (3 FAILs with quoted evidence). Coverage is not detection.

**REQ-CHECK-009: A mechanical gate SHALL DECLARE what it does not cover — the split is stated,
never implied.** Where `REQ-CHECK-008(c)` realizes part of a manifest's coverage as a runnable
checker, the mechanical and the prose-judged halves shall both be named:

- **(a) The checker declares its own exclusions**, by edge or claim class, in its machine-readable
  output — a `not_checked` field — and in its documented contract. An excluded item shall name the
  requirement or rationale that excludes it.
- **(b) An excluded item keeps its route.** Declaring an edge unchecked does not retire it; it
  remains a prose-judged edge and the manifest continues to carry it. Declaring is a statement
  about *this instrument*, not about the edge.
- **(c) Silence is forbidden.** A checker that covers a proper subset of a manifest's edges and
  says nothing about the remainder reports a green that a reader will attribute to the whole.

**Why this is a requirement and not a style note.** A green with an undeclared boundary is
indistinguishable from a green with no boundary, and the reader has no way to tell which they are
holding. The precedent this generalizes is `check_skill_readme_contract.py`, which implements the
mechanical subset of four README edges and emits `"not_checked": ["e-readme-desc"]` — that edge's
predicate is *intent* match, which tolerates paraphrase and is not mechanically decidable, so
claiming it would be exactly the vacuous check the instrument exists to close.

**What belongs on each side of the split.** Decidable, and therefore mechanical: counts, path and
identifier strings, artifact existence, set membership, byte or hash equality under a recorded
pin. Not decidable, and therefore prose-judged: **semantic mis-assignment** (a group whose count
is right and whose membership is wrong), missing qualifiers, intent match, and editorial omission.
The third is not merely undecidable but often **correct** — a doc that curates or omits detail is
not thereby in drift, and only an affirmative contradiction is.

## Evidence standard (verbatim from the original CONSISTENCY rule — REQ-CHECK-006)

Every check item must be backed by direct evidence before it is marked PASS or FAIL:

- **File existence**: read the file or glob for it. "I know it exists" is not evidence.
- **Identifier / interface match**: read the source and identify the definition. Compare names
  and flags character-by-character against what the derived node references.
- **Contract match**: read the source that produces the value/field-set and list it. Compare
  against what the derived node assumes.
- **Content match**: read both nodes and compare the relevant sections. Quote the lines.
- **Grep / command results**: show the command and its output.

If a check requires runtime execution that is unavailable or would have side effects, mark the
item **INCONCLUSIVE**: state what would need to run and why it couldn't. Never guess. "I believe
this is correct" is not evidence — show the line, the output, or the match.

Rationale: the engine's reliability rests entirely on the verifier refusing to assert without
evidence; this standard is the load-bearing invariant and is copied, not paraphrased.

## Verdict semantics

**REQ-CHECK-007: The verifier returns one of four per-item verdicts — PASS / FAIL /
INCONCLUSIVE / CONFLICT — and never fixes.** The main session acts on each:
- **PASS** → continue.
- **FAIL** → a derived node disagrees with its source; resolve in the same pass.
- **INCONCLUSIVE** → surface to the operator with the verifier's notes (never assume pass/fail).
- **CONFLICT** → a `fixed`-authority node is itself suspected stale (the exp-001 E4 case: the
  authority names something that does not exist). Distinct from FAIL: the fix is *not* to edit
  the derived node. Halt and report to the operator per §7 and `engine.md` REQ-ENGINE-004;
  never silently rewrite either side.

CONFLICT is a separate verdict precisely because its resolution differs from FAIL — FAIL fixes
the derivative, CONFLICT escalates the authority. Rationale: isolating verification from repair
keeps the verification mindset uncontaminated (the original's "dedicated sub-agent" rationale).
