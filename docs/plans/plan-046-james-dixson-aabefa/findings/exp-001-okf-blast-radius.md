---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-okf-blast-radius
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exp-001 — The `_shared/okf.py` blast radius, and what actually guards it

**Question:** What is the true blast radius of changing `_shared/okf.py`, and what validation guards it today?
**Method:** read the engine; hashed all five copies; ran `sync.py --check`; ran `change_validation.py run --tier fast --changed <path>` for **every** relevant path against the real repo; built an `rsync`'d scratch copy to inject divergences and mutants and re-measure; prototyped the proposed §1/§3 rows there and measured that they fire and fail-close. Repo left clean; canonical sha unchanged.

## Headline — the gate is not thin, it is absent, and it reports green

D-6 is confirmed **and under-stated**. Two of the four vendored copies match **no CHANGE-VALIDATION §3 glob at all**, and on a tree with a real divergence present the on-edit gate returned:

```json
{"tier":"fast","status":"pass","commands":[],"first_failure":null}
```

A **vacuous PASS, zero commands executed**, on a genuinely broken tree — while `sync.py --check` on that same tree exited 1. That is strictly worse than "the right test does not run", because the verdict reads green.

## 1. The engine

**Measured.** Three subcommands — `check <dir>`, `migrate <dir> [--dry-run]`, `scaffold <dir> [--member] [--subdir ...]`; shared `--json` / `--skill` accepted **both before and after** the subcommand (`parents=[common]` on parser and subparsers).

**Exit-code contract — only `check` is non-trivial:**

```python
return 0 if findings.ok else 1     # _cmd_check
def _cmd_migrate(...) -> int: ...; return 0   # ALWAYS 0
def _cmd_scaffold(...) -> int: ...; return 0  # ALWAYS 0
```

`Findings.ok` = `not any(f.level == "error" ...)` — **warnings never fail**. Confirmed live: a bundle with a `warning` finding returned `EXIT=0`.

**`check --json` shape:**

```json
{"command":"check","dir":"nested/b1","ok":true,
 "rulesets_composed":["OKF-BASELINE","OKF-YF-EXTENSIONS","OKF-PLAN"],
 "findings":[{"path":"references/r1.md","req":"REQ-OKF-FAM-001","level":"warning",
  "message":"type 'reference' not in OKF-PLAN vocab ['Plan','Finding',...]"}]}
```

`migrate --json` emits a different shape (`ChangePlan.as_dict()`); `scaffold --json` emits `{"command","dir"}`.

**Frontmatter model.** `read_frontmatter` → `(dict, body)`; no block ⇒ `({}, full_text)`; malformed YAML or non-mapping ⇒ `OKFParseError`. `write_frontmatter` is **merge-and-preserve** (REQ-OKF-070). `read_fields` is dual-mode (frontmatter-first, `**Field:**` fallback). `okf_version = "0.1"` is **hard-pinned at line 48**.

### The nested blind spot — measured, and it is the plan's target

`render_index(bundle)`: if `index.md` exists it is returned **verbatim** — no regeneration, no drift detection. Otherwise it synthesizes from `b.iterdir()` (direct children only) and emits `- [name.md](name.md)` for files and **`- [child/](child/index.md)` for subdirs**.

Meanwhile `check_conformance` is asymmetric:

| line | behavior |
| :-- | :-- |
| 798 | `md_files = [p for p in sorted(target.rglob("*.md"))]` — **does** recurse for per-file `type`/`okf_spec` |
| 802 | `root_reserved = {p.name for p in target.iterdir() if p.is_file()}` — reserved-file requirement is **root-only** |
| — | `non_reserved` excludes by **basename at every depth**, so a *nested* `index.md` is neither required nor checked |

Two live probes:

```
# subdir references/ with NO index.md:
{"ok": true, ...}   EXIT=0
# then added references/index.md with `type: Plan` + `okf_spec: bogus`
# (both hard REQ-OKF-031 errors at the root):
{"ok": true, ...}   EXIT=0   ← zero new findings
```

> **The engine links to a nested `index.md` it never requires and never creates — a dangling link by construction.** Enforcing nested indexes is closing a hole the engine itself opens, not adding a new demand.

## 2. The vendoring fan-out

