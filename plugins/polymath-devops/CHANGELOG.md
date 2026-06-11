# Changelog — polymath-devops

## [Unreleased]

### Added

- **`references/deployer-pattern.md`** — the deploy composition Polymath
  supports instead of an autonomous deployer: agents design promotion
  (env-promotion) and rollout (progressiveRollout), verify boots
  (appStarts), and draft the pipeline files (canonical bodies); the
  team's own CI/CD executes the mutation with its own credentials and
  approvals.
- `dockerize` and `ci-pipeline-github` consume project localization: `conventions_docs` role `deployment` from the project-context snapshot.

## [0.1.0]

### Added

- Initial v0.1 components: `dockerize`, `ci-pipeline-github`, `env-promotion` skills.
