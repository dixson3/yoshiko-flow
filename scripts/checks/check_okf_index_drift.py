#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""SC10 / REQ-OKF-CHK-004 — the CORPUS index-drift driver.

`reindex` judges ONE bundle. This drives it over the whole corpus, which is what makes
REQ-OKF-011 reachable from a gate at all. Measured at scoping: `okf.py reindex` appeared in
**zero** `CHANGE-VALIDATION.md` rows, **zero** CI steps, and was called by nothing in
`plan_manager.py`. Root-index drift had been repaired nine days earlier and had **already
regressed in 9 of the 30 index-bearing bundles** — every bundle authored after the repair.
Nothing noticed. A verb no gate invokes is not enforcement.

FOUR PROPERTIES, each written because its absence is a way to report a false clean:

1. **Depth-1 root enumeration, NEVER `rglob`.** The roots are `docs/plans/*`,
   `docs/research/*`, `Incubator/*/plans/*`, `Incubator/*/research/*`. `rglob` would descend
   into a bundle's own `findings/okf-migration-samples/**` and treat each nested FIXTURE
   bundle as a corpus root — inflating `bundles_checked` while inspecting fixtures, which is
   REQ-OKF-CHK-003's defect reappearing inside the enumerator.

2. **A nonexistent enumerated root is a HARD ERROR, never a skip.** This is the CONSUMER HALF
   of REQ-OKF-011's new `no-such-path`, and without it that new exit code buys nothing: a
   corpus sweep must tolerate `no-index` (most bundles have none), so a driver that folds
   `no-such-path` into `no-index` reads a mistyped root as a benign skip.

3. **`bundles_checked` + `--min-roots N`.** A driver that enumerated nothing exits 0 on every
   rule it applies. The floor is what makes "the corpus is clean" distinguishable from "the
   corpus was not read" (REQ-CLI-029(b)).

4. **Gitignore-aware**, so an untracked scratch directory is never enumerated.

The exclusion source is REQ-OKF-CHK-003's member-declared §3b — not a second list.

EXIT  0 clean  ·  1 drift  ·  2 INCONCLUSIVE (could not run)
      126/127 reserved to the shell (REQ-CLI-029(c)).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CHECK = "check-okf-index-drift"

