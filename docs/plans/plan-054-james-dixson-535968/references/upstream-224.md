---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #224: Success criteria that use `grep -qv` are environment-dependent: under ugrep the criterion CANNOT FAIL, and a false 'green' survives repeated verification

- **Number:** 224
- **Title:** Success criteria that use `grep -qv` are environment-dependent: under ugrep the criterion CANNOT FAIL, and a false 'green' survives repeated verification
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Filed by operator decision from the **plan-004** session in `dixson3/rc-files`. Sibling of #203 but a **different mechanism**: not "failure in output, success in `$?`", but *the same command returning different exit codes depending on which `grep` implementation is on PATH*.

## The defect

plan-004's SC1 asserted that a hostname decision has exactly one home in executable code:

```bash
grep -rn 'byid-mba-dixson3' bin/ cliproxyapi/ \
  | grep -v '^[^:]*:[0-9]*: *#' \
  | grep -qv '^bin/lib/variant.sh:'      # -> exit 1 expected
```

Run inside a Claude Code session, `grep` is a **shell function shadowing the binary with `ugrep`**:

```
$ which grep
grep () { ... exec -a ugrep "$_cc_bin" -G --ignore-files ... }
$ grep --version
ugrep 7.5.0 aarch64-apple-macosx
```

And **`ugrep -qv` does not agree with BSD/GNU `grep -qv`**. Measured on identical two-line input, in the same shell:

```
$ grep -cv '^bin/lib/variant.sh:' t.txt      # ugrep
1                                            # one non-matching line EXISTS
$ grep -qv '^bin/lib/variant.sh:' t.txt      # ugrep
exit=1                                       # ...but -q says "no"

$ command grep -qv '^bin/lib/variant.sh:' t.txt   # real grep
exit=0                                            # correct
```

`-c` and `-q` **contradict each other on the same input**. `-q` appears to report whether the *pattern* matched, rather than whether the inverted selection produced output.

## Consequence: a criterion that cannot fail

SC1 was **genuinely false from Epic 2 onward** — `cliproxyapi/README.md` legitimately contains the hostname twice, because Issues 2.2 and 4.1 *require* documenting the variant table. Ground truth with real `grep`:

```
$ command grep -rn 'byid-mba-dixson3' bin/ cliproxyapi/ | ... | command grep -qv '^bin/lib/variant.sh:'
exit=0     # VIOLATED
```

But every inline run reported exit 1 — **green**. It was reported green repeatedly, by the executing agent *and independently by an observing parent session that thought it was double-checking*. Two agents, same artifact, same wrong answer, because both ran in the same shadowed shell.

`recheck-criteria` at §6.4 caught it — running in a clean subshell with the real binary. That step earned its place: it is exactly the "true at discharge, false at completion" case it was built for, except the criterion was never true at all.

## Two distinct bugs, and the second is the general one

1. **SC1's text and its command disagreed.** The text said *"in executable code"*; the command grepped everything including `.md`. Fixed in-plan with `--exclude='*.md'`, verified to still catch a planted second implementation in `bin/pidev` (exit 0 with real grep).
2. **`grep -qv` is not portable.** This is the one worth a convention. Any criterion, gate `Test:`, or `CHANGE-VALIDATION.md` row using `grep -qv` has an exit code that depends on the operator's shell environment — and in the environment these skills are *most often run in*, it is silently wrong in the permissive direction.

## Suggested fix

- **Convention:** never use `grep -qv` in a criterion, gate test, or validation row. Use `grep -v PATTERN | grep -q .`, which measured **correct under ugrep** (exit 0 on the same input where `grep -qv` returned 1). Or invert to a positive match, or count with `-c` and compare.
- **Sweep the corpus** for existing `grep -qv` in `spec/*.md` `Verification:` lines, gate `Test:` clauses, `CHANGE-VALIDATION.md` recipes, and shipped scripts.
- **Consider a `doc_lint` check** flagging `grep -qv` in a `Verification:` clause — this is mechanically detectable, unlike #165's prose-shaped-as-command class.
- Worth noting in `yf-skill-authoring`: shipped skills run inside agent harnesses that **shadow standard tools**. A criterion's portability includes the harness, not just the OS.

## Why this is not #203

#203 is about instruments that report failure in output while exiting 0 — a contract violation *within* a tool. Here the tool is honest and consistent with itself; the exit code is correct for `ugrep`'s reading of `-q -v`. The failure is that **the criterion's author assumed one `grep`** and got another. Fixing #203's five instruments would not touch this.

## Related

- #203 — exit-code discipline (sibling class).
- #165 — `Verification:` lines that are prose shaped like commands; this is the inverse — a real command whose exit code is not what the author believes.
