# Exp 002 — #15 duplicated-helper inventory + yf-owned-asset architecture

## Part A — the sweep is a TWO-helper job (not the broad framing in #15)

| Rank | Helper | Copies / state | Verdict |
| :-- | :-- | :-- | :-- |
| 1 | `manifest_update.py` | **5 byte-identical** copies (hash `49791c6cee57`, 128 lines): yf-beads-upstream, yf-optimal-instructions, yf-plan, yf-research, yf-skill-authoring | **Consolidate** — highest value, zero drift, zero risk. Whole-file dup (not a fenced region). |
| 2 | Defensive `--json` parser | **3 divergent impls**: `research_manager.py` `_extract_first_json` (strongest), `plan_manager.py` `_parse_bd_json` (strong, different shape), `plan_manager.py` `json-get` cmd (plain `json.load`, **weakest — latent bug**) | **Consolidate** on `_extract_first_json`; carries a latent correctness fix for yf-plan's weaker `json-get`. |
| 3 | `shutil.which` tool-check | 4 superficial one-liners, divergent-on-purpose | **Leave** — false positive. The real check already migrated to the `yf` kernel (`cmd/common.rs:87`→`tool.rs`, plan-010). #15's named symbols `_SYSTEM_DEPS`/`missing_tools` are **STALE** (gone from Python). |
| 4 | PEP-723 headers + argparse/click | near-identical headers; 14-vs-6 argparse/click split | **Leave** — PEP-723 must be per-file inline; no shared body. Structurally non-shareable. |

**Implication:** scope the #15 sweep to helpers (1) and (2). Most apparent duplication is
false-positive or already in the kernel. The plan should explicitly note the stale `_SYSTEM_DEPS`/
`missing_tools` premise so it doesn't chase non-existent Python duplication.

## Part B — architecture (the real decision)

`yf` **already deploys embedded files to disk** (`deploy_skill`, `cmd/common.rs:100`: `embed::read_file`
+ `fs::write`), so option (b)'s core mechanic exists. But two guardrails constrain runtime resolution:

- **GR-003 — `yf` is not a skill runtime.** A `yf shared <helper>` that scripts shell out to *at run
  time* trips this. An install-time *deploy* of `_shared/` does not.
- **Independent installability (GR-006).** A skill installed without `yf` must still run. Any runtime
  dependency on the `yf` binary on PATH breaks this with no offline fallback except "vendor a copy
  anyway" — which defeats the purpose.

| Criterion | (a) Extend vendoring | (b) yf-owned **runtime** asset | (c) yf embeds `_shared/` + **install-time** deploy |
| :-- | :-- | :-- | :-- |
| Serves yf-owned-asset preference | No (copies in skills/) | Yes | Partial (canonical yf-owned; derived copies still land) |
| Independent installability | Yes | **No** | Yes (deployed copy self-contained) |
| Offline | Yes | Only if `yf` present | Yes |
| Rust-change cost | **Zero** | High (+ trips GR-003) | Low-medium (embed + extend deploy) |
| Drift control | Low (proven; `sync.py --check` + DRIFT-CHECK) | High | Medium |
| GR-003/GR-005 | Clean | **Trips GR-003** | Clean (install-time) |

## Recommendation

**Adopt option (a) extended vendoring for this sweep — zero `yf` change.** Option (b) runtime
resolution is structurally blocked (breaks independent installability, trips GR-003). The operator's
yf-owned preference is honored at the **authority layer**: canonical lives in repo-root `_shared/`
(already outside the `skills/` embed root), and per-skill copies are **generated artifacts** no human
maintains — the substance of "minimize content in skills."

**Sweep mechanics (no Rust):**
1. Add `_shared/manifest_update.py` canonical + register the 5 consumers in `sync.py`'s `CONSUMERS`.
   Whole-file dup → either extend `sync.py` with a **whole-file copy mode** (simpler, file is 100%
   shared) or wrap the body in BEGIN/END markers like the classifier.
2. Pick `_extract_first_json` as canonical defensive JSON parser; fence in `_shared/`; vendor into
   `plan_manager.py` (replacing weaker `json-get` + reconciling `_parse_bd_json`) and `research_manager.py`.
3. Add DRIFT-CHECK.md `value-equal` edges per canonical→copy pair (mirror `e-active-set-copy-*`) and
   add consumers to the trigger-scope node table.

**The operator's "yf owns `_shared/`" wish** is achievable only via **option (c)** (install-time
deploy — `yf` becomes the vendoring engine instead of `sync.py`), medium Rust cost, guardrail-safe.
**Not needed for the sweep** — recommend deferring as a follow-on (alongside the PEP-723 route #40).
This is the open decision to put to the operator: ship the sweep on (a) now, or bundle (c) so content
genuinely moves under `yf` ownership.
