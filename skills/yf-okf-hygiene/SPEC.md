# SPEC — OKF Hygiene (`yf-okf-hygiene`)

> Per-skill SPEC for full OKF **health** over an artifact corpus: read-only classification, the
> legacy backfill, index repair, and restore. Composed by the root macro `SPEC.md` under spec key
> **OKFH**. Requirements use RFC-2119 "shall"; *(testable)* items are the anchors a test names.
> Carries upstream #140-partial / #171-partial / #189-partial.

## 1. Purpose & scope

`yf-okf-hygiene` owns **corpus-level OKF health**: finding artifact bundles wherever they live,
classifying each one's conformance state, transforming the legacy ones into the OKF model, and
undoing that transform. It is the **operator-invoked** counterpart to `yf-okf`, which owns the
per-bundle engine (`check`, `migrate`, `reindex`, `scaffold`) that this skill calls.

The split is a **layer** boundary, not a feature boundary:

- **`yf-okf`** answers *"is THIS bundle conformant, and what does the engine do to one bundle?"*
- **`yf-okf-hygiene`** answers *"which bundles exist in this repository, what state is each in, and
  how do I move the whole population forward safely and reversibly?"*

Nothing here re-decides `yf-okf`'s conformance rules. Every verdict this skill reports about a
single bundle is the engine's verdict, surfaced at corpus scale.

**Motivating measurement (2026-08-28/29).** Half this corpus was never migrated — 30 of 59 plan
bundles still carry `README.md` and no `index.md`, purely as a function of age. And `okf migrate`,
the tool that would fix them, makes the audit **strictly worse on 30 of 30**: it stamps `plan.md`
frontmatter, which flips `okf_missing_level` from `warn` to `fail`, while leaving legacy prose in
the renamed index that `reindex --write` cannot repair. The correct transform is three steps and was
**unreachable from any command line**. That is the gap this skill closes.

## 2. Requirements (`REQ-OKFH-NNN`)

