# Changelog — polymath-iac

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `terraform-state`: S3 native lockfile locking; `import`/`moved`/`removed` blocks preferred over CLI state surgery; `plan -refresh-only` for drift.
- `terraform-module`: `moved` blocks on internal refactors; `terraform test`/tflint.
- `policy-as-code`: tfsec → Trivy.

## [0.8.0]

Infrastructure-as-Code authoring: reusable Terraform modules, state/backends/drift, policy-as-code guardrails (OPA/Sentinel/Checkov).

### Skills

- **policy-as-code** — Design policy-as-code guardrails (OPA/Rego, Sentinel, Checkov/tfsec) — enforce tagging, security, and cost rules in CI/plan with severity gates and exemptions.
- **terraform-module** — Author a reusable Terraform module — input variables with validation, typed outputs, sane defaults, versioning, provider constraints, and composition boundaries.
- **terraform-state** — Design Terraform state — remote backend, locking, state isolation/segmentation, drift detection, and safe import/move/rm operations without destroying live infra.
