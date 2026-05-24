---
plugin: polymath-platform
scenario: devex-metrics-sheet
expect:
  invoked:
    - polymath-platform:devex-metrics
  output_matches:
    - "Lead Time"
    - "Change Failure Rate"
    - "MTTR"
    - "(SPACE|Satisfaction|Time to merge)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 90
---

# Prompt

> Define DevEx metrics for the platform team.

Use polymath-platform:devex-metrics. Our team owns the developer
platform for a 200-engineer org. Pick DORA + SPACE metrics, set
targets, and document collection sources.

# Acceptance

- All four DORA metrics listed with target + source.
- At most 2 SPACE metrics chosen (to avoid dashboard noise).
- Targets are concrete numbers/thresholds, not "improve".
- A review cadence and an anti-pattern guard are included.
