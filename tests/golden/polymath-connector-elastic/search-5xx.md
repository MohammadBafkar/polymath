---
plugin: polymath-connector-elastic
scenario: search-5xx
expect:
  invoked:
    - polymath-connector-elastic:log-search
  output_matches:
    - "(logs-prod|index)"
    - "(http.response|status_code|bucket)"
    - "(trace.id|sample|relation)"
timeout_seconds: 90
---

# Prompt

> Search logs-prod-refund-* between 2026-05-23T14:00Z and 14:30Z for
> service.name:"refund-api" AND http.response.status_code >= 500.
> Bucket by status code and trace.id.

Use polymath-connector-elastic:log-search.

# Acceptance

- Index pattern is explicit, not `*`.
- Time range is explicit (gte + lte).
- Total count includes relation (exact vs. gte).
- Top buckets returned; sample capped at 10 with PII fields redacted.
- Cross-index hint surfaced when trace.id concentrates.
