# Changelog — polymath-iac

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 3 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `policy-as-code`, `terraform-module`, `terraform-state`: exact output shapes.
- `terraform-state`: Inputs no longer suggest DynamoDB locking (deprecated); state is read for structure, never for values.

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
