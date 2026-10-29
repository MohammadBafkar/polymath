---
plugin: polymath-performance
scenario: high-load-io-gateway
expect:
  invoked:
    - polymath-performance:high-load-io-design
  output_matches:
    - "(Little|in flight|concurrency)"
    - "(backpressure|shed|503|429)"
    - "(timeout|deadline)"
timeout_seconds: 120
---

# Prompt

> Our upload gateway must do 4,000 req/s with p99 under 300ms, each request waits ~40ms on storage and a metadata DB. How do I size the pools and threads and keep it from falling over under overload?

Use polymath-performance:high-load-io-design.

# Acceptance

- Runs concurrency.py for pool/thread sizing.
- Bounded queues and pools aligned with downstream limits.
- Open-loop load test plan.
