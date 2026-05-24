---
artifact: OKR
schemaVersion: 0.1
title: "{{title}}"
owner: "{{owner}}"
cycle: "{{cycle}}"
status: draft
created: "{{date}}"
---

# OKRs — {{title}} ({{cycle}})

> Andy Grove's OKR. **Objective** is qualitative + ambitious. **Key Results**
> are measurable and time-boxed; they prove the objective happened. 3–5 KRs
> per Objective; more than 5 = the objective is fuzzy.

## Objective

A one-sentence, qualitative, ambitious goal. Not a task; not a metric.

> {{objective}}

Test: would you describe success at the end of the cycle using these words?

## Key Results

Each KR is a number we can measure on day 1 and day N. Verb + metric +
target + deadline.

| # | Key Result | Baseline (day 0) | Target | Confidence (0.0–1.0) |
| - | ---------- | ---------------- | ------ | -------------------- |
| 1 | … | … | … | 0.5 |
| 2 | … | … | … | 0.3 |
| 3 | … | … | … | 0.7 |

Confidence updated weekly. Track the delta, not just the absolute number.

## Sandbagging guard

If every KR is at 0.9 confidence at start, the OKRs are too easy. Aim for
an average of ~0.5–0.7 across the set. "Bet" KRs at 0.3–0.5 are healthy.

## Anti-OKRs (out of scope)

What we explicitly are NOT trying to do this cycle. Prevents scope creep.

- …
- …

## Initiatives (what we'll do)

The work that moves KRs. KRs are outcomes; initiatives are output. Don't
confuse them.

- Initiative → KR mapping:
  - <initiative> → KR #1
  - <initiative> → KR #2

## Review cadence

- Weekly: confidence update; flag anything below 0.3 on a "bet" KR.
- Mid-cycle: re-score; cancel non-moving initiatives.
- End-of-cycle: grade (0.0–1.0 per KR); write the retro before the next set.
