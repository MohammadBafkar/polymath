# polymath-release

Release craft for the Polymath marketplace. Drafts commit messages, PR descriptions, CHANGELOG entries, and release notes.

## What it ships

- Commands: `/commit`, `/pr`, `/changelog`, `/release-notes`.
- Templates: `CHANGELOG-entry.md`, `PR-description.md` (materialized from `shared/templates/`).

## Installation

```bash
claude plugin install polymath-release@polymath
```

## Dependencies

- `polymath-core`

## Why commands, not skills

Each component is a thin alias around a procedure that does not bundle scripts or references — the canonical guidance is short and the templates are imported separately. If a future need bundles tooling (e.g. a semver bumper), promote that to a skill.

## License

Apache-2.0.
