---
type: Research Artifact
description: Source register for yf-research 005 — 228 sources (205 local corpus artifacts
  scored on the local evidence-strength rubric, 23 web sources with adjudicated credibility
  tiers). Generated mechanically from sources.json; every Summary.md citation anchors here.
okf_spec: OKF-RESEARCH
---

# Sources — 005 thrash detection and operator judgement

Generated from `sources.json` (228 entries). Local sources (100–545) carry an
`evidence_strength` band from the local-corpus rubric in `artifacts/triangulation.md` §1.2
(STRONG >= 80 · MODERATE 65–79 · WEAK 50–64 · INDICATIVE < 50). Web sources (601–623) carry
the adjudicated credibility tier from §1.3, which supersedes the mechanical scorer output.

## 100

- **Title:** 004's residue boundary, the rival-explanation mandate, and the cross-domain strength rule
- **Cluster:** review-pass-recurrence · **Type:** research-plan
- **Repo:** yoshiko-flow
- **Locator:** `docs/research/005-thrash-detection-and-operator-judgement/plan.yaml:method_notes`
- **Evidence strength:** **WEAK** (total 57 = directness 12 + reproducibility 18 + verification 12 + n/scope 15) — a statement of this study's own method, not an observation of the corpus
- **Retrieved:** 2026-08-28

> 004 is the direct predecessor and its boundary is the starting constraint: it found that plan bundles record ARTIFACTS, not live session behavior — thrashing happens in a session and leaves only indirect residue. 005 must reason from residue (recurring findings, bead reopens, revision oscillation) and say so, not pretend to observe the loop directly. ... Assign the red-team pass explicitly to the RIVAL explanations: task difficulty, missing tool/permission, context exhaustion, genuine underdetermination in the domain. A signal that cannot distinguish these is not a signal. ... yoshiko-flow is self-referential (the skill fixing itself). A pattern also present in writing/ or emacs.d — non-software, low-ceremony domains — is materially stronger.

## 101

- **Title:** Repo distribution of the 79 multi-pass bundles and the 40 recurrence matches
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `uv run scripts/finding_recurrence.py --census census.json --threshold 0.20 --id-floor 0.15 --json | aggregate: multipass bundles and recurrence-firing bundles per repo`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> repo -> multipass bundles, bundles-with-recurrence, total matches yoshiko-flow 42 11 26 d3-pxe 18 5 11 pybridge 7 0 0 writing 5 2 2 evri_py 4 1 1 rc-files 3 0 0

## 102

- **Title:** Measured review-pass format variance, the worktree double-count correction, the ~700-row validation defect, the letter-paragraph parse gap, and the self-reported-signal claim
- **Cluster:** review-pass-recurrence · **Type:** research-artifact
- **Repo:** yoshiko-flow
- **Locator:** `docs/research/005-thrash-detection-and-operator-judgement/artifacts/tooling-notes.md`
- **Evidence strength:** **WEAK** (total 57 = directness 12 + reproducibility 18 + verification 12 + n/scope 15) — a statement of this study's own method/tooling, not an observation of the corpus
- **Retrieved:** 2026-08-28

> An early fixed-position implementation mistook the Severity column for the finding text on ~700 rows before this was caught ... `yoshiko-flow`, `d3-pxe`, and `evri_py` each keep a `.worktrees/<branch>/` directory ... that MIRRORS the entire `docs/plans/` ... | bundles | 127 | **114** | | review passes | 391 | **301** | ... This shape is a KNOWN, DOCUMENTED GAP in `finding_recurrence.py` as shipped ... **51 self-reported cross-pass signals** ... This is the highest-confidence recurrence signal in the corpus because a human reviewer already did the cross-pass comparison; it should be weighted above the text-similarity matches in any downstream synthesis.

## 103

- **Title:** Corrected corpus census: 114 bundles / 301 review passes, and the per-bundle pass-count distribution
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `uv run scripts/corpus_scan.py --json`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> {"repo_count": 7, "repo_count_ok": 7, "repos_missing_or_broken": [], "total_bundles": 114, "total_review_passes": 301} pass-count -> bundles: 0:5 1:30 2:37 3:15 4:8 5:9 6:3 7:4 8:2 13:1 repo | bundles | passes: yoshiko-flow 56/166 | d3-pxe 19/73 | evri_py 9/13 | writing 11/18 | pybridge 11/20 | emacs.d 4/4 | rc-files 4/7

## 104

- **Title:** Severity-field availability and verdict vocabulary across the parsed corpus
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `uv run scripts/finding_recurrence.py --census census.json --threshold 0.20 --json | aggregate: severity and verdict tallies over all 1509 extracted findings`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> severity availability: total findings 1509 low 450 / medium 379 / high 265 / NONE 185 / med 147 / — 14 / medium-low 11 / low-medium 5 / medium-high 5 / low-med 3 / high, blocki 3 / gap 3 / low (new) 3 / med-low 3 / missing 2 verdicts: {'REVISE': 186, 'APPROVE': 83, None: 2}

## 105

- **Title:** Threshold sweep: recurrence matches fall 40 -> 3 with no plateau; weak-id-reuse and self-reported counts are threshold-invariant
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `for t in 0.20 0.25 0.30 0.35 0.45 0.55 0.70; do uv run scripts/finding_recurrence.py --census census.json --threshold $t --id-floor 0.15 --json; done`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> 0.20 {"bundles_processed": 79, "total_findings_extracted": 1509, "total_parse_warnings": 85, "total_recurrence_matches": 40, "total_weak_id_reuse_matches": 252, "total_self_reported_signals": 51} 0.25 ... 23 ... 252 ... 51 0.30 ... 12 ... 252 ... 51 0.35 ... 8 ... 252 ... 51 0.45 ... 4 ... 252 ... 51 0.55 ... 4 ... 252 ... 51 0.70 ... 3 ... 252 ... 51

## 106

- **Title:** E01 later side — the pass-4 concern is explicitly cosmetic and non-blocking
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-029-james-dixson-75fd34/reviews/pass-4.md:30-36`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> None blocking. One low-severity cosmetic note: 1. **Composition gate Test cites `yf-okf check` on a fixture bundle; Instructions run the Issue 1.3 test suite.** severity: low **Recommendation:** at execution, ensure the `yf-okf check` fixture bundle and the Issue 1.3 synthetic fixture are the same artifact so gate and unit test prove against one fixture. Cosmetic; does not block approval.

## 107

- **Title:** E01 earlier side — the pass-3 concern is medium severity
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-029-james-dixson-75fd34/reviews/pass-3.md:37-41`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> 2. **Resolver/composition only proven end-to-end at Issue 5.2 (last issue); no unit test/gate before Epics 2-4 build on it.** severity: medium Issue 1.3's tests are "against REQ-OKF-*" but no real `OKF-EXTENSION.md` exists at 1.3.

## 108

- **Title:** E02/E03 later side — the matched text is a RESOLUTION-CONFIRMATION block, not a concern
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-034-james-dixson-ac6633/reviews/pass-2.md:10-19`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ## Verdict: APPROVE Re-review after the pass-1 REVISE concerns (C1–C5) were addressed. All five confirmed resolved and grounded in shipped code. ## C1–C5 resolution confirmation - **C1 (single-file scope) — RESOLVED.** Budget check scoped to global `~/.codex/AGENTS.md`; single-file limitation documented in REQ-YF-TUNE-027 + warning text.

## 109

- **Title:** E04 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-039-james-dixson-150f79/reviews/pass-2.md:217`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | H1 | `\brelease` matches inside `ci-release`; SC6 falsified | high | Confirmed independently. The operator-chosen term-of-art guard was **measured and did not work**

## 110

- **Title:** E04 later side — explicit 'again'
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:138`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C1 | SC6 falsified again; 3.4b's `5→1` is `5→3` | high |

## 111

- **Title:** E05/E06 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-039-james-dixson-150f79/reviews/pass-2.md:223`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | M3 | EXP-001 figures drifted; plan-039 was not in the measured corpus | medium |

## 112

- **Title:** E05/E07 middle of the chain
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:140`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C3 | `exp-001` still carries superseded figures | medium |

## 113

- **Title:** E06/E07 later side — same object, third pass
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-039-james-dixson-150f79/reviews/pass-4.md:121`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | P3 | `exp-001` Implications still stale | low |

## 114

- **Title:** E08 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-040-james-dixson-1cabe4/reviews/pass-1.md:153`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C1 | Wrong guardrail (GR-BUP-002 vs 001) | high | Verified at source: `SPEC.md:269` GR-BUP-001 = never-bare-sync (REQ-BUP-030) ... | resolved |

## 115

- **Title:** E08 later side — partial landing
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-040-james-dixson-1cabe4/reviews/pass-2.md:112`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | D1 | Issue 2.3 still names GR-BUP-002 | high | Corrected to **GR-BUP-001 / REQ-BUP-030**

## 116

- **Title:** E09 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-047-james-dixson-dec9ff/reviews/pass-1.md:56`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | L3 | low | `SKILL.md:395-412` is the wrong slice; the block runs 365–420 and D-7's argument turns on the excluded header region | Correct the citation |

## 117

- **Title:** E09 later side — same citation still wrong three passes later
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-047-james-dixson-dec9ff/reviews/pass-4.md:58`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | P5 | low | `plan.md:26` cited `SKILL.md:395-412` while D-7/Issue 0.1 cite `365-420` for the same artifact; the fenced block is 365–421 | resolved |

## 118

- **Title:** E10 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-047-james-dixson-dec9ff/reviews/pass-2.md:43`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | N9 | medium | **SC20's verification depends on artifacts no issue produces.** No issue creates the seeded bad instances, so an executor satisfies it by assertion. Count wrong three ways: says 10, lists 8, Epic 6 has 11 |

## 119

- **Title:** E10 later / E12 earlier — explicit 'again'
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-047-james-dixson-dec9ff/reviews/pass-3.md:38`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | M4 | med | **SC20's count wrong three ways again**: text said 10, `Discharged-by` listed 9, Epic 6 has 11, schema-bearing types are 8 | resolved — "8 schema-bearing types (6.1–6.8)" |

## 120

- **Title:** E11 later side — the fix-induced-defect class, named by the reviewer
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-047-james-dixson-dec9ff/reviews/pass-4.md:54`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | P1 | med | **"six new ids" vs "seven"**, seven lines apart inside Issue 0.9. An executor obeying the second greps six of seven, leaving one unverified — inside the sweep installed to prevent the `REQ-DATA-020`–`023` collision. **Fourth consecutive cycle of a stale count surviving inside its own fix** | resolved

## 121

- **Title:** E12 later side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-047-james-dixson-dec9ff/reviews/pass-4.md:55`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | P2 | med | **SC20 still said "10 Epic-6 issues"** — wrong three ways again | resolved — "8 schema-bearing types (Issues 6.1–6.8)" |

## 122

- **Title:** E13 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-1.md:26`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C1 | high | Two capability gates are formal cycles: "relational checks can fail" blocks 3.5 but its evidence *is* 3.5; "intake binding does not wedge" blocks 5.3 but its condition presumes 5.3's binding |

## 123

- **Title:** E13 later side — the one instance where the fix made it strictly worse
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-2.md:47`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | N1 | high | `relational checks can fail` **still a cycle, made explicit** — `Blocks: 3.2, 3.3` while its condition draws evidence "from the rules from 3.2/3.3". Pass-1 moved it *onto* the producers of its own evidence — strictly worse |

## 124

- **Title:** E14 earlier side — shared premise, different defect
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-1.md:32`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C7 | high | Nothing orders 0.6 before the gates whose scripts it authors. `plan_manager.py` has **no auto-gate runner**, so a missing script yields bash 127 read by an agent as a red gate |

## 125

- **Title:** E14 later side — the shared premise restated under a different claim
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-2.md:48`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | N2 | high | **SC10d asserts an outcome no artifact can produce** — a deleted script returns 127 *from bash*; nothing maps 127→2, and `plan_manager.py` has no gate runner. Also SC10c uses bare `scripts/` which collides with the real top-level `scripts/` |

## 126

- **Title:** E15 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-2.md:54`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | N7 | med | **"declared target" has no producer** — gate-grammar, 1.5, SC1 and SC20 all consume it; 1.4b never declares one. The executor sets the bar after seeing the measurement |

## 127

- **Title:** E15 later side — unresolved
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-3.md:32`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | H2 | high | **The declared target is still declared after the measurement.** 1.4b `depends-on: 1.3`, and **no number appears anywhere in plan.md**. SC20 still cannot fail |

## 128

- **Title:** E16 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-4.md:52`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | L4 | low | SC1's `git diff --stat docs/plans` empty will be dirtied by plan-048's own bookkeeping |

## 129

- **Title:** E16 later side — a NEW defect at the same site, created by the repair
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-6.md:35`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | M5 | med | **SC1's verification exits 128** — `git diff --stat docs/plans -- ':!…'` parses the path as a revision. Correct form puts everything after `--` |

## 130

- **Title:** E17 earlier side — two defects named in one finding
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-6.md:33`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | M3 | med | `744` landed in plan.md but not in `findings/exp-002` (still `~700`) — the citation was corrected and the source was not, which is backwards under D-5. The plan.md cell is also malformed nested emphasis |

## 131

- **Title:** E17 later side — only one of the two was fixed
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-7.md:57`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C4 | low | plan.md's 744 cell still has overlapping emphasis (the linter has no rule for it) |

## 132

- **Title:** E18 later side — self-reported false resolution
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-049-james-dixson-725bc0/reviews/pass-2.md:44`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | D8 | low | **C15's claimed resolution did not land** — no mention of the `index.md`/`log.md` `files_checked: 0` vacuity anywhere in plan.md |

## 133

- **Title:** E19 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/reviews/pass-3.md:46`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C18 | low | The Objective cites **"0 of 53"** as a bare local measurement, contra D-5, R4 and EXP-004's own warning; the local figure is **26**. Separately the title and Objective still say "**six** … #177–#182" after D-6 dropped #177, while `index.md` says "five … #178-#182" |

## 134

- **Title:** E19 later side — the only genuine oscillation found (six -> five -> six)
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/reviews/pass-4.md:48`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C30 | medium | **Six defects are fixed; the title, Objective and index say five.** C18 changed them to "five … #178-#182", then #184 was added as a sixth `include` with its own issues. D-1 still says "the **six** … (#177–#182)" — a set that includes the dropped #177 and excludes #184 |

## 135

- **Title:** E20 earlier side — a site-scoped FINDING
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/reviews/pass-4.md:47`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C29 | medium | **#184 is in plan.md and `references/` but has no `upstream-triage.md` entry**, while **#183 is triaged with a blank disposition and appears in no plan.md row**. `index.md` calls triage "the record behind plan.md's Upstream Issues table" |

