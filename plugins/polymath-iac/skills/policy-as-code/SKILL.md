---
name: policy-as-code
description: Design policy-as-code guardrails (OPA/Rego, Sentinel, Checkov/Trivy) — enforce tagging, security, and cost rules in CI/plan with severity gates and exemptions.
---

# policy-as-code

> Guardrails beat gates-by-review: encode the rule once and it enforces itself on every plan. Write policies that block the dangerous and warn the merely untidy — and make exemptions explicit, not silent.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Enforcing org rules (security, tagging, cost, naming) on infrastructure automatically.
- Misconfigurations (public buckets, open security groups, untagged resources) keep reaching production.
- A workflow invokes `polymath-iac:policy-as-code`.

Not this when: you are scanning application code/CI broadly — that is `polymath-security:devsecops-pipeline` (this is the infra-policy layer it can call). For reviewing one generated plan by hand, `polymath-cloud:plan-review`.

## Inputs

- The rules to enforce and their severity (hard-block vs advisory).
- The toolchain (OPA/Conftest, Sentinel, Checkov, Trivy — tfsec's successor) and where it runs (plan-time, CI, admission).

## Procedure

1. **Catalog the rules** by intent: *security* (no public S3, no `0.0.0.0/0` ingress, encryption required), *cost* (instance-size/region caps, no orphaned resources), *governance* (mandatory tags, naming, allowed regions/services).
2. **Pick the enforcement point**: evaluate against the `terraform plan` JSON in CI (pre-apply) and/or at admission (OPA Gatekeeper for K8s). Pre-apply is the cheapest place to stop a bad change.
3. **Tool choice**: prebuilt rulesets (Checkov/Trivy) for common misconfig coverage fast; OPA/Rego or Sentinel for custom org policy. Often both — prebuilt for breadth, custom for the org-specific.
4. **Severity tiers**: hard-fail on security/compliance violations; warn on style/cost-advisories. Don't hard-block on everything or people route around it.
5. **Exemptions as code**: an explicit, reviewed, expiring waiver (with owner + reason) — never a silent skip. Track waivers.
6. **Test the policies**: unit-test rules against pass/fail fixtures so a policy change can't silently stop enforcing.
7. **Roll out gradually**: start advisory to measure violation volume, then ratchet to blocking once the backlog is burned down.
8. **Report**: violation trends and waiver inventory for governance.

## Output

```text
Policy-as-code design: AWS Terraform (Checkov + OPA/Conftest on plan JSON, in CI)

Rule                                   Intent       Tier      Tool
S3 buckets block public access         security     BLOCK     checkov CKV_AWS_53-56
no 0.0.0.0/0 ingress on 22/3389        security     BLOCK     checkov CKV_AWS_24/25
RDS storage encrypted                  security     BLOCK     checkov CKV_AWS_16
mandatory tags: owner, cost-center     governance   WARN → BLOCK after 30 days     conftest policy/tags.rego
instance types ≤ 2xlarge outside prod  cost         WARN      conftest policy/cost.rego

Enforcement: on `terraform show -json` in the PR pipeline (pre-apply); prod applies re-check in the apply job
Waivers:     .checkov.yaml / waivers.yaml entries need owner + reason + expiry (≤ 90 days); expired waiver fails CI
Tests:       conftest verify with pass/fail fixtures per rule, run in CI on policy changes
Rollout:     advisory 2 weeks (measure: 41 violations found) → burn down → blocking
Report:      weekly violation trend + waiver inventory to the platform channel
```

## Quality bar

- Rules are tiered: security/compliance hard-block, style/cost advise.
- Enforcement runs pre-apply on the plan (cheapest stop point), not only post-hoc.
- Exemptions are explicit, owned, and expiring — never silent.
- Policies have pass/fail tests so enforcement can't silently regress.
