---
type: Plan
okf_spec: OKF-PLAN
description: Standardize the README and code-adjacent documentation layout contract,
  and backfill all 20 skills to meet it
id: plan-061-james-dixson-6d8c97
author: james-dixson
created: '2026-08-30'
status: reconciling
deliverable_class: standard
fingerprint: c6b00c510909b0b072267e3e028bb9e41aaeb53ee06272ba4b951913888d8c31
epic: yf-mol-4cyz
---
# Plan: Standardize the README + code-adjacent documentation layout contract and backfill all 20 skills

**ID:** plan-061-james-dixson-6d8c97
**Author:** james-dixson
**Created:** 2026-08-30
**Status:** reconciling
**Deliverable-class:** standard
**Epic:** yf-mol-4cyz
**Fingerprint:** c6b00c510909b0b072267e3e028bb9e41aaeb53ee06272ba4b951913888d8c31

## Objective
Standardize the layout/structure contract across `README.md` and code-adjacent documentation
files, then backfill every impacted file so the contract is actually met.

**This is Plan 1 of 3** (upstream tracker **#315**). The original plan-061 scope — a single
combined website/docs realignment — was measured during investigation and proved too large for
one plan. The operator split it:

| | Plan | Tracker | Status |
| :-- | :-- | :-- | :-- |
| **1** | **README + code-adjacent layout contract, backfill 20 skills** | **#315** | **this plan** |
| 2 | `yf-okf-hygiene` corpus backfill — 8 legacy bundles | #316 | not started |
| 3 | Regenerate user-facing docs; separate content from process defects | #317 | not started |

Order 1 → 2 → 3 is a real dependency, not a convention: plans 2 and 3 both transform or
regenerate documentation **against the contract this plan establishes**. Running either first
would backfill onto a contract about to change.

### Explicitly OUT of scope (carried to the successor plans)

- The Pelican **build break** and every website content defect → **#317**
- The `yf-okf-hygiene` **corpus backfill** of 8 legacy bundles → **#316**
- The `DRIFT-CHECK.md` manifest-coverage work (`optional`-node hole, missing §6 trigger rows,
  `e-web-cli-surface`'s narrow source node, the #291/#247 edges) → **#317**

Findings `exp-001`, `exp-002` and `exp-004` in this bundle were produced under the original
combined scope and are **retained deliberately** — they are the evidence base for #316 and #317,
and re-deriving them later would repeat four investigations.

## Motivation
`DRIFT-CHECK.md` declares four README edges (`:99-102`, `:158-161`) — `e-readme-layout`
(`field-set-equal` against `find skills/<skill> -type f`), `e-readme-prereqs`, `e-readme-usage`
and `e-readme-desc`. **Nothing runs them.** `CHANGE-VALIDATION.md:6` excludes `yf-drift-check` as
*"prose/LLM trigger, not a runnable command"*, so the only firing surface is an on-edit
obligation — and #273 measured that prose naming an obligation is skipped where prose naming a
command is followed.

The consequence is measurable. Issue #244 reported "16/19 skills failing". Re-derived at HEAD on
2026-08-30, **every figure in it is stale-low**:

| Metric | #244 as filed | Measured today |
| :-- | --: | --: |
| `e-readme-layout` failing | 16 / 19 | **18 FAIL / 1 PASS / 1 N-A of 20** |
| `SPEC.md` omitted from fences | 10 | **12** |
| Stale unprefixed fence roots | 5 | **10** |
| `yf-plan` `document_types/` schemas | 20 | **19** `.toml` under `skills/yf-plan/scripts/document_types/` |
| `e-readme-prereqs` failing | 1 | 1 (unchanged) |
| `e-readme-usage` failing | 2 (+1 missing) | 3 (unchanged) |

Only `yf-beads-hygiene` passes `e-readme-layout` cleanly.

**The schema denominator, stated because it will otherwise be re-litigated:** the count is **19
`.toml` files** under `skills/yf-plan/scripts/document_types/`. `_shared/document_types/` carries
the same 19 plus a `README.md` — 20 directory entries. #244's "20" was almost certainly counting
that README, which is why the figures differ without either being careless.

**#244's numbers went stale inside a single plan-cycle.** That is not incidental — it is the
strongest available argument that the fix must be a runnable check rather than a repair pass. A
repair without the check regenerates this issue within two plans.

**A fifth failure mode the manifest cannot express.** `yf-okf-hygiene` has **no `README.md` at
all** — the only such skill, and structurally invisible to #244 (filed before it shipped). It is
`N/A` on all four edges: there is no README to fail a contract against. It is an *absence*, not a
mismatch. `skill-readme` is a **`required`** node, which enforces nothing — `required` only means
reference-validity checks apply *if the artifact is present*.

**`install.sh` does not exist.** Neither does `install.py`; `yf/src/parity.rs:2,5` calls the
latter "retired" (deleted at plan-010). `README.md:39` documents a *hosted vendor* installer at
`yoshikoflow.sh/install.sh` — a different artifact. Yet **17 skill READMEs** direct readers to
"the repo-level `install.sh`/`install.py`", and **`DRIFT-CHECK.md` itself does so three times** — `:219` and `:225` in §5 Required-Section
Contracts, naming it as the required Install-section source, and `:164` in §3, where it is the
declared source of truth for the `e-frontmatter` edge. The manifest names a nonexistent authority for its own contract — the error class its §7
conflict policy exists to catch, committed in itself. `e-install-url` cannot catch it: it checks
byte-identity of a URL duplicated between `SKILL.md` and README, **not that the mechanism named
is real.**

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| #315 | Plan 1/3: standardize the README + code-adjacent documentation layout contract | include | **The coarse tracker for this plan.** | TBD |
| #244 | README-contract drift: e-readme-layout fails 16/19 skills | include | Full scope per operator. Its counts are superseded by the re-measurement above; comment posted. | TBD |
| #247 | Drift findings no edge covers; install.sh/install.py do not exist | partial | **The `install.sh` half lands here.** The manifest-diagram half → #317. Comment posted recording the split. | TBD |
| #273 | The command-vs-obligation law | partial | Design input, not a deliverable — why the fix must be a runnable check. **Disposition corrected `include`→`partial` at reconcile (lander adjudication):** `include` mechanically requires CLOSED, but #273 is a corpus-wide law measured over five plans and this plan converted ONE obligation into ONE command. Closing it would assert the law is discharged everywhere — the exact class of unproven claim the law warns about, and contradicted by this row's own `Resolved By: —`. `partial` (OPEN + mandatory mention) is what the Notes always meant, and matches #149, whose Notes are the same class. | — |
| #149 | M5/M9: process rules that nothing executes | partial | Adopt "a step with no exit code is not a step". Not M9's remediation-edge scope. | — |
| #291 | yf-drift-check edge over the escape/stop taxonomy | deferred | Re-routed to #317 with the rest of the manifest work. Its own body is partly wrong — see exp-004. | — |
| #127 | web/concepts: define idiomatic workflow terms | exclude | Operator excluded; may fold into #317. | — |
| #104 | web: prevent runaway Pelican devservers | exclude | Unrelated to this plan; flagged on #317 as likely to bite there. | — |

## Investigation Findings

### Scoping decisions (operator, this session)

| # | Decision | Consequence |
| :-- | :-- | :-- |
| D1 | Triage as recommended, **plus** #244 and #291 at FULL inclusion; #127 excluded | Scope widens from the website into skill READMEs and a second new drift edge |
| D2 | (d) = **mechanical checks** bound to `CHANGE-VALIDATION.md`, not a full runner | Only genuinely countable edges get an exit code; prose edges keep their LLM route |
| D3 | Note the drift-check/change-validation obligation in the process-agent issue | **Done** — posted to #312 this session (comment 5470285301) |
| D4 | (b) = **everything that landed**, not just user-facing surfaces | Retrospectives, `land`/lander and the escalation surface are all in scope |

### Shipping state, verified before drafting (bears directly on D4)

| Behavior | State | Evidence |
| :-- | :-- | :-- |
| `land` verb | **shipped** | `plan_manager.py:8200` (`@cli.command("land")`) |
| `lander` agent | **shipped** | `skills/yf-plan/agents/lander.md` |
| Retrospectives | **shipped** | `retrospective-append`, `retrospective-report` |
| Autonomy levels | **shipped** | `SKILL.md:141` — `--checkpoint`/`--autonomous`/`--sweep-gates` |
| `yf-judgement` | **NOT a skill** | no `skills/yf-judgement/`; the escalation surface ships *inside yf-plan* as `escalation-raise`/`-resolve`/`-report`/`-push` + `judgement-never-fired-report` |

**The last row is load-bearing.** D4 says "everything that landed", and the naive reading of that
is a `yf-judgement` skill page. There is no such skill. Documenting one would manufacture exactly
the class of false claim this plan exists to remove. The escalation mechanism is documented **as
part of yf-plan**, or not at all.

### Approach hypothesis (pre-investigation)

The four workstreams are separable, but (c) and (d) share a root cause and must not be sequenced
apart: (c) makes a missing artifact *detectable*, (d) makes the detector *run*. Either alone
leaves a green light over a false site. (a) is mechanical repair gated on (c)/(d) existing, so
the repairs are proven by the new checks rather than asserted.

Open: whether the mechanical checker is a new script or an extension of an existing check under
`scripts/checks/`, and whether `e-skill-page-desc`'s optionality can be tightened without
breaking the name-pairing every other `e-skill-page-*` edge relies on.

## Approach

**A repair pass without a runnable check regenerates #244 within two plans.** That is not a
prediction — #244's own figures went stale inside one plan-cycle (16/19 → 18/20, 10 → 12, 5 →
10). So the check is built **first** and the backfill is proven *by* it, rather than asserted
after it.

Four sequenced moves:

1. **Pin the contract in SPEC, then build the checker.** SPEC-first per `AGENTS.md`: the
   `REQ-*` ids land ahead of the code. The checker mirrors `check_okf_index_drift.py`'s
   conventions exactly — PEP 723 header, `--json`, the house `0/1/2` exit contract, and a
   **`--min-skills` floor**, because a checker that enumerates zero skills exits 0 on every rule
   it applies. That floor is the difference between *"the corpus is clean"* and *"the corpus was
   not read"*.
2. **Standardize the fence on the ASCII tree** (operator decision; already the plurality at 10 of
   19), so the generator is one code path and the checker one parser.
3. **Regenerate mechanically, then author the residue.** 17 of 18 layout failures fall out of a
   single `find`-diff pass, which also fixes all 10 stale roots and the `yf-okf` overclaim in the
   same sweep. Only 4 skills need authored prose.
4. **Eradicate the `install.sh` reference** from 17 READMEs, **6 `SKILL.md` files**, the project-root `README.md`, *and from `DRIFT-CHECK.md` itself* — where it appears three times, including as the declared source of truth for an edge.

**Ordering constraint that is not negotiable:** the checker must be **red** against the current
tree before the backfill runs. A checker first observed green proves nothing about its
sensitivity — it may be green because it enumerated nothing. This is the `--min-skills` argument
one level up, and it is why Epic 1 ends with a recorded red run rather than a passing one.

**Deliberate non-goal.** This plan does **not** touch `web/`, the Pelican build, the
`DRIFT-CHECK.md` manifest-coverage holes, or the OKF corpus. Those are #317 and #316. The
temptation is real — the investigation found them and they are in this bundle's findings — but
folding them back in recreates the plan the operator just split.

## Epics
### Epic 0: Pin the contract in SPEC (SPEC-first)
- Issue 0.1: Add `REQ-*` ids to `SPEC.md` for the standardized README layout-fence contract — the ASCII-tree form, its per-entry trailing `# description` comment, and the exclusion set (`__pycache__`, `.pytest_cache`)
- Issue 0.2: Add `REQ-*` ids for the skill-README completeness check: enumeration, the `0/1/2` exit contract, and the **`--json` verdict schema** — `verdict`, `skills_enumerated`, and `failures[]` whose per-finding `class` is a **CLOSED enum**: `layout | prereqs | usage | missing-readme | fence-unparseable`. Pin the enum, not just the field: SC4 passes when the `fence-unparseable` array is empty, so a checker that never emits that class satisfies it vacuously — since the Epic-1 gate and SC2/SC3/SC2b all read named fields and nothing else pins them
- Issue 0.2b: Pin the `--min-skills` floor to exit **2**, never 1. A floor that trips at 1 is byte-identical to a real FAIL, so the sensitivity gate would pass on a checker that enumerated nothing — R1 realised through its own mitigation. Exit 2 states the instrument could not run, matching `check_okf_index_drift.py:36` and the REQ-DATA-057 INCONCLUSIVE→`warn` precedent
  - depends-on: 0.1
- Issue 0.3: Record all of the above in `SPEC.md`'s living-amendment log
  - depends-on: 0.2, 0.2b

### Epic 1: Build the checker and prove it is sensitive
- Issue 1.1: Write `scripts/checks/check_skill_readme_contract.py` mirroring `check_okf_index_drift.py` conventions — PEP 723 header, depth-1 `skills/*/` enumeration (never `rglob`), `--json` emitting the Issue-0.2 schema, exit `0/1/2`, and `--min-skills N` tripping at exit **2**
  - depends-on: 0.3
- Issue 1.2: Implement the edge checks over the README axis ONLY — layout `field-set-equal` against `find skills/<name> -type f`, prereqs `field-set-subset` against frontmatter `depends-on-tool`, usage `section-present` against the SKILL.md invocation list, and `README.md` existence per skill. **`e-readme-desc` is deliberately NOT implemented** — it is the one HYBRID edge of the four, its predicate is that the README one-liner matches the SKILL.md `description` **intent**, which tolerates paraphrase and is not mechanically decidable; it keeps its LLM route. `exp-003` could only spot-check it on **3 of 20** skills and rated it **INCONCLUSIVE**, so this plan neither enforces nor claims it. The **web-page existence half is likewise NOT built here**: `exp-002` specified the pair under the combined scope, `web/` belongs to #317, and building it now would make SC2 unsatisfiable until #317 lands
  - depends-on: 1.1
- Issue 1.3: Treat a **missing README** as its own verdict class, distinct from a failing one — the `yf-okf-hygiene` case has no README to fail a contract against, and collapsing absence into mismatch is the conflation this repo has now hit three times (#181, #207, #263)
  - depends-on: 1.2
- Issue 1.4: Write tests, including a **negative test that the checker FAILS on a planted defect**, one asserting the `--min-skills` floor trips at exit **2** on an empty enumeration, and **one planting an unparseable fence** so `fence-unparseable` cannot be a class the checker never emits
  - depends-on: 1.3
- Issue 1.5: **Record the checker's RED run against the pre-backfill tree** into `findings/exp-005-checker-red-run.md` — that exact filename, because SC1 asserts it and `recheck-criteria` is a HALTING step in the §6.4 chain, so a differently-named file leaves SC1 false forever and the plan cannot close. The sensitivity evidence. Expected: 18 layout failures, 1 prereqs, 3 usage, 1 missing README
  - depends-on: 1.4

### Epic 2: Standardize the fence and backfill mechanically
- Issue 2.1: Write the fence generator emitting the ASCII-tree form from a `find` walk, preserving existing per-entry `# description` comments where present and flagging entries that have none
  - depends-on: 1.5
- Issue 2.2: Convert the 9 non-tree READMEs (`yf-plan`; `yf-research`, `yf-incubator`, `yf-beads-authoring`, `yf-beads-extra`; the four `yf-markdown-*`) to the ASCII-tree form
  - depends-on: 2.1
- Issue 2.3: Regenerate all **20** layout fences — the 19 pre-existing plus `yf-okf-hygiene`'s, authored in 3.4; regenerating only 19 would leave the newest fence the one thing nothing verifies, fixing the 12 `SPEC.md` omissions, the 10 stale unprefixed roots, and the `yf-okf` overclaim (`LICENSE`, `agents/` — which do not exist) in one pass
  - depends-on: 2.2, 3.4
- Issue 2.4: Re-run the checker; the layout edge must go green for all README-bearing skills
  - depends-on: 2.3

### Epic 3: Author the residue the generator cannot produce
- Issue 3.1: Rewrite `yf-beads-upstream/README.md` Usage — it teaches `/beads-upstream …`; the real invocation is `/yf-beads-upstream`
  - depends-on: 1.5
- Issue 3.2: Rewrite `yf-incubator/README.md` Usage — teaches `/incubator …`; real invocation is `/yf-incubator`
  - depends-on: 1.5
- Issue 3.3: Author `yf-skill-authoring/README.md` Prerequisites (frontmatter declares `depends-on-tool: [uv]`) and its absent Usage section
  - depends-on: 1.5
- Issue 3.4: Author `skills/yf-okf-hygiene/README.md` from zero — all four sections, covering `audit | assess | backfill | reindex | restore`
  - depends-on: 1.5
- Issue 3.5: Add the missing `yf-okf-hygiene` row to the project-root `README.md` skill index (`e-index-table`)
  - depends-on: 3.4

### Epic 4: Eradicate the nonexistent `install.sh` authority
- Issue 4.1: Establish the correct Install-section source of truth — `yf self install --from-build --build` and `yf skills install`, with the hosted vendor installer at `yoshikoflow.sh/install.sh` named as the distinct artifact it is
  - depends-on: 0.3
- Issue 4.2: Repair every skill README that points at a repo-level `install.sh`/`install.py`. **Two populations needing different repairs:** 13 carry it as prose, and 4 carry it as a RUNNABLE command block — `yf-beads-authoring:24` and `yf-beads-extra:22` (a bare `./install.sh`), `yf-plan:59-62` and `yf-research:28-31` (four `./install.sh` invocations each). The prose is misleading; the command blocks teach a command that cannot run
  - depends-on: 4.1
- Issue 4.2b: Repair the same residue outside READMEs. **Measured: 6 `SKILL.md` files carry 14 lines** — `yf-okf:267`, `yf-plan:170,183,199,208`, `yf-research:55,170,177,195,204`, `yf-markdown-lint:192`, `yf-optimal-instructions:197`, `yf-skill-authoring:141,147`. All 13 are preflight / rules-install prose, never invocation lines — which is why Epic 4 stays safe to run unblocked by Gate 1 — but they are still a nonexistent authority. **Also `skills/yf-research/protocols/RESEARCH.md:4`** — and that one matters most: protocol files are SHIPPED, installed verbatim to `~/.<surface>/rules/`, so it is an always-loaded rule telling every user to run a script that does not exist. (`skills/yf-plan/protocols/PLANS.md` does not match.) Spec files under `skills/*/spec/` also mention it but are internal design prose, not reader-facing instruction, and are deliberately OUT of the gate's scope
  - depends-on: 4.1
- Issue 4.3: Fix `DRIFT-CHECK.md:164,219,225` — **three hits, not two.** `:219,225` are §5 Required-Section Contracts naming `install.sh` as the required Install-section source. `:164` is a THIRD, in **§3's `e-frontmatter` contract**, which defines the frontmatter keys as *"the frontmatter `install.py` actually reads"* — an edge whose declared source of truth is a file deleted at plan-010. Repoint it at whatever reads frontmatter today. The manifest names a nonexistent authority for its own contracts
  - depends-on: 4.1
  - resolves-upstream: #247 (partial)
- Issue 4.5: Reword `README.md:42` — *"The hosted `install.sh` is a byte-for-byte mirror of cargo-dist's `yf-installer.sh`"* — to name the artifact without the bare filename (e.g. "The hosted installer script"). **This sentence is TRUE**, and Gate 2's own Instructions call the hosted vendor installer legitimate; but a regex cannot distinguish hosted from repo-level, so the gate forbids a correct statement and would block 5.1 forever. Nothing is lost: `:39` two lines above already names the file in the install URL
  - depends-on: 4.1
- Issue 4.4: Sweep the **Gate-2 path set** (`skills/*/README.md skills/*/SKILL.md skills/*/protocols/*.md README.md DRIFT-CHECK.md`) and assert zero. **NOT repo-wide** — an unscoped sweep matches 108 tracked files, 63 of them archived plan bundles, and would contradict both Gate 2's Instructions and SC5
  - depends-on: 4.2, 4.2b, 4.3, 4.5

### Epic 5: Wire enforcement and land
- Issue 5.1: Add the FAST + FULL `CHANGE-VALIDATION.md` recipe rows for the checker
  - depends-on: 2.4, 3.5, 4.4
- Issue 5.2: Add the §3 Trigger Scope globs — `skills/*/SKILL.md`, `skills/*/README.md`
  - depends-on: 5.1
- Issue 5.3: Append the `CHANGE-VALIDATION.md:6` clarification, which **must contain the literal phrase `mechanical subset`** (SC11 greps for it) — the exclusion names the *skill*, which remains true; without this a reader infers no manifest edge is ever mechanically gated, which becomes false once this checker ships
  - depends-on: 5.2
- Issue 5.4: Run the FULL tier over the merged tree and record the green run. **On red, the rollback is `git revert` of the `--no-ff` merge commit** — landing is one revertable commit by construction (§6.1), and per `AGENTS.md` this tier is the last gate before `yf self install`, so a red FULL tier must block the redeploy, not merely be noted
  - depends-on: 5.3
- Issue 5.5: Update `#315`, `#244` and `#247` with outcomes
  - depends-on: 5.4
- Issue 5.6: File the `gate_consistency.py` blind spot upstream — it returned `PASS, gates: 4, findings: []` against this bundle while two of its four gates were unsatisfiable. Not this plan's remit to fix; recording it stops the next plan rediscovering it. Adjacent to #289
  - depends-on: 5.4
  - resolves-upstream: #315 (include), #244 (include)

## Gates

> **Known grammar gap — the `test_class` / `cwd` lines below do NOT survive extraction.**
> `plan_extract.py`'s gate grammar recognizes only `Type|Approvers|Condition|Test|Blocks|Instructions`,
> so `plan_extract.py --json` reports `test_class: None` for every gate here. **At the §5.2a pour the
> executing session must set `gate_type`, `test`, `test_class` and `cwd` as bead METADATA**, per
> SKILL.md's Field vocabulary. Without that step every gate below defaults to `manual`, the §5.2c
> sweep runs none of them, and both capability gates report INCONCLUSIVE forever rather than ever
> being evaluated. Precedent and identical admonition: `plan-058`'s `## Gates`.

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: checker is sensitive before backfill
- Type: auto
- test_class: probe
- cwd: worktree
- Condition: the checker returns a FAIL VERDICT — not merely a non-zero exit — while enumerating at least 20 skills and reporting at least 18 layout failures
- Test: test -f scripts/checks/check_skill_readme_contract.py && uv run scripts/checks/check_skill_readme_contract.py --min-skills 20 --json | jq -e '.verdict=="FAIL" and .skills_enumerated>=20 and ([.failures[]|select(.class=="layout")]|length>=18)'
- Blocks: epic:2, epic:3
- Instructions: Gate on the VERDICT, never the exit code. Measured: an uncaught exception and an unresolvable PEP 723 dependency BOTH exit 1, so a bare `test $? -eq 1` is satisfied by a checker that crashed having read nothing — the vacuous-check class (#263) this plan exists to close, reproduced in its own gate. A crash emits no parseable JSON, so `jq -e` fails closed. THIS GATE IS EXPECTED TO BE RED BEFORE EPIC 1 LANDS, AND THAT IS CORRECT, NOT A DEFECT: it blocks epics 2 and 3, which must not start until the checker exists and has been shown to fail. Measured: `coordinator.md` maps ANY non-zero to FAIL and reserves INCONCLUSIVE for an ABSENT test, so no exit code can signal not-yet-built; the leading `test -f` therefore buys a clean fast failure rather than a `uv run` error dump, NOT a distinct state. At the execute-start sweep this reports FAIL with no other work blocked, and the coordinator routes around it — BUT ONLY IF `test_class: probe` was carried into the bead metadata at pour; absent it the coordinator reads `manual` and reports INCONCLUSIVE instead, and the gate is never run at all. See the grammar-gap admonition at the head of this section. Do not treat that as a defect to repair, and do not resolve it by hand. If it is still red AFTER Epic 1 lands, repair the checker, not the READMEs. **Requires `jq`** — a missing `jq` exits 127, which reads as FAIL and is indistinguishable from a red checker, so confirm `command -v jq` before trusting a red verdict. **This gate does NOT block Epic 4**, and that is deliberate: Epic 4 edits Install prose only — it adds and removes no files — so it cannot perturb the layout, prereqs, usage or existence quantities this gate measures.

### Capability Gate: no install.sh reference survives
- Type: auto
- test_class: probe
- cwd: worktree
- Condition: no SHIPPED instruction surface — skill READMEs, skill SKILL.md files, installed protocol rules, the project README, or DRIFT-CHECK.md — directs a reader to a repo-level install.sh or install.py
- Test: test "$(grep -rlE '(\./install\.(sh|py)|repo-level .?install\.(sh|py)|`install\.(sh|py)`)' skills/*/README.md skills/*/SKILL.md skills/*/protocols/*.md README.md DRIFT-CHECK.md 2>/dev/null | wc -l | tr -d ' ')" = "0"
- Blocks: 5.1
- Instructions: The path set is SCOPED to current instruction surfaces on purpose. An unscoped repo-wide grep matches 108 tracked files, 63 of them ARCHIVED PLAN BUNDLES under docs/plans/ plus this plan's own plan.md — making the gate unsatisfiable without rewriting plan history, which is not a thing this plan should do. The pattern is BROADENED for the opposite reason: the narrow 'repo-level' phrasing misses the 4 READMEs that carry a runnable ./install.sh command block, which are the worst instances. Enumerate remaining hits with the same grep minus -l. The hosted vendor installer at yoshikoflow.sh/install.sh is a DIFFERENT artifact and is legitimate to reference by URL.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step


## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | The checker is green because it enumerated nothing, not because the tree is clean | high | Three layers, because the first two were each individually insufficient: the `--min-skills` floor pinned to exit **2** (Issue 0.2b — at exit 1 it is byte-identical to a real FAIL, so R1 would be realised *through its own mitigation*), the **verdict-based** gate (a crashed checker also exits 1), and the recorded red run (Issue 1.5) |
| R2 | Fence standardization balloons the diff and buries the content repair | med | Separate the conversion (2.2) from the regeneration (2.3) into distinct commits so a reviewer can read the content change apart from the cosmetic one |
| R3 | The generator destroys hand-written per-entry `# description` comments | med | 2.1 preserves existing comments and flags entries lacking one, rather than silently emitting a bare tree |
| R4 | Scope creep back into #316/#317 — the findings for both sit in this bundle | med | The Approach section names the non-goal explicitly; Epics contain no `web/` or OKF-corpus issue |
| R5 | `find`-based equality is brittle against generated artifacts | med | Exclusion set pinned in SPEC (0.1), not in the script alone, so it is reviewable |
| R6 | Repairing `DRIFT-CHECK.md` conflicts with #317's manifest work | low | 4.3 touches §5's Install-section source **and §3's `e-frontmatter` source detail at `:164`** — a stale-authority repair Gate 2 forces, not new edge design. #317 owns §1/§2/§6 and all new edges. Recorded on #247's comment |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The checker's RED run against the pre-backfill tree is recorded as an artifact | `test -f docs/plans/plan-061-james-dixson-6d8c97/findings/exp-005-checker-red-run.md` → exit 0 | 1.5 |
| SC2 | The checker passes over the post-backfill tree while enumerating all 20 skills | `uv run scripts/checks/check_skill_readme_contract.py --min-skills 20` → exit 0 | 2.4, 3.4, 3.5 |
| SC2b | No skill README teaches an unprefixed `/beads-upstream` or `/incubator` invocation | `grep -rE '(^\|[^-a-z])/(beads-upstream\|incubator)\b' skills/*/README.md` → exit 1 | 3.1, 3.2 |
| SC3 | Every one of the 20 skills has a `README.md` | `test "$(ls -d skills/*/ \| while read d; do test -f "$d/README.md" \|\| echo x; done \| wc -l \| tr -d ' ')" = 0` → exit 0 | 3.4 |
| SC4 | All **20** layout fences parse under the single ASCII-tree parser | `uv run scripts/checks/check_skill_readme_contract.py --min-skills 20 --json \| jq -e '[.failures[]\|select(.class=="fence-unparseable")]\|length==0'` → exit 0 | 2.2, 2.3 |
| SC5 | No current instruction surface directs a reader to a repo-level `install.sh`/`install.py` | `grep -rlE '(\./install\.(sh\|py)\|repo-level .?install\.(sh\|py)\|`install\.(sh\|py)`)' skills/*/README.md skills/*/SKILL.md skills/*/protocols/*.md README.md DRIFT-CHECK.md` → exit 1 | 4.4 |
| SC6 | The checker FAILS on a planted defect, and its `--min-skills` floor trips at exit 2 | `uv run --with pytest python3 -m pytest scripts/checks/test_check_skill_readme_contract.py -q` → exit 0 | 1.4 |
| SC7 | The `CHANGE-VALIDATION.md` FULL tier is green over the merged tree | `uv run "$(yf skill-dir yf-change-validation)/scripts/change_validation.py" run --tier full --json` → exit 0 | 5.4 |
| SC8 | `yf-okf-hygiene` appears in the project-root README skill index | `grep -q 'yf-okf-hygiene' README.md` → exit 0 | 3.5 |
| SC9 | No issue in this plan modifies `web/` or the OKF bundle corpus | manual: the merged diff's path set is read at reconcile — a command asserting the ABSENCE of a path from an unmerged future diff cannot be written at authoring time | 5.4 |
| SC10 | The layout-fence and checker contracts are pinned in `SPEC.md` ahead of the code | manual: SPEC-first ORDERING is a property of commit history, not of the tree — verified at reconcile by reading git log for SPEC.md against scripts/checks/ | 0.1, 0.2, 0.2b, 0.3 |
| SC11 | `CHANGE-VALIDATION.md`'s exclusion line no longer implies that no manifest edge is mechanically gated | `grep -q 'mechanical subset' CHANGE-VALIDATION.md` → exit 0 | 5.3 |
