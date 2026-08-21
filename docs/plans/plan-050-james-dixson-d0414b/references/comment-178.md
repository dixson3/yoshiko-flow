---
type: Reference
okf_spec: OKF-PLAN
id: comment-178
description: Drafted upstream comment for #178 (include, close) — including the two defects the contrast arm caught in the generator itself
---

# Draft comment → #178 (`include`; closes with this comment)

> **Fixed in `plan-050-james-dixson-d0414b`.**
>
> ## What shipped
>
> `REQ-CLI-025` — `plan_manager.py grant <plan-dir> [--check <file>]`. It generates the
> upstream-write authorization **proposal** from the plan's own Upstream Issues table. It
> never writes the authorization file, never performs an upstream write, and needs no
> network, so it runs before any `gh` call and before any authorization exists.
>
> The load-bearing part is not the generator; it is the **single source**. A new
> `UPSTREAM_REQUIREMENTS` table carries one entry per `UPSTREAM_DISPOSITIONS` literal
> (`end_state`, `state_reason`, `requires_mention`, `report_only`, and the rationale), and
> **both** `grant` and `_verify_row` read it. Before this they were two separate *prose*
> derivations of the same rule, which is how plan-048 halted its own reconcile: the grant was
> hand-derived, `#172`'s close was missed, and the omission surfaced only at
> `verify-reconcile` — after the outward-facing writes had begun. That plan's authorization
> file still carries the amendment repairing it, and names the cause: *"an oversight in THIS
> FILE, not a decision to withhold."*
>
> `--check` is the round-trip, and coverage is judged **per action, not per issue**: plan-048's
> omission was a *close* on an issue the grant already *mentioned*, which a per-issue check
> would have passed.
>
> ## `_verify_row` could not be the source, and that was measured
>
> The original design here was for the generator to call `_verify_row` directly. That was
> refuted: it returns `{detail, disposition, issue, verdict}` with **no `required_action`**, is
> **network-bound** (a `gh issue view` per row), and returns `fail: "unrecognised literal"` for
> an `exclude` row handed to it — a literal that *is* in the frozenset. Extracting the
> requirement is what makes one source servable to both readers.
>
> ## The generator was WRONG TWICE, and its own control caught both
>
> This is the more useful finding, so it is reported rather than quietly fixed. The fixture
> `ctl-178-grant` replays plan-048's **actual recorded grant** sliced at its amendment
> boundary, and — mandatorily — also replays the **amended** one, which must be *accepted*.
> That contrast arm exists because without it the fixture is satisfied by a checker that
> rejects everything, and a grant generator that never approves is not a generator.
>
> On its first run the contrast arm **failed**, twice over:
>
> 1. The table **declared** `supersede`'s actions as `[comment, close-not-planned]` while
>    `supersede`'s own `requires_mention` is `False`. The generator was demanding an
>    authorization clause for something the verifier would never check. A grant that asks for
>    **more** than the verifier requires is as wrong as one that asks for less — it just fails
>    in the direction that looks conservative.
> 2. `file-tracker` coverage was scoped to the issue number. But a grant written **before** the
>    tracker exists cannot name its number, because the number is *the thing being created*.
>    plan-048's real grant authorizes it as item 1, by plan id.
>
> **The repair makes the first divergence UNREPRESENTABLE, not merely corrected.** Grant
> actions are now **derived** from the requirement fields — a comment is asked for *iff*
> `requires_mention`, a close *iff* `end_state == CLOSED` — so the two halves cannot disagree
> at all. Only the tracker filing stays declared, because "create the issue" is not expressible
> as an end state. That durable form is what `SC8`'s assertion was for.
>
> ## The read is asserted BEHAVIORALLY
>
> `skills/yf-plan/scripts/test_upstream_requirements.py` (13 tests, registered as
> `uv-yf-upstream-req` in both CHANGE-VALIDATION tiers) mutates **one entry** in a throwaway
> copy of the table, re-runs `grant` **and** `_verify_row`, and asserts **both** verdicts
> change. The structural forms — the table exists, `_verify_row` imports it — were measured as
> **undetecting**: a table that is present and ignored passes them. `_gh_issue_view` is stubbed
> throughout, and that stub is load-bearing rather than convenient (`_verify_row` calls it
> unconditionally as its first act and returns `inconclusive` before consulting any table), so
> a separate test pins the stub itself.
>
> Measured: `ctl-178-grant` 1 → 0. The pre-amendment grant is rejected **naming `#172`'s
> comment and close**; the amended one is accepted; all six dispositions have exactly one
> entry. Recorded in
> `docs/plans/plan-050-james-dixson-d0414b/assets/red-prework.md`, with the two generator
> defects as `RE-009` in that bundle's `plan-retrospective.md`.
