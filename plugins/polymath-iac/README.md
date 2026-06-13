# polymath-iac

Infrastructure-as-Code authoring craft for the Polymath marketplace. The *authoring*
and *governance* of Terraform/OpenTofu — module design, state topology, and policy
guardrails.

Boundary: cloud-pattern/primitive selection lives in `polymath-cloud`
(`design-stack-composition`); **plan/diff review before apply is already
`polymath-cloud:plan-review`** — this plugin does not duplicate it. Broad app/CI
security scanning is `polymath-security:devsecops-pipeline`; `policy-as-code` here is
the infra-policy layer it calls.

## What it ships

- Skills:
  - `terraform-module` — author a reusable module: typed+validated input variables, outputs, provider constraints, no embedded backend, versioning, composition boundary.
  - `terraform-state` — remote backend + locking, state isolation by blast radius, drift detection, safe `import`/`state mv`/`state rm`, recovery.
  - `policy-as-code` — OPA/Rego, Sentinel, Checkov/tfsec guardrails enforced pre-apply with severity tiers and explicit expiring exemptions.

## Installation

```bash
claude plugin install polymath-iac@polymath
```

## Dependencies

- `polymath-core`
- `polymath-cloud`

## License

MIT.
