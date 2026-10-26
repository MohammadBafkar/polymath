# Changelog — polymath-cloud

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `design-aws-pattern`: cost example was ~20× low — now shown as arithmetic with assumptions; Lambda tree no longer equates "< 100 ms" with Lambda (cold starts); Timestream for LiveAnalytics is closed to new customers.
- `design-azure-pattern`: Cosmos DB strong consistency is not available with multi-region writes, and Azure SQL has no "multi-write groups"; added When-to-use and Quality bar.
- `design-gcp-pattern`: Cloud Run functions naming, Direct VPC egress, no hard-coded Cloud SQL limit; added When-to-use and Quality bar.
- `design-stack-composition`: S3 native lockfile locking (DynamoDB locking is deprecated), one root/backend per environment instead of CLI workspaces, `~> 5.0` semantics corrected, `.terraform.lock.hcl`, `terraform_remote_state` exposes the whole state.
- `plan-review`: the JSON plan holds sensitive values in plaintext — never echo them; drift comes from `resource_drift`; `read`/`forget` actions, `action_reason`/`replace_paths`; `${terraformBinary}` (never substituted) replaced.
- `cloud-cost-review`: Output shape and a no-mutation rule.

## [0.8.0]

Cloud infrastructure design craft: pattern selection across AWS, GCP, Azure + Terraform stack composition.

### Skills

- **cloud-cost-review** — Review cloud spend — rightsizing/waste, cost budgets + anomaly alerts, unit economics (cost per request/tenant), reserved coverage. Cloud cost, not internal token budgets (plugin-budget).
- **design-aws-pattern** — Pick the right AWS primitive for a workload — compute (Lambda/ECS/EKS/EC2), storage (S3/EFS/FSx), database (RDS/Aurora/DynamoDB) with cost + ops + scale tradeoffs.
- **design-azure-pattern** — Pick the right Azure primitive — compute (Functions / Container Apps / App Service / AKS), database (Azure SQL / Cosmos DB / Postgres Flex), storage (Blob / Files / Disk).
- **design-gcp-pattern** — Pick the right GCP primitive — compute (Cloud Run / GKE / Functions / GCE), database (Cloud SQL / Spanner / Firestore / Bigtable), storage (GCS) with cost + ops + scale tradeoffs.
- **design-stack-composition** — Design Terraform stack composition — module boundaries, state layout, workspace strategy, remote-state plumbing, blast radius per apply.
- **plan-review** — Read a terraform plan (binary or JSON) and surface destructive actions, drift, and unsafe diffs before apply.

### Commands

- **/design-aws** — Pick an AWS pattern for a workload — compute, storage, database, networking, cost, ops, flip conditions.
- **/design-azure** — Pick an Azure pattern for a workload — compute, database, storage, messaging, networking, cost, ops.
- **/design-gcp** — Pick a GCP pattern for a workload — compute, database, storage, messaging, networking, cost, ops, flip conditions.
- **/design-terraform-stack** — Design Terraform module and state layout up front; command entry point for the design-terraform-stack skill.
