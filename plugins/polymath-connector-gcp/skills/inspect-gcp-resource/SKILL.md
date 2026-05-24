---
name: inspect-gcp-resource
description: Inspect a GCP resource by full resource path — describe, IAM policy + testIamPermissions, recent audit logs, cost ping. Read-only.
---

# inspect-gcp-resource

> Read-only inspection of a single GCP resource. Output: state, who has effective access, recent audit-log events, and a cost ping.

## When to use

- An incident points at a GCS bucket / GKE cluster / Cloud SQL instance and the on-call needs the facts.
- A PRD references a resource by URL and you want to verify it exists with the expected config.
- A compliance review on a single resource.

## Inputs

- Resource path (required) — full canonical path: `projects/<id>/locations/<region>/<type>/<name>` (e.g. `projects/example-prod/locations/us-central1/instances/refund-db`).
- Project + region (optional) — fall back to `userConfig.gcpProject` + `userConfig.gcpRegion` if the path is partial.

## Procedure

1. **Parse the resource path** to extract project, location, type, name. Refuse vague names without project (collision risk across orgs).
2. **Describe via the type's `describe` verb.** Map:
   - `storage.bucket` → `gcloud storage buckets describe gs://<name>`.
   - `compute.instance` → `gcloud compute instances describe <name> --zone=<z>`.
   - `sql.instance` → `gcloud sql instances describe <name>`.
   - `container.cluster` (GKE) → `gcloud container clusters describe <name> --region=<r>`.
   - `pubsub.topic` / `subscription` → `gcloud pubsub topics describe <name>`.
   - `cloudfunctions.function` → `gcloud functions describe <name> --region=<r>`.
3. **IAM policy.** `gcloud <service> get-iam-policy <resource>`. Translate bindings into a `<principal>: [roles]` map.
4. **Effective permissions.** `gcloud projects test-iam-permissions <project> --permissions=<list>` for the principal of interest (default: the active credential's principal). Returns the subset actually granted.
5. **Recent audit logs.** `gcloud logging read 'protoPayload.resourceName="<path>" AND protoPayload.methodName!~"^google.*\\.list"' --limit=10 --freshness=24h`. Filter list/get calls; show writes.
6. **Cost ping.** `gcloud billing accounts list` then `gcloud alpha billing budgets list` for budgets attached to the project (per-resource cost via BigQuery export — skip if not configured; do not block).
7. **Output** a one-screen summary.

## Output

```text
inspect-gcp-resource

Resource:     projects/example-prod/locations/us-central1/instances/refund-db
Type:         sql.instance
Project:      example-prod

State
  Created:    2024-08-19
  Tier:       db-custom-2-7680
  Backups:    enabled (point-in-time recovery on)
  Public IP:  disabled, private-network-only

IAM (effective)
  group:platform-engineering@example.com    → roles/cloudsql.admin
  serviceAccount:refund-api@…iam            → roles/cloudsql.client
  user:alex@example.com                     → roles/cloudsql.viewer

Effective permissions (current principal = alex@example.com)
  cloudsql.instances.connect                ALLOWED
  cloudsql.instances.update                 DENIED
  cloudsql.instances.delete                 DENIED

Recent audit log writes (24h)
  - 2026-05-23 14:08 cloudsql.instances.patch by refund-api@…iam
  - 2026-05-22 09:01 cloudsql.users.create   by terraform@…iam

Cost ping
  Budget alerts attached: 1 ($800/mo, 78% consumed).
  Per-resource cost: enable BigQuery billing export for granular numbers.
```

## Quality bar

- Full resource path used (project + location + type + name).
- Effective permissions reported via `test-iam-permissions`, not raw policy bindings.
- Audit-log query excludes list/get; only mutations surface.
- Read-only — no `gcloud … create|update|delete` calls.

## Anti-patterns to avoid

- Querying with just a name. Cross-project name collisions exist; project must be explicit.
- Reading the IAM policy text and stopping there. Org policies and conditional bindings affect the effective answer.
- Treating "no audit logs in 24h" as "no recent change". Audit logs honor sample-rate config; some categories are off by default.
- Mixing `gcloud` with `bq` for cost when BigQuery billing export is not set up. Surface "not configured" rather than guessing.
