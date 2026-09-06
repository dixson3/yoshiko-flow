---
type: Escalation
okf_spec: OKF-PLAN
description: Open questions raised to the upstream controller during execution, with
  alternatives, a recommended default, and what happens if no answer arrives.
---
# Escalations

Questions this plan raised to its upstream controller, newest last. Each `## ESC-NNN` section
is one entry; `ESC-NNN` ids are append-only and are never reused or renumbered.

**The architecture is WRITE-THEN-NOTIFY, never ask-and-await.** The herdr channel has no
answer-return primitive, so the escalation IS this artifact and any push is merely a
notification about it. That is why `on_no_answer` is required on every entry: an escalation
that omits its own default pretends to a round-trip the transport cannot deliver.

`recommended` is stored SEPARATELY from `answer`, and the separation is the point. The
dominant operator input across the corpus is a choice among stated alternatives, and a schema
that records only the resolution destroys the default it was chosen against.

An escalation whose recommended default was taken **without an answer arriving** is
`resolved`, not `raised` — with `answer` recording the default that was taken. Leaving it
`raised` would make every fire-and-forget escalation trip the close-time open-escalation
warning, which would train a reader to ignore it.

## ESC-001

| Field | Value |
| :-- | :-- |
| `question` | SC3 requires okf-index-drift green over the WHOLE corpus, but no enumerated issue reindexes the 8 transformed bundles — Issue 5.2b is scoped to plan-065's own bundle only. Reindex the 8 as implied work, or leave SC3 red? |
| `alternatives` | Reindex the 8 transformed bundles (auto-derived descriptions) plus plan-065, as a separate commit after the backfill; Leave SC3 red and file it as a follow-on |
| `recommended` | Reindex the 8 transformed bundles (auto-derived descriptions) plus plan-065, as a separate commit after the backfill |
| `on_no_answer` | Take the recommended option: reindex all 9 drifting bundles. Measured: reindex --apply derives REAL descriptions from each member's frontmatter (verified on a plan-030 copy), so 5.2b's bare-bullet hazard applies only to plan-065's own frontmatter-less .json artifacts, which are hand-authored. The backfill's revert boundary 250aace stays intact; rollback becomes revert-both-in-reverse-order. |
| `detected_by` | self-report |
| `evidence` | check_okf_index_drift.py --min-roots 30: no_index 0 (SC3's added conjunct MET) but drifting 9, exit 1 — the 8 newly-transformed bundles plus plan-065. The transform's delete-renamed-README.md-prose step drops the README's ## File map, so every transformed index.md has no member listing. |
| `asked_of` |  |
| `state` | resolved |
| `answer` | ENDORSED by the upstream controller: reindex all 9 drifting bundles — done; index-drift-strict now exits 0 (no_index 0, drifting 0). The controller reached the same finding independently from the other side: plan-010/index.md at 368 bytes asserting 'a cold reader understands its purpose, environment and history from the files below alone' followed by NO FILES — a generated index that promises a listing and omits it is self-refuting on its face. PLUS the half this session did not draw: the root cause is a FIFTH ENGINE DEFECT and must be FILED, not merely worked around. okf_hygiene.py backfill --apply generates a NON-CONFORMANT index.md (header and objective only, no member listing), so every freshly transformed bundle immediately fails check_okf_index_drift.py — measured across all 8 bundles; repaired post-hoc by reindex --apply. Reindexing fixes the SYMPTOM in this corpus; the engine reproduces it for every future backfill in every repo that installs the skill. A SIXTH defect found alongside: the reindex dry run reports verdict=clean, exit=0 while proposing 9 add-missing changes — a verdict that disagrees with its own change list, the saturating-label failure in a new place. Consequence: SC10 says 'All FOUR' and names the fourth explicitly, so as written it would PASS while dropping two; amend SC10 to six and name each. Filing remains gated on yf-mol-e7k4.10; all six are drafted into findings/upstream-drafts.md by Issue 5.6 and no further. |
| `raised_when` | 2026-09-05 |
| `resolved_when` | 2026-09-05 |
| `no_answer_taken` | no |
| `push_batch` | 20260905T180650-1 |

