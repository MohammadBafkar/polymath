---
plugin: polymath-connector-aws
scenario: inspect-bucket
expect:
  invoked:
    - polymath-connector-aws:inspect-aws-resource
  output_matches:
    - "(arn:aws:s3|bucket)"
    - "(simulate.principal|effective)"
    - "(cloudtrail|cost)"
timeout_seconds: 90
---

# Prompt

> Inspect arn:aws:s3:::example-prod-uploads in profile prod-payments.

Use polymath-connector-aws:inspect-aws-resource.

# Acceptance

- Resource described (creation, encryption, public-access-block).
- Effective write principals enumerated via simulate-principal-policy (not raw policy JSON).
- Recent CloudTrail events surfaced.
- 7-day cost shown (or explicitly noted unavailable).
- Read-only — no put-/update-/delete- commands invoked.
