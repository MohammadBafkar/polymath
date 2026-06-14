# Changelog — polymath-iac

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Infrastructure-as-Code authoring: reusable Terraform modules, state/backends/drift, policy-as-code guardrails (OPA/Sentinel/Checkov).

### Skills

- **policy-as-code** — Design policy-as-code guardrails (OPA/Rego, Sentinel, Checkov/tfsec) — enforce tagging, security, and cost rules in CI/plan with severity gates and exemptions.
- **terraform-module** — Author a reusable Terraform module — input variables with validation, typed outputs, sane defaults, versioning, provider constraints, and composition boundaries.
- **terraform-state** — Design Terraform state — remote backend, locking, state isolation/segmentation, drift detection, and safe import/move/rm operations without destroying live infra.
