# polymath-infra-cloud

Cloud infrastructure design craft for the Polymath marketplace. One
plugin with four sibling skills covering AWS, GCP, Azure, and
Terraform stack composition.

## What it ships

- **Skills:**
  - `design-aws-pattern` — pick the right AWS primitive (Lambda /
    ECS / EKS / EC2; S3 / EFS / FSx; RDS / Aurora / DynamoDB) with
    cost-driver + flip-condition framing.
  - `design-gcp-pattern` — Cloud Run / GKE / Cloud Functions; Cloud
    SQL / Spanner / Firestore; GCS — same decision-tree shape.
  - `design-azure-pattern` — App Service / Functions / Container
    Apps / AKS; Azure SQL / Cosmos / Postgres Flexible; Storage.
  - `design-stack-composition` — Terraform stack layout: blast-radius
    zones (foundational / platform / service), state backend choice,
    workspaces-vs-directories rule, per-apply RBAC.
- **Commands:** `/design-aws`, `/design-gcp`, `/design-azure`,
  `/design-terraform-stack` (thin aliases).

## Pairs with

- `polymath-infra-kubernetes` for k8s manifests when the runtime
  choice is Kubernetes.
- `polymath-infra-postgres` for migration safety on the DB choice.
- `polymath-connector-terraform` for plan-review when the IaC
  changes land.
- Official cloud CLI / MCP for actual operations (`aws`, `gcloud`,
  `az`). This plugin is design-tier; ops belongs in the official
  surfaces.

## Installation

```bash
claude plugin install polymath-infra-cloud@polymath
```

## Shape

Single capability (cloud-pattern selection) with four provider-flavoured
skills — `cloud-pattern-aws`, `cloud-pattern-gcp`, `cloud-pattern-azure`,
and a Terraform-stack composition skill — under one plugin. Projects pick
a cloud once via `.polymath/project.yaml`; the skills adapt rather than
splitting the surface across multiple plugins.

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** AWS / GCP / Azure / Terraform official docs and MCP families
- **Polymath value:** Cross-cloud pattern selection with named cost drivers + flip conditions
- **Sunset trigger:** Demote when an official multi-cloud design MCP ships per-provider decision trees.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

MIT.
