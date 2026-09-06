---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-diagram-pipeline
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# EXP-004 — Is the `.d2` → `.png` repair loop achievable, and how is it verified?

**Question.** #317 requires repairs "at all sites together, re-rendering affected PNGs". Is
regeneration reproducible, is it verifiable, and can anything check a `.d2` against code?

## Result A — the render command exists but is UNDOCUMENTED for these files

No render target for `web/content/images/` exists anywhere: not in `web/Makefile`
(`grep -i 'd2\|png\|image'` → none), not in `web-deploy.yml` or `ci.yml`, not in
`CHANGE-VALIDATION.md`, not in `web/README.md`.

The only engine is `skills/yf-diagram-authoring/scripts/render.py:91-101` —
**`d2 --theme 0 --layout elk <slug>.d2 <slug>.png`** (`DEFAULT_LAYOUT = "elk"`, `:53`).
`render.py render-dir web/content/images` would work, but nothing in the repo says so;
`DRIFT-CHECK.md:284-287` names only `skills/*/spec/*.d2` and `docs/diagrams/*.d2`.

## Result B — all six PNGs DIFFER byte-wise, and NONE is content-stale

```
architecture:   fresh 86ea2fff (257508 B)  commit fcf7e94e (417426 B)   DIFFERS
formulas:       fresh d7f33162 (675008 B)  commit f0537509 (1514243 B)  DIFFERS
install-matrix: fresh fb1adb86 (172366 B)  commit f8fa37bc (329532 B)   DIFFERS
lifecycle:      fresh 8ce43d48 (100977 B)  commit c3008a16 (100970 B)   DIFFERS
phase-model:    fresh b33bdbaa (558916 B)  commit 55017788 (1052238 B)  DIFFERS
tune-matrix:    fresh 94904ddd (252242 B)  commit 01af826b (451719 B)   DIFFERS
```

**The cause is d2 version drift, not stale sources.** Evidence:

- d2 v0.8.2 is **byte-deterministic** — a second render into a fresh dir reproduced identical
  sha256 for both files tested. So this is not renderer nondeterminism.
- PNG headers show a **different d2 build** produced the commits: 5 of 6 committed files are
  colortype 6 (RGBA) with an `sRGB` chunk and 8192-byte IDATs; every fresh render is colortype 2
  (RGB), no `sRGB`, 4096-byte IDATs.
- Visual comparison of `install-matrix` shows **identical node sets and labels, reordered inside
  the container**. `lifecycle`'s entire diff is 5223 px of sub-pixel antialiasing on one label.
- `render.py check-dir web/content/images --json` → `{"status":"ok","orphans":[],"stale_advisory":[]}`.

**So every committed render faithfully depicts its source.** The one thing a byte comparison
would have been for — catching a diagram that disagrees with its own `.d2` — reports nothing here.

**A byte-equality acceptance criterion is therefore not viable ACROSS d2 versions.** Any bead
saying "re-render with a *different* d2 and confirm the PNG matches" fails on all six for a reason
unrelated to correctness.

> **AMENDED after red-team pass-2 C4 — this conclusion was stated too broadly.** Byte equality IS
> decidable **within** a pinned version. Re-measured independently: two renders of one source under
> d2 v0.8.2 produce **identical sha256** (`lifecycle` → `8ce43d48…` twice, `architecture` →
> `86ea2fff…` twice). So the honest criterion is sha256 equality against a fresh render under the
> recorded pin — **stronger** than the encoding-signature check that briefly replaced it, which was
> measured non-discriminating: all six fresh renders share one signature, and committed
> `lifecycle.png` already matches it while differing in sha256. SC10 now asserts sha256 equality.

## Result C — a `.d2` ↔ code checker IS buildable (~110 lines), with a limit

Against the committed sources:

