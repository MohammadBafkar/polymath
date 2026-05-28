---
plugin: polymath-devops
scenario: audit-dockerfile
expect:
  invoked:
    - polymath-devops:audit-dockerfile
  output_matches:
    - "(FROM|base.image|digest)"
    - "(USER|root|non.root)"
    - "(HEALTHCHECK|.dockerignore|secret)"
timeout_seconds: 60
---

# Prompt

> Audit a node-based Dockerfile: FROM node:20, single stage, COPY . .,
> CMD ["node", "index.js"], no USER, no HEALTHCHECK.

Use polymath-devops:audit-dockerfile.

# Acceptance

- Base image flagged as tag-pinned (floats) with digest-pin fix.
- USER non-root recommendation.
- HEALTHCHECK recommendation (or note orchestrator handles it).
- COPY . . criticized; fix proposed.