> **Identifier allocation.** `REQ-OKFH-001`..`REQ-OKFH-010` were allocated by plan-057 Issue 0.2 and
> measured collision-free repo-wide at allocation time (2026-08-29: zero occurrences outside the
> commissioning plan's own `plan.md`). The block is contiguous and this file is its only home.

### 2.1 Verb surface and exit contract

- **REQ-OKFH-001** *(testable)* the skill shall expose exactly the verbs **`audit`**, **`backfill`**,
  **`reindex`** and **`restore`** through a single engine script, and **every engine-backed verb its
  `SKILL.md` advertises shall be dispatchable by that script**.

  **The general property is the requirement, not the specific verb.** A `SKILL.md` that advertises a
  verb the engine cannot dispatch is an artifact asserting a capability nothing provides — and the
  failure relocates as easily as it is removed, so the check shall assert *every advertised
  engine-backed verb dispatches*, never *one named verb is gone*.

  **The `engine-backed` qualifier is load-bearing and measured.** A `SKILL.md` may legitimately
  advertise a verb that routes to prose rather than to the script (`init` is the shipped example:
  `yf-okf` advertises `init check migrate assess` while its engine dispatches
  `check migrate reindex scaffold`, and `init` is advertised-and-undispatchable **correctly**). A
  literal "every advertised verb dispatches" would be permanently red on a conforming skill.

  **`assess` shall not be advertised without being dispatchable.** Absorbing `yf-okf`'s
  advertised-but-unimplemented `assess` means absorbing the **capability**; the name shall either
  dispatch, alias a verb that does, or be retired. Re-advertising it here would move the defect one
  directory over rather than delete it.

- **REQ-OKFH-002** *(testable)* every verb shall honour the three-valued exit contract
  **`0` the criterion holds · `1` it does not · `2` the check could NOT RUN**, and shall inherit
  `REQ-CLI-029` in full: two-branch where it asserts a failure code, **fail loudly on an empty
  inspection**, and `126`/`127` reserved to the caller.

  **`--min-roots N` and `--require-legacy N` are this skill's two floors.** A corpus tool that
  inspected nothing exits `0` on every rule it applies, so "clean" and "not read" are the same
  observation without a declared floor.

  **A harness fault shall be `2`, never `1`.** Measured precedent to not reproduce: a sibling driver
  handed an **absolute** glob root raised an unhandled `NotImplementedError` from `pathlib` and
  exited `1` — which under its own documented contract means *drift*, so an instrument fault was
  reported as a corpus finding. Every root-accepting entry point here shall accept an **absolute**
  root without crashing, and shall report an un-runnable condition as `2`.

### 2.2 Discovery and classification

- **REQ-OKFH-003** *(testable)* **`audit` shall be READ-ONLY.** It shall discover bundle roots,
  classify each bundle, and report — and shall write **nothing**, to no path, on any code path,
  including the paths that discover a defect. Read-only is what makes the audit safe to run before
  consent is given, which is the only reason an operator can be shown evidence before authorizing a
  transform.

- **REQ-OKFH-004** *(testable)* `audit` shall classify each discovered bundle into exactly one of
  **`conformant` | `legacy-readme` | `legacy-underscore-index` | `hybrid-partial` | `unclassifiable`**,
  and shall emit the classification as structured JSON.

  `unclassifiable` is a real verdict and shall not collapse into any neighbour: a bundle the rules
  cannot place is a statement about the instrument's coverage, and folding it into `conformant`
  certifies what was never read while folding it into a legacy class manufactures work.

- **REQ-OKFH-005** *(testable)* **root detection shall be config-driven with a SELF-CONTAINED default
  exclusion set.** It shall hard-exclude `.git/**`, `.worktrees/**`, `.claude/worktrees/**`, `.yf/**`,
  archive directories and frozen fixture trees, and shall find incubator-analog roots
  (`<scope>/<slug>/plans/`) that a fixed four-root list misses.

  **A consumer-private member file is an OVERRIDE where present, never a PREREQUISITE.** The wider
  corpus is 514 bundles across 41 repositories and none of the foreign ones carries a yf-plan member
  declaration, so a default set that depended on one would make the skill unable to run anywhere but
  here — and being able to run elsewhere is the whole reason it is a skill rather than a script.

### 2.3 The backfill transform

- **REQ-OKFH-006** *(testable)* **`backfill` shall be the THREE-STEP transform — `migrate`, then
  DELETE the renamed legacy index, then REGENERATE the listing — and shall never be `migrate`
  alone.**

  **Measured, and this is the requirement's whole reason for existing:** `okf migrate` on its own
  introduces a new hard audit **`fail` on 30 of 30** legacy bundles. It stamps `plan.md` frontmatter,
  which flips `okf_missing_level` from `warn` to `fail`, and leaves legacy prose in the renamed index
  that `reindex --write` **cannot** repair. A half-done backfill is therefore **strictly worse than
  none**, which is also why the transform is specified as an indivisible unit rather than three
  independently invocable steps.

  Provenance, recorded so no reader mistakes it for a corpus result: the three-step transform was
  measured at **n=1** (plan-020). The `30/30` and `29/30` figures were measured over `migrate`
  **alone** — the transform this requirement rejects.

- **REQ-OKFH-007** *(testable)* `backfill` shall **HALT** on both declared risk classes —
  **`hybrid-partial`** and **objective divergence** — and shall require explicit operator resolution
  per bundle rather than choosing a side.

  Measured: 8 of 30 legacy bundles need explicit resolution. One bundle strands **10 phase-log
  bullets across 2 dates**, and 7 bundles' `README.md` objective differs from `plan.md`'s H1 — richer
  in the README in at least two cases, so "prefer `plan.md`" would silently discard authored content.
  A halt is the correct verdict precisely because the tool cannot know which text the author meant.

- **REQ-OKFH-008** *(testable)* `backfill` shall be **crash-recoverable BY MECHANISM**, keyed on a
  **durable per-bundle journal** — target path plus phase, written and **fsynced before the first
  rename** and unlinked only after cleanup — and **never on directory presence**.

  **It is NOT atomic, and the requirement says so because an operator reads this before consenting.**
  Measured: `os.rename` onto a **non-empty** directory raises `OSError errno 66`, so the swap is
  **two renames with a window in which the bundle is absent**. A recovery table keyed on directory
  presence is not total over the reachable states and reads *"staged, crashed before rename 1"* as
  *"done"*.

  **The reachable states are FIVE and are enumerated here, once, normatively** — because a five-state
  test and a five-state journal could otherwise be five *different* fives with every instrument
  green:

  | state | meaning |
  | :-- | :-- |
  | `S0` | nothing staged |
  | `S1` | staged, before rename 1 |
  | `S2` | after rename 1 — the bundle is **absent** |
  | `S3` | after rename 2 — the original is stashed |
  | `S4` | after rename 2, before the journal is unlinked |

  Recovery shall be **deterministic from all five**. Staging shall occur **inside the repository
  tree**, never in a system temporary directory — measured `EXDEV` risk across filesystems, which
  would turn a rename into a copy and void the reasoning above.

- **REQ-OKFH-009** *(testable)* `backfill` shall emit a **per-bundle audit record** and shall treat
  **three separate fail-closed preconditions** as the safety guarantee: **fingerprint invariance**,
  **phase-log bullet AND distinct-date equality**, and **per-bundle audit delta** — no bundle's audit
  verdict may be **worse** after the run than before it.

  **The content fingerprint is NOT the guarantee, and stating that is the point of this
  requirement.** The fingerprint covers `plan.md`'s content sections **only**: it excludes
  `README.md`, `index.md` and `log.md` entirely — that is, **every file the backfill mutates** — and
  it excludes the header preamble, which is exactly where migration adds frontmatter. A
  "byte-identical" result over it is therefore very nearly a **tautology**, and it is structurally
  blind to the one **measured** data-loss mode: the phase log lives above the first `## ` and is
  excluded from the hash. The phase-log equality check and the audit-delta check are what actually
  hold; the fingerprint check is retained as a cheap third signal, not as the argument.

### 2.4 Repair, reversal, and the `_index.md` route

- **REQ-OKFH-010** *(testable)* `reindex` shall **REFUSE** a legacy prose index rather than appending
  beneath it; `restore` shall be **record-driven with a PER-PATH operation kind**; and the
  `_index.md` legacy variant shall be routed by **detected member**, never by filename.

  **`reindex` refuses because appending is the silent-corruption path.** A legacy prose index is not
  a listing with entries missing — it is a different document. Appending a generated listing beneath
  it produces a file that satisfies the entry regex while carrying two contradictory listings.
  Converting a legacy index is `backfill`'s job, and the refusal is what keeps the two verbs from
  quietly overlapping.

  **`restore` needs a per-path kind because `git checkout` alone CANNOT undo the transform.** A
  modified or deleted **tracked** file is restored by `git checkout`; a **created** `index.md` or
  `log.md` is **absent from HEAD** and must be **unlinked**. A restore that only checks out leaves
  every created file behind and reports success. The git-backed half is sound because all 30 depth-1
  legacy `README.md` files were verified **individually** to be git-tracked — not assumed from the
  population.

  **The `_index.md` route dispatches on the detected member, not the filename**, so a bundle whose
  legacy index is named `_index.md` takes the same transform as one named `README.md` without a
  second code path. Scope is recorded honestly: it has exactly **one live in-repo target**, and the
  47% figure that motivates it is 227-of-243 in a **single foreign repository** this plan may not
  touch. The route is therefore built largely against self-authored fixtures, and that
  over-building risk is **accepted knowingly** rather than discovered later.

## 3. Interfaces

- **CLI / script:** `skills/yf-okf-hygiene/scripts/okf_hygiene.py`, PEP-723 inline deps, invoked via
  `uv run`, and **executable** (`chmod +x`) so a presence check with `test -x` is meaningful.
- **`audit` surface:** a **repeatable** `--root`, plus `--maxdepth N`, `--require-legacy N`,
  `--min-roots N` and `--json`. `--require-legacy` is the load-bearing flag: it asserts *no bundle
  remains legacy*, which a root count cannot express.
- **`backfill` surface:** dry-run by **default**; `--apply` performs the transform; `--record <path>`
  writes the per-bundle audit record REQ-OKFH-009 requires.
- **`restore` surface:** `--record <path>`, the same record `backfill --record` wrote.
- **Engine dependency:** the per-bundle verbs come from `yf-okf`'s engine. If a copy of that engine
  is vendored beside this script, it shall be registered with `_shared/sync.py`'s consumer list — an
  unregistered vendored copy is invisible to `--check` and drifts **silently and forever**, which is
  the failure mode that file's own comment describes. A `sys.path` hack to `_shared/` is not an
  option: skills deploy standalone.
- **Tests:** `skills/yf-okf-hygiene/scripts/test_okf_hygiene.py`, carrying a PEP-723 `dependencies`
  header, `import pytest`, **and** an `if __name__ == "__main__": sys.exit(pytest.main([__file__, "-q"]))`
  runner block. All three are load-bearing: without the runner, `uv run <file>` merely **imports** the
  module, executes no test, and exits **0**.

## 4. Guardrails (`GR-OKFH-NNN`)

- **GR-OKFH-001** `audit` writes nothing, ever. A verb that reports is not a verb that repairs.
- **GR-OKFH-002** `backfill --apply` is **consent-gated**. No green test substitutes for the
  authorization, because the risk it carries is data loss, not condition failure.
- **GR-OKFH-003** The default exclusion set is self-contained. The skill shall be *able* to run in a
  foreign repository; **executing** the backfill outside its own repository is out of scope.
- **GR-OKFH-004** Nothing is filed upstream to the OKF project. It is tracked read-only.
- **GR-OKFH-005** No bundle-root marker file is introduced (REQ-OKF-034).

## 5. Verification

| Requirement | Verified by |
| :-- | :-- |
| REQ-OKFH-001 | `scripts/checks/check-assess-verb-gone.sh` — every engine-backed advertised verb dispatches, across **both** OKF skills |
| REQ-OKFH-002 | `harness-selftest.sh` RED rows; absolute-root acceptance exercised per entry point |
| REQ-OKFH-003 | `test_okf_hygiene.py::audit_readonly_and_reindex_refusal` |
| REQ-OKFH-004 | `test_okf_hygiene.py` fixture-driven classification core (two-variant equivalence) |
| REQ-OKFH-005 | `test_okf_hygiene.py::root_detection_self_contained` |
| REQ-OKFH-006 | `test_okf_hygiene.py::fingerprint_invariance` + the corpus run |
| REQ-OKFH-007 | `test_okf_hygiene.py::plan030_hybrid_log_preserved` |
| REQ-OKFH-008 | `test_okf_hygiene.py::crash_recovery_all_states` — naming **each** of `S0`..`S4` |
| REQ-OKFH-009 | `scripts/checks/check-backfill-audit-delta.py --record <path>` |
| REQ-OKFH-010 | `test_okf_hygiene.py::restore_round_trip`, `::underscore_index_live_target`, `::audit_readonly_and_reindex_refusal` |

The suite runs in **both** `CHANGE-VALIDATION.md` tiers, so it is paid on every land rather than
once — six shipped scripts in this repository already have no tests at all (#189) and this skill
shall not become a seventh.

## 6. References

- `skills/yf-okf/SPEC.md` — the per-bundle engine contract this skill calls (`REQ-OKF-*`).
- `skills/yf-okf/spec/OKF-BASELINE.md`, `spec/OKF-YF-EXTENSIONS.md` — the composed ruleset.
- `skills/yf-plan/spec/cli.md` — `REQ-CLI-029`, the `scripts/checks/` harness contract.
- `docs/validation-layers.md` — the `doc_lint` ↔ `okf.check_conformance` layer boundary.
- Upstream: #140 (structure below the bundle root), #170 (round-trip fidelity), #171 (nested index
  generation), #189 (shipped scripts with no tests).
