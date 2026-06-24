# Exp 001 — yf-drift-check machinery shape (drives the sharing decision)

**Question:** What is yf-drift-check's machinery concretely, and is there reusable *code*
(for the new `yf-change-validation` skill) or only reusable *conventions*? Standalone-mirror
vs extract-to-`_shared/`?

## Verdict: **STANDALONE-MIRROR**

There is **no reusable code** in yf-drift-check — its entire engine is **prose executed by an
LLM** plus one report-only sub-agent. `_shared/` (plan-014) is a domain-specific *text-region
vendoring* tool, not engine machinery. Extracting "shared bootstrap machinery" would mean
*writing that code from scratch* with only two consumers — speculative generality. Mirror the
**conventions**; couple nothing.

## Evidence

- **No scripts.** `find skills/yf-drift-check -name '*.py' -o -name '*.sh'` → nothing. Layout is
  `SKILL.md`, `SPEC.md`, `README.md`, `agents/drift-verifier.md`,
  `protocols/DRIFT-CHECK-TRIGGER.md`, `spec/{schema,engine,checks}.md`, `templates/manifest.md`.
  plan-014 plan.md already recorded "drift-check is prose, not Python."
- **Manifest schema** (`spec/schema.md`, REQ-SCHEMA-001): the per-repo `DRIFT-CHECK.md` is markdown
  with **7 ordered `##` sections** + a §0 Status line (Nodes / Edges / Per-Edge Contracts /
  Referencers / Required-Section Contracts / Trigger Scope / Fixed-Authority Policy). Contract
  vocabulary is a **fixed 6-term set** (`path-resolves, identifier-matches, value-equal,
  field-set-subset, field-set-equal, section-present`).
- **Bootstrap = hybrid infer→approve→enforce, all prose** (REQ-ENGINE-003). "Infer a draft from
  what exists on disk … **never** a hardcoded conventional filename (the E4 lesson)." Draft is inert
  (`approved: no`) until the operator sets §0 `approved: yes`.
- **Trigger rule** (`protocols/DRIFT-CHECK-TRIGGER.md`): fires on edit of a path matching an
  **approved** manifest's §6 Trigger-Scope glob; **silent no-op** unless an approved manifest
  exists (no nag, no bootstrap-on-every-edit).
- **Dispatch**: main session spawns a `general-purpose` agent reading `agents/drift-verifier.md`
  (read-only), returning a fixed parseable block (`### PASS/FAIL/INCONCLUSIVE/CONFLICT`). The agent
  never writes; the main session acts.
- **`_shared/sync.py`** is `extract_region`/`replace_region` between markers with a hardcoded
  `CANONICAL` + `CONSUMERS` list — zero manifest/approval/dispatch/glob/schema machinery.

## Implications for the plan

- Build `yf-change-validation` **standalone**, mirroring drift-check's structure: a per-repo
  **`CHANGE-VALIDATION.md`** manifest (mirroring `DRIFT-CHECK.md`), a REQ-* `spec/` layout, an
  always-loaded trigger/`§0 approved`-gated protocol rule with silent no-op, and the
  infer→approve→enforce bootstrap discipline (+ the "infer from disk, never hardcode" E4 lesson).
- **Divergences that justify NOT sharing code:** the verifier is *read-only*; a validation runner
  **executes** build/test/lint. Inference source differs (file-graph vs toolchain). Verdict policy
  differs (drift's CONFLICT/fixed-authority vs plain PASS/FAIL). Unlike drift-check, change-validation
  **does** need a Python engine (it must run commands, parse exit codes, fingerprint the toolchain).
- The one shareable primitive (`tool_on_path`, ~10 lines `command -v`) is **below the extraction
  threshold** — inline it. Revisit `_shared/` extraction only if a *third* consumer shows real,
  identical, code-level duplication.
