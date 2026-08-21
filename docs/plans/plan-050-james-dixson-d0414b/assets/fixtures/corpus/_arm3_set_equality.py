"""ctl-178 arm 3: UPSTREAM_REQUIREMENTS and UPSTREAM_DISPOSITIONS are THE SAME SET.

SC10's structural half. A disposition literal with no table entry falls straight through to
`_verify_row`'s unrecognised-literal branch and is omitted from every grant — a generator
silently omitting a disposition is #181's defect class in a new place.

Run as a FILE rather than a heredoc: `plan_manager.py` imports click and pyyaml, so this
needs `uv run --with click --with pyyaml`, and stdin is not available for the script body
when the module path is also an argument.
"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("pm", sys.argv[1])
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

missing = pm.UPSTREAM_DISPOSITIONS - set(pm.UPSTREAM_REQUIREMENTS)
extra = set(pm.UPSTREAM_REQUIREMENTS) - pm.UPSTREAM_DISPOSITIONS
if missing or extra:
    print(f"missing={sorted(missing)} extra={sorted(extra)}", file=sys.stderr)
    sys.exit(1)

# Guard the guard: an empty frozenset would make the equality trivially true.
if len(pm.UPSTREAM_DISPOSITIONS) < 6:
    print(f"VACUOUS: only {len(pm.UPSTREAM_DISPOSITIONS)} disposition(s)", file=sys.stderr)
    sys.exit(2)
print(f"arm 3: {len(pm.UPSTREAM_REQUIREMENTS)} dispositions, each with exactly one entry")