**Measured — byte-identity holds right now**, all five `459cd5452eb7835717cca71af38170d9a6bd2a4eb159d790739880592a801aae`; `uv run _shared/sync.py --check` → `EXIT=0`.

`sync.py` declares `okf.py` a **WholeFileAsset** (lines 172–178), canonical `_shared/okf.py`, four consumers. Invocation is **manual** — `uv run _shared/sync.py` to regenerate, `--check` to report. **No hook, no pre-commit, no CI step** runs the regenerating form: `.github/workflows/ci.yml` contains only `cargo fmt` / `clippy` / `cargo test --workspace` plus a `baked-embed` job — no `uv`, no `_shared`, no `okf`.

Editing a vendored copy directly is *detectable* (`DIVERGED: skills/yf-okf/scripts/okf.py`, `EXIT=1`) but the detector **is not wired to that edit** — §3.

## 3. The validation gap — CONFIRMED

**`grep -n "okf" CHANGE-VALIDATION.md` → NONE.** `test_okf.py` appears nowhere in the manifest, nowhere in `ci.yml`.

The only `_shared` rows in §3:

```
| `_shared/**`          | `uv`, `uv-_shared` |
| `_shared/test_sync.py`| `uv`               |
```

**Measured FAST-tier fan-out — every row executed:**

| changed path | ids that fire | runs `test_okf.py`? |
| :-- | :-- | :-- |
| `_shared/okf.py` | `uv`, `uv-_shared` | **no** |
| `_shared/test_okf.py` | `uv`, `uv-_shared` | **no** |
| `skills/yf-plan/scripts/okf.py` | 18 `uv-yf-*` ids | **no** |
| `skills/yf-research/scripts/okf.py` | `uv-research`, `uv-research-cred` | **no** |
| `skills/yf-incubator/scripts/okf.py` | **`[]` (zero commands)** | **no** |
| `skills/yf-okf/scripts/okf.py` | **`[]` (zero commands)** | **no** |
| `skills/yf-okf/SKILL.md` | `frontmatter` | — |
| `skills/yf-okf/SPEC.md` | `uv-herdr-launch` | — |
| `skills/yf-okf/spec/OKF-BASELINE.md` | `cargo` | — |

*(The `SPEC.md → uv-herdr-launch` row is upstream #164, independently confirmed here.)*

**The working command** — `--with pyyaml` is required:

```
A) uv run --with pytest python3 -m pytest _shared/test_okf.py -q
   → ModuleNotFoundError: No module named 'yaml'            (FAIL)
B) uv run _shared/test_okf.py                → 31 passed    EXIT=0
C) uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q
   → 31 passed                                              EXIT=0
```

### Mutation probes — `render_index` is the least-tested function the plan will rewrite

| mutant | result |
| :-- | :-- |
| `read_fields` precedence (`if key not in model` → `if True`) | `1 failed, 30 passed` — **caught** |
| `render_index` reserved-filter (`if child.name in RESERVED_FILES` → `if False`) | **`31 passed`** while `render_index` demonstrably regressed to emitting `- [log.md](log.md)` — **NOT caught** |

> Wiring `test_okf.py` in **without adding `render_index` coverage** buys a gate that cannot see the regression class this plan is most likely to introduce.

## 4. The rows that close it — prototyped and measured

One §1 `fast` id **and its mirror in `full`** (FULL has no `okf` row today, so the mirror is required, not optional):

```
| `uv-okf` | `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q` |  |  |
```

Six §3 rows — **a bare `_shared/**` tweak is not sufficient**, it never reaches the vendored copies:

```
| `_shared/okf.py`                    | `uv-okf`, `uv-_shared` |
| `_shared/test_okf.py`               | `uv-okf`               |
| `skills/yf-okf/scripts/**`          | `uv-okf`, `uv-_shared` |
| `skills/yf-incubator/scripts/**`    | `uv-okf`, `uv-_shared` |
| `skills/yf-plan/scripts/okf.py`     | `uv-okf`, `uv-_shared` |
| `skills/yf-research/scripts/okf.py` | `uv-okf`, `uv-_shared` |
```

Measured with those rows in place — and **fail-closed proof** with the `read_fields` mutant:

```json
{"status":"fail","first_failure":{"id":"uv-okf",
 "returncode":1,"output_tail":"...F... test_read_fields_frontmatter_wins_over_field ..."}}
```

### A correction the plan must not repeat verbatim

plan-042's precedent is "name a test target, not a name filter — a filter matching nothing passes vacuously." **That rationale is cargo-specific.** Measured for pytest:

```
pytest _shared/test_nope.py -q            → EXIT=4  (missing file: hard error)
pytest _shared/test_okf.py -q -k nomatch  → EXIT=5  (no tests collected)
```

An explicit file target is still correct — but state the **real** reason (exit 4 on a moved/renamed target), not a vacuous-filter claim that does not hold for pytest.

## 5. DRIFT-CHECK edges

| edited | edges |
| :-- | :-- |
| `_shared/okf.py` | `e-okf-copy-{plan,research,incubator,okf}` — all `value-equal` byte-identity |
| `skills/yf-okf/scripts/okf.py` | `e-skill-script-cli`, `e-json-contract`, `e-okf-copy-okf` |
| `skills/yf-okf/SKILL.md` | the full 19-edge `skills/*/SKILL.md` fan-out |
| `OKF-BASELINE.md` | **not a named node** — covered only by the generic `spec` glob, single edge `e-spec-compliance` (→ SKILL.md) |

**The gap for strand (a).** `OKF-BASELINE.md:29` states *"when OKF ratifies or bumps its version, only `OKF-BASELINE.md` and the baked-in ruleset re-sync"* — declaring a coupling to `okf_version = "0.1"` at `okf.py:48`. **No DRIFT-CHECK edge encodes that coupling.** A v0.1→v0.2 baseline edit fires `e-spec-compliance` and `cargo`, neither of which looks at the engine. `grep -n "BASELINE" DRIFT-CHECK.md` returns nothing.

## 6. REQ ids

| family | defined | next free |
| :-- | :-- | :-- |
| `REQ-OKF-NNN` | 001–003, 010, 020–021, 030–031, 050, 060, 070–071 | block-local **004**, **011**, **022**, **032**, **051**, **061**, **072** |
| `REQ-OKF-CHK-` | 001 | **002** |
| `REQ-OKF-FAM-` | 001–004 | **005** |
| `REQ-OKF-MIG-` | 001–005 | **006** |

The numeric family is **blocked by section**, so a new bundle-model REQ takes **004**, not 072.

**Bonus defect — `REQ-OKF-034` is referenced but never defined:**

```
skills/yf-okf/SPEC.md:53:  `index.md` and `log.md` are reserved and exempt (REQ-OKF-034).
```

Almost certainly a typo for `031`. Under DRIFT-CHECK §7 "the authority names an identifier that does not exist" is a **CONFLICT-and-halt**, so resolve it before allocating near it.

`REQ-OKF-*` is used only by yf-okf. `REQ-PORT-006` is referenced twice in yf-okf's SPEC but **owned by yf-plan**.

## Implications

1. **D-6 upheld and widened** — six §3 rows, not a `_shared/**` tweak; both §1 tiers.
2. **`render_index` coverage belongs in the same first issue**, before the engine is touched.
3. **Strand (a) has no drift edge** — a baseline bump can silently leave `okf_version = "0.1"` baked in. Promote `OKF-BASELINE.md` to a **named** node and add an edge to the engine.
4. **The backfill cannot be gated on `migrate`** (always exits 0) — gate on a following `check`, and decide explicitly whether the nested-index rule emits `error` or `warning`, since `Findings.ok` ignores warnings.

## Honest limits

- **`run --tier full` was not executed** (multi-minute `cargo clippy --workspace --all-targets`). "FULL does not run `test_okf.py`" is measured on the manifest file, not on an executed FULL run.
- The `--changed skills/yf-plan/scripts/okf.py` probe executed 18 real suites; the id set and aggregate `pass` were recorded, not each suite's output.
- **Two mutants, not a systematic mutation run.** The `render_index` hole is measured for that one mutant; other `render_index` behaviors may be covered.
- Scratch experiments ran in an `rsync -a` copy excluding `.git`, `target`, `web`; `sync.py --check` behaved identically there, but any web-facing edge was untested.
- Trigger-scope results come from the **installed** `change_validation.py`, which per AGENTS.md may lag `skills/`. That is also what fires on a real edit, but installed-vs-source was not diffed.
