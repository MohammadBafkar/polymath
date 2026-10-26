# Changelog — polymath-data

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `run-experiment`: duration formula divided wrongly by the traffic fraction; the worked example's sample size was ~28× too large; percentile metrics need the delta method/bootstrap; success no longer means "crossed the MDE"; added no-peeking/sequential and sample-ratio-mismatch checks.
- `sql-optimize`: `EXPLAIN ANALYZE` executes the query (DML in a rolled-back transaction, prod caution); plan reading is leaf-first in every dialect with per-loop, child-inclusive timings; `Rows Removed by Filter` belongs to scans.
- `sql-write`: sargable predicates instead of "indexed predicates first"; `NOT IN`/NULL and time-zone traps; agent-run queries are read-only, DML only on approval.
- `metrics-tree`: funnel stages multiply, disjoint segments add (the anti-pattern contradicted the example); session leaf counted users; baselines are never invented.

## [0.8.0]

Data craft: SQL authoring, plan-based optimization, metrics-tree decomposition.

### Skills

- **metrics-tree** — Decompose a North Star metric into a tree of input metrics so each team can see the lever they own; output is a tree, not a dashboard.
- **run-experiment** — Plan an A/B (or A/B/n) experiment — hypothesis, primary + guardrail metrics, MDE + sample size + duration, randomization, stop conditions.
- **sql-optimize** — Read EXPLAIN ANALYZE output and propose targeted optimizations — index, predicate, join order, or query shape changes.
- **sql-write** — Write a SQL query that answers a specific question; parameterized, dialect-aware, readable, with the assumed schema documented inline.
