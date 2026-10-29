---
plugin: polymath-database
scenario: db-triage-slow-checkout
expect:
  invoked:
    - polymath-database:db-performance-triage
  output_matches:
    - "(wait|IOPS|bottleneck)"
    - "(pg_stat_statements|total time|calls)"
    - "(one|single|dominant).{0,40}(fix|change|bottleneck)"
timeout_seconds: 120
---

# Prompt

> Checkout latency tripled since Tuesday's deploy. The orders Postgres is at 98% of provisioned IOPS but CPU is only 38%. Find what is actually wrong before we buy a bigger instance.

Use polymath-database:db-performance-triage.

# Acceptance

- Layers checked in order (host, connections, waits, workload) with the ones ruled out listed.
- Statements ranked by total time and calls/sec, not slowest single run.
- ONE dominant bottleneck and one first fix with a success metric.
- No live mutation run by the skill.
