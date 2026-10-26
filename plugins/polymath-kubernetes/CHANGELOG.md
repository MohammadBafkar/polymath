# Changelog — polymath-kubernetes

<!-- markdownlint-disable MD024 -->

## [0.11.0]

### Fixed

- `propose-pod-security-standards`: `readOnlyRootFilesystem` is not part of the restricted profile; violators found via `kubectl label --dry-run=server` (the old `get pods | grep warn` verified nothing); `enforce-version` pinned.
- `write-manifest`: `/tmp` `emptyDir` for the read-only root filesystem, `automountServiceAccountToken: false`, digest-pinned image, graceful shutdown.
- `audit-rbac-grants`: `list`/`watch` on Secrets is full read access; `bind`, `pods/exec`, `nodes/proxy`, `serviceaccounts/token` escalation paths.

## [0.8.0]

Kubernetes craft: manifest defaults, RBAC audit, Pod Security Standards; prod-kubectl confirm hook.

### Skills

- **audit-rbac-grants** — Audit RBAC roles and bindings — find overbroad verbs (*), cluster-wide grants that should be namespaced, stale ServiceAccounts, anonymous access.
- **propose-pod-security-standards** — Propose Kubernetes Pod Security Standards (privileged/baseline/restricted) per namespace; identify violating workloads and remediations.
- **write-manifest** — Write a Kubernetes Deployment + Service + PDB manifest with safe defaults — resource requests/limits, probes, security context, topology spread.
