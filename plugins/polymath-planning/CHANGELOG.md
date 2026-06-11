# Changelog — polymath-planning

## [Unreleased]

### Changed

- `prioritize` skill folded in from the former `polymath-prioritize` plugin — prioritization is planning.

### Added

- **Plan template upgrades.** `templates/Plan.md` gains **Locked
  decisions** (decisions already made — spike/ADR/owner — the plan must
  not relitigate, each with its source) and a **Deferral registry**
  (wanted-but-deferred work, each entry with the condition that reopens
  it; distinct from Out of scope). `write-plan` fills both and adds a
  summary-first checkpoint: a one-screen skeleton is confirmed before
  the full document is written.
- `forecast` skill — forecast a delivery date/scope as a probability range
  (reference-class, throughput/Monte-Carlo, cone of uncertainty), distinct from
  the per-item three-point `estimate`.

## [0.1.0]

### Added

- `write-plan`, `work-breakdown`, `estimate` skills.
- `Plan.md` template under `templates/`.
- Frontmatter on `Plan.md` validated by
  [`registry/schemas/artifacts/Plan.schema.json`](../../registry/schemas/artifacts/Plan.schema.json);
  workflows producing a Plan can `mustPass: artifactValid` or
  `artifactSchemaStrict` against `docs/plans/<slug>.md`.
