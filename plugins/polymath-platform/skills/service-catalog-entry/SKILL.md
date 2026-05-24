---
name: service-catalog-entry
description: Author a service-catalog entry (Backstage/Cortex-shaped) — owner, tier, runbooks, dashboards, dependencies; populates catalog-info.yaml.
---

# service-catalog-entry

> Write a service catalog entry that's good enough for on-call to find what they need at 3am.

## When to use

- A new service is being onboarded onto the platform.
- An existing service has a stale or missing catalog entry.
- A workflow includes a "register service" step.

## Inputs

- Service name + one-sentence purpose.
- Repo URL.
- Owning team (a team handle, not a person).
- The runbooks / dashboards / alerts that already exist.

## Procedure

1. **Identity**:
   - `name`: kebab-case, globally unique within the org.
   - `title`: human-readable.
   - `description`: one sentence — what does this service do for which users.
2. **Owner** — a team, never a person.
3. **Tier** — pin one (Tier 1 = customer impact if down; Tier 2 = degraded UX; Tier 3 = internal-only). Tier drives on-call expectations and SLO targets.
4. **System** — the larger system this service belongs to (a few services together).
5. **Lifecycle** — `experimental`, `production`, `deprecated`. Stale "experimental" services pile up; review yearly.
6. **Dependencies** — what this service depends on. Both API dependencies and infrastructure (a queue, a database).
7. **Links** — runbook, dashboard, alert source, on-call rotation, error budget board. If a link doesn't exist, write the runbook before adopting the entry.

## Output (Backstage-shape, but the fields generalize)

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: refund-service
  title: Refund Service
  description: Initiates and tracks customer refunds via the Stripe API.
  tags: [tier-1, payments, golang]
  annotations:
    backstage.io/source-location: url:https://github.com/example/refund-service
    pagerduty.com/integration-key: <id>
  links:
    - url: https://runbooks.example/refund-service
      title: Runbook
      icon: docs
    - url: https://grafana.example/d/refund-service
      title: Dashboard
      icon: dashboard
spec:
  type: service
  lifecycle: production
  owner: team-payments
  system: payments
  providesApis: [refund-v1]
  dependsOn:
    - resource:default/postgres-refunds
    - component:default/notifications
```

## Quality bar

- Every Tier-1 service has a runbook URL that resolves.
- Owner is a team handle that has on-call rotation.
- Dependencies are accurate — out-of-date dependency lists are worse than missing ones.

## Anti-patterns to avoid

- Person owners ("alice@…"). People leave.
- "Tier" missing or `"`tbd`"`.
- `lifecycle: experimental` on services that have been in prod for 2 years.
