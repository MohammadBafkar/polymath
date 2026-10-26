---
name: terraform-state
description: Design Terraform state — remote backend, locking, state isolation/segmentation, drift detection, and safe import/move/rm operations without destroying live infra.
---

# terraform-state

> State is the most dangerous file in your infra: lose it, share it unlocked, or split it wrong and you reapply or destroy production. Design isolation and locking before scaling usage.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Setting up or restructuring Terraform state, backends, or workspaces.
- Concurrent applies clobber each other, blast radius is too large, or drift goes unnoticed.
- A workflow invokes `polymath-iac:terraform-state`.

Not this when: you are authoring a reusable module (`terraform-module`) or reviewing a specific plan (`polymath-cloud:plan-review`). This is about state topology and operations.

## Inputs

- Team size, environments, and the current state layout (monolithic? per-env?).
- The cloud/backend available (S3 with native lockfile locking, GCS, azurerm, HCP Terraform, …).
- State files hold secrets in plaintext: read structure and addresses, never quote values.

## Procedure

1. **Remote backend + locking**: store state remotely (S3 with native `use_lockfile` locking — DynamoDB locking is deprecated since Terraform 1.10 — GCS, azurerm, or HCP Terraform) with encryption and versioning; **never** local state for shared infra. Locking is non-negotiable for teams.
2. **Isolate state by blast radius**: separate state per environment (dev/stage/prod) and per independently-changing layer (network vs data vs app). A single giant state means every apply risks everything and serializes the team.
3. **Workspaces vs directories**: prefer separate root configs/dirs (or a tool like Terragrunt) for strong env isolation; CLI workspaces only for lightweight, low-risk variation — they share a backend and are easy to misfire.
4. **Drift detection**: scheduled `terraform plan -refresh-only` (or plain `plan`) to detect out-of-band changes; alert and reconcile. Decide the policy: codify the change or revert it — don't let drift accumulate.
5. **Safe state surgery** — prefer the config-driven blocks, which show up in `plan` and get code-reviewed: `import {}` to adopt existing resources, `moved {}` for renames/module moves (so Terraform doesn't destroy+recreate), `removed {}` to stop managing without destroying. Fall back to CLI `state mv` / `state rm` only when a block can't express it — and back up state (`terraform state pull > backup.tfstate`) first.
6. **Secrets in state**: assume state contains secrets — restrict backend access (least privilege), encrypt, and avoid outputs that leak them.
7. **Recovery**: state versioning/backups + a documented restore; protect against concurrent corruption.

## Output

```text
State design: payments infrastructure (AWS, 3 envs)

Backend:  S3 bucket per env (tfstate-payments-{dev,stage,prod}), SSE-KMS, versioning on, use_lockfile = true
Layout (one state per env × layer):
  envs/prod/network/   VPC, subnets, NAT            apply: platform team, 2 approvers
  envs/prod/data/      RDS, ElastiCache, S3 buckets  apply: platform team, 2 approvers, prevent_destroy on stores
  envs/prod/app/       ECS services, ALB rules, SQS  apply: payments team
  (dev and stage mirror the tree with their own buckets and credentials)
Drift:    nightly `terraform plan -refresh-only` per state → alert on any diff; policy: codify within 2 business days or revert
Surgery:  import {} / moved {} / removed {} blocks in a reviewed PR; CLI state mv/rm only after `terraform state pull > backup.tfstate`
Access:   prod state readable by the CI role and 3 named admins (state contains secrets); no human write outside CI
Recovery: restore from S3 object version; runbook docs/runbooks/terraform-state-restore.md, tested quarterly
```

## Quality bar

- Remote, encrypted, versioned backend with locking — no shared local state.
- State is segmented by environment and blast radius, not one monolith.
- Drift is detected on a cadence with a written reconcile policy.
- Refactors use `moved`/`import`/`removed` blocks (CLI state surgery only with a backup), never destroy+recreate of live infra.
