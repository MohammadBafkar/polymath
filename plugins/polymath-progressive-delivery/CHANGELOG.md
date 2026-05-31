# Changelog — polymath-progressive-delivery

## [Unreleased]

### Added

- `safe-rollout` skill — design a progressive rollout: feature-flag strategy,
  canary / blue-green / ring stages with bake times, SLO-driven health gates,
  automated rollback, and a kill switch; flags irreversible data changes a flag
  cannot undo. Ships with a golden fixture and a skill-triggering test.
