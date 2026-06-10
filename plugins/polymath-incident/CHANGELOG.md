# Changelog — polymath-incident

## [Unreleased]

### Added

- `postmortem-blameless` uses the project's `prompts.postmortem_template` from the project-context snapshot when set.

## [0.1.0]

### Added

- Initial v0.1 components: `incident-triage`, `postmortem-blameless`, `comms-update` skills.
- Commands: `/incident-start`, `/postmortem` (thin aliases).
- Ships `Postmortem.md` + `Comms-update.md` templates under `templates/`.
- Postmortem frontmatter validates against the `Postmortem` artifact schema.
