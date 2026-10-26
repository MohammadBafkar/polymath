---
name: design-stack-composition
description: Design Terraform stack composition — module boundaries, state layout, workspace strategy, remote-state plumbing, blast radius per apply.
---

# design-stack-composition

> One big Terraform state is a foot-cannon; one stack per resource is unmanageable. Pick the right granularity. Output: module + state layout, with the blast radius of each apply named.

## When to use

- Greenfield: setting up Terraform from scratch.
- Brownfield: an oversized state is becoming a deployment risk.
- Multi-environment / multi-account / multi-region rollout planning.

## Procedure

1. **Identify blast-radius zones.** Group resources by "who is impacted if this `apply` goes wrong":
   - **Foundational** (rarely changes; impact: entire org) — VPC, accounts, KMS, IAM trust policies.
   - **Platform** (monthly; impact: multiple services) — EKS clusters, shared databases, service mesh.
   - **Service** (per-feature; impact: one service) — Lambdas, ECS services, SQS, app DBs.
2. **One state per blast-radius zone × environment.** A bad change to the foundational stack should never block a service deploy.
3. **State backend.** Remote state with locking: S3 with native lockfile locking (`use_lockfile = true`, Terraform ≥ 1.10 — DynamoDB locking is deprecated), GCS (built-in locking), AzureRM blob (lease). Separate buckets/containers — and credentials — per environment. Local state on `main` is a refusal-to-merge.
4. **Workspaces vs directories.**
   - **Directories (one root per env)** for dev/staging/prod — the default. CLI workspaces share one backend and one set of credentials, so they can't give prod stricter access than dev (HashiCorp's own guidance: workspaces don't fit deployments that need separate credentials and access controls).
   - **Workspaces** only for short-lived, genuinely identical copies (per-PR preview stacks, load-test clones) where shared credentials are acceptable.
5. **Module boundaries.** A module owns a *capability*, not a *primitive*. `network-vpc` (capability) over `aws-vpc` (primitive); the module composes VPC + subnets + routes + NAT.
6. **`required_providers` + version pinning.** Modules declare a lower bound plus major ceiling (`>= 5.20, < 6.0`, or `~> 5.20` — note `~> 5.0` allows any 5.x); root stacks commit `.terraform.lock.hcl`, which pins exact provider versions and hashes. Floating across rebuilds = surprise plan output.
7. **Remote-state references** (`terraform_remote_state`) only between adjacent zones — and prefer publishing the few needed outputs to a parameter store (SSM, Secret Manager, Key Vault) or `tfe_outputs`: `terraform_remote_state` grants the reader the *entire* upstream state, secrets included. Service stacks read platform outputs (cluster ID, DB endpoints); platform stacks read foundational outputs (VPC ID, KMS key ARN). Service stacks should not reach into another service's state.
8. **Per-apply blast radius.** Document for each stack:
   - What it owns.
   - What breaks if you destroy it.
   - Who can apply it (RBAC; foundational stacks usually require multi-approver).

## Output

```text
design-stack-composition: refund-platform on AWS

States (foundational → service)

  1. foundational/
       Owns:    VPC, subnets, NAT, route tables, KMS keys, IAM trust policies.
       Blast:   ENTIRE ORG — protect.
       Apply:   2-person review, manual trigger.
       Backend: s3://acme-tf-state/foundational/<account-id>/terraform.tfstate

  2. platform-shared/
       Owns:    EKS cluster, shared RDS (analytics), service mesh.
       Blast:   ALL SERVICES — coordinated rollouts.
       Apply:   platform team, weekly cadence.
       Reads:   terraform_remote_state.foundational.outputs.{vpc_id, kms_arn}

  3. service-refund/  ← one per service
       Owns:    Lambda functions, SQS, DynamoDB tables, per-service IAM roles.
       Blast:   refund service only.
       Apply:   refund team, per-PR via CI.
       Reads:   terraform_remote_state.platform_shared.outputs.{cluster_id, mesh_ca}

Environments
  envs/{dev,staging,prod}/<stack>/ — one root and one backend per env;
  prod backend and apply role reachable only from the prod pipeline.

Module boundaries
  /modules/network/vpc           VPC + subnets + NAT + route tables (capability).
  /modules/eks/cluster-with-addons  EKS + ALB controller + cert-manager + ExternalDNS.
  /modules/service/lambda-sqs    Lambda + SQS + DLQ + alarms (capability).

Provider pinning
  Modules: >= 5.20, < 6.0
  Root:    .terraform.lock.hcl committed (exact versions + hashes; bumped deliberately)

Anti-foot-cannon checks
  ✓ No service stack references another service's state.
  ✓ Foundational state is RO from platform; platform state RO from service.
  ✓ All states locked (S3 native lockfile).
  ✗ Currently dev shares the prod backend bucket — separate buckets and credentials per env.
```

## Quality bar

- Stack boundaries match blast-radius zones, not org-chart boundaries.
- Remote state references go one direction (foundational → platform → service), never sideways.
- Workspaces vs directories chosen on structural divergence, not feature.
- RBAC for `apply` matches the blast radius.

## Anti-patterns to avoid

- One big monolithic state for the whole org. Apply takes minutes, blast radius is everything.
- One state per resource. State plumbing eats all the time you saved.
- CLI workspaces for dev/staging/prod — one backend and one credential set for every environment.
- Reading sibling services' remote state. Tight coupling masquerading as composition.
