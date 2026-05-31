# polymath-incident

Incident craft for the Polymath marketplace.

## What it ships

- Skills: `incident-triage`, `postmortem-blameless`, `comms-update`.
- Commands: `/incident-start`, `/postmortem`.
- Templates: `Postmortem.md`, `Comms-update.md`.
- Postmortem frontmatter validates against the `Postmortem` artifact schema; workflows can gate with `mustPass: artifactValid`.

## Pairs with

- `polymath-flows`: `respondToIncident` (drives end-to-end response) and `incidentRetroToActions` (decomposes a postmortem into trackable actions).
- `polymath-connector-pagerduty`, `polymath-connector-datadog`, `polymath-connector-jira` / `-linear`: connectors the workflows depend on.

## Installation

```bash
claude plugin install polymath-incident@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
