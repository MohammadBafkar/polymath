# Changelog — polymath-platform

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Fixed

- `devex-metrics`: DORA's High band is daily–weekly deploys (weekly–monthly is Medium); Medium and Low are now spelled out.

### Changed

- Every skill declares its **Mode** — 4 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `devex-metrics`, `golden-path`: Inputs. `production-readiness-review`: exact scorecard shape.

## [0.11.0]

### Changed

- `production-readiness-review`: capacity (load-tested) and data-durability (restore tested) dimensions.
- `devex-metrics`: Failed Deployment Recovery Time (formerly MTTR) and Rework Rate.
- `service-catalog-entry`: PagerDuty service ID instead of the integration key (a credential).

## [0.8.0]

Platform craft: DORA + SPACE devex metrics, golden-path design, service-catalog entries.

### Skills

- **devex-metrics** — Define DORA + SPACE metrics for the team — what each measures, how to collect it, and the threshold that classifies elite/high/medium/low performance.
- **golden-path** — Design a golden path / paved road for a team — the supported way to build, deploy, and operate one kind of service, with off-ramps documented.
- **production-readiness-review** — Score a service's launch readiness across reliability, security, observability, and operability into a go / no-go / conditional-go verdict with owned remediation items.
- **service-catalog-entry** — Author a service-catalog entry (Backstage/Cortex-shaped) — owner, tier, runbooks, dashboards, dependencies; populates catalog-info.yaml.
