---
type: Finding
okf_spec: OKF-PLAN
id: exp-006-round-trip-and-repin
description: Only 32 of 1567 okf-lint findings are the genuine disagreement, and all 32 flip on root framing — which OKF v0.2 is silent on. The write half cannot be tested.
---

# Finding: Characterise the okf-lint round-trip disagreement (#170), and determine what re-pinning `OKF-BASELINE.md` changes

### Approach Tested

Strictly read-only. bookpipe's `okf-lint.py` was copied to a scratch mirror (sole edit: raising the
`problems[:40]` print cap); write-path tests used the real script since it resolves siblings from
`__file__`. Every mutating run targeted a `$(mktemp -d)` copy. Runs: the repo root; a single bundle
copied to tmp with and without an `AGENTS.md` sentinel; the same bundle nested one level under a
synthetic vault root; `--fix --dry-run`; `--fix` forced by relocating under `Themes/`; both delegated
generators directly. Live spec fetched and diffed against the vendored copy; old location fetched and
md5-compared. Neither repo modified.

### Result

**measured:** — only 32 of 1567 findings are the genuine disagreement. Full categorisation (sums to
1567): 1169 broken links (**mostly noise** — placeholder link text like `relative-url-1`, plus the two
vendored OKF spec copies whose own example links resolve as real); 317 "has N concepts but no
index.md" (**root-framing artefact + v0.1 lag** — v0.2 §8 says `index.md` **MAY** appear in any
directory); **32 `non-root index.md must not carry frontmatter`** — the real finding; 26
`index.md: lists missing file log.md` (**an okf-lint defect**: `have` excludes reserved names but
`listed` does not, so a bundle correctly linking its own `log.md` is reported as listing a ghost); 9
filename-slug + 10 vault-policy findings (**bookpipe-specific, no OKF analogue**).

**measured:** — do NOT read the zero B1/B2 failures as a clean bill of health. The per-folder loop
`continue`s on a missing `index.md`, so the 317 no-index findings **suppress the concept-level checks
entirely**. Only **~100 of 1383** concept documents were actually frontmatter/type-checked; **~1285
were skipped unexamined.** The correct claim is narrow: of the ~100 inspected, all passed, and yf's
extension keys drew no complaint — okf-lint reads only `type` on concept documents.

**measured:** — the root-framing crux is a bit-for-bit flip. `is_root_index = (p == "index.md")`. The
identical bundle, byte-for-byte:

- `--root <bundle>`, no `AGENTS.md` -> **refuses to run at all** (okf-lint cannot lint a bare OKF
  bundle; it requires a bookpipe sentinel)
- `--root <bundle>` + stub `AGENTS.md` -> the index **passes**; both the frontmatter finding and the
  `log.md` ghost **disappear**
- same bundle one level down -> the finding **reappears**

All 32 findings of this class, and the 26 ghosts, are **entirely an artefact of where the consumer
decided the root was.** Nothing about the bundle changed.

**measured:** — OKF v0.2 IS SILENT on identifying a bundle root, and the gap is circular. §2 defines a
bundle as *"the unit of distribution"* with no root-identification procedure. §3 explicitly
contemplates *"A subdirectory within a larger repository"* — the spec **states** bundle root != repo
root, then gives a consumer no way to find it. §12 permits `okf_version` in *"the only place
frontmatter is permitted in an `index.md`"*. So **the only in-band marker of a bundle root is exactly
the key a wrongly-rooted consumer will reject as a violation.** No sentinel, manifest, or naming
convention appears anywhere in the 1006-line spec. This is an upstream specification defect, not a bug
in either tool.

Both tools resolve the silence identically in *form* and oppositely in *target*: yf's `REQ-OKF-004`
already says *"root-ness is a property of the INVOCATION, not of the filesystem"*, and okf-lint agrees
— but its invocation names the **vault**, not the bundle.