## 136

- **Title:** E20 later side — the reviewer names the prior pass's narrowness
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/reviews/pass-5.md:88`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C49 | medium | PRE-EXISTING | **`upstream-triage.md` is 47/49 blank.** Every one of the twelve rows the plan acts on has an empty `**Disposition:**`, while `index.md` calls the file "the triage record behind plan.md's Upstream Issues table". Pass 4's C29 flagged #183's blank and missed that the whole document is blank — a spotli[ght]

## 137

- **Title:** E21 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-1.md:37`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C5 | **high** | **D-8's live-site argument is REFUTED, and Issue 0.2 is scoped to one file.** Measured: roots = **12 live sites in 5 files**; stamp = **5 in 4**.

## 138

- **Title:** E21 later side — a genuinely new defect in the same area
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-4.md:48`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C49 | medium | **Two of 0.2's six files carry BOTH meanings of `REQ-PLAN-073`** — `SPEC.md` (roots at :239/:919, stamp at :349) and `plan_manager.py` (roots ×3, stamp at :1461). A file-scoped rename corrupts the stamp citations.

## 139

- **Title:** E22 earlier side — names TWO surfaces
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-3.md:53`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C40 | low | D-13 and R7 cite "0 of **41**"; measured now **0 of 46** — a moving-fact literal, the shape SC12b was rewritten to avoid |

## 140

- **Title:** E22 later side — canonical partial landing
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-4.md:49`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C50 | low | R7 still carries "0-of-41"; measured 0 of 46. C40 named D-13 *and* R7; only D-13 was fixed |

## 141

- **Title:** E23 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-054-james-dixson-535968/reviews/pass-1.md:32`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C4 | high | **`verify-reconcile` will fail deterministically.** `partial` requires end-state OPEN, `include` requires CLOSED-with-attribution. #119 is `partial` while 6.2 is titled "Close #119". #154 is absent from the table entirely despite EXP-006 directing a rescope.

## 142

- **Title:** E23 later side — same defect, now executed rather than predicted
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-054-james-dixson-535968/reviews/pass-2.md:40`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C27 | high | **SC19 is unsatisfiable, measured by running it** — `verify-reconcile` → `fail`, 15 of 23 rows. Three are structural: **#154 typed `deferred` while CLOSED upstream** (deferred demands OPEN — no execution can fix it); **#119 table says `include` but Issue 6.2 declares `partial`**

## 143

- **Title:** E24 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-054-james-dixson-535968/reviews/pass-5.md:42`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | N2 | high | **The `check-*.sh` baseline has no verifying verb and no criterion.** `verify-red-all` iterates `controls.txt`, whose set is derived with the `ctl-` pattern; a `check-*.sh` **can never match**, and 0.6 explicitly keeps `assets/checks/` outside it.

## 144

- **Title:** E24 later side — the reviewer explicitly types it as the same class one layer down
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-054-james-dixson-535968/reviews/pass-6.md:42`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | P1 | med | **The 28 `check-*.sh` red baseline has a verifier but no RECORDER.** Measured at source: `cmd_record_red` gates on `_in_manifest`, a `grep -qxF` against `controls.txt`, whose set is derived with the `ctl-` pattern — so `record-red` on a `check-*.sh` **hard-fails and writes nothing**. N2's class one [layer down]

## 145

- **Title:** E25 later side — the match is a VERIFICATION HEADING, not a concern
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-055-james-dixson-5f1c40/reviews/pass-7.md:25`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ### C1 recomputed independently — own parser, own regex, own closure

## 146

- **Title:** E26 later side — explicit false resolution
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-055-james-dixson-5f1c40/reviews/pass-7.md:63`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | P2 | low | **C3 was recorded resolved and is not fixed.** 0.4 still ends `"…governed by nothing: a per-row surface-dir override var and a three-valued precedence…"` — the clause after the colon is verbatim the pre-edit surface-column description, grafted where it does not parse.

## 147

- **Title:** E27 earlier side — Issue 5.1
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/reviews/pass-1.md:46`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C9 | MEDIUM | Issue 5.1 has no `depends-on`, breaking the negative test |

## 148

- **Title:** E27 later / E28 earlier — a DIFFERENT issue (2.3), same defect class
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/reviews/pass-2.md:59`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | D13 | LOW | Issue 2.3 has no `depends-on` and no ordering relative to the first restic run |

## 149

- **Title:** E28 later — a third different issue (6.1)
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/reviews/pass-3.md:59`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | E15 | LOW | Issue 6.1 has no `depends-on`; no ordering vs. the work whose limitations it records |

## 150

- **Title:** E29 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/reviews/pass-3.md:54`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | E10 | MEDIUM | Issue 4.2/SC1 reverse exp-001 on `--monitor-snapshots` without revisiting its config |

## 151

- **Title:** E29 later side — same SC1 and subcommand, a different claim
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/reviews/pass-4.md:49`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | F6 | MEDIUM | SC1 pins an unmeasured output shape for `sanoid --monitor-snapshots` |

## 152

- **Title:** E30 earlier side — a RESOLVED row, id C1
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-018-james-dixson-0b2d16/reviews/pass-3.md:140`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C1 | 0.5 blocks with no gate | **RESOLVED** | New conditional gate; blocks 1.1 only; acyclic; Epic 0 completes. |

## 153

- **Title:** E30/E31 later side — id C1 reused for an unrelated concern, also RESOLVED
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-018-james-dixson-0b2d16/reviews/pass-5.md:127`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C1 | Env precondition on the gate | **RESOLVED** | Preamble verified clause-by-clause. Ungated-template / gated-assert claim exactly right. 6.11 files it. |

## 154

- **Title:** E31 earlier side — a three-word headline sharing only the token 'gate'
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-018-james-dixson-0b2d16/reviews/pass-3.md:142`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C3 | Reload gate Test | **RESOLVED** | Retitled `Human Gate`; conformant and consistent with the Start Gate. |

## 155

- **Title:** E32 later side — canonical partial landing, self-reported
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-018-james-dixson-0b2d16/reviews/pass-5.md:65-66`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ### D1 (medium) Pass-4 C6 named **two** surfaces — Issue 0.5 **and the gate**. Only 0.5 was re-pointed. `plan.md:437`, the gate's Condition, still read `§363-364`, which is **PVE-STO-005 restic-repository-password prose**.

## 156

- **Title:** E33 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/ansible/plans/plan-002-james-dixson-06dce8/reviews/pass-1.md:31`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C7 | low | Citation/state nits: `pve_lxc` cites PVE-GPU-003 (that's the host boot-order unit, owned by `pve_host`); guest block is GPU-005/006. Issue 4.3 should pin `apt state=present` not `latest`.

## 157

- **Title:** E33 later side — the reviewer types it 'Residual'
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/ansible/plans/plan-002-james-dixson-06dce8/reviews/pass-2.md:24`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | N2 | low | Residual C7: the Approach `pve_lxc` bullet still cites `PVE-GPU-003/005/006` (GPU-003 is the host boot-order unit, owned by `pve_host`). Issue 3.3 + Success Criteria already dropped it.

## 158

- **Title:** E34 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-2.md:73`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | **N7** | low | **The traces auto-gate had no executable test** — prose where every other gate gives a command.

## 159

- **Title:** E34 later side — the supplied command is itself wrong; prose->command is progress
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-3.md:57`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | **L2** | low | Traces-gate prose said loopback, command used the LAN — shipping root Basic-auth creds across the network.

## 160

- **Title:** E35 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-2.md:74`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | **N8** | low | **`index.md` still advertised the skills gateway and a dedicated CT 107**, both reversed by S9 and D1; `log.md` had no pass-1 `review:` line.

## 161

- **Title:** E35 later side — near-verbatim, unresolved between passes
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-3.md:56`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | **L1** | low | `index.md` still advertised the dropped skills gateway and CT 107.

## 162

- **Title:** E36 earlier side
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/postgres/plans/plan-015-james-dixson-87ecab/reviews/pass-2.md:65`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ### N2 (HIGH) — the snapshot does not capture what R1b blames

## 163

- **Title:** E36 later side — same R1b failure mode, restated at HIGH after a fix attempt
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/postgres/plans/plan-015-james-dixson-87ecab/reviews/pass-3.md:78`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ### H3 (HIGH) — the config copy cannot roll anything back

## 164

- **Title:** E37 earlier side — the 'finding' is a stub section header, a parse artifact
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/postgres/plans/plan-015-james-dixson-87ecab/reviews/pass-2.md:79`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ### N3–N12

## 165

- **Title:** E38 later side — the fix cut one edge but the blocking path survives
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** evri_py
- **Locator:** `docs/plans/plan-008-james-dixson-d1f1e4/reviews/pass-3.md:28`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | NC5 | medium | The Reconcile Gate is `auto (all execution beads closed)` and blocks `4.2, 4.3`. "All execution beads" includes `3.2` (Windows clean-load), which the App Control gate can block indefinitely. So even though NC2 cut the `4.2→3.2` edge, `4.2` still can't fire until the reconcile gate opens

## 166

- **Title:** E39 earlier side — a three-word headline
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** writing
- **Locator:** `docs/plans/plan-002-james-dixson-62a38d/reviews/pass-1.md:91`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C4 | Multipart undecomposed | medium | Multipart Pelican publishing scoped OUT of v1 (generation stays multipart-aware); noted in plan | resolved |

## 167

- **Title:** E39 later side — different subject, one shared word
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** writing
- **Locator:** `docs/plans/plan-002-james-dixson-62a38d/reviews/pass-2.md:93`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | M6 | cover/hero mechanism undecomposed | — | 4.2 decomposes cover as a distinct draft attribute vs inline stream | resolved |

## 168

- **Title:** E40 earlier side — medium, operator decision surfaced
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** writing
- **Locator:** `docs/plans/plan-010-james-dixson-e049e3/reviews/pass-1.md:79`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C4 | No READY gate on `[needs-source]` | medium | **Operator decision surfaced** (block vs advisory); plan v2 adds the symmetric READY precondition per the operator's choice. | resolved (pending operator choice) |

## 169

- **Title:** E40 later side — the corpus's HIGHEST similarity match (0.600) and it is convergence: medium -> low, resolved
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** writing
- **Locator:** `docs/plans/plan-010-james-dixson-e049e3/reviews/pass-2.md:64`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C11 | `[needs-source]` gate recall | low | Issue 3.3 gains the coverage note: guarantee is "no flagged unresolved claim," and READY also requires ≥1 web-enabled footnoter pass to have run (no vacuous pass). | resolved |

## 170

- **Title:** The 8 episodes at the tool's documented operating point: 3 are id_reuse-basis (all FALSE on hand-audit), 1 is productive deepening
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `uv run scripts/finding_recurrence.py --census census.json --threshold 0.35 --id-floor 0.15 --json`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> plan-034-james-dixson-ac6633 p1->p2 sim=0.163 id_reuse plan-047-james-dixson-dec9ff p3->p4 sim=0.353 text_similarity plan-050-james-dixson-d0414b p4->p5 sim=0.359 text_similarity plan-055-james-dixson-5f1c40 p6->p7 sim=0.156 id_reuse plan-018-james-dixson-0b2d16 p3->p5 sim=0.250 id_reuse plan-002-james-dixson-06dce8 p1->p2 sim=0.419 text_similarity plan-010-james-dixson-49050b p2->p3 sim=0.438 text_similarity plan-010-james-dixson-e049e3 p1->p2 sim=0.600 text_similarity

## 171

- **Title:** All 51 self-reported cross-pass signals; 47 are clean all-resolved statements, 4 carry an actual failure rate (all plan-053)
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `uv run scripts/finding_recurrence.py --census census.json --threshold 0.20 --json | enumerate all 51 self_reported_signals`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> S01 plan-012 ... "All eight concerns resolved in `plan." S03 plan-026 pass-5 ... "All five pass-4 concerns are genuinely resolved and verified." S04 plan-028 pass-2 ... "All four pass-1 concerns verified genuinely and correctly resolved against the real repo." S17 plan-053 pass-2 ... "## Reproduction of pass-1's 14 resolutions" S18 plan-053 pass-3 ... "## Reproduction of pass-2's 15 resolutions" S19 plan-053 pass-4 ... "## Reproduction of pass-3's 14 resolutions — 7 of 14 (50%)" S20 plan-053 pass-5 ... "## Reproduction of pass-4's 10 resolutions — 9 of 10 (90%)" S50 rc-files plan-004 pass-1 ... "**Status: all 16 concerns resolved." TOTAL 51

## 172

- **Title:** A clean all-resolved self-report — a CONVERGENCE signal, counted by the tool as a recurrence signal
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-012-james-dixson-a99822/reviews/pass-2.md:37`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> All eight concerns resolved in `plan.md`; ready for operator approval → INTAKE.

## 173

- **Title:** A clean all-resolved self-report
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-028-james-dixson-a9738b/reviews/pass-2.md:9`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> All four pass-1 concerns verified genuinely and correctly resolved against the real repo.

## 174

