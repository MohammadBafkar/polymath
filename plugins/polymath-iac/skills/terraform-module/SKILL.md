---
name: terraform-module
description: Author a reusable Terraform module — input variables with validation, typed outputs, sane defaults, versioning, provider constraints, and composition boundaries.
---

# terraform-module

> A good module is a small, versioned contract: clear inputs, useful outputs, no hidden global state. Design the interface before the resources, the way you would an API.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Writing a new Terraform module or refactoring copy-pasted HCL into a reusable one.
- A module is hard to consume — unclear inputs, leaks provider config, or can't be versioned.
- A workflow invokes `polymath-iac:terraform-module`.

Not this when: you are choosing the cloud architecture/primitives — that is `polymath-cloud:design-stack-composition`. For state/backends, `polymath-iac:terraform-state`; for reviewing a generated plan, `polymath-cloud:plan-review`.

## Inputs

- The resource(s) the module provisions and the variation consumers need.
- Target providers/versions and the org's tagging/naming conventions.

## Procedure

1. **Design the interface first**: input variables (typed, documented, with `validation` blocks for constraints), and outputs that expose what consumers actually need (ids, ARNs, endpoints). Minimize the surface — fewer, well-chosen variables beat dozens.
2. **Sane, safe defaults**: secure-by-default values; required variables only where there's no safe default. Don't make every knob mandatory.
3. **No hidden global state**: the module declares `required_providers` + version constraints but does **not** configure providers or backends — the root module does. A module that pins a backend isn't reusable.
4. **Resource hygiene**: consistent naming + tagging (pass via variables/locals), `for_each` over `count` for stable addressing, explicit `depends_on` only where needed.
5. **Composition boundary**: one module = one cohesive capability. Compose small modules in the root; avoid a god-module. Nested modules only where genuinely shared.
6. **Versioning + sources**: tag releases (semver) and pin module sources by version; document upgrade/breaking changes. When you rename or restructure resources inside the module, ship `moved {}` blocks so consumers upgrade without destroy+recreate.
7. **Test it**: `terraform validate` + `tflint` in CI, and `terraform test` (or Terratest) against the example to prove the interface works.
8. **Document + example**: a README with inputs/outputs and a working example; lifecycle rules (`prevent_destroy`, `ignore_changes`) where state churn would be dangerous.
9. **Safety rails**: mark sensitive outputs `sensitive = true`; never bake secrets into the module.

## Output

The module skeleton and a one-paragraph design note, in this shape:

````text
modules/sqs-queue/            (capability: a queue with its DLQ, alarms, and access policy)
  versions.tf    required_providers { aws = { source = "hashicorp/aws", version = ">= 5.40, < 6.0" } }  — no provider/backend blocks
  variables.tf   name (string, validation: ^[a-z0-9-]{3,60}$) · visibility_timeout_seconds (number, default 30)
                 max_receive_count (number, default 5, validation 1–20) · tags (map(string), default {})
  main.tf        aws_sqs_queue.this + aws_sqs_queue.dlq (redrive) · aws_cloudwatch_metric_alarm.dlq_depth
  outputs.tf     queue_url, queue_arn, dlq_arn
  examples/basic/main.tf   module "refunds_queue" { source = "../.." name = "refunds" }
  tests/basic.tftest.hcl   asserts the redrive policy and the alarm threshold
Versioning: v1.0.0 tag; renames ship moved {} blocks; breaking input changes → v2.0.0 + UPGRADE.md
CI: terraform fmt -check · terraform validate · tflint · terraform test
````

## Quality bar

- The module declares provider *requirements* but configures no provider/backend.
- Inputs are typed with validation; sensitive outputs are marked sensitive.
- One cohesive capability per module; `for_each` used for stable addressing.
- Versioned with an example and documented inputs/outputs.
