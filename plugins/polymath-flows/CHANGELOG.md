# Changelog — polymath-flows

## [Unreleased]

### Added

- Initial v0.1 components: `run-workflow`, `resume-workflow`, `list-workflows` skills.
- `bin/polymath-flow` deterministic executable (validate, start, next, complete, fail, resume, assert, list).
- `workflows/shipFeature.yaml` — PRD → acceptance → implement → review → verify → changelog → PR draft.
- Embedded minimal YAML subset parser fallback when PyYAML is unavailable.
- Phase 1.5: `topology: fanout` accepted on workflow steps; `artifactValid` mustPass check (PRD, ADR, Postmortem, ThreatModel).
- Phase 1.5: `workflows/reviewPR.yaml` — orient (series) then four parallel critics declared with `topology: fanout` (correctness, coverage, security, challenge), reduced by a synthesize step. Depends on polymath-engineering, polymath-qa, polymath-security, polymath-thinking.
- Phase 4: `workflows/respondToIncident.yaml` — page-context → triage → query-during-incident → postmortem → file-bugs. Depends on polymath-incident, polymath-connector-pagerduty, polymath-connector-datadog, polymath-connector-jira. mustPass includes `artifactValid` against the Postmortem schema.
