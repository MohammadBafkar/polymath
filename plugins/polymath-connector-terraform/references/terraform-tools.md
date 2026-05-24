# Terraform plan-format reference

This connector reads plan output via the local `terraform` (or `tofu`) binary; there is no remote MCP server required — Terraform's CLI is the API.

## Producing a plan suitable for review

```bash
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json
```

The binary file is opaque; the JSON is the contract. Always go through the JSON form for review.

## Plan JSON shape (subset)

- `resource_changes[]` — primary signal. Each entry has:
  - `address` — full address (e.g. `module.network.aws_vpc.main`).
  - `type` / `name` — resource type and local name.
  - `change.actions` — array; see classification rules in the skill.
  - `change.before` / `change.after` — the diff payload.
  - `change.before_sensitive` / `change.after_sensitive` — boolean tree marking which leaves are sensitive.
- `configuration.provider_config[]` — provider versions (or lack thereof).
- `output_changes[]` — output drift; sometimes the only surface that exposes a regression.

## Sensitive values

When a field is marked sensitive, `before` / `after` are replaced with `(sensitive value)` in `terraform show` text output but are present as actual values in JSON unless `-no-color`/`-compact-warnings` filtering is applied. The skill must avoid echoing sensitive values into logs or PR comments.

## Tooling complements

- `tfsec` / `trivy config` — static rule checks (e.g. open security groups). Run separately; this skill focuses on *change* review, not greenfield rules.
- `terraform validate` — syntactic only. Does not catch destructive plans.
- `Atlantis` / `Spacelift` / `Terraform Cloud` — orchestration layers. They produce the same plan JSON; this skill works against any of them.

## Common pitfalls

- Reviewing `terraform plan` text output instead of the JSON. Text output drops structured information about sensitive fields and exact action arrays.
- Trusting `terraform plan -refresh=false` — it hides drift, which is often the most important signal.
- Reading a plan for one workspace and applying it to another. Plans embed the target workspace; an out-of-workspace apply is a guaranteed mistake.
