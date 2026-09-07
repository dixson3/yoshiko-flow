---
type: Asset
okf_spec: OKF-PLAN
description: "Body for the follow-on filed as #375 — lifecycle.d2's deps-missing label shorthand."
---
<!-- THE POSTED BODY IS EVERYTHING BELOW THIS COMMENT. The frontmatter above is
     bundle metadata (OKF REQ-OKF-003) and was NOT part of the upstream write:
     filed as #375. -->

`web/content/images/lifecycle.d2` labels the preflight outcomes
`ok / ignored / deps-missing / rule-drift`. The actual status literal is **`system_deps_missing`**,
not `deps-missing`.

**This is a deliberate label shorthand, not a claim about spelling** — the full literal would wrap
in that box — and it was confirmed by reading the rendered PNG during plan-066 (Issue 5.4).

### Why file it rather than fix it

It will **not survive a literal-equality checker** over preflight status values. No such checker
exists today, and widening the label pre-emptively for a checker that does not exist would trade a
legible diagram for a hypothetical. But the interaction is real and should be recorded before
someone builds that checker and reads the finding as a live defect.

### Options when it comes up

- widen the box and use the full literal; or
- keep the shorthand and add the diagram to that checker's declared `not_checked` set — which
  `REQ-CHECK-009` now requires be stated rather than implied.

Filed from plan-066 under D5.
