**A malformed finding, one level deeper than a single-star glob reaches.**

This file carries no `#` or `##` heading, so it violates `finding/has-heading` — the one
error-severity check the `finding` type retains after plan-048 Issue 2.9 moved the
content-shape checks to report-only.

That matters for what this fixture is FOR: it exists to prove the `paths` glob is
RECURSIVE (`findings/**/*.md`), and it can only prove that by producing a non-zero exit
from a file a single-level glob would never select. When 2.9 made the section checks
report-only, this fixture stopped failing and the recursion proof went silent — so it now
violates the check that still has teeth.

It is also missing all four mandated sections and any `**measured:**` / `**inferred:**`
marker, both of which are now reported rather than failed.
