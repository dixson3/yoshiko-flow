# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
# ]
# ///
"""Manager utility for the /yf-research skill.

Scope is deliberately narrow — defensive JSON extraction (`json-get`). Preflight
(deps + installed-rule hash + the idempotent gitignore scaffold) moved to the
`yf preflight` kernel (plan-010). Research-directory and index state is managed by
index_manager.py; report/citation tooling lives in link_normalizer.py and
credibility_scorer.py.
"""

import json
import sys

import click


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


@click.group()
def cli():
    """Manager for the /yf-research skill (defensive JSON extraction)."""
    pass


@cli.command("json-get")
@click.argument("keys", nargs=-1, required=True)
def json_get(keys: tuple[str, ...]):
    """Extract a value from JSON on stdin by key path (defensive).

    Tolerates warning prefixes and concatenated/array bd output by parsing the
    first balanced JSON value. Each argument is one nesting level; a numeric key
    indexes into a list (e.g. `bd show <id> --json | research_manager.py json-get 0 metadata`).
    """
    raw = sys.stdin.read()
    try:
        data = _extract_first_json(raw)
    except ValueError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError, ValueError):
            click.echo(
                f"ERROR: key {key!r} not found in path {' -> '.join(keys)}",
                err=True,
            )
            sys.exit(1)
    if isinstance(data, (dict, list)):
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(data)


if __name__ == "__main__":
    cli()
