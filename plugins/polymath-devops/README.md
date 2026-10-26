# polymath-devops

DevOps craft for the Polymath marketplace.

## What it ships

- Skills: `dockerize`, `ci-pipeline-github`, `env-promotion`, `audit-dockerfile`, `audit-compose`.
- Slash entry points: the audit skills are invoked directly (`/polymath-devops:audit-dockerfile`, `/polymath-devops:audit-compose`); no command shims.
- References: [`deployer-pattern.md`](references/deployer-pattern.md) — how agents compose env-promotion + progressiveRollout + appStarts around the team's OWN pipeline; Polymath ships no autonomous deployer.

## Installation

```bash
claude plugin install polymath-devops@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
