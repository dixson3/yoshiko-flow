#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""finding_recurrence.py — parse reviews/pass-N.md sequences and detect recurring concerns.

Read-only. For one plan bundle (or every bundle a corpus_scan.py JSON census names), parses
each `reviews/pass-N.md` into a list of findings, fingerprints each finding's headline text,
and reports candidate cross-pass "thrash episodes": the SAME concern recurring in pass N and
again in pass N+k.

Format variance this parser is built against (measured 2026-08-28, see
../artifacts/tooling-notes.md — read that file before changing the regexes below):

  - Pass number: NEVER taken from frontmatter/title (both vary); always the filename `pass-N.md`.
  - Verdict: searched as either a `## Verdict: WORD` heading or a `**Verdict:** WORD` /
    `**Verdict:** **WORD**` metadata line; first match wins, extra matches are counted, not
    reconciled.
  - Findings are extracted from THREE candidate shapes independently:
      1. markdown table rows whose first cell matches a finding-id grammar ([A-Z]{1,3}\\d+)
      2. `##`/`###` prose subsections keyed by the same id grammar
      3. top-level bullets (`-`, `*`, `\\d+.`) inside a `## Concerns` section, id or not
    A file may contribute findings from more than one shape (e.g. a table row AND its prose
    elaboration) — those are collapsed by id-within-file before recurrence is computed, never
    silently deduped across files.
  - Two repos (yoshiko-flow plan-053-style, pybridge) sometimes state pass-over-pass
    reproduction EXPLICITLY in prose ("N of M concerns... verified genuinely resolved",
    "Reproduction of pass-N's ... resolutions"). Those sections are extracted as a distinct,
    higher-confidence "self_reported" recurrence signal, separate from and not blended with the
    text-similarity fingerprint match below.

