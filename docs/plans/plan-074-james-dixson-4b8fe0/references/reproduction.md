---
type: Reference
okf_spec: OKF-PLAN
description: Portable baseline reproduction uses immutable H0 inputs and pinned checker bytes, with no sibling checkout or live tracker required.
---
# Portable reproduction and evidence limits

All paths below are relative to the repository root unless stated otherwise. The entire `assets/fixtures` subtree is archival input. Do not run captured scripts in place: native probe command receipts deliberately preserve historical scratch paths. Re-run native experiments only in newly owned disposable HOME/git/store roots with an allowlisted environment and no operator stores or credentials.

## Reproduce the baseline mismatch offline

Resolve the installed skill directory explicitly for the copy being tested. Verify its comparator SHA-256 against `assets/fixtures/provenance.json` first; a newer checker is not the old baseline. With `SKILL_DIR` set to that verified installed copy:

```sh
BUNDLE=docs/plans/plan-074-james-dixson-4b8fe0
uv run "$SKILL_DIR/scripts/pour_fidelity.py" \
  "$BUNDLE/assets/fixtures/pim-h0/beads.json" \
  "$BUNDLE/assets/fixtures/pim-h0/plan-012-james-dixson-d1af33" \
  --strict --plan plan-012-james-dixson-d1af33 --json
```

Observed baseline exit is **1**, with eight issue IDs, seven issue edges and four epics matching but gates 3 versus 4. Do not use shell `|| true` as a pass assertion. Missing paths/tools or wrong bytes are setup/instrument failures, not reproduction success. No live bd query is needed.

The subtree preserves the full original PIM plan bytes under its own basename so the comparator's `--plan` identity remains exact. This nested plan is an immutable fixture, not another active plan. Its original approved fingerprint is retained, not rewritten. `execution-epic-mapping.json` is original executor evidence and is not relabelled as a native pour response.

## Native positive and boundary evidence

`assets/fixtures/native-pours/current/` contains genuine bd 1.3.1 responses; `historical/` contains genuine checksum-verified bd 1.1.0 responses. Read `pour.stdout`, `list.stdout`, `show-wrapper.stdout`, `show-gate.stdout`, `commands.json`, `boundary-commands.json` and their exact stdout/stderr. Version/source/checksum references and line-numbered source excerpts are alongside them. The two pours used the same copied installed formula. No fixture was retyped to manufacture historical compatibility.

The wrong-target gate-resolution experiment is intentionally dangerous only inside its owned scratch: it demonstrates why gate-resolving the wrapper is forbidden in the repair. Do not replay it on PIM or YF's actual tracker. The preflight records explicitly show the isolated yf rule lookup was missing while native bd status was parsed healthy; these are not represented as full green yf preflights.

Verify `native-pours/SHA256SUMS` from that directory. The outer `assets/fixtures/SHA256SUMS` covers the immutable fixture collection; neither checksum list includes itself. Captured absolute paths are provenance, not portability dependencies.

## Three artifact boundaries

Source is pinned to commit 8c97581e85fd48ebdfac45866b03fd213b9a783a. Installed manager/comparator/extractor hashes match that source, while the executable reports a different dirty build stamp. `installed-status.json` independently records the matching embedded/installed skill tree hash. Do not generalize the three-file equality into a full build reconstruction or imply the dirty-stamped binary was rebuilt in this planning session.

Future Tier-1/Tier-2 suites must exercise modified source and a modified sandbox-installed tree. The frozen baseline reproduction remains red under the old pinned checker; later acceptance is a separate receipt from the new checker plus explicit role evidence. No source green substitutes for live installed validation after an authorized deployment.
