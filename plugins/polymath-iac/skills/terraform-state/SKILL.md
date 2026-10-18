---
name: terraform-state
description: Design Terraform state — remote backend, locking, state isolation/segmentation, drift detection, and safe import/move/rm operations without destroying live infra.
---

# terraform-state

> State is the most dangerous file in your infra: lose it, share it unlocked, or split it wrong and you reapply or destroy production. Design isolation and locking before scaling usage.

## When to use

- Setting up or restructuring Terraform state, backends, or workspaces.
- Concurrent applies clobber each other, blast radius is too large, or drift goes unnoticed.
- A workflow invokes `polymath-iac:terraform-state`.

Not this when: you are authoring a reusable module (`terraform-module`) or reviewing a specific plan (`polymath-cloud:plan-review`). This is about state topology and operations.

## Inputs

- Team size, environments, and the current state layout (monolithic? per-env?).
- The cloud/backend available (S3+DynamoDB, GCS, Terraform Cloud, etc.).

## Procedure

1. **Remote backend + locking**: store state remotely (S3+DynamoDB lock, GCS, azurerm, or TF Cloud) with encryption and versioning; **never** local state for shared infra. Locking is non-negotiable for teams.
2. **Isolate state by blast radius**: separate state per environment (dev/stage/prod) and per independently-changing layer (network vs data vs app). A single giant state means every apply risks everything and serializes the team.
3. **Workspaces vs directories**: prefer separate root configs/dirs (or a tool like Terragrunt) for strong env isolation; CLI workspaces only for lightweight, low-risk variation — they share a backend and are easy to misfire.
4. **Drift detection**: scheduled `terraform plan` to detect out-of-band changes; alert and reconcile. Decide the policy: codify the change or revert it — don't let drift accumulate.
5. **Safe state surgery**: `import` to bring existing resources under management; `state mv` for refactors (renames/module moves) so Terraform doesn't destroy+recreate; `state rm` to stop managing without destroying. Always plan and back up state first.
6. **Secrets in state**: assume state contains secrets — restrict backend access (least privilege), encrypt, and avoid outputs that leak them.
7. **Recovery**: state versioning/backups + a documented restore; protect against concurrent corruption.

## Output

- A one-page state design: backend + locking choice, the state segmentation (per env/layer) with blast-radius rationale, drift-detection cadence + policy, the import/move/rm runbook, access controls, and the recovery plan.

## Quality bar

- Remote, encrypted, versioned backend with locking — no shared local state.
- State is segmented by environment and blast radius, not one monolith.
- Drift is detected on a cadence with a written reconcile policy.
- Refactors use `state mv`/`import` (plan + backup first), never destroy+recreate of live infra.
