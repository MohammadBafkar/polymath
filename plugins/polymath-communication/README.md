# polymath-communication

Communication craft for the Polymath marketplace — internal and
customer-facing prose.

## What it ships

- Skills: `exec-brief`, `six-pager`, `meeting-notes`, `write-release-notes`,
  `write-advisory`, `write-sunset-notice`.
- Templates: `Exec-brief.md`, `Six-pager.md`.

`write-release-notes`, `write-advisory`, and `write-sunset-notice` were folded
in from the former `polymath-content` plugin: customer-facing prose is the same
audience-first craft as the internal briefs, so "which comms plugin?" is no
longer a disambiguation the user has to make.

## Installation

```bash
claude plugin install polymath-communication@polymath
```

## Dependencies

- `polymath-core`

## License

MIT.
