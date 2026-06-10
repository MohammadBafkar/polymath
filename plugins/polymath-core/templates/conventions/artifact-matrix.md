# Artifact matrix — {{org_or_project}}

> The single reference for which artifacts a piece of work requires, by
> work type and scope. When in doubt, size up — over-specifying is cheaper
> than implementing without guardrails and discovering the gap in review.

## Matrix

| Work type | Scope | Required artifacts |
|-----------|-------|--------------------|
| Bug | S/M | Ticket only |
| Bug | L/XL | {{artifacts}} |
| New feature | S/M | {{artifacts}} |
| New feature | L/XL | {{artifacts}} |
| Refactoring | — | {{artifacts}} |
| {{work_type}} | {{scope}} | {{artifacts}} |

## Decision rules

When the matrix leaves ambiguity:

1. **Behaviour, architecture, or data changes → {{requirements_artifact}}.**
2. **Module boundaries, API contracts, or data models → {{architecture_artifact}}.**
3. **Significant UI/UX changes → {{design_artifact}}.** "Significant" means
   a designer would need to specify it.

## Scope sizing

| Signal | Likely scope |
|--------|--------------|
| Single screen/endpoint, no data-model change | S/M |
| New user-facing capability with UI + backend | L/XL |
| New data-model entity or significant schema change | L/XL |
| Multiple modules or integration points | L/XL |
| Ambiguous — could be either | L/XL (size up) |

## Approval gates

An artifact is complete only with the right status and approvers; draft
artifacts do not unlock downstream work.

| Artifact | Status when complete | Required approvers |
|----------|---------------------|--------------------|
| {{artifact}} | {{status}} | {{approvers}} |
