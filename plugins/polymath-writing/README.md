# polymath-writing

Writing craft for the Polymath marketplace.

## What it ships

- Skills: `adr`, `rfc`, `runbook`, `architecture-doc`.
- Templates: `ADR.md`, `RFC.md`, `Runbook.md`, `Architecture-doc.md` (materialized from `shared/templates/`).
- Workflows can validate ADR frontmatter via `mustPass: artifactValid` against the `ADR` artifact schema.

## Installation

```bash
claude plugin install polymath-writing@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
