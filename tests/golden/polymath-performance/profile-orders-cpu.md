---
plugin: polymath-performance
scenario: profile-orders-cpu
expect:
  invoked:
    - polymath-performance:app-profiling
  output_matches:
    - "(flame graph|self time|share)"
    - "(one|single).{0,30}change"
    - "(verify|re-measure|baseline)"
timeout_seconds: 120
---

# Prompt

> Our orders service burns 62% CPU at 500 rps on 8 vCPU. I have an async-profiler flame graph where JSON serialization and Hibernate hydration are wide. What do we change first?

Use polymath-performance:app-profiling.

# Acceptance

- Picks the widest frame with expected gain bounded by its share.
- One change per iteration with re-measurement.
