# Changelog — polymath-data

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Data craft: SQL authoring, plan-based optimization, metrics-tree decomposition.

### Skills

- **metrics-tree** — Decompose a North Star metric into a tree of input metrics so each team can see the lever they own; output is a tree, not a dashboard.
- **run-experiment** — Plan an A/B (or A/B/n) experiment — hypothesis, primary + guardrail metrics, MDE + sample size + duration, randomization, stop conditions.
- **sql-optimize** — Read EXPLAIN ANALYZE output and propose targeted optimizations — index, predicate, join order, or query shape changes.
- **sql-write** — Write a SQL query that answers a specific question; parameterized, dialect-aware, readable, with the assumed schema documented inline.
