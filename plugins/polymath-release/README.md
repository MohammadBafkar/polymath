# polymath-release

Release & delivery craft for the Polymath marketplace — the lifecycle of a
shipped change, from commit through progressive rollout to eventual sunset.

## What it ships

- Skills: `commit`, `pr`, `changelog`, `release-notes`, `safe-rollout`,
  `deprecation-plan`, `migration-guide`.
- Slash entry points: every skill is directly invocable (`/polymath-release:commit`, `/polymath-release:pr`, …); no separate command shims.
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

## Why no command shims

A skill is already a slash command (`/polymath-release:<skill>`). A same-named command would only duplicate the always-on listing entry, so this plugin ships skills alone.

## License

MIT.
