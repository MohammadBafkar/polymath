# polymath-supply-chain

Software supply-chain craft: review what enters the build and whether you can prove where it came from.

## What it ships

- Skills: `supply-chain-review` — SBOM presence/completeness, dependency provenance + lockfile hygiene, license audit, build-pipeline trust, signing/SLSA attestation, risky-dependency flags, and compliance-control mapping.

## Why it exists

The audit found supply-chain/compliance structurally absent — `polymath-connector-snyk:triage-vulns` handles runtime CVEs, but nothing reviewed SBOM, provenance, licensing, or signing posture. This plugin covers that posture; it is distinct from runtime vuln triage and from the `bumpDependency` workflow.

## Installation

```bash
claude plugin install polymath-supply-chain@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
