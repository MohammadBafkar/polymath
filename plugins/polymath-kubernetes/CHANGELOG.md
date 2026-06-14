# Changelog — polymath-kubernetes

<!-- markdownlint-disable MD024 -->

## [0.8.0]

Kubernetes craft: manifest defaults, RBAC audit, Pod Security Standards; prod-kubectl confirm hook.

### Skills

- **audit-rbac-grants** — Audit RBAC roles and bindings — find overbroad verbs (*), cluster-wide grants that should be namespaced, stale ServiceAccounts, anonymous access.
- **propose-pod-security-standards** — Propose Kubernetes Pod Security Standards (privileged/baseline/restricted) per namespace; identify violating workloads and remediations.
- **write-manifest** — Write a Kubernetes Deployment + Service + PDB manifest with safe defaults — resource requests/limits, probes, security context, topology spread.