Fingerprinting is a normalized-token shingle (Jaccard) similarity over each finding's headline
(first ~40 words) only — never the resolution/remediation prose, which describes the FIX and
spuriously matches across unrelated findings ("added an explicit check", "verified: 0
occurrences"). The threshold is tunable (--threshold) and every match reports its score, so a
human can judge; this tool is deliberately conservative — it is built to UNDER-report rather
than manufacture thrash, per the research plan's explicit constraint.

Usage:
    uv run finding_recurrence.py --bundle <path/to/plan-bundle-dir> [--threshold 0.35] [--json]
    uv run finding_recurrence.py --census <corpus_scan.json> [--threshold 0.35] [--json]
    uv run finding_recurrence.py --census <corpus_scan.json> --min-passes 2 --json > episodes.json

Exit codes:
    0  ran (episodes found or not — check the report)
    1  named bundle/census path does not exist, or no bundles had >=2 review passes
    2  bad arguments
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

FINDING_ID_RE = re.compile(
    r"^(?:[A-Z]{2,6}-[A-Z]{0,3}\d{1,3}|(?:NC|NEW|ML|CG)?[A-Z]{1,3}\d{1,3})$"
)
FINDING_ID_INLINE_RE = re.compile(
    r"\b([A-Z]{2,6}-[A-Z]{0,3}\d{1,3}|(?:NC|NEW|ML|CG)?[A-Z]{1,3}\d{1,3})\b"
)

# Verdict label wording varies ("Verdict:", "Red-team verdict:") and some files trail the
# value with more prose on the same line ("REVISE → all concerns resolved..."), so neither the
# label nor a hard end-of-line anchor can be assumed — see tooling-notes.md.
VERDICT_HEADING_RE = re.compile(r"^#{1,3}\s*[\w\- ]*Verdict:?\s*\**\s*(APPROVE|REVISE|REJECT|BLOCK|CONDITIONAL[\w ]*?)\b", re.IGNORECASE | re.MULTILINE)
VERDICT_BOLD_RE = re.compile(r"\*\*[\w\- ]*Verdict:?\*\*:?\s*\**\s*(APPROVE|REVISE|REJECT|BLOCK|CONDITIONAL[\w ]*?)\b", re.IGNORECASE)

CONCERNS_HEADING_RE = re.compile(r"^#{1,3}\s*Concerns?\b.*$", re.IGNORECASE | re.MULTILINE)
NEXT_HEADING_RE = re.compile(r"^#{1,3}\s+\S", re.MULTILINE)

TABLE_ROW_RE = re.compile(r"^\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|")
TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|$")

PROSE_SUBSECTION_RE = re.compile(
    r"^#{2,4}\s+([A-Z]{2,6}-[A-Z]{0,3}\d{1,3}|(?:NC|NEW|ML|CG)?[A-Z]{1,3}\d{1,3})\b.*$",
    re.MULTILINE,
)

BULLET_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")
BOLD_SEVERITY_RE = re.compile(r"\[(HIGH|MEDIUM|MEDIUM-HIGH|LOW|CRITICAL)\]", re.IGNORECASE)
TRAILING_SEVERITY_RE = re.compile(r"severity:\s*(high|medium|medium-high|low|critical)", re.IGNORECASE)
LEADING_BOLD_SEVERITY_RE = re.compile(r"\((HIGH|MEDIUM|MEDIUM-HIGH|LOW|CRITICAL)\)", re.IGNORECASE)

SELF_REPORT_HEADING_RE = re.compile(
    r"^#{1,3}\s*(Reproduction of pass-\d+|Pass-\d+ resolution verification|Pass \d+ resolution verification).*$",
    re.IGNORECASE | re.MULTILINE,
)
SELF_REPORT_PROSE_RE = re.compile(
    r"([^.\n]{0,200}\b(?:verified genuinely resolved|all (?:ten|nine|eight|seven|six|five|four|three|two|\d+) [a-z0-9\- ]*concerns[^.\n]{0,120})[^.\n]{0,200}\.)",
    re.IGNORECASE,
)

STOPWORDS = {
    "the", "a", "an", "is", "was", "are", "were", "be", "been", "being", "to", "of", "in",
    "on", "at", "by", "for", "with", "and", "or", "but", "not", "no", "it", "its", "this",
    "that", "these", "those", "as", "if", "then", "than", "so", "do", "does", "did", "has",
    "have", "had", "will", "would", "could", "should", "can", "may", "might", "must", "which",
    "who", "what", "when", "where", "why", "how", "into", "onto", "from", "over", "under",
    "any", "all", "each", "every", "both", "either", "neither", "own", "same", "such", "only",
    "also", "still", "now", "here", "there", "one", "two", "three",
}

WORD_RE = re.compile(r"[a-z0-9']+")


@dataclass
class Finding:
    finding_id: str | None
    shape: str  # "table" | "prose_subsection" | "bullet"
    severity: str | None
    text: str
    file: str
    line: int


@dataclass
class ParsedPass:
    file: str
    pass_number: int
    verdict: str | None
    verdict_match_count: int
    findings: list[Finding]
    self_reported_recurrence: list[str]
    parse_warnings: list[str] = field(default_factory=list)


@dataclass
class RecurrenceMatch:
    bundle: str
    earlier_pass: int
    earlier_file: str
    earlier_line: int
    earlier_finding_id: str | None
    earlier_text: str
    later_pass: int
    later_file: str
    later_line: int
    later_finding_id: str | None
    later_text: str
    similarity: float
    match_basis: str  # "id_reuse" | "text_similarity"
    pass_gap: int


def normalize_headline(text: str, max_words: int = 40) -> list[str]:
    # strip markdown emphasis / punctuation-ish noise, keep words
    words = WORD_RE.findall(text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return words[:max_words]


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def extract_verdict(text: str) -> tuple[str | None, int]:
    matches = VERDICT_HEADING_RE.findall(text) + VERDICT_BOLD_RE.findall(text)
    if not matches:
        return None, 0
    normalized = matches[0].strip().upper()
    return normalized, len(matches)


def slice_concerns_section(text: str) -> str | None:
    m = CONCERNS_HEADING_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = NEXT_HEADING_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def split_row_cells(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [c.strip() for c in stripped.split("|")]


SEVERITY_HEADER_NAMES = {"severity", "sev"}
CONCERN_HEADER_NAMES = {"concern", "finding", "issue", "description", "title"}
ID_HEADER_NAMES = {"#", "id", "no", "num"}


def extract_table_findings(text: str, filename: str) -> list[Finding]:
    """Parse EVERY markdown table in the file, locating columns by HEADER NAME rather than
    fixed position — measured column order varies across repos (yoshiko-flow plan-053 uses
    `| # | Severity | Concern |`; yoshiko-flow plan-019 uses `| # | Concern | Severity |
    Status | Resolution |`; see tooling-notes.md). A table with no recognizable id + concern
    header pair (e.g. the "Reproduction of pass-N" classification table, or an Operator
    Resolutions table with no id column) is skipped entirely rather than guessed at.
    """
    findings: list[Finding] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip().startswith("|"):
            i += 1
            continue
        # candidate header row; must be followed by a separator row
        if i + 1 >= len(lines) or not TABLE_SEP_RE.match(lines[i + 1].strip()):
            i += 1
            continue
        header_cells = [c.lower() for c in split_row_cells(line)]
        id_idx = next((idx for idx, c in enumerate(header_cells) if c in ID_HEADER_NAMES), None)
        concern_idx = next(
            (idx for idx, c in enumerate(header_cells) if any(n in c for n in CONCERN_HEADER_NAMES)),
            None,
        )
        severity_idx = next(
            (idx for idx, c in enumerate(header_cells) if any(n in c for n in SEVERITY_HEADER_NAMES)),
            None,
        )

        table_start = i
        i += 2  # skip header + separator
        if id_idx is None or concern_idx is None:
            # not a findings table we recognize (e.g. Reproduction/Resolutions-without-id
            # classification tables) — skip past its body without extracting
            while i < len(lines) and lines[i].strip().startswith("|"):
                i += 1
            continue

        while i < len(lines) and lines[i].strip().startswith("|"):
            row = lines[i]
            if TABLE_SEP_RE.match(row.strip()):
                i += 1
                continue
            cells = split_row_cells(row)
            if max(id_idx, concern_idx, severity_idx or 0) >= len(cells):
                i += 1
                continue
            raw_id = cells[id_idx].strip("*` ")
            body = cells[concern_idx].strip()
            severity = cells[severity_idx].strip("*` ") if severity_idx is not None else None
            if FINDING_ID_RE.match(raw_id) and body:
                findings.append(Finding(raw_id, "table", severity, body, filename, i + 1))
            i += 1
        _ = table_start
    return findings


def extract_prose_subsection_findings(text: str, filename: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    line_offsets = []
    pos = 0
    for line in lines:
        line_offsets.append(pos)
        pos += len(line) + 1

    matches = list(PROSE_SUBSECTION_RE.finditer(text))
    for idx, m in enumerate(matches):
        fid = m.group(1)
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        # line number of heading
        line_no = text.count("\n", 0, m.start()) + 1
        headline = " ".join(body.split()[:40])
        if headline:
            findings.append(Finding(fid, "prose_subsection", None, headline, filename, line_no))
    return findings


def extract_bullet_findings(concerns_text: str, filename: str, base_line: int) -> list[Finding]:
    findings: list[Finding] = []
    lines = concerns_text.splitlines()
    current: list[str] | None = None
    current_line = 0
    current_indent = None

    def flush():
        if current is not None:
            body = " ".join(current).strip()
            if body:
                sev = None
                sm = BOLD_SEVERITY_RE.search(body) or TRAILING_SEVERITY_RE.search(body) or LEADING_BOLD_SEVERITY_RE.search(body)
                if sm:
                    sev = sm.group(1).upper()
                fid_m = FINDING_ID_INLINE_RE.search(body)
                fid = fid_m.group(1) if fid_m and body.strip().startswith(("*", "C", "N", fid_m.group(1))) else (fid_m.group(1) if fid_m else None)
                findings.append(Finding(fid, "bullet", sev, body, filename, base_line + current_line))

    for i, line in enumerate(lines):
        bm = BULLET_RE.match(line)
        indent = len(line) - len(line.lstrip())
        if bm and indent <= 2:
            flush()
            current = [bm.group(1)]
            current_line = i + 1
            current_indent = indent
        elif current is not None and line.strip() and (current_indent is None or indent > current_indent or not line.lstrip().startswith(("-", "*"))):
            current.append(line.strip())
        elif current is not None and not line.strip():
            continue
    flush()
    return findings


def dedupe_findings(findings: list[Finding]) -> list[Finding]:
    """Collapse same-id findings from different extraction shapes within one file.

    Prefers prose_subsection > table > bullet as the canonical text (fullest context),
    but always keeps every DISTINCT id, and keeps id-less findings as-is (can't dedupe those
    safely — they have no join key).
    """
    by_id: dict[str, list[Finding]] = {}
    idless: list[Finding] = []
    for f in findings:
        if f.finding_id:
            by_id.setdefault(f.finding_id, []).append(f)
        else:
            idless.append(f)
    shape_rank = {"prose_subsection": 0, "table": 1, "bullet": 2}
    out: list[Finding] = []
    for fid, group in by_id.items():
        group.sort(key=lambda f: shape_rank.get(f.shape, 9))
        out.append(group[0])
    out.extend(idless)
    return out


def extract_self_reported(text: str) -> list[str]:
    hits = []
    for m in SELF_REPORT_HEADING_RE.finditer(text):
        # capture the paragraph following the heading, trimmed
        start = m.end()
        rest = text[start:start + 400]
        hits.append((m.group(0) + " :: " + " ".join(rest.split())[:300]).strip())
    for m in SELF_REPORT_PROSE_RE.finditer(text):
        hits.append(m.group(1).strip())
    return hits


def parse_pass_file(path: Path) -> ParsedPass:
    text = path.read_text(errors="replace")
    warnings: list[str] = []

    m = re.search(r"pass-(\d+)", path.name)
    if not m:
        warnings.append(f"could not extract pass number from filename {path.name}")
        pass_number = -1
    else:
        pass_number = int(m.group(1))

    verdict, vcount = extract_verdict(text)
    if verdict is None:
        warnings.append("no verdict found")

    findings: list[Finding] = []
    findings.extend(extract_table_findings(text, str(path)))
    findings.extend(extract_prose_subsection_findings(text, str(path)))

    concerns_text = slice_concerns_section(text)
    if concerns_text:
        # locate base line number of the concerns section for bullet line numbers
        cm = CONCERNS_HEADING_RE.search(text)
        base_line = text.count("\n", 0, cm.end()) + 1 if cm else 0
        findings.extend(extract_bullet_findings(concerns_text, str(path), base_line))
    else:
        warnings.append("no '## Concerns' section found (bullet-shape extraction skipped)")

    if not findings:
        warnings.append("no findings extracted by any shape")

    findings = dedupe_findings(findings)
    self_reported = extract_self_reported(text)

    return ParsedPass(
        file=str(path),
        pass_number=pass_number,
        verdict=verdict,
        verdict_match_count=vcount,
        findings=findings,
        self_reported_recurrence=self_reported,
        parse_warnings=warnings,
    )


def compute_recurrence(
    bundle_name: str, passes: list[ParsedPass], threshold: float, id_floor: float
) -> tuple[list[RecurrenceMatch], list[RecurrenceMatch]]:
    """Returns (recurrence_matches, weak_id_reuse_matches).

    Measured fact this split exists to handle (see tooling-notes.md): finding-id GRAMMAR is
    not the same thing as finding-id STABILITY. Some repos/plans reuse `C1`/`C2`/... as fresh,
    UNRELATED ids on every pass rather than carrying a concern's id forward — id equality alone
    is then a coincidence, not evidence of recurrence. An id_reuse match is only promoted to
    `recurrence_matches` if its headline similarity ALSO clears `id_floor` (a much lower bar
    than the text_similarity `threshold`, since same-id + on-topic is already corroborating).
    Below that floor it goes to `weak_id_reuse_matches` — reported, never silently dropped, but
    kept out of the headline count so a naive `len(recurrence_matches)` consumer is not misled.
    """
    passes_sorted = sorted([p for p in passes if p.pass_number >= 0], key=lambda p: p.pass_number)
    matches: list[RecurrenceMatch] = []
    weak_id_matches: list[RecurrenceMatch] = []

    # precompute normalized token sets
    tokset: dict[tuple[str, int], set[str]] = {}
    for p in passes_sorted:
        for idx, f in enumerate(p.findings):
            tokset[(f.file, idx)] = set(normalize_headline(f.text))

    for i, earlier in enumerate(passes_sorted):
        for later in passes_sorted[i + 1:]:
            for ei, ef in enumerate(earlier.findings):
                for li, lf in enumerate(later.findings):
                    basis = None
                    score = 0.0
                    if ef.finding_id and lf.finding_id and ef.finding_id == lf.finding_id:
                        basis = "id_reuse"
                        etoks = tokset[(ef.file, ei)]
                        ltoks = tokset[(lf.file, li)]
                        score = jaccard(etoks, ltoks)
                    else:
                        etoks = tokset[(ef.file, ei)]
                        ltoks = tokset[(lf.file, li)]
                        score = jaccard(etoks, ltoks)
                        if score >= threshold:
                            basis = "text_similarity"
                    if basis is None:
                        continue
                    if basis == "text_similarity" and score < threshold:
                        continue
                    record = RecurrenceMatch(
                        bundle=bundle_name,
                        earlier_pass=earlier.pass_number,
                        earlier_file=ef.file,
                        earlier_line=ef.line,
                        earlier_finding_id=ef.finding_id,
                        earlier_text=ef.text[:300],
                        later_pass=later.pass_number,
                        later_file=lf.file,
                        later_line=lf.line,
                        later_finding_id=lf.finding_id,
                        later_text=lf.text[:300],
                        similarity=round(score, 3),
                        match_basis=basis,
                        pass_gap=later.pass_number - earlier.pass_number,
                    )
                    if basis == "id_reuse" and score < id_floor:
                        weak_id_matches.append(record)
                    else:
                        matches.append(record)
    return matches, weak_id_matches


def process_bundle(bundle_dir: Path, threshold: float, id_floor: float) -> dict:
    reviews_dir = bundle_dir / "reviews"
    if not reviews_dir.is_dir():
        return {
            "bundle": str(bundle_dir),
            "error": f"no reviews/ directory at {reviews_dir}",
            "pass_count": 0,
            "passes": [],
            "recurrence_matches": [],
            "weak_id_reuse_matches": [],
            "self_reported_signals": [],
        }
    pass_files = sorted(reviews_dir.glob("pass-*.md"))
    parsed = [parse_pass_file(p) for p in pass_files]
    if len(parsed) >= 2:
        matches, weak_matches = compute_recurrence(str(bundle_dir), parsed, threshold, id_floor)
    else:
        matches, weak_matches = [], []
    self_reported = [
        {"file": p.file, "pass": p.pass_number, "signal": s}
        for p in parsed
        for s in p.self_reported_recurrence
    ]
    return {
        "bundle": str(bundle_dir),
        "error": None,
        "pass_count": len(parsed),
        "passes": [asdict(p) for p in parsed],
        "recurrence_matches": [asdict(m) for m in matches],
        "weak_id_reuse_matches": [asdict(m) for m in weak_matches],
        "self_reported_signals": self_reported,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--bundle", type=Path, help="path to a single plan bundle directory")
    src.add_argument("--census", type=Path, help="corpus_scan.py --json output; process every bundle with >= --min-passes review passes")
    ap.add_argument("--threshold", type=float, default=0.35, help="Jaccard similarity threshold for a text_similarity match (default 0.35)")
    ap.add_argument("--id-floor", type=float, default=0.15, help="minimum headline similarity for an id-reuse match to count as real recurrence rather than coincidental id reuse (default 0.15)")
    ap.add_argument("--min-passes", type=int, default=2, help="skip bundles with fewer than this many review passes (default 2)")
    ap.add_argument("--json", action="store_true", help="emit JSON (default: human summary)")
    args = ap.parse_args()

    bundle_dirs: list[Path] = []
    skipped_missing = 0
    if args.bundle:
        if not args.bundle.is_dir():
            print(f"error: bundle path does not exist: {args.bundle}", file=sys.stderr)
            return 1
        bundle_dirs = [args.bundle]
    else:
        if not args.census.is_file():
            print(f"error: census file does not exist: {args.census}", file=sys.stderr)
            return 1
        census = json.loads(args.census.read_text())
        for repo in census.get("repos", []):
            for b in repo.get("bundles", []):
                if b.get("review_pass_count", 0) >= args.min_passes:
                    bundle_dirs.append(Path(b["bundle_path"]))
                else:
                    skipped_missing += 1

    if not bundle_dirs:
        print("error: no bundles to process (none met --min-passes)", file=sys.stderr)
        return 1

    results = [process_bundle(bd, args.threshold, args.id_floor) for bd in bundle_dirs]

    total_findings = sum(sum(len(p["findings"]) for p in r["passes"]) for r in results)
    total_matches = sum(len(r["recurrence_matches"]) for r in results)
    total_weak_id = sum(len(r["weak_id_reuse_matches"]) for r in results)
    total_self_reported = sum(len(r["self_reported_signals"]) for r in results)
    parse_warning_count = sum(len(p["parse_warnings"]) for r in results for p in r["passes"])
    error_bundles = [r["bundle"] for r in results if r["error"]]

    if args.json:
        out = {
            "threshold": args.threshold,
            "id_floor": args.id_floor,
            "bundles_processed": len(results),
            "bundles_skipped_min_passes": skipped_missing,
            "bundles_with_errors": error_bundles,
            "total_findings_extracted": total_findings,
            "total_parse_warnings": parse_warning_count,
            "total_recurrence_matches": total_matches,
            "total_weak_id_reuse_matches": total_weak_id,
            "total_self_reported_signals": total_self_reported,
            "results": results,
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"bundles processed: {len(results)} (skipped {skipped_missing} with < {args.min_passes} passes)")
        print(f"findings extracted: {total_findings}")
        print(f"parse warnings: {parse_warning_count}")
        print(f"candidate recurrence matches (threshold={args.threshold}, id_floor={args.id_floor}): {total_matches}")
        print(f"weak id-reuse (same id, unrelated content — NOT counted as recurrence): {total_weak_id}")
        print(f"self-reported cross-pass signals: {total_self_reported}")
        if error_bundles:
            print(f"bundles with errors: {error_bundles}", file=sys.stderr)
        for r in results:
            if r["recurrence_matches"]:
                print(f"\n--- {r['bundle']} ---")
                for m in r["recurrence_matches"]:
                    print(
                        f"  pass {m['earlier_pass']} -> pass {m['later_pass']} "
                        f"(gap {m['pass_gap']}, {m['match_basis']}, sim={m['similarity']}): "
                        f"{(m['earlier_finding_id'] or '?')}/{(m['later_finding_id'] or '?')} "
                        f"\"{m['later_text'][:80]}\""
                    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
