#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""beads-init — RETIRED shim.

The verify/repair engine that used to live here has moved into the `yf` kernel
(plan-010). The shared "is bd usable in this repo?" check and the standard repair
sequence are now:

    yf preflight yf-beads-init --json   # READ-ONLY health check (was: beads_init.py verify)
    yf doctor --repair                  # apply the standard repairs (was: beads_init.py repair --apply)
    yf doctor --repair --local-only     # also assert no Dolt remote

The load-bearing correction the engine encoded (parse `bd status --json` for an
`error` key rather than trusting the exit code, so an initialized-but-wedged repo
is classed `corrupted`, not `not_initialized`) is preserved in the kernel — see
docs/yf/preflight-contract.md §5 (REQ-YF-PRE-006/007).

This shim remains only so stale callers fail loudly with the new invocation.
"""

import sys

_MOVED = {
    "verify": "yf preflight yf-beads-init --json",
    "repair": "yf doctor --repair  (add --local-only to assert no Dolt remote)",
    "status": "yf doctor",
}


def main() -> int:
    sub = sys.argv[1] if len(sys.argv) > 1 else None
    target = _MOVED.get(sub)
    sys.stderr.write(
        "beads_init.py is retired: verify/repair moved to the `yf` kernel (plan-010).\n"
    )
    if target:
        sys.stderr.write(f"  Use: {target}\n")
    else:
        sys.stderr.write("  Use: yf preflight yf-beads-init --json  |  yf doctor --repair\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
