# polymath-kubernetes

Kubernetes craft for the Polymath marketplace.

## What it ships

- Skills: `write-manifest`, `audit-rbac-grants`, `propose-pod-security-standards`.
- Hook: `PreToolUse(Bash)` — blocks mutating kubectl commands when the current kube-context name matches `prod` (configurable via `POLYMATH_K8S_PROD_PATTERN`). Bypass per-call by including the literal token `POLYMATH_ACK_PROD` in the command.

## Installation

```bash
claude plugin install polymath-kubernetes@polymath
```

## Dependencies

- `polymath-core`

<!-- integration-policy:start -->
## Integration policy disclosure

Auto-generated from [`docs/INTEGRATION-POLICY.md`](../../docs/INTEGRATION-POLICY.md)
by `tools/sync-integration-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** kube docs + several community kube MCPs
- **Polymath value:** RBAC grant audit, Pod Security Standards proposals
- **Sunset trigger:** Demote when an official k8s MCP ships an opinionated RBAC + PSS workflow.
- **Status:** `experimental`
<!-- integration-policy:end -->

## License

MIT.
