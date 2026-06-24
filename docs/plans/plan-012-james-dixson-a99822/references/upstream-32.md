# Upstream #32: Add `yf doctor` subcommand to validate presence of `beads` and `uv`

- **Number:** 32
- **Title:** Add `yf doctor` subcommand to validate presence of `beads` and `uv`
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Context

The `dixson3/tap/yf` Homebrew formula previously declared hard `depends_on "beads"` and `depends_on "uv"`. These were removed so the formula no longer forces a brew-managed install of either tool — `uv` in particular is intentionally vendor-installed (curl installer + `uv self update`), and a transitive brew `uv` was shadowing the vendor copy on PATH and breaking `uv self update`.

Dropping the hard `depends_on` fixes the shadowing, but it also means nothing guarantees `beads` and `uv` are present and usable at runtime. `yf` depends on both at runtime.

## Request

Add a `yf doctor` subcommand that performs read-only validation of `yf`'s runtime prerequisites. At minimum it should:

- Verify `beads` (`bd`) is on PATH and invokable; report version.
- Verify `uv` is on PATH and invokable; report version.
- Report the resolved binary path for each (so a shadowed/duplicate install is visible).
- Exit non-zero if any required dependency is missing or non-functional, with a clear remediation hint (how to install each).

## Notes

- Keep it read-only / non-mutating — `doctor` verifies, it does not install or repair.
- Consider warning (not just reporting) when a dependency resolves to a Homebrew path for tools expected to be vendor-installed (e.g. `uv`), since that's the exact failure mode that motivated this issue.
