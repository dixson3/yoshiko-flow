# Review pass 1 — plan-016

**Verdict:** REVISE

Conformance pass: PASS (mechanical checklist, no gaps). Adversarial pass: REVISE — one
high-severity scoping ambiguity and several framing corrections; all tightenings, no redesign.

## Strengths

- Evidence over framing: all three issues re-sized against source (#36 absent, #15 stale symbols,
  5 byte-identical `manifest_update.py` copies).
- The `yf` Rust seam (`repair()` / `apply_native` / the `:320` "never adds a remote" boundary) is
  real and correctly located; `remove_remote: bool` plumbing fits the existing pattern.
- Destructive-git safety guards (`--cached`, content-guard, `--remove-remote` opt-in) are sound and
  correctly scoped — the load-bearing risk is handled.
- Merged-tree validation reach already wired (CHANGE-VALIDATION.md FULL tier covers `_shared/**`,
  `*.rs`, the touched skill scripts) — bundling Python + Rust in one plan is low-risk.
- Upstream dispositions clean; #40/#41 spun out as explicit deferrals.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | A.2 conflates two incompatible parser contracts: `_extract_first_json` (first balanced value) is **not** a superset of `_parse_bd_json` (flat list, unwraps `{"issues":[…]}`, flattens concatenated docs). Folding both into one canonical would break `_bd_list`. | Narrow A.2 to replacing the **`json-get` command's `json.load`** only; leave `_parse_bd_json` in place (or treat as a separate distinctly-contracted helper). Strike the "reconciling with `_parse_bd_json`" framing. |
| C2 | medium | A.2 is **not** purely behavior-preserving for `json-get`: the canonical version does list-index `data[int(key)]` (succeeds where plan's KeyErrors) and uses a different error string. | State A.2 **intentionally changes** `json-get` list-index + error-string behavior (that is the fix); confirm no caller parses the old error text. Don't claim pure preservation. |
| C3 | medium | "Preflight is read-only by construction" is overstated — preflight already writes the additive gitignore scaffold (`ensure_scaffold`). | Restate the invariant as "no *canonicalizing/destructive* mutation; the additive gitignore scaffold is the only sanctioned write." B.2 emits the offer via the existing `instructions` channel (preflight already surfaces `Run: yf doctor --repair`), not a new write path. |
| C4 | low | A.1 whole-file `sync.py` mode is new untested machinery; the plan doesn't record why over the lower-risk marker-wrap. | Add a one-line justification, or fall back to marker-wrapping `manifest_update.py` (reuses the proven region path). |
| C5 | low | B.2 scope is narrower in the plan than #39 (which wants all beads entry points to converge). | State that all listed entry points converge through the single shared `yf preflight` path (or enumerate exceptions), so D.1 can honestly close #39. |

## Missing

- **M1 (low):** B.1's "+ any pre-tracked dolt runtime artifacts" untrack set is not enumerated. Pin
  the exact glob/list (`embeddeddolt/`, `backup/`, `export-state.json`, `push-state.json`,
  `dolt-server.*` per #39) so the `git rm --cached` set is deterministic and testable.

## Gate Assessment

Gates minimal and correctly placed. Capability gate (`sync.py --check`) is the right A.1/A.2
backstop (A.3 must extend `CONSUMERS` before it is meaningful for the new pairs — sequenced
correctly). **Gap:** no gate asserts Epic B's Rust/parity green before D.1. Recommend adding a
`cargo test --workspace` (+ parity) auto-gate blocking D.1, mirroring the sync-check gate.

## Upstream Assessment

Dispositions evidence-backed. #36 close-as-already-fixed correct; #15 honest about stale premise;
#39 is the only at-risk close — its acceptance demands all-entry-point convergence + a specific
untrack set, so D.1 should close #39 only after B.2 entry-point coverage (C5) and B.1 artifact list
(M1) are pinned. Confirm D.1 files/updates the **one coarse** plan-scale tracking issue per
AGENTS.md, not granular sub-beads.

## Operator Resolutions

All seven folded into plan v2 (drafter-authority corrections; no operator input required — these are
fidelity tightenings, not scope/approach changes).

| Concern | Resolution | Status |
| :-- | :-- | :-- |
| C1 (A.2 parser contract) | A.2 narrowed to replace **only** `json-get`'s bare `json.load`; `_parse_bd_json` explicitly left in place (different flat-list/envelope/concat contract that `_bd_list` needs); not a merge target this sweep. | resolved |
| C2 (json-get behavior change) | A.2 now states the consolidation **intentionally** changes `json-get` list-index + error-string behavior (the fix), not pure preservation; verify no caller parses the old error string. | resolved |
| C3 (preflight read-only framing) | Restated the invariant (plan + findings line): preflight does **no canonicalizing/destructive mutation**; the additive gitignore scaffold is the only sanctioned write; B.2 offers via the existing `instructions` channel. | resolved |
| C4 (whole-file sync.py mode) | A.1 records the rationale (a 100%-shared file shouldn't carry in-band markers) and names marker-wrap as the acceptable fallback. | resolved |
| C5 (B.2 entry-point scope) | B.2 states all #39 entry points converge through the single shared `yf preflight` kernel path (one wiring covers all); enumerate any exceptions. | resolved |
| M1 (untrack artifact list) | B.1 step (1) pins the exact untrack set as a constant (`interactions.jsonl` + `embeddeddolt/`, `backup/`, `export-state.json`, `push-state.json`, `dolt-server.*`), tracked-only. | resolved |
| Gate gap (Rust/parity gate) | Added a `cargo test --workspace` (+ `parity::*`) capability gate blocking D.1, mirroring the sync-check gate, with the golden-regen instruction. | resolved |

**Final status:** all concerns resolved in plan v2. Frozen.
