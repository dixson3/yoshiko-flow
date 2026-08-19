**Red-team pass 99 — a deliberately malformed review report.**

No `#` or `##` heading anywhere, so `review/has-heading` (the type's one error-severity
check) fails. It also declares no verdict and carries none of the five body sections —
both report-only, because a review report is authored while the plan sits at `review`,
which is exactly where `STATUS_SEVERITY` would promote them.
