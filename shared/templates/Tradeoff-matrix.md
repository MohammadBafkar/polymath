---
artifact: TradeoffMatrix
schemaVersion: 0.1
title: "{{title}}"
owner: "{{owner}}"
created: "{{date}}"
---

# Tradeoff matrix: {{title}}

## Question

The decision being made, in one sentence. ("Pick the rate-limit backing
store.")

## Criteria

Pick 3–6 criteria that genuinely differentiate the options. Each criterion
has a weight (1–5; higher = more important). Document the weight rationale
in one line per criterion.

| Criterion | Weight | Rationale |
| --------- | ------ | --------- |
| Latency (P99) | 5 | Hot path; user-visible. |
| Operational burden | 4 | Small team; supportability matters. |
| Cost (monthly) | 3 | Material but not load-bearing. |
| Time to ship | 3 | Sprint commitment. |
| Cross-team buy-in | 2 | Existing infra. |

## Options × criteria

Score each option 1–5 per criterion. Weighted score = Σ(weight × score).
Show the math; don't hide a heuristic behind a single number.

| Option | Latency (×5) | Op burden (×4) | Cost (×3) | TTM (×3) | Buy-in (×2) | **Total** |
| ------ | ------------ | -------------- | --------- | -------- | ----------- | --------- |
| A. In-memory | 5 × 5 = 25 | 5 × 4 = 20 | 5 × 3 = 15 | 5 × 3 = 15 | 5 × 2 = 10 | **85** |
| B. Redis    | 5 × 5 = 25 | 3 × 4 = 12 | 4 × 3 = 12 | 4 × 3 = 12 | 4 × 2 = 8  | **69** |
| C. Postgres | 3 × 5 = 15 | 4 × 4 = 16 | 3 × 3 = 9  | 4 × 3 = 12 | 5 × 2 = 10 | **62** |

## Discussion

Where the numeric ranking doesn't match the gut call, name the tie-breaker.

- Option A scores highest but doesn't survive multiple instances; rejected on
  the "shared state across replicas" requirement (not captured in the matrix —
  noted now).
- Option B is the recommended path.
- Option C: rejected for latency. Revisit if we need durable counters.

## Recommendation

**Option B — Redis.** One sentence on why this wins after the discussion.

## What would change the answer?

If <X> happened, we'd revisit and pick <Y>. Useful for the next person.

## References

- ADR link (this matrix likely becomes the Alternatives section of an ADR).
- PRD / RFC links.
