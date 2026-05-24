# polymath-incident

Incident craft for the Polymath marketplace.

## What it ships

- Skills: `incident-triage`, `postmortem-blameless`, `comms-update`.
- Commands: `/incident-start`, `/postmortem`.
- Templates: `Postmortem.md`, `Comms-update.md`.
- Postmortem frontmatter validates against the `Postmortem` artifact schema; workflows can gate with `mustPass: artifactValid`.

## Why no workflow yet?

Per PLAN.md § 10: incident workflows wait for at least one observability or pager connector to exist (Phase 4). The skills here are usable on their own and become the building blocks of `respondToIncident` once connectors land.

## Installation

```bash
claude plugin install polymath-incident@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
