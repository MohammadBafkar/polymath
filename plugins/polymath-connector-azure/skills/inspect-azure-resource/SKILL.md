---
name: inspect-azure-resource
description: Inspect an Azure resource by ARM ID — describe, role-assignments + can-i probe, recent activity-log writes, cost ping. Read-only.
---

# inspect-azure-resource

> Read-only inspection of a single Azure resource. Output: state, who has effective access, recent activity-log writes, cost ping.

## When to use

- An incident points at a specific Azure resource and the on-call needs the facts.
- A PRD names a resource and you want to verify config + access.
- A compliance review on a single resource.

## Inputs

- ARM resource ID (required) — `/subscriptions/<sub>/resourceGroups/<rg>/providers/<provider>/<type>/<name>`.
- Subscription (optional) — fall back to `userConfig.azureSubscription` if not derivable from the ID.

## Procedure

1. **Parse the ARM ID** for subscription, resource group, provider, type, name. Refuse partial IDs.
2. **Switch to the right subscription** with `az account set --subscription <sub>` (per-call, do not assume the global default matches).
3. **Describe via `az resource show`** by default; for resources with richer typed commands, prefer those (`az storage account show`, `az sql server show`, `az aks show`, `az functionapp show`, `az keyvault show`).
4. **Role assignments.** `az role assignment list --scope <arm-id>`. Translate into a `<principal>: [roles]` map.
5. **Effective access (can-i probe).** `az role assignment list --assignee <principal> --scope <arm-id>` for the principal of interest; cross-check with `az role definition show` for what each role actually permits.
6. **Recent activity-log writes.** `az monitor activity-log list --resource-id <arm-id> --max-events 10 --status Succeeded --offset 24h`. Filter out reads; surface writes.
7. **Cost ping.** `az consumption usage list --start-date <…> --end-date <…> --query "[?contains(instanceId,'<short-name>')]"`. Skip if the subscription does not surface per-resource cost.
8. **Output** a one-screen summary.

## Output

```text
inspect-azure-resource

ARM ID:    /subscriptions/abc.../resourceGroups/refund-prod/providers/Microsoft.Sql/servers/refund-sql/databases/refund
Type:      Microsoft.Sql/servers/databases
RG:        refund-prod
Location:  eastus

State
  SKU:           S3 (Standard)
  Backup:        geo-redundant
  Public endpoint: disabled (private link only)

Role assignments (scoped to this resource)
  group:Platform-Eng                  → Contributor
  servicePrincipal:refund-api         → SQL DB Contributor
  user:alex@example.com               → SQL DB Reader

Effective access (current principal = alex@example.com)
  Microsoft.Sql/servers/databases/read              ALLOWED
  Microsoft.Sql/servers/databases/write             DENIED
  Microsoft.Sql/servers/databases/delete            DENIED

Recent activity log writes (24h)
  - 2026-05-23 14:12 Microsoft.Sql/servers/databases/write
                     by refund-api (sp object id ...)
  - 2026-05-22 09:01 Microsoft.Sql/servers/firewallRules/write
                     by alex@example.com

Cost (last 7d)
  $128.40  Microsoft.Sql/servers/databases (this DB)
```

## Quality bar

- ARM ID is complete (subscription + RG + provider + type + name).
- Subscription explicitly switched before resource calls.
- Effective access shown per principal, not raw role-assignment listing.
- Read-only — no `az … create|update|delete` calls.

## Anti-patterns to avoid

- Trusting the active subscription. `az account set` per call; the user's default may be wrong.
- Reading role assignments and stopping. Roles need to be resolved to the actions they grant for an honest answer.
- Treating Azure RBAC as the only access surface — resource-specific firewalls (SQL server firewall rules, Key Vault access policies) gate access independently.
- Logging the cost ping result alongside subscription numbers. Cost data carries financial signal; share with care.
