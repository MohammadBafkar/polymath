---
plugin: polymath-connector-azure
scenario: inspect-sql
expect:
  invoked:
    - polymath-connector-azure:inspect-azure-resource
  output_matches:
    - "(/subscriptions/|ARM)"
    - "(role assignment|effective|can.i)"
    - "(activity.log|consumption|cost)"
timeout_seconds: 90
---

# Prompt

> Inspect the SQL database at
> /subscriptions/abc.../resourceGroups/refund-prod/providers/Microsoft.Sql/servers/refund-sql/databases/refund.

Use polymath-connector-azure:inspect-azure-resource.

# Acceptance

- Resource described (SKU, backup, networking).
- Role assignments enumerated by principal.
- Effective access probed via role-definition resolution, not just listing.
- Recent activity-log writes shown.
- Read-only — no create/update/delete commands invoked.
