---
type: Plan
okf_spec: OKF-PLAN
id: plan-046-james-dixson-aabefa
author: james-dixson
created: '2026-08-18'
status: complete
deliverable_class: standard
fingerprint: 8efe609bc5613d7d79b050afc593a3de240c7d787e666c01e46c779ad911a9cb
epic: yf-mol-w3m
---
# Plan: OKF group — reconcile OKF-BASELINE to v0.2, and make bundle structure below the root generated rather than asserted

**ID:** plan-046-james-dixson-aabefa
**Author:** james-dixson
**Created:** 2026-08-18
**Status:** complete
**Deliverable-class:** standard
**Epic:** yf-mol-w3m
**Fingerprint:** 8efe609bc5613d7d79b050afc593a3de240c7d787e666c01e46c779ad911a9cb

## Objective

Three things, in dependency order:

1. **Reconcile `OKF-BASELINE.md` from OKF v0.1 to v0.2** (#141, subsuming the closed #128) —
   baseline records what OKF says verbatim; every yoshiko-flow opinion lands in
   `OKF-YF-EXTENSIONS.md`. Explicitly **no corpus migration** of existing frontmatter.
2. **Enforce OKF structure below the bundle root** (#140) — nested `index.md`, decided
   separately from nested `log.md`, as a stated **extension decision** rather than a
   conformance fix. Ship the `reindex` generation + drift-check capability **before** any
   enforcement, then backfill the existing corpus mechanically.
3. **Reconcile #92 as superseded** — not build it. Its emit half already shipped natively; its
   nested-tree half is #140. Close it with evidence.

## Motivation

`yf-okf` pins `OKF-BASELINE.md` to `okf_version: 0.1`, distilled from research project
`docs/research/001-okf-compliance-delta/`. Upstream shipped **v0.2** on 2026-08-15, whose §13
states it *"supersedes OKF v0.1"*. So the repo's declared baseline is, as of now, pinned to a
superseded revision of a spec it claims to track — and `OKF-BASELINE.md` is a **fixed authority**
node in `DRIFT-CHECK.md`, meaning every derived artifact is being checked against stale text.

The second problem is sharper and is what makes this worth a plan rather than a doc edit.
`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**: measured corpus-wide,
there are **zero** `index.md` files below any bundle root across `docs/plans/` and
`docs/research/`. A cold reader — overwhelmingly an agent — landing in a bundle's `references/`
or `findings/` must open every file to learn what the directory holds. That is exactly the cost
OKF §8 names index files to avoid: *"progressive disclosure: letting a human or agent see what
is available before opening individual documents."*

But enforcing nested indexes **creates a drift problem the moment it lands**. Four listings per
bundle across ~50 bundles, hand-maintained, is not viable, and **a stale index is worse than no
index — it asserts something false.** That ordering constraint (generation before enforcement)
is the spine of this plan, and it is the same lesson plan-045 paid for in a different currency:
an artifact that *claims* a fact nothing regenerates or checks is a liability, not a feature.

The third strand is a scope correction. #92 ("OKF export-emit integration, deferred") was
deferred in 2026-07 with explicit revisit triggers — a concrete consumer, a stable OKF release
with a non-Google adopter, or our own adoption of an OKF-consuming tool. **None has fired
cleanly.** The release trigger is **conjunctive** — "a stable release *and* a non-Google
adopter" — and there is still no upstream release or tag. Its adopter half, however, **has**
fired: four non-Google repositories were verified carrying literal OKF bundles, two at v0.2.
Trigger (c) fired on capability but not demand (D-8). Meanwhile the *reason* to defer partly
dissolved on its own: bundles now emit `type:` / `okf_spec:` frontmatter and root
`index.md`/`log.md` natively, and the remaining "whole-bundle nested `index.md` tree" that #92
called its true cost **is #140**. Leaving #92 open as a live tracker misrepresents both what is
built and what is wanted.

## Upstream Issues

**Coarse tracker:** [#167](https://github.com/dixson3/yoshiko-flow/issues/167) — `plan-046-james-dixson-aabefa execution tracking`.

| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| [#167](https://github.com/dixson3/yoshiko-flow/issues/167) | plan-046-james-dixson-aabefa execution tracking | tracker | Coarse plan-scale tracking issue (AGENTS.md coarse convention). Not a work row. | — |
| #141 | yf-okf: reconcile OKF-BASELINE from v0.1 to OKF v0.2 (supersedes #128) | include | Baseline to v0.2 verbatim + extension-layer concept mapping. **No corpus frontmatter migration.** | 2.9 |
| #140 | yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model | partial | **IN:** root-scoped `reindex --check`/`--write`, the drift model, the root backfill, the two extension decisions. **OUT:** nested `index.md` (deferred, D-9 — filed upstream by 5.5), nested `log.md` (dropped permanently, D-4), promotion to error-level enforcement (recorded not executed, 4.5). The `audit-close` half already shipped in plan-043 (#148). | 4.5 |
| #92 | OKF export-emit integration for yf-plan/research/incubator (deferred) | supersede | **Three named carve-outs** (projection delivery mode; conformance gate for yf-research and yf-incubator; consumer round-trip fidelity), filed by 5.5. Reconcile with mechanical evidence, do not build. | 5.6 |
| #118 | yf-plan README.md stale: still lists README.md as plan-folder orientation file (pre-OKF) | include | Four sites, not the two named. Local bead `yf-m78m`. The larger File Layout defect is split to 5.4. | 5.3 |

## Scoping Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| **D-1** | **#92 is reconciled as superseded — with three NAMED carve-outs, not cleanly.** | Its emit half is measurably shipped (exp-004) and its nested-tree half is #140's content. But a clean close silently drops three things: projection delivery mode; conformance gate for yf-research and yf-incubator; consumer round-trip fidelity. Revised at investigation: the original D-1 said "bifurcated into shipped + #140", which exp-004 refuted. |
| **D-2** | **Baseline to v0.2 + extension-layer mapping; NO corpus frontmatter migration.** | Confirmed, and for a **stronger** reason than originally stated: the repo emits `timestamp` **0** times and `# Citations` **0** times. yf independently declined both v0.1 features long before v0.2 retired them, so exposure to both breaking changes is exactly zero. |
| **D-3** | **Generation before enforcement — retargeted from the NESTED tier to the ROOT tier.** | The ordering principle survived; the tier did not. exp-003 measured `description` at **0 of 423** nested files, so every generated nested entry reads `*description pending*`; **74 of 142 (52%)** of subdirectories would get a listing of no value; and root indexes already carry described subdirectory entries in **16 of 19** bundles. Meanwhile real drift exists at the root **today** — 25 ghost entries + 15 unlisted files — invisible because `okf.py check` does no link resolution at all. **Correction (pass 1):** an earlier draft also claimed the nested rule would block `audit`, and therefore intake. **That was false — see D-12.** The retargeting stands on the grounds above, which are measured. |
| **D-4** | **Nested `index.md` and nested `log.md` decided separately — and they resolve differently.** | Nested `log.md`: **dropped permanently**. Measured 1–2 distinct commit dates per subdirectory, and every `okf.append_log` call site targets the bundle **root** — no producer event is scoped below it, so nothing would populate it. Nested `index.md`: **deferred behind a `description:` producer change** (D-9). |
| **D-5** | **Every v0.2↔yf mapping is recorded as AGREE / DIVERGE / ABSENT — never silently reconciled.** | Vindicated hardest on the credibility axis. v0.2 §5.1 **forbids storing a score**; yf stores one; and yf's own most careful research bundle contains a hand-written retraction of that score plus a manual category override. **#147 is the stored-score design failing in the documented way, not a heuristic bug** — so no "alignment by renaming". |
| **D-6** | **`_shared/test_okf.py` is gated BEFORE `okf.py` is touched — via six §3 rows, not a `_shared/**` tweak.** | Confirmed and **widened**. exp-001 measured that `skills/yf-okf/scripts/okf.py` and `skills/yf-incubator/scripts/okf.py` match **no §3 glob at all** and return a **vacuous PASS with zero commands executed** — on a scratch tree where `sync.py --check` exits 1 (the live tree is EXIT=0, all five byte-identical — exp-001's claim is scoped to its own mutated copy). That is worse than "the right test does not run": the verdict reads green. |
| **D-7** | **`status` is a declared PERMANENT divergence — yf declines v0.2 §5.4, even for new emissions.** | The one key where two spellings coexisting is **not** benign, because they are two *vocabularies on the same key*. It is read at a gate with the literal `"approved"` (`plan_manager.py:2152`), and already carries three meanings (yf-plan workflow, yf-research pipeline phase, v0.2 lifecycle). Corpus overlap with v0.2's vocabulary is `draft` only, 2 of 46. |
| **D-8** | **Trigger (c) partially fired: the CAPABILITY precondition, not the DEMAND precondition.** | Operator ruling. `bp/skills/okf-lint` is a genuine first-hand OKF-consuming tool we did not have on 2026-07-19 — but it governs the book vault and touches **zero** yf-\* bundles, so it creates no demand for #92's export projection. Supersede stands; the record is corrected rather than the conclusion changed. |
| **D-9** | **Nested `index.md` is deferred behind a `description:` producer change, and the deferral is RECORDED with its measurement.** | Not dropped and not silently shelved. Once producers stamp `description:`, nested indexes become worth generating **forward-only** and the backfill question dissolves on its own — old bundles keep their hand-written root index, new ones get real descriptions. |
| **D-10** | **New `reindex` findings land at WARNING level — belt-and-braces, not load-bearing.** | The audit already cannot surface them (D-12). Warning level is chosen anyway, because relying on an allowlist's *silence* is the same class of implicit guarantee this plan is written against, and because promotion to error (4.5) is a real future change that should not have to re-litigate the level. Promotion stays gated on a green corpus. |
| **D-11** | **The 31 bundles with NO root `index.md` are explicitly OUT of scope.** | Measured: 50 bundles, 19 indexes. Creating 31 new root indexes is a different change with a different consent profile from "regenerate 19 existing listings" — it authors orientation prose for legacy bundles. `reindex --check` returns **`no-index` (exit `2`)**, never `0`, for an index-less bundle, so their absence can never be mistaken for cleanliness. |
| **D-12** | **CORRECTION (pass 1): a new check CANNOT block `audit`. The earlier claim that it could was wrong.** | `plan_manager.py:3967` reads `if cf.level != "error" or cf.req not in _OKF_PORT050_REQS: continue` against `frozenset({"REQ-OKF-003","REQ-OKF-030","REQ-OKF-031","REQ-OKF-071"})` (`:3525`) — an **allowlist**, not a fold — and its source comment states REQ-OKF-001 is *"deliberately excluded"*. Missing `index.md` is emitted under REQ-OKF-001 (`_shared/okf.py:804`), so exp-003's 128 simulated findings would have been filtered at **any** level. Recorded rather than quietly patched: the false claim had exactly the shape this plan is written against — an assertion derived from *reading* code, presented as measured. Issue 3.8 now measures it by execution. |

## Investigation Findings

Four experiments, all read-only. Two materially revised the approved scope.

| Finding | Verdict |
| :-- | :-- |
| [exp-001](findings/exp-001-okf-blast-radius.md) | The gate on `okf.py` is not thin, it is **absent, and reports green.** Two of four vendored copies match no §3 glob; FAST returns `{"status":"pass","commands":[]}` on a divergent tree. `render_index` — the function this plan rewrites — is the least-tested in the suite (a mutation survived all 31 tests). |
| [exp-002](findings/exp-002-okf-v02-delta.md) | Exposure to both v0.2 breaking changes is **zero**. §13 is accurate but **incomplete** — it omits a `SHOULD NOT` → `MUST NOT` upgrade on the extension clause, and every section number moved. Two yf mechanisms have **no v0.2 counterpart** (the content fingerprint, strictly stronger than `stale_after`; the persisted `- validated:` receipt, which v0.2 §12 explicitly defers). |
| [exp-003](findings/exp-003-reindex-and-corpus-backfill.md) | **The nested backfill does not survive contact with the corpus.** `description` is 0/423. 128 findings, 50/50 bundles, 14/14 passing bundles broken. The real drift is at the **root**, today: 25 broken links + 15 unlisted files, invisible because `okf.py check` does no link resolution. |
| [exp-004](findings/exp-004-92-supersede-evidence.md) | Supersede holds, **with carve-outs**. The emit half shipped **8h39m before the deferral was recorded**. #92's stated rationale ("no confirmed non-Google adopter") is now **measurably false** — four verified adopters, two at v0.2. `emit_conformant_copy` is spec'd, unreachable, and untested. |

### The through-line

Three of the four findings are the same defect wearing different clothes: **an artifact asserting something nothing checks.**

- A **validation manifest** that reports `pass` having run zero commands (exp-001).
- An **index** that links files which do not exist, in production, right now (exp-003).
- A **SPEC `Verification:` line** that names a command nothing executes (exp-004, an instance of open #165).
- A **deferral rationale** whose stated premise was falsified by a commit nine hours older than it (exp-004).

That is the same class plan-045 documented and #165/#166 track. This plan does not set out to fix it generally — but every epic below is ordered so the check exists **before** the thing it checks.

## Approach

**Five epics, strictly ordered. The ordering is the design.**

1. **Gate the engine before touching it.** `okf.py` is vendored byte-identical to four locations and currently has an *absent* gate that reports green. Every later epic edits it. Wiring the suite first is what makes the rest of the plan verifiable rather than merely done.
2. **Reconcile the baseline to v0.2.** A documentation edit plus a one-constant bump — small enough that the gate from Epic 1 is the interesting part, which is precisely why it goes second.
3. **Build `reindex`, root-scoped.** Generation and drift-detection, warning-level, non-gating.
4. **Backfill the root corpus.** One mechanical pass, reviewed in aggregate, behind a human gate.
5. **Reconcile the upstream record.** #92 with carve-outs, #118, and the extension-layer decisions — including the ones that record what this plan deliberately did *not* build.

SPEC edits lead each epic, per the project's SPEC-first rule, and are mechanically forced: `DRIFT-CHECK.md` §7 marks `spec` and `per-skill-spec` as **fixed authority**, so editing an implementation ahead of its requirement produces a CONFLICT rather than a FAIL.

## Epics

> **Reading note.** Issues carry `pass-N` annotations recording what a review cycle changed and why. **The instruction is always the first sentence**; the annotations are provenance, kept inline because pointing at a review file failed once (pass 3, H2).


### Epic 1: Gate the engine before touching it

- Issue 1.1: **SPEC-first.** Resolve the dangling `REQ-OKF-034` cross-reference in `skills/yf-okf/SPEC.md:53` (measured: referenced exactly once, never defined). **Confirm the intended id from `git log`/`git blame` on that line before editing** — `REQ-OKF-031` is the likely target, but this is a **fixed-authority** SPEC and by this plan's own standard a hedge is not a basis for an authority edit. If it cannot be confirmed, record the uncertainty in the edit rather than resolving it silently. Under `DRIFT-CHECK.md` §7 an authority naming a non-existent identifier is a CONFLICT-and-halt, so this clears the way for allocating nearby ids.
- Issue 1.2: Add the `uv-okf` id to CHANGE-VALIDATION.md §1 **in both the `fast` and `full` tiers** — `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q` (measured working; plain `--with pytest` fails on `ModuleNotFoundError: yaml`).
- Issue 1.3: Add the six §3 trigger-scope rows, **with the id mapping stated per row** (pass 2 — an earlier draft named the paths but no ids, leaving R2's mitigation assigned to nobody):

  | path | ids |
  | :-- | :-- |
  | `_shared/okf.py` | `uv-okf`, `uv-_shared` |
  | `_shared/test_okf.py` | `uv-okf` |
  | `skills/yf-okf/scripts/**` | `uv-okf`, `uv-_shared` |
  | `skills/yf-incubator/scripts/**` | `uv-okf`, `uv-_shared` |
  | `skills/yf-plan/scripts/okf.py` | `uv-okf`, `uv-_shared` |
  | `skills/yf-research/scripts/okf.py` | `uv-okf`, `uv-_shared` |

  `uv-_shared` (`sync.py --check`) is the **vendor-drift** detector and today fires on **none** of the four vendored copies — so without these rows a hand-edited copy diverges silently. Glob resolution is a **union**, not first-match (verified), so adding rows is additive and cannot displace existing ids. **Document the real rationale for the explicit file target** — exit 4 on a moved/renamed target. Do **not** restate plan-042's "a filter passes vacuously" claim: measured, pytest exits **5** on a no-match filter, so that rationale is cargo-specific. **Correct it at its source too** — `CHANGE-VALIDATION.md:9-14` still asserts it in the header blockquote, and this issue already edits that file.
  - depends-on: 1.2
- Issue 1.4: **Verify the gate fires and fail-closes.** Confirm the two previously-`[]` paths now execute commands, and inject a temporary mutant to confirm FAST reports `status: fail` with `uv-okf` as `first_failure`. Revert the mutant. This issue exists because the defect being fixed is *a gate that reported green having run nothing* — asserting the fix without executing it would reproduce it.
  - depends-on: 1.3
- Issue 1.5: Add `render_index` and index-drift coverage to `_shared/test_okf.py`. Measured hole: a mutation disabling the reserved-file filter left all 31 tests green while `render_index` regressed to emitting `- [log.md](log.md)`. Epic 3 rewrites this function.
  - depends-on: 1.4
- Issue 1.6: Run the FULL tier once and record the result, closing exp-001's largest honest limit (it inferred FULL's behavior from the manifest rather than an executed run).
  - depends-on: 1.5

### Epic 2: Reconcile OKF-BASELINE to v0.2

- Issue 2.1: **Fetch OKF v0.1 verbatim** from a prior upstream commit of `okf/SPEC.md` and vendor it to `references/okf-spec-v0.1.md`. This closes exp-002's largest limit: v0.1's §1/§2/§6/§7 bodies were never quoted in-repo, so undeclared changes there could not be ruled out — and one undeclared change was already found *inside* the verified subset.
  **Fallback, because everything downstream chains through this issue.** If v0.1 is unrecoverable (squashed history, spec first added at v0.2, path renamed), **do not block the epic**: record the unrecoverability as a finding, fall back to the three in-repo verbatim copies exp-002 used (`OKF-BASELINE.md:149-151`, `sources.md:46`, `Summary.md:154`), and carry §13's incompleteness forward as a **stated limit** in Issue 2.4's verification subsection.
  - depends-on: 1.6
- Issue 2.2: **SPEC-first.** Allocate the REQ ids **Epics 2 AND 3** need — including the `reindex` verb and the drift-finding req Issue 3.6 lands under, which pass 2 found named nowhere — from the measured block-local next-free set (`REQ-OKF-004`, `-011`, `-022`, `-032`, `-051`, `-061`, `-072`; `CHK-002`; `FAM-005`; `MIG-006`) and record the v0.2 pin as a requirement.
  - depends-on: 1.6, 2.1
- Issue 2.3: Rewrite `spec/OKF-BASELINE.md` against the vendored v0.2 verbatim. Named wrong-after sites: **L141** (`timestamp` row), **L167** + **L171–178** (`# Citations`), **L149–151** + **L157–160** (the force upgrade), **every `(§N)` cross-reference** in §3/§4/§5/§6/§7/§7a, and the **three** places claiming OKF is silent on log ordering. Two are here (§4, §7a bullet 1); **the third is `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md:84`** — *"OKF reserves `log.md` as 'update history' but demonstrates no format and no ordering"* — assigned to **Issue 2.6**, which already edits that file. Under v0.2 §9 that premise is false, and yf's rule at `:89` stops being an extension decision and becomes baseline conformance. **It is fixed authority and there is no `spec`→`spec` edge in `DRIFT-CHECK.md`, so nothing would have detected it** (found at pass 4; the plan's own `exp-002:50` named all three while the issue named two).
  **Budget an expected drift FAIL.** `DRIFT-CHECK.md:80` scopes `skills/*/spec/*.md` → `e-spec-compliance` (`spec`→`skill-md`), so this edit will fire against `skills/yf-okf/SKILL.md` mid-epic. That is expected and recoverable — resolve it in the same pass rather than treating it as a halt. **Emit an explicit v0.1→v0.2 section map** (index §6→§8, log §7→§9, conformance §9→§11, versioning §5→§12, …) as part of this issue — SC4 is checked against that table, because v0.2 uses identical `(§N)` syntax and no grep can distinguish a surviving v0.1 reference from a correct v0.2 one — v0.2 §9 now specifies newest-first with an ISO-8601 MUST, **and yf guessed right**.
  - depends-on: 2.2
- Issue 2.4: Add a **§13-verification subsection** recording that §13 is accurate but omits the `SHOULD NOT` → `MUST NOT` upgrade in §4.1 and does not flag the renumbering. Quote v0.1's clause alongside v0.2 line 219 so the delta is auditable.
  - depends-on: 2.3
- Issue 2.4a: **SPEC-first for the version pin — the three FIXED-AUTHORITY sites, before the constant moves.** Amend `skills/yf-plan/spec/portability.md:19` (REQ-PORT-001), `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md:33`, and `skills/yf-okf/SPEC.md:201`, each of which states the pin as `0.1`. **If the constant is bumped first, the producer emits `0.2` while three fixed-authority documents say `0.1` — a `DRIFT-CHECK.md` §7 CONFLICT-and-halt mid-Epic-2, with Epics 3–5 chained behind it.** Added at pass 3.
  - depends-on: 2.4
- Issue 2.5: Bump `okf_version = "0.2"` in `_shared/okf.py`, re-vendor with `sync.py`, and update **every** remaining site. **The blast list is the EXECUTED corpus grep**, `grep -rniE "okf_version.*0\.1|OKF v0\.1" skills/ _shared/` — **widened at pass 4**, because the earlier `okf_version`-only form missed every bare `OKF v0.1` prose claim. Measured: the widened command returns **30 hits across 17 files**, of which **16 across 8 files** are the newly-caught bare-prose subset, including three `OKF-EXTENSION.md` files (`yf-plan`, `yf-research`, `yf-incubator`) that no earlier draft named:
  - the constant itself in all five copies (`_shared` + four vendored, each `:48`);
  - `_shared/test_okf.py:504` (`assert okf.okf_version == "0.1"`), `test_worktree.py:1179`, `:1296`;
  - prose sites `skills/yf-okf/SKILL.md:43`, `skills/yf-okf/README.md:84`, `skills/yf-plan/agents/captor.md:44`;
  - the bare `OKF v0.1` prose claims in `skills/yf-okf/{SKILL.md,README.md,SPEC.md}`, `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md`, and `skills/{yf-plan,yf-research,yf-incubator}/OKF-EXTENSION.md`;
  - *(the three fixed-authority `okf_version` spec sites are Issue 2.4a; `OKF-BASELINE.md` is Issue 2.3.)*

  **Corrected at pass 3.** An earlier draft called three test sites "the complete measured blast list" — derived from grepping tests, not the corpus. Six further non-test sites exist and three are fixed authority. That is the same over-claim shape this plan is written against.
  - depends-on: 2.4a
- Issue 2.6: Record the five mapping entries in `spec/OKF-YF-EXTENSIONS.md`, each labelled **AGREE / DIVERGE / ABSENT**: `sources`+credibility (DIVERGE — cite the `sources.md` retraction and the reproduced #147 output; **do not propose a rename**); `verified[]`/`stale_after` vs `verdict`/`fingerprint` (DIVERGE — yf's hash is stronger and not expressible in v0.2); `status` (COLLISION → permanent divergence per D-7); `generated.by` (ABSENT — a pure gap); Attested Computation vs `- validated:` (AGREE in determinism, **and yf persists a receipt v0.2 §12 explicitly defers**).
  - depends-on: 2.5
- Issue 2.7: Fix `OKF-YF-EXTENSIONS.md` **L37** — `status` moves from *Owner: yf* to *Owner: OKF (v0.2 §5.4), yf declines*. **Also fix `:84` in the same file** — the third "OKF is silent on log ordering" site assigned here by Issue 2.3. *(Restated in this issue at pass 5 so a per-bead executor claiming 2.6 in isolation cannot miss an assignment made in 2.3's text.)*
  - depends-on: 2.6
- Issue 2.8: Promote `spec/OKF-BASELINE.md` to a **named node** in `DRIFT-CHECK.md` and add an edge to the engine's version pin. Measured gap: the baseline itself declares a coupling to the baked-in ruleset, and **no edge encodes it** — a v0.1→v0.2 edit fires nothing that inspects `okf_version`.
  - depends-on: 2.7
- Issue 2.9: Mark `docs/research/001-okf-compliance-delta/` superseded with a yf-owned **`superseded_by:`** key plus the `type`/`okf_spec` frontmatter it lacks entirely. A **named exception** to D-2's no-migration rule, not a silent violation. Rationale: `OKF-BASELINE.md` L210–212 cites 001 as its provenance, so leaving it unmarked keeps v0.1 facts flowing into the layer being rewritten.
  - depends-on: 2.8
  - resolves-upstream: #141 (include)

### Epic 3: `reindex` — root-scoped generation and drift detection

- Issue 3.1: **SPEC-first.** Specify the `reindex` verb and its drift semantics in `skills/yf-okf/SPEC.md` against the ids allocated in 2.2. State the root-only v1 scope explicitly, with the D-9 deferral recorded beside it. **Also specify the bundle-root predicate itself** — `okf.py` today has *no notion of bundle-root*: `scaffold` (`:320`), `_read_index` (`:344`) and `render_index` (`:356`) each receive a bare directory and cannot distinguish a root from a subdirectory. Decide the rule here (presence of `plan.md`? a direct child of the configured plans/research root? an explicit `root=True` argument?) rather than discovering it at implementation time.
  **Also specify the `no-index` state** (D-11): a bundle with no root `index.md` is neither clean nor drifted. It is its own verdict with its own exit code — **`2`**, distinct from `0` clean and `1` drift, so the 31 legacy bundles can never be counted as green. Added at pass 2 — SC6 and Issue 4.4 asserted this behavior while no issue built it and no requirement specified it, which under the fixed-authority rule is a CONFLICT.
  - depends-on: 2.9
- Issue 3.2: **Make `okf_version` emission conditional on bundle-root** at the three unconditional write sites — `scaffold_bundle` (`:293`, frontmatter at `:320`), `_read_index` (`:340`/`:344`) and `render_index` (`:347`/`:356`). *(Pass 2: an earlier draft named a `write_index` function that does not exist; the line numbers were right.)* v0.2 §8 forbids frontmatter on a non-root index.
  **Premise corrected twice, in opposite directions.** An earlier draft claimed *"all 23 current indexes happen to be roots"* — false: **four are nested**, under `docs/plans/plan-029-.../findings/okf-migration-samples/*/after/`, and `incubator-bundle/after/index.md` opens with `okf_version: '0.1'`, the frontmatter §8 forbids. Pass 2 then **over-corrected**, calling this *"a LIVE violation, not a latent one"*. That over-shoots: those four are the **frozen migration fixtures Issue 4.1 explicitly refuses to touch**, written once by a one-off sample generator — **no live producer path emits them**. Both errors are recorded: they are the same failure in opposite directions, and the second was made while fixing the first.
  **Justification:** a **latent-defect fix**, not a prerequisite of anything this plan builds — D-9 defers nested indexes, so nothing here will generate one. It ships now because it is cheap, because it is a real conformance violation waiting on the first caller, and because `reindex` is the thing that will eventually be pointed below the root.
  **Evidence:** exp-002 §5 Carve-out 2 predicts this and labels itself *inferred, uncorroborated*; **exp-003 §5 MEASURED it**, running `render_index` against a scratch nested directory and observing the emitted `okf_version` frontmatter. Cite the measured one.
  - depends-on: 3.1
- Issue 3.3: Implement `reindex --check <bundle>`: report `missing` (present but unlisted), `ghost` (entry whose relative target does not resolve — covers dead files *and* dead dirs), `empty-dir`. Report `no-index` for a bundle with no root `index.md` (D-11) — **never** silently clean. Exit **`0`** clean / **`1`** drift / **`2`** `no-index`, JSON on every path. **No "stale metadata" check** — with `description` at 0/423 there is no metadata to go stale.
  **Handle the presence-optional case — decided at pass 2: FIX THE PRODUCER (Issue 4.2a), do not exempt.** The scaffold emits an `index.md` link to `plan-retrospective.md` unconditionally, but that file is **presence-optional** (REQ-PORT-ACT-RETROSPECTIVE) and absent from most bundles — so a naive `ghost` check flags every newly-scaffolded bundle. Observed live in this plan's own bundle: `index.md:20 ML003 broken link target: plan-retrospective.md`. The exempt branch is rejected on **layering**: it would require `_shared/okf.py` — the *baseline* engine — to know a yf-plan-specific optionality list (`RETROSPECTIVE_FILE` lives in `plan_manager.py:635`), inverting the baseline/extensions separation this plan exists to protect.
  - depends-on: 3.2
- Issue 3.4: Implement `reindex --write <bundle>` with prose preservation between `<!-- intro:start/end -->` / `<!-- notes:start/end -->`. Port two guards from `bp/okf-lint` **by approach, not by code**: `check_markers()` **hard-errors** on an unbalanced marker (a `:start` with no `:end` silently discards prose, unrecoverably), and `discarded_prose()` warns on dropped non-generated lines. **Live case:** `plan-045/index.md` carries a hand-written `## Note on scope-answers.md` a naive regenerator would delete. **Never invent a description** — preserve an existing one, emit a bare `- [title](path)` for a new entry rather than `*description pending*`.
  - depends-on: 3.3
- Issue 3.5: Tests for 3.2–3.4 in `_shared/test_okf.py`, including the marker-imbalance hard error and the prose-preservation case.
  - depends-on: 3.4
- Issue 3.6: Wire ghost/missing into `okf.py check` as **`warning`**-level findings under the new REQ allocated in 2.2.
  **Rationale, corrected at pass 2.** An earlier draft said to place the REQ *"explicitly outside `_OKF_PORT050_REQS`, so step 7 cannot promote them to fail and block intake"*. Both halves were wrong: the set is a literal four-element `frozenset`, so a new REQ is outside it **by construction** — there is nothing to do, and an executor would look for an action that does not exist — and the block-intake mechanism does not exist either (D-12). The real reason for warning level is D-10: **not depending on an allowlist's silence**, and not making the future promotion-to-error (4.5) re-litigate the level.
  - depends-on: 3.5
- Issue 3.7: Re-vendor via `sync.py` and confirm the Epic-1 gate observes the whole change — the end-to-end proof that D-6 bought something.
  - depends-on: 3.6
- Issue 3.8: **Measure the audit's actual behavior by EXECUTION, not by reading** (SC8, and the fix for D-12's false claim). Run `uv run skills/yf-plan/scripts/plan_manager.py audit <bundle>` **from the repo tree** against a bundle carrying a synthetic finding emitted at **`error`** level under the new REQ (a temporary local mutation, reverted — the same shape as Issue 1.4's mutant), and confirm it still exits 0.
  **The error level IS the discrimination, and pass 2 caught this.** The filter is `if cf.level != "error" or cf.req not in _OKF_PORT050_REQS`. Issue 3.6 lands the real finding at *warning*, so a warning-level synthetic is discarded by the **first** clause and never reaches the allowlist — it would test D-10 while appearing to test D-12.
  **Add a positive control:** an *allowlisted* error req (e.g. `REQ-OKF-003`) must produce a **non-zero** audit. Without it a green result is indistinguishable from a harness that cannot observe failure at all.
  **Assert the revert before closing** (`git diff --quiet` on the touched path). Issue 4.1 now depends on 3.8, so an unreverted mutant would have 4.1 measure a mutated tree. **The invocation path is the whole point:** a bare `plan_manager.py audit` resolves through `SKILL_DIR` to the *installed* skill, which imports its own vendored `okf.py` — it would exercise the **old** engine and report green regardless of what 3.6 did. This issue exists because a claim about this exact code path was asserted from reading it, and was wrong.
  - depends-on: 3.7

### Epic 4: Backfill the root corpus

- Issue 4.0: **SPEC-first for Epic 4.** `REQ-PORT-001` (`skills/yf-plan/spec/portability.md:19`) enumerates the listing members as *"(`plan.md`, `context.md`, `findings/`, `reviews/`, `references/`)"* — `upstream-triage.md` is **not** among them, and `_INDEX_MEMBERS` matches the REQ, not the corpus. So 4.2a(a) is a behavior change against a **fixed-authority** spec with no allocated requirement. Amend that enumeration, and for the research side allocate **`REQ-PORT-010`** in `skills/yf-research/spec/portability.md` (measured next-free: that file uses `REQ-PORT-001…009`, and `REQ-PORT-009:38` governs the reserved-file split but **enumerates no listing members**, so there is no analogous clause to amend — a new requirement is needed, not an edit). Both before any producer change. *(Added at pass 3 — structurally identical to the Epic-3 id gap the plan already treated as blocking. 4.2a(b) needs no amendment: `REQ-PORT-051` already says "When present … is listed", so the unconditional emission is a plain implementation bug.)*
  - depends-on: 3.8
- Issue 4.1: Run `reindex --check` over **the corpus, explicitly defined** (pinned at pass 2) as `docs/plans/*/index.md docs/research/*/index.md` — a **single-level** glob. **Never `docs/**/index.md`:** that would sweep the four frozen `plan-029/findings/okf-migration-samples/*/after/index.md` migration fixtures and let `--write` regenerate them, **destroying the recorded evidence of a completed plan**. Record the **pre-state** verbatim. **Expected: 40 items — 25 ghost entries (24 dead *directory* links + 1 dead file) + 15 unlisted files.** Corrected at pass 1: an earlier draft wrote "25 + 15 + 1", double-counting the dead file, which *is* the 1 ghost exp-003 reported separately. Note the unit mismatch that caused it — `markdown_lint` counts link violations while exp-003's prototype scored `ghost=1` because it did not resolve **directory** targets; Issue 3.3 broadens ghost to cover dead dirs, which is what makes the two agree.
  - depends-on: 4.0
- Issue 4.2a: Fix the **yf-plan** producer scaffold (`_INDEX_MEMBERS`, `plan_manager.py:622-631`) on three axes — (b) and (c) added at pass 1, (c) the largest:
  - (a) `upstream-triage.md` is unlisted in **8 of 19** root indexes — a systematic producer bug, not 8 independent oversights.
  - (b) The scaffold emits an unconditional link to the presence-optional `plan-retrospective.md`, producing a broken link in every bundle that never records one. *(Live in this plan's own bundle: `index.md:20`.)*
  - (c) **The template emits unconditional `findings/`, `diagrams/`, `assets/`, `references/` entries for directories that older bundles do not have — this is 24 of the 25 live ML003 violations**, and therefore the bulk of the defect. **Decided at pass 3: emit only for directories that EXIST.** The alternative — having `scaffold` create them — is self-defeating on two counts: **git does not track empty directories**, so a scaffolded `diagrams/`/`assets/` vanishes on clone and the ghost link returns; and it would generate exactly the `empty-dir` drift Issue 3.3 reports. *(This decision was claimed as applied at pass 2 and was not — the fourth instance of an over-stated resolution in this plan, which is why the reason is now inline rather than living only in a review file.)*
  - **Verify by scaffolding a THROWAWAY plan bundle** (SC7's stated method) and asserting the new index has no ghost and lists `upstream-triage.md` — **not** by re-inspecting the corpus this epic just edited. Invoke the **repo** copy explicitly (`uv run skills/yf-plan/scripts/plan_manager.py …`); a bare invocation resolves through `SKILL_DIR` to the *installed* skill and would test the old producer.
  - depends-on: 4.1
- Issue 4.2b: Fix the **yf-research** producer — a genuinely separate codebase, split out at pass 3 because 4.2 had grown to four axes across two producers and was no longer one deliverable. `docs/research/002/003/004` are produced by `index_manager.py` / `okf.add_index_entry`, and exp-003 measured *their* omissions (`plan.yaml`, `sources.json` — 3 of the 15 unlisted files). Fixing those three indexes in the sweep while leaving the producer that re-breaks them is precisely the backfill-without-generation ordering this plan's spine forbids. **Measure the research scaffold's actual output FIRST, then scope.** Whether `index_manager.py` also has the presence-optional-ghost and absent-subdirectory defects is **unmeasured** — do not assume it mirrors the yf-plan producer. Fix what it actually emits, and **verify with its own throwaway research bundle**, repo copy.
  - depends-on: 4.2a
- Issue 4.3a: Run `reindex --write` over the corpus **as defined in 4.1** (single-level glob; plan-029 fixtures excluded) **in the execution worktree**, render `git diff` over the affected indexes, and present the aggregate. **Ungated** — this issue produces the evidence the gate consumes, so gating it would be the cycle `red-team.md` warns about.
  - depends-on: 4.2b
- Issue 4.3b: **Commit the worktree changes 4.3a already wrote** — a commit, not a second generation pass; it does not re-run against the primary tree. Revert is `git checkout` on the affected worktree paths (R3). **Blocked by the Backfill Review gate.**
  - depends-on: 4.3a
- Issue 4.4: Verify `reindex --check` is green across **the 19 bundles that carry a root `index.md`** (D-11 — the other 31 must exit **`2`** (`no-index`), never `0`) **and** that `markdown_lint.py --rules ML003` is clean over the same single-level glob 4.1 pins (`docs/plans/*/index.md docs/research/*/index.md`). Two independent checks, because the second is what surfaced the defect in the first place.
  - depends-on: 4.3b
- Issue 4.5: Record — do **not** execute — the promotion-to-error decision, gated on 4.4 being green. Promotion is a separate, later change; landing it in the same pass would mean enforcing against a corpus whose greenness was verified minutes earlier by the same session. **Close #140 as `partial`** so a future reader cannot conclude the nested tier was built. The close comment carries this list verbatim (inlined at pass 2 rather than pointed at):
  - **IN:** root-scoped `reindex --check`/`--write`; the drift model; the root backfill; the two extension decisions.
  - **OUT:** nested `index.md` (deferred, D-9 — filed by 5.5(iv)); nested `log.md` (dropped permanently, D-4); promotion to error-level enforcement (recorded, not executed).
  - depends-on: 4.4
  - resolves-upstream: #140 (partial)

### Epic 5: Reconcile the upstream record

- Issue 5.1: Record in `spec/OKF-YF-EXTENSIONS.md` the two decisions this plan made by **not** building: nested `log.md` **dropped permanently** (with the 1–2-distinct-dates measurement and the no-producer-event finding as rationale), and nested `index.md` **deferred behind a `description:` producer change** (D-9), with exp-003's 0/423 measurement recorded so a future reader inherits the evidence rather than the conclusion.
  - depends-on: 4.5
- Issue 5.2: Resolve `emit_conformant_copy` — spec'd at `SPEC.md:28,194`, **zero callers, zero tests, not a CLI verb**. **Pre-decided at pass 1: DELETE it and amend the SPEC.** Exposing it as a verb would mean building the on-demand projection that D-1/exp-004 established has **no fired demand trigger** — reopening scope this plan closed. Reviving it is what **Issue 5.5(i)** tracks — filed explicitly, so the deletion does not erase the record of what was deleted. Leaving it as-is is how a future investigator concludes the projection "exists". **Re-vendor via `sync.py` in this issue**, since it edits `_shared/okf.py` after Epic 3's last re-vendor and SC3 asserts `sync.py --check` exits 0.
  - depends-on: 5.1
- Issue 5.3: **#118** — fix all four things at the two sites in `skills/yf-plan/README.md`: the two stale README-as-orientation lines (`:97`, `:144`) **and** the two omissions the issue does not name (`index.md`/`log.md` absent from both the portability-contract list at `:95-101` and the layout block at `:140-155`; measured: **zero** hits for either filename in the entire file). Also update #118's own drifted citation — it cites `SKILL.md:245`; the correct content is now `SKILL.md:262`.
  - depends-on: 5.2
  - resolves-upstream: #118 (include)
- Issue 5.4: File the skill-dir **File Layout** staleness separately (`README.md:106-138`, ~20 omissions including `SPEC.md`, `OKF-EXTENSION.md`, `test-harness/`, and 18 of 21 `scripts/` files). Same file, different defect — folding it into #118 would make #118 unreviewable.
  - depends-on: 5.3
- Issue 5.5: File **four** follow-on issues. **(i) was missing entirely until pass 2** — three separate places named "projection delivery mode" as a #92 carve-out while 5.5 filed a different third item, so the count read "three" and matched while the contents did not:
  **(i) projection delivery mode** (on-demand export), carrying Issue 5.2's deletion of `emit_conformant_copy` as its provenance so the capability is remembered rather than merely removed. (ii) **conformance gate for yf-research and yf-incubator** (cross-reference #165 — yf-research's SPEC states a `Verification:` line nothing executes); (iii) **consumer round-trip fidelity**, still unverified in the sense #92 meant (we demonstrate producer→producer only); (iv) **the D-9 nested-`index.md` deferral**, carrying exp-003's 0/423 measurement and the `description:`-producer prerequisite. (iv) was added at pass 1: recording the deferral only in `OKF-YF-EXTENSIONS.md` (5.1) leaves it **invisible to the issue tracker** — the same asymmetry that made #140's original `include` disposition dishonest.
  - depends-on: 5.4
- Issue 5.6: Close **#92** as superseded **with the three carve-outs named**, and write the close comment **against the measured record** — correcting the two now-false rationale bullets ("no confirmed non-Google adopter"; "no change to `plan_manager.py`"). **Be precise about which claim is falsified:** #92's *bullet* says "no confirmed non-Google adopter" — measurably false. Trigger 2's *text* says "**production** adopter", and exp-004 flags "production" as **inferred from repo prominence, not attested**. Correct the bullet; do **not** claim the trigger fired. A superseded-by-assertion close would reproduce the exact defect class this plan's findings document.
  - depends-on: 5.5
  - resolves-upstream: #92 (supersede)
- Issue 5.7: Update the **#128** reference to point at v0.2 and confirm it is subsumed by #141 (it is already CLOSED; this is a link correction, not a reopen).
  - depends-on: 5.6

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Engine gate green
- Type: auto
- Condition: the FAST tier executes a **non-empty** command list containing `uv-okf` for `skills/yf-okf/scripts/okf.py` — a path that today matches no glob and returns zero commands.
- Test:
  ```bash
  set -o pipefail   # else a crash in change_validation.py is indistinguishable from "predicate false"
  uv run skills/yf-change-validation/scripts/change_validation.py \
      run --tier fast --changed skills/yf-okf/scripts/okf.py --json \
    | python3 -c 'import sys,json; d=json.load(sys.stdin); sys.exit(0 if any(c.get("id")=="uv-okf" for c in d["commands"]) else 1)'
  ```
- test_class: probe
- cwd: worktree
- Blocks: Epic 2, Epic 3
- Instructions: satisfied by completing Epic 1.
  **Revised twice. Pass 1** replaced the original pytest Test, which exp-001 had measured at `31 passed, EXIT=0` on the *current* tree — already green before Epic 1 ran.
  **Pass 2 found the replacement no better, and verified it by execution.** As written it used an undefined `${CV_SKILL_DIR}` and did not spawn at all (`error: Failed to spawn: /scripts/change_validation.py`); with the path corrected it returned `{"commands":[],"status":"pass"}` and **EXIT=0** on today's tree. `coordinator.md:182` resolves a gate on **exit 0**, and the "pass iff `commands` contains `uv-okf`" clause was prose in a field nothing parses — so a `probe`-class gate would have **auto-resolved itself unattended at execute start**, before Epic 1 ran.
  **The exit code must carry the predicate**, which is what the pipe above does. Issue 1.4 verifies this command exits **non-zero today** — a gate whose non-vacuity was established by reading is the exact defect this plan exists to fix.

### Capability Gate: Backfill review
- Type: human
- Condition: the operator has reviewed the aggregate `reindex --write` diff across the **19** bundles that carry a root `index.md` (D-11) and authorized applying it.
- Test: *(none — this is a consent gate; no green test can substitute for authorization)*
- test_class: consent
- cwd: worktree
- Blocks: Issue 4.3b
- Instructions: **Revised at pass 1** — this gate originally blocked Issue 4.3, which was the issue that *produced* the diff it conditions on. 4.3 is now split: **4.3a generates and renders the diff (ungated)**, 4.3b applies and commits (gated). Review the diff for prose loss. `check_markers()` hard-errors on an unbalanced marker and `discarded_prose()` warns on dropped lines, but neither is a substitute for looking — `plan-045/index.md` carries hand-written prose a regenerator could delete. Revert is `git checkout` on the affected paths.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Mitigation |
| :-- | :-- | :-- |
| **R1** | **v0.1's §1/§2/§6/§7 were never quoted in-repo**, so further undeclared v0.2 changes cannot be ruled out — and one *was* found inside the verified subset, which is evidence §13 is not exhaustive. | Issue 2.1 fetches v0.1 verbatim from a prior upstream commit **before** the baseline rewrite. This is the one risk that would otherwise silently propagate into a fixed-authority document. |
| **R2** | **`sync.py` vendoring is manual with no CI step**, so a hand-edited vendored copy diverges silently. Measured: `uv-_shared` fires on **none of the four** vendored copies today, and two of them (`yf-okf`, `yf-incubator`) match no §3 glob whatsoever. *(An earlier draft said "two" for both, conflating the two counts.)* | **Issue 1.3's id table** wires `uv-_shared` to all four. |
| **R3** | **The backfill rewrites 19 hand-written root indexes**; generated output could delete prose. | Marker preservation + `check_markers()` hard error + `discarded_prose()` warning + a **human consent gate** on the aggregate diff + `git checkout` revert. Four layers because the failure is silent and unrecoverable from the artifact alone. |
| **R4** | **Adopting v0.2 `status` would break the parked-plan classifier** and the execute-eligibility path (`plan_manager.py:2152` matches the literal `"approved"`). | D-7 — declared permanent divergence, recorded in the extensions layer. Not adopted even for new emissions. |
| **R5** | ~~A new check landing at `error` level enters `_OKF_PORT050_REQS` and blocks intake.~~ **RETRACTED at pass 1 — this cannot happen.** `_OKF_PORT050_REQS` is an allowlist of four reqs; a new req is outside it by construction (D-12). The real residual risk is the inverse: **relying on that silence.** An allowlist is an implicit guarantee no test asserts, and a future edit widening it would resurrect the risk invisibly. | D-10 keeps warning level anyway, and **Issue 3.8 converts the guarantee from read to executed.** |
| **R6** | **This plan edits `skills/yf-plan/README.md` and the shared engine while running under yf-plan.** | Skill-artifact isolation (AGENTS.md): the repo's `skills/` matches none of the resolver's six roots, so there is no self-modification hazard. **The one real constraint: no `yf skills install` / `yf self install` mid-execution** — `plan_manager.py` is re-invoked per call, so a mid-execution deploy would run new scripts against old prose. Deploy at land-the-plane. |
| **R7** | **`emit_conformant_copy` is spec'd, unreachable and untested** — a future investigator could reasonably conclude the projection exists. | Issue 5.2 forces a decision (expose or delete + amend SPEC). Deferring it again is the one outcome not permitted. |
| **R8** | **A batched pytest run of `test_incubator_index.py` + `test_index_manager.py` yields `5 failed, 25 passed`** from a sibling-module name collision on `okf`; each file alone is green. | Measured and benign, but recorded here because a CI author who batches them would see red and misdiagnose it as a product defect. |
| **R9** | **Epic 4 rewrites this plan's OWN `index.md` mid-execution** — plan-046 is in the corpus `reindex --write` sweeps, and its index carries both defect classes (the `plan-retrospective.md` ghost and, until fixed, the `upstream-triage.md` omission). | Benign but worth naming: the bundle is git-tracked and the change is reviewed under the same consent gate as the other 18. It is also a useful end-to-end signal — if the sweep does not fix this bundle, it did not work. |

## Success Criteria

1. **The gate demonstrably fires, and its EXIT CODE says so.** The Engine-gate command (Gates §) exits **0** after Epic 1 and exits **non-zero today** — verified both ways, not asserted. Measured pre-state: `{"status":"pass","commands":[]}`, EXIT=0, which is why the predicate had to move into the exit code. Separately, an injected mutant produces `status: fail` with `uv-okf` as `first_failure`.
2. **`_shared/test_okf.py` is green and gated**, with new coverage that catches the measured `render_index` mutation hole.
3. **`okf_version` reads `0.2`** in all five copies and `sync.py --check` exits 0. Mechanically: `grep -rniE "okf_version.*0\.1|OKF v0\.1" skills/ _shared/` — **the same widened pattern Issue 2.5 uses** — returns **zero** hits. *(Widened at pass 5: the narrow `okf_version`-only form would not have caught the 16 bare-prose sites 2.5 was extended to fix.)* *(Reworded at pass 3 — the prior form named three test sites as "the complete blast list"; six further non-test sites exist, three of them fixed authority.)*
4. **Every reference in Issue 2.3's v0.1→v0.2 section map reads its v0.2 number** in `spec/OKF-BASELINE.md`, checked row by row against that table — *not* "zero surviving `(§N)` references", which is uncheckable since v0.2 uses the same syntax. The file also carries a §13-verification subsection naming the undeclared `SHOULD NOT` → `MUST NOT` upgrade.
5. **Five mapping entries exist in `OKF-YF-EXTENSIONS.md`**, each explicitly labelled AGREE / DIVERGE / ABSENT, and `status` is recorded as a permanent divergence.
6. **`reindex --check` exits 0 across the 19 bundles that carry a root `index.md`**, and **exits `2` (`no-index`) for each of the 31 that do not** (D-11) — a number, not a prose assertion. `markdown_lint.py --rules ML003` reports **0 violations** over the single-level glob pinned in 4.1 — measured today: **25**, of which 24 are dead directory links and 1 a dead file. *(Rescoped at pass 1: the original criterion said "all 50 bundles", which was unachievable — 31 have no index to check.)*
7. **`upstream-triage.md` is listed in every root index that has one** (measured today: unlisted in 8 of 19), **and BOTH producers emit it on creation** — verified by **Issue 4.2a** (yf-plan, `plan_manager.py`) and **Issue 4.2b** (yf-research, `index_manager.py`) each scaffolding its own throwaway bundle with the **repo** copy, not by inspecting the corpus the fix just edited. Each scaffold asserts the defects **its own producer actually exhibits** — for yf-plan, no ghost entry for a presence-optional file and no entries for absent subdirectories; for yf-research, whatever 4.2b's up-front measurement finds. *(Scoped at pass 4: asserting both defect classes of both producers in advance would make the criterion undischargeable for reasons no issue anticipated.)* *(Widened at pass 3 — the prior form named only the yf-plan producer, so Epic 4 could have closed green with the research producer untouched.)*
8. **`plan_manager.py audit` still exits 0** against a bundle carrying a synthetic index-drift finding — **executed by Issue 3.8 from the repo tree**, not from the installed skill, whose vendored `okf.py` would test the old engine and pass regardless. This is the criterion that converts D-12's correction from a claim into a measurement.
9. **#92 is closed with three named carve-outs and two corrected rationale bullets**; **four** follow-on issues are filed by 5.5 (the three carve-outs plus the D-9 deferral), and each of the three canonical carve-out names — `projection delivery mode`, `conformance gate for yf-research and yf-incubator`, `consumer round-trip fidelity` — appears **verbatim** in both `plan.md` and `upstream-triage.md`, with no variant spelling of any of the three surviving anywhere in the bundle. *(The forbidden variants are deliberately NOT quoted here — an earlier draft named them literally inside the criterion, which made the criterion its own counter-example and unpassable by construction. They are described in `reviews/pass-4.md`'s M1 row — which records the measured pre-normalization counts rather than the literals, for the same reason.)* *(Restated at pass 4. The prior criterion demanded equal `grep -c` counts across five sites — which cannot hold, since four of the five sites live in `plan.md` — and it named a command nobody had run. Measured before normalization the counts were 2/1, 3/1, 1/0.)* #118 is closed with all four sites fixed; the File Layout defect is filed separately.
10. **`emit_conformant_copy` is either a tested CLI verb or absent from both the code and the SPEC.** No third outcome.
