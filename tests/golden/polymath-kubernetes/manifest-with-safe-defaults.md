---
plugin: polymath-kubernetes
scenario: manifest-with-safe-defaults
expect:
  invoked:
    - polymath-kubernetes:write-manifest
  output_matches:
    - "runAsNonRoot"
    - "readinessProbe"
    - "(PodDisruptionBudget|policy/v1)"
    - "resources:"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Write Kubernetes manifests for our refund service.

Use polymath-kubernetes:write-manifest. Workload: refund,
image example/refund:0.1.0, 3 replicas, container port 8080,
HTTP health endpoint /healthz, namespace payments.

# Acceptance

- Deployment + Service + PodDisruptionBudget all present.
- securityContext sets runAsNonRoot: true and (read-only root fs OR
  capabilities.drop: ALL).
- readinessProbe defined; livenessProbe absent OR clearly distinct from
  readiness.
- resources.requests set (cpu + memory).
- Labels follow the recommended app.kubernetes.io/* set.
