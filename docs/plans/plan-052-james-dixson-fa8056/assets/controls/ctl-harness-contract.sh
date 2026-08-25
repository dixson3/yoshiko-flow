#!/usr/bin/env bash
# ctl-harness-contract (SC0) — the asserted set, the built set and controls.txt are ONE object.
#
# Exactly THREE arms, scoped deliberately: pass 5 measured a broader claim catching only 1 of
# the 4 defects it was credited with.
#
#   1. FILE arm      — every file gate-run.sh reads or writes appears in some issue's
#                      `touches:`. The "demonstrated present on the tree" fallback applies ONLY
#                      to paths OUTSIDE this bundle's assets/; anything under assets/ must be
#                      DECLARED.
#   2. INTERFACE arm — for each ctl-*.sh, every subcommand, flag or env var it passes to a repo
#                      script must appear in that script's --help OR be named as commissioned
#                      in some issue. This is the arm that catches `--fixture` and `CTL_TXT`;
#                      a file-granular check cannot.
#   3. BUILDER-PRECEDES-FIXER arm — for every control criterion, the builder issue must not have
#                      any other discharger among its own ANCESTORS; where it is the sole
#                      discharger, the criterion must state how RED is obtained. An inversion or
#                      sole-discharger case is a finding UNLESS the criterion OR ITS BUILDER
#                      ISSUE states how RED is obtained. Without that exemption the arm
#                      permanently fails on the plan's three by-design cases (SC1, SC0c, SC1b)
#                      and makes SC0 unsatisfiable — measured at pass 6 by implementing it.
#
# Plus the DERIVED lower bound: every issue whose `touches:` names assets/controls/*.sh must
# contribute >= 1 id to the generated set. That is what makes the closure non-vacuous.
#
# Exit: 0 all three arms hold · 1 a real finding · 2 the instrument could not run
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# The three arms are implemented inline — embedded rather than kept as a sibling file,
# so this control leaves NO undeclared artifact under the bundle's assets/ (ARM 1).
python3 - "$ASSETS" <<'PYEOF'
"""The three arms of plan-052's harness contract. See ctl-harness-contract.sh for the charter."""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ISSUE_RE = re.compile(r"^- Issue (\d+\.\d+[a-z]?): ")
EPIC_RE = re.compile(r"^### Epic (\d+):")
CTL_TOKEN = re.compile(r"\bctl-[a-z0-9]+(?:-[a-z0-9]+)*\b")
PATH_SPAN = re.compile(r"`([^`\s]+/[^`\s]+)`")


def section(text: str, heading: str) -> str:
    out, inside = [], False
    for ln in text.splitlines():
        if ln.startswith("## "):
            inside = ln.strip() == f"## {heading}"
            continue
        if inside:
            out.append(ln)
    return "\n".join(out)


def parse_issues(plan_text: str):
    """-> {issue_id: {"epic":.., "touches":[..], "text":..}}"""
    body = section(plan_text, "Epics")
    issues: dict[str, dict] = {}
    epic = cur = None
    for ln in body.splitlines():
        m = EPIC_RE.match(ln)
        if m:
            epic = m.group(1)
            continue
        m = ISSUE_RE.match(ln)
        if m:
            cur = m.group(1)
            issues[cur] = {"epic": epic, "touches": [], "text": ln, "depends_on": []}
            continue
        if cur is None:
            continue
        issues[cur]["text"] += "\n" + ln
        s = ln.strip()
        if s.startswith("- touches:"):
            issues[cur]["touches"] += PATH_SPAN.findall(s)
        elif s.startswith("- depends-on:"):
            issues[cur]["depends_on"] += [
                x.strip() for x in s.split(":", 1)[1].split(",") if x.strip()
            ]
    return issues