**measured:** — the write half CANNOT be tested. `--fix` fires only on bookpipe's `REFERENCE_TREES`, so
`--fix --dry-run` over the yf repo emitted **no `WOULD FIX` line at all** — structurally unreachable.
Forcing it by relocating under `Themes/` crashed: both generators write to hard-coded vault paths
(`FileNotFoundError: .../Book/index.md`). The bundle's `index.md` md5 was **unchanged** before and
after. **No third-party write/re-emit path exists to exercise.** #170's key-preservation question is
answered on the **read** side only.

**measured:** — I WAS WRONG that the old location is frozen. `knowledge-catalog/okf/SPEC.md` is
**md5-identical to the live copy** (`482250cc3d8987fbc711f54073f62c85`) and received the ISO-8601
commit on 2026-08-21T01:44Z — **18 hours before** the new repo's merge. The freeze notice is
**prospective intent, not observed state**.

**measured:** — vendored -> live diff is 41 lines, 100% the ISO-8601 change, and **§13 "Changes from
v0.1" was not updated** to mention it.

**measured:** — impact on this corpus is ZERO. `stale_after`, `usage_window`, `last_modified`,
`generated`, `verified` appear in **0** yf artifacts. `created: '2026-08-28'` is a **yf extension key**,
not an OKF timestamp key, so §5's rule does not reach it.

**measured:** — the citation surface is far smaller than it looks: 146 occurrences across 35 files, but
only 2 lines of live prose are normative (`yf-okf/SPEC.md:13`, `OKF-BASELINE.md:18`). The rest are
immutable provenance records — research sources, fixture corpora, issue snapshots — and re-pointing
them would falsify history.

**measured:** — yf's own corpus is internally inconsistent on the pin: of 32 index files, **21 carry
`okf_version: 0.1`** and 11 carry `0.2`, while all four `okf.py` copies pin `"0.2"`.

### Implications for Plan

**#170 is small and well-bounded** — 2% of findings, all flipping on one variable — not a corpus
problem. **And it is not resolvable by changing yf**: removing `okf_version` to satisfy okf-lint would
delete the only in-band root marker the spec defines. There is no yf-side change that makes both
framings pass.

**The ISO-8601 change is a non-event for the corpus but a major event for the pin's credibility.**
Content changed materially under an unchanged `**Version 0.2**` header with §13 not updated. "v0.2"
cannot function as a pin.

**My "the old location is frozen" premise was factually wrong.** The re-pin rationale must rest on
upstream's *stated intent*, which is sufficient and honest, not on observed staleness.

### Recommendations

1. **Record the root-identification silence in BOTH files, split by authority.** `OKF-BASELINE.md`
   gains a *"What OKF does not say: locating a bundle root"* section — quoting §2/§3/§8/§12, stating
   the absence as measured fact, and naming the circularity. `OKF-YF-EXTENSIONS.md` carries the
   *decision* that fills it: a yf artifact folder is a bundle root, and a consumer that roots elsewhere
   reports false violations — an upstream gap, not a yf defect.
2. **Do NOT add a marker file to yf bundles.** A unilateral extension to a format whose selling point
   is "no required tooling", that no consumer would look for.
3. **Pin the CONTENT, not the label** — `okf_baseline_sha256` of the vendored body as the authority,
   with source URL, upstream's `"0.2"` label (a mutable name, not a pin) and the commit sha as
   provenance. A hash is verifiable **offline** from the bundle alone, and moves only when SPEC.md's
   bytes move; a commit sha goes stale on unrelated repo commits and would produce false drift.
4. **Detection under D-6:** a `curl` + `sha256sum` comparison as a **FULL-tier** `CHANGE-VALIDATION`
   row, INCONCLUSIVE on network failure so an offline land is not blocked. It files nothing and
   proposes only that a human diff the copy. A label-only pin would have detected **nothing**; a
   content hash would have fired on 2026-08-21.
5. **Do not carry forward any claim that the corpus passes B1/B2 from this run** — 1285 of 1383
   concepts were never inspected. That assurance must come from `okf.py check`.
6. **Two incidental beads:** the 21-at-`0.1` / 11-at-`0.2` split between corpus and producer; and the
   `log.md` ghost bug, which is **okf-lint's**, noted not filed (D-6).
