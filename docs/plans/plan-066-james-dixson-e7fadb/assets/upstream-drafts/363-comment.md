---
type: Asset
okf_spec: OKF-PLAN
description: "Posted reconcile comment for upstream #363 (OKF-EXTENSION remediation) — POSTED and issue CLOSED 2026-09-07."
---
<!-- THE POSTED BODY IS EVERYTHING BELOW THIS COMMENT. The frontmatter above is
     bundle metadata (OKF REQ-OKF-003) and was NOT part of the upstream write:
     posted; #363 closed. -->

## Fixed in plan-066 — all three defect classes, across all three files

The root cause is one fact: **`OKF-EXTENSION.md` describes a migration that has since shipped**,
while still being written as a proposal.

- **3 stale `Status: DRAFT` banners** (`yf-plan`, `yf-research`, `yf-incubator`). Each said
  "Proposal only… the human ratification gate approves it before any implementation applies it."
  The gate approved it and the implementation landed in plan-029. All three now read **RATIFIED
  AND SHIPPED** and tell the reader to take the sections as behaviour.
  *(The three banners differ in their epic numbers — 3/6, 4/6, 5/6 — which an anchored edit caught
  rather than silently skipping two of the three files.)*
- **2 dangling symbols.** `seed_readme` is now **`seed_index`**; `HEADER_TEMPLATE` was **removed**
  along with the timestamped table it templated.
- **2 shipped-but-"open" decisions.** `OKF-RESEARCH` §5 still listed three sub-decisions "the
  ratification gate must confirm". All three are settled, and the outcomes are recorded inline as
  what the engine does today: the **bullet listing** (not a table); the `Phase` column carried
  **only in `log.md`**; and the rename fan-out **complete** — `index_manager.py` declares
  `INDEX_FILENAME = "index.md"` and `LOG_FILENAME = "log.md"`.

The partial-rename hazard that item warned about did not materialise.
