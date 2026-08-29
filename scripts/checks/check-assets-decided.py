#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""SC8 — `assets/**` is DECIDED: covered by a document type, or declared out of contract scope.

NOT SILENTLY UNCOVERED, WHICH IS THE THIRD STATE AND THE ONE THAT BITES. 62 authored
descriptions live under `assets/` directories across this corpus, selected by NO schema. That
is not a neutral gap: `check_okf_index_drift.py`'s exclusions are `assets/fixtures/**` and
`findings/okf-migration-samples/**` only, so `assets/*` **IS** enumerated by the live
index-drift gate — and this exact class turned `main` RED on 2026-08-29 when a bundle carried
an `assets/` directory present-but-unindexed and the FULL tier failed.

So the decision has a direct mechanical consequence on a running gate, which is why this is an
executable criterion rather than a prose one. Either answer is acceptable; SILENCE IS NOT.

  (a) COVERED — a `_shared/document_types/asset*.toml` whose `paths` select `assets/**`; or
  (b) OUT OF SCOPE — an `assets/**`-shaped glob in the effective exclusion set, which is read
      from the ENGINE (`okf.resolve_extension`), not re-parsed from the manifest. A second
      parser is a second grammar, and the two would disagree exactly where it matters.

EXIT  0 the decision is recorded, one way or the other
      1 neither is present — `assets/**` is silently uncovered
      2 could not run (no engine, no document_types directory — an EMPTY INSPECTION)
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

CHECK = "check-assets-decided"


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def selects_assets(paths: list[str]) -> bool:
    """A path glob that reaches INTO an `assets/` directory."""
    return any("assets/" in p for p in paths)


def main() -> int:
    root = repo_root()

    types_dir = root / "_shared" / "document_types"
    if not types_dir.is_dir():
        inconclusive(f"no document_types directory at {types_dir}")

    schemas = sorted(types_dir.glob("*.toml"))
    if not schemas:
        # FAIL LOUDLY ON AN EMPTY INSPECTION (REQ-CLI-029(b)). Zero schemas means every
        # "no schema selects assets" conclusion below is unearned.
        inconclusive(f"inspected 0 schemas under {types_dir} — nothing was read")

    covering: list[str] = []
    for s in schemas:
        try:
            data = tomllib.loads(s.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            inconclusive(f"cannot parse {s.name}: {exc}")
        paths = data.get("paths") or []
        if isinstance(paths, list) and selects_assets([str(p) for p in paths]):
            covering.append(f"{s.name} (type={data.get('type', '?')})")

    # The effective exclusion set, read FROM THE ENGINE.
    sys.path.insert(0, str(root / "_shared"))
    try:
        import okf  # type: ignore
    except Exception as exc:  # pragma: no cover - environment condition
        inconclusive(f"cannot import the okf engine: {exc}")
    try:
        excludes = [str(g) for g in okf.resolve_extension("yf-plan").exclude_globs]
    except Exception as exc:
        inconclusive(f"the engine could not resolve yf-plan's exclusion set: {exc}")

    # An `assets/**`-shaped exclusion is one that excludes the assets directory AS A WHOLE.
    # `assets/fixtures/**` does NOT qualify and must not be read as qualifying — it excludes a
    # subdirectory, which is precisely the state that leaves `assets/*` enumerated.
    blanket = [g for g in excludes
               if g.rstrip("/*").rstrip("/") == "assets" and g != "assets"]

    print(f"{CHECK}: inspected {len(schemas)} schema(s); "
          f"effective exclusions {excludes}")

    if covering:
        print(f"{CHECK}: DECIDED (covered) — schema(s) select assets/: {', '.join(covering)}")
        return 0
    if blanket:
        print(f"{CHECK}: DECIDED (out of scope) — blanket exclusion(s): {', '.join(blanket)}")
        return 0

    print(f"{CHECK}: FAIL — assets/** is SILENTLY UNCOVERED: no document type selects it "
          f"({len(schemas)} schemas read) and the effective exclusion set carries no blanket "
          f"`assets/**` ({excludes}). `assets/fixtures/**` does not count — it excludes a "
          f"SUBDIRECTORY, which is exactly the state that leaves assets/* enumerated by the "
          f"live index-drift gate.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
