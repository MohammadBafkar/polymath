# Changelog — polymath-release

## [Unreleased]

### Added

- `pr` uses the project's `prompts.pr_description_template` from the project-context snapshot when set.

### Changed

- Absorbed two adjacent lifecycle plugins so shipping → rolling out → retiring a
  change is one install: `safe-rollout` folded in from the former
  `polymath-progressive-delivery`, and `deprecation-plan` + `migration-guide`
  from the former `polymath-deprecation`. Workflow `invoke:` refs and golden
  tests updated to the new `polymath-release:` ids.

## [0.1.0]

### Added

- Initial v0.1 commands: `/commit`, `/pr`, `/changelog`, `/release-notes`.
- Materialized `CHANGELOG-entry.md` and `PR-description.md` templates.
