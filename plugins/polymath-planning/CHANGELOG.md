# Changelog — polymath-planning

## [Unreleased]

### Added

- `forecast` skill — forecast a delivery date/scope as a probability range
  (reference-class, throughput/Monte-Carlo, cone of uncertainty), distinct from
  the per-item three-point `estimate`.

## [0.1.0]

### Added

- `write-plan`, `work-breakdown`, `estimate` skills.
- `Plan.md` template under `templates/`.
- Frontmatter on `Plan.md` validated by
  [`shared/schemas/artifacts/Plan.schema.json`](../../shared/schemas/artifacts/Plan.schema.json);
  workflows producing a Plan can `mustPass: artifactValid` or
  `artifactSchemaStrict` against `docs/plans/<slug>.md`.
