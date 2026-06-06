# polymath-release

Release & delivery craft for the Polymath marketplace — the lifecycle of a
shipped change, from commit through progressive rollout to eventual sunset.

## What it ships

- Skills: `commit`, `pr`, `changelog`, `release-notes`, `safe-rollout`,
  `deprecation-plan`, `migration-guide`.
- Commands: `/commit`, `/pr`, `/changelog`, `/release-notes`.
- Templates: `CHANGELOG-entry.md`, `PR-description.md`.

`safe-rollout` (from the former `polymath-progressive-delivery`) and
`deprecation-plan` + `migration-guide` (from the former `polymath-deprecation`)
were folded in: shipping a change, rolling it out behind flags/SLO gates, and
eventually retiring it are one lifecycle, not three install decisions.

## Installation

```bash
claude plugin install polymath-release@polymath
```

## Dependencies

- `polymath-core`

## Why commands, not skills

Each component is a thin alias around a procedure that does not bundle scripts or references — the canonical guidance is short and the templates are imported separately. If a future need bundles tooling (e.g. a semver bumper), promote that to a skill.

## License

MIT.