DEFAULT_ROOTS = (
    "docs/plans/*",
    "docs/research/*",
    "Incubator/*/plans/*",
    "Incubator/*/research/*",
)


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def corpus_root() -> Path:
    """Where the BUNDLES are. Resolved from the caller's cwd."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                      text=True, stderr=subprocess.DEVNULL).strip()
        return Path(out)
    except Exception:
        return Path.cwd()


def engine_root() -> Path:
    """Where `_shared/okf.py` lives. Resolved from THIS SCRIPT's own location.

    SEPARATE FROM `corpus_root()`, and the separation is load-bearing. Collapsing the two
    made the driver import its engine from whatever tree the caller happened to stand in —
    so pointing it at a corpus outside this repo returned INCONCLUSIVE for the entirely
    unrelated reason that the target had no `_shared/`. "Where the instrument lives" and
    "what the instrument is measuring" are different questions, and a driver that cannot ask
    them separately can only ever measure its own repository.
    """
    return Path(__file__).resolve().parent.parent.parent


def git_ignored(root: Path, paths: list[Path]) -> set[Path]:
    """The subset git ignores. An untracked scratch bundle is not corpus."""
    if not paths:
        return set()
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "--stdin"],
            input="\n".join(str(p) for p in paths), capture_output=True, text=True)
        return {Path(ln.strip()) for ln in proc.stdout.splitlines() if ln.strip()}
    except Exception:
        return set()          # gitignore-awareness is a refinement, never a blocker


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", action="append", default=None, metavar="GLOB",
                    help="Bundle-root glob (repeatable). Default: the four corpus roots.")
    ap.add_argument("--min-roots", type=int, default=1,
                    help="Fail-loud floor on bundles_checked (REQ-CLI-029(b)).")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="Accepted for interface symmetry; output is JSON on every path.")
    a = ap.parse_args()

    root = corpus_root()
    sys.path.insert(0, str(engine_root() / "_shared"))
    try:
        import okf  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        inconclusive(f"cannot import the OKF engine: {e}")

    try:
        excludes = list(okf.resolve_extension("yf-plan").exclude_globs)
    except Exception:
        excludes = []

    root_globs = a.root or list(DEFAULT_ROOTS)

    # PROPERTY 2 — a root glob that MATCHES NOTHING is a hard error, not a skip.
    #
    # The predicate is over the glob's PARENT: `docs/plans/*` matching nothing could mean
    # "no plans yet" (legitimate) OR "docs/plans is a typo" (a caller bug), and the two are
    # distinguishable exactly by whether the parent directory exists. Demoting the second
    # into the first is how a mistyped path gets read as clean.
    bundles: list[Path] = []
    bad_roots: list[str] = []
    for g in root_globs:
        parent = (root / g).parent
        # A glob with wildcards in its PARENT (`Incubator/*/plans/*`) is checked by whether
        # the fixed prefix exists, so an absent optional tree (no `Incubator/`) is not an error.
        fixed = Path(g)
        while any(ch in fixed.name for ch in "*?["):
            fixed = fixed.parent
        if str(fixed) not in (".", "") and "*" not in str(fixed) and not (root / fixed).exists():
            # `Incubator/` is genuinely optional in most repos; the four defaults are only
            # an error when the caller NAMED them explicitly.
            if a.root is not None or not str(g).startswith("Incubator/"):
                bad_roots.append(g)
                continue
        # AN ABSOLUTE ROOT IS ORDINARY, NOT EXCEPTIONAL (REQ-CLI-029(d), plan-057 Issue 1.4).
        # Measured 2026-08-29: `--root "$PWD/docs/plans/*"` raised an unhandled
        # `NotImplementedError("Non-relative patterns are unsupported")` from `pathlib` and
        # exited **1** — which under THIS SCRIPT'S OWN documented contract means *drift*. A
        # harness fault reported as a corpus finding is worse than a traceback: the code is
        # wrong but in-contract, so no reader can tell. An absolute glob is now anchored at
        # its own filesystem root and matched relative to it; an unusable pattern is `2`.
        try:
            gp = Path(g)
            if gp.is_absolute():
                anchor = Path(gp.anchor)
                matched = [p for p in sorted(anchor.glob(str(gp.relative_to(anchor))))
                           if p.is_dir()]
            else:
                matched = [p for p in sorted(root.glob(g)) if p.is_dir()]
        except (NotImplementedError, ValueError, OSError) as exc:
            print(json.dumps({
                "check": CHECK, "verdict": "inconclusive", "exit": 2,
                "bundles_checked": 0, "bad_roots": [str(g)],
                "reason": (f"root pattern {g!r} could not be expanded: {exc} — this is a "
                           "statement about the INSTRUMENT, not about the corpus"),
            }, indent=1))
            return 2
        bundles.extend(matched)

    if bad_roots:
        print(json.dumps({
            "check": CHECK, "verdict": "error", "exit": 1,
            "bad_roots": bad_roots, "bundles_checked": 0,
            "reason": (f"{len(bad_roots)} enumerated root(s) do not exist: "
                       f"{', '.join(bad_roots)} — a mistyped root must never be demoted "
                       "into a clean sweep (REQ-OKF-CHK-004)"),
        }, indent=1))
        return 1

    ignored = git_ignored(root, bundles)
    bundles = [b for b in bundles if b not in ignored and b.resolve() not in
               {i.resolve() for i in ignored if i.exists()}]
    # A bundle EXCLUDED by the member's §3b is not corpus either.
    bundles = [b for b in bundles if not okf.is_excluded(b.name, excludes)]

    rows, drifting, inconclusive_rows = [], [], []
    for b in bundles:
        try:
            res = okf.reindex_check(b)
        except Exception as e:  # noqa: BLE001 - engine is crash-safe; defensive only
            res = {"verdict": "inconclusive", "reason": str(e)}
        v = res.get("verdict")
        row = {"bundle": str(b.relative_to(root)), "verdict": v,
               "counts": res.get("counts", {})}
        if v == "drift":
            row["findings"] = res.get("findings", [])
            drifting.append(row)
        elif v == "inconclusive":
            row["reason"] = res.get("reason")
            inconclusive_rows.append(row)
        elif v == "no-such-path":
            # Cannot happen from a glob match, and if it does the enumerator is broken.
            inconclusive_rows.append({**row, "reason": "enumerated path vanished mid-run"})
        rows.append(row)

    checked = len(rows)

    # PROPERTY 3 — the floor.
    if checked < a.min_roots:
        print(json.dumps({
            "check": CHECK, "verdict": "inconclusive", "exit": 2,
            "bundles_checked": checked, "min_roots": a.min_roots,
            "reason": (f"enumerated {checked} bundle(s), below the --min-roots floor of "
                       f"{a.min_roots} — a driver that read nothing cannot report clean"),
        }, indent=1))
        return 2

    out = {
        "check": CHECK,
        "bundles_checked": checked,
        "roots": root_globs,
        "exclude_globs": excludes,
        "with_index": sum(1 for r in rows if r["verdict"] in ("clean", "drift")),
        "no_index": sum(1 for r in rows if r["verdict"] == "no-index"),
        "drifting": len(drifting),
        "inconclusive": len(inconclusive_rows),
    }

    if drifting:
        out.update({"verdict": "drift", "exit": 1, "rows": drifting,
                    "reason": f"{len(drifting)} bundle(s) have root-index drift",
                    "remediation": ("Author real descriptions for the missing members. "
                                    "`reindex --write` will satisfy the gate with BARE "
                                    "bullets, which degrades the artifact while passing the "
                                    "check — it is not the operator remediation.")})
        print(json.dumps(out, indent=1))
        return 1

    if inconclusive_rows:
        out.update({"verdict": "inconclusive", "exit": 2, "rows": inconclusive_rows,
                    "reason": f"{len(inconclusive_rows)} bundle(s) could not be judged"})
        print(json.dumps(out, indent=1))
        return 2

    out.update({"verdict": "clean", "exit": 0,
                "reason": f"{checked} bundle(s) enumerated; no root-index drift"})
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
