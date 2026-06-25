"""Canonical defensive `--json` extractor — single source of truth (plan-016 `_shared/`).

This module is the **canonical** copy of the defensive *single-value* JSON extractor
shared by `yf-plan` (`plan_manager.py`) and `yf-research` (`research_manager.py`). Each
consuming script carries a **marker-fenced region** holding a verbatim copy of the
REGION delimited below; `_shared/sync.py` regenerates those regions in-place from this
file (skills cannot `import` each other — each must stay independently installable, so
the shared snippet is *vendored*, never imported).

Do **not** hand-edit the vendored copies. Edit the region here and run
`uv run _shared/sync.py`; `uv run _shared/sync.py --check` reports divergence. The copies
stay honest via the DRIFT-CHECK.md edges `e-json-extract-copy-plan` /
`e-json-extract-copy-research` (this file is the fixed authority; a divergent region is
the copy drifting — FAIL on the copy, never the canonical).

Scope note: this extracts the **first balanced JSON value** only. It is *not* a superset
of `plan_manager.py`'s `_parse_bd_json` (which flattens multiple concatenated docs and
unwraps the `{"issues":[…]}` envelope into a flat list) — that helper has a different
contract and is deliberately left unmerged.

The region assumes `json` is already imported by the consuming module (both consumers,
and this module below, import it).
"""

from __future__ import annotations

import json


# >>> BEGIN defensive json extractor (canonical) >>>
def _extract_first_json(text: str):
    """Defensively extract the first balanced JSON value from text.

    bd's --json output may carry a warning prefix and/or be a concatenated array
    (notably `bd show`/`bd list`). Strip to the first balanced {...} or [...] block
    and parse that. Raises ValueError if none parses.
    """
    open_to_close = {"{": "}", "[": "]"}
    for i, ch in enumerate(text):
        if ch in open_to_close:
            depth = 0
            in_str = False
            esc = False
            for j in range(i, len(text)):
                c = text[j]
                if in_str:
                    if esc:
                        esc = False
                    elif c == "\\":
                        esc = True
                    elif c == '"':
                        in_str = False
                    continue
                if c == '"':
                    in_str = True
                elif c in open_to_close:
                    depth += 1
                elif c in open_to_close.values():
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[i:j + 1])
                        except json.JSONDecodeError:
                            break
            # this opener didn't yield a parse; try the next one
    raise ValueError("no balanced JSON value found in input")
# <<< END defensive json extractor (canonical) <<<
