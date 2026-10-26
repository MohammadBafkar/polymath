---
name: terraform-module
description: Author a reusable Terraform module — input variables with validation, typed outputs, sane defaults, versioning, provider constraints, and composition boundaries.
---

# terraform-module

> A good module is a small, versioned contract: clear inputs, useful outputs, no hidden global state. Design the interface before the resources, the way you would an API.

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

- A module design/skeleton: the variable contract (typed + validated), outputs, `required_providers` constraints, naming/tagging approach, composition boundary, versioning plan, and the example usage.

## Quality bar

- The module declares provider *requirements* but configures no provider/backend.
- Inputs are typed with validation; sensitive outputs are marked sensitive.
- One cohesive capability per module; `for_each` used for stable addressing.
- Versioned with an example and documented inputs/outputs.
