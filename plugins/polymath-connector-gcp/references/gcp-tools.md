# GCP CLI reference

This connector wraps the local `gcloud` CLI; no remote MCP. Auth is the user's existing `gcloud` configuration (ADC + active account).

## Auth model

- `gcloud auth login` for user accounts.
- `gcloud auth application-default login` for ADC (used by client libraries).
- `gcloud auth activate-service-account --key-file=…` for headless contexts; do not embed key paths in repo files.
- Workload Identity Federation preferred for CI / runners (no key files).

## Read-side commands used

- `gcloud storage buckets describe`
- `gcloud compute instances describe / describe-iam-policy`
- `gcloud sql instances describe`
- `gcloud container clusters describe`
- `gcloud pubsub topics/subscriptions describe`
- `gcloud functions describe`
- `gcloud <service> get-iam-policy`
- `gcloud projects test-iam-permissions`
- `gcloud logging read`

## What this connector does NOT do

- It does not call mutating verbs (`create`, `update`, `delete`, `set-iam-policy`). Mutation is delegated to `polymath-infra-gcp` (write-side IaC).
- It does not issue tokens. Auth is the user's existing `gcloud` session.
- It does not span projects. Each inspection runs within one project; cross-project analysis is multiple invocations.

## Common pitfalls

- `gcloud` global `--project` flag overrides `userConfig.gcpProject` for one call but not subsequent ones; chained calls must each pass `--project` explicitly or rely on the active config.
- `get-iam-policy` returns *direct* bindings; conditional bindings (`condition.expression`) need separate evaluation.
- Audit-log queries pay per-byte; tight filters (`resourceName`, `methodName`) and short `--freshness` are required to avoid runaway scans.
- "Buckets" are global; "instances" / "clusters" / "subnets" are regional. Region-required commands without `--region` fail with confusing errors.
