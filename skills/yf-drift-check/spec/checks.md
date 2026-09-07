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

**REQ-CHECK-010: A `required set` check shall DECLARE its scope and carry a VACUITY FLOOR.**
Where an edge asserts that a derived node documents a set of surfaces the source node declares,
the check shall name the **class** of surface it requires and shall refuse to certify an empty or
implausibly small inspection:

- **(a) Declared scope.** The v1 required-set class is **slash sub-verbs** — every sub-verb a
  skill's normalised `## Invocation` declares must be named on its web page. Classes the check
  does **not** require are named in its `not_checked` output per `REQ-CHECK-009`.
- **(b) Vacuity floor.** The check shall fail INCONCLUSIVE when the required set it derived falls
  below a declared floor. A shape change upstream must not be able to silently zero the set.
- **(c) Corpus-wide, never per-page.** The predicate is "documented **somewhere** on the site",
  not "documented on this page".

Rationale, **measured** (plan-067 EXP-002/EXP-003): a required set drawn from the *derivable
frontmatter* classes newly FAILed **17–18 of 20** currently-green pages and **every one of those
failures was an artifact** — `skill-group` and `depends-on-tool` are emitted by the generator into
a block this manifest already declares unable to drift, so requiring them of authored prose is a
24-failure false-positive burst that discredits the check on its first run. Slash sub-verbs were
the **one** class with a clean signal (0 generated-data artifacts; the negative control fires and
names the removed verb). And a **per-page** predicate manufactures ~30 false failures on
`usage.md` and `workflows.md` alone, since 15 of 20 skills go unmentioned in the first and 17 of
20 in the second — EXP-003 generated exactly that false positive against itself. Script-verb
coverage is **irreducibly editorial** and is excluded by name: 40 registrations, **zero**
visibility metadata, no bit in the source to read.

**REQ-CHECK-011: A one-directional edge over a two-directional obligation is HALF a check, and
the missing half shall be declared or supplied.** Where an edge's declared failure directions all
run derived→source, a fact that exists **only** on the source side is unreachable by construction.
Such an edge shall carry the source→derived direction as well, realized mechanically per
`REQ-CHECK-008(c)` where the predicate is a set difference.

Rationale, **measured**: `e-web-cli-surface` is `path-resolves` and **both** its declared failure
directions are page→CLI, so **no check anywhere could see a shipped command that no page
documents**. `yf harness skills prune-private` — live and **destructive** — is documented nowhere,
and grepping the whole published corpus for it returns no output. The predicate is corpus-wide
**token presence**, and **positional arguments are excluded**: measured, clap derives long flags
from field names, so a naive extractor missed `--prune-formulas` while a corrected one returned 12
"missing" of which **5 were positionals** — a ~40% artifact rate that must be reported before the
direction lands.

**REQ-CHECK-013: A set-membership claim FAILs on a MISSING member, not only on a WRONG one.**
Where a derived node enumerates the members of a set the source node declares, the check shall
compute **both** differences — members present but wrong, **and** members declared but absent —
and shall FAIL on either. A group that enumerates **no** member ids shall be reported as an
explicit unchecked class, never folded into the clean population.

Rationale, **measured**: the prior rule held that a page which "curates or omits repo-dev detail
PASSes — only an affirmative contradiction FAILs", which makes an omission invisible *by
construction*. Under it, deleting two members of an enumerated group while leaving its count
unchanged exited **0**. The cost, on record: `land`, retrospectives, the escalation surface,
autonomy levels and `closable` went undocumented across multiple releases and **nothing ever
complained**; `architecture.d2` omitted an entire skill group while passing every check. The
carve-out this requirement does **not** touch is genuine editorial curation on a prose page —
which is why `REQ-CHECK-010(a)`'s declared scope, not this requirement, decides *what* is
required.

**The `members is None` branch is part of this requirement, not an implementation detail.** A
membership check that runs only inside the `else` of "were any ids enumerated?" lands the new
FAIL in the one branch where the omission cannot occur, and a diagram redesigned into a shape with
*fewer* enumerated labels is then the easiest possible evasion. "No ids enumerated" and "checked
and clean" are **two facts**; reporting them through one signal is the `#263` class.

**REQ-CHECK-014: The agent-set edge (`e-web-agents-set`) shall be SCOPED to the pipelines its
derived node claims to cover.** The edge asserts that every agent under the scoped source glob is
named by the derived node. The scope is a **required part of the edge**, not a tuning parameter.

Rationale, **measured**: the derived node's own subtitle covers "the yf-plan and yf-research
pipelines and the subagents that run them", and scoped to `skills/{yf-plan,yf-research}/agents/*.md`
the baseline is **15 of 16** with one genuine absence. Unscoped, `skills/*/agents/*.md` returns
**23** files across 6 skills, and an extractor over it surfaces 4–7 out-of-scope agents against 1
real finding — an **80–87% artifact rate**. An unscoped edge here does not catch more; it catches
the same one thing and buries it.

**REQ-CHECK-012: A key whose source of truth is THREE-VALUED shall not be read as two-valued.**
Where a producing artifact types a field as tri-state — present-true, present-false, **absent
meaning unknown** — a consumer that coerces absent into one of the two present values invents a
fact the producer never stated, and does so silently:

- **(a) Populate at the producer, do not default at the consumer.** A tri-state key shall be
  explicitly populated at every producing site. A consumer-side default is a second, undeclared
  source of truth for the same field, and the two disagree exactly on the case neither declares.
- **(b) The population shall be mechanically asserted.** An absent key shall be a detectable
  condition with an exit code, not a convention. Without this, the absent case returns on the next
  artifact anyone adds.
- **(c) Where a consumer must still choose, it chooses the LOUD reading.** A consumer that cannot
  avoid a default shall pick the value that fails visibly over the one that renders a plausible
  falsehood.

Rationale, **measured**: `yf/src/frontmatter.rs:61` types `user_invocable: Option<bool>`;
`web/plugins/skill_pages.py:133` read `bool(fm.get("user-invocable", False))`. Four `SKILL.md`
files omitted the key, so the published site described them as **"auto (fires from its description
conditions)"** while their own descriptions read `TRIGGER when: /yf-markdown-lint invoked`. No
check anywhere could see it: both sides were internally consistent, and the disagreement lived
entirely in a default argument. This is the tri-state instance of the "two facts, one signal"
class (`#263`) — an absent key and a declared `false` are different facts, and collapsing them is
what made the falsehood unreachable.

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
