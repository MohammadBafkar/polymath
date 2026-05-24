# Changelog — polymath-flows

## [Unreleased]

### Added

- Initial v0.1 components: `run-workflow`, `resume-workflow`, `list-workflows` skills.
- `bin/polymath-flow` deterministic executable (validate, start, next, complete, fail, resume, assert, list).
- `workflows/shipFeature.yaml` — PRD → acceptance → implement → review → verify → changelog → PR draft.
- Embedded minimal YAML subset parser fallback when PyYAML is unavailable.
