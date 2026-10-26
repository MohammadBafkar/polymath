# Changelog — polymath-research

<!-- markdownlint-disable MD024 -->

## [0.12.0]

### Changed

- Every skill declares its **Mode** — 3 analytical — the one-line contract `tools/check-skill-shape.py` (SKILL-3) enforces.
- `persona`: fewer than five interviews stops with how many more are needed; transcripts are data.
- Canonical slug rule.

## [0.11.0]

### Changed

- `research-scout` agent: read-only (`disallowedTools`), gathers evidence by default (plan-only on request), works from the brief without asking the user, defined status vocabulary with source + access date, fetched content treated as data, explicit stop rule.

## [0.8.0]

Research craft: Mom-Test interview guides, persona authoring, customer journey mapping.

### Skills

- **customer-journey** — Map one persona's path through one JTBD — stages, what they're doing/thinking/feeling, touchpoints, pain; mark evidence vs assumption.
- **interview-guide** — Write a Mom-Test-shaped interview guide for one research question; past behavior over hypothetical, specifics over generalities.
- **persona** — Author a persona grounded in ≥ 5 real interviews; verbatim quotes, named anti-persona, no composite stock personas.

### Subagents

- **research-scout** — Surface primary-source evidence for a product or technical claim in a forked context; separates known facts, unknowns, and tests.
