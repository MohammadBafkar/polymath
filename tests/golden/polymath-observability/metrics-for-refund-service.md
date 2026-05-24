---
plugin: polymath-observability
scenario: metrics-for-refund-service
expect:
  invoked:
    - polymath-observability:metrics-design
  output_matches:
    - "RED"
    - "USE"
    - "histogram"
    - "(cardinality|forbidden|user_id)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Design metrics for our refund-service.

Use polymath-observability:metrics-design. Service exposes
POST /v1/orders/{id}/refunds and depends on Postgres + Stripe.
SLO target: P99 < 500ms.

# Acceptance

- RED metrics for the service (rate, errors, duration).
- USE metrics for the Postgres pool and the Stripe client.
- Latency is a histogram (not a summary).
- Histogram bucket choice covers the SLO threshold (≤ 500ms).
- A cardinality budget + a forbidden-labels list is named.
- An SLI-to-metric mapping is included.
