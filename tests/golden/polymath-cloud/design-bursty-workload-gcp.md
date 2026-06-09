---
plugin: polymath-cloud
scenario: design-bursty-workload
expect:
  invoked:
    - polymath-cloud:design-gcp-pattern
  output_matches:
    - "(Cloud Run|GKE|Cloud Functions)"
    - "(Firestore|Spanner|Cloud SQL|BigQuery)"
    - "(flip|runner.up|cold.start)"
timeout_seconds: 60
---

# Prompt

> Pick a GCP pattern for a bursty, stateless service that processes
> refund events. Peak ~500 RPS, idle most of the day.

Use polymath-cloud:design-gcp-pattern.

# Acceptance

- Workload characterized quantitatively.
- Primary + runner-up + flip conditions.
- Cost driver named.
- Ops shape (logs/tracing/errors) covered.
