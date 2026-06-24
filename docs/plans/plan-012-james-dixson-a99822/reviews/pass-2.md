# Plan-012 Review — Pass 2 (Epics E & F scope addition)
**Date:** 2026-06-23
**Scope:** Epics E (fold BEADS.md → BEADS_INIT.md) and F (upstream default-none + preflight offer), plus their integration. Epics A–D were reviewed in `pass-1.md` and are not re-litigated here.

## Pass 1 — Conformance
**Verdict:** PASS

Epics E and F are structurally well-formed and integrate cleanly with the pass-1 skeleton: acceptance per task, linear acyclic depends-on edges (E.1→E.4, F.1→F.4), `resolves-upstream: (none)` lines consistent with the Upstream Issues table and the AGENTS.md coarse rule, DEC-2/DEC-3 referenced from Objective/Scoping/Approach/Risks/Success, gates (Reconcile extended to A–F; Verification Gate correctly Rust-only A/B), risks, and success criteria all updated. No dangling references; phase log records the addition. No structural gaps.

## Pass 2 — Red-team
**Verdict:** REVISE → **all concerns resolved** (see Operator Resolutions)

| ID | Severity | Location | Concern | Suggested resolution |
|:--|:--|:--|:--|:--|
| R1 | high | F.1; SKILL.md §0 push (137), Status/pull (236), init §1/§2 (87/92), Backends (72) | The short-circuits branch on the **literal string `false`**; an unconfigured repo (key absent → empty) is `!= "false"` and so **fails open** (proceeds to auth/enumerate). "Resolve unset to none" is insufficient — the *comparison logic* must change. | Invert to **default-deny**: treat anything `!= "true"` as disabled, at every named site; add a test fixture for the no-keys repo. |
| R2 | medium | F.1 marker note; UPSTREAM_TRACKING.md, SKILL.md §0 | Default-deny (R1) and "write `none` at beads-init" are redundant; a marker-only path fails open on repos initialized before the change. | Make default-deny load-bearing; demote the explicit marker to "optional disambiguation only, never required for correctness." |
| R3 | medium | F.2, DEC-3; BEADS_INIT.md preflight (11–13), silent-no-op (38–42) | The offer sits on the shared beads-preflight surface (runs for every beads skill). One-shot depends on the gate read matching the §0 key/precedence and on writing the decline-marker before re-firing; a read-only preflight can't persist and would re-prompt. | Fire only in an interactive context that can persist the decision; gate read identical to §0; add a "second preflight after decline → zero prompts" test. |
| R4 | medium | F.3/F.4, F preamble; SKILL.md trigger-split (52–63), UPSTREAM_TRACKING.md | F adds a second *procedural* trigger to the deliberately-minimal companion rule; offer prose risks drifting from SKILL.md init. | Keep the rule to trigger+gate+pointer (mirror the close-time trigger); procedure stays in SKILL.md; add a concrete DRIFT-CHECK edge SKILL.md ↔ UPSTREAM_TRACKING.md. |
| R5 | medium | E.1/E.2, DEC-2; BEADS_INIT.md (charter, 45 lines), UPSTREAM_TRACKING.md close-time trigger | The land-the-plane pointer is **already owned** by UPSTREAM_TRACKING.md — restating it recreates the duplicate always-loaded surface E exists to remove; and use-bd / shell-flag mandates are off BEADS_INIT.md's stated charter. | E.1 dedup must check **all** always-loaded surfaces (route the close-time pointer to UPSTREAM_TRACKING.md, don't restate); E.2 adds a one-line charter scope-note so the fold is on-charter. |
| R6 | low | F.3; SKILL.md line 79 | SKILL.md line 79 says the companion rule is "installed by `install.sh`" — there is no repo-level install.sh; `yf skills install` is the installer. | F.3 already edits this file — fix the one-word reference in the same pass. |
| R7 | low | M2b; AGENTS.md (12–16) | M2b should state the coarse issue is additive (E/F only) and must not duplicate/re-open #29–#32. | Add the additive-only clause. |
| R8 | low | F.1; Backends (72), init §1 (87) | F.1 enumerated only Push §0 + Status/pull; init §1/§2 default proposal and the Backends `none` row also encode the state. | Add init §1/§2 and the Backends-row confirmation to F.1's site list. |

## Operator Resolutions
| ID | Status | Resolved by |
|:--|:--|:--|
| R1 | resolved | F.1 rewritten to **default-deny** (`!= "true"` ⇒ disabled) at all four sites + new no-keys test fixture |
| R2 | resolved | F.1 demotes the `none` marker to "optional disambiguation only, never required for correctness; no marker-only path" |
| R3 | resolved | F.2 gates on same key/precedence as §0, fires only in a persist-capable interactive context, + "second preflight → zero prompts" test |
| R4 | resolved | F.3 keeps UPSTREAM_TRACKING.md to trigger+gate+pointer (procedure in SKILL.md); F.4 names the concrete SKILL.md ↔ UPSTREAM_TRACKING.md DRIFT-CHECK edge |
| R5 | resolved | E.1 dedup check spans all always-loaded surfaces (route close-time pointer to UPSTREAM_TRACKING.md, never restate); E.2 adds a charter scope-note |
| R6 | resolved | F.3 fixes the stale `install.sh` → `yf skills install` reference at SKILL.md line 79 |
| R7 | resolved | M2b additive-only clause added (E/F-only; #29–#32 cross-linked, never folded/re-opened) |
| R8 | resolved | F.1 site list extended to init §1/§2 + Backends `none` row confirmation |

## Summary
The E/F scope addition is structurally sound and well-motivated. The one high-severity catch (R1) was a real fail-open bug in the proposed default: the existing short-circuits compare against the literal `false`, so F.1 is now scoped as a **default-deny comparison change** with a regression test, and the marker path is explicitly non-load-bearing (R2). F.2/F.3/F.4 pin the offer-gate read, keep the companion rule minimal, and name the DRIFT-CHECK edge (R3/R4); E.1/E.2 dedup against the already-always-loaded close-time trigger and reconcile the BEADS_INIT.md charter (R5); R6–R8 are one-pass fixes folded into the owning tasks. All eight concerns resolved in `plan.md`; ready for operator approval → INTAKE.
