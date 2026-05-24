---
plugin: polymath-connector-gcp
scenario: inspect-sql
expect:
  invoked:
    - polymath-connector-gcp:inspect-gcp-resource
  output_matches:
    - "(projects/|gcloud)"
    - "(test-iam-permissions|effective)"
    - "(audit|logging)"
timeout_seconds: 90
---

# Prompt

> Inspect projects/example-prod/locations/us-central1/instances/refund-db.

Use polymath-connector-gcp:inspect-gcp-resource.

# Acceptance

- Resource described (tier, backups, networking).
- Effective permissions surfaced via test-iam-permissions, not just bindings.
- Recent audit-log writes shown (list/get filtered out).
- Read-only — no create/update/delete commands invoked.