```
AS-COMMITTED: FAIL (11 findings)
  architecture.d2:   total claims 18, truth 20
  architecture.d2:   group 'beads' claims 8, truth 5
  architecture.d2:   group 'utility' claims 6, truth 8
  architecture.d2:   group 'workflows' (3 skills) is NOT DEPICTED AT ALL
  formulas.d2:       claims 3 shipped formulas, truth 5
  formulas.d2:       not depicted: ['plan-review', 'verify-artifact']
  install-matrix.d2: opencode user '.config/opencode/skills', truth '.agents/skills'
  install-matrix.d2: opencode project '.opencode/skills', truth '.agents/skills'
  install-matrix.d2: pi user '.pi/agent/skills', truth '.agents/skills'
  install-matrix.d2: pi project '.pi/skills', truth '.agents/skills'
  install-matrix.d2: pi annotated 'lowercase-hyphen,max64' but name_transform: None
```

Negative control passes **both** directions: `fixed_rc=0 (want 0)`, `mutated_rc=1 (want 1)`.

**The honest limit — a text extractor cannot catch semantic mis-assignment.** In the *corrected*
render, the `beads group (5)` box still lists `plan · research · incubator` — which are the
**workflows** skills. The count is right and the membership is wrong. That residue is
irreducibly a human read, and it is exactly why `DRIFT-CHECK.md:191` classes `e-skill-page-desc`
as a prose edge.

## Result D — re-verification of all six

| File | #317 said | Verdict now | Defects |
| :-- | :-- | :-- | :-- |
| `architecture.d2` | wrong | **STILL WRONG** | total 18 vs 20; beads (8) vs 5; utility (6) vs 8; **workflows group entirely absent**; beads box lists workflows skills |
| `install-matrix.d2` | wrong | **STILL WRONG** | 4 wrong path cells + the retired `lowercase-hyphen,max64` |
| `formulas.d2` | wrong | **STILL WRONG** | "three shipped"; `plan-review`, `verify-artifact` undepicted |
| `tune-matrix.d2` | clean | **CLEAN** | all 8 cells verified vs `profiles/*.json` + `managed_block.rs:345-370` |
| `phase-model.d2` | clean | **CLEAN** | 10 status literals ⊆ `yf-plan/SKILL.md:231` |
| `lifecycle.d2` | clean | **CLEAN (caveat)** | `:10` shorthands preflight statuses (`deps-missing` vs real `system_deps_missing`). Cosmetic, but will not survive a literal-equality checker |

**Newly wrong, and NOT in #317 — two `.md` pages on REQUIRED edges are drifted right now:**
`architecture.md:59,65` (19 skills / utility (7)) under `e-web-skill-counts`, and
`architecture.md:47-48` + `install.md:191-192,204-206` under `e-web-cli-surface`.

**Coverage is not detection.** These sit on *required* edges and are still wrong.

## Implications for the plan

1. **The repair is achievable** — corrected sources compile in under 2 s each.
2. **Do not write a byte-equality criterion.** The honest post-condition is three-part: the
   source-text checker exits 0; `render.py check-dir` is clean; and a human reads each
   regenerated PNG for the semantic residue.
3. **A decision the plan must make:** re-rendering 3 of 6 leaves those three on v0.8.2 layout
   while the other three carry the older engine's — a visible split. Either re-render **all six**
   under one pinned d2 in one commit, or accept the inconsistency deliberately.
4. **The defect surface is 5 files, not 3** — the three `.d2` files *plus* `architecture.md` and
   `install.md`, all wrong about the same two facts. That is what "all sites together" means here.
5. **The gap is a missing DRIFT-CHECK node**, not a missing skill: add `web-diagram-src`
   (`web/content/images/*.d2`) with edges to the frontmatter contract, `harness_desc.rs`, and the
   formula set, plus a `CHANGE-VALIDATION.md` recipe row. Without it this recurs on the next
   `harness_desc.rs` change — which is precisely how it arose after plan-055.
6. **Add `architecture.md`'s harness table to `e-web-cli-surface`'s node set.** It carries the
   same matrix as `install.md` but is guarded only for counts, which is why its harness rows
   drifted undetected.
