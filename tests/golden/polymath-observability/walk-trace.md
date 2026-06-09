---
plugin: polymath-observability
scenario: walk-trace
expect:
  invoked:
    - polymath-observability:trace-investigate
  output_matches:
    - "(trace.id|7a8b9c|span)"
    - "(offending|error|status_code)"
    - "(self.time|hypothesis|chain)"
timeout_seconds: 90
---

# Prompt

> Investigate Honeycomb trace 7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d on dataset refund-api.

Use polymath-observability:trace-investigate.

# Acceptance

- Span tree reconstructed via trace.parent_id (not flat list by timestamp).
- Offending span identified by ancestor walk, not by latest timestamp.
- Latency breakdown is by self-time, not total time.
- Hypothesis cites the specific attribute/span supporting it.
