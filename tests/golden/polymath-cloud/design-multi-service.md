---
plugin: polymath-cloud
scenario: design-multi-service
expect:
  invoked:
    - polymath-cloud:design-stack-composition
  output_matches:
    - "(blast.radius|foundational|platform|service)"
    - "(workspace|directory|backend)"
    - "(terraform_remote_state|outputs|reads)"
timeout_seconds: 60
---

# Prompt

> Design Terraform stack composition for an org with 6 services on
> AWS, one shared Postgres, a shared EKS cluster, and 3 environments
> (dev/staging/prod).

Use polymath-cloud:design-stack-composition.

# Acceptance

- Stacks split by blast-radius zone (foundational / platform / service).
- Remote-state references flow one direction.
- Workspaces vs directories decision is explicit.
- Per-stack RBAC for apply named.
