# polymath-security

Security craft for the Polymath marketplace.

## What it ships

- Skills: `stride-threat-model`, `owasp-review`.
- Templates: `Threat-model.md` (materialized from `shared/templates/`).
- Workflows that invoke this plugin can validate the threat-model frontmatter with `mustPass: artifactValid` against the `ThreatModel` artifact schema.

## Installation

```bash
claude plugin install polymath-security@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
