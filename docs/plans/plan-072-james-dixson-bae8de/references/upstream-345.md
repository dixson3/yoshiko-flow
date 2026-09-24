---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #345 - yf-okf: REQ-OKF-010 metadata-line scan is fence-blind
  — flags quoted command output, so the only way to pass is to corrupt the evidence'
---
# Upstream #345: yf-okf: REQ-OKF-010 metadata-line scan is fence-blind — flags quoted command output, so the only way to pass is to corrupt the evidence

- **Number:** 345
- **Title:** yf-okf: REQ-OKF-010 metadata-line scan is fence-blind — flags quoted command output, so the only way to pass is to corrupt the evidence
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

## Observed

During research 061's package phase, `okf.py check` reported:

```
[error] artifacts/corpus-roundtrip.md  REQ-OKF-010
        a **Field:** metadata line sits below the first ##
```

The flagged line is **inside a fenced code block**. It is captured `pandoc` stdout, shown as evidence that pandoc deletes YAML frontmatter — i.e. the "metadata line" is *the subject of the research finding*, quoted verbatim.

Grepping `okf.py` for fence / backtick / `in_code` handling returns nothing: **the scan is fence-blind.**

## Why this is worse than an ordinary false positive

Any artifact that quotes markdown-shaped command output will trip it — and a research corpus quoting tool output is not an edge case, it is the normal shape of an evidence artifact. Documents about markdown are exactly the documents most likely to *contain* markdown.

**The only ways to make the check pass are to corrupt the evidence or to suppress the check.** 061 did neither — it left the captured output byte-exact and filed this instead. But a less careful run, or an agent under instruction to get the gate green, would edit captured tool output to satisfy a linter. That is a conformance check creating an incentive to falsify evidence, which is a considerably more serious failure mode than a noisy warning.

## Fix

Skip fenced regions (```` ``` ```` and `~~~`) and indented code blocks when scanning for `**Field:**` metadata lines. The same fence-awareness likely belongs in any other line-oriented scan in `okf.py` — worth a sweep rather than a point fix.

## Repro

Place a fenced block containing a line of the form `**Field:** value` below the first `##` heading in any OKF artifact, then run `okf.py check` on the bundle.

