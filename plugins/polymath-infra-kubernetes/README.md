# polymath-infra-kubernetes

Kubernetes craft for the Polymath marketplace.

## What it ships

- Skills: `write-manifest`, `audit-rbac-grants`, `propose-pod-security-standards`.
- Hook: `PreToolUse(Bash)` — blocks mutating kubectl commands when the current kube-context name matches `prod` (configurable via `POLYMATH_K8S_PROD_PATTERN`). Bypass per-call by including the literal token `POLYMATH_ACK_PROD` in the command.

## Installation

```bash
claude plugin install polymath-infra-kubernetes@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