- **Title:** A clean all-resolved self-report in a NON-SOFTWARE repo
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** rc-files
- **Locator:** `docs/plans/plan-004-james-dixson-f0bcc5/reviews/pass-1.md:9`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> **Status: all 16 concerns resolved.** C5 was routed to the operator (it reversed a scoping

## 175

- **Title:** A clean all-resolved self-report with quoted evidence
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** pybridge
- **Locator:** `docs/plans/plan-002-james-dixson-f111ab/reviews/pass-2.md:8`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> All 10 pass-1 concerns verified addressed in revised plan with quoted text.

## 176

- **Title:** D2 at pass 2 — the reproduction rate, and the partial-landing class named (RE-002)
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-2.md:14-24`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ## Reproduction of pass-1's 14 resolutions | Class | Count | Concerns | | :-- | --: | :-- | | **(a) landed and correct** | **9** | C2, C6, C7, C8, C9, C11, C12, C13, C14 | | **(b) recorded but absent** | **1** | C10 | | **(c) landed at one site, defect survives elsewhere** | **4** | C1, C3, C4, C5 | **9 of 14.** All four (c)-class failures are **RE-002's shape** — a global property repaired at the one site the reviewer named.

## 177

- **Title:** D2 at pass 3 — the rate falls, and the reviewer says so
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-3.md:12-24`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ## Reproduction of pass-2's 15 resolutions | (a) landed and correct | **9** | C16, C19, C20, C22, C24, C25, C26, C28, C29 | | (b) recorded but absent | 0 | — | | (c) landed at one site, defect survives elsewhere | **5** | C15, C17, C18, C21, C27 | | (d) itself a new defect | **1** | C23 | **9 of 15 (60%), against pass 2's 9 of 14 (64%) — this round did slightly WORSE.** And the shape is unchanged: every (c)-class failure is RE-002. **Three of the five were re-broken by pass-2's own remedies**

## 178

- **Title:** D2 at pass 4 — three-point falling trend and the named mechanism
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-4.md:15-27`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ## Reproduction of pass-3's 14 resolutions — 7 of 14 (50%) | (a) landed and correct | **7** | C30, C34, C35, C37, C39, C41, C43 | | (c) landed at one site, defect survives | **4** | C31, C32, C33, C40 | | (d) itself a new defect | **3** | C36, C38, C42 | **64% → 60% → 50%. The rate did not improve; it fell by the largest margin yet.** > **The reason is measurable, and it is the finding of the pass: pass-3's structural remedy was > ITSELF applied site-by-site.**

## 179

- **Title:** D2 at pass 5 — the rate recovers when the METHOD changes
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-5.md:23-31`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> ## Reproduction of pass-4's 10 resolutions — 9 of 10 (90%) | (a) landed and correct | **9** | C44, C45, C46, C47, C48, C49, C50, C52, C53 | | (c) landed at one site, defect survives | **1** | C51 | **64% → 60% → 50% → 90%. The method change is real and it worked.**

## 180

- **Title:** Discriminator cross-tab and per-bundle findings/HIGH/verdict trajectories
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `uv run scripts/finding_recurrence.py --census census.json --threshold 0.20 --json | cross-tab discriminators over the 37 bundles with >=3 passes and >=1 parsed finding`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> bundle rec np findings/pass HIGH/pass verdicts plan-048-james-dixson-ed68a5 5 7 12,12,14,10,8,9,8 7,6,4,1,2,0,0 REV*6,APP plan-054-james-dixson-535968 2 6 22,14,8,9,8,6 8,6,4,2,2,0 REV*5,APP plan-055-james-dixson-5f1c40 2 7 12,17,12,13,5,3,6 5,8,2,1,1,1,0 REV*6,APP plan-017-james-dixson-feb918 0 4 19,19,11,10 4,2,1,0 REV,REV,REV,APP plan-042-james-dixson-98631b 0 3 12,12,4 4,2,0 REV,REV,APP plan-041-james-dixson-a9d837 0 3 14,9,4 3,0,0 REV,REV,APP plan-043-james-dixson-a8afe8 0 4 15,6,4,0 4,1,0,0 REV,REV,REV,APP plan-004-james-dixson-f0bcc5 0 3 16,16,11 4,6,0 REV,REV,APP plan-050-james-dixson-d0414b 2 13 5,4,11,17,14,0,0,0,0,0,0,0,0 ... HIGH at pass>=3 recurrence: 10/17 (59%) control: 3/20 (15%) HIGH at pass>=2 recurrence: 12/17 (71%) control: 8/20 (40%) findings nonincreasing recurrence: 5/17 (29%) control: 12/20 (60%) p2 >= p1 findings recurrence: 6/17 (35%) control: 8/20 (40%)

## 181

- **Title:** Control-group pass digests — plan-026's re-scoping oscillation with entirely different concerns each round
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `uv run scripts/finding_recurrence.py --census census.json --threshold 0.20 --json | per-pass finding digests for 12 control bundles`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> plan-026-james-dixson-6e0e2f (7 passes, 0 recurrence matches) PASS 1 verdict=REVISE findings=6 [C1|medium] Epic 4 premise factually wrong for md2pdf: it **already** has `check_deps()` PASS 2 verdict=APPROVE findings=2 PASS 3 verdict=APPROVE findings=3 PASS 4 verdict=REVISE findings=5 [C1|medium] #85 reverses GR-MDLINT-001; Issue 1.1 doesn't amend it PASS 5 verdict=APPROVE findings=1 PASS 6 verdict=REVISE findings=5 PASS 7 verdict=APPROVE findings=1

## 182

- **Title:** Approve-then-revise reversal and non-increasing finding counts, recurrence-fired vs control
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `uv run scripts/finding_recurrence.py --census census.json --threshold 0.20 --json | verdict-reversal and finding-monotonicity over all 79 multi-pass bundles`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> recurrence-fired n=19 meanpasses=5.26 approve-reversal=4(21%) noninc-findings=7(37%) no-recurrence n=60 meanpasses=2.85 approve-reversal=4(7%) noninc-findings=50(83%)

## 183

- **Title:** D1 — the explicit cross-pass back-reference signal: 54 instances, 16 bundles, 39% at pass 2, present in 5 of 7 repos
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `python: for each multipass bundle, flag findings in pass N whose text names a finding id first introduced in an earlier pass AND matches /still|again|not land|did not|residual|unresolved|survives|not fixed|nothing changed|re-brok|recur|NOT LANDED|missed|incomplete/i`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> back-reference-with-failure-word signals: 54 across 16 bundles (of 79 multipass) by pass in which the back-ref appears: {2: 21, 3: 12, 4: 11, 5: 5, 6: 2, 7: 2, 8: 1} bundles: backref&tool=9 backref-only=7 tool-only=10 plan-041 3 | plan-042 5 | plan-043 1 | plan-049 4 | plan-050 6 | plan-053 9 | plan-054 4 | plan-055 6 plan-016(d3-pxe) 3 | plan-017(d3-pxe) 5 | plan-019(d3-pxe) 1 | plan-002(ansible) 1 | plan-010(litellm) 1 plan-008(evri_py) 1 | plan-010(pybridge) 1 | plan-004(rc-files) 3

## 184

- **Title:** D1 instance at pass 2 — a resolution row asserting something the plan does not contain
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-041-james-dixson-a9d837/reviews/pass-2.md:50`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C18 | **M3's resolution did not land.** pass-1 marks it `resolved — falsifier recorded in the E2 block`, but `grep -rn "falsif"` across the bundle hits **only `reviews/pass-1.md`**. A resolution row asserting something the plan does not contain is the failure mode this cycle exists to catch. | low |

## 185

- **Title:** D1 instance at pass 2 — canonical partial landing
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-042-james-dixson-98631b/reviews/pass-2.md:45`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | H1 | **C4 landed in the Decisions table only.** Issues 3.1 and 3.6, the gate Condition, Scope, and `context.md` all still specified the superseded `permissions.*` predicate. D-C1 carried no superseded marker. | **high** |

## 186

- **Title:** D1 instance — the fix landed at one site and the criterion checked at close still carries the defect
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-043-james-dixson-a8afe8/reviews/pass-3.md:57`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | C23 | **C18's fix did not propagate to SC2 or D10.** Issue 0.3 required enumerating every invocation, but SC2 — *the criterion checked at close* — still specified the superseded capture-only key. An implementer building capture-only enumeration would **satisfy SC2 and D10 while violating Issue 0.3**, leaving R8 unmitigated by the exact mechanism C18 identified. | medium |

## 187

- **Title:** D1 instance in a NON-SOFTWARE repo at pass 2 — partial landing, plus a false attribution
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** rc-files
- **Locator:** `docs/plans/plan-004-james-dixson-f0bcc5/reviews/pass-2.md:38`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | N2 | **C5 was applied to plan.md and to nothing else. EXP-001 was not amended at all** — it still carries the Linux curl installer, `INSTALL_DIR="$HOME/cliproxyapi"`, `systemctl --user`, `55-vendor-tools.sh`, and a per-platform summary table. plan.md attributes to EXP-001 a conclusion **EXP-001 does not state**. | high |

## 188

- **Title:** Only 6 of 114 bundles contain any cross-pass reproduction/verification section — D2 is an instrument to install, not residue to mine
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `python: regex /Reproduction of pass-\d+|resolution verification|verified genuinely resolved/i over all 301 pass files from corpus_scan.py`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> pattern files bundles false-resolution (recorded resolved, not fixed) 6 6 Nth consecutive cycle/round 23 16 defect inside its own fix 14 9 explicit "again" 31 17 explicit "still" 169 62 reproduction/verification section 17 6

## 189

- **Title:** The task-difficulty rival: plan size explains most of the variance in review-pass count
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `python: Spearman rank correlation of review_pass_count vs len(plan.md) over the 109 bundles with >=1 pass and a readable plan.md, from corpus_scan.py --json`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> np n med plan.md bytes med commits %recurrence 1 30 16398 2 0% 2 37 19790 3 5% 3-4 23 35758 5 22% 5+ 19 62461 6 63% Spearman rho(review passes, plan.md size) = 0.739 (n=109)

## 190

- **Title:** D7's firing rate is very nearly a monotone function of review-text volume
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `python: recurrence-firing rate bucketed by total findings extracted per bundle, over the 79 multi-pass bundles`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> total-findings bucket -> bundles, %with recurrence 0 n=8 0 (0%) 1-20 n=48 6 (12%) 21-50 n=16 7 (44%) 51+ n=7 6 (86%) pass count -> bundles, %with recurrence 2 n=37 2 (5%) 3 n=15 3 (20%) 4 n=8 2 (25%) 5+ n=19 12 (63%)

## 191

- **Title:** The missing-tool rival appears as an ordinary re-raised finding, indistinguishable from a partial landing
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** d3-pxe
- **Locator:** `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-3.md:51`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | **H1** | high | **The `plan-011 complete` gate still could not execute.** `op` is not installed on the pve host and `pct` exists nowhere else, but the one-liner needed both in one shell — so `$(op read …)` expanded to empty. N2 in a new venue.

## 192

- **Title:** A defect missed by six prior passes — a REVIEWER miss, not evidence of agent context loss
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-055-james-dixson-5f1c40/reviews/pass-7.md:64`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> | P3 | low | **A second stranded fragment of C3's exact class, in 0.8**, missed by all six prior passes: `"…leaves behind. editing a completed plan's bundle…"` — lowercase start, no subject, the residue of a deleted lead-in. A grep for `\. [a-z]` returns exactly this one hit, so the class is **enumerated rather than sampled**

## 193

- **Title:** The domain-underdetermination rival, positively instanced — and indistinguishable in the residue from a partial landing
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-039-james-dixson-150f79/reviews/pass-3.md:138`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> **SC6 rewritten to assert stable properties** — `evidence: prose-only`, `confidence: low`, and every residual enumerated as genuine subject-matter prose in `references/sc6-residuals.md` — with the reason recorded that a count was asserted twice and falsified twice, because the measured document is the document being edited.

## 194

- **Title:** The 'defect inside its own fix' sub-signal is effectively a single-repo artifact: 11 of 14 files are yoshiko-flow, the rest one d3-pxe plan
- **Cluster:** review-pass-recurrence · **Type:** tool-output
- **Repo:** (analysis)
- **Locator:** `python: regex /inside (its own|the) fix|introduced (by|inside) (the|this) .{0,30}fix|created by (this|the) .{0,25}(edit|fix|round)|re-?brok/i over all 301 pass files`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> --- defect inside own fix files (14 files / 9 bundles) --- yoshiko-flow/plan-041/pass-2.md, plan-042/pass-2.md, plan-047/pass-2.md, plan-047/pass-3.md, plan-047/pass-4.md, plan-048/pass-6.md, plan-050/pass-4.md, plan-052/pass-4.md, plan-052/pass-5.md, plan-053/pass-3.md, plan-054/pass-3.md d3-pxe/plan-016/pass-2.md, plan-016/pass-3.md, plan-016/pass-4.md

## 195

- **Title:** A D1 false-positive shape — a POSITIVE verification written with a negation-adjacent word ('residual')
- **Cluster:** review-pass-recurrence · **Type:** review-pass
- **Repo:** pybridge
- **Locator:** `docs/plans/plan-010-james-dixson-06eefa/reviews/pass-2.md:18`
- **Evidence strength:** **MODERATE** (total 76 = directness 40 + reproducibility 12 + verification 20 + n/scope 4) — verbatim quote from a reviews/pass-N.md, hand-read in the recurrence cluster's 40-episode audit; single-instance
- **Retrieved:** 2026-08-28

> - C1 resolved (residual N3: MATLAB `.zip` staple claim repeats the container error).

## 200

- **Title:** corrected per-repo bundle census
- **Cluster:** herdr-repo-interrogation · **Type:** tool-output
- **Repo:** multi
- **Locator:** `scripts/corpus_scan.py --json (2026-08-28)`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> 114 bundles, 301 review passes, 7/7 repos scanned OK

## 201

- **Title:** per-repo recurrence-candidate distribution is concentrated in 2 repos
- **Cluster:** herdr-repo-interrogation · **Type:** tool-output
- **Repo:** multi
- **Locator:** `scripts/finding_recurrence.py --census census.json --threshold 0.35 --id-floor 0.15 --json`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> total_recurrence_matches: 8 (yoshiko-flow 4, d3-pxe 3, writing 1; evri_py 0, pybridge 0, rc-files 0, emacs.d 0 bundles-eligible-for-episodes)

## 202

- **Title:** emacs.d's only 3+-pass-eligible REVISE never got a pass-2 — the plan was parked, not re-reviewed
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** emacs.d
- **Locator:** `docs/plans/plan-001-james-dixson-30e722/reviews/pass-1.md:1-5 and plan.md phase log`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> 2026-06-19 drafting: v2: stdio-bridge transport (EXP-004) folded into plan body; parked pending re-review

## 203

- **Title:** emacs.d resolves a REVISE in-place inside pass-1 itself rather than issuing a pass-2 file
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** emacs.d
- **Locator:** `docs/plans/plan-003-james-dixson-667e0b/reviews/pass-1.md:tail (Operator Resolutions table)`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> after this review, the operator made a modality decision ... The plan was reframed ... Several concerns are resolved or superseded by that reframe

## 204

- **Title:** rc-files runs a full MEASURED adversarial review, same C##/table/Operator-Resolutions convention as yoshiko-flow
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** rc-files
- **Locator:** `docs/plans/plan-004-james-dixson-f0bcc5/reviews/pass-1.md:concerns table (C1-C16)`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> C4 | high | **MEASURED.** A *dangling* symlink is silently written **through**, into the repo. `install_renamed.rb:append_default_if_different` uses `dst.file?`, which follows symlinks

## 205

- **Title:** rc-files pass-2 raises a genuinely NEW concern introduced by fixing pass-1, not a re-raised one — convergence, not thrash
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** rc-files
- **Locator:** `docs/plans/plan-004-james-dixson-f0bcc5/reviews/pass-2.md:concerns table (N1) and resolutions`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> N1 | high | Risk renumbering left 12 of 14 in-prose `R<n>` references pointing at the wrong risk ... | resolved

## 206

- **Title:** writing's one recurrence episode (score 0.60, highest in the corpus) is a deepening, not a re-litigation: severity dropped medium->low and the second pass closes a coverage gap the first left explicitly pending
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** writing
- **Locator:** `docs/plans/plan-010-james-dixson-e049e3/reviews/pass-1.md:79 and pass-2.md:64`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> pass-1 C4: 'No READY gate on `[needs-source]`' ... resolved (pending operator choice); pass-2 C11: '`[needs-source]` gate recall' ... Issue 3.3 gains the coverage note: guarantee is "no flagged unresolved claim"

## 207

- **Title:** a bundle whose review file's own Verdict: field literally says REVISE is nonetheless Status: complete in plan.md, because the resolutions table inside that same pass-2 file marks every concern resolved without a formal pass-3 APPROVE file
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** writing
- **Locator:** `docs/plans/plan-002-james-dixson-62a38d/plan.md (phase log) and reviews/pass-2.md (resolutions table)`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> Final status: resolved — plan revised to v4. [plan.md] **Status:** complete

## 208

- **Title:** d3-pxe genuine residual-fix recurrence, self-flagged by the reviewer as a repeat of the earlier finding
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** d3-pxe
- **Locator:** `Incubator/ansible/plans/plan-002-james-dixson-06dce8/reviews/pass-2.md:24`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> Residual C7: the Approach `pve_lxc` bullet still cites `PVE-GPU-003/005/006` (GPU-003 is the host boot-order unit, owned by `pve_host`). Issue 3.3 + Success Criteria already dropped it.

## 209

- **Title:** second d3-pxe residual-doc-sync recurrence: a fix agreed in pass-2 was not actually applied and was caught again in pass-3
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** d3-pxe
- **Locator:** `Incubator/litellm/plans/plan-010-james-dixson-49050b/reviews/pass-3.md:56`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> `index.md` still advertised the dropped skills gateway and CT 107.

## 210

- **Title:** pybridge's self-reported cross-pass verification convention is identical to yoshiko-flow's and d3-pxe's
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** pybridge
- **Locator:** `docs/plans/plan-003-james-dixson-e55a84/reviews/pass-2.md:1-19`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> All ten pass-1 concerns (C1–C6, M1–M3, G1, U1) verified genuinely resolved in the current `plan.md` (item-by-item below); the revisions introduced no material new risk.

## 211

- **Title:** yoshiko-flow near-verbatim self-flagged recurrence — 'wrong three ways again' echoes pass-3's own wording
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-047-james-dixson-dec9ff/reviews/pass-4.md:55`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> **SC20 still said "10 Epic-6 issues"** — wrong three ways again

## 212

- **Title:** yoshiko-flow recurrence where the later pass explicitly names the earlier pass's finding as an incomplete spot-fix
- **Cluster:** herdr-repo-interrogation · **Type:** plan-bundle
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/reviews/pass-5.md:88`
- **Evidence strength:** **MODERATE** (total 79 = directness 40 + reproducibility 12 + verification 20 + n/scope 7) — hand-read bundle in the cross-repo cluster; single repo
- **Retrieved:** 2026-08-28

> Pass 4's C29 flagged #183's blank and missed that the whole document is blank — a spotli[ght fix, not a systemic one]

## 213

- **Title:** pass-count distributions per repo: 3+-pass rate is a repo-level property, not evenly spread
- **Cluster:** herdr-repo-interrogation · **Type:** tool-output
- **Repo:** multi
- **Locator:** `scripts/corpus_scan.py --json, per-repo pass-count histograms (derived)`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> yoshiko-flow 23/56 (41%) 3+pass; d3-pxe 13/19 (68%) 3+pass; evri_py 1/9 (11%); writing 2/11 (18%); pybridge 2/11 (18%); emacs.d 0/4 (0%); rc-files 1/4 (25%)

## 214

- **Title:** OKF full-bundle scaffolding (log.md/index.md) is concentrated in the two heaviest-ceremony repos and near-absent in low-ceremony ones
- **Cluster:** herdr-repo-interrogation · **Type:** tool-output
- **Repo:** multi
- **Locator:** `scripts/corpus_scan.py --json, has_log_md / has_index_md presence rates (derived)`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> has_log_md: yoshiko-flow 27/56, d3-pxe 14/19, rc-files 1/4, evri_py 1/9, pybridge 0/11, writing 0/11, emacs.d 0/4

## 215

- **Title:** self-reported cross-pass verification signal rate scales with 3+-pass rate, not with repo type — evidence the confound is ceremony-volume not domain
- **Cluster:** herdr-repo-interrogation · **Type:** tool-output
- **Repo:** multi
- **Locator:** `scripts/finding_recurrence.py, self_reported_signals per repo (derived)`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> self_reported_signals: yoshiko-flow 29, d3-pxe 15, pybridge 4, rc-files 2, writing 1, evri_py 0, emacs.d 0

## 216

- **Title:** per-repo bundle lifespan medians vary two orders of magnitude, uncorrelated with ceremony label
- **Cluster:** herdr-repo-interrogation · **Type:** tool-output
- **Repo:** multi
- **Locator:** `scripts/corpus_scan.py --json, bundle lifespan (git_first_commit_date to git_last_commit_date), median hours (derived)`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> median hrs: rc-files 103.5, pybridge 17.2, d3-pxe 11.0, yoshiko-flow 53.3, evri_py 1.5, writing 0.4, emacs.d 0.0

## 301

- **Title:** All 7 repos have a healthy, non-wedged bd config
- **Cluster:** execution-telemetry · **Type:** bead
- **Repo:** all 7
- **Locator:** `bd status --json (run in each of the 7 corpus repos)`
- **Evidence strength:** **STRONG** (total 82 = directness 40 + reproducibility 18 + verification 20 + n/scope 4) — bd/interactions.jsonl record; all 3 corpus reopens hand-audited
- **Retrieved:** 2026-08-28

> {"schema_version":1,"summary":{...,"blocked_issues":6,"closed_issues":1917,...,"open_issues":39,...,"total_issues":1962}} -- clean JSON, no 'error' key, in yoshiko-flow, d3-pxe, evri_py, writing, pybridge, emacs.d, rc-files

## 302

- **Title:** issues.jsonl and interactions.jsonl field vocabularies, measured directly
- **Cluster:** execution-telemetry · **Type:** file
- **Repo:** yoshiko-flow
- **Locator:** `python3 field-union scan over ~/workspace/dixson3/yoshiko-flow/.beads/issues.jsonl and .beads/interactions.jsonl`
- **Evidence strength:** **MODERATE** (total 74 = directness 40 + reproducibility 18 + verification 12 + n/scope 4) — verbatim file content, path-located
- **Retrieved:** 2026-08-28

> issues.jsonl keys: ['_type','assignee','await_type','close_reason','closed_at','comment_count','created_at','created_by','defer_until','dependencies','dependency_count','dependent_count','description','external_ref','id','issue_type','labels','metadata','mol_type','notes','owner','priority','started_at','status','title','updated_at']; interactions.jsonl keys: ['actor','created_at','extra','id','issue_id','kind'], every kind == 'field_change', every extra.field == 'status'

## 303

- **Title:** bd history returns 745 mostly-duplicate Dolt-commit entries for one bead
- **Cluster:** execution-telemetry · **Type:** bead
- **Repo:** yoshiko-flow
- **Locator:** `bd history yf-mol-bh8.2.11 (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **STRONG** (total 82 = directness 40 + reproducibility 18 + verification 20 + n/scope 4) — bd/interactions.jsonl record; all 3 corpus reopens hand-audited
- **Retrieved:** 2026-08-28

> 745 entries; status-token counts across all entries: 641 [P2 - closed], 103 [P2 - open], 1 [P2 - in_progress]; e.g. 'ki5ebma3 2026-08-28 14:50:05 ... [P2 - closed]' immediately followed by 'nb0dueaf 2026-08-28 14:50:09 ... [P2 - closed]' for a bead last semantically touched 2026-08-26

## 304

- **Title:** yf-ek9a: coordinator batch-closes beads, making 84% of observed interval overlap an artifact
- **Cluster:** execution-telemetry · **Type:** bead
- **Repo:** yoshiko-flow
- **Locator:** `bd show yf-ek9a --json (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **STRONG** (total 82 = directness 40 + reproducibility 18 + verification 20 + n/scope 4) — bd/interactions.jsonl record; all 3 corpus reopens hand-audited
- **Retrieved:** 2026-08-28

> The coordinator closes beads in batches rather than when each unit of work finishes. That collapses distinct work intervals onto a single timestamp, so 84% of all observed interval overlap is an artifact of when the closes were flushed -- not of when work actually ran concurrently.

## 305

- **Title:** The one non-trivial reopen in the corpus is a bead-id mis-mapping bookkeeping fix, not rework
- **Cluster:** execution-telemetry · **Type:** file
- **Repo:** yoshiko-flow
- **Locator:** `grep 'yf-mol-bh8.2.11' .beads/interactions.jsonl (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **MODERATE** (total 74 = directness 40 + reproducibility 18 + verification 12 + n/scope 4) — verbatim file content, path-located
- **Retrieved:** 2026-08-28

> 2026-08-26T01:32:36Z closed -> open (reason: null); 2026-08-26T01:32:36Z in_progress -> closed (reason: '...NOTE: this reason was first recorded against yf-mol-bh8.2.11 (Issue 1.6b) by a bead-id mis-mapping; 2.11 has been reopened and carries its own control, ctl-208-edge-scope.')

## 306

- **Title:** Corpus-wide reopen rate: 3 of 2969 recorded status changes (0.1%), all in yoshiko-flow
- **Cluster:** execution-telemetry · **Type:** computed
- **Repo:** all 7
- **Locator:** `python3 scan of extra.field=='status' events in .beads/interactions.jsonl across all 7 repos (script: /tmp/005scratch/analyze_interactions.py, ephemeral)`
- **Evidence strength:** **MODERATE** (total 72 = directness 20 + reproducibility 25 + verification 12 + n/scope 15) — derived aggregate over primaries; command given; recomputed by the triangulator and reproduced
- **Retrieved:** 2026-08-28

> yoshiko-flow: 1687 status field_changes, 3 reopens (closed->open/in_progress); d3-pxe: 599 changes, 0 reopens; evri_py: 51 changes, 0; writing: 293 changes, 0; pybridge: 183 changes, 0; emacs.d: 53 changes, 0; rc-files: 103 changes, 0

## 307

- **Title:** interactions.jsonl date range starts within a day of each repo's earliest issue creation -- near-full-lifetime coverage
- **Cluster:** execution-telemetry · **Type:** file
- **Repo:** all 7
- **Locator:** `python3 min/max created_at scan of .beads/interactions.jsonl vs .beads/issues.jsonl per repo (script: /tmp/005scratch/check_coverage.py, ephemeral)`
- **Evidence strength:** **MODERATE** (total 74 = directness 40 + reproducibility 18 + verification 12 + n/scope 4) — verbatim file content, path-located
- **Retrieved:** 2026-08-28

> yoshiko-flow interactions range 2026-04-05T22:14:24Z..2026-08-28T14:50:05Z vs issues created range 2026-04-05T22:12:48Z..2026-08-17T18:46:15Z

## 308

- **Title:** Reopen example 2: a mechanical probe close/reopen cycle, not rework
- **Cluster:** execution-telemetry · **Type:** file
- **Repo:** yoshiko-flow
- **Locator:** `grep 'yf-mol-84r.4.1' .beads/interactions.jsonl (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **MODERATE** (total 74 = directness 40 + reproducibility 18 + verification 12 + n/scope 4) — verbatim file content, path-located
- **Retrieved:** 2026-08-28

> 2026-08-16T23:57:40Z in_progress -> closed | probe: unset var; 2026-08-16T23:57:50Z closed -> in_progress | None; 2026-08-16T23:58:27Z in_progress -> closed | Epic-3 SPEC amendments landed BEFORE any Epic-3 code...

## 309

- **Title:** Reopen example 3: another probe close/reopen cycle, not rework
- **Cluster:** execution-telemetry · **Type:** file
- **Repo:** yoshiko-flow
- **Locator:** `grep 'yf-mol-bh8.3.2' .beads/interactions.jsonl (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **MODERATE** (total 74 = directness 40 + reproducibility 18 + verification 12 + n/scope 4) — verbatim file content, path-located
- **Retrieved:** 2026-08-28

> 2026-08-26T02:14:59Z in_progress -> closed | probe; 2026-08-26T02:16:03Z closed -> open | None; 2026-08-26T02:16:03Z open -> closed | Issue 2.2: indented fenced continuations collected VERBATIM...

## 310

- **Title:** discovered-from chains: 1-7% of issues, max fan-out 3, max depth 3, mode depth 2
- **Cluster:** execution-telemetry · **Type:** computed
- **Repo:** all 7
- **Locator:** `python3 discovered-from edge/fanout/depth scan over .beads/issues.jsonl dependencies (script: /tmp/005scratch/discovered_from.py, ephemeral)`
- **Evidence strength:** **MODERATE** (total 72 = directness 20 + reproducibility 25 + verification 12 + n/scope 15) — derived aggregate over primaries; command given; recomputed by the triangulator and reproduced
- **Retrieved:** 2026-08-28

> yoshiko-flow: 26 edges/1245 issues, 23 roots, max depth 2; pybridge: 15 edges/229 issues, 11 roots, max depth 3 ({2: 10, 3: 1}); emacs.d: 0 discovered-from edges at all

## 311

- **Title:** bd blocked live-computed list agrees exactly with bd status blocked_issues count (6/6)
- **Cluster:** execution-telemetry · **Type:** bead
- **Repo:** yoshiko-flow
- **Locator:** `bd blocked --json (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **STRONG** (total 82 = directness 40 + reproducibility 18 + verification 20 + n/scope 4) — bd/interactions.jsonl record; all 3 corpus reopens hand-audited
- **Retrieved:** 2026-08-28

> total blocked: 6; yf-mol-49u.5 in_progress blocked_by_count=3 ['yf-mol-49u.4','yf-mol-49u.1','yf-mol-49u.3']; yf-mol-eci open blocked_by_count=6 [...]

## 312

- **Title:** writing repo: 29/29 blocked beads agree between bd status summary and bd blocked enumeration, all real dependency waits
- **Cluster:** execution-telemetry · **Type:** bead
- **Repo:** writing
- **Locator:** `bd blocked --json (run in ~/workspace/dixson3/writing)`
- **Evidence strength:** **STRONG** (total 82 = directness 40 + reproducibility 18 + verification 20 + n/scope 4) — bd/interactions.jsonl record; all 3 corpus reopens hand-audited
- **Retrieved:** 2026-08-28

> total blocked: 29; blog-mol-zzm.6.3 open blocked_by_count=6 [...]; blog-p1q open blocked_by_count=1 ['blog-qfs'] | Integrate transcript augmentations...

## 313

- **Title:** 'blocked' is a live-computed state, not a stored status literal -- bd list --status blocked returns empty
- **Cluster:** execution-telemetry · **Type:** bead
- **Repo:** yoshiko-flow / writing
- **Locator:** `bd list --status blocked --json (run in each repo)`
- **Evidence strength:** **STRONG** (total 82 = directness 40 + reproducibility 18 + verification 20 + n/scope 4) — bd/interactions.jsonl record; all 3 corpus reopens hand-audited
- **Retrieved:** 2026-08-28

> yoshiko-flow: 0 results; writing: 0 results -- both when bd status --json reported nonzero blocked_issues in the same repo at the same time

## 314

- **Title:** Essentially no dangling blocking edges corpus-wide (1 stray non-id string out of thousands of edges)
- **Cluster:** execution-telemetry · **Type:** computed
- **Repo:** all 7
- **Locator:** `python3 dangling-dependency scan over all 'blocks'-type edges in .beads/issues.jsonl per repo (script: /tmp/005scratch/dangling_deps.py, ephemeral)`
- **Evidence strength:** **MODERATE** (total 72 = directness 20 + reproducibility 25 + verification 12 + n/scope 15) — derived aggregate over primaries; command given; recomputed by the triangulator and reproduced
- **Retrieved:** 2026-08-28

> yoshiko-flow: 1 dangling 'blocks' target, sample [('yf-67e2d9e7','--metadata')] (a stray CLI flag string, not an issue id); all other 6 repos: 0 dangling targets

## 315

- **Title:** Small counts of open issues depending on already-closed blockers -- normal readiness state, not corruption
- **Cluster:** execution-telemetry · **Type:** computed
- **Repo:** evri_py / writing
- **Locator:** `same dangling_deps.py script, 'non-closed issue depends on a closed blocker' branch`
- **Evidence strength:** **MODERATE** (total 72 = directness 20 + reproducibility 25 + verification 12 + n/scope 15) — derived aggregate over primaries; command given; recomputed by the triangulator and reproduced
- **Retrieved:** 2026-08-28

> evri_py: 17 such edges, sample [('evri_py-mol-e3d.3.4','evri_py-mol-e3d.3.3','open'), ...]; writing: 2 such edges; all other 5 repos: 0

## 316

- **Title:** log.md exists in only 37.7% of plan bundles corpus-wide
- **Cluster:** execution-telemetry · **Type:** computed
- **Repo:** all 7
- **Locator:** `python3 has_log_md tally over corpus_scan.py --json output (run from RD)`
- **Evidence strength:** **MODERATE** (total 72 = directness 20 + reproducibility 25 + verification 12 + n/scope 15) — derived aggregate over primaries; command given; recomputed by the triangulator and reproduced
- **Retrieved:** 2026-08-28

> 43/114 bundles have log.md (37.7%)

## 317

- **Title:** No log.md in the corpus has more than 2 top-level entries
- **Cluster:** execution-telemetry · **Type:** file
- **Repo:** all 5 software repos
- **Locator:** `find <5 repos>/docs/plans -name log.md | xargs grep -c '^## ' | sort/uniq -c`
- **Evidence strength:** **MODERATE** (total 74 = directness 40 + reproducibility 18 + verification 12 + n/scope 4) — verbatim file content, path-located
- **Retrieved:** 2026-08-28

> 3 files: 0 entries; 16 files: 1 entry; 18 files: 2 entries (37 log.md files total)

## 318

- **Title:** A 2-entry log.md's populated section is a single retrospective recap of 5 review passes, not 5 incremental writes
- **Cluster:** execution-telemetry · **Type:** file
- **Repo:** yoshiko-flow
- **Locator:** `cat docs/plans/plan-054-james-dixson-535968/log.md`
- **Evidence strength:** **MODERATE** (total 74 = directness 40 + reproducibility 18 + verification 12 + n/scope 4) — verbatim file content, path-located
- **Retrieved:** 2026-08-28

> review-pass: red-team pass 5 (fifth independent, via Agent): REVISE -- 9 of 9 pass-4 resolutions reproduced; C1 landed as prose with neither the edge to run it nor the verb to prove it; LOOP BOUND REACHED, escalates to operator [... pass 4, 3, 2, 1 similarly listed under one heading]

## 319

- **Title:** yf-zrtx: started_at written for only 86/225 plan beads, not exposed by bd list --json
- **Cluster:** execution-telemetry · **Type:** bead
- **Repo:** yoshiko-flow
- **Locator:** `bd show yf-zrtx --json (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **STRONG** (total 82 = directness 40 + reproducibility 18 + verification 20 + n/scope 4) — bd/interactions.jsonl record; all 3 corpus reopens hand-audited
- **Retrieved:** 2026-08-28

> Beads carrying both started_at and closed_at: 86 of 225 (plan-048 alone: 0 of 39). Separately, bd list --json does not expose started_at at all.

## 320

- **Title:** 69.3% of plan bundles (79/114) have at least one bead referencing their plan_id string
- **Cluster:** execution-telemetry · **Type:** computed
- **Repo:** all 7
- **Locator:** `python3 plan_id substring join of corpus_scan.py bundle list against each repo's .beads/issues.jsonl title+description+close_reason+metadata text (script: /tmp/005scratch/join_plan.py, ephemeral)`
- **Evidence strength:** **MODERATE** (total 72 = directness 20 + reproducibility 25 + verification 12 + n/scope 15) — derived aggregate over primaries; command given; recomputed by the triangulator and reproduced
- **Retrieved:** 2026-08-28

> yoshiko-flow: 41/56 (73%); d3-pxe: 12/19 (63%); evri_py: 4/9 (44%); writing: 8/11 (73%); pybridge: 10/11 (91%); emacs.d: 1/4 (25%); rc-files: 3/4 (75%); TOTAL: 79/114 = 69.3%

## 321

- **Title:** Unjoined bundles are not simply pre-beads-adoption artifacts -- plan-044 (Aug 2026) is unjoined despite falling well inside the repo's beads-active period (since April 2026)
- **Cluster:** execution-telemetry · **Type:** computed
- **Repo:** yoshiko-flow
- **Locator:** `corpus_scan.py --json bundle records for plan-002-james-dixson-b8b610 and plan-044-james-dixson-f6fdbd, cross-checked against the join_plan.py unjoined list`
- **Evidence strength:** **MODERATE** (total 72 = directness 20 + reproducibility 25 + verification 12 + n/scope 15) — derived aggregate over primaries; command given; recomputed by the triangulator and reproduced
- **Retrieved:** 2026-08-28

> plan-002-james-dixson-b8b610: git_first_commit_date 2026-05-31T21:16:27-07:00; plan-044-james-dixson-f6fdbd: git_first_commit_date 2026-08-17T20:51:54-07:00 -- both unjoined despite yoshiko-flow beads activity starting 2026-04-05

## 322

- **Title:** Live example of blocked-state reflecting ordinary DAG phase-gating, not rework -- this research molecule's own retrieve step
- **Cluster:** execution-telemetry · **Type:** bead
- **Repo:** yoshiko-flow
- **Locator:** `bd blocked --json (run in ~/workspace/dixson3/yoshiko-flow), record for yf-mol-49u.5`
- **Evidence strength:** **STRONG** (total 82 = directness 40 + reproducibility 18 + verification 20 + n/scope 4) — bd/interactions.jsonl record; all 3 corpus reopens hand-audited
- **Retrieved:** 2026-08-28

> yf-mol-49u.5 'Retrieve: operator-breakthrough-turns' status in_progress, blocked_by_count=3, blocked_by=['yf-mol-49u.4','yf-mol-49u.1','yf-mol-49u.3']

## 401

- **Title:** Author-reported validation numbers, reproduced identically
- **Cluster:** git-churn-signatures · **Type:** tool-output
- **Repo:** corpus-wide
- **Locator:** `uv run scripts/churn_signature.py --census <corpus_scan.json> --json (run in docs/research/005-thrash-detection-and-operator-judgement)`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> 114/114 bundles processed, 0 errors. 5 churn-signal commits matched a revert/redo commit-message pattern (all 'actually' or 'correct ... in place'; no literal git revert commits found in this corpus). 233 repeatedly-touched files (>= 3 distinct commits touching one non-bundle file within a plan's commit window) across 53 bundles (61 bundles had none).

## 402

- **Title:** Total commit counts per repo
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** corpus-wide
- **Locator:** `git -C <repo> log --oneline | wc -l, run for all 7 corpus repos`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> yoshiko-flow=697 d3-pxe=323 evri_py=113 writing=117 pybridge=242 emacs.d=178 rc-files=374 (sum 2044)

## 403

- **Title:** Commits inside plan-bundle windows, summed per repo (may overlap across bundles)
- **Cluster:** git-churn-signatures · **Type:** tool-output
- **Repo:** corpus-wide
- **Locator:** `churn_signature.py --census output, field total_commits_in_window summed per repo_root`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> yoshiko-flow=727 (56 bundles) d3-pxe=344 (19) evri_py=56 (9) writing=44 (11) pybridge=141 (11) emacs.d=12 (4) rc-files=35 (4)

## 404

- **Title:** Window construction is a union of path-scoped and grep-scoped commits
- **Cluster:** git-churn-signatures · **Type:** tool-doc
- **Repo:** yoshiko-flow
- **Locator:** `uv run scripts/churn_signature.py --help`
- **Evidence strength:** **WEAK** (total 57 = directness 12 + reproducibility 18 + verification 12 + n/scope 15) — the tool's own docstring — describes intent, not measured behaviour
- **Retrieved:** 2026-08-28

> finds the commit window a plan touched — the union of (a) commits whose path-scoped `git log` touches the bundle directory itself ... and (b) commits on the current branch whose message mentions the plan's short id (`plan-NNN`)

## 405

- **Title:** Broad whole-history base-rate hit counts (subject+body, unanchored)
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** corpus-wide
- **Locator:** `git -C <repo> log --oneline -E --regexp-ignore-case --grep='revert' --grep='redo' --grep='take 2' --grep='take two' --grep='actually' --grep='fix the fix' --grep='oops' --grep='undo' --grep='wrong' --grep='incorrect' --grep='correct.*in place', run per repo`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> yoshiko-flow=75/697 d3-pxe=49/323 evri_py=6/113 writing=2/117 pybridge=8/242 emacs.d=10/178 rc-files=13/374 (total 163/2044 = 8.0%)

## 406

- **Title:** Example of a body-buried false-positive match for 'wrong'
- **Cluster:** git-churn-signatures · **Type:** git-show
- **Repo:** yoshiko-flow
- **Locator:** `git -C ~/workspace/dixson3/yoshiko-flow log -1 5b7edb9 --format="%B" | grep -in 'wrong' (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git show; verbatim commit body
- **Retrieved:** 2026-08-28

> - Fix check-prereqs.sh: wrong beads URL, missing git check, stale comment

## 407

- **Title:** Literal git-revert-generated commits found
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** corpus-wide
- **Locator:** `git -C <repo> log --oneline --grep='^Revert', run per repo`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> yoshiko-flow=1 d3-pxe=0 evri_py=1 writing=0 pybridge=0 emacs.d=0 rc-files=3 — all 5 matches are body prose lines starting with the word Revert, none is an actual `git revert` porcelain commit

## 408

- **Title:** Strongest true-positive churn signal found — self-reported triple drift
- **Cluster:** git-churn-signatures · **Type:** git-show
- **Repo:** yoshiko-flow
- **Locator:** `git -C ~/workspace/dixson3/yoshiko-flow show 18f3959e1daf1b429799671068dc8d1162722b15 --format='%B' (run in ~/workspace/dixson3/yoshiko-flow)`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git show; verbatim commit body
- **Retrieved:** 2026-08-28

> plan-045: make REQ-CLI-006 self-consistent and actually executed Third drift of one REQ inside one plan: grep gave 25, the spec asserted 24, and retrospective-report was unenumerated. It survived a 33/33 FULL-tier sweep because the REQ's own Verification line was prose shaped like a command -- nothing ran it.

## 409

- **Title:** Correct-in-place hit is a cross-plan documentation correction, not intra-plan thrash
- **Cluster:** git-churn-signatures · **Type:** git-show
- **Repo:** d3-pxe
- **Locator:** `git -C ~/workspace/dixson3/d3-pxe show 07d1bfb1ba643f03e8255a82489cc151a07890ef --format='%B' (run in ~/workspace/dixson3/d3-pxe)`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git show; verbatim commit body
- **Retrieved:** 2026-08-28

> plan-017 Issue 2.3: correct plan-016's 440 MB figure in place, at all four sites Annotated rather than silently rewritten: plan-016 is a historical record, so each site now carries a dated correction block explaining WHY the number is wrong, not just that it is.

## 410

- **Title:** 'Actually' hit #5 — proving a check actually catches, not a redo
- **Cluster:** git-churn-signatures · **Type:** git-show
- **Repo:** d3-pxe
- **Locator:** `git -C ~/workspace/dixson3/d3-pxe show ba8f6e93d5bd1f71dca0e7b843f8b3e06d2d705b --format='%B' (run in ~/workspace/dixson3/d3-pxe, Incubator/ansible/plans/plan-013)`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git show; verbatim commit body
- **Retrieved:** 2026-08-28

> plan-013 Issue 1.5: prove the new ledger checks actually catch (SC1) A gate that has never been seen to fail is not known to work.

## 411

- **Title:** Genuine hand-authored semantic revert, outside any plan-bundle window
- **Cluster:** git-churn-signatures · **Type:** git-show
- **Repo:** evri_py
- **Locator:** `git -C ~/workspace/evri/evri_py log -1 db41594 --format='%B' (run in ~/workspace/evri/evri_py)`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git show; verbatim commit body
- **Retrieved:** 2026-08-28

> bundler: restore local bundle_assets ownership; capture intent in SPEC Reverts 5d03ddc's PYBRIDGE_REPO dependency. evri_py owns the assets that...

## 412

- **Title:** Second genuine hand-authored semantic revert
- **Cluster:** git-churn-signatures · **Type:** git-show
- **Repo:** rc-files
- **Locator:** `git -C ~/_dotfiles/rc-files log -1 8b05e8b --format='%B' (run in ~/_dotfiles/rc-files)`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git show; verbatim commit body
- **Retrieved:** 2026-08-28

> pi.dev: drop vendored skills + YOSHIKO_FLOW rule (superseded by pi extensions) Reverts the 5440463 vendoring of yf-beads/naba skill markdown and the...

## 413

- **Title:** Third genuine hand-authored semantic revert
- **Cluster:** git-churn-signatures · **Type:** git-show
- **Repo:** rc-files
- **Locator:** `git -C ~/_dotfiles/rc-files log -1 50060b7 --format='%B' (run in ~/_dotfiles/rc-files)`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git show; verbatim commit body
- **Retrieved:** 2026-08-28

> re-add CodeGraphContext to curated uv tool list Reverts the removal from f27d2fa. Supports Python 3.10-3.14 per upstream, no pin needed.

## 414

- **Title:** main.rs / SPEC.md / Cargo.toml re-touch counts — hot files
- **Cluster:** git-churn-signatures · **Type:** tool-output
- **Repo:** yoshiko-flow
- **Locator:** `churn_signature.py bundle=docs/plans/plan-010-james-dixson-73eebd, field repeatedly_touched_files (run in docs/research/005-thrash-detection-and-operator-judgement)`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> {"file": "yf/src/main.rs", "touch_count": 9, ...} {"file": "SPEC.md", "touch_count": 6, ...} {"file": "yf/Cargo.toml", "touch_count": 6, ...}

## 415

- **Title:** ~30 SKILL.md/README.md files touched by the identical same 3 commits — mechanical bulk edit
- **Cluster:** git-churn-signatures · **Type:** tool-output
- **Repo:** yoshiko-flow
- **Locator:** `churn_signature.py bundle=docs/plans/plan-054-james-dixson-535968, field repeatedly_touched_files (run in docs/research/005-thrash-detection-and-operator-judgement)`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> skills/yf-beads-authoring/SKILL.md ... skills/yf-beads-hygiene/README.md ... skills/yf-research/agents/toolsmith.md — touch_count 3 each, commits [ac56bb0..., 7d656b2..., 9d1f653...] identical across every listed file

## 416

- **Title:** Window contamination — 2 of 7 touching commits belong to plan-054, 9 days later
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** yoshiko-flow
- **Locator:** `git -C ~/workspace/dixson3/yoshiko-flow log -1 --format='%h %ad %s' --date=short <sha>, for the 7 SHAs touching yf/src/coverage.rs in plan-044's window`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> d1fa3e5 2026-08-17 plan-044 Epic 0 ... c2e5208 2026-08-17 plan-044 Epic 1 ... a43805e 2026-08-17 plan-044 Issues 2.8-2.11 ... 4380c74 2026-08-26 plan-054 Issues 0.2-0.5: SPEC-first amendments for v0.5.0 ... 6d12a8e 2026-08-26 plan-054 Issues 1.1+1.2

## 417

- **Title:** Clean decomposition example — one commit per sequential Issue, same day
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** yoshiko-flow
- **Locator:** `git -C ~/workspace/dixson3/yoshiko-flow log -1 --format='%h %ad %s' --date=short <sha>, for the 6 SHAs touching yf/src/cmd/self_cmd/mod.rs in plan-018's window`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> b03b7bf 2026-06-30 feat(self): install-receipt contract (plan-018 3.1) ... c55afb8 (3.2) ... 6b37c17 (3.3) ... d371c9c (3.4a) ... a1f663b (3.5) ... 46281b5 (4.1)

## 418

- **Title:** Timing shape of the plan-045 correction — burst then 71-minute gap
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** yoshiko-flow
- **Locator:** `git -C ~/workspace/dixson3/yoshiko-flow log -1 --format='%h %ai %s' <sha>, for the 5 SHAs touching CHANGE-VALIDATION.md in plan-045's window`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> 11:32:24 plan-045 Epic 1 ... 11:46:34 Epic 2 (+14m) ... 11:53:16 Epic 3 (+7m) ... 12:00:36 Epic 4 (+7m) ... 13:11:37 make REQ-CLI-006 self-consistent and actually executed (+71m)

## 419

- **Title:** Decomposition example — ansible role defaults built incrementally across epics
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** d3-pxe
- **Locator:** `git -C ~/workspace/dixson3/d3-pxe log -1 --format='%h %s' <sha>, for the 7 SHAs touching ansible/roles/pve_backup/defaults/main.yml in plan-016's window`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> d44077b plan-016 Issues 1.2 + 1.4: pve_backup role skeleton ... dfd2a94 Issue 1.6 ... 9cb82be Epic 2 ... 505c90d Epic 3 ... 5b0698e Issues 4.1,4.2,4.4 ... 0e388c1 Issue 5.2 ... ffb875e SPEC PVE-STO-006

## 420

- **Title:** Window contamination example — a plan-010 commit inside plan-011's window
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** d3-pxe
- **Locator:** `git -C ~/workspace/dixson3/d3-pxe log -1 --format='%h %s' <sha>, for the 4 SHAs touching ansible/inventory/host_vars/postgres.yml in plan-011's window`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> 6020d15 plan-011 Issue 2.3 (part): inventory/host_vars/postgres.yml ... 6d580ea plan-011 Issue 3.8 ... 6d7c7fd Add CANARY.md ... 7a45c98 plan-010 Issue 3.0a: v2 Prisma resolver + dedicated litellm_proxy database

## 421

- **Title:** Window contamination example — a markdown-lint fix 5 weeks later inside plan-001's window
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** rc-files
- **Locator:** `git -C ~/_dotfiles/rc-files log -1 --format='%h %ad %s' --date=short <sha>, for the 5 SHAs touching AGENTS.md in plan-001's window`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> 0351992 2026-05-17 plan: bin/dotfiles consolidation (plan-001, bdplan) ... a486c78 2026-05-18 ... c41f63f 2026-05-19 ... c9f7836 2026-05-19 ... 9041f56 2026-06-24 markdown: enable yf-markdown-lint on-edit + fix ML008 alignment markers

## 422

- **Title:** Top basenames among the 233 repeatedly-touched files — dominated by hot/mandated files
- **Cluster:** git-churn-signatures · **Type:** tool-output
- **Repo:** corpus-wide
- **Locator:** `python3 aggregation over churn_signature.py --census output, Counter over repeatedly_touched_files[*].file.split('/')[-1]`
- **Evidence strength:** **MODERATE** (total 66 = directness 20 + reproducibility 25 + verification 6 + n/scope 15) — tool-asserted aggregate, not itself hand-audited; all three scripts re-run by the triangulator and reproduced exactly (114/301, 1509 findings, 40/8 episodes, 51 self-reported, 5 churn signals, 233 retouched)
- **Retrieved:** 2026-08-28

> SKILL.md=34 SPEC.md=24 README.md=18 main.yml=17 issues.jsonl=14 interactions.jsonl=7 plan_manager.py=6 CHANGE-VALIDATION.md=5 RESERVATIONS.md=5 cli.rs=4

## 423

- **Title:** Merge-commit counts confirm no squash-merge in this corpus
- **Cluster:** git-churn-signatures · **Type:** git-log
- **Repo:** corpus-wide
- **Locator:** `git -C <repo> log --oneline --merges | wc -l vs git -C <repo> log --oneline | wc -l, per repo`
- **Evidence strength:** **STRONG** (total 89 = directness 40 + reproducibility 25 + verification 20 + n/scope 4) — exact SHA + re-runnable git command; hand-audited commit subject/body
- **Retrieved:** 2026-08-28

> yoshiko-flow merges=89 total=697 d3-pxe merges=37 total=323 evri_py merges=8 total=113 writing merges=12 total=117 pybridge merges=9 total=242 emacs.d merges=7 total=178 rc-files merges=21 total=374

## 424

- **Title:** finding_recurrence.py's review-pass-residue signal, for comparison against git's
- **Cluster:** git-churn-signatures · **Type:** research-doc
- **Repo:** yoshiko-flow
- **Locator:** `docs/research/005-thrash-detection-and-operator-judgement/artifacts/tooling-notes.md, section 'Measured validation numbers'`
- **Evidence strength:** **WEAK** (total 57 = directness 12 + reproducibility 18 + verification 12 + n/scope 15) — a statement of this study's own method/tooling
- **Retrieved:** 2026-08-28

> 8 candidate thrash episodes at threshold 0.35 / id-floor 0.15 ... 51 self-reported cross-pass signals ... This is the highest-confidence recurrence signal in the corpus because a human reviewer already did the cross-pass comparison

## 425

- **Title:** 004's residue boundary, inherited as this cluster's starting constraint
- **Cluster:** git-churn-signatures · **Type:** project-doc
- **Repo:** yoshiko-flow
- **Locator:** `docs/research/005-thrash-detection-and-operator-judgement/plan.yaml, method_notes`
- **Evidence strength:** **MODERATE** (total 65 = directness 28 + reproducibility 18 + verification 12 + n/scope 7) — repo instruction file; primary but describes policy, not an episode
- **Retrieved:** 2026-08-28

> 004 is the direct predecessor and its boundary is the starting constraint: it found that plan bundles record ARTIFACTS, not live session behavior -- thrashing happens in a session and leaves only indirect residue.

## 501

- **Title:** Residue can MIS-ATTRIBUTE an operator turn: a logged 'operator approved' was actually the execute-session agent
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/log.md:11`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> approved: RATIFIED by operator 2026-08-17. CORRECTION: this transition was performed by the subordinate execute-session agent, not by an operator, and was originally logged as "operator approved" — which was false at the time it was written. INTAKE (fingerprint, commit 31a367b, merge 7aa7e04, tracking issue #79) therefore ran ahead of consent.

## 502

- **Title:** The corpus records ANSWERS, not QUESTIONS — a red-team pass names this as a defect
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-053-james-dixson-4015d3/reviews/pass-1.md:45`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | C13 | low | The three operator decisions D-5/D-6/D-7 have **no recorded question** — no `scope-answers.md`. Substance is independently corroborated by findings, but the framing cannot be audited |

## 503

- **Title:** An operator decision taken EARLY was invalidated by a later experiment — evidence that pre-elicitation can inject a wrong commitment
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-039-james-dixson-150f79/reviews/pass-1.md:97`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> operator selected all four fixes — but that selection was made *before* EXP-001 existed.

## 504

- **Title:** A review pass overturned an operator decision — the arrow runs backwards from the hypothesis's assumption
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-040-james-dixson-1cabe4/reviews/pass-1.md:174`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> **Note on process.** C6 changed an operator decision: the original ensure-label-before-use choice

## 505

- **Title:** Content-free record of an operator decision — something was decided, the artifact does not say what
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-009-james-dixson-4f56e2/reviews/pass-1.md:61`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | C7 | Operator decision — see below. | resolved |

## 506

- **Title:** T1 fork resolution (yoshiko-flow): operator selects between two apply modes the reviewer surfaced
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-002-james-dixson-b8b610/reviews/pass-1.md:23`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> **Resolution:** Operator confirmed **split apply mode** — K1 (token cuts) auto-applies; K2

## 507

- **Title:** T1/T4 (d3-pxe): operator sets a risk-window value the plan could not derive
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/reviews/pass-3.md:252`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | E2 | **Accepted — operator decision: raise to 90 days.** `NoncurrentDays: 90` in Issue 1.4's rule table. The property is restated as a **bounded window, not an unbounded claim**, in all four places it appears

## 508

- **Title:** T1 fork resolution (pybridge): explicit option (a) vs (b) selection
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** pybridge
- **Locator:** `docs/plans/plan-009-james-dixson-7e1c92/reviews/pass-1.md:65`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | C1 | Leg C: pull floor-lowering in (R1 b) vs measurement-gate-only (R1 a) | high | Operator chose **option (a)** (2026-06-21): measurement gate + ratchet only; floor-lowering filed as D.1.3. | resolved |

## 509

- **Title:** T1 fork resolution in a NON-software, low-ceremony repo — same shape as the software repos
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** emacs.d
- **Locator:** `docs/plans/plan-001-james-dixson-30e722/reviews/pass-1.md:69`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | C4 (auth posture) | Operator chose per-session bearer token in v1 (D7); 127.0.0.1 + Origin as defense-in-depth. Issues 2.1/4.1; R5 updated. | resolved |

## 510

- **Title:** T1 fork resolution (rc-files): packaging fork resolved by operator, with the actor column naming `operator`
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** rc-files
- **Locator:** `docs/plans/plan-004-james-dixson-f0bcc5/reviews/pass-1.md:103`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | C5 | med | Operator chose brew on both platforms. Entry moved to `Brewfile.common`; Linux vendor path, the symlinks.sh platform branch, the old Issue 1.3 and old SC9 all deleted; R5 downgraded to R6 (low). | `operator` | `resolved` |

## 511

- **Title:** T1 fork resolution (writing): split-vs-bundle decision resolved by operator choice
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** writing
- **Locator:** `docs/plans/plan-010-james-dixson-e049e3/reviews/pass-2.md:24`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> - Split vs bundle: **resolved** — operator chose bundle; conditionality removes ship-coupling.

## 512

- **Title:** T1 fork resolution mid-EXECUTION: operator picks option C from a three-way fork after a gate blocked the chain
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** evri_py
- **Locator:** `docs/plans/plan-006-james-dixson-38b166/plan.md (Phase log, 2026-06-21 executing)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> 2026-06-21 executing: R1 fired for #10 — pybridge#10 REOPENED (incomplete-fix root cause + repro). Epic 1 (#17) blocked on new gate eoz.12; transitive chain Epics 2/3/5/6 (#18/#22/#40/#39) held. Operator chose option C (hybrid: file upstream + proceed Epic 4 + hold chain).

## 513

- **Title:** T6 loop-bound override — the purest thrash-breaking turn, and a yf-ceremony artifact absent from 5 of 7 repos
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/log.md:16 (and lines 18,20,24,25,26,33 — seven separate raises)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> - autonomy: max-review-cycles raised to 13 for this invocation (cycles=12) — escalation override

## 514

- **Title:** One of only 4 T1 fork resolutions recorded as PRE-elicited at scoping time
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-003-james-dixson-adacc7/plan.md (Phase log, 2026-06-01 scoping)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> 2026-06-01 scoping: operator decisions locked (M2 per-project memory; GitHub-first; D3 folded in)

## 515

- **Title:** Pre-elicited scoping decisions (the 'locked' pattern)
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-024-james-dixson-76cee9/plan.md (Phase log, 2026-07-07 scoping)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> 2026-07-07 scoping: operator decisions locked (new status value; script-gated ready-check; reusable close-cascade helper)

## 516

- **Title:** Pre-elicitation explicitly credited with removing an investigation phase — the corpus's clearest support for asking early
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-034-james-dixson-ac6633/log.md:12`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> - drafting: scope clear from operator decisions (one plan/multi-epic; yf-5p9x hoisted to #97; yf-pxet reconcile+extend); low uncertainty, no INVESTIGATE phase

## 517

- **Title:** T2 scope subtraction taken on MEASURED non-convergence evidence that did not exist at scoping
- **Cluster:** operator-breakthrough-turns · **Type:** plan-decision
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/plan.md:92 (decision table row D-9)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim plan decision row; single-coder classification
- **Retrieved:** 2026-08-28

> | D-9 | **SPLIT at review cycle 5.** Epics 4 (M9) and 5 (#182/#184) go to **plan-051**; this plan lands the four mechanical fixes. | Operator decision on measured evidence. Concerns per pass ran **5 → 4 → 11 → 17 → 14**, and every high concern for three consecutive rounds landed on Epic 4, Epic 5, or the resolution round itself

## 518

- **Title:** T2 scope subtraction at review pass 3 — a quantified deferral
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-055-james-dixson-5f1c40/reviews/pass-3.md:126`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | N8 | medium | **OPERATOR DECISION — defer 4.1-4.5, keep 4.6/4.8/4.9.** Recorded as **D-14**. Plan drops from 38 issues / 26 criteria to **33 / 22** with no measured claim weakened. | `operator` | `resolved` |

## 519

- **Title:** T3 scope ADDITION mid-flight, invalidating the approval fingerprint
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-011-james-dixson-150357/log.md:16`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> - drafting: re-opened: adding Epic 5 Postgres observability (operator request) — fingerprint invalidated, re-review required

## 520

- **Title:** T4 risk-tolerance setting — a standing disposition that WAS pre-elicitable ('production is the line')
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** writing
- **Locator:** `docs/plans/plan-002-james-dixson-62a38d/plan.md (Phase log, 2026-06-26 drafting)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> 2026-06-26 drafting: v3 — operator relaxed C1 (staging-draft visibility accepted; production is the line); Substack config parameterized at project root (@dixson3 → @thesoftwarefactory)

## 521

- **Title:** T4 — a scoping CONSTRAINT recorded up front and later relaxed by the operator during execution
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-017-james-dixson-feb918/log.md:39`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> - executing: **operator relaxed the "no public DNS, no public hostname" scoping constraint.**

## 522

- **Title:** T5 authority grant — human gates pre-declared, then satisfied in one batched operator act
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-017-james-dixson-feb918/log.md:22`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> - executing: **OPERATOR AUTHORIZATIONS RECORDED (2026-08-18).** All five remaining human gates

## 523

- **Title:** T5 — only the operator could rule that a red gate was an environment defect, not a plan defect
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** pybridge
- **Locator:** `docs/plans/plan-003-james-dixson-e55a84/plan.md (Phase log, 2026-06-18 executing)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> 2026-06-18 executing: Tri-Platform Green gate resolved by OPERATOR OVERRIDE — macOS+Linux CI green (19/19 incl. 500MB, run 27734768524); Windows blocked by pre-existing runner cmake-PATH regression (pybridge-aey), not a plan code defect; real Windows CI validation deferred to that runner fix

## 524

- **Title:** THE prior-art pattern: the agent DRAFTS the forks with defaults and batches them to one approval boundary
- **Cluster:** operator-breakthrough-turns · **Type:** plan-decision
- **Repo:** writing
- **Locator:** `docs/plans/plan-005-james-dixson-44ae6f/plan.md:110-118`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim plan decision row; single-coder classification
- **Retrieved:** 2026-08-28

> **Operator decisions to confirm at approval** (defaults in brackets): - **D1 — spin-outs as new incubators vs PARTIAL. RESOLVED (2026-07-01): create both as new incubators** — `interregnum-elite-overproduction` and `social-distance-schismogenesis`. - **D2 — optional minor pieces. RESOLVED (2026-07-01): create both** — `story-red-widow` and `murphys-law-and-related`. - **D3 — the client T6 (maturity framework). ACCEPTED:** seed the *concept* only

## 525

- **Title:** Three drafted forks resolved in ONE operator turn — the cheapest operator turn in the corpus
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** writing
- **Locator:** `docs/plans/plan-005-james-dixson-44ae6f/plan.md (Phase log, 2026-07-01 approved)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> 2026-07-01 approved: operator approved; D1=both new, D2=both, D3=seed-only

## 526

- **Title:** The question-with-default pattern reused: reviewer marks concerns 'resolved (pending operator choice)'
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** writing
- **Locator:** `docs/plans/plan-010-james-dixson-e049e3/reviews/pass-1.md:79,85`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | C4 | No READY gate on `[needs-source]` | medium | **Operator decision surfaced** (block vs advisory); plan v2 adds the symmetric READY precondition per the operator's choice. | resolved (pending operator choice) |

## 527

- **Title:** CONTROL group: 9-word objective, 1 review pass, APPROVE
- **Cluster:** operator-breakthrough-turns · **Type:** plan-revision
- **Repo:** pybridge
- **Locator:** `docs/plans/plan-008-james-dixson-af7982/plan.md §Objective (first commit f98f637)`
- **Evidence strength:** **WEAK** (total 64 = directness 36 + reproducibility 12 + verification 12 + n/scope 4) — git-recovered plan.md revision; 'initial' is really 'first committed' (post-review in most bundles)
- **Retrieved:** 2026-08-28

> Investigate and fix #31: testArrayTransferMultiDim 2D ndarray transfer failure

## 528

- **Title:** CONTROL group: 18-word objective on a well-trodden LXC+Caddy recipe, 2 passes, APPROVE
- **Cluster:** operator-breakthrough-turns · **Type:** plan-revision
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-004-james-dixson-b79a13/plan.md §Objective (first commit 5a65d1d)`
- **Evidence strength:** **WEAK** (total 64 = directness 36 + reproducibility 12 + verification 12 + n/scope 4) — git-recovered plan.md revision; 'initial' is really 'first committed' (post-review in most bundles)
- **Retrieved:** 2026-08-28

> Add CalibreWeb ebook LXC guest fronted by a Caddy reverse proxy (Let's Encrypt via Route53 DNS-01) on pve

## 529

- **Title:** CONTROL group in a non-software repo: 15-word objective, 2 passes, APPROVE
- **Cluster:** operator-breakthrough-turns · **Type:** plan-revision
- **Repo:** rc-files
- **Locator:** `docs/plans/plan-003-james-dixson-450e38/plan.md §Objective (first commit 3e14d02)`
- **Evidence strength:** **WEAK** (total 64 = directness 36 + reproducibility 12 + verification 12 + n/scope 4) — git-recovered plan.md revision; 'initial' is really 'first committed' (post-review in most bundles)
- **Retrieved:** 2026-08-28

> Tailscale proxy container for SSH/RDP into a client tailnet (EVRInet) without leaving my own tailnet

## 530

- **Title:** REFUTATION of the objective-length reading: a 22-word, SPEC-anchored, well-specified objective that produced 8 review passes and 6 operator decisions
- **Cluster:** operator-breakthrough-turns · **Type:** plan-revision
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/plan.md §Objective (first commit 31a367b)`
- **Evidence strength:** **WEAK** (total 64 = directness 36 + reproducibility 12 + verification 12 + n/scope 4) — git-recovered plan.md revision; 'initial' is really 'first committed' (post-review in most bundles)
- **Retrieved:** 2026-08-28

> Implement the PVE-STO-005 backup tier (#51): Sanoid ZFS snapshots for the precious config/DB datasets plus scheduled Restic replication off-host to Amazon S3

## 531

- **Title:** RIVAL 'genuine domain underdetermination': the fork was not well-posed until an experiment ran
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/reviews/pass-4.md:219`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | F1 | **Accepted in part, and SETTLED BY MEASUREMENT — exp-007 (`findings/exp-007-restic-grouping-measurement.md`).** Operator decision: `--group-by host,paths`, applied to `backup` and `forget` in Issue 3.1, Issue 3.4's cadence table, R2 and SC5.

## 532

- **Title:** The SAME fork re-opened one pass later and re-measured — measurement, not argument, drove the operator turn
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/reviews/pass-5.md:232`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | G1 | **Accepted — confirmed by measurement, then fixed and re-measured (exp-007 §6, §7).** The defect is real: a conditional ninth path yields 2 groups and `no parent snapshot found`. Operator decision: pass **`media/books` as ONE directory target** with excludes.

## 533

- **Title:** RIVAL 'missing capability/permission' — 22 tasks stalled on unresolved human gates, not on under-specification
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-016-james-dixson-533fa8/log.md:8`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> - executing: Epic 1 partial: 1.1, 1.2, 1.4 closed. HALTED at the 'SPEC amendment approved' and 'AWS + 1Password write authority' capability gates — neither resolved. 22 open tasks remain, all gate-blocked.

## 534

- **Title:** RIVAL 'missing permission' causing a wholesale mid-execution pivot — an environmental fact, pre-elicitable as T5/T8
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** evri_py
- **Locator:** `docs/plans/plan-002-james-dixson-77c1c6/plan.md (Phase log, 2026-05-19 executing)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> 2026-05-19 executing: pivot to local-first — client cannot yet provision EVRI_PY_DISPATCH_TOKEN (operator is a repo guest, not org member). Epic 0 (pybridge release.yml notify-evri-py), Epic 3 (pybridge-triggered-release.yml), Epic 5 (CI end-to-end), Epics 6/7 (Linux/Windows) deferred.

## 535

- **Title:** T0 — a fork SURFACED to the operator and recorded as `unresolved`: the corpus's closest thing to a captured question
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-048-james-dixson-ed68a5/reviews/pass-4.md:77`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | H1 | high | **Operator decision — escalated.** The reviewer's option (a) is to split at approval rather than at 3.6: ship Epics 0–3 as plan-048, move Epics 4–6 to a successor. Option (b) re-bases the threshold to 5 so 3.6 tripwires a future cycle | `operator` | unresolved |

## 536

- **Title:** T0 in a second repo — a REVISE verdict driven by the need for operator decisions the agent could not take
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** pybridge
- **Locator:** `docs/plans/plan-009-james-dixson-7e1c92/reviews/pass-1.md:5,16`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> **Verdict:** REVISE (driven by the Leg C shipping-defect escalation; several concerns need operator decisions)

## 537

- **Title:** T0 — a concern marked RESOLVED by FRAMING the fork as an operator decision point, not by answering it
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** d3-pxe
- **Locator:** `docs/plans/plan-010-james-dixson-49050b/reviews/pass-2.md:44`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> | C6 | **RESOLVED** | R5 names the S7 breach explicitly and frames three options as an operator decision point. |

## 538

- **Title:** T6 process override — the operator changed the RESOLUTION METHOD, not the plan content
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/reviews/pass-4.md:87`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> Operator decision: resolve pass-4's concerns by **delegating the edit proposals to a sub-agent**,

## 539

- **Title:** T6 — the operator NARROWED the scope of a review pass to break an eleven-pass loop
- **Cluster:** operator-breakthrough-turns · **Type:** review-resolution
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-050-james-dixson-d0414b/reviews/pass-13.md:12,82`
- **Evidence strength:** **MODERATE** (total 72 = directness 40 + reproducibility 12 + verification 16 + n/scope 4) — verbatim quote from a review resolution cell; the 'operator did X' reading is an inference from an agent's own record (see id 501)
- **Retrieved:** 2026-08-28

> Eleventh independent pass, and a **narrow verification pass by operator decision** after the [...] The narrowing was an operator decision taken on measured grounds:

## 540

- **Title:** T3/T6 in a non-software repo — a mid-execution amendment plus an approval-staleness override
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** rc-files
- **Locator:** `docs/plans/plan-004-james-dixson-f0bcc5/log.md:12`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> - executing: stale-approval overridden (--force) — reasoning: mid-execution amendment adding Issue 6.6 + SC16, closing a yf-plan worktree/OS-artifact process gap found by the parent on the live machine; additive only, operator-authorized

## 541

- **Title:** T3 scope addition arriving AFTER approval — nothing a pre-flight question could have reached
- **Cluster:** operator-breakthrough-turns · **Type:** phase-log
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-019-james-dixson-eea8e7/plan.md (Phase log, 2026-07-02 approved)`
- **Evidence strength:** **MODERATE** (total 68 = directness 40 + reproducibility 12 + verification 12 + n/scope 4) — verbatim phase-log line; operator-attribution is an agent's claim, measurably fallible (id 501); single-coder classification
- **Retrieved:** 2026-08-28

> 2026-07-02 approved: post-approval scope add — dirty-build bypass (Issue 3.5 + REQ-YF-PRE-009 amend), operator-directed

## 542

- **Title:** T7 goal/intent statement — the 'the operator wants X' shape, always recorded at scoping in Motivation prose
- **Cluster:** operator-breakthrough-turns · **Type:** plan-revision
- **Repo:** yoshiko-flow
- **Locator:** `docs/plans/plan-036-james-dixson-461061/plan.md:44`
- **Evidence strength:** **WEAK** (total 64 = directness 36 + reproducibility 12 + verification 12 + n/scope 4) — git-recovered plan.md revision; 'initial' is really 'first committed' (post-review in most bundles)
- **Retrieved:** 2026-08-28

> The operator wants real, per-skill authored pages they can edit directly. The risk of authored pages is the inverse of the current design's strength: authored prose can **drift** from the skill's actual behavior as the skill evolves.

## 543

- **Title:** T9 taste — an aesthetic choice with no derivable criterion, trivially askable and trivially unguessable
- **Cluster:** operator-breakthrough-turns · **Type:** plan-revision
- **Repo:** emacs.d
- **Locator:** `docs/plans/plan-002-james-dixson-b23020/plan.md:41`
- **Evidence strength:** **WEAK** (total 64 = directness 36 + reproducibility 12 + verification 12 + n/scope 4) — git-recovered plan.md revision; 'initial' is really 'first committed' (post-review in most bundles)
- **Retrieved:** 2026-08-28

> The reference is the *readability* of `yf-markdown-pdf` (1in margins, calm page, legible links/tables), not a literal copy — that skill renders to white-paper PDF via pandoc+xelatex. The operator chose a **sepia/parchment** palette for the on-screen analog.

## 544

- **Title:** T8 environmental/authority fact captured by a context.md TEMPLATE FIELD — the corpus's most successful pre-elicitation (110/114 bundles)
- **Cluster:** operator-breakthrough-turns · **Type:** plan-revision
- **Repo:** pybridge
- **Locator:** `docs/plans/plan-009-james-dixson-7e1c92/context.md:44`
- **Evidence strength:** **WEAK** (total 64 = directness 36 + reproducibility 12 + verification 12 + n/scope 4) — git-recovered plan.md revision; 'initial' is really 'first committed' (post-review in most bundles)
- **Retrieved:** 2026-08-28

> - Upstream authority: GitHub Issues on `eigenvector-research-inc/pybridge` are the source of truth; operator authorizes the upstream push (conservative push policy). #4 stays OPEN by operator decision.

## 545

- **Title:** Evidence-surface census: 114 bundles / 301 review passes; context.md 112/114, log.md 43/114, phase log 113/114
- **Cluster:** operator-breakthrough-turns · **Type:** census
- **Repo:** all
- **Locator:** `docs/research/005-thrash-detection-and-operator-judgement/scripts/corpus_scan.py --json (run 2026-08-28)`
- **Evidence strength:** **MODERATE** (total 72 = directness 20 + reproducibility 25 + verification 12 + n/scope 15) — corpus_scan.py census; re-run and reproduced exactly
- **Retrieved:** 2026-08-28

> yoshiko-flow 56 bundles (166 passes); d3-pxe 19 (73); evri_py 9 (13); writing 11 (18); pybridge 11 (20); emacs.d 4 (4); rc-files 4 (7) — total 114 bundles / 301 review passes

## 601

- **Title:** mattpocock/skills — grill-me/SKILL.md
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grill-me/SKILL.md](https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grill-me/SKILL.md)
- **Credibility:** adjudicated tier **T1-primary** (mechanical scorer: 41 / questionable) — the skill file itself, fetched verbatim — highest tier for a claim about its own content; NOT a tier for any empirical claim
- **Retrieved:** 2026-08-28

> Call the Skill tool with "grilling".

## 602

- **Title:** mattpocock/skills — grilling/SKILL.md (the actual grill-me interview engine)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grilling/SKILL.md](https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grilling/SKILL.md)
- **Credibility:** adjudicated tier **T1-primary** (mechanical scorer: 41 / questionable) — as 601
- **Retrieved:** 2026-08-28

> Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. [...] The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

## 603

- **Title:** mattpocock/skills productivity README (grill-me/grilling framing)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/README.md](https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/README.md)
- **Credibility:** adjudicated tier **T1-primary** (mechanical scorer: 41 / questionable) — as 601
- **Retrieved:** 2026-08-28

> **[grill-me](./grill-me/SKILL.md)**: Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved.

## 604

- **Title:** bevibing/socrates-skill — SKILL.md (full prompt)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://raw.githubusercontent.com/bevibing/socrates-skill/main/SKILL.md](https://raw.githubusercontent.com/bevibing/socrates-skill/main/SKILL.md)
- **Credibility:** adjudicated tier **T1-primary** (mechanical scorer: 41 / questionable) — as 601
- **Retrieved:** 2026-08-28

> **NEVER give a direct answer.** Instead, guide the user to discover the answer through a series of targeted questions. This is non-negotiable — even if the user begs for the answer.

## 605

- **Title:** bevibing/socrates-skill README
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://raw.githubusercontent.com/bevibing/socrates-skill/main/README.md](https://raw.githubusercontent.com/bevibing/socrates-skill/main/README.md)
- **Credibility:** adjudicated tier **T1-primary** (mechanical scorer: 41 / questionable) — as 601
- **Retrieved:** 2026-08-28

> The agent **never** gives a direct answer — even if you ask for one.

## 606

- **Title:** Clarify When Necessary: Resolving Ambiguity Through Interaction with LMs (Zhang & Choi, NAACL Findings 2025)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://aclanthology.org/anthology-files/anthology-files/pdf/naacl/2025.naacl-findings.306.pdf](https://aclanthology.org/anthology-files/anthology-files/pdf/naacl/2025.naacl-findings.306.pdf)
- **Credibility:** adjudicated tier **T1-peer-reviewed** (mechanical scorer: 41 / questionable) — ACL Anthology (NAACL Findings 2025) — peer-reviewed; the URL rubric scored aclanthology.org 41/questionable, which is wrong
- **Retrieved:** 2026-08-28

> Determining when to ask for clarification is a challenging task that requires systems to consider the demands of the individual user (i.e., how much they prioritize speed and usability versus carefulness) and the distribution of interpretations for a given request (i.e., whether an ambiguous request has one dominant, inferable interpretation).

## 607

- **Title:** Knowing When to Ask: Self-Gated Clarification for Hierarchical Language Agents (Gao, Kang, Wang, Woo — AWS)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://arxiv.org/html/2606.11349v2](https://arxiv.org/html/2606.11349v2)
- **Credibility:** adjudicated tier **T2-preprint** (mechanical scorer: 63 / verify) — arXiv preprint, not peer-reviewed; the rubric's 92 domain-authority for arxiv.org over-ranks it relative to 606/611
- **Retrieved:** 2026-08-28

> Rather than treating clarification as an external uncertainty trigger, we propose ActionRating, a formulation that places it inside the agent's action space on a shared ordinal scale with navigation, so that asking competes directly with acting at every decision point and help-seeking becomes observable at intermediate states.

## 608

- **Title:** Knowing but Not Showing: LLMs Recognize Ambiguity but Rarely Ask Clarifying Questions (Su & Cardie)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://arxiv.org/html/2605.25284](https://arxiv.org/html/2605.25284)
- **Credibility:** adjudicated tier **T2-preprint** (mechanical scorer: 63 / verify) — arXiv preprint
- **Retrieved:** 2026-08-28

> LLMs Recognize Ambiguity but Rarely Ask Clarifying Questions

## 609

- **Title:** Act or Clarify? Modeling Sensitivity to Uncertainty and Cost in Communication (Tsvilodub & Mulligan, Tübingen)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://arxiv.org/html/2602.02843v3](https://arxiv.org/html/2602.02843v3)
- **Credibility:** adjudicated tier **T2-preprint** (mechanical scorer: 63 / verify) — arXiv preprint
- **Retrieved:** 2026-08-28

> Act or Clarify? Modeling Sensitivity to Uncertainty and Cost in Communication

## 610

- **Title:** CLAM: Selective Clarification for Ambiguous Questions with Generative Language Models (Kuhn, Gal, Farquhar)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://export.arxiv.org/pdf/2212.07769v2.pdf](https://export.arxiv.org/pdf/2212.07769v2.pdf)
- **Credibility:** adjudicated tier **T2-preprint** (mechanical scorer: 63 / verify) — arXiv preprint
- **Retrieved:** 2026-08-28

> Users often ask dialogue systems ambiguous questions that require clarification. We show that current language models rarely ask users to clarify ambiguous questions and instead provide incorrect answers.

## 611

- **Title:** CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs in LLMs (ACL 2024)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://aclanthology.org/anthology-files/pdf/acl/2024.acl-long.578.pdf](https://aclanthology.org/anthology-files/pdf/acl/2024.acl-long.578.pdf)
- **Credibility:** adjudicated tier **T1-peer-reviewed** (mechanical scorer: 41 / questionable) — ACL 2024 long paper — peer-reviewed; rubric under-scored (41)
- **Retrieved:** 2026-08-28

> CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs in Large Language Models

## 612

- **Title:** Agent Loop Detection: Definition & FutureAGI Guide (2026)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://futureagi.com/glossary/agent-loop-detection/](https://futureagi.com/glossary/agent-loop-detection/)
- **Credibility:** adjudicated tier **T4-vendor-glossary** (mechanical scorer: 41 / questionable) — commercial glossary page; no method, no data
- **Retrieved:** 2026-08-28

> The quieter failure is a stalled loop, where every step is syntactically valid but no step moves the task closer to completion.

## 613

- **Title:** When Agents Do Not Stop: Uncovering Infinite Agentic Loops in LLM Agents (Hou, Wang, Zhao, Wang — HUST)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://arxiv.org/html/2607.01641v1](https://arxiv.org/html/2607.01641v1)
- **Credibility:** adjudicated tier **T2-preprint** (mechanical scorer: 63 / verify) — arXiv preprint; reports 91.9% precision on 6,549 repos but unreviewed
- **Retrieved:** 2026-08-28

> We define an IAL as an execution failure in which an agentic feedback path repeatedly triggers LLM calls, tool invocations, agent executions, or workflow transitions without an effective termination condition.

## 614

- **Title:** Loop drift: how agents convince themselves they're making progress (Loop & Retry blog, 2026-07-07)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://loopandretry.github.io/posts/loop-drift/](https://loopandretry.github.io/posts/loop-drift/)
- **Credibility:** adjudicated tier **T4-practitioner** (mechanical scorer: 41 / questionable) — single-incident practitioner blog, n=1, unreplicated — cited by the prior-art cluster as an argument, not a result
- **Retrieved:** 2026-08-28

> We trusted the model's self-assessment. This is the deep one. Our loop asked the model, each step, whether it was making progress and whether it was done — and the model said yes, it was progressing, right up to the cap. [...] The model's sense of progress is generated from the same context that's drifting. Every 'I'm narrowing it down' was a fluent continuation of a transcript full of fluent continuations. A drifting agent's self-report drifts with it. Asking a stuck agent whether it's stuck is asking the unreliable narrator to review their own reliability.

## 615

- **Title:** kneelinghorse/agent-vitals — health monitor for production AI agents
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://github.com/kneelinghorse/agent-vitals](https://github.com/kneelinghorse/agent-vitals)
- **Credibility:** adjudicated tier **T4-oss** (mechanical scorer: 41 / questionable) — OSS project, 0 GitHub stars at retrieval, no external validation
- **Retrieved:** 2026-08-28

> **The direct-integration health monitor for production AI agents** — detect loops, stuck states, confabulation, thrash, and runaway costs with four numbers per step.

## 616

- **Title:** synthet1cc/unloop-mcp — MCP server that detects AI fix loops and forces course correction
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://github.com/synthet1cc/unloop-mcp](https://github.com/synthet1cc/unloop-mcp)
- **Credibility:** adjudicated tier **T4-oss** (mechanical scorer: 41 / questionable) — OSS project; its 55%-Jaccard loop rule is contradicted by this corpus (no threshold plateau; similarity does not rank truth)
- **Retrieved:** 2026-08-28

> **2. Unloop Detects the Loop** — The engine normalizes each error into a fingerprint (stripping paths, line numbers, timestamps) and compares fix descriptions using Jaccard similarity. When similarity exceeds 55%, it flags a loop. [...] | **CRITICAL** | 7+ attempts | "STOP. Revert everything. Ask the user for help." |

## 617

- **Title:** Yingqi-Han/learning-retrospective-skill — breaking retry loops, capturing verified lessons
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://github.com/Yingqi-Han/learning-retrospective-skill](https://github.com/Yingqi-Han/learning-retrospective-skill)
- **Credibility:** adjudicated tier **T4-oss** (mechanical scorer: 41 / questionable) — OSS project
- **Retrieved:** 2026-08-28

> Failure is not error — repeated attempts on a novel problem are legitimate exploration. The waste this skill targets is solving the **same** problem twice: struggling through a failure loop that a past session already resolved, because the lesson was never captured or never recalled.

## 618

- **Title:** Towards a typology of questions for requirements elicitation interviews (Zaremba & Liaskos, IEEE RE 2021)
- **Cluster:** prior-art · **Type:** web
- **URL:** [http://www.yorku.ca/liaskos/Papers/RE2021/RE2021.pdf](http://www.yorku.ca/liaskos/Papers/RE2021/RE2021.pdf)
- **Credibility:** adjudicated tier **T1-peer-reviewed** (mechanical scorer: 41 / questionable) — IEEE RE 2021 — peer-reviewed; author-hosted PDF on a .ca university host, which the rubric's .edu/.gov TLD test misses (scored 41)
- **Retrieved:** 2026-08-28

> Content is concerned with what the interviewer is interested in finding out about when asking a question. [...] R. Derr [4], inspired by the philosophical work of Aristotle and Kant, characterize question content based on the concept that the question presupposes. Thus, in reference to an object [...] one can question its existence, its identity, its properties, its relations to other objects, the number of the objects, if they are many, its time and location as well as whether the object is performing an action.

## 619

- **Title:** Ordering interrogative questions for effective requirements engineering: The W6H pattern (Sultan & Miranskyy, RePa 2015)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://doi.org/10.1109/repa.2015.7407731](https://doi.org/10.1109/repa.2015.7407731)
- **Credibility:** adjudicated tier **T1-peer-reviewed** (mechanical scorer: 41 / questionable) — IEEE RePa 2015 via DOI — peer-reviewed; rubric scored 41
- **Retrieved:** 2026-08-28

> Ordering interrogative questions for effective requirements engineering: The W6H pattern

## 620

- **Title:** Ambiguity and tacit knowledge in requirements elicitation interviews (Ferrari, Spoletini, Gnesi, RE 2015 journal version)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://iris.cnr.it/retrieve/38ee790c-9c4e-4758-9aae-6c87ab3bde7f/prod_353983-doc_114973.pdf](https://iris.cnr.it/retrieve/38ee790c-9c4e-4758-9aae-6c87ab3bde7f/prod_353983-doc_114973.pdf)
- **Credibility:** adjudicated tier **T1-peer-reviewed** (mechanical scorer: 41 / questionable) — CNR institutional repository copy of a peer-reviewed RE paper; rubric scored 41
- **Retrieved:** 2026-08-28

> Ambiguity in communication is often perceived as a major obstacle for knowledge transfer, which could...

## 621

- **Title:** otar/clarify-skill — Claude Code plugin, interrogates a request before any work starts
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://github.com/otar/clarify-skill](https://github.com/otar/clarify-skill)
- **Credibility:** adjudicated tier **T1-primary** (mechanical scorer: 41 / questionable) — the skill file/repo itself — primary for a claim about its own invocation posture
- **Retrieved:** 2026-08-28

> It interrogates your request with structured, clickable questions until it's unambiguous, before any work starts. [...] The skill leans toward asking — it surfaces borderline ambiguity rather than guessing.

## 622

- **Title:** What Makes Interruptions Disruptive? (Borst, Taatgen, van Rijn, CHI 2015)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://dl.acm.org/doi/10.1145/2702123.2702156](https://dl.acm.org/doi/10.1145/2702123.2702156)
- **Credibility:** adjudicated tier **T1-peer-reviewed** (mechanical scorer: 63 / verify) — ACM DL, CHI 2015 — peer-reviewed, highly cited
- **Retrieved:** 2026-08-28

> The experiments confirmed that problem state requirements are an important predictor for the disruptiveness of interruptions. This suggests that interfaces should be designed to a) interrupt users at low-problem state moments and b) maintain the problem state for the user when interrupted.

## 623

- **Title:** If Not Now, When?: The Effects of Interruption at Different Moments Within Task Execution (Adamczyk & Bailey, CHI 2004)
- **Cluster:** prior-art · **Type:** web
- **URL:** [https://www.interruptions.net/literature/Adamczyk-CHI04-p271-adamczyk.pdf](https://www.interruptions.net/literature/Adamczyk-CHI04-p271-adamczyk.pdf)
- **Credibility:** adjudicated tier **T1-peer-reviewed** (mechanical scorer: 41 / questionable) — CHI 2004 — peer-reviewed, foundational; hosted on interruptions.net, which the rubric scored 41
- **Retrieved:** 2026-08-28

> Our results show that different interruption moments have different impacts on user emotional state and positive social attribution, and suggest that a system could enable a user to maintain a high level of awareness while mitigating the disruptive effects of interruption.