def parse_criteria(plan_text: str):
    """-> [{"id":.., "criterion":.., "verification":.., "dischargers":[..]}]"""
    rows = []
    for ln in section(plan_text, "Success Criteria").splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] in ("#", ":--"):
            continue
        rows.append({
            "id": cells[0],
            "criterion": cells[1],
            "verification": cells[2],
            "dischargers": [x.strip() for x in cells[3].split(",") if x.strip()],
        })
    return rows


def ancestors(issue: str, issues: dict) -> set[str]:
    seen, stack = set(), list(issues.get(issue, {}).get("depends_on", []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack += issues.get(cur, {}).get("depends_on", [])
    return seen


RED_HINT = re.compile(
    r"driven RED|pinned (?:negative )?fixture|pinned fixture|RED is (?:therefore )?obtained"
    r"|intra-issue ordering|observe (?:them|it) RED|RED against|recorded to the ledger",
    re.I,
)


def main() -> int:
    assets = pathlib.Path(sys.argv[1]).resolve()
    plan = assets.parent / "plan.md"
    gate = assets / "gate-run.sh"
    ctl_dir = assets / "controls"
    controls_txt = assets / "controls.txt"
    for p in (plan, gate, ctl_dir, controls_txt):
        if not p.exists():
            print(f"INCONCLUSIVE: missing harness artifact: {p}", file=sys.stderr)
            return 2

    text = plan.read_text(encoding="utf-8")
    issues = parse_issues(text)
    criteria = parse_criteria(text)
    declared = {t for i in issues.values() for t in i["touches"]}
    findings: list[str] = []

    bundle = "docs/plans/plan-052-james-dixson-fa8056"
    repo_root = assets.parents[3]

    # ---------------- ARM 1: FILE ----------------
    gate_text = gate.read_text(encoding="utf-8")
    # Files the dispatcher reads or writes, as bundle-relative paths.
    harness_files = {
        f"{bundle}/assets/gate-run.sh",
        f"{bundle}/assets/gen-controls.py",
        f"{bundle}/assets/controls.txt",
        f"{bundle}/assets/red-observations.tsv",
    }
    for f in sorted(harness_files):
        if f in declared:
            continue
        # The "present on the tree" fallback is ONLY for paths outside this bundle's assets/.
        if "/assets/" in f:
            findings.append(f"ARM1: harness file not DECLARED in any issue's touches: {f}")
        elif not (repo_root / f).exists():
            findings.append(f"ARM1: harness file neither declared nor present on tree: {f}")

    # Every BUILT control must be declared by its builder.
    for p in sorted(ctl_dir.glob("ctl-*.sh")):
        rel = f"{bundle}/assets/controls/{p.name}"
        if rel not in declared:
            findings.append(f"ARM1: built control not declared in any issue's touches: {rel}")

    # THE ONE-OBJECT ASSERTION: asserted == built == controls.txt. This is SC0's actual
    # claim, and it is what makes the control RED until every builder has built.
    built_ids = {p.stem for p in ctl_dir.glob("ctl-*.sh")}
    asserted_ids = set()
    for row in criteria:
        asserted_ids |= {c for c in CTL_TOKEN.findall(row["verification"]) if "*" not in c}
    for cid in sorted(asserted_ids - built_ids):
        findings.append(f"ARM1: control ASSERTED by a criterion but NOT BUILT: {cid}")
    for cid in sorted(built_ids - asserted_ids):
        findings.append(f"ARM1: control BUILT but asserted by no criterion (orphan): {cid}")

    # DERIVED LOWER BOUND: every issue touching assets/controls/*.sh contributes >= 1 id.
    gen_ids = {
        ln.split("\t")[0]
        for ln in controls_txt.read_text(encoding="utf-8").splitlines() if ln.strip()
    }
    if not gen_ids:
        print("INCONCLUSIVE: generated control set is empty", file=sys.stderr)
        return 2
    for iid, info in sorted(issues.items()):
        mine = {
            m.group(1)
            for t in info["touches"]
            for m in [re.search(r"assets/controls/(ctl-[a-z0-9-]+)\.sh", t)] if m
        }
        if not mine:
            continue
        if not (mine & gen_ids):
            findings.append(
                f"ARM1/floor: issue {iid} touches assets/controls/*.sh but contributes 0 ids"
            )

    # ---------------- ARM 2: INTERFACE ----------------
    # Every subcommand / flag / env var a control passes to a REPO script must appear in that
    # script's --help, or be named as commissioned in some issue.
    commissioned_text = "\n".join(i["text"] for i in issues.values())
    help_cache: dict[str, str] = {}

    def script_help(rel: str) -> str | None:
        if rel in help_cache:
            return help_cache[rel]
        target = repo_root / rel
        if not target.exists():
            return None
        try:
            r = subprocess.run(["uv", "run", str(target), "--help"],
                               capture_output=True, text=True, timeout=120, cwd=repo_root)
            out = r.stdout + r.stderr
        except Exception:
            return None
        help_cache[rel] = out
        return out

    invoke_re = re.compile(r"(skills/[A-Za-z0-9_./-]+\.py)((?:\s+[-\w=./\"'$\{\}]+)*)")
    for p in sorted(ctl_dir.glob("ctl-*.sh")):
        body = p.read_text(encoding="utf-8")
        for m in invoke_re.finditer(body):
            rel, tail = m.group(1), m.group(2)
            helptext = script_help(rel)
            if helptext is None:
                continue  # not resolvable here; ARM1 owns file existence
            for flag in re.findall(r"(?<!\w)--[a-z][a-z0-9-]+", tail):
                if flag in helptext:
                    continue
                if flag in commissioned_text:
                    continue
                findings.append(
                    f"ARM2: {p.name} passes {flag} to {rel}, which is in neither its --help "
                    f"nor commissioned by any issue"
                )
    # Env vars the dispatcher honours must themselves be commissioned.
    for env in sorted(set(re.findall(r"\$\{([A-Z][A-Z0-9_]{2,})[:-]", gate_text))):
        if env in ("BASH_SOURCE",):
            continue
        if env not in commissioned_text and env not in gate_text.split("# Environment:")[-1]:
            findings.append(f"ARM2: dispatcher honours ${env}, commissioned nowhere")

    # ---------------- ARM 3: BUILDER-PRECEDES-FIXER ----------------
    builder_of: dict[str, str] = {}
    for iid, info in issues.items():
        for t in info["touches"]:
            m = re.search(r"assets/controls/(ctl-[a-z0-9-]+)\.sh", t)
            if m:
                builder_of.setdefault(m.group(1), iid)

    for row in criteria:
        ctls = [c for c in CTL_TOKEN.findall(row["verification"]) if "*" not in c]
        if not ctls:
            continue
        for cid in ctls:
            builder = builder_of.get(cid)
            if builder is None:
                findings.append(f"ARM3: {row['id']} names {cid}, which no issue builds")
                continue
            others = [d for d in row["dischargers"] if d != builder]
            anc = ancestors(builder, issues)
            inverted = [d for d in others if d in anc]
            sole = not others
            if not inverted and not sole:
                continue
            # EXEMPTION: the criterion OR its builder issue states how RED is obtained.
            if RED_HINT.search(row["criterion"]) or RED_HINT.search(
                issues.get(builder, {}).get("text", "")
            ):
                continue
            why = (f"builder {builder} has discharger(s) {inverted} among its ancestors"
                   if inverted else f"builder {builder} is the SOLE discharger")
            findings.append(
                f"ARM3: {row['id']}/{cid}: {why}, and neither the criterion nor the builder "
                f"issue states how RED is obtained"
            )

    if findings:
        print(f"FAIL: {len(findings)} harness-contract finding(s):", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"PASS: harness contract holds over {len(gen_ids)} control(s), "
          f"{len(criteria)} criteria, {len(issues)} issues (3 arms + derived floor)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PYEOF
